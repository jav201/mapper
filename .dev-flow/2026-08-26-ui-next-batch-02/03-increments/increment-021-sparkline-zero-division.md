# Increment 021 · Sparkline zero-division micro-increment · 2026-09-28

Fixes `INC7-CR-R3-F3` (HIGH, pre-existing product defect), the finding the
round-3 reviewer routed to the operator rather than to a further `Inc-7`
corrective pass (`increment-020-inc7-corrective-2.md`'s "Round 3" section;
`state.json`'s `p3_progress.NEW_FINDING_ROUTED_TO_OPERATOR`). Base HEAD
`b529b34` on `feat/ui-next-batch-02`, tree clean before starting
(`git status --porcelain` = 0 lines). Commits: `54f1cfc` (requirement),
`bc0ba0a` (fix + tests), this record.

## The requirement, first

No requirement stated what the 14-day activity sparkline paints when the
workspace has zero activity in the window. Added `A-105`
(`01-requirements.md`, appended after `A-104`), traced to `HLR-N13.3` via
`LLR-N13.1.6` (whose touched-symbols line already named
`HomeScreen._sparkline_text`). States the testable behaviour (all 14 bars at
the floor glyph on zero activity, no exception; exactly the last bar at the
maximum tier on activity today), the touched symbol, validation method,
numeric pass thresholds, and explicitly that the behaviour is
date-independent -- naming `tests/test_agree_floor.py`'s own pre-existing
hermeticity defect as the reason this had to be said explicitly (its result
depends on the repository's file dates; that is what let this crash escape
until the fixtures' mtimes drifted past 14 days). Also states, to head off
scope creep, that the amendment does not touch or license touching the
`14 x N_maps` glob-and-stat loop above the guard -- that cost is
`LLR-N13.1.6`'s own open clause, unrelated to this defect.

## The defect

`HomeScreen._sparkline_text` (`app.py:561-583`) computed
`max_count = max(counts) if counts else 1`. `counts` always has 14 entries
(one per day), so the `else 1` branch can never fire. When every entry is `0`
-- no `.mmd` in the workspace modified in the last 14 days -- `max_count` is
`0`, and `c / max_count` (`app.py:579`) raised `ZeroDivisionError`, crashing
the home screen for any workspace idle two weeks or more.

## Regression first (escaped-bug rule), RED on base

Wrote `tests/test_sparkline_floor.py` before touching `app.py`, ran it
against the unfixed code:

```
tests/test_sparkline_floor.py::test_a105_a_zero_activity_workspace_paints_every_bar_at_the_floor FAILED
tests/test_sparkline_floor.py::test_a105_activity_today_lights_exactly_the_last_bar PASSED
1 failed, 1 passed in 0.25s
```

Exact failure:

```
    idx = min(len(bars) - 1, int(c / max_count * (len(bars) - 1)))
E   ZeroDivisionError: division by zero
mapper\app.py:579: ZeroDivisionError
```

The fixture builds a workspace with one `.mmd` whose mtime is set to 20 days
before *now* via `os.utime` (`_touch`, `tests/test_sparkline_floor.py:32`) --
relative to `date.today()` at test time, not to a fixed calendar date, so this
reproduces deterministically on any date. Drives `HomeScreen()._sparkline_text(store)`
directly (confirmed a bare `HomeScreen()` instance needs no mounted app for
this method: it touches only its `store` argument and the module-level
`darkside` helpers).

The complementary arm
(`test_a105_activity_today_lights_exactly_the_last_bar`) already passed on
the unfixed code, as expected: with one map modified today, `max(counts) == 1`
is nonzero, so the base code's own `max_count` computation does not crash on
that fixture. Its role is not to catch the crash -- it is the "did not
flatten real activity" control, and it is caught by mutant 2 below.

## The fix

`mapper/app.py`, one added line plus a comment naming the amendment id:

```python
        max_count = max(counts) if counts else 1
        # `A-105` -- `counts` always has 14 entries, so the `else 1` branch
        # above never fires; when every entry is 0 (no `.mmd` modified in the
        # 14-day window) `max_count` is 0, and `c / max_count` below must not
        # divide by it.
        max_count = max_count or 1
        bars = "▁▂▂▃▃▄▅▆▇█"
```

The `14 x N_maps` glob loop above it and the style tiers below it
(`darkside.WORDMARK` / `darkside.MUT` split at `idx < 4`) are untouched --
`LLR-N13.1.6`'s glob-cost clause is `A-105`'s explicitly named carry, not this
pass's scope.

Re-run after the fix:

```
tests/test_sparkline_floor.py::test_a105_a_zero_activity_workspace_paints_every_bar_at_the_floor PASSED
tests/test_sparkline_floor.py::test_a105_activity_today_lights_exactly_the_last_bar PASSED
2 passed in 0.14s
```

## Hermeticity of `tests/test_agree_floor.py` -- decided from evidence

**Decision: (a).** Once the product crash is fixed, `test_agree_floor.py`'s 8
arms pass on any date -- their assertions (outline/radial canvas vs. strip
declaration agreement) never read activity counts; `HomeScreen` mounting only
incidentally crashed as a shared symptom of the same defect. No mtime pinning
added to that file.

Proved rather than asserted, both runs at the fixed code:

- **Main working tree** (preserved mtimes; newest fixture `truncado.mmd` is
  2026-09-11, 17 days before today, i.e. past the 14-day window and squarely
  the condition that used to crash):

  ```
  tests/test_agree_floor.py .......... [100%]
  8 passed in 76.05s
  ```

- **Fresh `git worktree`**, created detached at HEAD `b529b34` outside the
  repo (`/tmp/mapper-worktrees/hermeticity-check`, path is outside this
  repo's own worktree tree; the pre-existing `basewt` worktree was never
  touched), with the fix and the new test file copied in (mtimes on checkout
  = 2026-09-28, today, confirmed by stat before running):

  ```
  tests/test_agree_floor.py tests/test_sparkline_floor.py
  .......... [100%]
  10 passed in 76.51s
  ```

  Removed afterward: `git worktree remove /tmp/mapper-worktrees/hermeticity-check --force`;
  `git worktree list` confirms only the main tree and `basewt` remain.

Both green, on fixture sets 17 days apart in age -- the suite's own defect
(checked-in `.mmd` files with fixed mtimes making its *own* verdict
date-sensitive) is unchanged and undischarged by this pass, but it no longer
matters for `test_agree_floor.py`'s specific 8 arms because the crash that
exposed it is gone. `A-105`'s amendment names this distinction explicitly so
it is not re-derived by hand later.

## Mutation proof

Mutation discipline: sha256 pinned before each mutation, byte-level
read/write (the file is CRLF; the anchor strings account for `\r\n`),
`tests/test_sparkline_floor.py` run and the verdict printed **before**
restoring, byte-level restore, sha256 re-verified against the pin.
`git status --porcelain` showed only the intended diff throughout each
mutation window.

| # | Mutant | File : sha256 pin | Test run | Verdict | Restored, sha ok |
|---|---|---|---|---|---|
| 1 | The escaped bug returns: guard removed, reverting `max_count = max_count or 1` back to bare `max_count = max(counts) if counts else 1` | `mapper/app.py` : `ba31b9277d4655a4cd5ea5f75f42ea0561195c0ec36d993f64ff07a380fd8f03` | `tests/test_sparkline_floor.py` | **RED on the zero-activity arm, GREEN on the complementary arm** -- `1 failed, 1 passed`; failure: `ZeroDivisionError: division by zero` at `app.py:579`, identical to the pre-fix RED capture above | yes -- mutant sha `e14c8d77bb63628b37a4eb4624114ea566e8b80356266fb21f65c54751ab28eb` (incidentally identical to `mapper/app.py`'s pin in `increment-020`, confirming `app.py` was untouched between `0c4215a` and `b529b34`), restored sha matched `ba31b927...` |
| 2 | The guard over-corrects: `idx = min(len(bars) - 1, int(c / max_count * (len(bars) - 1)))` replaced with `idx = 0` (every bar forced to the floor, regardless of real activity) | `mapper/app.py` : `ba31b9277d4655a4cd5ea5f75f42ea0561195c0ec36d993f64ff07a380fd8f03` | `tests/test_sparkline_floor.py` | **RED on the complementary arm, GREEN on the zero-activity arm** -- `1 failed, 1 passed`; failure: `assert '▁▁▁▁▁▁▁▁▁▁▁▁▁▁' == '▁▁▁▁▁▁▁▁▁▁▁▁▁█'` -- today's map was flattened to the floor instead of lighting the last bar | yes -- mutant sha `9931cc70fc95fcc1187feb02503015cdd4acd14481ee56a2aa60689ae4123dca`, restored sha matched `ba31b927...` |

Mutant 1 and mutant 2 are deliberately complementary: mutant 1 (the crash
class) does not redden the complementary arm, because that arm's fixture has
real activity (`max(counts) == 1`, nonzero) and the base code never crashed
on a nonzero max -- only on an all-zero one. Mutant 2 (an over-broad "fix"
that floors everything) does not redden the zero-activity arm, because both
the correct fix and this mutant produce all-floor bars when there is no
activity. Each new arm has exactly one mutant here that kills it and not the
other, which is the intended, non-redundant pairing rather than a gap.

Full pins: `mapper/app.py` fixed state =
`ba31b9277d4655a4cd5ea5f75f42ea0561195c0ec36d993f64ff07a380fd8f03`.

## Tests run

Targeted:

```
tests/test_sparkline_floor.py tests/test_agree_floor.py tests/test_repair_cycles.py tests/test_app.py
56 passed in 87.66s
```

Full default lane, once, in the main working tree (`tests/test_sparkline_floor.py`
staged with `git add` first -- `test_a3_census.py`'s
`test_tc_a3_no_source_file_is_invisible_to_the_census` correctly reddened on
the first attempt while the new test file was untracked; re-run green after
staging, which is the gate behaving as documented, not a product defect):

```
1170 passed, 20 deselected, 3 xfailed in 380.11s (0:06:20)
```

Zero failures. `FLAKE-1`
(`test_llr_cnv_3_1_the_parent_walk_maps_a_nested_widget_to_its_region`,
`assert '' == 'inspector'`) did not fire this run. The count reconciles
exactly against `increment-020`'s last full-lane figure at this same HEAD
(`8 failed, 1160 passed` -- all 8 failures were `test_agree_floor.py`'s
`ZeroDivisionError` arms): `1160 + 8 (now passing) + 2 (new arms) = 1170`.

## Ruff

Baseline re-captured on unmodified HEAD `b529b34` (`git stash -u`, run, `git
stash pop`) rather than trusted from `increment-020`'s record: **27 distinct
errors, 29 output lines** (`ruff check --output-format=concise`) -- identical
to the prior baseline, confirming no drift between `0c4215a` and `b529b34`.

After this pass's changes: `diff` against that same-session baseline capture
is **empty**. Zero new errors, identical 27-error set.

## Files modified

- `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md` -- `A-105`
  appended.
- `mapper/app.py` -- one guard line (plus a 4-line comment) added at
  `_sparkline_text`'s `max_count` computation.
- `tests/test_sparkline_floor.py` -- new file, two arms (the escaped-bug
  regression and its complementary no-flatten control).
- `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-021-sparkline-zero-division.md`
  -- this record.

Four files, within the 5-file cap this micro-increment declared
(`mapper/app.py`, one test file, `01-requirements.md`, the increment record).
`.dev-flow/state.json` was not touched -- the coordinator updates it.

## Carries left open (not touched by this pass)

- **`LLR-N13.1.6`'s glob-cost clause** -- the `14 x N_maps` glob-and-stat loop
  in `_sparkline_text` (`app.py:565-574`) is untouched; its own numeric pass
  threshold (`glob` calls per mount `<= 2`) remains open. Named explicitly in
  `A-105` as out of this amendment's scope.
- **`tests/test_agree_floor.py`'s own hermeticity defect** -- its fixtures are
  checked-in `.mmd` files with fixed mtimes, so its *own* result is still
  date-sensitive in principle (this pass proved its 8 arms are unaffected in
  practice, post-fix, at two mtime ages 17 days apart, but did not pin its
  fixtures). Not fixed here -- option (a) was chosen and proved sufficient;
  see "Hermeticity", above.
- All carries already open at `increment-020` (`INC7-CR-R2-F2`,
  `INC7-CR-R2-F3`, `INC7-SEC-R2-F1/F2/F3`, the `table.clear()` routing item)
  are unchanged and untouched by this pass.
- No new `MICRO-SPARK-Fn` finding surfaced.

## Independent review

**PASS, no HIGH findings.** The reviewer reproduced RED on base and GREEN on
fix independently, and the two killing mutants they ran (guard removed;
division-by-`max_count` forced back unguarded) matched this increment's own
mutant table. Six non-blocking findings (`INC21-CR-F1` through
`INC21-CR-F6`) were folded in before `Inc-8` rather than deferred, because
`F1` leaves an `A-105` clause ("shall not flatten real activity") without an
arm that actually tests it -- an overclaim under this batch's rules, not a
nit.

## Review round (`INC21-CR-F1` through `F6`)

| Finding | Severity | Disposition |
|---|---|---|
| `INC21-CR-F1` | MEDIUM | **FIXED.** New arm `test_a105_two_days_of_activity_scale_relative_to_each_other` (two maps 3 days ago, one today); see below for the by-hand derivation and the `M6`/`M7` mutant kills. |
| `INC21-CR-F2` | LOW | **FIXED.** The `app.py` guard comment now reads `A-105` / `INC7-CR-R3-F3`. `A-105`'s Validation line now names all three arm functions by name, not just the file. |
| `INC21-CR-F3` | LOW | **FIXED -- race removed, not bounded.** Chose the second option offered: `_touch` now sets local noon of an explicit `date`, and every TODAY-dependent arm re-reads `date.today()` immediately after computing its bars and `pytest.skip`s if it moved. `A-105` states this choice explicitly (its own `INC21-CR-F3` paragraph). |
| `INC21-CR-F4` | LOW | **CARRIED to `qa-reviewer`, not fixed.** `A-105` now names the gap explicitly (style-tier pinning, `app.py:586`) as its own `INC21-CR-F4` paragraph, out of this amendment's scope. |
| `INC21-CR-F5` | LOW | **FIXED (documentation).** `A-105` states, as its own `INC21-CR-F5` paragraph, that `test_agree_floor.py` exercises the zero-activity path only incidentally (stale checked-in fixtures) and that the screen-level "shall not raise" clause rests on the first `test_sparkline_floor.py` arm, not on `test_agree_floor.py`. |
| `INC21-CR-F6` | LOW | **FIXED, folded into `F3`'s fix.** `_touch` no longer uses `time.time() - N * 86400`; it takes a `date` and computes `datetime.combine(day, time(12))`. The prose ("mtimes relative to `date.today()`") and the code now agree because the code literally consumes `date` objects built from `date.today()`, not because the prose was reworded to match a `time.time()` implementation. |

### `INC21-CR-F1`'s new arm, derived by hand

`test_a105_two_days_of_activity_scale_relative_to_each_other`: two maps
modified 3 days ago (count 2 that day), one map modified today (count 1).
Correct `max_count = max(counts) = 2`. Against `bars = "▁▂▂▃▃▄▅▆▇█"`
(`app.py:581`) and `idx = min(9, int(c / max_count * 9))` (`app.py:584`):

- today: `c=1, max_count=2` -> `idx = int(1/2*9) = int(4.5) = 4` -> `bars[4] = "▃"`
- 3 days ago: `c=2, max_count=2` -> `idx = int(2/2*9) = int(9.0) = 9` -> `bars[9] = "█"`
- every other day: `c=0` -> `idx=0` -> `bars[0] = "▁"`

In the 14-character output, today is the last character (index `-1`) and 3
days ago is 3 positions earlier (index `-4`) -- exactly the `bars[-4] ==
"█"`, `bars[-1] == "▃"` the coordinator specified; derived independently here
against the real formula before running anything, then confirmed by the
passing test.

### Mutation proof (`INC21-CR-F1`)

Same discipline as the first mutation table: sha256 pinned before each
mutation, byte-level read/write, `tests/test_sparkline_floor.py` run and the
verdict printed **before** restoring, byte-level restore, sha256
re-verified. `git status --porcelain` showed only the intended diff
throughout.

| # | Mutant | File : sha256 pin | Test run | Verdict | Restored, sha ok |
|---|---|---|---|---|---|
| M6 | `max_count = max(counts) if counts else 1` + the guard collapsed to `max_count = max(1, sum(counts))` | `mapper/app.py` : `aea69e4ffb19f0c8a733108063a465b81a29be3a24123999a9fca4e5d4b7878d` | `tests/test_sparkline_floor.py` | **RED on the new two-day arm, GREEN on the other two** -- `1 failed, 2 passed`; `sum(counts) = 3`, so `bars[-4]` came out `"▅"` (idx 5) instead of `"█"` | yes -- mutant sha `21cd3d1dbea4279e4d32c11e5f34831de96e49d94df626502d007c41b0dbce19`, restored sha matched the pin |
| M7 | `idx = min(len(bars) - 1, int(c / max_count * (len(bars) - 1)))` replaced with the binary tier `idx = 9 if c else 0` | `mapper/app.py` : `aea69e4ffb19f0c8a733108063a465b81a29be3a24123999a9fca4e5d4b7878d` | `tests/test_sparkline_floor.py` | **RED on the new two-day arm, GREEN on the other two** -- `1 failed, 2 passed`; today's bar came out `"█"` (idx 9, since `c=1` is truthy) instead of `"▃"` | yes -- mutant sha `a622fc55dbf183975a060714f32f35c7badd47bbd107fcfce438115fc3630b43`, restored sha matched the pin |

Neither `M6` nor `M7` reddens the first two arms -- expected and consistent
with `INC21-CR-F1`'s own diagnosis: both of those arms put activity on
exactly one day, where the true maximum, the true sum, and "any activity"
are numerically identical, so a wrong denominator or a wrong tiering scheme
is invisible to them. The two-day arm is what makes `M6` and `M7`
observable.

### Verification after the review round

Targeted only, per the coordinator's constraint (a test + comment + docs
change does not need the full lane):

```
tests/test_sparkline_floor.py tests/test_agree_floor.py
11 passed in 77.53s
```

Ruff: re-diffed against the same unmodified-HEAD baseline captured for the
first pass of this increment (`git stash -u`, run, `git stash pop` --
27 errors / 29 lines). `diff` is **empty** again after the review round's
changes. Zero new errors, identical set.

`mapper/app.py`'s diff versus `bc0ba0a` (this increment's first fix commit)
is comment-only: the guard line and its logic are untouched; only the
comment above it gained `/ INC7-CR-R3-F3`.
