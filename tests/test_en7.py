"""Inc-EN-7 -- `?` is a character in every text field (`T3`, `EN-Q3`, `B-72`).

Authority: `VERDICT-inc9-2026-09-30.md` Round 9 `T3`, `VERDICT-inc-en-2026-10-02.md` `EN-Q3` (supersedes
`INC9-UX-F2`), `BACKLOG` `B-72`, and `A-135`.  One rule: inside any `Input` the key types `?`; outside a text
field `?` opens the legend, and the palette's `legend` action opens it from anywhere.  Every arm presses the
real `question_mark` key.
"""
from __future__ import annotations

import inspect

import pytest
from textual.screen import Screen
from textual.widgets import Input

from mapper import app as app_module
from mapper import keymap
from mapper.app import ConstructScreen, MapperApp, PlugRepoScreen, _PromptScreen
from mapper.screens import help as help_screen
from mapper.screens.factory import FactoryScreen
from mapper.screens.help import HelpScreen
from mapper.screens.palette import CommandPalette
from mapper.widgets.inspector import FieldInput
from tests.test_repair_layout import _open_map, _tree

SIZES = [(118, 34), (87, 34)]
RULE = "? outside text fields opens this legend; inside a field it types ?"


async def _settle(pilot):
    await pilot.pause()
    await pilot.pause()


async def _plug(app, pilot):
    app.push_screen(PlugRepoScreen())
    await _settle(pilot)
    field = app.screen.query_one("#repo-input", Input)
    field.focus()
    await pilot.pause()
    assert app.focused is field
    return field


# -- in a text field `?` types ----------------------------------------------------------------------------------

@pytest.mark.parametrize("size", SIZES)
@pytest.mark.asyncio
async def test_question_mark_in_the_connect_repo_field_types_and_ends_the_value(tmp_path, size):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        field = await _plug(app, pilot)
        await pilot.press("a", "b", "slash", "c", "question_mark")
        await _settle(pilot)
        assert isinstance(app.screen, PlugRepoScreen), f"`?` opened {type(app.screen).__name__}"
        assert app.screen.query_one("#repo-input", Input).value == "ab/c?"
        assert app.focused is field


