# Validation — mapper — Batch `2026-08-26-ui-next-batch-02`

> Phase 4 artifact, authored after the fact from existing evidence (the batch was implemented,
> reviewed and merged before this record existed). The ONE complete gate-suite run was executed by
> the **orchestrator** (`C-25`); the `qa-reviewer` evaluates its result, attributes every row, and
> returns the rows here. Nothing below was re-run for this artifact; every number, node id and
> verdict is cited to a file in this repo or to the attached gate transcripts.

---

## ✅ Verdict (read first)

- **Result:** `PASS-WITH-NOTES`
- **Layer 0:** 14 increments carry an explicit per-increment mutant kill count in `state.json` `p3_progress` (A-114…A-126, A-128), and A-105 / A-111 / Inc-7 / Inc-8 record named RED kills in their own records; examples below. No increment recorded `none — no unit met the decision or boundary criterion`.
- **Requirements:** 35 amendments (A-105…A-139) · 34 carry a named, passing test node · 1 (A-106) is a documentation amendment with no dedicated node · 0 blocker fails
- **Black-box acceptance (Layer B):** ✓ every observable amendment driven through the shipped Textual surface (`App.run_test` / `pilot.press`) at 87 / 118 / 140 columns, with boundary + negative inputs, and the whole-branch adversarial PR QA (`VERDICT-merge-2026-10-03.md`) as the acceptance pass
- **Surface-reachability (bidirectional):** ✓ every named input dimension and deliverable observed through the handler (see the matrix in Detail) — no reachability gap recorded
- **Supersession inspection (read off the P3 packets):** ✓ superseding amendments are marked in-document (`A-108`→`A-107` width clauses; `A-119`→`A-117` st.5 / `A-118` st.1–2; `A-136`→`A-134` separator; `A-138` correction appended to `A-137`) and no surviving code ref names a retired id; no dedicated P3 packet ran the sweep
- **Test ledger:** ⚠ not closed — post is 2797 passed (+3 xfailed, 24 deselected) on the gate lane; collected count not recorded; baseline 429 was a `--collect-only -o addopts=` count (deselected included), so the units differ; D/A not recorded as one pair (see Detail)
- **Evidence checklist (qa-reviewer):** `qa-reviewer` agent evaluated the rows (gate run executed by the orchestrator; draft by `deepseek-v4-pro`) · 11 of 12 rows ✓ with evidence

> Justification for the token: the ONE complete gate run is clean — **2797 passed, 24 deselected, 3 xfailed, 0 failed** on the squash tree `46e190b` == branch tip `4572e52` (`gate-run-master-tree.txt`); one earlier full run hit FLAKE-2 once (10/10 alone); zero HIGH findings across the whole-branch gates (`VERDICT-merge-2026-10-03.md`). The notes are: one open flake (FLAKE-2) and operator-deferred residuals B-36, B-79…B-97 (`.dev-flow/BACKLOG.md`), none of which blocks this batch's gate.

---

## Detail (reference)

### Layer 0 — unit

Units that met either criterion (cyclomatic complexity ≥ 3, or a transform crossing a declared boundary in `docs/ARCHITECTURE.md`). Representative set, not the full population:

| Unit | Which criterion | Node id | Result |
|---|---|---|---|
| `mapper/osopen.py::confine_reason` (path-confinement walk) | crosses the filesystem/workspace boundary (ARCHITECTURE §3) | `test_inc9q_sec_f1_a_stream_suffix_on_a_link_component_is_refused_before_any_filesystem_call` | pass |
| `mapper/github.py::_classify` / `_is_url` (typed-repo decision) | crosses the process-argument boundary | `test_inc9k_s1_the_allow_list_predicate_refuses_a_url_shaped_text_outside_the_grammar` | pass |
| `mapper/app.py::HomeScreen._sparkline_text` (division by `max_count`) | boundary: division guard on activity data | `test_a105_a_zero_activity_workspace_paints_every_bar_at_the_floor` | pass |
| `mapper/store.py::_coerce_field` (widened coercion ladder) | crosses the load/save boundary (`LLR-STO.1.1`) | `test_g6a_load_coerces_a_sidecar_lone_surrogate_title_instead_of_denying_the_map` | pass |
| `mapper/keymap.py::bindings_for` (TEXT_ONLY_SCOPES omission) | crosses the seat/label boundary | `test_bindings_for_a_text_only_scope_offers_only_keys_that_work` | pass |
| `mapper/github.py::_run_git` pin set (`_GIT_PINS`) (`-c log.showSignature=false …`) | crosses the subprocess boundary | `test_gate2_sec3_every_git_call_pins_the_config_keys_that_can_run_a_program` | pass |

