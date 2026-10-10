"""PERF0B measurement harness for batch `2026-10-10-perf-batch` (second spike).

Extends PERF0's `spike/perf_harness.py`.  Measures only what a USER can
actually reach: loadable TREES (the store's parser refuses multi-parent
DAGs, `mapper/mermaid.py:85`), MapStore save/load, CSV import
(`mapper.import_csv.preview_csv`), the duplicate-slug route into dense
DAGs, and mount-path scaling/hot functions.

Nothing under `mapper/` or `tests/` is touched or monkey-patched.  Every
potentially-slow case runs in a subprocess with a 120 s hard cap; a case
that exceeds it is recorded TIMEOUT, never a hang.

Subcommands (each prints machine-readable lines; `RESULT {...}` is JSON):

    tree-case   --shape {wide,deep,balanced} --n N [--reps R]
                  One subprocess == one case (120 s cap):
                  (a) MapScreen mount -> first paint, median of --reps
                      (fresh tmp workspace per rep, saved via MapStore);
                  (b) latency of 5 navigation key presses (press ->
                      `_rendered_for` change + settle pause), median;
                  (c) one search keystroke cycle: `slash`, type the query,
                      `enter`, until `_rendered_for` settles.
    store       --shape NAME --n N   MapStore save/load, median of 3, no UI.
    csv-import  --rows N --shape {parent,depth} [--profile]
                  preview_csv timing (median of 3); --profile adds cProfile
                  and Graph.parent_of/children_of call counts (12 000 rows).
    slug-reach  Item 4: smallest duplicate-slug CSV -> preview graph parents,
                  LayeredRenderer render (what the import preview screen
                  runs), save + re-open verdict; then the p51 dense DAG
                  reproduced via duplicate slugs, timed preview render,
                  save + re-open verdict.
    mount-profile --shape NAME --n N
                  cProfile of one mount + one keypress (the largest case);
                  top 15 cumulative/tottime + children_of/parent_of counts.
    run         Orchestrates the full matrix, spawning workers per case.

Reproduce any single number with, from the repo root:

    python .dev-flow/2026-10-10-perf-batch/spike/perf0b_harness.py tree-case \
        --shape wide --n 2000
"""
from __future__ import annotations

