"""The new-map name modal for the mapper screens — A3 of batch
`2026-10-09-modular-batch` (LLR-MOD.1.1).

Home of `ConstructScreen`, the modal the home screen pushes to ask for a
new map name.  The name is re-exported from `mapper.app` so historical
`from mapper.app import ConstructScreen` sites keep resolving
(LLR-MOD.3.1); `screens/*` modules import it here directly (the B-02
remediation, LLR-MOD.6.1: no `screens` -> `app` back-edge).
"""
from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Static

from mapper import darkside
from mapper.screens.common import _refusal_toast
from mapper.store import MapStoreError


class ConstructScreen(ModalScreen[str | None]):
    """Ask for a new map name and return it."""

    BINDINGS = [("escape", "cancel", "cancel")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("new map", id="construct-label"),
            Input(placeholder="my-new-map", id="construct-input"),
            Static("", id="construct-hints"),
            id="construct-dialog",
        )

    def on_mount(self) -> None:
        self.query_one("#construct-input", Input).focus()
        hints = Text.assemble(
            ("↵", darkside.INK),
            (" create   ", darkside.MUT),
            ("esc", darkside.INK),
            (" cancel", darkside.MUT),
        )
        self.query_one("#construct-hints", Static).update(hints)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        name = event.value.strip().replace(" ", "-")
        if not name:
            return
        # `A-113`: refuse here too, so the dialog stays open and the name can be
        # fixed; the store refuses again by itself (it is the boundary).
        try:
            self.app.store.check_new_map_id(name)  # type: ignore[attr-defined]
        except MapStoreError as e:
            if _refusal_toast(self, e):
                return
            raise
        self.dismiss(name)
