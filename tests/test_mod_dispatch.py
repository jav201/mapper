"""LLR-MOD.2.1 / 2.2 / 2.3 + AT-066 (HLR-MOD.2): Textual dispatch through the mixins.

Spine B composes `MapScreen` from plain mixins (mechanism A).  Two of the three
failure modes the ARQ spike measured on Textual 8.2.8 are SILENT: a `BINDINGS`
declared in a mixin is never merged (keys drop), and an `on_*` name declared in
two MRO classes runs TWICE (`evidence/arq-mro-spike.transcript`).  So dispatch
preservation is guarded, not assumed:

* LLR-MOD.2.2 — method names of `MapScreen` and of every class it inherits from
  are pairwise disjoint.  The mixin set is DERIVED from `MapScreen`'s own bases
  under the package root being scanned (so a tmp-copy mutant is judged by its
  own tree), never hand-listed.
* LLR-MOD.2.1 — no mixin declares `BINDINGS`, `DEFAULT_CSS` or `CSS`, no mixin
  method carries an `@on(...)` decorator, and the AST-derived roster of core
  class-level constants is held only by the core class (0 shadowed, each
  assigned exactly once across the package).
* LLR-MOD.2.2 / ARCH-7 — the call-count control: a tiny app whose screen
  composes two mixins that both define `on_mount` must observe TWO calls,
  proving why the disjointness guard exists on this exact Textual version.
* AT-066 — the B1 pilot (LLR-MOD.2.3): drive the real `MapperApp` with real
  keys and assert the painted hint line equals the pre-B1 baseline
  (`evidence/at066-baseline.txt`, sha256 pinned below).  The key pressed is
  `M` (`next incomplete`): the action focuses the gap field and the
  `DescendantFocus` handler paints the fill-in hint through the `HintsOps`
  mixin (`_field_hint` / `_seat_glyph`).  Its RED runs the same capture in a
  SUBPROCESS over a tmp copy whose `MapScreen` drops `HintsOps` from its
  bases — the pressed key's path then raises/breaks and the capture differs
  or fails (the C5 mechanism of `tests/test_mod_parity.py`).
"""
from __future__ import annotations

import ast
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from textual.app import App
from textual.screen import Screen

from mapper.app import MapScreen, MapperApp
from mapper.widgets.chrome import HintLine

from tests.test_draft_save import _open, _press, _seed_map

REPO_ROOT = Path(__file__).resolve().parents[1]
MAP_PKG = REPO_ROOT / "mapper" / "screens" / "map"
AT066_BASELINE = (
    REPO_ROOT / ".dev-flow" / "2026-10-09-modular-batch" / "evidence" / "at066-baseline.txt"
)
AT066_SIZE = (118, 34)

#: PDR C4: the baseline's path, its sha256 and the bound key are pinned here.
#: Filled in from the pre-split-behaviour capture (this tree, before B1's
#: dispatch is ever exercised by a later increment).
AT066_BASELINE_SHA256 = "23b01b2abb202a80fbecf20cba95289ac22c33a43dd5d10c9a242af2bde31b3b"


# ---------------------------------------------------------------------------
# Structural checkers — every one takes the map package root, so the GREEN
# tests run them on the real tree and the RED tests on a tmp-copy mutant.
# ---------------------------------------------------------------------------

