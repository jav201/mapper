"""`MapScreen` — the map view (moved verbatim from `mapper/app.py` at
`2026-10-09-modular-batch` B0).

The class body is unchanged; Spine B (B1–B11) moves its concerns into sibling mixin
modules of this package.  `mapper.app` and `mapper.screens.map` re-export
`MapScreen`, so `from mapper.app import MapScreen` keeps resolving (LLR-MOD.3.1).
This module never imports `mapper.app` (LLR-MOD.6.2).
"""

from __future__ import annotations


from rich.text import Text
from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.geometry import Region
from textual.screen import Screen
from textual.widgets import Input, Static

from mapper import darkside
from mapper.diff import DiffResult, git_diff
from mapper.keymap import groups_for_keybar, label_for, SCOPE_MAP
from mapper.model import Ficha, Graph, Node
from mapper.motion import pulse_cursor
from mapper.screens.common import (
    COUNT_REGION_ID,
    keybar_groups,
    map_hint,
    MapHintLine,
    PAN_EDGE_HINT,
    PAN_INERT_HINT,
    screen_bindings,
)
from mapper.screens.map.navigation import NavigationModel
from mapper.screens.prompt import _FichaScreen
from mapper.store import MapStore
from mapper.views.layered import (
    _geometry as layered_geometry,
    header_rows,
    LayeredRenderer,
    painted_ids,
    pan_extent,
)
from mapper.views.outline import (
    header_rows as outline_header_rows,
    OutlineRenderer,
    painted_ids as outline_painted_ids,
)
from mapper.views.radial import (
    header_rows as radial_header_rows,
    painted_ids as radial_painted_ids,
    RadialRenderer,
)
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


