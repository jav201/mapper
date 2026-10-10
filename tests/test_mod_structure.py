"""LLR-MOD.1.1 / 1.2 / 1.3 + AT-068 (HLR-MOD.1): the target module map is real.

WHY this file exists: the operator's precondition for parallel product lanes is
that one feature is edited by editing one module file (US-001).  The ARQ target
map (`docs/ARCHITECTURE.md` TARGET rows) is only honest if a guard reads the
shipped tree and freezes it — a map that lies is worse than one that is stale.
So every structural property here is DERIVED from the code (MapScreen's own
bases, an AST scan of `mapper/screens/`), never hand-listed, and every checker
is a FUNCTION of a package root: the GREEN tests run it on the real tree, the
`*_red_*` tests plant exactly one defect in a tmp copy of the package and
assert the checker reports it — a permanent executable negative control.

* LLR-MOD.1.1 (`-k spine_a`) — every sibling screen class under
  `mapper/screens/` is re-exported from `mapper/app.py` (static re-export
  resolution, plus `is` identity at runtime on the real tree), and `app.py`
  defines no `Screen` subclass.
* LLR-MOD.1.2 (`-k b0`) — `MapScreen` is defined in
  `mapper/screens/map/screen.py`; `mapper/screens/map/__init__.py` re-exports
  it and holds nothing else; `mapper.app.MapScreen is
  mapper.screens.map.MapScreen`; `app.py` stays under 400 lines.
* LLR-MOD.1.3 (`-k spine_b`) — MapScreen's concern mixins (derived from its
  bases) each live in their own module under `mapper/screens/map/`, no two
  share a file, and `mapper/app.py` holds only `MapperApp`, `main`, the
  `__main__` guard and imports.
* AT-068 (`-k at068`) — one feature, one file: the concern->module map derived
  from MapScreen's bases' `__module__` is one distinct module per concern.
"""
from __future__ import annotations

import ast
import importlib
import inspect
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "mapper"

_SCREEN_BASES = frozenset({"Screen", "ModalScreen"})


# ---------------------------------------------------------------------------
# Small AST helpers
# ---------------------------------------------------------------------------

def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _has_screen_base(cls: ast.ClassDef) -> bool:
    """True when a class inherits Textual's `Screen` or `ModalScreen`
    (the latter subscripted, e.g. `ModalScreen[str | None]`)."""
    for base in cls.bases:
        name = None
        if isinstance(base, ast.Name):
            name = base.id
        elif isinstance(base, ast.Subscript) and isinstance(base.value, ast.Name):
            name = base.value.id
        if name in _SCREEN_BASES:
            return True
    return False


def _relative_imports(path: Path) -> set[tuple[str, str]]:
    """`(dotted module relative to the package, imported name)` for every
    level-1 relative import at the top of `path`."""
    out: set[tuple[str, str]] = set()
    for node in _parse(path).body:
        if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module:
            for alias in node.names:
                out.add((node.module, alias.asname or alias.name))
    return out


def _top_classes(path: Path) -> dict[str, ast.ClassDef]:
    return {
        node.name: node
        for node in _parse(path).body
        if isinstance(node, ast.ClassDef)
    }


def _class_segment(path: Path, name: str) -> tuple[ast.ClassDef, str] | None:
    """The ClassDef node and its exact source segment for `name` in `path`."""
    src = path.read_text(encoding="utf-8")
    for node in _parse(path).body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            segment = ast.get_source_segment(src, node)
            assert segment is not None
            return node, segment
    return None


# ---------------------------------------------------------------------------
# Derived sets
# ---------------------------------------------------------------------------

def derived_mixins(pkg: Path) -> list[str]:
    """MapScreen's own bases under `screens/map/screen.py`, minus Textual's
    `Screen` — the concern set, derived, never hand-listed."""
    screen_path = pkg / "screens" / "map" / "screen.py"
    classes = _top_classes(screen_path)
    assert "MapScreen" in classes, f"MapScreen not defined in {screen_path}"
    return [
        base.id
        for base in classes["MapScreen"].bases
        if isinstance(base, ast.Name) and base.id != "Screen"
    ]


