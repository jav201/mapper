# Validation — mapper — Batch 2026-10-11-fixes-batch

> **Artifact language:** English (`state.json` `language: en`).
> Phase 4 artifact. Content owner: `qa-reviewer` (Claude Sonnet), who evaluated the results of the Phase-1 validation strategy, named who executed each one and returned the rows; the orchestrator wrote this file. The ONE complete gate-suite run is the orchestrator's (`C-25`); the reviewer consumed its result and did not own it.

> **Owed in.** `core` ✓ · `full` ✓

## ✅ Verdict (read first)

> **Reserved field names.** `Result` · `Layer 0` · `Evidence checklist` · `⏸ DEFER` are read literally by the validator; the three verdict tokens are `PASS` · `PASS-WITH-NOTES` · `FAIL`.

- **Result:** `PASS-WITH-NOTES`
- **Layer 0:** 10 unit(s) met the criterion · 10 carry a named reddening mutation (21 mutants, M-FX1…M-FX17 plus 2b, 6b, 6c, 13b; each executed RED with its sha256 restore check, in the increment packets)
- **Requirements:** 23/23 pass (6 HLR + 17 LLR) · 0 blocker fails
- **Black-box acceptance (Layer B):** ✓ every story's `AT` observes its outcome through the shipped surface (boundary + negative): US-FX-001…006 → AT-084…089
- **Surface-reachability (bidirectional):** ✓ all named inputs AND outputs/deliverables reached/observed at the surface (matrix below); 0 gaps
- **Supersession inspection (read off the P3 packets):** ✓ all surviving refs negative — the pins that encoded the old behaviour (`slugify("---") == "n"`, the dump order, the A3 census 37) moved with the change; no live dependency on the old behaviour found
- **Test ledger:** ⚠ reconciles within one node — the packets add 55 nodes, the full-suite line is 56 above the previous batch's gate line (see ledger, `G-001`)
- **Evidence checklist (qa-reviewer):** `qa-reviewer (Claude Sonnet) · 9 of 9 rows ✓ with evidence`

**Full suite (orchestrator, clean shell, merged code `59a02d9`; later commits are records and docs only):**
`3432 passed, 24 deselected, 3 xfailed, 12 warnings in 2484.36s (0:41:24)` — 0 failed. The 24 deselected are the `slow` and `network` markers (`pyproject.toml:46` `addopts = "-m 'not slow and not network'"`); the 3 xfailed are pre-existing expected failures.

**Why PASS-WITH-NOTES and not PASS.** Every requirement passes and no blocker is open. The notes: (1) the blank roles window is evidenced `executed (injected delay)` only, never with a real slow git; (2) real-user evaluation `not performed — one-person team`; (3) the test ledger is off by one node against the previous gate line; (4) residual L1 (`B-133`) and the accepted F3b doubled start are carried, not fixed. None is a failing requirement, so not FAIL.

---

## Detail (reference)

### Layer 0 — unit

| Unit | Which criterion | Node id | Result |
|---|---|---|---|
| `slugify` (empty result) | LLR-FX.1.1 | `tests/test_mermaid.py::test_slugify_returns_empty_when_nothing_survives` | pass |
| CSV parent cell, blank-first; row-N id | LLR-FX.1.2 / 1.3 | `tests/test_fixes_csv_import.py::test_blank_parent_cell_is_a_root_candidate_not_a_reference_to_n`, `::test_id_with_no_slug_characters_becomes_row_n` | pass |
| CSV root by parentage | LLR-FX.2.1 | `tests/test_fixes_csv_import.py -k root` | pass |
| Orphan attach, no cycle | LLR-FX.2.2 | `tests/test_fixes_csv_import.py -k "permutation or cycle"` (24 of 24 permutations) | pass |
| `dump` root hoist | LLR-FX.3.1 / 3.2 | `tests/test_fixes_forest_root.py`, `tests/test_perf_dump.py::test_dump_fixture_goldens` | pass |
| Roles worker + catch set | LLR-FX.4.1 | `tests/test_fixes_roles_thread.py::test_roles_discovery_failure_degrades_to_no_repo` (8 arms) | pass |
| Hand-back guard (generation, `is_attached`) | LLR-FX.4.1 / 4.2 | `::test_roles_popped_screen_discards_late_discovery`, `::test_roles_latest_discovery_wins` | pass |
| Key bar and inert keys while loading; keypress reload | LLR-FX.4.3 / 4.4 | `::test_roles_keys_before_first_load_are_inert`, `::test_roles_keypress_reload_runs_no_git` | pass |
| `exporting.pan_extent` spy | LLR-FX.5.1 | `tests/test_export_state.py::test_exporting_reads_pan_extent_through_its_own_module_global` | pass |
| Leak registry key | LLR-FX.6.1 | `tests/test_inc9c.py -k "sec_f1 or at_089"` | pass |

