"""The hash-chained role log: append, verify, policy binding, forks (HLR-RH.2 / HLR-RH.3).

`reqharness/roles.yml` is a YAML multi-document stream, one chain event per
document (the P0 ruling O4 format).  Every event records the head it was made
against (`roles_seq` + `roles_hash` — R2) and extends the chain by
`this_hash = sha256(prev_hash + "\\n" + canonical_json(event_without_this_hash))`
(canonical JSON per LLR-RH.1.3 — never a concatenation, R3).  Genesis carries
`roles_hash: "GENESIS"` (no self-reference) and `config_hash` = sha256(canonical
config at creation), so a fresh registry is policy-bound from the first
document (R15).

Verify walks BY `prev_hash` FROM genesis — NOT by file position (R27): each
document's recorded `prev_hash` must be the walk's current head; a document
claiming an already-claimed parent is a fork sibling, not a continuation.
Authority is always the longest verified prefix; `effective_roles` folds the
verified prefix with `<=` ON the event's own `seq`, never at wall-clock time
(R2/R26).

The status words (exact — LLR-RH.3.3 / AT-079):

- ``chain verified``            — the chain verifies and the live config's
  canonical hash equals the newest verified policy-bearing event's
  ``config_hash``;
- ``config changed without approval`` — a failed link, an unknown action, a
  decreasing ``time``, an event bound to a head that does not exist in the
  chain, or a live-config/policy mismatch: the last verified roles and the
  last approved policy stay in force and every append is refused;
- ``chain forked at seq N``     — two documents claim the same ``prev_hash``
  and no valid ``resolve`` names the excluded sibling yet: BOTH children are
  excluded from authority, deterministically on every clone regardless of
  document order (R7);
- ``chain broken``              — a fork whose excluded branch has descendants
  (a multi-event excluded branch — single-event forks only this batch,
  recovery deferred B-126), a ``resolve`` naming a non-sibling or one whose
  chosen child fails the approval rule at its own bound head (R27), or a
  document the walk can never reach.

Approval rule (one write path, this module only — screens never edit the
file): ``approved_by`` must hold `admin` in the roles in force at the event's
bound head, and nobody approves a change to themselves (a sole admin's
own-role change stays pending until a second admin exists — O5/R6).  An
admin's change to SOMEONE ELSE applies in ONE event with
``requested_by == approved_by == that admin`` (O5).  A ``genesis`` event is
valid ONLY at walk position 1 — a later ``genesis`` is a hand-edit class
refusal, never a freshly minted admin (F1).

DOCUMENTED manual fork-recovery procedure (R16 — the core implements and
tests it; fork-recovery UI is deferred, B-126):

1. Run ``verify_chain``; the status reads ``chain forked at seq N``.  Both
   fork children are excluded from authority — the registry keeps working
   with the pre-fork roles.
2. The team decides which child stands (e.g. the branch whose change was
   actually agreed).
3. An admin appends ONE ``resolve`` event — ``append_resolve`` — whose
   ``prev_hash`` is the CHOSEN child's hash and whose ``resolve_excludes``
   names the excluded sibling's hash.  The resolve is valid ONLY when the
   chosen child itself passes the approval rule at its own bound head (a
   never-approvable child cannot be legitimized by resolve, R27).
4. Run ``verify_chain`` again: the chain verifies and authority returns.

Residuals stated, not hidden (R23): truncation of a tail no review, pending
request or baseline has bound yet verifies clean (head binding covers only
bound heads); a writer with repo access can rewrite chain, reviews and
recorded heads together consistently and defeat every mechanism this module
ships (layer 3 — B-122 strong mode is the named follow-up).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from mapper.reqharness.canonical import canonical_digest, chain_hash, nfc
from mapper.reqharness.config import (
    GENESIS_PREV,
    LIMIT_ROLES_YML_BYTES,
    PENDING_DIR,
    REQHARNESS_DIR,
    ROLES_NAME,
    _confine,
    _read_text,
    check_str,
    check_time,
    config_digest,
    load_config,
    load_documents,
    load_pending,
    read_event_file,
)
from mapper.reqharness.records import ChainEvent, ValidationError

ROLES_WHERE = f"{REQHARNESS_DIR}/{ROLES_NAME}"
#: The append lock (SEC F4): `reqharness/.roles.lock`, exclusively created
#: around every roles.yml append and removed in `finally` — a present lock
#: is a NAMED refusal, never deleted silently (it may be another process's).
LOCK_NAME = ".roles.lock"
LOCK_WHERE = f"{REQHARNESS_DIR}/{LOCK_NAME}"

STATUS_VERIFIED = "chain verified"
STATUS_TAMPERED = "config changed without approval"
STATUS_BROKEN = "chain broken"

ACTIONS = frozenset({"genesis", "policy", "grant", "revoke", "resolution", "resolve"})
ROLE_ACTIONS = frozenset({"genesis", "grant", "revoke"})


def fork_status(seq: int) -> str:
    """The exact fork word (AT-079): `chain forked at seq N`."""
    return f"chain forked at seq {seq}"


@dataclass(frozen=True)
class ChainReport:
    """The result of one verification: the status word, the verified prefix
    (the ONLY events authority may fold), and the fork/tamper detail."""

    status: str
    events: tuple[ChainEvent, ...]
    broken_index: int | None = None
    fork_seq: int | None = None
    fork: tuple[ChainEvent, ...] = ()
    excluded: tuple[str, ...] = ()
    policy_config_hash: str | None = None
    policy_ok: bool = True

    @property
    def ok(self) -> bool:
        """Chain verified AND the live config matches the policy in force."""
        return self.status == STATUS_VERIFIED

    @property
    def chain_ok(self) -> bool:
        """The chain itself verifies (no fork, no tamper) — the state in
        which appending is legal.  A policy mismatch (`config changed without
        approval`) still allows the ONE append that re-binds the config:
        `append_policy`."""
        return self.status in (STATUS_VERIFIED, STATUS_TAMPERED)

    @property
    def head(self) -> tuple[int, str]:
        """The current bound head — (roles_seq, roles_hash) the next event
        (or a review/pending/baseline) must record (R2)."""
        if not self.events:
            raise ValidationError(f"{ROLES_WHERE}: chain has no genesis event")
        return (len(self.events), self.events[-1].this_hash)


# ---------------------------------------------------------------------------
# Reading: confinement + limits + the typed event schema (R9 / LLR-RH.3.1 / 3.5)
#
# The confined reader and the size-limited text reader live in `config.py`
# (the shared leaf — ARCH C3); this module re-imports them unchanged.
# ---------------------------------------------------------------------------


def _read_roles(repo: str | Path) -> str:
    return _read_text(
        _confine(repo, ROLES_WHERE), where=ROLES_WHERE, limit=LIMIT_ROLES_YML_BYTES
    )


_EVENT_KEYS = {
    "seq",
    "time",
    "requested_by",
    "approved_by",
    "action",
    "person",
    "role",
    "note",
    "roles_seq",
    "roles_hash",
    "prev_hash",
    "this_hash",
}
_EVENT_OPTIONAL = {"config_hash", "request_hash", "resolve_excludes"}
# Per event kind, which optional keys are allowed — they "appear only on the
# events that need them" (model.py, R15/R6/R16): policy binding on genesis and
# `policy` — REQUIRED there (F3), a policy-bearing event must bind a config
# hash, never nothing; the pending request digest on a `resolution` AND on a
# grant/revoke that lands one (R6 — the resolution is derived from the chain
# by `pending.resolution`); the excluded sibling's hash on a `resolve`.
_OPTIONAL_BY_ACTION = {
    "genesis": frozenset({"config_hash"}),
    "policy": frozenset({"config_hash"}),
    "resolution": frozenset({"request_hash"}),
    "grant": frozenset({"request_hash"}),
    "revoke": frozenset({"request_hash"}),
    "resolve": frozenset({"resolve_excludes"}),
}


def _check_int(value: Any, *, where: str, field: str) -> int:
    """`seq`/`roles_seq` are the ONLY non-str fields (R18); a YAML `true` is
    a bool, not an int."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValidationError(
            f"{where}: field {field!r} must be an int, "
            f"got {type(value).__name__} ({value!r})"
        )
    return value


