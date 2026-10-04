# Increment 017 — the 2026-09-19 rulings applied · `A-100.1` · `A-100.2` · `A-100.3`

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Increment | `017` — the coordinator's rulings on increment 016's confirmation round |
| Lane (if the batch forked) | `none — batch not forked` |
| Requirement(s) | `A-100.1`, `A-100.2`, `A-100.3` (amendment set 9) · parent: `A-100` |
| Acceptance | `test_a_refusal_DECLARES_the_stale_artifact_it_leaves_behind` · `test_a_refusal_on_a_FIRST_export_claims_no_stale_file` · `test_no_rendered_row_is_folded_in_the_artifact[20-枝 {}]` / `[40-分岐 {}]` · `test_the_spawn_census_sees_an_undeclared_binary_in_EITHER_SPELLING[positional|keyword-argv]` · `test_the_spawn_census_positive_control_returns_a_NON_absence` |
| Agent | `software-dev` |
| Date | 2026-09-19 |

---

## 1 · What changed

**Four rulings applied. None of them widened scope, and the one that could have — deleting the
operator's stale file — was ruled against on a standing rule rather than on taste.**

**`A-100.1` — the export budget's derivation is STRUCK; the constant stands.** Both independent
passes of increment 016 raised it from opposite directions and **their conclusions disagreed by 6×**,
so it was re-measured rather than resolved by picking a reviewer. The mechanism: both cost harnesses
call `tracemalloc.start()` on the line *before* `t0`, so an allocation profiler ran inside the whole
timed region and inflated every point by 5.3–5.6×. **Both the struck `4.907 µs/cell` and its
`5.4264` replacement came from that same instrument** — the correction changed the number and kept
the instrument. `EXPORT_MAX_CELLS = 350_000` is unchanged and now rests on **the worst shape the
budget admits** (1.447 s against a 2-second target, ≈28 % margin) and carries **no rate at all**,
because cost spans 0.955–3.27 µs/cell across admitted shapes. A proposed 6× relaxation was REFUSED:
it generalised from the cheap shape family.

**`A-100.2` — a refusal now declares the stale artifact it leaves behind.** Refusing to write leaves
the *last* export's file at the very path the success toast names. The operator was told the export
declined, but not that the file still there is old — `B-68`'s own shape one seam over. **Declared,
not deleted:** the standard is that nothing is hidden without being declared, not that nothing stale
exists, and deleting the operator's file on a refusal without confirmation is the destructive act
`US-N05` already rules against. The sentence is **conditional**, because on a first export there is
no file to be stale and a claim about the world must not be false.

**`A-100.3` — two instrument gaps closed, both the same shape.** `S-F10`: `cell_len` was correct and
**unpinned** — substituting `len()` left 45 tests green while CJK titles fold. `S-F11`: the AST spawn
census read **positional** argv only, so the identical undeclared spawn failed the census written
positionally and passed it written `subprocess.run(args=[...])`. Both are *a lesson applied to an
instance and not to its class*, landing in the instrument rather than the product.

**Recorded as the SIXTH instance** of *the increment that closes a defect family is the increment
most likely to introduce a member of it* — `A-100.2`, **with its mitigation stated**: the operator
was told the export refused, just not that the old file persists. Partial mitigation is still an
instance; precision beats inflating the tally and beats suppressing it.

---

## 2 · Files modified

| File | Kind | Change |
|---|---|---|
| `mapper/app.py` | source | the `ExportTooLarge` handler declares the stale artifact, conditionally; `EXPORT_MAX_CELLS`'s per-cell derivation struck and re-grounded; the two contaminated seconds-figures in the `MAX_RENDER_NODES` paragraph struck and replaced by the cell ratio |
| `tests/test_export_state.py` | test | wide-glyph parametrisations (`S-F10`); the stale-declaration arm and its false-claim negative control (`A-100.2`) |
| `tests/test_hermetic.py` | test | `_spawn_argv` reads positional **and** `args=` argv; `_derived_spawn_executables` takes a `root` so an arm can drive the real census; the both-spellings arm and a positive control (`S-F11`) |
| `.dev-flow/…/01-requirements.md` | doc | Amendment set 9 — `A-100.1`, `A-100.2`, `A-100.3`; `A-100`'s normative budget clause amended in place |
| `.dev-flow/state.json` | doc | new control minted; catalog entry 1's own third exhibit corrected; entry 15 gains the recurrence and two extensions; the `urllib` citation struck |
| `.dev-flow/…/increment-016-confirm-reruled.md` | doc | the lane-guard bullet corrected in two places |

| Count | Value |
|---|---|
| **SOURCE files** | **1 / 4** (`mapper/app.py`) |
| Test files | 2 (uncapped) |
| Doc files | 4 (outside the count) |

---

