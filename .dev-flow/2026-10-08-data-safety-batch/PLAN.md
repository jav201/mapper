# PLAN — mapper — Batch 2026-10-08-data-safety-batch

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
| Batch | 2026-10-08-data-safety-batch |
| Objective | Data safety and verification debt: B-36 (one keystroke durably overwrites a map and its sidecar) plus the unrealised acceptance tests B-100/B-101 and the legend paint flake B-98 |
| Standing authorization | Asked 2026-10-08. Operator, verbatim: autonomy and merge "Autónomo + merge (Recomendado)"; decision recording "Confirmado"; scope "B-36 + ATs + flake (Recomendado)"; mode "full (Recomendado)". Merge only after a clean final PR-level `qa-reviewer` pass; a HIGH finding blocks; TUI design still needs the operator's prototype verdict. |
| First gate | `devflow-validate.py --brief` at rollover (606510f): exit 0, 0 block; `V7` identical to the rev100 manifest; NOTICEs `V27` (empty log) and `V40` (`owner` omitted by A-110) |
| Premises / RC-1 | RC-1: `git fetch origin`; `origin/master` = `07dd930` (2026-10-08) = merge-base of `feat/data-safety-batch`. RC-2: `git ls-remote --exit-code --heads origin` exit 0, newest commit 2026-10-08. Premises: §2.7 of `01-requirements.md` |

## Triggers

The trigger evaluation `state.json`'s `triggers.record` points at: one row per trigger evaluated, fired or not.

| Id | Verdict | Probe output |
|---|---|---|
| A1 | not fired | no new module or boundary move; planned edits are to existing `mapper/widgets/inspector.py`, `mapper/app.py` and `tests/*` (judged — no module-map probe exists) |
| A2 | fired | the batch spans ≥2 modules: `mapper/widgets/inspector.py` + `mapper/app.py` (US-001) and `tests/` (US-002/003/004) |
| A3 | fired (judged, design-contingent) | US-001's candidate remedies alter the inspector→screen commit path — `FieldCommitted` (`mapper/widgets/inspector.py:365`) is consumed by `mapper/app.py:3344`; remedy (a) introduces a new `Input.Changed` message. The interface change is why US-001 is REFINE |
| A4 | not fired | no parallel increments planned at intake; the batch runs one lane |
| B1 | fired | `grep -rl "FieldCommitted" tests/` → `tests/test_inspector.py`, `tests/test_g6_store_surrogates.py`, `tests/test_worklist_safety.py`; `grep -rl "on_ficha_inspector_field_committed" tests/` → `test_inspector.py`, `test_g6_store_surrogates.py` — tests not owned by US-001's story |
| B2 | not fired | no file moves planned |
| B3 | not fired | `ls tests/goldens` → no such directory; `find . -name "*.golden"` → 0 files |
| B4 | not fired | no new artifact-producing change; US-001 changes WHEN `_save_or_toast` runs, not the `.mmd`/sidecar format |
| C1 | not fired | no auth change |
| C2 | not fired | no secrets handling |
| C3 | not fired | no external integration; the batch touches inspector/app/store/tests only |
| C4 | not fired | no new sensitive-data (credential/PII) surface; ficha persistence is pre-existing |
| C5 | not fired | no DB |
| C6 | fired (scanner) | `python devflow-scan-spec.py .dev-flow/2026-10-08-data-safety-batch/01-requirements.md` → `flags: escape`, `security_required: true`; the match is the Esc key in §2.6, recorded anyway (triggers only raise); questions answered in `01-requirements.md` §6.3 |
| C7 | not fired | no network exposure |
| C8 | not fired | no new rendering of file-derived text into markup/ANSI/HTML sinks |
| D1 | fired | US-001 changes what the operator sees and touches (the inspector's save affordance); the batch objective itself names the UX change → prototype round per the standing operator rule (2026-09-04) |
| E1, E2 | fired | 4 stories (≥3); B-36 is a live data-loss defect (high risk declared at intake) |
| F1, F2 | not fired | installed flow `2026-10-04-rev100` manifest matches (orchestrator verified V7); backlog refreshed `2026-10-08` (`.dev-flow/BACKLOG.md:9`) |

## Where we are

<one paragraph: station, what the last gate decided, what is owed next>

## Objective

<the batch objective, restated>

## Per-story / per-station status

| Story / station | Status | Notes |
|---|---|---|
| US-001 | REFINE | design ruling (save affordance) pending; prototype round + operator verdict before implementation (standing rule 2026-09-04) |
| US-002 | READY | write AT-044 test (doubled `?`); reconcile AT-025b → existing `LLR-N13.1.5` nodes in `tests/test_repair_cycles.py` |
| US-003 | READY | orchestrator ruling at P0: AT-033/034/035 RETIRED here (they belong to deferred US-N14, `#D23`); AT-041/042 reconciled to `test_at_r12…` / `test_tc_r25…` / `test_tc_r26…` |
| US-004 | READY | spike done (tester agent): race in the test's own `scroll_to` setup (`immediate=False`), not reflow; test-side fix at 4 sites; regression RED 2/2 → GREEN 2/2 under an injected delay |
| P0 | open — US-002/003/004 READY; US-001 waits on the operator's prototype verdict (gallery published 2026-10-08) | trigger evaluation recorded; C6 fired by the scanner |

## Roadmap + increment plan

<the increments this batch expects, in order>

## Key decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-08 | US-003 READY: AT-033/034/035 retired to US-N14, AT-041/042 reconciled | the canonical record (`…ui-next-batch-02/01-requirements.md:6090`) marks US-N14 deferred; the B-101 attribution was the orchestrator's own error at close |
| 2026-10-08 | US-002: reconcile AT-025b to the existing `LLR-N13.1.5` nodes, no new node | the behaviour is already pinned by five nodes (`tests/test_repair_cycles.py:501…664`); a duplicate node adds maintenance, not coverage |
| 2026-10-08 | P0 stays open for US-001 until the operator's prototype verdict; US-004 spike runs now | standing rule 2026-09-04 (prototype round before TUI design); keeps the batch moving without deciding the operator's design question |
| 2026-10-08 | `owner` omitted from `state.json` | A-110 forbids profile paths in tracked files; the project rule wins over the flow convention; `V40` NOTICEs it |
| 2026-10-08 | US-004 READY with a test-side fix at four `scroll_to` sites | the spike measured the race and refuted the reflow hypothesis; widening to the sibling sites closes the class, not the instance |
| 2026-10-08 | C6 recorded as fired | the spec scanner flagged `escape`; triggers only raise, even on a word-level false positive |

## Risks / watch-items

- <risk · likelihood · mitigation>

## Conventions honored

- <convention>

## Out-of-scope carries

- <what this batch deliberately does not do, and where it is tracked>

## Test ledger

| Suite / command | Last run | Result |
|---|---|---|
| <command> | <date> | <result> |
