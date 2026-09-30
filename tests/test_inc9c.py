"""Inc-9c -- the operator's answers K1-K4 and the defects the Inc-9 reviews found.

Authority: `.dev-flow/2026-08-26-ui-next-batch-02/VERDICT-inc9-2026-09-30.md`.

Every arm here was committed RED first, as a STRICT xfail keyed by the step that
closes it (`OPEN_STEPS`); each implementation commit deletes its own step from
that set, and an arm that then fails is a failure, not an xfail.  The expected
WORDS are the operator's ruling (a literal table is the specification here, as
`EXPECTED_SEAT` is for the seat); everything else is derived at run time from the
seat, the screens' own widgets and the AST, and each derivation asserts itself
non-empty before any member is judged.

No user-profile path is ever typed literally: `PROFILE` is the declared
`<operator>` placeholder (`tests/test_no_operator_paths.py`, `A-110`).
"""
from __future__ import annotations

import ast
import pathlib

import pytest
from textual.containers import VerticalScroll
from textual.widgets import DataTable, Input, Static

from mapper import darkside, keymap
from mapper.app import (
    HomeScreen,
    MapperApp,
    MapScreen,
    PlugRepoScreen,
    RepoScreen,
    _ConfirmScreen,
    _ImportPreviewScreen,
    _PromptScreen,
    keybar_groups,
)
from mapper.model import Document, Ficha, Graph, Node
from mapper.screens.factory import FactoryScreen
from mapper.screens.help import HelpScreen
from mapper.screens.settings import SettingsScreen
from mapper.store import MapStore
from mapper.widgets.chrome import HintLine, KeyBar, TabStrip
from tests.test_inc9 import HELP_SCREENS, OPENERS, _product_sources
from tests.test_no_operator_paths import USER_PROFILE_PATH
from tests.test_repair_layout import _frame_rows, _rows_in, _tree

#: Steps not yet implemented.  An arm keyed to a step in this set is a strict xfail.
OPEN_STEPS: set[str] = set()


def red(step: str):
    if step not in OPEN_STEPS:
        return lambda fn: fn
    return pytest.mark.xfail(
        strict=True, reason=f"Inc-9c: committed RED; closed by the '{step}' step")


#: The declared redaction placeholder, never a real account (`A-110`).
PROFILE = r"C:\Users\<operator>\x"
SIZES = [(118, 34), (87, 34), (140, 45)]
SIZE = SIZES[0]


def _text(widget: Static) -> str:
    content = widget.content
    return getattr(content, "plain", str(content))


def _boom(*_a, **_k):
    raise OSError(f"[Errno 13] Permission denied: '{PROFILE}'")


# ---------------------------------------------------------------------------
# INC9-SEC-F1 -- no toast paints an absolute path or a user-profile path

def _office_fixture(app, tmp_path) -> FactoryScreen:
    template = tmp_path / "plantilla.docx"
    template.write_bytes(b"x")
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="proceso")))
    g.documents["plantilla"] = Document(
        name="plantilla", path=str(template), kind="docx", template=True)
    return FactoryScreen(g, process_name="demo")


async def _drive_create_seed(app, pilot, mp, tmp_path):
    mp.setattr(MapStore, "create_seed", _boom)
    await pilot.press("n")
    await pilot.pause()
    app.screen.query_one("#construct-input", Input).value = "mapa"
    await pilot.press("enter")


async def _drive_create_from_template(app, pilot, mp, tmp_path):
    mp.setattr(MapStore, "create_from_template", _boom)
    await pilot.press("t")
    await pilot.pause()
    await pilot.press("enter")
    await pilot.pause()
    app.screen.query_one("#prompt-input", Input).value = "mapa"
    await pilot.press("enter")


async def _drive_csv_not_found(app, pilot, mp, tmp_path):
    await pilot.press("i")
    await pilot.pause()
    app.screen.query_one("#prompt-input", Input).value = PROFILE + r"\nodos.csv"
    await pilot.press("enter")


async def _drive_csv_unreadable(app, pilot, mp, tmp_path):
    csv = tmp_path / "nodos.csv"
    csv.write_text("a,b\n", encoding="utf-8")
    mp.setattr("mapper.app.preview_csv", _boom)
    await pilot.press("i")
    await pilot.pause()
    app.screen.query_one("#prompt-input", Input).value = str(csv)
    await pilot.press("enter")


