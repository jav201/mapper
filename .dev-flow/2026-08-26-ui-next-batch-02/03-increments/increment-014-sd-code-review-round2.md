# Increment 014 — Inc-REPAIR S-D — Independent Code Review, ROUND 2

**Reviewer:** `code-reviewer` (independent of the author)
**Date:** 2026-09-18
**Repo/branch:** `C:\Users\jjgh8\Github\mapper` · `feat/ui-next-batch-02` · base `2f78ecc` · still uncommitted
**Round-1 verdict:** BLOCKED · `BLOCK-UNTIL: F1, F2`
**Predecessor:** `increment-014-sd-code-review.md`

## Verdict

> **APPROVED WITH FINDINGS.**
>
> **`BLOCK-UNTIL: F1, F2` is DISCHARGED** — by re-reading the diff and re-driving both
> defects on my own instruments, not by the corrective pass's report.
>
> Four findings remain, all **LOW**, none blocking. **R2-1** is the one I would take:
> `M5` survived, so F5's raise is the only new branch the suite cannot see — and this
> module already pins exactly that property for its sibling seam.

Nothing below is inherited. Every figure in the request was re-derived here, and the
two I could not re-derive are named in the Boundary statement.

## Scope reviewed

`git diff` against `2f78ecc` — 578 insertions / 63 deletions over 7 files. Round-2 delta
read in full: `PAN_INERT_HINT` (`app.py:80-97`), `_consumes_pan` (`app.py:1636-1682`),
`_reclamp_pan` (`app.py:1684-1712`), `_pan`'s inert branch (`app.py:1715-1725`), both
toggle actions + `_clear_pan_hint` (`app.py:3307-3351`), the five new arms
(`tests/test_pan.py:489-646`), the F4 deletion and its replacement prose
(`tests/test_canvas_header_charge.py:104-155`), `HintLine.text`/`set_hint`
(`mapper/widgets/chrome.py:141-159`).

---

## Round-1 findings — disposition

### F1 (HIGH) — pan discarded on a view excursion · **CLOSED** · `executed`

`_reclamp_pan`'s non-consumer branch now `return`s and the zeroing is gone
(`app.py:1710-1711`).

Re-driven on **my own** round-1 instrument, unchanged — `cr_sd_probe3c.py`, the `grande`
workspace (61 nodes, layered pan genuinely moves), guarded on `layered_moves > 0`, at
118x34 and 80x24:

| | Round 1 | **Round 2** |
|---|---|---|
| `on_entering_outline` | `(0, 0)` | **`(48, 0)`** |
| `back_in_layered` | `(0, 0)` | **`(48, 0)`** |
| `ROUND_TRIP_PRESERVED` | False | **True** |
| radial leg, **no key pressed** | `(0, 0)` — False | **`(48, 0)` — True** |
| `outline_after_pan_key` | inert | **still inert `(48, 0)`** |

The lying affordance stays dead while the state survives. Both properties hold at once,
as the round-1 fix-check predicted.

### F2 (HIGH) — PAN-1 unpinned · **CLOSED** · `executed`

**The round-1 mutant is dead.** `M1-CONSUMES-ALL` (`_consumes_pan` → everything pans),
which **SURVIVED at 1096** in round 1, is now **KILLED — 3 failed**.

### F3 (MED) — the inert hint latched · **CLOSED** · `executed`

`cr_sd_probe5.py`, guarded on `GUARD_pan_is_live_in_layered == True`, both sizes:

```
hint_in_radial               'siguiente ▸ esta vista no se desplaza · navega con j/k/h/l'
hint_back_in_layered_no_key  'siguiente ▸ '
LATCHES_A_FALSE_STATEMENT    False        (round 1: True)
hint_after_nav               'siguiente ▸ '
```

The clear survives `refresh_canvas`, which runs after it in both toggle actions — checked
by measurement, not by reading the call order.

### F4 (MED) — the arm that could not fail on its own subject · **CLOSED, deleted** · `executed`

Gone; the 7-of-10 table survives as prose at `tests/test_canvas_header_charge.py:104-121`,
including why it was the wrong instrument. Confirmed by the collected-count derivation
below: `test_canvas_header_charge.py` is **+5** over HEAD, which is the residue arm going
from 5 parametrizations to 10 and the F4 arm contributing **zero**.

### F5 (MED) — `_consumes_pan` fell through to `False` · **CLOSED in code, UNPINNED** · `executed`

Now enumerates all three renderers and raises `LookupError`, mirroring the siblings
verbatim. Correct — **and the suite cannot see it**. See **R2-1**.

### F6 (LOW) — hint register · **CLOSED** · `executed`

