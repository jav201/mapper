"""`S-B` -- outline's two cost caps, and the declarations that keep them honest.

Coordinator ruling 2026-09-11 took option (b): the caps are a DELIBERATE
improvement, not a cost-only change. `_fit` prices rows PHYSICALLY, so a shorter
row occupies fewer physical rows and `_fit` keeps MORE of them -- the picture and
the declared hidden count both move, on purpose.

THE CONDITION ATTACHED TO THAT LICENCE IS WHAT THESE ARMS PIN: a capped form must
DECLARE its capping in the frame. A capped title shows the existing ellipsis
idiom (`layered._clip`, one grammar, not a new one). A capped indent must not lie
about depth -- it carries the TRUE level beside a compression marker, so a deep
chain reads as deep and not as shallow. What the operator sees may compress; what
it ASSERTS stays true.
"""
from __future__ import annotations

import pytest
from rich.text import Text

from mapper.model import Edge, Ficha, Graph, Node
from mapper.views import outline
from mapper.views.state import ViewState

W, H = 118, 34


def chain(depth: int) -> Graph:
    g = Graph()
    g.add_node(Node(id="n0", ficha=Ficha(title="raiz")))
    for i in range(1, depth):
        g.add_node(Node(id=f"n{i}", ficha=Ficha(title=f"nodo {i}")))
        g.add_edge(Edge(f"n{i-1}", f"n{i}"))
    g.root_id = "n0"
    return g


def wide(n_chars: int) -> Graph:
    g = Graph()
    g.add_node(Node(id="raiz", ficha=Ficha(title="raiz")))
    g.add_node(Node(id="gordo", ficha=Ficha(title="x" * n_chars)))
    g.add_edge(Edge("raiz", "gordo"))
    g.root_id = "raiz"
    return g


def _rows_of(graph: Graph):
    rows, _sc = outline._rows(graph, ViewState(selected_id=graph.root_id, w=W, h=H))
    return rows


def _widest(rows) -> int:
    return max((Text(t.plain).cell_len for _n, t in rows), default=0)


# ---------------------------------------------------------------- the walk cost


@pytest.mark.parametrize("depth", (200, 1000, 4000))
def test_the_indent_is_bounded_by_geometry(depth):
    """MEASURED PRE-FIX: 8,029 cells at depth 4000, into a canvas 118 wide.

    The bound is DERIVED from the render width (`B-61`), so this asserts against
    `W` rather than against a number typed here -- a literal ceiling would pass
    at a width nobody drives.
    """
    widest = _widest(_rows_of(chain(depth)))
    assert widest <= W, (
        f"depth {depth}: widest row is {widest} cells into a {W}-cell canvas. "
        "The indent is unbounded again and the walk is quadratic in depth"
    )


@pytest.mark.parametrize("depth", (200, 1000, 4000))
def test_a_compressed_indent_still_tells_the_truth_about_depth(depth):
    """THE CONDITION ON THE LICENCE. Compression may not become a lie.

    A capped indent that simply stopped indenting would render a depth-4000 leaf
    identically to a depth-3 one -- the picture would be cheap and false. The
    marker carries the REAL level, so the row still asserts the truth.
    """
    rows = _rows_of(chain(depth))
    leaf = rows[-1][1].plain
    assert outline.DEPTH_MARK in leaf, (
        f"depth {depth}: the leaf row carries no compression marker, so a deep "
        f"chain is indistinguishable from a shallow one: {leaf[:60]!r}"
    )
    assert str(depth - 1) in leaf, (
        f"depth {depth}: the leaf row does not carry its true level "
        f"({depth - 1}): {leaf[:60]!r}"
    )


# ------------------------------------------------------------ F2, the row cap


@pytest.mark.parametrize("n", (10_000, 400_000))
def test_a_monster_title_is_clipped_to_one_frame(n):
    """MEASURED PRE-FIX: a 400,000-character title built a 400,004-cell row.

    The ceiling is one FRAME (`w * h`): a row longer than that cannot be shown
    entirely by any frame of this size, so beyond it the renderer was building
    text only to wrap, price and discard it.
    """
    widest = _widest(_rows_of(wide(n)))
    assert widest <= W * H + W, (
        f"a {n}-character title produced a {widest}-cell row; the frame is "
        f"{W}x{H} = {W * H} cells"
    )


def test_the_clip_uses_the_existing_ellipsis_idiom():
    """ONE GRAMMAR. A second truncator would be a second thing to keep in step.

    `layered._clip` is also where `LLR-COERCE.2`'s ordering lives -- coerce, THEN
    truncate -- so routing through it fixes the ordering as well as the bound.
    """
    rows = _rows_of(wide(400_000))
    fat = [t.plain for _n, t in rows if "x" in t.plain][0]
    assert fat.endswith("…"), (
        f"the clipped title does not use the ellipsis idiom: {fat[-20:]!r}"
    )


# ------------------------------------------------------------------- controls


def test_an_ordinary_map_is_untouched_by_either_cap():
    """THE CONTROL, and it is not decoration.

    Both arms above would still pass if the caps fired on EVERY row -- a
    renderer that clipped everything to one cell is bounded and marked. This
    asserts the caps stay out of the way of the maps the operator actually has:
    no marker, no ellipsis, and the indent still proportional to depth.
    """
    g = Graph()
    g.add_node(Node(id="raiz", ficha=Ficha(title="Auditoria")))
    g.add_node(Node(id="a", ficha=Ficha(title="Finanzas")))
    g.add_node(Node(id="b", ficha=Ficha(title="Nomina")))
    g.add_edge(Edge("raiz", "a"))
    g.add_edge(Edge("a", "b"))
    g.root_id = "raiz"

    body = "\n".join(t.plain for _n, t in _rows_of(g))
    assert outline.DEPTH_MARK not in body, (
        f"the depth marker fired on a 3-node map: {body!r}"
    )
    assert "…" not in body, f"the clip fired on short titles: {body!r}"
    # Depth still reads as depth: the grandchild is indented past the child.
    rows = _rows_of(g)
    lead = [len(t.plain) - len(t.plain.lstrip(" ")) for _n, t in rows[1:]]
    assert lead == sorted(lead) and lead[-1] > lead[0], (
        f"indentation no longer tracks depth on an ordinary map: {lead}"
    )
