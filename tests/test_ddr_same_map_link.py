"""DDR D1 / PDR C14, LLR-003.4 boundary: a link to the SAME map is still guarded.

`AT-011` guards a link to another map.  The boundary arm is a node whose link
target is the map it lives in: `↵` must still ask `save · discard · stay` before
any push, through the same single decision point (`MapScreen._guard_draft`).
`save`/`discard` push a second `MapScreen` for the same map (stack depth + 1);
`stay` holds the screen and keeps the draft pending.
"""
from __future__ import annotations

import pytest

from mapper.app import MapperApp, MapScreen
from tests.test_draft_save import (
    _answer,
    _guards,
    _inspector,
    _open,
    _press,
    _seed_map,
    _type_into,
)

SIZE = (140, 40)


def _seed_self_linked(app, map_id="ds"):
    """Seed `map_id` (via `_seed_map`) with node `a` linking back to `map_id`."""
    _seed_map(app, map_id)
    g = app.store.load(map_id)
    g.nodes["a"].ficha.fields["map"] = map_id
    app.store.save(map_id, g)
    return map_id


@pytest.mark.parametrize("answer", ["s", "d", "escape"])
async def test_llr_003_4_a_link_to_the_same_map_is_guarded(tmp_path, answer):
    """LLR-003.4 boundary: `↵` over a node linking to its own map with a draft
    asks once BEFORE any push.  `save`/`discard` push a second map screen for the
    same map (depth + 1); `stay` holds the current screen and keeps the draft."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        map_id = _seed_self_linked(app)
        screen = await _open(app, pilot, map_id, cursor="a")
        await _type_into(pilot, screen, "insp-title", "x")
        await _press(pilot, "escape")
        depth = len(app.screen_stack)

        await _press(pilot, "enter")
        assert _guards(app) == 1
        assert len(app.screen_stack) == depth + 1  # only the guard is up, no push yet
        await _answer(app, pilot, answer)

        if answer == "escape":
            assert len(app.screen_stack) == depth
            assert _inspector(screen).draft_values() == {"title": "alfax"}
        else:
            assert len(app.screen_stack) == depth + 1
            assert isinstance(app.screen, MapScreen)
            assert app.screen.map_id == map_id