def sibling_screen_classes(pkg: Path) -> dict[str, str]:
    """Sibling screen classes of the ARQ target map: `{class name: dotted
    module}` for every `Screen`/`ModalScreen` subclass defined in a
    `screens/<m>` module that `app.py` imports from — the module set is
    derived from app.py's own relative imports, so nothing is hand-listed
    (screens not part of the target map, e.g. `palette`/`help`, are excluded
    by construction).  The `map` package is spine_b's territory."""
    app_py = pkg / "app.py"
    sibling_modules = {
        module
        for module, _name in _relative_imports(app_py)
        if module.startswith("screens.") and module.count(".") == 1
    }
    found: dict[str, str] = {}
    for path in sorted((pkg / "screens").glob("*.py")):
        dotted = f"screens.{path.stem}"
        if dotted not in sibling_modules:
            continue
        for node in _parse(path).body:
            if isinstance(node, ast.ClassDef) and _has_screen_base(node):
                found[node.name] = dotted
    return found


# ---------------------------------------------------------------------------
# Structural checkers — each takes a package root, so the GREEN tests run it
# on the real tree and the RED tests on a tmp-copy mutant.
# ---------------------------------------------------------------------------

def spine_a_report(pkg: Path) -> dict[str, list[str]]:
    """LLR-MOD.1.1: every sibling screen class lives under `mapper/screens/`
    and is re-exported from `app.py`; `app.py` defines no Screen subclass."""
    problems: dict[str, list[str]] = {
        "screen_class_not_reexported": [],
        "screen_class_shadowed_in_app": [],
        "screen_subclass_in_app": [],
    }
    app_py = pkg / "app.py"
    app_tree = _parse(app_py)
    imported = _relative_imports(app_py)
    defined_in_app = {
        node.name
        for node in app_tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef))
    }
    for name, dotted in sorted(sibling_screen_classes(pkg).items()):
        if (dotted, name) not in imported:
            problems["screen_class_not_reexported"].append(
                f"{name} is not re-exported from app.py ({dotted})"
            )
        if name in defined_in_app:
            problems["screen_class_shadowed_in_app"].append(name)
    for node in app_tree.body:
        if isinstance(node, ast.ClassDef) and _has_screen_base(node):
            problems["screen_subclass_in_app"].append(node.name)
    return problems


def b0_report(pkg: Path) -> dict[str, list[str]]:
    """LLR-MOD.1.2: `MapScreen` lives in the package core; the package
    `__init__` re-exports it and holds nothing else; `app.py` stays small and
    Screen-subclass-free."""
    problems: dict[str, list[str]] = {
        "core_missing_map_screen": [],
        "init_no_reexport": [],
        "init_extra_logic": [],
        "app_screen_subclass": [],
        "app_over_400_lines": [],
        "app_no_map_screen_reexport": [],
    }
    screen_path = pkg / "screens" / "map" / "screen.py"
    if not screen_path.is_file():
        problems["core_missing_map_screen"].append("screens/map/screen.py is absent")
    elif "MapScreen" not in _top_classes(screen_path):
        problems["core_missing_map_screen"].append(
            "MapScreen is not defined in screens/map/screen.py"
        )

    init_path = pkg / "screens" / "map" / "__init__.py"
    if not init_path.is_file():
        problems["init_no_reexport"].append("screens/map/__init__.py is absent")
    else:
        extra: list[str] = []
        for node in _parse(init_path).body:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                continue  # docstring
            if (
                isinstance(node, ast.ImportFrom)
                and node.level == 1
                and node.module == "screen"
            ):
                continue  # the MapScreen re-export itself
            if isinstance(node, ast.Assign) and all(
                isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets
            ):
                continue
            extra.append(type(node).__name__)
        if extra:
            problems["init_extra_logic"].append(
                f"screens/map/__init__.py holds logic: {sorted(extra)}"
            )
        reexports = _relative_imports(init_path)
        if ("screen", "MapScreen") not in reexports:
            problems["init_no_reexport"].append(
                "screens/map/__init__.py does not re-export MapScreen"
            )

    app_py = pkg / "app.py"
    text = app_py.read_text(encoding="utf-8")
    if len(text.splitlines()) > 400:
        problems["app_over_400_lines"].append(f"{len(text.splitlines())} lines")
    for node in _parse(app_py).body:
        if isinstance(node, ast.ClassDef) and _has_screen_base(node):
            problems["app_screen_subclass"].append(node.name)
    if ("screens.map.screen", "MapScreen") not in _relative_imports(app_py):
        problems["app_no_map_screen_reexport"].append(
            "app.py does not re-export MapScreen from screens.map.screen"
        )
    return problems


