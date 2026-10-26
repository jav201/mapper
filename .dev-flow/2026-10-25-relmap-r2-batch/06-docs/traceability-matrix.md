# Traceability Matrix — mapper — Batch 2026-10-25-relmap-r2-batch

> **Artifact language:** canonical English scaffold. Generate the artifact in the batch's development language (`state.json` `language`); for Spanish batches **translate the prose, never a label**. This document mints no field a rule keys on — its ids (`US-`/`HLR-`/`LLR-`/`AT-`/`TC-`/`R-`) are read by the Atlas id-scanner and are not words in any language — so it carries no reserved-field block.

> **Owed in.** `core` — · `full` ✓

> Two chains (per the Two-layer validation rule) — a story is complete only when BOTH exist:
> - **Functional (white-box):** User Story → HLR → LLR → `TC-NNN` → File:line.
> - **Behavioral (black-box):** User Story → `AT-NNN` → observed outcome through the shipped surface.
> Every row must be complete when closing the batch (phase 6). Incomplete rows = coverage gaps and must be listed in the gaps section.
>
> Written at Phase 4 from the validated record (`../04-validation.md`); the user-story ids are the contract's `US-RMV-NNN` (`../01-requirements.md` §2.6). `File:line` names the file and the symbol, not a line number, because the symbols are what the tests import; the nodes cited are collected on the gate tree (4231 collected, 24 deselected). The TC column carries the family range the acceptance design's TC index assigns (`01b:341-346`) plus the contract-named TC id where one exists.

---

## 1. Master table — functional chain (white-box)

