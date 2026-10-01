"""Inc-9e -- the operator's design answers L1-L3 and the palette's group column.

Authority: `.dev-flow/2026-08-26-ui-next-batch-02/VERDICT-inc9-2026-09-30.md`
(Round 2, Inc-9e).  Every arm was committed RED first, as a STRICT xfail keyed by
the step that closes it (`OPEN_STEPS`); each implementation commit deletes its own
step from that set, and an arm that then fails is a failure, not an xfail.

The operator's words (`L1`, `L2`, `L3`) are the specification.  Every painted word
is compared with the seat, and a SENTINEL relabel of the seat proves a hand-written
copy cannot pass: a copy cannot contain a word it has never heard.
"""
from __future__ import annotations

import ast
import dataclasses
import inspect
import re

import pytest

from mapper import darkside, keymap
from mapper.app import HomeScreen, MapperApp, MapScreen, PlugRepoScreen, keybar_groups
from mapper.screens.factory import FactoryScreen
from mapper.screens.help import HelpScreen
from mapper.screens.palette import CommandPalette
from mapper.screens.settings import SettingsScreen
from mapper.widgets.chrome import HintLine, KeyBar, TabStrip
from tests.test_repair_layout import _rows_in, _tree

#: Steps not yet implemented.  An arm keyed to a step in this set is a strict xfail.
OPEN_STEPS: set[str] = {"tabs", "hint", "cr_f6", "order", "palette"}


def red(step: str):
    if step not in OPEN_STEPS:
        return lambda fn: fn
    return pytest.mark.xfail(
        strict=True, reason=f"Inc-9e: committed RED; closed by the '{step}' step")


SIZE = (118, 34)
SIZES = [(118, 34), (87, 34), (140, 45)]

#: The home doors the tab strip shows, as seat actions (`L1`).
TAB_ACTIONS = ("consult", "plug", "construct", "factory")


def _home_rows(*actions):
    rows = [b for b in keymap.KEYMAP if b.scope == keymap.SCOPE_HOME and b.action in actions]
    assert len(rows) == len(actions), (actions, rows)
    return rows


def _strip_text(screen) -> str:
    """The tab strip's FIRST line: the tabs and the wordmark, not the crumb."""
    return screen.query_one(TabStrip).content.plain.split("\n")[0]


def _letters(text: str) -> list[str]:
    """Single-letter tokens of a strip line: a key glyph standing beside a name."""
    tokens = text.replace("mapper", " ").split()
    return [t for t in tokens if len(t) == 1 and t.isalpha()]


def _sentinel_seat(monkeypatch):
    seat = [dataclasses.replace(b, label=f"zz-{b.action}") for b in keymap.KEYMAP]
    monkeypatch.setattr(keymap, "KEYMAP", seat)
    monkeypatch.setattr(keymap, "GROUP_HEADER", {g: f"zz-{g}" for g in keymap.GROUP_HEADER})


async def _screens(app, pilot):
    """Yield (name, screen) for home, map, factory, components and connect repo."""
    yield "home", app.screen
    for name, make in (
        ("map", lambda: MapScreen(_tree(app))),
        ("factory", FactoryScreen),
        ("components", SettingsScreen),
        ("connect repo", PlugRepoScreen),
    ):
        app.push_screen(make())
        await pilot.pause()
        await pilot.pause()
        yield name, app.screen
        app.pop_screen()
        await pilot.pause()


# ---------------------------------------------------------------------------
# L1 -- tab letters only on home, with the seat's labels

