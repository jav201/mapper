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
| Requirements covered | `US-CSV-001 · US-CSV-002 · US-CSV-003 · HLR-CSV.1 · HLR-CSV.2 · HLR-CSV.3 · LLR-CSV.1.1 · LLR-CSV.1.2 · LLR-CSV.1.3 · LLR-CSV.2.1 · LLR-CSV.2.2 · LLR-CSV.2.3 · LLR-CSV.3.1` (amended at the P2 round-1 review: LLR-CSV.2.3 added, HLR-CSV.1/LLR-CSV.1.1 re-scoped to the round-trip check — Ledger: `LED-2026-10-10-csv-safety-batch.2`…`.4`; amended at the P2 round-2 review, rulings R11–R16: the round trip compares node-id set and edge set only — LLR-CSV.1.3 added, LLR-CSV.2.3 pinned at the `s` keypress with a pinned toast — Ledger: `LED-2026-10-10-csv-safety-batch.5`…`.10`) |
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

This design makes `MapStore.save` refuse — before writing any byte — every graph whose
saved form would not load back as the same graph (the round-trip check of ruling R2,
as amended by ruling R11: `mermaid.parse(mermaid.dump(G))` must succeed and reproduce G's
node-id set and edge set as (parent, child) pairs — the ROOT is not compared, because a
forest's root drifts on reparse (`dump` writes edges before parentless nodes, `parse` takes
the first parentless node in text order — pre-existing, B-117) — HLR-CSV.1), and makes
`_ImportPreviewScreen.refresh_canvas` name the
colliding CSV rows (raw ids + line numbers per `csv.DictReader.line_num`) in the
existing refusal panel, in the exact sentence HLR-CSV.2 fixes, keyed on the collision
record with the precedence collision > multi-parent > cycle (rulings R1/R3). The
preview's save action additionally refuses any import carrying a non-empty collision
record, whether or not the graph violates a loader rule (LLR-CSV.2.3). The happy path
— a valid CSV previews, saves and re-opens identical — is the regression guard
(HLR-CSV.3).

Will NOT do: accept multi-parent maps end to end (DAG model — out of MVP scope per
`mapper/mermaid.py:86`); touch the loader (`MapStore.load`, `mermaid.parse` — the invariant oracle);
silently disambiguate colliding ids; add any new screen, key, widget or toast wording.

## 2 · Modules and boundaries

| Module | What it owns here | What it exposes | What it must NOT reach into |
|---|---|---|---|
| `model` (`mapper/model.py`) | The loader-invariant predicate the preview's multi-parent sentence needs: `Graph.multi_parent_ids() -> list[str]` (kept per ruling R2 — the STORE check no longer uses it) and the collision record value types `CsvCollision` / `CsvRow` (frozen dataclasses) plus one defaulted `Graph` field `csv_collisions: list[CsvCollision] = field(default_factory=list, compare=False, repr=False)` (ruling R10: `Graph.__eq__`/`repr` do not change) | Additive only: a new method, two new value types, one defaulted field on `Graph` | nothing — `model` has no outbound dependencies (`docs/ARCHITECTURE.md` §3) |
| `store` (`mapper/store.py`) | `MapStore.save`'s pre-write validation (`mapper/store.py:810-824`): keep the existing cycle guard (`:822-824`, LLR-R01.5) and add the multi-parent refusal next to it, both before `mermaid.dump` at `:826` | Same `save(map_id, graph) -> None` signature; one new `MapStoreError` raise | unchanged: `store` depends on `model` only — the new check is imported from `model`, so no new edge |
| `import_csv` (`mapper/import_csv.py`) | Collision detection in `preview_csv`'s first pass (`mapper/import_csv.py:49-74`): track every row's `(nid, line_no, raw_id)` and populate `graph.csv_collisions` for every slug produced by more than one row (including auto-generated `row-N` / title slugs from the empty-id path, `:54-56`) | Same `preview_csv(path: Path) -> Graph` signature — the record travels ON the returned `Graph` | unchanged: `import_csv` depends on `model` + `mermaid` (`slugify`) only; it still never writes anything |
| `screens` (`mapper/screens/import_preview.py`) | `_ImportPreviewScreen.refresh_canvas` (`mapper/screens/import_preview.py:55-78`): before rendering, apply the precedence (ruling R3): non-empty `preview_graph.csv_collisions` → paint the collision sentence; else non-empty `multi_parent_ids()` → paint the multi-parent sentence; else `find_cycle()` non-None → paint the cycle sentence — in every case keeping the existing "could not draw the preview" header (`:74`) with the sentence in the body, instead of rendering; on a clean graph render exactly as today. `_ImportPreviewScreen.action_save` (`:88`): refuse AT the `s` keypress, BEFORE pushing the "save as" prompt (no name is asked for a save that cannot happen), by the same toast mechanism the store refusals surface (`screen.notify`, `markup=False`) at the call site — severity `error`, pinned text `the CSV has colliding ids — nothing was saved; see the preview`, no exception raised — when `preview_graph.csv_collisions` is non-empty, whether or not the graph violates a loader rule (ruling R1, LLR-CSV.2.3, pinned by ruling R15) | Same screen class, same `__init__(preview_graph, source_path)`, same `#import-preview-canvas` Static, same save key | unchanged: `screens` may import `model` (`docs/ARCHITECTURE.md` §3 `screens` row) — the predicate and the record are read from there; never `mapper.app` |

