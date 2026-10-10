# PLAN — mapper — Batch 2026-10-09-hygiene-batch

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
| Batch | 2026-10-09-hygiene-batch |
| Objective | Draft-save code hygiene (B-103) and the `INC9G-R8` record debt (B-99) |
| Standing authorization | Asked 2026-10-09 through AskUserQuestion. Operator answers, verbatim: scope «B-103 + B-99 (Recomendado)»; mode and authorization «core + autónomo + merge (Recomendado)». The decision-recording acknowledgement was not asked as a separate question this batch. The recording obligation is unconditional and is honoured here, in `state.json.decisions_log` and in `05-close.md`. Merge only after a clean final PR-level qa-reviewer pass; a HIGH finding blocks. |
| First gate | `devflow-validate.py --brief` on `903e0f0` (before the rollover): exit 1, with 1 block, which is `V7` — `SKILL.md` differs from the hash the bundle's manifest declares (`29e9c490927538a7 != a2751ce96e24b120`). It is external: the installed flow bundle was changed outside this project, and this batch does not modify `~/.claude`. |
| Premises / RC-1 | RC-1 (a): `git fetch origin`; `origin/master` = `903e0f0e46f6c7ef894f86b25dc14d2255c1728b`, which is the local tip, so no rebase was needed. RC-2: `git ls-remote --exit-code --heads origin master` → `903e0f0…`, newest commit 2026-10-09 13:02:40 -0600. The premises are in `01-requirements.md` §2.7 (4 TRUE). |

## Triggers

| Id | Verdict | Probe output |
|---|---|---|
| A1 | not fired | no new module: the planned files are `mapper/app.py` and `tests/test_draft_hygiene.py` |
| A2 | not fired | one product module touched (`mapper/app.py`) |
| A3 | not fired | `MapScreen.guard_open()` is consumed only by `MapperApp` in the same module; no other module calls `MapScreen` members it changes (`grep -rn "_draft_guard_open" mapper` → `app.py` only) |
| A4 | not fired | one lane, one increment |
| B1 | not fired | `grep -rn "_draft_guard_open\|_last_save_error" tests --include=*.py` → no output |
| B2 | not fired | no file moves |
| B3 | not fired | no golden directory exists under `tests/` (`find tests -type d -iname "*golden*" -o -iname "*snap*"` → no output); the golden census tests (`test_repair_golden_census.py`) read paint snapshots, and this change paints nothing new |
| B4 | not fired | no artifact produced for another component |
| C1–C7 | not fired | `devflow-scan-spec.py` flagged only `expose`, which is a Python method here (`01-requirements.md` §6.3) |
| C8 | not fired | no text reaches markup; strings unchanged |
| D1 | not fired | nothing the user sees or touches changes (behaviour-preserving; strings, keys and layout unchanged) |
| D2 | not fired | no prototype |
| E1 | not fired | 2 stories, 1 increment |
| E2 | not fired | risk declared low (B-103 rows are LOWs) |
| E3 | not fired | internal tool, not a client deliverable |
| F1 | fired | the local `flow_hash` differs from the manifest (`V7`, see First gate). Control C-45 PULL: recorded. No pull or edit of `~/.claude`, because another session owns the flow bundle (rev101). |
| F2 | not fired | the backlog was refreshed at the data-safety close (B-102, B-103 added in `2b6315d`) |

## Where we are

P0 is closed and P1 is drafting. The contract `01-requirements.md` holds 2 stories, 2 HLR and 3 LLR. The next gate is P1 → P2.

## Objective

1. Close B-103: a typed failed-save error slot on `MapScreen`, a public `guard_open()` that the quit walk reads, and F5 ruled.
2. Close B-99: re-verify the `HOME-1` kill on master and record it.

## Per-story / per-station status

| Story / station | Status | Notes |
|---|---|---|
| US-001 | READY | B-103 |
| US-002 | READY | B-99. The witness already exists (Inc-9h, 2026-10-01); the debt is a stale record unless the kill fails on master |
| P0 | approved | self-approved under the standing authorization |

## Roadmap + increment plan

1. **Increment 001:**
   - `mapper/app.py`: the typed slot, `guard_open()`, and the `action_quit` read;
   - `tests/test_draft_hygiene.py`: structural test (TC-001, TC-002);
   - AT-060 / AT-061 tagged on their existing nodes;
   - the `HOME-1` mutation transcript (AT-062).
2. **P4:** full suite. **P5:** core close, backlog rows B-99 and B-103 marked DONE.

## Key decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-09 | Mode `core`, autonomous + merge (operator) | internal refactor, no visible change |
| 2026-10-09 | B-99 handled as re-verification, not new work | `increment-034-inc9h.md` §4 already records the witness and the `HOME-1` kill; ui-next-02's P4 copied a stale gap. Executed evidence decides. |
| 2026-10-09 | F5: no change | `01-requirements.md` §6.2 |
| 2026-10-09 | AT ids start at AT-060 | they avoid colliding with the `test_at_0NN` nodes of earlier batches (the highest on disk is `test_at_055`) |

## Risks / watch-items

- `V7` stays red at every gate. It is external, and it is recorded rather than worked around.
- A behaviour-preserving refactor can drift visibly. The guard against that is the existing draft-save and draft-exit suites, plus the full suite at P4.

## Conventions honored

- No operator paths in tracked files (`tests/test_no_operator_paths.py`).
- Real keys in Textual tests.
- Max 4 source files.
- Neutral commit identity.

## Out-of-scope carries

- B-102 (accepted draft-model residuals): revisit only if observed.

## Test ledger

| Suite / command | Last run | Result |
|---|---|---|
| full suite (data-safety P4, `cab8181`) | 2026-10-09 | 2920 passed / 0 failed |

## Decision log

| Station | Date | Decision |
|---|---|---|
| P0 | 2026-10-09 | approved — US-001, US-002 READY; F1 fired (external `V7`), all others not fired |
