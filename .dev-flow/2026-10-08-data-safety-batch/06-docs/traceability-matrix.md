# Traceability Matrix — mapper — Batch `2026-10-08-data-safety-batch`

> Phase 6 artifact. The §1 rows were drafted by three small Kimi units (`kimi-code/kimi-for-coding`; one per HLR group) from `01-requirements.md`, the Layer A table of `04-validation.md` and `grep` over `mapper/`; composed and checked by the orchestrator (27 rows = the 27 LLR headings, no duplicates). `T/` = `tests/`. Status `pass` = passed in the Phase-4 gate run on `cab8181` (2920 passed / 0 failed, orchestrator).

## 1. Master table — functional chain (white-box)

| US | HLR | LLR | Test node(s) | Implementation (file:line) | Status |
|----|-----|-----|--------------|----------------------------|--------|
| US-001 | HLR-001 | LLR-001.1 | `T/test_inspector.py::test_llr_001_1_draft_surface_is_a_copy_and_clears` | `mapper/widgets/inspector.py:288` (`draft_values`), `:292` (`has_draft`), `:295` (`clear_draft`) | pass |
| US-001 | HLR-001 | LLR-001.2 | `T/test_inspector.py::test_llr_001_2_draft_updates_on_every_keystroke_and_posts_no_save`; `T/test_inspector.py::test_llr_001_2_a_stale_change_from_a_re_pointed_input_is_dropped` | `mapper/widgets/inspector.py:479` (`on_input_changed`) | pass |
| US-001 | HLR-001 | LLR-001.3 | inspection: `grep -rn 'FieldCommitted\|field_committed' --include='*.py' mapper tests` → 0 hits | `mapper/widgets/inspector.py` + `mapper/app.py` — `FieldCommitted`/`field_committed` 0 hits (removed) | pass |
| US-001 | HLR-001 | LLR-001.4 | `T/test_draft_save.py::test_llr_001_4_one_ctrl_s_is_one_store_save` | `mapper/app.py:3521` (`action_save_draft`); seat `mapper/keymap.py:184` (`KeyBinding("ctrl+s", "ctrl+s", "save_draft", "save", "node")`) | pass |
| US-001 | HLR-002 | LLR-002.1 | `T/test_inspector.py::test_llr_002_1_dirty_is_against_the_shown_value_plain_alters_title`; `T/test_inspector.py::test_llr_002_1_dirty_is_measured_against_plain_not_the_raw_title`; `T/test_inspector.py::test_llr_002_1_dirty_is_against_the_shown_value_unknown_state` | `mapper/widgets/inspector.py:312` (`_shown_value`), `:338` (dirty comparison vs shown value) | pass |
| US-001 | HLR-002 | LLR-002.2 | `T/test_inspector.py::test_llr_002_2_markers_update_without_remounting_the_focused_field`; `T/test_draft_save.py::test_at_003_header_counts_unsaved_fields_and_marks_each` | `mapper/widgets/inspector.py:223` (`_header`, `● unsaved (N)` at `:227`), `:264` (`_dirty_count`) | pass |
| US-001 | HLR-003 | LLR-003.1 | `T/test_draft_save.py::test_llr_003_1_modal_returns_the_token_for_each_key[s-save\|d-discard\|escape-stay]`; `test_llr_003_1_an_unbound_key_answers_nothing`; `test_llr_003_1_the_title_follows_the_ruled_wording`; `test_llr_003_1_an_empty_title_renders_empty_guillemets`; `test_llr_003_1_modal_title_is_literal_and_plain[esc\|click-markup\|surrogate]`; `test_llr_003_1_a_markup_payload_in_the_title_is_painted_literally`; `test_llr_003_1_the_hint_row_is_read_from_the_draft_seat`; `test_llr_003_1_the_hint_follows_the_seat_not_a_literal`; `test_llr_003_1_the_screen_bindings_are_generated_from_the_seat`; `test_llr_003_1_app_chords_do_not_pass_through_the_guard` | `mapper/screens/draft_guard.py:20` (`DraftGuardScreen`); `mapper/keymap.py:33` (`SCOPE_DRAFT`), `:282` (`MODAL_SCOPES`) | pass |
| US-001 | HLR-003 | LLR-003.2 | `T/test_draft_save.py::test_llr_003_2_node_change_guard_holds_the_inspector_on_the_draft_node`; `test_llr_003_2_a_second_mover_while_the_guard_is_up_stacks_no_second_guard`; `test_llr_003_2_a_move_onto_the_same_node_needs_no_guard`; `test_at_004_node_change_with_a_draft_presents_the_guard[s-save\|d-discard\|escape-stay]` | `mapper/app.py:3307` (`refresh_canvas`), `:3318` (`_guard_draft` before `_repoint`) | pass |
| US-001 | HLR-003 | LLR-003.3 | `T/test_draft_exits.py::test_at_005a_leave_with_q_is_guarded[s\|d\|escape]`; `T/test_draft_exits.py::test_at_005b_leave_with_esc_is_guarded[s\|d\|escape]`; `T/test_ddr_esc_search.py::test_llr_003_3_esc_with_a_live_search_clears_it_and_opens_no_guard` | `mapper/app.py:4934` (`action_home`), `:4937` (`action_back_or_home`), `:4970` (`_guard_draft(self.app.pop_screen)`) | pass |
| US-001 | HLR-003 | LLR-003.4 | `T/test_draft_exits.py::test_at_011_following_a_link_is_guarded[s\|d\|escape]`; `T/test_ddr_same_map_link.py::test_llr_003_4_a_link_to_the_same_map_is_guarded[s\|d\|escape]` | `mapper/app.py:3799` (`_guard_draft` before the linked-`MapScreen` push) | pass |
| US-001 | HLR-003 | LLR-003.5 | `T/test_draft_exits.py::test_at_012_quit_is_guarded[s\|d\|escape]`; `test_llr_003_5_a_second_ctrl_q_stacks_no_second_guard`; `test_llr_003_5_quit_walk_chains_two_drafts[d\|s]`; `test_at_013_quit_walks_a_lower_map_screen_draft`; `test_pdr_c1_quit_while_a_node_guard_is_open_does_not_wedge` | `mapper/app.py:5191` (`MapperApp.action_quit`), `:5220` (stack walk via `screen._guard_draft`) | pass |
| US-001 | HLR-003 | LLR-003.6 | `T/test_draft_exits.py::test_at_014_structural_write_opens_the_guard_first[at_014a\|at_014b]`; `test_at_014_structural_write_opens_the_guard_first_attachments[at_014c\|at_014d]` | `mapper/app.py:4790` (`action_add_child`), `:4840` (`action_archive`), `:3714` (`action_add_attachment`), `:3717` (`action_remove_attachment`) — each via `mapper/app.py:3462` (`_guard_draft`) | pass |
| US-001 | HLR-004 | LLR-004.1 | T/test_draft_save.py::test_llr_004_1_one_snapshot_and_one_write_per_multi_field_save | mapper/app.py:3732 | pass |
| US-001 | HLR-004 | LLR-004.2 | T/test_draft_save.py::test_at_002a_failed_save_reloads_from_disk[zero_files\|both_files]; T/test_draft_save.py::test_llr_004_2_failure_restores_the_undo_stack_exactly_at_depth; T/test_draft_save.py::test_llr_004_2_reload_raises_restores_the_pre_save_graph_without_a_write; T/test_draft_save.py::test_llr_004_2_a_save_failure_names_ctrl_s_to_retry; T/test_draft_save.py::test_llr_004_2_a_draft_on_a_vanished_node_is_dropped_with_a_warning; T/test_draft_save.py::test_llr_004_2_failure_clears_focus_and_rebuilds_nav; T/test_draft_save.py::test_llr_004_2_a_reload_that_carries_the_drafted_state_turns_it_clean | mapper/app.py:3524 | pass |
| US-001 | HLR-004 | LLR-004.3 | T/test_draft_save.py::test_at_009_undo_leaves_the_draft_and_recomputes_the_markers; T/test_draft_save.py::test_llr_004_3_undo_with_an_empty_stack_keeps_the_draft | mapper/app.py:3750 | pass |
| US-001 | HLR-004 | LLR-004.4 | T/test_draft_save.py::test_llr_004_4_ctrl_s_under_focus_writes_the_whole_map | mapper/store.py:809 | pass |
| US-001 | HLR-005 | LLR-005.1 | T/test_inspector.py::test_llr_005_1_enter_leaves_the_field_and_keeps_the_draft | mapper/widgets/inspector.py:487 | pass |
| US-001 | HLR-005 | LLR-005.2 | T/test_draft_save.py::test_llr_005_2_fill_in_hint_reads_the_save_glyph_from_the_seat | mapper/app.py:3870 | pass |
| US-001 | HLR-006 | LLR-006.1 | T/test_inspector.py::test_llr_006_1_state_change_updates_the_draft_and_writes_nothing | mapper/widgets/inspector.py:498 | pass |
| US-001 | HLR-006 | LLR-006.2 | T/test_inspector.py::test_llr_006_2_every_editable_surface_has_a_draft_key[title\|notes\|D\|state] | mapper/widgets/inspector.py:83 | pass |
| US-002 | HLR-007 | LLR-007.1 | `tests/test_double_question_mark.py::test_at_044_a_doubled_question_mark_opens_one_legend` | `mapper/app.py:5184` (`def action_help` pushes one `HelpScreen`) | pass |
| US-002 | HLR-007 | LLR-007.2 | `tests/test_repair_cycles.py::test_at_025b_a_damaged_map_declares_itself_and_the_others_keep_their_values`; `test_llr_n13_1_5_a_broken_map_is_distinguishable_from_a_healthy_EMPTY_one`; `test_llr_n13_1_5_the_damaged_card_carries_a_DECLARED_glyph`; `test_llr_n13_1_5_a_LOAD_WARNING_also_reaches_the_card`; `test_llr_n13_1_5_the_card_carries_the_DECLARED_state_string`; `test_llr_n13_1_5_no_OTHER_surface_paints_a_damaged_map_as_healthy[hero\|resume]` | `mapper/app.py:934` (damaged card paints `darkside.DAMAGED_MAP_STATE`, `mapper/darkside.py:857`) | pass |
| US-003 | HLR-008 | LLR-008.1 | `tests/test_repair_layout.py::test_at_r12_pressing_help_presents_every_map_binding`; `test_tc_r25_the_presented_set_equals_the_keymap_set_in_both_directions[map\|home]` | `mapper/keymap.py:307` (`def bindings_for`) | pass |
| US-003 | HLR-008 | LLR-008.3 | `tests/test_repair_layout.py::test_tc_r25_the_presented_set_equals_the_keymap_set_in_both_directions[app]`; `test_tc_r25b_a_screen_declaring_no_scope_presents_the_app_set` | `mapper/screens/help.py:288` (`HelpScreen.__init__` default `scope=SCOPE_APP`) | pass |
| US-003 | HLR-008 | LLR-008.2 | none (inspection — retirement record, ids absent from `tests/` by design) | `.dev-flow/BACKLOG.md:211` (`AT-033/034/035 RETIRED, travel with US-N14 (#D23)`) | pass |
| US-004 | HLR-009 | LLR-009.1 | `tests/test_help_scope.py::test_hlr_n16_4_legend_declares_its_own_keys[size0\|size1\|size2]`; `test_e3_the_own_keys_are_visible_at_rest_and_at_the_end[size0\|size1\|size2]`; `tests/test_en7.py::test_the_painted_legend_ends_with_the_rule[size0\|size1]` | `mapper/screens/help.py:442` (`def _render_own_scope_keys`) | pass |
| US-004 | HLR-009 | LLR-009.2 | `tests/test_help_scope.py::test_at_008_the_own_keys_loop_is_deterministic_under_a_late_scroll[size0\|size1\|size2]`; `tests/test_en7.py::test_the_painted_legend_ends_with_the_rule_under_a_late_scroll[size0\|size1]` | `mapper/screens/help.py:442` (`def _render_own_scope_keys`) | pass |

