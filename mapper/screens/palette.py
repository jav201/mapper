"""Command palette screen (ctrl+p)."""
from __future__ import annotations

from itertools import groupby

from rich.markup import escape
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, ListItem, ListView, Static

from mapper import darkside
from mapper.keymap import KEYMAP, KeyBinding, palette_items


class CommandPalette(ModalScreen[str | None]):
    """Fuzzy command palette; dismisses the selected action or None."""

    BINDINGS = [
        ("escape", "dismiss_none", "Close"),
        ("enter", "run_selected", "Run"),
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
        color: #1783ff;
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
    .palette-key { color: #1783ff; }
    #palette-list > ListItem.--highlight .palette-key {
        color: #000000;
    }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            Input(placeholder="/comando", id="palette-input"),
            ListView(id="palette-list"),
            id="palette-dialog",
        )

    def on_mount(self) -> None:
        self._refresh_list("")
        self.query_one("#palette-input", Input).focus()

    def _binding_label(self, binding: KeyBinding) -> Text:
        return Text.assemble(
            (f"{escape(binding.group)}  ", darkside.MUT),
            (escape(binding.key), darkside.ACCENT),
            ("  ", ""),
            (escape(binding.action), darkside.INK),
        )

    def _refresh_list(self, query: str) -> None:
        list_view = self.query_one("#palette-list", ListView)
        list_view.clear()
        items = palette_items(query)
        # Group by group name to keep related commands together.
        self._items = sorted(items, key=lambda b: b.group)
        for binding in self._items:
            label = Static(self._binding_label(binding))
            label.add_class("palette-binding")
            list_view.append(ListItem(label))
        if self._items:
            list_view.index = 0

    def on_input_changed(self, event: Input.Changed) -> None:
        self._refresh_list(event.value)

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
