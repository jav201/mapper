"""Inc-SEED -- a typed map id names a file inside the workspace, and creating never
overwrites (`A-113`; findings `SEED-1`, `SEED-2`).

Every defect arm is driven through the REAL key path from home (`n`, `t`, `i` + `s`)
and was committed RED first, as a STRICT xfail keyed by the step that closes it
(`OPEN_STEPS`); the fix commit empties the set.  The store-level arms exist so a
mutant that validates only in the UI still dies.

While the defect is live a traversal name would really write outside the sandbox
(a drive-qualified name lands at a drive root), so `_guard_writes` records every
write target and performs only the ones inside the test's own `tmp_path`.

No user-profile path is typed literally (`A-110`).
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest
from textual.widgets import Input

from mapper.app import ConstructScreen, MapperApp, MapScreen
from mapper.model import Ficha, Graph, Node
from mapper.store import TEMPLATES, MapStore, MapStoreError

OPEN_STEPS: set[str] = set()


def red(step: str):
    if step not in OPEN_STEPS:
        return lambda fn: fn
    return pytest.mark.xfail(
        strict=True, reason=f"Inc-SEED: committed RED; closed by the '{step}' step")


SIZE = (118, 34)

#: Names that must never reach the disk.  The third is a drive-qualified absolute
#: path; the last is an NTFS alternate-data-stream spelling.
BAD_NAMES = ["../x", "..\\x", "C:\\x", "CON", "a/b", "a:b"]
#: Names whose rejection text must not echo them (they carry a path shape).
PATHLIKE = {"../x", "..\\x", "C:\\x", "a/b", "a:b"}


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_snapshot(root: Path) -> dict[str, str]:
    return {
        p.relative_to(root).as_posix(): _digest(p)
        for p in sorted(root.rglob("*")) if p.is_file()
    }


def _guard_writes(monkeypatch, sandbox: Path) -> list[Path]:
    """Record every temp-file write; perform only those inside `sandbox`."""
    real = MapStore._write_tmp
    targets: list[Path] = []
    root = sandbox.resolve()

    def recording(self, path, text):
        targets.append(Path(path))
        try:
            inside = Path(path).resolve().is_relative_to(root)
        except (OSError, ValueError):
            inside = False
        if not inside:
            raise OSError("write refused by the test sandbox")
        return real(self, path, text)

    monkeypatch.setattr(MapStore, "_write_tmp", recording)
    return targets


def _seed_existing(ws: Path, map_id: str = "layout") -> dict[str, str]:
    store = MapStore(ws)
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="the real map", meta="keep me")))
    store.save(map_id, g)
    return {
        f"{map_id}.mmd": _digest(ws / f"{map_id}.mmd"),
        f"{map_id}_nodos.yml": _digest(ws / f"{map_id}_nodos.yml"),
    }


async def _open_construct(app, pilot, name: str, csv) -> None:
    await pilot.press("n")
    await pilot.pause()
    app.screen.query_one("#construct-input", Input).value = name
    await pilot.press("enter")
    await pilot.pause()


async def _open_template(app, pilot, name: str, csv) -> None:
    await pilot.press("t")
    await pilot.pause()
    await pilot.press("enter")
    await pilot.pause()
    app.screen.query_one("#prompt-input", Input).value = name
    await pilot.press("enter")
    await pilot.pause()


async def _open_import(app, pilot, name: str, csv: Path) -> None:
    await pilot.press("i")
    await pilot.pause()
    app.screen.query_one("#prompt-input", Input).value = str(csv)
    await pilot.press("enter")
    await pilot.pause()
    await pilot.press("s")
    await pilot.pause()
    app.screen.query_one("#prompt-input", Input).value = name
    await pilot.press("enter")
    await pilot.pause()


ENTRY_POINTS = {
    "construct": _open_construct,
    "template": _open_template,
    "import": _open_import,
}


async def _drive(entry: str, ws: Path, name: str, toasts: list[str], csv=None):
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        app.notify = lambda msg, **kw: toasts.append(str(msg))
        await ENTRY_POINTS[entry](app, pilot, name, csv)
        return type(app.screen)


def _csv(tmp_path: Path) -> Path:
    path = tmp_path / "nodos.csv"
    path.write_text("id,title,parent\nroot,raiz,\nn1,hijo,root\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# SEED-1: creating a map whose id exists never overwrites it

EXISTING_NAMES = ["layout"]
if sys.platform == "win32":
    EXISTING_NAMES.append("LAYOUT")  # NTFS is case-insensitive: same file


@red("seed-safety")
@pytest.mark.parametrize("typed", EXISTING_NAMES)
@pytest.mark.parametrize("entry", sorted(ENTRY_POINTS))
async def test_seed1_existing_map_is_left_byte_identical(tmp_path, entry, typed):
    """One keystroke on an existing name must not replace the map (`B-36`'s
    position).  sha256 of the `.mmd` and the `_nodos.yml` before and after, plus a
    toast the operator can read.

    RED on `fddd07d`: `create_seed` / `create_from_template` / "save as" call
    `save`, which replaces both files."""
    ws = tmp_path / "ws"
    before = _seed_existing(ws)
    toasts: list[str] = []
    screen = await _drive(entry, ws, typed, toasts, _csv(tmp_path))
    after = {n: _digest(ws / n) for n in before}
    assert after == before, f"{entry}: an existing map was overwritten"
    assert toasts, f"{entry}: the refusal must reach the operator as a toast"
    assert screen is not MapScreen, f"{entry}: the session moved on as if it had created the map"


# ---------------------------------------------------------------------------
# SEED-2: a typed id never leaves the workspace

@red("seed-safety")
@pytest.mark.parametrize("name", BAD_NAMES)
@pytest.mark.parametrize("entry", sorted(ENTRY_POINTS))
async def test_seed2_bad_name_writes_nothing_and_toasts(tmp_path, monkeypatch, entry, name):
    """The workspace's parent (`tmp_path`) and the workspace are snapshotted before
    and after: nothing new, nothing changed.  A toast names the rule and carries
    neither the sandbox path nor, for a path-shaped name, the typed text.

    RED on `fddd07d`: the name is joined onto the workspace unchecked."""
    ws = tmp_path / "ws"
    MapStore(ws)
    csv = _csv(tmp_path)
    targets = _guard_writes(monkeypatch, tmp_path)
    before = _tree_snapshot(tmp_path)
    toasts: list[str] = []
    await _drive(entry, ws, name, toasts, csv)
    root = ws.resolve()
    outside = [t for t in targets if not Path(t).resolve().is_relative_to(root)]
    assert not outside, f"{entry}: {name!r} tried to write outside the workspace"
    assert _tree_snapshot(tmp_path) == before, f"{entry}: {name!r} wrote something"
    assert toasts, f"{entry}: {name!r} was refused silently"
    text = "\n".join(toasts)
    assert str(tmp_path) not in text
    if name in PATHLIKE:
        assert name not in text, "the toast echoes the rejected, path-shaped text"


# ---------------------------------------------------------------------------
# The positive control: a valid new name still creates the map

@pytest.mark.parametrize("entry", sorted(ENTRY_POINTS))
async def test_seed_valid_new_name_creates_the_map(tmp_path, entry):
    ws = tmp_path / "ws"
    MapStore(ws)
    toasts: list[str] = []
    screen = await _drive(entry, ws, "brand-new", toasts, _csv(tmp_path))
    assert (ws / "brand-new.mmd").is_file()
    assert (ws / "brand-new_nodos.yml").is_file()
    assert screen is MapScreen


# ---------------------------------------------------------------------------
# The construct dialog refuses early: it stays open so the name can be fixed

@red("seed-safety")
async def test_seed_construct_dialog_stays_open_on_a_refused_name(tmp_path):
    ws = tmp_path / "ws"
    MapStore(ws)
    toasts: list[str] = []
    screen = await _drive("construct", ws, "../x", toasts)
    assert screen is ConstructScreen
    assert toasts


# ---------------------------------------------------------------------------
# Store level: the boundary refuses by itself, whatever the UI did

@red("seed-safety")
@pytest.mark.parametrize(
    "name", BAD_NAMES + ["", " ", "x.", "..", "a*b", "NUL.txt", "com1", "lpt9"])
def test_seed_store_refuses_every_write_door(tmp_path, name):
    ws = tmp_path / "ws"
    store = MapStore(ws)
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="r")))
    template_id = next(iter(TEMPLATES))
    before = _tree_snapshot(tmp_path)
    for call in (
        lambda: store.save(name, g),
        lambda: store.create(name, g),
        lambda: store.create_seed(name),
        lambda: store.create_from_template(name, template_id),
    ):
        with pytest.raises(MapStoreError) as err:
            call()
        assert str(tmp_path) not in str(err.value)
    assert _tree_snapshot(tmp_path) == before


@red("seed-safety")
def test_seed_store_create_refuses_an_existing_id(tmp_path):
    ws = tmp_path / "ws"
    before = _seed_existing(ws)
    store = MapStore(ws)
    with pytest.raises(MapStoreError):
        store.create_seed("layout")
    assert {n: _digest(ws / n) for n in before} == before


@red("seed-safety")
def test_seed_store_refuses_when_only_the_sidecar_exists(tmp_path):
    ws = tmp_path / "ws"
    store = MapStore(ws)
    (ws / "half_nodos.yml").write_text("keep: me\n", encoding="utf-8")
    with pytest.raises(MapStoreError):
        store.create_seed("half")
    assert (ws / "half_nodos.yml").read_text(encoding="utf-8") == "keep: me\n"
    assert not (ws / "half.mmd").exists()


@red("seed-safety")
def test_seed_store_load_refuses_a_link_that_leaves_the_workspace(tmp_path):
    """A `map:` link is file-derived text; `load` is the read-side door."""
    ws = tmp_path / "ws"
    store = MapStore(ws)
    _seed_existing(tmp_path, "secret")
    with pytest.raises(MapStoreError):
        store.load("../secret")


def test_seed_store_accepts_ordinary_names(tmp_path):
    store = MapStore(tmp_path / "ws")
    for name in ("layout", "mi mapa", "a.b", "ñandú", "brand-new_2", "concept", "console"):
        store.create_seed(name)
        assert (tmp_path / "ws" / f"{name}.mmd").is_file()