## 1b. Behavioral chain (black-box)

| US | Acceptance test(s) | Shipped surface | Observed outcome / deliverable | Status |
|----|--------------------|-----------------|--------------------------------|--------|
| US-001 | AT-001 … AT-015 (AT-002a, AT-013 Layer-A seams; AT-005a/b, AT-014a–d per key) — nodes in `T/test_draft_save.py`, `T/test_draft_exits.py`, `T/test_inc1c_ux.py` | the inspector, `ctrl+s`, the `save · discard · stay` guard, every exit key (`j`/`k`, `q`, `esc`, `↵` on a link, `ctrl+q`, `a`/`x`/`A`/`X`), `u` | the map's `.mmd` and `_nodos.yml` are byte-identical until `ctrl+s` and written once after (sha256 pair); the unsaved state is visible (red marks, hidden-card prefix); every exit asks first | pass |
| US-002 | AT-044 (`T/test_double_question_mark.py`), AT-025b (`T/test_repair_cycles.py::test_at_025b_…`) | the `?` legend; the home card table | one legend after a doubled `?`; a damaged map declares itself on its own card, others keep their values | pass |
| US-003 | AT-041 (`T/test_repair_layout.py::test_at_r12_…`), AT-042 (`test_tc_r25[map,home,app]` + `test_tc_r25b_…`, declared multi-arm reconciliation) | the traceability record + the legend's presented set | every acceptance id of the previous batch resolves to an on-disk node or a retirement (AT-033/034/035 retired with deferred US-N14) | pass (inspection + test) |
| US-004 | AT-008 (`T/test_help_scope.py::test_at_008_…`, test-instrument check) + TC-009.1 | the own-keys legend test under an injected late scroll | the loop is deterministic; the settle assertion fails loud when the scroll never lands | pass |