async def _drive_export_too_large(app, pilot, mp, tmp_path):
    from mapper.export import ExportTooLarge

    def refuse(self, size):
        raise ExportTooLarge(10, 5)

    screen = app.screen
    (screen.store.workspace / f"{screen.map_id}.svg").write_text("<svg/>", encoding="utf-8")
    mp.setattr(MapScreen, "_export_view_state", refuse)
    await pilot.press("e")


async def _drive_export_failed(app, pilot, mp, tmp_path):
    mp.setattr("mapper.app.save_svg", _boom)
    await pilot.press("e")


async def _drive_export_ok(app, pilot, mp, tmp_path):
    await pilot.press("e")


async def _drive_generate_ok(app, pilot, mp, tmp_path):
    mp.setattr("mapper.screens.factory.office.resolve", lambda *a, **k: None)
    await pilot.press("g")


async def _drive_generate_failed(app, pilot, mp, tmp_path):
    mp.setattr("mapper.screens.factory.office.resolve", _boom)
    await pilot.press("g")


async def _drive_repo_unexpected(app, pilot, mp, tmp_path):
    return None


#: site -> (how it opens, driver, what a useful toast still names)
SITES = {
    "create-map": ("home", _drive_create_seed, ["mapa", "OSError"]),
    "create-from-template": ("home", _drive_create_from_template, ["mapa", "OSError"]),
    "csv-not-found": ("home", _drive_csv_not_found, ["nodos.csv"]),
    "csv-unreadable": ("home", _drive_csv_unreadable, ["nodos.csv", "OSError"]),
    "export-too-large": ("map", _drive_export_too_large, [".svg"]),
    "export-failed": ("map", _drive_export_failed, ["OSError"]),
    "export-ok": ("map", _drive_export_ok, [".svg"]),
    "generate-ok": ("factory", _drive_generate_ok, [".docx"]),
    "generate-failed": ("factory", _drive_generate_failed, ["OSError"]),
    "repo-unexpected": ("repo", _drive_repo_unexpected, ["OSError"]),
}


@red("toasts")
@pytest.mark.parametrize("site", sorted(SITES))
async def test_inc9c_sec_f1_no_toast_paints_an_absolute_path(tmp_path, monkeypatch, site):
    """Every toast site, driven with a failure whose message carries a user-profile
    path (`PROFILE`, the placeholder).  What reaches the operator's eye -- a notify
    or the map's event strip -- names the map / file relatively and the exception
    TYPE, and contains neither the profile path nor the workspace's absolute path.
    Same fix as `_save_or_toast` (`G6-C-F2`, `B-30`).  A positive control per site:
    the toast exists and still names what failed."""
    opens, driver, names = SITES[site]
    if site == "repo-unexpected":
        # `@work(thread=True)` exits the app on a worker failure, so the
        # `except Exception` around `wait()` is reached only by a failure of the
        # wait itself; a stub worker whose `wait()` raises drives exactly that.
        class _Failing:
            async def wait(self):
                raise OSError(f"[Errno 2] No such file: '{PROFILE}'")

        monkeypatch.setattr(RepoScreen, "fetch_graph", lambda self: _Failing())
    app = MapperApp(tmp_path)
    toasts: list[str] = []
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        app.notify = lambda msg, **kw: toasts.append(str(msg))
        if opens == "map":
            app.push_screen(MapScreen(_tree(app)))
        elif opens == "factory":
            app.push_screen(_office_fixture(app, tmp_path))
        elif opens == "repo":
            app.push_screen(RepoScreen("owner/name"))
        else:
            _tree(app)
        for _ in range(3):
            await pilot.pause()
        await driver(app, pilot, monkeypatch, tmp_path)
        for _ in range(4):
            await pilot.pause()
        if opens == "map":
            strip = _text(app.screen.query_one("#map-toast", Static))
            if strip.strip():
                toasts.append(strip)
        workspace = str(app.store.workspace)
    assert toasts, f"{site}: the site fired no toast -- the driver proves nothing"
    joined = "\n".join(toasts)
    assert USER_PROFILE_PATH.search(joined) is None, (site, toasts)
    assert "<operator>" not in joined and PROFILE not in joined, (site, toasts)
    assert workspace not in joined and str(tmp_path) not in joined, (site, toasts)
    for name in names:
        assert name in joined, f"{site}: the toast no longer names {name!r}: {toasts}"


