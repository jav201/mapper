"""Runnable prototype: repo navigation & loading variants.

Run: python prototypes/repo_nav/prototype.py [A|B|C]
Keys: 1/2/3 switch variants, q quit, j/k navigate table, i focus input (A/C), c open command bar (B).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Input, Static

from mapper import darkside
from mapper.keymap import groups_for_keybar


@dataclass
class Branch:
    name: str
    ahead: int
    behind: int
    ci: str
    updated: str
    kind: str = "branch"


BRANCHES = [
    Branch("main", 0, 0, "success", "hace 2h", "release"),
    Branch("feature/auth", 4, 2, "pending", "hace 1d", "branch"),
    Branch("hotfix/db", 1, 5, "failure", "hace 3h", "hotfix"),
    Branch("refactor/ui", 12, 1, "pending", "hace 4d", "branch"),
    Branch("experimental/ml", 30, 8, "failure", "hace 1sem", "branch"),
    Branch("release/v1.9", 0, 0, "success", "hace 1sem", "release"),
]


class RepoNavScreen(Screen):
    """Base screen with priority bindings so keys don't get trapped by Input."""

    BINDINGS = [
        Binding("q", "app.quit", "Salir", priority=True),
        Binding("1", "switch_variant('A')", "A", priority=True),
        Binding("2", "switch_variant('B')", "B", priority=True),
        Binding("3", "switch_variant('C')", "C", priority=True),
        Binding("j", "next", "Siguiente", priority=True),
        Binding("k", "prev", "Anterior", priority=True),
    ]

    def __init__(self, variant: str = "A") -> None:
        super().__init__()
        self.variant = variant
        self.selected = 1

    def action_switch_variant(self, variant: str) -> None:
        self.app.push_screen(RepoNavScreen(variant))

    def action_next(self) -> None:
        self.selected = min(len(BRANCHES) - 1, self.selected + 1)
        self._refresh_table()

    def action_prev(self) -> None:
        self.selected = max(0, self.selected - 1)
        self._refresh_table()

    def _refresh_table(self) -> None:
        table = self.query_one("#branch-table", Static)
        table.update(self._render_table())

    def _render_table(self) -> str:
        lines = []
        for i, branch in enumerate(BRANCHES):
            rail = "▶" if i == self.selected else "▐"
            kind_icon = {"release": "◆", "hotfix": "◈", "branch": "◫"}.get(branch.kind, "◫")
            state = "ok" if branch.ahead < 10 and branch.behind < 10 and branch.ci == "success" else "risk"
            if branch.ci == "failure":
                state = "blocked"
            state_color = {"ok": "#f5f5f5", "risk": "#ffd230", "blocked": "#ff4f42"}.get(state, "#737373")
            lines.append(
                f"{rail} {kind_icon} {branch.name:22} +{branch.ahead:2}/-{branch.behind:2}  "
                f"ci:{branch.ci:7}  {branch.updated:10}  [{state_color}]{state}[/]"
            )
        return "\n".join(lines)


class VariantA(RepoNavScreen):
    """Focus-aware form + progress bar + table."""

    def compose(self) -> ComposeResult:
        yield Static(darkside.tab_strip("p", ["conectar repo"]).plain)
        yield Static("● clonar  ▸  ◐ fetch  ▸  ○ ramas  ▸  ○ listo", id="stage-line")
        yield Static("▰▰▰▰▰▰▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱  42%", id="progress-line")
        yield Vertical(
            Static("owner/repo", classes="muted"),
            Input(value="jav201/taskboard", id="repo-input"),
            Static("↵ conectar    tab mueve foco    1/2/3 cambia variante    q salir", classes="muted"),
            id="form-box",
        )
        yield Static(self._render_table(), id="branch-table")
        yield Static(darkside.keybar(groups_for_keybar(["nav", "app"])).plain)


class VariantB(RepoNavScreen):
    """Command bar at bottom + inline progress + dense dashboard."""

    BINDINGS = RepoNavScreen.BINDINGS + [Binding("c", "focus_cmd", "Comando", priority=True)]

    def compose(self) -> ComposeResult:
        yield Static(darkside.tab_strip("p", ["jav201/taskboard"]).plain)
        yield Static("cargando ramas ▰▰▰▰▰▰▰▰▰▰▱▱▱▱▱▱▱▱▱▱▱▱  45%   ◐ 3/6 ramas")
        yield Static(self._render_table(), id="branch-table")
        yield Input(placeholder="c owner/repo", id="cmd-input")
        yield Static("c abre barra · j/k navega · 1/2/3 variantes · q salir")
        yield Static(darkside.keybar(groups_for_keybar(["nav", "app"])).plain)

    def action_focus_cmd(self) -> None:
        self.query_one("#cmd-input", Input).focus()


class VariantC(RepoNavScreen):
    """Two-pane sidebar with stage progress + grouped table."""

    def compose(self) -> ComposeResult:
        yield Static(darkside.tab_strip("p", ["conectar repo"]).plain)
        with Horizontal(id="two-pane"):
            with Vertical(id="sidebar"):
                yield Static("owner/repo", classes="muted")
                yield Input(value="jav201/taskboard", id="repo-input")
                yield Static("● clonar\n◐ fetch\n○ ramas\n○ listo\n")
                yield Static("▰▰▰▰▰▰▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱  60%")
            yield Static(self._render_table(), id="branch-table", expand=True)
        yield Static("i enfoca input · j/k navega · 1/2/3 variantes · q salir")
        yield Static(darkside.keybar(groups_for_keybar(["nav", "app"])).plain)


class RepoNavApp(App):
    CSS = """
    Screen { background: #000000; color: #f5f5f5; }
    Input { border: none; background: #262626; color: #f5f5f5; }
    Input:focus { border: none; background: #262626; }
    #two-pane { height: 1fr; }
    #sidebar { width: 30; background: #121212; padding: 1 1; }
    .muted { color: #737373; }
    """

    def __init__(self, variant: str = "A") -> None:
        super().__init__()
        self.variant = variant

    def on_mount(self) -> None:
        screen_class = {"A": VariantA, "B": VariantB, "C": VariantC}.get(self.variant, VariantA)
        self.push_screen(screen_class())


if __name__ == "__main__":
    variant = sys.argv[1] if len(sys.argv) > 1 else "A"
    RepoNavApp(variant).run()
