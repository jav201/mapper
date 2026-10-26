"""HLR-RVT.1 / LLR-RVT.1.1-.1.3 -- the presentation leaf (`PDR-2026-10-25-relmap-r2-batch#D2`).

One definition site and one import path for `cut`, `DISPLAY_MAX` and
`refusal_line`, and the move changes no rendered byte.  Every property is
DERIVED from the shipped tree by AST (C-31); each checker is a FUNCTION of
source text so a planted-violation arm proves it can report a failure.

Per the orchestrator ruling at the PDR seal (COND-ARCH-2/COND-QA-1,
`LED-2026-10-25-r2.16`) the re-points land in two trunk increments:
Inc-1a re-points `model`/`descriptor`/`audit` (this file's census arm
`test_no_old_path_readers_inc_1a` names those three paths; the one remaining
old-path reader, `relmap.model.cut` at `adapter.py`, is re-pointed in Inc-1b
and its census arm lands there), Inc-1b re-points `adapter`.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

import mapper
from mapper.relmap.descriptor import CAUSE
from mapper.relmap.text import DISPLAY_MAX, K5_CAUSE, cut, refusal_line

PKG = Path(mapper.__file__).resolve().parent
RELMAP = PKG / "relmap"
TESTS = PKG.parent / "tests"

DEFINED = ("cut", "refusal_line", "DISPLAY_MAX")
#: the old import paths Inc-1a re-points; `relmap.model.cut` (the adapter reader)
#: is Inc-1b's arm, added to this table by that increment
OLD_PATHS_1A = (
    ("mapper.relmap.model", "DISPLAY_MAX"),
    ("mapper.relmap.descriptor", "refusal_line"),
    ("mapper.relmap.audit", "refusal_line"),
)
DOTTED_1A = re.compile(
    r"mapper\.relmap\.model\.(?:cut|DISPLAY_MAX)"
    r"|mapper\.relmap\.(?:descriptor|audit)\.refusal_line"
)


def _relmap_sources() -> dict[str, str]:
    """Every module file under `mapper/` (N-2, independent review: the census
    width now matches the packet claim — the whole tree, not the package)."""
    return {
        p.relative_to(PKG).as_posix(): p.read_text(encoding="utf-8")
        for p in sorted(PKG.rglob("*.py"))
    }


def _definitions(name: str) -> list[str]:
    """Module files under `mapper/` that DEFINE `name` (a `def`, or an
    assignment for the constant)."""
    found = []
    for fname, source in _relmap_sources().items():
        for node in ast.walk(ast.parse(source, filename=fname)):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
                found.append(fname)
            elif name == "DISPLAY_MAX" and isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "DISPLAY_MAX":
                        found.append(fname)
    return found


def _old_path_readers(old_paths) -> list[str]:
    """Every import statement anywhere in `mapper/` or `tests/` that names an
    (module, name) old path, as `file:line`."""
    hits = []
    for path in sorted(PKG.rglob("*.py")) + sorted(TESTS.rglob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or not node.module:
                continue
            for alias in node.names:
                if (node.module, alias.name) in old_paths:
                    rel = path.relative_to(PKG.parent).as_posix()
                    hits.append(f"{rel}:{node.lineno} {node.module}.{alias.name}")
    return hits


def _dotted_references(pattern) -> list[str]:
    """Source-level hits for the dotted old paths inside the `relmap` package
    (attribute-form readers the import census cannot see).  Tests are covered
    by the import census and by running them; scanning test sources here would
    flag this file's own planted-violation strings."""
    hits = []
    for path in sorted(RELMAP.glob("*.py")):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if pattern.search(line):
                hits.append(f"mapper/relmap/{path.name}:{lineno} {line.strip()}")
    return hits


# ------------------------------------------------------------------ LLR-RVT.1.1 (one site per name)


@pytest.mark.parametrize("name", DEFINED)
def test_one_definition_site_per_primitive(name):
    assert _definitions(name) == ["relmap/text.py"], name


@pytest.mark.parametrize(
    "planted",
    [
        "def cut(text):\n    return text\n",
        "DISPLAY_MAX = 120\n",
        "def refusal_line(base_name, cause, limit=None):\n    return cause\n",
    ],
)
def test_definition_census_finds_a_second_site(planted):
    assert len(_definitions_in(planted, "model.py")) == 1