**Measured by mutation, never by line coverage.** Named mutations and their RED, drawn from the increment records and `state.json`:

| Unit | Mutation applied | RED observed? | Transcript |
|---|---|---|---|
| `_sparkline_text` (`A-105`) | `max_count = sum(counts)` (M6) and binary tier (M7) | survived first pass; **killed** by the two-day arm | `state.json` `p3_progress.SPARKLINE_MICRO_INCREMENT_RELEASED_2026-09-28.review` — "9 mutants (M6 max->sum and M7 binary tier survived -> INC21-CR-F1); fold round added a two-day arm that kills both" |
| `confine_reason` step 1b (`A-125`) | stream-suffix refusal removed (`lnk:$I30` accepted) | RED | `state.json:1278` — `Inc-9q` "mutants: 23 killed; 1 survivor led to removing dead code" |
| `github._classify` (`A-121`) | `_is_local_path` total-predicate catch removed (`~nosuchuser` raises) | RED | `state.json:1384` — `Inc-9m` "mutants: 35 RED / 3 equivalent survivors (declared)" |
| `confine_reason` step 4 backstop (`A-126`) | final `resolve()` backstop deleted (`lstat` misreport returns `ok`) | RED | `state.json:1254` — `Inc-9r` "mutants: 16/16" |
| `DsChip.Changed` (`A-128`) | `control` property omitted (returns `None`) | RED | `state.json:1230` — `Inc-X3` "mutants: 7/7" |
| Inc-8 legend (`A-107`/`A-108`/`A-109`) | 12 carried findings each discharged by a named mutant; closing battery | 8 of 10 RED | `state.json:803` "12 carried findings discharged by mutant"; `:870` "10 mutants, 8 RED as claimed, MUT-H2b and MUT-SEARCH survive -> F2, F3" |

### UX walkthrough — only if trigger family D fired

> Trigger family **D fired** (this batch is a UI batch: the atlas canvas, the legend, and the
> whole-UI English migration). The walkthrough below is driven through the REAL mechanism — the
> Textual pilot (`App.run_test`, `pilot.press`) — not a proxy.

| Criterion (when the user does X, they observe Y) | Driven with the REAL mechanism | Painted result asserted | Verdict |
|---|---|---|---|
| An attachment chip opens with real keys / a real click (`A-128`) | `App.run_test` + `pilot.press("tab"/"enter"/"space")` and a synthetic click at 87/118 cols | resolved path handed to a recording launcher stub | pass |
| `?` is a character in every text field (`A-135`) | real `?` press in each field; `select_on_focus=False` | cursor at end, `?` appended, no whole-value replace | pass |
| The legend docks while ≥ `LEGEND_DOCK_MIN_VIEW_CELLS` view cells stay visible (`A-108`) | `pilot` at 87 (modal) and 118/140 (docked) | docked panel 44 cols, view undimmed, pan reveal on the visible canvas (`A-109`) | pass |
| `j`/`k` on home with ≥1 map does not stop the app (`A-139` PR-QA-F1) | real `j`/`k` press | home table cursor moves, app survives | pass |
| A pan edge shows `edge of the map` and the hint clears on view change (`A-139` PR-QA-F3) | real `o`/`r`/`R` pan | resting hint restored, `_clear_pan_hint` covers both | pass |

**Mechanism used:** a headless Textual driver (`App.run_test` + `pilot.press`), plus the composited-frame reader in the test harness — not `none`.

