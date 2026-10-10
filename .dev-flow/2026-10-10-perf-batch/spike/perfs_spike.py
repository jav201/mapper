"""PERFS feasibility spike for batch `2026-10-10-perf-batch` (Lane S).

Question: can the map mount render the map canvas ONCE instead of 3 times,
painting byte-identical output, without breaking `refresh_canvas`'s ordering
rules?

This script INSTRUMENTS `LayeredRenderer.render` with a monkeypatch (nothing
under `mapper/` is modified) and drives the real app the way
`tests/test_mod_parity.py` does: `MapperApp(ws)` + `run_test(size=(w, 34))` +
real screen pushes.  For every render call it records WHEN it happened: the
canvas `size`, the canvas `region`, the screen size and the `(w, h)` geometry
the renderer was asked to paint, plus which caller originated it
(`refresh_canvas` / `_declare_after_layout` / `on_resize` / other).

Cases:
    seed@118 / seed@87   the small E-1 seed map (`tests/test_draft_save.py`
                         `_seed_map`), mounted like `_open` does
    wide@118             a generated wide-2000 tree (`perf0b_harness.build_tree`)

Subcommands:
    baseline --out JSON   measure the CURRENT tree (unmodified or prototype)
                          and write the numbers + the sha256 of the settled
                          `#map-canvas` text and of the whole screen's
                          compositor strips (path/date normalised, the same
                          oracle `tests/test_mod_parity.py` uses).
    check --baseline JSON --expect-ncalls N
                          measure again and assert: for the seed cases the
                          mount-phase render count equals N AND the settled
                          canvas/screen hashes equal the baseline's.  This is
                          the spike's executable PASS/FAIL oracle (GREEN with
                          the prototype applied, RED on the reverted tree).

No home directory or account name ever appears in the output: only sizes,
counts and hashes.  The throwaway workspaces live in the system temp dir and
are removed afterwards; their paths are never printed or stored.

Reproduce, from the repo root:

    PYTHONDONTWRITEBYTECODE=1 python -B \\
        .dev-flow/2026-10-10-perf-batch/spike/perfs_spike.py baseline \\
        --out .dev-flow/2026-10-10-perf-batch/evidence/perfs-baseline.json
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import inspect
import json
import shutil
import sys
import tempfile
from pathlib import Path

SPIKE_DIR = Path(__file__).resolve().parent
BATCH_DIR = SPIKE_DIR.parent
REPO_ROOT = BATCH_DIR.parent.parent
for _p in (str(REPO_ROOT), str(SPIKE_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from perf0b_harness import _wait_first_paint, build_tree  # noqa: E402

HEIGHT = 34
_ORIGIN_FUNCS = ("refresh_canvas", "_declare_after_layout", "on_resize")


def _origin() -> str:
    """The first painting-frame function on the stack: who asked for render."""
    for frame in inspect.stack()[1:]:
        if frame.function in _ORIGIN_FUNCS:
            return frame.function
    return "other"


class RenderProbe:
    """Monkeypatch over `LayeredRenderer.render` recording WHEN each call ran."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def __enter__(self) -> "RenderProbe":
        from mapper.views.layered import LayeredRenderer

        self._orig = LayeredRenderer.render
        probe = self

        def counting(renderer_self, graph, state):
            entry: dict = {
                "origin": _origin(),
                "state_w": state.w,
                "state_h": state.h,
                "state_sha256": hashlib.sha256(repr(state).encode("utf-8")).hexdigest()[:16],
            }
            try:
                from textual.app import active_app

                screen = active_app.get().screen
                canvas = screen.query_one("#map-canvas")
                entry["canvas_size"] = [canvas.size.width, canvas.size.height]
                entry["canvas_region"] = [canvas.region.width, canvas.region.height]
                entry["screen_size"] = [screen.size.width, screen.size.height]
            except Exception as exc:  # noqa: BLE001 - probing must never break
                entry["probe_error"] = type(exc).__name__
            probe.calls.append(entry)
            return probe._orig(renderer_self, graph, state)

        LayeredRenderer.render = counting
        return self

    def __exit__(self, *exc) -> None:
        from mapper.views.layered import LayeredRenderer

        LayeredRenderer.render = self._orig


def _normalised_screen_sha(app, ws: Path) -> str:
    """sha256 of the whole settled frame, normalised like AT-065 does."""
    from tests.test_mod_parity import _normalise

    strips = app.screen._compositor.render_strips()  # noqa: SLF001
    text = "\n".join(_normalise("".join(seg.text for seg in strip), ws) for strip in strips)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canvas_sha(app) -> str:
    from textual.widgets import Static

    canvas = app.screen.query_one("#map-canvas", Static)
    return hashlib.sha256(canvas.render().plain.encode("utf-8")).hexdigest()


async def _settle(pilot, probe, calls_before: int, max_pauses: int = 40) -> None:
    """Pause until no new render call has appeared for a few consecutive
    pauses (the settle chain re-schedules itself via `call_after_refresh`)."""
    quiet = 0
    for _ in range(max_pauses):
        await pilot.pause()
        if len(probe.calls) == calls_before:
            quiet += 1
            if quiet >= 6:
                return
        else:
            quiet = 0
            calls_before = len(probe.calls)


