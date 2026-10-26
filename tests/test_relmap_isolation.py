"""HLR-RMP.2 / LLR-RMP.2.1, LLR-RMP.1.2, LLR-RMM.1.1 (floor) -- the relation kind is isolated, profile-blind
and Python-3.10-clean; TC-RM-01 pins that the tree kind still refuses a cycle.

Every property is DERIVED from the shipped tree by AST (C-31); each checker is a FUNCTION of
source text so a planted-violation arm proves it can report a failure (a census that cannot
fail is the vacuous check this batch exists to avoid).  The checkers walk the WHOLE tree, so
function-local imports are counted in both import forms (LLR-RMP.2.1 boundary catalog).
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

import mapper
from mapper.relmap.profile import REQHARNESS

PKG = Path(mapper.__file__).resolve().parent
RELMAP = PKG / "relmap"

ALLOWED_OSOPEN = frozenset({
    "read_capped", "ContentReadError", "MAX_MAP_BYTES", "MAX_NODES", "MAX_EDGES",
    "confine_reason", "is_link"})
ALLOWED_DERIVE = frozenset({"parse_canon", "CanonObject", "LIMIT_ROLES_YML_BYTES"})
# every module that is NOT the standard library or `mapper`: PyYAML only
THIRD_PARTY_OK = frozenset({"yaml"})

# LLR-RMM.1.1: names introduced after Python 3.10, as qualified names (and `import` forms).
BANNED_QUALIFIED = frozenset({
    "enum.StrEnum", "typing.Self", "typing.assert_never", "typing.LiteralString",
    "itertools.batched", "datetime.UTC", "pathlib.Path.walk"})
BANNED_BUILTINS = frozenset({"ExceptionGroup", "BaseExceptionGroup"})
BANNED_MODULES = frozenset({"tomllib"})


def _relmap_files() -> list[Path]:
    return sorted(RELMAP.glob("*.py"))


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


# ------------------------------------------------------------------ import resolution


def _imports(tree: ast.AST, module_name: str):
    """(absolute module, imported name | None, lineno) for every import at any scope.

    `module_name` is the dotted name of the file being read, so a relative import resolves.
    `from mapper import x` is the submodule `mapper.x` (name None).
    """
    package = module_name.rsplit(".", 1)[0] if "." in module_name else ""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name, None, node.lineno
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                parts = package.split(".")
                base = ".".join(parts[: len(parts) - node.level + 1])
                target = f"{base}.{node.module}" if node.module else base
            else:
                target = node.module or ""
            for alias in node.names:
                if target == "mapper":
                    yield f"mapper.{alias.name}", None, node.lineno
                else:
                    yield target, alias.name, node.lineno


def forbidden_imports(source: str, module_name: str) -> list[str]:
    """The imports LLR-RMP.2.1 forbids in a relmap module (stdlib, PyYAML, own modules and the named mapper names pass)."""
    found = []
    for mod, name, line in _imports(ast.parse(source), module_name):
        root = mod.split(".")[0]
        if root != "mapper":
            if root in sys.stdlib_module_names or root in THIRD_PARTY_OK:
                continue
            found.append(f"{line}: third-party {mod}")
        elif mod == "mapper.relmap" or mod.startswith("mapper.relmap."):
            continue
        elif mod == "mapper.osopen":
            if name not in ALLOWED_OSOPEN:
                found.append(f"{line}: {mod}.{name}")
        elif mod == "mapper.yamlscan":
            continue
        elif mod == "mapper.reqharness.derive":
            if name not in ALLOWED_DERIVE:
                found.append(f"{line}: {mod}.{name}")
        else:
            found.append(f"{line}: {mod}" + (f".{name}" if name else ""))
    return found


def importers_of_relmap(source: str, module_name: str) -> bool:
    for mod, _name, _line in _imports(ast.parse(source), module_name):
        if mod == "mapper.relmap" or mod.startswith("mapper.relmap."):
            return True
    return False


def _module_name(path: Path) -> str:
    rel = path.relative_to(PKG.parent).with_suffix("")
    return ".".join(rel.parts)


def test_the_relmap_package_exists_and_the_probe_sees_files():
    names = {p.name for p in _relmap_files()}
    assert {"__init__.py", "profile.py", "model.py"} <= names, names


@pytest.mark.parametrize("path", _relmap_files(), ids=lambda p: p.name)
def test_relmap_modules_import_only_what_the_contract_allows(path):
    assert forbidden_imports(path.read_text(encoding="utf-8"), _module_name(path)) == []


@pytest.mark.parametrize(
    "source",
    [
        "from mapper.store import MapStore\n",
        "import mapper.model\n",
        "from mapper import model\n",
        "def f():\n    from mapper.model import Graph\n",  # function-local, from-form
        "def f():\n    import mapper.mermaid\n",  # function-local, plain form
        "from mapper.osopen import open_external\n",
        "from mapper.reqharness.derive import load_canon\n",
        "from mapper.reqharness import audit\n",
        "from ..model import Graph\n",  # relative into the tree kind
        "import textual\n",
        "import rich\n",
    ],
)
def test_planted_violations_are_reported(source):
    assert forbidden_imports(source, "mapper.relmap.model") != []


@pytest.mark.parametrize(
    "source",
    [
        "import os, sys, re\nfrom dataclasses import dataclass\n",
        "import yaml\n",
        "from mapper.osopen import MAX_NODES, MAX_EDGES, read_capped\n",
        "from mapper.reqharness.derive import parse_canon\n",
        "from mapper.relmap.profile import Profile\n",
        "from .profile import Profile\n",
        "from mapper.relmap import profile\n",
        "import mapper.yamlscan\n",
    ],
)
def test_allowed_imports_are_not_flagged(source):
    assert forbidden_imports(source, "mapper.relmap.model") == []


def test_only_app_and_the_package_import_relmap():
    seen = {}
    for path in sorted(PKG.rglob("*.py")):
        rel = path.relative_to(PKG).as_posix()
        if rel.startswith("relmap/"):
            continue
        # R2 ARQ amendment (the `screens/relmap` row of docs/ARCHITECTURE.md
        # §3): the relation screen package is the sanctioned D3 consumer — it
        # imports `relmap` the way `app` does, and the census below is about
        # everyone ELSE staying out of the headless core.
        if rel.startswith("screens/relmap/"):
            continue
        # R2 amendment (relmap-r2 Inc-6, lane L6 — LLR-RVH.1.1/.3.1 draft-time
        # verification names `descriptor.discover_descriptors` /
        # `default_descriptor` for Home's recents build): `screens/home.py`
        # discovers and routes relation descriptors through the same D3 door —
        # the read-only discovery API only, never the derivation engine.
        if importers_of_relmap(path.read_text(encoding="utf-8"), _module_name(path)):
            seen[rel] = True
    assert set(seen) <= {"app.py", "screens/home.py"}, seen


@pytest.mark.parametrize(
    "source,name",
    [
        ("from mapper.relmap.model import build_map\n", "mapper.model"),
        ("import mapper.relmap\n", "mapper.store"),
        ("from mapper import relmap\n", "mapper.reqharness.audit"),
        ("from .relmap import model\n", "mapper.app"),
        ("def f():\n    from .relmap import model\n", "mapper.model"),
    ],
)
def test_the_importer_census_can_see_an_importer(source, name):
    assert importers_of_relmap(source, name)


def test_init_re_exports_nothing():
    tree = _parse(RELMAP / "__init__.py")
    body = [n for n in tree.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
    assert body == [], "relmap/__init__.py must hold no import, no assignment, no __all__"


# ------------------------------------------------------------------ LLR-RMP.1.2


def profile_literals(*profiles) -> set[str]:
    out: set[str] = set()
    for p in profiles:
        out.update(p.node_kinds)
        out.update(t.name for t in p.edge_types)
        out.update(g.kind for g in p.gaps)
    return out


def engine_literal_violations(source: str, literals: set[str]) -> list[str]:
    """String literals equal to a profile name.  An empty literal set is refused (empty-set guard)."""
    if not literals:
        raise ValueError("a census over an empty literal set proves nothing")
    return [
        f"{n.lineno}: {n.value!r}"
        for n in ast.walk(ast.parse(source))
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value in literals
    ]


def test_engine_names_no_kind():
    literals = profile_literals(REQHARNESS)
    assert len(literals) >= 17, literals  # 5 kinds + 4 edge types + 8 gap kinds
    engine = [p for p in _relmap_files() if p.name in ("model.py", "gaps.py")]
    assert "model.py" in {p.name for p in engine}
    for path in engine:
        assert engine_literal_violations(path.read_text(encoding="utf-8"), literals) == [], path.name


@pytest.mark.parametrize("planted", ["refines", "US", "HLR WITHOUT LLR", "binds"])
def test_engine_census_finds_a_planted_literal(planted):
    literals = profile_literals(REQHARNESS)
    src = f"def f(edge):\n    return edge.type == {planted!r}\n"
    assert len(engine_literal_violations(src, literals)) >= 1


def test_engine_census_refuses_an_empty_literal_set():
    with pytest.raises(ValueError):
        engine_literal_violations("x = 1\n", set())


# ------------------------------------------------------------------ LLR-RMM.1.1 floor


def _dotted(node: ast.AST, alias: dict[str, str]) -> str | None:
    if isinstance(node, ast.Name):
        return alias.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        base = _dotted(node.value, alias)
        return None if base is None else f"{base}.{node.attr}"
    return None


def floor_violations(source: str) -> list[str]:
    """Constructs and names past Python 3.10 (parse under the 3.10 grammar, then a qualified-name census)."""
    tree = ast.parse(source, feature_version=(3, 10))
    alias: dict[str, str] = {}
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                alias[a.asname or a.name.split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
                if a.name.split(".")[0] in BANNED_MODULES:
                    found.append(f"{node.lineno}: import {a.name}")
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod.split(".")[0] in BANNED_MODULES:
                found.append(f"{node.lineno}: from {mod}")
            for a in node.names:
                alias[a.asname or a.name] = f"{mod}.{a.name}"
                if f"{mod}.{a.name}" in BANNED_QUALIFIED:
                    found.append(f"{node.lineno}: from {mod} import {a.name}")
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            dotted = _dotted(node, alias)
            if dotted in BANNED_QUALIFIED:
                found.append(f"{node.lineno}: {dotted}")
            # `Path.walk` is reached through instances, so any `.walk` whose receiver is not
            # the `os` module is flagged; `os.walk` is a 3.10 name and stays allowed.
            if node.attr == "walk" and _dotted(node.value, alias) != "os":
                found.append(f"{node.lineno}: <receiver>.walk")
        elif isinstance(node, ast.Name) and node.id in BANNED_BUILTINS:
            found.append(f"{node.lineno}: {node.id}")
    return found


def _floor_files() -> list[Path]:
    files = list(_relmap_files())
    ys = PKG / "yamlscan.py"
    if ys.exists():
        files.append(ys)
    return files


def test_py310_floor():
    files = _floor_files()
    assert len(files) >= 3, files
    for path in files:
        assert floor_violations(path.read_text(encoding="utf-8")) == [], path.name


@pytest.mark.parametrize(
    "planted",
    [
        "import tomllib\n",
        "from tomllib import loads\n",
        "import enum\nclass K(enum.StrEnum): pass\n",
        "from enum import StrEnum\n",
        "import typing\nx: typing.Self\n",
        "from typing import assert_never\n",
        "from typing import LiteralString\n",
        "import itertools\nitertools.batched([], 2)\n",
        "from itertools import batched\n",
        "import datetime\nx = datetime.UTC\n",
        "from datetime import UTC\n",
        "from pathlib import Path\nlist(Path('.').walk())\n",
        "try:\n    pass\nexcept ExceptionGroup:\n    pass\n",
    ],
)
def test_py310_floor_finds_a_planted_violation(planted):
    assert len(floor_violations(planted)) >= 1


@pytest.mark.parametrize(
    "legit",
    [
        "import os\nfor _ in os.walk('.'):\n    pass\n",
        "from os import walk\nfor _ in walk('.'):\n    pass\n",
        "import enum\nclass K(enum.Enum): pass\n",
        "from typing import Optional, Any\n",
        "from datetime import datetime, timezone\nx = timezone.utc\n",
        "import itertools\nitertools.chain([], [])\n",
    ],
)
def test_py310_floor_does_not_flag_a_legitimate_310_name(legit):
    assert floor_violations(legit) == []


def test_py310_floor_rejects_a_post_310_grammar():
    with pytest.raises(SyntaxError):
        floor_violations("try:\n    pass\nexcept* ValueError:\n    pass\n")


# ------------------------------------------------------------------ TC-RM-01


def test_tc_rm_01_a_cyclic_tree_map_is_still_refused_at_load(tmp_path):
    """Regression pin (it gates nothing new, and says so): the tree kind keeps refusing a cycle."""
    from mapper.mermaid import CYCLE_ARROW, MermaidError, parse
    from mapper.store import MapStore, MapStoreError

    cyclic = "graph TD\n    a[A] --> b[B]\n    b --> c[C]\n    c --> a\n"
    with pytest.raises(MermaidError) as err:
        parse(cyclic)
    assert err.value.cycle == ["a", "b", "c", "a"]
    store = MapStore(tmp_path / "workspace")
    (store.workspace / "ciclico.mmd").write_text(cyclic, encoding="utf-8")
    with pytest.raises(MapStoreError) as load_err:
        store.load("ciclico")
    assert str(load_err.value) == "the map has a cycle: " + CYCLE_ARROW.join(["a", "b", "c", "a"])


# ------------------------------------------------------------------ stdlib bans (LED .46, M-RMP-7)

# ARCHITECTURE section 3 bans these for `relmap` (and `yamlscan` is a leaf with no I/O wording at all);
# LLR-RMP.2.1 permits the whole standard library, so without this census nothing enforces the ban.
BANNED_PROCESS_NETWORK = frozenset({
    "subprocess", "socket", "urllib", "http", "ftplib", "smtplib", "requests"})
BANNED_OS_CALLS = frozenset({
    "system", "popen", "startfile", "fork", "execv", "execve", "execl", "execle", "execlp", "execvp",
    "spawnv", "spawnl", "spawnve", "spawnvp"})
WRITE_MODE_CHARS = frozenset("wax+")
WRITE_FLAG_NAMES = frozenset({"O_WRONLY", "O_RDWR", "O_CREAT", "O_APPEND", "O_TRUNC", "O_EXCL"})
WRITE_METHODS = frozenset({"write_text", "write_bytes"})


def _mode_argument(call: ast.Call, positional: int):
    for kw in call.keywords:
        if kw.arg == "mode":
            return kw.value
    return call.args[positional] if len(call.args) > positional else None


def stdlib_ban_violations(source: str) -> list[str]:
    """Imports of a process or network module, process-spawning `os` calls and any WRITE-mode open."""
    tree = ast.parse(source)
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] in BANNED_PROCESS_NETWORK:
                    found.append(f"{node.lineno}: import {a.name}")
        elif isinstance(node, ast.ImportFrom):
            if not node.level and (node.module or "").split(".")[0] in BANNED_PROCESS_NETWORK:
                found.append(f"{node.lineno}: from {node.module}")
        elif isinstance(node, ast.Constant) and node.value in WRITE_FLAG_NAMES:
            found.append(f"{node.lineno}: write flag {node.value!r}")
        elif isinstance(node, ast.Attribute) and node.attr in WRITE_FLAG_NAMES:
            found.append(f"{node.lineno}: write flag {node.attr}")
        elif isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name) and fn.id == "open":
                mode, label = _mode_argument(node, 1), "open"
            elif isinstance(fn, ast.Attribute) and fn.attr in WRITE_METHODS:
                found.append(f"{node.lineno}: .{fn.attr}()")
                continue
            elif isinstance(fn, ast.Attribute) and fn.attr in BANNED_OS_CALLS:
                found.append(f"{node.lineno}: .{fn.attr}()")
                continue
            elif isinstance(fn, ast.Attribute) and fn.attr in ("open", "fdopen"):
                receiver = fn.value.id if isinstance(fn.value, ast.Name) else ""
                if receiver == "os" and fn.attr == "open":
                    continue  # its flags are policed by the write-flag names above
                mode, label = _mode_argument(node, 1 if receiver in ("io", "builtins", "os") else 0), f".{fn.attr}"
            else:
                continue
            if mode is None:
                continue
            if not (isinstance(mode, ast.Constant) and isinstance(mode.value, str)):
                found.append(f"{node.lineno}: {label}() with a non-literal mode")
            elif WRITE_MODE_CHARS & set(mode.value):
                found.append(f"{node.lineno}: {label}(mode={mode.value!r})")
    return found


def _ban_files() -> list[Path]:
    files = list(_relmap_files())
    ys = PKG / "yamlscan.py"
    if ys.exists():
        files.append(ys)
    return files


def test_stdlib_bans():
    files = _ban_files()
    assert {"descriptor.py", "model.py", "gaps.py", "yamlscan.py"} <= {p.name for p in files}, files
    for path in files:
        assert stdlib_ban_violations(path.read_text(encoding="utf-8")) == [], path.name


@pytest.mark.parametrize(
    "planted",
    [
        "import subprocess\n",
        "import subprocess as sp\n",
        "from subprocess import run\n",
        "def f():\n    import socket\n",
        "import urllib.request\n",
        "from http import client\n",
        "from urllib.parse import quote\n",
        "import ftplib\n",
        "import smtplib\n",
        "import requests\n",
        "import os\nos.system('x')\n",
        "import os\nos.popen('x')\n",
        "open('f', 'w')\n",
        "open('f', 'wb')\n",
        "open('f', mode='a')\n",
        "open('f', 'r+')\n",
        "open('f', 'x')\n",
        "open('f', m)\n",
        "import io\nio.open('f', 'w')\n",
        "from pathlib import Path\nPath('f').open('w')\n",
        "from pathlib import Path\nPath('f').open(mode='ab')\n",
        "from pathlib import Path\nPath('f').write_text('x')\n",
        "from pathlib import Path\nPath('f').write_bytes(b'x')\n",
        "import os\nos.open('f', os.O_WRONLY)\n",
        "import os\nos.open('f', os.O_RDONLY | os.O_CREAT)\n",
        "import os\nos.open('f', os.O_RDWR | os.O_TRUNC)\n",
        "import os\nflags = getattr(os, 'O_APPEND', 0)\n",
    ],
)
def test_stdlib_ban_census_finds_a_planted_violation(planted):
    assert len(stdlib_ban_violations(planted)) >= 1


@pytest.mark.parametrize(
    "legit",
    [
        "import os\nfd = os.open('f', os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0))\n",
        "open('f')\n",
        "open('f', 'r')\n",
        "open('f', 'rb')\n",
        "from pathlib import Path\nPath('f').open('rb')\nPath('f').read_text()\n",
        "import os, stat\nos.lstat('f')\nos.listdir('.')\n",
        "from dataclasses import dataclass\nimport yaml\n",
    ],
)
def test_stdlib_ban_census_does_not_flag_a_read(legit):
    assert stdlib_ban_violations(legit) == []
