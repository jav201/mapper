"""HLR-RH.4 / HLR-RH.5 — review events, pending resolution derived from
the chain, the content-keyed parse cache and the derived object states.

The node names are the executed verification named in
`.dev-flow/2026-10-11-reqharness-batch/01-requirements.md` §3 for HLR-RH.4
and HLR-RH.5 (plus the pending-resolution node of ruling R6 and the identity
precedence node HLR-RH.4's verification lists).  Every refusal is asserted
BY NAME (R9); the state words and the informative mark are asserted
byte-for-byte; the negative controls M-RG1/2/3/4/5, M-FN1/2 and M-PR1 are
the declared reddening mutations of each oracle (executed RED in
`evidence/rh4-red.transcript`).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

import pytest
import yaml

from mapper.reqharness import derive, identity, pending, reviews
from mapper.reqharness.cache import ParseCache
from mapper.reqharness.canonical import canonical_digest, nfc
from mapper.reqharness.chain import (
    append_policy,
    approve_pending,
    effective_roles,
    propose,
    reject_pending,
    verify_chain,
)
from mapper.reqharness.config import (
    create_registry,
    email_sha256,
    load_config,
    load_documents,
)
from mapper.reqharness.records import ValidationError
from tests.test_reqharness_yaml_census import _yaml_load_violations

T0 = "2026-10-11T09:00:00Z"
T1 = "2026-10-11T09:01:00Z"
T2 = "2026-10-11T09:02:00Z"
T3 = "2026-10-11T09:03:00Z"
T4 = "2026-10-11T09:04:00Z"
T5 = "2026-10-11T09:05:00Z"
T6 = "2026-10-11T09:06:00Z"

NAME_RE = re.compile(r"\d{8}-[0-9a-f]{8}\.yml\Z")

CANON_HEADER = (
    "| Id | Statement | Rationale | Owning batch | Status |\n"
    "|---|---|---|---|---|\n"
)


def _row(object_id: str, statement: str, status: str, rationale: str = "") -> str:
    return (
        f"| {object_id} | {statement} | {rationale} | "
        f"2026-10-11-reqharness-batch | {status} |\n"
    )


HLR_FIELDS = {
    "statement": "The system shall verify the chain.",
    "rationale": "first rationale",
    "status": "active",
}


def _seed(root: Path) -> None:
    create_registry(
        root, person="bob", name="Bob Admin", email="bob@example.invalid", now=T0
    )


def _config_doc(root: Path):
    path = root / "reqharness" / "config.yml"
    (document,) = load_documents(
        path.read_text(encoding="utf-8"), where="reqharness/config.yml"
    )
    return path, document


def _add_ana(root: Path) -> None:
    """Add ana to the config and re-bind it through an admin `policy`
    event (the edited config is otherwise `config changed without
    approval`)."""
    path, document = _config_doc(root)
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
    append_policy(root, approved_by="bob", note="add ana", now=T1)


def _grant_reviewer(root: Path, now: str = T2) -> None:
    assert propose(
        root, requester="bob", action="grant",
        person="ana", role="req-reviewer", now=now,
    ) is None


def _digests(config, fields, class_id="HLR"):
    cls = next(c for c in config.classes if c.id == class_id)
    return derive.object_digests(cls, fields)


def _record_review(
    root: Path,
    object_id: str,
    fields: dict,
    *,
    class_id: str = "HLR",
    reviewer: str = "ana",
    kind: str = "human",
    now: str = T3,
    head: tuple[int, str] | None = None,
) -> Path:
    config = load_config(root)
    if head is None:
        head = verify_chain(root).head
    normative, informative = _digests(config, fields, class_id)
    return reviews.record_review(
        root,
        object_id=object_id,
        class_id=class_id,
        normative_digest=normative,
        informative_digest=informative,
        verdict="reviewed",
        reviewer=reviewer,
        kind=kind,
        note="fixture review",
        now=now,
        head=head,
        seq=reviews.next_seq(root),
    )


def _derive(root: Path, canon_text: str, cache: ParseCache | None = None):
    """The full derivation over a fixture canon, merged with the canon
    reader's own named reports."""
    config = load_config(root)
    report = verify_chain(root)
    scan = reviews.load_reviews(root, cache=cache)
    canon, canon_reported = derive.parse_canon(canon_text)
    result = derive.derive_states(canon, scan, report, config)
    return result, tuple(result.reported) + tuple(canon_reported)


