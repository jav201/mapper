"""US-N07 «búsqueda» — the search core (Inc-4a).

`AT-018`, `AT-019`, `AT-020`, `AT-052`, and the `LLR-N07.3.1` / `LLR-N07.3.3`
unit arms.  `AT-021` lives in `test_layered.py` (the renderer's file) and
`TC-026b` in `test_fold.py` (the pill's file), each beside the surface it gates.

TERMINAL SIZE IS DECLARED, NOT DEFAULTED.  `run_test()` defaults to 80x24, and
`_apply_region_visibility` auto-hides BOTH the rail and the inspector there -- the
configuration that produced a false three-pass reading earlier in this batch.
The declared context of use is 118x34, and every pilot predicate below ASSERTS
the configuration it asked for is the one it got before reading anything: a size
argument is a request, not a guarantee.

THE CANVAS PAINTS TITLES, NEVER IDS (0/8 at three widths).  No predicate here
searches painted text for a node id; ids are observed as data through
`painted_ids`, and paint is observed through the region-clipped frame.
"""
from __future__ import annotations

import re

from mapper import darkside
from mapper.app import COUNT_REGION_ID, SEARCH_COUNT_SUBJECT, MapperApp
from mapper.search import SearchIndex, tree_order
from mapper.views.layered import painted_ids
from tests.inc3_support import (
    install,
    oracle_traced,
    open_map,
    pan_graph,
    rows_in,
    canvas_rows,
    hidden_under,
)
from tests.inc4_support import (
    ABSENT_QUERY,
    MAP_ID,
    QUERY,
    build_adjuntos,
    descendants_of,
    expected_tree_order,
    narrow_hits,
)

CONTEXT_OF_USE = (118, 34)
# The first measured size at which the rail leaves, so the strip's origin could
# move.  `AT-052`'s claim is positional and a single-size run cannot see a count
# line pinned to an absolute row.
RAIL_GONE_SIZE = (100, 30)

# The count line as a PATTERN: a numeral (bare, or `n/N`) bound in the same
# expression as the declared subject noun.  A bare `5/5 coincidencias` does not
# match, which is `AT-052`'s whole assertion.  The noun is read from the shipped
# constant, so the expectation is a DERIVATION of the product's own declaration
# and not a second copy of the wording that drifts from it.
COUNT_RE = re.compile(r"(\d+)(?:\s*/\s*(\d+))?\s+" + re.escape(SEARCH_COUNT_SUBJECT))


def count_region_text(screen) -> str:
    """The count strip, region-clipped and JOINED before parsing.

    Measured height 1 at 118x34, 100x30 and 80x24 -- so the join is a no-op at
    every size this file uses.  It is kept anyway: `test_overflow.py` records a
    wrap at a 30-column strip, and the region's height is not a constant any
    predicate may assume.
    """
    return " ".join(rows_in(screen, screen.query_one(f"#{COUNT_REGION_ID}").region))


async def submit(pilot, q: str) -> None:
    """Open search with the real `/`, type, and submit with the real `enter`."""
    await pilot.press("slash")
    await pilot.pause()
    for ch in q:
        await pilot.press("space" if ch == " " else ch)
    await pilot.press("enter")
    await pilot.pause()


def assert_declared_layout(screen, *, rail: bool, inspector: bool) -> None:
    """A size argument is a request; this is the receipt."""
    assert screen.query_one("#map-rail").display is rail
    assert screen.query_one("#map-inspector").display is inspector


# --------------------------------------------------------------------------
# LLR-N07.1.2 / AT-020 — the widening is intentional, and monotone


def test_at_020_hit_widening_is_intentional(tmp_path):
    """AT-020 — id, subtitle and attachment now match, and nothing stopped.

    Three arms on one graph and one query, each an id the OLD inline predicate
    rejects.  The negative control is reproduced in this file rather than
    imported, because `LLR-N07.1.1` deletes the production copy -- a control
    imported from the thing under test would be deleted along with it and leave
    an arm that reads like a control and asserts nothing.
    """
    graph = build_adjuntos(tmp_path)
    wide = SearchIndex(graph).query(QUERY)
    narrow = narrow_hits(graph, QUERY)

    # Both halves non-empty BEFORE they are compared, or a widening that
    # collapsed to nothing would read as a widening.
    assert wide, "the new owner returned no hits at all"
    assert narrow, "the negative control returned no hits, so it controls nothing"

    # P-020.3 — monotone.  Nothing that used to match stopped matching.
    assert set(narrow) <= set(wide)
    assert set(narrow) - set(wide) == set(), "the widening LOST a hit"
    gained = set(wide) - set(narrow)
    assert gained, "nothing was gained, so there is no widening to be intentional"

    # P-020.1 — the three arms, DERIVED rather than hand-listed.  For every
    # gained id, work out which haystack components alone carry the query; the
    # union of those must cover the whole declared delta.  A fixture edit that
    # broke an arm fails this coverage assertion, not merely the arm.
    def components(nid: str) -> set[str]:
        node = graph.nodes[nid]
        parts = {
            "id": node.id,
            "title": node.ficha.title,
            "meta": node.ficha.meta,
            "notes": node.ficha.notes,
            "fields": " ".join(node.ficha.fields.values()),
            "attachments": " ".join(
                a.caption or a.path for a in node.ficha.attachments
            ),
        }
        return {k for k, v in parts.items() if QUERY in v.lower()}

    covered: set[str] = set()
    for nid in gained:
        covered |= components(nid)
    # `{id, meta, attachments}` is exactly `Graph.search_hits`' haystack minus
    # the three the old predicate already read.
    assert {"id", "meta", "attachments"} <= covered, (
        f"the widening's declared delta is not exercised; covered={sorted(covered)}"
    )

    # P-020.2 — and each of the three is a hit under the new owner while the old
    # predicate rejects it, which is what makes the arm about the WIDENING and
    # not about matching in general.
    for kind in ("id", "meta", "attachments"):
        sole = [nid for nid in gained if components(nid) == {kind}]
        assert sole, f"no node matches by {kind} ALONE; the arm is not isolated"
        for nid in sole:
            assert nid in wide
            assert nid not in narrow


def test_llr_n07_3_1_hits_come_back_in_tree_order(tmp_path):
    """The ordering helper walks the tree, not the dict.

    THE SELF-GUARD IS THE POINT.  On the shipped `legacy` fixture, BOTH of this
    batch's working queries give `tree_order == dict_order`, so this assertion
    written against it would have passed while asserting nothing.  The guard
    fails the test on a fixture where the two coincide instead of quietly
    passing on it.
    """
    graph = build_adjuntos(tmp_path)
    hits = set(SearchIndex(graph).query(QUERY))

    dict_ordered = [nid for nid in graph.nodes if nid in hits]
    tree_ordered = [nid for nid in expected_tree_order(graph) if nid in hits]
    assert tree_ordered != dict_ordered, (
        "SELF-GUARD: the two orders coincide on this fixture, so the assertion "
        "below cannot fail and must not be trusted"
    )

    # The expectation is the test's OWN pre-order walk (`inc4_support`), never
    # `mapper.search.tree_order` -- an ordering assertion that asks the ordering
    # helper for its expectation asserts that the helper agrees with itself.
    assert SearchIndex(graph).query(QUERY) == tree_ordered
    assert tree_order(graph) == expected_tree_order(graph)


def test_llr_n07_3_3_a_blank_query_is_not_a_match_everything(tmp_path):
    """Empty and whitespace-only queries resolve to ZERO hits.

    The counterfactual is non-trivial and is asserted here rather than described:
    the SHIPPED `Graph.search_hits` returns 6 of 6 for `""` and 4 of 6 for
    `"   "`, because `if q in hay` makes the empty string a substring of every
    haystack.  A probe that cannot show a non-trivial pre-state is unproven.
    """
    graph = build_adjuntos(tmp_path)
    index = SearchIndex(graph)

    assert len(graph.search_hits("")) == len(graph.nodes) == 6
    assert 0 < len(graph.search_hits("   ")) < len(graph.nodes)

    for blank in ("", "   ", "\t", "\n "):
        assert index.hits(blank) == frozenset(), blank
        assert index.query(blank) == [], blank

    # Rich markup is not a match-everything either, and it is not a match-nothing
    # by accident: the same graph answers the bare term.
    assert index.query(f"[bold]{QUERY}[/]") == []
    assert index.query(QUERY), "the control query stopped matching"

    # The count may be taken from either shape, on every graph -- including one
    # whose second component the root cannot reach.
    for q in ("", "   ", QUERY, ABSENT_QUERY):
        assert len(index.query(q)) == len(index.hits(q)), q


def test_the_search_owner_loses_no_hit_the_root_cannot_reach(tmp_path):
    """A disconnected component still counts, or the count under-reports.

    `test_layered.py` already ships a forest fixture, so a `.mmd` declaring a
    second component is a shape this tree meets rather than a hypothetical.  A
    tree-order walk alone would silently drop those ids.
    """
    graph = build_adjuntos(tmp_path)
    from mapper.model import Ficha, Node

    graph.add_node(Node(id="huerfano", ficha=Ficha(title="Otro riesgo")))
    assert "huerfano" not in tree_order(graph), (
        "the orphan is reachable from the root, so this arm controls nothing"
    )
    ordered = SearchIndex(graph).query(QUERY)
    assert "huerfano" in ordered
    assert ordered[-1] == "huerfano", "unreachable hits come last, in graph order"
    assert len(ordered) == len(SearchIndex(graph).hits(QUERY))


# --------------------------------------------------------------------------
# HLR-N07.2 / AT-018 — the count covers the whole graph


