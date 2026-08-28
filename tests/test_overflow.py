"""HLR-N06.3 — nothing is hidden without being declared, and it reconciles.

`TC-034` .. `TC-038`, `AT-015`, `AT-016`.  Every acceptance here is ONE on-disk
node driving one whole chain (C-18): "covered by the combination of X and Y" is
an unrealized claim, not a coverage argument.
"""
from __future__ import annotations

import re

import pytest
from rich.color import EIGHT_BIT_PALETTE, Color, ColorSystem

from tests.inc3_support import (
    rows_in,
    canvas_rows,
    hidden_under,
    height_offset,
    install,
    naive_hidden_sum,
    open_map,
    oracle_traced,
)
from mapper import darkside
# `MapScreen` is no longer imported: every reference to it was
# `MapScreen.HEADER_ROWS`, and that constant is gone -- the header's height is
# now MEASURED per call by `layered.header_rows`, which this module imports
# instead and pins directly against the rendered line.
from mapper.app import MapperApp
from mapper.model import Graph
from mapper.views.layered import (
    FOLD_PILL_TOKEN,
    OVERFLOW_TOKEN,
    LayeredRenderer,
    header_rows,
    painted_ids,
)
from mapper.views.state import ViewState
# The balanced builder, imported rather than re-typed: `HEADER_ROWS` now has to
# be measured over node count, and a second copy of a graph builder is a copy
# that drifts.
from tests.test_repair_depth import _balanced

# The four configurations `HLR-N06.3` pins, plus two this increment ADDS and the
# reason it adds them, which is a correction to `A-98` rather than belt-and-
# braces.  `A-98` states that `(30, 6)` discriminates the dropped-column mutant
# `MUT-B`.  Re-measured on `legacy` at all four pinned rows, it does NOT: at
# `(30, 6)` the ROW bound alone already excludes every node but `erp`, so the
# column bound cannot change the answer and `MUT-B` is green on all four.  The
# column bound first bites at `(30, 12)`, where three rows of cards are on
# screen and the two right-hand ones are past the right edge.  Dropping either
# extra row lets `MUT-B` ship.
#
# The fourth component is the PAN, and it is the row the acceptance was missing
# entirely.  `02j`'s risk row 5 says `painted_ids` must consume the same pan
# offsets `render` does, or the declared set is correct only for a canvas that
# has never moved -- and every configuration here used to be un-panned, so a
# future edit to `geo.place` would have been caught by no acceptance arm.  The
# offsets are chosen where `legacy` has live travel in BOTH axes (measured at
# 30x12: `max_pan_x = 17`, `max_pan_y = 2`), and `_drive` asserts the pan it
# achieved rather than the pan it asked for.
PINNED_CONFIGURATIONS = (
    (50, 12, (), (0, 0)),          # nothing hidden
    (50, 12, ("erp",), (0, 0)),    # hidden by fold only
    (30, 6, (), (0, 0)),           # hidden by viewport only
    (30, 6, ("erp",), (0, 0)),     # hidden by both
)
ADDED_CONFIGURATIONS = (
    (30, 12, (), (0, 0)),          # where the COLUMN bound is live — reddens MUT-B
    (30, 12, ("erp",), (0, 0)),
    (30, 12, (), (8, 2)),          # hidden by a PANNED viewport — both axes live
)
CONFIGURATIONS = PINNED_CONFIGURATIONS + ADDED_CONFIGURATIONS

# The header wraps, so a per-row regex either misses the numeral or binds it to
# the wrong label (QA-N-06).  The rows are joined before this is applied.
_DECLARED = re.compile(
    re.escape(OVERFLOW_TOKEN) + r"\s*(\d+)\s+fuera\s+de\s+vista"
)
_PILL = re.compile(re.escape(FOLD_PILL_TOKEN) + r".*?\+(\d+)")


def _declared_total(rows: list[str]) -> int | None:
    """Parse the indicator's numeral out of the painted canvas.

    Rows are JOINED first: at 100x30 the header renders as two rows with the
    count numeral on one and its label on the next.

    AND THE WHITESPACE BETWEEN THE WORDS IS `\\s+`, NOT A LITERAL SPACE, which
    is the difference between reading the frame and reading a frame that happens
    not to have wrapped.  A row is padded to the region width, so joining two
    rows puts the padding INSIDE the sentence: at a 30-column pagination strip
    the declaration paints as `... fuera de ` / `vista ...` and the joined text
    carries two spaces.  With a literal space this helper returned `None` on a
    strip that was declaring the right number all along -- i.e. it reported the
    requirement's unwanted behaviour on correct output, which would have been
    read as a defect in the product rather than in the parse.
    """
    match = _DECLARED.search(" ".join(rows))
    return int(match.group(1)) if match else None


async def _drive(tmp_path, w, h, folded, pan=(0, 0)):
    """Mount `MapScreen` so the renderer receives EXACTLY `(w, h)`, and prove it.

    The terminal height is derived from a measured offset rather than typed, and
    the achieved configuration is asserted -- so a screen that silently rendered
    at some other size fails here instead of quietly answering a question nobody
    asked.  THE PAN IS ASSERTED THE SAME WAY: `refresh_canvas` re-clamps into
    the legal range, so a row asking for travel the layout does not have would
    otherwise run un-panned while looking like it exercised pan.
    """
    install(tmp_path, "legacy")
    offset = await height_offset(tmp_path, "legacy", w)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(w, h + offset)) as pilot:
        await pilot.pause()
        screen = await open_map(app, pilot, "legacy")
        # THE FIXTURE IS ASSERTED, not assumed.  Without the `install` above,
        # `MapScreen` catches the load failure and mounts a ONE-NODE graph
        # titled "error" -- on which every predicate below is trivially green.
        # Measured: this arm was passing on that graph until the sibling
        # `TC-038` arm's own vacuity guard exposed it.
        assert sorted(screen.graph.nodes) == [
            "alm", "cont", "erp", "fin", "inv", "nom", "pres", "rrhh"
        ], sorted(screen.graph.nodes)
        screen.folded = frozenset(folded)
        screen.pan_x, screen.pan_y = pan
        screen.refresh_canvas()
        await pilot.pause()
        achieved = screen._canvas_size()  # noqa: SLF001
        assert achieved == (w, h), (
            f"asked for renderer size {(w, h)} and got {achieved}; the "
            f"configuration under test is not the one the table names"
        )
        assert (screen.pan_x, screen.pan_y) == pan, (
            f"asked for pan {pan} and the clamp left {(screen.pan_x, screen.pan_y)}; "
            f"this row does not exercise the pan it names"
        )
        rows = canvas_rows(screen)
        declared = painted_ids(screen.graph, screen._view_state(w, h))  # noqa: SLF001
        traced = oracle_traced(screen.graph, folded, w, rows, pan_x=screen.pan_x)
        return screen, rows, declared, traced


# --------------------------------------------------------------------------
# LLR-N06.3.1 — one set difference, never a sum


