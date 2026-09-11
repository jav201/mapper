"""Outline (indented text) renderer."""
from __future__ import annotations

from rich.console import Console
from rich.text import Text

from mapper import darkside
from mapper.model import Graph
from mapper.views.layered import OVERFLOW_TOKEN, _clip
from mapper.views.state import ViewState


# Declared rendering bound, chosen from measurement, not taste.  This renderer
# is the one that sets it: its per-line indent is quadratic in depth, so a deep
# chain measured 0.26 s at 12000 nodes and 1.01 s at 24000.  See radial.py's
# note; a test keeps the three values in step.
MAX_RENDER_NODES = 12000


# The compression marker.  A capped indent MUST NOT LIE ABOUT DEPTH: it carries
# the TRUE level, so a deep chain reads as deep rather than as shallow.  What the
# operator sees may compress; what it asserts stays true -- `PHYS-3`'s spirit,
# and the condition attached to the ruling that licensed the cap.
DEPTH_MARK = "⇲"


def _indent(level: int, budget: int) -> str:
    """The row's indent, bounded by GEOMETRY and declaring its own compression.

    UNBOUNDED BEFORE `S-B(+C)`: this returned `"  " * level`, quadratic in depth
    across a walk.  MEASURED -- at depth 4000 the leaf's indent alone is 7,998
    cells into a canvas 118 wide, and the walk BUILDS 15,996,000 indent
    characters against 468,460 capped, 34.1x.  With `MAX_RENDER_NODES = 12000`
    the worst admissible chain builds ~144 million.  `rail.py` had already fixed
    this exact shape.

    CAPPING IS SAFE FROM PAN, CHECKED RATHER THAN ASSUMED: this module reads
    neither `pan_x` nor `pan_y`, so cells past the canvas width are unreachable
    here.  `rail.py`'s licence to cap came from its fixed width and absent pan,
    and such a licence does not transfer by resemblance.

    THE CAP IS NOT COST-ONLY, AND THAT WAS RULED RATHER THAN DECIDED HERE.
    `_fit` prices rows PHYSICALLY, so a shorter row occupies fewer physical rows
    and `_fit` keeps MORE of them -- the picture and the declared hidden count
    both move.  Coordinator ruling 2026-09-11 took that deliberately: a
    depth-4000 chain spending 69 physical rows to show one logical row is
    pathology wearing fidelity's name.

    `budget` is DERIVED from the render width by the caller, never a constant
    (`B-61`).
    """
    if 2 * level <= budget:
        return "  " * level
    run = max(0, budget - len(str(level)) - 1)
    return " " * run + f"{DEPTH_MARK}{level} "


def _child_index(graph: Graph) -> dict[str, list[str]]:
    """Adjacency built once. Graph.children_of rescans every edge per call."""
    index: dict[str, list[str]] = {}
    for edge in graph.edges:
        index.setdefault(edge.parent_id, []).append(edge.child_id)
    return index


def _degraded(n: int) -> Text:
    """Declared degradation: naming what was dropped beats raising."""
    out = Text()
    out.append("◆ ", style=darkside.INK)
    out.append("mapper", style=darkside.WORDMARK)
    out.append(" · outline", style=darkside.MUT)
    out.append(chr(10) * 2)
    out.append(
        f"mapa de {n} nodos: supera el límite de {MAX_RENDER_NODES} nodos. "
        "Se omitió el listado de nodos y los conteos por rama.",
        style=darkside.WARN,
    )
    return out


def _header_line() -> Text:
    """This renderer's header, built in ONE place -- `_rows` and `header_rows`.

    Extracted for the reason `layered` records at its own header: the charge and
    the paint must come off the same helper, or there are two copies of the
    header's shape and they drift.  `_degraded` builds its own banner and is
    deliberately NOT routed through here: it is a different line on a frame that
    has no rows to fit, and folding them would make this helper answer for two
    shapes at once.
    """
    out = Text()
    out.append("◆ ", style=darkside.INK)
    out.append("mapper", style=darkside.WORDMARK)
    out.append(" · outline", style=darkside.MUT)
    return out


