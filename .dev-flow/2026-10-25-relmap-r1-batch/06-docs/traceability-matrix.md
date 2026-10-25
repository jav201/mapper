# Traceability Matrix — mapper — Batch 2026-10-25-relmap-r1-batch

> **Artifact language:** canonical English scaffold. Generate the artifact in the batch's development language (`state.json` `language`); for Spanish batches **translate the prose, never a label**. This document mints no field a rule keys on — its ids (`US-`/`HLR-`/`LLR-`/`AT-`/`TC-`/`R-`) are read by the Atlas id-scanner and are not words in any language — so it carries no reserved-field block.

> **Owed in.** `core` — · `full` ✓

> Two chains (per the Two-layer validation rule) — a story is complete only when BOTH exist:
> - **Functional (white-box):** User Story → HLR → LLR → `TC-NNN` → File:line.
> - **Behavioral (black-box):** User Story → `AT-NNN` → observed outcome through the shipped surface.
> Every row must be complete when closing the batch (phase 6). Incomplete rows = coverage gaps and must be listed in the gaps section.
>
> Written at Phase 4 from the validated record (`../04-validation.md`); the user-story ids are the contract's `US-RM-NNN` (`../01-requirements.md` §2.6), the HLR/LLR ids drop the `RM` stem as the contract does (`HLR-RMP.1` etc.). `File:line` names the file and the symbol, not a line number, because the symbols are what the tests import; the nodes cited are collected on the gate tree (4022 selected of 4046 collected, 24 deselected).

---

## 1. Master table — functional chain (white-box)

