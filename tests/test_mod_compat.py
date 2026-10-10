"""AT-067 / AT-069 and LLR-MOD.3.1 / LLR-MOD.3.2 — the compatibility guard file.

WHY this file exists (batch `2026-10-09-modular-batch`, increment B12): the split
of `mapper/app.py` moves every screen out of `app.py`, but 70 import sites in
`tests/` (and two in `mapper/`) still read names from `mapper.app`, and the suite
patches eight distinct names (premise 4 of `01-requirements.md`).  A move that
drops one re-export or repoints one patch to a module that merely BINDS the name
instead of READING it fails silently — the import still resolves and only one
test arm stops biting.  So every checker here is executable forever, not a
one-time census:

- LLR-MOD.3.1: every name any test or product module imports from `mapper.app`
  (collected by AST, never hand-listed) must resolve on `mapper.app`.  A tmp
  copy of the package with one re-export dropped is the permanent RED control.
- LLR-MOD.3.2 / AT-067: the seven module-global patch targets of premise 4 must
  be module globals of the modules that READ them, and patching through the
  reading module must change observable behaviour through the shipped screens
  with real keys.  An AST guard walks EVERY patch site in `tests/`
  (dotted-string `setattr`/`patch`, module-object `setattr`, and direct
  `<module>.<name> = ...` assignment) and requires the target module to bind or
  read the patched name; class-attribute patches such as
  `GitHubConnector.fetch` are recognised and skipped with a reason.  A tmp copy
  whose searching module no longer reads `MAX_RENDER_NODES` is the RED control.
- AT-069: the source-reading tests pinned in
  `.dev-flow/2026-10-09-modular-batch/evidence/at069-baseline.json` must keep
  at least their baseline assert/test counts, and none of them may locate a
  moved construct by a literal `mapper/app.py` path pin alone.  A baseline with
  one pin raised above the current count is the RED control.

All UI strings observed here are English; keys are pressed through the pilot,
never injected.
"""
from __future__ import annotations

import ast
import importlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "mapper"
TESTS = ROOT / "tests"
BASELINE_JSON = ROOT / ".dev-flow" / "2026-10-09-modular-batch" / "evidence" / "at069-baseline.json"

# Premise 4 of the contract: the seven module-global repoint targets and the
# module that READS each name (the reader of the patch site, not merely a
# module that binds it).  `GitHubConnector.fetch` is the eighth patch name: a
# class-attribute patch on the shared class object, it survives the move with
# no repoint (ARCH-11) and is covered by its own AT-067 arm.
PATCH_SURFACE = {
    "MAX_RENDER_NODES": "mapper.screens.map.searching",
    "SearchIndex": "mapper.screens.map.searching",
    "refusal_sentence": "mapper.screens.common",
    "save_svg": "mapper.screens.map.exporting",
    "pan_extent": "mapper.screens.map.panning",
    "LayeredRenderer": "mapper.screens.import_preview",
    "preview_csv": "mapper.screens.home",
}

# Receiver names under which the pytest `monkeypatch` fixture appears in this
# suite (one helper takes it as `mp`).
_PATCHERS = {"monkeypatch", "mp"}


# ---------------------------------------------------------------------------
# shared AST helpers
# ---------------------------------------------------------------------------

def _importable(dotted: str) -> bool:
    try:
        return importlib.util.find_spec(dotted) is not None
    except Exception:
        return False


def _split_dotted(dotted: str) -> tuple[str | None, list[str]]:
    """Longest importable module prefix of `dotted` -> (module, remaining)."""
    parts = dotted.split(".")
    for i in range(len(parts), 0, -1):
        candidate = ".".join(parts[:i])
        if _importable(candidate):
            return candidate, parts[i:]
    return None, parts


def _alias_table(tree: ast.Module) -> dict[str, str]:
    """Map every name bound by an import statement to its dotted source."""
    table: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                table[alias.asname or alias.name.split(".")[0]] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                if alias.name != "*":
                    table[alias.asname or alias.name] = f"{node.module}.{alias.name}"
    return table


