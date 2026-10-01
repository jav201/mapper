"""The OS-handler boundary is countable (`docs/ARCHITECTURE.md` section 3, amended in Inc-9n, `A-122`).

Inbound ban, as reworded: `open_external` (and its launcher) is referenced only from `app`.  `github` and
`screens` may import `osopen.safe_local_path`, which decides on strings and launches nothing.  Derived from
the modules' own ASTs, so a new caller fails the test instead of passing a hand-listed expectation.
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
OPEN_STEPS: set[str] = {"arch"}


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


def test_outside_app_only_safe_local_path_is_imported_from_osopen():
    seen: dict[str, set[str]] = {}
    for rel, tree in _sources():
        if rel in ALLOWED_FILES:
            continue
        imports = list(_osopen_imports(tree))
        if imports:
            seen[rel] = {name for _, name in imports}
    assert seen, "the AST walk found no osopen import outside app: the probe is broken"
    assert all(names == {"safe_local_path"} for names in seen.values()), seen
    assert not any(rel.startswith(("widgets/", "views/")) for rel in seen), seen
    assert set(seen) == {"github.py", "screens/factory.py"}, set(seen)


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
    assert "`osopen.safe_local_path`" in screens_row, screens_row
    assert "`open_external` is referenced only from `app`" in osopen_row, osopen_row
    assert "`widgets` / `views` / `screens` → `osopen`" not in osopen_row, osopen_row
    github_src = ast.parse((PKG / "github.py").read_text(encoding="utf-8"))
    imported = {n.module for n in ast.walk(github_src) if isinstance(n, ast.ImportFrom) and n.level == 1}
    assert imported == {"darkside", "model", "osopen"}, imported
