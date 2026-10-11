"""LLR-RH.7.3 / LLR-RH.4.4 / R20 / R27a-d — the identity reader and the
hardened read-only git allowlist.

Node names per the executed verification in
`.dev-flow/2026-10-11-reqharness-batch/01-requirements.md`: the repo-local-
then-global precedence node, the R27c resolution/argv-census node, the R27d
`safe.directory` node — plus the R20/R27 fixtures (fsmonitor sentinel,
`.git/index` byte-identical, the source census) and the code-review
follow-up nodes (RHFIX23 F4–F7).  Identity is injected
through a temp repo and a temp global config file; the operator's real git
config is never read for a fixture value nor written at all.
"""
from __future__ import annotations

import ast
import hashlib
import os
import subprocess
from pathlib import Path

import pytest

from mapper.reqharness import identity

#: The R20/R27 allowlist, as argv tails after the hardened prefix.  The source
#: census arm below derives the shipped set from the AST and compares against
#: THIS table — the test is the oracle, not the module.
ALLOWED_TAILS = {
    ("rev-parse", "--show-toplevel"),
    ("rev-parse", "HEAD"),
    ("config", "--get", "user.name"),
    ("config", "--get", "user.email"),
    ("--no-optional-locks", "status", "--porcelain"),
}


def _fixture_env(tmp_path: Path) -> dict[str, str]:
    """The env of the FIXTURE-CREATION subprocesses only: GIT_CONFIG_GLOBAL at
    a temp file, so `git init` / `git config` never touch the operator's real
    git config.  The module under test strips GIT_CONFIG* (R20), so this file
    never reaches the allowlist calls."""
    return {**os.environ, "GIT_CONFIG_GLOBAL": str(tmp_path / "global.gitconfig")}


def _git(repo: Path, *args: str, env: dict[str, str]) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, f"git {' '.join(args)}: {result.stderr}"
    return result.stdout


