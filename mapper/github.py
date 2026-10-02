"""Read-only repo-to-map adapter: local git path, remote URL, or GitHub owner/name.

Priority:
  1. Local filesystem path that points at a git repo -> read with `git` commands.
  2. A URL on the closed allow-list (`https://host[:port]/path`, `git@host:path`; see `_is_url`)
     -> clone to a local cache and read with `git`.
  3. `owner/name` -> use the authenticated `gh` CLI (existing behaviour) with optional
     local clone/cache if the repo is public and git is available.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlparse

from .darkside import plain
from .model import Edge, Ficha, Graph, Node
from .osopen import safe_local_path


ProgressCallback = Callable[[int, int, str], None]


class GitHubError(Exception):
    pass


class GitHubTimeout(GitHubError):
    """A process ran out of its budget.  The typed signal `_refresh_mirror` reads
    (`INC9G-CR-F5`): a message suffix is a protocol any other error could join."""


# `S1` (operator, Round 8): a typed repo URL is accepted only as one of these two shapes, and
# every other text is refused.  The allow-list lives here and nowhere else: `fetch`,
# `_ensure_cloned` and `painted_repo` all read `_is_url`.
#   https://host[:port]/seg(/seg)*[/]   host: ASCII letters, digits, `-` and `.`, starts with a
#                                        letter or digit; port: digits; no userinfo, no IPv6
#   git@host:seg(/seg)*[/]              the same host and segments; no port
# seg: one or more of `[A-Za-z0-9._~-]`, never `.` or `..`, never starting with `-`.  Anything else
# (`?`, `#`, `%`, `@`, whitespace, `\`, `//` in the path, `http://`, other schemes) is outside.
_HOST = r"[A-Za-z0-9][A-Za-z0-9.-]*"
_SEG = r"[A-Za-z0-9._~-]+"
_HTTPS_URL = re.compile(rf"https://{_HOST}(?::[0-9]+)?(?P<path>(?:/{_SEG})+/?)")
_SCP_URL = re.compile(rf"git@{_HOST}:(?P<path>{_SEG}(?:/{_SEG})*/?)")
_UNSUPPORTED = ("refusing the repository: use https://host/path, git@host:path, owner/name "
                "or a local folder")
UNRECOGNISED = "(unrecognised URL)"


def _is_url(value: str) -> bool:
    match = _HTTPS_URL.fullmatch(value) or _SCP_URL.fullmatch(value)
    if match is None:
        return False
    return all(seg not in (".", "..") and not seg.startswith("-")
               for seg in match.group("path").strip("/").split("/"))


def _is_owner_name(value: str) -> bool:
    parts = value.split("/")
    return (len(parts) == 2 and bool(_OWNER_RE.fullmatch(parts[0]))
            and bool(_NAME_RE.fullmatch(parts[1])) and parts[1] not in (".", ".."))


def _classify(spec: str) -> str:
    """`INC9K-CR-F2`: the ONE decision for a typed repo, read by `fetch` and `painted_repo` so
    what is painted is exactly what `fetch` takes.  Returns "local", "url" or "gh", or raises
    `GitHubError` with the refusal (nothing is echoed)."""
    _refuse_unsafe(spec)
    if _is_local_path(spec):
        return "local"
    if _is_url(spec):
        _repo_name_from_url(spec)
        return "url"
    if _is_owner_name(spec):
        return "gh"
    raise GitHubError(_UNSUPPORTED)


def source_kind(spec: str) -> str:
    """`INC9M-CR-F8`: the public name of the one decision (`"local"`, `"url"` or `"gh"`); raises
    `GitHubError` for a refused text.  The badge reads this, not the private `_classify`."""
    return _classify(spec)


def painted_repo(spec: str) -> str:
    """`S1` + `R1`: the typed text, only when `fetch` would take it; any other text (a credential
    form included) is never painted, whatever it holds."""
    try:
        _classify(spec)
    except GitHubError:
        return UNRECOGNISED
    return spec


def _is_local_path(value: str) -> bool:
    """Total: no typed text makes it raise.  `S1` applied to paths: `safe_local_path` accepts only a
    drive-absolute or a relative path and decides on the string, so a UNC, device or NT-namespace
    text is refused BEFORE any filesystem call (on Windows an SMB lookup on the UI thread).

    `INC9L-CR-F4` (accepted): the `OSError` catch is broad because the ruling wants a total
    predicate; a local folder that cannot be read may fall through to the `owner/name` path."""
    path = safe_local_path(value)
    if path is None:
        return False
    try:
        return path.is_dir() and (path / ".git").is_dir()
    except (RuntimeError, OSError, ValueError):
        return False


_SUBPROCESS_TIMEOUT = 30
# A mirror clone moves a whole history, so it gets a longer budget than a read.
_CLONE_TIMEOUT = 120

_TIMED_OUT = "timed out"

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
        "terminal prompts disabled", "permission denied (publickey", "invalid username or password",
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
# `INC9F-CR-F6`: the fixed set, declared once: the four stderr categories and the
# timeout (`unknown (exit N)` is the open remainder and carries its own code).
CATEGORIES = tuple(name for name, _ in _CATEGORY_MARKERS) + (_TIMED_OUT,)
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
    if _TRANSPORT_HELPER_RE.match(spec.lstrip()):
        raise GitHubError("refusing the repository: transport helpers are not accepted")


def _git_env() -> dict[str, str]:
    """The environment of every `git` call (`INC9F-CR` item 13): English stderr, so
    `_failure_category` matches on a localised git, and no credential prompt, so a
    private HTTPS repo fails instead of hanging.  Built per call, not at import: a
    snapshot would pin the HOME the process started with."""
    return {**os.environ, "LC_ALL": "C", "GIT_TERMINAL_PROMPT": "0"}


def _run_git(
    cwd: Path,
    args: list[str],
    check: bool = True,
    timeout: int = _SUBPROCESS_TIMEOUT,
) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["git", "-C", str(cwd)] + args,
            capture_output=True,
            text=True,
            check=check,
            encoding="utf-8",
            timeout=timeout,
            env=_git_env(),
        )
    except FileNotFoundError as exc:
        raise GitHubError("git CLI not found") from exc
    except subprocess.CalledProcessError as exc:
        category = _failure_category(exc.stderr, exc.returncode)
        raise GitHubError(f"git {args[0]} failed: {category}") from None
    except subprocess.TimeoutExpired:
        raise GitHubTimeout(f"git {args[0]} failed: {_TIMED_OUT}") from None


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
    # `INC9L-CR-F2`: `git@host:path` has no URL path for `urlparse` (`git@h:r` reads as a scheme and
    # a path-less URL, which refused the very form the refusal sentence tells the user to type).
    scp = _SCP_URL.fullmatch(url)
    path = scp.group("path") if scp else urlparse(url).path
    if not path:
        return "repo"
    name = path.rstrip("/").rsplit("/", 1)[-1].removesuffix(".git")
    if not name.strip(". ") or any(c in name for c in "/\\:"):
        raise GitHubError("refusing the repository URL: its last segment is not a usable name")
    return name


def _normalise_url(url: str) -> str:
    return url.strip().rstrip("/").removesuffix(".git")


def _refresh_mirror(target: Path) -> str:
    """Fetch into a cached mirror; "" when fresh, else the fixed category it is stale for.

    `INC9F-CR-F4`: a timeout or a failed fetch is not a failed connect: the mirror
    still holds what the last connect saw.  A refresh moves history, so it gets the
    clone's budget, not a read's.
    """
    # `INC9G-SEC-F2`: `--prune`, or a branch the remote deleted stays in the mirror and is
    # shown as live.
    try:
        result = _run_git(target, ["fetch", "--prune", "--all"], check=False, timeout=_CLONE_TIMEOUT)
    except GitHubTimeout:
        return _TIMED_OUT
    if result.returncode != 0:
        return _failure_category(result.stderr, result.returncode)
    return ""


def _mirror_dir(cache_dir: Path, name: str, form: str) -> Path:
    return cache_dir / f"{name}-{hashlib.sha256(form.encode('utf-8')).hexdigest()[:12]}"


def _is_mirror_of(mirror: Path, url: str) -> bool:
    """Whether the mirror's `origin` is the URL as typed (a trailing `/` aside)."""
    result = _run_git(mirror, ["config", "--get", "remote.origin.url"], check=False)
    return result.returncode == 0 and result.stdout.strip().rstrip("/") == url.rstrip("/")


