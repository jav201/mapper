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
| Standing authorization | <none — every gate is asked, or: <the commission, quoted or cited> (runtime cannot prompt)> |
| First gate | <the first gate run's exit code and what its `V7` line reported> |
| Premises / RC-1 | <the verified `origin/main` tip, or: no origin — RC-1 not possible, local tip <sha>; each premise the batch rests on> |

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
| C6 | not fired | no new input-parsing/validation surface; the commit-affordance change is UX (family D), not a new parser |
| C7 | not fired | no network exposure |
| C8 | not fired | no new rendering of file-derived text into markup/ANSI/HTML sinks |
| D | fired | US-001 changes what the operator sees and touches (the inspector's save affordance); the batch objective itself names the UX change → prototype round per the standing operator rule (2026-09-04) |
| E | fired | 4 stories (≥3); B-36 is a live data-loss defect (high risk declared at intake) |
| F | not fired | installed flow `2026-10-04-rev100` manifest matches (orchestrator verified V7); backlog refreshed `2026-10-08` (`.dev-flow/BACKLOG.md:9`) |

## Where we are

<one paragraph: station, what the last gate decided, what is owed next>

## Objective

<the batch objective, restated>

## Per-story / per-station status

| Story / station | Status | Notes |
|---|---|---|
| US-001 | REFINE | design ruling (save affordance) pending; prototype round + operator verdict before implementation (standing rule 2026-09-04) |
| US-002 | READY | write AT-044 test (doubled `?`); reconcile AT-025b → existing `LLR-N13.1.5` nodes in `tests/test_repair_cycles.py` |
| US-003 | REFINE | B-101 mis-attributes AT-033/034/035 to US-N13 (they are US-N14, deferred); AT-041/042 already realised under AT-R12 / TC-R25 / TC-R26 names |
| US-004 | SPIKE | FLAKE-2 mechanism is a hypothesis (framework key `left` vs seat-declared own-scope group); needs reproduction |
| P0 | in progress — intake drafted, awaiting orchestrator gate | §2.6/§2.7/§2.8 drafted; Triggers table filled; gate decision owed |

## Roadmap + increment plan

<the increments this batch expects, in order>

## Key decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-08 | <decision> | <reason> |

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
