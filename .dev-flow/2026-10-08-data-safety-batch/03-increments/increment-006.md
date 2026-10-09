# Increment 006 — DDR conditions: boundary arms, joined AT-025b node, TC-009.1 (US-001, US-002, US-004)

| Field | Value |
|---|---|
| Batch | `2026-10-08-data-safety-batch` |
| Increment | DDR fixes (conditions D1–D5 and the qa lens's three conditions) — tests and records only |
| Requirement(s) | LLR-003.3 · LLR-003.4 · LLR-003.6 · HLR-007 · LLR-007.2 · HLR-009 · LLR-009.1 · LLR-002.2 |
| Base | `0a16d90` |
| Method | Five small Kimi units (`kimi -m kimi-code/kimi-for-coding -p`, one per worktree, run in parallel; operator ruling 2026-10-09: K2.x first, K3 only for Opus-grade work). A DeepSeek unit for AT-025b produced no output for 9 min and was stopped; the same plan was re-run on Kimi. Records and the `I-remount-per-key` re-run by the orchestrator. |

## 1 · What changed
- D1 (PDR C14 boundary arms): esc with a live search clears it and opens no guard; a link to the SAME map is guarded (`s`/`d`/`esc`); archiving the draft's own node (`s`/`d`).
- D4: one joined node for AT-025b.
- TC-009.1: the settle assertion fails loud when the scroll never lands.
- D2/D3: requirements, design and `docs/ARCHITECTURE.md` aligned with the shipped code (ledger `.66`); ledger `.67` (AT-025b / AT-042), `.68` (C14 arms).

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `tests/test_ddr_esc_search.py` | test | LLR-003.3 | new, 1 node |
| `tests/test_ddr_same_map_link.py` | test | LLR-003.4 | new, 3 nodes |
| `tests/test_ddr_archive_own.py` | test | LLR-003.6 | new, 2 nodes |
| `tests/test_repair_cycles.py` | test | HLR-007, LLR-007.2 | `test_at_025b_a_damaged_map_declares_itself_and_the_others_keep_their_values` |
| `tests/test_help_scope.py` | test | HLR-009, LLR-009.1 | `test_tc_009_1_settle_assertion_fails_loud_when_the_scroll_never_lands` |
| `docs/ARCHITECTURE.md` | doc | HLR-003, HLR-004 | D3 |
| `.dev-flow/2026-10-08-data-safety-batch/01-requirements.md` | doc | LLR-004.2, HLR-007 | D2, ledger pointers |
| `.dev-flow/2026-10-08-data-safety-batch/01-requirements-ledger.md` | doc | LLR-004.2, LLR-007.2, LLR-003.6 | `.66`–`.68` |
| `.dev-flow/2026-10-08-data-safety-batch/design/design-proposal.md` | doc | LLR-004.2 | D2 |
| `.dev-flow/2026-10-08-data-safety-batch/design/PDR-2026-10-08-data-safety-batch.md` | doc | HLR-003 | C14 row corrected (D5) |
| `.dev-flow/2026-10-08-data-safety-batch/design/DDR-2026-10-08-data-safety-batch.md` | doc | HLR-003 | DDR record |

Source files: **0**.

## 3 · RED counterfactual and mutation verdicts (executed; each unit restored `mapper/` byte-identically, sha256 checked)

| Node | Mutation | Verdict |
|---|---|---|
| `test_ddr_esc_search` | route the search-clearing esc through `_guard_draft` | killed (`1 == 0`, a guard opened) |
| `test_ddr_same_map_link[s,d,escape]` | push the linked map without `_guard_draft` | killed (3 failed) |
| `test_ddr_archive_own[save,discard]` | `action_archive` calls `_archive()` directly | killed (2 failed) |
| `test_at_025b_…` | the damaged branch painted like a healthy card (`app.py:933-937`) | killed (no declared glyph) |
| `test_tc_009_1_…` | delete the settle assertion in `_effective_keys` | killed (`DID NOT RAISE`) — the Inc-3 settle-assert survivors are now guarded |
| `I-remount-per-key` (Inc-1b, crashed on the 120 s timeout) | `_put_draft` remounts the form on each key | **killed** by `tests/test_inspector.py::test_llr_002_2_markers_update_without_remounting_the_focused_field` (orchestrator, `--timeout=30`, 1 failed in 20.2 s; `inspector.py` restored) |

## 4 · Test results
- File level (orchestrator): each new file green; `tests/test_repair_cycles.py` 34 passed; `tests/test_help_scope.py` 51 passed.
- Full default lane: run at the Phase-4 gate on the integrated tree (`04-validation.md`).
- **Ledger:** 2915 + 9 (1 + 3 + 2 + 1 + 1, plus `same_map_link` ×3 counted above → 1+3+2+1+1 = 8 functions / 9 collected incl. parametrisation) — reconciled against the gate's collected count.

## 4b · Independent review
DDR lenses (`architect`, `qa-reviewer`) set these conditions; their discharge is re-read at the Phase-4 gate.

## 5 · Risks
- None new; tests and records only.

## 6 · Pending items
- External: validator `V7` flags the installed flow bundle (`SKILL.md` vs its manifest) — the flow's own rev101 work, not this project.
