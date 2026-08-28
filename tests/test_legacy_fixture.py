"""Tests for the legacy fixture and schema coverage rendering."""
from pathlib import Path

from mapper.model import SchemaField
from mapper.views.state import ViewState
from mapper.store import MapStore
from mapper.views.layered import LayeredRenderer


def test_legacy_fixture_loads(tmp_path):
    store = MapStore(tmp_path)
    fixture_mmd = Path(__file__).parent.parent / "fixtures" / "legacy.mmd"
    fixture_yml = Path(__file__).parent.parent / "fixtures" / "legacy_nodos.yml"
    (tmp_path / "legacy.mmd").write_text(fixture_mmd.read_text(encoding="utf-8"))
    (tmp_path / "legacy_nodos.yml").write_text(fixture_yml.read_text(encoding="utf-8"))

    graph = store.load("legacy")
    assert graph.root_id == "erp"
    assert len(graph.nodes) == 8
    assert any(f.key == "D" and f.required for f in graph.schema)


def test_legacy_renderer_shows_per_card_coverage():
    """The canvas still shows coverage per card, as letters on each node.

    The word "cobertura" used to appear here too, from the renderer's own ficha
    strip.  That strip was removed in batch `ui_next-01` because the inspector
    panel renders the same card — the map was drawing it twice.  The assertion
    was not dropped: it moved to `test_inspector.py`, which observes coverage on
    the surface that now owns it.  What stays here is the per-card evidence, which
    the canvas is still responsible for.
    """
    store = MapStore(Path(__file__).parent.parent / "fixtures")
    graph = store.load("legacy")
    renderer = LayeredRenderer()
    text = renderer.render(graph, ViewState(selected_id="erp", w=120, h=40))
    assert "SIN ACTA" not in text.plain or "ACTA-2011-034" in text.plain
    assert "D✓" in text.plain or "D░" in text.plain
    # The strip is gone: its two distinctive strings must not come back here.
    assert "selecciona un nodo" not in text.plain
    assert "cobertura" not in text.plain
