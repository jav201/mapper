"""Inc-8 -- US-N16 «leyenda»: the legend panel, read through the painted frame.

Every arm opens the legend with the real `question_mark` chord and declares its
Pilot size, read from `tests/test_repair_layout.py` rather than re-typed
(`HLR-N16.1`'s oracle block).  The frame is clipped to `#help-dialog` with that
module's `_rows_in`, so the map's keybar showing through the modal backdrop is
never read as legend content.
"""
from __future__ import annotations

import pytest
from rich.style import Style
from textual.app import App

from mapper import darkside, keymap
from mapper.app import MapperApp
from mapper.keymap import SCOPE_HELP, SCOPE_MAP, bindings_for, duplicate_chords
from mapper.screens.help import (
    LEGEND_ROW_CELLS,
    SECTION_COLOURS,
    SECTION_VOCABULARY,
    HelpScreen,
    vocabulary_for,
)
from tests.test_overflow import _contrast
from tests.test_repair_layout import NARROW_SIZE, WIDE_SIZES, _open_map, _rows_in, _tree

SIZE = WIDE_SIZES[0]


async def _legend_from_map(app, pilot, *view_keys: str):
    await _open_map(app, pilot, _tree(app))
    for key in view_keys:
        await pilot.press(key)
        await pilot.pause()
    await pilot.press("question_mark")
    await pilot.pause()
    await pilot.pause()
    assert isinstance(app.screen, HelpScreen)
    return app.screen


async def _legend_from_home(app, pilot):
    _tree(app)
    await pilot.pause()
    await pilot.press("question_mark")
    await pilot.pause()
    await pilot.pause()
    assert isinstance(app.screen, HelpScreen)
    return app.screen


async def _harvest(app, pilot, reader):
    """`reader(screen, dialog_region)` at EVERY scroll position of the pane.

    `scroll_to` is legitimate here: it harvests content.  Whether an operator
    can scroll is `HLR-N16.4`'s arm, which presses real keys (`QA3-C-04`).
    """
    screen = app.screen
    dialog = screen.query_one("#help-dialog")
    pane = screen.query_one("#help-bindings")
    out = []
    for _ in range(60):
        out.extend(reader(screen, dialog.region))
        if pane.scroll_offset.y >= pane.max_scroll_y:
            return out
        pane.scroll_to(y=pane.scroll_offset.y + max(1, pane.region.height - 1), animate=False)
        await pilot.pause()
        await pilot.pause()
    pytest.fail("the legend pane never reached the bottom of its scroll range")


def _painted_segments(screen, region) -> list[tuple[str, Style]]:
    """(text, style) runs of the composited frame that lie inside `region`."""
    out = []
    strips = screen._compositor.render_strips()  # noqa: SLF001
    for strip in strips[region.y:region.y + region.height]:
        x = 0
        for seg in strip:
            width = len(seg.text)
            if x >= region.x and x + width <= region.x + region.width and seg.text.strip():
                out.append((seg.text, seg.style))
            x += width
    return out


def _hex(color) -> str | None:
    return None if color is None else color.get_truecolor().hex


def _paints_as(style: Style, declared: str) -> bool:
    want = Style.parse(darkside.resolve_style(declared))
    if _hex(style.color) != _hex(want.color) or bool(style.bold) != bool(want.bold):
        return False
    return want.bgcolor is None or _hex(style.bgcolor) == _hex(want.bgcolor)


# ---------------------------------------------------------------------------
# HLR-N16.2 -- the title names the view (TC-066)

@pytest.mark.parametrize("view_keys,view", [((), "atlas"), (("o",), "outline"), (("r",), "radial")])
async def test_hlr_n16_2_legend_names_the_map_view(tmp_path, view_keys, view):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        screen = await _legend_from_map(app, pilot, *view_keys)
        title = _rows_in(screen, screen.query_one("#help-title").region)
        assert any(f"leyenda · {view}" in row for row in title), title


