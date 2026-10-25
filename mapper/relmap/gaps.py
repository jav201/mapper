"""Gap detection and ranking over a `RelMap`, generic over the profile's gap catalogue.

`detect_gaps` reads `map.profile.gaps` and names no node kind, edge type or gap kind
(LLR-RMP.1.2, LLR-RMG.1.1); the four patterns are the closed set of `profile.PATTERNS`.
A row fires only when every kind in its `needs` is in `map.sourced` (an unsourced kind
yields no gap -- an honest partial map).  A node is eligible for an "eligible" row only
when its status is exactly `active`; every other node still counts for `up`, `down` and
`reach`.  Detection order is catalogue order, then node (or edge) input order.

`detect_gaps` returns `reach = 0` on every gap: reach is computed by `rank_gaps`, only for
the severity bands needed to fill `limit` lines, and ONLY through `RelMap.reach`, so every
traversal is drawn on the map's one shared visit budget (security C1).  This module never
reads adjacency itself.

For an edge-evidence row the gap sits on the edge's `dst`: a change at `dst` is what the
missing evidence leaves unchecked.  Sentence slots are filled in one pass, so a title that
contains a slot name is never re-expanded.  A slot the row's pattern does not supply (for
example `<src>` in a `lacks_*` sentence) is left in the sentence as written.

The row flags `eligible` and `open`, and the `unparsed` qualifier, apply to `lacks_in` and
`lacks_out` rows only; `cycle` and `edge_unevidenced` rows ignore them.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, replace

from mapper.relmap.model import RelMap
from mapper.relmap.profile import SEVERITIES, GapRow

ACTIVE = "active"
QUALIFIER = " (canon rows near this id could not be parsed or linked: {n})"
_SLOT = re.compile(r"<(id|title|n|src|dst)>")


@dataclass(frozen=True)
class Gap:
    severity: str
    kind: str
    node: str
    sentence: str
    reach: int


def _fill(template: str, **values: str) -> str:
    return _SLOT.sub(lambda m: values.get(m.group(1), m.group(0)), template)


def _qualified(sentence: str, unparsed: int) -> str:
    return sentence + QUALIFIER.format(n=unparsed) if unparsed > 0 else sentence


def _cycles(m: RelMap, row: GapRow) -> list[Gap]:
    return [
        Gap(row.severity, row.kind, comp[0], _fill(row.sentence, id=comp[0], n=str(len(comp))), 0)
        for comp in m.cycles
    ]


def _lacks(m: RelMap, row: GapRow, incoming: bool) -> list[Gap]:
    linked: set[str] = set()
    for e in m.edges:
        if e.type != row.edge:
            continue
        end, other = (e.dst, e.src) if incoming else (e.src, e.dst)
        if row.peer is not None and m.node(other).kind != row.peer:
            continue
        linked.add(end)
    found = []
    for n in m.nodes:
        if n.kind != row.node_kind or n.id in linked:
            continue
        if row.eligible and n.status != ACTIVE:
            continue
        if row.open and not n.open:
            continue
        sentence = _fill(row.sentence, id=n.id, title=n.title)
        found.append(Gap(row.severity, row.kind, n.id, _qualified(sentence, n.unparsed), 0))
    return found


def _unevidenced(m: RelMap, row: GapRow) -> list[Gap]:
    return [
        Gap(row.severity, row.kind, e.dst, _fill(row.sentence, src=e.src, dst=e.dst), 0)
        for e in m.edges
        if e.type == row.edge and e.evidence_missing
    ]


def detect_gaps(m: RelMap) -> list[Gap]:
    """Every gap of every catalogue row whose kinds are sourced, in detection order, reach 0."""
    found: list[Gap] = []
    for row in m.profile.gaps:
        if not all(kind in m.sourced for kind in row.needs):
            continue
        if row.pattern == "cycle":
            found += _cycles(m, row)
        elif row.pattern == "lacks_in":
            found += _lacks(m, row, incoming=True)
        elif row.pattern == "lacks_out":
            found += _lacks(m, row, incoming=False)
        else:
            found += _unevidenced(m, row)
    return found


def rank_gaps(m: RelMap, gaps: list[Gap], limit: int | None) -> tuple[list[Gap], int]:
    """Rank `gaps`; return `(ranked, reach_not_computed)`.

    Order is severity, then reach descending, detection order on ties.  `reach_not_computed`
    counts the gaps whose reach was not computed.

    Reach is looked up (`RelMap.reach`) only for the severity bands needed to fill `limit`
    lines -- every band when `limit` is `None`.  A gap whose reach comes back `None` (the
    shared budget is spent) ranks with reach 0 and is counted.  All gaps are returned; a
    caller that prints `limit` of them reads the first `limit`.
    """
    band = {sev: i for i, sev in enumerate(SEVERITIES)}
    size = {sev: 0 for sev in SEVERITIES}
    for g in gaps:
        size[g.severity] += 1
    needed: set[str] = set()
    before = 0
    for sev in SEVERITIES:
        if limit is None or before < limit:
            needed.add(sev)
        before += size[sev]
    not_computed = 0
    scored: list[Gap] = []
    for g in gaps:
        if g.severity in needed:
            r = m.reach(g.node)
            if r is None:
                not_computed += 1
                r = 0
            g = replace(g, reach=r)
        scored.append(g)
    return sorted(scored, key=lambda g: (band[g.severity], -g.reach)), not_computed