| US | HLR | LLR | TC | File:line | Status | Notes |
|----|-----|-----|-----|-----------|--------|-------|
| US-RMV-001 | HLR-RVM.1 | LLR-RVM.1.1 | TC-RM-04…09 · `tests/test_relmap_matrix.py` window/ruler arms | `mapper/screens/relmap/matrix.py` (`MatrixView.paint`, `_window`) | pass | M-RVM-1a/1b |
| US-RMV-001 | HLR-RVM.1 | LLR-RVM.1.2 | TC-RM-04…09 · `tests/test_relmap_matrix.py` cell-census arms | `mapper/screens/relmap/matrix.py` (`_cell`, `_winning_edge`) | pass | D5 glyph table; M-RVM-2/3 |
| US-RMV-001 | HLR-RVM.1 | LLR-RVM.1.3 | TC-RM-04…09 · `tests/test_relmap_matrix.py` legend arms | `mapper/screens/relmap/matrix.py` (legend line) | pass | M-RVM-2 |
| US-RMV-001 | HLR-RVM.2 | LLR-RVM.2.1 | TC-RM-04…09 · `tests/test_relmap_matrix.py::test_l0_rings_two_hop_same_direction_only` | `mapper/screens/relmap/matrix.py` (`_ring`) | pass | M-RVM-5 |
| US-RMV-001 | HLR-RVM.2 | LLR-RVM.2.2 | TC-RM-04…09 · `tests/test_relmap_matrix.py::test_summary_and_gauge_against_the_oracle` | `mapper/screens/relmap/matrix.py` (lens summary, gauge) | pass | M-RVM-6/7 |
| US-RMV-001 | HLR-RVM.2 | LLR-RVM.2.3 | TC-RM-04…09 · `tests/test_relmap_matrix.py::test_at131_lens_summary_hop_counts_and_dimming` | `mapper/screens/relmap/matrix.py` (the dimming census) | pass | M-RVM-7 |
| US-RMV-001 | HLR-RVM.3 | LLR-RVM.3.1 | TC-RM-04…09 · `tests/test_relmap_matrix.py::test_no_test_columns_declaration_and_skeleton_honesty` | `mapper/screens/relmap/matrix.py` (the declared test-column line) | pass | M-RVM-8 |
| US-RMV-001 | HLR-RVM.3 | LLR-RVM.3.2 | TC-RM-04…09 · `tests/test_relmap_matrix.py` empty-state arms | `mapper/screens/relmap/matrix.py` (empty/unknown-focus states) | pass | M-RVM-9 |
| US-RMV-001 | HLR-RVM.4 | LLR-RVM.4.1 | TC-RM-04…09 · `tests/test_relmap_matrix.py::test_geometry_audit_sweep_is_clean_at_every_size` | `mapper/screens/relmap/matrix.py` + `mapper/canvas.py` (the C10 audit hook) | pass | M-RVM-10 |
| US-RMV-001 | HLR-RVM.4 | LLR-RVM.4.2 | TC-RM-04…09 · `tests/test_relmap_matrix.py::test_at134_hostile_payload_on_the_live_surface` + the sink census | `mapper/screens/relmap/base.py` (`label`, the `_row_text`/`fit` seam) | pass | M-RVM-11 · M-RVH-18 |
| US-RMV-002 | HLR-RVG.1 | LLR-RVG.1.1 | TC-RM-10…14 · `tests/test_relmap_gaps_view.py::test_rvg_1_1_*` | `mapper/screens/relmap/gaps.py` (`GapsView.paint`) | pass | M-RVG-1 |
| US-RMV-002 | HLR-RVG.1 | LLR-RVG.1.2 | TC-RM-10…14 · `tests/test_relmap_gaps_view.py::test_rvg_1_2_*` | `mapper/screens/relmap/gaps.py` (header, chips, field band) | pass | M-RVG-2 |
| US-RMV-002 | HLR-RVG.1 | LLR-RVG.1.3 | TC-RM-10…14 · `tests/test_relmap_gaps_view.py::test_rvg_1_3_*` | `mapper/screens/relmap/gaps.py` (row anatomy, cursor) | pass | ranked row axis (D1); M-RVG-4 |
| US-RMV-002 | HLR-RVG.1 | LLR-RVG.1.4 | TC-RM-10…14 · `tests/test_relmap_scalecheck.py` (7) | `mapper/screens/relmap/gaps.py` (window, WHAT drop rule) | pass | M-RVG-5/6 |
| US-RMV-002 | HLR-RVG.1 | LLR-RVG.1.5 | TC-RM-10…14 · `tests/test_relmap_gaps_view.py::test_rvg_1_5_*` | `mapper/screens/relmap/gaps.py` (`toggle(kind)`) | pass | key `k`; COND-UX-2 oracle arm; M-RVG-7 |
| US-RMV-002 | HLR-RVG.2 | LLR-RVG.2.1 | TC-RM-10…14 · `tests/test_relmap_gaps_view.py::test_rvg_2_1_source_census_no_upper_no_caps_kind_literal` | `mapper/screens/relmap/gaps.py` (casing) | pass | M-RVG-8 |
| US-RMV-002 | HLR-RVG.2 | LLR-RVG.2.2 | TC-RM-10…14 · `tests/test_relmap_gaps_view.py::test_rvg_2_2_*` | `mapper/screens/relmap/gaps.py` (chrome strings) | pass | M-RVG-9 |
| US-RMV-002 | HLR-RVG.2 | LLR-RVG.2.3 | TC-RM-10…14 · `tests/test_relmap_gaps_view.py::test_rvg_2_3_*` | `mapper/screens/relmap/gaps.py` (reach cells, tally) | pass | M-RVG-10/11 |
| US-RMV-002 | HLR-RVG.3 | LLR-RVG.3.1 | TC-RM-10…14 · `tests/test_relmap_gaps_view.py::test_rvg_3_1_*` | `mapper/screens/relmap/gaps.py` + `base.py` (the label sink) | pass | M-RVG-12/13 |
| US-RMV-003 | HLR-RVS.1 | LLR-RVS.1.1 | TC-RM-15…20 · `tests/test_relmap_sheet.py::test_llr_rvs_1_1_*` | `mapper/screens/relmap/sheet.py` (`SheetView.paint`, header rows) | pass | M-RVS-4 |
| US-RMV-003 | HLR-RVS.1 | LLR-RVS.1.2 | TC-RM-15…20 · `tests/test_relmap_sheet.py::test_llr_rvs_1_2_*` | `mapper/screens/relmap/sheet.py` (label casing) | pass | M-RVS-5 |
| US-RMV-003 | HLR-RVS.2 | LLR-RVS.2.1 | TC-RM-15…20 · `tests/test_relmap_sheet.py::test_llr_rvs_2_1_and_2_2_section_oracles_asymmetric` | `mapper/screens/relmap/sheet.py` (`feeds it`) | pass | M-RVS-2 |
| US-RMV-003 | HLR-RVS.2 | LLR-RVS.2.2 | TC-RM-15…20 · `tests/test_relmap_sheet.py::test_llr_rvs_2_1_and_2_2_section_oracles_asymmetric` | `mapper/screens/relmap/sheet.py` (`a change reaches`) | pass | M-RVS-2 |
| US-RMV-003 | HLR-RVS.2 | LLR-RVS.2.3 | TC-RM-15…20 · `tests/test_relmap_sheet.py::test_llr_rvs_2_3_evidence_glyph_table` | `mapper/screens/relmap/sheet.py` (glyph column) | pass | M-RVS-3 |
| US-RMV-003 | HLR-RVS.2 | LLR-RVS.2.4 | TC-RM-15…20 · `tests/test_relmap_sheet.py::test_llr_rvs_2_4_*` | `mapper/screens/relmap/sheet.py` (declared empties) | pass | M-RVS-6 |
| US-RMV-003 | HLR-RVS.3 | LLR-RVS.3.1 | TC-RM-15…20 · `tests/test_relmap_sheet.py::test_llr_rvs_3_1_declared_hop2_cuts_direct_only` | `mapper/screens/relmap/sheet.py` (the `╌╌` cut lines) | pass | two hatch chars — the Statement wins (accepted deviation D-1); M-RVS-7 |
| US-RMV-003 | HLR-RVS.3 | LLR-RVS.3.2 | TC-RM-15…20 · `tests/test_relmap_sheet.py::test_llr_rvs_3_2_stacked_lists_every_node_by_minimum_hop` | `mapper/screens/relmap/sheet.py` (stacked density) | pass | TC-RM-17 synthetic 3-level arm (COND-QA-5); M-RVS-9 |
| US-RMV-003 | HLR-RVS.3 | LLR-RVS.3.3 | TC-RM-15…20 · `tests/test_relmap_sheet.py::test_llr_rvs_3_3_c_toggle_flips_rows_note_and_word_together` | `mapper/screens/relmap/sheet.py` (`toggle(kind)`) | pass | key `c`; per-view word (D1); M-RVS-9 |
| US-RMV-003 | HLR-RVS.4 | LLR-RVS.4.1 | TC-RM-15…20 · `tests/test_relmap_sheet.py::test_llr_rvs_4_1_*` | `mapper/screens/relmap/sheet.py` (`gaps on this node`) | pass | M-RVS-10 |
| US-RMV-003 | HLR-RVS.5 | LLR-RVS.5.1 | TC-RM-15…20 · `tests/test_relmap_sheet.py::test_llr_rvs_5_1_hostile_frame_renders_byte_literal_on_one_row` + the seam census | `mapper/screens/relmap/sheet.py` + `base.py` (single assembly seam) | pass | M-RVS-1 |
| US-RMV-003 | HLR-RVS.6 | LLR-RVS.6.1 | TC-RM-15…20 · `tests/test_relmap_sheet.py::test_llr_rvs_6_1_width_discipline_zero_c10_events` (4 arms) | `mapper/screens/relmap/sheet.py` (width discipline) | pass | M-RVS-11 |
| US-RMV-003 | HLR-RVS.6 | LLR-RVS.6.2 | TC-RM-15…20 · `tests/test_relmap_sheet.py::test_llr_rvs_6_2_overflow_is_counted_never_silent` | `mapper/screens/relmap/sheet.py` (counted overflow) | pass | M-RVS-11 |
| US-RMV-004 | HLR-RVH.2 | LLR-RVS.7.1 | TC-RM-15…20 · `tests/test_relmap_sheet.py::test_llr_rvs_7_1_no_osopen_no_render_call` | `mapper/screens/relmap/sheet.py` (read-only evidence labels) | pass | re-traced to HLR-RVH.2 per LED-2026-10-25-r2.04; M-RVS-12 |
| US-RMV-004 | HLR-RVH.1 | LLR-RVH.1.1 | TC-RM-21…27 · `tests/test_relmap_shell.py::test_llr_rvh_1_1_*` | `mapper/screens/home.py` (`_recent_entries`) + `mapper/relmap/descriptor.py` (discovery) | pass | M-RVH-1 |
| US-RMV-004 | HLR-RVH.1 | LLR-RVH.1.2 | TC-RM-22 · `tests/test_relmap_shell.py::test_llr_rvh_1_2_*` | `mapper/screens/home.py` (kind badges, chips) | pass | painted badge clip parked (B-159) |
| US-RMV-004 | HLR-RVH.1 | LLR-RVH.1.3 | TC-RM-21…27 · `tests/test_relmap_shell.py::test_llr_rvh_1_3_one_list_sorted_by_name_across_kinds` | `mapper/screens/home.py` (`_recent_entries`) | pass | M-RVH-3 |
| US-RMV-004 | HLR-RVH.2 | LLR-RVH.2.1 | TC-RM-21…27 · `tests/test_relmap_shell.py::test_llr_rvh_2_1_at_146_open_routes_by_kind` | `mapper/app.py` (screen routing) + `mapper/screens/relmap/screen.py` | pass | M-RVH-4 |
| US-RMV-004 | HLR-RVH.2 | LLR-RVH.2.2 | TC-RM-21…27 · `tests/test_relmap_shell.py::test_llr_rvh_2_2_relmap_scope_binds_no_write_action` | `mapper/keymap.py` (`SCOPE_RELMAP` BINDINGS census) | pass | M-RVH-5 |
| US-RMV-004 | HLR-RVH.2 | LLR-RVH.2.3 | TC-RM-21…27 · `tests/test_relmap_shell.py::test_llr_rvh_2_3_opening_a_relation_map_writes_nothing` | `mapper/screens/relmap/screen.py` + `mapper/store.py` (no writes on open) | pass | M-RVH-6 |
| US-RMV-004 | HLR-RVH.3 | LLR-RVH.3.1 | TC-RM-21…27 · `tests/test_relmap_shell.py::test_llr_rvh_3_1_*` | `mapper/screens/relmap/screen.py` (derive-on-open) | pass | M-RVH-7 |
| US-RMV-004 | HLR-RVH.3 | LLR-RVH.3.2 | TC-RM-21…27 · `tests/test_relmap_shell.py::test_llr_rvh_3_2_open_derives_once_and_r_rederives` | `mapper/screens/relmap/screen.py` (the `r` refresh) | pass | COND-QA-4 wrap; M-RVH-8 |
| US-RMV-004 | HLR-RVH.3 | LLR-RVH.3.3 | TC-RM-21…27 · `tests/test_relmap_shell.py::test_llr_rvh_3_3_non_git_workspace_derives` | `mapper/relmap/adapter.py` (workspace-root canon resolution) | pass | LED-2026-10-25-r2.03 |
| US-RMV-004 | HLR-RVH.4 | LLR-RVH.4.1 | TC-RM-21…27 · `tests/test_relmap_shell.py::test_llr_rvh_4_1_*` + `tests/test_keymap.py` seat pins | `mapper/keymap.py` (`SCOPE_RELMAP` seat) | pass | `k` bound in the Statement (LED-r2.12); M-RVH-14/19 |
| US-RMV-004 | HLR-RVH.4 | LLR-RVH.4.2 | TC-RM-25 · `tests/test_relmap_shell.py::test_llr_rvh_4_2_*` | `mapper/screens/relmap/screen.py` (BINDINGS/keybar generation) | pass | M-RVH-13/16/17 |
| US-RMV-004 | HLR-RVH.4 | LLR-RVH.4.3 | TC-RM-21…27 · `tests/test_relmap_shell.py::test_llr_rvh_4_3_view_switching_updates_the_crumb` + the review F-arms | `mapper/screens/relmap/screen.py` (compose, crumb, one cursor per view) | pass | D1 as amended at Inc-2; M-RVH-13 |
| US-RMV-004 | HLR-RVH.4 | LLR-RVH.4.4 | TC-RM-21…27 · `tests/test_relmap_shell.py::test_at_149_*` | `mapper/screens/relmap/screen.py` + `mapper/keymap.py` (help/palette) | pass | M-RVH-12 |
| US-RMV-004 | HLR-RVH.5 | LLR-RVH.5.1 | TC-RM-21…27 · `tests/test_relmap_shell.py::test_llr_rvh_5_1_*` | `mapper/screens/relmap/screen.py` + `base.py` (the refusal notice) | pass | double-paint observation parked (B-163); M-RVH-15 |
| US-RMV-004 | HLR-RVH.5 | LLR-RVH.5.2 | TC-RM-27 · `tests/test_relmap_shell.py::test_llr_rvh_5_2_*` | `mapper/screens/relmap/base.py` (`label`, coerce-before-cut) | pass | M-RVH-15/18 |
| US-RMV-005 | HLR-RVT.1 | LLR-RVT.1.1 | TC-RM-28 · `tests/test_relmap_text.py` definition-census arms | `mapper/relmap/text.py` (`cut`, `DISPLAY_MAX`, `refusal_line`) | pass | M-RVT-1 |
| US-RMV-005 | HLR-RVT.1 | LLR-RVT.1.2 | TC-RM-29 · `tests/test_relmap_text.py` reader-census arms | `mapper/relmap/text.py` (the one import path) + the three re-pointed consumers | pass | M-RVT-2 |
| US-RMV-005 | HLR-RVT.1 | LLR-RVT.1.3 | TC-RM-29 · `tests/test_relmap_text.py` R1-contract arms + the byte-identity probes | `mapper/relmap/text.py` + `mapper/relmap/audit.py` (`structure_lines`) | pass | hash `b7ff2e38…5a07`; M-RVT-3 |
| US-RMV-006 | HLR-RVU.1 | LLR-RVU.1.1 | TC-RM-30 · `tests/test_hook_line_bound.py` (7) + the amended R1 arms | `mapper/reqharness/audit.py` (`_cut_hook_line`, `HOOK_LINE_CELLS`) | pass | bound 240 on the escaped form; code points not cells (B-161); M-RVU-1/2/3 |

