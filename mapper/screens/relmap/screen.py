"""`RelMapScreen` — the relation screen host (batch `2026-10-25-relmap-r2-batch`,
trunk Inc-2).

The host owns what every view shares: the seat-derived chrome (TabStrip crumb,
KeyBar — LLR-RVH.4.2/.4.3), the one view canvas, the derive-on-open + `r`
re-derivation through the D3 API (LLR-RVH.3.2, R-019 recompute-on-open), the
host-owned selection the cursor keys move, and the closed-set refusal path
(LLR-RVH.5.1).  The three renderers land in lanes 3/4/5 against the frozen
surface in `base.py`; until then `base.PendingView` paints the honest minimum.

Read-only by contract: no draft, no save, no `store` write, no `osopen`
launch — the derivation reads the truth files through `relmap`'s readers
alone, resolved at the workspace root (workspace-as-repo, LLR-RVH.3.3); the
canon is never required to live in a git repository.

This module never imports `mapper.app` (LLR-MOD.6.2 — the cycle ban); the
workspace arrives as a constructor argument, the way Home will route it in
Inc-6.
"""
from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.dom import NoActiveAppError
from textual.screen import Screen
from textual.widgets import Static

from mapper import darkside
from mapper.keymap import SCOPE_RELMAP, groups_for_keybar
from mapper.relmap.adapter import CanonUnavailable, derive_reqharness_map
from mapper.relmap.descriptor import (
    Descriptor,
    DescriptorError,
    default_descriptor,
    load_descriptor,
)
from mapper.relmap.gaps import detect_gaps, rank_gaps
from mapper.relmap.model import RelMap, RelMapLimitError
from mapper.relmap.text import refusal_line
from mapper.screens.common import keybar_groups, screen_bindings
from mapper.screens.relmap import base
from mapper.widgets.chrome import KeyBar, TabStrip

#: The view-specific chords and their home views (LLR-RVH.4.1, COND-UX-1):
#: `enter` focuses the matrix lens, `c` chains the sheet, `k` groups the gaps.
_TOGGLE_HOME = {"enter": "matrix", "c": "sheet", "k": "gaps"}
#: The views whose row axis IS the node list (their LLRs make rows nodes):
#: their cursor moves the host-owned node selection (`focus`).  The gaps
#: view's row axis is the ranked-gap catalogue (D1, amended) — its cursor
#: highlights a gap row and leaves `focus` untouched.
_NODE_AXIS_VIEWS = ("matrix", "sheet")
#: The fixed cause for a derivation refused by the shipped node/edge caps.
#: Worded here, in the chrome, because the presentation leaf's refusal wording
#: is RVT-owned and this cause names no K-row: it is a derivation failure,
#: not a read refusal.
_DERIVE_LIMIT_CAUSE = "map exceeds the derived-size limit"


