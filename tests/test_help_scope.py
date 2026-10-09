"""Inc-8 -- US-N16 «leyenda»: the legend panel, read through the painted frame.

Every arm opens the legend with the real `question_mark` chord and declares its
Pilot size, read from `tests/test_repair_layout.py` rather than re-typed
(`HLR-N16.1`'s oracle block).  The frame is clipped to `#help-dialog` with that
module's `_rows_in`, so the map's keybar showing through the modal backdrop is
never read as legend content.
"""
from __future__ import annotations

import contextlib

import pytest
from rich.cells import cell_len
from rich.style import Style
from rich.text import Text
from textual.app import App
from textual.widget import Widget

from mapper import darkside, keymap
from mapper.app import MapperApp
from mapper.screens import help as help_screen
from mapper.keymap import SCOPE_HELP, SCOPE_MAP, bindings_for, duplicate_chords
from mapper.screens.help import (
    LEGEND_ROW_CELLS,
    LEGEND_TITLE,
    SECTION_COLOURS,
    SECTION_VOCABULARY,
    HelpScreen,
    vocabulary_for,
)
from tests.test_overflow import _contrast
from tests.test_repair_layout import NARROW_SIZE, WIDE_SIZES, _open_map, _painted_bindings, _rows_in, _tree

SIZE = WIDE_SIZES[0]
#: Verdict `F9` moved the dock threshold, so `NARROW_SIZE` (100 columns, the
#: map's rail auto-hidden) now DOCKS.  The modal is kept in the "both
#: layouts" arms at the widest width it holds for a view starting at column
#: 0 -- derived from the panel and the minimum, not re-typed.
MODAL_SIZE = (help_screen.LEGEND_DOCKED_CELLS + help_screen.LEGEND_DOCK_MIN_VIEW_CELLS - 1,
              NARROW_SIZE[1])
LAYOUT_SIZES = [SIZE, NARROW_SIZE, MODAL_SIZE]


#: `US-004` / `FLAKE-2`.  `Widget.scroll_to` defaults to `immediate=False`, which
#: queues `_scroll_to` with `call_after_refresh`; on a loaded machine that call
#: can land AFTER the next sample.  This flag + fixture emulate the load: while
#: `late_scroll()` is open, ONLY a queued `_scroll_to` is made to land 150 ms late.
_LATE = {"on": False}


@contextlib.contextmanager
def late_scroll():
    """Open the window in which a queued `_scroll_to` lands late (a no-op unless
    the `delay_deferred_scroll` fixture is installed)."""
    _LATE["on"] = True
    try:
        yield
    finally:
        _LATE["on"] = False


@pytest.fixture
def delay_deferred_scroll(monkeypatch):
    """Route a queued `_scroll_to` through `set_timer(0.15, ...)`, but only while
    `late_scroll()` is open, so the product's own key-driven scrolls stay
    untouched.  Adapted from `spike/red_green_flake2.py`."""
    original = Widget.call_after_refresh

    def late(self, callback, *args, **kwargs):
        if _LATE["on"] and getattr(callback, "__name__", "") == "_scroll_to":
            return self.set_timer(0.15, lambda: callback(*args, **kwargs))
        return original(self, callback, *args, **kwargs)

    monkeypatch.setattr(Widget, "call_after_refresh", late)


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


async def _harvest(app, pilot, reader, region_id: str = "#help-dialog"):
    """`reader(screen, region)` at EVERY scroll position of the pane.

    `scroll_to` is legitimate here: it harvests content.  Whether an operator
    can scroll is `HLR-N16.4`'s arm, which presses real keys (`QA3-C-04`).

    `region_id` narrows the read to one child widget (`INC8-CR-F5`): the
    default, `#help-dialog`, also contains `#help-colours`, whose §3.5 swatch
    paints the SAME glyph (`█`) in the SAME style (`SAGE`) as `V19`'s
    coverage-microbar sample -- so a caller checking a vocabulary member's
    style against the WHOLE dialog cannot tell "the vocabulary section painted
    it" from "the colour row painted something that happens to match".
    """
    screen = app.screen
    region_widget = screen.query_one(region_id)
    pane = screen.query_one("#help-bindings")
    out = []
    for _ in range(60):
        region = region_widget.region
        if region_id != "#help-dialog":
            # `INC8-D-F2`: a widget INSIDE the pane has an unclipped region
            # that scrolls off the top -- measured `y=-10` at the docked
            # height -- and a negative `y` makes `strips[y:y+h]` slice from
            # the END of the frame.  What the operator sees of that widget is
            # the part inside the pane.
            region = region.intersection(pane.region)
        out.extend(reader(screen, region))
        if pane.scroll_offset.y >= pane.max_scroll_y:
            return out
        target = pane.scroll_offset.y + max(1, pane.region.height - 1)
        pane.scroll_to(y=target, animate=False, immediate=True)
        await pilot.pause()
        await pilot.pause()
        assert pane.scroll_offset.y == min(target, pane.max_scroll_y), "the harvest scroll did not land"
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
    """The legend paints a sample as the VIEW does: fg and bold as declared,
    and the ground the member declares or, verdict `E2`, the view's own
    `GROUND` -- never the panel's `PANEL` under it."""
    want = Style.parse(darkside.resolve_style(declared))
    if _hex(style.color) != _hex(want.color) or bool(style.bold) != bool(want.bold):
        return False
    return _hex(style.bgcolor) == (_hex(want.bgcolor) or darkside.GROUND)


