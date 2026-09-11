"""Outline (indented text) renderer."""
from __future__ import annotations

from rich.console import Console
from rich.text import Text

from mapper import darkside
from mapper.model import Graph
from mapper.views.state import ViewState


# Declared rendering bound, chosen from measurement, not taste.  This renderer
# is the one that sets it: its per-line indent is quadratic in depth, so a deep
# chain measured 0.26 s at 12000 nodes and 1.01 s at 24000.  See radial.py's
# note; a test keeps the three values in step.
MAX_RENDER_NODES = 12000


def _indent(level: int) -> str:
    return "  " * level


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
    header = Text()
    header.append("◆ ", style=darkside.INK)
    header.append("mapper", style=darkside.WORDMARK)
    header.append(" · outline", style=darkside.MUT)
    rows.append((None, header))

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

    def walk(nid: str, depth: int) -> None:
        stack = [(nid, depth)]
        while stack:
            cur, lv = stack.pop()
            node = graph.nodes[cur]
            prefix = _indent(lv) + ("- " if lv else "")
            line = Text()
            # B-47 / A-89: this renderer reaches `export.save_svg` through
            # `MapScreen.action_export_svg` exactly as the layered one does,
            # and it coerced nothing -- measured, a hostile title through it
            # writes an SVG that is not well-formed XML.  The guarantee
            # `AT-009` asserts held only in radial view.
            title = darkside.plain(node.ficha.title)
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
        nid for nid, _line in _fit(rows, state.w, state.h) if nid is not None
    )


class OutlineRenderer:
    """Render a Graph as an editable-looking indented outline."""

    def render(self, graph: Graph, state: ViewState) -> Text:
        rows, short_circuit = _rows(graph, state)
        if short_circuit is not None:
            return short_circuit
        result = Text()
        for i, (_nid, row) in enumerate(_fit(rows, state.w, state.h)):
            if i:
                result.append("\n")
            result.append(row)
        return result
