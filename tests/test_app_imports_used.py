"""B-104 / AT-064 of `2026-10-09-canon-batch` (HLR-CAN.2, LLR-CAN.2.1), generalised to the
package by LLR-MOD.5.1 (Inc-0 of batch `2026-10-09-modular-batch`).

WHY: an unused import in the largest module hides the next real lint warning
among old ones. `ruff` is not a declared project dependency, so this AST test
is the guard. The split of `mapper/app.py` into `mapper/screens/**` moves code,
not the rule: every module of the package the split creates — `mapper/app.py`
plus every `mapper/screens/**/*.py` that exists — is held to the same check, so
a moved module cannot smuggle an unused import past a stale `app.py`-only pin.

Rule for future deliberate re-exports: add the name to `ALLOWED_UNUSED` under
its package-relative path, with a reason, never weaken the check.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _package_modules() -> list[str]:
    """`mapper/app.py` plus every `mapper/screens/**` module, as package-relative posix paths."""
    files = ["mapper/app.py"]
    files += sorted(
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in (ROOT / "mapper" / "screens").rglob("*.py")
    )
    return files


MODULES = _package_modules()

# Deliberate re-exports — and pre-existing violations recorded at Inc-0, when this
# check first reached `mapper/screens/**` and Inc-0 could not edit product files —
# go here, keyed by package-relative path, each name with its reason.
ALLOWED_UNUSED: dict[str, dict[str, str]] = {
    "mapper/app.py": {
        name: "re-export for from-mapper.app import sites (LLR-MOD.3.1)"
        for name in (
            "COUNT_REGION_ID", "MAX_RENDER_NODES", "PAN_INERT_HINT", "SEARCH_ACTIVE_LABEL",
            "SEARCH_COUNT_SUBJECT", "SEARCH_SUSPENDED_NOTICE", "SearchIndex", "_ConfirmScreen",
            "_FichaScreen", "_QUERY_ECHO_CELLS", "_path_refusal", "map_hint", "pan_extent",
            "save_svg", "GitHubConnector", "NavigationModel", "RepoScreen",
        )
    },
    "mapper/screens/__init__.py": {
        name: "deliberate re-export declared in __all__"
        for name in (
            "CommandPalette", "CoverageScreen", "DraftGuardScreen", "EditorScreen",
            "FactoryScreen", "HelpScreen", "SettingsScreen",
        )
    },
    "mapper/screens/map/__init__.py": {
        "MapScreen": "deliberate re-export declared in __all__ (B0 moved MapScreen here)",
    },
    "mapper/screens/factory.py": {
        "Node": "pre-existing unused import, recorded at Inc-0 (test-only increment; no product edit allowed)",
        "Vertical": "pre-existing unused import, recorded at Inc-0 (test-only increment; no product edit allowed)",
    },
    "mapper/screens/settings.py": {
        "darkside": "pre-existing unused import, recorded at Inc-0; only mentioned in docstrings/comments",
    },
}


def unused_imports(source: str) -> set[str]:
    """Return the module-level import names of `source` that are never used.

    - bound names: `import a.b` binds `a`; `import x as y` binds `y`;
      `from m import n` binds `n`; `from m import n as z` binds `z`;
      `from __future__ import ...` is skipped; only imports that are direct
      children of the module (module level) count.
    - used names: every `ast.Name` in Load context anywhere in the module —
      this includes the base Name of an `ast.Attribute` chain such as
      `re.compile` -> `re`. A name appearing only inside a string, docstring or
      comment does NOT count (AST strings are `ast.Constant`).
    - per-file allowances (deliberate re-exports and Inc-0-recorded
      pre-existing violations) are subtracted by the caller, which knows the
      file the source came from; this checker stays a pure function of source.
    """
    tree = ast.parse(source)
    bound: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                bound.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module == "__future__":
                continue
            for alias in node.names:
                bound.add(alias.asname or alias.name)
    used = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    return bound - used


@pytest.mark.parametrize("rel", MODULES)
def test_at_064_app_imports_nothing_it_does_not_use(rel):
    """AT-064: no module of the package imports a name it does not use."""
    source = (ROOT / rel).read_text(encoding="utf-8")
    unused = unused_imports(source) - set(ALLOWED_UNUSED.get(rel, ()))
    assert unused == set(), f"{rel}: unused imports: {sorted(unused)}"


CASES = [
    ("import os\nos.getcwd()\n", set()),
    ("import os\n", {"os"}),
    ("import a.b\na.b.c()\n", set()),
    ("import a.b\n", {"a"}),
    ("import numpy as np\nnp.zeros(1)\n", set()),
    ("import numpy as np\n", {"np"}),
    ("from m import n as z\n", {"z"}),
    ("from m import n\nn()\n", set()),
    ("from __future__ import annotations\n", set()),
    ("import re\nx = 're.compile'\n", {"re"}),
    ("import re\n\"\"\"re is mentioned\"\"\"\n", {"re"}),
    # CR-2, documented limits: a quoted annotation is a string, so it does not count as a
    # use (add the name to ALLOWED_UNUSED if that is ever deliberate) ...
    ("import os\nx: 'os.PathLike'\n", {"os"}),
    # ... and only module-level import statements bind names: a guarded import is not checked.
    ("try:\n    import os\nexcept ImportError:\n    pass\n", set()),
]


@pytest.mark.parametrize("source, expected", CASES)
def test_llr_can_2_1_checker_arms(source, expected):
    """Synthetic sources arm the checker itself (boundary catalog of LLR-CAN.2.1)."""
    assert unused_imports(source) == expected