# ---------------------------------------------------------------------------
# HLR-N16.2 -- the title names the view (TC-066)

#: One name per view, the one the legend title carries (Inc-8 verdict `D5`,
#: English per the 2026-09-29 language ruling), read from `VIEW_NAMES`, and
#: the key that switches a map to it.
HOME_VIEW = darkside.VIEW_NAMES["home"]
MAP_VIEW_KEYS = {darkside.VIEW_NAMES["canvas"]: (), darkside.VIEW_NAMES["outline"]: ("o",),
                 darkside.VIEW_NAMES["radial"]: ("r",)}


@pytest.mark.parametrize("view_keys,view", [(k, v) for v, k in MAP_VIEW_KEYS.items()])
async def test_hlr_n16_2_legend_names_the_map_view(tmp_path, view_keys, view):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        screen = await _legend_from_map(app, pilot, *view_keys)
        title = _rows_in(screen, screen.query_one("#help-title").region)
        assert any(f"{LEGEND_TITLE} · {view}" in row for row in title), title


async def test_hlr_n16_2_legend_names_the_sala(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        screen = await _legend_from_home(app, pilot)
        title = _rows_in(screen, screen.query_one("#help-title").region)
        assert any(f"{LEGEND_TITLE} · {HOME_VIEW}" in row for row in title), title


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
        if view == HOME_VIEW:
            await _legend_from_home(app, pilot)
        else:
            await _legend_from_map(app, pilot, *MAP_VIEW_KEYS[view])
        assert app.screen.view == view
        # `INC8-CR-F5`: scoped to `#help-vocabulary`, not the whole dialog --
        # see `_harvest`'s docstring for why the wider region is blind to a
        # vocabulary section that stopped painting a member the colour rows
        # happen to paint too (`V19`/`SAGE`).
        painted = await _harvest(app, pilot, _painted_segments, region_id="#help-vocabulary")

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

@pytest.mark.parametrize("source", ["atlas", "componentes"])
async def test_llr_n16_2_2_empty_vocabulary_omits_the_section(tmp_path, source):
    """A screen with no canvas has no vocabulary: the components screen, opened
    by its real `?`.  `atlas` declares one and is the positive control.

    Until the Inc-8 design pass the empty case was `outline`; verdict `D3`
    gave `esquema` a vocabulary of its own, so it no longer is one.
    """
    from mapper.screens.settings import SettingsScreen

    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        if source == "atlas":
            await _legend_from_map(app, pilot)
        else:
            app.push_screen(SettingsScreen())
            await pilot.pause()
            await pilot.press("question_mark")
            await pilot.pause()
            await pilot.pause()
            assert isinstance(app.screen, HelpScreen)
        view, scope = app.screen.view, app.screen.scope
        rows = "\n".join(await _harvest(app, pilot, _rows_in))

    empty = not vocabulary_for(view)
    assert empty == (source != "atlas"), f"the fixture views changed their vocabularies: {view}"
    for header in (SECTION_VOCABULARY, SECTION_COLOURS):
        assert (header in rows) is not empty, f"{header!r} painted={header in rows} for {view}"
    missing = [b.label for b in bindings_for(scope) if b.label not in rows]
    assert not missing, f"key rows lost with the section: {missing}"


# ---------------------------------------------------------------------------
# LLR-N16.2.3 -- everything reaching the legend is coerced and bounded (TC-069)

HOSTILE = "[bold red]x[/] \x07 \u202e " + "漢" * 60
BANNED = {cp for lo, hi in darkside.COERCION_RANGES for cp in range(lo, hi + 1)}


async def test_llr_n16_2_3_legend_coerces_and_bounds_every_string(tmp_path, monkeypatch):
    """A seat label, a vocabulary caption, a sample and the view name, each
    carrying Rich markup, a C0 byte, U+202E and a wide-character run that
    splits at the width.  Painted: no banned code point, the markup literal,
    and no row wider than `LEGEND_ROW_CELLS` (the row-length clause)."""
    monkeypatch.setattr(keymap, "KEYMAP", [
        *keymap.KEYMAP, keymap.KeyBinding("F9", "F9", "home", HOSTILE, "leave")])
    monkeypatch.setattr(darkside, "DECLARED_VOCABULARY", (
        *darkside.DECLARED_VOCABULARY, ("V1", HOSTILE, HOSTILE, "INK on PANEL")))
    # `INC8-SEC-F4`: no arm covered `DECLARED_COLOURS` coercion at all -- a
    # hostile colour LABEL (the only file-derived part of a colour row; the
    # token stays a real one so `resolve_style` does not itself object).
    monkeypatch.setattr(darkside, "DECLARED_COLOURS", (
        *darkside.DECLARED_COLOURS, ("CX", "█", HOSTILE, "ACCENT")))
    view = "atlas" + HOSTILE
    monkeypatch.setitem(darkside.LEGEND_VIEWS, view, darkside.LEGEND_VIEWS["atlas"])
    monkeypatch.setitem(darkside.LEGEND_COLOURS, view, (*darkside.LEGEND_COLOURS["atlas"], "CX"))
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await _open_map(app, pilot, _tree(app))
        app.push_screen(HelpScreen(SCOPE_MAP, view=view))
        await pilot.pause()
        await pilot.pause()
        screen = app.screen
        texts = [screen._render_title(), screen._render_keymap(),  # noqa: SLF001
                 screen._render_vocabulary(vocabulary_for(view)),  # noqa: SLF001
                 screen._render_colours()]  # noqa: SLF001
        title = "\n".join(_rows_in(screen, screen.query_one("#help-title").region))
        rows = await _harvest(app, pilot, _rows_in)

        # `INC8-CR-F2`: the row budget was hand-copied from the CSS width.
        # Pinned here against the real widget's own usable-width attribute, so
        # a CSS edit that stops matching reddens instead of silently drifting.
        # `SIZE` is docked (verdict `E1`), so the budget is the docked one.
        pane = screen.query_one("#help-bindings")
        budget = screen.row_cells
        assert screen.docked and pane.scrollable_content_region.width == budget

    painted = "\n".join(rows)
    # Per surface, so one sink parsing markup cannot hide behind the others.
    assert "[bold red]x[/]" in title, f"the title interpreted markup: {title!r}"
    assert painted.count("[bold red]x[/]") >= 4, "a hostile string never reached the frame"
    assert not {ord(c) for c in painted} & BANNED
    for text in texts:
        for line in text.split("\n"):
            assert line.cell_len <= budget, (line.cell_len, line.plain[:40])


# ---------------------------------------------------------------------------
# HLR-N16.4 -- the legend declares every key that works inside it (TC-086)

def _painted_help_keys(rows: list[str]) -> set[str]:
    """Which `SCOPE_HELP` keys the FRAME actually shows an item for.

    `INC8-CR-F1`, re-read for verdict `E3`'s two-line group
    (`esc q close · ↑ ↓ scroll`): a row splits into ` · `-separated items, and
    an item is key glyphs followed by ONE word.  A key is painted when its
    glyph sits in an item whose word is the legend's word for its action
    (`OWN_SCOPE_COPY`) -- glyph alone would also hit `q` and `esc`'s OTHER
    bindings in the map scope's `leave` group (`q -> home`,
    `esc -> back`), which paint the same two glyphs under another word.
    The seat is used only to decode a painted item back into the `key` names
    `effective` is keyed on.

    `INC8-P2-CR-F9` (`A-112` st. 6): an item is matched WHOLE, in the exact
    form the group paints it -- the seat's glyphs for one word, single-spaced,
    then the word.  Pairing any glyph token with the last token of any
    `·`-split piece also matched a key-section row (`esc` padded to the key
    column, then `close`) once the seat's labels became English words.
    """
    forms: dict[str, set[str]] = {}
    for actions, word in help_screen.OWN_SCOPE_COPY:
        seat = [b for b in bindings_for(SCOPE_HELP) if b.action in actions]
        forms[" ".join([*(b.glyph for b in seat), word])] = {b.key for b in seat}
    painted: set[str] = set()
    for row in rows:
        for item in row.split(help_screen._ITEM_SEP.strip()):  # noqa: SLF001
            painted |= forms.get(item.strip(), set())
    return painted


def test_inc8_p2_cr_f9_a_key_row_never_reads_as_an_own_scope_item():
    """`A-112` st. 6.  A key-section row whose label happens to BE an
    own-scope word -- `esc` over `close`, under the key column's padding --
    is not an own-scope item; the item form itself still is.  Both rows are
    built from the painters' own pieces, not typed."""
    key_row = help_screen._INDENT + darkside.fit("esc", help_screen._KEY_CELLS) + "close"  # noqa: SLF001
    assert _painted_help_keys([key_row]) == set(), key_row
    item = help_screen._ITEM_SEP.join(  # noqa: SLF001
        " ".join([*(b.glyph for b in bindings_for(SCOPE_HELP) if b.action in actions), word])
        for actions, word in help_screen.OWN_SCOPE_COPY)
    assert _painted_help_keys([help_screen._INDENT + item]) == {  # noqa: SLF001
        b.key for b in bindings_for(SCOPE_HELP)}


async def _effective_keys(app, pilot, screen) -> set[str]:
    """Press every key of the legend's derived universe from the MIDDLE of the
    scroll range and return those with a MEASURED effect.  The one loop both
    `test_hlr_n16_4_legend_declares_its_own_keys` and its injected-delay arm run,
    so reverting `immediate=True` here reddens the arm (`LLR-009.2`)."""
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
        target = pane.max_scroll_y // 2
        with late_scroll():
            pane.scroll_to(y=target, animate=False, immediate=True)
        await pilot.pause()
        assert pane.scroll_offset.y == target, "the positioning scroll did not land"
        before = (pane.scroll_offset, len(app.screen_stack), app.screen, app.focused)
        await pilot.press(key)
        await pilot.pause()
        await pilot.pause()
        after = (pane.scroll_offset, len(app.screen_stack), app.screen, app.focused)
        if after != before:
            effective.add(key)
    return effective


async def _painted_own_keys(app, pilot) -> set[str]:
    if not isinstance(app.screen, HelpScreen):
        await pilot.press("question_mark")
        await pilot.pause()
        await pilot.pause()
    # `INC8-P2-CR-F9`: read from the own-scope GROUP alone.  Until round
    # 3 the title also painted `esc close`, so `esc` was proved by the
    # title and a group that lost it stayed green.  The group sits
    # outside the scrolling pane, so one read is all of it.
    screen = app.screen
    rows = _rows_in(screen, screen.query_one("#help-own-scope").region)
    return _painted_help_keys(rows)


@pytest.mark.parametrize("size", LAYOUT_SIZES)
async def test_hlr_n16_4_legend_declares_its_own_keys(tmp_path, size):
    """Keys with a MEASURED effect == keys the legend actually PAINTS.

    The universe is DERIVED from the legend's live binding chain -- the chain
    Textual dispatches non-priority keys through, plus every priority binding --
    less the keys Textual's own `App` base binds on every screen of every app
    (`ctrl+q`, `ctrl+c`), which no scope of this seat declares (`INC8-F3`).
    Each key is pressed for real from the MIDDLE of the scroll range, and its
    effect is read from the pane, the screen stack and the focus.

    `INC8-CR-F1`.  The right-hand side used to be `declared` -- keys the SEAT
    lists for `SCOPE_HELP`, regardless of whether the legend ever paints a row
    for them -- which is exactly the gap `HLR-N16.4` names: "the set the legend
    PAINTS for its own scope", not the set it merely declares. A mutant that
    stops PAINTING a key's row while leaving its seat entry untouched left the
    old arm green. `painted`, below, is read from the composited frame.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        screen = await _legend_from_map(app, pilot)
        effective = await _effective_keys(app, pilot, screen)
        painted = await _painted_own_keys(app, pilot)

    assert effective == painted, (
        f"work but not painted: {sorted(effective - painted)}; "
        f"painted but inert: {sorted(painted - effective)}"
    )


@pytest.mark.parametrize("size", LAYOUT_SIZES)
async def test_at_008_the_own_keys_loop_is_deterministic_under_a_late_scroll(
        tmp_path, size, delay_deferred_scroll):
    """AT-008 / LLR-009.2 (`FLAKE-2`).  The same loop as the own-keys node, with
    the positioning scroll's queued call landing 150 ms late.  Revert
    `immediate=True` in `_effective_keys` and an inert key reads as effective
    (`work but not painted`) or the settle assertion fails."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        screen = await _legend_from_map(app, pilot)
        effective = await _effective_keys(app, pilot, screen)
        painted = await _painted_own_keys(app, pilot)
    assert effective == painted, (
        f"work but not painted: {sorted(effective - painted)}; "
        f"painted but inert: {sorted(painted - effective)}"
    )


async def test_the_delay_fixture_delays_a_queued_scroll_only_inside_the_window(
        tmp_path, delay_deferred_scroll):
    """Instrument RED-proof for `delay_deferred_scroll`: a NON-immediate
    `scroll_to` inside `late_scroll()` has not landed after two pauses and does
    land later; outside the window it lands as usual.  Without this the arm
    above could pass because nothing was ever delayed."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await _legend_from_map(app, pilot)
        pane = app.screen.query_one("#help-bindings")
        target = pane.max_scroll_y // 2
        assert target > 0
        with late_scroll():
            pane.scroll_to(y=target, animate=False)
        await pilot.pause()
        assert pane.scroll_offset.y == 0, "the fixture did not delay the queued scroll"
        await pilot.pause(0.4)
        assert pane.scroll_offset.y == target, "the delayed scroll never landed"
        pane.scroll_to(y=0, animate=False)
        await pilot.pause()
        await pilot.pause()
        assert pane.scroll_offset.y == 0, "outside the window the scroll must not be delayed"


async def test_llr_009_1_the_harvest_scroll_lands_before_it_is_read_under_a_late_scroll(
        tmp_path, delay_deferred_scroll):
    """C12 / LLR-009.1 site `_harvest`: revert `immediate=True` there and the
    settle assertion fails while the scroll is delayed."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await _legend_from_map(app, pilot)
        assert app.screen.query_one("#help-bindings").max_scroll_y > 2
        with late_scroll():
            seen = await _harvest(app, pilot, _rows_in)
    assert seen


async def test_llr_009_1_the_bindings_scroll_lands_before_it_is_read_under_a_late_scroll(
        tmp_path, delay_deferred_scroll):
    """C12 / LLR-009.1 site `tests/test_repair_layout.py::_painted_bindings`."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await _legend_from_map(app, pilot)
        assert app.screen.query_one("#help-bindings").max_scroll_y > 2
        with late_scroll():
            painted = await _painted_bindings(app, pilot)
    assert all(b.label in painted for b in bindings_for(SCOPE_MAP))


@pytest.mark.parametrize("size", LAYOUT_SIZES)
async def test_e3_the_own_keys_are_visible_at_rest_and_at_the_end(tmp_path, size):
    """`INC8-F-CR-F1` / verdict `E3`: "visible at rest" is PINNED, not only
    painted somewhere in the scroll range.  The own-scope keys read off the
    dialog with the pane at its top, and again at its end, each equal every
    own key the legend paints anywhere -- so the group cannot move into the
    scrolling pane, at either end of it, without reddening.  The pane must
    really scroll, or "at the end" would be "at rest" again."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        screen = await _legend_from_map(app, pilot)
        dialog = screen.query_one("#help-dialog")
        pane = screen.query_one("#help-bindings")
        assert pane.max_scroll_y > 0, "the pane does not scroll; 'at the end' is 'at rest'"
        pane.scroll_home(animate=False)
        await pilot.pause()
        await pilot.pause()
        at_rest = _painted_help_keys(_rows_in(screen, dialog.region))
        painted = _painted_help_keys(await _harvest(app, pilot, _rows_in))
        pane.scroll_end(animate=False)
        await pilot.pause()
        await pilot.pause()
        assert pane.scroll_offset.y == pane.max_scroll_y
        at_end = _painted_help_keys(_rows_in(screen, dialog.region))
    assert painted == {b.key for b in bindings_for(SCOPE_HELP)}, painted
    assert at_rest == painted, f"not visible at rest: {sorted(painted - at_rest)}"
    assert at_end == painted, f"scrolled away at the end: {sorted(painted - at_end)}"


async def test_f9_the_layout_sizes_drive_both_layouts(tmp_path):
    """The "both layouts" arms are parametrized on `LAYOUT_SIZES`; this is the
    trigger they depend on, asserted: the modal size really is modal, and the
    others dock -- so a threshold that moved again cannot quietly turn every
    case into one layout."""
    layouts = {}
    for size in LAYOUT_SIZES:
        app = MapperApp(tmp_path / f"{size[0]}x{size[1]}")
        async with app.run_test(size=size) as pilot:
            screen = await _legend_from_map(app, pilot)
            layouts[size] = screen.docked
    assert layouts == {SIZE: True, NARROW_SIZE: True, MODAL_SIZE: False}, layouts


@pytest.mark.parametrize("size", LAYOUT_SIZES)
async def test_e1_the_vocabulary_section_is_painted_first(tmp_path, size):
    """Verdict `E1`: the vocabulary comes BEFORE the keys, in both layouts,
    in the order `01b` §3.6 lists (pinned equal to these constants by
    `test_inc8_cr_f3_the_section_headers_and_footer_EQUAL_section_3_6`).
    Read from the painted frame: each header's first row, walking the pane
    top to bottom, and the vocabulary header visible with the pane at rest."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        screen = await _legend_from_map(app, pilot)
        pane = screen.query_one("#help-bindings")
        at_rest = "\n".join(_rows_in(screen, pane.region))
        rows = await _harvest(app, pilot, _rows_in, region_id="#help-bindings")
    order = (SECTION_VOCABULARY, SECTION_COLOURS, help_screen.SECTION_KEYS)
    first = [next((i for i, row in enumerate(rows) if header in row), None) for header in order]
    assert None not in first and first == sorted(first), dict(zip(order, first))
    assert SECTION_VOCABULARY in at_rest, "the vocabulary is not what the pane shows at rest"


@pytest.mark.parametrize("docked", [False, True], ids=["modal", "docked"])
def test_e1_no_painted_string_is_cut_at_either_budget(docked):
    """Verdict `E1`: the row budget re-derives from each width, and a label
    that would not fit is SHORTENED in the copy, never cut on screen.  Every
    string each layout paints appears whole -- `fit` would have replaced its
    tail with `…` -- and no row exceeds the layout's budget."""
    def whole(needle: str, text: Text, where: str) -> None:
        assert needle in text.plain, f"{where}: {needle!r} is cut at {screen.row_cells} cells"
        for line in text.plain.split("\n"):
            assert Text(line).cell_len <= screen.row_cells, (where, line)

    for view in sorted(darkside.LEGEND_VIEWS):
        screen = HelpScreen(SCOPE_MAP, view=view)
        screen.docked = docked
        whole(f"{help_screen.LEGEND_TITLE} · {view}", screen._render_title(), "title")  # noqa: SLF001
        vocabulary = screen._render_vocabulary(vocabulary_for(view))  # noqa: SLF001
        for _vid, _glyph, label, _style in vocabulary_for(view):
            whole(label, vocabulary, f"{view} vocabulary")
        colours = screen._render_colours()  # noqa: SLF001
        for _rid, _swatch, label, _token in help_screen.colours_for(view):
            whole(label, colours, f"{view} colours")
    for line in help_screen.FOOTER_LINES:
        whole(line, screen._render_footer(), "footer")  # noqa: SLF001
    own = screen._render_own_scope_keys()  # noqa: SLF001
    for _actions, word in help_screen.OWN_SCOPE_COPY:
        whole(word, own, "own-scope group")
    for scope in (SCOPE_MAP, keymap.SCOPE_HOME):
        keys = HelpScreen(scope)
        keys.docked = docked
        for binding in bindings_for(scope):
            whole(binding.label, keys._render_keymap(), f"{scope} keys")  # noqa: SLF001


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
    # Exempt by the painted TEXT, never by style: a chrome seat sharing a style
    # value with some vocabulary member (`MUT` is `V4b`'s) must still be read.
    exempt = {m[1].strip() for m in darkside.DECLARED_VOCABULARY if m[1]}
    exempt |= {c[1] for c in darkside.DECLARED_COLOURS}
    screen = HelpScreen(SCOPE_MAP, view="atlas")
    texts = [screen._render_title(), screen._render_keymap(),  # noqa: SLF001
             screen._render_vocabulary(vocabulary_for("atlas")),  # noqa: SLF001
             screen._render_colours(), screen._render_footer()]  # noqa: SLF001
    styles = {str(span.style) for text in texts for span in text.spans
              if (painted := text.plain[span.start:span.end].strip())
              and painted not in exempt}
    assert len(styles) >= 3, styles
    for style in styles:
        fg = Style.parse(style).color
        ratio = _contrast(_hex(fg), darkside.PANEL)
        assert ratio >= 4.5, f"{style} paints legend text at {ratio:.2f}:1 on PANEL"


# ---------------------------------------------------------------------------
# Inc-8 corrective pass 1 -- security findings and the remaining code-review
# findings that do not need a running app.

def test_inc8_sec_f1_fit_never_fabricates_a_row(monkeypatch):
    """`INC8-SEC-F1`.  `plain()` deliberately PRESERVES a literal LF and TAB --
    `widgets/inspector.py` hands a multi-line notes field through it into a
    widget that is allowed to wrap.  `fit()` has no such caller: every result
    becomes exactly ONE row of a fixed-width panel, so a label carrying an
    embedded LF painted a REAL second row once the padded string reached a
    `Text` sink -- a row the row-length budget never accounted for.
    """
    hostile = "\n q  BORRAR TODO"
    monkeypatch.setattr(keymap, "KEYMAP", [
        *keymap.KEYMAP, keymap.KeyBinding("f10", "F10", "home", hostile, "leave")])
    screen = HelpScreen(SCOPE_MAP, view="atlas")
    text = screen._render_keymap()  # noqa: SLF001
    lines = text.plain.split("\n")
    hostile_lines = [ln for ln in lines if "BORRAR TODO" in ln]
    assert len(hostile_lines) == 1, f"the label split across rows: {hostile_lines}"
    assert "F10" in hostile_lines[0], "the glyph and the label parted onto two rows"
    for line in lines:
        assert Text(line).cell_len <= LEGEND_ROW_CELLS, (Text(line).cell_len, line)


def test_inc8_sec_f2_resolve_style_raises_on_an_undeclared_word():
    """`INC8-SEC-F2`.  `resolve_style` used to hand an unrecognised word
    straight through: a declared style `link file:///x` painted a live OSC-8
    hyperlink, and `[bold]` reached `Style.parse` and raised THERE instead of
    at this boundary.  It now raises here, before any sink sees the word.
    """
    with pytest.raises(ValueError):
        darkside.resolve_style("link file:///x")
    with pytest.raises(ValueError):
        darkside.resolve_style("[bold]")
    # A declared style keeps working: the allow-list is additive, not a ban.
    assert (darkside.resolve_style("bold GROUND on WARN")
            == f"bold {darkside.GROUND} on {darkside.WARN}")


def test_inc8_f_sec_f1_the_style_allow_list_does_not_authorize_itself(monkeypatch):
    """`INC8-F-SEC-F1`.  The allow-list WAS `_declared_modifiers()` -- read from
    the declarations it guards -- so declaring `link file:///x` in a row
    allow-listed `link` and `file:///x`.  It is now the hard-coded
    `_STYLE_MODIFIERS`; what the declarations use must sit inside it, and a
    row declaring anything else raises at `resolve_style` -- the render
    returns no `Text` at all, so no sink ever parses the word.  Under the old
    derived allow-list the same call RETURNED a `Text` carrying a live link."""
    assert darkside._declared_modifiers() <= darkside._STYLE_MODIFIERS  # noqa: SLF001
    assert darkside._STYLE_MODIFIERS == frozenset({"bold", "on"})  # noqa: SLF001
    monkeypatch.setattr(darkside, "DECLARED_VOCABULARY", (
        *darkside.DECLARED_VOCABULARY, ("V1", "▐", "hostile", "link file:///x")))
    screen = HelpScreen(SCOPE_MAP, view="atlas")
    with pytest.raises(ValueError, match=r"^resolve_style: undeclared style word 'link'"):
        screen._render_vocabulary(vocabulary_for("atlas"))  # noqa: SLF001


@pytest.mark.parametrize("docked", [False, True], ids=["modal", "docked"])
def test_inc8_sec_f3_a_wide_close_key_cannot_blow_the_row_budget(monkeypatch, docked):
    """`INC8-SEC-F3`.  The close hint is built from a seat value nothing
    upstream bounds; an oversized one painted a 95-cell row from a 75-cell
    budget in `_render_title`.  Since verdict `E3` the hint's WORD is the
    legend's own copy (`close`), so the seat value that reaches the title is
    the key's GLYPH -- made huge here, in both layouts' budgets, and through
    the own-scope group too, which paints the same glyph.
    """
    huge = "X" * 200
    patched = [
        keymap.KeyBinding("escape", huge, "dismiss_none", "cerrar", "help")
        if (b.key, b.action, b.group) == ("escape", "dismiss_none", "help") else b
        for b in keymap.KEYMAP
    ]
    monkeypatch.setattr(keymap, "KEYMAP", patched)
    screen = HelpScreen(SCOPE_MAP, view="atlas")
    screen.docked = docked
    # Since round 3 the close hint is painted once, in the own-scope group:
    # the title no longer carries the seat's glyph at all.
    assert "XXXX" not in screen._render_title().plain  # noqa: SLF001
    text = screen._render_own_scope_keys()  # noqa: SLF001
    assert "XXXX" in text.plain, "the hostile glyph never reached this surface"
    for line in text.plain.split("\n"):
        assert Text(line).cell_len <= screen.row_cells, (Text(line).cell_len, line)


@pytest.mark.parametrize("docked", [False, True], ids=["modal", "docked"])
def test_inc8_p2_cr_f2_the_own_scope_group_is_its_title_and_two_lines(docked):
    """`INC8-P2-CR-F2` / verdict `E3`: the group compresses to its title plus the
    FEWEST lines its four items need -- two in the modal, where they always fit.

    Re-derived at Inc-9c (`INC9B-F1`: a label's width is a hidden input to a
    layout band).  The operator's `home end top/bottom` (K1) makes the second
    pair 42 cells against the docked row's 37, so the docked panel needs a third
    line; the old "exactly two, in both layouts" was the band of the old word.
    The expectation is derived from the grid, not written: the minimal number of
    lines that hold the items in `01b`'s order, at most `OWN_SCOPE_ITEMS_PER_LINE`
    to a line, each line within the row budget -- computed here independently of
    the renderer's own packing."""
    screen = HelpScreen(SCOPE_MAP, view="atlas")
    screen.docked = docked
    lines = screen._render_own_scope_keys().plain.split("\n")  # noqa: SLF001
    assert lines[0] == help_screen.LEGEND_OWN_SCOPE_GROUP, lines[0]

    seat = bindings_for(SCOPE_HELP)
    widths = []
    for actions, word in help_screen.OWN_SCOPE_COPY:
        glyphs = [b.glyph for b in seat if b.action in actions]
        widths.append(len(" ".join(glyphs)) + 1 + len(word))
    budget = screen.row_cells - len(help_screen._INDENT)  # noqa: SLF001
    sep = len(help_screen._ITEM_SEP)  # noqa: SLF001
    fewest = None
    for split in range(1 << (len(widths) - 1)):
        groups, cur = [], [widths[0]]
        for i, w in enumerate(widths[1:]):
            if split >> i & 1:
                groups.append(cur)
                cur = [w]
            else:
                cur.append(w)
        groups.append(cur)
        if all(len(g) <= help_screen.OWN_SCOPE_ITEMS_PER_LINE
               and sum(g) + sep * (len(g) - 1) <= budget for g in groups):
            fewest = len(groups) if fewest is None else min(fewest, len(groups))
    assert fewest is not None, (widths, budget)
    assert len(lines) - 1 == fewest, (docked, widths, budget, lines)
    assert fewest == (3 if docked else 2), (docked, fewest)


def test_inc8_p2_cr_f1_an_invisible_only_parent_is_not_painted_empty():
    """`INC8-P2-CR-F1`: `INC8-F-SEC-F2`'s crumb arm proved the TAIL; an
    ancestor is sized by the same rule and was untested.  A parent made only
    of a zero-width code point keeps its one visible cell."""
    line = darkside._crumb_line([chr(0x202E), "tail"], 80)  # noqa: SLF001
    assert line.plain == chr(0xFFFD) + " / tail", ascii(line.plain)


def test_inc8_f_sec_f2_an_invisible_only_part_is_not_painted_empty(monkeypatch):
    """`INC8-F-SEC-F2`.  `fit(s, 0)` is `""` by contract, and callers sized it
    by the RAW string: a part made only of zero-width code points measured 0
    cells, asked `fit` for 0, and vanished -- though `fit` would have painted
    it as a one-cell U+FFFD.  Callers now size by `darkside.shown_cells`.  The
    crumb's tail, and a legend sample, each keep a visible cell."""
    line = darkside._crumb_line(["root", "\u202e"], 80)  # noqa: SLF001
    assert line.plain.endswith("\ufffd"), f"the crumb's tail was painted empty: {line.plain!r}"
    assert darkside.shown_cells("\u202e") == 1 and darkside._cells("\u202e") == 0  # noqa: SLF001

    monkeypatch.setattr(darkside, "DECLARED_VOCABULARY", (
        *darkside.DECLARED_VOCABULARY, ("VZ", "\u200b", "an invisible sample", "INK")))
    monkeypatch.setitem(darkside.LEGEND_VIEWS, "atlas", (*darkside.LEGEND_VIEWS["atlas"], "VZ"))
    screen = HelpScreen(SCOPE_MAP, view="atlas")
    text = screen._render_vocabulary(vocabulary_for("atlas"))  # noqa: SLF001
    row = next(ln for ln in text.plain.split("\n") if "an invisible sample" in ln)
    assert "\ufffd" in row, f"the sample was painted empty: {row!r}"


def test_inc8_sec_f4_a_hostile_colour_label_is_coerced_and_bounded(monkeypatch):
    """`INC8-SEC-F4`.  No arm covered `DECLARED_COLOURS` coercion at all until
    this pass added one to `test_llr_n16_2_3_legend_coerces_and_bounds_every_string`
    (the real sink, through a running app).  This is the same guarantee read
    directly off `_render_colours`, without the app, for a fast, isolated proof.
    """
    # Reuses the module-level `HOSTILE` rather than spelling a second one: `C-56`
    # and the record's own scan requirement (no new literal control/bidi
    # character) are best satisfied by not retyping the U+202E escape at all.
    monkeypatch.setattr(darkside, "DECLARED_COLOURS", (
        *darkside.DECLARED_COLOURS, ("CX", "█", HOSTILE, "ACCENT")))
    monkeypatch.setitem(darkside.LEGEND_COLOURS, "atlas", (*darkside.LEGEND_COLOURS["atlas"], "CX"))
    screen = HelpScreen(SCOPE_MAP, view="atlas")
    text = screen._render_colours()  # noqa: SLF001
    assert "[bold red]x[/]" in text.plain, "the hostile label never reached the frame"
    for line in text.plain.split("\n"):
        assert Text(line).cell_len <= LEGEND_ROW_CELLS, (Text(line).cell_len, line)


def test_inc8_cr_f7_grouping_survives_a_non_adjacent_same_id_row():
    """`INC8-CR-F7`.  `itertools.groupby` only merges RUNS of equal keys, so a
    row's members SPLIT into two captions the moment a different id sat
    between them in declaration order -- true only because
    `DECLARED_VOCABULARY` happens to keep every row's members adjacent, a fact
    `_render_vocabulary` has no business depending on.
    """
    screen = HelpScreen(SCOPE_MAP, view="atlas")
    members = [
        ("V19", "█", "coverage microbar", "SAGE"),
        ("V19", "█", "coverage microbar", "INK"),
        ("V20", "▲ vence", "actas vencidas", "WARN on PANEL"),
        ("V19", "░", "coverage microbar", "WORDMARK"),
    ]
    text = screen._render_vocabulary(members)  # noqa: SLF001
    captions = text.plain.count("coverage microbar")
    assert captions == 1, f"V19 split into {captions} captions: {text.plain!r}"


def test_inc8_cr_f7_a_compound_line_cannot_exceed_the_row_budget():
    """`INC8-CR-F7`.  Each sample used to be clamped only against the ROW
    budget in isolation; several samples each individually under budget could
    still SUM past it, and the pad went silently negative (`" " * negative`
    is `""`, never an error) while the row it padded stayed over width.
    """
    screen = HelpScreen(SCOPE_MAP, view="atlas")
    members = [
        ("VX", "A" * 40, "una etiqueta", "INK"),
        ("VX", "B" * 40, "una etiqueta", "ACCENT"),
    ]
    text = screen._render_vocabulary(members)  # noqa: SLF001
    for line in text.plain.split("\n"):
        assert Text(line).cell_len <= LEGEND_ROW_CELLS, (Text(line).cell_len, line)


def test_inc8_ux_f11_the_scrollbar_thumb_clears_the_non_text_contrast_floor():
    """`INC8-UX-F11`.  WCAG 1.4.11 non-text contrast: the scrollbar THUMB is a
    UI component (it shows scroll position and is draggable) and must clear
    3:1 against its own track.  Textual's own default (unstyled) thumb
    measured 1.55:1 here.

    `ASH`, not `ACCENT`: `LLR-S06.3.3` seals the blue literal `#1783ff` at
    exactly 8 tracked sites (`B-43`, out of this pass's scope), so a 9th
    would break a sealed requirement having nothing to do with this pane.
    """
    assert f"scrollbar-color: {darkside.ASH};" in HelpScreen.CSS
    assert f"scrollbar-background: {darkside.PANEL};" in HelpScreen.CSS
    ratio = _contrast(darkside.ASH, darkside.PANEL)
    assert ratio >= 3.0, ratio


@pytest.mark.parametrize("s", [
    "left\tright", "first\nsecond", "carriage\rreturn", "中文字串",
], ids=["tab", "newline", "cr", "cjk"])
def test_inc8_p3_cr_f3_shown_cells_is_what_fit_actually_paints(s):
    """`INC8-P3-CR-F3`: `shown_cells` was UNPINNED -- no arm measured it
    against a real `fit` paint, and `_cells(darkside.plain(s))` (skipping
    `_row_text`'s tab/newline/CR-to-space translation) survives every
    existing arm.  `fit(s, big)` pads `_row_text(s)` out to `big` cells for a
    `big` no real caller would truncate against; stripped of that padding,
    its own cell length is exactly what a caller sizing by `shown_cells`
    was promised.  A control character changes the measure: `rich.cells`
    scores a bare `\\t`/`\\n`/`\\r` as ZERO cells, so the mutant under-counts
    by one cell per row-breaker, and a wide CJK string keeps both sides
    honest about double-width glyphs too."""
    big = 100
    assert darkside.shown_cells(s) == cell_len(darkside.fit(s, big).rstrip())


# ---------------------------------------------------------------------------
# TC-009.1 -- the settle assertion fails loud when the scroll never lands

async def test_tc_009_1_settle_assertion_fails_loud_when_the_scroll_never_lands(
        tmp_path, monkeypatch):
    """DDR / TC-009.1 (site `_effective_keys`).  With `Widget._scroll_to` a
    no-op, the positioning scroll can never land, and the helper's settle
    assertion -- `the positioning scroll did not land` -- must fire on the
    first key instead of sampling a pane that never moved.  Nothing else in
    the AT-008 sequence is touched: the same `_legend_from_map` +
    `_effective_keys` path, one size."""
    monkeypatch.setattr(Widget, "_scroll_to", lambda self, *args, **kwargs: None)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        screen = await _legend_from_map(app, pilot)
        with pytest.raises(AssertionError, match="positioning scroll did not land"):
            await _effective_keys(app, pilot, screen)
