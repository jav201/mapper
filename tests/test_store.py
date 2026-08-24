"""Unit tests for mapper.store."""
import shutil

import pytest

from mapper.model import Edge, Ficha, Graph, Node, SchemaField
from mapper.store import MapStore, MapStoreError


def test_store_save_load_roundtrip(tmp_store):
    g = Graph(schema=[SchemaField(key="D", label="documento", required=True)])
    g.add_node(Node(id="root", ficha=Ficha(title="Root", fields={"D": "ACTA-1"})))
    g.add_node(Node(id="child", ficha=Ficha(title="Child", fields={})))
    g.add_edge(Edge("root", "child"))

    tmp_store.save("demo", g)
    loaded = tmp_store.load("demo")

    assert loaded.root_id == "root"
    assert set(loaded.nodes) == {"root", "child"}
    assert loaded.nodes["root"].ficha.title == "Root"
    assert loaded.schema[0].key == "D"


def test_store_rebuilds_index_when_deleted(tmp_store):
    g = Graph()
    g.add_node(Node(id="a", ficha=Ficha(title="A")))
    tmp_store.save("demo", g)

    # delete derived db
    tmp_store.db_path.unlink(missing_ok=True)
    assert not tmp_store.db_path.exists()

    loaded = tmp_store.load("demo")
    assert "a" in loaded.nodes


def test_store_missing_map_raises(tmp_store):
    with pytest.raises(MapStoreError):
        tmp_store.load("missing")


def test_store_create_from_template(tmp_store):
    graph = tmp_store.create_from_template("legacy", "legacy-audit")
    assert graph.root_id == "root"
    assert graph.nodes["root"].ficha.title == "auditoría legacy"
    keys = {f.key for f in graph.schema}
    assert {"D", "O", "E"} <= keys
    assert "C" in keys


def test_store_create_from_template_unknown(tmp_store):
    with pytest.raises(MapStoreError):
        tmp_store.create_from_template("x", "no-such-template")


def test_store_isolates_maps_with_same_node_ids(tmp_store):
    """Two maps with the same node id must not collide in the index."""
    g1 = Graph()
    g1.add_node(Node(id="root", ficha=Ficha(title="Mapa Uno")))
    g2 = Graph()
    g2.add_node(Node(id="root", ficha=Ficha(title="Mapa Dos")))

    tmp_store.save("m1", g1)
    tmp_store.save("m2", g2)

    assert tmp_store.load("m1").nodes["root"].ficha.title == "Mapa Uno"
    assert tmp_store.load("m2").nodes["root"].ficha.title == "Mapa Dos"


def test_store_atomic_save(tmp_store):
    """Save should leave valid files even if interrupted (atomic via temp+rename)."""
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="Atomico")))
    tmp_store.save("atomic", g)

    mmd = tmp_store.workspace / "atomic.mmd"
    yml = tmp_store.workspace / "atomic_nodos.yml"
    assert mmd.exists()
    assert yml.exists()
    # No stray temp files should remain.
    assert not list(tmp_store.workspace.glob("atomic*.tmp"))
