"""MapScreen's `search` concern as the `SearchingOps` mixin (searching.py).

Moved verbatim out of `screen.py` at `2026-10-09-modular-batch` Spine B; composed into
`MapScreen`. Never imports `mapper.app` (LLR-MOD.6.2).
"""

from __future__ import annotations

from mapper import darkside
from mapper.screens import CoverageScreen
from mapper.screens.common import (
    _QUERY_ECHO_CELLS,
    map_hint,
    SEARCH_ACTIVE_LABEL,
    SEARCH_COUNT_SUBJECT,
    SEARCH_SUSPENDED_NOTICE,
)
from mapper.search import SearchIndex
from mapper.views.layered import MAX_RENDER_NODES, overflow_phrase
from mapper.widgets.chrome import HintLine
from mapper.widgets.inspector import FichaInspector
from rich.text import Text
from textual.widgets import Input


class SearchingOps:
    """MapScreen's `search` concern (moved verbatim at 2026-10-09-modular-batch Spine B).

    A plain mixin composed into `MapScreen` (screen.py): it declares no BINDINGS, no
    DEFAULT_CSS and no `@on` handlers (Textual ignores them on a non-DOMNode base), and its
    method names are disjoint from every other concern's (LLR-MOD.2.1, LLR-MOD.2.2).
    """

    def _search_index(self) -> SearchIndex:
        """The owner of "what matches", CONSTRUCTED IN ONE PLACE.

        Extracted when `Inc-4c` gave the count region a second question to ask.
        `test_the_count_and_the_paint_share_one_resolution` censuses this
        module for `SearchIndex(...)` call sites and pins the total at one,
        deliberately: a second construction is how the strip's number and the
        canvas's highlight come to be computed from two owners that agree today
        and drift tomorrow.  `_whole_graph_tally` was that second site, and the
        arm reddened on it.

        THE ARM WAS RIGHT AND THE FIX IS TO SHARE, NOT TO EXEMPT.  The tally is
        only ever read where `_search_order` returned `None`, so no frame paints
        both -- but "these two cannot disagree because of when they run" is a
        REASONED argument, and this batch has three recorded cases of a reasoned
        agreement argument surviving a mutation that broke the property.  One
        constructor is a structural one.
        """
        return SearchIndex(self.graph)

    def _whole_graph_tally(self) -> int:
        """How many nodes match, over the WHOLE graph, WITHOUT ordering them.

        `HLR-N07.2`'s figure, reached by the cheap half of the owner.
        `SearchIndex.query` states `len(query(q)) == len(hits(q))` for every
        graph and says in as many words that the count line may be taken from
        either; this takes it from `hits` because that is the half the renderer's
        bound was never about.  Measured at 12002 nodes: 0.0075 s here against
        0.0122 s for the ordered form.

        DELIBERATELY NOT MEMOISED AND DELIBERATELY NOT NAMED LIKE A RESOLUTION.
        It is reached only from `_count_line`, once per strip build, and it
        returns an `int` rather than a result set -- so it is not a second
        answer to "what matches" that could drift from `_search_order`'s, which
        is the defect `C-D6a` and the single-resolution rule exist to prevent.
        The walk does not call it, and must not: `_walk_hits` is pinned by AST to
        exactly one resolution source, and a count read from a second place
        inside that handler is the shape its own arm warns can slip past the
        vocabulary regex.
        """
        return len(self._search_index().hits(self.query_text))

    def _query_echo(self) -> str:
        """The operator's query, coerced and BOUNDED, for the count region.

        Through `fit` for two separate reasons that happen to share a call.  The
        query is operator text on a surface this batch touches, so it is a
        coercion sink (`HLR-COERCE`) -- measured elsewhere in this file, a
        right-to-left override left alive reverses the sentence it sits in.  And
        it is unbounded in length on a region that WRAPS, so without a cell
        budget it grows the strip and takes rows from `#map-body`.

        THE CAP IS IN CELLS; THE DIMENSION THAT MATTERS IS ROWS, AND THE TWO
        ARE NOT THE SAME -- which is why the query is line-flattened BEFORE it
        is fitted.  `plain` deliberately preserves U+0009 and U+000A
        (`darkside.PRESERVED_CODE_POINTS`, and layout elsewhere depends on
        that), so 32 cells can be 32 ROWS.  Measured on the shipped surface at
        118x34 with a line-break-bearing query, before this flattening: the
        count region went to 32 rows, `#map-canvas` was crushed to 1, and the
        `esc limpiar` affordance left the painted frame entirely.  That is the
        `Inc-4b` collapse shape reproduced one surface over -- unbounded text
        taking the rows from `#map-body` and pushing the recovery affordance
        off-frame -- so the cap has to bound the row count, not the cell count,
        and `translate` is where it does.  The flattening is LOCAL TO THIS SINK
        on purpose: `plain` must keep both code points for the surfaces whose
        layout reads them.

        THE TABLE IS DERIVED FROM `PRESERVED_CODE_POINTS`, NOT RE-LISTED HERE.
        It used to spell the two code points again, which made this sink a silent
        DUPLICATE of the frozenset that decides them: a code point added there
        would keep being preserved by `plain` and stop being flattened here, and
        the row bound would reopen with every arm still green.  Reading the same
        owner means growth there is covered here by construction.

        WHY THIS REPO OWNS THAT GUARD RATHER THAN INHERITING IT.  No operator
        path on Textual 8.2.8 delivers U+000A into the `Input`: `enter` submits,
        and `Input._on_paste` takes `event.text.splitlines()[0]`.  The pin in
        `pyproject.toml` is exact, so that holds today -- but it is a
        third-party implementation detail with no documented guarantee, and the
        `Input` at the call site declares neither `max_length` nor `restrict`.
        A defence nothing here asserts is a defence a version bump removes in
        silence, so the guard is stated locally and
        `test_the_query_echo_bounds_rows_and_not_only_cells` pins OUR behaviour
        rather than Textual's.

        A FIXED CAP, AND THE FILE'S OWN PRECEDENT SAYS FIXED CAPS ARE WRONG --
        so this one is measured rather than reasoned.  `_HINT_BRANCH_CELLS`
        records a fixed 40 that fitted at 118 and wrapped at 80, and the budget
        there had to become the row's remainder.  THE TWO CASES DIFFER IN WHAT
        OVERFLOW COSTS: on `HintLine` a wrap pushed the affordances out of the
        painted frame, so the cap had to guarantee no wrap at all.  Here the
        region is the strip itself, `#map-body` is `height: 1fr` and absorbs the
        row, and predicate 1 only asks that the declaration be READABLE -- a
        two-row region is as readable as a one-row one.  What must not happen is
        UNBOUNDED growth, and 32 flattened cells bounds it.

        THE SWEPT EVIDENCE, CORRECTED -- AND THE CORRECTION IS "THIS NUMBER IS
        NOT STABLE", NOT A SECOND NUMBER.  An earlier revision claimed the extra
        row appeared at 60 and nowhere else.  Review swept the same band and
        found five widths (60, 65, 85, 90, 95).  Re-swept here on the shipped
        tree, same band, same step, at height 34 over the `adjuntos` fixture
        above the bound: NINE widths with length 1 against length 2000 (60, 65,
        70, 110, 115, 120, 125, 130, 135) and EIGHT with the six-character
        fixture against the same fixture plus 2000 (60, 65, 70, 115, 120, 125,
        130, 135).  Three measurements, three different width sets, because WHICH
        widths pay depends on how much of the row the rest of the strip has
        already spent -- the page numeral, the notice and the chord all scale
        with the fixture.  So the count of widths is NOT the load-bearing figure
        and is recorded here only to stop the next reader trusting one.

        WHAT IS STABLE ACROSS ALL THREE SWEEPS, and what the cap actually rests
        on: the delta is 0 or +1 at every width measured, never more; and the
        declaration is never taken off-frame.  That one row is the whole price of
        the fixed cap, and it is stated here rather than rounded off.

        A WIDTH-RELATIVE BUDGET WAS WRITTEN FIRST AND REMOVED.  It read
        `self.size.width`, which RAISES `NoActiveAppError` on a screen that is
        not mounted -- the way three unit arms in `test_search.py` reach this
        code -- so it made a pure string helper depend on being inside a running
        app.  It bought one row at the narrow end of the band.
        """
        return darkside.fit(
            self.query_text.translate(dict.fromkeys(darkside.PRESERVED_CODE_POINTS, " ")),
            _QUERY_ECHO_CELLS,
        ).rstrip()

    def _suspended_count_line(self) -> Text:
        """`LLR-N07.3.4` predicate 1 — the region above the renderer's bound.

        Four facts on one row: the query, the whole-graph count, the chord that
        still works, and what is suspended.  The chord's glyph is read FROM THE
        SEAT (`UX-Q3-b`'s one-declaration-four-readers rule), so a later rebind
        of `back_or_home` reaches this string without a second edit.

        WHICH CHORD IS NAMED, AND WHY IT IS NOT `n`.  `#D43`'s example wording
        names the walk (`n recorre`).  It is not painted here, because above the
        bound the walk DECLINES -- `_walk_hits` returns on `hits is None` -- and
        a region promising a chord the handler refuses is the `AT-052`/`AT-053`
        lying-affordance class this batch exists to close, reproduced by the fix
        for it.  What is painted instead is the chord that DOES work at this
        size, `esc`, plus a notice naming the walk among the suspended things.
        The clause's numeric threshold asks for the query, the count and the
        notice; all three are here.  The Statement's third clause is not
        satisfiable without either a second resolution source inside `_walk_hits`
        (forbidden by `test_cd6a`'s AST arm) or unpicking `_search_order`'s
        `None` (which `M-N07.3.4-a` presumes stays), and it is reported rather
        than quietly reinterpreted.
        """
        head = f"{SEARCH_ACTIVE_LABEL}: «"
        tail = (
            f"» · {self._whole_graph_tally()} {SEARCH_COUNT_SUBJECT} · "
            f"{self._seat_glyph('back_or_home')} clear · "
            f"{SEARCH_SUSPENDED_NOTICE}  "
        )
        return darkside.Text(
            f"{head}{self._query_echo()}{tail}", style=darkside.INK
        )

    def _count_line(self) -> Text:
        """`n/N coincidencias en el mapa` — HLR-N07.2, on the `#D37` strip.

        `N` is the WHOLE-GRAPH match count and comes from the search owner, not
        from `painted_ids` and not from anything that has seen `folded` or the
        pan offsets.  `n` is where the SELECTION sits inside that list, which is
        the only honest reading available: the walk that moves the selection
        between matches lands in the next increment, so `n` is `0` whenever the
        cursor is not itself a match, and it says so rather than reserving a
        placeholder numeral that would be a lie until the walk arrives.

        A query with no non-whitespace character paints NO LINE AT ALL
        (`LLR-N07.3.3`), which is also the state of a screen nobody has searched
        on yet -- and the two are the same state, so they paint the same way.
        `0 coincidencias en el mapa` means something different and is reserved
        for it: a question that was asked and came back empty.

        ABOVE THE RENDERER'S BOUND THE REGION DECLARES THE SEARCH ANYWAY
        (`LLR-N07.3.4`, `#D43`) -- AND THIS REVERSES WHAT `Inc-4b` SHIPPED HERE.
        Until `#D43` this branch returned an empty `Text`, on the argument that
        above the bound the question was never ANSWERED and `0 coincidencias`
        over a graph holding 6001 real matches is the lying affordance US-N07
        exists to remove.  The second half of that argument still stands and is
        why `0` is not what gets painted.  The FIRST half was wrong: the question
        can be answered cheaply, and the silence left the operator with a query
        that still changed what `n` did while no surface advertised it -- live
        enough to change a keypress, invisible enough to have no affordance.

        SO THE COUNT IS TAKEN FROM `hits`, NOT FROM `_search_order`, and that is
        the whole reason it is affordable.  `SearchIndex.query` documents
        `len(query(q)) == len(hits(q))` for every graph, so the figure is the one
        `HLR-N07.2` owns either way; what differs is the cost, and only the
        ORDERING was ever expensive.  Measured on a real 12002-node graph:
        `hits` 0.0075 s, `tree_order` 0.0097 s, `query` 0.0122 s.  The
        "seconds each, four resolutions per repaint" figure `_search_order`'s
        bound was argued from predates `tree_order`'s child-index repair and no
        longer holds -- so the bound now buys ~12 ms, and the argument for it is
        the RENDERER's (nothing is drawn, so no hit set is meaningful to it)
        rather than the search's.

        WHAT `_search_order`'s `None` NOW MEANS, restated because this branch is
        what gave it its old meaning.  It no longer means "nobody asked": the
        count line asks at every size.  It means the ORDER was not resolved, so
        no highlight is painted and no walk is available -- which is exactly what
        `SEARCH_SUSPENDED_NOTICE` says on the same row.

        THE SUSPENSION NOTICE IS THE LOAD-BEARING HALF, not decoration.  A live
        count over an unlit canvas with no stated reason trades one hidden state
        for another, and `M-N07.3.4-b` is precisely the mutant that paints the
        count and drops the notice.

        Below the bound nothing here changed: `n/N`, the reserved `0`, and the
        offset `LLR-N07.3.2` asks for are all as `Inc-4a` shipped them.  Because
        everything painted before this point on the strip has a fixed width for
        a given graph, the count begins at the SAME offset whether it reads `0`
        or `3/5`.

        The tone is deliberately uniform.  `LLR-N07.3.2`'s empty-state TONE ships
        with the query chip, the hint line and the two toasts in the increment
        that owns them; painting a tone split here that nothing observes would
        be shipping an unobserved behaviour on a green suite, which is the exact
        failure this batch is spending its budget to stop.
        """
        if not self.query_text.strip():
            return darkside.Text("")
        hits = self._search_order()
        if hits is None:
            return self._suspended_count_line()
        if not hits:
            return darkside.Text(f"0 {SEARCH_COUNT_SUBJECT}  ", style=darkside.INK)
        at = hits.index(self.nav.cursor) + 1 if self.nav.cursor in hits else 0
        return darkside.Text(
            f"{at}/{len(hits)} {SEARCH_COUNT_SUBJECT}  ", style=darkside.INK
        )

    def _pagination_text(self) -> Text:
        total = len(self.graph.nodes)
        page = 1
        per_page = max(1, total)
        # For now the tree is not paginated; this reserves the affordance.
        #
        # SUPERSEDED BY `Inc-STRIPS` -- THE METER IS BOUNDED NOW, and the block
        # below is kept because it records how the bound was arrived at.  Read
        # it as history: every sentence in it was true of the tree it was
        # written against and the first two are false of this one.  An earlier
        # revision of THIS increment claimed to have corrected it in place and
        # had not; the confirmation pass caught the packet asserting a byte
        # -identical block had changed, which is the same defect one register up.
        #
        # HISTORICAL, from the pre-bound tree:
        # THE METER IS STILL UNBOUNDED HERE, DELIBERATELY, AND BOUNDING IT IS
        # NECESSARY BUT NOT SUFFICIENT.  An earlier revision of this comment said
        # a cap "would not have helped"; that was wrong and is corrected here
        # rather than deleted, because a reader who trusts it bounds the minimap
        # alone and the count is still unreadable.  The meter prices one glyph
        # per node, so on a real 12002-node graph this region renders 104 rows
        # and is laid out at y=42 of a 34-row frame.  A 24-step cap was written
        # and measured: it takes the region to 2 rows but it is still laid out at
        # y=55, because `#map-minimap` is `height: auto` over the root's 4001
        # children and renders 668 rows on its own -- which also crushes
        # `#map-canvas` to a single row.  THE CONVERSE CONTROL WAS ALSO MEASURED,
        # minimap hidden and meter left unbounded: at 80x24 ALL 21 visible rows
        # are meter glyphs and the count is still off-screen, and at 118x34 the
        # same control yields 31 readable rows with the count on the last.  So
        # the minimap and the meter are INDEPENDENT causes and each alone is
        # enough to hide the count; the remedy bounds the minimap, the meter and
        # the overflow declaration TOGETHER.  That is a layout collapse across
        # three unbounded strips, not a defect of the count line, and it is
        # reported for its own increment rather than half-fixed from inside this
        # one.  See `increment-004c.md`, finding F-2 and its round-2 section.
        # THE METER IS BOUNDED HERE, and the numerals beside it carry the truth
        # the bar can no longer carry.  Priced one glyph per node it rendered
        # 12002 cells on a real large graph; capped at `METER_STEPS` it is one
        # row at every declared width.  Past the cap the bar stops being a
        # one-to-one scale and becomes a compressed one -- which is why
        # `page/per_page` is printed next to it and is NOT capped: the reader
        # who needs the exact figure reads the numerals, not the blocks.
        steps = min(per_page, self.METER_STEPS)
        filled = min(page, steps)
        text = darkside.Text.assemble(
            (" ", ""),
            darkside.step_meter(filled, steps),
            (f"   {page}/{per_page}  ", darkside.MUT),
        )
        text.append(self._count_line())
        # HLR-N06.3 on the strip beside the canvas, from the SAME `painted_ids`
        # pass the renderer used, so the two surfaces cannot declare different
        # totals.  `None` means a view that declares nothing, and the strip then
        # keeps only its reserved-affordance content.
        #
        # A BROKEN DECLARATION GETS ITS OWN WORDS, NOT SILENCE (`AT-058`).
        # `_painted_ids_for` RAISES for a renderer with no entry, and that raise
        # must not escape: this runs inside the message pump, and `TC-R08`
        # requires `refresh_canvas` to survive ANY renderer exception -- tests
        # and future code substitute renderers at runtime, and identity dispatch
        # cannot tell a substituted renderer from a forgotten one.  So the raise
        # is CAUGHT HERE and turned into a DIFFERENT OBSERVABLE.  Falling back to
        # silence instead would be the exact collision `AT-058` exists to break:
        # `LLR-N06.3.3` makes silence mean "nothing is hidden".
        try:
            hidden = self._unpainted_ids()
        except LookupError:
            text.append("hidden-node count unavailable ", style=darkside.INK)
            return text
        if hidden:
            # ONE SPELLING, consumed rather than repeated (`F7`).  This copy
            # already differed from the two renderers' -- same words, different
            # padding -- which is how a triplicated sentence starts drifting.
            text.append(f"{overflow_phrase(len(hidden))} ", style=darkside.INK)
        return text

    def _search_order(self) -> tuple[str, ...] | None:
        """The live hits, over the WHOLE graph, in tree order.  `None` above the
        renderer's bound, where no order is resolved.

        WHAT `None` MEANS WAS NARROWED BY `LLR-N07.3.4` (`#D43`).  It used to
        mean "the question was not asked", and `_count_line` painted nothing on
        it.  The count region now asks at every graph size -- through
        `_whole_graph_tally`, which is the cheap half of the same owner -- so
        `None` means only that the ORDER was not resolved: no highlight is
        painted and no walk is available.  Every consumer below still reads it
        the same way; what changed is that a fourth surface stopped inferring
        "nobody asked" from it.

        THE SINGLE RESOLUTION ON THIS SCREEN.  The count line and the hit set
        the renderer paints from both come from here, and `_search_hits` is
        derived from it rather than resolved beside it -- deliberately, and the
        cost of the alternative was measured rather than imagined.  An earlier
        revision of this increment let the count line call the owner itself
        while `_view_state` called it separately; the two agreed, but nothing
        made them, and a mutation that scoped ONE of them to the visible set
        left the other correct and the acceptance green.  Two paths to "what
        matches" is the exact defect US-N07 exists to close, reproduced inside
        the screen that closes it.

        `MapScreen.folded` and `pan_x`/`pan_y` are not consulted and must never
        be: a count taken over what is on screen is risk A-6, and US-N06 ships
        fold in this same batch, so a viewport-scoped count would ACTIVELY
        CREATE the defect this story exists to close.

        THE BOUND IS THE RENDERER'S OWN, AND OBEYING IT IS THE POINT.  Above
        `MAX_RENDER_NODES` the renderer returns its overflow declaration without
        evaluating anything, so ordering a tree the app has already declared it
        will not draw buys nothing.  Search stops where drawing stops.

        THE COST FIGURE THIS BOUND WAS ARGUED FROM NO LONGER HOLDS, and saying so
        is the point of this paragraph.  `Inc-4a` justified the bound on "seconds
        each, three to four resolutions per repaint"; that measurement predates
        `tree_order`'s child-index repair, which took the walk from `O(N*E)` to
        `O(E)`.  RE-MEASURED at 12002 nodes for `Inc-4c`: `hits` 0.0075 s,
        `tree_order` 0.0097 s, `query` 0.0122 s.  So the bound is worth about
        12 ms per resolution, not seconds, and what still justifies it is the
        RENDERER's argument -- nothing is drawn, so no hit set is meaningful to
        it -- rather than the search's.  The figure is corrected here rather than
        left standing because a justification that names a mechanism which has
        since been repaired is how a later reader deletes the right guard.
        `S-15` observed that this bound limits the render COUNT and not the WORK;
        this closes the instance, not the underlying observation.

        AND "DECLARES NOTHING" IS RETURNED AS `None`, NEVER AS AN EMPTY ORDER.
        The first revision of this bound returned an empty order, which
        `_count_line` cannot tell from a question that came back empty -- so at
        12002 nodes it painted `0 coincidencias en el mapa` over a graph holding
        241 real matches.  An unanswered question and an answer of zero are
        different facts, they are gated by different arms, and the type is what
        keeps them apart.

        THE ORDER HANDED OUT IS IMMUTABLE.  It was the memo's own list, so a
        consumer that sorted or trimmed what it received corrupted every later
        read in the same pass.  No shipped consumer does; `Inc-4b`'s next-match
        walk is the plausible first, and `ViewState.hits` is a `frozenset` one
        layer up for exactly this reason, so the two decisions now agree.

        THE MEMO IS SCOPED TO ONE PAINT PASS AND CANNOT GO STALE.  Three to four
        consumers reach this helper per repaint (`_view_state` from the render
        and again from `_unpainted_ids`, plus `_count_line`), and each used to
        resolve from scratch.  `_open_paint_pass` drops the memo at the START of
        every repaint, so the only way to read a stale order is to have already
        painted a stale screen -- and the memo is keyed on the graph OBJECT and
        the query text, so switching maps mid-pass cannot alias either.
        """
        if len(self.graph.nodes) > MAX_RENDER_NODES:
            return None
        memo = self._search_memo
        if memo is not None and memo[0] is self.graph and memo[1] == self.query_text:
            return memo[2]
        order = tuple(self._search_index().query(self.query_text))
        self._search_memo = (self.graph, self.query_text, order)
        return order

    def _search_hits(self) -> frozenset[str]:
        """The same resolution, in the shape a renderer receives.

        The bound's `None` and an empty order collapse to the same empty set
        HERE and only here, which is correct for this consumer and is not a
        reintroduction of the conflation `_count_line` had to unpick: above the
        bound the renderer paints no tree at all, so a hit set that highlights
        nothing is the truthful parameter.  The distinction matters only where
        something is DECLARED about the answer, which is the count line.
        """
        return frozenset(self._search_order() or ())

    def action_search(self) -> None:
        inp = self.query_one("#search-input", Input)
        inp.disabled = False
        inp.display = True
        inp.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search-input":
            self.query_text = event.value
            event.input.display = False
            event.input.disabled = True
            self.focus()
            self.refresh_canvas()
            # AFTER the repaint, deliberately: the hint then describes the
            # frame the operator is now looking at, and the order it reads is
            # the one `refresh_canvas` just resolved rather than a second
            # resolution beside it.
            #
            # `None` IS NO LONGER EXCLUDED HERE (`LLR-N07.3.4`).  Above the
            # renderer's bound a query is live and `esc` clears it, so the hint
            # has an affordance to promise; `_search_hint` grew the third arm
            # that says what is suspended instead of `sin coincidencias`, which
            # would declare an empty answer over a graph that may hold thousands
            # of matches.  The guard below is the shared predicate, which now
            # asks about the QUERY -- so the blank query is still excluded and
            # the bound no longer is.
            order = self._search_order()
            if self._search_is_live():
                self.query_one(HintLine).set_hint(self._search_hint(order))
            else:
                self.query_one(HintLine).set_hint(map_hint())

    def on_input_blurred(self, event: Input.Blurred) -> None:
        if event.input.id == "search-input":
            event.input.display = False
            event.input.disabled = True
            self.focus()

    def _search_is_live(self) -> bool:
        """What BOTH `esc` and the hint line mean by "a search is live".

        ONE PREDICATE, BOTH CALLERS -- unchanged from `Inc-4b`.  WHAT IT READS
        CHANGED (`LLR-N07.3.4`, `#D43`), and this reverses `Inc-4b`'s version.

        It used to be `query_text.strip() and _search_order() is not None`, so
        above the renderer's bound it answered `False` and `esc` popped the
        screen on the first press.  Both gates approved that ON THE PREMISE that
        nothing was painted to clear.  `#D43` rejects the premise: the count
        region now declares the query at every graph size, so there IS something
        to clear, and a chord whose meaning varies with the size of the map is a
        lying affordance with extra steps -- the operator learns a rule that
        silently stops holding on a large map, and learns it by losing their
        place.

        SO IT READS THE QUERY, WHICH IS THE STATE, AND NOT THE RESOLUTION, WHICH
        IS A RENDERING DETAIL.  `M-N07.3.4-a` is exactly this method left reading
        the resolution while the region is taught to declare the query, and the
        acceptance reddens it by asserting `esc` across BOTH regimes in one node.

        It no longer reaches the search resolution at all, which is why it and
        `action_back_or_home` were REMOVED from `test_search.py`'s
        `_PASS_FREE_READERS` rather than left there: that arm pins its set in
        both directions, and a stale exemption fails it.
        """
        return bool(self.query_text.strip())

    def _unfold_onto(self, nid: str) -> list[str]:
        """Open every folded branch that hides *nid*; return what was opened.

        `LLR-N06.2.4`.  Landing the selection inside a fold moves it somewhere
        the operator cannot see, which is the silent state change US-N06
        forbids.  The branch is NOT re-closed when the walk moves past it: that
        would undo, unasked, the only thing that made the previous step legible.
        The child index is built once for the same reason `search.tree_order`
        builds one -- `Graph.children_of` is a full scan of `graph.edges`.
        """
        if not self.folded:
            return []
        kids: dict[str, list[str]] = {}
        for edge in self.graph.edges:
            kids.setdefault(edge.parent_id, []).append(edge.child_id)
        opened: list[str] = []
        for start in sorted(self.folded):
            seen: set[str] = set()
            stack = list(kids.get(start, ()))
            while stack:
                cid = stack.pop()
                if cid in seen:
                    continue
                seen.add(cid)
                stack.extend(kids.get(cid, ()))
            if nid in seen:
                opened.append(start)
        self.folded = self.folded - set(opened)
        return opened

    def _branch_name(self, nid: str) -> str:
        """What the hint line calls a branch: its title, or its id if it has none.

        Lifted out of `_walk_hits` rather than written inline, and the reason is
        mechanical: the acceptance asserts BY AST that the walk handler contains
        no boolean expression, because `search_hits or lens_matches` is the shape
        `M-N07.3-a` takes.  A `title or nid` fallback is harmless and is the same
        shape, so it lives here instead of weakening the rule to allow it.

        Through `plain()`: the title is file-derived and the hint line is a
        surface this batch touches (`HLR-COERCE`).

        The `.get` is not defensive padding: a folded id that is an edge parent
        with no `Node` entry raises `KeyError` on the keypress, and while the
        shipped loader synthesises a node for every `.mmd` edge endpoint (so no
        FILE reaches it), the fold set is keyed on ids, not on nodes.  Falling
        through to the id arm costs one call and removes a crash from a path
        that has no other error handling.
        """
        node = self.graph.nodes.get(nid)
        title = node.ficha.title if node else ""
        if title:
            return darkside.plain(title)
        return darkside.plain(nid)

    def _walk_hits(self, step: int) -> None:
        """Move the selection to the next (or previous) match, wrapping both ways.

        ONE SOURCE OF "WHAT MATCHES", AND NO FALLBACK (`C-D6a`).  The order comes
        from `_search_order` and from nowhere else.  The named weaker variant
        `M-N07.3-a` is this walk written over two result sets joined by `or`
        with neither ever cleared: it passes `AT-022` whenever only one of them
        is populated -- which is every single-feature test -- and the two diverge
        silently the first time an operator uses both.  There is no second set in
        this batch (`#D23` defers the lens), so the invariant "submitting a
        search clears the lens matches" would be GREEN BEFORE ANY CODE WAS
        WRITTEN, which is the vacuous check this batch exists to stop.  It is
        closed STRUCTURALLY instead: this method reads exactly one resolution and
        contains no boolean fallback, and `test_search.py` asserts both BY AST.
        What that buys, stated exactly: the two NAMED shapes of `M-N07.3-a` are
        structurally unavailable here rather than merely undetected.  It is not
        a proof that no second result set can exist -- one named outside the
        arm's vocabulary and joined by concatenation would satisfy both
        assertions.

        THE ORDER IS THE ONE THE FRAME ON SCREEN WAS PAINTED FROM.  `_search_order`
        is memoised per paint pass and keyed on the graph object and the query
        text, and a walk changes neither, so the memo of the last frame is the
        same value a fresh resolution would return.  The repaint that follows
        opens its own pass; this method is registered in the acceptance's
        exemption table with that reason rather than opening one of its own.
        """
        hits = self._search_order()
        declaring = not self._rebind_declared
        self._rebind_declared = True
        if not self.query_text.strip():
            # `E1b` -- nothing was ever asked.  A blank or whitespace-only query
            # is the SAME state (`LLR-N07.3.3`) and the count line already paints
            # the two identically.  The body reports the STATE rather than
            # prescribing the `/` route: `#D6` made the route conditional, so a
            # body naming it is accidentally true today and misdirection the
            # increment a second producer lands.
            self._walk_toast(
                declaring,
                "no active search",
                "no matches to step through",
            )
            return
        if hits is None:
            # Above the renderer's bound.  `E1c`'s body here would declare "no
            # aparece en este mapa" over a graph that may hold thousands of
            # matches, which is why this branch exists at all.
            #
            # THE LABEL WAS `búsqueda sin evaluar` AND IS NOW FALSE
            # (`LLR-N07.3.4`, which is the clause that finally OWNS this string).
            # The count region evaluates the search at every graph size now and
            # paints the whole-graph figure, so a toast saying the search was not
            # evaluated contradicts the row above it.  What is actually suspended
            # is the thing the operator just asked for -- the walk -- and that is
            # what the toast now names, in the same words
            # `SEARCH_SUSPENDED_NOTICE` uses on the region.
            #
            # THE COUNT IS DELIBERATELY NOT REPEATED HERE.  The region carries it
            # persistently, which is the point of `#D43`; a toast that repeated
            # it would be a second surface making the same claim, and reading it
            # would mean calling a counter from inside the one handler `C-D6a`
            # pins by AST to a single resolution source.
            self._walk_toast(
                declaring,
                "walk suspended",
                f"the map exceeds the limit of {MAX_RENDER_NODES} nodes",
            )
            return
        if not hits:
            # `E1c` -- asked, and answered empty.  The body interpolates the
            # OPERATOR'S query, which makes this toast a coercion sink: measured,
            # `darkside.plain` strips a control byte and a right-to-left
            # override where `Text.assemble` leaves the override alive, and an
            # override reverses the toast's own sentence.
            self._walk_toast(
                declaring,
                "0 matches",
                f"«{darkside.plain(self.query_text)}» is not in this map",
            )
            return
        if self.nav.cursor in hits:
            index = (hits.index(self.nav.cursor) + step) % len(hits)
        else:
            index = 0 if step > 0 else len(hits) - 1
        target = hits[index]
        opened = self._unfold_onto(target)
        self.nav.cursor = target
        self.refresh_canvas()
        line = self.query_one(HintLine)
        line.set_hint(self._hint_with_opened(self._search_hint(hits), opened, line.size.width))
        if declaring:
            self._declare_rebind()

    def action_next_hit(self) -> None:
        self._walk_hits(1)

    def action_prev_hit(self) -> None:
        self._walk_hits(-1)

    def action_coverage(self) -> None:
        def on_select(node_id: str | None) -> None:
            if node_id is None or node_id not in self.graph.nodes:
                return
            self._goto_gap(node_id)

        self.app.push_screen(CoverageScreen(self.graph, self.map_id), callback=on_select)

    # -- coverage worklist (US-N04) ----------------------------------------
    def _incomplete_order(self) -> list[str]:
        """Nodes with a missing required field, in the coverage report's order.

        Walks the tree the same way `CoverageScreen` does, so "next" in the
        worklist means the same thing as "next row" in the report.  Consumes
        `Ficha.missing_required`, the model's single owner of what is missing.
        """
        out: list[str] = []
        if self.graph.root_id is None:
            return out
        visited: set[str] = set()
        stack = [self.graph.root_id]
        while stack:
            nid = stack.pop()
            if nid in visited or nid not in self.graph.nodes:
                continue
            visited.add(nid)
            if self.graph.nodes[nid].ficha.missing_required(self.graph.schema):
                out.append(nid)
            for cid in reversed(self.graph.children_of(nid)):
                if cid not in visited:
                    stack.append(cid)
        return out

    def _goto_gap(self, node_id: str) -> bool:
        """Move the cursor to *node_id* and focus its first missing field."""
        if node_id not in self.graph.nodes:
            return False
        self.nav.cursor = node_id
        if self.inspector_hidden:
            self.inspector_hidden = False
            self._apply_region_visibility()
        # Ask for the focus BEFORE refreshing: the inspector applies the request
        # at the end of the rebuild that creates the rows, so the two are ordered
        # causally instead of racing on frame timing.
        missing = self.graph.nodes[node_id].ficha.missing_required(self.graph.schema)
        inspector = self.query_one("#map-inspector", FichaInspector)
        inspector.focus_after_rebuild(missing[0].key if missing else None)
        self.refresh_canvas()
        if missing:
            # The save key is READ FROM THE SEAT (LLR-005.2): `↵` keeps the draft
            # and leaves the field (R7), so naming it here would advertise a save
            # that does not happen -- the defect US-N03 exists to remove.
            save = self._seat_glyph("save_draft")
            self.query_one(HintLine).set_hint(
                f"fill in «{missing[0].label}» · {save} {self._seat_label('save_draft')}"
                " · esc leave field",
                save,
            )
        return True

    def action_next_gap(self) -> None:
        """Advance to the next node that is missing a required field.

        Wraps once.  When nothing anywhere is missing it says so, rather than
        cycling silently on the same node forever.
        """
        order = self._incomplete_order()
        if not order:
            self._event_toast("coverage complete", "no required field is missing")
            return
        if self.nav.cursor in order:
            idx = (order.index(self.nav.cursor) + 1) % len(order)
        else:
            idx = 0
        self._goto_gap(order[idx])
