# Increment 3 — `HLR-GOLD.1` + `LLR-PERF.1`: the derived pin census, `B3`'s correction, the honest fixture

**Batch:** `2026-08-27-repair-batch-02` · **Base ref:** `d877784` · **Branch:** `fix/repair-batch-02`
**Source files: 0 of 4.** Tests and records only.

> **BLUF.** Trigger `B3` was recorded `not_fired` on a probe that was **correct as executed and had
> the wrong input set**: `ls tests/goldens` → no such directory, in a repo that keeps its
> byte-identity pins in a dict inside a test file. A non-activation with a false probe is
> indistinguishable from a trigger nobody evaluated (C-48). The architect lens then reported **18**
> pins from a literal; derived here, it is **12**. Both records are corrected, and the derivation is
> what makes the correction stick.

---

## 1 · What changed

**1. The pin census is derived, never typed** (`LLR-GOLD.1.1`). `tests/test_repair_golden_census.py`
parses `MASTER_LEGACY_DIGESTS` out of `tests/test_repair_depth.py` and asserts
`len(census) == len(renderers) × len(sizes)`. **The threshold is a product, not the number 12** —
writing `== 12` would be the same defect as the reported 18: a literal that stays green when a pin is
added or removed. Every cell of the grid is additionally asserted present, because a product can
match by coincidence while one renderer is double-pinned and another is missing a size.

Parsed rather than imported: importing `test_repair_depth` pulls in Textual and builds depth-5000
fixtures at collection time, which is a large cost for reading two constants — and it would couple
this census to that module's import health.

**2. `RadialRenderer` is named as pinned at all four sizes** — the operative half for the feature
batch. Its Inc-1 makes `Canvas.rows()` honour the `dots`/`bgs` layers, which is exactly what the
radial view paints, so **those four pins redden by construction**. That is an expected re-baseline,
not a regression, and naming it here is what stops it surfacing as a mid-increment surprise (C-24).

**3. `B3`'s non-activation record is corrected, and not merely flipped** (`LLR-GOLD.1.2`). The test
asserts the correction record exists, names the **input-set** error, and names **where the pins
actually live** — so the next reader can check it and cannot re-run the same wrong probe.

**4. The honest 51-node measurement fixture** (`LLR-PERF.1`), and nothing more.

**5. An observation recorded so it does not read as a defect later:** `OutlineRenderer` emits
identical bytes at three of its four sizes, so **12 pins hold only 10 distinct digests**. A future
reader counting distinct digests would otherwise conclude three pins had been lost.

### 1.1 · What `LLR-PERF.1` deliberately does NOT do

**`S-18` (the mount work-budget / deadline mechanism) is PARKED by operator rider** for the feature
batch's PDR, which already carries the pre-authorised renderer-contract change — the deadline hook
belongs in that redesign, *designed once, not patched into three private copies of the walk*. This
batch lands the **measurement**, not the **control**. A fixture asserting a time budget would *be*
the bolted-in mechanism the rider forbids, arriving through the back door of a test file.

**A second, independent reason, measured by this batch:** the slow lane already asserts wall clock
and is ~10% flaky under concurrent load. Adding a second wall-clock assertion to that lane would add
a second flake, not a second guarantee.

**The measurement, recorded not gated:**

```
LLR-PERF.1 measurement: 51 nodes, 410 edges, LayeredRenderer at 140x45 -> 2.3066s
  (NO BUDGET ASSERTED -- S-18 is parked for the feature batch's PDR)
```

**2.3s for 51 nodes is itself the argument that `S-18` is a real design item**, which is exactly what
the rider wanted this increment to supply and no more.

---

## 2 · Files modified

| File | Kind | Note |
|---|---|---|
| `tests/test_repair_golden_census.py` | test (new, uncapped) | 7 nodes |
| `tests/test_repair_perf_shape.py` | test (new, uncapped) | 2 nodes (1 fast shape arm, 1 `slow` measurement) |

**0 source files.** No product code changes in this increment.

---

## 3 · How to test

```bash
PYTHONUTF8=1 python -m pytest tests/test_repair_golden_census.py -q -p no:randomly -o addopts=
PYTHONUTF8=1 python -m pytest tests/test_repair_perf_shape.py -q -p no:randomly -o addopts= -s
```

## 4 · Test results

