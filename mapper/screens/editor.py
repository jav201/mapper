"""Document source editor screen."""
from __future__ import annotations

import re

from rich.markup import escape
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static, TextArea

from mapper import darkside


_TAG_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")


class EditorScreen(ModalScreen[str | None]):
    """Modal editor for a document template source; returns source or None."""

    BINDINGS = [
        ("ctrl+s", "save", "Guardar"),
        ("escape", "cancel", "Cancelar"),
        ("tab", "toggle_preview", "Prever"),
    ]

    CSS = """
    EditorScreen {
        align: center middle;
        background: #000000 70%;
    }
    #editor-dialog {
        width: 90;
        height: 30;
        background: #121212;
        padding: 1 2;
    }
    #editor-title {
        color: #f5f5f5;
        text-style: bold;
        margin-bottom: 1;
    }
    #editor-textarea {
        width: 100%;
        height: 18;
        border: none;
        background: #262626;
        color: #f5f5f5;
    }
    #editor-preview {
        width: 100%;
        height: 18;
        background: #262626;
        color: #f5f5f5;
        display: none;
    }
    #editor-preview.shown { display: block; }
    #editor-textarea.hidden { display: none; }
    #editor-detected {
        height: auto;
        color: #737373;
        margin-top: 1;
    }
    #editor-hints {
        height: auto;
        color: #737373;
        margin-top: 1;
    }
    .editor-tag { color: #737373; }
    """

    def __init__(self, source: str = "") -> None:
        super().__init__()
        self.source = source

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("editar documento", id="editor-title"),
            TextArea(text=self.source, language="markdown", id="editor-textarea"),
            Static(self._render_preview(self.source), id="editor-preview"),
            Static(self._detected_line(self.source), id="editor-detected"),
            Static("ctrl+s salvar  ·  esc cancelar  ·  tab prever", id="editor-hints"),
            id="editor-dialog",
        )

    def on_mount(self) -> None:
        self.query_one("#editor-textarea", TextArea).focus()

    def _detected_tags(self, source: str) -> list[str]:
        return sorted(set(_TAG_RE.findall(source)))

    def _detected_line(self, source: str) -> Text:
        tags = self._detected_tags(source)
        parts: list[tuple[str, str]] = [("detectados: ", darkside.MUT)]
        for i, tag in enumerate(tags):
            if i > 0:
                parts.append((", ", darkside.MUT))
            parts.append((escape(tag), darkside.INK))
        if not tags:
            parts.append(("ninguno", darkside.MUT))
        return Text.assemble(*parts)

    def _render_preview(self, source: str) -> Text:
        parts: list[tuple[str, str]] = []
        pos = 0
        for match in _TAG_RE.finditer(source):
            start, end = match.span()
            if start > pos:
                parts.append((escape(source[pos:start]), darkside.INK))
            parts.append((escape(match.group(0)), darkside.MUT))
            pos = end
        if pos < len(source):
            parts.append((escape(source[pos:]), darkside.INK))
        return Text.assemble(*parts)

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        source = event.text_area.text
        self.query_one("#editor-preview", Static).update(self._render_preview(source))
        self.query_one("#editor-detected", Static).update(self._detected_line(source))

    def action_save(self) -> None:
        self.dismiss(self.query_one("#editor-textarea", TextArea).text)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_toggle_preview(self) -> None:
        preview = self.query_one("#editor-preview", Static)
        textarea = self.query_one("#editor-textarea", TextArea)
        if preview.has_class("shown"):
            preview.remove_class("shown")
            textarea.remove_class("hidden")
            textarea.focus()
        else:
            preview.add_class("shown")
            textarea.add_class("hidden")
            preview.update(self._render_preview(textarea.text))