_ONE_ROW = CANON_HEADER + _row("HLR-TEST.1", HLR_FIELDS["statement"], "active", HLR_FIELDS["rationale"])


def test_normative_edit_needs_review_informative_marks_only(tmp_path):
    """LLR-RH.4.1: a normative-field edit re-derives `changed · review`;
    an informative-only edit keeps `reviewed` and raises the visible
    `changed (informative)` mark (M-RG1 folds the informative fields into
    the normative digest)."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)

    result, _ = _derive(tmp_path, _ONE_ROW)
    assert result.states == {"HLR-TEST.1": derive.STATE_NOT_REVIEWED}

    _record_review(tmp_path, "HLR-TEST.1", HLR_FIELDS)
    result, _ = _derive(tmp_path, _ONE_ROW)
    assert result.states == {"HLR-TEST.1": derive.STATE_REVIEWED}
    assert result.informative_marks == ()

    # informative-only edit: rationale changes, statement stays
    edited_info = dict(HLR_FIELDS, rationale="second rationale")
    canon = CANON_HEADER + _row(
        "HLR-TEST.1", edited_info["statement"], "active", edited_info["rationale"]
    )
    result, _ = _derive(tmp_path, canon)
    assert result.states == {"HLR-TEST.1": derive.STATE_REVIEWED}  # state holds
    assert result.informative_marks == ("HLR-TEST.1",)  # the mark appears

    # normative edit: the statement itself changes
    edited_norm = dict(HLR_FIELDS, statement="The system shall verify the chain twice.")
    canon = CANON_HEADER + _row(
        "HLR-TEST.1", edited_norm["statement"], "active", edited_norm["rationale"]
    )
    result, _ = _derive(tmp_path, canon)
    assert result.states == {"HLR-TEST.1": derive.STATE_CHANGED}
    assert result.informative_marks == ()


def test_review_by_signer_without_role_in_force_is_pre_reviewed(tmp_path):
    """LLR-RH.4.2: a review whose signer held no reviewer role at its
    BOUND HEAD derives `pre-reviewed`, is flagged unentitled and the
    registry stays evaluable — never `not verifiable` on that account; a
    later grant must not retro-authorize (M-RG2 checks today's head); a
    chain break still dominates (precedence 1)."""
    _seed(tmp_path)
    # the review binds the GENESIS head — ana is not a reviewer there, and
    # no later grant may retro-authorize a review bound this early (R5)
    genesis_head = (1, verify_chain(tmp_path).events[0].this_hash)
    early = _record_review(
        tmp_path, "HLR-TEST.1", HLR_FIELDS, reviewer="ana", now=T0, head=genesis_head
    )
    _add_ana(tmp_path)  # ana is a person, NOT yet a reviewer

    result, _ = _derive(tmp_path, _ONE_ROW)
    assert result.verifiable  # evaluable, not `not verifiable`
    assert result.states == {"HLR-TEST.1": derive.STATE_PRE_REVIEWED}
    assert result.pre_reviewed == ("HLR-TEST.1",)
    assert result.unentitled == (early.name,)  # counted apart

    # the later grant must not retro-authorize the genesis-bound review
    _grant_reviewer(tmp_path, now=T2)
    result, _ = _derive(tmp_path, _ONE_ROW)
    assert result.states == {"HLR-TEST.1": derive.STATE_PRE_REVIEWED}
    assert result.unentitled == (early.name,)

    # an entitled human review at the post-grant head closes the state;
    # the old unentitled review stays counted apart
    _record_review(tmp_path, "HLR-TEST.1", HLR_FIELDS, now=T3)
    result, _ = _derive(tmp_path, _ONE_ROW)
    assert result.states == {"HLR-TEST.1": derive.STATE_REVIEWED}
    assert result.unentitled == (early.name,)  # the qualifying one is not

    # a newer pre-review never downgrades the qualifying review (R5 (2))
    _record_review(tmp_path, "HLR-TEST.1", HLR_FIELDS, kind="model", reviewer="kimi", now=T4)
    result, _ = _derive(tmp_path, _ONE_ROW)
    assert result.states == {"HLR-TEST.1": derive.STATE_REVIEWED}

    # precedence (1): a chain break dominates every outcome
    roles = tmp_path / "reqharness" / "roles.yml"
    roles.write_text(
        roles.read_text(encoding="utf-8").replace("ana", "mallory", 1),
        encoding="utf-8",
        newline="\n",
    )
    result, _ = _derive(tmp_path, _ONE_ROW)
    assert not result.verifiable
    assert result.states == {}
    assert result.reason == "config changed without approval"


def test_model_review_never_closes_state(tmp_path):
    """LLR-RH.4.3: a `kind: model` review — self-declared — derives
    `pre-reviewed` even with a matching digest and an entitled signer,
    and never satisfies a closing rule (M-RG3 treats model as closing)."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)
    # ana HOLDS the reviewer role at the bound head — `kind` alone keeps
    # this event a pre-review (the M-RG3 mutant drops exactly that gate)
    _record_review(
        tmp_path, "HLR-TEST.1", HLR_FIELDS, kind="model", reviewer="ana", now=T3
    )

    result, _ = _derive(tmp_path, _ONE_ROW)
    assert result.states == {"HLR-TEST.1": derive.STATE_PRE_REVIEWED}
    assert result.states["HLR-TEST.1"] != derive.STATE_REVIEWED
    assert result.pre_reviewed == ("HLR-TEST.1",)
    assert result.unentitled == ()  # the signer held the role; it is a model


def test_review_file_naming_and_exclusive_create(tmp_path):
    """LLR-RH.4.6 (R8/R22): review files are named
    `<yyyymmdd>-<sha8 of canonical content>.yml` — from content only, no
    caller-supplied slug (M-FN1); a second write fails the exclusive
    create; the loader recomputes sha8 — a name/content mismatch is
    reported BY NAME and non-closing (M-FN2); a link on the path is
    refused via `osopen` (R8)."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)

    path = _record_review(tmp_path, "HLR-TEST.1", HLR_FIELDS)
    assert path.parent == tmp_path / "reqharness" / "reviews"
    assert NAME_RE.fullmatch(path.name)
    assert path.name.startswith("20261011-")

    # the name is the content's: recompute sha8 over the canonical content
    where = f"reqharness/reviews/{path.name}"
    (document,) = load_documents(
        path.read_text(encoding="utf-8"), where=where
    )
    recomputed = canonical_digest(nfc(document))[:8]
    assert path.name == f"20261011-{recomputed}.yml"

    # seq allocation is monotonic per registry
    assert reviews.next_seq(tmp_path) == 2

    # exclusive create: the byte-identical event (same seq, same head) is a
    # name collision — an error, never a silent overwrite
    config = load_config(tmp_path)
    normative, informative = _digests(config, HLR_FIELDS)
    with pytest.raises(ValidationError, match="exclusive create"):
        reviews.record_review(
            tmp_path,
            object_id="HLR-TEST.1",
            class_id="HLR",
            normative_digest=normative,
            informative_digest=informative,
            verdict="reviewed",
            reviewer="ana",
            kind="human",
            note="fixture review",
            now=T3,
            head=verify_chain(tmp_path).head,
            seq=1,
        )

    # M-FN2: rewrite the bytes under the same name -> reported by name
    text = path.read_text(encoding="utf-8").replace(
        "fixture review", "hand edit keeps the old name"
    )
    path.write_text(text, encoding="utf-8", newline="\n")
    scan = reviews.load_reviews(tmp_path)
    assert scan.events == ()
    assert any(
        path.name in line and "name/content mismatch" in line
        for line in scan.reported
    ), scan.reported

    # R8: a junction on the reviews directory is refused, named
    linked = tmp_path / "linked"
    linked.mkdir()
    try:
        subprocess.run(
            ["cmd", "/c", "mklink", "/J",
             str(linked / "reqharness"), str(tmp_path / "reqharness")],
            check=True, capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("junction creation is unavailable on this host")
    with pytest.raises(ValidationError, match=r"refused \(link\)"):
        reviews.record_review(
            linked,
            object_id="HLR-TEST.1",
            class_id="HLR",
            normative_digest="ab" * 32,
            informative_digest="cd" * 32,
            verdict="reviewed",
            reviewer="ana",
            kind="human",
            note="x",
            now=T3,
            head=(1, "GENESIS"),
            seq=reviews.next_seq(tmp_path),
        )


def test_derived_states_boundary_catalog(tmp_path):
    """LLR-RH.5.1/5.2 — the boundary catalog: an empty registry derives
    zero states; a genesis-only chain verifies; a withdrawn requirement
    derives `retired` (M-RG4 counts it active); an unparseable canon row
    is reported by line and derives no state; a corrupted review file at
    derive time is reported by name and derives no state (R26); a review
    bound to an unknown head makes the registry `not verifiable`."""
    # empty registry: header only, genesis-only chain
    _seed(tmp_path)
    result, reported = _derive(tmp_path, CANON_HEADER)
    assert result.verifiable
    assert result.states == {}  # zero states, the partition is vacuous
    assert reported == ()

    # withdrawn marker: status starting with `withdrawn` -> retired
    canon = CANON_HEADER + (
        _row("HLR-TEST.1", HLR_FIELDS["statement"], "active", HLR_FIELDS["rationale"])
        + _row("HLR-WITH.1", "A withdrawn requirement.", "withdrawn (see note)")
    )
    result, _ = _derive(tmp_path, canon)
    assert result.states == {
        "HLR-TEST.1": derive.STATE_NOT_REVIEWED,
        "HLR-WITH.1": derive.STATE_RETIRED,
    }

    # unparseable canon row: reported by line, never guessed or skipped
    broken = CANON_HEADER + "| HLR-BAD.2 | a broken row |\n"
    result, reported = _derive(tmp_path, broken)
    assert "HLR-BAD.2" not in result.states
    assert len([line for line in reported if "HLR-BAD.2" in line]) == 1
    assert any("line" in line for line in reported if "HLR-BAD.2" in line)

    # corrupted review file at derive time: named, derives no state
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)
    reviews_dir = tmp_path / "reqharness" / "reviews"
    reviews_dir.mkdir(exist_ok=True)
    (reviews_dir / "corrupt.yml").write_text(
        "verdict: [unclosed\n", encoding="utf-8", newline="\n"
    )
    result, reported = _derive(tmp_path, _ONE_ROW)
    assert result.verifiable
    assert result.states == {"HLR-TEST.1": derive.STATE_NOT_REVIEWED}
    assert any("reviews/corrupt.yml" in line for line in reported), reported

    # unknown bound head: not verifiable dominates (R2 / precedence 1)
    _record_review(
        tmp_path,
        "HLR-TEST.1",
        HLR_FIELDS,
        now=T3,
        head=(99, "ab" * 32),  # a head the chain does not contain
    )
    result, reported = _derive(tmp_path, _ONE_ROW)
    assert not result.verifiable
    assert result.states == {}
    assert result.reason == derive.NOT_VERIFIABLE
    assert any("not in the current chain" in line for line in reported), reported


def _write_bulk_reviews(root: Path, config, count: int, head: tuple[int, str]) -> None:
    """`count` valid review files across `count` objects, written directly
    (the bulk cold/warm fixture — record_review's per-file seq scan would
    be quadratic here)."""
    reviews_dir = root / "reqharness" / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)
    cls = next(c for c in config.classes if c.id == "HLR")
    for index in range(count):
        fields = {"statement": f"Statement {index}.", "status": "active"}
        normative, informative = derive.object_digests(cls, fields)
        body = nfc(
            {
                "seq": index + 1,
                "time": T3,
                "object": f"HLR-BULK.{index}",
                "class": "HLR",
                "normative_digest": normative,
                "informative_digest": informative,
                "verdict": "reviewed",
                "reviewer": "bob",  # the genesis admin is entitled at head 1
                "kind": "human",
                "roles_seq": head[0],
                "roles_hash": head[1],
                "note": f"bulk {index}",
            }
        )
        digest = canonical_digest(body)
        name = f"20261011-{digest[:8]}.yml"
        (reviews_dir / name).write_text(
            yaml.safe_dump(body, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
            newline="\n",
        )


def _bulk_canon(count: int) -> str:
    lines = [CANON_HEADER]
    for index in range(count):
        lines.append(_row(f"HLR-BULK.{index}", f"Statement {index}.", "active"))
    return "".join(lines)


def test_review_parse_cache_is_pure_accelerator(tmp_path):
    """LLR-RH.5.3 (R4): the cache (`.git/reqharness-cache/`, keyed by
    sha256(file bytes)) derives states equal to a cache-deleted run —
    100% equal across the fixture set; a poisoned entry and a CORRUPT
    CACHE FILE are bounded to a re-parse, never a verdict change (R26);
    a content-modified event re-parses under its new key; the audit state
    is cache-OFF and writes nothing (M-RG5 lets a cached parse skip the
    re-validation — the bust+re-parse path is what it reddens)."""
    _seed(tmp_path)
    config = load_config(tmp_path)
    head = verify_chain(tmp_path).head
    count = 250
    _write_bulk_reviews(tmp_path, config, count, head)
    canon = _bulk_canon(count)
    (tmp_path / ".git").mkdir()

    def derive_now(use_cache: bool):
        cache = ParseCache.open(tmp_path) if use_cache else None
        result, _ = _derive(tmp_path, canon, cache=cache)
        if cache is not None:
            cache.save()
        return result

    cold = derive_now(True)
    cache_file = tmp_path / ".git" / "reqharness-cache" / "reviews.json"
    assert cache_file.exists()  # inside .git/, never tracked
    warm = derive_now(True)
    assert warm == cold  # warm == cold equality

    # cache deleted -> identical results
    cache_file.unlink()
    assert derive_now(True) == cold

    # cache OFF (the audit state) derives the same and writes nothing
    cache_file.unlink(missing_ok=True)
    assert derive_now(False) == cold
    assert not cache_file.exists()

    # poisoned entry: garbage under the file's content key -> re-parse
    victim = sorted((tmp_path / "reqharness" / "reviews").iterdir())[0]
    key = hashlib.sha256(victim.read_bytes()).hexdigest()
    cache_file.write_text(
        json.dumps({key: {"garbage": "document"}}),
        encoding="utf-8",
        newline="\n",
    )
    assert derive_now(True) == cold

    # corrupt cache file: bounded to a rebuild
    cache_file.write_text("not json {{{", encoding="utf-8", newline="\n")
    assert derive_now(True) == cold

    # content-modified event: a new key, re-parsed, equal results
    text = victim.read_text(encoding="utf-8").replace("bulk 0", "bulk 0 edited")
    victim.write_text(text, encoding="utf-8", newline="\n")
    cold_after = derive_now(False)
    assert derive_now(True) == cold_after


def test_never_yaml_load_source_census(tmp_path, monkeypatch):
    """LLR-RH.1.1/5.3 (R-SCALE a + R21): the reqharness package parses
    only through the custom loader subclass — the AST census finds zero
    banned `yaml.load`/`load_all`/`full_load`/`unsafe_load` calls — and
    the fallback-loader arm exercises the pure-Python base when
    CSafeLoader is unavailable (M-YC1 routes a load through `yaml.load`)."""
    pkg = Path(reviews.__file__).resolve().parent
    files = sorted(pkg.glob("*.py"))
    assert files, "the census scanned no files — it would pass vacuously"
    violations = [
        report for path in files for report in _yaml_load_violations(path)
    ]
    assert not violations, "banned yaml.load call(s): " + "; ".join(violations)

    # fallback base: a SafeLoader-only twin still parses through the seam
    fallback_twin = type("FallbackTwin", (yaml.SafeLoader,), {})
    monkeypatch.setattr(
        "mapper.reqharness.config.ReqHarnessLoader", fallback_twin
    )
    documents = load_documents("note: plain\n", where="fallback.yml")
    assert documents == [{"note": "plain"}]


def test_identity_reader_repo_local_then_global(tmp_path, monkeypatch):
    """LLR-RH.4.4/7.3 (the HLR-RH.4 verification node): reviewer identity
    is repo-local git config first, global fallback second; tests inject
    both — the operator's real config is never read for a fixture value.
    Mutant M-ID1 (read only the global config) reddens the first arm."""
    env = {**os.environ, "GIT_CONFIG_GLOBAL": str(tmp_path / "global.gitconfig")}
    repo = tmp_path / "work"
    repo.mkdir()
    init = subprocess.run(
        ["git", "init", "-q", str(repo)],
        env=env, capture_output=True, text=True, encoding="utf-8",
    )
    assert init.returncode == 0, init.stderr

    def git(*args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            env=env, capture_output=True, text=True, encoding="utf-8",
        )
        assert result.returncode == 0, result.stderr
        return result.stdout

    git("config", "user.name", "Local Person")
    git("config", "user.email", "local@example.test")
    home = tmp_path / "home"
    home.mkdir()
    (home / ".gitconfig").write_text(
        '[user]\n\tname = Global Person\n\temail = global@example.test\n',
        encoding="utf-8",
    )
    monkeypatch.setitem(os.environ, "HOME", str(home))
    monkeypatch.setitem(os.environ, "USERPROFILE", str(home))

    assert identity.read(repo) == identity.Identity("Local Person", "local@example.test")

    git("config", "--unset", "user.name")
    git("config", "--unset", "user.email")
    assert identity.read(repo) == identity.Identity("Global Person", "global@example.test")


def test_pending_resolution_derived_from_chain_reference(tmp_path):
    """R6 (HLR-RH.2): a pending request's resolution is DERIVED from the
    chain — an admin's `a` lands the change as the event referencing the
    request's sha256, `r` lands a `resolution` event with an empty change,
    the file stays, and the derivation survives a re-read (restart); a
    non-admin resolution never lands (M-PR1); nobody resolves their own
    request; a name/content-mismatched pending file is reported by name
    (R22)."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    assert propose(
        tmp_path, requester="bob", action="grant",
        person="ana", role="admin", now=T2,
    ) is None  # a second admin exists now

    held = propose(
        tmp_path, requester="bob", action="grant",
        person="bob", role="req-reviewer", now=T3,  # a self-change: pending
    )
    assert held is not None
    scan = pending.list_pending(tmp_path)
    assert scan.reported == ()
    assert len(scan.requests) == 1
    request = scan.requests[0]
    assert pending.resolution(verify_chain(tmp_path), request) == "pending"

    # nobody approves their own request; a non-admin never resolves (M-PR1)
    with pytest.raises(ValidationError, match="their own"):
        approve_pending(tmp_path, pending=request.name, approver="bob", now=T4)
    with pytest.raises(ValidationError, match="no admin"):
        approve_pending(tmp_path, pending=request.name, approver="mallory", now=T4)

    # `a`: the change lands as the chain event referencing the request hash
    event = approve_pending(tmp_path, pending=request.name, approver="ana", now=T4)
    assert event.request_hash == request.digest
    report = verify_chain(tmp_path)
    assert report.ok
    assert pending.resolution(report, request) == "approved"
    assert "req-reviewer" in effective_roles(report)["bob"]

    # `r`: a resolution event with an empty change; the file stays
    held2 = propose(
        tmp_path, requester="ana", action="grant",
        person="ana", role="req-reviewer", now=T5,  # self-change: pending
    )
    scan = pending.list_pending(tmp_path)
    assert len(scan.requests) == 2  # the approved file is still on disk
    request2 = next(r for r in scan.requests if r.name == held2.name)
    rejected = reject_pending(tmp_path, pending=request2.name, approver="bob", now=T6)
    assert rejected.action == "resolution"
    assert rejected.request_hash == request2.digest
    assert rejected.person == "" and rejected.role == ""
    report = verify_chain(tmp_path)
    assert report.ok
    assert pending.resolution(report, request2) == "rejected"
    assert "req-reviewer" not in effective_roles(report).get("ana", ())

    # restart arm: the derivation is rebuilt from files + chain alone
    again = pending.list_pending(tmp_path)
    report = verify_chain(tmp_path)
    by_name = {r.name: pending.resolution(report, r) for r in again.requests}
    assert by_name[request.name] == "approved"
    assert by_name[request2.name] == "rejected"

    # R22: a hand-edited pending file under its old name is reported
    text = held2.read_text(encoding="utf-8").replace("second", "hand edit")
    (tmp_path / "reqharness" / "pending" / "tampered.yml").write_text(
        text, encoding="utf-8", newline="\n"
    )
    scan = pending.list_pending(tmp_path)
    assert any(
        "tampered.yml" in line and "name/content mismatch" in line
        for line in scan.reported
    ), scan.reported


