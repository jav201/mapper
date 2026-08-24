"""Tests for document factory model and resolution."""
from mapper.model import Document, Edge, Ficha, Graph, Node


def test_resolve_document_inherits_from_parent():
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="root")))
    g.add_node(Node(id="child", ficha=Ficha(title="child")))
    g.add_edge(Edge("root", "child"))
    g.documents["oferta"] = Document(
        name="oferta",
        source="puesto: {{puesto}}",
        tags={"puesto": "ingeniero"},
    )
    resolved = g.resolve_document("oferta", g.nodes["child"])
    assert resolved.tags["puesto"] == "ingeniero"


def test_local_tag_overrides_inherited():
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="root")))
    g.add_node(Node(id="child", ficha=Ficha(title="child")))
    g.add_edge(Edge("root", "child"))
    g.documents["oferta"] = Document(
        name="oferta",
        source="{{puesto}}",
        tags={"puesto": "senior"},
    )
    g.nodes["child"].ficha.fields["doc_oferta_puesto"] = "junior"
    resolved = g.resolve_document("oferta", g.nodes["child"])
    assert resolved.tags["puesto"] == "senior"


def test_missing_document_returns_empty():
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="root")))
    resolved = g.resolve_document("missing", g.nodes["root"])
    assert resolved.source == ""