def test_tc_034_the_unpainted_set_is_a_difference_not_a_sum(tmp_path):
    """The `anidado` fixture's whole reason for existing.

    `FOLD = {ops, log}` with `log` nested INSIDE the folded `ops`: the naive rule
    contributes `log -> [alm, flo]` and `ops -> [alm, comp, flo, log]` and
    declares 6, while the graph only hides 4.  It double-counts exactly `alm`
    and `flo`, inflation 2 — a number that cannot be right and that no
    non-overlapping fixture can catch.

    `legacy` is PROVABLY unfalsifiable here: over all 7 of its non-empty fold
    configurations the two rules never disagree, which the sibling arm below
    executes rather than asserts.
    """
    graph = install(tmp_path, "anidado")
    assert len(graph.nodes) == 7, "the fixture did not round-trip through MapStore"
    folded = frozenset({"ops", "log"})

    hidden = hidden_under(graph, folded)
    assert sorted(hidden) == ["alm", "comp", "flo", "log"]
    assert len(hidden) == 4
    assert naive_hidden_sum(graph, folded) == 6
    assert naive_hidden_sum(graph, folded) != len(hidden), (
        "the two rules agree on this fixture, so the acceptance cannot fail"
    )

    # And the product computes the difference, not the sum.
    state = ViewState(w=140, h=45, folded=folded)
    unpainted = frozenset(graph.nodes) - painted_ids(graph, state)
    assert unpainted == hidden
    assert len(unpainted) < naive_hidden_sum(graph, folded)


def test_tc_035_the_positive_control_a_fold_where_naive_equals_painted(tmp_path):
    """PDR `#D11`. Without this the negative control is green by construction.

    A probe that can only ever report "the naive rule is wrong" is not measuring
    the rule, it is asserting a conclusion.  `FOLD = {log}` on the SAME fixture
    has no nesting, so the two rules agree — and the same instrument that
    returned 6 != 4 above returns 2 == 2 here.
    """
    graph = install(tmp_path, "anidado")
    folded = frozenset({"log"})

    hidden = hidden_under(graph, folded)
    assert sorted(hidden) == ["alm", "flo"]
    assert naive_hidden_sum(graph, folded) == len(hidden) == 2, (
        "the positive control does not reproduce: the instrument cannot return "
        "the other answer, so its negative verdict proves nothing"
    )
    state = ViewState(w=140, h=45, folded=folded)
    assert frozenset(graph.nodes) - painted_ids(graph, state) == hidden


def test_tc_036_the_legacy_fixture_cannot_falsify_this_llr(tmp_path):
    """Executed exhaustively, because `02a` argued it and `M-6` quoted 3 rows.

    All 7 non-empty fold configurations of `legacy`: **0** where the naive sum
    differs from the true hidden union.  An acceptance that ran only on `legacy`
    could not fail, whatever the implementation did — which is why `anidado`
    is a gate condition and not a nicety.
    """
    graph = install(tmp_path, "legacy")
    # The root is excluded, and that exclusion is the requirement's own framing:
    # its sole nesting candidate IS the root, and folding a whole map away is
    # "a degenerate case, not the story's".  Derived, not typed.
    internal = sorted(
        {edge.parent_id for edge in graph.edges} - {graph.root_id}
    )
    assert internal, "no foldable branch derived; the sweep would be vacuous"

    def sweep(branches):
        agree = disagree = 0
        for mask in range(1, 1 << len(branches)):
            folded = frozenset(
                nid for i, nid in enumerate(branches) if mask >> i & 1
            )
            if naive_hidden_sum(graph, folded) == len(hidden_under(graph, folded)):
                agree += 1
            else:
                disagree += 1
        return agree, disagree

    agree, disagree = sweep(internal)
    assert agree + disagree == 7, (agree, disagree)
    assert disagree == 0, (
        "legacy would falsify this LLR after all; the anidado fixture's whole "
        "argument rests on it not being able to"
    )
    # POSITIVE CONTROL for the sweep itself: the same instrument DOES find
    # disagreements once the root is admitted (folding `erp` and a child
    # double-counts that child's descendants), so a 0 above is a measurement
    # and not an instrument that can only ever answer 0.
    _agree_all, disagree_all = sweep(sorted({e.parent_id for e in graph.edges}))
    assert disagree_all > 0


# --------------------------------------------------------------------------
# LLR-N06.3.3 — the zero case, and LLR-N06.3.1's header-row measurement


def test_tc_037_no_indicator_while_every_node_is_painted(tmp_path):
    """LLR-N06.3.3 — 0 occurrences of the leading token.

    An indicator permanently reading zero trains the operator to ignore it,
    which is the same failure as not having one.  Driven on the 6-node M-1 shape
    at 140x45, where the canvas is wide enough that nothing is hidden — the
    positive control being the sibling arm, which finds the token when it should.
    """
    graph = install(tmp_path, "legacy")
    state = ViewState(w=140, h=45)
    assert painted_ids(graph, state) == frozenset(graph.nodes), (
        "nothing is hidden at this size, or the arm below is vacuous"
    )
    painted = LayeredRenderer().render(graph, state).plain
    assert OVERFLOW_TOKEN not in painted

    # The control: the same token IS painted where nodes really are hidden.
    tight = ViewState(w=140, h=8)
    assert painted_ids(graph, tight) != frozenset(graph.nodes)
    assert OVERFLOW_TOKEN in LayeredRenderer().render(graph, tight).plain


def _header_rows_in_frame(screen) -> int | None:
    """Rows the header's first LOGICAL line occupies IN THE COMPOSITED FRAME.

    THE INSTRUMENT, AND IT IS DELIBERATELY NOT THE PRODUCT'S.  The pin this
    serves used to compute `-(-len(header) // (w - 2))` — `header_rows`'s own
    arithmetic, re-typed — and call the result a measurement.  Two sides that
    share a formula cannot disagree about it: that helper could not fail on a
    wrong divisor (both used `w - 2`), on word-wrap (neither wrapped) or on a
    wide character (both used `len`).  Swapping only the helper for a real
    render, product untouched, reddened 27 of the 520 cells it was declaring
    green.  That is the same discipline failure that produced `B-61` — a formula
    asserted rather than measured — relocated into the arm that was supposed to
    catch it.

    So this reads the rows Textual actually PAINTED into the canvas region and
    asks how many of them the header consumed.  It goes through the compositor,
    so it fails on a wrong divisor, on word-wrap and on a wide character alike.
    Rows are re-joined and their whitespace collapsed because a wrap breaks the
    line at a space and pads what is left of the row.

    `None` when the region is SHORTER than the wrapped header: the frame has
    clipped the evidence and there is nothing left to measure.  Reported by the
    caller rather than skipped, so a sweep cannot go green by becoming blind.
    """
    w, h = screen._canvas_size()  # noqa: SLF001
    line = screen._current_renderer().render(  # noqa: SLF001
        screen.graph, screen._view_state(w, h)  # noqa: SLF001
    ).plain.split("\n")[0]
    target = re.sub(r"\s+", " ", line).strip()
    rows = canvas_rows(screen)
    for k in range(1, len(rows) + 1):
        for joiner in (" ", ""):
            if re.sub(r"\s+", " ", joiner.join(rows[:k])).strip() == target:
                return k
    return None