`PAN_INERT_HINT = "esta vista no se desplaza · navega con j/k/h/l"`, declared once as a
module constant so the setter and the clearer cannot drift. Refusal paired with the next
move, matching the strip's house pattern. See **R2-4** for one measured consequence.

### F7 (LOW/process) — recorded. `n/a — no code owed`.

---

## Round-1 claims I re-derived

**The A3 census is back to exactly 34 and `argful` is still 62. CONFIRMED.**
`cr_sd_probe4b.py`, running `test_a3_census.render_call_sites()` — the pins' own
derivation — against a detached `2f78ecc` worktree and the working tree:

```
zeroarg: HEAD=32  NOW=34  delta=+2
  tests/test_agree_floor.py: 2 -> 4     (only file that moved)
    NOW tests/test_agree_floor.py:194, :195
argful:  HEAD=62  NOW=62  delta=0
```

**No `mapper/` file changed its zero-arg site count**, which is the specific check your
question needs: the first `_clear_pan_hint` added a *production* widget render and the
pins caught it; the `HintLine.text` version adds none. The pins did their job and the
repair is real.

**Lanes and lint.**

| | Measured by me |
|---|---|
| default | **1094 passed / 19 deselected / 3 xfailed**, exit 0, 340 s |
| slow | **19 passed**, 1097 deselected, 52 s *(round-1 boundary item, now closed)* |
| `ruff check .` | **27** — identical to `2f78ecc` in a detached worktree |
| ruff, the 6 S-D files | 1 — `mapper/app.py:5 F401 're'`, pre-existing, untouched |
| `FLAKE-2` | did not fire in either lane. `n/a — not reproduced here` |

**The ledger, derived mechanically from the base rather than from round 1.** Your
`1096 − 7 + 5 = 1094` is right, and here is the stronger form — per-file collected
counts, `2f78ecc` → now:

```
tests/test_agree_floor.py           4 -> 8   (+4)   two radial arms x two map_ids
tests/test_canvas_header_charge.py 37 -> 42  (+5)   residue arm 5 -> 10 params; F4 arm = 0
tests/test_pan.py                  20 -> 25  (+5)   the five PAN-1 instances
HEAD collected 1083  ->  NOW collected 1097
```

1083 = 1080 passed + 3 xfailed, the batch's recorded base figure. 1097 = 1094 + 3
xfailed. **1080 + 14 = 1094**, and the 14 decomposes per file. The ledger reconciles end
to end from the base, not only relative to round 1.

---

## The three things you asked me to attack

### (1) Can each arm fail for the reason its name gives? — YES, and the attribution is clean · `executed`

You ran three mutants but not per arm. I ran five and recorded **which node ids fired**
(`C:\Users\jjgh8\clde\cr_sd_r2_battery.py`; scope: `test_pan.py`,
`test_canvas_header_charge.py`, `test_agree_floor.py`, `test_a3_census.py`):

| Mutant | Verdict | Arms that fired |
|---|---|---|
| **M1** `_consumes_pan` → everything pans | **KILLED** 3 failed | `inert_AND_DECLARED[outline]`, `[radial]`, `the_inert_hint_does_not_LATCH` |
| **M2** restore the F1 zeroing | **KILLED** 2 failed | `view_excursion_does_not_DISCARD[outline]`, `[radial]` — **and nothing else** |
| **M3** drop both `_clear_pan_hint()` calls | **KILLED** 1 failed | `the_inert_hint_does_not_LATCH` — **and nothing else** |
| **M4** inert but SILENT (drop the `set_hint`) | **KILLED** 3 failed | `inert_AND_DECLARED[outline]`, `[radial]`, `the_inert_hint_does_not_LATCH` |
| **M5** F5 revert: raise → `return False` | ***SURVIVED*** 90 passed | — |

Reading it:

- **The excursion arm is exclusively sensitive to F1's defect.** M2 kills it and nothing
  else; no other mutant touches it. Named correctly, fires only for its reason.
- **The latch arm is exclusively sensitive to F3's defect** — M3 kills it alone.
- **Both halves of "inert AND declared" are pinned separately**: M1 kills it on the
  offsets moving, M4 on the declaration vanishing. Neither half rides on the other.
- **The latch arm also fires under M1 and M4, and that is the arm working, not
  mis-attribution.** Its first assertion is a precondition guard — *"the hint never
  appeared, so this arm cannot show it failing to clear"* — and under M1/M4 the hint
  never appears. **It refuses to report vacuously instead of passing.** That is the
  property round 1 said the suite lacked, and it is the best thing in this diff.
- No arm is redundant. Every arm has a mutant it uniquely kills.

