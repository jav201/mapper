"""Read-only GitHub repo-to-map adapter via the authenticated `gh` CLI."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone

from .model import Edge, Ficha, Graph, Node


class GitHubError(Exception):
    pass


class GitHubConnector:
    """Fetch repository metadata and return a Graph representing branches as lanes."""

    def __init__(self, repo: str):
        self.repo = repo

    def _gh(self, args: list[str]) -> dict | list:
        cmd = ["gh"] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
            )
        except subprocess.CalledProcessError as exc:
            raise GitHubError(exc.stderr.strip() or exc.stdout.strip()) from exc
        except FileNotFoundError as exc:
            raise GitHubError("gh CLI not found") from exc
        return json.loads(result.stdout or "{}")

    def fetch(self) -> Graph:
        parts = self.repo.split("/")
        if len(parts) != 2:
            raise GitHubError(f"repo must be owner/name, got {self.repo}")
        owner, name = parts

        repo_info = self._gh(["repo", "view", self.repo, "--json", "name,defaultBranchRef"])
        default_branch = repo_info.get("defaultBranchRef", {}).get("name", "main")

        branches = self._gh([
            "api", f"repos/{owner}/{name}/branches?per_page=20",
        ])
        if not isinstance(branches, list):
            raise GitHubError("unexpected response from gh api branches")

        graph = Graph()
        root = Node(id=self.repo, ficha=Ficha(title=self.repo, meta="repo"))
        graph.add_node(root)

        for branch in branches:
            bname = branch["name"]
            # ahead/behind against default branch
            comparison = self._gh([
                "api", f"repos/{owner}/{name}/compare/{default_branch}...{bname}",
            ])
            ahead = comparison.get("ahead_by", 0)
            behind = comparison.get("behind_by", 0)

            # CI verdict from latest commit check-runs
            ci = ""
            try:
                commit = self._gh([
                    "api", f"repos/{owner}/{name}/commits/{bname}",
                ])
                sha = commit.get("sha", "")
                if sha:
                    checks = self._gh([
                        "api", f"repos/{owner}/{name}/commits/{sha}/check-runs",
                    ])
                    conclusions = [
                        c.get("conclusion", "")
                        for c in checks.get("check_runs", [])
                    ]
                    if "failure" in conclusions:
                        ci = "fail"
                    elif "success" in conclusions:
                        ci = "ok"
                    elif conclusions:
                        ci = "pending"
            except GitHubError:
                ci = ""

            state = "ok"
            if ci == "fail":
                state = "blocked"
            elif ahead > 10 or behind > 10:
                state = "risk"

            node = Node(
                id=bname,
                ficha=Ficha(
                    title=bname,
                    meta=f"+{ahead}/-{behind}",
                    state=state,
                    notes=f"CI: {ci or 'unknown'}",
                ),
            )
            graph.add_node(node)
            graph.add_edge(Edge(parent_id=self.repo, child_id=bname))

        return graph
