# Requirements Document — mapper — Batch 2026-10-10-csv-safety-batch

> **Artifact language**
> This template is the canonical **English scaffold**. Generate the artifact in the batch's development language (`state.json` `language`). For Spanish batches, translate the **prose** — section headers and guidance — **and never a label**, and use `deberá` as the normative keyword (≡ `shall`). The normative RULES in this preamble are **language-independent** and enforced regardless of artifact language.

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/guides/req-template.md` and its part 2, `templates/guides/req-template.part2.md`, explain each field below and the rules that read them. It ships with the flow and is not copied into this batch.

> **Reserved field names.** The **field names and block keywords below are language-independent** — the
> validator parses them literally and they are never translated:
> `Validation` · `Acceptance test(s)` · `Boundary catalog` · `Negative control` · `Premise evaluation` · `Fork preconditions` · `Ledger` · `Requirement` · `⏸ DEFER`
> Everything else on this page — headings, guidance, the prose in every cell — is translated with the batch.
> **One strategy, not two:** the flow ships no alias table, so a translated label is read as an ABSENT one and the rule keyed on it reports a true-sounding silence.
> **And one FLOW-WIDE reserved token, read out of this artifact by `V42` no matter which template minted it:** `⏸ DEFER`. It is a MARKER rather than a field name, which is why it is stated here *and* in `/dev-flow` §Language of artifacts rather than in a per-template list — a deferral can be written in any batch artifact, including the ones that carry no block at all.

---

## 1. Introduction

### 1.1 Purpose
*(Informative text. Describes the document's objective.)*

Specify the requirements for B-CSV safety (backlog B-114): a CSV import must never
produce a map that cannot be re-opened. Two CSV rows whose ids slugify to the same id
collapse into one node with two parents; the import preview renders the collapsed
graph, the save persists it, and re-open fails in `MapStore.load` with the loader's
"multiple parents (out of MVP scope)" refusal. This batch makes the store refuse —
before writing any byte — what its loader refuses, and makes the import preview name
the colliding rows so the operator can fix the source data.

### 1.2 Scope
*(What this batch covers and what it does NOT cover.)*

Covers: the round-trip invariant of `MapStore.save`/`MapStore.load` (multi-parent
refusal added; cycle refusal already enforced at LLR-R01.5 and kept); the collision
record `preview_csv` keeps of slug-collapsed rows; the refusal sentence the import
preview paints; acceptance tests AT-072…AT-074 through the real app.

Does NOT cover: accepting multi-parent maps end to end (DAG model — out of MVP
scope); any change to the loader (`MapStore.load`, `mermaid.parse`) — the loader is
the invariant oracle; the perf batch whose evidence proved the defect.

### 1.3 Definitions, acronyms, abbreviations
| Term | Definition |
|------|------------|
| slug collision | two or more CSV rows whose `id` (or auto-generated id) maps through `slugify` to the same node id |
| loader invariants | the properties `MapStore.load` requires of a persisted map: every node has at most one parent (`mapper/mermaid.py:84-86`), the graph has no cycle (`mapper/mermaid.py:123`), and the `.mmd`/`_nodos.yml` pair is intact (the sidecar `_mmd_hash` fingerprint, `mapper/store.py`) |
| round-trip invariant | for every graph G: `save(G)` succeeds ⇒ `load()` returns G; `save(G)` fails ⇒ no file in the workspace changed |
| refusal panel | the existing "could not draw the preview" panel painted by `_ImportPreviewScreen.refresh_canvas` (`mapper/screens/import_preview.py:72-76`) |

### 1.4 References
*(Related documents, standards, external tickets.)*

- `.dev-flow/BACKLOG.md` B-114 (this batch's defect; evidence: `origin/feat/perf-batch` `.dev-flow/2026-10-10-perf-batch/evidence/perf0b-slug-small.csv` and `perf0b-slug-reach.transcript`).
- `mapper/import_csv.py` (`preview_csv`), `mapper/screens/import_preview.py`, `mapper/screens/common.py` (`_save_or_toast`), `mapper/store.py` (`MapStore.save`, LLR-R01.5), `mapper/mermaid.py` (`parse`, line 85).
- `tests/test_draft_save.py` (E-1 pilot helpers reused by the ATs), `tests/test_g6_store_surrogates.py` (the G6-C-F4 preview-save flow pattern).

### 1.5 Document overview
*(How this document is structured.)*

§2 overall description (product perspective, source user stories with DoR, premise
evaluation, fork preconditions); §3 high-level requirements; §4 low-level
requirements + Information Flow Contract; §5 validation strategy; §7 the ledger
(authored as a separate file, `01-requirements-ledger.md`).

---

## 2. Overall description

### 2.1 Product perspective
*(How the change fits into the larger system.)*

mapper persists maps as a `.mmd` pair (graph text + `_nodos.yml` sidecar) in a
workspace directory. The CSV import path is: operator picks a CSV →
`preview_csv(path)` builds a `Graph` → `_ImportPreviewScreen` renders it → `s` opens
the "save as" prompt → `_save_or_toast` guards `store.create`/`store.save` → the
workspace holds the pair → re-open runs `MapStore.load` → `mermaid.parse`. The defect
lives in the asymmetry: the build-save leg never runs the loader's checks, so a graph
the loader refuses can be persisted. This batch closes the asymmetry at the save
boundary and explains it at the preview boundary — both are existing surfaces.

### 2.2 Product functions
*(High-level list of functional capabilities.)*

- `MapStore.save` validates every graph against the loader's invariants and refuses
  (raising `MapStoreError`) before writing any byte.
- `preview_csv` records every slug collision with the contributing rows' original
  ids and line numbers.
- `_ImportPreviewScreen.refresh_canvas` paints the refusal panel naming the
  colliding rows (or the cycle) when the preview graph violates an invariant.

### 2.3 User characteristics
*(Roles, permissions, expected experience levels.)*

A single operator role: edits mind maps through the TUI, imports CSVs exported from
spreadsheets (ids may carry spaces, case, punctuation). No administrative surface is
involved.

### 2.4 Constraints
*(Technological, regulatory, business.)*

- The loader is the invariant oracle and does not change (`mermaid.py` line 85's
  "out of MVP scope" wording is the product's own scope statement).
- The toast shows the exception type only (G6-C-F2, `mapper/screens/common.py:217`);
  explanatory text ships in the preview panel, never in the toast.
- UI strings English-only; colours from `mapper/darkside.py` tokens; no operator
  path or account name may reach any painted string (guard A-110).

### 2.5 Assumptions and dependencies
*(What we take for granted. If an assumption fails, the batch is invalidated.)*

- `slugify` is the single id normaliser on both the build leg (`preview_csv`) and the
  parse leg (`mermaid.parse` node ids), so a collision detected at build time is a
  collision the loader would refuse. (Verified as premise 1; the parse leg's
  multiple-parent refusal is the loader side of the same invariant.)
- `_save_or_toast` remains the single guarded call site for screen-initiated saves
  (G6-C-F2/G6-C-F3), so one `MapStoreError` covers every save path.
- pytest + Textual `run_test` pilot remain the test substrate (Textual 8.2.8).

### 2.6 Source user stories

| ID | User Story | Source | DoR status |
|----|------------|--------|------------|
| US-CSV-001 | As a mapper operator, I want the app to refuse to save a CSV import that cannot be re-opened, so that my workspace never holds a map that errors on open. | B-114 (evidence `perf0b-slug-reach.transcript`) | READY |
| US-CSV-002 | As a mapper operator, I want the import preview to tell me which CSV rows collide (their original ids and line numbers) before I try to save, so that I can fix the ids and import again instead of losing the import to a re-open error. | B-114 + orchestrator decision D2 | READY |
| US-CSV-003 | As a mapper operator, I want a valid CSV to keep importing, saving and re-opening unchanged, so that the safety checks never cost me the working path. | regression guard demanded by the round-trip invariant | READY |

#### Refinement log (one block per story)

**US-CSV-001 — the store refuses what the loader refuses**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = mapper operator · outcome = an unopenable map is never persisted; a refused save changes nothing on disk · why = B-114 measured a saved map that fails `load` with a ParseError-derived MapStoreError · out of scope = DAG/multi-parent maps, loader changes.
- **Feasibility (E, S):** implementation path = extend `MapStore.save`'s existing pre-write validation (LLR-R01.5 cycle check) with the multi-parent check; `_save_or_toast` already toasts `MapStoreError` and returns False · dependencies/unknowns = none — all surfaces exist · fits one batch? = yes.
- **Evaluability (T) — behavioral, black-box:** "When I import a colliding CSV and press `s`, I observe the toast, no files in the workspace, and the preview still open."
- **Open questions:** none.
- **Classification:** `READY` — behavioral criterion observable through the shipped save flow.

**US-CSV-002 — the preview names the colliding rows**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = mapper operator · outcome = the preview panel names the colliding rows (original ids + line numbers) and says the map cannot be saved · why = the operator needs the source rows to fix the data; a bare "could not draw" hides them · out of scope = auto-fixing/renaming ids (rejected: silent disambiguation, decision D-rejected in PLAN.md).
- **Feasibility (E, S):** implementation path = `preview_csv` records collisions; `refresh_canvas` paints the refusal panel when the preview graph violates an invariant · dependencies/unknowns = none · fits one batch? = yes.
- **Evaluability (T) — behavioral, black-box:** "When I open a colliding CSV, I observe the preview panel sentence naming rows 5 (id 'a-b') and 6 (id 'A B')."
- **Open questions:** none.
- **Classification:** `READY`.

**US-CSV-003 — the working path is untouched**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = mapper operator · outcome = a valid CSV saves via the preview and re-opens identical · why = the safety checks must not tax the happy path · out of scope = import format changes.
- **Feasibility (E, S):** implementation path = e2e round-trip assertion through the real save flow · fits one batch? = yes.
- **Evaluability (T):** "When I import a valid CSV, press `s`, name the map, and re-open it, I observe the same nodes, edges and titles."
- **Classification:** `READY**.

