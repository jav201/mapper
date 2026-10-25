"""L2a prescan cost measurement — batch 2026-10-23-hygiene-batch, lane L2a.

The PLAN.md watch-item: "Prescan adds one pass over the sidecar — load-time delta on
the largest perf sidecar (1,369,835 B / 12,000 nodes) measured at the L2a gate".

The tracked perf-evidence workspaces (`perf0b-ws-*`) are NOT in this worktree, so the
equivalent sidecar is generated here: `build_wide(12000)` (12,000 nodes / 11,999
edges — the same shape and counts as the recorded `perf0b-ws-*` sidecars, ledger .5)
saved through MapStore into a temporary workspace.

Measured, per repetition:
  (a) full `MapStore.load` — reader + prescan + safe_load + build + reindex;
  (b) the prescan alone over the sidecar text (`_prescan_sidecar`);
  (c) the load-time delta attributable to the prescan pass, as (b) against (a).
"""
import statistics
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from tests.perf_goldens_capture import build_wide  # noqa: E402
from mapper.store import MapStore  # noqa: E402

REPS = 5

with tempfile.TemporaryDirectory() as tmp:
    ws = Path(tmp) / "ws"
    ws.mkdir()
    store = MapStore(ws)
    store.save("p", build_wide(12000))
    sidecar_path = ws / "p_nodos.yml"
    sidecar_bytes = sidecar_path.stat().st_size
    yml_text = sidecar_path.read_text(encoding="utf-8")

    loads, pres = [], []
    for _ in range(REPS):
        started = time.perf_counter()
        store.load("p")
        loads.append(time.perf_counter() - started)
        started = time.perf_counter()
        store._prescan_sidecar("p", yml_text)
        pres.append(time.perf_counter() - started)

load_med = statistics.median(loads)
pre_med = statistics.median(pres)
print(f"fixture: build_wide(12000) saved via MapStore — sidecar {sidecar_bytes} bytes, "
      "12,000 nodes / 11,999 edges (equivalent of perf0b-ws-*, ledger .5)")
print(f"repetitions: {REPS}")
for i, (load, pre) in enumerate(zip(loads, pres)):
    print(f"  rep {i + 1}: load {load * 1000:.1f} ms   prescan {pre * 1000:.1f} ms")
print(f"median full load:        {load_med * 1000:.1f} ms")
print(f"median prescan pass:     {pre_med * 1000:.1f} ms")
print(f"prescan share of load:   {pre_med / load_med * 100:.2f} %")
print(f"load-time delta (watch-item, not a gate): +{pre_med * 1000:.1f} ms per load")
