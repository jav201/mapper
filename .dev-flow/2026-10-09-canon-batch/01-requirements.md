# Requirements Document — mapper — Batch 2026-10-09-canon-batch

> **Artifact language**
> This template is the canonical **English scaffold**. Generate the artifact in the batch's development language (`state.json` `language`). For Spanish batches, translate the **prose** — section headers and guidance — **and never a label**, and use `deberá` as the normative keyword (≡ `shall`). The normative RULES in this preamble are **language-independent** and enforced regardless of artifact language.

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/docs/req-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

> **Reserved field names.** The **field names and block keywords below are language-independent** — the
> validator parses them literally and they are never translated:
> `Validation` · `Acceptance test(s)` · `Boundary catalog` · `Negative control` · `Premise evaluation` · `Fork preconditions` · `Ledger` · `Requirement` · `⏸ DEFER`
> Everything else on this page — headings, guidance, the prose in every cell — is translated with the batch.
> **One strategy, not two:** the flow ships no alias table, so a translated label is read as an ABSENT one and the rule keyed on it reports a true-sounding silence.
> **And one FLOW-WIDE reserved token, read out of this artifact by `V42` no matter which template minted it:** `⏸ DEFER`. It is a MARKER rather than a field name, which is why it is stated here *and* in `/dev-flow` §Language of artifacts rather than in a per-template list — a deferral can be written in any batch artifact, including the ones that carry no block at all.

---

## 1. Introduction

### 1.1 Purpose
Close B-105 and B-104:
- **B-105:** the requirements of `2026-10-09-hygiene-batch` are absent from the canon, because their ids collided with `2026-10-08-data-safety-batch`'s.
- **B-104:** a pre-existing unused import, `re` at `mapper/app.py:7`.

### 1.2 Scope
In scope:
- append five rows to `REQUIREMENTS.md`, one per hygiene requirement, under namespaced ids, each naming the id its record uses;
- remove `import re` from `mapper/app.py`;
- two guard tests.

From this batch on, requirement ids are namespaced: this batch uses `CAN`.

Out of scope:
- rewriting any existing canon row or any sealed batch record;
- the flow-side fix (the template seed and the fold), which is reported to the operator for the flow's own backlog;
- B-102.

### 1.3 Definitions, acronyms, abbreviations
| Term | Definition |
|------|------------|
| canon | `REQUIREMENTS.md`: one row per requirement id, with its statement, owning batch and status (`artifact_homes.requirements_canon`) |
| record id | the id a requirement carries in its own batch record (`HLR-001`, …) |
| canon id | the id a requirement carries in the canon; for the hygiene batch, `HLR-HYG.1`, … |

### 1.4 References
- `.dev-flow/BACKLOG.md` B-104, B-105.
- `.dev-flow/2026-10-09-hygiene-batch/05-close.md` §2.
- `.dev-flow/2026-10-09-hygiene-batch/01-requirements-ledger.md` LED .7 is not present. The rename was reverted, as `05-close.md` §2 explains.

### 1.5 Document overview
- §2: stories and premises.
- §3: HLR.
- §4: LLR and the IFC.
- §5: validation.

---

## 2. Overall description

### 2.1 Product perspective
- The canon is a repo document that the flow reads (`V22`) and maintainers read.
- `mapper/app.py` loses one unused import.
- No runtime behaviour changes.

### 2.2 Product functions
None new.

### 2.3 User characteristics
The maintainer and operator, who read the canon to learn what the project demands and which batch owns each requirement.

### 2.4 Constraints
- **Append-only canon:** an existing row is never rewritten.
- **Sealed records are not edited.**
- At most 4 source files per increment.
- No UI change.

### 2.5 Assumptions and dependencies
The fold's normalisation (backticks dropped, `|` escaped as `\|`) is what the five appended statements follow, so that a later fold would recognise them. This is checked against the rows the fold printed at the hygiene close (§2.7).

### 2.6 Source user stories

| ID | User Story | Source | DoR status |
|----|------------|--------|------------|
| US-001 | As the maintainer, I want every requirement the hygiene batch declared to be in the canon under an id that cannot collide, naming the id its record uses, so that the canon answers "what does the project demand, and who owns it" for that batch too. | B-105 | READY |
| US-002 | As the maintainer, I want `mapper/app.py` to import nothing it does not use, so that the busiest module carries no dead import and a new lint warning stands out. | B-104 | READY |

#### Refinement log (one block per story)

