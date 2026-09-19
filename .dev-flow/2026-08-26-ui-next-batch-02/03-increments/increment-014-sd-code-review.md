# Increment 014 — Inc-REPAIR S-D — Independent Code Review

**Reviewer:** `code-reviewer` (independent of the author)
**Date:** 2026-09-18
**Repo/branch:** `C:\Users\jjgh8\Github\mapper` · `feat/ui-next-batch-02` · base `2f78ecc`
**Scope:** the UNCOMMITTED working tree at review time.

## Verdict

> **BLOCKED — F1 and F2 are HIGH and OPEN.**
>
> Re-entry is governed by **`BLOCK-UNTIL: F1, F2`**, which authorises nothing. It is
> discharged only by me RE-READING the diff after the fixes land — not by the
> corrective pass reporting that it ran.

Two of the three workstreams are clean and, where I could falsify them, I failed to.
The third — **PAN-1** — ships an operator-visible **state-loss regression** and ships
**entirely unpinned**: I reverted its whole behavioural fix and the full default lane
stayed green at 1096.

## Scope reviewed

`git diff` against `2f78ecc`, read in full — 320 insertions / 61 deletions over 6 files:

| File | Range read |
|---|---|
| `mapper/views/radial.py` | +1 import; `_header_line` 107–120; `header_rows` 123–164; `_paint` 399–422 |
| `mapper/app.py` | imports 57–64; `_header_rows_for` 1534–1560; `_consumes_pan` 1617–1648; `_reclamp_pan` 1650–1669; `_pan` 1671–1714 |
| `tests/test_canvas_header_charge.py` | 101–200 (both rewritten arms + the new pin) |
| `tests/test_agree_floor.py` | 156–251 (`NARROW_SIZES`, `_radial_frame`, the radial arm, the outline control) |
| `tests/test_a3_census.py` | 254–275, 373–386 (both cardinality pins) |
| `.dev-flow/state.json` | the `FLAKE-2` block |

Everything below is `executed` unless marked otherwise. Nothing was inherited.

---

## Findings

### F1 — A view excursion silently DISCARDS the operator's pan · **HIGH** · `executed`

**What.** `_reclamp_pan`'s new non-consumer branch does not merely decline to clamp —
it **zeroes** `pan_x`/`pan_y`. `refresh_canvas` calls `_reclamp_pan` on every repaint,
so pressing `o` (or `r`) and then pressing it again throws the operator's pan position
away. **No key was pressed, nothing was declared, and the offsets do not come back.**

**Where.** `mapper/app.py:1662-1663`

```python
if not self._consumes_pan(self._current_renderer()):
    self.pan_x = self.pan_y = 0
    return
```

**How I constructed it.** My first attempt at this case was **worthless and said so**:
on `legacy`/`anidado` at 118x34 and 80x24 the round trip reported `PRESERVED=True` —
but `layered_moves` was **0** and pan never left `(0,0)`, so the probe could not tell
preserve from discard (`C-31`, input-set-as-oracle; the code's own comment at
`app.py:1710` already records that `H`/`L` are no-ops on the shipped maps at every
width but one). I built a workspace whose map genuinely pans and **guarded the probe
on `layered_moves > 0`**. Driven through the real screen actions, never a model.

`C:\Users\jjgh8\clde\cr_sd_probe3c.py`, `grande` (61 nodes), both 118x34 and 80x24 —
and the same probe run against a detached `2f78ecc` worktree for the before-picture:

| Step | HEAD `2f78ecc` | Working tree |
|---|---|---|
| pan in layered | `(48, 0)` | `(48, 0)` |
| enter outline | `(48, 0)` | **`(0, 0)`** |
| press `L` in outline | `(56, 0)` silently — **the PAN-1 defect** | `(48→0, 0)`, hint fires — defect cured |
| back in layered | `(56, 0)` | **`(0, 0)`** |
| radial round trip, **no key pressed** | `(48, 0)` — `PRESERVED True` | `(0, 0)` — **`PRESERVED False`** |

The radial row is the load-bearing one: **no pan key is pressed at all**, and the pan
is gone. This is not the lying affordance being fixed; it is new state loss the
increment introduced, on the path the increment's own ruling makes routine (radial is
for focus-based navigation — you go there and you come back).

**Why it matters.** It is the same family the increment exists to close, one seam over.
`PAN-1`'s charge is *"the app held a pan the picture never reflected."* This ships
*"the app discarded a pan the operator set, without saying so"* — and `AT-058`'s
doctrine, cited twice in this very diff, is **declare, never silently omit**.