def test_review_cache_caches_validated_parses_only(tmp_path):
    """RHFIX4 H2: the cache stores VALIDATED parses only — a review file
    whose unquoted `time: 2026-10-11` coerces to a date fails the typed
    schema, is reported BY NAME, and its raw parse never enters the store,
    so `save()` cannot raise on a non-serialisable value; the scan result
    is identical with the cache deleted."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)
    good = _record_review(tmp_path, "HLR-TEST.1", HLR_FIELDS)
    reviews_dir = tmp_path / "reqharness" / "reviews"
    good_text = good.read_text(encoding="utf-8")
    (reviews_dir / "badtime.yml").write_text(
        re.sub(r"time: ['\"]2026-10-11T09:03:00Z['\"]", "time: 2026-10-11", good_text),
        encoding="utf-8",
        newline="\n",
    )
    (tmp_path / ".git").mkdir()

    cache = ParseCache.open(tmp_path)
    scan = reviews.load_reviews(tmp_path, cache=cache)
    cache.save()  # must not raise: the refused parse never entered the store
    assert [event.name for event in scan.events] == [good.name]
    assert any(
        "badtime.yml" in line and "must be a str" in line
        for line in scan.reported
    ), scan.reported

    cache_file = tmp_path / ".git" / "reqharness-cache" / "reviews.json"
    store = json.loads(cache_file.read_text(encoding="utf-8"))
    docs = store["docs"]  # the v2 payload: {"v": 2, "docs": {sha: doc}, "stat": {...}}
    bad_key = hashlib.sha256((reviews_dir / "badtime.yml").read_bytes()).hexdigest()
    assert bad_key not in docs  # the validated-parses-only invariant (H2)
    good_key = hashlib.sha256(good.read_bytes()).hexdigest()
    assert good_key in docs

    # cache deleted -> identical scan (events and reports)
    cache_file.unlink()
    again = reviews.load_reviews(tmp_path, cache=ParseCache.open(tmp_path))
    assert again.events == scan.events
    assert again.reported == scan.reported


def test_review_cache_size_guard_is_separate_limit(tmp_path):
    """RHFIX4 L2: the cache file has its OWN 64 MB payload limit — separate
    from roles.yml's 4 MB — so the cache persists at the 100 000-file
    scale; `save()` takes an injected limit: a payload over it is skipped
    silently (the cache rebuilds next run), never raised."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)
    good = _record_review(tmp_path, "HLR-TEST.1", HLR_FIELDS)
    (tmp_path / ".git").mkdir()
    cache = ParseCache.open(tmp_path)
    reviews.load_reviews(tmp_path, cache=cache)

    from mapper.reqharness.cache import LIMIT_CACHE_FILE_BYTES

    assert LIMIT_CACHE_FILE_BYTES == 64 * 1024 * 1024  # named constant (L2)
    cache_file = tmp_path / ".git" / "reqharness-cache" / "reviews.json"
    cache.save(limit=8)  # an injected limit far below the payload
    assert not cache_file.exists()  # over the limit: not written, no raise
    cache.save()  # the real 64 MB limit persists the validated parse
    assert cache_file.exists()
    warm = reviews.load_reviews(tmp_path, cache=ParseCache.open(tmp_path))
    assert [event.name for event in warm.events] == [good.name]


