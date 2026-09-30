"""Inc-9 -- help scope routing, the seat migration of the last two help screens,
the English chrome, and `LLR-N06.2.5`'s notify census.

Every subject set below is DERIVED from the product at run time -- the screen
set from the product modules' `Screen` subclasses, the label set from the live
`KEYMAP`, the header set from the screens' own `compose` source, the notify
sites from the AST -- and each derivation asserts it is non-empty before any
member is judged.  The one declaration is `CHROME_LEXICON`: a dictionary cannot
be derived from the code it judges (`A-112`).
"""
from __future__ import annotations

import ast
import importlib
import inspect
import pathlib
import pkgutil
import re
import subprocess
import sys
import types
import unicodedata

import pytest
from textual.binding import Binding
from textual.screen import Screen

import mapper
from mapper import darkside, keymap
from mapper.app import MapperApp
from mapper.keymap import bindings_for
from mapper.model import Graph
from mapper.screens.help import LEGEND_TITLE, HelpScreen
from tests.test_help_scope import _harvest
from tests.test_repair_layout import WIDE_SIZES, _open_map, _rows_in, _tree

ROOT = pathlib.Path(mapper.__file__).resolve().parent.parent
SIZE = WIDE_SIZES[0]
#: The help chord, read from the seat rather than typed.
HELP_CHORD = next(b.key for b in keymap.KEYMAP if b.action == "help")


def _product_modules() -> list[types.ModuleType]:
    return [importlib.import_module(info.name)
            for info in pkgutil.walk_packages(mapper.__path__, "mapper.")]


PRODUCT_MODULES = _product_modules()


def _product_sources() -> dict[str, str]:
    out = {}
    for module in PRODUCT_MODULES:
        path = pathlib.Path(module.__file__)
        out[path.relative_to(ROOT).as_posix()] = path.read_text(encoding="utf-8")
    assert out, "no product source was read"
    return out


# ---------------------------------------------------------------------------
# LLR-N16.1.1 -- the screen set is derived, never enumerated

def _help_screens(modules) -> dict[str, type[Screen]]:
    """Every `Screen` subclass a product module DEFINES whose merged bindings
    carry the help chord.  Named offenders are forbidden by `LLR-N16.1.1`."""
    found = {}
    for module in modules:
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if (issubclass(cls, Screen) and cls.__module__ == module.__name__
                    and HELP_CHORD in cls._merged_bindings.key_to_bindings):  # noqa: SLF001
                found[cls.__name__] = cls
    assert found, "the derived help-screen set is empty: nothing below would be judged"
    return found


HELP_SCREENS = _help_screens(PRODUCT_MODULES)


def test_llr_n16_1_1_the_screen_set_is_derived_and_large_enough():
    assert len(HELP_SCREENS) >= 7, sorted(HELP_SCREENS)


def test_llr_n16_1_1_an_emptied_derivation_turns_red():
    """The mutation arm the LLR names: an empty module set must not pass."""
    with pytest.raises(AssertionError, match="empty"):
        _help_screens([])


# ---------------------------------------------------------------------------
# LLR-N16.1.2 -- every help screen declares a scope the seat really offers

@pytest.mark.xfail(strict=True, reason="RED until Inc-9 declares SCOPE_FACTORY/SCOPE_SETTINGS")
def test_llr_n16_1_2_every_help_screen_declares_a_scope():
    declared = set(keymap.GROUP_SCOPE.values())
    undeclared = sorted(name for name, cls in HELP_SCREENS.items()
                        if getattr(cls, "KEY_SCOPE", None) not in declared)
    assert undeclared == [], f"help screens with no declared seat scope: {undeclared}"
    thin = {name: len(bindings_for(cls.KEY_SCOPE)) for name, cls in HELP_SCREENS.items()
            if len(bindings_for(cls.KEY_SCOPE)) < 3}
    assert thin == {}, f"a declared scope the seat leaves (nearly) empty: {thin}"


