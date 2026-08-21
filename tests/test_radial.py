"""Tests for radial renderer."""
from mapper.model import Edge, Ficha, Graph, Node
from mapper.views.radial import RadialRenderer


def test_radial_renderer():
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="Root")))
    g.add_node(Node(id="a", ficha=Ficha(title="A")))
    g.add_node(Node(id="b", ficha=Ficha(title="B")))
    g.add_edge(Edge("root", "a"))
    g.add_edge(Edge("root", "b"))

    renderer = RadialRenderer()
    text = renderer.render(g, selected_id="a", w=60, h=20)
    assert "Root" in text.plain
    assert "A" in text.plain
    assert "B" in text.plain