**US-001 — the hygiene requirements reach the canon**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):**
  - user = maintainer;
  - outcome = five canon rows owned by `2026-10-09-hygiene-batch`, ids `HLR-HYG.1`, `HLR-HYG.2`, `LLR-HYG.1.1`, `LLR-HYG.1.2`, `LLR-HYG.2.1`, each statement ending `(Record id: <id>.)`;
  - out of scope = renaming the data-safety rows.
- **Feasibility (E, S):** append five lines and add one test; fits one increment.
- **Evaluability (T) — behavioral, black-box:** "When the maintainer reads `REQUIREMENTS.md`, they find each hygiene requirement once, with its statement and its record id, and no canon id appears twice." The artifact on disk is the surface.
- **Open questions:** none.
- **Classification:** `READY`.

**US-002 — no unused import in `mapper/app.py`**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** outcome = `import re` gone; every module-level import of `app.py` is used.
- **Feasibility (E, S):** a one-line removal and one test.
- **Evaluability (T) — behavioral, black-box:** "When the maintainer reads `mapper/app.py`, every module-level import is used." The oracle is the AST test over the shipped module (AT-064). `ruff check mapper/app.py` reporting no F401 is corroborating evidence and is not the oracle (LED .6).
- **Open questions:** none.
- **Classification:** `READY`.

### 2.7 Premise evaluation (C-43) — MANDATORY, one row per premise

| # | Premise, as a truth-apt proposition | Tier | Verdict | Executed evidence (command output / `file:line` — **NOT** a citation of another document) | Disposition |
|---|---|---|---|---|---|
| 1 | the canon holds no row owned by `2026-10-09-hygiene-batch` and no `HYG` id | executed | ✅ TRUE | `grep -c HYG REQUIREMENTS.md` → `0`; `grep -n hygiene-batch REQUIREMENTS.md` → no output | in scope (LLR-CAN.1.1) |
| 2 | the canon holds no duplicate requirement id today | executed | ✅ TRUE | `awk -F'\|' '/^\| [HL]LR/{print $2}' REQUIREMENTS.md \| sort \| uniq -d` → no output | in scope (LLR-CAN.1.2 guards it) |
| 3 | the hygiene record declares exactly five requirement headings | executed | ✅ TRUE | `grep -n "^### \(HLR\|LLR\)" .dev-flow/2026-10-09-hygiene-batch/01-requirements.md` → lines 126, 151, 173, 190, 202 | in scope |
| 4 | `re` is imported at `mapper/app.py:7` and never used | executed | ✅ TRUE | `grep -n "^import re" mapper/app.py` → `7:import re`; no `re.` usage; `ruff check mapper/app.py` → `F401 re imported but unused` | in scope (LLR-CAN.2.1) |

- **Premise evaluation:** 4 premise(s) · 4 ✅ TRUE / 0 ❌ FALSE / 0 ❓ UNDECIDABLE

### 2.8 Fork preconditions (C-52) — MANDATORY, and the declared empty when the batch does not fork

| # | Condition (`C-52`) | Discharged? | The executed evidence |
|---|---|---|---|
| 1 | **Frozen contract** | ✅ | one lane |
| 2 | **Disjoint FILE sets** | ✅ | one lane |
| 3 | **Crossed reverse census** | ✅ | one lane |
| 4 | **One owner of the trunk** | ✅ | the orchestrator |

- **Fork preconditions:** none — this batch runs one lane

---

## 3. High-level requirements (HLR)

