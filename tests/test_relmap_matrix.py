"""The matrix renderer — the traceability grid + the two-hop impact lens.

Lane L3, batch `2026-10-25-relmap-r2-batch`, increment 003.  Every node here
maps to the contract (`01-requirements.md` §4, the RVM family) and to the
acceptance design (`01b-acceptance-design.md` AT-130…AT-134):

* Layer 0 — branchful helpers with >= 3 cyclomatic paths (the window
  function, the strongest-edge ranking, the ring builder, the toggle
  vocabulary) exercised directly against `mapper/screens/relmap/matrix.py`.
* Layer A — white-box census arms over `build_map`-built synthetic maps
  (fixture policy ARC-05: built INLINE here, never in a shared fixture
  module), TC-RM-04…09.
* Layer B — the AT-130…134 nodes through the real app: `MapperApp` on a
  fixture workspace, `RelMapScreen` pushed the way Home will route it
  (the trunk `tests/test_relmap_shell.py` idiom), REAL keys via
  `pilot.press` (C-16), non-default values moved (C-10).

The hostile arms (AT-134) ride the COND-SEC-1 lane arm: canon-derived text
reaches the renderer through the ONE label sink (`base.label` —
`darkside._row_text`/`fit`, coerce-then-cut) so a payload of brackets, ESC,
U+202E, control chars, LF or TAB renders literally on ONE row.

Live-canon arms (AT-130/131 premise P2) copy the worktree's own
`REQUIREMENTS.md` into a non-git tmp workspace — the derived skeleton is
the honest 303-node map (85 HLR, 218 LLR, 215 `refines` edges, 7 gaps).
"""
from __future__ import annotations

import asyncio
import re
from pathlib import Path

import pytest
from rich.text import Text

import mapper
from mapper import darkside
from mapper.app import MapperApp
from mapper.canvas import Canvas
from mapper.relmap.descriptor import default_descriptor
from mapper.relmap.model import Edge, Node, VISIT_BUDGET, build_map
from mapper.relmap.profile import REQHARNESS
from mapper.screens.relmap import base
from mapper.screens.relmap.screen import RelMapScreen

ROOT = Path(mapper.__file__).resolve().parent.parent
LIVE_CANON = ROOT / "REQUIREMENTS.md"

#: The verbatim legend pinned by LLR-RVM.1.3 / AT-133 (Darkside casing).
LEGEND = "✓ verifies · ! evidence missing · · no verifies edge"
#: The verbatim skeleton declaration pinned by LLR-RVM.3.1 / AT-130.
NO_TEST_COLUMNS = ("no test columns yet — the AT→test table (B-141) "
                   "feeds this view")
#: Grid geometry pinned by the renderer (and mirrored here as the oracle).
GRID_TOP = 4  # header(1) + note/declaration(1) + ruler(2)


@pytest.fixture
def matrix_mod():
    """The renderer module under test — imported lazily so the RED phase
    fails at assertion/fixture level (PendingView answers `build_view`)
    rather than killing the whole collection."""
    from mapper.screens.relmap import matrix
    return matrix


def canon(*rows: str) -> str:
    return "| Id | Status | Statement |\n|---|---|---|\n" + "".join(
        r + "\n" for r in rows)


def row(row_id: str, status: str = "active", statement: str = "text") -> str:
    return f"| {row_id} | {status} | {statement} |"


# ---------------------------------------------------------------------------
# Synthetic maps (ARC-05: inline, never in a shared fixture module)
# ---------------------------------------------------------------------------

def demo_canon() -> str:
    return canon(
        row("HLR-DEMO.1", statement="parent one"),
        row("HLR-DEMO.2", statement="parent two"),
        row("LLR-DEMO.1.1"),
        row("LLR-DEMO.1.2"),
        row("LLR-DEMO.2.1"),
        row("LLR-DEMO.2.2"),
    )


def binds_map():
    """AT-133's census map: AT/TC nodes under REQHARNESS (possible
    in-process though the canon does not source them)."""
    nodes = (
        Node("HLR-T.1", "HLR", "parent"),
        Node("LLR-T.1.1", "LLR", "child one"),
        Node("LLR-T.1.2", "LLR", "child two"),
        Node("AT-1", "AT", "alpha", open=True),
        Node("AT-2", "AT", "beta"),
        Node("AT-3", "AT", "gamma", open=True),
        Node("AT-4", "AT", "delta"),
        Node("TC-1", "TC", "t one"),
        Node("TC-2", "TC", "t two"),
        Node("TC-3", "TC", "t three"),
    )
    edges = (
        Edge("HLR-T.1", "LLR-T.1.1", "refines"),
        Edge("HLR-T.1", "LLR-T.1.2", "refines"),
        Edge("AT-2", "TC-2", "binds"),
        Edge("AT-2", "TC-3", "binds"),
        Edge("AT-3", "TC-1", "binds", evidence_missing=True),
        Edge("TC-1", "LLR-T.1.1", "verifies", evidence_missing=True),
        Edge("TC-2", "LLR-T.1.1", "verifies"),
        Edge("TC-3", "HLR-T.1", "verifies"),
    )
    return build_map(REQHARNESS, nodes, edges,
                     sourced=("HLR", "LLR", "AT", "TC"))


def chain_map():
    """A same-direction three-chain with a side verifies edge:
    US-1 -> HLR-2 -> LLR-3, TC-9 verifies LLR-3."""
    nodes = (
        Node("US-1", "US", "root"),
        Node("HLR-2", "HLR", "mid"),
        Node("LLR-3", "LLR", "leaf"),
        Node("TC-9", "TC", "check"),
    )
    edges = (
        Edge("US-1", "HLR-2", "refines"),
        Edge("HLR-2", "LLR-3", "refines"),
        Edge("TC-9", "LLR-3", "verifies"),
    )
    return build_map(REQHARNESS, nodes, edges,
                     sourced=("US", "HLR", "LLR", "TC"))


def wide_map(count: int = 60):
    """One HLR over `count` LLRs — rows window far past the viewport."""
    nodes = [Node("HLR-W.1", "HLR", "root")]
    nodes += [Node(f"LLR-W.1.{i + 1:02d}", "LLR", f"leaf {i + 1}")
              for i in range(count)]
    edges = [Edge("HLR-W.1", f"LLR-W.1.{i + 1:02d}", "refines")
             for i in range(count)]
    return build_map(REQHARNESS, nodes, edges, sourced=("HLR", "LLR"))


