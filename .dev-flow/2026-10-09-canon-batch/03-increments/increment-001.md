# Increment 001 — HLR-CAN.1, HLR-CAN.2 · `hygiene requirements appended to the canon (B-105); unused import removed (B-104)`

> **Artifact language:** English (`state.json` `language: en`).

> **Owed in.** `core` ✓ · `full` ✓

> **Where this lives:** the **repo**, `.dev-flow/2026-10-09-canon-batch/03-increments/increment-001.md`. It is not synced to the vault.

| Field | Value |
|---|---|
| Batch | `2026-10-09-canon-batch` |
| Increment | `001` |
| Lane (if the batch forked) | n/a — one lane |
| Requirement(s) | `HLR-CAN.1 v1 / LLR-CAN.1.1, LLR-CAN.1.2` · `HLR-CAN.2 v1 / LLR-CAN.2.1` |
| Acceptance | `AT-063` · `AT-064` · white-box `tests/test_requirements_canon.py` (3 nodes), `tests/test_app_imports_used.py` (1 + 13 arms) · unit none |
| Agent | Each worker ran in its own worktree.<br>• **canon test:** DeepSeek (`deepseek-v4-pro`, unit CAN1);<br>• **import test + the `import re` deletion:** Kimi (`kimi-for-coding`, unit CAN2);<br>• **the five canon rows, nits, mutations, record:** the orchestrator (Claude Opus 5.5). |
| Date | `2026-10-09` |

---

## 1 · What changed

**`REQUIREMENTS.md` now lists the five hygiene requirements under collision-free ids, and `mapper/app.py` no longer imports `re`.**

- **The five appended rows.** `HLR-HYG.1`, `HLR-HYG.2`, `LLR-HYG.1.1`, `LLR-HYG.1.2` and `LLR-HYG.2.1` were added at the end of the requirement table.
  - Each row holds the fold-normalised statement of its record heading, followed by `(Record id: <id>.)`.
  - Each row has owner `2026-10-09-hygiene-batch` and status `active`.
  - The change is append-only: `git diff` shows 5 insertions and 0 deletions.
- **AT-063** pins those rows to the record. It carries its own literal copy of the fold's normalisation, so drift on either side turns it RED. It also checks that canon ids are unique and that the table holds at least 134 rows.
- **AT-064** reads `mapper/app.py`'s AST and asserts that every module-level import is used. `ruff check mapper/app.py` now prints `All checks passed!`.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/app.py` | source | HLR-CAN.2, LLR-CAN.2.1 | `import re` deleted (1 line) |
| `REQUIREMENTS.md` | doc | | 5 rows appended (HYG ids) |
| `tests/test_requirements_canon.py` | test | HLR-CAN.1, LLR-CAN.1.1, LLR-CAN.1.2 | new: AT-063, uniqueness/floor, normaliser arms |
| `tests/test_app_imports_used.py` | test | HLR-CAN.2, LLR-CAN.2.1 | new: AT-064 + 13 synthetic arms |

