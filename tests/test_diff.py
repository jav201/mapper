"""Unit tests for mapper.diff."""
import subprocess

import pytest

from mapper.diff import DiffResult, _compare_graphs, git_diff
from mapper.model import Edge, Ficha, Graph, Node, SchemaField
from mapper.store import MapStore


def test_compare_graphs_detects_added_removed_changed():
    schema = [
        SchemaField(key="D", label="documento", required=True),
        SchemaField(key="O", label="dueño", required=True),
    ]
    old = Graph(schema=schema)
    old.add_node(Node(id="root", ficha=Ficha(title="Root", fields={"D": "r", "O": "o"})))
    old.add_node(Node(id="gone", ficha=Ficha(title="Gone")))
    old.add_edge(Edge("root", "gone"))

    cur = Graph(schema=schema)
    cur.add_node(Node(id="root", ficha=Ficha(title="Root", fields={"D": "r", "O": "o"})))
    cur.add_node(Node(id="new", ficha=Ficha(title="New")))
    cur.add_edge(Edge("root", "new"))
    # changed title + field
    cur.nodes["root"].ficha.title = "Root Renamed"
    cur.nodes["root"].ficha.fields["O"] = "other"

    result = _compare_graphs(old, cur)
    assert result.added == {"new"}
    assert result.removed == {"gone"}
    assert "title" in result.changed["root"]
    assert "O" in result.changed["root"]
    assert "D" not in result.changed["root"]
    assert result.removed_titles == {"gone": "Gone"}


def test_git_diff_returns_none_outside_repo(tmp_store):
    assert git_diff("demo", tmp_store) is None


def test_git_diff_returns_none_when_not_committed(tmp_store, tmp_path):
    ws = tmp_store.workspace
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="Root")))
    tmp_store.save("demo", g)

    subprocess.run(["git", "init", "-q"], cwd=ws, check=True)
    assert git_diff("demo", tmp_store) is None


def test_git_diff_with_committed_map(tmp_store, tmp_path):
    ws = tmp_store.workspace
    schema = [SchemaField(key="D", label="documento", required=True)]
    g = Graph(schema=schema)
    g.add_node(Node(id="root", ficha=Ficha(title="Root", fields={"D": "ACTA-1"})))
    g.add_node(Node(id="child", ficha=Ficha(title="Child", fields={"D": "ACTA-2"})))
    g.add_edge(Edge("root", "child"))
    tmp_store.save("demo", g)

    subprocess.run(["git", "init", "-q"], cwd=ws, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=ws, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=ws, check=True)
    subprocess.run(["git", "add", "."], cwd=ws, check=True)
    subprocess.run(["git", "commit", "-m", "initial", "-q"], cwd=ws, check=True)

    # current graph differs: remove child, change title, add new
    cur = tmp_store.load("demo")
    cur.nodes["root"].ficha.title = "Root v2"
    del cur.nodes["child"]
    cur.edges = [e for e in cur.edges if e.child_id != "child"]
    cur.add_node(Node(id="new", ficha=Ficha(title="New", fields={"D": "ACTA-3"})))
    cur.add_edge(Edge("root", "new"))
    tmp_store.save("demo", cur)

    result = git_diff("demo", tmp_store)
    assert isinstance(result, DiffResult)
    assert result.added == {"new"}
    assert result.removed == {"child"}
    assert "title" in result.changed["root"]
    assert result.removed_titles == {"child": "Child"}
