"""Shared fixtures for the relmap audit tests (proposal 2.1 row 5, ledger .35).

A HELPER module, never a copy: the repository builders are IMPORTED from the release tests, so a
renamed or reshaped source helper fails the import loudly instead of drifting.  This module adds
the relmap wrappers on top of them: a repository with a registry (and optionally an all-reviewed,
exit-0 one), a subprocess runner that pins the child to THIS checkout's `mapper` and can set
`PYTHONHASHSEED`, and a splitter that finds the verdict line by its prefix.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from tests.test_reqharness_registry import (
    CANON_HEADER,
    T3,
    _add_ana,
    _grant_reviewer,
    _record_review,
    _row,
)
from tests.test_reqharness_release import (
    HLR_FIELDS,
    ONE_ROW,
    ROOT,
    _audit_cli,
    _git_repo,
    _seed,
    _write_canon,
)

__all__ = [
    "CANON_HEADER", "HLR_FIELDS", "ONE_ROW", "ROOT", "T3", "_audit_cli", "block_of", "child_mapper_file", "ready_repo",
    "registry_repo", "report_of", "row", "run_audit", "run_audit_nohook",
]

row = _row

def canon_of(*rows: tuple[str, str, str]) -> str:
    """A canon in the release-test shape from `(id, statement, status)` triples."""
    return CANON_HEADER + "".join(_row(i, s, st) for i, s, st in rows)


def registry_repo(tmp_path: Path, name: str, canon_text: str | bytes | None) -> Path:
    """A git repo with a verified registry chain and `canon_text` as REQUIREMENTS.md (None: no
    canon file).  Nothing is reviewed, so the audit exits 1 -- use `ready_repo` for exit 0."""
    repo = _git_repo(tmp_path, name)
    _seed(repo)
    _write_bytes_or_text(repo, canon_text)
    return repo


def ready_repo(tmp_path: Path, name: str, canon_text: str, reviewed_ids: dict[str, dict]) -> Path:
    """A repo whose audit exits 0: every id in `reviewed_ids` (id -> its review fields) is
    reviewed by an entitled reviewer; `canon_text` must hold no other active object."""
    repo = _git_repo(tmp_path, name)
    _seed(repo)
    _add_ana(repo)
    _grant_reviewer(repo)
    for object_id, fields in reviewed_ids.items():
        _record_review(repo, object_id, fields, class_id=object_id.split("-", 1)[0], now=T3)
    _write_bytes_or_text(repo, canon_text)
    return repo


def _write_bytes_or_text(repo: Path, canon_text: str | bytes | None) -> None:
    if canon_text is None:
        return
    if isinstance(canon_text, bytes):
        (repo / "REQUIREMENTS.md").write_bytes(canon_text)
    else:
        _write_canon(repo, canon_text)


def _env(hashseed: str | None) -> dict[str, str]:
    env = {**os.environ, "PYTHONPATH": str(ROOT), "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
    env.pop("NO_COLOR", None)
    env.pop("TERM", None)
    if hashseed is not None:
        env["PYTHONHASHSEED"] = hashseed
    return env


def child_mapper_file() -> str:
    """Where the CHILD process imports `mapper` from (asserted to be this checkout by the tests)."""
    done = subprocess.run(
        [sys.executable, "-c", "import mapper; print(mapper.__file__)"],
        cwd=ROOT, env=_env(None), capture_output=True, text=True, encoding="utf-8", timeout=60,
    )
    return done.stdout.strip()


def run_audit(*args: str, hashseed: str | None = None) -> subprocess.CompletedProcess:
    """The real console entry in a subprocess with the 60 s timeout (`TimeoutExpired` is a FAIL),
    the child pinned to this checkout through PYTHONPATH."""
    return subprocess.run(
        [sys.executable, "-c", "from mapper.app import main; main()", "--audit", *args],
        cwd=ROOT, env=_env(hashseed), capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=60,
    )


def run_audit_nohook(*args: str) -> subprocess.CompletedProcess:
    """The same audit WITHOUT the structure hook: `run_cli(argv)`, the baseline for exit codes."""
    code = "import sys; from mapper.reqharness.audit import run_cli; sys.exit(run_cli(sys.argv))"
    return subprocess.run(
        [sys.executable, "-c", code, "--audit", *args],
        cwd=ROOT, env=_env(None), capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=60,
    )


def report_of(stdout: str) -> tuple[list[str], list[str]]:
    """`(lines up to and including the verdict line, the block after it)`.  The verdict is found
    by its prefix `verdict: ` -- it is no longer the last line (LLR-RMU.1.1)."""
    lines = stdout.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    verdict = [i for i, line in enumerate(lines) if line.startswith("verdict: ")]
    assert len(verdict) == 1, verdict
    return lines[: verdict[0] + 1], lines[verdict[0] + 1:]


def block_of(stdout: str) -> list[str]:
    return report_of(stdout)[1]
