"""Radial (mind-map) renderer."""
from __future__ import annotations

import math

from rich.text import Text

from mapper import darkside
from mapper.canvas import Canvas
from mapper.model import Graph
from mapper.views.layered import overflow_phrase
from mapper.views.state import ViewState


# Achromatic branch tints — KMBlue is reserved for the active path.
# Avoid STEP/WORDMARK here because they are background greys and would be
# nearly invisible as text on the black canvas.
_GREYS = (
    darkside.INK,
    darkside.ASH,
    darkside.MUT,
)


# Declared rendering bound, chosen from measurement, not taste.  At 12000 nodes
# the worst render measured 0.29 s; at 24000 it measured 1.01 s, which is past
# the point a redraw still feels immediate.  Above the bound the radial layout
# is not drawn at all — see MAX_RENDER_NODES in layered.py and outline.py, which
# a test keeps in step with this one.
MAX_RENDER_NODES = 12000


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


def _leaf_counts(index: dict[str, list[str]], seeds: list[str]) -> dict[str, int]:
    """Leaves under every node reachable from seeds, iterative post-order.

    Memoised: a node reached down two branches is summed once, which is what
    the recursive original computed the slow way.

    Bounded on the active path.  Recursion answered a cyclic graph with a
    RecursionError, which the screens catch; a plain loop would answer it by
    never returning, and a hang is worse than a crash.  Cycles are refused at
    load (HLR-R01), but the CSV import preview builds a graph without going
    near the parser, so the traversal states its own bound.
    """
    counts: dict[str, int] = {}
    for seed in seeds:
        visiting: set[str] = set()
        stack: list[tuple[str, bool]] = [(seed, False)]
        while stack:
            nid, expanded = stack.pop()
            if expanded:
                visiting.discard(nid)
                counts[nid] = sum(counts[c] for c in index[nid])
                continue
            if nid in counts:
                continue
            if nid in visiting:
                raise ValueError(f"cycle through {nid}: the graph is not a tree")
            children = index.get(nid)
            if not children:
                counts[nid] = 1
                continue
            visiting.add(nid)
            stack.append((nid, True))
            stack.extend((c, False) for c in children if c not in counts)
    return counts


def _leaves(graph: Graph, nid: str) -> int:
    """Leaves under nid. Iterative and memoised; the recursive original died at
    CPython's C-recursion ceiling, which no recursion limit can lift."""
    return _leaf_counts(_child_index(graph), [nid])[nid]


def _degraded(n: int) -> Text:
    """Declared degradation: naming what was dropped beats raising."""
    out = Text()
    out.append("◆ ", style=darkside.INK)
    out.append("mapper", style=darkside.WORDMARK)
    out.append(" · mapa mental", style=darkside.MUT)
    out.append(chr(10) * 2)
    out.append(
        f"mapa de {n} nodos: supera el límite de {MAX_RENDER_NODES} nodos. "
        "Se omitió el dibujo radial completo (nodos, aristas y etiquetas).",
        style=darkside.WARN,
    )
    return out