def _dotted_of(expr: ast.expr, table: dict[str, str]) -> str | None:
    """Resolve a Name/Attribute chain against the import table, if possible."""
    if isinstance(expr, ast.Name):
        return table.get(expr.id)
    if isinstance(expr, ast.Attribute):
        base = _dotted_of(expr.value, table)
        return f"{base}.{expr.attr}" if base else None
    return None


def _module_source(pkg_root: Path, dotted: str) -> Path | None:
    """Source file for a module: prefer the tree under `pkg_root` (so a tmp
    mutant copy is read from the copy), else the installed/stdlib origin."""
    rel = Path(*dotted.split("."))
    for candidate in (pkg_root / rel.with_suffix(".py"), pkg_root / rel / "__init__.py"):
        if candidate.is_file():
            return candidate
    try:
        spec = importlib.util.find_spec(dotted)
    except Exception:
        return None
    if spec and spec.origin and spec.origin.endswith(".py") and Path(spec.origin).is_file():
        return Path(spec.origin)
    return None


def _module_level_bindings(tree: ast.Module) -> set[str]:
    bound: set[str] = set()
    for stmt in tree.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound.add(stmt.name)
        elif isinstance(stmt, ast.Import):
            bound.update(a.asname or a.name.split(".")[0] for a in stmt.names)
        elif isinstance(stmt, ast.ImportFrom):
            bound.update(a.asname or a.name for a in stmt.names if a.name != "*")
        elif isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                for name in _target_names(target):
                    bound.add(name)
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            bound.add(stmt.target.id)
    return bound


def _target_names(target: ast.expr) -> list[str]:
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, ast.Starred):
        return _target_names(target.value)
    if isinstance(target, (ast.Tuple, ast.List)):
        return [name for elt in target.elts for name in _target_names(elt)]
    return []


def _module_binds_or_reads(source: Path, name: str) -> bool:
    """The contract's guard (LLR-MOD.3.2): the target module binds the patched
    name at module level (def/class/assignment/import — a true module global)
    or actually READS it (an `ast.Name` load anywhere in its source)."""
    tree = ast.parse(source.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == name and isinstance(node.ctx, ast.Load):
            return True
    return name in _module_level_bindings(tree)


# ---------------------------------------------------------------------------
# LLR-MOD.3.1 — every imported name is re-exported
# ---------------------------------------------------------------------------

def collect_mapper_app_imports(tests_root: Path, pkg_root: Path) -> set[str]:
    """Every name any test or product module takes from `mapper.app`, by AST:
    `from mapper.app import X` (any scope), and attribute loads `alias.X`
    where `alias` resolves to the `mapper.app` module (e.g.
    `from mapper import app as app_module; app_module._path_refusal`)."""
    names: set[str] = set()
    for base in (tests_root, pkg_root):
        for path in sorted(base.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            table = _alias_table(tree)
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.ImportFrom)
                    and node.module == "mapper.app"
                ):
                    names.update(a.name for a in node.names if a.name != "*")
                elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
                    dotted = _dotted_of(node, table)
                    if not dotted:
                        continue
                    module, rest = _split_dotted(dotted)
                    if module == "mapper.app" and rest and not rest[0].startswith("__"):
                        names.add(rest[0])
    return names


def check_reexports(pkg_root: Path, tests_root: Path) -> list[str]:
    """Names imported from `mapper.app` that `app.py` does not bind at module
    level — i.e. re-exports the split dropped."""
    required = collect_mapper_app_imports(tests_root, pkg_root)
    app_tree = ast.parse((pkg_root / "mapper" / "app.py").read_text(encoding="utf-8"))
    return sorted(required - _module_level_bindings(app_tree))


_IMPORTED_NAMES = collect_mapper_app_imports(TESTS, PKG)


def test_llr_mod_3_1_reexports_static_tree():
    """GREEN arm on the real tree: the AST census is non-empty and every name
    it collects is bound at module level of `mapper/app.py` (the re-export
    block)."""
    assert _IMPORTED_NAMES, "the import census derived nothing; it cannot pass vacuously"
    missing = check_reexports(ROOT, TESTS)
    assert missing == [], f"names imported from mapper.app but not re-exported: {missing}"


