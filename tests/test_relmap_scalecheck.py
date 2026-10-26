"""AT-137 — the 118/87 scale sweep for the gaps renderer (lane L4, inc 004).

The C10 discipline arms (every painted line inside the canvas width and the
frame exactly the viewport height — the gaps renderer paints no `Canvas`
cells, so the audit mapping has no sink site here; the equivalent guarantee
is asserted directly on the emitted rows), the WHAT drop-whole ladder, the
87-column truncation arm, the cursor-following window with its cut markers,
and the cap-scale arm: an in-test `build_map` map at the shipped `MAX_NODES`
cap (100,000 nodes, `mapper/osopen.py:93-4`, `LED-2026-10-25-r2.09`)
rendered through the gaps window at 118 AND 87 with every undisplayed row
declared.

Per COND-QA-3 (FLAKE-2 class) NO assertion here reads a clock: the open/`r`
derivation wall-clock budget (10× the 303-node skeleton baseline) is a
RECORDED PACKET MEASUREMENT (`evidence/p3-inc004-measure.txt`), never a
committed wall-clock assert.  The cross-view portions of AT-137 (the
matrix-row window, the sheet overflow line) need the other lanes' renderers
— absent in this tree; they are recorded as join-time (F-5) in the packet.
"""
from __future__ import annotations

from mapper.osopen import MAX_NODES
from mapper.relmap.gaps import detect_gaps, rank_gaps
from mapper.relmap.model import Node, build_map
from mapper.screens.relmap import base

from tests.test_relmap_gaps_view import (
    HUB,
    canon_row,
    gap_rows,
    hlr_map,
    hub_map,
    multi_kind_map,
    ranked_state,
    squash,
)

WIDTHS = (118, 87)
HEIGHT = 28


def _wide_map(n):
    """`n` childless HLRs — the window-overflow fixture."""
    return hlr_map(*[f"HLR-W.{i}" for i in range(n)])


def _disciplined(rows, w, budget):
    """The C10 audit-clean equivalent for a row-assembled renderer: exactly
    `budget` rows and no row wider than `w` — the compositor can neither
    clip an over-wide line nor lose a dropped one.  (Content rows the layout
    pads to exactly `w`; marker/tally lines are honest natural width.)"""
    assert len(rows) == budget, f"frame height {len(rows)} != viewport {budget}"
    for i, row in enumerate(rows):
        assert row.cell_len <= w, f"row {i} is {row.cell_len} cells wide, wider than {w}"


# ---------------------------------------------------------------------------
# The 118/87 sweep — audit-clean at both sizes
# ---------------------------------------------------------------------------


def test_c10_sweep_ranked_at_118_and_87(tmp_path):
    from tests.test_relmap_gaps_view import snapshot_state

    view = base.build_view("gaps")
    for w in WIDTHS:
        rows = view.paint(snapshot_state(tmp_path, width=w, height=HEIGHT))
        _disciplined(rows, w, HEIGHT)
        assert len(gap_rows(rows)) == 7, "the snapshot fits unwindowed at both sizes"


def test_c10_sweep_by_kind_at_118_and_87():
    view = base.build_view("gaps")
    m = multi_kind_map()
    state, _ = ranked_state(m, width=118, height=HEIGHT)
    for w in WIDTHS:
        state = base.ViewState(
            state.relmap, None, None, 0, state.gaps, w, HEIGHT)
        rows = view.paint(state)
        _disciplined(rows, w, HEIGHT)
    view.toggle("k")
    for w in WIDTHS:
        state = base.ViewState(
            state.relmap, None, None, 0, state.gaps, w, HEIGHT)
        rows = view.paint(state)
        _disciplined(rows, w, HEIGHT)


def test_c10_sweep_windowed_at_118_and_87():
    """A map that overflows the body: markers included, discipline holds."""
    view = base.build_view("gaps")
    m = _wide_map(40)
    for w in WIDTHS:
        for cursor in (0, 20, 39):
            state, _ = ranked_state(m, cursor=cursor, width=w, height=12)
            rows = view.paint(state)
            _disciplined(rows, w, 12)
            markers = [squash(r.plain) for r in rows[3:] if r.plain.strip().startswith("+")]
            assert markers, "an overflowed body must declare its cut rows"
            # every painted row is either a marker or a real ranked row
            assert len(gap_rows(rows)) + len(markers) <= 9


# ---------------------------------------------------------------------------
# AT-137 — the WHAT drop-whole ladder and the 87-column truncation arm
# ---------------------------------------------------------------------------