## 1b. Behavioral chain (black-box)

> Per user story: the acceptance test that observes the outcome through the shipped surface. A story with a complete functional chain but no behavioral row is INCOMPLETE. All view ATs drive the real TUI through `MapperApp(workspace=…)` under `run_test()` pilots; AT-151/AT-152 drive `mapper --audit` as subprocesses; AT-150's deliverable is the on-disk artifact (C-18).

| US | Acceptance test (`AT-NNN`) | Shipped surface | Observed outcome / deliverable | Status |
|----|----------------------------|-----------------|--------------------------------|--------|
| US-RMV-001 | AT-130…AT-134 | the relation screen, matrix view + lens | the honest skeleton, the lens summary/gauge/dimming, the binds-glyph census, the hostile-payload literal render | pass |
| US-RMV-002 | AT-135…AT-139 | the relation screen, gaps view (ranked + by-kind) | the ranked catalogue, the `k` toggle byte-identical back, the 118/87 sweep and the 100k cap, honest zeros, hostile canon literal | pass |
| US-RMV-003 | AT-140…AT-144 | the relation screen, node sheet (direct + `c` stacked) | the direct feeders, the stacked chain, the node's own gaps, the 87-col discipline, the hostile sheet literal | pass |
| US-RMV-004 | AT-145…AT-149 | Home + the relation screen chrome | the interleaved recents list, kind routing, the derived row, view switching/refresh/leave, help + palette seat equality | pass |
| US-RMV-005 | AT-150 · AT-151 | the on-disk census + the `--audit` bytes | one definition site / one import path / zero old-path hits; the refusal bytes byte-identical to the R1 goldens | pass |
| US-RMV-006 | AT-152 | the `--audit` hook lines | the 240-bound spelling-aware cut on the escaped form, the D4 behaviours intact | pass |

