"""Textual TUI app for mapper — darkside UI."""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path

from rich.markup import escape
from rich.text import Text
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
from textual.widgets import DataTable, Input, Label, Static

from . import darkside
from .diff import DiffResult, git_diff
from .export import save_svg
from .github import GitHubConnector, GitHubError
from .import_csv import preview_csv
from .keymap import (
    GROUP_SCOPE,
    SCOPE_APP,
    SCOPE_HOME,
    SCOPE_IMPORT,
    SCOPE_MAP,
    SCOPE_PLUG,
    SCOPE_REPO,
    groups_for_keybar,
    textual_bindings,
)
from .mermaid import dump as dump_mermaid, slugify
from .model import Document, Edge, Ficha, Graph, Node
from .motion import pulse_cursor
from .screens import CommandPalette, CoverageScreen, FactoryScreen, HelpScreen, SettingsScreen
from .store import MapStore, TEMPLATES
from .views.layered import LayeredRenderer
from .views.outline import OutlineRenderer
from .views.radial import RadialRenderer
from .widgets.chrome import GroupBox, HintLine, KeyBar, TabStrip
from .widgets.inspector import INSPECTOR_WIDTH, FichaInspector


def screen_bindings(scope: str) -> list[Binding]:
    """Generate a screen's `BINDINGS` from the one keymap seat (US-N03).

    Screens never hand-write a binding list: the seat is the single source, so the
    keys a screen binds and the keys the palette and help advertise cannot drift.
    """
    return [
        Binding(key, action, label, priority=priority)
        for key, action, label, priority in textual_bindings(scope)
    ]


