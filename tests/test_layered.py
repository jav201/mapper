"""Unit tests for mapper.views.layered."""
from mapper.model import Edge, Ficha, Graph, Node
from mapper.views.layered import LayeredRenderer


def test_layered_renderer_produces_text():
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="Root", meta="m1")))
    g.add_node(Node(id="child", ficha=Ficha(title="Child", meta="m2")))
    g.add_edge(Edge("root", "child"))

    renderer = LayeredRenderer()
    text = renderer.render(g, selected_id="root", w=60, h=20)
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
    text = renderer.render(g, selected_id="a", w=80, h=20)
    assert "Árbol A" in text.plain
    assert "Hoja A" in text.plain
    assert "Árbol B" in text.plain
