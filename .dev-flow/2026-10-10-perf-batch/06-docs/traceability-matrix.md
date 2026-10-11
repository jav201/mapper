# Traceability Matrix — mapper — Batch `2026-10-10-perf-batch`

> **Artifact language:** canonical English scaffold. Generate the artifact in the batch's development language (`state.json` `language`); for Spanish batches **translate the prose, never a label**. This document mints no field a rule keys on — its ids (`US-`/`HLR-`/`LLR-`/`AT-`/`TC-`/`R-`) are read by the Atlas id-scanner and are not words in any language — so it carries no reserved-field block; what it must not do is order the translation of somebody else's.

> **Owed in.** `core` — · `full` ✓
> **Sources:** `01-requirements.md` + ledger, `04-validation.md`, `05-postmortem.md`, `03-increments/`, the shipped tree and `python -B -m pytest --collect-only -q -p no:cacheprovider` re-collection per selector. `T/` = `tests/`. Status `pass` = passed in the join gate run 2 (`evidence/join-gate-run2-full-suite.transcript`, 3223 passed / 24 deselected / 3 xfailed / 0 failed, orchestrator, base `5cde04e`). Every selector below was re-collected at `3b84e2c` (HEAD) for this matrix: **no selector collects 0** (counts in the `TC` column). HLR-PERF.3 / LLR-PERF.3.1–3.2 / US-PERF-003 and AT-077/077b are WITHDRAWN to B-118 (ledger `LED-2026-10-10-perf-batch.3`) — kept as marked rows, never deleted.

---

## 1. Master table — functional chain (white-box)

| US | HLR | LLR | TC (selector → real node ids, count) | File:line | Increment(s) | Result | Status |
|----|-----|-----|--------------------------------------|-----------|--------------|--------|--------|
| US-PERF-001 | HLR-PERF.1 | LLR-PERF.1.1 | `T/test_perf_paint_clip.py` (17) → `test_wire_count_budget`, `test_bare_canvas_clip_equality` (+9 `elbow` params), `test_bare_canvas_clip_equality_edge` ×4, `test_bare_canvas_clip_equality_paints_something`, `test_render_grid_clip_identity`, `test_at_075_keypress_wire_budget`, … | `mapper/canvas.py:113` (`edge`), `:127` (`elbow_down`) — spans clipped to `0 <= x < w`, `0 <= y < h` before iterating (`:136`, `:141`) | 002 (Inc-R1, Lane R) | pass | pass |
| US-PERF-001 | HLR-PERF.1 | LLR-PERF.1.2 | `T/test_perf_layout_memo.py` (26) → `test_memo_miss_spy`, `test_at_075b_memo_misses_and_golden`, `test_memo_invalidation_arms[resize\|title\|fold\|focus\|undo\|add_child\|round_trip]`, `test_memo_id_reuse`, `test_nodes_writer_census` (+16 planted-form arms) | `mapper/views/layered.py:192` (`_tree_layout_unscaled`), `:350` (`_geometry`, memo threaded as the `layout_memo` argument), `:413-431` (hit check, `_LayoutMemo` key, `_layout_misses` spy) | 004 (Inc-R2, Lane R) | pass | pass |
| US-PERF-001 | HLR-PERF.1 | LLR-PERF.1.3 | `T/test_mod_parity.py` (3) · `T/test_repair_golden_census.py` (7) · `T/test_perf_paint_clip.py::test_render_grid_clip_identity` — all inside the gate; plus `T/test_perf_goldens_manifest.py` (2) → `test_manifest_names_base_sha_5cde04e`, `test_every_golden_exists_and_matches_its_sha256` | the byte-identity oracle: `T/goldens/perf/**` (MANIFEST + 26 goldens, base SHA `5cde04e`) + the pre-existing AT-065 parity goldens | 001 (capture), every lane increment | pass | pass |
| US-PERF-002 | HLR-PERF.2 | LLR-PERF.2.1 | `T/test_perf_adjacency.py` (18) → `test_cache_mutation_script_equality`, `test_cache_counted_ops`, `test_mid_rebuild_failure_leaves_token_invalid`, `test_edges_writer_census`, `test_census_in_place_forms[setitem\|slice\|del\|iadd\|imul\|sort\|reverse\|clear\|extend\|insert\|remove\|pop\|alias]`, `test_minimap_outline_forest_dag_bytes` | `mapper/model.py:134-141` (`_adj_src`/`_adj_len`/`_adj_children`/`_adj_parents`, private + `compare=False, repr=False`), `:204-205` (validity token), `:214` (rebuild) | 003 (Inc-M1 + follow-up, Lane M) | pass | pass |
| US-PERF-002 | HLR-PERF.2 | LLR-PERF.2.2 | `T/test_perf_dump.py` (3) → `test_dump_counted_ops_scaling_ratio`, `test_dump_fixture_goldens`, `test_at_076_real_save_dump_budget` | `mapper/mermaid.py:131` (`dump`), `:151-160` — ONE local incident-id pass over every edge (dangling edges counted), membership replaces the per-node `any()` rescan | 005 (Inc-M2, Lane M) | pass | pass |
| US-PERF-002 | HLR-PERF.2 | LLR-PERF.2.3 | inspection — `git diff 5cde04e unit/perfm1 -- mapper/views` **empty** on the Lane M branch (recorded per lane at the DDR, ruling R17); `_child_index` per-render builds still present in `mapper/views/` | `mapper/views/*.py` — 0 Lane M bytes; the model cache stays `_`-private to `mapper/model.py` | 003, 005 (M-M3 per-lane check) | pass | pass |
| US-PERF-003 | HLR-PERF.3 | LLR-PERF.3.1 | **WITHDRAWN to B-118** — the former test 077 node was never created (`tests/test_perf_mount.py` does not exist on disk) | — | Lane S (withdrew at the spike gate) | withdrawn | withdrawn |
| US-PERF-003 | HLR-PERF.3 | LLR-PERF.3.2 | **WITHDRAWN to B-118** — the former test 077b node was never created | — | Lane S (withdrew at the spike gate) | withdrawn | withdrawn |