**Measured by mutation, never by line coverage.** Mutant text and the restore hash are in the packets; the transcripts are under `evidence/`.

| Unit | Mutation applied | RED observed? | Transcript |
|---|---|---|---|
| `slugify` | M-FX1 (`or "n"` back) | yes — killed by `test_slugify_returns_empty_…`, AT-084 | `evidence/inc001-red.transcript` |
| parent cell | M-FX2, M-FX2b (slug-based has-parent test) | yes | `evidence/inc001-red.transcript` |
| row-N fallback | M-FX3 | yes — `test_id_with_no_slug_characters_becomes_row_n` | `evidence/inc001-red.transcript` |
| root choice | M-FX4 (first row root), M-FX5 (parked row root) | yes — AT-085, permutation node | `evidence/inc001-red.transcript` |
| `dump` hoist | M-FX6, 6b, 6c, 7, 12 (third edge walk) | yes — AT-086, byte goldens, `test_dump_counted_ops_scaling_ratio` | `evidence/inc002-red.transcript` |
| roles worker | M-FX8 (sync discovery), M-FX9 (no inert guard), M-FX10 (reload re-runs git), M-FX14 (catch removed) | yes | `evidence/inc003-red.transcript` |
| hand-back | M-FX11 (no generation), M-FX13, M-FX13b (no `is_attached`), M-FX17 (full key bar) | yes | `evidence/inc003-red.transcript`, `evidence/inc003-review-green.transcript` |
| export spy | M-FX15 (`layered.pan_extent`) | yes — spy count 0 | `evidence/inc004-red.transcript` |
| leak registry | M-FX16 (`(file, expr)` key) | yes — second site absorbed | `evidence/inc004-red.transcript` |

### UX walkthrough — trigger family D fired (the import preview and the roles screen change what the operator sees)

Driven by the `qa-reviewer` (Claude Sonnet), headless, at 118×34 (the reference width), through the real app.

| Criterion (when the user does X, they observe Y) | Driven with the REAL mechanism | Painted result asserted | Verdict |
|---|---|---|---|
| Import a CSV with a blank-root row and a `!!!` row: the preview header reads "3 nodes"; root `Alpha` has no `? `; `? Beta` and `? Bang` are parked under it; no node `n` | `i`, path, `enter` in `MapperApp` | painted `#import-preview-canvas` text | ✓ |
| Import a child-first CSV: `Root` is painted above `Child`; the cycle sentence does not appear | same keys | painted frame | ✓ |
| Import a CSV whose parent cell is punctuation only: `R` is the root; `? K` is parked | same keys | painted frame | ✓ |
| Press `R` for the roles screen: it is pushed at once, the four surfaces are empty, the main thread is not blocked; then the repo-less workspace paints "chain no repo" and "no repo — connect a repository…" | `R` from home, `pilot.press`, a gated `identity._run_git` | the four painted Statics, before and after release | ✓ |

**Mechanism used:** a UI test driver (Textual `run_test(size=(118,34))` + `pilot.press`).

