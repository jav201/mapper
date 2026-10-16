"""Review events: the immutable, content-named event store under
`reqharness/reviews/` (HLR-RH.4 / LLR-RH.4.6).

One file per review event, named `<yyyymmdd>-<sha8 of canonical content>.yml`
— derived from canonical content ONLY, never from a caller-supplied slug (R8)
— and written with exclusive create: a second write under the same name is an
error, never a silent overwrite (sha8 is 32 bits; a collision is refused, by
construction).  Every event binds the object id, its class, the normative
digest at review time, the informative digest, the reviewer free-text id, a
self-declared `kind` (`human` or `model`), and the chain head it was made
against (`roles_seq` + `roles_hash` — R2).

The loader recomputes sha8 over the canonical content of every file; a
name/content mismatch is reported BY NAME and non-closing (R22).  Malformed,
oversize or link-reached files are likewise reported by name, never silently
skipped (R9).  Parsing may be accelerated by the content-keyed cache
(`cache.py`, R4); the cache holds validated parses only (a refused file's
raw parse never enters it — H2), a cached parse that fails re-validation is
busted and re-parsed from the bytes, so the cache can never change a derived
state (M-RG5).  Path confinement reuses the one containment rule
(`mapper.osopen.confine_reason` / `is_link`, R8): `..`, links and junctions
under `reqharness/` are refused.

Events are immutable once written — a correction is a NEW event (the seq
monotonically increases); there is no review write API beyond `record_review`.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from mapper.osopen import confine_reason, is_link
from mapper.reqharness.cache import ParseCache
from mapper.reqharness.canonical import canonical_digest, nfc
from mapper.reqharness.chain import read_event_file
from mapper.reqharness.config import (
    LIMIT_REVIEW_FILE_COUNT,
    REQHARNESS_DIR,
    check_int,
    check_str,
    check_time,
    load_documents,
)
from mapper.reqharness.records import (
    AlreadySignedError,
    ReviewLimitError,
    ValidationError,
)

REVIEW_DIR = "reviews"

#: The content-derived name shape (R8); both groups are recomputed at read.
NAME_RE = re.compile(r"(\d{8})-([0-9a-f]{8})\.yml\Z", re.ASCII)

#: A review kind is SELF-DECLARED; `model` is always a pre-review (R5).
KINDS = frozenset({"human", "model"})

_REVIEW_KEYS = {
    "seq",
    "time",
    "object",
    "class",
    "normative_digest",
    "informative_digest",
    "verdict",
    "reviewer",
    "kind",
    "roles_seq",
    "roles_hash",
    "note",
    "owning_batch",
}

#: `owning_batch` is OPTIONAL (F1): a record written before it existed lacks
#: the field and loads exactly as today (legacy) — it is never required.
_REVIEW_REQUIRED_KEYS = _REVIEW_KEYS - {"owning_batch"}


@dataclass(frozen=True)
class ReviewEvent:
    """One parsed review event — every stored field, NFC-normalised."""

    name: str
    seq: int
    time: str
    object: str
    class_id: str
    normative_digest: str
    informative_digest: str
    verdict: str
    reviewer: str
    kind: str
    roles_seq: int
    roles_hash: str
    note: str
    owning_batch: str = ""


@dataclass(frozen=True)
class ReviewScan:
    """The result of one load pass: the valid events plus every problem
    found, each reported by name — corruption, refusal or name/content
    mismatch derives no state and is never silent (R9/R22/R26)."""

    events: tuple[ReviewEvent, ...]
    reported: tuple[str, ...]


def scan_event_dir(repo: str | Path, subdir: str) -> tuple[list[str], list[str]]:
    """The shared event-directory listing: sorted file names plus named
    refusals.  Links/reparse points and non-regular files under the
    directory are refused BY NAME via `osopen.is_link` (R8); the caller
    owns the per-file size limit."""
    target = Path(repo) / REQHARNESS_DIR / subdir
    names: list[str] = []
    reported: list[str] = []
    if not target.is_dir():
        return names, reported
    try:
        with os.scandir(target) as entries:
            for entry in entries:
                where = f"{REQHARNESS_DIR}/{subdir}/{entry.name}"
                try:
                    info = entry.stat(follow_symlinks=False)
                except OSError as exc:
                    reported.append(f"{where}: cannot stat ({exc})")
                    continue
                if is_link(info):
                    reported.append(f"{where}: refused (link)")
                    continue
                if not entry.is_file(follow_symlinks=False):
                    reported.append(f"{where}: refused (not a regular file)")
                    continue
                names.append(entry.name)
    except OSError as exc:
        raise ValidationError(
            f"{REQHARNESS_DIR}/{subdir}: cannot read ({exc})"
        ) from exc
    if len(names) > LIMIT_REVIEW_FILE_COUNT:
        raise ReviewLimitError(
            f"{REQHARNESS_DIR}/{subdir}: too many review files "
            f"({len(names)} > {LIMIT_REVIEW_FILE_COUNT} limit)"
        )
    return sorted(names), reported


def record_review(
    repo: str | Path,
    *,
    object_id: str,
    class_id: str,
    normative_digest: str,
    informative_digest: str,
    verdict: str,
    reviewer: str,
    kind: str,
    note: str,
    now: str,
    head: tuple[int, str],
    seq: int,
    owning_batch: str = "",
) -> Path:
    """Write ONE review event, content-named and exclusively created (R8).

    The name derives from the canonical content only — there is no name
    parameter (M-FN1).  *head* is the chain head the review is bound to
    (`verify_chain(repo).head`).  The free-text fields are type-checked
    before anything is written (L3): a non-str verdict, reviewer or object
    id is a named refusal, never a coerced file.  *owning_batch* is the
    object's owning batch at sign time (F1) and is stored only when
    non-empty, so a record written without it loads exactly as today."""
    if kind not in KINDS:
        raise ValidationError(
            f"record_review: kind must be one of {sorted(KINDS)}, got {kind!r}"
        )
    when = check_time(now, where="record_review", field="now")
    seq = check_int(seq, where="record_review", field="seq")
    object_id = check_str(object_id, where="record_review", field="object")
    verdict = check_str(verdict, where="record_review", field="verdict")
    reviewer = check_str(reviewer, where="record_review", field="reviewer")
    owning_batch = check_str(owning_batch, where="record_review", field="owning_batch")
    body = {
        "seq": seq,
        "time": when,
        "object": object_id,
        "class": class_id,
        "normative_digest": normative_digest,
        "informative_digest": informative_digest,
        "verdict": verdict,
        "reviewer": reviewer,
        "kind": kind,
        "roles_seq": head[0],
        "roles_hash": head[1],
        "note": note,
    }
    if owning_batch:
        body["owning_batch"] = owning_batch
    body = nfc(body)
    digest = canonical_digest(body)
    name = f"{when[0:4]}{when[5:7]}{when[8:10]}-{digest[:8]}.yml"
    where = f"{REQHARNESS_DIR}/{REVIEW_DIR}/{name}"
    resolved, reason = confine_reason(where, Path(repo))
    if reason != "ok" or resolved is None:
        raise ValidationError(f"{where}: refused ({reason})")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    try:
        with resolved.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(yaml.safe_dump(body, sort_keys=False, allow_unicode=True))
    except FileExistsError:
        raise AlreadySignedError(
            f"{where}: review event already exists (exclusive create, R8)"
        ) from None
    return resolved


def next_seq(repo: str | Path) -> int:
    """The next per-registry review seq: max of the valid events + 1.
    A corrupt sibling file is reported, never silently counted (R9)."""
    scan = load_reviews(repo)
    return max((event.seq for event in scan.events), default=0) + 1


def _validate_review(document: Any, *, name: str, where: str) -> ReviewEvent:
    """The typed schema over one review document (R3/R18) — named by file."""
    if not isinstance(document, dict):
        raise ValidationError(
            f"{where}: expected a mapping, got {type(document).__name__} ({document!r})"
        )
    keys = set(document)
    unknown = sorted(str(k) for k in keys - _REVIEW_KEYS)
    if unknown:
        raise ValidationError(f"{where}: unknown key(s): {', '.join(unknown)}")
    missing = sorted(_REVIEW_REQUIRED_KEYS - keys)
    if missing:
        raise ValidationError(f"{where}: missing key(s): {', '.join(missing)}")
    kind = check_str(document["kind"], where=where, field="kind")
    if kind not in KINDS:
        raise ValidationError(f"{where}: kind must be one of {sorted(KINDS)}, got {kind!r}")
    return ReviewEvent(
        name=name,
        seq=check_int(document["seq"], where=where, field="seq"),
        time=check_time(document["time"], where=where, field="time"),
        object=check_str(document["object"], where=where, field="object"),
        class_id=check_str(document["class"], where=where, field="class"),
        normative_digest=check_str(
            document["normative_digest"], where=where, field="normative_digest"
        ),
        informative_digest=check_str(
            document["informative_digest"], where=where, field="informative_digest"
        ),
        verdict=check_str(document["verdict"], where=where, field="verdict"),
        reviewer=check_str(document["reviewer"], where=where, field="reviewer"),
        kind=kind,
        roles_seq=check_int(document["roles_seq"], where=where, field="roles_seq"),
        roles_hash=check_str(document["roles_hash"], where=where, field="roles_hash"),
        note=check_str(document["note"], where=where, field="note"),
        # NFC at read (RS1a security re-check L-b): the derive comparison
        # against the NFC canon cell is then symmetric.
        owning_batch=nfc(check_str(
            document.get("owning_batch", ""), where=where, field="owning_batch"
        )),
    )


def _check_name(document: dict[str, Any], name: str, *, where: str) -> None:
    """R22: sha8 recomputed over the canonical content at read; a mismatch
    with the file name is reported BY NAME and non-closing."""
    match = NAME_RE.fullmatch(name)
    digest = canonical_digest(nfc(document))
    when = document.get("time", "")
    date = f"{when[0:4]}{when[5:7]}{when[8:10]}" if isinstance(when, str) else ""
    if match is None or match.group(1) != date or match.group(2) != digest[:8]:
        raise ValidationError(
            f"{where}: name/content mismatch "
            f"(recomputed sha8 {digest[:8]} of the canonical content, R22)"
        )


def _parse_single(text: str, *, where: str) -> Any:
    documents = load_documents(text, where=where)
    if len(documents) != 1:
        raise ValidationError(
            f"{where}: expected exactly 1 document, found {len(documents)}"
        )
    return documents[0]


def _file_stat(repo: str | Path, name: str) -> os.stat_result | None:
    """The live stat of one review file for the fast path, or None when it
    cannot be stated or is a link (a link falls through to the full read
    path, where the confined reader refuses it BY NAME).  *name* always
    comes from the confined ``scan_event_dir`` listing (a directory entry
    name carries no separators), so the join stays inside
    ``reqharness/reviews/`` — no second confinement walk is needed for a
    stat that never reads through the file."""
    try:
        info = os.stat(
            Path(repo) / REQHARNESS_DIR / REVIEW_DIR / name,
            follow_symlinks=False,
        )
    except OSError:
        return None
    if is_link(info):
        return None
    return info


def _load_one(
    repo: str | Path, name: str, cache: ParseCache | None
) -> ReviewEvent:
    """One review file: stat fast path (no read) or a confined + size-limited
    read, cache-accelerated parse, typed schema, R22 name check.  A fast-path
    hit and every sha-keyed hit is re-validated (CPU only, no I/O); a hit
    that fails is busted and re-parsed from the bytes, and only a VALIDATED
    document is remembered — so a poisoned entry is bounded to a re-parse
    (M-RG5) and the raw parse of a refused file never enters the store
    (H2)."""
    where = f"{REQHARNESS_DIR}/{REVIEW_DIR}/{name}"
    rel = f"{REVIEW_DIR}/{name}"
    stat: os.stat_result | None = None
    if cache is not None:
        stat = _file_stat(repo, name)
        if stat is not None:
            document = cache.fast(rel, stat)
            if document is not None:
                try:
                    event = _validate_review(document, name=name, where=where)
                    _check_name(document, name, where=where)
                except ValidationError:
                    cache.bust_name(rel)  # a poisoned on-disk entry — drop it
                else:
                    return event  # the validated parse, file unread (fast path)
    text = read_event_file(repo, rel)
    if cache is None:
        document = _parse_single(text, where=where)
        event = _validate_review(document, name=name, where=where)
        _check_name(document, name, where=where)
        return event
    document, key = cache.parse(text, where=where)
    try:
        event = _validate_review(document, name=name, where=where)
        _check_name(document, name, where=where)
    except ValidationError:
        cache.bust(key)  # a poisoned on-disk entry — drop it
        document, key = cache.parse(text, where=where)  # re-parse from the bytes
        event = _validate_review(document, name=name, where=where)
        _check_name(document, name, where=where)
    cache.remember(key, document, name=rel, stat=stat)  # validated parses only (H2)
    return event


def load_reviews(repo: str | Path, *, cache: ParseCache | None = None) -> ReviewScan:
    """Every valid review event, plus named reports of everything refused
    (R9/R22/R26).  With *cache* given, `cache.save()` persists what was
    learned; the scan result never depends on the cache being present."""
    names, reported = scan_event_dir(repo, REVIEW_DIR)
    events: list[ReviewEvent] = []
    for name in names:
        where = f"{REQHARNESS_DIR}/{REVIEW_DIR}/{name}"
        try:
            events.append(_load_one(repo, name, cache))
        except ValidationError as exc:
            reported.append(str(exc))
        except ValueError as exc:  # unhashable keys etc. — named, not a crash
            reported.append(f"{where}: {exc}")
    return ReviewScan(events=tuple(events), reported=tuple(reported))


__all__ = [
    "KINDS",
    "NAME_RE",
    "REVIEW_DIR",
    "ReviewEvent",
    "ReviewScan",
    "load_reviews",
    "next_seq",
    "record_review",
    "scan_event_dir",
]