### 2.7 Premise evaluation (C-43) — MANDATORY, one row per premise

| # | Premise, as a truth-apt proposition | Tier | Verdict | Executed evidence (command output / `file:line` — **NOT** a citation of another document) | Disposition |
|---|---|---|---|---|---|
| 1 | The loader refuses a node with two parents: `mermaid.parse` raises `ParseError` on the second parent edge of any node. | code | ✅ TRUE | `mapper/mermaid.py:84-86` — `if cid in child_to_parent: raise ParseError(f"Line {line_no}: node '{cid}' has multiple parents (out of MVP scope)")` (read via `sed -n '60,130p' mapper/mermaid.py`) | relied on; loader left untouched |
| 2 | `MapStore.save` currently performs NO multi-parent check: its only pre-write validation is the cycle guard. | code | ✅ TRUE | `mapper/store.py:810-833` — `save` body: `cycle = graph.find_cycle(); if cycle is not None: raise MapStoreError(...)` then `dump`/`_build_sidecar`/two-phase write; no parent-count check (read via `sed -n '810,870p' mapper/store.py`) | relied on; increment 1 adds the check |
| 3 | The defect reproduces end to end on the evidence branch: the colliding CSV saves cleanly and fails to re-open. | measurement | ✅ TRUE | `git show origin/feat/perf-batch:.dev-flow/2026-10-10-perf-batch/evidence/perf0b-slug-reach.transcript` prints `"small_save_error": null` and `"small_load_error": "MapStoreError: could not read the card of dup: dup_nodos.yml unreadable (ParseError)"` for `perf0b-slug-small.csv` (ids `a-b` / `A B`) | relied on; the batch's raison d'être |
| 4 | `_save_or_toast` catches any exception from the write, toasts, and returns `False`, leaving the calling screen open. | code | ✅ TRUE | `mapper/screens/common.py:217-260` — `except Exception as e: screen._last_save_error = type(e).__name__; if toast: ... return False` | relied on; no new save plumbing |
| 5 | The toast shows the exception TYPE only (G6-C-F2), so explanatory text must ship in the preview panel, not the toast. | code | ✅ TRUE | `mapper/screens/common.py` docstring at `:240` — "the toast names the map id and the exception TYPE only, never `str(e)`" | D2 pins the sentence on the panel |
| 6 | A cyclic `parent` column reaches the preview without passing `mermaid.parse`, but `MapStore.save` already refuses cycles (LLR-R01.5). | code | ✅ TRUE | `mapper/screens/import_preview.py:60-62` comment ("a CSV whose `parent` column is circular builds a cyclic graph without ever passing through `mermaid.parse`") + `mapper/store.py:826-828` cycle guard in `save` | cycle cases ride the existing guard; this batch extends the preview sentence family |
| 7 | The next free acceptance-test number is AT-072. | measurement | ✅ TRUE | `grep -rohE 'AT-0[0-9]+' tests/ REQUIREMENTS.md \| sort -u \| tail -3` → `AT-069`, `AT-070`, `AT-071` | AT-072…AT-074 assigned |

