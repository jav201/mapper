"""LLR-RH.5.4 — the parse-cache STAT FAST PATH (orchestrator ruling, perf-rh
unit): a warm load of immutable, content-named review events reuses the
validated parse when (relative name, st_size, st_mtime_ns, st_ino, st_dev)
ALL match the cached entry, WITHOUT reading the file bytes; any mismatch or
missing stat field falls through to the full path (read, sha256, typed
schema, R22 name check); `--audit` stays cache-OFF and re-reads everything.

Residual, stated and tested: an in-place rewrite that preserves size, mtime
AND file id defeats the fast path (on Windows `st_ino` is the NTFS file
index, unchanged by an in-place rewrite) — that writer can equally write
`.git/reqharness-cache` itself (the same trust boundary as R4), and the
cache-OFF audit load catches the change by re-reading every file.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from mapper.reqharness import reviews
from mapper.reqharness.cache import ParseCache
from tests.test_reqharness_registry import (
    HLR_FIELDS,
    _add_ana,
    _grant_reviewer,
    _record_review,
    _seed,
)


def _seeded_review(tmp_path) -> Path:
    """A small registry with one valid human review; returns the event file."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    _grant_reviewer(tmp_path)
    (tmp_path / ".git").mkdir()
    return _record_review(tmp_path, "HLR-TEST.1", HLR_FIELDS)


def _cold_load(tmp_path):
    """One cache-building load pass, persisted."""
    cache = ParseCache.open(tmp_path)
    scan = reviews.load_reviews(tmp_path, cache=cache)
    cache.save()
    return scan


def _forbid_reads(monkeypatch):
    """The read/open path fails if called — proves no file bytes are read."""
    def no_read(repo, name):
        raise AssertionError(f"read_event_file called for unchanged file {name}")

    monkeypatch.setattr(reviews, "read_event_file", no_read)


def _count_reads(monkeypatch) -> list:
    """The read path is wrapped with a counter — proves the full path ran."""
    reads: list = []
    real = reviews.read_event_file

    def counting(repo, name):
        reads.append(name)
        return real(repo, name)

    monkeypatch.setattr(reviews, "read_event_file", counting)
    return reads


def _same_size_variant(text: str) -> str:
    """Same-length bytes with a different note char (recomputes sha8, R22)."""
    marker = "fixture review"
    index = text.index(marker)
    return text[:index] + "X" + text[index + 1 :]


def test_warm_load_skips_unchanged_file_bytes(tmp_path, monkeypatch):
    """(1) The fast path: a warm load of an unchanged event serves the
    validated parse from the persisted stat index — the file's bytes are
    never read (the read path is monkeypatched to fail)."""
    victim = _seeded_review(tmp_path)
    cold = _cold_load(tmp_path)
    assert [event.name for event in cold.events] == [victim.name]
    assert cold.reported == ()

    store = json.loads(
        (tmp_path / ".git" / "reqharness-cache" / "reviews.json").read_text(
            encoding="utf-8"
        )
    )
    assert f"reviews/{victim.name}" in store["stat"]  # the entry records stat

    _forbid_reads(monkeypatch)
    warm = reviews.load_reviews(tmp_path, cache=ParseCache.open(tmp_path))
    assert warm.events == cold.events
    assert warm.reported == cold.reported


def test_same_size_same_mtime_new_file_id_takes_full_path(tmp_path, monkeypatch):
    """(2) A byte change with the SAME size and a forced-equal mtime but a
    DIFFERENT file id (delete + recreate via os.replace — on Windows
    `st_ino` is the NTFS file index and it changes) is CAUGHT: the stat
    tuple mismatches, the full path reads and re-hashes the file, and the
    R22 name/content mismatch is reported by name, non-closing."""
    victim = _seeded_review(tmp_path)
    cold = _cold_load(tmp_path)
    old = os.stat(victim, follow_symlinks=False)

    text = victim.read_text(encoding="utf-8")
    variant = victim.with_suffix(".tmp")
    variant.write_text(
        _same_size_variant(text), encoding="utf-8", newline="\n"
    )
    os.replace(variant, victim)
    os.utime(victim, ns=(old.st_atime_ns, old.st_mtime_ns))
    new = os.stat(victim, follow_symlinks=False)
    assert (new.st_size, new.st_mtime_ns) == (old.st_size, old.st_mtime_ns)
    assert new.st_ino != old.st_ino  # Windows st_ino: the NTFS file index

    reads = _count_reads(monkeypatch)
    warm = reviews.load_reviews(tmp_path, cache=ParseCache.open(tmp_path))
    assert reads == [f"reviews/{victim.name}"]  # the full path ran
    assert warm.events == ()  # the rewritten event derives no state
    assert any(
        victim.name in line and "name/content mismatch" in line
        for line in warm.reported
    ), warm.reported
    assert cold.events  # sanity: the original was valid


