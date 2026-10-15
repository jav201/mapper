# Review — mapper — Batch 2026-10-11-fixes-batch

> **Artifact language:** English (`state.json` `language: en`).
> Phase 2 artifact. Reviewers (in parallel): `architect` ∥ `qa-reviewer` ∥ `security-reviewer` by trigger family C (always in `full`).

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/guides/review-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

## ✅ Verdict (read first)

- **Gate:** `approve` → Phase 3, recommended. The one review run (`qa-reviewer` role, model DeepSeek, independent of the author) returned `approve-with-conditions`; every condition is resolved in the requirements (LED-2026-10-11-fixes-batch.7 … .11). The operator's gate decision is still owed.
- **Out-of-scope findings:** none.

- **Findings:** 0 blocker · 2 major · 5 minor — all 7 resolved (dispositions below).
- **shall/should check:** ✓ clean (no modal `should` in any HLR/LLR statement; new statements use `shall` only).
- **Two-layer (blockers):** ✓ every story (US-FX-001…006) has an `AT` (AT-084…AT-089) · output requirements name deliverable and observation · both trace chains complete · ATs drive the shipped surface.
- **Census (change-first):** done — best-effort + gate-confirmed.
- **Security:** not run — trigger family C did not fire in `core`; the batch adds no input surface, and the narrowed catch lets unexpected exceptions propagate (see `01-requirements.md` §6.3).
- **Evidence checklists (architect / qa / security):** qa-reviewer role: complete (probes quoted in the review). architect, security-reviewer: not run (`core`).

---

## Detail (reference)

### Findings
| ID | Reviewer | Severity | Area / Req | What | Recommendation | Status |
|----|----------|----------|------------|------|----------------|--------|
| MAJOR-1 | qa-reviewer (DeepSeek) | major | LLR-FX.4.1, 4.2, 4.3 | worker lifetime when the roles screen is popped before discovery returns is unspecified | guard the hand-back; test `Esc` before release | fixed — LED .7 |
| MAJOR-2 | qa-reviewer (DeepSeek) | major | LLR-FX.4.1 | "a discovery that raises is caught" has no reachable seam and no stated catch type | name the catch and the injected seam | fixed — LED .8 |
| MINOR-1 | qa-reviewer (DeepSeek) | minor | LLR-FX.1.3 | `row-N` counter discipline and interleaved cases ambiguous | state the discipline; add arms | fixed — LED .9 |
| MINOR-2 | qa-reviewer (DeepSeek) | minor | LLR-FX.2.1 | depth-column parentage absent from the root truth table | add a depth-only arm | fixed — LED .9 |
| MINOR-3 | qa-reviewer (DeepSeek) | minor | HLR-FX.4 / LLR-FX.4.3 | HLR says every key inert, LLR keeps `Esc` | align the HLR | fixed — LED .10 |
| MINOR-4 | qa-reviewer (DeepSeek) | minor | §5.1 / AT-085 | named helper `_import_and_press_save` cannot reach a typed-name save | point AT-085 at `_open_import` | fixed — LED .10 |
| MINOR-5 | qa-reviewer (DeepSeek) | minor | LLR-FX.1.1 | Unicode labels neither covered nor declared out of scope | declare scope | fixed — LED .11 |

#### Disposition of each finding