# Contiguous across the whole `B-61` band at a height that leaves the region
# tall enough to hold the header, plus the sizes the carry and the reviews
# named by transcript.  The unit is the TERMINAL, and the canvas region is
# derived from it by the real layout — which is the entire point of driving the
# app instead of the renderer.
_HEADER_TERMS = tuple((w, 30) for w in range(20, 41)) + (
    (28, 17), (30, 20), (31, 16), (50, 20), (80, 24), (140, 45),
)


@pytest.mark.asyncio
@pytest.mark.parametrize("map_id", ("legacy", "anidado"))
async def test_llr_n06_3_1_the_charged_header_height_is_the_composited_one(
    tmp_path, map_id
):
    """`header_rows` replaces `HEADER_ROWS = 2`, pinned against the FRAME.

    THE CONSTANT WAS NOT A MEASUREMENT, it was one fixture's number at one width
    band.  Both of the header's paddings are clamped at 0, so below `avail = 48`
    the line is a fixed core plus the `▽ N` declaration — 55 cells on `legacy`
    at every narrow width — and that wraps to three physical rows across the
    band and four at the floor, where `_canvas_size` floors `w` at 20.

    AND THE REPLACEMENT WAS NOT A MEASUREMENT EITHER, until this round.  It
    charged `ceil(len / (w - 2))`, which is not the wrap the widget performs:
    Rich WORD-WRAPS, so a line `ceil` prices at 2 rows can occupy 3.  Measured
    over a 943-configuration terminal sweep on `legacy`, the arithmetic charge
    was short of the real wrap at 23 of them — under-charging, which is `B-61`.
    So the product renders the line, and this arm measures the answer OFF THE
    COMPOSITED FRAME rather than re-deriving it.

    EQUALITY, NOT AN INEQUALITY, AND THAT IS THE UPGRADE.  The previous pin
    asserted only `charged >= measured`, because wrapping everything at `w - 2`
    over-charged wherever the region was actually `w` wide.  It is: measured
    here, `#map-canvas` carries no padding and no border — asserted below rather
    than read off the stylesheet — so its content width is its REGION width,
    which is `_canvas_width()` at 724 of the 943 configurations and
    `_canvas_width() - 2` at the other 219.  The screen now passes the measured
    width, and the charge matches the frame exactly at every configuration the
    frame can show, on both fixtures.  Equality is worth having because an
    over-charge is not free: at a short region it costs the operator the only
    body row there was.

    THE SHORT REGIONS ARE COUNTED, NOT SKIPPED.  Where the region is shorter
    than the wrapped header the frame has clipped the evidence, so there is no
    measurement to compare against — and the charge cannot be observed there
    either, because `_canvas_size` takes the same short-region branch whatever
    it is.  Those are counted and the count is bounded, so this arm cannot pass
    by having gone blind.
    """
    install(tmp_path, map_id)
    checked, clipped, seen = 0, 0, set()
    for term in _HEADER_TERMS:
        app = MapperApp(tmp_path)
        async with app.run_test(size=term) as pilot:
            await pilot.pause()
            screen = await open_map(app, pilot, map_id)
            for _ in range(3):
                await pilot.pause()
            canvas = screen.query_one("#map-canvas")
            # NO PADDING AND NO BORDER, asserted.  This is the fact the old
            # divisor rationale got wrong, and it is cheaper to pin than to
            # re-read `#map-canvas`'s rules every time the stylesheet moves.
            assert canvas.content_size.width == canvas.region.width, (
                f"{term}: content width {canvas.content_size.width} is not the "
                f"region width {canvas.region.width}; `#map-canvas` has grown "
                f"padding or a border and the wrap width is no longer the region"
            )
            charged = screen._header_rows(canvas.content_size.width)  # noqa: SLF001
            _w, h = screen._canvas_size()  # noqa: SLF001
            measured = _header_rows_in_frame(screen)
            if measured is None:
                assert canvas.region.height <= charged, (
                    f"{term}: the frame could not show the header in a region "
                    f"{canvas.region.height} rows tall against a charge of "
                    f"{charged} -- the header is wider than the charge admits"
                )
                clipped += 1
                continue
            assert charged == measured, (
                f"{map_id} {term}: charged {charged} physical header rows "
                f"against {measured} in the composited frame (region "
                f"{canvas.region.width}x{canvas.region.height})"
            )
            # AND THE SCREEN CONSUMED THE SAME NUMBER.  Pinning `header_rows`
            # alone leaves the WIRING free: `_canvas_size` could hand it a
            # guessed width and this arm would never know, because it asks the
            # helper itself.  Measured -- a mutant passing `w - 2` there
            # survived the equality above and dies here.  `render` emits
            # `1 + (h - 1)` logical lines and the frame spends `measured`
            # physical rows on the first, so the body budget `row_limit = h - 1`
            # is exactly what the frame left.
            if canvas.region.height > measured:
                assert h - 1 == canvas.region.height - measured, (
                    f"{map_id} {term}: `_canvas_size` gave the renderer "
                    f"row_limit {h - 1} into the {canvas.region.height - measured} "
                    f"body rows the frame actually left (region height "
                    f"{canvas.region.height}, header {measured})"
                )
            else:
                assert h == 1, (
                    f"{map_id} {term}: the header fills the region, so no body "
                    f"row is paintable and h must be 1; got {h}"
                )
            checked += 1
            seen.add(measured)

    # NON-VACUOUS ON BOTH AXES: most configurations really were measured, and
    # the band really does contain headers taller than the two rows the deleted
    # constant assumed.  Without this, a change that clipped every region would
    # leave the arm green on nothing.
    assert clipped <= len(_HEADER_TERMS) // 3, (
        f"{clipped} of {len(_HEADER_TERMS)} configurations clipped the header; "
        "this arm has gone blind"
    )
    assert checked >= 2 * len(_HEADER_TERMS) // 3, checked
    assert {2, 3} <= seen, sorted(seen)


