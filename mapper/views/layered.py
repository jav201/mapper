"""Layered tree renderer for concept and legacy maps."""
from __future__ import annotations

from rich.markup import escape
from rich.text import Text

from mapper import darkside
from mapper.canvas import Canvas
from mapper.diff import DiffResult
from mapper.model import Graph, Node


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
    if _vis_width(s) <= width:
        return s
    return s[: max(0, width - 1)] + "…"


def _fit(s: str, width: int) -> str:
    s = _clip(s, width)
    return s + " " * (width - _vis_width(s))


def _tree_layout(graph: Graph, card_w: int, gap: int = 3) -> dict[str, tuple[int, int]]:
    """In-order leaf slots; internal nodes centred over their children.
    Handles forests (disconnected trees) by laying out each root tree side-by-side.
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

    roots = [nid for nid in graph.nodes if graph.parent_of(nid) is None]
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
        diff: DiffResult | None = None,
    ) -> Text:
        if graph.root_id is None or not graph.nodes:
            return Text("(no map loaded)")

        added_ids = diff.added if diff else set()
        removed_ids = diff.removed if diff else set()
        changed = diff.changed if diff else {}
        removed_titles = diff.removed_titles if diff else {}

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
        tree_bottom = (depth_max + 1) * card_h + depth_max * edge_h
        removed_h = (card_h + 2) if removed_ids else 0
        body_h = max(tree_bottom + removed_h, h - 5)

        have_total, req_total = graph.coverage()
        pct = round(100 * have_total / req_total) if req_total else 100

        lines: list[Text] = []
        if with_header:
            header = Text()
            header.append("◆ ", style=darkside.INK)
            header.append("mapper", style=darkside.WORDMARK)
            title_suffix = " · árbol legacy" if legacy else " · mapa de conceptos"
            header.append(title_suffix, style=darkside.MUT)
            if legacy:
                filled = min(5, max(0, round(pct / 20)))
                header.append(" " * max(0, avail - 48))
                header.append(darkside.step_meter(filled, 5))
            header.append(" " * max(0, avail - 30))
            header.append(f"{len(all_ids)} nodos", style=darkside.MUT)
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
                    cv.put(xx, y + 2, sf.key, darkside.MUT)
                    cv.put(xx + 1, y + 2, "✓" if have else "░",
                           darkside.INK if have else darkside.STEP)
                    xx += 3
            else:
                for j, ch in enumerate(_fit(node.ficha.meta, card_w - 2)):
                    cv.put(cx + 1 + j, y + 1, ch, darkside.MUT)

            parent = graph.parent_of(nid)
            if parent is not None and parent in pos:
                px, plv = pos[parent]
                px = max(0, px - card_w // 2)
                edge_tone = darkside.ACCENT if (is_added or parent in added_ids) else "frame"
                cv.elbow_down(px + card_w // 2, plv * level_h + card_h,
                              cx + card_w // 2, y - 1, edge_tone)

        # Removed nodes rendered as alert ghosts below the tree.
        if removed_ids:
            gy = tree_bottom + 1
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
            cx, lv = pos[selected_id]
            cx = cx - card_w // 2
            y = lv * level_h
            block_style = f"bold {darkside.GROUND} on {darkside.ACCENT}"
            for j, ch in enumerate("▐ " + _fit(node.ficha.title, card_w - 3)):
                cv.put(cx + j, y, ch, block_style)

        lines.extend(cv.rows())

        # ficha strip
        sel = graph.nodes.get(selected_id)
        lines.append(Text("─" * avail, style=darkside.STEP))
        if sel is not None:
            strip = Text()
            strip.append("▸ ", style=darkside.INK)
            strip.append(sel.ficha.title, style="bold")
            strip.append(f"   {sel.ficha.meta}", style=darkside.MUT)
            if legacy:
                have, req = sel.ficha.required_coverage(graph.schema)
                strip.append("   cobertura ", style=darkside.MUT)
                strip.append(darkside.step_meter(have, req))
            lines.append(strip)
            if legacy:
                doc = sel.ficha.fields.get("D", "")
                row = Text()
                row.append("  documento ", style=darkside.MUT)
                row.append(doc or "sin acta", style=darkside.INK if doc else darkside.ALERT)
                row.append("   dueño ", style=darkside.MUT)
                row.append(sel.ficha.fields.get("O", "—"), style=darkside.INK)
                row.append("   creado ", style=darkside.MUT)
                row.append(sel.ficha.fields.get("Y", "—"), style=darkside.INK)
                lines.append(row)
            if sel.ficha.notes:
                lines.append(Text(_fit("  " + sel.ficha.notes, avail), style=darkside.MUT))
        else:
            lines.append(Text(_fit("  (selecciona un nodo — j/k/h/l, ↵ abre la ficha)", avail), style=darkside.MUT))

        # Join rows into one Text with newlines
        result = Text()
        for i, row in enumerate(lines[:h]):
            if i:
                result.append("\n")
            result.append(row)
        return result