- **Premise evaluation:** 7 premise(s) · ✅ TRUE — all premises verified against code or executed evidence; none undecidable.

### 2.8 Fork preconditions (C-52) — MANDATORY, and the declared empty when the batch does not fork

| # | Condition (`C-52`) | Discharged? | The executed evidence |
|---|---|---|---|
| 1 | **Frozen contract** — no shared interface is touched inside a lane; one that must change returns to the trunk (trigger A3) | ✅ | single lane; the only shared seam is `MapStore.save`'s pre-validation (additive — new `MapStoreError` raise before the existing writes; signature and happy-path behaviour unchanged) |
| 2 | **Disjoint FILE sets**, not just modules — two lanes may not edit the same file, not even different regions | ✅ | one lane — file set `{mapper/store.py, mapper/import_csv.py, mapper/screens/import_preview.py, tests/test_csv_safety_store.py, tests/test_csv_safety_preview.py}` |
| 3 | **Crossed reverse census** — family B run per lane and **shared before starting**; the trunk's act, impossible from inside a lane | ✅ | not applicable — one lane |
| 4 | **One owner of the trunk** — requirements, traceability, backlog and spec are never written from a lane | ✅ | requirements owned by this batch's P1 unit (orchestrator); no lane writes them |

- **Fork preconditions:** none — this batch runs one lane; the four conditions are each discharged trivially as declared above.

