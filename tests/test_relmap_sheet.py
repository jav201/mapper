"""The node-sheet renderer — lane L5, increment 005 (batch
`2026-10-25-relmap-r2-batch`).

Sheet arms only: the host owes its chrome at trunk Inc-2 (`tests/test_relmap_shell.py`).
This file pins what the SHEET owes over the frozen D1 surface
(`mapper/screens/relmap/base.py`): the two-row header over `RelMap.node` with
the Darkside kind chip and NO source segment (LLR-RVS.1.1, AT-140), Darkside
casing on canon-derived labels (LLR-RVS.1.2), the `feeds it` / `a change
reaches` section oracles on an asymmetric fixture with the frozen D5
evidence-glyph column (LLR-RVS.2.1-.2.3), honest declared empties
(LLR-RVS.2.4), the declared hop-2 cuts counted per direction (LLR-RVS.3.1,
TC-RM-17), the stacked full chain with per-direction minimum-hop markers on a
diamond fixture (LLR-RVS.3.2), the `c` density toggle flipping rows, note and
crumb word together (LLR-RVS.3.3, AT-141, COND-QA-5), the focused node's own
gaps consumed as given (LLR-RVS.4.1, AT-142), the one-sink markup safety
(LLR-RVS.5.1, AT-144), width discipline with the C10 audit hook armed
(LLR-RVS.6.1, AT-143), the counted overflow line (LLR-RVS.6.2) and the
read-only evidence-label census (LLR-RVS.7.1).

Synthetic maps are built INLINE through `build_map` (ARC-05 — the lane fixture
policy; `tests/_relmap_fixtures.py` is trunk-only and is never touched here).
The pilot arms drive REAL keys through `run_test()` (C-16) on a non-git
fixture workspace (the AT-driver seam, F-5).
"""
from __future__ import annotations

import ast
import inspect

import pytest
from rich.text import Text

from mapper import darkside
from mapper.app import MapperApp
from mapper.relmap.adapter import derive_reqharness_map
from mapper.relmap.descriptor import default_descriptor
from mapper.relmap.gaps import Gap, detect_gaps, rank_gaps
from mapper.relmap.model import Edge, Node, build_map
from mapper.relmap.profile import REQHARNESS, EdgeType, GapRow, Profile
from mapper.screens.relmap import base
from mapper.screens.relmap import sheet as sheet_mod
from mapper.screens.relmap import RelMapScreen
from textual.widgets import Static

# ---------------------------------------------------------------------------
# The frozen copy the ATs assert (hand-written — the oracle is not imported
# from the implementation under test)
# ---------------------------------------------------------------------------

FEEDS_BAND = "feeds it — what a change to them does to this node"
REACHES_BAND = "a change reaches — what changing this node forces"
GAPS_BAND = "gaps on this node"
EMPTY_LINE = "╌╌ none on record"
NO_NODES_LINE = "╌╌ no nodes on record"
DIRECT_NOTE = "next ▸ direct feeders only — the chain is one key away, and the cut is declared"
STACKED_NOTE = "next ▸ feeds it and a change reaches come free from the engine (§3.4 C12)"
CUT_UP = "╌╌ +{n:02d} more upstream at hop 2 — c shows the chain"
CUT_DOWN = "╌╌ +{n:02d} more downstream at hop 2 — c shows the chain"
MORE = "… +{n:02d} more"

WORD_DIRECT = "direct only"
WORD_STACKED = "stacked chain"

#: The CAPS profile: the same reqharness shape with catalogue-stored ALL-CAPS
#: type and gap-kind names, so Darkside casing (LLR-RVS.1.2) is exercised
#: against a disagreeing producer, not a coincidentally-lowercase one.
CAPS = Profile(
    name="caps",
    node_kinds=("US", "HLR", "LLR", "AT", "TC"),
    edge_types=(
        EdgeType("REFINES", (("US", "HLR"), ("HLR", "LLR")), True, "none"),
        EdgeType("COVERS", (("AT", "US"),), False, "optional"),
        EdgeType("VERIFIES", (("TC", "LLR"), ("TC", "HLR")), False, "required"),
        EdgeType("BINDS", (("AT", "TC"),), False, "graduated"),
    ),
    gaps=(
        GapRow("HLR WITHOUT LLR", "MED", "lacks_out", "HLR", "REFINES", "LLR",
               True, False, ("HLR", "LLR"), "<id> has no LLR under it: <title>"),
    ),
)


def make_map(profile, nodes, edges):
    return build_map(profile, tuple(nodes), tuple(edges),
                     sourced=profile.node_kinds)


def view_state(m, focus, gaps=(), w=118, h=34, notice=None):
    return base.ViewState(m, notice, focus, 0, tuple(gaps), w, h)


def build(m, focus, **kw):
    """The landed sheet view + a state — the unit-arm entry."""
    return sheet_mod.build_view(), view_state(m, focus, **kw)


def plains(view, st):
    return [r.plain for r in view.paint(st)]


def fitted(rows, w):
    return [darkside.fit(row, w) for row in rows]


def style_at(row: Text, index: int) -> str:
    for span in row.spans:
        if span.start <= index < span.end:
            return span.style or ""
    return ""


def _section(rows, band):
    """The content rows under *band*, up to the next band or the note line.
    Band rows are located by content (the viewport width is the renderer's
    own — never restated here)."""
    marker = f" {band} "
    i = next(idx for idx, r in enumerate(rows) if r.startswith(marker))
    bands = tuple(f" {b} " for b in (FEEDS_BAND, REACHES_BAND, GAPS_BAND))
    out = []
    for r in rows[i + 1:]:
        if r.startswith(bands) or r.startswith("next ▸"):
            break
        out.append(r)
    return out


# ---------------------------------------------------------------------------
# Inline synthetic fixtures (ARC-05)
# ---------------------------------------------------------------------------

def three_level_map():
    """US-T -> HLR-T -> LLR-T: the synthetic 3-level chain (TC-RM-17)."""
    return make_map(
        REQHARNESS,
        [
            Node("US-T", "US", "root need"),
            Node("HLR-T", "HLR", "mid statement"),
            Node("LLR-T", "LLR", "focused statement"),
        ],
        [
            Edge("US-T", "HLR-T", "refines"),
            Edge("HLR-T", "LLR-T", "refines"),
        ],
    )