| US | HLR | LLR | TC | File:line | Status | Notes |
|----|-----|-----|-----|-----------|--------|-------|
| US-RM-001 | HLR-RMP.1 | LLR-RMP.1.1 | `tests/test_relmap_profile.py::test_edge_table` · `tests/test_relmap_profile.py::test_catalogue_table` · `tests/test_relmap_profile.py::test_values_are_frozen` | `mapper/relmap/profile.py` (`REQHARNESS`, `EdgeType`, `GapRow`) | pass | mutants M-RMP-3 / M-RMP-5 |
| US-RM-001 | HLR-RMP.1 | LLR-RMP.1.2 | `tests/test_relmap_isolation.py::test_engine_names_no_kind` | `mapper/relmap/model.py`, `gaps.py` (profile-blind engine) | pass | M-RMP-1 |
| US-RM-001 | HLR-RMP.2 | LLR-RMP.2.1 | `tests/test_relmap_isolation.py::test_relmap_modules_import_only_what_the_contract_allows` · `tests/test_relmap_isolation.py::test_only_app_and_the_package_import_relmap` · `tests/test_relmap_isolation.py::test_init_re_exports_nothing` · `tests/test_relmap_isolation.py::test_tc_rm_01_a_cyclic_tree_map_is_still_refused_at_load` | `mapper/relmap/__init__.py` (zero bytes) · `tests/test_arch_osopen_callers.py` allow-list | pass | TC-RM-01; M-RMP-2 / M-RMP-4 / M-RMP-6; Layer A only, declared |
| US-RM-001 | HLR-RMM.1 | LLR-RMM.1.1 | `tests/test_relmap_model.py::test_value_defaults` · `tests/test_relmap_model.py::test_multi_parent_and_order` · `tests/test_relmap_isolation.py::test_py310_floor` · `tests/test_relmap_isolation.py::test_stdlib_bans` | `mapper/relmap/model.py` (`Node`, `Edge`, `RelMap`, `build_map`) | pass | the real 3.10 run is `not-run` (B-148) |
| US-RM-001 | HLR-RMM.1 | LLR-RMM.1.2 | `tests/test_relmap_model.py::test_problem_duplicate_id` · `::test_problem_unsafe_id` · `::test_problem_unsafe_id_boundary_200_is_safe` · `::test_problem_unknown_node_kind` · `::test_problem_unknown_edge_type` · `::test_problem_unknown_endpoint` · `::test_problem_unknown_endpoint_names_an_excluded_node_as_unknown` · `::test_problem_disallowed_pair` · `::test_problem_mixed_input_yields_six_and_keeps_the_valid_remainder` (9 arms) | `mapper/relmap/model.py` (`Problem`, `build_map`) | pass | M-RMM-1 |
| US-RM-001 | HLR-RMM.1 | LLR-RMM.1.3 | `tests/test_relmap_model.py::test_caps_nodes_at_cap_load_and_cap_plus_one_refuses` · `tests/test_relmap_model.py::test_caps_edges_at_cap_load_and_cap_plus_one_refuses` · `tests/test_relmap_model.py::test_caps_refuse_before_any_validation_work` | `mapper/relmap/model.py` (`RelMapLimitError`, caps from `mapper/osopen.py`) | pass | M-RMM-5 |
| US-RM-001 | HLR-RMM.2 | LLR-RMM.2.1 | `tests/test_relmap_model.py::test_direction_per_edge_type` · `tests/test_relmap_model.py::test_direction_premise_six_figures_on_the_reqharness_profile` | `mapper/relmap/model.py` (`up`, `down`) | pass | Layer A only, declared (first end-to-end observation is R2) |
| US-RM-001 | HLR-RMM.2 | LLR-RMM.2.2 | `tests/test_relmap_model.py::test_reach_budget_per_row` · `tests/test_relmap_model.py::test_reach_memo_is_counts` · `tests/test_relmap_model.py::test_reach_chain_at_cap_has_no_recursion_error` · `tests/test_relmap_model.py::test_queries_leave_the_graph_unchanged` | `mapper/relmap/model.py` (`reach`, `neighbourhood`, `VISIT_BUDGET`) | pass | M-RMM-6 / 8 / 10 / 11 |
| US-RM-002 | HLR-RMM.3 | LLR-RMM.3.1 | `tests/test_relmap_model.py::test_cycle_self_loop` · `::test_cycle_three_nodes_flags_each_cycle_edge_and_still_loads` · `::test_cycle_two_disjoint_cycles_in_node_order` · `::test_cycle_acyclic_reports_none_and_clears_a_caller_supplied_flag` · `::test_cycle_edge_between_two_cycles_is_not_in_a_cycle` · `::test_cycle_deep_chain_has_no_cycle_and_no_recursion_error` · `::test_cycle_deep_ring_is_one_component_and_no_recursion_error` (7 arms) | `mapper/relmap/model.py` (iterative Tarjan) | pass | Layer A only, declared (premise 5); M-RMM-3 |
| US-RM-002 | HLR-RMG.1 | LLR-RMG.1.1 | `tests/test_relmap_gaps.py::test_cycle_positive_two_node_ring` · `tests/test_relmap_gaps.py::test_cycle_positive_self_loop_is_a_component_of_one` · `tests/test_relmap_gaps.py::test_cycle_negative_no_cycle_no_gap` · `tests/test_relmap_gaps.py::test_us_without_at_positive_and_negative` · `tests/test_relmap_gaps.py::test_us_without_at_is_for_active_us_only` · `tests/test_relmap_gaps.py::test_open_at_without_test_positive_and_negatives` · `tests/test_relmap_gaps.py::test_verifies_without_evidence_positive_and_negative` · `tests/test_relmap_gaps.py::test_at_tagged_only_positive_and_negative` · `tests/test_relmap_gaps.py::test_llr_not_verified_positive_and_negative` · `tests/test_relmap_gaps.py::test_edge_type_filter_lacks_in_other_edge_type_is_no_verifier` · `tests/test_relmap_gaps.py::test_edge_type_filter_lacks_out_other_edge_type_is_no_binding` · `tests/test_relmap_gaps.py::test_hlr_without_llr_positive_and_negative` · `tests/test_relmap_gaps.py::test_an_incoming_refines_does_not_count_as_a_child` · `tests/test_relmap_gaps.py::test_orphan_tc_positive_and_negative_and_no_status_filter` · `tests/test_relmap_gaps.py::test_peer_kind_restricts_the_linking_edge` · `tests/test_relmap_gaps.py::test_the_empty_map_has_no_gap` · `tests/test_relmap_gaps.py::test_detection_order_is_catalogue_order_then_input_order` · `tests/test_relmap_gaps.py::test_detect_returns_reach_zero_and_does_not_spend_the_budget` · `tests/test_relmap_gaps.py::test_retired_node_not_reported_but_traversed` · `tests/test_relmap_gaps.py::test_an_active_node_is_reported_where_the_retired_one_is_not` · `tests/test_relmap_gaps.py::test_a_map_with_no_hlr_has_no_hlr_without_llr_gap` (the detector arms of `tests/test_relmap_gaps.py`) · `tests/test_relmap_gaps.py::test_gap_sentence_qualified` | `mapper/relmap/gaps.py` (`detect_gaps`, `Gap`) | pass | M-RMG-2 / M-RMG-4; reviewer mutant D (edge-type filter) |
| US-RM-002 | HLR-RMG.1 | LLR-RMG.1.2 | `tests/test_relmap_gaps.py::test_unsourced_kind_is_silent` · `tests/test_relmap_gaps.py::test_withdrawn_only_llr_is_not_a_gap` · `tests/test_relmap_adapter.py::test_snapshot_gaps` | `mapper/relmap/gaps.py` (activation and eligibility) | pass | M-RMG-1 / 3 / 6 |
| US-RM-002 | HLR-RMG.1 | LLR-RMG.1.3 | `tests/test_relmap_gaps.py::test_ranking` · `tests/test_relmap_gaps.py::test_rank_visit_cap` · `tests/test_relmap_gaps.py::test_rank_100k_sinks` · `tests/test_relmap_gaps.py::test_rank_limit_none_stays_inside_the_budget` | `mapper/relmap/gaps.py` (`rank_gaps`) | pass | M-RMG-2 / M-RMG-5 |
| US-RM-004 | HLR-RML.1 | LLR-RML.1.1 | `tests/test_relmap_descriptor.py::test_cause_table_is_k1_to_k17` · `tests/test_relmap_descriptor.py::test_cause_is_read_only` · `tests/test_relmap_descriptor.py::test_k1_k2_via_load_descriptor` · `::test_k6_k7_via_load_descriptor` · `::test_k8_anchor_and_alias_name_nothing` · `::test_k9_depth_65_refused_and_depth_64_loads` · `::test_k10_not_valid_yaml_prints_only_the_cause` | `mapper/relmap/descriptor.py` (`CAUSE`, `DescriptorError`, `load_descriptor`) | pass | M-RML-1 / 2 / 10 / 15 / 17 |
| US-RM-004 | HLR-RML.1 | LLR-RML.1.2 | `tests/test_relmap_descriptor.py::test_schema_table_refusals` · `tests/test_relmap_descriptor.py::test_schema_table_k16_names_the_key_not_the_value` · `tests/test_relmap_descriptor.py::test_default_descriptor_row` | `mapper/relmap/descriptor.py` (`Descriptor`, `default_descriptor`) | pass | M-RML-3 / M-RML-11 |
| US-RM-004 | HLR-RML.1 | LLR-RML.1.3 | `tests/test_relmap_descriptor.py::test_paths_confined` · `tests/test_relmap_descriptor.py::test_paths_confined_names_the_field` | `mapper/relmap/descriptor.py` (path confinement) | pass | M-RML-4 |
| US-RM-004 | HLR-RML.1 | LLR-RML.1.4 | `tests/test_yamlscan.py` (16) · `tests/test_prescan_refusal_goldens.py::test_prescan_refusal_text_is_byte_identical` | `mapper/yamlscan.py` (`prescan`, `YamlLimitError`) · `mapper/store.py` (`_prescan_sidecar` delegates) | pass | golden generated by base `25d69fe`; M-RML-5 / M-RML-6 / M-RML-12 |
| US-RM-004 | HLR-RML.1 | LLR-RML.1.5 | `tests/test_relmap_descriptor.py::test_read_repo_text_reads_a_plain_file` · `::test_read_repo_text_missing_file_is_k3` · `::test_read_repo_text_directory_is_k2_and_is_never_opened` · `::test_read_repo_text_fifo_is_k2_and_is_never_opened` · `::test_read_repo_text_link_is_k1_and_is_never_opened` · `::test_read_repo_text_file_symlink_is_k1` · `::test_read_repo_text_windows_junction_is_a_reparse_point_is_link_catches` · `::test_read_repo_text_a_hard_linked_regular_file_is_read` · `::test_read_repo_text_cannot_open_is_k4` · `::test_read_repo_text_unclassified_oserror_from_the_reader_is_k4` · `::test_read_repo_text_nul_is_k6_and_invalid_utf8_is_k7` · `::test_read_repo_text_cap_plus_minus_one_for_both_caps` · `::test_read_repo_text_cap_plus_one_reads_at_most_cap_plus_one_bytes` · `::test_read_repo_text_far_over_the_cap_is_never_read_whole` · `::test_read_repo_text_identity_mismatch_is_k2` · `::test_read_repo_text_device_mismatch_is_k2` · `::test_read_repo_text_opened_file_not_regular_is_k2` · `::test_read_repo_text_inode_zero_on_both_sides_is_read` · `::test_read_repo_text_inode_zero_on_one_side_only_is_read` · `::test_read_repo_text_the_opened_descriptor_is_closed` (20 arms) | `mapper/relmap/descriptor.py` (`read_repo_text`, `RepoReadError`) | pass | M-RML-7 / 8 / 14 / 16 |
| US-RM-004 | HLR-RML.1 | LLR-RML.1.6 | `tests/test_relmap_descriptor.py::test_repo_root_census_counts` · `::test_repo_root_census_sorted_by_code_point_and_case_sensitive` · `::test_repo_root_census_lists_non_regular_entries_so_reading_refuses_them` · `::test_repo_root_census_does_not_descend` · `tests/test_relmap_audit.py::test_canon_derived_once` | `mapper/relmap/descriptor.py` (`discover_descriptors`) · `mapper/relmap/audit.py` (`structure_lines`) | pass | M-RML-9 / M-RML-13 |
| US-RM-001 | HLR-RMA.1 | LLR-RMA.1.1 | `tests/test_relmap_adapter.py::test_snapshot_census` · `tests/test_relmap_adapter.py::test_snapshot_sha256` · `tests/test_relmap_adapter.py::test_snapshot_sha256_crlf_arm` · `tests/test_relmap_adapter.py::test_gitattributes_keeps_the_fixture_bytes` · `tests/test_relmap_adapter.py::test_live_invariants` | `mapper/relmap/adapter.py` (`derive_reqharness_map`) · `tests/fixtures/relmap/REQUIREMENTS.snapshot.md` · `.gitattributes` | pass | snapshot sha256 `b093c920…`; M-RMA-2/6/7/9 |
| US-RM-001 | HLR-RMA.1 | LLR-RMA.1.2 | `tests/test_relmap_adapter.py::test_rule_d1_table` · `tests/test_relmap_adapter.py::test_rule_d1_edges_are_unique_pairs_in_canon_order` · `tests/test_relmap_adapter.py::test_an_unlinked_llr_is_never_attached_to_a_prefix` | `mapper/relmap/adapter.py` (rule D-1) | pass | M-RMA-1 |
| US-RM-001 | HLR-RMA.1 | LLR-RMA.1.3 | `tests/test_relmap_adapter.py::test_reported_rows_are_notes` · `tests/test_relmap_adapter.py::test_unparsed_counts` · `tests/test_relmap_adapter.py::test_report_line_shape_yields_id` | `mapper/relmap/adapter.py` (`Derivation.reported`) | pass | M-RMA-3/5/8; reviewer mutant C |
| US-RM-001 | HLR-RMA.1 | LLR-RMA.1.4 | `tests/test_relmap_adapter.py::test_readonly` · `tests/test_relmap_adapter.py::test_canon_is_read_once_through_read_repo_text` | `mapper/relmap/adapter.py` | pass | M-RMA-4 |
| US-RM-003 | HLR-RMU.1 | LLR-RMU.1.1 | TC-RM-02 `tests/test_relmap_audit.py::test_tc_rm_02_raising_callable` · TC-RM-03 `tests/test_relmap_audit.py::test_tc_rm_03_refusal_path` · `tests/test_relmap_audit.py::test_hook_line_bound` · `tests/test_relmap_audit.py::test_fixed_lines_key_on_chain_status_not_verdict_text` · `tests/test_relmap_audit.py::test_run_cli_without_the_hook_is_byte_identical` | `mapper/reqharness/audit.py` (`run_cli`, `_hook_lines`) · `mapper/app.py` (`main` passes `structure_lines`) | pass | M-RMU-2/4/10/12 |
| US-RM-003 | HLR-RMU.1 | LLR-RMU.1.2 | `tests/test_relmap_audit.py::test_line_formats` · `tests/test_relmap_audit.py::test_header_first` · `tests/test_relmap_audit.py::test_format_structure_cuts_inside` · `tests/test_relmap_audit.py::test_refusal_line_hostile_name` · `tests/test_relmap_audit.py::test_sources_line_configured_string` · `tests/test_relmap_audit.py::test_gap_cap_is_twenty_with_an_overflow_line` · `tests/test_relmap_audit.py::test_note_cap_is_ten_with_an_overflow_line` | `mapper/relmap/audit.py` (`format_structure`) · `mapper/relmap/descriptor.py` (`refusal_line`) | pass-with-deviation (note wordings, G-003) | M-RMU-3/5/7/9/11/13/14 |
| US-RM-003 | HLR-RMU.1 | LLR-RMU.1.3 | `tests/test_relmap_audit.py::test_escaped_and_no_forged_verdict` · `tests/test_relmap_audit.py::test_reported_note_with_bidi_is_cut_and_escaped` · `tests/test_relmap_audit.py::test_exit_code_unchanged` | `mapper/reqharness/audit.py` (sink escapes every hook line) | pass | M-RMU-1 / M-RMU-8 |
| US-RM-003 | HLR-RMU.1 | LLR-RMU.1.4 | `tests/test_relmap_audit.py::test_byte_stable` · `tests/test_relmap_audit.py::test_canon_derived_once` | `mapper/relmap/audit.py` (`structure_lines`) | pass | M-RMU-6; seeds 0 and 2 |