def keybar_groups(scope: str) -> list[str]:
    """The keybar's group order for *scope*, derived from the seat.

    Derived rather than hand-listed: a second list naming the map's groups would
    be exactly the drift the seat exists to prevent.
    """
    return [g for g, s in GROUP_SCOPE.items() if s in (scope, SCOPE_APP)]


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
    """Home screen with GLANCE posture: one hero, everything else available."""

    KEY_SCOPE = SCOPE_HOME
    BINDINGS = screen_bindings(SCOPE_HOME)

    def compose(self) -> ComposeResult:
        yield TabStrip("c")
        yield Static("", id="home-identity")
        yield GroupBox(Static(id="home-hero"), id="home-hero-box")
        yield Static("", id="home-microbar")
        yield GroupBox(Static(id="home-resume"), id="home-resume-box")
        yield GroupBox(
            Vertical(
                Static("", id="home-empty"),
                DataTable(id="home-recents", cursor_type="row"),
                id="home-recents-inner",
            ),
            id="home-recents-box",
        )
        yield Static("", id="home-archived")
        yield HintLine("elige una puerta para empezar")
        yield KeyBar(
            [
                ("nav", [("j/k", "elegir"), ("↵", "abrir"), ("r", "retomar")]),
                ("doors", [("c", "consultar"), ("p", "repo"), ("n", "construir"),
                           ("t", "plantilla"), ("i", "importar csv"), ("f", "fábrica")]),
                ("app", [("s", "componentes"), ("ctrl+p", "paleta"), ("?", "ayuda"), ("q", "salir")]),
            ]
        )

    def _map_metrics(self, graph: Graph) -> dict[str, int]:
        total = len(graph.nodes)
        con_acta = sum(1 for n in graph.nodes.values() if n.ficha.fields.get("D", "").strip())
        sin_acta = total - con_acta
        today = date.today().isoformat()
        vencen = sum(
            1 for n in graph.nodes.values()
            if n.ficha.fields.get("due", "").strip() == today
        )
        have, req = graph.coverage()
        pct = int(100 * have / max(1, req))
        return {
            "total": total,
            "con_acta": con_acta,
            "sin_acta": sin_acta,
            "vencen": vencen,
            "coverage": pct,
        }

    def _hero_text(self, map_name: str, metrics: dict[str, int]) -> Text:
        sin_acta = metrics["sin_acta"]
        vencen = metrics["vencen"]
        # calm board: count in INK with no WARN line
        number_style = darkside.INK if sin_acta == 0 and vencen == 0 else darkside.WARN
        lines = Text()
        lines.append(darkside.draw_number(str(sin_acta), number_style))
        lines.append("\n", "")
        lines.append("nodos sin acta\n", darkside.MUT)
        lines.append(escape(map_name) + "\n", darkside.INK)
        if vencen > 0:
            lines.append(f"▲ {vencen} vencen hoy", darkside.WARN)
        return lines

    def _microbar_text(self, metrics: dict[str, int]) -> Text:
        total = max(1, metrics["total"])
        con = metrics["con_acta"]
        sin = metrics["sin_acta"]
        pct = metrics["coverage"]
        return Text.assemble(
            ("  con acta ", darkside.MUT), (f"{con} ", darkside.MUT),
            darkside.microbar(con, total), ("    ", ""),
            ("sin acta ", darkside.WARN), (f"{sin} ", darkside.WARN),
            darkside.microbar(sin, total, fill=darkside.WARN), ("    ", ""),
            (f"cobertura {pct} %", darkside.INK),
        )

    def _sparkline_text(self, store: MapStore) -> Text:
        today = date.today()
        days = [today - timedelta(days=i) for i in range(13, -1, -1)]
        counts: list[int] = []
        for d in days:
            day_count = 0
            for mmd in store.workspace.glob("*.mmd"):
                try:
                    mtime = date.fromtimestamp(mmd.stat().st_mtime)
                    if mtime == d:
                        day_count += 1
                except Exception:
                    pass
            counts.append(day_count)
        max_count = max(counts) if counts else 1
        bars = "▁▂▂▃▃▄▅▆▇█"
        parts: list[tuple[str, str]] = [("actividad 14d  ", darkside.MUT)]
        for c in counts:
            idx = min(len(bars) - 1, int(c / max_count * (len(bars) - 1)))
            # sparkline stays in the dim tier — never INK or ACCENT
            style = darkside.WORDMARK if idx < 4 else darkside.MUT
            parts.append((bars[idx], style))
        return darkside.Text.assemble(*parts)

    def on_mount(self) -> None:
        store: MapStore = self.app.store  # type: ignore[attr-defined]

        # Identity row
        identity = self.query_one("#home-identity", Static)
        glyph, _ = darkside.moon(date.today())
        identity_text = Text()
        identity_text.append(glyph, style=darkside.WORDMARK)
        identity_text.append(" mapper", style=darkside.WORDMARK)
        identity_text.append("   mapas vivos", style=darkside.MUT)
        identity.update(identity_text)

        mmd_files = sorted(store.workspace.glob("*.mmd"))
        hero_map: str | None = None
        hero_metrics: dict[str, int] | None = None

        # Prefer the last session map for the hero; fall back to most recent mmd.
        last_map, _ = store.last_session()
        if last_map:
            try:
                graph = store.load(last_map)
                hero_map = last_map
                hero_metrics = self._map_metrics(graph)
            except Exception:
                pass

        if hero_map is None and mmd_files:
            hero_map = mmd_files[0].stem
            try:
                hero_metrics = self._map_metrics(store.load(hero_map))
            except Exception:
                hero_metrics = {"total": 0, "con_acta": 0, "sin_acta": 0, "vencen": 0, "coverage": 0}

        hero_box = self.query_one("#home-hero-box", GroupBox)
        hero = self.query_one("#home-hero", Static)
        microbar = self.query_one("#home-microbar", Static)
        if hero_map and hero_metrics:
            hero.update(self._hero_text(hero_map, hero_metrics))
            microbar.update(self._microbar_text(hero_metrics))
            # Add the dim-tier sparkline beside the hero text inside the same box.
            spark = self._sparkline_text(store)
            hero.update(Text.assemble(
                self._hero_text(hero_map, hero_metrics), ("\n", ""), spark,
            ))
            hero_box.display = True
            microbar.display = True
        else:
            hero_box.display = False
            microbar.display = False

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

        archived = self.query_one("#home-archived", Static)
        if not mmd_files:
            table.display = False
            self.query_one("#home-empty", Static).update(self._empty_text())
            self.query_one("#home-empty", Static).display = True
            archived.display = False
            return

        table.display = True
        self.query_one("#home-empty", Static).display = False
        archived_count = 0  # placeholder until archive feature lands
        if archived_count:
            archived.update(
                Text.assemble((f"  ({archived_count} mapa archivado — u restaura)", darkside.MUT))
            )
            archived.display = True
        else:
            archived.display = False

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

    def action_settings(self) -> None:
        self.app.push_screen(SettingsScreen())

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
        """Refresh the home surface when returning."""
        self.on_mount()


