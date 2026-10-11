# Traceability matrix — 2026-10-11-reqharness-batch

> Master record US → HLR → LLR → test/verification node → evidence. Every id is
> parsed from `01-requirements.md`; coverage percentages in §2 are computed by
> `trace_coverage.py` in this directory (run: `python trace_coverage.py` from the
> repo root) — never by hand. `tests/` = `tests/`. Node ids were re-collected with
> `python -B -m pytest --collect-only -q -p no:cacheprovider`; every selector
> cited below collects ≥ 1 node.

## 1 · Master table (white-box)

`TC` cites `file::node` selectors (real collected node ids). Result is the
04-validation Layer-0 verdict.

| US | HLR | LLR | TC (selector → real node ids) | Result |
|---|---|---|---|---|
| US-RH-001 | HLR-RH.1 | LLR-RH.1.1 | tests/test_reqharness_config.py::test_load_rejects_unknown_reviewer_role · test_check_int_rejects_bool · test_nesting_event_stream_refuses_superlinear_depth · test_nesting_event_stream_refuses_lexically_bypassed_shapes · test_nesting_event_stream_boundary_and_quoted_scalars | pass |
| US-RH-001 | HLR-RH.1 | LLR-RH.1.2 | tests/test_reqharness_config.py::test_genesis_creates_chain_with_declared_admin | pass |
| US-RH-001 | HLR-RH.1 | LLR-RH.1.3 | tests/test_reqharness_config.py::test_canonical_json_typed_schema · test_time_format_is_ascii_fullmatch · test_nfc_refuses_colliding_keys | pass |
| US-RH-001 | HLR-RH.1 | LLR-RH.1.4 | tests/test_reqharness_config.py::test_email_sha256_roundtrip | pass |
| US-RH-001 | HLR-RH.2 | LLR-RH.2.1 | tests/test_reqharness_chain.py::test_admin_applies_to_someone_else_in_one_event | pass |
| US-RH-001 | HLR-RH.2 | LLR-RH.2.2 | tests/test_reqharness_chain.py::test_self_change_and_non_admin_stay_pending · test_pending_resolution_refuses_name_content_mismatch · test_pending_write_refuses_link_and_writes_nothing_outside | pass |
| US-RH-001 | HLR-RH.2 | LLR-RH.2.3 | tests/test_reqharness_chain.py::test_effective_roles_at_time_t · test_request_resolving_event_needs_alien_approver | pass |
| US-RH-001 | HLR-RH.2 | LLR-RH.2.4 | tests/test_reqharness_chain.py::test_policy_event_binds_config · test_policy_event_requires_config_hash | pass |
| US-RH-001 | HLR-RH.2 | LLR-RH.2.5 | tests/test_reqharness_chain.py::test_head_binding_unknown_head_not_verifiable | pass |
| US-RH-001 | HLR-RH.3 | LLR-RH.3.1 | tests/test_reqharness_chain.py::test_verify_walks_by_prev_hash_in_order_fork_resolve · test_hand_edit_breaks_chain_and_keeps_last_verified | pass |
| US-RH-001 | HLR-RH.3 | LLR-RH.3.2 | tests/test_reqharness_chain.py::test_merge_fork_is_detected · test_multi_event_excluded_branch_is_broken | pass |
| US-RH-001 | HLR-RH.3 | LLR-RH.3.3 | tests/test_reqharness_chain.py::test_hand_edit_breaks_chain_and_keeps_last_verified | pass |
| US-RH-001 | HLR-RH.3 | LLR-RH.3.4 | tests/test_reqharness_chain.py::test_fork_resolve_event_recovers · test_fork_recovery_reappend_on_head · test_resolve_naming_non_sibling_is_invalid · test_resolve_chosen_child_must_pass_approval_rule | pass |
| US-RH-001 | HLR-RH.3 | LLR-RH.3.5 | tests/test_reqharness_chain.py::test_input_limits_reported_by_name | pass |
| US-RH-002 | HLR-RH.4 | LLR-RH.4.1 | tests/test_reqharness_registry.py::test_normative_edit_needs_review_informative_marks_only | pass |
| US-RH-002 | HLR-RH.4 | LLR-RH.4.2 | tests/test_reqharness_registry.py::test_review_by_signer_without_role_in_force_is_pre_reviewed | pass |
| US-RH-002 | HLR-RH.4 | LLR-RH.4.3 | tests/test_reqharness_registry.py::test_model_review_never_closes_state | pass |
| US-RH-002 | HLR-RH.4 | LLR-RH.4.4 | tests/test_reqharness_registry.py::test_identity_reader_repo_local_then_global | pass |
| US-RH-002 | HLR-RH.4 | LLR-RH.4.5 | tests/test_reqharness_registry.py::test_review_by_signer_without_role_in_force_is_pre_reviewed | pass |
| US-RH-002 | HLR-RH.4 | LLR-RH.4.6 | tests/test_reqharness_registry.py::test_review_file_naming_and_exclusive_create | pass |
| US-RH-002 | HLR-RH.5 | LLR-RH.5.1 | tests/test_reqharness_registry.py::test_derived_states_boundary_catalog | pass |
| US-RH-002 | HLR-RH.5 | LLR-RH.5.2 | tests/test_reqharness_registry.py::test_derived_states_boundary_catalog | pass |
| US-RH-002 | HLR-RH.5 | LLR-RH.5.3 | tests/test_reqharness_registry.py::test_review_parse_cache_is_pure_accelerator · test_review_cache_caches_validated_parses_only · test_review_cache_size_guard_is_separate_limit | pass |
| US-RH-002 | HLR-RH.5 | LLR-RH.5.4 | measurement: evidence/p4-timing.transcript (median 0.4432 s ≤ 0.5 s) + tests/test_reqharness_cache_fastpath.py (5 nodes: test_warm_load_skips_unchanged_file_bytes · test_same_size_same_mtime_new_file_id_takes_full_path · test_changed_size_or_mtime_takes_full_path · test_same_size_same_mtime_same_inode_rewrite_is_the_residual · test_fast_path_results_identical_with_cache_deleted) | MET |
| US-RH-003 | HLR-RH.6 | LLR-RH.6.1 | tests/test_reqharness_baseline.py::test_baseline_freezes_commit_sha_and_diffs · test_baseline_load_refuses_untyped_objects_and_bad_name | pass |
| US-RH-003 | HLR-RH.6 | LLR-RH.6.2 | tests/test_reqharness_baseline.py::test_at_081_baseline_vs_now_reports_new_changed_retired | pass |
| US-RH-003 | HLR-RH.7 | LLR-RH.7.1 | tests/test_reqharness_release.py::test_release_rules_and_verdicts | pass |
| US-RH-003 | HLR-RH.7 | LLR-RH.7.2 | tests/test_reqharness_release.py::test_at_080_audit_report_counts_every_state_exactly · test_audit_cli_refuses_escaping_repo_path · test_audit_cli_resolves_relative_repo_argument · test_audit_cli_refuses_baseline_link_escaping_repo · test_audit_report_prints_chain_status_when_canon_unreadable · test_audit_cli_refusal_line_has_one_prefix · test_audit_render_escapes_registry_derived_text · test_audit_cli_names_no_registry_state · test_audit_render_escapes_bidi_and_separator_text · test_audit_cli_refusal_line_escapes_control_text · test_audit_visible_escapes_nbsp_combining_and_variation_selectors · test_audit_cli_baseline_schema_violation_is_named_not_a_traceback · test_audit_cli_baseline_name_traversal_is_refused_by_name · test_resolve_inside_refuses_lexical_dotdot_escape | pass |
| US-RH-003 | HLR-RH.7 | LLR-RH.7.3 | tests/test_reqharness_registry.py::test_identity_reader_repo_local_then_global | pass |
| US-RH-001 | HLR-RH.8 | LLR-RH.8.1 | tests/test_roles_screen.py::test_at_077a_roles_screen_opens_from_home_and_paints_matrix + test_inc9*/test_en5/test_keymap door-count guards | pass |
| US-RH-001 | HLR-RH.8 | LLR-RH.8.2 | tests/test_roles_screen.py::test_at_078_non_admin_toggle_pends_admin_applies_in_one_key · test_at_079_tampered_chain_paints_broken_state_and_blocks_release | pass |
| US-RH-001 | HLR-RH.8 | LLR-RH.8.3 | tests/test_roles_screen.py::test_at_077b_status_band_shows_chain_head_viewer_and_pending | pass |
| US-RH-001 | HLR-RH.8 | LLR-RH.8.4 | tests/test_roles_screen.py::test_at_077c_file_derived_text_paints_through_text_sinks + test_at_077c_…_source_censuses_no_hex_no_stray_glyph_no_str_sink | pass |
| US-RH-001 | HLR-RH.8 | LLR-RH.8.5 | screen source censuses (mapper/widgets·screens census pins, itemised in increment-009 r4) | pass |
| US-RH-001 | HLR-RH.8 | LLR-RH.8.6 | tests/test_roles_screen.py::test_at_082_admin_resolves_pending_with_a_and_r · test_at_083_forked_chain_paints_excluded_and_recovers | pass |
| US-RH-003 | HLR-RH.9 | LLR-RH.9.1 | 06-docs/d12-devflow-review-ledger-proposal.md (this document set) | delivered |