@pytest.mark.xfail(strict=True, reason="RED until Inc-9 migrates both screens (C-D9b)")
def test_cd9b_unmigrated_screens_shrinks_to_the_two_left():
    assert keymap.UNMIGRATED_SCREENS == ("EditorScreen", "CoverageScreen")


# ---------------------------------------------------------------------------
# HLR-N16.1 / B-18 -- every route carries its scope, read from the painted panel

def _factory_graph(app) -> Graph:
    return app.store.load(_tree(app))


#: How the arm below reaches each derived screen.  NOT the subject set: the
#: completeness arm under it fails if a derived help screen has no opener.
OPENERS = {
    "HomeScreen": None,
    "MapScreen": "map",
    "_ImportPreviewScreen": lambda app, cls: cls(_factory_graph(app), pathlib.Path("nodos.csv")),
    "PlugRepoScreen": lambda app, cls: cls(),
    "RepoScreen": lambda app, cls: cls("owner/name"),
    "FactoryScreen": lambda app, cls: cls(_factory_graph(app)),
    "SettingsScreen": lambda app, cls: cls(),
}
#: The executed pre-state (M-11): these five open the legend on `app`.
RED_BEFORE_INC9 = {"_ImportPreviewScreen", "PlugRepoScreen", "RepoScreen",
                   "FactoryScreen", "SettingsScreen"}


def test_every_derived_help_screen_has_an_opener():
    assert set(OPENERS) == set(HELP_SCREENS)


def _key_rows(rows: list[str]) -> set[tuple[str, str]]:
    """(glyph, label) of every key row `_render_keymap` paints: the indent,
    a 10-cell key column, then the label.  Group headers and the section
    header carry no indent and are skipped."""
    out = set()
    for row in rows:
        if row.startswith("  ") and row[2:3].strip():
            out.add((row[2:12].strip(), row[12:].strip()))
    return out


def _route_params():
    for name in sorted(HELP_SCREENS):
        marks = [pytest.mark.xfail(strict=True, reason="B-18 / LLR-N16.1.2, RED before Inc-9")] \
            if name in RED_BEFORE_INC9 else []
        yield pytest.param(name, marks=marks, id=name)


@pytest.mark.parametrize("name", list(_route_params()))
async def test_hlr_n16_1_every_help_route_carries_its_scope(tmp_path, monkeypatch, name):
    """Press the real help chord on each derived screen: the legend opens on
    THAT screen's declared scope, its title names the screen's view, and the
    key rows it paints -- harvested across every scroll position of the
    `#help-content` widget -- EQUAL `bindings_for(source.KEY_SCOPE)`.

    Keyed on the SOURCE screen's scope, never the legend's own: the naive
    oracle is true on the broken screen (`HLR-N16.1`, M-11)."""
    monkeypatch.setattr("mapper.app.GitHubConnector.fetch",
                        lambda self, progress=None: Graph())
    cls = HELP_SCREENS[name]
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        opener = OPENERS[name]
        if opener == "map":
            await _open_map(app, pilot, _tree(app))
        elif opener is not None:
            app.push_screen(opener(app, cls))
            await pilot.pause()
            await pilot.pause()
        source = app.screen
        assert type(source) is cls
        # `H1`: `?` explains the view outside text fields.  The plug screen's
        # only widget IS a text field (`INC9-F3`), so focus leaves it first.
        app.set_focus(None)
        await pilot.press(HELP_CHORD)
        await pilot.pause()
        await pilot.pause()
        legend = app.screen
        assert isinstance(legend, HelpScreen), f"{name}: the help chord opened no legend"
        scope = getattr(cls, "KEY_SCOPE", None)
        assert legend.scope == scope, f"{name} opened the legend on {legend.scope!r}"
        view = getattr(source, "legend_view", None) or scope
        title = _rows_in(legend, legend.query_one("#help-title").region)
        assert any(f"{LEGEND_TITLE} · {view}" in row for row in title), title
        rows = await _harvest(app, pilot, _rows_in, "#help-content")
    expected = {(b.glyph, b.label) for b in bindings_for(scope)}
    painted = _key_rows(rows)
    assert painted == expected, (
        f"{name}: painted but not the scope's {sorted(painted - expected)}; "
        f"the scope's but not painted {sorted(expected - painted)}")


