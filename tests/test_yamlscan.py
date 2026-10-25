"""LLR-RML.1.4 -- the leaf prescan: `mapper/yamlscan.py`.

The byte limb of the move is `tests/test_prescan_refusal_goldens.py`; this file pins the leaf's
own contract (the typed error, the 40-character display cut, the iterative scan) and, by AST,
that `store.py` no longer defines the logic and `yamlscan.py` stays a leaf that reads no file.
"""
from __future__ import annotations

import ast
import time
from pathlib import Path

import pytest
import yaml

import mapper
from mapper import yamlscan
from mapper.osopen import MAX_DEPTH
from mapper.yamlscan import ANCHOR_NAME_DISPLAY, YamlLimitError, prescan

PKG = Path(mapper.__file__).resolve().parent


def _nested_flow(n: int) -> str:
    text = "0"
    for _ in range(n):
        text = "{k: " + text + "}"
    return text


def test_constants():
    assert ANCHOR_NAME_DISPLAY == 40
    assert MAX_DEPTH == 64


def test_clean_documents_pass():
    for text in ("", "a: 1\n", "a: [1, 2, {b: 3}]\n", "# only a comment\n", "a: 1\n---\nb: 2\n"):
        assert prescan(text) is None


def test_anchor_is_refused_with_its_name():
    with pytest.raises(YamlLimitError) as err:
        prescan("a: &x 1\n")
    assert (err.value.kind, err.value.shown, err.value.limit) == ("anchor", "x", MAX_DEPTH)


def test_alias_is_refused_with_its_name():
    # an alias event alone (the anchor it points at need not exist for the event scan)
    with pytest.raises(YamlLimitError) as err:
        prescan("b: *zz\n")
    assert (err.value.kind, err.value.shown) == ("anchor", "zz")


def test_the_alias_check_is_independent_of_the_anchor_check():
    """M-RML-5: a leaf that only looks at anchor definitions would pass this document."""
    with pytest.raises(YamlLimitError) as err:
        prescan("- *only_an_alias\n")
    assert err.value.shown == "only_an_alias"


@pytest.mark.parametrize("length,shown", [(40, "g" * 40), (41, "g" * 40 + "…"), (5000, "g" * 40 + "…")])
def test_anchor_name_is_cut_at_forty_characters(length, shown):
    with pytest.raises(YamlLimitError) as err:
        prescan("a: &" + "g" * length + " 1\n")
    assert err.value.shown == shown


def test_depth_64_passes_and_65_is_refused():
    assert prescan(_nested_flow(MAX_DEPTH)) is None
    with pytest.raises(YamlLimitError) as err:
        prescan(_nested_flow(MAX_DEPTH + 1))
    assert (err.value.kind, err.value.shown, err.value.limit) == ("depth", "", MAX_DEPTH)


def test_depth_counts_block_collections_too():
    text = "".join("  " * i + "- \n" for i in range(MAX_DEPTH + 1)) + "  " * (MAX_DEPTH + 1) + "- x\n"
    with pytest.raises(YamlLimitError) as err:
        prescan(text)
    assert err.value.kind == "depth"


def test_ten_thousand_deep_is_refused_fast_without_recursion_error():
    started = time.perf_counter()
    with pytest.raises(YamlLimitError):
        prescan(_nested_flow(10_000))
    assert time.perf_counter() - started < 5.0


def test_a_yaml_error_propagates_untouched():
    with pytest.raises(yaml.YAMLError):
        prescan("a: [\n")


def test_limit_error_is_not_valueerror():
    """The callers' nets catch `ValueError` and `yaml.YAMLError`: a typed refusal must not be one (M-RML-12)."""
    assert issubclass(YamlLimitError, Exception)
    assert not issubclass(YamlLimitError, (ValueError, yaml.YAMLError, OSError))


def _tree(name: str) -> ast.Module:
    return ast.parse((PKG / name).read_text(encoding="utf-8"))


def test_store_no_longer_defines_the_prescan_logic():
    """The rule lives in one place: `store.py` delegates, holds no event loop, no limit constant."""
    source = (PKG / "store.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {
        n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    yaml_parse = [n for n in ast.walk(tree) if isinstance(n, ast.Attribute) and n.attr == "parse"
                  and isinstance(n.value, ast.Name) and n.value.id == "yaml"]
    assert not yaml_parse, "store.py must not run the event scan itself"
    assert not names & {"SequenceStartEvent", "MappingStartEvent", "ANCHOR_NAME_DISPLAY", "MAX_DEPTH"}, names
    assert "prescan" in names and "YamlLimitError" in names


def test_store_does_not_define_the_display_constant():
    from mapper import store
    assert not hasattr(store, "ANCHOR_NAME_DISPLAY")
    assert not hasattr(store, "MAX_DEPTH")


def test_the_leaf_reads_no_file_and_imports_only_osopen_max_depth():
    tree = _tree("yamlscan.py")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            callee = node.func
            name = callee.id if isinstance(callee, ast.Name) else getattr(callee, "attr", "")
            assert name not in {"open", "read_text", "read_bytes", "read_capped"}, name
    froms = [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.level]
    assert [(n.module, [a.name for a in n.names]) for n in froms] == [("osopen", ["MAX_DEPTH"])]
    assert yamlscan.ANCHOR_NAME_DISPLAY == 40
