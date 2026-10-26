"""The matrix renderer — the traceability grid + the two-hop impact lens.

Lane L3, batch `2026-10-25-relmap-r2-batch`, increment 003.  The view the
operator chose at the prototype round (`d_matriz_lente = "matrix-panel"`):
the DSM grid on the left, the impact lens in a SEPARATE right panel, "the
grid stays clean" (`verdict-2026-10-24.json`; the layout reference is the
THROWAWAY `prototypes/round-2026-10-23/relmap/proto.py`, studied never
imported).

Layout, top to bottom, all painted into ONE audited `Canvas`
(LLR-RVM.4.1 — every label is pre-cut to its seat through the one sink
`base.label`, never leaning on `put` clipping):

* grid header — `row → col` and a right-aligned `matrix: <kinds> × <kinds>`
  note fitted inside the LEFT region (never over the panel);
* the column zone — the two-digit ruler (tens over ones) when the map
  sources test-side nodes, the `NN out of view` count when columns are
  windowed, or the verbatim declaration
  `no test columns yet — the AT→test table (B-141) feeds this view` when
  the map sources none (LLR-RVM.3.1 — ZERO phantom test-side cells);
* the grid rows — one per sourced node in input order: a right-aligned
  row number, a space, the id cut to a field between 8 and 12 cells, and
  one glyph cell per displayed column pair (diagonal `▪`, no edge `·`,
  strongest edge wins — ALERT-class before plain, then profile edge-type
  order; the frozen D5 glyph table).  Rows window to keep the selection
  visible, centred where the ends allow, and the flap under the grid
  declares `NN–NN / N`.  A row whose node can bind but has no binds edge
  bears the `○` badge in the gutter (ALERT when the node is open, MUT
  when it is closed or historical);
* the lens panel on the right (`what feeds it ←` / `a change reaches →`,
  `↑1`/`↑2`/`↓1`/`↓2` hop markers, edge input order, each member once,
  hop 2 ONLY through a drawn hop-1 member of the same direction, overflow
  counted `+NN more`); the summary `change <id> reaches N nodes` over
  `hop 1: n direct · hop 2: m chained` and the WARN reach gauge, against
  the greatest reach on the map.  A `None` reach (budget spent) renders
  `not computed` in WARN with an empty gauge — never a fabricated number;
* the legend row `✓ verifies · ! evidence missing · · no verifies edge`,
  cut to the viewport width.

Two readings are declared here and pinned by the tests (records proposed
in the increment packet):

* "lens widths below 60 cells" (LLR-RVM.2.1) reads as the VIEWPORT
  width: at the shipped 118/87 sizes the lens keeps its hop-2 rows
  (matching the operator-approved reference renders at both sizes) and
  folds them — counted, never dropped — below a 60-cell viewport.
* A spent-budget summary keeps the whole `not computed` text on the row:
  ` change <id>: not computed` — the wordy `reaches N nodes` frame would
  cut the mandated words at the shipped panel widths.

The viewport height: the host's `#relmap-canvas` is content-sized, so the
body height is derived from the active app's terminal size minus the four
chrome rows the host composes (TabStrip 2 + notice 1 + keybar 1), falling
back to `state.height` when no app context is active (the white-box
arms).  The matrix cursor axis is the node list (D1, amended); the one
toggle-state channel (COND-ARCH-1) owns `enter` only — the matrix lens,
state word `panel lens`; `c`/`k` are not this renderer's and answer `""`.
"""
from __future__ import annotations

from rich.text import Text
from textual.app import active_app

from mapper import darkside
from mapper.canvas import Canvas
from mapper.screens.relmap import base

