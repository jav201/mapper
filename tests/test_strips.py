"""Inc-STRIPS — the three unbounded strips, and the count nobody could read.

`LLR-N07.3.4` predicate 1 was recorded SATISFIED UNDER A MOVED BOUND: every
above-bound arm reached the branch by lowering `MAX_RENDER_NODES`, which drives
the handler honestly but cannot observe the field frame.  At a genuine
12002-node graph the count region was off-viewport, so the paint half of that
requirement landed where no operator could read it.

THREE INDEPENDENT CAUSES, each alone sufficient, measured during `Inc-4c`'s F-2
and re-measured here before anything was changed: `#map-minimap` was
`height: auto` over the root's 4001 children (471 rows at 118x34, 712 at 80x24),
the pagination meter priced one glyph per node (12002 cells), and the strip
holding them WRAPPED rather than clipping.  The remedy bounds all three.

THE PREDICATE IS THAT THE COUNT IS READABLE IN ITS OWN REGION, clipped out of
the composited frame -- not that the region is on-viewport, and not that the
words appear somewhere on the frame.  All three are different claims, and this
module has now been wrong about two of them:

  * measuring the REGION's height: pre-fix at 118x34 `#map-pagination` reported
    TEN visible rows while the count itself sat off-screen, because
    `_pagination_text` appends the count AFTER the meter;
  * measuring the WHOLE FRAME: unsound in both directions -- a false GREEN at
    50x34 where the region is clipped and `HintLine` carries the same words, and
    a false RED at 60x34 where a raw join glued a wrapped phrase together.

A region's visibility is not its content's visibility, and neither is some other
widget's content.  Measure what the operator reads, in the place the requirement
names.
"""
from __future__ import annotations

import re

import pytest

from mapper.app import (
    COUNT_REGION_ID,
    MAX_RENDER_NODES,
    MapperApp,
    MapScreen,
    SEARCH_COUNT_SUBJECT,
    SEARCH_SUSPENDED_NOTICE,
)
from mapper.model import Edge, Ficha, Graph, Node
from mapper.search import SearchIndex
from tests.inc3_support import open_map, rows_in

# The two declared regimes: the batch's context of use, and `run_test`'s default
# where the rail auto-hides.  A collapse that is fixed at one and not the other
# is not fixed.
SIZES = [(118, 34), (80, 24)]

# The strips' declared ceiling, read from the stylesheet's intent.  Asserted as
# a bound rather than an equality: `max-height` is a CEILING and the ordinary
# map must be free to use fewer rows -- which is the whole difference between
# this and the first draft of the rule (see `test_the_ceiling_is_not_a_floor`).
STRIP_CEILING = 3


def branchy_graph(branches: int, total: int, title_cells: int = 0) -> Graph:
    """A graph whose ROOT FANOUT is the thing that drove the minimap's height.

    The collapse is not a function of node count alone: `#map-minimap` renders
    one entry per top-level branch, so the fanout is the variable that matters
    to it, while the meter is priced on the total.  Both are parameters here so
    an arm can drive either cause on its own.
    """
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="Raiz del mapa", meta="meta")))
    kids = []
    for i in range(branches):
        nid = f"c{i}"
        title = f"rama {i}"
        if title_cells:
            title = (title + " " + "x" * title_cells)[:title_cells]
        g.add_node(Node(id=nid, ficha=Ficha(title=title)))
        g.add_edge(Edge("root", nid))
        kids.append(nid)
    n = 1 + branches
    i = 0
    while n < total:
        nid = f"d{n}"
        g.add_node(Node(id=nid, ficha=Ficha(title=f"hoja {n}")))
        g.add_edge(Edge(kids[i % len(kids)], nid))
        n += 1
        i += 1
    return g


async def _regions(screen):
    return {
        wid: screen.query_one(wid).region
        for wid in ("#map-canvas", "#map-minimap", "#map-pagination")
    }