def _help_constructions() -> list[tuple[str, int, ast.Call]]:
    out = []
    for path, source in _product_sources().items():
        for node in ast.walk(ast.parse(source)):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "HelpScreen"):
                out.append((path, node.lineno, node))
    return out


@pytest.mark.xfail(strict=True, reason="B-18: five un-scoped HelpScreen() routes before Inc-9")
def test_b18_no_product_site_constructs_an_unscoped_legend():
    sites = _help_constructions()
    assert sites, "the AST walk found no HelpScreen construction: the probe is broken"
    unscoped = [(p, line) for p, line, call in sites
                if not call.args and not any(k.arg == "scope" for k in call.keywords)]
    assert unscoped == [], unscoped


# ---------------------------------------------------------------------------
# C-D9a -- the `tab` drop on SettingsScreen, gated on a WORKING positive control

async def _tab_walk(tmp_path, cls) -> list[int]:
    """Nine real `tab` presses; each focused widget as its index in the
    screen's own focus chain, so two apps' walks compare."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        app.push_screen(cls())
        await pilot.pause()
        await pilot.pause()
        chain = list(app.screen.focus_chain)
        walk = []
        for _ in range(9):
            await pilot.press("tab")
            await pilot.pause()
            walk.append(chain.index(app.focused) if app.focused in chain else -1)
    return walk


@pytest.mark.xfail(strict=True, reason="RED: the sheet has no focus chain before Inc-9 (A-112 st. 8)")
async def test_cd9a_the_probe_sees_a_transition_and_the_drop_is_neutral(tmp_path):
    from mapper.screens.settings import SettingsScreen

    class WithScreenTab(SettingsScreen):
        """The pre-drop bindings, re-declared: the POSITIVE control."""
        BINDINGS = [Binding("tab", "focus_next", "", priority=True),
                    Binding("shift+tab", "focus_previous", "", priority=True)]

    control = await _tab_walk(tmp_path / "control", WithScreenTab)
    shipped = await _tab_walk(tmp_path / "shipped", SettingsScreen)
    transitions = sum(a != b for a, b in zip(control, control[1:]))
    assert -1 not in control and transitions >= 1, (
        f"the probe cannot see a focus transition, so it cannot judge the drop: {control}")
    assert shipped == control, f"dropping the screen's tab changed traversal: {shipped} vs {control}"
    assert "SettingsScreen" not in keymap.TAB_BINDING_EXCEPTIONS


# ---------------------------------------------------------------------------
# LLR-N14.3.2 (C-D6b) -- the nine-press guard, re-run after Inc-9

async def test_llr_n14_3_2_nine_tabs_from_the_map_still_walk_the_ring(tmp_path):
    """Re-run as `C-D6b` requires.  The ring is DERIVED from the screen's own
    focus chain (this fixture's schema paints fewer inspector fields than the
    M-10 measurement's, so the 9-target literal does not apply to it): nine
    presses make eight transitions, each to the NEXT member of the ring."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 45)) as pilot:
        await _open_map(app, pilot, _tree(app))
        ring = list(app.screen.focus_chain)
        walk = []
        for _ in range(9):
            await pilot.press("tab")
            await pilot.pause()
            walk.append(ring.index(app.focused))
    assert len(ring) >= 2, ring
    assert len(set(walk)) == min(9, len(ring))
    assert sum(a != b for a, b in zip(walk, walk[1:])) == 8
    assert all(b == (a + 1) % len(ring) for a, b in zip(walk, walk[1:])), walk


# ---------------------------------------------------------------------------
# #D10 -- `.factory-tag` retoned (Inc-1 registered it, Inc-9 closes it)

@pytest.mark.xfail(strict=True, reason="RED: ACCENT on a label until Inc-9 retones it")
def test_d10_the_factory_tag_is_painted_in_mut():
    from mapper.screens.factory import FactoryScreen

    match = re.search(r"\.factory-tag\s*\{\s*color:\s*(#[0-9a-fA-F]{6})", FactoryScreen.CSS)
    assert match, "the .factory-tag rule is gone; the register row it closes needs rereading"
    assert match.group(1).lower() == darkside.MUT.lower()


# ---------------------------------------------------------------------------
# LLR-N06.2.5 -- every dynamic notify site is markup-off AND coerced

def _is_plain(node) -> bool:
    return isinstance(node, ast.Call) and (
        (isinstance(node.func, ast.Attribute) and node.func.attr == "plain")
        or (isinstance(node.func, ast.Name) and node.func.id == "plain"))


def _notify_sites() -> list[tuple[str, int, ast.Call]]:
    out = []
    for path, source in _product_sources().items():
        for node in ast.walk(ast.parse(source)):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "notify"):
                out.append((path, node.lineno, node))
    return out


