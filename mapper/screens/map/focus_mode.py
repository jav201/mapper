"""MapScreen's `focus` concern as the `FocusModeOps` mixin (focus_mode.py).

Moved verbatim out of `screen.py` at `2026-10-09-modular-batch` Spine B; composed into
`MapScreen`. Never imports `mapper.app` (LLR-MOD.6.2).
"""

from __future__ import annotations

from mapper.screens.map.navigation import NavigationModel


class FocusModeOps:
    """MapScreen's `focus` concern (moved verbatim at 2026-10-09-modular-batch Spine B).

    A plain mixin composed into `MapScreen` (screen.py): it declares no BINDINGS, no
    DEFAULT_CSS and no `@on` handlers (Textual ignores them on a non-DOMNode base), and its
    method names are disjoint from every other concern's (LLR-MOD.2.1, LLR-MOD.2.2).
    """

    def action_toggle_focus(self) -> None:
        if self.focus_active:
            self.graph = self.base_graph
            self.focus_active = False
            self.nav = NavigationModel(self.graph)
            if self.nav.cursor not in self.graph.nodes:
                self.nav.cursor = self.graph.root_id
            self.refresh_canvas()
            return

        if self.nav.cursor is None or self.nav.cursor not in self.graph.nodes:
            return
        self._push_snapshot()
        self.graph = self.base_graph.focus(self.nav.cursor)
        self.focus_active = True
        self.nav = NavigationModel(self.graph)
        self.refresh_canvas()