def test_changed_size_or_mtime_takes_full_path(tmp_path, monkeypatch):
    """(3) A changed size OR a changed mtime alone re-binds the entry: the
    full path runs (the file is read); a size change that breaks the content
    digest is reported by name, an mtime-only change re-validates and
    refreshes the stat tuple (the next warm load reads nothing again)."""
    victim = _seeded_review(tmp_path)
    _cold_load(tmp_path)

    # (a) size change: one extra content byte -> full read, mismatch reported
    text = victim.read_text(encoding="utf-8")
    victim.write_text(
        text.replace("fixture review", "fixture reviews", 1),
        encoding="utf-8",
        newline="\n",
    )
    reads = _count_reads(monkeypatch)
    scan = reviews.load_reviews(tmp_path, cache=ParseCache.open(tmp_path))
    assert reads == [f"reviews/{victim.name}"]
    assert scan.events == ()
    assert any(
        victim.name in line and "name/content mismatch" in line
        for line in scan.reported
    ), scan.reported

    # restore the original bytes (content == old, but mtime moved on)
    victim.write_text(text, encoding="utf-8", newline="\n")
    cache = ParseCache.open(tmp_path)
    scan = reviews.load_reviews(tmp_path, cache=cache)
    cache.save()
    assert [event.name for event in scan.events] == [victim.name]

    # (b) mtime-only change: same bytes, fresh mtime -> full path, still valid
    reads = _count_reads(monkeypatch)
    os.utime(victim)  # touch: mtime differs from the recorded tuple
    cache = ParseCache.open(tmp_path)
    scan = reviews.load_reviews(tmp_path, cache=cache)
    cache.save()  # the caller persists the refreshed stat tuple
    assert reads == [f"reviews/{victim.name}"]  # re-read despite equal bytes
    assert [event.name for event in scan.events] == [victim.name]

    # the touched tuple is re-recorded: the next warm load skips the read
    _forbid_reads(monkeypatch)
    warm = reviews.load_reviews(tmp_path, cache=ParseCache.open(tmp_path))
    assert warm.events == scan.events


def test_same_size_same_mtime_same_inode_rewrite_is_the_residual(
    tmp_path, monkeypatch
):
    """The residual, stated and pinned: an IN-PLACE rewrite (same file
    object — size, mtime AND the NTFS file index all preserved) is invisible
    to the fast path, which serves the validated parse without reading; the
    cache-OFF audit load re-reads every file and catches the mismatch."""
    victim = _seeded_review(tmp_path)
    _cold_load(tmp_path)
    old = os.stat(victim, follow_symlinks=False)

    data = bytearray(victim.read_bytes())
    marker = b"fixture review"
    index = bytes(data).index(marker)
    data[index] = ord(b"X")  # same length, different bytes, in place
    with open(victim, "r+b") as handle:
        handle.write(bytes(data))
    os.utime(victim, ns=(old.st_atime_ns, old.st_mtime_ns))
    new = os.stat(victim, follow_symlinks=False)
    assert (new.st_size, new.st_mtime_ns, new.st_ino) == (
        old.st_size,
        old.st_mtime_ns,
        old.st_ino,
    )

    # the fast path cannot see this — no read happens (the residual)
    with monkeypatch.context() as scoped:
        _forbid_reads(scoped)
        warm = reviews.load_reviews(tmp_path, cache=ParseCache.open(tmp_path))
    assert [event.name for event in warm.events] == [victim.name]

    # --audit (cache OFF) re-reads everything: the change IS caught there
    audit = reviews.load_reviews(tmp_path, cache=None)
    assert audit.events == ()
    assert any(
        victim.name in line and "name/content mismatch" in line
        for line in audit.reported
    ), audit.reported


def test_fast_path_results_identical_with_cache_deleted(tmp_path):
    """(4) Deleting the cache changes no result: cold, warm (fast path),
    cache-deleted rebuild and re-warm scans are all identical."""
    _seeded_review(tmp_path)
    cold = _cold_load(tmp_path)
    warm = reviews.load_reviews(tmp_path, cache=ParseCache.open(tmp_path))
    assert warm == cold

    cache_file = tmp_path / ".git" / "reqharness-cache" / "reviews.json"
    cache_file.unlink()
    rebuilt = _cold_load(tmp_path)  # the full path re-learns every entry
    assert rebuilt == cold
    rewarm = reviews.load_reviews(tmp_path, cache=ParseCache.open(tmp_path))
    assert rewarm == cold