---

## 3. High-level requirements (HLR)

### HLR-CSV.1 — the store refuses what its loader refuses
- **Traceability:** US-CSV-001
- **Ledger:** LED-2026-10-10-csv-safety-batch.1
- **Statement:** When `MapStore.save(map_id, graph)` is called with a graph that violates a loader invariant — any node has more than one parent, or the graph has a cycle — the system shall raise `MapStoreError` with a plain-language reason BEFORE writing or replacing any byte of the workspace, so that no map the loader would refuse can be persisted.
- **Rationale (informative):** measured on `origin/feat/perf-batch`: the colliding CSV (`a-b` / `A B`) saved with `save_error: null` and failed re-open with a ParseError-derived `MapStoreError` (premise 3). The store already refuses cycles (LLR-R01.5, added because the same asymmetry left an unloadable file listed with 0 nodes); the multi-parent half is the open defect. Orchestrator decision D1: the invariant is `save(G)` ok ⇒ `load()` = G and `save(G)` fails ⇒ no workspace file changed — the store refuses what its own loader refuses, on the existing `_save_or_toast` surface, with no new UI.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_csv_safety_store.py` (nodes to be created in increment 1: `test_save_refuses_multi_parent_graph`, `test_save_refuses_cycle_still`, `test_refused_save_changes_no_workspace_byte`); e2e through `tests/test_csv_safety_preview.py::test_at_072_refused_save_toasts_and_writes_nothing`.
- **Numeric pass threshold:** exit code 0; for every fixture graph in the boundary catalog either `save` raises `MapStoreError` AND the sha256 digest of every workspace file is unchanged, or `save` succeeds AND `MapStore.load(map_id)` returns a graph equal to the saved one (same node ids, edges, root and titles).
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** importing the colliding CSV and pressing `s` shows the existing toast, writes no file into the workspace, and leaves the import preview open; re-open is impossible because there is nothing to re-open.
  - **Shipped surface:** `MapStore.save` (`mapper/store.py`) behind `_save_or_toast` (`mapper/screens/common.py:217`) and the import-preview save flow (`s` → "save as" prompt, `mapper/keymap.py:223`).
  - **Acceptance test(s):** AT-072
  - **Boundary catalog (QC-3):** ☑ empty — a 0-row/0-node CSV saves and re-opens as an empty map (no nodes ⇒ no invariant to violate) ☑ boundary — single row; duplicate slug where one colliding row is the root; self-parent (1-cycle) ☑ invalid — duplicate slug (two rows), three-way collision, auto-id collision (two empty-id rows sharing a title) ☑ error — cycle via the `parent` column; the colliding perf evidence CSV itself.
  - **Negative control:** executed in increment 1 — mutation M1: delete the multi-parent check in `MapStore.save` (keep the cycle check) → `test_save_refuses_multi_parent_graph` goes RED (save succeeds; the paired `load` then raises). Stored as a transcript per lesson B-112(2).

---

### HLR-CSV.2 — the preview names the colliding rows
- **Traceability:** US-CSV-002
- **Ledger:** LED-2026-10-10-csv-safety-batch.1
- **Statement:** When the import preview graph violates a loader invariant, `_ImportPreviewScreen.refresh_canvas` shall paint the existing refusal panel (the "could not draw the preview" slot) with a sentence naming the responsible CSV rows instead of drawing the graph, using this exact wording — for a slug collision: `CSV rows {n1} (id '{raw1}') and {n2} (id '{raw2}') collapse into the node id '{slug}'; a map can hold only one parent per node, so rename the duplicated ids and import again.` (for three or more contributing rows the row list is comma-joined with `and` before the last; for a cycle: `the parent column builds a cycle ({a → b → a}); a saved map must be a tree, so fix the parent references and import again.`) — where each `{nk}` is the row's 1-based line number in the CSV file and each `{rawk}` is the id exactly as typed in that row.
- **Rationale (informative):** orchestrator decision D2: the operator must learn the cause BEFORE pressing save, from the surface they are already looking at. The text ships in the panel because the toast shows the exception type only (G6-C-F2, premise 5). Decision D3 makes the sentence possible: `preview_csv` records which original rows collapsed into which slug. The rejected alternative — silently disambiguating ids (`a-b`, `a-b-2`) — changes the user's data without telling them and makes their `parent` references ambiguous.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_csv_safety_preview.py::test_at_073_preview_names_the_colliding_rows` (to be created in increment 2).
- **Numeric pass threshold:** exit code 0; the `#import-preview-canvas` Static's source contains the exact sentence above with the correct line numbers and raw ids for each colliding fixture, byte-for-byte after `darkside.plain` normalisation.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** on opening the colliding CSV, the preview panel says the collision sentence naming rows 5 (id 'a-b') and 6 (id 'A B') — not a silently collapsed graph.
  - **Shipped surface:** `_ImportPreviewScreen.refresh_canvas` (`mapper/screens/import_preview.py:55-78`), data from `preview_csv` (`mapper/import_csv.py`).
  - **Acceptance test(s):** AT-073
  - **Boundary catalog (QC-3):** ☑ empty — no collision ⇒ the panel draws the graph as today (no sentence) ☑ boundary — collision on the root row; auto-id collision (empty id column, same title twice); three-way collision (list grammar with `and`) ☑ invalid — the two-row slug collision; the perf evidence CSV verbatim ☑ error — cyclic `parent` column ⇒ the cycle sentence naming the cycle path.
  - **Negative control:** executed in increment 2 — mutation M2: make `refresh_canvas` paint the graph (skip the invariant branch) or drop the collision record from `preview_csv` → `test_at_073_preview_names_the_colliding_rows` goes RED (sentence absent). Stored as a transcript.

