"""The relation-map read model: a typed, multi-parent directed graph built under a `Profile`.

A KIND beside the tree `Graph`, never a mutation of it (R-016): this module imports nothing
from the tree kind.  It names no node kind, edge type or gap kind -- every such name comes
from the `Profile` handed to `build_map` (LLR-RMP.1.2).

`build_map` returns an immutable `RelMap`.  An invalid element is reported as a `Problem`
and excluded, never raised; only a map over the node or edge cap is refused
(`RelMapLimitError`).  A cycle is REPORTED (`RelMap.cycles`, `Edge.in_cycle`) and the map
still loads -- the opposite policy to the tree kind, each right for its kind.

VISIT BUDGET (security C1).  One budget of `VISIT_BUDGET` node expansions per `RelMap`
object, for its whole lifetime, is drawn on by every `reach` traversal -- including the ones
`gaps.rank_gaps` makes.  `reach` counts each node expansion and reads adjacency through
`down` (the one adjacency read the tests wrap); a ranking must go through `reach`, never
traverse `down` itself.  A traversal that would pass the budget is abandoned, nothing is
memoised for it, and `reach` returns `None` ("not computed"), never a hang and never a partial count.
`visits` reports how much of the budget is spent.  `neighbourhood` is NOT on the budget (it
is O(V+E) per call): a view calls it for the focused node only.

Every traversal is iterative (explicit stack or queue); a 100,000-node chain must not
recurse.
"""
from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass, replace

from mapper.osopen import MAX_EDGES, MAX_NODES
from mapper.relmap.profile import Profile

VISIT_BUDGET = 2_000_000
ID_MAX = 200


class RelMapLimitError(Exception):
    """The input is over the node or edge cap; the message names the limit."""


@dataclass(frozen=True)
class Node:
    id: str
    kind: str
    title: str = ""
    status: str = "active"
    open: bool = False
    unparsed: int = 0


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    type: str
    evidence_missing: bool = False  # graduated: evidence -> False, tagged without evidence -> True
    in_cycle: bool = False  # set by the builder only


@dataclass(frozen=True)
class Problem:
    kind: str
    subject: str


def _unsafe(node_id: str) -> bool:
    return node_id == "" or len(node_id) > ID_MAX or not node_id.isprintable()


def _cycles(
    order: list[str], succ: dict[str, list[str]]
) -> tuple[tuple[tuple[str, ...], ...], dict[str, int]]:
    """Strongly connected components of size > 1, plus single nodes with a self-loop (Tarjan, iterative).

    Members are in node input order, components in the input order of their first member.
    Returns the components and a node -> component number map.
    """
    position = {nid: i for i, nid in enumerate(order)}
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    found: list[list[str]] = []
    for start in order:
        if start in index:
            continue
        index[start] = low[start] = len(index)
        stack.append(start)
        on_stack.add(start)
        work = [(start, 0)]
        while work:
            v, i = work[-1]
            targets = succ.get(v, ())
            if i < len(targets):
                work[-1] = (v, i + 1)
                w = targets[i]
                if w not in index:
                    index[w] = low[w] = len(index)
                    stack.append(w)
                    on_stack.add(w)
                    work.append((w, 0))
                elif w in on_stack:
                    low[v] = min(low[v], index[w])
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[v])
            if low[v] == index[v]:
                comp = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    comp.append(w)
                    if w == v:
                        break
                if len(comp) > 1 or v in succ.get(v, ()):
                    found.append(sorted(comp, key=position.__getitem__))
    found.sort(key=lambda comp: position[comp[0]])
    comp_of = {nid: n for n, comp in enumerate(found) for nid in comp}
    return tuple(tuple(c) for c in found), comp_of


