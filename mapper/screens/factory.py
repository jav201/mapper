"""Document factory screen for process-template editing."""
from __future__ import annotations

import re

from rich.markup import escape
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from mapper import darkside
from mapper.model import Document, Graph, Node
from mapper.widgets.chrome import TabStrip


_TAG_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")


class _Nav:
    """Minimal tree cursor helper for the factory screen."""

    def __init__(self, graph: Graph):
        self.graph = graph
        self.cursor = graph.root_id

    def children(self, nid: str | None = None) -> list[str]:
        nid = nid or self.cursor
        return self.graph.children_of(nid) if nid else []

    def parent(self) -> str | None:
        return self.graph.parent_of(self.cursor) if self.cursor else None

    def next_sibling(self) -> str | None:
        p = self.parent()
        if p is None:
            return None
        sibs = self.children(p)
        if self.cursor not in sibs:
            return None
        idx = sibs.index(self.cursor)
        return sibs[idx + 1] if idx + 1 < len(sibs) else None

    def prev_sibling(self) -> str | None:
        p = self.parent()
        if p is None:
            return None
        sibs = self.children(p)
        if self.cursor not in sibs:
            return None
        idx = sibs.index(self.cursor)
        return sibs[idx - 1] if idx > 0 else None

    def first_child(self) -> str | None:
        ch = self.children()
        return ch[0] if ch else None


