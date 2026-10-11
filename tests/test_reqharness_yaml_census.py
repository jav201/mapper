"""The permanent "never `yaml.load`" census over `mapper/` (R-SCALE a + R21;
LLR-RH.1.1) — code-review follow-up M2.

Every YAML parse in the product is either the reqharness loader subclass
(`ReqHarnessLoader`, on CSafeLoader/SafeLoader) passed EXPLICITLY as
`Loader=`, or the safe spellings the rest of the project already uses —
`yaml.safe_load` (mapper/store.py, mapper/diff.py, mapper/screens/map/undo.py)
and `yaml.safe_dump`.  This AST scan refuses any call to `yaml.load` /
`yaml.load_all` / `yaml.full_load` / `yaml.unsafe_load` — including through
`import yaml as ...` and `from yaml import ...` aliases — unless the call
passes `Loader=ReqHarnessLoader`, the one loader the reqharness core allows.
The planted-violation arm on a tmp copy is the positive control: a census
that can only ever return an empty list is not a census.
"""
from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAPPER_PKG = REPO_ROOT / "mapper"

#: Every PyYAML entry point that bypasses safe_load; `load_all` with an
#: explicit `Loader=ReqHarnessLoader` (config.py) is the one sanctioned call.
BANNED_LOADS = frozenset({"load", "load_all", "full_load", "unsafe_load"})


def _passes_reqharness_loader(node: ast.Call) -> bool:
    for keyword in node.keywords:
        if keyword.arg == "Loader":
            value = keyword.value
            return (
                isinstance(value, ast.Name) and value.id == "ReqHarnessLoader"
            ) or (
                isinstance(value, ast.Attribute)
                and value.attr == "ReqHarnessLoader"
            )
    return False


def _yaml_load_violations(path: Path) -> list[str]:
    """Every banned YAML-load call in *path* that is not Loader=ReqHarnessLoader."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    module_aliases = {"yaml"}
    direct_aliases: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            module_aliases.update(
                alias.asname or alias.name for alias in node.names if alias.name == "yaml"
            )
        elif isinstance(node, ast.ImportFrom) and node.module == "yaml":
            direct_aliases.update(
                alias.asname or alias.name
                for alias in node.names
                if alias.name in BANNED_LOADS
            )
    violations = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute):
            if not (
                isinstance(func.value, ast.Name)
                and func.value.id in module_aliases
                and func.attr in BANNED_LOADS
            ):
                continue
            label = f"{func.value.id}.{func.attr}"
        elif isinstance(func, ast.Name):
            if func.id not in direct_aliases:
                continue
            label = func.id
        else:
            continue
        if _passes_reqharness_loader(node):
            continue
        violations.append(f"{path.name}:{node.lineno}: {label}(...)")
    return violations


def _mapper_sources(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)


def test_no_banned_yaml_load_ships_in_mapper():
    """The census arm over the live package: zero banned calls, and the scan
    input is non-empty (a census over nothing passes vacuously)."""
    files = _mapper_sources(MAPPER_PKG)
    assert files, "the census scanned no files — it would pass vacuously"
    violations = [
        report for path in files for report in _yaml_load_violations(path)
    ]
    assert not violations, "banned yaml.load call(s): " + "; ".join(violations)


def test_yaml_load_census_flags_a_planted_violation(tmp_path):
    """The positive control: the SAME scan over a tmp copy flags every banned
    spelling — plain attribute, aliased module import, and from-import — and
    admits the compliant `Loader=ReqHarnessLoader` form plus `yaml.safe_load`
    and `yaml.safe_dump`."""
    planted = tmp_path / "planted.py"
    planted.write_text(
        "import yaml\n"
        "import yaml as yl\n"
        "from yaml import load, full_load\n"
        "def f(text):\n"
        "    yaml.load(text)\n"
        "    yl.load_all(text)\n"
        "    load(text)\n"
        "    full_load(text)\n"
        "    yaml.unsafe_load(text)\n"
        "    yaml.load_all(text, Loader=ReqHarnessLoader)\n"
        "    yaml.safe_load(text)\n"
        "    yaml.safe_dump({})\n",
        encoding="utf-8",
    )
    violations = _yaml_load_violations(planted)
    assert len(violations) == 5, violations
    assert all("Loader" not in report for report in violations)
