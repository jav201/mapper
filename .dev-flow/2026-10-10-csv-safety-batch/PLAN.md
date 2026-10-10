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
| A1 | not fired | no module created or moved; the change lives inside `mapper/store.py`, `mapper/import_csv.py`, `mapper/screens/import_preview.py` |
| A2 | **fired** | three modules touched (store, import_csv, screens/import_preview) |
| A3 | **fired** | `preview_csv` gains a collision record that `screens/import_preview.py` consumes; `MapStore.save` gains a refusal its callers (`_save_or_toast`) consume |
| A4 | not fired | two sequential increments, one lane |
| B1 | **fired** | `grep -rlE "MapStore|preview_csv|_ImportPreviewScreen" tests/` → 40 files of other batches assert these symbols; reverse census owed per increment |
| B2 | not fired | no file moves |
| B3 | not fired | no golden captures the import preview or the store bytes (AT-065 goldens cover the map screen only) |
| B4 | **fired** | the saved map (`.mmd` + sidecar) is consumed by `MapStore.load`; AT-074 is the output-then-consume test |
| C1 / C2 / C3 / C4 / C5 / C7 | not fired | no auth, secret, external integration, sensitive data, destructive DB or network surface |
| C6 | **fired** | the CSV file is an input surface; the refusal parses operator-supplied ids |
| C8 | **fired** | the refusal sentence paints CSV-derived ids — they must pass `darkside.plain` (no markup/ANSI injection), asserted in LLR-CSV.2.2 |
| D1 | **fired** | the preview paints a new refusal sentence in its existing panel; no new widget, layout or key — copy only, stated verbatim in HLR-CSV.2 |
| D2 | not fired | no prototype in another technology |
| E1 | **fired** | 3 user stories |
| E2 / E3 | not fired | not declared high risk at intake; no client/regulated deliverable |
| F1 | **fired** | the installed flow bundle differs from its manifest (`V7`, external — the same notice every recent batch carries) |
| F2 | not fired | backlog refreshed this session (B-108..B-114) |

## Where we are

Batch open: P0 (this plan) and P1 (`01-requirements.md` + ledger) authored from the unit
brief. Defect B-114 reproduced from evidence on `origin/feat/perf-batch`
(`perf0b-slug-reach.transcript`: `small_save_error: null`, `small_load_error: MapStoreError
... (ParseError)`); loader invariants enumerated from `mapper/mermaid.py` and
`mapper/store.py`. **P2 round 1 recorded in `02-review.md`: `iterate-to-refine`** (5
blockers, 11 majors, 8 minors; architect + qa, both read-only). The orchestrator ruled
R1–R10 (any collision blocks; the store check is a round trip; neutral cycle sentence and
precedence collision > multi-parent > cycle; two items routed to backlog as B-115/B-116;
`_open_import` drive path; the sha256 no-write oracle; `line_num` semantics; per-layer
negative controls; pinned grammar + boundary additions; `compare=False, repr=False` and the
`mapper/model.py` increment-1 ownership) — applied to the contract, ledger and proposal in
P1 iteration 1 (`LED-2026-10-10-csv-safety-batch.2`…`.4`). **P2 round 2 recorded in
`02-review.md`: `approve-with-conditions` on both artifacts (architect + qa).** The
orchestrator ruled R11–R16 (the round trip compares the node-id set and the edge set only —
NOT the root, forest drift to B-117 + a forest regression requirement LLR-CSV.1.3; honest
complexity + a P4 numeric threshold for the added parse; the root-collision fixture's
preview sentence is the COLLISION sentence; AT-072's negative control is the record-keyed
preview mutation, not M1; the preview refuses at the `s` keypress before the save-as prompt
with a pinned toast; a mutation-id glossary + the `splitlines()` caveat) — applied to the
contract, ledger, proposal and this plan (`LED-2026-10-10-csv-safety-batch.5`…`.10`), the
PDR was sealed `approved with conditions` (`design/PDR-2026-10-10-csv-safety-batch.md`), and
B-117 was appended to `BACKLOG.md`. Next owed: the PDR gate's `V7` line, then increment 1
(store refusal).

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