| Count | Value |
|---|---|
| **SOURCE files** | **1 / 4** |
| Test files | 2 (uncapped) |
| Doc files | 1 (`REQUIREMENTS.md`, outside the count) |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_requirements_canon.py tests/test_app_imports_used.py
ruff check mapper/app.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | none — no unit meets the criterion | n/a |
| **A · white-box** ↔ LLR | `core` · `full` | `test_llr_can_1_2_*`, `test_llr_can_1_1_*`, `test_llr_can_2_1_checker_arms` (13) | 15 passed |
| **B · black-box** `AT-NNN` ↔ story | `core` · `full` | AT-063, AT-064 | 2 passed |
| Increment GREEN after the nits | — | both new files | **17 passed** (`inc001-mutation-battery.transcript`, "GREEN after restore") |
| Regression set (before the nits; the nits touched only the two new test files) | — | the canon readers, the `app.py` parsers, the draft suites | **147 passed, 0 failed** (`inc001-regression-set.transcript`) |
| `ruff` corroboration (AT-064) | — | `mapper/app.py` + both new files | `All checks passed!` (`inc001-ruff.transcript`, orchestrator) |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | C0: `REQUIREMENTS.md` set to its base bytes (`git show HEAD:REQUIREMENTS.md`). A1: `import re` restored in `mapper/app.py`. |
| Instrument | `can_mutate.py` (an orchestrator script in the session scratch). Every restore is sha256-checked. |
| Where it ran | the main checkout, with no worker running |
| Transcript | `evidence/inc001-mutation-battery.transcript` |
| Restore proven by | `restored byte-identical: True` after every mutant |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1`, `python -B` |
| Arms resolved at baseline | 3 canon nodes + 14 import nodes = 17 |
| Verdict granularity | per node id (`FAILED` lines named) |
| Arms that stayed GREEN | Under C0, `test_llr_can_1_1_normaliser_pins_the_fold_rules`: by design it tests literals. Under A1, the 13 synthetic arms: they test the checker, not `app.py`. |

| Field | Value |
|---|---|
| **RED counterfactual** | Transcript: `.dev-flow/2026-10-09-canon-batch/evidence/inc001-mutation-battery.transcript`. Every restore is byte-identical.<br>• **C0** (the canon at its base, without the 5 rows) → `test_at_063_*` FAILED (`found 0`) and `test_llr_can_1_2_*` FAILED (`129 >= 134`).<br>• **A1** (`import re` restored) → `test_at_064_*` FAILED (`{'re'} == set()`).<br>The `app.py` mutant's hash, `4b47adcf…`, equals the pre-batch file. |

| Field | Value |
|---|---|
| **Mutation verdicts** | Transcript: `.dev-flow/2026-10-09-canon-batch/evidence/inc001-mutation-battery.transcript`. Every restore is byte-identical.<br>• **C0** (rows absent): KILLED by AT-063 and LLR-CAN.1.2.<br>• **C1** (the `LLR-HYG.1.2` row duplicated): KILLED by AT-063 (`found 2`) and LLR-CAN.1.2 (`duplicate canon ids: ['LLR-HYG.1.2']`).<br>• **C2** (the statement of `HLR-HYG.1` altered): KILLED by AT-063 (`statement drifted`).<br>• **C3** (the `(Record id: LLR-001.1.)` suffix stripped): KILLED by AT-063.<br>• **A1** (`import re` restored): KILLED by AT-064.<br>The arms that stayed GREEN are named in the table above. |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_requirements_canon.py` | the base canon (C0) | `2 failed, 1 passed` |
| `tests/test_app_imports_used.py` | `app.py` with `re` (A1), and the synthetic arms (`import os` → `{"os"}`, etc.) | `1 failed, 11 passed` (A1); the arms assert the expected unused sets |
| `can_mutate.py` | each mutation asserts that it changed the bytes (`mutation did not apply` aborts) | applied 5/5 |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 3 instruments, each shown RED before its first PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the five canon rows in `REQUIREMENTS.md` | AT-063 reads the file from disk and compares each statement cell to N(record) + suffix | passed; C2 and C3 RED |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 1 artifact (the appended rows), asserted on disk |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| inc001-deepseek-unit-report.transcript | .dev-flow/2026-10-09-canon-batch/evidence/inc001-deepseek-unit-report.transcript | 282f3df74231f0e1b723dcb0f67e0c8dd11ffe37394818b0504d04666e571f1d |
| inc001-kimi-unit-report.transcript | .dev-flow/2026-10-09-canon-batch/evidence/inc001-kimi-unit-report.transcript | b65b8805761863faa5d26f2720a3bd156180a01995170c2100f4c3ba7f6a3957 |
| inc001-mutation-battery.transcript | .dev-flow/2026-10-09-canon-batch/evidence/inc001-mutation-battery.transcript | 463e02f6e58afd6d80e472acf840251ee6185a26dd113f2e62e8e9deb7c6cc00 |
| inc001-regression-set.transcript | .dev-flow/2026-10-09-canon-batch/evidence/inc001-regression-set.transcript | bcfa666d905ce4fb0e89e13b027021ceb673f0762a3bbfcf6c1079666baf52f0 |
| inc001-ruff.transcript | .dev-flow/2026-10-09-canon-batch/evidence/inc001-ruff.transcript | 6f23f81c4bdca5fb01baab621e5550c2be031bfc96bdf59a1b13be096c451c14 |