class RelMap:
    """An immutable relation map; built only by `build_map`.

    `nodes` and `edges` are tuples in input order; `problems` the elements that were
    excluded; `cycles` the components found by `_cycles`; `sourced` the node kinds the
    producer actually read (a kind not sourced yields no node and no gap).
    """

    __slots__ = (
        "_profile", "_nodes", "_edges", "_problems", "_cycles", "_sourced",
        "_by_id", "_up", "_down", "_visits", "_reach_memo",
    )

    def __init__(
        self,
        profile: Profile,
        nodes: tuple[Node, ...],
        edges: tuple[Edge, ...],
        problems: tuple[Problem, ...],
        cycles: tuple[tuple[str, ...], ...],
        sourced: frozenset[str],
        up: dict[str, tuple[str, ...]],
        down: dict[str, tuple[str, ...]],
    ) -> None:
        self._profile = profile
        self._nodes = nodes
        self._edges = edges
        self._problems = problems
        self._cycles = cycles
        self._sourced = sourced
        self._by_id = {n.id: n for n in nodes}
        self._up = up
        self._down = down
        self._visits = 0
        self._reach_memo: dict[str, int] = {}

    @property
    def profile(self) -> Profile:
        return self._profile

    @property
    def nodes(self) -> tuple[Node, ...]:
        return self._nodes

    @property
    def edges(self) -> tuple[Edge, ...]:
        return self._edges

    @property
    def problems(self) -> tuple[Problem, ...]:
        return self._problems

    @property
    def cycles(self) -> tuple[tuple[str, ...], ...]:
        return self._cycles

    @property
    def sourced(self) -> frozenset[str]:
        return self._sourced

    @property
    def visits(self) -> int:
        """Node expansions drawn so far on the shared `VISIT_BUDGET`."""
        return self._visits

    def node(self, node_id: str) -> Node | None:
        return self._by_id.get(node_id)

    def up(self, node_id: str) -> tuple[str, ...]:
        """Ids a change at `node_id` comes from, in edge input order; empty for an unknown id."""
        return self._up.get(node_id, ())

    def down(self, node_id: str) -> tuple[str, ...]:
        """Ids a change at `node_id` reaches directly, in edge input order; empty for an unknown id."""
        return self._down.get(node_id, ())

    def reach(self, node_id: str) -> int | None:
        """Distinct nodes reachable through `down`, excluding `node_id`; `None` once the shared budget is spent."""
        if node_id not in self._by_id:
            return 0
        memo = self._reach_memo
        if node_id in memo:
            return memo[node_id]
        seen = {node_id}
        queue = deque([node_id])
        while queue:
            if self._visits >= VISIT_BUDGET:
                return None
            current = queue.popleft()
            self._visits += 1
            for nxt in self.down(current):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        memo[node_id] = len(seen) - 1
        return memo[node_id]

    def neighbourhood(self, node_id: str, hops: int) -> frozenset[str]:
        """`node_id` and every node within `hops` steps through `up` or `down`; empty for an unknown id."""
        if node_id not in self._by_id:
            return frozenset()
        seen = {node_id}
        frontier = [node_id]
        for _ in range(max(hops, 0)):
            fresh = []
            for x in frontier:
                for y in (*self._up.get(x, ()), *self._down.get(x, ())):
                    if y not in seen:
                        seen.add(y)
                        fresh.append(y)
            if not fresh:
                break
            frontier = fresh
        return frozenset(seen)


def build_map(
    profile: Profile,
    nodes: Iterable[Node],
    edges: Iterable[Edge],
    *,
    sourced: Iterable[str],
) -> RelMap:
    """Validate `nodes` and `edges` under `profile` and return the map of the valid remainder."""
    nodes = tuple(nodes)
    edges = tuple(edges)
    if len(nodes) > MAX_NODES:
        raise RelMapLimitError(f"more than {MAX_NODES} nodes")
    if len(edges) > MAX_EDGES:
        raise RelMapLimitError(f"more than {MAX_EDGES} edges")

    kinds = frozenset(profile.node_kinds)
    types = {t.name: t for t in profile.edge_types}
    problems: list[Problem] = []

    kept_nodes: list[Node] = []
    accepted: dict[str, str] = {}
    for n in nodes:
        if _unsafe(n.id):
            problems.append(Problem("unsafe id", n.id))
        elif n.id in accepted:
            problems.append(Problem("duplicate id", n.id))
        elif n.kind not in kinds:
            problems.append(Problem("unknown node kind", n.id))
        else:
            accepted[n.id] = n.kind
            kept_nodes.append(n)

    valid: list[Edge] = []
    for e in edges:
        subject = f"{e.src}->{e.dst}"
        etype = types.get(e.type)
        if etype is None:
            problems.append(Problem("unknown edge type", subject))
        elif e.src not in accepted or e.dst not in accepted:
            problems.append(Problem("unknown endpoint", subject))
        elif (accepted[e.src], accepted[e.dst]) not in etype.pairs:
            problems.append(Problem("disallowed pair", subject))
        else:
            valid.append(e)

    succ: dict[str, list[str]] = {}
    for e in valid:
        succ.setdefault(e.src, []).append(e.dst)
    cycles, comp_of = _cycles([n.id for n in kept_nodes], succ)

    final: list[Edge] = []
    up: dict[str, list[str]] = {}
    down: dict[str, list[str]] = {}
    for e in valid:
        in_cycle = e.src in comp_of and comp_of.get(e.dst) == comp_of[e.src]
        final.append(replace(e, in_cycle=in_cycle))
        if types[e.type].downstream:
            origin, target = e.src, e.dst
        else:
            origin, target = e.dst, e.src
        down.setdefault(origin, []).append(target)
        up.setdefault(target, []).append(origin)

    return RelMap(
        profile,
        tuple(kept_nodes),
        tuple(final),
        tuple(problems),
        cycles,
        frozenset(sourced),
        {k: tuple(v) for k, v in up.items()},
        {k: tuple(v) for k, v in down.items()},
    )