| Run | Result | Exit |
|---|---|---|
| both new files | **9 passed** in 2.59s | 0 |
| whole fast lane | **517 passed, 17 deselected** | 0 |
| whole slow lane | **17 passed, 517 deselected** | 0 |
| collection | **534 tests collected** | 0 |
| `ruff` on the new files | **All checks passed** | 0 |

### 4.1 · Counterfactual — executed, byte-exact restores

Detached copy. Pristine `tests/test_repair_depth.py` sha256 `16a6892a…` (CRLF);
`.dev-flow/state.json` sha256 `a2b9f7ea…` (**LF**). Both restored byte-exact.

| Mutant | Mutation | RED arms |
|---|---|---|
| `G-a` | drop one pin from `MASTER_LEGACY_DIGESTS` | **4** |
| `G-b` | drop a size from `GOLDEN_SIZES` | **3** |
| `G-c` | flip `B3` back to `not_fired` | **1** |
| `G-d` | strip the input-set reason from the correction | **1** |
| `G-e` | strip the name of where the pins actually live | **1** |

`G-a` and `G-b` are the requirement's named `M-GOLD-a` in its two honest forms: a hand-written number
survives both; the derivation reddens on both. `G-d` and `G-e` are what make the correction a
*correction* rather than a flipped boolean — C-48's whole point.

### 4.2 · ⚠ A harness bug this increment found in itself

The first run of this counterfactual **failed its own restore assertion**. Cause: the harness used
text-mode I/O, and a text round-trip rewrites line endings — reading translates CRLF → LF, writing
translates LF → `os.linesep`. On a CRLF file that is identity, so it looks correct; `state.json` is
**LF**, so the "restore" changed every line in the file.

**The live repo was never at risk** (the lab is a copy, and `git status` on `.dev-flow/state.json`
was clean throughout), but the harness would have reported a false restore. Both harnesses were
converted to **byte I/O**, with the mutation pattern normalised to the file's own line ending rather
than the file normalised to the pattern. **The Inc-1 battery was re-run under byte I/O and reproduced
all 19 verdicts identically** — the bug was latent there because `mapper/store.py` is CRLF.

The general lesson, and it is the reason this is written down rather than quietly fixed: **a
sha256-verified restore only proves what the harness actually wrote.** A harness that normalises on
read cannot detect that it denormalised on write.

---

## 5 · Risks

1. **`test_tc_p06b` pins the literal 12** and is labelled a **regression pin, not a gate** (C-40's
   corollary). The product assertion is the arm above it. Adding a legitimate pin is expected to
   redden it and the number gets updated — that is the intended behaviour, not a defect.
2. **`B3`'s correction was already committed** before this increment (it landed at the feature
   batch's un-park). This increment does not create it; it **pins** it so it cannot silently regress
   and so the reason survives. Stated plainly rather than presented as new work.
3. **The census parses a sibling test module's source.** If `MASTER_LEGACY_DIGESTS` stops being a
   module-level literal, `_literal()` raises with a clear message rather than silently returning
   empty — but it is a coupling worth knowing about.

## 6 · Pending items

- Whole-branch `security-reviewer` sign-off and adversarial `qa-reviewer` pass — both retained as
  merge gates.
- Backlog carry: the slow-lane wall-clock flake (Inc-1 §4.0), with its recipe.

## 7 · Suggested next task

Whole-branch gates → commit → PR → merge → `/dev-flow-sync`. Then the feature batch
`2026-08-26-ui-next-batch-02` is commissioned separately, inheriting the two riders in `PLAN.md` §4.

---

## 8 · Evidence checklist

| Item | ✓/✗ | Evidence |
|---|---|---|
| Tests / lint pass | ✓ | 9 passed exit 0; fast 517, slow 17, 534 collected; ruff clean on new files |
| No secrets | ✓ | tests and records only |
| No destructive command | ✓ | no git mutation; counterfactuals on detached copies |
| File count within cap | ✓ | **0 source files** |
| Counterfactual executed | ✓ | 5 mutants, §4.1 |
| Restore proven | ✓ | byte-exact on both targets, after the harness bug in §4.2 was fixed |
| Derived, not hand-listed (C-31) | ✓ | the census is parsed from the declaration; the threshold is a product, not a literal |
| Non-activation carries its probe (C-48) | ✓ | `AT-P07` asserts the correction names the input-set error **and** where the pins live |
| Operator rider honoured | ✓ | `LLR-PERF.1` asserts **no** budget; the measurement is printed, §1.1 |