async def test_at_018_the_count_covers_the_whole_graph_in_four_states(tmp_path):
    """AT-018 — one numeral, four states, each reached by a REAL chord.

    The states are the product `{fold, no fold} x {pan, no pan}`, constructed as
    an explicit product so a state cannot be dropped silently, and each is
    ASSERTED to have been reached before its numeral is read.

    THE FIXTURE IS `pan_graph`, AND THE REASON IS EXECUTED.  The batch's design
    note put this predicate on `legacy` at 118x34 on the claim that the pan arm
    is reachable there.  It is not: measured on `legacy` at that size,
    `pan_extent` returns `((53, 56), (13, 25))`, so `max_pan_x` and `max_pan_y`
    are both **0** and state (c) would silently degrade into state (a) -- the arm
    would look like it exercised the viewport and would have exercised nothing.
    `pan_graph` overflows both axes at the declared size (`max_pan_x = 49`).
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        app.store.save("panmap", pan_graph())
        screen = await open_map(app, pilot, "panmap")
        assert_declared_layout(screen, rail=True, inspector=True)

        query = "hoja"
        expected = len(SearchIndex(screen.graph).query(query))
        assert expected > 0, "the query matches nothing; two zeros would pass"

        # The branch that will be folded holds a hit, and that hit is painted
        # right now -- so folding can actually remove it from view.
        branch = "b0"
        inside = descendants_of(screen.graph, branch) & set(
            SearchIndex(screen.graph).query(query)
        )
        assert inside, "the folded branch holds no hit; the fold arm is vacuous"

        await submit(pilot, query)

        def numerals() -> tuple[int, int]:
            joined = count_region_text(screen)
            m = COUNT_RE.search(joined)
            assert m is not None, f"no count line painted: {joined!r}"
            # `n/N`: the whole-graph total is the SECOND numeral.
            return int(m.group(1)), int(m.group(2))

        def painted() -> frozenset[str]:
            return painted_ids(screen.graph, screen._view_state(*screen._canvas_size()))

        seen: dict[tuple[bool, bool], int] = {}

        # (a) nothing folded, nothing panned.
        assert screen.folded == frozenset() and screen.pan_x == 0
        assert inside <= painted(), "the hit is not on screen to begin with"
        seen[(False, False)] = numerals()[1]

        # (b) the branch folded with the REAL `z`.
        screen.nav.cursor = branch
        screen.refresh_canvas()
        await pilot.pause()
        await pilot.press("z")
        await pilot.pause()
        assert screen.folded == frozenset({branch})
        assert not (inside & painted()), "folding did not hide the hit"
        seen[(True, False)] = numerals()[1]

        # (c) unfolded again, then panned with the REAL `L` until a hit leaves
        # the canvas.  The target is not named: the loop runs until the
        # condition holds and the test FAILS if it never does.
        await pilot.press("z")
        await pilot.pause()
        assert screen.folded == frozenset()
        before = set(SearchIndex(screen.graph).query(query)) & painted()
        assert before, "no hit is painted, so nothing can be panned off"
        for _ in range(60):
            if not (before <= painted()):
                break
            await pilot.press("L")
            await pilot.pause()
        assert screen.pan_x > 0, "the pan chord never moved the viewport"
        gone = before - painted()
        assert gone, "no hit was ever panned off canvas; the arm is vacuous"
        seen[(False, True)] = numerals()[1]

        # (d) both.
        screen.nav.cursor = branch
        screen.refresh_canvas()
        await pilot.pause()
        await pilot.press("z")
        await pilot.pause()
        assert screen.folded == frozenset({branch}) and screen.pan_x > 0
        seen[(True, True)] = numerals()[1]

        # The product is complete, and every state answered the SAME whole-graph
        # number.  Equality, never `>=`: a floor cannot see an under-count.
        assert set(seen) == {(f, p) for f in (False, True) for p in (False, True)}
        assert set(seen.values()) == {expected}, seen


async def test_at_019_the_count_is_invariant_under_fold(tmp_path):
    """AT-019 — the count does not move when a matching branch folds.

    THE PINNED QUERY IS `carlos` AND THE PIN IS LOAD-BEARING.  Executed on
    `legacy`, `carlos` matches exactly `pres`, which lies strictly inside `fin`;
    the batch's other working query `riesgo` matches `rrhh` and `alm`, NEITHER
    inside `fin`, so folding cannot change its count under a correct
    implementation OR under the defect -- the arm would be green either way.
    The inside-the-branch clause is what carries the statement's meaning into
    the acceptance.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        app.store.save("legacy", install(tmp_path, "legacy"))
        screen = await open_map(app, pilot, "legacy")
        assert_declared_layout(screen, rail=True, inspector=True)

        query, branch = "carlos", "fin"
        hits = set(SearchIndex(screen.graph).query(query))
        assert hits, "the pinned query matches nothing"
        # Re-derived by the test's own descendant walk, never asked of the
        # product.
        inside = hits & hidden_under(screen.graph, frozenset({branch}))
        assert inside, (
            f"{query!r} matches nothing strictly inside {branch!r}; the "
            "invariant would hold vacuously"
        )

        await submit(pilot, query)

        def count() -> int:
            m = COUNT_RE.search(count_region_text(screen))
            assert m is not None
            return int(m.group(2))

        def painted() -> frozenset[str]:
            return painted_ids(screen.graph, screen._view_state(*screen._canvas_size()))

        # P-019.2 — the hit is genuinely painted, observed BOTH as data and as
        # pixels, before anything is folded.  Only then is the equality below a
        # statement about the invariant rather than about two absences.
        w, _h = screen._canvas_size()
        assert inside <= painted()
        traced = oracle_traced(
            screen.graph, screen.folded, w, canvas_rows(screen), screen.pan_x
        )
        assert inside <= traced, "the hit is declared painted but leaves no trace"

        before = count()
        assert before > 0, "a count of zero cannot demonstrate invariance"

        screen.nav.cursor = branch
        screen.refresh_canvas()
        await pilot.pause()
        await pilot.press("z")
        await pilot.pause()
        assert screen.folded == frozenset({branch})
        assert not (inside & painted()), "the fold did not hide the matching node"
        folded_count = count()

        await pilot.press("z")
        await pilot.pause()
        assert screen.folded == frozenset()
        after = count()

        assert before == folded_count == after > 0


# --------------------------------------------------------------------------
# HLR-N07.2 `#D37` / AT-052 — the line names its subject


async def test_at_052_the_count_line_names_its_subject(tmp_path):
    """AT-052 — the count declares WHICH question it answers.

    The strip already carries a page numeral and an off-canvas numeral, so a
    bare `5/5` would leave two count-shaped surfaces on one strip
    distinguishable only by an implementer's wording choice.  The pattern binds
    a numeral AND the declared subject noun in ONE expression; the noun is read
    from the shipped constant so a wording change moves both sides together.

    Run at two sizes because the claim is positional: 100x30 is the first
    measured size at which the rail leaves and the strip's origin moves
    (`y=30` -> `y=25`).
    """
    for size, rail in ((CONTEXT_OF_USE, True), (RAIL_GONE_SIZE, False)):
        app = MapperApp(tmp_path)
        async with app.run_test(size=size) as pilot:
            await pilot.pause()
            build_adjuntos(tmp_path)
            screen = await open_map(app, pilot, MAP_ID)
            assert_declared_layout(screen, rail=rail, inspector=True)

            # Before any search there is no count line at all -- so what the
            # arms below find was painted BY the search.
            assert COUNT_RE.search(count_region_text(screen)) is None

            await submit(pilot, QUERY)
            live = count_region_text(screen)
            matches = list(COUNT_RE.finditer(live))
            assert len(matches) == 1, (size, live)
            hit = matches[0]
            assert int(hit.group(2)) == len(SearchIndex(screen.graph).query(QUERY))

            # The sibling numeral is present on the SAME strip and is NOT what
            # the pattern matched -- which is the "two surfaces, distinguishable
            # by content" claim made mechanical rather than asserted in prose.
            page = f"1/{len(screen.graph.nodes)}"
            assert page in live, (size, live)
            assert live.index(page) < hit.start(), (size, live)
            assert SEARCH_COUNT_SUBJECT not in live[: hit.start()]

            # A query that matches nothing paints `0 <subject>` -- at the SAME
            # offset, measured on this same screen at this same size rather than
            # asserted as a literal column, which would break at every width.
            await submit(pilot, ABSENT_QUERY)
            empty = count_region_text(screen)
            empty_match = COUNT_RE.search(empty)
            assert empty_match is not None, (size, empty)
            assert empty_match.group(1) == "0" and empty_match.group(2) is None
            assert empty_match.start() == hit.start(), (size, hit.start(), empty)

            # And a blank query paints no count line at all, which is a THIRD
            # state and not a synonym for the empty result.
            await submit(pilot, "   ")
            blank = count_region_text(screen)
            assert COUNT_RE.search(blank) is None, (size, blank)
            assert SEARCH_COUNT_SUBJECT not in blank
            assert page in blank, "the strip lost its own content too"

    # THE RESIDUE THE MUTATION CANNOT REACH, CLOSED WITHOUT COPYING THE WORDING.
    # `COUNT_RE` is DERIVED from `SEARCH_COUNT_SUBJECT`, so mutating the constant
    # moves both sides of every arm above together and the mutation is inert by
    # construction -- recorded, not hidden.  What those arms constrain is the
    # constant's WIRING, never its SHAPE: degraded to a single token it would
    # still bind a numeral to a subject and still pass, shipping a line reading
    # `5/5 x` while `AT-052`'s requirement is that the line declare WHICH
    # question it answers.  A floor on the phrase's length closes that without
    # becoming the second copy of the wording the single-declaration rule exists
    # to prevent.
    assert len(SEARCH_COUNT_SUBJECT.split()) >= 3, SEARCH_COUNT_SUBJECT


