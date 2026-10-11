"""Inc-M2 (perf batch, Lane M) — LLR-PERF.2.2: `mermaid.dump` emits parentless
nodes in one linear LOCAL incident pass.

`dump` (`mapper/mermaid.py`) used to test orphan membership per node with
`any(e.parent_id == node.id or e.child_id == node.id for e in graph.edges)` —
an O(N·E) rescan (18,003,000 edge visits on wide-6000, PERF0C §7.3).  The fix
builds the incident-id set in ONE local pass over every edge — local to the
dump call, NOT the Lane M adjacency cache (ruling R11: a counting wrapper that
swapped `edges` would send a cache variant cold and cost 3E) — including
DANGLING edges (an edge whose endpoint is missing from `nodes` is skipped when
written but its ids still count), then emits the edgeless nodes in the same
node-dict order, with the same `emitted` dedup and escaping.  The emitted
`.mmd` text stays byte-identical (the dump goldens pinned at base SHA
`5cde04e`).

Counting instrument (both arms): the test swaps `graph.edges` for a
`_CountingEdges(list)` subclass that counts every yielded edge — one yield per
visited edge, so one full pass contributes exactly E.  Per dump call the bound
is <= 2*E + C and the wide-tree scaling ratio count(2N)/count(N) must stay in
[1.8, 2.2] (linear — the M-M2a mutant's per-node `any()` scan quadruples it).

RED transcripts: `.dev-flow/2026-10-10-perf-batch/evidence/m2-red.transcript`.
"""
from __future__ import annotations

import mapper.mermaid as mermaid
from mapper.app import MapperApp
from mapper.mermaid import dump, parse
from mapper.model import Edge, Ficha, Graph, Node
from mapper.screens.prompt import _PromptScreen

from tests.perf_goldens_capture import (
    FIXTURES,
    GOLDEN_DIR,
    build_dangling,
    build_forest,
    build_single,
    build_wide,
)
from tests.test_draft_save import _open, _press

#: The small additive constant of the per-dump bound `<= 2*E + c`.
_DUMP_C = 4


class _CountingEdges(list):
    """A list counting every edge yielded to a consumer (one yield == 1 visit)."""

    visits: int

    def __iter__(self):
        for edge in super().__iter__():
            self.visits += 1
            yield edge


# --- TC-M5: counted ops + scaling ratio (LLR-PERF.2.2) ------------------------


def test_dump_counted_ops_scaling_ratio():
    """ONE `dump` call iterates `graph.edges` <= 2*E + c; doubling N doubles.

    Wide trees have no orphans, so both the write pass and the incident pass
    run the full list: exactly 2E visits, ratio 2.000.  The pre-change
    per-node `any()` scan cost ~N*E visits and quadruples the ratio (M-M2a).
    """
    n = 1500
    counts: dict[int, int] = {}
    for size in (n, 2 * n):
        graph = build_wide(size)
        graph.edges = _CountingEdges(graph.edges)
        graph.edges.visits = 0
        dump(graph)
        counts[size] = graph.edges.visits
        e = size - 1  # build_wide: one root plus size-1 children
        assert counts[size] > 0, "the counting wrapper observed no edge visits"
        assert counts[size] <= 2 * e + _DUMP_C, (
            f"dump iterated graph.edges {counts[size]} times on wide-{size} "
            f"(E={e}) — the per-node rescan is back (bound is 2*E + {_DUMP_C})"
        )
    ratio = counts[2 * n] / counts[n]
    assert 1.8 <= ratio <= 2.2, (
        f"dump edge-iteration scaling ratio {ratio:.3f} on wide trees is not "
        "linear (the O(N*E) orphan scan quadruples it)"
    )


# --- TC-M6: fixture byte goldens (LLR-PERF.2.2 behaviour oracle) --------------


