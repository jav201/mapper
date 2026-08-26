"""Black-box tests for the command palette and the scoped help overlay (US-N03).

Every test here drives the REAL mechanism — `pilot.press` with the actual keys —
because the design that approved this batch was a static SVG and proves nothing
about Textual's key routing (control C-16).
"""
from __future__ import annotations

from mapper import keymap
from mapper.app import MapperApp, MapScreen
from mapper.model import Edge, Ficha, Graph, Node
from mapper.screens.help import HelpScreen
from mapper.screens.palette import CommandPalette


def _seed(app, map_id="palette-test"):
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="Root")))
    g.add_node(Node(id="child", ficha=Ficha(title="Child")))
    g.add_edge(Edge("root", "child"))
    app.store.save(map_id, g)
    return map_id


async def test_ctrl_p_opens_darkside_palette(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("ctrl+p")
        await pilot.pause()
        assert isinstance(app.screen, CommandPalette)


async def test_at_n03c_palette_is_scoped_to_the_active_screen(tmp_path):
    """AT-N03c — the palette offers exactly the scope of the screen that opened it.

    RED mutation: make `palette_items` ignore its scope argument; home-only entries
    then appear in a map's palette and this assertion fails.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        app.push_screen(MapScreen(_seed(app)))
        await pilot.pause()
        await pilot.press("ctrl+p")
        await pilot.pause()
        palette = app.screen
        assert isinstance(palette, CommandPalette)
        assert palette.scope == keymap.SCOPE_MAP
        offered = {b.action for b in palette._items}
        assert "coverage" in offered
        assert "consult" not in offered, "a home-only action leaked into the map palette"
        assert "table_down" not in offered


async def test_at_n03b_selecting_a_palette_entry_executes_it(tmp_path):
    """AT-N03b — a palette entry actually runs its action, through the real chain.

    Drives: real `ctrl+p` -> type a query -> real `enter`.  The oracle is the
    observable effect (the coverage screen is now on top), not "the palette closed"
    — the old test asserted the latter and passed while dispatching nothing.

    RED mutation: revert `KeyBinding.action` for `coverage` to the Spanish label
    "cobertura"; `action_cobertura` does not exist, nothing is pushed, and the
    CoverageScreen assertion fails.
    """
    from mapper.screens.coverage import CoverageScreen

    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        app.push_screen(MapScreen(_seed(app)))
        await pilot.pause()

        await pilot.press("ctrl+p")
        await pilot.pause()
        palette = app.screen
        assert isinstance(palette, CommandPalette)

        palette.query_one("#palette-input").value = "cobertura"
        await pilot.pause()
        assert [b.action for b in palette._items] == ["coverage"], (
            "the query must narrow to exactly one entry for this test to be exact"
        )

        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, CoverageScreen), (
            "selecting 'cobertura' must execute action_coverage, not merely close the palette"
        )


async def test_at_n03d_help_shows_exactly_the_active_scope(tmp_path):
    """AT-N03d — `?` shows the keys that work here, and none that do not.

    RED mutation: render the whole KEYMAP instead of `bindings_for(self.scope)`;
    "consultar mapas" then appears in a map's help and the absence assertion fails.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        app.push_screen(MapScreen(_seed(app)))
        await pilot.pause()
        await pilot.press("question_mark")
        await pilot.pause()
        help_screen = app.screen
        assert isinstance(help_screen, HelpScreen)
        assert help_screen.scope == keymap.SCOPE_MAP

        shown = help_screen.query_one("#help-content").render().plain
        for binding in keymap.bindings_for(keymap.SCOPE_MAP):
            assert binding.label in shown, f"{binding.label} works here but help hides it"
        assert "consultar mapas" not in shown, "help advertises a key that does nothing here"


async def test_palette_empty_query_dispatches_nothing(tmp_path):
    """Boundary: a query matching no entry must not dispatch anything.

    This is the case the superseded test accidentally exercised while claiming to
    prove dispatch.  Here it is asserted deliberately, as a negative.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        app.push_screen(MapScreen(_seed(app)))
        await pilot.pause()
        await pilot.press("ctrl+p")
        await pilot.pause()
        palette = app.screen
        palette.query_one("#palette-input").value = "zzzzznotacommand"
        await pilot.pause()
        assert palette._items == []
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, MapScreen), "an empty result must fall back to the map"