def asymmetric_map():
    """Focus HLR-F: `feeds it` = up (US-F via REFINES), `a change reaches` =
    down (TC-F/TC-G via VERIFIES — evidenced and missing — LLR-F/LLR-B via
    REFINES, edge input order).  The verifies edges run TC -> HLR so the
    wrong-direction lookup mutant finds nothing; TC-S is a true sink."""
    return make_map(
        CAPS,
        [
            Node("US-F", "US", "us title"),
            Node("HLR-F", "HLR", "focused hlr"),
            Node("TC-F", "TC", "tc evidenced"),
            Node("TC-G", "TC", "tc missing"),
            Node("LLR-F", "LLR", "first child"),
            Node("LLR-B", "LLR", "second child"),
            Node("TC-S", "TC", "sink"),
        ],
        [
            Edge("US-F", "HLR-F", "REFINES"),
            Edge("TC-F", "HLR-F", "VERIFIES", evidence_missing=False),
            Edge("TC-G", "HLR-F", "VERIFIES", evidence_missing=True),
            Edge("HLR-F", "LLR-F", "REFINES"),
            Edge("HLR-F", "LLR-B", "REFINES"),
        ],
    )


def glyph_map():
    """One map, three foci, every D5 glyph row.  Direction semantics per the
    D3 model: verifies/binds/covers edges list the TC/AT in `down` of the
    verified/bound/covered node and that node in `up` of the TC/AT."""
    return make_map(
        CAPS,
        [
            Node("US-1", "US", "us one"),
            Node("US-2", "US", "us two"),
            Node("HLR-1", "HLR", "hlr one"),
            Node("LLR-1", "LLR", "llr one"),
            Node("LLR-2", "LLR", "llr two"),
            Node("TC-1", "TC", "tc evidenced"),
            Node("TC-2", "TC", "tc missing"),
            Node("TC-3", "TC", "tc binds"),
            Node("AT-1", "AT", "at bound"),
            Node("AT-2", "AT", "at tagged"),
            Node("AT-3", "AT", "at covers"),
            Node("AT-4", "AT", "at covers not"),
        ],
        [
            Edge("US-1", "HLR-1", "REFINES"),
            Edge("HLR-1", "LLR-1", "REFINES"),
            Edge("TC-1", "LLR-1", "VERIFIES", evidence_missing=False),
            Edge("TC-2", "LLR-1", "VERIFIES", evidence_missing=True),
            Edge("AT-1", "TC-3", "BINDS", evidence_missing=False),
            Edge("AT-2", "TC-3", "BINDS", evidence_missing=True),
            Edge("TC-3", "LLR-2", "VERIFIES", evidence_missing=False),
            Edge("AT-3", "US-2", "COVERS", evidence_missing=False),
            Edge("AT-4", "US-2", "COVERS", evidence_missing=True),
            Edge("US-2", "HLR-1", "REFINES"),
        ],
    )


def hop2_map():
    """Focus LLR-D.  Per-direction minimum hops: up HLR-D(1), US-D(2 — the
    +01 upstream cut); down TC-D(1) only.  The both-direction count
    (M-RVS-7) sees {US-D, TC-E, AT-D} at hop 2 — a deliberate disagreement.
    Flow semantics per the D3 model: covers AT-D -> US-D flows US-D -> AT-D,
    verifies TC-* -> * flows * -> TC-*."""
    return make_map(
        REQHARNESS,
        [
            Node("US-D", "US", "up one"),
            Node("AT-D", "AT", "up two"),
            Node("HLR-D", "HLR", "mid"),
            Node("LLR-D", "LLR", "focused"),
            Node("TC-D", "TC", "down one"),
            Node("TC-E", "TC", "side"),
        ],
        [
            Edge("AT-D", "US-D", "covers"),
            Edge("AT-D", "TC-D", "binds", evidence_missing=False),
            Edge("US-D", "HLR-D", "refines"),
            Edge("HLR-D", "LLR-D", "refines"),
            Edge("TC-E", "HLR-D", "verifies", evidence_missing=False),
            Edge("TC-D", "LLR-D", "verifies", evidence_missing=False),
        ],
    )


def diamond_wired_map():
    """The diamond the profile cannot build (the reqharness flow graph is a
    DAG — up-reachable and down-reachable sets never intersect on a
    profile-valid map, so OQ-SHEET-5's both-sections row and M-RVS-8's
    mixed-depth marker need a hand-wired map): TC-C sits in `down` of the
    focus at hop 1 AND in `up` at hop 2, so a both-direction BFS marks it at
    mixed depth 1 where the per-direction minimum is 2."""
    base_map = make_map(
        REQHARNESS,
        [
            Node("LLR-F", "LLR", "focused"),
            Node("HLR-A", "HLR", "up one"),
            Node("TC-C", "TC", "both ways"),
        ],
        [],
    )
    edges = (
        Edge("HLR-A", "LLR-F", "refines"),
        Edge("HLR-A", "TC-C", "covers"),  # wired: flows TC-C -> HLR-A
        Edge("LLR-F", "TC-C", "refines"),  # wired: flows LLR-F -> TC-C
    )
    return base_relmap(base_map, edges)


def gap_map():
    return make_map(
        CAPS,
        [
            Node("HLR-G", "HLR", "gap carrier"),
            Node("HLR-H", "HLR", "clean"),
            Node("LLR-H", "LLR", "child"),
        ],
        [Edge("HLR-H", "LLR-H", "REFINES")],
    )


def ranked_gaps(m):
    ranked, _ = rank_gaps(m, detect_gaps(m), None)
    return tuple(ranked)


def overflow_map(n_down=40):
    nodes = [Node("HLR-BIG", "HLR", "big parent")]
    edges = []
    for i in range(1, n_down + 1):
        nodes.append(Node(f"LLR-BIG.{i}", "LLR", f"child {i}"))
        edges.append(Edge("HLR-BIG", f"LLR-BIG.{i}", "refines"))
    return make_map(REQHARNESS, nodes, edges)


def hostile_map():
    return make_map(
        REQHARNESS,
        [
            Node("HLR-H", "HLR", "hostile [bold]red[/] \x1b[31m\x07\u202e\tpayload"),
            Node("LLR-[bold]HOST.1[/]", "LLR",
                 "title [bold]red[/] \x1b[31m\x07\u202e\nsecond row"),
        ],
        [Edge("HLR-H", "LLR-[bold]HOST.1[/]", "refines")],
    )