def one_feature_one_file_report(pkg: Path) -> dict[str, list[str]]:
    """The AT-068 core: MapScreen's derived concern mixins each live in their
    own module under `screens/map/` — no mixin missing, none in the core
    `screen.py`, no two sharing a file."""
    problems: dict[str, list[str]] = {
        "mixin_missing": [],
        "mixin_in_core": [],
        "mixins_share_file": [],
    }
    map_dir = pkg / "screens" / "map"
    files: dict[str, str] = {}
    for name in derived_mixins(pkg):
        locations = [
            path.name
            for path in sorted(map_dir.glob("*.py"))
            if name in _top_classes(path)
        ]
        if not locations:
            problems["mixin_missing"].append(name)
        elif "screen.py" in locations or len(locations) != 1:
            problems["mixin_in_core"].append(f"{name} defined in {locations}")
        else:
            files[name] = locations[0]
    owner_by_file: dict[str, str] = {}
    for name, file in sorted(files.items()):
        if file in owner_by_file:
            problems["mixins_share_file"].append(
                f"{owner_by_file[file]} and {name} share {file}"
            )
        else:
            owner_by_file[file] = name
    return problems


def spine_b_report(pkg: Path) -> dict[str, list[str]]:
    """LLR-MOD.1.3: the concern split holds, and `app.py` holds only
    MapperApp/main/imports."""
    report = one_feature_one_file_report(pkg)
    report["app_extra_defs"] = _app_extra_defs(pkg / "app.py")
    return report


def _app_extra_defs(app_py: Path) -> list[str]:
    """Anything in app.py beyond docstring, imports, `MapperApp`, `main` and
    the `__main__` guard."""
    extra: list[str] = []
    for node in _parse(app_py).body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue  # docstring
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(node, ast.ClassDef):
            if node.name != "MapperApp":
                extra.append(f"class {node.name}")
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name != "main":
                extra.append(f"def {node.name}")
            continue
        if isinstance(node, ast.Assign) and all(
            isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets
        ):
            continue
        if isinstance(node, ast.If) and _is_main_guard(node):
            continue
        extra.append(type(node).__name__)
    return extra


def _is_main_guard(node: ast.If) -> bool:
    test = node.test
    return (
        isinstance(test, ast.Compare)
        and isinstance(test.left, ast.Name)
        and test.left.id == "__name__"
        and len(test.ops) == 1
        and isinstance(test.ops[0], ast.Eq)
        and len(test.comparators) == 1
        and isinstance(test.comparators[0], ast.Constant)
        and test.comparators[0].value == "__main__"
    )


def _remove_relative_import(src: str, module: str, name: str) -> str:
    """Remove a single-name level-1 relative import line (a deleted
    re-export, the b0 negative control)."""
    tree = ast.parse(src)
    for node in tree.body:
        if (
            isinstance(node, ast.ImportFrom)
            and node.level == 1
            and node.module == module
            and len(node.names) == 1
            and node.names[0].name == name
            and node.names[0].asname is None
        ):
            lines = src.splitlines(keepends=True)
            assert node.end_lineno is not None
            del lines[node.lineno - 1 : node.end_lineno]
            return "".join(lines)
    raise AssertionError(f"import of {name} from {module} not found")