- Boundaries respected as declared in `docs/ARCHITECTURE.md`: ✓ — the load-bearing placement
  decisions survived the round-1 rulings: the **store check is the round trip in `store`**
  (ruling R2) — `MapStore.save` already imports `mermaid` for `dump`, so the check
  `parse(dump(G))` introduces no new dependency edge and cannot drift from the loader it
  round-trips through; the **`model` predicate serves only the preview** — `screens` depends
  on `model` (§3 `screens` row), so `Graph.multi_parent_ids()` and the `csv_collisions`
  record are readable there with zero new edges. Putting the store check in `mermaid` would
  invert the dependency (`mermaid` must not know about the store); duplicating the scan
  store-side + preview-side would let the two surfaces drift apart on what is refusable. The
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

Of these, **2 (multi-parent)** and **3 (cycle)** are the classic graph-shape invariants —
but ruling R2 (answering architect A4/A5) replaces the enumerated-checks design with the
general round trip, because a `Graph` argument CAN violate refusal 1 and can silently
corrupt the reparse in ways no enumerated predicate catches (both verified by the
architect on temp workspaces):

- a node **title containing a newline** dumps to an unparsable `.mmd` → `parse` raises
  (refusal 1) — so the P1 claim that refusals 1 and 4–8 "cannot be violated by a Graph"
  was **false for refusal 1** and is corrected here (ruling R10 / architect B1);
- a node **title containing `-->`** (e.g. an orphan node titled `a --> b`) re-parses as a
  **spurious edge** — the reparse succeeds with a different graph: silent corruption;
- **exact duplicate edges** are dropped by `dump`'s `emitted` set (`mapper/mermaid.py`
  `dump`), so the reparse succeeds and loses a row.

So `MapStore.save`'s pre-write validation is the **round trip** (HLR-CSV.1,
LLR-CSV.1.1): refuse, before any byte is written, when
`mermaid.parse(mermaid.dump(G))` raises OR yields a structure different from G — the
node-id set or the edge set as (parent, child) pairs. **The root is NOT compared**
(ruling R11): `parse` takes the root from text order (`mapper/mermaid.py:96-105,127`)
and `dump` writes all edges before edgeless parentless nodes (`mapper/mermaid.py:135-158`),
so any forest (≥2 parentless nodes) changes root on reparse — pre-existing, probed by the
architect (`scratchpad/probe/rt.py`): the legacy map `a` / `b --> c` loads today with root
`a`, and a root-comparing check would report `a -> b` and refuse every save of a map that
opens today, with no in-app repair. Comparing the root is therefore wrong for forests; it
is also unnecessary for trees, where the root is the unique parentless node and is
determined by the edge set (a child-first-declared tree round-trips fine). The drift is
recorded as **B-117** and pinned by the forest regression LLR-CSV.1.3. The refusal reason
names the rule in plain language (multiple parents / cycle / the dump does not re-parse /
the reparse changes the graph). Refusing duplicate edges is an **intended superset of the
loader** (architect A5): the loader would accept the reparse; the store refuses the row
loss.