def _validate_event(document: Any, index: int) -> ChainEvent:
    """The typed schema over one chain document — every refusal named by the
    file AND the document (R9); walk-level problems stay chain statuses.

    Required keys must be present, optional keys may be absent, unknown keys
    are rejected, and each optional key is allowed only on the event kinds
    that need it (R15/R6/R16)."""
    where = f"{ROLES_WHERE}: document {index + 1}"
    if not isinstance(document, dict):
        raise ValidationError(
            f"{where}: expected a mapping, got {type(document).__name__} ({document!r})"
        )
    keys = set(document)
    unknown = sorted(str(k) for k in keys - (_EVENT_KEYS | _EVENT_OPTIONAL))
    if unknown:
        raise ValidationError(f"{where}: unknown key(s): {', '.join(unknown)}")
    missing = sorted(_EVENT_KEYS - keys)
    if missing:
        raise ValidationError(f"{where}: missing key(s): {', '.join(missing)}")
    action = check_str(document["action"], where=where, field="action")
    allowed_optional = _OPTIONAL_BY_ACTION.get(action, _EVENT_OPTIONAL)
    misplaced = sorted(str(k) for k in (keys & _EVENT_OPTIONAL) - allowed_optional)
    if misplaced:
        raise ValidationError(
            f"{where}: key(s) not allowed on a {action!r} event: "
            f"{', '.join(misplaced)}"
        )
    if action in ("genesis", "policy") and "config_hash" not in keys:
        raise ValidationError(f"{where}: missing key(s): config_hash")
    optional = {
        key: check_str(document[key], where=where, field=key)
        for key in sorted(keys & _EVENT_OPTIONAL)
    }
    return ChainEvent(
        index=index,
        seq=_check_int(document["seq"], where=where, field="seq"),
        time=check_time(document["time"], where=where, field="time"),
        requested_by=check_str(document["requested_by"], where=where, field="requested_by"),
        approved_by=check_str(document["approved_by"], where=where, field="approved_by"),
        action=action,
        person=check_str(document["person"], where=where, field="person"),
        role=check_str(document["role"], where=where, field="role"),
        note=check_str(document["note"], where=where, field="note"),
        roles_seq=_check_int(document["roles_seq"], where=where, field="roles_seq"),
        roles_hash=check_str(document["roles_hash"], where=where, field="roles_hash"),
        prev_hash=check_str(document["prev_hash"], where=where, field="prev_hash"),
        this_hash=check_str(document["this_hash"], where=where, field="this_hash"),
        config_hash=optional.get("config_hash"),
        request_hash=optional.get("request_hash"),
        resolve_excludes=optional.get("resolve_excludes"),
    )


