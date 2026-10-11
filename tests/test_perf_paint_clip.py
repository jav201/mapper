"""AT-075 / LLR-PERF.1.1 / LLR-PERF.1.3 (batch `2026-10-10-perf-batch`, Inc-R1, Lane R).

Lane R's first increment clips the spans `Canvas.elbow_down` and `Canvas.edge`
iterate to the canvas rectangle BEFORE looping, so out-of-canvas cells are
never visited.  `wire` already bounds-checks every cell and drops the
out-of-bounds writes, so the clip is byte-identical by construction
(requirements premise 2) -- and this module proves it:

* `test_bare_canvas_clip_equality` (LLR-PERF.1.1, layer 0) -- the clipped
  methods write exactly the cells the PRE-CHANGE loops wrote.  The reference
  loops are copies kept INSIDE this test file, never a `Canvas` flag, over
  the shapes the requirement names: `x1 < x0` (degenerate span), spans fully
  off-canvas, `ybus` above and below the canvas, negative pan origin, and a
  bus span reaching past the right edge.
* `test_render_grid_clip_identity` (LLR-PERF.1.3, layer 0) -- the render
  grid (empty / single / deep-5000 / wide-2000 / wide-6000 / forest / fold /
  panned ViewState, at 118x34 and 87x34) rebuilt with the capture script's
  own builders is byte-identical to the base goldens pinned at base SHA
  `5cde04e`, and a multi-parent DAG built directly paints identically with
  the clip active vs the in-test reference loops.
* `test_wire_count_budget` (LLR-PERF.1.1, layer 0 counted oracle) and
  `test_at_075_keypress_wire_budget` (AT-075, HLR-PERF.1, layer B) -- the
  scripted two-keypress session (`l`, `j`) on wide-2000 at 118x34 through
  the real app (`MapperApp` + `run_test(size=(118, 34))`, real keys, helpers
  imported from `tests/test_draft_save.py`) performs at most 61,500
  `Canvas.wire` calls in total with the counter RESET after mount — the cap
  is 5x the measured 12,264 for this session (61,320, rounded up to 61,500;
  DDR qa LOW-4, `evidence/ddr2-red.transcript`), vs the measured baseline
  without the clip of 23,983,998 (PERF0C SS7.1) — and AT-075's settled
  canvas rows byte-equal the pinned golden
  (`tests/goldens/perf/at075_075b_wide2000_118x34.txt`, base SHA `5cde04e`).

Negative controls (PDR SS5): M-R1a (remove the clip) -> the wire-count budget
RED (~24 M calls); a Y-ONLY clip -> the budget RED (the x-axis carries the
whole gain: the unclipped bus row is what the budget counts); M-R1b (clamp
the bus upper bound to `min(xb, w-1)` -- drops one in-bounds cell) -> the
bare-`Canvas` equality RED.
"""
from __future__ import annotations

import difflib

import pytest

from mapper.app import MapperApp
from mapper.canvas import _D, _L, _R, _U, Canvas
from mapper.model import Edge, Ficha, Graph, Node
from mapper.views.layered import LayeredRenderer
from mapper.views.state import ViewState

from tests.perf_goldens_capture import (
    GOLDEN_DIR,
    _canvas_lines,
    build_wide,
    render_grid_cases,
)
from tests.test_draft_save import _open, _press

WIRE_CAP = 61_500
BASELINE_2_KEYS = 23_983_998
TERMINAL = (118, 34)
AT075_GOLDEN = GOLDEN_DIR / "at075_075b_wide2000_118x34.txt"


# ---------------------------------------------------------------------------
# Reference copies of the PRE-CHANGE span loops (LLR-PERF.1.1: the reference
# lives in the test file, never behind a `Canvas` flag).
# ---------------------------------------------------------------------------

def _ref_edge(c: Canvas, x0: int, y0: int, x1: int, y1: int,
              tone: str = "frame") -> None:
    """The pre-change `Canvas.edge` loop, verbatim."""
    for y in range(min(y0, y1), max(y0, y1) + 1):
        c.wire(x0, y, _U | _D, tone)


def _ref_elbow_down(c: Canvas, x0: int, y0: int, x1: int, ybus: int,
                    tone: str = "frame") -> None:
    """The pre-change `Canvas.elbow_down` loop, verbatim."""
    c.wire(x0, y0, _D, tone)
    for y in range(y0 + 1, ybus):
        c.wire(x0, y, _U | _D, tone)
    c.wire(x0, ybus, _U | (_R if x1 > x0 else _L), tone)
    xa, xb = min(x0, x1), max(x0, x1)
    for x in range(xa + 1, xb):
        c.wire(x, ybus, _L | _R, tone)
    c.wire(x1, ybus, _D | (_L if x1 > x0 else _R), tone)


def _snapshot(c: Canvas) -> dict:
    """Every painted layer of the canvas -- the equality oracle."""
    return {
        "cells": dict(c.cells),
        "bits": dict(c.bits),
        "dots": dict(c.dots),
        "bgs": dict(c.bgs),
        "wire_tones": dict(c._wire_tones),  # noqa: SLF001
    }


