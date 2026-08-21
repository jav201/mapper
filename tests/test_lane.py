"""Tests for lane renderer."""
from mapper.model import Edge, Ficha, Graph, Node
from mapper.views.lane import LaneRenderer


def test_lane_renderer():
    g = Graph()
    g.add_node(Node(id="repo", ficha=Ficha(title="repo")))
    g.add_node(Node(id="main", ficha=Ficha(title="main", meta="+0/-0")))
    g.add_node(Node(id="feat", ficha=Ficha(title="feat", meta="+3/-1", state="risk")))
    g.add_edge(Edge("repo", "main"))
    g.add_edge(Edge("repo", "feat"))

    renderer = LaneRenderer()
    text = renderer.render(g, selected_id="feat", w=60, h=20)
    assert "main" in text.plain
    assert "feat" in text.plain
    assert "+3/-1" in text.plain