| Field | Value |
|---|---|
| **Evidence files** | 5 artifacts, each at the declared home and cited with the digest of its stored bytes (`devflow-evidence.py --root .`) |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes: "no duplicate canon id" and "no unused import in `app.py`" |
| If the result is an ABSENCE, what made the search wide enough | the whole requirement table (anchored on `\| Id \|`, floor 134) and every module-level import of `app.py` |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_llr_can_1_2_canon_ids_are_unique_and_the_table_is_not_empty`, `test_at_064_app_imports_nothing_it_does_not_use` (both docstrings say so) |
| Conjunctive criteria: one mutation per conjunct | AT-063: present (C0), once (C1), statement (C2), suffix (C3), each killed; owner and status are not mutated separately |
| Synthetic instance of the absent case | C1 (a duplicated row); A1 (`import re`); the synthetic import arms |
| **Positive control for every probe that returned an ABSENCE** | under C1 and A1, the same unmodified tests reported the present cases |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rln "REQUIREMENTS\|import re" tests --include=*.py` | `test_repair_cycles.py` and `test_vocabulary_declaration.py` read batch records, not the canon; both were re-run green in the regression set |
| B2 file moved on disk | none moved | not fired |
| B3 byte-identical golden | no golden directory | not fired |
| B4 artifact consumed elsewhere | `REQUIREMENTS.md` → the flow's `V22` / `--fold-canon` | fired at P0; the close gate re-runs both (PLAN B4 control) |

| A3 | interface consumed by another module changed | `grep -rn "app\.re\b\|from mapper.app import re" mapper tests` | no hits — not fired |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run. B1 had 2 hits, re-validated green. B4 fired and is verified at the close gate. B2, B3 and A3 did not fire. |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| hygiene requirements missing from the canon | every requirement heading of the hygiene record | `grep -n "^### \(HLR\|LLR\)" .dev-flow/2026-10-09-hygiene-batch/01-requirements.md` (P0 premise 3) | 5 | 5 rows appended | none |
| unused imports in `app.py` | every F401 in `app.py` | `ruff check mapper/app.py` (P0 premise 4) | 1 | `app.py:7` | none |

| Field | Value |
|---|---|
| **Correction population** | 2 corrections, each enumerated at P0 before the first site was edited |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| `import re` in `mapper/app.py` | 0 hits | yes | AT-064 green; `ruff` clean |

### Signed-balance test ledger

`post = base − deleted + added` → `2944 = 2927 − 0 + 17`  ✓ reconciles. The count comes from `pytest --collect-only -q`: `2944/2968 tests collected (24 deselected)`. The base, 2927, is the hygiene close count.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, independent of the authors DeepSeek, Kimi and the orchestrator) · APPROVE-WITH-NITS, 0 HIGH / 0 MED / 2 LOW · both folded in, and the battery was re-run after the nits (all KILLED again):<br>• **CR-1:** the record's headings are counted as a list, and exactly 5 unique ones are asserted;<br>• **CR-2:** two arms document the checker's limits: a quoted annotation does not count as a use, and a guarded import is not checked. |

---

## 5 · Risks

- The limits of `unused_imports` are documented by tests (CR-2). A deliberate re-export, or a name used only in a quoted annotation, goes through `ALLOWED_UNUSED` with a reason.
- B-105's failure mode (an id reused and never appended) is not detected by anything in the repo. The flow-side fix is the operator's decision (§6.3 of the contract).

## 6 · Pending items / spec deviations

- The orchestrator removed a duplicate `import pytest` from the worker's file before review.
- None open.

## 7 · Suggested next task

P4: full suite. Then the core close, where the close fold is expected to fold the five `CAN` ids.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 1 / 4 |
| 2 | Tests written in this same increment | all | ✓ | 2 new test files |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | n/a — no unit meets the criterion |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | C0, A1 (§4) |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 5 probes |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | one lane |
| 8 | Frozen interfaces untouched | all | ✓ | none frozen |
| 9 | Coverage claims verified **on disk** | all | ✓ | 17 passed; 2944 collected |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 |
| 11 | **Mutation verdicts** declared | all | ✓ | C0–C3, A1 KILLED |
| 12 | **Instrument RED-proof** declared | all | ✓ | 3 instruments |
| 13 | **Correction population** declared | all | ✓ | 2 corrections |
| 14 | **Emitted-form assertion** declared | all | ✓ | canon rows on disk |
| 15 | **Independent review** names somebody | all | ✓ | `code-reviewer` |
| 16 | **Evidence files** declared | all | ✓ | 5 files with sha256 |