**Suggested fix (verified, not proposed).** The zeroing is not required by the
docstring's own rationale — *"rather than clamped against an extent belonging to a
different renderer"* is satisfied by declining to clamp. Hold the offsets:

```python
if not self._consumes_pan(self._current_renderer()):
    return          # HOLD the offsets; the non-consumer ignores them, and
                    # `_reclamp_pan` clamps them honestly on the way back.
```

I applied exactly that one-line change under the mutation harness
(`C:\Users\jjgh8\clde\cr_sd_fixcheck.py`, sha-verified restore) and re-drove it:

- `ROUND_TRIP_PRESERVED` → **True**, `ROUND_TRIP_PRESERVED_RADIAL` → **True**, both sizes.
- `outline_after_pan_key` stays `(48, 0)` — **the lying affordance stays dead** and the
  hint still fires. The two properties are not in tension.
- `tests/test_pan.py test_overflow.py test_key_dispatch.py test_agree_floor.py
  test_canvas_header_charge.py` → **189 passed**, exit 0.

`software-dev` applies it; I do not.

---

### F2 — The whole PAN-1 workstream ships UNPINNED · **HIGH** · `executed`

**What.** The increment adds no test for any part of PAN-1. Mechanically:

- `grep -rn "_consumes_pan\|no se desplaza" tests/` → **zero hits**.
- `tests/test_pan.py` contains **no** `outline_mode` / `radial_mode` — pan is never
  driven in a non-layered view anywhere in the suite.
- The diff touches 3 test files; none of them is about pan.

**Mutation, and it is decisive.** `M-CR-PAN-A`: `_consumes_pan` → `return True`. This
single edit reverts **both** behavioural halves at once, because the `_pan` guard and
the `_reclamp_pan` branch are both gated on it — it restores the exact pre-S-D lying
affordance.

```
target:        C:\Users\jjgh8\Github\mapper\mapper\app.py
orig sha256:   49300f7dea4c280c05480fe9fa432943893d48e79e9532a7d7086c51dd5188d5
CRLF anchor occurrences: 1
mutant sha256: aac303223786c417f9e4c5f271a493a1e4b0e23846b88d2e8bc10bc6d7b403c3

============ M-CR-PAN-A VERDICT ============
SURVIVED | pytest exit: 0
  1096 passed, 19 deselected, 3 xfailed in 335.58s
============================================
restored sha256: 49300f7dea4c280c05480fe9fa432943893d48e79e9532a7d7086c51dd5188d5
restore verified byte-for-byte
```

Discipline: `C:\Users\jjgh8\clde\cr_sd_mutate.py`, reviewer scratchpad, byte-level I/O,
**CRLF-normalised anchor asserted `== 1`** (an LF anchor would have matched zero times
and the harness prints `BAD`, never `SURVIVED`), verdict printed **before** the restore
assert, `PYTHONDONTWRITEBYTECODE=1`, `__pycache__` purged both sides, sha256 restore.

**Why it matters.** `1096 passed` is a **true statement about this increment that
carries no information about a third of it**. The suite cannot distinguish the shipped
behaviour from the defect it was written to remove. And F1 is the direct consequence:
the arm that would have caught the state loss is the arm that does not exist.

**Suggested fix.** Three arms, all end-to-end through `MapScreen`, on a map where
layered pan genuinely moves (the shipped fixtures **cannot** carry these — pan is a
no-op on them, and an arm built on them is green by construction):

1. **Inert-and-declared:** in outline and in radial, a pan key leaves `(pan_x, pan_y)`
   unchanged **and** sets the hint. Positive control in the same arm: the same key in
   **layered** moves the offsets — otherwise the arm cannot tell "inert" from "the
   fixture never panned". This is the arm that kills `M-CR-PAN-A`.
