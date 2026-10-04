"""Inc-EN-6 -- the palette footer advertises the arrows (`N2`, `INC9F-UX-F4`).

Authority: `VERDICT-inc9-2026-09-30.md` Round 4 N2 and `VERDICT-inc-en-2026-10-02.md` (EN-6).  The footer reads
`↑↓ move · ↵ run · esc close` (E3 of Round 3 gave the pairs a middle dot); every word and glyph is the seat's own, so a relabelled seat must reach the footer.
"""
from __future__ import annotations

import dataclasses

import pytest

from mapper import keymap
from mapper.app import MapperApp
from mapper.screens.palette import CommandPalette
from textual.widgets import Input, ListView

SIZES = [(118, 34), (87, 34)]


async def _open(app, pilot):
    await pilot.press("ctrl+p")
    await pilot.pause()
    await pilot.pause()
    pal = app.screen
    assert isinstance(pal, CommandPalette), pal
    return pal


def _footer(pal) -> str:
    return pal.query_one("#palette-count").content.plain


def _seat_pairs():
    up = keymap.hint_pair(keymap.SCOPE_PALETTE, "move_up")
    down = keymap.hint_pair(keymap.SCOPE_PALETTE, "move_down")
    return up, down, keymap.hint_pair(keymap.SCOPE_PALETTE, "run_selected"), keymap.hint_pair(keymap.SCOPE_PALETTE, "dismiss_none")


@pytest.mark.parametrize("size", SIZES)
@pytest.mark.asyncio
async def test_the_footer_reads_move_run_close_in_that_order_and_fits(tmp_path, size):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        pal = await _open(app, pilot)
        footer = _footer(pal)
        dialog_w = pal.query_one("#palette-dialog").region.width
    up, down, run, close = _seat_pairs()
    move = up.split(" ", 1)[0] + down.split(" ", 1)[0] + " " + up.split(" ", 1)[1]
    assert (move, run, close) == ("↑↓ move", "↵ run", "esc close"), (move, run, close)
    at = [footer.index(p) for p in (move, run, close)]
    assert at == sorted(at) and len(set(at)) == 3, (footer, at)
    assert len(footer) <= dialog_w, (len(footer), dialog_w, footer)


@pytest.mark.asyncio
async def test_a_relabelled_seat_reaches_the_footer(tmp_path, monkeypatch):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZES[0]) as pilot:
        await pilot.pause()
        glyphs = {"move_up": "UU", "move_down": "DD"}
        seat = [
            dataclasses.replace(b, label=f"zz-{b.action}", glyph=glyphs.get(b.action, b.glyph))
            for b in keymap.KEYMAP
        ]
        monkeypatch.setattr(keymap, "KEYMAP", seat)
        pal = await _open(app, pilot)
        footer = _footer(pal)
    assert "UUDD zz-move_up" in footer, footer
    assert "zz-run_selected" in footer and "zz-dismiss_none" in footer, footer
    assert "move" not in footer.replace("zz-move_up", ""), footer


def test_the_two_arrow_rows_share_one_word_and_are_each_bound_once():
    rows = [b for b in keymap.KEYMAP if b.scope == keymap.SCOPE_PALETTE and b.action in ("move_up", "move_down")]
    assert sorted((b.key, b.glyph) for b in rows) == [("down", "↓"), ("up", "↑")]
    assert {b.label for b in rows} == {"move"}
    keys = [b.key for b in CommandPalette.BINDINGS]
    assert keys.count("up") == 1 and keys.count("down") == 1, keys


@pytest.mark.asyncio
async def test_the_arrows_move_the_lit_row_and_enter_runs_it(tmp_path, monkeypatch):
    """`EN6-REV-F2`: the arrows must reach the SEAT BINDINGS.  The index moving is not enough: an `on_key` that forwards
    `up`/`down` itself (and stops the event) moves the row too, and leaves the seat rows as decoration.  So the two
    actions are recorded."""
    fired: list[str] = []
    for name in ("action_move_up", "action_move_down"):
        original = getattr(CommandPalette, name)

        def spy(self, _original=original, _name=name):
            fired.append(_name)
            return _original(self)

        monkeypatch.setattr(CommandPalette, name, spy)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZES[0]) as pilot:
        await pilot.pause()
        pal = await _open(app, pilot)
        lv = pal.query_one("#palette-list", ListView)
        assert lv.index == 0
        await pilot.press("down", "down")
        await pilot.pause()
        assert lv.index == 2
        assert fired == ["action_move_down", "action_move_down"], fired
        await pilot.press("up")
        await pilot.pause()
        assert lv.index == 1
        assert fired[-1] == "action_move_up" and len(fired) == 3, fired
        await pilot.press("up", "up", "up")
        await pilot.pause()
        assert lv.index == 0, "the lit row stops at the first"
        await pilot.press("pagedown")
        await pilot.pause()
        assert lv.index > 1, "page keys still forward"
        assert app.screen is pal, "an arrow never closes the palette"
        assert pal.query_one("#palette-input", Input).has_focus
        lit = pal._items[lv.index]  # noqa: SLF001
        dismissed: list[object] = []
        monkeypatch.setattr(pal, "dismiss", lambda value=None: dismissed.append(value))
        await pilot.press("enter")
        await pilot.pause()
        # `EN6-REV-F3`: what `enter` hands back is the LIT action, not merely "something closed the palette".
        assert dismissed == [lit.action], (dismissed, lit.action)


@pytest.mark.asyncio
async def test_the_arrows_do_not_break_typing_or_the_cursor_in_the_box(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZES[0]) as pilot:
        await pilot.pause()
        pal = await _open(app, pilot)
        box = pal.query_one("#palette-input", Input)
        await pilot.press("m", "a", "left", "x", "down", "up", "end", "p")
        await pilot.pause()
        assert box.value == "mxap", box.value
        assert app.screen is pal and box.has_focus