def _alias_relative_import(src: str, module: str, name: str) -> str:
    """Alias a single-name level-1 relative import to `_<name>` — a dropped
    re-export (the name no longer reaches app.py's namespace), the spine_a
    negative control."""
    tree = ast.parse(src)
    for node in tree.body:
        if (
            isinstance(node, ast.ImportFrom)
            and node.level == 1
            and node.module == module
            and len(node.names) == 1
            and node.names[0].name == name
            and node.names[0].asname is None
        ):
            line = src.splitlines(keepends=True)[node.lineno - 1]
            assert node.end_col_offset is not None
            replacement = line[: node.col_offset] + line[node.col_offset :].replace(
                f"import {name}", f"import {name} as _{name}", 1
            )
            lines = src.splitlines(keepends=True)
            lines[node.lineno - 1] = replacement
            return "".join(lines)
    raise AssertionError(f"import of {name} from {module} not found")


# ---------------------------------------------------------------------------
# LLR-MOD.1.1 — sibling screens own their names
# ---------------------------------------------------------------------------

def test_llr_mod_1_1_spine_a_screens_own_their_names():
    """GREEN: every derived sibling screen class is re-exported from app.py
    and app.py defines no Screen subclass; at runtime every re-export is the
    same object (`is` identity through the re-export)."""
    report = spine_a_report(PACKAGE)
    assert report == {key: [] for key in report}

    import mapper.app as app_module

    screens = sibling_screen_classes(PACKAGE)
    assert screens, "no sibling screen classes derived from mapper/screens/"
    for name, dotted in sorted(screens.items()):
        owner = importlib.import_module(f"mapper.{dotted}")
        assert getattr(app_module, name) is getattr(owner, name), (
            f"mapper.app.{name} is not {dotted}.{name}"
        )


def test_llr_mod_1_1_spine_a_red_dropped_reexport_is_reported(tmp_path):
    """RED (planted defect: the `from .screens.repo import RepoScreen`
    re-export line is deleted from the tmp copy's app.py): the checker must
    report RepoScreen as no longer re-exported."""
    copy = tmp_path / "mapper"
    shutil.copytree(PACKAGE, copy)
    app_py = copy / "app.py"
    app_py.write_text(
        _alias_relative_import(
            app_py.read_text(encoding="utf-8"), "screens.repo", "RepoScreen"
        ),
        encoding="utf-8",
    )

    report = spine_a_report(copy)
    assert any("RepoScreen" in item for item in report["screen_class_not_reexported"]), (
        report
    )


def test_llr_mod_1_1_spine_a_red_screen_subclass_left_in_app_is_reported(tmp_path):
    """RED (planted defect: a `Screen` subclass is planted back into the tmp
    copy's app.py — the pre-A1 shape): the checker must report it."""
    copy = tmp_path / "mapper"
    shutil.copytree(PACKAGE, copy)
    app_py = copy / "app.py"
    app_py.write_text(
        app_py.read_text(encoding="utf-8")
        + "\nfrom textual.screen import Screen\n\n\nclass LeftOverScreen(Screen):\n    pass\n",
        encoding="utf-8",
    )

    report = spine_a_report(copy)
    assert "LeftOverScreen" in report["screen_subclass_in_app"], report


# ---------------------------------------------------------------------------
# LLR-MOD.1.2 — MapScreen lives in the package core
# ---------------------------------------------------------------------------