@pytest.mark.parametrize("name", sorted(_IMPORTED_NAMES))
def test_llr_mod_3_1_reexports_resolve(name):
    """Each collected name resolves on the real `mapper.app` module object."""
    app_module = importlib.import_module("mapper.app")
    assert hasattr(app_module, name), f"mapper.app has no attribute {name!r}"
    assert getattr(app_module, name) is not None


def test_llr_mod_3_1_reexports_red_when_a_reexport_is_dropped(tmp_path):
    """Permanent RED control (LLR-MOD.3.1 negative control): a tmp copy of the
    package with one required re-export's import line removed from `app.py`
    loses that name, and the checker — run on the copy — reports it."""
    mutant = tmp_path / "pkg"
    shutil.copytree(PKG, mutant / "mapper")
    app_py = mutant / "mapper" / "app.py"
    lines = app_py.read_text(encoding="utf-8").splitlines(keepends=True)
    # Pick a required name whose module-level binding in app.py is a single
    # one-line import, and drop exactly that line.
    import re

    dropped_name = None
    dropped_line = None
    for name in sorted(_IMPORTED_NAMES):
        pattern = re.compile(rf"^from\s+\S+\s+import\s+{re.escape(name)}\s*$")
        matches = [ln for ln in lines if pattern.match(ln.strip())]
        if matches:
            dropped_name, dropped_line = name, matches[0]
            break
    assert dropped_line is not None, (
        "the planted defect lost its anchor: no required name is bound by a "
        "single-line import in app.py"
    )
    kept = [ln for ln in lines if ln != dropped_line]
    app_py.write_text("".join(kept), encoding="utf-8")
    missing = check_reexports(tmp_path / "pkg", TESTS)
    assert dropped_name in missing, f"defect not detected; checker reported {missing}"


# ---------------------------------------------------------------------------
# LLR-MOD.3.2 — the AST patch-site guard
# ---------------------------------------------------------------------------

class PatchSite:
    def __init__(self, file: str, lineno: int, module: str, name: str):
        self.file = file
        self.lineno = lineno
        self.module = module
        self.name = name

    def __repr__(self):  # pragma: no cover - debugging aid
        return f"PatchSite({self.file}:{self.lineno} {self.module}.{self.name})"


def collect_patch_sites(tests_root: Path) -> tuple[list[PatchSite], list[str]]:
    """Every patch site in `tests/`, classified.  Returns (guarded sites, skips
    with reasons).  Covers the three forms of the contract: dotted-string
    `monkeypatch.setattr("a.b.c", ...)` (and `mock.patch`, reserved for later
    suites), module-object `monkeypatch.setattr(<imported module alias>,
    "name", ...)`, and direct `<module alias>.<name> = ...` assignments."""
    sites: list[PatchSite] = []
    skips: list[str] = []
    for path in sorted(tests_root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        table = _alias_table(tree)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("setattr", "patch")
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in _PATCHERS
                and len(node.args) >= 2
            ):
                first, second = node.args[0], node.args[1]
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    module, rest = _split_dotted(first.value)
                    if module is None:
                        skips.append(f"{path.name}:{node.lineno} unresolvable target {first.value!r}")
                    elif len(rest) >= 2:
                        skips.append(
                            f"{path.name}:{node.lineno} class-attribute patch {first.value!r}"
                        )
                    elif len(rest) == 0:
                        skips.append(f"{path.name}:{node.lineno} whole-module patch {first.value!r}")
                    else:
                        sites.append(PatchSite(path.name, node.lineno, module, rest[0]))
                    continue
                dotted = _dotted_of(first, table)
                if dotted is None:
                    skips.append(f"{path.name}:{node.lineno} instance/dynamic target")
                elif not _importable(dotted):
                    skips.append(f"{path.name}:{node.lineno} class-or-value patch on {dotted!r}")
                elif not (isinstance(second, ast.Constant) and isinstance(second.value, str)):
                    skips.append(f"{path.name}:{node.lineno} dynamic attribute name")
                else:
                    sites.append(PatchSite(path.name, node.lineno, dotted, second.value))
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        isinstance(target, ast.Attribute)
                        and isinstance(target.value, ast.Name)
                        and isinstance(target.ctx, ast.Store)
                    ):
                        dotted = table.get(target.value.id)
                        if dotted is None:
                            continue
                        if not _importable(dotted):
                            skips.append(
                                f"{path.name}:{node.lineno} class-or-value assignment on {dotted!r}"
                            )
                        else:
                            sites.append(PatchSite(path.name, node.lineno, dotted, target.attr))
    return sites, skips