class _ImportPreviewScreen(Screen):
    """Preview a CSV import before saving it as a named map."""

    KEY_SCOPE = SCOPE_IMPORT
    BINDINGS = screen_bindings(SCOPE_IMPORT)

    def __init__(self, preview_graph: Graph, source_path: Path) -> None:
        super().__init__()
        self.preview_graph = preview_graph
        self.source_path = source_path

    def compose(self) -> ComposeResult:
        yield TabStrip("i", crumb=["import", self.source_path.name])
        yield Static("", id="import-preview-canvas")
        yield HintLine("s guarda · esc volver")
        yield KeyBar(groups_for_keybar(keybar_groups(self.KEY_SCOPE)))

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

    KEY_SCOPE = SCOPE_PLUG
    BINDINGS = screen_bindings(SCOPE_PLUG)

    def compose(self) -> ComposeResult:
        yield TabStrip("p", crumb=["conectar repo"])
        yield Vertical(
            Label("conectar repositorio", id="repo-title"),
            Input(placeholder="owner/name o URL de github", id="repo-input"),
            id="repo-dialog",
        )
        yield HintLine("ingresa owner/name, URL o ruta local y presiona ↵", "↵")
        yield KeyBar(groups_for_keybar(keybar_groups(self.KEY_SCOPE)))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "repo-input":
            raw = event.value.strip()
            repo = self._normalize_repo(raw)
            if repo:
                self.app.push_screen(RepoScreen(repo))

    @staticmethod
    def _normalize_repo(value: str) -> str:
        """Accept owner/name, full GitHub URL, or local path."""
        value = value.strip().rstrip("/")
        if not value:
            return ""
        # Strip scheme and trailing .git from GitHub URLs.
        lowered = value.lower()
        if lowered.startswith("https://github.com/") or lowered.startswith("http://github.com/"):
            path = value.split("github.com/", 1)[1]
            path = path.removesuffix(".git")
            return path  # owner/name
        if ":" in value and "git@github.com" in lowered:
            path = value.split(":", 1)[1]
            path = path.removesuffix(".git")
            return path
        return value

    def action_home(self) -> None:
        self.app.pop_screen()

    def action_palette(self) -> None:
        self.app.action_palette()

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())