def tc_map(count: int = 20):
    """One LLR verified by `count` TCs — the column window + ruler."""
    nodes = [Node("HLR-C.1", "HLR", "root"),
             Node("LLR-C.1.1", "LLR", "leaf")]
    nodes += [Node(f"TC-{i + 1:02d}", "TC", f"test {i + 1}")
              for i in range(count)]
    edges = [Edge("HLR-C.1", "LLR-C.1.1", "refines")]
    edges += [Edge(f"TC-{i + 1:02d}", "LLR-C.1.1", "verifies")
              for i in range(count)]
    return build_map(REQHARNESS, nodes, edges, sourced=("HLR", "LLR", "TC"))


def lf_tab_map():
    """The AT-134 LF/TAB payload title — build_map keeps titles verbatim,
    so the renderer's one-row seam is what coerces the bytes."""
    nodes = (
        Node("HLR-LF.1", "HLR", "left\tright\nnext payload"),
        Node("LLR-LF.1.1", "LLR", "child"),
    )
    edges = (Edge("HLR-LF.1", "LLR-LF.1.1", "refines"),)
    return build_map(REQHARNESS, nodes, edges, sourced=("HLR", "LLR"))


# ---------------------------------------------------------------------------
# Painting helpers (the oracle side)
# ---------------------------------------------------------------------------

def fresh_view(matrix_mod, lens_on: bool = False):
    view = matrix_mod.build_view()
    if lens_on:
        assert view.toggle("enter") == "panel lens"
    return view


def paint(view, m, *, focus, width=118, height=30):
    idx = {n.id: i for i, n in enumerate(m.nodes)}
    state = base.ViewState(
        relmap=m, notice=None, focus=focus, cursor=idx.get(focus, 0),
        gaps=(), width=width, height=height,
    )
    return view.paint(state)


def plain(rows) -> str:
    return "\n".join(r.plain for r in rows)


def gutter_layout(m):
    """The row-label field widths (LLR-RVM.1.1: right-aligned row number,
    a space, the id cut to a field between 8 and 12 cells, a space)."""
    numw = max(2, len(str(len(m.nodes))))
    idw = max(8, min(12, max(darkside.shown_cells(n.id) for n in m.nodes)))
    return numw, idw, numw + 1 + idw + 1


def checking_kinds(m):
    """Kinds that CHECK other nodes: srcs of a non-downstream edge type."""
    kinds = set()
    for t in m.profile.edge_types:
        if not t.downstream:
            kinds |= {src for src, _dst in t.pairs}
    return kinds


def checking_cols(m):
    return [n for n in m.nodes if n.kind in checking_kinds(m)]


def grid_row_line(lines, m, i, numw):
    """The painted line holding node i's grid row, or None when the
    windowing has it out of view.  Panel lines are excluded by requiring
    the row number (or the ○ badge) in the gutter."""
    nid = m.nodes[i].id
    tag_digit = f"{i + 1:>{numw}}"
    for ln in lines:
        if ln[numw + 1:numw + 1 + len(nid)] != nid:
            continue
        gutter = ln[:numw].strip()
        if gutter.startswith("○"):
            return ln
        if gutter.isdigit() and gutter == tag_digit.strip() or gutter == tag_digit:
            return ln
    return None


def style_at(text: Text, x: int) -> str:
    for span in text.spans:
        if span.start <= x < span.end:
            return str(span.style)
    return ""


def oracle_cell(m, rid: str, cid: str) -> str:
    """The independent cell oracle: strongest edge wins — ALERT-class
    (evidence missing or in cycle) before plain, then profile edge-type
    order; the D5 glyph table."""
    if rid == cid:
        return "▪"
    edges = [e for e in m.edges if (e.src == rid and e.dst == cid)
             or (e.src == cid and e.dst == rid)]
    if not edges:
        return "·"
    order = {t.name: i for i, t in enumerate(m.profile.edge_types)}

    def key(e):
        return (0 if (e.evidence_missing or e.in_cycle) else 1,
                order.get(e.type, 99))

    e = min(edges, key=key)
    if e.type == "verifies":
        return "!" if (e.evidence_missing or e.in_cycle) else "✓"
    if e.type == "binds":
        return "◐" if e.evidence_missing else "●"
    return {"refines": "•", "covers": "≡"}.get(e.type, "?")


def census_cells(rows, m) -> list[str]:
    """Census every visible (row, column) cell against the oracle."""
    lines = [r.plain for r in rows]
    numw, _idw, lw = gutter_layout(m)
    cols = checking_cols(m)
    bad = []
    for i, n in enumerate(m.nodes):
        ln = grid_row_line(lines, m, i, numw)
        if ln is None:
            continue
        for k, cn in enumerate(cols):
            got = ln[lw + k]
            want = oracle_cell(m, n.id, cn.id)
            if got != want:
                bad.append(f"{n.id} x {cn.id}: got {got!r} want {want!r}")
    return bad


# ---------------------------------------------------------------------------
# Layer 0 — the branchful helpers
# ---------------------------------------------------------------------------

def test_l0_window_centres_where_the_ends_allow(matrix_mod):
    """LLR-RVM.1.1: the window keeps `at` visible, centred where the ends
    allow, clamped at both edges (3+ paths)."""
    w = matrix_mod._window(60, 26, 30)
    assert len(w) == 26 and 30 in w
    assert w.start == 30 - 26 // 2  # centred: off = at - avail // 2
    assert matrix_mod._window(60, 26, 0).start == 0  # left end clamps
    tail = matrix_mod._window(60, 26, 59)
    assert tail.stop == 60 and 59 in tail  # right end clamps
    clamped = matrix_mod._window(60, 26, 50)
    assert clamped.start == 60 - 26 and 50 in clamped  # right-clamped
    assert len(matrix_mod._window(10, 26, 5)) == 10  # whole set, no pad


def test_l0_winning_edge_alert_before_plain(matrix_mod):
    """LLR-RVM.1.2: ALERT-class (evidence missing or in cycle) beats plain,
    then profile edge-type order decides."""
    plain_edge = Edge("TC-1", "LLR-T.1", "verifies")
    alert_miss = Edge("TC-2", "LLR-T.1", "verifies", evidence_missing=True)
    alert_cycle = Edge("TC-3", "LLR-T.1", "verifies", in_cycle=True)
    order = {t.name: i for i, t in enumerate(REQHARNESS.edge_types)}
    assert matrix_mod._winning_edge(
        [plain_edge, alert_miss], order) is alert_miss
    assert matrix_mod._winning_edge(
        [plain_edge, alert_cycle], order) is alert_cycle
    assert matrix_mod._winning_edge([plain_edge], order) is plain_edge
    assert matrix_mod._winning_edge([], order) is None
    # profile edge-type order: refines (index 0) beats verifies (index 2)
    refines = Edge("HLR-T.1", "LLR-T.1", "refines")
    assert matrix_mod._winning_edge(
        [plain_edge, refines], order) is refines


