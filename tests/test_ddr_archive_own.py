"""DDR D1 / PDR C14 (LLR-003.6 boundary): archiving the draft's OWN node.

`x` is a structural write, so over a pending draft it must pass the single
decision point (`MapScreen._guard_draft`) before anything is touched.  The
boundary this file pins is archiving the very node the draft belongs to: the
guard's `save` arm writes a title whose node is about to be archived, and the
`discard` arm drops that same title.  Either way the operation ends as ONE
archive: no second guard opens, the node is gone from the graph, the cursor
lands on an existing node, the draft is no longer pending, and the files on
disk are exactly the archive's result -- loadable by the store.  The drafted
title is not required to survive: it belonged to the archived node.
"""
from __future__ import annotations

import pytest

from mapper.app import MapperApp, _ConfirmScreen
from tests.test_draft_save import (
    _answer,
    _disk,
    _guards,
    _hashes,
    _inspector,
    _open,
    _press,
    _seed_map,
    _type_into,
)

SIZE = (140, 40)


@pytest.mark.parametrize("key", ["s", "d"], ids=["save", "discard"])
async def test_llr_003_6_archiving_the_drafts_own_node(tmp_path, key):
    """`x` over a draft on the cursor's own node asks once and writes nothing
    until answered.  `save`/`discard` both resolve into the archive arm (its
    own confirmation, not a second draft guard); confirming archives the node
    and leaves the map as one archive -- no pending draft, cursor on a node
    that exists, disk loadable by the store."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        await _type_into(pilot, screen, "insp-title", "x")
        await _press(pilot, "escape")
        before = _hashes(tmp_path, map_id)

        await _press(pilot, "x")
        assert _guards(app) == 1
        assert _hashes(tmp_path, map_id) == before

        await _answer(app, pilot, key)
        await pilot.pause()
        assert _guards(app) == 0
        # Answering the guard resolved into the archive arm's own confirmation
        # -- a different modal, not a second draft guard.
        assert isinstance(app.screen, _ConfirmScreen)
        await _press(pilot, "y")

        assert "a" not in screen.graph.nodes
        assert screen.nav.cursor in screen.graph.nodes
        assert not _inspector(screen).has_draft()
        assert _hashes(tmp_path, map_id) != before
        disk = _disk(tmp_path, map_id)
        assert set(disk.nodes) == {"root", "b"}