- **Increment 1 — the store refuses what its loader refuses.** `mapper/store.py`: `MapStore.save` validates by round trip (ruling R2, amended by ruling R11): refuse when `mermaid.parse(mermaid.dump(G))` raises or yields a different node-id set or edge set ((parent, child) pairs) — the root is NOT compared (a forest's root drifts on reparse: `dump` writes edges before parentless nodes, `parse` takes the first parentless node in text order — pre-existing, B-117) — covering multi-parent, cycle, newline title, arrow title and duplicate edges; the check parses the exact text `save` writes (one `dump` per save — the same string is written, ruling R12), raising `MapStoreError` with a plain-language reason before any byte is written; `_save_or_toast` already turns that into the existing toast and returns `False`. `mapper/model.py`: the `Graph.csv_collisions` field (`compare=False, repr=False`), the `CsvCollision`/`CsvRow` types and `Graph.multi_parent_ids()` (the preview's multi-parent sentence needs it; the store check does not). Tests: `tests/test_csv_safety_store.py` (unit TCs + no-partial-write digest oracle over every workspace file incl. `mapper.db`/`*.tmp`, plus the forest regression `test_save_accepts_legacy_forest_after_edit` — LLR-CSV.1.3). Complexity is stated honestly (ruling R12): `dump` is already O(N·E) in its parentless-node loop (`mapper/mermaid.py:152-153`, B-33 territory, not fixed here); the added cost is one `parse`, budgeted ≤ 25 % of `MapStore.save` wall time on a 6 000-node wide tree, measured once at P4 (median of 3) as evidence — not a wall-clock assertion in the suite. Source files: 2 (`mapper/model.py`, `mapper/store.py`) — per ruling R10 / architect B3.
- **Increment 2 — the preview says why, before the user tries to save.** `mapper/import_csv.py`: `preview_csv` records which original rows (raw id + line number via `csv.DictReader.line_num`) collapsed into which slug. `mapper/screens/import_preview.py`: `_ImportPreviewScreen.refresh_canvas` paints the existing "could not draw the preview" panel (header kept, sentence in body) with the exact refusal sentence — precedence collision > multi-parent > cycle (rulings R1/R3/R13: the root-collision fixture carries a non-empty record, so the COLLISION sentence wins at the preview; the store refuses the same graph as a cycle) — and `_ImportPreviewScreen.action_save` refuses at the `s` keypress, BEFORE pushing the save-as prompt (no name is asked for a save that cannot happen), by emitting the same toast mechanism the store refusals use at the call site — severity `error`, pinned text exactly `the CSV has colliding ids — nothing was saved; see the preview`, no exception raised (ruling R15, LLR-CSV.2.3). Tests: `tests/test_csv_safety_preview.py` (AT-072/073/074 + AT-072b/c/d through `MapperApp` + `run_test` + real keys, driven by `_open_import` from `tests/test_seed_safety.py:107-117` through its `s` step; the colliding fixtures assert NO prompt screen was pushed, the pinned toast text, and the workspace sha256 oracle unchanged; AT-074 still types the name). Source files: 2.
- **Validation / close.** RED proof per increment (revert product change only, confirm FAIL, restore byte-identical, re-run GREEN); full-suite gate re-run after any post-review repair; `04-validation.md` + `05-close.md`.