class RepoScreen(Screen):
    """A GitHub repo rendered as a two-pane branch dashboard (variant C)."""

    KEY_SCOPE = SCOPE_REPO
    BINDINGS = screen_bindings(SCOPE_REPO)

    progress_current: reactive[int] = reactive(0)
    progress_total: reactive[int] = reactive(1)
    progress_stage: reactive[str] = reactive("")
    loading: reactive[bool] = reactive(True)

    def __init__(self, repo: str):
        super().__init__()
        self.repo = repo
        self.graph = Graph()
        self.nav = NavigationModel(self.graph)
        self.selected_index = 0

    def compose(self) -> ComposeResult:
        yield TabStrip("p", crumb=[self.repo])
        with Horizontal(id="repo-dashboard"):
            with Vertical(id="repo-sidebar"):
                yield Static(self.repo, id="repo-name")
                yield Static(self._stages_text(), id="repo-stages")
                yield Static(self._progress_text(), id="repo-progress")
                yield Static(
                    "j/k navega tabla\n↵ detalle\nq inicio\n? ayuda",
                    id="repo-sidebar-hints",
                )
            yield Static(self._render_table(), id="repo-table", expand=True)
        yield KeyBar(
            [
                ("nav", [("j/k", "sig/ant"), ("↵", "detalle")]),
                ("app", [("ctrl+p", "paleta"), ("?", "ayuda"), ("q", "inicio")]),
            ]
        )

    def _stages_text(self) -> Text:
        stages = ["iniciando", "leyendo ramas", "calculando métricas", "listo"]
        if self.loading:
            current = min(2, int(3 * self.progress_current / max(1, self.progress_total)))
        else:
            current = 3
        text = Text()
        for i, stage in enumerate(stages):
            if i > 0:
                text.append("\n", "")
            if i < current:
                text.append(f"● {stage}", darkside.INK)
            elif i == current:
                marker = "◐" if self.loading else "●"
                text.append(f"{marker} {stage}", darkside.WARN if self.loading else darkside.INK)
            else:
                text.append(f"○ {stage}", darkside.WORDMARK)
        return text

    def _progress_text(self) -> Text:
        pct = min(100, int(100 * self.progress_current / max(1, self.progress_total)))
        width = 22
        filled = int(width * pct / 100)
        return Text.assemble(
            ("▰" * filled, darkside.INK),
            ("▱" * (width - filled), darkside.WORDMARK),
            (f" {pct}%", darkside.MUT),
        )

    def watch_progress_current(self) -> None:
        self._refresh_sidebar()

    def watch_progress_total(self) -> None:
        self._refresh_sidebar()

    def watch_loading(self) -> None:
        self._refresh_sidebar()

    def _refresh_sidebar(self) -> None:
        try:
            stages = self.query_one("#repo-stages", Static)
            progress = self.query_one("#repo-progress", Static)
        except Exception:
            return
        stages.update(self._stages_text())
        progress.update(self._progress_text())

    def _branch_kind(self, name: str) -> str:
        lowered = name.lower()
        if lowered in {"main", "master"} or lowered.startswith("release/"):
            return "release"
        if lowered.startswith("hotfix/"):
            return "hotfix"
        return "branch"

    def _state_indicator(self, state: str) -> Text:
        if state == "blocked":
            return Text.assemble(("● ", darkside.ALERT), ("bloqueado", darkside.ALERT))
        if state == "risk":
            return Text.assemble(("● ", darkside.WARN), ("riesgo", darkside.WARN))
        return Text.assemble(("● ", darkside.INK), ("ok", darkside.MUT))

    def _source_kind(self) -> str:
        repo_path = Path(self.repo).expanduser()
        if repo_path.is_dir() and (repo_path / ".git").is_dir():
            return "local"
        if "://" in self.repo or self.repo.count("/") == 1:
            return "github"
        return "local"

    def _source_badge(self) -> Text:
        kind = self._source_kind()
        return darkside.Text.assemble(
            (f" {kind} ", f"{darkside.INK} on {darkside.STEP}"),
        )

    def _age_days(self, date_str: str) -> int:
        if not date_str:
            return -1
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d").date()
            return (date.today() - dt).days
        except ValueError:
            return -1

    def _time_row(self, name: str, age_days: int, glyph: str, style: str, note: str) -> Text:
        return darkside.time_row(name, age_days, glyph, style, note)

    def _render_table(self) -> Text:
        if not self.graph.nodes:
            return Text("(no hay ramas cargadas)", style=darkside.MUT)

        root_id = self.graph.root_id or ""
        items: list[tuple[str, Node]] = []
        for nid, node in self.graph.nodes.items():
            if nid == root_id:
                continue
            items.append((nid, node))

        branches = [(nid, n) for nid, n in items if n.ficha.fields.get("kind") != "release"]
        releases = [(nid, n) for nid, n in items if n.ficha.fields.get("kind") == "release"]

        lines = Text()
        # Source honesty badge + counts
        lines.append("  ")
        lines.append_text(self._source_badge())
        lines.append(f"   {len(branches)} ramas · {len(releases)} releases\n", darkside.MUT)
        lines.append("\n", "")

        def render_group(title: str, nodes: list[tuple[str, Node]], glyph: str,
                         style: str) -> None:
            if not nodes:
                return
            lines.append(f"  {title}\n", darkside.MUT)
            for idx, (nid, node) in enumerate(nodes):
                name = node.ficha.title or nid
                if name.startswith("release:"):
                    name = name[len("release:"):]
                age = self._age_days(node.ficha.fields.get("date", ""))
                note_parts: list[str] = []
                if age >= 0:
                    if age == 0:
                        note_parts.append("hoy")
                    elif age == 1:
                        note_parts.append("ayer")
                    elif age < 7:
                        note_parts.append(f"hace {age} d")
                    elif age < 30:
                        note_parts.append(f"hace {age // 7} sem")
                    else:
                        note_parts.append(f"hace {age // 30} mes")
                meta = node.ficha.meta or ""
                if meta and meta != "release":
                    note_parts.append(meta)
                if node.ficha.notes and node.ficha.notes != "CI: unknown":
                    note_parts.append(node.ficha.notes)
                note = " · ".join(note_parts) or "sin datos"
                row = self._time_row(name, max(0, age), glyph, style, note)
                # selection marker
                marker = "▶ " if idx == self.selected_index else "  "
                lines.append(marker, darkside.ACCENT if idx == self.selected_index else "")
                lines.append_text(row)
                lines.append("\n", "")
            lines.append("\n", "")

        order = {"release": 0, "hotfix": 1, "branch": 2}
        branches.sort(key=lambda item: (order.get(self._branch_kind(item[0]), 2), item[0]))
        render_group("ramas", branches, "●", darkside.INK)
        render_group("releases", releases, "◆", darkside.INK)

        lines.append("  ")
        lines.append("●", darkside.INK)
        lines.append(" commit   ", darkside.MUT)
        lines.append("◆", darkside.INK)
        lines.append(" release   ", darkside.MUT)
        lines.append("╎", darkside.WORDMARK)
        lines.append(" hoy   (30 días)\n", darkside.MUT)
        return lines

    def _refresh_table(self) -> None:
        table = self.query_one("#repo-table", Static)
        table.update(self._render_table())

    @work(thread=True)
    def fetch_graph(self) -> Graph:
        def on_progress(current: int, total: int, stage: str) -> None:
            try:
                self.app.call_from_thread(self._update_progress, current, total, stage)
            except Exception:
                pass
        return GitHubConnector(self.repo).fetch(progress=on_progress)

    def _update_progress(self, current: int, total: int, stage: str) -> None:
        try:
            self.progress_current = current
            self.progress_total = total
            self.progress_stage = stage
        except Exception:
            pass

    async def on_mount(self) -> None:
        self.loading = True
        self._refresh_sidebar()
        table = self.query_one("#repo-table", Static)
        table.update(Text("  conectando… esto puede tardar unos segundos", style=darkside.MUT))
        try:
            worker = self.fetch_graph()
            self.graph = await worker.wait()
            self.notify(f"conectado: {len(self.graph.nodes)} nodos")
        except GitHubError as exc:
            self.notify(str(exc), severity="error")
            self.graph = Graph()
        except Exception as exc:
            self.notify(f"error inesperado: {exc}", severity="error")
            self.graph = Graph()
        self.loading = False
        self.nav = NavigationModel(self.graph)
        self.selected_index = 0
        self._refresh_sidebar()
        self._refresh_table()
        pulse_cursor(table)

    def action_next_sibling(self) -> None:
        root_id = self.graph.root_id or ""
        count = sum(1 for n in self.graph.nodes if n != root_id)
        if count == 0:
            return
        self.selected_index = (self.selected_index + 1) % count
        self._refresh_table()

    def action_prev_sibling(self) -> None:
        root_id = self.graph.root_id or ""
        count = sum(1 for n in self.graph.nodes if n != root_id)
        if count == 0:
            return
        self.selected_index = (self.selected_index - 1) % count
        self._refresh_table()

    def action_home(self) -> None:
        self.app.pop_screen()

    def action_palette(self) -> None:
        self.app.action_palette()

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())


