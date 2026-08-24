"""Unit tests for mapper.import_csv."""
from pathlib import Path

from mapper.import_csv import preview_csv
from mapper.model import Edge


def test_preview_csv_parent_column(tmp_path):
    path = tmp_path / "nodes.csv"
    path.write_text("id,title,parent\nroot,sistema,\na,auth,root\nb,db,root\n", encoding="utf-8")
    graph = preview_csv(path)
    assert graph.root_id == "root"
    assert set(graph.nodes) == {"root", "a", "b"}
    assert graph.parent_of("a") == "root"
    assert graph.parent_of("b") == "root"


def test_preview_csv_depth_column(tmp_path):
    path = tmp_path / "nodes.tsv"
    path.write_text("id\ttitle\tdepth\nroot\tsistema\t0\na\tauth\t1\nb\tdb\t1\n", encoding="utf-8")
    graph = preview_csv(path)
    assert graph.root_id == "root"
    assert graph.parent_of("a") == "root"
    assert graph.parent_of("b") == "root"


def test_preview_csv_parks_orphans_with_marker(tmp_path):
    path = tmp_path / "nodes.csv"
    path.write_text("id,title,parent\nroot,sistema,\na,auth,unknown\n", encoding="utf-8")
    graph = preview_csv(path)
    assert graph.parent_of("a") == "root"
    assert graph.nodes["a"].ficha.title == "? auth"


def test_preview_csv_extra_fields(tmp_path):
    path = tmp_path / "nodes.csv"
    path.write_text("id,title,parent,D,O\nroot,sistema,,,\na,auth,root,ACTA-1,Juan\n", encoding="utf-8")
    graph = preview_csv(path)
    assert graph.nodes["a"].ficha.fields == {"D": "ACTA-1", "O": "Juan"}


def test_preview_csv_empty_file(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    graph = preview_csv(path)
    assert graph.nodes == {}


def test_preview_csv_generates_ids_for_empty_id_column(tmp_path):
    path = tmp_path / "nodes.csv"
    path.write_text(
        "id,title,parent\nroot,raíz,\n,sin id,root\n,otro,root\n", encoding="utf-8"
    )
    graph = preview_csv(path)
    assert graph.parent_of("sin-id") == "root"
    assert graph.parent_of("otro") == "root"
    assert len(graph.nodes) == 3
