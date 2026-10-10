"""`MapScreen` — the map view (moved verbatim from `mapper/app.py` at
`2026-10-09-modular-batch` B0).

The class body is unchanged; Spine B (B1–B11) moves its concerns into sibling mixin
modules of this package.  `mapper.app` and `mapper.screens.map` re-export
`MapScreen`, so `from mapper.app import MapScreen` keeps resolving (LLR-MOD.3.1).
This module never imports `mapper.app` (LLR-MOD.6.2).
"""

from __future__ import annotations


from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.geometry import Region
from textual.screen import Screen
from textual.widgets import Input, Static

from mapper import darkside
from mapper.diff import DiffResult
from mapper.keymap import groups_for_keybar, label_for, SCOPE_MAP
from mapper.model import Ficha, Graph, Node
from mapper.screens.common import (
    COUNT_REGION_ID,
    keybar_groups,
    map_hint,
    MapHintLine,
    screen_bindings,
)
from mapper.screens.map.navigation import NavigationModel
from mapper.screens.prompt import _FichaScreen
from mapper.store import MapStore
from mapper.views.layered import LayeredRenderer
from mapper.views.outline import OutlineRenderer
from mapper.views.radial import RadialRenderer
from mapper.views.state import ViewState
from mapper.widgets.chrome import HintLine, KeyBar, TabStrip
from mapper.widgets.inspector import FichaInspector, FieldInput, INSPECTOR_WIDTH
from mapper.widgets.rail import OutlineRail, RAIL_WIDTH
from mapper.screens.map.hints import HintsOps
from mapper.screens.map.exporting import ExportingOps
from mapper.screens.map.opening import OpeningOps
from mapper.screens.map.undo import UndoOps
from mapper.screens.map.focus_mode import FocusModeOps
from mapper.screens.map.editing import EditingOps
from mapper.screens.map.drafts import DraftsOps
from mapper.screens.map.navigation import NavOps
from mapper.screens.map.searching import SearchingOps
from mapper.screens.map.panning import PanningOps
from mapper.screens.map.painting import PaintingOps


