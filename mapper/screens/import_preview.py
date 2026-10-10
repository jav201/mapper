"""The CSV-import preview screen — A7 of batch
`2026-10-09-modular-batch` (LLR-MOD.1.1).

Home of `_ImportPreviewScreen`, the screen the home screen pushes after the
operator picks a CSV/TSV path: it renders a live preview of the parsed graph
and, on save, stores it as a named map and pushes `MapScreen` (imported here
from `mapper.screens.map`, never from `mapper.app`; §3).  The name is
re-exported from `mapper.app` so historical `from mapper.app import
_ImportPreviewScreen` sites keep resolving (LLR-MOD.3.1).
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static

from mapper import darkside
from mapper.keymap import SCOPE_IMPORT, groups_for_keybar, hint_pair
from mapper.motion import pulse_cursor
from mapper.screens.common import _save_or_toast, keybar_groups, screen_bindings
from mapper.screens.map import MapScreen
from mapper.screens.prompt import _PromptScreen
from mapper.views.layered import LayeredRenderer
from mapper.views.state import ViewState
from mapper.widgets.chrome import HintLine, KeyBar, TabStrip

if TYPE_CHECKING:
    from mapper.model import Graph
    from mapper.store import MapStore


class _ImportPreviewScreen(Screen):
    """Preview a CSV import before saving it as a named map."""

    KEY_SCOPE = SCOPE_IMPORT
    BINDINGS = screen_bindings(SCOPE_IMPORT)

    def __init__(self, preview_graph: Graph, source_path: Path) -> None:
        super().__init__()
        self.preview_graph = preview_graph
        self.source_path = source_path

    def compose(self) -> ComposeResult:
        yield TabStrip("i", crumb=["import", self.source_path.name])
        yield Static("", id="import-preview-canvas")
        yield HintLine(f"{hint_pair(SCOPE_IMPORT, 'save')} · {hint_pair(SCOPE_IMPORT, 'home')}")
        yield KeyBar(groups_for_keybar(keybar_groups(self.KEY_SCOPE)))

    def on_mount(self) -> None:
        self.refresh_canvas()

    def refresh_canvas(self) -> None:
        canvas = self.query_one("#import-preview-canvas", Static)
        renderer = LayeredRenderer()
        size = self.size or self.app.size
        # Same sink class as MapScreen.refresh_canvas, and a live second door:
        # a CSV whose `parent` column is circular builds a cyclic graph without
        # ever passing through `mermaid.parse`, so the parser's refusal cannot
        # reach it.  Measured — see increment-001 §1.
        try:
            text = renderer.render(
                self.preview_graph,
                ViewState(
                    selected_id=self.preview_graph.root_id,
                    w=max(20, size.width),
                    h=max(5, size.height - 10),
                ),
            )
        except Exception as exc:
            text = darkside.Text.assemble(
                (" could not draw the preview\n\n", f"bold {darkside.INK}"),
                (f" {darkside.plain(str(exc))}", darkside.MUT),
            )
        canvas.update(text)
        pulse_cursor(canvas)

    def action_save(self) -> None:
        def on_name(name: str | None) -> None:
            if not name:
                return
            # `G6-C-F4`: the "guardar como" name is operator-typed and reaches
            # `store.save(name, ...)` as the map id, uncoerced until now.
            name = darkside.plain(name)
            store: MapStore = self.app.store  # type: ignore[attr-defined]
            if not _save_or_toast(self, store, name, self.preview_graph, new=True):
                return
            self.app.push_screen(MapScreen(name))

        self.app.push_screen(
            _PromptScreen("save as", self.source_path.stem),
            callback=on_name,
        )

    def action_home(self) -> None:
        self.app.pop_screen()

    def action_palette(self) -> None:
        self.app.action_palette()
