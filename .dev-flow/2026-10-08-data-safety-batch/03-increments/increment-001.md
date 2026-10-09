# Increment 001 — US-004 / HLR-009 · `FLAKE-2 deflake: immediate scroll + injected-delay regression`

> Batch-plan name: **Inc-3**. The file is `increment-001.md` because it is the first increment packet written into this batch's `03-increments/` home (Inc-1a/1b/2 are not yet delivered).

| Field | Value |
|---|---|
| Batch | `2026-10-08-data-safety-batch` |
| Increment | `001` (plan name Inc-3) |
| Lane (if the batch forked) | none · worktree `mapper-inc3`, branch `inc3/flake2`, base `fc2e4c9` |
| Requirement(s) | US-004 · HLR-009 · LLR-009.1 · LLR-009.2 · design rows 3.1–3.3 · PDR condition C12 |
| Acceptance | AT-008 · white-box TC-009.2 · unit — none (test-instrument change only) |
| Agent | `software-dev` |
| Date | 2026-10-08 |

---

## 1 · What changed

The legend own-keys test no longer races a queued scroll. The four `scroll_to(..., animate=False)` sites now pass `immediate=True` and assert the settled offset before anything is sampled (design 3.1). The own-keys loop is lifted into `_effective_keys(app, pilot, screen)` (+ `_painted_own_keys`) and is run by both the existing node and a new injected-delay arm (3.2). The fixture `delay_deferred_scroll` plus the `late_scroll()` window (3.3, adapted from `spike/red_green_flake2.py`) makes only the test's own queued `_scroll_to` land 150 ms late. Per C12 each of the other three sites also got a delayed-scroll arm. 0 source files, 8 new nodes.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `tests/test_help_scope.py` | test | US-004, HLR-009, LLR-009.1, LLR-009.2, AT-008 | `delay_deferred_scroll` fixture + `late_scroll()`; `_harvest` (was `:93`) immediate + settle assert; `_effective_keys` / `_painted_own_keys` lifted from the n16_4 node (was `:365`), node now calls them; new nodes: `test_at_008_…` x3 sizes, fixture RED-proof node, `_harvest` arm, `_painted_bindings` arm |
| `tests/test_repair_layout.py` | test | US-004, HLR-009, LLR-009.1 | `_painted_bindings` (was `:118`) immediate + settle assert |
| `tests/test_en7.py` | test | US-004, HLR-009, LLR-009.1 | body of `test_the_painted_legend_ends_with_the_rule` (was `:246`) lifted to `_footer_text_at_the_end` with immediate + settle assert + `target > 0` guard; new `…_under_a_late_scroll` arm x2 sizes |
| `.gitattributes` | config | HLR-009 | `.dev-flow/*/evidence/** -text` so stored evidence keeps its bytes (template, §Evidence files) |
| `.dev-flow/2026-10-08-data-safety-batch/evidence/*` (5 files) | doc | | transcripts + the mutation driver `inc3-mutate.py` |
| `.dev-flow/2026-10-08-data-safety-batch/03-increments/increment-001.md` | doc | | this packet |

| Count | Value |
|---|---|
| **SOURCE files** | **0** / 4 |
| Test files | 3 (uncapped) |
| Doc files | 6 (outside the count); 1 config |

---

## 3 · How to test

