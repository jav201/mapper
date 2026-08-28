"""Radial (mind-map) renderer."""
from __future__ import annotations

import math

from rich.text import Text

from mapper import darkside
from mapper.canvas import Canvas
from mapper.model import Graph
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


class RadialRenderer:
    """Render a Graph as a radial mind map."""

    def render(self, graph: Graph, state: ViewState) -> Text:
        selected_id, w, h = state.selected_id, state.w, state.h
        if graph.root_id is None:
            return Text("(no map loaded)")
        if len(graph.nodes) > MAX_RENDER_NODES:
            return _degraded(len(graph.nodes))

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
                elif j == 0:
                    style = ""
                elif nid in on_path:
                    style = darkside.ACCENT
                else:
                    style = branch_of.get(nid, darkside.MUT)
                cv.put(x + j, y, ch, style)
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

        lines = [Text()]
        header = Text()
        header.append("◆ ", style=darkside.INK)
        header.append("mapper", style=darkside.WORDMARK)
        header.append(" · mapa mental", style=darkside.MUT)
        lines[0] = header
        lines.extend(cv.rows())

        result = Text()
        for i, row in enumerate(lines[:h]):
            if i:
                result.append("\n")
            result.append(row)
        return result
