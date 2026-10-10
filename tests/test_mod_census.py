"""LLR-MOD.7.2 (HLR-MOD.7): the ARCHITECTURE §4 F1/F2 freeze made mechanical.

`docs/ARCHITECTURE.md` §4 freezes the MapScreen contract in two tables: F1
(the 30-attribute state roster — no attribute gains a writer concern, no new
cross-concern attribute) and F2 (the cross-concern method surface — names and
signatures frozen).  The batch archive froze the pre-split reality of both in
`.dev-flow/2026-10-09-modular-batch/spike/census.json`, produced by the
throwaway `ast_census.py` over the single pre-split `MapScreen`.

WHY this test exists: the split is done by CUT/PASTE, so any later lane edit
that adds a writer to a shared attribute, adds a cross-concern call, or
loses/adds a method is SILENT — the suite can stay green while the freeze
drifts.  LLR-MOD.7.2 therefore re-runs the census over the SHIPPED PACKAGE
(`MapScreen` core class + every mixin base, derived from the `MapScreen` bases
under the package root being scanned — never hand-listed) and diffs it against
the frozen `census.json`:

* the SET of method names must be equal, and
* per method, `reads` / `writes` / `calls` of `self.<attr>` and other
  `MapScreen` methods must be equal (same AST definitions as `ast_census.py`;
  `first_line` / `line_count` are move artifacts and are ignored).

So an attribute gaining a writer, a new cross-concern call, or a lost/added
method is RED without a census amendment.  GREEN runs the checker on the real
tree; each `red_*` node plants one defect in a tmp copy of the package and
asserts the drift report catches it — a permanent executable negative control
(LLR-MOD.7.2's "Negative control" block).
"""
from __future__ import annotations

import ast
import re
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MAP_PKG = REPO_ROOT / "mapper" / "screens" / "map"
CENSUS_JSON = (
    REPO_ROOT / ".dev-flow" / "2026-10-09-modular-batch" / "spike" / "census.json"
)


# ---------------------------------------------------------------------------
# Method census — the read/write/call definitions are copied verbatim from
# `.dev-flow/2026-10-09-modular-batch/spike/ast_census.py` so the diff against
# its `census.json` output is definition-identical.
# ---------------------------------------------------------------------------

