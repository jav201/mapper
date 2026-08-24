"""Radial (mind-map) renderer."""
from __future__ import annotations

import math

from rich.text import Text

from mapper import darkside
from mapper.canvas import Canvas
from mapper.model import Graph


# Achromatic branch tints only — KMBlue is reserved for selection/interactivity.
_HUES = (
    darkside.STEP,
    "#3a3a3a",
    "#4a4a4a",
    darkside.MUT,
    "#5a5a5a",
    "#666666",
    darkside.INK,
    "#2e2e2e",
)


def _leaves(graph: Graph, nid: str) -> int:
    children = graph.children_of(nid)
    if not children:
        return 1
    return sum(_leaves(graph, c) for c in children)


class RadialRenderer:
    """Render a Graph as a radial mind map."""

    def render(
        self,
        graph: Graph,
        selected_id: str | None = None,
        w: int = 80,
        h: int = 24,
        **kwargs,
    ) -> Text:
        if graph.root_id is None:
            return Text("(no map loaded)")

        inner = w - 2
        body_h = h - 4
        cv = Canvas(inner, body_h)
        cv.dots = {}
        cv.bgs = {}

        cx0, cy0 = max(10, inner // 5), body_h // 2
        pos: dict[str, tuple[int, int]] = {}
        branch_of: dict[str, str] = {}

        def place(nid: str, level: int, a0: float, a1: float) -> None:
            a = (a0 + a1) / 2
            r = level * max(10, inner // 4)
            squash = min(0.55, max(0.3, cy0 / max(1, r)))
            x = max(0, min(inner - 1, int(cx0 + r * math.cos(a))))
            y = max(0, min(body_h - 1, int(cy0 + r * math.sin(a) * squash)))
            pos[nid] = (x, y)
            children = graph.children_of(nid)
            if not children:
                return
            total = sum(_leaves(graph, c) for c in children) or 1
            acc = a0
            for c in children:
                frac = _leaves(graph, c) / total
                place(c, level + 1, acc, acc + frac * (a1 - a0))
                acc += frac * (a1 - a0)

        # Place root
        pos[graph.root_id] = (cx0, cy0)
        children = graph.children_of(graph.root_id)
        total = sum(_leaves(graph, c) for c in children) or 1
        span = 1.75
        acc = -span / 2
        for i, ch in enumerate(children):
            frac = _leaves(graph, ch) / total
            branch_of[ch] = _HUES[i % len(_HUES)]
            place(ch, 1, acc, acc + frac * span)
            acc += frac * span

        # Propagate branch hues to descendants
        def tag(nid: str, hue: str) -> None:
            branch_of[nid] = hue
            for c in graph.children_of(nid):
                tag(c, hue)

        for i, ch in enumerate(children):
            tag(ch, _HUES[i % len(_HUES)])
        branch_of[graph.root_id] = darkside.INK

        # Draw edges as simple lines in dot space
        for nid in graph.nodes:
            parent = graph.parent_of(nid)
            if parent is None or parent not in pos or nid not in pos:
                continue
            x0, y0 = pos[parent]
            x1, y1 = pos[nid]
            hue = branch_of.get(nid, "frame")
            # Draw a few dots along the line
            steps = max(1, int(math.hypot(x1 - x0, y1 - y0) * 4))
            for s in range(steps + 1):
                t = s / steps
                dx = x0 + (x1 - x0) * t
                dy = y0 + (y1 - y0) * t
                cv.dots[(int(dx * 2), int(dy * 4))] = hue

        # Draw nodes as pills
        for nid in graph.nodes:
            if nid not in pos:
                continue
            x, y = pos[nid]
            node = graph.nodes[nid]
            sel = nid == selected_id
            title = node.ficha.title[:18]
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
                else:
                    style = branch_of.get(nid, darkside.INK)
                cv.put(x + j, y, ch, style)
            marker = "◆" if nid == graph.root_id else "●"
            if sel:
                marker_style = block
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
