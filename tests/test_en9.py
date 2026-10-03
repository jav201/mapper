"""Inc-EN-9 -- a screen whose only control is a text field does not list `?` (`E4`, `EN7-REV-F1`).

Authority: `VERDICT-inc-en-2026-10-02.md` Round 4 (`E4`), `A-137`.  On connect-repo the only focusable control is
the text field, so `?` always types there (`A-135`): the key bar and the legend must not list a chord that cannot
fire.  `ctrl+p palette` stays on the bar and the palette's `legend` action still opens the legend.  Every arm presses
real keys at 118 and 87 columns.  The arms marked RED were committed `xfail(strict=True)` and measured RED on
`9105abc` (with `--runxfail`); the source commit removed the marker.
"""
from __future__ import annotations

import dataclasses
import re

import pytest
from textual.widgets import Input, Static

from mapper import keymap
from mapper.app import MapperApp, PlugRepoScreen, RepoScreen
from mapper.github import GitHubConnector, GitHubError
from mapper.screens.factory import FactoryScreen
from mapper.screens.help import HelpScreen
from mapper.screens.palette import CommandPalette
from mapper.screens.settings import SettingsScreen
from mapper.widgets.chrome import KeyBar
from tests.test_repair_layout import _open_map, _tree

SIZES = [(118, 34), (87, 34)]
RED = pytest.mark.xfail(strict=True, reason="E4: the connect-repo bar and legend still list `?`")


async def _settle(pilot):
    await pilot.pause()
    await pilot.pause()


async def _open(app, pilot, where, monkeypatch=None):
    """Put *where* on screen and return it, no text field focused except on connect-repo."""
    if where == "plug":
        app.push_screen(PlugRepoScreen())
    elif where == "map":
        await _open_map(app, pilot, _tree(app))
    elif where == "factory":
        app.push_screen(FactoryScreen(app.store.load(_tree(app))))
    elif where == "settings":
        app.push_screen(SettingsScreen())
    elif where == "repo":
        def fetch(self, progress=None):
            raise GitHubError("stub")
        monkeypatch.setattr(GitHubConnector, "fetch", fetch)
        app.push_screen(RepoScreen("owner/name"))
    await _settle(pilot)
    return app.screen


def _bar(screen) -> str:
    return screen.query_one(KeyBar).content.plain


def _legend(app) -> str:
    pane = app.screen.query_one("#help-bindings")
    return "\n".join(s.content.plain for s in pane.query(Static))


async def _legend_from_the_palette(app, pilot):
    await pilot.press("ctrl+p")
    await _settle(pilot)
    assert isinstance(app.screen, CommandPalette)
    for ch in "legend":
        await pilot.press(ch)
    await _settle(pilot)
    await pilot.press("enter")
    await _settle(pilot)
    assert isinstance(app.screen, HelpScreen), type(app.screen).__name__
    return _legend(app)


# -- connect-repo: the chord that only types is not listed ---------------------------------------------------------

@RED
@pytest.mark.parametrize("size", SIZES)
@pytest.mark.asyncio
async def test_the_connect_repo_bar_does_not_list_the_question_mark(tmp_path, size):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, "plug")
        bar = _bar(screen)
        await pilot.press("question_mark")
        await _settle(pilot)
        typed = screen.query_one("#repo-input", Input).value
    assert "?" not in bar and "legend" not in bar, bar
    assert "ctrl+p palette" in bar, bar
    assert typed == "?", "the key the bar no longer lists is the key that types"


@RED
@pytest.mark.parametrize("size", SIZES)
@pytest.mark.asyncio
async def test_the_legend_opened_from_the_palette_on_connect_repo_does_not_list_the_question_mark(tmp_path, size):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        await _open(app, pilot, "plug")
        text = await _legend_from_the_palette(app, pilot)
    assert "ctrl+p" in text, text
    assert re.search(r"^\s+\? +legend", text, re.M) is None, text


@RED
def test_bindings_for_a_text_only_scope_offers_only_keys_that_work():
    rows = keymap.bindings_for(keymap.SCOPE_PLUG)
    assert [b.glyph for b in rows if b.scope == keymap.SCOPE_APP] == ["ctrl+p"], rows
    assert all(b.action != "help" for b in rows)
    assert [b for b in keymap.palette_items("legend", keymap.SCOPE_PLUG) if b.action == "help"], (
        "the palette still offers the legend action there"
    )


# -- every other screen keeps `? legend` and it works --------------------------------------------------------------

@pytest.mark.parametrize("size", SIZES)
@pytest.mark.parametrize("where", ["home", "map", "factory", "repo"])
@pytest.mark.asyncio
async def test_other_screens_still_list_the_question_mark_and_it_opens_the_legend(tmp_path, monkeypatch, size, where):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, where, monkeypatch)
        bar = _bar(screen)
        assert not isinstance(app.focused, Input), app.focused
        await pilot.press("question_mark")
        await _settle(pilot)
        opened = type(app.screen).__name__
        text = _legend(app) if isinstance(app.screen, HelpScreen) else ""
    # A long bar folds its tail into `... +N  ? all keys` (`darkside.keybar`); either spelling is the `?` row.
    assert re.search(r"\? (legend|all keys)", bar), bar
    assert opened == "HelpScreen", opened
    assert "legend" in text, text


# -- derivation: the seat decides, not a painted string ----------------------------------------------------------

def _relabelled():
    return [
        dataclasses.replace(b, glyph="ZZ", label="zz-legend") if b.action == "help" and b.scope == keymap.SCOPE_APP else b
        for b in keymap.KEYMAP
    ]


@pytest.mark.parametrize("size", SIZES)
@pytest.mark.parametrize("where", ["plug", "settings"])
@pytest.mark.asyncio
async def test_a_relabelled_seat_row_is_listed_where_it_works_and_absent_where_it_only_types(
    tmp_path, monkeypatch, size, where
):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        monkeypatch.setattr(keymap, "KEYMAP", _relabelled())
        screen = await _open(app, pilot, where)
        bar = _bar(screen)
        await pilot.press("ctrl+p")
        await _settle(pilot)
        palette_rows = [b.label for b in app.screen._items]
    if where == "settings":
        assert "ZZ zz-legend" in bar, bar
    else:
        assert "ZZ" not in bar and "zz-legend" not in bar, bar
        assert "zz-legend" in palette_rows, palette_rows
