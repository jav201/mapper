"""PERF0 measurement harness for batch `2026-10-10-perf-batch` (measurement spike).

Headless, deterministic, stdlib-only measurement (time.perf_counter, cProfile,
pstats, statistics).  Runs the three shipped renderers' PUBLIC API
(`Renderer().render(graph, ViewState(...))`) over reproducible graph shapes.

Nothing under `mapper/` or `tests/` is touched or monkey-patched.  Every
potentially-slow case runs in a subprocess with a hard timeout; a case that
exceeds it is recorded as TIMEOUT, never a hang.

Subcommands (each prints machine-readable lines; `RESULT {...}` is JSON):

    render    --shape NAME --renderer {layered,outline,radial} [--reps N]
              [--early-stop SEC] [--w 118 --h 34]
              One subprocess == one case; up to --reps renders, median reported.
              Early-stop: further reps are skipped once a rep exceeds
              --early-stop seconds (slow cases keep a single clean sample).
    index-time --shape NAME
              Time of the adjacency/parent index the renderers build per pass.
    profile   --shape NAME --renderer NAME
              cProfile of one full render; top 15 by cumulative and by tottime,
              plus the call counts of Graph.children_of / Graph.parent_of.
    mount     --shape NAME [--size 118x34] [--reps N]
              MapScreen mount -> first paint inside App.run_test (median of N).
    sweep
              Orchestrates the full matrix from THIS process, spawning `render`
              workers per case.  Sequential timed phase for the cheap cases,
              concurrent classification phase (bounded pool, timing discarded)
              for the cases the 73-node / 72.5 s precedent says are exponential;
              any case that finishes cheaply there is re-run sequentially.

Shapes:
    p51      5 layers x 10 per layer, fully connected across boundaries
             (tests/test_repair_perf_shape.py's fixture, 51 nodes / 410 edges)
    p73      6 layers x 12 per layer, fully connected (73 nodes / 732 edges) --
             the S-15 demonstration shape from
             .dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md ~L4271
    sweep    layered DAGs, N ~ {50,100,200,400} = LAYERS x PER_LAYER + 1, at
             k in {1: sparse E~=N, 4: moderate E~=4N, PER_LAYER: dense PER_LAYER^2
             per boundary}; node j in a layer links to children j..j+k-1 (mod P)
    chain    one chain of 1000 nodes (E = 999)

Reproduce any single number with, from the repo root:

    python .dev-flow/2026-10-10-perf-batch/spike/perf_harness.py render \
        --shape p51 --renderer layered --reps 3
"""
from __future__ import annotations

import argparse
import asyncio
import cProfile
import io
import json
import math
import os
import pstats
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SPIKE_DIR = Path(__file__).resolve().parent
BATCH_DIR = SPIKE_DIR.parent
REPO_ROOT = BATCH_DIR.parent.parent  # .dev-flow/2026-10-10-perf-batch/spike/ -> repo root
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

RUN_CAP_SECONDS = 120          # hard cap per single render run (spec)
EARLY_STOP_SECONDS = 15        # skip remaining reps once a rep exceeds this
SCRIPT_REL = ".dev-flow/2026-10-10-perf-batch/spike/perf_harness.py"

from mapper.model import Edge, Ficha, Graph, Node  # noqa: E402


# --------------------------------------------------------------------------
# Graph builders
# --------------------------------------------------------------------------

def layered_dag(layers: int, per_layer: int, k: int) -> Graph:
    """Layers x per_layer DAG + root; each node links to k children (mod P).

    k == per_layer reproduces the fully-connected fixture (PER_LAYER^2 edges
    per boundary); k == 1 gives E ~= N (P parallel chains under the root).
    """
    graph = Graph(root_id="root")
    graph.add_node(Node(id="root", ficha=Ficha(title="root")))
    previous = ["root"]
    for layer in range(layers):
        current = [f"n{layer}_{j}" for j in range(per_layer)]
        for j, nid in enumerate(current):
            graph.add_node(Node(id=nid, ficha=Ficha(title=f"node {layer}.{j}")))
        for parent in previous:
            if parent == "root":
                children = current
            else:
                j = int(parent.rsplit("_", 1)[1])
                children = [current[(j + t) % per_layer] for t in range(k)]
            for child in children:
                graph.edges.append(Edge(parent_id=parent, child_id=child))
        previous = current
    return graph