def header_rows(graph: Graph, w: int, wrap_w: int) -> int:
    """PHYSICAL rows THIS renderer's first line occupies at `wrap_w`.

    `MapScreen._canvas_size` used to charge `layered.header_rows` in every view,
    including this one, and the two headers are not the same line: layered's is a
    wordmark plus a coverage meter plus an overflow declaration, this one is
    `◆ mapper · outline`.  MEASURED over a ten-width sweep from 20 to 118,
    layered's charge exceeds this renderer's own first line by TWO rows at
    widths 20..28 and by ONE at 34 and above -- at EVERY width in the sweep.
    Each overcharged row is a body row the region could have shown and the
    renderer was never told about.

    The signature matches `layered.header_rows` exactly so `_canvas_size` can
    dispatch on the renderer without special-casing either shape.  `graph` and
    `w` are unused HERE because this header is a fixed string rather than a
    graph-derived meter -- they are not dropped from the signature, because the
    caller must be able to treat every view's charge identically and a narrower
    signature would put that branch back at the call site.

    RENDERED, NOT DIVIDED (`B-61`).  The same `Console.render_lines` instrument
    `_fit` uses, because Rich WORD-WRAPS and a `ceil(cells / w)` formula prices a
    line short of the wrap the widget actually performs.  A long-enough header
    would take two rows here too, which is why this measures rather than
    returning the 1 the sweep happens to show.
    """
    console = Console(width=max(1, wrap_w))
    return max(1, len(console.render_lines(_header_line(), pad=False)))