# ---------------------------------------------------------------------------
# LLR-PERF.1.1 (layer 0): bare-`Canvas` equality, clipped vs reference.
# ---------------------------------------------------------------------------

#: (w, h, x0, y0, x1, ybus) for `elbow_down` and `edge` is derived below.
_ELBOW_CASES = [
    # x1 < x0: the child drops off the bus to the LEFT of the parent.
    (20, 10, 8, 2, 3, 6),
    # Bus reaching past the right edge: the in-bounds tail cell (w-1, ybus)
    # must still be painted (M-R1b clamps this away and is non-equivalent).
    (20, 10, 15, 2, 25, 6),
    # Spans fully off-canvas to the right.
    (20, 10, 50, 2, 90, 6),
    # Spans fully off-canvas to the left.
    (20, 10, -50, 2, -30, 6),
    # ybus above the canvas (bus row out of bounds, drop partially visible).
    (20, 10, 5, 2, 12, -4),
    # ybus below the canvas (vertical drop partially visible).
    (20, 10, 5, 8, 12, 40),
    # Fully below: nothing paints at all.
    (20, 10, 5, 25, 12, 40),
    # Negative pan origin: the whole span shifted up-left into the frame.
    (20, 10, -15, -3, -6, 4),
    # ybus == y0: the middle loop is empty in both implementations.
    (20, 10, 5, 4, 12, 4),
]

_EDGE_CASES = [
    (20, 10, 5, 0, 5, 100),      # taller than the canvas, both ends clipped
    (20, 10, 5, -50, 5, -30),    # fully above
    (20, 10, -3, -5, -3, 30),    # x out of bounds, y straddling the frame
    (20, 10, 19, 2, 19, 8),      # hugging the right edge
]


@pytest.mark.parametrize("case", _ELBOW_CASES)
def test_bare_canvas_clip_equality(case):
    """LLR-PERF.1.1: clipped `elbow_down` writes exactly the cells the
    pre-change loop wrote -- 0 differences across every named shape."""
    w, h, x0, y0, x1, ybus = case
    ref = Canvas(w, h)
    _ref_elbow_down(ref, x0, y0, x1, ybus)
    clipped = Canvas(w, h)
    clipped.elbow_down(x0, y0, x1, ybus)
    assert _snapshot(clipped) == _snapshot(ref), (case, "elbow_down")


@pytest.mark.parametrize("case", _EDGE_CASES)
def test_bare_canvas_clip_equality_edge(case):
    """LLR-PERF.1.1, the `edge` span: same equality, vertical spans."""
    w, h, x0, y0, _x1, y1 = case
    ref = Canvas(w, h)
    _ref_edge(ref, x0, y0, x0, y1)
    clipped = Canvas(w, h)
    clipped.edge(x0, y0, x0, y1)
    assert _snapshot(clipped) == _snapshot(ref), (case, "edge")


def test_bare_canvas_clip_equality_paints_something():
    """Guard against a vacuous oracle: the reference loops paint cells in the
    in-bounds cases above (so an equality pass compares real content)."""
    ref = Canvas(20, 10)
    _ref_elbow_down(ref, 8, 2, 3, 6)
    _ref_edge(ref, 5, 0, 5, 100)
    assert ref.bits, "the in-bounds reference shapes painted no cells"


# ---------------------------------------------------------------------------
# LLR-PERF.1.3 (layer 0): render-grid identity against the base goldens.
# ---------------------------------------------------------------------------

def test_render_grid_clip_identity():
    """LLR-PERF.1.3: with the clip active, the full fixture grid rebuilds
    byte-identically to the base goldens (0 diffs at every shape and size),
    and a multi-parent DAG built directly paints identically with the clip
    active vs the in-test reference loops."""
    failures: list[str] = []
    for case_id, relative, text in render_grid_cases():
        golden = (GOLDEN_DIR / relative).read_text(encoding="utf-8")
        if text != golden:
            diff = "\n".join(
                list(difflib.unified_diff(
                    golden.splitlines(), text.splitlines(),
                    relative, "rendered", lineterm=""))[:20]
            )
            failures.append(f"{case_id}:\n{diff}")
    assert not failures, "\n\n".join(failures)

    # Boundary the goldens do not pin: a multi-parent DAG built directly
    # (rendered identically, never saved).  Render with the reference loops
    # swapped in, then with the clipped product methods, and compare bytes.
    dag = Graph()
    dag.add_node(Node(id="root", ficha=Ficha(title="raiz", meta="meta raiz")))
    for nid, title in (("a", "rama a"), ("b", "rama b")):
        dag.add_node(Node(id=nid, ficha=Ficha(title=title, meta=f"meta {nid}")))
        dag.add_edge(Edge(parent_id="root", child_id=nid))
    dag.add_node(Node(id="shared", ficha=Ficha(title="compartido", meta="meta s")))
    dag.add_edge(Edge(parent_id="a", child_id="shared"))
    dag.add_edge(Edge(parent_id="b", child_id="shared"))

    reference_renderer = LayeredRenderer()
    reference_renderer_render = reference_renderer.render
    original_elbow, original_edge = Canvas.elbow_down, Canvas.edge
    Canvas.elbow_down, Canvas.edge = _ref_elbow_down, _ref_edge
    try:
        reference_text = reference_renderer_render(dag, ViewState(w=118, h=34)).plain
    finally:
        Canvas.elbow_down, Canvas.edge = original_elbow, original_edge

    clipped_text = LayeredRenderer().render(dag, ViewState(w=118, h=34)).plain
    assert clipped_text == reference_text, (
        "multi-parent DAG: clipped render differs from the reference-loop render"
    )