def test_llr_n06_3_1_the_charge_band_over_node_count_and_width(tmp_path):
    """The SHAPE of the charge across `(n, w, wrap_w)` — a characterization.

    THIS ARM DOES NOT VERIFY THE CHARGE, and saying so is the point.  Its
    predecessor claimed to, by comparing `header_rows` against a re-typed copy
    of `header_rows`; the verification now lives one arm up, against the
    composited frame, where the two sides do not share a computation.  What a
    grid buys that the frame cannot is REACH: `_balanced(11999)` sits just under
    `MAX_RENDER_NODES` and no terminal can composite it, so the node-count axis
    is only visible here.

    THE GRID IS DENSE ON BOTH AXES ON PURPOSE.  The pin this line descends from
    sampled `n` at 8, 10, 40, 100, 1000 and `w` at 20, 30, 50, …, and recorded
    its own sample gaps as facts: "3 rows at w=30 from n>=40" (the true
    threshold is a WIDTH shift, visible only because the grid jumped 10→40) and
    "w <= 30" (the band reaches 34 near `MAX_RENDER_NODES`, invisible because
    the grid jumped 30→50).  Every bound below is DERIVED from the grid.

    `wrap_w` IS SWEPT OVER BOTH MEASURED VALUES, `w` and `w - 2`, because those
    are the two the canvas region actually takes — 724 and 219 of 943
    configurations respectively — and a grid that fixed it at one of them would
    be pinning half the product.
    """
    graph = install(tmp_path, "legacy")

    grid = []
    for n in (8, 10, 11, 13, 14, 20, 39, 40, 100, 1000):
        probe = graph if n == 8 else _balanced(n)
        for w in list(range(20, 41)) + [50, 58, 80, 140, 300]:
            for wrap in (w, w - 2):    # the two widths the region is measured at
                grid.append((n, w, wrap, header_rows(probe, w, wrap)))
    assert len(grid) == 10 * 26 * 2 == 520, len(grid)

    charged_by_w = {}
    for _n, w, _wrap, charged in grid:
        charged_by_w.setdefault(w, set()).add(charged)

    # THE DELETED CONSTANT IS REFUTED by the same grid, on the record: a charge
    # above 2 exists, so `HEADER_ROWS = 2` was wrong and not merely imprecise.
    assert {c for *_s, c in grid} == {2, 3, 4}, sorted({c for *_s, c in grid})
    assert 3 in charged_by_w[21] and 4 in charged_by_w[20], (
        charged_by_w[20], charged_by_w[21]
    )

    # THE BAND, DERIVED.  `w >= 35` is two rows at every node count the renderer
    # will draw and at both wrap widths; below 23 it is never two.
    assert all(
        charged_by_w[w] == {2}
        for w in (35, 36, 37, 38, 39, 40, 50, 58, 80, 140, 300)
    ), {w: charged_by_w[w] for w in charged_by_w if w >= 35}
    assert all(2 not in charged_by_w[w] for w in range(20, 23)), {
        w: charged_by_w[w] for w in range(20, 23)
    }
    # The node-count axis is real ON ITS OWN, at a width where the small graph
    # is already down to two rows — the half the old grid's 30→50 jump could
    # not see.
    assert charged_by_w[31] == {2, 3}, charged_by_w[31]

    # MONOTONE IN THE WRAP WIDTH: a narrower wrap can only cost more rows.  This
    # is what makes a measured region width safe to trust — if the measurement
    # is ever a little narrow, the charge errs towards over-charging, and
    # over-charging is the direction that keeps `row_limit` honest.
    for n, w, wrap, charged in grid:
        if wrap == w:
            narrow = header_rows(graph if n == 8 else _balanced(n), w, w - 2)
            assert narrow >= charged, (n, w, narrow, charged)

    # AND THE BAND REACHES 34 at the top of the legal node range, which is the
    # bound the oldest pin recorded as `w <= 30`.  Derived, not quoted.
    huge = _balanced(11999)
    assert header_rows(huge, 34, 34) == 3, header_rows(huge, 34, 34)
    assert header_rows(huge, 35, 35) == 2, header_rows(huge, 35, 35)


@pytest.mark.asyncio
async def test_b56_the_declaration_is_right_on_the_first_look_with_no_repaint(tmp_path):
    """`B-56` CLOSED, pinned on the path that used to be wrong — no repaint.

    Every other arm in this module calls `refresh_canvas()` before it measures,
    which is what hid this: `on_mount` paints before the compositor has given
    the canvas its region, so the declaration described a frame that did not
    exist.  Measured, that was not a stale numeral but an ABSENT one -- at
    `legacy` 50x20 and 60x20 the strip said nothing at all while half the map
    was off screen, and `LLR-N06.3.3` makes absence MEAN "nothing is hidden".
    Nor did it heal at the first keypress: at the root `j` is a no-op, so
    nothing repaints, and a reader who only LOOKS at the map never clears it.

    So this arm presses nothing and repaints nothing.  It is green only because
    `on_mount` schedules `_declare_after_layout`.

    BOTH DECLARING SURFACES, WHICH IS `B-60` CLOSED RATHER THAN CARRIED.  The
    carry said the canvas HEADER could still under-declare on the first frame
    while "the strip -- the surface the operator reads -- is correct", and that
    every repaint reconciles them.  Measured at exactly these four sizes, the
    header numeral was ABSENT, not stale, while four nodes were hidden -- and
    `LLR-N06.3.3` makes absence MEAN "nothing is hidden", so the surface with
    the map on it was declaring the opposite of the truth.  Measured over nine
    keys, `j`/`k`/`h`/the arrows/`tab` did not heal it; only `l` and `o` did.
    So the canvas is asserted here beside the strip, on the same first look.

    AND THE SIZE LIST IS NOT THE COVERAGE ARGUMENT — the arm below is.  Four
    sizes closed the four instances this was measured at and left the mechanism
    open one band over; `test_b60_the_declaration_follows_the_region_to_its_settle`
    carries the sizes where it recurred, on both fixtures.
    """
    install(tmp_path, "legacy")
    checked = 0
    for term in ((50, 20), (60, 20), (40, 20), (30, 20)):
        app = MapperApp(tmp_path)
        async with app.run_test(size=term) as pilot:
            await pilot.pause()
            screen = await open_map(app, pilot, "legacy")
            for _ in range(3):
                await pilot.pause()
            assert len(screen.graph.nodes) == 8
            hidden = screen._unpainted_ids()  # noqa: SLF001
            assert hidden, f"{term} hides nothing; this size cannot falsify the arm"
            strip = " ".join(
                rows_in(screen, screen.query_one("#map-pagination").region)
            )
            assert _declared_total([strip]) == len(hidden), (
                f"{term}: the strip declares {_declared_total([strip])} on a "
                f"first look that is hiding {len(hidden)}"
            )
            assert _declared_total(canvas_rows(screen)) == len(hidden), (
                f"{term}: the canvas header declares "
                f"{_declared_total(canvas_rows(screen))} on a first look that "
                f"is hiding {len(hidden)}; `None` here means the numeral is "
                f"ABSENT, which LLR-N06.3.3 makes mean 'nothing is hidden'"
            )
            checked += 1
    assert checked == 4


# The band where the first look diverged AFTER `_declare_after_layout` was
# added, one fixture each side of the slash.  Not a wider sample of the same
# thing: at these sizes `_apply_region_visibility` reflows the body row, so the
# canvas region is still moving when the post-mount callback fires.
_SETTLE_TERMS = {
    "legacy": ((31, 16), (32, 16), (34, 15), (35, 14)),
    "anidado": ((34, 14), (35, 14)),
}