## 1b · Behavioral chain (black-box)

| US | Acceptance test | Shipped surface | Observed outcome | Status |
|---|---|---|---|---|
| US-RH-001 | AT-077a | roles screen opened from home with `R`, paints the matrix (variant B, genesis copy) | matrix paints through Text sinks | pass |
| US-RH-001 | AT-077b | footer status band | chain head, viewer identity, pending count — 6 elements | pass |
| US-RH-001 | AT-077c | file-derived text | paints through Text sinks; source censuses: no hex, no stray glyph, no str sink | pass |
| US-RH-001 | AT-078 | `space` propose on the matrix | non-admin toggle pends; admin applies in one event | pass |
| US-RH-001 | AT-079 | tampered chain on screen | broken state paints, release blocked, screen read-only | pass |
| US-RH-003 | AT-080 | `mapper --audit <repo>` (real subprocess) | report counts every derived state exactly; unentitled separate | pass |
| US-RH-003 | AT-081 | `baseline vs now` (real subprocess) | new/changed/retired (+stale/in-base classes) — 5/5 classes | pass |
| US-RH-001 | AT-082 | admin `a`/`r` on a pending cell | request resolves once; own request refused; non-admin/tampered inert; named refusals | pass |
| US-RH-001 | AT-083 | forked chain on screen | both children paint excluded; `resolve` recovers (core) | pass |

