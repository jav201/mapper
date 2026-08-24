"""Textual TUI app for mapper — darkside UI."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from rich.markup import escape
from rich.text import Text
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import DataTable, Input, Label, Static

from . import darkside
from .diff import DiffResult, git_diff
from .export import save_svg
from .github import GitHubConnector, GitHubError
from .import_csv import preview_csv
from .keymap import groups_for_keybar
from .mermaid import dump as dump_mermaid, slugify
from .model import Document, Edge, Ficha, Graph, Node
from .motion import pulse_cursor
from .screens import CommandPalette, CoverageScreen, FactoryScreen, HelpScreen
from .store import MapStore, TEMPLATES
from .views.lane import HybridLaneRenderer, LaneRenderer, RailTimelineRenderer
from .views.layered import LayeredRenderer
from .views.outline import OutlineRenderer
from .views.radial import RadialRenderer
from .widgets.chrome import GroupBox, HintLine, KeyBar, TabStrip


class NavigationModel:
    """Cursor navigation over a tree graph."""

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


# ---------------------------------------------------------------------------
# Modal helpers
# ---------------------------------------------------------------------------


class _PromptScreen(ModalScreen[str | None]):
    """Simple darkside modal that returns a single text value."""

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, title: str, placeholder: str = "") -> None:
        super().__init__()
        self.title = title
        self.placeholder = placeholder

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(self.title, id="prompt-label"),
            Input(placeholder=self.placeholder, id="prompt-input"),
            Static("", id="prompt-hints"),
            id="prompt-dialog",
        )

    def on_mount(self) -> None:
        self.query_one("#prompt-input", Input).focus()
        hints = Text.assemble(
            ("↵", darkside.INK),
            (" confirmar   ", darkside.MUT),
            ("esc", darkside.INK),
            (" cancelar", darkside.MUT),
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
        ("y", "confirm", "Sí"),
        ("n", "dismiss", "No"),
        ("escape", "dismiss", "No"),
        ("q", "dismiss", "No"),
    ]

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(self.message, id="confirm-label"),
            Static("", id="confirm-hints"),
            id="confirm-dialog",
        )

    def on_mount(self) -> None:
        hints = Text.assemble(
            ("y", darkside.INK),
            (" sí   ", darkside.MUT),
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

    BINDINGS = [("escape", "dismiss", "Close"), ("q", "dismiss", "Close")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("elegir plantilla", id="template-title"),
            DataTable(id="template-table", cursor_type="row"),
            id="template-dialog",
        )

    def on_mount(self) -> None:
        table = self.query_one("#template-table", DataTable)
        table.clear()
        table.add_columns("▐ plantilla", "descripción")
        for key, data in TEMPLATES.items():
            desc = data.get("seed_title", key)
            table.add_row(escape(key), escape(desc), key=key)
        if table.row_count == 0:
            table.add_row("(sin plantillas)", "", key="")

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

    BINDINGS = [("escape", "dismiss", "Close"), ("q", "dismiss", "Close")]

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
            text.append("estado ", style=darkside.MUT)
            text.append(escape(ficha.state), style=darkside.INK)
            text.append("\n")

        have, req = ficha.required_coverage(self.graph.schema)
        if req:
            text.append("cobertura ", style=darkside.MUT)
            text.append_text(darkside.step_meter(have, req))
            text.append("\n")

        doc = ficha.fields.get("D", "")
        text.append("documento ", style=darkside.MUT)
        text.append(escape(doc) if doc else "sin acta",
                    style=darkside.INK if doc else darkside.ALERT)
        text.append("\n")
        text.append("dueño ", style=darkside.MUT)
        text.append(escape(ficha.fields.get("O", "—")), style=darkside.INK)
        text.append("\n")
        text.append("creado ", style=darkside.MUT)
        text.append(escape(ficha.fields.get("Y", "—")), style=darkside.INK)
        text.append("\n")

        linked = self.node.linked_map_id()
        if linked:
            text.append("enlace ", style=darkside.MUT)
            text.append(escape(linked), style=darkside.ACCENT)
            text.append("  (↵ abre el mapa)", style=darkside.MUT)
            text.append("\n")

        if ficha.notes:
            text.append("\nnotas\n", style=darkside.MUT)
            text.append(escape(ficha.notes), style=darkside.INK)

        if ficha.fields:
            text.append("\ncampos\n", style=darkside.MUT)
            for key, value in ficha.fields.items():
                if key in {"D", "O", "Y", "map"}:
                    continue
                text.append(f"  {escape(key)} ", style=darkside.MUT)
                text.append(escape(value), style=darkside.INK)
                text.append("\n")

        if ficha.attachments:
            text.append("\nadjuntos\n", style=darkside.MUT)
            for att in ficha.attachments:
                text.append(f"  {escape(att.caption or att.path)}\n", style=darkside.INK)

        self.query_one("#ficha-content", Static).update(text)

    def action_dismiss(self) -> None:
        self.dismiss(None)


class ConstructScreen(ModalScreen[str | None]):
    """Ask for a new map name and return it."""

    BINDINGS = [("escape", "cancel", "Cancelar")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("nuevo mapa", id="construct-label"),
            Input(placeholder="mi-nuevo-mapa", id="construct-input"),
            Static("", id="construct-hints"),
            id="construct-dialog",
        )

    def on_mount(self) -> None:
        self.query_one("#construct-input", Input).focus()
        hints = Text.assemble(
            ("↵", darkside.INK),
            (" crear   ", darkside.MUT),
            ("esc", darkside.INK),
            (" cancelar", darkside.MUT),
        )
        self.query_one("#construct-hints", Static).update(hints)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        name = event.value.strip().replace(" ", "-")
        if name:
            self.dismiss(name)


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------


class HomeScreen(Screen):
    """Home screen with resume row, recents and door shortcuts."""

    BINDINGS = [
        ("c", "consult", "Consultar mapas"),
        ("p", "plug", "Conectar repo"),
        ("n", "construct", "Construir"),
        ("t", "template", "Plantilla"),
        ("i", "import_csv", "Importar CSV"),
        ("f", "factory", "Fábrica"),
        ("r", "resume", "Retomar"),
        ("j", "table_down", "Bajar"),
        ("k", "table_up", "Subir"),
        ("q", "quit", "Salir"),
    ]

    def compose(self) -> ComposeResult:
        yield TabStrip("c")
        yield Static("", id="home-identity")
        yield GroupBox(Static(id="home-resume"), id="home-resume-box")
        yield GroupBox(
            Vertical(
                Static("", id="home-empty"),
                DataTable(id="home-recents", cursor_type="row"),
                id="home-recents-inner",
            ),
            id="home-recents-box",
        )
        yield HintLine("elige una puerta para empezar")
        yield KeyBar(
            [
                ("nav", [("j/k", "elegir"), ("↵", "abrir"), ("r", "retomar")]),
                ("doors", [("c", "consultar"), ("p", "repo"), ("n", "construir"),
                           ("t", "plantilla"), ("i", "importar csv"), ("f", "fábrica")]),
                ("app", [("ctrl+p", "paleta"), ("?", "ayuda"), ("q", "salir")]),
            ]
        )

    def on_mount(self) -> None:
        store: MapStore = self.app.store  # type: ignore[attr-defined]

        # Resume row
        resume = self.query_one("#home-resume", Static)
        map_id, node_id = store.last_session()
        if map_id and node_id:
            try:
                graph = store.load(map_id)
                node = graph.nodes.get(node_id)
                node_name = node.ficha.title if node else node_id
            except Exception:
                node_name = node_id
            resume.update(
                Text.assemble(
                    (" ↩ retomar ", f"bold {darkside.GROUND} on {darkside.ACCENT}"),
                    (" ", ""),
                    (escape(map_id), darkside.INK),
                    (" / ", darkside.MUT),
                    (escape(node_name), darkside.MUT),
                    ("   última sesión", darkside.MUT),
                )
            )
            self.query_one("#home-resume-box", GroupBox).display = True
        else:
            self.query_one("#home-resume-box", GroupBox).display = False

        # Recents table
        table = self.query_one("#home-recents", DataTable)
        table.clear()
        table.add_columns("▐ name", "kind", "nodos", "docs")

        identity = self.query_one("#home-identity", Static)
        mmd_files = sorted(store.workspace.glob("*.mmd"))
        if not mmd_files:
            table.display = False
            self.query_one("#home-empty", Static).update(self._empty_text())
            self.query_one("#home-empty", Static).display = True
            identity.display = False
            return

        table.display = True
        self.query_one("#home-empty", Static).display = False
        glyph, _ = darkside.moon(date.today())
        identity_text = Text()
        identity_text.append(glyph, style=darkside.WORDMARK)
        identity_text.append(" mapper", style=darkside.WORDMARK)
        identity_text.append("   mapas vivos", style=darkside.MUT)
        identity.update(identity_text)
        identity.display = True
        for mmd in mmd_files:
            map_name = mmd.stem
            try:
                graph = store.load(map_name)
                kind = "legacy" if graph.schema else "concept"
                nodos = str(len(graph.nodes))
                docs = str(len(graph.documents))
            except Exception:
                kind, nodos, docs = "concept", "0", "0"
            table.add_row(
                escape(map_name),
                Text.assemble((f" {kind} ", f"{darkside.INK} on {darkside.STEP}")),
                nodos,
                docs,
                key=map_name,
            )

    def _empty_text(self) -> Text:
        lines: list[tuple[str, str]] = [
            ("c", darkside.ACCENT),
            (" consult  ", darkside.INK),
            ("abre un mapa reciente\n", darkside.MUT),
            ("p", darkside.ACCENT),
            (" repo     ", darkside.INK),
            ("conecta un repositorio\n", darkside.MUT),
            ("n", darkside.ACCENT),
            (" construct", darkside.INK),
            ("crea un nuevo mapa\n", darkside.MUT),
            ("t", darkside.ACCENT),
            (" template ", darkside.INK),
            ("mapa desde plantilla\n", darkside.MUT),
            ("i", darkside.ACCENT),
            (" import   ", darkside.INK),
            ("CSV / TSV de nodos\n", darkside.MUT),
            ("f", darkside.ACCENT),
            (" factory  ", darkside.INK),
            ("documentos de proceso\n", darkside.MUT),
        ]
        return Text.assemble(*lines)

    def action_consult(self) -> None:
        table = self.query_one("#home-recents", DataTable)
        if table.display:
            table.focus()

    def action_table_down(self) -> None:
        table = self.query_one("#home-recents", DataTable)
        if table.display and table.cursor_row is not None:
            table.cursor_down()

    def action_table_up(self) -> None:
        table = self.query_one("#home-recents", DataTable)
        if table.display and table.cursor_row is not None:
            table.cursor_up()

    def action_resume(self) -> None:
        store: MapStore = self.app.store  # type: ignore[attr-defined]
        map_id, node_id = store.last_session()
        if map_id and node_id:
            self.app.push_screen(MapScreen(map_id))

    def action_plug(self) -> None:
        self.app.push_screen(PlugRepoScreen())

    def action_factory(self) -> None:
        demo = Graph()
        demo.add_node(Node(id="root", ficha=Ficha(title="proceso demo")))
        demo.add_node(Node(id="n1", ficha=Ficha(title="paso uno")))
        demo.add_edge(Edge("root", "n1"))
        demo.documents["plantilla"] = Document(name="plantilla", source="hola {{nombre}}")
        self.app.push_screen(FactoryScreen(demo, process_name="demo"))

    def _open_map(self, name: str | None) -> None:
        if not name:
            return
        self.app.push_screen(MapScreen(name))

    def action_construct(self) -> None:
        def on_name(name: str | None) -> None:
            if not name:
                return
            store: MapStore = self.app.store  # type: ignore[attr-defined]
            try:
                store.create_seed(name)
                self.app.push_screen(MapScreen(name))
            except Exception as e:
                self.notify(f"no se pudo crear el mapa: {e}", severity="error")

        self.app.push_screen(ConstructScreen(), callback=on_name)

    def action_template(self) -> None:
        def on_pick(result: tuple[str, str] | None) -> None:
            if result is None:
                return
            name, template_id = result
            store: MapStore = self.app.store  # type: ignore[attr-defined]
            try:
                store.create_from_template(name, template_id)
                self.app.push_screen(MapScreen(name))
            except Exception as e:
                self.notify(f"no se pudo crear el mapa: {e}", severity="error")

        def on_template(template_id: str | None) -> None:
            if template_id is None:
                return
            self.app.push_screen(
                _PromptScreen("nombre del mapa", f"{template_id}-map"),
                callback=lambda name: on_pick((name, template_id)) if name else None,
            )

        if not TEMPLATES:
            self.notify("no hay plantillas disponibles")
            return
        self.app.push_screen(_TemplateScreen(), callback=on_template)

    def action_import_csv(self) -> None:
        def on_path(path_str: str | None) -> None:
            if path_str is None:
                return
            path = Path(path_str).expanduser()
            if not path.exists():
                self.notify(f"archivo no encontrado: {path}", severity="error")
                return
            try:
                preview = preview_csv(path)
            except Exception as e:
                self.notify(f"no se pudo leer CSV: {e}", severity="error")
                return
            self.app.push_screen(_ImportPreviewScreen(preview, path))

        self.app.push_screen(
            _PromptScreen("ruta del CSV / TSV", "/ruta/a/nodos.csv"),
            callback=on_path,
        )

    def action_quit(self) -> None:
        self.app.exit()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        map_id = str(event.row_key.value)
        self.app.push_screen(MapScreen(map_id))

    def on_screen_resume(self) -> None:
        """Refresh the recents list when returning to home."""
        self.on_mount()


class _ImportPreviewScreen(Screen):
    """Preview a CSV import before saving it as a named map."""

    BINDINGS = [
        ("s", "save", "Guardar"),
        ("escape", "home", "Volver"),
        ("ctrl+p", "palette", "Paleta"),
        ("?", "help", "Ayuda"),
    ]

    def __init__(self, preview_graph: Graph, source_path: Path) -> None:
        super().__init__()
        self.preview_graph = preview_graph
        self.source_path = source_path

    def compose(self) -> ComposeResult:
        yield TabStrip("i", crumb=["import", self.source_path.name])
        yield Static("", id="import-preview-canvas")
        yield HintLine("s guarda · esc volver")
        yield KeyBar(groups_for_keybar(["app"]))

    def on_mount(self) -> None:
        self.refresh_canvas()

    def refresh_canvas(self) -> None:
        canvas = self.query_one("#import-preview-canvas", Static)
        renderer = LayeredRenderer()
        size = self.size or self.app.size
        text = renderer.render(
            self.preview_graph,
            selected_id=self.preview_graph.root_id,
            w=max(20, size.width),
            h=max(5, size.height - 10),
        )
        canvas.update(text)
        pulse_cursor(canvas)

    def action_save(self) -> None:
        def on_name(name: str | None) -> None:
            if not name:
                return
            store: MapStore = self.app.store  # type: ignore[attr-defined]
            try:
                store.save(name, self.preview_graph)
                self.app.push_screen(MapScreen(name))
            except Exception as e:
                self.notify(f"no se pudo guardar: {e}", severity="error")

        self.app.push_screen(
            _PromptScreen("guardar como", self.source_path.stem),
            callback=on_name,
        )

    def action_home(self) -> None:
        self.app.pop_screen()

    def action_palette(self) -> None:
        self.app.action_palette()

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())


class PlugRepoScreen(Screen):
    """Input screen for plugging a GitHub repo."""

    BINDINGS = [
        ("escape", "home", "Volver"),
        ("ctrl+p", "palette", "Paleta"),
        ("?", "help", "Ayuda"),
    ]

    def compose(self) -> ComposeResult:
        yield TabStrip("p", crumb=["conectar repo"])
        yield Vertical(
            Label("conectar repositorio github", id="repo-title"),
            Input(placeholder="owner/name", id="repo-input"),
            id="repo-dialog",
        )
        yield HintLine("ingresa owner/name y presiona ↵", "↵")
        yield KeyBar(groups_for_keybar(["app"]))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "repo-input":
            repo = event.value.strip()
            if repo:
                self.app.push_screen(RepoScreen(repo))

    def action_home(self) -> None:
        self.app.pop_screen()

    def action_palette(self) -> None:
        self.app.action_palette()

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())


class RepoScreen(Screen):
    """A GitHub repo rendered as branch lanes."""

    BINDINGS = [
        ("j", "next_sibling", "Siguiente"),
        ("k", "prev_sibling", "Anterior"),
        ("v", "cycle_view", "Cambiar vista"),
        ("q", "home", "Inicio"),
        ("ctrl+p", "palette", "Paleta"),
        ("?", "help", "Ayuda"),
    ]

    def __init__(self, repo: str):
        super().__init__()
        self.repo = repo
        self.graph = Graph()
        self.nav: NavigationModel = NavigationModel(self.graph)
        self._renderers = [
            LaneRenderer(),
            RailTimelineRenderer(),
            HybridLaneRenderer(),
        ]
        self._renderer_index = 0

    @property
    def renderer(self):
        return self._renderers[self._renderer_index]

    def compose(self) -> ComposeResult:
        yield TabStrip("p", crumb=[self.repo])
        yield Static("(cargando repo...)", id="repo-canvas")
        yield HintLine("j/k navega · v cambia vista · q inicio")
        yield KeyBar(
            [
                ("nav", [("j/k", "sig/ant")]),
                ("view", [("v", "cambiar vista")]),
                ("app", [("ctrl+p", "paleta"), ("?", "ayuda"), ("q", "inicio")]),
            ]
        )

    @work(thread=True)
    def fetch_graph(self) -> Graph:
        return GitHubConnector(self.repo).fetch()

    async def on_mount(self) -> None:
        canvas = self.query_one("#repo-canvas", Static)
        canvas.update("(cargando repo...)")
        try:
            self.graph = await self.fetch_graph()
        except GitHubError as exc:
            self.notify(str(exc), severity="error")
            self.graph = Graph()
        self.nav = NavigationModel(self.graph)
        self.refresh_canvas()

    def refresh_canvas(self) -> None:
        canvas = self.query_one("#repo-canvas", Static)
        size = self.size or self.app.size
        w = max(20, size.width)
        h = max(5, size.height - 6)
        text = self.renderer.render(
            self.graph,
            selected_id=self.nav.cursor,
            w=w,
            h=h,
        )
        canvas.update(text)
        pulse_cursor(canvas)

    def action_next_sibling(self) -> None:
        nxt = self.nav.next_sibling()
        if nxt:
            self.nav.cursor = nxt
            self.refresh_canvas()

    def action_prev_sibling(self) -> None:
        prv = self.nav.prev_sibling()
        if prv:
            self.nav.cursor = prv
            self.refresh_canvas()

    def action_cycle_view(self) -> None:
        self._renderer_index = (self._renderer_index + 1) % len(self._renderers)
        self.refresh_canvas()
        names = ["lista", "rail", "híbrido"]
        self.notify(f"vista: {names[self._renderer_index]}")

    def action_home(self) -> None:
        self.app.pop_screen()

    def action_palette(self) -> None:
        self.app.action_palette()

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())


class MapScreen(Screen):
    """A map rendered as a layered tree."""

    BINDINGS = [
        ("j", "next_sibling", "Siguiente"),
        ("k", "prev_sibling", "Anterior"),
        ("l", "child", "Hijo"),
        ("h", "parent", "Padre"),
        ("enter", "open_ficha", "Abrir"),
        ("slash", "search", "Buscar"),
        ("f", "toggle_focus", "Foco"),
        ("o", "toggle_outline", "Outline"),
        ("r", "toggle_radial", "Radial"),
        ("e", "export_svg", "Exportar SVG"),
        ("a", "add_child", "Agregar hijo"),
        ("d", "open_documents", "Documentos"),
        ("x", "archive", "Archivar"),
        ("u", "undo", "Deshacer"),
        ("=", "toggle_diff", "Diff vs HEAD"),
        ("m", "coverage", "Cobertura"),
        ("q", "home", "Inicio"),
        ("escape", "back_or_home", "Volver"),
        ("ctrl+p", "palette", "Paleta"),
        ("?", "help", "Ayuda"),
    ]

    def __init__(self, map_id: str, source_crumb: list[str] | None = None) -> None:
        super().__init__()
        self.map_id = map_id
        self.source_crumb = source_crumb
        self.store: MapStore | None = None
        self.graph: Graph = Graph()
        self.base_graph: Graph = Graph()
        self.nav: NavigationModel = NavigationModel(self.graph)
        self.renderer = LayeredRenderer()
        self.outline_renderer = OutlineRenderer()
        self.radial_renderer = RadialRenderer()
        self.query_text = ""
        self.focus_active = False
        self.outline_mode = False
        self.radial_mode = False
        self.diff_active = False
        self.diff: DiffResult | None = None
        self._snapshots: list[bytes] = []

    def compose(self) -> ComposeResult:
        crumb_prefix = self.source_crumb or [self.map_id]
        yield TabStrip("c", crumb=crumb_prefix + [""])
        yield Static("(cargando mapa...)", id="map-canvas")
        yield Input(placeholder="/buscar", id="search-input")
        yield GroupBox(Static(id="map-ficha"), id="map-ficha-box")
        yield HintLine("navega con j/k/h/l · ↵ ficha · / buscar")
        yield KeyBar(
            [
                ("nav", [("j/k", "sig/ant"), ("h/l", "padre/hijo"), ("↵", "abrir")]),
                ("node", [("a", "agregar hijo"), ("d", "documento"), ("x", "archivar")]),
                ("view", [("f", "foco"), ("o", "outline"), ("r", "radial"),
                          ("/", "buscar"), ("e", "exportar"), ("=", "diff"), ("m", "cobertura")]),
                ("app", [("ctrl+p", "paleta"), ("u", "deshacer"), ("?", "ayuda"), ("q", "inicio")]),
            ]
        )

    def on_mount(self) -> None:
        self.store = self.app.store  # type: ignore[attr-defined]
        search = self.query_one("#search-input", Input)
        search.display = False
        search.disabled = True
        self.focus()

        if self.map_id == "new":
            self.graph = Graph()
            self.graph.add_node(Node(id="root", ficha=Ficha(title="nuevo mapa")))
            self.base_graph = self.graph
            if self.store is not None:
                self.store.save(self.map_id, self.graph)
        else:
            try:
                self.base_graph = self.store.load(self.map_id)
                self.graph = self.base_graph
            except Exception as e:
                self.notify(f"error cargando mapa: {e}", severity="error")
                self.graph = Graph()
                self.graph.add_node(Node(id="root", ficha=Ficha(title="error")))
                self.base_graph = self.graph

        self.nav = NavigationModel(self.graph)

        # Resume cursor from last session if it points into this map.
        if self.store is not None:
            last_map, last_node = self.store.last_session()
            if last_map == self.map_id and last_node in self.graph.nodes:
                self.nav.cursor = last_node
            self.store.record_session(self.map_id, self.nav.cursor)

        self.refresh_canvas()

    def _current_renderer(self):
        if self.outline_mode:
            return self.outline_renderer
        if self.radial_mode:
            return self.radial_renderer
        return self.renderer

    def _current_crumb(self) -> list[str]:
        prefix = self.source_crumb or [self.map_id]
        if self.source_crumb:
            prefix = prefix + [f"linked: {self.map_id}"]
        return prefix

    def refresh_canvas(self) -> None:
        canvas = self.query_one("#map-canvas", Static)
        renderer = self._current_renderer()
        size = self.size or self.app.size
        w = max(20, size.width)
        h = max(5, size.height - 10)
        text = renderer.render(
            self.graph,
            selected_id=self.nav.cursor,
            w=w,
            h=h,
            query=self.query_text,
            diff=self.diff if self.diff_active else None,
        )
        canvas.update(text)
        pulse_cursor(canvas)

        tab = self.query_one(TabStrip)
        node = self.graph.nodes.get(self.nav.cursor or "")
        node_title = node.ficha.title if node else ""
        tab.set_crumb(self._current_crumb() + [node_title])

        self.query_one("#map-ficha", Static).update(self._ficha_text(node, w - 4))

    def _ficha_text(self, node: Node | None, width: int) -> Text:
        if node is None:
            return Text.assemble(("  (selecciona un nodo)", darkside.MUT))

        ficha = node.ficha
        text = Text()
        text.append("▸ ", style=darkside.ACCENT)
        text.append(escape(ficha.title or node.id), style=f"bold {darkside.INK}")
        if ficha.meta:
            text.append("   ")
            text.append(escape(ficha.meta), style=darkside.MUT)

        have, req = ficha.required_coverage(self.graph.schema)
        if req:
            text.append("   ")
            text.append_text(darkside.step_meter(have, req))

        text.append("\n")

        doc = ficha.fields.get("D", "")
        text.append("  documento ", style=darkside.MUT)
        text.append(escape(doc) if doc else "sin acta",
                    style=darkside.INK if doc else darkside.ALERT)
        text.append("   dueño ", style=darkside.MUT)
        text.append(escape(ficha.fields.get("O", "—")), style=darkside.INK)
        text.append("   creado ", style=darkside.MUT)
        text.append(escape(ficha.fields.get("Y", "—")), style=darkside.INK)

        linked = node.linked_map_id()
        if linked:
            text.append("   enlace ", style=darkside.MUT)
            text.append(escape(linked), style=darkside.ACCENT)

        if ficha.notes:
            note = ficha.notes
            if len(note) > width - 4:
                note = note[: width - 5] + "…"
            text.append("\n  ")
            text.append(escape(note), style=darkside.MUT)

        return text

    def _push_snapshot(self) -> None:
        if self.store is None:
            return
        mmd = dump_mermaid(self.graph)
        sidecar = self.store._build_sidecar(self.graph)
        import yaml

        yml = yaml.safe_dump(sidecar, sort_keys=False, allow_unicode=True)
        self._snapshots.append(json.dumps({"mmd": mmd, "yml": yml}).encode())

    def _pop_snapshot(self) -> None:
        if not self._snapshots:
            self.notify("nada que deshacer")
            return
        import yaml

        blob = self._snapshots.pop()
        data = json.loads(blob.decode())
        graph = self.store._graph_from_sidecar(data["mmd"], yaml.safe_load(data["yml"]) or {})
        self.graph = graph
        self.base_graph = graph
        if self.nav.cursor not in self.graph.nodes:
            self.nav.cursor = self.graph.root_id
        self.store.save(self.map_id, self.graph)
        self.refresh_canvas()
        self.notify("deshacer aplicado")

    def action_next_sibling(self) -> None:
        nxt = self.nav.next_sibling()
        if nxt:
            self.nav.cursor = nxt
            self.refresh_canvas()

    def action_prev_sibling(self) -> None:
        prv = self.nav.prev_sibling()
        if prv:
            self.nav.cursor = prv
            self.refresh_canvas()

    def action_child(self) -> None:
        ch = self.nav.first_child()
        if ch:
            self.nav.cursor = ch
            self.refresh_canvas()

    def action_parent(self) -> None:
        p = self.nav.parent()
        if p:
            self.nav.cursor = p
            self.refresh_canvas()

    def action_open_ficha(self) -> None:
        node = self.graph.nodes.get(self.nav.cursor or "")
        if node is None:
            return
        linked = node.linked_map_id()
        if linked:
            crumb_back = self._current_crumb() + [node.ficha.title or node.id]
            self.app.push_screen(MapScreen(linked, source_crumb=crumb_back))
            return
        self.app.push_screen(_FichaScreen(node, self.graph))

    def action_search(self) -> None:
        inp = self.query_one("#search-input", Input)
        inp.disabled = False
        inp.display = True
        inp.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search-input":
            self.query_text = event.value
            event.input.display = False
            event.input.disabled = True
            self.focus()
            self.refresh_canvas()

    def on_input_blurred(self, event: Input.Blurred) -> None:
        if event.input.id == "search-input":
            event.input.display = False
            event.input.disabled = True
            self.focus()

    def action_toggle_focus(self) -> None:
        if self.focus_active:
            self.graph = self.base_graph
            self.focus_active = False
            self.nav = NavigationModel(self.graph)
            if self.nav.cursor not in self.graph.nodes:
                self.nav.cursor = self.graph.root_id
            self.refresh_canvas()
            return

        if self.nav.cursor is None or self.nav.cursor not in self.graph.nodes:
            return
        self._push_snapshot()
        self.graph = self.base_graph.focus(self.nav.cursor)
        self.focus_active = True
        self.nav = NavigationModel(self.graph)
        self.refresh_canvas()

    def action_toggle_outline(self) -> None:
        self.outline_mode = not self.outline_mode
        self.radial_mode = False
        self.refresh_canvas()

    def action_toggle_radial(self) -> None:
        self.radial_mode = not self.radial_mode
        self.outline_mode = False
        self.refresh_canvas()

    def action_toggle_diff(self) -> None:
        if self.diff_active:
            self.diff_active = False
            self.refresh_canvas()
            self.notify("diff oculto")
            return
        if self.store is None:
            return
        diff = git_diff(self.map_id, self.store)
        if diff is None:
            self.notify("sin diff disponible (¿está el mapa en git?)")
            return
        self.diff = diff
        self.diff_active = True
        self.refresh_canvas()
        added = len(diff.added)
        removed = len(diff.removed)
        changed = len(diff.changed)
        self.notify(f"diff: +{added} -{removed} ~{changed}")

    def action_coverage(self) -> None:
        def on_select(node_id: str | None) -> None:
            if node_id is None or node_id not in self.graph.nodes:
                return
            self.nav.cursor = node_id
            self.refresh_canvas()

        self.app.push_screen(CoverageScreen(self.graph, self.map_id), callback=on_select)

    def action_export_svg(self) -> None:
        if self.store is None:
            return
        try:
            size = self.size or self.app.size
            renderer = self._current_renderer()
            text = renderer.render(
                self.graph,
                selected_id=self.nav.cursor,
                w=max(20, size.width),
                h=max(5, size.height - 10),
                query=self.query_text,
            )
            path = self.store.workspace / f"{self.map_id}.svg"
            save_svg(text, path)
            self.notify(f"svg exportado a {path}")
        except Exception as e:
            self.notify(f"exportación fallida: {e}", severity="error")

    def _guard_focus_mutation(self) -> bool:
        """Return True if a structural mutation should proceed."""
        if self.focus_active:
            self.notify("no se puede editar con focus activo (presiona f para salir)")
            return False
        return True

    def action_add_child(self) -> None:
        if self.nav.cursor is None or self.nav.cursor not in self.graph.nodes:
            self.notify("selecciona un nodo primero")
            return
        if not self._guard_focus_mutation():
            return

        def on_title(title: str | None) -> None:
            if not title or self.store is None:
                return
            self._push_snapshot()
            parent_id = self.nav.cursor
            base = slugify(title) or "n"
            nid = base
            counter = 1
            while nid in self.graph.nodes:
                nid = f"{base}-{counter}"
                counter += 1
            node = Node(id=nid, ficha=Ficha(title=title))
            self.graph.add_node(node)
            self.graph.add_edge(Edge(parent_id=parent_id, child_id=nid))
            self.store.save(self.map_id, self.graph)
            self.base_graph = self.graph
            self.nav.cursor = nid
            self.refresh_canvas()

        self.app.push_screen(_PromptScreen("nombre del hijo", "nuevo hijo"), callback=on_title)

    def action_open_documents(self) -> None:
        node_id = self.nav.cursor
        if node_id is None or node_id not in self.graph.nodes:
            self.notify("selecciona un nodo primero")
            return
        doc_name = self.graph.document_names()[0] if self.graph.document_names() else ""
        self.app.push_screen(
            FactoryScreen(
                self.graph,
                process_name=self.map_id,
                node_id=node_id,
                document_name=doc_name,
                map_id=self.map_id,
            )
        )

    def action_archive(self) -> None:
        if self.nav.cursor is None or self.nav.cursor not in self.graph.nodes or self.store is None:
            return
        if not self._guard_focus_mutation():
            return
        node = self.graph.nodes[self.nav.cursor]

        def do_archive(confirmed: bool) -> None:
            if not confirmed:
                return
            self._push_snapshot()
            self._remove_subtree(self.nav.cursor)
            self.store.save(self.map_id, self.graph)
            self.base_graph = self.graph
            self.nav.cursor = self.graph.root_id
            self.refresh_canvas()
            self.notify(f"archivado: {node.ficha.title or node.id}")

        if self.nav.cursor == self.graph.root_id:
            self.app.push_screen(
                _ConfirmScreen("¿archivar el nodo raíz? esto reemplazará la raíz del mapa."),
                callback=do_archive,
            )
        else:
            do_archive(True)

    def _remove_subtree(self, root_id: str) -> None:
        remove: set[str] = set()
        stack = [root_id]
        while stack:
            nid = stack.pop()
            if nid in remove:
                continue
            remove.add(nid)
            stack.extend(self.graph.children_of(nid))
        self.graph.nodes = {k: v for k, v in self.graph.nodes.items() if k not in remove}
        self.graph.edges = [
            e for e in self.graph.edges if e.parent_id not in remove and e.child_id not in remove
        ]
        if self.graph.root_id in remove:
            self.graph.root_id = next(iter(self.graph.nodes), None)

    def action_undo(self) -> None:
        self._pop_snapshot()

    def action_home(self) -> None:
        self.app.pop_screen()

    def action_back_or_home(self) -> None:
        """Pop one screen when coming from a linked map, otherwise go home."""
        if self.source_crumb:
            self.app.pop_screen()
        else:
            self.app.pop_screen()

    def action_palette(self) -> None:
        self.app.action_palette()

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())


class MapperApp(App):
    """Main application entry point."""

    COMMAND_PALETTE_ENABLE = False

    CSS = """
    Screen { background: #000000; color: #f5f5f5; }
    .group-box { background: #121212; }

    Input {
        border: none;
        background: #262626;
        color: #f5f5f5;
        padding: 0 1;
    }
    Input:focus { border: none; background: #262626; color: #f5f5f5; }

    DataTable {
        background: #121212;
        color: #f5f5f5;
        border: none;
    }
    DataTable > .datatable--header {
        background: #262626;
        color: #737373;
        text-style: bold;
    }
    DataTable > .datatable--cursor {
        background: #1783ff;
        color: #000000;
    }
    DataTable > .datatable--hover {
        background: #262626;
    }

    HomeScreen { layout: vertical; }
    #home-resume-box { height: auto; }
    #home-recents-box { height: 1fr; }
    #home-recents { width: 100%; height: 100%; border: none; }
    #home-empty { width: 100%; height: 100%; }
    #home-identity { width: 100%; text-align: center; padding: 1 0; }

    MapScreen, RepoScreen, PlugRepoScreen { layout: vertical; }
    #map-canvas, #repo-canvas { width: 100%; height: 1fr; }
    #map-ficha-box { height: auto; }
    #map-ficha { height: auto; padding: 0 1; }
    #search-input { dock: bottom; display: none; }

    PlugRepoScreen { align: center middle; }
    #repo-dialog { width: 50; height: auto; background: #121212; padding: 1 2; }
    #repo-title { text-style: bold; color: #f5f5f5; margin-bottom: 1; }

    ConstructScreen, _PromptScreen, _FichaScreen, _TemplateScreen, _ConfirmScreen {
        align: center middle;
        background: #000000 70%;
    }
    #construct-dialog, #prompt-dialog, #ficha-dialog, #template-dialog, #confirm-dialog {
        width: 50;
        height: auto;
        background: #121212;
        padding: 1 2;
    }
    #template-table { width: 100%; height: auto; max-height: 20; border: none; background: #121212; }
    #template-table > .datatable--header { background: #262626; color: #737373; text-style: bold; }
    #template-table > .datatable--cursor { background: #1783ff; color: #000000; }
    #ficha-dialog { width: 60; max-height: 28; }
    #construct-label, #prompt-label, #template-title, #confirm-label {
        text-align: center;
        text-style: bold;
        color: #f5f5f5;
        margin-bottom: 1;
    }
    #construct-hints, #prompt-hints, #confirm-hints {
        text-align: center;
        color: #737373;
        margin-top: 1;
    }

    _ImportPreviewScreen { layout: vertical; }
    #import-preview-canvas { width: 100%; height: 1fr; }
    """

    BINDINGS = [
        ("ctrl+p", "palette", "Paleta"),
        ("?", "help", "Ayuda"),
        ("q", "quit", "Salir"),
    ]

    def __init__(self, workspace: Path | str):
        super().__init__()
        self.store = MapStore(workspace)

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())

    def on_screen_resume(self, event) -> None:
        """Refresh the map list when returning to home."""
        if isinstance(self.screen, HomeScreen):
            self.screen.on_mount()

    def action_palette(self) -> None:
        target_screen = self.screen

        def on_command(action: str | None) -> None:
            if not action:
                return
            method_name = f"action_{action.replace(' ', '_')}"
            if hasattr(target_screen, method_name):
                getattr(target_screen, method_name)()
            elif hasattr(self, method_name):
                getattr(self, method_name)()

        self.push_screen(CommandPalette(), callback=on_command)

    def action_help(self) -> None:
        self.push_screen(HelpScreen())

    def action_quit(self) -> None:
        self.exit()


def main() -> None:
    import sys

    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / "maps"
    app = MapperApp(workspace)
    app.run()


if __name__ == "__main__":
    main()
