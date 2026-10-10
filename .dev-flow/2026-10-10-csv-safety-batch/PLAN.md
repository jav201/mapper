# PLAN — mapper — Batch 2026-10-10-csv-safety-batch

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
| Batch | 2026-10-10-csv-safety-batch |
| Objective | B-114 data safety: a CSV import must never produce a map that cannot be re-opened. `MapStore.save` refuses what `MapStore.load` refuses (multi-parent graphs from slug collisions, cycles), before writing any byte; the import preview names the colliding CSV rows instead of drawing a graph the save will refuse. |
| Standing authorization | `state.json` `batch_objective` (B-114, quoted in Objective above) — the runtime cannot prompt; the commission is the batch objective itself, recorded in `state.json` at batch open. Orchestrator design decisions 1–3 (see Key decisions) are pre-authorised by the operator's unit brief; no gate re-ask is needed for them. |
| First gate | not yet run — this unit authored P0 (plan) and P1 (requirements) only; the first gate run and its `V7` line are owed at the PDR gate. |
| Premises / RC-1 | no `origin/main`; trunk is `origin/master` at `a36f63e` (verified `git rev-parse --short origin/master` + `git merge-base --is-ancestor origin/master HEAD` → ancestor-ok). Each other premise the batch rests on is evaluated in §2.7 of `01-requirements.md` with executed evidence. |

## Triggers

The trigger evaluation `state.json`'s `triggers.record` points at: one row per trigger evaluated, fired or not.

| Id | Verdict | Probe output |
|---|---|---|
| <A1 / B1 / …> | not evaluated in this unit | trigger probes are owed at the PDR gate; P0/P1 authored from the unit brief and measured premises only |

## Where we are

Batch open: P0 (this plan) and P1 (`01-requirements.md` + ledger) authored from the unit
brief. Defect B-114 reproduced from evidence on `origin/feat/perf-batch`
(`perf0b-slug-reach.transcript`: `small_save_error: null`, `small_load_error: MapStoreError
... (ParseError)`); loader invariants enumerated from `mapper/mermaid.py` and
`mapper/store.py`. Next owed: PDR gate, then increment 1 (store refusal).

## Objective

Restated from `state.json`: two CSV rows whose ids slugify to the same id (e.g. `a-b` and
`A B`) collapse into one node with two parents in `mapper/import_csv.py` (`preview_csv`:
`nid = slugify(raw_id)`, then `graph.add_node` overwrites and both rows add an edge). The
import preview renders it; the save persists it; re-open fails in `MapStore.load` →
`mapper/mermaid.py:85` "multiple parents (out of MVP scope)". Make the import and the
save refuse — with an explanation — what the loader refuses, so a saved map always
re-opens. Round-trip invariant: for every graph G, `save(G)` succeeds ⇒ `load()` returns
G, and `save(G)` fails ⇒ no file in the workspace changed.

## Per-story / per-station status

| Story / station | Status | Notes |
|---|---|---|
| US-CSV-001 (store refuses what the loader refuses) | READY | DoR in `01-requirements.md` §2.6; AT-072 |
| US-CSV-002 (preview names the colliding rows) | READY | DoR in `01-requirements.md` §2.6; AT-073 |
| US-CSV-003 (valid CSV still saves and re-opens) | READY | regression guard for the happy path; AT-074 |

## Roadmap + increment plan

- **Increment 1 — the store refuses what its loader refuses.** `mapper/store.py`: `MapStore.save` validates the graph against the loader's invariants (every node at most one parent — currently unchecked; cycle — already LLR-R01.5) and raises `MapStoreError` with a plain-language reason before any byte is written; `_save_or_toast` already turns that into the existing toast and returns `False`. Tests: `tests/test_csv_safety_store.py` (unit TCs + no-partial-write digest oracle). Source files: 1 (`mapper/store.py`).
- **Increment 2 — the preview says why, before the user tries to save.** `mapper/import_csv.py`: `preview_csv` records which original rows (raw id + line number) collapsed into which slug. `mapper/screens/import_preview.py`: `_ImportPreviewScreen.refresh_canvas` paints the existing "could not draw the preview" panel with the exact refusal sentence naming the colliding rows (ids + line numbers) when the preview graph violates an invariant, instead of drawing a graph the save will refuse. Tests: `tests/test_csv_safety_preview.py` (AT-072/073/074 through `MapperApp` + `run_test` + real keys). Source files: 2.
- **Validation / close.** RED proof per increment (revert product change only, confirm FAIL, restore byte-identical, re-run GREEN); full-suite gate re-run after any post-review repair; `04-validation.md` + `05-close.md`.