def _paint(graph: Graph, state: ViewState) -> tuple[Text, frozenset[str]]:
    """Render the map AND report which nodes survived onto the canvas.

    THE ONE PASS BOTH `render` AND `painted_ids` CONSUME, for the reason
    `outline` shares its row pass: two passes would be two definitions of
    "painted", and `B-60` is exactly what that costs -- the canvas and the strip
    declaring different totals for the same frame.
    """
    selected_id, w, h = state.selected_id, state.w, state.h
    # RESOLVED ids, decided by `mapper.search` (HLR-N07.1).  This renderer
    # evaluates no query predicate of its own -- it never sees the query.
    hits = state.hits
    if graph.root_id is None:
        return Text("(no map loaded)"), frozenset()
    if len(graph.nodes) > MAX_RENDER_NODES:
        return _degraded(len(graph.nodes)), frozenset()

    inner = w - 2
    body_h = h - 4
    cv = Canvas(
        inner, body_h,
        tones=darkside.tone_set(), fallback=darkside.MUT,
    )

    cx0, cy0 = max(10, inner // 5), body_h // 2
    pos: dict[str, tuple[int, int]] = {}
    branch_of: dict[str, str] = {}
    index = _child_index(graph)
    parents = _parent_index(graph)
    # Runs before place and tag, so those two never meet a cyclic graph.
    leaves = _leaf_counts(index, [graph.root_id, *graph.nodes, *index])

    def place(nid: str, level: int, a0: float, a1: float) -> None:
        stack = [(nid, level, a0, a1)]
        while stack:
            cur, lv, lo, hi = stack.pop()
            a = (lo + hi) / 2
            r = lv * max(10, inner // 4)
            squash = min(0.55, max(0.3, cy0 / max(1, r)))
            x = max(0, min(inner - 1, int(cx0 + r * math.cos(a))))
            y = max(0, min(body_h - 1, int(cy0 + r * math.sin(a) * squash)))
            pos[cur] = (x, y)
            kids = index.get(cur)
            if not kids:
                continue
            total = sum(leaves[c] for c in kids) or 1
            acc = lo
            spans = []
            for c in kids:
                frac = leaves[c] / total
                spans.append((c, lv + 1, acc, acc + frac * (hi - lo)))
                acc += frac * (hi - lo)
            # Reversed, so the LIFO stack still visits children left to right.
            stack.extend(reversed(spans))

    # Place root
    pos[graph.root_id] = (cx0, cy0)
    children = index.get(graph.root_id, [])
    total = sum(leaves[c] for c in children) or 1
    span = 1.75
    acc = -span / 2
    for i, ch in enumerate(children):
        frac = leaves[ch] / total
        branch_of[ch] = _GREYS[i % len(_GREYS)]
        place(ch, 1, acc, acc + frac * span)
        acc += frac * span

    # Compute active path from root to selected node.
    on_path: set[str] = set()
    if selected_id and selected_id in graph.nodes:
        current = selected_id
        while current is not None:
            on_path.add(current)
            current = parents.get(current)

    # Assign an achromatic grey tint to each top-level branch.
    for i, ch in enumerate(children):
        branch_of[ch] = _GREYS[i % len(_GREYS)]

    def tag(nid: str, grey: str) -> None:
        stack = [nid]
        while stack:
            cur = stack.pop()
            branch_of[cur] = grey
            stack.extend(index.get(cur, ()))

    for i, ch in enumerate(children):
        tag(ch, _GREYS[i % len(_GREYS)])
    branch_of[graph.root_id] = darkside.INK

    # Draw edges as simple lines in dot space.
    for nid in graph.nodes:
        parent = parents.get(nid)
        if parent is None or parent not in pos or nid not in pos:
            continue
        x0, y0 = pos[parent]
        x1, y1 = pos[nid]
        if nid in on_path and parent in on_path:
            hue = darkside.ACCENT
        else:
            hue = branch_of.get(nid, darkside.MUT)
        # Draw a few dots along the line.
        steps = max(1, int(math.hypot(x1 - x0, y1 - y0) * 4))
        for s in range(steps + 1):
            t = s / steps
            dx = x0 + (x1 - x0) * t
            dy = y0 + (y1 - y0) * t
            cv.dots[(int(dx * 2), int(dy * 4))] = hue

    # THE CELL-OWNERSHIP LEDGER. `Canvas.put` is LAST-WRITE-WINS and records
    # no owner, so a later pill silently overwrites an earlier one's cells.
    # Deriving the painted set from `pos` -- which nodes were PLACED -- is
    # therefore `M-N06.3-b`: measured, it over-declares by 6 of 8 at 30x6,
    # because placement says where a pill was WRITTEN and not whether it
    # SURVIVED. These two dicts replay the writes so the question can be
    # answered from what is still on the canvas.
    owners: dict[tuple[int, int], str] = {}
    title_cells: dict[str, list[tuple[int, int]]] = {}
    # Draw nodes as pills.
    for nid in graph.nodes:
        if nid not in pos:
            continue
        x, y = pos[nid]
        node = graph.nodes[nid]
        sel = nid == selected_id
        # Coerce BEFORE slicing.  The title is file-derived and this is the
        # only place it enters the canvas; `save_svg` then snapshots those
        # bytes to a file that leaves the machine, where the terminal's own
        # escaping does not travel with it.
        title = darkside.plain(node.ficha.title)[:18]
        cw = len(title) + 3
        x = max(0, min(inner - cw, x - cw // 2))
        y = max(0, min(body_h - 1, y))
        pill_bg = darkside.PANEL
        for j in range(cw):
            cv.bgs[(x + j, y)] = pill_bg
        block = f"bold {darkside.GROUND} on {darkside.ACCENT}"
        for j, ch in enumerate(" " + title):
            if sel:
                style = block
            elif nid in hits:
                # Selection is painted ON TOP of a hit, as in the layered
                # renderer -- which paints the hit style for EVERY cell of
                # the title, and so does this.
                #
                # An earlier revision guarded this with `and j`, to "keep the
                # leading pad cell out of the highlight".  That conjunct was
                # DEAD and the claim was false: cell `j == 0` is `(x, y)`,
                # and the marker `put` below overwrites it unconditionally
                # for every node, hit or not.  Measured over 225
                # configurations, dropping the conjunct leaves the emitted
                # spans byte-identical -- so it guarded nothing and diverged
                # from `layered` for no reason.
                style = f"{darkside.INK} on {darkside.STEP}"
            elif j == 0:
                style = ""
            elif nid in on_path:
                style = darkside.ACCENT
            else:
                style = branch_of.get(nid, darkside.MUT)
            cv.put(x + j, y, ch, style)
            # ONLY IF THE PUT LANDED. `Canvas.put` refuses a cell outside its
            # bounds, and `body_h` can be ZERO -- at a 30x16 terminal
            # `_canvas_size` hands this renderer h=4, so `h - 4` is 0 and the
            # canvas holds no rows at all. Recording ownership unconditionally
            # credited nodes with cells the canvas never accepted, and the frame
            # then showed none of them: measured, `alm` declared painted at five
            # sizes on `legacy` while the region was blank below the header.
            #
            # Membership is an EXACT test rather than a copy of `put`'s
            # condition: `ch` here is always a single character, so bounds are
            # the only refusal, and an out-of-bounds cell cannot have been stored
            # by any earlier node either. Re-spelling the condition is the thing
            # that would drift.
            if (x + j, y) not in cv.cells:
                continue
            owners[(x + j, y)] = nid
            if j:
                # `j == 0` is the leading pad, which this node's own marker
                # overwrites below. The TITLE cells are what the operator reads,
                # so they are what ownership is judged on.
                title_cells.setdefault(nid, []).append((x + j, y))
        marker = "◆" if nid == graph.root_id else "●"
        if sel:
            marker_style = block
        elif nid in on_path:
            marker_style = darkside.ACCENT
        elif nid == graph.root_id:
            marker_style = darkside.INK
        else:
            marker_style = branch_of.get(nid, darkside.MUT)
        cv.put(x, y, marker, marker_style)
        if (x, y) in cv.cells:
            owners[(x, y)] = nid

    # RADIAL'S PAINTED PREDICATE, STATED HERE AND NOT BORROWED (`02m` 7.3).
    # A node is painted when EVERY cell of its title image is still owned by
    # it after the replay -- i.e. the operator can read the whole label.
    # Outline's predicate (the full title sought in the frame) does not
    # transfer: radial TRUNCATES to 18 cells, so a full-title trace
    # under-counts -- measured 0 of 8 at five sizes where the frame plainly
    # shows pills. Layered's does not transfer either: it anchors on card
    # columns radial has no equivalent of.
    #
    # A cell outside the canvas is dropped by `put`, so it never enters
    # `owners` and the node fails this test -- but ONLY because the recording
    # above is gated on the put having landed. An earlier draft of this comment
    # asserted that property while the code recorded unconditionally, which made
    # it false: the sentence described `put`'s behaviour and the ledger was not
    # `put`. The gate is what makes it true.
    painted = frozenset(
        nid for nid, cells in title_cells.items()
        if cells and all(owners.get(c) == nid for c in cells)
    )

    lines = [Text()]
    header = Text()
    header.append("◆ ", style=darkside.INK)
    header.append("mapper", style=darkside.WORDMARK)
    header.append(" · mapa mental", style=darkside.MUT)
    # BOTH DECLARING SURFACES, not just the strip (`LLR-N06.3.5`).  A canvas that
    # hides nodes and says nothing is not merely unhelpful: `LLR-N06.3.3` makes
    # silence mean *nothing is hidden*, so it asserts a smaller map than the one
    # the operator opened.
    #
    # The SENTENCE is consumed from `layered.overflow_phrase`, never re-spelled
    # (`F7`).  Radial is the renderer that would have made it a FOURTH copy.
    #
    # No fixed-point loop is needed here, and the difference from `outline` is
    # structural rather than lucky: `render` emits `1 + body_h` rows against a
    # budget of `h = body_h + 4`, so the header can never evict a body row and
    # the count cannot change by being declared.  `outline` fits its body INTO
    # the same budget the header spends from, which is why it has to settle.
    unpainted = len(graph.nodes) - len(painted)
    if unpainted:
        header.append(f"  {overflow_phrase(unpainted)}", style=darkside.INK)
    lines[0] = header
    lines.extend(cv.rows())

    result = Text()
    for i, row in enumerate(lines[:h]):
        if i:
            result.append("\n")
        result.append(row)
    return result, painted


def painted_ids(graph: Graph, state: ViewState) -> frozenset[str]:
    """The ids this renderer's own geometry says reached the canvas.

    A module-level PURE function, deliberately not an `IRenderer` member, for
    the reason `layered.painted_ids` records: the Protocol is
    `runtime_checkable`, so a second member would flip every shipped renderer to
    `isinstance -> False`, and a side-channel attribute set by `render` is
    cross-contaminated by the export call site, which renders the same
    long-lived renderer at a different size.
    """
    return _paint(graph, state)[1]


class RadialRenderer:
    """Render a Graph as a radial mind map."""

    def render(self, graph: Graph, state: ViewState) -> Text:
        return _paint(graph, state)[0]
