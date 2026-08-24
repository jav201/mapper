"""Help screen showing the full keymap."""
from __future__ import annotations

from itertools import groupby

from rich.markup import escape
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static

from mapper import darkside
from mapper.keymap import KEYMAP


class HelpScreen(ModalScreen[None]):
    """Modal help overlay with the full grouped keymap."""

    BINDINGS = [
        ("escape", "dismiss", "Cerrar"),
        ("q", "dismiss", "Cerrar"),
    ]

    CSS = """
    HelpScreen {
        align: center middle;
        background: #000000 70%;
    }
    #help-dialog {
        width: 80;
        height: auto;
        max-height: 28;
        background: #121212;
        padding: 1 2;
    }
    #help-title {
        text-style: bold;
        color: #f5f5f5;
        margin-bottom: 1;
    }
    .help-group {
        color: #737373;
        margin-top: 1;
        margin-bottom: 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("atajos", id="help-title"),
            Static(self._render_keymap(), id="help-content"),
            id="help-dialog",
        )

    def _render_keymap(self) -> Text:
        parts: list[tuple[str, str]] = []
        for group, bindings in groupby(
            sorted(KEYMAP, key=lambda b: b.group), key=lambda b: b.group
        ):
            parts.append((f"\n{escape(group)}\n", darkside.MUT))
            for binding in bindings:
                parts.append((f"  {escape(binding.key)}  ", darkside.INK))
                parts.append((f"{escape(binding.action)}\n", darkside.MUT))
        return Text.assemble(*parts)

    def action_dismiss(self) -> None:
        self.dismiss(None)
