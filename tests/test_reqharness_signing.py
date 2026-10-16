"""HLR-RS.2 / HLR-RS.3 / HLR-RS.5 — the headless review-signing core:
the `entitled_to_sign` pre-flight predicate (the 10-arm truth table) and the
`sign_review` orchestration (the TOCTOU `moved_*` re-checks, the `unapproved_config`
config gate, `already_signed` / `review_limit` write refusals, the fixed `now`
clock and the no-CLI/entry-point pin).

Node names are the executed verification named in
`.dev-flow/2026-10-15-review-screen-batch/01-requirements.md` §3 for
LLR-RS.2.1 / LLR-RS.2.2 / LLR-RS.2.4.  Every refusal is asserted by its stable
reason code (never a free-text guess) and writes nothing; helpers are reused
from `tests/test_reqharness_registry.py`; the negative controls M-RS5/M-RS6/
M-RS7/M-RS8/M-RS14/M-RS19/M-RS22/M-RS23/M-RS29 are the declared reddening
mutations (executed RED in `evidence/rs1b-red.transcript`).
"""
from __future__ import annotations

import ast
import pathlib
from pathlib import Path

import pytest
import yaml

import mapper
from mapper.reqharness import derive, reviews, signing
from mapper.reqharness.chain import append_policy, propose, verify_chain
from mapper.reqharness.config import create_registry, email_sha256, load_config
from mapper.reqharness.records import (
    AlreadySignedError,
    Config,
    Person,
    ReqClass,
    ReleaseRule,
    ReviewLimitError,
    SigningRefused,
)
from tests.test_reqharness_chain import _fork_parts, _write_docs
from tests.test_reqharness_registry import (
    CANON_HEADER,
    HLR_FIELDS,
    T0,
    T2,
    T3,
    T4,
    T5,
    _ONE_ROW,
    _add_ana,
    _config_doc,
    _grant_reviewer,
    _record_review,
    _row,
    _seed,
    _set_authors,
)


def _write_canon(root: Path, text: str) -> None:
    (root / "REQUIREMENTS.md").write_text(text, encoding="utf-8", newline="\n")


def _confirm(root: Path, object_id: str = "HLR-TEST.1"):
    """The sign intent's (digest, head, owning_batch) at the current state."""
    config = load_config(root)
    report = verify_chain(root)
    canon, _ = derive.load_canon(root)
    obj = next(c for c in canon if c.id == object_id)
    cls = next(c for c in config.classes if c.id == obj.class_id)
    normative, _ = derive.object_digests(cls, obj.fields)
    return normative, report.head, obj.owning_batch


def _grant(root: Path, person_id: str, role: str, *, now: str) -> None:
    assert (
        propose(
            root,
            requester="bob",
            action="grant",
            person=person_id,
            role=role,
            now=now,
        )
        is None
    )


def _tamper_chain(root: Path) -> None:
    """Corrupt the grant event (not the policy event), so the chain link stops
    recomputing while the policy prefix (and its config_hash) stays verified —
    a pure chain tamper, reported `tampered` (not `unapproved_config`)."""
    roles = root / "reqharness" / "roles.yml"
    text = roles.read_text(encoding="utf-8")
    assert "person: ana" in text
    roles.write_text(
        text.replace("person: ana", "person: mallory", 1),
        encoding="utf-8",
        newline="\n",
    )


def _row_batch(object_id: str, statement: str, status: str, batch: str, rationale: str = "") -> str:
    return f"| {object_id} | {statement} | {rationale} | {batch} | {status} |\n"


# ---------------------------------------------------------------------------
# `entitled_to_sign` — the 10-arm truth table + the two `(True, "")` cases
# ---------------------------------------------------------------------------


def test_entitled_to_sign_requires_the_designated_role_at_the_current_head(tmp_path):
    """LLR-RS.2.2 (M-RS6): the no-role arm — ana is a declared person but holds
    no `req-reviewer` at the current head — and the entitled case, where ana
    holds TWO roles (req-reviewer + admin) and the designated one suffices."""
    _seed(tmp_path)
    _add_ana(tmp_path)  # ana is a person, NOT yet a reviewer
    _write_canon(tmp_path, _ONE_ROW)

    assert signing.entitled_to_sign(
        tmp_path, "HLR-TEST.1", "ana@example.invalid"
    ) == (False, signing.REASON_NO_ROLE)

    _grant_reviewer(tmp_path)  # ana holds req-reviewer at head 3
    _grant(tmp_path, "ana", "admin", now=T3)  # a second, non-designated role
    assert signing.entitled_to_sign(
        tmp_path, "HLR-TEST.1", "ana@example.invalid"
    ) == (True, "")