def _classes(pkg: Path) -> dict[str, ast.ClassDef]:
    """Top-level classes of the package's `*.py`, by name."""
    found: dict[str, ast.ClassDef] = {}
    for path in sorted(pkg.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                found[node.name] = node
    return found


def _mixin_names(pkg: Path) -> set[str]:
    """`MapScreen`'s own bases minus Textual's `Screen` — the derived mixin set."""
    screen = _classes(pkg)["MapScreen"]
    return {b.id for b in screen.bases if isinstance(b, ast.Name)} - {"Screen"}


def _method_names(cls: ast.ClassDef) -> set[str]:
    return {
        node.name
        for node in cls.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _class_level_assignments(cls: ast.ClassDef) -> set[str]:
    names: set[str] = set()
    for node in cls.body:
        if isinstance(node, ast.Assign):
            names |= {t.id for t in node.targets if isinstance(t, ast.Name)}
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def _disjoint_method_names(pkg: Path) -> dict[str, set[str]]:
    """Method-name sets of `MapScreen` and of every class in its derived mixin set."""
    classes = _classes(pkg)
    roster = {"MapScreen", *_mixin_names(pkg)}
    missing = roster - classes.keys()
    assert not missing, f"classes named in MapScreen's bases not found under {pkg}: {missing}"
    return {name: _method_names(classes[name]) for name in sorted(roster)}


def _collisions(by_class: dict[str, set[str]]) -> list[str]:
    names = sorted(by_class)
    return [
        f"{a} x {b}: {sorted(by_class[a] & by_class[b])}"
        for i, a in enumerate(names)
        for b in names[i + 1:]
        if by_class[a] & by_class[b]
    ]


_BANNED_DECLARATIONS = ("BINDINGS", "DEFAULT_CSS", "CSS")


def _mixin_declaration_violations(pkg: Path) -> list[str]:
    """LLR-MOD.2.1 as one report: banned declarations and shadowed/dropped
    core constants.  Empty list == pass."""
    classes = _classes(pkg)
    mixins = _mixin_names(pkg)
    violations: list[str] = []
    core_constants = _class_level_assignments(classes["MapScreen"])
    for name in sorted(mixins):
        cls = classes[name]
        assignments = _class_level_assignments(cls)
        for ban in _BANNED_DECLARATIONS:
            if ban in assignments:
                violations.append(f"{name} declares {ban}")
        for shadowed in sorted(assignments & core_constants):
            violations.append(f"{name} shadows core constant {shadowed}")
        for node in cls.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for dec in node.decorator_list:
                    target = dec.func if isinstance(dec, ast.Call) else dec
                    if isinstance(target, ast.Name) and target.id == "on":
                        violations.append(f"{name}.{node.name} has an @on decorator")
    counts: dict[str, int] = {}
    for cls in classes.values():
        for const in _class_level_assignments(cls):
            counts[const] = counts.get(const, 0) + 1
    for const in sorted(core_constants):
        if counts.get(const) != 1:
            violations.append(
                f"core constant {const} is assigned at class level "
                f"{counts.get(const)} times across the package"
            )
    return violations


def _inject_method(path: Path, class_name: str, method: str) -> None:
    """Insert `def <method>(self, event): pass` as the first member of the class."""
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    cls = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and node.name == class_name
    )
    lines = src.splitlines(keepends=True)
    at = cls.body[0].lineno - 1
    lines[at:at] = [f"    def {method}(self, event): pass\n\n"]
    path.write_text("".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# LLR-MOD.2.2 — pairwise-disjoint method names (GREEN + tmp-copy RED)
# ---------------------------------------------------------------------------

def test_llr_mod_2_2_method_names_disjoint_across_map_package():
    """GREEN on the real tree: the mixin set is derived (not hand-listed) and
    non-empty, and no method name collides across `MapScreen` and its mixins —
    a duplicated `on_*` would fire twice on Textual 8.2.8 (see the call-count
    control below)."""
    mixins = _mixin_names(MAP_PKG)
    assert mixins, "the mixin set derived from MapScreen's bases is empty"
    by_class = _disjoint_method_names(MAP_PKG)
    assert _collisions(by_class) == [], _collisions(by_class)


def test_llr_mod_2_2_red_duplicate_method_name_across_mixins(tmp_path):
    """RED on a tmp copy: the same handler name added to a mixin AND the core
    must be reported by the checker (spike rule 3: it would fire twice)."""
    copy = tmp_path / "map"
    shutil.copytree(MAP_PKG, copy)
    _inject_method(copy / "hints.py", "HintsOps", "on_resize")
    _inject_method(copy / "screen.py", "MapScreen", "on_resize")
    collisions = _collisions(_disjoint_method_names(copy))
    assert any("on_resize" in c for c in collisions), collisions


# ---------------------------------------------------------------------------
# LLR-MOD.2.1 — BINDINGS / CSS / @on and class constants only on the core
# ---------------------------------------------------------------------------

def test_llr_mod_2_1_bindings_and_constants_live_only_on_the_core():
    """GREEN on the real tree: 0 banned declarations in any mixin, 0 shadowed
    or dropped core constants — and the AST-derived roster really is held by
    the runtime `MapScreen` class object."""
    assert _mixin_declaration_violations(MAP_PKG) == []
    core_constants = _class_level_assignments(_classes(MAP_PKG)["MapScreen"])
    assert "BINDINGS" in core_constants
    dropped = {name for name in core_constants if name not in vars(MapScreen)}
    assert dropped == set(), f"core constants missing from MapScreen.__dict__: {dropped}"


def test_llr_mod_2_1_red_mixin_declaring_bindings_or_on(tmp_path):
    """RED on a tmp copy: a mixin declaring `BINDINGS` and an `@on`-decorated
    method must both be reported (spike rules 1–2: keys silently drop, the
    decorator is silently ignored)."""
    copy = tmp_path / "map"
    shutil.copytree(MAP_PKG, copy)
    hints = copy / "hints.py"
    src = hints.read_text(encoding="utf-8")
    tree = ast.parse(src)
    cls = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and node.name == "HintsOps"
    )
    lines = src.splitlines(keepends=True)
    at = cls.body[0].lineno - 1
    lines[at:at] = [
        "    BINDINGS = []\n",
        "\n",
        "    @on(Static.Changed)\n",
        "    def _mutant_changed(self, event):\n",
        "        pass\n",
        "\n",
    ]
    hints.write_text("".join(lines), encoding="utf-8")

    violations = _mixin_declaration_violations(copy)
    assert any("declares BINDINGS" in v for v in violations), violations
    assert any("@on" in v for v in violations), violations


# ---------------------------------------------------------------------------
# LLR-MOD.2.2 / ARCH-7 — the call-count control: why disjointness matters
# ---------------------------------------------------------------------------

class _FirstMixin:
    def on_mount(self) -> None:
        self.app.mount_calls.append("first")


class _SecondMixin:
    def on_mount(self) -> None:
        self.app.mount_calls.append("second")


class _DuplicateHandlerScreen(_FirstMixin, _SecondMixin, Screen):
    pass


class _DuplicateHandlerApp(App):
    def __init__(self) -> None:
        super().__init__()
        self.mount_calls: list[str] = []

    def on_mount(self) -> None:
        self.push_screen(_DuplicateHandlerScreen())


async def test_llr_mod_2_2_duplicate_handler_runs_twice():
    """ARCH-7, measured on the shipped Textual 8.2.8: `on_*` handlers run from
    EVERY MRO class that defines them.  A screen whose two mixins both define
    `on_mount` must observe BOTH calls — an idempotent handler may change no
    paint, so only a call count can carry this RED (HLR-MOD.2's boundary)."""
    app = _DuplicateHandlerApp()
    async with app.run_test() as pilot:
        await pilot.pause()
    assert sorted(app.mount_calls) == ["first", "second"], app.mount_calls


# ---------------------------------------------------------------------------
# AT-066 — the B1 pilot (LLR-MOD.2.3): real keys through the real app
# ---------------------------------------------------------------------------

def _painted_hint_line(screen) -> str:
    """The HintLine row as COMPOSITED — the seam `tests/test_draft_save.py`
    reads (`_hint_text_and_prefix_style`), not the stored value."""
    region = screen.query_one(HintLine).region
    strips = screen._compositor.render_strips()  # noqa: SLF001
    text = ""
    for strip in strips[region.y: region.y + region.height]:
        x = 0
        for seg in strip:
            if region.x <= x < region.x + region.width:
                text += seg.text
            x += len(seg.text)
    return text.rstrip()


async def _at066_capture(ws: Path) -> list[str]:
    """The pilot's scripted sequence: open the seeded map, press `M`.  Runnable
    both inside pytest and, via `asyncio.run`, in the mutant subprocess."""
    app = MapperApp(ws)
    async with app.run_test(size=AT066_SIZE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        await _press(pilot, "M")
        return [_painted_hint_line(screen)]


async def test_at066_pilot_hints_dispatch_through_the_mixin(tmp_path):
    """AT-066 (LLR-MOD.2.3, HLR-MOD.2): the key pressed is `M` — the `view`
    seat's `next incomplete` action, bound in `MapScreen.BINDINGS`.  The action
    jumps to node `b` (the seeded gap) and focuses its missing field; the
    `DescendantFocus` handler then paints the fill-in hint THROUGH the
    `HintsOps` mixin (`_field_hint`/`_seat_glyph`).  The painted hint line must
    equal the pre-B1 baseline, whose sha256 is pinned (PDR C4)."""
    assert any(b.key == "M" for b in MapScreen.BINDINGS), "M is no longer bound on MapScreen"
    painted = await _at066_capture(tmp_path)
    digest = hashlib.sha256(AT066_BASELINE.read_bytes()).hexdigest()
    assert digest == AT066_BASELINE_SHA256, (
        f"baseline {AT066_BASELINE.name} does not hash to the pinned record: {digest}"
    )
    baseline = AT066_BASELINE.read_text(encoding="utf-8").splitlines()
    assert painted == baseline, (painted, baseline)


_AT066_SUBPROCESS = r"""
import asyncio
import importlib.util
import sys

mut, repo, ws = sys.argv[1], sys.argv[2], sys.argv[3]
spec = importlib.util.spec_from_file_location(
    "test_mod_dispatch", repo + "/tests/test_mod_dispatch.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
lines = asyncio.run(module._at066_capture(__import__("pathlib").Path(ws)))
sys.stdout.write("\n".join(lines) + "\n")
"""


def test_at066_hints_dispatch_red_when_the_mixin_is_dropped(tmp_path):
    """AT-066's RED (C5 mechanism): a tmp copy of the package with `HintsOps`
    REMOVED from `MapScreen`'s bases is captured in a SUBPROCESS (`PYTHONPATH`
    on the copy, cwd = the copy so it wins).  Without the mixin the pressed
    `M` key's paint path (`self._field_hint()`) is gone, so the capture must
    DIFFER from the baseline or FAIL — a green mutant would mean the oracle
    cannot see the mixin at all."""
    mut = tmp_path / "mut"
    shutil.copytree(REPO_ROOT / "mapper", mut / "mapper")
    screen_py = mut / "mapper" / "screens" / "map" / "screen.py"
    source = screen_py.read_text(encoding="utf-8")
    # Drop HintsOps from MapScreen's bases whatever the other Spine B mixins are.
    mutated, n = re.subn(r"^(class MapScreen\([^)]*?)\bHintsOps,\s*", r"\1", source, count=1, flags=re.M)
    assert n == 1, "B1's composition (HintsOps among MapScreen's bases) is not on the tree"
    screen_py.write_text(mutated, encoding="utf-8")

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"  # the capture is UTF-8; Windows defaults to cp1252
    env["PYTHONPATH"] = os.pathsep.join(
        [str(mut), str(REPO_ROOT), env.get("PYTHONPATH", "")]
    )
    result = subprocess.run(
        [sys.executable, "-B", "-c", _AT066_SUBPROCESS,
         str(mut), str(REPO_ROOT), str(tmp_path / "ws")],
        capture_output=True, text=True, encoding="utf-8", env=env, timeout=180,
        cwd=mut,  # `-c` puts cwd first on sys.path: the mutant package must win
    )
    baseline = AT066_BASELINE.read_text(encoding="utf-8").splitlines()
    painted = result.stdout.splitlines()
    assert result.returncode != 0 or painted != baseline, (
        f"the mutant painted the baseline (rc={result.returncode}): {painted!r}"
    )