# ---------------------------------------------------------------------------
# Roles in force: the verified-prefix fold, `<=` ON the event's own `seq`
# (LLR-RH.2.3, as amended by LED-2026-10-11-reqharness-batch.31)
# ---------------------------------------------------------------------------


def _roles_in_force(events: tuple[ChainEvent, ...], bound_seq: int) -> dict[str, set[str]]:
    """Fold verified-prefix events whose OWN `seq` is <= bound_seq — the
    ONE boundary comparison (M-CH5 flips this `<=` to `<`).  The fold is on
    `seq`, NOT on `roles_seq` (LED.31): an event at seq k+1 records
    `roles_seq` k, so a `roles_seq` fold would leak it into head k — and a
    grant never retro-authorizes a review bound to an earlier head."""
    held: dict[str, set[str]] = {}
    for event in events:
        if event.action not in ROLE_ACTIONS or event.seq > bound_seq:
            continue
        if event.action == "revoke":
            held.get(event.person, set()).discard(event.role)
        else:
            held.setdefault(event.person, set()).add(event.role)
    return held


def effective_roles(
    report: ChainReport, bound_seq: int | None = None, bound_hash: str | None = None
) -> dict[str, tuple[str, ...]]:
    """The roles in force at a bound head (roles_seq, roles_hash) of the
    VERIFIED chain — never at wall-clock time (R2).  A bound head that does
    not exist in the verified chain raises (an unknown recorded head is `not
    verifiable`, LLR-RH.2.5).  With no bound, the current head."""
    if bound_seq is None or bound_hash is None:
        bound_seq, bound_hash = report.head
    if not (1 <= bound_seq <= len(report.events)) or (
        report.events[bound_seq - 1].this_hash != bound_hash
    ):
        raise ValidationError(
            f"bound head ({bound_seq}, {bound_hash}) is not in the verified chain"
        )
    held = _roles_in_force(report.events, bound_seq)
    return {person: tuple(sorted(roles)) for person, roles in held.items() if roles}


def _passes_approval(event: ChainEvent, prefix: tuple[ChainEvent, ...]) -> bool:
    """The approval rule at the event's own bound head: `approved_by` held
    `admin` in the roles in force there, and nobody approved a change about
    themselves.  Genesis is declared, not approved — and the shortcut holds
    only with NO prefix, i.e. at walk position 1 (F1: a seq-2 `genesis` by
    a non-admin must not mint an admin).

    SEC F5: an event that references a pending request (`request_hash`) is
    a derived approval — the approver must NOT be the request's requester
    (the API-level check in `approve_pending` is the first line; this is
    the chain-walk backstop that refuses a hand-crafted event the same way,
    and a fork child that violates it can never be legitimized by
    `resolve`)."""
    if event.action == "genesis":
        return not prefix
    in_force = _roles_in_force(prefix, event.roles_seq)
    if "admin" not in in_force.get(event.approved_by, set()):
        return False
    if event.action in ("grant", "revoke"):
        if event.approved_by == event.person:
            return False
        if event.request_hash is not None and event.approved_by == event.requested_by:
            return False
    if event.action == "resolution" and (
        event.approved_by == event.requested_by or event.approved_by == event.person
    ):
        return False
    return True