class MapScreen(PaintingOps, PanningOps, SearchingOps, NavOps, DraftsOps, EditingOps, FocusModeOps, UndoOps, OpeningOps, ExportingOps, HintsOps, Screen):
    """A map rendered as a layered tree."""

    KEY_SCOPE = SCOPE_MAP
    BINDINGS = screen_bindings(SCOPE_MAP)
    # The inspector's fields mount after this screen does, and Textual would
    # auto-focus the first of them — which silently disables every single-letter
    # map binding, because a focused Input consumes printable keys.  The map, not
    # a text field, owns the keyboard on arrival.
    AUTO_FOCUS = None

    def __init__(self, map_id: str, source_crumb: list[str] | None = None) -> None:
        super().__init__()
        self.map_id = map_id
        self.source_crumb = source_crumb
        self.store: MapStore | None = None
        self.graph: Graph = Graph()
        self.base_graph: Graph = Graph()
        self.nav: NavigationModel = NavigationModel(self.graph)
        self.renderer = LayeredRenderer()
        self.outline_renderer = OutlineRenderer()
        self.radial_renderer = RadialRenderer()
        self.query_text = ""
        self.focus_active = False
        self.outline_mode = False
        self.radial_mode = False
        self.diff_active = False
        self.diff: DiffResult | None = None
        self.rail_hidden = False
        self.inspector_hidden = False
        self._regions_pinned = False
        # US-N06.  The screen owns fold and pan; the rail and the renderer are
        # readers.  `folded` lived on `OutlineRail` until Inc-3, where a region
        # the layout auto-hides below 118 columns owned state the canvas needed.
        self.folded: frozenset[str] = frozenset()
        self.pan_x = 0
        self.pan_y = 0
        # The pan the operator had when a docked legend moved the view, kept
        # until the legend closes (`legend_docked`, Inc-8 verdict `F2`).
        self._pan_before_legend: tuple[int, int] | None = None
        # The focused widget's id (or `None`) at that same moment -- captured
        # alongside the pan, restored alongside it (`INC8-P3-CR-F1`).  Valid
        # only while `_pan_before_legend` is not `None`; the two are set and
        # cleared together.
        self._focus_before_legend: str | None = None
        # Set by `legend_closed`, consumed by `on_screen_resume`: the pan and
        # focus to restore once THIS screen is active again.  Restoring from
        # `legend_closed` itself is too early -- it runs before the legend's
        # own `dismiss()` even pops this screen back on, and Textual's own
        # `AUTO_FOCUS` grabs the rail during that pop whenever nothing is
        # focused (`INC8-P3-CR-F1`, carried `UX-F7`).  `on_screen_resume`
        # answers the same `ScreenResume` that auto-focus does.
        self._legend_restore_pending: tuple[int, int, str | None] | None = None
        # The canvas region `_declare_after_layout` last painted a numeral for.
        # `None` means "never", which is why the first pass always re-schedules.
        self._declared_for: Region | None = None
        # EVERYTHING the canvas's current content was produced FROM: the
        # renderer and the whole `ViewState`.  `P1` says content and geometry
        # agree at rest, and the settle pass may skip a re-render it knows would
        # be byte-identical.  Measured: without that skip, one settle pass on an
        # 11999-node graph in outline costs 0.33 s at 118x34 -- a full re-render
        # -- and doubles a repaint that already costs 0.36 s.
        #
        # THIS HELD ONLY `(w, h)` AND THAT WAS A DEFECT THE SECURITY REVIEW
        # FIRED.  Content is a function of the renderer plus NINE `ViewState`
        # fields; geometry is two of them.  A guard keyed on two inputs is a
        # PROJECTION of `P1`, not `P1`, so any other input changing without an
        # intervening `refresh_canvas` let the settle declare the frame
        # reconciled and skip -- while the strip repainted from the new state
        # against a canvas holding the old one.  Demonstrated: the canvas header
        # declaring 7 in layered beside a strip declaring 5 in outline, at one
        # unchanged geometry.  That is `B-60` reintroduced through the mechanism
        # built to prevent it.
        #
        # `ViewState` is a frozen dataclass, so `==` is total over its fields and
        # costs O(fields) -- it cannot give back the 0.33 s the skip exists to
        # save.  Now the predicate really is the invariant rather than a shadow
        # of it, which is what the comment below already claimed.
        self._rendered_for: tuple[object, ViewState] | None = None
        # ONE FRAME'S resolution, held only for the duration of that frame.
        # See `_search_order`; `_open_paint_pass` is what bounds its lifetime.
        self._search_memo: tuple[Graph, str, tuple[str, ...]] | None = None
        # `#D5b` took `n` from `next_gap` and gave it to the walk, and the
        # relocated chord is undiscoverable through `?` until Inc-8.  The first
        # `n` press on this screen says so.  Per SCREEN and not per process:
        # a process-wide flag is class state shared by every map the operator
        # opens and by every test in a run, and the acceptance reads the frame
        # twice rather than reading this field.
        self._rebind_declared = False
        # US-001 (LLR-003.2): set while a draft guard this screen pushed is up,
        # so a second exit never stacks a second guard.
        self._draft_guard_open = False
        # B-103: set by `_save_or_toast` when a save raises, read by `_save_draft`
        # for the failed-save toast.
        self._last_save_error: str | None = None

    def compose(self) -> ComposeResult:
        crumb_prefix = self.source_crumb or [self.map_id]
        yield TabStrip("c", crumb=crumb_prefix + [""])
        yield Static("", id="map-minimap")
        # Variant A «taller»: rail | canvas | inspector.  The inspector is the ONE
        # ficha surface — it replaces both the old `#map-ficha` GroupBox and the
        # LayeredRenderer's own ficha strip, which rendered the same card twice.
        yield Horizontal(
            OutlineRail(id="map-rail"),
            Static("", id="map-canvas"),
            FichaInspector(id="map-inspector"),
            id="map-body",
        )
        yield Input(placeholder="/search", id="search-input")
        yield Static("", id=COUNT_REGION_ID)
        yield Static("", id="map-toast")
        yield MapHintLine(map_hint())
        # The keybar reads the same seat the bindings are generated from, so it
        # cannot advertise a key the screen does not bind (US-N03).
        yield KeyBar(groups_for_keybar(keybar_groups(self.KEY_SCOPE)))

    def _notice_load_warnings(self, graph: Graph) -> None:
        """Tell the operator which node and which field were unreadable.

        LLR-R03.4.  The map still loaded (LLR-R03.5), so this is a notice and not
        an error path; `darkside.plain` because the node id and the key both come
        out of a file.
        """
        if not graph.load_warnings:
            return
        self.notify(
            darkside.plain("; ".join(graph.load_warnings)),
            severity="warning",
            markup=False,
        )

    def _establish_graph(self, graph: Graph, *, cursor: str | None) -> None:
        """Make *graph* the screen's map: the ONE load path (design 1b.9).

        `on_mount` and a failed save's reload both come through here, so the
        reload re-establishes the view exactly as opening the map does
        (LLR-004.2): the whole map, focus cleared (a focused view is a subgraph),
        load warnings surfaced, a fresh navigation, the cursor kept if its node
        still exists and the root otherwise.
        """
        self.base_graph = self.graph = graph
        self.focus_active = False
        self._notice_load_warnings(graph)
        self.nav = NavigationModel(graph)
        self.nav.cursor = cursor if cursor in graph.nodes else graph.root_id

    def on_mount(self) -> None:
        self.store = self.app.store  # type: ignore[attr-defined]
        search = self.query_one("#search-input", Input)
        search.display = False
        search.disabled = True
        self.focus()

        try:
            self._establish_graph(self.store.load(self.map_id), cursor=None)
        except Exception as e:
            error_graph = Graph()
            error_graph.add_node(Node(id="root", ficha=Ficha(title="error")))
            self._establish_graph(error_graph, cursor=None)
            self.notify(
                f"error loading map: {darkside.plain(str(e))}",
                severity="error",
                markup=False,
            )

        # Resume cursor from last session if it points into this map.
        if self.store is not None:
            last_map, last_node = self.store.last_session()
            if last_map == self.map_id and last_node in self.graph.nodes:
                self.nav.cursor = last_node
            self.store.record_session(self.map_id, self.nav.cursor)

        self._apply_region_visibility()
        self.refresh_canvas()
        # Keep focus off the side regions on arrival: a focused Input eats every
        # single-letter key, so the map's own navigation would be dead until the
        # operator blurred it by hand.  Scheduled after the refresh because the
        # rail and the inspector's fields are focusable and mount after this runs.
        self.call_after_refresh(self._park_focus)
        # `B-56` AND `B-60`, both CLOSED rather than carried.  The carry they
        # replace was recorded on measurements that were wrong twice over: the
        # declaration was ABSENT at ordinary sizes rather than merely stale, and
        # ordinary navigation did not clear it.  See `_declare_after_layout`,
        # which repaints the two surfaces that DECLARE -- the canvas and the
        # strip -- and nothing that focuses, so `LLR-CNV.3.1` and `B-50` are
        # untouched.
        self.call_after_refresh(self._declare_after_layout)

    # -- region layout (LLR-N06.6) -----------------------------------------
    # Below this width the canvas cannot show a card's coverage row without
    # clipping it mid-field, and a clipped field is indistinguishable from a
    # present one — the canvas would silently misreport coverage.  Measured by
    # the UX lens: a 5-field schema needs card_w >= 15, so n*18-3 <= w-2.
    MIN_CANVAS_WIDTH = 58

    def _chrome_width(self) -> int:
        """Columns taken by the rail and inspector at the current setting."""
        return (0 if self.rail_hidden else RAIL_WIDTH) + (
            0 if self.inspector_hidden else INSPECTOR_WIDTH
        )

    def _apply_region_visibility(self) -> None:
        """Collapse the side regions when the terminal cannot afford them.

        Auto-collapse is width-driven, but an explicit toggle wins: once the
        operator has hidden or shown a region by hand, we stop second-guessing.
        """
        size = self.size or self.app.size
        if not self._regions_pinned:
            available = size.width - RAIL_WIDTH - INSPECTOR_WIDTH
            if available < self.MIN_CANVAS_WIDTH:
                self.rail_hidden = True
            if size.width - INSPECTOR_WIDTH < self.MIN_CANVAS_WIDTH:
                self.inspector_hidden = True
        self.query_one("#map-rail", OutlineRail).display = not self.rail_hidden
        self.query_one("#map-inspector", FichaInspector).display = not self.inspector_hidden

    def action_toggle_rail(self) -> None:
        self._regions_pinned = True
        self.rail_hidden = not self.rail_hidden
        self._apply_region_visibility()
        self._clear_pan_hint()
        self.refresh_canvas()

    def action_toggle_inspector(self) -> None:
        self._regions_pinned = True
        self.inspector_hidden = not self.inspector_hidden
        self._apply_region_visibility()
        self.refresh_canvas()

    def action_focus_rail(self) -> None:
        """Move keyboard focus to the rail, and say so on the hint line."""
        rail = self.query_one("#map-rail", OutlineRail)
        if self.rail_hidden:
            self.action_toggle_rail()
        rail.focus()
        self.query_one(HintLine).set_hint(
            f"rail · ↵ {label_for(SCOPE_MAP, 'collapse_branch')} · "
            f"esc {label_for(SCOPE_MAP, 'back_or_home')}", "esc"
        )
        self.refresh_canvas()

    # -- pan (HLR-N06.1) ---------------------------------------------------
    # One press moves the window by this many cells.  A single cell makes the
    # chord feel dead on a map that overflows by 60 columns; a whole viewport
    # loses the operator's place.  Vertical is smaller because a card row is
    # 4-5 cells tall and a page-sized jump skips whole levels.
    PAN_STEP_X = 8
    PAN_STEP_Y = 4

    # `HEADER_ROWS = 2` USED TO LIVE HERE, AND IT WAS FALSE.  The note argued
    # the header's length is always `avail + 5` or `2 * avail - 43`, hence
    # always between `avail` and `2 * avail`, hence exactly two physical rows.
    # Both of its paddings are CLAMPED AT 0, so below `avail = 48` neither
    # formula applies: the line is a fixed core plus the `▽ N fuera de vista`
    # declaration, and on `legacy` that is 55 cells at EVERY narrow width.
    # Measured, it wraps to THREE physical rows at canvas width 21..34 and FOUR
    # at 20 -- and `_canvas_size` floors `w` at 20, so the band is one resize
    # away.  Charging 2 there left the screen believing one or two more body
    # rows survived than the region could show, and `painted_ids` declared nodes
    # that leave no trace: at terminal (28,17) it declared `erp` on a frame with
    # zero card marks while the strip read 7 against a truth of 8.  That is
    # `CR-F1`'s defect verbatim, one width band over (`B-61`).
    #
    # The number is now MEASURED per call by `layered.header_rows`, off the same
    # `_header_line` helper `render` paints from, so there is no second copy of
    # the header's shape to drift.

    def _park_focus(self) -> None:
        """Hand the keyboard back to the map itself."""
        self.set_focus(None)

    def on_resize(self, event: events.Resize) -> None:
        """Re-declare when the layout actually settles — `B-60`, closed properly.

        `on_mount` schedules `_declare_after_layout` on the FIRST
        `call_after_refresh`, and at narrow terminals that callback runs while
        `_apply_region_visibility`'s show/hide is still reflowing the row.
        Instrumented at (31,16): the callback saw a 29x2 canvas region, so
        `_canvas_size` took the short-region branch, returned `h = 1` and
        declared nothing painted; the region then settled to 31x3.  With no
        resize handler nothing recomputed, so BOTH declaring surfaces kept a
        numeral computed for a frame that no longer existed -- the strip said 8
        while 7 were hidden.  Reproduced at (31,16), (32,16), (34,15), (35,14)
        on `legacy` and independently on `anidado`, so it is not a fixture
        quirk.

        A one-shot post-mount callback cannot see the settle; the resize can.
        This repaints the same two surfaces `_declare_after_layout` does and
        nothing that focuses, so `LLR-CNV.3.1` and `B-50` stay where they are.

        THIS HANDLER ALONE DOES NOT CLOSE IT, and the measurement says why: a
        SCREEN resize is not a CANVAS resize.  Traced at (31,16), this fires
        once with the terminal's own 31x16 -- BEFORE the row reflows -- and the
        canvas region moves twice more afterwards without any further screen
        resize.  So this covers the case that had no handler at all, an operator
        resizing the terminal after mount, and `_declare_after_layout` chases
        the region to its settle from wherever it is entered.
        """
        self._declared_for = None
        self._declare_after_layout()

    def on_descendant_focus(self, event: events.DescendantFocus) -> None:
        """`H2` (closing verdict, round 5): repaint on every focus change, so
        the selection's tone always matches the real focus owner --
        `_view_state`'s `focus_owner` already decides blue (`V23`, on the
        canvas) versus grey (`V24`, focus elsewhere); nothing here decides
        the tone, it only asks for the repaint that reads it.

        MEASURED DEFECT: `tab` alone never repainted anything on this
        screen, so a card stayed painted blue after the keyboard had already
        left the canvas -- and closing the legend after such a `tab`
        inherited exactly that stale paint (`esc` restores the FOCUS
        correctly, `_restore_after_legend` already does that, but nothing
        told the canvas the tone underneath it was wrong before `?` was ever
        pressed).

        The canvas-only path (`_declare_after_layout`), never
        `refresh_canvas`: this must not rebuild the inspector or move focus
        itself, only redraw what the CURRENT focus already is.  Cheap when
        the change stays inside the canvas: `_declare_after_layout` no-ops
        whenever the `ViewState` it would paint -- `focus_owner` included --
        already equals the one last painted (`P1`)."""
        self._declare_after_layout()
        if isinstance(event.widget, FieldInput):
            # U2: while a field holds the keyboard, typing drafts and `j` types,
            # so the map-navigation hint lies.  Name the save key instead.
            self.query_one(HintLine).set_hint(self._field_hint(), self._seat_glyph("save_draft"))

    def on_descendant_blur(self, event: events.DescendantBlur) -> None:
        """The other half of `H2`: a field can blur to NOTHING (the
        inspector's own `escape`, `FichaInspector.action_leave_field` ->
        `set_focus(None)`) with no `DescendantFocus` to follow it. Without
        this the tone would stay on "focus elsewhere" after the keyboard had
        already left every region."""
        self._declare_after_layout()
        if isinstance(event.widget, FieldInput):
            # The field's draft hint (Inc-1c U2) is a borrow: hand the resting hint back.
            # If the keyboard landed on another field, that field already set its own
            # hint; if it landed on an attachment chip, the chip's `open attachment`
            # swap (`Z2`) needs the resting text to swap inside, so re-announce it.
            focused = self.app.focused
            if isinstance(focused, FieldInput):
                return
            self.query_one(HintLine).set_hint(self._resting_hint())
            if FichaInspector._is_chip(focused):
                self.query_one("#map-inspector", FichaInspector)._announce_open_attachment()

    # -- the docked legend (Inc-8 verdicts `F2`, `F9`, `G2`, `G5`) ----------
    # The legend reads `legend_view_left` and calls the two methods below;
    # nothing else does.  They move the view only through this screen's own
    # pan state and its clamp, never a renderer.

    #: `G5`: the revealed card keeps this many columns clear of the docked
    #: panel's left edge, so it does not sit flush against it.  Declared once
    #: here; `_pan_revealing_selection` is the only reader.
    REVEAL_MARGIN_CELLS = 2

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        """Undo Textual's own post-resume auto-focus once the legend that
        just closed left a restore pending (`INC8-P3-CR-F1` fix `c`).

        `Screen._update_auto_focus` answers this SAME `ScreenResume` and
        focuses the first focusable widget the instant `self.focused` is
        `None` at resume -- regardless of what was focused before `?` was
        pressed.  This handler is dispatched BEFORE that framework pass
        (Textual walks the MRO for a `ScreenResume` handler and this
        screen's own `on_screen_resume` sits ahead of `Screen`'s internal
        `_on_screen_resume` in it), so restoring inline here would still
        lose to the auto-focus that runs right after.  `call_after_refresh`
        posts a fresh message instead, which this screen's queue processes
        only once the `ScreenResume` already being handled -- auto-focus
        included -- is done with."""
        if self._legend_restore_pending is not None:
            pan_x, pan_y, focus_id = self._legend_restore_pending
            self._legend_restore_pending = None
            self.call_after_refresh(self._restore_after_legend, pan_x, pan_y, focus_id)

    def _restore_after_legend(self, pan_x: int, pan_y: int, focus_id: str | None) -> None:
        """The pre-legend focus wins over the auto-focus grab -- restored
        FIRST, so the one repaint that follows reads the real owner through
        `_focus_owner` instead of the transient one.  That ordering is what
        the operator saw as the selection card flashing from blue to grey on
        `esc` (`INC8-P3-UX-F1`, carried `UX-F7`).

        `INC8-CL-CR-F1`: the pan is re-clamped AFTER the restore, on the
        canvas's CURRENT size -- a resize while the legend was open (docked
        or modal; the legend keeps the operator's kept pan through either)
        can shrink the extent under `pan_x`.  At an unchanged size this is a
        no-op: the kept pan is already legal, so `A-109`'s "closing still
        restores the kept pan exactly" is unaffected.

        `INC8-FU-F6` (follow-up, non-blocking at Inc-8's close): this used to
        set the pan through `_move_pan`, which repaints on its own, and then
        repaint AGAIN below to show what `_reclamp_pan` had just clamped --
        two calls to `_declare_after_layout` for one restore, the second
        cheap only because it usually has nothing left to change.  The pan is
        set directly here instead (the same assignment `_move_pan` makes,
        without its repaint), clamped, and declared exactly once, over the
        FINAL value either step could have produced.

        `_reclamp_pan` reaches `_view_state`, which is `_PASS_FREE_READERS`'
        business, not this method's -- see that dict's own entry for why a
        stale search memo cannot corrupt what `_reclamp_pan` computes here
        (`test_search.py`)."""
        widget = None
        if focus_id is not None:
            matches = self.query(f"#{focus_id}")
            if len(matches):
                widget = matches.first()
        self.set_focus(widget)
        self.pan_x, self.pan_y = pan_x, pan_y
        self._reclamp_pan(*self._canvas_size())
        self._declare_after_layout()

    # The coverage strip's budget: A COUNT CEILING AND A CELL BUDGET, and the
    # second exists because the first alone shipped broken.
    #
    # A count cap bounds ENTRIES; it does not bound CELLS, and titles are
    # file-derived.  The first revision capped 24 entries and appended the
    # declaration and the legend LAST, so at 80 columns those 24 entries wanted
    # about five rows and the clip ate entries 20-23, the declaration, and the
    # whole legend -- leaving the operator four coverage glyphs with no key, on
    # a strip still reporting its full three rows.  Measured: with short titles
    # the legend is lost from TWENTY branches up at 80 columns, and on a large
    # graph 118 was the ONLY width in {60, 70, 80, 100, 118} where the
    # declaration survived at all.
    #
    # `_HINT_BRANCH_CELLS` above records this same lesson in its own words -- a
    # fixed cell count fits at 118 and WRAPS at 80 -- and this is the second
    # surface to learn it.  So the entries take the ROW'S REMAINDER: the
    # caption, the legend and the declaration are reserved FIRST and the entries
    # fill what is left.  The affordances outrank the entries, exactly as they
    # do on the hint line.
    # THERE IS NO SEPARATE COUNT CEILING, and its absence is a finding rather
    # than a simplification.  A `MINIMAP_BRANCHES = 24` sat here beside the cell
    # budget, and a mutant setting it to `10**9` left the whole suite GREEN --
    # measured first by both independent reviews, then reproduced here after the
    # budget landed.  The reason is not a missing oracle: `min(24, budget //
    # per_entry)` is decided by the BUDGET at every width below roughly 162
    # columns, so the ceiling had no work left to do.  Two bounds where one does
    # the work is the duplication this batch keeps paying for; the redundant one
    # is gone, and the arm tests the bound that actually binds.
    #
    # Must equal the stylesheet's `max-height` for `#map-minimap`.  Two
    # spellings of one number is how they drift, so an arm asserts the two agree
    # rather than trusting this comment to be read.
    MINIMAP_ROWS = 3
    _MINIMAP_CAPTION_CELLS = 14
    _MINIMAP_LEGEND_CELLS = 37
    _MINIMAP_DECL_CELLS = 26
    _MINIMAP_NAME_CELLS = 12
    # a name, a space, the glyph, and the three-cell gap after it
    _MINIMAP_ENTRY_OVERHEAD = 5

    # The meter's step ceiling.  24 was measured during `Inc-4c`'s F-2 work as
    # the value that takes this region to two rows on a 12002-node graph; with
    # the minimap and this strip now both bounded in the stylesheet it is one
    # row at 118 columns and fits inside the strip's 3 at 80.
    METER_STEPS = 24

    # The chrome around a toast's detail: the leading space, the label, and the
    # three-cell gap before the detail starts.
    _TOAST_CHROME_CELLS = 4

    # Widget id -> the `FOCUS_OWNERS` name that id stands for.  Bare ids, not
    # `#`-prefixed strings: nothing here is a CSS selector, and synthesising one
    # to compare against another string that merely looks like one silently
    # compares "#None" for every unnamed widget.
    _FOCUS_REGIONS = (
        ("map-rail", "rail"),
        ("map-inspector", "inspector"),
        ("map-canvas", "canvas"),
    )

    def _focus_owner(self) -> str:
        """Which region holds the keyboard, as one of `FOCUS_OWNERS`.

        Derived from the app's real focused widget rather than tracked
        separately: a second copy of "where the focus is" is a copy that goes
        stale, and the stale copy is the one the canvas would paint from.
        Returns `""` when nothing is focused, or when the focused widget belongs
        to no declared region -- the value that paints what the tree painted
        before this field existed.

        MEASURED: `#map-canvas` is `can_focus=False`, so `"canvas"` is not
        reachable through the real wiring today and the focused tone is arrived
        at via the `""` fallback.  The entry is kept because it is correct the
        moment the canvas becomes focusable, but a reader should not assume it
        is live (`B-53`).

        `""` IS ALSO THE HONEST ANSWER ON A NARROW TERMINAL, and that is not a
        defect: below `MIN_CANVAS_WIDTH`, `_apply_region_visibility` auto-hides
        the rail and the inspector, so nothing focusable remains and the focus
        chain is legitimately empty.  An earlier revision read that as "tab
        drops focus on this screen" and carried it as a defect -- measured only
        at the 80x24 default test size.  At 118x34 the chain is
        `[map-rail, insp-title, insp-state, insp-notes]` and tab traverses
        normally.  Retracted in `A-96`.
        """
        node = getattr(self.app, "focused", None)
        while node is not None:
            node_id = getattr(node, "id", None)
            for region_id, owner in self._FOCUS_REGIONS:
                if node_id == region_id:
                    return owner
            node = getattr(node, "parent", None)
        return ""

    # -- the card draft: save, guard, failure (US-001) ---------------------
    # The inspector holds the draft; this screen, which owns the graph and the
    # store, is the only thing that writes it.  `widgets -> store` is banned.

    UNDO_DEPTH = 20

    def action_open_ficha(self) -> None:
        node = self.graph.nodes.get(self.nav.cursor or "")
        if node is None:
            return
        linked = node.linked_map_id()
        if linked:
            crumb_back = self._current_crumb() + [node.ficha.title or node.id]
            self._guard_draft(lambda: self.app.push_screen(MapScreen(linked, source_crumb=crumb_back)))
            return
        self.app.push_screen(_FichaScreen(node, self.graph))

    #: Above this many cells the export ANNOUNCES ITSELF before it freezes the
    #: pump.  A JUDGEMENT, named as one, and deliberately NOT derived from a
    #: time: this seam's whole lesson is that cost is not a function of cells,
    #: so any cells-to-seconds threshold would be that same false universal a
    #: third time.  The notice therefore states the EXTENT and promises no
    #: duration.  Roughly a quarter of the budget, which on the measured shapes
    #: is about where an export stops being instantaneous on any terminal.
    EXPORT_DECLARE_CELLS = 90_000

    #: How long the export yields so the notice can actually REACH THE SCREEN.
    #: MEASURED, and it is why this action is `async`.  A notice that arrives
    #: after the freeze it warns about is an apology, not a declaration -- and
    #: three cheaper shapes were measured and REJECTED: notifying then blocking
    #: in the same handler paints the toast 404 ms LATE, `call_after_refresh`
    #: 403 ms late, and an async action yielding with `sleep(0)` 403 ms late.
    #: Only a real yield lets the pump mount and paint the toast first (+50 ms,
    #: measured).  So declaring the wait DOES need async, and this constant is
    #: the whole of what that costs.
    EXPORT_DECLARE_PAUSE = 0.05

    #: How many times `_export_view_state` may grow the canvas looking for the
    #: size at which the whole map fits.  MEASURED, not guessed, and measured by
    #: COUNTING THE CALLS THIS LOOP MAKES rather than by replaying it: across
    #: the pan fixture, 200- and 1000-long chains, 200/500/4001-wide fanouts, a
    #: 50x400-character title set and three wide-and-deep shapes, the extent
    #: settles after exactly ONE growth step -- `layered._geometry` stops
    #: shrinking `card_w` once the width is generous, so the second probe
    #: already fits.
    #:
    #: AN INDEPENDENT PASS MEASURED TWO on its own shape set, and that number is
    #: named here rather than reconciled away: six is headroom over both, and a
    #: docstring quoting only the author's own figure is the declaration family
    #: again.  Six is headroom for a shape nobody has measured, not a prediction
    #: that six will ever be needed -- and the exhaustion path below REFUSES, so
    #: being wrong about it costs a refusal rather than a cropped artifact.
    EXPORT_EXTENT_STEPS = 6

    #: The export's area budget, in CELLS, and the number is DERIVED.
    #:
    #: IN CELLS BECAUSE CELLS ARE WHAT COSTS.  `Canvas.rows()` walks a dense
    #: `w x h` grid, so export cost tracks the map's BOUNDING-BOX AREA and not
    #: its node count.  `MAX_RENDER_NODES` bounds the wrong quantity here: a
    #: 1,801-node map that is wide AND deep at once carries roughly 23x the
    #: CELLS of a 4,002-node map that is only wide, and costs several times as
    #: much wall clock despite holding fewer than half the nodes.  Bounding
    #: nodes in this seam would license the expensive shape and refuse the
    #: cheap one.
    #:
    #: (The figures that stood here -- "169 s" and "14 s" -- are STRUCK for the
    #: same reason as the derivation below: both came from the profiler-
    #: contaminated harness and overstate wall clock by 5.3-5.6x.  The ORDERING
    #: they were cited for is real and survives re-measurement, so the claim
    #: stands on the cell ratio, which no instrument error touches, rather than
    #: on two seconds-figures that were never true.)
    #:
    #: THE TARGET IS **2 SECONDS** of synchronous freeze.  `action_export_svg`
    #: runs on the Textual message pump with no progress bar and no cancel, and
    #: beyond roughly two seconds an unresponsive TUI reads as hung rather than
    #: busy.  Time is what binds, not memory -- that part stands.
    #:
    #: BUT THE HEAP FIGURE IS STRUCK, AND IT IS THE FOURTH CLAIM OF THIS
    #: DOCSTRING'S FAMILY, ONE AXIS OVER.  It read "peak heap fits 18.9
    #: bytes/cell, so the whole budget below costs about 7 MB".  Measured with
    #: no clock read at all: 42.8 B/cell at fan 940, and 147.9 B/cell at fan
    #: 3,645 -- AT THE SAME CELL COUNT, and an independent reader measuring
    #: render plus `save_svg` together got 292.3 B/cell and 102 MB against the
    #: claimed 7.  A per-cell MEMORY rate varies with node density for exactly
    #: the reason given below for why no per-cell TIME rate may appear, so the
    #: same prohibition applies and no replacement figure is offered.
    #:
    #: EVERY PER-CELL DERIVATION THIS CONSTANT ONCE CARRIED IS STRUCK.  Two
    #: were written here in turn -- "4.907 us/cell, so 2.0 s / 4.907 us =
    #: 407,616, round down to 400,000", then its replacement "a measured
    #: bracket, 315,252 cells -> 1.801 s and 490,052 -> 2.631 s, so 2.000 s
    #: falls at 357,156, round down to 350,000; cross-checked by a
    #: through-origin fit at 5.4264 us/cell".  BOTH ARE FALSE, AND THEY ARE
    #: FALSE FOR THE SAME REASON: the harness that produced them
    #: (`sec_b68_real_cost.py`, then `b68_budget_probe.py`) calls
    #: `tracemalloc.start()` on the line BEFORE it takes `t0`, so an allocation
    #: profiler ran inside the whole timed region and inflated every point by
    #: 5.3-5.6x.  Measured clean, that bracket's own shape costs **0.301 s**,
    #: not 1.801 -- reproduced independently at 0.321 s and 0.331 s.
    #:
    #: A CORRECTION THAT CHANGES THE NUMBER BUT KEEPS THE INSTRUMENT HAS NOT
    #: CORRECTED ANYTHING.  That is why this is a strike and not an annotation:
    #: the second derivation was not a faithful record taken under an
    #: undeclared condition, it was the first defect re-run.  When a figure is
    #: wrong the question is whether the INPUT or the INSTRUMENT was wrong, and
    #: re-deriving from the same instrument reproduces the defect while looking
    #: like diligence.
    #:
    #: AND THE PER-CELL MODEL ITSELF IS WRONG, which is why no rate appears
    #: above.  Cost per cell tracks NODE DENSITY, not area, so a single rate
    #: cannot derive a cell budget in either direction -- which is why two
    #: independent passes that each sampled one shape family reached answers 6x
    #: apart: wide-and-deep is cheap per cell, wide-only is dense and expensive.
    #:
    #: (The span first written here, "0.955 to 3.27 us/cell, a 3.4x spread", is
    #: STRUCK with the universal below and for the same reason: it was measured
    #: over the same restricted region, at tall start heights only.  An
    #: independent pass measured up to ~53 us/cell once the start height is free
    #: -- roughly a 55x spread.  The QUALITATIVE claim, that the rate varies
    #: with density and so cannot be a single number, is what survives, and it
    #: is stated without a figure because no figure is safe here.)
    #:
    #: WHAT JUSTIFIES 350,000 IS UTILITY, AND *NOT* A TIME GUARANTEE.  THE TIME
    #: CLAIM THAT STOOD HERE IS STRUCK, AND IT IS THE SECOND DERIVATION OF THIS
    #: CONSTANT TO BE STRUCK FOR A DIFFERENT REASON THAN THE ONE BEFORE IT.
    #: It read: "the worst ACCEPTED shape -- 1,000 wide, 312,026 cells -- costs
    #: 1.447 s against the 2-second target, a margin of about 28%.  Nothing the
    #: budget admits crosses the target."  THE UNIVERSAL IS FALSE.
    #:
    #: WHY IT IS FALSE: the hunt varied GRAPH SHAPE and held the START HEIGHT
    #: fixed, and the start height is not a free choice -- it is
    #: `max(5, size.height - 10)`, set by the operator's TERMINAL, and it governs
    #: how much node DENSITY a fixed cell budget admits.  A SHORTER terminal
    #: gives a smaller `h`, so `w * h <= EXPORT_MAX_CELLS` admits a far WIDER
    #: map, and width is what costs.  Measured clean, the worst ADMITTED shape
    #: per terminal:
    #:
    #:     118x40 ->   940 wide, 349,711 cells ->  1.91 s   (under)
    #:     118x35 -> 1,121 wide, 349,778 cells ->  2.41 s   (1.2x over)
    #:      80x24 -> 1,944 wide, 349,935 cells ->  5.94 s   (3.0x over)
    #:     118x20 -> 2,651 wide, 349,943 cells -> 10.38 s   (5.2x over)
    #:     118x11 -> 3,645 wide, 349,928 cells -> 17.73 s   (8.9x over)
    #:
    #: It is over target at 80x24, the classic default, and over target at the
    #: very terminal the struck sentence was measured on.
    #:
    #: THIS IS `C-31` AT THE SEARCH RATHER THAN THE INSTRUMENT, and it is the
    #: corollary minted one revision earlier, applied to its own author: the
    #: previous derivation was struck for a contaminated INSTRUMENT, the
    #: instrument was fixed, and the SEARCH was left holding a governing
    #: variable fixed.  Correcting how you measure does not correct what you
    #: measured over.
    #:
    #: NO SAFE-SIDE TIME CLAIM IS MADE HERE, AND THE THIRD ATTEMPT AT ONE IS
    #: STRUCK ALONGSIDE THE OTHER TWO.  It read: "at start heights of about 30
    #: rows and up, the worst admitted shape stays under 2 s.  Below that it
    #: rises monotonically as the terminal shortens."  NEITHER HALF SURVIVES,
    #: but FOR DIFFERENT REASONS, and the first reason is not the one first
    #: recorded.
    #:
    #: THE SAFE SIDE IS NOT A PROPERTY OF THIS CODE AT ALL.  It was first
    #: recorded here as FALSE, on 4-of-9 runs over 2 s at start height 30 and an
    #: independent 7-of-9.  A SECOND READER THEN FAILED TO REPRODUCE IT
    #: ENTIRELY: 27 runs of the identical shape, 0 over 2 s, 1.333 to 1.662 s,
    #: on artifact bytes identical to both other parties'.  Three measurements
    #: of the same work: 0/27, 4/9, 7/9.  SO THE SENTENCE DESCRIBES A
    #: MACHINE-SESSION, NOT `mapper` -- and that is a BETTER ground for striking
    #: it than "false", because "false" invites a fourth CORRECTED number while
    #: this rules the whole claim shape out.  The 2-second boundary sits inside
    #: between-machine variance, so an upper quantile taken here would have
    #: RATIFIED the struck sentence on one machine and refuted it on another.
    #:
    #: THE ROOT CAUSE IS STILL A STATISTIC, and the failed reproduction sharpens
    #: it rather than weakening it.  The 1.91 s behind the sentence was a
    #: MINIMUM.  Best-of-N is the right statistic for demonstrating a BREACH --
    #: if the minimum exceeds the bound then every run does -- and the WRONG one
    #: for demonstrating SAFETY, where nothing about the other runs follows from
    #: it.  Measured across the three parties, the MINIMUM was the most
    #: reproducible statistic (1.321 vs 1.333, 0.9% apart) and the tail the
    #: least (1.617 vs 2.146), so quoting a minimum is wrong TWICE: it cannot
    #: bound a maximum, AND it is the statistic most likely to look stable --
    #: which makes a safety claim built on it look robust exactly when it is not.
    #:
    #: EVERY SECONDS-FIGURE SURVIVING IN THIS BLOCK IS `IRREDUCIBLY A READING`,
    #: not a property: taken on one Windows machine, best-of-N unless stated,
    #: n as given.  They are kept because they show the SHAPE of the cost, and
    #: none of them may be used as a bound.
    #:
    #: "Monotonically" is false: the curve rises and then PLATEAUS.  ITS CAUSE
    #: AND ITS BOUNDARY WERE BOTH STATED WRONG HERE AND ARE CORRECTED -- a wrong
    #: CAUSE is worse than a wrong number, because it is what the next reader
    #: reasons from.  The text said "the start height FLOORS at 5: every
    #: terminal at or below 15 rows admits the identical shape".  Measured, the
    #: extent settles at `max(8, start + 1)` where 8 is THE MAP'S OWN CONTENT
    #: HEIGHT -- so the plateau runs to terminal 17, not 15, and it is the
    #: content-height floor that causes it, not the start-height floor of 5.
    #: Proof that the floor of 5 is not the cause: changing it to 1 leaves the
    #: extent at terminals 9 through 17 completely unchanged.
    #:
    #: Three runs of that identical plateau work measured 18.9 s, 21.0 s and
    #: 18.9 s -- a 2.1 s spread on one idle machine, which is its own argument
    #: against any wall-clock sentence living in this docstring.
    #:
    #: THE FAMILY, THREE DEEP: the first derivation was struck for a
    #: contaminated INSTRUMENT, the second for a SEARCH that held a governing
    #: variable fixed, and this one for the STATISTIC.  Each correction was
    #: sound and each left the next layer untouched.
    #:
    #: WHAT IS TRUE AND CLOCKLESS, and it is the MECHANISM rather than a number:
    #: THE SAME MAP IS ADMITTED OR REFUSED DEPENDING ON THE TERMINAL.  A
    #: 3,645-wide fanout fits this budget at start height 5 and is refused at
    #: 30, because the budget bounds `w * h` while the start height is chosen by
    #: the operator's terminal.  That is precisely why A CELLS-ONLY BUDGET
    #: CANNOT EXPRESS A TIME BOUND: cost depends on `w` and `h` separately and
    #: this constant constrains only their product, so no value of it makes any
    #: universal true.  Making the freeze genuinely bounded needs a different
    #: BOUND, which is a ruling rather than a constant -- and until there is
    #: one, the export DECLARES the wait instead of promising its length.
    #: `test_the_SAME_map_is_admitted_or_refused_by_the_TERMINAL` pins that
    #: mechanism without a clock, so it cannot flake and cannot drift.  It pins
    #: the BOUNDARY (17 admitted against 18 refused) rather than two far-apart
    #: points, because the far-apart version missed three mutations of the very
    #: expression it existed to pin.
    #:
    #: AND THE TERMINAL IS NOT THE ONLY GOVERNING VARIABLE -- THE VIEW IS A
    #: SECOND ONE, named here because leaving it inherited is how all three
    #: struck sentences went wrong.  `outline` and `radial` DECLINE the resize
    #: (they hold no viewport), so the export keeps a terminal-sized state and
    #: this budget can never refuse in those views at all: the same fan-3,645
    #: map that is refused in `layered` at a 40-row terminal is admitted in both
    #: of them.  Every figure in this block is a `layered` figure.
    #:
    #: DECLARED GAP, measured rather than assumed: the floor of `5` in
    #: `max(5, size.height - 10)` is pinned by NOTHING.  Changing it to 1 leaves
    #: every verdict unchanged, because the content-height floor of 8 dominates
    #: for any map large enough to approach the budget -- so the floor is
    #: observable only in the EXTENT of a small map, where the verdict never
    #: moves.  It is a mandate nothing reads, and closing it needs an extent
    #: arm rather than a budget one.
    #:
    #: SO THE CONSTANT RESTS ON UTILITY ALONE, which is untouched and never
    #: depended on the arithmetic: a 72001x24004 SVG is unreadable by anybody
    #: whatever it costs to produce.  A proposal to relax the budget to ~2.12M
    #: cells is still REFUSED -- it generalised from the cheap shape family and
    #: would admit wide-only maps costing many seconds more than these.
    #:
    #: THE UTILITY GROUND IS UNTOUCHED AND STANDS ALONE.  Even were the cost
    #: free, a 72001x24004 SVG is not an artifact any recipient can read, so
    #: `A-100` does not rest on the arithmetic at all -- which is precisely why
    #: striking the arithmetic costs the ruling nothing.
    #:
    #: WHAT THAT REFUSES -- AND EVERY ROW BELOW IS TERMINAL-SCOPED, which this
    #: list did not say and which makes some of its rows conditional rather than
    #: factual.  All of it was taken at `118x34`, identified after the fact by an
    #: independent reader reproducing the 500-wide row at exactly 150,025 cells.
    #: The CHAIN rows are content-bound and hold at any terminal; the FANOUT rows
    #: are not, and at least one INVERTS: the 500-wide fanout is admitted at
    #: `118x67` (348,058) and REFUSED at `118x68` (354,059).  Measured at
    #: `118x34`: the pan fixture (4,320 cells), a 500-wide fanout (150,025), a
    #: 200-long chain (96,480) and 50 nodes carrying 400-character titles
    #: (15,025) all export.  A 1,000-deep chain (480,480) and a 4,001-way fanout
    #: (1,200,325) are REFUSED.  The wide-and-deep boundary is MEASURED rather
    #: than interpolated: 161 nodes (315,252 cells) export, 201 nodes (490,052)
    #: do not -- that pair alone was NOT re-verified by the reader who found the
    #: scoping defect, because its fixture is ambiguous from the text, so it is
    #: flagged rather than confirmed.
    #: That is the intended consequence rather than a regrettable one: a
    #: 120x4004 artifact is four thousand rows tall and a 48013-column one is
    #: unreadable by anybody, so the refusal costs a file nobody wanted.  `f`
    #: focuses a subtree, which is the route the refusal message names.
    EXPORT_MAX_CELLS = 350_000

    def action_palette(self) -> None:
        self.app.action_palette()

    def action_help(self) -> None:
        self.app.action_help()
