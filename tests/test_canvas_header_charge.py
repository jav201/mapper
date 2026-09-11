"""`S-B(+C)` defect 2 — the canvas header charge is PER RENDERER.

`MapScreen._canvas_size` had no renderer branch while `refresh_canvas` picked the
renderer separately, so outline and radial were priced with LAYERED's header.

THE POSITIVE CONTROL IS THE LOAD-BEARING ROW. `layered.header_rows` agrees with
layered's own first line at all ten widths of the sweep; that is what makes the
outline and radial gaps a finding rather than instrument error. An arm that only
showed outline differing from layered could not tell "outline is overcharged"
from "the instrument disagrees with the charge".
"""
from __future__ import annotations

import pytest
from rich.console import Console
from rich.text import Text

from mapper.model import Edge, Ficha, Graph, Node, SchemaField
from mapper.views import layered, outline, radial
from mapper.views.state import ViewState

WIDTHS = (20, 24, 28, 34, 40, 50, 60, 80, 100, 118)


def _graph() -> Graph:
    g = Graph()
    g.schema = [SchemaField(key="D", label="documento", required=True)]
    g.add_node(Node(id="raiz", ficha=Ficha(title="Auditoria legacy", fields={"D": "x"})))
    for i in range(7):
        nid = f"n{i}"
        g.add_node(Node(id=nid, ficha=Ficha(title=f"Proceso numero {i}")))
        g.add_edge(Edge("raiz", nid))
    g.root_id = "raiz"
    return g


def _first_line_rows(renderer, graph: Graph, w: int) -> int:
    """PHYSICAL rows the renderer's own first line occupies -- measured, not computed.

    The same `Console.render_lines` instrument `outline._fit` and
    `layered.header_rows` use. A `ceil(cells / w)` formula is `B-61`.
    """
    out = renderer.render(graph, ViewState(selected_id="raiz", w=w, h=24))
    first = out.split(allow_blank=True)[0] if out.plain else Text("")
    return len(Console(width=w).render_lines(first, pad=False))


@pytest.mark.parametrize("w", WIDTHS)
def test_the_layered_charge_equals_layered_own_first_line(w):
    """POSITIVE CONTROL. Without this the other two arms prove nothing.

    If the charge and the measuring instrument disagreed even for the renderer
    the charge was BUILT for, then every gap this module reports would be the
    instrument's, not the code's.
    """
    graph = _graph()
    assert layered.header_rows(graph, w, w) == _first_line_rows(
        layered.LayeredRenderer(), graph, w
    ), (
        f"at w={w} the layered charge disagrees with layered's own first line; "
        "the instrument and the charge are not describing the same frame, so no "
        "gap this module reports can be trusted"
    )


# Widths where outline's OWN header wraps past one row. Without these the sweep
# above cannot tell `outline.header_rows` from `return 1`: the header is
# `\u25c6 mapper \u00b7 outline`, 18 cells, so every width in `WIDTHS` prices it at
# exactly one row and a constant passes all ten. FIRED: the constant mutant
# SURVIVED the ten-width sweep. This is control 20 in the batch's own catalog --
# a parametrization that samples one failure mode tests one failure mode.
NARROW = (6, 8, 10, 12, 14, 16)


def test_the_narrow_sweep_actually_exercises_a_wrap():
    """META-ARM: the widths above must produce a charge greater than one.

    Without this, `NARROW` could silently stop exercising the wrap -- if the
    header were shortened, every width would price at one row again and the arm
    below would go back to being unable to fail, with nothing saying so.
    """
    graph = _graph()
    charges = {w: outline.header_rows(graph, w, w) for w in NARROW}
    assert max(charges.values()) > 1, (
        f"no width in NARROW wraps outline's header: {charges}. The arm below "
        "can no longer distinguish a measurement from a constant"
    )


