# Review — mapper — Batch 2026-10-09-hygiene-batch

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`).
> Phase 2 artifact. Reviewers (in parallel): `architect` ∥ `qa-reviewer` ∥ `security-reviewer` by trigger family C (always in `full`).

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/docs/review-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

## ✅ Verdict (read first)

- **Gate:** round 1 → `iterate-to-refine` → Phase 1, because QA-1 is a requirement-defect major. Round 2 → `approve` → Phase 3, after QA confirmed the fixes (see Round 2 below).
- **Out-of-scope findings:** none.

- **Findings (round 1):** 0 blocker · 1 major · 6 minor. All 7 were applied in P1 iteration 1 (ledger `LED-2026-10-09-hygiene-batch.1`–`.4`).
- **shall/should check:** ✓ clean.
- **Two-layer (blockers):** ✓ every story has an `AT` · the output reqs name a deliverable and an observation · both trace chains are complete · the ATs are black-box (they drive real keys and assert the toast text, the guard count and the hint line).
- **Census (change-first):** done — best-effort + gate-confirmed. The reverse census of `_save_or_toast` writers was widened to `mapper/` (QA-2).
- **Security:** ✓ not run. Trigger family C did not fire in this `core` batch, and the scan flag `expose` is answered as a false positive in `01-requirements.md` §6.3.
- **Evidence checklists (architect / qa):** ✓ both attached. Each has one ✗, and both ✗ items were fixed in iteration 1.

---

## Detail (reference)

### Findings
| ID | Reviewer | Severity | Area / Req | What | Recommendation | Status |
|----|----------|----------|------------|------|----------------|--------|
| QA-1 | qa-reviewer | major | HLR-001, AT-061 | The negative control says "a second guard stacks". That cannot happen: `_guard_draft` returns silently when its guard is up (`app.py:3474-3475`). What actually breaks is that the walk wedges, so the later `ctrl+q` opens no guard (`test_draft_exits.py:187`). | Reword the control; execute the two mutants and record their failing lines. | fixed (LED .1) |
| QA-2 | qa-reviewer | minor | LLR-001.1 | `_save_or_toast` writes the slot on non-`MapScreen` screens (`factory.py:219`, `app.py:1167`). The census grepped `app.py` only. | Name them; state the intent. | fixed (LED .2) |
| QA-3 | qa-reviewer | minor | LLR-001.1/001.2 TC | A source-shape test does not encode intent, and `vars()`/`__dict__` reads are not covered. | Add behaviour checks plus AST over `mapper/`, and state the blind spot. | fixed (LED .3) |
| QA-4 | qa-reviewer | minor | Traceability | No tag mechanism is named for the existing AT nodes. | Use the AT id in the docstring, and list the touched test files. | fixed (LED .1) |
| QA-R | qa-reviewer | minor | Regression checklist | No regression set is named. | List the draft/exit/inspector/inc9h suites. | fixed (LED .1) |
| ARCH-1 | architect | minor | §6.2 F5 | "Hand-renamed file" is inaccurate: load and save share `check_map_id` (`store.py:681`, `:810`), so the case is unreachable. | Restate the reason. | fixed (LED .4) |
| ARCH-2 | architect | minor | LLR-001.1/001.2 | The verification form is unstated, and a grep is brittle. | Add behaviour checks plus a package-wide scan. | fixed (LED .3, merged with QA-3) |
| ARCH-3 | architect | minor | LLR-001.1 | The `:299` write stays untyped on other screens. | Keep it, comment it, keep the `or "error"` fallback, and state what would change it. | fixed (LED .2, merged with QA-2) |

The counts: QA-2/ARCH-3 and QA-3/ARCH-2 are the same defects seen by both lenses. That makes 8 rows, 6 distinct defects, and 1 major.

### shall / should check
Clean. `shall` appears only in the Statement lines, and no `should` appears in any HLR/LLR statement.

### Two-layer acceptance review (blockers)

| Story / Req | (a) AT present | (b) deliverable+method named | (c) both chains | (d) black-box pure | Status |
|-------------|----------------|------------------------------|-----------------|--------------------|--------|
| US-001 | yes (AT-060, AT-061) | yes (toast text, guard modal, through real keys) | yes (US-001 → HLR-001 → LLR-001.1/001.2 → `test_draft_hygiene.py`) | yes | ✓ |
| US-002 | yes (AT-062) | yes (home hint line, `↵` pair present/absent) | yes (US-002 → HLR-002 → LLR-002.1 → mutation transcript) | yes | ✓ |

### Supersession census (change-first)
Planned files:
- `mapper/app.py` (source);
- `tests/test_draft_hygiene.py` (new);
- `tests/test_draft_save.py`, `tests/test_draft_exits.py`, `tests/test_inc9h.py` (docstring tags only).

Families run:
- **behavioral placeholder:** no placeholder is touched;
- **structural/placement:** no file moves;
- **AST composition:** `tests/test_g6_store_surrogates.py` parses `_save_or_toast` call sites. The helper's signature and call sites are unchanged, so it stays green; the increment gate must confirm this;
- **frozen module:** none declared.

Reservation: `tests/test_inspector.py:64` names a mutation on `_save_draft`'s `_save_or_toast` call. The increment gate runs that file.

### Security review summary
Not run, because trigger family C did not fire in this `core` batch (PLAN.md §Triggers). The scan flag `expose` (C7) is a false positive: it refers to a Python method, and the answer is in `01-requirements.md` §6.3.

### Evidence checklists — architect · qa-reviewer

**architect (round 1):**
- ✓ constraints stated (§2.4);
- ✓ alternatives n/a (the shape is set by `has_pending_draft()`, `app.py:3458`; method vs property was checked);
- ✓ non-applicable constraints marked;
- ✓ recommendation tied to constraints;
- ✓ risks listed;
- ✓ cost/latency n/a;
- ✓ diagram n/a (two short IFC chains);
- ✗ "what would change the recommendation" was not stated. **Fixed** in LLR-001.1 (LED .2);
- ✓ two-layer chains present;
- ✓ cited lines re-read (`app.py` 299, 786, 1626, 3474-3481, 3548, 3565, 5217; `tests/test_inc9h.py:504`).

**qa-reviewer (round 1, mode plan):**
- ✓ acceptance in "When … the operator sees" prose (accepted for `core`);
- ✓ expected results explicit;
- ✓ edge cases (boundary + error; empty/invalid n/a with reasons);
- ✗ regression checklist was missing. **Fixed** (LED .1);
- ✓ exit criteria (§5.2);
- ✓ no PII/secrets;
- ✓ mode declared;
- ✓ Layer B through the shipped surface;
- ✓ reachability through keys and screens;
- ✓ no unfilled template.

### Round 2 (light confirmation)

QA re-read the amended contract and the ledger. Result:
- QA-1, QA-2, QA-3, QA-4 and the regression checklist are **resolved**, each with its line in `01-requirements.md` (`:146-149`, `:178`, `:184`, `:195-199`).
- **One new minor (A):** "touched for the tag only" read as if the batch touched three test files, when it touches four (one is new). Fixed by the orchestrator (LED .5). Tests are outside the source cap, and the source count is 1.
- **One QA "not checked" item, now verified by the orchestrator:** `app.py:1167` lies inside `class _ImportPreviewScreen` (`awk` over `mapper/app.py`). The requirement was corrected to the private class name.
- **Round 2 verdict:** `approve` → Phase 3. Self-approved under the standing authorization.
