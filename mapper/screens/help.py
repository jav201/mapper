"""Help screen showing the keymap that actually works on the active screen."""
from __future__ import annotations

from itertools import groupby

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static

from mapper import darkside
from mapper.keymap import SCOPE_APP, SCOPE_HELP, bindings_for, textual_bindings


class HelpScreen(ModalScreen[None]):
    """Modal help overlay listing the bindings reachable from one scope.

    Help is scoped, not global: showing a key that does nothing here is the
    discoverability bug this batch exists to remove (US-N03).
    """

    # Its own scope.  Borrowing the palette's meant binding `enter -> run_selected`,
    # a method this screen does not define, which was a silent no-op.
    BINDINGS = [
        Binding(key, action, label, priority=priority)
        for key, action, label, priority in textual_bindings(SCOPE_HELP)
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

    def __init__(self, scope: str = SCOPE_APP) -> None:
        super().__init__()
        self.scope = scope

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(f"atajos · {self.scope}", id="help-title"),
            Static(self._render_keymap(), id="help-content"),
            id="help-dialog",
        )

    def _render_keymap(self) -> Text:
        parts: list[tuple[str, str]] = []
        entries = bindings_for(self.scope)
        for group, bindings in groupby(
            sorted(entries, key=lambda b: b.group), key=lambda b: b.group
        ):
            parts.append((f"\n{group}\n", darkside.MUT))
            for binding in bindings:
                parts.append((f"  {binding.glyph:<8}", darkside.INK))
                parts.append((f"{binding.label}\n", darkside.MUT))
        return Text.assemble(*parts)

    def action_dismiss_none(self) -> None:
        self.dismiss(None)