---

### HLR-CSV.3 — the working path is untouched
- **Traceability:** US-CSV-003
- **Ledger:** LED-2026-10-10-csv-safety-batch.1
- **Statement:** When a CSV with no slug collision and no cycle is imported and saved through the import preview, the system shall persist the map and `MapStore.load` shall return a graph with the same node ids, edges, root and titles as the preview graph (the round-trip invariant on the happy path).
- **Rationale (informative):** the safety checks must never tax the working path; this HLR is the regression guard that keeps the new validation honest — including the root-collision boundary, where a naive parent-count check could pass while the persisted map re-opens with a different root (the round-trip equality, root included, is what bites).
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_csv_safety_preview.py::test_at_074_valid_csv_saves_and_reopens_identical` (to be created in increment 2); unit round-trip nodes in `tests/test_csv_safety_store.py` (increment 1).
- **Numeric pass threshold:** exit code 0; reloaded graph equal to the preview graph: same node-id set, same edge set (parent/child pairs), same `root_id`, same titles — 0 differences.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** a valid CSV imports, the preview draws the graph, `s` + a name saves it, and opening the map shows the identical tree.
  - **Shipped surface:** the same import-preview save flow as HLR-CSV.1, plus `MapStore.load`.
  - **Acceptance test(s):** AT-074
  - **Boundary catalog (QC-3):** ☑ empty — empty CSV: preview shows an empty graph and save/re-open round-trips as an empty map ☑ boundary — single-row CSV; deepest-nesting valid CSV from the fixtures ☑ invalid — none applies (the happy path admits only valid input) ☑ error — none applies.
  - **Negative control:** mutation M3: make `mermaid.dump` omit node titles (or skip the sidecar write) → the round-trip node goes RED (reloaded graph unequal / unloadable). Executed in increment 1.

---

## 4. Low-level requirements (LLR)

> Each LLR decomposes an HLR into a verifiable property at the implementation level.
> Same regime: EARS syntax owed in `full`, recommended in `core`. ID format: `LLR-<HLR>.<M>`.

### LLR-CSV.1.1 — `MapStore.save` refuses a graph the loader would refuse
- **Traceability:** HLR-CSV.1
- **Ledger:** LED-2026-10-10-csv-safety-batch.1
- **Statement:** The `MapStore.save` pre-write validation (`mapper/store.py`) shall reject any graph in which a node has more than one parent by raising `MapStoreError` naming the duplicated child id, and shall keep rejecting cyclic graphs (LLR-R01.5), in both cases before any byte is written; the check shall use the graph model's own parent relation (each node id appears as a child in at most one edge), not a text-level heuristic.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_csv_safety_store.py::test_save_refuses_multi_parent_graph tests/test_csv_safety_store.py::test_save_refuses_cycle_still` (to be created in increment 1).
- **Numeric pass threshold:** assert `MapStoreError` raised for every multi-parent fixture (two-row collision, three-way collision, collision-on-root, auto-id collision) and for the cyclic and self-parent fixtures; assert the happy-path fixtures (empty, single row, valid tree) raise nothing — 0 unexpected outcomes.
- **Negative control:** mutation M1 (delete the multi-parent check, keep the cycle check) → RED, as recorded in HLR-CSV.1.
- **Boundary catalog:** ☑ empty (empty graph saves) ☑ boundary (single row; collision where one row is the root) ☑ invalid (two-row/three-way/auto-id collisions) ☑ error (cycle via parent column; self-parent).

