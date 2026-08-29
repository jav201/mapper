"""Layered tree renderer for concept and legacy maps."""
from __future__ import annotations

from dataclasses import dataclass

from rich.console import Console
from rich.markup import escape
from rich.text import Text

from mapper import darkside
from mapper.canvas import Canvas
from mapper.model import Graph
from mapper.views.state import ViewState


# Declared rendering bound, chosen from measurement, not taste.  See the note on
# MAX_RENDER_NODES in radial.py; a test keeps the three values in step.
MAX_RENDER_NODES = 12000

# The leading token of the overflow declaration (HLR-N06.3) and of a fold pill
# (HLR-N06.2), each declared ONCE here.  `mapper.app` imports them rather than
# re-typing them: two copies of a token agree on the day they are written and
# drift the first time one is edited, which is the defect `LLR-COERCE.1`
# removed one file over for a code-point list.
OVERFLOW_TOKEN = "▽"
FOLD_PILL_TOKEN = "▸"

# The coverage percentage `header_rows` prices the meter at.  Any value does:
# `darkside.step_meter(filled, total)` emits `total` glyphs whatever `filled`
# is, so the meter is 5 cells wide at every percentage and the percentage
# cannot change the header's LENGTH, which is the only thing that function
# needs.  Named rather than inlined so the reason travels with the value.
_METER_PCT = 100


STATE_STYLE = {
    "ok": darkside.INK,
    "risk": darkside.WARN,
    "late": darkside.WARN,
    "blocked": darkside.ALERT,
    "": darkside.INK,
}


def _vis_width(s: str) -> int:
    """Approximate visible width (simple: length, no CJK handling)."""
    return len(s)


def _clip(s: str, width: int) -> str:
    """LLR-COERCE.2: coerce, THEN truncate.

    The order is the requirement.  Truncation MANUFACTURES the defect out of a
    source that was balanced: a title carrying U+202E … U+202C cut at `width`
    between the two leaves an unterminated right-to-left override in the painted
    row, and no amount of coercing afterwards puts the terminator back.  Every
    truncator in this module funnels through here, so the ordering is stated in
    one place rather than at each call site.
    """
    s = darkside.plain(s)
    if _vis_width(s) <= width:
        return s
    return s[: max(0, width - 1)] + "…"


def _fit(s: str, width: int) -> str:
    s = _clip(s, width)
    return s + " " * (width - _vis_width(s))


def _child_index(graph: Graph) -> dict[str, list[str]]:
    """Adjacency built once. Graph.children_of rescans every edge per call."""
    index: dict[str, list[str]] = {}
    for edge in graph.edges:
        index.setdefault(edge.parent_id, []).append(edge.child_id)
    return index


def _parent_index(graph: Graph) -> dict[str, str]:
    """First parent per child, matching Graph.parent_of's first-edge-wins rule."""
    parents: dict[str, str] = {}
    for edge in graph.edges:
        parents.setdefault(edge.child_id, edge.parent_id)
    return parents


def _descendants(index: dict[str, list[str]], nid: str) -> set[str]:
    """Every node under *nid*, exclusive.  Deduplicated, so a diamond counts once."""
    out: set[str] = set()
    stack = list(index.get(nid, ()))
    while stack:
        cid = stack.pop()
        if cid in out:
            continue
        out.add(cid)
        stack.extend(index.get(cid, ()))
    return out


def _hidden_ids(index: dict[str, list[str]], folded: frozenset[str]) -> frozenset[str]:
    """The UNION of the folded branches' descendants — never the sum.

    LLR-N06.3.1's whole subject: a node inside two folded branches (an inner
    fold nested in an outer one) is hidden once, and adding the two counts
    declares more hidden nodes than the graph contains.
    """
    hidden: set[str] = set()
    for nid in folded:
        hidden |= _descendants(index, nid)
    return frozenset(hidden)


