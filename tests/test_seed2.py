"""Inc-SEED-2 -- the security review of Inc-SEED, closed (`A-113`, dated note 2026-09-30).

Findings: SEED2-F1 a real map named `new` was overwritten on open; SEED2-F2 the `..`
substring rule refused `v1..v2`; SEED2-F3 no length rule; SEED2-F4 a lone surrogate
passed the id check and left partial files; SEED2-F5 `CONIN$`/`CONOUT$`/`CLOCK$`.

Every defect arm was committed RED as a STRICT xfail keyed by the step that closes it
(`OPEN_STEPS`); the fix commits empty the set.  No user-profile path is typed literally.
"""
from __future__ import annotations

import pytest
from textual.widgets import DataTable

from mapper.app import MapperApp, MapScreen
from mapper.model import Ficha, Graph, Node
from mapper.store import MapIdError, MapStore, check_map_id
from tests.test_seed_safety import _digest, _drive, _tree_snapshot

OPEN_STEPS: set[str] = set()


def red(step: str):
    if step not in OPEN_STEPS:
        return lambda fn: fn
    return pytest.mark.xfail(
        strict=True, reason=f"Inc-SEED-2: committed RED; closed by the '{step}' step")


def _graph(title: str) -> Graph:
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title=title)))
    return g


# ---------------------------------------------------------------------------
# SEED2-F1: opening a real map named `new` must not replace it

@red("f1")
async def test_seed2_f1_opening_a_real_map_named_new_leaves_it_byte_identical(tmp_path):
    """The home row select pushes `MapScreen("new")`, which `on_mount` treated as a
    "make a fresh map" sentinel: both files were replaced by `root[nuevo mapa]`, no toast.

    RED on `a4f8b42`: sha256 of the `.mmd` and the sidecar change on open."""
    ws = tmp_path / "ws"
    MapStore(ws).save("new", _graph("KEEP-ME"))
    files = ("new.mmd", "new_nodos.yml")
    before = {n: _digest(ws / n) for n in files}
    app = MapperApp(ws)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        table = app.screen.query_one("#home-recents", DataTable)
        for _ in range(len(table.rows) + 1):
            if table.cursor_row >= 0 and str(
                    table.coordinate_to_cell_key(table.cursor_coordinate).row_key.value) == "new":
                break
            await pilot.press("down")
            await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, MapScreen)
        assert app.screen.map_id == "new"
        assert app.screen.graph.nodes["root"].ficha.title == "KEEP-ME"
    assert {n: _digest(ws / n) for n in files} == before


# ---------------------------------------------------------------------------
# SEED2-F2: `..` is the parent only when the id IS dots

@red("f2")
def test_seed2_f2_an_id_that_merely_contains_two_dots_creates_saves_and_loads(tmp_path):
    store = MapStore(tmp_path / "ws")
    store.create_seed("v1..v2")
    g = _graph("second")
    store.save("v1..v2", g)
    assert store.load("v1..v2").nodes["root"].ficha.title == "second"
    assert (tmp_path / "ws" / "v1..v2.mmd").is_file()


@pytest.mark.parametrize("name", [".", "..", "...", "....", ". ", ".. "])
def test_seed2_f2_dot_only_ids_are_still_refused(tmp_path, name):
    with pytest.raises(MapIdError):
        check_map_id(name)
    store = MapStore(tmp_path / "ws")
    before = _tree_snapshot(tmp_path)
    with pytest.raises(MapIdError):
        store.create_seed(name)
    assert _tree_snapshot(tmp_path) == before


# ---------------------------------------------------------------------------
# SEED2-F3: an over-long id gets a rule toast, not the generic one that echoes it

LIMIT = 100


@red("f3")
def test_seed2_f3_store_refuses_an_id_over_the_limit(tmp_path):
    store = MapStore(tmp_path / "ws")
    with pytest.raises(MapIdError) as err:
        store.create_seed("x" * (LIMIT + 1))
    assert "x" * 20 not in str(err.value)
    assert str(tmp_path) not in str(err.value)


def test_seed2_f3_an_id_at_the_limit_is_accepted(tmp_path):
    store = MapStore(tmp_path / "ws")
    store.create_seed("y" * LIMIT)
    assert (tmp_path / "ws" / f"{'y' * LIMIT}.mmd").is_file()


@red("f3")
async def test_seed2_f3_a_300_character_id_gets_a_rule_toast_that_omits_the_name(tmp_path):
    ws = tmp_path / "ws"
    MapStore(ws)
    name = "z" * 300
    toasts: list[str] = []
    before = _tree_snapshot(tmp_path)
    await _drive("construct", ws, name, toasts)
    assert toasts, "the refusal must reach the operator"
    text = "\n".join(toasts)
    assert "zzzzzzzzzz" not in text, "the toast echoes the typed name"
    assert "FileNotFoundError" not in text and "OSError" not in text, "the generic toast fired"
    assert str(tmp_path) not in text
    assert _tree_snapshot(tmp_path) == before


# ---------------------------------------------------------------------------
# SEED2-F4: a lone surrogate never reaches the disk

SURROGATES = ["a" + chr(0xD800), chr(0xDFFF), "x" + chr(0xDC00) + "y"]


def _map_files(ws) -> list[str]:
    return sorted(p.name for p in ws.iterdir() if p.suffix in (".mmd", ".yml"))


@red("f4")
@pytest.mark.parametrize("name", SURROGATES, ids=["a+D800", "DFFF", "x+DC00+y"])
def test_seed2_f4_store_refuses_a_lone_surrogate_and_writes_nothing(tmp_path, name):
    """RED on `a4f8b42`: `save` writes `<id>.mmd` and `<id>_nodos.yml`, then the
    sqlite reindex raises `UnicodeEncodeError`; both files stay behind."""
    ws = tmp_path / "ws"
    store = MapStore(ws)
    for call in (
        lambda: store.save(name, _graph("ok")),
        lambda: store.create(name, _graph("ok")),
        lambda: store.create_seed(name),
    ):
        with pytest.raises(MapIdError):
            call()
        assert _map_files(ws) == [], "partial files were left behind"


@red("f4")
async def test_seed2_f4_construct_with_a_surrogate_name_gets_a_rule_toast(tmp_path):
    ws = tmp_path / "ws"
    MapStore(ws)
    toasts: list[str] = []
    await _drive("construct", ws, "a" + chr(0xD800), toasts)
    assert toasts
    assert "UnicodeEncodeError" not in "\n".join(toasts), "the generic toast fired"
    assert _map_files(ws) == []


# ---------------------------------------------------------------------------
# SEED2-F5: the console device names

@red("f5")
@pytest.mark.parametrize(
    "name", ["CONIN$", "CONOUT$", "CLOCK$", "conin$", "ClOcK$.txt"])
def test_seed2_f5_console_and_clock_device_names_are_refused(tmp_path, name):
    store = MapStore(tmp_path / "ws")
    before = _tree_snapshot(tmp_path)
    with pytest.raises(MapIdError):
        store.create_seed(name)
    assert _tree_snapshot(tmp_path) == before


def test_seed2_f5_ordinary_dollar_names_stay_valid(tmp_path):
    store = MapStore(tmp_path / "ws")
    for name in ("price$", "CONIN", "CLOCKS$"):
        store.create_seed(name)
        assert (tmp_path / "ws" / f"{name}.mmd").is_file()