---

## 2. Coverage summary

| Metric | Value |
|--------|-------|
| Total user stories | 6 |
| Covered user stories | 6 (100%) — every story has a complete functional chain AND a behavioral row |
| Total HLR | 20 |
| Implemented HLR | 20 (100%) |
| Total LLR | 52 |
| Implemented LLR | 52 (100%) |
| Test cases | 27 (TC-RM-04…30) plus the contract-named guard pins |
| TC pass | 27 (all families green in the gate run) |
| TC fail | 0 |
| TC pending | 0 |

---

## 3. Detected gaps

> Incomplete rows, requirements without TC, or TCs without code mapping.

| ID | Type | Description | Proposed action |
|----|------|-------------|-----------------|
| G-001 | escaped defects (closed) | the two full-suite escapes (census trio; privacy transcript) — see `../04-validation.md` | closed `2e83cf6` / `cdc4491`; lessons for P5 |
| G-003 | not-run | the real Python 3.10 run for the R2 code | BACKLOG B-165 |
| G-004 | parked observation | the Home kind badge paints clipped at both widths | BACKLOG B-159 |
| G-005 | parked observation | the unavailable refusal line paints twice | BACKLOG B-163 |
| G-006 | declared scope gap | the full `AT × TC` binds-glyphs grid awaits the B-141 AT→test table | BACKLOG B-141 |
| G-007 | numbering gap | M-RVM-4 is undefined in every batch artifact | BACKLOG B-162 (register or renumber at the join) |