def _degraded(n: int, legacy: bool) -> Text:
    """Declared degradation: naming what was dropped beats raising."""
    out = Text()
    out.append("◆ ", style=darkside.INK)
    out.append("mapper", style=darkside.WORDMARK)
    out.append(" · árbol legacy" if legacy else " · mapa de conceptos", style=darkside.MUT)
    out.append(chr(10) * 2)
    out.append(
        f"mapa de {n} nodos: supera el límite de {MAX_RENDER_NODES} nodos. "
        "Se omitió el dibujo del árbol completo (fichas, aristas y cobertura).",
        style=darkside.WARN,
    )
    return out


def _tree_layout(
    graph: Graph,
    card_w: int,
    gap: int = 3,
    hidden: frozenset[str] = frozenset(),
) -> dict[str, tuple[int, int]]:
    """In-order leaf slots; internal nodes centred over their children.
    Handles forests (disconnected trees) by laying out each root tree side-by-side.
    Returns {id: (cx_cells, level)}.

    `hidden` is the set folded away: pruning it from the adjacency makes a folded
    branch's root a leaf for layout purposes, so the slots close up and the pill
    lands where the subtree used to be.  Empty by default, which is the shipped
    behaviour byte for byte.
    """
    pos: dict[str, tuple[float, int]] = {}
    slot = [0]
    index = _child_index(graph)
    if hidden:
        index = {
            nid: [cid for cid in children if cid not in hidden]
            for nid, children in index.items()
        }
    has_parent = {edge.child_id for edge in graph.edges}

    def walk(nid: str, depth: int) -> None:
        # visiting is the active path.  Recursion answered a cyclic graph with a
        # RecursionError, which the screens catch; a plain loop would answer it
        # by never returning, and a hang is worse than a crash.
        visiting: set[str] = set()
        stack: list[tuple[str, int, bool]] = [(nid, depth, False)]
        while stack:
            cur, lv, expanded = stack.pop()
            children = index.get(cur)
            if not children:
                pos[cur] = (slot[0], lv)
                slot[0] += 1
                continue
            if expanded:
                visiting.discard(cur)
                xs = [pos[cid][0] for cid in children]
                pos[cur] = ((xs[0] + xs[-1]) / 2, lv)
                continue
            if cur in visiting:
                raise ValueError(f"cycle through {cur}: the graph is not a tree")
            visiting.add(cur)
            stack.append((cur, lv, True))
            # Reversed, so the LIFO stack still visits children left to right
            # and the in-order slot numbering is the one the recursion produced.
            stack.extend((cid, lv + 1, False) for cid in reversed(children))

    roots = [nid for nid in graph.nodes if nid not in has_parent and nid not in hidden]
    if not roots:
        # Fallback to the declared root if the graph has no obvious roots.
        roots = [graph.root_id] if graph.root_id in graph.nodes else []
    if not roots:
        return {}

    for root in roots:
        start_slot = slot[0]
        walk(root, 0)
        # Add a gap between trees in the same forest.
        if slot[0] > start_slot:
            slot[0] += 1

    step = card_w + gap
    return {nid: (card_w // 2 + int(cx * step), lv) for nid, (cx, lv) in pos.items()}


@dataclass(frozen=True)
class _Geometry:
    """One layout pass, shared by `render` and `painted_ids` so they cannot drift.

    Everything below `place` is derived here and nowhere else.  The two consumers
    disagreeing about which nodes reached the canvas is exactly the failure
    `HLR-N06.3` is an identity rather than a promise to prevent, so they are
    given one computation instead of two that agree today.
    """

    pos: dict[str, tuple[int, int]]
    visible: list[str]
    hidden: frozenset[str]
    pill_ids: list[str]
    index: dict[str, list[str]]
    card_w: int
    card_h: int
    level_h: int
    avail: int
    body_h: int
    row_limit: int
    tree_bottom: int
    removed_h: int
    changed: dict[str, list[str]]
    pan_x: int
    pan_y: int
    legacy: bool
    gap: int

    def place(self, nid: str) -> tuple[int, int]:
        """A node's TOP-LEFT canvas cell, pan applied.

        `max(0, ...)` is the shipped layout clamp and runs BEFORE the pan
        subtraction: applied after, panning right would pile every card back
        onto column 0 instead of moving the window over the map.
        """
        cx, lv = self.pos[nid]
        return max(0, cx - self.card_w // 2) - self.pan_x, lv * self.level_h - self.pan_y

    def title_width(self, nid: str) -> int:
        chip = self.changed.get(nid) or []
        chip_len = len(" " + ",".join(chip) + " ") if chip else 0
        return self.card_w - 3 - chip_len


def _geometry(graph: Graph, state: ViewState) -> _Geometry | None:
    """The layout block, extracted verbatim, plus fold pruning.

    Returns `None` for the two shapes `render` answers without drawing a tree —
    an empty graph and one past `MAX_RENDER_NODES` — so `painted_ids` declares
    nothing painted for exactly the frames that paint no tree.
    """
    w, h = state.w, state.h
    if graph.root_id is None or not graph.nodes:
        return None
    if len(graph.nodes) > MAX_RENDER_NODES:
        return None

    diff = state.diff
    removed_ids = diff.removed if diff else set()
    changed = diff.changed if diff else {}

    index = _child_index(graph)
    hidden = _hidden_ids(index, state.folded)
    visible = [nid for nid in graph.nodes if nid not in hidden]
    # A pill is painted only for a folded branch that is itself on the canvas:
    # a fold nested inside another fold has no card to sit under, and painting
    # one anyway is how the pill sum starts double-counting (LLR-N06.3.2).
    pill_ids = [nid for nid in visible if nid in state.folded and index.get(nid)]

    n_leaves = sum(
        1 for nid in visible
        if not [cid for cid in index.get(nid, ()) if cid not in hidden]
    )
    gap = 3
    widest = max(
        max(_vis_width(graph.nodes[nid].ficha.title) + 3,
            _vis_width(graph.nodes[nid].ficha.meta) + 2)
        for nid in visible
    )
    card_w = min(26, max(14, widest))
    avail = w - 2
    if n_leaves * (card_w + gap) - gap > avail:
        card_w = max(9, (avail - (n_leaves - 1) * gap) // n_leaves)
    legacy = bool(graph.schema)
    card_h, edge_h = (3 if legacy else 2), 2
    level_h = card_h + edge_h

    pos = _tree_layout(graph, card_w, gap, hidden)
    depth_max = max(lv for _, lv in pos.values()) if pos else 0
    tree_bottom = (depth_max + 1) * card_h + depth_max * edge_h
    removed_h = (card_h + 2) if removed_ids else 0
    # A pill sits one row under its card, and the deepest possible pill row IS
    # `tree_bottom`; without this the canvas would be exactly one row too short
    # to hold the pill it was asked to paint.
    pill_h = 1 if pill_ids else 0
    # Rows past h are dropped by the lines[:h] slice below, so painting them
    # is pure cost — and on a deep map it is the cost that dominates.
    body_h = min(max(tree_bottom + removed_h + pill_h, h - 5), max(h, 1))

    return _Geometry(
        pos=pos, visible=visible, hidden=hidden, pill_ids=pill_ids, index=index,
        card_w=card_w, card_h=card_h, level_h=level_h, avail=avail,
        body_h=body_h,
        # `lines` is the header plus `body_h` canvas rows and is cut by
        # `lines[:h]`, so canvas row y survives iff `1 + y < h`.
        row_limit=h - 1,
        tree_bottom=tree_bottom, removed_h=removed_h, changed=changed,
        pan_x=state.pan_x, pan_y=state.pan_y, legacy=legacy, gap=gap,
    )


def _title_image(graph: Graph, geo: _Geometry, nid: str) -> str:
    """`HLR-N06.3`'s normative painted-trace predicate, product side.

    BOTH restrictions, and the column one is not an implementation detail: the
    row bound alone is the mutant the requirement names `MUT-B`, and it survives
    the "nothing hidden" configuration entirely.  Returns `""` when the node's
    title row never reaches the frame.
    """
    cx, y = geo.place(nid)
    if not (0 <= y < geo.body_h and y < geo.row_limit):
        return ""
    title = _fit(graph.nodes[nid].ficha.title, max(1, geo.title_width(nid)))
    return "".join(
        ch for j, ch in enumerate(title) if 0 <= cx + 2 + j < geo.avail
    )


def painted_ids(graph: Graph, state: ViewState) -> frozenset[str]:
    """The ids this renderer's own geometry says reached the canvas.

    A module-level PURE function, deliberately not a `IRenderer` member and not
    an attribute `render` sets: the Protocol is `runtime_checkable`, so a second
    member would flip all six shipped renderers to `isinstance -> False`, and a
    side-channel attribute is cross-contaminated by the export call site, which
    renders the same long-lived renderer at a different size.
    """
    geo = _geometry(graph, state)
    if geo is None:
        return frozenset()
    return frozenset(
        nid for nid in geo.visible if _title_image(graph, geo, nid).strip()
    )


def pan_extent(graph: Graph, state: ViewState) -> tuple[tuple[int, int], tuple[int, int]]:
    """`((extent_x, span_x), (extent_y, span_y))` — `LLR-N06.1.2`'s `E` and `W`.

    Exported so the screen clamps against the layout the renderer actually drew
    rather than re-deriving a second geometry that agrees until one is edited.
    """
    geo = _geometry(graph, state)
    if geo is None:
        return ((0, max(1, state.w - 2)), (0, max(1, state.h - 1)))
    extent_x = max(
        (max(0, cx - geo.card_w // 2) + geo.card_w for cx, _ in geo.pos.values()),
        default=0,
    )
    extent_y = geo.tree_bottom + geo.removed_h + (1 if geo.pill_ids else 0)
    return ((extent_x, geo.avail), (extent_y, geo.row_limit))


def _header_line(
    graph: Graph, avail: int, legacy: bool, pct: int, unpainted: int
) -> Text:
    """The canvas header, built in ONE place — `render` and `header_rows`.

    Extracted because the screen has to CHARGE for this line's physical height
    and a second copy of its construction is a copy that drifts: the constant
    `HEADER_ROWS = 2` was exactly such a copy, and it was wrong by one row at
    every canvas width up to 34 (`B-61`).  The two paddings are clamped at 0, so
    below `avail = 48` the line is a fixed core plus the declaration rather than
    the `2 * avail - 43` the old note described — which is why it wraps to three
    rows on a narrow terminal while the note said two.
    """
    header = Text()
    header.append("◆ ", style=darkside.INK)
    header.append("mapper", style=darkside.WORDMARK)
    header.append(
        " · árbol legacy" if legacy else " · mapa de conceptos", style=darkside.MUT
    )
    if legacy:
        filled = min(5, max(0, round(pct / 20)))
        header.append(" " * max(0, avail - 48))
        header.append(darkside.step_meter(filled, 5))
    header.append(" " * max(0, avail - 30))
    header.append(f"{len(graph.nodes)} nodos", style=darkside.MUT)
    # HLR-N06.3 — the declaration, and it is an identity: the numeral is
    # `len(graph.nodes) - |painted|` over the set THIS pass computed, never a
    # fold count added to a viewport count.  LLR-N06.3.3 is the `if`: while
    # everything is painted the token does not appear at all, because an
    # indicator permanently reading zero trains the operator to ignore it.
    # `INK` rather than `WORDMARK` per PDR-addendum-3 #D28 — WORDMARK
    # measures 1.85 : 1 against GROUND and vanishes entirely on the WINDOWS
    # rung, and this line carries the whole story's promise.
    if unpainted:
        header.append(
            f"  {OVERFLOW_TOKEN} {unpainted} fuera de vista", style=darkside.INK
        )
    return header


def header_rows(graph: Graph, w: int, wrap_w: int) -> int:
    """PHYSICAL rows this renderer's first line occupies when the canvas paints it.

    The number `MapScreen._canvas_size` has to subtract from the region before
    it prices a body row.  It replaces the constant `HEADER_ROWS = 2`, which was
    a measurement of one fixture at one width band: measured here, `legacy`'s
    header takes THREE rows at narrow canvas widths and FOUR at the floor, and
    `_canvas_size` floors `w` at 20, so the band is reachable by resizing a
    terminal.  Charging 2 there left the screen believing one or two more body
    rows survived than the region could show, and `painted_ids` declared nodes
    that leave no trace — `CR-F1`'s defect, verbatim, one width band over.

    THE LINE IS RENDERED, NOT DIVIDED.  The first version of this function
    returned `ceil(len(first) / (w - 2))`, and that is not the wrap the widget
    performs: Rich WORD-WRAPS, so a line that `ceil` prices at 2 rows can occupy
    3.  Measured over a 943-configuration terminal sweep on `legacy`, the
    arithmetic charge was short of the real wrap at 23 of them — under-charging,
    which is `B-61` by this increment's own definition.  It is short for the
    same reason the constant it replaced was: a formula standing in for a
    measurement.  So the line goes through `Console.render_lines`, which is what
    the widget's own paint does.

    `wrap_w` IS THE WIDTH THE WIDGET WRAPS AT, AND IT IS NOT `w - 2`.  Two
    different widths are in play and an earlier revision conflated them.  `w` is
    the width the renderer BUILDS the line to (`avail = w - 2`, the paddings the
    line is assembled from).  `wrap_w` is the width the canvas widget WRAPS it
    at, which is that widget's content width — and `#map-canvas` carries
    `width: 1fr; height: 100%` with no padding and no border, so its content
    width is its REGION width, measured equal in all 943 configurations.  That
    region is `w` at 724 of them and `w - 2` at 219, so `w - 2` is not the
    widget's content width — it is one of the two values that width takes, and
    the wrong one most of the time.  Wrapping everything at `w - 2` charges a row
    too many wherever those two columns change the wrap: measured, 26 of the 636
    configurations whose region is tall enough for the frame to show the header.
    An over-charge is not free — at a short region it costs the operator the only
    body row there was, and `_canvas_size` then declares nothing painted.  So the
    caller MEASURES it and passes it -- there is no default, because there is no
    width this function could guess that is not the same mistake again.

    THE WORST CASE IS CHARGED, NOT THE CURRENT ONE, and that is what makes this
    computable at all.  The line's length depends on `unpainted`, which depends
    on `row_limit`, which depends on this number — a cycle.  It is broken by
    pricing the LONGEST the line can be (`unpainted = len(graph.nodes)`, the
    most digits and the token always present), which is safe in the one
    direction that matters: over-charging emits FEWER body rows than the region
    can show, and `row_limit` still describes exactly what was emitted, so the
    identity holds and at most one physical row goes unused.  Under-charging is
    the defect.  Nothing here reads `painted`, `row_limit` or `body_h`, so this
    is a pure function of `(graph, w, wrap_w)` and there is no fixed point being
    iterated — the unconditional worst-case pricing breaks the cycle on its own.

    `pct` IS NOT COMPUTED.  It used to come from `graph.coverage()`, an O(n)
    walk of every node's `required_coverage`, three times per repaint and twice
    per `J` keypress on the key-repeat path.  It cannot change the answer:
    `darkside.step_meter(filled, total)` emits `total` glyphs whatever `filled`
    is, so the meter is 5 cells at every percentage and the header's length
    takes exactly two values, one per `legacy` flag.  A constant is passed and
    the walk is gone.

    `max(1, ...)` because the two shapes `render` answers without a tree still
    occupy a line, and a zero would make `_canvas_size` hand the renderer a
    taller frame than the region holds.
    """
    avail = max(1, w - 2)
    if graph.root_id is None or not graph.nodes:
        first = "(no map loaded)"
    elif len(graph.nodes) > MAX_RENDER_NODES:
        first = _degraded(len(graph.nodes), bool(graph.schema)).plain.split("\n")[0]
    else:
        first = _header_line(
            graph, avail, bool(graph.schema), _METER_PCT, len(graph.nodes)
        ).plain
    console = Console(width=max(1, wrap_w), legacy_windows=False)
    return max(1, len(console.render_lines(Text(first), pad=False)))


class LayeredRenderer:
    """Render a Graph as a layered tree of ficha cards."""

    def render(self, graph: Graph, state: ViewState) -> Text:
        selected_id, h = state.selected_id, state.h
        # RESOLVED ids, decided by `mapper.search`.  The renderer evaluates no
        # query predicate of its own (HLR-N07.1): it used to carry one, and the
        # count taken from the other owner disagreed with the highlight painted
        # from this one.
        hit_ids, diff = state.hits, state.diff
        # `with_header` was a parameter no caller ever passed.  Executed across
        # the tracked tree: one declaration, one use, zero call sites supplying
        # it -- so the header was unconditional in fact and is unconditional in
        # code now.  It is deliberately NOT a `ViewState` field.
        if graph.root_id is None or not graph.nodes:
            return Text("(no map loaded)")
        if len(graph.nodes) > MAX_RENDER_NODES:
            return _degraded(len(graph.nodes), bool(graph.schema))

        parents = _parent_index(graph)

        added_ids = diff.added if diff else set()
        removed_ids = diff.removed if diff else set()
        changed = diff.changed if diff else {}
        removed_titles = diff.removed_titles if diff else {}

        geo = _geometry(graph, state)
        index = geo.index
        all_ids = geo.visible
        gap = geo.gap
        card_w, avail = geo.card_w, geo.avail
        legacy, card_h = geo.legacy, geo.card_h
        pos, tree_bottom, body_h = geo.pos, geo.tree_bottom, geo.body_h

        have_total, req_total = graph.coverage()
        pct = round(100 * have_total / req_total) if req_total else 100

        # The declaration is computed BEFORE the header rather than appended to
        # a half-built one, because the header is now built in a single helper
        # that `MapScreen` also calls to measure this line's physical height.
        painted = frozenset(
            nid for nid in all_ids if _title_image(graph, geo, nid).strip()
        )
        lines: list[Text] = [
            _header_line(graph, avail, legacy, pct, len(graph.nodes) - len(painted))
        ]

        cv = Canvas(avail, body_h)
        for nid in all_ids:
            cx, y = geo.place(nid)
            node = graph.nodes[nid]
            tone = STATE_STYLE.get(node.ficha.state, "default")
            hit = nid in hit_ids
            is_added = nid in added_ids
            changed_keys = changed.get(nid, [])

            chip_text = ""
            if changed_keys:
                chip_text = " " + ",".join(changed_keys) + " "
            title_w = card_w - 3 - (len(chip_text) if changed_keys else 0)
            title = _fit(node.ficha.title, max(1, title_w))
            for j, ch in enumerate("▐ " + title):
                if hit:
                    style = f"{darkside.INK} on {darkside.STEP}"
                elif j == 0:
                    style = darkside.ACCENT if is_added else darkside.STEP
                else:
                    style = tone
                cv.put(cx + j, y, ch, style)
            if changed_keys:
                chip = _fit(chip_text, len(chip_text))
                chip_x = cx + card_w - len(chip)
                for j, ch in enumerate(chip):
                    cv.put(chip_x + j, y, ch, f"{darkside.GROUND} on {darkside.WARN}")

            if legacy:
                # row 2: document chip
                doc = node.ficha.fields.get("D", "")
                doc_txt = f"◫ {doc}" if doc else "◫ sin acta"
                doc_style = darkside.INK if doc else darkside.ALERT
                cv.text(cx + 1, y + 1, _fit(doc_txt, card_w - 2), doc_style)
                # row 3: schema letters
                xx = cx + 1
                for sf in graph.schema:
                    have = bool(node.ficha.fields.get(sf.key))
                    # `SchemaField.key` is file-derived and `MapStore.load` does
                    # not coerce it, so this sink was the one place in the
                    # DEFAULT renderer where a sidecar's control code point
                    # still reached the terminal and the exported SVG -- B-47's
                    # exact failure, in the view that ships enabled.  The `[:1]`
                    # is not defensive padding: `cv.put` writes whatever string
                    # it is given into ONE cell while the loop below advances by
                    # a fixed 3, so the layout has always assumed a single-cell
                    # key and this states that assumption instead of trusting it.
                    cv.put(xx, y + 2, darkside.plain(sf.key)[:1] or " ",
                           darkside.MUT)
                    cv.put(xx + 1, y + 2, "✓" if have else "░",
                           darkside.INK if have else darkside.STEP)
                    xx += 3
            else:
                for j, ch in enumerate(_fit(node.ficha.meta, card_w - 2)):
                    cv.put(cx + 1 + j, y + 1, ch, darkside.MUT)

            parent = parents.get(nid)
            if parent is not None and parent in pos:
                px, py = geo.place(parent)
                edge_tone = darkside.ACCENT if (is_added or parent in added_ids) else "frame"
                cv.elbow_down(px + card_w // 2, py + card_h,
                              cx + card_w // 2, y - 1, edge_tone)

        # HLR-N06.2 — a folded branch declares itself, with the count of what it
        # is hiding, in the row the subtree used to start on.
        for nid in geo.pill_ids:
            cx, y = geo.place(nid)
            n_hidden = len(_descendants(index, nid))
            # LLR-N07.1.3.  The tail is the branch's own share of the RESOLVED
            # hit set, not a predicate re-evaluated here.  It is a declared
            # behaviour change and not a refactor: the hit definition widened by
            # `{id, meta, attachments}`, so the number moves for existing maps --
            # measured on one fixture, a `+2` branch's tail goes 1 -> 2.  An
            # empty hit set paints no tail, which is what keeps the value
            # query-driven rather than a constant.
            n_hits = len(_descendants(index, nid) & hit_ids)
            tail = f" {n_hits}" if n_hits else ""
            name_w = max(1, card_w - 5 - len(str(n_hidden)) - len(tail))
            core = f"{FOLD_PILL_TOKEN} {_clip(graph.nodes[nid].ficha.title, name_w)} +{n_hidden}"
            # The left bar and the hit count in WARN: LLR-S06.3.5 gives WARN the
            # single job "outstanding attention -- work pending, at risk or in
            # flight, and nothing has failed", and matches sealed inside a folded
            # branch are work the operator still has pending.  The bar plus one
            # space mirrors the card's own `▐ ` prefix, so the pill reads as the
            # slot the subtree vacated rather than as a different kind of mark.
            cv.put(cx, y + card_h, "▐", darkside.WARN)
            cv.text(cx + 2, y + card_h, core, darkside.MUT)
            if tail:
                cv.text(cx + 2 + len(core), y + card_h, tail, darkside.WARN)

        # Removed nodes rendered as alert ghosts below the tree.
        if removed_ids:
            gy = tree_bottom + 1 - geo.pan_y
            cv.text(0, gy, "─" * avail, darkside.STEP)
            cv.text(1, gy + 1, "eliminados", darkside.MUT)
            gx = 12
            for nid in sorted(removed_ids):
                title = removed_titles.get(nid, nid)
                ghost = _fit(escape(title), card_w - 2)
                # strikethrough via unicode combining char is fragile; use a tilde prefix.
                cv.text(gx, gy + 2, "~" + ghost[:-1], darkside.ALERT)
                gx += card_w + gap
                if gx + card_w > avail:
                    break

        # selection highlight on top
        if selected_id and selected_id in pos:
            node = graph.nodes[selected_id]
            cx, y = geo.place(selected_id)
            # Carry B-05: the canvas painted a full-strength selection block
            # regardless of where the keyboard actually was, so the rail, the
            # canvas and the inspector each claimed the selection at once and
            # none of them told the operator which one would answer a key.
            # While another region owns the focus the selection is still SHOWN
            # -- losing your place is worse than a soft highlight -- but it
            # stops claiming to be active.
            #
            # `""` means the owner is unknown, and it paints what the tree
            # painted before this field existed.  That is what keeps the
            # signature migration byte-identical.
            if state.focus_owner in ("", "canvas"):
                block_style = f"bold {darkside.GROUND} on {darkside.ACCENT}"
            else:
                block_style = f"{darkside.INK} on {darkside.STEP}"
            for j, ch in enumerate("▐ " + _fit(node.ficha.title, card_w - 3)):
                cv.put(cx + j, y, ch, block_style)

        lines.extend(cv.rows())

        # The ficha strip that used to live here is gone: the inspector panel on
        # MapScreen is now the single ficha surface.  Rendering it in both places
        # showed the same card twice.  Suppressing it with a new render kwarg was
        # rejected — IRenderer.render is a frozen interface this batch may not touch.

        # Join rows into one Text with newlines
        result = Text()
        for i, row in enumerate(lines[:h]):
            if i:
                result.append("\n")
            result.append(row)
        return result