# ---------------------------------------------------------------------------
# Verify: the BY-prev_hash walk from genesis (LLR-RH.3.1 / 3.2 / 3.4 — R27)
# ---------------------------------------------------------------------------


def _check_event(
    event: ChainEvent,
    prefix: tuple[ChainEvent, ...],
    prev_head: str,
    last_time: str | None,
    *,
    check_approval: bool = True,
) -> str | None:
    """The per-event checks in the walk; returns the first problem found or
    None.  Every failure here is a hand-edit class -> `config changed
    without approval`."""
    if event.action not in ACTIONS:
        return f"unknown action {event.action!r}"
    if chain_hash(prev_head, _event_body(event)) != event.this_hash:
        return "chain link does not recompute (tampered event)"
    position = len(prefix) + 1
    if event.seq != position:
        return f"seq {event.seq} is not the walk position {position}"
    if (event.action == "genesis") != (position == 1):
        return (
            f"{event.action!r} at walk position {position}: genesis is "
            "allowed only at position 1, and position 1 must be genesis"
        )
    if last_time is not None and event.time < last_time:
        return f"time {event.time} decreases after {last_time}"
    if position == 1:
        if event.roles_seq != 1 or event.roles_hash != GENESIS_PREV:
            return "genesis does not bind the declared root"
    elif event.roles_seq != position - 1 or event.roles_hash != prev_head:
        return (
            f"bound head ({event.roles_seq}, {event.roles_hash}) does not exist "
            f"in the chain"
        )
    if check_approval and not _passes_approval(event, prefix):
        return f"{event.approved_by!r} may not approve {event.action} at this head"
    return None


def _event_body(event: ChainEvent) -> dict[str, Any]:
    """The event as hashed: every stored field except `this_hash` (and the
    reader-side `index`)."""
    body: dict[str, Any] = {
        "seq": event.seq,
        "time": event.time,
        "requested_by": event.requested_by,
        "approved_by": event.approved_by,
        "action": event.action,
        "person": event.person,
        "role": event.role,
        "note": event.note,
        "roles_seq": event.roles_seq,
        "roles_hash": event.roles_hash,
        "prev_hash": event.prev_hash,
    }
    if event.config_hash is not None:
        body["config_hash"] = event.config_hash
    if event.request_hash is not None:
        body["request_hash"] = event.request_hash
    if event.resolve_excludes is not None:
        body["resolve_excludes"] = event.resolve_excludes
    return body


