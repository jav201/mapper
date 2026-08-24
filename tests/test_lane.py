"""Tests for lane renderer."""
from mapper.model import Edge, Ficha, Graph, Node
from mapper.views.lane import HybridLaneRenderer, LaneRenderer, RailTimelineRenderer


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


def test_rail_timeline_renderer():
    g = Graph()
    g.add_node(Node(id="repo", ficha=Ficha(title="repo")))
    g.add_node(Node(id="main", ficha=Ficha(title="main", meta="+0/-0")))
    g.add_node(Node(id="feat", ficha=Ficha(title="feature/auth", meta="+4/-2", notes="CI: pending")))
    g.add_edge(Edge("repo", "main"))
    g.add_edge(Edge("repo", "feat"))

    renderer = RailTimelineRenderer()
    text = renderer.render(g, selected_id="feat", w=80, h=24)
    assert "feature/auth" in text.plain
    assert "+4/-2" in text.plain
    assert "run" in text.plain or "pending" in text.plain


def test_hybrid_lane_renderer():
    g = Graph()
    g.add_node(Node(id="repo", ficha=Ficha(title="repo")))
    g.add_node(Node(id="main", ficha=Ficha(title="main", meta="+0/-0")))
    g.add_node(Node(id="hotfix", ficha=Ficha(title="hotfix/db", meta="+1/-5", notes="CI: fail")))
    g.add_edge(Edge("repo", "main"))
    g.add_edge(Edge("repo", "hotfix"))

    renderer = HybridLaneRenderer()
    text = renderer.render(g, selected_id="hotfix", w=80, h=20)
    assert "hotfix/db" in text.plain
    assert "+1" in text.plain
    assert "fail" in text.plain
