"""The ranked-gaps renderer (batch `2026-10-25-relmap-r2-batch`, lane L4,
increment 004).

The view renders ONE row per detected gap in the order the host supplies in
``ViewState.gaps`` — already ranked by ``rank_gaps`` (severity, then reach
descending, detection order on ties) — and never re-sorts, re-filters or
invents rows (LLR-RVG.1.1): the painted rows always come from ``state.gaps``
in its exact order.  The one thing re-derived here is the not-computed count
(the second member of the SAME deterministic, memoized ranking call the host
made — the D1 surface carries only the ranked tuple), declared on the tally
and never fabricated (LLR-RVG.2.3).

Layout over the frozen surface: a header naming the ranking, the always-four
tally chips, the field band, then the ranked rows — zero-padded rank, the gap
kind in Darkside casing (a case-only transform, LLR-RVG.2.1), the node id,
the WHAT sentence, the zero-padded three-digit reach count (the only reach
visual — no microbar, LLR-RVG.1.3) and the severity word.  Rows that do not
fit the body window are declared as cut markers (``+NN above`` / ``+NN
more``) and the window follows the host cursor; a WHAT value that does not
fit ends with a single ellipsis, and below its 12-cell minimum the WHAT
column drops WHOLE rather than truncating (LLR-RVG.1.4).

`k` regroups the same catalogue into one band per gap kind in catalogue
order — band head with the kind label, the member count and the band's worst
severity, member rows keeping their global rank numbers, a hint line naming
the grouping, and a counted ``+NN more`` marker when the bands overflow the
window (LLR-RVG.1.5).  Pressing `k` again returns the ranked frame
byte-identical.

Every canon-derived string (kind, node id, sentence) passes through
``darkside.plain`` and the one label sink (``base.label`` — ``_row_text`` /
``fit`` into explicit-style ``Text``), so a hostile payload renders literally
on one row with no style leak and no markup parse (LLR-RVG.3.1, C8/C-17).

The shipped host's canvas ``Static`` is auto-height: on the first paint the
viewport height channel carries the degenerate 1.  Below a small floor the
renderer paints an honest default body (24 rows) instead of a one-line view;
an explicit viewport height is always respected, so the window budget is
exactly testable (LLR-RVG.1.4's sweep drives heights directly).
"""
from __future__ import annotations

from rich.text import Text

from mapper import darkside as D
from mapper.relmap.gaps import rank_gaps
from mapper.relmap.profile import SEVERITIES
from mapper.screens.relmap import base

_NAME = "gaps"
_TITLE = "gaps — what the record does not say"
_NOTE = "ranked by severity, then reach ↓"
_EMPTY = "no gaps on record"
_HINT = "same catalogue grouped by gap kind — scan for a detector, not a severity"
_NOT_COMPUTED = "reach not computed: {}"

#: The viewport-height floor for the degenerate first paint (see the module
#: docstring): chrome 3 + body 21, well inside the 34-row reference class.
_DEFAULT_BODY = 24
#: Below this WHAT width the column drops whole (LLR-RVG.1.4).
_WHAT_MIN = 12
_NODE_W = 12

_SEV_STYLE = dict(zip(SEVERITIES, (D.ALERT, D.INK, D.MUT)))
_SEV_WORD = {sev: sev.lower() for sev in SEVERITIES}


def _budget(height: int) -> int:
    """The painted row count: an explicit viewport height is respected
    (2–3 paint 2–3 — review-inc004 F1 tightened the floor to the
    degenerate value only); the degenerate mount-time 1 paints the honest
    default body."""
    return max(height if height > 1 else _DEFAULT_BODY, 1)


def _cased(kind: str) -> str:
    """A catalogue kind in Darkside casing — a case-only transform whose
    result is otherwise byte-identical to the kind string."""
    return D.plain(kind).lower()


def _kind_width(gaps) -> int:
    return min(26, max(D.shown_cells(_cased(g.kind)) for g in gaps))


def _rank_width(n: int) -> int:
    return max(2, len(str(n)))


def _columns(w: int, kind_w: int, rank_w: int):
    """The column geometry: (x_kind, x_node, x_what, x_reach, x_sev,
    what_w, show_what).  The WHAT column drops whole below `_WHAT_MIN`."""
    x_kind = rank_w + 3
    x_node = x_kind + kind_w + 2
    x_what = x_node + _NODE_W + 2
    x_reach = w - 16
    x_sev = w - 7
    what_w = x_reach - 2 - x_what
    show_what = what_w >= _WHAT_MIN
    return (x_kind, x_node, x_what, x_reach, x_sev, what_w, show_what)


