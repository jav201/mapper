"""The OS-handler boundary is countable (`docs/ARCHITECTURE.md` section 3, amended in Inc-9n, `A-122`).

Inbound ban, as reworded: `open_external` (and its launcher) is referenced only from `app`.  `github` may import
`osopen.safe_local_path`; `screens` that name plus `confine`, `lexically_outside` and the sentence constant
`PATH_NOT_SUPPORTED` (Inc-9o, `A-123`): none of them launches anything.  Derived from the modules' own ASTs, so
a new caller fails the test instead of passing a hand-listed expectation.
"""
from __future__ import annotations

import ast
import pathlib
import re

import pytest

import mapper

PKG = pathlib.Path(mapper.__file__).parent
DOCS = PKG.parent / "docs" / "ARCHITECTURE.md"
LAUNCH_NAMES = {"open_external", "_default_launcher", "startfile"}
ALLOWED_FILES = {"app.py", "osopen.py"}
OPEN_STEPS: set[str] = set()


def red(step: str):
    if step in OPEN_STEPS:
        return pytest.mark.xfail(
            strict=True, reason=f"Inc-9n: committed RED; closed by the '{step}' step")
    return lambda fn: fn


def _sources():
    for path in sorted(PKG.rglob("*.py")):
        yield path.relative_to(PKG).as_posix(), ast.parse(path.read_text(encoding="utf-8"))


def _names(tree: ast.AST) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            found.add(node.id)
        elif isinstance(node, ast.Attribute):
            found.add(node.attr)
        elif isinstance(node, ast.alias):
            found.add(node.name.split(".")[-1])
            if node.asname:
                found.add(node.asname)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            found.add(node.name)
    return found


def test_the_launcher_names_appear_only_in_app_and_osopen():
    referencing = {rel for rel, tree in _sources() if _names(tree) & LAUNCH_NAMES}
    assert referencing == ALLOWED_FILES, referencing


def _osopen_imports(tree: ast.AST):
    """(module-tail, imported name) for every import of the `osopen` module, relative or absolute."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            tail = (node.module or "").split(".")[-1]
            if tail == "osopen":
                for alias in node.names:
                    yield "from", alias.name
            elif tail in ("mapper", "") and any(a.name == "osopen" for a in node.names):
                yield "module", "osopen"
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[-1] == "osopen":
                    yield "module", alias.name


ALLOWED_OUTSIDE_APP = {
    "github.py": {"safe_local_path"},
    "screens/factory.py": {"safe_local_path", "confine", "lexically_outside", "PATH_NOT_SUPPORTED"},
}


@red("arch")
def test_outside_app_only_the_allowed_names_are_imported_from_osopen():
    seen: dict[str, set[str]] = {}
    for rel, tree in _sources():
        if rel in ALLOWED_FILES:
            continue
        imports = list(_osopen_imports(tree))
        if imports:
            seen[rel] = {name for _, name in imports}
    assert seen, "the AST walk found no osopen import outside app: the probe is broken"
    assert seen == ALLOWED_OUTSIDE_APP, seen
    assert not any(rel.startswith(("widgets/", "views/")) for rel in seen), seen
    assert not any(n in seen["github.py"] | seen["screens/factory.py"] for n in LAUNCH_NAMES), seen


def _back_edges() -> dict[str, list[int]]:
    """The `from mapper.app import ...` sites (a `screens` -> `app` back-edge), by file, with their lines."""
    found: dict[str, list[int]] = {}
    for rel, tree in _sources():
        if not rel.startswith("screens/"):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (node.module == "mapper.app" or (
                    node.level and (node.module or "") == "app")):
                found.setdefault(rel, []).append(node.lineno)
    return {rel: sorted(lines) for rel, lines in found.items()}


@red("arch")
def test_the_four_known_back_edges_are_exactly_the_ones_the_map_lists():
    edges = _back_edges()
    assert {rel: len(lines) for rel, lines in edges.items()} == {"screens/factory.py": 3, "screens/settings.py": 1}, edges
    row = _row(_section3(), "screens")
    for rel, lines in edges.items():
        for line in lines:
            assert f"`mapper/{rel}:{line}`" in row, (rel, line, row)
    assert "factory.py:343" not in row, row


def _row(table_text: str, module: str) -> str:
    match = re.search(rf"^\| `{module}` \|.*$", table_text, re.MULTILINE)
    assert match, module
    return match.group(0)


def _section3() -> str:
    text = DOCS.read_text(encoding="utf-8")
    return text[text.index("## 3 "):text.index("## 4 ")]


@red("arch")
def test_the_architecture_map_says_what_the_modules_import():
    section = _section3()
    github_row = _row(section, "github")
    screens_row = _row(section, "screens")
    osopen_row = _row(section, "osopen")
    assert "`osopen.safe_local_path`" in github_row and "`design`" in github_row, github_row
    for name in ("safe_local_path", "confine", "lexically_outside", "PATH_NOT_SUPPORTED"):
        assert f"`osopen.{name}`" in screens_row, (name, screens_row)
    assert "`open_external` is referenced only from `app`" in osopen_row, osopen_row
    assert "`widgets` / `views` / `screens` → `osopen`" not in osopen_row, osopen_row
    github_src = ast.parse((PKG / "github.py").read_text(encoding="utf-8"))
    imported = {n.module for n in ast.walk(github_src) if isinstance(n, ast.ImportFrom) and n.level == 1}
    assert imported == {"darkside", "model", "osopen"}, imported