def _message_arg(call: ast.Call):
    """The message expression of a `notify` call, positional or `message=`."""
    if call.args:
        return call.args[0]
    return next((k.value for k in call.keywords if k.arg == "message"), None)


_RAW_EXCEPTION_NAMES = frozenset({"e", "exc", "err", "error"})
_PATH_NAMES = frozenset({"path", "target", "source", "filepath"})


def _unwrap_plain(node):
    while (isinstance(node, ast.Call)
           and ((isinstance(node.func, ast.Attribute) and node.func.attr == "plain")
                or (isinstance(node.func, ast.Name) and node.func.id == "plain"))
           and len(node.args) == 1):
        node = node.args[0]
    return node


def _leaky(expr) -> bool:
    """A value that can carry an absolute path into a toast: a raw exception, its
    `str()`, or a bare path-named variable.  `type(e).__name__`, names, file
    `.name`s and numbers are fine."""
    expr = _unwrap_plain(expr)
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) and expr.func.id == "str" \
            and len(expr.args) == 1:
        expr = expr.args[0]
    if isinstance(expr, ast.Name):
        return expr.id in _RAW_EXCEPTION_NAMES or expr.id in _PATH_NAMES
    if isinstance(expr, ast.Attribute):
        return expr.attr == "workspace"
    return False


def _leaky_interpolations(message) -> list[str]:
    """Every interpolated / wrapped value in a notify message that `_leaky` flags."""
    message = _unwrap_plain(message)
    out: list[str] = []
    if isinstance(message, ast.JoinedStr):
        for part in message.values:
            if isinstance(part, ast.FormattedValue) and _leaky(part.value):
                out.append(ast.unparse(_unwrap_plain(part.value)))
    elif _leaky(message):
        out.append(ast.unparse(message))
    return out


#: Declared carries, keyed by (file, the flagged expression).  Each is a value
#: that is NOT a bare operator path, with the reason it stays.  A stale entry --
#: one the source no longer produces -- fails `test_..._every_exception_is_real`.
LEAK_EXCEPTIONS: dict[tuple[str, str], str] = {
    ("mapper/app.py", "str(exc)"): "INC9C-F3: `GitHubError`'s own message (git stderr) "
                                  "and `store.load`'s path-free `MapStoreError` text",
    ("mapper/app.py", "str(e)"): "`store.load`'s `MapStoreError`, written path-free at B-30",
    ("mapper/screens/factory.py", "source"): "INC9C-F4: echo of the path the operator "
                                            "typed at the prompt (factory.py is outside this "
                                            "increment's file budget beyond two sites)",
}


def _notify_leaks() -> tuple[list[tuple[str, int, str]], int]:
    leaks, dynamic = [], 0
    for path, source in _product_sources().items():
        for node in ast.walk(ast.parse(source)):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "notify"):
                continue
            message = _message_arg(node)
            if message is None or isinstance(message, ast.Constant):
                continue
            dynamic += 1
            for expr in _leaky_interpolations(message):
                leaks.append((path, node.lineno, expr))
    return leaks, dynamic


@red("toasts")
def test_inc9c_sec_f1_census_no_notify_interpolates_a_raw_exception_or_path():
    leaks, dynamic = _notify_leaks()
    assert dynamic > 10, "the census found (almost) no dynamic notify site: it is vacuous"
    undeclared = [(p, n, e) for p, n, e in leaks if (p, e) not in LEAK_EXCEPTIONS]
    assert undeclared == [], f"toasts that can paint an absolute path: {undeclared}"


def test_inc9c_sec_f1_every_leak_exception_is_still_real():
    leaks, _ = _notify_leaks()
    found = {(p, e) for p, _, e in leaks}
    stale = [key for key in LEAK_EXCEPTIONS if key not in found]
    assert stale == [], f"stale leak exceptions, gone from the source: {stale}"


