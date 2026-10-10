"""Dependency guards for the modularised `mapper` package.

Covers HLR-MOD.6 / HLR-MOD.7 and their LLRs — LLR-MOD.6.1 (the four B-02
function-local `mapper.app` imports are gone, BOTH import forms matched by AST
at any scope), LLR-MOD.6.2 (no module under `mapper/screens/` — the `screens/map`
package included — imports `mapper.app` at any scope), LLR-MOD.7.1 (the amended
ARCHITECTURE §3 dependency rules: concern mixin modules never import each other,
only `screen.py` imports the concern modules, sibling screens import
`MapScreen` / `NavigationModel` from `mapper.screens.map` never from
`mapper.app`, and nothing imports `mapper.app` outside `__main__`-style entry
points) — and their acceptance tests AT-070 (B-02 is closed on the shipped tree,
`factory.py` importing `_PromptScreen` from `mapper.screens.prompt` at module
level) and AT-071 (the shipped module graph is what makes post-B11 parallel
lanes legal).

WHY this file exists: the `screens -> app` back-edge is the cycle ARCHITECTURE
§3 bans, and a concern importing a sibling concern would recreate the coupling
mechanism the split removed.  Both failures are silent until something
partially-initialised gets imported (spike R-8), so every rule is derived from
the shipped ASTs — the concern set comes from `MapScreen`'s actual bases, not
from a hand list — and every checker is a function of a package root run GREEN
on the real tree and RED on a tmp-copy mutant, a permanent executable negative
control per rule.
"""
from __future__ import annotations

import ast
import pathlib
import shutil

import pytest

import mapper

PKG = pathlib.Path(mapper.__file__).parent

# §3 `screens/map` row + LLR-MOD.7.1: only `app` (the orchestrator, which
# depends on `screens/map`) and the composing core may import the concern
# modules; the sibling screens that construct `MapScreen` may import
# `MapScreen` / `NavigationModel` from `mapper.screens.map`.
ALLOWED_CONCERN_IMPORTERS = {
    "app.py",
    "screens/map/screen.py",
    "screens/home.py",
    "screens/import_preview.py",
    "screens/repo.py",
}
ALLOWED_SIBLING_IMPORTERS = {
    "screens/home.py",
    "screens/import_preview.py",
    "screens/repo.py",
}
SIBLINGS_IMPORT_FROM_MAP = {"MapScreen", "NavigationModel"}


def _py_files(root: pathlib.Path):
    for path in sorted(root.rglob("*.py")):
        yield path.relative_to(root).as_posix(), path


def _app_import_lines(tree: ast.AST):
    """Line numbers of every import of `mapper.app` — `import mapper.app` under
    any alias, `from mapper.app import ...`, and relative `..app` forms — at any
    scope (LLR-MOD.6.1 matches BOTH forms by AST)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "mapper.app" or alias.name.startswith("mapper.app."):
                    yield node.lineno
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                module = node.module or ""
                if module == "mapper.app" or module.startswith("mapper.app."):
                    yield node.lineno
            else:
                if (node.module or "").split(".")[-1] == "app" or (
                    not node.module and any(a.name == "app" for a in node.names)
                ):
                    yield node.lineno


def _map_pkg_imports(rel: str, tree: ast.AST):
    """(form, tail, names) for imports resolving into `mapper.screens.map`:
    form "names" — `from mapper.screens.map.<tail> import <names>` (absolute)
    or `from .<tail> import <names>` (inside the map package); form "module" —
    the map package or one of its modules imported as a module object."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "mapper.screens.map" or alias.name.startswith(
                    "mapper.screens.map."
                ):
                    tail = alias.name.split(".", 3)[-1] if alias.name.count(".") >= 3 else ""
                    yield "module", tail, [alias.asname or tail]
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                module = node.module or ""
                if module == "mapper.screens.map":
                    for alias in node.names:
                        yield "module", alias.name, [alias.asname or alias.name]
                elif module.startswith("mapper.screens.map."):
                    yield "names", module.split(".", 3)[-1], [
                        a.name for a in node.names
                    ]
            elif rel.startswith("screens/map/"):
                if node.module:
                    yield "names", node.module.split(".")[0], [
                        a.name for a in node.names
                    ]
                else:
                    for alias in node.names:
                        yield "module", alias.name, [alias.asname or alias.name]