class RelMapScreen(Screen):
    """A derived relation map hosted across the three ported views."""

    KEY_SCOPE = SCOPE_RELMAP
    BINDINGS = screen_bindings(SCOPE_RELMAP)
    # The relation screen binds printable keys screen-wide; a focused widget
    # must not eat them (the MapScreen pattern).
    AUTO_FOCUS = None

    def __init__(
        self,
        name: str,
        workspace: Path | str,
        descriptor: Descriptor | None = None,
        descriptor_path: Path | None = None,
    ) -> None:
        if descriptor is not None and descriptor_path is not None:
            raise ValueError("pass descriptor or descriptor_path, not both")
        super().__init__()
        #: The crumb's first part — the descriptor base name or the derived
        #: entry's name.  File-derived: every read routes through the seam.
        self.source_name = name
        self.workspace = Path(workspace)
        self.descriptor = descriptor
        self.descriptor_path = descriptor_path
        self.active_view = "matrix"
        self.relmap: RelMap | None = None
        self.notice: str | None = None
        self.focus: str | None = None
        # ONE CURSOR PER VIEW (D1, amended): each view's cursor moves within
        # [0, row_count) of THAT view's own row axis, clamped at the ends,
        # never wrapping; the active view's cursor is the one passed in
        # ViewState.cursor.
        self._cursors = {name: 0 for name in base.VIEW_NAMES}
        self.gaps: tuple = ()
        # The renderer state word PER VIEW (COND-ARCH-1): the crumb shows
        # the ACTIVE view's own word — switching views never shows another
        # view's word, and switching back restores it.
        self._view_state_words = {name: "" for name in base.VIEW_NAMES}
        self._views = {n: base.build_view(n) for n in base.VIEW_NAMES}

    # -- lifecycle -----------------------------------------------------------

    def compose(self) -> ComposeResult:
        yield TabStrip(None, crumb=self._crumb_parts(), id="relmap-crumb")
        yield Static("", id="relmap-notice")
        yield Static("", id="relmap-canvas")
        # The keybar reads the same seat the bindings are generated from, so it
        # cannot advertise a key the screen does not bind (LLR-RVH.4.2).
        yield KeyBar(groups_for_keybar(keybar_groups(self.KEY_SCOPE)), id="relmap-keybar")

    def on_mount(self) -> None:
        self._derive()

    def _derive(self) -> None:
        """Derive the map from the descriptor and canon (LLR-RVH.3.2/.3.3).

        The one derivation door.  A refused descriptor or an unavailable canon
        yields the fixed refusal line as the notice and NO map — the closed
        cause set, never ``str(exc)``, a path or a YAML snippet (LLR-RVH.5.1),
        and the screen stays alive for `q`/`escape` (M-RVH-14).
        """
        try:
            descriptor = self._load_descriptor()
            derivation = derive_reqharness_map(self.workspace, descriptor)
        except DescriptorError as exc:
            self._set_unavailable(refusal_line(exc.name, exc.cause, exc.limit))
            return
        except CanonUnavailable as exc:
            self._set_unavailable(
                refusal_line(self.source_name, exc.cause, exc.limit)
            )
            return
        except RelMapLimitError:
            self._set_unavailable(
                refusal_line(self.source_name, _DERIVE_LIMIT_CAUSE)
            )
            return
        self.relmap = derivation.map
        self.notice = None
        self.gaps = self._rank_gaps()
        self.focus = self.relmap.nodes[0].id if self.relmap.nodes else None
        self._cursors = {name: 0 for name in base.VIEW_NAMES}
        self._repaint()

    def _load_descriptor(self) -> Descriptor:
        """The descriptor this screen derives from — the host loads a descriptor
        FILE itself so its refusal surfaces here (LLR-RVH.5.1); a handed
        descriptor (the derived entry, LLR-RVH.3.1) is used as given."""
        if self.descriptor_path is not None:
            return load_descriptor(self.descriptor_path, self.workspace)
        if self.descriptor is not None:
            return self.descriptor
        return default_descriptor()

    def _rank_gaps(self) -> tuple:
        """The host-supplied gap rows every renderer receives (D1) — ranked
        once here so no renderer re-ranks (LLR-RVG.1.1)."""
        if self.relmap is None:
            return ()
        ranked, _overflow = rank_gaps(self.relmap, detect_gaps(self.relmap), None)
        return tuple(ranked)

    def _set_unavailable(self, notice: str) -> None:
        self.relmap = None
        self.gaps = ()
        self.focus = None
        self._cursors = {name: 0 for name in base.VIEW_NAMES}
        self.notice = notice
        self._repaint()

    # -- chrome --------------------------------------------------------------

    def _crumb_parts(self) -> list[str]:
        """`reqharness / relmap / matrix` (+ the renderer's state word, when
        the active renderer owns one — COND-ARCH-1).  Every part is
        file-derived, so every part is plained before the strip's own
        `fit`/`_row_text` coercion runs (the MapScreen idiom)."""
        tail = self.active_view
        word = self._view_state_words[self.active_view]
        if word:
            tail = f"{tail} · {word}"
        return [
            darkside.plain(self.source_name),
            "relmap",
            tail,
        ]

    def _paint_crumb(self) -> None:
        self.query_one("#relmap-crumb", TabStrip).set_crumb(self._crumb_parts())

    def _paint_notice(self) -> None:
        self.query_one("#relmap-notice", Static).update(
            base.label(self.notice, self._width()) if self.notice else ""
        )

    def _width(self) -> int:
        try:
            return self.app.size.width or darkside.DECLARED_CONTEXT_CELLS
        except NoActiveAppError:
            return darkside.DECLARED_CONTEXT_CELLS

    def _view_state(self, width: int, height: int) -> base.ViewState:
        return base.ViewState(
            relmap=self.relmap,
            notice=self.notice,
            focus=self.focus,
            cursor=self._cursors[self.active_view],
            gaps=self.gaps,
            width=width,
            height=height,
        )

    def _viewport(self) -> tuple[int, int]:
        canvas = self.query_one("#relmap-canvas", Static)
        return (canvas.size.width or self._width(), canvas.size.height or 1)

    def _repaint(self) -> None:
        """The one repaint: notice, crumb, and the active view's canvas over
        the frozen surface."""
        self._paint_crumb()
        self._paint_notice()
        canvas = self.query_one("#relmap-canvas", Static)
        width, height = self._viewport()
        view = self._views[self.active_view]
        canvas.update(base.frame(view.paint(self._view_state(width, height))))

    # -- actions (the seat's `action` stems — LLR-RVH.4.1) -------------------

    def action_matrix(self) -> None:
        self._switch("matrix")

    def action_gaps(self) -> None:
        self._switch("gaps")

    def action_sheet(self) -> None:
        self._switch("sheet")

    def _switch(self, view: str) -> None:
        if view == self.active_view:
            return
        self.active_view = view
        self._repaint()

    def action_refresh(self) -> None:
        """`r` — re-derive from the SAME descriptor and canon (LLR-RVH.3.2)."""
        self._derive()

    def action_leave(self) -> None:
        """`q`, and `escape` as the quiet-leave alias.  Read-only: no guard
        has anything to ask about."""
        self.app.pop_screen()

    def action_move_up(self) -> None:
        self._move_selection(-1)

    def action_move_down(self) -> None:
        self._move_selection(1)

    def action_move_left(self) -> None:
        self._move_selection(-1)

    def action_move_right(self) -> None:
        self._move_selection(1)

    def _move_selection(self, step: int) -> None:
        """Move the ACTIVE view's cursor within [0, row_count) — clamped at
        the ends, NO wrap (holding `down` stops at the last row).  The view's
        OWN row_count defines the axis (D1, amended): the node list for
        matrix/sheet, the ranked-gap rows for gaps.  On a node-axis view the
        node selection (`focus`) follows the cursor; the gaps cursor is not
        the node axis and leaves `focus` untouched."""
        if self.relmap is None:
            return
        view = self._views[self.active_view]
        width, height = self._viewport()
        count = view.row_count(self._view_state(width, height))
        if count <= 0:
            return
        cursor = min(max(self._cursors[self.active_view] + step, 0), count - 1)
        self._cursors[self.active_view] = cursor
        if self.active_view in _NODE_AXIS_VIEWS and self.relmap.nodes:
            self.focus = self.relmap.nodes[cursor].id
        self._repaint()

    def action_lens(self) -> None:
        self._toggle("enter")

    def action_chain(self) -> None:
        self._toggle("c")

    def action_by_kind(self) -> None:
        self._toggle("k")

    def _toggle(self, kind: str) -> None:
        """The one toggle mechanism (COND-ARCH-1) — and the out-of-view inert
        rule (COND-UX-1, M-RVH-19): off the chord's home view this is a no-op,
        byte for byte; on it, the ACTIVE renderer's `toggle` flips its state
        and returns the state word for the crumb slot."""
        if _TOGGLE_HOME[kind] != self.active_view:
            return
        word = self._views[self.active_view].toggle(kind)
        self._view_state_words[self.active_view] = word
        self._repaint()