| Act | What it is | Performed? |
|---|---|---|
| Automated walkthrough | the criteria above, driven through the REAL mechanism | performed |
| Expert inspection | a cognitive walkthrough against declared criteria, by a reviewer and not a user | performed — the PDR `ux-reviewer` (Claude Sonnet) review, `design/PDR-2026-10-11-fixes-batch.md` |
| Evaluation with users | real users of the system, doing the tasks named in the context of use | not performed — one-person team |

- **Method:** headless drive of the shipped screens by the reviewer; the roles-screen blank window is produced by gating `identity._run_git` (an injected delay), not by a genuinely slow git.
- **Participants or population:** none (no user evaluation).
- **Evidence of the evaluation:** AT-084, AT-085, AT-087 (painted-frame assertions) and `evidence/inc003-review-green.transcript`.
- **Limits:** the blank roles window is evidenced `executed (injected delay)` only; no real slow git was run. The visible loading cue is deliberately absent (operator ruling R4) and is `B-128`. Nothing here establishes that a real operator finds the blank window acceptable.

### Layer A — functional (white-box): per-requirement results

| Req | Method | Executed verification | Numeric threshold | Result | Evidence |
|-----|--------|-----------------------|-------------------|--------|----------|
| HLR-FX.1 | test | `tests/test_fixes_csv_import.py tests/test_mermaid.py` | 0 failed; ids `{alpha, beta, row-1}`, 0 nodes `n` | pass | full suite 0 failed; M-FX1, 2, 2b |
| LLR-FX.1.1 | test | `tests/test_mermaid.py::test_slugify_returns_empty_when_nothing_survives` | `slugify("---") == ""` | pass | M-FX1 |
| LLR-FX.1.2 | test | `…::test_blank_parent_cell_is_a_root_candidate_…`, `…::test_punctuation_only_parent_cell_parks_the_row` | 3 of 3 arms | pass | M-FX2, 2b |
| LLR-FX.1.3 | test | `…::test_id_with_no_slug_characters_becomes_row_n` | `!!!` → `row-1` | pass | M-FX3 |
| HLR-FX.2 | test | `tests/test_fixes_csv_import.py tests/test_csv_safety_preview.py tests/test_import_csv.py` | `root_id == "root"`, no cycle | pass | M-FX4, 5 |
| LLR-FX.2.1 | test | `tests/test_fixes_csv_import.py -k root` | truth table | pass | M-FX4, 5 |
| LLR-FX.2.2 | test | `-k "permutation or cycle"` plus the two preview sentences | 24 of 24 permutations equal | pass | M-FX4 |
| HLR-FX.3 | test | `tests/test_fixes_forest_root.py tests/test_csv_safety_store.py tests/test_perf_dump.py` | 8 of 8 roots; goldens byte-identical; visits ≤ 2E + 4 | pass | M-FX6, 7, 12 |
| LLR-FX.3.1 | test | `tests/test_fixes_forest_root.py tests/test_perf_dump.py` | B-117 bytes `graph TD\n    a\n    b --> c\n` | pass | M-FX6, 6b, 6c, 7 |
| LLR-FX.3.2 | test + inspection | `tests/test_csv_safety_store.py::test_save_accepts_legacy_forest_after_edit`, `tests/test_perf_dump.py::test_dump_fixture_goldens`; `grep -c "root drifts" mapper/store.py` | 0 lines asserting drift | pass | `git diff 81fba65..HEAD --stat -- tests/goldens` prints nothing |
| HLR-FX.4 | test | `tests/test_fixes_roles_thread.py tests/test_roles_screen.py` | 3 of 3 git calls off the main thread; 0 paints on a popped screen | pass | M-FX8…14, 17 |
| LLR-FX.4.1 | test | `…::test_at_087_…`, `…::test_roles_discovery_failure_degrades_to_no_repo`, `…::test_roles_popped_screen_discards_late_discovery` | worker thread; narrow catch; discard after pop | pass | M-FX8, 13, 13b, 14 |
| LLR-FX.4.2 | test | `…::test_roles_paints_nothing_until_discovery_returns`, `…::test_roles_latest_discovery_wins` | 4 of 4 surfaces empty; latest wins | pass | M-FX11 |
| LLR-FX.4.3 | test | `…::test_roles_keys_before_first_load_are_inert` | 0 bytes written; key bar reduced | pass | M-FX9, 17 |
| LLR-FX.4.4 | test | `…::test_roles_keypress_reload_runs_no_git`, `tests/test_roles_screen.py` | git count 3 → 3; 22 nodes pass | pass | M-FX10 |
| HLR-FX.5 | test | `tests/test_export_state.py::test_exporting_reads_pan_extent_through_its_own_module_global` | spy ≥ 1 call, `m.svg` exists | pass | M-FX15 |
| LLR-FX.5.1 | test | same node | spy count 0 under M-FX15 | pass | M-FX15 |
| HLR-FX.6 | test | `tests/test_inc9c.py -k "sec_f1 or at_089"` | 14 passed; second record reported | pass | M-FX16 |
| LLR-FX.6.1 | test | same selection | `undeclared == [("mapper/screens/home.py", 412, "str(exc)")]` | pass | M-FX16 |

