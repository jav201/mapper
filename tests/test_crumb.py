"""Inc-CRUMB — the TITLE-LENGTH vector of the collapse `Inc-STRIPS` half-closed.

`Inc-STRIPS` bounded `#map-minimap` and `#map-pagination` and closed
`LLR-N07.3.4` against the FANOUT vector. The security review then measured that
the same collapse is reachable through a different door: `TabStrip`'s crumb is a
fourth unbounded strip taking a raw ficha title, and ONE 4000-character title
reproduces it verbatim -- canvas one row, count region off-viewport, at 80x24.

FOUR STRIPS, NOT TWO, AND THE FOURTH WAS FOUND BY A REVIEWER RATHER THAN BY THE
INCREMENT. `#map-toast` is the same shape with a smaller blast radius (it needs
an operator action and clears on the next toast), and `KeyBar` turned out to be
a FIFTH -- not unbounded, but rendering its first frame at a hard-coded 118
cells, which wraps to four rows on a narrow terminal and takes three from the
canvas.

THE CLOSING EVIDENCE IS A PAIR. This module's title-length arms must go
RED -> GREEN across the increment, AND `test_strips.py`'s fanout arms must stay
GREEN untouched. Either alone would leave the requirement half-closed again,
which is the state this increment exists to end.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from rich.text import Text

from mapper.app import COUNT_REGION_ID, MapperApp, SEARCH_COUNT_SUBJECT
from mapper.widgets.chrome import TabStrip
from mapper.model import Edge, Ficha, Graph, Node
from tests.inc3_support import open_map, rows_in

SIZES = [(118, 34), (80, 24)]
# Long enough to reproduce the measured collapse, and the security review's own
# figure so the arm and the finding cite one number.
HOSTILE_CELLS = 4000
# `TabStrip` is a tab row that may wrap once at narrow widths, plus the one
# crumb row. More than that and the crumb is deciding the layout again.
#
# THREE, not two, and the difference was measured rather than chosen: at 60
# columns the tabs plus the wordmark exceed the terminal and the tab row wraps,
# so a two-row ceiling clipped the crumb away entirely -- `Inc-STRIPS`' F1
# reproduced by this increment's own lid, caught by the declaration arm below.
TABSTRIP_ROWS = 3


def deep_graph(title_cells: int, depth: int = 4) -> Graph:
    """A CHAIN, so the crumb has ancestors to drop as well as a tail to keep.

    A flat fixture would exercise the tail bound and never the ancestor
    accounting, and the declaration this increment adds is about the ancestors.
    """
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="R" * title_cells, meta="m")))
    parent = "root"
    for i in range(depth):
        nid = f"n{i}"
        g.add_node(Node(id=nid, ficha=Ficha(title=f"nivel {i} " + "y" * title_cells)))
        g.add_edge(Edge(parent, nid))
        parent = nid
    return g


@pytest.mark.parametrize("size", SIZES, ids=lambda s: f"{s[0]}x{s[1]}")
@pytest.mark.asyncio
async def test_at_the_title_length_vector_cannot_hide_the_count(tmp_path, size):
    """THE CLOSING ARM for `LLR-N07.3.4`'s second vector.

    Pre-fix this is RED at both sizes: at 80x24 `TabStrip` rendered 54 rows and
    put `#map-canvas` at y=56 and the count region at y=57, both off a 24-row
    frame. The predicate is the one `Inc-STRIPS` settled on -- the count is
    readable IN ITS OWN REGION, never merely that the region is on-viewport and
    never that the words appear somewhere on the frame.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        app.store.save("hostil", deep_graph(HOSTILE_CELLS))
        screen = await open_map(app, pilot, "hostil")
        await pilot.pause()

        canvas = screen.query_one("#map-canvas").region
        assert canvas.height > 1, (
            f"at {size} the canvas is {canvas.height} row(s): a strip has taken "
            "the frame, which is the collapse this increment closes"
        )

        await pilot.press("/")
        await pilot.pause()
        for ch in "nivel":
            await pilot.press(ch)
        await pilot.press("enter")
        await pilot.pause()

        rows = rows_in(screen, screen.query_one(f"#{COUNT_REGION_ID}").region)
        assert rows, f"at {size} the count region is off-viewport"
        painted = " ".join(" ".join(rows).split())
        assert SEARCH_COUNT_SUBJECT in painted, (
            f"at {size} the count is not readable in its own region on a map "
            "whose only unusual property is a long title"
        )


@pytest.mark.parametrize("size", SIZES, ids=lambda s: f"{s[0]}x{s[1]}")
@pytest.mark.asyncio
async def test_the_crumb_cannot_outgrow_its_ceiling(tmp_path, size):
    """The bound itself, independent of what it protects.

    Driven at a length that reproduced the collapse AND at one that merely
    degraded it -- 500 characters already cost a third of the canvas at 80x24,
    so a bound that only holds at the extreme is not a bound.
    """
    for cells in (500, HOSTILE_CELLS):
        app = MapperApp(tmp_path)
        async with app.run_test(size=size) as pilot:
            await pilot.pause()
            app.store.save(f"t{cells}", deep_graph(cells))
            screen = await open_map(app, pilot, f"t{cells}")
            await pilot.pause()
            strip = screen.query_one("TabStrip").region
            assert strip.height <= TABSTRIP_ROWS, (
                f"at {size} with a {cells}-cell title TabStrip is "
                f"{strip.height} rows; the crumb is deciding the layout"
            )


