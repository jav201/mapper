"""The identity reader and the hardened read-only git allowlist (R11/R20/R27).

Reviewer identity is read from git config -- repo-local first, then global --
and nothing else about the operator is consulted.  The ONLY subprocesses the
ReqHarness core may ever run are the read-only allowlist rows below, reduced
and hardened per round-2 ruling R20 and round-3 ruling R27; the former
``git log`` row (the committer-vs-reviewer email warning) is DEFERRED (B-124)
and is not here:

| Command | Use | Runs in the audit path? |
|---|---|---|
| ``git rev-parse --show-toplevel`` | repo-root discovery (D13) | yes |
| ``git rev-parse HEAD`` | baseline commit SHA | yes |
| ``git config --get user.name`` / ``user.email`` | identity (repo-local then global) | yes |
| ``git --no-optional-locks status --porcelain`` | baseline dirty flag -- ONLY inside ``Baseline.create`` | NO (R27a) |

Every call is an argv list with ``shell=False`` and a 10 s timeout, prefixed
``<abs git> --no-pager -c core.fsmonitor=false -c core.hooksPath=<os.devnull>
-C <repo>`` -- never ``cwd=<repo>`` -- over an env carrying
``GIT_OPTIONAL_LOCKS=0`` as the ONLY ``GIT_*`` key: every other inherited
``GIT_*`` variable (``GIT_DIR``, ``GIT_WORK_TREE``, ``GIT_INDEX_FILE``,
``GIT_COMMON_DIR``, ``GIT_OBJECT_DIRECTORY``, ``GIT_CONFIG*``, ...) is
stripped (F5).  ``git`` is resolved ONCE to an ABSOLUTE path by walking PATH
ourselves: each directory that resolves to the audited repo, the current
working directory, ``.`` or an empty entry is skipped — compared resolved —
then ``git`` plus each PATHEXT extension is tried on Windows (``git`` on
POSIX) and the first existing regular file wins (R27c, F4).  No
``shutil.which`` — before Python 3.12 it searches ``.`` on Windows regardless
of ``NoDefaultCurrentDirectoryInExePath`` — and no process-wide env mutation;
a failed resolution is NOT cached, so repairing PATH is enough (F7).  A
``safe.directory`` refusal -- or ANY git non-zero exit, timeout included --
becomes the named result ``no repo`` (R27d), never a crash; a repo path the
platform refuses to resolve (a NUL byte) lands there too (F6).

Honest ceiling (LLR-RH.4.4): this identity is SELF-CLAIMED and spoofable by
any committer; the chain proves integrity and approval, not authorship.  The
residual layer-3 risk -- a full consistent rewrite of chain + every review by
a writer with repo access -- is answered by B-122's strong mode (signed
commits), a named follow-up, with git anchoring of genesis also follow-up.
Stated residual: ``git status`` trusts the repo's ``.git/config`` (a repo's
``filter.<name>.clean`` can still run on it) -- which is exactly why the
status row is Baseline.create-only and never part of ``--audit`` (R27a/b).
"""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

#: The named result for "not a usable repository" (R27d): a ``safe.directory``
#: refusal, any other git non-zero exit, a timeout, or no git on PATH.
NO_REPO = "no repo"

#: The subprocess timeout of every allowlist call, in seconds (R20).
_TIMEOUT = 10

#: The exact allowlist, as argv tails after the hardened prefix.  A tail not
#: in this set is a programmer error and is refused loudly at the call site;
#: the source census in ``tests/test_reqharness_identity.py`` derives the same
#: set from the shipped AST so the guard cannot drift silently.
_ALLOWED_TAILS = (
    ("rev-parse", "--show-toplevel"),
    ("rev-parse", "HEAD"),
    ("config", "--get", "user.name"),
    ("config", "--get", "user.email"),
    ("--no-optional-locks", "status", "--porcelain"),
)

#: ``git`` resolved once per audited repo: ``<repo key> -> absolute path``.
#: Only SUCCESSFUL resolutions are stored — a failed one must not be
#: cached, so repairing PATH is enough without a new process (F7).
_GIT_CACHE: dict[str, str] = {}


@dataclass(frozen=True)
class Identity:
    """The reviewer identity from git config; empty strings when unset."""

    name: str
    email: str


def _resolve_path(path: Path) -> Path | None:
    """``path`` expanded and resolved — None when the platform refuses
    (a NUL byte, a missing drive, ...): such a path can never supply
    ``git`` and never crashes the caller (F6)."""
    try:
        return path.expanduser().resolve()
    except (OSError, ValueError, RuntimeError):
        return None


