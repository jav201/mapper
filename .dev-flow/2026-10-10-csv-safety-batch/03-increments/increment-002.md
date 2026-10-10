# Increment 002 — HLR-CSV.2 · HLR-CSV.3 · LLR-CSV.2.1 / LLR-CSV.2.2 / LLR-CSV.2.3 / LLR-CSV.3.1 · `The preview says why, before the user tries to save`

> **Artifact language:** English.
> **Owed in.** `core` ✓ · `full` ✓
> **Where this lives:** the repo, `.dev-flow/2026-10-10-csv-safety-batch/03-increments/increment-002.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-10-csv-safety-batch` |
| Increment | `002` (CSVI2) |
| Lane (if the batch forked) | n/a — one lane · increment 2 owns `import_csv` + `screens/import_preview.py` (increment 1 owns `model` + `store`, ruling R10 / architect B3) |
| Requirement(s) | `HLR-CSV.2` · `HLR-CSV.3` · `LLR-CSV.2.1` · `LLR-CSV.2.2` · `LLR-CSV.2.3` · `LLR-CSV.3.1` (e2e twin AT-074) |
| Acceptance | AT-072 · AT-072b · AT-072c · AT-072d · AT-073 · AT-074 through `MapperApp(tmp_path)` + `run_test(size=...)` + real keys via `_open_import` (`tests/test_seed_safety.py:107-117`); unit layer 0 in `tests/test_csv_safety_preview.py` |
| Agent | Kimi (`kimi-code/kimi-for-coding`) via the kimi CLI — worker unit CSVI2 |
| Date | `2026-10-10` |

---

## 1 · What changed

- **`preview_csv` fills `graph.csv_collisions` in its first pass** (LLR-CSV.2.1, ruling R7): every row appends a `CsvRow(line_no=reader.line_num, raw_id=raw_id)` to a per-slug list as it is read, so blank lines and CRLF endings count exactly as `csv.DictReader` counts them; after the orphan pass the slugs produced by two or more rows become `CsvCollision` records — raw id as typed, including auto-generated ids from the empty-id path (`title` slug / `row-N`), and including collisions that violate no loader rule (ruling R1). Signature unchanged (F4: tests patch `mapper.screens.home.preview_csv`); the record travels on the returned `Graph` and is never persisted.
- **`_ImportPreviewScreen.refresh_canvas` paints the refusal panel before rendering, with precedence collision > multi-parent > cycle** (HLR-CSV.2, LLR-CSV.2.2, rulings R1/R3/R13): a non-empty `csv_collisions` paints the pinned collision sentence per colliding slug (two rows: `CSV rows {n1} (id '{raw1}') and {n2} (id '{raw2}') collapse into the node id '{slug}'; a map can hold only one parent per node, so rename the duplicated ids and import again.`; three or more: comma-joined with `and` before the last, exactly `rows 2, 3 and 4`, no Oxford comma); else `multi_parent_ids()` paints the multi-parent sentence naming the duplicated child ids; else `find_cycle()` paints the neutral cycle sentence `the import builds a cycle ({a → b → a}); a saved map must be a tree, so fix the parent references and import again.` In every tier the existing header `could not draw the preview` is kept verbatim with the sentence(s) in the panel body; every interpolated piece passes `darkside.plain` (C8) and styling comes from `darkside` tokens (`INK`/`MUT`). An empty CSV (root None) or a clean graph renders exactly as today — no sentence, no crash. The renderer-exception fallback branch is untouched.
- **`_ImportPreviewScreen.action_save` refuses at the `s` keypress, BEFORE pushing the save-as prompt** (LLR-CSV.2.3, rulings R1/R15): when `preview_graph.csv_collisions` is non-empty — whether or not the graph violates a loader rule — it emits `screen.notify(..., severity="error", markup=False)` with the pinned text `the CSV has colliding ids — nothing was saved; see the preview`, at the call site, no exception raised, nothing written; the screen stays open and no name is asked for a save that cannot happen. Graphs without a collision record are unchanged: the store's round-trip check (increment 1) still refuses loader-violating graphs via `_save_or_toast`.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/import_csv.py` | source | LLR-CSV.2.1 | per-row `(nid, line_num, raw_id)` tracking in the first pass; `graph.csv_collisions` populated after the orphan pass; `CsvCollision`/`CsvRow` imported from `model` (increment 1's carrier) |
| `mapper/screens/import_preview.py` | source | LLR-CSV.2.2, LLR-CSV.2.3 | module helpers `_collision_sentence` / `_refusal_sentences` (pinned grammar, `darkside.plain` on every interpolated piece); the precedence branch in `refresh_canvas` before the render (header kept, sentence(s) in body); the record-keyed, prompt-preceding refusal in `action_save` with the pinned error toast |
| `tests/test_csv_safety_preview.py` | test | LLR-CSV.2.1, LLR-CSV.2.2, LLR-CSV.2.3, LLR-CSV.3.1, AT-072…AT-074 | new — 12 nodes (§4) |
| `.dev-flow/2026-10-10-csv-safety-batch/evidence/inc2-red.transcript` | generated | LLR-CSV.2.1/2.2/2.3 | RED-proof transcript (§4) |

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 4** (`mapper/import_csv.py`, `mapper/screens/import_preview.py`) |
| Test files | 1 (`tests/test_csv_safety_preview.py`) |
| Doc files | 1 (this packet + the evidence transcript — outside the count) |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_csv_safety_preview.py tests/test_csv_safety_store.py tests/test_import_csv.py tests/test_seed_safety.py tests/test_repair_cycles.py tests/test_gate2.py tests/test_mod_compat.py
ruff check mapper/import_csv.py mapper/screens/import_preview.py tests/test_csv_safety_preview.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `tests/test_csv_safety_preview.py` (12 new) + re-run pins `tests/test_csv_safety_store.py`, `tests/test_import_csv.py`, `tests/test_seed_safety.py`, `tests/test_repair_cycles.py`, `tests/test_gate2.py`, `tests/test_mod_compat.py` | **166 passed in 78.43s** (§3 command, this worktree) |