@pytest.mark.asyncio
async def test_the_crumb_declares_the_ancestors_it_drops(tmp_path):
    """Bounded is not enough: what is dropped has to be SAID.

    `keybar` states the reason in its own docstring -- a bare ellipsis "is a lie
    by omission: it says something was cut but not that anything is missing, let
    alone how much". The crumb now ends `+N … / tail` for the same reason.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=(60, 24)) as pilot:
        await pilot.pause()
        app.store.save("deep", deep_graph(40, depth=5))
        screen = await open_map(app, pilot, "deep")
        await pilot.pause()
        # THE CURSOR HAS TO BE DEEP, and the first draft of this arm forgot it:
        # the crumb reflects the CURSOR's path, so at the root there are no
        # ancestors to drop and the arm was asserting a declaration that had
        # nothing to declare. It failed for the right reason and said so.
        screen.nav.cursor = "n4"
        screen.refresh_canvas()
        await pilot.pause()
        strip = screen.query_one("TabStrip")
        painted = " ".join(" ".join(rows_in(screen, strip.region)).split())
        assert "…" in painted, (
            "the crumb dropped ancestors without marking the truncation"
        )
        assert "+" in painted, (
            "the crumb elides ancestors without declaring HOW MANY -- a bare "
            "ellipsis is a lie by omission"
        )


@pytest.mark.asyncio
async def test_the_toast_detail_cannot_take_the_canvas(tmp_path):
    """`SEC-F4`. Same class as the crumb, smaller blast radius.

    Several `_event_toast` call sites hand it a file-derived node title, and
    `#map-toast` took its rows from `#map-body`: measured, a 4000-character
    detail rendered 36 rows at 118x34 and left the canvas ONE.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("m", deep_graph(4))
        screen = await open_map(app, pilot, "m")
        await pilot.pause()
        screen._event_toast("probado", "T" * HOSTILE_CELLS)  # noqa: SLF001
        await pilot.pause()

        assert screen.query_one("#map-toast").region.height <= 2, (
            "the toast strip grew past two rows on a long detail"
        )
        assert screen.query_one("#map-canvas").region.height > 1, (
            "a toast detail took the canvas; the bound is at the wrong seam"
        )


@pytest.mark.asyncio
async def test_the_keybar_renders_at_its_TRUE_width_on_the_first_frame(tmp_path):
    """The FIFTH strip, and the one no bound would have caught.

    `KeyBar.__init__` rendered at a hard-coded 118 cells and relied on
    `on_resize` to correct it. The correction lands -- and is not enough.

    MEASURED, against a reconstruction of the pre-fix widget: the resize fires,
    `keybar` is called again at the true width, and the pre-fix widget HOLDS the
    corrected render. At 35 columns it paints the same text as the fixed one.
    Its region is FOUR rows against ONE, because auto-height was computed from
    the 118-cell render when layout ran and `update()` does not re-run that.

    That is why this arm asserts the REGION HEIGHT and the canvas it steals
    from, not the painted text: the painted text is identical across the defect
    and cannot fail. HEAD's own numbers are the oracle -- `KeyBar` one row.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=(35, 14)) as pilot:
        await pilot.pause()
        app.store.save("m", deep_graph(4, depth=2))
        screen = await open_map(app, pilot, "m")
        await pilot.pause()

        assert screen.query_one("KeyBar").region.height == 1, (
            "KeyBar is wrapping on the first frame: it is rendering at a width "
            "the terminal does not have"
        )
        assert screen.query_one("#map-canvas").region.height > 1, (
            "the canvas lost its rows to the key bar"
        )


# Widths BELOW the tab row's natural floor (62), where the first version of the
# bound was measured against the wrong number and no arm was looking.
#
# THE FLOOR IS 31, MEASURED RATHER THAN ESTIMATED. Below it the TAB ROW ALONE
# needs three rows -- the tabs plus the wordmark are about 57 cells -- so it
# fills the whole ceiling and evicts the crumb no matter how well the crumb is
# bounded. That is the PRE-EXISTING tab-row wrap this increment carries and does
# not claim to fix (`tab_strip` sizes itself to `max(width, tabs + wordmark)`),
# and it is the honest lower limit of what this arm can assert. Measured: the
# tab row is 3 rows at widths 28-30 and 2 rows from 31 up.
NARROW_WIDTHS = [35, 40, 50, 60]


@pytest.mark.parametrize("width", NARROW_WIDTHS)
@pytest.mark.asyncio
async def test_the_crumb_is_bounded_BELOW_the_tab_rows_natural_width(tmp_path, width):
    """The arm whose absence let the first bound ship broken.

    `tab_strip` sizes itself to `max(width, tabs + wordmark)` -- a floor of 62 --
    and the first version of this increment handed THAT to the crumb's budget
    instead of the terminal's width. Below 62 columns the crumb was therefore
    budgeted against a frame wider than the one it had: cell-correct against 62,
    and wrapped in reality. Measured then: six rows wanted at 30 columns with the
    crumb entirely evicted by the lid, and between 35 and 60 a line that ended
    mid-title with NEITHER ellipsis NOR `+N`, because `fit`'s ellipsis sat in the
    clipped row.

    The other arms in this module drive 118 and 80 -- the two widths at which
    that defect is invisible. That is why it shipped, and it is why this arm
    exists rather than a wider assertion on the existing ones.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 20)) as pilot:
        await pilot.pause()
        app.store.save("deep", deep_graph(80, depth=4))
        screen = await open_map(app, pilot, "deep")
        await pilot.pause()
        screen.nav.cursor = "n3"
        screen.refresh_canvas()
        await pilot.pause()

        strip = screen.query_one("TabStrip")
        assert strip.region.height <= TABSTRIP_ROWS, (
            f"at {width} columns TabStrip is {strip.region.height} rows"
        )
        painted = " ".join(" ".join(rows_in(screen, strip.region)).split())
        # THE CRUMB SURVIVES THE LID. A strip reporting its full height while
        # having eaten the crumb is the exact shape of `Inc-STRIPS`' F1, and at
        # 30 columns the first version of this bound did precisely that.
        assert "nivel 3" in painted or "…" in painted, (
            f"at {width} columns the crumb is not on the frame at all; the lid "
            f"ate it. Painted: {painted[:70]!r}"
        )