All rows are consumed from the merged-tree full-suite run above (0 failed), not re-run by this record.

### Layer B — behavioral (black-box) acceptance

| US | Acceptance test (`AT-NNN`) | Surface driven | Deliverable observed (path / element) | repr · boundary · negative | Result |
|----|----------------------------|----------------|---------------------------------------|----------------------------|--------|
| US-FX-001 | AT-084 `tests/test_fixes_csv_import.py::test_at_084_empty_parent_cells_are_roots_not_node_n` | `i` import in the real app | painted `#import-preview-canvas`: no node `n`, root without `? `, `row-1` | ✓ · ✓ blank, whitespace, punctuation-only · ✓ M-FX1/2 | pass |
| US-FX-002 | AT-085 `…::test_at_085_child_listed_before_root_imports_saves_and_reopens` | `i`, preview, `s`, `MapStore.load` | reopened two-node tree rooted at `root`; no cycle sentence | ✓ · ✓ child first, grandchild first · ✓ ring of three | pass |
| US-FX-003 | AT-086 `tests/test_fixes_forest_root.py::test_at_086_forest_root_survives_save_and_reload` | `MapStore.save` then `load` | saved `.mmd` names the root first; same root on reload | ✓ · ✓ orphan root, edge-parent root · ✓ dangling edge | pass |
| US-FX-004 | AT-087 `tests/test_fixes_roles_thread.py::test_at_087_roles_screen_git_reads_run_off_the_ui_thread` | `R` from home | four painted Statics; 3 of 3 git calls off the main thread | ✓ · ✓ keys before first load · ✓ discovery raises → `no repo` | pass |
| US-FX-005 | AT-088 `tests/test_export_state.py::test_exporting_reads_pan_extent_through_its_own_module_global` | the `e` key | `m.svg` on disk, spy count ≥ 1 | ✓ · ✓ · ✓ M-FX15 count 0 | pass |
| US-FX-006 | AT-089 `tests/test_inc9c.py::test_at_089_a_second_leak_site_in_an_excused_file_is_still_flagged` | the leak census | second `str(exc)` record listed undeclared | ✓ · ✓ · ✓ M-FX16 | pass |

### Bidirectional surface-reachability matrix

| Direction | US dimension / deliverable | Service param / producer | Reached/observed at surface? | TC / AT | Status |
|-----------|---------------------------|--------------------------|------------------------------|---------|--------|
| input | blank / whitespace / punctuation parent cell | `import_csv` parent read | yes — `i` key | AT-084 | ✓ |
| input | row order of the CSV | root selection | yes — `i` key, 24 permutations | AT-085, LLR-FX.2.2 | ✓ |
| input | root of a forest graph | `dump` | yes — `MapStore.save` | AT-086 | ✓ |
| input | `R` key, keys during loading | `RolesScreen` | yes — `pilot.press` | AT-087, LLR-FX.4.3 | ✓ |
| output | import preview text, saved `.mmd` | `preview_csv`, `dump` | yes — painted frame, file on disk | AT-084/085/086 | ✓ |
| output | roles screen four Statics | `_apply_facts` | yes — painted text | AT-087 | ✓ |
| output | `m.svg` | `exporting.py` | yes — file on disk | AT-088 | ✓ |

