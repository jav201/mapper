# Increment 004 — Inc-4: AT-044 node, AT-042's two arms, reconciliation (US-002, US-003)

| Field | Value |
|---|---|
| Batch | `2026-10-08-data-safety-batch` |
| Increment | Inc-4 (design §2.1 rows 4.1–4.3) — packet numbered by completion order |
| Requirement(s) | HLR-007 · LLR-007.1 · LLR-007.2 · HLR-008 · LLR-008.1 · LLR-008.2 · LLR-008.3 · PDR condition C14 (AT-042 mutation aimed at `HelpScreen`) |
| Base | `554314f` (Inc-1b branch point) · commit `3d3e999` |
| Authors | tests and the reconciliation proposal drafted by `deepseek/deepseek-v4-pro` (one short `opencode run`, no hang); RED re-run, reconciliation applied, lane run and packet by the orchestrator (Claude Opus 5.5) |

## 1 · What changed
- New AT-044 node: a doubled `?` from a map opens exactly one legend; the screen stack does not grow.
- AT-042's two missing arms: `test_tc_r25` parametrised over `[SCOPE_MAP, SCOPE_HOME, SCOPE_APP]` (the `[app]` arm is the smallest set) and the new `test_tc_r25b_a_screen_declaring_no_scope_presents_the_app_set`.
- AT-041 annotated on its node; AT-033/034/035 written as mentions (backticked), not declarations — they are retired with the deferred US-N14 (`#D23`).
- Reconciliation applied from `03-increments/inc4-reconciliation-proposal.md`: ledger `.64` (realisations) and `.65` (AT-044's real mutation), BACKLOG B-100 and B-101 marked DONE, §3.1 rows AT-044 / AT-042 and the HLR-007 / LLR-007.1 negative controls corrected.

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `tests/test_double_question_mark.py` | test (new) | HLR-007, LLR-007.1, AT-044 | `test_at_044_a_doubled_question_mark_opens_one_legend` |
| `tests/test_repair_layout.py` | test | HLR-008, LLR-008.1, LLR-008.3, AT-041, AT-042 | `test_tc_r25` parametrised incl. `[app]`; new `test_tc_r25b_…`; AT-041 comment on `test_at_r12_…` |
| `.dev-flow/2026-10-08-data-safety-batch/01-requirements.md` | record | HLR-007, HLR-008 | §3.1 AT-044/AT-042 rows; retired ids as mentions; negative-control wording |
| `.dev-flow/2026-10-08-data-safety-batch/01-requirements-ledger.md` | record | LLR-007.1, LLR-008.3 | entries `.64`, `.65` |
| `.dev-flow/BACKLOG.md` | record | HLR-007, HLR-008 | B-100, B-101 → DONE |
| `.dev-flow/2026-10-08-data-safety-batch/03-increments/inc4-reconciliation-proposal.md` | record (new) | HLR-008 | the drafter's proposal and RED evidence |
| `.dev-flow/2026-10-08-data-safety-batch/evidence/inc4-default-lane.transcript` | record (new) | n/a — evidence | the lane below, profile path scrubbed |

Source files: **0**.

## 3 · RED counterfactual and mutation verdicts (executed)

| Node | Mutation (one-site edit of `mapper/`, restored byte-identical) | Verdict |
|---|---|---|
| AT-044 | bind `?` in the help seat (design-named) | **survived — inert**: `HelpScreen` defines no `action_help` |
| AT-044 | drop `SCOPE_HELP` from `MODAL_SCOPES` (design-named) | **survived — inert**: the modal binding chain cuts the app off |
| AT-044 | app-scope `?` row → `priority=True` | **killed** (`1 failed`), re-run independently by the orchestrator; `mapper/keymap.py` sha256 `8555441e0f14be59…` before = after |
| AT-042 no-scope (`test_tc_r25b`) | `HelpScreen` default `scope=SCOPE_APP` → `SCOPE_HELP` (`mapper/screens/help.py:288`) | **killed**; `help.py` sha256 `17011f2f…` before = after |
| AT-042 `[app]` | `self.scope = scope` → a non-app constant in `HelpScreen.__init__` | **killed**; hash restored |

The two inert design mutations are recorded (ledger `.65`) rather than dropped: the discriminating mutation is the one the existing guard `test_no_screen_binds_the_question_mark_at_priority` protects against.

## 4 · Test results
- File level (orchestrator): `tests/test_repair_layout.py tests/test_double_question_mark.py` → 21 passed; `tests/test_help_scope.py` → 50 passed (drafter).
- **One complete default lane (orchestrator):** `python -B -W error::SyntaxWarning -m pytest -q -rf -p no:cacheprovider` → `2831 passed, 24 deselected, 3 xfailed in 1424.24s`, `EXIT_CODE=0` (`evidence/inc4-default-lane.transcript`).
- **Ledger:** base 2831 collected (Inc-1a) − 0 + 3 (`at_044`, `tc_r25[app]`, `tc_r25b`) = 2834 = 2831 passed + 3 xfailed. ✓

## 4b · Independent review
⚠ owed — `code-reviewer` runs at the integration of Inc-1b + Inc-4.

## 5 · Risks
- AT-044 certifies the modal-chain guarantee only against the `priority=True` regression; a future `action_help` on `HelpScreen` would change which mutations bite (recorded, ledger `.65`).

## 6 · Pending items / deviations
- Deviation: the design's AT-044 mutations were inert; replaced by `priority=True` (ledger `.65`).
- Validator `V2` still lists AT-001, AT-002, AT-002a (Inc-1b) and AT-005a/b, AT-014a–d (Inc-2) — owned by those increments.

## 7 · Suggested next task
Integrate with Inc-1b, then Inc-2 in small DeepSeek units.

## Addendum (orchestrator, 2026-10-09)
- **§4b `code-reviewer`:** OK to advance · no findings; AT-044 and AT-042 arms sound; merged ledger 2890 = 2887 + 3 (collection, executed).
