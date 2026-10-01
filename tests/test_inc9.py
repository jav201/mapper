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

def test_llr_n16_1_2_every_help_screen_declares_a_scope():
    declared = set(keymap.GROUP_SCOPE.values())
    undeclared = sorted(name for name, cls in HELP_SCREENS.items()
                        if getattr(cls, "KEY_SCOPE", None) not in declared)
    assert undeclared == [], f"help screens with no declared seat scope: {undeclared}"
    thin = {name: len(bindings_for(cls.KEY_SCOPE)) for name, cls in HELP_SCREENS.items()
            if len(bindings_for(cls.KEY_SCOPE)) < 3}
    assert thin == {}, f"a declared scope the seat leaves (nearly) empty: {thin}"


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


@pytest.mark.parametrize("name", sorted(HELP_SCREENS))
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


def test_b18_no_product_site_constructs_an_unscoped_legend():
    sites = _help_constructions()
    assert sites, "the AST walk found no HelpScreen construction: the probe is broken"
    unscoped = [(p, line) for p, line, call in sites
                if not call.args and not any(k.arg == "scope" for k in call.keywords)]
    assert unscoped == [], unscoped


# ---------------------------------------------------------------------------
# C-D9a -- the `tab` drop on SettingsScreen, gated on a WORKING positive control

async def _tab_walk(tmp_path, cls) -> tuple[list[int], int]:
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
    return walk, len(chain)


async def test_cd9a_the_probe_sees_transitions_and_the_drop_restores_traversal(tmp_path):
    """`C-D9a`, measured rather than assumed.  The PDR's probe saw `None` x 9
    and could not fail (`A-112` st. 8).  This one walks the sheet's own focus
    chain: on the shipped screen nine presses make eight transitions, each to
    the next member -- the POSITIVE control, proof the probe sees a move.  The
    pre-drop bindings, re-declared on a subclass, leave focus where it is: they
    did not re-declare traversal, they stopped it (`LLR-N06.5`'s measurement,
    reproduced).  So the drop is not neutral; it is a repair, and it ships."""
    from mapper.screens.settings import SettingsScreen

    class WithScreenTab(SettingsScreen):
        """The pre-drop `tab`/`shift+tab` bindings, verbatim."""
        BINDINGS = [Binding("tab", "focus_next", "Siguiente", priority=True),
                    Binding("shift+tab", "focus_previous", "Anterior", priority=True)]

    shipped, ring = await _tab_walk(tmp_path / "shipped", SettingsScreen)
    pre_drop, _ = await _tab_walk(tmp_path / "pre_drop", WithScreenTab)
    assert -1 not in shipped, shipped
    assert sum(a != b for a, b in zip(shipped, shipped[1:])) == 8, shipped
    # `INC9-CR-F6`: the ORDER, not just the count -- eight jumps to arbitrary
    # stops would satisfy the count; traversal is each press to the NEXT member.
    assert ring >= 2 and all(b == (a + 1) % ring for a, b in zip(shipped, shipped[1:])), (
        shipped, ring)
    assert len(set(pre_drop)) == 1, f"the pre-drop bindings moved focus after all: {pre_drop}"
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


def _message_arg(call: ast.Call):
    """The message expression of a `notify` call: positional, or `message=`
    (`INC9-CR-F4`: the census read `args[0]` only, so `notify(message=f"...")`
    was invisible to it)."""
    if call.args:
        return call.args[0]
    return next((k.value for k in call.keywords if k.arg == "message"), None)


def _coerced(arg) -> bool:
    """`A-112` st. 7: the whole message through `plain()`, or every
    interpolated value through it.  No third shape."""
    if _is_plain(arg):
        return True
    if isinstance(arg, ast.JoinedStr):
        return all(_is_plain(v.value) for v in arg.values if isinstance(v, ast.FormattedValue))
    return False


