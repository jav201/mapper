# Requirements ledger — mapper — Batch 2026-10-09-canon-batch

> Append-only. Entries are added in chronological order and never rewritten. The live
> contract is `01-requirements.md`; this file records how it came to say what it says.
> Every entry names the requirement it amends; every requirement names its entries. `V26`
> compares the two sets of pairs both ways.

_No entries yet. The first amendment to the live contract writes the first one, in the
shape the field guide's §7 shows (`req-template.md` in the guide directory init prints), and nothing
above this line is ever edited._

### LED-2026-10-09-canon-batch.1 — ARCH-1 (major): the close fold folds this batch's CAN rows, not the HYG rows
- **Requirement:** HLR-CAN.1
- **Date:** 2026-10-09
- **What changed:** §6.2 now states that the close fold appends five `CAN` rows. The PLAN B4 control is corrected. The HYG rows are verified by AT-063.
- **Why:** `fold_canon` iterates the active batch's declared headings only (`devflow-init.py`). The plan expected `kept` for the HYG ids, which the fold never reads.
- **Evidence:** 02-review.md round 1, ARCH-1.

### LED-2026-10-09-canon-batch.2 — QA-2 / ARCH-2 (major): "equals" is pinned to the fold's full normalisation
- **Requirement:** HLR-CAN.1, LLR-CAN.1.1
- **Date:** 2026-10-09
- **What changed:**
  - The statement cell is pinned to N(record) + ` (Record id: <id>.)`. N's four rules are listed, and the test keeps them as its own literals.
  - The escaped-pipe boundary (`LLR-001.1`) is added.
  - A stripped-suffix control is added.
- **Why:** "equals" was under-specified. A test that reused the writer's normaliser could not go RED on normaliser drift.
- **Evidence:** 02-review.md round 1, QA-2 and ARCH-2; `devflow-init.py` `_statement`.

### LED-2026-10-09-canon-batch.3 — QA-3 / ARCH-3 (minor): non-vacuous table parse; the guard's scope is stated
- **Requirement:** HLR-CAN.1, LLR-CAN.1.2
- **Date:** 2026-10-09
- **What changed:**
  - The test anchors on the `| Id |` header and reads only the first cell.
  - It requires at least 82 rows and exactly 5 record headings.
  - The rationale says that the uniqueness check is a regression net, not a B-105 detector.
- **Why:** without these, the test could pass over an empty set, and the rationale overstated what the guard catches.
- **Evidence:** 02-review.md round 1, QA-3 and ARCH-3.

### LED-2026-10-09-canon-batch.4 — QA-1 / QA-4 / QA-5: AT-064's oracle, the import boundary catalog, the re-export rule
- **Requirement:** HLR-CAN.2, LLR-CAN.2.1
- **Date:** 2026-10-09
- **What changed:**
  - AT-064's oracle is the AST test, and `ruff` is separate, attributed evidence (`not-run` if absent).
  - The boundary catalog now covers `__future__`, Name loads and attribute bases, strings not counting, and synthetic-source arms.
  - Star imports and `__all__` are out of scope.
  - A future re-export goes on an explicit allowlist.
- **Why:** the stated observable (`ruff`) was not what the AT executes, and `ruff` is not a declared dependency. The catalog missed cases that would false-positive.
- **Evidence:** 02-review.md round 1, QA-1, QA-4 and QA-5.

### LED-2026-10-09-canon-batch.5 — correction of .3: the row floor is 134, not 82
- **Requirement:** HLR-CAN.1, LLR-CAN.1.2
- **Date:** 2026-10-09
- **What changed:** the row floor is now at least 134 (129 + 5). Entry .3 said 82; this entry supersedes that figure.
- **Why:** the 82 came from the qa-reviewer's count of 77 rows. Counting the rows from the `| Id |` header to the end of the table gives 129. The architect's figure was also 129.
- **Evidence:** `awk '/^\| Id \|/{f=1;next} f&&/^\|---/{next} f&&/^\|/{n++} f&&!/^\|/{f=0} END{print n}' REQUIREMENTS.md` → `129`.

### LED-2026-10-09-canon-batch.6 — P2 round 2 (minor NEW-1): US-002's wording follows the AT-064 oracle
- **Requirement:** HLR-CAN.2
- **Date:** 2026-10-09
- **What changed:**
  - US-002's benefit clause no longer promises `ruff`-clean output.
  - Its evaluability names the AST test as the oracle, with `ruff` as corroboration.
- **Why:** after LED .4, the story still stated the `ruff` output as the observable. That contradicted HLR-CAN.2.
- **Evidence:** 02-review.md round 2, NEW-1.
