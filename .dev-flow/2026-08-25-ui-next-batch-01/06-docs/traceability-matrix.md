# Traceability matrix — `2026-08-25-ui-next-batch-01`

Generated from the **collected pytest nodes**, not transcribed from the spec: every row below was
produced by walking the real test collection, so a row cannot claim a node that does not exist.

## Behavioural chain — `US -> AT -> on-disk node`

| AT | Story | On-disk node |
|---|---|---|
| `AT-N01A` | US-N01 edición in-situ | `tests/test_inspector.py::test_at_n01a_editing_a_schema_field_persists_to_disk` |
| `AT-N01B` | US-N01 edición in-situ | `tests/test_inspector.py::test_at_n01b_state_persists_for_every_value` |
| `AT-N01C` | US-N01 edición in-situ | `tests/test_inspector.py::test_at_n01c_rows_are_labelled_from_the_schema_not_the_key` |
| `AT-N01D` | US-N01 edición in-situ | `tests/test_inspector.py::test_at_n01d_required_and_empty_is_flagged` |
| `AT-N01E` | US-N01 edición in-situ | `tests/test_inspector.py::test_at_n01e_hostile_file_derived_text_renders_literally` |
| `AT-N02A` | US-N02 adjuntos | `tests/test_attachments.py::test_at_n02a_adding_an_attachment_persists` |
| `AT-N02B` | US-N02 adjuntos | `tests/test_attachments.py::test_at_n02b_activating_an_attachment_reaches_the_boundary` |
| `AT-N02C` | US-N02 adjuntos | `tests/test_attachments.py::test_at_n02c_removing_deletes_exactly_that_one` |
| `AT-N02D` | US-N02 adjuntos | `tests/test_attachments.py::test_at_n02d_a_refused_attachment_is_reported_not_silently_dropped` |
| `AT-N03A` | US-N03 keymap único | `tests/test_keymap.py::test_at_n03a_every_binding_resolves_to_a_real_action` |
| `AT-N03B` | US-N03 keymap único | `tests/test_palette.py::test_at_n03b_selecting_a_palette_entry_executes_it` |
| `AT-N03C` | US-N03 keymap único | `tests/test_palette.py::test_at_n03c_palette_is_scoped_to_the_active_screen` |
| `AT-N03D` | US-N03 keymap único | `tests/test_palette.py::test_at_n03d_help_shows_exactly_the_active_scope` |
| `AT-N03E` | US-N03 keymap único | `tests/test_rail.py::test_at_n03e_keybar_truncation_names_what_is_hidden` |
| `AT-N03F` | US-N03 keymap único | `tests/test_keymap.py::test_at_n03f_bound_keys_match_the_seat_exactly` |
| `AT-N04A` | US-N04 worklist de cobertura | `tests/test_worklist_safety.py::test_at_n04a_enter_on_a_coverage_row_jumps_and_focuses_the_gap` |
| `AT-N04B` | US-N04 worklist de cobertura | `tests/test_worklist_safety.py::test_at_n04b_next_gap_advances_across_nodes_and_wraps` |
| `AT-N04C` | US-N04 worklist de cobertura | `tests/test_worklist_safety.py::test_at_n04c_a_complete_map_reports_exhaustion_and_does_not_cycle` |
| `AT-N04D` | US-N04 worklist de cobertura | `tests/test_worklist_safety.py::test_at_n04d_complete_map_coverage_report_is_not_a_selectable_row` |
| `AT-N05A` | US-N05 seguridad | `tests/test_worklist_safety.py::test_at_n05a_archiving_a_subtree_asks_first_and_a_refusal_preserves_it` |
| `AT-N05B` | US-N05 seguridad | `tests/test_worklist_safety.py::test_at_n05b_accepting_removes_exactly_that_subtree` |
| `AT-N05C` | US-N05 seguridad | `tests/test_worklist_safety.py::test_at_n05c_undo_survives_leaving_and_re_entering_the_map` |
| `AT-N05D` | US-N05 seguridad | `tests/test_worklist_safety.py::test_at_n05d_undo_on_an_empty_stack_reports_and_does_not_raise` |
| `AT-N06A` | HLR-N06 modelo de foco | `tests/test_rail.py::test_at_n06a_rail_selection_marks_focus_and_the_hint_names_the_region` |
| `AT-N06B` | HLR-N06 modelo de foco | `tests/test_inspector.py::test_at_n06b_escape_leaves_the_field_and_keeps_the_value` |
| `AT-N06D` | HLR-N06 modelo de foco | `tests/test_rail.py::test_at_n06d_regions_collapse_by_key_and_by_width` |
| `AT-N06E` | HLR-N06 modelo de foco | `tests/test_rail.py::test_at_n06e_narrow_terminal_auto_collapses_the_rail` |

**27 acceptance tests, each mapping to exactly one node** (control C-18, verified
mechanically — see `04-validation.md` §2).

## Verification that is NOT a test

| id | Subject | Method | Note |
|---|---|---|---|
| `MAN-01` | the hop from `open_external(...)` to the OS default application | **inspection** | No honest black-box oracle short of launching a real program. `AT-N02b` gates the chain up to the seam with the launcher injected; **a green `AT-N02b` is not sign-off for MAN-01.** |

## Functional chain — `HLR -> LLR -> tests`

| HLR | LLRs | Primary test files |
|---|---|---|
| HLR-N01 in-situ editing | LLR-N01.1 … N01.11 | `tests/test_inspector.py` |
| HLR-N02 attachments | LLR-N02.1 … N02.10 | `tests/test_attachments.py` |
| HLR-N03 one keymap | LLR-N03.1 … N03.6 | `tests/test_keymap.py`, `tests/test_palette.py` |
| HLR-N04 coverage worklist | LLR-N04.1 … N04.3 | `tests/test_worklist_safety.py`, `tests/test_coverage.py` |
| HLR-N05 safety | LLR-N05.1 … N05.6 | `tests/test_worklist_safety.py` |
| HLR-N06 focus model | LLR-N06.1 … N06.6 | `tests/test_rail.py`, `tests/test_inspector.py` |

**Total collected nodes: 210.** Suite: `210 passed`, exit 0.