def _mixin_modules(root: pathlib.Path) -> dict[str, str]:
    """`MapScreen`'s mixin bases, DERIVED from the code: class name ->
    `screens/map/<file>.py` that defines it.  Never hand-listed."""
    screen_tree = ast.parse(
        (root / "screens" / "map" / "screen.py").read_text(encoding="utf-8")
    )
    base_names = []
    for node in ast.walk(screen_tree):
        if isinstance(node, ast.ClassDef) and node.name == "MapScreen":
            for base in node.bases:
                if isinstance(base, ast.Name):
                    base_names.append(base.id)
    assert base_names, "MapScreen bases not found: the derivation probe is broken"
    owners: dict[str, str] = {}
    for path in sorted((root / "screens" / "map").glob("*.py")):
        if path.name == "__init__.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name in base_names:
                owners[node.name] = f"screens/map/{path.name}"
    # Bases defined outside the package (e.g. textual's `Screen`) simply have
    # no owner here — the derived concern set is whatever IS owned in the map
    # package.  An empty set means the composition probe is broken, not green.
    assert owners, "no MapScreen base is defined in screens/map: derivation broken"
    return owners


# --------------------------------------------------------------------------
# Checkers — each takes a package root (Path to a `mapper` dir) and returns
# the violation set (empty == GREEN).
# --------------------------------------------------------------------------


def screens_app_import_sites(root: pathlib.Path) -> dict[str, list[int]]:
    """LLR-MOD.6.1/6.2: `rel file -> [lines]` of every `mapper.app` import,
    either form, any scope, anywhere under `screens/`."""
    found: dict[str, list[int]] = {}
    for rel, path in _py_files(root):
        if not rel.startswith("screens/"):
            continue
        lines = list(_app_import_lines(ast.parse(path.read_text(encoding="utf-8"))))
        if lines:
            found[rel] = lines
    return found


def map_app_import_sites(root: pathlib.Path) -> dict[str, list[int]]:
    """LLR-MOD.6.2: the same property scoped to the `screens/map` package."""
    return {
        rel: lines
        for rel, lines in screens_app_import_sites(root).items()
        if rel.startswith("screens/map/")
    }


def package_app_import_sites(root: pathlib.Path) -> dict[str, list[int]]:
    """LLR-MOD.7.1: nothing in the whole package imports `mapper.app` except
    `__main__`-style entry points, DERIVED by glob (currently none)."""
    entry_points = {rel for rel, _ in _py_files(root) if rel.endswith("__main__.py")}
    found: dict[str, list[int]] = {}
    for rel, path in _py_files(root):
        if rel in entry_points:
            continue
        lines = list(_app_import_lines(ast.parse(path.read_text(encoding="utf-8"))))
        if lines:
            found[rel] = lines
    return found


def concern_cross_imports(root: pathlib.Path) -> dict[str, list[str]]:
    """LLR-MOD.7.1: concern mixin modules never import each other.  A map
    module other than `screen.py` may not import a mixin class from a sibling
    map module, nor pull in a concern module as a module object — the
    `NavigationModel` import from `navigation.py` is the one sanctioned
    non-mixin name (§3 lets siblings read the shared model)."""
    mixins = _mixin_modules(root)
    concern_mods = {pathlib.Path(f).stem for f in mixins.values()}
    bad: dict[str, list[str]] = {}
    for rel, path in _py_files(root):
        if not rel.startswith("screens/map/") or rel == "screens/map/screen.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        hits = []
        for form, tail, names in _map_pkg_imports(rel, tree):
            if tail not in concern_mods:
                continue
            if form == "module" or any(n in mixins for n in names):
                hits.append(f"{tail} -> {names}")
        if hits:
            bad[rel] = hits
    return bad


