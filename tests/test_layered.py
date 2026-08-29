"""Unit tests for mapper.views.layered."""
import ast
import pathlib

from mapper import darkside
from mapper.model import Edge, Ficha, Graph, Node
from mapper.views.state import ViewState
from mapper.views.layered import LayeredRenderer
from tests.inc4_support import QUERY, build_adjuntos, narrow_hits


def test_layered_renderer_produces_text():
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="Root", meta="m1")))
    g.add_node(Node(id="child", ficha=Ficha(title="Child", meta="m2")))
    g.add_edge(Edge("root", "child"))

    renderer = LayeredRenderer()
    text = renderer.render(g, ViewState(selected_id="root", w=60, h=20))
    assert "Root" in text.plain
    assert "Child" in text.plain


def test_layered_renderer_handles_forest_without_crash():
    """A graph with disconnected trees should render all nodes."""
    g = Graph()
    g.add_node(Node(id="a", ficha=Ficha(title="Árbol A")))
    g.add_node(Node(id="b", ficha=Ficha(title="Hoja A")))
    g.add_node(Node(id="c", ficha=Ficha(title="Árbol B")))
    g.add_edge(Edge("a", "b"))
    # No edge connecting c; g.root_id will be 'a' by default.

    renderer = LayeredRenderer()
    text = renderer.render(g, ViewState(selected_id="a", w=80, h=20))
    assert "Árbol A" in text.plain
    assert "Hoja A" in text.plain
    assert "Árbol B" in text.plain


def _selection_style(text, title: str) -> str:
    """The style covering the selected card's own glyphs."""
    start = text.plain.index(title)
    return " ".join(
        str(s.style) for s in text.spans if s.start <= start < s.end
    )


def _graph():
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="Raiz")))
    g.add_node(Node(id="child", ficha=Ficha(title="Hijo")))
    g.add_edge(Edge("root", "child"))
    return g


def test_at_010_the_selection_tone_follows_the_focus_owner():
    """Carry B-05: the canvas claimed the selection wherever the keyboard was.

    Three regions each painted a full-strength selection at once, so none of
    them told the operator which one would answer the next key.

    This drives a NON-DEFAULT value and asserts the captured tone actually
    changed.  A test run at the default would confirm the default and say
    nothing about the wiring.
    """
    renderer = LayeredRenderer()
    focused = renderer.render(_graph(), ViewState(selected_id="root", w=60, h=20,
                                                  focus_owner="canvas"))
    elsewhere = renderer.render(_graph(), ViewState(selected_id="root", w=60, h=20,
                                                    focus_owner="inspector"))

    assert focused.plain == elsewhere.plain, (
        "the difference must be TONE only -- the same characters, so the "
        "operator does not lose their place when focus moves"
    )
    assert _selection_style(focused, "Raiz") != _selection_style(elsewhere, "Raiz")


def test_at_010_an_unknown_focus_owner_paints_what_the_tree_painted_before():
    """The default is what keeps the signature migration byte-identical.

    `""` means "nobody told us", and every byte-identity digest in the suite
    renders through it.  If the unknown owner dimmed the selection, the four
    re-baselined pins and the eight held ones would all move for a reason that
    has nothing to do with the migration.
    """
    renderer = LayeredRenderer()
    unknown = renderer.render(_graph(), ViewState(selected_id="root", w=60, h=20))
    canvas = renderer.render(_graph(), ViewState(selected_id="root", w=60, h=20,
                                                 focus_owner="canvas"))
    assert _selection_style(unknown, "Raiz") == _selection_style(canvas, "Raiz")


def test_at_010_every_declared_focus_owner_is_accepted():
    """The domain is declared, so a value outside it is a spec question, not a
    silent fallthrough.  Derived from the declaration, never re-typed."""
    from mapper.views.state import FOCUS_OWNERS

    assert FOCUS_OWNERS[0] == "", "the unknown owner must be the first declared value"
    renderer = LayeredRenderer()
    tones = {
        owner: _selection_style(
            renderer.render(_graph(), ViewState(selected_id="root", w=60, h=20,
                                                focus_owner=owner)),
            "Raiz",
        )
        for owner in FOCUS_OWNERS
    }
    assert len(set(tones.values())) == 2, (
        f"expected exactly two tones -- active and inactive -- got {tones}"
    )