def _rows(
    graph: Graph, state: ViewState
) -> tuple[list[tuple[str | None, Text]], Text | None]:
    """Every line this renderer would emit, paired with the node it shows.

    THE ONE PASS BOTH `render` AND `painted_ids` CONSUME.  Two passes would be
    two definitions of "painted", and `B-60` is exactly what that costs: the
    canvas and the strip declaring different totals for the same frame.

    Returns `(rows, short_circuit)`.  `short_circuit` is a finished renderable
    for the frames that have no rows to fit -- no map loaded, or a graph past
    the render bound.
    """
    selected_id = state.selected_id
    # RESOLVED ids, decided by `mapper.search` (HLR-N07.1).  This renderer
    # evaluates no query predicate of its own -- it never sees the query.
    hits = state.hits
    rows: list[tuple[str | None, Text]] = []
    rows.append((None, _header_line()))

    if graph.root_id is None:
        rows.append((None, Text("(no map loaded)")))
        return rows, Text("\n").join(t for _n, t in rows)
    if len(graph.nodes) > MAX_RENDER_NODES:
        return [], _degraded(len(graph.nodes))

    index = _child_index(graph)

    def subtree_counts() -> dict[str, tuple[int, int]]:
        """(nodes, sin acta) per subtree, one memoised post-order pass.

        The shipped version re-walked the whole subtree for every internal
        node, which is quadratic and is why a deep map never finished.

        visiting is the active path.  Recursion answered a cyclic graph
        with a RecursionError, which the screens catch; a plain loop would
        answer it by never returning, and a hang is worse than a crash.
        """
        own = {
            nid: 0 if node.ficha.fields.get("D", "").strip() else 1
            for nid, node in graph.nodes.items()
        }
        counts: dict[str, tuple[int, int]] = {}
        visiting: set[str] = set()
        stack: list[tuple[str, bool]] = [(graph.root_id, False)]
        while stack:
            nid, expanded = stack.pop()
            if expanded:
                visiting.discard(nid)
                total = 1
                missing = own.get(nid, 1)
                for cid in index[nid]:
                    ct, cm = counts[cid]
                    total += ct
                    missing += cm
                counts[nid] = (total, missing)
                continue
            if nid in counts:
                continue
            if nid in visiting:
                raise ValueError(f"cycle through {nid}: the graph is not a tree")
            children = index.get(nid)
            if not children:
                counts[nid] = (1, own.get(nid, 1))
                continue
            visiting.add(nid)
            stack.append((nid, True))
            stack.extend((c, False) for c in children if c not in counts)
        return counts

    # Runs before walk, so walk never meets a cyclic graph.
    totals = subtree_counts()

    # BOTH CAPS DERIVED FROM THE FRAME, NEVER SPELLED (`B-61`).
    #
    # `indent_budget` -- half the render width.  An indent allowed to fill the
    # width would leave no cells for the title it is indenting, so the row would
    # cost everything and say nothing.
    #
    # `row_cap` -- one whole frame.  A row longer than `w * h` cannot be shown
    # ENTIRELY by any frame of this size, so that is the widest slice worth
    # building; beyond it the renderer was constructing text to wrap, price and
    # discard.  MEASURED: a 400,000-character title built a 400,004-cell row and
    # 3,390 physical rows before `_fit` dropped it.
    indent_budget = max(2, state.w // 2)
    row_cap = max(state.w, state.w * state.h)

    def walk(nid: str, depth: int) -> None:
        stack = [(nid, depth)]
        while stack:
            cur, lv = stack.pop()
            node = graph.nodes[cur]
            prefix = _indent(lv, indent_budget) + ("- " if lv else "")
            line = Text()
            # B-47 / A-89: this renderer reaches `export.save_svg` through
            # `MapScreen.action_export_svg` exactly as the layered one does,
            # and it coerced nothing -- measured, a hostile title through it
            # writes an SVG that is not well-formed XML.  The guarantee
            # `AT-009` asserts held only in radial view.
            # `_clip`, NOT a second truncator: it is the ellipsis idiom already
            # in this family, and it calls `darkside.plain` itself, so THE
            # COERCION THIS LINE USED TO DO EXPLICITLY IS NOT LOST.  That -- the
            # title path being coerced AT ALL -- is the load-bearing property
            # here, and it is what `test_outline_caps.py` now pins.
            #
            # AN EARLIER VERSION OF THIS COMMENT CLAIMED MORE, AND THE SECURITY
            # REVIEW REFUTED IT.  It said routing through `_clip` "fixes the
            # coercion ORDER", because cutting between a `U+202E` and its
            # terminator would strand an unterminated override.  MEASURED: it
            # cannot.  `_CONTROL_MAP` maps all 235 banned code points to exactly
            # one `U+FFFD` each, so `plain` is length- and index-preserving and
            # `truncate(plain(s)) == plain(truncate(s))` IDENTICALLY -- 20,000
            # fuzzed hostile pairs, zero differences, and a mutant running the
            # forbidden order stayed green on all 1058 arms.  There is never an
            # override left to strand, because `plain` replaced it.
            #
            # The ordering still costs nothing and the code is unchanged; what
            # changed is the reason given for it.  A true outcome resting on a
            # false mechanism is the shape this batch keeps cataloguing, and it
            # would have become load-bearing the day `plain` deleted rather than
            # replaced.
            title = _clip(node.ficha.title, row_cap)
            if cur == selected_id:
                block = f"bold {darkside.GROUND} on {darkside.ACCENT}"
                line.append(prefix, style=block)
                line.append(title, style=block)
            elif cur in hits:
                # Selection is painted ON TOP of a hit, exactly as the
                # layered renderer orders them: losing your place is worse
                # than losing one highlight, and a selected node is already
                # the one the operator is looking at.
                line.append(prefix, style=darkside.MUT)
                line.append(title, style=f"{darkside.INK} on {darkside.STEP}")
            else:
                line.append(prefix, style=darkside.MUT)
                line.append(title, style="bold")
            # Collapsed branches still answer: declare counts inline.
            children = index.get(cur)
            if children:
                total, missing = totals[cur]
                note = f"  {total} nodos"
                if missing:
                    note += f" · {missing} sin acta"
                style = darkside.WARN if missing else darkside.MUT
                if cur == selected_id:
                    style = f"bold {darkside.GROUND} on {darkside.ACCENT}"
                line.append(note, style=style)
            elif node.ficha.meta:
                line.append(f"  {darkside.plain(node.ficha.meta)}", style=darkside.MUT)
            rows.append((cur, line))
            if children:
                # Reversed, so the LIFO stack still emits pre-order,
                # left to right, exactly as the recursion did.
                stack.extend((cid, lv + 1) for cid in reversed(children))

    walk(graph.root_id, 0)

    return rows, None


def _fit(
    rows: list[tuple[str | None, Text]], w: int, h: int
) -> list[tuple[str | None, Text]]:
    """The prefix of `rows` that OCCUPIES at most `h` physical rows at width `w`.

    MEASURED, never computed from cell counts.  Rich WORD-WRAPS, so a line a
    `ceil(cells / w)` formula prices at two rows can take three -- that formula
    is `B-61`, and `layered.header_rows` already measures rather than computes
    for the same reason.

    THE OLD CUT WAS `lines[:h]`, A LOGICAL SLICE, AND IT SHIPPED A LIE.
    Measured on `anidado` at a (30,16) terminal: four logical lines need SEVEN
    physical rows at region width 30 into a region that holds five, and the
    fourth reached no cell of the composited frame -- while a declaration built
    from the logical slice called that node painted.  Nine such cases across a
    144-combination sweep, every one of them on `anidado` and none on `legacy`,
    which is why `AT-056` now drives both fixtures.

    Stops at the budget, so the measuring costs at most `h` lines rather than
    one per node -- the 12002-node bound is never walked for this.
    """
    console = Console(width=max(1, w), no_color=True)
    kept: list[tuple[str | None, Text]] = []
    used = 0
    for nid, line in rows:
        cost = max(1, len(console.render_lines(line, pad=False)))
        if used + cost > h:
            break
        kept.append((nid, line))
        used += cost
    return kept


def _declared(rows, kept) -> int:
    """How many NODES the fit dropped.  Rows without a node id do not count."""
    return (sum(1 for nid, _t in rows if nid)
            - sum(1 for nid, _t in kept if nid))


def _widen(
    rows: list[tuple[str | None, Text]], hidden: int
) -> list[tuple[str | None, Text]]:
    """`rows` with the declaration appended to the header, built in ONE place."""
    header = rows[0][1].copy()
    header.append(f"  {OVERFLOW_TOKEN} {hidden} fuera de vista", style=darkside.INK)
    return [(rows[0][0], header), *rows[1:]]


def floor_reached(rows: list[tuple[str | None, Text]], w: int, h: int) -> bool:
    """Is this frame at `LLR-N06.3.5`'s EMPTY-FRAME FLOOR?

    The floor is the geometric condition the requirement's exception names: the
    declaring header CANNOT FIT WITHOUT EVICTING THE LAST CONTENT ROW -- here,
    the widened header fits nothing at all while the unwidened one still fits
    something.

    PUBLIC, AND EXTRACTED FOR THE ARM, BECAUSE THE ARM WAS SELECTING ON THE
    CONSEQUENCE.  `tests/test_agree_floor.py` used to pick its frames by "the
    canvas said nothing", which is what the floor CAUSES rather than what the
    floor IS.  The code review fired the difference: widening `_fit_declared`'s
    fallback BEYOND the floor left the arm green at 4 passed while the exempted
    set grew from 9 to 17 on `legacy` and 9 to 14 on `anidado` -- so the
    exception could not lapse in the one direction that matters.

    Single-sourced rather than transcribed into the test: a second spelling of
    this predicate would be a second definition of the floor, which is `F7_3`'s
    failure ("three predicates behind one operator-facing numeral") one clause
    over.
    """
    if not rows:
        return False
    kept = _fit(rows, w, h)
    hidden = _declared(rows, kept)
    if hidden <= 0 or not kept:
        return False
    return not _fit(_widen(rows, hidden), w, h)


def _fit_declared(
    rows: list[tuple[str | None, Text]], w: int, h: int
) -> list[tuple[str | None, Text]]:
    """Fit, DECLARE what the fit hid, and re-fit -- because the declaration is
    painted in the header and can itself cost a row.

    `LLR-N06.3.5`: bounded is not enough, what is dropped has to be SAID, on the
    renderer's own surface as well as the strip.  `LLR-N06.3.3` makes silence
    mean *nothing is hidden*, so a canvas that hides seven nodes and says nothing
    is not merely unhelpful -- it makes a false positive claim.

    THE LOOP IS NOT DECORATION.  Appending the token widens the header, which can
    wrap it onto another physical row, which evicts a body line, which changes
    the number the token states.  A single pass would paint a declaration that
    its own painting falsified.  It iterates to a FIXED POINT and is bounded: at
    most three passes, and it returns the last fit either way, so a pathological
    frame degrades to a slightly stale numeral rather than looping.

    `render` and `painted_ids` both come through here, so the canvas header, the
    strip and the declaration are one computation -- `B-60`'s lesson.
    """
    kept = _fit(rows, w, h)
    if not rows:
        return kept
    hidden = _declared(rows, kept)
    for _ in range(3):
        if hidden <= 0:
            return kept
        candidate = _fit(_widen(rows, hidden), w, h)
        # `H1`, REFINED RATHER THAN CONTRADICTED (coordinator ruling
        # 2026-09-10).  `Inc-STRIPS` recorded H1 as "a declaration must not
        # manufacture the omission it announces", but its own evidence says
        # something narrower: the unconditional reserve dropped 2 of 3 branches
        # and declared "+2" AT IDENTICAL STRIP AND CANVAS HEIGHTS EITHER WAY --
        # the dropped branches bought NOTHING.  The law is therefore "a
        # declaration must not spend content and INFORM NOTHING".
        #
        # Here it informs.  Measured at (30,16) on `legacy`: suppressing the
        # declaration paints ONE of eight nodes and says nothing, which
        # `LLR-N06.3.3` makes into the assertion that this is a one-node map --
        # the worst lie available in a tool whose whole story is that nothing is
        # hidden silently.  Declaring spends that node and tells the operator
        # eight are out of view, which is actionable.  So the declaration wins,
        # and the loop below settles the count against the POST-declaration
        # frame: a canvas that declared 7 after its own header took the row
        # would be lying about its own cost.
        # THE ONE FLOOR THE RULING STILL LEAVES: never return an EMPTY frame.
        # If the widened header does not fit at all, `_fit` drops it too and the
        # canvas paints NOTHING -- not the nodes, not the declaration. Measured
        # at (34,14) on `legacy`, where the budget is one row and the declaring
        # header needs two. That is `H1`-refined's forbidden case in its purest
        # form: it spends everything and informs nothing. Fall back to the
        # header the frame CAN hold; the strip still declares.
        if not candidate and kept:
            return kept
        kept = candidate
        settled = _declared(rows, kept)
        if settled == hidden:
            return kept
        hidden = settled
    return kept


def painted_ids(graph: Graph, state: ViewState) -> frozenset[str]:
    """The ids this renderer's own geometry says reached the canvas.

    A module-level PURE function, deliberately not an `IRenderer` member, for
    the reason `layered.painted_ids` records: the Protocol is
    `runtime_checkable`, so a second member would flip every shipped renderer to
    `isinstance -> False`, and a side-channel attribute set by `render` is
    cross-contaminated by the export call site, which renders the same
    long-lived renderer at a different size.

    It answers from `_fit` -- the SAME pass `render` cuts with -- so the
    declaration and the cut cannot disagree about what "painted" means.
    """
    rows, short_circuit = _rows(graph, state)
    if short_circuit is not None:
        return frozenset()
    return frozenset(
        nid for nid, _line in _fit_declared(rows, state.w, state.h)
        if nid is not None
    )


class OutlineRenderer:
    """Render a Graph as an editable-looking indented outline."""

    def render(self, graph: Graph, state: ViewState) -> Text:
        rows, short_circuit = _rows(graph, state)
        if short_circuit is not None:
            return short_circuit
        result = Text()
        for i, (_nid, row) in enumerate(_fit_declared(rows, state.w, state.h)):
            if i:
                result.append("\n")
            result.append(row)
        return result
