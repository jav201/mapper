"""Command palette screen (ctrl+p)."""
from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, ListItem, ListView, Static

from mapper import darkside
from mapper.keymap import (
    SCOPE_APP,
    SCOPE_PALETTE,
    KeyBinding,
    palette_items,
    textual_bindings,
)


class CommandPalette(ModalScreen[str | None]):
    """Fuzzy command palette; dismisses the selected action stem, or None.

    The entries are the bindings reachable from *scope* — the scope of the screen
    that opened the palette — so every row it offers is a key that works right
    here, and selecting one dispatches a real `action_*` method.
    """

    BINDINGS = [
        Binding(key, action, label, priority=priority)
        for key, action, label, priority in textual_bindings(SCOPE_PALETTE)
    ]

    CSS = """
    CommandPalette {
        align: center middle;
        background: #000000 70%;
    }
    #palette-dialog {
        width: 80;
        height: auto;
        max-height: 24;
        background: #121212;
    }
    #palette-input {
        border: none;
        background: #262626;
        color: #f5f5f5;
        padding: 0 1;
    }
    #palette-list {
        width: 100%;
        height: auto;
        max-height: 20;
        border: none;
        background: #121212;
    }
    #palette-list > ListItem {
        height: 1;
        padding: 0 1;
        color: #f5f5f5;
        background: #121212;
    }
    #palette-list > ListItem.--highlight {
        background: #1783ff;
        color: #000000;
    }
    .palette-group { color: #737373; }
    .palette-key { color: #f5f5f5; }
    #palette-list > ListItem.--highlight .palette-key {
        color: #000000;
    }
    #palette-count {
        width: 100%;
        height: 1;
        background: #262626;
    }
    """

    def __init__(self, scope: str = SCOPE_APP) -> None:
        super().__init__()
        self.scope = scope
        self._items: list[KeyBinding] = []

    def compose(self) -> ComposeResult:
        yield Vertical(
            Input(placeholder="/comando", id="palette-input"),
            ListView(id="palette-list"),
            Static("", id="palette-count"),
            id="palette-dialog",
        )

    def on_mount(self) -> None:
        self._refresh_list("")
        self.query_one("#palette-input", Input).focus()

    def _binding_label(self, binding: KeyBinding) -> Text:
        # Every field is placed as its own span with an explicit style: nothing is
        # interpolated into a markup-parsed string.
        return Text.assemble(
            (f"{binding.group:<8}", darkside.WORDMARK),
            (binding.label, darkside.INK),
            ("  ", ""),
            (binding.glyph, darkside.ACCENT),
        )

    def _refresh_list(self, query: str) -> None:
        list_view = self.query_one("#palette-list", ListView)
        list_view.clear()
        # Group by group name to keep related commands together.
        self._items = sorted(palette_items(query, self.scope), key=lambda b: b.group)
        for binding in self._items:
            label = Static(self._binding_label(binding))
            label.add_class("palette-binding")
            list_view.append(ListItem(label))
        if self._items:
            list_view.index = 0
        total = len(palette_items("", self.scope))
        self.query_one("#palette-count", Static).update(
            Text.assemble(
                (f" {len(self._items)}/{total} acciones", darkside.MUT),
                ("   ↵", darkside.ACCENT),
                (" ejecutar   ", darkside.MUT),
                ("esc", darkside.ACCENT),
                (" cerrar", darkside.MUT),
            )
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        self._refresh_list(event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # The search box holds focus, so it consumes `enter` before the screen
        # binding can see it; without this the palette could never be run from the
        # keyboard at all.
        event.stop()
        self.action_run_selected()

    def action_dismiss_none(self) -> None:
        self.dismiss(None)

    def action_run_selected(self) -> None:
        list_view = self.query_one("#palette-list", ListView)
        highlighted = list_view.highlighted_child
        if highlighted is None:
            self.dismiss(None)
            return
        idx = list_view.index
        if 0 <= idx < len(self._items):
            self.dismiss(self._items[idx].action)
        else:
            self.dismiss(None)