def test_record_review_type_checks_text_fields(tmp_path):
    """RHFIX4 L3: record_review type-checks the free-text fields BEFORE
    writing — a non-str verdict, reviewer or object id is a named refusal
    and no file is created."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)
    config = load_config(tmp_path)
    normative, informative = _digests(config, HLR_FIELDS)
    base = dict(
        object_id="HLR-TEST.1",
        class_id="HLR",
        normative_digest=normative,
        informative_digest=informative,
        verdict="reviewed",
        reviewer="ana",
        kind="human",
        note="x",
        now=T3,
        head=verify_chain(tmp_path).head,
        seq=reviews.next_seq(tmp_path),
    )
    for field, value in (
        ("verdict", 5),
        ("reviewer", None),
        ("object_id", ["HLR-TEST.1"]),
    ):
        with pytest.raises(ValidationError, match="must be a str"):
            reviews.record_review(tmp_path, **{**base, field: value})
    reviews_dir = tmp_path / "reqharness" / "reviews"
    assert not reviews_dir.exists()  # refusals happen before any write


__all__ = [  # the node ids this file owns, for the packet's ledger
    "test_normative_edit_needs_review_informative_marks_only",
    "test_review_by_signer_without_role_in_force_is_pre_reviewed",
    "test_model_review_never_closes_state",
    "test_review_file_naming_and_exclusive_create",
    "test_derived_states_boundary_catalog",
    "test_review_parse_cache_is_pure_accelerator",
    "test_never_yaml_load_source_census",
    "test_identity_reader_repo_local_then_global",
    "test_pending_resolution_derived_from_chain_reference",
    "test_review_cache_caches_validated_parses_only",
    "test_review_cache_size_guard_is_separate_limit",
    "test_record_review_type_checks_text_fields",
]
