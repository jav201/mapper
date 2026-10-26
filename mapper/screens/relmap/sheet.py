"""The node-sheet renderer (lane L5, increment 005, batch
`2026-10-25-relmap-r2-batch`).

The sheet is the focused node's ficha over the frozen D1 surface
(`mapper/screens/relmap/base.py`): a two-row header (`<id> · <title>` bold
INK + the `darkside.kind_chip` badge, no source segment — the D3 `Node`
exposes none), two banded sections — `feeds it` (`RelMap.up`, a change at
them reaches this node) and `a change reaches` (`RelMap.down`) — with the
frozen D5 evidence-glyph column, the `gaps on this node` band over the
host-supplied ranked rows, and the `next ▸` density note.

The one toggle kind is `c` (LLR-RVS.3.3, COND-ARCH-1): direct density lists
hop-1 neighbours and DECLARES the hop-2 cut (`╌╌ +NN more upstream/downstream
at hop 2 — c shows the chain`, per-direction minimum-distance-2 counts,
omitted at zero); stacked density lists every distinct node by per-direction
minimum hop (`↑N`/`↓N`), unbounded in depth, with the counted `… +NN more`
viewport line as the safety valve.  The crumb words are `direct only` /
`stacked chain`; `enter`/`k` are not ours and return `""`.

Every canon-derived label is coerced through `darkside.plain` and cut through
`darkside.fit` BEFORE it is styled (the C-10 order), and the rows are blitted
onto a `mapper.canvas.Canvas` so the C10 audit mapping (constructor-injected)
records every out-of-bounds or overprinting write.  Evidence names are labels
only: no file-opener import, no attachment (LLR-RVS.7.1).  The row axis is
the node list — the host's cursor moves the node selection (D1, amended).
"""
from __future__ import annotations

from rich.cells import cell_len
from rich.text import Text

from mapper import darkside
from mapper.canvas import Canvas
from mapper.screens.relmap import base

_FEEDS_BAND = "feeds it — what a change to them does to this node"
_REACHES_BAND = "a change reaches — what changing this node forces"
_GAPS_BAND = "gaps on this node"
_EMPTY = "╌╌ none on record"
_NO_NODES = "╌╌ no nodes on record"
_DIRECT_NOTE = "direct feeders only — the chain is one key away, and the cut is declared"
_STACKED_NOTE = "feeds it and a change reaches come free from the engine (§3.4 C12)"
_WORD_DIRECT = "direct only"
_WORD_STACKED = "stacked chain"

#: The viewport-height floor for the degenerate mount-time paint: the host's
#: canvas ``Static`` is auto-height, so the first paint arrives with height
#: 1.  An explicit viewport height is always respected (the sweep arms drive
#: heights directly); the degenerate 1 paints the honest default body (chrome
#: 3 + body 21, inside the 34-row reference class), which the growing widget
#: then reports back as a real height.
_DEFAULT_BODY = 24

#: The D5 evidence-glyph table (LLR-RVS.2.3): keyed on the edge TYPE; the
#: `○` no-binds-edge badge is a matrix row badge and never appears here.


def _evidence_glyph(etype: str, edge) -> tuple[str, str] | None:
    """One glyph for an edge's evidence state, keyed on the edge type."""
    if etype in ("verifies", "covers"):
        if edge.evidence_missing or edge.in_cycle:
            return ("!", darkside.ALERT)
        return ("✓", darkside.SAGE)
    if etype == "binds":
        if edge.evidence_missing:
            return ("◐", darkside.WARN)
        return ("●", darkside.SAGE)
    return None


def _layers(m, focus: str, direction: str, max_hop: int | None):
    """Per-direction minimum-hop layering through the D3 query surface
    (`up`/`down` — never renderer-private adjacency): [(node, predecessor,
    hop)] in hop-then-edge-input order (first discovery wins)."""
    step = m.up if direction == "up" else m.down
    seen = {focus}
    frontier = (focus,)
    layers = []
    hop = 0
    while frontier and (max_hop is None or hop < max_hop):
        hop += 1
        fresh = []
        for node in frontier:
            for nb in step(node):
                if nb not in seen:
                    seen.add(nb)
                    layers.append((nb, node, hop))
                    fresh.append(nb)
        frontier = fresh
    return layers


def _budget(height: int) -> int:
    """The painted row count: an explicit viewport height is respected; the
    degenerate mount-time 1 paints the honest default body."""
    return max(height if height > 1 else _DEFAULT_BODY, 1)


