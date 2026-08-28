"""Tests for radial renderer."""
import mapper.views.radial as radial_mod
from mapper.canvas import Canvas
from mapper.model import Edge, Ficha, Graph, Node
from mapper.views.radial import RadialRenderer

BRAILLE = range(0x2800, 0x2900)

# The pre-change painted set for M1_TITLES at 80x24, captured at 5d8ee0d before
# Canvas composed the layers.  This is a regression PIN, not the gate: its
# subject is the renderer's pre-existing output, which is exactly what must not
# change.  The gate is the derived containment arm below.
PRE_CHANGE_PAINTED = set("acefilmnoprstvz·◆●")

M1_TITLES = ("finanzas", "inventarios", "nomina", "compras", "reportes")


def _m1_graph() -> Graph:
    """Root plus five children -- the M-1 shape, six nodes and five edges."""
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="mapa")))
    for i, title in enumerate(M1_TITLES):
        g.add_node(Node(id=f"n{i}", ficha=Ficha(title=title)))
        g.add_edge(Edge("root", f"n{i}"))
    return g


def _braille_count(text) -> int:
    return sum(1 for c in text.plain if ord(c) in BRAILLE)


def _render_capturing_canvas(monkeypatch, graph, **kw):
    """Render, and keep the Canvas the renderer built.

    The containment arm needs the glyphs the renderer explicitly PUT, derived
    from the same run rather than hand-listed.
    """
    built = []
    real = radial_mod.Canvas

    def spy(*args, **kwargs):
        cv = real(*args, **kwargs)
        built.append(cv)
        return cv

    monkeypatch.setattr(radial_mod, "Canvas", spy)
    text = RadialRenderer().render(graph, **kw)
    return text, built[-1]


def test_at_007b_braille_edges_reach_the_painted_output(monkeypatch):
    """PIN (radial). The threshold is a COUNT; the pre-state is exactly 0.

    An adjective ("braille appears") has no measured pre-state and no mutation
    that can move it.  Executed at 5d8ee0d, this graph through this renderer at
    this geometry painted 0 characters in U+2800..U+28FF while the renderer was
    writing 184 dots that `Canvas.rows()` discarded.
    """
    text, cv = _render_capturing_canvas(monkeypatch, _m1_graph(), w=80, h=24)
    assert len(cv.dots) > 0
    assert _braille_count(text) > 0


def test_at_007b_the_containment_arm_nothing_the_renderer_painted_is_lost(monkeypatch):
    """`count > 0` reddens a DELETION but cannot redden a wrong composition.

    `M-CNV.2-a` -- compose the dots layer at the WRONG precedence, so braille
    overwrites the node cards -- emits the glyphs and passes `count > 0`.  It
    is caught here, because the card glyphs vanish from the painted set.
    `M-CNV.2-b` (draw braille only where the cell was already blank) passes
    both, correctly: braille is ADDED, and nothing is lost.

    The set is DERIVED from the run, never hand-listed.  A hand-list fails in
    both directions here: the parked one contained seven LayeredRenderer box
    glyphs this renderer never paints (so it would block the correct fix), and
    a non-ASCII-only subset is vacuous, because the three non-ASCII markers sit
    at pill origins the braille happens not to overwrite -- the glyphs the
    mutation actually destroys are ASCII letters from the pill titles.
    """
    text, cv = _render_capturing_canvas(monkeypatch, _m1_graph(), w=80, h=24)
    put_glyphs = {ch for ch, _ in cv.cells.values() if not ch.isspace()}
    painted = {c for c in text.plain if not c.isspace()}

    assert len(put_glyphs) >= 10, "the derived containment set is too small to discriminate"
    assert put_glyphs <= painted
    assert PRE_CHANGE_PAINTED <= painted
    assert any(ord(c) in BRAILLE for c in painted), "the arm must be measured on a render that added braille"


def test_at_007b_a_single_node_graph_paints_no_braille_for_the_stated_reason(monkeypatch):
    """The empty arm names ONE cause.

    `count == 0` on a single node passed BEFORE the fix for two independent
    reasons -- the dots layer was empty AND `rows()` dropped it regardless --
    so it could not tell you which held, and after the fix it would have
    changed from passing for the wrong reason to passing for the right one with
    no observable difference.  Asserting the layer is empty names the cause.
    """
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="solo")))
    text, cv = _render_capturing_canvas(monkeypatch, g, w=80, h=24)
    assert len(cv.dots) == 0
    assert _braille_count(text) == 0


def test_llr_cnv_1_1_the_renderer_no_longer_monkey_patches_the_canvas(monkeypatch):
    """The layers are the canvas's, declared in its constructor."""
    _, cv = _render_capturing_canvas(monkeypatch, _m1_graph(), w=80, h=24)
    assert isinstance(cv, Canvas)
    assert cv.dots is not Canvas(1, 1).dots
    assert "dots" in vars(cv) and "bgs" in vars(cv)


def test_radial_renderer():
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="Root")))
    g.add_node(Node(id="a", ficha=Ficha(title="A")))
    g.add_node(Node(id="b", ficha=Ficha(title="B")))
    g.add_edge(Edge("root", "a"))
    g.add_edge(Edge("root", "b"))

    renderer = RadialRenderer()
    text = renderer.render(g, selected_id="a", w=60, h=20)
    assert "Root" in text.plain
    assert "A" in text.plain
    assert "B" in text.plain