def hostile_gaps():
    return (
        Gap("MED", "HLR WITHOUT LLR", "LLR-[bold]HOST.1[/]",
            "gap [bold]red[/] sentence \x1b[31m\x07\u202e payload", 0),
    )


# ---------------------------------------------------------------------------
# LLR-RVS.1 — the header
# ---------------------------------------------------------------------------


def test_llr_rvs_1_1_header_is_two_rows_over_relmap_node():
    """Row 0 bold INK `<id> · <title>`, row 1 the kind chip — from
    `RelMap.node(focused)`, no source/path segment (AT-140)."""
    view, st = build(three_level_map(), "LLR-T")
    rows = view.paint(st)
    assert rows[0].plain == darkside.fit("LLR-T · focused statement", 118)
    assert rows[0].spans[0].style == f"bold {darkside.INK}"
    assert rows[1].plain == " LLR " + " " * (118 - 5)
    assert style_at(rows[1], 2) == f"{darkside.INK} on {darkside.STEP}"
    # NO source/path segment: the header is EXACTLY the fitted `id · title`.
    assert rows[0].plain.rstrip() == "LLR-T · focused statement"
    for w in (87, 40):
        rows = view.paint(view_state(three_level_map(), "LLR-T", w=w))
        assert rows[0].plain == darkside.fit("LLR-T · focused statement", w)
        assert rows[1].plain.startswith(" LLR ")


def test_llr_rvs_1_2_darkside_casing_on_canon_labels():
    """Edge-type and gap-kind labels render lowercase (the CAPS profile stores
    them ALL-CAPS — verbatim rendering, M-RVS-2, reddens this).  Node ids and
    kinds are identifiers and keep their case."""
    view, st = build(asymmetric_map(), "HLR-F")
    rows = plains(view, st)
    assert darkside.fit("↑1 refines US-F", 118) in rows
    assert darkside.fit("↓1 verifies TC-F ✓", 118) in rows
    assert darkside.fit("↓1 verifies TC-G !", 118) in rows
    for caps in ("REFINES", "VERIFIES", "BINDS", "COVERS"):
        assert caps not in [r.rstrip() for r in rows], caps
    m = gap_map()
    view, st = build(m, "HLR-G", gaps=ranked_gaps(m))
    rows = plains(view, st)
    assert any(r.startswith("! hlr without llr  ") for r in rows)
    assert not any("HLR WITHOUT LLR" in r for r in rows)
    # identifiers keep their case
    assert any("HLR-G" in r for r in rows)


def test_llr_rvs_1_2_casing_source_census():
    """No caps-transformation helper and no catalogue caps literal in the
    renderer source — the census a per-label fake cannot satisfy."""
    source = inspect.getsource(sheet_mod)
    assert ".upper(" not in source
    for caps in ("HLR WITHOUT LLR", "VERIFIES WITHOUT EVIDENCE", "REFINES"):
        assert caps not in source, caps


# ---------------------------------------------------------------------------
# LLR-RVS.2 — feeds it / a change reaches
# ---------------------------------------------------------------------------


def test_llr_rvs_2_1_and_2_2_section_oracles_asymmetric():
    """`feeds it` lists `up(focused)`, `a change reaches` lists `down(focused)`,
    in edge input order, on an asymmetric fixture (M-RVS-3 wrong-direction
    lookup, M-RVS-4 swapped sections)."""
    m = asymmetric_map()
    assert m.up("HLR-F") == ("US-F",)
    assert m.down("HLR-F") == ("TC-F", "TC-G", "LLR-F", "LLR-B")
    view, st = build(m, "HLR-F")
    rows = plains(view, st)
    feeds = _section(rows, FEEDS_BAND)
    reaches = _section(rows, REACHES_BAND)
    assert feeds == fitted(["↑1 refines US-F"], 118)
    assert reaches == fitted([
        "↓1 verifies TC-F ✓",
        "↓1 verifies TC-G !",
        "↓1 refines LLR-F",
        "↓1 refines LLR-B",
    ], 118)


def test_llr_rvs_2_3_evidence_glyph_table():
    """refines none · verifies/covers ✓ SAGE evidenced, ! ALERT missing (or in
    cycle) · binds ● SAGE bound, ◐ WARN tagged; no ○ on sheet rows."""
    m = glyph_map()

    view, st = build(m, "LLR-1")
    rows = plains(view, st)
    assert _section(rows, FEEDS_BAND) == fitted([
        "↑1 refines HLR-1",
        CUT_UP.format(n=2),
    ], 118)
    assert _section(rows, REACHES_BAND) == fitted([
        "↓1 verifies TC-1 ✓",
        "↓1 verifies TC-2 !",
    ], 118)

    view, st = build(m, "TC-3")
    painted = view.paint(st)
    rows = [r.plain for r in painted]
    feeds = _section(rows, FEEDS_BAND)
    reaches = _section(rows, REACHES_BAND)
    assert feeds == fitted(["↑1 verifies LLR-2 ✓"], 118)
    assert reaches == fitted(["↓1 binds AT-1 ●", "↓1 binds AT-2 ◐"], 118)
    row = painted[rows.index(reaches[0])]
    assert style_at(row, row.plain.index("●")) == darkside.SAGE
    row = painted[rows.index(reaches[1])]
    assert style_at(row, row.plain.index("◐")) == darkside.WARN

    view, st = build(m, "US-2")
    rows = plains(view, st)
    assert _section(rows, FEEDS_BAND) == [darkside.fit(EMPTY_LINE, 118)]
    assert _section(rows, REACHES_BAND) == fitted([
        "↓1 covers AT-3 ✓", "↓1 covers AT-4 !", "↓1 refines HLR-1",
        CUT_DOWN.format(n=1),
    ], 118)

    row = [r for r in view.paint(view_state(m, "LLR-1"))
           if "TC-2" in r.plain][0]
    assert style_at(row, row.plain.index("!")) == darkside.ALERT

    # an in-cycle verifies edge renders ! ALERT even when evidenced: drive the
    # flag directly through a hand-wired RelMap (the profile cannot build this
    # shape — that is the point of the flag).
    from dataclasses import replace as dc_replace

    probe = make_map(
        REQHARNESS,
        [Node("TC-W", "TC", ""), Node("LLR-W", "LLR", "")],
        [Edge("TC-W", "LLR-W", "verifies", evidence_missing=False)],
    )
    cyc_edge = dc_replace(probe.edges[0], in_cycle=True)
    wired = base_relmap(probe, (cyc_edge,))
    row = [r for r in build(wired, "LLR-W")[0].paint(view_state(wired, "LLR-W"))
           if "TC-W" in r.plain][0]
    assert style_at(row, row.plain.index("!")) == darkside.ALERT


