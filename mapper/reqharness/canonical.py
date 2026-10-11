"""Canonical serialisation for hashing (ruling R3 / LLR-RH.1.3).

The canonical form is JSON with sorted keys, no whitespace, `ensure_ascii=False`,
computed AFTER NFC normalisation.  Digests are sha256 over that canonical JSON
of the `{field: normalised value}` object — NEVER a concatenation of values:
`{"a": "ab", "b": "c"}` and `{"a": "a", "b": "bc"}` hash differently because
the field names travel with the values (the `"ab"+"c" == "a"+"bc"` ambiguity of
concatenation cannot occur).
"""
from __future__ import annotations

import hashlib
import json
import unicodedata
from typing import Any


class NfcKeyCollision(ValueError):
    """Two mapping keys collapse to the same string under NFC normalisation.

    The dict would silently lose one entry, and two documents differing only
    in Unicode spelling would hash identically — canonicalisation refuses
    instead of collapsing (R3)."""


def nfc(value: Any) -> Any:
    """NFC-normalise every string in *value* (recursive); pass everything
    else through untouched.  Values are NFC-normalised before hashing (R3).

    A mapping whose keys are not unique AFTER normalisation raises
    NfcKeyCollision naming both keys — the silent collapse is an ambiguity
    the canonical digest must not hide."""
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, dict):
        result: dict[Any, Any] = {}
        original: dict[Any, Any] = {}
        for key, item in value.items():
            normalised = nfc(key)
            if normalised in result:
                raise NfcKeyCollision(
                    f"keys {original[normalised]!r} and {key!r} "
                    "collide after NFC normalisation"
                )
            original[normalised] = key
            result[normalised] = nfc(item)
        return result
    if isinstance(value, (list, tuple)):
        return [nfc(item) for item in value]
    return value


def canonical_json(value: Any) -> str:
    """The canonical serialisation: sorted keys, no whitespace,
    `ensure_ascii=False`, after NFC."""
    return json.dumps(
        nfc(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )


def canonical_digest(value: Any) -> str:
    """sha256 of the canonical JSON of *value* (hex digest)."""
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def chain_hash(prev_hash: str, event: dict[str, Any]) -> str:
    """The link recomputation every chain event is verified with (R2/R3):
    `sha256(prev_hash + "\n" + canonical_json(event_without_this_hash))`."""
    payload = prev_hash + "\n" + canonical_json(event)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