---

## 4. Changes from previous batch

*(Added, modified, or closed since `2026-10-25-relmap-r1-batch`.)*

| Type | Item | Detail |
|------|------|--------|
| new | US-RMV-001…006 | the relation screen: matrix + lens, ranked gaps + `k` by-kind, node sheet + `c` chain, the Home shell routing, the `relmap/text.py` presentation leaf, the 240 hook bound |
| new | HLR-RVM.1–4, RVG.1–3, RVS.1–6, RVH.1–5, RVT.1, RVU.1 | 20 HLR, 52 LLR (`../01-requirements.md` §3, §4) |
| new | AT-130…AT-152 · TC-RM-04…30 | 23 acceptance tests (TUI pilots + census + CLI), 27 test cases |
| new | modules `mapper/screens/relmap/` (`__init__`, `screen`, `base`, `matrix`, `gaps`, `sheet`) and `mapper/relmap/text.py` | `docs/ARCHITECTURE.md` §2/§3 rows; the D1 host↔renderer surface frozen at the PDR |
| modified | `mapper/relmap/{model,descriptor,audit,adapter}.py` | the three primitives move to the `text.py` leaf (one definition site, one import path, zero old-path refs; rendered bytes byte-identical) |
| modified | `mapper/keymap.py` | the additive `SCOPE_RELMAP` seat (13 bindings) |
| modified | `mapper/screens/home.py` · `mapper/app.py` | relation rows listed and routed by kind; the `relmap.descriptor` discovery edge |
| modified | `mapper/reqharness/audit.py` | the per-line bound 240 (`_cut_hook_line`) in the F-SEC-3 order |
| modified | guards, same landing | `tests/test_keymap.py` / `test_key_dispatch.py` pins · `tests/test_darkside_census.py` pin 82→94 · `tests/test_inc9.py` lexicon +13 seat rows · `tests/test_inc9c.py` pin 240→246 · `tests/test_repair_artifact_claims.py` re-parametrized (the 4 renamed ids) |
| closed at P4 | two full-suite escapes | `LED-2026-10-25-r2.31` (census trio) and the A-110 transcript redaction — see `../04-validation.md` G-001/G-002 |