# ---------------------------------------------------------------------------
# AT-075 (layer B) + its layer-0 counted oracle: the wire-call budget.
# ---------------------------------------------------------------------------

def _counting_wire(monkeypatch) -> list[int]:
    """A counting wrapper on `Canvas.wire`; returns the mutable counter."""
    real = Canvas.wire
    calls = [0]

    def counting(self, x, y, mask, tone="frame"):
        calls[0] += 1
        return real(self, x, y, mask, tone)

    monkeypatch.setattr(Canvas, "wire", counting)
    return calls


def _golden_blocks(text: str) -> dict[str, list[str]]:
    """Split the AT-075/075b golden into {step title: painted lines}."""
    blocks: dict[str, list[str]] = {}
    title: str | None = None
    for line in text.splitlines():
        if line.startswith("=== step: ") and line.endswith(" ==="):
            title = line[len("=== step: "):-len(" ===")]
            blocks[title] = []
        elif title is not None:
            blocks[title].append(line)
    return blocks


async def test_wire_count_budget(tmp_path, monkeypatch):
    """LLR-PERF.1.1 counted oracle: the scripted two-keypress sequence (`l`,
    `j`) on wide-2000 at 118x34 performs <= 61,500 `Canvas.wire` calls with
    the counter reset after mount.  Cap derivation (DDR qa LOW-4): the
    measured clipped count for this exact session is 12,264
    (`evidence/r1-red.transcript` §2); the cap is 5x that measurement
    (61,320), rounded up to 61,500 — so a clip that loses most of the x-axis
    gain (e.g. a y-only clip, back at 23,983,998) or a span widened ~10x
    both fail the cap, while measurement jitter cannot."""
    calls = _counting_wire(monkeypatch)
    app = MapperApp(tmp_path)
    async with app.run_test(size=TERMINAL) as pilot:
        await pilot.pause()
        app.store.save("perf2000", build_wide(2000))
        await _open(app, pilot, "perf2000", cursor="root")
        calls[0] = 0  # counter reset after mount (golden provenance protocol)
        await _press(pilot, "l")
        await _press(pilot, "j")
        total = calls[0]
    print(f"\nwire calls for l,j on wide-2000 at {TERMINAL[0]}x{TERMINAL[1]} "
          f"(counter reset after mount): {total} "
          f"(baseline {BASELINE_2_KEYS}, cap {WIRE_CAP})")
    assert total <= WIRE_CAP, (
        f"{total} wire calls for two keypresses exceeds the cap {WIRE_CAP} "
        f"(baseline {BASELINE_2_KEYS})"
    )


async def test_at_075_keypress_wire_budget(tmp_path, monkeypatch):
    """AT-075 (HLR-PERF.1): same session as `test_wire_count_budget` AND the
    settled `#map-canvas` rows after open, `l` and `j` byte-equal the golden
    pinned at base SHA `5cde04e` -- byte-identical paint at a fraction of the
    render work."""
    calls = _counting_wire(monkeypatch)
    app = MapperApp(tmp_path)
    async with app.run_test(size=TERMINAL) as pilot:
        await pilot.pause()
        app.store.save("perf2000", build_wide(2000))
        screen = await _open(app, pilot, "perf2000", cursor="root")
        calls[0] = 0  # counter reset after mount (golden provenance protocol)
        painted: list[tuple[str, list[str]]] = [
            (f"open (cursor {screen.nav.cursor})", _canvas_lines(screen)),
        ]
        await _press(pilot, "l")
        painted.append((f"l (cursor {screen.nav.cursor})", _canvas_lines(screen)))
        await _press(pilot, "j")
        painted.append((f"j (cursor {screen.nav.cursor})", _canvas_lines(screen)))
        total = calls[0]
    print(f"\nAT-075 wire calls (l,j, counter reset after mount): {total}")
    assert total <= WIRE_CAP, (
        f"{total} wire calls for two keypresses exceeds the cap {WIRE_CAP} "
        f"(baseline {BASELINE_2_KEYS})"
    )

    blocks = _golden_blocks(AT075_GOLDEN.read_text(encoding="utf-8"))
    for title, lines in painted:
        assert blocks.get(title) == lines, (
            f"canvas after {title!r} drifted from the base golden "
            f"{AT075_GOLDEN.name}"
        )
