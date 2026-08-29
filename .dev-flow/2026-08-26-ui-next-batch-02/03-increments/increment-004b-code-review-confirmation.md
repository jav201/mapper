# Code Review — Increment 4b, round-2 CONFIRMATION pass

**Verdict: PASS.** Both HIGH findings are independently DISCHARGED — re-measured, not read off
the author's table. Both MEDIUM fixes hold, including the width-aware budget that replaced the
remedy a reviewer proposed and that measurement rejected. Three NEW findings, none HIGH: one LOW
on a decorative self-guard, one MEDIUM on sealed-text drift, one LOW on an unqualified `shall`.
None blocks the increment.

---

## 0 · Confirmation environment

`git clone --local --no-hardlinks` of the repository at `a971432` into the scratchpad, working tree
of `mapper/`, `tests/` and `.dev-flow/` overlaid, index reconciled with `git add -N` **in the mirror
only**. Overlay fidelity established **before any mutation**, two ways:

```
sha256 over mapper/*.py, mapper/*/*.py, tests/*.py   ->  byte-identical to the real repo
full lane, PYTHONUTF8=1                              ->  847 passed, 17 deselected, 3 xfailed
```

That reproduces the declared exit lane exactly, so every verdict below is read against a tree known
to start green. Four independent mirrors were used so full-lane mutants could run concurrently;
each restores by sha256 to `mapper/app.py = 6f0f1461…95c0b51` before the next mutant is applied.
Mutations are described **by position and operation only**; no mutated token and no hostile code
point is spelled here.

**The real repository was never mutated.** Closing state, verified:

```
mapper/app.py        6f0f14614ff93fa8b3bee31d06339954cd3ae0e58149cb48e0159be7995c0b51
mapper/keymap.py     3846c22ebb2f69b5dc7589a0f29444c3e7f90845189b09a49def70d828d7c159
tests/test_search.py d66a21c385dee8ae349bde712daf06378971843a896babc395138335f007ab8f
tests/test_fold.py   420ba5fddb4f9559afed09c9e4c0ee990f24b0bdd744d5a6da289f85f49ea13b
HEAD = a971432, nothing committed, tests/test_inc4_census.py still staged
```

### 0.1 · Arm counts asserted before any verdict was trusted

```
tests/test_inc4_census.py                                          ->  3   ✓
test_search.py -k "at_022 or at_023 or at_051 or at_053 or p052_2
                   or cd6a or above_the_render_bound
                   or esc_and_the_hint_line"                        -> 12   ✓
test_fold.py   -k "at_046 or at_047 or esc_limpiar_off_the_frame"   ->  6   ✓
collection, all markers                                             -> 867  ✓
```

Every mutation verdict below is a **per-arm** verdict read from `-v` output, never a process exit
code, and every selector's base count was read before the mutant was applied.

---

## 1 · C1 · `F1` — the dead entry path · **DISCHARGED**

Three mutants, all re-run by me on the mirror.

| Id | Operation | Base | Mutated | Verdict |
|---|---|---|---|---|
| `R2` | the else limb's body replaced by a raise | 847 passed | **3 failed, 844 passed** | RED |
| `R1` | the else limb's two endpoints exchanged | 2 passed | **1 failed** | RED |
| `R1b` | the else limb's conditional collapsed to its forward arm | 2 passed | **1 failed** | RED |

**`R2` reproduces the headline exactly.** The three reddened nodes are
`test_search.py::test_at_022b_the_walk_enters_from_outside_the_hit_set` and **both sizes** of
`test_fold.py::test_the_opened_branch_name_cannot_push_esc_limpiar_off_the_frame` — two independent
paths, as claimed. The limb is no longer dead to the suite.

**The `N` limb is the half that matters, and the receipt holds.** Under `R1b` the arm fails at the
**backward** assertion and the **forward** assertion passes:

```
R1b -> assert 'riesgo-root' == 'c'   (backward; the forward assertion is listed as executed-and-passed)
R1  -> assert 'c' == 'riesgo-root'   (forward)
```

Two different assertions, two different mutants. A forward-only arm would have shipped green under
`R1b`. That is the receipt round 1 asked for and it is genuine.