async def test_the_selection_numeral_is_the_cursors_place_among_the_hits(tmp_path):
    """The FIRST numeral of `n/N`, which nothing else in the suite reads.

    `AT-018` and `AT-052` assert `group(2)`, the whole-graph total; `group(1)`
    was computed at `AT-018` and DISCARDED, and read nowhere else except for the
    bare `0` of the no-match line.  So any value at all shipped green in the `n`
    position -- an unobserved behaviour on a green suite, which is the failure
    this batch is spending its budget to stop, and `_count_line`'s own docstring
    argues against shipping a numeral that is a lie.

    THE EXPECTATION IS DERIVED, NEVER SPELLED.  A literal would be wrong: `0/N`
    is FIXTURE-DEPENDENT, not universal.  On `adjuntos` a fresh screen reads
    `1/5`, because the root matches `riesgo` by id and the cursor starts on the
    root; on a map whose root is not a hit the same code reads `0/N`.  So the
    arm computes the cursor's place in the resolved order and compares.

    BOTH BRANCHES ARE EXERCISED AND BOTH ARE ASSERTED NON-VACUOUS.  A predicate
    that only ever saw the cursor ON a hit would not see `0` regress, and one
    that only ever saw it OFF a hit would not see the ordinal regress.  This is
    also the numeral `Inc-4b`'s next-match walk MOVES: without this it would
    move an undefended number.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        build_adjuntos(tmp_path)
        screen = await open_map(app, pilot, MAP_ID)
        assert_declared_layout(screen, rail=True, inspector=True)

        await submit(pilot, QUERY)

        order = SearchIndex(screen.graph).query(QUERY)
        assert len(order) >= 2, "a one-hit fixture cannot show an ordinal move"
        off = [nid for nid in screen.graph.nodes if nid not in order]
        assert off, "every node matches; the `0` branch is unreachable here"

        def selection_numeral() -> int:
            joined = count_region_text(screen)
            m = COUNT_RE.search(joined)
            assert m is not None, f"no count line painted: {joined!r}"
            return int(m.group(1))

        def expected() -> int:
            cursor = screen.nav.cursor
            return order.index(cursor) + 1 if cursor in order else 0

        seen: set[int] = set()
        # Every hit in turn, plus every non-hit -- so the ordinal is checked at
        # each of its values and the `0` is checked at more than one node.
        for nid in order + off:
            screen.nav.cursor = nid
            screen.refresh_canvas()
            await pilot.pause()
            want = expected()
            assert selection_numeral() == want, (nid, want, count_region_text(screen))
            seen.add(want)

        # The product is complete: every ordinal 1..len(order) was observed, and
        # so was the `0`.  Without this the loop could have run entirely inside
        # one branch and still passed.
        assert seen == set(range(0, len(order) + 1)), seen


def _self_reads(fn) -> set[str]:
    """Every `self.X` attribute name read anywhere in *fn*'s source."""
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(fn).lstrip())
    return {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
    }


def _app_tree():
    """`mapper/app.py` parsed, for censuses that must see the WHOLE module."""
    import ast
    import inspect
    import pathlib

    from mapper.app import MapScreen

    src = pathlib.Path(inspect.getfile(MapScreen)).read_text(encoding="utf-8")
    return ast.parse(src)


def test_the_count_and_the_paint_share_one_resolution(tmp_path):
    """`HLR-N07.1`'s promise, asserted structurally rather than by coincidence.

    `AT-019` shows the count does not MOVE when a branch folds; this shows the
    strip's number and the canvas's highlight are computed from ONE resolution,
    so they cannot disagree.

    WHAT THIS ARM PROVES, STATED HONESTLY.  An earlier revision of it asserted
    only that each named consumer MENTIONS the helper -- positive membership,
    nothing more -- and review demonstrated three shapes that passed it while
    breaking the property: a second resolution added BESIDE the retained helper
    call, that same second path scoped to the viewport (risk A-6 itself), and a
    pure helper whose RESULT the count line then narrows by the folded set.  The
    last was executed: on both acceptance fixtures the folded branch id is not
    itself a hit, so narrowing the count by `folded` changed neither number
    (`AT-018` 8->8, `AT-019` 1->1) and the mutant passed `AT-018`, `AT-019` and
    the old arm at once.  The old docstring claimed the surfaces "could not
    have" disagreed "for a deeper reason than 'both happen to call the same
    function today'"; it established exactly that and nothing more.

    So the property is now carried by three predicates that together close the
    additive, the viewport-scoped, the downstream-narrowing and the
    new-consumer shapes:

      (1) the helper reads no viewport state -- the whole-graph clause;
      (2) `LLR-N07.2.1` governs "the count computation", which is
          `_search_order`, `_search_hits` and `_count_line`, so the viewport ban
          covers the whole chain from the resolution to the pinned argument.
          `_search_hits` was the one link left out of an earlier revision, and
          review CONSTRUCTED the defect through exactly that gap: narrowing the
          derivation inside it left every named surface untouched, kept `hits=`
          a bare call, and passed the entire fast lane while making the count
          and the paint disagree on the shipped `adjuntos` fixture -- count 5
          against 4 painted highlights, for each of the three hits that are
          foldable branches.  The ban is free there because `_search_hits`
          reads no viewport state and has no reason to.
          `_view_state` is deliberately NOT under this ban:
          it reads `folded`/`pan_x`/`pan_y` legitimately, because passing the
          viewport to the RENDERER is its job.  What must not vary is the hit
          set, so that argument is pinned structurally instead;
      (3) a module-wide census: the owner is CONSTRUCTED exactly once and the
          model's raw resolver is not reached at all, so a second path reddens
          whichever method grows it and whether or not the first is retained.

    `Inc-4b` adds a fourth consumer, which is the shape the old arm was
    structurally blind to; (3) is what sees it.
    """
    import ast

    from mapper.app import MapScreen

    VIEWPORT = ("folded", "pan_x", "pan_y")

    resolves = _self_reads(MapScreen._search_order)
    assert resolves, "the derivation found no attribute reads at all"
    assert "graph" in resolves and "query_text" in resolves, resolves

    # (1) + (2) -- the whole count computation, per `LLR-N07.2.1`'s own wording.
    for method in (
        MapScreen._search_order,
        MapScreen._search_hits,
        MapScreen._count_line,
    ):
        reads = _self_reads(method)
        leaked = [name for name in VIEWPORT if name in reads]
        assert not leaked, (method.__name__, leaked, reads)

    # Every consumer goes THROUGH the helper.
    assert "_search_order" in _self_reads(MapScreen._search_hits)
    assert "_search_order" in _self_reads(MapScreen._count_line)
    assert "_search_hits" in _self_reads(MapScreen._view_state)

    # (2b) `_view_state` may read the viewport -- it hands it to the renderer --
    # but the hit set it carries must be the helper's answer UNNARROWED.  A
    # `hits=` argument that wrapped, filtered or intersected the call would not
    # be a bare `self._search_hits()` call and reddens here.
    import inspect as _inspect

    vs = ast.parse(_inspect.getsource(MapScreen._view_state).lstrip())
    hits_args = [
        kw.value
        for node in ast.walk(vs)
        if isinstance(node, ast.Call)
        for kw in node.keywords
        if kw.arg == "hits"
    ]
    assert len(hits_args) == 1, f"expected one hits= argument, found {len(hits_args)}"
    arg = hits_args[0]
    assert (
        isinstance(arg, ast.Call)
        and not arg.args
        and not arg.keywords
        and isinstance(arg.func, ast.Attribute)
        and arg.func.attr == "_search_hits"
        and isinstance(arg.func.value, ast.Name)
        and arg.func.value.id == "self"
    ), f"hits= is not a bare self._search_hits() call: {ast.dump(arg)}"

    # (3) The census.  1 construction site today, so this passes now and reddens
    # the moment a second appears -- including in a method not named here.
    tree = _app_tree()
    built = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "SearchIndex"
    ]
    assert len(built) == 1, f"a second resolution was constructed at {built}"

    # And the owner is not bypassed: `Graph.search_hits` is the model's raw
    # resolver, which `SearchIndex.hits` wraps to apply `LLR-N07.3.3`.  Reaching
    # it directly from the screen would be a second resolution that never
    # constructs `SearchIndex` and so slips past the census above.
    raw = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "search_hits"
    ]
    assert raw == [], f"the screen reaches the raw resolver at {raw}"


def _titled_graph(n: int, token: str = "zeta"):
    """A branching graph of *n* nodes where every other title carries *token*."""
    from mapper.model import Edge, Ficha, Graph, Node

    graph = Graph()
    prev = None
    for i in range(n):
        nid = f"n{i}"
        word = token if i % 2 == 0 else "alfa"
        graph.add_node(Node(id=nid, ficha=Ficha(title=f"nodo {i} {word}")))
        if prev is not None:
            graph.add_edge(Edge(parent_id=(prev if i % 3 else "n0"), child_id=nid))
        prev = nid
    return graph


def test_the_search_obeys_the_renderers_declared_bound(tmp_path):
    """Above `MAX_RENDER_NODES` the search stops where the drawing stops.

    THE REGRESSION THIS PINS WAS MEASURED, NOT IMAGINED.  The renderer refuses
    to draw past the bound and returns its overflow declaration without
    evaluating anything -- render cost 0.000 s at 12002 nodes.  The resolution
    honoured no such bound, so above the limit the ENTIRE frame cost was a
    search ordering a tree that would never be painted: 4 resolutions per
    repaint, seconds each.  At entry this path was free, because `_view_state`
    passed a query STRING and the renderer returned the declaration before ever
    evaluating a predicate -- so the cost was a clean regression of this
    increment and the bound is what closes it.

    NON-VACUOUS BY CONSTRUCTION: the same query on the same shape BELOW the
    bound resolves a non-empty order, so the empty answer above it is the
    bound's doing and not the query's.
    """
    from mapper.app import MapScreen
    from mapper.views.layered import MAX_RENDER_NODES

    screen = MapScreen("bounded")
    screen.query_text = "zeta"

    screen.graph = _titled_graph(40)
    assert len(screen.graph.nodes) <= MAX_RENDER_NODES
    below = screen._search_order()
    screen._open_paint_pass()
    assert below, "the query matches nothing below the bound; the arm is vacuous"

    screen.graph = _titled_graph(MAX_RENDER_NODES + 2)
    assert len(screen.graph.nodes) > MAX_RENDER_NODES
    # The hits are genuinely there -- the OWNER still finds them.  What stops is
    # the ordering, at the app seam, and only above the bound.
    assert SearchIndex(screen.graph).hits("zeta"), "no hit above the bound either"
    # `None`, NOT an empty order: the two are different facts and the arm below
    # (`..._does_not_claim_zero_matches`) is what says why the difference is
    # load-bearing.  Asserted as identity so an empty order cannot satisfy it.
    assert screen._search_order() is None


