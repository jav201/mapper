"""PERFP4 wall-clock evidence for batch `2026-10-10-perf-batch`.

MEASUREMENT ONLY.  Compares HEAD (this worktree) against BASE (sibling
worktree at commit 5cde04e) on four wall-clock cases, interleaving
BASE/HEAD per case and taking the median of 3 per side:

    A  mount -> first paint, wide-2000 at 118x34 (perf0b's mount measurement)
    B  two navigation keys `l` then `j` on a mounted wide-2000 map at 118x34
       (wall time of key -> repaint settle, per key)
    C  MapStore.save and MapStore.load of a wide-6000 tree (no UI)
    D  layered render of the dense p51 shape (perf_harness), one render

Each measurement runs in a FRESH subprocess with `cwd` set to the tree
being measured and `PYTHONDONTWRITEBYTECODE=1`, timeout 150 s.  Nothing
under `mapper/` or `tests/` is changed.  The measurement logic is the
existing spike harness (`perf_harness.py`, `perf0b_harness.py`): their
functions are imported and called directly; the only trick is resolving
the `mapper` package to the tree being measured (import `mapper.model`
from the tree *first*, so every later `from mapper.* import ...` binds to
that tree's package via `sys.modules`).

Subcommands:

    worker --tree PATH --case {A,B,C,D}
                   One measurement in this process; prints a single
                   `RESULT {json}` line to stdout.  `mapper` resolves to
                   `--tree`.
    run            Orchestrator: interleaves base/head per case, writes the
                   transcript to evidence/p4-wallclock.transcript, prints the
                   summary table.

Reproduce the whole run from the repo root:

    PYTHONDONTWRITEBYTECODE=1 python \
        .dev-flow/2026-10-10-perf-batch/spike/p4_wallclock.py run
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
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

BASE_COMMIT = "5cde04e"
TIMEOUT_SECONDS = 150.0

CASES = ("A", "B", "C", "D")
CASE_METRICS = {
    "A": ["mount_s"],
    "B": ["l_s", "j_s"],
    "C": ["save_s", "load_s"],
    "D": ["render_s"],
}
CASE_LABELS = {
    "A": "A mount wide-2000 118x34",
    "B": "B nav 'l' / 'j' wide-2000",
    "C": "C store save/load wide-6000",
    "D": "D layered p51",
}
METRIC_LABELS = {
    "mount_s": "A mount",
    "l_s": "B nav 'l'",
    "j_s": "B nav 'j'",
    "save_s": "C save",
    "load_s": "C load",
    "render_s": "D render",
}

SCRIPT_REL = os.path.relpath(Path(__file__).resolve(), REPO_ROOT)


def _rel(tree: str) -> str:
    """Repo-relative label for a tree path (never a home path / account name)."""
    try:
        rel = os.path.relpath(tree, str(REPO_ROOT))
    except ValueError:
        rel = tree
    return rel.replace("\\", "/")


# --------------------------------------------------------------------------
# Worker: one measurement in this process, `mapper` bound to `--tree`
# --------------------------------------------------------------------------

def _worker_tree_mapper(tree: str):
    """Insert `tree` first and import its `mapper` package.

    Once `mapper` is in `sys.modules` from `tree`, every later submodule
    import (`mapper.app`, `mapper.store`, `mapper.views.*`) resolves to
    `tree`'s package directory regardless of `sys.path` order.  This is what
    lets the trunk harness functions run unchanged against either tree.
    """
    sys.path.insert(0, tree)
    import mapper.model  # noqa: F401  (bind the tree's mapper package)

    sys.path.insert(0, str(SPIKE_DIR))  # harness importable (defensive)
    from perf_harness import (  # noqa: F401
        _mount_once,
        build_shape,
        make_renderer,
        view_state,
    )
    from perf0b_harness import (  # noqa: F401
        _press_settle,
        _wait_first_paint,
        build_tree,
    )


def _case_A() -> dict:
    from perf_harness import _mount_once
    from perf0b_harness import build_tree

    graph = build_tree("wide", 2000)
    ws = Path(tempfile.mkdtemp(prefix="perfp4-a-", dir=str(BATCH_DIR / "evidence")))
    try:
        mount_s = asyncio.run(_mount_once(ws, "p", graph, 118, 34))
    finally:
        shutil.rmtree(ws, ignore_errors=True)
    return {"mount_s": mount_s}


def _case_B() -> dict:
    from mapper.app import MapperApp, MapScreen
    from mapper.store import MapStore
    from perf0b_harness import _press_settle, _wait_first_paint, build_tree

    graph = build_tree("wide", 2000)
    ws = Path(tempfile.mkdtemp(prefix="perfp4-b-", dir=str(BATCH_DIR / "evidence")))
    try:
        MapStore(str(ws)).save("p", graph)
        app = MapperApp(str(ws))

        async def _run():
            async with app.run_test(size=(118, 34)) as pilot:
                await pilot.pause()
                app.push_screen(MapScreen("p"))
                await _wait_first_paint(app, pilot)
                screen = app.screen
                l_s = await _press_settle(pilot, screen, "l")
                j_s = await _press_settle(pilot, screen, "j")
            return l_s, j_s

        l_s, j_s = asyncio.run(_run())
    finally:
        shutil.rmtree(ws, ignore_errors=True)
    return {"l_s": l_s, "j_s": j_s}


def _case_C() -> dict:
    from mapper.store import MapStore
    from perf0b_harness import build_tree

    graph = build_tree("wide", 6000)
    ws = Path(tempfile.mkdtemp(prefix="perfp4-c-", dir=str(BATCH_DIR / "evidence")))
    try:
        store = MapStore(str(ws))
        t0 = time.perf_counter()
        store.save("p", graph)
        save_s = time.perf_counter() - t0
        t0 = time.perf_counter()
        store.load("p")
        load_s = time.perf_counter() - t0
    finally:
        shutil.rmtree(ws, ignore_errors=True)
    return {"save_s": save_s, "load_s": load_s}


def _case_D() -> dict:
    from perf_harness import build_shape, make_renderer, view_state

    graph = build_shape("p51")
    renderer = make_renderer("layered")
    state = view_state(graph, 118, 34)
    t0 = time.perf_counter()
    renderer.render(graph, state)
    render_s = time.perf_counter() - t0
    return {"render_s": render_s}


_CASE_FN = {"A": _case_A, "B": _case_B, "C": _case_C, "D": _case_D}


def cmd_worker(args) -> None:
    _worker_tree_mapper(args.tree)
    try:
        result = _CASE_FN[args.case]()
        result["case"] = args.case
        result["error"] = None
    except Exception as exc:  # noqa: BLE001  (record, never hang)
        result = {"case": args.case, "error": f"{type(exc).__name__}: {exc}"}
    print("RESULT " + json.dumps(result))


# --------------------------------------------------------------------------
# Orchestrator
# --------------------------------------------------------------------------

def _resolve_base_tree() -> str:
    base = REPO_ROOT.parent / "perf-base"
    if not (base / "mapper").is_dir():
        # create the BASE worktree if it is not already present
        subprocess.run(
            ["git", "worktree", "add", str(base), BASE_COMMIT],
            cwd=str(REPO_ROOT), capture_output=True, text=True, check=True,
        )
    return str(base)


def _spawn(tree: str, case: str) -> dict:
    cmd = [sys.executable, str(Path(__file__).resolve()), "worker",
           "--tree", tree, "--case", case]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd, cwd=tree, capture_output=True, text=True,
            timeout=TIMEOUT_SECONDS, env=env,
        )
        wall = time.perf_counter() - t0
    except subprocess.TimeoutExpired:
        return {"case": case, "tree": tree, "timeout": True,
                "wall": TIMEOUT_SECONDS}
    for line in proc.stdout.splitlines():
        if line.strip().startswith("RESULT "):
            data = json.loads(line.strip()[len("RESULT "):])
            data["timeout"] = False
            data["wall"] = wall
            data["rc"] = proc.returncode
            return data
    return {"case": case, "tree": tree, "timeout": False, "wall": wall,
            "rc": proc.returncode, "no_result": True,
            "stderr_tail": proc.stderr[-800:]}


def _median(vals: list[float]) -> float | None:
    return statistics.median(vals) if vals else None


def cmd_run(_args) -> None:
    head = str(REPO_ROOT)
    base = _resolve_base_tree()
    head_rel = _rel(head)
    base_rel = _rel(base)

    lines: list[str] = []
    def emit(s: str = "") -> None:
        lines.append(s)
        print(s)

    emit("# PERFP4 wall-clock evidence — batch 2026-10-10-perf-batch")
    emit(f"# generated by {SCRIPT_REL}")
    emit("")
    emit("## Machine")
    emit(f"cpu_count = {os.cpu_count()}")
    emit(f"python   = {sys.version.split()[0]} ({sys.executable.split(os.sep)[-1]})")
    emit("")
    emit("## Trees")
    emit(f"HEAD = {head_rel}  (this worktree)")
    emit(f"BASE = {base_rel}  (commit {BASE_COMMIT})")
    emit("")
    emit("## Protocol")
    emit(f"Each case: base, head, base, head, base, head (interleaved), "
         f"median of 3 per side.")
    emit(f"Each measurement: fresh subprocess, cwd = tree, "
         f"PYTHONDONTWRITEBYTECODE=1, timeout {TIMEOUT_SECONDS:.0f} s.")
    emit("")
    emit("## Commands")
    emit(f"# full run:")
    emit(f"PYTHONDONTWRITEBYTECODE=1 python {SCRIPT_REL} run")
    emit(f"# one worker (cwd set to the tree):")
    emit(f"PYTHONDONTWRITEBYTECODE=1 python {SCRIPT_REL} worker "
         f"--tree <tree> --case <CASE>")
    emit("")

    # (case, metric) -> {"base": [..], "head": [..]}
    collected: dict[tuple[str, str], dict[str, list[float]]] = {}
    for case in CASES:
        for metric in CASE_METRICS[case]:
            collected[(case, metric)] = {"base": [], "head": []}

    raw: list[dict] = []
    for case in CASES:
        emit(f"## Case {case} — {CASE_LABELS[case]}")
        for run_index in range(3):
            for side in ("base", "head"):
                tree = base if side == "base" else head
                tree_rel = base_rel if side == "base" else head_rel
                result = _spawn(tree, case)
                raw.append({"case": case, "side": side, "run": run_index + 1,
                            **result})
                if result.get("timeout"):
                    emit(f"  {side} run{run_index + 1}: TIMEOUT "
                         f"(> {TIMEOUT_SECONDS:.0f} s)")
                    continue
                if result.get("error") or result.get("no_result"):
                    tail = result.get("stderr_tail", "")
                    err = result.get("error") or result.get("no_result")
                    emit(f"  {side} run{run_index + 1}: ERROR {err} "
                         f"wall={result['wall']:.3f}s {tail}")
                    continue
                for metric in CASE_METRICS[case]:
                    val = result.get(metric)
                    if val is None:
                        continue
                    collected[(case, metric)][side].append(val)
                    emit(f"  {side} run{run_index + 1}: {metric} = "
                         f"{val:.6f} s (wall {result['wall']:.3f} s)")
        emit("")

    # Summary per metric
    emit("## Summary (min / median / max, seconds)")
    emit("")
    emit("metric | base min | base median | base max | head min | head median "
         "| head max | speed-up (base/head)")
    emit("---|---|---|---|---|---|---|---")
    final_rows: list[tuple[str, str, str]] = []
    for case in CASES:
        for metric in CASE_METRICS[case]:
            label = METRIC_LABELS[metric]
            b = collected[(case, metric)]["base"]
            h = collected[(case, metric)]["head"]
            bmed, hmed = _median(b), _median(h)
            def fmt(v):
                return "TIMEOUT" if v is None else f"{v:.4f}"
            if bmed and hmed and hmed > 0:
                speedup = f"{bmed / hmed:.2f}x"
            else:
                speedup = "n/a"
            emit(f"{label} | {fmt(min(b)) if b else '-'} | {fmt(bmed)} | "
                 f"{fmt(max(b)) if b else '-'} | "
                 f"{fmt(min(h)) if h else '-'} | {fmt(hmed)} | "
                 f"{fmt(max(h)) if h else '-'} | {speedup}")
            final_rows.append((label, fmt(bmed), fmt(hmed), speedup))
    emit("")

    # Final table
    emit("## Final table")
    emit("")
    emit("case | base median | head median | speed-up")
    emit("---|---|---|---")
    for label, b, h, s in final_rows:
        emit(f"{label} | {b} | {h} | {s}")
    emit("")

    transcript = "\n".join(lines) + "\n"
    out_path = BATCH_DIR / "evidence" / "p4-wallclock.transcript"
    out_path.write_text(transcript, encoding="utf-8")
    print(f"\n# transcript written to {_rel(str(out_path))}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_worker = sub.add_parser("worker")
    p_worker.add_argument("--tree", required=True)
    p_worker.add_argument("--case", required=True, choices=CASES)
    p_worker.set_defaults(func=cmd_worker)
    p_run = sub.add_parser("run")
    p_run.set_defaults(func=cmd_run)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