### LLR-CSV.1.2 — a refused save changes no workspace byte
- **Traceability:** HLR-CSV.1
- **Ledger:** LED-2026-10-10-csv-safety-batch.1
- **Statement:** The validation of LLR-CSV.1.1 shall run before the two-phase write begins (before `mermaid.dump`, the temp-file writes and the `.replace` calls), so that a refused save leaves every pre-existing workspace file — including a previously saved version of the same map id — byte-identical.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_csv_safety_store.py::test_refused_save_changes_no_workspace_byte` (to be created in increment 1) — sha256 digest of every workspace file captured before the refused save and compared after; includes the case where the map id already exists with prior content.
- **Numeric pass threshold:** 0 files changed; 0 digest mismatches across all refused-save fixtures.
- **Negative control:** mutation M1b: move the validation to after the first temp-file replace → digest of the target `.mmd` changes → RED.
- **Boundary catalog:** ☑ error — refused save over a pre-existing map (overwrite attempt) is the load-bearing boundary; the rest is covered by LLR-CSV.1.1's fixtures.

### LLR-CSV.2.1 — `preview_csv` records every slug collision with its source rows
- **Traceability:** HLR-CSV.2
- **Ledger:** LED-2026-10-10-csv-safety-batch.1
- **Statement:** `preview_csv` (`mapper/import_csv.py`) shall record, for every node id that more than one CSV row produced, the list of contributing rows with each row's 1-based line number in the CSV file and the id exactly as typed in that row (including auto-generated ids from the empty-id-column path), exposed on the returned graph or alongside it for the preview screen to read.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_csv_safety_preview.py::test_preview_csv_records_collisions` (to be created in increment 2).
- **Numeric pass threshold:** for the colliding fixtures the record names exactly the expected (line number, raw id) pairs — 0 missing, 0 extra; for non-colliding fixtures the record is empty.
- **Negative control:** mutation M2b: stop appending to the collision record → `test_preview_csv_records_collisions` RED; downstream AT-073 also RED.
- **Boundary catalog:** ☑ boundary (auto-id collision; collision on the root row) ☑ invalid (two-row, three-way collisions) — empty/single-row fixtures assert an empty record.

