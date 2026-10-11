"""HLR-RH.7 — release-rule evaluation and the read-only `--audit` CLI
(LLR-RH.7.1 / LLR-RH.7.2), AT-080 through the real console entry.

Node names per the executed verification in
`.dev-flow/2026-10-11-reqharness-batch/01-requirements.md` §3 for HLR-RH.7:
`test_release_rules_and_verdicts` (LLR-RH.7.1), AT-080
(`test_at_080_audit_report_counts_every_state_exactly`),
`test_audit_cli_refuses_escaping_repo_path` (LLR-RH.7.2 confinement,
M-AU2), the schema-refusal ladder of the reviewed nit (a)
(`test_verify_hand_added_document_becomes_status_not_exception`) and the
audit-level R27d arm (`test_audit_report_names_no_repo_on_git_refusal`).
The negative controls M-RL1 (one rule unevaluated) and M-AU1 (`--audit`
ignored -> TUI -> `TimeoutExpired` = FAIL) are the declared reddening
mutations (executed RED in `evidence/rh5-red.transcript`).
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

from mapper.reqharness import audit as audit_mod
from mapper.reqharness import derive, identity, release, reviews
from mapper.reqharness.chain import propose, verify_chain
from mapper.reqharness.config import create_registry, load_config
from mapper.reqharness.records import ValidationError
from tests.test_reqharness_identity import _fixture_env, _git, _make_repo
from tests.test_reqharness_registry import (
    CANON_HEADER,
    T0,
    T3,
    T4,
    _add_ana,
    _grant_reviewer,
    _record_review,
    _row,
    _seed,
)

ROOT = Path(__file__).resolve().parent.parent


def _git_repo(parent: Path, name: str) -> Path:
    """A second fixture git repo (the identity helper hardcodes `work`)."""
    repo = parent / name
    repo.mkdir()
    env = _fixture_env(parent)
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
    (repo / "tracked.txt").write_text("tracked\n", encoding="utf-8", newline="\n")
    _git(repo, "add", "tracked.txt", env=env)
    _git(repo, "commit", "-q", "-m", "init", env=env)
    return repo

ONE_ROW = CANON_HEADER + _row(
    "HLR-TEST.1", "The system shall verify the chain.", "active", "first rationale"
)
HLR_FIELDS = {
    "statement": "The system shall verify the chain.",
    "rationale": "first rationale",
    "status": "active",
}


def _write_canon(repo: Path, text: str) -> None:
    (repo / "REQUIREMENTS.md").write_text(text, encoding="utf-8", newline="\n")


def _break_policy(root: Path) -> None:
    """Edit the config WITHOUT the re-binding `policy` event — the live
    config's digest no longer matches the newest verified policy event."""
    import yaml

    from mapper.reqharness.config import email_sha256, load_documents

    path = root / "reqharness" / "config.yml"
    (document,) = load_documents(
        path.read_text(encoding="utf-8"), where="reqharness/config.yml"
    )
    document["people"].append(
        {
            "id": "ana",
            "name": "Ana Reviewer",
            "email_sha256": email_sha256("ana@example.invalid"),
        }
    )
    path.write_text(
        yaml.safe_dump(document, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
        newline="\n",
    )


def _verdict(root: Path, canon_text: str):
    """The release evaluation over a fixture canon: safe chain
    verification, review scan, derivation — then `release.evaluate`.
    A broken config never escapes: it is the not-verifiable block."""
    report = release.safe_verify(root)
    config = load_config(root) if report.ok else None
    scan = reviews.load_reviews(root)
    canon, _reported = derive.parse_canon(canon_text)
    if config is None:
        derivation = derive.Derivation(
            verifiable=False, reason=report.status, reported=tuple(scan.reported)
        )
        verdict = release.Verdict(
            ready=False,
            text=release.VERDICT_NOT_VERIFIABLE,
            rules=(
                (release.RULE_CHAIN, False),
                (release.RULE_POLICY, False),
                (release.RULE_SIGNERS, False),
            ),
        )
    else:
        derivation = derive.derive_states(canon, scan, report, config)
        verdict = release.evaluate(config, report, derivation)
    return verdict, derivation


def _audit_cli(*args: str) -> subprocess.CompletedProcess:
    """The REAL console entry in a subprocess with the R26 timeout:
    `TimeoutExpired` is a FAIL (M-AU1's oracle — main() ignoring `--audit`
    starts the TUI and hangs here)."""
    return subprocess.run(
        [sys.executable, "-c", "from mapper.app import main; main()", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )


def test_release_rules_and_verdicts(tmp_path):
    """LLR-RH.7.1: the mandatory rules + the config rules each have a
    fixture and every verdict string matches byte-for-byte — unreviewed ->
    `not ready · unreviewed requirements`; a broken chain, a policy
    mismatch or an unknown head -> exactly `not ready · registry not
    verifiable`; an unentitled review alone stays evaluable; all green ->
    `ready`.  Config MAY add rules (an unknown id is a named failure) and
    a config without `all_active_reviewed` does not block on unreviewed
    objects.  M-RL1 (one mandatory rule unevaluated) reddens the
    per-rule census assertions.  The retired-exclusion arm is
    LLR-RH.5.2's release-side fixture (an unreviewed withdrawn id
    never blocks an otherwise ready registry)."""
    # unreviewed object: evaluable, blocked by the config-declared rule
    _seed(tmp_path)
    verdict, derivation = _verdict(tmp_path, ONE_ROW)
    assert verdict.ready is False
    assert verdict.text == "not ready · unreviewed requirements"
    assert derivation.verifiable
    evaluated = {rule for rule, _ok in verdict.rules}
    assert evaluated >= set(release.MANDATORY_RULES), verdict.rules
    assert verdict.rule(release.RULE_ALL_REVIEWED) is False

    # a broken chain (hand edit): exactly the not-verifiable block
    roles = tmp_path / "reqharness" / "roles.yml"
    roles.write_text(
        roles.read_text(encoding="utf-8").replace("bob", "mallory", 1),
        encoding="utf-8",
        newline="\n",
    )
    verdict, derivation = _verdict(tmp_path, ONE_ROW)
    assert verdict.text == "not ready · registry not verifiable"
    assert not derivation.verifiable
    assert not verdict.rule(release.RULE_CHAIN)

    # a policy mismatch (config edited, never re-bound): the same block
    broken = tmp_path / "broken"
    broken.mkdir()
    _seed(broken)
    _break_policy(broken)  # edits the config; NO policy event re-binds it
    verdict, _ = _verdict(broken, ONE_ROW)
    assert verdict.text == "not ready · registry not verifiable"
    assert not verdict.rule(release.RULE_POLICY)

    # unentitled review alone: evaluable, never the not-verifiable block
    unentitled = tmp_path / "unentitled"
    unentitled.mkdir()
    _seed(unentitled)
    genesis_head = (1, verify_chain(unentitled).events[0].this_hash)
    _record_review(
        unentitled, "HLR-TEST.1", HLR_FIELDS, now=T0, head=genesis_head
    )
    _add_ana(unentitled)  # ana is a person, not yet a reviewer
    verdict, derivation = _verdict(unentitled, ONE_ROW)
    assert verdict.text == "not ready · unreviewed requirements"
    assert verdict.text != "not ready · registry not verifiable"
    assert derivation.verifiable
    assert derivation.pre_reviewed == ("HLR-TEST.1",)
    assert len(derivation.unentitled) == 1

    # all green: the entitled review closes the only active object
    green = tmp_path / "green"
    green.mkdir()
    _seed(green)
    _add_ana(green)
    _grant_reviewer(green)
    _record_review(green, "HLR-TEST.1", HLR_FIELDS, now=T3)
    _write_canon(green, ONE_ROW)
    verdict, _ = _verdict(green, ONE_ROW)
    assert verdict.ready is True
    assert verdict.text == "ready"
    assert all(ok for _rule, ok in verdict.rules)

    # config without `all_active_reviewed`: unreviewed no longer blocks
    relaxed = tmp_path / "relaxed"
    relaxed.mkdir()
    create_registry(
        relaxed, person="bob", name="Bob Admin", email="bob@example.invalid",
        now=T0, release_rules=("chain_verified", "policy_verified", "signers_in_force"),
    )
    _write_canon(relaxed, ONE_ROW)
    verdict, _ = _verdict(relaxed, ONE_ROW)
    assert verdict.ready is True
    assert verdict.text == "ready"

    # LLR-RH.5.2: `all_active_reviewed` considers only non-retired
    # objects - an unreviewed WITHDRAWN id never blocks a registry whose
    # active objects are all reviewed
    retired = tmp_path / "retired"
    retired.mkdir()
    _seed(retired)
    _add_ana(retired)
    _grant_reviewer(retired)
    _record_review(retired, "HLR-TEST.1", HLR_FIELDS, now=T3)
    retired_canon = CANON_HEADER + (
        _row("HLR-TEST.1", HLR_FIELDS["statement"], "active", HLR_FIELDS["rationale"])
        + _row("HLR-WITH.1", "A withdrawn requirement.", "withdrawn (deferred)")
    )
    _write_canon(retired, retired_canon)
    verdict, derivation = _verdict(retired, retired_canon)
    assert derivation.states["HLR-WITH.1"] == derive.STATE_RETIRED
    assert derivation.states["HLR-TEST.1"] == derive.STATE_REVIEWED
    assert verdict.ready is True  # the retired id does not block
    assert verdict.text == "ready"

    # config MAY add rules, never remove the mandatory three: an unknown
    # rule id is a named failure, not a silent skip
    unknown = tmp_path / "unknown"
    unknown.mkdir()
    create_registry(
        unknown, person="bob", name="Bob Admin", email="bob@example.invalid",
        now=T0, release_rules=("all_active_reviewed", "bogus_rule"),
    )
    _write_canon(unknown, ONE_ROW)
    verdict, _ = _verdict(unknown, ONE_ROW)
    assert verdict.ready is False
    assert verdict.text == "not ready · unknown release rule 'bogus_rule'"


def test_verify_hand_added_document_becomes_status_not_exception(tmp_path):
    """Reviewed nit (a): a schema ValidationError from a tampered or
    hand-added document becomes the status `chain broken` — or `config
    changed without approval` when it is the config — never an exception
    escaping `--audit` or the release evaluation.  The fixture is a
    hand-added genesis lacking `config_hash`."""
    repo = _make_repo(tmp_path)
    _seed(repo)
    _write_canon(repo, ONE_ROW)
    roles = repo / "reqharness" / "roles.yml"
    original_roles = roles.read_text(encoding="utf-8")

    # a hand-added genesis document WITHOUT config_hash (R15 binds it)
    roles.write_text(
        "---\n"
        "seq: 1\n"
        "time: '2026-10-11T09:00:00Z'\n"
        "requested_by: bob\n"
        "approved_by: genesis\n"
        "action: genesis\n"
        "person: bob\n"
        "role: admin\n"
        "note: hand-added\n"
        "roles_seq: 1\n"
        "roles_hash: GENESIS\n"
        "prev_hash: GENESIS\n"
        "this_hash: '00'\n",
        encoding="utf-8",
        newline="\n",
    )
    report = release.safe_verify(repo)
    assert report.status == "chain broken"
    verdict, derivation = _verdict(repo, ONE_ROW)
    assert not derivation.verifiable
    assert verdict.text == "not ready · registry not verifiable"

    # through the shipped surface: the report names the status, never a
    # traceback, and the exit code is 1
    proc = _audit_cli("--audit", str(repo))
    assert proc.returncode == 1
    assert "chain: chain broken" in proc.stdout
    assert "verdict: not ready · registry not verifiable" in proc.stdout
    assert "Traceback" not in proc.stderr

    # the config arm: a malformed config is `config changed without
    # approval`, equally not an exception
    roles.write_text(original_roles, encoding="utf-8", newline="\n")
    config_path = repo / "reqharness" / "config.yml"
    config_path.write_text(
        config_path.read_text(encoding="utf-8") + "surprise_key: 1\n",
        encoding="utf-8",
        newline="\n",
    )
    report = release.safe_verify(repo)
    assert report.status == "config changed without approval"
    verdict, _ = _verdict(repo, ONE_ROW)
    assert verdict.text == "not ready · registry not verifiable"


def _workspace_digest(root: Path) -> str:
    """sha256 over every file's relative path + content — the audit's
    writes-nothing oracle (R4): the digest is identical before/after."""
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(str(path.relative_to(root)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def test_at_080_audit_report_counts_every_state_exactly(tmp_path):
    """AT-080 (US-RH-002/003, HLR-RH.7): a subprocess
    (`subprocess.run(timeout=60)`, TimeoutExpired = FAIL — R26) running
    the REAL console entry over a fixture holding ONE object per state:
    the report counts each state EXACTLY (pre-reviews and unentitled
    counted separately, the informative mark shown, the R17 old-head WARN
    line), the chain status + counts + verdict sections all print, the
    exit code is 0 on `ready` and 1 on `not ready`, no TUI starts, and
    the workspace digest is unchanged (cache OFF, writes nothing).

    M-AU1 (`--audit` ignored by main() -> the TUI launches -> the 60 s
    timeout raises TimeoutExpired) reddens this node; M-RL1 reddens the
    all-green arm's exit code."""
    repo = _make_repo(tmp_path)
    _seed(repo)
    _add_ana(repo)
    _grant_reviewer(repo)  # chain head 3: ana holds req-reviewer
    head_now = verify_chain(repo).head
    genesis_head = (1, verify_chain(repo).events[0].this_hash)

    rev_fields = {"statement": "The system shall stay.", "rationale": "first", "status": "active"}
    _record_review(repo, "HLR-REV.1", rev_fields, now=T3, head=head_now)
    cha_fields = {"statement": "The system shall move.", "rationale": "", "status": "active"}
    _record_review(repo, "HLR-CHA.1", cha_fields, now=T3, head=head_now)
    # an unentitled review: ana bound to the GENESIS head, before the grant
    pre_fields = {"statement": "The system shall wait.", "rationale": "", "status": "active"}
    _record_review(
        repo, "HLR-PRE.1", pre_fields, reviewer="ana", now=T3, head=genesis_head
    )
    # the R17 old-head WARN: one more event, then ana's role is revoked
    # AFTER her head-3 review (the revocation's bound head follows it)
    assert propose(
        repo, requester="bob", action="grant", person="ana",
        role="admin", now=T3,
    ) is None
    assert propose(
        repo, requester="bob", action="revoke", person="ana",
        role="req-reviewer", now=T4,
    ) is None

    canon = CANON_HEADER + (
        _row("HLR-REV.1", rev_fields["statement"], "active", "edited rationale")
        + _row("HLR-CHA.1", "The system shall move now.", "active")
        + _row("HLR-PRE.1", pre_fields["statement"], "active")
        + _row("HLR-NOT.1", "The system shall sleep.", "active")
        + _row("HLR-RET.1", "The system shall retire.", "withdrawn (deferred)")
    )
    _write_canon(repo, canon)

    before = _workspace_digest(repo)
    proc = _audit_cli("--audit", str(repo))
    after = _workspace_digest(repo)
    assert proc.returncode == 1, proc.stderr  # unreviewed objects remain
    assert before == after, "the audit wrote something (R4)"
    assert not (repo / ".git" / "reqharness-cache").exists(), "cache must stay OFF"

    out = proc.stdout
    assert "repo: " in out
    assert "chain: chain verified" in out
    # every state counted EXACTLY — one object per state
    assert (
        "counts: reviewed=1, changed · review=1, pre-reviewed=1, "
        "not reviewed=1, retired=1" in out
    )
    assert "pre-reviews: 1 (HLR-PRE.1)" in out
    assert "unentitled reviews: 1 (" in out
    assert "informative marks: HLR-REV.1 (changed (informative))" in out
    assert "WARNING: HLR-REV.1" in out  # R17 old-head binding warn
    assert "identity ceiling:" in out
    assert "verdict: not ready · unreviewed requirements" in out
    assert "Traceback" not in proc.stderr

    # the all-green fixture: exit code 0 on `ready`
    green = _git_repo(tmp_path, "green")
    _seed(green)
    _add_ana(green)
    _grant_reviewer(green)
    _record_review(green, "HLR-TEST.1", HLR_FIELDS, now=T3)
    _write_canon(green, ONE_ROW)
    ok = _audit_cli("--audit", str(green))
    assert ok.returncode == 0, ok.stderr
    assert "verdict: ready" in ok.stdout
    assert "counts: reviewed=1, changed · review=0, pre-reviewed=0, not reviewed=0, retired=0" in ok.stdout


def test_audit_cli_refuses_escaping_repo_path(tmp_path):
    """LLR-RH.7.2: an escaping/unknown repo path is refused BEFORE any
    file is read, through the one containment rule
    (`mapper.osopen.confine_reason`).  M-AU2 (confinement moved after the
    reads) reddens this node: the linked repo would audit cleanly."""
    outside = tmp_path / "outside"
    outside.mkdir()
    _seed(outside)
    _write_canon(outside, ONE_ROW)

    linked = tmp_path / "linked"
    linked.mkdir()
    try:
        if os.name == "nt":
            subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(linked / "repo"), str(outside)],
                check=True,
                capture_output=True,
            )
        else:
            (linked / "repo").symlink_to(outside, target_is_directory=True)
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("link creation is unavailable on this host")

    with pytest.raises(ValidationError, match="refused"):
        audit_mod.audit(linked / "repo")
    with pytest.raises(ValidationError, match="refused"):
        audit_mod.audit(tmp_path / "missing")

    proc = _audit_cli("--audit", str(linked / "repo"))
    assert proc.returncode == 1
    assert "refused" in proc.stderr
    assert "Traceback" not in proc.stderr


def test_audit_report_names_no_repo_on_git_refusal(tmp_path, monkeypatch):
    """R27d (audit level): a `safe.directory` refusal — any git non-zero
    exit — yields the NAMED result `no repo` in the audit report, never a
    crash.  The refusal is simulated with git's own
    GIT_TEST_ASSUME_DIFFERENT_OWNER, injected below the `_git_env` seam
    (the F5 strip would remove it)."""
    repo = _make_repo(tmp_path)
    _seed(repo)
    _write_canon(repo, ONE_ROW)
    assert identity.repo_root(repo) != identity.NO_REPO

    real_git_env = identity._git_env

    def refusal_env() -> dict[str, str]:
        env = real_git_env()
        env["GIT_TEST_ASSUME_DIFFERENT_OWNER"] = "1"
        return env

    monkeypatch.setattr(identity, "_git_env", refusal_env)
    report = audit_mod.audit(repo)
    assert report.chain_status == "no repo"
    assert report.ready is False
    assert report.verdict == "not ready · no repo"
    rendered = audit_mod.render(report)
    assert "chain: no repo" in rendered
    assert "Traceback" not in rendered


def test_audit_cli_resolves_relative_repo_argument(tmp_path):
    """M1: the repo argument is the operator's choice — `mapper --audit ..`
    run with cwd inside a subdirectory of the repo resolves through to the
    repo's toplevel and audits it (chain status and verdict print, no
    refusal on stderr)."""
    repo = _make_repo(tmp_path)
    _seed(repo)
    _add_ana(repo)
    _grant_reviewer(repo)
    _record_review(repo, "HLR-TEST.1", HLR_FIELDS, now=T3)
    _write_canon(repo, ONE_ROW)
    sub = repo / "sub"
    sub.mkdir()
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    proc = subprocess.run(
        [sys.executable, "-c", "from mapper.app import main; main()", "--audit", ".."],
        cwd=sub,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    assert "chain: chain verified" in proc.stdout
    assert "verdict: ready" in proc.stdout
    assert "Traceback" not in proc.stderr


def test_audit_cli_refuses_baseline_link_escaping_repo(tmp_path):
    """M1: a `reqharness/baselines/<name>.yml` that is a link resolving
    OUTSIDE the toplevel is refused by name — `mapper --audit <repo>
    --baseline x` exits 1, the refusal names the file, never a traceback.
    Skipped on hosts where symlink creation fails."""
    outside = tmp_path / "outside.yml"
    outside.write_text("name: x\n", encoding="utf-8", newline="\n")
    repo = _make_repo(tmp_path)
    _seed(repo)
    _write_canon(repo, ONE_ROW)
    target = repo / "reqharness" / "baselines" / "x.yml"
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        target.symlink_to(outside)
    except OSError:
        pytest.skip("symlink creation is unavailable on this host")
    proc = _audit_cli("--audit", str(repo), "--baseline", "x")
    assert proc.returncode == 1
    assert "x.yml" in proc.stderr
    assert "refused" in proc.stderr
    assert "Traceback" not in proc.stderr


def test_audit_report_prints_chain_status_when_canon_unreadable(tmp_path):
    """M2: a missing or non-UTF-8 REQUIREMENTS.md must not hide the chain
    status — the report still prints `chain:`, the per-state counts it can
    compute (all zero), the named not-ready line
    `canon unreadable: <reason>` and exits 1."""
    repo = _make_repo(tmp_path)
    _seed(repo)
    _add_ana(repo)
    _grant_reviewer(repo)
    _record_review(repo, "HLR-TEST.1", HLR_FIELDS, now=T3)

    proc = _audit_cli("--audit", str(repo))  # REQUIREMENTS.md missing
    assert proc.returncode == 1
    assert "chain: chain verified" in proc.stdout
    assert (
        "counts: reviewed=0, changed · review=0, pre-reviewed=0, "
        "not reviewed=0, retired=0" in proc.stdout
    )
    assert "canon unreadable: REQUIREMENTS.md: file not found" in proc.stdout
    assert "verdict: not ready · canon unreadable" in proc.stdout
    assert "Traceback" not in proc.stderr

    (repo / "REQUIREMENTS.md").write_bytes(b"\xff\xfe\x00not utf-8")
    proc = _audit_cli("--audit", str(repo))
    assert proc.returncode == 1
    assert "chain: chain verified" in proc.stdout
    assert "canon unreadable: REQUIREMENTS.md: not valid UTF-8" in proc.stdout
    assert "Traceback" not in proc.stderr


def test_audit_cli_refusal_line_has_one_prefix(tmp_path):
    """L1: the named refusal carries exactly ONE `audit:` prefix — the
    exact stderr line is asserted, so a doubled `audit: audit:` reddens."""
    missing = tmp_path / "missing"
    proc = _audit_cli("--audit", str(missing))
    assert proc.returncode == 1
    assert proc.stderr.splitlines() == [
        f"audit: {missing}: refused (not a directory)"
    ]


__all__ = [  # the node ids this file owns, for the packet's ledger
    "test_release_rules_and_verdicts",
    "test_verify_hand_added_document_becomes_status_not_exception",
    "test_at_080_audit_report_counts_every_state_exactly",
    "test_audit_cli_refuses_escaping_repo_path",
    "test_audit_report_names_no_repo_on_git_refusal",
    "test_audit_cli_resolves_relative_repo_argument",
    "test_audit_cli_refuses_baseline_link_escaping_repo",
    "test_audit_report_prints_chain_status_when_canon_unreadable",
    "test_audit_cli_refusal_line_has_one_prefix",
]



def test_audit_render_escapes_registry_derived_text(tmp_path):
    """SEC F1 (DDR follow-up): `audit.render` escapes EVERY registry-derived
    value — C0/C1 controls, ESC, DEL and CR/LF paint as their ``\\xNN``
    spellings — so a crafted canon id or reviewer id can never inject a
    terminal escape sequence or spoof a verdict line.  Through the real
    console entry (timeout=60): a canon id carrying ESC derives an
    informative mark; a person id carrying a newline signs the closing
    review and lands in the R17 old-head WARN — the output holds no raw
    ESC/C1/DEL byte and exactly ONE `verdict:` line."""
    import yaml

    from mapper.reqharness.chain import append_policy
    from mapper.reqharness.config import email_sha256, load_documents

    repo = _make_repo(tmp_path)
    _seed(repo)
    bad_id = "HLR-\x1b[8mX"
    bad_person = "x\nverdict: ready"
    fields = {"statement": "The system shall stay.", "rationale": "first", "status": "active"}

    # a real configured person whose id carries the newline injection, made
    # a reviewer by an admin grant (one event)
    config_path = repo / "reqharness" / "config.yml"
    (document,) = load_documents(
        config_path.read_text(encoding="utf-8"), where="reqharness/config.yml"
    )
    document["people"].append(
        {
            "id": bad_person,
            "name": "Crafty Reviewer",
            "email_sha256": email_sha256("crafty@example.invalid"),
        }
    )
    config_path.write_text(
        yaml.safe_dump(document, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
        newline="\n",
    )
    append_policy(repo, approved_by="bob", note="add reviewer", now=T3)
    assert propose(
        repo, requester="bob", action="grant",
        person=bad_person, role="req-reviewer", now=T3,
    ) is None  # head 3: the crafted signer holds req-reviewer
    head_now = verify_chain(repo).head
    _record_review(repo, bad_id, fields, reviewer=bad_person, now=T3, head=head_now)
    # the R17 old-head WARN carries the reviewer text: one more event
    # moves the head past the review's bound head, THEN the signer's
    # role is revoked
    assert propose(
        repo, requester="bob", action="grant",
        person=bad_person, role="admin", now=T4,
    ) is None
    assert propose(
        repo, requester="bob", action="revoke",
        person=bad_person, role="req-reviewer", now=T4,
    ) is None
    # an informative-only edit carries the object id in the informative mark
    edited = dict(fields, rationale="second rationale")
    canon = CANON_HEADER + _row(bad_id, edited["statement"], "active", edited["rationale"])
    _write_canon(repo, canon)

    proc = _audit_cli("--audit", str(repo))
    assert proc.returncode == 0, proc.stderr  # the only active object is reviewed
    out = proc.stdout
    assert "\x1b" not in out  # no raw ESC reaches the terminal
    assert "\x7f" not in out  # nor DEL
    assert "\r" not in out  # nor a carriage return
    assert not any(0x80 <= ord(ch) <= 0x9F for ch in out)  # nor any C1 control
    # exactly ONE verdict line — the spoofed `verdict:` is visible-escaped
    verdict_lines = [line for line in out.splitlines() if line.startswith("verdict: ")]
    assert verdict_lines == ["verdict: ready"], verdict_lines
    # the injections paint as their visible spellings
    assert "\\x1b[8m" in out
    assert "x\\x0averdict: ready" in out


def test_audit_cli_names_no_registry_state(tmp_path):
    """QA C1 (DDR follow-up): `mapper --audit` on a usable git repo with NO
    registry (`reqharness/` absent) prints the named state
    `chain: no registry yet` and verdict `not ready · no registry yet` —
    not the alarming `chain broken` — and exits 1, never a traceback."""
    repo = _make_repo(tmp_path)  # a git repo with a commit, no reqharness/
    assert not (repo / "reqharness").exists()
    proc = _audit_cli("--audit", str(repo))
    assert proc.returncode == 1
    assert "chain: no registry yet" in proc.stdout
    assert "verdict: not ready · no registry yet" in proc.stdout
    assert "chain broken" not in proc.stdout
    assert "Traceback" not in proc.stderr


def test_audit_render_escapes_bidi_and_separator_text(tmp_path):
    """SEC F1 nit (DDRFIX-C): the escaper covers Unicode categories Cc, Cf
    (bidi overrides U+202A–U+202E, U+2066–U+2069, zero-width U+200B–U+200F,
    U+2060, U+FEFF) and Zl/Zp (U+2028, U+2029).  A reviewer id carrying
    U+2028 would split `str.splitlines()` — forging a second `verdict:`
    line — and a bidi override / zero-width in an object id would reach the
    terminal raw; here both paint as their visible ``\\uXXXX`` spellings, so
    the output holds exactly ONE verdict line and none of the raw chars."""
    import yaml

    from mapper.reqharness.chain import append_policy
    from mapper.reqharness.config import email_sha256, load_documents

    repo = _make_repo(tmp_path)
    _seed(repo)
    bad_id = "HLR-\u202e\u200bX"
    bad_person = "x\u2028verdict: ready"
    fields = {"statement": "The system shall stay.", "rationale": "first", "status": "active"}

    # a real configured person whose id carries the U+2028 injection, made
    # a reviewer by an admin grant (one event) — same fixture shape as the
    # C0/C1 escaping node, new payload classes
    config_path = repo / "reqharness" / "config.yml"
    (document,) = load_documents(
        config_path.read_text(encoding="utf-8"), where="reqharness/config.yml"
    )
    document["people"].append(
        {
            "id": bad_person,
            "name": "Crafty Reviewer",
            "email_sha256": email_sha256("crafty@example.invalid"),
        }
    )
    config_path.write_text(
        yaml.safe_dump(document, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
        newline="\n",
    )
    append_policy(repo, approved_by="bob", note="add reviewer", now=T3)
    assert propose(
        repo, requester="bob", action="grant",
        person=bad_person, role="req-reviewer", now=T3,
    ) is None  # head 3: the crafted signer holds req-reviewer
    head_now = verify_chain(repo).head
    _record_review(repo, bad_id, fields, reviewer=bad_person, now=T3, head=head_now)
    # the R17 old-head WARN carries the reviewer text: one more event
    # moves the head past the review's bound head, THEN the signer's
    # role is revoked
    assert propose(
        repo, requester="bob", action="grant",
        person=bad_person, role="admin", now=T4,
    ) is None
    assert propose(
        repo, requester="bob", action="revoke",
        person=bad_person, role="req-reviewer", now=T4,
    ) is None
    # an informative-only edit carries the object id in the informative mark
    edited = dict(fields, rationale="second rationale")
    canon = CANON_HEADER + _row(bad_id, edited["statement"], "active", edited["rationale"])
    _write_canon(repo, canon)

    proc = _audit_cli("--audit", str(repo))
    assert proc.returncode == 0, proc.stderr  # the only active object is reviewed
    out = proc.stdout
    for ch in ("\u2028", "\u202e", "\u200b"):
        assert ch not in out, f"raw {ch!r} reached the terminal"
    # exactly ONE verdict line — U+2028 cannot forge a second one
    verdict_lines = [line for line in out.splitlines() if line.startswith("verdict: ")]
    assert verdict_lines == ["verdict: ready"], verdict_lines
    # the injections paint as their visible spellings
    assert "\\u2028" in out
    assert "\\u202e" in out
    assert "\\u200b" in out


def test_audit_cli_refusal_line_escapes_control_text(tmp_path):
    """SEC F1 nit (DDRFIX-C): EVERY line the CLI writes — stdout or stderr —
    goes through the escaper, the named refusal included.  The refusal
    echoes the operator's repo argument verbatim; a bidi override / line
    separator / C1 / ESC in it paints as its visible spelling on stderr,
    never raw — the refusal path cannot inject terminal control sequences.
    (The name need not exist: the confinement lstat loop breaks at the
    missing tail and the not-a-directory refusal names the text as given.)"""
    raw = str(tmp_path / "x\u202ey\u2028z\x1b\u009b")
    proc = _audit_cli("--audit", raw)
    assert proc.returncode == 1
    for ch in ("\x1b", "\u009b", "\u202e", "\u2028"):
        assert ch not in proc.stderr, f"raw {ch!r} reached the terminal"
    assert "\\u202e" in proc.stderr
    assert "\\u2028" in proc.stderr
    assert "\\x1b" in proc.stderr
    assert "\\x9b" in proc.stderr
    # the whole line: the escaped prefix, one named refusal (the reason
    # word depends on how the OS reacts to a control char in the name)
    expected_prefix = "audit: " + str(tmp_path) + "\\" + "x\\u202ey\\u2028z\\x1b\\x9b"
    lines = proc.stderr.splitlines()
    assert len(lines) == 1, proc.stderr
    assert lines[0].startswith(expected_prefix), proc.stderr
    assert ": refused (" in lines[0], proc.stderr


def test_audit_visible_escapes_nbsp_combining_and_variation_selectors():
    """SEC F1 nit (K3 re-check LOW-3): `_visible` escapes every separator
    OTHER than the plain U+0020 space (NBSP U+00A0, the U+2000–U+200A range,
    narrow NBSP U+202F, U+205F, ideographic U+3000 — an invisible or
    width-spoofing space in a crafted id), every combining mark (Mn U+0301,
    Me U+20DD — a combining sequence can overlay or reorder glyphs) and
    every variation selector (U+FE0F, U+E01EF — an emoji-presentation swap
    on a spoofed line) as its visible ``\\\\uXXXX`` spelling, while ASCII,
    ordinary BMP text and the plain space pass through untouched."""
    from mapper.reqharness.audit import _visible

    assert _visible("\u00a0\u2000\u2007\u202f\u205f\u3000\u0301\u20dd\ufe0f\U000e01ef") == (
        "\\u00a0\\u2000\\u2007\\u202f\\u205f\\u3000\\u0301\\u20dd\\ufe0f\\ue01ef"
    )
    assert _visible("plain text, with spaces") == "plain text, with spaces"
    assert _visible("caf\u00e9 \u4e2d\u6587") == "caf\u00e9 \u4e2d\u6587"
    # the C0/C1 and Cf/Zl/Zp arms are unchanged by the widening
    assert _visible("x\x1b\u009b\u2028\ufeffy") == "x\\x1b\\x9b\\u2028\\ufeffy"
