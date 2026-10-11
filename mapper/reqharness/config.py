"""Typed config schema, the refusing YAML loader and registry creation (HLR-RH.1).

LLR-RH.1.1 — the loader: a custom subclass on `yaml.CSafeLoader` when
available, `yaml.SafeLoader` otherwise — never `yaml.load` with any other
loader (R-SCALE a + R21; census-enforced).  The subclass refuses duplicate
keys at construction time; anchors/aliases are refused by scanning the event
stream first, because the C composer resolves aliases before Python-level
overrides can see them (the fallback loader gets the identical refusal through
the same scan).

LLR-RH.1.2 — `create_registry` writes `config.yml` plus a `roles.yml` whose
single genesis document records `roles_hash: "GENESIS"` (no self-reference)
and `config_hash` = sha256(canonical config at creation), so the registry is
policy-bound from the first document (R15).

LLR-RH.1.3 — the typed schema: every field `str` except `seq`/`roles_seq: int`;
unknown keys, missing keys and non-`str` scalars rejected with every field
isinstance-checked; `time` fields match exactly `YYYY-MM-DDTHH:MM:SSZ` (R18);
the writer always quotes scalars (SafeDumper quotes exactly the scalars that
would otherwise coerce), values are NFC-normalised before hashing.

LLR-RH.1.4 — emails are stored only as `email_sha256`, sha256 of the LOWERCASED
address (R12; NFC-normalised per R3 — the spec says lowercased and nothing
else, so whitespace is NOT stripped).  `email_sha256` is pseudonymised
personal data — unsalted, dictionary-reversible; the jurisdiction question
goes to the operator (R23).
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from mapper.osopen import confine_reason
from mapper.reqharness.canonical import canonical_digest, chain_hash, nfc
from mapper.reqharness.records import (
    Config,
    Person,
    ReleaseRule,
    ReqClass,
    ValidationError,
    YamlRefusal,
)

REQHARNESS_DIR = "reqharness"
CONFIG_NAME = "config.yml"
ROLES_NAME = "roles.yml"
PENDING_DIR = "pending"
GENESIS_PREV = "GENESIS"
GENESIS_NOTE = "declared at registry creation"

# Input limits (R9) — the named home every limit reported by name reads from.
# Their ENFORCEMENT lands with the increments that load the bounded files —
# LIMIT_ROLES_YML_BYTES with the chain reader (RH2), LIMIT_EVENT_FILE_BYTES
# and LIMIT_REVIEW_FILE_COUNT with the reviews/pending store (RH4); this
# increment declares and exports the names so they are pinned before the
# consumers exist.
LIMIT_EVENT_FILE_BYTES = 64 * 1024  # per review/pending file
LIMIT_ROLES_YML_BYTES = 4 * 1024 * 1024  # roles.yml
LIMIT_REVIEW_FILE_COUNT = 100_000  # review files per registry

#: The nesting ceiling (SEC F2, DDRFIX-C): the AUTHORITATIVE bound is the
#: event stream — `load_documents` counts collection start events during the
#: `yaml.parse` pass (the same pass that refuses anchors/aliases) and raises
#: the named refusal the moment depth exceeds this, BEFORE compose/construct,
#: so a pathological deep-nesting file can never drive the parser's
#: superlinear behaviour nor the C composer's recursion.  A lexical pre-scan
#: is deliberately NOT used: plain-scalar apostrophes, compact block
#: sequences and complex keys made it bypassable.
LIMIT_NESTING_DEPTH = 64

#: The content-derived event-name shape (R8) — the one shape every
#: review/pending file name carries; `reviews.py` pins the identical regex
#: for the review store and every loader recomputes the groups at read.
EVENT_NAME_RE = re.compile(r"(\d{8})-([0-9a-f]{8})\.yml\Z", re.ASCII)

# re.ASCII pins `\d` to 0-9 (Arabic-Indic digits must NOT satisfy the time
# schema), and fullmatch — not match with `$` — refuses a trailing "\n"
# (`$` admits one): the time format is exact, R18.
TIME_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", re.ASCII)

# R-SCALE a + R21: CSafeLoader when the libyaml bindings exist, SafeLoader
# otherwise — these two bases ONLY, never yaml.load with any other loader.
_LoaderBase = getattr(yaml, "CSafeLoader", None) or yaml.SafeLoader


class ReqHarnessLoader(_LoaderBase):
    """The one YAML loader for every reqharness file.  Duplicate keys are
    refused here, at construction time, before the mapping collapses them."""

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            seen: set[Any] = set()
            for key_node, _value_node in node.value:
                key = self.construct_object(key_node, deep=True)
                try:
                    duplicate = key in seen
                except TypeError:
                    continue  # an unhashable key cannot be duplicate-checked
                if duplicate:
                    raise YamlRefusal(f"duplicate key: {key!r}")
                seen.add(key)
        return super().construct_mapping(node, deep=deep)


def load_documents(text: str, *, where: str) -> list[Any]:
    """Every YAML document in *text*, parsed through the one loader.

    Refusals are named, never silent (R9): anchors/aliases (R21), duplicate
    keys, nesting deeper than `LIMIT_NESTING_DEPTH` (SEC F2 — counted on the
    event stream, before compose/construct), syntax errors and parser
    deep-nesting failures (RecursionError/ValueError, the
    mapper/store.py:706-720 ladder) all become a ValidationError naming
    *where*.

    SEC F2 (DDRFIX-C): the event iteration itself is the bound.  The C
    parser is an explicit state machine — `yaml.parse` yields events
    iteratively, with no recursion per nesting level — so counting
    SequenceStart/MappingStart (+1) and their End events (-1) in the same
    pass that refuses anchors/aliases is linear, never recursive, and raises
    the moment depth exceeds the ceiling: the parser never composes a
    deeper structure, and the multi-MB flood attacks are refused after ~65
    events, not after ~4 MB of parsing.
    """
    depth = 0
    try:
        # Aliases are resolved inside the C composer before any Python-level
        # compose hook runs, so anchors/aliases are refused on the event
        # stream — one scan serves both loader bases with identical
        # behaviour (and carries the SEC F2 depth count, DDRFIX-C).
        for event in yaml.parse(text, Loader=ReqHarnessLoader):
            if isinstance(event, yaml.AliasEvent) or getattr(event, "anchor", None):
                raise YamlRefusal("anchors and aliases are not allowed")
            if isinstance(event, (yaml.SequenceStartEvent, yaml.MappingStartEvent)):
                depth += 1
                if depth > LIMIT_NESTING_DEPTH:
                    raise ValidationError(
                        f"{where}: nesting too deep (depth "
                        f"{depth} > {LIMIT_NESTING_DEPTH})"
                    )
            elif isinstance(event, (yaml.SequenceEndEvent, yaml.MappingEndEvent)):
                depth -= 1
        return list(yaml.load_all(text, Loader=ReqHarnessLoader))
    except YamlRefusal as exc:
        raise YamlRefusal(f"{where}: {exc}") from exc
    except ValidationError:
        # The named refusals raised by this function itself (the SEC F2
        # `nesting too deep` depth count) are ValidationError — a ValueError
        # subclass — so they must surface as themselves; re-wrapping them
        # below would double the `<where>:` prefix.  (K3 re-check LOW-1.)
        raise
    except (yaml.YAMLError, ValueError, RecursionError) as exc:
        raise ValidationError(f"{where}: malformed YAML ({exc})") from exc


# ---------------------------------------------------------------------------
# The confined event-file reader (R8/R9) — ARCH C3: shared leaf pieces
# ---------------------------------------------------------------------------
#
# `chain` and `pending` both read <= 64 KB event files under `reqharness/`
# through this ONE reader; it lives here, in the leaf every reqharness
# module may import, so neither direction of a chain<->pending module
# edge is ever needed to reach it.


def _confine(repo: str | Path, where: str) -> Path:
    resolved, reason = confine_reason(where, Path(repo))
    if reason != "ok" or resolved is None:
        raise ValidationError(f"{where}: refused ({reason})")
    return resolved


def _read_text(path: Path, *, where: str, limit: int) -> str:
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        raise ValidationError(f"{where}: file not found") from None
    except OSError as exc:
        raise ValidationError(f"{where}: cannot read ({exc})") from exc
    if len(raw) > limit:
        raise ValidationError(
            f"{where}: file too large ({len(raw)} bytes > {limit} byte limit)"
        )
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"{where}: not valid UTF-8 ({exc})") from exc


def read_event_file(repo: str | Path, name: str) -> str:
    """A <= 64 KB reqharness event file (a review or a pending request),
    confined and named (R8/R9); the reviews and pending stores share it."""
    where = f"{REQHARNESS_DIR}/{name}"
    return _read_text(_confine(repo, where), where=where, limit=LIMIT_EVENT_FILE_BYTES)


# ---------------------------------------------------------------------------
# Typed schema (LLR-RH.1.3)
# ---------------------------------------------------------------------------


def check_str(value: Any, *, where: str, field: str) -> str:
    """The isinstance check every field carries: all fields are `str`."""
    if not isinstance(value, str):
        raise ValidationError(
            f"{where}: field {field!r} must be a str, "
            f"got {type(value).__name__} ({value!r})"
        )
    return value


def check_int(value: Any, *, where: str, field: str) -> int:
    """The type check the chain's `seq`/`roles_seq` ints carry: EXACTLY `int`
    — `type(v) is int`, not isinstance, because `bool` subclasses `int` and
    `True` must never count as seq 1 (LLR-RH.1.3).  This is the shared
    helper the chain reader (RH2) imports for event validation; wherever
    config.py constructs a `seq`/`roles_seq` it passes through here."""
    if type(value) is not int:
        raise ValidationError(
            f"{where}: field {field!r} must be an int, "
            f"got {type(value).__name__} ({value!r})"
        )
    return value


def check_time(value: Any, *, where: str, field: str) -> str:
    """A chain `time` field: exactly `YYYY-MM-DDTHH:MM:SSZ` (R18)."""
    value = check_str(value, where=where, field=field)
    if not TIME_RE.fullmatch(value):
        raise ValidationError(
            f"{where}: field {field!r} must match YYYY-MM-DDTHH:MM:SSZ exactly, "
            f"got {value!r}"
        )
    return value


def _check_list(value: Any, *, where: str, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValidationError(
            f"{where}: field {field!r} must be a list, "
            f"got {type(value).__name__} ({value!r})"
        )
    return value


def _check_exact_keys(
    mapping: Any, expected: set[str], *, where: str
) -> dict[str, Any]:
    """Unknown keys rejected, missing keys rejected (LLR-RH.1.3)."""
    if not isinstance(mapping, dict):
        raise ValidationError(
            f"{where}: expected a mapping, got {type(mapping).__name__} "
            f"({mapping!r})"
        )
    keys = set(mapping)
    unknown = sorted(str(k) for k in keys - expected)
    if unknown:
        raise ValidationError(f"{where}: unknown key(s): {', '.join(unknown)}")
    missing = sorted(expected - keys)
    if missing:
        raise ValidationError(f"{where}: missing key(s): {', '.join(missing)}")
    return mapping


def _check_str_list(value: Any, *, where: str, field: str) -> tuple[str, ...]:
    items = _check_list(value, where=where, field=field)
    for index, item in enumerate(items):
        check_str(item, where=where, field=f"{field}[{index}]")
    return tuple(items)


_CONFIG_KEYS = {"version", "people", "roles", "classes", "release_rules"}
_PERSON_KEYS = {"id", "name", "email_sha256"}
_CLASS_KEYS = {"id", "reviewer_role", "normative_fields", "informative_fields"}
_ID_KEYS = {"id"}


def validate_config(document: Any, *, where: str = f"{REQHARNESS_DIR}/{CONFIG_NAME}") -> Config:
    """The typed schema over a config document, cross-checks included:
    every class's `reviewer_role` must be a declared role, and normative and
    informative field sets must be disjoint lists of strings (R5)."""
    document = _check_exact_keys(document, _CONFIG_KEYS, where=where)
    version = check_str(document["version"], where=where, field="version")

    people = []
    for index, raw in enumerate(_check_list(document["people"], where=where, field="people")):
        person = _check_exact_keys(raw, _PERSON_KEYS, where=f"{where}: people[{index}]")
        people.append(
            Person(
                id=check_str(person["id"], where=where, field=f"people[{index}].id"),
                name=check_str(person["name"], where=where, field=f"people[{index}].name"),
                email_sha256=check_str(
                    person["email_sha256"], where=where, field=f"people[{index}].email_sha256"
                ),
            )
        )

    roles = []
    for index, raw in enumerate(_check_list(document["roles"], where=where, field="roles")):
        role = _check_exact_keys(raw, _ID_KEYS, where=f"{where}: roles[{index}]")
        roles.append(check_str(role["id"], where=where, field=f"roles[{index}].id"))
    if len(set(roles)) != len(roles):
        raise ValidationError(f"{where}: duplicate role id(s)")

    classes = []
    for index, raw in enumerate(_check_list(document["classes"], where=where, field="classes")):
        cls_where = f"{where}: classes[{index}]"
        cls = _check_exact_keys(raw, _CLASS_KEYS, where=cls_where)
        class_id = check_str(cls["id"], where=where, field=f"classes[{index}].id")
        normative = _check_str_list(
            cls["normative_fields"], where=cls_where, field="normative_fields"
        )
        informative = _check_str_list(
            cls["informative_fields"], where=cls_where, field="informative_fields"
        )
        overlap = sorted(set(normative) & set(informative))
        if overlap:
            raise ValidationError(
                f"{cls_where}: class={class_id} normative/informative overlap: "
                f"{', '.join(overlap)}"
            )
        classes.append(
            ReqClass(
                id=class_id,
                reviewer_role=check_str(
                    cls["reviewer_role"], where=where, field=f"classes[{index}].reviewer_role"
                ),
                normative_fields=normative,
                informative_fields=informative,
            )
        )

    role_ids = set(roles)
    for cls in classes:
        if cls.reviewer_role not in role_ids:
            raise ValidationError(
                f"{where}: class={cls.id} role={cls.reviewer_role} is not a declared role"
            )

    release_rules = []
    for index, raw in enumerate(
        _check_list(document["release_rules"], where=where, field="release_rules")
    ):
        rule = _check_exact_keys(raw, _ID_KEYS, where=f"{where}: release_rules[{index}]")
        release_rules.append(
            ReleaseRule(
                id=check_str(rule["id"], where=where, field=f"release_rules[{index}].id")
            )
        )

    return Config(
        version=version,
        people=tuple(people),
        roles=tuple(roles),
        classes=tuple(classes),
        release_rules=tuple(release_rules),
    )


# ---------------------------------------------------------------------------
# Email hashing (LLR-RH.1.4)
# ---------------------------------------------------------------------------


def email_sha256(email: str) -> str:
    """sha256 of the lowercased, NFC-normalised address — the ONLY form an
    email is stored in (R12).  LLR-RH.1.4 says LOWERCASED and nothing else:
    no `strip()` — surrounding whitespace is part of the address and changes
    the hash; NFC per R3 (values are normalised before hashing)."""
    return hashlib.sha256(nfc(email.lower()).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Load / create (LLR-RH.1.1 / LLR-RH.1.2)
# ---------------------------------------------------------------------------


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dump(document: Any) -> str:
    """The writer: SafeDumper, which quotes exactly the scalars that would
    otherwise coerce (timestamps, `no`, `1`, empty) — the typed schema's
    writer-side half (R3)."""
    return yaml.safe_dump(document, sort_keys=False, allow_unicode=True)


def canonical_config(config: Config) -> dict[str, Any]:
    """The normalised `{field: value}` form hashing binds to (R3)."""
    return {
        "version": config.version,
        "people": [
            {"id": p.id, "name": p.name, "email_sha256": p.email_sha256}
            for p in config.people
        ],
        "roles": [{"id": role} for role in config.roles],
        "classes": [
            {
                "id": cls.id,
                "reviewer_role": cls.reviewer_role,
                "normative_fields": list(cls.normative_fields),
                "informative_fields": list(cls.informative_fields),
            }
            for cls in config.classes
        ],
        "release_rules": [{"id": rule.id} for rule in config.release_rules],
    }


def config_digest(config: Config) -> str:
    """sha256(canonical config) — the value `policy` events and genesis bind."""
    return canonical_digest(canonical_config(config))


def load_config(repo: str | Path) -> Config:
    """Load and validate `reqharness/config.yml` inside *repo*.

    Every refusal names the file (R9); a missing file, a file over the
    `LIMIT_EVENT_FILE_BYTES` cap (R9 — the same 64 KB ceiling the event
    files carry), bad UTF-8, malformed YAML or a schema violation is a
    ValidationError, never a traceback.
    """
    where = f"{REQHARNESS_DIR}/{CONFIG_NAME}"
    path = Path(repo) / REQHARNESS_DIR / CONFIG_NAME
    text = _read_text(path, where=where, limit=LIMIT_EVENT_FILE_BYTES)
    documents = load_documents(text, where=where)
    if len(documents) != 1:
        raise ValidationError(
            f"{where}: expected exactly 1 document, found {len(documents)}"
        )
    return validate_config(nfc(documents[0]), where=where)


_DEFAULT_CLASSES = (
    {
        "id": "HLR",
        "reviewer_role": "req-reviewer",
        "normative_fields": ["statement"],
        "informative_fields": ["rationale"],
    },
    {
        "id": "LLR",
        "reviewer_role": "req-reviewer",
        "normative_fields": ["statement"],
        "informative_fields": [],
    },
)

_DEFAULT_RELEASE_RULES = ("all_active_reviewed", "chain_verified", "signers_in_force")


class RegistryExistsError(ValidationError):
    """`create_registry` found an existing registry and refused to touch it.

    A registry is created only into empty ground: an existing `config.yml`
    or `roles.yml` is never overwritten, and the refusal names the file (R9)."""


def create_registry(
    repo: str | Path,
    *,
    person: str,
    name: str,
    email: str,
    now: str | None = None,
    roles: tuple[str, ...] = ("admin", "req-reviewer"),
    classes: tuple[dict[str, Any], ...] = _DEFAULT_CLASSES,
    release_rules: tuple[str, ...] = _DEFAULT_RELEASE_RULES,
) -> Config:
    """Create a fresh registry in *repo*: `config.yml` plus a `roles.yml`
    whose genesis document is policy-bound from the first document (R15) —
    `config_hash` = sha256(canonical config at creation), `roles_hash:
    "GENESIS"` (no self-reference), `prev_hash: GENESIS`, and a `this_hash`
    that verifies by the chain-link recomputation."""
    now = (
        check_time(now, where="create_registry", field="now")
        if now is not None
        else _utc_now()
    )
    document = nfc(
        {
            "version": "1",
            "people": [
                {"id": person, "name": name, "email_sha256": email_sha256(email)}
            ],
            "roles": [{"id": role} for role in roles],
            "classes": [dict(cls) for cls in classes],
            "release_rules": [{"id": rule} for rule in release_rules],
        }
    )
    config = validate_config(document)
    target = Path(repo) / REQHARNESS_DIR
    existing = [
        name for name in (CONFIG_NAME, ROLES_NAME) if (target / name).is_file()
    ]
    if existing:
        raise RegistryExistsError(
            f"{REQHARNESS_DIR}: registry already exists "
            f"({', '.join(existing)}); refusing to overwrite"
        )
    target.mkdir(parents=True, exist_ok=True)
    (target / CONFIG_NAME).write_text(_dump(document), encoding="utf-8", newline="\n")

    event: dict[str, Any] = {
        "seq": check_int(1, where="create_registry", field="seq"),
        "time": now,
        "requested_by": person,
        "approved_by": "genesis",
        "action": "genesis",
        "person": person,
        "role": "admin",
        "note": GENESIS_NOTE,
        "config_hash": config_digest(config),
        "roles_seq": check_int(1, where="create_registry", field="roles_seq"),
        "roles_hash": GENESIS_PREV,
        "prev_hash": GENESIS_PREV,
    }
    event["this_hash"] = chain_hash(GENESIS_PREV, event)
    (target / ROLES_NAME).write_text(
        "---\n" + _dump(event), encoding="utf-8", newline="\n"
    )
    return config


# ---------------------------------------------------------------------------
# The pending-request schema and loader (R6/R8/R22) — ARCH C3: the shared
# validator lives in this leaf, so `chain` (the write side) imports it at
# module level instead of closing a chain<->pending import cycle.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PendingRequest:
    """One parsed pending request file — every stored field, named."""

    name: str
    digest: str  # the canonical content hash a resolution event must reference
    requested_by: str
    action: str  # grant | revoke
    person: str
    role: str
    note: str
    time: str
    roles_seq: int
    roles_hash: str


_PENDING_KEYS = {
    "requested_by",
    "change",
    "time",
    "note",
    "roles_seq",
    "roles_hash",
}
_PENDING_CHANGE_KEYS = {"action", "person", "role"}
_PENDING_ACTIONS = frozenset({"grant", "revoke"})


def validate_pending_document(document: Any, *, name: str, where: str) -> PendingRequest:
    """The typed schema over one pending document — named by file (R9).

    The request hash is the canonical digest of the (NFC-normalised)
    document — the full-hex form of the content-derived name the file was
    written under (`<yyyymmdd>-<sha8>.yml`, R8).  The loader recomputes it
    at read; a name/content mismatch is reported BY NAME and non-closing
    (R22)."""
    if not isinstance(document, dict):
        raise ValidationError(
            f"{where}: expected a mapping, got {type(document).__name__} ({document!r})"
        )
    keys = set(document)
    unknown = sorted(str(k) for k in keys - _PENDING_KEYS)
    if unknown:
        raise ValidationError(f"{where}: unknown key(s): {', '.join(unknown)}")
    missing = sorted(_PENDING_KEYS - keys)
    if missing:
        raise ValidationError(f"{where}: missing key(s): {', '.join(missing)}")
    change = document["change"]
    if not isinstance(change, dict):
        raise ValidationError(
            f"{where}: change must be a mapping, got {type(change).__name__} ({change!r})"
        )
    change_keys = set(change)
    unknown = sorted(str(k) for k in change_keys - _PENDING_CHANGE_KEYS)
    if unknown:
        raise ValidationError(f"{where}: change has unknown key(s): {', '.join(unknown)}")
    missing = sorted(_PENDING_CHANGE_KEYS - change_keys)
    if missing:
        raise ValidationError(f"{where}: change has missing key(s): {', '.join(missing)}")
    action = check_str(change["action"], where=where, field="change.action")
    if action not in _PENDING_ACTIONS:
        raise ValidationError(
            f"{where}: change.action must be grant/revoke, got {action!r}"
        )
    seq = document["roles_seq"]
    if type(seq) is not int:
        raise ValidationError(
            f"{where}: field 'roles_seq' must be an int, "
            f"got {type(seq).__name__} ({seq!r})"
        )
    digest = canonical_digest(nfc(document))
    match = EVENT_NAME_RE.fullmatch(name)
    when = document["time"]
    date = f"{when[0:4]}{when[5:7]}{when[8:10]}" if isinstance(when, str) else ""
    if match is None or match.group(1) != date or match.group(2) != digest[:8]:
        raise ValidationError(
            f"{where}: name/content mismatch "
            f"(recomputed sha8 {digest[:8]} of the canonical content, R22)"
        )
    return PendingRequest(
        name=name,
        digest=digest,
        requested_by=check_str(document["requested_by"], where=where, field="requested_by"),
        action=action,
        person=check_str(change["person"], where=where, field="change.person"),
        role=check_str(change["role"], where=where, field="change.role"),
        note=check_str(document["note"], where=where, field="note"),
        time=check_time(document["time"], where=where, field="time"),
        roles_seq=seq,
        roles_hash=check_str(document["roles_hash"], where=where, field="roles_hash"),
    )


def load_pending(repo: str | Path, name: str) -> PendingRequest:
    """One pending request file, confined, size-limited, schema-checked and
    content-checked by name (R8/R9/R22) — the ONE validator the write side
    (`chain.approve_pending`/`reject_pending`) and the read side
    (`pending.list_pending`) share."""
    where = f"{REQHARNESS_DIR}/{PENDING_DIR}/{name}"
    documents = load_documents(
        read_event_file(repo, f"{PENDING_DIR}/{name}"), where=where
    )
    if len(documents) != 1:
        raise ValidationError(
            f"{where}: expected exactly 1 document, found {len(documents)}"
        )
    return validate_pending_document(documents[0], name=name, where=where)


__all__ = [
    "CONFIG_NAME",
    "EVENT_NAME_RE",
    "GENESIS_NOTE",
    "GENESIS_PREV",
    "LIMIT_EVENT_FILE_BYTES",
    "LIMIT_NESTING_DEPTH",
    "LIMIT_REVIEW_FILE_COUNT",
    "LIMIT_ROLES_YML_BYTES",
    "PENDING_DIR",
    "PendingRequest",
    "RegistryExistsError",
    "REQHARNESS_DIR",
    "ROLES_NAME",
    "TIME_RE",
    "ReqHarnessLoader",
    "canonical_config",
    "check_int",
    "check_str",
    "check_time",
    "config_digest",
    "create_registry",
    "email_sha256",
    "load_config",
    "load_documents",
    "load_pending",
    "read_event_file",
    "validate_config",
    "validate_pending_document",
]