### HLR-CAN.1 — every hygiene requirement is in the canon under a collision-free id
- **Traceability:** US-001
- **Ledger:** LED-2026-10-09-canon-batch.1, LED-2026-10-09-canon-batch.2, LED-2026-10-09-canon-batch.3, LED-2026-10-09-canon-batch.5
- **Statement:** The canon shall hold, for each requirement heading of `2026-10-09-hygiene-batch`'s record, exactly one row owned by that batch whose statement equals the record's statement and names the record id, and no requirement id shall appear in more than one canon row.
- **Rationale (informative):**
  - The fold keeps an existing id and never rewrites it, so a reused id leaves its batch out of the canon while `V22` reads green.
  - The uniqueness check is a regression net for these appends. It is not a detector of B-105's failure mode, which is an id reused and never appended (§6.3).
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_requirements_canon.py`
- **Numeric pass threshold:** exit code 0; 5 hygiene rows matched; 0 duplicate ids.
- **Priority:** medium
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** `REQUIREMENTS.md` lists `HLR-HYG.1`, `HLR-HYG.2`, `LLR-HYG.1.1`, `LLR-HYG.1.2` and `LLR-HYG.2.1`, owned by `2026-10-09-hygiene-batch`. Each statement ends `(Record id: <id>.)`, and every id in the file is unique.
  - **Shipped surface:** the file `REQUIREMENTS.md` on disk.
  - **Acceptance test(s):** AT-063
  - **Boundary catalog (QC-3):** ☑ empty — the hygiene record must yield exactly 5 headings and the canon table at least 134 rows (129 before this batch + 5), so the test cannot pass over an empty set ☑ boundary — a record id whose canon row is missing; a canon id appearing twice; a statement holding an escaped pipe (`LLR-001.1`'s `str \| None`) ☐ invalid ☑ error — a statement that drifts from its record; a row whose `(Record id: …)` suffix is stripped.
  - **Negative control:** executed at Phase 3. AT-063 goes RED in each of these cases:
    - on today's canon, which has no hygiene rows;
    - when one appended row is duplicated;
    - when one statement is altered;
    - when one `(Record id: …)` suffix is stripped.

### HLR-CAN.2 — `mapper/app.py` imports nothing it does not use
- **Traceability:** US-002
- **Ledger:** LED-2026-10-09-canon-batch.4, LED-2026-10-09-canon-batch.6
- **Statement:** The module `mapper/app.py` shall import no module-level name that it does not reference.
- **Rationale (informative):** an unused import in the largest module hides the next real lint warning among old ones.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_app_imports_used.py` and `ruff check mapper/app.py`
- **Numeric pass threshold:** exit code 0 for both.
- **Priority:** low
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** `mapper/app.py` imports no name it does not use. **The AT's oracle is the AST test**, which reads the shipped module file. `ruff check mapper/app.py` is separate evidence, run once by the orchestrator and attributed. `ruff` is not a declared project dependency, so if it is absent that run is recorded as `not-run`, never as a pass.
  - **Shipped surface:** the module file `mapper/app.py`, which is the surface a maintainer reads.
  - **Acceptance test(s):** AT-064
  - **Boundary catalog (QC-3):** ☐ empty ☑ boundary — an `import a.b` binds `a`, and a `from x import y as z` binds `z` ☐ invalid ☐ error.
  - **Negative control:** AT-064 goes RED on today's `app.py`, because `re` is unused. Executed at Phase 3.

---

## 4. Low-level requirements (LLR)

### LLR-CAN.1.1 — five appended canon rows, one per hygiene heading
- **Traceability:** HLR-CAN.1
- **Ledger:** LED-2026-10-09-canon-batch.2
- **Statement:** `REQUIREMENTS.md` shall end its requirement table with five rows, `HLR-HYG.1`, `HLR-HYG.2`, `LLR-HYG.1.1`, `LLR-HYG.1.2`, `LLR-HYG.2.1`, mapping to the record ids `HLR-001`, `HLR-002`, `LLR-001.1`, `LLR-001.2`, `LLR-002.1`. Each row's statement cell shall equal N(record statement) + ` (Record id: <id>.)`, where N is the fold's normalisation:
  1. drop backticks and `**`;
  2. strip leading and trailing spaces, tabs, `*` and `-`;
  3. drop a trailing `*(…)*`;
  4. escape `|` as `\|`.

  The owner shall be `2026-10-09-hygiene-batch` and the status `active`. The test pins these four rules as literals of its own and does not import the fold, so that a drift of either side goes RED.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_requirements_canon.py -k hygiene`
- **Numeric pass threshold:** exit code 0.
- **Negative control:** RED on today's canon (no rows).
- **Boundary catalog:** ☑ empty — exactly 5 record headings ☑ boundary — a missing row; the escaped pipe in `LLR-001.1` ☑ error — a drifted statement; a stripped record-id suffix.

### LLR-CAN.1.2 — canon ids are unique
- **Traceability:** HLR-CAN.1
- **Ledger:** LED-2026-10-09-canon-batch.3, LED-2026-10-09-canon-batch.5
- **Statement:** Every requirement id in the first cell of a row of `REQUIREMENTS.md`'s requirement table shall appear exactly once. The table is anchored on its `| Id |` header and read until the first non-row line. Only the first cell is read (`split("|")[1]`, as the fold does), so escaped pipes in later cells cannot shift it. The table shall hold at least 134 rows.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_requirements_canon.py -k unique`
- **Numeric pass threshold:** exit code 0.
- **Negative control:** a canon with one row duplicated turns it RED. Executed at Phase 3 by mutation.
- **Boundary catalog:** ☑ boundary — two rows with one id.

