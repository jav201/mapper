# Validation — mapper — Batch 2026-10-09-canon-batch

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`); for Spanish batches **translate the prose, never a label** — the reserved field names are declared in §✅ Verdict and are read literally.
> Phase 4 artifact. Content owner: `qa-reviewer`, who **EVALUATES** the results of the validation strategy fixed in Phase 1, **names who executed each one** and returns the rows; the orchestrator writes `04-validation.md` (`stations/shared-homes-roles.md` §Delegation). The ONE complete gate-suite run is the orchestrator's (`C-25`); a sub-agent consumes the result and never owns the run.

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/docs/validation-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

## ✅ Verdict (read first)

> **Reserved field names.** The **field names and block keywords below are language-independent** — the
> validator parses them literally and they are never translated:
> `Result` · `Layer 0` · `Evidence checklist` · `⏸ DEFER`
> Everything else on this page — headings, guidance, the prose in every cell — is translated with the batch.
> **One strategy, not two:** the flow ships no alias table, so a translated label is read as an ABSENT one and the rule keyed on it reports a true-sounding silence.
> **And one FLOW-WIDE reserved token, read out of this artifact by `V42` no matter which template minted it:** `⏸ DEFER`. It is a MARKER rather than a field name, which is why it is stated here *and* in `/dev-flow` §Language of artifacts rather than in a per-template list — a deferral can be written in any batch artifact, including the ones that carry no block at all.
>
> **And so are the three verdict tokens** `PASS` · `PASS-WITH-NOTES` · `FAIL`, which are VALUES and not prose.
> A Spanish batch writes `- **Result:** PASS`, not `- **Resultado:** aprobado`: the label, the tokens and the
> reviewer-identity tokens below are the machine's vocabulary.

- **Result:** PASS-WITH-NOTES
- **Layer 0:** 0 unit(s) met the criterion · 0 carry a named reddening mutation
- **Requirements:** 5/5 pass (HLR-CAN.1, HLR-CAN.2, LLR-CAN.1.1, LLR-CAN.1.2, LLR-CAN.2.1) · 0 blocker fails
- **Black-box acceptance (Layer B):** ✓ every story's `AT` observes its outcome through the shipped surface (boundary + negative)
- **Surface-reachability (bidirectional):** ✓ all named inputs AND outputs/deliverables reached/observed at the surface
- **Supersession inspection (read off the P3 packets):** ✓ all surviving refs negative
- **Test ledger:** ✓ reconciles (`base − D + A = post`)
- **Evidence checklist (qa-reviewer):** `qa-reviewer` (Claude Sonnet, independent) · ACCEPT; both optional notes applied · 11 of 11 rows ✓

> If every line is ✓, the Detail below is reference only. Any ⚠/✗ → read the matching part.

---

## Detail (reference)

### Layer 0 — unit

| Unit | Which criterion | Node id | Result |
|---|---|---|---|
| none — no unit meets the criterion: the change is a document append plus a one-line import removal, and no behaviour reaches cyclomatic ≥3 or crosses a module boundary | — | — | n/a |

**Measured by mutation, never by line coverage.** For each unit, name the mutation and paste the RED:

| Unit | Mutation applied | RED observed? | Transcript |
|---|---|---|---|
| none | — | — | — |

### UX walkthrough — only if trigger family D fired

| Criterion (when the user does X, they observe Y) | Driven with the REAL mechanism | Painted result asserted | Verdict |
|---|---|---|---|
| not applicable — no trigger-D surface | — | — | — |

**Mechanism used:** `none — inspected only`

| Act | What it is | Performed? |
|---|---|---|
| Automated walkthrough | the criteria above, driven through the REAL mechanism | `not applicable — no trigger-D surface` |
| Expert inspection | a cognitive walkthrough against declared criteria, by a reviewer and not a user | `not applicable — no trigger-D surface` |
| Evaluation with users | real users of the system, doing the tasks named in the context of use | `not applicable — no trigger-D surface` |

- **Method:** trigger family D did not fire. The change is a document append (five `REQUIREMENTS.md` rows) and a one-line import removal (`import re` in `mapper/app.py`), so there is nothing a user sees and no surface to drive. The acceptance outcomes are instead observed through the shipped surfaces by AT-063 (the file `REQUIREMENTS.md` on disk) and AT-064 (the module `mapper/app.py` on disk).
- **Participants or population:** none — not applicable.
- **Evidence of the evaluation:** none — not applicable.
- **Limits:** this establishes nothing about real-user UX because the change is invisible to a user by design (an append to a repo document and a dead-import removal). The walkthrough was skipped on those grounds, not because a criterion was dropped.

### Layer A — functional (white-box): per-requirement results
> `TC-NNN` ↔ LLR/HLR. `Result` = pass / fail. `Evidence` = command output, observed behavior, inspection note, or analysis result.

| Req | Method | Executed verification | Numeric threshold | Result | Evidence |
|-----|--------|-----------------------|-------------------|--------|----------|
| HLR-CAN.1 | test | whole-file run `python -B -m pytest -q -p no:cacheprovider tests/test_requirements_canon.py` (RED under C0/C1/C2/C3, GREEN after restore, in `inc001-mutation-battery.transcript`) and the gate suite (`p4-full-suite.transcript`) — **executed by: orchestrator** | exit code 0 · 5 hygiene rows matched · 0 duplicate ids | pass | `tests/test_requirements_canon.py::test_at_063_every_hygiene_requirement_is_in_the_canon_once` · `tests/test_requirements_canon.py::test_llr_can_1_2_canon_ids_are_unique_and_the_table_is_not_empty`; RED/GREEN in `evidence/inc001-mutation-battery.transcript`, gate in `evidence/p4-full-suite.transcript` |
| HLR-CAN.2 | test | whole-file run `python -B -m pytest -q -p no:cacheprovider tests/test_app_imports_used.py` (RED under A1, GREEN after restore, in `inc001-mutation-battery.transcript`), `ruff check mapper/app.py` → `All checks passed!` (`inc001-ruff.transcript`), and the gate suite (`p4-full-suite.transcript`) — **executed by: orchestrator** | exit code 0 for both | pass | `tests/test_app_imports_used.py::test_at_064_app_imports_nothing_it_does_not_use`; RED/GREEN in `evidence/inc001-mutation-battery.transcript`, `ruff` in `evidence/inc001-ruff.transcript`, gate in `evidence/p4-full-suite.transcript` |
| LLR-CAN.1.1 | test (integration) | whole-file run `python -B -m pytest -q -p no:cacheprovider tests/test_requirements_canon.py` — the contract's selector `-k hygiene` selects a subset of this file (checked by the orchestrator, `evidence/p4-selector-check.transcript`: `pytest --collect-only -q -k hygiene`); the battery ran the whole file, which contains it (`inc001-mutation-battery.transcript`: C0/C2/C3 RED, "GREEN after restore" 17 passed) — **executed by: orchestrator** | exit code 0 | pass | `tests/test_requirements_canon.py::test_at_063_every_hygiene_requirement_is_in_the_canon_once` · `tests/test_requirements_canon.py::test_llr_can_1_1_normaliser_pins_the_fold_rules`; RED/GREEN in `evidence/inc001-mutation-battery.transcript` · note: `test_llr_can_1_1_normaliser_pins_the_fold_rules` is literal pins with no RED of its own; the rule's RED comes from AT-063 under C2/C3 |
| LLR-CAN.1.2 | test (integration) | whole-file run `python -B -m pytest -q -p no:cacheprovider tests/test_requirements_canon.py` — the contract's selector `-k unique` selects a subset of this file (checked by the orchestrator, `evidence/p4-selector-check.transcript`: `pytest --collect-only -q -k unique`); the battery ran the whole file, which contains it (`inc001-mutation-battery.transcript`: C0/C1 RED, "GREEN after restore" 17 passed) — **executed by: orchestrator** | exit code 0 | pass | `tests/test_requirements_canon.py::test_llr_can_1_2_canon_ids_are_unique_and_the_table_is_not_empty`; RED/GREEN in `evidence/inc001-mutation-battery.transcript` |
| LLR-CAN.2.1 | test (unit) | whole-file run `python -B -m pytest -q -p no:cacheprovider tests/test_app_imports_used.py` — the contract's selector `-k llr_can_2_1` selects a subset of this file (checked by the orchestrator, `evidence/p4-selector-check.transcript`: `pytest --collect-only -q -k llr_can_2_1`); the battery ran the whole file, which contains it (`inc001-mutation-battery.transcript`: A1 RED, "GREEN after restore" 17 passed) and `ruff check mapper/app.py` (`inc001-ruff.transcript`) — **executed by: orchestrator** | exit code 0 | pass | `tests/test_app_imports_used.py::test_at_064_app_imports_nothing_it_does_not_use` · `tests/test_app_imports_used.py::test_llr_can_2_1_checker_arms[...]` (13 arms); RED/GREEN in `evidence/inc001-mutation-battery.transcript`, `ruff` in `evidence/inc001-ruff.transcript` |

**A worked example — text to read, never rows of your record.** It sits in a fence so that nothing has to be deleted: a row copied out of it would claim a verification nobody ran. Write your own rows in the table above.

```text
| *(example)* HLR-001 | test | `pytest … -k TC-001` | exit 0 | | |
| *(example)* LLR-001.1 | test (unit) | `…` | `…` | | |
```

### Layer B — behavioral (black-box) acceptance

| US | Acceptance test (`AT-NNN`) | Surface driven | Deliverable observed (path / element) | repr · boundary · negative | Result |
|----|----------------------------|----------------|---------------------------------------|----------------------------|--------|
| US-001 | AT-063 | the file `REQUIREMENTS.md` on disk | the five appended rows `HLR-HYG.1`, `HLR-HYG.2`, `LLR-HYG.1.1`, `LLR-HYG.1.2`, `LLR-HYG.2.1` | repr: each statement equals N(record) + `(Record id: <id>.)` · boundary: the escaped pipe in `LLR-001.1` (`str \| None`), 5 headings, ≥134 rows · negative: C0, C1, C2, C3 killed | pass |
| US-002 | AT-064 | the module `mapper/app.py` on disk | the empty unused-import set (`import re` gone) | repr: every module-level import referenced · boundary: the 13 synthetic arms (`import a.b` binds `a`, alias binding, string/docstring/comment don't count) · negative: A1 killed | pass |

### Bidirectional surface-reachability matrix (extends A-5)
> Every named INPUT dimension AND every named OUTPUT/deliverable is exercised/observed through the handler — not only the service API.

| Direction | US dimension / deliverable | Service param / producer | Reached/observed at surface? | TC / AT | Status |
|-----------|---------------------------|--------------------------|------------------------------|---------|--------|
| input | US-001 the hygiene record's `HLR`/`LLR` headings | the hygiene record `01-requirements.md` headings (read by AT-063's `_record_statements`) | yes | AT-063 | ✓ |
| input | US-002 the module-level imports of `app.py` | `mapper/app.py` AST (read by AT-064's `unused_imports`) | yes | AT-064 | ✓ |
| output | US-001 the five canon rows (`HLR-HYG.1`, `HLR-HYG.2`, `LLR-HYG.1.1`, `LLR-HYG.1.2`, `LLR-HYG.2.1`) | `REQUIREMENTS.md` rows on disk | yes | AT-063 | ✓ |
| output | US-002 the empty unused-import set | `unused_imports(mapper/app.py)` → `set()` | yes | AT-064 | ✓ |

### Signed-balance test ledger
> `post = base − D + A`. State counts in collected / passed-lean / passed-full form.

| base | − D | + A | = post | actual collected | passed-lean / full | reconciles? |
|------|-----|-----|--------|------------------|--------------------|-------------|
| 2927 | 0 | 17 | 2944 | 2944 (`2944/2968 tests collected (24 deselected)`) | — / 2941 passed + 3 xfailed = 2944, 0 failed (`evidence/p4-full-suite.transcript`, 1502.08s, exit 0) | yes |

### Gaps detected
| ID | Requirement | Gap | Severity | Proposed action |
|----|-------------|-----|----------|-----------------|
| G-001 | HLR-CAN.1 / LLR-CAN.1.2 (watch item) | B-105's failure mode — an id reused and never appended — is not detectable by anything in the repo: the fold keeps an existing id and never rewrites it, so the missing batch stays out of the canon while `V22` reads green. This is a flow-side defect, not a product defect. | minor | the flow-side fix (the template seed and the fold) is the operator's decision, reported to the flow's own backlog (§6.3 of the contract). No repo action blocks this batch. |

### Escaped-bug regression (if a defect escaped the suite)

| Regression id (`AT-NNN` / `TC-NNN`) | Pre-fix run (evidence it FAILED) | Pre-fix RED kind (value / shape) | Post-fix value-discriminating? (QC-2) | Post-fix result | Reconciled node |
|-------------------------------------|----------------------------------|----------------------------------|----------------------------------------|-----------------|-----------------|
| none — no defect escaped | — | — | — | — | — |

### Evidence checklist — qa-reviewer (full)
> Attach `qa-reviewer`'s completed evidence checklist (items in `agents/qa-reviewer.md`), each marked ✓/✗ with one-line evidence. An unchecked or evidence-less item blocks the gate.

**Who executed what:**
- **The orchestrator (Claude Opus 5.5)** ran the gate suite, the mutation battery (C0–C3, A1), the regression set, `ruff`, and the selector check. It also wrote the five canon rows.
- **The worker DeepSeek (`deepseek-v4-pro`)** authored `tests/test_requirements_canon.py`, and drafted this file. The orchestrator corrected the draft: the `-k` selectors do match.
- **The worker Kimi (`kimi-for-coding`)** authored `tests/test_app_imports_used.py` and the `import re` deletion. Kimi's report shows 11 arms and 12 passed; the code-review nits CR-1/CR-2 later brought it to 13 arms.
- **The `qa-reviewer`** ran nothing and read the transcripts.

| # | Item | ✓/✗ | Evidence |
|---|---|---|---|
| 1 | Acceptance criteria as outcomes | ✓ | AT-063, AT-064 observed in Layer B |
| 2 | Explicit Expected | ✓ | exit 0; exactly one row per id; empty unused-import set |
| 3 | Edge cases | ✓ | escaped pipe, ≥134 rows, 13 synthetic arms, C0–C3 + A1 negatives |
| 4 | Regression checklist | ✓ | `inc001-regression-set.transcript` 147 passed (orchestrator) + the gate |
| 5 | Exit criteria | ✓ | 0 failed; all requirements pass |
| 6 | No PII / secrets | ✓ | transcripts scrubbed; `test_no_operator_paths` green in the gate |
| 7 | Mode + executor per result | ✓ | validation; "executed by: orchestrator" on each Layer A row |
| 8 | Layer B with boundary + negative | ✓ | `REQUIREMENTS.md` and `mapper/app.py` on disk |
| 9 | Bidirectional reachability | ✓ | 2 inputs, 2 outputs |
| 10 | Ledger | ✓ | 2927 − 0 + 17 = 2944; gate 2941 passed + 3 xfailed |
| 11 | No unfilled template | ✓ | this checklist pasted |