---

## 5. Quick bidirectional mapping

### 5.1 By user story
- **US-RMV-001** → HLR-RVM.1–4 → LLR-RVM.1.1–4.2 (10) → TC-RM-04…09 · AT-130…134
- **US-RMV-002** → HLR-RVG.1–3 → LLR-RVG.1.1–3.1 (9) → TC-RM-10…14 · AT-135…139
- **US-RMV-003** → HLR-RVS.1–6 → LLR-RVS.1.1–7.1 (14, of which RVS.7.1 traces to HLR-RVH.2) → TC-RM-15…20 · AT-140…144
- **US-RMV-004** → HLR-RVH.1–5 → LLR-RVH.1.1–5.2 (15) → TC-RM-21…27 (22/25/27 named) · AT-145…149
- **US-RMV-005** → HLR-RVT.1 → LLR-RVT.1.1–1.3 (3) → TC-RM-28/29 · AT-150/151
- **US-RMV-006** → HLR-RVU.1 → LLR-RVU.1.1 (1) → TC-RM-30 · AT-152

### 5.2 By code file
- `mapper/screens/relmap/matrix.py` → LLR-RVM.1.1–4.2 → TC-RM-04…09 · AT-130…134
- `mapper/screens/relmap/gaps.py` → LLR-RVG.1.1–3.1 → TC-RM-10…14 · AT-135…139
- `mapper/screens/relmap/sheet.py` → LLR-RVS.1.1–7.1 → TC-RM-15…20 · AT-140…144
- `mapper/screens/relmap/screen.py` + `mapper/keymap.py` → LLR-RVH.2.1–2.3, RVH.3.1–3.3, RVH.4.1–4.4, RVH.5.1/.5.2 → TC-RM-21…27 · AT-146…149
- `mapper/screens/home.py` + `mapper/app.py` → LLR-RVH.1.1–1.3, RVH.2.1 → TC-RM-21…27 · AT-145/146
- `mapper/screens/relmap/base.py` → LLR-RVM.4.2, RVG.3.1, RVS.5.1, RVH.5.2 (the shared label sink) → the TC-RM-27 census + the hostile AT arms
- `mapper/relmap/text.py` → LLR-RVT.1.1–1.3 → TC-RM-28/29 · AT-150/151
- `mapper/reqharness/audit.py` → LLR-RVU.1.1 → TC-RM-30 · AT-152

---

## 6. Batch sign-off

| Field | Value |
|-------|-------|
| Batch ID | `2026-10-25-relmap-r2-batch` |
| Closing date | 2026-10-26 — Phase 4 validated (PASS-WITH-NOTES, `../04-validation.md`); the DDR sealed `approved with conditions` and **both MAJOR conditions were discharged at the P5 close** (COND-DDR-1 citations re-repaired, COND-DDR-2 pre-fix REDs captured — `../01-requirements-ledger.md` `LED-2026-10-25-r2.32/.33`); P5 post-mortem (`../05-postmortem.md`) and the P6 documents complete; the batch awaits the vault sync |
| Total iterations (sum of phases) | per `state.json` `iterations_per_station`: P1=2 (two amendment passes), all others 0; P2 ran two review passes inside one station visit |
| Validation passed | yes — PASS-WITH-NOTES (`../04-validation.md`): the real Python 3.10 run is `not-run` (B-165/B-148, operator); two parked walkthrough observations (B-159, B-163); the M-RVM-4 numbering gap (B-162) |
| Synced to Obsidian | no — `phase_status: awaiting-sync`; the canonical vault copies are written by `/dev-flow-sync` at close |
