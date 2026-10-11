"""HLR-RH.6 — baselines: the freeze (commit SHA + dirty flag) and the
five-class diff (LLR-RH.6.1 / LLR-RH.6.2), AT-081 through the real CLI.

Node names per the executed verification in
`.dev-flow/2026-10-11-reqharness-batch/01-requirements.md` §3 for HLR-RH.6:
`test_baseline_freezes_commit_sha_and_diffs` (LLR-RH.6.1) and
`test_at_081_baseline_vs_now_reports_new_changed_retired` (LLR-RH.6.2 via
the shipped `--audit <repo> --baseline v0` surface).  The negative controls
M-BL1 (commit SHA omitted) · M-BL2 (presence-only classification) · M-BL3
(`deleted` collapsed into `retired`) · M-BL4 (dirty flag forced) are the
declared reddening mutations of each oracle (executed RED in
`evidence/rh5-red.transcript`).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from mapper.reqharness import baseline
from mapper.reqharness.baseline import Baseline
from mapper.reqharness.chain import verify_chain
from mapper.reqharness.records import ValidationError
from tests.test_reqharness_identity import _fixture_env, _git, _make_repo
from tests.test_reqharness_registry import (
    CANON_HEADER,
    T3,
    T4,
    T5,
    _add_ana,
    _grant_reviewer,
    _record_review,
    _row,
    _seed,
)

ROOT = Path(__file__).resolve().parent.parent

OK_FIELDS = {"statement": "The system shall hold.", "rationale": "", "status": "active"}
DEL_FIELDS = {"statement": "The system shall go.", "rationale": "", "status": "active"}
WITH_FIELDS = {"statement": "The system shall withdraw.", "rationale": "", "status": "active"}

BASE_CANON = CANON_HEADER + (
    _row("HLR-TEST.1", "The system shall verify the chain.", "active", "first rationale")
    + _row("HLR-OK.4", OK_FIELDS["statement"], "active")
    + _row("HLR-WITH.1", WITH_FIELDS["statement"], "active")
    + _row("HLR-DEL.3", DEL_FIELDS["statement"], "active")
)


def _write_canon(repo: Path, text: str) -> None:
    (repo / "REQUIREMENTS.md").write_text(text, encoding="utf-8", newline="\n")


def _commit_all(repo: Path, tmp_path: Path, message: str) -> None:
    env = _fixture_env(tmp_path)
    _git(repo, "add", "-A", env=env)
    _git(repo, "commit", "-q", "-m", message, env=env)


def _seeded_repo(tmp_path: Path) -> Path:
    """A git repo holding a verifiable registry and the base canon."""
    repo = _make_repo(tmp_path)
    _seed(repo)
    _add_ana(repo)
    _grant_reviewer(repo)
    _write_canon(repo, BASE_CANON)
    _record_review(repo, "HLR-TEST.1", {
        "statement": "The system shall verify the chain.",
        "rationale": "first rationale",
        "status": "active",
    }, now=T3)
    _record_review(repo, "HLR-OK.4", OK_FIELDS, now=T3)
    _commit_all(repo, tmp_path, "registry")
    return repo


def _audit_cli(*args: str) -> subprocess.CompletedProcess:
    """The REAL console entry in a subprocess (M-AU1's harness): if main()
    ignored `--audit` the TUI would start and `timeout=60` would raise
    TimeoutExpired — counted as FAIL (R26)."""
    return subprocess.run(
        [sys.executable, "-c", "from mapper.app import main; main()", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )


def test_baseline_freezes_commit_sha_and_diffs(tmp_path):
    """LLR-RH.6.1: `Baseline.create` pins the current `git rev-parse HEAD`
    and records `dirty` from `git status --porcelain --no-optional-locks`
    on a clean AND a dirty tree; the frozen file round-trips through the
    typed loader; the chain head is pinned.  The five-class diff
    classifies every mutated fixture object (LLR-RH.6.2): new / changed /
    retired / unchanged / deleted — `reactivated` deferred (B-125).

    M-BL1 (SHA omitted) reddens the commit arms; M-BL4 (dirty forced)
    reddens the clean-tree arm; M-BL2 (presence-only) reddens the changed
    arm; M-BL3 (deleted -> retired) reddens the deleted arm."""
    repo = _seeded_repo(tmp_path)
    env = _fixture_env(tmp_path)

    base = Baseline.create(repo, "v0", now=T3)
    head = verify_chain(repo).head
    assert base.commit == _git(repo, "rev-parse", "HEAD", env=env).strip()
    assert len(base.commit) == 40
    assert base.dirty is False  # the tree was committed clean
    assert (base.roles_seq, base.roles_hash) == head

    # the frozen file round-trips through the typed loader
    loaded = Baseline.load(repo, "v0")
    assert loaded == base
    frozen_file = repo / "reqharness" / "baselines" / "v0.yml"
    assert frozen_file.is_file()

    # an existing baseline is never overwritten
    with pytest.raises(ValidationError, match="already exists"):
        Baseline.create(repo, "v0", now=T4)

    # dirty tree at freeze: recorded, refused nothing (M-BL4 reddens here)
    (repo / "stray.txt").write_text("untracked\n", encoding="utf-8", newline="\n")
    assert _git(repo, "status", "--porcelain", env=env).strip() != ""
    dirty = Baseline.create(repo, "v1", now=T4)
    assert dirty.dirty is True

    # the five mutations: a normative edit, a new id, a withdrawal, a
    # deletion, and a deleted review file
    review_path = repo / "reqharness" / "reviews"
    victim = sorted(review_path.iterdir())[0]
    victim.unlink()
    edited = CANON_HEADER + (
        _row("HLR-TEST.1", "The system shall verify the chain twice.", "active", "first rationale")
        + _row("HLR-OK.4", OK_FIELDS["statement"], "active")
        + _row("HLR-WITH.1", WITH_FIELDS["statement"], "withdrawn (see note)")
        + _row("HLR-NEW.2", "A brand new requirement.", "active")
    )
    _write_canon(repo, edited)

    data = baseline.snapshot(repo)
    result = baseline.diff(base, data.objects, current_review_files=data.review_files)
    assert result.classes == {
        "HLR-TEST.1": baseline.CLASS_CHANGED,  # normative digest moved
        "HLR-OK.4": baseline.CLASS_UNCHANGED,
        "HLR-WITH.1": baseline.CLASS_RETIRED,  # active -> retired
        "HLR-NEW.2": baseline.CLASS_NEW,
        "HLR-DEL.3": baseline.CLASS_DELETED,  # in the baseline, gone now
    }
    assert result.deleted_reviews == (victim.name,)
    assert result.baseline_dirty is False

    # baseline-vs-baseline: the same classes through a second freeze
    other = Baseline.create(repo, "v2", now=T5)
    cross = baseline.diff(base, other.objects, current_review_files=other.review_files)
    assert cross.classes == result.classes
    assert cross.deleted_reviews == result.deleted_reviews


def test_at_081_baseline_vs_now_reports_new_changed_retired(tmp_path):
    """AT-081 (through the shipped surface): after a normative edit, a new
    HLR, a withdrawal and a deletion, `mapper --audit <repo> --baseline v0`
    lists each object under changed / new / retired / deleted (five
    classes — `reactivated` deferred, B-125) and prints the baseline's
    dirty flag.  M-BL2 (presence-only classification) reddens the changed
    arm; M-BL3 (deleted collapsed into retired) reddens the deletion arm."""
    repo = _seeded_repo(tmp_path)
    Baseline.create(repo, "v0", now=T3)

    edited = CANON_HEADER + (
        _row("HLR-TEST.1", "The system shall verify the chain twice.", "active", "first rationale")
        + _row("HLR-OK.4", OK_FIELDS["statement"], "withdrawn (see note)")
        + _row("HLR-NEW.2", "A brand new requirement.", "active")
    )
    _write_canon(repo, edited)

    proc = _audit_cli("--audit", str(repo), "--baseline", "v0")
    assert proc.returncode == 1, proc.stderr  # unreviewed objects remain
    out = proc.stdout
    assert "chain: chain verified" in out
    assert "baseline v0: dirty=false" in out
    assert "changed: HLR-TEST.1" in out
    assert "new: HLR-NEW.2" in out
    assert "retired: HLR-OK.4" in out
    assert "deleted: HLR-DEL.3" in out
    assert "verdict: not ready" in out
    assert "Traceback" not in proc.stderr


def test_baseline_load_refuses_untyped_objects_and_bad_name(tmp_path):
    """H1 + L2 (unit level): `Baseline.load` validates `objects` is a LIST
    before iterating it (null / int corruptions are named ValidationErrors,
    never a TypeError) and applies `create`'s name rule to the loaded
    `name` — no `/`, `\\` or `..`.  A non-mapping row is equally named."""
    repo = _seeded_repo(tmp_path)
    Baseline.create(repo, "v0", now=T3)
    frozen_file = repo / "reqharness" / "baselines" / "v0.yml"
    document = yaml.safe_load(frozen_file.read_text(encoding="utf-8"))

    for mutant in (None, 5, ["a string row"]):
        document["objects"] = mutant
        frozen_file.write_text(
            yaml.safe_dump(document, sort_keys=False),
            encoding="utf-8",
            newline="\n",
        )
        with pytest.raises(ValidationError, match=r"objects"):
            Baseline.load(repo, "v0")

    document["objects"] = []
    for bad_name in ("../escape", "a/b", "a\\b", ".."):
        document["name"] = bad_name
        frozen_file.write_text(
            yaml.safe_dump(document, sort_keys=False),
            encoding="utf-8",
            newline="\n",
        )
        with pytest.raises(ValidationError, match=r"refused \(name\)"):
            Baseline.load(repo, "v0")


def test_audit_cli_baseline_schema_violation_is_named_not_a_traceback(tmp_path):
    """H1 (through the shipped surface): a baseline whose `objects` is
    null, an int, or holds a non-mapping row makes
    `mapper --audit <repo> --baseline v0` exit 1 with the named refusal on
    stderr — never a traceback (real console entry in a subprocess,
    timeout=60)."""
    repo = _seeded_repo(tmp_path)
    Baseline.create(repo, "v0", now=T3)
    frozen_file = repo / "reqharness" / "baselines" / "v0.yml"
    document = yaml.safe_load(frozen_file.read_text(encoding="utf-8"))
    for mutant in (None, 5, ["a string row"]):
        document["objects"] = mutant
        frozen_file.write_text(
            yaml.safe_dump(document, sort_keys=False),
            encoding="utf-8",
            newline="\n",
        )
        proc = _audit_cli("--audit", str(repo), "--baseline", "v0")
        assert proc.returncode == 1
        assert "objects" in proc.stderr
        assert "Traceback" not in proc.stderr


def test_audit_cli_baseline_name_traversal_is_refused_by_name(tmp_path):
    """HIGH (re-review follow-up): `--baseline ../../../outside/y` — and
    the backslash spelling — is refused by NAME before any path is built
    (the file sits OUTSIDE the toplevel, one `reqharness/baselines/`
    level shall never escape it): exit 1, the named refusal on stderr,
    the outside file's marker never printed, no traceback.  Real console
    entry in a subprocess (timeout=60)."""
    repo = _seeded_repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "y.yml").write_text(
        "name: OUTSIDE_MARKER_VALUE\n", encoding="utf-8", newline="\n"
    )
    for name in ("../../../outside/y", "..\\..\\..\\outside\\y"):
        proc = _audit_cli("--audit", str(repo), "--baseline", name)
        assert proc.returncode == 1
        assert "refused (name)" in proc.stderr
        assert "OUTSIDE_MARKER_VALUE" not in proc.stdout
        assert "OUTSIDE_MARKER_VALUE" not in proc.stderr
        assert "Traceback" not in proc.stderr


def test_resolve_inside_refuses_lexical_dotdot_escape(tmp_path):
    """LOW (re-review follow-up, unit level): `_resolve_inside` asserts
    the FINAL resolved path sits under the resolved root — a lexical
    `..` escape with no link involved is refused `refused (outside)`,
    and an inside path is returned resolved, not lexical."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (tmp_path / "outside.yml").write_text(
        "name: OUTSIDE_MARKER_VALUE\n", encoding="utf-8", newline="\n"
    )
    with pytest.raises(ValidationError, match=r"refused \(outside\)"):
        baseline._resolve_inside(repo, "reqharness/../../outside.yml")
    inside = baseline._resolve_inside(repo, "reqharness/baselines/v0.yml")
    assert inside == (repo / "reqharness" / "baselines" / "v0.yml").resolve()


__all__ = [  # the node ids this file owns, for the packet's ledger
    "test_baseline_freezes_commit_sha_and_diffs",
    "test_at_081_baseline_vs_now_reports_new_changed_retired",
    "test_baseline_load_refuses_untyped_objects_and_bad_name",
    "test_audit_cli_baseline_schema_violation_is_named_not_a_traceback",
    "test_audit_cli_baseline_name_traversal_is_refused_by_name",
    "test_resolve_inside_refuses_lexical_dotdot_escape",
]
