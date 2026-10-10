"""MapScreen's `export` concern as the `ExportingOps` mixin (exporting.py).

Moved verbatim out of `screen.py` at `2026-10-09-modular-batch` Spine B; composed into
`MapScreen`. Never imports `mapper.app` (LLR-MOD.6.2).
"""

from __future__ import annotations

import asyncio
from dataclasses import replace
from mapper import darkside
from mapper.export import ExportError, ExportTooLarge, save_svg
from mapper.views.layered import pan_extent
from mapper.views.state import export_neutralised, ViewState


class ExportingOps:
    """MapScreen's `export` concern (moved verbatim at 2026-10-09-modular-batch Spine B).

    A plain mixin composed into `MapScreen` (screen.py): it declares no BINDINGS, no
    DEFAULT_CSS and no `@on` handlers (Textual ignores them on a non-DOMNode base), and its
    method names are disjoint from every other concern's (LLR-MOD.2.1, LLR-MOD.2.2).
    """

    async def action_export_svg(self) -> None:
        if self.store is None:
            return
        try:
            size = self.size or self.app.size
            renderer = self._current_renderer()
            # THE BUDGET IS CHECKED FIRST, so a refusal never announces a wait
            # it is not going to take.
            state = self._export_view_state(size)
            cells = max(0, state.w) * max(0, state.h)
            if cells >= self.EXPORT_DECLARE_CELLS:
                # A FREEZE NOBODY WAS TOLD ABOUT IS THIS BATCH'S OWN DEFECT
                # CLASS APPLIED TO TIME INSTEAD OF CONTENT -- hidden without
                # being declared.  The export is bounded and useful now, but
                # bounded is not instant: the worst shape the budget admits
                # still costs seconds on a short terminal, and a TUI that stops
                # answering with no indication reads as hung rather than busy.
                self.notify(
                    darkside.plain(f"exporting {cells} cells; this may take a moment."),
                    markup=False,
                )
                await asyncio.sleep(self.EXPORT_DECLARE_PAUSE)
            text = renderer.render(self.graph, state)
            path = self.store.workspace / f"{self.map_id}.svg"
            save_svg(text, path)
            self._event_toast("exported", path.name)
        except ExportTooLarge as too_large:
            # A REFUSAL, AND IT NAMES THE ROUTE FORWARD.  Nothing is written --
            # see `_export_view_state` for why a partial artifact is the one
            # outcome this path may not produce.  The message carries the
            # measured extent, the budget, and the chord that makes the map
            # small enough, because a refusal the operator cannot act on is a
            # capability regression rather than a safeguard.
            #
            # AND IT DECLARES THE STALE FILE, because refusing to write leaves
            # whatever the LAST export wrote sitting at the very path the
            # success toast names.  The operator is told the export refused;
            # without this they are not told that the file still there is OLD --
            # and a stale artifact at the expected path is this batch's own
            # defect family (`B-68`: a file that looks current and is not),
            # reintroduced one seam over by the increment that closed it.
            #
            # DECLARED RATHER THAN DELETED, and that is the correct answer
            # rather than the cautious one.  The standard is that nothing is
            # hidden without being DECLARED -- not that nothing stale exists --
            # so an old file the operator has been told about is declared.  And
            # deleting their file on their behalf, on a refusal, with no
            # confirmation is the destructive act `US-N05` already ruled
            # against: silently deleting would break a standing ruling in order
            # to soften a lesser one.
            #
            # THE SENTENCE IS CONDITIONAL BECAUSE IT MUST NEVER BE FALSE -- AND
            # ITS FIRST FORM WAS FALSE ANYWAY.  It read "... es de una
            # exportación anterior y ya no refleja este mapa", guarded by
            # `path.exists()`.  But EXISTENCE IS NOT STALENESS, and the guard and
            # the sentence were therefore two different claims.  Measured: export
            # a map, change NOTHING about the graph, then make the same map
            # exceed the budget -- the artifact on disk is still a faithful
            # export of that exact graph, and the refusal called it stale.
            #
            # So it now says only what `exists()` licenses: nothing was written,
            # a file is there, and an earlier export wrote it.  Whether that file
            # still matches the map is something this code does not know and must
            # not assert.  Telling the operator a CURRENT file is stale is the
            # same category of error as letting them believe a STALE file is
            # current -- both are the artifact misdescribing itself, which is the
            # family `B-68` names.
            # `CR17-F4`, and it is this fix's OWN principle turned on it. The
            # sentence was justified as saying "only what `exists()` licenses"
            # -- and then said an EXPORT wrote the file, which `exists()` does
            # not license: a directory, or a file the operator dropped there,
            # would have been called a previous export. `is_file()` licenses
            # "el archivo"; nothing licenses a claim about its author, so no
            # claim about its author is made. What the operator actually needs
            # is that NOTHING WAS WRITTEN and what is there is not this export,
            # and both of those are true whoever put it there.
            # `E2` (operator, 2026-10-02) then asked the sentence to say where the file comes from, so it now does:
            # that claim is the operator's ruling, not something `is_file()` licenses.
            path = self.store.workspace / f"{self.map_id}.svg"
            stale = ""
            if path.is_file():
                stale = (
                    f" Nothing was written; {path.name} on disk is from an earlier export."
                )
            self.notify(
                darkside.plain(f"map too large to export: {too_large.cells} cells, "
                f"limit {too_large.limit}. Focus a subtree with f and export that view."
                f"{stale}"),
                severity="warning",
                markup=False,
            )
        except Exception as e:
            self.notify(darkside.plain(f"export failed: {type(e).__name__}"), severity="error", markup=False)

    def _export_view_state(self, size) -> ViewState:
        """The state an export renders from: the canvas state, minus the session.

        THE SAME STATE THE CANVAS DRAWS FROM, EXCEPT WHAT IS TRANSIENT.  Sharing
        the state is what closes the measured defect that decided the renderer
        contract: this site passed `query` and omitted `diff`, so an SVG
        exported during a diff silently lost its tinting.  One constructor
        leaves no second argument list to under-fill.

        AN EXPORT IS A STANDALONE ARTIFACT, so it must not encode where the
        session happened to be.  That was ruled once, for the focus owner:
        "which screen region owns the keyboard" is meaningless inside a file,
        and measured on a plain operator sequence -- `tab` (or `g`, which
        focuses the rail), then `e` -- passing the live owner through painted
        the selected node in the INACTIVE tone.  An export always renders as
        though the canvas were focused.

        `B-68` IS THAT SAME RULING, APPLIED TO THE OTHER HALF OF THE SAME
        EXPRESSION.  The pan offsets are transient view state sitting in the
        very `_view_state(...)` call the `focus_owner` `replace()` wrapped, and
        they rode through untouched: the export sized itself from the TERMINAL
        while `_geometry` shrinks `card_w` at that wider width until the tree
        fits, collapsing `max_pan_x` to 0 -- so an offset perfectly legal on the
        canvas was out of range for the export and shifted content off the
        artifact's left edge.  Measured on the pan fixture: 47,263 bytes at
        pan (0,0) against 16,718 at the reachable pan (49,10) -- roughly 65% of
        the map missing from a file the operator hands to someone else, and
        the file looks complete to both of them.  Reachable with no view
        change: pan to the edge, press `e`.

        SO THE FIX REMOVES THE STATE RATHER THAN BOUNDING IT.  Clamping the pan
        to the export's own geometry would stop the content loss and still
        encode a scroll position in a standalone artifact, which is the thing
        the ruling forbids.  The recipient wants the MAP, not where the
        operator happened to be looking.  An "export what I am looking at" mode,
        if it is ever wanted, is a separate deliberate feature whose crop is
        DECLARED IN THE ARTIFACT.

        THE TRANSIENT SET IS DERIVED, NOT LISTED HERE.  `focus_owner`, then the
        pan offsets, then `selected_id` and `hits` were each noticed one at a
        time -- which is a ruling about a CLASS being discharged as a handful of
        instances, leaving the next field for the next reviewer to find.  The
        classification now lives beside the dataclass as
        `views.state.EXPORT_FIELD_KINDS`, and `export_neutralised` resets every
        field marked `transient` to its own declared default.  A field added to
        `ViewState` without a row there fails an arm instead of inheriting
        whichever behaviour its neighbour happened to have.

        AND THE EXTENT IS BOUNDED, BECAUSE "ALWAYS FULL EXTENT" DID NOT SURVIVE
        MEASUREMENT.  Export cost follows the map's BOUNDING-BOX AREA -- the
        canvas walks a dense `w x h` grid -- so a wide AND deep map priced at
        ~125 minutes and ~16 GB inside the product's own node cap, paid on the
        message pump.  It also fails on utility before it fails on cost: a
        72001x24004 SVG is not an artifact any recipient can read.

        SO THIS REFUSES, AND A REFUSAL IS NOT A CROP.  The defect `B-68` names
        is a file that LOOKS COMPLETE AND IS NOT.  Producing nothing and saying
        why preserves that principle exactly; producing a truncated,
        best-effort or silently-shrunk artifact reinstates it.  There is no
        partial-artifact path out of this method, and the exhaustion case below
        refuses for the same reason rather than shipping whatever it had
        reached.

        A VIEW THAT DOES NOT CONSUME PAN DECLINES THE RESIZE, matching
        `_reclamp_pan` one seam over: outline and radial hold no viewport, so
        growing a canvas to "fit the extent" would be applying a layered
        helper renderer-independently -- the defect `PAN-1` closed.  Their
        offsets are still zeroed, because zero is what they already behave as.

        HONEST BOUNDARY: "full extent" here is GEOMETRIC.  It guarantees every
        node's CARD is inside the artifact, not that every node's TITLE is
        printed whole -- `layered._geometry` clamps `card_w` down as the tree
        widens, so at 300 leaves a 40-character title still renders in about
        nine columns. That clamping is identical to the canvas's and is not
        changed here; it is stated so "the recipient wants the MAP" is not read
        as "nothing is ever elided".
        """
        state = export_neutralised(
            self._view_state(max(20, size.width), max(5, size.height - 10))
        )
        if not self._consumes_pan(self._current_renderer()):
            return self._within_export_budget(state)
        for _ in range(self.EXPORT_EXTENT_STEPS):
            try:
                (extent_x, span_x), (extent_y, span_y) = pan_extent(self.graph, state)
            except Exception:
                # Same argument as `refresh_canvas`'s guard and `_pan`'s: a
                # graph that is not a tree raises out of `_tree_layout` by
                # design, and an export is not worth killing the app over.  The
                # render two lines up raises on the same graph into the same
                # handler, so this returns the terminal-sized request rather
                # than inventing a second failure mode for it.
                return self._within_export_budget(state)
            if extent_x <= span_x and extent_y <= span_y:
                return self._within_export_budget(state)
            state = replace(
                state,
                w=state.w + max(0, extent_x - span_x) + 2,
                h=state.h + max(0, extent_y - span_y) + 1,
            )
        # EXHAUSTED WITHOUT FITTING.  Measured, this does not happen -- the
        # extent settles in one step on every shape probed, and an independent
        # pass reproduced it at two.  But returning `state` here would toast
        # "exportado" over an artifact that is cropped for a reason nobody
        # recorded, which is `B-68` with no pan to blame.  Refuse instead.
        #
        # AND IT REFUSES WITH ITS OWN REASON, not with `ExportTooLarge`.  This
        # branch is reached by a state that did not CONVERGE, which is not the
        # same event as a state that was too big -- an exhausted extent can sit
        # under the budget, and `ExportTooLarge` would then hand the operator a
        # number that contradicts its own sentence and advice (`f`) that cannot
        # help.  A message must not name a culprit its condition cannot
        # identify, so this one names what actually happened.
        raise ExportError(
            f"the export extent did not settle in {self.EXPORT_EXTENT_STEPS} steps "
            f"(reached {state.w}x{state.h}); a cropped artifact is the defect this "
            "refuses, so nothing is written"
        )

    def _within_export_budget(self, state: ViewState) -> ViewState:
        """Return `state`, or refuse if rendering it would exceed the budget."""
        cells = max(0, state.w) * max(0, state.h)
        if cells > self.EXPORT_MAX_CELLS:
            raise ExportTooLarge(cells, self.EXPORT_MAX_CELLS)
        return state
