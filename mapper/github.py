"""Read-only repo-to-map adapter: local git path, remote URL, or GitHub owner/name.

Priority:
  1. Local filesystem path that points at a git repo -> read with `git` commands.
  2. URL (`https://`, `http://`, `git@`) -> clone to a local cache and read with `git`.
  3. `owner/name` -> use the authenticated `gh` CLI (existing behaviour) with optional
     local clone/cache if the repo is public and git is available.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from .model import Edge, Ficha, Graph, Node


ProgressCallback = Callable[[int, int, str], None]


class GitHubError(Exception):
    pass


_URL_RE = re.compile(r"^(https?://|git@).+")


def _is_url(value: str) -> bool:
    return bool(_URL_RE.match(value))


def _is_local_path(value: str) -> bool:
    p = Path(value).expanduser()
    return p.is_dir() and (p / ".git").is_dir()


_SUBPROCESS_TIMEOUT = 30
# A mirror clone moves a whole history, so it gets a longer budget than a read.
_CLONE_TIMEOUT = 120

# `M2`: a failure is reported as ONE of these, chosen by code from stable
# fragments of the tool's English stderr.  The stderr itself is never painted or
# put in an exception: it names the cache path, and a URL may carry a token.
# Order matters: the first category with a matching fragment wins.
_CATEGORY_MARKERS = (
    ("host not found", (
        "could not resolve host", "name or service not known", "no such host",
        "temporary failure in name resolution", "unknown host",
    )),
    ("authentication required", (
        "could not read username", "could not read password", "authentication failed",
        "terminal prompts disabled", "permission denied", "invalid username or password",
        "http 401", "http 403", "error: 401", "error: 403", "gh auth login",
    )),
    ("not found or private", (
        "repository not found", "' not found", "does not exist", "http 404", "error: 404",
        "could not resolve to a repository", "does not appear to be a git repository",
    )),
    ("network unreachable", (
        "network is unreachable", "failed to connect", "connection refused",
        "connection timed out", "connection reset", "no route to host",
        "couldn't connect", "unable to connect", "error connecting to",
    )),
)
_OWNER_RE = re.compile(r"[A-Za-z0-9-]+")
_NAME_RE = re.compile(r"[A-Za-z0-9._-]+")
_TRANSPORT_HELPER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*::")


def _failure_category(stderr: str | None, returncode: int) -> str:
    low = (stderr or "").lower()
    for category, markers in _CATEGORY_MARKERS:
        if any(m in low for m in markers):
            return category
    return f"unknown (exit {returncode})"


def _refuse_unsafe(spec: str) -> None:
    """A typed repository spec is data, never an option or a transport helper."""
    if spec.lstrip().startswith("-"):
        raise GitHubError("refusing the repository: it may not start with '-'")
    if _TRANSPORT_HELPER_RE.match(spec):
        raise GitHubError("refusing the repository: transport helpers are not accepted")


def _run_git(cwd: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["git", "-C", str(cwd)] + args,
            capture_output=True,
            text=True,
            check=check,
            encoding="utf-8",
            timeout=_SUBPROCESS_TIMEOUT,
        )
    except FileNotFoundError as exc:
        raise GitHubError("git CLI not found") from exc
    except subprocess.CalledProcessError as exc:
        category = _failure_category(exc.stderr, exc.returncode)
        raise GitHubError(f"git {args[0]} failed: {category}") from None
    except subprocess.TimeoutExpired:
        raise GitHubError(f"git {args[0]} failed: timed out") from None


def _default_branch(cwd: Path) -> str:
    """Return the default branch name for a local repo."""
    result = _run_git(cwd, ["symbolic-ref", "refs/remotes/origin/HEAD"], check=False)
    if result.returncode == 0 and result.stdout:
        return result.stdout.strip().rsplit("/", 1)[-1]
    result = _run_git(cwd, ["rev-parse", "--abbrev-ref", "HEAD"])
    return result.stdout.strip() or "main"


def _local_branches(cwd: Path) -> list[str]:
    result = _run_git(cwd, ["branch", "-a", "--format=%(refname:short)"])
    names = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    out = []
    seen: set[str] = set()
    for name in names:
        if name == "HEAD":
            continue
        # Keep the full branch name. Strip only the literal "remotes/" bookkeeping
        # prefix; keep "origin/feature/x" intact so category branches survive.
        short = name
        if short.startswith("remotes/"):
            short = short[len("remotes/"):]
        if short in seen:
            continue
        seen.add(short)
        out.append(short)
    return out


def _ahead_behind(cwd: Path, base: str, branch: str) -> tuple[int, int]:
    """Return (ahead, behind) for `branch` relative to `base`."""
    result = _run_git(
        cwd,
        ["rev-list", "--left-right", "--count", "--end-of-options", f"{base}...{branch}"],
        check=False,
    )
    if result.returncode != 0 or not result.stdout:
        return 0, 0
    parts = result.stdout.strip().split("\t")
    if len(parts) != 2:
        return 0, 0
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return 0, 0


def _last_commit_info(cwd: Path, branch: str) -> dict[str, str]:
    """Return author and date for the latest commit on branch."""
    fmt = "%an|%aI|%s"
    result = _run_git(cwd, ["log", "-1", f"--format={fmt}", "--end-of-options", branch], check=False)
    info = {"author": "", "date": "", "subject": ""}
    if result.returncode != 0 or not result.stdout:
        return info
    parts = result.stdout.strip().split("|", 2)
    if len(parts) >= 3:
        info["author"] = parts[0]
        info["date"] = parts[1]
        info["subject"] = parts[2]
    return info


def _tags(cwd: Path) -> list[str]:
    result = _run_git(cwd, ["tag", "-l"], check=False)
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _repo_name_from_url(url: str) -> str:
    """The last URL segment, which becomes a directory name under the cache.

    `B-77b`: it is typed text, so it is refused when it could leave the cache
    (`..`, a run of dots, a separator, a drive colon) or name nothing (empty).
    """
    parsed = urlparse(url)
    if not parsed.path:
        return "repo"
    name = parsed.path.rstrip("/").rsplit("/", 1)[-1].removesuffix(".git")
    if not name.strip(". ") or any(c in name for c in "/\\:"):
        raise GitHubError("refusing the repository URL: its last segment is not a usable name")
    return name


def _normalise_url(url: str) -> str:
    return url.strip().rstrip("/").removesuffix(".git")


def _ensure_cloned(url: str, cache_dir: Path) -> Path:
    """Clone or refresh `url` into a cache directory and return the path."""
    _refuse_unsafe(url)
    name = _repo_name_from_url(url)
    # `INC9F-SEC-F1`: the last segment alone collides (`alice/tools`, `bob/tools`),
    # and a cache hit then shows whichever remote the mirror holds.
    target = cache_dir / f"{name}-{hashlib.sha256(_normalise_url(url).encode('utf-8')).hexdigest()[:12]}"
    # `--mirror` makes a BARE repository: `HEAD` is a file and there is no `.git`.
    if (target / "HEAD").is_file():
        try:
            _run_git(target, ["fetch", "--all"], check=False)
        except GitHubError:
            # `INC9F-SEC-F3`: a stale mirror beats no map, as a failed fetch already does.
            pass
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(
            ["git", "clone", "--mirror", "--", url, str(target)],
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            timeout=_CLONE_TIMEOUT,
        )
    except FileNotFoundError as exc:
        raise GitHubError("git CLI not found") from exc
    except subprocess.TimeoutExpired:
        # No chaining: the timeout carries the argv, and the URL may hold a token.
        raise GitHubError(f"could not clone '{name}': timed out") from None
    if result.returncode != 0:
        # `INC9BC-SEC-F3`, `M2`: the repo's name and one fixed category, never
        # git's own text (the cache path, the URL's credentials).
        category = _failure_category(result.stderr, result.returncode)
        raise GitHubError(f"could not clone '{name}': {category}")
    return target


def _build_graph_from_git(
    cwd: Path,
    display_name: str,
    progress: ProgressCallback | None = None,
) -> Graph:
    """Build a repo Graph from a local git checkout."""
    default = _default_branch(cwd)
    branches = _local_branches(cwd)
    tags = _tags(cwd)

    graph = Graph()
    root_meta = f"ramas {len(branches)} · tags {len(tags)} · default {default}"
    root = Node(id=display_name, ficha=Ficha(title=display_name, meta=root_meta))
    graph.add_node(root)

    total = len(branches[:50])
    if progress:
        progress(0, total, "leyendo ramas")

    for idx, bname in enumerate(branches[:50], 1):
        ahead, behind = _ahead_behind(cwd, default, bname)
        info = _last_commit_info(cwd, bname)
        date_str = ""
        if info.get("date"):
            try:
                dt = datetime.fromisoformat(info["date"].replace("Z", "+00:00"))
                date_str = dt.astimezone(timezone.utc).strftime("%Y-%m-%d")
            except ValueError:
                date_str = info["date"][:10]

        state = "ok"
        if ahead > 10 or behind > 10:
            state = "risk"

        notes = ""
        if info.get("author"):
            notes = f"{info['author']} {date_str}".strip()

        node = Node(
            id=bname,
            ficha=Ficha(
                title=bname,
                meta=f"+{ahead}/-{behind}",
                state=state,
                notes=notes,
                fields={"kind": "branch", "date": date_str},
            ),
        )
        graph.add_node(node)
        graph.add_edge(Edge(parent_id=display_name, child_id=bname))

    # Releases = git tags, rendered on the same time axis.
    for tname in tags[:20]:
        info = _last_commit_info(cwd, tname)
        date_str = ""
        if info.get("date"):
            try:
                dt = datetime.fromisoformat(info["date"].replace("Z", "+00:00"))
                date_str = dt.astimezone(timezone.utc).strftime("%Y-%m-%d")
            except ValueError:
                date_str = info["date"][:10]
        node = Node(
            id=f"release:{tname}",
            ficha=Ficha(
                title=tname,
                meta="release",
                notes=info.get("subject", ""),
                fields={"kind": "release", "date": date_str},
            ),
        )
        graph.add_node(node)
        graph.add_edge(Edge(parent_id=display_name, child_id=node.id))

    if progress:
        progress(total, total, "listo")

    return graph


class GitHubConnector:
    """Fetch repository metadata and return a Graph representing branches as lanes."""

    def __init__(self, repo: str, cache_dir: Path | str | None = None):
        self.repo = repo
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "mapper" / "repos"
        self.cache_dir = Path(cache_dir)

    def _gh(self, args: list[str]) -> dict | list:
        cmd = ["gh"] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
                timeout=_SUBPROCESS_TIMEOUT,
            )
        except subprocess.CalledProcessError as exc:
            category = _failure_category(exc.stderr, exc.returncode)
            raise GitHubError(f"could not query '{self.repo}': {category}") from None
        except FileNotFoundError as exc:
            raise GitHubError("gh CLI not found") from exc
        except subprocess.TimeoutExpired:
            raise GitHubError(f"could not query '{self.repo}': timed out") from None
        return json.loads(result.stdout or "{}")

    def _fetch_gh(self, progress: ProgressCallback | None = None) -> Graph:
        parts = self.repo.split("/")
        if len(parts) != 2:
            raise GitHubError(f"repo must be owner/name, got {self.repo}")
        owner, name = parts
        # `INC9F-SEC-F4`: both segments go into `gh api` paths; `.` and `..` are path
        # steps and `?`, `#`, `%` would add a query or a fragment.
        if (not _OWNER_RE.fullmatch(owner) or not _NAME_RE.fullmatch(name)
                or name in (".", "..")):
            raise GitHubError("refusing the repository: owner/name has characters GitHub does not allow")

        repo_info = self._gh(["repo", "view", self.repo, "--json", "name,defaultBranchRef"])
        default_branch = repo_info.get("defaultBranchRef", {}).get("name", "main")

        branches = self._gh([
            "api", f"repos/{owner}/{name}/branches?per_page=20",
        ])
        if not isinstance(branches, list):
            raise GitHubError("unexpected response from gh api branches")

        tags = self._gh([
            "api", f"repos/{owner}/{name}/tags?per_page=20",
        ])
        if not isinstance(tags, list):
            tags = []

        graph = Graph()
        root = Node(id=self.repo, ficha=Ficha(title=self.repo, meta="repo"))
        graph.add_node(root)

        total = len(branches)
        if progress:
            progress(0, total, "leyendo ramas")

        for idx, branch in enumerate(branches, 1):
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

            date_str = ""
            if commit and isinstance(commit, dict):
                raw = commit.get("commit", {}).get("committer", {}).get("date", "")
                if raw:
                    date_str = raw[:10]

            node = Node(
                id=bname,
                ficha=Ficha(
                    title=bname,
                    meta=f"+{ahead}/-{behind}",
                    state=state,
                    notes=f"CI: {ci or 'unknown'}",
                    fields={"kind": "branch", "date": date_str},
                ),
            )
            graph.add_node(node)
            graph.add_edge(Edge(parent_id=self.repo, child_id=bname))
            if progress:
                progress(idx, total, "calculando métricas")

        for idx, tag in enumerate(tags, 1):
            tname = tag.get("name", f"tag-{idx}")
            raw = tag.get("commit", {}).get("url", "")
            date_str = ""
            if raw:
                try:
                    commit_data = self._gh(["api", raw])
                    date_str = (
                        commit_data.get("commit", {})
                        .get("committer", {})
                        .get("date", "")[:10]
                    )
                except GitHubError:
                    pass
            node = Node(
                id=f"release:{tname}",
                ficha=Ficha(
                    title=tname,
                    meta="release",
                    fields={"kind": "release", "date": date_str},
                ),
            )
            graph.add_node(node)
            graph.add_edge(Edge(parent_id=self.repo, child_id=node.id))

        return graph

    def fetch(self, progress: ProgressCallback | None = None) -> Graph:
        _refuse_unsafe(self.repo)
        if _is_local_path(self.repo):
            cwd = Path(self.repo).expanduser().resolve()
            return _build_graph_from_git(cwd, cwd.name, progress=progress)
        if _is_url(self.repo):
            cwd = _ensure_cloned(self.repo, self.cache_dir)
            return _build_graph_from_git(cwd, _repo_name_from_url(self.repo), progress=progress)
        return self._fetch_gh(progress=progress)
