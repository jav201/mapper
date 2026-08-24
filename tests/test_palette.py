"""Tests for the darkside command palette."""
from __future__ import annotations

from mapper.app import MapperApp
from mapper.screens.palette import CommandPalette


async def test_ctrl_p_opens_darkside_palette(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_palette()
        await pilot.pause()
        assert isinstance(app.screen, CommandPalette)


async def test_palette_dispatches_selected_action(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        store = app.store
        Node = __import__("mapper.model", fromlist=["Node"]).Node
        Ficha = __import__("mapper.model", fromlist=["Ficha"]).Ficha
        Graph = __import__("mapper.model", fromlist=["Graph"]).Graph
        g = Graph()
        g.add_node(Node(id="root", ficha=Ficha(title="Root")))
        store.save("palette-test", g)

        from mapper.app import MapScreen

        app.push_screen(MapScreen("palette-test"))
        await pilot.pause()

        app.action_palette()
        await pilot.pause()
        palette = app.screen
        assert isinstance(palette, CommandPalette)

        # Search for "add" and run the first match.
        input_widget = palette.query_one("#palette-input")
        input_widget.value = "add"
        await pilot.pause()
        palette.action_run_selected()
        await pilot.pause()
        # The action pushed a prompt modal for the child name.
        assert not isinstance(app.screen, CommandPalette)