## 2. Coverage summary

| Metric | Value |
|--------|-------|
| Total user stories | 4 |
| Covered user stories | 4 (100%) |
| Total HLR | 9 |
| Implemented HLR | 9 (100%) |
| Total LLR | 27 |
| Implemented LLR | 27 (100%) |
| Test cases (collected at the gate) | 2923 (batch added 123: 2800 → 2923) |
| TC pass | 2920 + 3 xfailed (expected) |
| TC fail | 0 |
| TC pending | 0 |

Counts: `grep -c '^### HLR-'` → 9 and `grep -c '^### LLR-'` → 27 on `01-requirements.md`; the gate figures from `evidence/p4-gate-run.transcript`.

## 3. Detected gaps

| ID | Type | Description | Proposed action |
|----|------|-------------|-----------------|
| G-1 | declared exception | AT-002a and AT-013 are Layer-A injection tests (a failing store; a lower map screen's draft) — not reachable through keys alone | none — declared in `01-requirements.md` §3.1 / §5.1 |
| G-2 | declared exception | AT-008 is a test-instrument check (the shipped surface is the test itself) | none — declared |
| G-3 | declared reconciliation | AT-042 is realised by arms of two functions (three scope sets by design) | none — ledger `.67` |
| G-4 | accepted residuals | A-13, A-14, A-15 (`01-requirements.md` §6.3) | backlog B-102 |