def _count_line_text(screen) -> str:
    """The count line as the strip receives it, without mounting an app.

    `_pagination_text` appends this verbatim (asserted structurally below), so
    the string here is the string painted -- and reading it directly is what
    lets these two arms run against a 12002-node graph without paying for a
    real frame, which was measured at seconds each.
    """
    import ast
    import inspect

    from mapper.app import MapScreen

    assert "_count_line" in _self_reads(MapScreen._pagination_text), (
        "the strip no longer builds its count from `_count_line`; this helper "
        "reads a surface the operator does not see"
    )
    strip = ast.parse(inspect.getsource(MapScreen._pagination_text).lstrip())
    appended = [
        node
        for node in ast.walk(strip)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "append"
        for arg in node.args
        if isinstance(arg, ast.Call)
        and isinstance(arg.func, ast.Attribute)
        and arg.func.attr == "_count_line"
    ]
    assert len(appended) == 1, "the count line is not appended to the strip bare"
    return screen._count_line().plain


def test_above_the_bound_the_count_line_does_not_claim_zero_matches(tmp_path):
    """The bound must not paint a FALSE statement about the operator's data.

    `AT-052` reserves `0 <subject>` for a question that was asked and came back
    empty.  Above `MAX_RENDER_NODES` no question is answered at all -- the
    resolution is skipped precisely because nothing will be drawn -- so painting
    `0` there declares that a graph FULL of matches contains none.  Measured at
    12002 nodes on the first revision of the bound: the strip read
    `0 coincidencias en el mapa` beside its own `12002 fuera de vista`, on a
    graph the search owner still resolves matches in.  That is the defect class
    US-N07 exists to close, reintroduced at smaller scale by the fix for it.

    NON-VACUOUS BY CONSTRUCTION, AND THE GUARD IS THE WHOLE POINT.  The owner is
    asked independently and must find matches, so `0` would be a lie rather than
    a coincidence; without that assert this arm would pass on a graph that
    genuinely has none and gate nothing.

    THIS FAILS INDEPENDENTLY of its sibling
    (`..._still_says_zero_when_the_answer_is_empty`), and that separation is
    deliberate: they assert different facts, and one predicate covering both
    would let the empty-state wording vanish behind the bound's silence.
    """
    from mapper.app import MapScreen
    from mapper.views.layered import MAX_RENDER_NODES

    screen = MapScreen("unbounded")
    screen.query_text = "zeta"
    screen.graph = _titled_graph(MAX_RENDER_NODES + 2)
    assert len(screen.graph.nodes) > MAX_RENDER_NODES

    real = SearchIndex(screen.graph).hits("zeta")
    assert real, "the graph holds no match; `0` would be TRUE and the arm vacuous"

    painted = _count_line_text(screen)
    assert COUNT_RE.search(painted) is None, (len(real), painted)
    assert SEARCH_COUNT_SUBJECT not in painted, painted
    assert painted.strip() == "", painted


def test_below_the_bound_the_count_line_still_says_zero_when_empty(tmp_path):
    """And the silence above the bound did not swallow the empty state.

    The sibling arm above forbids a count line on a graph too large to draw.
    The cheapest way to satisfy it is to stop painting `0 <subject>` at all --
    which would silently delete `AT-052`'s empty-result wording, a state the
    operator reaches by typing a query that matches nothing.  So this arm holds
    the other half, on a graph BELOW the bound, and the two must fail for
    different reasons.

    Uses the same helper and the same fixture shape as its sibling, so the only
    variable between them is which side of the bound the graph sits on.
    """
    from mapper.app import MapScreen
    from mapper.views.layered import MAX_RENDER_NODES

    screen = MapScreen("bounded-empty")
    screen.graph = _titled_graph(40)
    assert len(screen.graph.nodes) <= MAX_RENDER_NODES

    # The SAME screen answers both ways, so the emptiness below is the query's
    # doing and not the fixture's.
    screen.query_text = "zeta"
    assert SearchIndex(screen.graph).hits("zeta"), "the fixture matches nothing"
    assert COUNT_RE.search(_count_line_text(screen)) is not None

    screen._open_paint_pass()
    screen.query_text = ABSENT_QUERY
    assert not SearchIndex(screen.graph).hits(ABSENT_QUERY), "the query DOES match"

    painted = _count_line_text(screen)
    empty = COUNT_RE.search(painted)
    assert empty is not None, painted
    assert empty.group(1) == "0" and empty.group(2) is None, painted


def test_a_query_that_matches_nothing_does_not_walk_the_tree(monkeypatch):
    """`LLR-N07.3.3` enforced for the WORK, not only for the result.

    The blank guard answered `frozenset()` in ~4 microseconds and the walk then
    ran anyway against an empty hit set -- so an operator who has NEVER SEARCHED
    paid the full ordering cost on every repaint, which is the DEFAULT STATE of
    the screen rather than an edge case.  Measured before the fix: 3.26 s per
    call at 12000 nodes for a query of whitespace.

    Asserted by COUNTING the walk rather than by timing it: a wall-clock
    threshold on a shared runner is a flake, and the property is "the walk does
    not happen", which is exactly what a counter observes.
    """
    from mapper import search as search_module

    walks = []
    real = search_module.tree_order
    monkeypatch.setattr(
        search_module,
        "tree_order",
        lambda graph: (walks.append(1), real(graph))[1],
    )

    graph = _titled_graph(200)
    index = SearchIndex(graph)

    for blank in ("", "   ", " ", "\t"):
        assert index.query(blank) == []
    assert index.query("no-such-token-xyzzy") == []
    assert walks == [], f"the tree was walked {len(walks)} times for nothing"

    # And the counter is live -- a query that DOES match still walks, so the
    # emptiness above is the guard and not a broken monkeypatch.
    assert index.query("zeta")
    assert walks == [1]


def test_one_paint_pass_resolves_exactly_once(tmp_path):
    """The memo lives for one repaint, and for no longer than that.

    Three to four consumers reach the resolver per repaint -- `_view_state` from
    the render and again from `_unpainted_ids`, plus `_count_line` -- and each
    used to resolve from scratch.  Measured at the bound before the fix: 4
    resolutions with a query active, 3 with a blank one.

    BOTH HALVES ARE ASSERTED, AND THE SECOND IS THE ONE THAT MATTERS.  A memo
    that never expired would serve a stale order after an edit; the contract is
    that `_open_paint_pass` -- which every repaint calls first -- drops it, so
    the only way to read a stale order is to have already painted a stale
    screen.  WHICH methods count as "every repaint" is not asserted here: this
    arm owns the memo's BEHAVIOUR within one pass, and
    `test_every_reader_of_the_resolution_is_inside_a_paint_pass` owns the set.
    """
    from mapper import search as search_module
    from mapper.app import MapScreen

    built = []
    real = search_module.SearchIndex

    class Counting(real):  # type: ignore[misc,valid-type]
        def __init__(self, graph):
            built.append(1)
            super().__init__(graph)

    import mapper.app as app_module

    original = app_module.SearchIndex
    app_module.SearchIndex = Counting
    try:
        screen = MapScreen("memoised")
        screen.graph = _titled_graph(60)
        screen.query_text = "zeta"

        screen._open_paint_pass()
        first = screen._search_order()
        assert first, "the query matches nothing; the memo arm is vacuous"
        for _ in range(5):
            assert screen._search_order() == first
        assert built == [1], f"one pass resolved {len(built)} times"

        # A NEW pass must resolve again -- the memo does not outlive its frame.
        screen._open_paint_pass()
        assert screen._search_order() == first
        assert built == [1, 1], f"the memo survived the pass boundary: {built}"

        # A query change inside one pass is not served from the memo either.
        answered = screen._search_order()
        screen.query_text = "alfa"
        assert screen._search_order() != answered
        assert len(built) == 3
    finally:
        app_module.SearchIndex = original

    # The protocol itself is gated by `test_every_reader_of_the_resolution_...`
    # below, which DERIVES the set of readers instead of naming them.