@pytest.mark.slow
@pytest.mark.parametrize("size", SIZES, ids=lambda s: f"{s[0]}x{s[1]}")
@pytest.mark.asyncio
async def test_at_llr_n07_3_4_the_count_is_READABLE_at_the_shipped_bound(tmp_path, size):
    """`AT` for predicate 1, at the SHIPPED bound rather than a moved one.

    `slow`-marked for the same reason the depth-5000 acceptance is: building and
    rendering a genuine 12002-node graph costs ~13 s per size, and the batch runs
    the marked lane at every gate anyway.  The bound is NOT lowered here -- that
    is the entire point of the arm, and the fast structural bounds below are a
    complement to it, never a substitute.

    THE COUNT IS DERIVED, NOT SPELLED.  `SEARCH_COUNT_SUBJECT` and
    `SEARCH_SUSPENDED_NOTICE` are the module's single declarations of these
    strings, so this arm is a derivation of the shipped text rather than a second
    copy that drifts from it.  A bare query echo would NOT discriminate: the
    fixture's titles are `rama N`, so searching `rama` puts the query's letters
    on the canvas whether or not the count region is readable at all.
    """
    graph = branchy_graph(branches=4001, total=MAX_RENDER_NODES + 2)
    assert len(graph.nodes) > MAX_RENDER_NODES, "the arm must sit ABOVE the bound"

    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        app.store.save("big", graph)
        screen = await open_map(app, pilot, "big")
        await pilot.pause()

        await pilot.press("/")
        await pilot.pause()
        for ch in "rama":
            await pilot.press(ch)
        await pilot.press("enter")
        await pilot.pause()

        # THE COUNT REGION, NOT THE WHOLE FRAME.  The first revision of this arm
        # joined every row of the composited frame, and it was unsound in BOTH
        # directions -- measured by the independent review, not anticipated:
        #
        #   * FALSE GREEN at 50x34: the count region's own rows are clipped, and
        #     the arm passed anyway because `HintLine`, a DIFFERENT widget,
        #     carries the same words.  Predicate 1 is region-scoped; the arm was
        #     not, so it certified a region it never looked at.
        #   * FALSE RED at 60x34: the count is readable across a wrap inside the
        #     region, and the raw join glued `...en el` + padding + `mapa...`.
        #
        # And a mutant that dropped the notice from the count region left all
        # six arms green -- killed only by pre-existing arms that reach the
        # branch by LOWERING the bound, which is the moved bound this increment
        # exists to stop relying on.
        #
        # `rows_in` clips the frame to the region, and whitespace is collapsed
        # AFTER the join because a region-clipped row carries its own right-pad.
        # Both are the idiom `test_search.py` already established.
        region = screen.query_one(f"#{COUNT_REGION_ID}").region
        rows = rows_in(screen, region)
        assert rows, f"the count region is off-viewport at {size}"
        painted = " ".join(" ".join(rows).split())

        assert SEARCH_COUNT_SUBJECT in painted, (
            f"at {size} the search count is not readable IN THE COUNT REGION; "
            "the region is on the frame but the count is not"
        )
        assert SEARCH_SUSPENDED_NOTICE in painted, (
            f"at {size} the suspension notice is not readable in the count "
            "region -- the load-bearing half of the declaration"
        )
        # THE QUERY CLAUSE. Predicate 1 asks for the query, the count AND the
        # notice; the first revision asserted two of three and argued the
        # omission on whole-frame grounds that region-scoping removed. A mutant
        # dropping the echo reddened four arms elsewhere and ZERO here.
        # Discriminating inside the region because the region holds no titles --
        # on the frame it would not be, since the fixture's titles are `rama N`.
        assert "«" + "rama" + "»" in painted, (
            f"at {size} the count region does not name the query it counted"
        )
        # THE NUMERIC CLAUSE, which the first revision omitted entirely.  The
        # threshold is `== len(SearchIndex(graph).query(q))`, and the tally is
        # DERIVED from the same owner the screen resolves through rather than
        # recomputed by a second definition of "what matches".
        tally = len(SearchIndex(graph).query("rama"))
        assert f"{tally} {SEARCH_COUNT_SUBJECT}" in painted, (
            f"at {size} the region does not carry the whole-graph tally "
            f"{tally}; a count region that names a different number than the "
            "search resolved is the two-owners defect this batch closed"
        )