@pytest.mark.parametrize("w", WIDTHS)
def test_outline_is_charged_its_own_header_and_not_layereds(w):
    """`outline.header_rows` prices OUTLINE's header.

    Measured pre-fix: layered's charge exceeds outline's own first line by TWO
    rows at 20..28 and by ONE from 34 up -- at every width in the sweep. Each
    overcharged row is a body row the region could have shown.
    """
    graph = _graph()
    assert outline.header_rows(graph, w, w) == _first_line_rows(
        outline.OutlineRenderer(), graph, w
    ), f"at w={w} outline's charge does not equal outline's own first line"


@pytest.mark.parametrize("w", (24, 28, 50, 80, 118))
def test_radial_still_receives_layereds_charge_and_S_D_must_redden_this(w):
    """THE DECLARED RESIDUE, PINNED SO IT CANNOT CLOSE SILENTLY.

    `views/radial.py` is `S-D`'s file, so registering a radial charge here would
    put `S-B(+C)` over its file cap. The coordinator ruled for the option that
    STATES the hole rather than omitting it -- this batch's `AT-058` doctrine
    applied to a charge instead of a declaration.

    So this arm pins the WRONG number on purpose. It asserts radial is still
    priced with layered's header AND that layered's header is genuinely larger
    than radial's own first line at these widths, which is what makes the residue
    real rather than a naming difference.

    **`S-D` MUST REDDEN THIS ARM.** When radial gets its own measured charge,
    this arm fails and is rewritten to the equality form the other two use. A
    green run of this arm after `S-D` means `S-D` did not close the residue.
    """
    graph = _graph()
    charged = layered.header_rows(graph, w, w)
    own = _first_line_rows(radial.RadialRenderer(), graph, w)
    assert charged > own, (
        f"at w={w} layered's charge ({charged}) no longer exceeds radial's own "
        f"first line ({own}). Either radial's header grew or S-D landed; if S-D "
        "landed, rewrite this arm to the equality form -- do not delete it"
    )


# ---------------------------------------------------------------------------
# THE DISPATCH ITSELF.
#
# The three arms above test the module-level CHARGES. None of them can see
# `app.py` revert to charging layered everywhere, because none of them go
# through `_header_rows_for` -- the arm would stay green while the defect came
# back. That is the same shape as this batch's `M-TXT` (an arm asserting a
# property of an expression it built itself) and its `P1` arms (trigger
# independence mistaken for discriminating power). So the dispatch is driven.


def _screen():
    from mapper.app import MapScreen

    return MapScreen("test")


def test_the_dispatch_gives_each_view_its_own_charge():
    """`MapScreen` charges outline OUTLINE's header, not layered's."""
    screen = _screen()
    assert screen._header_rows_for(screen.renderer) is layered.header_rows
    assert screen._header_rows_for(screen.outline_renderer) is outline.header_rows


def test_radial_dispatch_is_the_DECLARED_residue_and_S_D_must_change_it():
    """Radial is routed to LAYERED's charge ON PURPOSE, and that is pinned.

    `views/radial.py` is `S-D`'s file; registering a radial charge here would put
    `S-B(+C)` over its file cap. The coordinator ruled for stating the hole
    rather than omitting it. **`S-D` MUST REDDEN THIS ARM** -- when radial gets
    its own charge, this identity stops holding.
    """
    screen = _screen()
    assert screen._header_rows_for(screen.radial_renderer) is layered.header_rows, (
        "radial no longer receives layered's charge -- if S-D landed, rewrite "
        "this arm to assert radial.header_rows; do not delete it"
    )


def test_an_unregistered_renderer_RAISES_rather_than_defaulting():
    """An absent renderer is a CODE DEFECT, not a view with no header.

    Matching `_painted_ids_for`: a silent default would let a new view be priced
    with some other view's header and paint into a void, which is `CR-F1`'s
    defect and the reason this batch made that dispatch raise in the first place.
    """
    screen = _screen()
    with pytest.raises(LookupError):
        screen._header_rows_for(object())