**The not-in-hits precondition holds — but not by the mechanism the docstring claims.** See NEW-1.
The precondition is enforced by *construction* (`tests/test_search.py:1366` selects the cursor by the
predicate `nid not in found`), and a fixture in which every node matched would raise `StopIteration`
at that line — loud, not silent. So the arm cannot silently return to the other limb. The assertion
two lines below it, labelled `SELF-GUARD`, is a tautology and can never fire.

---

## 2 · C2 · `F2` — `AT-047`'s re-close blind spot · **DISCHARGED**

The improvement is **measured, not asserted**. I reconstructed the round-1 shape of `AT-047` — the
single further press, same fixture helper, same `_pill_titles` assertions, same two sizes — and ran
both forms under the *same* re-close mutant in the same process:

| Under `R3` (opened set re-added to `folded` at the top of the next walk call) | size 118x34 | size 80x24 |
|---|---|---|
| `AT-047`, **round-1 form** (one further press) | **PASSED** | **PASSED** |
| `AT-047`, **round-2 form** (walk asserted out of the branch) | **FAILED** | **FAILED** |
| `AT-046` (both sizes) | PASSED | PASSED |

Base for the selector was 4 passed; mutated 2 failed, located at

```
AssertionError: b's fold pill is painted again: ['Contratos en …', 'Auditoria']
```

which is the assertion the author located. The round-1 arm was blind to this defect and the round-2
arm is not. That is the finding discharged on evidence rather than on a table.

**The walk-out loop is bounded and cannot pass without leaving the branch.**
`tests/test_fold.py:1102-1111`: the loop is `for _ in range(len(hits) + 2)`, breaks on the cursor
leaving the pre-walk hidden set, and is followed by a hard `assert screen.nav.cursor not in hidden`
with a message naming exactly why. It cannot hang (bounded, and `timeout = 120` in `pyproject.toml`
is a second backstop) and it cannot silently pass (the assertion is outside the loop, not a `break`
that falls through). `_walk_until_hidden` at `tests/test_fold.py:993-998` has the same shape and
`raise`s rather than skipping. Both are correct.

---

## 3 · `M2` — the width-aware budget, swept rather than sampled

The prompt asked me to treat my own recommendation as a hypothesis. **Correction to the record
first: the `darkside.fit(names, 40)` + reorder recommendation was the *security* review's `F1`, not
the code review's** (`increment-004b-security-review.md:31-55`). The code review's `F1` was the dead
walk limb. The substance of the prompt stands; the attribution does not.

### 3.1 · The shipped budget, 25 widths

Driven with the arm's own scenario (branch title of 400 repeated filler characters, one real fold,
the real query, the real walk into the branch), reading the composited hint region — not the
widget's `text`:

| width | hint region height | `limpiar` in frame | announcement painted |
|---|---|---|---|
| 200 · 160 · 140 · 118 | 1 | **yes** | yes |
| 110 · 100 · 95 · 92 · 90 · 88 · 86 · 84 · 82 | 1 | **yes** | yes |
| 80 · 78 · 76 · 74 · 72 · 70 · 69 | 1 | **yes** | yes |
| 68 · 67 · 66 · 65 · 60 · 55 · 50 | 1 | **yes** | **dropped** |
| 45 · 40 | 2 | **yes** | **dropped** |

**`esc limpiar` survives at every width tested, 40 through 200.** The strip stays one row down to 50
columns; at 45 and 40 it wraps to two rows, but the announcement is already dropped there, so that
wrap is the base affordance string against a very narrow row and not the branch name — the guard is
doing its job and something else is at its limit, well below any declared size.

**The announcement's drop threshold is exactly 69 / 68 columns**, narrowed by a second sweep:
painted at 69, dropped at 68. This matches the arithmetic of the budget — the affordance prefix is
38 characters and the overhead constant is 23, so the remainder falls below the 8-cell floor at 69
columns. **The narrowest declared regime is 80 columns; the threshold is eleven columns below it.**

### 3.2 · `R6` — the first-attempt fix, re-run

| Id | Operation | Base | 118x34 | 80x24 |
|---|---|---|---|---|
| `R6` | the width term removed from the budget (fixed cap) | 2 passed | **PASSED** | **FAILED** |

Confirmed: reddens at 80x24 **only**, exactly as claimed, at