#: Grid geometry (the header + the two ruler rows above the grid).
_GRID_TOP = 4
#: The id field is cut to between 8 and 12 cells (LLR-RVM.1.1).
_ID_MIN, _ID_MAX = 8, 12
#: The panel width follows the operator-approved prototype formula.
_PANEL_MIN, _PANEL_MAX = 30, 40
#: The gutter↔panel gap, both sides clear for the audit.
_GAP = 2
#: The chrome the host composes above/under the canvas (LLR-RVM.4.1's
#: viewport derivation: TabStrip 2 + notice 1 + keybar 1).
_CHROME_ROWS = 4
#: LLR-RVM.2.1: below a 60-cell viewport the lens folds its hop-2 rows.
_HOP2_FOLD_WIDTH = 60
#: The verbatim legend (LLR-RVM.1.3 / AT-133, Darkside casing).
_LEGEND = "✓ verifies · ! evidence missing · · no verifies edge"
#: The verbatim skeleton declaration (LLR-RVM.3.1 / AT-130).
_NO_TEST_COLUMNS = ("no test columns yet — the AT→test table (B-141) "
                    "feeds this view")
#: The selection tint (the prototype's focus treatment).
_TINT = f"bold {darkside.GROUND} on {darkside.ACCENT}"
#: The panel background margin style.
_PANEL_BG = f"on {darkside.PANEL}"

_EMPTY = "no node on record"


