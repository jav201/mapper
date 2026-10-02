"""Settings canary screen for the darkside component sheet."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Static

from mapper import darkside
from mapper.keymap import SCOPE_SETTINGS, groups_for_keybar, textual_bindings
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


class _Grid(VerticalScroll, can_focus=False):
    """The sheet's rows, scrolling (`INC9-UX-F3`): nine rows of four lines outgrow a
    34-row terminal.  The container is not itself a tab stop -- the components are."""


class _StateRow(Static):
    """One component rendered in default / focused / disabled columns."""

    def __init__(self, label: str, widget_factory, **kwargs) -> None:
        super().__init__(**kwargs)
        self.label = label
        self.default = widget_factory()
        self.focused = widget_factory()
        # `A-112` st. 8: NOT `self.disabled` -- that is Textual's own
        # `Widget.disabled`, and a widget object there is truthy, which
        # disabled this row and every component in it: the sheet had no focus
        # chain at all, so `tab` could never move focus.
        self.inert = widget_factory()
        self.inert.disabled = True

    def compose(self) -> ComposeResult:
        yield Static(self.label, classes="settings-label")
        yield self.default
        yield self.focused
        yield self.inert


class SettingsScreen(Screen):
    """Canary screen: every darkside component in its three states."""

    # LLR-N16.1.2 / `#D9`: generated from the seat.  `tab`/`shift+tab` are
    # Textual's own traversal (`C-D9a`); `palette` and `help` dispatch to the
    # App, which opens both on THIS scope (B-18).
    KEY_SCOPE = SCOPE_SETTINGS
    # `K2`: the screen is `components` on every surface -- this is the legend's title.
    legend_view = "components"
    BINDINGS = [
        Binding(key, action, label, priority=priority)
        for key, action, label, priority in textual_bindings(SCOPE_SETTINGS)
    ]

    CSS = """
    SettingsScreen { layout: vertical; background: #000000; }
    #settings-grid { height: 1fr; }
    .settings-label { width: 14; color: #737373; }
    """

    def compose(self) -> ComposeResult:
        # `K2`: no tab is active here -- the sheet is none of the four doors.
        yield TabStrip(None, crumb=["components"])
        yield Static("component         default          focused          disabled",
                     id="settings-header")
        with _Grid(id="settings-grid"):
            yield _StateRow("switch", lambda: DsSwitch(True))
            yield _StateRow("stepper", lambda: DsStepper(3, min_value=0, max_value=9))
            yield _StateRow("slider", lambda: DsSlider(0.55))
            yield _StateRow("segmented", lambda: DsSegmented(["moon", "tide", "night"], 0))
            yield _StateRow("progress", lambda: DsProgress(3, 5))
            yield _StateRow("spinner", lambda: DsSpinner(0, "loading…"))
            yield _StateRow("text field", lambda: DsTextField("system-leg"))
            yield _StateRow("pagination", lambda: DsPagination(2, 5))
            yield _StateRow("tag chip", lambda: DsChip(label="legacy"))
        yield HintLine("tab walks the components — focus is the solid block", "tab")
        from mapper.app import keybar_groups

        yield KeyBar(groups_for_keybar(keybar_groups(self.KEY_SCOPE)))

    def on_mount(self) -> None:
        # Each row used to focus its own `focused` cell on mount, so the LAST row
        # won -- the tag chip, below the fold.  Focus starts on the first.
        self.call_after_refresh(lambda: self.query(_StateRow).first().focused.focus())

    def action_home(self) -> None:
        self.app.pop_screen()