def _walk(
    docs: list[ChainEvent],
) -> tuple[str, tuple[ChainEvent, ...], int | None, int | None, tuple[ChainEvent, ...], tuple[str, ...]]:
    """The BY-prev_hash walk.  Returns (status, verified prefix, broken
    document index, fork seq, fork children, excluded hashes)."""
    events: list[ChainEvent] = []
    consumed: set[int] = set()
    by_prev: dict[str, list[ChainEvent]] = {}
    for doc in docs:
        by_prev.setdefault(doc.prev_hash, []).append(doc)
    head = GENESIS_PREV
    last_time: str | None = None
    status = STATUS_VERIFIED
    broken_index: int | None = None
    fork_seq: int | None = None
    fork: tuple[ChainEvent, ...] = ()
    excluded: set[str] = set()

    while True:
        candidates = by_prev.get(head, [])
        continuations = [d for d in candidates if d.action != "resolve"]
        resolves = [d for d in candidates if d.action == "resolve"]
        if not continuations:
            # A resolve claiming a head with nothing to resolve is invalid.
            if resolves:
                status, broken_index = STATUS_BROKEN, min(r.index for r in resolves)
            break
        if len(continuations) == 1:
            event = continuations[0]
            consumed.add(id(event))
            if resolves:
                status, broken_index = STATUS_BROKEN, min(r.index for r in resolves)
                break
            problem = _check_event(event, tuple(events), head, last_time)
            if problem is not None:
                status, broken_index = STATUS_TAMPERED, event.index
                break
            events.append(event)
            head, last_time = event.this_hash, event.time
            continue

        # A fork: >= 2 documents claim the same prev_hash (R7/R27).
        for child in continuations:
            consumed.add(id(child))
        fork = tuple(sorted(continuations, key=lambda d: (d.seq, d.index)))
        fork_seq = min(d.seq for d in continuations)
        child_hashes = {d.this_hash for d in continuations}
        descendants = [
            d
            for d in docs
            if id(d) not in consumed
            and d.action != "resolve"
            and d.prev_hash in child_hashes
        ]
        if descendants:
            # A multi-event excluded branch — single-event forks only this
            # batch; recovery is deferred (B-126).
            status, broken_index = STATUS_BROKEN, min(d.index for d in descendants)
            break
        chosen: tuple[ChainEvent, ChainEvent] | None = None
        resolves_here = sorted(
            (d for d in docs if d.action == "resolve" and d.prev_hash in child_hashes),
            key=lambda d: (d.seq, d.index),
        )
        for resolve in resolves_here:
            siblings = child_hashes - {resolve.prev_hash}
            if siblings != {resolve.resolve_excludes}:
                continue  # a resolve cannot mint exclusions out of thin air
            child = next(c for c in continuations if c.this_hash == resolve.prev_hash)
            if _check_event(child, tuple(events), head, last_time) is not None:
                continue  # the chosen child itself must verify
            if not _passes_approval(child, tuple(events)):
                continue  # a never-approvable child cannot be legitimized (R27)
            if (
                _check_event(
                    resolve, (*events, child), child.this_hash, child.time,
                    check_approval=False,
                )
                is not None
            ):
                continue
            if (
                "admin"
                not in _roles_in_force(events, child.roles_seq).get(
                    resolve.approved_by, set()
                )
            ):
                # The resolve is approved at the CHOSEN CHILD's bound head.
                continue
            chosen = (child, resolve)
            break
        if chosen is None:
            excluded |= child_hashes  # both children stay excluded either way
            if resolves_here:
                # Resolves exist but every one is invalid (a non-sibling
                # exclusion, an unverifiable or never-approvable chosen
                # child, a non-admin resolver) -> `chain broken` (R27).
                status, broken_index = STATUS_BROKEN, min(r.index for r in resolves_here)
            else:
                status = fork_status(fork_seq)
            break
        child, resolve = chosen
        consumed.add(id(resolve))
        excluded |= child_hashes - {child.this_hash}
        events.append(child)
        events.append(resolve)
        head, last_time = resolve.this_hash, resolve.time

    if status == STATUS_VERIFIED:
        leftovers = [d for d in docs if id(d) not in consumed]
        if leftovers:
            status, broken_index = STATUS_BROKEN, min(d.index for d in leftovers)
    return status, tuple(events), broken_index, fork_seq, fork, tuple(sorted(excluded))


def _inspect(repo: str | Path) -> ChainReport:
    """Parse and walk roles.yml (no policy gate — verify_chain adds it)."""
    documents = load_documents(_read_roles(repo), where=ROLES_WHERE)
    docs = [_validate_event(document, index) for index, document in enumerate(documents)]
    status, events, broken_index, fork_seq, fork, excluded = _walk(docs)
    policy_config_hash = next(
        (e.config_hash for e in reversed(events) if e.config_hash is not None), None
    )
    return ChainReport(
        status=status,
        events=events,
        broken_index=broken_index,
        fork_seq=fork_seq,
        fork=fork,
        excluded=excluded,
        policy_config_hash=policy_config_hash,
    )


def verify_chain(repo: str | Path) -> ChainReport:
    """Verify roles.yml and bind the live config through the newest verified
    policy-bearing event (genesis or `policy` — R1/R15).

    On ANY failure the last verified prefix and the last approved policy stay
    in force (the report's `events` and `policy_config_hash`) and `ok` is
    False, so every append path refuses.
    """
    report = _inspect(repo)
    live = config_digest(load_config(repo))
    policy_ok = report.policy_config_hash == live
    if report.status == STATUS_VERIFIED and not policy_ok:
        report = replace(report, status=STATUS_TAMPERED, policy_ok=False)
    else:
        report = replace(report, policy_ok=policy_ok)
    return report


# ---------------------------------------------------------------------------
# Append: the one write path (LLR-RH.2.1 / 2.2 / 2.4 / 3.4)
# ---------------------------------------------------------------------------


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _checked_now(now: str | None, *, where: str, last_time: str | None) -> str:
    value = check_time(now, where=where, field="now") if now else _utc_now()
    if last_time is not None and value < last_time:
        raise ValidationError(
            f"{where}: time {value} decreases after {last_time} (chain time "
            "must be non-decreasing, R18)"
        )
    return value