def _edge_index(m):
    """The first edge (edge input order) for every change-flow endpoint pair
    — the profile's direction bit orients each edge exactly the way
    ``build_map`` does, so an upstream-type edge (verifies/binds/covers) is
    indexed by ``(dst, src)``."""
    types = {t.name: t for t in m.profile.edge_types}
    index = {}
    for e in m.edges:
        t = types[e.type]
        key = (e.src, e.dst) if t.downstream else (e.dst, e.src)
        index.setdefault(key, e)
    return index


def _edge_for(index, pred: str, nb: str, direction: str):
    """The connecting edge for a chain row one hop from *pred* to *nb*: an
    up-row names the edge whose change flows nb -> pred (toward the focus);
    a down-row the edge whose change flows pred -> nb (away from it)."""
    key = (nb, pred) if direction == "up" else (pred, nb)
    return index.get(key)


class SheetView:
    """The node-sheet renderer over the frozen surface.  `audit` is the
    optional C10 mapping the sweep arms inject at construction; production
    wiring (`build_view()`) runs without one."""

    name = "sheet"

    def __init__(self, audit=None) -> None:
        self._audit = audit
        self._stacked = False

    # -- the frozen D1 entries ------------------------------------------------

    def paint(self, state: base.ViewState) -> list[Text]:
        w, h = max(state.width, 1), _budget(state.height)
        canvas = Canvas(w, h, audit=self._audit)
        if state.notice:
            self._emit(canvas, 0, base.label(state.notice, w))
            return canvas.rows()
        node = state.relmap.node(state.focus) if state.relmap and state.focus else None
        if node is None:
            self._emit(canvas, 0, base.label(_NO_NODES, w, darkside.MUT))
            return canvas.rows()
        rows = self._content(state.relmap, node, state.gaps)
        if len(rows) > h:
            shown = rows[: h - 1]
            hidden = len(rows) - len(shown)
            rows = shown + [("text", f"… +{hidden:02d} more", darkside.MUT)]
        for y, descriptor in enumerate(rows[:h]):
            self._emit(canvas, y, self._render(descriptor, w))
        return canvas.rows()

    def row_count(self, state: base.ViewState) -> int:
        """The sheet axis is the node list (D1, amended): the host's cursor
        moves the node selection."""
        if state.relmap is None:
            return 0
        return len(state.relmap.nodes)

    def toggle(self, kind: str) -> str:
        """`c` flips the chain density and returns the crumb word; the other
        kinds are not the sheet's and return ``""`` (COND-UX-1)."""
        if kind != "c":
            return ""
        self._stacked = not self._stacked
        return _WORD_STACKED if self._stacked else _WORD_DIRECT

    # -- content ---------------------------------------------------------------

    def _content(self, m, node, gaps) -> list[tuple]:
        focus = node.id
        edges = _edge_index(m)
        up_layers = _layers(m, focus, "up", None if self._stacked else 2)
        down_layers = _layers(m, focus, "down", None if self._stacked else 2)
        rows: list[tuple] = [("header", node), ("chip", node.kind)]
        rows.append(("band", _FEEDS_BAND))
        rows += self._chain_rows(m, edges, up_layers, "up", focus)
        if not self._stacked:
            n_up = sum(1 for _, _, hop in up_layers if hop == 2)
            if n_up:
                rows.append(("text",
                             f"╌╌ +{n_up:02d} more upstream at hop 2 — c shows the chain",
                             darkside.MUT))
        rows.append(("band", _REACHES_BAND))
        rows += self._chain_rows(m, edges, down_layers, "down", focus)
        if not self._stacked:
            n_down = sum(1 for _, _, hop in down_layers if hop == 2)
            if n_down:
                rows.append(("text",
                             f"╌╌ +{n_down:02d} more downstream at hop 2 — c shows the chain",
                             darkside.MUT))
        rows.append(("band", _GAPS_BAND))
        mine = [g for g in gaps if g.node == focus]
        if mine:
            rows += [("gap", g.kind, g.sentence) for g in mine]
        else:
            rows.append(("text", _EMPTY, darkside.MUT))
        rows.append(("note", _STACKED_NOTE if self._stacked else _DIRECT_NOTE))
        return rows

    def _chain_rows(self, m, edges, layers, direction, focus) -> list[tuple]:
        """The section rows: direct density shows hop 1 only (the hop-2 cut is
        declared by the caller); stacked shows every layer.  An empty section
        paints the declared empty line — never skipped."""
        limit = None if self._stacked else 1
        out = []
        for nb, pred, hop in layers:
            if limit is not None and hop > limit:
                continue
            edge = _edge_for(edges, pred, nb, direction)
            etype = darkside.plain(edge.type.lower()) if edge is not None else "?"
            glyph = _evidence_glyph(etype, edge) if edge is not None else None
            out.append(("chain", direction == "up", hop, etype, nb, glyph))
        if not out:
            out.append(("text", _EMPTY, darkside.MUT))
        return out

    # -- rendering --------------------------------------------------------------

    def _render(self, descriptor: tuple, w: int) -> Text:
        kind = descriptor[0]
        if kind == "header":
            node = descriptor[1]
            return base.label(f"{node.id} · {node.title}", w, f"bold {darkside.INK}")
        if kind == "chip":
            chip = darkside.kind_chip(darkside.plain(descriptor[1]))
            if chip.cell_len < w:
                chip.append(" " * (w - chip.cell_len))
            return chip
        if kind == "band":
            return Text(darkside.fit(f" {descriptor[1]} ", w),
                        style=f"bold {darkside.INK} on {darkside.STEP}")
        if kind == "text":
            return base.label(descriptor[1], w, descriptor[2])
        if kind == "chain":
            return _render_chain(descriptor, w)
        if kind == "gap":
            return _render_gap(descriptor, w)
        return _render_note(descriptor, w)

    @staticmethod
    def _emit(canvas: Canvas, y: int, row: Text) -> None:
        """Blit ONE fitted row onto the canvas cell by cell, carrying each
        span's explicit style — the audit mapping sees every write."""
        if y >= canvas.h:
            return
        spans = [(s.start, s.end, s.style or "") for s in row.spans]
        x = 0
        for i, ch in enumerate(row.plain):
            style = ""
            for s0, s1, st in spans:
                if s0 <= i < s1:
                    style = st
                    break
            canvas.put(x, y, ch, style)
            x += cell_len(ch)