def test_dump_fixture_goldens():
    """`dump` bytes byte-equal every golden pinned at base SHA `5cde04e`.

    Covers the three committed fixtures (round-tripped through `parse`),
    wide-6000, forest, empty, single-node, and the DANGLING-EDGE graph —
    plus two inline arms pinning today's base behaviour where the committed
    goldens are structurally invariant to a wrong fix:

    * ``orphan-order`` — two orphan nodes, emitted in NODE-DICT order: the
      committed fixtures are all connected trees (zero orphans) and ``single``
      has exactly one, so no pinned golden can see the orphan loop's order
      (M-M2b's reordering reddens THIS arm).
    * ``dangling-solo`` — a node whose ONLY incident edge is dangling (its
      other endpoint is missing from ``nodes``): it must NOT be re-emitted as
      an orphan, i.e. the dangling edge's ids still count toward membership.
      The pinned ``dangling.mmd`` is invariant to this by construction — a
      missing endpoint is never a node, so dropping its membership flips no
      node's emission there (dropping dangling-edge counting reddens THIS
      arm).

    M-M2b's dedup/escaping drift reddens the pinned arms.
    """
    cases: list[tuple[str, str, bytes]] = []
    for name in ("legacy", "anidado", "truncado"):
        src = (FIXTURES / f"{name}.mmd").read_text(encoding="utf-8")
        cases.append(
            (name, dump(parse(src)), (GOLDEN_DIR / "dump" / f"{name}.mmd").read_bytes())
        )
    for name, text in (
        ("wide6000", dump(build_wide(6000))),
        ("forest", dump(build_forest())),
        ("empty", dump(Graph())),
        ("single", dump(build_single())),
        ("dangling", dump(build_dangling())),
    ):
        cases.append(
            (name, text, (GOLDEN_DIR / "dump" / f"{name}.mmd").read_bytes())
        )

    ordered = Graph()
    ordered.add_node(Node(id="zeta"))
    ordered.add_node(Node(id="alfa"))
    ordered.add_node(Node(id="root", ficha=Ficha(title="raiz")))
    ordered.add_node(Node(id="kid"))
    ordered.add_edge(Edge(parent_id="root", child_id="kid"))
    cases.append(
        ("orphan-order", dump(ordered), b"graph TD\n    root[raiz] --> kid\n    zeta\n    alfa\n")
    )

    solo = Graph()
    solo.add_node(Node(id="solo"))
    solo.add_edge(Edge(parent_id="solo", child_id="fantasma"))
    cases.append(("dangling-solo", dump(solo), b"graph TD\n"))

    failures: list[str] = []
    for name, text, expected in cases:
        if text.encode("utf-8") != expected:
            failures.append(
                f"{name}: dump bytes drifted (base 5cde04e behaviour golden)"
            )
    assert not failures, "\n".join(failures)


# --- AT-076: real persisting add_child gesture through the real app -----------


async def test_at_076_real_save_dump_budget(tmp_path, monkeypatch):
    """Open a SAVED wide-6000 map, add a child with real keys (`a`, a typed
    title, `enter` — `editing.py` add_child persisting via `_save_or_toast`),
    and bound the ONE `mermaid.dump` call the save performs to <= 2*E + c edge
    iterations — while the saved `.mmd` bytes byte-equal the AT-076 golden
    (pinned at base SHA `5cde04e`, on the map AFTER the add_child edit).

    The counting wrapper wraps `mapper.mermaid.dump` ITSELF (the store imports
    it at call time, `store.py:861`); the live graph's `edges` are swapped for
    a counting list AFTER the map is open, and the wrapper reads the visit
    delta across the dump call only.  M-M2a (restore the per-node `any()`
    scan) reddens this node on the iteration bound.
    """
    app = MapperApp(tmp_path)
    stats: dict[str, int | None] = {"calls": 0, "visits": None, "e_final": 0}
    real_dump = mermaid.dump

    def counting_dump(graph):
        edges = graph.edges
        start = getattr(edges, "visits", None)
        stats["calls"] += 1
        text = real_dump(graph)
        if start is not None:
            stats["visits"] = edges.visits - start
        return text

    monkeypatch.setattr(mermaid, "dump", counting_dump)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("perf6000", build_wide(6000))
        screen = await _open(app, pilot, "perf6000", cursor="root")
        # Install the counting edges list on the LIVE graph; app-side
        # invalidations outside the dump call do not affect the wrapper's
        # per-call delta.
        screen.graph.edges = _CountingEdges(screen.graph.edges)
        screen.graph.edges.visits = 0
        await _press(pilot, "a")
        assert isinstance(app.screen, _PromptScreen), type(app.screen).__name__
        await pilot.press(*"hijoperf")
        await pilot.press("enter")
        await pilot.pause()
        stats["e_final"] = len(screen.graph.edges)
        saved = (tmp_path / "perf6000.mmd").read_bytes()

    # The gesture performed exactly one more dump (the initial seed save plus
    # the persisting add_child save) and it was the counted one.
    assert stats["calls"] == 2, (
        f"expected the seed save plus ONE gesture dump, got {stats['calls']}"
    )
    assert stats["visits"] is not None, (
        "the gesture's dump did not observe the counting edges list"
    )
    e_final = stats["e_final"]  # 5999 + the new child == 6000
    assert stats["visits"] <= 2 * e_final + _DUMP_C, (
        f"the save's dump iterated graph.edges {stats['visits']} times "
        f"(E={e_final}) — the per-node rescan is back (bound 2*E + {_DUMP_C})"
    )
    golden = (GOLDEN_DIR / "at076_saved_wide6000_after_add_child.mmd").read_bytes()
    assert saved == golden, (
        "the saved .mmd after add_child drifted from the AT-076 golden "
        "(base 5cde04e)"
    )