## 1b. Behavioral chain (black-box)

> Per user story: the acceptance test that observes the outcome through the shipped surface. A story with a complete functional chain but no behavioral row is INCOMPLETE. All nodes are in `tests/test_relmap_audit.py` and drive `mapper --audit <repo>` as a subprocess.

| US | Acceptance test (`AT-NNN`) | Shipped surface | Observed outcome / deliverable | Status |
|----|----------------------------|-----------------|--------------------------------|--------|
| US-RM-001 | AT-117 · AT-119 · AT-124 | `mapper --audit` stdout | the summary line `nodes=275 (HLR=76, LLR=199) edges=196 (refines=196) cycles=0`; 7 `unparsed row` notes + the unlinked list, no invented edge; `skipped 3 canon rows …; unknown status=1` | pass |
| US-RM-002 | AT-118 · AT-125 | `mapper --audit` stdout | exactly one `MED · HLR WITHOUT LLR` line where it is a gap; the qualifier `(canon rows near this id could not be parsed or linked: N)` | pass |
| US-RM-003 | AT-120 · AT-122 · AT-126 · AT-128 · AT-129 | `mapper --audit` stdout and exit code | block after the verdict with the informational header; exit code and pre-verdict lines unchanged; hostile values escaped; unavailable lines; byte-stable under two hash seeds; every long value cut to 120 | pass-with-deviation (AT-126 (c) and marker scope, G-003) |
| US-RM-004 | AT-121 · AT-127 | `mapper --audit` stdout | `structure: refused (<base name>): <fixed cause text> - descriptor skipped` per cause; 8 descriptors then the overflow line | pass |
| — | AT-123 | retired (it drove the library API `MapStore.load`; now the Layer A pin TC-RM-01) | n/a | n/a — ledger `.65` |

