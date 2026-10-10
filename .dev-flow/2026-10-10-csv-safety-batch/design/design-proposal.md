# Design proposal — mapper — Batch 2026-10-10-csv-safety-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language
> The normative rules below are language-independent. **Where that language is declared:**
> `state.json`'s `language` key in `core` and `full`.

> **Reserved field names.** The **field names and block keywords below are language-independent** — the
> validator parses them literally and they are never translated:
> `Design proposal` · `7 · Forward-applicability table` · `⏸ DEFER`
> Everything else on this page — headings, guidance, the prose in every cell — is translated with the batch.
> **One strategy, not two:** the flow ships no alias table, so a translated label is read as an ABSENT one and the rule keyed on it reports a true-sounding silence.
> **Why a HEADING is reserved here and a FIELD NAME everywhere else:** `C-49`'s artifact is the §7 TABLE, and a rule that read a summary bullet instead of the rows would be reading a claim about the table rather than the table. `V52` therefore keys on this document's own H1 and on the §7 heading, which is why both are on the machine plane. **And one FLOW-WIDE reserved token, read out of this artifact by `V42` no matter which template minted it:** `⏸ DEFER`. It is a MARKER rather than a field name, which is why it is stated here *and* in `/dev-flow` §Language of artifacts rather than in a per-template list — a deferral can be written in any batch artifact, including the ones that carry no block at all.

> **Owed in.** `core` by trigger · `full` ✓
> **Source:** `/dev-flow-init` step 4's seed-by-level table, which is this fact's one home. A level marked `—` **does not owe this artifact, and its absence is not an omission**; `by trigger` means the station exists only when the `triggers` block fired, and `stations_active` in `state.json` is the authority for *this* batch. Where a SECTION or a gate row is owed more narrowly than the artifact, it says so on the row.

> **Where this lives: the VAULT + Drive**, not the repo — it is deliberation, and its traceability to
> code is weak. It is **cited by id** from the repo (`PDR-<batch_id>#D<n>`), never copied.
> What binds code — a frozen interface, a design characteristic — also lands in the **repo**, in the
> requirement or in `docs/ARCHITECTURE.md`. *The vault keeps the deliberation; the repo keeps the commitment.*

> **The forward-applicability rule (ISO/IEC/IEEE 15288).** Everything below must be NAMED as the input
> of a later activity. **If a section of this proposal is nobody's input, delete it — it does not belong
> in the PDR.** That rule is what allows this document to cost half the batch without being waste.

| Field | Value |
|---|---|
| Id | `PDR-2026-10-10-csv-safety-batch` |
| Requirements covered | `US-CSV-001 · US-CSV-002 · US-CSV-003 · HLR-CSV.1 · HLR-CSV.2 · HLR-CSV.3 · LLR-CSV.1.1 · LLR-CSV.1.2 · LLR-CSV.2.1 · LLR-CSV.2.2 · LLR-CSV.3.1` (all v1, Ledger: none) |
| Modules touched (from `docs/ARCHITECTURE.md`) | `model` · `store` · `import_csv` · `screens` (`screens/import_preview.py`) |
| Triggers that fired | `A2 · A3 · B1 · B4 · C6 · C8 · D1 · E1 · F1` |
| Author / reviewers | `architect` · `qa-reviewer` |

---

## 1 · Objective and scope

Close the build-save/load asymmetry B-114 measured (`origin/feat/perf-batch`,
`perf0b-slug-reach.transcript`: `small_save_error: null`, `small_load_error: MapStoreError …
(ParseError)`): a CSV import whose rows slug-collide (`a-b` / `A B`) collapses into one node with two
parents in `preview_csv` (`mapper/import_csv.py:57` `nid = slugify(raw_id)`, `:73` `graph.add_node`
overwrites, `:81` both rows add an edge); the save persists it; re-open fails in
`MapStore.load` → `mermaid.parse:85` "multiple parents (out of MVP scope)".