```
AssertionError: the hint line wrapped to 2 rows on a 400-character branch title …
assert 2 == 1   where 2 = Region(x=0, y=21, width=80, height=2).height
```

Swept under `R6`, the fixed cap wraps the strip from **100 columns downward** — so the recommended
form was not marginal at 80, it was wrong across a 60-column band. The second declared size earns
its place.

**One honest nuance, in the arm's favour.** Under `R6` at 80x24 the `limpiar` assertion still
*passes*; the arm's teeth are the **height** assertion. The round-2 prose describes `limpiar` being
lost, which is the ~2000-character measurement, not what the 400-character arm catches. The arm
therefore fires one step *earlier* than the narrative — it catches the wrap before the affordance is
actually lost. That is stronger, not weaker, but the artifact's wording and the arm's mechanism are
not the same claim.

### 3.3 · `R5` and `R10`

| Id | Operation | Base | Mutated | Located at |
|---|---|---|---|---|
| `R5` | the cell bound removed from the name segment | 4 passed | **2 failed** | `assert 5 == 1` (118x34), `assert 7 == 1` (80x24) |
| `R10` | the announcement suppressed unconditionally | 4 passed | **4 failed** | `'Contratos en riesgo' in <hint>` (AT-046 ×2) and `'abrió' in <hint>` (×2) |

Both reproduce the author's located assertions verbatim. `R10` going red confirms the announcement
is genuinely gated rather than absent — which is the precondition for ruling on RISK-2 at all.

---

## 4 · The two declared risks · RULINGS

### RISK-1 · `esc` above the render bound now pops on the FIRST press — **RULING: the resolution is correct. Ship it. A ux lens is wanted, but not as a gate.**

The principle the unification encodes is the right one and it is the stronger half of `#D38`: **a
handler must not act where no affordance was painted.** `#D38` fixed the case where the hint
promised and the handler did not deliver; acting where nothing was promised is the same defect
mirrored, and it is worse in one respect — the operator gets no screen change at all and presses
again. One predicate for both surfaces (`mapper/app.py:2321-2337`, consumed at `:2271` and `:2853`)
is the correct shape, and `R4` proves the second conjunct is load-bearing on **two different arms at
two different assertions**:

```
R4 -> assert hint != 'sin coincidencias · esc limpiar'   (the above-the-bound arm)
R4 -> assert 'limpiar' not in <hint>                     (the esc arm -- a different node)
```

Against making the hint promise `esc limpiar` above the bound instead: above the bound
`_search_order()` returns `None` — the question was never answered — so there is nothing painted to
clear. A hint promising to clear an invisible query is the lying affordance `US-N07` exists to
remove, one surface over. The chosen resolution is the one consistent with the rest of the batch.

**One residual asymmetry worth a ux ruling, not a code change.** Above the bound the query survives
in `query_text` and still changes what `n` does — the walk paints `búsqueda sin evaluar` rather than
`sin búsqueda activa` (`mapper/app.py:2499-2510`) — while no surface advertises the query and `esc`
declines to clear it. The operator's escape is not blocked: `escape` pops the screen and the query
dies with it, visibly. So there is no lock-in and no silent state change. But "a query that is live
enough to change a keypress and invisible enough to have no affordance" is a state worth a
deliberate ux decision. **Not a gate item.**

### RISK-2 · the fold announcement can be dropped on a very narrow terminal — **RULING: legitimate degradation, NOT a `shall` violation at any declared size. The requirement text should say so.**

Three reasons, in order of weight.

1. **No declared size reaches the threshold.** The batch's declared context of use is 118x34 and its
   second declared regime is 80x24 (`01-requirements.md:732-735`, the `R-013` auto-hide band). The
   measured drop threshold is **68 columns** — eleven below the narrower declared regime. Within
   everything the document declares, `LLR-N06.2.4`'s clause is satisfied, and `R10` proves it is
   satisfied by a gated mechanism rather than by luck.
2. **Honouring the clause literally at that width would defeat it.** `HintLine` wraps rather than
   clips. Below ~69 columns, painting the name costs the strip a row, and rows come out of the
   canvas; swept under `R6`, a build that insists on painting the name takes the strip to two rows at
   100 columns and keeps going. A name painted on a row that has left the frame is not painted. The
   clause cannot be honoured below the threshold — it can only be *appeared* to be honoured.
