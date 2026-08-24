"""Tests for mapper.mermaid round-trip."""
from __future__ import annotations

from mapper.mermaid import dump, parse, slugify
from mapper.model import Edge, Ficha, Graph, Node
from mapper.store import MapStore


def test_slugify_allows_hyphens():
    assert slugify("Mi Hijo Nuevo") == "mi-hijo-nuevo"
    assert slugify("a_b") == "a_b"
    assert slugify("---") == "n"


def test_parse_hyphenated_ids():
    src = "graph TD\n    root --> mi-hijo\n"
    graph = parse(src)
    assert "mi-hijo" in graph.nodes
    assert graph.parent_of("mi-hijo") == "root"


def test_dump_and_parse_roundtrip_with_hyphens(tmp_path):
    store = MapStore(tmp_path)
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="Root")))
    g.add_node(Node(id="mi-hijo", ficha=Ficha(title="Mi Hijo")))
    g.add_node(Node(id="otro-nieto", ficha=Ficha(title="Otro Nieto")))
    g.add_edge(Edge("root", "mi-hijo"))
    g.add_edge(Edge("mi-hijo", "otro-nieto"))

    store.save("hyphens", g)
    loaded = store.load("hyphens")

    assert set(loaded.nodes) == {"root", "mi-hijo", "otro-nieto"}
    assert loaded.parent_of("mi-hijo") == "root"
    assert loaded.parent_of("otro-nieto") == "mi-hijo"



