"""HLR-N06.1 — pan moves the window and is bounded.

`TC-030`, `TC-031`, `AT-011`, `AT-012`.  The acceptances press the REAL `H` and
`L`, never `action_*`: `QA-B-10`'s rule is that a chord-agnostic requirement is
legitimate and a chord-agnostic acceptance test is not, and `AT-012` asserting
the `borde del territorio` declaration against a key nobody had named is what
made that a defect rather than an untidiness.
"""
from __future__ import annotations

import pytest

from mapper.app import MapScreen, MapperApp
from mapper.model import Edge, Ficha, Graph, Node
from mapper.views.layered import LayeredRenderer, _tree_layout, pan_extent
from mapper.views.state import ViewState
from mapper.widgets.chrome import HintLine
from tests.inc3_support import canvas_rows, install, open_map, pan_graph, rows_in

# The declared context of use.  `run_test()` defaults to 80x24, where
# `_apply_region_visibility` auto-hides BOTH the rail and the inspector, so a
# reading taken there describes a screen the operator does not have (B-54).
#
# `height_offset` IS DELIBERATELY NOT IMPORTED HERE, and the unused import that
# used to be was a real signal rather than untidiness.  Its job is to convert a
# terminal height into a renderer height when a test needs a NAMED renderer
# size; every arm in this module instead reads `screen._canvas_size()` back off
# the mounted screen and derives its press counts from `pan_extent` at that
# size, which is the stronger form of the same discipline -- it measures the
# achieved geometry rather than computing a size it hopes it got.  Nothing here
# needs the helper, so it is not imported.
CONTEXT_OF_USE = (118, 34)


def _hint(screen) -> str:
    """The hint line as PAINTED, not as stored — HLR-N06.1 says paint."""
    return " ".join(rows_in(screen, screen.query_one(HintLine).region))


# --------------------------------------------------------------------------
# LLR-N06.1.2 — the clamp


@pytest.mark.parametrize(
    "offset,extent,span,expected",
    [
        # Both far extremes.
        (-10 ** 6, 300, 100, 0),
        (10 ** 6, 300, 100, 200),
        # Inside the range, and both of its endpoints.
        (0, 300, 100, 0),
        (200, 300, 100, 200),
        (137, 300, 100, 137),
        # E < W: a map SMALLER than the canvas has a legal range of exactly one
        # position.  An off-by-one here is how the map jumps off screen on a
        # small graph, and a bare `extent - span` would be negative.
        (5, 40, 100, 0),
        (-5, 40, 100, 0),
        # E == W: the other single-position case.
        (5, 100, 100, 0),
        (0, 100, 100, 0),
    ],
)
def test_tc_030_the_pan_clamp_holds_over_the_declared_range(
    offset, extent, span, expected
):
    """LLR-N06.1.2 — `[0, max(0, E - W)]` for every input, over 9 of them."""
    result = MapScreen._clamp_pan(offset, extent, span)
    assert result == expected
    assert 0 <= result <= max(0, extent - span)


def test_tc_030_the_clamp_is_not_the_identity(tmp_path):
    """The discriminating negative: a clamp that returns its input passes every
    in-range row above.  Two of the nine rows are out of range on purpose, and
    this states that as a property rather than trusting the table to have them.
    """
    out_of_range = [(-10 ** 6, 300, 100), (10 ** 6, 300, 100), (5, 40, 100)]
    changed = [
        (o, e, s) for o, e, s in out_of_range
        if MapScreen._clamp_pan(o, e, s) != o
    ]
    assert len(changed) == 3


# --------------------------------------------------------------------------
# LLR-N06.1.1 — the offsets travel in the view state