def _ensure_cloned(
    url: str, cache_dir: Path, on_stale: Callable[[str], None] | None = None,
) -> Path:
    """Clone or refresh `url` into a cache directory and return the path.

    `on_stale` is told the category when a cache hit could not be refreshed.

    `S1`: a text outside the allow-list is refused here too, before any process (`INC9J-SEC-F2`),
    so a direct call is no weaker than `GitHubConnector.fetch`; `INC9I-CR-F3` still pins `fetch`
    as the only production caller.
    """
    _refuse_unsafe(url)
    if not _is_url(url):
        raise GitHubError(_UNSUPPORTED)
    name = _repo_name_from_url(url)
    # `INC9F-SEC-F1`: the last segment alone collides (`alice/tools`, `bob/tools`),
    # and a cache hit then shows whichever remote the mirror holds.
    target = _mirror_dir(cache_dir, name, _normalise_url(url))
    # `--mirror` makes a BARE repository: `HEAD` is a file and there is no `.git`.
    if (target / "HEAD").is_file() and not _is_mirror_of(target, url):
        # `INC9G-SEC-F1`: one normal form, two remotes (`r` and `r.git` on a plain server, a
        # hash collision, a tampered cache): the mirror there is not this URL's.  This URL
        # gets its own directory, keyed on the form as typed; if that holds another remote
        # too, the connect is refused.  The key never reads the mirror's contents otherwise.
        # `INC9H-SEC-F1`: the key lives in a space of its own.  Without the prefix a URL with
        # no `.git` keyed the fallback on the very string the primary key is (`tools` after
        # `tools.git`), found the same foreign mirror again and refused for good.
        target = _mirror_dir(cache_dir, name, "as-typed:" + url.rstrip("/"))
        if (target / "HEAD").is_file() and not _is_mirror_of(target, url):
            raise GitHubError("refusing the cached copy: it belongs to another repository")
    if (target / "HEAD").is_file():
        stale = _refresh_mirror(target)
        if stale and on_stale is not None:
            on_stale(stale)
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
            env=_git_env(),
        )
    except FileNotFoundError as exc:
        raise GitHubError("git CLI not found") from exc
    except subprocess.TimeoutExpired:
        # No chaining: the timeout carries the argv, and the URL may hold a token.
        raise GitHubError(f"could not clone '{plain(name)}': {_TIMED_OUT}") from None
    if result.returncode != 0:
        # `INC9BC-SEC-F3`, `M2`: the repo's name and one fixed category, never
        # git's own text (the cache path, the URL's credentials).
        category = _failure_category(result.stderr, result.returncode)
        raise GitHubError(f"could not clone '{plain(name)}': {category}")
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
    root_meta = f"branches {len(branches)} · tags {len(tags)} · default {default}"
    root = Node(id=display_name, ficha=Ficha(title=display_name, meta=root_meta))
    graph.add_node(root)

    total = len(branches[:50])
    if progress:
        progress(0, total, "reading branches")

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
        progress(total, total, "ready")

    return graph


