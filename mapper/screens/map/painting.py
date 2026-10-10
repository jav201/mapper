"""MapScreen's `views` concern as the `PaintingOps` mixin (painting.py).

Moved verbatim out of `screen.py` at `2026-10-09-modular-batch` Spine B; composed into
`MapScreen`. Never imports `mapper.app` (LLR-MOD.6.2).
"""

from __future__ import annotations

from mapper import darkside
from mapper.diff import git_diff
from mapper.motion import pulse_cursor
from mapper.screens.common import COUNT_REGION_ID
from mapper.views.layered import header_rows, painted_ids
from mapper.views.outline import (
    header_rows as outline_header_rows,
    painted_ids as outline_painted_ids,
)
from mapper.views.radial import header_rows as radial_header_rows, painted_ids as radial_painted_ids
from mapper.views.state import ViewState
from mapper.widgets.chrome import TabStrip
from mapper.widgets.inspector import FichaInspector
from mapper.widgets.rail import OutlineRail, RAIL_WIDTH
from rich.text import Text
from textual.widgets import Static


class PaintingOps:
    """MapScreen's `views` concern (moved verbatim at 2026-10-09-modular-batch Spine B).

    A plain mixin composed into `MapScreen` (screen.py): it declares no BINDINGS, no
    DEFAULT_CSS and no `@on` handlers (Textual ignores them on a non-DOMNode base), and its
    method names are disjoint from every other concern's (LLR-MOD.2.1, LLR-MOD.2.2).
    """

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
