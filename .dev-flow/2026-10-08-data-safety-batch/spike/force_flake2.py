"""Scratch: force the suspected race. Same loop as test_hlr_n16_4, plus ONE injected
late layout change (a terminal resize across the dock threshold) landing between
`before` and `after` of the inert key `left`. Expect: 'left' reported effective."""
import os, sys
sys.path.insert(0, os.getcwd())
import pytest
from textual.app import App
from mapper.app import MapperApp
from mapper.keymap import SCOPE_HELP, bindings_for
from mapper.screens.help import HelpScreen
from tests.test_help_scope import _legend_from_map, LAYOUT_SIZES, _painted_help_keys, _rows_in

async def run(tmp_path, size, perturb_key, resize_to):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        screen = await _legend_from_map(app, pilot)
        framework = set(App._merged_bindings.key_to_bindings)
        universe = {k for _n, b in screen._modal_binding_chain for k in b.key_to_bindings}
        universe |= {k for _n, b in screen._binding_chain for k, bs in b.key_to_bindings.items() if any(x.priority for x in bs)}
        universe -= framework
        effective = set()
        for key in sorted(universe):
            if not isinstance(app.screen, HelpScreen):
                await pilot.press("question_mark"); await pilot.pause(); await pilot.pause()
            pane = app.screen.query_one("#help-bindings")
            pane.scroll_to(y=pane.max_scroll_y // 2, animate=False)
            await pilot.pause()
            before = (pane.scroll_offset, len(app.screen_stack), app.screen, app.focused)
            if key == perturb_key:
                await pilot.resize_terminal(*resize_to)   # injected late reflow
            await pilot.press(key); await pilot.pause(); await pilot.pause()
            pane = app.screen.query_one("#help-bindings") if isinstance(app.screen, HelpScreen) else pane
            after = (pane.scroll_offset, len(app.screen_stack), app.screen, app.focused)
            if after != before:
                effective.add(key)
        return sorted(effective)

@pytest.mark.parametrize("perturb", [None, "left"])
async def test_force(tmp_path, perturb, capsys):
    eff = await run(tmp_path, LAYOUT_SIZES[0], perturb, (140, 90))
    with capsys.disabled():
        print(f"\nFORCE perturb={perturb} -> 'left' effective: {'left' in eff}; effective={eff}")
