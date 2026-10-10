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
    from mapper.model import CsvCollision, Graph
    from mapper.store import MapStore


def _collision_sentence(collision: CsvCollision) -> str:
    """The exact HLR-CSV.2 sentence for one colliding slug (LLR-CSV.2.2)."""
    rows = [
        (row.line_no, darkside.plain(row.raw_id)) for row in collision.rows
    ]
    if len(rows) == 2:
        listing = (
            f"rows {rows[0][0]} (id '{rows[0][1]}') "
            f"and {rows[1][0]} (id '{rows[1][1]}')"
        )
    else:
        nums = ", ".join(str(n) for n, _ in rows[:-1]) + f" and {rows[-1][0]}"
        ids = ", ".join(f"'{raw}'" for _, raw in rows[:-1])
        ids += f" and '{rows[-1][1]}'"
        listing = f"rows {nums} (ids {ids})"
    return (
        f"CSV {listing} collapse into the node id "
        f"'{darkside.plain(collision.slug)}'; a map can hold only one parent "
        "per node, so rename the duplicated ids and import again."
    )


def _refusal_sentences(graph: Graph) -> list[str]:
    """The refusal sentence(s) for a preview graph, by the precedence
    collision > multi-parent > cycle (rulings R1/R3); empty when the graph
    violates no invariant and records no collision (clean or empty CSV)."""
    if graph.csv_collisions:
        return [_collision_sentence(c) for c in graph.csv_collisions]
    dupes = graph.multi_parent_ids()
    if dupes:
        names = ", ".join(f"'{darkside.plain(d)}'" for d in dupes)
        return [
            f"the import gives the node {names} more than one parent; "
            "a map can hold only one parent per node, so fix the parent "
            "references and import again."
        ]
    cycle = graph.find_cycle()
    if cycle:
        path = " → ".join(darkside.plain(cid) for cid in cycle)
        return [
            f"the import builds a cycle ({path}); a saved map must be a "
            "tree, so fix the parent references and import again."
        ]
    return []


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
        sentences = _refusal_sentences(self.preview_graph)
        if sentences:
            # HLR-CSV.2 / LLR-CSV.2.2: the existing refusal panel — header
            # kept verbatim, the pinned sentence(s) in its body.  Every
            # interpolated piece passed `darkside.plain` at assembly (C8).
            body = " " + "\n ".join(sentences)
            text = darkside.Text.assemble(
                (" could not draw the preview\n\n", f"bold {darkside.INK}"),
                (body, darkside.MUT),
            )
            canvas.update(text)
            pulse_cursor(canvas)
            return
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
        # LLR-CSV.2.3 (ruling R15): refuse AT the `s` keypress, BEFORE the
        # "save as" prompt is pushed — no name is asked for a save that cannot
        # happen.  A non-empty collision record refuses even when the graph
        # violates no loader rule (ruling R1).  This is an authored toast at
        # the call site (`_save_or_toast` can only toast a store raise), so
        # the pinned text names the cause the store toast cannot carry.
        if self.preview_graph.csv_collisions:
            self.notify(
                "the CSV has colliding ids — nothing was saved; see the preview",
                severity="error",
                markup=False,
            )
            return

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
