# PLAN — mapper — Batch 2026-10-09-canon-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language.
> **Owed in.** `core` ✓ · `full` ✓
> Seeded by `/dev-flow-init` step 4 in both modes; the living plan is owed at every gate
> that follows (`/dev-flow` §Living plan is the rule's home).

> **Field guide:** `templates/docs/plan-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

The living compendium of this batch: where-we-are · objective · per-story/per-station status ·
roadmap + increment plan · key decisions · risks/watch-items · conventions honored ·
out-of-scope carries · test ledger · decision log (the human-readable mirror of `state.json`).
**Create at batch open and update at every gate and significant checkpoint** — the
orchestrator presents the full plan in-conversation at each phase gate.

## Header

| Field | Value |
|---|---|
| Project | mapper |
| Batch | 2026-10-09-canon-batch |
| Objective | B-105 (the hygiene requirements appended to the canon under namespaced ids) and B-104 (the unused `re` import) |
| Standing authorization | Asked 2026-10-09 through AskUserQuestion, after the operator's «Dale, agrégalo y continúa.». The operator's answers, verbatim: B-105 «Anexar al canon (Recomendado)»; mode and authorization «core + autónomo + merge (Recomendado)». The decision-recording obligation is honoured unconditionally. Merge only after a clean final PR-level qa-reviewer pass; a HIGH finding blocks. |
| First gate | `devflow-validate.py --brief` right after the rollover, on `558b415`: 1 block, `V7`, which is external (the installed flow bundle differs from its manifest) |
| Premises / RC-1 | `git fetch origin`; `origin/master` = `558b41522c7d` = the local tip. The premises are in `01-requirements.md` §2.7 (4 TRUE). |

## Triggers

| Id | Verdict | Probe output |
|---|---|---|
| A1 | not fired | no module created; files `REQUIREMENTS.md`, `mapper/app.py`, two new tests |
| A2 | not fired | one product module (`mapper/app.py`), one import line |
| A3 | not fired | no interface changes (`re` is unused: `grep -n "[^a-z_]re\." mapper/app.py` → no output) |
| A4 | not fired | one lane |
| B1 | not fired | `grep -rln REQUIREMENTS tests --include=*.py` → `tests/test_repair_cycles.py`, `tests/test_vocabulary_declaration.py`; both read a batch's own `01-requirements.md` (`test_repair_cycles.py:30-33`, `test_vocabulary_declaration.py:297`), not the canon. No test asserts `app.py`'s import list |
| B2 | not fired | no file moves |
| B3 | not fired | no golden directory under `tests/` |
| B4 | fired | `REQUIREMENTS.md` is consumed by the flow's `V22` and `--fold-canon`. Control (corrected at P2, `LED-2026-10-09-canon-batch.1`): the close fold folds THIS batch's five `CAN` rows (it reads only the active batch's headings). The five `HYG` rows are verified by AT-063. The close gate re-runs `V22` and expects the `CAN` ids folded and `0 refused` |
| C1–C8 | not fired | no input, network, secret, auth or markup surface; `devflow-scan-spec.py` is run at P1 |
| D1, D2 | not fired | nothing the user sees changes |
| E1–E3 | not fired | 2 stories, 1 increment, low risk, internal |
| F1 | fired | `V7`: the local flow hash differs from the manifest. Recorded; `~/.claude` is not touched (owned by the rev101 session) |
| F2 | not fired | the backlog was refreshed at the hygiene close (B-104, B-105) |

## Where we are

P0 is closed. P1: the contract is drafted, with 2 stories, 2 HLR and 3 LLR, all with namespaced ids.

## Objective

1. Append the five hygiene requirements to `REQUIREMENTS.md` as `HLR-HYG.*` / `LLR-HYG.*`, each naming its record id.
2. Guard canon-id uniqueness.
3. Remove `import re` and guard unused imports in `app.py`.

## Per-story / per-station status

| Story / station | Status | Notes |
|---|---|---|
| US-001 | READY | B-105 |
| US-002 | READY | B-104 |
| P0 | approved | self-approved under the standing authorization |

## Roadmap + increment plan

1. **Increment 001:** worker units in isolated worktrees, each verified by the orchestrator before integration.
   - **U1, DeepSeek:** `tests/test_requirements_canon.py`.
   - **U2, Kimi:** `tests/test_app_imports_used.py`.
   - **Orchestrator:** the five canon rows (deterministic append), the one-line import removal, the mutation runs and the record.
2. **P4:** full suite. **P5:** core close.

## Key decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-09 | Append, never rename (operator: «Anexar al canon») | sealed records and canon rows are never rewritten |
| 2026-10-09 | Namespaced ids from this batch on (`CAN`) | B-105's root cause; the flow-side fix is reported to the operator |
| 2026-10-09 | Worker routing announced at kickoff: DeepSeek U1, Kimi U2, Sonnet reviews | operator: announce model use; «sigue intentando sacarle provecho» |

## Risks / watch-items

- `V7` stays red (external).
- The fold's normalisation must match exactly, or a later fold could treat a row as different. The close gate re-runs the fold and expects `0 refused`.

## Conventions honored

- Append-only canon; sealed records untouched.
- No operator paths in tracked files.
- Max 4 source files.
- Namespaced requirement ids.

## Out-of-scope carries

- The flow-side B-105 fix (template seed, fold): the operator decides; it belongs to the flow's own backlog.
- B-102.

## Test ledger

| Suite / command | Last run | Result |
|---|---|---|
| full suite (hygiene P4, `092875e`) | 2026-10-09 | 2924 passed / 3 xfailed / 0 failed |

## Decision log

| Station | Date | Decision |
|---|---|---|
| P0 | 2026-10-09 | approved — US-001, US-002 READY; B4 and F1 fired |