def test_the_header_rows_METHOD_routes_through_the_dispatch(monkeypatch):
    """`_header_rows` must USE the dispatch, not merely have one beside it.

    FIRED AND NEEDED. The first version of this module tested the module-level
    charges and `_header_rows_for` in isolation, and a mutant that reverted
    `_header_rows`'s BODY to `layered.header_rows` in every view SURVIVED all 28
    arms -- the dispatch existed, was correct, and was not called. That is this
    batch's `P1` lesson exactly: trigger-independence is not discriminating
    power, so the arm supplies the trigger and asserts the result came from the
    branch it names.

    `_canvas_width` is stubbed because it reads widget geometry that needs a live
    app; the stub fixes the ONE input the charge does not depend on here, and the
    assertion is still about which FUNCTION produced the number.
    """
    graph = _graph()
    screen = _screen()
    screen.graph = graph
    monkeypatch.setattr(type(screen), "_canvas_width", lambda self: 40)

    screen.outline_mode = True
    screen.radial_mode = False
    got = screen._header_rows(40)
    assert got == outline.header_rows(graph, 40, 40), (
        "the outline view's charge did not come from outline.header_rows"
    )
    assert got != layered.header_rows(graph, 40, 40), (
        f"the outline view is still being charged layered's header ({got}); "
        "the dispatch is present but `_header_rows` is not routing through it"
    )

    screen.outline_mode = False
    assert screen._header_rows(40) == layered.header_rows(graph, 40, 40)


@pytest.mark.parametrize("w", NARROW)
def test_the_outline_charge_is_measured_and_not_the_constant_one(w):
    """At narrow widths the charge must EXCEED one, which a constant cannot do.

    THE RENDERED-FIRST-LINE ORACLE DOES NOT APPLY HERE, AND THAT IS A FINDING
    RATHER THAN AN INCONVENIENCE. Driven at these widths, the arm above fails --
    not because the charge is wrong, but because the two sides stop describing
    the same line. `_fit_declared` WIDENS `rows[0]` with the `fuera de vista`
    declaration when rows are hidden, so the renderer's first emitted line is the
    DECLARING header, while the charge prices the BARE one.

    The charge is right to price the bare header: `_canvas_size` runs BEFORE the
    renderer and hands it an `h`; the declaration-widening then happens inside
    that budget, where `_fit` prices every row physically and drops one to make
    room. A charge that tried to anticipate the widening would be pricing a frame
    that does not exist yet -- and would need the fit whose input it is computing.

    So this regime asserts the property the constant mutant violates, and says
    plainly which oracle it is NOT using.
    """
    graph = _graph()
    assert outline.header_rows(graph, w, w) > 1, (
        f"at w={w} outline's header is priced at one row; the header is 18 cells "
        "and cannot fit. A constant would pass here"
    )


def test_the_METHOD_degrades_where_the_DISPATCH_raises(monkeypatch):
    """The asymmetry is DELIBERATE, and it is pinned so a tidy-up cannot undo it.

    `_header_rows_for` RAISES for an unregistered renderer -- an absent charge is
    a code defect, and the arm above pins that. `_header_rows` must NOT, because
    it runs inside the drawing path: `_canvas_size` is called BEFORE
    `refresh_canvas`'s guard, so a raise there kills the one path `LLR-R01.4`
    ratifies as survive-anything.

    THIS WAS NOT FORESEEN, IT WAS FIRED. The first version of this increment
    copied `_painted_ids_for`'s strict shape wholesale, and `TC-R08` -- which
    installs a renderer that is not one of the three and asserts the app still
    paints "no se pudo dibujar el mapa" -- failed on both of its parameter cases.
    The pattern transferred; the CONSEQUENCE did not. A declaration that raises
    costs a numeral; a charge that raises costs the whole picture.

    So: strict where it can be acted on, degrading where a ratified guarantee
    outranks it. Anyone making these two symmetric again must redden this arm.
    """
    screen = _screen()
    screen.graph = _graph()
    monkeypatch.setattr(type(screen), "_canvas_width", lambda self: 40)
    monkeypatch.setattr(type(screen), "_current_renderer", lambda self: object())

    with pytest.raises(LookupError):
        screen._header_rows_for(screen._current_renderer())

    assert screen._header_rows(40) == layered.header_rows(screen.graph, 40, 40), (
        "an unregistered renderer must fall back to layered's charge inside the "
        "drawing path, not raise -- TC-R08 is what this protects"
    )
