"""B-103 hygiene (LLR-001.1 / LLR-001.2 of `2026-10-09-hygiene-batch`).

WHY: two failure modes that break silently.

- LLR-001.1: `_last_save_error` was read through
  `getattr(self, "_last_save_error", "")` in `_save_draft`, so a future rename
  of the slot (or a typo at the write in `_save_or_toast`) degrades to the
  word `error` in the toast and no test can tell.  The slot must be declared
  on `MapScreen` and read directly.  (The AST read-side check cannot see a
  read through `vars()` / `__dict__`; that is accepted as out of scope.)
- LLR-001.2: `action_quit` reached across classes into `screen._draft_guard_open`,
  a private of `MapScreen`; a rename on either side breaks silently.  The quit
  walk must go through a public `guard_open()`.
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path

import mapper
from mapper.app import MapperApp, MapScreen

from tests.test_draft_save import (
    WIDE,
    _answer,
    _guards,
    _open,
    _press,
    _seed_map,
    _type_into,
)


def _package_dir() -> Path:
    return Path(mapper.__file__).resolve().parent


def _all_sources() -> dict[Path, ast.AST]:
    return {
        path: ast.parse(path.read_text(encoding="utf-8"))
        for path in sorted(p.resolve() for p in _package_dir().rglob("*.py"))
    }


def _find_class(tree: ast.AST, name: str) -> ast.ClassDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    raise AssertionError(f"class {name} not found")


def _class_tree(cls: type) -> ast.AST:
    """Parse the file that declares `cls`, located BY CONTENT (LLR-MOD.5.1).

    The class name is searched across every module source in the package
    and must have EXACTLY ONE home: a definition duplicated into a second
    file -- or dropped from the tree -- reddens here instead of the AST pin
    quietly following one copy.  That single home must also be the file
    `inspect.getfile` reports for the live class, so the pin cannot drift
    onto a same-named class the imported object does not use.
    """
    sources = _all_sources()
    homes = sorted(
        path for path, tree in sources.items()
        if any(
            isinstance(node, ast.ClassDef) and node.name == cls.__name__
            for node in ast.walk(tree)
        )
    )
    assert len(homes) == 1, f"{cls.__name__} resolves to {len(homes)} homes: {homes}"
    declared = Path(inspect.getfile(cls)).resolve()
    assert homes[0] == declared, (homes[0], declared)
    return sources[homes[0]]


async def test_llr_001_1_last_save_error_is_declared_none_before_any_save(tmp_path):
    """The slot exists on a fresh screen and starts None: a screen that never
    saved has no error to name, so nothing may leak a stale `error` word."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed_map(app))
        assert screen._last_save_error is None


def test_llr_001_1_last_save_error_is_declared_and_never_read_through_getattr():
    """AST: `MapScreen.__init__` declares the slot (an AnnAssign), and NO module
    in the package reads it through `getattr`.  A `getattr` default would hide a
    renamed slot as the word `error`.  Not detected: a read via `vars()` /
    `__dict__` lookup."""
    tree = _class_tree(MapScreen)
    init = next(
        n for n in _find_class(tree, "MapScreen").body
        if isinstance(n, ast.FunctionDef) and n.name == "__init__"
    )
    targets = [
        n.target for n in ast.walk(init)
        if isinstance(n, ast.AnnAssign)
        and isinstance(n.target, ast.Attribute)
        and n.target.attr == "_last_save_error"
    ]
    assert targets, "MapScreen.__init__ declares no _last_save_error AnnAssign"

    for path, source in _all_sources().items():
        for node in ast.walk(source):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            if node.func.id != "getattr":
                continue
            consts = [a.value for a in node.args if isinstance(a, ast.Constant)]
            assert "_last_save_error" not in consts, (path, node.lineno)


async def test_llr_001_2_guard_open_follows_the_guard(tmp_path):
    """Real keys (the sequence of test_pdr_c1_quit_while_a_node_guard_is_open_...
    in test_draft_exits.py): `escape` with no guard up closes nothing,
    `j` opens the node guard and `guard_open()` follows, answering `escape`
    (stay) closes it and `guard_open()` follows back."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed_map(app))
        await _type_into(pilot, screen, "insp-title", "x")
        await _press(pilot, "escape")
        assert screen.guard_open() is False
        await _press(pilot, "j")
        assert _guards(app) == 1
        assert screen.guard_open() is True
        await _answer(app, pilot, "escape")
        assert screen.guard_open() is False


def test_llr_001_2_no_read_of_the_guard_flag_outside_map_screen():
    """AST: every attribute access named `_draft_guard_open` lies inside the
    `MapScreen` class body (its declaration, `_guard_draft`, `guard_open`);
    the private is not read across classes.  And `MapperApp.action_quit` calls
    the public `guard_open()`."""
    class _Track(ast.NodeVisitor):
        def __init__(self, path: Path):
            self.path = path
            self.enclosing: list[str] = []

        def visit_ClassDef(self, node: ast.ClassDef):
            self.enclosing.append(node.name)
            self.generic_visit(node)
            self.enclosing.pop()

        def visit_Attribute(self, node: ast.Attribute):
            if node.attr == "_draft_guard_open":
                assert self.enclosing == ["MapScreen"], (self.path, node.lineno, self.enclosing)
            self.generic_visit(node)

    for path, source in _all_sources().items():
        _Track(path).visit(source)

    app_tree = _class_tree(MapperApp)
    action_quit = next(
        n for n in _find_class(app_tree, "MapperApp").body
        if isinstance(n, ast.FunctionDef) and n.name == "action_quit"
    )
    calls = [
        node.func.attr for node in ast.walk(action_quit)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
    ]
    assert "guard_open" in calls, "action_quit does not call guard_open()"
