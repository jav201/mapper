# Traceability Matrix — mapper — Batch `2026-10-09-modular-batch`

> Phase 6 artifact (drafted by a Kimi `kimi-for-coding` unit; sources `01-requirements.md`, `01-requirements-ledger.md`, `04-validation.md`, `05-postmortem.md`, `03-increments/`, the shipped tree and `python -B -m pytest --collect-only -q -p no:cacheprovider` re-collection per selector). `T/` = `tests/`. Status `pass` = passed in the Phase-4 gate run at `69676cf` (3133 passed / 24 deselected / 3 xfailed / 0 failed, orchestrator, `evidence/p4-gate-full-suite.transcript`). Every selector below was re-collected at `c5905d6` for this matrix: **no selector collects 0** (counts in the `TC` column; `3/10` = 3 of the file's 10 nodes). LLR-MOD.7.1 is cited **as amended by LED-2026-10-09-modular-batch.12** (the two shipped edges: `NavigationModel` from `navigation.py`, and the `mapper.screens` package modal re-exports).

## 1. Master table — functional chain (white-box)

| US | HLR | LLR | TC (selector → real node ids, count) | File:line | Increment(s) | Result | Status |
|----|-----|-----|--------------------------------------|-----------|--------------|--------|--------|
| US-001 | HLR-MOD.1 | LLR-MOD.1.1 | `T/test_mod_structure.py -k spine_a` → `test_llr_mod_1_1_spine_a_screens_own_their_names`, `…_red_dropped_reexport_is_reported`, `…_red_screen_subclass_left_in_app_is_reported` (3/10) | `mapper/screens/common.py`, `prompt.py`, `construct.py`, `repo.py`, `plug_repo.py`, `import_preview.py`, `home.py`; `mapper/screens/map/navigation.py:23` (`NavigationModel`) | A1, A2, A3, A5a, A5b, A6, A7, A4 | pass | pass |
| US-001 | HLR-MOD.1 | LLR-MOD.1.2 | `T/test_mod_structure.py -k b0` → `test_llr_mod_1_2_b0_map_screen_lives_in_the_package_core`, `…_red_missing_core_reexport_is_reported`, `…_red_screen_subclass_left_in_app_is_reported` (3/10) | `mapper/screens/map/screen.py:54` (`class MapScreen`); `mapper/screens/map/__init__.py:12` (re-export only); `mapper/app.py` at 340 lines (`wc -l`) | B0 | pass | pass |
| US-001 | HLR-MOD.1 | LLR-MOD.1.3 | `T/test_mod_structure.py -k spine_b` → `test_llr_mod_1_3_spine_b_each_concern_lives_in_its_own_module`, `…_red_merged_mixins_are_reported`, `…_red_mixin_moved_into_core_is_reported` (3/10) | `mapper/screens/map/screen.py:41-51` (the 11 mixin imports), `:54` (`MapScreen(<11 mixins>, Screen)`); one concern module per `mapper/screens/map/*.py` | B1–B11 | pass | pass |
| US-002 | HLR-MOD.2 | LLR-MOD.2.1 | `T/test_mod_dispatch.py -k bindings` → `test_llr_mod_2_1_bindings_and_constants_live_only_on_the_core`, `…_red_mixin_declaring_bindings_or_on` (2/7) | `mapper/screens/map/screen.py:57` (`KEY_SCOPE`), `:58` (`BINDINGS = screen_bindings(SCOPE_MAP)`) — every class constant on the core only | B0 (F3) | pass | pass |
| US-002 | HLR-MOD.2 | LLR-MOD.2.2 | `T/test_mod_dispatch.py -k disjoint` → `test_llr_mod_2_2_method_names_disjoint_across_map_package` (1/7; plus `test_llr_mod_2_2_duplicate_handler_runs_twice`, the behavioural arm) | the 12 `mapper/screens/map/` modules — pairwise-disjoint method sets; `screens/**` binds patch names at module level, never imports them from `mapper.app` | B1, guard at every spine gate (R-5) | pass | pass |
| US-002 | HLR-MOD.2 | LLR-MOD.2.3 | `T/test_mod_dispatch.py -k pilot` → `test_at066_pilot_hints_dispatch_through_the_mixin` (1/7 — same node as AT-066's baseline) | `mapper/screens/map/hints.py:25` (`HintsOps`); dispatch through the mixin MRO | B1 (spike) | pass | pass |
| US-003 | HLR-MOD.3 | LLR-MOD.3.1 | `T/test_mod_compat.py -k reexport` → `test_llr_mod_3_1_reexports_static_tree`, `…_reexports_resolve[<name>]` ×21, `…_red_when_a_reexport_is_dropped` (25/32) | `mapper/app.py:11-40` (the permanent re-export block + `__all__`, after the `d4948b2` repair) | A1, A2, A3, A5a, A5b, A6, A7, A4, B0 | pass | pass |
| US-003 | HLR-MOD.3 | LLR-MOD.3.2 | `T/test_mod_compat.py -k patch_guard` → `test_llr_mod_3_2_patch_guard_every_site_targets_a_reading_module`, `…_red_when_the_target_stops_reading` (2/32); the bite checks ride in `T/test_search.py`, `T/test_inc9q.py`, `T/test_en8.py`, `T/test_app.py`, `T/test_inc9c.py`, `T/test_inc9n.py`, `T/test_inc9.py` | repointed module-globals: `searching.py:18-19` (`SearchIndex`, `MAX_RENDER_NODES`), `common.py:30` (`refusal_sentence`), `exporting.py:12` (`save_svg`), `panning.py:10` (`pan_extent`), `import_preview.py:26` (`LayeredRenderer`), `home.py:28` (`preview_csv`); `GitHubConnector.fetch` unpicked (class-attribute patch); guard map `T/test_mod_compat.py:54` (`PATCH_SURFACE`) | per increment: A1, A4, A7, B2, B9, B10 | pass | pass |
| US-002 | HLR-MOD.4 | LLR-MOD.4.1 | the gate run itself — `python -B -m pytest -q -p no:cacheprovider tests/` at each of the 9 increment gates and P4 | whole suite; 0 failed at every gate (P4: 3133 passed / 0 failed) | every increment, P4 | pass | pass |
| US-002 | HLR-MOD.4 | LLR-MOD.4.2 | `T/test_mod_parity.py -k parity` → `test_at065_parity_matches_golden[118]`, `[87]` (of 3; the third node is the mutant-copy RED arm) | goldens `evidence/mod_parity_118.txt`, `evidence/mod_parity_87.txt` (captured at `90e731b`, Inc-0, pre-move); runner `T/test_mod_parity.py:159` | Inc-0 (capture), all increments (re-drive) | pass | pass |
| US-002 | HLR-MOD.4 | LLR-MOD.4.3 | `T/test_mod_bodies.py` (4) → `test_llr_mod_4_3_bodies_match_baseline`, `…_no_undefined_globals`, 2 tmp-copy RED arms | baseline `evidence/mod-bodies-baseline.json` (per-method `ast.dump`); `T/test_mod_bodies.py:243` | all increments | pass | pass |
| US-003 | HLR-MOD.5 | LLR-MOD.5.1 | the six Inc-0 files: `T/test_draft_hygiene.py`, `T/test_darkside_census.py`, `T/test_keymap.py`, `T/test_en5.py`, `T/test_en7.py`, `T/test_app_imports_used.py` (no single selector — LLR nodes; the AT-069 node is `T/test_mod_compat.py -k at069`, 2/32, per LED .11) | pins located by content across `mapper/**/*.py`; `test_keymap.py` module set = `pkgutil.walk_packages(mapper)`; baseline `evidence/at069-baseline.json` | Inc-0 | pass | pass |
| US-003 | HLR-MOD.5 | LLR-MOD.5.2 | `T/test_arch_osopen_callers.py`, `T/test_inc9p.py`, `T/test_inc9q.py` (5+84+68 collected; run at the B3/B9 gates and P4) | `screens/map/opening.py:10` (`open_external` call site, moved at B3 — the allow-list gained it in the same increment, C9) | B3, B9 | pass | pass |
| US-003 | HLR-MOD.6 | LLR-MOD.6.1 | `T/test_mod_deps.py -k b02` → `test_llr_mod_6_1_b02_no_from_import_form_anywhere_under_screens`, `…_no_plain_or_aliased_import_form_anywhere`, `…_function_local_scope_is_detected`, +1 (4/13) | module-level imports now: `mapper/screens/factory.py:26-27` (`common`, `prompt`), `mapper/screens/settings.py:12` (`common`); 4 function-local imports deleted | A1, A2 | pass | pass |
| US-003 | HLR-MOD.6 | LLR-MOD.6.2 | `T/test_mod_deps.py -k no_app_import` → `test_llr_mod_6_2_no_app_import_map_package_at_any_scope`, `…_sibling_screens_never_import_map_screen_from_app` (2/13) | 0 occurrences of either import form referencing `mapper.app` under `mapper/screens/` (AST, any scope); `home.py:42`, `import_preview.py:24` import `MapScreen` from `mapper.screens.map` | B0, all increments | pass | pass |
| US-001 | HLR-MOD.7 | LLR-MOD.7.1 | `T/test_mod_deps.py -k arch` → `test_llr_mod_7_1_arch_concern_mixins_never_import_each_other`, `…_concern_helper_name_import_is_flagged`, `…_screens_init_does_not_import_sibling_screens`, `…_only_screen_py_imports_the_concern_modules`, `…_sibling_screens_import_map_names_from_the_map_package`, `…_nothing_imports_mapper_app_outside_entry_points` (6/13) | §3 rules over the shipped ASTs (as amended by LED .12): the `NavigationModel` value-class edge (`focus_mode.py:9`), the `mapper.screens` package-modal edges (`drafts.py:13`, `opening.py:11`, `searching.py:10`), `repo.py:31` (`NavigationModel` only) | B3, B12 (+ increment 023 narrowing per D-C2/D-C3) | pass | pass |
| US-001 | HLR-MOD.7 | LLR-MOD.7.2 | `T/test_mod_census.py` (3) → `test_llr_mod_7_2_census_matches_the_frozen_baseline`, 2 RED arms (`…_red_writer_drift`, `…_red_new_method`) | `T/test_mod_census.py:39` re-runs `spike/ast_census.py`, diffs vs `spike/census.json` (the F1/F2 freeze) | B12 | pass | pass |

## 1b. Behavioral chain (black-box)

| US | Acceptance test (`AT-NNN`) | Shipped surface | Observed outcome / deliverable | Status |
|----|----------------------------|-----------------|--------------------------------|--------|
| US-001 | AT-068 — `T/test_mod_structure.py -k at068` → `test_at068_one_feature_one_file` (1/10; companions AT-069/070/071, same story per DDR C3) | the repository tree itself | the 12 map modules + 7 sibling modules exist, each owning its names; `app.py` at the 340-line boundary | pass |
| US-002 | AT-065 — `T/test_mod_parity.py -k at065` → `test_at065_parity_matches_golden[118]`, `[87]`, `…_red_on_a_mutant_copy` (3/3); AT-066 — `T/test_mod_dispatch.py -k at066` → `test_at066_pilot_hints_dispatch_through_the_mixin`, `…_red_when_the_mixin_is_dropped` (2/7) | the painted screen of the real app, driven with real keys (`MapperApp(tmp_path)` + `run_test(size=…)` + `pilot.press(...)`) | every painted line of the scripted session byte-equal to the pre-move goldens at 118 and 87 columns; the hint line after real-key dispatch through the mixins | pass |
| US-003 | AT-067 — `T/test_mod_compat.py -k at067` → `test_at067_the_seven_targets_are_module_globals_of_their_reading_modules`, `…_patching_the_limit_through_the_reading_module_bites`, `…_github_connector_fetch_bites_through_the_shared_class_object` (3/32); AT-069 — `T/test_mod_compat.py -k at069` → `test_at069_baseline_counts_hold`, `…_red_when_a_baseline_pin_is_raised_above_the_current_counts` (2/32); AT-070 — `T/test_mod_deps.py -k at070` → `test_at070_b02_closed` (1/13); AT-071 — `T/test_mod_deps.py -k at071` → `test_at071_the_module_graph_allows_parallel_lanes` (1/13) | the shipped screens (search/count line, path-refusal toast) and the shipped source tree (suite's imports, patch sites, pins, module graph) | the patched refusal/limit bites through the repointed module-global, observed on screen; the 21 re-exported names resolve; the 14 single-home pins hold; B-02 closed (0 back-edges); the §3 module graph holds | pass |

## 2. Coverage summary

| Metric | Value |
|--------|-------|
| Total user stories | 3 |
| Covered user stories | 3 (100%) |
| Total HLR | 7 |
| Implemented HLR | 7 (100%) |
| Total LLR | 17 |
| Implemented LLR | 17 (100%) |
| Test cases (this batch's guard files, collected) | 72 (structure 10 + dispatch 7 + compat 32 + deps 13 + bodies 4 + census 3 + parity 3) |
| TC pass | 72/72 (inside the P4 gate: 3133 passed) |
| TC fail | 0 |
| TC pending | 5 network-marked tests not run (no network at the gates — declared non-run, not a pass; G-004) |

Suite ledger (04-validation.md:139): **2941 − 3 + 195 = 3133 passed**, +3 xfailed = 3136 collected of 3160 (24 deselected by `pyproject.toml:46`).

## 3. Detected gaps

| ID | Type | Description | Proposed action |
|----|------|-------------|-----------------|
| G-001 | LLR-MOD.7.2 | the census baseline lives in the batch folder (`spike/census.json`, read by `tests/test_mod_census.py:39`); archiving the folder breaks the guard | backlog B-108 — move the baseline under `tests/` before archiving |
| G-002 | LLR-MOD.7.1 | the D-C3 cycle guard (`screens_init_sibling_imports`, `tests/test_mod_deps.py:303`) sees only DIRECT importers of `mapper.screens.map` | backlog B-109 — widen to transitive scope |
| G-003 | HLR-MOD.3 / LLR-MOD.3.2 | CR-3: `screens/map/exporting.py:13` has its own unpatched `pan_extent` reader | backlog B-110 — add a patch site or document the single-reader contract |
| G-004 | LLR-MOD.4.1 | the 5-test network lane was not run | backlog — run `-m network` when network is available |
| G-005 | process | the A2–A4+B0 group-review LOW (leak-exception key granularity) has no backlog row of its own | backlog B-113 — next batch touching `tests/test_inc9q.py` |

## 4. Changes from previous batch

| Type | Item | Detail |
|------|------|--------|
| closed | B-02 (four cycle-dodging function-local imports of `mapper.app`) | A1/A2 moved them to module-level imports of `screens/common.py`/`screens/prompt.py`; AT-070 proves 0 back-edges remain |
| new | HLR-MOD.1–7, LLR-MOD.1.1–7.2, US-001–003 | this batch's contract (17 LLRs, all pass) |
| new | controls AT-065…AT-071 + the guard files `T/test_mod_structure/dispatch/compat/deps/census/bodies/parity.py` | 72 guard nodes, each with executed or structurally-guaranteed RED arms |
| amended | `docs/ARCHITECTURE.md` §2/§3/§4 | TARGET rows landed (A5b/A6/A7/A4/B0 rows written only when on disk, `20c0161`); F1–F5 freeze rows |
| deferred | B-108…B-113 | carried findings + P5 process items — see the post-mortem's deferred table |

## 5. Quick bidirectional mapping

### 5.1 By user story
- **US-001** (one feature, one file) → HLR-MOD.1, HLR-MOD.7 → LLR-MOD.1.1, 1.2, 1.3, 7.1, 7.2 → TC: `-k spine_a`/`b0`/`spine_b` (9), `-k arch` (6), `test_mod_census.py` (3); AT-068 (+ companions AT-069/070/071).
- **US-002** (the app does not change) → HLR-MOD.2, HLR-MOD.4 → LLR-MOD.2.1, 2.2, 2.3, 4.1, 4.2, 4.3 → TC: `-k bindings` (2), `-k disjoint`/`pilot` (2), the 9 increment gates, `-k parity` (3), `test_mod_bodies.py` (4); AT-065, AT-066.
- **US-003** (the suite sees nothing) → HLR-MOD.3, HLR-MOD.5, HLR-MOD.6 → LLR-MOD.3.1, 3.2, 5.1, 5.2, 6.1, 6.2 → TC: `-k reexport` (25), `-k patch_guard` (2), the six Inc-0 files, `test_arch_osopen_callers/inc9p/inc9q`, `-k b02` (4), `-k no_app_import` (2); AT-067, AT-069, AT-070.

### 5.2 By code file (each new module → the LLR that owns it)
- `mapper/screens/common.py` → LLR-MOD.1.1 (A1) · `mapper/screens/prompt.py` → LLR-MOD.1.1 (A2) · `mapper/screens/construct.py` → LLR-MOD.1.1 (A3) · `mapper/screens/map/navigation.py` → LLR-MOD.1.1 (A5a) · `mapper/screens/repo.py` → LLR-MOD.1.1 (A5b) · `mapper/screens/plug_repo.py` → LLR-MOD.1.1 (A6) · `mapper/screens/import_preview.py` → LLR-MOD.1.1 + LLR-MOD.3.2 (A7) · `mapper/screens/home.py` → LLR-MOD.1.1 + LLR-MOD.3.2 (A4) · `mapper/screens/map/screen.py` + `map/__init__.py` → LLR-MOD.1.2 (B0), LLR-MOD.2.1 (F3) · `mapper/screens/map/hints.py` → LLR-MOD.1.3/2.3 (B1) · `exporting.py` → LLR-MOD.1.3/3.2 (B2) · `opening.py` → LLR-MOD.1.3/5.2/7.1 (B3) · `undo.py` → LLR-MOD.1.3 (B4) · `focus_mode.py` → LLR-MOD.1.3 (B5) · `editing.py` → LLR-MOD.1.3 (B6) · `drafts.py` → LLR-MOD.1.3/5.2 (B7) · `navigation.py` (`NavOps`) → LLR-MOD.1.3 (B8) · `searching.py` → LLR-MOD.1.3/3.2/5.2 (B9) · `panning.py` → LLR-MOD.1.3/3.2 (B10) · `painting.py` → LLR-MOD.1.3 (B11) · `mapper/app.py` (reduced, `__all__`) → LLR-MOD.1.2/3.1 (B0/B12) · the 7 guard files `T/test_mod_*.py` → LLR-MOD.4.1 at every gate (B12, increment 023).

## 6. Batch sign-off

| Field | Value |
|-------|-------|
| Batch ID | `2026-10-09-modular-batch` |
| Closing date | 2026-10-10 |
| Total iterations (sum of phases) | 10 station passes, 2 iterations (P1 ×2, P2 ×2 — `state.json` `decisions_log`; post-mortem metrics table) |
| Validation passed | yes (PASS-WITH-NOTES; notes = 3 carried LOWs + 1 declared non-run, none blocking) |
| Synced to Obsidian | no record of a sync in the batch records |