New node ids:

- `tests/test_csv_safety_preview.py::test_preview_csv_records_collisions` — LLR-CSV.2.1: the record names exactly the expected (line number, raw id) pairs per slug for the CRLF perf-evidence CSV (rows 5/6), a blank-line CSV (blank line counted: rows 4/5), a three-way collision, the auto-id collision, and the two no-loader-violation shapes (two parentless rows; one parented + one parentless); empty for clean/single/empty fixtures
- `tests/test_csv_safety_preview.py::test_at_073_preview_names_the_colliding_rows` — AT-073 (HLR-CSV.2, LLR-CSV.2.2): through the real import flow (`i`, path, `enter`), the `#import-preview-canvas` Static source contains the `could not draw the preview` header AND the exact pinned sentence naming rows 5 (id 'a-b') and 6 (id 'A B') — header and sentence asserted together (ruling R10)
- `tests/test_csv_safety_preview.py::test_empty_csv_panel_renders_no_sentence` — LLR-CSV.2.2 boundary: an empty CSV (root None) paints no refusal sentence and does not crash
- `tests/test_csv_safety_preview.py::test_cycle_csv_paints_the_neutral_cycle_sentence` — LLR-CSV.2.2: a cyclic `parent` column and a self-parent both paint the neutral cycle sentence with the `find_cycle()` path (`a → b → c → a` / `a → a`)
- `tests/test_csv_safety_preview.py::test_three_way_collision_uses_list_grammar` — LLR-CSV.2.2 boundary: exactly `rows 2, 3 and 4` (no Oxford comma) with `(ids 'dup', 'DUP' and 'Dup')`
- `tests/test_csv_safety_preview.py::test_colliding_cyclic_csv_paints_the_collision_sentence` — precedence (rulings R3/R13): the evidence CSV's graph IS cyclic AND records a collision — the COLLISION sentence wins at the preview
- `tests/test_csv_safety_preview.py::test_markup_in_id_is_painted_verbatim` — C8: ids like `[bold]x[/bold]` / `[BOLD]X[/BOLD]` (both slug to `bold-x-bold`) are painted verbatim as plain text, ids passed through `darkside.plain`
- `tests/test_csv_safety_preview.py::test_at_072_refused_save_toasts_and_writes_nothing` — AT-072 (HLR-CSV.1 observable outcome via the preview layer, ruling R14): the colliding evidence CSV through `i`, path, `enter`, `s` — NO prompt screen pushed (the preview screen stays on top), the pinned toast fires with severity `error`, `markup=False`, text exactly `the CSV has colliding ids — nothing was saved; see the preview`, and the workspace sha256 oracle (every file recursive, incl. `mapper.db`) is unchanged with no `.mmd`/`_nodos.yml` appearing
- `tests/test_csv_safety_preview.py::test_at_072b_parentless_slug_collision_refuses_save` — AT-072b (LLR-CSV.2.3): two parentless rows sharing one slug (no loader rule violated) — same refusal, toast, no-write oracle
- `tests/test_csv_safety_preview.py::test_at_072c_mixed_parentage_slug_collision_refuses_save` — AT-072c (LLR-CSV.2.3): one parented + one parentless row sharing one slug — same assertions
- `tests/test_csv_safety_preview.py::test_at_072d_auto_id_slug_collision_refuses_save` — AT-072d (LLR-CSV.2.3): two empty-id rows with the same title (auto-id collision) — same assertions
- `tests/test_csv_safety_preview.py::test_at_074_valid_csv_saves_and_reopens_identical` — AT-074 (HLR-CSV.3, LLR-CSV.3.1 e2e twin): a valid CSV through the full `_open_import` (`s` DOES push the save-as prompt, the name is typed, the save lands, no pinned toast); `MapStore.load` returns identical node ids, edge set, `root_id` and titles vs `preview_csv`

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | (M2 flavor 1) `sentences = []` in `refresh_canvas`; (M2 flavor 2) a generic refusal painted when the sentence list is empty; (M2b) `preview_csv` stops appending to the collision record; (M2c) the `csv_collisions` refusal removed from `action_save` |
| Instrument | hand edit of the product file, applied and reverted by explicit copy (`cp <backup> <product>`); every restore checked by sha256 |
| Where it ran | this worktree |
| Transcript | `.dev-flow/2026-10-10-csv-safety-batch/evidence/inc2-red.transcript` (relative paths only) |
| Restore proven by | sha256 of `mapper/screens/import_preview.py` returned to `2e40feb83ee27deb04cae2127cbf6efb8cdaef7552095a4cb0b6485fcdf2955e` and of `mapper/import_csv.py` to `9dfb12a8590451831534b7263fe9e03e9dd0169d16468265f6079f8f37794f30` after every mutation |
| Bytecode cache | run with `python -B` |
| Arms resolved at baseline | 4 mutations × their named nodes (below) |
| Verdict granularity | per node id |
| Arms that stayed GREEN | under M2 flavor 1 the empty-panel node stayed green (the renderer fallback repaints the existing header without a sentence) — M2 flavor 2, the glossary's second flavor, reddens it; under M2 flavor 2 AT-073 stayed green (flavor 1 reddens it) |

