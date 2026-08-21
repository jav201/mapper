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
