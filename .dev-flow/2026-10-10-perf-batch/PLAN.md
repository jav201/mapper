# PLAN — mapper — Batch 2026-10-10-perf-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language.
> **Owed in.** `core` ✓ · `full` ✓
> Seeded by `/dev-flow-init` step 4 at both levels; the living plan is owed at every gate
> that follows (`/dev-flow` §Living plan is the rule's home).

> **Field guide:** `templates/guides/plan-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

The living compendium of this batch: where-we-are · objective · per-story/per-station status ·
roadmap + increment plan · key decisions · risks/watch-items · conventions honored ·
out-of-scope carries · test ledger · decision log (the human-readable mirror of `state.json`).
**Create at batch open and update at every gate and significant checkpoint** — the
orchestrator presents the full plan in-conversation at each phase gate.

## Header

| Field | Value |
|---|---|
| Project | mapper |
| Batch | 2026-10-10-perf-batch |
| Objective | Performance and scale (B-33): measure first, then bound and reduce the work a large map costs — open, keypress repaint, search, save/load |
| Standing authorization | full + autonomous + merge — operator: "Si, remedia rendimiento y escala." (2026-10-09), "sigue, usa kimi-for-coding como está" (2026-10-10); see `state.json` `standing_authorization` |
| First gate | <the first gate run's exit code and what its `V7` line reported> |
| Premises / RC-1 | <the verified `origin/main` tip, or: no origin — RC-1 not possible, local tip <sha>; each premise the batch rests on> |

## Triggers

The trigger evaluation `state.json`'s `triggers.record` points at: one row per trigger evaluated, fired or not.

| Id | Verdict | Probe output |
|---|---|---|
| A1 | **fired** | a shared render walk / layout cache may become its own module under `mapper/views/` (decided at ARQ) |
| A2 | **fired** | renderers (`mapper/views/layered.py`, `outline.py`, `radial.py`, `mapper/canvas.py`), `mapper/model.py`, `mapper/mermaid.py`, the mount path (`mapper/screens/map/painting.py`, `screen.py`) |
| A3 | **fired** | a `Graph` adjacency index changes an interface every renderer and the store consume |
| A4 | **fired** | three disjoint lanes are planned — renderer cost, model/serialisation cost, mount paint count — the first batch to use the modular split for parallel work |
| B1 | **fired** | renderer and `Graph` symbols are asserted by many other batches' tests (`grep -rlE "LayeredRenderer|OutlineRenderer|RadialRenderer|children_of" tests/`) |
| B2 | not fired | no file moves planned |
| B3 | **fired** | the AT-065 parity goldens (`evidence/mod_parity_118.txt`, `mod_parity_87.txt` of the modular batch, pinned in `tests/test_mod_parity.py`) and `tests/test_repair_golden_census.py` capture painted output — every remedy must keep them byte-identical; that is the batch's behaviour oracle |
| B4 | not fired | no new artifact consumed elsewhere (the `.mmd` text must stay byte-identical — asserted, not a new consumer) |
| C1–C8 | not fired | no auth, secrets, integration, sensitive data, destructive DB, input surface, network or new markup over file text |
| D1 | not fired for this scope | behaviour-preserving remedies paint identical output; the S-18 work budget (changes what is painted) is OUT of this batch's first scope and goes to a prototype round first |
| D2 | not fired | — |
| E1 | **fired** | ≥ 3 planned increments |
| E2 / E3 | not fired | — |
| F1 | **fired** | flow bundle differs from its manifest (`V7`, external) |
| F2 | not fired | backlog refreshed this session |

## Where we are

**P0, RESUMED 2026-10-10** after `2026-10-10-csv-safety-batch` merged (PR #18 `6dfffde`, state PR #19 `5cde04e`); master merged into this branch, `base_ref` re-stamped to `5cde04e`, the csv-safety log archived. Earlier: **P0, PAUSED 2026-10-10.** The measurement is done (`spike/perf-baseline.md` §1–§7; `evidence/perf0*-*.transcript`). The P0 spike also found a data-safety defect outside this batch's scope (B-114: a CSV import saves a map that cannot be re-opened). The operator ruled 2026-10-10 to fix it first in a short separate batch, opened in its own worktree per §Batch rollover; this batch resumes at P0's gate after that batch merges (rebase onto master, archive its log).

## Objective

Bound and reduce the work a large map costs. Measured (P0): opening a wide 2000-node map takes 4.8 s and 6000+ times out; every navigation key repaints the whole map (0.6–1.9 s at 2000–6000 nodes); mount paints three times; save is O(N·E) in the Mermaid dump; load is YAML-bound. The dense-DAG cost of B-33 (72.5 s) is not reachable by opening a saved map (the parser refuses multi-parent nodes).

## Per-story / per-station status

| Story / station | Status | Notes |
|---|---|---|
| P0 | in progress | measurement done; resumed after the B-114 batch merged |

## Roadmap + increment plan

To be planned at P1 from `spike/perf-baseline.md` §4 and §7 (candidates: incremental repaint per keypress; one paint at mount; linear Mermaid dump; then the render work budget S-18).

## Key decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-10 | pause at P0 for B-114 | operator ruling: data safety before performance |
| 2026-10-10 | resume at P0, rebased on master `5cde04e` | the csv-safety batch merged; its `MapStore.save` round-trip check adds one `parse` per save (+3.2 % at 6 000 nodes) — the save-cost baseline in `spike/perf-baseline.md` §7 predates it |

## Risks / watch-items

- Any remedy that changes what is painted (e.g. a work-budget degradation notice) needs a prototype verdict first · likely for S-18 · prototype round before implementing

## Conventions honored

- Worker model: Kimi `kimi-for-coding`; reviews by Claude; measurements by subprocess with timeouts, never in-process repeated apps (PERF0B harness hang)

## Out-of-scope carries

- Does not fix B-114 (separate batch) nor accept multi-parent maps end to end

## Test ledger

| Suite / command | Last run | Result |
|---|---|---|
| `python -B .dev-flow/2026-10-10-perf-batch/spike/perf_harness.py` (see baseline for args) | 2026-10-10 | baseline tables in `spike/perf-baseline.md` |