async def _measure_one(app_ws: Path, map_kind: str, width: int) -> dict:
    """Mount one map at `width` x 34 and record the mount-phase render calls
    plus the settled output hashes; then one `_open`-style explicit
    `refresh_canvas` (seed only) to show what the harness's own repaint
    adds on top of the mount."""
    from mapper.app import MapperApp, MapScreen
    from mapper.store import MapStore

    app = MapperApp(str(app_ws))
    if map_kind == "wide":
        MapStore(str(app_ws)).save("p", build_tree("wide", 2000))
        map_id = "p"
    else:
        from tests.test_draft_save import _seed_map

        map_id = _seed_map(app)
    probe = RenderProbe()
    result: dict = {"width": width, "map": map_kind}
    async with app.run_test(size=(width, HEIGHT)) as pilot:
        with probe:
            await pilot.pause()
            app.push_screen(MapScreen(map_id))
            await _wait_first_paint(app, pilot)
            await _settle(pilot, probe, len(probe.calls))
            screen = app.screen
            result["mount_ncalls"] = len(probe.calls)
            result["mount_calls"] = list(probe.calls)
            result["canvas_sha256"] = _canvas_sha(app)
            result["screen_sha256"] = _normalised_screen_sha(app, app_ws)
            result["declared_for"] = (
                list(screen._declared_for) if screen._declared_for is not None else None  # noqa: SLF001
            )
            # The explicit repaint `tests/test_mod_parity.py`'s `_open` makes.
            if map_kind == "seed":
                before = len(probe.calls)
                screen.nav.cursor = "a"
                screen.refresh_canvas()
                await _settle(pilot, probe, before)
                result["explicit_ncalls"] = len(probe.calls) - before
                result["explicit_calls"] = probe.calls[before:]
                result["canvas_sha256_after_explicit"] = _canvas_sha(app)
                result["screen_sha256_after_explicit"] = _normalised_screen_sha(app, app_ws)
    return result


def _run_all() -> dict:
    out: dict = {}
    for kind, widths in (("seed", (118, 87)), ("wide", (118,))):
        for width in widths:
            ws = Path(tempfile.mkdtemp(prefix="perfs-spike-"))
            try:
                out[f"{kind}_{width}"] = asyncio.run(_measure_one(ws, kind, width))
            finally:
                shutil.rmtree(ws, ignore_errors=True)
    return out


def _print_human(results: dict) -> None:
    for case, r in results.items():
        print(f"=== {case} ===")
        print(f"mount renders: {r['mount_ncalls']}")
        for i, c in enumerate(r["mount_calls"], 1):
            print(
                f"  #{i} origin={c['origin']:<22} state=({c['state_w']},{c['state_h']}) "
                f"state_sha={c.get('state_sha256')} "
                f"canvas_size={c.get('canvas_size')} canvas_region={c.get('canvas_region')} "
                f"screen={c.get('screen_size')}"
                + (f" PROBE-ERROR={c['probe_error']}" if "probe_error" in c else "")
            )
        print(f"  settled canvas sha256: {r['canvas_sha256']}")
        print(f"  settled screen sha256: {r['screen_sha256']}")
        print(f"  settled _declared_for: {r['declared_for']}")
        if "explicit_ncalls" in r:
            print(f"explicit _open refresh_canvas renders: {r['explicit_ncalls']}")
            for i, c in enumerate(r["explicit_calls"], 1):
                print(
                    f"  #e{i} origin={c['origin']:<22} state=({c['state_w']},{c['state_h']}) "
                    f"canvas_size={c.get('canvas_size')} canvas_region={c.get('canvas_region')}"
                )
            print(f"  after-explicit canvas sha256: {r['canvas_sha256_after_explicit']}")
            print(f"  after-explicit screen sha256: {r['screen_sha256_after_explicit']}")


def cmd_baseline(args) -> None:
    results = _run_all()
    _print_human(results)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=1), encoding="utf-8")
    print(f"baseline written: {out_path}")


def cmd_check(args) -> None:
    baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    current = _run_all()
    _print_human(current)
    failures: list[str] = []
    for case, c in current.items():
        # The spike's target: NO render may run while the canvas region is
        # unassigned (canvas size (0,0), the pre-layout frame).
        prelayout = [x for x in c["mount_calls"] if x.get("canvas_size") == [0, 0]]
        if prelayout:
            failures.append(
                f"{case}: {len(prelayout)} render(s) at an unassigned canvas "
                f"region (pre-layout frame not skipped)"
            )
        if c["mount_ncalls"] != args.expect_ncalls:
            failures.append(
                f"{case}: mount_ncalls {c['mount_ncalls']} != expected {args.expect_ncalls}"
            )
        b = baseline[case]
        for field in ("canvas_sha256", "screen_sha256"):
            if c[field] != b[field]:
                failures.append(f"{case}: {field} differs from baseline")
        for field in ("canvas_sha256_after_explicit", "screen_sha256_after_explicit"):
            if c.get(field) != b.get(field):
                failures.append(f"{case}: {field} differs from baseline")
    if failures:
        print("CHECK FAIL:")
        for f in failures:
            print(f"  - {f}")
        raise SystemExit(1)
    print(f"CHECK PASS: no pre-layout render, mount renders == {args.expect_ncalls} "
          "in every case, canvas and screen byte-identical to baseline (mount "
          "and after the explicit repaint)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_base = sub.add_parser("baseline")
    p_base.add_argument("--out", required=True)
    p_base.set_defaults(func=cmd_baseline)
    p_check = sub.add_parser("check")
    p_check.add_argument("--baseline", required=True)
    p_check.add_argument("--expect-ncalls", type=int, required=True)
    p_check.set_defaults(func=cmd_check)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