@pytest.mark.parametrize("size", SIZES, ids=lambda s: f"{s[0]}x{s[1]}")
@pytest.mark.asyncio
async def test_the_strips_cannot_outgrow_their_ceiling(tmp_path, size):
    """The bound, driven by FANOUT at a node count the default lane can afford.

    The minimap's height is a function of the root's branch count, so this
    reaches the same cause as the slow arm without paying for 12002 nodes.  If
    this ever passes while the slow arm fails, the difference is the meter or the
    total, and the two arms together say which.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        app.store.save("wide", branchy_graph(branches=600, total=900))
        screen = await open_map(app, pilot, "wide")
        await pilot.pause()

        regions = await _regions(screen)
        for wid in ("#map-minimap", "#map-pagination"):
            assert regions[wid].height <= STRIP_CEILING, (
                f"{wid} is {regions[wid].height} rows at {size}; the stylesheet "
                f"bounds it at {STRIP_CEILING}. An unbounded strip decides the "
                "layout, which is how the canvas was crushed to one row"
            )
        assert regions["#map-canvas"].height > 1, (
            f"the canvas is {regions['#map-canvas'].height} row(s) at {size}; a "
            "strip has taken the frame again"
        )


@pytest.mark.asyncio
async def test_the_ceiling_is_not_a_floor(tmp_path):
    """`max-height`, not `height` -- and this arm exists because I got it wrong.

    The first draft of the stylesheet rule wrote `height: 3`, which fixed the
    collapse and then charged EVERY map two rows it never needed: `legacy` has
    eight branches and wants a ONE-row minimap, so at a 35x14 terminal the canvas
    fell to a single row and the coverage declaration degraded to nothing. Three
    arms in `test_overflow.py` caught it.

    MEASURED AT A WIDE TERMINAL, and the first draft of THIS arm got that wrong
    too: it drove 35 columns, where even a three-branch minimap wraps to the full
    three rows because the legend alone needs the width. The strip was at its
    ceiling for an honest reason and the arm read it as the defect. A ceiling is
    only distinguishable from a floor where the content is genuinely SHORT, so
    the width has to be one where it is.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("small", branchy_graph(branches=3, total=8))
        screen = await open_map(app, pilot, "small")
        await pilot.pause()

        regions = await _regions(screen)
        assert regions["#map-minimap"].height < STRIP_CEILING, (
            "a small map's minimap is using the full ceiling at 118 columns, "
            "where its content fits in one row; `max-height` has become "
            "`height` and every small map is paying for the large one"
        )


@pytest.mark.asyncio
async def test_a_small_map_at_a_small_terminal_keeps_its_canvas(tmp_path):
    """The regression `max-height` was chosen to prevent, at the size that showed it.

    Separate from the arm above because the two claims are observable at
    DIFFERENT sizes: the ceiling-is-not-a-floor property needs a width where the
    strip's content is short, and this one needs the cramped terminal where the
    tax actually bit. Asserting both in one arm is what made the first draft
    drive 35 columns and read an honest 3-row strip as a defect.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=(35, 14)) as pilot:
        await pilot.pause()
        app.store.save("small", branchy_graph(branches=3, total=8))
        screen = await open_map(app, pilot, "small")
        await pilot.pause()

        regions = await _regions(screen)
        assert regions["#map-canvas"].height > 1, (
            f"the canvas is {regions['#map-canvas'].height} row(s) on a small "
            "map at a small terminal -- the regression `max-height` prevents"
        )


@pytest.mark.parametrize("size", SIZES, ids=lambda s: f"{s[0]}x{s[1]}")
@pytest.mark.asyncio
async def test_the_declaration_and_the_legend_survive_the_clip(tmp_path, size):
    """`F1`/`F2` — the clip must not eat what the increment added.

    Both reviews found this from opposite sides: the declaration and the legend
    were appended LAST, so at ordinary file-chosen title lengths the clip ate
    them while the strip still reported its full three rows. The 24-branch case
    was the sharper one -- nothing "missing" by the increment's own accounting,
    and the operator reading four coverage glyphs with no key.

    SIXTY CELLS IS NOT A PATHOLOGICAL TITLE, it is a sentence. The old arm could
    not see any of this because it measured `region.height`, which was 3
    throughout -- the region's visibility is not its content's visibility, one
    strip to the left of where this module already says so.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        app.store.save("wide", branchy_graph(branches=40, total=60, title_cells=60))
        screen = await open_map(app, pilot, "wide")
        await pilot.pause()

        strip = screen.query_one("#map-minimap")
        painted = " ".join(" ".join(rows_in(screen, strip.region)).split())

        assert "ramas sin mostrar" in painted, (
            f"at {size} the remainder declaration is not on the frame; the "
            "strip declares nothing while claiming to declare the remainder"
        )
        assert "sin datos" in painted, (
            f"at {size} the coverage legend is not on the frame; the operator "
            "reads the glyphs with no key, on a strip that reports full height"
        )


