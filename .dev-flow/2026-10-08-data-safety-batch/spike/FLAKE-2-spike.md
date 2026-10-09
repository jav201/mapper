# FLAKE-2 spike (US-004 / B-98) -- `test_hlr_n16_4_legend_declares_its_own_keys[size0]`

State: **finding (hypothesis refuted, mechanism reproduced and traced).** Spike only; no product or test edit.
Env: Python, Textual 8.2.8, pytest 8.3.4, pytest-asyncio 0.25.0, pytest-timeout (no pytest-repeat). 16 cores.

## 1. When `left` counts as "working" (tests/test_help_scope.py)
- Universe (`:349-352`) includes `left`: it is a framework binding of the legend's `VerticalScroll` (`ScrollableContainer`: left/right/up/down/...), not a `SCOPE_HELP` row. Confirmed: universe = declared 8 keys + `ctrl+pagedown, ctrl+pageup, left, right, shift+tab, super+c, tab`.
- A key is "effective" iff `(pane.scroll_offset, len(screen_stack), app.screen, app.focused)` differs between `before` (`:370`) and `after` (`:375`). Nothing attributes the change to the key.
- `left`/`right` are INERT in a healthy run: `pane.max_scroll_x == 0` (virtual width 39 < pane width 40), so `action_scroll_left` raises SkipAction. Measured: 8 effective keys == 8 declared, at all three sizes.
- `painted` (`:383-384`) only ever contains declared keys, so any extra effective key fails as "work but not painted".

## 2. Hypothesis check
Intake hypothesis (horizontal reflow makes `left` really scroll) is **refuted**: traced failures show unchanged geometry (see 3); `max_scroll_x` stayed 0.

## 3. Actual mechanism
The test positions the pane with `pane.scroll_to(y=max_scroll_y // 2, animate=False)` (`:361`). Textual 8.2.8 `Widget.scroll_to` has `immediate=False` by default, which queues `_scroll_to` via `call_after_refresh`. One `pilot.pause()` does not guarantee that queued call has run. When the machine is loaded it runs *after* `before` was sampled and *during* the next key's window, so an inert key sees `scroll_offset` jump to the mid position and is counted as effective.
Trace (instrumented copy of the loop, 3 hits): `key=left`, `before=Offset(0,0)` (position left by the preceding `home`), `after=Offset(0,23)` (the mid position), same screen/focus, geometry identical before/after (`max_scroll_y 46, virtual (39,82), pane (40,36), app (140,45), -docked`). `left` is simply the inert key that follows `home` (sorted order: escape, home, left); the same defect can hit any inert key (`right`, `ctrl+pagedown` also appeared in the forced run).

## 4. Reproduction
| attempt | result |
|---|---|
| node alone, unloaded, 1x3 sizes | 3 passed, 0/3 |
| scenario x30 per size (90 runs, one process), 16 busy CPU procs | **1/90** fail, size0, exact message `work but not painted: ['left']; painted but inert: []` |
| instrumented scenario, size0 only, 3 procs x 40 (120 runs), under load | **3/120** spurious `left` (all with before y=0 / after y=23) |
| earlier 6 runs under load | 0/6 |
| full file / after preceding files (`test_github.py` precedes it) / full default lane | not run: cheap load repro sufficed |
Rate ~1-2.5% per size0 run under CPU saturation, near 0 unloaded. Scratch drivers: `repeat_flake2.py` (SPIKE_N, SPIKE_SIZES), `trace_flake2.py`. Run with `--timeout=0` (the repo's per-test timeout kills multi-run loops).

Deterministic RED/GREEN (`red_green_flake2.py`, run twice each): a fixture makes ONLY the test's own `scroll_to` queued call land 150 ms late (emulating load).
- RED (current step): fails 2/2, e.g. `work but not painted: ['ctrl+pagedown','left','right']`.
- GREEN (`immediate=True` + settle assert): passes 2/2 under the same delay.

## 5. Proposed fix (test-side, 2 lines, no product change)
In `tests/test_help_scope.py` ~`:361`: `pane.scroll_to(y=pane.max_scroll_y // 2, animate=False, immediate=True)` and `assert pane.scroll_offset.y == pane.max_scroll_y // 2` before sampling `before` (fail loud if the setup did not land). Why test-side: the product is behaving correctly (`left` is inert; the legend honestly paints only its own keys); the oracle is racy because setup is deferred. Same pattern should be grepped in sibling arms (`tests/test_help_scope.py` `_harvest`, other `scroll_to(... animate=False)` before a measured press).
Rejected: adding `left`/`right` to the framework exclusion -- would hide a real foreign key that starts scrolling; and sleeping longer -- still a race.

## 6. Regression test that fails before the fix
Add an arm that applies the late-landing fixture of `red_green_flake2.py` (monkeypatch `Widget.call_after_refresh` to delay `_scroll_to` for the test's own positioning call) and runs the n16_4 loop: it fails on the current step (RED, seen) and passes with `immediate=True` (GREEN, seen). It needs no load and no repeat count.

## Limits
Cause of the first-observed 2026-10-03 failure assumed identical (same message, size0, same key); not provable from one old log. Python 3.11 / one machine only. Pass rate after the fix under load not measured (expected 0; verify with `SPIKE_N` loop on a patched copy before merging).
