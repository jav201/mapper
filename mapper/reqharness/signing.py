"""Headless review signing: the entitlement predicate and the orchestrated
write path (HLR-RS.2 / HLR-RS.3 / HLR-RS.5).

`entitled_to_sign(repo, object_id, identity_email) -> (bool, reason)` is the
one pre-flight predicate: it resolves the git identity EMAIL to EXACTLY ONE
declared person (zero or several are each a named refusal — A3), and returns
`(True, "")` only when the chain verifies, the identity resolves, the object
exists, is ACTIVE (not withdrawn/retired) and its class is declared, the
resolved viewer holds the class's `reviewer_role` in `effective_roles(report)`
at the current head, and the viewer is NOT an author of the object's owning
batch.  Every failure is a named reason code; nothing is written.

`sign_review(repo, object_id, identity_email, *, confirm_digest, confirm_head,
confirm_owning_batch, now=None) -> Path` orchestrates the write through
the existing `reviews.record_review` API (immutable, content-named, exclusive
create).  One snapshot is threaded through the entitlement check, the
confirm comparison and the write: it loads the config and chain ONCE, refuses
unless `config_digest(config) == report.policy_config_hash`
(`unapproved_config`, F6), resolves the object and its class, then re-checks
the confirmed object/digest/head against the current snapshot with the fixed
reason-code precedence (`moved_object` · `moved_digest` · `moved_head` ·
`moved_role`; an object gone is `unknown_object`, a revoke that loses the role
is `moved_role` else `moved_head`).  The role/author decision runs through the
pure `entitlement` predicate on that same snapshot — no second load.  Loader
`ValidationError`s are converted to `SigningRefused` — never a bare exception
into the worker (A4); the review store's typed refusals (`ReviewLimitError`,
`AlreadySignedError`) map to `review_limit` / `already_signed` by type, never
by message text.  The record is written with `class_id` from the canon object,
`verdict="reviewed"`, `kind="human"`, `note=""`, the object's owning batch
stored (F1), and the current head.

The module is headless (docs/ARCHITECTURE.md §3): it imports no Textual, no
Rich and no identity reader — it RECEIVES the identity email (the screen
resolves it, R1/A3).
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from mapper.reqharness.chain import (
    STATUS_TAMPERED,
    ChainReport,
    effective_roles,
)
from mapper.reqharness.config import config_digest, email_sha256, load_config
from mapper.reqharness.derive import CanonObject, load_canon, object_digests
from mapper.reqharness.records import (
    REASON_AUTHOR,
    REASON_NO_ROLE,
    AlreadySignedError,
    Config,
    ReviewLimitError,
    SigningRefused,
    ValidationError,
)
from mapper.reqharness.release import safe_verify
from mapper.reqharness.reviews import next_seq, record_review

# The signing-refusal reason codes (the `entitled_to_sign` truth-table arms,
# the `moved_*` TOCTOU codes and the write refusals).  `no_role` and `author`
# are shared with `derive`'s `unentitled` causes (records.py).
REASON_TAMPERED = "tampered"
REASON_FORKED = "forked"
REASON_NO_REGISTRY = "no_registry"
REASON_UNKNOWN_VIEWER = "unknown_viewer"
REASON_AMBIGUOUS_VIEWER = "ambiguous_viewer"
REASON_UNKNOWN_OBJECT = "unknown_object"
REASON_RETIRED = "retired"
REASON_CLASS_UNDECLARED = "class_undeclared"
REASON_MOVED_OBJECT = "moved_object"
REASON_MOVED_DIGEST = "moved_digest"
REASON_MOVED_HEAD = "moved_head"
REASON_MOVED_ROLE = "moved_role"
REASON_ALREADY_SIGNED = "already_signed"
REASON_REVIEW_LIMIT = "review_limit"
REASON_UNAPPROVED_CONFIG = "unapproved_config"


def _utc_now() -> str:
    """`now=None` means UTC now (the record `time` field's exact shape)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def chain_reason(report: ChainReport) -> str:
    """The named reason for a chain that does not verify: tampered, forked,
    or (the not-verifiable bucket) `no_registry` — a broken chain or a repo
    with no registry at all.  Public so the screen's arm-time check reads the
    SAME mapping the write path uses, instead of copying the fork match."""
    if report.status == STATUS_TAMPERED:
        return REASON_TAMPERED
    if report.status.startswith("chain forked"):
        return REASON_FORKED
    return REASON_NO_REGISTRY


def _viewer(config: Config, identity_email: str) -> tuple[str | None, str]:
    """Resolve the git identity email to EXACTLY ONE declared person id.
    Zero matches -> `unknown_viewer`; several -> `ambiguous_viewer`."""
    hashed = email_sha256(identity_email)
    matches = [person.id for person in config.people if person.email_sha256 == hashed]
    if not matches:
        return None, REASON_UNKNOWN_VIEWER
    if len(matches) > 1:
        return None, REASON_AMBIGUOUS_VIEWER
    return matches[0], ""


def _classes(config: Config) -> dict[str, object]:
    return {cls.id: cls for cls in config.classes}


def _find_object(
    canon: tuple[CanonObject, ...], object_id: str
) -> CanonObject | None:
    for obj in canon:
        if obj.id == object_id:
            return obj
    return None


def _retired(obj: CanonObject) -> bool:
    return obj.fields.get("status", "").lower().startswith("withdrawn")


def _unapproved_config(report: ChainReport, config: Config) -> bool:
    """F6: the live config's digest differs from the newest verified policy
    event's `config_hash` — the one check both `entitled_to_sign` and
    `sign_review` share, so a config mismatch reads `unapproved_config` (not
    the generic `tampered`) in BOTH functions."""
    return (
        report.policy_config_hash is not None
        and config_digest(config) != report.policy_config_hash
    )


def _authors_map(config: Config) -> dict[str, tuple[str, ...]]:
    return {batch: people for batch, people in config.authors}


def entitlement(
    report: ChainReport,
    config: Config,
    canon: tuple[CanonObject, ...],
    viewer: str,
    object_id: str,
) -> tuple[bool, str]:
    """The pure entitlement decision over ONE already-loaded snapshot: the
    live config is the approved policy (F6, `unapproved_config`), the object
    exists, is active (not withdrawn/retired), its class is declared, the
    viewer holds the class's reviewer role at the current head, and the viewer
    is not an author of the object's owning batch.  PURE — no loads; the caller
    owns the snapshot (config, canon and report are threaded from
    `entitled_to_sign`'s or `sign_review`'s single load).  Public so the
    screen's arm-time check reuses it instead of re-deriving the decision."""
    if _unapproved_config(report, config):
        return (False, REASON_UNAPPROVED_CONFIG)
    obj = _find_object(canon, object_id)
    if obj is None:
        return (False, REASON_UNKNOWN_OBJECT)
    if _retired(obj):
        return (False, REASON_RETIRED)
    cls = _classes(config).get(obj.class_id)
    if cls is None:
        return (False, REASON_CLASS_UNDECLARED)
    if cls.reviewer_role not in effective_roles(report).get(viewer, ()):
        return (False, REASON_NO_ROLE)
    if obj.owning_batch and viewer in _authors_map(config).get(obj.owning_batch, ()):
        return (False, REASON_AUTHOR)
    return (True, "")


def entitled_to_sign(
    repo: str | Path, object_id: str, identity_email: str
) -> tuple[bool, str]:
    """The one pre-flight predicate (HLR-RS.3 / HLR-RS.5).  Returns
    `(True, "")` only when the chain verifies, the identity email resolves to
    exactly one declared person, the object exists, is active and its class is
    declared, the viewer holds the class's reviewer role at the current head,
    and the viewer is not an author of the object's owning batch.  Otherwise
    `(False, <reason>)` names exactly the failing check and writes nothing."""
    report = safe_verify(repo)
    try:
        config = load_config(repo)
    except ValidationError:
        return (False, REASON_NO_REGISTRY)
    # F6 before the generic chain refusal: an unapproved config reads
    # `unapproved_config` here exactly as `sign_review` refuses it, so the two
    # functions agree on the one config-gate arm.
    if _unapproved_config(report, config):
        return (False, REASON_UNAPPROVED_CONFIG)
    if not report.ok:
        return (False, chain_reason(report))
    viewer, reason = _viewer(config, identity_email)
    if viewer is None:
        return (False, reason)
    try:
        canon, _ = load_canon(repo)
    except ValidationError:
        return (False, REASON_NO_REGISTRY)
    return entitlement(report, config, canon, viewer, object_id)


def _refuse(reason: str, message: str, **fields: object) -> SigningRefused:
    return SigningRefused(reason, message, **fields)


def sign_review(
    repo: str | Path,
    object_id: str,
    identity_email: str,
    *,
    confirm_digest: str,
    confirm_head: tuple[int, str],
    confirm_owning_batch: str,
    now: str | None = None,
) -> Path:
    """Orchestrate the write through `reviews.record_review` and return the
    written `Path`, or raise `SigningRefused` with a stable reason code and
    write nothing (LLR-RS.2.1).  `confirm_digest`/`confirm_head`/
    `confirm_owning_batch` are the sign intent captured at `b`; they are
    re-checked against the current snapshot (the TOCTOU guard) in the fixed
    precedence `moved_object` · `moved_digest` · `moved_head` · `moved_role`.
    `now=None` means UTC now.

    One snapshot is threaded through the entitlement check, the confirm
    comparison and the write: `safe_verify`, `load_config` and `load_canon`
    each run EXACTLY once, and `entitlement` (the role/author decision) reads
    that snapshot — never a second load (F1)."""
    report = safe_verify(repo)
    try:
        config = load_config(repo)
    except ValidationError as exc:
        raise _refuse(REASON_NO_REGISTRY, f"cannot sign: {exc}") from exc
    # F6: refuse an unapproved config — the live config's digest differs from
    # the newest verified policy event's (checked before the generic chain
    # refusal, so a config mismatch is `unapproved_config`, not `tampered`).
    if _unapproved_config(report, config):
        raise _refuse(
            REASON_UNAPPROVED_CONFIG,
            "cannot sign: the live config is not the approved policy",
        )
    if not report.ok:
        raise _refuse(
            chain_reason(report),
            f"cannot sign: registry not verifiable ({report.status})",
            status=report.status,
        )
    viewer, reason = _viewer(config, identity_email)
    if viewer is None:
        raise _refuse(reason, f"cannot sign: {reason}")
    try:
        canon, _ = load_canon(repo)
    except ValidationError as exc:
        raise _refuse(REASON_NO_REGISTRY, f"cannot sign: {exc}") from exc
    obj = _find_object(canon, object_id)
    if obj is None:
        raise _refuse(
            REASON_UNKNOWN_OBJECT, f"cannot sign: unknown object {object_id}",
            object=object_id,
        )
    if _retired(obj):
        raise _refuse(
            REASON_RETIRED, f"cannot sign: {object_id} is retired", object=object_id,
        )
    cls = _classes(config).get(obj.class_id)
    if cls is None:
        raise _refuse(
            REASON_CLASS_UNDECLARED,
            f"cannot sign: {object_id}'s class is not declared",
            object=object_id,
        )
    normative, informative = object_digests(cls, obj.fields)
    # The TOCTOU re-checks (M-RS5 removes this block), in the documented
    # precedence: the owning batch / object first, then the confirmed digest,
    # then the head (a revoke that loses the role is `moved_role` else
    # `moved_head`).
    if confirm_owning_batch != obj.owning_batch:
        raise _refuse(REASON_MOVED_OBJECT, "cannot sign: the object changed since b")
    if confirm_digest != normative:
        raise _refuse(REASON_MOVED_DIGEST, "cannot sign: the content changed since b")
    if confirm_head != report.head:
        roles = effective_roles(report)
        if cls.reviewer_role not in roles.get(viewer, ()):
            raise _refuse(REASON_MOVED_ROLE, "cannot sign: the role changed since b")
        raise _refuse(REASON_MOVED_HEAD, "cannot sign: the head changed since b")
    # The full entitlement re-check (identity + role + authorship at the
    # current head) — the author arm is the one check the moved_* block does
    # not carry.  It reads THIS snapshot (no second load).
    ok, reason = entitlement(report, config, canon, viewer, object_id)
    if not ok:
        raise _refuse(reason, f"cannot sign: {reason}")
    when = now if now is not None else _utc_now()
    try:
        seq = next_seq(repo)
    except ReviewLimitError as exc:
        raise _refuse(
            REASON_REVIEW_LIMIT, "cannot sign: the review-file limit is reached",
        ) from exc
    except ValidationError as exc:
        raise _refuse(REASON_NO_REGISTRY, f"cannot sign: {exc}") from exc
    try:
        return record_review(
            repo,
            object_id=object_id,
            class_id=obj.class_id,
            normative_digest=normative,
            informative_digest=informative,
            verdict="reviewed",
            reviewer=viewer,
            kind="human",
            note="",
            now=when,
            head=report.head,
            seq=seq,
            owning_batch=obj.owning_batch,
        )
    except AlreadySignedError as exc:
        raise _refuse(
            REASON_ALREADY_SIGNED, "cannot sign: this content was already signed",
        ) from exc
    except ValidationError as exc:
        raise _refuse(REASON_NO_REGISTRY, f"cannot sign: {exc}") from exc


__all__ = [
    "REASON_ALREADY_SIGNED",
    "REASON_AMBIGUOUS_VIEWER",
    "REASON_CLASS_UNDECLARED",
    "REASON_FORKED",
    "REASON_MOVED_DIGEST",
    "REASON_MOVED_HEAD",
    "REASON_MOVED_OBJECT",
    "REASON_MOVED_ROLE",
    "REASON_NO_REGISTRY",
    "REASON_RETIRED",
    "REASON_TAMPERED",
    "REASON_UNAPPROVED_CONFIG",
    "REASON_UNKNOWN_OBJECT",
    "REASON_UNKNOWN_VIEWER",
    "chain_reason",
    "entitled_to_sign",
    "entitlement",
    "sign_review",
]