def _append_body(repo: str | Path, body: dict[str, Any]) -> ChainEvent:
    """The ONE write path: hash the body over its `prev_hash` and append one
    YAML document to roles.yml.

    SEC F4 — the append is serialized with an exclusive lock file
    (`reqharness/.roles.lock`, `O_CREAT|O_EXCL`, removed in `finally`): a
    present lock is a NAMED refusal and is never deleted silently (it may
    belong to a concurrent append or be stale after a crash — the refusal
    says so).  Under the lock the bound head is re-verified — a head that
    moved between the report the event was built on and the locked append
    refuses, never appends on a stale head — and a file whose last byte is
    not a newline is repaired with a prepended `\\n`, so a hand-truncated
    tail can never glue the new document's `---` marker onto the previous
    line."""
    body = nfc(dict(body))
    body["this_hash"] = chain_hash(
        body["prev_hash"], {k: v for k, v in body.items() if k != "this_hash"}
    )
    path = _confine(repo, ROLES_WHERE)
    lock_path = path.parent / LOCK_NAME
    try:
        lock_fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise ValidationError(
            f"{ROLES_WHERE}: refused (append lock held: {LOCK_WHERE} exists — "
            "a concurrent append is in progress, or the lock is stale after "
            "a crash; remove it only when no append is running)"
        ) from None
    except OSError as exc:
        raise ValidationError(f"{LOCK_WHERE}: cannot create lock ({exc})") from exc
    try:
        report = _inspect(repo)
        if body["action"] == "resolve":
            if body["prev_hash"] not in {c.this_hash for c in report.fork}:
                raise ValidationError(
                    f"{ROLES_WHERE}: refused (head changed under the append lock: "
                    "the resolve parent is no longer a fork child)"
                )
        elif not report.chain_ok or report.head != (
            body["roles_seq"],
            body["prev_hash"],
        ):
            raise ValidationError(
                f"{ROLES_WHERE}: refused (head changed under the append lock: "
                f"{report.status})"
            )
        try:
            with path.open("rb") as handle:
                handle.seek(-1, os.SEEK_END)
                needs_newline = handle.read(1) != b"\n"
        except FileNotFoundError:
            needs_newline = False
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(
                ("\n" if needs_newline else "")
                + "---\n"
                + yaml.safe_dump(body, sort_keys=False, allow_unicode=True)
            )
    finally:
        os.close(lock_fd)
        try:
            lock_path.unlink()
        except OSError:
            pass  # our own lock, best-effort removal; a stale one is never touched
    return _validate_event(body, body["seq"] - 1)


def _append_event(
    repo: str | Path,
    report: ChainReport,
    *,
    requested_by: str,
    approved_by: str,
    action: str,
    person: str = "",
    role: str = "",
    note: str = "",
    now: str,
    config_hash: str | None = None,
    request_hash: str | None = None,
    resolve_excludes: str | None = None,
    prev_hash: str | None = None,
    seq: int | None = None,
    roles_seq: int | None = None,
) -> ChainEvent:
    """Build the next event on the verified head (or, for a fork `resolve`,
    on the chosen child via *prev_hash*/*seq*/*roles_seq*) and append it."""
    if not report.chain_ok:
        raise ValidationError(f"{ROLES_WHERE} is not appendable: {report.status}")
    if action not in ACTIONS:
        raise ValidationError(f"unknown action {action!r}")
    position = len(report.events)
    head_hash = report.events[-1].this_hash if position else GENESIS_PREV
    prev = prev_hash if prev_hash is not None else head_hash
    body: dict[str, Any] = {
        "seq": seq if seq is not None else position + 1,
        "time": now,
        "requested_by": requested_by,
        "approved_by": approved_by,
        "action": action,
        "person": person,
        "role": role,
        "note": note,
        "roles_seq": roles_seq if roles_seq is not None else (position if position else 1),
        "roles_hash": prev,
        "prev_hash": prev,
    }
    if config_hash is not None:
        body["config_hash"] = config_hash
    if request_hash is not None:
        body["request_hash"] = request_hash
    if resolve_excludes is not None:
        body["resolve_excludes"] = resolve_excludes
    return _append_body(repo, body)


def _require_admin(report: ChainReport, *, who: str, where: str) -> None:
    if "admin" not in effective_roles(report).get(who, ()):
        raise ValidationError(f"{where}: {who!r} holds no admin in the roles in force")