## Key decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-10 | D1 — the store refuses what its loader refuses: `MapStore.save` validates against the loader's invariants and raises `MapStoreError` BEFORE writing any byte; `_save_or_toast` toasts and returns `False`, so nothing is saved and the preview stays open | reuses the existing guarded save surface (`mapper/screens/common.py:217`, G6-C-F2/G6-C-F3); no new UI; guarantees the round-trip invariant `save(G)` ok ⇒ `load()` = G |
| 2026-10-10 | D2 — the preview says why: the existing "could not draw the preview" panel of `_ImportPreviewScreen.refresh_canvas` names the colliding CSV rows (original ids + line numbers) when the preview graph violates an invariant, in the exact sentence stated in HLR-CSV.2 | changes painted text in an existing slot only; the operator learns the cause before pressing save; text reaches the panel, not the toast, because the toast shows the exception TYPE only (G6-C-F2) |
| 2026-10-10 | D3 — `preview_csv` records which original rows collapsed into which slug (raw id + line number per contributing row), so the message can name them | the slug alone cannot be mapped back to source rows; auto-generated ids (`row-N`, title slugs for empty id column) are recorded the same way |
| 2026-10-10 | Rejected: silently disambiguating ids (`a-b`, `a-b-2`) | it changes the user's data without telling them, and their `parent` references become ambiguous — the map they get is not the map they typed |
| 2026-10-10 | Reused surfaces, no prototype round | the refusal flows entirely through `MapStore.save` → `_save_or_toast` → existing toast and the existing preview panel; no new screen, key, or widget |
| 2026-10-10 | D3 pin (ruling R15) — the preview's record-keyed refusal happens at the `s` keypress, BEFORE the save-as prompt is pushed (no name is asked for a save that cannot happen), by the same toast mechanism at the call site, severity `error`, pinned text `the CSV has colliding ids — nothing was saved; see the preview`; no exception is raised | qa MED-3 + architect B6: when the refusal fires was unpinned, and `_save_or_toast` cannot toast without a store raise — the refusal names its own toast at the call site |
| 2026-10-10 | D4 — sentence precedence collision > multi-parent > cycle: the root-collision fixture carries a non-empty `csv_collisions` record, so the preview paints the COLLISION sentence; its reclassification as a cycle governs the STORE layer only (the store refuses the graph as a cycle — its refusal remains a store unit case) | ruling R13 (qa HIGH-1): the boundary text contradicted LLR-CSV.2.2 and the precedence rule; §5 fixtures and HLR-CSV.2 now agree |
| 2026-10-10 | D5 — the round trip compares the node-id set and the edge set ((parent, child) pairs) only; the root is NOT compared, because a forest's root drifts on reparse (`dump` writes edges before parentless nodes, `parse` takes the first parentless node in text order — pre-existing) | ruling R11 (architect A7/B4, qa 4): comparing the root would refuse every save of a forest map that opens today; the drift is recorded as B-117 and pinned by the forest regression LLR-CSV.1.3 |

## Risks / watch-items

- Toast wording rule G6-C-F2 (`mapper/screens/common.py:217`): the toast shows the exception type only, never `str(e)` — the row-naming text must live in the preview panel, never in the toast · medium · D2 pins the sentence on the panel; AT-073 reads the panel's Static source.
- Cycle evidence: the preview comment at `mapper/screens/import_preview.py:60-62` records that a circular `parent` column builds a cyclic graph without passing `mermaid.parse`, and `MapStore.save` already refuses cycles (LLR-R01.5) — measured in the modular batch (increment-001 §1). This batch must keep that guard green and extend the refusal sentence family to cycles · low · AT boundary catalog includes cycle via parent column and self-parent.
- Root-collision boundary: if one colliding row IS the root, the graph may pass a naive "one parent per node" check yet round-trip with a different root · medium · LLR-CSV.3.1's round-trip equality (root included) is the oracle; boundary catalog carries "duplicate where one is the root".
- `row-N`/title-slug auto-ids can collide too (two empty-id rows with the same title) · low · LLR-CSV.2.1 records collisions from auto-generated ids as first-class rows.
- Operator-path leak guard A-110 (`tests/test_no_operator_paths.py`): no absolute path or account name may reach any painted string or tracked file · low · the refusal sentence and the pinned toast interpolate only CSV ids and line numbers, all routed through `darkside.plain`.
- Forest root drift (ruling R11 → **B-117**): a forest's root changes on reload because `dump` writes edges before parentless nodes and `parse` takes the first parentless node in text order — pre-existing; the round-trip check must NOT compare the root, or every forest save is refused · medium · LLR-CSV.1.3's `test_save_accepts_legacy_forest_after_edit` pins that the check accepts a legacy forest after an edit; the drift itself is backlog B-117.

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
