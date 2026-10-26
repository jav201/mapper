"""The ranked-gaps renderer — lane L4, increment 004 (batch `2026-10-25-relmap-r2-batch`).

Unit arms (Layer A) over the frozen D1 surface plus the AT arms (Layer B) that
drive the REAL app with REAL keys (C-16): AT-135 (ranked screen + cursor),
AT-136 (`k` by-kind, byte-identical toggle-back, the per-band membership
oracle answering LLR-RVG.1.5's flagged misalignment), AT-138 honesty arms and
AT-139 (hostile canon text).  The scale sweep (AT-137) lives in
`tests/test_relmap_scalecheck.py`.

Fixtures are built INLINE per ARC-05: synthetic `build_map` maps, plus canon
workspaces through the real adapter where the AT-driver path is the point.
The renderer is imported through the wiring convention (`base.build_view`),
so a missing module is the honest RED shape; the source census arms read
`mapper.screens.relmap.gaps` directly.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import mapper.screens.relmap.gaps as gaps_mod
from mapper import darkside
from mapper.app import MapperApp
from mapper.relmap.adapter import derive_reqharness_map
from mapper.relmap.descriptor import default_descriptor
from mapper.relmap.gaps import Gap, detect_gaps, rank_gaps
from mapper.relmap.model import Edge, Node, build_map
from mapper.relmap.profile import REQHARNESS, SEVERITIES, EdgeType, GapRow, Profile
from mapper.screens.relmap import base
from mapper.screens.relmap import RelMapScreen

# ---------------------------------------------------------------------------
# Inline fixtures (ARC-05 — the shared fixture module is trunk-only)
# ---------------------------------------------------------------------------

HEADER = "| Id | Status | Statement |\n|---|---|---|\n"


def canon_row(row_id: str, statement: str = "text") -> str:
    return f"| {row_id} | active | {statement} |"


SNAPSHOT_TITLES = {
    "HLR-A.2": "the alpha record",
    "HLR-B.3": "the beta record",
    "HLR-CAN.1": "the canon record",
    "HLR-C.4": "the gamma record",
    "HLR-D.5": "the delta record",
    "HLR-REPAIR.1": "the repair record",
    "HLR-E.6": "the epsilon record",
}


def snapshot_canon() -> str:
    """The R1 snapshot shape: 7 `hlr without llr` gaps, exactly two qualified.

    Ranked order is canon (input) order: HLR-CAN.1 lands on rank 03 and
    HLR-REPAIR.1 on rank 06; the unlinked orphan LLRs qualify exactly those
    two with a count of two.
    """
    return HEADER + "".join(
        r + "\n"
        for r in (
            canon_row("HLR-A.2", SNAPSHOT_TITLES["HLR-A.2"]),
            canon_row("HLR-B.3", SNAPSHOT_TITLES["HLR-B.3"]),
            canon_row("HLR-CAN.1", SNAPSHOT_TITLES["HLR-CAN.1"]),
            canon_row("HLR-C.4", SNAPSHOT_TITLES["HLR-C.4"]),
            canon_row("HLR-D.5", SNAPSHOT_TITLES["HLR-D.5"]),
            canon_row("HLR-REPAIR.1", SNAPSHOT_TITLES["HLR-REPAIR.1"]),
            canon_row("HLR-E.6", SNAPSHOT_TITLES["HLR-E.6"]),
            # unlinked orphans: their rule-D-1 stems (CAN/REPAIR) qualify the
            # two dotted HLRs above with a count of two each
            canon_row("LLR-CAN.9", "orphan near CAN"),
            canon_row("LLR-CAN.10", "orphan near CAN"),
            canon_row("LLR-REPAIR.9", "orphan near REPAIR"),
            canon_row("LLR-REPAIR.10", "orphan near REPAIR"),
        )
    )


SNAPSHOT_IDS = list(SNAPSHOT_TITLES)
QUALIFIED = {"HLR-CAN.1", "HLR-REPAIR.1"}
QUALIFIER = " (canon rows near this id could not be parsed or linked: 2)"
KIND = "hlr without llr"


def derive_snapshot(tmp_path):
    """The snapshot map + ranked gaps through the real adapter (read-only)."""
    (tmp_path / "REQUIREMENTS.md").write_text(snapshot_canon(), encoding="utf-8")
    derivation = derive_reqharness_map(tmp_path, default_descriptor())
    ranked, not_computed = rank_gaps(
        derivation.map, detect_gaps(derivation.map), None
    )
    return derivation.map, ranked, not_computed


def snapshot_state(tmp_path, cursor=0, width=170, height=28):
    m, ranked, _ = derive_snapshot(tmp_path)
    return base.ViewState(m, None, None, cursor, tuple(ranked), width, height)


def hlr_map(*ids: str, unparsed: dict[str, int] | None = None):
    """`len(ids)` childless HLRs over the reqharness profile — one gap each."""
    unparsed = unparsed or {}
    return build_map(
        REQHARNESS,
        [Node(i, "HLR", f"record {n}", unparsed=unparsed.get(i, 0))
         for n, i in enumerate(ids)],
        (),
        sourced=("HLR", "LLR"),
    )


def ranked_state(m, cursor=0, width=118, height=28):
    ranked, not_computed = rank_gaps(m, detect_gaps(m), None)
    return (
        base.ViewState(m, None, None, cursor, tuple(ranked), width, height),
        not_computed,
    )


CHAIN = Profile(
    "chain", ("N",), (EdgeType("next", (("N", "N"),), True, "none"),), ()
)


def chain_map(*specs):
    """`(prefix, count)` chains: reach(prefix) == count (the R1 idiom)."""
    nodes, edges = [], []
    for prefix, count in specs:
        ids = [prefix] + [f"{prefix}.{i}" for i in range(count)]
        nodes += [Node(i, "N") for i in ids]
        edges += [Edge(a, b, "next") for a, b in zip(ids, ids[1:])]
    return build_map(CHAIN, nodes, edges, sourced=("N",))


def multi_kind_map():
    """Three gap kinds in one map, in catalogue band order that is NOT
    row-count order: us without at (×1), llr not verified (×2), hlr without
    llr (×1)."""
    return build_map(
        REQHARNESS,
        [Node("US1", "US", "story one"), Node("AT1", "AT", "closed at"),
         Node("HLR1", "HLR", "lonely hlr"),
         Node("LLR1", "LLR", "low one"), Node("LLR2", "LLR", "low two")],
        (),
        sourced=("US", "AT", "HLR", "LLR", "TC"),
    )


HUB = Profile(
    "hub", ("N",), (EdgeType("next", (("N", "N"),), True, "none"),),
    (GapRow("NO PARENT", "HIGH", "lacks_in", "N", "next", None, False, False,
            ("N",), "<id> has no parent"),),
)


def hub_map(gap_nodes, chain_len):
    """`gap_nodes` orphans pointing into one chain (the R1 idiom)."""
    head = [f"c{i}" for i in range(chain_len)]
    nodes = [Node(f"g{i}", "N") for i in range(gap_nodes)] + [Node(c, "N") for c in head]
    edges = [Edge(f"g{i}", head[0], "next") for i in range(gap_nodes)]
    edges += [Edge(a, b, "next") for a, b in zip(head, head[1:])]
    return build_map(HUB, nodes, edges, sourced=("N",))


# ---------------------------------------------------------------------------
# Paint/parse helpers
# ---------------------------------------------------------------------------


def squash(text: str) -> str:
    """A painted line with column padding collapsed — the AT-135 asserted
    string form (`no gap node what reach status`)."""
    return " ".join(text.split())


def body_lines(rows) -> list[str]:
    """The non-blank painted body (everything below the three chrome rows)."""
    return [r.plain for r in rows[3:] if r.plain.strip()]


def gap_text_rows(rows) -> list:
    """Body Text rows that carry a ranked row (zero-padded rank in cells 0-1)."""
    return [r for r in rows[3:] if r.plain[:2].isdigit()]


def gap_rows(rows) -> list[str]:
    """The plain text of the ranked body rows."""
    return [r.plain for r in gap_text_rows(rows)]


def styles_of(row) -> set[str]:
    return {span.style for span in row.spans}


# ---------------------------------------------------------------------------
# LLR-RVG.1.1 — the rendered order IS the host-ranked order (M-RVG-1)
# ---------------------------------------------------------------------------


def test_rvg_1_1_rendered_order_is_the_ranked_order():
    """The renderer paints `state.gaps` exactly as ranked — severity, then
    reach descending, detection order on ties — and never re-sorts.
    M-RVG-1 (re-sort by node id) reddens this."""
    view = base.build_view("gaps")
    m = chain_map(("x", 5), ("h", 0), ("y", 9))
    found = [Gap("MED", "k", n, "", 0) for n in ("x", "h", "y")]
    ranked, _ = rank_gaps(m, found, None)
    assert [g.node for g in ranked] == ["y", "x", "h"]  # reach 9, 5, 0
    state = base.ViewState(m, None, None, 0, tuple(ranked), 118, 28)
    rows = view.paint(state)
    painted = [squash(r).split()[2] for r in gap_rows(rows)]
    assert painted == ["y", "x", "h"], (
        "the painted order must be the ranked order, not node-id order"
    )
    assert [r[:2] for r in gap_rows(rows)] == ["01", "02", "03"]


def test_rvg_1_1_snapshot_fixture_shape(tmp_path):
    """Positive control: the inline snapshot derives 7 gaps, exactly two
    qualified, ranked in canon order — the AT-135 fixture shape."""
    m, ranked, not_computed = derive_snapshot(tmp_path)
    assert [g.node for g in ranked] == SNAPSHOT_IDS
    assert [g.severity for g in ranked] == ["MED"] * 7
    assert {g.reach for g in ranked} == {0}
    assert not_computed == 0
    qualified = {g.node for g in ranked if QUALIFIER.strip() in g.sentence}
    assert qualified == QUALIFIED


# ---------------------------------------------------------------------------
# LLR-RVG.1.2 — header, tally chips, field band (M-RVG-2)
# ---------------------------------------------------------------------------


def test_rvg_1_2_header_chips_and_field_band(tmp_path):
    """AT-135's chrome strings: header left + right-aligned ranking note, the
    always-four tally chips, and the field band in column order."""
    view = base.build_view("gaps")
    rows = view.paint(snapshot_state(tmp_path))
    header = rows[0].plain
    assert header.startswith("gaps — what the record does not say")
    assert header.rstrip().endswith("ranked by severity, then reach ↓")
    tally = squash(rows[1].plain)
    for chip in ("high 0", "med 7", "low 0", "total 7"):
        assert chip in tally, f"the tally chip {chip!r} is owed"
    assert squash(rows[2].plain).startswith("no gap node what reach status")


def test_rvg_1_2_total_chip_counts_the_rendered_rows():
    """M-RVG-2: the `total` chip must count the same rows that are rendered."""
    view = base.build_view("gaps")
    m = hlr_map(*[f"HLR-W.{i}" for i in range(40)])
    state, _ = ranked_state(m, cursor=39, width=118, height=12)
    rows = view.paint(state)
    tally = squash(rows[1].plain)
    assert "total 40" in tally
    hidden = 40 - len(gap_rows(rows))
    assert hidden == 32, "the +NN above marker declares exactly the hidden rows"
    assert "+32 above" in [squash(r) for r in body_lines(rows)]


# ---------------------------------------------------------------------------
# LLR-RVG.1.3 — row anatomy, cursor on the worst gap, no microbar (M-RVG-3/4)
# ---------------------------------------------------------------------------


def test_rvg_1_3_row_anatomy_at_full_width(tmp_path):
    """At a generous width nothing truncates: every row is EXACTLY
    `<rank> <kind> <node> <sentence> 000 <sev>` — the qualified rows end with
    the `(canon rows near this id could not be parsed or linked: 2)`
    qualifier.  M-RVG-3 (unpadded reach / a bar glyph) and M-RVG-10
    (`000` as `-`) redden the exact string."""
    view = base.build_view("gaps")
    rows = view.paint(snapshot_state(tmp_path, width=170))
    painted = gap_rows(rows)
    assert len(painted) == 7
    for i, line in enumerate(painted, start=1):
        node = SNAPSHOT_IDS[i - 1]
        sentence = f"{node} has no LLR under it: {SNAPSHOT_TITLES[node]}"
        if node in QUALIFIED:
            sentence += QUALIFIER
        expected = f"{i:02d} {KIND} {node} {sentence} 000 med"
        assert squash(line) == expected, f"row {i:02d} anatomy drifted"


def test_rvg_1_3_the_cursor_highlights_the_ranked_row(tmp_path):
    """M-RVG-4: the highlight rides `state.cursor` — at view open that is row
    01 (the worst gap), and it moves with the cursor."""
    view = base.build_view("gaps")
    for cursor in (0, 1, 6):
        rows = view.paint(snapshot_state(tmp_path, cursor=cursor))
        highlights = [
            any(f"on {darkside.STEP}" in (s or "") for s in styles_of(row))
            for row in gap_text_rows(rows)
        ]
        assert highlights == [i == cursor for i in range(7)], (
            f"cursor {cursor}: the highlight must ride exactly that row"
        )


def test_rvg_1_3_no_microbar_anywhere(tmp_path):
    """The count column is the only reach visual: no bar-block glyphs in any
    painted row (M-RVG-3's bar variant)."""
    view = base.build_view("gaps")
    rows = view.paint(snapshot_state(tmp_path))
    for row in rows:
        assert not any(ch in row.plain for ch in "▁▂▃▄▅▆▇█"), (
            "a reach microbar glyph leaked into the gaps view"
        )


# ---------------------------------------------------------------------------
# LLR-RVG.1.5 — by-kind mode (M-RVG-7) + the membership oracle (COND-UX-2)
# ---------------------------------------------------------------------------

HINT = "same catalogue grouped by gap kind — scan for a detector, not a severity"


def _oracle_bands(gaps):
    """The LLR-RVG.1.5 oracle: group the ranked catalogue by kind in
    CATALOGUE order; per band keep the member list (kind, node) IN ORDER,
    the count and the worst severity."""
    members: dict[str, list[int]] = {}
    for i, g in enumerate(gaps):
        members.setdefault(g.kind, []).append(i)
    bands = []
    for row in REQHARNESS.gaps:
        if row.kind in members:
            idxs = members[row.kind]
            worst = min((gaps[i].severity for i in idxs), key=SEVERITIES.index)
            bands.append(
                (row.kind, [(gaps[i].kind, gaps[i].node) for i in idxs],
                 len(idxs), worst.lower())
            )
    return bands


def _painted_bands(rows, kind_w):
    """Parse the painted by-kind frame back into
    [(kind, [(kind, node), ...], count, worst word)] — band heads carry the
    kind at col 1, the severity word and `×N`; members keep their global
    rank in cells 0-1, the kind at the kind column and the node after it."""
    x_kind, x_node = 5, 5 + kind_w + 2
    bands: list[tuple] = []
    current = None
    for line in body_lines(rows):
        if line.lstrip().startswith("+"):
            continue  # the counted-overflow marker
        if HINT in line:
            continue  # the bottom-anchored grouping hint
        if line[:2].isdigit():
            assert current is not None, "a member row with no band above it"
            member_kind = line[x_kind:x_kind + kind_w].strip().lower()
            node = line[x_node:x_node + 12].strip()
            current[1].append((member_kind, node))
            continue
        kind = line[1:1 + kind_w].strip().lower()
        count = int(re.search(r"×(\d+)", line).group(1))
        worst = re.search(r"\b(high|med|low)\b", line).group(1)
        current = [kind, [], count, worst]
        bands.append(current)
    return [(k, members, n, w) for k, members, n, w in bands]


def test_rvg_1_5_by_kind_bands_match_the_membership_oracle():
    """AT-136 + COND-UX-2: each band's member node ids equal the oracle
    grouping of the ranked catalogue — per-band id sets AND order — in
    catalogue order with `×N` and the worst severity.  M-RVG-7 (bands sorted
    by row count) reddens the ORDER half of this arm."""
    view = base.build_view("gaps")
    m = multi_kind_map()
    state, _ = ranked_state(m, cursor=0, width=118, height=28)
    oracle = _oracle_bands(state.gaps)
    assert [b[0] for b in oracle] == ["US WITHOUT AT", "LLR NOT VERIFIED",
                                      "HLR WITHOUT LLR"]
    assert oracle[1][2] == 2 and oracle[1][3] == "med"
    view.toggle("k")
    rows = view.paint(state)
    painted = _painted_bands(rows, kind_w=16)
    expected = [(k.lower(), [(mk.lower(), n) for mk, n in members], n, w)
                for k, members, n, w in oracle]
    assert painted == expected, (
        "the painted bands drifted from the oracle grouping — the prototype's\n"
        "first-band/row misalignment must not reproduce"
    )


def test_rvg_1_5_member_rows_keep_their_global_ranks():
    """Bands regroup; the member rows keep their global rank numbers."""
    view = base.build_view("gaps")
    m = multi_kind_map()
    state, _ = ranked_state(m, width=118, height=28)
    view.toggle("k")
    rows = view.paint(state)
    ranks = [r.plain[:2] for r in rows[3:] if r.plain[:2].isdigit()]
    assert ranks == ["01", "02", "03", "04"], (
        "band 1 holds rank 01, band 2 holds ranks 02+03, band 3 holds rank 04"
    )


def _serialized(rows):
    return [(r.plain, [(s.start, s.end, s.style) for s in r.spans]) for r in rows]


def test_rvg_1_5_toggle_word_hint_and_byte_identical_toggle_back(tmp_path):
    """AT-136: `k` returns the state word `by kind` and paints the hint;
    pressing again returns the ranked frame BYTE-IDENTICAL.  `enter`/`c`
    are not this renderer's kinds and return ``""``."""
    view = base.build_view("gaps")
    state = snapshot_state(tmp_path, cursor=2)
    ranked_first = view.paint(state)
    assert view.toggle("k") == "by kind"
    by_kind = view.paint(state)
    assert view.toggle("k") == ""
    ranked_again = view.paint(state)
    assert view.toggle("enter") == "" and view.toggle("c") == ""
    assert view.toggle("k") == "by kind" and view.toggle("k") == ""
    assert len(by_kind) == len(ranked_first), "total painted rows unchanged"
    hint_lines = [r for r in by_kind if HINT in r.plain]
    assert len(hint_lines) == 1, "the grouping hint paints exactly once"
    assert not any(HINT in r.plain for r in ranked_first)
    assert _serialized(ranked_again) == _serialized(ranked_first), (
        "AT-136: the ranked frame must come back byte-identical"
    )


def test_rvg_1_5_by_kind_on_an_empty_map_keeps_the_empty_state():
    """AT-136 boundary: `k` on a map with no gaps keeps `no gaps on record`."""
    view = base.build_view("gaps")
    m = build_map(REQHARNESS, (), (), sourced=("HLR", "LLR"))
    state, _ = ranked_state(m, width=118, height=28)
    assert view.toggle("k") == "by kind"
    rows = view.paint(state)
    assert "no gaps on record" in [squash(r.plain) for r in rows]
    assert not gap_rows(rows)


# ---------------------------------------------------------------------------
# LLR-RVG.2.1/.2.2 — Darkside casing, census-guarded (M-RVG-8/9)
# ---------------------------------------------------------------------------


def test_rvg_2_1_source_census_no_upper_no_caps_kind_literal():
    """LLR-RVG.2.1: a source census over the renderer finds no `.upper()` and
    no hard-coded caps literal of a shipped catalogue kind.  M-RVG-8 reddens
    both halves."""
    source = Path(gaps_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    uppers = [n for n in ast.walk(tree)
              if isinstance(n, ast.Attribute) and n.attr == "upper"]
    assert uppers == [], "the renderer must never upper-case a label"
    caps_kinds = {row.kind for row in REQHARNESS.gaps}
    literals = {n.value for n in ast.walk(tree)
                if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    planted = literals & caps_kinds
    assert planted == set(), f"caps catalogue literals planted: {planted}"


def test_rvg_2_2_chrome_is_all_lowercase():
    """LLR-RVG.2.2: every chrome string the view paints — header, tally,
    fields, cut markers, the empty line, the hint, the band heads — is
    authored lowercase.  M-RVG-9 (one caps chrome string) reddens this."""
    view = base.build_view("gaps")
    m = hlr_map(*[f"HLR-W.{i}" for i in range(40)])
    state, _ = ranked_state(m, cursor=39, width=118, height=12)

    def assert_darkside(rows):
        chrome = [rows[0], rows[1], rows[2]] + [
            r for r in rows[3:] if r.plain.strip().startswith("+")
        ]
        for row in chrome:
            words = [w for w in squash(row.plain).split() if w.isalpha()]
            assert words == [w.lower() for w in words], (
                f"a chrome word is not Darkside-cased: {row.plain!r}"
            )

    rows = view.paint(state)
    assert_darkside(rows)
    assert squash(rows[2].plain) == "no gap node what reach status"
    view.toggle("k")
    rows = view.paint(state)
    assert HINT in [squash(r.plain) for r in rows]
    assert_darkside(rows)
    for row in rows[3:]:
        if (row.plain.strip() and not row.plain[:2].isdigit()
                and not row.plain.lstrip().startswith("+")):
            words = [w for w in squash(row.plain).split() if w.isalpha()]
            assert words == [w.lower() for w in words]


def test_rvg_2_2_empty_state_line():
    view = base.build_view("gaps")
    m = build_map(REQHARNESS, (), (), sourced=("HLR", "LLR"))
    state, _ = ranked_state(m, width=118, height=28)
    rows = view.paint(state)
    tally = squash(rows[1].plain)
    for chip in ("high 0", "med 0", "low 0", "total 0"):
        assert chip in tally
    assert "no gaps on record" in [squash(r.plain) for r in rows]


# ---------------------------------------------------------------------------
# LLR-RVG.2.3 — honest zeros and the not-computed declaration (M-RVG-10/11)
# ---------------------------------------------------------------------------


def test_rvg_2_3_zero_reach_is_painted_as_computed_never_a_dash(tmp_path):
    """AT-138-adjacent unit arm: `000` rendered as computed — never `-`,
    never blank.  A nonzero reach proves the count is data, not decoration.
    M-RVG-10 reddens this."""
    view = base.build_view("gaps")
    rows = view.paint(snapshot_state(tmp_path, width=170))
    for line in gap_rows(rows):
        assert " 000 med" in squash(line)
        assert " - " not in squash(line)
    m = chain_map(("y", 9))
    ranked, _ = rank_gaps(m, [Gap("MED", "k", "y", "", 0)], None)
    state = base.ViewState(m, None, None, 0, tuple(ranked), 118, 28)
    rows = view.paint(state)
    assert "009" in squash(gap_rows(rows)[0])


def test_rvg_1_4_explicit_heights_2_to_3_are_respected_not_floored():
    """review-inc004 F1: the viewport floor applies to the DEGENERATE
    mount-time 1 only — an explicit height of 2 or 3 painted 4 rows under
    the old `max(..., 4)` (one or two rows more than the channel names);
    explicit heights are always respected."""
    view = base.build_view("gaps")
    m = hlr_map("HLR-A")
    ranked, _ = rank_gaps(m, detect_gaps(m), None)
    for h in (2, 3, 4):
        state = base.ViewState(m, None, None, 0, tuple(ranked), 118, h)
        rows = view.paint(state)
        assert len(rows) == h, f"explicit height {h} painted {len(rows)} rows"
    # the degenerate mount-time 1 still paints the honest default body
    state = base.ViewState(m, None, None, 0, tuple(ranked), 118, 1)
    assert len(view.paint(state)) == 24


def test_rvg_2_3_budget_spent_declares_not_computed():
    """AT-138(b): when the shared visit budget is spent, every reach cell is
    still an honest zero-padded count and the tally declares the exact
    not-computed count — never a fabricated number.  M-RVG-11 reddens this."""
    view = base.build_view("gaps")
    m = hub_map(50_000, 49_990)
    found = detect_gaps(m)
    for g in found[:60]:
        m.reach(g.node)  # spend the shared budget the way another view would
    ranked, not_computed = rank_gaps(m, found, None)
    assert not_computed > 0
    by_node = {g.node: g for g in ranked}

    def reach_token(line):
        return squash(line).split()[-2]

    # window over the FIRST rows: the computed reaches paint zero-padded, as
    # ranked — data, never decoration
    state = base.ViewState(m, None, None, 0, tuple(ranked), 118, 28)
    rows = view.paint(state)
    assert f"reach not computed: {not_computed}" in squash(rows[1].plain)
    painted = gap_rows(rows)
    assert len(painted) == 24, "windowed body at height 28 (cursor 0, marker below)"
    for line in painted:
        node = squash(line).split()[3]
        assert reach_token(line) == f"{by_node[node].reach:03d}"
    assert any(reach_token(line) != "000" for line in painted), (
        "the computed reaches must paint as computed"
    )
    # window over the LAST rows: the budget-spent tail is an honest `000`
    state = base.ViewState(m, None, None, len(ranked) - 1, tuple(ranked), 118, 28)
    rows = view.paint(state)
    for line in gap_rows(rows):
        assert reach_token(line) == "000", (
            "a not-computed reach ranks with 0 and paints `000`, never a dash"
        )
    assert f"reach not computed: {not_computed}" in squash(rows[1].plain)


def test_rvg_2_3_qualifier_on_exactly_the_two_snapshot_nodes(tmp_path):
    """AT-138(c): with the cursor off row 1, the qualifier rides exactly
    HLR-CAN.1 (rank 03) and HLR-REPAIR.1 (rank 06)."""
    view = base.build_view("gaps")
    rows = view.paint(snapshot_state(tmp_path, cursor=2, width=170))
    qualified = []
    for line in gap_rows(rows):
        if QUALIFIER.strip() in line:
            qualified.append(next(t for t in squash(line).split() if t.startswith("HLR-")))
    assert sorted(qualified) == sorted(QUALIFIED)


# ---------------------------------------------------------------------------
# LLR-RVG.3.1 — the one sink, hostile payloads (M-RVG-12/13)
# ---------------------------------------------------------------------------

HOSTILE_TITLE = "a\tb\nc\x1b[31m[bold]x[/bold]\u202e\x07d"
HOSTILE_ID = "HLR-[bold]x[/bold]"


def test_rvg_3_1_hostile_payload_renders_literally_on_one_row():
    """AT-139 unit arm: markup brackets, ESC, U+202E, U+0007 and raw LF/TAB
    in canon-derived text render byte-literal through the one sink — one
    row, no style leak, no parse error, row count equal to the benign
    twin's.  M-RVG-12 (coercion bypass) reddens the controls; M-RVG-13
    (markup-parsing sink) reddens the literal-brackets half."""
    view = base.build_view("gaps")
    hostile = build_map(
        REQHARNESS, [Node(HOSTILE_ID, "HLR", HOSTILE_TITLE)], (), sourced=("HLR", "LLR")
    )
    benign = build_map(REQHARNESS, [Node("HLR-B.1", "HLR", "plain record")],
                       (), sourced=("HLR", "LLR"))
    h_state, _ = ranked_state(hostile, width=118, height=28)
    b_state, _ = ranked_state(benign, width=118, height=28)
    h_rows = view.paint(h_state)
    b_rows = view.paint(b_state)
    assert len(h_rows) == len(b_rows)
    assert len(gap_rows(h_rows)) == len(gap_rows(b_rows)) == 1
    joined = "\n".join(r.plain for r in h_rows)
    assert "\x1b" not in joined and "\t" not in joined, "controls never reach the frame raw"
    assert all("\n" not in r.plain for r in h_rows), "a payload cannot forge a second row"
    assert "�" in joined, "controls must coerce to U+FFFD, never raw"
    assert "[bold]x[/bold]" in joined, "markup brackets render literally"
    hostile_styles: set[str] = set()
    for row in h_rows:
        hostile_styles |= styles_of(row)
    benign_styles: set[str] = set()
    for row in b_rows:
        benign_styles |= styles_of(row)
    assert hostile_styles <= benign_styles, (
        f"payload-attributable style runs leaked: {hostile_styles - benign_styles}"
    )


def test_rvg_3_1_the_renderer_uses_no_markup_parsing_sink():
    """Census half of LLR-RVG.3.1: the renderer assembles explicit-style
    `Text` through `base.label` only — no `from_markup`, no console sink."""
    source = Path(gaps_mod.__file__).read_text(encoding="utf-8")
    assert "from_markup" not in source
    assert "markup=True" not in source


def test_the_notice_obligation_is_the_whole_body():
    """The frozen D1 notice rule: when `state.notice` is set, the fixed
    refusal line IS the body — nothing beside it."""
    view = base.build_view("gaps")
    state = base.ViewState(
        None, "structure: refused (x): file not found - descriptor skipped",
        None, 0, (), 118, 12)
    rows = view.paint(state)
    assert "file not found" in rows[0].plain
    assert all(not r.plain.strip() for r in rows[1:])


def test_row_count_is_the_ranked_axis():
    """D1: the gaps cursor axis is the ranked-gap rows; no map → 0."""
    view = base.build_view("gaps")
    m = multi_kind_map()
    state, _ = ranked_state(m, width=118, height=28)
    assert view.row_count(state) == 4
    empty = base.ViewState(None, "notice", None, 0, (), 118, 28)
    assert view.row_count(empty) == 0


# ---------------------------------------------------------------------------
# Layer B — the AT arms through the real app (C-16: REAL keys)
# ---------------------------------------------------------------------------


def frame_text(screen) -> str:
    """The painted frame as one plain string — the `test_relmap_shell` idiom."""
    return "\n".join(
        "".join(seg.text for seg in strip)
        for strip in screen._compositor.render_strips()  # noqa: SLF001
    )


def painted_frame(screen) -> bytes:
    """The composited frame serialized as (text, style) runs."""
    rows = [
        [(seg.text, str(seg.style)) for seg in strip]
        for strip in screen._compositor.render_strips()  # noqa: SLF001
    ]
    return repr(rows).encode("utf-8")


def canvas_strips(screen) -> list:
    """The composited strips of the view canvas — the rows between the host
    chrome (tab strip + crumb + notice = 3 rows) and the keybar."""
    strips = list(screen._compositor.render_strips())  # noqa: SLF001
    key_y = next(
        i for i, s in enumerate(strips)
        if "view" in "".join(seg.text for seg in s)
        and "matrix" in "".join(seg.text for seg in s)
    )
    return strips[3:key_y]


def canvas_row_runs(screen, prefix):
    """The (text, style) runs of the painted canvas row starting with
    *prefix* — for the highlight-band assertions."""
    for strip in canvas_strips(screen):
        text = "".join(seg.text for seg in strip)
        if text.startswith(prefix):
            return [(seg.text, str(seg.style)) for seg in strip]
    return None


def open_relmap(app, workspace, name="reqharness"):
    screen = RelMapScreen(name, workspace, descriptor=default_descriptor())
    app.push_screen(screen)
    return screen


async def pause(pilot, n=2):
    for _ in range(n):
        await pilot.pause()


async def test_at135_the_ranked_gaps_screen(tmp_path):
    """AT-135: open the snapshot map, press `2` (non-default), assert the
    chrome and row 01; press `down` and assert the highlight moved to row 02
    with `focus` untouched (the gaps axis is not the node axis).

    Crumb deviation (declared in the increment packet): the shipped host's
    crumb format is `name / relmap / view [· toggle-state word]` — the
    prototype's `gaps · reach count` scene label is not a toggle word, so at
    open the crumb reads `reqharness / relmap / gaps` and after `k` it reads
    `reqharness / relmap / gaps · by kind`.
    """
    (tmp_path / "REQUIREMENTS.md").write_text(snapshot_canon(), encoding="utf-8")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        screen = open_relmap(app, tmp_path)
        await pause(pilot)
        assert screen.active_view == "matrix"
        await pilot.press("2")
        await pause(pilot)
        painted = frame_text(app.screen)
        assert "reqharness / relmap / gaps" in painted
        header = next(l for l in painted.splitlines()
                      if l.startswith("gaps — what the record does not say"))
        assert header.rstrip().endswith("ranked by severity, then reach ↓")
        for chip in ("high 0", "med 7", "low 0", "total 7"):
            assert chip in painted
        fields = next(l for l in painted.splitlines() if l.startswith("no "))
        assert squash(fields).startswith("no gap node what reach status")
        row1 = next(l for l in painted.splitlines() if l.startswith("01 "))
        collapsed = squash(row1)
        assert collapsed.startswith(f"01 {KIND} HLR-A.2")
        assert collapsed.endswith(" 000 med")
        # the qualified rows are honestly truncated at 118 (WHAT width) — the
        # full qualifier string is pinned by the unit arm at width 170
        row3 = next(l for l in painted.splitlines() if l.startswith("03 "))
        assert "… 000 med" in squash(row3), "WHAT truncates with one ellipsis, reach/status intact"
        # the keybar fragment the seat labels carry (host-owned chrome)
        bar = next(l for l in painted.splitlines() if "view" in l and "matrix" in l)
        for frag in ("1 matrix", "2 gaps", "3 sheet"):
            assert frag in bar, f"the keybar does not paint {frag!r}"
        focus_before = screen.focus
        # the highlight starts on row 01 (the worst gap — cursor default 0)
        assert any("on #262626" in style for _, style in canvas_row_runs(app.screen, "01 "))
        assert not any("on #262626" in style for _, style in (canvas_row_runs(app.screen, "02 ") or [("", "")]))
        await pilot.press("down")
        await pause(pilot)
        assert screen._cursors["gaps"] == 1, "the cursor rides the ranked-row axis"
        assert screen.focus == focus_before, "the gaps cursor leaves `focus` untouched"
        assert not any("on #262626" in style for _, style in (canvas_row_runs(app.screen, "01 ") or [("", "")]))
        assert any("on #262626" in style for _, style in canvas_row_runs(app.screen, "02 "))


async def test_at136_by_kind_through_the_app(tmp_path):
    """AT-136: `k` regroups into one band (×7, worst severity med), paints the
    hint, lands `by kind` in the crumb; pressing `k` again returns the ranked
    frame byte-identical."""
    (tmp_path / "REQUIREMENTS.md").write_text(snapshot_canon(), encoding="utf-8")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        open_relmap(app, tmp_path)
        await pause(pilot)
        await pilot.press("2")
        await pause(pilot)
        before = painted_frame(app.screen)
        await pilot.press("k")
        await pause(pilot)
        painted = frame_text(app.screen)
        assert "reqharness / relmap / gaps · by kind" in painted
        assert HINT in painted
        head = next(l for l in painted.splitlines() if l.startswith(f" {KIND}"))
        assert "×7" in head
        assert " med " in f" {squash(head)} "
        ranks = [l[:2] for l in painted.splitlines() if l[:2].isdigit()]
        assert ranks == [f"{i:02d}" for i in range(1, 8)], "global ranks kept"
        await pilot.press("k")
        await pause(pilot)
        assert painted_frame(app.screen) == before, (
            "AT-136: the ranked frame must return byte-identical"
        )
        crumb = next(l for l in frame_text(app.screen).splitlines()
                     if "relmap / gaps" in l)
        assert "· by kind" not in crumb


async def test_at137_the_window_follows_the_cursor_at_87(tmp_path):
    """AT-137 (gaps portion, 87×34): a 30-gap map, the cursor driven to the
    last row — the window follows it and declares every undisplayed row."""
    rows = [canon_row(f"HLR-W.{i}", f"record {i}") for i in range(30)]
    (tmp_path / "REQUIREMENTS.md").write_text(
        HEADER + "".join(r + "\n" for r in rows), encoding="utf-8")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(87, 34)) as pilot:
        screen = open_relmap(app, tmp_path)
        await pause(pilot)
        await pilot.press("2")
        await pause(pilot)
        for _ in range(35):  # clamped at the last row — no wrap
            await pilot.press("down")
        await pause(pilot)
        assert screen._cursors["gaps"] == 29
        painted = frame_text(app.screen)
        # The viewport height is renderer-driven on the joined tree (the mount
        # body comes from the real matrix renderer, not the one-row
        # `PendingView`), so the window size is derived from the painted frame
        # rather than pinned to the lane-tree geometry — the asserted property
        # is that the window FOLLOWS the cursor and declares every undisplayed
        # row exactly (`LED-2026-10-25-r2.19`).
        ranks = [int(l[:2]) for l in painted.splitlines() if l[:2].isdigit()]
        assert ranks and ranks[-1] == 30, "the window reaches the last row"
        above = next(l for l in painted.splitlines()
                     if l.startswith("+") and "above" in l)
        declared = int(above.split()[0].lstrip("+"))
        assert declared == ranks[0] - 1, (
            "every undisplayed row above the window is declared exactly"
        )
        last = next(l for l in painted.splitlines() if l.startswith("30 "))
        assert "HLR-W.29" in last and squash(last).endswith(" 000 med")
        assert not any(l.startswith("+") and "more" in l for l in painted.splitlines())


async def test_at138_empty_map_through_the_app(tmp_path):
    """AT-138(a): a canon with no HLR/LLR rows — zero chips and the empty
    line; the view stays alive; `k` keeps the empty state."""
    (tmp_path / "REQUIREMENTS.md").write_text(HEADER, encoding="utf-8")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        open_relmap(app, tmp_path)
        await pause(pilot)
        await pilot.press("2")
        await pause(pilot)
        painted = frame_text(app.screen)
        for chip in ("high 0", "med 0", "low 0", "total 0"):
            assert chip in painted
        assert "no gaps on record" in painted
        await pilot.press("k")
        await pause(pilot)
        assert "no gaps on record" in frame_text(app.screen), (
            "AT-136 boundary: by-kind on an empty map keeps the empty state"
        )


async def test_at139_hostile_canon_through_the_app(tmp_path):
    """AT-139: a canon row whose id carries markup brackets and whose title
    carries ESC / U+202E / U+0007 renders literally on the gaps canvas — no
    style leak, no parse error, one payload row like the benign twin."""
    (tmp_path / "REQUIREMENTS.md").write_text(
        HEADER + canon_row(HOSTILE_ID, "payload \x1b[31m tail \u202e end \x07") + "\n",
        encoding="utf-8",
    )
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        open_relmap(app, tmp_path)
        await pause(pilot)
        await pilot.press("2")
        await pause(pilot)
        strips = canvas_strips(app.screen)
        text = "\n".join("".join(seg.text for seg in s) for s in strips)
        assert "[bold]x[/bold]" in text, "the bracket payload renders literally"
        assert "\x1b" not in text, "ESC never reaches the frame"
        assert "�" in text, "controls coerce to U+FFFD"
        runs = [(seg.text, str(seg.style)) for s in strips for seg in s]
        payload_row = next(
            (text_, style) for text_, style in runs if "payload" in text_)
        allowed = {"", darkside.MUT, darkside.INK, f"bold {darkside.INK}"}
        overlay = f" on {darkside.STEP}"
        assert payload_row[1] in allowed or payload_row[1].removesuffix(overlay) in allowed, (
            f"the payload segment carries a foreign style: {payload_row[1]!r}"
        )
        assert sum(1 for s in strips if s[0].text[:2].isdigit()) == 1, (
            "exactly one gap row — like the benign twin"
        )