def propose(
    repo: str | Path,
    *,
    requester: str,
    action: str,
    person: str,
    role: str,
    note: str = "",
    now: str | None = None,
) -> Path | None:
    """Propose a grant/revoke (LLR-RH.2.1/2.2, ruling O5).

    An admin's change about SOMEONE ELSE applies in ONE event
    (`requested_by == approved_by == that admin`) and returns None.  A change
    about the requester themselves, or by a non-admin, writes ONE pending
    request file under `reqharness/pending/` — roles.yml is untouched — and
    returns its path.  A pending self-change becomes appendable once a second
    admin exists (`approve_pending` with a different approver).
    """
    if action not in ("grant", "revoke"):
        raise ValidationError(
            f"propose: action must be grant/revoke, got {action!r} "
            "(policy uses append_policy, fork recovery uses append_resolve)"
        )
    config = load_config(repo)
    report = verify_chain(repo)
    if not report.ok:
        raise ValidationError(f"propose: roles.yml is not appendable: {report.status}")
    person_ids = {p.id for p in config.people}
    if requester not in person_ids:
        raise ValidationError(f"propose: requester {requester!r} is not a declared person")
    if person not in person_ids:
        raise ValidationError(f"propose: person {person!r} is not a declared person")
    if role not in config.roles:
        raise ValidationError(f"propose: role {role!r} is not a declared role")
    when = _checked_now(now, where="propose", last_time=report.events[-1].time)
    held = effective_roles(report)
    if person != requester and "admin" in held.get(requester, ()):
        _append_event(
            repo, report,
            requested_by=requester, approved_by=requester,
            action=action, person=person, role=role, note=note, now=when,
        )
        return None
    return _write_pending(
        repo,
        requested_by=requester, action=action, person=person, role=role,
        note=note, now=when, head=report.head,
    )


def _write_pending(
    repo: str | Path,
    *,
    requested_by: str,
    action: str,
    person: str,
    role: str,
    note: str,
    now: str,
    head: tuple[int, str],
) -> Path:
    """One pending request file, content-keyed and exclusively created (R6/R8).

    SEC F3 — confine-then-create, exactly like `reviews.record_review`: the
    confined path is resolved BEFORE anything is written, and a link or
    junction at `reqharness/pending` (or any parent component) is refused
    by name — the write never reaches through a link."""
    body = nfc(
        {
            "requested_by": requested_by,
            "change": {"action": action, "person": person, "role": role},
            "time": now,
            "note": note,
            "roles_seq": head[0],
            "roles_hash": head[1],
        }
    )
    digest = canonical_digest(body)
    name = f"{now[:4]}{now[5:7]}{now[8:10]}-{digest[:8]}.yml"
    where = f"{REQHARNESS_DIR}/{PENDING_DIR}/{name}"
    resolved = _confine(repo, where)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    try:
        with resolved.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(yaml.safe_dump(body, sort_keys=False, allow_unicode=True))
    except FileExistsError:
        raise ValidationError(
            f"{where}: pending request already exists"
        ) from None
    return resolved


def _check_request_open(report: ChainReport, *, digest: str, where: str) -> None:
    """H1: a pending request resolves AT MOST ONCE — any event of the
    verified chain already referencing its digest refuses a second
    resolution (approve-after-approve, reject-after-approve and
    approve-after-reject are all the same refusal)."""
    for event in report.events:
        if event.request_hash == digest:
            raise ValidationError(
                f"{where}: request already resolved "
                f"(verified chain event seq {event.seq} references it)"
            )


def approve_pending(
    repo: str | Path, *, pending: str, approver: str, now: str | None = None
) -> ChainEvent:
    """Apply a held pending request with a DIFFERENT admin's approval — the
    second-admin path (LLR-RH.2.2): a sole admin's own-role change stays
    pending until a second admin exists.  The change lands as the chain
    event referencing the request's sha256; the pending file stays on disk
    and the resolution is derived from the chain (R6).  Refuses a request
    the verified chain has already resolved (H1) and a file whose name does
    not match its canonical content (R22, the shared validator)."""
    report = verify_chain(repo)
    if not report.ok:
        raise ValidationError(f"approve_pending: roles.yml is not appendable: {report.status}")
    request = load_pending(repo, pending)
    if approver == request.requested_by:
        raise ValidationError(
            f"approve_pending: {approver!r} cannot approve their own request"
        )
    if approver == request.person:
        raise ValidationError(
            f"approve_pending: nobody approves a change to themselves ({approver!r})"
        )
    _require_admin(report, who=approver, where="approve_pending")
    _check_request_open(report, digest=request.digest, where="approve_pending")
    when = _checked_now(
        now, where="approve_pending", last_time=report.events[-1].time
    )
    return _append_event(
        repo, report,
        requested_by=request.requested_by, approved_by=approver,
        action=request.action, person=request.person, role=request.role,
        note=request.note, now=when,
        request_hash=request.digest,
    )