class GitHubConnector:
    """Fetch repository metadata and return a Graph representing branches as lanes."""

    def __init__(self, repo: str, cache_dir: Path | str | None = None):
        self.repo = repo
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "mapper" / "repos"
        self.cache_dir = Path(cache_dir)
        # The category a cache hit could not be refreshed for ("" = fresh): the
        # screen says so, because the map it paints is the cached copy.
        self.stale = ""

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
                # `INC9G-SEC-F5`: never wait on a prompt (`git`'s own twin is `_git_env`).
                env={**os.environ, "GH_PROMPT_DISABLED": "1"},
            )
        except subprocess.CalledProcessError as exc:
            category = _failure_category(exc.stderr, exc.returncode)
            raise GitHubError(f"could not query '{self.repo}': {category}") from None
        except FileNotFoundError as exc:
            raise GitHubError("gh CLI not found") from exc
        except subprocess.TimeoutExpired:
            raise GitHubError(f"could not query '{self.repo}': {_TIMED_OUT}") from None
        return json.loads(result.stdout or "{}")

    def _fetch_gh(self, progress: ProgressCallback | None = None) -> Graph:
        # `INC9F-SEC-F4`: both segments go into `gh api` paths; `.` and `..` are path
        # steps and `?`, `#`, `%` would add a query or a fragment.  `S1`: `fetch` has refused
        # a malformed spec already, with the one sentence; this is the same check, kept.
        # `INC9K-SEC-F2`: the names the API returns are data too: each is one encoded segment.
        if not _is_owner_name(self.repo):
            raise GitHubError(_UNSUPPORTED)
        owner, name = self.repo.split("/")

        repo_info = self._gh(["repo", "view", self.repo, "--json", "name,defaultBranchRef"])
        default = repo_info.get("defaultBranchRef", {}).get("name", "main")
        # `INC9L-SEC-F3`: `.` and `..` are path steps, which `quote` leaves as they are.
        if default in (".", ".."):
            raise GitHubError("unexpected response from gh repo view")
        qdefault = quote(default, safe="")

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
            progress(0, total, "reading branches")

        for idx, branch in enumerate(branches, 1):
            bname = branch["name"]
            if bname in (".", ".."):
                # `INC9M-CR-F5`: a skipped branch still counts, so progress reaches the total.
                if progress:
                    progress(idx, total, "computing metrics")
                continue
            qname = quote(bname, safe="")
            # ahead/behind against default branch
            comparison = self._gh([
                "api", f"repos/{owner}/{name}/compare/{qdefault}...{qname}",
            ])
            ahead = comparison.get("ahead_by", 0)
            behind = comparison.get("behind_by", 0)

            # CI verdict from latest commit check-runs
            ci = ""
            # `INC9M-SEC-F3`: bound per iteration, so a failing lookup neither leaves it unbound
            # nor keeps the previous branch's date.
            commit: dict = {}
            try:
                commit = self._gh([
                    "api", f"repos/{owner}/{name}/commits/{qname}",
                ])
                sha = commit.get("sha", "")
                if sha and sha not in (".", ".."):
                    checks = self._gh([
                        "api", f"repos/{owner}/{name}/commits/{quote(sha, safe='')}/check-runs",
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
                progress(idx, total, "computing metrics")

        for idx, tag in enumerate(tags, 1):
            tname = tag.get("name", f"tag-{idx}")
            # `INC9L-SEC-F4`: the API's own `commit.url` is data and would be handed to `gh api`
            # as the whole request (a foreign host, a `-X` flag); the path is built from the sha.
            sha = tag.get("commit", {}).get("sha", "")
            date_str = ""
            if sha and sha not in (".", ".."):
                try:
                    commit_data = self._gh(
                        ["api", f"repos/{owner}/{name}/commits/{quote(sha, safe='')}"])
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

    def _mark_stale(self, category: str) -> None:
        self.stale = category

    def fetch(self, progress: ProgressCallback | None = None) -> Graph:
        # `INC9G-CR-F7`: a connector that connects twice must not carry the first
        # connect's stale category into the second.
        self.stale = ""
        kind = _classify(self.repo)
        if kind == "local":
            local = safe_local_path(self.repo)
            if local is None:
                raise GitHubError(_UNSUPPORTED)
            cwd = local.resolve()
            return _build_graph_from_git(cwd, cwd.name, progress=progress)
        if kind == "url":
            cwd = _ensure_cloned(self.repo, self.cache_dir, on_stale=self._mark_stale)
            return _build_graph_from_git(cwd, _repo_name_from_url(self.repo), progress=progress)
        return self._fetch_gh(progress=progress)
