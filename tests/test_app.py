"""Tests for mapper.app."""
import pytest

from mapper.app import MapScreen, MapperApp, NavigationModel
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


async def test_focus_active_blocks_structural_edits(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        # Seed a map with two children.
        store = app.store
        g = Graph()
        g.add_node(Node(id="root", ficha=Ficha(title="Root")))
        g.add_node(Node(id="keep", ficha=Ficha(title="Keep")))
        g.add_node(Node(id="focus-root", ficha=Ficha(title="Focus Root")))
        g.add_edge(Edge("root", "keep"))
        g.add_edge(Edge("root", "focus-root"))
        store.save("focus-test", g)

        app.push_screen(MapScreen("focus-test"))
        await pilot.pause()
        screen = app.screen
        screen.nav.cursor = "focus-root"
        screen.action_toggle_focus()
        await pilot.pause()
        assert screen.focus_active

        # Attempt to add a child while focused: should be blocked.
        screen.action_add_child()
        await pilot.pause()
        # Map on disk must still contain all original nodes.
        loaded = store.load("focus-test")
        assert set(loaded.nodes) == {"root", "keep", "focus-root"}
