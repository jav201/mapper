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

# SEVERAL GEOMETRIES, AND THE CODE REVIEW IS WHY. These arms drove one frame
# (118x34), so replacing BOTH derivations with constants equal to their values
# there left the entire default lane green at 1051 passed -- while `chain(200)`
# under that mutant built a 96-cell row into a 24-cell canvas, a 4x overrun of
# the exact pathology the caps exist to prevent. That is control 20 of this
# batch's own catalog -- "a parametrization that samples one failure mode tests
# one failure mode" -- and this module did not inherit it from the sibling that
# quotes it verbatim.
GEOMETRIES = ((118, 34), (40, 20), (24, 10))
W, H = 118, 34


def chain(depth: int, titled: bool = True) -> Graph:
    """A chain. `titled=False` gives titles that CANNOT contain the level.

    The level-free titles exist because the depth-marker oracle was satisfied by
    the fixture: titles read `nodo {i}`, so `str(depth - 1) in leaf` was True
    from the TITLE whatever the marker said. A marker reporting `level // 10`
    passed all ten arms.
    """
    g = Graph()
    g.add_node(Node(id="n0", ficha=Ficha(title="raiz")))
    for i in range(1, depth):
        title = f"nodo {i}" if titled else "nodo"
        g.add_node(Node(id=f"n{i}", ficha=Ficha(title=title)))
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


def _rows_of(graph: Graph, w: int = W, h: int = H):
    rows, _sc = outline._rows(graph, ViewState(selected_id=graph.root_id, w=w, h=h))
    return rows


def _widest(rows) -> int:
    return max((Text(t.plain).cell_len for _n, t in rows), default=0)


# ---------------------------------------------------------------- the walk cost


@pytest.mark.parametrize("geom", GEOMETRIES)
@pytest.mark.parametrize("depth", (200, 1000, 4000))
def test_the_indent_is_bounded_by_geometry(depth, geom):
    """MEASURED PRE-FIX: 8,029 cells at depth 4000, into a canvas 118 wide.

    The bound is DERIVED from the render width (`B-61`), so this asserts against
    `W` rather than against a number typed here -- a literal ceiling would pass
    at a width nobody drives.
    """
    w, h = geom
    rows = _rows_of(chain(depth), w, h)
    leaf = rows[-1][1].plain
    lead = len(leaf) - len(leaf.lstrip(" "))

    # THE ORACLE IS THE INDENT, NOT THE WHOLE ROW, and getting that wrong is
    # worth recording. The first strengthening of this arm asserted
    # `widest_row <= w` and FAILED at (40,20) and (24,10) -- correctly, but for
    # the wrong reason: a row is ALLOWED to exceed the width. Rich wraps it and
    # `_fit` prices the physical rows that result; that is the whole basis of
    # `B-61`. What must track the width is the INDENT, because that is the
    # quadratic term. So the walk-cost bound is asserted where it lives, and the
    # whole-row bound is the frame ceiling below.
    assert lead <= w // 2, (
        f"depth {depth} at {geom}: the leaf's indent run is {lead} cells against "
        f"a derived budget of {w // 2}. The budget is not tracking the frame -- "
        "a constant equal to the 118-wide value (59) passes at 118 and overruns "
        "at 24"
    )
    assert _widest(rows) <= w * h + w, (
        f"depth {depth} at {geom}: widest row is {_widest(rows)} cells against a "
        f"frame of {w * h}"
    )


@pytest.mark.parametrize("depth", (200, 1000, 4000))
def test_a_compressed_indent_still_tells_the_truth_about_depth(depth):
    """THE CONDITION ON THE LICENCE. Compression may not become a lie.

    A capped indent that simply stopped indenting would render a depth-4000 leaf
    identically to a depth-3 one -- the picture would be cheap and false. The
    marker carries the REAL level, so the row still asserts the truth.
    """
    # TITLES WITHOUT THE LEVEL, and the marker read ADJACENT to its glyph.
    # Both halves are the fix: the old oracle was `str(depth-1) in leaf` over
    # titles reading `nodo {i}`, so the TITLE satisfied it and a marker
    # reporting `level // 10` -- lying about depth by 10x -- passed.
    rows = _rows_of(chain(depth, titled=False))
    leaf = rows[-1][1].plain
    assert outline.DEPTH_MARK in leaf, (
        f"depth {depth}: the leaf row carries no compression marker, so a deep "
        f"chain is indistinguishable from a shallow one: {leaf[:60]!r}"
    )
    assert f"{outline.DEPTH_MARK}{depth - 1}" in leaf, (
        f"depth {depth}: the marker does not state the TRUE level "
        f"({depth - 1}) beside its glyph: {leaf[:60]!r}. A marker that "
        "compresses is licensed; one that misreports depth is not"
    )