@pytest.mark.asyncio
@pytest.mark.parametrize("map_id", ("legacy", "anidado"))
async def test_b60_the_declaration_follows_the_region_to_its_settle(tmp_path, map_id):
    """`B-60`'s RESIDUAL — the region settles after the callback that declares.

    `_declare_after_layout` fires on the first `call_after_refresh`, and at
    these widths that is too early: `_apply_region_visibility`'s show/hide is
    still reflowing the body row.  Instrumented at (31,16) on `legacy`, the
    passes saw a 31x1 region and then a 29x2 one, so `_canvas_size` took the
    short-region branch, returned `h = 1` and declared nothing painted — and the
    region then SETTLED at 31x3 with nothing left to recompute it.  Both
    declaring surfaces kept a numeral computed for a frame that no longer
    existed: the strip read 8 against a truth of 7.

    A SCREEN RESIZE IS NOT A CANVAS RESIZE, which is why `on_resize` alone does
    not close it.  Traced, the screen's resize arrives BEFORE the row reflows
    and the canvas region moves twice more afterwards without another.  So the
    declaration re-schedules itself while the region keeps changing and stops
    when it does not, and `on_resize` covers the case that had no handler at all
    — an operator resizing the terminal after mount.

    BOTH SURFACES, AND BOTH FIXTURES.  The strip and the canvas were each needed
    to see it: at (34,15) on `legacy` the canvas numeral was ABSENT while the
    strip was merely stale, and `LLR-N06.3.3` makes absence MEAN "nothing is
    hidden".  `anidado` carries its own two sizes so this cannot be read as a
    `legacy` quirk.

    It presses nothing and repaints nothing, exactly like `B-56` above: a
    `refresh_canvas()` here would repaint away the very claim.
    """
    install(tmp_path, map_id)
    checked = 0
    for term in _SETTLE_TERMS[map_id]:
        app = MapperApp(tmp_path)
        async with app.run_test(size=term) as pilot:
            await pilot.pause()
            screen = await open_map(app, pilot, map_id)
            for _ in range(3):
                await pilot.pause()
            hidden = screen._unpainted_ids()  # noqa: SLF001
            assert hidden, f"{term} hides nothing; this size cannot falsify the arm"
            strip = " ".join(
                rows_in(screen, screen.query_one("#map-pagination").region)
            )
            assert _declared_total([strip]) == len(hidden), (
                f"{map_id} {term}: the strip declares {_declared_total([strip])} "
                f"on a first look that is hiding {len(hidden)}"
            )
            assert _declared_total(canvas_rows(screen)) == len(hidden), (
                f"{map_id} {term}: the canvas header declares "
                f"{_declared_total(canvas_rows(screen))} on a first look that is "
                f"hiding {len(hidden)}; `None` here means the numeral is ABSENT, "
                f"which LLR-N06.3.3 makes mean 'nothing is hidden'"
            )
            checked += 1
    assert checked == len(_SETTLE_TERMS[map_id])


@pytest.mark.asyncio
async def test_b60_resizing_the_terminal_re_declares_without_a_keypress(tmp_path):
    """The other half of `B-60`: the operator resizes, and nobody presses a key.

    `MapScreen` had NO resize handler at all — grep-confirmed — so every
    declaration was computed for whichever frame existed at mount.  Drag a
    terminal from a size where the whole map fits to one where it does not and
    both declaring surfaces keep saying "nothing is hidden", which
    `LLR-N06.3.3` makes a statement rather than a silence.  Ordinary navigation
    does not heal it either: measured over nine keys, only `l` and `o`
    reconcile, and at the root `j` is a no-op.

    So this presses nothing.  It resizes, waits for the layout, and asks the
    two surfaces what they say.  The FIRST size is asserted to hide nothing, so
    the arm cannot pass by having been in the hidden state all along.

    THE WIDTH IS HELD CONSTANT, AND THAT IS A BOUND ON THIS ARM RATHER THAN A
    CONVENIENCE.  `_apply_region_visibility` runs in `on_mount` and on an
    explicit toggle, and NOWHERE ELSE -- so shrinking the terminal across the
    auto-collapse threshold does not re-evaluate it.  Measured: from (140,45) to
    (50,20) the rail and the inspector stay shown, `_chrome_width()` is 60
    columns of a 50-column terminal, and the canvas region collapses to ONE
    column, where mounting at (50,20) directly collapses both and gives 50.
    That is a separate defect on the same path, pre-existing (there was no
    resize handler at all) and NOT closed here: re-running the visibility pass
    on resize shows and hides focusable regions, which is where `LLR-CNV.3.1`
    and `B-50` placed the keyboard.  It is carried, and this arm changes only
    the height so it measures re-declaration and not that.
    """
    install(tmp_path, "legacy")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 45)) as pilot:
        await pilot.pause()
        screen = await open_map(app, pilot, "legacy")
        for _ in range(3):
            await pilot.pause()
        assert len(screen.graph.nodes) == 8
        # THE CONTROL: at this size nothing is hidden, so a stale numeral here
        # is indistinguishable from a correct one and the resize is the whole
        # measurement.
        assert not screen._unpainted_ids(), "the starting size already hides nodes"  # noqa: SLF001

        await pilot.resize_terminal(140, 14)
        for _ in range(4):
            await pilot.pause()

        hidden = screen._unpainted_ids()  # noqa: SLF001
        assert hidden, "the resize hid nothing; this arm cannot falsify anything"
        strip = " ".join(rows_in(screen, screen.query_one("#map-pagination").region))
        assert _declared_total([strip]) == len(hidden), (
            f"after a resize the strip declares {_declared_total([strip])} "
            f"against {len(hidden)} hidden, with no key pressed"
        )
        assert _declared_total(canvas_rows(screen)) == len(hidden), (
            f"after a resize the canvas header declares "
            f"{_declared_total(canvas_rows(screen))} against {len(hidden)} "
            f"hidden; `None` means the numeral is ABSENT, which LLR-N06.3.3 "
            f"makes mean 'nothing is hidden'"
        )


