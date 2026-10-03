# Increment 056 -- Gate-1: FLAKE-1, FLAKE-4 and the Inc-EN carries

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `9a2d1c7`. Authority: `A-138` (appended to `01-requirements.md`, dated 2026-10-03) and the Inc-EN closure block of `state.json` (`FLAKES`, `CARRIES`). Source files: 1 (`mapper/keymap.py`, a docstring only; cap 4, no overage). Everything else is tests and docs. `state.json` was not touched.

## 1. What changed

**FLAKE-1 (`test_llr_cnv_3_1_the_parent_walk_maps_a_nested_widget_to_its_region`, `tests/test_app.py`): a TEST race, not a user race.**

- Cause, measured. `MapScreen.on_mount` ends with `self.call_after_refresh(self._park_focus)` (`mapper/app.py`), which runs `set_focus(None)`. The test focused `#insp-title` after ONE `pilot.pause()`. When the park had not yet run, it ran after the focus and blurred the field: `app.focused` ended `None`, the owner `''`, the recorded signature `assert '' == 'inspector'`.
- Evidence it is that and not something else: a harness wrapped `Screen.set_focus` and logged every call in each failing iteration: `['insp-title', None]`, the `None` always coming from `_park_focus` (`app.py:2174`). In the same failing iterations the widget was the same object as a fresh query, attached, running, `can_focus=True`, with a 1-row region, so a stale or unmounted widget is ruled out. Before the focus call `app.focused` was `map-rail` (the park had not happened yet). Extra pauses afterwards never restored the focus (29 tried), which is why the older note "more pauses do not fix it" was true of the READ and misleading about the cause: the fix is to wait BEFORE focusing.
- Not a user race: the park is the intended arrival behaviour (its comment: a focused `Input` would eat the map's single-letter keys), and it runs within the first frames after the map mounts; an operator cannot Tab into a field in that window. No source change is owed.
- Fix: the test waits (bounded, 40 pauses) until nothing is focused (the park has run), queries and focuses `#insp-title`, waits (bounded, 40 pauses) until `app.focused is title`, then runs the UNCHANGED assertion `screen._focus_owner() == "inspector"`. Oracle unchanged.

**FLAKE-4 (`tests/test_inc9c.py::test_inc9c_ux_f3_components_scroll_and_every_tab_stop_is_on_screen`): a TEST race.** Visibility was read after one `pilot.pause()` while the grid's scroll back to the first stop (about 7 rows) was still animating. Measured: the focused widget became fully visible after 1 or 3 extra pauses in the failing steps, with a fractional `scroll_y` (4.97, 1.31, 1.34) at the single read. New helper `_until_visible` polls the same observable (`geo.clip` contains `geo.region`, the existing `_visible`) for at most 40 pauses; it is called before the two reads. The assertions are unchanged, and a widget that never becomes visible still lands in `hidden`.

**Carries.**
- `EN9-REV-F1`: docstring of `keymap.textual_bindings` reworded (source, docstring only): the binding is reachable only programmatically today (`app.set_focus(None)`). Measured here: Tab, shift+Tab and a click on the field keep focus on `#repo-input`; `set_focus(None)` gives `None`. Dated correction notes appended to `A-137` and to record 055.
- `EN9-REV-F2`: note appended to record 055 section 1, dropping "and the screen `BINDINGS`" from the first bullet.
- `EN9-REV-F3`: `tests/test_keymap.py::test_groups_for_keybar_drops_the_typed_help_key_whatever_the_group_order`: no `?` row for `['plug', 'app']` or `['app', 'plug']`, with positive controls (`['nav', 'app']` and `['app']` DO list `?`).
- Record 051: back-reference appended (`EN2-REV-F1` was the `_rebuild` restore comment, settled by `EN-8`, per the record 048 notes).
- `A-138` appended.

## 2. Files modified

Source (1): `mapper/keymap.py` (docstring). Tests (3): `tests/test_app.py`, `tests/test_inc9c.py`, `tests/test_keymap.py`. Docs (4): `01-requirements.md` (`A-137` correction, `A-138`), records 051 and 055 (appended notes), this record. Scratch (not in the repo): harnesses and logs under the session scratchpad; a scratch `git worktree` of `9a2d1c7` under `%TEMP%` (removed).

## 3. How to test

`python -B -W error::SyntaxWarning -m pytest -q -rf tests/test_app.py tests/test_inc9c.py tests/test_keymap.py` (temp HOME and USERPROFILE, git identity from environment variables, default basetemp). The races only show under load, so the claims below rest on the harness numbers and the mutants, not on one green run.

## 4. Measurements and mutants

Rates on `9a2d1c7` (BEFORE) and the fixed tree (AFTER). "Load" = a second pytest process running the full default lane in a loop on the base worktree, plus whatever else the shared machine was running (other agents' pytest processes were visible, so the load is real but not controlled).

| Measurement | Before | After |
|---|---|---|
| FLAKE-1, isolated test, fresh process x50, no deliberate load | 0/50 | 0/50 (taken under load) |
| FLAKE-1, whole `test_app.py` x50, no deliberate load | 1/50 (signature `assert '' == 'inspector'`) | 0/50 (taken under load) |
| FLAKE-1, isolated x50, under load | 0/50 | 0/50 |
| FLAKE-1, whole `test_app.py` x50, under load | 0/50 | 0/50 |
| FLAKE-1, arm body in ONE process, fresh app per iteration, no deliberate load | 2/300, 5/400 (about 1%) | 0/500 |
| FLAKE-1, same harness, under load, single-pause vs poll | 7/600 (1.2%) | 0/600 |
| FLAKE-4, `-k ux_f3` x50 (2 sizes per run), under load | 1/50 | 0/50 |
| FLAKE-4, mutant (poll disabled) x100, under load | 1/100 | -- |
| FLAKE-4, fixed x100, under load | -- | 0/100 |
| FLAKE-4, body in ONE process, single read, 2 sizes x150, under load | 1/300 runs (earlier sample: 2/40) | residual after the poll: 0 (waited 1 or 3 pauses when needed, never the 40) |

The pytest-level counts are small because the events are rare; do not read "0/50" as proof. What carries the claim is the diagnosis (the `set_focus(None)` trace for FLAKE-1, the fractional `scroll_y` and pauses-needed histogram for FLAKE-4) and the mutants.

Mutants:

| # | Mutant | Result |
|---|---|---|
| M1 | FLAKE-1 test, poll removed (single pause read, as on the base), with the park delayed by k extra `call_after_refresh` hops (a deterministic version of the race; harness outside the repo) | single-pause read FAILED 9/10, 4/10, 3/10, 4/10 for k = 1, 2, 3, 5; the poll version FAILED 0/10 at every k. The poll is what the test relies on |
| M2 | FLAKE-4 test, `_until_visible` with `tries=0` (single read) | measured failure-rate comparison only (no deterministic delay hook for the grid animation was added): 1/100 against 0/100 for the fixed test, and 1/300 vs 0 residual in the harness. Declared: this is a rate, not a kill |
| M3 | `groups_for_keybar`: scope taken from the first group (`scope = GROUP_SCOPE[active_groups[0]]`) | KILLED by the new arm alone (1 failed; `tests/test_keymap.py` and `tests/test_en9.py` otherwise 119 passed). `['plug', 'app']` alone would NOT kill it, which is why the arm carries the app-first order. File restored from a byte copy |

## 5. Test results

- Ruff: `ruff check .` base `9a2d1c7` 26, head 26, programmatic multiset difference over (path, code, message) EMPTY.
- `-W error::SyntaxWarning`: the four touched `.py` files compile clean.
- Full default lane x3 (sequential, uninterrupted, `-rf`, the last step): see the section appended below.

## 6. Risks, unmeasured, next

- Both fixes are tests only; no product behaviour changed. The bounded polls cost nothing on the fast path (zero extra pauses when the state is already right).
- `FLAKE-1`'s poll waits for `app.focused is None`. If a future change makes the arrival park stop running, the first poll times out after 40 pauses and the test then fails on its unchanged assertion, which is the intended behaviour.
- NOT measured: a deterministic delay for the FLAKE-4 grid animation (M2 is a rate); the fixed tests on a quiet machine beyond the runs above; POSIX.
- The load was shared with other agents' work and varied during the session; the before/after rows were not taken in one controlled interleaving.
- Suggested next: the whole-branch gates the closure block lists.

## 7. Full default lane x3 (last step)

On `c2cafec` (all code and tests; this docs commit follows), sequential, uninterrupted, nothing else of mine running, `python -B -W error::SyntaxWarning -m pytest -q -rf -p no:cacheprovider`, temp HOME and USERPROFILE, git identity from environment variables, default basetemp:

| Run | Result | Time |
|---|---|---|
| 1 | `2769 passed, 24 deselected, 3 xfailed` (0 failed), exit 0 | 1363.28 s |
| 2 | `2769 passed, 24 deselected, 3 xfailed` (0 failed), exit 0 | 1441.14 s |
| 3 | `2769 passed, 24 deselected, 3 xfailed` (0 failed), exit 0 | 1389.01 s |

Baseline 2768; the +1 is the new `EN9-REV-F3` arm. Other agents' work (reviewers in their own worktrees) shared the machine, so the timings vary. No lane was discarded.
