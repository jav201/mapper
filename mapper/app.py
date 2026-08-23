"""Textual TUI app for mapper."""
from __future__ import annotations

from pathlib import Path

from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, ListItem, ListView, Static

from .model import Edge, Ficha, Graph, Node
from .export import save_svg
from .github import GitHubConnector, GitHubError
from .search import SearchIndex
from .store import MapStore
from .views.lane import LaneRenderer
from .views.layered import LayeredRenderer
from .views.outline import OutlineRenderer
from .views.radial import RadialRenderer


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


class HomeScreen(Screen):
    """Three-door home screen."""

    BINDINGS = [
        ("c", "consult", "Consult maps"),
        ("p", "plug", "Plug repo"),
        ("n", "construct", "Construct"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static("◆ MAPPER", classes="title")
        yield Static("Mapas vivos para encontrar informacion relevante.", classes="subtitle")
        with Horizontal(id="doors"):
            yield Button("Consult maps [c]", id="btn-consult")
            yield Button("Plug repo [p]", id="btn-plug")
            yield Button("Construct [n]", id="btn-construct")
        yield ListView(id="map-list")
        yield Footer()

    def on_mount(self) -> None:
        store: MapStore = self.app.store  # type: ignore[attr-defined]
        self.query_one("#map-list", ListView).clear()
        for mmd in sorted(store.workspace.glob("*.mmd")):
            self.query_one("#map-list", ListView).append(
                ListItem(Static(mmd.stem), name=mmd.stem)
            )

    def action_consult(self) -> None:
        self.query_one("#map-list", ListView).focus()

    def action_plug(self) -> None:
        self.app.push_screen(PlugRepoScreen())

    def action_construct(self) -> None:
        self.app.push_screen(MapScreen("new"))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        map_id = str(event.item.name)
        self.app.push_screen(MapScreen(map_id))


class PlugRepoScreen(Screen):
    """Input screen for plugging a GitHub repo."""

    BINDINGS = [("escape", "home", "Back")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static("Plug a GitHub repo (owner/name)", classes="title")
        yield Input(placeholder="jav201/taskboard", id="repo-input")
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "repo-input":
            repo = event.value.strip()
            if repo:
                self.app.push_screen(RepoScreen(repo))

    def action_home(self) -> None:
        self.app.pop_screen()


class RepoScreen(Screen):
    """A GitHub repo rendered as branch lanes."""

    BINDINGS = [
        ("j", "next_sibling", "Next"),
        ("k", "prev_sibling", "Prev"),
        ("q", "home", "Home"),
    ]

    def __init__(self, repo: str):
        super().__init__()
        self.repo = repo
        self.graph = Graph()
        self.nav: NavigationModel = NavigationModel(self.graph)
        self.renderer = LaneRenderer()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static("(loading repo...)", id="repo-canvas")
        yield Footer()

    def render(self):
        """Explicit render to avoid any accidental None from internal _render."""
        return Text("")

    def on_mount(self) -> None:
        try:
            self.graph = GitHubConnector(self.repo).fetch()
        except GitHubError as exc:
            self.notify(str(exc), severity="error")
            self.graph = Graph()
        self.nav = NavigationModel(self.graph)
        self.refresh_canvas()

    def refresh_canvas(self) -> None:
        canvas = self.query_one("#repo-canvas", Static)
        size = self.size or self.app.size
        w = max(20, size.width)
        h = max(5, size.height - 3)
        text = self.renderer.render(
            self.graph,
            selected_id=self.nav.cursor,
            w=w,
            h=h,
        )
        canvas.update(text)

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

    def action_home(self) -> None:
        self.app.pop_screen()


class MapScreen(Screen):
    """A map rendered as a layered tree."""

    BINDINGS = [
        ("j", "next_sibling", "Next"),
        ("k", "prev_sibling", "Prev"),
        ("l", "child", "Child"),
        ("h", "parent", "Parent"),
        ("slash", "search", "Search"),
        ("f", "focus", "Focus"),
        ("escape", "unfocus", "Unfocus"),
        ("o", "toggle_outline", "Outline"),
        ("r", "toggle_radial", "Radial"),
        ("e", "export_svg", "Export SVG"),
        ("q", "home", "Home"),
    ]

    def __init__(self, map_id: str):
        super().__init__()
        self.map_id = map_id
        self.store: MapStore = None  # type: ignore[assignment]
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

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static("(loading map...)", id="map-canvas")
        yield Input(placeholder="/search", id="search-input")
        yield Footer()

    def render(self):
        """Explicit render to avoid any accidental None from internal _render."""
        return Text("")

    def on_mount(self) -> None:
        self.store = self.app.store  # type: ignore[attr-defined]
        self.query_one("#search-input", Input).display = False
        if self.map_id == "new":
            self.graph = Graph()
            self.graph.add_node(Node(id="root", ficha=Ficha(title="New map")))
            self.base_graph = self.graph
        else:
            try:
                self.base_graph = self.store.load(self.map_id)
                self.graph = self.base_graph
            except Exception as e:
                self.notify(f"Error loading map: {e}", severity="error")
                self.graph = Graph()
                self.graph.add_node(Node(id="root", ficha=Ficha(title="Error")))
                self.base_graph = self.graph
        self.nav = NavigationModel(self.graph)
        self.refresh_canvas()

    def refresh_canvas(self) -> None:
        canvas = self.query_one("#map-canvas", Static)
        if self.outline_mode:
            renderer = self.outline_renderer
        elif self.radial_mode:
            renderer = self.radial_renderer
        else:
            renderer = self.renderer
        size = self.size or self.app.size
        w = max(20, size.width)
        h = max(5, size.height - 3)
        text = renderer.render(
            self.graph,
            selected_id=self.nav.cursor,
            w=w,
            h=h,
            query=self.query_text,
        )
        canvas.update(text)

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

    def action_search(self) -> None:
        inp = self.query_one("#search-input", Input)
        inp.display = True
        inp.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search-input":
            self.query_text = event.value
            event.input.display = False
            self.refresh_canvas()

    def on_input_blurred(self, event: Input.Blurred) -> None:
        if event.input.id == "search-input":
            event.input.display = False

    def action_focus(self) -> None:
        if self.nav.cursor and not self.focus_active:
            self.graph = self.base_graph.focus(self.nav.cursor)
            self.focus_active = True
            self.nav = NavigationModel(self.graph)
            self.refresh_canvas()

    def action_unfocus(self) -> None:
        if self.focus_active:
            self.graph = self.base_graph
            self.focus_active = False
            self.nav = NavigationModel(self.graph)
            self.refresh_canvas()

    def action_home(self) -> None:
        self.app.pop_screen()

    def action_toggle_outline(self) -> None:
        self.outline_mode = not self.outline_mode
        self.radial_mode = False
        self.refresh_canvas()

    def action_toggle_radial(self) -> None:
        self.radial_mode = not self.radial_mode
        self.outline_mode = False
        self.refresh_canvas()

    def action_export_svg(self) -> None:
        try:
            size = self.size or self.app.size
            text = self.renderer.render(
                self.graph,
                selected_id=self.nav.cursor,
                w=max(20, size.width),
                h=max(5, size.height - 3),
                query=self.query_text,
            )
            path = self.store.workspace / f"{self.map_id}.svg"
            save_svg(text, path)
            self.notify(f"Exported SVG to {path}")
        except Exception as e:
            self.notify(f"Export failed: {e}", severity="error")


class MapperApp(App):
    """Main application entry point."""

    CSS = """
    HomeScreen, PlugRepoScreen { align: center middle; }
    .title { text-align: center; text-style: bold; color: magenta; margin: 1; }
    .subtitle { text-align: center; color: $text-muted; margin-bottom: 2; }
    #doors { height: auto; align: center middle; }
    #doors Button { margin: 1; }
    #map-list { width: 60%; height: auto; border: solid $primary; }
    MapScreen, RepoScreen { layout: vertical; }
    #map-canvas { width: 100%; height: 1fr; }
    #repo-canvas { width: 100%; height: 1fr; }
    #search-input { dock: bottom; }
    """

    def __init__(self, workspace: Path | str):
        super().__init__()
        self.store = MapStore(workspace)

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())


def main() -> None:
    import sys

    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / "maps"
    app = MapperApp(workspace)
    app.run()


if __name__ == "__main__":
    main()