| Act | What it is | Performed? |
|---|---|---|
| Automated walkthrough | the criteria above, driven through the REAL mechanism | performed — per-increment UX reviews at 87/118/140 cols; the whole-branch adversarial PR QA (`VERDICT-merge-2026-10-03.md`) |
| Expert inspection | a cognitive walkthrough against declared criteria, by a reviewer | performed — per-increment `ux-reviewer` lenses (e.g. `INC9P-UX-F1`, `INC9Q-UX-F2`) |
| Evaluation with users | real users of the system, doing the tasks in context | not performed — this team is one person and no user of this surface exists outside it |

- **Method:** headless Textual pilot runs at the batch's driven widths (widths per test file, e.g. `tests/test_gate2.py:33` `NARROW=(87,34)`; `tests/test_repair_layout.py` `NARROW_SIZE=(100,24)`, `WIDE_SIZES=[(140,45),(120,40)]`), plus the whole-branch adversarial PR QA which drove the app with real keys and reported `PR-QA-F1`…`PR-QA-F12`.
- **Participants or population:** none — one-person team; no real user of the surface exists outside the operator.
- **Evidence of the evaluation:** `VERDICT-merge-2026-10-03.md` (adversarial PR QA); `state.json` `p3_progress` per-increment UX review verdicts (`PASS-WITH-NOTICES`/`PASS-WITH-FINDINGS`).
- **Limits:** no real-user evaluation (ISO 9241-210); automated walkthroughs are not users; terminal mouse input is Pilot's synthetic click, not a real terminal (`A-128`).

### Layer A — functional (white-box): per-requirement results

> One row per amendment A-105…A-139. `Result` = pass / fail. `RED→GREEN` cites the record that
> shows the arm reddening before the fix and going green after. Node ids are the collected pytest
> node ids on disk; "no dedicated node" marks a documentation-only amendment.