def _definitions_in(source: str, fname: str) -> list[str]:
    found = []
    for node in ast.walk(ast.parse(source, filename=fname)):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in DEFINED:
            found.append(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in DEFINED:
                    found.append(target.id)
    return found


def test_the_leaf_imports_nothing():
    tree = ast.parse((RELMAP / "text.py").read_text(encoding="utf-8"), filename="text.py")
    imports = [
        n for n in tree.body
        if isinstance(n, (ast.Import, ast.ImportFrom))
        and not (isinstance(n, ast.ImportFrom) and n.module == "__future__")
    ]
    assert imports == [], "text.py is the stdlib-only leaf: it imports nothing but __future__"


# ------------------------------------------------------------------ LLR-RVT.1.2 (one import path)


def test_no_old_path_readers_inc_1a():
    assert _old_path_readers(OLD_PATHS_1A) == []


def test_no_dotted_old_path_references_inc_1a():
    assert _dotted_references(DOTTED_1A) == []


def _audit_all_listing() -> list[str]:
    """`audit.py`'s `__all__` as written, parsed from source -- the module is
    NOT imported here: mid-move (Inc-1a) it is unimportable on purpose, its
    `adapter` dependency being the old-path reader Inc-1b re-points."""
    tree = ast.parse((RELMAP / "audit.py").read_text(encoding="utf-8"), filename="audit.py")
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    return [elt.value for elt in node.value.elts if isinstance(elt, ast.Constant)]
    raise AssertionError("audit.py carries no module-level __all__")


def test_audit_all_drops_the_refusal_line_reexport():
    assert "refusal_line" not in _audit_all_listing()


#: the old import path Inc-1b re-points (the adapter reader, declared at Inc-1a)
OLD_PATHS_1B = (
    ("mapper.relmap.model", "cut"),
)


def test_no_old_path_readers_inc_1b():
    assert _old_path_readers(OLD_PATHS_1B) == []


def test_audit_and_adapter_import_the_leaf_for_own_use():
    """One import path, at runtime: the re-pointed consumers hold the leaf's
    objects, and the old attribute path on `model` is gone."""
    import mapper.relmap.adapter as relmap_adapter
    import mapper.relmap.audit as relmap_audit
    from mapper.relmap import model as relmodel
    from mapper.relmap import text

    assert relmap_adapter.cut is text.cut
    assert relmap_audit.cut is text.cut
    assert relmap_audit.refusal_line is text.refusal_line
    assert not hasattr(relmodel, "cut")
    assert not hasattr(relmodel, "DISPLAY_MAX")


def test_reader_census_finds_a_planted_old_path_reader():
    planted = "def f():\n    from mapper.relmap.descriptor import refusal_line\n    return refusal_line\n"
    assert _old_path_readers_in(planted) == ["2: mapper.relmap.descriptor.refusal_line"]


def _old_path_readers_in(source: str) -> list[str]:
    hits = []
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue
        for alias in node.names:
            if (node.module, alias.name) in OLD_PATHS_1A:
                hits.append(f"{node.lineno}: {node.module}.{alias.name}")
    return hits


# ------------------------------------------------------------------ LLR-RVT.1.3 (no rendered byte changes)


def test_cut_reproduces_the_r1_contract():
    assert DISPLAY_MAX == 120
    assert cut("") == ""
    assert cut("a" * 120) == "a" * 120
    cut121 = cut("a" * 121)
    assert len(cut121) == 120 and cut121.endswith("…") and cut121[:-1] == "a" * 119
    assert len(cut("b" * 1_000_000)) == 120


def test_refusal_line_reproduces_the_r1_contract():
    # N-1 (independent review): fail at the drift site, one derivation
    # upstream of the rendered-bytes guards below.
    assert K5_CAUSE == CAUSE["K5"]
    assert refusal_line("a.relmap.yml", CAUSE["K1"]) == (
        "structure: refused (a.relmap.yml): is a link - descriptor skipped"
    )
    assert refusal_line("a.relmap.yml", CAUSE["K5"], 123) == (
        "structure: refused (a.relmap.yml): exceeds the 123 byte limit - descriptor skipped"
    )
    assert "exceeds the byte limit" in refusal_line("a.relmap.yml", CAUSE["K5"])
    long = refusal_line("n" * 300, CAUSE["K1"])
    assert len(long) <= len("structure: refused (): ") + 120 + len(": is a link - descriptor skipped")
    assert "…" in long
