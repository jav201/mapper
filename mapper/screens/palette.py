"""Command palette screen (ctrl+p)."""
from __future__ import annotations

from rich.cells import cell_len
from rich.text import Text
from textual import events
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
    bar_group_order,
    group_header,
    hint_pair,
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
    #palette-list > ListItem.-highlight {
        background: #1783ff;
        color: #000000;
    }
    .palette-group { color: #737373; }
    .palette-key { color: #f5f5f5; }
    #palette-list > ListItem.-highlight .palette-key {
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
        self._head_cells = 0
        self._label_cells = 0
        self._labels: list[Static] = []

    def compose(self) -> ComposeResult:
        yield Vertical(
            Input(placeholder="/command", id="palette-input"),
            ListView(id="palette-list"),
            Static("", id="palette-count"),
            id="palette-dialog",
        )

    async def on_mount(self) -> None:
        await self._refresh_list("")
        self.query_one("#palette-input", Input).focus()

    def _binding_label(self, binding: KeyBinding, selected: bool = False) -> Text:
        # Every field is placed as its own span with an explicit style: nothing is
        # interpolated into a markup-parsed string.
        # The HEADER word the key bar paints, never the seat's group id (`INC9C-F2`).
        head = group_header(binding.group)
        # Both columns are padded to the seat's widest word, so the label column
        # and the key column each start at one cell on every row.
        # `INC9F-UX-F1`: a span's colour beats the `-highlight` CSS, and the row's
        # background IS the accent, so the selected row is painted in one ground-on-
        # accent colour (5.7:1) instead of the unselected row's three.
        head_style, label_style, key_style = (
            (darkside.GROUND,) * 3 if selected
            else (darkside.WORDMARK, darkside.INK, darkside.ACCENT)
        )
        return Text.assemble(
            (head + " " * (self._head_cells - cell_len(head)) + "  ", head_style),
            (binding.label + " " * (self._label_cells - cell_len(binding.label)) + "  ", label_style),
            (binding.glyph, key_style),
        )

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        lit = self.query_one("#palette-list", ListView).index
        for i, (label, binding) in enumerate(zip(self._labels, self._items)):
            label.update(self._binding_label(binding, selected=(i == lit)))

    async def _refresh_list(self, query: str) -> None:
        list_view = self.query_one("#palette-list", ListView)
        # `INC9G-CR-F1`: `clear()` removes the rows on a later turn.  Unawaited, `index = 0`
        # below lit a node that was being removed and the new first row never got
        # `-highlight`: `↵` ran a row painted GROUND on the plain ground (1.12:1).
        await list_view.clear()
        self._labels = []
        # Grouped in the key bar's order, so the palette and the bar read alike.
        order = {g: i for i, g in enumerate(bar_group_order(self.scope))}
        self._head_cells = max(cell_len(group_header(g)) for g in order)
        self._label_cells = max(cell_len(b.label) for b in palette_items("", self.scope))
        self._items = sorted(palette_items(query, self.scope), key=lambda b: order[b.group])
        for binding in self._items:
            label = Static(self._binding_label(binding))
            label.add_class("palette-binding")
            self._labels.append(label)
            list_view.append(ListItem(label))
        if self._items:
            list_view.index = 0
        total = len(palette_items("", self.scope))
        # The footer's key words are the seat's own palette rows (`K3`).
        up_key, move_word = hint_pair(SCOPE_PALETTE, "move_up").split(" ", 1)
        down_key = hint_pair(SCOPE_PALETTE, "move_down").split(" ", 1)[0]
        run_key, run_word = hint_pair(SCOPE_PALETTE, "run_selected").split(" ", 1)
        close_key, close_word = hint_pair(SCOPE_PALETTE, "dismiss_none").split(" ", 1)
        self.query_one("#palette-count", Static).update(
            Text.assemble(
                (f" {len(self._items)}/{total} actions", darkside.MUT),
                ("   " + up_key + down_key, darkside.ACCENT),
                (f" {move_word}   ", darkside.MUT),
                (run_key, darkside.ACCENT),
                (f" {run_word}   ", darkside.MUT),
                (close_key, darkside.ACCENT),
                (f" {close_word}", darkside.MUT),
            )
        )

    def on_key(self, event: events.Key) -> None:
        # The search box holds focus, so the list never sees the page keys: forward
        # them, and leave the box focused so typing keeps filtering.  The arrows are
        # seat rows (`move_up` / `move_down`): the box binds neither, so they reach
        # the screen's `BINDINGS` and need no forwarding here.
        if event.key not in ("pageup", "pagedown"):
            return
        event.stop()
        event.prevent_default()
        list_view = self.query_one("#palette-list", ListView)
        step = max(1, list_view.size.height - 1)
        self._move(-step if event.key == "pageup" else step)

    def _move(self, delta: int) -> None:
        list_view = self.query_one("#palette-list", ListView)
        if not self._items:
            return
        target = (list_view.index or 0) + delta
        list_view.index = max(0, min(len(self._items) - 1, target))

    def action_move_up(self) -> None:
        self._move(-1)

    def action_move_down(self) -> None:
        self._move(1)

    async def on_input_changed(self, event: Input.Changed) -> None:
        await self._refresh_list(event.value)

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