- **Complexity:** O(N+E) for the structure comparison (sets built once) plus one `parse` of the dumped text — and the check's `mmd_text` IS the text written: one `dump` per save, the same string that `save` persists (ruling R12 — no second dump). Stated honestly: `dump` itself is already **O(N·E)** in its parentless-node loop (`mapper/mermaid.py:152-153` — `any(e.parent_id == node.id or e.child_id == node.id for e in graph.edges)` per node; the exact anti-pattern the perf batch measured, B-33 territory, NOT fixed here). The numeric threshold (ruling R12): the added parse costs ≤ 25 % of `MapStore.save` wall time for a 6 000-node wide tree, measured ONCE at P4 as evidence (median of 3 runs) — a measurement record in the increment packet, NOT a wall-clock assertion in the suite. (`Graph.parent_of` at `mapper/model.py:152-156` scans all
  edges per call — `parent_of` per node is O(N·E), the exact anti-pattern the perf batch
  measured; it is NOT used by the check. The same anti-pattern exists today inside
  `preview_csv`'s orphan loop at `mapper/import_csv.py:101`; that loop is out of this
  batch's scope and recorded as a watch-item in §6.)
- **`Graph.multi_parent_ids()` is kept** (`model`) — not for the store check but for the
  preview's multi-parent sentence (the middle tier of the precedence collision >
  multi-parent > cycle, ruling R3). The store check does not call it.

## 3 · Diagrams

Information view — the two refusal surfaces and the shared predicate (all other viewpoints: n/a,
the change is one predicate + one data field + one paint branch):

```text
CSV file ──preview_csv(import_csv)──► Graph { nodes, edges, root_id, csv_collisions }
                                          │                          ▲ populated in pass 1
                    (line_no via reader.line_num, raw_id per row)
                                          │
              refresh_canvas precedence (collision > multi-parent > cycle):
                1. csv_collisions non-empty  → collision sentence (ruling R1)
                2. multi_parent_ids() non-empty → multi-parent sentence
                3. find_cycle() non-None → cycle sentence
                     │
        MapStore.save (store.py:810)             _ImportPreviewScreen (import_preview.py:55)
        ROUND TRIP (ruling R2, R11):            invariant branch before render,
        refuse BEFORE dump(:826) when          header kept, sentence in body
        parse(dump(G)) raises or changes         │
        node ids / edges (root NOT compared):    ▼
          MapStoreError ──► _save_or_toast ──► toast (type only) + return False
          action_save ALSO refuses a non-empty csv_collisions (LLR-CSV.2.3)
          AT THE s KEYPRESS, BEFORE the save-as prompt (ruling R15) — same toast
          mechanism, pinned text, no write (LLR-CSV.1.2)
                     │
                     ▼ no write of any byte (LLR-CSV.1.2)
        .mmd + _nodos.yml pair ──MapStore.load──► Graph (oracle, untouched)
```

## 4 · Interfaces that change — and which ones FREEZE

