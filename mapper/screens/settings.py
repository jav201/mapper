"""Settings canary screen for the darkside component sheet."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from mapper import darkside
from mapper.widgets.chrome import HintLine, KeyBar, TabStrip
from mapper.widgets.components import (
    DsChip,
    DsPagination,
    DsProgress,
    DsSegmented,
    DsSlider,
    DsSpinner,
    DsStepper,
    DsSwitch,
    DsTextField,
)


class _StateRow(Static):
    """One component rendered in default / focused / disabled columns."""

    def __init__(self, label: str, widget_factory, **kwargs) -> None:
        super().__init__(**kwargs)
        self.label = label
        self.default = widget_factory()
        self.focused = widget_factory()
        self.disabled = widget_factory()
        self.disabled.disabled = True

    def compose(self) -> ComposeResult:
        yield Static(self.label, classes="settings-label")
        yield self.default
        yield self.focused
        yield self.disabled

    def on_mount(self) -> None:
        self.focused.focus()


class SettingsScreen(Screen):
    """Canary screen: every darkside component in its three states."""

    BINDINGS = [
        Binding("q", "home", "Salir", priority=True),
        Binding("escape", "home", "Salir", priority=True),
        Binding("tab", "focus_next", "Siguiente", priority=True),
        Binding("shift+tab", "focus_previous", "Anterior", priority=True),
        Binding("ctrl+p", "palette", "Paleta", priority=True),
        Binding("?", "help", "Ayuda", priority=True),
    ]

    CSS = """
    SettingsScreen { layout: vertical; background: #000000; }
    #settings-grid { height: 1fr; }
    .settings-label { width: 14; color: #737373; }
    """

    def compose(self) -> ComposeResult:
        yield TabStrip("c", crumb=["preferencias"])
        yield Static("componente        default          focused          disabled",
                     id="settings-header")
        with Vertical(id="settings-grid"):
            yield _StateRow("switch", lambda: DsSwitch(True))
            yield _StateRow("stepper", lambda: DsStepper(3, min_value=0, max_value=9))
            yield _StateRow("slider", lambda: DsSlider(0.55))
            yield _StateRow("segmented", lambda: DsSegmented(["luna", "marea", "noche"], 0))
            yield _StateRow("progress", lambda: DsProgress(3, 5))
            yield _StateRow("spinner", lambda: DsSpinner(0, "cargando…"))
            yield _StateRow("text field", lambda: DsTextField("sistema-leg"))
            yield _StateRow("pagination", lambda: DsPagination(2, 5))
            yield _StateRow("tag chip", lambda: DsChip(label="legacy"))
        yield HintLine("tab recorre componentes — el foco es el bloque sólido", "tab")
        yield KeyBar(
            [
                ("nav", [("tab", "siguiente"), ("shift+tab", "anterior")]),
                ("app", [("ctrl+p", "paleta"), ("?", "ayuda"), ("q/esc", "salir")]),
            ]
        )

    def action_home(self) -> None:
        self.app.pop_screen()

    def action_palette(self) -> None:
        self.app.action_palette()

    def action_help(self) -> None:
        from mapper.screens.help import HelpScreen

        self.app.push_screen(HelpScreen())