def test_l0_cell_glyph_table(matrix_mod):
    """LLR-RVM.1.2 + the frozen D5 table (OQ-M3)."""
    assert matrix_mod._cell(None) == ("·", darkside.WORDMARK)
    ok = Edge("TC-1", "LLR-T.1", "verifies")
    miss = Edge("TC-1", "LLR-T.1", "verifies", evidence_missing=True)
    assert matrix_mod._cell(ok) == ("✓", darkside.SAGE)
    assert matrix_mod._cell(miss) == ("!", darkside.ALERT)
    bound = Edge("AT-1", "TC-1", "binds")
    tagged = Edge("AT-1", "TC-1", "binds", evidence_missing=True)
    assert matrix_mod._cell(bound) == ("●", darkside.SAGE)
    assert matrix_mod._cell(tagged) == ("◐", darkside.WARN)
    assert matrix_mod._cell(Edge("A", "B", "refines")) == ("•", darkside.MUT)
    assert matrix_mod._cell(Edge("A", "B", "covers")) == ("≡", darkside.MUT)


def test_l0_rings_two_hop_same_direction_only(matrix_mod):
    """LLR-RVM.2.1: hop 2 only through a DRAWN hop-1 member of the same
    direction, each member once, edge input order (M-RVM-5's oracle)."""
    m = chain_map()
    up = matrix_mod._ring(m, "LLR-3", "up")
    assert [(nid, hop) for nid, hop, _p in up] == [("HLR-2", 1), ("US-1", 2)]
    down = matrix_mod._ring(m, "US-1", "down")
    assert [(nid, hop) for nid, hop, _p in down] == [("HLR-2", 1),
                                                     ("LLR-3", 2)]
    # each member once, even when two hop-1 members share a hop-2 target
    m2 = build_map(
        REQHARNESS,
        (Node("US-1", "US"), Node("US-2", "US"), Node("HLR-3", "HLR"),
         Node("LLR-4", "LLR")),
        (Edge("US-1", "HLR-3", "refines"), Edge("US-2", "HLR-3", "refines"),
         Edge("HLR-3", "LLR-4", "refines")),
        sourced=("US", "HLR", "LLR"),
    )
    up = matrix_mod._ring(m2, "LLR-4", "up")
    assert [(nid, hop) for nid, hop, _p in up] == [("HLR-3", 1),
                                                   ("US-1", 2), ("US-2", 2)]


def test_l0_toggle_vocabulary(matrix_mod):
    """COND-ARCH-1: `enter` is the matrix lens (word `panel lens`); the
    other kinds answer `""` and own no state here."""
    view = matrix_mod.build_view()
    assert view.toggle("c") == ""
    assert view.toggle("k") == ""
    assert view.toggle("enter") == "panel lens"
    assert view.toggle("enter") == ""  # flips back off
    assert view.toggle("enter") == "panel lens"
    assert view.name == "matrix"


def test_l0_row_count_is_the_node_axis(matrix_mod):
    """D1 (amended): the matrix cursor axis is the node list."""
    view = matrix_mod.build_view()
    m = binds_map()
    state = base.ViewState(relmap=m, notice=None, focus=m.nodes[0].id,
                           cursor=0, gaps=(), width=118, height=30)
    assert view.row_count(state) == len(m.nodes)
    empty_state = base.ViewState(relmap=None, notice="refused", focus=None,
                                 cursor=0, gaps=(), width=118, height=30)
    assert view.row_count(empty_state) == 0


# ---------------------------------------------------------------------------
# Layer A — white-box census arms over synthetic maps (TC-RM-04…09)
# ---------------------------------------------------------------------------

def test_notice_paints_only_the_refusal_line(matrix_mod):
    """The renderer's notice obligation (D1): when `state.notice` is set
    the fixed refusal line IS the body — through the one label sink, no
    body content beside it."""
    view = fresh_view(matrix_mod)
    notice = "relmap: canon unavailable (file not found) — refusing to map"
    state = base.ViewState(relmap=None, notice=notice, focus=None, cursor=0,
                           gaps=(), width=60, height=12)
    rows = view.paint(state)
    assert len(rows) == 12
    body = [r for r in rows if r.plain.strip()]
    assert len(body) == 1
    assert notice[:59] in body[0].plain  # cut to the viewport through fit
    assert body[0].cell_len <= 60
    for r in rows:
        assert r.cell_len <= 60


def test_empty_map_paints_no_node_on_record(matrix_mod):
    """LLR-RVM.3.2 / AT-130 boundary: zero nodes -> the declared empty
    state on the grid AND the lens (which prints nothing else)."""
    view = fresh_view(matrix_mod)
    m = build_map(REQHARNESS, (), (), sourced=())
    rows = view.paint(view_row_state(m, None))
    text = plain(rows)
    assert text.count("no node on record") == 2  # grid side + lens side
    assert "what feeds it" not in text


def test_unknown_focus_paints_the_empty_state_without_raising(matrix_mod):
    """LLR-RVM.3.2 / M-RVM-9: a selection naming no node on the map must
    not raise; it paints the same declared state."""
    view = fresh_view(matrix_mod)
    m = demo_map()
    rows = view.paint(view_row_state(m, "NO-SUCH-NODE"))
    assert plain(rows).count("no node on record") == 2


