"""Layered tree renderer for concept and legacy maps."""
from __future__ import annotations

from rich.text import Text

from mapper.canvas import Canvas
from mapper.model import Graph, Node


STATE_STYLE = {
    "ok": "green",
    "risk": "yellow",
    "late": "red",
    "blocked": "red",
    "": "default",
}


def _vis_width(s: str) -> int:
    """Approximate visible width (simple: length, no CJK handling)."""
    return len(s)


def _clip(s: str, width: int) -> str:
    if _vis_width(s) <= width:
        return s
    return s[: max(0, width - 1)] + "…"


def _fit(s: str, width: int) -> str:
    s = _clip(s, width)
    return s + " " * (width - _vis_width(s))


def _tree_layout(graph: Graph, card_w: int, gap: int = 3) -> dict[str, tuple[int, int]]:
    """In-order leaf slots; internal nodes centred over their children.
    Returns {id: (cx_cells, level)}.
    """
    pos: dict[str, tuple[float, int]] = {}
    slot = [0]

    def walk(nid: str, depth: int) -> None:
        children = graph.children_of(nid)
        if not children:
            pos[nid] = (slot[0], depth)
            slot[0] += 1
            return
        for cid in children:
            walk(cid, depth + 1)
        xs = [pos[cid][0] for cid in children]
        pos[nid] = ((xs[0] + xs[-1]) / 2, depth)

    if graph.root_id is None:
        return {}
    walk(graph.root_id, 0)
    step = card_w + gap
    return {nid: (card_w // 2 + int(cx * step), lv) for nid, (cx, lv) in pos.items()}


class LayeredRenderer:
    """Render a Graph as a layered tree of ficha cards."""

    def render(
        self,
        graph: Graph,
        selected_id: str | None = None,
        w: int = 80,
        h: int = 24,
        query: str = "",
        with_header: bool = True,
    ) -> Text:
        if graph.root_id is None or not graph.nodes:
            return Text("(no map loaded)")

        all_ids = list(graph.nodes)
        n_leaves = sum(1 for nid in all_ids if not graph.children_of(nid))
        gap = 3
        widest = max(
            max(_vis_width(graph.nodes[nid].ficha.title) + 3,
                _vis_width(graph.nodes[nid].ficha.meta) + 2)
            for nid in all_ids
        )
        card_w = min(26, max(14, widest))
        avail = w - 2
        if n_leaves * (card_w + gap) - gap > avail:
            card_w = max(9, (avail - (n_leaves - 1) * gap) // n_leaves)
        legacy = bool(graph.schema)
        card_h, edge_h = (3 if legacy else 2), 2
        level_h = card_h + edge_h

        pos = _tree_layout(graph, card_w, gap)
        depth_max = max(lv for _, lv in pos.values()) if pos else 0
        body_h = max((depth_max + 1) * card_h + depth_max * edge_h, h - 5)

        have_total, req_total = graph.coverage()
        pct = round(100 * have_total / req_total) if req_total else 100

        lines: list[Text] = []
        if with_header:
            header = Text()
            header.append("◆ MAPPER", style="bold magenta")
            title_suffix = " · árbol legacy" if legacy else " · mapa de conceptos"
            header.append(title_suffix, style="dim")
            if legacy:
                header.append(" " * max(0, avail - 45))
                header.append(f"cobertura {pct}%", style="bold" if pct > 80 else "yellow" if pct > 50 else "red")
            header.append(" " * max(0, avail - 30))
            header.append(f"{len(all_ids)} nodos", style="dim")
            lines.append(header)

        cv = Canvas(avail, body_h)
        for nid in all_ids:
            cx, lv = pos[nid]
            cx = cx - card_w // 2
            cx = max(0, cx)
            y = lv * level_h
            node = graph.nodes[nid]
            tone = STATE_STYLE.get(node.ficha.state, "default")
            qlower = query.lower()
            hit = query and (
                qlower in node.ficha.title.lower()
                or qlower in node.ficha.notes.lower()
                or any(qlower in v.lower() for v in node.ficha.fields.values())
            )
            title = _fit(node.ficha.title, card_w - 3)
            for j, ch in enumerate("▐ " + title):
                style = "reverse" if hit else (tone if j == 0 else "default")
                cv.put(cx + j, y, ch, style)

            if legacy:
                # row 2: document chip
                doc = node.ficha.fields.get("D", "")
                doc_txt = f"◫ {doc}" if doc else "◫ SIN ACTA"
                doc_style = "green" if doc else "red"
                cv.text(cx + 1, y + 1, _fit(doc_txt, card_w - 2), doc_style)
                # row 3: schema letters
                xx = cx + 1
                for sf in graph.schema:
                    have = bool(node.ficha.fields.get(sf.key))
                    cv.put(xx, y + 2, sf.key, "default")
                    cv.put(xx + 1, y + 2, "✓" if have else "░",
                           "green" if have else "dim")
                    xx += 3
            else:
                for j, ch in enumerate(_fit(node.ficha.meta, card_w - 2)):
                    cv.put(cx + 1 + j, y + 1, ch, "dim")

            parent = graph.parent_of(nid)
            if parent is not None and parent in pos:
                px, plv = pos[parent]
                px = max(0, px - card_w // 2)
                cv.elbow_down(px + card_w // 2, plv * level_h + card_h,
                              cx + card_w // 2, y - 1, "frame")

        # selection highlight on top
        if selected_id and selected_id in pos:
            node = graph.nodes[selected_id]
            cx, lv = pos[selected_id]
            cx = cx - card_w // 2
            y = lv * level_h
            for j, ch in enumerate("▐ " + _fit(node.ficha.title, card_w - 3)):
                style = "bold magenta" if j == 0 else "bold"
                cv.put(cx + j, y, ch, style)

        lines.extend(cv.rows())

        # ficha strip
        sel = graph.nodes.get(selected_id)
        lines.append(Text("─" * avail, style="frame"))
        if sel is not None:
            strip = Text()
            strip.append("▸ ", style="bold magenta")
            strip.append(sel.ficha.title, style="bold")
            strip.append(f"   {sel.ficha.meta}", style="dim")
            if legacy:
                have, req = sel.ficha.required_coverage(graph.schema)
                strip.append(f"   {have}/{req} requeridos",
                             style="bold" if have == req else "red" if have < req - 1 else "yellow")
            lines.append(strip)
            if legacy:
                doc = sel.ficha.fields.get("D", "")
                row = Text()
                row.append("  documento ", style="dim")
                row.append(doc or "SIN ACTA", style="green" if doc else "red")
                row.append("   dueño ", style="dim")
                row.append(sel.ficha.fields.get("O", "—"), style="default")
                row.append("   creado ", style="dim")
                row.append(sel.ficha.fields.get("Y", "—"), style="default")
                lines.append(row)
            if sel.ficha.notes:
                lines.append(Text(_fit("  " + sel.ficha.notes, avail), style="dim"))
        else:
            lines.append(Text(_fit("  (selecciona un nodo — j/k/h/l, ↵ abre la ficha)", avail), style="dim"))

        # Join rows into one Text with newlines
        result = Text()
        for i, row in enumerate(lines[:h]):
            if i:
                result.append("\n")
            result.append(row)
        return result