@pytest.mark.asyncio
async def test_a_region_too_short_for_a_body_row_declares_nothing_painted(tmp_path):
    """`_canvas_size`'s short-region branch, ON THE HEIGHT AXIS — the real one.

    WRITTEN BECAUSE THE CARRY BOUNDED THE WRONG AXIS.  The recorded note said
    the affected band was "exactly 20..29 columns of canvas".  It is not a width
    band at all: the branch is selected by `region.height <= header rows`, and
    the failure reproduced at (50, 14) and (100, 10) — ordinary geometries far
    outside that band — as well as at (31, 18).  The old code returned
    `h = region.height` there, so `row_limit = h - 1` believed canvas row 0
    survived when the two-row header had eaten the whole region: all 8 nodes
    hidden, the indicator declaring 7.

    AND THE WIDTH AXIS IS BACK IN THE SWEEP, because correcting the axis was
    over-corrected into dropping it.  The fix that closed the height case priced
    the header with a CONSTANT 2, so the same over-declaration recurred at every
    width where the header wraps further: at terminal (28,17) the renderer
    declared `erp` on a frame carrying zero card marks and the strip read 7
    against a truth of 8 (`B-61`).  These rows were RED on the shipped tree
    before `header_rows` replaced the constant — they are the regression, not
    belt-and-braces.

    Swept over BOTH axes, through the real screen, and the identity
    `declared == traced` is asserted at every size — including the sizes where
    the region is genuinely too short, which is where it used to break.
    """
    install(tmp_path, "legacy")
    short, tall = [], []
    for term_w, term_h in (
        (31, 18), (50, 14), (100, 10), (60, 12), (80, 11),
        (50, 20), (80, 24), (100, 30), (118, 34),
        # THE `B-61` BAND — canvas width 20..34, where the header takes three or
        # four rows.  Each of these five was measured over-declaring before the
        # fix; (28,17) is the transcript quoted above.
        (20, 24), (22, 30), (26, 19), (28, 17), (28, 30), (34, 22),
    ):
        app = MapperApp(tmp_path)
        async with app.run_test(size=(term_w, term_h)) as pilot:
            await pilot.pause()
            screen = await open_map(app, pilot, "legacy")
            screen.refresh_canvas()
            await pilot.pause()
            assert len(screen.graph.nodes) == 8
            region_h = screen.query_one("#map-canvas").region.height
            w, h = screen._canvas_size()  # noqa: SLF001
            declared = painted_ids(screen.graph, screen._view_state(w, h))  # noqa: SLF001
            traced = oracle_traced(
                screen.graph, (), w, canvas_rows(screen), pan_x=screen.pan_x
            )
            # THE IDENTITY, at every size in the sweep.  This is the assertion
            # the old branch broke, and it breaks again the moment the
            # short-region case starts over-declaring.
            assert declared == traced, (
                f"terminal {(term_w, term_h)}: region.height={region_h}, "
                f"canvas={(w, h)} declares {sorted(declared - traced)} with no "
                f"trace and traces {sorted(traced - declared)} undeclared"
            )
            # The SCREEN's helper, with the region's own content width: the
            # wrap width is measured, never guessed (see `_header_rows`).
            charged = screen._header_rows(  # noqa: SLF001
                screen.query_one("#map-canvas").content_size.width
            )
            (short if region_h <= charged else tall).append(
                (term_w, term_h, region_h, len(declared), charged)
            )

    # NON-VACUITY, on three halves now: the sweep must actually contain the
    # branch it was written for, it must contain sizes that paint something — a
    # sweep of nothing-painted cases would satisfy the identity trivially — and
    # it must contain sizes where the header costs MORE than two rows, which is
    # the band the identity used to break in.
    assert short, f"no size in the sweep reaches the short-region branch: {tall}"
    assert all(painted == 0 for *_size, painted, _c in short), short
    assert any(painted > 0 for *_size, painted, _c in tall), tall
    assert any(charged > 2 for *_size, _p, charged in short + tall), short + tall
    assert any(
        charged > 2 and painted > 0 for *_size, painted, charged in tall
    ), tall


@pytest.mark.asyncio
async def test_the_canvas_is_charged_every_row_the_header_leaves(tmp_path):
    """`row_limit` == region rows − header rows.  The OTHER side of the identity.

    WRITTEN BECAUSE A MUTANT SURVIVED THE WHOLE SUITE.  `declared == traced` is
    structurally one-sided: `h` feeds the render AND the declaration, so a
    `_canvas_size` that under-sizes by a row shrinks both together and every
    arm above stays green while a card the region could show disappears.
    Measured: `region.height - header_rows(...)` in place of
    `region.height - (rows - 1)` permanently discards one body row — at (31,16)
    the only visible card vanishes — and the full suite passed with it.

    So this pins the OTHER direction: the frame the renderer is given is as tall
    as the region allows.  Nothing else in the suite says the canvas may not
    quietly waste rows, and a declaration that is honest about a frame smaller
    than the region is still the wrong frame.

    The equality is `row_limit == region.height - charged`, and `charged` is
    `header_rows` rather than a literal — the same measurement `_canvas_size`
    consumes, so this cannot pass by both sides sharing a wrong constant: the
    arm above already pins `header_rows` against the rendered line.
    """
    install(tmp_path, "legacy")
    checked = []
    for term in ((80, 24), (118, 34), (50, 20), (60, 18), (28, 30), (22, 30)):
        app = MapperApp(tmp_path)
        async with app.run_test(size=term) as pilot:
            await pilot.pause()
            screen = await open_map(app, pilot, "legacy")
            screen.refresh_canvas()
            await pilot.pause()
            assert len(screen.graph.nodes) == 8
            canvas = screen.query_one("#map-canvas")
            region_h = canvas.region.height
            _w, h = screen._canvas_size()  # noqa: SLF001
            # Through the SCREEN's helper, so the wrap width is the measured one
            # `_canvas_size` itself prices with.  Calling `header_rows` here with
            # a guessed width would re-open exactly the divisor question this
            # round closed.
            charged = screen._header_rows(canvas.content_size.width)  # noqa: SLF001
            if region_h <= charged:      # the short branch has its own arm
                continue
            # `render` emits `1 + (h - 1)` LOGICAL lines and the widget spends
            # `charged` PHYSICAL rows on the first, so the body budget is
            # `region_h - charged` and `row_limit` is `h - 1`.
            assert h - 1 == region_h - charged, (
                f"{term}: canvas h={h} gives row_limit {h - 1} into a region of "
                f"{region_h} rows whose header costs {charged}; the canvas is "
                f"{region_h - charged - (h - 1)} rows away from full utilisation"
            )
            checked.append((term, region_h, charged, h))
    # NON-VACUITY: the sweep must reach the tall branch at all, and it must
    # contain a size where the header costs more than two rows — otherwise a
    # constant 2 would satisfy this arm.
    assert len(checked) >= 4, checked
    assert any(charged > 2 for *_s, charged, _h in checked), checked