class MapScreen(Screen):
    """A map rendered as a layered tree."""

    KEY_SCOPE = SCOPE_MAP
    BINDINGS = screen_bindings(SCOPE_MAP)
    # The inspector's fields mount after this screen does, and Textual would
    # auto-focus the first of them — which silently disables every single-letter
    # map binding, because a focused Input consumes printable keys.  The map, not
    # a text field, owns the keyboard on arrival.
    AUTO_FOCUS = None

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
        yield Static("", id="map-minimap")
        # Variant A «taller»: rail | canvas | inspector.  The inspector is the ONE
        # ficha surface — it replaces both the old `#map-ficha` GroupBox and the
        # LayeredRenderer's own ficha strip, which rendered the same card twice.
        yield Horizontal(
            Static("", id="map-canvas"),
            FichaInspector(id="map-inspector"),
            id="map-body",
        )
        yield Input(placeholder="/buscar", id="search-input")
        yield Static("", id="map-pagination")
        yield Static("", id="map-toast")
        yield HintLine("navega con j/k/h/l · ↵ ficha · / buscar")
        # The keybar reads the same seat the bindings are generated from, so it
        # cannot advertise a key the screen does not bind (US-N03).
        yield KeyBar(groups_for_keybar(keybar_groups(self.KEY_SCOPE)))

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
        # Keep focus off the inspector's fields on arrival: a focused Input eats
        # every single-letter key, so the map's own navigation would be dead until
        # the operator blurred it by hand.
        self.set_focus(None)

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

    def _branch_coverage_glyph(self, branch_root: str) -> tuple[str, str]:
        """Return (glyph, style) for a top-level branch's coverage minimap."""
        nodes = [branch_root]
        stack = [branch_root]
        while stack:
            parent = stack.pop()
            for cid in self.graph.children_of(parent):
                nodes.append(cid)
                stack.append(cid)
        total = len(nodes)
        con_acta = sum(1 for nid in nodes if self.graph.nodes[nid].ficha.fields.get("D", "").strip())
        if total == 0:
            return ("╱", darkside.WORDMARK)
        pct = con_acta / total
        if pct >= 1.0:
            return ("█", darkside.INK)
        if pct >= 0.5:
            return ("▒", darkside.MUT)
        return ("░", darkside.WARN)

    def _minimap_text(self) -> Text:
        if self.graph.root_id is None:
            return Text("")
        parts: list[tuple[str, str]] = [("  cobertura   ", darkside.MUT)]
        for cid in self.graph.children_of(self.graph.root_id):
            glyph, style = self._branch_coverage_glyph(cid)
            name = self.graph.nodes[cid].ficha.title or cid
            parts.append((f"{name} ", darkside.MUT))
            parts.append((glyph, style))
            parts.append(("   ", ""))
        parts.extend([
            ("█", darkside.INK), (" completa ", darkside.MUT),
            ("▒", darkside.MUT), (" media ", darkside.MUT),
            ("░", darkside.WARN), (" baja ", darkside.MUT),
            ("╱", darkside.WORDMARK), (" sin datos", darkside.MUT),
        ])
        return darkside.Text.assemble(*parts)

    def _pagination_text(self) -> Text:
        total = len(self.graph.nodes)
        page = 1
        per_page = max(1, total)
        # For now the tree is not paginated; this reserves the affordance.
        return darkside.Text.assemble(
            (" ", ""),
            darkside.step_meter(min(page, per_page), per_page),
            (f"   {page}/{per_page}  ", darkside.MUT),
        )

    def _event_toast(self, label: str, detail: str = "") -> None:
        """Bottom strip for events only — status words, not glyphs."""
        toast = self.query_one("#map-toast", Static)
        if detail:
            text = darkside.Text.assemble(
                (f" {label}", f"bold {darkside.INK}"),
                (f"   {detail}", darkside.MUT),
            )
        else:
            text = darkside.Text.assemble((f" {label}", f"bold {darkside.INK}"))
        toast.styles.background = darkside.PANEL
        toast.update(text)

    def refresh_canvas(self) -> None:
        canvas = self.query_one("#map-canvas", Static)
        renderer = self._current_renderer()
        size = self.size or self.app.size
        # The canvas no longer owns the full width: the inspector takes a fixed
        # column beside it, so render to what is actually left.
        w = max(20, size.width - INSPECTOR_WIDTH)
        h = max(5, size.height - 8)
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

        self.query_one("#map-inspector", FichaInspector).show(node, self.graph)
        self.query_one("#map-minimap", Static).update(self._minimap_text())
        self.query_one("#map-pagination", Static).update(self._pagination_text())

    def on_ficha_inspector_field_committed(
        self, event: FichaInspector.FieldCommitted
    ) -> None:
        """Persist an inspector edit.

        The widget cannot write: `widgets -> store` is banned, so it reports what
        the operator did and this screen — which owns the graph and the store —
        decides what that costs.
        """
        event.stop()
        node = self.graph.nodes.get(event.node_id)
        if node is None or self.store is None:
            return
        current = self._ficha_value(node.ficha, event.field)
        if current == event.value:
            return
        # Snapshot BEFORE mutating, so `u` reverts this edit rather than an
        # unrelated earlier structural change.
        self._push_snapshot()
        if event.field == "title":
            node.ficha.title = event.value
        elif event.field == "notes":
            node.ficha.notes = event.value
        elif event.field == "state":
            node.ficha.state = event.value
        else:
            node.ficha.fields[event.field] = event.value
        self.store.save(self.map_id, self.graph)
        self.base_graph = self.graph
        self.refresh_canvas()
        self._event_toast("guardado", node.ficha.title or node.id)

    @staticmethod
    def _ficha_value(ficha: Ficha, field: str) -> str:
        if field == "title":
            return ficha.title
        if field == "notes":
            return ficha.notes
        if field == "state":
            return ficha.state
        return ficha.fields.get(field, "")

    def on_field_input_left(self, event) -> None:
        """`escape` inside a field returns focus to the map, keeping the value."""
        event.stop()
        self.set_focus(None)
        self.query_one(HintLine).set_hint("navega con j/k/h/l · ↵ ficha · / buscar")

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
        self._event_toast("deshacer", "estado restaurado")

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
            self._event_toast("exportado", str(path))
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
            self._event_toast("archivado", node.ficha.title or node.id)

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
        self.app.action_help()