def test_entitled_to_sign_truth_table_includes_retired_and_class_undeclared(tmp_path):
    """LLR-RS.2.2 (M-RS7): the retired arm — a withdrawn object is refused even
    though the signer holds the role — and the class-undeclared arm — an LLR
    object in a registry that declares only the HLR class."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)
    retired_canon = CANON_HEADER + _row("HLR-TEST.1", "x", "withdrawn (deferred)")
    _write_canon(tmp_path, retired_canon)
    assert signing.entitled_to_sign(
        tmp_path, "HLR-TEST.1", "ana@example.invalid"
    ) == (False, signing.REASON_RETIRED)

    no_llr = tmp_path / "no_llr"
    no_llr.mkdir()
    create_registry(
        no_llr, person="bob", name="Bob Admin", email="bob@example.invalid", now=T0,
        classes=(
            {
                "id": "HLR",
                "reviewer_role": "req-reviewer",
                "normative_fields": ["statement"],
                "informative_fields": [],
            },
        ),
    )
    _write_canon(no_llr, CANON_HEADER + _row("LLR-TEST.1", "x", "active"))
    assert signing.entitled_to_sign(
        no_llr, "LLR-TEST.1", "bob@example.invalid"
    ) == (False, signing.REASON_CLASS_UNDECLARED)


def test_entitled_to_sign_refuses_an_author_of_the_object_batch(tmp_path):
    """LLR-RS.2.2 / HLR-RS.5 (M-RS19): the author arm — ana holds the
    reviewer role AND is a declared author of the object's batch, so the ONLY
    failing check is authorship — and the blank-`Owning batch` case, where
    authorship is not recorded and signing is allowed on that ground."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)
    _set_authors(tmp_path, {"2026-10-11-reqharness-batch": ["ana"]})
    _write_canon(tmp_path, _ONE_ROW)
    assert signing.entitled_to_sign(
        tmp_path, "HLR-TEST.1", "ana@example.invalid"
    ) == (False, signing.REASON_AUTHOR)

    blank = tmp_path / "blank"
    blank.mkdir()
    _seed(blank)
    _add_ana(blank)
    _grant_reviewer(blank)
    blank_canon = CANON_HEADER + "| HLR-TEST.1 | x |  |  | active |\n"
    _write_canon(blank, blank_canon)
    assert signing.entitled_to_sign(
        blank, "HLR-TEST.1", "ana@example.invalid"
    ) == (True, "")


def test_entitled_to_sign_truth_table_chain_arms(tmp_path):
    """LLR-RS.2.2 (M-RS8): the tampered / forked / no-registry arms — each a
    single-failure fixture over a chain that does not verify."""
    tampered = tmp_path / "tampered"
    tampered.mkdir()
    _seed(tampered)
    _add_ana(tampered)
    _grant_reviewer(tampered)
    _tamper_chain(tampered)
    assert signing.entitled_to_sign(
        tampered, "HLR-TEST.1", "ana@example.invalid"
    ) == (False, signing.REASON_TAMPERED)

    forked = tmp_path / "forked"
    forked.mkdir()
    base, child_a, child_b = _fork_parts(forked)
    _write_docs(forked, [*base, child_a, child_b])
    assert signing.entitled_to_sign(
        forked, "HLR-TEST.1", "ana@example.invalid"
    ) == (False, signing.REASON_FORKED)

    empty = tmp_path / "empty"
    empty.mkdir()
    assert signing.entitled_to_sign(
        empty, "HLR-TEST.1", "ana@example.invalid"
    ) == (False, signing.REASON_NO_REGISTRY)


