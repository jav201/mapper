"""Unit tests for mapper.views.layered."""
from mapper.model import Edge, Ficha, Graph, Node
from mapper.views.state import ViewState
from mapper.views.layered import LayeredRenderer


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
