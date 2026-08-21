"""Tests for outline renderer."""
from mapper.model import Edge, Ficha, Graph, Node
from mapper.views.outline import OutlineRenderer


def test_outline_renderer():
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="Root", meta="meta")))
    g.add_node(Node(id="child", ficha=Ficha(title="Child")))
    g.add_edge(Edge("root", "child"))

    renderer = OutlineRenderer()
    text = renderer.render(g, w=60, h=20)
    assert "Root" in text.plain
    assert "Child" in text.plain
    assert "  - Child" in text.plain