def guard_patch_sites(pkg_root: Path, tests_root: Path) -> tuple[list[str], list[PatchSite], list[str]]:
    """Run the guard: returns (violations, guarded sites, skips).  A violation
    is a patch site whose target module neither binds nor reads the patched
    name — the silent-failure mode LLR-MOD.3.2 exists to prevent."""
    sites, skips = collect_patch_sites(tests_root)
    violations: list[str] = []
    guarded: list[PatchSite] = []
    for site in sites:
        source = _module_source(pkg_root, site.module)
        if source is None:
            skips.append(f"{site.file}:{site.lineno} no source for {site.module}")
            continue
        if _module_binds_or_reads(source, site.name):
            guarded.append(site)
        else:
            violations.append(
                f"{site.file}:{site.lineno} patches {site.module}.{site.name} "
                f"but that module neither binds nor reads {site.name!r}"
            )
    return violations, guarded, skips


def test_llr_mod_3_2_patch_guard_every_site_targets_a_reading_module():
    """GREEN arm: across every patch site in `tests/`, each target module
    binds or reads the patched name; the seven premise-4 module-global targets
    are guarded through their contract reading modules (never through
    `mapper.app`); and the class-attribute skips are recognised with a reason
    (so the skip path cannot swallow a real site silently)."""
    violations, guarded, skips = guard_patch_sites(ROOT, TESTS)
    assert guarded, "the guard derived no patch sites at all; it cannot pass vacuously"
    assert violations == [], "\n".join(violations)
    guarded_by_name: dict[str, set[str]] = {}
    for site in guarded:
        guarded_by_name.setdefault(site.name, set()).add(site.module)
    for name, reader in PATCH_SURFACE.items():
        assert name in guarded_by_name, (
            f"premise-4 target {name!r} has no guarded patch site — was a repoint dropped?"
        )
        assert reader in guarded_by_name[name], (
            f"{name!r} is patched on {sorted(guarded_by_name[name])}, "
            f"which does not include its reading module {reader}"
        )
    assert not any(site.module == "mapper.app" for site in guarded), (
        "a module-global patch site still targets mapper.app instead of its reading module"
    )
    assert any("class-attribute patch" in reason and "GitHubConnector.fetch" in reason
               for reason in skips), (
        "GitHubConnector.fetch must be recognised as a surviving class-attribute patch; "
        f"skips were: {skips}"
    )


def test_llr_mod_3_2_patch_guard_red_when_the_target_stops_reading(tmp_path):
    """Permanent RED control (LLR-MOD.3.2 negative control): a tmp copy of the
    package whose `screens/map/searching.py` no longer binds or reads
    `MAX_RENDER_NODES` (every token renamed, the import included) makes the
    five searching patch sites vacuous, and the guard — run on the copy —
    reports them."""
    mutant = tmp_path / "pkg"
    shutil.copytree(PKG, mutant / "mapper")
    searching_py = mutant / "mapper" / "screens" / "map" / "searching.py"
    source = searching_py.read_text(encoding="utf-8")
    assert "MAX_RENDER_NODES" in source
    searching_py.write_text(
        source.replace("MAX_RENDER_NODES", "UNREAD_RENDER_BOUND"), encoding="utf-8"
    )
    violations, guarded, skips = guard_patch_sites(tmp_path / "pkg", TESTS)
    planted = [v for v in violations if "searching" in v and "MAX_RENDER_NODES" in v]
    assert planted, (
        f"defect not detected: expected a violation for mapper.screens.map.searching."
        f"MAX_RENDER_NODES, got {violations}"
    )


# ---------------------------------------------------------------------------
# AT-067 — the patch-surface contract
# ---------------------------------------------------------------------------

