"""Fixes batch increment 002 (B-117): a forest map keeps its declared root
across save + reload, and `dump` stays byte-identical wherever text order
already elects that root.

LLR-FX.3.1 (the hoist), LLR-FX.3.2 (the moved pins live in their own files),
AT-086, TC-FX-3.1, TC-FX-3.3.
"""
import json

import pytest
import yaml

from mapper.mermaid import dump, parse
from mapper.model import Edge, Ficha, Graph, Node
from mapper.store import MapStore

# The three forest shapes of requirements premise 3: 2 + 2 + 4 = 8 parentless
# nodes. Each is (text, parentless ids).
_SHAPES = [
    ("graph TD\n    a\n    b --> c\n", ["a", "b"]),
    ("graph TD\n    b --> c\n    a --> d\n", ["b", "a"]),
    ("graph TD\n    x\n    b --> c\n    a[Alpha] --> d\n    z\n", ["x", "b", "a", "z"]),
]
_CASES = [(text, rid) for text, ids in _SHAPES for rid in ids]


def _node(nid: str, title: str = "") -> Node:
    return Node(id=nid, ficha=Ficha(title=title))


def _forest_with_root(text: str, root: str) -> Graph:
    graph = parse(text)
    graph.root_id = root
    return graph


@pytest.fixture
def store(tmp_path) -> MapStore:
    return MapStore(tmp_path)


def test_at_086_forest_root_survives_save_and_reload(store):
    g = Graph()
    g.add_node(_node("a", "Alpha"))
    g.add_node(_node("b", "Bravo"))
    g.add_node(_node("c", "Charlie"))
    g.add_edge(Edge("b", "c"))
    assert g.root_id == "a"

    store.save("forest", g)

    saved = (store.workspace / "forest.mmd").read_text(encoding="utf-8")
    assert saved.splitlines()[1] == "    a[Alpha]"
    assert saved.count("a[Alpha]") == 1
    assert store.load("forest").root_id == "a"


@pytest.mark.parametrize("text, root", _CASES)
def test_every_parentless_node_set_as_root_reparses_to_itself(text, root):
    graph = _forest_with_root(text, root)
    assert parse(dump(graph)).root_id == root


def test_b117_reproduction_bytes():
    graph = _forest_with_root("graph TD\n    b --> c\n    a\n", "a")
    assert dump(graph) == "graph TD\n    a\n    b --> c\n"


def test_orphan_root_is_not_declared_twice():
    graph = _forest_with_root("graph TD\n    b --> c\n    a[Alpha]\n", "a")
    out = dump(graph)
    assert out == "graph TD\n    a[Alpha]\n    b --> c\n"
    assert out.count("a[Alpha]") == 1


def test_edge_parent_root_gets_a_standalone_line_first():
    graph = _forest_with_root("graph TD\n    b --> c\n    a --> d\n", "a")
    assert dump(graph) == "graph TD\n    a\n    b --> c\n    a --> d\n"


@pytest.mark.parametrize(
    "text, root",
    [
        ("graph TD\n    a\n    b --> c\n", "a"),
        ("graph TD\n    b --> c\n    a\n", "b"),
        ("graph TD\n    a --> b\n    b --> c\n", "a"),
    ],
)
def test_root_already_elected_by_text_order_changes_nothing(text, root):
    graph = _forest_with_root(text, root)
    assert dump(graph) == text


def test_empty_and_single_node_graphs_are_unchanged():
    assert dump(Graph()) == "graph TD\n"
    single = Graph()
    single.add_node(_node("only", "Only"))
    assert dump(single) == "graph TD\n    only[Only]\n"


def test_root_that_is_a_written_child_is_not_hoisted():
    graph = parse("graph TD\n    a --> b\n    x\n")
    graph.root_id = "b"
    assert dump(graph) == "graph TD\n    a --> b\n    x\n"


def test_root_whose_only_edge_dangles_stays_unwritten():
    g = Graph()
    g.add_node(_node("first"))
    g.add_node(_node("solo"))
    g.add_edge(Edge("solo", "ghost"))
    g.root_id = "solo"
    assert dump(g) == "graph TD\n    first\n"


def test_root_id_absent_from_nodes_leaves_the_text_unchanged():
    graph = parse("graph TD\n    b --> c\n    a\n")
    graph.root_id = "nope"
    assert dump(graph) == "graph TD\n    b --> c\n    a\n"


def test_undo_snapshot_of_a_forest_restores_the_declared_root(store):
    # TC-FX-3.3: the undo path (`undo.py` _push_snapshot / _pop_snapshot) is
    # dump + sidecar -> `_graph_from_sidecar`; no AT reaches it.
    graph = _forest_with_root("graph TD\n    a\n    b --> c\n", "a")
    blob = json.dumps(
        {
            "mmd": dump(graph),
            "yml": yaml.safe_dump(store._build_sidecar(graph), sort_keys=False, allow_unicode=True),
        }
    ).encode()
    data = json.loads(blob.decode())
    restored = store._graph_from_sidecar(data["mmd"], yaml.safe_load(data["yml"]) or {})
    assert restored.root_id == "a"
