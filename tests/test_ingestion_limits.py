"""Q2 ingestion limits — bounded map-file loading, prescan, count caps, bounded CSV reads.

Authority: batch `2026-10-23-hygiene-batch` — HLR-Q2.1/Q2.2, LLR-Q2.1.1/.1.2/.1.3/Q2.2.1,
AT-109…AT-114, mutants M-Q2-1…M-Q2-5.  Lane L2a owns this file.

Sequencing note (PDR section B row 6, ruling R7): the `preview_csv`-level CSV arms
(`test_csv_*`, LLR-Q2.2.1) and the running-screen arm (`test_at_114_*`) are authored in L2a
but are EXPECTED RED until L2b lands `import_csv`'s cap + the home-screen toast wording.
Declared in increment-003 section 5; green only after BOTH increments land.
"""
from __future__ import annotations

import os
import subprocess
import time
import types

import pytest

from mapper.app import MapperApp, _PromptScreen
from mapper.diff import git_diff
from mapper.import_csv import preview_csv
from mapper.model import Edge, Graph, Node
from mapper.osopen import (
    BINARY_PROBE_BYTES,
    MAX_EDGES,
    MAX_FILE_BYTES,
    MAX_MAP_BYTES,
    MAX_NODES,
    ContentReadError,
)
from mapper.store import MapStore, MapStoreError, _check_count_caps

MMD = "graph TD\n    a[raiz]\n"


def _write_map(ws, map_id="m", mmd_text=MMD, yml_text="{}"):
    (ws / f"{map_id}.mmd").write_text(mmd_text, encoding="utf-8")
    (ws / f"{map_id}_nodos.yml").write_text(yml_text, encoding="utf-8")


def _nested_flow(n: int) -> str:
    """A flow-mapping nested *n* mappings deep with a scalar leaf: `{k: {k: ... 0}}`
    (plus the sidecar's own top-level mapping, total collection depth is n + 1)."""
    text = "0"
    for _ in range(n):
        text = "{k: " + text + "}"
    return text


# ---------------------------------------------------------------------------
# AT-109 / LLR-Q2.1.1 — byte caps on map files (stat path, TOCTOU path, cap-1 loads)
# ---------------------------------------------------------------------------