def _window(n: int, avail: int, at: int) -> range:
    """`avail` consecutive indices of `n`, centred on `at` where the ends
    allow (LLR-RVM.1.1)."""
    avail = max(0, min(avail, n))
    off = max(0, min(n - avail, at - avail // 2))
    return range(off, min(n, off + avail))


def _pair_index(m):
    """Every edge keyed by its UNORDERED endpoint pair."""
    idx: dict[tuple[str, str], list] = {}
    for e in m.edges:
        key = (e.src, e.dst) if e.src <= e.dst else (e.dst, e.src)
        idx.setdefault(key, []).append(e)
    return idx


def _between(index, a: str, b: str) -> list:
    key = (a, b) if a <= b else (b, a)
    return index.get(key, ())


def _winning_edge(edges, type_order):
    """The strongest edge of the pair: ALERT-class (evidence missing or
    in cycle) before plain, then profile edge-type order (LLR-RVM.1.2)."""
    if not edges:
        return None

    def key(e):
        return (0 if (e.evidence_missing or e.in_cycle) else 1,
                type_order.get(e.type, 99))

    return min(edges, key=key)


def _cell(edge):
    """The D5 glyph table for the winning edge: verifies `✓`/`!`, binds
    `●` bound / `◐` tagged, refines `•`, covers `≡`, empty pair `·`."""
    if edge is None:
        return "·", darkside.WORDMARK
    if edge.type == "verifies":
        if edge.evidence_missing or edge.in_cycle:
            return "!", darkside.ALERT
        return "✓", darkside.SAGE
    if edge.type == "binds":
        if edge.evidence_missing:
            return "◐", darkside.WARN
        return "●", darkside.SAGE
    if edge.type == "refines":
        return "•", darkside.MUT
    if edge.type == "covers":
        return "≡", darkside.MUT
    return "·", darkside.WORDMARK


def _evidence_glyph(edge):
    """The lens-row evidence glyph for verifies/binds edges."""
    if edge.type == "verifies":
        if edge.evidence_missing or edge.in_cycle:
            return "!", darkside.ALERT
        return "✓", darkside.SAGE
    if edge.type == "binds":
        if edge.evidence_missing:
            return "◐", darkside.WARN
        return "●", darkside.SAGE
    return "", ""


def _ring(m, sel: str, direction: str) -> list[tuple[str, int, str | None]]:
    """One direction of the lens ring: `(node id, hop, hop-1 parent)`.

    Hop 1 is the direct `up`/`down` of `sel` in edge input order; hop 2
    reaches ONLY through a drawn hop-1 member of the same direction, each
    node listed once (LLR-RVM.2.1, M-RVM-5's oracle).
    """
    adjacent = m.up if direction == "up" else m.down
    first = list(adjacent(sel))
    seen = set(first)
    seen.add(sel)
    rows = [(nid, 1, None) for nid in first]
    for h1 in first:
        for nid in adjacent(h1):
            if nid not in seen:
                seen.add(nid)
                rows.append((nid, 2, h1))
    return rows


def _test_side_kinds(m) -> set[str]:
    """The kinds that CHECK other nodes — srcs of a non-downstream edge
    type (the AT/TC checking side of the profile; the engine names no
    kind, so the renderer derives the set from the profile's direction
    flags)."""
    kinds = set()
    for t in m.profile.edge_types:
        if not t.downstream:
            kinds |= {src for src, _dst in t.pairs}
    return kinds


def _bind_kinds_and_types(m) -> tuple[set[str], set[str]]:
    """Kinds that can carry a graduated binds edge, and those edge types —
    for the `○` row badge (LLR-RVM.1.2)."""
    names = {t.name for t in m.profile.edge_types
             if t.evidence == "graduated"}
    kinds = set()
    for t in m.profile.edge_types:
        if t.name in names:
            kinds |= {src for src, _dst in t.pairs}
    return kinds, names


def _panel_width(w: int) -> int:
    pw = min(_PANEL_MAX, max(_PANEL_MIN, w // 3))
    if w - pw - _GAP < 12:  # degenerate narrow terminals: keep a gutter
        pw = max(10, w - _GAP - 12)
    return pw


def _framed(inner: Text, pw: int) -> Text:
    """The panel line: 1-cell margins and padding carry the PANEL
    background, exactly `pw` cells wide."""
    iw = max(0, pw - 2)
    pad = max(0, iw - inner.cell_len)
    out = Text(" ", style=_PANEL_BG)
    out.append_text(inner)
    if pad:
        out.append(" " * pad, _PANEL_BG)
    out.append(" ", _PANEL_BG)
    return out


def _blit(canvas: Canvas, x0: int, y: int, text: Text) -> None:
    """Paint an assembled, pre-fitted label into the canvas cell by cell
    (per-char styles preserved).  Every string was coerced and cut by the
    one sink before it gets here, so no write can leave the canvas."""
    if y < 0 or y >= canvas.h or x0 >= canvas.w:
        return
    plain = text.plain
    if not plain:
        return
    styles = [""] * len(plain)
    for span in text.spans:
        style = str(span.style) if span.style else ""
        for i in range(max(0, span.start), min(span.end, len(plain))):
            styles[i] = style
    for j, ch in enumerate(plain):
        canvas.put(x0 + j, y, ch, styles[j])


class MatrixView:
    """The traceability matrix + the two-hop impact lens panel."""

    name = "matrix"

    def __init__(self) -> None:
        self._lens = False

    # -- the frozen D1 surface ------------------------------------------------

    def toggle(self, kind: str) -> str:
        """COND-ARCH-1: `enter` owns the matrix lens (state word
        `panel lens`); `c`/`k` belong to the other renderers and own no
        state here.  The seat's out-of-view inertness is host-owned."""
        if kind != "enter":
            return ""
        self._lens = not self._lens
        return "panel lens" if self._lens else ""

    def row_count(self, state: base.ViewState) -> int:
        """The matrix cursor axis is the node list (D1, amended)."""
        if state.relmap is None:
            return 0
        return len(state.relmap.nodes)

    def paint(self, state: base.ViewState) -> list[Text]:
        w, h = self._viewport(state)
        audit: dict[str, list] = {"clip": [], "overprint": []}
        canvas = Canvas(w, h, audit=audit)
        if state.notice:
            # The renderer's notice obligation: the fixed refusal line IS
            # the body, through the one label sink, nothing beside it.
            _blit(canvas, 0, 0, base.label(state.notice, w))
            return canvas.rows()
        m = state.relmap
        if m is None or not m.nodes:
            self._paint_empty(canvas, w)
            return canvas.rows()
        id2idx = {n.id: i for i, n in enumerate(m.nodes)}
        sel_idx = id2idx.get(state.focus)
        if sel_idx is None:
            # LLR-RVM.3.2 / M-RVM-9: an unknown selection never raises.
            self._paint_empty(canvas, w)
            return canvas.rows()
        sel = m.nodes[sel_idx].id
        pw = _panel_width(w)
        left_end = w - pw - _GAP
        index = _pair_index(m)
        order = {t.name: i for i, t in enumerate(m.profile.edge_types)}
        show_hop2 = w >= _HOP2_FOLD_WIDTH
        # LLR-RVM.2.3: neighbourhood is consulted for the FOCUSED NODE
        # ONLY, once per paint, and only while the lens is on.
        nbh = m.neighbourhood(sel, 2) if self._lens else frozenset()

        self._paint_grid(canvas, m, sel, sel_idx, index, order, pw,
                         left_end, nbh, h)
        self._paint_panel(canvas, m, sel, index, order, pw, h, show_hop2)
        return canvas.rows()

    # -- viewport --------------------------------------------------------------

    @staticmethod
    def _viewport(state: base.ViewState) -> tuple[int, int]:
        """The canvas is content-sized, so the body height derives from
        the active terminal minus the host's chrome rows; the white-box
        arms (no app context) drive the renderer through `state`."""
        w = max(1, state.width)
        h = max(1, state.height)
        try:
            app = active_app.get()
        except LookupError:
            return w, h
        screen_h = app.size.height or 0
        if screen_h:
            h = max(h, screen_h - _CHROME_ROWS)
        return w, h

    def _paint_empty(self, canvas: Canvas, w: int) -> None:
        """LLR-RVM.3.2: zero nodes or an unknown selection — the matrix
        and the lens print nothing but the declared state."""
        pw = _panel_width(w)
        left_end = max(1, w - pw - _GAP)
        _blit(canvas, 0, 1, base.label(_EMPTY, left_end))
        _blit(canvas, w - pw, 1, base.label(_EMPTY, pw))

    # -- the grid ---------------------------------------------------------------

    def _paint_grid(self, canvas, m, sel, sel_idx, index, order, pw,
                    left_end, nbh, h) -> None:
        nodes = m.nodes
        numw = max(2, len(str(len(nodes))))
        idw = max(_ID_MIN,
                  min(_ID_MAX, max(darkside.shown_cells(n.id) for n in nodes)))
        lw = numw + 1 + idw + 1
        col_kinds = _test_side_kinds(m)
        cols = [n for n in nodes if n.kind in col_kinds]
        col_ids = [n.id for n in cols]
        ci = col_ids.index(sel) if sel in col_ids else 0
        dim_row = [self._lens and nodes[i].id not in nbh
                   for i in range(len(nodes))]
        dim_col = [self._lens and cid not in nbh for cid in col_ids]

        _blit(canvas, 0, 0, base.label("row → col",
                                       darkside.shown_cells("row → col"),
                                       f"bold {darkside.INK}"))
        row_kinds = []
        for n in nodes:
            if n.kind not in row_kinds:
                row_kinds.append(n.kind)
        note = f"matrix: {', '.join(row_kinds)} × " + (
            ", ".join(dict.fromkeys(n.kind for n in cols)) or "—")
        header_w = darkside.shown_cells("row → col")
        note_w = min(darkside.shown_cells(note),
                     max(0, left_end - header_w - 1))
        if note_w:
            _blit(canvas, left_end - note_w - 1, 0,
                  base.label(note, note_w, darkside.MUT))

        col_window = range(0)
        if not cols:
            # LLR-RVM.3.1: the verbatim declaration where the column
            # header would sit, and ZERO phantom test-side cells.
            _blit(canvas, 0, 1,
                  base.label(_NO_TEST_COLUMNS, max(0, left_end),
                             darkside.MUT))
        else:
            col_avail = max(0, left_end - lw)
            col_window = _window(len(cols), col_avail, ci)
            if len(col_window) < len(cols):
                marker = f"{len(cols) - len(col_window):02d} out of view"
                marker_w = min(darkside.shown_cells(marker),
                               max(0, left_end))
                _blit(canvas, max(0, left_end - marker_w), 1,
                      base.label(marker, marker_w, darkside.MUT))
            for k, j in enumerate(col_window):
                num = j + 1
                for y, digit in ((2, str(num // 10) if num >= 10 else " "),
                                 (3, str(num % 10))):
                    if col_ids[j] == sel:
                        style = _TINT
                    elif dim_col[j]:
                        style = f"dim {darkside.MUT}"
                    else:
                        style = darkside.MUT
                    canvas.put(lw + k, y, digit, style)

        row_avail = max(0, h - _GRID_TOP - 2)
        row_window = _window(len(nodes), row_avail, sel_idx)
        bind_kinds, bind_types = _bind_kinds_and_types(m)
        bound_nodes = {e.src for e in m.edges if e.type in bind_types} | {
            e.dst for e in m.edges if e.type in bind_types}
        for r, i in enumerate(row_window):
            y = _GRID_TOP + r
            node = nodes[i]
            if node.id == sel:
                gutter_style = _TINT
            elif dim_row[i]:
                gutter_style = f"dim {darkside.INK}"
            else:
                gutter_style = darkside.INK
            _blit(canvas, 0, y, base.label(
                f"{i + 1:>{numw}} {node.id}", lw, gutter_style))
            if node.kind in bind_kinds and node.id not in bound_nodes:
                badge_style = (darkside.ALERT if node.open else darkside.MUT)
                if node.id == sel:
                    badge_style = _TINT
                elif dim_row[i]:
                    badge_style = f"dim {badge_style}"
                _blit(canvas, 0, y, base.label("○", 1, badge_style))
            if cols:
                for k, j in enumerate(col_window):
                    rid, cid = node.id, col_ids[j]
                    if rid == cid:
                        glyph, style = "▪", darkside.MUT
                    else:
                        glyph, style = _cell(
                            _winning_edge(_between(index, rid, cid), order))
                    if rid == sel or cid == sel:
                        style = _TINT
                    canvas.put(lw + k, y, glyph, style)

        flap_y = _GRID_TOP + len(row_window)
        if cols:
            _blit(canvas, lw, flap_y,
                  base.label("▁" * len(col_window), len(col_window),
                             darkside.WORDMARK))
        # review-inc003 F2: at degenerate body heights the row window is
        # empty and `stop` is 0 — clamp the flap's window end so it can
        # never read `01–00 / N`.
        label = f"{row_window.start + 1:02d}–{max(1, row_window.stop):02d} / {len(nodes)}"
        span = max(len(col_window), max(0, left_end - lw))
        label_w = min(darkside.shown_cells(label), span)
        _blit(canvas, lw + max(0, (span - label_w) // 2), flap_y,
              base.label(label, label_w, darkside.MUT))
        _blit(canvas, 1, h - 1, base.label(_LEGEND, max(0, canvas.w - 2),
                                           darkside.MUT))

    # -- the lens panel ----------------------------------------------------------

    def _paint_panel(self, canvas, m, sel, index, order, pw, h,
                     show_hop2) -> None:
        iw = max(1, pw - 2)
        x0 = canvas.w - pw
        node = m.node(sel)

        def emit(lines: list[Text]) -> None:
            # The last canvas row belongs to the legend — the panel
            # never paints there (no collision at degenerate heights).
            for y, line in enumerate(lines[:max(0, h - 1)]):
                _blit(canvas, x0, y, _framed(line, pw))

        lines: list[Text] = [
            base.label(f" lens · {sel}", iw, f"bold {darkside.INK} "
                                             f"on {darkside.STEP}"),
        ]
        if node is not None and node.title:
            lines.append(base.label(f" {node.title}", iw, darkside.MUT))
        lines.append(base.label(" what feeds it ←", iw, darkside.MUT))

        up_rows, up_folded = self._ring_lines(m, sel, index, order, "up",
                                              iw, show_hop2)
        down_rows, down_folded = self._ring_lines(m, sel, index, order,
                                                  "down", iw, show_hop2)
        both_empty = (not up_rows and not down_rows
                      and not up_folded and not down_folded)
        block: list[Text] = []
        if not both_empty:
            if up_rows:
                block += up_rows
            elif not up_folded:
                block.append(base.label(" ╌╌╌ root — nothing feeds it", iw,
                                        darkside.MUT))
        if up_folded:
            block.append(base.label(f" ╌╌ +{up_folded:02d} more", iw,
                                    darkside.MUT))
        block.append(base.label(" a change reaches →", iw, darkside.MUT))
        if both_empty or (not down_rows and not down_folded):
            block.append(base.label(" ╌╌╌ relates to nothing", iw,
                                    darkside.ALERT))
        else:
            block += down_rows
            if down_folded:
                block.append(base.label(f" ╌╌ +{down_folded:02d} more", iw,
                                        darkside.MUT))

        # Overflow members are counted `+NN more`, never dropped silently;
        # the last canvas row belongs to the legend (the emit cap) and the
        # summary/hop/gauge tail (3 lines) is always owed its room.
        budget = max(0, h - 1 - len(lines) - 3)
        if len(block) <= budget:
            lines += block
        else:
            shown = block[:max(0, budget - 1)]
            skipped = len(block) - len(shown)
            lines += shown
            lines.append(base.label(f" ╌╌ +{skipped:02d} more", iw,
                                    darkside.MUT))

        reach = m.reach(sel)
        down_ring = _ring(m, sel, "down")
        down1 = sum(1 for _n, hop, _p in down_ring if hop == 1)
        down2 = sum(1 for _n, hop, _p in down_ring if hop == 2)
        if reach is None:
            # LLR-RVM.2.2: never a fabricated number; the WARN words stay
            # whole on the row (the packet records the presentation).
            inner = Text()
            inner.append_text(base.label(f" change {sel}: ", iw,
                                         f"bold {darkside.INK}"))
            room = max(0, iw - darkside.shown_cells(f" change {sel}: "))
            inner.append_text(base.label("not computed", room, darkside.WARN))
            lines.append(inner)
        else:
            lines.append(base.label(
                f" change {sel} reaches {reach} nodes", iw,
                f"bold {darkside.INK}"))
        lines.append(base.label(
            f" hop 1: {down1} direct · hop 2: {down2} chained", iw,
            darkside.MUT))
        reaches = [r for n in m.nodes if (r := m.reach(n.id)) is not None]
        gauge = Text()
        gauge.append_text(base.label(" reach  ", 8, ""))
        gauge.append_text(darkside.microbar(reach or 0, max(reaches, default=0),
                                            width=10, fill=darkside.WARN))
        if reach is None:
            room = max(0, iw - 18)
            gauge.append_text(base.label(" not computed", room, darkside.WARN))
        else:
            gauge.append_text(base.label(f" {reach:02d}", 3, darkside.INK))
        lines.append(gauge)
        emit(lines)

    def _ring_lines(self, m, sel, index, order, direction, iw, show_hop2):
        """The ring rows (Text, pre-fitted) plus the folded hop-2 count.
        Single-spaced so the rows read exactly as the acceptance strings
        pin them (`↑1 refines <id>`)."""
        rows = _ring(m, sel, direction)
        arrow = "↑" if direction == "up" else "↓"
        lines = []
        folded = 0
        for nid, hop, parent in rows:
            if hop == 2 and not show_hop2:
                folded += 1
                continue
            tone = darkside.INK if hop == 1 else darkside.MUT
            if hop == 1:
                edges = _between(index, nid, sel)
            else:
                edges = (_between(index, nid, parent)
                         or _between(index, parent, sel))
            edge = _winning_edge(edges, order)
            etype = edge.type if edge is not None else "relates"
            glyph, gstyle = ("", "")
            if edge is not None:
                glyph, gstyle = _evidence_glyph(edge)
            id_w = max(1, iw - 4 - len(etype) - (2 if glyph else 0))
            line = Text()
            line.append_text(base.label(f"{arrow}{hop} ", 3, tone))
            line.append_text(base.label(etype, len(etype), darkside.VIOLET))
            line.append_text(base.label(" ", 1, ""))
            # the id and its evidence glyph read as one segment (`TC-1 !`),
            # the id coerced and cut by the seam before the glyph lands
            id_cut = darkside.fit(nid, id_w).rstrip()
            line.append(id_cut, tone)
            if glyph:
                line.append(f" {glyph}", gstyle)
            lines.append(line)
        return lines, folded


def build_view() -> MatrixView:
    """The wiring convention (D1): `mapper/screens/relmap/<name>.py`
    exposes `build_view() -> RelMapView`."""
    return MatrixView()