---

## 2. Coverage summary

| Metric | Value |
|--------|-------|
| Total user stories | 4 |
| Covered user stories | 4 (100%) |
| Total HLR | 9 |
| Implemented HLR | 9 (100%) |
| Total LLR | 26 |
| Implemented LLR | 26 (100%) |
| Test cases | 447 collected items added by the batch (counted on disk by node-id set difference, 4 renamed parameter ids deleted — P-18) |
| TC pass | all 4017 passed in the orchestrator's gate run (4022 selected of 4046 collected, 24 deselected: 2 skipped, 3 xfailed; the DDR adds one node, 4023 on the sealed tree) |
| TC fail | 0 |
| TC pending | 0 |

---

## 3. Detected gaps

> Incomplete rows, requirements without TC, or TCs without code mapping.

| ID | Type | Description | Proposed action |
|----|------|-------------|-----------------|
| G-001 | declared Layer A only | HLR-RMM.2, HLR-RMM.3, HLR-RMP.2 and 7 of the 8 catalogue kinds have no shipped surface in R1 (contract OQ-R1-2, §5.4) | first end-to-end observation in R2 (B-140) and when the US/AT canon exists (B-141) |
| G-002 | not run | the real Python 3.10 run of the new code | BACKLOG B-148 (operator-run) |
| G-003 | wording drift | AT-126(c), AT-126 marker scope and the LLR-RMU.1.2 note wordings differ from the shipped behaviour: accepted deviations, `pass-with-deviation`, the shipped behaviour is normative | BACKLOG B-149 |
| G-004 | canon hygiene | 7 unparsed canon rows and 3 unlinked LLRs, reported by the block | BACKLOG B-142 (open) |
| G-005 | watch-items | double `build_map`; per-line bound of a generic hook; UX observations of the block | BACKLOG B-146, B-147, B-150 |