def base_relmap(m, edges):
    """The same map with `edges` swapped in — an in_cycle flag the profile
    builder cannot produce."""
    from mapper.relmap.model import RelMap

    up: dict[str, list[str]] = {}
    down: dict[str, list[str]] = {}
    for e in edges:
        t = {t.name: t for t in m.profile.edge_types}[e.type]
        if t.downstream:
            origin, target = e.src, e.dst
        else:
            origin, target = e.dst, e.src
        down.setdefault(origin, []).append(target)
        up.setdefault(target, []).append(origin)
    return RelMap(
        m.profile, m.nodes, tuple(edges), (), (), m.sourced,
        {k: tuple(v) for k, v in up.items()},
        {k: tuple(v) for k, v in down.items()},
    )


def test_llr_rvs_2_4_honest_empty_sections():
    """An empty section paints `╌╌ none on record` in MUT immediately under
    its band — never skipped (M-RVS-6)."""
    view, st = build(three_level_map(), "LLR-T")
    rows = plains(view, st)
    assert _section(rows, REACHES_BAND) == [darkside.fit(EMPTY_LINE, 118)]
    assert _section(rows, GAPS_BAND) == [darkside.fit(EMPTY_LINE, 118)]
    # the empty line sits IMMEDIATELY under the band
    i = next(idx for idx, r in enumerate(rows)
             if r.startswith(f" {REACHES_BAND} "))
    assert rows[i + 1] == darkside.fit(EMPTY_LINE, 118)
    # a sink node (no up, no down) declares both sections empty
    m = asymmetric_map()
    assert m.up("TC-S") == () and m.down("TC-S") == ()
    view, st = build(m, "TC-S")
    rows = plains(view, st)
    assert _section(rows, FEEDS_BAND) == [darkside.fit(EMPTY_LINE, 118)]
    assert _section(rows, REACHES_BAND) == [darkside.fit(EMPTY_LINE, 118)]


def test_llr_rvs_2_4_empty_line_is_mut():
    view, st = build(three_level_map(), "LLR-T")
    rows = view.paint(st)
    i = next(idx for idx, r in enumerate(rows)
             if r.plain.startswith(f" {REACHES_BAND} "))
    empty = rows[i + 1]
    assert style_at(empty, 0) == darkside.MUT


def test_empty_relmap_paints_a_declared_empty_sheet():
    m = make_map(REQHARNESS, [], [])
    view, st = build(m, None)
    rows = view.paint(st)
    assert len(rows) == 34
    assert rows[0].plain == darkside.fit(NO_NODES_LINE, 118)
    assert all(r.cell_len == 118 for r in rows)


def test_notice_is_the_body_through_the_sink():
    notice = "structure: refused (x): file not found - descriptor skipped"
    view, st = build(None, None, notice=notice)
    rows = view.paint(st)
    assert rows[0].plain == darkside.fit(notice, 118)
    assert all(r.plain == " " * 118 for r in rows[1:])


# ---------------------------------------------------------------------------
# LLR-RVS.3 — declared cuts and the `c` chain density
# ---------------------------------------------------------------------------


def test_llr_rvs_3_1_declared_hop2_cuts_direct_only():
    """The cut line: zero-padded NN, lowercase words, em-dash, OMITTED at
    zero; the count is the per-direction minimum-distance-2 count,
    cross-checked against the behavioural oracle `neighbourhood(2) −
    neighbourhood(1)` filtered per direction (M-RVS-7 counts both
    directions and disagrees on this fixture)."""
    m = hop2_map()
    view, st = build(m, "LLR-D")
    rows = plains(view, st)
    assert _section(rows, FEEDS_BAND) == fitted([
        "↑1 refines HLR-D",
        CUT_UP.format(n=1),
    ], 118)
    assert _section(rows, REACHES_BAND) == fitted([
        "↓1 verifies TC-D ✓",
        CUT_DOWN.format(n=1),
    ], 118)
    # the 3-level chain (LLR focus): upstream cut present, downstream omitted
    m = three_level_map()
    view, st = build(m, "LLR-T")
    rows = plains(view, st)
    assert darkside.fit(CUT_UP.format(n=1), 118) in rows
    assert "downstream at hop 2" not in "\n".join(rows)
    # behavioural oracle cross-check on the hop2 map: the per-direction
    # counts equal `neighbourhood(2) − neighbourhood(1)` filtered per
    # direction — and BOTH disagree with the both-direction count
    m = hop2_map()
    focus = "LLR-D"

    def directional_oracle(step):
        ring = m.neighbourhood(focus, 2) - m.neighbourhood(focus, 1)
        seen = {focus}
        frontier = [focus]
        while frontier:
            fresh = [nb for node in frontier for nb in step(node)
                     if nb not in seen]
            for nb in fresh:
                seen.add(nb)
            frontier = fresh
        return {n for n in ring if n in seen}

    assert m.neighbourhood(focus, 2) - m.neighbourhood(focus, 1) == {
        "US-D", "TC-E", "AT-D"}
    assert directional_oracle(m.up) == {"US-D"}
    assert directional_oracle(m.down) == {"AT-D"}