def test_llr_mod_1_2_b0_map_screen_lives_in_the_package_core():
    """GREEN: MapScreen is defined in screens/map/screen.py, the package
    __init__ re-exports it (and nothing else), app.py is under 400 lines and
    holds no Screen subclass — and at runtime `mapper.app.MapScreen is
    mapper.screens.map.MapScreen`."""
    report = b0_report(PACKAGE)
    assert report == {key: [] for key in report}

    import mapper.app as app_module
    import mapper.screens.map as map_pkg

    assert app_module.MapScreen is map_pkg.MapScreen
    file = inspect.getfile(app_module.MapScreen).replace("\\", "/")
    assert file.endswith("mapper/screens/map/screen.py"), file


def test_llr_mod_1_2_b0_red_missing_core_reexport_is_reported(tmp_path):
    """RED (planted defect: the `from .screen import MapScreen` re-export is
    deleted from the tmp copy's screens/map/__init__.py): the checker must
    report it."""
    copy = tmp_path / "mapper"
    shutil.copytree(PACKAGE, copy)
    init_py = copy / "screens" / "map" / "__init__.py"
    init_py.write_text(
        _remove_relative_import(
            init_py.read_text(encoding="utf-8"), "screen", "MapScreen"
        ),
        encoding="utf-8",
    )

    report = b0_report(copy)
    assert report["init_no_reexport"], report


def test_llr_mod_1_2_b0_red_screen_subclass_left_in_app_is_reported(tmp_path):
    """RED (planted defect: a Screen subclass is planted into the tmp copy's
    app.py, which shall hold only MapperApp): the checker must report it."""
    copy = tmp_path / "mapper"
    shutil.copytree(PACKAGE, copy)
    app_py = copy / "app.py"
    app_py.write_text(
        app_py.read_text(encoding="utf-8")
        + "\nfrom textual.screen import Screen\n\n\nclass StrayScreen(Screen):\n    pass\n",
        encoding="utf-8",
    )

    report = b0_report(copy)
    assert "StrayScreen" in report["app_screen_subclass"], report


# ---------------------------------------------------------------------------
# LLR-MOD.1.3 — each concern method lives in its own module
# ---------------------------------------------------------------------------

def test_llr_mod_1_3_spine_b_each_concern_lives_in_its_own_module():
    """GREEN: the derived concern mixins each live in their own module under
    screens/map/, no two share a file, app.py holds only MapperApp/main +
    imports — and at runtime MapScreen.__mro__ shows the same concern classes
    ahead of Textual's Screen."""
    report = spine_b_report(PACKAGE)
    assert report == {key: [] for key in report}

    from textual.screen import Screen

    from mapper.screens.map.screen import MapScreen

    runtime_mixins = [
        base
        for base in MapScreen.__mro__
        if base is not MapScreen and base.__module__.startswith("mapper.screens.map")
    ]
    assert runtime_mixins, "no concern mixins derived from MapScreen's MRO"
    assert [base.__name__ for base in runtime_mixins] == derived_mixins(PACKAGE)
    assert MapScreen.__mro__.index(Screen) > MapScreen.__mro__.index(runtime_mixins[-1])
    modules = [base.__module__ for base in runtime_mixins]
    assert len(set(modules)) == len(modules), (
        f"two concerns share a module: {modules}"
    )


def test_llr_mod_1_3_spine_b_red_merged_mixins_are_reported(tmp_path):
    """RED (planted defect: the first two derived concern mixins are merged
    into one file — one concern's class is appended to the other's module and
    its own module deleted): the checker must report the shared file."""
    copy = tmp_path / "mapper"
    shutil.copytree(PACKAGE, copy)
    map_dir = copy / "screens" / "map"
    moved, host = derived_mixins(copy)[:2]
    moved_path = map_dir / one_feature_one_file_owner(copy, moved)
    found = _class_segment(moved_path, moved)
    assert found is not None, f"{moved} not defined in {moved_path}"
    _, segment = found
    host_path = map_dir / one_feature_one_file_owner(copy, host)
    host_path.write_text(
        host_path.read_text(encoding="utf-8") + "\n\n" + segment + "\n",
        encoding="utf-8",
    )
    moved_path.unlink()

    report = spine_b_report(copy)
    assert any(
        moved in item and host in item for item in report["mixins_share_file"]
    ), report


