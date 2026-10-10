"""CSV-safety increment 1: `MapStore.save` refuses what its loader refuses.

LLR-CSV.1.1 (round-trip refusal), LLR-CSV.1.2 (no-write oracle), LLR-CSV.1.3
(legacy forest regression) and the unit round-trip nodes of LLR-CSV.3.1.
"""
import hashlib

import pytest
import yaml

from mapper.model import Edge, Ficha, Graph, Node
from mapper.store import MapStore, MapStoreError


def _digests(workspace) -> dict[str, str]:
    """sha256 of EVERY file under the workspace, walked recursively."""
    return {
        str(p.relative_to(workspace)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(workspace.rglob("*"))
        if p.is_file()
    }


def _node(nid: str, title: str = "") -> Node:
    return Node(id=nid, ficha=Ficha(title=title))


def _multi_parent_graphs() -> list[tuple[str, Graph]]:
    """The slug-collision shapes of the LLR-CSV.1.1 boundary catalog."""
    graphs: list[tuple[str, Graph]] = []
    # two-row collision: ids `a-b` and `A B` slugify to the same node `a-b`
    g = Graph()
    g.add_node(_node("a-b"))
    g.add_node(_node("x"))
    g.add_node(_node("y"))
    g.add_edge(Edge("x", "a-b"))
    g.add_edge(Edge("y", "a-b"))
    graphs.append(("two rows", g))
    # three-way collision
    g = Graph()
    g.add_node(_node("dup"))
    for parent in ("p1", "p2", "p3"):
        g.add_node(_node(parent))
        g.add_edge(Edge(parent, "dup"))
    graphs.append(("three rows", g))
    # auto-id collision: two empty-id rows share the title slug `row-1`, and
    # each row carries its own parent reference -> `row-1` gets two parents
    g = Graph()
    g.add_node(_node("row-1"))
    g.add_node(_node("p1"))
    g.add_node(_node("p2"))
    g.add_edge(Edge("p1", "row-1"))
    g.add_edge(Edge("p2", "row-1"))
    graphs.append(("auto ids", g))
    return graphs


def test_save_refuses_multi_parent_graph(tmp_store):
    for name, graph in _multi_parent_graphs():
        before = _digests(tmp_store.workspace)
        with pytest.raises(MapStoreError, match="more than one parent"):
            tmp_store.save(name.replace(" ", "-"), graph)
        after = _digests(tmp_store.workspace)
        assert after == before, f"{name}: a refused save changed the workspace"
        assert not list(tmp_store.workspace.rglob("*.mmd"))


def test_save_refuses_cycle_still(tmp_store):
    # LLR-R01.5 guard kept verbatim: cyclic and self-parent graphs refuse.
    cycle = Graph()
    for nid in ("a", "b"):
        cycle.add_node(_node(nid))
    cycle.add_edge(Edge("a", "b"))
    cycle.add_edge(Edge("b", "a"))
    with pytest.raises(MapStoreError, match="cycle"):
        tmp_store.save("cyc", cycle)

    self_parent = Graph()
    self_parent.add_node(_node("solo"))
    self_parent.add_edge(Edge("solo", "solo"))
    with pytest.raises(MapStoreError, match="cycle"):
        tmp_store.save("self", self_parent)
    assert not list(tmp_store.workspace.rglob("*.mmd"))


def test_save_refuses_unparsable_dump(tmp_store):
    # A node title containing a newline dumps to text the loader refuses.
    graph = Graph()
    graph.add_node(_node("root"))
    graph.add_node(_node("bad", title="first line\nsecond line"))
    graph.add_edge(Edge("root", "bad"))
    before = _digests(tmp_store.workspace)
    with pytest.raises(MapStoreError, match="would not re-open"):
        tmp_store.save("nl", graph)
    assert _digests(tmp_store.workspace) == before


def test_save_refuses_reparse_structure_mismatch(tmp_store):
    # An orphan node titled `a --> b` re-parses as a spurious edge (the node-id
    # set changes); exact duplicate edges are dropped by `dump` (the edge
    # multiset changes).  Both are silent corruption the store now refuses.
    arrow = Graph()
    arrow.add_node(_node("x", title="a --> b"))
    before = _digests(tmp_store.workspace)
    with pytest.raises(MapStoreError, match="change the nodes"):
        tmp_store.save("arrow", arrow)
    assert _digests(tmp_store.workspace) == before

    dup = Graph()
    dup.add_node(_node("a"))
    dup.add_node(_node("b"))
    dup.add_edge(Edge("a", "b"))
    dup.add_edge(Edge("a", "b"))
    before = _digests(tmp_store.workspace)
    with pytest.raises(MapStoreError, match="change the connections"):
        tmp_store.save("dupes", dup)
    assert _digests(tmp_store.workspace) == before


def test_refused_save_changes_no_workspace_byte(tmp_store):
    # The fixture OVERWRITES an existing map id with prior content: a check
    # moved after any write turns RED because the target .mmd digest changes.
    keep = Graph()
    keep.add_node(_node("root", title="keep me"))
    keep.add_node(_node("kid", title="child"))
    keep.add_edge(Edge("root", "kid"))
    tmp_store.save("keep", keep)
    mmd_before = (tmp_store.workspace / "keep.mmd").read_bytes()

    bad = Graph()
    bad.add_node(_node("dup"))
    bad.add_node(_node("p1"))
    bad.add_node(_node("p2"))
    bad.add_edge(Edge("p1", "dup"))
    bad.add_edge(Edge("p2", "dup"))
    before = _digests(tmp_store.workspace)
    with pytest.raises(MapStoreError):
        tmp_store.save("keep", bad)
    after = _digests(tmp_store.workspace)
    assert after == before
    assert set(after) == set(before)
    assert (tmp_store.workspace / "keep.mmd").read_bytes() == mmd_before
    assert not list(tmp_store.workspace.glob("*.tmp"))


def _write_legacy_pair(store: MapStore, map_id: str, mmd_text: str, graph: Graph) -> None:
    """Write the `.mmd` + sidecar pair exactly as the old app would."""
    sidecar = store._build_sidecar(graph)
    sidecar["_mmd_hash"] = store._text_hash(mmd_text, "")
    yml_text = yaml.safe_dump(sidecar, sort_keys=False, allow_unicode=True)
    (store.workspace / f"{map_id}.mmd").write_text(mmd_text, encoding="utf-8")
    (store.workspace / f"{map_id}_nodos.yml").write_text(yml_text, encoding="utf-8")


def test_save_accepts_legacy_forest_after_edit(tmp_store):
    # LLR-CSV.1.3: a legacy forest (`a` / `b --> c`, two parentless nodes)
    # loads, accepts an edit, and saves — the round-trip check compares the
    # node-id set and edge set only, NOT the root (ruling R11 / B-117).
    legacy = Graph()
    legacy.add_node(_node("a", title="A"))
    legacy.add_node(_node("b", title="B"))
    legacy.add_node(_node("c", title="C"))
    legacy.add_edge(Edge("b", "c"))
    _write_legacy_pair(tmp_store, "forest", "graph TD\n    a\n    b --> c\n", legacy)

    loaded = tmp_store.load("forest")
    assert loaded.root_id == "a"
    assert set(loaded.nodes) == {"a", "b", "c"}

    loaded.add_node(_node("d", title="D"))
    loaded.add_edge(Edge("a", "d"))
    tmp_store.save("forest", loaded)

    reloaded = tmp_store.load("forest")
    assert set(reloaded.nodes) == set(loaded.nodes)
    assert {(e.parent_id, e.child_id) for e in reloaded.edges} == {
        (e.parent_id, e.child_id) for e in loaded.edges
    }
    assert reloaded.nodes["d"].ficha.title == "D"


def test_save_load_roundtrip_valid_trees(tmp_store):
    # LLR-CSV.3.1 unit round trip: a valid tree saves and re-opens identical
    # (node ids, edges, root, titles).
    tree = Graph()
    tree.add_node(_node("root", title="Root"))
    tree.add_node(_node("mid", title="Middle"))
    tree.add_node(_node("leaf", title="Leaf"))
    tree.add_edge(Edge("root", "mid"))
    tree.add_edge(Edge("mid", "leaf", label="goes to"))
    tmp_store.save("tree", tree)
    loaded = tmp_store.load("tree")
    assert set(loaded.nodes) == {"root", "mid", "leaf"}
    assert {(e.parent_id, e.child_id) for e in loaded.edges} == {
        ("root", "mid"),
        ("mid", "leaf"),
    }
    assert loaded.root_id == "root"
    assert loaded.nodes["leaf"].ficha.title == "Leaf"

    # child-first declared: the child node is added to the Graph before its
    # parent; the saved map still re-opens with identical nodes and edges.
    child_first = Graph()
    child_first.add_node(_node("kid", title="Kid"))
    child_first.add_node(_node("top", title="Top"))
    child_first.add_edge(Edge("top", "kid"))
    child_first.root_id = "top"  # `add_node` keeps the first node as root;
    # set the real root so the in-memory graph is the tree the text declares.
    tmp_store.save("childfirst", child_first)
    reloaded = tmp_store.load("childfirst")
    assert set(reloaded.nodes) == {"kid", "top"}
    assert {(e.parent_id, e.child_id) for e in reloaded.edges} == {("top", "kid")}


def test_save_load_roundtrip_empty_and_single_node(tmp_store):
    empty = Graph()
    tmp_store.save("empty", empty)
    assert tmp_store.load("empty").nodes == {}

    single = Graph()
    single.add_node(_node("solo", title="Only"))
    tmp_store.save("single", single)
    loaded = tmp_store.load("single")
    assert set(loaded.nodes) == {"solo"}
    assert loaded.root_id == "solo"