def test_tc_031_pan_translates_the_drawing_origin(tmp_path):
    """Two renders at two offsets differ, and the OUTPUT SHAPE does not.

    The shape clause is the one that reddens the plausible wrong fix: shifting
    by slicing the rendered rows changes the row or the cell count, which is a
    map that shrinks as you pan rather than a window that moves over it.
    """
    # NOT `legacy`: measured, its extent at w=50 is 45 against a span of 48, so
    # it fits, `pan_extent` is 0 in both axes and this arm would compare a frame
    # with itself and pass.  The guard below is what found that.
    graph = pan_graph()
    state = ViewState(w=50, h=20)
    (extent_x, span_x), _ = pan_extent(graph, state)
    assert extent_x > span_x, (
        f"extent {extent_x} fits in span {span_x}; there is nothing to pan and "
        f"this arm would compare a frame with itself"
    )

    still = LayeredRenderer().render(graph, state)
    panned = LayeredRenderer().render(graph, ViewState(w=50, h=20, pan_x=8))
    assert still.plain != panned.plain

    a, b = still.plain.split("\n"), panned.plain.split("\n")
    assert len(a) == len(b)
    # Row 0 is the header, which is not part of the map plane and does not pan.
    assert [len(r) for r in a[1:]] == [len(r) for r in b[1:]]

    # The renderer holds no pan state of its own: rendering the un-panned state
    # again after a panned render returns the first image byte for byte.
    assert LayeredRenderer().render(graph, state).plain == still.plain


def test_tc_031_the_renderer_is_a_pure_function_of_graph_and_state(tmp_path):
    """LLR-N06.1.1's acceptance criterion, executed on ONE long-lived renderer.

    `MapScreen` holds one renderer (`app.py`) and calls `render` from the canvas
    repaint and from the SVG export at DIFFERENT sizes.  A renderer that kept
    pan — or a painted set — as a side effect would let one `e` press poison the
    other call site; measured, that shape made the indicator declare `0 hidden`
    on a canvas hiding 7.
    """
    graph = install(tmp_path, "legacy")
    renderer = LayeredRenderer()
    small = renderer.render(graph, ViewState(w=30, h=6)).plain
    renderer.render(graph, ViewState(w=140, h=45, pan_x=20, folded=frozenset({"fin"})))
    assert renderer.render(graph, ViewState(w=30, h=6)).plain == small


# --------------------------------------------------------------------------
# AT-011 / AT-012 — the real chords, through the shipped screen


