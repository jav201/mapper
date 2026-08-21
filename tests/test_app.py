"""Tests for mapper.app."""
import pytest

from mapper.app import MapScreen, NavigationModel
from mapper.model import Edge, Ficha, Graph, Node


def test_navigation_model():
    g = Graph()
    g.add_node(Node(id="a"))
    g.add_node(Node(id="b"))
    g.add_node(Node(id="c"))
    g.add_edge(Edge("a", "b"))
    g.add_edge(Edge("a", "c"))
    nav = NavigationModel(g)
    assert nav.cursor == "a"
    nav.cursor = "b"
    assert nav.next_sibling() == "c"
    assert nav.prev_sibling() is None
    assert nav.parent() == "a"


def test_map_screen_renders():
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="Root")))
    g.add_node(Node(id="child", ficha=Ficha(title="Child")))
    g.add_edge(Edge("root", "child"))
    screen = MapScreen("test")
    screen.graph = g
    screen.nav = NavigationModel(g)
    # Just ensure render does not blow up
    text = screen.renderer.render(g, selected_id="root", w=60, h=20)
    assert "Root" in text.plain
