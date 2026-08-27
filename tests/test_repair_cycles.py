"""HLR-R01 — a map whose edge set contains a directed cycle is refused, not fatal.

S-01a: `mermaid.parse` accepted `c --> a`; both renderers then raised
`RecursionError` and `MapScreen.refresh_canvas` had no guard, so the exception
escaped the Textual message pump and the application died.

The arrow the cycle path is joined by is U+2192; it is constructed here rather
than spelled, so this file stays ASCII and a mangled separator cannot pass
unnoticed.
"""
from __future__ import annotations

import pytest
from textual.widgets import Static

from mapper.app import HomeScreen, MapScreen, MapperApp
from mapper.mermaid import CYCLE_ARROW, MermaidError, parse
from mapper.model import Edge, Ficha, Graph, Node
from mapper.store import MapStoreError

ARROW = chr(0x2192)

CYCLE_MMD = "graph TD\n    a[A] --> b[B]\n    b --> c[C]\n    c --> a\n"
OTHER_CYCLE_MMD = "graph TD\n    x[X] --> y[Y]\n    y --> x\n"
ACYCLIC_MMD = "graph TD\n    root[Root] --> a[A]\n    a --> b[B]\n    root --> c[C]\n"


def _diamond() -> Graph:
    """a fans out to b and c, both of which point at d.

    `d` is reached twice down two different branches.  That is a legitimate
    shape, not a cycle, and a refusal that flags it is a false refusal — the
    arm §4 of the requirements prices as high as passing wrong work.
    """
    graph = Graph()
    for nid in ("a", "b", "c", "d"):
        graph.add_node(Node(id=nid, ficha=Ficha(title=nid.upper())))
    graph.add_edge(Edge("a", "b"))
    graph.add_edge(Edge("a", "c"))
    graph.add_edge(Edge("b", "d"))
    graph.add_edge(Edge("c", "d"))
    return graph


def _graph_from_pairs(pairs: list[tuple[str, str]]) -> Graph:
    graph = Graph()
    for parent, child in pairs:
        for nid in (parent, child):
            if nid not in graph.nodes:
                graph.add_node(Node(id=nid))
        graph.add_edge(Edge(parent, child))
    return graph


# ---------------------------------------------------------------- LLR-R01.1


def test_tc_r01_find_cycle_reports_a_multi_node_cycle_in_traversal_order():
    """The real case: the cycle closes three edges away from where it started.

    A detector that only compares an edge's two endpoints reports nothing here,
    which is exactly how S-01a shipped.
    """
    graph = _graph_from_pairs([("a", "b"), ("b", "c"), ("c", "a")])

    cycle = graph.find_cycle()

    assert cycle == ["a", "b", "c", "a"], cycle
    # The entry node is repeated last, so the path reads as a closed loop.
    assert cycle[0] == cycle[-1]


def test_tc_r02_find_cycle_terminates_on_a_self_loop():
    """An edge from a node to itself is the degenerate cycle and must terminate."""
    graph = _graph_from_pairs([("a", "a")])

    assert graph.find_cycle() == ["a", "a"]


def test_tc_r03_find_cycle_returns_none_for_a_diamond():
    """Two parents is a legitimate shape; re-visiting is not re-entering.

    This is the discriminating negative for the detector itself: a rule that
    calls any second visit a cycle would deny this correct map.
    """
    assert _diamond().find_cycle() is None


def test_tc_r03b_find_cycle_searches_every_disconnected_component():
    """The cycle is in the second component, which a root-only walk never enters."""
    graph = _graph_from_pairs([("r", "s"), ("p", "q"), ("q", "p")])

    cycle = graph.find_cycle()

    assert cycle is not None
    assert set(cycle) == {"p", "q"}


def test_tc_r04_find_cycle_uses_no_recursion_at_depth_that_would_blow_the_stack():
    """A 5000-deep acyclic chain: iterative returns None, recursive would raise.

    The bound is chosen well above `sys.getrecursionlimit()` so that raising the
    limit — the plausible-weaker fix for depth — would not rescue a recursive
    implementation here either.
    """
    pairs = [(f"n{i}", f"n{i + 1}") for i in range(5000)]

    assert _graph_from_pairs(pairs).find_cycle() is None


