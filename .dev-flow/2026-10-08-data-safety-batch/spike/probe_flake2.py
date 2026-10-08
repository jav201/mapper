"""Scratch probe for FLAKE-2: same scenario as test_hlr_n16_4, but logs per-key before/after."""
import sys, os
sys.path.insert(0, os.getcwd())
import pytest
from textual.app import App
from mapper.app import MapperApp
from mapper.keymap import SCOPE_HELP, bindings_for
from tests.test_help_scope import _legend_from_map, LAYOUT_SIZES

@pytest.mark.parametrize("size", LAYOUT_SIZES)
async def test_probe(tmp_path, size, capsys):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        screen = await _legend_from_map(app, pilot)
        framework = set(App._merged_bindings.key_to_bindings)
        universe = {k for _n, b in screen._modal_binding_chain for k in b.key_to_bindings}
        universe |= {k for _n, b in screen._binding_chain for k, bs in b.key_to_bindings.items() if any(x.priority for x in bs)}
        universe -= framework
        with capsys.disabled():
            print("\nSIZE", size, "universe", sorted(universe), "declared", sorted(b.key for b in bindings_for(SCOPE_HELP)))
            pane = screen.query_one("#help-bindings")
            print(" pane max_scroll_x/y", pane.max_scroll_x, pane.max_scroll_y, "virtual", pane.virtual_size, "size", pane.size, "focused", app.focused)
            from mapper.screens.help import HelpScreen
            for key in sorted(universe):
                if not isinstance(app.screen, HelpScreen):
                    await pilot.press("question_mark"); await pilot.pause(); await pilot.pause()
                pane = app.screen.query_one("#help-bindings")
                pane.scroll_to(y=pane.max_scroll_y // 2, animate=False)
                await pilot.pause()
                before = (pane.scroll_offset, len(app.screen_stack), app.screen, app.focused)
                await pilot.press(key); await pilot.pause(); await pilot.pause()
                after = (pane.scroll_offset, len(app.screen_stack), app.screen, app.focused)
                print("  ", key, "EFFECTIVE" if before != after else "-", before if before != after else "", after if before != after else "")