RED outputs (verbatim tails from the transcript):

- M2 flavor 1 + `-k "at_073 or empty_csv_panel"` → `1 failed, 1 passed, 10 deselected` — `test_at_073_preview_names_the_colliding_rows` `FAILED` (the sentence is absent; the graph is painted instead).
- M2 flavor 2 + `-k "empty_csv_panel or at_073"` → `1 failed, 1 passed, 10 deselected` — `test_empty_csv_panel_renders_no_sentence` `FAILED` (a sentence paints on an empty CSV).
- M2b + `-k "records_collisions or at_073"` → `2 failed, 10 deselected` — `test_preview_csv_records_collisions` and `test_at_073_preview_names_the_colliding_rows` `FAILED` (the record is empty; AT-073 is downstream RED, exactly LLR-CSV.2.1's negative control).
- M2c + `-k "at_072"` → `4 failed, 8 deselected` — `test_at_072_refused_save_toasts_and_writes_nothing`, `test_at_072b_parentless_slug_collision_refuses_save`, `test_at_072c_mixed_parentage_slug_collision_refuses_save`, `test_at_072d_auto_id_slug_collision_refuses_save` `FAILED` (the save-as prompt opens for a save that cannot happen; no pinned toast; the no-write oracle bites where the flow then saves).

| Field | Value |
|---|---|
| **RED counterfactual** | M2 (both flavors) reddens its named LLR-CSV.2.2 nodes; M2b reddens the LLR-CSV.2.1 record node and AT-073 downstream; M2c reddens AT-072/072b/072d. Transcript at `evidence/inc2-red.transcript`; restore digests returned after every mutation |

| Field | Value |
|---|---|
| **Mutation verdicts** | 4 mutants, all KILLED per node id (M2f1 → AT-073, M2f2 → empty panel, M2b → 2 nodes, M2c → 4 nodes); arms that stayed GREEN: named above (each flavor's complement — no node a flavor claims stayed green); restored byte-identical (sha256) and the full §3 run re-run GREEN (166 passed) |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_csv_safety_preview.py` (the new nodes) | M2/M2b/M2c product mutations (above) | `FAILED` — missing sentence / empty record / prompt pushed — verbatim tails in the transcript |
| `ruff check mapper/import_csv.py mapper/screens/import_preview.py tests/test_csv_safety_preview.py` | the authored files | `All checks passed!` (no finding — the instrument is green at baseline; the pytest nodes above carry the RED proof) |

| Field | Value |
|---|---|
| **Instrument RED-proof** | the pytest nodes shown RED under every mutation before the PASS was believed; ruff green at baseline |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the `#import-preview-canvas` Static's rendered text | AT-073 and the sentence-family nodes assert against `Static.render().plain` — the emitted painted form, not the helper's return | the exact pinned sentences found byte-for-byte (assertions passed) |
| the workspace file set + digests | `_digests(workspace)` = `{relative path: sha256}` for every file via `rglob("*")`, captured before the `s` keypress and compared after on AT-072/072b/072c/072d | equal dicts, no `.mmd`/`_nodos.yml` appeared (assertions passed) |
| the toast | `app.notify` captured via `_capture_notices` (imported from `tests/test_draft_save.py`) and asserted as `(message, severity=error, markup=False)` | the pinned text fired exactly once per refusal (assertion passed) |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 3 artifacts, each asserted against its emitted form |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| inc2-red.transcript | .dev-flow/2026-10-10-csv-safety-batch/evidence/inc2-red.transcript | `065c581fc3f69bf6cc6741d480c20503f93c83a3e8c67c3c83b6251e71f1aa7c` |

| Field | Value |
|---|---|
| **Evidence files** | `evidence/inc2-red.transcript` — baseline hashes, all four RED runs, restores and sha256 checks, final 166-passed GREEN (sha256 of the stored bytes cited above) |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | no — every refusal/sentence is driven by a CSV fixture this increment writes; the "no existing test breaks" claim is the P3 full-suite gate's, not this increment's (verification here is the §3 file set only) |
| If the result is an ABSENCE, what made the search wide enough | n/a |
| Guard labelled as protecting a CONCLUSION, not a behaviour | n/a |
| Conjunctive criteria: one mutation per conjunct | per-conjunct: the record (M2b) · the painted sentence (M2) · the `s`-keypress refusal (M2c) |
| Synthetic instance of the absent case | each colliding CSV fixture IS the synthetic instance of a colliding import |
| **Positive control for every probe that returned an ABSENCE** | AT-074 is the positive control for the no-write oracle's complement (a valid CSV DOES write the pair), and the digest probe itself is shown biting under M2c where the unguarded flow saves |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rlE "MapStore\|preview_csv\|_ImportPreviewScreen" tests/` | 40 files (executed at P1, design §6); this increment only fills a defaulted field and adds paint/refusal branches — the §3 re-run pins (`test_import_csv.py` ×6 callers, `test_seed_safety.py` `_open_import`, `test_repair_cycles.py` incl. the `test_tc_r08b` header-substring watch-item, `test_gate2.py` F5 empty-id rows, `test_mod_compat.py` F4 PATCH_SURFACE) stay green |
| B2 file moved on disk | n/a — no file moved | not fired |
| B3 byte-identical golden captures this source | n/a — no golden reads the preview canvas or the record | not fired |
| B4 artifact produced here is consumed elsewhere | the collision record is consumed by `_ImportPreviewScreen` only; AT-074's saved pair is consumed by `MapStore.load` | exercised end to end by AT-074 |

| A3 | interface consumed by another module changed | `preview_csv` keeps its signature; `_ImportPreviewScreen` keeps its constructor, Static id and header — the record and the refusal are behavioural additions consumed in-repo |

| Field | Value |
|---|---|
| **Reverse census** | 4 probes run (B1 and B4 fired with the hits above, re-validated green by the §3 run; B2, B3 did not fire; A3 additive — the only consumer is the preview screen itself) |

### Correction population — enumerated BEFORE the first site was edited

| Field | Value |
|---|---|
| **Correction population** | none — this increment adds behaviour only; no pre-existing defect in the touched files was corrected (ruff clean at baseline) |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|---|---|---|---|
| n/a — no marker superseded | n/a | n/a | n/a |

### Signed-balance test ledger

`post = base − deleted + added` → `166 = 154 + 12 − 0` ✓ reconciles (154 pre-existing nodes across the seven §3 files, 12 added in `tests/test_csv_safety_preview.py`, 0 deleted).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | **PENDING** — the orchestrator dispatches it (per the unit brief) |

---

## 5 · Risks

- The multi-parent sentence tier (middle of the precedence) has no pinned wording in HLR-CSV.2 — only its existence and keying on `Graph.multi_parent_ids()` are required; this increment's wording names the duplicated child ids and may be re-worded by review without touching the pinned collision/cycle sentences.
- `preview_csv`'s orphan loop still scans `parent_of` per node (O(N·E), design §6 watch-item) — out of this batch's scope by ruling R12's honesty note; not fixed here.
- The `splitlines()` caveat (ruling R16) applies to the painted line numbers for CSVs carrying `\x0b`/`\x0c`/`\x1c`–`\x1e`/`\x85`/`\u2028`/`\u2029` — stated in LLR-CSV.2.1, no fixture required.

## 6 · Pending items / spec deviations

- The P4 numeric perf measurement (ruling R12) — evidence only, owed at validation.
- `ARCHITECTURE.md` §4 `Graph` row amendment (ruling R10 / architect B3) — owed at batch close.

## 7 · Suggested next task

Validation/close: the P3 full-suite gate (re-run after any post-review repair), the P4 perf evidence, `04-validation.md` + `05-close.md`.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 2 / 4 (§2) |
| 2 | Tests written in this same increment | all | ✓ | 12 nodes in `tests/test_csv_safety_preview.py` |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | 12 nodes, 166 passed (§3) |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | M2 (2 flavors) / M2b / M2c, transcript + restore digests (§4) |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 4 probes (§4) |
| 6 | `code-reviewer` passed | `core` · `full` | ⚠ | PENDING — orchestrator dispatches (§4b) |
| 7 | No file from another lane touched | all | ✓ | one lane; files = §2 |
| 8 | Frozen interfaces untouched | all | ✓ | `preview_csv` signature and `_ImportPreviewScreen` constructor/Static id/`could not draw the preview` header unchanged (F4 patch surface and `test_tc_r08b` stay green) |
| 9 | Coverage claims verified **on disk** | all | ✓ | 166 passed here (§3 command) |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 |
| 11 | **Mutation verdicts** declared | all | ✓ | §4 — 4 mutants KILLED per node id |
| 12 | **Instrument RED-proof** declared | all | ✓ | §4 — pytest nodes (+ ruff green at baseline) |
| 13 | **Correction population** declared | all | ✓ | §4 (none) |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4 (rendered Static text + workspace digest map + captured toast) |
| 15 | **Independent review** names somebody | all | ⚠ | PENDING (§4b) — dispatched by the orchestrator |
| 16 | **Evidence files** declared | all | ✓ | §4 — `evidence/inc2-red.transcript` with sha256 |