| Req | What it requires (≤12 words) | Test node id(s) | RED→GREEN record | Result |
|-----|------------------------------|-----------------|------------------|--------|
| A-105 | zero-activity sparkline paints floor bars, no raise | `test_sparkline_floor.py::test_a105_a_zero_activity_workspace_paints_every_bar_at_the_floor` (and 2 siblings) | `increment-021-sparkline-zero-division.md`; `state.json:664` "regression RED on base (ZeroDivisionError app.py:579), GREEN on fix" | pass |
| A-106 | retire V7/V8/V4; discharge resolves to painted forms | no dedicated node — docs-only; predicate pinned by `test_help_scope.py::test_llr_n16_2_1_every_member_is_painted_in_its_declared_style` | `increment-022-inc8-legend.md` "Design pass" | pass (docs-only) |
| A-107 | docked legend full height, modal keeps cap | `test_repair_layout.py::test_tc_r36_the_dialog_height_is_governed_by_a_named_declaration[docked-full-height]` | `increment-022-inc8-legend.md` "Design pass 2" | pass |
| A-108 | dock threshold derived from visible-minimum | `test_repair_layout.py::test_tc_r36_...[cap-governs]` / `...[percentage-governs]`; `test_legend_design.py::test_f9_the_legend_docks_exactly_while_the_view_keeps_its_minimum` | `increment-022-inc8-legend.md` "Design pass 3" | pass |
| A-109 | docked pan range = visible canvas + margin | `test_legend_design.py::test_g2_a_card_at_the_maps_right_edge_is_revealed_whole_and_closing_returns_it`, `::test_h3_the_painted_margin_is_the_declared_one_everywhere` | `increment-022-inc8-legend.md` "Design pass 4" + addendum | pass |
| A-110 | no tracked file names a real account | `test_no_operator_paths.py::test_a110_no_undeclared_user_profile_path_in_any_tracked_file` (+ env backstop arm) | `increment-023-scrub-operator-paths.md`; `state.json:908` "RED 249 lines / 70 files -> GREEN" | pass |
| A-111 | coerce ficha text; every save degrades to toast | `test_g6_store_surrogates.py::test_g6a_load_coerces_a_sidecar_lone_surrogate_title_...` (+ 11 corrective/census arms) | `increment-024-g6-store-surrogates.md`; A-111 "RED-before evidence (all 8 arms reproduce…)" | pass |
| A-112 | English chrome: labels, headers, one name/view | `test_inc9.py::test_a112_the_chrome_is_english` (+ census/lexicon arms) | `increment-025-inc9.md` | pass |
| A-113 | map-id confinement, create-never-overwrites | `test_seed_safety.py::test_seed_store_create_refuses_an_existing_id`; `test_seed2.py::test_seed2_f3_store_refuses_an_id_over_the_limit` | `increment-028-seed-safety.md`; `state.json:1016` "396 hostile runs, 0 escapes" | pass |
| A-114 | repo specs are data; failure = fixed category | `test_inc9f.py::test_inc9f_f1_a_dash_url_is_refused_before_any_git_runs` (+ census) | `increment-032-inc9f.md`; `state.json:1579` "30/30 killed" | pass |
| A-115 | palette contrast, mirror keyed on URL, typed text plain | `test_inc9g.py::test_inc9g_sec_f1_two_remotes_with_one_last_segment_get_two_mirrors` | `increment-033-inc9g.md`; `state.json:1546` "34/34 run killed (record); reviewer: R8 survives, record claim wrong" | pass (arm green; record's 34/34 mutant claim contradicted by the reviewer — R8 survivor, see Gaps) |
| A-116 | row-0 lit, one toast, prune, typed stale signal | `test_inc9h.py::test_inc9h_cr_f5_the_timeout_is_a_typed_signal_not_a_message_suffix` | `increment-034-inc9h.md`; `state.json:1490` "33/33" | pass |
| A-117 | fallback key disjoint; credential refused | `test_inc9i.py::test_inc9i_sec_f2_userinfo_in_a_typed_url_is_refused_before_any_process` | `increment-035-inc9i.md`; `state.json:1516` "11/11" | pass |
| A-118 | curl-style authority read; redact userinfo | `test_inc9j.py::test_inc9j_sec_f1_extra_slashes_do_not_hide_userinfo_from_the_refusal` | `increment-036-inc9j.md`; `state.json:1469` "12/12" | pass |
| A-119 | closed allow-list for typed repo URLs | `test_inc9k.py::test_inc9k_s1_an_allowed_url_reaches_the_clone_as_typed` | `increment-037-inc9k.md`; `state.json:1441` "25/26 (M16 equivalent, declared)" | pass |
| A-120 | one refusal sentence (T1); UNC before FS call | `test_inc9l.py::test_inc9l_unc_a_double_slash_text_touches_no_filesystem_and_is_refused` | `increment-038-inc9l.md`; `state.json:1414` "23/23" | pass |
| A-121 | allow-list for typed local paths (one helper) | `test_inc9m.py::test_inc9m_s1_every_other_text_is_refused_before_any_filesystem_call` | `increment-039-inc9m.md` | pass |
| A-122 | sidecar paths confined; DOS devices refused; U1/U2 | `test_inc9n.py::test_inc9n_f2_a_dos_device_name_is_refused_by_the_helper_before_any_filesystem_call` | `increment-040-inc9n.md`; `state.json:1359` "28/28" | pass |
| A-123 | one containment helper; V1/V2; FLAKE-3 fix | `test_inc9o.py::test_inc9o_confine_refuses_a_link_before_any_stat_resolve_or_final_path_lookup` | `increment-041-inc9o.md`; `state.json:1332` "31 RED / 2 equivalent on Windows" | pass |
| A-124 | normalised components, hard links, W1/W2 | `test_inc9p.py::test_inc9p_sec_f1_a_normalised_component_is_refused_before_any_filesystem_call` | `increment-042-inc9p.md`; `state.json:1300` "27/27" | pass |
| A-125 | stream suffix, hard links at open, X1/X2 | `test_inc9q.py::test_inc9q_sec_f1_a_stream_suffix_on_a_link_component_is_refused_before_any_filesystem_call` | `increment-043-inc9q.md`; `state.json:1278` "23 killed; 1 survivor → dead code removed" | pass |
| A-126 | final-resolve backstop; colon reason (Y1) | `test_inc9r.py::test_inc9r_cr_f1_pin_ordinary_and_missing_tail_paths_still_work` | `increment-044-inc9r.md`; `state.json:1254` "16/16" | pass |
| A-127 | lone surrogate in a typed path refused | `test_inc9s.py::test_inc9s_sec_f3_a_lone_surrogate_is_refused_by_the_allow_list_with_no_filesystem_call` | `increment-045-inc9s.md` | pass |
| A-128 | attachment chip opens with real keys/click | `test_inc9x3.py::test_inc9x3_a_key_on_a_file_chip_opens_the_resolved_inside_path` (+ 3) | `increment-046-x3.md`; `state.json:1230` "7/7" | pass |
| A-129 | English in osopen/github/factory/editor | `test_en1.py::test_no_spanish_user_facing_string` (+ scanner self-check) | `increment-047-en1.md` | pass |
| A-130 | English in coverage/components/inspector/rail (+ Z2) | `test_en2.py::test_z2_a_focused_chip_says_open_attachment_...` | `increment-048-en2.md` | pass |
| A-131 | English in lane/layered/outline/radial (acta→record) | `test_en3.py::test_no_spanish_user_facing_string` (+ lane arm) | `increment-049-en3.md` | pass |
| A-132 | English in store/legend/components; Z1 non-toggle | `test_en4.py::test_z1_opening_an_attachment_chip_twice_with_real_keys_leaves_selected_false` | `increment-050-en4.md` | pass |
| A-133 | English in app.py; closes two carries | `test_en5.py::test_home_metrics_hero_and_microbar_read_in_english` | `increment-051-en5.md` | pass |
| A-134 | palette footer advertises arrows (N2) | `test_en6.py::test_the_footer_reads_move_run_close_in_that_order_and_fits` | `increment-052-en6.md` | pass |
| A-135 | `?` is a character in every text field (B-72) | `test_en7.py::test_no_screen_binds_the_question_mark_at_priority` (+ 2) | `increment-053-en7.md` | pass |
| A-136 | operator wording rulings E1–E3 | `test_en8.py::test_e1_the_pan_edge_notice_reads_edge_of_the_map` (+ E2/E3 arms) | `increment-054-en8.md` | pass |
| A-137 | `?` not listed where the only control is a field (E4) | `test_en9.py::test_bindings_for_a_text_only_scope_offers_only_keys_that_work` (+ 2) | `increment-055-en9.md` | pass |
| A-138 | FLAKE-1/FLAKE-4 test races fixed; carry cleanup | `test_app.py::test_llr_cnv_3_1_the_parent_walk_maps_a_nested_widget_to_its_region` (FLAKE-1), `test_inc9c.py::test_inc9c_ux_f3_components_scroll_and_every_tab_stop_is_on_screen` (FLAKE-4) | `increment-056-gate1.md`; `state.json:1178` "3 x 2769/0" | pass |
| A-139 | pre-merge fixes PR-QA-F1/F3/F4/F5, BRANCH-SEC-F3 | `test_gate2.py::test_gate2_f1_no_other_call_site_uses_a_widget_method_that_does_not_exist` (+ 3) | `increment-057-gate2.md`; `state.json:1181` "Gate-2 fixes + review PASS, 2797/0" | pass |

### Layer B — behavioral (black-box) acceptance

> Driven through the SHIPPED surface, not the service API. The whole-branch adversarial PR QA
> (`VERDICT-merge-2026-10-03.md`) is the acceptance pass; per-increment UX reviews supply the
> boundary/negative evidence. Who executed each is named.

| Amendment / story | Acceptance observed | Surface driven | Deliverable observed (path / element) | repr · boundary · negative | Result |
|----|-----------------|----------------|---------------------------------------|---------------------------|--------|
| A-128 attachment chip opens | real `tab`→`enter`/`space`, real click | Textual pilot (`App.run_test`, `pilot.press`) at 87/118 | `open_external` handed the resolved inside path (recording stub) | repr inside path · boundary 87 cols (`I` first) · negative refused-outside toasts V1 and never launches | pass |
| A-135 `?` types in fields | real `?` press in connect-repo + inspector + search | pilot | `?` character appended; no select-all overwrite | repr every field · boundary 87/118 · negative priority-binding removed | pass |
| A-137 `?` not listed on connect-repo | keybar/legend omit `?` where a field is the only control | `bindings_for`/`groups_for_keybar` read from the seat | `?` absent from connect-repo listing, present on components | repr components · boundary TEXT_ONLY_SCOPES · negative relabelled `?` row still listed on map/home | pass |
| A-108/A-109 legend dock + pan | dock/modal switch and pan reveal | pilot at 87/118/140 | docked 44-col panel; card revealed whole, margin asserted on the composited frame | repr 118/140 · boundary 87 switch · negative modal layout does not widen the range | pass |
| A-139 PR-QA-F1 `j`/`k` home | `j`/`k` on home with ≥1 map does not crash | pilot | `DataTable` action cursor moves | repr with 1 map · boundary 0 maps · negative `action_cursor_down`/`up` (not the dead `cursor_*`) | pass |
| A-139 PR-QA-F5 CSV id | generated CSV id is `row-N` | CSV import through the handler | `row-N` (was `fila-N`) | repr N · boundary root row · negative `? ` orphan prefix unchanged (B-93) | pass |

Executed by: the **orchestrator** (gate run), the whole-branch **adversarial PR QA** reviewer, and the per-increment **ux-reviewer** agent (`state.json` `p3_progress` review verdicts). No row is a `demo`; each is a driven `test (driver)` / e2e.

### Bidirectional surface-reachability matrix (extends A-5)

| Direction | Amendment dimension / deliverable | Service param / producer | Reached/observed at surface? | TC / AT | Status |
|-----------|----------------------------------|--------------------------|------------------------------|---------|--------|
| input | typed repo URL/text | `github._classify` / `_is_url` | yes | `test_inc9k.py::test_inc9k_s1_...` | ✓ |
| input | typed local path | `osopen.safe_local_path` / `confine_reason` | yes | `test_inc9m.py::test_inc9m_s1_...` | ✓ |
| input | map id (construct / CSV save-as) | `store.check_map_id` / `create` | yes | `test_seed_safety.py::test_seed_store_create_refuses_an_existing_id` | ✓ |
| input | `?` keypress in text fields | `keymap.TEXT_ONLY_SCOPES` / `screen_bindings` | yes | `test_en7.py::test_no_screen_binds_the_question_mark_at_priority` | ✓ |
| output | attachment launch (deliverable: opened file) | `open_external` | yes | `test_inc9x3.py::test_inc9x3_a_key_on_a_file_chip_opens_the_resolved_inside_path` | ✓ |
| output | English copy painted/notified | census over `mapper/` literals | yes | `test_en1.py::test_no_spanish_user_facing_string` … `test_en9.py` | ✓ |
| output | map save on-disk pair (`.mmd` + sidecar) | `store.save` guarded via `_save_or_toast` | yes | `test_g6_store_surrogates.py::test_g6c_f3_census_every_store_save_call_is_guarded` | ✓ |
| output | CSV import id `row-N` | factory generate | yes | `test_gate2.py::test_gate2_f5_a_csv_row_with_no_id_and_no_title_gets_an_english_id` | ✓ |

### Signed-balance test ledger

> `post = base − D + A`. State counts in collected / passed-lean / passed-full form. The batch did
> not record D and A as a single pair; the per-increment lanes are the honest ledger.

| base | − D | + A | = post | actual collected | passed-lean / full | reconciles? |
|------|-----|-----|--------|------------------|--------------------|-------------|
| 429 (batch baseline, `PLAN.md:405`) | not recorded | not recorded | 2797 passed (+3 xfailed, 24 deselected) | not recorded | not recorded / 2797 passed | not closed — collected not recorded; baseline 429 counts deselected nodes (`--collect-only -o addopts=`), so the units differ; D/A not recorded as one pair |

Notes: the Inc-9 → EN → Gate sub-line ran **1558 → 2797** (`state.json:1069` Inc-9e close → `gate-run-master-tree.txt`), a delta of +1239 collected nodes; the batch's first clean full lane was 1170 (`state.json:665`). The gate run's own command and count are recorded verbatim in `gate-run-master-tree.txt`.

### Gaps detected

| ID | Requirement | Gap | Severity | Proposed action |
|----|-------------|-----|----------|-----------------|
| FLAKE-2 | `HLR-N16.4` own-keys declaration | `test_help_scope.py::test_hlr_n16_4_legend_declares_its_own_keys` fails once under load (`left` worked but not painted), 10/10 alone | minor | already carried (`state.json:1184-1186`); re-run solo on flake |
| B-36 | inspector blur commit | one keystroke durably overwrites a map + sidecar, no confirmation | deferred (design) | operator-deferred; first item of the next design batch (`BACKLOG.md:159`) |
| B-79 | Inc-9 line residuals | `INC9R-SEC-F1/F2`, `INC9P-SEC-F2` (TOCTOU narrowed not closed, hard links not detected on attachment parents) | low | next hardening pass |
| B-80 | toast layout | fixed ~60-col toast leaves one-word orphans at 118/140 | low | next design batch, prototype round first |
| B-81 | Inc-9 record accuracy | `increment-044-inc9r.md` records overstate / name intended killers not first `-x` failure | minor | Inc-9s or a later cleanup |
| B-82 | coverage/editor modals | no legend route (`UNMIGRATED_SCREENS`) | low | later design batch |
| B-83 | 87-col `M` focuses hidden field | inspector 0x0 region takes keys | low | design batch (with B-86) |
| B-84 | store/exporter write-through hard link | `_write_tmp` and `export.save_svg` | low | security hardening |
| B-85 | lane renderers paint raw control chars | latent, unreachable today | low | hardening |
| B-86 | coverage `↵` focuses the hidden field (second route of B-83) | typed text persists in an invisible field (`PR-QA-F6`) | low | design batch (with B-83) |
| B-87 | focus parks on hidden rail after modal close | keys go to invisible region at 87 | low | design batch |
| B-88 | connect-repo selection marker on two rows; `1 releases` | polish | low | small polish |
| B-89 | prompt placeholder reads like a default | empty `↵` closes silently | low | design batch |
| B-90 | palette lists `legend ?` on connect-repo | `?` types there | low | with B-82 |
| B-91 | connect-repo chrome + `press ↵ ↵` hint + github badge | polish | low | design batch |
| B-92 | dead `c`/`r` on empty home | advertised but inert | low | design batch |
| B-93 | CSV root row painted `? Root` | orphan prefix on root | low | small |
| B-94 | mirror fetch config not pinned (`remote.<n>.uploadpack`, `core.sshCommand`) | cache tampering | low | with B-96/B-97 |
| B-95 | `I`-toggle stale `edge of the map` hint | `GATE2-REV-F1` MEDIUM | major (backlog, merge-first) | next batch |
| B-96 | repo-config parsing hardening (`column.ui`, `i18n.logOutputEncoding`) | `GATE2-REV-F2` LOW | low | with B-94 |
| B-97 | tampered-cache hook + small carries | `GATE2-REV-F3/F4` LOW | low | next hardening pass |
| INC9G-R8 | Inc-9g mutant R8 survives (reviewer) though the record claims 34/34 killed | an A-115 branch has no killing witness | low | next batch: add the witness arm and correct `increment-033-inc9g.md` |

### Escaped-bug regression (if a defect escaped the suite)

| Regression id | Pre-fix run (evidence it FAILED) | Pre-fix RED kind (value / shape) | Post-fix value-discriminating? (QC-2) | Post-fix result | Reconciled node |
|---------------|----------------------------------|----------------------------------|----------------------------------------|-----------------|-----------------|
| `test_a105_a_zero_activity_workspace_paints_every_bar_at_the_floor` | `ZeroDivisionError` at `app.py:579` on a 14-day-idle workspace (`INC7-CR-R3-F3`, HIGH) | value (division by `max_count == 0`) | yes — the two-day arm `test_a105_two_days_of_activity_scale_relative_to_each_other` discriminates true-max vs sum vs binary tier | pass | `test_sparkline_floor.py::test_a105_*` |
| `test_inc9s_sec_f3_a_lone_surrogate_is_refused_by_the_allow_list_with_no_filesystem_call` | regression of `929a039`: `UnicodeEncodeError` escaped the walk's `except` | shape (exception out of a narrow `except`) | yes — `surrogatepass` second guard + astral pin `..._an_astral_character_counts_as_two_units_and_is_accepted` | pass | `test_inc9s.py::test_inc9s_sec_f3_*` |
| `test_g6c_f7_crlf_notes_round_trip_as_lf_with_no_replacement_char` | `plain()` mapped `\r`→U+FFFD at the LOAD boundary, corrupting CRLF notes silently (self-introduced) | value (permanent corruption) | yes — `test_g6c_f7_tab_cjk_emoji_round_trip_byte_identical` pins byte-identity | pass | `test_g6_store_surrogates.py::test_g6c_f7_*` |

### Evidence checklist — qa-reviewer (full)

> Evaluated by the `qa-reviewer` agent (Sonnet, read-only) from this artifact, the gate transcripts and a re-grep of `state.json`, `tests/` and `mapper/`. The one gate run was executed by the orchestrator; per-increment mutant counts and UX verdicts were executed by the reviewer agents recorded in `state.json`; the draft was written by `deepseek-v4-pro`.

| # | Item | ✓/✗ | Evidence / executor |
|---|---|---|---|
| 1 | One complete run, launched by the orchestrator — never stitched | ✓ | `gate-run-master-tree.txt`: 2797 passed, 24 deselected, 3 xfailed, 1486.29s; executor: orchestrator, tree `46e190b`. The earlier FLAKE-2 run (`gate-run-1-flake.txt`) is disclosed, not stitched |
| 2 | Layer 0 · Layer A · Layer B present | ✓ | Layer 0 tables, 35 Layer A rows, 6 Layer B rows; mutant counts from `state.json` (reviewer agents); Layer A citations corrected after the qa-reviewer pass (A-114, A-117…A-120, A-125 rows) |
| 3 | UX walkthrough with the real mechanism and the painted result | ✓ | Textual pilot in the suite (orchestrator's gate run) + per-increment `ux-reviewer` verdicts; adversarial PR QA drove the app for `VERDICT-merge-2026-10-03.md` |
| 4 | Representative + boundary + negative | ✓ | Layer B repr · boundary · negative column, 6 rows (drafter; checked by qa-reviewer) |
| 5 | The deliverable actually observed | ✓ | Bidirectional matrix output rows; test nodes exist on disk (spot-checked) |
| 6 | Bidirectional surface-reachability matrix | ✓ | 8 rows (4 input, 4 output); nodes exist |
| 7 | A negative result names its over-breadth, and that over-breadth is guarded (C-55 limb 1) | ✓ | `test_en1.py::test_scanner_sees_what_it_claims` exists (inspection) |
| 8 | Every probe that returned an absence carries its positive control (C-55 limb 2) | ✓ | `test_inc9n_f2_pin_a_name_that_only_looks_like_a_device_is_accepted`, `test_seed2_f5_ordinary_dollar_names_stay_valid` exist |
| 9 | Verdict `PASS` / `PASS-WITH-NOTES` / `FAIL` | ✓ | `PASS-WITH-NOTES`; notes: FLAKE-2, deferred residuals B-36 / B-79…B-97, INC9G-R8 |
| 10 | No unfilled template (no angle-bracket placeholder as a live value) | ✓ | remaining bracket text is quoted prose only (e.g. the B-94 git key name) |
| 11 | Ledger reconciles | ✗ | declared not closed: 2797 is the passed count, collected not recorded, baseline unit differs (429 includes deselected); D/A not recorded as a pair |
| 12 | No real PII / secrets | ✓ | no account name, profile path or credential in the artifact; the operator is referred to by role |

---

*Drafted by `deepseek/deepseek-v4-pro` (via `opencode run`) from existing evidence. Verified by the orchestrator (Claude Opus 5.5) and by a `qa-reviewer` agent; together they corrected the A-114, A-115, A-117…A-120 and A-125 mutation citations (an off-by-one shift along the Inc-9 chain), the missing B-86 row, a wrong symbol path (`_run_git`), the width citation, the ledger's collected/passed confusion, and the authorship attribution. The gate run was the orchestrator's. Where the record is silent the field says `not recorded`.*