2. **Round trip (F1's regression):** pan in layered → toggle to outline → toggle back →
   the offsets are the ones the operator set. Same for radial, **with no key pressed**.
3. **Latch (F3):** the hint does not survive back into a view where pan is live.

---

### F3 — The new hint LATCHES a false statement into a view where pan IS live · **MEDIUM** · `executed`

**What.** `_pan`'s inert branch sets the hint and returns. Nothing ever clears it.
Press `L` in radial → `r` back to layered → the strip still reads
**`esta vista no se desplaza`** while standing in the view that does scroll, and it
survives unrelated repaints.

**Where.** `mapper/app.py:1681` (set) vs `mapper/app.py:1713` (the only clear, reachable
only on a *successful* pan).

**Evidence.** `C:\Users\jjgh8\clde\cr_sd_probe5.py`, guarded on
`GUARD_pan_is_live_in_layered == True`, both 118x34 and 80x24:

```
hint_in_radial                'siguiente ▸ esta vista no se desplaza'
hint_back_in_layered_no_key   'siguiente ▸ esta vista no se desplaza'
LATCHES_A_FALSE_STATEMENT     True
hint_after_nav                'siguiente ▸ esta vista no se desplaza'
```

**Why it matters.** This is the diff's own doctrine turned on the diff's own new code.
`app.py:1708-1712` records this exact shape as *"a real misdescription rather than
untidiness: the hint is set on a no-op and nothing ever unset it… it latched on the
first sideways press and then sat there describing every LIVE `J`/`K` as an edge the
operator had not reached."* The new branch reintroduces the class on a new surface,
with a statement that is not merely stale but **false in the view it is displayed in**.

**Suggested fix.** Clear it where the property stops holding — `action_toggle_outline`
and `action_toggle_radial` are the two seams, and the clear belongs beside the
`refresh_canvas()` they already call. (Setting it from `refresh_canvas` on the current
renderer would also work and is arguably the honest place, but it is a larger change
than this finding needs.)

---

### F4 — `test_the_residue_S_D_closed_was_real_and_measured` cannot fail on the defect it names · **MEDIUM** · `executed`

**This answers (b) directly: no, it does not earn its place as written.**

Its predicate is `layered.header_rows(g, w, w) > _first_line_rows(radial…)`. Neither
operand is anything `S-D` produced. Concretely:

- **Revert `radial.header_rows` to layered's** — the actual residue coming back — and
  **this arm stays green.** It is insensitive to the defect its own name claims.
- **Revert the dispatch** — same, green.
- The two things that *would* redden it are an edit to **layered's** header or to
  **radial's rendered** header — i.e. unrelated UI work, in a batch that is actively
  editing operator-visible strings (it just shipped one).

So its failure modes are exactly inverted: silent on the regression, loud on the
irrelevant. That is `C-40`'s defect a second time in the same module — a pin whose
declared subject is not the subject it can see — and labelling it a pin does not repair
a predicate that points at the wrong pair of objects.

The residue is already pinned twice and correctly: `test_the_dispatch_gives_radial_its_own_charge`
(the seam) and `test_radial_is_charged_its_own_header_and_not_layereds` (the equality).
This arm adds no coverage and adds a false-alarm surface.

**I did verify its arithmetic is honest.** `C:\Users\jjgh8\clde\cr_sd_probe1.py`, on the
arm's OWN fixture: `layered_charge > radial_own` at exactly `24, 28, 50, 60, 80, 100,
118` and **not** at `20, 34, 40`. The "**7 of 10**, 24 and 28 and every width from 50
up" claim is reproduced exactly, and the chosen parametrization is exactly those 7.
The *number* is right; the *arm* is the problem.

**Suggested fix.** Delete the arm and move its measured table into the module docstring
or the S-D close note as the historical record it is. If it is kept, it must be
renamed — `..._was_real_and_measured` promises a guarantee about `S-D` that the
predicate does not provide.

---

### F5 — `_consumes_pan` answers "unregistered" and "does not pan" with the same silence · **MEDIUM** · `executed`

**This answers "is it too narrow?": no — `renderer is self.renderer` is right, and
identity is mandated. The divergence from its siblings is the defect.**

The docstring cites `A-98` / ruling `02j` — *"a probe must not answer 'this view has no
pan' and 'this view's pan is broken' with the same silence"* — and then does not
implement the shape that delivers it. Both sibling seams enumerate every renderer and
**raise** on an unregistered one:

- `_header_rows_for` (`app.py:1559`): `raise LookupError(f"no header charge registered for {renderer!r}")`
- `_painted_ids_for` (`app.py:1812`): raises, with the reason spelled out — an
  unregistered renderer answering with the legitimate empty value *"would be a lie."*

`_consumes_pan` instead falls through to `False`. A fourth renderer added tomorrow is
**silently classified as non-panning** — and now, after F1, silently has its pan zeroed
on every repaint. That is precisely the silence the docstring invokes `02j` to forbid.

Do **not** make it a property of the renderer: `getattr(renderer, "consumes_pan", False)`
is the shape `A-98`/`02j` rules out, for the same reason.

**Suggested fix.** Mirror the siblings exactly:

```python
if renderer is self.renderer:
    return True
if renderer is self.outline_renderer or renderer is self.radial_renderer:
    return False    # RULED, not absent: focus-based/polar navigation (2026-09-18)
raise LookupError(f"no pan consumption registered for {renderer!r}")
```

---

### F6 — Hint register: a declarative sentence among key legends, offering no alternative · **LOW** · `executed`

**This answers (c).** Two of the three checks pass; one drifts.

**Permanence — CORRECT.** `"esta vista no se desplaza"` reads as a standing property of
the view, which is what the ruling says it is. The contrast with its nearest sibling is
exactly right: `"borde del territorio"` is a *location* and correctly reads as
transient (move the other way and it is gone). A hint that read transient here — "no
puedes desplazarte ahora" — would be the `UI-AT058` failure. It does not. Good.

**Lexicon — CORRECT, and better than I expected.** The app's own keybinding labels are
`desplazar izquierda / derecha / arriba / abajo` (`tests/test_key_dispatch.py:70-74`).
The hint reuses the app's established verb for pan rather than inventing one. Strong
conformance.

**Register — DRIFTS.** Every other hint on this strip is a label or a key legend:

| | |
|---|---|
| `DEFAULT_MAP_HINT` | `navega con j/k/h/l · ↵ ficha · / buscar` |
| rail | `rail · ↵ plegar rama · esc volver al mapa` |
| required field | `completa «X» · ↵ guarda · esc deja el campo` |
| pan edge | `borde del territorio` |
| **new** | `esta vista no se desplaza` |

It is the only full declarative sentence, and the only refusal that does not pair
itself with the next move — the house pattern is *refusal · what to do instead*. In
radial the alternative exists and is the point of the ruling.

**Suggested fix (taste, not correctness).** `esta vista no se desplaza · navega con j/k/h/l`
— fits the 80-col strip (`siguiente ▸ ` + 48 cells) and matches the sibling shape.
Author's call.

---

### F7 — The pre-gate's "6 arm-instances will redden" was falsifiable before S-D started · **LOW / process** · `executed`

**This answers (a): your diagnosis is right, and it is stronger than you put it.**

I looked for a way `S-D` should have reddened
`test_radial_still_receives_layereds_charge_and_S_D_must_redden_this` and there is
none. Its predicate reads `layered.header_rows` and radial's **rendered** first line.
`S-D` changes neither: `layered.py` was **dropped from the cut** by the 2026-09-18
amendment, and closing a *charge* residue by definition does not move the *painted*
header. So the amended cut did not merely fail to redden the arm — **it removed the
last file whose edit could have moved that predicate.** The prediction became
arithmetically impossible at cut-amendment time, and reading the predicate then would
have shown it.

The one arm that did redden is the one that drives `_header_rows_for`, the seam the
defect lives in. That is the general lesson and your rewrite states it correctly.
Recorded here because the same shape will recur: **a pin's declared subject and its
predicate's operands must be the same objects**, and a cut amendment should be checked
against the arms the pre-gate expects to redden.

No action owed on the code. The rewrite to the equality form is correct.

---

## Confirmations — what I attacked and could not break

**(d) The A3 census 32 → 34 is exactly the two sites claimed. CONFIRMED.** `n/a — no
defect`. Derived by running `test_a3_census.render_call_sites()` — **the pin's own
derivation** — against both trees (`C:\Users\jjgh8\clde\cr_sd_probe4.py`):

```
zeroarg: HEAD=32  NOW=34  delta=+2
  tests/test_agree_floor.py: 2 -> 4
    new: tests/test_agree_floor.py:194  (canvas.render())
         tests/test_agree_floor.py:195  (strip.render())
argful:  HEAD=62  NOW=62  delta=0
```

Both new sites are the `_radial_frame` twins, both zero-arg widget renders, both
correctly outside the A3. **`argful` is unchanged at 62** and no `mapper/` file moved —
which is the check that matters for your masking question: a real migration defect
would have shown as an `argful` delta or a production-file site. There is none. Both
pins moved together in one lane run, as their construction requires.

**The `_header_line` factoring is inert. CONFIRMED — I tried to falsify it and failed.**
`C:\Users\jjgh8\clde\cr_sd_probe2.py` loads `2f78ecc:mapper/views/radial.py` as a
separate module and compares `_paint` output — **plain text, style spans, and the
returned painted set** — against the working tree:

- **6 579 renders** (your 144 ×45): 9 graphs including the 3 real fixtures
  (`legacy`, `anidado`, `truncado`) loaded through `MapStore`, widths **4…200**
  (the whole narrow wrap band, not just the sweep), heights 3…50, two selections each.
- **0 differences.**
- **Comparator control FIRED** (w=40 vs w=39 reported a difference), so the zero is a
  measurement and not a dead comparator.

By inspection the factoring is also textually equivalent — the old code built `header`
before `unpainted` existed and appended the phrase after; the new code passes
`unpainted` in. Same line, one source. This is the cleanest part of the increment.

**The header-charge equality is not a narrow-band accident. CONFIRMED.**
`cr_sd_probe1.py`: `radial.header_rows(g,w,w) == _first_line_rows(radial…)` holds at
**10 of 10** `WIDTHS` **and** at all 7 widths of my own narrow extension (6, 8, 10, 12,
14, 16, 18), where the header wraps to 3–8 rows. The arm is exercising real wrap
behaviour, not a constant — the failure mode `NARROW` exists to catch for outline does
not apply here.

**Worst-case charging is correct and matches the siblings.** `n/a — by design`. Probe 1
shows the charge diverges from a zero-`unpainted` line by 1 row at every `w ≤ 40`, so
radial over-charges when the frame hides nothing. That is `layered.header_rows`'s
documented tradeoff (stability across a repaint) and it errs in the **safe** direction —
fewer body rows, never a phantom declaration, so it cannot produce `CR-F1`. Conforming,
not a finding.

**Lanes and lint, re-derived, inheriting nothing.**

| | Measured by me |
|---|---|
| default lane | **1096 passed, 19 deselected, 3 xfailed**, exit 0, 324 s |
| `ruff check .` | **27 errors** — identical to `2f78ecc` measured in a detached worktree |
| ruff on the 5 S-D files | 1 — `mapper/app.py:5 F401 're' imported but unused`, **pre-existing**, line 5, untouched |
| `FLAKE-2` | did not fire in my run; `n/a — not reproduced here`. Your 4-of-10 isolated figure stands unchallenged and unverified by me. |

**The working tree is exactly as I found it.** `git status --porcelain` shows the same
6 modified files; `mapper/app.py` sha256 `49300f7d…` before and after both harness runs;
the comparison worktree was created detached and removed. I am not the writer.

---

## Boundary statement

**What I saw.** The complete diff, read line by line; the surrounding code at every seam
it touches (`_header_rows_for`, `_painted_ids_for`, `_canvas_size`, `refresh_canvas`,
`_view_state`, both view-toggle actions, every `set_hint` call site in `mapper/`); the
full default lane executed here; ruff on both trees; and five probes of my own, each
driving the derived set or the real screen rather than a model of it.

**What I could not see — constructed, not asserted.**

1. **The operator cost of radial's worst-case over-charge at the declared context.**
   I *measured* that the divergence exists (probe 1: worst-case 2 rows vs a 1-row
   zero-`unpainted` line at every `w ≤ 40`) and I *reasoned* it is safe. What I did not
   do is drive a real fixture at 118x34 and a short region and count the body rows the
   operator loses when nothing is hidden. It is bounded at one row and it errs toward
   under-showing, which is why I stopped — but "one row, safe direction" is an argument,
   not a measurement, and I am naming it as such rather than implying I checked.
2. **The `-m slow` lane.** Not run. Your `19 passed` is uncorroborated by me.
3. **`FLAKE-2` in isolation.** Not reproduced; the `4 of 10` figure is yours.
4. **Security and functional-suite validation** are `security-reviewer`'s and
   `qa-reviewer`'s lanes. I flag for `qa-reviewer` that **F2 makes "the lane is green"
   a weaker statement than it reads** — the PAN-1 third of this increment is invisible
   to the suite, and that is a coverage gap, not a correctness finding, once F2's arms
   are specified.
5. **The `grande` fixture is mine, not the tree's.** F1 and F3 are reproducible only on
   a map where layered pan actually moves. That workspace is generated by my probes and
   is not in the repo — which is itself part of F2's fix: the arms that pin PAN-1 will
   need such a fixture, because the shipped ones make every pan arm green by
   construction.

---

## Evidence checklist

- [x] **Diff read in full** — 6 files, ranges tabulated under *Scope reviewed*.
- [x] **Correctness pass (edge / None / error paths)** — F1 (state loss), F3 (latch),
      F5 (unregistered renderer falls through instead of raising). Also checked: the
      non-consumer early return skips `pan_extent`, so the cyclic-graph guard at
      `app.py:1688` is bypassed for outline/radial — harmless, `n/a — no defect`.
- [x] **Simplicity pass** — no premature abstraction found. `_header_line` is a genuine
      two-caller extraction (`DECL-118-TWICE`), not speculative. My recommended F1 fix
      **removes** a line rather than adding one.
- [x] **Reuse / duplication** — `header_rows` correctly reuses `Console.render_lines`
      (the `outline`/`_fit` instrument, `B-61`) and keeps the `(graph, w, wrap_w)`
      signature so `_canvas_size` dispatches without a special case. `_consumes_pan`
      reuses the identity-dispatch pattern but **not** its raise (F5). `_radial_frame`
      deliberately does not share `_frame`, and the `C-60` reason given is sound — a
      control that shares a code path with its subject stops being a control.
- [x] **Tests reviewed for intent, not behaviour** — F2 (a third of the increment
      unpinned, proven by a surviving mutant), F4 (a pin insensitive to its own named
      defect), F7 (a pin whose subject was not the change's subject). The `C-55` rider
      on the AGREE-1 control is correctly discharged: the outline control arm
      (`test_the_narrow_grid_really_does_reach_a_floor_in_outline`) is what makes
      radial's zero admissible, and the `assert exercised` guard is what keeps the
      radial arm from asserting nothing. That workstream is well built.
- [x] **Verdict explicit** — **BLOCKED**; `BLOCK-UNTIL: F1, F2` governs re-entry; no
      HIGH carries applied-and-verified evidence, because neither fix is applied.

## Evidence states

| Finding / check | State |
|---|---|
| F1 pan discard | `executed` — probe3c, both trees, guarded on `layered_moves > 0` |
| F1 suggested fix | `executed` — applied under harness, verified, restored by sha |
| F2 `M-CR-PAN-A` SURVIVED | `executed` — full default lane, 1096 passed, exit 0 |
| F2 corrective arms | `planned` — owed by `software-dev` |
| F3 hint latch | `executed` — probe5, live-pan guard, 2 sizes |
| F4 pin insensitivity | `executed` — by construction over the predicate's operands |
| F5 missing raise | `executed` — read against both sibling seams |
| F6 hint register | `executed` — compared against all 5 strip strings |
| F7 pre-gate prediction | `executed` — `n/a` for the code, process note only |
| Header factoring inert | `executed` — 6 579 renders, 0 diffs, control fired |
| Charge equality 10/10 + narrow 7/7 | `executed` — probe1 |
| A3 census +2, argful 62→62 | `executed` — probe4, the pin's own derivation |
| Default lane / ruff | `executed` — 1096 / 27, ruff baseline matched at `2f78ecc` |
| `-m slow` lane | `not-run` |
| `FLAKE-2` isolation rate | `not-run` — `n/a — did not fire here` |
| Security review | `n/a — security-reviewer's lane` |
| Functional suite validation | `n/a — qa-reviewer's lane` |

## What is owed before S-D can close

1. **F1** — hold the offsets instead of zeroing them (one line; verified).
2. **F2** — the three arms above, on a fixture where layered pan actually moves.
   `M-CR-PAN-A` must be **KILLED** and that verdict printed.
3. **F3** — clear the hint at the two view-toggle seams.
4. **F4 / F5 / F6** — recommendations. They do not block; F5 is the one I would take.

Then **re-review**, by me, **on the diff**. `BLOCK-UNTIL: F1, F2` is not discharged by a
report that the corrective pass ran.

## Probes

Reviewer scratchpad — `C:\Users\jjgh8\clde\`:
`cr_sd_probe1.py` (charge derivation) · `cr_sd_probe2.py` (inertness, HEAD-vs-now) ·
`cr_sd_probe3.py` (round trip — **vacuous, kept as the record of the `C-31` near-miss**) ·
`cr_sd_probe3b.py` (finding a pannable configuration) · `cr_sd_probe3c.py` (guarded round
trip) · `cr_sd_probe4.py` (A3 delta) · `cr_sd_probe5.py` (hint latch) ·
`cr_sd_mutate.py` (`M-CR-PAN-A`) · `cr_sd_fixcheck.py` (F1 fix verification).
