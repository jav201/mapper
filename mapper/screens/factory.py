"""Document factory screen for process-template editing."""
from __future__ import annotations

import re
from pathlib import Path

from rich.markup import escape
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from mapper import darkside, office
from mapper.model import Document, Graph, Node
from mapper.widgets.chrome import HintLine, KeyBar, TabStrip


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
        Binding("j", "next_sibling", "Siguiente", priority=True),
        Binding("k", "prev_sibling", "Anterior", priority=True),
        Binding("h", "parent", "Padre", priority=True),
        Binding("l", "child", "Hijo", priority=True),
        Binding("d", "edit_doc", "Editar doc", priority=True),
        Binding("i", "import_office", "Importar office", priority=True),
        Binding("g", "generate_office", "Generar", priority=True),
        Binding("0", "start_node", "Inicio", priority=True),
        Binding("q", "home", "Salir", priority=True),
        Binding("escape", "home", "Salir", priority=True),
        Binding("ctrl+p", "palette", "Paleta", priority=True),
        Binding("?", "help", "Ayuda", priority=True),
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
        map_id: str | None = None,
    ) -> None:
        super().__init__()
        self.graph = graph
        self.process_name = process_name
        self.map_id = map_id
        self._start_node_id = node_id if node_id in graph.nodes else graph.root_id
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
        yield HintLine("j/k/h/l navega · d edita · i importa · g genera · 0 inicio · q salir")
        yield KeyBar(
            [
                ("nav", [("j/k", "sig/ant"), ("h/l", "padre/hijo"), ("0", "inicio")]),
                ("doc", [("d", "editar"), ("i", "importar"), ("g", "generar")]),
                ("app", [("ctrl+p", "paleta"), ("?", "ayuda"), ("q/esc", "salir")]),
            ]
        )

    def on_mount(self) -> None:
        self._refresh()

    def _persist(self) -> None:
        """Persist graph changes to disk when we belong to a saved map."""
        if not self.map_id:
            return
        store = getattr(self.app, "store", None)
        if store is None:
            return
        store.save(self.map_id, self.graph)

    def _step_meter(self) -> Text:
        total = max(1, self._max_depth() + 1)
        filled = self._depth(self.nav.cursor or "")
        return darkside.step_meter(filled, total)

    def _parent_index(self) -> dict[str, str]:
        """First parent per node, built once. `parent_of` rescans every edge."""
        index: dict[str, str] = {}
        for edge in self.graph.edges:
            index.setdefault(edge.child_id, edge.parent_id)
        return index

    def _depth(self, nid: str) -> int:
        """Steps to the root along the parent chain.

        A cycle makes depth undefined, and the shipped loop answered one by
        never returning.  Depth here is a progress reading for the step meter,
        not the picture, so a cyclic chain is answered with its acyclic prefix
        instead of with a hang.
        """
        depth = 0
        current = nid
        seen = {nid}
        while True:
            parent = self.graph.parent_of(current)
            if parent is None or parent in seen:
                return depth
            depth += 1
            seen.add(parent)
            current = parent

    def _max_depth(self) -> int:
        """The deepest node, in one pass with the chains memoised.

        The shipped version called `_depth` per node and `_depth` called
        `parent_of` per step, each of which rescans every edge.  Measured on a
        chain: 0.004 s at depth 100, 1.717 s at depth 800.
        """
        parent = self._parent_index()
        depths: dict[str, int] = {}
        deepest = 0
        for start in self.graph.nodes:
            chain: list[str] = []
            current: str | None = start
            seen: set[str] = set()
            while current is not None and current not in depths and current not in seen:
                seen.add(current)
                chain.append(current)
                current = parent.get(current)
            # A chain that ran off the top is rooted at 0; one that ran into an
            # already-measured node continues from it; one that closed on
            # itself is a cycle, whose prefix is measured from 0 as `_depth`
            # does.
            base = depths[current] if current is not None and current in depths else -1
            for offset, nid in enumerate(reversed(chain)):
                depths[nid] = base + 1 + offset
            if chain:
                deepest = max(deepest, depths[chain[0]])
        return deepest

    def _tree_lines(self) -> Text:
        """Never propagates: `_refresh` runs from `on_mount`, outside any guard."""
        try:
            return self._tree_text()
        except ValueError:
            return Text.assemble(
                ("no se puede dibujar: el mapa tiene un ciclo", darkside.ALERT)
            )

    def _tree_text(self) -> Text:
        lines: list[tuple[str, str]] = []
        block = f"bold {darkside.GROUND} on {darkside.ACCENT}"
        index: dict[str, list[str]] = {}
        for edge in self.graph.edges:
            index.setdefault(edge.parent_id, []).append(edge.child_id)

        if self.graph.root_id is not None:
            # `visiting` is the active path: iterative alone turns the
            # recursion's bounded crash into an unbounded hang.
            visiting: set[str] = set()
            stack: list[tuple[str, int, bool]] = [(self.graph.root_id, 0, False)]
            while stack:
                nid, depth, leaving = stack.pop()
                if leaving:
                    visiting.discard(nid)
                    continue
                if nid in visiting:
                    raise ValueError(f"cycle through {nid}: the graph is not a tree")
                node = self.graph.nodes[nid]
                prefix = "  " * depth + "▸ "
                selected = nid == self.nav.cursor
                # `darkside.plain`, not `escape`: this string goes into a `Text`
                # with an explicit style, and `Text` does not parse markup — so
                # `escape` only prints visible backslashes while leaving the
                # ANSI/OSC control bytes that `_CONTROL_MAP` exists to strip.  The
                # rail already coerces the same file-derived titles this way; the
                # two files disagreed about one threat.  (Increment 2b review, F4.)
                title = darkside.plain(node.ficha.title or nid)
                lines.append((f"{prefix}{title}\n", block if selected else darkside.INK))
                children = index.get(nid)
                if not children:
                    continue
                visiting.add(nid)
                stack.append((nid, depth, True))
                # Reversed, so the LIFO stack still emits left to right.
                stack.extend((cid, depth + 1, False) for cid in reversed(children))
        return Text.assemble(*lines)

    def _is_office(self, doc: Document) -> bool:
        return doc.kind in {"docx", "pptx", "xlsx"}

    def _office_path(self, doc: Document) -> Path | None:
        if not doc.path:
            return None
        store = self.app.store  # type: ignore[attr-defined]
        candidate = Path(doc.path)
        if candidate.is_absolute():
            return candidate
        return store.workspace / candidate

    def _preview(self) -> Text:
        node = self.graph.nodes.get(self.nav.cursor or "")
        if node is None or not self.document_name:
            return Text.assemble(("sin documento", darkside.MUT))
        doc = self.graph.resolve_document(self.document_name, node)

        if self._is_office(doc):
            path = self._office_path(doc)
            if path is None or not path.exists():
                return Text.assemble(("archivo de plantilla no encontrado", darkside.ALERT))
            preview = office.extract_preview_text(path)
            # Show a resolved preview by replacing tags in the plain text.
            for key, value in doc.tags.items():
                preview = preview.replace(f"{{{{{key}}}}}", value)
            lines = [line.strip() for line in preview.splitlines() if line.strip()]
            text = Text()
            text.append(f"[{doc.kind}] ", style=darkside.ACCENT)
            text.append(escape(str(path)), style=darkside.MUT)
            text.append("\n", style="")
            for line in lines[:12]:
                text.append(escape(line[:120]), style=darkside.INK)
                text.append("\n", style="")
            if len(lines) > 12:
                text.append("…", style=darkside.MUT)
            return text

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

        if self._is_office(doc):
            path = self._office_path(doc)
            keys: set[str] = set(doc.tags)
            if path is not None and path.exists():
                keys.update(office.extract_tags(path))
            parts: list[tuple[str, str]] = []
            for key in sorted(keys):
                local = doc.tags.get(key, "")
                inherited = doc.inherited.get(key, "")
                parts.append((f"{{{{{escape(key)}}}}}  ", darkside.ACCENT))
                parts.append((f"{escape(local) or '-'}  ", darkside.INK))
                parts.append((f"{escape(inherited) or '-'}\n", darkside.MUT))
            return Text.assemble(*parts) if parts else Text.assemble(("(sin tags)", darkside.MUT))

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

        if self._is_office(doc):
            self.action_generate_office()
            return

        def on_save(source: str | None) -> None:
            if source is None:
                return
            if self.document_name in self.graph.documents:
                self.graph.documents[self.document_name].source = source
                self.graph.documents[self.document_name].kind = "text"
                self.graph.documents[self.document_name].path = ""
            else:
                self.graph.documents[self.document_name] = Document(
                    name=self.document_name,
                    source=source,
                )
            self._persist()
            self._refresh()

        self.app.push_screen(EditorScreen(doc.source), callback=on_save)

    def action_import_office(self) -> None:
        from mapper.app import _PromptScreen

        def on_path(path_str: str | None) -> None:
            if path_str is None:
                return
            source = Path(path_str).expanduser()
            if not source.exists():
                self.notify(f"archivo no encontrado: {source}", severity="error", markup=False)
                return
            kind = source.suffix.lower().lstrip(".")
            if kind not in {"docx", "pptx", "xlsx"}:
                self.notify("solo .docx / .pptx / .xlsx", severity="error")
                return
            store = self.app.store  # type: ignore[attr-defined]
            target = store.workspace / "templates" / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            import shutil

            shutil.copy2(source, target)
            rel = target.relative_to(store.workspace).as_posix()
            self.graph.documents[self.document_name] = Document(
                name=self.document_name,
                path=rel,
                kind=kind,
                template=True,
            )
            self._persist()
            self._refresh()
            self.notify(f"plantilla importada: {rel}", markup=False)

        self.app.push_screen(
            _PromptScreen("ruta del archivo office", "/ruta/a/plantilla.docx"),
            callback=on_path,
        )

    def action_generate_office(self) -> None:
        node = self.graph.nodes.get(self.nav.cursor or "")
        if node is None or not self.document_name:
            return
        doc = self.graph.resolve_document(self.document_name, node)
        if not self._is_office(doc):
            self.notify("el documento actual no es office")
            return
        path = self._office_path(doc)
        if path is None or not path.exists():
            self.notify("archivo de plantilla no encontrado", severity="error")
            return
        store = self.app.store  # type: ignore[attr-defined]
        suffix = Path(doc.path).suffix or ".docx"
        target = store.workspace / f"{self.document_name}-{node.id}{suffix}"
        try:
            office.resolve(path, doc.tags, target)
            self.notify(f"generado: {target}", markup=False)
        except Exception as exc:
            self.notify(f"no se pudo generar: {exc}", severity="error", markup=False)

    def action_start_node(self) -> None:
        """Return to the node that was selected when the factory opened."""
        if self._start_node_id and self._start_node_id in self.graph.nodes:
            self.nav.cursor = self._start_node_id
            self._refresh()

    def action_home(self) -> None:
        self.app.pop_screen()

    def action_palette(self) -> None:
        from mapper.screens.palette import CommandPalette

        self.app.push_screen(CommandPalette())

    def action_help(self) -> None:
        from mapper.screens.help import HelpScreen

        self.app.push_screen(HelpScreen())