def test_relates_to_nothing_when_the_selection_is_isolated(matrix_mod):
    """LLR-RVM.3.2: no up and no down members -> `╌╌╌ relates to nothing`
    in ALERT; a one-sided empty ring keeps its own hatch line."""
    m = build_map(
        REQHARNESS,
        (Node("HLR-I.1", "HLR", "parent"),
         Node("LLR-I.1.1", "LLR", "kid"),
         Node("HLR-I.2", "HLR", "lonely")),
        (Edge("HLR-I.1", "LLR-I.1.1", "refines"),),
        sourced=("HLR", "LLR"),
    )
    view = fresh_view(matrix_mod)
    rows = paint(view, m, focus="HLR-I.2")  # the isolated node
    text = plain(rows)
    assert "what feeds it ←" in text
    assert "a change reaches →" in text
    assert text.count("╌╌╌ relates to nothing") == 1
    alert = [r for r in rows if "╌╌╌ relates to nothing" in r.plain][0]
    x = alert.plain.index("╌╌╌ relates to nothing")
    assert darkside.ALERT in style_at(alert, x)

    rows = paint(view, m, focus="LLR-I.1.1")  # has an up, no down
    text = plain(rows)
    assert "↑1 refines HLR-I.1" in text
    assert text.count("╌╌╌ relates to nothing") == 1
    # the up ring is not empty, so the root hatch line is NOT painted
    assert "nothing feeds it" not in text

    rows = paint(view, m, focus="HLR-I.1")  # no up, one down (the root)
    text = plain(rows)
    assert "↓1 refines LLR-I.1.1" in text
    assert text.count("╌╌╌ root — nothing feeds it") == 1
    assert "╌╌╌ relates to nothing" not in text
    root_line = [r for r in rows if "╌╌╌ root — nothing feeds it" in r.plain][0]
    x = root_line.plain.index("╌╌╌ root — nothing feeds it")
    assert darkside.MUT in style_at(root_line, x)


def test_degenerate_height_flap_never_reads_an_empty_window(matrix_mod):
    """review-inc003 F2: below the 6-row body budget (`_GRID_TOP` 4 + the
    flap/legend reservation) the row window is EMPTY and the flap must not
    read `01–00 / N` — the guard clamps the window end to at least 1.
    Cosmetic-only at terminal heights no contract size reaches (the C10
    sweep's smallest arm is (40,12)); the painted frame must not raise."""
    m = demo_map()
    view = fresh_view(matrix_mod)
    # h == 6 is the one visible degenerate height: the row budget
    # (`_GRID_TOP` 4 + flap/legend reservation 2) is exactly 0, the window
    # is empty, and the flap paints one row above the legend.
    rows = paint(view, m, focus="HLR-DEMO.1", height=6)
    text = plain(rows)
    assert "01–00" not in text
    assert f"/ {len(m.nodes)}" in text


def test_window_declarations_keep_the_selection_visible(matrix_mod):
    """LLR-RVM.1.1 + LLR-RVM.1.3 / M-RVM-1: with 60 rows over a 30-row
    viewport the selected row below the fold stays painted and the flap
    declares the window in words."""
    m = wide_map(60)
    view = fresh_view(matrix_mod)
    focus = m.nodes[45].id
    rows = paint(view, m, focus=focus)
    text = plain(rows)
    assert "LLR-W.1.46" in text  # the selected row is on screen
    match = re.search(r"\d{2}–\d{2} / 61", text)
    assert match, f"row window declaration missing: {text!r}"
    start, stop = int(match.group(0)[:2]), int(match.group(0)[3:5])
    assert start <= 46 <= stop
    assert stop - start <= 27  # windowed to the viewport, not the whole set


