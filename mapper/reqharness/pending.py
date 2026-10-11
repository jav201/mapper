"""Pending requests: one file per request under `reqharness/pending/`, with
the resolution DERIVED from the chain (HLR-RH.2 / ruling R6).

A held request is written by `chain.propose` (self-changes and non-admin
proposals — LLR-RH.2.2); this module owns the directory listing and the
derivation.  The request FILE's schema, confinement and R22 name/content
check live in `config.py` (the shared leaf — ARCH C3: `chain` imports the
one validator `load_pending` from there at module level, so the
chain<->pending import cycle is gone and no function-local import
remains); this module re-exports them unchanged.

The file stays on disk forever — deleting it would destroy the audit trail
of what was requested — and its resolved state is derived:

- an admin resolves it with ``a`` (approve — the change lands as the chain
  event that references the request's sha256) or ``r`` (reject — a
  ``resolution`` event referencing the sha256 with an empty change);
- `resolution()` replays the VERIFIED chain prefix and answers
  ``approved`` / ``rejected`` / ``pending`` — nothing is recorded anywhere
  but the chain, so the derivation survives restarts by construction.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from mapper.reqharness.config import (
    PENDING_DIR,
    PendingRequest,
    load_pending,
)
from mapper.reqharness.records import ValidationError
from mapper.reqharness.reviews import scan_event_dir

if TYPE_CHECKING:
    from mapper.reqharness.chain import ChainReport

RESOLVED_APPROVED = "approved"
RESOLVED_REJECTED = "rejected"
RESOLVED_PENDING = "pending"

_PENDING_ACTIONS = frozenset({"grant", "revoke"})


@dataclass(frozen=True)
class PendingScan:
    """One directory pass: the valid requests plus named reports."""

    requests: tuple[PendingRequest, ...]
    reported: tuple[str, ...]


def list_pending(repo: str | Path) -> PendingScan:
    """Every valid pending request plus named reports; the directory may be
    absent (no request has ever been held) — that is an empty registry, not
    an error."""
    names, reported = scan_event_dir(repo, PENDING_DIR)
    requests: list[PendingRequest] = []
    for name in names:
        try:
            requests.append(load_pending(repo, name))
        except ValidationError as exc:
            reported.append(str(exc))
    return PendingScan(requests=tuple(requests), reported=tuple(reported))


def resolution(report: ChainReport, request: PendingRequest) -> str:
    """The R6 derivation: replay the VERIFIED chain prefix for an event
    referencing this request's digest — a ``grant``/``revoke`` applying the
    held change is an approval, a ``resolution`` event (empty change) is a
    rejection, and no reference at all means the request is still pending.
    Unverified tail events can never resolve anything."""
    for event in report.events:
        if event.request_hash != request.digest:
            continue
        if (
            event.action in _PENDING_ACTIONS
            and event.person == request.person
            and event.role == request.role
        ):
            return RESOLVED_APPROVED
        if event.action == "resolution":
            return RESOLVED_REJECTED
    return RESOLVED_PENDING


__all__ = [
    "PENDING_DIR",
    "RESOLVED_APPROVED",
    "RESOLVED_PENDING",
    "RESOLVED_REJECTED",
    "PendingRequest",
    "PendingScan",
    "list_pending",
    "load_pending",
    "resolution",
]