### Signed-balance test ledger

| base | − D | + A | = post | actual collected | passed-lean / full | reconciles? |
|------|-----|-----|--------|------------------|--------------------|-------------|
| 3376 passed (previous batch's gate line, `2026-10-11-reqharness-batch`) | 0 | 55 (001: 16, 002: 20, 003: 17, 004: 2) | 3431 | 3459 (3432 passed + 24 deselected + 3 xfailed) | 3432 passed (default selection) | ⚠ no — off by one node |

The 1-node difference is not attributable from the artifacts: the base is the previous batch's gate line, not a collection at this batch's open commit, and no `--collect-only` was run at `81fba65`. Declared as `G-001`; not a failure.

### Gaps detected
| ID | Requirement | Gap | Severity | Proposed action |
|----|-------------|-----|----------|-----------------|
| G-001 | test ledger | one node between the packets' sum (55) and the gate-line difference (56) | minor | a `--collect-only` count at `81fba65` in the next batch's open; non-blocking |
| G-002 | HLR-FX.4 | blank roles window evidenced only with an injected delay; no visible cue | minor | `B-128` (prototype round before any cue) |
| G-003 | HLR-FX.4 | exit-time thread residual L1 | minor | `B-133` (bound ≈ 30 s) |

### Escaped-bug regression (if a defect escaped the suite)

Not applicable — the defects (B-115, B-116, B-117, B-127, B-110, B-113) were known before the batch; each regression node has its RED-on-base proof in `evidence/inc001-red.transcript` … `inc004-red.transcript`.

### Evidence checklist — qa-reviewer (full)

| # | Item | ✓/✗ | Evidence |
|---|------|-----|----------|
| 1 | Every HLR/LLR has a result row | ✓ | Layer A: 6 HLR, 17 LLR rows |
| 2 | Every US has a passing AT | ✓ | Layer B: AT-084…089 |
| 3 | Every AT is one on-disk node | ✓ | DDR row 4 |
| 4 | Each unit has a named reddening mutation, RED observed | ✓ | Layer 0 mutation table; 21 mutants |
| 5 | Full suite executed and 0 failed | ✓ | `3432 passed, 24 deselected, 3 xfailed … (0:41:24)` |
| 6 | Walkthrough driven through the real mechanism, painted text asserted | ✓ | UX table |
| 7 | Evidence honesty: blank window `executed (injected delay)` only; no real-user claim | ✓ | UX limits |
| 8 | Test ledger reconciled | ✓ | reconciled within a declared 1-node gap `G-001` (⚠, minor) |
| 9 | No secrets or personal paths in artifacts | ✓ | `tests/test_no_operator_paths.py` green in the full suite |

### G-001 resolved (orchestrator, 2026-10-15)

Measured with `pytest --collect-only -q` at the P3-open commit `81fba65` and at the merged head, both in a clean shell: **3379 → 3435 collected** (24 deselected both times), i.e. **3376 → 3432 passed** with 3 xfailed both times. `comm` of the two node lists: **+56, −0**. The 56th node is not in any packet because no increment wrote it: `tests/test_repair_map_truth.py::test_at_p04_every_owned_path_exists_on_disk[screens-mapper/screens/roles.py]` — a parametrised census over the paths `docs/ARCHITECTURE.md` declares, gaining one case when increment 003 added `mapper/screens/roles.py` to the `screens` row (PDR condition C3). Per file: `test_fixes_forest_root.py` +20, `test_fixes_roles_thread.py` +17, `test_fixes_csv_import.py` +15, `test_export_state.py` +1, `test_inc9c.py` +1, `test_mermaid.py` +1, `test_repair_map_truth.py` +1. The 3376 base is therefore measured, not assumed.