def _resolve_git(repo: Path) -> str | None:
    """Resolve ``git`` ONCE to an absolute path, excluding ``repo`` (R27c).
    A repo path the platform refuses to resolve degrades to ``no repo``,
    never a crash (F6); a failed resolution is NOT cached (F7)."""
    key_path = _resolve_path(repo)
    if key_path is None:
        return None
    key = str(key_path)
    if key not in _GIT_CACHE:
        found = _which_git(repo)
        if found is not None:
            _GIT_CACHE[key] = found
    return _GIT_CACHE.get(key)


def _which_git(exclude: Path) -> str | None:
    """Resolve ``git`` by walking PATH ourselves (F4) — never
    ``shutil.which`` (before Python 3.12 it searches ``.`` on Windows
    regardless of ``NoDefaultCurrentDirectoryInExePath``) and never a
    process-wide env mutation.

    Each directory that resolves to the audited repo, the current working
    directory, ``.`` or an empty entry is skipped — compared resolved — then
    ``git`` plus each PATHEXT extension is tried on Windows (plain ``git``
    on POSIX); the first existing regular file wins.  A ``git.exe`` planted
    in the repo's cwd can therefore never win, however PATH is arranged
    (R27c).
    """
    target_path = _resolve_path(exclude)
    if target_path is None:
        return None
    target = os.path.normcase(str(target_path))
    cwd_path = _resolve_path(Path.cwd())
    cwd = os.path.normcase(str(cwd_path)) if cwd_path is not None else None
    if os.name == "nt":
        # An EMPTY (or unset) PATHEXT falls back to the platform default —
        # with "" the split below would try no names at all.
        pathext = os.environ.get("PATHEXT") or ".COM;.EXE;.BAT;.CMD"
        names = [f"git{ext}" for ext in pathext.split(";") if ext]
    else:
        names = ["git"]
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not entry:
            continue  # an empty entry means the cwd — never supplies git
        resolved = _resolve_path(Path(entry))
        if resolved is None:
            continue
        norm = os.path.normcase(str(resolved))
        if norm == target or norm.startswith(target + os.sep):
            continue  # inside the audited repo — never supplies git
        if norm == cwd:
            continue  # the current working directory — never supplies git
        for name in names:
            candidate = resolved / name
            if candidate.is_file():
                return str(candidate)
    return None


def _git_env() -> dict[str, str]:
    """The environment of every allowlist call (R20/F5): EVERY inherited
    ``GIT_*`` variable is stripped — ``GIT_DIR``, ``GIT_WORK_TREE``,
    ``GIT_INDEX_FILE``, ``GIT_COMMON_DIR``, ``GIT_OBJECT_DIRECTORY``,
    ``GIT_CONFIG*``, ... — then ``GIT_OPTIONAL_LOCKS=0`` is set, the only
    ``GIT_*`` key the child ever sees."""
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GIT_")
    }
    env["GIT_OPTIONAL_LOCKS"] = "0"
    return env


def _run_git(repo: Path, tail: list[str]) -> str | None:
    """Run one allowlist call; stdout stripped on exit 0, None on ANY failure.

    None -- never an exception -- is what the named ``no repo`` result is
    built from (R27d).
    """
    if tuple(tail) not in _ALLOWED_TAILS:
        raise ValueError(f"git call outside the read-only allowlist: {tail!r}")
    exe = _resolve_git(repo)
    if exe is None:
        return None
    argv = [
        exe,
        "--no-pager",
        "-c",
        "core.fsmonitor=false",
        "-c",
        f"core.hooksPath={os.devnull}",
        "-C",
        str(repo),
        *tail,
    ]
    try:
        result = subprocess.run(
            argv,
            shell=False,
            timeout=_TIMEOUT,
            env=_git_env(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def repo_root(repo: Path) -> str:
    """The absolute toplevel of the work tree containing ``repo`` (D13), or
    the named result ``no repo`` (R27d)."""
    found = _run_git(repo, ["rev-parse", "--show-toplevel"])
    return found if found else NO_REPO


def head_commit(repo: Path) -> str:
    """The current HEAD commit SHA, or the named result ``no repo``."""
    found = _run_git(repo, ["rev-parse", "HEAD"])
    return found if found else NO_REPO


def read(repo: Path) -> Identity:
    """Reviewer identity: repo-local ``user.name``/``user.email``, falling
    back to global config -- git's own precedence, one ``config --get`` per
    field.  Unset fields come back as empty strings; any failure degrades to
    an empty identity, never a crash."""
    name = _run_git(repo, ["config", "--get", "user.name"])
    email = _run_git(repo, ["config", "--get", "user.email"])
    return Identity(name=name or "", email=email or "")


def status_porcelain(repo: Path) -> str:
    """The dirty-flag source: ``status --porcelain`` under ``--no-optional-locks``
    and ``GIT_OPTIONAL_LOCKS=0``.  Baseline.create ONLY (R27a) -- ``--audit``
    runs NO ``git status`` at all."""
    found = _run_git(repo, ["--no-optional-locks", "status", "--porcelain"])
    return NO_REPO if found is None else found
