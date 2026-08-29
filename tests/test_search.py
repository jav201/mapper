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
