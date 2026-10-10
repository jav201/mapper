"""PERF0C focused profile for batch `2026-10-10-perf-batch`.

cProfile of the three user-reachable hot paths, one subprocess per case
(120 s cap enforced by the caller):

    nav     One navigation keypress sequence (`l`, then `j`) on an
            already-mounted wide-2000 map: profiler starts after first
            paint, stops after the second repaint settles.  Top 20 by
            cumulative and tottime (file:line, repo-relative) plus call
            counts of Graph.children_of / Graph.parent_of and every
            renderer / rail / minimap / inspector refresh function that
            appears in the profile.
    mount   The MOUNT of the same wide-2000 map (push_screen -> first
            paint).  Same outputs.
    store   MapStore.save and MapStore.load of a wide-6000 tree (no UI),
            profiled separately.  Top 15 each.

Nothing under `mapper/` or `tests/` is touched or monkey-patched.  All
printed paths are repo-relative (the repo root prefix is stripped, so no
home directory or account name ever appears in the output).

Reproduce any case from the repo root:

    PYTHONDONTWRITEBYTECODE=1 python -B \\
        .dev-flow/2026-10-10-perf-batch/spike/perf0c_profile.py nav
"""
from __future__ import annotations

import argparse
import asyncio
import cProfile
import io
import json
import pstats
import shutil
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

from perf0b_harness import (  # noqa: E402
    _press_settle,
    _wait_first_paint,
    build_tree,
)

WIDTH, HEIGHT = 118, 34

# Component files whose refresh/lookup functions get their own call-count
# table (renderer / rail / minimap / inspector / crumb / model lookups).
COMPONENT_SUFFIXES = (
    "mapper/model.py",
    "mapper/views/lane.py",
    "mapper/views/layered.py",
    "mapper/views/outline.py",
    "mapper/views/radial.py",
    "mapper/views/state.py",
    "mapper/widgets/rail.py",
    "mapper/widgets/inspector.py",
    "mapper/screens/map/painting.py",
    "mapper/screens/map/screen.py",
)


def _rel(path: str) -> str:
    """Repo-relative for project files; package-relative for third-party /
    stdlib files (textual/app.py, asyncio/events.py, ...).  No home path or
    account name ever survives into the output."""
    norm = path.replace("/", "\\")
    repo = str(REPO_ROOT).replace("/", "\\")
    if norm.startswith(repo + "\\"):
        return path[len(str(REPO_ROOT)) + 1:]
    for marker in ("\\site-packages\\", "\\Lib\\"):
        idx = norm.find(marker)
        if idx != -1:
            return norm[idx + len(marker):]
    return norm


def _tables(profiler: cProfile.Profile, top: int) -> dict:
    """Top-N by cumulative and by tottime, as rows of
    (function, file:line, ncalls, tottime, cumtime)."""
    out = {}
    for sort_key in ("cumulative", "tottime"):
        stats = pstats.Stats(profiler)
        rows = []
        for (fname, line, func), (_cc, nc, tt, ct, _callers) in stats.stats.items():
            rows.append((ct if sort_key == "cumulative" else tt,
                         func, f"{_rel(fname)}:{line}", nc, tt, ct))
        rows.sort(key=lambda r: r[0], reverse=True)
        out[sort_key] = [
            {"func": f, "fileline": fl, "ncalls": n, "tottime": round(tt, 4),
             "cumtime": round(ct, 4)}
            for _key, f, fl, n, tt, ct in rows[:top]
        ]
    return out


def _component_counts(profiler: cProfile.Profile) -> dict:
    """Call counts for model lookups + every component refresh function."""
    counts = {}
    for (fname, _line, func), (_cc, nc, _tt, _ct, _callers) in pstats.Stats(profiler).stats.items():
        rel = _rel(fname).replace("\\", "/")
        if any(rel.endswith(sfx) for sfx in COMPONENT_SUFFIXES):
            key = f"{rel}:{func}"
            counts[key] = nc
    return dict(sorted(counts.items()))


def _emit(label: str, profiler: cProfile.Profile, top: int) -> None:
    print(f"=== {label} ===")
    tables = _tables(profiler, top)
    for sort_key in ("cumulative", "tottime"):
        print(f"--- TOP {top} BY {sort_key.upper()} ---")
        for i, row in enumerate(tables[sort_key], 1):
            print(f"{i:2d}. {row['func']:<28} {row['fileline']:<46} "
                  f"ncalls={row['ncalls']:<9} tottime={row['tottime']:>9.4f} "
                  f"cumtime={row['cumtime']:>9.4f}")
    print("--- COMPONENT / MODEL CALL COUNTS ---")
    print(json.dumps(_component_counts(profiler), indent=1))