def test_llr_mod_1_3_spine_b_red_mixin_moved_into_core_is_reported(tmp_path):
    """RED (planted defect: the last derived concern mixin is moved into the
    core screen.py — one file now edits two concerns): the checker must
    report the mixin in the core module."""
    copy = tmp_path / "mapper"
    shutil.copytree(PACKAGE, copy)
    map_dir = copy / "screens" / "map"
    name = derived_mixins(copy)[-1]
    own_file = one_feature_one_file_owner(copy, name)
    own_path = map_dir / own_file
    found = _class_segment(own_path, name)
    assert found is not None, f"{name} not defined in {own_path}"
    _, segment = found
    screen_path = map_dir / "screen.py"
    screen_path.write_text(
        screen_path.read_text(encoding="utf-8") + "\n\n" + segment + "\n",
        encoding="utf-8",
    )
    own_path.unlink()

    report = spine_b_report(copy)
    assert any(name in item for item in report["mixin_in_core"]), report


def one_feature_one_file_owner(pkg: Path, mixin: str) -> str:
    """The single file under screens/map/ defining `mixin` (helper for the
    mutants; the checker's own derivation is what is asserted)."""
    map_dir = pkg / "screens" / "map"
    owners = [
        path.name
        for path in sorted(map_dir.glob("*.py"))
        if mixin in _top_classes(path)
    ]
    assert len(owners) == 1, f"{mixin} expected in exactly one module, found {owners}"
    return owners[0]


# ---------------------------------------------------------------------------
# AT-068 — one feature, one file (HLR-MOD.1's black-box reading of the tree)
# ---------------------------------------------------------------------------

def test_at068_one_feature_one_file(tmp_path):
    """AT-068: for each concern, the set of files you would edit to change
    that concern is exactly ONE module.  GREEN: the concern->module map
    derived from MapScreen's bases' `__module__` has one distinct module per
    concern, none of them the core screen.py, and the AST checker agrees on
    the real tree.  RED: a tmp copy with two derived concerns merged into one
    file is reported."""
    from mapper.screens.map.screen import MapScreen

    concerns = [
        base
        for base in MapScreen.__mro__
        if base is not MapScreen and base.__module__.startswith("mapper.screens.map")
    ]
    assert concerns, "no concern mixins derived from MapScreen's MRO"
    modules = [base.__module__ for base in concerns]
    assert len(set(modules)) == len(modules), (
        f"one feature does not map to one file: {modules}"
    )
    for module in modules:
        path = PACKAGE.joinpath(*module.split(".")[1:]).with_suffix(".py")
        assert path.is_file(), f"{module} is not a shipped module"
        assert path.name != "screen.py", (
            f"concern {module} lives in the core screen.py"
        )

    assert one_feature_one_file_report(PACKAGE) == {
        "mixin_missing": [],
        "mixin_in_core": [],
        "mixins_share_file": [],
    }

    # RED — permanent negative control on a tmp copy: two concerns in one file.
    copy = tmp_path / "mapper"
    shutil.copytree(PACKAGE, copy)
    map_dir = copy / "screens" / "map"
    moved, host = derived_mixins(copy)[:2]
    moved_path = map_dir / one_feature_one_file_owner(copy, moved)
    found = _class_segment(moved_path, moved)
    assert found is not None, f"{moved} not defined in {moved_path}"
    _, segment = found
    host_path = map_dir / one_feature_one_file_owner(copy, host)
    host_path.write_text(
        host_path.read_text(encoding="utf-8") + "\n\n" + segment + "\n",
        encoding="utf-8",
    )
    moved_path.unlink()

    report = one_feature_one_file_report(copy)
    assert any(
        moved in item and host in item for item in report["mixins_share_file"]
    ), report