@pytest.mark.asyncio
async def test_a_layout_that_cannot_be_drawn_does_not_kill_the_app(tmp_path):
    """The sink guard, over the calls Inc-3 added OUTSIDE it.

    `refresh_canvas`'s try/except says it is "scoped to the sink, not to the
    exception types known today", because it runs inside the message pump and an
    escape there kills the app with the operator's unsaved edits in it.  Inc-3
    added two `_tree_layout`-reaching calls and put both outside it --
    `_reclamp_pan` and `_pagination_text` -> `painted_ids` -- and `_pan` reaches
    `pan_extent` with no guard at all.  Executed on a cyclic graph before the
    repair, one `L` press took `app.is_running` to False.

    NOT REACHABLE THROUGH THE SHIPPED LOADERS TODAY, and that is stated rather
    than glossed: `mermaid.parse` rejects multi-parent, and `store.load` and
    `store.save` both reject cycles through `find_cycle`.  This is a
    defence-in-depth arm, and the guard's own comment is the argument for it.
    The graph is therefore installed directly on the mounted screen, which is
    the only way to reach the state the guard exists for.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        screen = await _open_pan_map(app, pilot)

        cyclic = Graph()
        for i in range(4):
            cyclic.add_node(Node(id=f"n{i}", ficha=Ficha(title=f"N{i}", meta="m")))
        for i in range(4):
            cyclic.add_edge(Edge(parent_id=f"n{i}", child_id=f"n{(i + 1) % 4}"))
        # The fixture is asserted: a graph that lays out fine proves nothing.
        with pytest.raises(ValueError):
            _tree_layout(cyclic, 14, 3, frozenset())
        screen.graph = cyclic

        # The repaint itself must not escape -- this is the call that runs in
        # the message pump.
        screen.refresh_canvas()
        await pilot.pause()

        # The degradation is DECLARED, not silent: the canvas says so, and the
        # strip declares nothing rather than a number it could not compute.
        assert "no se pudo dibujar el mapa" in " ".join(canvas_rows(screen))
        assert screen._unpainted_ids() is None  # noqa: SLF001

        for key in ("L", "H", "J", "K", "j", "z"):
            await pilot.press(key)
            await pilot.pause()
            assert app.is_running, f"the {key!r} key killed the app on a cyclic graph"


@pytest.mark.asyncio
async def test_a_dangling_edge_does_not_escape_refresh_canvas(tmp_path):
    """The SIBLING SINK, which sat outside the same guard.

    `refresh_canvas`'s `try` closes before the minimap is written, so
    `_minimap_text` and `_branch_coverage_glyph` — which index
    `self.graph.nodes[...]` with ids taken straight from `children_of` — raised
    from inside the message pump with nothing catching them.  The asymmetry was
    the finding: `_unpainted_ids` has its own try/except and the minimap had
    none, in the same method, for the same class of failure the cycle guard
    beside this arm was added for.

    REACHABILITY IS STATED HONESTLY: "could not construct from a file", not
    "unreachable".  `mermaid.parse` calls `_ensure_node` for BOTH edge endpoints
    and `MapStore.load` routes a cycle to `MapStoreError`, so no `.mmd`/`.yml`
    pair was found that produces a dangling edge — the same defence-in-depth
    footing as the cycle arm.

    SCOPED TO `refresh_canvas`, AND THE SCOPE IS ITSELF A FINDING.  Measured on
    this fixture: `_minimap_text()` and `_branch_coverage_glyph()` both raise
    `KeyError`, `OutlineRail.show()` does NOT — but the rail then raises the
    same `KeyError` from inside its own `render()`, at COMPOSITOR paint time,
    which is a different path and one no guard in `refresh_canvas` can reach.
    So this arm asserts what this increment fixed (the method does not let the
    exception escape) and does not assert that the frame survives, because it
    does not.  `mapper/widgets/rail.py` is outside this increment's fix set;
    the rail's unguarded `render` is recorded as a CARRY.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        screen = await _open_pan_map(app, pilot)

        dangling = Graph()
        dangling.add_node(Node(id="root", ficha=Ficha(title="raiz", meta="m")))
        dangling.add_node(Node(id="hijo", ficha=Ficha(title="hijo", meta="m")))
        dangling.add_edge(Edge(parent_id="root", child_id="hijo"))
        dangling.edges.append(Edge(parent_id="root", child_id="fantasma"))
        assert "fantasma" not in dangling.nodes
        screen.graph = dangling

        # THE FIXTURE IS ASSERTED AT THE SINK: without this the arm below is
        # `refresh_canvas` on an ordinary graph, which never needed a guard.
        with pytest.raises(KeyError):
            screen._minimap_text()  # noqa: SLF001
        with pytest.raises(KeyError):
            screen._branch_coverage_glyph("root")  # noqa: SLF001

        # THE GUARD, AND IT IS THE WHOLE ASSERTION.  Un-guarded, this call
        # raises `KeyError` straight out of the message pump — where an escape
        # kills the app with the operator's unsaved edits in it.  Guarded, the
        # coverage strip degrades to empty and the method completes.
        #
        # NOTHING IS READ OFF THE COMPOSITED FRAME HERE, and that is forced
        # rather than preferred: compositing calls `OutlineRail.render`, which
        # raises the same `KeyError` at PAINT time (the carry above), so a
        # `frame_rows` read would fail on the rail's defect instead of measuring
        # this one.  The `pytest.raises` clauses above are what keep this
        # non-vacuous: they prove the sink really does raise on this fixture.
        screen.refresh_canvas()


