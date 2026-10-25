"""Scalecheck sweep — LLR-Q3.1.1 / LLR-Q3.1.2 / LLR-Q3.2.3 (AT-115, AT-116 arms).

Batch `2026-10-23-hygiene-batch`, lane L3.  The sweep proves every renderer in
the `mapper.views` exported roster stays inside its viewport at the five
recorded terminal sizes across the four recorded states of
`.dev-flow/2026-10-23-hygiene-batch/design/state-matrix.md`
(ledger `LED-2026-10-23-hygiene-batch.7`): **6 renderers x 5 sizes x 4 states =
120 geometry assertions**.  The audit arm (LLR-Q3.2.3) injects a sink at the
`Canvas` construction sites and fails the sweep on any unexplained overprint or
clip.  Asserting mutants: M-Q3-1 (a renderer's bounds handling broken) ·
M-Q3-2 (event recording removed).  Dangling-edge graphs stay OUT of the sweep
(state matrix §Excluded — a renderer crash on that input is a backlog item).
"""
from pathlib import Path

from rich.cells import cell_len

import mapper.views as views
from mapper.canvas import Canvas
from mapper.mermaid import parse
from mapper.views.layered import OVERFLOW_TOKEN, overflow_phrase, painted_ids
from mapper.views.state import ViewState
from tests.perf_goldens_capture import build_empty, build_fold_tree, build_forest

REPO = Path(__file__).resolve().parents[1]

SIZES = ((80, 24), (90, 30), (118, 34), (160, 45), (200, 50))
RECORDED_CENSUS = 6
EXPECTED_ROSTER = {
    "LayeredRenderer",
    "OutlineRenderer",
    "LaneRenderer",
    "HybridLaneRenderer",
    "RailTimelineRenderer",
    "RadialRenderer",
}
EMPTY_STATE_TEXTS = ("(no map loaded)", "(no repo loaded)")

_PLAIN_GRAPH = parse((REPO / "fixtures" / "anidado.mmd").read_text(encoding="utf-8"))


def _roster():
    """LLR-Q3.1.1 — the subject set is DERIVED from code, guarded against an
    empty or changed roster (C-31): a dropped export reddens the guard."""
    names = list(views.__all__)
    assert names, "mapper.views.__all__ is empty — the sweep would be vacuous"
    assert len(names) >= RECORDED_CENSUS, (
        f"roster {names} is smaller than the recorded census of {RECORDED_CENSUS}"
    )
    assert set(names) == EXPECTED_ROSTER, (
        f"roster changed against the recorded census: {sorted(names)}"
    )
    return [(name, getattr(views, name)) for name in names]


def _states():
    """The four recorded states (design/state-matrix.md), graphs shared so the
    folded state can prove fold-invariance on the same graph."""
    fold_graph = build_fold_tree()
    return {
        "plain": (_PLAIN_GRAPH, {}, None),
        "folded": (fold_graph, {"folded": frozenset({"mid"})}, fold_graph),
        "empty": (build_empty(), {}, None),
        "orphan": (build_forest(), {}, None),
    }


def test_renderer_roster_derived():
    """LLR-Q3.1.1 — completeness guard over the code-derived roster."""
    assert len(_roster()) == RECORDED_CENSUS


def _check_geometry(name, graph, text, w, h, state_name, state, failures):
    """LLR-Q3.1.2 as amended by ledger .11 (ruling R10): 1..h lines; every line
    <= w cells, with Layered's wordmark header asserted EXACTLY against its
    documented arithmetic — body budget (w - 2) + node-count meter + overflow
    declaration when the render leaves nodes unpainted (byte-pinned by the
    perf render goldens, measured at all five sizes)."""
    combo = f"{name} {w}x{h} {state_name}"
    lines = text.plain.splitlines()
    if not lines:
        failures.append(f"{combo}: rendered text is empty")
        return
    if len(lines) > h:
        failures.append(f"{combo}: {len(lines)} lines > {h}")
    if state_name == "empty":
        # Documented short-circuit: <= h lines, the named text present —
        # "exactly h lines" does not hold for zero-node graphs (state matrix,
        # LLR-Q3.1.2 threshold note).
        if any(cell_len(line) > w for line in lines):
            failures.append(f"{combo}: a line exceeds {w} cells")
        if not any(t in text.plain for t in EMPTY_STATE_TEXTS):
            failures.append(f"{combo}: no named empty-state text")
        return
    for i, line in enumerate(lines):
        width = cell_len(line)
        if name == "LayeredRenderer" and i == 0:
            expected = (w - 2) + cell_len(f"{len(graph.nodes)} nodes")
            unpainted = len(graph.nodes) - len(painted_ids(graph, state))
            if unpainted:
                expected += cell_len(f"  {overflow_phrase(unpainted)}")
            if width != expected:
                failures.append(
                    f"{combo}: header is {width} cells != exact arithmetic {expected}"
                )
        elif width > w:
            failures.append(f"{combo}: line {i} is {width} cells > {w}")