def _render_chain(descriptor: tuple, w: int) -> Text:
    """`↑1 refines HLR-X` (marker + type VIOLET, id INK, one evidence glyph);
    the id absorbs the width cut — coercion first, cut second (C-10)."""
    _, up, hop, etype, nid, glyph = descriptor
    marker = ("↑" if up else "↓") + str(hop)
    gtext, gstyle = glyph if glyph else ("", "")
    reserve = cell_len(gtext) + (1 if glyph else 0)
    id_budget = w - (cell_len(marker) + 1) - cell_len(etype) - 1 - reserve
    if id_budget < 1:
        etype = darkside.fit(etype, max(1, w - cell_len(marker) - 2 - reserve))
        id_budget = w - (cell_len(marker) + 1) - cell_len(etype) - 1 - reserve
    id_part = darkside.fit(darkside.plain(nid), id_budget).rstrip() if id_budget >= 1 else ""
    line = Text()
    line.append(f"{marker} ", darkside.VIOLET)
    line.append(etype, darkside.VIOLET)
    line.append(" ")
    line.append(id_part, darkside.INK if hop == 1 else darkside.MUT)
    if glyph:
        line.append(f" {gtext}", gstyle)
    if line.cell_len < w:
        line.append(" " * (w - line.cell_len))
    return line


def _render_gap(descriptor: tuple, w: int) -> Text:
    """`! <kind>  <sentence>` — kind in bold ALERT (Darkside-cased), sentence
    in MUT, both coerced and the sentence cut to the row width with one
    trailing ellipsis."""
    _, kind, sentence = descriptor
    kind_part = darkside.plain(kind).lower()
    head = f"! {kind_part}  "
    budget = w - cell_len(head)
    if budget < 1:
        kind_part = darkside.fit(kind_part, max(1, w - 5))
        head = f"! {kind_part}  "
        budget = w - cell_len(head)
    sent = darkside.fit(darkside.plain(sentence), budget) if budget >= 1 else ""
    line = Text()
    line.append("! ")
    line.append(kind_part, f"bold {darkside.ALERT}")
    line.append("  ")
    line.append(sent, darkside.MUT)
    if line.cell_len < w:
        line.append(" " * (w - line.cell_len))
    return line


def _render_note(descriptor: tuple, w: int) -> Text:
    """The `next ▸` density note through `darkside.hint_line` (the renderer
    owns the text; the host owns the binding and the crumb slot)."""
    line = darkside.hint_line(descriptor[1])
    if line.cell_len < w:
        line.append(" " * (w - line.cell_len))
    return line


def build_view() -> SheetView:
    """The wiring convention (D1): `base.build_view("sheet")` calls this."""
    return SheetView()