def chain(depth: int) -> Graph:
    """One chain: root -> n0 -> ... -> n{depth-2} (depth nodes, depth-1 edges)."""
    graph = Graph(root_id="root")
    graph.add_node(Node(id="root", ficha=Ficha(title="root")))
    prev = "root"
    for i in range(depth - 1):
        nid = f"n{i}"
        graph.add_node(Node(id=nid, ficha=Ficha(title=f"node {i}")))
        graph.edges.append(Edge(parent_id=prev, child_id=nid))
        prev = nid
    return graph


# (name, builder) -- N and E are derived at build time, never typed twice.
SHAPES = {
    "p51": lambda: layered_dag(5, 10, 10),
    "p73": lambda: layered_dag(6, 12, 12),
    # Loadable 51-node tree (k=1: single parent per node) -- the store's
    # parser REFUSES the multi-parent p51 DAG ("multiple parents, out of MVP
    # scope", mapper/mermaid.py:85), so this is the 51-node shape the app's
    # mount path can actually paint.
    "tree51": lambda: layered_dag(5, 10, 1),
    "chain1000": lambda: chain(1000),
}
# Sweep: N ~ {50, 100, 200, 400} at (layers, per_layer) with k in {1, 4, P}.
_SWEEP_GEOM = [(7, 7), (11, 9), (14, 14), (20, 20)]
for _L, _P in _SWEEP_GEOM:
    for _k, _dens in ((1, "sparse"), (4, "moderate"), (_P, "dense")):
        SHAPES[f"sweep-N{_L * _P + 1}_{_dens}"] = (
            lambda L=_L, P=_P, k=_k: layered_dag(L, P, k)
        )

RENDERERS = ("layered", "outline", "radial")


def build_shape(name: str) -> Graph:
    return SHAPES[name]()


def shape_stats(graph: Graph) -> dict:
    return {"nodes": len(graph.nodes), "edges": len(graph.edges)}


def make_renderer(name: str):
    if name == "layered":
        from mapper.views.layered import LayeredRenderer
        return LayeredRenderer()
    if name == "outline":
        from mapper.views.outline import OutlineRenderer
        return OutlineRenderer()
    if name == "radial":
        from mapper.views.radial import RadialRenderer
        return RadialRenderer()
    raise SystemExit(f"unknown renderer {name!r}")


def view_state(graph: Graph, w: int, h: int):
    from mapper.views.state import ViewState
    return ViewState(selected_id=graph.root_id, w=w, h=h)


# --------------------------------------------------------------------------
# Worker: render timings (+ index build time)
# --------------------------------------------------------------------------

def _time_index_build(graph: Graph) -> float:
    """Cost of the adjacency/parent indexes the renderers build per pass."""
    from mapper.views.layered import _child_index, _parent_index
    started = time.perf_counter()
    _child_index(graph)
    _parent_index(graph)
    return time.perf_counter() - started


def cmd_render(args) -> None:
    graph = build_shape(args.shape)
    renderer = make_renderer(args.renderer)
    state = view_state(graph, args.w, args.h)
    index_s = _time_index_build(graph)

    reps_done = 0
    times: list[float] = []
    status = "OK"
    for _ in range(args.reps):
        started = time.perf_counter()
        renderer.render(graph, state)
        elapsed = time.perf_counter() - started
        times.append(elapsed)
        reps_done += 1
        if elapsed > args.early_stop:
            break
    if any(t > RUN_CAP_SECONDS for t in times):
        status = "OVER-CAP"
    result = {
        "shape": args.shape, "renderer": args.renderer, "w": args.w, "h": args.h,
        **shape_stats(graph), "reps_requested": args.reps, "reps_done": reps_done,
        "times_s": times, "index_build_s": index_s, "status": status,
        "median_s": statistics.median(times) if times else None,
        "min_s": min(times) if times else None, "max_s": max(times) if times else None,
    }
    print("RESULT " + json.dumps(result))


def cmd_index_time(args) -> None:
    graph = build_shape(args.shape)
    started = time.perf_counter()
    n = 7  # a handful of samples; the op is microseconds-to-milliseconds
    for _ in range(n):
        _time_index_build(graph)
    per = (time.perf_counter() - started) / n
    print("RESULT " + json.dumps({
        "shape": args.shape, **shape_stats(graph), "index_build_s": per,
    }))


# --------------------------------------------------------------------------
# Worker: cProfile of one full render
# --------------------------------------------------------------------------

