"""Scratch: the n16_4 loop, instrumented. Records, per run, any key that is 'effective' but
NOT in the declared set, with the before/after tuple and the pane geometry, so the
cause of a spurious 'effective' can be read off."""
import os, sys
sys.path.insert(0, os.getcwd())
from textual.app import App
from mapper.app import MapperApp
from mapper.keymap import SCOPE_HELP, bindings_for
from mapper.screens.help import HelpScreen
from tests.test_help_scope import _legend_from_map, LAYOUT_SIZES

N = int(os.environ.get("SPIKE_N", "50"))

async def test_trace(tmp_path_factory, capsys):
    hits = 0
    for i in range(N):
        app = MapperApp(tmp_path_factory.mktemp("t"))
        async with app.run_test(size=LAYOUT_SIZES[0]) as pilot:
            screen = await _legend_from_map(app, pilot)
            declared = {b.key for b in bindings_for(SCOPE_HELP)}
            framework = set(App._merged_bindings.key_to_bindings)
            universe = {k for _n, b in screen._modal_binding_chain for k in b.key_to_bindings}
            universe |= {k for _n, b in screen._binding_chain for k, bs in b.key_to_bindings.items() if any(x.priority for x in bs)}
            universe -= framework
            for key in sorted(universe):
                if not isinstance(app.screen, HelpScreen):
                    await pilot.press("question_mark"); await pilot.pause(); await pilot.pause()
                pane = app.screen.query_one("#help-bindings")
                pane.scroll_to(y=pane.max_scroll_y // 2, animate=False)
                await pilot.pause()
                g0 = (pane.max_scroll_y, tuple(pane.virtual_size), tuple(pane.size), tuple(app.size), app.screen.has_class("-docked"))
                b = (pane.scroll_offset, len(app.screen_stack), app.screen, app.focused)
                await pilot.press(key); await pilot.pause(); await pilot.pause()
                pane2 = app.screen.query_one("#help-bindings") if isinstance(app.screen, HelpScreen) else pane
                g1 = (pane2.max_scroll_y, tuple(pane2.virtual_size), tuple(pane2.size), tuple(app.size), app.screen.has_class("-docked")) if isinstance(app.screen, HelpScreen) else None
                a = (pane2.scroll_offset, len(app.screen_stack), app.screen, app.focused)
                if a != b and key not in declared:
                    hits += 1
                    with capsys.disabled():
                        print(f"\nSPURIOUS iter={i} key={key}\n before={b}\n after ={a}\n geom0={g0}\n geom1={g1}", flush=True)
    with capsys.disabled():
        print(f"\nTRACE iterations={N} spurious={hits}", flush=True)