---

## 4. Changes from previous batch

| Type | Item | Detail |
|------|------|--------|
| new | US-RM-001…US-RM-004 | the relation-map kind (R1, headless): profile table, typed multi-parent read model, ranked gap detection, canon adapter, structure lines in `mapper --audit`, bounded descriptor reads |
| new | HLR-RMP.1, RMP.2, RMM.1, RMM.2, RMM.3, RMG.1, RML.1, RMA.1, RMU.1 | 9 HLR, 26 LLR (`../01-requirements.md` §3, §4) |
| new | AT-117…AT-122, AT-124…AT-129 · TC-RM-01…TC-RM-03 | 12 acceptance tests; AT-123 retired |
| new | modules `mapper/relmap/` (7 files) and `mapper/yamlscan.py` | `docs/ARCHITECTURE.md` §2 rows `relmap`, `yamlscan` |
| modified | `mapper/store.py` · `mapper/reqharness/audit.py` · `mapper/app.py` · `mapper/search.py` | prescan delegated to the leaf (byte-identical text); `run_cli` gains `extra_lines`; `app` passes the hook; one comment qualified (`mapper/model.py:149`) |
| modified | guards, same landing | `tests/test_arch_osopen_callers.py` allow-list · `tests/test_repair_artifact_claims.py` (declared `_CITATION_EXCEPTIONS`, ledger `.71`) · two comment wordings in `tests/test_ingestion_limits.py` and `tests/test_repair_sidecar.py` |
| closed at P4 | three full-suite regressions | LED `.69`, `.70`, `.71` (see `../04-validation.md` G-001) |

