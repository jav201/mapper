"""DDR D1 / PDR C14 (LLR-003.3 boundary): `esc` with a LIVE SEARCH and a
pending draft clears the search and opens NO guard.

`MapScreen.action_back_or_home` branches (`mapper/app.py`): a live search is
cleared and the map screen stays (`#D38`); only with no search live does the
pop route through `_guard_draft`.  Clearing a search leaves nothing -- the
screen stays, nothing is written or dropped -- so with a draft pending the
search-clearing branch must NOT ask `save · discard · stay`.  The decision
point itself (`_guard_draft`) is not re-implemented here; the oracle is that
no `DraftGuardScreen` appears on the stack.
"""
from __future__ import annotations

from mapper.app import MapperApp, MapScreen
from tests.test_draft_save import (
    _guards,
    _hashes,
    _header,
    _inspector,
    _open,
    _press,
    _seed_map,
    _type_into,
)

SIZE = (140, 40)


async def test_llr_003_3_esc_with_a_live_search_clears_it_and_opens_no_guard(tmp_path):
    """Draft pending + search live: one `esc` clears the search, asks nothing,
    keeps the map screen on top, writes nothing and keeps the draft pending."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        await _type_into(pilot, screen, "insp-title", "x")
        await _press(pilot, "escape")
        assert _inspector(screen).draft_values() == {"title": "alfax"}
        start = _hashes(tmp_path, map_id)

        await _press(pilot, "slash")
        await _press(pilot, "b", "e", "t", "a")
        await _press(pilot, "enter")
        assert screen._search_is_live()

        await _press(pilot, "escape")

        assert _guards(app) == 0
        assert not screen._search_is_live()
        assert screen.query_text == ""
        assert isinstance(app.screen, MapScreen)
        assert app.screen is screen
        assert _hashes(tmp_path, map_id) == start
        assert _inspector(screen).draft_values() == {"title": "alfax"}
        assert "●" in _header(screen)