def _coerced(arg) -> bool:
    """`A-112` st. 7: the whole message through `plain()`, or every
    interpolated value through it.  No third shape."""
    if _is_plain(arg):
        return True
    if isinstance(arg, ast.JoinedStr):
        return all(_is_plain(v.value) for v in arg.values if isinstance(v, ast.FormattedValue))
    return False


@pytest.mark.xfail(strict=True, reason="RED: 16 dynamic sites uncoerced before Inc-9")
def test_llr_n06_2_5_notify_sites_are_coerced():
    sites = _notify_sites()
    assert len(sites) > 0, "the AST walk found no notify call: the census is vacuous"
    dynamic = [(p, n, c) for p, n, c in sites if c.args and not isinstance(c.args[0], ast.Constant)]
    assert dynamic, "no dynamic site: nothing below is judged"
    markup_on = [(p, n) for p, n, c in dynamic
                 if not any(k.arg == "markup" and isinstance(k.value, ast.Constant)
                            and k.value.value is False for k in c.keywords)]
    assert markup_on == [], f"dynamic notify sites parsing markup: {markup_on}"
    uncoerced = [(p, n) for p, n, c in dynamic if not _coerced(c.args[0])]
    assert uncoerced == [], f"dynamic notify sites not routed through plain(): {uncoerced}"


def test_llr_n06_2_5_the_coercion_predicate_discriminates():
    """Positive and negative controls for `_coerced`, so the census cannot be
    green because the predicate accepts everything."""
    def arg(src):
        return ast.parse(src, mode="eval").body
    assert _coerced(arg("darkside.plain(f'x {e}')"))
    assert _coerced(arg("f'x {darkside.plain(e)} {plain(n)}'"))
    assert not _coerced(arg("f'x {e}'"))
    assert not _coerced(arg("f'x {darkside.plain(e)} {n}'"))
    assert not _coerced(arg("str(exc)"))


# ---------------------------------------------------------------------------
# A-112 -- English chrome: the language census

#: The declared English vocabulary of the chrome (`A-112`).  Adding a word is
#: a deliberate edit in the commit that paints it.
CHROME_LEXICON = frozenset("""
    add all app archive attachment back bottom branch browse build card child choose
    close command component connect coverage csv default details diff disabled document
    documents doors down edit export factory file focus focused fold from generate go
    hide home import last leave legend list map maps match mind missing nav new next node
    office open outline page palette pan parent plug previous quit rail remove repo
    repository resume right left run save scroll search settings show sibling start svg
    template to toggle top tree undo up view
""".split())

#: Screen headers outside Inc-9's declared files, owned by the increment that
#: closes each (`A-112` "Split").  The stale guard below reddens when one goes.
LANGUAGE_EXCEPTIONS = {
    ("mapper/screens/coverage.py", "cobertura incompleta"): "Inc-9b",
    ("mapper/screens/editor.py", "editar documento"): "Inc-9b",
}


def _seat_strings() -> list[tuple[str, str]]:
    out = [("mapper/keymap.py", b.label) for b in keymap.KEYMAP]
    out += [("mapper/keymap.py", group) for group in keymap.GROUP_SCOPE]
    return out


