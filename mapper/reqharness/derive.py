"""Derived object states under the explicit R5 precedence table (HLR-RH.5).

The registry is DERIVED (P0 ruling O1): the canon — the HLR/LLR rows of
`REQUIREMENTS.md` — is the single source of object content; review events
carry the digests; the chain carries the authority.  `derive_states` folds
the three together and assigns each canon object exactly one state:

    reviewed        a kind:human review matches the CURRENT normative digest
                    and its signer held the class's reviewer_role at its
                    BOUND HEAD (authority at the bound head, never
                    wall-clock — R2)
    "changed · review"  reviews exist but none matches the current digest
                    (a stale-digest review never closes)
    pre-reviewed    reviews exist on the current digest but none is a
                    qualifying human review — the newest is a self-declared
                    model review, or its signer held no designated role at
                    the bound head (flagged unentitled, counted apart, never
                    blocking alone — R5)
    "not reviewed"  no review event names the id
    retired         the canon marks the id withdrawn (status starting with
                    "withdrawn") — excluded from every release rule

The precedence (explicit, R5/R14): (1) `not verifiable` — a chain/policy
break or a review bound to a head that does not exist in the current chain —
dominates every outcome; (2) a newer pre-review NEVER downgrades a
qualifying human review on the same digest; (3) a review on a stale digest
never closes; (4) unentitled reviews are reported and counted apart; (5)
retired objects are excluded from every release rule; (6) an unparseable
canon row is REPORTED by line and derives no state — never silently skipped.

The informative mark: while the normative digest matches, an
informative_digest different from the newest review's recorded one raises
the visible `changed (informative)` mark WITHOUT changing the state
(B-121 ruling 2; the informative fields never feed the normative digest —
M-RG1).

The normative/informative digests are sha256 of the canonical JSON of
`{field: normalised value}` over the class's field sets (R3 — never a
concatenation).  Old-head binding (R17): a review whose bound head precedes
a LATER revocation of its signer's role earns a non-blocking WARN line —
a stated residual, layer 3 remains the strong answer.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from mapper.reqharness.canonical import canonical_digest, nfc
from mapper.reqharness.chain import ChainReport, effective_roles
from mapper.reqharness.config import LIMIT_ROLES_YML_BYTES
from mapper.reqharness.records import (
    REASON_AUTHOR,
    REASON_NO_ROLE,
    REASON_OWNING_BATCH_MISMATCH,
    REASON_OWNING_BATCH_MISSING,
    Config,
    ValidationError,
)
from mapper.reqharness.reviews import ReviewScan

CANON_NAME = "REQUIREMENTS.md"

STATE_REVIEWED = "reviewed"
STATE_CHANGED = "changed \u00b7 review"  # changed · review
STATE_PRE_REVIEWED = "pre-reviewed"
STATE_NOT_REVIEWED = "not reviewed"
STATE_RETIRED = "retired"
INFORMATIVE_MARK = "changed (informative)"
NOT_VERIFIABLE = "not verifiable"

#: HLR/LLR rows are the objects of record; anything else in the table is
#: not an object and is skipped silently (it has no review semantics).
_ROW_ID_RE = re.compile(r"^(HLR|LLR)-\S+$")


@dataclass(frozen=True)
class CanonObject:
    """One canon row: id, class (from the id prefix) and its field values
    (`statement`, any informative-field column such as `rationale`, and
    `status`), remembered by line for named reports.  `owning_batch` is the
    `Owning batch` column (no longer dropped — HLR-RS.5); a blank cell is
    the empty string."""

    id: str
    class_id: str
    fields: dict[str, str]
    line: int
    owning_batch: str = ""


@dataclass(frozen=True)
class Derivation:
    """The derived registry: one state per (non-reported) canon object.

    `verifiable` is False exactly when a chain/policy break or an unknown
    recorded head dominates — every other field is empty then and the
    release verdict is `not ready · registry not verifiable`.

    `unentitled` carries the FILE NAMES of the human reviews that must NOT
    count toward `reviewed`, counted apart and never blocking alone (R5).
    An `unentitled` review has ONE OR MORE causes — `no_role` (the signer
    held no designated role at its bound head), `author` (the signer is an
    author of the object's owning batch — HLR-RS.5) or
    `owning_batch_mismatch` (the STORED owning batch differs from the
    object's current cell — F1).  A fourth cause, `owning_batch_missing`,
    fires ONLY when authorship is declared (`authors` non-empty): a human
    review whose record carries no `owning_batch` (absent or empty) is then
    unentitled because the mismatch cannot be checked.  `unentitled_reasons`
    records the `(file name, reason code)` pairs; a legacy record without
    `owning_batch` is evaluated as today (no mismatch or missing cause) only
    when no authorship is declared.  `authors_missing` lists the object ids
    of ACTIVE objects whose owning batch is blank or absent from the config
    `authors` map — the data the `authors_declared` release rule reads."""

    verifiable: bool
    states: dict[str, str] = field(default_factory=dict)
    informative_marks: tuple[str, ...] = ()
    pre_reviewed: tuple[str, ...] = ()
    unentitled: tuple[str, ...] = ()
    unentitled_reasons: tuple[tuple[str, str], ...] = ()
    authors_missing: tuple[str, ...] = ()
    reported: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    reason: str | None = None


def _collapse(value: str) -> str:
    """The canon-cell normalisation: whitespace collapsed (the worked
    example of design §3.3 — NFC happens inside the canonical digest)."""
    return " ".join(value.split())


def parse_canon(text: str) -> tuple[tuple[CanonObject, ...], tuple[str, ...]]:
    """The minimal canon reader over the `REQUIREMENTS.md` table shape.

    The header row names the columns; `Id` and `Status` are required, every
    other column becomes a field (`statement`, plus any informative-field
    column a fixture carries).  A row whose id looks like an object id but
    whose cells do not match the header is REPORTED by line — never guessed,
    never silently skipped (R14)."""
    header: list[str] | None = None
    objects: list[CanonObject] = []
    reported: list[str] = []
    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        first = cells[0] if cells else ""
        if header is None:
            lowered = [cell.lower() for cell in cells]
            if first.lower() == "id":
                if "status" not in lowered:
                    reported.append(
                        f"{CANON_NAME} line {line_no}: header has no Status column"
                    )
                    continue
                header = lowered
            continue
        if not _ROW_ID_RE.fullmatch(first):
            continue  # a table row that is not an object of record
        if len(cells) != len(header):
            reported.append(
                f"{CANON_NAME} line {line_no}: cannot parse row for {first!r} "
                f"({len(cells)} cells, expected {len(header)})"
            )
            continue
        fields = {
            name: _collapse(value)
            for name, value in zip(header, cells)
            if name not in ("id", "owning batch")
        }
        owning_batch = nfc(
            _collapse(
                next(
                    (value for name, value in zip(header, cells) if name == "owning batch"),
                    "",
                )
            )
        )
        class_id = first.split("-", 1)[0]
        objects.append(
            CanonObject(
                id=first,
                class_id=class_id,
                fields=fields,
                line=line_no,
                owning_batch=owning_batch,
            )
        )
    return tuple(objects), tuple(reported)


def load_canon(repo: str | Path) -> tuple[tuple[CanonObject, ...], tuple[str, ...]]:
    """Read and parse `<repo>/REQUIREMENTS.md` (the canon lives at the repo
    root, not under `reqharness/`); a missing or unreadable file is a named
    ValidationError (R9)."""
    path = Path(repo) / CANON_NAME
    where = CANON_NAME
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        raise ValidationError(f"{where}: file not found") from None
    except OSError as exc:
        raise ValidationError(f"{where}: cannot read ({exc})") from exc
    if len(raw) > LIMIT_ROLES_YML_BYTES:
        raise ValidationError(
            f"{where}: file too large ({len(raw)} bytes > {LIMIT_ROLES_YML_BYTES} byte limit)"
        )
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"{where}: not valid UTF-8 ({exc})") from exc
    return parse_canon(text)


def object_digests(cls, fields: dict[str, str]) -> tuple[str, str]:
    """(normative_digest, informative_digest): sha256 of the canonical JSON
    of `{field: normalised value}` over the class's field sets — never a
    concatenation (R3).  M-RG1 folds the informative fields into the
    normative digest; the two stay separate here."""
    normative = canonical_digest({name: fields.get(name, "") for name in cls.normative_fields})
    informative = canonical_digest(
        {name: fields.get(name, "") for name in cls.informative_fields}
    )
    return normative, informative


def _role_in_force(report: ChainReport, review, role: str) -> bool:
    """True when the review's signer held *role* in the VERIFIED chain at
    the review's BOUND HEAD — never at today's head (M-RG2)."""
    try:
        held = effective_roles(report, review.roles_seq, review.roles_hash)
    except ValidationError:
        return False
    return role in held.get(review.reviewer, ())


def _known_head(report: ChainReport, review) -> bool:
    """The recorded head exists in the current verified chain (R2/R17)."""
    return (
        1 <= review.roles_seq <= len(report.events)
        and report.events[review.roles_seq - 1].this_hash == review.roles_hash
    )


def _unentitled_reasons(
    report: ChainReport,
    review,
    cls,
    obj: CanonObject,
    authors_map: dict[str, tuple[str, ...]],
) -> tuple[str, ...]:
    """The causes a human review is unentitled for (HLR-RS.5 / F1), in a
    fixed order: `owning_batch_missing`, `owning_batch_mismatch`, `author`,
    `no_role`.  A model review is never unentitled (it stays pre-review).
    `owning_batch_missing` fires ONLY when authorship is declared
    (`authors_map` non-empty) and the review's record lacks `owning_batch`
    (absent or empty) — the mismatch cannot be checked.  A legacy record
    without `owning_batch` is evaluated as today only when no authorship is
    declared, and a blank or undeclared owning batch has no author set."""
    if review.kind != "human":
        return ()
    reasons: list[str] = []
    if authors_map and not review.owning_batch:
        reasons.append(REASON_OWNING_BATCH_MISSING)
    if review.owning_batch and review.owning_batch != obj.owning_batch:
        reasons.append(REASON_OWNING_BATCH_MISMATCH)
    if obj.owning_batch and review.reviewer in authors_map.get(obj.owning_batch, ()):
        reasons.append(REASON_AUTHOR)
    if not _role_in_force(report, review, cls.reviewer_role):
        reasons.append(REASON_NO_ROLE)
    return tuple(reasons)


def derive_states(
    canon: tuple[CanonObject, ...],
    scan: ReviewScan,
    report: ChainReport,
    config: Config,
) -> Derivation:
    """The derivation: canon rows + review events + the verified chain,
    under the R5 precedence table.  Pure — reads, never writes."""
    reported = list(scan.reported)

    if not report.ok:
        # Precedence (1): a chain/policy break dominates every outcome.
        return Derivation(verifiable=False, reason=report.status, reported=tuple(reported))

    unknown = [event.name for event in scan.events if not _known_head(report, event)]
    if unknown:
        # Precedence (1): a review bound to a head the chain no longer
        # contains — truncation and rewrite detection (R2).
        reported.extend(
            f"reviews/{name}: bound head is not in the current chain (not verifiable)"
            for name in unknown
        )
        return Derivation(verifiable=False, reason=NOT_VERIFIABLE, reported=tuple(reported))

    classes = {cls.id: cls for cls in config.classes}
    authors_map = {batch: people for batch, people in config.authors}
    by_object: dict[str, list] = {}
    for event in scan.events:
        by_object.setdefault(event.object, []).append(event)

    states: dict[str, str] = {}
    marks: list[str] = []
    pre_reviewed: list[str] = []
    unentitled: list[str] = []
    unentitled_reasons: list[tuple[str, str]] = []
    authors_missing: list[str] = []
    warnings: list[str] = []

    for obj in canon:
        cls = classes.get(obj.class_id)
        if cls is None:
            reported.append(
                f"{CANON_NAME} line {obj.line}: class {obj.class_id!r} is not "
                "declared in config"
            )
            continue
        status = obj.fields.get("status", "")
        if status.lower().startswith("withdrawn"):
            states[obj.id] = STATE_RETIRED  # excluded from every release rule (R5)
            continue
        if not obj.owning_batch or obj.owning_batch not in authors_map:
            authors_missing.append(obj.id)  # the authors_declared rule reads this
        normative, informative = object_digests(cls, obj.fields)
        reviews = sorted(
            by_object.get(obj.id, ()), key=lambda event: (event.time, event.name)
        )
        if not reviews:
            states[obj.id] = STATE_NOT_REVIEWED
            continue
        matching = [r for r in reviews if r.normative_digest == normative]
        qualifying = [
            r
            for r in matching
            if r.kind == "human"
            and not _unentitled_reasons(report, r, cls, obj, authors_map)
        ]
        if qualifying:
            # Precedence (2): a newer pre-review never downgrades this.
            states[obj.id] = STATE_REVIEWED
            newest = reviews[-1]
            if newest.normative_digest == normative and (
                newest.informative_digest != informative
            ):
                marks.append(obj.id)  # the visible informative mark
        elif matching:
            states[obj.id] = STATE_PRE_REVIEWED
            pre_reviewed.append(obj.id)
        else:
            states[obj.id] = STATE_CHANGED  # a stale digest never closes
        # Unentitled reviews are human reviews with one or more of the three
        # causes (role / author / owning-batch mismatch), counted apart (R5).
        for review in reviews:
            reasons = _unentitled_reasons(report, review, cls, obj, authors_map)
            if not reasons:
                continue
            unentitled.append(review.name)
            unentitled_reasons.extend((review.name, reason) for reason in reasons)
        for review in reviews:
            if review.kind != "human":
                continue
            if not _role_in_force(report, review, cls.reviewer_role):
                continue
            later_revocation = any(
                event.action == "revoke"
                and event.person == review.reviewer
                and event.role == cls.reviewer_role
                and event.roles_seq > review.roles_seq
                for event in report.events
            )
            if later_revocation:
                warnings.append(
                    f"{obj.id}: review by {review.reviewer} is bound before a "
                    "later revocation of their role (old-head binding — a "
                    "stated residual, R17)"
                )

    return Derivation(
        verifiable=True,
        states=states,
        informative_marks=tuple(marks),
        pre_reviewed=tuple(pre_reviewed),
        unentitled=tuple(unentitled),
        unentitled_reasons=tuple(unentitled_reasons),
        authors_missing=tuple(authors_missing),
        reported=tuple(reported),
        warnings=tuple(warnings),
    )


__all__ = [
    "CANON_NAME",
    "Derivation",
    "CanonObject",
    "INFORMATIVE_MARK",
    "NOT_VERIFIABLE",
    "STATE_CHANGED",
    "STATE_NOT_REVIEWED",
    "STATE_PRE_REVIEWED",
    "STATE_RETIRED",
    "STATE_REVIEWED",
    "derive_states",
    "load_canon",
    "object_digests",
    "parse_canon",
]