def _window(n: int, body: int, at: int):
    """The body window, centred on `at` where the ends allow, reserving one
    body row per cut marker.  Returns (off, end, above, below): `above` and
    `below` are the undeclared-row counts the markers must name."""
    slot = body
    off = end = above = below = 0
    for _ in range(3):
        off = max(0, min(n - slot, at - slot // 2))
        end = min(n, off + slot)
        above, below = off, n - end
        need = (1 if above else 0) + (1 if below else 0)
        if body - need == slot:
            break
        slot = body - need
    return off, end, above, below


def _header(w: int) -> Text:
    note_w = D.shown_cells(_NOTE)
    row = base.label(_TITLE, max(1, w - note_w - 1), f"bold {D.INK}")
    row.append_text(base.label(" ", 1))
    row.append_text(base.label(_NOTE, note_w, D.MUT))
    return row


def _tally(gaps, not_computed: int) -> Text:
    row = Text()
    for sev in SEVERITIES:
        n = sum(1 for g in gaps if g.severity == sev)
        word = f"{_SEV_WORD[sev]} {n}"
        row.append_text(base.label(word, D.shown_cells(word), _SEV_STYLE[sev]))
        row.append_text(base.label("   ", 3))
    total = f"total {len(gaps)}"
    row.append_text(base.label(total, D.shown_cells(total), f"bold {D.INK}"))
    if not_computed:
        row.append_text(base.label("   ", 3))
        marker = _NOT_COMPUTED.format(not_computed)
        row.append_text(base.label(marker, D.shown_cells(marker), D.WARN))
    return row


def _fields(w: int, geo, kind_w: int, rank_w: int) -> Text:
    x_kind, x_node, x_what, x_reach, x_sev, what_w, show_what = geo
    row = Text()
    row.append_text(base.label("no", rank_w, f"bold {D.MUT}"))
    row.append_text(base.label("", x_kind - rank_w))
    row.append_text(base.label("gap", kind_w, f"bold {D.MUT}"))
    row.append_text(base.label("", 2))
    row.append_text(base.label("node", _NODE_W, f"bold {D.MUT}"))
    row.append_text(base.label("", 2))
    if show_what:
        row.append_text(base.label("what", what_w, f"bold {D.MUT}"))
        row.append_text(base.label("", max(0, x_reach - x_what - what_w)))
    else:
        row.append_text(base.label("", max(0, x_reach - row.cell_len)))
    row.append_text(base.label("reach", 5, f"bold {D.MUT}"))
    row.append_text(base.label("", max(0, x_sev - x_reach - 5)))
    row.append_text(base.label("status", w - x_sev, f"bold {D.MUT}"))
    return row


def _gap_row(gap, index: int, w: int, geo, kind_w: int, rank_w: int,
             cursor: bool) -> Text:
    x_kind, x_node, x_what, x_reach, x_sev, what_w, show_what = geo
    row = Text()
    row.append_text(base.label(f"{index + 1:02d}", rank_w, D.MUT))
    row.append_text(base.label("", x_kind - rank_w))
    row.append_text(base.label(_cased(gap.kind), kind_w, D.INK))
    row.append_text(base.label("", 2))
    row.append_text(base.label(D.plain(gap.node), _NODE_W, f"bold {D.INK}"))
    row.append_text(base.label("", 2))
    if show_what:
        row.append_text(base.label(D.plain(gap.sentence), what_w, D.MUT))
    row.append_text(base.label("", max(0, x_reach - row.cell_len)))
    reach = f"{gap.reach:03d}"
    reach_w = max(3, D.shown_cells(reach))
    row.append_text(base.label(reach, reach_w, D.INK))
    row.append_text(base.label("", max(0, x_sev - x_reach - reach_w)))
    row.append_text(
        base.label(_SEV_WORD[gap.severity], w - x_sev, _SEV_STYLE[gap.severity])
    )
    if cursor:
        row.stylize(f"on {D.STEP}")
    return row


def _bands(gaps, profile):
    """The by-kind grouping: one band per kind present, in catalogue (table)
    order, each over exactly its own ranked members, in ranked order."""
    members: dict[str, list[int]] = {}
    for i, g in enumerate(gaps):
        members.setdefault(g.kind, []).append(i)
    return [(row.kind, members[row.kind]) for row in profile.gaps
            if row.kind in members]


def _band_head(kind: str, count: int, worst: str, w: int, kind_w: int) -> Text:
    step = f"on {D.STEP}"
    row = Text()
    row.append_text(base.label(f" {_cased(kind)}", kind_w + 1, f"bold {D.INK} {step}"))
    row.append_text(base.label("  ", 2, step))
    row.append_text(base.label(_SEV_WORD[worst], 5, f"bold {_SEV_STYLE[worst]} {step}"))
    row.append_text(base.label(f" ×{count}", 4, f"{D.INK} {step}"))
    row.append_text(base.label("", max(0, w - row.cell_len), step))
    return row


class GapsView:
    """The gaps renderer over the frozen D1 surface (see `base.RelMapView`)."""

    name = _NAME

    def __init__(self) -> None:
        self._by_kind = False

    # -- the frozen surface -------------------------------------------------

    def toggle(self, kind: str) -> str:
        """`k` owns this renderer's grouping state; every other kind is not
        ours (COND-ARCH-1: the host calls us only on our home view)."""
        if kind != "k":
            return ""
        self._by_kind = not self._by_kind
        return "by kind" if self._by_kind else ""

    def row_count(self, state: base.ViewState) -> int:
        """The gaps cursor axis is the ranked-gap rows (D1, amended)."""
        if state.relmap is None:
            return 0
        return len(state.gaps)

    def paint(self, state: base.ViewState) -> list[Text]:
        w = state.width
        budget = _budget(state.height)
        if state.notice:
            rows = [base.label(state.notice, w)]
            return rows + [base.label("", w)] * (budget - 1)
        if not state.gaps:
            return self._empty_frame(w, budget)
        if self._by_kind:
            return self._by_kind_frame(state, w, budget)
        return self._ranked_frame(state, w, budget)

    # -- frames -------------------------------------------------------------

    def _chrome(self, state, w, kind_w, rank_w):
        geo = _columns(w, kind_w, rank_w)
        return [
            _header(w),
            _tally(state.gaps, self._not_computed(state)),
            _fields(w, geo, kind_w, rank_w),
        ], geo

    def _ranked_frame(self, state, w, budget) -> list[Text]:
        gaps = state.gaps
        kind_w = _kind_width(gaps)
        rank_w = _rank_width(len(gaps))
        chrome, geo = self._chrome(state, w, kind_w, rank_w)
        rows = list(chrome)
        body = budget - 3
        n = len(gaps)
        if n <= body:
            off, end, above, below = 0, n, 0, 0
        else:
            off, end, above, below = _window(n, body, state.cursor)
        if above:
            rows.append(base.label(f"+{above:02d} above", w, D.MUT))
        for i in range(off, end):
            rows.append(_gap_row(gaps[i], i, w, geo, kind_w, rank_w,
                                 cursor=(i == state.cursor)))
        if below:
            rows.append(base.label(f"+{below:02d} more", w, D.MUT))
        while len(rows) < budget:
            rows.append(base.label("", w))
        return rows[:budget]

    def _by_kind_frame(self, state, w, budget) -> list[Text]:
        gaps = state.gaps
        kind_w = _kind_width(gaps)
        rank_w = _rank_width(len(gaps))
        chrome, geo = self._chrome(state, w, kind_w, rank_w)
        rows = list(chrome)
        body = budget - 3
        band_area = body - 1  # the hint is bottom-anchored on the last row
        bands = _bands(gaps, state.relmap.profile)
        needed = sum(1 + len(idxs) for _, idxs in bands)
        if needed > band_area:
            band_area -= 1  # reserve the `+NN more` marker row
        hidden = 0
        painted = 0
        for kind, idxs in bands:
            block = 1 + len(idxs)
            if painted >= band_area:
                hidden += block
                continue
            worst = min((gaps[i].severity for i in idxs), key=SEVERITIES.index)
            rows.append(_band_head(kind, len(idxs), worst, w, kind_w))
            painted += 1
            take = len(idxs)
            if painted + take > band_area:
                take = band_area - painted
            for gi in idxs[:take]:
                rows.append(_gap_row(gaps[gi], gi, w, geo, kind_w, rank_w,
                                     cursor=False))
            painted += take
            hidden += len(idxs) - take
        if hidden:
            rows.append(base.label(f"+{hidden:02d} more", w, D.MUT))
        rows.append(base.label(_HINT, w, D.MUT))
        while len(rows) < budget:
            rows.insert(len(rows) - 1, base.label("", w))
        return rows

    def _empty_frame(self, w, budget) -> list[Text]:
        rows = [_header(w), _tally((), 0), base.label(_EMPTY, w, D.MUT)]
        while len(rows) < budget:
            rows.append(base.label("", w))
        return rows

    def _not_computed(self, state) -> int:
        """The count of gaps whose reach the ranking could not compute — the
        second member of the same deterministic ranking call the host made
        (reach is memoized on the map), re-issued here because the frozen
        surface carries only the ranked tuple.  The painted rows always come
        from `state.gaps` in its exact order; this never re-sorts them."""
        if state.relmap is None or not state.gaps:
            return 0
        return rank_gaps(state.relmap, list(state.gaps), None)[1]


def build_view() -> GapsView:
    """The wiring convention (`base.build_view`)."""
    return GapsView()