## 3 · How to test

```bash
cd C:/Users/<operator>/Github/mapper
set PYTHONUTF8=1 && set PYTHONIOENCODING=utf-8

python -m pytest -q                     # default lane
python -m pytest -q -m slow
python -m pytest -q -m network
python -m ruff check --isolated --output-format=concise mapper tests

python -m pytest tests/test_export_state.py tests/test_hermetic.py -q
```

---

## 4 · Test results

| Lane | Exit | Tail |
|---|---|---|
| default | **0** | `1140 passed, 20 deselected, 3 xfailed in 371.97s` |
| slow | **0** | `19 passed, 1144 deselected in 58.76s` |
| network | **0** | `1 passed, 1162 deselected in 0.35s` |
| ruff | — | **27 findings, SETS EQUAL AT EQUAL SCOPE** vs `a552783`; both parses asserted non-empty (27/27, added 0, removed 0) |

### Signed-balance test ledger

`post = base − deleted + added` → **`1140 = 1133 − 0 + 7`** ✓ reconciles.
Added, itemised: 2 wide-glyph fold params · 2 `A-100.2` arms · 2 census-spelling params · 1 census
positive control. Deselected unchanged at 20; xfailed unchanged at 3.

### Mutation battery — 5 sites, fired per SITE against the shipped bytes

Baseline asserted green (43 nodes) before the first mutation. Byte-level I/O; sha256 pins; verdicts
printed **before** every restore assert; substitution count asserted at exactly 1 per site;
`PYTHONDONTWRITEBYTECODE=1`; anchors normalised per file's own line ending.

| Site | Expect | Verdict | Reddened — **and the granularity is the result** |
|---|---|---|---|
| `G1` `cell_len` → `len` | KILL | **KILLED** | **only** `[20-枝 {}]` and `[40-分岐 {}]`. The four narrow-title params stayed GREEN — which is precisely why this conjunct was unpinned before |
| `G2` the stale sentence never emitted | KILL | **KILLED** | only `test_a_refusal_DECLARES_the_stale_artifact_it_leaves_behind` |
| `G3` the stale sentence emitted UNCONDITIONALLY | KILL | **KILLED** | only `test_a_refusal_on_a_FIRST_export_claims_no_stale_file` |
| `G4` census reverted to positional argv only | KILL | **KILLED** | **only** the `keyword-argv` param; the `positional` one stayed green — the discriminating pair is real |
| `G5` comment-only negative control | SURVIVE | **SURVIVED** | — |

Restores byte-identical: `export.py` `56773345bc4731f1`, `test_hermetic.py` `853ea0b287b50101`.

**`G2`/`G3` are a pair and neither alone is sufficient.** *It says a stale file is there* and *it
never says so falsely* fail independently, so an affordance that declines owes a pin per half —
here, per half of a conditional claim.

### Instrument RED-proof