def test_inc9c_sec_f1_the_leak_predicate_discriminates():
    def leaks(src):
        return _leaky_interpolations(ast.parse(src, mode="eval").body)
    assert leaks("darkside.plain(f'no se pudo: {e}')") == ["e"]
    assert leaks("f'generado: {target}'") == ["target"]
    assert leaks("darkside.plain(str(exc))") == ["str(exc)"]
    assert leaks("f'x {darkside.plain(str(e))}'") == ["str(e)"]
    assert leaks("f'x {self.store.workspace}'") == ["self.store.workspace"]
    assert leaks("darkside.plain(f'x {type(e).__name__}')") == []
    assert leaks("darkside.plain(f'x {target.name} {len(g)}')") == []
    assert _message_arg(ast.parse("n.notify(message=f'{e}')", mode="eval").body) is not None


# ---------------------------------------------------------------------------
# K1 -- the ux reviewer's wording table, all of it

#: (scope, action) -> the ruled label.
K1_LABELS = {
    ("home", "table_down"): "next map",
    ("home", "table_up"): "previous map",
    ("home", "settings"): "components",
    ("map", "toggle_focus"): "focus branch",
    ("map", "toggle_diff"): "show/hide diff",
    ("map", "collapse_branch"): "fold/unfold",
    ("map", "coverage"): "coverage report",
    ("map", "next_gap"): "next incomplete",
    ("repo", "next_sibling"): "next branch",
    ("repo", "prev_sibling"): "previous branch",
    ("repo", "home"): "back",
    ("factory", "start_node"): "back to start",
    ("app", "palette"): "palette",
}
#: group id -> the header painted in the key bar, the legend and the palette.
K1_HEADERS = {
    "doors": "open", "list": "maps", "exit": "exit", "nav": "move", "tree": "move",
    "app": "global", "plug": "connect repo", "settings": "components",
}


def _row(scope: str, action: str):
    rows = [b for b in keymap.KEYMAP if b.scope == scope and b.action == action]
    assert len(rows) == 1, (scope, action, rows)
    return rows[0]


@red("wording")
@pytest.mark.parametrize("scope_action", sorted(K1_LABELS))
def test_inc9c_k1_each_ruled_label_is_in_the_seat(scope_action):
    assert _row(*scope_action).label == K1_LABELS[scope_action]


@red("wording")
def test_inc9c_k1_group_headers_and_their_single_source():
    headers = {g: keymap.group_header(g) for g in keymap.GROUP_SCOPE}
    assert {g: h for g, h in headers.items() if g in K1_HEADERS} == K1_HEADERS
    assert all(headers.values()), headers
    # `q quit` is not a list action: it leaves the maps group for its own.
    assert _row("home", "quit").group == "exit"
    # Two scopes may share one painted word, never one scope two groups.
    for scope in set(keymap.GROUP_SCOPE.values()):
        painted = [headers[g] for g in keymap.GROUP_SCOPE if keymap.GROUP_SCOPE[g] == scope]
        assert len(painted) == len(set(painted)), (scope, painted)


@red("wording")
def test_inc9c_k1_the_keybar_overflow_and_the_legend_own_line():
    assert darkside.KEYBAR_MORE == "all keys"
    bar = darkside.keybar([("g", [(f"k{i}", f"label number {i}") for i in range(30)])], width=60)
    assert bar.plain.endswith("  ? all keys"), bar.plain
    hidden = bar.plain.rsplit("+", 1)[1].split()[0]
    assert hidden.isdigit() and int(hidden) > 0, bar.plain
    own = HelpScreen(keymap.SCOPE_HELP)._render_own_scope_keys().plain  # noqa: SLF001
    assert "home end top/bottom" in own and "ends" not in own, own


