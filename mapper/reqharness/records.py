"""ReqHarness value objects and error types (HLR-RH.1).

Plain frozen dataclasses with `str` fields (all `str` except the `seq` /
`roles_seq` ints the chain carries) and the module's error ladder.  The core
is headless (docs/ARCHITECTURE.md §3): nothing here imports Textual, Rich or
any other mapper module.
"""
from __future__ import annotations

from dataclasses import dataclass


class ReqHarnessError(Exception):
    """Base for every error the ReqHarness core raises."""


class ValidationError(ReqHarnessError, ValueError):
    """A file under `reqharness/` failed the typed schema or cannot be parsed.

    Carries the file name and the offending field/value — every refusal is
    reported BY NAME, never silently skipped (R9).
    """


class YamlRefusal(ValidationError):
    """A YAML document was refused at parse time: anchors/aliases (R21), a
    duplicate key, or syntax the loader cannot compose."""


class SigningRefused(ValidationError):
    """A signing pre-flight or write was refused, carrying a STABLE reason
    code (one of the reason-code literals below) plus the interpolation
    fields the screen uses to paint the named refusal (LLR-RS.2.1).

    A refusal writes nothing; the reason code is the stable identifier the
    screen maps to its §6.6 string, never a free-text prose guess."""

    def __init__(self, reason: str, message: str = "", **fields: object) -> None:
        self.reason = reason
        self.fields = fields
        super().__init__(message or reason)


class ReviewLimitError(ValidationError):
    """The review-file count limit was reached (too many files under an event
    directory) — a named, typed refusal the signer maps to `review_limit`."""


class AlreadySignedError(ValidationError):
    """A review event under the same content-named path already exists — the
    exclusive-create (R8) collision the signer maps to `already_signed`."""


#: The stable reason-code literals this batch carries.  RS1a owns the four
#: `unentitled` causes `derive` assigns; RS1b adds the signing refusal codes.
REASON_NO_ROLE = "no_role"
REASON_AUTHOR = "author"
REASON_OWNING_BATCH_MISMATCH = "owning_batch_mismatch"
REASON_OWNING_BATCH_MISSING = "owning_batch_missing"


@dataclass(frozen=True)
class Person:
    """A registry member.  The email is stored ONLY as `email_sha256`
    (sha256 of the lowercased address — R12); the display name stays in clear."""

    id: str
    name: str
    email_sha256: str


@dataclass(frozen=True)
class ReqClass:
    """A requirement class (e.g. `HLR`/`LLR`): its reviewer role and the
    normative/informative field sets.  The two sets are disjoint (R5)."""

    id: str
    reviewer_role: str
    normative_fields: tuple[str, ...]
    informative_fields: tuple[str, ...]


@dataclass(frozen=True)
class ReleaseRule:
    """A config-declared release rule id.  The three mandatory rules (chain
    verified, policy verified, closing reviews signed by a role in force at the
    bound head) are hard-coded in the core; config may ADD, never remove (R1)."""

    id: str


@dataclass(frozen=True)
class ChainEvent:
    """One document of the `roles.yml` stream — the hash-chained role log.

    Every field is a quoted `str` except `seq`/`roles_seq: int` and the
    reader-side `index` (the document's position in the file); `config_hash`,
    `request_hash` and `resolve_excludes` appear only on the events that need
    them (R15/R6/R16)."""

    index: int
    seq: int
    time: str
    requested_by: str
    approved_by: str
    action: str
    person: str
    role: str
    note: str
    roles_seq: int
    roles_hash: str
    prev_hash: str
    this_hash: str
    config_hash: str | None = None
    request_hash: str | None = None
    resolve_excludes: str | None = None


@dataclass(frozen=True)
class Config:
    """The validated, NFC-normalised live configuration (LLR-RH.1.1/1.3).

    `authors` is the optional admin-approved authorship map (HLR-RS.5):
    owning-batch id -> declared person ids, in config order.  Absent or
    empty `authors` is omitted from `canonical_config`, so a config that
    never declared authorship keeps today's `config_hash` (A2)."""

    version: str
    people: tuple[Person, ...]
    roles: tuple[str, ...]
    classes: tuple[ReqClass, ...]
    release_rules: tuple[ReleaseRule, ...]
    authors: tuple[tuple[str, tuple[str, ...]], ...] = ()