| Instrument | Known-bad input | What it reported |
|---|---|---|
| the clean cost harness | the product's own shapes, with `mapper.__file__` asserted | resolved to the shipped tree; the editable-install trap (`S-F14`) is what made the assert necessary |
| the mutation harness | a multi-line `\n` anchor against a CRLF file | `anchor matched 0x, needs exactly 1 — a mutation that never applied reads as a survivor` |
| the spawn census | an empty synthetic tree, then the real product tree | `set()` for the empty tree **and** non-empty for the real one, asserted together, so a broken walk cannot pass |
| the ruff set harness | both sides extracted, both parses asserted non-empty | 27/27, added 0, removed 0 |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Enumeration command | Count | Sites edited |
|---|---|---|---|
| the per-cell derivation of `EXPORT_MAX_CELLS` | `grep -rn "1.801\|5.4264\|4.907\|357,156\|400_000" mapper/ .dev-flow/` | 4 | `mapper/app.py`, `01-requirements.md` (`A-100` clause + set 9), `state.json` (catalog entry 1's own exhibit), this packet |
| *`github.py` already imports `urllib`* | `grep -rn "already imports .urllib" .dev-flow/` | 2 | `increment-016-confirm-reruled.md`, `state.json` |

Both are the **STRIKE** branch: neither was a faithful record taken under an undeclared condition.
The `5.4264` figure is the sharper case — it was itself a *correction*, which is what minted the new
control.

---

## 4b · Independent review

| Field | Value |
|---|---|
| **Independent review** | **NOT YET OBTAINED for this increment.** Increment 016's two passes cleared the tree at `f3398f4`; this increment changes `mapper/app.py` after that clearance, so their verdicts do **not** extend to it. |

**Stated rather than implied.** The rulings applied here were the coordinator's, and a coordinator
ruling is not an independent review — it authorises the change, it does not inspect the
implementation of it. `A-100.2` is a behaviour change in the product's refusal path and `A-100.1`
edits a normative requirement clause, so both are review-bearing. Owed before the whole-branch gate.

---

## 5 · Risks

- **The refusal message is now longer and carries an absolute path.** On a narrow terminal the toast
  may wrap or elide; the path is the operator's own workspace, so it discloses nothing they do not
  have, but a very long workspace path could push the actionable half (`f`) out of view. Not measured
  against a narrow terminal — declared.
- **`A-100.1` re-grounds the constant on a hunt, not a proof.** "The worst shape the budget admits"
  is the right *criterion*, but it was established by searching two shape families across two
  starting heights, not by an argument that no worse admitted shape exists. A third family could
  exceed 2 s while staying under 350,000 cells. The margin (≈28 %) is the headroom against that.
- **The budget remains a static constant against a machine-dependent target.** Unchanged from
  increment 016 and not re-opened here.
- **`FLAKE-1` did not fire in this session's runs**, which carries no information at 2-in-9. Still
  owed at the whole-branch gate, and the next step is capturing the failing ORDER.

---

## 6 · Pending items / spec deviations

1. **Independent review of THIS increment is owed** — see §4b.
2. **Inc-CONFIRM item 3 is still not started**: `F3`→qa, `F7`→ux, `SEC-H2`, `UI-AT058` plus the newer
   `"esta vista no se desplaza"` string, the `B-64` driven sweep over the 31 reachable sites.
3. **`N3` (the SVG reader spelled twice) is NOT fixed here.** It was dispositioned to item 3 and is a
   test-only refactor touching the oracle two acceptance families rest on — moving it in the same
   increment that changes those arms would blur what any failure meant.
4. **`SEC-F4`** (the diff ghost strip) — open MEDIUM, disposition judged ADEQUATE by the
   re-confirmation pass; wants a one-line ruling, not code.
5. **`S-F12`** (`export_neutralised` fails open at runtime), **`S-F15`** (suite needs a git work
   tree), **`N5`/`N6`** — carried, LOW.
6. **The lane guard's bypass residual** — carried; axis recorded **PARTIALLY HELD**, and its citation
   corrected (the import is `urllib.parse` and does no I/O; the carry rests on the argument).
7. **`.gitattributes` / `autocrlf`** — carried to post-merge. The fix is `-text`, never `text eol=lf`.
8. **`artifact_homes.evidence` is still not declared**, so nothing here is evidence under `C-59`.
9. **The validator exits 1** with pre-existing blocks, dispositioned external and non-blocking.

---

## 7 · Suggested next task

**Inc-CONFIRM item 3** — the routed pickups, plus `N3`. `F3` and `F7` are independent-lens items and
dispatch in parallel **to separate mirrors** (entry 15, and its two new extensions). `SEC-H2` and the
`UI-AT058` register check are reads. The `B-64` sweep has its probe at `C:/Users/<operator>/clde/b49_probe.py`
and must DRIVE the derived set rather than a hand-built model of it.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | **1 / 4** — `mapper/app.py` |
| 2 | Tests written in this same increment | all | ✓ | 7 new nodes, itemised in the ledger |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `_spawn_argv` (branching over call forms) driven by the both-spellings parametrisation |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | §4 — 5 sites, 4 KILL all killed, 1 expected survivor |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | `grep -rn "_spawn_argv\|_derived_spawn_executables" tests/ mapper/` → owner module only; `EXPORT_MAX_CELLS` consumers re-validated by the lane |
| 6 | `code-reviewer` passed — a HIGH blocks | `core` · `full` | **✗ OWED** | §4b — not obtained for this increment; 016's clearance does not extend past `f3398f4` |
| 7 | No file from another lane touched | all | ✓ | batch not forked |
| 8 | Frozen interfaces untouched | all | ✓ | `IRenderer.render` unchanged; `_spawn_argv` is test-local |
| 9 | Coverage claims verified **on disk** | all | ✓ | every figure re-measured this session |
| 10 | Load-bearing emptiness declared | all | ✓ | the census positive control asserts the real tree is non-empty, so `set()` on a synthetic tree is an answer and not a broken walk |
| 11 | **Mutation verdicts** declared — per arm | all | ✓ | §4, per site, with the killed node ids named |
| 12 | **Instrument RED-proof** declared | all | ✓ | §4 — 4 instruments |
| 13 | **Correction population** declared | all | ✓ | §4 — 2 corrections, enumerated before the first edit |
| 14 | **Emitted-form assertion** declared | all | ✓ | the fold arm reads row identity off the emitted SVG, now including wide glyphs |
| 15 | **Independent review** names somebody | all | **✗ OWED** | §4b |
| 16 | **Evidence files** declared | all | ⚠ | `none — this batch declares no artifact_homes.evidence`; declared gap, inherited |