def _keybar_literals() -> list[tuple[str, str]]:
    """Group headers and labels of every hand-written `KeyBar([...])` literal."""
    out = []
    for path, source in _product_sources().items():
        for node in ast.walk(ast.parse(source)):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "KeyBar" and node.args
                    and isinstance(node.args[0], ast.List)):
                continue
            for group in node.args[0].elts:
                name, pairs = group.elts
                out.append((path, name.value))
                out += [(path, pair.elts[1].value) for pair in pairs.elts]
    return out


_HEADER_ID = re.compile(r"-(title|header|label)$")


def _screen_headers() -> list[tuple[str, str]]:
    """`A-112` st. 4 (a)-(c), from the source: the tab strip's labels, the
    literal crumbs passed to `TabStrip`, and the literal text of a `Static` or
    `Label` whose id names it a title, header or label -- inside every product
    `Screen` subclass."""
    out = []
    tab_strip = ast.parse(inspect.getsource(darkside.tab_strip))
    for node in ast.walk(tab_strip):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "tabs":
            out += [("mapper/darkside.py", pair.elts[1].value) for pair in node.value.elts]
    screens = {cls.__name__ for module in PRODUCT_MODULES
               for _, cls in inspect.getmembers(module, inspect.isclass)
               if issubclass(cls, Screen) and cls.__module__ == module.__name__}
    for path, source in _product_sources().items():
        for cls_node in ast.walk(ast.parse(source)):
            if not (isinstance(cls_node, ast.ClassDef) and cls_node.name in screens):
                continue
            for node in ast.walk(cls_node):
                if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
                    continue
                kw = {k.arg: k.value for k in node.keywords}
                if node.func.id == "TabStrip" and isinstance(kw.get("crumb"), ast.List):
                    out += [(path, e.value) for e in kw["crumb"].elts
                            if isinstance(e, ast.Constant) and isinstance(e.value, str)]
                ident = kw.get("id")
                if (node.func.id in ("Static", "Label") and node.args
                        and isinstance(node.args[0], ast.Constant)
                        and isinstance(ident, ast.Constant) and _HEADER_ID.search(ident.value)):
                    out.append((path, node.args[0].value))
    return out


def _judge(strings: list[tuple[str, str]]) -> list[tuple[str, str, str]]:
    bad = []
    for path, text in strings:
        if (path, text) in LANGUAGE_EXCEPTIONS:
            continue
        accented = [c for c in text if ord(c) > 127 and unicodedata.category(c).startswith("L")]
        if accented:
            bad.append((path, text, f"non-ASCII letter {accented}"))
        unknown = [w for w in re.findall(r"[^\W\d_]+", text.lower()) if w not in CHROME_LEXICON]
        if unknown:
            bad.append((path, text, f"not in the chrome lexicon: {unknown}"))
    return bad


@pytest.mark.parametrize("source", ["seat", "keybar", "headers"])
@pytest.mark.xfail(strict=True, reason="RED: Spanish chrome before Inc-9 (A-112)")
def test_a112_the_chrome_is_english(source):
    strings = {"seat": _seat_strings, "keybar": _keybar_literals,
               "headers": _screen_headers}[source]()
    assert strings, f"the {source} derivation is empty: nothing would be judged"
    assert _judge(strings) == []


def test_a112_the_language_judge_discriminates():
    """Controls for `_judge`: a Spanish word, an accented letter and an
    English word outside the lexicon are each caught; lexicon words pass."""
    assert _judge([("x", "open card")]) == []
    assert _judge([("x", "salir")]), "a Spanish word passed"
    assert _judge([("x", "fbrica".replace("fb", "fáb"))]), "an accented letter passed"


def test_a112_every_language_exception_is_still_real():
    derived = set(_screen_headers())
    for key, owner in LANGUAGE_EXCEPTIONS.items():
        assert key in derived, f"stale language exception, gone from the source: {key}"
        assert owner.startswith("Inc-"), owner


