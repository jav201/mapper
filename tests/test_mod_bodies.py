"""LLR-MOD.4.3 — the method-body oracle and the name-clean gate.

The modular batch moves every method of `MapScreen` (and the rest of
`mapper/app.py`) out of the monolith into new modules.  The risk is a move
that silently changes a body: the suite goes green, behaviour has drifted.
So this file pins, per increment:

(a) BYTE-IDENTICAL BODIES — every method of every class and every top-level
    function defined in `mapper/app.py` at Inc-0 is dumped with
    `ast.dump(node, include_attributes=False)` and compared against a
    baseline JSON captured on the pre-move tree.  The search for each key
    runs across ALL `*.py` under the package root, so after a move the same
    key is found in its new module.  A key found zero times (lost by a
    move) or more than once (duplicated by a move) is reported.

(b) NAME-CLEAN NEW MODULES — no module references an undefined global: a
    Name load that resolves to no module-level binding/import, no builtin,
    and no enclosing function/class scope binding.  Checked with `symtable`
    over `mapper/app.py` and every `mapper/screens/**/*.py`.

BASELINE FORMAT (`.dev-flow/2026-10-09-modular-batch/evidence/mod-bodies-baseline.json`):
a JSON object `{qualified_key: sha256_hex}` — keys sorted, values are the
sha256 of the `ast.dump` string (not the dump itself, to keep the evidence
file small).  Key format: `"<ClassName>.<method>"` for methods (immediate
enclosing class), `"<function>"` for top-level functions.  Regenerate with:

    python -B tests/test_mod_bodies.py

RED controls (both run on a tmp copy of the package, never the real tree):
a one-token mutation inside a `MapScreen` method body reddens the baseline
diff, and a deleted import reddens the undefined-global check.
"""
from __future__ import annotations

import ast
import builtins
import hashlib
import json
import shutil
import symtable
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "mapper"
BASELINE_PATH = REPO / ".dev-flow" / "2026-10-09-modular-batch" / "evidence" / "mod-bodies-baseline.json"

# Module dunders a scope may read without an explicit binding, plus the
# implicit `__class__` closure that zero-argument `super()` injects.
_DUNDERS = frozenset({
    "__name__", "__file__", "__doc__", "__package__", "__loader__", "__spec__",
    "__builtins__", "__annotations__", "__debug__", "__cached__", "__class__",
})
_KNOWN_GLOBALS = frozenset(dir(builtins)) | _DUNDERS


def _py_files(root: Path) -> list[Path]:
    """Every `*.py` under `root` (a package dir) or the file itself."""
    if root.is_file():
        return [root]
    return sorted(root.rglob("*.py"))


def _bodies_in_file(path: Path) -> dict[str, str]:
    """Qualified key -> `ast.dump` for each class method and top-level
    function defined in ONE file.  Nested classes key on their immediate
    class name, per the census format."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: dict[str, str] = {}

    def walk_body(body: list[ast.stmt], prefix: str) -> None:
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                found[prefix + node.name] = ast.dump(node, include_attributes=False)
            elif isinstance(node, ast.ClassDef):
                walk_body(node.body, node.name + ".")

    walk_body(tree.body, "")
    return found


def method_occurrences(root: Path) -> dict[str, list[str]]:
    """Key -> every dump found for it across ALL `*.py` under `root`.

    A list longer than one means the move duplicated a definition; a key
    the baseline carries that is absent here was found zero times.
    """
    # Spine B (2026-10-09-modular-batch) composes `MapScreen` from plain mixins:
    # a method moved into `class HintsOps` is still `MapScreen.<name>` for the
    # census.  The mixin set is DERIVED from `MapScreen`'s own bases under
    # `root` (so a tmp-copy mutant is judged by its own tree), never hand-listed.
    mixins = _map_screen_mixins(root)
    found: dict[str, list[str]] = {}
    for path in _py_files(root):
        for key, dump in _bodies_in_file(path).items():
            cls, _, name = key.rpartition(".")
            if cls in mixins:
                key = f"MapScreen.{name}"
            found.setdefault(key, []).append(dump)
    return found


def _map_screen_mixins(root: Path) -> set[str]:
    """Names of the classes `MapScreen` inherits from, other than Textual's."""
    names: set[str] = set()
    for path in _py_files(root):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ClassDef) and node.name == "MapScreen":
                names |= {b.id for b in node.bases if isinstance(b, ast.Name)} - {"Screen"}
    return names