class MapScreen(SearchingOps, NavOps, DraftsOps, EditingOps, FocusModeOps, UndoOps, OpeningOps, ExportingOps, HintsOps, Screen):
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

    def action_collapse_branch(self) -> None:
        """Fold or unfold the branch under the cursor — LLR-N06.2.1, LLR-N06.2.2.

        The rail used to own this and mutate its own `collapsed` set, so the
        canvas never learned about a fold at all.
        """
        nid = self.nav.cursor
        if nid is None:
            return
        if nid not in self.folded and not self.graph.children_of(nid):
            # LLR-N06.2.2.  The natural implementation paints a pill reading
            # `+0`, which declares a hidden count of zero and is worse than
            # nothing; the product already answers "nothing to do" out loud
            # elsewhere (`next_gap` toasts `cobertura completa`).
            self.notify(
                "this node has no descendants",
                title="nothing to fold",
                severity="information",
                markup=False,
            )
            return
        self.folded = (
            self.folded - {nid} if nid in self.folded else self.folded | {nid}
        )
        self.refresh_canvas()

    # -- pan (HLR-N06.1) ---------------------------------------------------
    # One press moves the window by this many cells.  A single cell makes the
    # chord feel dead on a map that overflows by 60 columns; a whole viewport
    # loses the operator's place.  Vertical is smaller because a card row is
    # 4-5 cells tall and a page-sized jump skips whole levels.
    PAN_STEP_X = 8
    PAN_STEP_Y = 4

    @staticmethod
    def _clamp_pan(offset: int, extent: int, span: int) -> int:
        """LLR-N06.1.2 — the legal range is `[0, max(0, E - W)]`, always.

        The `E < W` case is why the outer `max(0, ...)` is there rather than a
        bare `extent - span`: a map smaller than the canvas has a legal pan
        range of exactly one position, and a negative upper bound would let
        `min` return it and slide the map off screen on a small graph.
        """
        return max(0, min(offset, max(0, extent - span)))

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

    def _header_rows(self, wrap_w: int) -> int:
        """The header's measured physical height for the frame about to be sized.

        WRAPPED AT THE WIDGET'S CONTENT WIDTH, WHICH IS NOT `w - 2`.  An earlier
        revision wrapped at `w - 2` and justified it as "the canvas widget's
        content width".  Measured across a 943-configuration terminal sweep on
        `legacy`, it is not: `#map-canvas` is `width: 1fr; height: 100%` with no
        padding and no border, so its content width equals its REGION width, and
        that region is `_canvas_width()` at 724 of the 943 and `_canvas_width()
        - 2` at the other 219.  At terminal (28,17) the content width is 28, not
        26, and the frame shows three rows because Rich WORD-WRAPS a 55-cell
        line at 28 -- not because of a two-column inset.  The old reading reached
        the right row count through the wrong mechanism, which is why it was
        compensating rather than causing.  So the measured width is passed in.

        `wrap_w` comes from the same `content_size` read `_canvas_size` uses to
        price the body, so the guard and the subtraction cannot disagree about
        which frame they are describing.

        THE CHARGE IS PER RENDERER, AND IT USED TO BE LAYERED'S IN EVERY VIEW.
        `_canvas_size` has no renderer branch while `refresh_canvas` picks the
        renderer separately, so outline and radial were priced with layered's
        header.  MEASURED over a ten-width sweep from 20 to 118, with layered's
        own first line as the positive control -- `layered.header_rows` agrees
        with it at ALL TEN widths, which is what makes the other two columns a
        finding rather than instrument error:

            w    charged   layered   outline   radial
            20      3         3         1        3
            24      3         3         1        2
            28      3         3         1        2
            34      2         2         1        2
            40      2         2         1        2
            50+     2         2         1        1

        Outline is overcharged at EVERY width in the sweep; each overcharged row
        is a body row the region could have shown and the renderer was never
        told about.
        THE DISPATCH IS STRICT AND THIS CALL SITE IS NOT, AND THE ASYMMETRY IS
        DELIBERATE.  `_painted_ids_for` raises for an unregistered renderer and
        lets that raise escape, because `frozenset()` is a legitimate declaration
        and a BROKEN one must not present as an ABSENT one.  I copied that shape
        here and it was wrong: the CONSEQUENCE does not transfer.  A declaration
        that raises costs a numeral; a CHARGE that raises means the canvas cannot
        be sized at all, and `_canvas_size` runs BEFORE `refresh_canvas`'s guard,
        so the raise escaped the one path `LLR-R01.4` ratifies as survive-
        anything.

        FIRED, AND IT IS WHAT CAUGHT THIS.  `TC-R08` installs a renderer that is
        not one of the three and asserts the app still paints "no se pudo dibujar
        el mapa" rather than dying; both of its parameter cases failed against the
        strict version.  So strictness stays where it can be ACTED on -- the
        dispatch, pinned by its own arm -- and the drawing path DEGRADES to
        layered's charge, which is a wrong row budget on a frame that is about to
        paint a failure notice anyway.
        """
        try:
            charge = self._header_rows_for(self._current_renderer())
        except LookupError:
            charge = header_rows
        return charge(self.graph, self._canvas_width(), wrap_w)

    def _header_rows_for(self, renderer):
        """The function this renderer's header charge comes from.

        IDENTITY, NEVER `getattr`, matching `_painted_ids_for` and for the same
        reason (`A-98`, ruling `02j`): a probe answers "this view has no header"
        and "this view's charge is broken" with the same silence.

        THE RADIAL RESIDUE IS CLOSED (`S-D`).  Until this stage radial was an
        EXPLICIT fallback to `layered.header_rows` -- stated here and pinned by
        an arm so the fix would redden the arm rather than close the hole
        silently, which is this batch's `AT-058` doctrine applied to a CHARGE.
        The residue was real and it was measured, not suspected: on the arm's own
        fixture, layered's charge EXCEEDED radial's own first line at SEVEN of
        the ten swept widths -- 24, 28, and every width from 50 up -- and each
        overcharged row is a body row the region could have shown and the
        renderer was never told about.  `radial.header_rows` now equals radial's
        own first line at TEN of ten, which is the equality form the other two
        entries hold to.

        An unregistered renderer RAISES.  A future view that genuinely has no
        header gets an explicit entry returning a charge of one, exactly as
        `outline` and `radial` got explicit entries in `_painted_ids_for`.
        """
        if renderer is self.renderer:
            return header_rows
        if renderer is self.outline_renderer:
            return outline_header_rows
        if renderer is self.radial_renderer:
            return radial_header_rows
        raise LookupError(f"no header charge registered for {renderer!r}")

    def _canvas_width(self) -> int:
        """Columns the canvas renderer is given.  Floors at 20 (`B-61`'s band)."""
        size = self.size or self.app.size
        # The canvas no longer owns the full width: the inspector takes a fixed
        # column beside it, so render to what is actually left.
        return max(20, size.width - self._chrome_width())

    def _canvas_size(self) -> tuple[int, int]:
        """The `(w, h)` the canvas renderer is given, in ONE place.

        `refresh_canvas`, the pan clamp and the overflow helper must all price
        the same frame; three inline copies of this arithmetic is how they start
        disagreeing about which nodes were on screen.

        `h` COMES FROM THE WIDGET'S REGION, not from `size.height - 8`, and that
        is a defect fix US-N06 forced into the open.  Measured on `legacy`: at a
        50x20 terminal the shipped arithmetic asked for 12 rows into a region
        that holds 8, so four nodes were drawn into a void -- hidden, with
        nothing declaring them, which is the story's promise inverted.  Across a
        nine-size sweep the shipped `h` made the declared painted set disagree
        with the composited frame at five sizes; the region-derived `h` agrees at
        all nine.

        THE THREE BRANCHES ARE THREE DIFFERENT FRAMES, and an earlier revision
        collapsed the middle one into the last.  `region.height == 0` is the
        genuinely pre-layout case, and only there is `size.height - 8` an honest
        guess.  A region that is REAL but no taller than the header is not
        pre-layout at all -- it is a short terminal, and the header has eaten the
        whole region.  Returning `region.height` there left `row_limit = h - 1`
        believing canvas row 0 survived, so `painted_ids` declared a node painted
        that leaves no trace: measured on `legacy` at (31,18), (50,14) and
        (100,10), all 8 nodes hidden and the indicator declaring 7.  Returning 1
        makes `row_limit` 0, which is the truth -- no body row is paintable.

        BOTH USES OF THE HEADER'S HEIGHT TAKE THE MEASURED VALUE, and they have
        to move together: the guard asks "has the header eaten the whole
        region", the subtraction asks "how many body rows are left".  Charging a
        constant 2 in either place is `B-61`.  `render` emits `1 + (h - 1)`
        LOGICAL lines and the widget spends `rows` PHYSICAL rows on the first of
        them, so the frame shows `region.height - rows` body rows and the
        renderer must be told `h - 1 = region.height - rows`.
        """
        w = self._canvas_width()
        canvas = self.query_one("#map-canvas", Static)
        region = canvas.region
        if not region.height:                    # genuinely pre-layout
            size = self.size or self.app.size
            return w, max(5, size.height - 8)
        # The header is priced AFTER the region is known to be real, because the
        # width it wraps at is that region's content width -- there is no honest
        # value for it above this line.
        rows = self._header_rows(canvas.content_size.width or region.width)
        if region.height <= rows:                # real, but the header fills it
            return w, 1                          # row_limit == 0 -> nothing painted
        return w, region.height - (rows - 1)

    def _consumes_pan(self, renderer) -> bool:
        """Does THIS renderer read the pan offsets it would be given?

        IDENTITY, NEVER `getattr`, matching `_header_rows_for` and
        `_painted_ids_for` for the same reason (`A-98`, ruling `02j`): a probe
        must not answer "this view has no pan" and "this view's pan is broken"
        with the same silence.

        MEASURED, NOT INFERRED (`PAN-1`).  `views/outline.py` and
        `views/radial.py` hold ZERO code references to `pan_x`/`pan_y` -- the one
        textual match in outline is prose inside a docstring -- while
        `views/layered.py` consumes both.  Driven end to end with pan set
        DIRECTLY, so no keypress side effect could be mistaken for the thing:
        layered's picture moves, outline's and radial's never do, at any size.

        AND THE MANIFESTATION WAS WORSE THAN A WRONG NUMBER.  The screen computed
        a LAYERED extent for every view and clamped `pan_x`/`pan_y` against it,
        so in the two views that ignore pan the operator's keys moved nothing
        while internal state advanced -- the app held a pan the picture never
        reflected.  A lying affordance of the MOTION kind, the same family as the
        `esc` rulings `#D38`/`#D43`: an affordance that teaches a rule which
        silently stops holding.

        RADIAL DOES NOT WANT PAN, and that is a ruling rather than an omission
        (coordinator 2026-09-18).  Its navigation is focus-based and its layout
        is polar around the selected node, so a viewport is a category error
        rather than a missing feature.  The fix is therefore NOT "give radial
        pan" but "stop advertising and advancing pan on behalf of a view that
        does not consume it".  Reversible if a later measurement shows radial
        genuinely wants a viewport.

        EVERY RENDERER IS ENUMERATED AND AN UNREGISTERED ONE RAISES, exactly as
        `_header_rows_for` and `_painted_ids_for` do.  The first version of this
        method fell through to `False`, which is the defect its own citation of
        `02j` forbids: a fourth renderer added tomorrow would be SILENTLY
        classified as non-panning, with nothing anywhere saying so.  `False` is
        a LEGITIMATE answer here, which is exactly why it may not double as the
        answer for "I have never heard of this renderer".

        THE RAISE IS UNGUARDED ON THE PAN PATH, AND THAT IS A DECISION RATHER
        THAN AN ACCIDENT.  Of the three dispatches this one alone is called from
        `_pan` BEFORE its `try`, so an unregistered renderer plus one pan
        keypress would escape into the message pump -- the sink that `except`
        exists for.  The sibling `_header_rows_for` MEASURED ITS WAY TO THE
        OPPOSITE ANSWER and softens its raise in the drawing path, on the
        argument that "a declaration that raises costs a numeral; a charge that
        raises costs the whole picture".  That argument does not transfer: a
        charge is needed to paint EVERY frame, so degrading keeps the map on
        screen, whereas pan consumption is consulted only when the operator
        presses a pan key -- and degrading it would silently reinstate exactly
        the defect this raise was added to remove.  A view whose pan class is
        unknown must not be guessed at on the operator's behalf.

        WHAT THAT COSTS, stated here rather than discovered later: if a fourth
        renderer is ever constructed without an entry here, the first pan press
        takes the app down.  That is a code defect failing loudly the moment it
        is first exercised, which is this batch's stated preference, and it is
        unreachable in a shipped build -- `app.py` constructs exactly three
        renderers and an arm pins that an unregistered one raises.
        """
        if renderer is self.renderer:
            return True
        if renderer is self.outline_renderer or renderer is self.radial_renderer:
            # RULED, not absent: focus-based / polar navigation (2026-09-18).
            return False
        raise LookupError(f"no pan consumption registered for {renderer!r}")

    def _reclamp_pan(self, w: int, h: int) -> None:
        """Pull both offsets back into range for the frame about to be drawn.

        A resize or a fold shrinks the extent under a pan that was legal a
        moment ago, and `LLR-N06.1.2` says the system shall not ACCEPT an offset
        outside the range -- not merely that it shall not produce one.

        A VIEW THAT DOES NOT CONSUME PAN DECLINES TO CLAMP, and HOLDS the
        offsets (`PAN-1`).  Clamping against `layered`'s extent here would be the
        same renderer-independent application of a layered-specific helper that
        defect 2 was, one seam over -- so the branch exists.  But declining to
        clamp is the whole of what it needs to do.

        IT MUST NOT ZERO THEM, AND THE FIRST VERSION OF THIS BRANCH DID.
        `refresh_canvas` calls this on every repaint, so zeroing here threw the
        operator's pan away on a mere excursion into outline or radial -- no key
        pressed, nothing declared, offsets gone, measured `(48, 0)` -> `(0, 0)`
        on a round trip.  That is the SAME FAMILY this increment exists to
        close, one seam over: `PAN-1`'s charge is "the app held a pan the
        picture never reflected", and zeroing shipped "the app discarded a pan
        the operator set, without saying so".  The non-consumer ignores the
        offsets while it is on screen, and this method clamps them honestly on
        the way back.
        """
        if not self._consumes_pan(self._current_renderer()):
            return
        (extent_x, span_x), (extent_y, span_y) = pan_extent(
            self.graph, self._view_state(w, h)
        )
        self.pan_x = self._clamp_pan(self.pan_x, extent_x, span_x)
        self.pan_y = self._clamp_pan(self.pan_y, extent_y, span_y)

    def _pan(self, dx: int, dy: int) -> None:
        # INERT AND DECLARED, never inert and silent (`PAN-1`, ruling 2026-09-18).
        # Before this, a pan key in outline or radial advanced `pan_x`/`pan_y`
        # against a LAYERED extent and repainted a picture that consumes
        # neither, so the operator got no movement, no message, and a hidden
        # offset that outlived the view.  Saying so is the whole fix: a key that
        # does nothing and explains why is an honest affordance; one that does
        # nothing quietly is indistinguishable from a broken keyboard, which is
        # the confusion `US-N06` exists to remove.
        if not self._consumes_pan(self._current_renderer()):
            self.query_one(HintLine).set_hint(PAN_INERT_HINT)
            return
        w, h = self._canvas_size()
        try:
            (extent_x, span_x), (extent_y, span_y) = pan_extent(
                self.graph, self._view_state(w, h)
            )
        except Exception:
            # Same argument as `refresh_canvas`'s guard, and the same sink-scoped
            # shape: this runs inside the message pump, `_tree_layout` raises by
            # design on a graph that is not a tree, and an escape here kills the
            # app with the operator's unsaved edits in it.  Measured on a cyclic
            # graph before this guard: one `L` press and `app.is_running` went
            # False.  A frame that cannot be laid out cannot be panned, so the
            # answer is the one the edge already has a declaration for.
            self.query_one(HintLine).set_hint(PAN_EDGE_HINT)
            return
        nx = self._clamp_pan(self.pan_x + dx * self.PAN_STEP_X, extent_x, span_x)
        ny = self._clamp_pan(self.pan_y + dy * self.PAN_STEP_Y, extent_y, span_y)
        if (nx, ny) == (self.pan_x, self.pan_y):
            # HLR-N06.1's unwanted-behaviour clause.  A silent no-op at the edge
            # is indistinguishable from a keyboard that stopped working, and
            # blank space past the content is indistinguishable from "the map
            # has nothing there" -- the exact confusion US-N06 exists to remove.
            self.query_one(HintLine).set_hint(PAN_EDGE_HINT)
            return
        self.pan_x, self.pan_y = nx, ny
        # CLEARED ON SUCCESS, and the omission was a real misdescription rather
        # than untidiness: the hint is set on a no-op and nothing ever unset it,
        # so on the shipped maps -- where `H`/`L` are no-ops at every width but
        # one -- it latched on the first sideways press and then sat there
        # describing every LIVE `J`/`K` as an edge the operator had not reached.
        self.query_one(HintLine).set_hint(self._resting_hint())
        self.refresh_canvas()

    def action_pan_left(self) -> None:
        self._pan(-1, 0)

    def action_pan_right(self) -> None:
        self._pan(1, 0)

    def action_pan_up(self) -> None:
        self._pan(0, -1)

    def action_pan_down(self) -> None:
        self._pan(0, 1)

    def _unpainted_ids(self) -> frozenset[str] | None:
        """The graph's nodes minus the ones the current render actually painted.

        LLR-N06.3.1 read literally: ONE set difference, and no fold count is
        added to a viewport count anywhere.  Summing the two double-counts every
        node that is both folded and off-screen, and the indicator then declares
        more hidden nodes than the graph contains.

        `None` -- not an empty set -- when the operator is in a view that
        declares nothing.

        THAT STATE NOW HAS NO OCCUPANT, and this docstring described the old one
        long after it was gone: it said `painted_ids` lived on `views/layered.py`
        ONLY, that `outline` and `radial` hide nodes without declaring them, and
        that the hole was carried as `B-55`.  All three were true when written
        and all three are false now -- `B-55` closed across `layered` (Inc-3),
        `outline` (`Inc-B55a`) and `radial` (`Inc-B55b`), so every view the
        screen builds declares.

        The `None` branch is kept rather than deleted because it is the CONTRACT,
        not a description of today's view set: a future view that declares
        nothing by design gets an explicit `None` entry in `_painted_ids_for`,
        exactly as `outline` and `radial` had.  Answering that with a `getattr`
        probe would still convert a declared gap into a silent skip, which is why
        the dispatch is by identity.

        `None` ALSO when the layout itself failed.  `painted_ids` shares
        `_geometry` with `render`, so it raises on exactly the frames the canvas
        cannot draw -- and this helper is called from `refresh_canvas`, inside
        the message pump.  Letting that escape turns a contained, declared
        degradation ("no se pudo dibujar el mapa") into a dead app.  `None` is
        the value this helper already has for "this view declares nothing",
        which is the truthful answer for a frame that was never laid out.

        RESOLUTION HAPPENS OUTSIDE THE GUARD, AND THAT IS LOAD-BEARING
        (`AT-058`).  The `except` below is TOTAL, so a renderer with no entry in
        `_painted_ids_for` would be caught here and answered `None` -- and
        `None` means "this view declares nothing", which `LLR-N06.3.3` makes
        mean "nothing is hidden".  A BROKEN declaration would present as an
        ABSENT one.  `Inc-B55` is what makes this seam reachable by more than
        one renderer, so the two are separated BEFORE anything is wired through
        it: an unregistered renderer RAISES, and only a layout failure degrades
        to `None`.
        """
        declare = self._painted_ids_for(self._current_renderer())
        if declare is None:
            return None
        w, h = self._canvas_size()
        try:
            painted = declare(self.graph, self._view_state(w, h))
        except Exception:
            return None
        return frozenset(self.graph.nodes) - painted

    def _painted_ids_for(self, renderer):
        """The function this renderer declares its painted set through.

        IDENTITY, NEVER `getattr` (`A-98`, ruling `02j`): a probe answers "this
        view declares nothing" and "this view's declaration is broken" with the
        same `None`, which is the silent skip this batch keeps catching.

        `None` here means DECLARES NOTHING BY DESIGN, and it is an EXPLICIT
        entry rather than an absence -- `outline` and `radial` are the `B-55`
        hole, stated rather than omitted.  A renderer ABSENT from this mapping
        is a CODE DEFECT and raises, because `frozenset()` is a LEGITIMATE
        return for this helper's caller -- both degraded render paths produce
        one -- so an unregistered renderer answering with it would be a lie the
        strip paints as "nothing hidden".
        """
        if renderer is self.renderer:
            return painted_ids
        if renderer is self.outline_renderer:
            return outline_painted_ids
        if renderer is self.radial_renderer:
            # DECLARES SINCE `Inc-B55b`, through a cell-ownership replay rather
            # than a filter over `place()`: the canvas is last-write-wins and
            # records no owner, so deriving from placement over-declares
            # (`M-N06.3-b`).  The declared set was checked against the
            # composited frame and equalled it at every combination driven -- by
            # a SCRATCH PROBE at 16, and by the suite's own arms, which are 13
            # (10 `AT-059` plus 3 `AT-057`, the latter on `legacy` only). The
            # "16" belongs to the probe and is not reproducible from the tree,
            # which is why both numbers are given rather than the flattering
            # one.
            return radial_painted_ids
        raise LookupError(
            f"no painted_ids declared for {type(renderer).__name__}; add an "
            "explicit entry -- absence is a code defect, not a view with "
            "nothing to say"
        )

    def _park_focus(self) -> None:
        """Hand the keyboard back to the map itself."""
        self.set_focus(None)

    def _declare_after_layout(self) -> None:
        """Repaint BOTH declaring surfaces once layout is real — B-56 and B-60.

        `on_mount` paints before the compositor has given the canvas its region,
        so the declaration computed there describes a frame that does not exist.
        Measured on `legacy`, that is not a stale numeral but an ABSENT one: at
        50x20 and 60x20 -- ordinary sizes -- half the map was off screen and the
        strip said nothing at all, which `LLR-N06.3.3` makes mean "nothing is
        hidden".

        AND ORDINARY NAVIGATION DOES NOT HEAL IT.  Measured over nine keys, only
        `l` and `o` reconcile the surfaces; `j`, `k`, `h`, the arrow keys and
        `tab` do not -- at the root `j` is a no-op, so nothing repaints.  A
        reader who only LOOKS at the map, which is US-N06's whole use case,
        would otherwise keep two contradicting indicators indefinitely.  An
        earlier revision recomputed only the STRIP and carried the canvas
        header's own numeral as `B-60` on the claim that "any repaint at all
        reconciles them"; that claim was measured and is false, so the residual
        is closed here instead of narrated.

        A full `refresh_canvas` would also close it and would also re-`show` the
        rail and the inspector, moving the keyboard after `LLR-CNV.3.1` and
        `B-50` placed it -- measured, `call_after_refresh(refresh_canvas)`
        reddens the focus arm with `assert 'rail' == 'inspector'`.  So this
        repaints exactly the two surfaces that DECLARE and nothing that focuses.
        No `pulse_cursor`: this is a declaration repaint, not a cursor move, and
        a second breath on mount is motion the operator did not cause.
        """
        self._open_paint_pass()
        canvas = self.query_one("#map-canvas", Static)
        region = canvas.region
        w, h = self._canvas_size()
        # THE GUARD IS `P1` ITSELF, not a second mechanism.  `P1` says content
        # and geometry agree at rest; if they ALREADY agree, this re-render is
        # byte-identical and there is nothing to reconcile.  That is why it is
        # safe in a way "re-render only when the strip changed" would not be:
        # the predicate skipped on is the property the invariant asserts, so the
        # guard cannot drift from what it protects.
        #
        # AND IT IS THE WHOLE INPUT, NOT A PROJECTION OF IT.  Keyed on `(w, h)`
        # alone this sentence was FALSE and the security review fired it: content
        # depends on the renderer and every `ViewState` field, so a view switch
        # at one unchanged geometry let this skip while the strip repainted --
        # canvas declaring 7 in layered beside a strip declaring 5 in outline.
        #
        # It is not an optimisation looking for a problem.  MEASURED on an
        # 11999-node graph -- the largest `outline` will render -- one unguarded
        # settle pass costs 0.33 s at 118x34 and 0.28 s at 80x24, roughly
        # DOUBLING a repaint that already costs 0.36 s.  Arming the settle from
        # `refresh_canvas` without this would have shipped that.
        state = self._view_state(w, h)
        renderer = self._current_renderer()
        if (renderer, state) != self._rendered_for:
            try:
                text = renderer.render(self.graph, state)
            except Exception:
                # `refresh_canvas` has already painted its declared "no se pudo
                # dibujar el mapa" for this frame; overwriting it from here would
                # replace a stated degradation with a second copy of itself.
                pass
            else:
                canvas.update(text)
                self._rendered_for = (renderer, state)
        self.query_one(f"#{COUNT_REGION_ID}", Static).update(self._pagination_text())
        # ONE PASS IS NOT ENOUGH, AND THAT WAS `B-60`'s RESIDUAL.  This runs on
        # the first `call_after_refresh`, and at narrow terminals the region is
        # still reflowing then: instrumented at (31,16) the three passes saw
        # 31x1, then 29x2, and the region SETTLED at 31x3 afterwards, so both
        # declaring surfaces kept a numeral computed for a frame that no longer
        # existed -- the strip read 8 against a truth of 7.  So the declaration
        # follows the region until it stops moving, which is the condition it
        # actually needs and one a one-shot callback cannot express.  It
        # terminates because it re-schedules only while the region CHANGED, so
        # a settled layout costs exactly one extra no-op pass.
        if region != self._declared_for:
            self._declared_for = region
            self.call_after_refresh(self._declare_after_layout)

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

    def _current_renderer(self):
        if self.outline_mode:
            return self.outline_renderer
        if self.radial_mode:
            return self.radial_renderer
        return self.renderer

    @property
    def legend_view(self) -> str:
        """HLR-N16.2: the name of the view `?` explains, read from the same
        two booleans `_current_renderer` reads.  One name per view, the one
        the legend title carries (Inc-8 verdict `D5`, in English per the
        2026-09-29 language ruling), read from `darkside.VIEW_NAMES`; this
        screen's own headers keep their words until Inc-9."""
        if self.outline_mode:
            return darkside.VIEW_NAMES["outline"]
        if self.radial_mode:
            return darkside.VIEW_NAMES["radial"]
        return darkside.VIEW_NAMES["canvas"]

    # -- the docked legend (Inc-8 verdicts `F2`, `F9`, `G2`, `G5`) ----------
    # The legend reads `legend_view_left` and calls the two methods below;
    # nothing else does.  They move the view only through this screen's own
    # pan state and its clamp, never a renderer.

    #: `G5`: the revealed card keeps this many columns clear of the docked
    #: panel's left edge, so it does not sit flush against it.  Declared once
    #: here; `_pan_revealing_selection` is the only reader.
    REVEAL_MARGIN_CELLS = 2

    @property
    def legend_view_left(self) -> int:
        """`F9`: the first column of the view, so the legend docks only while
        the canvas keeps its minimum beside the panel.  The rail is the only
        region left of the canvas (`_chrome_width` counts it the same way)."""
        return 0 if self.rail_hidden else RAIL_WIDTH

    def legend_docked(self, panel_x: int | None) -> None:
        """The legend is docked with its left edge at screen column `panel_x`,
        or is open but not docked (`None`, the modal layout).

        The pan the operator had when the legend opened is kept, and every
        call starts from it: a resize re-derives the reveal instead of
        stacking one on another, and the modal layout gets the kept pan back
        exactly.  Docked, the view pans right just enough for the selected
        card to sit wholly left of the panel -- only when the panel is what
        covers it.  A card already clear of the panel, or already past the
        canvas's right edge before the legend opened, does not move the view.
        The pan stays in `LLR-N06.1.2`'s legal range, so a card at the map's
        own right edge can stay partly covered (`INC8-D3-F2`).

        Both steps go through `_move_pan` (`INC8-P3-CR-F1` fix `a`+`b`),
        which repaints through `_declare_after_layout`'s canvas-only path --
        never the rail or the inspector, so the keyboard's focus is never at
        risk from opening the legend -- and which itself no-ops when nothing
        actually needs repainting.  The reveal is read from the state the
        reset-to-kept-pan step recorded (`_rendered_for`), so this path
        never reads the search resolution outside a paint pass
        (`test_search.py`'s census)."""
        if self._pan_before_legend is None:
            self._pan_before_legend = (self.pan_x, self.pan_y)
            focused = self.focused
            self._focus_before_legend = focused.id if focused is not None else None
        kept_x, kept_y = self._pan_before_legend
        self._move_pan(kept_x, kept_y)
        if panel_x is not None:
            self._move_pan(self._pan_revealing_selection(panel_x), kept_y)

    def legend_closed(self) -> None:
        """The legend closed: the pan and the focus it held return exactly
        (`F2`, `INC8-P3-CR-F1`).

        This runs from `HelpScreen.action_dismiss_none`, BEFORE its own
        `dismiss()` pops this screen back onto the stack -- the pop's
        `ScreenResume` has not even been posted yet, and Textual's own
        `AUTO_FOCUS` answers exactly that message by grabbing the rail
        whenever nothing is focused here (carried `UX-F7`, measured on the
        base tree, no code of this batch's).  Restoring here would just be
        overwritten a moment later, so the restore itself waits for
        `on_screen_resume`, which answers the very same message."""
        if self._pan_before_legend is None:
            return
        self._legend_restore_pending = (*self._pan_before_legend, self._focus_before_legend)
        self._pan_before_legend = None
        self._focus_before_legend = None

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

    def _move_pan(self, pan_x: int, pan_y: int) -> None:
        """Move the pan and repaint through `_declare_after_layout`'s
        canvas-only render path rather than `refresh_canvas`
        (`INC8-P3-CR-F1` fix `a`+`b`).  A legend-driven pan move never
        changes the selected node, the fold or the graph, so the rail and
        the inspector have nothing to re-show; `refresh_canvas`'s own
        rebuild of the inspector (`FichaInspector._rebuild`'s
        `remove_children`) is exactly what threw the keyboard's focus to the
        rail every time this ran, docked or modal.

        Called UNCONDITIONALLY: `_declare_after_layout` already no-ops when
        the `ViewState` it would paint equals `_rendered_for` (`P1`), so a
        call that changes nothing costs one cheap dataclass compare.  A
        hand-rolled `(pan_x, pan_y)` guard here looked equivalent and is NOT:
        a terminal resize can change the CANVAS's geometry while leaving the
        pan NUMBER the same, and that guard then skipped the repaint the new
        geometry needed -- measured RED on
        `test_f2_the_modal_layout_does_not_pan_and_a_resize_re_derives_the_pan`
        (resized narrow then back to the reference width: the reveal came
        back `(0, 0)` instead of the original `(7, 0)`, because the pan
        value alone had not changed even though the frame it was read
        against had)."""
        self.pan_x, self.pan_y = pan_x, pan_y
        self._declare_after_layout()

    def _pan_revealing_selection(self, panel_x: int) -> int:
        """The painted pan, moved right until the selected card's box ends
        `REVEAL_MARGIN_CELLS` short of screen column `panel_x` (`G5`), or
        already does.  Only a renderer that consumes pan moves (`PAN-1`:
        outline and radial do not pan).  Read from the state the canvas was
        last painted from, through the same layout it draws
        (`layered._geometry`, read only), so the card is where the frame
        paints it.

        `A-109` (Inc-8 design pass 4, verdict `G2`): the target is clamped to
        the range legal on the VISIBLE canvas -- the columns left of the
        docked panel -- not the canvas's own full drawn width.  A card whose
        pre-dock pan already sat at the OLD range's maximum (the map's own
        right edge) used to stay partly covered: the old bound assumed the
        whole drawn width was visible, when the panel already covers the
        rightmost `panel_x`-to-`avail` slice of it regardless.  This is the
        one clamp `LLR-N06.1.2` now amends, and only for this call: `_clamp_pan`
        itself, and every other caller of it, is untouched.

        `H3` (closing verdict, round 5) fixes two things in the SAME call:

        `right`'s off-by-one.  A card's box is `geo.card_w` columns wide, but
        the title row's own fit (`views/layered.py`: `title_w = card_w - 3`,
        the glyph `▐ ` two columns ahead of it) never reaches the box's own
        last column when the row carries no change chip -- that column is
        declared width, not painted ink.  Treating it as painted put the
        margin's target one column too far right, so `REVEAL_MARGIN_CELLS`
        painted as 3 blank columns on an ordinary card, not 2.  `right` below
        is ONE COLUMN PAST the last column this call has reason to believe is
        painted -- never "the box's own last painted column" itself, which is
        `right - 1` (`INC8-FU-F4`: an earlier revision of this docstring said
        the second thing and meant the first).

        `INC8-FU-F1` (follow-up, non-blocking at Inc-8's close): a changed
        card paints ONE MORE column than an ordinary one.  `views/layered.py`
        paints the diff chip through the box's own last column
        (`chip_x + len(chip) - 1 == cx + geo.card_w - 1`), the exact column
        the ordinary case never reaches -- and the selection's own highlight
        pass never repaints that one column either way, diff or not, so it is
        the chip's paint that survives there.  Measured before this fix: a
        changed, selected card left only 1 blank column, not the declared 2,
        because `right` subtracted the ordinary case's `- 1` even where the
        chip made that column painted ink.  `chip_painted` below reads the
        SAME predicate `views/layered.py` gates the chip's own paint on
        (`changed.get(nid)` truthy, not merely `nid in changed`, which would
        wrongly count a diff entry whose list happens to be empty).

        The widened range.  At the map's own true right edge the OLD clamp
        left the margin exactly 0 -- read at the time as `LLR-N06.1.2`'s own
        "no blank space past the content" principle.  The operator's answer
        withdrew that reading for this one case (`A-109`'s dated addendum):
        the margin is painted everywhere, edge included, so the legal range
        this call clamps against widens by `REVEAL_MARGIN_CELLS` too -- room
        the docked panel already occupies on screen regardless of where the
        pan sits, exactly `A-109`'s own argument for widening to the visible
        span in the first place, one step further."""
        cursor = self.nav.cursor
        if cursor is None or not self._consumes_pan(self._current_renderer()):
            return self.pan_x
        _renderer, state = self._rendered_for
        pan_x = state.pan_x
        try:
            geo = layered_geometry(self.graph, state)
            (extent_x, _span_x), _y = pan_extent(self.graph, state)
        except Exception:
            # A frame that cannot be laid out cannot be panned (`_pan`).
            return pan_x
        if geo is None or cursor not in geo.pos:
            return pan_x
        canvas_x = self.query_one("#map-canvas", Static).region.x
        card_x, _card_y = geo.place(cursor)
        changed = state.diff.changed if state.diff else {}
        chip_painted = bool(changed.get(cursor))
        right = canvas_x + card_x + geo.card_w - (0 if chip_painted else 1)
        edge = panel_x - self.REVEAL_MARGIN_CELLS
        if card_x >= geo.avail or right <= edge:
            return pan_x
        visible_span = panel_x - canvas_x
        return self._clamp_pan(
            pan_x + right - edge, extent_x + self.REVEAL_MARGIN_CELLS, visible_span
        )

    def _branch_coverage_glyph(self, branch_root: str) -> tuple[str, str]:
        """Return (glyph, style) for a top-level branch's coverage minimap.

        THE `seen` SET IS NOT DEFENSIVE PADDING; without it this walk does not
        terminate.  It had no visited check at all, so on a graph with a cycle
        it re-expanded the same nodes forever -- an unbounded HANG reached from
        `refresh_canvas`, outside every guard, which is worse than the crash the
        sibling guards catch and is the one failure mode this tree's own rule
        singles out.  It also double-counted on a multi-parent DAG, where a node
        reachable by two paths landed in `nodes` twice and skewed the coverage
        percentage this glyph exists to report.
        """
        nodes = [branch_root]
        seen = {branch_root}
        stack = [branch_root]
        while stack:
            parent = stack.pop()
            for cid in self.graph.children_of(parent):
                if cid in seen:
                    continue
                seen.add(cid)
                nodes.append(cid)
                stack.append(cid)
        total = len(nodes)
        con_acta = sum(1 for nid in nodes if self.graph.nodes[nid].ficha.fields.get("D", "").strip())
        if total == 0:
            return ("╱", darkside.WORDMARK)
        pct = con_acta / total
        if pct >= 1.0:
            return ("█", darkside.INK)
        if pct >= 0.5:
            return ("▒", darkside.MUT)
        return ("░", darkside.WARN)

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

    def _minimap_entry_limit(self, width: int, branches: int) -> int:
        """How many branches fit once the affordances have been paid for.

        THE DECLARATION'S CELLS ARE RESERVED ONLY IF THERE WILL BE A
        DECLARATION, and the conditional is the whole point of this method
        rather than a refinement of it.  Reserving unconditionally MANUFACTURES
        the omission it announces: measured on the shipped `legacy` map at
        35x14, an unconditional reserve drew ONE of three branches and declared
        `+2 ramas sin mostrar`, where the plain strip had drawn all three -- and
        the strip's height and the canvas's height were IDENTICAL either way, so
        the two dropped branches bought nothing at all.

        That is this increment's own `height: 3` mistake in a second costume:
        taxing the ordinary map to bound the pathological one.  The order below
        resolves the apparent circularity -- the limit decides whether there is
        a remainder, and the remainder decides the reserve -- by asking the
        cheaper question first: if everything fits WITHOUT a declaration, no
        declaration is needed and none is charged for.
        """
        per_entry = self._MINIMAP_NAME_CELLS + self._MINIMAP_ENTRY_OVERHEAD
        base = self.MINIMAP_ROWS * max(1, width) - self._MINIMAP_CAPTION_CELLS \
            - self._MINIMAP_LEGEND_CELLS
        if max(0, base) // per_entry >= branches:
            return branches
        return max(0, base - self._MINIMAP_DECL_CELLS) // per_entry

    def _minimap_text(self, width: int) -> Text:
        if self.graph.root_id is None:
            return Text("")
        parts: list[tuple[str, str]] = [("  coverage   ", darkside.MUT)]
        children = self.graph.children_of(self.graph.root_id)
        limit = self._minimap_entry_limit(width, len(children))
        for cid in children[:limit]:
            glyph, style = self._branch_coverage_glyph(cid)
            # Both halves are file-derived, and this widget's whole job is
            # telling the operator WHICH branch is at risk -- a `U+202E` here
            # displays one branch's coverage under a neighbour's name, so an
            # uncoerced title deceives the operator on exactly the judgement the
            # minimap exists to support.  `refresh_canvas` repaints it, which is
            # what puts it inside `LLR-N06.2.3`'s "every file-derived string
            # painted on a surface this batch touches".
            #
            # BOUNDED IN CELLS TOO, and `fit` rather than a slice: it coerces
            # (it calls `plain` itself) and it truncates VISIBLY.  A silent
            # row-drop is what the previous revision did, and an operator cannot
            # tell a truncated branch name from a short one.
            name = darkside.fit(self.graph.nodes[cid].ficha.title or cid,
                                self._MINIMAP_NAME_CELLS)
            parts.append((f"{name} ", darkside.MUT))
            parts.append((glyph, style))
            parts.append(("   ", ""))
        undrawn = len(children) - limit
        if undrawn > 0:
            # INK, not MUT, and `#D28` is why: this is a DECLARATION of how much
            # is not on screen -- the same load-bearing role the rule escalates,
            # and the role it names the minimap caption under.  `#map-minimap`
            # inherits `Screen`'s ground today, where `MUT` would clear the
            # floor; `INK` clears on either ground, so the token stays legible
            # if this strip is ever given a `PANEL` background.
            parts.append((f"+{undrawn} branches not shown   ", darkside.INK))
        parts.extend([
            ("█", darkside.INK), (" complete ", darkside.MUT),
            ("▒", darkside.MUT), (" medium ", darkside.MUT),
            ("░", darkside.WARN), (" low ", darkside.MUT),
            ("╱", darkside.WORDMARK), (" no data", darkside.MUT),
        ])
        return darkside.Text.assemble(*parts)

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

    def _open_paint_pass(self) -> None:
        """Drop the frame-scoped search memo; called at the top of every repaint.

        Deliberately a named seam rather than an inline assignment: the memo's
        correctness argument is "it lives for exactly one paint pass", and that
        claim is only checkable if every pass opens the same way.
        """
        self._search_memo = None

    def _view_state(self, w: int, h: int) -> ViewState:
        """The renderer's whole parameter surface, built in ONE place.

        Built once and reused by every call site, which is what closes the
        measured defect that motivated the parameter object: the export site
        passed `query` without `diff`, so an SVG exported during a diff silently
        lost its tinting while the on-screen canvas kept it.  With one
        constructor there is no second argument list to forget.
        """
        return ViewState(
            selected_id=self.nav.cursor,
            w=w,
            h=h,
            focus_owner=self._focus_owner(),
            hits=self._search_hits(),
            diff=self.diff if self.diff_active else None,
            pan_x=self.pan_x,
            pan_y=self.pan_y,
            folded=self.folded,
        )

    def refresh_canvas(self) -> None:
        # US-001, LLR-003.2: the node-change guard, at the ONE re-pointing site
        # every cursor mover ends in, and FIRST -- before the canvas, the crumb,
        # the rail or the inspector repaint -- so `stay` needs no repaint and the
        # inspector is never re-pointed under a draft (A-9).
        self._drop_orphan_draft()
        inspector = self.query_one("#map-inspector", FichaInspector)
        if inspector.has_draft() and self.nav.cursor != inspector.draft_node_id:
            target = self.nav.cursor
            self.nav.cursor = inspector.draft_node_id
            inspector.focus_after_rebuild(None)
            self._guard_draft(lambda: self._repoint(target))
        self._open_paint_pass()
        canvas = self.query_one("#map-canvas", Static)
        renderer = self._current_renderer()
        w, h = self._canvas_size()
        # Any renderer failure is a drawing problem, not an application problem:
        # this method runs inside the message pump, so an escape here kills the
        # app.  Scoped to the sink, not to the exception types known today --
        # which is why `_reclamp_pan` is INSIDE it rather than beside it: it
        # reaches the same `_tree_layout` the render does, and Inc-3 had moved it
        # out where the guard could not see it.
        try:
            self._reclamp_pan(w, h)
            # CAPTURED, not recomputed afterwards: `_reclamp_pan` can move
            # `pan_x`/`pan_y`, so a second `_view_state` call is not necessarily
            # the state this content was produced from -- and recording a state
            # the render did not use is exactly the desync the guard exists to
            # prevent.
            state = self._view_state(w, h)
            text = renderer.render(self.graph, state)
        except Exception as exc:
            state = self._view_state(w, h)
            text = darkside.Text.assemble(
                (" could not draw the map\n\n", f"bold {darkside.INK}"),
                (f" {darkside.plain(str(exc))}", darkside.MUT),
            )
        canvas.update(text)
        # EVERYTHING this content was produced from, recorded so the settle pass
        # can tell "already reconciled" from "needs a re-render" (`P1`).  Set
        # even on the degraded path: the failure text is what the canvas now
        # HOLDS for this state, and re-rendering would only replace a stated
        # degradation with a copy of itself.
        self._rendered_for = (renderer, state)
        pulse_cursor(canvas)

        tab = self.query_one(TabStrip)
        node = self.graph.nodes.get(self.nav.cursor or "")
        node_title = node.ficha.title if node else ""
        # EVERY crumb segment, not just the title: `_current_crumb` also carries
        # `map_id` and the link chain, which are file-derived too.  Found by the
        # frame-level half of `LLR-N06.2.3`'s census rather than by the
        # region-by-region half -- `TabStrip` is queried BY TYPE here, so it has
        # no id for a region sweep to enumerate, and a hostile ficha title was
        # reaching the composited frame through the breadcrumb with the same
        # `U+202E` the minimap leaked.
        tab.set_crumb([
            darkside.plain(part) for part in self._current_crumb() + [node_title]
        ])

        self.query_one("#map-inspector", FichaInspector).show(node, self.graph)
        self.query_one("#map-rail", OutlineRail).show(
            self.graph, self.nav.cursor, self.folded
        )
        # GUARDED LIKE ITS SIBLING, and the asymmetry was the finding: this call
        # sits past the `try` above, `_branch_coverage_glyph` and `_minimap_text`
        # both index `self.graph.nodes[...]` unchecked, and a dangling edge
        # raises `KeyError` from inside the message pump -- which kills the app,
        # exactly the shape the cycle guard was added for.  `_unpainted_ids` has
        # its own try/except; the minimap had none.  A coverage strip that
        # cannot be drawn is a drawing problem, so it degrades to empty.
        #
        # THIS GUARD DOES NOT SAVE THE APP ON A DANGLING EDGE, and the comment
        # above says only that this method stops leaking one.  Measured, the
        # composited paint of the same graph still dies: `OutlineRail.render`
        # indexes `graph.nodes[...]` unchecked too and raises at compositor
        # paint time, one sink over and on a different path.  That sink is
        # CARRIED, not closed -- see the arm in `tests/test_pan.py` that states
        # in terms what it asserts (the exception does not escape this method)
        # and what it does not (that the frame survives).
        strip = self.query_one("#map-minimap", Static)
        # The strip's OWN width, not the screen's: it is docked full-width today
        # but reading the screen would make this budget wrong the moment it is
        # not.  `size.width` is 0 before the first layout, and the fallback is
        # the screen rather than a constant so the pre-layout frame budgets from
        # something real.
        strip_width = strip.size.width or self.size.width
        try:
            minimap = self._minimap_text(strip_width)
        except Exception:
            minimap = darkside.Text("")
        strip.update(minimap)
        # LAST, and the position is load-bearing rather than incidental: the
        # declaration is computed from `painted_ids` over the state that was
        # just rendered, and `_focus_owner` -- which `_view_state` reads -- is
        # only settled once the side regions have been shown.  Moved ahead of
        # them during development and 6 arms went red on focus and on the rail's
        # byte identity.
        self.query_one(f"#{COUNT_REGION_ID}", Static).update(self._pagination_text())
        # ...AND THE LINE ABOVE CAN MOVE THE CANVAS THAT WAS PAINTED ABOVE IT.
        # `P1`, and the mechanism was measured rather than reasoned.  The strip
        # is content-height (`#map-pagination` carries `max-height` and no
        # `height`) while `#map-body` is `1fr`, so the strip's own row count
        # decides how many rows the canvas gets.  In `outline` the declaration is
        # absent, so this line renders 17 cells instead of layered's 36, stops
        # wrapping at terminal widths <= 34, and hands the canvas back a row --
        # AFTER `canvas.update` ran.  Nothing re-rendered, because this method
        # never armed the settle loop.  Measured on `legacy`: the canvas held 3
        # lines where the settled geometry asks for 4 at (30,16) and (32,16), 5
        # where it asks 6 at (24,20), 1 where it asks 2 at (34,14).  The return
        # trip is worse -- layered content written at outline's larger `h` into a
        # region that then SHRINKS overflows by a physical row, CLIPPING content
        # rather than leaving a blank one.
        #
        # `_declare_after_layout` already does the right thing: it re-renders at
        # the CURRENT geometry and chases the region until it stops moving.  It
        # was simply never armed from here.  Clearing `_declared_for` stops its
        # first pass mistaking this frame for one it already reconciled, and it
        # terminates on its own -- it re-schedules only while the region CHANGED,
        # so a settled layout costs exactly one no-op pass.
        self._declared_for = None
        self.call_after_refresh(self._declare_after_layout)
        self._paint_draft_hint()

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

    def action_toggle_outline(self) -> None:
        self.outline_mode = not self.outline_mode
        self.radial_mode = False
        self._clear_pan_hint()
        self.refresh_canvas()

    def action_toggle_radial(self) -> None:
        self.radial_mode = not self.radial_mode
        self.outline_mode = False
        self._clear_pan_hint()
        self.refresh_canvas()

    def action_toggle_diff(self) -> None:
        if self.diff_active:
            self.diff_active = False
            self.refresh_canvas()
            self.notify("diff hidden")
            return
        if self.store is None:
            return
        diff = git_diff(self.map_id, self.store)
        if diff is None:
            self.notify("no diff available (is the map in git?)")
            return
        self.diff = diff
        self.diff_active = True
        self.refresh_canvas()
        added = len(diff.added)
        removed = len(diff.removed)
        changed = len(diff.changed)
        self.notify(darkside.plain(f"diff: +{added} -{removed} ~{changed}"), markup=False)

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
