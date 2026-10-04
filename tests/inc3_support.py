"""Shared fixtures and the painted-trace ORACLE for the US-N06 increment.

Not a test module (no `test_` prefix, so pytest does not collect it); it exists
so `AT-011` .. `AT-017` share one oracle instead of four that agree on the day
they are written.

WHY THE ORACLE LOOKS LIKE THIS.  `HLR-N06.3`'s promise is an identity between
what the product declares painted and what the frame actually shows, so the two
sides must not share a computation.  The product side is
`mapper.views.layered.painted_ids`, off `_geometry`.  The oracle side below
NEVER imports either: it re-derives `card_w` from its own copy of the sizing
formula and reads the answer out of the COMPOSITED FRAME.

It does call `_tree_layout`, and that is deliberate rather than an oversight.
`M-N06.3-b` -- the named weaker variant this batch must redden -- is *computing
the painted set from `_tree_layout`'s keys*, i.e. treating PLACED as PAINTED.
The oracle does the opposite: it uses placement only to know WHERE to look, and
then asks the frame whether anything is there.  Executed on `legacy` at 30x6,
`_tree_layout` has 8 keys and this oracle returns 1 -- so the two are not the
same measurement, which is the control that says using it here is sound.
"""
from __future__ import annotations

import pathlib

from mapper import darkside
from mapper.app import MapScreen, MapperApp
from mapper.model import Edge, Ficha, Graph, Node
from mapper.store import MapStore
from mapper.views.layered import _tree_layout

FIXTURES = pathlib.Path(__file__).resolve().parents[1] / "fixtures"


# -- fixtures --------------------------------------------------------------
def install(tmp_path, map_id: str) -> Graph:
    """Copy a shipped fixture into a workspace and load it through `MapStore`.

    Through `MapStore.load`, never by building a `Graph` by hand, so the fixture
    exercises the real load path -- the same idiom `_legacy_graph` already uses
    in `tests/test_repair_depth.py`.
    """
    for name in (f"{map_id}.mmd", f"{map_id}_nodos.yml"):
        (tmp_path / name).write_text(
            (FIXTURES / name).read_text(encoding="utf-8"), encoding="utf-8"
        )
    return MapStore(tmp_path).load(map_id)


def pan_graph() -> Graph:
    """A map that overflows in BOTH axes on the canvas of a 118x34 TERMINAL.

    THE UNIT IS THE TERMINAL, NOT THE RENDERER, and the distinction is the whole
    correction: at a 118x34 terminal the rail and the inspector take 60 columns
    between them, so the canvas this fixture has to overflow is 58x25 -- not
    118x34.  Measured through the real screen at that terminal, `max_pan_x = 49`
    and `max_pan_y = 10`, so both chords are live.  Handed straight to the
    renderer at `w=118` the same fixture has `max_pan_x = 0`, because `_geometry`
    shrinks `card_w` until the leaves fit `avail` and a canvas that wide never
    needs the floor -- which is the reading that made this docstring look false.

    The claim is ASSERTED rather than described, at the size it names, by
    `test_the_pan_fixture_overflows_both_axes_at_the_declared_context` in
    `tests/test_pan.py`.  A shared fixture whose docstring states a measured
    property it does not have is how a driver ends up exercising a no-op while
    looking like it exercised the feature.

    Sized so the overflow is real but small: the acceptance presses the chord
    until the extent is exhausted, and the press count is derived from
    `pan_extent` at run time, never typed.  Eight branches give the width, the
    eight-deep chain gives the height.
    """
    graph = Graph()
    graph.add_node(Node(id="root", ficha=Ficha(title="raiz", meta="m")))
    for i in range(8):
        graph.add_node(Node(id=f"b{i}", ficha=Ficha(title=f"rama {i}", meta="m")))
        graph.add_edge(Edge(parent_id="root", child_id=f"b{i}"))
        graph.add_node(Node(id=f"h{i}", ficha=Ficha(title=f"hoja {i}", meta="m")))
        graph.add_edge(Edge(parent_id=f"b{i}", child_id=f"h{i}"))
    previous = "root"
    for i in range(8):
        graph.add_node(Node(id=f"c{i}", ficha=Ficha(title=f"nivel {i}", meta="m")))
        graph.add_edge(Edge(parent_id=previous, child_id=f"c{i}"))
        previous = f"c{i}"
    return graph


# -- the composited frame --------------------------------------------------
def frame_rows(screen) -> list[str]:
    """Every row of the COMPOSITED frame — what the operator actually sees."""
    return [
        "".join(seg.text for seg in strip)
        for strip in screen._compositor.render_strips()  # noqa: SLF001
    ]


def rows_in(screen, region) -> list[str]:
    """The composited frame clipped to one widget's region.

    The same screen-level clip `tests/test_repair_layout.py:74` established, and
    the one `HLR-N06.3` names normatively.  Deliberately NOT the widget's own
    `render_lines` and deliberately NOT `render().plain`.
    """
    rows = frame_rows(screen)
    band = rows[region.y: region.y + region.height]
    return [r[region.x: region.x + region.width] for r in band]


def canvas_rows(screen) -> list[str]:
    return rows_in(screen, screen.query_one("#map-canvas").region)


# -- the oracle ------------------------------------------------------------
def _child_index(graph: Graph) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for edge in graph.edges:
        index.setdefault(edge.parent_id, []).append(edge.child_id)
    return index