def cmd_profile(args) -> None:
    graph = build_shape(args.shape)
    renderer = make_renderer(args.renderer)
    state = view_state(graph, args.w, args.h)

    profiler = cProfile.Profile()
    profiler.enable()
    renderer.render(graph, state)
    profiler.disable()

    stats = pstats.Stats(profiler)
    out = io.StringIO()

    def model_call_counts() -> dict:
        counts = {}
        for (fname, _line, func), (cc, nc, _tt, _ct, _callers) in stats.stats.items():
            if func in ("children_of", "parent_of") and fname.endswith("model.py"):
                counts[func] = {"primitive_calls": cc, "total_calls": nc}
        return counts

    print(f"PROFILE shape={args.shape} renderer={args.renderer} "
          f"nodes={len(graph.nodes)} edges={len(graph.edges)} {args.w}x{args.h}")
    print(f"model O(E) lookups: {json.dumps(model_call_counts())}")
    for sort_key, label in (("cumulative", "TOP 15 BY CUMULATIVE"),
                            ("tottime", "TOP 15 BY TOTTIME")):
        print(f"--- {label} ---")
        stats.stream = out
        stats.sort_stats(sort_key).print_stats(15)
        print(out.getvalue())
        out = io.StringIO()
        stats = pstats.Stats(profiler)


# --------------------------------------------------------------------------
# Worker: MapScreen mount -> first paint
# --------------------------------------------------------------------------

async def _mount_once(ws_dir: Path, map_id: str, graph: Graph, width: int, height: int) -> float:
    from mapper.app import MapperApp, MapScreen
    from mapper.store import MapStore

    MapStore(str(ws_dir)).save(map_id, graph)
    app = MapperApp(str(ws_dir))
    async with app.run_test(size=(width, height)) as pilot:
        await pilot.pause()
        started = time.perf_counter()
        app.push_screen(MapScreen(map_id))

        async def wait_first_paint():
            while getattr(app.screen, "_rendered_for", None) is None:
                await pilot.pause()
            await pilot.pause()  # let the canvas.update flush into the frame

        await asyncio.wait_for(wait_first_paint(), timeout=RUN_CAP_SECONDS)
        return time.perf_counter() - started


def cmd_mount(args) -> None:
    from mapper.store import MapStore  # noqa: F401  (import sanity before timing)

    graph = build_shape(args.shape)
    width, height = args.size
    times: list[float] = []
    for _ in range(args.reps):
        ws_dir = Path(tempfile.mkdtemp(
            prefix="perf0-ws-", dir=str(BATCH_DIR / "evidence")))
        try:
            times.append(asyncio.run(_mount_once(ws_dir, "p", graph, width, height)))
        finally:
            shutil.rmtree(ws_dir, ignore_errors=True)
    print("RESULT " + json.dumps({
        "shape": args.shape, **shape_stats(graph), "size": [width, height],
        "reps": args.reps, "times_s": times,
        "median_s": statistics.median(times), "min_s": min(times), "max_s": max(times),
    }))


# --------------------------------------------------------------------------
# Orchestrator: the full matrix
# --------------------------------------------------------------------------

def _spawn_render(shape: str, renderer: str, reps: int, timeout: float) -> dict:
    """Run one render case in a subprocess; TIMEOUT instead of hanging."""
    cmd = [sys.executable, str(Path(SCRIPT_REL)), "render",
           "--shape", shape, "--renderer", renderer,
           "--reps", str(reps), "--early-stop", str(EARLY_STOP_SECONDS)]
    try:
        proc = subprocess.run(
            cmd, cwd=str(REPO_ROOT), capture_output=True, text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"shape": shape, "renderer": renderer, "timeout": True}
    for line in proc.stdout.splitlines():
        if line.startswith("RESULT "):
            result = json.loads(line[len("RESULT "):])
            result["timeout"] = False
            return result
    return {"shape": shape, "renderer": renderer, "timeout": True,
            "stderr_tail": proc.stderr[-400:]}


