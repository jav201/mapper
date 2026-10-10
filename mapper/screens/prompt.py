"""The four literal prompt modals for the mapper screens — A2 of batch
`2026-10-09-modular-batch` (LLR-MOD.1.1).

Home of the modals the screens push for a quick answer: `_PromptScreen`
(a single text value), `_ConfirmScreen` (yes/no), `_TemplateScreen` (pick a
map template) and `_FichaScreen` (the selected node's ficha details).  Every
name is re-exported from `mapper.app` so historical `from mapper.app import X`
sites keep resolving (LLR-MOD.3.1); `screens/*` modules import them here
directly — the B-02 remediation (LLR-MOD.6.1): `factory.py`'s function-local
`_PromptScreen` import became a module-level import of this file at A2,
closing the last `screens` -> `app` back-edge.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from rich.markup import escape
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Input, Static

from mapper import darkside
from mapper.store import TEMPLATES

if TYPE_CHECKING:  # `_FichaScreen.__init__` annotates its params as `Node` / `Graph`
    from mapper.model import Graph, Node


class _PromptScreen(ModalScreen[str | None]):
    """Simple darkside modal that returns a single text value."""

    BINDINGS = [("escape", "cancel", "cancel")]

    def __init__(self, title: str, placeholder: str = "") -> None:
        super().__init__()
        self.title = title
        self.placeholder = placeholder

    def compose(self) -> ComposeResult:
        # `S-F2`, and it is `SEC-H2`'s own lesson applied to the instance that
        # fix missed.  `SEC-H2` was fixed AT THE SINK precisely so the CLASS
        # would be closed rather than one call site -- and then only
        # `_ConfirmScreen` got the switch, leaving its structural twin here with
        # the grammar still on.  Every caller passes a literal today (all seven
        # derived, and an independent census over the whole suite confirmed it),
        # so nothing is exploitable; the point is that `self.title` is a `str`
        # PARAMETER, and the next caller to route a node title through it would
        # reopen the defect with every arm green.
        #
        # A class fix applied to one member of the class is an instance fix
        # wearing a class fix's clothes.
        yield Vertical(
            Static(self.title, id="prompt-label", markup=False),
            Input(placeholder=self.placeholder, id="prompt-input"),
            Static("", id="prompt-hints"),
            id="prompt-dialog",
        )

    def on_mount(self) -> None:
        self.query_one("#prompt-input", Input).focus()
        hints = Text.assemble(
            ("↵", darkside.INK),
            (" confirm   ", darkside.MUT),
            ("esc", darkside.INK),
            (" cancel", darkside.MUT),
        )
        self.query_one("#prompt-hints", Static).update(hints)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        self.dismiss(value if value else None)


class _ConfirmScreen(ModalScreen[bool]):
    """Simple yes/no confirmation modal."""

    BINDINGS = [
        ("y", "confirm", "yes"),
        ("n", "dismiss", "no"),
        ("escape", "dismiss", "no"),
        ("q", "dismiss", "no"),
    ]

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        # `SEC-H2`: `markup=False` IS THE SECURITY CONTROL, not a formatting
        # preference.  `Static` renders a `str` through TEXTUAL's markup grammar
        # -- wider than Rich's, and it accepts `[@click=<action>]`, which binds a
        # runnable action to a span.  This message interpolates the node's ficha
        # title, and a sidecar title is untrusted input, so a title can bind
        # `screen.confirm` to the very words being read and archive a subtree on
        # ONE CLICK, with no `y`.  Measured on the unfixed tree: the payload
        # `[@click=screen.confirm]Acta[/]` painted as `¿archivar «Acta»?` -- a
        # sentence IDENTICAL to the benign one.  That is what makes it a security
        # defect rather than a rendering bug: the human-in-the-loop stops being
        # enforced and the human cannot see that it stopped.  `[conceal]` hides
        # the rest of the sentence, and an unclosed tag kills the app out of the
        # compositor's own reflow, where no caller can catch it.
        #
        # FIXED AT THE SINK, DELIBERATELY.  Escaping at the one call site would
        # be the instance fix for a class defect, and the next message built here
        # would inherit the hazard.  A coercion idiom is correct only relative to
        # its SINK -- and `markup=False` is the idiom this module already uses on
        # every `notify`.
        yield Vertical(
            Static(self.message, id="confirm-label", markup=False),
            Static("", id="confirm-hints"),
            id="confirm-dialog",
        )

    def on_mount(self) -> None:
        hints = Text.assemble(
            ("y", darkside.INK),
            (" yes   ", darkside.MUT),
            ("n", darkside.INK),
            (" no", darkside.MUT),
        )
        self.query_one("#confirm-hints", Static).update(hints)

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_dismiss(self) -> None:
        self.dismiss(False)


class _TemplateScreen(ModalScreen[str | None]):
    """Modal that lets the user pick a map template."""

    BINDINGS = [("escape", "dismiss", "close"), ("q", "dismiss", "close")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("choose template", id="template-title"),
            DataTable(id="template-table", cursor_type="row"),
            id="template-dialog",
        )

    def on_mount(self) -> None:
        table = self.query_one("#template-table", DataTable)
        table.clear()
        table.add_columns("▐ template", "description")
        for key, data in TEMPLATES.items():
            desc = data.get("seed_title", key)
            table.add_row(escape(key), escape(desc), key=key)
        if table.row_count == 0:
            table.add_row("(no templates)", "", key="")

    def action_dismiss(self) -> None:
        self.dismiss(None)

    def action_select(self) -> None:
        table = self.query_one("#template-table", DataTable)
        if table.cursor_row is None:
            self.dismiss(None)
            return
        key = table.coordinate_to_cell_key(table.cursor_coordinate)
        value = str(key.value) if key else ""
        self.dismiss(value if value else None)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        value = str(event.row_key.value)
        self.dismiss(value if value else None)


class _FichaScreen(ModalScreen[None]):
    """Modal that shows the selected node's ficha details."""

    BINDINGS = [("escape", "dismiss", "close"), ("q", "dismiss", "close")]

    def __init__(self, node: Node, graph: Graph) -> None:
        super().__init__()
        self.node = node
        self.graph = graph

    def compose(self) -> ComposeResult:
        yield Vertical(Static(id="ficha-content"), id="ficha-dialog")

    def on_mount(self) -> None:
        ficha = self.node.ficha
        text = Text()
        text.append(escape(ficha.title or self.node.id), style=f"bold {darkside.INK}")
        text.append("\n")
        if ficha.meta:
            text.append(escape(ficha.meta), style=darkside.MUT)
            text.append("\n")
        if ficha.state:
            text.append("state ", style=darkside.MUT)
            text.append(escape(ficha.state), style=darkside.INK)
            text.append("\n")

        have, req = ficha.required_coverage(self.graph.schema)
        if req:
            text.append("coverage ", style=darkside.MUT)
            text.append_text(darkside.step_meter(have, req))
            text.append("\n")

        doc = ficha.fields.get("D", "")
        text.append("record ", style=darkside.MUT)
        text.append(escape(doc) if doc else "—",
                    style=darkside.INK if doc else darkside.ALERT)
        text.append("\n")
        text.append("owner ", style=darkside.MUT)
        text.append(escape(ficha.fields.get("O") or "—"), style=darkside.INK)
        text.append("\n")
        text.append("created ", style=darkside.MUT)
        text.append(escape(ficha.fields.get("Y") or "—"), style=darkside.INK)
        text.append("\n")

        linked = self.node.linked_map_id()
        if linked:
            text.append("link ", style=darkside.MUT)
            text.append(escape(linked), style=darkside.ACCENT)
            text.append("  (↵ opens the map)", style=darkside.MUT)
            text.append("\n")

        if ficha.notes:
            text.append("\nnotes\n", style=darkside.MUT)
            text.append(escape(ficha.notes), style=darkside.INK)

        if ficha.fields:
            text.append("\nfields\n", style=darkside.MUT)
            for key, value in ficha.fields.items():
                if key in {"D", "O", "Y", "map"}:
                    continue
                text.append(f"  {escape(key)} ", style=darkside.MUT)
                text.append(escape(value), style=darkside.INK)
                text.append("\n")

        if ficha.attachments:
            text.append("\nattachments\n", style=darkside.MUT)
            for att in ficha.attachments:
                text.append(f"  {escape(att.caption or att.path)}\n", style=darkside.INK)

        self.query_one("#ficha-content", Static).update(text)

    def action_dismiss(self) -> None:
        self.dismiss(None)