---

## 5. Quick bidirectional mapping

### 5.1 By user story
- **US-RM-001** → HLR-RMP.1, RMP.2, RMM.1, RMM.2, RMA.1 → LLR-RMP.1.1, RMP.1.2, RMP.2.1, RMM.1.1, RMM.1.2, RMM.1.3, RMM.2.1, RMM.2.2, RMA.1.1–RMA.1.4 → TC: `tests/test_relmap_profile.py`, `test_relmap_isolation.py`, `test_relmap_model.py`, `test_relmap_adapter.py` · AT-117, AT-119, AT-124
- **US-RM-002** → HLR-RMM.3, RMG.1 → LLR-RMM.3.1, RMG.1.1, RMG.1.2, RMG.1.3 → TC: `tests/test_relmap_model.py`, `test_relmap_gaps.py` · AT-118, AT-125
- **US-RM-003** → HLR-RMU.1 → LLR-RMU.1.1–RMU.1.4 → TC: `tests/test_relmap_audit.py` (TC-RM-02, TC-RM-03 and the formatter arms) · AT-120, AT-122, AT-126, AT-128, AT-129
- **US-RM-004** → HLR-RML.1 → LLR-RML.1.1–RML.1.6 → TC: `tests/test_relmap_descriptor.py`, `test_yamlscan.py`, `test_prescan_refusal_goldens.py` · AT-121, AT-127