def _sweep_cases() -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Split the matrix into (timed-sequential, classification-concurrent).

    The concurrent set holds every sweep case whose cost the 73-node / 72.5 s
    precedent (S-15) says is exponential in the layer count: the moderate lane
    at N >= 100 and the dense lane at N >= 100.  They are run 1-rep in a
    bounded pool purely to classify TIMEOUT vs completed; anything that
    completes cheaply is re-run clean in phase B-survivor pass.
    """
    named = [s for s in SHAPES if not s.startswith("sweep-")]
    sequential: list[tuple[str, str]] = [(s, r) for s in named for r in RENDERERS]
    sequential += [(s, r) for s in sorted(SHAPES)
                   if s.startswith("sweep-")
                   and ("sparse" in s or s.endswith("N50_moderate")
                        or s.endswith("N50_dense"))
                   for r in RENDERERS]
    concurrent: list[tuple[str, str]] = [
        (s, r) for s in sorted(SHAPES) for r in RENDERERS
        if s.startswith("sweep-") and (s, r) not in sequential]
    return sequential, concurrent


def _fit_exponent(points: list[tuple[float, float]]) -> float | None:
    """Least-squares slope of log(y) on log(x); None if < 2 finite points."""
    pts = [(math.log(x), math.log(y)) for x, y in points if x > 0 and y > 0]
    if len(pts) < 2:
        return None
    n = len(pts)
    sx = sum(p[0] for p in pts)
    sy = sum(p[1] for p in pts)
    sxx = sum(p[0] ** 2 for p in pts)
    sxy = sum(p[0] * p[1] for p in pts)
    denom = n * sxx - sx * sx
    if denom == 0:
        return None
    return (n * sxy - sx * sy) / denom


def cmd_sweep(_args) -> None:
    sequential, concurrent = _sweep_cases()
    results: dict[tuple[str, str], dict] = {}

    print(f"# phase A: sequential timed cases ({len(sequential)})")
    for shape, renderer in sequential:
        result = _spawn_render(shape, renderer, reps=3, timeout=3 * RUN_CAP_SECONDS + 30)
        results[(shape, renderer)] = result
        print(json.dumps({k: v for k, v in result.items() if k != "stderr_tail"}))

    print(f"# phase B: concurrent classification cases ({len(concurrent)})")
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {
            pool.submit(_spawn_render, s, r, 1, RUN_CAP_SECONDS + 15): (s, r)
            for s, r in concurrent
        }
        for future, key in futures.items():
            result = future.result()
            results[key] = result
            print(json.dumps({k: v for k, v in result.items() if k != "stderr_tail"}))

    print("# phase B survivors re-run clean (sequential, reps=3)")
    for (shape, renderer), result in list(results.items()):
        if result.get("timeout") or result.get("median_s") is None:
            continue
        if (shape, renderer) in concurrent and result["median_s"] < 30:
            clean = _spawn_render(shape, renderer, reps=3, timeout=3 * RUN_CAP_SECONDS + 30)
            results[(shape, renderer)] = clean
            print(json.dumps({k: v for k, v in clean.items() if k != "stderr_tail"}))

    print("# scaling fit over completed sweep cases (log-log least squares)")
    by_e: list[tuple[float, float]] = []
    by_n: list[tuple[float, float]] = []
    for (shape, _r), result in results.items():
        if not shape.startswith("sweep-") or result.get("median_s") is None:
            continue
        by_e.append((result["edges"], result["median_s"]))
        by_n.append((result["nodes"], result["median_s"]))
    print(f"fit points: {len(by_e)}")
    print(f"exponent time~E^a: a={_fit_exponent(by_e)}")
    print(f"exponent time~N^b: b={_fit_exponent(by_n)}")
    # per-renderer fits vs E
    for renderer in RENDERERS:
        pts = [(r["edges"], r["median_s"]) for (s, _r), r in results.items()
               if s.startswith("sweep-") and _r == renderer
               and r.get("median_s") is not None]
        print(f"exponent time~E^a [{renderer}]: a={_fit_exponent(pts)} ({len(pts)} pts)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_render = sub.add_parser("render")
    p_render.add_argument("--shape", required=True, choices=sorted(SHAPES))
    p_render.add_argument("--renderer", required=True, choices=RENDERERS)
    p_render.add_argument("--reps", type=int, default=3)
    p_render.add_argument("--early-stop", type=float, default=EARLY_STOP_SECONDS)
    p_render.add_argument("--w", type=int, default=118)
    p_render.add_argument("--h", type=int, default=34)
    p_render.set_defaults(func=cmd_render)

    p_index = sub.add_parser("index-time")
    p_index.add_argument("--shape", required=True, choices=sorted(SHAPES))
    p_index.set_defaults(func=cmd_index_time)

    p_profile = sub.add_parser("profile")
    p_profile.add_argument("--shape", required=True, choices=sorted(SHAPES))
    p_profile.add_argument("--renderer", required=True, choices=RENDERERS)
    p_profile.add_argument("--w", type=int, default=118)
    p_profile.add_argument("--h", type=int, default=34)
    p_profile.set_defaults(func=cmd_profile)

    p_mount = sub.add_parser("mount")
    p_mount.add_argument("--shape", required=True, choices=sorted(SHAPES))
    p_mount.add_argument("--size", type=int, nargs=2, default=[118, 34])
    p_mount.add_argument("--reps", type=int, default=3)
    p_mount.set_defaults(func=cmd_mount)

    p_sweep = sub.add_parser("sweep")
    p_sweep.set_defaults(func=cmd_sweep)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