3. **The competing obligation outranks it and the ranking is the right way round.** `esc limpiar` is
   the recovery route `#D38` newly promises; the announcement is a courtesy the operator can also
   read off the map, since the branch visibly opened. Losing the recovery route is the worse failure.
   The code ranks them correctly.

**But the sealed text does not say any of this** — see NEW-3. The clause is written unconditionally.
The right close is a one-line proviso in the requirement, not a code change.

---

## 5 · Also confirmed

### 5.1 · The two declared survivors — **declaring them is adequate**

| Id | Operation | Whole lane | Verdict |
|---|---|---|---|
| `R7` | the `_branch_name` guard reverted to a bare subscript | **847 passed** | SURVIVES |
| `R8` | the branch count cap removed from the name join | **847 passed** | SURVIVES |

Both re-run by me over the **full lane**, not a selector. Both survive exactly as predicted.

**`R7` — declaring it is right, and adding an arm would be wrong.** The branch is unreachable from
file data (the loader synthesises a `Node` for every edge endpoint), so an arm would have to build an
in-memory graph the load path cannot produce, and would then pin a state that does not exist. The
guard is a one-line fall-through with no behaviour to assert. Declaring an uncovered line is the
honest close; inventing an arm to make the ledger look complete would be the dishonest one.

**`R8` — declaring it is adequate, and I disagree with the author on one point.** The author says
closing it needs a four-nested-fold fixture. That is true for the `+N` overflow text, but the
*slice* half is closable more cheaply: a fixture with two folded branches both hiding the same hit
would make `opened` length 2 and put two names in the join, which distinguishes the cap's presence
from its absence at `_HINT_BRANCHES` = 3 only if the cap is lowered — so no, at the shipped constant
the author is right, four folds is the honest cost. **The declaration stands.** The operator-visible
claim is pinned anyway: the width budget (`R5`, `R6`) bounds the painted result regardless of how
many names the join produced, and `R5`/`R6` are both RED. The uncovered line is a cosmetic count, not
a frame-affecting one.

### 5.2 · The pre-existing map-body defect and the arm's self-guard — **the self-guard is REAL**

This is the thing standing between the arm and a false green, and it holds. I raised the arm's title
length from 400 to the length at which the author says the pre-existing defect takes over, and ran
the shipped arm. It fails **at the self-guard**, at both sizes, with the self-guard's own message:

```
118x34 -> AssertionError: the chrome is already off-frame before the walk; this arm would be
          measuring the map body's unbounded content, not the hint line
          assert 42 < 34   where 42 = Region(x=0, y=42, width=116, height=1).y
80x24  -> same message
          assert 59 < 24   where 59 = Region(x=0, y=59, width=78, height=1).y
```

`y=59` of a 24-row frame, reproduced independently. The guard fires **before** the search and
**before** the walk (`tests/test_fold.py:1206`), so it cannot be reached by a frame the walk
corrupted, and it names the confusion it exists to prevent. This is a genuine false-green barrier,
and the pre-existing defect it fences off is correctly recorded rather than quietly fixed inside a
walk increment.

### 5.3 · Ledger arithmetic — **11 is right**

The table carries eleven rows: `R1`, `R1b`, `R2`, `R3`, `R4`, `R5`, `R6`, `R7`, `R8`, `R9`, `R10`.
Nine RED plus two surviving reconciles to eleven. `R1b` is a distinct mutant — I re-ran it against
its own base and it fails at an assertion `R1` does not touch, so it is not a variant. The
orchestrator's correction at the gate is correct and the prose's original "10 run" was the error.

### 5.4 · `M1` — the exemptions are reasoned and **cannot be widened**

`R9` (the `_search_is_live` exemption row removed) is RED, at:

```
AssertionError: ['_search_is_live'] reach the search resolution without opening a paint
pass and without a stated reason.
```

I then ran the mutation the ledger does **not** contain — the one that matters for "widened, not
reasoned". I added a row to `_PASS_FREE_READERS` for a method that reaches nothing:

```
AssertionError: ['_widened_by_the_reviewer'] no longer reach the resolution; drop the exemption
```

The table is pinned as an **exact set in both directions** (`tests/test_search.py:1087-1096`):
unexplained readers fail, stale exemptions fail, and an exemption with an empty reason fails. The
two new rows are therefore load-bearing declarations, not a widened allowlist. Confirmed.