# --------------------------------------------------------------------------
# LLR-N07.1.1 / AT-021 — the renderer's own hit predicate is DELETED


def _hit_style() -> str:
    """The hit tone, read from `darkside` at run time.

    Never a hex literal: the palette moves, and a test that pins `#f5f5f5 on
    #262626` goes stale the first time it does while still looking like it
    asserts the hit style.
    """
    return f"{darkside.INK} on {darkside.STEP}"


def _hit_image(text) -> str:
    """The characters the renderer painted with the hit style, in order.

    Read off the returned `Text`'s SPANS, never by substring search: the canvas
    paints titles and a substring probe cannot tell "this node is a hit" from
    "some node whose title contains these letters is".
    """
    style = _hit_style()
    return "".join(text.plain[s.start:s.end] for s in text.spans if s.style == style)


def test_at_021_hits_come_from_the_state(tmp_path):
    """AT-021 — the renderer paints the hit set it was HANDED.

    P-021.1, the arm a RENAME cannot satisfy.  The injected id is `f`
    (`Hallazgos`), which neither definition of "hit" would ever return for this
    query -- asserted here for BOTH definitions rather than assumed -- so a
    renderer still deciding for itself paints nothing and the arm fails.  A
    deletion asserted only by absence is satisfied by a rename; this is not.
    """
    graph = build_adjuntos(tmp_path)
    injected = "f"

    # The counterfactual, executed: no predicate in this tree would elect `f`.
    assert injected not in graph.search_hits(QUERY)
    assert injected not in narrow_hits(graph, QUERY)
    title = graph.nodes[injected].ficha.title

    renderer = LayeredRenderer()
    state = ViewState(selected_id=graph.root_id, w=58, h=26)

    # The negative control FIRST: with an empty hit set nothing carries the hit
    # style at all, so the positive arm below is about the set and not about the
    # style existing somewhere on every frame.
    assert _hit_image(renderer.render(graph, state)) == ""

    painted = _hit_image(
        renderer.render(graph, ViewState(
            selected_id=graph.root_id, w=58, h=26,
            hits=frozenset({injected}),
        ))
    )
    assert title[:6] in painted, (title, painted)

    # And it is EXACTLY that node: a second render naming a different id paints
    # a different card, which is what stops "the hit style appears somewhere"
    # from passing as "the injected id was painted".
    other = _hit_image(
        renderer.render(graph, ViewState(
            selected_id=graph.root_id, w=58, h=26,
            hits=frozenset({"c"}),
        ))
    )
    assert graph.nodes["c"].ficha.title[:6] in other
    assert title[:6] not in other

    # P-021.2 — the deletion census, in the SAME node.  `C-18` asks one
    # acceptance id to drive its whole named chain from one place, and this
    # chain has two ends: the renderer paints what it is handed (above) AND the
    # thing that used to decide is gone (below).  Split across two nodes, the id
    # maps to two and the traceability edge stops being an edge.
    #
    # DERIVED BY AST, NEVER BY GREP.  A grep cannot separate a call from a
    # MENTION -- this tree has already been bitten by a docstring that made a
    # census read one site too many -- and an absence-only assertion is
    # satisfied by a RENAME, which is why the arm above exists beside this one.
    #
    # Executed pre-state at the increment's entry commit: 1 `FunctionDef` named
    # `_matches` and 9 `qlower` bindings/loads, all in `layered.py`
    # (`lane.py` 0, `outline.py` 0, `radial.py` 0, `state.py` 0, `__init__.py` 0).
    views = pathlib.Path(__file__).resolve().parents[1] / "mapper" / "views"
    modules = sorted(views.rglob("*.py"))
    assert len(modules) >= 5, f"the derived module set collapsed: {modules}"

    predicates = 0
    parameter_uses = 0
    for module in modules:
        tree = ast.parse(module.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_matches":
                predicates += 1
            if isinstance(node, ast.Name) and node.id == "qlower":
                parameter_uses += 1
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                parameter_uses += sum(1 for a in node.args.args if a.arg == "qlower")

    assert predicates == 0
    assert parameter_uses == 0