### 5.2 By code file
- `mapper/relmap/profile.py` → LLR-RMP.1.1 → TC: `tests/test_relmap_profile.py`
- `mapper/relmap/model.py` → LLR-RMM.1.1–RMM.3.1 → TC: `tests/test_relmap_model.py`
- `mapper/relmap/gaps.py` → LLR-RMG.1.1–RMG.1.3 → TC: `tests/test_relmap_gaps.py` · AT-118, AT-125
- `mapper/yamlscan.py` and `mapper/store.py` (delegation) → LLR-RML.1.4 → TC: `tests/test_yamlscan.py`, `tests/test_prescan_refusal_goldens.py`, `tests/test_ingestion_limits.py` (unchanged oracle)
- `mapper/relmap/descriptor.py` → LLR-RML.1.1–RML.1.3, RML.1.5, RML.1.6, RMU.1.2 (`refusal_line`) → TC: `tests/test_relmap_descriptor.py` · AT-121, AT-127
- `mapper/relmap/adapter.py` → LLR-RMA.1.1–RMA.1.4 → TC: `tests/test_relmap_adapter.py` · AT-117, AT-119, AT-124
- `mapper/relmap/audit.py` → LLR-RMU.1.2–RMU.1.4 → TC: `tests/test_relmap_audit.py` · AT-120, AT-122, AT-126, AT-128, AT-129
- `mapper/reqharness/audit.py` and `mapper/app.py` → LLR-RMU.1.1 → TC: TC-RM-02, TC-RM-03, `test_hook_line_bound` · AT-120, AT-126

---

## 6. Batch sign-off

| Field | Value |
|-------|-------|
| Batch ID | `2026-10-25-relmap-r1-batch` |
| Closing date | 2026-10-25 — Phase 4 validated; DDR sealed approved with conditions; P5 post-mortem (`../05-postmortem.md`) and P6 documents (`executive-summary.md`, `functionality.md`) written the same day. The batch is closed for sign-off; merge and vault sync remain with the operator |
| Total iterations (sum of phases) | per `state.json` `iterations_per_station`: P1=1 (re-entered once after the first P2 pass), all others 0; P2 ran three review passes |
| Validation passed | yes — PASS-WITH-NOTES (`../04-validation.md`): the real Python 3.10 run is `not-run` (B-148, operator) |
| Synced to Obsidian | no |
