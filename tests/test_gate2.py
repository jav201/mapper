"""Gate-2 -- the pre-merge fixes of `VERDICT-merge-2026-10-03.md` (M1).

Authority: `A-139`.  Every arm a fix closes was committed RED first as a STRICT xfail keyed by the step
that closes it (`OPEN_STEPS`), then run with `--runxfail` on the base commit in a separate worktree.  An
arm that is not keyed is a pin (green on the base), killed by a mutant instead.

Real keys everywhere a key is the contract.  Nothing here reaches the network, a real `gh`, a real cache
or a real file launcher.  Control and bidi characters are `\\u` escapes (this file is ASCII).
"""
from __future__ import annotations

import stat
import subprocess
import zipfile
from pathlib import Path

import pytest
from textual.widgets import DataTable

from mapper import github
from mapper.app import PAN_INERT_HINT, MapScreen, MapperApp, map_hint
from mapper.github import GitHubConnector
from mapper.import_csv import preview_csv
from mapper.model import Document, Ficha, Graph, Node
from mapper.screens.factory import FactoryScreen
from mapper.store import MapStore
from mapper.widgets.chrome import HintLine
from tests.inc3_support import open_map, pan_graph, rows_in

OPEN_STEPS: set[str] = set()

SIZE = (118, 34)
NARROW = (87, 34)
BOTH = [SIZE, NARROW]


def red(step: str):
    if step in OPEN_STEPS:
        return pytest.mark.xfail(
            strict=True, reason=f"Gate-2: committed RED; closed by the '{step}' step")
    return lambda fn: fn


def _graph(title: str) -> Graph:
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title=title)))
    return g


# ---------------------------------------------------------------------------
# PR-QA-F1 -- `j` / `k` on home call a method DataTable does not have

def _row_ids(table: DataTable) -> list[str]:
    return [str(k.value) for k in table.rows]


def _cursor_id(table: DataTable) -> str:
    return str(table.coordinate_to_cell_key(table.cursor_coordinate).row_key.value)


@red("f1")
@pytest.mark.parametrize("size", BOTH)
async def test_gate2_f1_j_j_k_walk_the_home_cursor_and_enter_opens_the_row_under_it(tmp_path, size):
    """The seat advertises `j next map` / `k previous map`.  RED on `0133cfb`: the first `j` raises
    `AttributeError: 'DataTable' object has no attribute 'cursor_down'` and the app stops."""
    ws = tmp_path / "ws"
    store = MapStore(ws)
    for name in ("alfa", "beta", "gamma"):
        store.save(name, _graph(name))
    app = MapperApp(ws)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        table = app.screen.query_one("#home-recents", DataTable)
        assert table.row_count == 3
        seen = [table.cursor_row]
        for key in ("j", "j", "k"):
            await pilot.press(key)
            await pilot.pause()
            assert app.is_running, f"the app stopped on {key!r}"
            seen.append(table.cursor_row)
        assert seen == [0, 1, 2, 1], seen
        expected = _row_ids(table)[1]
        assert _cursor_id(table) == expected
        await pilot.press("enter")
        await pilot.pause()
        await pilot.pause()
        assert isinstance(app.screen, MapScreen) and app.screen.map_id == expected, app.screen


@red("f1")
@pytest.mark.parametrize("size", BOTH)
async def test_gate2_f1_with_one_map_j_and_k_clamp_and_the_app_stays_up(tmp_path, size):
    ws = tmp_path / "ws"
    MapStore(ws).save("solo", _graph("solo"))
    app = MapperApp(ws)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        table = app.screen.query_one("#home-recents", DataTable)
        assert table.row_count == 1
        for key in ("j", "k", "j", "k"):
            await pilot.press(key)
            await pilot.pause()
            assert app.is_running, f"the app stopped on {key!r}"
            assert table.cursor_row == 0
        await pilot.press("enter")
        await pilot.pause()
        await pilot.pause()
        assert isinstance(app.screen, MapScreen) and app.screen.map_id == "solo"


@red("f1")
def test_gate2_f1_no_other_call_site_uses_a_widget_method_that_does_not_exist():
    """The census: the product calls neither `.cursor_down(` nor `.cursor_up(` (DataTable's are
    `action_cursor_down` / `action_cursor_up`); a widget that really has them would be listed here."""
    root = Path(github.__file__).parent
    hits = []
    for path in root.rglob("*.py"):
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if ".cursor_down(" in line or ".cursor_up(" in line:
                hits.append(f"{path.name}:{n}")
    assert hits == [], hits


# ---------------------------------------------------------------------------
# PR-QA-F3 -- the map hint after a pan, an edge, a view change

def _painted(screen) -> str:
    return " ".join(" ".join(rows_in(screen, screen.query_one(HintLine).region)).split())


def _stored(screen) -> str:
    return screen.query_one(HintLine).text


async def _open_pan(app, pilot) -> MapScreen:
    app.store.save("pan", pan_graph())
    screen = await open_map(app, pilot, "pan")
    await pilot.pause()
    return screen


