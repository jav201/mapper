"""The GitHub repo dashboard screen — A5b of batch
`2026-10-09-modular-batch` (LLR-MOD.1.1).

Home of `RepoScreen`, the two-pane branch dashboard the plug-repo screen
pushes after the operator types a repo.  The name is re-exported from
`mapper.app` so historical `from mapper.app import RepoScreen` sites keep
resolving (LLR-MOD.3.1); `screens/*` modules import it here directly once
their increments move them (the B-02 remediation, LLR-MOD.6.1: no
`screens` -> `app` back-edge).
"""
from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Static
from textual.worker import WorkerFailed

from mapper import darkside, github
from mapper.github import GitHubConnector, GitHubError, painted_repo
from mapper.keymap import SCOPE_APP, SCOPE_REPO, groups_for_keybar, hint_pair
from mapper.model import Graph
from mapper.motion import pulse_cursor
from mapper.screens.common import keybar_groups, screen_bindings
from mapper.screens.map.navigation import NavigationModel
from mapper.widgets.chrome import KeyBar, TabStrip

if TYPE_CHECKING:
    from mapper.model import Node


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
        # `S1`: what is painted; `self.repo` stays as typed for the connector.
        self.shown = painted_repo(repo)
        self.graph = Graph()
        self.nav = NavigationModel(self.graph)
        self.selected_index = 0
        self.failure = ""
        self.stale = ""

    def compose(self) -> ComposeResult:
        yield TabStrip("p", crumb=[self.shown])
        with Horizontal(id="repo-dashboard"):
            with Vertical(id="repo-sidebar"):
                # `INC9F-SEC-F2`: typed text, painted as text: `Static(str)` parses markup.
                yield Static(Text(darkside.plain(self.shown)), id="repo-name")
                yield Static(self._stages_text(), id="repo-stages")
                yield Static(self._progress_text(), id="repo-progress")
                yield Static(self._sidebar_hints(), id="repo-sidebar-hints")
            yield Static(self._render_table(), id="repo-table", expand=True)
        yield KeyBar(groups_for_keybar(keybar_groups(self.KEY_SCOPE)))

    @staticmethod
    def _sidebar_hints() -> str:
        """The body panel's key hints, read from the seat (`K3`).  No `↵` line:
        this screen binds no enter and no handler answers it (`INC9C-F1`)."""
        pairs = [hint_pair(SCOPE_REPO, a) for a in ("next_sibling", "prev_sibling", "home")]
        return "\n".join([*pairs, hint_pair(SCOPE_APP, "help")])

    def _stages_text(self) -> Text:
        if self.failure:
            # `M2`: the toast expires; the panel is what stays.  The same fixed
            # sentence the toast carries, and the way out in the seat's word.
            return Text.assemble(
                ("▲ failed\n", darkside.INK),
                (self.failure + "\n", darkside.INK),
                (hint_pair(SCOPE_REPO, "home"), darkside.MUT),
            )
        stages = ["starting", "reading branches", "computing metrics", "ready"]
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
        if self.stale and not self.loading:
            # `P1`: the toast expires and `listo` would read as a fresh connect; the line
            # stays for as long as the cached copy is what the screen shows.
            # `INC9H-UX-F1`: the category goes on its own line, so the 30-cell sidebar never
            # breaks it (`unknown (exit` / `1)`).
            text.append("\n", "")
            text.append(darkside.plain(f"▲ cached copy:\n{self.stale}"), darkside.INK)
        return text

    def _progress_text(self) -> Text:
        if self.failure:
            return Text("")
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
            return Text.assemble(("● ", darkside.ALERT), ("blocked", darkside.ALERT))
        if state == "risk":
            return Text.assemble(("● ", darkside.WARN), ("risk", darkside.WARN))
        return Text.assemble(("● ", darkside.INK), ("ok", darkside.MUT))

    def _source_kind(self) -> str:
        # `INC9L-CR-F3`: the one decision `fetch` and `painted_repo` already read; a remote
        # (`gh` or a URL) keeps the `github` badge, and a refused text is not a remote.
        try:
            return "local" if github.source_kind(self.repo) == "local" else "github"
        except GitHubError:
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
            return Text("(no branches loaded)", style=darkside.MUT)

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
        lines.append(f"   {len(branches)} branches · {len(releases)} releases\n", darkside.MUT)
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
                        note_parts.append("today")
                    elif age == 1:
                        note_parts.append("yesterday")
                    elif age < 7:
                        note_parts.append(f"{age} d ago")
                    elif age < 30:
                        note_parts.append(f"{age // 7} wk ago")
                    else:
                        note_parts.append(f"{age // 30} mo ago")
                meta = node.ficha.meta or ""
                if meta and meta != "release":
                    note_parts.append(meta)
                if node.ficha.notes and node.ficha.notes != "CI: unknown":
                    note_parts.append(node.ficha.notes)
                note = " · ".join(note_parts) or "no data"
                row = self._time_row(name, max(0, age), glyph, style, note)
                # selection marker
                marker = "▶ " if idx == self.selected_index else "  "
                lines.append(marker, darkside.ACCENT if idx == self.selected_index else "")
                lines.append_text(row)
                lines.append("\n", "")
            lines.append("\n", "")

        order = {"release": 0, "hotfix": 1, "branch": 2}
        branches.sort(key=lambda item: (order.get(self._branch_kind(item[0]), 2), item[0]))
        render_group("branches", branches, "●", darkside.INK)
        render_group("releases", releases, "◆", darkside.INK)

        lines.append("  ")
        lines.append("●", darkside.INK)
        lines.append(" commit   ", darkside.MUT)
        lines.append("◆", darkside.INK)
        lines.append(" release   ", darkside.MUT)
        lines.append("╎", darkside.WORDMARK)
        lines.append(" today   (30 days)\n", darkside.MUT)
        return lines

    def _refresh_table(self) -> None:
        table = self.query_one("#repo-table", Static)
        table.update(self._render_table())

    @work(thread=True, exit_on_error=False)
    def fetch_graph(self) -> Graph:
        def on_progress(current: int, total: int, stage: str) -> None:
            try:
                self.app.call_from_thread(self._update_progress, current, total, stage)
            except Exception:
                pass
        connector = GitHubConnector(self.repo)
        graph = connector.fetch(progress=on_progress)
        self.stale = connector.stale
        return graph

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
        table.update(Text("  connecting… this may take a few seconds", style=darkside.MUT))
        try:
            worker = self.fetch_graph()
            self.graph = await worker.wait()
            count = len(self.graph.nodes)
            if self.stale:
                # `INC9F-CR-F4`: the refresh failed; what is painted is the cached copy.
                # `P2`: this is the ONE toast of a stale connect (`conectado` would
                # contradict it); `P1` pairs it with the panel line.  The way back is the seat's.
                self.notify(
                    darkside.plain(
                        f"showing the cached copy ({count} nodes): {self.stale} · "
                        f"{hint_pair(SCOPE_REPO, 'home')} to retry"),
                    severity="warning", markup=False)
            else:
                self.notify(darkside.plain(f"connected: {count} nodes"), markup=False)
        except Exception as exc:
            # `INC9BC-SEC-F3`: the worker does not exit the app (`exit_on_error`),
            # so its failure arrives here wrapped, and `GitHubError` is reachable.
            if isinstance(exc, WorkerFailed):
                exc = exc.error
            if isinstance(exc, GitHubError):
                self.failure = darkside.plain(str(exc))
            else:
                self.failure = darkside.plain(f"unexpected error: {type(exc).__name__}")
            self.notify(darkside.plain(self.failure), severity="error", markup=False)
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
