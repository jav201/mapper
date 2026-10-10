"""The connect-repo input screen — A6 of batch
`2026-10-09-modular-batch` (LLR-MOD.1.1).

Home of `PlugRepoScreen`, the single-field screen the operator types an
owner/name, URL or local path into; on submit it pushes `RepoScreen`
(imported here from `mapper.screens.repo`, never from `mapper.app`; §3).
The name is re-exported from `mapper.app` so historical
`from mapper.app import PlugRepoScreen` sites keep resolving (LLR-MOD.3.1).
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Input, Label

from mapper.keymap import SCOPE_PLUG, groups_for_keybar
from mapper.screens.common import keybar_groups, screen_bindings
from mapper.screens.repo import RepoScreen
from mapper.widgets.chrome import HintLine, KeyBar, TabStrip


class PlugRepoScreen(Screen):
    """Input screen for plugging a GitHub repo."""

    KEY_SCOPE = SCOPE_PLUG
    # `K4`: the legend's title reads the SCREEN's name, not the scope id.
    legend_view = "connect repo"
    BINDINGS = screen_bindings(SCOPE_PLUG)

    def compose(self) -> ComposeResult:
        yield TabStrip("p", crumb=["connect repo"])
        yield Vertical(
            Label("connect repo", id="repo-title"),
            Input(placeholder="owner/name or github URL", id="repo-input"),
            id="repo-dialog",
        )
        yield HintLine("enter owner/name, a URL or a local path and press ↵", "↵")
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
            path = value.split("/", 3)[3]  # the check above is case-insensitive, so is this
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
