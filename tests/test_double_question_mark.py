"""Inc-4 — AT-044 (LLR-007.1): a doubled `?` opens exactly one legend.

The help scope is modal — `MODAL_SCOPES` carries `SCOPE_HELP` (`mapper/keymap.py:278`) —
so `bindings_for("help")` returns only the help seat and a second `?` binds to
nothing: no second legend stacks.  This node is the on-disk realisation of the
`AT-044` acceptance id (`HLR-N16.3`'s "a doubled `?` does not stack a second
legend"), which had no node of its own before this batch.
"""
from __future__ import annotations

from mapper.app import MapperApp
from mapper.screens.help import HelpScreen
from tests.test_repair_layout import _open_map, _tree


async def test_at_044_a_doubled_question_mark_opens_one_legend(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 45)) as pilot:
        await _open_map(app, pilot, _tree(app))
        depth = len(app.screen_stack)

        await pilot.press("question_mark")
        await pilot.pause()
        await pilot.pause()
        assert isinstance(app.screen, HelpScreen), "the first ? did not open the legend"
        legend = app.screen
        assert len(app.screen_stack) == depth + 1, "the first ? did not push exactly one legend"

        await pilot.press("question_mark")
        await pilot.pause()
        await pilot.pause()
        assert app.screen is legend, "the second ? closed or replaced the legend"
        assert isinstance(app.screen, HelpScreen), "the second ? left the legend screen"
        assert len(app.screen_stack) == depth + 1, (
            "the second ? grew the screen stack — a second legend stacked"
        )