### LLR-CAN.2.1 — the unused `re` import is removed and guarded
- **Traceability:** HLR-CAN.2
- **Ledger:** LED-2026-10-09-canon-batch.4
- **Statement:** `mapper/app.py` shall not contain `import re`, and a test shall assert that every module-level import name of `mapper/app.py` is referenced in that module.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_app_imports_used.py`
- **Numeric pass threshold:** exit code 0.
- **Negative control:** RED with `import re` restored.
- **Boundary catalog:** ☑ boundary, with synthetic-source arms that check the checker itself:
  - `import a.b` binds `a`;
  - `import x as y` and `from m import n as z` bind the alias;
  - an alias imported but unused is reported;
  - a name mentioned only in a string, docstring or comment does not count as used.

  What counts as a use: an `ast.Name` load, or the base `ast.Name` of an `ast.Attribute`. `from __future__ import …` is excluded. Star imports and `__all__` are out of scope (`app.py` has neither). A future deliberate re-export must go on an explicit allowlist in the test, with its reason; the test is not weakened for it.

### Information Flow Contract (IFC) — C-54

- **Part A — flows:**

```
FLOW hygiene-requirements-to-canon
SOURCE: .dev-flow/2026-10-09-hygiene-batch/01-requirements.md headings
NODES: the five appended REQUIREMENTS.md rows (LLR-CAN.1.1), the uniqueness check (LLR-CAN.1.2)
SINK: REQUIREMENTS.md, read by V22 and by maintainers
```

- **Part B — boundary decomposition:** no. The batch changes one document and one import, and no component of the boundary is addressable on its own.

---

## 5. Validation strategy

### 5.1 Methods

> - **Layer A — white-box / functional:** `tests/test_requirements_canon.py` (LLR-CAN.1.1, LLR-CAN.1.2), `tests/test_app_imports_used.py` (LLR-CAN.2.1).
> - **Layer B — black-box / behavioral acceptance (`AT-NNN`):**
>   - AT-063 reads the shipped `REQUIREMENTS.md` against the shipped hygiene record.
>   - AT-064 reads the shipped `mapper/app.py`; `ruff check mapper/app.py` is run alongside it.

### 5.2 Batch acceptance criteria
- 100% of LLRs are covered by an executed check with a pass result.
- Every AT is GREEN, with an executed RED counterfactual.
- The full suite is green at P4 (0 failed).
- No existing canon row and no sealed record changed (`git diff` over `REQUIREMENTS.md` shows additions only).

---

## 6. Appendices (optional)

### 6.1 Extended glossary
### 6.2 Relevant design decisions
- **Append, never rename.** The data-safety rows keep `HLR-001`…, because they were folded first and own those ids. The hygiene rows take `HYG`. The record id is written into the statement, because the canon has no alias column and adding one would rewrite every row.
- **Namespaced ids from this batch on (`CAN`).** This is a project convention until the flow's template seeds a namespace (reported for the flow backlog).
- **The close fold appends this batch's own five rows** (`HLR-CAN.1`, `HLR-CAN.2`, `LLR-CAN.1.1`, `LLR-CAN.1.2`, `LLR-CAN.2.1`). The fold reads only the active batch's headings (`devflow-init.py` `fold_canon`). The five `HYG` rows are verified by AT-063, not by the fold.
- **What would change this design:** a fold that can alias or rewrite rows. With one, the in-statement record id would become unnecessary.
### 6.3 Open risks
- A later batch that again uses a plain `HLR-001` repeats B-105. Mitigations: the convention above, and LLR-CAN.1.2, which does not catch a reused id that is never appended. That case is only caught by reading the fold's `kept:` lines, which is stated here and not claimed away.
### 6.4 Phase-1 reconciliation log — moved to the ledger (§7)

### 6.5 Requirement amendments — moved to the ledger (§7)

---

## 7. The ledger — authored as a SEPARATE FILE

The fence below is the ledger's seed: `devflow-init.py` writes it to `01-requirements-ledger.md`. The shape of an entry is in the field guide.

```markdown
# Requirements ledger — mapper — Batch 2026-10-09-canon-batch

> Append-only. Entries are added in chronological order and never rewritten. The live
> contract is `01-requirements.md`; this file records how it came to say what it says.
> Every entry names the requirement it amends; every requirement names its entries. `V26`
> compares the two sets of pairs both ways.

_No entries yet. The first amendment to the live contract writes the first one, in the
shape the field guide's §7 shows (`req-template.md` in the guide directory init prints), and nothing
above this line is ever edited._
```