class MapperApp(App):
    """Main application entry point."""

    # Textual's own attribute is ENABLE_COMMAND_PALETTE.  This app previously set
    # COMMAND_PALETTE_ENABLE, a name Textual never reads, so the built-in palette
    # silently owned ctrl+p and mapper's own palette was unreachable by keyboard.
    # Caught only once a test pressed the real key instead of calling the action.
    ENABLE_COMMAND_PALETTE = False

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

    MapScreen, PlugRepoScreen { layout: vertical; }
    RepoScreen { layout: vertical; }
    #repo-dashboard { height: 1fr; }
    #repo-sidebar { width: 30; background: #121212; padding: 1 1; }
    #repo-name { text-style: bold; color: #f5f5f5; margin-bottom: 1; }
    #repo-stages { color: #737373; margin-bottom: 1; }
    #repo-progress { color: #737373; margin-bottom: 1; }
    #repo-sidebar-hints { color: #737373; }
    #repo-table { height: 1fr; background: #000000; padding: 0 1; }
    /* Variant A «taller»: canvas + inspector side by side.  Depth comes from the
       background step, never from a border — borders are reserved for modals. */
    #map-body { height: 1fr; }
    #map-canvas { width: 1fr; height: 100%; }
    #map-inspector {
        width: 36;
        height: 100%;
        background: #121212;
        padding: 0 1;
        overflow-y: auto;
    }
    #map-inspector .insp-label { color: #737373; }
    #map-inspector Input {
        border: none;
        background: #262626;
        color: #f5f5f5;
        height: 1;
        padding: 0 1;
    }
    #map-inspector Input:focus { background: #1783ff; color: #000000; }
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

    KEY_SCOPE = SCOPE_APP
    # The app's own bindings come from the seat too — this was the one list that
    # escaped it.  Its hand-written `q -> quit` was bound app-wide, so on the plug
    # and import-preview screens (neither of which declares `q`) pressing `q` quit
    # the application outright, discarding an unsaved import, while palette and
    # help advertised no such key.  `q` now quits only in home scope, where it is
    # advertised.
    BINDINGS = screen_bindings(SCOPE_APP)

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
        scope = getattr(target_screen, "KEY_SCOPE", SCOPE_APP)

        def on_command(action: str | None) -> None:
            if not action:
                return
            # `action` is an action_* method stem straight from the keymap seat,
            # never a translated label — that is what makes the entry dispatch.
            method_name = f"action_{action}"
            if hasattr(target_screen, method_name):
                getattr(target_screen, method_name)()
            elif hasattr(self, method_name):
                getattr(self, method_name)()

        self.push_screen(CommandPalette(scope), callback=on_command)

    def action_help(self) -> None:
        self.push_screen(HelpScreen(getattr(self.screen, "KEY_SCOPE", SCOPE_APP)))

    def action_quit(self) -> None:
        self.exit()


def main() -> None:
    import sys

    # Windows terminals default to cp1252 and crash on box-drawing glyphs.
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / "maps"
    app = MapperApp(workspace)
    app.run()


if __name__ == "__main__":
    main()
