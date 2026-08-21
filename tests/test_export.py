"""Tests for SVG export."""
from pathlib import Path

from mapper.export import save_svg
from mapper.model import Ficha, Graph, Node
from mapper.views.layered import LayeredRenderer


def test_save_svg(tmp_path):
    g = Graph()
    g.add_node(Node(id="a", ficha=Ficha(title="A")))
    text = LayeredRenderer().render(g, selected_id="a", w=40, h=12)
    out = tmp_path / "out.svg"
    save_svg(text, out)
    assert out.exists()
    assert "<svg" in out.read_text(encoding="utf-8")