# --------------------------------------------------------------------------
# Case 1: one navigation keypress pair on a mounted wide-2000 map
# --------------------------------------------------------------------------

async def _nav_once(ws_dir: Path) -> None:
    from mapper.app import MapperApp, MapScreen
    from mapper.store import MapStore

    MapStore(str(ws_dir)).save("p", build_tree("wide", 2000))
    app = MapperApp(str(ws_dir))
    async with app.run_test(size=(WIDTH, HEIGHT)) as pilot:
        await pilot.pause()
        app.push_screen(MapScreen("p"))
        await _wait_first_paint(app, pilot)
        screen = app.screen
        profiler = cProfile.Profile()
        profiler.enable()
        await _press_settle(pilot, screen, "l")
        await _press_settle(pilot, screen, "j")
        profiler.disable()
        return profiler


def cmd_nav(_args) -> None:
    ws = Path(tempfile.mkdtemp(prefix="perf0c-nav-", dir=str(BATCH_DIR / "evidence")))
    try:
        t0 = time.perf_counter()
        profiler = asyncio.run(_nav_once(ws))
        wall = time.perf_counter() - t0
    finally:
        shutil.rmtree(ws, ignore_errors=True)
    print(f"PROFILE nav wide-2000: keys 'l' then 'j' on mounted map, "
          f"{WIDTH}x{HEIGHT}, wall under profiler {wall:.3f} s")
    _emit("nav wide-2000 (l, j)", profiler, 20)


# --------------------------------------------------------------------------
# Case 2: mount of the same wide-2000 map (open -> first paint)
# --------------------------------------------------------------------------

async def _mount_once(ws_dir: Path) -> cProfile.Profile:
    from mapper.app import MapperApp, MapScreen
    from mapper.store import MapStore

    MapStore(str(ws_dir)).save("p", build_tree("wide", 2000))
    app = MapperApp(str(ws_dir))
    async with app.run_test(size=(WIDTH, HEIGHT)) as pilot:
        await pilot.pause()
        profiler = cProfile.Profile()
        profiler.enable()
        app.push_screen(MapScreen("p"))
        await _wait_first_paint(app, pilot)
        profiler.disable()
        return profiler


def cmd_mount(_args) -> None:
    ws = Path(tempfile.mkdtemp(prefix="perf0c-mount-", dir=str(BATCH_DIR / "evidence")))
    try:
        t0 = time.perf_counter()
        profiler = asyncio.run(_mount_once(ws))
        wall = time.perf_counter() - t0
    finally:
        shutil.rmtree(ws, ignore_errors=True)
    print(f"PROFILE mount wide-2000: push_screen -> first paint, "
          f"{WIDTH}x{HEIGHT}, wall under profiler {wall:.3f} s")
    _emit("mount wide-2000", profiler, 20)


# --------------------------------------------------------------------------
# Case 3: MapStore.save / MapStore.load of a wide-6000 tree
# --------------------------------------------------------------------------

def cmd_store(_args) -> None:
    from mapper.store import MapStore

    graph = build_tree("wide", 6000)
    ws = Path(tempfile.mkdtemp(prefix="perf0c-store-", dir=str(BATCH_DIR / "evidence")))
    try:
        store = MapStore(str(ws))

        profiler = cProfile.Profile()
        profiler.enable()
        store.save("p", graph)
        profiler.disable()
        save_prof = profiler

        profiler = cProfile.Profile()
        profiler.enable()
        store.load("p")
        profiler.disable()
        load_prof = profiler
    finally:
        shutil.rmtree(ws, ignore_errors=True)
    print(f"PROFILE store wide-6000: nodes={len(graph.nodes)} "
          f"edges={len(graph.edges)}")
    _emit("MapStore.save wide-6000", save_prof, 15)
    _emit("MapStore.load wide-6000", load_prof, 15)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("nav").set_defaults(func=cmd_nav)
    sub.add_parser("mount").set_defaults(func=cmd_mount)
    sub.add_parser("store").set_defaults(func=cmd_store)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