def test_at137_the_what_column_drops_whole_below_its_minimum():
    """M-RVG-6: below `WHAT_MIN = 12` cells the WHAT column drops WHOLE —
    never truncated.  The ladder steps the width down and watches the
    `what` field header and column vanish together while `reach`/`status`
    stay intact."""
    view = base.build_view("gaps")
    m = _wide_map(3)
    last_with = None
    first_without = None
    for w in range(118, 55, -1):
        state, _ = ranked_state(m, width=w, height=HEIGHT)
        rows = view.paint(state)
        fields = squash(rows[2].plain)
        has_what = "what" in fields.split()
        if has_what:
            last_with = w
        elif first_without is None:
            first_without = w
        # invariant at every width: reach + status columns intact
        for line in gap_rows(rows):
            assert squash(line).endswith("000 med"), f"row broke at width {w}"
        _disciplined(rows, w, HEIGHT)
    assert last_with is not None and first_without == last_with - 1, (
        f"the drop must flip between two adjacent widths: {last_with}/{first_without}"
    )
    # the measured column width at the last `what` width honors the minimum;
    # the first width without it fell below
    state, _ = ranked_state(m, width=last_with, height=HEIGHT)
    fields = view.paint(state)[2].plain
    x_what = fields.index("what")
    x_reach = fields.index("reach")
    assert x_reach - x_what - 2 >= 12, "WHAT_MIN holds at the last wide width"
    state, _ = ranked_state(m, width=first_without, height=HEIGHT)
    fields = view.paint(state)[2].plain
    x_node = fields.index("node")
    x_reach = fields.index("reach")
    # the width the WHAT column WOULD have had (node column is 12 cells)
    assert x_reach - 2 - (x_node + 4 + 12 + 2) < 12, "below the minimum the column is gone"


def test_at137_what_values_end_ellipsis_at_87_with_reach_and_status_intact():
    """AT-137 asserted arm (87×34): truncated WHAT values end with the single
    ellipsis glyph; `reach` and `status` stay intact at their columns."""
    view = base.build_view("gaps")
    m = hlr_map("HLR-LONGNAME.1", "HLR-B.2")
    state, _ = ranked_state(m, width=87, height=HEIGHT)
    rows = view.paint(state)
    _disciplined(rows, 87, HEIGHT)
    fields = rows[2].plain
    x_reach = fields.index("reach")
    for line in gap_rows(rows):
        squashed = squash(line)
        assert "…" in squashed, "a long WHAT ends with the ellipsis"
        # reach + severity at the declared columns, untouched
        assert line[x_reach:x_reach + 3] == "000"
        assert squashed.endswith("med")


# ---------------------------------------------------------------------------
# AT-137 — the window follows the cursor, every undisplayed row declared
# ---------------------------------------------------------------------------


def test_at137_window_follows_the_cursor_and_declares_every_cut_row():
    """M-RVG-5: clamping the window to the first page reddens this — for a
    mid-map cursor the painted window must contain exactly that row, with the
    rows above and below declared in words."""
    view = base.build_view("gaps")
    m = _wide_map(40)
    state, _ = ranked_state(m, cursor=20, width=87, height=12)
    rows = view.paint(state)
    _disciplined(rows, 87, 12)
    painted = gap_rows(rows)
    markers = [squash(r.plain) for r in rows[3:] if r.plain.strip().startswith("+")]
    nodes = [next(t for t in squash(p).split() if t.startswith("HLR-")) for p in painted]
    ranked_nodes = [g.node for g in state.gaps]
    assert ranked_nodes[20] in nodes, "the window must cover the cursor row"
    first_rank = int(painted[0][:2])
    last_rank = int(painted[-1][:2])
    assert markers[0] == f"+{first_rank - 1:02d} above"
    assert markers[-1] == f"+{40 - last_rank:02d} more"
    # the declared cuts plus the painted rows account for every ranked row
    assert (first_rank - 1) + len(painted) + (40 - last_rank) == 40


# ---------------------------------------------------------------------------
# AT-137 cap-scale arm — 100,000 nodes at the shipped MAX_NODES cap
# ---------------------------------------------------------------------------


def test_at137_cap_scale_100k_map_renders_at_118_and_87():
    """SEC-2 / `LED-2026-10-25-r2.09`: an in-test `build_map` map at the
    shipped cap renders through the gaps window at 118 AND 87 — the window
    bounds the work, every undisplayed row is declared in words, and zero
    unexplained audit events (the C10 discipline census) are recorded.  The
    matrix/sheet portions of this arm are join-time (F-5) — they need the
    other lanes' renderers."""
    view = base.build_view("gaps")
    m = build_map(
        HUB, [Node(f"s{i}", "N") for i in range(MAX_NODES)], [], sourced=("N",)
    )
    ranked, not_computed = rank_gaps(m, detect_gaps(m), None)
    assert len(ranked) == MAX_NODES and not_computed == 0
    state = base.ViewState(
        m, None, None, MAX_NODES - 1, tuple(ranked), 118, HEIGHT)
    for w in WIDTHS:
        st = base.ViewState(state.relmap, None, None, state.cursor, state.gaps, w, HEIGHT)
        rows = view.paint(st)
        _disciplined(rows, w, HEIGHT)
        painted = gap_rows(rows)
        markers = [squash(r.plain) for r in rows[3:] if r.plain.strip().startswith("+")]
        # the cursor rides the LAST row: only an above marker, declaring
        # every undisplayed row in one contiguous counted block
        assert len(markers) == 1 and "above" in markers[0]
        hidden = MAX_NODES - len(painted)
        assert markers[0] == f"+{hidden} above", (
            "every undisplayed row must be declared by the marker"
        )
        assert painted[-1].startswith("100000"), "the last rank paints in full"
        assert squash(painted[-1]).split()[3] == f"s{MAX_NODES - 1}", (
            "the window ends on the cursor row — the last node of the cap map"
        )
        assert "total 100000" in squash(rows[1].plain)