def test_llr_rvs_3_2_stacked_lists_every_node_by_minimum_hop():
    """Stacked density: full chain, per-direction minimum-hop markers, ordered
    by hop then edge input order.  The diamond (hand-wired — the profile's
    flow graph is a DAG, so the both-sections row and the mixed-depth
    disagreement cannot arise on a profile-valid map) puts TC-C in `down` at
    hop 1 and in `up` at hop 2: it renders under BOTH sections (OQ-SHEET-5)
    marked ↑2 — a both-direction BFS (M-RVS-8) marks it ↑1."""
    view, st = build(three_level_map(), "LLR-T")
    view.toggle("c")
    rows = plains(view, st)
    assert _section(rows, FEEDS_BAND) == fitted([
        "↑1 refines HLR-T",
        "↑2 refines US-T",
    ], 118)

    m = diamond_wired_map()
    assert m.down("LLR-F") == ("TC-C",) and m.up("LLR-F") == ("HLR-A",)
    view, st = build(m, "LLR-F")
    view.toggle("c")
    rows = plains(view, st)
    feeds = _section(rows, FEEDS_BAND)
    reaches = _section(rows, REACHES_BAND)
    assert feeds == fitted([
        "↑1 refines HLR-A",
        "↑2 covers TC-C ✓",
    ], 118)
    # the wired cycle LLR-F -> TC-C -> HLR-A -> LLR-F puts TC-C in `down` at
    # hop 1 and HLR-A in `down` at hop 2 — TC-C renders under BOTH sections
    assert reaches == fitted([
        "↓1 refines TC-C",
        "↓2 covers HLR-A ✓",
    ], 118)
    # the hop-2 cut lines are DIRECT-density declarations — absent stacked
    assert "hop 2" not in "\n".join(feeds + reaches)
    # the stacked id gradation: hop-1 ids carry INK, hop≥2 ids carry MUT
    # (the review's M-REV-2 flattens the gradation to plain INK and reddens
    # this oracle)
    painted = view.paint(st)
    by_plain = {r.plain: r for r in painted}
    row1 = by_plain[fitted(["↑1 refines HLR-A"], 118)[0]]
    assert style_at(row1, row1.plain.index("HLR-A")) == darkside.INK
    row2 = by_plain[fitted(["↑2 covers TC-C ✓"], 118)[0]]
    assert style_at(row2, row2.plain.index("TC-C")) == darkside.MUT
    row3 = by_plain[fitted(["↓2 covers HLR-A ✓"], 118)[0]]
    assert style_at(row3, row3.plain.index("HLR-A")) == darkside.MUT


def test_llr_rvs_3_3_c_toggle_flips_rows_note_and_word_together():
    """`c` flips direct ↔ stacked; the word is `direct only` ↔ `stacked
    chain`; the note lines are verbatim; `enter`/`k` are not ours (AT-141;
    M-RVS-9 flips the note without the rows — COND-QA-5 pins the SYNTHETIC
    kill: the 3-level chain gains its `↑2` row exactly when the note
    flips)."""
    view, st = build(three_level_map(), "LLR-T")
    assert view.toggle("enter") == ""
    assert view.toggle("k") == ""
    assert view.toggle("c") == WORD_STACKED
    stacked_rows = plains(view, st)
    note = [r for r in stacked_rows if r.startswith("next ▸")]
    assert note == [darkside.fit(STACKED_NOTE, 118)]
    assert darkside.fit("↑2 refines US-T", 118) in stacked_rows
    assert view.toggle("c") == WORD_DIRECT
    direct_rows = plains(view, st)
    note = [r for r in direct_rows if r.startswith("next ▸")]
    assert note == [darkside.fit(DIRECT_NOTE, 118)]
    assert darkside.fit("↑2 refines US-T", 118) not in direct_rows
    assert darkside.fit(CUT_UP.format(n=1), 118) in direct_rows


# ---------------------------------------------------------------------------
# LLR-RVS.4 — gaps on this node
# ---------------------------------------------------------------------------


def test_llr_rvs_4_1_only_the_focused_nodes_gaps_as_given():
    """Exactly the focused node's gaps from the host-supplied rows, consumed
    AS GIVEN (no re-rank, no re-detect), `! <kind>  <sentence>`, kind in bold
    ALERT, Darkside-cased (AT-142; M-RVS-10 filters by severity instead of
    the node)."""
    m = gap_map()
    gaps = ranked_gaps(m)
    assert len(gaps) == 1 and gaps[0].node == "HLR-G"
    view, st = build(m, "HLR-G", gaps=gaps)
    rows = plains(view, st)
    gap_rows = _section(rows, GAPS_BAND)
    assert gap_rows == [darkside.fit(
        "! hlr without llr  HLR-G has no LLR under it: gap carrier", 118)]
    painted = view.paint(st)
    row = [r for r in painted if r.plain.startswith("! hlr without llr")][0]
    assert style_at(row, row.plain.index("hlr without llr")) == f"bold {darkside.ALERT}"
    # another node: the declared empty line, even though HLR-G's gap is in
    # the host-supplied rows
    view, st = build(m, "HLR-H", gaps=gaps)
    rows = plains(view, st)
    assert _section(rows, GAPS_BAND) == [darkside.fit(EMPTY_LINE, 118)]
    # consumed as given: order follows the supplied tuple, not severity
    g2 = Gap("LOW", "ORPHAN TC", "HLR-G", "second sentence", 0)
    g1 = Gap("HIGH", "TRACEABILITY CYCLE", "HLR-G", "first sentence", 0)
    view, st = build(m, "HLR-G", gaps=(g2, g1))
    rows = plains(view, st)
    gap_rows = _section(rows, GAPS_BAND)
    assert gap_rows[0].startswith("! orphan tc  second sentence")
    assert gap_rows[1].startswith("! traceability cycle  first sentence")


def test_llr_rvs_4_1_sentence_cut_to_width_one_ellipsis():
    m = gap_map()
    view, st = build(m, "HLR-G", gaps=ranked_gaps(m), w=40)
    rows = plains(view, st)
    row = [r for r in rows if r.startswith("! ")][0]
    assert row.endswith("…")
    assert row.count("…") == 1
    sentence = "HLR-G has no LLR under it: gap carrier"
    assert row == darkside.fit(
        "! hlr without llr  " + darkside.fit(sentence, 40 - 2 - 15 - 2), 40)


# ---------------------------------------------------------------------------
# LLR-RVS.5 — the one sink under hostile payloads
# ---------------------------------------------------------------------------