### LLR-CSV.2.2 — the refusal panel paints the exact collision sentence
- **Traceability:** HLR-CSV.2
- **Ledger:** LED-2026-10-10-csv-safety-batch.1
- **Statement:** `_ImportPreviewScreen.refresh_canvas` (`mapper/screens/import_preview.py`) shall paint the refusal panel with the exact sentence fixed in HLR-CSV.2 — interpolated with the colliding rows' line numbers and raw ids from LLR-CSV.2.1's record (cycle case: the cycle path from `graph.find_cycle()`) — instead of rendering the graph, whenever the preview graph violates a loader invariant; every interpolated piece shall pass through `darkside.plain`, and all styling shall come from `mapper/darkside.py` tokens (the existing `INK`/`MUT` pattern of the slot).
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_csv_safety_preview.py::test_at_073_preview_names_the_colliding_rows` plus the cycle-sentence node (to be created in increment 2).
- **Numeric pass threshold:** exit code 0; the Static source matches the exact sentence template byte-for-byte after `darkside.plain` normalisation, with correct line numbers/ids per fixture.
- **Negative control:** mutation M2 (paint the graph anyway / generic message) → RED, as recorded in HLR-CSV.2.
- **Boundary catalog:** ☑ invalid (two-row collision) ☑ error (cycle via parent column; self-parent) ☑ boundary (three-way list grammar; collision on the root row).

### LLR-CSV.3.1 — happy-path round-trip equality
- **Traceability:** HLR-CSV.3
- **Ledger:** LED-2026-10-10-csv-safety-batch.1
- **Statement:** For every preview graph that passes the LLR-CSV.1.1 validation, `MapStore.save` followed by `MapStore.load` on the same map id shall return a graph equal to the saved one — same node-id set, same parent/child edge set, same `root_id`, same node titles — including for the empty graph and the single-node graph.
- **Validation:** `test (unit)`
- **Executed verification:** round-trip nodes in `tests/test_csv_safety_store.py` (to be created in increment 1); e2e twin `tests/test_csv_safety_preview.py::test_at_074_valid_csv_saves_and_reopens_identical` (increment 2).
- **Numeric pass threshold:** 0 differences on every fixture (node ids, edges, root, titles).
- **Negative control:** mutation M3 (dump omits titles / sidecar skipped) → RED, as recorded in HLR-CSV.3.
- **Boundary catalog:** ☑ empty (empty graph round-trips) ☑ boundary (single row; deepest fixture tree) — invalid/error classes are covered by LLR-CSV.1.1.

### Information Flow Contract (IFC) — C-54

> Part A in every batch; Part B when the system's boundary has components a consumer can address independently. The block syntax, its fields and the rules that read them are in `templates/ifc-template.md`, which ships with the flow and is not copied into this batch.

- **Part A — flows:**

```text
FLOW csv-rows-to-preview
SOURCE: the CSV/TSV file picked by the operator
NODES:
  - preview_csv (mapper/import_csv.py) — owner: LLR-CSV.2.1 (builds the graph AND the collision record)
  - _ImportPreviewScreen.refresh_canvas (mapper/screens/import_preview.py) — owner: LLR-CSV.2.2 (paints graph or the refusal sentence)
SINK: the #import-preview-canvas Static painted on screen
```

```text
FLOW preview-to-workspace
SOURCE: the preview graph + the operator's save keypress (s) and typed map name
NODES:
  - _ImportPreviewScreen.action_save (mapper/screens/import_preview.py) — owner: existing surface
  - _save_or_toast (mapper/screens/common.py:217) — owner: existing surface (toast + False on raise)
  - MapStore.save validation (mapper/store.py) — owner: LLR-CSV.1.1, LLR-CSV.1.2 (refuse BEFORE any byte)
SINK: the workspace .mmd + _nodos.yml pair (written only when validation passes)
```

```text
FLOW workspace-to-graph
SOURCE: the workspace .mmd + _nodos.yml pair
NODES:
  - MapStore.load (mapper/store.py) — owner: existing surface (invariant oracle, untouched)
  - mermaid.parse (mapper/mermaid.py) — owner: existing surface (multi-parent refusal :85; cycle refusal :123)
