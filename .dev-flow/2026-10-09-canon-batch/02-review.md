# Review — mapper — Batch 2026-10-09-canon-batch

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`).
> Phase 2 artifact. Reviewers (in parallel): `architect` ∥ `qa-reviewer` ∥ `security-reviewer` by trigger family C (always in `full`).

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/docs/review-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

## ✅ Verdict (read first)

- **Gate:** round 1 → `iterate-to-refine` → Phase 1 (ARCH-1 and QA-2 are requirement-defect majors; QA-1 is a major). Round 2 → `approve` → Phase 3.
- **Out-of-scope findings:** none.

- **Findings (round 1):** 0 blocker · 3 major · 5 minor. All applied in P1 iteration 1 (ledger `LED-2026-10-09-canon-batch.1`–`.5`). Round 2: 1 new minor (NEW-1), applied (LED .6).
- **shall/should check:** ✓ clean.
- **Two-layer (blockers):** ✓ every story has an `AT`.
  - AT-063 observes `REQUIREMENTS.md` on disk.
  - AT-064 observes the shipped module through its AST oracle, with `ruff` as attributed corroboration.
  - Both chains are complete.
- **Census (change-first):** done — best-effort + gate-confirmed. No test parses the canon: `tests/test_repair_cycles.py:30` and `tests/test_vocabulary_declaration.py:297` read batch records.
- **Security:** ✓ not run — trigger family C did not fire; `devflow-scan-spec.py` flags none.
- **Evidence checklists (architect / qa):** ✓ both attached. The architect's one ✗ ("what would change the recommendation") is fixed in §6.2. The qa-reviewer's ✗ rows (edge cases, Layer B of AT-064) are fixed (LED .2–.4).

---

## Detail (reference)

### Findings
| ID | Reviewer | Severity | Area / Req | What | Recommendation | Status |
|----|----------|----------|------------|------|----------------|--------|
| ARCH-1 | architect | major | PLAN B4, §6.2 | The close fold reads only the active batch's headings (`devflow-init.py` `fold_canon`). It folds this batch's five `CAN` rows, not "kept" HYG rows. | Correct the control; state the CAN fold; AT-063 verifies HYG | fixed (LED .1) |
| QA-2 | qa-reviewer | major | HLR-CAN.1, LLR-CAN.1.1 | "Equals" is under-specified. The test must not reuse the writer's normaliser. The escaped pipe in `LLR-001.1` is a boundary. | Pin N's rules as test literals; add the escaped-pipe boundary and a suffix-strip control | fixed (LED .2) |
| ARCH-2 | architect | minor | LLR-CAN.1.1 | The fold's `_statement` has four rules (backticks/`**`, strip ` \t*-`, trailing `*(…)*`, `\|`); the contract listed two. | Replicate all four | fixed (LED .2) |
| QA-1 | qa-reviewer | major | HLR-CAN.2 / AT-064 | The stated observable (`ruff`) is not what the AT executes, and `ruff` is not a declared dependency. | The AST test is the oracle; `ruff` is attributed corroboration, `not-run` if absent | fixed (LED .4) |
| QA-3 | qa-reviewer | minor | LLR-CAN.1.2 | Non-vacuous parse needed. | Anchor on `\| Id \|`, read the first cell only, set a row floor, require exactly 5 record headings | fixed (LED .3; the floor was corrected to 134 in LED .5) |
| ARCH-3 | architect | minor | HLR-CAN.1 rationale | The uniqueness guard is a regression net, not a B-105 detector. | Say so | fixed (LED .3) |
| QA-4 | qa-reviewer | minor | LLR-CAN.2.1 | The import boundary catalog was thin (`__future__`, Name-load rule, strings, synthetic arms). | Extend it | fixed (LED .4) |
| QA-5 | qa-reviewer | minor | LLR-CAN.2.1 | A future re-export could be blocked. | Explicit allowlist with a reason | fixed (LED .4) |
| NEW-1 | qa-reviewer (round 2) | minor | US-002 | The story still named the `ruff` output as the observable. | Reword to match HLR-CAN.2 | fixed (LED .6) |

**Reviewer error caught by the orchestrator:** QA-3 counted 77 canon rows and proposed an 82-row floor. An `awk` count from the `| Id |` header gives 129, and the architect also reported 129. The floor is 134, and QA confirmed this in round 2 (LED .5).

### shall / should check
Clean.

### Two-layer acceptance review (blockers)

| Story / Req | (a) AT present | (b) deliverable+method named | (c) both chains | (d) black-box pure | Status |
|-------------|----------------|------------------------------|-----------------|--------------------|--------|
| US-001 | yes (AT-063) | yes — `REQUIREMENTS.md` rows read from disk | yes (US-001 → HLR-CAN.1 → LLR-CAN.1.1/1.2 → `tests/test_requirements_canon.py`) | yes — reads the shipped canon and the record, not the writer | ✓ |
| US-002 | yes (AT-064) | yes — `mapper/app.py` read as a file; `ruff` corroborates | yes (US-002 → HLR-CAN.2 → LLR-CAN.2.1 → `tests/test_app_imports_used.py`) | yes (a maintainer's surface is the module) | ✓ |

### Supersession census (change-first)
Planned files: `REQUIREMENTS.md` (append), `mapper/app.py` (one line deleted), `tests/test_requirements_canon.py`, `tests/test_app_imports_used.py` (new).
- No golden.
- No frozen module.
- `tests/test_draft_hygiene.py` parses `app.py`'s AST, and an import removal does not touch the classes it inspects. The increment gate re-runs it.

### Security review summary
Not run, because trigger family C did not fire. Scan flags: none.

### Evidence checklists — architect · qa-reviewer

**architect:**
- ✓ constraints stated (§2.4);
- ✓ alternatives — forced by the fold's four-column shape; the alias column was rejected (§6.2);
- ✓ recommendation tied to constraints;
- ✓ risks (§6.3) + ARCH-1;
- ✓ cost and latency n/a;
- ✓ diagram n/a (one linear flow, IFC);
- ✗→✓ "what would change it" is now in §6.2;
- ✓ two-layer chains present;
- ✓ privacy n/a.

**qa-reviewer (mode plan):**
- ✓ mode declared;
- ✓ ACs as outcomes;
- ✗→✓ edge cases (LED .2–.4);
- ✓ negative controls named, RED on today's tree;
- ✓ exit criteria;
- ✓ no PII;
- ✗→✓ Layer B of AT-064 (LED .4);
- ✓ reachability (file on disk);
- ✓ no unfilled template;
- ✓ single-table structure confirmed.

### Round 2 (light confirmation)
- The qa-reviewer confirmed QA-1 to QA-5 resolved (`01-requirements.md:150-217`) and the 134 floor.
- One new minor, NEW-1, was fixed (LED .6).
- **Verdict: `approve` → Phase 3.** Self-approved under the standing authorization.