def concern_module_importers(root: pathlib.Path) -> dict[str, set[str]]:
    """LLR-MOD.7.1: only `screen.py` (plus `app` and the sibling screens, in
    `ALLOWED_CONCERN_IMPORTERS`) imports the concern modules at all — `rel ->
    concern module tails imported for their mixin content`."""
    mixins = _mixin_modules(root)
    concern_mods = {pathlib.Path(f).stem for f in mixins.values()}
    importers: dict[str, set[str]] = {}
    for rel, path in _py_files(root):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        tails = set()
        for form, tail, names in _map_pkg_imports(rel, tree):
            if tail not in concern_mods:
                continue
            if form == "module" or any(n in mixins for n in names):
                tails.add(tail)
        if tails:
            importers[rel] = tails
    return importers


def sibling_map_importers(root: pathlib.Path) -> dict[str, set[str]]:
    """LLR-MOD.7.1: sibling screens (`screens/*.py` outside the map package)
    that import `mapper.screens.map` at all, and the names they take.  §3 bans
    any importer outside {home, import_preview, repo} and any name outside
    {MapScreen, NavigationModel}."""
    importers: dict[str, set[str]] = {}
    for rel, path in _py_files(root):
        if not rel.startswith("screens/") or rel.startswith("screens/map/"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        names = set()
        for _form, _tail, imported in _map_pkg_imports(rel, tree):
            names.update(imported)
        if names:
            importers[rel] = names
    return importers


def factory_imports_prompt_at_module_level(root: pathlib.Path) -> bool:
    """LLR-MOD.6.1/AT-070: `factory.py` holds `_PromptScreen` as a module-level
    import of `mapper.screens.prompt` (the A2 remediation of the last B-02
    function-local back-edge)."""
    tree = ast.parse((root / "screens" / "factory.py").read_text(encoding="utf-8"))
    return any(
        isinstance(node, ast.ImportFrom)
        and node.module == "mapper.screens.prompt"
        and any(a.name == "_PromptScreen" for a in node.names)
        for node in tree.body
    )


def settings_imports_common_at_module_level(root: pathlib.Path) -> bool:
    """LLR-MOD.6.1/AT-070: `settings.py` holds `keybar_groups` as a module-level
    import of `mapper.screens.common` (the A1 remediation)."""
    tree = ast.parse((root / "screens" / "settings.py").read_text(encoding="utf-8"))
    return any(
        isinstance(node, ast.ImportFrom)
        and node.module == "mapper.screens.common"
        and any(a.name == "keybar_groups" for a in node.names)
        for node in tree.body
    )


# --------------------------------------------------------------------------
# Mutation helpers — tmp copies of the package with one planted defect each.
# --------------------------------------------------------------------------


def _copy_pkg(tmp_path: pathlib.Path) -> pathlib.Path:
    dest = tmp_path / "mapper"
    shutil.copytree(PKG, dest, ignore=shutil.ignore_patterns("__pycache__"))
    return dest


def _plant_from_app_import(pkg: pathlib.Path, rel: str, scoped: bool) -> None:
    """Plant `from mapper.app import keybar_groups` (the historical B-02 shape)."""
    path = pkg / rel
    if scoped:
        path.open("a", encoding="utf-8").write(
            "\n\ndef _planted_scope_probe():\n"
            "    from mapper.app import keybar_groups  # planted defect\n"
            "    return keybar_groups\n"
        )
    else:
        path.open("a", encoding="utf-8").write(
            "\nfrom mapper.app import keybar_groups  # planted defect\n"
        )


# --------------------------------------------------------------------------
# LLR-MOD.6.1 — the four B-02 function-local imports are removed (`-k b02`)
# --------------------------------------------------------------------------


def test_llr_mod_6_1_b02_no_from_import_form_anywhere_under_screens(tmp_path):
    assert screens_app_import_sites(PKG) == {}
    mutant = _copy_pkg(tmp_path)
    _plant_from_app_import(mutant, "screens/map/panning.py", scoped=False)
    with pytest.raises(AssertionError):
        assert screens_app_import_sites(mutant) == {}


def test_llr_mod_6_1_b02_no_plain_or_aliased_import_form_anywhere(tmp_path):
    """The `import mapper.app [as ...]` form is matched too, not just
    `from mapper.app import ...` — LLR-MOD.6.1 says BOTH forms, by AST."""
    mutant = _copy_pkg(tmp_path)
    (mutant / "screens" / "map" / "hints.py").open("a", encoding="utf-8").write(
        "\nimport mapper.app as _planted_app  # planted defect\n"
    )
    with pytest.raises(AssertionError):
        assert screens_app_import_sites(mutant) == {}


def test_llr_mod_6_1_b02_function_local_scope_is_detected(tmp_path):
    """The historical B-02 imports were function-local; the AST walk must see
    a defect at any scope, not only module level."""
    mutant = _copy_pkg(tmp_path)
    _plant_from_app_import(mutant, "screens/factory.py", scoped=True)
    with pytest.raises(AssertionError):
        assert screens_app_import_sites(mutant) == {}


# --------------------------------------------------------------------------
# LLR-MOD.6.2 — no `mapper.app` import from the package, map package scoped
# (`-k no_app_import`)
# --------------------------------------------------------------------------


def test_llr_mod_6_2_no_app_import_map_package_at_any_scope(tmp_path):
    assert map_app_import_sites(PKG) == {}
    mutant = _copy_pkg(tmp_path)
    _plant_from_app_import(mutant, "screens/map/searching.py", scoped=True)
    with pytest.raises(AssertionError):
        assert map_app_import_sites(mutant) == {}


def test_llr_mod_6_2_no_app_import_sibling_screens_never_import_map_screen_from_app(
    tmp_path,
):
    """LLR-MOD.6.2's second clause: a sibling screen importing `MapScreen` from
    `mapper.app` (instead of `mapper.screens.map`) is the banned back-edge."""
    mutant = _copy_pkg(tmp_path)
    (mutant / "screens" / "home.py").open("a", encoding="utf-8").write(
        "\nfrom mapper.app import MapScreen as _PlantedMapScreen  # planted defect\n"
    )
    with pytest.raises(AssertionError):
        assert screens_app_import_sites(mutant) == {}


# --------------------------------------------------------------------------
# AT-070 — B-02 is closed on the shipped tree (`-k at070`, own node)
# --------------------------------------------------------------------------


def test_at070_b02_closed(tmp_path):
    assert screens_app_import_sites(PKG) == {}, (
        "HLR-MOD.6/AT-070: a `screens -> app` import edge is back on the tree"
    )
    assert factory_imports_prompt_at_module_level(PKG), (
        "AT-070: factory.py must import `_PromptScreen` from "
        "`mapper.screens.prompt` at module level (A2 remediation)"
    )
    assert settings_imports_common_at_module_level(PKG), (
        "AT-070: settings.py must import `keybar_groups` from "
        "`mapper.screens.common` at module level (A1 remediation)"
    )
    # Negative control (permanent): restoring one cycle-dodging function-local
    # import (premise 6's shape) reddens the AT.
    mutant = _copy_pkg(tmp_path)
    _plant_from_app_import(mutant, "screens/factory.py", scoped=True)
    with pytest.raises(AssertionError):
        assert screens_app_import_sites(mutant) == {}


# --------------------------------------------------------------------------
# LLR-MOD.7.1 — the amended §3 dependency rules (`-k arch`)
# --------------------------------------------------------------------------


def test_llr_mod_7_1_arch_concern_mixins_never_import_each_other(tmp_path):
    assert concern_cross_imports(PKG) == {}
    # Planted defect: a sibling-concern import (HLR-MOD.7's named mutation).
    mutant = _copy_pkg(tmp_path)
    (mutant / "screens" / "map" / "painting.py").open("a", encoding="utf-8").write(
        "\nfrom mapper.screens.map.searching import SearchingOps  # planted defect\n"
    )
    with pytest.raises(AssertionError):
        assert concern_cross_imports(mutant) == {}


def test_llr_mod_7_1_arch_only_screen_py_imports_the_concern_modules(tmp_path):
    importers = concern_module_importers(PKG)
    assert set(importers) <= ALLOWED_CONCERN_IMPORTERS, importers
    assert "screens/map/screen.py" in importers, (
        f"the composing core must import its concern modules, else the probe "
        f"is vacuous: {importers}"
    )
    # Planted defect: `painting.py` importing the searching concern module.
    mutant = _copy_pkg(tmp_path)
    (mutant / "screens" / "map" / "painting.py").open("a", encoding="utf-8").write(
        "\nfrom mapper.screens.map.searching import SearchingOps  # planted defect\n"
    )
    with pytest.raises(AssertionError):
        assert set(concern_module_importers(mutant)) <= ALLOWED_CONCERN_IMPORTERS


def test_llr_mod_7_1_arch_sibling_screens_import_map_names_from_the_map_package(
    tmp_path,
):
    importers = sibling_map_importers(PKG)
    assert importers, "the AST walk found no sibling importer: the probe is broken"
    assert set(importers) <= ALLOWED_SIBLING_IMPORTERS, importers
    for rel, names in importers.items():
        assert names <= SIBLINGS_IMPORT_FROM_MAP, (rel, names)
    # Planted defect: a sibling screen taking MapScreen from mapper.app —
    # caught by the no-app-import guard, which is part of this rule.
    mutant = _copy_pkg(tmp_path)
    (mutant / "screens" / "home.py").open("a", encoding="utf-8").write(
        "\nfrom mapper.app import MapScreen as _PlantedMapScreen  # planted defect\n"
    )
    with pytest.raises(AssertionError):
        assert screens_app_import_sites(mutant) == {}


def test_llr_mod_7_1_arch_nothing_imports_mapper_app_outside_entry_points(tmp_path):
    assert package_app_import_sites(PKG) == {}
    mutant = _copy_pkg(tmp_path)
    (mutant / "screens" / "common.py").open("a", encoding="utf-8").write(
        "\nimport mapper.app  # planted defect\n"
    )
    with pytest.raises(AssertionError):
        assert package_app_import_sites(mutant) == {}


# --------------------------------------------------------------------------
# AT-071 — the module graph allows parallel lanes (`-k at071`, own node)
# --------------------------------------------------------------------------


def test_at071_the_module_graph_allows_parallel_lanes(tmp_path):
    """HLR-MOD.7's behavioural chain end to end: every §3 rule holds on the
    shipped module graph — the property that makes post-B11 lanes legal."""
    assert screens_app_import_sites(PKG) == {}
    assert map_app_import_sites(PKG) == {}
    assert package_app_import_sites(PKG) == {}
    assert concern_cross_imports(PKG) == {}
    assert set(concern_module_importers(PKG)) <= ALLOWED_CONCERN_IMPORTERS
    siblings = sibling_map_importers(PKG)
    assert set(siblings) <= ALLOWED_SIBLING_IMPORTERS
    for rel, names in siblings.items():
        assert names <= SIBLINGS_IMPORT_FROM_MAP, (rel, names)
    # Negative controls (permanent, per HLR-MOD.7): mutation on tmp copies.
    mutant = _copy_pkg(tmp_path)
    _plant_from_app_import(mutant, "screens/map/drafts.py", scoped=False)
    with pytest.raises(AssertionError):
        assert map_app_import_sites(mutant) == {}
    mutant2 = _copy_pkg(tmp_path / "second")
    (mutant2 / "screens" / "map" / "painting.py").open("a", encoding="utf-8").write(
        "\nfrom mapper.screens.map.searching import SearchingOps  # planted defect\n"
    )
    with pytest.raises(AssertionError):
        assert concern_cross_imports(mutant2) == {}