def test_tc_r04b_find_cycle_finds_a_cycle_closing_at_the_end_of_a_deep_chain():
    """Depth and cyclicity together: the back edge is 5000 nodes from the entry."""
    pairs = [(f"n{i}", f"n{i + 1}") for i in range(5000)]
    pairs.append(("n5000", "n0"))

    cycle = _graph_from_pairs(pairs).find_cycle()

    assert cycle is not None
    assert cycle[0] == "n0" and cycle[-1] == "n0"
    assert len(cycle) == 5002


def test_find_cycle_returns_none_for_an_empty_graph():
    assert Graph().find_cycle() is None


# ---------------------------------------------------------------- LLR-R01.2


def test_tc_r05_parse_refuses_a_cycle_and_names_the_path():
    with pytest.raises(MermaidError) as excinfo:
        parse(CYCLE_MMD)

    assert excinfo.value.cycle == ["a", "b", "c", "a"]
    assert f"a{ARROW}b{ARROW}c{ARROW}a" in str(excinfo.value)


def test_tc_r05b_the_cycle_separator_is_u2192():
    """Pinned by codepoint, so a look-alike separator cannot pass this file."""
    assert CYCLE_ARROW == ARROW
    assert ord(CYCLE_ARROW) == 0x2192


def test_tc_r06_parse_still_accepts_an_acyclic_map():
    """The discriminating negative for the parser: refusal must not be blanket."""
    graph = parse(ACYCLIC_MMD)

    assert set(graph.nodes) == {"root", "a", "b", "c"}
    assert graph.root_id == "root"
    assert graph.parent_of("b") == "a"


def test_tc_r06b_parse_refuses_a_self_loop():
    with pytest.raises(MermaidError) as excinfo:
        parse("graph TD\n    a[A] --> a\n")

    assert excinfo.value.cycle == ["a", "a"]


# ---------------------------------------------------------------- LLR-R01.3


def test_tc_r07_store_load_surfaces_the_cycle_as_a_spanish_map_store_error(tmp_store):
    (tmp_store.workspace / "ciclico.mmd").write_text(CYCLE_MMD, encoding="utf-8")

    with pytest.raises(MapStoreError) as excinfo:
        tmp_store.load("ciclico")

    assert str(excinfo.value) == f"el mapa tiene un ciclo: a{ARROW}b{ARROW}c{ARROW}a"


# ---------------------------------------------------------------- LLR-R01.4


class _Boom:
    """A renderer that fails the way a cyclic graph made the shipped ones fail."""

    def __init__(self, exc: Exception):
        self.exc = exc

    def render(self, *args, **kwargs):
        raise self.exc