@pytest.mark.asyncio
async def test_the_paint_site_differences_one_set_on_a_PARTIAL_overlap(tmp_path):
    """`LLR-N06.3.1` at the PAINT SITE, on the state where a sum is wrong.

    WRITTEN BECAUSE A MUTANT SURVIVED ALL TWELVE ARMS OF THIS MODULE.  `TC-039`
    drives the paint site but at 140x45, where the viewport hides nothing, so a
    sum that over-counts only when viewport-hidden ∩ fold-hidden is PARTIAL is
    invisible to it; `AT-015` reads the renderer-written header rather than the
    strip; `TC-038` and the `B-56` arm run unfolded.  Measured, such a sum
    paints `▽ 15 fuera de vista` on an eight-node map at `legacy` 30x12 with
    `erp` folded, with `tests/test_overflow.py` 12 of 12 green.

    So: `anidado` at the NESTED fold `{ops, log}` — `TC-039`'s own state — driven
    at 50x16 instead of 140x45, read through the STRIP, with the truth taken
    from the composited frame by the oracle and never from the helper under
    test.  The size was found by sweeping 56 sizes × 3 folds on `anidado` and 30
    × 4 on `legacy` for the state where BOTH causes bite at once; on these two
    shallow shipped maps it is a narrow band, which is itself why no arm was
    standing on it.

    THE OVERLAP IS ASSERTED, NOT ASSUMED, on all three clauses that make the row
    discriminating: a fold hides something, the VIEWPORT independently hides
    something, and the naive combination of the two disagrees with the truth.
    Without the third this is `TC-035`'s positive control again.
    """
    install(tmp_path, "anidado")
    folded = ("ops", "log")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(50, 16)) as pilot:
        await pilot.pause()
        screen = await open_map(app, pilot, "anidado")
        screen.folded = frozenset(folded)
        screen.refresh_canvas()
        for _ in range(3):
            await pilot.pause()
        graph = screen.graph
        assert len(graph.nodes) == 7, sorted(graph.nodes)

        w, h = screen._canvas_size()  # noqa: SLF001
        rows = canvas_rows(screen)
        traced = oracle_traced(graph, folded, w, rows, pan_x=screen.pan_x)
        declared = painted_ids(graph, screen._view_state(w, h))  # noqa: SLF001
        assert declared == traced, (sorted(declared), sorted(traced))
        truth = len(graph.nodes) - len(traced)

        fold_hidden = hidden_under(graph, folded)
        view_hidden = frozenset(graph.nodes) - traced - fold_hidden
        assert fold_hidden, "no fold hides anything; the row is unfolded"
        assert view_hidden, (
            "the viewport hides nothing beyond the fold; this row cannot reach "
            "the overlap state and is TC-039 at another size"
        )
        naive = naive_hidden_sum(graph, folded) + len(view_hidden)
        assert naive != truth, (
            f"the naive sum reads {naive} and the truth is {truth}; they agree "
            f"at this row, so it cannot discriminate a sum from a difference"
        )

        strip = " ".join(
            rows_in(screen, screen.query_one("#map-pagination").region)
        )
        assert _declared_total([strip]) == truth, (
            f"the strip declares {_declared_total([strip])} on a frame that "
            f"traces {sorted(traced)} of {len(graph.nodes)}"
        )
        # And the two declaring surfaces still agree at this configuration.
        assert _declared_total(rows) == truth


@pytest.mark.asyncio
async def test_tc_039_the_screen_helper_differences_one_set_on_the_overlap_case(tmp_path):
    """`LLR-N06.3.1` AT THE SCREEN, which `TC-034` does not reach.

    WRITTEN BECAUSE A MUTANT SURVIVED.  `TC-034` asserts the property against
    `painted_ids`, one layer below `MapScreen._unpainted_ids`; the battery arm
    that made the SCREEN add a fold count to a viewport count stayed GREEN,
    because the only surface reading that helper is painted from the same helper
    and both sides of the comparison moved together.  An inert predicate gets
    rewritten, not re-argued.

    Driven on `anidado` at `FOLD = {ops, log}` -- `log` nested inside the folded
    `ops` -- where the naive sum is 6 and the truth is 4.

    AND IT WAS STILL ONE LAYER TOO LOW.  The rewrite above reads
    `_unpainted_ids()`, a SET-returning helper; `LLR-N06.3.1` forbids a SUM, and
    a sum can only be expressed where a COUNT is taken, which is
    `_pagination_text`.  Mutating exactly there -- `len(unpainted) +
    naive_hidden_sum(...)` -- paints a strip reading `6 fuera de vista` against
    a truth of 4 while all ten tests in this module pass.  So the arm now reads
    the PAINTED STRIP too, on the same state, and the second assertion names the
    number the mutant paints rather than only the number it should.
    """
    install(tmp_path, "anidado")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 45)) as pilot:
        await pilot.pause()
        screen = await open_map(app, pilot, "anidado")
        assert len(screen.graph.nodes) == 7
        screen.folded = frozenset({"ops", "log"})
        screen.refresh_canvas()
        await pilot.pause()

        hidden = screen._unpainted_ids()  # noqa: SLF001
        truth = hidden_under(screen.graph, screen.folded)
        naive = naive_hidden_sum(screen.graph, screen.folded)
        assert naive == 6 and len(truth) == 4, (naive, sorted(truth))
        assert hidden == truth, sorted(hidden ^ truth)
        assert len(hidden) < naive, (
            "the screen declares the naive sum; every node both folded AND "
            "off-screen is being counted twice"
        )

        # THE PAINTED SURFACE, on the same state — the layer the mutant lives
        # on.  Nothing is hidden by the VIEWPORT at 140x45, so every node the
        # strip declares is hidden by the fold, and the two rules differ by 2.
        strip = " ".join(
            rows_in(screen, screen.query_one("#map-pagination").region)
        )
        assert _declared_total([strip]) == len(truth) == 4, strip
        assert f"{naive} fuera de vista" not in strip, (
            f"the strip declares the naive sum {naive}; the truth is {len(truth)}"
        )


@pytest.mark.asyncio
async def test_tc_040_a_pill_nested_inside_another_fold_is_not_painted(tmp_path):
    """`LLR-N06.3.2` through the PILLS, on the nesting case.

    WRITTEN BECAUSE A MUTANT SURVIVED.  The battery arm that painted a pill for
    every id in `folded`, nested ones included, stayed GREEN: `TC-034` and
    `TC-035` read `painted_ids` without rendering, and `AT-014`'s folds are all
    siblings, so nothing exercised a nested fold on the painted surface.

    This is the transcript `LLR-N06.3.2` says `TC-032` shall re-run through the
    real renderer once the fold mechanism ships: ONE painted pill, reading 4,
    equal to the true hidden union -- not two pills summing to 6.
    """
    graph = install(tmp_path, "anidado")
    folded = frozenset({"ops", "log"})
    painted = LayeredRenderer().render(
        graph, ViewState(w=140, h=45, folded=folded)
    ).plain

    counts = [int(m.group(1)) for m in _PILL.finditer(" ".join(painted.split("\n")))]
    assert counts == [4], counts
    assert sum(counts) == len(hidden_under(graph, folded)) == 4
    assert sum(counts) != naive_hidden_sum(graph, folded)
    # And the pill names the branch it is standing in for.
    assert "Operaciones" in painted
    # `log` is inside the fold, so neither its card nor a pill for it is painted.
    assert "Logistica" not in painted