`M4` is a mutant you did not run and it matters: without it, "the key is inert" could
have been pinned while "and it says so" was not.

Discipline: byte-level I/O, CRLF-normalised anchors asserted at an **exact expected
count** (M3's is `== 2`, both toggle seams; a mismatch prints `BAD`, never `SURVIVED`),
verdicts printed before the restore assert, `PYTHONDONTWRITEBYTECODE=1`, `__pycache__`
purged both sides, sha256 restore verified
(`149cc8b5c0b535bd043f2e9a9bf62de2eda0c2c72891fac92cbd6a0c5fc1fab8` in and out).

### (2) Is `_clear_pan_hint`'s exact match too brittle? — NO. Keep it. · `executed`

It equality-tests a value that **exactly one site writes, from the same module
constant**. That is the tightest correct scope, it satisfies `DECL-118-TWICE`, and it is
what makes the clear unable to swallow another handler's declaration — the property your
docstring claims and the reason a `startswith` or a substring test would be worse.

The alternative — a boolean flag set beside the `set_hint` — is a **second spelling of
the same fact**, which is the shape `DECL-118-TWICE` exists to refuse. It would also add
screen state whose only job is to describe other screen state.

I checked for a real composer: `_hint_with_opened(...)` at `app.py:3236` composes onto
the *search* hint, and nothing anywhere composes onto the pan hint. So the brittleness is
hypothetical today.

**The one condition under which it needs revisiting**, recorded so the next reader does
not re-derive it: if a handler ever composes onto `PAN_INERT_HINT`, the equality silently
stops matching, the hint latches again, **and the latch arm stays green** because it
drives the plain path. Whoever adds such a composition owns moving the clear.

### (3) Is holding right when the GRAPH CHANGES underneath? — YES, and I constructed it · `executed`

**My first attempt at this was green by construction and I threw it away.**
`cr_sd_r2_probe6.py` folded a branch and resized, reported `IN_RANGE_ON_RETURN=True`
everywhere — but the held pan was 320 and the post-mutation legal max never fell below
459, so the assertion could not fail. That is the `C-31` failure I flagged in round 1,
reproduced in my own instrument.

`cr_sd_r2_probe7.py` replaces it, **guarded on `new_max < held_pan`** and refusing to
report otherwise, with mutations violent enough to collapse the extent. Park in outline
at the far edge, change the world, come back:

| Case @ size | held | new legal max | on return | in range |
|---|---|---|---|---|
| `action_toggle_focus` @118x34 | 480 | 0 | **0** | ✔ |
| resize to 600x40 @118x34 | 480 | **35** | **35** | ✔ |
| graph replaced by a 2-node graph @118x34 | 480 | 0 | **0** | ✔ |
| all three @80x24 | 480 | 0 | **0** | ✔ |

Six configurations, the guard biting in all six. The `600x40` row is the informative one:
480 clamped to **exactly the new maximum, 35** — a real clamp, not a reset to zero. The
frame has content and `app.is_running` is True in every case.

**The mechanism is `refresh_canvas`'s ordering**, and it is load-bearing:
`_reclamp_pan` → `_view_state` → `render`, with the state **captured** after the
reclamp. So the first layered frame after the return already carries a legal offset;
**no out-of-range offset ever reaches a painted frame.**

**One judgement worth recording rather than filing.** *During* the excursion the held
offset is out of range for the new world (480 while the max is 0). Read literally,
`LLR-N06.1.2` says the system shall not ACCEPT an offset outside the range. I read
holding as compliant: no non-consuming renderer reads the offsets, they are part of no
frame, and the first consuming frame clamps them. The alternative reading demands
zeroing, which is F1. The tradeoff is real and the increment picked the right side of it —
but it is a reading, so it is written down here rather than left implicit.

---

## Remaining findings

### R2-1 — F5's raise is the only new branch the suite cannot see · **LOW** · `executed`

`M5` (raise → `return False`, the exact F5 revert) **SURVIVED**: 90 passed, exit 0.

This is a **convention gap, not an oversight of mine to hand-wave**: this module already
pins precisely this property for the sibling seam —
`tests/test_canvas_header_charge.py:199`,
`test_an_unregistered_renderer_RAISES_rather_than_defaulting`, which is
`with pytest.raises(LookupError): screen._header_rows_for(object())` and nothing more.

**Suggested fix** — one arm, beside the five:

```python
def test_pan1_an_unregistered_renderer_RAISES_rather_than_defaulting():
    """`False` is a legitimate answer here, so it may not double as
    "I have never heard of this renderer" (`A-98`, ruling `02j`)."""
    screen = _screen()
    with pytest.raises(LookupError):
        screen._consumes_pan(object())
```

Not blocking: the branch is correct, and it guards a renderer that does not exist.

### R2-2 — `_consumes_pan` is the only one of the three dispatches whose raise reaches an UNGUARDED path · **LOW** · `executed`

For whoever adds a fourth renderer, recorded so it is not re-derived:

- `_painted_ids_for`'s raise is reached from `refresh_canvas`, inside its guard.
- `_header_rows_for`'s raise is **deliberately** softened in the drawing path —
  `test_the_header_rows_METHOD_routes_through_the_dispatch` pins that `_header_rows`
  falls back to layered's charge rather than raising, on the measured argument that
  *"a declaration that raises costs a numeral; a charge that raises costs the whole
  picture."*
- `_consumes_pan` is called from **`_pan`, before its `try`** (`app.py:1723`). An
  unregistered renderer plus one pan keypress escapes into the message pump — the exact
  sink `_pan`'s own `except` exists for, which records that an escape there took
  `app.is_running` to False.

The honest counter-argument, which is why this is LOW and not MEDIUM: an unregistered
renderer **is** a code defect, and the batch's stated preference is to fail loud on one.
I am not asking for a change. I am asking that the asymmetry be a decision rather than an
accident, since the module next door measured its way to the opposite answer.

### R2-3 — two of the three arms bypass the operator's actual keys · **LOW** · `executed`

`test_pan1_a_pan_key_is_inert_AND_DECLARED...` and
`..._does_not_DISCARD_the_operators_pan` switch views by assigning `outline_mode` /
`radial_mode` and calling `refresh_canvas()` directly. The latch arm uses
`await pilot.press("r")` — the real path.

Consequence: if a future change moved the discard into `action_toggle_outline` /
`action_toggle_radial` rather than `_reclamp_pan`, the excursion arm would not see it —
and those two actions are exactly where `_clear_pan_hint` now lives, so they are actively
being edited. My own probes drove the toggle *actions* and confirm the behaviour holds
there, so this is a suite-shape gap, not a live defect.

**Suggested fix.** Have the excursion arm press `o` / `r` as the latch arm does. It costs
nothing and closes the gap.

Also in the same two arms: `setattr(screen, flag, True)` is **dead** — the next two lines
assign both flags unconditionally. Delete the line.

### R2-4 — the F6 wording wraps the single-line hint one column earlier than its longest sibling · **LOW / informational** · `executed`

My round-1 recommendation made the string longer, so I measured what it cost. First
width at which the composed hint fits on ONE row, through `darkside.hint_line`:

| hint | cells | fits on one row from |
|---|---|---|
| `borde del territorio` | 20 | 32 |
| `DEFAULT_MAP_HINT` | 39 | 51 |
| rail hint | 41 | **57** |
| **`PAN_INERT_HINT`** | 46 | **58** |

At w ≤ 50 it wraps to two rows in a widget documented as *"Single-line next-step hint"*,
and the operator sees `esta vista no se desplaza ·` with a dangling separator.

**This is not a new failure class** — it is one column worse than the rail hint, which
already wraps at 56 and ships. Reporting it because it is a consequence of *my* round-1
recommendation and you should have the number, not because I think it needs changing. If
the strip's narrow-width behaviour is ever taken up, this constant joins that work; it
does not lead it.

---

## Boundary statement

**What I saw.** The full round-2 diff; every seam it touches and the two sibling
dispatches it claims to mirror; `HintLine`'s implementation; both lanes executed here;
ruff on both trees; the A3 derivation and the collected-count ledger run against a
detached `2f78ecc`; five mutants with per-node attribution; and four probes, two of which
I rewrote after catching them asserting nothing.

**What I could not see — constructed before declaring, not asserted.**

1. **My independence on F1 is structurally weaker than on the rest, and I will not
   pretend otherwise.** The one-line fix now in the tree is the snippet I prescribed in
   round 1 and verified under my own harness then. My round-2 confirmation of it is
   therefore partly a confirmation of my own prescription. What makes F1 genuinely
   discharged is evidence I did **not** author: the excursion arm, written by
   `software-dev`, and `M2`'s kill, which fires that arm and nothing else. I am naming
   this rather than counting my own recommendation twice.
2. **`FLAKE-2` did not fire in either lane here.** Your `4 of 10` isolated rate remains
   yours; I neither reproduced nor challenged it. Both my green lanes carry the same
   qualification every figure in this batch carries.
3. **The `grande` workspace is mine and is not in the repo.** Every finding I raised
   across both rounds needed a map where layered pan genuinely moves. The suite now uses
   `pan_graph`, the repo's own pannable fixture — the right call, and better than my
   generated one, since it is the fixture the rest of `test_pan.py` already asserts
   overflows. I did not re-derive `pan_graph`'s `max_pan_x = 49`; the arms' own
   `_pan_is_live` guard is what protects them, and I read it.
4. **I did not exercise the narrow terminal band end to end.** R2-4 is a render-level
   measurement through `darkside.hint_line`, not a driven app at 40 columns. The
   distinction matters: I measured what Rich does to the string, not what the operator
   sees after the widget clips it.
5. **Security and functional-suite validation** remain `security-reviewer`'s and
   `qa-reviewer`'s. For `qa-reviewer`: round 1's warning that "the lane is green" was a
   weaker statement than it read **no longer applies to PAN-1** — four of the five
   mutants now die. It still applies to R2-1's single branch.

**The tree is exactly as I found it.** `git status --porcelain` shows the same 7 modified
files plus the two review artifacts (untracked); `mapper/app.py` sha256
`149cc8b5c0b535bd043f2e9a9bf62de2eda0c2c72891fac92cbd6a0c5fc1fab8` before and after the
battery; the comparison worktree was created detached and removed. You remain the single
writer.

---

## Evidence checklist

- [x] **Diff read in full** — ranges tabulated under *Scope reviewed*.
- [x] **Correctness pass** — F1/F3 re-driven on my instruments; the graph-changes-underneath
      case constructed with a biting guard; R2-2 (raise reaching an unguarded path) found
      by reading the two sibling call paths.
- [x] **Simplicity pass** — the F1 fix removes a line. `PAN_INERT_HINT` is a genuine
      two-site constant. `_clear_pan_hint` is 3 statements. No speculative generality;
      R2-3's `setattr` is the only dead code.
- [x] **Reuse / duplication** — `_consumes_pan` now mirrors both siblings exactly. The
      hint constant kills the only duplication the change could have introduced. The new
      arms reuse `pan_graph`, `_open_pan_map`, `_hint` and `CONTEXT_OF_USE` rather than
      minting a fixture — better than my own probes did.
- [x] **Tests verify intent** — per-arm mutation attribution above; every arm carries a
      positive control; the latch arm's precondition guard makes it refuse to report
      vacuously. R2-1 and R2-3 are the two remaining shape gaps.
- [x] **Verdict explicit** — **APPROVED WITH FINDINGS**; `BLOCK-UNTIL: F1, F2`
      **DISCHARGED** by re-reading the artifact; no HIGH open.

## Evidence states

| Item | State |
|---|---|
| F1 closed | `executed` — probe3c, guarded, 2 sizes, both views |
| F2 closed | `executed` — M1 KILLED 3 failed (SURVIVED in round 1) |
| F3 closed | `executed` — probe5, live-pan guard, 2 sizes |
| F4 closed | `executed` — collected-count derivation, +5 not +12 |
| F5 closed in code | `executed` — read against both siblings |
| F5 pinned | `failed` — **M5 SURVIVED**; see R2-1 |
| F6 closed | `executed` |
| Per-arm attribution (Q1) | `executed` — 5 mutants, node ids captured |
| `_clear_pan_hint` scope (Q2) | `executed` — single writer confirmed, no composer exists |
| Graph-changes-underneath (Q3) | `executed` — probe7, guard bites in 6/6 |
| probe6 | `failed` — vacuous, superseded by probe7, recorded not hidden |
| A3 census 34 / argful 62 | `executed` — pins' own derivation, both trees |
| Ledger 1080 + 14 = 1094 | `executed` — per-file collected counts |
| default lane | `executed` — 1094 / 19 / 3, exit 0 |
| slow lane | `executed` — 19 passed *(round-1 gap closed)* |
| ruff | `executed` — 27 now, 27 at base |
| `FLAKE-2` | `not-run` — `n/a — did not fire` |
| R2-2 unguarded raise | `executed` — by reading the three call paths |
| R2-3 arms bypass the keys | `executed` |
| R2-4 hint wrap width | `executed` — render-level only, see Boundary 4 |
| Security / functional suite | `n/a — other reviewers' lanes` |

## Probes

`C:\Users\jjgh8\clde\` — `cr_sd_probe3c.py`, `cr_sd_probe4b.py`, `cr_sd_probe5.py`
(round-1 instruments, re-run unchanged) · `cr_sd_r2_probe6.py` (**vacuous — kept as the
record**) · `cr_sd_r2_probe7.py` (guarded extent collapse) · `cr_sd_r2_battery.py`
(five mutants, per-arm attribution).