@red("wording")
async def test_inc9c_k1_home_door_list_reads_browse_and_build(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        text = app.screen._empty_text().plain  # noqa: SLF001
    assert "consult" not in text and "construct" not in text, text
    assert "browse" in text and "build" in text, text


# ---------------------------------------------------------------------------
# INC9-UX-F4 -- the home door list and the home key bar read the seat

@red("ux")
async def test_inc9c_ux_f4_home_reads_its_labels_from_the_seat(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, HomeScreen)
        bar = screen.query_one(KeyBar)
        door_text = screen._empty_text().plain  # noqa: SLF001
    assert bar.groups == keymap.groups_for_keybar(keybar_groups(keymap.SCOPE_HOME)), bar.groups
    doors = [b for b in keymap.bindings_for(keymap.SCOPE_HOME) if b.key in "cpntif"
             and b.group == "doors"]
    assert len(doors) == 6, doors
    for b in doors:
        assert f"{b.glyph} {b.label}" in door_text, (b.glyph, b.label, door_text)
    assert [g for g, _ in bar.groups][-1] == keymap.group_header("app")


# ---------------------------------------------------------------------------
# K2 -- `components`;  K4 -- `connect repo`

async def _tab_strip_active_tabs(app) -> list[str]:
    strip = app.screen.query_one(TabStrip)
    text = strip.content
    accent = f"on {darkside.ACCENT}"
    return [text.plain[s.start:s.end].strip() for s in text.spans if accent in str(s.style)]


@red("wording")
async def test_inc9c_k2_components_is_one_name_on_every_surface(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        door = _row("home", "settings").label
        app.push_screen(SettingsScreen())
        await pilot.pause()
        await pilot.pause()
        active = await _tab_strip_active_tabs(app)
        crumb_rows = _rows_in(app.screen, app.screen.query_one(TabStrip).region)
        app.set_focus(None)
        await pilot.press("question_mark")
        await pilot.pause()
        await pilot.pause()
        legend_title = _rows_in(app.screen, app.screen.query_one("#help-title").region)
        groups = [keymap.group_header(b.group) for b in keymap.bindings_for("settings")]
    assert door == "components"
    assert any("components" in r for r in crumb_rows), crumb_rows
    assert any("legend · components" in r for r in legend_title), legend_title
    assert "components" in groups, groups
    assert active == [], f"the tab strip marks {active} on the components screen"


@red("wording")
async def test_inc9c_k4_connect_repo_is_one_name_on_every_surface(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        app.push_screen(PlugRepoScreen())
        await pilot.pause()
        await pilot.pause()
        strip = _rows_in(app.screen, app.screen.query_one(TabStrip).region)
        title = _text(app.screen.query_one("#repo-title", Static))
        door = _row("home", "plug").label
        groups = [keymap.group_header(b.group) for b in keymap.bindings_for("plug")]
        app.set_focus(None)
        await pilot.press("question_mark")
        await pilot.pause()
        await pilot.pause()
        legend_title = _rows_in(app.screen, app.screen.query_one("#help-title").region)
    joined = " ".join(strip)
    assert "p connect repo" in joined, strip
    assert strip[1].count("connect repo") == 1 and "connect repo" in strip[1], strip
    assert title == "connect repo" and door == "connect repo"
    assert "connect repo" in groups, groups
    assert any("legend · connect repo" in r for r in legend_title), legend_title


@red("wording")
def test_inc9c_k4_import_and_repo_keep_their_names():
    assert keymap.group_header("import") == "import"
    assert keymap.group_header("repo") == "repo"


# ---------------------------------------------------------------------------
# K3 -- key hints in English, each key with its seat label's word

def _seat_pair(scope: str, action: str, key: str | None = None) -> str:
    rows = [b for b in keymap.KEYMAP if b.scope == scope and b.action == action
            and (key is None or b.key == key)]
    assert len(rows) == 1, (scope, action, key, rows)
    return f"{rows[0].glyph} {rows[0].label}"


@red("hints")
async def test_inc9c_k3_modal_footers_and_the_repo_panel_are_english(tmp_path, monkeypatch):
    monkeypatch.setattr("mapper.app.GitHubConnector.fetch", lambda self, progress=None: Graph())
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        app.push_screen(_PromptScreen("nombre", "x"))
        await pilot.pause()
        prompt = _text(app.screen.query_one("#prompt-hints", Static))
        app.pop_screen()
        app.push_screen(_ConfirmScreen("seguro"))
        await pilot.pause()
        confirm = _text(app.screen.query_one("#confirm-hints", Static))
        app.pop_screen()
        app.push_screen(RepoScreen("owner/name"))
        await pilot.pause()
        panel = _text(app.screen.query_one("#repo-sidebar-hints", Static))
    assert prompt == "↵ confirm   esc cancel", prompt
    assert confirm == "y yes   n no", confirm
    assert panel.split("\n") == [
        _seat_pair("repo", "next_sibling"),
        _seat_pair("repo", "prev_sibling"),
        _seat_pair("repo", "home"),
        _seat_pair("app", "help"),
    ], panel


@red("hints")
async def test_inc9c_k3_the_construct_modal_footer_is_english(tmp_path):
    from mapper.app import ConstructScreen

    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        app.push_screen(ConstructScreen())
        await pilot.pause()
        hints = _text(app.screen.query_one("#construct-hints", Static))
    assert hints == "↵ create   esc cancel", hints


@red("hints")
async def test_inc9c_k3_the_factory_import_and_map_hints_use_the_seat_word(tmp_path):
    from mapper.app import DEFAULT_MAP_HINT

    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        factory = FactoryScreen(app.store.load(_tree(app)))
        app.push_screen(factory)
        await pilot.pause()
        factory_hint = _text(factory.query_one(HintLine))
        app.pop_screen()
        imp = _ImportPreviewScreen(app.store.load(_tree(app)), pathlib.Path("nodos.csv"))
        app.push_screen(imp)
        await pilot.pause()
        import_hint = _text(imp.query_one(HintLine))
    for action in ("edit_doc", "import_office", "generate_office", "start_node"):
        assert _seat_pair("factory", action) in factory_hint, (action, factory_hint)
    assert _seat_pair("factory", "home", key="q") in factory_hint, factory_hint
    assert "salir" not in factory_hint and "inicio" not in factory_hint, factory_hint
    assert _seat_pair("import", "save") in import_hint and _seat_pair("import", "home") in import_hint
    assert "guarda" not in import_hint and "volver" not in import_hint, import_hint
    assert _seat_pair("map", "open_ficha") in DEFAULT_MAP_HINT, DEFAULT_MAP_HINT
    assert _seat_pair("map", "search") in DEFAULT_MAP_HINT, DEFAULT_MAP_HINT
    assert "ficha" not in DEFAULT_MAP_HINT and "buscar" not in DEFAULT_MAP_HINT


@red("hints")
def test_inc9c_k3_the_repo_surfaces_no_longer_advertise_a_dead_enter():
    """`INC9C-F1`: `↵ details` was advertised on the repo screen with no binding
    and no handler behind it (the lying affordance `US-N03` exists to remove)."""
    repo_rows = keymap.bindings_for(keymap.SCOPE_REPO)
    assert repo_rows and "enter" not in {b.key for b in repo_rows}
    source = _product_sources()["mapper/app.py"]
    assert "↵ detalle" not in source and '"details"' not in source


# ---------------------------------------------------------------------------
# INC9-UX-F2 / F3 / F10 / F11

@red("ux")
async def test_inc9c_ux_f2_a_real_question_mark_in_the_repo_field_opens_the_legend(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        app.push_screen(PlugRepoScreen())
        await pilot.pause()
        await pilot.pause()
        field = app.screen.query_one("#repo-input", Input)
        field.focus()
        field.value = "owner/na"
        await pilot.pause()
        assert app.focused is field
        await pilot.press("question_mark")
        await pilot.pause()
        await pilot.pause()
        legend = app.screen
        assert isinstance(legend, HelpScreen), f"`?` in the field opened {type(legend).__name__}"
        title = _rows_in(legend, legend.query_one("#help-title").region)
        assert any("legend · connect repo" in r for r in title), title
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, PlugRepoScreen)
        assert app.screen.query_one("#repo-input", Input).value == "owner/na"


def _visible(screen, widget) -> bool:
    geo = screen.find_widget(widget)
    return geo.clip.intersection(geo.region) == geo.region and geo.region.height > 0


@red("ux")
@pytest.mark.parametrize("size", [(118, 34), (87, 34)])
async def test_inc9c_ux_f3_components_scroll_and_every_tab_stop_is_on_screen(tmp_path, size):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        app.push_screen(SettingsScreen())
        await pilot.pause()
        await pilot.pause()
        screen = app.screen
        grid = screen.query_one("#settings-grid")
        chain = list(screen.focus_chain)
        assert isinstance(grid, VerticalScroll), type(grid).__name__
        assert len(chain) >= 10, chain
        assert app.focused in chain and _visible(screen, app.focused), (
            "focus starts off screen", screen.find_widget(app.focused).region)
        hidden = []
        for step in range(len(chain)):
            await pilot.press("tab")
            await pilot.pause()
            if not _visible(screen, app.focused):
                hidden.append((step, type(app.focused).__name__))
    assert hidden == [], f"tab stops off screen at {size}: {hidden}"


def _header(group: str) -> str:
    """`keymap.group_header`, falling back to the id so an order arm fails on the
    ORDER (its defect) and not on the missing name."""
    return getattr(keymap, "group_header", lambda g: g)(group)


def _legend_group_rows(rows: list[str]) -> list[str]:
    """Group headers in the legend's key section: unindented rows under it."""
    out, inside = [], False
    for row in rows:
        stripped = row.strip()
        if stripped == "keys in this view":
            inside = True
        elif inside and stripped and not row.startswith("  ") and stripped not in out:
            out.append(stripped)
    return out


@red("ux")
@pytest.mark.parametrize("name", sorted(HELP_SCREENS))
async def test_inc9c_ux_f10_legend_groups_follow_the_key_bar_order(tmp_path, monkeypatch, name):
    from mapper.app import GitHubConnector
    from tests.test_help_scope import _harvest

    monkeypatch.setattr(GitHubConnector, "fetch", lambda self, progress=None: Graph())
    cls = HELP_SCREENS[name]
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        opener = OPENERS[name]
        if opener == "map":
            from tests.test_repair_layout import _open_map
            await _open_map(app, pilot, _tree(app))
        elif opener is not None:
            app.push_screen(opener(app, cls))
            await pilot.pause()
            await pilot.pause()
        app.set_focus(None)
        await pilot.press("question_mark")
        await pilot.pause()
        await pilot.pause()
        rows = await _harvest(app, pilot, _rows_in, "#help-content")
    present = {b.group for b in keymap.bindings_for(cls.KEY_SCOPE)}
    expected = [_header(g) for g in keybar_groups(cls.KEY_SCOPE) if g in present]
    assert len(expected) >= 2, (name, expected)
    assert _legend_group_rows(rows) == expected, (name, _legend_group_rows(rows), expected)


@red("ux")
async def test_inc9c_ux_f11_enter_on_home_is_a_seat_row_and_opens_the_selected_map(tmp_path):
    row = _row("home", "open_selected")
    assert (row.key, row.glyph) == ("enter", "↵")
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        map_id = _tree(app)
        app.screen.on_mount()
        await pilot.pause()
        table = app.screen.query_one("#home-recents", DataTable)
        assert table.row_count >= 1
        app.set_focus(None)
        await pilot.press("enter")
        await pilot.pause()
        await pilot.pause()
        assert isinstance(app.screen, MapScreen) and app.screen.map_id == map_id, app.screen


# ---------------------------------------------------------------------------
# One name per group: what the key bar paints, the legend paints

#: The two screens whose key bar was hand-written; the rest are seat-generated and
#: agree by construction (kept in the parametrization as the guard that they still do).
_HAND_WRITTEN_BARS = {"HomeScreen", "RepoScreen"}


@pytest.mark.parametrize("name", [
    pytest.param(n, marks=[red("wording")] if n in _HAND_WRITTEN_BARS and "wording" in OPEN_STEPS else [])
    for n in sorted(set(HELP_SCREENS) - {"MapScreen"})])
async def test_inc9c_the_key_bar_and_the_legend_name_every_group_alike(tmp_path, monkeypatch, name):
    from mapper.app import GitHubConnector
    from tests.test_help_scope import _harvest

    monkeypatch.setattr(GitHubConnector, "fetch", lambda self, progress=None: Graph())
    cls = HELP_SCREENS[name]
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        opener = OPENERS[name]
        if opener is not None:
            app.push_screen(opener(app, cls))
            await pilot.pause()
            await pilot.pause()
        bars = app.screen.query(KeyBar)
        assert len(bars) == 1, (name, len(bars))
        bar_names = [g for g, items in bars.first().groups if items]
        app.set_focus(None)
        await pilot.press("question_mark")
        await pilot.pause()
        await pilot.pause()
        legend_names = _legend_group_rows(await _harvest(app, pilot, _rows_in, "#help-content"))
    assert bar_names and set(bar_names) <= set(legend_names), (name, bar_names, legend_names)


def test_inc9c_helpers_are_not_vacuous():
    assert len(SITES) == 10 and len(K1_LABELS) == 13
    assert _frame_rows