def method_dumps(root: Path) -> dict[str, str]:
    """Key -> `ast.dump`, requiring every key to occur exactly once under
    `root`.  Keys found more than once are reported (raised), never
    silently collapsed."""
    found = method_occurrences(root)
    duplicated = sorted(k for k, v in found.items() if len(v) > 1)
    if duplicated:
        raise ValueError(f"keys found more than once under {root}: {duplicated}")
    return {k: v[0] for k, v in found.items()}


def baseline_diff(root: Path, baseline: dict[str, str]) -> dict[str, list[str]]:
    """The whole oracle as one report: baseline keys found zero times
    (`missing`), more than once (`duplicated`), or with a body whose dump
    no longer hashes to the baseline (`changed`).  Empty lists == pass."""
    found = method_occurrences(root)
    return {
        "missing": sorted(k for k in baseline if not found.get(k)),
        "duplicated": sorted(k for k in baseline if len(found.get(k, [])) > 1),
        "changed": sorted(
            k for k, v in found.items()
            if k in baseline and len(v) == 1
            and hashlib.sha256(v[0].encode()).hexdigest() != baseline[k]
        ),
    }


def _screens_modules(root: Path) -> list[str]:
    """`screens/**/*.py` as dotted module names relative to the package."""
    return [
        ".".join(p.relative_to(root).with_suffix("").parts)
        for p in sorted(root.glob("screens/**/*.py"))
    ]


def undefined_globals(root: Path, modules: list[str]) -> dict[str, set[str]]:
    """Per module, the Name loads that resolve to nothing: no module-level
    binding/import, no builtin, no enclosing function/class scope binding
    (free variables are followed to their binding by `symtable`)."""
    result: dict[str, set[str]] = {}
    for module in modules:
        path = root.joinpath(*module.split(".")).with_suffix(".py")
        top = symtable.symtable(
            path.read_text(encoding="utf-8"), str(path), "exec"
        )
        bound = {
            s.get_name()
            for s in top.get_symbols()
            if s.is_assigned() or s.is_imported() or s.is_namespace()
        }
        undefined: set[str] = set()

        def visit(tab: symtable.SymbolTable) -> None:
            for symbol in tab.get_symbols():
                if (
                    symbol.is_referenced()
                    and not symbol.is_free()  # resolves in an enclosing scope
                    and not symbol.is_assigned()
                    and not symbol.is_imported()
                    and not symbol.is_namespace()
                    and not symbol.is_parameter()
                ):
                    name = symbol.get_name()
                    if name not in bound and name not in _KNOWN_GLOBALS:
                        undefined.add(name)
            for child in tab.get_children():
                visit(child)

        visit(top)
        result[module] = undefined
    return result


def _load_baseline() -> dict[str, str]:
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


def _mutate_method_token(src: str, qualname: str) -> tuple[str, str]:
    """One-token mutation: rename the first loaded Name inside the named
    method to `<name>_mut`.  Returns (mutated source, mutated name)."""
    tree = ast.parse(src)
    target: ast.AST | None = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                key = f"{node.name}.{item.name}" if isinstance(
                    item, (ast.FunctionDef, ast.AsyncFunctionDef)
                ) else None
                if key == qualname:
                    target = item
    assert target is not None, f"{qualname} not found"
    for node in ast.walk(target):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id != "self":
            lines = src.splitlines(keepends=True)
            line = lines[node.lineno - 1]
            assert node.end_col_offset is not None
            lines[node.lineno - 1] = (
                line[: node.col_offset] + node.id + "_mut" + line[node.end_col_offset:]
            )
            return "".join(lines), node.id
    raise AssertionError(f"no loadable Name inside {qualname}")