# ------------------------------------------------------------ F2, the row cap


@pytest.mark.parametrize("geom", GEOMETRIES)
@pytest.mark.parametrize("n", (10_000, 400_000))
def test_a_monster_title_is_clipped_to_one_frame(n, geom):
    """MEASURED PRE-FIX: a 400,000-character title built a 400,004-cell row.

    The ceiling is one FRAME (`w * h`): a row longer than that cannot be shown
    entirely by any frame of this size, so beyond it the renderer was building
    text only to wrap, price and discard it.

    THREE GEOMETRIES, AND THE CONFIRMATION PASS IS WHY. The first fold added the
    sweep to the INDENT arm and left this one at a single frame, so `F1` was only
    half closed: substituting `row_cap = 4012` -- its value at 118x34 -- while
    leaving the indent derived survived the ENTIRE DEFAULT LANE at 1059 passed,
    building a 4,016-cell row into a 240-cell canvas. A 16.7x overrun at (24,10),
    lane green. Control 20 twice in one module: a fix that applies the control to
    one of two siblings has applied it to neither.
    """
    w, h = geom
    widest = _widest(_rows_of(wide(n), w, h))
    assert widest <= w * h + w, (
        f"a {n}-character title produced a {widest}-cell row at {geom}; the "
        f"frame is {w}x{h} = {w * h} cells. A constant equal to the 118x34 value "
        "passes there and overruns by 16.7x at (24,10)"
    )


