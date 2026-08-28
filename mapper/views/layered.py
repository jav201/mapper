"""Layered tree renderer for concept and legacy maps."""
from __future__ import annotations

from rich.markup import escape
from rich.text import Text

from mapper import darkside
from mapper.canvas import Canvas
from mapper.model import Graph, Node
from mapper.views.state import ViewState


# Declared rendering bound, chosen from measurement, not taste.  See the note on
# MAX_RENDER_NODES in radial.py; a test keeps the three values in step.
MAX_RENDER_NODES = 12000


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


def _tree_layout(graph: Graph, card_w: int, gap: int = 3) -> dict[str, tuple[int, int]]:
    """In-order leaf slots; internal nodes centred over their children.
    Handles forests (disconnected trees) by laying out each root tree side-by-side.
    Returns {id: (cx_cells, level)}.
    """
    pos: dict[str, tuple[float, int]] = {}
    slot = [0]
    index = _child_index(graph)
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

    roots = [nid for nid in graph.nodes if nid not in has_parent]
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

    def render(self, graph: Graph, state: ViewState) -> Text:
        selected_id, w, h = state.selected_id, state.w, state.h
        query, diff = state.query, state.diff
        # `with_header` was a parameter no caller ever passed.  Executed across
        # the tracked tree: one declaration, one use, zero call sites supplying
        # it -- so the header was unconditional in fact and is unconditional in
        # code now.  It is deliberately NOT a `ViewState` field.
        if graph.root_id is None or not graph.nodes:
            return Text("(no map loaded)")
        if len(graph.nodes) > MAX_RENDER_NODES:
            return _degraded(len(graph.nodes), bool(graph.schema))

        index = _child_index(graph)
        parents = _parent_index(graph)

        added_ids = diff.added if diff else set()
        removed_ids = diff.removed if diff else set()
        changed = diff.changed if diff else {}
        removed_titles = diff.removed_titles if diff else {}

        all_ids = list(graph.nodes)
        n_leaves = sum(1 for nid in all_ids if not index.get(nid))
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
        # Rows past h are dropped by the lines[:h] slice below, so painting them
        # is pure cost — and on a deep map it is the cost that dominates.
        body_h = min(max(tree_bottom + removed_h, h - 5), max(h, 1))

        have_total, req_total = graph.coverage()
        pct = round(100 * have_total / req_total) if req_total else 100

        lines: list[Text] = []
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

            parent = parents.get(nid)
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