# ---------------------------------------------------------------------------
# SEC-F1 + DECL-118-TWICE -- ONE defect carried in halves since Inc-CRUMB.
#
# `TabStrip.__init__` renders the crumb with NO width, so `darkside._crumb_line`
# takes its own hardcoded 118-cell fallback. That fallback is the batch's
# declared context spelled a SECOND time -- `chrome._KEYBAR_FALLBACK_CELLS` is
# the first -- and nothing makes the two agree.
#
# It was recorded as not-live, and the reason matters: the content is superseded
# before paint and the height is clamped by `TabStrip`'s `max-height: 3` lid. So
# THE CSS LID IS LOAD-BEARING for the init path, which is the shape the batch
# named at Inc-CRUMB's birth -- never a CSS lid over unbounded content.


def _long_crumb() -> list[str]:
    """Ancestors long enough that a 118-cell budget and a 40-cell one differ."""
    return [f"nivel-{i}-" + "x" * 20 for i in range(6)]


@pytest.mark.parametrize("width", [30, 40, 60])
@pytest.mark.asyncio
async def test_sec_f1_the_first_crumb_render_is_budgeted_to_the_REAL_width(tmp_path, width):
    """The init render, before any resize can rescue it.

    Measured on the composited frame would prove nothing here: `on_resize` fires
    and supersedes the content, so the frame is right either way. The defect is
    in what the widget HOLDS at construction, and that is what a later render
    replaces -- the `KeyBar` lesson from `Inc-CRUMB`, one widget over.

    So this reads the renderable the constructor produced, with no resize
    allowed to intervene.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 20)) as pilot:
        await pilot.pause()
        strip = TabStrip("c", crumb=_long_crumb())
        held = strip.render()
        text = held.plain if hasattr(held, "plain") else str(held)
        crumb_row = text.split("\n")[1] if "\n" in text else ""
        cells = Text(crumb_row).cell_len

        assert crumb_row, "the fixture produced no crumb row; the arm is vacuous"
        assert cells <= width, (
            f"the constructor budgeted the crumb against {cells} cells at a "
            f"{width}-column terminal -- it took `_crumb_line`'s hardcoded 118 "
            "fallback instead of the width the app already knows. The CSS lid "
            "is what hides this, which is the one thing a lid must never be."
        )


def test_decl_118_is_spelled_ONCE():
    """The declared context has ONE home, and this is what pins it.

    `chrome._KEYBAR_FALLBACK_CELLS`, `darkside._crumb_line`'s inline fallback and
    `darkside.keybar`'s default parameter were the same number in three places
    with nothing making them agree -- the batch's own control: anything spelled
    twice will drift. THREE, not two: the carry record said two, and the third
    was found only when this arm was written. That is the ledger control proving
    itself on its first outing.

    COUNTED FROM THE AST, not by grepping the text. A regex over source lines
    counts the number inside docstrings and comments -- five of the eight hits
    the first version of this arm reported were PROSE describing the defect,
    including this module's own history. Only a real numeric literal can drift.
    """
    import ast

    from mapper import darkside as _d
    from mapper.widgets import chrome as _c

    spellings = {}
    for name, mod in (("darkside.py", _d), ("chrome.py", _c)):
        tree = ast.parse(Path(mod.__file__).read_text(encoding="utf-8"))
        spellings[name] = [
            node.lineno for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and node.value == 118
            and not isinstance(node.value, bool)
        ]
    total = sum(len(v) for v in spellings.values())
    assert total <= 1, (
        f"the declared context is spelled {total} times as a literal: "
        f"{spellings}. One home, or they drift -- and they cannot be kept in "
        "step by being equal today."
    )