@pytest.mark.asyncio
async def test_the_pan_fixture_overflows_both_axes_at_the_declared_context(tmp_path):
    """`pan_graph`'s docstring claim, ASSERTED at the size it names.

    A shared fixture whose docstring states a measured property it does not have
    is how a driver ends up exercising a no-op while looking like it exercised
    the feature -- the defect class this increment already caught once in
    itself.  So the claim is executed here rather than described there.

    THE UNIT IS THE TERMINAL.  At a 118x34 terminal the rail and the inspector
    take 60 columns between them, so the canvas the fixture has to overflow is
    58x25; measured here, `max_pan_x = 49` and `max_pan_y = 10`.  Handed to the
    renderer at `w = 118` the same fixture has `max_pan_x = 0`, because
    `_geometry` shrinks `card_w` until the leaves fit `avail` and a canvas that
    wide never reaches the floor.  Both readings are true of different things,
    and the negative one is asserted below so the distinction cannot be lost
    again by someone re-measuring at the renderer.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        screen = await _open_pan_map(app, pilot)
        w, h = screen._canvas_size()  # noqa: SLF001
        assert (w, h) < CONTEXT_OF_USE, (
            f"the canvas is {(w, h)} at a {CONTEXT_OF_USE} terminal; the side "
            f"regions are not taking their columns and this arm is measuring "
            f"the wrong frame"
        )
        (extent_x, span_x), (extent_y, span_y) = pan_extent(
            screen.graph, screen._view_state(w, h)  # noqa: SLF001
        )
        assert extent_x - span_x > 0, (w, h, extent_x, span_x)
        assert extent_y - span_y > 0, (w, h, extent_y, span_y)

    # The NEGATIVE reading, on the renderer rather than the terminal: at
    # `w = 118` horizontal pan is dead, and `H`/`L` are inert.  Recorded as an
    # executed number so "the fixture does not overflow at 118x34" cannot come
    # back as a finding without the unit attached to it.
    (rx, rsx), _ry = pan_extent(pan_graph(), ViewState(w=118, h=34))
    assert rx - rsx <= 0, (rx, rsx)


async def _open_pan_map(app, pilot):
    app.store.save("pan", pan_graph())
    screen = await open_map(app, pilot, "pan")
    await pilot.pause()
    return screen


@pytest.mark.asyncio
async def test_at_011_the_real_pan_chord_moves_the_painted_window(tmp_path):
    """AT-011 — one press of the real `L`, and the painted range changes.

    Read from the COMPOSITED frame clipped to the canvas region, never from
    `render().plain`: the question is what the operator sees.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        screen = await _open_pan_map(app, pilot)
        w, h = screen._canvas_size()
        (extent_x, span_x), _ = pan_extent(screen.graph, screen._view_state(w, h))
        assert extent_x > span_x, (
            f"the fixture does not overflow at {CONTEXT_OF_USE}: extent "
            f"{extent_x} vs span {span_x}, so a pan cannot change anything"
        )

        before = canvas_rows(screen)
        await pilot.press("L")
        await pilot.pause()
        after = canvas_rows(screen)

        assert screen.pan_x == MapScreen.PAN_STEP_X
        assert after != before
        assert len(after) == len(before)
        assert {len(r) for r in after} == {len(r) for r in before}