This design makes `MapStore.save` refuse — before writing any byte — every graph whose shape the
loader refuses (HLR-CSV.1), and makes `_ImportPreviewScreen.refresh_canvas` name the colliding CSV
rows (raw ids + 1-based line numbers) in the existing refusal panel, in the exact sentence HLR-CSV.2
fixes (HLR-CSV.2). The happy path — a valid CSV previews, saves and re-opens identical — is the
regression guard (HLR-CSV.3).

Will NOT do: accept multi-parent maps end to end (DAG model — out of MVP scope per
`mapper/mermaid.py:86`); touch the loader (`MapStore.load`, `mermaid.parse` — the invariant oracle);
silently disambiguate colliding ids; add any new screen, key, widget or toast wording.

## 2 · Modules and boundaries

| Module | What it owns here | What it exposes | What it must NOT reach into |
|---|---|---|---|
| `model` (`mapper/model.py`) | The loader-invariant predicate, new in this batch: `Graph.multi_parent_ids() -> list[str]` and the collision record value types `CsvCollision` / `CsvRow` (frozen dataclasses) plus one defaulted `Graph` field `csv_collisions` | Additive only: a new method, two new value types, one defaulted field on `Graph` | nothing — `model` has no outbound dependencies (`docs/ARCHITECTURE.md` §3) |
| `store` (`mapper/store.py`) | `MapStore.save`'s pre-write validation (`mapper/store.py:810-824`): keep the existing cycle guard (`:822-824`, LLR-R01.5) and add the multi-parent refusal next to it, both before `mermaid.dump` at `:826` | Same `save(map_id, graph) -> None` signature; one new `MapStoreError` raise | unchanged: `store` depends on `model` only — the new check is imported from `model`, so no new edge |
| `import_csv` (`mapper/import_csv.py`) | Collision detection in `preview_csv`'s first pass (`mapper/import_csv.py:49-74`): track every row's `(nid, line_no, raw_id)` and populate `graph.csv_collisions` for every slug produced by more than one row (including auto-generated `row-N` / title slugs from the empty-id path, `:54-56`) | Same `preview_csv(path: Path) -> Graph` signature — the record travels ON the returned `Graph` | unchanged: `import_csv` depends on `model` + `mermaid` (`slugify`) only; it still never writes anything |
| `screens` (`mapper/screens/import_preview.py`) | `_ImportPreviewScreen.refresh_canvas` (`mapper/screens/import_preview.py:55-78`): before rendering, run the same `model`-level invariant predicate on `self.preview_graph`; on violation paint the existing "could not draw the preview" panel (`:72-76`) with the exact HLR-CSV.2 sentence (collision or cycle wording) instead of rendering; on a clean graph render exactly as today | Same screen class, same `__init__(preview_graph, source_path)`, same `#import-preview-canvas` Static | unchanged: `screens` may import `model` (`docs/ARCHITECTURE.md` §3 `screens` row) — the predicate and the record are read from there; never `mapper.app` |

- Boundaries respected as declared in `docs/ARCHITECTURE.md`: ✓ — the load-bearing placement is the
  invariant predicate in `model`: `store` depends on `model` (§3 `store` row) and `screens` depends on
  `model` (§3 `screens` row), so ONE predicate serves both save and preview with zero new dependency
  edges. Putting it in `mermaid` would leave `screens` reaching for a format adapter it does not
  otherwise need; putting it in `store` is importable from `screens` (§3 allows `screens → store`)
  but would give the multi-parent scan two homes that can drift apart — the save side and the
  preview side would disagree on what is refusable. The
  §3 `model` row's ban ("any → `model`" is inbound-only) is untouched: `model` gains no imports.

### 2a · The loader's invariant list — the exact oracle (enumerated from code)

`mermaid.parse` (`mapper/mermaid.py:61-128`) refuses, per line of `.mmd` text:

1. **Unsupported syntax** — a non-empty, non-comment, non-header line matching neither the edge nor
   the node regex → `ParseError` (`mapper/mermaid.py:108`).