import argparse
import asyncio
import cProfile
import csv
import io
import json
import math
import pstats
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SPIKE_DIR = Path(__file__).resolve().parent
BATCH_DIR = SPIKE_DIR.parent
REPO_ROOT = BATCH_DIR.parent.parent
for _p in (str(REPO_ROOT), str(SPIKE_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from perf_harness import (  # noqa: E402  (PERF0's harness, same directory)
    RUN_CAP_SECONDS,
    _fit_exponent,
    _mount_once,
    chain,
)

SCRIPT_REL = ".dev-flow/2026-10-10-perf-batch/spike/perf0b_harness.py"
SIZES_N = (500, 2000, 6000, 12000)
TREE_SHAPES = ("wide", "deep", "balanced")
BRANCHING = 8
SEARCH_QUERY = "node"

from mapper.model import Edge, Ficha, Graph, Node  # noqa: E402


# --------------------------------------------------------------------------
# Tree builders (all single-parent: they survive the store round-trip)
# --------------------------------------------------------------------------

def build_tree(shape: str, n: int) -> Graph:
    if shape == "deep":
        return chain(n)
    graph = Graph(root_id="root")
    graph.add_node(Node(id="root", ficha=Ficha(title="root")))
    if shape == "wide":
        for i in range(n - 1):
            nid = f"n{i}"
            graph.add_node(Node(id=nid, ficha=Ficha(title=f"node {i}")))
            graph.edges.append(Edge(parent_id="root", child_id=nid))
        return graph
    if shape == "balanced":
        # Breadth-first, BRANCHING children per node, until N nodes exist.
        frontier = ["root"]
        counter = 0
        while counter < n - 1 and frontier:
            parent = frontier.pop(0)
            for _ in range(BRANCHING):
                if counter >= n - 1:
                    break
                nid = f"n{counter}"
                counter += 1
                graph.add_node(Node(id=nid, ficha=Ficha(title=f"node {nid}")))
                graph.edges.append(Edge(parent_id=parent, child_id=nid))
                frontier.append(nid)
        return graph
    raise SystemExit(f"unknown tree shape {shape!r}")


# Navigation keys per shape (real bindings read from mapper/keymap.py
# SCOPE_MAP: j=next_sibling, l=child).  wide: l enters the children row,
# then j walks siblings; deep/balanced: l walks down (always has a child
# in the first five levels).
NAV_KEYS = {
    "wide": ["l", "j", "j", "j", "j"],
    "deep": ["l", "l", "l", "l", "l"],
    "balanced": ["l", "l", "l", "l", "l"],
}


# --------------------------------------------------------------------------
# Worker: one tree case (mount / keypress / search)
# --------------------------------------------------------------------------

async def _wait_first_paint(app, pilot):
    while getattr(app.screen, "_rendered_for", None) is None:
        await pilot.pause()
    await pilot.pause()


async def _press_settle(pilot, screen, key: str, timeout: float = 90.0) -> float:
    """One real key press; measure until `_rendered_for` changes + settle."""
    before = screen._rendered_for
    started = time.perf_counter()
    await pilot.press(key)

    async def _changed():
        while screen._rendered_for is before:
            await pilot.pause()

    await asyncio.wait_for(_changed(), timeout=timeout)
    await pilot.pause()  # let the settle pass / frame flush run
    return time.perf_counter() - started


async def _tree_case_once(ws_dir: Path, graph: Graph, shape: str):
    """Mount once, then measure keypress latencies and one search cycle."""
    from mapper.app import MapperApp, MapScreen
    from mapper.store import MapStore

    MapStore(str(ws_dir)).save("p", graph)
    app = MapperApp(str(ws_dir))
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.push_screen(MapScreen("p"))
        await _wait_first_paint(app, pilot)
        screen = app.screen

        key_times = []
        for key in NAV_KEYS[shape]:
            key_times.append(await _press_settle(pilot, screen, key))

        # Search keystroke cycle: slash opens the input, type the query,
        # enter submits -> repaint.  Measured as one operator gesture.
        before = screen._rendered_for
        started = time.perf_counter()
        await pilot.press("slash")
        await pilot.press(*SEARCH_QUERY)
        await pilot.press("enter")

        async def _searched():
            while screen._rendered_for is before:
                await pilot.pause()

        await asyncio.wait_for(_searched(), timeout=90.0)
        await pilot.pause()
        search_s = time.perf_counter() - started
        hits_declared = screen.query_text.strip() == SEARCH_QUERY
    return key_times, search_s, hits_declared


def cmd_tree_case(args) -> None:
    graph = build_tree(args.shape, args.n)

    mount_times = []
    for _ in range(args.reps):
        ws = Path(tempfile.mkdtemp(prefix="perf0b-ws-", dir=str(BATCH_DIR / "evidence")))
        try:
            mount_times.append(asyncio.run(_mount_once(ws, "p", graph, 118, 34)))
        finally:
            shutil.rmtree(ws, ignore_errors=True)

    ws = Path(tempfile.mkdtemp(prefix="perf0b-ws-", dir=str(BATCH_DIR / "evidence")))
    try:
        key_times, search_s, declared = asyncio.run(_tree_case_once(ws, graph, args.shape))
    finally:
        shutil.rmtree(ws, ignore_errors=True)

    print("RESULT " + json.dumps({
        "shape": args.shape, "n": args.n,
        "nodes": len(graph.nodes), "edges": len(graph.edges),
        "mount_reps": args.reps, "mount_times_s": mount_times,
        "mount_median_s": statistics.median(mount_times),
        "nav_keys": NAV_KEYS[args.shape], "keypress_times_s": key_times,
        "keypress_median_s": statistics.median(key_times),
        "search_cycle_s": search_s, "search_query": SEARCH_QUERY,
        "search_declared": declared,
    }))


# --------------------------------------------------------------------------
# Worker: MapStore save/load (no UI)
# --------------------------------------------------------------------------

def cmd_store(args) -> None:
    from mapper.store import MapStore

    graph = build_tree(args.shape, args.n)
    saves, loads = [], []
    for _ in range(3):
        ws = Path(tempfile.mkdtemp(prefix="perf0b-store-", dir=str(BATCH_DIR / "evidence")))
        try:
            store = MapStore(str(ws))
            t0 = time.perf_counter()
            store.save("p", graph)
            saves.append(time.perf_counter() - t0)
            t0 = time.perf_counter()
            store.load("p")
            loads.append(time.perf_counter() - t0)
        finally:
            shutil.rmtree(ws, ignore_errors=True)
    print("RESULT " + json.dumps({
        "shape": args.shape, "n": args.n,
        "nodes": len(graph.nodes), "edges": len(graph.edges),
        "save_s": statistics.median(saves), "load_s": statistics.median(loads),
        "save_all": saves, "load_all": loads,
    }))


# --------------------------------------------------------------------------
# Worker: CSV import
# --------------------------------------------------------------------------

def _csv_rows(shape: str, n: int) -> list[tuple[str, str, str, str]]:
    """(id, title, parent, depth) rows; row 0 is the root."""
    rows = [("root", "root", "", "0")]
    if shape == "parent":
        # Binary-heap tree: node i's parent is node (i-1)//2.
        for i in range(n - 1):
            parent = "root" if i < 2 else f"n{(i - 1) // 2}"
            rows.append((f"n{i}", f"node {i}", parent, ""))
    else:  # depth: an outline that indents to depth 6 and restarts.
        last = [0] * 8
        for i in range(n - 1):
            depth = (i % 7) + 1
            last[depth] = i
            parent = f"n{last[depth - 1]}" if depth > 1 else "root"
            rows.append((f"n{i}", f"node {i}", parent, str(depth)))
    return rows


def _write_csv(path: Path, shape: str, n: int) -> None:
    rows = _csv_rows(shape, n)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["id", "title", "parent", "depth"])
        writer.writerows(rows)


def _preview(path: Path) -> Graph:
    from mapper.import_csv import preview_csv

    return preview_csv(path)


def cmd_csv_import(args) -> None:
    path = BATCH_DIR / "evidence" / f"perf0b-csv-{args.shape}-{args.rows}.csv"
    _write_csv(path, args.shape, args.rows)
    times = []
    graph = None
    for _ in range(3):
        t0 = time.perf_counter()
        graph = _preview(path)
        times.append(time.perf_counter() - t0)
    out = {
        "shape": args.shape, "rows": args.rows,
        "nodes": len(graph.nodes), "edges": len(graph.edges),
        "preview_s": statistics.median(times), "all_s": times,
    }
    if args.profile:
        profiler = cProfile.Profile()
        profiler.enable()
        graph = _preview(path)
        profiler.disable()
        stats = pstats.Stats(profiler)

        def model_counts() -> dict:
            counts = {}
            for (fname, _line, func), (cc, nc, _tt, _ct, _callers) in stats.stats.items():
                if func in ("children_of", "parent_of") and fname.endswith("model.py"):
                    counts[func] = {"primitive_calls": cc, "total_calls": nc}
            return counts

        out["model_lookups"] = model_counts()
        stream = io.StringIO()
        for sort_key in ("cumulative", "tottime"):
            stats.stream = stream
            stats.sort_stats(sort_key).print_stats(12)
        out["profile"] = stream.getvalue()
    print("RESULT " + json.dumps(out))


# --------------------------------------------------------------------------
# Worker: duplicate-slug reachability (item 4)
# --------------------------------------------------------------------------

def cmd_slug_reach(_args) -> None:
    from mapper.import_csv import preview_csv
    from mapper.store import MapStore
    from mapper.views.layered import LayeredRenderer
    from mapper.views.state import ViewState

    ev = BATCH_DIR / "evidence"

    # -- 4a: the smallest duplicate-slug CSV --------------------------------
    # "a-b" and "A B" slugify to the same id (`mapper/mermaid.slugify`
    # lowercases and collapses [-space]+ to "-").  The two rows declare
    # DIFFERENT parents, so the shared node is multi-parent.
    small = ev / "perf0b-slug-small.csv"
    small.write_text(
        "id,title,parent\n"
        "root,Root,\n"
        "p1,First parent,root\n"
        "p2,Second parent,root\n"
        "a-b,First,p1\n"
        "A B,Second,p2\n",
        encoding="utf-8",
    )
    g = preview_csv(small)
    dup_parents = sorted(
        e.parent_id for e in g.edges if e.child_id == "a-b"
    )
    t0 = time.perf_counter()
    small_render = LayeredRenderer().render(
        g, ViewState(selected_id=g.root_id, w=118, h=24))
    small_render_s = time.perf_counter() - t0
    small_multi_parent = len(dup_parents) > 1

    # -- 4a: save + re-open of the multi-parent preview graph ---------------
    ws = Path(tempfile.mkdtemp(prefix="perf0b-slug-", dir=str(ev)))
    save_error = None
    try:
        store = MapStore(str(ws))
        try:
            store.save("dup", g)
        except Exception as exc:  # noqa: BLE001
            save_error = f"{type(exc).__name__}: {exc}"
        load_error = None
        if save_error is None:
            try:
                store.load("dup")
            except Exception as exc:  # noqa: BLE001
                load_error = f"{type(exc).__name__}: {exc}"
    finally:
        shutil.rmtree(ws, ignore_errors=True)

    # -- 4b: reproduce the p51 dense DAG through duplicate slugs ------------
    from perf_harness import build_shape

    p51 = build_shape("p51")
    rows = ["id,title,parent"]
    for edge in p51.edges:
        rows.append(f"{edge.child_id},{edge.child_id},{edge.parent_id}")
    dense_csv = ev / "perf0b-slug-p51.csv"
    dense_csv.write_text("\n".join(rows) + "\n", encoding="utf-8")
    gd = preview_csv(dense_csv)
    dense_parents = sorted(
        {e.parent_id for e in gd.edges if e.child_id == "n4_0"}
    )
    t0 = time.perf_counter()
    dense_render = LayeredRenderer().render(
        gd, ViewState(selected_id=gd.root_id, w=118, h=24))
    dense_render_s = time.perf_counter() - t0

    ws = Path(tempfile.mkdtemp(prefix="perf0b-slug-", dir=str(ev)))
    dense_save_error = None
    try:
        store = MapStore(str(ws))
        try:
            store.save("dense", gd)
        except Exception as exc:  # noqa: BLE001
            dense_save_error = f"{type(exc).__name__}: {exc}"
        dense_load_error = None
        if dense_save_error is None:
            try:
                store.load("dense")
            except Exception as exc:  # noqa: BLE001
                dense_load_error = f"{type(exc).__name__}: {exc}"
    finally:
        shutil.rmtree(ws, ignore_errors=True)

    print("RESULT " + json.dumps({
        "small_csv": "id,title,parent / root,Root / p1,First parent,root / "
                     "p2,Second parent,root / a-b,First,a-b / A B,Second,p2",
        "small_nodes": len(g.nodes), "small_edges": len(g.edges),
        "small_dup_parents": dup_parents,
        "small_multi_parent": small_multi_parent,
        "small_render_s": small_render_s,
        "small_render_ok": small_render is not None and len(str(small_render)) > 0,
        "small_save_error": save_error, "small_load_error": load_error,
        "p51_csv_rows": len(rows) - 1,
        "p51_nodes": len(gd.nodes), "p51_edges": len(gd.edges),
        "p51_n4_0_parents": dense_parents,
        "p51_render_s": dense_render_s,
        "p51_save_error": dense_save_error, "p51_load_error": dense_load_error,
    }))


# --------------------------------------------------------------------------
# Worker: cProfile of one mount + one keypress (slowest reachable case)
# --------------------------------------------------------------------------

async def _profiled_mount(graph: Graph, shape: str) -> None:
    from mapper.app import MapperApp, MapScreen
    from mapper.store import MapStore

    ws = Path(tempfile.mkdtemp(prefix="perf0b-prof-", dir=str(BATCH_DIR / "evidence")))
    try:
        MapStore(str(ws)).save("p", graph)
        app = MapperApp(str(ws))
        async with app.run_test(size=(118, 34)) as pilot:
            await pilot.pause()
            app.push_screen(MapScreen("p"))
            await _wait_first_paint(app, pilot)
            screen = app.screen
            await _press_settle(pilot, screen, NAV_KEYS[shape][0])
    finally:
        shutil.rmtree(ws, ignore_errors=True)


def cmd_mount_profile(args) -> None:
    graph = build_tree(args.shape, args.n)
    profiler = cProfile.Profile()
    profiler.enable()
    asyncio.run(_profiled_mount(graph, args.shape))
    profiler.disable()
    stats = pstats.Stats(profiler)
    counts = {}
    for (fname, _line, func), (cc, nc, _tt, _ct, _callers) in stats.stats.items():
        if func in ("children_of", "parent_of") and fname.endswith("model.py"):
            counts[func] = {"primitive_calls": cc, "total_calls": nc}
    print(f"PROFILE shape={args.shape} n={args.n} "
          f"nodes={len(graph.nodes)} edges={len(graph.edges)} 118x34")
    print(f"model O(E) lookups on mount path: {json.dumps(counts)}")
    stream = io.StringIO()
    for sort_key, label in (("cumulative", "TOP 15 BY CUMULATIVE"),
                            ("tottime", "TOP 15 BY TOTTIME")):
        print(f"--- {label} ---")
        stats.stream = stream
        stats.sort_stats(sort_key).print_stats(15)
        print(stream.getvalue())
        stream = io.StringIO()
        stats = pstats.Stats(profiler)


# --------------------------------------------------------------------------
# Orchestrator: the full PERF0B matrix
# --------------------------------------------------------------------------

def _spawn(cmd_args: list[str], timeout: float) -> dict:
    cmd = [sys.executable, str(Path(SCRIPT_REL)), *cmd_args]
    try:
        proc = subprocess.run(
            cmd, cwd=str(REPO_ROOT), capture_output=True, text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"cmd": cmd_args, "timeout": True}
    for line in proc.stdout.splitlines():
        if line.startswith("RESULT "):
            result = json.loads(line[len("RESULT "):])
            result["timeout"] = False
            return result
    return {"cmd": cmd_args, "timeout": True,
            "stderr_tail": proc.stderr[-500:]}


def cmd_run(_args) -> None:
    trees: dict[tuple[str, int], dict] = {}
    stores: dict[tuple[str, int], dict] = {}
    csvs: dict[tuple[str, int], dict] = {}

    print(f"# tree cases: {len(TREE_SHAPES) * len(SIZES_N)} "
          f"(one subprocess each, {RUN_CAP_SECONDS} s cap)")
    for shape in TREE_SHAPES:
        for n in SIZES_N:
            res = _spawn(["tree-case", "--shape", shape, "--n", str(n),
                          "--reps", "3"], RUN_CAP_SECONDS + 30)
            trees[(shape, n)] = res
            print(json.dumps({k: v for k, v in res.items() if k != "profile"}))

    print("# store round-trip (no UI)")
    for shape in TREE_SHAPES:
        for n in SIZES_N:
            res = _spawn(["store", "--shape", shape, "--n", str(n)], 120)
            stores[(shape, n)] = res
            print(json.dumps(res))

    print("# csv import")
    for shape in ("parent", "depth"):
        for n in (1000, 5000, 12000):
            res = _spawn(["csv-import", "--rows", str(n), "--shape", shape], 120)
            csvs[(shape, n)] = res
            print(json.dumps({k: v for k, v in res.items() if k != "profile"}))

    print("# log-log fit: mount time ~ N^b per shape")
    for shape in TREE_SHAPES:
        pts = [(n, r["mount_median_s"]) for (s, n), r in trees.items()
               if s == shape and not r.get("timeout") and r.get("mount_median_s")]
        print(f"fit[{shape}] points={len(pts)} exponent={_fit_exponent(pts)}")
    pts = [(n, r["mount_median_s"]) for (s, n), r in trees.items()
           if not r.get("timeout") and r.get("mount_median_s")]
    print(f"fit[all] points={len(pts)} exponent={_fit_exponent(pts)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_tree = sub.add_parser("tree-case")
    p_tree.add_argument("--shape", required=True, choices=TREE_SHAPES)
    p_tree.add_argument("--n", type=int, required=True)
    p_tree.add_argument("--reps", type=int, default=3)
    p_tree.set_defaults(func=cmd_tree_case)

    p_store = sub.add_parser("store")
    p_store.add_argument("--shape", required=True, choices=TREE_SHAPES)
    p_store.add_argument("--n", type=int, required=True)
    p_store.set_defaults(func=cmd_store)

    p_csv = sub.add_parser("csv-import")
    p_csv.add_argument("--rows", type=int, required=True)
    p_csv.add_argument("--shape", required=True, choices=("parent", "depth"))
    p_csv.add_argument("--profile", action="store_true")
    p_csv.set_defaults(func=cmd_csv_import)

    p_slug = sub.add_parser("slug-reach")
    p_slug.set_defaults(func=cmd_slug_reach)

    p_prof = sub.add_parser("mount-profile")
    p_prof.add_argument("--shape", required=True, choices=TREE_SHAPES)
    p_prof.add_argument("--n", type=int, required=True)
    p_prof.set_defaults(func=cmd_mount_profile)

    p_run = sub.add_parser("run")
    p_run.set_defaults(func=cmd_run)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