```bash
cd <worktree>   # mapper-inc3
python -B -W error::SyntaxWarning -m pytest -q -rf -p no:cacheprovider tests/test_help_scope.py tests/test_en7.py tests/test_repair_layout.py
python -B -m pytest -q -p no:cacheprovider tests/test_help_scope.py -k "n16_4 or at_008"
python -B -W error::SyntaxWarning -m pytest -q -rf -p no:cacheprovider      # default lane, ~24 min
python -B .dev-flow/2026-10-08-data-safety-batch/evidence/inc3-mutate.py S1-imm   # one mutant: apply, run, restore, sha-verify
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | n/a — no cyclomatic >=3 production code; test-instrument change | n/a |
| **A · white-box** `TC-009.2` ↔ LLR-009.1/009.2 | `core` · `full` | `test_help_scope.py::test_at_008_…[size0..2]`, `::test_the_delay_fixture_delays_…`, `::test_llr_009_1_…harvest…`, `::test_llr_009_1_…bindings…`, `test_en7.py::test_the_painted_legend_ends_with_the_rule_under_a_late_scroll[size0,1]` | 8 passed (new) |
| **B · black-box** `AT-008` (test-instrument check) | `core` · `full` | `test_help_scope.py::test_at_008_the_own_keys_loop_is_deterministic_under_a_late_scroll[size0..2]` | 3 passed |

Touched files, fully: `tests/test_help_scope.py tests/test_en7.py tests/test_repair_layout.py` gave 101 passed (base 93 + 8), 74.95 s. Python 3.12.7, Textual 8.2.8, executed.

**Default lane (executed once, whole tree, at the final code):** `python -B -W error::SyntaxWarning -m pytest -q -rf -p no:cacheprovider` finished with exit code 1 and `1 failed, 2804 passed, 24 deselected, 3 xfailed in 1432.01s (0:23:52)`. The one failure is **not caused by this increment**: `tests/test_repair_golden_census.py::test_at_p07_trigger_b3_is_recorded_fired_and_not_merely_flipped` asserts `"B3"` is in `.dev-flow/state.json["triggers"]["fired"]`. That node reads batch state only, this increment touches neither it nor `state.json` (unmodified on the branch), so it fails on the base commit `fc2e4c9` for the same reason (state.json was re-seeded for this batch). Not fixed here (out of scope); see §6. Selected count: 2800 base, 2808 post = 2804 passed + 1 failed + 3 xfailed.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | `tests/test_help_scope.py`, `_effective_keys` (the former `:365` site): `pane.scroll_to(y=target, animate=False, immediate=True)` becomes `…animate=False)`, settle assert kept |
| Instrument | project code: `evidence/inc3-mutate.py` (Python driver: apply a unique byte-anchored replacement, run the nodes, restore from saved bytes, compare sha256) |
| Where it ran | my own worktree `mapper-inc3` |
| Transcript | `evidence/inc3-red-counterfactual.transcript`: `test_at_008_…[size0] FAILED`, `[size1] FAILED`, `[size2] FAILED` with `AssertionError: the positioning scroll did not land`; `test_hlr_n16_4…[size0..2] PASSED` (no delay, so the node alone is blind, which is the point of the arm); fixture node PASSED; `3 failed, 4 passed`. Mutation applied: `changed: True` |
| Restore proven by | before `33020b287ab3963336dbc48301eb2b5d015dd1df9cab6c67c27597c4ce2a5094`, mutated `00b39e0c382e2153f1ae5fb874262ba8f72e230bdc23bbeed1732a7c511b31d9`, after restore `33020b28…5094`, `restored: True` |
| Bytecode cache | `python -B` on every run (C-46) |
| Arms resolved at baseline | 7 (3 at_008 + 3 n16_4 + 1 fixture node), asserted by the 7 verdict lines |
| Verdict granularity | per resolved node id (the driver parses `pytest -v`) |
| Arms that stayed GREEN | `test_hlr_n16_4…[size0..2]` and the fixture node, as expected: no delay is injected there |

| Field | Value |
|---|---|
| **RED counterfactual** | `_effective_keys` `immediate=True` removed: `test_at_008_…[size0,size1,size2]` RED (settle assertion); transcript `evidence/inc3-red-counterfactual.transcript`; restore digest `33020b28…5094` equals the pre-mutation digest. Removing BOTH `immediate=True` and the settle assert (the original FLAKE-2 step, S1-both) turns the same 3 arms RED with the spike's own failure: `work but not painted: ['right']; painted but inert: ['home','pagedown','pageup']` (size2), `painted but inert: ['end','home','pagedown','pageup']` (size0, size1). The arm therefore detects the race itself, not only the added assert |

### Mutation verdicts — per resolved node (`evidence/inc3-mutation-battery.transcript`, `…-battery-2.transcript`; every mutant restored, digest checked `restored: True`)

Pre-mutation digests (each equals its restore): `test_help_scope.py` 33020b28…5094 · `test_repair_layout.py` f6cd73aa…9b59 · `test_en7.py` a6853ba5…a193da (full values in the transcripts).

| Mutant | Mutation (position · operation) | Nodes run | Verdict | Arms that stayed GREEN / reason |
|---|---|---|---|---|
| S1-imm | `_effective_keys` drop `immediate=True` | at_008 x3, n16_4 x3, fixture | **KILLED** (at_008 x3) | n16_4 x3, fixture (no delay there) |
| S1-both | `_effective_keys` drop `immediate=True` and settle assert (original step) | same 7 | **KILLED** (at_008 x3, spike message) | n16_4 x3, fixture |
| S1-assert | `_effective_keys` drop settle assert only | same 7 | **SURVIVED** | all 7. Equivalent while `immediate=True` holds: the assert can only fire if the setup scroll did not land, and `immediate` guarantees it does. Kept as the fail-loud guard (HLR-009 error boundary) |
| S1-halfwin | `_effective_keys` close the `late_scroll()` window | same 7 | **SURVIVED** | all 7. Equivalent: with `immediate=True` nothing is queued, so the window is inert; it matters only for the regression, covered by S1-imm |
| F-off | fixture never delays (`False and …`) | at_008 x3, fixture | **KILLED** (fixture node) | at_008 x3 GREEN: blind without a delay; the fixture node is the instrument RED-proof |
| F-zero | fixture delay 0.15 to 0.0 | at_008 x3, fixture | **KILLED** (fixture node) | at_008 x3 |
| F-always | fixture delays outside the window | at_008 x3, n16_4 x3, fixture | **KILLED** (at_008 x3 `work but not painted: ['left']…`, and the fixture node) | n16_4 x3 (fixture not installed there) |
| S2-imm | `_harvest` drop `immediate=True` | harvest arm | **KILLED** | none |
| S2-both | `_harvest` drop `immediate=True` and settle assert (original step) | harvest arm | **SURVIVED** | arm GREEN: `_harvest` reads a UNION over positions and re-derives its step from the live offset, so a late landing costs a stale duplicate read, never a wrong result. The ORIGINAL `_harvest` is not observably flaky under the delay; the new assertion is hygiene, killed only through S2-imm |
| S2-assert | `_harvest` drop settle assert only | harvest arm | **SURVIVED** | equivalent while `immediate=True` holds |
| S2-min | `_harvest` assert `== min(target, max)` becomes `== target` | harvest arm | **KILLED** | the clamp is load-bearing: the last step overshoots |
| S3-imm | `_painted_bindings` drop `immediate=True` | bindings arm | **KILLED** | none |
| S3-both | `_painted_bindings` drop both (original step) | bindings arm | **SURVIVED** | same union-read reason as S2-both |
| S3-assert | `_painted_bindings` drop settle assert only | bindings arm | **SURVIVED** | equivalent |
| S3-min | `_painted_bindings` drop `min()` clamp | bindings arm | **KILLED** | none |
| S4-imm | en7 drop `immediate=True` | late arm x2, plain node x2 | **KILLED** (late arm x2, `the legend did not scroll to its end`) | plain node x2 (no delay) |
| S4-both | en7 drop `immediate=True` and settle assert (original step) | same 4 | **SURVIVED** | arms GREEN: the footer is a docked widget outside the scrolling pane, its text does not depend on the pane offset, so the original site cannot race into a wrong result |
| S4-assert | en7 drop settle assert only | same 4 | **SURVIVED** | equivalent |
| S4-guard | en7 drop `target > 0` guard | same 4 | **SURVIVED** | the legend scrolls at both sizes today; the guard protects the premise of the arm, not a behaviour (load-bearing emptiness, below) |
| S4-guard-inv | en7 `target > 0` becomes `target > 10000` | same 4 | **KILLED** (4 failed) | proves the guard can fire |

**C12 verdict for the other three sites (`:93`, `:118`, `:246`).** A delayed-scroll arm exists for each and goes RED when `immediate=True` is removed (S2-imm, S3-imm, S4-imm KILLED). Declared surviving mutants, with the reason: for each of those three sites the **pre-fix step itself** (S2-both, S3-both, S4-both) survives. The old code was never observably flaky there (union read / docked footer), so those arms certify the new settle assertion, not a fixed race. The only site with a genuine race is `:365` (S1-both KILLED, reproducing the spike's message). Also surviving, all equivalent: S1-assert, S1-halfwin, S2-assert, S3-assert, S4-assert.

| Field | Value |
|---|---|
| **Mutation verdicts** | 20 mutants run per resolved node: 11 KILLED, 9 SURVIVED (all declared above with reason), 0 CRASH, 0 BAD; transcripts `evidence/inc3-mutation-battery.transcript`, `evidence/inc3-mutation-battery-2.transcript`, `evidence/inc3-red-counterfactual.transcript` (S1-imm); each restore digest returned to the pre-mutation value |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `delay_deferred_scroll` fixture | F-off (condition forced `False`), F-zero (delay 0), F-always (no window) planted in its MECHANISM | `test_the_delay_fixture_delays_a_queued_scroll_only_inside_the_window FAILED`, `AssertionError: the fixture did not delay the queued scroll` (battery transcript) |
| `_effective_keys` + at_008 arm | the original unfixed step (S1-both) | `work but not painted: ['right']; painted but inert: ['home', 'pagedown', 'pageup']` (battery transcript) |
| `evidence/inc3-mutate.py` | an anchor that is not unique prints `BAD`; every run prints `changed: True` for the mutated digest and `restored: True` after | all 20 runs show `changed: True` then `restored: True` |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 3 instruments, each shown RED before its first PASS was believed |

### Emitted-form assertion

| Field | Value |
|---|---|
| **Emitted-form assertion** | none — this increment emits no artifact beyond the evidence transcripts. The default-lane transcript was post-processed: the operator's profile path prefix is replaced by `<USERPROFILE>` in 11 places (batch guard A-110); counts and tail are unchanged |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED counterfactual transcript | `.dev-flow/2026-10-08-data-safety-batch/evidence/inc3-red-counterfactual.transcript` | `03ade731a1ec308d6a0bdaeb283d7530b0b76986f86f91ec47402f4e4f31534a` |
| Mutation battery 1 (18 mutants) | `.dev-flow/2026-10-08-data-safety-batch/evidence/inc3-mutation-battery.transcript` | `1e1f216d28e28c4bf765edc4bfe72ed4223bf37cc3d291da4fc3794a9bfd18ad` |
| Mutation battery 2 (S4-guard-inv) | `.dev-flow/2026-10-08-data-safety-batch/evidence/inc3-mutation-battery-2.transcript` | `022ff218c10d97b739e91adb19f6139479f578d421180b17dba3ce8932fa88d7` |
| Mutation driver | `.dev-flow/2026-10-08-data-safety-batch/evidence/inc3-mutate.py` | `4c635d59eade7cfc2bcec3a5088c660f12a9890c3264827226fc25e266dd39d9` |
| Default-lane transcript (path-scrubbed; last line `EXIT_CODE=1` appended by the wrapper) | `.dev-flow/2026-10-08-data-safety-batch/evidence/inc3-default-lane.transcript` | `064869c63f6634d6ac2b2ca693ba254ef9b9d02d99b0a26282d8024320fad6b2` |

The touched-files run (101 passed) is not stored as its own file; the lane transcript covers those nodes. `.gitattributes` marks the evidence `-text`.

| Field | Value |
|---|---|
| **Evidence files** | 5 artifacts at the declared home with the digest of their working-tree bytes; the index-blob digests are re-checked after commit (see §6) |

### Load-bearing emptiness

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — "the legend scrolls at every tested size" (`max_scroll_y > 0`); if the legend ever fits, the delayed scroll is a no-op and the arms pass vacuously |
| If the result is an ABSENCE, what made the search wide enough | not an absence search |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `assert target > 0` in `_footer_text_at_the_end`; `assert pane.max_scroll_y > 2` in `_effective_keys` and the two C12 arms; S4-guard-inv shows the guard can fire |
| Conjunctive criteria: one mutation per conjunct | settle assert (S*-assert), `immediate` (S*-imm), clamp (S2/S3-min), window (S1-halfwin): verdicts above |
| Synthetic instance of the absent case | none built; a legend that fits is not constructible without changing product content |
| **Positive control for every probe that returned an ABSENCE** | n/a — no absence probe |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by other tests | `grep -rln "_harvest" tests/` | `test_help_scope.py` (owner), `test_inc9.py`, `test_inc9c.py` (import it), `test_legend_design.py` (a node name only); all green in the default lane. `_painted_bindings`: only `test_repair_layout.py` (2 callers) and the new arm. `grep -rn "_effective_keys\|_painted_own_keys" tests` outside `test_help_scope.py`: 0 hits |
| B2 file moved on disk | none moved | n/a |
| B3 goldens capture this source | `git ls-files \| grep -c goldens` | 0 tracked golden files |
| B4 artifact consumed elsewhere | `grep -rln "test_help_scope import\|test_en7 import" tests` | `test_inc9.py`, `test_inc9c.py` (`_harvest`), and the new `test_en7.py` import of the fixture |
| A3 interface consumed by another module | `_harvest` signature unchanged | 2 importers re-validated in the lane |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1, B2, B3, B4, A3); 3 hits re-validated green in the default lane; none fired a defect |

### Correction population

| Correction | Population | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| a queued `scroll_to(..., animate=False)` sampled before it landed | every `scroll_to(` call in tests | `grep -rn "scroll_to(" tests` (run before editing) | 4 | 4 (`test_help_scope.py:93`, `:365`; `test_en7.py:246`; `test_repair_layout.py:118`) | 0 |

| Field | Value |
|---|---|
| **Correction population** | 1 correction enumerated with its method before the first site was edited (4 sites, 4 edited) |

### Signed-balance test ledger

`post = base − deleted + added` gives `2808 = 2800 − 0 + 8` ✓ reconciles. Default-lane selected; base measured by `--collect-only` at `fc2e4c9`: `2800/2824 tests collected (24 deselected)`; post: 2804 passed + 1 failed + 3 xfailed = 2808. Per touched file: 93 to 101 (test_help_scope 44 to 52, test_en7 31 to 33, test_repair_layout 18 to 18).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | ABSENT — not yet run; owed by the orchestrator (`code-reviewer`) |

---

## 5 · Risks

- The fixture patches `Widget.call_after_refresh` and keys on the callback name `_scroll_to`; a Textual upgrade that renames it makes `delay_deferred_scroll` inert. The fixture RED-proof node fails loud in that case (F-off).
- Pass rate of the fixed node under real CPU load was not re-measured (the spike's `repeat_flake2.py` loop was not re-run); the determinism evidence is the injected delay, not statistics.
- Only Python 3.12.7 / Textual 8.2.8 / one machine.
- Importing the fixture into `tests/test_en7.py` couples it to `tests/test_help_scope.py` (already the pattern for `_harvest`).

---

## 6 · Pending items / spec deviations

- **Default lane is not green on the base either:** `tests/test_repair_golden_census.py::test_at_p07_trigger_b3_is_recorded_fired_and_not_merely_flipped` reads `.dev-flow/state.json` triggers, which the new batch's init reset (`B3` not in `fired`). The orchestrator must rule: restore the trigger record or retire the test. Not touched here.
- Design 3.1 asks for the settle assert at all four sites; done. At `:93`/`:118` it sits after the two pauses and clamps with `min(target, max_scroll_y)` (S2-min/S3-min show the clamp is needed).
- Surviving mutants S2-both, S3-both, S4-both: those three sites were not observably flaky before; no further arm can make them so.
- After commit: re-derive the evidence digests from the index blobs (`git show :<path> | sha256sum`).

---

## 7 · Suggested next task

Orchestrator ruling on the `test_at_p07` state.json failure, then `code-reviewer` on this diff (§4b), then merge `inc3/flake2` and proceed to the next planned increment.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 0 source files, 3 test files (§2) |
| 2 | Tests written in this same increment | all | ✓ | 8 new nodes, 93 to 101 in the touched files |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | n/a — test-instrument change, no production logic |
| 4 | RED counterfactual declared | `core` · `full` | ✓ | S1-imm 3 arms RED, `evidence/inc3-red-counterfactual.transcript`, restore digest `33020b28…5094` |
| 5 | Reverse census declared | `core` · `full` | ✓ | §4 Reverse census, 5 probes |
| 6 | `code-reviewer` passed | `core` · `full` | ⚠ | not yet run (§4b ABSENT) |
| 7 | No file from another lane touched | all | ✓ | only 3 test files, 1 config, `.dev-flow` batch dirs; `mapper/`, `prototypes/`, `mapper.db`, `fixtures/.mapper/` untouched |
| 8 | Frozen interfaces untouched | all | ✓ | no source file changed |
| 9 | Coverage claims verified on disk | all | ✓ | counts from `--collect-only` and the stored lane transcript |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 Load-bearing emptiness |
| 11 | Mutation verdicts declared per arm | all | ✓ | 20 mutants, 11 KILLED / 9 SURVIVED declared |
| 12 | Instrument RED-proof declared | all | ✓ | 3 instruments |
| 13 | Correction population declared | all | ✓ | 4 sites enumerated by grep before editing |
| 14 | Emitted-form assertion declared | all | ✓ | none — with the path-scrub note |
| 15 | Independent review names somebody | all | ⚠ | ABSENT, owed |
| 16 | Evidence files declared with stored digests | all | ✓ | 5 files; index-blob re-check listed in §6 |