@pytest.mark.asyncio
async def test_the_CELL_BUDGET_is_the_bound_that_binds(tmp_path):
    """`F3` — the bound shipped with no oracle, and this is it.

    Both reviews measured that setting `MINIMAP_BRANCHES` to `10**9` left the
    whole suite green: the CSS clip alone satisfied every predicate, so neither
    Python bound was observed by anything.

    THE ANSWER TURNED OUT TO BE SHARPER THAN A MISSING ARM. Re-fired after the
    cell budget landed, that mutant STILL survived -- because
    `min(24, budget // per_entry)` is decided by the BUDGET at every width below
    roughly 162 columns, so the count ceiling had no work left. It was removed
    rather than given a test it could only pass vacuously, and this arm now
    drives the bound that actually binds.

    The assertion is a DERIVATION: the strip must declare exactly the remainder
    the screen's own budget implies, so a change to the budget's arithmetic --
    the reserve, the per-entry cost, the row ceiling -- moves the expected
    number with it and cannot pass by coincidence.
    """
    branches = 400
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("many", branchy_graph(branches=branches, total=branches + 40))
        screen = await open_map(app, pilot, "many")
        await pilot.pause()

        strip = screen.query_one("#map-minimap")
        painted = " ".join(" ".join(rows_in(screen, strip.region)).split())

        # A CONSERVATION LAW, not a re-read of the budget.  The first version of
        # this arm asked `_minimap_entry_limit` what it expected and then
        # asserted the strip declared that -- so a mutant that changed the
        # budget's arithmetic moved BOTH sides and survived.  That is
        # reader-as-oracle: the expected value came out of the artifact under
        # verification.  It is the illegal twin of deriving a test's DOMAIN from
        # its own fixture, which is legal, and this module gets to hold both.
        #
        # What is asserted instead is a property no arithmetic can satisfy by
        # coincidence: every branch is either DRAWN or DECLARED, never neither.
        # A budget that drops entries without counting them, or declares a
        # remainder it did not drop, breaks this whatever its constants say.
        drawn = len(re.findall(r"rama \d+", painted))
        declared = re.search(r"\+(\d+) ramas sin mostrar", painted)
        assert declared, (
            "the strip drops branches and declares no remainder; every branch "
            "must be drawn or declared"
        )
        assert 0 < drawn < branches, (
            f"the strip painted {drawn} of {branches} entries; the budget must "
            "bound the map without emptying the strip"
        )
        assert drawn + int(declared.group(1)) == branches, (
            f"{drawn} drawn + {declared.group(1)} declared != {branches} "
            "branches; the strip lost some without saying so"
        )


def test_the_row_ceiling_is_spelled_once():
    """`MINIMAP_ROWS` and the stylesheet must agree, and nothing else checks it.

    Two spellings of one number is how they drift -- this batch's own longest
    lesson. The Python budget reserves rows against `MINIMAP_ROWS`; the clip is
    enforced by `max-height` in the CSS. If they disagree the budget is computed
    against a ceiling that is not the one applied, and the failure is silent.
    """
    import re

    rule = re.search(r"#map-minimap\s*\{[^}]*max-height:\s*(\d+)", MapperApp.CSS)
    assert rule, "the `#map-minimap` max-height rule is gone; the clip is the bound"
    assert int(rule.group(1)) == MapScreen.MINIMAP_ROWS, (
        f"the stylesheet clips at {rule.group(1)} rows and the budget reserves "
        f"against {MapScreen.MINIMAP_ROWS}; the two spellings have drifted"
    )


@pytest.mark.asyncio
async def test_a_small_map_declares_NOTHING_because_it_drops_nothing(tmp_path):
    """`H1` — the reserve must not manufacture the omission it announces.

    This arm exists because the confirmation pass found the increment had made
    a SHIPPED map worse. `_minimap_entry_limit` reserved the declaration's cells
    unconditionally, so at 35x14 a three-branch map drew ONE branch and declared
    `+2 ramas sin mostrar` -- where the pre-increment strip drew all three, and
    the strip's height and the canvas's height were IDENTICAL either way. The
    two dropped branches bought nothing.

    It is this increment's own `height: 3` mistake in a second costume: taxing
    the ordinary map to bound the pathological one. And the conservation law
    could not see it -- `1 drawn + 2 declared == 3` is perfectly conserved --
    which is why a bound needs an arm on BOTH sides: one that reddens when the
    strip keeps too much, and this one, which reddens when it drops what it did
    not need to.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=(35, 14)) as pilot:
        await pilot.pause()
        app.store.save("small", branchy_graph(branches=3, total=8))
        screen = await open_map(app, pilot, "small")
        await pilot.pause()

        strip = screen.query_one("#map-minimap")
        painted = " ".join(" ".join(rows_in(screen, strip.region)).split())
        assert "ramas sin mostrar" not in painted, (
            "a three-branch map declares a remainder it did not need to drop; "
            "the declaration's reserve is being charged when there is nothing "
            "to declare"
        )
        assert len(re.findall(r"rama \d+", painted)) == 3, (
            "the strip dropped branches on a map small enough to draw them all"
        )
