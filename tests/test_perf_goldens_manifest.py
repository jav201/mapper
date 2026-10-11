"""PERFG0 (batch `2026-10-10-perf-batch`): the behaviour goldens stay byte-identical.

Every golden the batch pins was captured on the BASE product at base SHA
`5cde04e` before the lanes forked (PDR golden provenance protocol, the AT-065
precedent).  `tests/goldens/perf/MANIFEST.json` records, per golden, the case
id, the base SHA and the sha256 of its bytes; this module asserts the manifest
still names base `5cde04e` and that every listed file exists and hashes to its
recorded sha256.  Any later edit to a golden — or to the product code that
paints/dumps it, caught by the lane tests re-comparing against these bytes —
turns this RED.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

GOLDEN_DIR = Path(__file__).resolve().parent / "goldens" / "perf"
MANIFEST = GOLDEN_DIR / "MANIFEST.json"
BASE_SHA = "5cde04e"


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_manifest_names_base_sha_5cde04e():
    """Golden provenance: the manifest's base SHA is the pre-fork base."""
    assert _manifest()["base_sha"] == BASE_SHA


def test_every_golden_exists_and_matches_its_sha256():
    """0 diffs: each listed golden on disk still hashes to its recorded sha256."""
    failures: list[str] = []
    for entry in _manifest()["goldens"]:
        path = GOLDEN_DIR / entry["file"]
        if not path.is_file():
            failures.append(f"missing golden: {entry['file']}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != entry["sha256"]:
            failures.append(
                f"golden drifted: {entry['file']}: {digest} != {entry['sha256']}"
            )
        if entry.get("base_sha") != BASE_SHA:
            failures.append(f"wrong base_sha on entry: {entry['file']}")
    assert not failures, "\n".join(failures)