def test_llr_rvs_5_1_hostile_frame_renders_byte_literal_on_one_row():
    """A hostile title, neighbour id and gap sentence render byte-literal:
    no markup parse, no control bytes, ONE row per logical row, and no
    ACCENT/ALERT/WARN span carrying payload text (AT-144; the M-RVS-1
    family)."""
    m = hostile_map()
    view, st = build(m, "LLR-[bold]HOST.1[/]", gaps=hostile_gaps())
    rows = view.paint(st)
    assert len(rows) == 34
    assert all(r.cell_len == 118 for r in rows)
    text = "\n".join(r.plain for r in rows)
    assert "[bold]red[/]" in text
    for bad in ("\x1b", "\x07", "\u202e", "\t"):
        assert bad not in text
    for r in rows:  # ONE row per logical row: LF can never forge a second row
        assert "\n" not in r.plain
    assert "�" in text  # coerced control/format code points
    # no ACCENT/ALERT/WARN span may carry payload characters
    for row in rows:
        for span in row.spans:
            frag = row.plain[span.start:span.end]
            if "[bold]red[/]" in frag:
                assert darkside.ACCENT not in (span.style or "")
                assert darkside.ALERT not in (span.style or "")
                assert darkside.WARN not in (span.style or "")
    header = rows[0]
    assert style_at(header, header.plain.index("[bold]")) == f"bold {darkside.INK}"
    # the hostile focus id and title render byte-literal in the header
    assert "LLR-[bold]HOST.1[/]" in header.plain
    # the hostile gap sentence renders byte-literal on its gap row
    gap_row = [r for r in rows if r.plain.startswith("! ")][0]
    assert "gap [bold]red[/] sentence" in gap_row.plain


# ---------------------------------------------------------------------------
# LLR-RVS.6 — width discipline and counted overflow
# ---------------------------------------------------------------------------


def _sweep_fixtures():
    long_title = "a very long statement that keeps going " * 4
    m = make_map(
        REQHARNESS,
        [Node("HLR-L", "HLR", long_title),
         Node("LLR-L.1", "LLR", long_title)] +
        [Node(f"LLR-W.{i}", "LLR", "w") for i in range(12)],
        [Edge("HLR-L", f"LLR-W.{i}", "refines") for i in range(1, 13)],
    )
    g = Gap("MED", "HLR WITHOUT LLR", "HLR-L", long_title, 0)
    return m, g


@pytest.mark.parametrize("w,h", [(118, 34), (87, 34)])
@pytest.mark.parametrize("stacked", [False, True])
def test_llr_rvs_6_1_width_discipline_zero_c10_events(w, h, stacked):
    """Every row fits the canvas width EXACTLY (fit pad or single-ellipsis
    cut); with the C10 audit mapping injected the painted frame records zero
    clip/overprint entries (AT-143; M-RVS-11 paints the raw title)."""
    m, g = _sweep_fixtures()
    audit: dict = {}
    view = sheet_mod.SheetView(audit=audit)
    if stacked:
        view.toggle("c")
    st = view_state(m, "HLR-L", gaps=(g,), w=w, h=h)
    rows = view.paint(st)
    assert len(rows) == h
    for row in rows:
        assert row.cell_len == w
        assert "\n" not in row.plain
    assert audit.get("clip", []) == []
    assert audit.get("overprint", []) == []
    # the raw title is NEVER painted: the header is the fitted `id · title`
    long_title = m.node("HLR-L").title
    assert rows[0].plain == darkside.fit(f"HLR-L · {long_title}", w)


def test_llr_rvs_6_1_long_statement_ellipsis_matches_fit():
    m, g = _sweep_fixtures()
    view, st = build(m, "HLR-L", gaps=(g,), w=87)
    rows = plains(view, st)
    row = [r for r in rows if r.startswith("! ")][0]
    assert row.count("…") == 1
    assert row.endswith("…")
    assert row == darkside.fit(
        "! hlr without llr  " + darkside.fit(
            m.node("HLR-L").title, 87 - 2 - 15 - 2), 87)


def test_llr_rvs_6_2_overflow_is_counted_never_silent():
    """Rows past the viewport are declared `… +NN more` in MUT — the body's
    last line (AT-141/143 black-box promotion; M-RVS-12 drops rows with no
    counted line)."""
    m = overflow_map(40)
    view, st = build(m, "HLR-BIG", w=87, h=12)
    rows = view.paint(st)
    assert len(rows) == 12
    # content: header, chip, band, empty feeds, band, 40 rows, band, empty
    # gaps, note = 48 rows; 11 shown + the counted line
    assert rows[-1].plain == darkside.fit(MORE.format(n=48 - 11), 87)
    assert style_at(rows[-1], 0) == darkside.MUT
    assert "↓1 refines LLR-BIG.1" in rows[5]
    # when everything fits, the note is the last CONTENT line (the canvas
    # pads the remainder of the viewport with blank rows)
    view, st = build(three_level_map(), "LLR-T", w=87, h=34)
    rows = view.paint(st)
    note_at = next(i for i, r in enumerate(rows)
                   if r.plain == darkside.fit(DIRECT_NOTE, 87))
    assert all(r.plain.strip() == "" for r in rows[note_at + 1:])


def test_llr_rvs_6_1_degenerate_height_paints_the_honest_default_body():
    """The mount-time degenerate viewport (the shipped host's auto-height
    canvas settles at height 1 — LED-2026-10-25-r2.19) paints the honest
    default body of 24 rows, header included; every explicit height is
    respected as-is.  The review's M-REV-1 flattens the `_budget` floor to
    `max(height, 1)` and reddens this arm."""
    m = three_level_map()
    view = sheet_mod.build_view()
    rows = view.paint(view_state(m, "LLR-T", h=1))
    assert len(rows) == 24
    assert rows[0].plain == darkside.fit("LLR-T · focused statement", 118)
    for h in (2, 17, 34):
        rows = view.paint(view_state(m, "LLR-T", h=h))
        assert len(rows) == h


# ---------------------------------------------------------------------------
# LLR-RVS.7 — read-only evidence labels
# ---------------------------------------------------------------------------


def test_llr_rvs_7_1_no_osopen_no_render_call():
    """Evidence names are labels: no `osopen` import/call, no `.render(` call
    (the A3 census pins the renderer surface), no clickable attachment."""
    tree = ast.parse(inspect.getsource(sheet_mod))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert not any("osopen" in a.name for a in node.names), ast.dump(node)
        if isinstance(node, ast.ImportFrom):
            assert "osopen" not in (node.module or ""), ast.dump(node)
        assert not (isinstance(node, ast.Attribute) and node.attr == "render")
    source = inspect.getsource(sheet_mod)
    assert "osopen" not in source
    assert ".render(" not in source


# ---------------------------------------------------------------------------
# The D1 surface from the sheet side
# ---------------------------------------------------------------------------


def test_d1_sheet_wiring_row_count_and_toggle_vocabulary():
    view = base.build_view("sheet")
    assert view.name == "sheet"
    assert not isinstance(view, base.PendingView)
    m = three_level_map()
    assert view.row_count(view_state(m, "LLR-T")) == 3
    assert view.row_count(view_state(None, None)) == 0
    assert view.toggle("enter") == "" and view.toggle("k") == ""
    assert view.toggle("c") == WORD_STACKED
    assert view.toggle("c") == WORD_DIRECT