def _qual_name(node):
    """Dotted name for Attribute/Name, None otherwise."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


class _MethodCensus(ast.NodeVisitor):
    """Collect, for one function body: self-attr reads/writes and self-method calls."""

    def __init__(self):
        self.reads = set()
        self.writes = set()
        self.calls = set()  # other methods called via self.<m>(
        self._local_scopes = []

    def visit_FunctionDef(self, node):
        if self._local_scopes:
            self._local_scopes[-1].add(node.name)
        self._local_scopes.append(set())
        for a in node.args.args + node.args.kwonlyargs:
            self._local_scopes[-1].add(a.arg)
        if node.args.vararg:
            self._local_scopes[-1].add(node.args.vararg.arg)
        if node.args.kwarg:
            self._local_scopes[-1].add(node.args.kwarg.arg)
        self.generic_visit(node)
        self._local_scopes.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, node):
        self._local_scopes.append(set())
        for a in node.args.args:
            self._local_scopes[-1].add(a.arg)
        self.generic_visit(node)
        self._local_scopes.pop()

    def visit_ExceptHandler(self, node):
        self._local_scopes.append(set())
        if node.name:
            self._local_scopes[-1].add(node.name)
        for stmt in node.body:
            self.visit(stmt)
        self._local_scopes.pop()

    def _is_local(self, name):
        return any(name in s for s in self._local_scopes)

    def visit_Attribute(self, node):
        qn = _qual_name(node)
        if qn and qn.startswith("self."):
            attr = qn.split(".", 1)[1]
            # writes: only direct self.x = / self.x += etc, not self.x.y =
            if isinstance(node.ctx, (ast.Store, ast.Del)):
                if "." not in attr:
                    self.writes.add(attr)
                else:
                    # self.x.y = z writes self.x's contents; count x as read
                    self.reads.add(attr.split(".")[0])
            elif isinstance(node.ctx, ast.Load):
                self.reads.add(attr.split(".")[0])
        self.generic_visit(node)

    def visit_Call(self, node):
        # self.method(...) call
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "self"
        ):
            self.calls.add(node.func.attr)
        self.generic_visit(node)


# ---------------------------------------------------------------------------
# Structural checkers — each takes the map package root, so GREEN tests run
# them on the real tree and RED tests on a tmp-copy mutant (the tmp copy is
# judged by its own derived mixin set, never a hand-listed one).
# ---------------------------------------------------------------------------

def _mixin_names(pkg: Path) -> set[str]:
    """`MapScreen`'s own bases minus Textual's `Screen` — the derived mixin set."""
    tree = ast.parse((pkg / "screen.py").read_text(encoding="utf-8"))
    core = next(
        n
        for n in tree.body
        if isinstance(n, ast.ClassDef) and n.name == "MapScreen"
    )
    names = set()
    for base in core.bases:
        if isinstance(base, ast.Name):
            names.add(base.id)
        elif isinstance(base, ast.Attribute):
            names.add(base.attr)
    names.discard("Screen")
    return names


def census_of_mapscreen(pkg: Path) -> dict[str, dict[str, set[str]]]:
    """Package-aware census: `MapScreen` core class + every mixin base.

    Returns {method_name: {"reads": set, "writes": set, "calls": set}} with
    the same definitions as `ast_census.py`.  The class set is derived from
    `MapScreen`'s bases under ``pkg`` (plus the core class itself), and the
    modules are discovered by globbing the package — nothing is hand-listed.
    """
    wanted = _mixin_names(pkg) | {"MapScreen"}
    methods: dict[str, dict[str, set[str]]] = {}
    for path in sorted(pkg.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if not isinstance(node, ast.ClassDef) or node.name not in wanted:
                continue
            for item in node.body:
                if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                c = _MethodCensus()
                c.visit(item)
                methods[item.name] = {
                    "reads": set(c.reads),
                    "writes": set(c.writes),
                    "calls": set(c.calls),
                }
    return methods


def frozen_baseline() -> dict[str, dict[str, set[str]]]:
    """The archived pre-split census, reduced to the frozen comparison shape."""
    import json

    data = json.loads(CENSUS_JSON.read_text(encoding="utf-8"))
    return {
        m["name"]: {
            "reads": set(m["reads"]),
            "writes": set(m["writes"]),
            "calls": set(m["calls"]),
        }
        for m in data["methods"]
    }


def census_drift(
    baseline: dict[str, dict[str, set[str]]],
    current: dict[str, dict[str, set[str]]],
) -> list[str]:
    """Human-readable drift report; empty list means the freeze holds."""
    problems = []
    for name in sorted(set(baseline) - set(current)):
        problems.append(f"lost method: {name}")
    for name in sorted(set(current) - set(baseline)):
        problems.append(f"new method: {name}")
    for name in sorted(set(baseline) & set(current)):
        for kind in ("reads", "writes", "calls"):
            for attr in sorted(current[name][kind] - baseline[name][kind]):
                problems.append(f"{name}: gained {kind[:-1]} {attr}")
            for attr in sorted(baseline[name][kind] - current[name][kind]):
                problems.append(f"{name}: lost {kind[:-1]} {attr}")
    return problems


# ---------------------------------------------------------------------------
# Mutant planting (tmp copies only — no product file is ever touched).
# ---------------------------------------------------------------------------

def _copy_map_package(tmp_path: Path) -> Path:
    dst = tmp_path / "mapper"
    shutil.copytree(
        REPO_ROOT / "mapper", dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    return dst / "screens" / "map"


def _first_mixin_class(pkg: Path) -> tuple[Path, ast.ClassDef]:
    """First (by sorted file order, then line) class of the derived mixin set."""
    mixins = _mixin_names(pkg)
    for path in sorted(pkg.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name in mixins:
                return path, node
    raise AssertionError("no mixin class found in the copied package")


def _class_indent(path: Path, cls: ast.ClassDef) -> str:
    line = path.read_text(encoding="utf-8").splitlines()[cls.lineno - 1]
    return re.match(r"\s*", line).group(0) + "    "


def _plant_writer(pkg: Path, attr: str) -> tuple[Path, str]:
    """Add `self.<attr> = None` to a mixin method that does not already write it.

    Returns (mutated file, mutated method name).  The method is the first one
    of the first mixin class whose frozen writes exclude ``attr`` — LLR-MOD.7.2's
    negative control: a synthetic writer for an F1 attribute in a second concern.
    """
    baseline = frozen_baseline()
    path, cls = _first_mixin_class(pkg)
    for item in cls.body:
        if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if attr not in baseline[item.name]["writes"]:
            break
    else:
        raise AssertionError(f"no mixin method without a frozen write of {attr!r}")
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    first = item.body[0]
    indent = re.match(r"\s*", lines[first.lineno - 1]).group(0)
    lines.insert(first.lineno - 1, f"{indent}self.{attr} = None\n")
    path.write_text("".join(lines), encoding="utf-8")
    return path, item.name


def _plant_method(pkg: Path, method_name: str) -> tuple[Path, str]:
    """Append a brand-new method to the first mixin class.  Returns (file, name)."""
    path, cls = _first_mixin_class(pkg)
    indent = _class_indent(path, cls)
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    lines[cls.end_lineno:cls.end_lineno] = [
        f"{indent}def {method_name}(self):\n",
        f"{indent}    return self.graph\n",
    ]
    path.write_text("".join(lines), encoding="utf-8")
    return path, method_name


# ---------------------------------------------------------------------------
# GREEN + RED
# ---------------------------------------------------------------------------

def test_llr_mod_7_2_census_matches_the_frozen_baseline():
    drift = census_drift(frozen_baseline(), census_of_mapscreen(MAP_PKG))
    assert drift == []


def test_llr_mod_7_2_red_writer_drift(tmp_path):
    """Negative control: `self.graph = None` planted in a mixin method — the
    attribute gains a writer concern, the exact F1 drift the freeze bans."""
    pkg = _copy_map_package(tmp_path)
    path, method = _plant_writer(pkg, "graph")
    drift = census_drift(frozen_baseline(), census_of_mapscreen(pkg))
    assert drift, "planted writer drift was not reported"
    assert f"{method}: gained write graph" in drift
    assert str(path).endswith(".py")


def test_llr_mod_7_2_red_new_method(tmp_path):
    """Negative control: a new cross-cutting method added to a mixin — the
    method-name set no longer equals the frozen F2 surface."""
    pkg = _copy_map_package(tmp_path)
    path, name = _plant_method(pkg, "_mod_red_probe")
    drift = census_drift(frozen_baseline(), census_of_mapscreen(pkg))
    assert drift, "planted new method was not reported"
    assert f"new method: {name}" in drift
    # the ONLY drift is the planted method — nothing else moved
    assert drift == [f"new method: {name}"]