SINK: the Graph the app renders on re-open (LLR-CSV.3.1's equality oracle)
```

- **Part B — boundary decomposition:** no — no component of the boundary is addressable on its own; the only public entry points are `preview_csv` and `MapStore`, both exercised end to end by the ATs.

---

## 5. Validation strategy

### 5.1 Methods

> **Two layers** (per the Two-layer validation rule). Every batch declares BOTH:
> - **Layer A — white-box / functional (`TC-NNN`):** validates the HLR/LLR mechanism (the HOW). Methods: `test`, `inspection`, `analysis`.
> - **Layer B — black-box / behavioral acceptance (`AT-NNN`):** validates the user story's outcome through the shipped surface (the WHAT). Method: `acceptance`.

Layer A — unit/integration tests in `tests/test_csv_safety_store.py` (TC: save
refusal, no-partial-write digest oracle, round-trip equality, collision record) and
`tests/test_csv_safety_preview.py` (TC: sentence painting, cycle sentence).
Layer B — acceptance tests through the real app (`MapperApp(tmp_path)` +
`run_test(size=...)` + `pilot.press`, import-preview flow per the G6-C-F4 pattern in
`tests/test_g6_store_surrogates.py:555-600`, E-1 helpers imported from
`tests/test_draft_save.py`):

- **AT-072** (US-CSV-001 / HLR-CSV.1): import the colliding CSV (`a-b` / `A B` +
  parents, the perf evidence shape) through the real import flow; press `s`, answer
  the "save as" prompt with a real name; observe the toast, an empty workspace (no
  `.mmd`/`_nodos.yml` written), and the preview still open.
- **AT-073** (US-CSV-002 / HLR-CSV.2): same CSV; assert the `#import-preview-canvas`
  Static source contains the exact HLR-CSV.2 sentence naming rows 5 (id 'a-b') and 6
  (id 'A B').
- **AT-074** (US-CSV-003 / HLR-CSV.3): a valid multi-row CSV; save via `s` + name;
  re-open with `MapStore.load` and assert node ids, edges, root and titles identical
  to the preview graph.

### 5.2 Batch acceptance criteria
- 100% of LLRs (CSV.1.1 … CSV.3.1) covered by at least one executed test with pass result, each with an executed negative control (mutation M1/M1b/M2/M2b/M3) recorded as a transcript.
- AT-072, AT-073, AT-074 pass through `MapperApp` + `run_test` with real keys; every AT owns a node distinct from its LLR nodes.
- The existing suite stays green: `MapStore.save`'s cycle guard (LLR-R01.5) and the G6 toast-wording tests are re-run, not just the new files.
- No requirement without an assigned validation method; no painted string carrying an operator path or account name (guard A-110 stays green).
- Boundary evidence: empty, single row, duplicate slug, three-way collision, cycle via parent column, self-parent, collision where one row is the root, auto-id collision — each named by a fixture in the two new test files.

---

## 6. Appendices (optional)

### 6.1 Extended glossary
### 6.2 Relevant design decisions
D1/D2/D3 and the rejected silent-disambiguation alternative are recorded in PLAN.md §Key decisions and mirrored in the HLR rationales above.
### 6.3 Open risks
Root-collision boundary (a naive parent-count check passes while the persisted map re-opens with a different root) — mitigated by LLR-CSV.3.1's round-trip equality including `root_id`.
### 6.4 Phase-1 reconciliation log — moved to the ledger (§7)

### 6.5 Requirement amendments — moved to the ledger (§7)

---

## 7. The ledger — authored as a SEPARATE FILE

The fence below is the ledger's seed: `devflow-init.py` writes it to `01-requirements-ledger.md`. The shape of an entry is in the field guide.

```markdown
# Requirements ledger — mapper — Batch 2026-10-10-csv-safety-batch

> Append-only. Entries are added in chronological order and never rewritten. The live
> contract is `01-requirements.md`; this file records how it came to say what it says.
> Every entry names the requirement it amends; every requirement names its entries. `V26`
> compares the two sets of pairs both ways.

_No entries yet. The first amendment to the live contract writes the first one, in the
shape the field guide's §7 shows (`req-template.part2.md` in the guide directory init prints), and nothing
above this line is ever edited._
```