async def test_hlr_n16_2_legend_names_the_sala(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        screen = await _legend_from_home(app, pilot)
        title = _rows_in(screen, screen.query_one("#help-title").region)
        assert any("leyenda · sala" in row for row in title), title


# ---------------------------------------------------------------------------
# LLR-N16.2.1 -- one declaration, painted in its own styles (TC-067)

@pytest.mark.parametrize("view", sorted(darkside.LEGEND_VIEWS))
async def test_llr_n16_2_1_every_member_is_painted_in_its_declared_style(tmp_path, view):
    """Every member of `view`'s vocabulary that HAS a sample is found in the
    painted frame, as that sample, in that member's resolved style.

    The members come from the declaration (`vocabulary_for`), never from a list
    here, and the arm asserts it checked all of them -- a vocabulary that
    shrank to one member would otherwise pass over one member.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        if view == "sala":
            await _legend_from_home(app, pilot)
        else:
            await _legend_from_map(app, pilot)
        assert app.screen.view == view
        painted = await _harvest(app, pilot, _painted_segments)

    members = [m for m in vocabulary_for(view) if m[1]]
    assert len(members) == len([m for m in darkside.DECLARED_VOCABULARY
                                if m[0] in darkside.LEGEND_VIEWS[view] and m[1]])
    unpainted = [
        (vid, glyph, style) for vid, glyph, _label, style in members
        if not any(glyph.strip() in text and _paints_as(st, style) for text, st in painted)
    ]
    assert not unpainted, f"members not painted in their declared style: {unpainted}"


# ---------------------------------------------------------------------------
# LLR-N16.2.2 -- an empty vocabulary omits the section (TC-068)

@pytest.mark.parametrize("view_keys,view", [((), "atlas"), (("o",), "outline")])
async def test_llr_n16_2_2_empty_vocabulary_omits_the_section(tmp_path, view_keys, view):
    """`outline` declares no vocabulary; `atlas` does and is the positive control."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await _legend_from_map(app, pilot, *view_keys)
        assert app.screen.view == view
        rows = "\n".join(await _harvest(app, pilot, _rows_in))

    empty = not vocabulary_for(view)
    assert empty == (view == "outline"), "the fixture views changed their vocabularies"
    for header in (SECTION_VOCABULARY, SECTION_COLOURS):
        assert (header in rows) is not empty, f"{header!r} painted={header in rows} for {view}"
    missing = [b.label for b in bindings_for(SCOPE_MAP) if b.label not in rows]
    assert not missing, f"key rows lost with the section: {missing}"


# ---------------------------------------------------------------------------
# LLR-N16.2.3 -- everything reaching the legend is coerced and bounded (TC-069)

HOSTILE = "[bold red]x[/] \x07 ‮ " + "漢" * 60
BANNED = {cp for lo, hi in darkside.COERCION_RANGES for cp in range(lo, hi + 1)}


async def test_llr_n16_2_3_legend_coerces_and_bounds_every_string(tmp_path, monkeypatch):
    """A seat label, a vocabulary caption, a sample and the view name, each
    carrying Rich markup, a C0 byte, U+202E and a wide-character run that
    splits at the width.  Painted: no banned code point, the markup literal,
    and no row wider than `LEGEND_ROW_CELLS` (the row-length clause)."""
    monkeypatch.setattr(keymap, "KEYMAP", [
        *keymap.KEYMAP, keymap.KeyBinding("F9", "F9", "home", HOSTILE, "salir")])
    monkeypatch.setattr(darkside, "DECLARED_VOCABULARY", (
        *darkside.DECLARED_VOCABULARY, ("V1", HOSTILE, HOSTILE, "INK on PANEL")))
    view = "atlas" + HOSTILE
    monkeypatch.setitem(darkside.LEGEND_VIEWS, view, darkside.LEGEND_VIEWS["atlas"])
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await _open_map(app, pilot, _tree(app))
        app.push_screen(HelpScreen(SCOPE_MAP, view=view))
        await pilot.pause()
        await pilot.pause()
        screen = app.screen
        texts = [screen._render_title(), screen._render_keymap(),  # noqa: SLF001
                 screen._render_vocabulary(vocabulary_for(view))]  # noqa: SLF001
        rows = await _harvest(app, pilot, _rows_in)

    painted = "\n".join(rows)
    assert painted.count("[bold red]x[/]") >= 3, "a hostile string never reached the frame"
    assert not {ord(c) for c in painted} & BANNED
    for text in texts:
        for line in text.split("\n"):
            assert line.cell_len <= LEGEND_ROW_CELLS, (line.cell_len, line.plain[:40])


# ---------------------------------------------------------------------------
# HLR-N16.4 -- the legend declares every key that works inside it (TC-086)

@pytest.mark.parametrize("size", [SIZE, NARROW_SIZE])
async def test_hlr_n16_4_legend_declares_its_own_keys(tmp_path, size):
    """Keys with a MEASURED effect == keys the seat declares for the legend.

    The universe is DERIVED from the legend's live binding chain -- the chain
    Textual dispatches non-priority keys through, plus every priority binding --
    less the keys Textual's own `App` base binds on every screen of every app
    (`ctrl+q`, `ctrl+c`), which no scope of this seat declares (`INC8-F3`).
    Each key is pressed for real from the MIDDLE of the scroll range, and its
    effect is read from the pane, the screen stack and the focus.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        screen = await _legend_from_map(app, pilot)
        framework = set(App._merged_bindings.key_to_bindings)  # noqa: SLF001
        universe = {key for _node, bmap in screen._modal_binding_chain  # noqa: SLF001
                    for key in bmap.key_to_bindings}
        universe |= {key for _node, bmap in screen._binding_chain  # noqa: SLF001
                     for key, bs in bmap.key_to_bindings.items() if any(b.priority for b in bs)}
        universe -= framework
        declared = {b.key for b in bindings_for(SCOPE_HELP)}
        assert declared <= universe, "a declared key is not even bound"

        effective = set()
        for key in sorted(universe):
            if not isinstance(app.screen, HelpScreen):
                await pilot.press("question_mark")
                await pilot.pause()
                await pilot.pause()
            pane = app.screen.query_one("#help-bindings")
            assert pane.max_scroll_y > 2, "the legend fits; nothing here could scroll"
            pane.scroll_to(y=pane.max_scroll_y // 2, animate=False)
            await pilot.pause()
            before = (pane.scroll_offset, len(app.screen_stack), app.screen, app.focused)
            await pilot.press(key)
            await pilot.pause()
            await pilot.pause()
            after = (pane.scroll_offset, len(app.screen_stack), app.screen, app.focused)
            if after != before:
                effective.add(key)

    assert effective == declared, (
        f"work but undeclared: {sorted(effective - declared)}; "
        f"declared but inert: {sorted(declared - effective)}"
    )


# ---------------------------------------------------------------------------
# C-D25a / C-D25b -- Inc-8's own seat diff, and the collision set re-run

ENTRY_HELP_SEAT = frozenset({("escape", "dismiss_none"), ("q", "dismiss_none")})
DECLARED_ADDED = frozenset({
    ("up", "legend_up"), ("down", "legend_down"),
    ("pageup", "legend_page_up"), ("pagedown", "legend_page_down"),
    ("home", "legend_home"), ("end", "legend_end"),
})


def test_cd25a_the_seat_diff_is_exactly_the_six_rows_inc8_declares():
    exit_seat = frozenset((b.key, b.action) for b in bindings_for(SCOPE_HELP))
    assert exit_seat - ENTRY_HELP_SEAT == DECLARED_ADDED
    assert ENTRY_HELP_SEAT - exit_seat == frozenset()
    touched = {b.scope for b in keymap.KEYMAP if (b.key, b.action) in DECLARED_ADDED}
    assert touched == {SCOPE_HELP}, touched


def test_cd25b_no_chord_collides_on_entry_or_on_exit():
    assert duplicate_chords() == []
    entry = [b for b in keymap.KEYMAP
             if not (b.scope == SCOPE_HELP and (b.key, b.action) in DECLARED_ADDED)]
    assert len(entry) == len(keymap.KEYMAP) - len(DECLARED_ADDED)
    seen, clashes = set(), []
    for b in entry:
        if (b.scope, b.key) in seen:
            clashes.append((b.scope, b.key))
        seen.add((b.scope, b.key))
    assert clashes == []


# ---------------------------------------------------------------------------
# #D28 -- the legend's own readable text clears 4.5:1 on its surface

def test_d28_the_legend_chrome_clears_the_contrast_floor():
    """Title, headers, keys and captions are readable, load-bearing text.

    Exempt, by `#D28`'s own clause and by `LLR-N16.2.1`: the vocabulary samples
    and colour swatches, which must paint the VIEW's style, not the legend's.
    """
    assert f"background: {darkside.PANEL};" in HelpScreen.CSS
    exempt = {darkside.resolve_style(m[3]) for m in darkside.DECLARED_VOCABULARY}
    exempt |= {darkside.resolve_style(c[2]) for c in darkside.DECLARED_COLOURS}
    screen = HelpScreen(SCOPE_MAP, view="atlas")
    texts = [screen._render_title(), screen._render_keymap(),  # noqa: SLF001
             screen._render_vocabulary(vocabulary_for("atlas")),  # noqa: SLF001
             screen._render_colours(), screen._render_footer()]  # noqa: SLF001
    styles = {str(span.style) for text in texts for span in text.spans
              if text.plain[span.start:span.end].strip()} - exempt
    assert len(styles) >= 3, styles
    for style in styles:
        fg = Style.parse(style).color
        ratio = _contrast(_hex(fg), darkside.PANEL)
        assert ratio >= 4.5, f"{style} paints legend text at {ratio:.2f}:1 on PANEL"
