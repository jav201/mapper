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