@pytest.mark.parametrize(
    "exc",
    [
        RecursionError("maximum recursion depth exceeded"),
        ValueError("something this batch never anticipated"),
    ],
    ids=["recursion-error", "unanticipated-error"],
)
async def test_tc_r08_refresh_canvas_survives_any_renderer_exception(tmp_path, exc):
    """The sink class, not the two exception types this batch happens to know.

    Batch 1 §2.1b: a guard written for the named cases is satisfied at those
    cases' boundary while its siblings keep the defect, so the second parameter
    is an exception type nothing in this increment produces.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        graph = Graph()
        graph.add_node(Node(id="root", ficha=Ficha(title="Root")))
        app.store.save("sano", graph)

        app.push_screen(MapScreen("sano"))
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, MapScreen)

        screen._current_renderer = lambda: _Boom(exc)
        screen.refresh_canvas()
        await pilot.pause()

        # The app is still alive and still on the map screen ...
        assert app.screen is screen
        # ... and the canvas carries the Spanish notice rather than a picture.
        painted = screen.query_one("#map-canvas", Static).render().plain
        assert "no se pudo dibujar el mapa" in painted


async def test_tc_r09_home_screen_notices_a_refused_map_and_still_lists_the_rest(
    tmp_path,
):
    """AT-R01 through the shipped surface: the sala loads every map on mount."""
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        store = app.store
        good = Graph()
        good.add_node(Node(id="root", ficha=Ficha(title="Root")))
        good.add_node(Node(id="a", ficha=Ficha(title="A")))
        good.add_edge(Edge("root", "a"))
        store.save("sano", good)
        (store.workspace / "ciclico.mmd").write_text(CYCLE_MMD, encoding="utf-8")
        store.record_session("ciclico", "a")

        notices: list[str] = []
        app.notify = lambda msg, **kw: notices.append(str(msg))

        app.push_screen(HomeScreen())
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, HomeScreen)

        # The operator is told, in Spanish, which map and which cycle.
        assert any(
            "no se pudo cargar ciclico" in n
            and f"a{ARROW}b{ARROW}c{ARROW}a" in n
            for n in notices
        ), notices
        # And the screen still works: the healthy map is listed.
        table = screen.query_one("#home-recents")
        assert "sano" in {str(k.value) for k in table.rows}


@pytest.mark.parametrize(
    "raised",
    [
        MapStoreError("el mapa tiene un ciclo: a → b → a"),
        RuntimeError("algo inesperado"),
        KeyError("root"),
        TypeError("'int' object has no attribute 'strip'"),
        ValueError("valor raro"),
    ],
    ids=["batch_own", "runtime", "key", "type", "value"],
)
async def test_tc_r09b_the_home_sink_is_scoped_to_the_class_not_to_this_batch(
    tmp_path, raised
):
    """LLR-R01.4's BREADTH, armed (increment 1, finding F2).

    TC-R09 drives only the exception type THIS batch produces, so narrowing the
    handler to `except MapStoreError` reddens nothing across the whole tree —
    the code was correct and no node said so, which is the exact failure the
    LLR's own rationale cites.  The unrelated types below are the arms: they are
    not types the batch knows about, which is the point of a sink-CLASS guard.

    `TypeError` is here deliberately — it is what a malformed ficha field raised
    before increment 3, so it is the sibling defect, not a hypothetical.

    Since re-gate finding `G1` this node also arms the markup defense at the
    THIRD sink `HomeScreen.load_or_notice` opens — the load-FAILURE branch, which
    `C3` never reached because it named only the two load-warning sinks.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        store = app.store
        good = Graph()
        good.add_node(Node(id="root", ficha=Ficha(title="Root")))
        store.save("sano", good)
        store.record_session("sano", "root")

        real_load = store.load

        def exploding_load(name: str):
            if name == "sano":
                raise raised
            return real_load(name)

        store.load = exploding_load
        # The kwargs are CAPTURED, not discarded (G1).  A stub spelled
        # `lambda msg, **kw: notices.append(str(msg))` throws away the only thing
        # defending this sink — verbatim the mechanism finding F3 identified at
        # the other two.
        notices: list[tuple[str, dict]] = []
        app.notify = lambda msg, **kw: notices.append((str(msg), kw))

        app.push_screen(HomeScreen())
        await pilot.pause()

        # The screen survives whatever came out of the load ...
        assert isinstance(app.screen, HomeScreen)
        # ... and the operator is told, in Spanish, which map failed.
        hits = [(m, kw) for m, kw in notices if "no se pudo cargar sano" in m]
        assert hits, (raised, notices)
        # `hits` is asserted non-empty BEFORE the `all(...)`, because `all()` over
        # an empty list is True and would certify the defense of a sink that never
        # fired.
        #
        # The markup defense at the third sink.  `notify` defaults to
        # `markup=True` and `darkside.plain` deliberately PRESERVES markup, so
        # `markup=False` is the whole defense — over text that is file-derived:
        # `MapStoreError` interpolates node ids read out of a sidecar.
        assert all(kw.get("markup") is False for _, kw in hits), hits


async def test_tc_r08b_import_preview_survives_a_cyclic_csv(tmp_path):
    """The sibling sink, found by the reverse census and reproduced.

    `_ImportPreviewScreen.refresh_canvas` renders from inside `on_mount`, and a
    CSV whose `parent` column is circular builds a cyclic graph that never goes
    near `mermaid.parse` — so the parser's refusal cannot protect it.  A guard
    written only at the two symbols the requirement names leaves this door open,
    which is precisely the shape LLR-R01.4's rationale cites.
    """
    from mapper.app import _ImportPreviewScreen
    from mapper.import_csv import preview_csv

    csv_path = tmp_path / "ciclico.csv"
    csv_path.write_text("id,title,parent\na,A,c\nb,B,a\nc,C,b\n", encoding="utf-8")
    graph = preview_csv(csv_path)
    # The precondition this test rests on: the CSV really is cyclic.
    assert graph.find_cycle() is not None

    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        app.push_screen(_ImportPreviewScreen(graph, csv_path))
        await pilot.pause()

        assert isinstance(app.screen, _ImportPreviewScreen)
        painted = app.screen.query_one("#import-preview-canvas", Static).render().plain
        assert "no se pudo dibujar la vista previa" in painted