# ---------------------------------------------------------------------------
# AT arms through the real host (Layer B — real keys, C-16)
# ---------------------------------------------------------------------------

HEADER = "| Id | Status | Statement |\n|---|---|---|\n"


def canon(*rows: str) -> str:
    return HEADER + "".join(r + "\n" for r in rows)


def row(row_id: str, status: str = "active", statement: str = "text") -> str:
    return f"| {row_id} | {status} | {statement} |"


def frame_text(screen) -> str:
    return "\n".join(
        "".join(seg.text for seg in strip)
        for strip in screen._compositor.render_strips()  # noqa: SLF001
    )


def frame_runs(screen):
    """The composited frame as merged (text, style) runs — adjacent segments
    with the same style merge, so a styled label is findable as ONE run
    (the compositor hands per-character segments for cell-built rows)."""
    out = []
    for strip in screen._compositor.render_strips():  # noqa: SLF001
        merged: list[list[str]] = []
        for seg in strip:
            style = str(seg.style)
            if merged and merged[-1][1] == style:
                merged[-1][0] += seg.text
            else:
                merged.append([seg.text, style])
        out.append([(t, s) for t, s in merged])
    return out


LONG = "a long statement that will not fit eighty seven cells " * 3

WORKSPACE_CANON = canon(
    row("HLR-DEMO.1", statement="the host arms"),
    row("LLR-DEMO.1.1"),
    row("LLR-DEMO.1.2"),
    row("HLR-DEMO.2", statement=LONG.strip()),
)


@pytest.fixture
def workspace(tmp_path):
    (tmp_path / "REQUIREMENTS.md").write_text(WORKSPACE_CANON, encoding="utf-8")
    return tmp_path


async def open_sheet(app, pilot, ws, presses=()):
    """Push the relation screen, switch to the sheet with the real `3` key,
    then drive any cursor moves on the SHEET's own row axis (the node list —
    the pre-lane matrix view in this worktree is the PendingView placeholder,
    whose cursor is an honest no-op; the joined AT moves the cursor on the
    landed matrix and presses `3`, the same end state)."""
    screen = RelMapScreen("demo", ws, descriptor=default_descriptor())
    app.push_screen(screen)
    await pilot.pause()
    await pilot.pause()
    await pilot.press("3")
    await pilot.pause()
    await pilot.pause()
    for key in presses:
        await pilot.press(key)
        await pilot.pause()
        await pilot.pause()
    return screen


def canvas_size(screen):
    canvas = screen.query_one("#relmap-canvas", Static)
    return canvas.size.width or 118, canvas.size.height or 1


async def test_at_140_sheet_on_a_linked_llr(workspace):
    """Cursor onto an LLR with a parent HLR (non-default), press `3`: header
    `id · title` + chip, `feeds it` = exactly the oracle's `up` rows
    (`↑1 refines <HLR id>`, no glyph), the reaches and gaps sections declare
    their empties, the density note reads `direct only`, no source/path
    segment.  (The crumb word lands after the first `c` round-trip — the
    host stores toggle words only on toggle; asserted in AT-141.)"""
    app = MapperApp(workspace)
    async with app.run_test(size=(118, 34)) as pilot:
        screen = await open_sheet(app, pilot, workspace, presses=("down",))
        assert screen.focus == "LLR-DEMO.1.1"
        w, _ = canvas_size(screen)
        painted = frame_text(app.screen)
        # the frozen host stores the toggle word only AFTER a toggle, so the
        # first-open crumb reads `name / relmap / sheet` and the density word
        # is declared by the note line (the same convention the gaps lane
        # pins for `by kind`; the AT-141 arm asserts both words in the crumb
        # after the real `c` round-trip — deviation recorded in the packet)
        crumb = next(ln for ln in painted.splitlines() if "relmap / sheet" in ln)
        assert crumb.rstrip() == "demo / relmap / sheet"
        lines = painted.splitlines()
        header = next(ln for ln in lines if ln.startswith("LLR-DEMO.1.1 · "))
        assert header.rstrip() == "LLR-DEMO.1.1 · text"
        assert "/" not in header
        chip = lines[lines.index(header) + 1]
        assert chip.startswith(" LLR ")
        feeds = _section(lines, FEEDS_BAND)
        assert [r.rstrip() for r in feeds] == ["↑1 refines HLR-DEMO.1"]
        assert [r.rstrip() for r in _section(lines, REACHES_BAND)] == [EMPTY_LINE]
        assert [r.rstrip() for r in _section(lines, GAPS_BAND)] == [EMPTY_LINE]
        note = next(ln for ln in lines if ln.startswith("next ▸"))
        assert note.strip() == DIRECT_NOTE
        assert w == 118


async def test_at_141_c_chain_density_on_an_hlr(workspace):
    """`3` on the HLR: reaches rows; `c` flips the crumb to `stacked chain`
    and the note to the stacked line — the one-hop rows unchanged
    (asserted, not assumed); `c` again restores both."""
    app = MapperApp(workspace)
    async with app.run_test(size=(118, 34)) as pilot:
        await open_sheet(app, pilot, workspace)
        painted = frame_text(app.screen)
        reaches_direct = [r.rstrip() for r in _section(painted.splitlines(), REACHES_BAND)]
        assert reaches_direct == [
            "↓1 refines LLR-DEMO.1.1", "↓1 refines LLR-DEMO.1.2",
        ]
        await pilot.press("c")
        await pilot.pause()
        await pilot.pause()
        painted = frame_text(app.screen)
        crumb = next(ln for ln in painted.splitlines() if "relmap / sheet" in ln)
        assert "sheet · stacked chain" in crumb
        note = next(ln for ln in painted.splitlines() if ln.startswith("next ▸"))
        assert note.strip() == STACKED_NOTE
        reaches_stacked = [r.rstrip() for r in _section(painted.splitlines(), REACHES_BAND)]
        assert reaches_stacked == reaches_direct
        feeds = [r.rstrip() for r in _section(painted.splitlines(), FEEDS_BAND)]
        assert feeds == [EMPTY_LINE]
        await pilot.press("c")
        await pilot.pause()
        await pilot.pause()
        painted = frame_text(app.screen)
        crumb = next(ln for ln in painted.splitlines() if "relmap / sheet" in ln)
        assert "sheet · direct only" in crumb
        note = next(ln for ln in painted.splitlines() if ln.startswith("next ▸"))
        assert note.strip() == DIRECT_NOTE


