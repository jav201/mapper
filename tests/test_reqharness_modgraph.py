"""ARCH C3 (DDR follow-up) — the reqharness module graph is acyclic at
every scope: no module under `mapper/reqharness` imports a module that
imports it back.

The census is derived from the shipped ASTs — every import of one
reqharness module by another, at ANY scope (module level, function body,
`if TYPE_CHECKING:` block), either import form — and asserts no pair of
modules has edges in both directions.  Before the DDR fix the walk found
exactly one back-edge: `chain` reached `pending`'s validator through a
function-local import while `pending` imported `PENDING_DIR` /
`read_event_file` / `ChainReport` from `chain` at module level.  The fix
moved the shared pieces (`PENDING_DIR`, the confined event-file reader,
the pending schema + `load_pending` validator) down into `config.py` (the
leaf both import from); `chain` now imports the validator at module level
and `pending` holds only a type-checking import of `ChainReport`.

Negative control (permanent): a planted function-local back-import on a
tmp copy of the package is reported — the census is not vacuous.
"""
from __future__ import annotations

import ast
import pathlib
import shutil

import pytest

import mapper

PKG = pathlib.Path(mapper.__file__).parent / "reqharness"


def _reqharness_imports(tree: ast.AST, own: str) -> set[str]:
    """The reqharness module tails *tree* imports, at any scope and in
    either form (`from mapper.reqharness.chain import X`,
    `from mapper.reqharness import chain`, `import mapper.reqharness.chain`,
    and relative `from .chain import X`)."""
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "mapper.reqharness":
                found.update(a.name for a in node.names)
            elif module.startswith("mapper.reqharness."):
                found.add(module.split(".")[2])
            elif node.level and module.split(".")[-1] not in ("", own):
                # `from . import chain` / `from .chain import X`
                if module:
                    found.add(module.split(".")[0])
                else:
                    found.update(a.name for a in node.names)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                if parts[:2] == ["mapper", "reqharness"] and len(parts) >= 3:
                    found.add(parts[2])
    found.discard(own)
    return found


def _back_edges(root: pathlib.Path) -> dict[str, set[str]]:
    """`module -> {modules it imports that import it back}` — empty when the
    graph has no two-way pair (GREEN)."""
    graphs: dict[str, set[str]] = {}
    for path in sorted(root.glob("*.py")):
        if path.name == "__init__.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        graphs[path.stem] = _reqharness_imports(tree, path.stem)
    bad = {
        mod: {other for other in targets if mod in graphs.get(other, set())}
        for mod, targets in graphs.items()
    }
    return {mod: others for mod, others in bad.items() if others}


def test_no_reqharness_module_imports_a_module_that_imports_it_back(tmp_path):
    """ARCH C3: the static AST census over the shipped tree — zero two-way
    import pairs at any scope.  On the pre-fix tree this found
    `chain -> pending` (function-local) against `pending -> chain`
    (module level)."""
    bad = _back_edges(PKG)
    assert bad == {}, f"reqharness import cycle(s): {bad}"
    # the graph must not be empty either: the probe must see real edges
    graph = {
        path.stem: _reqharness_imports(
            ast.parse(path.read_text(encoding="utf-8")), path.stem
        )
        for path in sorted(PKG.glob("*.py"))
        if path.name != "__init__.py"
    }
    assert any(graph.values()), "the census saw no edges at all: vacuous"


def test_the_census_catches_a_planted_function_local_back_import(tmp_path):
    """Negative control: restoring the pre-fix shape — a function-local
    `from mapper.reqharness.pending import list_pending` in `chain.py`,
    against `pending`'s module-level (type-checking) edge to `chain` — is
    reported."""
    mutant = tmp_path / "reqharness"
    shutil.copytree(PKG, mutant, ignore=shutil.ignore_patterns("__pycache__"))
    target = mutant / "chain.py"
    target.write_text(
        target.read_text(encoding="utf-8")
        + "\n\ndef _planted_scope_probe():\n"
        "    from mapper.reqharness.pending import list_pending  # planted defect\n"
        "    return list_pending\n",
        encoding="utf-8",
    )
    bad = _back_edges(mutant)
    assert bad, "the planted back-import was not reported"
    assert "chain" in bad and "pending" in bad["chain"], bad
