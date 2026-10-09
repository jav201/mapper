"""Inc-2 (LLR-003.3, AT-005a/AT-005b): leaving the map screen is guarded.

`q` (`home`) and `escape` (`back_or_home`, with no live search) both pop the map
screen.  With a pending draft neither may pop it silently: the pop is wrapped in
`_guard_draft`, the single decision point, so it asks `save · discard · stay`
first.  `save`/`discard` leave; `stay` holds the screen and the draft.

`escape` with a live search clears the search and is NOT guarded -- a separate
branch of `action_back_or_home`, not exercised here.
"""
from __future__ import annotations

import pytest

from mapper.app import MapperApp
from mapper.model import Edge, Ficha, Graph, Node, SchemaField
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

_SCHEMA = [SchemaField(key="D", label="documento", required=True)]


def _seed_linked(app, first="ds", second="ds2"):
    """Seed `first` whose node `a` links to `second`, and seed `second` too."""
    g = Graph()
    g.schema = list(_SCHEMA)
    g.add_node(Node(id="root", ficha=Ficha(title="raiz", fields={"D": "r"})))
    g.add_node(Node(id="a", ficha=Ficha(title="alfa", state="ok", notes="n", fields={"D": "acta", "map": second})))
    g.add_node(Node(id="b", ficha=Ficha(title="beta")))
    g.add_edge(Edge("root", "a"))
    g.add_edge(Edge("root", "b"))
    app.store.save(first, g)
    _seed_map(app, second)
    return first


@pytest.mark.parametrize("answer", ["s", "d", "escape"])
async def test_at_005a_leave_with_q_is_guarded(tmp_path, answer):
    """AT-005a: `q` over a draft asks once.  `save`/`discard` pop the map screen;
    `stay` holds it and keeps the draft pending."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        await _type_into(pilot, screen, "insp-title", "x")
        await _press(pilot, "escape")
        depth = len(app.screen_stack)

        await _press(pilot, "q")
        assert _guards(app) == 1
        await _answer(app, pilot, answer)

        if answer == "escape":
            assert len(app.screen_stack) == depth
            assert _inspector(screen).draft_values() == {"title": "alfax"}
        else:
            assert len(app.screen_stack) == depth - 1


@pytest.mark.parametrize("answer", ["s", "d", "escape"])
async def test_at_005b_leave_with_esc_is_guarded(tmp_path, answer):
    """AT-005b: `escape` with no live search over a draft asks once and resolves
    through the same three answers as `q`."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        await _type_into(pilot, screen, "insp-title", "x")
        await _press(pilot, "escape")
        depth = len(app.screen_stack)

        await _press(pilot, "escape")
        assert _guards(app) == 1
        await _answer(app, pilot, answer)

        if answer == "escape":
            assert len(app.screen_stack) == depth
            assert _inspector(screen).draft_values() == {"title": "alfax"}
        else:
            assert len(app.screen_stack) == depth - 1


@pytest.mark.parametrize("answer", ["s", "d", "escape"])
async def test_at_011_following_a_link_is_guarded(tmp_path, answer):
    """AT-011 (LLR-003.4): `↵` over a linking node with a draft asks once before
    pushing the target map.  `save`/`discard` push it (depth + 1); `stay` holds
    the current screen and keeps the draft pending."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        first = _seed_linked(app)
        screen = await _open(app, pilot, first, cursor="a")
        await _type_into(pilot, screen, "insp-title", "x")
        await _press(pilot, "escape")
        depth = len(app.screen_stack)

        await _press(pilot, "enter")
        assert _guards(app) == 1
        await _answer(app, pilot, answer)

        if answer == "escape":
            assert len(app.screen_stack) == depth
            assert _inspector(screen).draft_values() == {"title": "alfax"}
        else:
            assert len(app.screen_stack) == depth + 1
