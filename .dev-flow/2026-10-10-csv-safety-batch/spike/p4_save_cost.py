"""P4 measurement owed by C2/R12 (LED-2026-10-10-csv-safety-batch.6).

Measured once at P4: the added cost of MapStore.save's round-trip check
(LLR-CSV.1.1) as a share of save wall time for a 6 000-node wide tree,
in a tmp workspace. Median of 3 runs per leg. The "check skipped" leg
monkeypatches MapStore._check_round_trip to a no-op INSIDE this script
only — no product file is touched. Threshold: added share <= 25 %.
"""

import statistics
import tempfile
import time
from pathlib import Path

from mapper.model import Edge, Ficha, Graph, Node
from mapper.store import MapStore

N = 6000
REPS = 3


def wide_tree() -> Graph:
    """One root with N-1 children: the wide shape dump's parentless-node
    loop makes O(N*E) (mapper/mermaid.py:152-153, ruling R12)."""
    nodes = {
        f"n{i:05d}": Node(id=f"n{i:05d}", ficha=Ficha(title=f"node {i}"))
        for i in range(N)
    }
    edges = [Edge(parent_id="n00000", child_id=f"n{i:05d}") for i in range(1, N)]
    return Graph(nodes=nodes, edges=edges, root_id="n00000")


def bench(skip_check: bool) -> float:
    orig = MapStore._check_round_trip
    if skip_check:
        MapStore._check_round_trip = lambda self, graph, mmd_text: None
    try:
        with tempfile.TemporaryDirectory() as tmp:
            store = MapStore(Path(tmp))
            graph = wide_tree()
            times = []
            for rep in range(REPS):
                t0 = time.perf_counter()
                store.save("perf", graph)
                times.append(time.perf_counter() - t0)
                print(f"  rep {rep + 1}: {times[-1]:.3f}s")
            return statistics.median(times)
    finally:
        MapStore._check_round_trip = orig


def main() -> None:
    print(f"P4 save-cost measurement — {N}-node wide tree, median of {REPS}")
    print("leg 1: MapStore.save with the round-trip check (LLR-CSV.1.1)")
    with_check = bench(skip_check=False)
    print(f"  median: {with_check:.3f}s")
    print("leg 2: same save, _check_round_trip monkeypatched to a no-op "
          "(inside this script only)")
    without_check = bench(skip_check=True)
    print(f"  median: {without_check:.3f}s")
    added = with_check - without_check
    share = added / with_check * 100.0
    print(f"added cost of the round-trip check: {added:.3f}s "
          f"= {share:.1f}% of save wall time")
    print(f"threshold <= 25%: {'PASS' if share <= 25.0 else 'FAIL'}")


if __name__ == "__main__":
    main()