## Key decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-10 | D1 — the store refuses what its loader refuses: `MapStore.save` validates against the loader's invariants and raises `MapStoreError` BEFORE writing any byte; `_save_or_toast` toasts and returns `False`, so nothing is saved and the preview stays open | reuses the existing guarded save surface (`mapper/screens/common.py:217`, G6-C-F2/G6-C-F3); no new UI; guarantees the round-trip invariant `save(G)` ok ⇒ `load()` = G |
| 2026-10-10 | D2 — the preview says why: the existing "could not draw the preview" panel of `_ImportPreviewScreen.refresh_canvas` names the colliding CSV rows (original ids + line numbers) when the preview graph violates an invariant, in the exact sentence stated in HLR-CSV.2 | changes painted text in an existing slot only; the operator learns the cause before pressing save; text reaches the panel, not the toast, because the toast shows the exception TYPE only (G6-C-F2) |
| 2026-10-10 | D3 — `preview_csv` records which original rows collapsed into which slug (raw id + line number per contributing row), so the message can name them | the slug alone cannot be mapped back to source rows; auto-generated ids (`row-N`, title slugs for empty id column) are recorded the same way |
| 2026-10-10 | Rejected: silently disambiguating ids (`a-b`, `a-b-2`) | it changes the user's data without telling them, and their `parent` references become ambiguous — the map they get is not the map they typed |
| 2026-10-10 | Reused surfaces, no prototype round | the refusal flows entirely through `MapStore.save` → `_save_or_toast` → existing toast and the existing preview panel; no new screen, key, or widget |

## Risks / watch-items

- Toast wording rule G6-C-F2 (`mapper/screens/common.py:217`): the toast shows the exception type only, never `str(e)` — the row-naming text must live in the preview panel, never in the toast · medium · D2 pins the sentence on the panel; AT-073 reads the panel's Static source.
- Cycle evidence: the preview comment at `mapper/screens/import_preview.py:60-62` records that a circular `parent` column builds a cyclic graph without passing `mermaid.parse`, and `MapStore.save` already refuses cycles (LLR-R01.5) — measured in the modular batch (increment-001 §1). This batch must keep that guard green and extend the refusal sentence family to cycles · low · AT boundary catalog includes cycle via parent column and self-parent.
- Root-collision boundary: if one colliding row IS the root, the graph may pass a naive "one parent per node" check yet round-trip with a different root · medium · LLR-CSV.3.1's round-trip equality (root included) is the oracle; boundary catalog carries "duplicate where one is the root".
- `row-N`/title-slug auto-ids can collide too (two empty-id rows with the same title) · low · LLR-CSV.2.1 records collisions from auto-generated ids as first-class rows.
- Operator-path leak guard A-110 (`tests/test_no_operator_paths.py`): no absolute path or account name may reach any painted string or tracked file · low · the refusal sentence interpolates only CSV ids and line numbers, all routed through `darkside.plain`.

## Conventions honored

- English-only UI strings; colours from `mapper/darkside.py` tokens, keys from `mapper/keymap.py` — no hard-coded glyph or hex (import-scope save key is `s`, `keymap.py:223`).
- Tests drive the real app: `MapperApp(tmp_path)` + `app.run_test(size=...)` + `pilot.press(...)` — real keys, never `post_message`/`.focus()` shortcuts; helpers imported from `tests/test_draft_save.py` where they exist.
- pytest only from the worktree root, `-p no:cacheprovider`, single test files.
- No git mutations from batch units; the orchestrator commits.

## Out-of-scope carries

- Accepting multi-parent maps end to end (a DAG/forest map model) — out of MVP scope per `mapper/mermaid.py:86`; tracked in BACKLOG if ever wanted.
- The perf batch (`origin/feat/perf-batch`) — its evidence is only the defect's proof; no perf work here.
- Changing the loader (`MapStore.load`/`mermaid.parse`) — the loader is the invariant oracle; only the save side and the preview side move.

## Test ledger

| Suite / command | Last run | Result |
|---|---|---|
| `python -B -m pytest -q -p no:cacheprovider tests/test_csv_safety_store.py` | not yet created — owed in increment 1 | — |
| `python -B -m pytest -q -p no:cacheprovider tests/test_csv_safety_preview.py` | not yet created — owed in increment 2 | — |