## 2 · Coverage summary

Computed by `trace_coverage.py` (executed at close; its stdout is quoted in
`../05-postmortem.md`'s metrics and in the close record): every US, HLR and
LLR in `01-requirements.md` appears in §1; every AT in §5.1 appears in §1b;
every cited `file::node` selector collects ≥ 1 node and the cited files pass
in the gate suite (3376 passed, 0 failed at `6b6750e`).

- US coverage: 3/3 (100%) — each US has ≥ 1 black-box AT observing its outcome.
- HLR coverage: 9/9 (100%) — each HLR owns ≥ 1 LLR with executing nodes.
- LLR coverage: 36/36 (100%) — 35 by suite nodes, LLR-RH.5.4 by the pinned
  measurement protocol (P4 + PERF-RH re-measurement, MET 0.4432 s ≤ 0.5 s),
  LLR-RH.9.1 by this document set.
- AT coverage: 9/9 (100%) pass through the shipped surface.

## 3 · Detected gaps

| ID | Requirement | Gap | Severity | Action |
|---|---|---|---|---|
| G-001 | LLR-RH.5.4 | warm-cache derive missed the budget at P4 (5.27 s) | major | RESOLVED — stat fast path, re-measured 0.4432 s MET (increment-010) |
| G-002 | LLR-RH.5.4 | same-stat in-place rewrite defeats the fast path | residual (stated) | test-pinned (`test_same_size_same_mtime_same_inode_rewrite_is_the_residual`); `--audit` cache-off catches it |
| G-003 | HLR-RH.3 | multi-event excluded branch reports `chain broken`, no core recovery | major | B-126 (widened) |
| G-004 | HLR-RH.6 | no `reactivated` diff class; no progression on diff | major | B-125 |
| G-005 | HLR-RH.7 | no committer-vs-reviewer warning | minor | B-124 |
| G-006 | HLR-RH.8 | roles-screen git calls on the UI thread (≈ 30 s worst case) | major | B-127 |
| G-007 | full suite | post-close1 full-suite run | minor | orchestrator-owned (C-25), done at `6b6750e` (3376 passed) |

## 5 · Quick bidirectional mapping

### 5.1 By user story

- **US-RH-001 (admin):** HLR-RH.1 · HLR-RH.2 · HLR-RH.3 · HLR-RH.8 → AT-077a/b/c, AT-078, AT-079, AT-082, AT-083.
- **US-RH-002 (reviewer):** HLR-RH.4 · HLR-RH.5 → (white-box nodes; states observed via AT-080's audit counts).
- **US-RH-003 (board member):** HLR-RH.6 · HLR-RH.7 · HLR-RH.9 → AT-080, AT-081, LLR-RH.9.1 (D12 proposal).

### 5.2 By code file

- `mapper/reqharness/config.py` → LLR-RH.1.x, LLR-RH.3.5 (depth bound).
- `mapper/reqharness/chain.py` → LLR-RH.2.x, LLR-RH.3.1–3.4.
- `mapper/reqharness/identity.py` → LLR-RH.4.4, LLR-RH.7.3.
- `mapper/reqharness/{reviews,pending,derive,cache}.py` → LLR-RH.4.x, LLR-RH.5.x.
- `mapper/reqharness/{baseline,release,audit}.py` → LLR-RH.6.x, LLR-RH.7.x.
- `mapper/screens/roles.py` (+ `mapper/screens/home.py` door, `mapper/keymap.py` scope) → LLR-RH.8.x.
- `06-docs/d12-devflow-review-ledger-proposal.md` → LLR-RH.9.1.
