# Design review record — DDR — mapper — Batch 2026-10-11-fixes-batch

> **Artifact language.** English (`state.json` `language: en`).

> **Owed in.** `core` by trigger (DDR active in this batch's `stations_active`) · `full` ✓
> **Source:** `/dev-flow-init` step 4's seed-by-level table, which is this fact's one home. `stations_active` in `state.json` is the authority for *this* batch.

> **Where this lives: the VAULT + Drive** once sealed (published by `/dev-flow-sync`); staged here under `design/` until then. It is **sealed** and **cited by id** from the repo. If this record changes after the seal it is a NEW version with a NEW id (`DDR-2026-10-11-fixes-batch-v2`), never a silent edit.

> **Notice convention.** `⚠` yellow = notice, declare the reason and continue · `✗` red = block · `✓` green = satisfied **with its evidence cited**. Without a citation an item is asserted, not satisfied.

| Field | Value |
|---|---|
| Record id | `DDR-2026-10-11-fixes-batch` |
| Reviews | the sealed `PDR-2026-10-11-fixes-batch` (`design/PDR-2026-10-11-fixes-batch.md`) plus its amendment E1 (§E, LED-2026-10-11-fixes-batch.18); the four increments on `feat/fixes-batch`, range `81fba65..59a02d9` |
| Participants | DDR: `architect` (Claude Opus) + `software-dev` + `qa-reviewer` (Claude Sonnet) |
| Date sealed | `2026-10-15` |
| **Verdict** | `approved with conditions — all conditions discharged` |

---

## A · PDR checklist — preliminary design review

*Not owed at this record.* The PDR is the sealed record `PDR-2026-10-11-fixes-batch`; this DDR reviews it and does not re-run it.

---

## B · DDR checklist — detailed design review · **and the JOIN point when the batch forked**

The batch did not fork (one lane, serial 001 to 004: `design/design-proposal.md` §8; `PLAN.md`). The join items below therefore read as the serial-integration checks: crossed census, one-node-per-AT, ledger, file-set overlap, budget, condition discharge.

Commits in range (`git log --oneline 81fba65..HEAD`): 001 `d412ed0`; 002 `2d57228` (merge `2fc6087`); 004 `a7b0f54`, `b4ce603` (merge `de3c6d0`); 003 `c7c975a` (merge `59a02d9`); orchestrator and review commits `e5a242b`, `f786d29`, `67bf64c`, `74d051a`, `da8b1d4`, `0f349a8`, `2e094fb`.

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | What changed against the PDR, **and why** | ⚠ | Six deltas, all declared and none a scope change. (a) **`is_attached` instead of `is_mounted`** (PDR C1, amendment E1): Textual 8.2.8 keeps `is_mounted` True after a pop, so the guard could never fire (`increment-003.md:90`, deviation 1); code `mapper/screens/roles.py:535-537`; documents amended in `0f349a8`; ledger `.18`. (b) **M-FX2 needed an extra arm and M-FX2b**: on the patched tree a slug-based has-parent test yields the same edges; the punctuation node gained the `k,K,!!!` then `r,R,` arm and M-FX2b reproduces the requirement's literal symptom (`increment-001.md:80-89`). (c) **Added mutants**: M-FX6b and M-FX6c in 002 (`increment-002.md:83-84`), M-FX13b in 003 (`increment-003.md:86`); 003 also needed a direct SUCCESS arm in the popped-screen node because the framework cancel alone left M-FX13 GREEN (deviation 2, `:92`). (d) **A3 census pin 37 to 39 over two steps**: 38 by the 001 helper `tests/test_fixes_csv_import.py:39` (found by 002, `increment-002.md:58`; fixed in `74d051a`, message in `da8b1d4`), 39 by the 003 helper `_painted` (`increment-003.md:34`, `c7c975a`); census still derives the set from the tracked tree. (e) **`_open_roles` bounded wait**: `asyncio.wait_for(..., timeout=60)` at `tests/test_roles_screen.py:239` (`2e094fb`, review L2). (f) **Exit-time thread residual L1 accepted**: the default executor's non-daemon thread can keep the process alive up to the git timeout (about 30 s) after quitting mid-discovery; the app exits in 0.67 s; bounded, no data loss (`increment-003.md:183`). Also: 001 pin move `slugify("---")` from `"n"` to `""` (`increment-001.md:33`); 002 pin `orphan-order` arm `root_id` (`increment-002.md:34`). **Housekeeping closed at the seal:** gate rows 6 and 15 and the `Independent review PENDING` line of packets 001, 002 and 003 now cite the §4b reviews (APPROVE-WITH-NITS each; 001 Claude Opus, 002 and 003 DeepSeek); `grep -n 'Independent review PENDING' 03-increments/*.md` prints nothing. |
| 2 | Frozen interfaces still intact — or the work returned to the trunk and it is declared | ⚠ | PDR §8 list (`design/design-proposal.md:167-169`): `parse`, `_check_round_trip` comparison set, `identity.py`, the four Static ids, key scope, all goldens. `git diff 81fba65..HEAD -- mapper/reqharness` is empty (0 lines, so `identity.py` untouched); changed source is exactly `mapper/import_csv.py`, `mapper/mermaid.py`, `mapper/store.py` (docstring only), `mapper/screens/roles.py`; `RolesScreen()` and the Static ids unchanged (`increment-003.md:154-155, 217`); `preview_csv`, `CsvRow`, `csv_collisions` unchanged (`increment-001.md:208`); `parse` unchanged, visit bound `<= 2E + 4` passes (`increment-002.md:148`). **⚠ cost notice (architect, ruled):** the root hoist adds an O(E) short-circuit scan over `written_parents`, a separate list built beside the edge loops; it is **not** a third pass over `graph.edges`, so the 2E+4 budget as counted is kept and the visit-count node stays green. Documented contract moves (not breaches): `slugify` empty result and `dump` root-first, in `docs/ARCHITECTURE.md:101`. |
| 3 | **Reverse census CROSSED between lanes** (the one check impossible from inside a lane) | ⚠ | Per-increment B-census hits: **001** `increment-001.md:143-147` (slugify: `test_csv_safety_store`, `test_mermaid`, new file; preview_csv: `test_csv_safety_preview`, `test_gate2`, `test_import_csv`, `test_inc9c`, `test_inc9n`, `test_mod_compat`, `test_repair_cycles`, `test_repair_fields`); **002** `increment-002.md:141` (dump: `perf_goldens_capture`, `test_csv_safety_store`, `test_fixes_csv_import`, `test_fixes_forest_root`, `test_inc9e`, `test_mermaid`, `test_mod_bodies`, `test_mod_compat`, `test_perf_dump`, `test_repair_cycles`, `test_search`); **003** `increment-003.md:151-155` (`test_roles_screen`, `test_app_imports_used`, `test_inc9`, `test_keymap`, new file); **004** has no source symbol (test-only). **Crossings:** 001's symbols are asserted by 002's tests and the reverse: `tests/test_mermaid.py` (001 pin and nodes) and `tests/test_csv_safety_store.py` (002 assertion) both run under both mermaid changes, and `tests/test_fixes_csv_import.py` (001) calls `MapStore.save` and so asserts 002's `dump`; all green in 002's run (326 + 128 passed) and in the merged tree's later runs. 003 and 004 symbols (`RolesScreen`, `exporting.pan_extent`, `LEAK_EXCEPTIONS`) are asserted by no other increment's tests. **⚠ one real cross-coupling, found and closed:** 001's `_render().plain` helper moved the A3 census (a file 001 never ran), surfaced by 002 and fixed in `74d051a`; 003 then moved it again. **Golden-drift census (B3): `git diff 81fba65..HEAD --stat -- tests/goldens` prints nothing (0 lines, exit 0): zero golden drift.** The merged-tree full-suite run is the gate for the rest: `3432 passed, 24 deselected, 3 xfailed, 12 warnings in 2484.36s (0:41:24)` (orchestrator, clean shell, merged code `59a02d9`; 0 failed; the 24 deselected are the `slow` and `network` markers, `pyproject.toml:46` `addopts = "-m 'not slow and not network'"`; later commits are records and docs only). |
| 4 | Every `AT-NNN` realises in **exactly one** on-disk node (C-18) | ✓ | Grep of `tests/*.py` for the node definitions, one `def` per AT: AT-084 `tests/test_fixes_csv_import.py:214` `test_at_084_empty_parent_cells_are_roots_not_node_n`; AT-085 `tests/test_fixes_csv_import.py:237` `test_at_085_child_listed_before_root_imports_saves_and_reopens`; AT-086 `tests/test_fixes_forest_root.py:42` `test_at_086_forest_root_survives_save_and_reload`; AT-087 `tests/test_fixes_roles_thread.py:117` `test_at_087_roles_screen_git_reads_run_off_the_ui_thread`; AT-088 `tests/test_export_state.py:621` `test_exporting_reads_pan_extent_through_its_own_module_global` (docstring `:622` names AT-088); AT-089 `tests/test_inc9c.py:323` `test_at_089_a_second_leak_site_in_an_excused_file_is_still_flagged`. Six ATs, six nodes, no AT with two definitions; `test_a3_census.py` and the module docstrings mention AT ids in comments only. |
| 5 | Test ledger **summed** across lanes, reconciled | ✓ | New nodes: 001 = 16 (15 + 1 in `test_mermaid.py`; `increment-001.md:167`), 002 = 20 (`increment-002.md:164`), 003 = 17 (`increment-003.md:175`), 004 = 2 (`increment-004.md:51`); **sum 55 added, 0 deleted**; existing nodes changed in count: 0 (pins moved, see row 1). Executed lines: 001 `1 failed, 589 passed` (the one failure, `PLAN.md:187` operator-path pattern, was absent from 003's run and fixed in `d412ed0`); 002 `326 passed` + `128 passed`; 003 `1731 passed, 4 deselected`; 004 `101 passed`. Per-increment runs overlap and are not additive; the reconciling number is the merged-tree full-suite run: `3432 passed, 24 deselected, 3 xfailed, 12 warnings in 2484.36s (0:41:24)` (orchestrator, clean shell, merged code `59a02d9`; 0 failed; the 24 deselected are the `slow` and `network` markers, `pyproject.toml:46` `addopts = "-m 'not slow and not network'"`; later commits are records and docs only). |
| 6 | No lane touched another lane's file | ✓ | `git show --stat` of `d412ed0`, `2d57228`, `a7b0f54`/`b4ce603`, `c7c975a`: 001 = `import_csv.py`, `mermaid.py`, `test_fixes_csv_import.py`, `test_mermaid.py` (+ packet, transcript, one `PLAN.md` line); 002 = `mermaid.py`, `store.py`, `test_fixes_forest_root.py`, `test_csv_safety_store.py`, `test_perf_dump.py`; 004 = `test_export_state.py`, `test_inc9c.py`; 003 = `roles.py`, `ARCHITECTURE.md`, `test_fixes_roles_thread.py`, `test_roles_screen.py`, `test_a3_census.py`. Overlaps: `mapper/mermaid.py` by 001 and 002, **declared** and serialised in PDR §8 (`design/design-proposal.md:167-169`); `tests/test_a3_census.py` by the orchestrator commits `74d051a`/`da8b1d4` (001's helper) and 003, serial. 004 shares no file with any other increment. |
| 7 | Source-file budget: any lane that reached or exceeded 4, reviewed here | ✓ | SOURCE files: 001 = 2 (`increment-001.md:37`), 002 = 2 (`increment-002.md:38`, `store.py` docstring only), 003 = 1 (`increment-003.md:38`), 004 = 0 (`increment-004.md:36`). None reached 4; batch total 4 distinct source files, equal to `git diff 81fba65..HEAD --stat -- mapper` (4 files). |
| 8 | **Every open PDR condition discharged one by one, by RE-READING the artifact** | ✓ | Table below: C1-C8 and E1, each read in the artifact that was to change. Full-suite confirmation of the code-side rows: `3432 passed, 24 deselected, 3 xfailed, 12 warnings in 2484.36s (0:41:24)` (orchestrator, clean shell, merged code `59a02d9`; 0 failed; the 24 deselected are the `slow` and `network` markers, `pyproject.toml:46` `addopts = "-m 'not slow and not network'"`; later commits are records and docs only). |
| 9 | **F3b — doubled discovery start** (ARQ finding; reviewer concern: two workers at push) | ✓ | **ACCEPTED with evidence.** At push both `on_mount` and `on_screen_resume` start a discovery: **6 git calls at open, the same count as the old synchronous code** (`design/arq-note.md:81`, measured before and after in the scratch copy). The generation guard makes the second win; `test_roles_latest_discovery_wins` and M-FX11 pin it (`increment-003.md:84`). No new cost, so not coalesced; recorded rather than specified away. |
| 10 | **L1 — exit-time thread residual** (DDR `#D2`) | ⚠ | **ACCEPTED, bound stated, backlog `B-133`.** After quitting mid-discovery the default executor's non-daemon thread can keep the process alive until its git calls time out: 3 git calls × the 10 s `_TIMEOUT` (`identity.py`) ≈ 30 s worst case; two parallel workers (F3b) run side by side, so the bound stays ≈ 30 s, not 60 s. The app itself exits in 0.67 s; no data loss; unreachable before B-127. Tracked in `.dev-flow/BACKLOG.md` as `B-133`. |

**A conditional verdict is not an authorisation.** Each condition below is discharged by reading the
artifact that was supposed to change — not by trusting that the corrective pass ran.

| # | Condition left open at PDR | Discharged? | The artifact line that proves it |
|---|---|---|---|
| C1 | Worker returns the facts; hand-back in `on_worker_state_changed` with generation and liveness check; no `call_from_thread` | ✓ | `mapper/screens/roles.py:519-520` (generation bump, worker start), `:528-537` (`on_worker_state_changed`, `gen != self._gen or not self.is_attached`); `grep call_from_thread mapper/screens/roles.py` returns no code line; M-FX11/13/13b KILLED (`increment-003.md:84-86`). Guard name amended by E1. |
| C2 | F2 corrected: no resave reorder; hoist only for in-session roots; cannot repair drifted maps | ✓ | `01-requirements.md:305` ("Disk effect" line); `increment-002.md:19` ("on resave the hoist does not fire"); `tests/test_fixes_forest_root.py` `test_root_already_elected_by_text_order_changes_nothing` (3 arms) in `increment-002.md:62`. |
| C3 | Increment 003 amends `docs/ARCHITECTURE.md` (`screens` row paths, ownership, exposes; `mermaid` row note) | ✓ | `docs/ARCHITECTURE.md:113` (`mapper/screens/roles.py` in paths; "`roles.py` owns `RolesScreen`"; `RolesScreen` in exposes) and `:101` (`mermaid` row, "amended `2026-10-11-fixes-batch`"); commit `c7c975a` stat. |
| C4 | Key-bar subtraction until first facts, painted-frame test and mutant | ✓ | `increment-003.md:19` (key bar omits the three edit rows), `:88` (M-FX17 KILLED by `test_roles_keys_before_first_load_are_inert`), `:123` (emitted-form assertion on `KeyBar.render().plain`). |
| C5 | AT-084/085/087 assert painted frame text, not `update()` args (C-32) | ✓ | `increment-001.md:64, 114` (painted `#import-preview-canvas`); `increment-003.md:63, 122` (painted four surfaces); test module docstrings `tests/test_fixes_csv_import.py:6` and `tests/test_fixes_roles_thread.py:3`; census comment `tests/test_a3_census.py:387-392`. |
| C6 | Walkthrough honesty: blank window `executed (injected delay)` only; no real-user claim; no extra signal | ✓ | `design/design-proposal.md:302` (evidence-honesty line) and §9.4 (`:292`); no loading chrome added (`increment-003.md:198`). |
| C7 | Threshold arm `,Alpha,` then `,,` gives `{alpha, row-1}` | ✓ | `tests/test_fixes_csv_import.py:111` (`id,title,parent\n,Alpha,\n,,\n`); `increment-001.md:63`; M-FX3 KILLED (`:85`). |
| C8 | One sentence naming the `row-N` collision surface in requirements §6.3 | ✓ | `01-requirements.md:467` (the `row-N` collision surface sentence, cross-ref LLR-FX.1.3, design §10, §9.1(d)). |
| E1 | Hand-back check reads `is_attached`, not `is_mounted` | ✓ | PDR §E row E1 (`design/PDR-2026-10-11-fixes-batch.md:89`); `01-requirements.md:321` and `:325` read `is_attached`; `design/arq-note.md:75, 79` and `design/design-proposal.md:48, 107, 320` read `is_attached`; code `roles.py:535-537`; the one `is_mounted` in code is the explanatory comment (`increment-003.md:171`). The sealed PDR text at `:59` (C1) keeps `is_mounted` by the amendment rule. |

---

## C · Verdict and what it means

- `approved` — the bar is met on all three axes (Coverage · Certainty · Evidence); state which.
- `approved with conditions` — list them above; each is individually dischargeable and re-read at the next gate.
- `rejected` — **returns to DESIGN, not to implementation.** Name the gap that caused it.

**Verdict: `approved with conditions — all conditions discharged`.** Axes: Coverage (rows 4, 8: six ATs in six nodes, C1-C8 and E1 re-read) · Certainty (the merged-tree full suite: `3432 passed, 24 deselected, 3 xfailed, 12 warnings in 2484.36s (0:41:24)` (orchestrator, clean shell, merged code `59a02d9`; 0 failed; the 24 deselected are the `slow` and `network` markers, `pyproject.toml:46` `addopts = "-m 'not slow and not network'"`; later commits are records and docs only)) · Evidence (rows 1-10 cited). Two independent reviews were applied: `architect` (Claude Opus) approved with conditions, `qa-reviewer` (Claude Sonnet) approved with conditions; the orchestrator's rulings discharge them one by one:

| # | Condition | Ruling | Discharged by |
|---|---|---|---|
| a | F3b doubled discovery start | accepted with evidence (6 git calls, same as before) | row 9 |
| b | `docs/ARCHITECTURE.md` header stale | header now reads "Last amended by `2026-10-11-fixes-batch`" | `docs/ARCHITECTURE.md:18` |
| c | L1 exit-time residual unowned | backlog `B-133`, bound ≈ 30 s stated | row 10; `.dev-flow/BACKLOG.md` |
| d | `pending` full-suite claims | replaced by the executed line and marker | rows 3, 5, 8 and this section |
| e | hoist cost unstated | row 2 → ⚠ with the O(E) `written_parents` scan declared, 2E+4 kept | row 2 |
| f | gate rows 6/15 and `Independent review PENDING` stale | reconciled to the §4b reviews | row 1 housekeeping; `03-increments/increment-001..003.md` |

Open notices carried forward, none blocking: row 1 (declared deltas), row 2 (hoist scan), row 10 (L1, `B-133`).

## D · Ids this record binds *(the glue of the repo ↔ vault split)*

| This record's decision | Id | Where it lands in the **repo** |
|---|---|---|
| E1 guard name `is_attached` confirmed against the code | `PDR-2026-10-11-fixes-batch#E1` | `mapper/screens/roles.py:535-537`; LLR-FX.4.1 (`01-requirements.md:321`) |
| ARQ F1 map amendment landed (PDR D1) | `PDR-2026-10-11-fixes-batch#D1` | `docs/ARCHITECTURE.md:101, 113` |
| F2 correction held (PDR D4): no resave reorder | `PDR-2026-10-11-fixes-batch#D4` | LLR-FX.3.1 (`01-requirements.md:305`) |
| A3 census pin moves 37 to 38 to 39, itemised | `DDR-2026-10-11-fixes-batch#D1` | `tests/test_a3_census.py` (`74d051a`, `da8b1d4`, `c7c975a`) |
| L1 exit-time thread residual accepted, bound ≈ 30 s | `DDR-2026-10-11-fixes-batch#D2` | `increment-003.md:183` (§4b); backlog `B-133` |
| F3b doubled discovery start accepted (6 git calls, unchanged) | `DDR-2026-10-11-fixes-batch#D3` | `design/arq-note.md:81`; `roles.py` generation guard |

**What decides code lands in the repo.** A decision that fixes an interface does not stay only in the
vault: it is reflected in the requirement or in the module map, which are versioned beside the code.