def _make_repo(tmp_path: Path) -> Path:
    """A temp repo with one tracked file, one commit and repo-local identity,
    created entirely inside the fixture env."""
    repo = tmp_path / "work"
    repo.mkdir()
    env = _fixture_env(tmp_path)
    init = subprocess.run(
        ["git", "init", "-q", str(repo)],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert init.returncode == 0, init.stderr
    _git(repo, "config", "user.name", "Local Person", env=env)
    _git(repo, "config", "user.email", "local@example.test", env=env)
    (repo / "tracked.txt").write_text("tracked\n", encoding="utf-8")
    _git(repo, "add", "tracked.txt", env=env)
    _git(repo, "commit", "-q", "-m", "init", env=env)
    return repo


def test_identity_reader_repo_local_then_global(tmp_path, monkeypatch):
    """LLR-RH.4.4/7.3: identity is repo-local `git config` first, global
    fallback second.  The injected global config reaches the module's git
    calls through HOME (GIT_CONFIG* is stripped from them, R20); the fixture
    env's GIT_CONFIG_GLOBAL exists so the repo creation never touches the
    operator's real config, and nothing here writes to any real config.

    Mutant M-ID1 (read only the global config) reddens the first arm; a
    local-only reader reddens the fallback arm."""
    env = _fixture_env(tmp_path)
    repo = tmp_path / "work"
    repo.mkdir()
    init = subprocess.run(
        ["git", "init", "-q", str(repo)],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert init.returncode == 0, init.stderr
    _git(repo, "config", "user.name", "Local Person", env=env)
    _git(repo, "config", "user.email", "local@example.test", env=env)

    home = tmp_path / "home"
    home.mkdir()
    (home / ".gitconfig").write_text(
        '[user]\n\tname = Global Person\n\temail = global@example.test\n',
        encoding="utf-8",
    )
    monkeypatch.setitem(os.environ, "HOME", str(home))
    monkeypatch.setitem(os.environ, "USERPROFILE", str(home))

    # Repo-local beats the injected global config.
    assert identity.read(repo) == identity.Identity(
        "Local Person", "local@example.test"
    )

    # No repo-local config -> the global fallback serves the identity.
    _git(repo, "config", "--unset", "user.name", env=env)
    _git(repo, "config", "--unset", "user.email", env=env)
    assert identity.read(repo) == identity.Identity(
        "Global Person", "global@example.test"
    )


def test_git_resolution_absolute_and_path_pinned(tmp_path, monkeypatch):
    """LLR-RH.7.3 (R27b/c): `git` resolves ONCE to an absolute path over a
    PATH that excludes the audited repo, so a planted executable in the
    repo's cwd never wins; every recorded argv carries the absolute
    executable, `--no-pager`, the two `-c` pins, the `-C <repo>` form (never
    `cwd=<repo>`), `shell=False`, the 10 s timeout and the stripped env with
    `GIT_OPTIONAL_LOCKS=0`.  The audit path runs NO `git status` (R27a).

    Mutant M-ID2 (bare/relative resolution, or honouring the planted
    executable) reddens the executable assertions."""
    repo = _make_repo(tmp_path)

    # A hostile executable planted in the repo's cwd, made visible by putting
    # the repo FIRST on PATH — resolution must still find the real git.
    if os.name == "nt":
        planted = repo / "git.cmd"
        planted.write_text("@echo off\r\necho planted\r\n", encoding="utf-8")
    else:
        planted = repo / "git"
        planted.write_text("#!/bin/sh\necho planted\n", encoding="utf-8")
        planted.chmod(0o755)
    monkeypatch.setitem(
        os.environ, "PATH", str(repo) + os.pathsep + os.environ.get("PATH", "")
    )
    # Inherited git state that MUST NOT reach the child (R20; F5 widens the
    # strip to EVERY GIT_* key — GIT_DIR/GIT_WORK_TREE/GIT_CONFIG* and also
    # GIT_INDEX_FILE / GIT_COMMON_DIR / GIT_OBJECT_DIRECTORY).
    monkeypatch.setitem(os.environ, "GIT_DIR", str(repo / ".git"))
    monkeypatch.setitem(os.environ, "GIT_WORK_TREE", str(repo))
    monkeypatch.setitem(os.environ, "GIT_INDEX_FILE", str(repo / ".git" / "index"))
    monkeypatch.setitem(os.environ, "GIT_COMMON_DIR", str(repo / ".git"))
    monkeypatch.setitem(
        os.environ, "GIT_OBJECT_DIRECTORY", str(repo / ".git" / "objects")
    )
    monkeypatch.setitem(
        os.environ, "GIT_CONFIG_GLOBAL", str(tmp_path / "injected.gitconfig")
    )

    calls: list[tuple[list[str], dict]] = []
    real_run = subprocess.run

    def recorder(*args, **kwargs):
        argv = list(args[0] if args else kwargs["args"])
        calls.append((argv, kwargs))
        return real_run(*args, **kwargs)

    monkeypatch.setattr(subprocess, "run", recorder)

    root = identity.repo_root(repo)
    head = identity.head_commit(repo)
    who = identity.read(repo)
    assert Path(root).resolve() == repo.resolve()
    assert len(head) == 40
    assert who.name == "Local Person"

    assert calls, "the recorder saw no subprocess: the argv census is vacuous"
    executables = {argv[0] for argv, _ in calls}
    assert len(executables) == 1, f"git resolved more than once: {executables}"
    (exe,) = executables
    assert os.path.isabs(exe), f"executable is not absolute: {exe!r}"
    assert Path(exe).resolve() != planted.resolve(), (
        "resolution honoured the executable planted in the repo's cwd (R27c)"
    )
    hooks_pin = f"core.hooksPath={os.devnull}"
    for argv, kwargs in calls:
        assert argv[0] == exe
        assert argv[1] == "--no-pager"
        pairs = list(zip(argv, argv[1:]))
        assert ("-c", "core.fsmonitor=false") in pairs, argv
        assert ("-c", hooks_pin) in pairs, argv
        at = argv.index("-C")
        assert argv[at + 1] == str(repo), argv
        tail = tuple(argv[at + 2 :])
        assert tail in ALLOWED_TAILS, argv
        assert tail != ("--no-optional-locks", "status", "--porcelain"), (
            "the audit path ran git status (R27a)"
        )
        assert kwargs.get("shell") is False, kwargs
        assert kwargs.get("timeout") == 10, kwargs
        assert "cwd" not in kwargs, "git ran with cwd=<repo> (R27)"
        env = kwargs["env"]
        assert env["GIT_OPTIONAL_LOCKS"] == "0", env
        for key in env:
            assert not key.startswith("GIT_") or key == "GIT_OPTIONAL_LOCKS", (
                f"inherited git state reached the child env (F5): {key}"
            )


def test_git_resolution_excludes_repo_and_cwd(tmp_path, monkeypatch):
    """RHFIX F4 (R27c): `git` is resolved by walking the filtered PATH
    ourselves — each directory that resolves to the audited repo, the
    current working directory, `.` or an empty entry is skipped, compared
    resolved — so a planted `git.cmd`/`git.exe` in the repo's cwd can
    never win, even with the repo FIRST on PATH (before Python 3.12
    `shutil.which` searches `.` on Windows regardless of
    `NoDefaultCurrentDirectoryInExePath` — the old mechanism — and the new
    code performs no process-wide env mutation).

    Mutant M-ID3 (let the repo/cwd supply `git`) -> the planted executable
    wins -> this node is RED."""
    repo = _make_repo(tmp_path)

    # A hostile executable planted in the repo's cwd, made visible TWICE:
    # the repo itself is FIRST on PATH, and an EMPTY PATH entry (which
    # means the cwd) sits right behind it.
    if os.name == "nt":
        planted = [repo / "git.cmd", repo / "git.exe"]
        for path in planted:
            path.write_text("@echo off\r\necho planted\r\n", encoding="utf-8")
    else:
        planted = [repo / "git"]
        planted[0].write_text("#!/bin/sh\necho planted\n", encoding="utf-8")
        planted[0].chmod(0o755)
    monkeypatch.chdir(repo)
    monkeypatch.setitem(
        os.environ,
        "PATH",
        os.pathsep.join([str(repo), "", *os.environ.get("PATH", "").split(os.pathsep)]),
    )

    calls: list[tuple[list[str], dict]] = []
    real_run = subprocess.run

    def recorder(*args, **kwargs):
        argv = list(args[0] if args else kwargs["args"])
        calls.append((argv, kwargs))
        return real_run(*args, **kwargs)

    monkeypatch.setattr(subprocess, "run", recorder)

    root = identity.repo_root(repo)
    assert Path(root).resolve() == repo.resolve(), (
        "the planted executable ran: repo-root discovery is broken (R27c)"
    )
    assert calls, "the recorder saw no subprocess: the census is vacuous"
    executables = {argv[0] for argv, _ in calls}
    assert len(executables) == 1, f"git resolved more than once: {executables}"
    (exe,) = executables
    assert os.path.isabs(exe), f"executable is not absolute: {exe!r}"
    exe_resolved = Path(exe).resolve()
    assert exe_resolved not in {p.resolve() for p in planted}, (
        "resolution honoured the executable planted in the repo's cwd (F4)"
    )
    assert repo.resolve() not in exe_resolved.parents, (
        "the resolved executable lives inside the audited repo (F4)"
    )


def test_windows_resolution_skips_extensionless_git(tmp_path, monkeypatch):
    """Reviewed nit (b): on Windows `_which_git` tries ONLY `git` + the
    PATHEXT extensions — never an extensionless `git` — so a planted
    extensionless file ahead of the real git on PATH can never win.
    (POSIX tries exactly `git`, so the arm is Windows-only.)"""
    if os.name != "nt":
        pytest.skip("the extensionless candidate is a Windows-only shape")
    repo = _make_repo(tmp_path)

    planted_dir = tmp_path / "planted"
    planted_dir.mkdir()
    planted = planted_dir / "git"  # extensionless — must NOT be considered
    planted.write_text("@echo off\r\necho planted\r\n", encoding="utf-8")
    monkeypatch.setitem(
        os.environ,
        "PATH",
        os.pathsep.join(
            [str(planted_dir), *os.environ.get("PATH", "").split(os.pathsep)]
        ),
    )

    root = identity.repo_root(repo)
    assert Path(root).resolve() == repo.resolve(), (
        "resolution honoured the extensionless git planted on PATH (nit b)"
    )
    exe = identity._resolve_git(repo)
    assert exe is not None
    assert Path(exe).resolve() != planted.resolve()


def test_windows_resolution_falls_back_when_pathext_empty(tmp_path, monkeypatch):
    """RHFIX5 L3: on Windows, an EMPTY (or unset) PATHEXT falls back to the
    platform default ``.COM;.EXE;.BAT;.CMD`` — with ``""`` the split would
    try no names at all and resolution would find nothing.  A planted
    ``git.exe`` in a temp PATH dir is found under an empty PATHEXT."""
    if os.name != "nt":
        pytest.skip("PATHEXT is a Windows-only mechanism")
    repo = _make_repo(tmp_path)

    planted_dir = tmp_path / "planted"
    planted_dir.mkdir()
    planted = planted_dir / "git.exe"
    planted.write_bytes(b"MZ\x90\x00planted")
    monkeypatch.setitem(os.environ, "PATHEXT", "")
    monkeypatch.setitem(
        os.environ,
        "PATH",
        os.pathsep.join(
            [str(planted_dir), *os.environ.get("PATH", "").split(os.pathsep)]
        ),
    )

    found = identity._which_git(repo)
    assert found is not None, "empty PATHEXT must fall back to the default"
    assert Path(found).resolve() == planted.resolve()


def test_unresolvable_repo_path_is_named_no_repo_not_a_crash(tmp_path):
    """RHFIX F6: a repo path the platform refuses to resolve (a NUL byte
    makes `Path.resolve()` raise ValueError) degrades to the named
    `no repo` — the resolve() guard catches (OSError, ValueError,
    RuntimeError) — never an exception."""
    bogus = Path(str(tmp_path) + "\x00junk")
    assert identity.repo_root(bogus) == identity.NO_REPO
    assert identity.head_commit(bogus) == identity.NO_REPO
    assert identity.status_porcelain(bogus) == identity.NO_REPO
    assert identity.read(bogus) == identity.Identity("", "")


def test_failed_git_resolution_is_not_cached(tmp_path, monkeypatch):
    """RHFIX F7: a failed git resolution must NOT be cached (`_GIT_CACHE`
    stores no `None`), so repairing PATH is enough without a new process.
    Mutant F7a (cache the failed resolution) -> the repaired call still
    says `no repo` -> this node is RED."""
    repo = _make_repo(tmp_path)
    saved_path = os.environ.get("PATH", "")
    monkeypatch.setitem(os.environ, "PATH", "")
    assert identity.repo_root(repo) == identity.NO_REPO
    monkeypatch.setitem(os.environ, "PATH", saved_path)
    root = identity.repo_root(repo)
    assert root != identity.NO_REPO
    assert Path(root).resolve() == repo.resolve()


def test_safe_directory_refusal_is_named_no_repo_not_a_crash(
    tmp_path, monkeypatch
):
    """R27d / M-AU3: a `safe.directory` refusal — simulated with git's own
    GIT_TEST_ASSUME_DIFFERENT_OWNER, so the refusal and its exit code are
    real, not mocked — yields the named result `no repo` for every
    audit-path query, never an exception.  F5 strips EVERY inherited
    ``GIT_*`` key (this variable included) from the child env, so the
    refusal hook is injected below the `_git_env` seam — the git
    invocation itself is untouched and still exits 128 for real."""
    repo = _make_repo(tmp_path)
    assert identity.repo_root(repo) != identity.NO_REPO, (
        "fixture repo must resolve before the refusal is injected"
    )

    real_git_env = identity._git_env

    def refusal_env() -> dict[str, str]:
        env = real_git_env()
        env["GIT_TEST_ASSUME_DIFFERENT_OWNER"] = "1"
        return env

    monkeypatch.setattr(identity, "_git_env", refusal_env)

    assert identity.repo_root(repo) == identity.NO_REPO
    assert identity.NO_REPO == "no repo"
    assert identity.head_commit(repo) == identity.NO_REPO
    assert identity.status_porcelain(repo) == identity.NO_REPO
    # `git config` is not a repository operation: it still answers, and even
    # where it did not, Identity degradation is a value, not a crash.
    who = identity.read(repo)
    assert isinstance(who, identity.Identity)


def test_fsmonitor_sentinel_absent_after_hardened_calls(tmp_path):
    """R20/R27b: a repo whose `.git/config` sets `core.fsmonitor` to a
    sentinel command keeps the sentinel ABSENT after the hardened calls.
    fsmonitor is only consulted by commands that refresh the index — among
    the allowlist rows that is `status` alone (rev-parse/config never query
    it), which is exactly why the status row is Baseline.create-only
    (R27a) and carries the same pin as every other call.

    Mutant: drop the `-c core.fsmonitor=false` pin -> the sentinel appears
    -> this node is RED (GIT_OPTIONAL_LOCKS=0 alone does not stop the
    hook)."""
    repo = _make_repo(tmp_path)
    sentinel = tmp_path / "sentinel"
    env = _fixture_env(tmp_path)
    target = str(sentinel).replace(os.sep, "/")
    _git(repo, "config", "core.fsmonitor", f'touch "{target}"', env=env)

    assert identity.status_porcelain(repo) == "", (
        "clean repo must give empty porcelain, not the no-repo result"
    )
    assert identity.repo_root(repo) != identity.NO_REPO
    assert identity.head_commit(repo) != identity.NO_REPO
    assert identity.read(repo).name == "Local Person"
    assert not sentinel.exists(), (
        "core.fsmonitor ran: the hardened pin is missing (R27b)"
    )


def test_git_index_byte_identical_after_audit_path_calls(tmp_path):
    """R27a: the audit path (rev-parse x2, config x2) runs NO `git status`,
    so `.git/index` is byte-identical before and after — an audit writes
    nothing, not even git's own bookkeeping."""
    repo = _make_repo(tmp_path)
    index = repo / ".git" / "index"
    assert index.exists(), "fixture must have a real index to compare"
    before = hashlib.sha256(index.read_bytes()).hexdigest()

    identity.repo_root(repo)
    identity.head_commit(repo)
    identity.read(repo)

    after = hashlib.sha256(index.read_bytes()).hexdigest()
    assert before == after


def test_allowlist_source_census_no_non_allowlisted_subprocess():
    """LLR-RH.7.3 inspection arm: over `mapper/reqharness/`, the only
    `subprocess.run` site is identity.py's single hardened seam, every
    literal `_run_git` tail is an allowlist row, and every allowlist row is
    exercised — so a planted `git log` (B-124 stays deferred) or any
    non-allowlisted shape reddens the census."""
    pkg = Path(identity.__file__).resolve().parent
    run_sites = 0
    seen_tails: set[tuple[str, ...]] = set()
    for path in sorted(pkg.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "run"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "subprocess"
            ):
                assert path.name == "identity.py", (
                    f"subprocess outside the identity module: "
                    f"{path.name}:{node.lineno}"
                )
                run_sites += 1
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "_run_git"
                and len(node.args) >= 2
                and isinstance(node.args[1], ast.List)
                and all(
                    isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                    for elt in node.args[1].elts
                )
            ):
                seen_tails.add(
                    tuple(elt.value for elt in node.args[1].elts)
                )
    assert run_sites == 1, (
        f"expected the one hardened seam in identity.py, found {run_sites}"
    )
    assert seen_tails <= ALLOWED_TAILS, seen_tails - ALLOWED_TAILS
    assert seen_tails == ALLOWED_TAILS, (
        f"allowlist rows missing from the census: {ALLOWED_TAILS - seen_tails}"
    )