| Interface | Current | After | Consumers | **Frozen for the fork?** |
|---|---|---|---|---|
| `Graph` value object (`model`) | fields `nodes`, `edges`, `root_id`, `schema`, `documents`, `load_warnings` (`mapper/model.py:90-98`) | + one defaulted field `csv_collisions: list[CsvCollision] = field(default_factory=list, compare=False, repr=False)` (ruling R10 — `Graph.__eq__`/`repr` do not change, answering architect B3 / qa B6) and + one method `multi_parent_ids() -> list[str]` (preview's multi-parent sentence only; the store check is the round trip and does not use it); new frozen value types `CsvCollision(slug: str, rows: tuple[CsvRow, ...])`, `CsvRow(line_no: int, raw_id: str)` — all additive, every existing constructor and literal keeps working | `store`, `views`, `mermaid`, `import_csv`, `screens`, `app`, `github`, `search` (ARCHITECTURE §4 `Graph` row — amendment owed at close, ruling R10) | **YES — the field is defaulted and additive with `compare=False, repr=False` (the `ViewState` precedent in §4: "adding a defaulted field is additive and never re-opens the A3"); no consumer's construction, equality or persistence changes** |
| `preview_csv` (`import_csv`) | `preview_csv(path: Path) -> Graph`, silently collapsing slug collisions (`mapper/import_csv.py:57-73`) | Same signature, same return type, same graph for every non-colliding input; colliding inputs additionally carry a populated `csv_collisions` — each row's line number taken from `csv.DictReader.line_num` (ruling R7, so blank lines and CRLF count exactly as the reader counts them), each raw id as typed; the record is populated for every collision shape, including collisions that violate no loader rule (ruling R1) | `screens/home.py:28,511`; test callers `tests/test_import_csv.py` (6 sites), `tests/test_gate2.py:371`, `tests/test_repair_cycles.py:371`; **F4 patch surface**: `mapper.screens.home.preview_csv` patched by `tests/test_inc9c.py:114`, `tests/test_inc9n.py:285`, listed in `tests/test_mod_compat.py:61` PATCH_SURFACE | **YES — signature and `Graph` return type are the F4 contract; only the record's content is new** |
| `_ImportPreviewScreen` (`screens/import_preview.py`) | `__init__(preview_graph, source_path)` (`:41-44`); `refresh_canvas` renders and paints the refusal panel only on a renderer exception (`:63-77`); `action_save` delegates to `_save_or_toast` (`:88`) | Same constructor (the record arrives inside `preview_graph`); `refresh_canvas` gains a precedence branch BEFORE the render (ruling R3, answering architect B2): non-empty `csv_collisions` → collision sentence; else `multi_parent_ids()` non-empty → multi-parent sentence; else `find_cycle()` non-None → cycle sentence (cycle path via `find_cycle()`'s return, `mapper/model.py:181`) — every tier keeps the "could not draw the preview" header (`:74`) with the sentence in the body; renderer-exception branch kept as the fallback. `action_save` refuses (ruling R1, LLR-CSV.2.3, pinned by ruling R15) when `preview_graph.csv_collisions` is non-empty — AT the `s` keypress, BEFORE pushing the "save as" prompt (no name is asked for a save that cannot happen), by emitting the same toast mechanism the store refusals surface (`screen.notify`, `markup=False`) at the call site with severity `error` and the pinned text `the CSV has colliding ids — nothing was saved; see the preview` — no exception raised, nothing written — whether or not the graph violates a loader rule | constructed by `mapper/screens/home.py` and by `tests/test_repair_cycles.py:381`; canvas read by `tests/test_repair_cycles.py:388` and the new AT-073 | **YES — class, constructor, Static id and the "could not draw the preview" header substring are pinned by `tests/test_repair_cycles.py` (see §6 risks); only the panel body gains the sentence, and the save action gains the record-keyed, prompt-preceding refusal** |
| `MapStore.save` (`store`) | `save(map_id, graph) -> None`; pre-write validation = cycle guard only (`mapper/store.py:810-824`) | Same signature; the pre-write validation becomes the round trip (ruling R2, amended by ruling R11): refuse when `mermaid.parse(mermaid.dump(graph))` raises or yields a different node-id set or edge set ((parent, child) pairs) — the root is NOT compared (a forest's root drifts on reparse: `dump` writes edges before parentless nodes, `parse` takes the first parentless node in text order — pre-existing, B-117) — one `MapStoreError` raise naming the rule in plain language, next to the cycle guard, both before `dump` at `:826`; the check parses the exact text written (one `dump` per save — the same string is persisted, ruling R12). Covers multi-parent, cycle, newline title, arrow title, duplicate edges (intended superset) | `_save_or_toast` (`mapper/screens/common.py:217-267`, routes every screen-initiated save); ~60 direct test call sites (B1 census) | **YES — signature and cycle-guard message frozen (LLR-R01.5 pins and G6 toast tests); the new refusal is additive behaviour** |
| `_save_or_toast` (`screens/common.py:217`) | `-> bool`; False + toast (type only) on any raise | unchanged — the new `MapStoreError` is just another exception it already catches | `screens/import_preview.py:88`, `screens/map/*` draft save, `tests/test_g6_store_surrogates.py` | **YES — frozen contract (False + toast on `MapStoreError`); this batch relies on it, does not move it** |

**A3 note:** the only interface whose *shape* moves is the additive `Graph` field + method (defaulted
field precedent, above). `MapStore.save` and `preview_csv` keep their signatures — the A3 trigger
fired on the *behavioural* contract (new refusal consumed by `_save_or_toast`; new record consumed by
`refresh_canvas`), which is why this design is allowed to land in one lane.

## 5 · Proposed test cases

| Id | Layer (0 unit / A white / B black / UX) | What it asserts | **The mutation that would turn it RED** |
|---|---|---|---|
| `tests/test_csv_safety_store.py::test_save_refuses_multi_parent_graph` (LLR-CSV.1.1) | 0 | The round-trip check raises `MapStoreError` naming the rule for the multi-parent fixtures (two-row collision, three-way collision, auto-id collision) and the cyclic / self-parent fixtures; happy-path fixtures (empty, single row, valid tree) raise nothing | **M1:** delete the round-trip check in `MapStore.save` → the fixtures save and the paired `load` raises or returns a different graph → RED |
| `tests/test_csv_safety_store.py::test_save_refuses_cycle_still` (LLR-CSV.1.1, LLR-R01.5 guard) | 0 | The pre-existing cycle refusal is untouched: cyclic and self-parent graphs raise the same `MapStoreError` ("the map has a cycle: …") | Delete the cycle guard at `mapper/store.py:822-824` → cyclic fixture saves → RED |
| `tests/test_csv_safety_store.py::test_save_refuses_unparsable_dump` (LLR-CSV.1.1) | 0 | A node title containing a newline refuses: `mermaid.parse(mermaid.dump(G))` raises (the architect's verified A4 case) | **M1** → the dump lands and `load` raises → RED |
| `tests/test_csv_safety_store.py::test_save_refuses_reparse_structure_mismatch` (LLR-CSV.1.1) | 0 | A title containing `-->` (reparse gains a spurious edge) and exact duplicate edges (dump drops them) refuse — the reparse must reproduce G's node-id set and edge set ((parent, child) pairs; root not compared — ruling R11) | **M1** → the corrupted/lossy map persists → RED |
| `tests/test_csv_safety_store.py::test_refused_save_changes_no_workspace_byte` (LLR-CSV.1.2) | 0 | No-write oracle (ruling R6): sha256 of EVERY workspace file — `iterdir()` recursive, including `mapper.db` and any `*.tmp` — captured before a refused save equals the after-state; the file set is unchanged and no `*_nodos.yml`/`*.mmd` appeared. The fixture OVERWRITES a pre-existing map id with prior content (ruling R6 / qa A6) | **M1b:** move the validation to after the first temp-file `replace` → the target `.mmd` digest changes → RED (bites only because the fixture overwrites an existing map) |
| `tests/test_csv_safety_store.py::test_save_accepts_legacy_forest_after_edit` (LLR-CSV.1.3, ruling R11) | 0 | A legacy forest map (`a` / `b --> c`, two parentless nodes) loads via `MapStore.load`, accepts an edit (a child added to one of its trees), and saves — then reloads with an equal node-id set and edge set (the root may differ on reparse: `dump` writes edges before parentless nodes, `parse` takes the first parentless node in text order — pre-existing, B-117) | **M4:** re-add the root comparison to the round-trip check → the check reports `root a -> b` and refuses a map that opens today → RED while every tree fixture stays green |
| round-trip nodes in `tests/test_csv_safety_store.py` (LLR-CSV.3.1) | 0 | For every passing fixture (empty graph, single node, deepest fixture tree): `save` then `load` returns equal node-id set, edge set, `root_id` and titles — 0 differences | **M3:** make `mermaid.dump` omit node titles (or skip the sidecar write) → reloaded graph unequal / unloadable → RED |
| `tests/test_csv_safety_preview.py::test_preview_csv_records_collisions` (LLR-CSV.2.1) | 0 | `preview_csv` populates `graph.csv_collisions` with exactly the expected `(line_no, raw_id)` rows per slug for two-row, three-way, root-collision, auto-id and no-loader-violation fixtures (two parentless rows; one parented + one parentless), plus blank-line and CRLF fixtures whose line numbers follow `csv.DictReader.line_num`; the perf evidence CSV's colliding rows are 5 and 6; empty for non-colliding fixtures | **M2b:** stop appending to the collision record → record empty → RED (and AT-073 downstream RED) |
| `tests/test_csv_safety_preview.py::test_empty_csv_panel_renders_no_sentence` (LLR-CSV.2.2, ruling R9/qa A8) | 0 | An empty CSV (root None) paints the empty panel with NO refusal sentence | **M2** (paint the sentence unconditionally) → RED |
| `tests/test_csv_safety_preview.py::test_at_073_preview_names_the_colliding_rows` (HLR-CSV.2, LLR-CSV.2.2) | B | Through `MapperApp(tmp_path)` + `run_test(size=…)` + real keys via `_open_import` (`tests/test_seed_safety.py:107-117`): the `#import-preview-canvas` Static source contains the "could not draw the preview" header AND the exact HLR-CSV.2 sentence naming rows 5 (id 'a-b') and 6 (id 'A B'), byte-for-byte after `darkside.plain` normalisation — header and sentence asserted together (ruling R10/qa B4); plus the cycle-sentence node (neutral wording, `a → b → a`), the self-parent-via-parent-column node, the three-way list grammar (exactly `rows 2, 3 and 4`) and the precedence node — a colliding cyclic CSV AND the root-collision fixture both paint the COLLISION sentence (ruling R13: the record is non-empty, so precedence wins; the root-collision graph's refusal as a cycle is asserted at the STORE layer only) | **M2:** make `refresh_canvas` paint the graph (skip the invariant branch) or paint a generic message → sentence absent → RED. Per layer (ruling R8): removing ONLY the preview record/branch reddens this node; removing ONLY the store check leaves it green |
| `tests/test_csv_safety_preview.py::test_at_072_refused_save_toasts_and_writes_nothing` (HLR-CSV.1) | B | Import the colliding perf-evidence CSV through `_open_import`; press `s` — NO "save as" prompt is pushed (the collision record is non-empty, so the LLR-CSV.2.3 refusal fires at the `s` keypress, ruling R15) and the pinned toast shows: severity `error`, text exactly `the CSV has colliding ids — nothing was saved; see the preview`; the no-write oracle holds (ruling R6: sha256 snapshot of every workspace file incl. `mapper.db`/`*.tmp`, file set unchanged, no `.mmd`/`_nodos.yml`) and the preview stays open | **M2c** (remove the preview's record-keyed refusal) → the prompt opens and the save can land → RED. Per layer (ruling R8, corrected by R14): this node's CSV carries a non-empty record, so the preview refuses BEFORE the store — the store-side mutation M1 does NOT redden this node; the store layer's controls are its own unit nodes (`test_save_refuses_*`) |
| `tests/test_csv_safety_preview.py::test_at_072b_parentless_slug_collision_refuses_save` (LLR-CSV.2.3, ruling R1) | B | Two parentless rows sharing one slug — violates NO loader rule — through `_open_import` (`i`, path, enter, `s`): the collision sentence paints AND at the `s` keypress NO prompt screen is pushed; the pinned toast fires (severity `error`, text exactly `the CSV has colliding ids — nothing was saved; see the preview` — ruling R15), the no-write oracle holds, the preview stays open | **M2c:** remove the `csv_collisions` refusal from `action_save` → the prompt opens and the save lands, silently losing a row → RED |
| `tests/test_csv_safety_preview.py::test_at_072c_mixed_parentage_slug_collision_refuses_save` (LLR-CSV.2.3, ruling R1) | B | One parented row + one parentless row sharing one slug: same assertions — at the `s` keypress NO prompt screen is pushed, the pinned toast fires, the no-write oracle holds, the preview stays open (ruling R15) | **M2c** → RED |
| `tests/test_csv_safety_preview.py::test_at_072d_auto_id_slug_collision_refuses_save` (LLR-CSV.2.3, ruling R1) | B | Two empty-id rows with the same title (auto-id collision): same assertions — at the `s` keypress NO prompt screen is pushed, the pinned toast fires, the no-write oracle holds, the preview stays open (ruling R15) | **M2c** → RED |
| `tests/test_csv_safety_preview.py::test_at_074_valid_csv_saves_and_reopens_identical` (HLR-CSV.3) | B | A valid multi-row CSV through `_open_import`: `s` DOES push the "save as" prompt (the record is empty), the name is typed, the save lands; `MapStore.load` returns node ids, edges, `root_id` and titles identical to the preview graph | **M3** → re-open unequal → RED; **M1** over-broad (refuses a valid tree) → save raises → RED |
| Re-run pins (no new nodes): `tests/test_repair_cycles.py`, `tests/test_g6_store_surrogates.py` toast-wording nodes, `tests/test_import_csv.py` (6 callers), `tests/test_mod_compat.py` (F4 PATCH_SURFACE) | A | The B1 reverse census: every existing consumer of the touched symbols stays green | Any of the frozen interfaces drifting (signature, panel header, toast wording) → pin RED |

**Declared here, at authoring time, not at execution time.** The mutation column names the exact
reddening change per case (M1/M1b/M2/M2b/M2c/M3/M4 — ids defined in `01-requirements.md` §6.1, ruling R16), each to be executed as a
transcript per the batch's RED-proof rule.

## 6 · Risks and rejected alternatives

> Risks (with the B1 reverse-census result executed in this unit):

- **No existing test saves a graph the new check would refuse (executed census, NOT a
  no-break claim).** Executed census: every `store.save` call in `tests/` saves a tree or
  an empty graph; the only multi-parent fixtures (`tests/test_repair_cycles.py::_diamond`,
  used by `test_at_r03`/`test_at_r03b`) never reach `save` — they stop at
  `parse(dump(diamond))` (`tests/test_repair_cycles.py:477-484`); the cyclic preview fixture
  `test_tc_r08b_import_preview_survives_a_cyclic_csv`
  (`tests/test_repair_cycles.py:371-391`) builds a cyclic CSV, pushes `_ImportPreviewScreen`
  and never presses `s`. So the refusal is expected to be purely additive against the
  suite — but per ruling R10 / qa QB3 this is **verified by the P3 full-suite gate, not
  claimed here** (the qa spot-checks: `_diamond`, `test_tc_r08b`, trees in
  `test_legend_design.py` / `test_repair_depth.py` / `test_search.py`, `test_pan.py:173`).
  **Watch-item (not a break):** `test_tc_r08b` asserts the substring "could not draw the
  preview" in the painted panel — the new precedence branch MUST keep that existing header
  line (`mapper/screens/import_preview.py:74`) and put the sentence in the body; AT-073
  asserts header and sentence together. **Second watch-item:** `test_gate2_f5`
  (`tests/test_gate2.py:368-373`) builds two empty-id rows (`row-1`/`row-2`, no collision)
  — stays green because distinct auto-ids produce no collision record.
  **`ARCHITECTURE.md` §4 `Graph` row amendment is owed at close** (ruling R10 /
  architect B3): the new field `csv_collisions` (defaulted, `compare=False`, `repr=False`)
  and method `multi_parent_ids()` must be recorded in the repo's commitment, not only here.
- **C8 / guard A-110:** the refusal sentence interpolates operator-supplied CSV ids and line
  numbers — every interpolated piece passes `darkside.plain` before assembly (the existing
  `plain(str(exc))` pattern at `mapper/screens/import_preview.py:75`), markup stays off, and no
  path or account name can reach the panel (the sentence carries only ids and line numbers).
- **Toast wording (G6-C-F2):** the toast shows the exception TYPE only; the row-naming text lives
  exclusively in the panel. The new `MapStoreError` message must not be interpolated into any
  toast (it is not — `_save_or_toast` at `mapper/screens/common.py:260-265` uses `type(e).__name__`).
- **Root-collision boundary (ruling R13, correcting round 1's R3 wording):** the fixture's `csv_collisions` record is NON-EMPTY (the colliding root row contributes to it), so at the PREVIEW the precedence collision > multi-parent > cycle wins and the COLLISION sentence paints. Its reclassification as a cycle governs the STORE layer only — the orphan loop (`mapper/import_csv.py:97-102`) closes the graph into a cycle, which the store's round-trip check refuses (`find_cycle=['a-b','c','a-b']`, save says "the map has a cycle"); that store-level refusal remains a store unit case (LLR-CSV.1.1), asserted in `tests/test_csv_safety_store.py`, not in the preview nodes. The general protection against a persisted map re-opening with a different root remains LLR-CSV.3.1's round-trip equality (whose happy-path fixtures are trees, where the root is determined by the edge set); the boundary catalog carries the fixture in both layers with this split.
- **Perf:** the structure comparison is O(N+E) with sets built once per call; the check's added cost is one `parse` of the dumped text, and the check parses the exact text written (one `dump` per save — the same string is persisted, ruling R12). Stated honestly: `dump` is already O(N·E) in its parentless-node loop (`mapper/mermaid.py:152-153` — B-33 territory, NOT fixed here). `parent_of` per node is banned in the new code (the perf batch measured it O(N·E)); the numeric threshold (ruling R12): the added parse costs ≤ 25 % of `MapStore.save` wall time for a 6 000-node wide tree, measured once at P4 (median of 3) as evidence — NOT a wall-clock assertion in the suite. The pre-existing `parent_of`-per-node loop at `mapper/import_csv.py:101` is NOT in this batch's file scope to fix — recorded as a backlog candidate, not silently widened.
- **Forest root drift (ruling R11 → B-117):** pre-existing — `dump` writes edges before parentless nodes and `parse` takes the first parentless node in text order, so a forest's root changes on reload (architect probe `scratchpad/probe/rt.py`: legacy `a` / `b --> c` loads with root `a`; reparse yields `b`). The round trip must NOT compare the root, or every save of a forest that opens today is refused (all save paths: `mapper/screens/map/editing.py:51,77,124,147`, `undo.py:64`, `drafts.py:141`, `factory.py:217`, `import_preview.py` — no in-app repair exists). Regression pinned by LLR-CSV.1.3's `test_save_accepts_legacy_forest_after_edit`; the drift itself is **B-117**. **Stated fallback (qa MED-4):** if the P3 full-suite gate finds a graph that saves on master today but the new check refuses, the batch returns to design with that fixture — the round trip is broader than today's loader guarantees, and a found break is a design input, not something to patch around at the gate.
- **F4 patch surface:** `preview_csv` stubs in `tests/test_inc9c.py:114` / `tests/test_inc9n.py:285`
  replace the whole function; the unchanged signature keeps them biting. `CsvCollision` defaulting
  to empty means a stubbed `Graph` has no record and the preview branch degrades to render/fallback
  exactly as today.
- **`splitlines()` caveat (ruling R16):** `csv.DictReader` counts lines via `str.splitlines()`,
  which also breaks on `\x0b`, `\x0c`, `\x1c`–`\x1e`, `\x85`, `\u2028` and `\u2029` — so a `line_num`
  in the sentence may differ from an editor's line number when the CSV carries those characters.
  Stated as a caveat in LLR-CSV.2.1; no fixture required.
- **Id glossary (ruling R16):** mutation ids (M1, M1b, M2, M2b, M2c, M3, M4), finding ids
  (round 1: architect `A1`–`A6`, proposal `B1`–`B6`, qa `Q1`–`Q9`, `QB1`–`QB6`; round 2:
  architect `A7`, `B5`, `B6`, qa `1`–`7`), rulings (`R1`–`R16`) and ledger ids
  (`LED-2026-10-10-csv-safety-batch.N`) are each one thing, named once — the canonical
  glossary is `01-requirements.md` §6.1; no id is reused for a second meaning.

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
| design characteristics: the round-trip save check (`parse(dump(G))` must reproduce the node-id set and the edge set ((parent, child) pairs) — the ROOT is NOT compared, ruling R11 / B-117; the check parses the exact text written — one `dump` per save, ruling R12; `dump`'s own O(N·E) parentless loop stated honestly, B-33 territory; refusal names the rule; the preview precedence collision > multi-parent > cycle with `csv_collisions` keyed first — the root-collision fixture paints the COLLISION sentence at the preview and is refused as a cycle at the store, ruling R13; `action_save`'s record-keyed refusal AT the `s` keypress before the save-as prompt, pinned toast `the CSV has colliding ids — nothing was saved; see the preview`, severity `error`, no exception raised, ruling R15; `Graph.csv_collisions` (`compare=False, repr=False`) + `CsvCollision`/`CsvRow` as the collision-record carrier; `Graph.multi_parent_ids()` kept for the preview's multi-parent sentence only; exact sentence templates of HLR-CSV.2 (three-way grammar exactly `rows 2, 3 and 4`; neutral cycle wording; line numbers via `csv.DictReader.line_num`, with the `splitlines()` caveat of ruling R16); the forest regression (`test_save_accepts_legacy_forest_after_edit`, LLR-CSV.1.3) and the P4 perf threshold (added parse ≤ 25 % of `MapStore.save` wall time on a 6 000-node wide tree, median of 3, evidence only — ruling R12) | the Phase-3 increments (increment 1: store refusal, `mapper/model.py` + `mapper/store.py`; increment 2: preview sentence + record, `mapper/import_csv.py` + `mapper/screens/import_preview.py`) and the DDR | `PLAN.md` roadmap; increment specs; `04-validation.md` traceability matrix (LLR → test node) |
| enablers: the boundary-catalog fixtures (empty, single row, two-row/three-way collision, collision-on-root — cycle case, auto-id collision, two parentless rows, one parented + one parentless, newline title, arrow title, duplicate edges, cycle via parent column, self-parent via the parent column, blank-line CSV, CRLF CSV, the empty-CSV panel, the perf evidence CSV verbatim), E-1 helpers imported from `tests/test_draft_save.py`, the real AT drive path `_open_import` from `tests/test_seed_safety.py:107-117` | Phase 3 test authoring and validation | `tests/test_csv_safety_store.py`, `tests/test_csv_safety_preview.py` (both to be created) |
| proposed test cases with named reddening mutations M1/M1b/M2/M2b/M2c/M3 and per-layer negative controls (ruling R8) | layers 0/A/B execution and the DDR's RED-proof transcripts | §5 above; the RED-proof step of each increment (`04-validation.md`) |
| design → requirement traceability (D1 check placement — now the round trip per ruling R2; D2 sentence on panel; D3 collision record; LLR-CSV.2.3 preview save refusal; frozen `MapStore.save` / `_save_or_toast` / `preview_csv` contracts) | the matrix and the DDR | `01-requirements.md` §4 IFC owners; `docs/ARCHITECTURE.md` §4 rows this batch amends (the `Graph` row — owed at close, ruling R10) |

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
