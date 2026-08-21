"""Unit tests for mapper.model."""
import pytest

from mapper.model import Attachment, Edge, Ficha, Graph, Node, SchemaField


def test_node_required_coverage():
    schema = [
        SchemaField(key="D", label="documento", required=True),
        SchemaField(key="O", label="dueño", required=True),
        SchemaField(key="N", label="notas", required=False),
    ]
    ficha = Ficha(fields={"D": "ACTA-1", "N": "nota"})
    assert ficha.required_coverage(schema) == (1, 2)


def test_graph_focus():
    g = Graph()
    for nid in "abc":
        g.add_node(Node(id=nid))
    g.add_edge(Edge("a", "b"))
    g.add_edge(Edge("b", "c"))
    focused = g.focus("b")
    assert focused.root_id == "b"
    assert set(focused.nodes) == {"b", "c"}


def test_graph_search_hits():
    g = Graph()
    n = Node(id="x", ficha=Ficha(title="Factura", notes="acta de prueba"))
    g.add_node(n)
    assert g.search_hits("acta") == ["x"]


def test_graph_coverage():
    schema = [SchemaField(key="D", label="documento", required=True)]
    g = Graph(schema=schema)
    g.add_node(Node(id="a", ficha=Ficha(fields={"D": "x"})))
    g.add_node(Node(id="b", ficha=Ficha(fields={})))
    assert g.coverage() == (1, 2)