### 5.5 · Instrument re-measurements

```
ruff, scope mapper/ tests/, --output-format concise, line/col normalised, diffed as sorted sets
  entry (clean a971432 checkout): 27 findings
  exit  (working tree):           27 findings
  NEW: (none)   GONE: (none)      -> IDENTICAL

len(KEYMAP)              = 54
len(bindings_for("map")) = 33      rows with scope == "map" = 31
duplicate_chords()       = []

source files changed vs HEAD: mapper/app.py, mapper/keymap.py  -> 2, the declared budget
```

---

## 6 · NEW findings

### NEW-1 — the `AT-022b` "SELF-GUARD" assertion is a tautology and can never fire  [Severity: LOW]

- **What:** `assert outsider not in order` cannot fail. `outsider` is selected on the line above by
  the predicate `nid not in found`, and `order` is built two lines earlier by filtering on
  `nid in found`. `order` is a subset of `found` by construction, so the assertion is a theorem.
- **Where:** `tests/test_search.py:1366-1370`, claim made at `tests/test_search.py:1344-1347` and
  repeated in `increment-004b.md:464-468`.
- **Why it matters:** the *protection* is real — the cursor genuinely starts outside the hit set, and
  a fixture in which every node matched would raise `StopIteration` at `:1366`, loudly. So there is
  no false confidence in the arm's verdict. But the artifact and the docstring both describe a
  mechanism that does not exist ("a fixture edit that made the node a hit reddens the arm"), and a
  later reader who trusts that sentence will believe a guard is watching a seam nothing watches.
  There is also a real seam left unguarded: the arm computes `found` from `SearchIndex(...).query(...)`
  while production resolves through `_search_order()`. If those ever diverge — which is precisely
  what `M-N07.3-a`, a second result set, would do — `outsider` could be inside production's hit set
  while the test still believed it was outside.
- **Suggested fix:** make the guard non-tautological by asserting against the **production**
  resolution, after the query is submitted:
  ```python
  await submit(pilot, QUERY)
  assert outsider not in (screen._search_order() or ()), (
      "SELF-GUARD: the cursor must start OUTSIDE the resolution the WALK reads, "
      "or this node resolves through the `in hits` limb and asserts nothing new"
  )
  ```
  and reword the docstring and `increment-004b.md:466-468` to say the precondition is enforced by
  construction, with this assertion covering the oracle-divergence case.

### NEW-2 — `LLR-N06.2.4`'s numeric pass threshold still specifies the predicate this round measured to be insufficient  [Severity: MEDIUM]

- **What:** `PRED-C` in the sealed requirement reads *"After 1 further walk press, the previously
  opened branch paints no fold pill."* The shipped arm no longer does that — it walks until the
  cursor is asserted **out** of the branch. The correction was made in the test file's section header
  and in `increment-004b.md`; the requirement itself is unamended and `01-requirements.md` is not in
  this increment's modified-file set.
- **Where:** `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md:2046-2048` versus
  `tests/test_fold.py:921-925` and `tests/test_fold.py:1102-1111`.
- **Why it matters:** the sealed threshold is now known-defective, and the evidence is in hand —
  measured in §2 above, the single-press form **passes at both sizes** under a re-close mutant that
  the walk-out form fails at both sizes. A requirement whose stated numeric threshold is weaker than
  the shipped arm is the exact shape of drift this batch's traceability discipline exists to prevent:
  the next increment that reads `LLR-N06.2.4` to build an arm will build the weak one, and it will be
  green. This is bookkeeping, not behaviour — nothing shipped is wrong — but it is bookkeeping that
  decays into a false-confidence test one increment later.
- **Suggested fix:** amend item 3 of the numeric pass threshold to
  *"`PRED-C` — the branch stays open, observed on the SURFACE. Once the walk has moved OUT of the
  opened branch — asserted, not counted in presses — that branch paints no fold pill. Read from the
  painted frame. ('Out of', not 'one more press': the next hit can be inside the same branch, where a
  re-closing implementation re-opens on the same press and is indistinguishable — measured, Inc-4b
  round 2.)"* and add it to the batch's spec-corrections list with the two-form measurement as its
  evidence.

