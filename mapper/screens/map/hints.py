"""MapScreen's `hints` concern as the `HintsOps` mixin (hints.py).

Moved verbatim out of `screen.py` at `2026-10-09-modular-batch` Spine B; composed into
`MapScreen`. Never imports `mapper.app` (LLR-MOD.6.2).
"""

from __future__ import annotations

from mapper import darkside
from mapper.keymap import bindings_for, KeyBinding
from mapper.screens.common import (
    _HINT_BRANCH_CELLS,
    _HINT_BRANCHES,
    _HINT_NAME_MIN_CELLS,
    _HINT_NAME_OVERHEAD,
    map_hint,
    PAN_EDGE_HINT,
    PAN_INERT_HINT,
    SEARCH_SUSPENDED_NOTICE,
)
from mapper.widgets.chrome import HintLine
from textual.widgets import Static


class HintsOps:
    """MapScreen's `hints` concern (moved verbatim at 2026-10-09-modular-batch Spine B).

    A plain mixin composed into `MapScreen` (screen.py): it declares no BINDINGS, no
    DEFAULT_CSS and no `@on` handlers (Textual ignores them on a non-DOMNode base), and its
    method names are disjoint from every other concern's (LLR-MOD.2.1, LLR-MOD.2.2).
    """

    def _event_toast(self, label: str, detail: str = "") -> None:
        """Bottom strip for events only — status words, not glyphs.

        THE DETAIL IS BOUNDED AT THIS SEAM, which is the only place all eleven
        call sites pass through.  Several of them hand it a file-derived node
        title, `#map-toast` carries no height rule, and the strip took its rows
        from `#map-body` -- so a 4000-character detail rendered 36 rows at 118x34
        and left the canvas ONE.  Same class as the crumb above it, with a
        smaller blast radius: it needs an operator action and it clears on the
        next toast, which is why it is degradation rather than a persistent
        collapse.

        `darkside.fit` COERCES AS WELL AS TRUNCATES -- it calls `plain` itself --
        so bounding here also closes a coercion gap the security review found at
        the export sink, which passed `str(path)` raw.  One seam, both defects,
        every call site.
        """
        toast = self.query_one("#map-toast", Static)
        if detail:
            room = max(
                self._TOAST_CHROME_CELLS,
                self.size.width - len(label) - self._TOAST_CHROME_CELLS,
            )
            detail = darkside.fit(detail, min(room, len(detail))).rstrip()
            text = darkside.Text.assemble(
                (f" {label}", f"bold {darkside.INK}"),
                (f"   {detail}", darkside.MUT),
            )
        else:
            text = darkside.Text.assemble((f" {label}", f"bold {darkside.INK}"))
        toast.styles.background = darkside.PANEL
        toast.update(text)

    # -- US-N07 · the walk over the live matches (`#D5b`, `HLR-N07.3`) ------
    def _seat_row(self, action: str) -> KeyBinding | None:
        """The seat's row for *action* in this screen's scope, at CALL time.

        Never captured at import.  Everything the surfaces below paint about a
        chord -- the glyph in the hint line, the glyph and the label in the
        rebind declaration -- is read through here, so a later rebind reaches
        the painted string without a second edit.  This increment is itself the
        proof that the hazard is real: `n` meant `next_gap` one commit ago.
        """
        for binding in bindings_for(self.KEY_SCOPE):
            if binding.action == action:
                return binding
        return None

    def _seat_glyph(self, action: str) -> str:
        row = self._seat_row(action)
        return row.glyph if row else ""

    def _seat_label(self, action: str) -> str:
        row = self._seat_row(action)
        return row.label if row else ""

    def _field_hint(self) -> str:
        """The hint while an inspector field holds the keyboard (U2).

        Typing drafts the field and `j` types a letter, so the map-navigation
        hint would lie; this names the save key from the seat instead
        (LLR-005.2)."""
        save = self._seat_glyph("save_draft")
        return f"type to draft · {save} {self._seat_label('save_draft')} · esc leave field"

    def _search_hint(self, hits: tuple[str, ...] | None) -> str:
        """`UX-Q3-b`'s hint for a live search, glyphs READ FROM THE SEAT.

        Takes the resolved order as an ARGUMENT rather than resolving again, so
        the hint cannot describe a different answer from the one its caller
        acted on -- the same "one resolution per frame" rule `_search_order`'s
        memo exists to enforce, applied one surface up.
        """
        clear = f"{self._seat_glyph('back_or_home')} clear"
        if hits is None:
            # Above the renderer's bound.  `sin coincidencias` here would be the
            # lying affordance one surface over from the one `_count_line`
            # refuses to paint -- it declares an empty answer over a graph that
            # may hold thousands of matches.  The state comes first and the
            # affordance last, which is the shape the empty-state hint below
            # already uses, and `esc` is promised because `esc` now works here.
            return f"{SEARCH_SUSPENDED_NOTICE} · {clear}"
        if not hits:
            return f"no matches · {clear}"
        return (
            f"{self._seat_glyph('next_hit')} next · "
            f"{self._seat_glyph('prev_hit')} previous · {clear}"
        )

    def _declare_rebind(self) -> None:
        """Say ONCE that `n` changed hands (`AT-051b`).

        Every string comes from the SEAT.  A typed copy would go on announcing a
        rebind that a later increment moved again, which is the failure the
        declaration exists to prevent, reproduced inside the declaration.
        Between this increment and Inc-8 the relocated `next_gap` is
        undiscoverable through `?` -- its `view` group sits below the legend's
        fold at the declared size -- so this toast is the only painted route to
        its new home.
        """
        self._event_toast(
            f"{self._seat_glyph('next_hit')} · {self._seat_label('next_hit')}",
            f"{self._seat_label('next_gap')} now on {self._seat_glyph('next_gap')}",
        )

    def _walk_toast(self, declaring: bool, label: str, detail: str) -> None:
        """One toast slot, and the one-time declaration outranks it on press 1.

        `E1b` and `E1c` are painted on every later press; on the very first they
        would hide the fact that the KEY changed meaning, which is the more
        urgent of the two things to say and the only one that is ever said.
        """
        if declaring:
            self._declare_rebind()
            return
        self._event_toast(label, detail)

    def _hint_with_opened(self, hint: str, opened: list[str], width: int) -> str:
        """Append `abrió «…»` to *hint*, BOUNDED, and BEHIND the affordances.

        Branch titles are file-derived: unbounded in length, and one walk can
        open several nested folds at once.  `HintLine` WRAPS rather than clips,
        so an unbounded segment does not overflow the strip -- it grows the
        strip and takes the rows from the canvas.  Measured at the declared
        118x34 with a ~2000-character title and one real `n`: the strip went to
        18 rows, the map to ONE, and `n siguiente · N anterior · esc limpiar`
        left the painted frame -- including `esc limpiar`, the affordance `#D38`
        newly promises.  So the increment that introduced the recovery route
        also introduced the way to lose it.

        TWO INDEPENDENT GUARDS, because either alone is insufficient.  Order:
        the names go AFTER the affordances, so a wrap that still happened could
        only push the ANNOUNCEMENT off, never the keys.  Budget: the name gets
        the row's remainder, capped, so no wrap happens at all -- a FIXED cap
        was tried first and measured wrapping at 80 columns, where the whole
        strip then left the frame.  With no room to say anything the
        announcement is dropped: the operator can see the branch opened, and
        losing `esc` is the worse of the two failures.
        """
        if not opened:
            return hint
        names = ", ".join(self._branch_name(nid) for nid in opened[:_HINT_BRANCHES])
        if len(opened) > _HINT_BRANCHES:
            names += f" +{len(opened) - _HINT_BRANCHES}"
        room = min(_HINT_BRANCH_CELLS, width - len(hint) - _HINT_NAME_OVERHEAD)
        if room < _HINT_NAME_MIN_CELLS:
            return hint
        # `fit` truncates to display CELLS and re-coerces; its padding is
        # stripped because this sits inside quotes, not in a column.
        return f"{hint} · opened «{darkside.fit(names, room).rstrip()}»"

    def _clear_pan_hint(self) -> None:
        """Drop `PAN_INERT_HINT` when the view changes underneath it.

        THE HINT IS A STATEMENT ABOUT THE VIEW, so it stops being true the
        moment the view changes -- and `_pan`'s own clear is reachable only on a
        SUCCESSFUL pan, which a non-panning view never performs.  Without this
        the hint LATCHES: press a pan key in radial, press `r` back to layered,
        and the strip still reads "esta vista no se desplaza" while standing in
        the view that does scroll.  Not merely stale -- FALSE in the view
        displaying it.

        This is the defect `_pan` already records one branch down ("the hint is
        set on a no-op and nothing ever unset it ... it latched on the first
        sideways press and then sat there describing every LIVE `J`/`K` as an
        edge the operator had not reached"), reintroduced on a new surface by
        the branch added to fix `PAN-1`.  Cleared HERE, at the seam where the
        property stops holding, rather than on the next successful pan.

        Scoped to the pan hint alone: an unconditional clear would swallow
        whatever another handler had just declared.

        READS `HintLine.text`, THE STORED VALUE, rather than rendering the
        widget to inspect it.  A zero-arg `render()` here would be a WIDGET-
        protocol call in PRODUCTION code -- correctly outside the `A3`, but the
        census pins that population and a new production site changes it; the
        first version of this method did exactly that and the `A3` pins caught
        it.  The stored value is also the honest source: it is what `set_hint`
        wrote, with no styling or wrapping in between.
        """
        hint = self.query_one(HintLine)
        if hint.text in (PAN_INERT_HINT, PAN_EDGE_HINT):
            hint.set_hint(self._resting_hint())

    def _resting_hint(self) -> str:
        """What the hint line says when no handler has declared anything: the live search's hint while a
        query is live, else the map's.  `_pan` and `_clear_pan_hint` restore THIS, never a blank
        (`PR-QA-F3`: a blank hint after a pan is a map that stopped saying what the keys are)."""
        if self._search_is_live():
            return self._search_hint(self._search_order())
        return map_hint()
