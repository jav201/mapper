"""Textual TUI app for mapper — darkside UI."""
from __future__ import annotations

import json
import re
from dataclasses import replace
from datetime import date, datetime, timedelta
from pathlib import Path

from rich.markup import escape
from rich.text import Text
from textual import events, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.geometry import Region
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
from .model import Attachment, Document, Edge, Ficha, Graph, Node
from .motion import pulse_cursor
from .osopen import OK as OSOPEN_OK, open_external
from .screens import CommandPalette, CoverageScreen, FactoryScreen, HelpScreen, SettingsScreen
from .store import MapStore, TEMPLATES
from .views.layered import (
    OVERFLOW_TOKEN,
    LayeredRenderer,
    header_rows,
    pan_extent,
    painted_ids,
)
from .views.state import ViewState
from .views.outline import OutlineRenderer
from .views.radial import RadialRenderer
from .widgets.chrome import GroupBox, HintLine, KeyBar, TabStrip
from .widgets.inspector import INSPECTOR_WIDTH, FichaInspector
from .widgets.rail import RAIL_WIDTH, OutlineRail


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

        # The sala loads every map in the workspace, so one refusable map must
        # cost a notice rather than the screen.  Scoped to the sink: any
        # exception from a load, not only the types this batch knows about.
        broken: list[str] = []

        def load_or_notice(name: str) -> Graph | None:
            try:
                graph = store.load(name)
            except Exception as exc:
                if name not in broken:
                    broken.append(name)
                    self.notify(
                        f"no se pudo cargar {darkside.plain(name)}: {darkside.plain(str(exc))}",
                        severity="error",
                        markup=False,
                    )
                return None
            if graph.load_warnings:
                self.notify(
                    f"{darkside.plain(name)}: {darkside.plain('; '.join(graph.load_warnings))}",
                    severity="warning",
                    markup=False,
                )
            return graph

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
            graph = load_or_notice(last_map)
            if graph is not None:
                hero_map = last_map
                hero_metrics = self._map_metrics(graph)

        if hero_map is None and mmd_files:
            hero_map = mmd_files[0].stem
            graph = load_or_notice(hero_map)
            if graph is not None:
                hero_metrics = self._map_metrics(graph)
            else:
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
            graph = load_or_notice(map_id)
            node = graph.nodes.get(node_id) if graph is not None else None
            node_name = node.ficha.title if node else node_id
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
            graph = load_or_notice(map_name)
            if graph is not None:
                kind = "legacy" if graph.schema else "concept"
                nodos = str(len(graph.nodes))
                docs = str(len(graph.documents))
            else:
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
                self.notify(f"no se pudo crear el mapa: {e}", severity="error", markup=False)

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
                self.notify(f"no se pudo crear el mapa: {e}", severity="error", markup=False)

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
                self.notify(f"archivo no encontrado: {path}", severity="error", markup=False)
                return
            try:
                preview = preview_csv(path)
            except Exception as e:
                self.notify(f"no se pudo leer CSV: {e}", severity="error", markup=False)
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
        # Same sink class as MapScreen.refresh_canvas, and a live second door:
        # a CSV whose `parent` column is circular builds a cyclic graph without
        # ever passing through `mermaid.parse`, so the parser's refusal cannot
        # reach it.  Measured — see increment-001 §1.
        try:
            text = renderer.render(
                self.preview_graph,
                ViewState(
                    selected_id=self.preview_graph.root_id,
                    w=max(20, size.width),
                    h=max(5, size.height - 10),
                ),
            )
        except Exception as exc:
            text = darkside.Text.assemble(
                (" no se pudo dibujar la vista previa\n\n", f"bold {darkside.INK}"),
                (f" {darkside.plain(str(exc))}", darkside.MUT),
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
                self.notify(f"no se pudo guardar: {e}", severity="error", markup=False)

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
                text.append(f"{marker} {stage}", darkside.PULSE if self.loading else darkside.INK)
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
            self.notify(f"conectado: {len(self.graph.nodes)} nodos", markup=False)
        except GitHubError as exc:
            self.notify(str(exc), severity="error", markup=False)
            self.graph = Graph()
        except Exception as exc:
            self.notify(f"error inesperado: {exc}", severity="error", markup=False)
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
        self.rail_hidden = False
        self.inspector_hidden = False
        self._regions_pinned = False
        # US-N06.  The screen owns fold and pan; the rail and the renderer are
        # readers.  `folded` lived on `OutlineRail` until Inc-3, where a region
        # the layout auto-hides below 118 columns owned state the canvas needed.
        self.folded: frozenset[str] = frozenset()
        self.pan_x = 0
        self.pan_y = 0
        # The canvas region `_declare_after_layout` last painted a numeral for.
        # `None` means "never", which is why the first pass always re-schedules.
        self._declared_for: Region | None = None

    def compose(self) -> ComposeResult:
        crumb_prefix = self.source_crumb or [self.map_id]
        yield TabStrip("c", crumb=crumb_prefix + [""])
        yield Static("", id="map-minimap")
        # Variant A «taller»: rail | canvas | inspector.  The inspector is the ONE
        # ficha surface — it replaces both the old `#map-ficha` GroupBox and the
        # LayeredRenderer's own ficha strip, which rendered the same card twice.
        yield Horizontal(
            OutlineRail(id="map-rail"),
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

    def _notice_load_warnings(self, graph: Graph) -> None:
        """Tell the operator which node and which field were unreadable.

        LLR-R03.4.  The map still loaded (LLR-R03.5), so this is a notice and not
        an error path; `darkside.plain` because the node id and the key both come
        out of a file.
        """
        if not graph.load_warnings:
            return
        self.notify(
            darkside.plain("; ".join(graph.load_warnings)),
            severity="warning",
            markup=False,
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
                self._notice_load_warnings(self.base_graph)
            except Exception as e:
                self.notify(
                    f"error cargando mapa: {darkside.plain(str(e))}",
                    severity="error",
                    markup=False,
                )
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

        self._apply_region_visibility()
        self.refresh_canvas()
        # Keep focus off the side regions on arrival: a focused Input eats every
        # single-letter key, so the map's own navigation would be dead until the
        # operator blurred it by hand.  Scheduled after the refresh because the
        # rail and the inspector's fields are focusable and mount after this runs.
        self.call_after_refresh(self._park_focus)
        # `B-56` AND `B-60`, both CLOSED rather than carried.  The carry they
        # replace was recorded on measurements that were wrong twice over: the
        # declaration was ABSENT at ordinary sizes rather than merely stale, and
        # ordinary navigation did not clear it.  See `_declare_after_layout`,
        # which repaints the two surfaces that DECLARE -- the canvas and the
        # strip -- and nothing that focuses, so `LLR-CNV.3.1` and `B-50` are
        # untouched.
        self.call_after_refresh(self._declare_after_layout)

    # -- region layout (LLR-N06.6) -----------------------------------------
    # Below this width the canvas cannot show a card's coverage row without
    # clipping it mid-field, and a clipped field is indistinguishable from a
    # present one — the canvas would silently misreport coverage.  Measured by
    # the UX lens: a 5-field schema needs card_w >= 15, so n*18-3 <= w-2.
    MIN_CANVAS_WIDTH = 58

    def _chrome_width(self) -> int:
        """Columns taken by the rail and inspector at the current setting."""
        return (0 if self.rail_hidden else RAIL_WIDTH) + (
            0 if self.inspector_hidden else INSPECTOR_WIDTH
        )

    def _apply_region_visibility(self) -> None:
        """Collapse the side regions when the terminal cannot afford them.

        Auto-collapse is width-driven, but an explicit toggle wins: once the
        operator has hidden or shown a region by hand, we stop second-guessing.
        """
        size = self.size or self.app.size
        if not self._regions_pinned:
            available = size.width - RAIL_WIDTH - INSPECTOR_WIDTH
            if available < self.MIN_CANVAS_WIDTH:
                self.rail_hidden = True
            if size.width - INSPECTOR_WIDTH < self.MIN_CANVAS_WIDTH:
                self.inspector_hidden = True
        self.query_one("#map-rail", OutlineRail).display = not self.rail_hidden
        self.query_one("#map-inspector", FichaInspector).display = not self.inspector_hidden

    def action_toggle_rail(self) -> None:
        self._regions_pinned = True
        self.rail_hidden = not self.rail_hidden
        self._apply_region_visibility()
        self.refresh_canvas()

    def action_toggle_inspector(self) -> None:
        self._regions_pinned = True
        self.inspector_hidden = not self.inspector_hidden
        self._apply_region_visibility()
        self.refresh_canvas()

    def action_focus_rail(self) -> None:
        """Move keyboard focus to the rail, and say so on the hint line."""
        rail = self.query_one("#map-rail", OutlineRail)
        if self.rail_hidden:
            self.action_toggle_rail()
        rail.focus()
        self.query_one(HintLine).set_hint(
            "rail · ↵ plegar rama · esc volver al mapa", "esc"
        )
        self.refresh_canvas()

    def action_collapse_branch(self) -> None:
        """Fold or unfold the branch under the cursor — LLR-N06.2.1, LLR-N06.2.2.

        The rail used to own this and mutate its own `collapsed` set, so the
        canvas never learned about a fold at all.
        """
        nid = self.nav.cursor
        if nid is None:
            return
        if nid not in self.folded and not self.graph.children_of(nid):
            # LLR-N06.2.2.  The natural implementation paints a pill reading
            # `+0`, which declares a hidden count of zero and is worse than
            # nothing; the product already answers "nothing to do" out loud
            # elsewhere (`next_gap` toasts `cobertura completa`).
            self.notify(
                "este nodo no tiene descendientes",
                title="nada que plegar",
                severity="information",
                markup=False,
            )
            return
        self.folded = (
            self.folded - {nid} if nid in self.folded else self.folded | {nid}
        )
        self.refresh_canvas()

    # -- pan (HLR-N06.1) ---------------------------------------------------
    # One press moves the window by this many cells.  A single cell makes the
    # chord feel dead on a map that overflows by 60 columns; a whole viewport
    # loses the operator's place.  Vertical is smaller because a card row is
    # 4-5 cells tall and a page-sized jump skips whole levels.
    PAN_STEP_X = 8
    PAN_STEP_Y = 4

    @staticmethod
    def _clamp_pan(offset: int, extent: int, span: int) -> int:
        """LLR-N06.1.2 — the legal range is `[0, max(0, E - W)]`, always.

        The `E < W` case is why the outer `max(0, ...)` is there rather than a
        bare `extent - span`: a map smaller than the canvas has a legal pan
        range of exactly one position, and a negative upper bound would let
        `min` return it and slide the map off screen on a small graph.
        """
        return max(0, min(offset, max(0, extent - span)))

    # `HEADER_ROWS = 2` USED TO LIVE HERE, AND IT WAS FALSE.  The note argued
    # the header's length is always `avail + 5` or `2 * avail - 43`, hence
    # always between `avail` and `2 * avail`, hence exactly two physical rows.
    # Both of its paddings are CLAMPED AT 0, so below `avail = 48` neither
    # formula applies: the line is a fixed core plus the `▽ N fuera de vista`
    # declaration, and on `legacy` that is 55 cells at EVERY narrow width.
    # Measured, it wraps to THREE physical rows at canvas width 21..34 and FOUR
    # at 20 -- and `_canvas_size` floors `w` at 20, so the band is one resize
    # away.  Charging 2 there left the screen believing one or two more body
    # rows survived than the region could show, and `painted_ids` declared nodes
    # that leave no trace: at terminal (28,17) it declared `erp` on a frame with
    # zero card marks while the strip read 7 against a truth of 8.  That is
    # `CR-F1`'s defect verbatim, one width band over (`B-61`).
    #
    # The number is now MEASURED per call by `layered.header_rows`, off the same
    # `_header_line` helper `render` paints from, so there is no second copy of
    # the header's shape to drift.

    def _header_rows(self, wrap_w: int) -> int:
        """The header's measured physical height for the frame about to be sized.

        WRAPPED AT THE WIDGET'S CONTENT WIDTH, WHICH IS NOT `w - 2`.  An earlier
        revision wrapped at `w - 2` and justified it as "the canvas widget's
        content width".  Measured across a 943-configuration terminal sweep on
        `legacy`, it is not: `#map-canvas` is `width: 1fr; height: 100%` with no
        padding and no border, so its content width equals its REGION width, and
        that region is `_canvas_width()` at 724 of the 943 and `_canvas_width()
        - 2` at the other 219.  At terminal (28,17) the content width is 28, not
        26, and the frame shows three rows because Rich WORD-WRAPS a 55-cell
        line at 28 -- not because of a two-column inset.  The old reading reached
        the right row count through the wrong mechanism, which is why it was
        compensating rather than causing.  So the measured width is passed in.

        `wrap_w` comes from the same `content_size` read `_canvas_size` uses to
        price the body, so the guard and the subtraction cannot disagree about
        which frame they are describing.
        """
        return header_rows(self.graph, self._canvas_width(), wrap_w)

    def _canvas_width(self) -> int:
        """Columns the canvas renderer is given.  Floors at 20 (`B-61`'s band)."""
        size = self.size or self.app.size
        # The canvas no longer owns the full width: the inspector takes a fixed
        # column beside it, so render to what is actually left.
        return max(20, size.width - self._chrome_width())

    def _canvas_size(self) -> tuple[int, int]:
        """The `(w, h)` the canvas renderer is given, in ONE place.

        `refresh_canvas`, the pan clamp and the overflow helper must all price
        the same frame; three inline copies of this arithmetic is how they start
        disagreeing about which nodes were on screen.

        `h` COMES FROM THE WIDGET'S REGION, not from `size.height - 8`, and that
        is a defect fix US-N06 forced into the open.  Measured on `legacy`: at a
        50x20 terminal the shipped arithmetic asked for 12 rows into a region
        that holds 8, so four nodes were drawn into a void -- hidden, with
        nothing declaring them, which is the story's promise inverted.  Across a
        nine-size sweep the shipped `h` made the declared painted set disagree
        with the composited frame at five sizes; the region-derived `h` agrees at
        all nine.

        THE THREE BRANCHES ARE THREE DIFFERENT FRAMES, and an earlier revision
        collapsed the middle one into the last.  `region.height == 0` is the
        genuinely pre-layout case, and only there is `size.height - 8` an honest
        guess.  A region that is REAL but no taller than the header is not
        pre-layout at all -- it is a short terminal, and the header has eaten the
        whole region.  Returning `region.height` there left `row_limit = h - 1`
        believing canvas row 0 survived, so `painted_ids` declared a node painted
        that leaves no trace: measured on `legacy` at (31,18), (50,14) and
        (100,10), all 8 nodes hidden and the indicator declaring 7.  Returning 1
        makes `row_limit` 0, which is the truth -- no body row is paintable.

        BOTH USES OF THE HEADER'S HEIGHT TAKE THE MEASURED VALUE, and they have
        to move together: the guard asks "has the header eaten the whole
        region", the subtraction asks "how many body rows are left".  Charging a
        constant 2 in either place is `B-61`.  `render` emits `1 + (h - 1)`
        LOGICAL lines and the widget spends `rows` PHYSICAL rows on the first of
        them, so the frame shows `region.height - rows` body rows and the
        renderer must be told `h - 1 = region.height - rows`.
        """
        w = self._canvas_width()
        canvas = self.query_one("#map-canvas", Static)
        region = canvas.region
        if not region.height:                    # genuinely pre-layout
            size = self.size or self.app.size
            return w, max(5, size.height - 8)
        # The header is priced AFTER the region is known to be real, because the
        # width it wraps at is that region's content width -- there is no honest
        # value for it above this line.
        rows = self._header_rows(canvas.content_size.width or region.width)
        if region.height <= rows:                # real, but the header fills it
            return w, 1                          # row_limit == 0 -> nothing painted
        return w, region.height - (rows - 1)

    def _reclamp_pan(self, w: int, h: int) -> None:
        """Pull both offsets back into range for the frame about to be drawn.

        A resize or a fold shrinks the extent under a pan that was legal a
        moment ago, and `LLR-N06.1.2` says the system shall not ACCEPT an offset
        outside the range -- not merely that it shall not produce one.
        """
        (extent_x, span_x), (extent_y, span_y) = pan_extent(
            self.graph, self._view_state(w, h)
        )
        self.pan_x = self._clamp_pan(self.pan_x, extent_x, span_x)
        self.pan_y = self._clamp_pan(self.pan_y, extent_y, span_y)

    def _pan(self, dx: int, dy: int) -> None:
        w, h = self._canvas_size()
        try:
            (extent_x, span_x), (extent_y, span_y) = pan_extent(
                self.graph, self._view_state(w, h)
            )
        except Exception:
            # Same argument as `refresh_canvas`'s guard, and the same sink-scoped
            # shape: this runs inside the message pump, `_tree_layout` raises by
            # design on a graph that is not a tree, and an escape here kills the
            # app with the operator's unsaved edits in it.  Measured on a cyclic
            # graph before this guard: one `L` press and `app.is_running` went
            # False.  A frame that cannot be laid out cannot be panned, so the
            # answer is the one the edge already has a declaration for.
            self.query_one(HintLine).set_hint("borde del territorio")
            return
        nx = self._clamp_pan(self.pan_x + dx * self.PAN_STEP_X, extent_x, span_x)
        ny = self._clamp_pan(self.pan_y + dy * self.PAN_STEP_Y, extent_y, span_y)
        if (nx, ny) == (self.pan_x, self.pan_y):
            # HLR-N06.1's unwanted-behaviour clause.  A silent no-op at the edge
            # is indistinguishable from a keyboard that stopped working, and
            # blank space past the content is indistinguishable from "the map
            # has nothing there" -- the exact confusion US-N06 exists to remove.
            self.query_one(HintLine).set_hint("borde del territorio")
            return
        self.pan_x, self.pan_y = nx, ny
        # CLEARED ON SUCCESS, and the omission was a real misdescription rather
        # than untidiness: the hint is set on a no-op and nothing ever unset it,
        # so on the shipped maps -- where `H`/`L` are no-ops at every width but
        # one -- it latched on the first sideways press and then sat there
        # describing every LIVE `J`/`K` as an edge the operator had not reached.
        self.query_one(HintLine).set_hint("")
        self.refresh_canvas()

    def action_pan_left(self) -> None:
        self._pan(-1, 0)

    def action_pan_right(self) -> None:
        self._pan(1, 0)

    def action_pan_up(self) -> None:
        self._pan(0, -1)

    def action_pan_down(self) -> None:
        self._pan(0, 1)

    def _unpainted_ids(self) -> frozenset[str] | None:
        """The graph's nodes minus the ones the current render actually painted.

        LLR-N06.3.1 read literally: ONE set difference, and no fold count is
        added to a viewport count anywhere.  Summing the two double-counts every
        node that is both folded and off-screen, and the indicator then declares
        more hidden nodes than the graph contains.

        `None` -- not an empty set -- when the operator is in a view that
        declares nothing.  `painted_ids` lives on `views/layered.py` only, and
        `outline` and `radial` also hide nodes without declaring them (measured
        at 30x6 on `legacy`: 5 of 8 and 2 of 8 traced).  That hole is carried as
        `B-55` to Inc-5; answering it here with a `getattr` probe would convert
        a declared gap into a silent skip.

        `None` ALSO when the layout itself failed.  `painted_ids` shares
        `_geometry` with `render`, so it raises on exactly the frames the canvas
        cannot draw -- and this helper is called from `refresh_canvas`, inside
        the message pump.  Letting that escape turns a contained, declared
        degradation ("no se pudo dibujar el mapa") into a dead app.  `None` is
        the value this helper already has for "this view declares nothing",
        which is the truthful answer for a frame that was never laid out.
        """
        if self._current_renderer() is not self.renderer:
            return None
        w, h = self._canvas_size()
        try:
            painted = painted_ids(self.graph, self._view_state(w, h))
        except Exception:
            return None
        return frozenset(self.graph.nodes) - painted

    def _park_focus(self) -> None:
        """Hand the keyboard back to the map itself."""
        self.set_focus(None)

    def _declare_after_layout(self) -> None:
        """Repaint BOTH declaring surfaces once layout is real — B-56 and B-60.

        `on_mount` paints before the compositor has given the canvas its region,
        so the declaration computed there describes a frame that does not exist.
        Measured on `legacy`, that is not a stale numeral but an ABSENT one: at
        50x20 and 60x20 -- ordinary sizes -- half the map was off screen and the
        strip said nothing at all, which `LLR-N06.3.3` makes mean "nothing is
        hidden".

        AND ORDINARY NAVIGATION DOES NOT HEAL IT.  Measured over nine keys, only
        `l` and `o` reconcile the surfaces; `j`, `k`, `h`, the arrow keys and
        `tab` do not -- at the root `j` is a no-op, so nothing repaints.  A
        reader who only LOOKS at the map, which is US-N06's whole use case,
        would otherwise keep two contradicting indicators indefinitely.  An
        earlier revision recomputed only the STRIP and carried the canvas
        header's own numeral as `B-60` on the claim that "any repaint at all
        reconciles them"; that claim was measured and is false, so the residual
        is closed here instead of narrated.

        A full `refresh_canvas` would also close it and would also re-`show` the
        rail and the inspector, moving the keyboard after `LLR-CNV.3.1` and
        `B-50` placed it -- measured, `call_after_refresh(refresh_canvas)`
        reddens the focus arm with `assert 'rail' == 'inspector'`.  So this
        repaints exactly the two surfaces that DECLARE and nothing that focuses.
        No `pulse_cursor`: this is a declaration repaint, not a cursor move, and
        a second breath on mount is motion the operator did not cause.
        """
        canvas = self.query_one("#map-canvas", Static)
        region = canvas.region
        w, h = self._canvas_size()
        try:
            text = self._current_renderer().render(self.graph, self._view_state(w, h))
        except Exception:
            # `refresh_canvas` has already painted its declared "no se pudo
            # dibujar el mapa" for this frame; overwriting it from here would
            # replace a stated degradation with a second copy of itself.
            pass
        else:
            canvas.update(text)
        self.query_one("#map-pagination", Static).update(self._pagination_text())
        # ONE PASS IS NOT ENOUGH, AND THAT WAS `B-60`'s RESIDUAL.  This runs on
        # the first `call_after_refresh`, and at narrow terminals the region is
        # still reflowing then: instrumented at (31,16) the three passes saw
        # 31x1, then 29x2, and the region SETTLED at 31x3 afterwards, so both
        # declaring surfaces kept a numeral computed for a frame that no longer
        # existed -- the strip read 8 against a truth of 7.  So the declaration
        # follows the region until it stops moving, which is the condition it
        # actually needs and one a one-shot callback cannot express.  It
        # terminates because it re-schedules only while the region CHANGED, so
        # a settled layout costs exactly one extra no-op pass.
        if region != self._declared_for:
            self._declared_for = region
            self.call_after_refresh(self._declare_after_layout)

    def on_resize(self, event: events.Resize) -> None:
        """Re-declare when the layout actually settles — `B-60`, closed properly.

        `on_mount` schedules `_declare_after_layout` on the FIRST
        `call_after_refresh`, and at narrow terminals that callback runs while
        `_apply_region_visibility`'s show/hide is still reflowing the row.
        Instrumented at (31,16): the callback saw a 29x2 canvas region, so
        `_canvas_size` took the short-region branch, returned `h = 1` and
        declared nothing painted; the region then settled to 31x3.  With no
        resize handler nothing recomputed, so BOTH declaring surfaces kept a
        numeral computed for a frame that no longer existed -- the strip said 8
        while 7 were hidden.  Reproduced at (31,16), (32,16), (34,15), (35,14)
        on `legacy` and independently on `anidado`, so it is not a fixture
        quirk.

        A one-shot post-mount callback cannot see the settle; the resize can.
        This repaints the same two surfaces `_declare_after_layout` does and
        nothing that focuses, so `LLR-CNV.3.1` and `B-50` stay where they are.

        THIS HANDLER ALONE DOES NOT CLOSE IT, and the measurement says why: a
        SCREEN resize is not a CANVAS resize.  Traced at (31,16), this fires
        once with the terminal's own 31x16 -- BEFORE the row reflows -- and the
        canvas region moves twice more afterwards without any further screen
        resize.  So this covers the case that had no handler at all, an operator
        resizing the terminal after mount, and `_declare_after_layout` chases
        the region to its settle from wherever it is entered.
        """
        self._declared_for = None
        self._declare_after_layout()

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
        """Return (glyph, style) for a top-level branch's coverage minimap.

        THE `seen` SET IS NOT DEFENSIVE PADDING; without it this walk does not
        terminate.  It had no visited check at all, so on a graph with a cycle
        it re-expanded the same nodes forever -- an unbounded HANG reached from
        `refresh_canvas`, outside every guard, which is worse than the crash the
        sibling guards catch and is the one failure mode this tree's own rule
        singles out.  It also double-counted on a multi-parent DAG, where a node
        reachable by two paths landed in `nodes` twice and skewed the coverage
        percentage this glyph exists to report.
        """
        nodes = [branch_root]
        seen = {branch_root}
        stack = [branch_root]
        while stack:
            parent = stack.pop()
            for cid in self.graph.children_of(parent):
                if cid in seen:
                    continue
                seen.add(cid)
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
            # Both halves are file-derived, and this widget's whole job is
            # telling the operator WHICH branch is at risk -- a `U+202E` here
            # displays one branch's coverage under a neighbour's name, so an
            # uncoerced title deceives the operator on exactly the judgement the
            # minimap exists to support.  `refresh_canvas` repaints it, which is
            # what puts it inside `LLR-N06.2.3`'s "every file-derived string
            # painted on a surface this batch touches".
            name = darkside.plain(self.graph.nodes[cid].ficha.title or cid)
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
        text = darkside.Text.assemble(
            (" ", ""),
            darkside.step_meter(min(page, per_page), per_page),
            (f"   {page}/{per_page}  ", darkside.MUT),
        )
        # HLR-N06.3 on the strip beside the canvas, from the SAME `painted_ids`
        # pass the renderer used, so the two surfaces cannot declare different
        # totals.  `None` means a view that declares nothing, and the strip then
        # keeps only its reserved-affordance content.
        hidden = self._unpainted_ids()
        if hidden:
            text.append(f"{OVERFLOW_TOKEN} {len(hidden)} fuera de vista ",
                        style=darkside.INK)
        return text

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

    # Widget id -> the `FOCUS_OWNERS` name that id stands for.  Bare ids, not
    # `#`-prefixed strings: nothing here is a CSS selector, and synthesising one
    # to compare against another string that merely looks like one silently
    # compares "#None" for every unnamed widget.
    _FOCUS_REGIONS = (
        ("map-rail", "rail"),
        ("map-inspector", "inspector"),
        ("map-canvas", "canvas"),
    )

    def _focus_owner(self) -> str:
        """Which region holds the keyboard, as one of `FOCUS_OWNERS`.

        Derived from the app's real focused widget rather than tracked
        separately: a second copy of "where the focus is" is a copy that goes
        stale, and the stale copy is the one the canvas would paint from.
        Returns `""` when nothing is focused, or when the focused widget belongs
        to no declared region -- the value that paints what the tree painted
        before this field existed.

        MEASURED: `#map-canvas` is `can_focus=False`, so `"canvas"` is not
        reachable through the real wiring today and the focused tone is arrived
        at via the `""` fallback.  The entry is kept because it is correct the
        moment the canvas becomes focusable, but a reader should not assume it
        is live (`B-53`).

        `""` IS ALSO THE HONEST ANSWER ON A NARROW TERMINAL, and that is not a
        defect: below `MIN_CANVAS_WIDTH`, `_apply_region_visibility` auto-hides
        the rail and the inspector, so nothing focusable remains and the focus
        chain is legitimately empty.  An earlier revision read that as "tab
        drops focus on this screen" and carried it as a defect -- measured only
        at the 80x24 default test size.  At 118x34 the chain is
        `[map-rail, insp-title, insp-state, insp-notes]` and tab traverses
        normally.  Retracted in `A-96`.
        """
        node = getattr(self.app, "focused", None)
        while node is not None:
            node_id = getattr(node, "id", None)
            for region_id, owner in self._FOCUS_REGIONS:
                if node_id == region_id:
                    return owner
            node = getattr(node, "parent", None)
        return ""

    def _view_state(self, w: int, h: int) -> ViewState:
        """The renderer's whole parameter surface, built in ONE place.

        Built once and reused by every call site, which is what closes the
        measured defect that motivated the parameter object: the export site
        passed `query` without `diff`, so an SVG exported during a diff silently
        lost its tinting while the on-screen canvas kept it.  With one
        constructor there is no second argument list to forget.
        """
        return ViewState(
            selected_id=self.nav.cursor,
            w=w,
            h=h,
            focus_owner=self._focus_owner(),
            query=self.query_text,
            diff=self.diff if self.diff_active else None,
            pan_x=self.pan_x,
            pan_y=self.pan_y,
            folded=self.folded,
        )

    def refresh_canvas(self) -> None:
        canvas = self.query_one("#map-canvas", Static)
        renderer = self._current_renderer()
        w, h = self._canvas_size()
        # Any renderer failure is a drawing problem, not an application problem:
        # this method runs inside the message pump, so an escape here kills the
        # app.  Scoped to the sink, not to the exception types known today --
        # which is why `_reclamp_pan` is INSIDE it rather than beside it: it
        # reaches the same `_tree_layout` the render does, and Inc-3 had moved it
        # out where the guard could not see it.
        try:
            self._reclamp_pan(w, h)
            text = renderer.render(self.graph, self._view_state(w, h))
        except Exception as exc:
            text = darkside.Text.assemble(
                (" no se pudo dibujar el mapa\n\n", f"bold {darkside.INK}"),
                (f" {darkside.plain(str(exc))}", darkside.MUT),
            )
        canvas.update(text)
        pulse_cursor(canvas)

        tab = self.query_one(TabStrip)
        node = self.graph.nodes.get(self.nav.cursor or "")
        node_title = node.ficha.title if node else ""
        # EVERY crumb segment, not just the title: `_current_crumb` also carries
        # `map_id` and the link chain, which are file-derived too.  Found by the
        # frame-level half of `LLR-N06.2.3`'s census rather than by the
        # region-by-region half -- `TabStrip` is queried BY TYPE here, so it has
        # no id for a region sweep to enumerate, and a hostile ficha title was
        # reaching the composited frame through the breadcrumb with the same
        # `U+202E` the minimap leaked.
        tab.set_crumb([
            darkside.plain(part) for part in self._current_crumb() + [node_title]
        ])

        self.query_one("#map-inspector", FichaInspector).show(node, self.graph)
        self.query_one("#map-rail", OutlineRail).show(
            self.graph, self.nav.cursor, self.folded
        )
        # GUARDED LIKE ITS SIBLING, and the asymmetry was the finding: this call
        # sits past the `try` above, `_branch_coverage_glyph` and `_minimap_text`
        # both index `self.graph.nodes[...]` unchecked, and a dangling edge
        # raises `KeyError` from inside the message pump -- which kills the app,
        # exactly the shape the cycle guard was added for.  `_unpainted_ids` has
        # its own try/except; the minimap had none.  A coverage strip that
        # cannot be drawn is a drawing problem, so it degrades to empty.
        #
        # THIS GUARD DOES NOT SAVE THE APP ON A DANGLING EDGE, and the comment
        # above says only that this method stops leaking one.  Measured, the
        # composited paint of the same graph still dies: `OutlineRail.render`
        # indexes `graph.nodes[...]` unchecked too and raises at compositor
        # paint time, one sink over and on a different path.  That sink is
        # CARRIED, not closed -- see the arm in `tests/test_pan.py` that states
        # in terms what it asserts (the exception does not escape this method)
        # and what it does not (that the frame survives).
        try:
            minimap = self._minimap_text()
        except Exception:
            minimap = darkside.Text("")
        self.query_one("#map-minimap", Static).update(minimap)
        # LAST, and the position is load-bearing rather than incidental: the
        # declaration is computed from `painted_ids` over the state that was
        # just rendered, and `_focus_owner` -- which `_view_state` reads -- is
        # only settled once the side regions have been shown.  Moved ahead of
        # them during development and 6 arms went red on focus and on the rail's
        # byte identity.
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
        self._event_toast("guardado", darkside.plain(node.ficha.title or node.id))

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

    # -- attachments (US-N02) ----------------------------------------------
    def on_ficha_inspector_attachment_activated(
        self, event: FichaInspector.AttachmentActivated
    ) -> None:
        """Open an attachment through the one OS-handler boundary.

        The refusal is always shown: a dropped status word would make a refused
        launch indistinguishable from a successful one (LLR-N02.9).
        """
        event.stop()
        node = self.graph.nodes.get(event.node_id)
        if node is None or self.store is None:
            return
        if not 0 <= event.index < len(node.ficha.attachments):
            return
        att = node.ficha.attachments[event.index]
        status = open_external(
            att.kind, att.path, workspace=self.store.workspace,
            launcher=getattr(self.app, "attachment_launcher", None),
        )
        # Both branches carry file-derived text, so both are coerced.  `notify`
        # parses markup by default in textual 8.2.8 (Toast.render calls
        # Content.from_markup), so a hostile path could crash the toast or, worse,
        # REWRITE the refusal text the operator is reading — defeating the point
        # of showing the real target at the exact moment it matters.
        shown = darkside.plain(att.path)
        if status == OSOPEN_OK:
            self._event_toast("abierto", darkside.plain(att.caption or att.path))
        else:
            self.notify(f"{status}: {shown}", severity="warning", markup=False)

    def on_ficha_inspector_attachment_add_requested(
        self, event: FichaInspector.AttachmentAddRequested
    ) -> None:
        event.stop()
        node = self.graph.nodes.get(event.node_id)
        if node is None or self.store is None:
            return

        def on_target(target: str | None) -> None:
            if not target:
                return
            self._push_snapshot()
            kind = "url" if "://" in target else "file"
            node.ficha.attachments.append(Attachment(kind=kind, path=target))
            self.store.save(self.map_id, self.graph)
            self.base_graph = self.graph
            self.refresh_canvas()
            self._event_toast("adjunto agregado", darkside.plain(target))

        self.app.push_screen(
            _PromptScreen("ruta o url del adjunto", "docs/acta.pdf"), callback=on_target
        )

    def on_ficha_inspector_attachment_remove_requested(
        self, event: FichaInspector.AttachmentRemoveRequested
    ) -> None:
        event.stop()
        node = self.graph.nodes.get(event.node_id)
        if node is None or self.store is None:
            return
        if not 0 <= event.index < len(node.ficha.attachments):
            return
        removed = node.ficha.attachments.pop(event.index)
        self._push_snapshot()
        self.store.save(self.map_id, self.graph)
        self.base_graph = self.graph
        self.refresh_canvas()
        self._event_toast(
            "adjunto quitado", darkside.plain(removed.caption or removed.path)
        )

    def action_add_attachment(self) -> None:
        self.query_one("#map-inspector", FichaInspector).request_add_attachment()

    def action_remove_attachment(self) -> None:
        self.query_one("#map-inspector", FichaInspector).request_remove_attachment()

    UNDO_DEPTH = 20

    @property
    def _snapshots(self) -> list[bytes]:
        """This map's undo history, held by the App so it outlives the screen.

        Keyed by `map_id`: one global stack would let an undo taken in map B
        restore a snapshot of map A, which is data loss wearing a feature's
        clothes.
        """
        return self.app.undo_stacks.setdefault(self.map_id, [])

    def _push_snapshot(self) -> None:
        if self.store is None:
            return
        mmd = dump_mermaid(self.graph)
        sidecar = self.store._build_sidecar(self.graph)
        import yaml

        yml = yaml.safe_dump(sidecar, sort_keys=False, allow_unicode=True)
        stack = self._snapshots
        stack.append(json.dumps({"mmd": mmd, "yml": yml}).encode())
        del stack[: max(0, len(stack) - self.UNDO_DEPTH)]

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
        self.notify(f"diff: +{added} -{removed} ~{changed}", markup=False)

    def action_coverage(self) -> None:
        def on_select(node_id: str | None) -> None:
            if node_id is None or node_id not in self.graph.nodes:
                return
            self._goto_gap(node_id)

        self.app.push_screen(CoverageScreen(self.graph, self.map_id), callback=on_select)

    # -- coverage worklist (US-N04) ----------------------------------------
    def _incomplete_order(self) -> list[str]:
        """Nodes with a missing required field, in the coverage report's order.

        Walks the tree the same way `CoverageScreen` does, so "next" in the
        worklist means the same thing as "next row" in the report.  Consumes
        `Ficha.missing_required`, the model's single owner of what is missing.
        """
        out: list[str] = []
        if self.graph.root_id is None:
            return out
        visited: set[str] = set()
        stack = [self.graph.root_id]
        while stack:
            nid = stack.pop()
            if nid in visited or nid not in self.graph.nodes:
                continue
            visited.add(nid)
            if self.graph.nodes[nid].ficha.missing_required(self.graph.schema):
                out.append(nid)
            for cid in reversed(self.graph.children_of(nid)):
                if cid not in visited:
                    stack.append(cid)
        return out

    def _goto_gap(self, node_id: str) -> bool:
        """Move the cursor to *node_id* and focus its first missing field."""
        if node_id not in self.graph.nodes:
            return False
        self.nav.cursor = node_id
        if self.inspector_hidden:
            self.inspector_hidden = False
            self._apply_region_visibility()
        # Ask for the focus BEFORE refreshing: the inspector applies the request
        # at the end of the rebuild that creates the rows, so the two are ordered
        # causally instead of racing on frame timing.
        missing = self.graph.nodes[node_id].ficha.missing_required(self.graph.schema)
        inspector = self.query_one("#map-inspector", FichaInspector)
        inspector.focus_after_rebuild(missing[0].key if missing else None)
        self.refresh_canvas()
        if missing:
            self.query_one(HintLine).set_hint(
                # `↵` is what commits, not ctrl+s — MapScreen binds no ctrl+s at
                # all, and advertising a key that does nothing on the primary flow
                # is the exact defect US-N03 exists to remove.
                f"completa «{missing[0].label}» · ↵ guarda · esc deja el campo", "↵"
            )
        return True

    def action_next_gap(self) -> None:
        """Advance to the next node that is missing a required field.

        Wraps once.  When nothing anywhere is missing it says so, rather than
        cycling silently on the same node forever.
        """
        order = self._incomplete_order()
        if not order:
            self._event_toast("cobertura completa", "no falta ningún campo requerido")
            return
        if self.nav.cursor in order:
            idx = (order.index(self.nav.cursor) + 1) % len(order)
        else:
            idx = 0
        self._goto_gap(order[idx])

    def action_export_svg(self) -> None:
        if self.store is None:
            return
        try:
            size = self.size or self.app.size
            renderer = self._current_renderer()
            # The same state the canvas draws from, EXCEPT the focus owner.
            #
            # Sharing the state is what closes the measured defect that decided
            # the renderer contract: this site passed `query` and omitted
            # `diff`, so an SVG exported during a diff silently lost its
            # tinting.  One constructor leaves no second argument list to
            # under-fill.
            #
            # But an export is a STANDALONE ARTIFACT, and "which screen region
            # owns the keyboard" is meaningless inside it.  Measured on a plain
            # operator sequence -- `tab` (or `g`, which focuses the rail), then
            # `e` to export -- passing the live owner through painted the
            # selected node in the INACTIVE tone.  An export always renders as
            # though the canvas were focused.
            text = renderer.render(
                self.graph,
                replace(
                    self._view_state(max(20, size.width), max(5, size.height - 10)),
                    focus_owner="",
                ),
            )
            path = self.store.workspace / f"{self.map_id}.svg"
            save_svg(text, path)
            self._event_toast("exportado", str(path))
        except Exception as e:
            self.notify(f"exportación fallida: {e}", severity="error", markup=False)

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
            self._event_toast("archivado", darkside.plain(node.ficha.title or node.id))

        # Every archive is confirmed, root or not.  A non-root subtree used to be
        # destroyed with no prompt at all, and `x` sits next to the navigation
        # keys.  The message names how much goes, because "archivar" alone does
        # not tell the operator that the children go too.
        count = self._subtree_size(self.nav.cursor)
        name = node.ficha.title or node.id
        # Archiving everything is not archiving, it is erasing.  The confirmation
        # used to promise it would "replace the root of the map" and then wrote an
        # EMPTY map to disk — nodes {}, root_id None — with the only recovery an
        # in-memory undo stack that dies with the process.  Refuse instead.
        if count >= len(self.graph.nodes):
            self.notify(
                "no se puede archivar todo el mapa: quedaría vacío. "
                "archiva una rama, o elimina el mapa desde inicio.",
                severity="warning",
                markup=False,
            )
            return
        if self.nav.cursor == self.graph.root_id:
            message = (
                f"¿archivar la raíz «{name}» y sus {count - 1} descendientes? "
                "esto reemplazará la raíz del mapa."
            )
        elif count > 1:
            message = f"¿archivar «{name}» y sus {count - 1} descendientes?"
        else:
            message = f"¿archivar «{name}»?"
        self.app.push_screen(_ConfirmScreen(message), callback=do_archive)

    def _subtree_size(self, root_id: str | None) -> int:
        """How many nodes would go if this subtree were archived."""
        if root_id is None:
            return 0
        seen: set[str] = set()
        stack = [root_id]
        while stack:
            nid = stack.pop()
            if nid in seen or nid not in self.graph.nodes:
                continue
            seen.add(nid)
            stack.extend(self.graph.children_of(nid))
        return len(seen)

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
    /* S-07 (LLR-R04.1): without this rule the rail defaults to the full width of
       #map-body, so the canvas collapses to 1 column and the inspector is laid
       out entirely off-screen (measured at 140x45: rail x=0 w=140, inspector
       x=141..177).  The 24 is a LITERAL and not an interpolation of
       rail.RAIL_WIDTH on purpose: TC-R22 asserts the two agree, and a value the
       stylesheet derived from the constant could never disagree with it. */
    #map-rail { width: 24; height: 100%; }
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
        # Undo history lives here, not on MapScreen: a screen is rebuilt every
        # time the operator re-enters a map, which used to discard the history
        # silently and make an archived subtree unrecoverable.
        self.undo_stacks: dict[str, list[bytes]] = {}
        self.attachment_launcher = None

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