def _oversize_mmd() -> bytes:
    """A map file past the byte cap, built from COMMENT lines (parse skips them) so
    that even a mutant which lets it through the reader cannot hang the mermaid regex."""
    line = b"%% " + b"g" * 77 + b"\n"
    return b"graph TD\n    a[raiz]\n" + line * (MAX_MAP_BYTES // 78 + 2)


def test_at_109_byte_cap_stat_refuses_and_names_limit_and_map(tmp_path):
    (tmp_path / "m.mmd").write_bytes(_oversize_mmd())
    (tmp_path / "m_nodos.yml").write_bytes(b"{}")
    with pytest.raises(MapStoreError) as caught:
        MapStore(tmp_path).load("m")
    msg = str(caught.value)
    assert str(MAX_MAP_BYTES) in msg, msg
    assert "m" in msg, msg
    assert str(tmp_path) not in msg, msg


def test_at_109_byte_cap_grow_between_stat_and_read_refuses(tmp_path, monkeypatch):
    """TOCTOU: the stat reports a small file, the capped re-read reports the truth."""
    (tmp_path / "m.mmd").write_bytes(_oversize_mmd())
    (tmp_path / "m_nodos.yml").write_bytes(b"{}")
    real_stat = os.stat

    def fake_stat(p, *args, **kwargs):
        if str(p).endswith("m.mmd"):
            return types.SimpleNamespace(st_size=1)
        return real_stat(p, *args, **kwargs)

    monkeypatch.setattr(os, "stat", fake_stat)
    with pytest.raises(MapStoreError) as caught:
        MapStore(tmp_path).load("m")
    assert str(MAX_MAP_BYTES) in str(caught.value), str(caught.value)


def test_at_109_text_map_at_byte_cap_minus_1_loads(tmp_path):
    yml = b"# " + b"a" * (MAX_MAP_BYTES - 4) + b"\n"
    assert len(yml) == MAX_MAP_BYTES - 1
    (tmp_path / "m.mmd").write_bytes(b"graph TD\n    a[raiz]\n")
    (tmp_path / "m_nodos.yml").write_bytes(yml)
    graph = MapStore(tmp_path).load("m")
    assert "a" in graph.nodes


# ---------------------------------------------------------------------------
# AT-110/111 / LLR-Q2.1.2 — prescan: anchors, aliases, depth (M-Q2-1)
# ---------------------------------------------------------------------------


def test_at_111_anchor_refused_names_anchor_and_map(tmp_path):
    _write_map(tmp_path, yml_text="top: &x 1\nother: *x\n")
    with pytest.raises(MapStoreError) as caught:
        MapStore(tmp_path).load("m")
    msg = str(caught.value)
    assert "'x'" in msg, msg
    assert "m" in msg, msg
    assert str(tmp_path) not in msg, msg


def test_at_111_alias_refused(tmp_path):
    _write_map(tmp_path, yml_text="top: &x [1, 2]\nother: *x\n")
    with pytest.raises(MapStoreError) as caught:
        MapStore(tmp_path).load("m")
    assert "'x'" in str(caught.value), str(caught.value)


def test_at_111_anchor_name_in_refusal_is_bounded(tmp_path):
    """inc003-F1 (independent review, MAJOR): the anchor NAME is
    attacker-controlled sidecar content; the refusal must name it TRUNCATED
    (40 chars + an ellipsis — LLR-N13.1.7: a coordinate that carries a value
    behaves like a value) so a hostile sidecar cannot push an unbounded string
    into the operator-facing sink.  A 5,000-char anchor names its 40-char
    prefix and nothing more.  Mutant: revert the truncation in
    `mapper.yamlscan.prescan` → this arm RED."""
    name = "a" * 5000
    _write_map(tmp_path, yml_text=f"top: &{name} 1\n")
    with pytest.raises(MapStoreError) as caught:
        MapStore(tmp_path).load("m")
    msg = str(caught.value)
    assert name[:40] in msg, msg
    assert "…" in msg, msg
    assert name[100:] not in msg, msg
    assert len(msg) <= 160, len(msg)
    assert str(tmp_path) not in msg, msg


def test_at_110_depth_64_parses(tmp_path):
    """Total collection depth 64 (top-level mapping + 63 nested) is the last accepted level."""
    _write_map(tmp_path, yml_text="nest: " + _nested_flow(63) + "\n")
    graph = MapStore(tmp_path).load("m")
    assert "a" in graph.nodes


def test_at_110_depth_65_refuses_naming_depth_limit(tmp_path):
    _write_map(tmp_path, yml_text="nest: " + _nested_flow(64) + "\n")
    with pytest.raises(MapStoreError) as caught:
        MapStore(tmp_path).load("m")
    msg = str(caught.value)
    assert "depth limit" in msg, msg
    assert "m" in msg, msg
    assert str(tmp_path) not in msg, msg


def test_at_110_deep_10000_refuses_fast_without_recursion_error(tmp_path):
    """A 10,000-deep nesting bomb is a typed refusal in under 5 s — never RecursionError."""
    _write_map(tmp_path, yml_text="nest: " + _nested_flow(10000) + "\n")
    started = time.perf_counter()
    with pytest.raises(MapStoreError) as caught:
        MapStore(tmp_path).load("m")
    elapsed = time.perf_counter() - started
    assert "depth limit" in str(caught.value), str(caught.value)
    assert elapsed < 5.0, elapsed


# ---------------------------------------------------------------------------
# AT-112/113 / LLR-Q2.1.3 — node and edge count caps (M-Q2-4; ruling R1, ledger .1/.5)
# ---------------------------------------------------------------------------


def test_at_112_node_count_cap_plus_1_refuses(tmp_path):
    """100,001 nodes refuse: the sidecar carries 100,000 ids the `.mmd` never defined
    (ghost nodes are still added, per B-29/AT-049) plus the one parsed node."""
    yml = "nodes:\n" + "".join(f"  n{i:06d}: {{}}\n" for i in range(MAX_NODES))
    (tmp_path / "m.mmd").write_text(MMD, encoding="utf-8")
    (tmp_path / "m_nodos.yml").write_text(yml, encoding="utf-8")
    with pytest.raises(MapStoreError) as caught:
        MapStore(tmp_path).load("m")
    msg = str(caught.value)
    assert "nodes" in msg, msg
    assert str(MAX_NODES) in msg, msg
    assert str(tmp_path) not in msg, msg


def test_at_113_edge_count_cap_plus_1_refuses():
    """100,001 edges refuse.  A synthetic graph: `mermaid.parse` only builds trees
    (a child may not repeat a parent), so through `load` edges <= nodes - 1 and the
    edges cap is structurally unreachable there — the check itself is the surface."""
    graph = Graph()
    graph.add_node(Node(id="a"))
    graph.add_node(Node(id="b"))
    for _ in range(MAX_EDGES + 1):
        graph.add_edge(Edge(parent_id="a", child_id="b"))
    with pytest.raises(MapStoreError) as caught:
        _check_count_caps("m", graph)
    msg = str(caught.value)
    assert "edges" in msg, msg
    assert str(MAX_EDGES) in msg, msg


def test_count_caps_exactly_at_cap_pass():
    """Boundary: exactly 100,000 nodes / 100,000 edges is the last accepted level."""
    nodes_graph = Graph()
    for i in range(MAX_NODES):
        nodes_graph.add_node(Node(id=f"n{i:06d}"))
    _check_count_caps("m", nodes_graph)
    edges_graph = Graph()
    edges_graph.add_node(Node(id="a"))
    edges_graph.add_node(Node(id="b"))
    for _ in range(MAX_EDGES):
        edges_graph.add_edge(Edge(parent_id="a", child_id="b"))
    _check_count_caps("m", edges_graph)


# ---------------------------------------------------------------------------
# Diff side — the shared caps through the existing diff -> store edge (ruling R8);
# the None-on-error contract survives a capped-out diff-side load.
# ---------------------------------------------------------------------------


def _git(ws, *args):
    subprocess.run(["git", *args], cwd=ws, check=True, capture_output=True)


def _repo_with_head(tmp_path, mmd_bytes: bytes, yml_text: str):
    ws = tmp_path / "repo"
    ws.mkdir()
    _git(ws, "init", "-q")
    _git(ws, "config", "user.email", "q2@lane.invalid")
    _git(ws, "config", "user.name", "lane")
    (ws / "m.mmd").write_bytes(mmd_bytes)
    (ws / "m_nodos.yml").write_text(yml_text, encoding="utf-8")
    _git(ws, "add", ".")
    _git(ws, "commit", "-q", "-m", "base")
    return ws


def test_diff_side_clean_head_still_diffs(tmp_path):
    """Positive control: the diff arms' None comes from the cap, not from a broken setup."""
    ws = _repo_with_head(tmp_path, MMD.encode("utf-8"), "{}")
    assert git_diff("m", MapStore(ws)) is not None


def test_diff_side_anchor_head_yields_none(tmp_path):
    ws = _repo_with_head(tmp_path, MMD.encode("utf-8"), "top: &x 1\nother: *x\n")
    (ws / "m_nodos.yml").write_text("{}", encoding="utf-8")
    assert git_diff("m", MapStore(ws)) is None


def test_diff_side_oversize_head_yields_none(tmp_path):
    """S1 (acceptance bound, revised at the L2b gate — increment-004 section 5): a
    HEAD map file past the byte cap degrades to None — the store refuses the
    oversized captured text before any parse."""
    big = _oversize_mmd()
    ws = _repo_with_head(tmp_path, big, "{}")
    (ws / "m.mmd").write_bytes(MMD.encode("utf-8"))
    assert git_diff("m", MapStore(ws)) is None


# ---------------------------------------------------------------------------
# LLR-Q2.2.1 — bounded CSV content reads (authored L2a, green at L2b).
# (Review inc003-F2: relabelled from "AT-113" — AT-113 is the EDGES arm,
# realized above as `test_at_113_edge_count_cap_plus_1_refuses`; the CSV read
# arms trace to LLR-Q2.2.1, the toast arm below to AT-114.)
# Typed refusals are osopen.ContentReadError: import_csv -> store stays forbidden
# (R-015), so the reader's own typed error is the refusal family here (declared in
# increment-003/-004 section 6).
# ---------------------------------------------------------------------------


def test_csv_at_file_cap_plus_1_refuses(tmp_path):
    csv_path = tmp_path / "big.csv"
    csv_path.write_bytes(b"id,title\nA," + b"x" * MAX_FILE_BYTES)
    with pytest.raises(ContentReadError) as caught:
        preview_csv(csv_path)
    assert str(MAX_FILE_BYTES) in str(caught.value), str(caught.value)


def test_csv_at_file_cap_minus_1_loads(tmp_path):
    csv_path = tmp_path / "edge.csv"
    # cap-1 bytes as ~323k DISTINCT rows: a single field over 128 KiB would hit
    # the csv module's own field-size limit first — a pre-existing, unrelated bound.
    header = b"id,title\n"
    m = (MAX_FILE_BYTES - 1 - len(header)) // 13 - 1
    rem = MAX_FILE_BYTES - 1 - len(header) - 13 * m
    rows = b"".join(b"r%06d,xxxx\n" % i for i in range(m))
    tail = b"z" * (rem - 3) + b",y\n"
    payload = header + rows + tail
    assert len(payload) == MAX_FILE_BYTES - 1
    csv_path.write_bytes(payload)
    graph = preview_csv(csv_path)
    assert "r000000" in graph.nodes and "zzzzzzzzzz" in graph.nodes
    assert graph.csv_collisions == []


def test_csv_nul_at_byte_0_refuses_as_binary(tmp_path):
    csv_path = tmp_path / "nul0.csv"
    csv_path.write_bytes(b"\x00id,title\nA,uno\n")
    with pytest.raises(ContentReadError) as caught:
        preview_csv(csv_path)
    assert "binary" in str(caught.value), str(caught.value)


def test_csv_nul_at_last_probe_byte_refuses_as_binary(tmp_path):
    """A NUL at byte 8,191 — the last byte inside the probe window."""
    csv_path = tmp_path / "nul8191.csv"
    payload = b"id,title\n" + b"x" * (BINARY_PROBE_BYTES - 1 - len(b"id,title\n")) + b"\x00"
    assert len(payload) == BINARY_PROBE_BYTES
    assert payload[BINARY_PROBE_BYTES - 1] == 0
    csv_path.write_bytes(payload)
    with pytest.raises(ContentReadError) as caught:
        preview_csv(csv_path)
    assert "binary" in str(caught.value), str(caught.value)


def test_csv_nul_past_probe_window_is_not_refused_by_the_probe(tmp_path):
    """The documented probe bound (LLR-Q2.2.1): a NUL past the first 8 KiB is outside
    the probe — the file is a text CSV and imports."""
    csv_path = tmp_path / "late.csv"
    csv_path.write_bytes(b"id,title\na," + b"x" * 9000 + b"\x00")
    graph = preview_csv(csv_path)
    assert "a" in graph.nodes


def test_csv_non_utf8_refuses_typed_naming_the_reason(tmp_path):
    """inc004-F2 (independent review, MINOR): bytes that pass the NUL probe but
    are not UTF-8 used to escape `read_capped` as a bare `UnicodeDecodeError`,
    so the operator saw only the exception TYPE name (the home screen's generic
    toast branch).  The reader now refuses it TYPED — an authored, path-free
    message naming the reason — so the reason reaches the operator (AT-114).
    Mutant: remove the `except UnicodeDecodeError` limb in
    `mapper/osopen.py`'s `read_capped` → this arm RED."""
    csv_path = tmp_path / "latin1.csv"
    csv_path.write_bytes("id,title\nA,niño\n".encode("latin-1"))
    with pytest.raises(ContentReadError) as caught:
        preview_csv(csv_path)
    msg = str(caught.value)
    assert "UTF-8" in msg, msg
    assert str(tmp_path) not in msg, msg


# ---------------------------------------------------------------------------
# AT-114 — the CSV refusal toast through the RUNNING home screen (ruling R7, m5).
# Authored L2a, EXPECTED RED until L2b lands the toast wording (PDR section B row 6).
# ---------------------------------------------------------------------------


async def test_at_114_csv_refusal_toast_shows_the_reason(tmp_path):
    csv_path = tmp_path / "bom.csv"
    csv_path.write_bytes(b"id,title\nA,un\x00o\n")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        toasts: list[str] = []
        real_notify = app.notify

        def notify(message, **kw):
            toasts.append(str(message))
            return real_notify(message, **kw)

        app.notify = notify
        await pilot.press("i")
        await pilot.pause()
        assert isinstance(app.screen, _PromptScreen), app.screen
        await pilot.press(*str(csv_path))
        await pilot.press("enter")
        for _ in range(6):
            await pilot.pause()
    refusal = [t for t in toasts if "could not read CSV" in t]
    assert refusal, toasts
    assert "NUL" in refusal[0], refusal
    assert "bom.csv" in refusal[0], refusal
    assert str(tmp_path) not in refusal[0], refusal
