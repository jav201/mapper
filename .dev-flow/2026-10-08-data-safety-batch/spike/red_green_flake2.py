"""Scratch: deterministic RED/GREEN for FLAKE-2.
`delay_deferred_scroll` emulates a loaded machine: Textual's `Widget.scroll_to` (immediate=False,
the default) queues `_scroll_to` with `call_after_refresh`; here that queued call lands 150 ms late.
RED  = the test's current step  pane.scroll_to(y=mid, animate=False)
GREEN= the proposed step        pane.scroll_to(y=mid, animate=False, immediate=True)  (+ settle assert)"""
import os, sys
sys.path.insert(0, os.getcwd())
import pytest
from textual.app import App
from textual.widget import Widget
from mapper.app import MapperApp
from mapper.keymap import SCOPE_HELP, bindings_for
from mapper.screens.help import HelpScreen
from tests.test_help_scope import _legend_from_map, LAYOUT_SIZES, _painted_help_keys, _rows_in

_LATE = {'on': False}

@pytest.fixture
def delay_deferred_scroll(monkeypatch):
    orig = Widget.call_after_refresh
    def slow(self, callback, *a, **kw):
        # only the TEST's own positioning call is made late (flag set around it); the product's key actions are untouched
        if _LATE["on"] and getattr(callback, "__name__", "") == "_scroll_to":
            return self.set_timer(0.15, lambda: callback(*a, **kw))
        return orig(self, callback, *a, **kw)
    monkeypatch.setattr(Widget, "call_after_refresh", slow)

async def effective_keys(tmp_path, immediate):
    app = MapperApp(tmp_path)
    async with app.run_test(size=LAYOUT_SIZES[0]) as pilot:
        screen = await _legend_from_map(app, pilot)
        framework = set(App._merged_bindings.key_to_bindings)
        universe = {k for _n, b in screen._modal_binding_chain for k in b.key_to_bindings}
        universe |= {k for _n, b in screen._binding_chain for k, bs in b.key_to_bindings.items() if any(x.priority for x in bs)}
        universe -= framework
        eff = set()
        for key in sorted(universe):
            if not isinstance(app.screen, HelpScreen):
                await pilot.press("question_mark"); await pilot.pause(); await pilot.pause()
            pane = app.screen.query_one("#help-bindings")
            _LATE["on"] = True
            pane.scroll_to(y=pane.max_scroll_y // 2, animate=False, immediate=immediate)
            _LATE["on"] = False
            await pilot.pause()
            if immediate:
                assert pane.scroll_offset.y == pane.max_scroll_y // 2   # proposed settle guard
            before = (pane.scroll_offset, len(app.screen_stack), app.screen, app.focused)
            await pilot.press(key); await pilot.pause(); await pilot.pause()
            pane = app.screen.query_one("#help-bindings") if isinstance(app.screen, HelpScreen) else pane
            after = (pane.scroll_offset, len(app.screen_stack), app.screen, app.focused)
            if after != before: eff.add(key)
        return eff

async def test_red_current_step_fails_when_scroll_lands_late(tmp_path, delay_deferred_scroll):
    eff = await effective_keys(tmp_path, immediate=False)
    declared = {b.key for b in bindings_for(SCOPE_HELP)}
    assert eff == declared, f"work but not painted: {sorted(eff - declared)}; painted but inert: {sorted(declared - eff)}"

async def test_green_immediate_step_passes_under_same_delay(tmp_path, delay_deferred_scroll):
    eff = await effective_keys(tmp_path, immediate=True)
    declared = {b.key for b in bindings_for(SCOPE_HELP)}
    assert eff == declared, f"work but not painted: {sorted(eff - declared)}; painted but inert: {sorted(declared - eff)}"