def test_llr_n06_2_5_notify_sites_are_coerced():
    sites = _notify_sites()
    assert len(sites) > 0, "the AST walk found no notify call: the census is vacuous"
    dynamic = [(p, n, c) for p, n, c in sites
               if _message_arg(c) is not None and not isinstance(_message_arg(c), ast.Constant)]
    assert dynamic, "no dynamic site: nothing below is judged"
    markup_on = [(p, n) for p, n, c in dynamic
                 if not any(k.arg == "markup" and isinstance(k.value, ast.Constant)
                            and k.value.value is False for k in c.keywords)]
    assert markup_on == [], f"dynamic notify sites parsing markup: {markup_on}"
    uncoerced = [(p, n) for p, n, c in dynamic if not _coerced(_message_arg(c))]
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


def test_llr_n06_2_5_the_census_reads_a_message_keyword():
    """`INC9-CR-F4`: a site that passes its message by keyword is judged like any
    other.  The mutant this arm kills is `notify(message=f"...")` in product code."""
    def call(src):
        return ast.parse(src, mode="eval").body
    positional = call("self.notify(darkside.plain(f'x {e}'), markup=False)")
    keyword = call("self.notify(message=f'x {e}', markup=False)")
    assert _message_arg(positional) is positional.args[0]
    assert _message_arg(keyword) is keyword.keywords[0].value
    assert not _coerced(_message_arg(keyword)), "a keyword message slipped the predicate"
    assert _message_arg(call("self.notify(severity='error')")) is None


# ---------------------------------------------------------------------------
# A-112 -- English chrome: the language census

#: The declared English vocabulary of the chrome (`A-112`).  Adding a word is
#: a deliberate edit in the commit that paints it.
CHROME_LEXICON = frozenset("""
    add all app archive attachment back bottom branch browse build card child choose
    close command component components connect coverage csv default details diff disabled
    document documents doors down edit exit export factory file focus focused fold from
    generate global go help hide home import incomplete keys last leave legend list map
    maps match mind missing move nav new next node office open outline page palette pan
    parent plug previous quit rail remove repo report repository resume right left run
    save scroll search settings show sibling start svg template to toggle top tree undo
    unfold up view
""".split())

#: Screen headers allowed to stay non-English, owned by the increment that
#: closes each.  Empty since Inc-9b closed the last two (`A-112` "Split"); the
#: stale guard below reddens when an entry outlives its source.
LANGUAGE_EXCEPTIONS: dict[tuple[str, str], str] = {}


def _seat_strings() -> list[tuple[str, str]]:
    out = [("mapper/keymap.py", b.label) for b in keymap.KEYMAP]
    out += [("mapper/keymap.py", group) for group in keymap.GROUP_SCOPE]
    # Inc-9c (`K1`): what is PAINTED is the header, and two groups may share one.
    out += [("mapper/keymap.py", header) for header in keymap.GROUP_HEADER.values()]
    return out


def _keybar_literals() -> list[tuple[str, str]]:
    """Group headers and labels of every hand-written `KeyBar([...])` literal,
    and the keybar's own truncation word (`A-112` st. 3)."""
    out = [("mapper/darkside.py", darkside.KEYBAR_MORE)]
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
    # `Inc-9e` (`L1`): the strip's labels ARE the seat's -- `tab_strip` carries no
    # literal -- so they are derived from the doors it names, not parsed out of a
    # literal list that no longer exists.
    tabs = [("mapper/darkside.py", keymap.label_for(keymap.SCOPE_HOME, action))
            for action in darkside._TAB_ACTIONS]
    assert tabs, "no tab label derived from darkside.tab_strip"
    out = list(tabs)
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
    assert len(out) > len(tabs), "no crumb or title derived from any Screen subclass"
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


def test_a112_a_label_that_names_a_view_uses_its_one_name():
    rows = [(view, b) for view in darkside.VIEW_NAMES for b in keymap.KEYMAP
            if b.action == f"toggle_{view}"]
    assert rows, "no seat row switches to a view: the rule judges nothing"
    wrong = [(b.key, b.label) for view, b in rows if darkside.VIEW_NAMES[view] not in b.label]
    assert wrong == [], wrong