async def _press(pilot, *keys: str) -> None:
    for key in keys:
        await pilot.press(key)
        await pilot.pause()


async def _to_the_edge(pilot, screen, key: str) -> None:
    for _ in range(60):
        if _stored(screen) == "edge of the map":
            return
        await _press(pilot, key)
    raise AssertionError("never reached the edge of the map")


@red("f3")
@pytest.mark.parametrize("size", BOTH)
async def test_gate2_f3_after_a_live_pan_the_hint_is_the_map_hint_not_blank(tmp_path, size):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = await _open_pan(app, pilot)
        key = "L" if size == SIZE else "J"
        await _press(pilot, key)
        assert (screen.pan_x, screen.pan_y) != (0, 0), "the press was a no-op; this arm proves nothing"
        assert _stored(screen) == map_hint()
        assert " ".join(map_hint().split()) in _painted(screen), _painted(screen)


@red("f3")
@pytest.mark.parametrize("size", BOTH)
@pytest.mark.parametrize("view_key", ["o", "r", "R"])
async def test_gate2_f3_the_edge_hint_does_not_survive_a_view_change(tmp_path, size, view_key):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = await _open_pan(app, pilot)
        await _to_the_edge(pilot, screen, "J")
        assert _stored(screen) == "edge of the map"
        await _press(pilot, view_key)
        assert _stored(screen) == map_hint(), _stored(screen)
        assert "edge of the map" not in _painted(screen)


@red("f3")
@pytest.mark.parametrize("size", BOTH)
@pytest.mark.parametrize("leave_key", ["o", "r"])
async def test_gate2_f3_the_inert_hint_gives_way_to_the_map_hint(tmp_path, size, leave_key):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = await _open_pan(app, pilot)
        await _press(pilot, "o", "J")
        assert _stored(screen) == PAN_INERT_HINT, "outline did not decline the pan; this arm proves nothing"
        await _press(pilot, leave_key)
        assert _stored(screen) == map_hint(), _stored(screen)
        assert PAN_INERT_HINT not in _painted(screen)


@red("f3")
@pytest.mark.parametrize("size", BOTH)
async def test_gate2_f3_a_live_search_hint_is_neither_blanked_by_a_pan_nor_dropped_by_a_view_change(tmp_path, size):
    """The search-active hint is the resting hint while a query is live: a pan, an edge and a view
    change restore THAT, not `map_hint()`.  Green on the base for the first press only if the pan keeps
    the hint; the view-change half is the part the fix could break."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = await _open_pan(app, pilot)
        await _press(pilot, "slash")
        await pilot.press("r", "a", "m", "a")
        await pilot.press("enter")
        await pilot.pause()
        assert screen._search_is_live()
        search_hint = screen._search_hint(screen._search_order())
        assert _stored(screen) == search_hint and search_hint != map_hint()
        await _press(pilot, "J")
        assert screen.pan_y != 0, "the press was a no-op; this arm proves nothing"
        assert _stored(screen) == screen._search_hint(screen._search_order()), _stored(screen)
        await _to_the_edge(pilot, screen, "J")
        await _press(pilot, "o")
        assert _stored(screen) == screen._search_hint(screen._search_order()), _stored(screen)


@pytest.mark.parametrize("size", BOTH)
async def test_gate2_f3_a_hint_another_handler_declared_is_not_swallowed_by_a_view_change(tmp_path, size):
    """The scoping `_clear_pan_hint` documents: only a pan hint is replaced."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = await _open_pan(app, pilot)
        screen.query_one(HintLine).set_hint("something else declared this")
        await _press(pilot, "o")
        assert _stored(screen) == "something else declared this"


# ---------------------------------------------------------------------------
# BRANCH-SEC-F3 -- a repo's own config must not run a program through `git log`

def _forged_signature_repo(root: Path) -> tuple[Path, Path]:
    """A local repo whose own config verifies signatures through a marker-writing program, and whose
    only commit carries a forged `gpgsig` header (written with `hash-object`, no key involved)."""
    repo = root / "victim"
    repo.mkdir()
    marker = root / "marker.txt"
    program = root / "fake-gpg.sh"
    program.write_text(f'#!/bin/sh\necho ran > "{marker.as_posix()}"\nexit 1\n', encoding="utf-8", newline="\n")
    program.chmod(program.stat().st_mode | stat.S_IEXEC)

    def git(*args: str, stdin: str | None = None) -> str:
        # Bytes in, bytes out: text mode would turn the commit's LF into CRLF on Windows.
        done = subprocess.run(["git", "-C", str(repo), *args], input=None if stdin is None else stdin.encode(),
                              capture_output=True, check=True)
        return done.stdout.decode().strip()

    git("init", "-q", "-b", "master")
    tree = git("hash-object", "-t", "tree", "-w", "--stdin", stdin="")
    commit = (
        f"tree {tree}\nauthor a <a@example.invalid> 1700000000 +0000\n"
        "committer a <a@example.invalid> 1700000000 +0000\n"
        "gpgsig -----BEGIN PGP SIGNATURE-----\n \n forged\n -----END PGP SIGNATURE-----\n\nforged\n"
    )
    sha = git("hash-object", "-t", "commit", "-w", "--stdin", stdin=commit)
    git("update-ref", "refs/heads/master", sha)
    git("config", "log.showSignature", "true")
    git("config", "gpg.program", program.as_posix())
    return repo, marker