### NEW-3 — the `shall paint the hint line naming the branch it opened` clause carries no width proviso  [Severity: LOW]

- **What:** the clause is unconditional in the sealed text. Measured, the announcement is dropped at
  68 columns and narrower.
- **Where:** `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md:2027-2029`; the drop is at
  `mapper/app.py:2449-2451`.
- **Why it matters:** the behaviour is correct (RULING, §4) and no declared size reaches the
  threshold, so this is not a violation in practice. But a `shall` that the code knowingly does not
  satisfy at some inputs, with the deviation recorded only as a risk note in an increment artifact,
  is how an undeclared exception becomes an undiscovered one. The requirement should carry the
  proviso the code already implements.
- **Suggested fix:** append to the statement: *"…shall paint the hint line naming the branch it
  opened **where the strip has room for the name without wrapping** — below that the affordances
  outrank the announcement, because `HintLine` wraps rather than clips and a wrapped strip takes its
  rows from the canvas (measured: the announcement is dropped at 68 columns and narrower; the
  narrowest declared regime is 80)."* Alternatively, declare a minimum supported terminal width for
  the batch and note that the threshold sits below it.

---

## 7 · Evidence checklist

- [✓] **Mirror built and fidelity established BEFORE mutating** — `847 passed, 17 deselected,
      3 xfailed` on the overlaid clone, plus byte-identical sha256 over all overlaid sources.
- [✓] **Diff read in full** — `mapper/app.py:93-101, 2252-2274, 2305-2337, 2367-2454, 2456-2540,
      2830-2857`; `tests/test_search.py:974-1096, 1332-1391, 1826-1877`;
      `tests/test_fold.py:910-1248`.
- [✓] **Arm counts asserted before verdicts** — 3 / 12 / 6 / 867, all ✓.
- [✓] **C1 re-run independently** — `R2` (full lane, 3 failed / 844 passed), `R1`, `R1b`; the
      backward and forward assertions confirmed to fail under different mutants.
- [✓] **C2 measured, not asserted** — the round-1 form reconstructed and run under the same re-close
      mutant: round-1 PASSES at both sizes, round-2 FAILS at both.
- [✓] **Walk-out loop audited** — bounded by `len(hits) + 2`, hard assertion outside the loop,
      `timeout = 120` as a second backstop. Cannot hang, cannot pass without leaving.
- [✓] **`M2` swept, not sampled** — 25 widths from 40 to 200 plus a 6-width narrowing pass;
      `esc limpiar` survives at every width; drop threshold located exactly at 69 / 68.
- [✓] **The rejected remedy re-measured** — under a fixed cap the strip wraps from 100 columns down;
      `R6` reddens at 80x24 only, 118x34 passes.
- [✓] **Survivors re-run over the WHOLE lane** — `R7` 847 passed, `R8` 847 passed.
- [✓] **The self-guard tested by driving it** — fires at both sizes with its own message.
- [✓] **The exemption table probed in the direction the ledger did not** — a widened row is refused
      as stale; the set is exact in both directions.
- [✓] **Ledger arithmetic checked by counting rows** — 11.
- [✓] **Instruments re-measured** — ruff sets identical (27 = 27, zero NEW, zero GONE);
      `bindings_for("map")` = 33; source files = 2.
- [✓] **No mutated token and no hostile code point spelled** — described by position and operation
      throughout.
- [✓] **Real repository unmutated** — four sha256 values identical to the declared exit, `HEAD`
      still `a971432`, nothing committed.
- [✓] **Verdict explicit.**

---

## 8 · Verdict

- [x] **OK to advance.**
- [ ] OK with the listed fixes applied first
- [ ] Block

**PASS.** `F1` and `F2` are DISCHARGED on my own measurements. `M1` and `M2` hold, and `M2`'s
second attempt is better than the remedy that was recommended to it — verified across a width sweep
rather than at two points. The two declared risks are correctly resolved, and the two declared
survivors are correctly declared. The three NEW findings are one LOW on a decorative assertion, one
MEDIUM on a requirement that now lags its own arm, and one LOW on an unqualified clause. **None is a
correctness defect and none is a false-confidence test, so none blocks the increment.** NEW-2 should
be closed before `Inc-5` reads `LLR-N06.2.4` to build anything.