@red("tabs")
@pytest.mark.asyncio
async def test_inc9e_l1_home_strip_paints_each_tab_letter_and_its_seat_label(tmp_path):
    """Every tab letter equals a seat key that opens that tab, and its label is the
    seat's (closes INC9BC-UX-F1: the strip said `browse`, the bar `browse maps`)."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        text = _strip_text(app.screen)
    rows = _home_rows(*TAB_ACTIONS)
    assert rows
    for b in rows:
        assert b.group == "doors", b
        assert f" {b.glyph} {b.label} " in text, (b.glyph, b.label, text)


@pytest.mark.asyncio
async def test_inc9e_l1_a_home_tab_letter_really_opens_its_tab(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        for b in _home_rows("plug", "factory"):
            await pilot.press(b.key)
            await pilot.pause()
            await pilot.pause()
            assert not isinstance(app.screen, HomeScreen), b
            await pilot.press("escape")
            await pilot.pause()
            await pilot.pause()
            assert isinstance(app.screen, HomeScreen), b


@red("tabs")
@pytest.mark.asyncio
async def test_inc9e_l1_no_other_screen_paints_a_key_letter_in_the_strip(tmp_path):
    """On the map `n` is `next match` and `f` is `focus branch`: a letter in the
    strip would give one key two meanings on one screen."""
    app = MapperApp(tmp_path)
    seen = []
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        async for name, screen in _screens(app, pilot):
            if name == "home":
                continue
            text = _strip_text(screen)
            seen.append(name)
            assert not _letters(text), (name, text)
            for b in _home_rows(*TAB_ACTIONS):
                assert f" {b.label} " in text, (name, b.label, text)
    assert seen == ["map", "factory", "components", "connect repo"], seen


@red("tabs")
@pytest.mark.asyncio
async def test_inc9e_l1_the_strip_follows_a_relabelled_seat_on_every_screen(tmp_path, monkeypatch):
    """A hand-written tab label equals today's seat word and passes an equality
    arm; a sentinel relabel cannot be guessed."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        map_id = _tree(app)
        _sentinel_seat(monkeypatch)
        for name, make in (("home", None), ("map", lambda: MapScreen(map_id)),
                           ("factory", FactoryScreen), ("connect repo", PlugRepoScreen)):
            if make:
                app.push_screen(make())
                await pilot.pause()
                await pilot.pause()
            strip = _strip_text(app.screen)
            for action in TAB_ACTIONS:
                assert f"zz-{action}" in strip, (name, action, strip)
            if make:
                app.pop_screen()
                await pilot.pause()


@red("tabs")
def test_inc9e_l1_only_the_home_strip_carries_letters_at_the_render_function():
    home = darkside.tab_strip("c", None).plain.split("\n")[0]
    assert len(_letters(home)) == len(TAB_ACTIONS), home
    for text in (darkside.tab_strip("c", ["m"]), darkside.tab_strip("f", None),
                 darkside.tab_strip("p", ["connect repo"]), darkside.tab_strip(None, ["c"])):
        assert not _letters(text.plain.split("\n")[0]), text.plain


# ---------------------------------------------------------------------------
# L2 -- `next ▸`

@red("hint")
@pytest.mark.asyncio
async def test_inc9e_l2_no_hint_line_says_siguiente(tmp_path):
    """A census over the hint lines: the render function and every `HintLine`
    painted on the screens the batch ships."""
    assert darkside.hint_line("probe").plain.startswith("next ▸ ")
    app = MapperApp(tmp_path)
    painted = []
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        async for _name, screen in _screens(app, pilot):
            for hint in screen.query(HintLine):
                painted.append(hint.content.plain)
    assert len(painted) >= 4, painted
    assert all("siguiente" not in p.lower() for p in painted), painted
    assert all(p.startswith("next ▸ ") for p in painted), painted


# ---------------------------------------------------------------------------
# INC9BC-CR-F6 -- an explicit "no active tab"

@red("cr_f6")
def test_inc9e_cr_f6_the_components_screen_passes_none_not_a_tab_key():
    import mapper.screens.settings as settings
    calls = [n for n in ast.walk(ast.parse(inspect.getsource(settings)))
             if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "TabStrip"]
    assert len(calls) == 1, calls
    first = calls[0].args[0]
    assert isinstance(first, ast.Constant) and first.value is None, ast.dump(first)


def test_inc9e_cr_f6_none_marks_no_tab():
    text = darkside.tab_strip(None, ["components"])
    accent = f"on {darkside.ACCENT}"
    assert not [s for s in text.spans if accent in str(s.style)], text.spans
    marked = darkside.tab_strip("c", None)
    assert [s for s in marked.spans if accent in str(s.style)], "control: a real tab is marked"


# ---------------------------------------------------------------------------
# L3 -- the home doors come first

@red("order")
def test_inc9e_l3_home_bar_and_legend_order_start_with_open():
    order = keymap.bar_group_order(keymap.SCOPE_HOME)
    heads = [keymap.group_header(g) for g in order]
    assert heads[0] == "open" and heads.index("open") < heads.index("maps"), heads
    assert keybar_groups(keymap.SCOPE_HOME) == order
    legend = HelpScreen(keymap.SCOPE_HOME)._render_keymap().plain  # noqa: SLF001
    titles = [ln for ln in legend.split("\n")[1:] if ln and not ln.startswith(" ")]
    assert titles[:2] == ["open", "maps"], titles