@pytest.mark.xfail(strict=True, reason="RED: 'alternar radial' does not name 'mind map'")
def test_a112_a_label_that_names_a_view_uses_its_one_name():
    rows = [(view, b) for view in darkside.VIEW_NAMES for b in keymap.KEYMAP
            if b.action == f"toggle_{view}"]
    assert rows, "no seat row switches to a view: the rule judges nothing"
    wrong = [(b.key, b.label) for view, b in rows if darkside.VIEW_NAMES[view] not in b.label]
    assert wrong == [], wrong


@pytest.mark.xfail(strict=True, reason="RED: the home header says 'mapas vivos'")
async def test_a112_the_home_header_reads_its_one_name(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = app.screen
        row = "".join(_rows_in(screen, screen.query_one("#home-identity").region))
    assert darkside.VIEW_NAMES["home"] in row.split(), row


@pytest.mark.xfail(strict=True, reason="Inc-9b: the map views' own headers are outside Inc-9's cap")
def test_inc9b_each_map_view_header_names_its_view():
    from mapper.views import layered, outline, radial

    headers = {
        "canvas": layered._header_line(Graph(), 118, False, 0, 0).plain,  # noqa: SLF001
        "outline": outline._header_line().plain,  # noqa: SLF001
        "radial": radial._header_line(0).plain,  # noqa: SLF001
    }
    wrong = {k: h for k, h in headers.items() if f"· {darkside.VIEW_NAMES[k]}" not in h}
    assert wrong == {}, wrong


# ---------------------------------------------------------------------------
# C-D25a / C-D25b -- Inc-9's own seat diff against the batch state it entered

ENTRY_SHA = "6fe35f5"
#: The rows Inc-9 declares: `#D9`'s migration of the two last help screens.
DECLARED_ADDED = frozenset({
    ("factory", "j", "next_sibling"), ("factory", "k", "prev_sibling"),
    ("factory", "h", "parent"), ("factory", "l", "child"),
    ("factory", "0", "start_node"), ("factory", "d", "edit_doc"),
    ("factory", "i", "import_office"), ("factory", "g", "generate_office"),
    ("factory", "q", "home"), ("factory", "escape", "home"),
    ("settings", "q", "home"), ("settings", "escape", "home"),
})
#: Group headers renamed to English (`A-112` st. 2); no key changes scope.
DECLARED_REGROUPED = frozenset({("lista", "list"), ("salir", "leave")})


def _entry_seat():
    source = subprocess.run(
        ["git", "show", f"{ENTRY_SHA}:mapper/keymap.py"], cwd=ROOT, check=True,
        capture_output=True, text=True, encoding="utf-8").stdout
    module = types.ModuleType("keymap_at_entry")
    sys.modules[module.__name__] = module
    try:
        exec(compile(source, "keymap_at_entry", "exec"), module.__dict__)  # noqa: S102
    finally:
        sys.modules.pop(module.__name__)
    return module


def _projection(seat) -> set[tuple]:
    return {(b.scope, b.key, b.action, b.glyph, b.priority) for b in seat}


@pytest.mark.xfail(strict=True, reason="RED until Inc-9 adds its rows and regroups")
def test_cd25a_the_seat_diff_is_exactly_what_inc9_declares():
    entry = _entry_seat()
    before, after = _projection(entry.KEYMAP), _projection(keymap.KEYMAP)
    assert before - after == set(), f"a row was lost or rebound: {sorted(before - after)}"
    assert {row[:3] for row in after - before} == DECLARED_ADDED
    old = {(b.scope, b.key): b.group for b in entry.KEYMAP}
    moved = {(old[(b.scope, b.key)], b.group) for b in keymap.KEYMAP
             if (b.scope, b.key) in old and old[(b.scope, b.key)] != b.group}
    assert moved == DECLARED_REGROUPED, moved


def test_cd25b_no_chord_collides_on_entry_or_on_exit():
    entry = _entry_seat()
    assert entry.duplicate_chords() == []
    assert keymap.duplicate_chords() == []