def test_sweep():
    """LLR-Q3.1.2 / AT-115 — the 120-combo geometry sweep over the state matrix."""
    failures = []
    for name, cls in _roster():
        renderer = cls()
        for state_name, (graph, kw, fold_graph) in _states().items():
            for w, h in SIZES:
                state = ViewState(w=w, h=h, **kw)
                text = renderer.render(graph, state)
                _check_geometry(name, graph, text, w, h, state_name, state, failures)
                if state_name == "folded" and name != "LayeredRenderer":
                    # Fold-invariance: the other five renderers must answer a
                    # folded ViewState byte-identically to the unfolded one on
                    # the SAME graph (state matrix applicability matrix).
                    unfolded = renderer.render(
                        fold_graph, ViewState(w=w, h=h)
                    ).plain
                    if unfolded != text.plain:
                        failures.append(f"{name} {w}x{h} folded: fold-variant vs plain")
    assert not failures, "\n".join(failures)


def test_sweep_audit_arm(monkeypatch):
    """LLR-Q3.2.3 as amended by ledger .12/.13 (ruling R10): canvas-constructing
    renderers get an audited canvas on every non-empty render; the
    direct-composition renderers are asserted to construct NONE (never silently
    skipped); zero unexplained events everywhere."""
    sinks = []
    real_init = Canvas.__init__

    def audited_init(self, w, h, tones=(), fallback="", audit=None):
        sink = {"clip": [], "overprint": []}
        sinks.append(sink)
        real_init(self, w, h, tones=tones, fallback=fallback, audit=sink)

    # Measured construction census over the full 120-combo matrix (ledger .13):
    # grep `Canvas(` over mapper/views/ finds exactly three construction sites —
    # layered.py, radial.py and lane.py (the lane.py site serves RailTimeline).
    CONSTRUCTS = {"LayeredRenderer", "RadialRenderer", "RailTimelineRenderer"}
    monkeypatch.setattr(Canvas, "__init__", audited_init)
    unexplained = []
    for name, cls in _roster():
        renderer = cls()
        for state_name, (graph, kw, _fold_graph) in _states().items():
            for w, h in SIZES:
                before = len(sinks)
                text = renderer.render(graph, ViewState(w=w, h=h, **kw))
                fresh = sinks[before:]
                combo = f"{name} {w}x{h} {state_name}"
                if state_name == "empty" or name not in CONSTRUCTS:
                    # The documented short-circuit (empty) and the
                    # direct-composition renderers construct no canvas — the arm
                    # pins exactly that, per LLR-Q3.2.3 as amended (.12/.13).
                    assert not fresh, f"{combo}: unexpected canvas construction"
                    continue
                assert fresh, f"{combo}: no audited canvas was constructed"
                clips = [xy for sink in fresh for xy in sink["clip"]]
                overprints = [xy for sink in fresh for xy in sink["overprint"]]
                if overprints:
                    unexplained.append(f"{combo}: overprint at {overprints}")
                # A clip is explained only when the rendered plain text
                # declares the overflow in words (the overflow token).
                if clips and OVERFLOW_TOKEN not in text.plain:
                    unexplained.append(f"{combo}: clip at {clips} with no overflow declaration")
    assert not unexplained, "\n".join(unexplained)