@red("order")
@pytest.mark.parametrize("size", SIZES[:2])
@pytest.mark.asyncio
async def test_inc9e_l3_the_home_bar_paints_the_doors_first(tmp_path, size):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        rows = _rows_in(app.screen, app.screen.query_one(KeyBar).region)
    joined = " ".join(r.strip() for r in rows)
    assert joined.startswith("open "), joined
    assert "browse maps" in joined, joined


# ---------------------------------------------------------------------------
# INC9C-F2 / INC9BC-UX-F4 -- the palette

async def _palette_rows(app, pilot):
    app.action_palette()
    await pilot.pause()
    await pilot.pause()
    pal = app.screen
    assert isinstance(pal, CommandPalette), pal
    rows = [item.query_one("Static").content.plain
            for item in pal.query("#palette-list > ListItem")]
    footer = pal.query_one("#palette-count").content.plain
    placeholder = pal.query_one("#palette-input").placeholder
    return pal, rows, footer, placeholder


@red("palette")
@pytest.mark.parametrize("opener", ["home", "map"])
@pytest.mark.asyncio
async def test_inc9e_palette_paints_header_words_in_the_bar_order(tmp_path, opener):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        scope = keymap.SCOPE_HOME
        if opener == "map":
            app.push_screen(MapScreen(_tree(app)))
            await pilot.pause()
            await pilot.pause()
            scope = keymap.SCOPE_MAP
        pal, rows, _footer, _ph = await _palette_rows(app, pilot)
        items = list(pal._items)  # noqa: SLF001
    assert items and len(rows) == len(items)
    painted = []
    for row, b in zip(rows, items):
        head = keymap.group_header(b.group)
        assert row.startswith(head + " "), (row, head)
        if b.group != head:
            assert not re.match(rf"{re.escape(b.group)}\b", row), ("raw group id painted", row)
        if not painted or painted[-1] != head:
            painted.append(head)
    expected = [keymap.group_header(g) for g in keymap.bar_group_order(scope)
                if any(b.group == g for b in items)]
    assert painted == expected, (painted, expected)


@red("palette")
@pytest.mark.asyncio
async def test_inc9e_palette_paints_no_raw_group_id_anywhere(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        app.push_screen(MapScreen(_tree(app)))
        await pilot.pause()
        await pilot.pause()
        _pal, rows, _f, _p = await _palette_rows(app, pilot)
    raw = {g for g, h in keymap.GROUP_HEADER.items() if g != h} - set(keymap.GROUP_HEADER.values())
    assert {"nav", "doors", "list", "app"} <= raw
    assert rows
    for row in rows:
        assert row.split(" ", 1)[0] not in raw, row


@red("palette")
@pytest.mark.asyncio
async def test_inc9e_palette_footer_and_placeholder_are_english(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        _pal, rows, footer, placeholder = await _palette_rows(app, pilot)
    total = len(rows)
    assert footer.strip().startswith(f"{total}/{total} actions"), footer
    for spanish in ("acciones", "ejecutar", "cerrar", "comando"):
        assert spanish not in footer + placeholder, (footer, placeholder)
    assert "run" in footer and "close" in footer, footer


@red("palette")
@pytest.mark.asyncio
async def test_inc9e_palette_footer_words_come_from_the_seat(tmp_path, monkeypatch):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        _sentinel_seat(monkeypatch)
        _pal, _rows, footer, _ph = await _palette_rows(app, pilot)
    assert keymap.hint_pair(keymap.SCOPE_PALETTE, "run_selected") in footer, footer
    assert keymap.hint_pair(keymap.SCOPE_PALETTE, "dismiss_none") in footer, footer
    assert "zz-run_selected" in footer and "zz-dismiss_none" in footer, footer


@red("palette")
@pytest.mark.asyncio
async def test_inc9e_palette_headers_follow_a_relabelled_seat(tmp_path, monkeypatch):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        _sentinel_seat(monkeypatch)
        _pal, rows, _f, _p = await _palette_rows(app, pilot)
    assert rows and all(r.startswith("zz-") for r in rows), rows
