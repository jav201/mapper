"""The content-keyed review parse cache (ruling R4 / LLR-RH.5.3) with the
stat fast path (orchestrator ruling for the LLR-RH.5.4 budget miss).

The cache lives INSIDE ``.git/reqharness-cache/`` — local, never tracked, no
``.git/info/exclude`` write — and is keyed by sha256(file bytes): read + hash,
skip the parse.  It stores VALIDATED parses ONLY: the consumer runs the typed
schema and the R22 name/content check FIRST and hands the surviving document
to ``remember`` — a raw parse is never cached, so a file that fails
validation can never park a wrong-shaped or non-serialisable value in the
store, and ``save()`` cannot fail on what it holds (H2).

Because every entry passed validation before it was cached, a poisoned entry
can only arrive from outside the program (a direct write into ``.git/``); it
is bounded by the schema + name checks every hit is re-validated with — a
poisoned entry or a corrupt cache file degrades to a re-parse, NEVER a
verdict change — and deleting the cache changes no result (the suite asserts
equal outputs with and without).  Residuals, stated not hidden: an attacker
with local ``.git`` write access can plant entries (bounded to a re-parse by
the later checks), and the file NAME pins only sha8 while the cache key is
the full sha256 — a deliberate sha8 collision could alias two names (R22's
32-bit pin), though the content digests still differ.

THE STAT FAST PATH: review event files are immutable and content-named (the
sha8 in the name is recomputed at read), so a warm load does not need to
re-read the bytes of a file whose identity is unchanged.  ``fast(name,
stat)`` serves the validated parse for ``name`` when the entry's recorded
stat tuple ``(st_size, st_mtime_ns, st_ino, st_dev)`` — relative name plus
size, mtime in nanoseconds, file id and device — ALL match the live file,
WITHOUT reading it.  Any mismatch (or a missing stat field, or an entry that
was never fully checked) falls through to the full path: read, sha256, typed
schema, R22 name check, then ``remember`` refreshes the entry with the new
stat tuple.  On Windows ``st_ino`` is the NTFS file index (it changes when a
file is deleted and recreated); an in-place rewrite that preserves size,
mtime AND file id defeats the fast path — that writer can equally write
``.git/reqharness-cache`` itself (the same trust boundary as above), and
``--audit`` (cache OFF) re-reads every file by design, so release evaluation
via audit is unaffected.  A fast-path hit is still re-validated (schema +
name check over the cached document — CPU only, no I/O); a hit that fails is
dropped via ``bust_name`` and re-parsed from the bytes, exactly like a
poisoned sha-keyed entry.

Two states:

- ``ParseCache.open(repo)`` — the normal loader cache; active only when
  ``<repo>/.git`` exists (the cache's declared home); a registry outside a
  git work tree simply parses every time.
- ``ParseCache.disabled()`` — the audit state (R4): ``--audit`` runs with the
  cache OFF and writes nothing anywhere.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from mapper.reqharness.config import load_documents
from mapper.reqharness.records import ValidationError

CACHE_DIR = ".git/reqharness-cache"
CACHE_NAME = "reviews.json"

#: The cache file's OWN payload limit (L2) — deliberately separate from
#: ``LIMIT_ROLES_YML_BYTES``: the cache must persist at the 100 000-review
#: scale, where the aggregate of ~1000-byte validated parses is tens of MB.
LIMIT_CACHE_FILE_BYTES = 64 * 1024 * 1024

#: The persisted store's format marker: a flat dict of this shape is trusted,
#: anything else (a v1 flat {sha: doc} file, garbage) is bounded to a rebuild.
_STORE_VERSION = 2

#: The stat fields the fast path keys on (ruling): relative name plus size,
#: mtime in nanoseconds, file id and device.  A match on ALL of them reuses
#: the validated parse without reading the file.
_STAT_FIELDS = ("st_size", "st_mtime_ns", "st_ino", "st_dev")


def _stat_tuple(stat: os.stat_result) -> tuple[int, int, int, int] | None:
    """The fast-path key over one live stat: every field, or None if any is
    missing (a missing field always falls through to the full path)."""
    values = []
    for field in _STAT_FIELDS:
        value = getattr(stat, field, None)
        if value is None:
            return None
        values.append(value)
    return tuple(values)  # type: ignore[return-value]


class ParseCache:
    """A pure accelerator over YAML parsing, keyed by content hash, with a
    stat fast path over immutable event files.

    ``parse`` returns ``(document, key)`` and remembers NOTHING: the caller
    validates the document (typed schema + R22 name check) and calls
    ``remember(key, document, name=..., stat=...)`` only once it passes, so
    the store holds validated parses exclusively (H2).  A hit that fails
    re-validation is dropped with ``bust``/``bust_name`` and re-parsed from
    the bytes — the only way a poisoned on-disk entry is reached — so the
    cached state can never differ from a cache-free run.
    """

    def __init__(self, root: Path | None) -> None:
        self._root = root  # None = disabled (audit, or no .git present)
        self._store: dict[str, Any] = {}
        self._stat: dict[str, list[Any]] = {}  # rel name -> [stat tuple, sha]
        self._dirty = False
        if root is not None:
            path = root / CACHE_NAME
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                # A corrupt cache file (or a missing one) is bounded to a
                # rebuild — never an error, never a verdict change (R26).
                raw = {}
            if (
                isinstance(raw, dict)
                and raw.get("v") == _STORE_VERSION
                and isinstance(raw.get("docs"), dict)
                and isinstance(raw.get("stat"), dict)
            ):
                self._store = {
                    str(key): value for key, value in raw["docs"].items() if isinstance(key, str)
                }
                self._stat = {
                    str(key): value
                    for key, value in raw["stat"].items()
                    if isinstance(key, str) and isinstance(value, list) and len(value) == 2
                }

    # -- constructors ------------------------------------------------------

    @classmethod
    def open(cls, repo: str | Path) -> "ParseCache":
        """The loader cache for *repo*; disabled when ``<repo>/.git`` is
        not a directory (the cache has no declared home there)."""
        git = Path(repo) / ".git"
        return cls(Path(repo) / CACHE_DIR) if git.is_dir() else cls(None)

    @classmethod
    def disabled(cls) -> "ParseCache":
        """The audit state (R4): parse-only, remember nothing, save nothing."""
        return cls(None)

    # -- the operations ------------------------------------------------------

    def parse(self, text: str, *, where: str) -> tuple[Any, str]:
        """The single-document parse of *text*, keyed by sha256(bytes).

        Raises ValidationError naming *where* on malformed YAML or a document
        count other than one — the same refusal a cache-free parse gives.
        The result is NOT cached here: ``remember`` owns the store, so only a
        validated parse is ever cached (H2)."""
        key = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if self._root is not None and key in self._store:
            return self._store[key], key
        documents = load_documents(text, where=where)
        if len(documents) != 1:
            raise ValidationError(
                f"{where}: expected exactly 1 document, found {len(documents)}"
            )
        return documents[0], key

    def fast(self, name: str, stat: os.stat_result) -> Any | None:
        """The stat fast path: the validated parse for *name* when the live
        stat matches the entry's recorded tuple on EVERY field (name, size,
        mtime ns, file id, device) — WITHOUT reading the file.  Any mismatch
        or missing field returns None and the caller takes the full path."""
        if self._root is None:
            return None
        entry = self._stat.get(name)
        live = _stat_tuple(stat)
        if entry is None or live is None:
            return None
        recorded = entry[0]
        if (
            isinstance(recorded, list)
            and len(recorded) == len(_STAT_FIELDS)
            and all(value is not None for value in recorded)
            and tuple(recorded) == live
        ):
            return self._store.get(entry[1])
        return None

    def remember(
        self,
        key: str,
        document: Any,
        *,
        name: str | None = None,
        stat: os.stat_result | None = None,
    ) -> None:
        """Cache one VALIDATED parse — the ONLY store path (H2).  With *name*
        and *stat* given, the entry is recorded for the fast path (refreshed
        on every full check, so an mtime-only change re-binds the tuple)."""
        if self._root is not None:
            self._store[key] = document
            self._dirty = True
            if name is not None and stat is not None:
                live = _stat_tuple(stat)
                if live is not None:
                    self._stat[name] = [list(live), key]
                    self._dirty = True

    def bust(self, key: str) -> None:
        """Drop one entry — the consumer's re-validation refused it."""
        if self._root is not None and key in self._store:
            del self._store[key]
            for name in [n for n, entry in self._stat.items() if entry[1] == key]:
                del self._stat[name]
            self._dirty = True

    def bust_name(self, name: str) -> None:
        """Drop one fast-path entry AND the document it pointed to — a
        fast-path hit that failed re-validation (the document is bad for
        every name, so the sha-keyed entry goes with it)."""
        if self._root is None:
            return
        entry = self._stat.pop(name, None)
        if entry is not None and entry[1] in self._store:
            del self._store[entry[1]]
            self._dirty = True
        elif entry is not None:
            self._dirty = True

    def save(self, *, limit: int = LIMIT_CACHE_FILE_BYTES) -> None:
        """Persist the cache (call after a load pass); a no-op when nothing
        was learned, when disabled, when the payload exceeds *limit* (the
        cache file's own 64 MB budget, L2 — under it the cache persists at
        the 100 000-file scale), or when the write itself fails — the cache
        is an accelerator, never a source of truth."""
        if self._root is None or not self._dirty:
            return
        try:
            self._root.mkdir(parents=True, exist_ok=True)
            payload = json.dumps(
                {"v": _STORE_VERSION, "docs": self._store, "stat": self._stat},
                sort_keys=True,
                ensure_ascii=False,
            )
            if len(payload.encode("utf-8")) <= limit:
                (self._root / CACHE_NAME).write_text(
                    payload, encoding="utf-8", newline="\n"
                )
        except (OSError, TypeError, ValueError):
            pass  # bounded to "parse again next time"


__all__ = ["CACHE_DIR", "CACHE_NAME", "LIMIT_CACHE_FILE_BYTES", "ParseCache"]