@red("sec3")
def test_gate2_sec3_a_repo_config_cannot_run_a_program_through_git_log(tmp_path):
    """RED on `0133cfb`: `git log -1` with `log.showSignature=true` runs `gpg.program` on the forged
    header and the marker appears."""
    repo, marker = _forged_signature_repo(tmp_path)
    # The control: the repo does run the program when asked the plain way (the trap is armed).
    subprocess.run(["git", "-C", str(repo), "log", "-1"], capture_output=True, check=False)
    assert marker.is_file(), "the trap is not armed: plain `git log -1` did not run the program"
    marker.unlink()
    graph = GitHubConnector(str(repo)).fetch()
    assert "master" in graph.nodes
    assert not marker.exists(), "fetch() ran the repository's gpg.program"


@red("sec3")
def test_gate2_sec3_every_git_call_pins_the_config_keys_that_can_run_a_program(monkeypatch, tmp_path):
    seen: list[list[str]] = []

    def fake_run(argv, **kw):
        seen.append(list(argv))
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    monkeypatch.setattr(github.subprocess, "run", fake_run)
    github._run_git(tmp_path, ["tag", "-l"])
    argv = seen[-1]
    assert "log.showSignature=false" in argv and "core.fsmonitor=false" in argv, argv
    assert argv[argv.index("log.showSignature=false") - 1] == "-c"
    assert argv[argv.index("core.fsmonitor=false") - 1] == "-c"
    assert argv.index("-c") < argv.index("tag"), "the pins must precede the subcommand"
    github._last_commit_info(tmp_path, "master")
    assert "--no-show-signature" in seen[-1], seen[-1]
    assert seen[-1].index("--no-show-signature") < seen[-1].index("--end-of-options")


# ---------------------------------------------------------------------------
# BRANCH-SEC-F4 / PR-QA-F4 -- the factory preview

def _make_docx(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
           f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:document>")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", "<?xml version='1.0' encoding='UTF-8' standalone='yes'?><Types/>")
        zf.writestr("word/document.xml", xml)


def _doc_graph(path: str) -> Graph:
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="proceso")))
    g.documents["plantilla"] = Document(name="plantilla", path=path, kind="docx", template=True)
    return g


async def _factory_preview(tmp_path, text: str, size) -> tuple[str, str]:
    ws = tmp_path / "ws"
    _make_docx(ws / "templates" / "plantilla.docx", text)
    app = MapperApp(ws)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph("templates/plantilla.docx"), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        assert app.screen is screen
        frame = "\n".join(rows_in(screen, screen.query_one("#factory-preview").region))
        return screen._preview().plain, frame


@red("f4")
@pytest.mark.parametrize("size", BOTH)
async def test_gate2_f4_the_preview_names_the_template_by_its_workspace_relative_path(tmp_path, size):
    """RED on `0133cfb`: the preview paints the resolved absolute path (drive, profile folder)."""
    plain, frame = await _factory_preview(tmp_path, "hello", size)
    assert "templates/plantilla.docx" in plain
    for painted in (plain, frame):
        assert ":\\" not in painted and ":/" not in painted, painted
        assert "Users" not in painted, painted
    assert str(tmp_path) not in plain


@red("f4")
@pytest.mark.parametrize("size", BOTH)
async def test_gate2_f4_extracted_docx_text_is_coerced_before_it_is_painted(tmp_path, size):
    """RED on `0133cfb`: a bidi override, a C1 CSI and a tag character in a paragraph reach the frame."""
    hostile = "a\u202eb\u009bc\U000E0041d"
    plain, frame = await _factory_preview(tmp_path, hostile, size)
    assert "\ufffd" in plain
    for bad in ("\u202e", "\u009b", "\U000E0041"):
        assert bad not in plain, hex(ord(bad))
        assert bad not in frame, hex(ord(bad))
    assert "a\ufffdb\ufffdc\ufffdd" in plain, plain


# ---------------------------------------------------------------------------
# PR-QA-F5 -- the generated CSV id is English

@red("f5")
def test_gate2_f5_a_csv_row_with_no_id_and_no_title_gets_an_english_id(tmp_path):
    path = tmp_path / "nodes.csv"
    path.write_text("id,title,parent\nroot,root,\n,,root\n,,root\n", encoding="utf-8")
    graph = preview_csv(path)
    assert "row-1" in graph.nodes and "row-2" in graph.nodes, sorted(graph.nodes)
    assert not any(n.startswith("fila") for n in graph.nodes), sorted(graph.nodes)
