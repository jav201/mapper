"""Unit tests for mapper.screens.coverage."""
from mapper.model import Edge, Ficha, Graph, Node, SchemaField
from mapper.screens.coverage import CoverageScreen


def test_coverage_report_names_the_missing_field_in_words():
    """The report shows `SchemaField.label`, never the raw key letter.

    It used to return `["O"]`.  A coverage report whose "missing" column reads
    `D,O` tells the operator nothing about what to go and fill in — which is the
    complaint US-N01 was raised on, and it applies to this surface too.
    """
    schema = [
        SchemaField(key="D", label="documento", required=True),
        SchemaField(key="O", label="dueño", required=True),
        SchemaField(key="C", label="criticidad", required=False),
    ]
    ficha = Ficha(title="x", fields={"D": "acta"})
    assert CoverageScreen._missing_keys(ficha, schema) == ["dueño"]
    # An optional field is never reported as missing, however empty.
    assert "criticidad" not in CoverageScreen._missing_keys(ficha, schema)


def test_coverage_incomplete_nodes_ordered_by_subtree():
    schema = [SchemaField(key="D", label="documento", required=True)]
    g = Graph(schema=schema)
    g.add_node(Node(id="root", ficha=Ficha(title="Root", fields={"D": "r"})))
    g.add_node(Node(id="a", ficha=Ficha(title="A")))  # incomplete
    g.add_node(Node(id="b", ficha=Ficha(title="B", fields={"D": "b"})))
    g.add_node(Node(id="c", ficha=Ficha(title="C")))  # incomplete
    g.add_edge(Edge("root", "a"))
    g.add_edge(Edge("root", "b"))
    g.add_edge(Edge("b", "c"))

    screen = CoverageScreen(g, "demo")
    nodes = screen._incomplete_nodes()
    assert [n.id for n in nodes] == ["a", "c"]