async def test_at_142_the_nodes_own_gaps(workspace):
    """The gap-carrying HLR lists exactly its own gap — kind in bold ALERT,
    Darkside-cased, sentence cut to width — and no other node's gap appears."""
    derivation = derive_reqharness_map(workspace, default_descriptor())
    oracle = [g for g in detect_gaps(derivation.map) if g.node == "HLR-DEMO.2"]
    assert len(oracle) == 1
    app = MapperApp(workspace)
    async with app.run_test(size=(87, 34)) as pilot:
        screen = await open_sheet(app, pilot, workspace,
                                  presses=("down", "down", "down"))
        w, _ = canvas_size(screen)
        assert w == 87
        painted = frame_text(app.screen)
        gap_rows = [ln.rstrip() for ln in _section(painted.splitlines(), GAPS_BAND)]
        expected = f"! {oracle[0].kind.lower()}  {oracle[0].sentence}"
        assert len(gap_rows) == 1
        assert gap_rows[0].startswith("! hlr without llr  ")
        assert gap_rows[0] == darkside.fit(expected, w).rstrip()
        # the long sentence is cut with ONE trailing ellipsis at 87
        assert gap_rows[0].endswith("…")
        assert gap_rows[0].count("…") == 1
        # kind in bold ALERT
        runs = frame_runs(app.screen)
        flat = [(t, s) for strip in runs for t, s in strip]
        kind_runs = [s for t, s in flat if "hlr without llr" in t]
        assert kind_runs and all(f"bold {darkside.ALERT}" in s for s in kind_runs)
        # no other node's gap appears
        assert "LLR-DEMO" not in "\n".join(gap_rows)


def big_workspace(workspace):
    rows = [row("HLR-BIG", statement="big parent")]
    for i in range(1, 41):
        rows.append(row(f"LLR-BIG.{i}"))
    big = workspace / "big"
    big.mkdir()
    (big / "REQUIREMENTS.md").write_text(canon(*rows), encoding="utf-8")
    return big


async def test_at_143_87_column_check_and_counted_overflow(workspace):
    """At (87, 34) no row exceeds 87 cells, nothing wraps, the long-statement
    ellipsis matches fit — and on a many-LLR map the counted `… +NN more`
    line in MUT is the body's last visible line (LLR-RVS.6.2 black-box)."""
    app = MapperApp(workspace)
    async with app.run_test(size=(87, 34)) as pilot:
        await open_sheet(app, pilot, workspace, presses=("down",))
        lines = frame_text(app.screen).splitlines()
        assert len(lines) == 34, "a wrapped row would shift the frame"
        for ln in lines:
            assert Text(ln).cell_len <= 87
    big = big_workspace(workspace)
    app = MapperApp(big)
    async with app.run_test(size=(87, 34)) as pilot:
        screen = await open_sheet(app, pilot, big)
        _, h = canvas_size(screen)
        # direct content over the BIG map: header, chip, band, empty feeds,
        # band, 40 reaches rows, band, empty gaps, note = 48 rows
        hidden = 48 - (h - 1)
        lines = frame_text(app.screen).splitlines()
        assert len(lines) == 34
        for ln in lines:
            assert Text(ln).cell_len <= 87
        counted = next(ln for ln in lines if ln.strip().startswith("… +"))
        assert counted.strip() == MORE.format(n=hidden)
        runs = frame_runs(app.screen)
        idx = next(i for i, strip in enumerate(runs)
                   if "".join(t for t, _ in strip).strip() == counted.strip())
        styled = [s for t, s in runs[idx] if t.strip()]
        assert styled and all(darkside.MUT in s for s in styled)
        # nothing non-blank between the counted line and the keybar
        after = [ln for ln in lines[idx + 1:] if ln.strip()]
        assert after and all("all keys" in ln or "quit" in ln for ln in after)


async def test_at_144_hostile_payload_on_the_sheet(tmp_path):
    """A focused-node title carrying `[bold]red[/]`, ESC, BEL and U+202E
    renders byte-literal; no unintended ACCENT/ALERT/WARN span; no raise;
    `q` leaves cleanly.

    LF/TAB are deliberately absent from this canon-carried payload: the canon
    parser structurally excludes them (`parse_canon` line-splits before cell
    parsing; `_collapse` normalises TAB to space), so they can never reach a
    label through the shipped input surface — their coverage lives at the
    renderer seam, in `test_llr_rvs_5_1_hostile_frame_renders_byte_literal_on_one_row`'s
    in-process fixture above (review-inc005 F4)."""
    hostile = canon(
        row("HLR-HOST.1", statement="[bold]red[/] \x1b[31m\x07\u202e plain"),
        row("LLR-HOST.1.1", statement="[bold]red[/] \x1b[31m\x07\u202e title"),
    )
    (tmp_path / "REQUIREMENTS.md").write_text(hostile, encoding="utf-8")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await open_sheet(app, pilot, tmp_path, presses=("down",))
        runs = frame_runs(app.screen)
        flat = [(t, s) for strip in runs for t, s in strip]
        payload_runs = [(t, s) for t, s in flat if "[bold]red[/]" in t]
        assert payload_runs, "the payload must render"
        for t, s in payload_runs:
            assert darkside.ACCENT not in s
            assert darkside.ALERT not in s
            assert darkside.WARN not in s
        painted = frame_text(app.screen)
        assert "\x1b" not in painted and "\u202e" not in painted
        header = next(ln for ln in painted.splitlines()
                      if ln.startswith("LLR-HOST.1.1 · "))
        assert "[bold]red[/]" in header
        await pilot.press("q")
        await pilot.pause()
        assert app.screen.__class__.__name__ == "HomeScreen"


async def test_fixture_canon_derives_through_the_real_adapter(workspace):
    """Positive control for the fixture class: the small canon derives the
    four seeded nodes through the real adapter (the pilot arms read it)."""
    derivation = derive_reqharness_map(workspace, default_descriptor())
    assert [n.id for n in derivation.map.nodes] == [
        "HLR-DEMO.1", "LLR-DEMO.1.1", "LLR-DEMO.1.2", "HLR-DEMO.2",
    ]