def test_at067_the_seven_targets_are_module_globals_of_their_reading_modules():
    """Each premise-4 module-global target is a module global of the module
    that reads it (no lazy read through `mapper.app` — the F4 design is
    dropped)."""
    for name, dotted in PATCH_SURFACE.items():
        module = importlib.import_module(dotted)
        assert name in vars(module), f"{dotted} does not bind {name!r} at module level"


async def test_at067_patching_the_limit_through_the_reading_module_bites(tmp_path, monkeypatch):
    """The behavioural half of the contract, observed through the shipped
    MapScreen with REAL keys: `mapper.screens.map.searching.MAX_RENDER_NODES`
    is set to one node below the map size, the map is opened, the query is
    typed and submitted with real keys — and the walk's over-limit notice
    names the patched bound on the painted frame (never the 'no matches'
    lie, because the query does match)."""
    from mapper.app import MapperApp
    from mapper.widgets.chrome import HintLine
    from tests.inc3_support import open_map, rows_in
    from tests.inc4_support import MAP_ID, QUERY, build_adjuntos

    import mapper.screens.map.searching as searching_module

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        graph = build_adjuntos(tmp_path)
        app.store.save(MAP_ID, graph)
        screen = await open_map(app, pilot, MAP_ID)
        monkeypatch.setattr(searching_module, "MAX_RENDER_NODES", len(graph.nodes) - 1)

        await pilot.press("slash")
        await pilot.pause()
        for ch in QUERY:
            await pilot.press("space" if ch == " " else ch)
        await pilot.press("enter")
        await pilot.pause()

        hint = screen.query_one(HintLine).text
        assert hint != "no matches · esc clear", hint
        assert screen._search_order() is None, "the patched bound was not reached"

        await pilot.press("n")
        await pilot.pause()
        await pilot.press("n")
        await pilot.pause()
        painted = " ".join(rows_in(screen, screen.query_one("#map-toast").region)).strip()
        assert str(len(graph.nodes) - 1) in painted, painted
        assert "0 matches" not in painted, painted
        assert "is not in this map" not in painted, painted


def test_at067_github_connector_fetch_bites_through_the_shared_class_object(tmp_path, monkeypatch):
    """The eighth patch name survives the move with no repoint (ARCH-11): the
    class object reachable from `mapper.app` IS the shared class, and patching
    `fetch` on it changes behaviour for the shipped call shape
    `GitHubConnector(repo).fetch(progress=...)` that `RepoScreen.fetch_graph`
    performs."""
    from mapper.app import GitHubConnector
    from mapper.github import GitHubConnector as TrueConnector
    from mapper.model import Graph

    assert GitHubConnector is TrueConnector, "mapper.app must re-export the shared class object"

    calls: list[str] = []

    def fake_fetch(self, progress=None):
        calls.append(self.repo)
        return Graph()

    monkeypatch.setattr(GitHubConnector, "fetch", fake_fetch)
    connector = TrueConnector("owner/repo", cache_dir=tmp_path)
    graph = connector.fetch(progress=None)
    assert calls == ["owner/repo"], "the class-attribute patch did not bite"
    assert isinstance(graph, Graph)


# ---------------------------------------------------------------------------
# AT-069 — the source-reading tests keep their baseline
# ---------------------------------------------------------------------------

def _assert_and_test_counts(path: Path) -> tuple[int, int]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    asserts = sum(isinstance(node, ast.Assert) for node in ast.walk(tree))
    tests = sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
        for node in ast.walk(tree)
    )
    return asserts, tests


def _pinned_file(tests_root: Path, rel: str) -> Path:
    """Baseline keys are repo-relative; resolve them under the tests root."""
    return tests_root / rel.removeprefix("tests/")


def check_at069_baseline(baseline: dict, tests_root: Path) -> list[str]:
    """A baseline entry whose pinned assert/test counts sit above the current
    file's counts is a weakening (someone deleted assertions or tests)."""
    violations: list[str] = []
    for rel, pins in baseline["files"].items():
        asserts, test_fns = _assert_and_test_counts(_pinned_file(tests_root, rel))
        if asserts < pins["assert_statements"]:
            violations.append(
                f"{rel}: asserts {asserts} < baseline {pins['assert_statements']}"
            )
        if test_fns < pins["test_functions"]:
            violations.append(
                f"{rel}: test functions {test_fns} < baseline {pins['test_functions']}"
            )
    return violations