def hidden_under(graph: Graph, folded) -> frozenset[str]:
    """The oracle's own union-of-descendants, so it never asks the product."""
    index = _child_index(graph)
    hidden: set[str] = set()
    for start in folded:
        stack = list(index.get(start, ()))
        while stack:
            nid = stack.pop()
            if nid in hidden:
                continue
            hidden.add(nid)
            stack.extend(index.get(nid, ()))
    return frozenset(hidden)


def naive_hidden_sum(graph: Graph, folded) -> int:
    """`M-N06.3.1`: the SUM of per-branch descendant counts.

    The rule `LLR-N06.3.1` forbids, computed here so the acceptance can show the
    two rules disagreeing rather than assert that they would.
    """
    index = _child_index(graph)
    total = 0
    for start in folded:
        seen: set[str] = set()
        stack = list(index.get(start, ()))
        while stack:
            nid = stack.pop()
            if nid in seen:
                continue
            seen.add(nid)
            stack.extend(index.get(nid, ()))
        total += len(seen)
    return total


def oracle_traced(
    graph: Graph, folded, w: int, rows: list[str], pan_x: int = 0
) -> frozenset[str]:
    """`HLR-N06.3`'s normative painted-trace predicate, oracle side.

    A node counts as painted when its clipped title image is found AT THE
    COLUMNS ITS CARD OCCUPIES in one of the region-clipped painted rows.
    BOTH halves are load-bearing and the requirement measured why: the `_clip`
    image alone false-negatives 20 times over the sweep (a card partly past the
    right edge is never painted whole, but the node plainly IS painted), and a
    raw-title or raw-id trace is 0 of 8 at every width because the canvas paints
    TITLES and truncates them.

    THE ANCHOR IS NOT COSMETIC.  This predicate used to ask "does this substring
    appear SOMEWHERE in SOME row", and when `card_w` floors at 9 the title
    budget is 6 cells, so distinct titles clip to the SAME image and the oracle
    traced them all off one card.  Executed on `pan_graph` at 80x24, pan_x=24,
    four nodes shared the image `nive` and the unanchored oracle traced 21 where
    the anchored one traces 16 -- the product's own answer.  Over-tracing
    weakens `PRED-2` (`declared <= traced`), which is the predicate `02j` relies
    on to redden the placed-not-painted mutant.

    WHY THERE IS NO `pan_y` PARAMETER, stated rather than left to be noticed.
    `pan_x` moves the columns a card occupies, so the anchor has to consume it.
    The vertical component is consumed by `rows` instead: those are the rows of
    the ALREADY-PANNED frame, and a node scrolled off the top simply has no row
    holding its image.  Mapping a canvas row to a region row would need the
    header's PHYSICAL row count, which is the one number `HEADER_ROWS` is
    already only approximately right about -- so the oracle scans, and the scan
    is invariant under `pan_y` by construction.  An unused `pan_y` argument
    would be the same defect this increment is fixing one import over.
    """
    index = _child_index(graph)
    hidden = hidden_under(graph, folded)
    visible = [nid for nid in graph.nodes if nid not in hidden]
    n_leaves = sum(
        1 for nid in visible
        if not [cid for cid in index.get(nid, ()) if cid not in hidden]
    )
    gap = 3
    widest = max(
        max(len(graph.nodes[nid].ficha.title) + 3,
            len(graph.nodes[nid].ficha.meta) + 2)
        for nid in visible
    )
    card_w = min(26, max(14, widest))
    avail = w - 2
    if n_leaves * (card_w + gap) - gap > avail:
        card_w = max(9, (avail - (n_leaves - 1) * gap) // n_leaves)

    pos = _tree_layout(graph, card_w, gap, hidden)
    traced: set[str] = set()
    for nid in visible:
        cx, _level = pos[nid]
        cx = max(0, cx - card_w // 2) - pan_x
        width = max(1, card_w - 3)
        title = darkside.plain(graph.nodes[nid].ficha.title)
        if len(title) > width:
            title = title[: max(0, width - 1)] + "…"
        title = title + " " * (width - len(title))
        ink = [
            (cx + 2 + j, ch) for j, ch in enumerate(title)
            if 0 <= cx + 2 + j < avail and ch.strip()
        ]
        if ink and any(
            all(x < len(row) and row[x] == ch for x, ch in ink) for row in rows
        ):
            traced.add(nid)
    return frozenset(traced)


# -- driving the shipped screen -------------------------------------------
async def open_map(app, pilot, map_id: str) -> MapScreen:
    app.push_screen(MapScreen(map_id))
    await pilot.pause()
    await pilot.pause()
    return app.screen


async def height_offset(tmp_path, map_id: str, term_w: int, probe_h: int = 30) -> int:
    """`terminal height - renderer h` at this terminal WIDTH, MEASURED.

    B-54, stated as machinery instead of as a warning.  `run_test()` defaults to
    80x24, where `_apply_region_visibility` auto-hides the rail and the
    inspector, and the surrounding chrome's own wrapping makes the gap between
    the terminal height and the canvas region depend on the WIDTH.  Three passes
    once agreed on a false reading because nobody varied the size.  So the
    offset is measured per width and the caller then ASSERTS the configuration
    it asked for is the one it got.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=(term_w, probe_h)) as pilot:
        await pilot.pause()
        screen = await open_map(app, pilot, map_id)
        _w, h = screen._canvas_size()  # noqa: SLF001
        return probe_h - h
