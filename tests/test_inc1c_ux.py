"""Inc-1c / UX-1 M1: the hidden-inspector draft prefix must appear immediately.

At 87 columns the inspector auto-hides.  `M` reveals a field for the operator to
fill, but leaving that field hides the card again while the draft is still
pending.  The hint line must lead with `● unsaved (N) · ctrl+s save` the moment
the card hides — not on some later repaint — because that is the only surface a
pending draft has while the card is gone (PDR C6 / R8).
"""
from __future__ import annotations

from mapper.app import MapperApp
from tests.test_draft_save import (
    _hint_text_and_prefix_style,
    _open,
    _press,
    _seed_map,
)


async def test_inc1c_c6_prefix_appears_when_the_card_hides_again(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=(87, 34)) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        await _press(pilot, "M")
        await _press(pilot, "z")
        await _press(pilot, "enter")
        text, _ = _hint_text_and_prefix_style(screen)
        assert text.lstrip().startswith("● unsaved (1)"), text