@pytest.mark.asyncio
async def test_at_012_pan_is_bounded_at_both_edges_and_declares_the_edge(tmp_path):
    """AT-012 — both boundaries, the real keys, and the painted declaration.

    The press count `K` is DERIVED from the layout extent and the canvas width
    at run time, never hard-coded — a typed count is a count that stops
    exhausting the extent the day the fixture changes.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        screen = await _open_pan_map(app, pilot)
        w, h = screen._canvas_size()
        (extent_x, span_x), _ = pan_extent(screen.graph, screen._view_state(w, h))
        max_pan = max(0, extent_x - span_x)
        assert max_pan > 0

        # BOUNDARY 1 — panning LEFT at column 0.
        assert screen.pan_x == 0
        before = canvas_rows(screen)
        await pilot.press("H")
        await pilot.pause()
        assert screen.pan_x == 0
        assert canvas_rows(screen) == before
        assert "borde del territorio" in _hint(screen)

        # BOUNDARY 2 — panning RIGHT past the last column that shows content.
        presses = max_pan // MapScreen.PAN_STEP_X + 1
        assert presses >= 2, presses
        for _ in range(presses):
            await pilot.press("L")
            await pilot.pause()
        assert screen.pan_x == max_pan

        exhausted = canvas_rows(screen)
        await pilot.press("L")
        await pilot.pause()
        assert screen.pan_x == max_pan
        assert canvas_rows(screen) == exhausted
        assert "borde del territorio" in _hint(screen)


@pytest.mark.asyncio
async def test_at_012_the_vertical_chords_are_bounded_the_same_way(tmp_path):
    """The other axis, because `J`/`K` are two of the four rows this seat adds
    and a pan that is bounded in one axis only loses the map in the other."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        screen = await _open_pan_map(app, pilot)
        w, h = screen._canvas_size()
        _x, (extent_y, span_y) = pan_extent(screen.graph, screen._view_state(w, h))
        max_pan = max(0, extent_y - span_y)
        assert max_pan > 0, (extent_y, span_y)

        await pilot.press("K")
        await pilot.pause()
        assert screen.pan_y == 0
        assert "borde del territorio" in _hint(screen)

        for _ in range(max_pan // MapScreen.PAN_STEP_Y + 1):
            await pilot.press("J")
            await pilot.pause()
        assert screen.pan_y == max_pan
        bottom = canvas_rows(screen)
        await pilot.press("J")
        await pilot.pause()
        assert canvas_rows(screen) == bottom
        assert "borde del territorio" in _hint(screen)


@pytest.mark.asyncio
async def test_a_live_J_press_changes_what_the_canvas_paints(tmp_path):
    """The VERTICAL axis needs a CONTENT oracle, and it had none.

    WRITTEN BECAUSE A MUTANT SURVIVED ALL 789 TESTS.  Drop `- self.pan_y` from
    `_Geometry.place` and `J`/`K` become a complete product no-op: the attribute
    moves, the frame does not, and the suite is green.  The identity
    `declared == traced` cannot see it — `render` and `painted_ids` share
    `place`, so a LOCKSTEP edit moves both sides together — and neither can
    `oracle_traced`, which is row-scan-invariant under `pan_y` by construction
    (its docstring states that as a strength; it is also this blind spot).  The
    same lockstep edit on `pan_x` IS caught, because the oracle consumes
    `pan_x` explicitly.  So the one bug class the identity cannot see was, on
    this axis, the one the oracle could not see either.

    The bounded arm above cannot substitute: it asserts the frame is UNCHANGED
    at the edges, which a pan that never moves anything satisfies trivially.
    This asserts the positive — one LIVE press, and the rows the operator sees
    are different rows.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        screen = await _open_pan_map(app, pilot)
        w, h = screen._canvas_size()
        _x, (extent_y, span_y) = pan_extent(screen.graph, screen._view_state(w, h))
        assert extent_y - span_y >= MapScreen.PAN_STEP_Y, (
            f"the fixture has {max(0, extent_y - span_y)} rows of vertical "
            f"travel at {CONTEXT_OF_USE}; one press cannot move the window and "
            f"this arm would be vacuous"
        )

        before = canvas_rows(screen)
        await pilot.press("J")
        await pilot.pause()
        after = canvas_rows(screen)

        assert screen.pan_y == MapScreen.PAN_STEP_Y, screen.pan_y
        # THE CONTENT, not the attribute.  This is the clause the lockstep
        # mutant fails and every other vertical arm passes.
        assert after != before, (
            "`J` moved `pan_y` and the painted canvas is byte-identical; the "
            "vertical pan is a no-op the operator cannot see"
        )
        # The frame is still the same SHAPE — a pan translates the window, it
        # does not resize or reflow it.
        assert len(after) == len(before)
        assert {len(r) for r in after} == {len(r) for r in before}


@pytest.mark.asyncio
async def test_the_edge_hint_does_not_latch_across_a_live_pan(tmp_path):
    """`borde del territorio` is CLEARED on a successful pan.

    It was set on a no-op and cleared by nothing, so it latched on the first
    press that hit an edge and then sat there describing every later LIVE pan as
    an edge the operator had not reached.  On the shipped maps that is the
    normal case rather than an unlucky one: swept over the shipped fixtures,
    horizontal pan is live at exactly one terminal width, so `H`/`L` are almost
    always no-ops — the hint latches immediately and then misdescribes `J`.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        screen = await _open_pan_map(app, pilot)

        # LATCH IT on a genuine no-op: `K` at the top edge.
        await pilot.press("K")
        await pilot.pause()
        assert screen.pan_y == 0
        assert "borde del territorio" in _hint(screen)

        # Then a LIVE pan on the other side of the same axis.
        await pilot.press("J")
        await pilot.pause()
        assert screen.pan_y == MapScreen.PAN_STEP_Y, (
            "the follow-up press was itself a no-op; this arm proves nothing"
        )
        assert "borde del territorio" not in _hint(screen), (
            f"the edge hint survived a live pan: {_hint(screen)!r}"
        )
