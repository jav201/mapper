"""The SINGLE owner of "what matches" — and of the order matches come back in.

Before this increment there were two live definitions of a hit and they
disagreed.  `Graph.search_hits` joined six haystacks (id, title, `meta`, notes,
field values, each attachment's caption-or-path); the layered renderer carried
its own inline predicate over three (title, notes, field values).  Executed on
one graph with one query, the two returned `['riesgo-root','b','c','d','e']` and
`['b','d']` — so a count taken from one and a highlight painted from the other
disagree ON SCREEN, which is the defect US-N07 exists to close.  The renderers
now receive a resolved `frozenset[str]` and evaluate no predicate at all.

WHY THE DELEGATION IS NOT A POINTLESS WRAPPER.  `Graph.search_hits` answers
"which nodes contain this text" and is the right home for that.  It is NOT the
right home for the two things this module adds, both of which are about the
QUERY rather than about the graph:

  * a blank query is not a match-everything.  `search_hits("")` returns every
    node, because `if q in hay` makes the empty string a substring of every
    haystack -- executed, all 6 of a 6-node graph, and `"   "` returns 4 (only
    the nodes whose joined haystack happens to contain a space).  A blank query
    lighting the whole map is the SHIPPED behaviour, and `LLR-N07.3.3` is what
    stops the count line inheriting it;
  * hits come back in TREE order, not in dict-insertion order.  They differ:
    executed on the Inc-4 fixture, `['riesgo-root','b','d','e','c']` against
    `['riesgo-root','b','c','d','e']`.

THIS MODULE IMPORTS NO TEXTUAL AND NO `views`.  It is consumed by `app.py`,
which puts the resolved set on `ViewState`; the `views -> search` edge is
deliberately never created, because `frozenset[str]` is a builtin and carries no
dependency with it.
"""
from __future__ import annotations

from .model import Graph


def tree_order(graph: Graph) -> list[str]:
    """Every node id, pre-order from the root, children in DECLARED order.

    Reproduces the walk shape of `MapScreen._incomplete_order` — a stack seeded
    with the root, pushing `reversed(children_of(nid))` — so "next match" and
    "next missing field" mean the same kind of "next" to the operator.  The
    shape is reproduced rather than shared: `_incomplete_order` filters as it
    walks and lives on a Textual screen, and importing a screen into the search
    owner would put the app's event loop inside a headless module.

    Ids not reachable from the root are NOT dropped -- see `SearchIndex.query`.

    THE CHILD INDEX IS BUILT ONCE, AND THAT IS NOT A MICRO-OPTIMISATION.
    `Graph.children_of` (`model.py:149`) is a full linear scan of `graph.edges`,
    so asking it once per node makes this walk `O(N*E)` -- measured at the
    renderer's declared ceiling, 4.19 s for ONE call, against 0.008 s for the
    matching it orders and 0.14 s for the entire frame.  This runs in the
    repaint path, several times per frame, so the quadratic is an operator-
    visible freeze rather than a number in a profile.  One `O(E)` pass up front
    buys the same answer: the outputs were compared case by case over the real
    fixtures, a cyclic/forest/dangling-edge graph and synthetic trees to 3000
    nodes -- 96 cases, 0 mismatches.
    """
    out: list[str] = []
    if graph.root_id is None:
        return out
    kids: dict[str, list[str]] = {}
    for edge in graph.edges:
        kids.setdefault(edge.parent_id, []).append(edge.child_id)
    seen: set[str] = set()
    stack = [graph.root_id]
    while stack:
        nid = stack.pop()
        if nid in seen or nid not in graph.nodes:
            continue
        seen.add(nid)
        out.append(nid)
        for cid in reversed(kids.get(nid, ())):
            if cid not in seen:
                stack.append(cid)
    return out


class SearchIndex:
    """Simple in-memory search over the current graph."""

    def __init__(self, graph: Graph):
        self.graph = graph

    def hits(self, q: str) -> frozenset[str]:
        """The matching ids as a SET — the shape a renderer receives.

        A query with no non-whitespace character matches NOTHING (`LLR-N07.3.3`).
        """
        if not q.strip():
            return frozenset()
        return frozenset(self.graph.search_hits(q))

    def query(self, q: str) -> list[str]:
        """The matching ids in tree order.

        A node the root cannot reach still counts as a match -- a `.mmd` may
        declare a second disconnected component, and a hit silently missing from
        this list would make the count under-report the graph it was promised to
        cover.  Such ids come last, in the graph's own order, so
        `len(query(q)) == len(hits(q))` holds for every graph and the count line
        may be taken from either.

        THE EMPTY-HIT RETURN IS THE DEFAULT STATE OF THE SCREEN, NOT AN EDGE
        CASE.  `hits` correctly answers `frozenset()` for a blank query in ~4
        microseconds (`LLR-N07.3.3`), but the walk below used to run anyway
        against an empty `found` -- so an operator who has NEVER SEARCHED paid
        the full ordering cost on every repaint: measured 3.26 s per call at
        12000 nodes for a query of `"   "`.  The guard was right about the
        RESULT and silent about the WORK.  It also short-circuits a query that
        simply matches nothing, where the ordering has nothing to order.
        """
        found = self.hits(q)
        if not found:
            return []
        walked = [nid for nid in tree_order(self.graph) if nid in found]
        # Hoisted: inside the comprehension this set was rebuilt once PER
        # CANDIDATE, an O(N^2) on its own and independent of the walk's.
        seen = set(walked)
        return walked + [nid for nid in self.graph.nodes
                         if nid in found and nid not in seen]