def test_columns_out_of_view_and_the_two_digit_ruler(matrix_mod):
    """LLR-RVM.1.3: the two-digit ruler (tens over ones) above the grid
    and the hidden column count declared as `NN out of view`."""
    m = tc_map(80)  # 80 test-side columns over the 64-cell grid span
    view = fresh_view(matrix_mod)
    rows = paint(view, m, focus="LLR-C.1.1")
    text = plain(rows)
    assert "out of view" in text
    match = re.search(r"(\d{2}) out of view", text)
    hidden = int(match.group(1))
    numw, _idw, lw = gutter_layout(m)
    cols = checking_cols(m)
    grid_ln = grid_row_line([r.plain for r in rows], m, 1, numw)
    left_end = 118 - min(40, max(30, 118 // 3)) - 2  # the grid span only
    visible_cols = sum(
        1 for k in range(len(cols))
        if grid_ln is not None and lw + k < left_end
        and grid_ln[lw + k] != " "
    )
    assert hidden + visible_cols == 80
    # the ruler: ones digits on the row above the grid for every column
    ones = rows[GRID_TOP - 1].plain
    for k in range(visible_cols):
        assert ones[lw + k].isdigit()


def test_no_test_columns_declaration_and_skeleton_honesty(matrix_mod):
    """LLR-RVM.3.1 / AT-130 + M-RVM-8: no test-side nodes -> the verbatim
    declaration where the column header would sit, NO column ruler, and
    zero phantom test-side cells (no `·` block to the right of the
    gutter)."""
    m = build_map(
        REQHARNESS,
        (Node("HLR-S.1", "HLR", "parent"), Node("LLR-S.1.1", "LLR", "kid")),
        (Edge("HLR-S.1", "LLR-S.1.1", "refines"),),
        sourced=("HLR", "LLR"),
    )
    view = fresh_view(matrix_mod)
    rows = paint(view, m, focus="HLR-S.1")
    text = plain(rows)
    assert NO_TEST_COLUMNS in text
    assert "out of view" not in text
    numw, _idw, lw = gutter_layout(m)
    left_end = 118 - min(40, max(30, 118 // 3)) - 2  # the grid region only
    for r in rows[GRID_TOP:-1]:  # the legend row legitimately names `·`
        body = r.plain[lw:left_end]
        for glyph in "·▪✓●◐○≡•!":
            assert glyph not in body, (
                f"phantom column block painted: {r.plain!r}")
    # the census: no US/AT/TC token the map does not contain
    for tok in ("US-", "AT-", "TC-"):
        assert tok not in text


def test_geometry_audit_sweep_is_clean_at_every_size(matrix_mod,
                                                     monkeypatch):
    """LLR-RVM.4.1 / TC-RM-09: every canvas the renderer constructs carries
    the audit mapping (the wrapper below injects a sink into EVERY
    construction) and accumulates zero clip/overprint events; rows stay
    within the viewport at the 118/87 reference pair and a degenerate
    narrow size."""
    sinks = []
    real_init = Canvas.__init__

    def audited_init(self, w, h, tones=(), fallback="", audit=None):
        sink = {"clip": [], "overprint": []}
        sinks.append(sink)
        real_init(self, w, h, tones=tones, fallback=fallback, audit=sink)

    monkeypatch.setattr(Canvas, "__init__", audited_init)
    maps = [demo_map(), binds_map(), chain_map(), wide_map(60), tc_map(20)]
    for m in maps:
        for w, h in ((118, 30), (87, 30), (40, 12)):
            view = fresh_view(matrix_mod)
            rows = paint(view, m, focus=m.nodes[0].id, width=w, height=h)
            assert len(rows) <= h
            for r in rows:
                assert r.cell_len <= w, f"{w}x{h}: overwide row {r.plain!r}"
    assert sinks, "the renderer constructed no canvas at all"
    for sink in sinks:
        assert not sink["clip"], f"unexplained clip: {sink['clip']}"
        assert not sink["overprint"], (
            f"unexplained overprint: {sink['overprint']}")


def test_hop2_rows_fold_below_the_sixty_cell_viewport(matrix_mod):
    """LLR-RVM.2.1: at lens widths below 60 cells the hop-2 rows fold
    away leaving `↑1`/centre/`↓1`, and the folded members are counted as
    `+NN more` — never dropped silently."""
    m = chain_map()
    wide = fresh_view(matrix_mod)
    text = plain(paint(wide, m, focus="US-1", width=160, height=30))
    assert "↓1 refines HLR-2" in text
    assert "↓2 refines LLR-3" in text
    narrow = fresh_view(matrix_mod)
    text = plain(paint(narrow, m, focus="US-1", width=50, height=30))
    assert "↓1 refines HLR-2" in text
    assert "↓2" not in text
    assert "+01 more" in text  # the folded hop-2 member is counted


def test_legend_line_names_the_evidence_glyphs(matrix_mod):
    """LLR-RVM.1.3 / AT-133: the legend row, verbatim, cut to the
    viewport width when it does not fit."""
    m = binds_map()
    view = fresh_view(matrix_mod)
    rows = paint(view, m, focus="HLR-T.1")
    assert rows[-1].plain.strip() == LEGEND
    rows = paint(view, m, focus="HLR-T.1", width=40, height=12)
    last = rows[-1].plain
    assert last.strip().startswith("✓ verifies · ! evidence missing")
    assert last.rstrip().endswith("…")
    assert Text(last).cell_len <= 40


def test_hostile_title_renders_on_one_row_through_the_sink(matrix_mod):
    """LLR-RVM.4.2 / AT-134 unit arm (C8/C-17): brackets literal, ESC and
    U+202E coerced to U+FFFD, everything on ONE row."""
    m = build_map(
        REQHARNESS,
        (Node("HLR-H.1", "HLR",
              "hostile [bold]title[/bold] with \x1b ESC and \u202e RLO"),
         Node("LLR-H.1.1", "LLR", "kid")),
        (Edge("HLR-H.1", "LLR-H.1.1", "refines"),),
        sourced=("HLR", "LLR"),
    )
    view = fresh_view(matrix_mod)
    rows = paint(view, m, focus="HLR-H.1")
    text = plain(rows)
    assert "hostile [bold]title[/bold]" in text  # brackets literal
    assert "�" in text  # ESC and U+202E coerced to U+FFFD
    assert "\x1b" not in text
    assert "\u202e" not in text
    row = next(r for r in rows if "hostile [bold]" in r.plain)
    x = row.plain.index("hostile [bold]")
    assert "bold" not in style_at(row, x), (
        "the payload forged a bold style run — markup was parsed")


def test_cell_census_on_the_synthetic_binds_map(matrix_mod):
    """AT-133 / LLR-RVM.1.2: every (row, column) cell against the
    independent oracle; the ○ badge in the gutter for an AT node with no
    binds edge — ALERT when open, MUT when closed."""
    m = binds_map()
    view = fresh_view(matrix_mod)
    rows = paint(view, m, focus="HLR-T.1")
    assert census_cells(rows, m) == []
    numw, _idw, lw = gutter_layout(m)
    lines = [r.plain for r in rows]
    # the two unbound AT rows bear the ○ badge, in the gutter
    open_row = next(r for r in rows
                    if r.plain[numw + 1:].startswith("AT-1"))
    closed_row = next(r for r in rows
                      if r.plain[numw + 1:].startswith("AT-4"))
    assert open_row.plain[0] == "○"
    assert closed_row.plain[0] == "○"
    assert darkside.ALERT in style_at(open_row, 0)
    assert darkside.MUT in style_at(closed_row, 0)
    # bound AT rows carry no badge
    bound_row = next(r for r in rows
                     if r.plain[numw + 1:].startswith("AT-2"))
    assert bound_row.plain[0] != "○"
    # evidence tones: ● on file SAGE, ◐ tagged WARN (M-RVM-3's arm)
    col_ids = [c.id for c in checking_cols(m)]
    x_tagged = lw + col_ids.index("TC-1")
    tagged_row = next(r for r in rows
                      if r.plain[numw + 1:].startswith("AT-3"))
    assert tagged_row.plain[x_tagged] == "◐"
    assert darkside.WARN in style_at(tagged_row, x_tagged)
    x_bound = lw + col_ids.index("TC-2")
    assert bound_row.plain[x_bound] == "●"
    assert darkside.SAGE in style_at(bound_row, x_bound)


def test_lens_rows_carry_the_edge_evidence_glyphs(matrix_mod):
    """LLR-RVM.2.1 / AT-133: verifies lens rows carry `✓`/`!` per
    `Edge.evidence_missing`; hop markers and Darkside-cased edge types."""
    m = binds_map()
    view = fresh_view(matrix_mod)
    text = plain(paint(view, m, focus="LLR-T.1.1"))
    assert "↑1 refines HLR-T.1" in text
    assert "↓1 verifies TC-1 !" in text   # evidence_missing -> ALERT glyph
    assert "↓1 verifies TC-2 ✓" in text   # evidence on file


def test_summary_and_gauge_against_the_oracle(matrix_mod):
    """LLR-RVM.2.2 / AT-131: `change <id> reaches N nodes` over
    `hop 1: n direct · hop 2: m chained`; the gauge fill is proportional
    to reach against the greatest reach on the map."""
    m = chain_map()
    view = fresh_view(matrix_mod)
    rows = paint(view, m, focus="US-1")
    text = plain(rows)
    assert "change US-1 reaches 3 nodes" in text  # HLR-2, LLR-3, TC-9
    assert "hop 1: 1 direct · hop 2: 1 chained" in text
    gauge = next(r for r in rows if " reach  " in r.plain)
    assert "03" in gauge.plain
    filled = gauge.plain.count("█")
    track = gauge.plain.count("░")
    assert filled == 10 and track == 0  # 3 of 3 against the map max
    # a node with 2 of the map max 3 fills 7 of 10 cells
    rows = paint(view, m, focus="HLR-2")
    gauge = next(r for r in rows if " reach  " in r.plain)
    assert gauge.plain.count("█") == 7 and gauge.plain.count("░") == 3


def test_reach_not_computed_renders_honestly(matrix_mod):
    """LLR-RVM.2.2 / AT-132 + M-RVM-7: a spent visit budget -> `not
    computed` in WARN with an EMPTY gauge — never a fabricated number —
    while the hop counts and the dimming source stay numeric."""
    m = chain_map()
    m._visits = VISIT_BUDGET  # exhaust the shared budget in-test
    m._reach_memo.clear()
    view = fresh_view(matrix_mod)
    rows = paint(view, m, focus="US-1")
    text = plain(rows)
    assert "not computed" in text
    assert not re.search(r"reaches \d+", text)
    line = next(r for r in rows if "not computed" in r.plain)
    x = line.plain.index("not computed")
    assert darkside.WARN in style_at(line, x)
    gauge = next(r for r in rows if " reach  " in r.plain)
    assert "░" in gauge.plain and "█" not in gauge.plain
    assert "hop 1: 1 direct · hop 2: 1 chained" in text  # hops unaffected


def test_neighbourhood_is_called_for_the_focused_node_only(matrix_mod,
                                                            monkeypatch):
    """LLR-RVM.2.3 / M-RVM-6: one `neighbourhood(selection, 2)` call per
    paint while the lens focus is on — never one per painted row — and
    none while the lens is off."""
    from mapper.relmap.model import RelMap
    m = wide_map(60)
    calls = []
    real = RelMap.neighbourhood

    def counting(self, node_id, hops):
        calls.append(node_id)
        return real(self, node_id, hops)

    monkeypatch.setattr(RelMap, "neighbourhood", counting)
    view = fresh_view(matrix_mod, lens_on=True)
    paint(view, m, focus="LLR-W.1.40")
    assert calls == ["LLR-W.1.40"]  # one call, for the focused node only
    calls.clear()
    view = fresh_view(matrix_mod)  # lens off
    paint(view, m, focus="LLR-W.1.40")
    assert calls == []


def demo_map():
    return build_map(
        REQHARNESS,
        (Node("HLR-DEMO.1", "HLR", "parent one"),
         Node("HLR-DEMO.2", "HLR", "parent two"),
         Node("LLR-DEMO.1.1", "LLR", "child"),
         Node("LLR-DEMO.1.2", "LLR", "child"),
         Node("LLR-DEMO.2.1", "LLR", "child"),
         Node("LLR-DEMO.2.2", "LLR", "child")),
        (Edge("HLR-DEMO.1", "LLR-DEMO.1.1", "refines"),
         Edge("HLR-DEMO.1", "LLR-DEMO.1.2", "refines"),
         Edge("HLR-DEMO.2", "LLR-DEMO.2.1", "refines"),
         Edge("HLR-DEMO.2", "LLR-DEMO.2.2", "refines")),
        sourced=("HLR", "LLR"))


def view_row_state(m, focus):
    idx = {n.id: i for i, n in enumerate(m.nodes)}
    return base.ViewState(relmap=m, notice=None, focus=focus,
                          cursor=idx.get(focus, 0), gaps=(),
                          width=118, height=30)


# ---------------------------------------------------------------------------
# Layer B — AT-130…134 through the real app, real keys (C-16)
# ---------------------------------------------------------------------------

def _painted_runs(screen):
    return [[(seg.text, str(seg.style)) for seg in strip]
            for strip in screen._compositor.render_strips()]  # noqa: SLF001


def _frame_lines(screen):
    return ["".join(t for t, _ in r) for r in _painted_runs(screen)]


def _style_at_runs(runs, x):
    pos = 0
    for text, style in runs:
        if pos <= x < pos + len(text):
            return style
        pos += len(text)
    return ""


def _canvas_top(lines):
    return next(i for i, ln in enumerate(lines) if "row → col" in ln)


async def _open_relmap(app, pilot, workspace, name="demo"):
    screen = RelMapScreen(name, workspace,
                          descriptor=default_descriptor())
    app.push_screen(screen)
    await pilot.pause()
    await pilot.pause()
    return screen


def _audit_wrapper(monkeypatch):
    sinks = []
    real_init = Canvas.__init__

    def audited_init(self, w, h, tones=(), fallback="", audit=None):
        sink = {"clip": [], "overprint": []}
        sinks.append(sink)
        real_init(self, w, h, tones=tones, fallback=fallback, audit=sink)

    monkeypatch.setattr(Canvas, "__init__", audited_init)
    return sinks


def _assert_audit_clean(sinks):
    for sink in sinks:
        assert not sink["clip"], f"unexplained clip: {sink['clip']}"
        assert not sink["overprint"], (
            f"unexplained overprint: {sink['overprint']}")


def _assert_dimming_census(screen, m, lens_on: bool):
    """AT-131/132's black-box census: FAINT (Rich `dim`) runs on the grid
    row labels OUTSIDE the selection's 2-neighbourhood, none inside —
    and none anywhere while the lens is off."""
    runs = _painted_runs(screen)
    lines = ["".join(t for t, _ in r) for r in runs]
    top = _canvas_top(lines)
    numw = max(2, len(str(len(m.nodes))))
    nbh = m.neighbourhood(screen.focus, 2) if lens_on else frozenset()
    found = 0
    for i, n in enumerate(m.nodes):
        ln = grid_row_line(lines, m, i, numw)
        if ln is None:
            continue
        y = lines.index(ln)
        # only grid rows inside the canvas region
        if not (top <= y < top + 30):
            continue
        found += 1
        style = _style_at_runs(runs[y], numw + 1)
        if lens_on and n.id not in nbh:
            assert "dim" in style, (
                f"{n.id} is outside the 2-neighbourhood but its label is "
                f"not dimmed: {style!r}")
        else:
            assert "dim" not in style, (
                f"{n.id} is inside the neighbourhood (or the lens is off) "
                f"but its label is dimmed: {style!r}")
    assert found >= 2, "the census found no grid rows"


async def test_f5_at_driver_injection_reaches_home(tmp_path):
    """Fork precondition F-5 re-check at lane entry: the fixture-workspace
    injection reaches Home and lists the seeded map (the seam the shell
    lane completes with relation-row routing in Inc-6)."""
    (tmp_path / "seed.mmd").write_text("graph TD\n  A --> B\n",
                                       encoding="utf-8")
    (tmp_path / "seed_nodos.yml").write_text("nodos: {}\n", encoding="utf-8")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        from mapper.screens.home import HomeScreen
        assert isinstance(app.screen, HomeScreen)
        painted = "\n".join(
            "".join(seg.text for seg in strip)
            for strip in app.screen._compositor.render_strips())  # noqa: SLF001
        assert "seed" in painted


async def test_at130_matrix_opens_on_the_honest_skeleton(tmp_path):
    """AT-130 (118x34): the live skeleton derives through the real app;
    `2`/`1` leave and re-enter the matrix; the selection moves down to a
    real LLR (non-default); the declaration, the lens heads, the `↑1
    refines` oracle row and the `NN–NN / 303` window are all painted."""
    (tmp_path / "REQUIREMENTS.md").write_text(
        LIVE_CANON.read_text(encoding="utf-8"), encoding="utf-8")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        screen = await _open_relmap(app, pilot, tmp_path, "live")
        await pilot.press("2")
        await pilot.press("1")
        target = next(
            i for i, n in enumerate(screen.relmap.nodes)
            if n.kind == "LLR" and screen.relmap.up(n.id))
        for _ in range(target):
            await pilot.press("down")
        await pilot.pause()
        text = "\n".join(_frame_lines(screen))
        assert screen.focus == screen.relmap.nodes[target].id
        assert NO_TEST_COLUMNS in text
        assert "what feeds it ←" in text
        assert "a change reaches →" in text
        assert re.search(r"\d{2}–\d{2} / 303", text), (
            f"the live row window declaration is missing: {text!r}")
        parent = screen.relmap.up(screen.focus)[0]
        assert f"↑1 refines {parent}" in text
        # the selection's row is visible on screen
        numw = max(2, len(str(len(screen.relmap.nodes))))
        assert grid_row_line(_frame_lines(screen), screen.relmap,
                             target, numw) is not None


async def test_at130_87_column_boundary(tmp_path, monkeypatch):
    """AT-130's 87x34 arm: the declaration and the lens rows stay inside
    the panel — zero unexplained audit events at the boundary size."""
    (tmp_path / "REQUIREMENTS.md").write_text(demo_canon(), encoding="utf-8")
    sinks = _audit_wrapper(monkeypatch)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(87, 34)) as pilot:
        screen = await _open_relmap(app, pilot, tmp_path)
        for _ in range(3):
            await pilot.press("down")
        await pilot.pause()
        lines = _frame_lines(screen)
        text = "\n".join(lines)
        assert "no test columns yet" in text
        # the declaration stays in the left (grid) region, clear of the
        # panel (the panel title shares the frame row — measure only the
        # grid span)
        decl = next(ln for ln in lines if "no test columns yet" in ln)
        grid_span = decl[:87 - 30]
        last_cell = max(i for i, ch in enumerate(grid_span) if ch != " ")
        assert last_cell < 87 - 30, "the declaration bleeds into the panel"
        # the lens head lives inside the right-hand panel
        lens_line = next(ln for ln in lines if "what feeds it ←" in ln)
        assert lens_line.index("what feeds it ←") >= 87 - 30
        for ln in lines:
            assert Text(ln).cell_len <= 87
        assert screen.focus == screen.relmap.nodes[3].id  # non-default
    _assert_audit_clean(sinks)


async def test_at130_zero_node_map_boundary(tmp_path):
    """AT-130's boundary arm through the real app: a canon with no
    requirement rows derives an empty map and the matrix declares it."""
    (tmp_path / "REQUIREMENTS.md").write_text(
        "a canon with no table at all\n", encoding="utf-8")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        screen = await _open_relmap(app, pilot, tmp_path)
        await pilot.pause()
        assert screen.relmap is not None and not screen.relmap.nodes
        text = "\n".join(_frame_lines(screen))
        assert "no node on record" in text


async def test_at131_lens_summary_hop_counts_and_dimming(tmp_path,
                                                        monkeypatch):
    """AT-131 (118x34): an HLR selected at a non-default position; the
    summary, the hop counts, the gauge row; `enter` focuses the lens —
    the crumb shows `panel lens` — and the painted frame dims exactly the
    grid labels outside the selection's 2-neighbourhood."""
    (tmp_path / "REQUIREMENTS.md").write_text(demo_canon(), encoding="utf-8")
    sinks = _audit_wrapper(monkeypatch)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        screen = await _open_relmap(app, pilot, tmp_path)
        await pilot.press("down")  # HLR-DEMO.2, non-default
        await pilot.pause()
        m = screen.relmap
        focus = screen.focus
        assert focus == "HLR-DEMO.2"
        text = "\n".join(_frame_lines(screen))
        assert f"change {focus} reaches 2 nodes" in text
        assert "hop 1: 2 direct · hop 2: 0 chained" in text
        gauge = next(ln for ln in _frame_lines(screen) if " reach " in ln)
        assert "02" in gauge
        for child in m.down(focus):
            assert f"↓1 refines {child}" in text
        # lens off: nothing is dimmed
        _assert_dimming_census(screen, m, lens_on=False)
        await pilot.press("enter")
        await pilot.pause()
        assert "matrix · panel lens" in "\n".join(_frame_lines(screen))
        _assert_dimming_census(screen, m, lens_on=True)
    _assert_audit_clean(sinks)


async def test_at131_87_column_boundary(tmp_path, monkeypatch):
    """AT-131's 87x34 boundary arm: the summary line is cut INSIDE the
    panel with zero unexplained audit events."""
    (tmp_path / "REQUIREMENTS.md").write_text(demo_canon(), encoding="utf-8")
    sinks = _audit_wrapper(monkeypatch)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(87, 34)) as pilot:
        screen = await _open_relmap(app, pilot, tmp_path)
        await pilot.press("down")
        await pilot.pause()
        lines = _frame_lines(screen)
        summary = next(ln for ln in lines
                       if " reaches" in ln[57:] and "reaches →" not in ln)
        assert summary.rstrip().endswith("…")  # cut inside the panel
        assert f"change {screen.focus} reaches" in summary
        for ln in lines:
            assert Text(ln).cell_len <= 87
    _assert_audit_clean(sinks)


async def test_at132_budget_spent_renders_not_computed(tmp_path):
    """AT-132: the shared visit budget exhausted in-test; the lens count
    renders `not computed` with no fabricated digits; the dimming census
    is unchanged under the spent budget."""
    (tmp_path / "REQUIREMENTS.md").write_text(demo_canon(), encoding="utf-8")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        screen = await _open_relmap(app, pilot, tmp_path)
        screen.relmap._visits = VISIT_BUDGET
        screen.relmap._reach_memo.clear()
        await pilot.press("down")
        await pilot.pause()
        text = "\n".join(_frame_lines(screen))
        assert "not computed" in text
        assert not re.search(r"reaches \d+", text)
        await pilot.press("enter")
        await pilot.pause()
        _assert_dimming_census(screen, screen.relmap, lens_on=True)


async def test_at133_binds_cell_census_through_real_keys(tmp_path):
    """AT-133: the synthetic binds map injected in-process (the canon
    cannot source AT/TC nodes); REAL keys move the selection across the
    bound and unbound AT rows (non-default); the cell census, the legend,
    the badge tones and the verifies lens glyphs are asserted on the
    painted surface."""
    (tmp_path / "REQUIREMENTS.md").write_text(demo_canon(), encoding="utf-8")
    app = MapperApp(tmp_path)
    smap = binds_map()
    async with app.run_test(size=(118, 34)) as pilot:
        screen = await _open_relmap(app, pilot, tmp_path)
        screen.relmap = smap
        screen.focus = smap.nodes[0].id
        screen._cursors = {n: 0 for n in base.VIEW_NAMES}  # noqa: SLF001
        await pilot.pause()
        # move onto the first LLR (verifies lens rows) then to an AT row
        await pilot.press("down")
        await pilot.pause()
        assert screen.focus == "LLR-T.1.1"
        text = "\n".join(_frame_lines(screen))
        assert LEGEND in text
        assert "↓1 verifies TC-1 !" in text
        assert "↓1 verifies TC-2 ✓" in text
        first_at = next(i for i, n in enumerate(smap.nodes)
                        if n.kind == "AT")
        for _ in range(first_at - 1):
            await pilot.press("down")
        await pilot.pause()
        assert screen.focus == smap.nodes[first_at].id
        # the full cell census against the oracle, on the exported text
        lines = _frame_lines(screen)
        numw, _idw, lw = gutter_layout(smap)
        for i, n in enumerate(smap.nodes):
            ln = grid_row_line(lines, smap, i, numw)
            assert ln is not None, f"row {n.id} is not painted"
            for k, cn in enumerate(checking_cols(smap)):
                got = ln[lw + k]
                want = oracle_cell(smap, n.id, cn.id)
                assert got == want, f"{n.id} x {cn.id}: {got!r} != {want!r}"
        # badge tones on the painted frame: ALERT (open) vs MUT (closed).
        # Move the selection off the badged rows first — a selected row
        # carries the focus tint across its gutter by design.
        await pilot.press("up")
        await pilot.pause()
        lines = _frame_lines(screen)
        runs = _painted_runs(screen)
        for nid, tone in (("AT-1", darkside.ALERT), ("AT-4", darkside.MUT)):
            ln = grid_row_line(lines, smap,
                               next(i for i, n in enumerate(smap.nodes)
                                    if n.id == nid), numw)
            y = lines.index(ln)
            style = _style_at_runs(runs[y], 0)
            assert tone in style, f"{nid} badge style {style!r} lacks {tone}"


async def test_at134_hostile_payload_on_the_live_surface(tmp_path,
                                                        monkeypatch):
    """AT-134: the hostile canon through the real app; the hostile node
    selected after real key moves; the payload renders literally — the
    plained substring is present, zero raw ESC bytes, no forged style,
    zero unexplained audit events."""
    hostile = canon(
        row("HLR-[bold]HOST[/bold].1", statement=(
            "hostile [bold]t[/bold] \x1b\u202e\u0007xyz")),
        row("LLR-HOST.1.1", statement="child"),
    )
    (tmp_path / "REQUIREMENTS.md").write_text(hostile, encoding="utf-8")
    sinks = _audit_wrapper(monkeypatch)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        screen = await _open_relmap(app, pilot, tmp_path)
        await pilot.press("down")
        await pilot.press("up")  # back on the hostile node, keys moved
        await pilot.pause()
        assert screen.focus == "HLR-[bold]HOST[/bold].1"
        text = "\n".join(_frame_lines(screen))
        # the coerced payload rides on ONE row, controls as U+FFFD
        assert "hostile [bold]t[/bold] ���xyz" in text
        assert "\x1b" not in text
        assert "\u202e" not in text
        # the printable prefix of the cut id renders literally in the gutter
        assert "HLR-[bold]H" in text
        # no forged style: the run carrying the payload's [bold] has no
        # bold attribute (checked on the panel title line, which is never
        # part of the focus tint)
        runs = _painted_runs(screen)
        lines = _frame_lines(screen)
        y = next(i for i, ln in enumerate(lines)
                 if "hostile [bold]t[/bold]" in ln)
        x = lines[y].index("hostile [bold]t[/bold]")
        style = _style_at_runs(runs[y], x)
        assert "bold" not in style, f"the payload forged a style: {style!r}"
    _assert_audit_clean(sinks)


async def test_at134_lf_tab_payload_renders_on_one_row(tmp_path):
    """AT-134's LF/TAB arm (COND-SEC-1, P12): a title carrying an
    embedded LF + TAB coerces to single spaces and renders on ONE row —
    the hostile text cannot forge a second row."""
    (tmp_path / "REQUIREMENTS.md").write_text(demo_canon(), encoding="utf-8")
    app = MapperApp(tmp_path)
    smap = lf_tab_map()
    async with app.run_test(size=(118, 34)) as pilot:
        screen = await _open_relmap(app, pilot, tmp_path)
        screen.relmap = smap
        screen.focus = smap.nodes[0].id
        screen._cursors = {n: 0 for n in base.VIEW_NAMES}  # noqa: SLF001
        await pilot.pause()
        await pilot.press("down")
        await pilot.press("up")
        await pilot.pause()
        assert screen.focus == "HLR-LF.1"
        text = "\n".join(_frame_lines(screen))
        # the coerced payload rides on exactly ONE row of the screen
        carriers = [ln for ln in text.splitlines()
                    if "left right next" in ln]
        assert len(carriers) == 1, (
            f"the payload forged extra rows: {carriers!r}")
        assert "\t" not in text