# ------------------------------------------------------- AT-R01 / R02 / R03


async def test_at_r01_opening_a_cyclic_map_refuses_it_without_killing_the_app(
    tmp_path,
):
    """The end-to-end oracle: open the cycle map on the real MapScreen."""
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        (app.store.workspace / "ciclico.mmd").write_text(CYCLE_MMD, encoding="utf-8")

        notices: list[str] = []
        app.notify = lambda msg, **kw: notices.append(str(msg))

        app.push_screen(MapScreen("ciclico"))
        await pilot.pause()

        assert isinstance(app.screen, MapScreen)
        assert any("error cargando mapa" in n and "ciclo" in n for n in notices), notices
        assert any(f"a{ARROW}b{ARROW}c{ARROW}a" in n for n in notices), notices

        # Still usable: the screen paints and answers a keypress.
        await pilot.press("j")
        await pilot.pause()
        assert isinstance(app.screen, MapScreen)


def test_at_r02_the_message_names_the_actual_cycle_not_a_fixed_string(tmp_store):
    """Two different cycles must produce two different messages, each its own."""
    (tmp_store.workspace / "uno.mmd").write_text(CYCLE_MMD, encoding="utf-8")
    (tmp_store.workspace / "dos.mmd").write_text(OTHER_CYCLE_MMD, encoding="utf-8")

    with pytest.raises(MapStoreError) as first:
        tmp_store.load("uno")
    with pytest.raises(MapStoreError) as second:
        tmp_store.load("dos")

    prefix = "el mapa tiene un ciclo: "
    one, two = str(first.value), str(second.value)
    assert one != two
    # Read the path back out of each message rather than searching for a
    # substring: the Spanish prefix itself contains letters used as node ids.
    path_one = one[len(prefix):].split(ARROW)
    path_two = two[len(prefix):].split(ARROW)

    # Whole path, not just its head — the arm that names only the first node
    # reads correct and reddens exactly here.
    assert path_one == ["a", "b", "c", "a"]
    assert path_two == ["x", "y", "x"]
    # Each message names only its own nodes: a message that concatenated both
    # cycles would pass the inequality above.
    assert set(path_one).isdisjoint(path_two)


def test_at_r03_an_acyclic_map_still_loads(tmp_store):
    """A refusal that refuses everything is not a fix — and neither is a
    refusal that flags a legitimate diamond.

    Both negatives live on this one node.  A tree alone is inert against the
    false-refusal arm, because a tree re-visits nothing: measured, the
    "any re-visited node is a cycle" mutant leaves a tree-only oracle green.
    """
    (tmp_store.workspace / "sano.mmd").write_text(ACYCLIC_MMD, encoding="utf-8")

    graph = tmp_store.load("sano")

    assert set(graph.nodes) == {"root", "a", "b", "c"}
    assert graph.root_id == "root"
    assert graph.find_cycle() is None
    # The false-refusal half: two parents is a shape, not a cycle.
    assert _diamond().find_cycle() is None


def test_at_r03b_a_diamond_is_not_called_a_cycle(tmp_path):
    """The false-refusal arm's fixture.

    A diamond cannot round-trip through the store: `mermaid.parse` has refused
    two parents as out of MVP scope since long before this batch, so the
    strongest available statement is that the *cycle* rule does not claim it.
    Both halves matter — `find_cycle` returns `None`, and the parser's refusal
    of the diamond's own mermaid text is still the pre-existing multiple-parents
    `ParseError` and never a `MermaidError`.  An arm that calls any re-visited
    node a cycle reddens on the first assertion.
    """
    from mapper.mermaid import ParseError, dump

    diamond = _diamond()
    assert diamond.find_cycle() is None

    with pytest.raises(ParseError) as excinfo:
        parse(dump(diamond))
    assert not isinstance(excinfo.value, MermaidError)
    assert "multiple parents" in str(excinfo.value)