**A worked example — text to read, never rows of your record.** It sits in a fence so that nothing has to be deleted: a row copied out of it would claim a trace nobody made. Write your own rows in the table above.

```text
| *(example)* US-001 | HLR-001 | LLR-001.1 | TC-001 | `src/foo.ts:42` | pass | |
| *(example)* US-001 | HLR-001 | LLR-001.2 | TC-002 | `src/foo.ts:78` | pass | |
| *(example)* US-001 | HLR-001 | LLR-002.1 | TC-003 | `src/bar.ts:15` | pass | |
| *(example)* US-002 | HLR-002 | LLR-002.1 | TC-004 | `src/baz.ts:90` | fail | See gap G-001 |
```

## 1b. Behavioral chain (black-box)

| US | Acceptance test (`AT-NNN`) | Shipped surface | Observed outcome / deliverable | Status |
|----|----------------------------|-----------------|--------------------------------|--------|
| US-PERF-001 | AT-075 — `T/test_perf_paint_clip.py::test_at_075_keypress_wire_budget` (1/17; the file's other 16 nodes are its unit arms); AT-075b — `T/test_perf_layout_memo.py::test_at_075b_memo_misses_and_golden` (1/26) | the painted screen of the real app, driven with real keys (`MapperApp(tmp_path)` + `run_test(size=(118,34))` + `pilot.press(...)`, helpers imported from `T/test_draft_save.py`) on a generated wide-2000 map | the `#map-canvas` strips after open/`l`/`j` (AT-075) and open + `l,j,j,j,j`, archive, `l` (AT-075b) byte-equal the goldens pinned at base `5cde04e`; the wire counter reads 12,264 (baseline 23,983,998, cap 61,500); the `_layout_misses` spy reads 1 per session | pass |
| US-PERF-002 | AT-076 — `T/test_perf_dump.py::test_at_076_real_save_dump_budget` (1/3) | the real persisting edit gesture — open a SAVED generated wide-6000 map, `a` add_child through real keys (persists via `_save_or_toast`), counting wrapper on `mapper.mermaid.dump` | the saved `.mmd` bytes after the edit, byte-equal to the golden pinned at base `5cde04e`; ONE dump call iterating 12,000 ≤ 2·E + 4 edges (baseline 18,009,001) | pass |
| US-PERF-003 | AT-077 / AT-077b — **WITHDRAWN to B-118** (ledger `.3`; nodes never created) | — | — | withdrawn |

**A worked example — text to read, never rows of your record.** It sits in a fence so that nothing has to be deleted: a row copied out of it would claim a trace nobody made. Write your own rows in the table above.

```text
| *(example)* US-001 | AT-001 | `<handler/screen/CLI>` | `<outcome / file:path>` | pass |
```

---

## 2. Coverage summary

| Metric | Value |
|--------|-------|
| Total user stories | 3 (1 withdrawn, marked) |
| Covered user stories | 3 (100% — US-PERF-003 covered by its recorded withdrawal to B-118) |
| Total HLR | 3 (1 withdrawn, marked) |
| Implemented HLR | 3 (100%) |
| Total LLR | 8 (2 withdrawn, marked) |
| Implemented LLR | 8 (100%) |
| Test cases (this batch's new files, collected at `3b84e2c`) | 66 (paint_clip 17 + layout_memo 26 + adjacency 18 + dump 3 + manifest 2) |
| TC pass | 66/66 (inside the join gate: 3223 passed / 0 failed) |
| TC fail | 0 |
| TC pending | 0 |

Suite ledger (`04-validation.md`): **3157 − 0 + 66 = 3223 passed**, +3 xfailed = 3226 collected of 3250 (24 deselected by `pyproject.toml`); slow lane 19 passed.

---

## 3. Detected gaps

| ID | Type | Description | Proposed action |
|----|------|-------------|-----------------|
| G-001 | HLR-PERF.1 scoping | the layout memo covers the render path only — `painted_ids` (`mapper/views/layered.py:495`), `pan_extent` (`:509`) and the pan clamp's `layered_geometry` reader (`mapper/screens/map/panning.py:277`) still lay out per selection-only key | backlog B-120 — thread the renderer memo into the three readers (screen-side files) |
| G-002 | HLR-PERF.2 out of scope | load wall-clock unchanged (2.32 → 2.22 s): `MapStore.load` is 100% YAML `safe_load` of the metadata sidecar (`spike/perf-baseline.md` §7.4) | backlog row B-121 proposed — sidecar parse cost in a store-side batch |
| G-003 | HLR-PERF.3 / US-PERF-003 | mount renders 2–3×; the single-render design was not proven (spike inconclusive) | backlog B-118 — measure wide-2000 first, then design |
| G-004 | LLR-PERF.1.2 (M-R2d) | the `id()`-recycle mutant is unreddenable on this interpreter (0/2000 forced reuses); safety by construction + Lane M's two-replacement script (DDR C4, ruling R13 escape) | declared; re-visit only on a runtime that recycles addresses |

**A worked example — text to read, never rows of your record.** It sits in a fence so that nothing has to be deleted: a row copied out of it would claim a gap nobody detected. Write your own rows in the table above.

```text
| *(example)* G-001 | TC fail | TC-004 fails on condition X | See post-mortem phase 5 |
| *(example)* G-002 | no coverage | LLR-005.2 has no associated TC | Move to next batch |
```

---

## 4. Changes from previous batch

| Type | Item | Detail |
|------|------|--------|
| new | HLR-PERF.1/2 (+3 withdrawn with Lane S), LLR-PERF.1.1–2.3 (+3.1/3.2 withdrawn), US-PERF-001/002 (+003 withdrawn), AT-075/075b/076 | this batch's contract — behaviour-preserving performance at scale; 8 surviving LLRs, all pass |
| new | counted-operations oracle regime + base-pinned goldens (`tests/goldens/perf/**`, 27 files, base SHA `5cde04e`) | thresholds are measured counts, never wall-clock; every golden captured pre-remedy at the trunk (PDR C10) |
| new | guard files `T/test_perf_paint_clip.py` / `test_perf_layout_memo.py` / `test_perf_adjacency.py` / `test_perf_dump.py` / `test_perf_goldens_manifest.py` | 66 nodes, each negative control executed RED with a sha256-verified restore |
| modified | `mapper/canvas.py`, `mapper/views/layered.py`, `mapper/model.py`, `mapper/mermaid.py` (+203/−26) | the four remedies — span clip, unscaled-layout memo, adjacency cache, linear incident dump |
| modified | `tests/test_a3_census.py` (pin 65 → 80), `tests/test_repair_store_boundary.py`, `.gitattributes` (`tests/goldens/** -text`, `2c64f76`) | gate follow-ups + the byte-pin line-ending rule |
| closed | B-33's performance follow-up (this batch IS the follow-up; B-33 stays open for `MAX_RENDER_NODES`-class work) | the S-15 dense-DAG cost is unreachable through the shipped loader (parser refuses multi-parent nodes) |
| withdrawn | Lane S → B-118 | spike PERFS inconclusive; requirements marked, not deleted (ledger `.3`) |
| proposed | B-121 — load sidecar parse cost | no backlog row existed; proposed in `05-postmortem.md` |

---

## 5. Quick bidirectional mapping

### 5.1 By user story
- **US-PERF-001** (a keypress costs ≥ 5× less render work, byte-identically) → HLR-PERF.1 → LLR-PERF.1.1, 1.2, 1.3 → TC: `test_perf_paint_clip.py` (17), `test_perf_layout_memo.py` (26), `test_mod_parity.py` (3) + `test_repair_golden_census.py` (7) + `test_perf_goldens_manifest.py` (2); AT-075, AT-075b.
- **US-PERF-002** (save is O(N+E), byte-identically) → HLR-PERF.2 → LLR-PERF.2.1, 2.2, 2.3 → TC: `test_perf_adjacency.py` (18), `test_perf_dump.py` (3), the M-M3 per-lane file-diff check; AT-076.
- **US-PERF-003** (mount paints once) → HLR-PERF.3 → LLR-PERF.3.1–3.2 → WITHDRAWN to B-118 (ledger `.3`); AT-077/077b never created.

### 5.2 By code file (each touched product file → the LLR that owns it)
- `mapper/canvas.py` → LLR-PERF.1.1 (span clip) + LLR-PERF.1.3 (byte identity) → `test_perf_paint_clip.py` (17)
- `mapper/views/layered.py` → LLR-PERF.1.2 (unscaled-layout memo) + LLR-PERF.1.3 → `test_perf_layout_memo.py` (26); LLR-PERF.2.3 pins Lane M out of this directory
- `mapper/model.py` → LLR-PERF.2.1 (adjacency cache) → `test_perf_adjacency.py` (18)
- `mapper/mermaid.py` → LLR-PERF.2.2 (linear incident dump) → `test_perf_dump.py` (3)
- `tests/goldens/perf/**` + `tests/perf_goldens_capture.py` + `tests/test_perf_goldens_manifest.py` → LLR-PERF.1.3 / the provenance protocol (PDR C10)
- `tests/test_a3_census.py` (M), `tests/test_repair_store_boundary.py` (M), `.gitattributes` (M) → gate follow-ups, no new LLR

---

## 6. Batch sign-off

| Field | Value |
|-------|-------|
| Batch ID | `2026-10-10-perf-batch` |
| Closing date | 2026-10-10 |
| Total iterations (sum of phases) | 10 station passes, 2 iterations (P1 ×2, P2 ×2 — `state.json` `decisions_log`) |
| Validation passed | yes (PASS-WITH-NOTES; notes = B-120 scoping, load YAML-bound, Lane S withdrawn — none blocking) |
| Synced to Obsidian | no record of a sync in the batch records |