class FactoryScreen(Screen):
    """Factory mode: resolve documents against a process tree."""

    BINDINGS = [
        ("j", "next_sibling", "Next"),
        ("k", "prev_sibling", "Prev"),
        ("h", "parent", "Parent"),
        ("l", "child", "Child"),
        ("d", "edit_doc", "Edit doc"),
        ("q", "home", "Home"),
        ("ctrl+p", "palette", "Palette"),
        ("?", "help", "Help"),
    ]

    CSS = """
    FactoryScreen { layout: vertical; background: #000000; }
    #factory-header { height: auto; }
    #factory-body { height: 1fr; }
    #factory-tree {
        width: 40%;
        height: 100%;
        background: #121212;
    }
    #factory-preview {
        width: 60%;
        height: 100%;
        background: #121212;
    }
    #factory-steps {
        height: auto;
        color: #737373;
        padding: 0 1;
    }
    .factory-node { color: #f5f5f5; }
    .factory-node-selected {
        background: #1783ff;
        color: #000000;
    }
    .factory-tag { color: #1783ff; }
    .factory-missing { color: #ff4f42; }
    """

    def __init__(
        self,
        graph: Graph,
        process_name: str = "proceso",
        node_id: str | None = None,
        document_name: str | None = None,
    ) -> None:
        super().__init__()
        self.graph = graph
        self.process_name = process_name
        self.nav = _Nav(graph)
        if node_id is not None and node_id in graph.nodes:
            self.nav.cursor = node_id
        self.document_name = document_name or (
            graph.document_names()[0] if graph.document_names() else ""
        )

    def compose(self) -> ComposeResult:
        yield TabStrip("f")
        yield Static(id="factory-steps")
        with Horizontal(id="factory-body"):
            yield Static(id="factory-tree")
            yield Static(id="factory-preview")

    def on_mount(self) -> None:
        self._refresh()

    def _step_meter(self) -> Text:
        total = max(1, self._max_depth() + 1)
        filled = self._depth(self.nav.cursor or "")
        return darkside.step_meter(filled, total)

    def _depth(self, nid: str) -> int:
        depth = 0
        current = nid
        while True:
            parent = self.graph.parent_of(current)
            if parent is None:
                return depth
            depth += 1
            current = parent

    def _max_depth(self) -> int:
        return max((self._depth(nid) for nid in self.graph.nodes), default=0)

    def _tree_lines(self) -> Text:
        lines: list[tuple[str, str]] = []
        block = f"bold {darkside.GROUND} on {darkside.ACCENT}"

        def walk(nid: str, depth: int) -> None:
            node = self.graph.nodes[nid]
            prefix = "  " * depth + "▸ "
            selected = nid == self.nav.cursor
            title = escape(node.ficha.title or nid)
            lines.append((f"{prefix}{title}\n", block if selected else darkside.INK))
            for cid in self.graph.children_of(nid):
                walk(cid, depth + 1)

        if self.graph.root_id is not None:
            walk(self.graph.root_id, 0)
        return Text.assemble(*lines)

    def _preview(self) -> Text:
        node = self.graph.nodes.get(self.nav.cursor or "")
        if node is None or not self.document_name:
            return Text.assemble(("sin documento", darkside.MUT))
        doc = self.graph.resolve_document(self.document_name, node)
        parts: list[tuple[str, str]] = []
        pos = 0
        for match in _TAG_RE.finditer(doc.source):
            start, end = match.span()
            if start > pos:
                parts.append((escape(doc.source[pos:start]), darkside.INK))
            key = match.group(1).strip()
            value = doc.tags.get(key)
            if value:
                parts.append((escape(value), darkside.INK))
            else:
                parts.append((escape(f"{{{{{key}}}}}"), darkside.ALERT))
            pos = end
        if pos < len(doc.source):
            parts.append((escape(doc.source[pos:]), darkside.INK))
        return Text.assemble(*parts) if parts else Text.assemble(("(vacío)", darkside.MUT))

    def _tags_table(self) -> Text:
        node = self.graph.nodes.get(self.nav.cursor or "")
        if node is None or not self.document_name:
            return Text.assemble(("", ""))
        doc = self.graph.resolve_document(self.document_name, node)
        parts: list[tuple[str, str]] = []
        for key in sorted(set(doc.tags) | set(_TAG_RE.findall(doc.source))):
            local = doc.tags.get(key, "")
            inherited = doc.inherited.get(key, "")
            parts.append((f"{{{{{escape(key)}}}}}  ", darkside.ACCENT))
            parts.append((f"{escape(local) or '-'}  ", darkside.INK))
            parts.append((f"{escape(inherited) or '-'}\n", darkside.MUT))
        return Text.assemble(*parts)

    def _refresh(self) -> None:
        tab = self.query_one(TabStrip)
        node = self.graph.nodes.get(self.nav.cursor or "")
        node_name = escape(node.ficha.title or self.nav.cursor or "") if node else ""
        tab.set_crumb([self.process_name, node_name])
        self.query_one("#factory-steps", Static).update(self._step_meter())
        self.query_one("#factory-tree", Static).update(self._tree_lines())
        preview = self.query_one("#factory-preview", Static)
        preview.update(Text.assemble(
            (self.document_name or "documento", f"bold {darkside.INK}"), "\n\n",
            self._preview(), "\n\n",
            ("tags", f"bold {darkside.MUT}"), "\n",
            self._tags_table(),
        ))

    def action_next_sibling(self) -> None:
        nxt = self.nav.next_sibling()
        if nxt:
            self.nav.cursor = nxt
            self._refresh()

    def action_prev_sibling(self) -> None:
        prv = self.nav.prev_sibling()
        if prv:
            self.nav.cursor = prv
            self._refresh()

    def action_parent(self) -> None:
        p = self.nav.parent()
        if p:
            self.nav.cursor = p
            self._refresh()

    def action_child(self) -> None:
        ch = self.nav.first_child()
        if ch:
            self.nav.cursor = ch
            self._refresh()

    def action_edit_doc(self) -> None:
        from mapper.screens.editor import EditorScreen

        node = self.graph.nodes.get(self.nav.cursor or "")
        if node is None or not self.document_name:
            return
        doc = self.graph.resolve_document(self.document_name, node)

        def on_save(source: str | None) -> None:
            if source is None:
                return
            if self.document_name in self.graph.documents:
                self.graph.documents[self.document_name].source = source
            else:
                self.graph.documents[self.document_name] = Document(
                    name=self.document_name,
                    source=source,
                )
            self._refresh()

        self.app.push_screen(EditorScreen(doc.source), callback=on_save)

    def action_home(self) -> None:
        self.app.pop_screen()

    def action_palette(self) -> None:
        from mapper.screens.palette import CommandPalette

        self.app.push_screen(CommandPalette())

    def action_help(self) -> None:
        from mapper.screens.help import HelpScreen

        self.app.push_screen(HelpScreen())