def _delete_a_used_import(src: str) -> tuple[str, str]:
    """Delete one import statement whose binding is used inside a nested
    scope (the real-tree modules are clean, so any such deletion must be
    reported).  Returns (mutated source, deleted name)."""
    tree = ast.parse(src)
    for stmt in tree.body:
        if not isinstance(stmt, (ast.Import, ast.ImportFrom)):
            continue
        names = [a.asname or a.name.split(".")[0] for a in stmt.names]
        top = symtable.symtable(src, "<copy>", "exec")
        used_nested = {
            symbol.get_name()
            for tab in top.get_children()
            for symbol in tab.get_symbols()
            if symbol.is_referenced()
            and not symbol.is_free()
            and not symbol.is_assigned()
            and symbol.is_global()
        }
        for name in names:
            if name in used_nested:
                lines = src.splitlines(keepends=True)
                assert stmt.end_lineno is not None
                del lines[stmt.lineno - 1: stmt.end_lineno]
                return "".join(lines), name
    raise AssertionError("no import used inside a nested scope found")


def test_llr_mod_4_3_bodies_match_baseline():
    """Every Inc-0 census body is byte-identical and appears exactly once
    somewhere in the package: no method lost, duplicated or edited by a
    move.  Diff must be empty (missing / duplicated / changed all none)."""
    diff = baseline_diff(PACKAGE, _load_baseline())
    assert diff == {"missing": [], "duplicated": [], "changed": []}


def test_llr_mod_4_3_no_undefined_globals():
    """`app.py` and every `screens/` module resolve every Name load:
    0 undefined-global references anywhere in the scanned set."""
    modules = ["app"] + _screens_modules(PACKAGE)
    result = undefined_globals(PACKAGE, modules)
    dirty = {module: sorted(names) for module, names in result.items() if names}
    assert dirty == {}


def test_llr_mod_4_3_red_one_token_body_mutation_reddens_the_diff(tmp_path):
    """Negative control on a tmp copy: rename one Name inside a MapScreen
    method body — the baseline diff must come back non-empty, proving the
    oracle sees a one-token drift, not just wholesale loss."""
    import inspect

    from mapper.app import MapScreen

    copy = tmp_path / "mapper"
    shutil.copytree(PACKAGE, copy)
    # The file MapScreen lives in is DERIVED, not named: B0 moved it out of
    # `app.py` and Spine B spreads its methods further (2026-10-09-modular-batch).
    rel = Path(inspect.getfile(MapScreen)).resolve().relative_to(PACKAGE.resolve())
    target = copy / rel
    src = target.read_text(encoding="utf-8")
    methods = sorted(k for k in _bodies_in_file(target) if k.startswith("MapScreen."))
    assert methods, "the Inc-0 census must contain MapScreen methods"
    mutated, name = _mutate_method_token(src, methods[0])
    target.write_text(mutated, encoding="utf-8")

    diff = baseline_diff(copy, _load_baseline())
    assert diff["changed"], f"mutation of {name} went undetected: {diff}"
    assert not diff["missing"] and not diff["duplicated"]


def test_llr_mod_4_3_red_a_deleted_import_reddens_undefined_globals(tmp_path):
    """Negative control on a tmp copy: delete one import whose binding is
    used inside a nested scope — the name-clean check must report it."""
    copy = tmp_path / "mapper"
    copy.mkdir()
    (copy / "app.py").write_text(
        (PACKAGE / "app.py").read_text(encoding="utf-8"), encoding="utf-8"
    )
    app_py = copy / "app.py"
    mutated, name = _delete_a_used_import(app_py.read_text(encoding="utf-8"))
    app_py.write_text(mutated, encoding="utf-8")

    result = undefined_globals(copy, ["app"])
    assert name in result["app"], f"deleting {name} went undetected: {result}"


if __name__ == "__main__":
    # Baseline capture (Inc-0, pre-move tree): the census universe is what
    # `mapper/app.py` defines TODAY; values are sha256(ast.dump) so the
    # evidence file stays small.  Keys are written sorted.
    dumps = method_dumps(PACKAGE / "app.py")
    baseline = {
        key: hashlib.sha256(dumps[key].encode()).hexdigest() for key in sorted(dumps)
    }
    BASELINE_PATH.write_text(
        json.dumps(baseline, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"{len(baseline)} keys -> {BASELINE_PATH}")