def test_entitled_to_sign_truth_table_identity_and_object_arms(tmp_path, monkeypatch):
    """LLR-RS.2.2 (M-RS14): the unknown-viewer, ambiguous-viewer and
    unknown-object arms — each a single-failure fixture."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)
    _write_canon(tmp_path, _ONE_ROW)

    assert signing.entitled_to_sign(
        tmp_path, "HLR-TEST.1", "nobody@example.invalid"
    ) == (False, signing.REASON_UNKNOWN_VIEWER)

    assert signing.entitled_to_sign(
        tmp_path, "HLR-NOPE.9", "ana@example.invalid"
    ) == (False, signing.REASON_UNKNOWN_OBJECT)

    # ambiguous-viewer: two declared people sharing one resolved hash (the
    # config now refuses duplicate emails, so the arm is exercised through a
    # hand-built config — the defensive check the duplicate-id refusal and this
    # predicate share).  The hand-built config's digest differs from the policy
    # in force, so F6 (the `unapproved_config` arm, checked first) is pinned to
    # pass here — only the ambiguity arm may fire.
    shared = email_sha256("ana@example.invalid")
    ambiguous = Config(
        version="1",
        people=(
            Person(id="ana", name="Ana", email_sha256=shared),
            Person(id="reviewer-2", name="Reviewer Two", email_sha256=shared),
        ),
        roles=("req-reviewer",),
        classes=(
            ReqClass(
                id="HLR",
                reviewer_role="req-reviewer",
                normative_fields=("statement",),
                informative_fields=(),
            ),
        ),
        release_rules=(ReleaseRule(id="all_active_reviewed"),),
        authors=(),
    )
    with monkeypatch.context() as m:
        m.setattr(signing, "load_config", lambda repo: ambiguous)
        m.setattr(signing, "config_digest", lambda config: verify_chain(tmp_path).policy_config_hash)
        assert signing.entitled_to_sign(
            tmp_path, "HLR-TEST.1", "ana@example.invalid"
        ) == (False, signing.REASON_AMBIGUOUS_VIEWER)


def test_entitled_to_sign_refuses_an_unapproved_config(tmp_path):
    """LLR-RS.2.2 (F6 / M-RS29): the live config's digest differs from the
    newest verified policy event's — `entitled_to_sign` refuses
    `unapproved_config`, agreeing with `sign_review` on the one config gate."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)
    _write_canon(tmp_path, _ONE_ROW)

    path, document = _config_doc(tmp_path)
    document["people"].append(
        {"id": "subject", "name": "Subject", "email_sha256": email_sha256("subject@example.invalid")}
    )
    path.write_text(
        yaml.safe_dump(document, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
        newline="\n",
    )
    assert signing.entitled_to_sign(
        tmp_path, "HLR-TEST.1", "ana@example.invalid"
    ) == (False, signing.REASON_UNAPPROVED_CONFIG)


# ---------------------------------------------------------------------------
# `sign_review` — the orchestrated write path
# ---------------------------------------------------------------------------


def test_sign_review_writes_a_record_that_derive_reads_as_reviewed(tmp_path):
    """LLR-RS.2.1 (B4 output-then-consume): sign_review writes ONE record whose
    `kind`/`verdict`/`note`/`class_id`/`reviewer`/`owning_batch` are fixed and
    whose `class_id` comes from the canon object (an LLR object writes `LLR`,
    not a hard-coded `HLR`); `derive` re-reads it as `reviewed`."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)
    _write_canon(tmp_path, _ONE_ROW)

    digest, head, batch = _confirm(tmp_path)
    path = signing.sign_review(
        tmp_path, "HLR-TEST.1", "ana@example.invalid",
        confirm_digest=digest, confirm_head=head, confirm_owning_batch=batch, now=T4,
    )
    assert path.exists()
    by_name = {e.name: e for e in reviews.load_reviews(tmp_path).events}
    event = by_name[path.name]
    assert event.kind == "human"
    assert event.verdict == "reviewed"
    assert event.note == ""
    assert event.class_id == "HLR"
    assert event.reviewer == "ana"
    assert event.owning_batch == batch

    result, _ = _derive(tmp_path, _ONE_ROW)
    assert result.states["HLR-TEST.1"] == derive.STATE_REVIEWED

    # an LLR object: the record writes the canon class_id, not the id prefix
    lr_canon = CANON_HEADER + _row("LLR-TEST.1", "x", "active")
    _write_canon(tmp_path, lr_canon)
    digest, head, batch = _confirm(tmp_path, "LLR-TEST.1")
    path2 = signing.sign_review(
        tmp_path, "LLR-TEST.1", "ana@example.invalid",
        confirm_digest=digest, confirm_head=head, confirm_owning_batch=batch, now=T4,
    )
    by_name = {e.name: e for e in reviews.load_reviews(tmp_path).events}
    assert by_name[path2.name].class_id == "LLR"


def test_sign_review_refuses_on_tampered_or_forked_or_no_registry(tmp_path):
    """LLR-RS.2.1: sign_review refuses a tampered chain, a forked chain and a
    repo with no registry — each with the named reason and nothing written."""
    tampered = tmp_path / "tampered"
    tampered.mkdir()
    _seed(tampered)
    _add_ana(tampered)
    _grant_reviewer(tampered)
    _write_canon(tampered, _ONE_ROW)
    digest, head, batch = _confirm(tampered)
    _tamper_chain(tampered)
    with pytest.raises(SigningRefused) as exc:
        signing.sign_review(
            tampered, "HLR-TEST.1", "ana@example.invalid",
            confirm_digest=digest, confirm_head=head, confirm_owning_batch=batch, now=T4,
        )
    assert exc.value.reason == signing.REASON_TAMPERED
    assert not (tampered / "reqharness" / "reviews").exists()

    forked = tmp_path / "forked"
    forked.mkdir()
    base, child_a, child_b = _fork_parts(forked)
    _write_docs(forked, [*base, child_a, child_b])
    with pytest.raises(SigningRefused) as exc:
        signing.sign_review(
            forked, "HLR-TEST.1", "ana@example.invalid",
            confirm_digest="ab" * 32, confirm_head=(3, "cd" * 32),
            confirm_owning_batch="", now=T4,
        )
    assert exc.value.reason == signing.REASON_FORKED
    assert not (forked / "reqharness" / "reviews").exists()

    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(SigningRefused) as exc:
        signing.sign_review(
            empty, "HLR-TEST.1", "ana@example.invalid",
            confirm_digest="ab" * 32, confirm_head=(1, "cd" * 32),
            confirm_owning_batch="", now=T4,
        )
    assert exc.value.reason == signing.REASON_NO_REGISTRY


def test_sign_review_freezes_the_clock_via_now(tmp_path):
    """LLR-RS.2.1: `now` is the record's `time` verbatim — the clock is frozen
    so the content-named file is deterministic; `now=None` would use UTC."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)
    _write_canon(tmp_path, _ONE_ROW)
    digest, head, batch = _confirm(tmp_path)
    fixed = "2026-10-11T09:09:09Z"
    path = signing.sign_review(
        tmp_path, "HLR-TEST.1", "ana@example.invalid",
        confirm_digest=digest, confirm_head=head, confirm_owning_batch=batch, now=fixed,
    )
    by_name = {e.name: e for e in reviews.load_reviews(tmp_path).events}
    assert by_name[path.name].time == fixed


def test_sign_review_refuses_an_unapproved_config(tmp_path):
    """LLR-RS.2.1 (F6 / M-RS29): the live config's digest differs from the
    newest verified policy event's — refused `unapproved_config`, nothing
    written."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)
    _write_canon(tmp_path, _ONE_ROW)
    digest, head, batch = _confirm(tmp_path)

    path, document = _config_doc(tmp_path)
    document["people"].append(
        {"id": "subject", "name": "Subject", "email_sha256": email_sha256("subject@example.invalid")}
    )
    path.write_text(
        yaml.safe_dump(document, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(SigningRefused) as exc:
        signing.sign_review(
            tmp_path, "HLR-TEST.1", "ana@example.invalid",
            confirm_digest=digest, confirm_head=head, confirm_owning_batch=batch, now=T4,
        )
    assert exc.value.reason == signing.REASON_UNAPPROVED_CONFIG
    assert not (tmp_path / "reqharness" / "reviews").exists()


def test_sign_review_refuses_when_the_object_digest_head_or_role_moved(tmp_path):
    """LLR-RS.2.1 / TC-RS-2.2.2 (M-RS5): the four TOCTOU codes — object, digest,
    head and role each moved between the arm and the confirm, one reason code
    each, nothing written."""
    digest_moved = tmp_path / "digest"
    digest_moved.mkdir()
    _seed(digest_moved)
    _add_ana(digest_moved)
    _grant_reviewer(digest_moved)
    _write_canon(digest_moved, _ONE_ROW)
    digest, head, batch = _confirm(digest_moved)
    edited = CANON_HEADER + _row(
        "HLR-TEST.1", "The system shall verify twice.", "active", HLR_FIELDS["rationale"]
    )
    _write_canon(digest_moved, edited)
    with pytest.raises(SigningRefused) as exc:
        signing.sign_review(
            digest_moved, "HLR-TEST.1", "ana@example.invalid",
            confirm_digest=digest, confirm_head=head, confirm_owning_batch=batch, now=T4,
        )
    assert exc.value.reason == signing.REASON_MOVED_DIGEST
    assert not (digest_moved / "reqharness" / "reviews").exists()

    head_moved = tmp_path / "head"
    head_moved.mkdir()
    _seed(head_moved)
    _add_ana(head_moved)
    _grant_reviewer(head_moved)
    _write_canon(head_moved, _ONE_ROW)
    digest, head, batch = _confirm(head_moved)
    _grant(head_moved, "ana", "admin", now=T3)  # head moves, role still held
    with pytest.raises(SigningRefused) as exc:
        signing.sign_review(
            head_moved, "HLR-TEST.1", "ana@example.invalid",
            confirm_digest=digest, confirm_head=head, confirm_owning_batch=batch, now=T4,
        )
    assert exc.value.reason == signing.REASON_MOVED_HEAD
    assert not (head_moved / "reqharness" / "reviews").exists()

    role_moved = tmp_path / "role"
    role_moved.mkdir()
    _seed(role_moved)
    _add_ana(role_moved)
    _grant_reviewer(role_moved)
    _write_canon(role_moved, _ONE_ROW)
    digest, head, batch = _confirm(role_moved)
    assert (
        propose(
            role_moved, requester="bob", action="revoke",
            person="ana", role="req-reviewer", now=T3,
        )
        is None
    )
    with pytest.raises(SigningRefused) as exc:
        signing.sign_review(
            role_moved, "HLR-TEST.1", "ana@example.invalid",
            confirm_digest=digest, confirm_head=head, confirm_owning_batch=batch, now=T4,
        )
    assert exc.value.reason == signing.REASON_MOVED_ROLE
    assert not (role_moved / "reqharness" / "reviews").exists()

    object_moved = tmp_path / "object"
    object_moved.mkdir()
    _seed(object_moved)
    _add_ana(object_moved)
    _grant_reviewer(object_moved)
    _write_canon(object_moved, _ONE_ROW)
    digest, head, batch = _confirm(object_moved)
    new_batch = CANON_HEADER + _row_batch(
        "HLR-TEST.1", HLR_FIELDS["statement"], "active", "some-other-batch",
        HLR_FIELDS["rationale"],
    )
    _write_canon(object_moved, new_batch)
    with pytest.raises(SigningRefused) as exc:
        signing.sign_review(
            object_moved, "HLR-TEST.1", "ana@example.invalid",
            confirm_digest=digest, confirm_head=head,
            confirm_owning_batch=batch, now=T4,
        )
    assert exc.value.reason == signing.REASON_MOVED_OBJECT
    assert not (object_moved / "reqharness" / "reviews").exists()

    both_moved = tmp_path / "both"
    both_moved.mkdir()
    _seed(both_moved)
    _add_ana(both_moved)
    _grant_reviewer(both_moved)
    _write_canon(both_moved, _ONE_ROW)
    digest, head, batch = _confirm(both_moved)
    moved_content_and_batch = CANON_HEADER + _row_batch(
        "HLR-TEST.1", "The system shall verify twice.", "active", "some-other-batch",
        HLR_FIELDS["rationale"],
    )
    _write_canon(both_moved, moved_content_and_batch)
    with pytest.raises(SigningRefused) as exc:
        signing.sign_review(
            both_moved, "HLR-TEST.1", "ana@example.invalid",
            confirm_digest=digest, confirm_head=head,
            confirm_owning_batch=batch, now=T4,
        )
    # the documented precedence: `moved_object` is checked first, so an object
    # AND digest both moved reports `moved_object`, not `moved_digest`.
    assert exc.value.reason == signing.REASON_MOVED_OBJECT
    assert not (both_moved / "reqharness" / "reviews").exists()


def test_sign_review_refuses_already_signed_identical_content(tmp_path, monkeypatch):
    """LLR-RS.2.4 (M-RS22): identical content signed twice — the same seq and
    `now` (two concurrent signers) — is the content-named collision, refused
    `already_signed`, nothing new written."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)
    _write_canon(tmp_path, _ONE_ROW)
    digest, head, batch = _confirm(tmp_path)

    monkeypatch.setattr(signing, "next_seq", lambda repo: 1)
    first = signing.sign_review(
        tmp_path, "HLR-TEST.1", "ana@example.invalid",
        confirm_digest=digest, confirm_head=head, confirm_owning_batch=batch, now=T4,
    )
    assert first.exists()
    with pytest.raises(SigningRefused) as exc:
        signing.sign_review(
            tmp_path, "HLR-TEST.1", "ana@example.invalid",
            confirm_digest=digest, confirm_head=head, confirm_owning_batch=batch, now=T4,
        )
    assert exc.value.reason == signing.REASON_ALREADY_SIGNED


def test_sign_review_refuses_at_the_review_file_count_limit(tmp_path, monkeypatch):
    """LLR-RS.2.4 (M-RS22): the review-file count limit is reached — refused
    `review_limit`, nothing written."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)
    _record_review(tmp_path, "HLR-A.1", HLR_FIELDS, now=T3)
    _record_review(tmp_path, "HLR-B.1", HLR_FIELDS, now=T4)
    _write_canon(tmp_path, _ONE_ROW)
    digest, head, batch = _confirm(tmp_path)
    monkeypatch.setattr(reviews, "LIMIT_REVIEW_FILE_COUNT", 1)
    with pytest.raises(SigningRefused) as exc:
        signing.sign_review(
            tmp_path, "HLR-TEST.1", "ana@example.invalid",
            confirm_digest=digest, confirm_head=head, confirm_owning_batch=batch, now=T4,
        )
    assert exc.value.reason == signing.REASON_REVIEW_LIMIT


def _resolve_relative(package: str, level: int, module: str) -> str:
    """The absolute dotted target of an `ImportFrom`: an absolute (`level 0`)
    import is its `module` verbatim; a relative import starts at the importing
    file's `package` (dotted), climbs `level - 1` packages, then appends `module`."""
    if level == 0:
        return module
    parts = package.split(".") if package else []
    for _ in range(level - 1):
        if parts:
            parts.pop()
    if module:
        parts.extend(module.split("."))
    return ".".join(parts)


def _imports_signing(source: str, *, package: str) -> bool:
    """True when *source* imports `signing` through any accepted form: the
    absolute (`from mapper.reqharness.signing import x`, `import
    mapper.reqharness.signing`), the package-qualified (`from mapper.reqharness
    import signing`), any relative `ImportFrom` that resolves from the importing
    file's `package` to `mapper.reqharness.signing` or to `mapper.reqharness`
    with `signing` among the imported names, and any string literal containing
    `reqharness.signing` (dynamic `import_module` / `__import__`)."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "mapper.reqharness.signing" or alias.name.startswith(
                    "mapper.reqharness.signing."
                ):
                    return True
        elif isinstance(node, ast.ImportFrom):
            target = _resolve_relative(package, node.level, node.module or "")
            names = {alias.name for alias in node.names}
            if target == "mapper.reqharness.signing" or target.startswith(
                "mapper.reqharness.signing."
            ):
                return True
            if target == "mapper.reqharness" and "signing" in names:
                return True
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if "reqharness.signing" in node.value:
                return True
    return False


#: The only importers `signing` permits (LLR-RS.2.4): `screens/review.py` (the
#: RS2 screen, not yet written) and the test file that tests `signing` itself.
ALLOWED_SIGNING_IMPORTERS = {"screens/review.py", "tests/test_reqharness_signing.py"}


def _signing_importers() -> set[str]:
    """Every module under `mapper/` or `tests/` that imports `signing`, by
    relative path (mapper files relative to the package, test files relative to
    the repo root)."""
    root = pathlib.Path(mapper.__file__).parent.parent
    pkg = pathlib.Path(mapper.__file__).parent
    paths = [*pkg.rglob("*.py"), *root.joinpath("tests").rglob("*.py")]
    importers: set[str] = set()
    for path in sorted(paths):
        package = ".".join(path.parent.relative_to(root).parts)
        if _imports_signing(path.read_text(encoding="utf-8"), package=package):
            try:
                importers.add(path.relative_to(pkg).as_posix())
            except ValueError:
                importers.add(path.relative_to(root).as_posix())
    return importers


def test_signing_import_forms_are_all_detected():
    """LLR-RS.2.4 (F2 fix): every import form that reaches `signing` is caught —
    the absolute, package-qualified, relative (resolved from the importing
    file's package) and dynamic (`import_module` / `__import__` string literal)
    forms — and a relative import only reaches `signing` when its package path
    resolves there."""
    detected = [
        ("from mapper.reqharness.signing import sign_review\n", "mapper"),
        ("import mapper.reqharness.signing\n", "mapper"),
        ("from mapper.reqharness import signing\n", "mapper"),
        ("from . import signing\n", "mapper.reqharness"),
        ("from .signing import sign_review\n", "mapper.reqharness"),
        ("from .reqharness import signing\n", "mapper"),
        ("from ..reqharness.signing import sign_review\n", "mapper.screens"),
        ('importlib.import_module("mapper.reqharness.signing")\n', "mapper"),
        ('__import__("mapper.reqharness.signing")\n', "mapper"),
    ]
    for source, package in detected:
        assert _imports_signing(source, package=package), source

    undetected = [
        ("from . import signing\n", "mapper"),
        ("from .signing import sign_review\n", "mapper"),
        ("from .signing import sign_review\n", "mapper.screens"),
        ("from ..reqharness import signing\n", "mapper"),
        ('importlib.import_module("mapper.reqharness")\n', "mapper"),
    ]
    for source, package in undetected:
        assert not _imports_signing(source, package=package), source


def test_sign_review_has_no_cli_or_entry_point_exposure():
    """LLR-RS.2.4 (M-RS23): `signing` has no console_scripts entry, no `--sign`
    flag in `app.py`, and only the allowlisted importers (`screens/review.py`,
    the RS2 screen not yet written, and this test file) may import it — pinned
    by AST and the shipped `pyproject.toml`."""
    root = pathlib.Path(mapper.__file__).parent.parent
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    scripts = pyproject.split("[project.scripts]")[1].split("[")[0]
    assert "signing" not in scripts

    app = (pathlib.Path(mapper.__file__).parent / "app.py").read_text(encoding="utf-8")
    assert "--sign" not in app

    assert _signing_importers() <= ALLOWED_SIGNING_IMPORTERS


def test_sign_review_loads_config_chain_and_canon_exactly_once(tmp_path, monkeypatch):
    """LLR-RS.2.1 (F1 fix): the role/author decision runs on sign_review's OWN
    snapshot — `safe_verify`, `load_config` and `load_canon` each run EXACTLY
    ONCE per sign_review (no second load)."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)
    _write_canon(tmp_path, _ONE_ROW)
    digest, head, batch = _confirm(tmp_path)

    calls = {"verify": 0, "config": 0, "canon": 0}
    real_verify, real_config, real_canon = (
        signing.safe_verify,
        signing.load_config,
        signing.load_canon,
    )

    def counting_verify(repo):
        calls["verify"] += 1
        return real_verify(repo)

    def counting_config(repo):
        calls["config"] += 1
        return real_config(repo)

    def counting_canon(repo):
        calls["canon"] += 1
        return real_canon(repo)

    monkeypatch.setattr(signing, "safe_verify", counting_verify)
    monkeypatch.setattr(signing, "load_config", counting_config)
    monkeypatch.setattr(signing, "load_canon", counting_canon)

    path = signing.sign_review(
        tmp_path, "HLR-TEST.1", "ana@example.invalid",
        confirm_digest=digest, confirm_head=head, confirm_owning_batch=batch, now=T4,
    )
    assert path.exists()
    assert calls == {"verify": 1, "config": 1, "canon": 1}


def test_sign_review_confirm_owning_batch_is_a_required_keyword(tmp_path):
    """LLR-RS.2.1 (F3 fix): `confirm_owning_batch` has no default — it is a
    required keyword (the RS2 screen passes its sign-intent owning batch)."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)
    _write_canon(tmp_path, _ONE_ROW)
    digest, head, _ = _confirm(tmp_path)
    with pytest.raises(TypeError):
        signing.sign_review(
            tmp_path, "HLR-TEST.1", "ana@example.invalid",
            confirm_digest=digest, confirm_head=head, now=T4,
        )


def test_two_signers_different_content_both_write_and_duplicate_seq_is_tolerated(
    tmp_path, monkeypatch
):
    """LLR-RS.2.4 (F5): two different entitled signers sign the SAME object with
    different content → two review files exist, both load, the duplicate `seq`
    tolerated (nothing reads seq)."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    path, document = _config_doc(tmp_path)
    document["people"].append(
        {
            "id": "reviewer-2",
            "name": "Reviewer Two",
            "email_sha256": email_sha256("reviewer-2@example.invalid"),
        }
    )
    path.write_text(
        yaml.safe_dump(document, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
        newline="\n",
    )
    append_policy(tmp_path, approved_by="bob", note="add reviewer-2", now=T2)
    _grant_reviewer(tmp_path, now=T3)
    _grant(tmp_path, "reviewer-2", "req-reviewer", now=T4)

    _write_canon(tmp_path, _ONE_ROW)
    digest, head, batch = _confirm(tmp_path)
    monkeypatch.setattr(signing, "next_seq", lambda repo: 1)

    first = signing.sign_review(
        tmp_path, "HLR-TEST.1", "ana@example.invalid",
        confirm_digest=digest, confirm_head=head, confirm_owning_batch=batch, now=T5,
    )
    assert first.exists()

    edited = CANON_HEADER + _row(
        "HLR-TEST.1", "The system shall verify twice.", "active",
        HLR_FIELDS["rationale"],
    )
    _write_canon(tmp_path, edited)
    digest2, head2, batch2 = _confirm(tmp_path)
    second = signing.sign_review(
        tmp_path, "HLR-TEST.1", "reviewer-2@example.invalid",
        confirm_digest=digest2, confirm_head=head2, confirm_owning_batch=batch2,
        now=T5,
    )
    assert second.exists()
    assert first != second

    scan = reviews.load_reviews(tmp_path)
    by_name = {e.name: e for e in scan.events}
    assert set(by_name) == {first.name, second.name}
    assert by_name[first.name].reviewer == "ana"
    assert by_name[second.name].reviewer == "reviewer-2"
    assert by_name[first.name].seq == 1
    assert by_name[second.name].seq == 1  # duplicate seq tolerated


def test_sign_review_maps_typed_review_errors_not_message_text(tmp_path, monkeypatch):
    """LLR-RS.2.4 (F6 fix): the `already_signed` / `review_limit` mapping is by
    TYPE (AlreadySignedError / ReviewLimitError), never by message text — a
    typed error whose message lacks the old prose still maps to its code."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)
    _write_canon(tmp_path, _ONE_ROW)
    digest, head, batch = _confirm(tmp_path)

    def _boom(exc):
        def _raise(*_args, **_kwargs):
            raise exc

        return _raise

    monkeypatch.setattr(
        signing, "record_review", _boom(AlreadySignedError("typed collision"))
    )
    with pytest.raises(SigningRefused) as exc:
        signing.sign_review(
            tmp_path, "HLR-TEST.1", "ana@example.invalid",
            confirm_digest=digest, confirm_head=head, confirm_owning_batch=batch,
            now=T4,
        )
    assert exc.value.reason == signing.REASON_ALREADY_SIGNED

    monkeypatch.setattr(
        signing, "next_seq", _boom(ReviewLimitError("typed limit"))
    )
    with pytest.raises(SigningRefused) as exc:
        signing.sign_review(
            tmp_path, "HLR-TEST.1", "ana@example.invalid",
            confirm_digest=digest, confirm_head=head, confirm_owning_batch=batch,
            now=T4,
        )
    assert exc.value.reason == signing.REASON_REVIEW_LIMIT


def _derive(root: Path, canon_text: str):
    config = load_config(root)
    report = verify_chain(root)
    scan = reviews.load_reviews(root)
    canon, canon_reported = derive.parse_canon(canon_text)
    result = derive.derive_states(canon, scan, report, config)
    return result, tuple(result.reported) + tuple(canon_reported)


__all__ = [
    "test_entitled_to_sign_requires_the_designated_role_at_the_current_head",
    "test_entitled_to_sign_truth_table_includes_retired_and_class_undeclared",
    "test_entitled_to_sign_refuses_an_author_of_the_object_batch",
    "test_entitled_to_sign_truth_table_chain_arms",
    "test_entitled_to_sign_truth_table_identity_and_object_arms",
    "test_entitled_to_sign_refuses_an_unapproved_config",
    "test_sign_review_writes_a_record_that_derive_reads_as_reviewed",
    "test_sign_review_refuses_on_tampered_or_forked_or_no_registry",
    "test_sign_review_freezes_the_clock_via_now",
    "test_sign_review_refuses_an_unapproved_config",
    "test_sign_review_refuses_when_the_object_digest_head_or_role_moved",
    "test_sign_review_refuses_already_signed_identical_content",
    "test_sign_review_refuses_at_the_review_file_count_limit",
    "test_sign_review_has_no_cli_or_entry_point_exposure",
    "test_signing_import_forms_are_all_detected",
    "test_sign_review_loads_config_chain_and_canon_exactly_once",
    "test_sign_review_confirm_owning_batch_is_a_required_keyword",
    "test_two_signers_different_content_both_write_and_duplicate_seq_is_tolerated",
    "test_sign_review_maps_typed_review_errors_not_message_text",
]