def _map_screen_self_reads() -> dict[str, set[str]]:
    """Every `MapScreen` method -> the `self.X` names its source reads.

    Parsed from the module rather than reached through `inspect`, so a method
    nothing in this process ever calls is still seen.  Nested definitions are
    walked into deliberately: a closure inside a method that reaches the
    resolution is that method reaching it.
    """
    import ast

    cls = next(
        node
        for node in ast.walk(_app_tree())
        if isinstance(node, ast.ClassDef) and node.name == "MapScreen"
    )
    return {
        item.name: {
            sub.attr
            for sub in ast.walk(item)
            if isinstance(sub, ast.Attribute)
            and isinstance(sub.value, ast.Name)
            and sub.value.id == "self"
        }
        for item in cls.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


# Every reader of the resolution that is NOT itself inside a paint pass, with
# the reason it is safe there.  This is a shrinking list, never a defining one:
# the set it excuses is DERIVED below, so a reader added tomorrow appears in the
# derivation and fails as unexplained.  A stale entry fails too.
_PASS_FREE_READERS = {
    "__init__": "declares the memo; there is no pass to be inside of yet",
    "_open_paint_pass": "IS the pass opener -- it clears the memo, never reads a resolution",
    "_search_order": "the resolver itself",
    "_search_hits": "resolver helper; runs inside whichever pass called it",
    "_count_line": "resolver helper; runs inside whichever pass called it",
    "_view_state": "resolver helper; builds the renderer's parameters in its caller's pass",
    "_pagination_text": "builds the strip; both of its callers open a pass first",
    "_unpainted_ids": "reached only from `_pagination_text`, inside that caller's pass",
    "_reclamp_pan": "called from INSIDE `refresh_canvas`'s pass, deliberately (see its call site)",
    "_pan": "reads the extent of the frame ON SCREEN -- the frame being panned -- then repaints",
    "action_pan_left": "wrapper over `_pan`",
    "action_pan_right": "wrapper over `_pan`",
    "action_pan_up": "wrapper over `_pan`",
    "action_pan_down": "wrapper over `_pan`",
    "action_export_svg": "consumes the memo of the frame currently painted, which is what it depicts",
    # Inc-4b's keypress-bound consumer, which this arm was written to force into
    # declaring itself.  It DECLINES to open a pass, and the reason is the same
    # shape as `_pan`'s rather than a shrug: the walk moves the selection AMONG
    # the matches the operator is currently looking at, so the resolution of the
    # frame on screen is the correct input and not a stale one -- and it cannot
    # BE stale, because the memo is keyed on the graph object and the query text
    # and a walk changes neither.  The repaint it ends with opens its own pass.
    "_walk_hits": "moves the selection inside the matches of the frame ON SCREEN, then repaints",
    "action_next_hit": "wrapper over `_walk_hits`",
    "action_prev_hit": "wrapper over `_walk_hits`",
    "on_input_submitted": "reads the order of the frame `refresh_canvas` painted on the line above",
    # Round 2.  `esc` and the hint line were written with different guards and
    # disagreed above the renderer's bound, so they now share one predicate --
    # which puts BOTH of them in the derived set.  That is this arm working as
    # designed, not an obstacle to routing around: the consolidation is exactly
    # the kind of edit that grows the reader set, and it has to declare itself.
    "_search_is_live": "asks whether the frame ON SCREEN is showing an answer, which is the previous pass's",
    "action_back_or_home": "wrapper over `_search_is_live`; clears and repaints, or leaves",
}


def test_every_reader_of_the_resolution_is_inside_a_paint_pass(tmp_path):
    """The memo's contract, DERIVED over the class instead of listed.

    WHY THIS ARM WAS REWRITTEN.  Its predecessor iterated a hand-written
    two-tuple -- `refresh_canvas` and `_declare_after_layout` -- under a comment
    claiming "a new repaint path that forgets it reddens here".  That claim was
    FALSE on the day it shipped: `_pan` and `action_export_svg` both reach
    `_view_state` with zero passes opened, measured, and a path added tomorrow
    would simply not be in the tuple.  A predicate that quantifies over a set is
    only as strong as the set, and a hand-listed set survives every mutation of
    the code it claims to govern.

    SO THE SET IS COMPUTED.  Starting from the resolver and the memo, the
    readers are grown transitively over `self.X` calls, and the growth STOPS at
    any method that opens its own pass -- which is exactly the semantics of the
    contract: a caller of `refresh_canvas` is covered because `refresh_canvas`
    opens a pass.  What survives is the set of methods that reach the resolution
    WITHOUT one, and every member must carry a stated reason.

    THE THREE EXEMPTIONS THAT ARE JUDGEMENTS, NOT BOOKKEEPING, ARE NAMED HERE.
    `_pan` reads the extent of the frame already on screen and then repaints;
    `action_export_svg` renders the frame currently painted, so the previous
    pass's memo is the correct input rather than a stale one; `_reclamp_pan` is
    called from inside `refresh_canvas`'s own pass.  None is a defect today and
    review could not construct a live stale paint through any of them -- but
    they are the shape `Inc-4b`'s keypress-bound consumer will have, which is
    why this arm has to exist BEFORE that lands rather than after.

    THE WALK CANNOT PASS VACUOUSLY.  An empty or broken parse would excuse
    everything, so the class must yield a plausible number of methods, the seeds
    must resolve to real ones, the derived set must clear a floor measured at
    15, and the closure must be shown to have propagated more than one hop.
    """
    reads = _map_screen_self_reads()

    # Non-vacuity, before any verdict is read from the derivation.
    assert len(reads) >= 60, f"the class parsed to only {len(reads)} methods"
    assert {"_search_order", "_view_state", "_open_paint_pass"} <= set(reads), sorted(reads)

    # EXACT SET, NOT A SUBSET -- and the difference is the whole arm (`NEW-4`).
    # This classifier reads a NAME MENTION, not a call, and carries no ordering,
    # so a method that merely names the opener is excused while it reads the
    # PREVIOUS frame's memo.  Two live seams were constructed against the subset
    # form and both stayed GREEN because the set was allowed to GROW from 2 to 3
    # unnoticed: (a) deferring the opener via `call_after_refresh` and reading
    # now -- which is this file's own house idiom at `app.py:1256` and `:1599`,
    # not a contrivance -- and (b) naming the opener inside a guard that never
    # calls it.  Pinning the set exactly reddens both and leaves the shipped tree
    # green.  The arm exists to force `Inc-4b`'s consumer to DECLARE itself; a
    # subset check is precisely the form that lets it decline silently.
    openers = {name for name, r in reads.items() if "_open_paint_pass" in r}
    assert openers == {"refresh_canvas", "_declare_after_layout"}, sorted(openers)

    reaching = {name for name in ("_search_order", "_view_state") if name in reads}
    reaching |= {name for name, r in reads.items() if "_search_memo" in r}
    reaching -= openers
    while True:
        grown = {
            name
            for name, r in reads.items()
            if name not in reaching and name not in openers and r & reaching
        }
        if not grown:
            break
        reaching |= grown

    # The closure ran, and it ran further than one hop: `action_pan_left` reaches
    # the resolution only through `_pan`, so its presence is the receipt that the
    # transitive step works rather than the seed alone being reported back.
    assert len(reaching) >= 15, (len(reaching), sorted(reaching))
    assert "action_pan_left" in reaching, sorted(reaching)

    unexplained = sorted(reaching - set(_PASS_FREE_READERS))
    assert not unexplained, (
        f"{unexplained} reach the search resolution without opening a paint "
        f"pass and without a stated reason.  Open a pass, or register the "
        f"method in `_PASS_FREE_READERS` with why the previous frame's memo is "
        f"the correct input for it."
    )
    stale = sorted(set(_PASS_FREE_READERS) - reaching)
    assert not stale, f"{stale} no longer reach the resolution; drop the exemption"
    assert all(_PASS_FREE_READERS.values()), "an exemption carries no reason"


def test_the_resolution_cannot_be_corrupted_by_the_caller(tmp_path):
    """What `_search_order` hands out is not the memo's own object.

    Three consumers read the same resolution inside one pass.  While the memo
    handed back its own `list`, a consumer that sorted or trimmed what it
    received corrupted every later read in that pass -- measured: a caller
    mutating its result changed what the next caller saw, same object identity.
    No shipped consumer mutates it, so this was latent; `Inc-4b`'s next-match
    walk is the plausible first, and `ViewState.hits` is a `frozenset` one layer
    up for precisely this reason, so the two decisions should agree.

    ASSERTED AS A PROPERTY, NOT AS A TYPE.  The arm attempts the corruption and
    then re-reads, so it holds for a tuple, for a defensive copy, or for any
    later shape -- what it forbids is the aliasing, not a particular container.
    """
    from mapper.app import MapScreen

    screen = MapScreen("aliasing")
    screen.graph = _titled_graph(60)
    screen.query_text = "zeta"

    screen._open_paint_pass()
    first = screen._search_order()
    assert first, "the query matches nothing; the aliasing arm would be vacuous"
    before = list(first)

    try:
        first.append("intruder")  # type: ignore[union-attr]
    except AttributeError:
        pass  # immutable -- one of the two ways to hold the property

    second = screen._search_order()
    assert list(second) == before, (before, list(second))
    assert "intruder" not in second


def test_the_two_tree_walks_agree(tmp_path):
    """`search.tree_order` and `MapScreen._incomplete_order` walk the same tree.

    THE DUPLICATION IS REAL AND IS RECORDED, NOT REPAIRED HERE.  The two walks
    are structurally identical -- same root seed, same
    `nid in seen or nid not in graph.nodes` guard, same `reversed(children)`
    push, same visited set -- and only the filter line differs.  `tree_order`'s
    docstring justifies the copy by rejecting a `search -> app` import, and that
    reason does not hold: `app.py` already imports `search` (`app.py:42`), so
    `_incomplete_order` consuming `tree_order` creates no new edge.

    IT IS STILL NOT DONE IN THIS INCREMENT, DELIBERATELY.  `_incomplete_order`
    is the US-N04 coverage worklist's ordering -- a different requirement's
    shipped behaviour, outside this increment's acceptance -- and rewriting it
    to consume `tree_order` would change that path on a gate that does not cover
    it.  The lower-risk move is this predicate: it buys the guarantee the
    dedup would have bought (the two "next"s mean the same thing to the
    operator) at zero behavioural risk, and the dedup is carried.

    THE FIXTURE IS BUILT HERE BECAUSE NO SHIPPED FIXTURE DISCRIMINATES.
    Measured over `legacy`, `anidado`, `adjuntos` and `pan_graph`: three have no
    incomplete node at all, and on `legacy` the two incomplete nodes come out in
    the same relative order under a tree walk and under dict-insertion order --
    so a pin on any of them would pass against a walk that ignored the tree
    entirely.  This graph is shaped so that it cannot: the assert below FAILS if
    the discrimination is ever lost.
    """
    from mapper.app import MapScreen
    from mapper.model import Edge, Ficha, Graph, Node, SchemaField

    required = SchemaField(key="owner", label="responsable", required=True)
    graph = Graph(schema=[required])
    # Insertion order r,a,b,c,d -- deliberately NOT the tree's order.
    for nid in ("r", "a", "b", "c", "d", "island"):
        fields = {"owner": "x"} if nid == "r" else {}
        graph.add_node(Node(id=nid, ficha=Ficha(title=nid, fields=fields)))
    for parent, child in (
        ("r", "c"), ("r", "a"), ("a", "d"), ("a", "b"),
        ("c", "d"),        # diamond: d is reachable two ways
        ("d", "d"),        # self loop
        ("b", "ghost"),    # dangling edge, no such node
        ("island", "b"),   # edge INTO the reachable set from outside it
    ):
        graph.add_edge(Edge(parent_id=parent, child_id=child))

    walked = tree_order(graph)
    insertion = list(graph.nodes)
    def incomplete(seq) -> list[str]:
        return [
            nid for nid in seq
            if graph.nodes[nid].ficha.missing_required(graph.schema)
        ]

    # The fixture earns its keep, or this test says so.
    assert walked != insertion, "the walk order matches insertion order"
    assert incomplete(walked) != incomplete(insertion), (
        "the incomplete subset is order-identical under both; a walk that "
        "ignored the tree would pass this pin"
    )
    assert len(incomplete(walked)) < len(walked), "the filter drops nothing"
    assert "island" not in walked, "the unreachable node leaked into the walk"

    screen = MapScreen("agreement")
    screen.graph = graph
    assert screen._incomplete_order() == incomplete(walked)


def test_the_hit_tone_is_read_from_darkside(tmp_path):
    """A pin, labelled as one: the hit style is not spelled as a hex literal.

    Recorded so the sibling predicates in `test_layered.py` may read the tone
    from `darkside` at run time rather than pinning `#f5f5f5 on #262626`, which
    would go stale the first time the palette moves.
    """
    assert darkside.INK and darkside.STEP
    assert darkside.INK != darkside.STEP


# ==========================================================================
# Inc-4b — the `#D5b` walk, its two empty-state toasts, the one-time rebind
# declaration, state-dependent `esc`, and the seat-derived hint line.
#
# EVERY predicate below presses a REAL chord and reads a PAINTED surface.  The
# one deliberate exception is documented where it occurs: a query containing a
# right-to-left override cannot be typed through `pilot.press`, so that arm sets
# the Input's value and still submits with the real `enter`.


def toast_text(screen) -> str:
    """The event strip, region-clipped and JOINED — never `_event_toast`'s args.

    Reading the arguments would assert what the application MEANT to say.  The
    two empty-state toasts are required to be distinguishable to an OPERATOR,
    which is a claim about the frame.
    """
    return " ".join(rows_in(screen, screen.query_one("#map-toast").region)).strip()


def hint_text(screen) -> str:
    from mapper.widgets.chrome import HintLine

    return screen.query_one(HintLine).text


def hint_rows(screen) -> str:
    from mapper.widgets.chrome import HintLine

    return " ".join(rows_in(screen, screen.query_one(HintLine).region))


async def test_at_022_the_walk_follows_tree_order_and_wraps(tmp_path):
    """AT-022 — `n` walks the matches in TREE order, and wraps in both directions.

    THE SELF-GUARD IS THE FIRST ASSERTION AND IT IS NOT A FORMALITY (`C-55` limb
    2).  On the shipped `legacy` fixture BOTH of this batch's working queries
    give `tree_order == dict_order`, so this node written against it would have
    passed while asserting nothing at all -- on the very requirement whose own
    acceptance criteria name that failure.  The guard is evaluated on the live
    fixture at run time, before any ordering claim is read.

    THE EXPECTATION IS THE TEST'S OWN PRE-ORDER DFS (`inc4_support`), never
    `mapper.search.tree_order`: an ordering assertion that asks the ordering
    helper for its expectation asserts that the helper agrees with itself.

    AND THE SELECTION IS ASSERTED VISIBLE WHERE IT LANDS, at every step
    (`LLR-N06.2.4` PRED-A + PRED-B).  Without that limb "the selection moved to
    the next match" passes on a screen where the operator cannot see the
    selection, which is the silent state change US-N06 forbids.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        app.store.save(MAP_ID, build_adjuntos(tmp_path))
        screen = await open_map(app, pilot, MAP_ID)
        assert_declared_layout(screen, rail=True, inspector=True)

        found = set(SearchIndex(screen.graph).query(QUERY))
        dict_ordered = [nid for nid in screen.graph.nodes if nid in found]
        tree_ordered = [nid for nid in expected_tree_order(screen.graph) if nid in found]
        assert tree_ordered != dict_ordered, (
            "SELF-GUARD: the two orders coincide on this fixture, so the walk "
            "assertion below cannot fail and must not be trusted"
        )
        assert len(tree_ordered) >= 3, (
            "a wrap needs a list long enough to walk off the end of; `carlos` on "
            "`legacy` returns ONE hit and cannot demonstrate one"
        )

        await submit(pilot, QUERY)
        start = screen.nav.cursor

        def painted() -> frozenset[str]:
            return painted_ids(screen.graph, screen._view_state(*screen._canvas_size()))

        def traced() -> frozenset[str]:
            w, _h = screen._canvas_size()
            return oracle_traced(
                screen.graph, screen.folded, w, canvas_rows(screen), screen.pan_x
            )

        # P-022.1 — the recorded sequence, one press at a time.  The press count
        # is DERIVED (`len(hits) + 1`), never the literal, and the last press is
        # the one that has to wrap.
        first = (tree_ordered.index(start) + 1) % len(tree_ordered)
        expected = [
            tree_ordered[(first + i) % len(tree_ordered)]
            for i in range(len(tree_ordered) + 1)
        ]
        recorded = []
        for _ in range(len(tree_ordered) + 1):
            await pilot.press("n")
            await pilot.pause()
            recorded.append(screen.nav.cursor)
            # P-022.5 — visible where it landed, on both channels, every step.
            assert screen.nav.cursor in painted(), (screen.nav.cursor, sorted(painted()))
            assert screen.nav.cursor in traced(), (screen.nav.cursor, sorted(traced()))
        assert recorded == expected, (recorded, expected)

        # P-022.3 — the forward wrap, asserted as its own statement rather than
        # left implicit inside the sequence equality: after exactly `len(hits)`
        # presses the cursor is back where it started.
        assert recorded[len(tree_ordered) - 1] == start

        # P-022.4 — the backward wrap.  Walk forward until the cursor sits on the
        # FIRST hit in tree order (asserted reached, never assumed), then one real
        # `N` must land on the LAST.
        for _ in range(len(tree_ordered) + 1):
            if screen.nav.cursor == tree_ordered[0]:
                break
            await pilot.press("n")
            await pilot.pause()
        assert screen.nav.cursor == tree_ordered[0], "never reached the first hit"
        await pilot.press("N")
        await pilot.pause()
        assert screen.nav.cursor == tree_ordered[-1]


async def test_at_022b_the_walk_enters_from_outside_the_hit_set(tmp_path):
    """AT-022b — the FIRST press when the cursor is not itself a match.

    THIS IS THE WALK'S PRIMARY ENTRY, and until round 2 it was executed by NO
    test in the suite: replacing the `else` limb's body with a raise left the
    whole lane green.  Nothing in `on_input_submitted` moves the cursor onto a
    hit, so an operator who searches for something away from where they are
    standing takes this limb on their very first `n`.  `AT-022` misses it for a
    fixture reason and not a design one -- the resting cursor on `adjuntos`
    (`riesgo-root`) happens to BE a match, so every press there resolves
    through `hits.index(cursor)` instead.

    THE PRECONDITION IS ENFORCED BY CONSTRUCTION, AND THEN PINNED TO PRODUCTION.
    The cursor node is SELECTED as one the index does not match, so a fixture in
    which everything matched raises `StopIteration` at the selection rather than
    passing while testing nothing.  What construction cannot see is the seam the
    self-guard covers: this arm resolves the hit set through `SearchIndex`, while
    the walk reads `_search_order`.  A SECOND, DIVERGENT RESOLUTION -- the shape
    of `M-N07.3-a`, and the exact defect `US-N07` exists to close -- would put
    this node INSIDE production's hits while the arm still believed it outside,
    silently returning the press to the `in hits` limb.  So the guard is taken
    after `submit`, against the order the walk itself reads, and it is that
    divergence and not the fixture that it can fail on.

    THE `N` LIMB IS THE HALF THAT MATTERS.  Swapping the two endpoints is the
    natural typo in `0 if step > 0 else len(hits) - 1`, and a forward-only arm
    cannot see it: with the endpoints exchanged, `n` from outside still lands
    somewhere plausible and only `N` reads the wrong end.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        app.store.save(MAP_ID, build_adjuntos(tmp_path))
        screen = await open_map(app, pilot, MAP_ID)
        assert_declared_layout(screen, rail=True, inspector=True)

        found = set(SearchIndex(screen.graph).query(QUERY))
        order = [nid for nid in expected_tree_order(screen.graph) if nid in found]
        assert len(order) >= 3, (order, "the two endpoints must be distinguishable")
        assert order[0] != order[-1]

        # Construction, not assertion: a fixture in which every node matched
        # raises `StopIteration` right here, loudly.
        outsider = next(nid for nid in screen.graph.nodes if nid not in found)

        await submit(pilot, QUERY)
        assert outsider not in (screen._search_order() or ()), (
            "SELF-GUARD: the cursor must start OUTSIDE the resolution the WALK "
            "reads, or this node resolves through the `in hits` limb and asserts "
            "nothing new"
        )

        # Forward from outside -> the FIRST hit in tree order.
        screen.nav.cursor = outsider
        screen.refresh_canvas()
        await pilot.pause()
        assert screen.nav.cursor == outsider, "the repaint moved the cursor"
        await pilot.press("n")
        await pilot.pause()
        assert screen.nav.cursor == order[0], (screen.nav.cursor, order)

        # Backward from outside -> the LAST.  Re-entered from outside, because
        # the press above left the cursor inside the set.
        screen.nav.cursor = outsider
        screen.refresh_canvas()
        await pilot.pause()
        await pilot.press("N")
        await pilot.pause()
        assert screen.nav.cursor == order[-1], (screen.nav.cursor, order)


async def test_at_023_e1b_and_e1c_are_painted_differently(tmp_path):
    """AT-023 / P-023.4 — two empty states, two toasts, on BOTH channels.

    `M-N07.3-b` is implementing them as ONE toast: green on any test that asserts
    "a toast appears", and it tells an operator who has never searched to go and
    look for a query they never typed.  The titles AND the bodies are asserted
    pairwise distinct, and both are read off the painted `#map-toast` region
    rather than off `_event_toast`'s arguments.

    THE FIRST `n` PRESS IS CONSUMED DELIBERATELY.  It paints the one-time rebind
    declaration (`AT-051b`), which outranks both of these on press one; `E1b` is
    what the SECOND press paints.  Asserted here rather than worked around, so
    the interaction between the two requirements is pinned instead of discovered.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        app.store.save(MAP_ID, build_adjuntos(tmp_path))
        screen = await open_map(app, pilot, MAP_ID)
        assert_declared_layout(screen, rail=True, inspector=True)

        # E1b — nothing was ever submitted.
        assert screen.query_text == ""
        await pilot.press("n")
        await pilot.pause()
        declaration = toast_text(screen)
        await pilot.press("n")
        await pilot.pause()
        e1b = toast_text(screen)
        assert e1b != declaration

        # E1c — submitted, and it came back empty.
        await submit(pilot, ABSENT_QUERY)
        assert SearchIndex(screen.graph).query(ABSENT_QUERY) == [], (
            "the pinned absent query matches something; E1c is unreachable"
        )
        await pilot.press("n")
        await pilot.pause()
        e1c = toast_text(screen)

        # The declared strings, spelled here ON PURPOSE.  This table is the
        # specification (`UX-Q3-b`, `E1b`, `E1c`) and its whole value is that it
        # is not derived from the code it checks.
        e1b_title, e1b_body = "sin búsqueda activa", "no hay coincidencias que recorrer"
        e1c_title = "0 coincidencias"
        e1c_body = "«" + ABSENT_QUERY + "» no aparece en este mapa"

        assert e1b_title in e1b and e1b_body in e1b, e1b
        assert e1c_title in e1c and e1c_body in e1c, e1c

        # PAIRWISE, on both channels, from the frame.  One shared toast fails all
        # four of these.
        assert e1b_title not in e1c
        assert e1b_body not in e1c
        assert e1c_title not in e1b
        assert e1c_body not in e1b
        assert e1b != e1c


async def test_at_023_e1c_routes_the_operators_query_through_plain(tmp_path):
    """`E1c`'s body interpolates the query, so the toast is a COERCION SINK.

    Measured: `darkside.plain` strips a right-to-left override where
    `Text.assemble` leaves it alive -- and `Text.assemble` is what paints this
    toast.  An override inside the guillemets reverses the toast's own sentence
    on the operator's screen.

    THE HOSTILE CODE POINT IS BUILT FROM ITS NUMBER, never spelled into this
    file: the same rule `tests/test_inc3_census.py::hostile` follows, and the
    one the coercion census over tracked files enforces.

    ONE DELIBERATE DEPARTURE FROM "PRESS THE REAL CHORD", stated rather than
    hidden: an override has no Textual key name, so it cannot be typed through
    `pilot.press`.  The value is placed on the real `Input` and submitted with
    the real `enter`, so the whole shipped submit path still runs -- only the
    keystrokes that would produce the string are bypassed.
    """
    from textual.widgets import Input

    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        app.store.save(MAP_ID, build_adjuntos(tmp_path))
        screen = await open_map(app, pilot, MAP_ID)
        assert_declared_layout(screen, rail=True, inspector=True)

        hostile = ABSENT_QUERY + chr(0x202E) + "zz"
        # The control that makes this arm mean something: the constructor the
        # toast is actually built with does NOT strip the override, so a body
        # that reached the frame unrouted would carry it.
        assert chr(0x202E) in darkside.Text.assemble((hostile, "")).plain
        assert chr(0x202E) not in darkside.plain(hostile)
        assert SearchIndex(screen.graph).query(hostile) == []

        await pilot.press("slash")
        await pilot.pause()
        screen.query_one("#search-input", Input).value = hostile
        await pilot.press("enter")
        await pilot.pause()
        assert screen.query_text == hostile

        await pilot.press("n")   # consumes the one-time declaration
        await pilot.pause()
        await pilot.press("n")
        await pilot.pause()
        painted = toast_text(screen)
        assert "0 coincidencias" in painted, painted
        assert chr(0x202E) not in painted, "the override reached the painted toast"
        assert "«" + darkside.plain(hostile) + "»" in painted, painted


async def test_at_051_the_real_M_reaches_next_gap(tmp_path):
    """AT-051 — the RELOCATED chord is pressed, not merely declared.

    The whole-seat pin and `duplicate_chords()` are DECLARATION checks: they
    prove the seat says `M` is `next_gap`, and neither presses it.  A seat row
    can be correct while the action it names is unreachable.  The mutation this
    arm exists for is renaming the row while `MapScreen` still dispatches
    `next_gap` from `n`: the pins stay green and this fails.

    Scoped deliberately to DISPATCH.  `action_next_gap`'s own correctness is
    `AT-N04b`'s, already shipped, so the expectation here is computed from
    `_incomplete_order()` -- the same list the action consumes.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        app.store.save("legacy", install(tmp_path, "legacy"))
        screen = await open_map(app, pilot, "legacy")
        assert_declared_layout(screen, rail=True, inspector=True)

        order = screen._incomplete_order()
        assert order, "nothing is missing a required field; the arm is vacuous"
        before = screen.nav.cursor
        if before in order:
            expected = order[(order.index(before) + 1) % len(order)]
        else:
            expected = order[0]
        assert expected != before, "the target equals the start; nothing to observe"

        await pilot.press("M")
        await pilot.pause()
        assert screen.nav.cursor == expected, (before, screen.nav.cursor, order)


async def test_at_051_M_on_a_complete_map_says_so(tmp_path):
    """The other half of the relocated chord: it still reports full coverage."""
    from mapper.model import Edge, Ficha, Graph, Node

    graph = Graph()
    graph.add_node(Node(id="root", ficha=Ficha(title="raiz")))
    graph.add_node(Node(id="a", ficha=Ficha(title="alfa")))
    graph.add_edge(Edge("root", "a"))
    assert graph.schema == [], "a required field would make this map incomplete"

    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        app.store.save("complete", graph)
        screen = await open_map(app, pilot, "complete")
        assert screen._incomplete_order() == []
        await pilot.press("M")
        await pilot.pause()
        assert "cobertura completa" in toast_text(screen)


async def test_at_051b_the_rebind_is_declared_exactly_once(tmp_path):
    """AT-051b — the first `n` says the key changed hands; the second does not.

    `#D5b` took `n` from `next_gap`, and between this increment and Inc-8 the
    relocated chord is undiscoverable through `?` -- its `view` group sits below
    the legend's fold at the declared size.  An operator who presses `n`
    expecting the old behaviour has no painted route to the new one, and this
    toast is it.

    EVERY STRING IS READ FROM THE SEAT, never typed here: the declaration's only
    job is to name what is actually bound, and a typed expectation would keep
    passing after the next rebind moved it.

    "ONE-TIME" IS HALF THE CLAIM, and it is read from the FRAME TWICE.  A
    persistence store is not consulted: that would assert what the application
    believes rather than what it painted.
    """
    from mapper.keymap import bindings_for

    seat = {b.action: b for b in bindings_for("map")}
    assert {"next_hit", "next_gap"} <= set(seat), sorted(seat)

    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        app.store.save(MAP_ID, build_adjuntos(tmp_path))
        screen = await open_map(app, pilot, MAP_ID)
        assert_declared_layout(screen, rail=True, inspector=True)

        await pilot.press("n")
        await pilot.pause()
        first = toast_text(screen)
        # Names the new duty of `n` AND the new home of `next_gap`.
        assert seat["next_hit"].glyph in first, first
        assert darkside.plain(seat["next_hit"].label) in first, first
        assert darkside.plain(seat["next_gap"].label) in first, first
        assert seat["next_gap"].glyph in first, first

        await pilot.press("n")
        await pilot.pause()
        second = toast_text(screen)
        assert darkside.plain(seat["next_hit"].label) not in second, second
        assert second != first


async def test_at_053_esc_clears_a_live_search_and_stays_on_the_map(tmp_path):
    """AT-053 / `#D38` — `esc limpiar` is a promise the handler now keeps.

    Before this branch existed `action_back_or_home` popped the screen
    UNCONDITIONALLY while the hint line advertised `esc limpiar`, so an operator
    who followed the hint left the map.  Two arms that fail independently, and
    the second is the regression limb: without it the repair can break
    `back_or_home` altogether and stay green.
    """
    def hit_image(screen) -> str:
        style = f"{darkside.INK} on {darkside.STEP}"
        text = screen._current_renderer().render(
            screen.graph, screen._view_state(*screen._canvas_size())
        )
        return "".join(text.plain[s.start:s.end] for s in text.spans if s.style == style)

    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        app.store.save(MAP_ID, build_adjuntos(tmp_path))
        screen = await open_map(app, pilot, MAP_ID)
        assert_declared_layout(screen, rail=True, inspector=True)

        # ARM 1 -- a live search: `esc` clears it and the map STAYS.
        await submit(pilot, QUERY)
        assert COUNT_RE.search(count_region_text(screen)), "no count line to clear"
        assert hit_image(screen) != "", "nothing carries the hit style to begin with"
        assert "limpiar" in hint_text(screen), hint_text(screen)

        await pilot.press("escape")
        await pilot.pause()
        assert app.screen is screen, "esc popped the map out from under a live search"
        assert screen.query_text == ""
        assert COUNT_RE.search(count_region_text(screen)) is None, count_region_text(screen)
        assert hit_image(screen) == "", "a node still carries the hit style"

        # ARM 2 -- the REGRESSION limb.  With no search live, `esc` still leaves.
        await pilot.press("escape")
        await pilot.pause()
        assert app.screen is not screen, "esc no longer leaves the map"


async def test_p052_2_the_hint_line_reads_its_glyphs_from_the_seat(tmp_path):
    """`UX-Q3-b` — two limbs, and a hard-coded hint passes (a) and fails (b).

    Limb (a) is the declared string, verbatim, with the shipped seat.  Limb (b)
    moves the seat's glyph for `next_hit` and requires the repainted hint to
    follow it.  This increment is itself the proof the hazard is real: `n` meant
    `next_gap` one commit ago, and a hint that spelled it would still say so.
    """
    import dataclasses

    from mapper import keymap

    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        app.store.save(MAP_ID, build_adjuntos(tmp_path))
        screen = await open_map(app, pilot, MAP_ID)
        assert_declared_layout(screen, rail=True, inspector=True)

        # (a) the shipped seat, the declared string.
        await submit(pilot, QUERY)
        assert hint_text(screen) == "n siguiente · N anterior · esc limpiar"
        assert "n siguiente" in hint_rows(screen), hint_rows(screen)

        # ... and the empty-result variant, on the same surface.
        await submit(pilot, ABSENT_QUERY)
        assert hint_text(screen) == "sin coincidencias · esc limpiar"
        assert "sin coincidencias" in hint_rows(screen), hint_rows(screen)

        # (b) move the SEAT, and the painted hint must move with it.
        moved = [
            dataclasses.replace(b, glyph="»") if b.action == "next_hit" else b
            for b in keymap.KEYMAP
        ]
        assert [b.glyph for b in moved] != [b.glyph for b in keymap.KEYMAP], (
            "the monkeypatch changed nothing; limb (b) would pass on anything"
        )
        original = keymap.KEYMAP
        keymap.KEYMAP = moved
        try:
            await submit(pilot, QUERY)
            assert hint_text(screen).startswith("» siguiente · "), hint_text(screen)
        finally:
            keymap.KEYMAP = original

        await submit(pilot, QUERY)
        assert hint_text(screen) == "n siguiente · N anterior · esc limpiar"


def test_cd6a_the_walk_reads_exactly_one_resolution():
    """`C-D6a`, closed STRUCTURALLY (`#D37`) rather than asserted vacuously.

    The sealed invariant is "submitting a search clears the lens matches, and
    submitting a lens clears the search hits".  THERE IS NO LENS IN THIS BATCH
    (`#D23` defers US-N14 whole), so the only form that invariant can take here
    is "a field nothing ever writes is still empty" -- GREEN BEFORE ANY CODE IS
    WRITTEN, which is the vacuous check this batch exists to stop, landing on the
    very invariant that was meant to close a gap.

    So the mutant is made STRUCTURALLY UNAVAILABLE instead of undetected.
    `M-N07.3-a` is the walk written over two result sets joined by `or` with
    neither ever cleared; it passes `AT-022` whenever only one is populated,
    which is every single-feature test.  This arm reads the walk handler's AST
    and requires exactly ONE resolution source and NO boolean fallback.

    WHAT IS ACTUALLY ENFORCED, stated exactly, because the earlier wording
    ("cannot be expressed in the handler at all") claimed more than the code
    checks.  The teeth are `used == {"_search_order"}`: a second resolution
    named anywhere in this class's result-set vocabulary reddens it.  The
    `BoolOp` check is a COARSE SECOND BELT, not the rule -- a second set whose
    name misses the vocabulary regex and which is combined without `and`/`or`
    (tuple concatenation, `dict.fromkeys`, `itertools.chain`) satisfies both
    assertions.  So: the two NAMED shapes of `M-N07.3-a` are unavailable here,
    and an unnamed second set combined non-boolean-ly is not caught by this arm.
    The rule is not weakened for that -- it already caught a real `title or nid`
    fallback on its first run, and the fix was to lift the fallback into
    `_branch_name` rather than to allow it.

    THE VOCABULARY IS DERIVED FROM THE CLASS, not hand-listed: a hand-listed
    vocabulary of one member would make "exactly one" trivially true.
    """
    import ast
    import re

    cls = next(
        node
        for node in ast.walk(_app_tree())
        if isinstance(node, ast.ClassDef) and node.name == "MapScreen"
    )
    methods = {
        item.name: item
        for item in cls.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "_walk_hits" in methods, sorted(methods)

    def self_reads(node) -> set[str]:
        return {
            sub.attr
            for sub in ast.walk(node)
            if isinstance(sub, ast.Attribute)
            and isinstance(sub.value, ast.Name)
            and sub.value.id == "self"
        }

    # Every name on this class that could hold or produce a RESULT SET.  Note
    # `query_text` does not match, and must not: a query is not a result set, and
    # the walk legitimately reads it to tell "never asked" from "asked and empty".
    pattern = re.compile(r"hits|matches|search_order|search_memo|lens")
    vocabulary = {name for name in self_reads(cls) if pattern.search(name)}
    vocabulary |= {name for name in methods if pattern.search(name)}
    assert len(vocabulary) >= 3, (
        f"only {sorted(vocabulary)} could be a resolution source, so 'exactly "
        "one' is not a choice this class offers"
    )

    used = self_reads(methods["_walk_hits"]) & vocabulary
    assert used == {"_search_order"}, (
        f"the walk reads {sorted(used)}; it must read exactly one resolution, "
        "and `M-N07.3-a` is what a second one becomes"
    )

    fallbacks = [n for n in ast.walk(methods["_walk_hits"]) if isinstance(n, ast.BoolOp)]
    assert not fallbacks, (
        "the walk handler contains a boolean expression; `search_hits or "
        "lens_matches` is exactly the shape this forbids"
    )


async def test_the_walk_above_the_render_bound_declares_neither_zero_nor_silence(
    tmp_path, monkeypatch
):
    """The THIRD empty-ish state, which the sealed text never names.

    `_search_order` returns `None` above `MAX_RENDER_NODES` — Inc-4a's own
    distinction, and it was measured rather than imagined: with an empty order
    returned instead, the strip painted `0 coincidencias en el mapa` over a graph
    holding thousands of real matches.  The walk inherits that hazard the moment
    it grows an empty-result toast, because `E1c` says «q» NO APARECE EN ESTE
    MAPA — a claim about the graph that nobody evaluated.

    So the walk has a third branch, and this is its arm.  The bound is moved
    rather than a twelve-thousand-node fixture built: the branch is selected by
    `len(graph.nodes) > MAX_RENDER_NODES`, and moving either side of that
    comparison reaches the same code.  Building the graph would cost minutes per
    run to exercise one `if`.

    ALSO PINS THE HINT LINE, which is where the same conflation would land next:
    above the bound the hint must NOT read `sin coincidencias`.
    """
    import mapper.app as app_module

    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        graph = build_adjuntos(tmp_path)
        app.store.save(MAP_ID, graph)
        screen = await open_map(app, pilot, MAP_ID)
        assert_declared_layout(screen, rail=True, inspector=True)

        monkeypatch.setattr(app_module, "MAX_RENDER_NODES", len(graph.nodes) - 1)
        assert screen._search_order() is None, "the bound was not reached"
        # And the query DOES match on this graph, so "nothing was found" would be
        # false rather than merely unhelpful.
        assert SearchIndex(graph).query(QUERY), "the query matches nothing anyway"

        await submit(pilot, QUERY)
        assert hint_text(screen) != "sin coincidencias · esc limpiar", hint_text(screen)

        await pilot.press("n")   # consumes the one-time declaration
        await pilot.pause()
        await pilot.press("n")
        await pilot.pause()
        painted = toast_text(screen)
        assert "0 coincidencias" not in painted, painted
        assert "no aparece en este mapa" not in painted, painted
        assert "sin búsqueda activa" not in painted, painted
        assert str(len(graph.nodes) - 1) in painted, painted


async def test_esc_and_the_hint_line_agree_about_what_a_live_search_is(
    tmp_path, monkeypatch
):
    """`esc` may only act where the hint line advertised it (`#D38`, round 2).

    The two guards were written independently -- the hint asked for
    `query_text.strip() and order is not None`, `esc` asked for
    `query_text.strip()` alone -- and above the renderer's bound they disagreed.
    Measured there: the hint promises nothing, and yet the first `escape`
    cleared a query that was never painted, changed no pixel and did not leave
    the map.  A keypress silently swallowed is the INVERSE of the defect `#D38`
    exists to fix, and it is worse than the original in one way: `#D38`'s
    operator at least got a screen change.

    BOTH LIMBS ARE ASSERTED AND THEY FAIL SEPARATELY.  Below the bound the hint
    promises and `esc` must clear WITHOUT leaving; above it the hint promises
    nothing and `esc` must leave on the FIRST press.  A predicate that only
    checked the second limb is green on an `esc` that never clears at all.
    """
    import mapper.app as app_module

    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        graph = build_adjuntos(tmp_path)
        app.store.save(MAP_ID, graph)
        screen = await open_map(app, pilot, MAP_ID)
        assert_declared_layout(screen, rail=True, inspector=True)

        # LIMB 1 — below the bound.  The hint promises, so `esc` keeps the map.
        await submit(pilot, QUERY)
        assert "limpiar" in hint_text(screen), hint_text(screen)
        await pilot.press("escape")
        await pilot.pause()
        assert app.screen is screen, "esc popped the map out from under a live search"
        assert screen.query_text == ""

        # LIMB 2 — above the bound, reached the way `§1.6 C`'s own arm reaches
        # it.  The hint promises nothing, so `esc` must NOT act on the query.
        monkeypatch.setattr(app_module, "MAX_RENDER_NODES", len(graph.nodes) - 1)
        await submit(pilot, QUERY)
        assert screen._search_order() is None, "the bound was not reached"
        assert "limpiar" not in hint_text(screen), hint_text(screen)
        assert screen.query_text.strip(), "the query is gone; the limb is vacuous"

        await pilot.press("escape")
        await pilot.pause()
        assert app.screen is not screen, (
            "esc swallowed a keypress where the hint promised nothing: it "
            "cleared an unpainted query instead of leaving the map"
        )