def check_no_stale_app_py_pins(tests_root: Path, baseline_files: list[str]) -> list[str]:
    """No pinned file locates a moved construct by a literal `mapper/app.py`
    path alone: a literal naming `app.py` may only appear in a statement with
    filesystem/path-read intent (a read call, a subscript lookup, or a path
    join) when its enclosing scope also scans the moved tree (`screens`,
    `rglob`, `walk_packages`, `inspect.getfile`) — otherwise the pin goes
    blind the moment the construct moves."""
    read_calls = ("read_text", "getsource", "walk_packages", "rglob", "getsourcefile")
    violations: list[str] = []

    def names_app_py(value: str) -> bool:
        return value in ("app.py", "mapper/app.py", "mapper\\app.py") or value.endswith(
            ("/app.py", "\\app.py")
        )

    def has_read_intent(stmt: ast.stmt, parent: ast.AST | None) -> bool:
        if isinstance(parent, ast.Subscript):
            return True
        for node in ast.walk(stmt):
            if isinstance(node, ast.Call):
                func = node.func
                callee = func.id if isinstance(func, ast.Name) else (
                    func.attr if isinstance(func, ast.Attribute) else ""
                )
                if callee in read_calls or callee.endswith("read_text"):
                    return True
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                return True
        return False

    for rel in baseline_files:
        path = _pinned_file(tests_root, rel)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        parents: dict[ast.AST, ast.AST] = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parents[child] = node
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
                continue
            if not names_app_py(node.value):
                continue
            parent = parents.get(node)
            if isinstance(parent, ast.Subscript):
                # A lookup label into a sources mapping (e.g.
                # `_product_sources()["mapper/app.py"]`), not a path read: the
                # mapping itself is built from imported modules, so the pin
                # follows the code.
                continue
            stmt = node
            while stmt is not None and not isinstance(stmt, ast.stmt):
                stmt = parents.get(stmt)  # type: ignore[assignment]
            if stmt is None or not has_read_intent(stmt, parent):
                continue
            scope = stmt
            while scope is not None and not isinstance(
                scope, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)
            ):
                scope = parents.get(scope)  # type: ignore[assignment]
            scope_dump = ast.dump(scope) if scope is not None else ""
            if any(token in scope_dump for token in ("screens", "walk_packages", "getfile", "rglob")):
                continue
            violations.append(
                f"{rel}:{node.lineno} reads {node.value!r} by literal path with no "
                f"companion scan of the moved tree in the same scope"
            )
    return violations


def test_at069_baseline_counts_hold():
    """GREEN arm: every pinned file still carries at least its baseline assert
    and test-function counts (HLR-MOD.5: the generalisation may add, never
    remove)."""
    baseline = json.loads(BASELINE_JSON.read_text(encoding="utf-8"))
    assert baseline["files"], "the baseline pins no files; this arm cannot pass vacuously"
    violations = check_at069_baseline(baseline, TESTS)
    assert violations == [], "\n".join(violations)
    stale = check_no_stale_app_py_pins(TESTS, sorted(baseline["files"]))
    assert stale == [], "\n".join(stale)


def test_at069_red_when_a_baseline_pin_is_raised_above_the_current_counts(tmp_path):
    """Permanent RED control (AT-069): a baseline with one entry's counts
    raised above the current file's actual counts is detected — the guard
    cannot be satisfied by deleting the assertions the baseline pins."""
    baseline = json.loads(BASELINE_JSON.read_text(encoding="utf-8"))
    mutant = json.loads(json.dumps(baseline))
    target = "tests/test_search.py"
    actual_asserts, _ = _assert_and_test_counts(_pinned_file(TESTS, target))
    mutant["files"][target]["assert_statements"] = actual_asserts + 1
    violations = check_at069_baseline(mutant, TESTS)
    assert any(target in violation for violation in violations), (
        f"planted baseline raise not detected; violations: {violations}"
    )