def reject_pending(
    repo: str | Path, *, pending: str, approver: str, now: str | None = None
) -> ChainEvent:
    """Record a rejection (R6): a `resolution` chain event referencing the
    pending request's sha256 with an EMPTY change — no grant/revoke lands.
    The pending file stays on disk; the rejection is derived from the chain
    (`pending.resolution`).  Admin only, never one's own request, never a
    request the chain has already resolved (H1), never a name/content-
    mismatched file (R22, the shared validator)."""
    report = verify_chain(repo)
    if not report.ok:
        raise ValidationError(f"reject_pending: roles.yml is not appendable: {report.status}")
    request = load_pending(repo, pending)
    if approver == request.requested_by:
        raise ValidationError(
            f"reject_pending: {approver!r} cannot reject their own request"
        )
    _require_admin(report, who=approver, where="reject_pending")
    _check_request_open(report, digest=request.digest, where="reject_pending")
    when = _checked_now(
        now, where="reject_pending", last_time=report.events[-1].time
    )
    return _append_event(
        repo, report,
        requested_by=request.requested_by, approved_by=approver,
        action="resolution", person="", role="", note=request.note, now=when,
        request_hash=request.digest,
    )


def append_policy(repo: str | Path, *, approved_by: str, note: str = "", now: str | None = None) -> ChainEvent:
    """Bind the LIVE config by its canonical digest — admin in force required
    (R1/LLR-RH.2.4).  Until this runs after a config edit, the registry is in
    `config changed without approval` and no append lands."""
    config = load_config(repo)
    report = verify_chain(repo)
    if not report.chain_ok:
        raise ValidationError(f"append_policy: roles.yml is not appendable: {report.status}")
    _require_admin(report, who=approved_by, where="append_policy")
    when = _checked_now(now, where="append_policy", last_time=report.events[-1].time)
    return _append_event(
        repo, report,
        requested_by=approved_by, approved_by=approved_by,
        action="policy", person="", role="", note=note, now=when,
        config_hash=config_digest(config),
    )


def append_resolve(
    repo: str | Path,
    *,
    approved_by: str,
    chosen_hash: str,
    excludes_hash: str,
    note: str = "",
    now: str | None = None,
) -> ChainEvent:
    """The fork-recovery event (LLR-RH.3.4, R16/R27): `prev_hash` is the
    CHOSEN fork child, `resolve_excludes` names the excluded sibling, the
    chosen child must itself pass the approval rule at its own bound head,
    and the resolver must hold admin in the roles in force at that head."""
    report = _inspect(repo)
    if not report.fork:
        raise ValidationError(f"append_resolve: {ROLES_WHERE} has no fork to resolve")
    if chosen_hash not in {c.this_hash for c in report.fork}:
        raise ValidationError(f"append_resolve: {chosen_hash} is not a fork child")
    if excludes_hash not in {c.this_hash for c in report.fork} or excludes_hash == chosen_hash:
        raise ValidationError(
            f"append_resolve: {excludes_hash} is not the excluded fork sibling"
        )
    child = next(c for c in report.fork if c.this_hash == chosen_hash)
    prefix_time = report.events[-1].time if report.events else None
    if _check_event(
        child, report.events, child.prev_hash, prefix_time, check_approval=False
    ) is not None:
        raise ValidationError("append_resolve: the chosen fork child does not verify")
    if not _passes_approval(child, report.events):
        raise ValidationError(
            "append_resolve: the chosen child fails the approval rule at its "
            "own bound head"
        )
    if "admin" not in _roles_in_force(report.events, child.roles_seq).get(approved_by, set()):
        raise ValidationError(
            f"append_resolve: {approved_by!r} holds no admin in the roles in "
            "force at the chosen child's bound head"
        )
    when = _checked_now(now, where="append_resolve", last_time=child.time)
    return _append_event(
        repo, ChainReport(status=STATUS_VERIFIED, events=report.events),
        requested_by=approved_by, approved_by=approved_by,
        action="resolve", person="", role="", note=note, now=when,
        resolve_excludes=excludes_hash,
        prev_hash=chosen_hash,
        seq=child.seq + 1,
        roles_seq=child.seq,
    )


__all__ = [
    "ACTIONS",
    "PENDING_DIR",
    "ROLES_WHERE",
    "STATUS_BROKEN",
    "STATUS_TAMPERED",
    "STATUS_VERIFIED",
    "ChainReport",
    "append_policy",
    "append_resolve",
    "approve_pending",
    "effective_roles",
    "fork_status",
    "propose",
    "read_event_file",
    "reject_pending",
    "verify_chain",
]
