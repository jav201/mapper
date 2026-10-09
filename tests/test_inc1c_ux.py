"""Inc-1c / UX-1 M1: the hidden-inspector draft prefix must appear immediately.

At 87 columns the inspector auto-hides.  `M` reveals a field for the operator to
fill, but leaving that field hides the card again while the draft is still
pending.  The hint line must lead with `● unsaved (N) · ctrl+s save` the moment
the card hides — not on some later repaint — because that is the only surface a
pending draft has while the card is gone (PDR C6 / R8).
"""
from __future__ import annotations

from rich.style import Style
from textual.widgets import Input

from mapper import darkside
from mapper.app import MapperApp
from mapper.widgets.chrome import HintLine
from tests.test_draft_save import (
    _hint_text_and_prefix_style,
    _inspector,
    _open,
    _press,
    _seed_map,
    _type_into,
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


def _header_text_and_style(screen) -> tuple[str, Style | None]:
    """The inspector header as COMPOSITED (what the operator sees), and the style
    the `● unsaved (N)` run is painted in."""
    header = _inspector(screen).query_one("#insp-header")
    region = header.region
    strips = screen._compositor.render_strips()  # noqa: SLF001
    text, mark_style = "", None
    for strip in strips[region.y: region.y + region.height]:
        x = 0
        for seg in strip:
            if region.x <= x < region.x + region.width:
                text += seg.text
                if "● unsaved" in seg.text and mark_style is None:
                    mark_style = seg.style
            x += len(seg.text)
    return text, mark_style


async def test_inc1c_unsaved_header_is_painted_in_alert(tmp_path):
    """R8: the inspector header's `● unsaved (N)` marker is painted ALERT (red),
    not WARN (amber) -- the unsaved content is a thing the operator must resolve,
    not merely something pending."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 36)) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        await _type_into(pilot, screen, "insp-title", "x")
        text, style = _header_text_and_style(screen)
        assert "● unsaved (1)" in text, text
        assert style is not None
        assert style.color.get_truecolor().hex.lower() == darkside.ALERT.lower()


async def test_inc1c_tab_into_a_field_names_ctrl_s(tmp_path):
    """U2: tabbing into an inspector field swaps the map-navigation hint for the
    draft hint, which names `ctrl+s` and stops promising `↵ open card` while `j`
    types a letter."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 36)) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        for _ in range(12):
            if isinstance(app.focused, Input):
                break
            await pilot.press("tab")
            await pilot.pause()
        focused = app.focused
        assert isinstance(focused, Input), focused
        assert str(getattr(focused, "id", "") or "").startswith("insp-"), focused
        hint = screen.query_one(HintLine).text
        assert "ctrl+s save" in hint, hint
        assert "↵ open card" not in hint, hint