def test_the_clip_uses_the_existing_ellipsis_idiom():
    """ONE GRAMMAR. A second truncator would be a second thing to keep in step.

    `layered._clip` is also the helper that COERCES the file-derived title, so
    routing through it buys the bound and the coercion together.

    THIS DOCSTRING CARRIED THE RETRACTED SENTENCE TWO DOCSTRINGS ABOVE THE ONE
    THAT RETRACTED IT. It read "...is also where `LLR-COERCE.2`'s ordering lives
    -- coerce, THEN truncate -- so routing through it fixes the ordering as well
    as the bound", which is the verbatim claim retracted at `outline.py` and in
    `AT-056`. `plain` maps all 235 banned points to one `U+FFFD` each and is
    therefore index-preserving, so the ordering buys nothing here; a mutant
    running the forbidden order stays green. Retracting a claim in one file while
    it stands in the same file's neighbour is how it comes back.

    What this arm actually asserts is narrow and stated as such: the clip uses
    the ELLIPSIS idiom rather than a second truncator's grammar. The coercion is
    pinned by `test_outlines_title_path_is_coerced_not_merely_clipped` below and,
    repo-wide, by `test_inc3_census.py`.
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


# ---------------------------------------------------------- the caps' premise


def test_the_caps_licence_holds_outline_still_reads_no_pan():
    """THE DEPENDENCY THE CAPS REST ON, ARMED (`PAN-1`).

    Capping the indent is only safe because cells past the canvas width are
    UNREACHABLE in this view -- outline reads no pan, so there is no horizontal
    scroll that could take the operator into the region the cap removes.
    `rail.py`'s licence to cap came from its fixed width and absent pan, and such
    a licence does not transfer by resemblance; this one was checked.

    IT WAS DECLARED AND NOT ARMED, WHICH THE CODE REVIEW CALLED ASYMMETRIC --
    this same increment pinned radial's header-charge residue with two arms while
    leaving its own premise on prose. If outline ever gains pan, the caps must be
    revisited, and this arm is what says so at the moment it happens rather than
    at the next review.

    AST, NOT TEXT (control 22): the module's own docstrings discuss `pan_x` in
    prose, so a grep answers "present" for a file with zero live reads. Only the
    parsed tree distinguishes a description of the defect from the defect.
    """
    import ast
    from pathlib import Path

    src = Path(outline.__file__).read_text(encoding="utf-8")
    reads = [
        node.attr
        for node in ast.walk(ast.parse(src))
        if isinstance(node, ast.Attribute) and node.attr in ("pan_x", "pan_y")
    ]
    assert reads == [], (
        f"outline now reads {sorted(set(reads))}. The cost caps assume content "
        "past the canvas width is unreachable in this view -- if pan arrived, "
        "that premise is gone and `_indent`'s budget must be revisited "
        "(`PAN-1`, routed to S-D)"
    )


# ------------------------------------------------- the coercion the cap rides


def test_outlines_title_path_is_coerced_not_merely_clipped():
    """`LLR-COERCE.2` AT OUTLINE'S CALL SITE -- the arm this increment shipped without.

    THIS ARM'S FIRST DOCSTRING WAS FALSE, AND THE CONFIRMATION PASS MEASURED IT
    FALSE. It repeated gate 2's premise -- "removing the COERCION and removing
    the CAP fail the identical three tests, so the coercion contributed ZERO
    SIGNAL" -- and that does not reproduce. Isolating the coercion (cap kept,
    coercion removed) reddens TWO arms: this one AND
    `test_inc3_census.py::test_a89_every_reached_renderer_coerces_what_it_paints`.
    That census arm is UNCHANGED across both folds and was written two increments
    earlier, so outline's coercion was already pinned before it was declared
    unpinned. A true outcome resting on a false measurement -- this batch's own
    recurring shape, and it was in the arm that exists to prevent it.

    SO WHY THIS ARM STILL EXISTS. The census pins the property repo-wide; this
    pins it AT THE CALL SITE, names the code points per `C-56`, and fails with a
    message that says which one escaped. Defence in depth beside a census arm is
    defensible -- claiming the call site was unarmed was not. `TC-081`, the node
    `01-requirements.md` designates for `LLR-COERCE.2`, still does not exist.

    THE PROPERTY IS "COERCED AT ALL", AND THAT IS DELIBERATE. The same review
    refuted the ordering rationale this line once carried: `plain` maps every
    banned code point to exactly one `U+FFFD`, so it is length- and
    index-preserving and the coerce/truncate order cannot matter. What matters is
    that the path is coerced, so that is what is asserted.

    WHAT IT COSTS WHEN IT IS NOT: with the coercion removed, `U+001B`, `U+202E`
    and `U+E0041` reach the painted row AND the exported SVG, and the SVG stops
    parsing as XML -- which is `B-47`/`A-89`, the defect this renderer's own
    comment says it closed.

    Code points are NAMED, never pasted (`C-56`).
    """
    hostile = "acta" + chr(0x1B) + chr(0x202E) + chr(0xE0041) + chr(0x200D) + "firmada"
    g = Graph()
    g.add_node(Node(id="raiz", ficha=Ficha(title="raiz")))
    g.add_node(Node(id="malo", ficha=Ficha(title=hostile)))
    g.add_edge(Edge("raiz", "malo"))
    g.root_id = "raiz"

    body = "".join(t.plain for _n, t in _rows_of(g))
    for cp, name in ((0x1B, "U+001B"), (0x202E, "U+202E"),
                     (0xE0041, "U+E0041"), (0x200D, "U+200D")):
        assert chr(cp) not in body, (
            f"{name} reached the painted row from a ficha title. Outline's title "
            "path is no longer coerced -- it reaches the SVG export too, where it "
            "stops the document parsing as XML (B-47 / A-89)"
        )
    # NON-VACUITY: the row must still carry the benign text, or the assertions
    # above are satisfied by a renderer that painted nothing at all.
    assert "acta" in body and "firmada" in body, (
        f"the hostile title vanished entirely rather than being coerced: {body!r}"
    )