@pytest.mark.parametrize("size", SIZES)
@pytest.mark.parametrize("field_id", ["insp-title", "insp-notes", "insp-field-D"])
@pytest.mark.asyncio
async def test_question_mark_in_an_inspector_field_appends_and_keeps_the_content(tmp_path, size, field_id):
    """At 118 the inspector is on screen: a path the operator can take (`Tab`, a click).  At 87 it is not (the
    field has a 0x0 region): the 87 params are a PROGRAMMATIC-FOCUS control, they say what `focus()` does to a field
    nobody can see, not that an operator can reach it (`EN7-REV-F4`; `B-82` records the live path to it).  The
    region assertion below pins which of the two each param is."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        map_id = _tree(app)
        graph = app.store.load(map_id)
        graph.nodes["root"].ficha.notes = "a note"
        app.store.save(map_id, graph)
        screen = await _open_map(app, pilot, map_id)
        field = screen.query_one(f"#{field_id}", FieldInput)
        assert (field.region.area > 0) == (size == SIZES[0]), (size, field.region)
        before = field.value
        assert before, "the probe needs a field that holds something to lose"
        field.focus()
        await pilot.pause()
        assert app.focused is field
        assert field.selected_text == "", "focus must not select the whole value (B-72)"
        await pilot.press("question_mark")
        await _settle(pilot)
        assert isinstance(app.screen, type(screen)), f"`?` opened {type(app.screen).__name__}"
        assert field.value == before + "?"


@pytest.mark.parametrize("size", SIZES)
@pytest.mark.asyncio
async def test_question_mark_in_search_types(tmp_path, size):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = await _open_map(app, pilot, _tree(app))
        await pilot.press("slash")
        await _settle(pilot)
        box = screen.query_one("#search-input", Input)
        assert app.focused is box
        await pilot.press("question_mark")
        await _settle(pilot)
        assert app.screen is screen
        assert box.value == "?"


@pytest.mark.parametrize("size", SIZES)
@pytest.mark.asyncio
async def test_question_mark_in_the_palette_box_types(tmp_path, size):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        await pilot.press("ctrl+p")
        await _settle(pilot)
        palette = app.screen
        assert isinstance(palette, CommandPalette)
        await pilot.press("question_mark")
        await _settle(pilot)
        assert app.screen is palette
        assert palette.query_one("#palette-input", Input).value == "?"


@pytest.mark.parametrize("size", SIZES)
@pytest.mark.parametrize("make", [lambda: ConstructScreen(), lambda: _PromptScreen("save as", "x")])
@pytest.mark.asyncio
async def test_question_mark_in_a_prompt_types(tmp_path, size, make):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        prompt = make()
        app.push_screen(prompt)
        await _settle(pilot)
        box = prompt.query_one(Input)
        assert app.focused is box
        await pilot.press("question_mark")
        await _settle(pilot)
        assert app.screen is prompt
        assert "?" in box.value, box.value


# -- outside a text field `?` opens the legend ---------------------------------------------------------------------

@pytest.mark.parametrize("size", SIZES)
@pytest.mark.parametrize("where", ["map", "home", "factory"])
@pytest.mark.asyncio
async def test_question_mark_outside_a_field_opens_the_legend(tmp_path, size, where):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        if where == "map":
            await _open_map(app, pilot, _tree(app))
        elif where == "factory":
            app.push_screen(FactoryScreen(app.store.load(_tree(app))))
            await _settle(pilot)
        source = app.screen
        assert not isinstance(app.focused, Input), f"the probe needs no field focused: {app.focused!r}"
        await pilot.press("question_mark")
        await _settle(pilot)
        assert isinstance(app.screen, HelpScreen), f"`?` on {where} opened {type(app.screen).__name__}"
        assert app.screen.scope == source.KEY_SCOPE


@pytest.mark.parametrize("size", SIZES)
@pytest.mark.parametrize("where", ["map", "plug"])
@pytest.mark.asyncio
async def test_the_palette_legend_action_still_opens_the_legend(tmp_path, size, where):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        if where == "map":
            await _open_map(app, pilot, _tree(app))
        else:
            await _plug(app, pilot)
        source = app.screen
        await pilot.press("ctrl+p")
        await _settle(pilot)
        assert isinstance(app.screen, CommandPalette)
        for ch in "legend":
            await pilot.press(ch)
        await _settle(pilot)
        await pilot.press("enter")
        await _settle(pilot)
        assert isinstance(app.screen, HelpScreen), f"the palette's legend opened {type(app.screen).__name__}"
        assert app.screen.scope == source.KEY_SCOPE


# -- the mechanism: no screen raises `help` over a text field ---------------------------------------------------------

def _screen_classes():
    from mapper import screens as screens_pkg  # noqa: F401  (import the package so the modules below resolve)
    import importlib
    import pkgutil

    classes = {}
    for info in pkgutil.iter_modules(screens_pkg.__path__):
        module = importlib.import_module(f"mapper.screens.{info.name}")
        for _n, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, Screen):
                classes[cls] = None
    for _n, cls in inspect.getmembers(app_module, inspect.isclass):
        if issubclass(cls, Screen):
            classes[cls] = None
    return list(classes)


def test_no_screen_binds_the_question_mark_at_priority():
    offenders = []
    for cls in _screen_classes():
        for b in getattr(cls, "BINDINGS", []):
            key, priority = (b.key, b.priority) if hasattr(b, "key") else (b[0], False)
            if "question_mark" in key.split(",") and priority:
                offenders.append(cls.__name__)
    assert not offenders, offenders
    assert not [b for b in keymap.KEYMAP if b.key == "question_mark" and b.priority]


def test_the_connect_repo_field_has_no_question_mark_exception():
    assert not hasattr(app_module, "_RepoInput")
    assert "check_consume_key" not in inspect.getsource(app_module)


# -- the copy ---------------------------------------------------------------------------------------------------------

def test_the_footer_states_the_rule_and_fits_the_docked_row():
    assert " ".join(help_screen.FOOTER_LINES) == RULE, help_screen.FOOTER_LINES
    for line in help_screen.FOOTER_LINES:
        assert len(line) <= help_screen.LEGEND_DOCKED_ROW_CELLS, line
    source = inspect.getsource(help_screen).lower()
    assert "select-all" not in source and "select all" not in source


@pytest.mark.parametrize("size", SIZES)
@pytest.mark.asyncio
async def test_the_painted_legend_ends_with_the_rule(tmp_path, size):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        _tree(app)
        await pilot.pause()
        await pilot.press("question_mark")
        await _settle(pilot)
        legend = app.screen
        assert isinstance(legend, HelpScreen)
        pane = legend.query_one("#help-bindings")
        pane.scroll_to(y=pane.max_scroll_y, animate=False)
        await _settle(pilot)
        footer = legend.query_one("#help-footer")
        text = footer.content.plain
    assert " ".join(row.strip() for row in text.splitlines()) == RULE, text