| Finding | Disposition | Where it landed |
|---|---|---|
| MAJOR-1 | Accepted, with the orchestrator ruling: a result returning after the pop is **discarded** (no paint, no notification, no exception), via worker cancellation on unmount plus an `is_mounted` / not-cancelled check in the hand-back. The reviewer's proposed `try/except Exception` around the hand-back is not adopted (it would hide defects). | `01-requirements.md`: LLR-FX.4.1 statement, threshold, negative control (M-FX13), validation node `test_roles_popped_screen_discards_late_discovery`; LLR-FX.4.2 statement; HLR-FX.4 statement, threshold, boundary catalog, negative control. Ledger `.7`. |
| MAJOR-2 | Accepted, with the orchestrator ruling: catch exactly `(OSError, ValueError, subprocess.SubprocessError, ValidationError)` around discovery, map to the existing `no repo` state with its existing copy; any other type propagates (a `RuntimeError` arm proves it). Seam in tests: a monkeypatched function on `identity.repo_root` / `identity.read`; no production seam. The reviewer's bare `except Exception` is not adopted. | LLR-FX.4.1 statement, threshold (4 degradation arms + 1 propagation arm), negative control (M-FX14), boundary catalog; HLR-FX.4 boundary catalog and negative control; new node `test_roles_discovery_failure_degrades_to_no_repo`. Ledger `.8`. |
| MINOR-1 | Accepted. Counter = one shared sequence, advancing once per row that takes a `row-N` id; three new threshold arms (empty id + punctuation title; empty-slug row then empty-id row; typed `row-N` after auto `row-N` → collision record). | LLR-FX.1.3 statement, threshold, boundary catalog. Ledger `.9`. |
| MINOR-2 | Accepted. A parent edge is built from the `parent` or `depth` column; arm `a,A,,0` / `b,B,,1` / `c,C,,2`. Exact depth semantics to be re-confirmed at the increment-001 RED proof (declared in the LLR). | LLR-FX.2.1 statement, threshold, boundary catalog; HLR-FX.2 boundary catalog. Ledger `.9`. |
| MINOR-3 | Accepted. HLR now says "every editing key … inert while `Esc` keeps its existing action". | HLR-FX.4 statement. Ledger `.10`. |
| MINOR-4 | Accepted. AT-085 uses `tests/test_seed_safety.py::_open_import`; `_import_and_press_save` stays for AT-084's preview-only assertion. | `01-requirements.md` §5.1 (Layer B). Ledger `.10`. |
| MINOR-5 | Accepted with the orchestrator ruling: scope is only what `slugify` does today (keeps `\w`, so `niño` stays `niño`); one non-regression arm in AT-084 / LLR-FX.1.1; anything more is out of scope. | §1.2 scope; HLR-FX.1 threshold and boundary catalog; LLR-FX.1.1 threshold and boundary catalog. Ledger `.11`. |

### shall / should check
Clean. The statements added or amended by this pass (LLR-FX.1.1, 1.3, 2.1, 4.1, 4.2, HLR-FX.4, new HLR-FX.5/6 and LLR-FX.5.1/6.1) use `shall` only; no `should`/`debería`.

### Two-layer acceptance review (blockers)

| Story / Req | (a) AT present | (b) deliverable+method named | (c) both chains | (d) black-box pure | Status |
|-------------|----------------|------------------------------|-----------------|--------------------|--------|
| US-FX-001 | yes (AT-084) | yes | yes | yes | ✓ |
| US-FX-002 | yes (AT-085) | yes | yes | yes | ✓ |
| US-FX-003 | yes (AT-086) | yes | yes | yes | ✓ |
| US-FX-004 | yes (AT-087) | yes | yes | yes | ✓ |
| US-FX-005 | yes (AT-088) | yes (`m.svg` + spy count) | yes | yes — drives `e` on a real map; the spy is the oracle of a test-hygiene story | ✓ |
| US-FX-006 | yes (AT-089) | yes (undeclared list) | yes | yes — drives the census comparison | ✓ |

### Supersession census (change-first)
Files planned: `mapper/mermaid.py`, `mapper/import_csv.py`, `mapper/store.py` (docstring), `mapper/screens/roles.py`; tests `test_fixes_csv_import.py`, `test_fixes_forest_root.py`, `test_fixes_roles_thread.py` (new), `test_mermaid.py`, `test_csv_safety_store.py`, `test_perf_dump.py`, `test_roles_screen.py` (moved pins), and for increment 004 `test_export_state.py`, `test_inc9c.py`. Reservations: the line-sensitive leak key (LLR-FX.6.1) makes later edits around the three `notify` calls fail loud, by design; the increment gates confirm completeness.

### Security review summary
Not run — trigger family C did not fire in `core`. The author's answers to the scan's questions are in `01-requirements.md` §6.3; the orchestrator may still route increment 003.

### Evidence checklists (full) — architect · qa-reviewer · security-reviewer
- qa-reviewer role (model DeepSeek, independent of the author): ✓ base defects reproduced in-tree by read-only probes (`slugify` empty results, forest root drift, edge-parent root); ✓ `build_forest` stays golden-identical under the hoist; ✓ increment file counts within the cap; ✓ mutants M-FX1…M-FX12 each paired to a node that can go RED; ✓ backward compatibility (`parse` unchanged). Evidence: the review's "Confirmed positives" section.
- architect, security-reviewer: not run (`core`).