2. **Multiple parents** — a node id appearing as the child of a second edge while already in
   `child_to_parent` → `ParseError("… has multiple parents (out of MVP scope)")`
   (`mapper/mermaid.py:84-87`). Fires even when both edges name the *same* parent, because the
   membership test precedes any equality test.
3. **Cycle** — after the edge set builds, `graph.find_cycle()` non-None → `MermaidError(cycle)`
   (`mapper/mermaid.py:121-123`).

The sidecar reader (`MapStore.load`, `mapper/store.py:680-795`) refuses:

4. **Missing `.mmd`** → `MapStoreError` (`mapper/store.py:684-690`).
5. **Unreadable text** — `OSError` / `UnicodeDecodeError` on either file → typed `MapStoreError`
   (`mapper/store.py:697-704`).
6. **Sidecar YAML failure** — `YAMLError` / `ValueError` / `RecursionError` from `safe_load` →
   typed `MapStoreError` (`mapper/store.py:705-727`).
7. **Sidecar not a mapping** — top-level list/scalar → `MapStoreError` (`mapper/store.py:730-735`).
8. **`_graph_from_sidecar` graph-build failure** — wraps the parse-leg refusals 2 and 3 above:
   `MermaidError` restated as "the map has a cycle: …" (`mapper/store.py:738-741`); every other
   exception typed as `… unreadable (<TypeName>)` (`mapper/store.py:744-768`).
9. **`_mmd_hash` mismatch** — torn two-phase pair → **warning**, not refusal (`mapper/store.py:780-782`).

Of these, only **2 (multi-parent)** and **3 (cycle)** are properties of a *Graph* input; 1 and 4–8
are properties of persisted text the store's own writer produces and a `Graph` argument cannot
violate (refusal 2 is also re-enforced textually by 8). So `MapStore.save`'s pre-write validation
checks exactly two graph-shape invariants, in `model`:

- **I1 — at most one parent per node:** each node id appears as `child_id` in at most one edge.
  Detected in ONE pass over `graph.edges` building a `child_count` dict; the refused set is every
  child with count ≥ 2, in first-seen order. **O(N+E).** (`Graph.parent_of` at
  `mapper/model.py:152-156` scans all edges per call — `parent_of` per node is O(N·E), the exact
  anti-pattern the perf batch measured; it is NOT used by the check. The same anti-pattern exists
  today inside `preview_csv`'s orphan loop at `mapper/import_csv.py:101`; that loop is out of this
  batch's scope and recorded as a watch-item in §6.)
- **I2 — acyclic:** `Graph.find_cycle()` (`mapper/model.py:158-193`), already iterative and
  O(N+E) (adjacency built once at `:166-168`), already enforced at `mapper/store.py:822-824`.

## 3 · Diagrams

Information view — the two refusal surfaces and the shared predicate (all other viewpoints: n/a,
the change is one predicate + one data field + one paint branch):

```text
CSV file ──preview_csv(import_csv)──► Graph { nodes, edges, root_id, csv_collisions }
                                          │                          ▲ populated in pass 1
                    model::Graph.multi_parent_ids() │            (nid, line_no, raw_id) per row
                     │ I1 (new)          │ I2 (find_cycle, existing)
                     ▼                   ▼
        MapStore.save (store.py:810)   _ImportPreviewScreen.refresh_canvas (import_preview.py:55)
        refuses BEFORE dump(:826):     invariant violated?
          MapStoreError ──► _save_or_toast ──► toast (type only) + return False  │ yes: paint refusal panel
                     │ no write of any byte (LLR-CSV.1.2)            │ no: render as today (LayeredRenderer)
                     ▼                                                ▼
        .mmd + _nodos.yml pair ──MapStore.load──► Graph (oracle, untouched)
```

## 4 · Interfaces that change — and which ones FREEZE

| Interface | Current | After | Consumers | **Frozen for the fork?** |
|---|---|---|---|---|
| `Graph` value object (`model`) | fields `nodes`, `edges`, `root_id`, `schema`, `documents`, `load_warnings` (`mapper/model.py:90-98`) | + one defaulted field `csv_collisions: list[CsvCollision]` (default empty) and + one method `multi_parent_ids() -> list[str]`; new frozen value types `CsvCollision(slug: str, rows: tuple[CsvRow, ...])`, `CsvRow(line_no: int, raw_id: str)` — all additive, every existing constructor and literal keeps working | `store`, `views`, `mermaid`, `import_csv`, `screens`, `app`, `github`, `search` (ARCHITECTURE §4 `Graph` row) | **YES — the field is defaulted and additive (the `ViewState` precedent in §4: "adding a defaulted field is additive and never re-opens the A3"); no consumer's construction, equality or persistence changes** |
| `preview_csv` (`import_csv`) | `preview_csv(path: Path) -> Graph`, silently collapsing slug collisions (`mapper/import_csv.py:57-73`) | Same signature, same return type, same graph for every non-colliding input; colliding inputs additionally carry a populated `csv_collisions` | `screens/home.py:28,511`; test callers `tests/test_import_csv.py` (6 sites), `tests/test_gate2.py:371`, `tests/test_repair_cycles.py:371`; **F4 patch surface**: `mapper.screens.home.preview_csv` patched by `tests/test_inc9c.py:114`, `tests/test_inc9n.py:285`, listed in `tests/test_mod_compat.py:61` PATCH_SURFACE | **YES — signature and `Graph` return type are the F4 contract; only the record's content is new** |
| `_ImportPreviewScreen` (`screens/import_preview.py`) | `__init__(preview_graph, source_path)` (`:41-44`); `refresh_canvas` renders and paints the refusal panel only on a renderer exception (`:63-77`) | Same constructor (the record arrives inside `preview_graph`); `refresh_canvas` gains an invariant branch BEFORE the render: non-empty `multi_parent_ids()` or non-None `find_cycle()` → paint the refusal panel with the exact HLR-CSV.2 sentence (cycle path via `find_cycle()`'s return, `mapper/model.py:181`); renderer-exception branch kept as the fallback | constructed by `mapper/screens/home.py` and by `tests/test_repair_cycles.py:381`; canvas read by `tests/test_repair_cycles.py:388` and the new AT-073 | **YES — class, constructor, Static id and the "could not draw the preview" header substring are pinned by `tests/test_repair_cycles.py` (see §6 risks); only the panel body gains the sentence** |
| `MapStore.save` (`store`) | `save(map_id, graph) -> None`; pre-write validation = cycle guard only (`mapper/store.py:810-824`) | Same signature; one additional `MapStoreError` raise (multi-parent, naming the duplicated child id, plain-language) placed next to the cycle guard, both before `dump` at `:826` | `_save_or_toast` (`mapper/screens/common.py:217-267`, routes every screen-initiated save); ~60 direct test call sites (B1 census) | **YES — signature and cycle-guard message frozen (LLR-R01.5 pins and G6 toast tests); the new refusal is additive behaviour** |
| `_save_or_toast` (`screens/common.py:217`) | `-> bool`; False + toast (type only) on any raise | unchanged — the new `MapStoreError` is just another exception it already catches | `screens/import_preview.py:88`, `screens/map/*` draft save, `tests/test_g6_store_surrogates.py` | **YES — frozen contract (False + toast on `MapStoreError`); this batch relies on it, does not move it** |

**A3 note:** the only interface whose *shape* moves is the additive `Graph` field + method (defaulted
field precedent, above). `MapStore.save` and `preview_csv` keep their signatures — the A3 trigger
fired on the *behavioural* contract (new refusal consumed by `_save_or_toast`; new record consumed by
`refresh_canvas`), which is why this design is allowed to land in one lane.

## 5 · Proposed test cases

| Id | Layer (0 unit / A white / B black / UX) | What it asserts | **The mutation that would turn it RED** |
|---|---|---|---|
| `tests/test_csv_safety_store.py::test_save_refuses_multi_parent_graph` (LLR-CSV.1.1) | 0 | `MapStore.save` raises `MapStoreError` naming the duplicated child for every multi-parent fixture (two-row collision, three-way collision, collision-on-root, auto-id collision) and the cyclic / self-parent fixtures; happy-path fixtures (empty, single row, valid tree) raise nothing | **M1:** delete the multi-parent check in `MapStore.save` (keep the cycle check) → the multi-parent fixtures save and the paired `load` raises → RED |
| `tests/test_csv_safety_store.py::test_save_refuses_cycle_still` (LLR-CSV.1.1, LLR-R01.5 guard) | 0 | The pre-existing cycle refusal is untouched: cyclic and self-parent graphs raise the same `MapStoreError` ("the map has a cycle: …") | Delete the cycle guard at `mapper/store.py:822-824` → cyclic fixture saves → RED |
| `tests/test_csv_safety_store.py::test_refused_save_changes_no_workspace_byte` (LLR-CSV.1.2) | 0 | sha256 of every workspace file captured before a refused save equals the after-digest — including a refused save over a pre-existing map id with prior content | **M1b:** move the validation to after the first temp-file `replace` → target `.mmd` digest changes → RED |
| round-trip nodes in `tests/test_csv_safety_store.py` (LLR-CSV.3.1) | 0 | For every passing fixture (empty graph, single node, deepest fixture tree): `save` then `load` returns equal node-id set, edge set, `root_id` and titles — 0 differences | **M3:** make `mermaid.dump` omit node titles (or skip the sidecar write) → reloaded graph unequal / unloadable → RED |
| `tests/test_csv_safety_preview.py::test_preview_csv_records_collisions` (LLR-CSV.2.1) | 0 | `preview_csv` populates `graph.csv_collisions` with exactly the expected `(line_no, raw_id)` rows per slug for two-row, three-way, root-collision and auto-id fixtures; empty for non-colliding fixtures | **M2b:** stop appending to the collision record → record empty → RED (and AT-073 downstream RED) |
| `tests/test_csv_safety_preview.py::test_at_073_preview_names_the_colliding_rows` (HLR-CSV.2, LLR-CSV.2.2) | B | Through `MapperApp(tmp_path)` + `run_test(size=…)` + real keys: the `#import-preview-canvas` Static source contains the exact HLR-CSV.2 sentence naming rows 5 (id 'a-b') and 6 (id 'A B'), byte-for-byte after `darkside.plain` normalisation; plus the cycle-sentence node (`a → b → a` wording) and the three-way list grammar | **M2:** make `refresh_canvas` paint the graph (skip the invariant branch) or paint a generic message → sentence absent → RED |
| `tests/test_csv_safety_preview.py::test_at_072_refused_save_toasts_and_writes_nothing` (HLR-CSV.1) | B | Import the colliding perf-evidence CSV through the real flow; press `s`, answer the "save as" prompt with a real name; observe the toast (type only), an empty workspace (no `.mmd`/`_nodos.yml`), and the preview still open | **M1** (store-side deletion) → save succeeds and files land → RED; **M2** (panel-side skip) leaves it green by design — the mutation for this node is M1 |
| `tests/test_csv_safety_preview.py::test_at_074_valid_csv_saves_and_reopens_identical` (HLR-CSV.3) | B | A valid multi-row CSV: `s` + name saves through the preview; `MapStore.load` returns node ids, edges, `root_id` and titles identical to the preview graph | **M3** → re-open unequal → RED; **M1** over-broad (refuses a valid tree) → save raises → RED |
| Re-run pins (no new nodes): `tests/test_repair_cycles.py`, `tests/test_g6_store_surrogates.py` toast-wording nodes, `tests/test_import_csv.py` (6 callers), `tests/test_mod_compat.py` (F4 PATCH_SURFACE) | A | The B1 reverse census: every existing consumer of the touched symbols stays green | Any of the frozen interfaces drifting (signature, panel header, toast wording) → pin RED |

**Declared here, at authoring time, not at execution time.** The mutation column names the exact
reddening change per case (M1/M1b/M2/M2b/M3 from `01-requirements.md` §4), each to be executed as a
transcript per the batch's RED-proof rule.

## 6 · Risks and rejected alternatives

> Risks (with the B1 reverse-census result executed in this unit):

- **No existing test saves a graph the new check would refuse.** Executed census: every
  `store.save` call in `tests/` saves a tree or an empty graph; the only multi-parent fixtures
  (`tests/test_repair_cycles.py::_diamond`, used by `test_at_r03`/`test_at_r03b`) never reach
  `save` — they stop at `parse(dump(diamond))` (`tests/test_repair_cycles.py:477-484`); the cyclic
  preview fixture `test_tc_r08b_import_preview_survives_a_cyclic_csv`
  (`tests/test_repair_cycles.py:371-391`) builds a cyclic CSV, pushes `_ImportPreviewScreen` and
  never presses `s`. So the multi-parent refusal is purely additive against the suite. **Watch-item
  (not a break):** `test_tc_r08b` asserts the substring "could not draw the preview" in the painted
  panel — the new invariant branch MUST keep that existing header line (`mapper/screens/import_preview.py:74`)
  and put the sentence in the body. **Second watch-item:** `test_gate2_f5`
  (`tests/test_gate2.py:368-373`) builds two empty-id rows (`row-1`/`row-2`, no collision) — stays
  green because distinct auto-ids produce no collision record.
- **C8 / guard A-110:** the refusal sentence interpolates operator-supplied CSV ids and line
  numbers — every interpolated piece passes `darkside.plain` before assembly (the existing
  `plain(str(exc))` pattern at `mapper/screens/import_preview.py:75`), markup stays off, and no
  path or account name can reach the panel (the sentence carries only ids and line numbers).
- **Toast wording (G6-C-F2):** the toast shows the exception TYPE only; the row-naming text lives
  exclusively in the panel. The new `MapStoreError` message must not be interpolated into any
  toast (it is not — `_save_or_toast` at `mapper/screens/common.py:260-265` uses `type(e).__name__`).
- **Root-collision boundary:** a collision where one row is the root can pass a naive parent-count
  check yet re-open with a different root. Oracle: LLR-CSV.3.1's round-trip equality includes
  `root_id`; the boundary catalog carries the fixture.
- **Perf:** both invariants are O(N+E) with adjacency/count built once per call; `parent_of` per
  node is banned in the new code (the perf batch measured it O(N·E)). The pre-existing
  `parent_of`-per-node loop at `mapper/import_csv.py:101` is NOT in this batch's file scope to fix
  — recorded as a backlog candidate, not silently widened.
- **F4 patch surface:** `preview_csv` stubs in `tests/test_inc9c.py:114` / `tests/test_inc9n.py:285`
  replace the whole function; the unchanged signature keeps them biting. `CsvCollision` defaulting
  to empty means a stubbed `Graph` has no record and the preview branch degrades to render/fallback
  exactly as today.

| Alternative considered | Why it was rejected |
|---|---|
| Silent disambiguation of colliding ids (`a-b`, `a-b-2`) | Changes the user's data without telling them and makes their `parent` references ambiguous — the map they get is not the map they typed (PLAN.md D-rejected). |
| Second return value / small result type from `preview_csv` (`tuple[Graph, list[…]]` or `PreviewResult`) | Census: 8 direct test callers unpack a single value (`tests/test_import_csv.py` ×6, `tests/test_gate2.py:371`, `tests/test_repair_cycles.py:371`) plus `mapper/screens/home.py:511`; a signature change breaks all of them and re-opens the F4 `preview_csv` patch contract. An attribute on the returned `Graph` (defaulted field) travels the existing constructor with zero caller breakage. |
| The invariant check only in `MapStore.save` | Closes the persistence hole but fails US-CSV-002: the operator learns the cause only AFTER pressing save, from a toast that shows the exception type only. The preview must say why before the save attempt. |
| The invariant check only in the preview | Leaves the asymmetry open for every other graph producer that reaches `MapStore.save` (the GitHub connector, the factory, hand-built graphs in tests); HLR-CSV.1's round-trip invariant is only guaranteed at the save boundary. |
| The predicate in `mermaid` or duplicated per surface (store-side + preview-side scans) | `screens` has no declared `mermaid` edge and would gain one; store-side+preview-side copies of the scan can drift apart — the two surfaces would disagree on what is refusable. `model` is the one module both may import (§3), and `Graph` already owns the cycle predicate (`find_cycle`). |
| Persisting `csv_collisions` into the sidecar | The record is build-time provenance, not map content; persisting it would change the sidecar shape (B4 output-then-consume) and serve no re-open purpose. It lives on the in-memory `Graph` only. |

## 7 · Forward-applicability table — **the section that makes this document honest**

| Output of this PDR | Named consumer downstream | Where the consumer will read it |
|---|---|---|
| design characteristics: the invariant predicate `Graph.multi_parent_ids()` + `find_cycle` as the two loader-invariant checks, both O(N+E); `Graph.csv_collisions` + `CsvCollision`/`CsvRow` as the collision-record carrier; exact sentence templates of HLR-CSV.2 | the Phase-3 increments (increment 1: store refusal; increment 2: preview sentence) and the DDR | `PLAN.md` roadmap; increment specs; `04-validation.md` traceability matrix (LLR → test node) |
| enablers: the boundary-catalog fixtures (empty, single row, two-row/three-way collision, collision-on-root, auto-id collision, cycle via parent column, self-parent, the perf evidence CSV verbatim), E-1 helpers imported from `tests/test_draft_save.py`, the G6-C-F4 save-flow pattern from `tests/test_g6_store_surrogates.py:555-600` | Phase 3 test authoring and validation | `tests/test_csv_safety_store.py`, `tests/test_csv_safety_preview.py` (both to be created) |
| proposed test cases with named reddening mutations M1/M1b/M2/M2b/M3 | layers 0/A/B execution and the DDR's RED-proof transcripts | §5 above; the RED-proof step of each increment (`04-validation.md`) |
| design → requirement traceability (D1 check placement, D2 sentence on panel, D3 collision record; frozen `MapStore.save` / `_save_or_toast` / `preview_csv` contracts) | the matrix and the DDR | `01-requirements.md` §4 IFC owners; `docs/ARCHITECTURE.md` §4 rows this batch amends (commitment, at close) |

- ⚠ Any row whose consumer column is empty: **remove the output, or explain why it is being produced.** — none; every row names its consumer.

## 8 · Parallelisation plan *(only if the batch forks)*

Not applicable — one lane, two sequential increments (trigger A4 not fired; PLAN.md §Fork
preconditions discharged trivially). The file-set discipline still holds per increment:

| Lane | Modules / layer | Files it owns | Agent |
|---|---|---|---|
| Increment 1 — store refusal | `model` (predicate + field/types), `store` (save validation); tests layer 0/A | `mapper/model.py`, `mapper/store.py`, `tests/test_csv_safety_store.py` (2 source files) | store-lane worker |
| Increment 2 — preview sentence | `import_csv` (collision record), `screens` (`refresh_canvas` invariant branch); tests layer B (AT-072/073/074) | `mapper/import_csv.py`, `mapper/screens/import_preview.py`, `tests/test_csv_safety_preview.py` (2 source files) | preview-lane worker |

- `modules(lane_i) ∩ modules(lane_j) = { }` — or same domain / different layers with the interface frozen: ✓ (lane 2 consumes lane 1's `model` additions; the `Graph` field/method are additive and defaulted, so lane 1 may land them without lane 2)
- **File sets are disjoint** (not just modules — two lanes may not edit the same file, not even different regions): ✓ (source and test file sets are pairwise disjoint)
- Family-B reverse census run **per lane and shared** before forking: ✓ (executed at P1: 40 files reference the touched symbols; §6 risks lists every census hit the new refusal or the new paint branch can touch — none break)
- Trunk-only artifacts (requirements · traceability · backlog · SPEC) are written **only** by the trunk: ✓
