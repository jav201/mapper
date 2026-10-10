"""MapScreen's `pan` concern as the `PanningOps` mixin (panning.py).

Moved verbatim out of `screen.py` at `2026-10-09-modular-batch` Spine B; composed into
`MapScreen`. Never imports `mapper.app` (LLR-MOD.6.2).
"""

from __future__ import annotations

from mapper.screens.common import PAN_EDGE_HINT, PAN_INERT_HINT
from mapper.views.layered import _geometry as layered_geometry, pan_extent
from mapper.widgets.chrome import HintLine
from textual.widgets import Static


class PanningOps:
    """MapScreen's `pan` concern (moved verbatim at 2026-10-09-modular-batch Spine B).

    A plain mixin composed into `MapScreen` (screen.py): it declares no BINDINGS, no
    DEFAULT_CSS and no `@on` handlers (Textual ignores them on a non-DOMNode base), and its
    method names are disjoint from every other concern's (LLR-MOD.2.1, LLR-MOD.2.2).
    """

    @staticmethod
    def _clamp_pan(offset: int, extent: int, span: int) -> int:
        """LLR-N06.1.2 — the legal range is `[0, max(0, E - W)]`, always.

        The `E < W` case is why the outer `max(0, ...)` is there rather than a
        bare `extent - span`: a map smaller than the canvas has a legal pan
        range of exactly one position, and a negative upper bound would let
        `min` return it and slide the map off screen on a small graph.
        """
        return max(0, min(offset, max(0, extent - span)))

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