async def test_a112_the_home_header_reads_its_one_name(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = app.screen
        row = "".join(_rows_in(screen, screen.query_one("#home-identity").region))
    assert darkside.VIEW_NAMES["home"] in row.split(), row
    # `INC9-CR-F8`: and the name it replaced is not painted beside it.
    assert "mapas vivos" not in row, row


def _map_view_first_lines() -> list[tuple[str, str, str]]:
    """`(view, which line, its first painted row)` for every map-view header
    and every `_degraded` banner, legacy and concept atlas both (`INC9-CR-F1`)."""
    from mapper.views import layered, outline, radial

    def first(text) -> str:
        return text.plain.split("\n")[0]

    g = Graph()
    rows = [
        ("canvas", "header", first(layered._header_line(g, 118, False, 0, 0))),  # noqa: SLF001
        ("canvas", "header legacy", first(layered._header_line(g, 118, True, 0, 0))),  # noqa: SLF001
        ("canvas", "degraded", first(layered._degraded(9, False))),  # noqa: SLF001
        ("canvas", "degraded legacy", first(layered._degraded(9, True))),  # noqa: SLF001
        ("radial", "header", first(radial._header_line(0))),  # noqa: SLF001
        ("radial", "degraded", first(radial._degraded(9))),  # noqa: SLF001
        ("outline", "header", first(outline._header_line())),  # noqa: SLF001
        ("outline", "degraded", first(outline._degraded(9))),  # noqa: SLF001
    ]
    assert {v for v, _, _ in rows} == set(darkside.VIEW_NAMES) - {"home"}, rows
    return rows


def test_inc9b_each_map_view_header_names_its_view():
    wrong = {(v, w): t for v, w, t in _map_view_first_lines()
             if f"· {darkside.VIEW_NAMES[v]}" not in t}
    assert wrong == {}, wrong


def test_inc9b_each_map_view_header_reads_view_names_not_a_literal(monkeypatch):
    """The name must be READ: swap every entry for a sentinel and each header
    and banner follows it.  A header that spells its name fails here even when
    the spelling happens to equal the ratified word."""
    for view in darkside.VIEW_NAMES:
        monkeypatch.setitem(darkside.VIEW_NAMES, view, f"zz-{view}-zz")
    wrong = {(v, w): t for v, w, t in _map_view_first_lines()
             if f"· zz-{v}-zz" not in t}
    assert wrong == {}, wrong


def test_inc9b_the_atlas_states_its_map_kind_in_english_as_secondary_text():
    from mapper.views import layered

    g = Graph()
    for legacy, kind in ((False, "concept map"), (True, "legacy tree")):
        for line in (layered._header_line(g, 118, legacy, 0, 0).plain,  # noqa: SLF001
                     layered._degraded(9, legacy).plain.split("\n")[0]):  # noqa: SLF001
            assert f"· {darkside.VIEW_NAMES['canvas']} · {kind}" in line, line


async def test_inc9b_the_coverage_and_editor_titles_are_english_and_state_free():
    from textual.app import App

    from mapper.model import Ficha, Node, SchemaField
    from mapper.screens.coverage import CoverageScreen
    from mapper.screens.editor import EditorScreen

    schema = [SchemaField(key="D", label="documento", required=True)]
    incomplete = Graph(schema=schema)
    incomplete.add_node(Node(id="root", ficha=Ficha(title="Root")))
    complete = Graph(schema=schema)
    complete.add_node(Node(id="root", ficha=Ficha(title="Root", fields={"D": "r"})))
    titles: dict[str, str] = {}
    app = App()
    async with app.run_test(size=SIZE) as pilot:
        for name, graph in (("coverage, incomplete map", incomplete),
                            ("coverage, complete map", complete)):
            await app.push_screen(CoverageScreen(graph, "demo"))
            await pilot.pause()
            assert app.screen.complete is (graph is complete), name
            titles[name] = app.screen.query_one("#coverage-title").content
            await app.pop_screen()
        await app.push_screen(EditorScreen("x"))
        await pilot.pause()
        titles["editor"] = app.screen.query_one("#editor-title").content
    assert _judge([("screen", t) for t in titles.values()]) == [], titles
    cov = {titles["coverage, incomplete map"], titles["coverage, complete map"]}
    assert len(cov) == 1, f"the coverage title changes with the state it reports: {cov}"
    assert "incomplete" not in next(iter(cov)), cov


# ---------------------------------------------------------------------------
# C-D25a / C-D25b -- Inc-9's own seat diff against the batch state it entered

ENTRY_SHA = "6fe35f5"
#: The seat as it stood at `ENTRY_SHA`, pinned as a LITERAL:
#: `(scope, key, action, glyph, priority, group)`.  It was read with `git show`,
#: which ERRORs on a shallow clone (`INC9-CR-F2`); a literal cannot, and -- like
#: `EXPECTED_SEAT` -- it is the specification precisely because it is not derived
#: from the thing it checks.  Generated from `git show 6fe35f5:mapper/keymap.py`
#: when it was pinned.
ENTRY_ROWS = (
    ('app', 'ctrl+p', 'palette', 'ctrl+p', False, 'app'),
    ('app', 'question_mark', 'help', '?', False, 'app'),
    ('help', 'down', 'legend_down', '↓', False, 'help'),
    ('help', 'end', 'legend_end', 'end', False, 'help'),
    ('help', 'escape', 'dismiss_none', 'esc', False, 'help'),
    ('help', 'home', 'legend_home', 'home', False, 'help'),
    ('help', 'pagedown', 'legend_page_down', 'pagedown', False, 'help'),
    ('help', 'pageup', 'legend_page_up', 'pageup', False, 'help'),
    ('help', 'q', 'dismiss_none', 'q', False, 'help'),
    ('help', 'up', 'legend_up', '↑', False, 'help'),
    ('home', 'c', 'consult', 'c', False, 'doors'),
    ('home', 'f', 'factory', 'f', False, 'doors'),
    ('home', 'i', 'import_csv', 'i', False, 'doors'),
    ('home', 'j', 'table_down', 'j', False, 'lista'),
    ('home', 'k', 'table_up', 'k', False, 'lista'),
    ('home', 'n', 'construct', 'n', False, 'doors'),
    ('home', 'p', 'plug', 'p', False, 'doors'),
    ('home', 'q', 'quit', 'q', False, 'lista'),
    ('home', 'r', 'resume', 'r', False, 'doors'),
    ('home', 's', 'settings', 's', False, 'doors'),
    ('home', 't', 'template', 't', False, 'doors'),
    ('import', 'escape', 'home', 'esc', False, 'import'),
    ('import', 's', 'save', 's', False, 'import'),
    ('map', 'A', 'add_attachment', 'A', False, 'node'),
    ('map', 'H', 'pan_left', 'H', False, 'view'),
    ('map', 'I', 'toggle_inspector', 'I', False, 'view'),
    ('map', 'J', 'pan_down', 'J', False, 'view'),
    ('map', 'K', 'pan_up', 'K', False, 'view'),
    ('map', 'L', 'pan_right', 'L', False, 'view'),
    ('map', 'M', 'next_gap', 'M', False, 'view'),
    ('map', 'N', 'prev_hit', 'N', False, 'nav'),
    ('map', 'R', 'toggle_rail', 'R', False, 'view'),
    ('map', 'X', 'remove_attachment', 'X', False, 'node'),
    ('map', 'a', 'add_child', 'a', False, 'node'),
    ('map', 'd', 'open_documents', 'd', False, 'node'),
    ('map', 'e', 'export_svg', 'e', False, 'view'),
    ('map', 'enter', 'open_ficha', '↵', False, 'nav'),
    ('map', 'equals_sign', 'toggle_diff', '=', False, 'view'),
    ('map', 'escape', 'back_or_home', 'esc', False, 'salir'),
    ('map', 'f', 'toggle_focus', 'f', False, 'view'),
    ('map', 'g', 'focus_rail', 'g', False, 'view'),
    ('map', 'h', 'parent', 'h', False, 'nav'),
    ('map', 'j', 'next_sibling', 'j', False, 'nav'),
    ('map', 'k', 'prev_sibling', 'k', False, 'nav'),
    ('map', 'l', 'child', 'l', False, 'nav'),
    ('map', 'm', 'coverage', 'm', False, 'view'),
    ('map', 'n', 'next_hit', 'n', False, 'nav'),
    ('map', 'o', 'toggle_outline', 'o', False, 'view'),
    ('map', 'q', 'home', 'q', False, 'salir'),
    ('map', 'r', 'toggle_radial', 'r', False, 'view'),
    ('map', 'slash', 'search', '/', False, 'nav'),
    ('map', 'u', 'undo', 'u', False, 'node'),
    ('map', 'x', 'archive', 'x', False, 'node'),
    ('map', 'z', 'collapse_branch', 'z', False, 'view'),
    ('palette', 'enter', 'run_selected', '↵', False, 'palette'),
    ('palette', 'escape', 'dismiss_none', 'esc', False, 'palette'),
    ('plug', 'escape', 'home', 'esc', True, 'plug'),
    ('repo', 'j', 'next_sibling', 'j', True, 'repo'),
    ('repo', 'k', 'prev_sibling', 'k', True, 'repo'),
    ('repo', 'q', 'home', 'q', True, 'repo'),
)
#: The rows the seat gained since `ENTRY_SHA`: Inc-9's `#D9` migration of the two
#: last help screens, and Inc-9c's `home enter` (`INC9-UX-F11`).
DECLARED_ADDED = frozenset({
    ("home", "enter", "open_selected"),
    ("factory", "j", "next_sibling"), ("factory", "k", "prev_sibling"),
    ("factory", "h", "parent"), ("factory", "l", "child"),
    ("factory", "0", "start_node"), ("factory", "d", "edit_doc"),
    ("factory", "i", "import_office"), ("factory", "g", "generate_office"),
    ("factory", "q", "home"), ("factory", "escape", "home"),
    ("settings", "q", "home"), ("settings", "escape", "home"),
})
#: Group headers renamed to English (`A-112` st. 2); no key changes scope.
DECLARED_REGROUPED = frozenset({("lista", "list"), ("lista", "exit"), ("salir", "leave")})


def _entry_projection() -> set[tuple]:
    return {row[:5] for row in ENTRY_ROWS}


def _projection(seat) -> set[tuple]:
    return {(b.scope, b.key, b.action, b.glyph, b.priority) for b in seat}


def _entry_duplicate_chords() -> list[tuple[str, str]]:
    """`keymap.duplicate_chords()`'s rule, applied to the pinned entry rows."""
    pairs = [(row[0], row[1]) for row in ENTRY_ROWS]
    clashes = {p for p in pairs if pairs.count(p) > 1}
    app_keys = {key for scope, key in pairs if scope == "app"}
    clashes |= {(scope, key) for scope, key in pairs if scope != "app" and key in app_keys}
    return sorted(clashes)


def test_cd25_the_pinned_entry_seat_is_not_vacuous():
    assert len(ENTRY_ROWS) == 60, len(ENTRY_ROWS)
    assert len({row[:2] for row in ENTRY_ROWS}) == 60, "two entry rows share a (scope, key)"


def test_cd25a_the_seat_diff_is_exactly_what_inc9_declares():
    before, after = _entry_projection(), _projection(keymap.KEYMAP)
    assert before - after == set(), f"a row was lost or rebound: {sorted(before - after)}"
    assert {row[:3] for row in after - before} == DECLARED_ADDED
    old = {(row[0], row[1]): row[5] for row in ENTRY_ROWS}
    moved = {(old[(b.scope, b.key)], b.group) for b in keymap.KEYMAP
             if (b.scope, b.key) in old and old[(b.scope, b.key)] != b.group}
    assert moved == DECLARED_REGROUPED, moved


@pytest.mark.parametrize("scope", sorted(set(keymap.GROUP_SCOPE.values()) - {keymap.SCOPE_APP}
                                           - set(keymap.MODAL_SCOPES)))
def test_inc9_f6_the_app_group_closes_every_generated_key_bar(scope):
    """`INC9-F6`: the renders showed the factory and settings bars LEADING
    with `app`, because their groups were declared after it."""
    from mapper.app import keybar_groups

    groups = keybar_groups(scope)
    assert groups[-1] == "app" and groups.count("app") == 1, groups


def test_cd25b_no_chord_collides_on_entry_or_on_exit():
    assert _entry_duplicate_chords() == []
    assert keymap.duplicate_chords() == []