@pytest.mark.asyncio
async def test_tc_038_both_declaring_surfaces_read_one_truth(tmp_path):
    """The canvas and the pagination strip declare the SAME numeral, ON A FIRST LOOK.

    Two surfaces, one computation: both come off `painted_ids` for the state the
    canvas was just rendered with.  Two surfaces with two computations is how
    they start disagreeing, which is `LLR-N06.2.1`'s lesson one widget over.

    THE DOCSTRING USED TO SAY "always" AND THE BODY REPAINTED FIRST, which is
    the property this arm now actually holds without help.  It called
    `refresh_canvas()` before measuring and carried a comment saying the residual
    was "one frame" that "any repaint reconciles"; remove that line on the tree
    as it stood and this arm failed `assert 4 == 7`, because only the STRIP was
    recomputed after layout and the canvas header kept its pre-layout numeral
    (`B-60`).  Measured over nine keys, only `l` and `o` healed it — `j`, `k`,
    `h`, the arrows and `tab` did not — so "any repaint" was false too.
    `_declare_after_layout` now repaints BOTH declaring surfaces, so THIS ARM
    PRESSES NOTHING AND REPAINTS NOTHING before it measures, and is green only
    because that scheduling exists.

    And `_unpainted_ids()` returns `None` -- not an empty set -- in a view that
    declares nothing, so the strip keeps its reserved-affordance content instead
    of claiming `0 hidden` on a canvas that is hiding several.

    THIS ARM RUNS UNFOLDED, and that is why it could not see the naive-sum
    mutant: on `legacy` with no fold the naive rule and the true rule coincide.
    The nested-fold case is driven through the painted strip in `TC-039` and at
    a partial overlap in the arm above, which are the arms that have the nesting.
    """
    install(tmp_path, "legacy")
    offset = await height_offset(tmp_path, "legacy", 50)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(50, 6 + offset)) as pilot:
        await pilot.pause()
        screen = await open_map(app, pilot, "legacy")
        for _ in range(3):
            await pilot.pause()
        assert len(screen.graph.nodes) == 8

        hidden = screen._unpainted_ids()  # noqa: SLF001
        assert hidden, "nothing is hidden at this size; the arm would be vacuous"
        strip = " ".join(
            rows_in(screen, screen.query_one("#map-pagination").region)
        )
        assert _declared_total([strip]) == len(hidden)
        assert _declared_total(canvas_rows(screen)) == len(hidden)

        # The outline view declares nothing, and says so with `None`.
        await pilot.press("o")
        await pilot.pause()
        assert screen.outline_mode
        assert screen._unpainted_ids() is None  # noqa: SLF001
        strip = " ".join(
            rows_in(screen, screen.query_one("#map-pagination").region)
        )
        assert OVERFLOW_TOKEN not in strip
        assert strip.strip(), "the strip lost its reserved-affordance content"


# --------------------------------------------------------------------------
# AT-015 / AT-016 — the acceptance, over every configuration


def _contrast(fg: str, bg: str) -> float:
    def luminance(colour: str) -> float:
        triplet = Color.parse(colour).get_truecolor()
        channels = []
        for raw in (triplet.red, triplet.green, triplet.blue):
            value = raw / 255
            channels.append(
                value / 12.92 if value <= 0.03928
                else ((value + 0.055) / 1.055) ** 2.4
            )
        r, g, b = channels
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    first, second = luminance(fg), luminance(bg)
    lighter, darker = max(first, second), min(first, second)
    return (lighter + 0.05) / (darker + 0.05)


@pytest.mark.asyncio
async def test_at_015_the_declared_total_reconciles_at_every_configuration(tmp_path):
    """AT-015 — `PRED-1` and `PRED-4`, plus the two empty cases.

    THE CONFIGURATION COUNT IS ASSERTED, not left to whoever runs the test.
    Measured at `(50, 12, ())` — the first row of the table — two of the three
    named mutants are green on all three set predicates, so an acceptance that
    ran only the first row could not fail on them.
    """
    driven = []
    for w, h, folded, pan in CONFIGURATIONS:
        screen, rows, declared, _traced = await _drive(tmp_path, w, h, folded, pan)
        driven.append((w, h, folded, pan))

        total = _declared_total(rows)
        expected = len(screen.graph.nodes) - len(declared)
        if expected == 0:
            assert total is None, (
                f"{(w, h, folded, pan)}: an indicator painted while nothing is hidden"
            )
        else:
            # PRED-1 reconciliation.
            assert total == expected, (w, h, folded, pan, total, expected)

        # PRED-4 legibility.  The declaration carries the whole story's promise
        # and was assigned `WORDMARK`, which measures 1.85 : 1 against GROUND at
        # both rungs and collapses INTO the ground on the WINDOWS rung.  Every
        # other predicate can be green on a frame the operator cannot read.
        assert _contrast(darkside.INK, darkside.GROUND) >= 4.5
        assert darkside.INK != darkside.GROUND
        eight_bit = EIGHT_BIT_PALETTE[
            Color.parse(darkside.INK).downgrade(ColorSystem.EIGHT_BIT).number
        ].hex
        assert _contrast(eight_bit, darkside.GROUND) >= 4.5, eight_bit

    assert set(PINNED_CONFIGURATIONS) <= set(driven), (
        "a configuration the requirement PINS was not driven"
    )
    assert len(driven) == len(CONFIGURATIONS) == 7, driven
    assert any(pan != (0, 0) for *_rest, pan in driven), (
        "no configuration pans; the pan x overflow identity has no acceptance"
    )

    # E3, the genuinely empty case: a 0-node graph mounts, declares nothing and
    # paints no pill.  Distinct from the zero-hidden case above, which the parked
    # entry conflated with it.
    empty = Graph()
    assert painted_ids(empty, ViewState(w=80, h=24)) == frozenset()
    painted = LayeredRenderer().render(empty, ViewState(w=80, h=24)).plain
    assert painted == "(no map loaded)"
    assert OVERFLOW_TOKEN not in painted and FOLD_PILL_TOKEN not in painted


@pytest.mark.asyncio
async def test_at_016_the_declared_set_equals_the_traced_set(tmp_path):
    """AT-016 — `PRED-2 ∧ PRED-3`, i.e. SET EQUALITY, over every configuration.

    `PRED-2` alone is green on the pure-deletion mutant: `all()` over an empty
    set is `True`, so a renderer declaring NOTHING painted passes it — which is
    precisely the shipped pre-state.  `PRED-3` costs nothing (`traced` is already
    computed) and catches both that and the plausible weakening that omits
    exactly the nodes a fold would hide.
    """
    driven = []
    outcomes = []
    for w, h, folded, pan in CONFIGURATIONS:
        screen, _rows, declared, traced = await _drive(tmp_path, w, h, folded, pan)
        driven.append((w, h, folded, pan))
        outcomes.append((len(declared), len(screen.graph.nodes) - len(declared)))
        assert declared <= traced, (
            f"PRED-2 soundness: {(w, h, folded, pan)} declares "
            f"{sorted(declared - traced)} painted with no trace in the frame"
        )
        assert traced <= declared, (
            f"PRED-3 completeness: {(w, h, folded, pan)} paints "
            f"{sorted(traced - declared)} and declares them hidden"
        )

    assert set(PINNED_CONFIGURATIONS) <= set(driven)
    assert len(driven) == len(CONFIGURATIONS) == 7, driven
    # NON-DEGENERACY, ASSERTED OVER THE OUTCOMES, and the previous form of this
    # guard could not do its own job: it re-checked that the literal
    # `CONFIGURATIONS` table has distinct rows -- which is a property of the
    # table, visible by reading it -- while `driven` is appended purely from the
    # loop variables.  Forcing all seven configurations to identical RESULTS
    # still passed it.  The stated purpose was "all agreeing on 8-of-8 would be
    # copies of one case", so that is what is measured now.
    assert len(set(outcomes)) >= 3, outcomes
    assert any(hidden == 0 for _painted, hidden in outcomes), outcomes
    assert any(hidden > 0 for _painted, hidden in outcomes), outcomes
