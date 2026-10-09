# Increment 003 — HLR-001/-002/-004/-005/-006 · `Card draft, ctrl+s, failure handling and the node-change guard`

> Batch-plan name: **Inc-1b**. The file is `increment-003.md` because it is the third packet written into this batch's `03-increments/` home (`increment-001.md` = Inc-3, `increment-002.md` = Inc-1a).

> **Interruption declared.** The first `software-dev` run of this increment was stopped by an accidental interrupt while its mutation battery was running. A second run (this packet's author) verified and completed the work instead of regenerating it. What the interrupt left behind, and how it was found, is in §6 (it left `mapper/app.py` in a **mutated** state).

| Field | Value |
|---|---|
| Batch | `2026-10-08-data-safety-batch` |
| Increment | `003` (plan name Inc-1b) |
| Lane (if the batch forked) | none · worktree `mapper-inc1b`, branch `inc1b/draft-save`, based on `554314f` |
| Requirement(s) | HLR-001 · HLR-002 · HLR-004 · HLR-005 · HLR-006 · LLR-001.1–001.4 · LLR-002.1–002.2 · LLR-003.1 (F1 boundary) · LLR-003.2 · LLR-004.1–004.4 · LLR-005.1–005.2 · LLR-006.1–006.2 · design rows 1b.1–1b.14a, 1b.15, 1b.16 · verdict R1–R9 · PDR C2, C3, C6, C7, C8, C10, C11, C13, C14 (Inc-1b parts) |
| Acceptance | AT-001 · AT-002 · AT-002a · AT-003 · AT-004 · AT-006 · AT-007 · AT-009 · AT-010 · AT-015 · white-box TC-001.1–TC-006.2, TC-004.2a–d · unit TC-L0-1, TC-L0-2 |
| Agent | `software-dev` |
| Date | 2026-10-09 |

---

## 1 · What changed

A card edit is now a **draft**: every keystroke updates an in-memory draft in the inspector, nothing is written on blur, `↵` or a state change, and `ctrl+s` (new map-seat row, not `priority`) writes the whole draft in **one** `store.save` with **one** undo snapshot. The header shows `● unsaved (N)` and each dirty label a `●` (WARN), repainted in place without remounting the focused field. A failed save restores the undo stack exactly, reloads the map through the screen's own load path (`_establish_graph`) and re-diffs the draft against disk; if the reload also fails the pre-save graph is kept and the toast reads `could not reload · draft kept · leaving needs d (discard)` (C8). Moving the cursor to another node with a draft opens the Inc-1a guard (`save · discard · stay`) before any repaint. With the card hidden, the hint line leads with `● unsaved (N) · ctrl+s save · ` in ALERT (C6/R8). After `ctrl+s` from inside a field, focus returns to that field (C7). `FieldCommitted` and its handler are deleted (I-5).

The source files are 3, all as the design names them. 57 new test nodes, 1 renamed.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/keymap.py` | source | LLR-001.4, LLR-005.2, AT-002, AT-010 | `KeyBinding("ctrl+s", "ctrl+s", "save_draft", "save", "node")`, not `priority` (1b.1) |
| `mapper/widgets/inspector.py` | source | HLR-001, HLR-002, HLR-005, HLR-006, LLR-001.1, LLR-001.2, LLR-001.3, LLR-002.1, LLR-002.2, LLR-005.1, LLR-006.1, LLR-006.2, AT-001, AT-003, AT-006, AT-007, AT-009, AT-010 | `FieldInput(node_id=…)`; draft surface `draft_node_id` / `draft_values()` / `has_draft()` / `clear_draft()`; `_field_of`, `_shown_value`, `_put_draft`; `on_input_changed`; `↵` → `action_leave_field`; segment → draft; `UNSAVED_STYLE = darkside.WARN`; `_paint_dirty` (no rebuild); `show()` re-diff; `FieldCommitted`, `on_input_blurred`, `_commit` deleted (1b.2–1b.8) |
| `mapper/app.py` | source | HLR-001, HLR-004, LLR-001.3, LLR-001.4, LLR-003.1, LLR-003.2, LLR-004.1, LLR-004.2, LLR-004.3, LLR-004.4, LLR-005.2, AT-002, AT-002a, AT-004, AT-006, AT-009, AT-015 | `MapHintLine` (draft prefix, C6); `_establish_graph`; `_paint_draft_hint`; `_drop_orphan_draft`; `_guard_draft` + `_draft_guard_open`; `_repoint`; `_apply_field` (replaces `_ficha_value`); `action_save_draft` / `_save_draft`; `_focused_field_id` / `_refocus_field` (C7); `_push_snapshot(graph=None)`; guard at the top of `refresh_canvas`; fill-in hint from the seat; `on_ficha_inspector_field_committed` deleted (1b.9–1b.16) |
| `tests/test_draft_save.py` | test | HLR-001, HLR-004, LLR-001.4, LLR-003.1, LLR-003.2, LLR-004.1–004.4, LLR-005.2, AT-001, AT-002, AT-002a, AT-003, AT-004, AT-006, AT-007, AT-009, AT-010, AT-015 | +28 functions, 37 nodes (E-1, E-2 helpers; C6, C7, F1 nodes) |
| `tests/test_inspector.py` | test | LLR-001.1, LLR-001.2, LLR-002.1, LLR-002.2, LLR-005.1, LLR-006.1, LLR-006.2, AT-003 | +11 functions, 16 nodes; E-6 tap with the C11 denylist; §5.3 (a) re-points of `n01a/b/d` |
| `tests/test_g6_store_surrogates.py` | test | LLR-001.3, LLR-004.2 | §5.3 (a): `g6b_field_committed…` renamed `g6b_draft_save…`; drivers type + `ctrl+s`; site key `draft_save`; f2 toast selected by content |
| `tests/test_worklist_safety.py` | test | LLR-004.1 | §5.3 (a): typed + `ctrl+s` instead of a posted message |
| `tests/test_data_safety_census.py` | test | LLR-001.4 | `DATA_SAFETY_ADDED` 4th row; +1 node `the_map_scope_gains_exactly_the_save_row` |
| `tests/test_keymap.py` | test | LLR-001.4 | §5.3 (c): `map: 31 → 32` |
| `tests/test_key_dispatch.py` | test | LLR-001.4 | §5.3 (b): `EXPECTED_SEAT` + `("map","ctrl+s")` |
| `tests/test_inc4_census.py` | test | LLR-001.4 | §5.3 NEW: subtract the batch's map row from the live seat |
| `tests/test_darkside_census.py` | test | LLR-002.1, LLR-002.2 | §5.3 NEW: +2 classified sites (WARN pending; ALERT hint prefix per R8), `38 → 40` |
| `.dev-flow/…/evidence/inc1b-*` (12 files) | doc | | driver, render script, renders, transcripts (§4 Evidence files) |
| `.dev-flow/…/03-increments/increment-003.md` | doc | | this packet |

| Count | Value |
|---|---|
| **SOURCE files** | **3** / 4 ⚠ (within the cap; the ⚠ marks that `mapper/app.py` alone carries +244/−54 lines — one file, but a large one, see §5) |
| Test files | 9 (0 new, 9 edited; uncapped) |
| Doc files | 13 (outside the count) |

---

## 3 · How to test

```bash
cd <worktree>   # mapper-inc1b
python -B -W error::SyntaxWarning -m pytest -q -rf -p no:cacheprovider tests/test_draft_save.py tests/test_inspector.py tests/test_g6_store_surrogates.py tests/test_worklist_safety.py tests/test_data_safety_census.py tests/test_keymap.py tests/test_key_dispatch.py tests/test_inc4_census.py tests/test_darkside_census.py
python -B .dev-flow/2026-10-08-data-safety-batch/evidence/inc1b-mutate.py red        # base-tree counterfactual (BASE pinned 554314f)
python -B .dev-flow/2026-10-08-data-safety-batch/evidence/inc1b-mutate.py census     # design 5.3 census
python -B .dev-flow/2026-10-08-data-safety-batch/evidence/inc1b-mutate.py A-no-refocus   # one mutant: apply, run, restore, sha-verify
python -B .dev-flow/2026-10-08-data-safety-batch/evidence/inc1b-render.py            # frames at 87/118/140
python -B -W error::SyntaxWarning -m pytest -q -rf -p no:cacheprovider               # default lane, ~25 min
```

**Manual, owed to the operator (C14):** in the real Windows terminal, open a map, type in a card field, press `ctrl+s` (both files change, focus stays in the field), then press `ctrl+q`. Not executed here (no real terminal in this environment).

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** TC-001.1, TC-001.2b, TC-002.1, TC-L0-1, TC-L0-2, LLR-003.1 F1 | `core` · `full` | `IN::test_llr_001_1_draft_surface_is_a_copy_and_clears`, `…a_stale_change_from_a_re_pointed_input_is_dropped`, `…dirty_is_against_the_shown_value_plain_alters_title`, `…_unknown_state`, `…dirty_is_measured_against_plain_not_the_raw_title`, `test_layer0_put_draft_branches[stale,equal_to_shown,set]`; `DS::test_layer0_apply_field_coerces_and_routes[title,notes,state,D]`, `DS::test_llr_003_1_an_empty_title_renders_empty_guillemets` | passed (executed) |
| **A · white-box** TC-001.2a, TC-001.4, TC-002.2, TC-003.2, TC-004.1, TC-004.2a–d, TC-004.3, TC-004.4, TC-005.1, TC-005.2, TC-006.1, TC-006.2, AT-002a, C6, C7 | `core` · `full` | the `test_llr_*` nodes of §2 plus `test_c6_…[87,118,140]`, `test_c7_…` | passed (executed) |
| **B · black-box** AT-001, AT-002, AT-003, AT-004[s,d,esc], AT-006, AT-007, AT-009, AT-010, AT-015[esc,click-markup] | `core` · `full` | `DS::test_at_*` | passed (executed) |

Touched files: `297 passed` before the fixes of this run; after them the default lane below. Python 3.12.7, Textual 8.2.8, Windows, executed.

**Default lane (executed, whole tree, final code, app.py `97ad3e64…`):** `python -B -W error::SyntaxWarning -m pytest -q -rf -p no:cacheprovider` → `2884 passed, 24 deselected, 3 xfailed in 1457.93s (0:24:17)`, `EXIT_CODE=0`. Transcript `evidence/inc1b-default-lane.transcript`. **Run 1 failed** (`1 failed, 2883 passed`, `EXIT_CODE=1`, kept as `evidence/inc1b-default-lane-1-r29.transcript`): `tests/test_repair_depth.py::test_tc_r29_no_recursive_graph_traversal_anywhere_in_mapper` flagged `MapScreen._refocus_field.focus` — the nested callback named `focus` calls `field.focus()`, which the static recursion census reads as self-recursion. Fixed by renaming the callback `restore_focus` (no behaviour change); run 2 is green.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | the three source files replaced by their `554314f` blobs (`git show 554314f:<path>`, written in place, restored from saved bytes; no stash, no checkout); every new and edited test as on disk |
| Instrument | `evidence/inc1b-mutate.py red` (BASE pinned to `554314f`, never `HEAD`) |
| Where it ran | own worktree `mapper-inc1b` |
| Transcript | `evidence/inc1b-red-counterfactual.transcript`: `59 failed, 238 passed` — `test_draft_save.py` 35 (of its 50 nodes; the 15 green ones are the Inc-1a modal nodes plus the F1 empty-title node, which test `DraftGuardScreen` alone), `test_inspector.py` 18, `test_data_safety_census.py` 2, `test_g6_store_surrogates.py` 1, `test_keymap.py` 1, `test_key_dispatch.py` 1, `test_darkside_census.py` 1 |
| Restore proven by | `restored: True` for `inspector.py` `bd24c09b…`, `app.py` `f37b33f5…`, `keymap.py` `dc3f513a…` |
| Bytecode cache | `python -B` on every run |

⚠ The RED, the census and the 48-mutant battery ran on `app.py` `f37b33f5…` (after the C6 repair of §6). One later source edit, the `restore_focus` rename (lane run 1), touches only the C7 helper; `A-no-refocus` was re-run on the final `97ad3e64…`, KILLED, appended to the battery transcript.

| Field | Value |
|---|---|
| **RED counterfactual** | base-tree swap of the 3 source files: 59 nodes RED by assertion, per resolved node id; transcript `evidence/inc1b-red-counterfactual.transcript`; all three files restored (`restored: True`). C13: `G-plain-title` turns `test_at_015_guard_title_carries_no_escape_byte[esc]` RED through `j` |

**Design §5.3 regression census (executed):** final source, the 8 edited existing test files at `554314f` + `test_inc9.py` + `test_a3_census.py`: `16 failed, 271 passed` (`evidence/inc1b-regression-census.transcript`). Every predicted (a)/(b)/(c)/NEW row reddened: `n01a`, `n01b[0..3]`, `n01d`; `g6b_field_committed…`, `g6c[field_commit]`, `g6c[undo]`, `g6c_f2`; `worklist n05_6`; `keymap completeness`; `n03h`; `inc4 cd25a`; `darkside hue census`; plus `test_inc9::cd25a` (reads `DATA_SAFETY_ADDED` from the base census file, which lacks the 4th row — consistent, green with the final file). `test_inc9` f6 and `test_keymap` M-1 stayed green as predicted.

### Mutation verdicts — per resolved node (`evidence/inc1b-mutation-battery.transcript`)

48 mutants, one at a time, over the behaviour files (`test_draft_save`, `test_inspector`, `test_g6_store_surrogates`, `test_worklist_safety`; seat mutants also over the census/keymap files). Every run prints `changed: True` and `restored: True`; pre-mutation digests `inspector.py bd24c09b…`, `app.py f37b33f5…`, `keymap.py dc3f513a…`, `draft_guard.py a162b1d6…`.

| Mutant | Mutation | Verdict | RED nodes |
|---|---|---|---|
| I-blur-save | blur → `_save_draft` re-added | KILLED | 21 (incl. `at_001`, `at_004[*]`, `llr_001_4`) |
| I-changed-to-blur | draft updated on blur only | KILLED | 25 (incl. `at_010`, `c7`) |
| I-stale-keyed-to-node | entry keyed to `self.node.id` | KILLED | `llr_001_2_a_stale_change…` |
| I-values-not-copy | `draft_values` returns the live dict | KILLED | `llr_001_1…` |
| I-clear-noop | `clear_draft` no-op | KILLED | 3 |
| I-count-binary | `N = min(1, len)` | KILLED | 3 (`at_003`, `at_002a[zero]`, `at_009`) |
| I-no-paint-on-change | no repaint on a keystroke | KILLED | 6 |
| I-remount-per-key | `_rebuild` per keystroke | **CRASH** | session hit the 120 s `pytest-timeout` (thread method kills the process; no node id resolved) |
| I-raw-title | dirty vs raw title | KILLED | `llr_002_1_dirty_is_measured_against_plain_not_the_raw_title` (new this run; it SURVIVED the interrupted run's battery, see below) |
| I-raw-state | dirty vs raw state | **CRASH** | 120 s timeout (`STATE_VALUES.index("weird")` raises inside `_rows`; the rebuild never completes) |
| I-prune-inverted | `==` prune → `!=` | KILLED | 65 |
| I-no-rediff | `show()` does not re-diff | KILLED | `llr_004_2_a_reload_that_carries_the_drafted_state_turns_it_clean` (new this run; SURVIVED before, see below) |
| I-no-notes-key | `notes` arm of `_field_of` dropped | KILLED | 5 |
| I-enter-saves | `↵` saves | KILLED | 3 |
| I-enter-stays | `↵` does not leave the field | KILLED | 2 |
| I-enter-direct | design's literal synchronous call | KILLED | 2 |
| I-segment-saves | segment saves at once | KILLED | 5 |
| A-snapshot-after | snapshot after applying | KILLED | 4 |
| A-save-twice | `_save_or_toast` twice | KILLED | 4 |
| A-save-per-field | one save per field | KILLED | 4 |
| A-snapshot-per-field | one snapshot per field | KILLED | `llr_004_1…` |
| A-clear-on-failure | clear draft on failure | KILLED | 3 |
| A-no-reload | keep `base_graph` | KILLED | 4 |
| A-pop-not-restore | `pop()` not slice restore | KILLED | `llr_004_2_failure_restores_the_undo_stack_exactly_at_depth` |
| A-mutate-then-save | apply onto `base_graph` before save | KILLED | `llr_004_2_reload_raises…` |
| A-save-subgraph | save `self.graph` | KILLED | `llr_004_4…` |
| A-assign-graph-only | reload without `_establish_graph` | KILLED | 2 |
| A-no-orphan-drop | skip `_drop_orphan_draft` | KILLED | `llr_004_2_a_draft_on_a_vanished_node…` |
| A-stay-repoints | `stay` re-points | KILLED | `at_004[escape-stay]` |
| A-show-before-guard | inspector re-pointed before the guard | KILLED | `llr_003_2_node_change_guard_holds…` |
| A-second-guard | no re-entrancy check | KILLED | `llr_003_2_a_second_mover…` |
| A-guard-same-node | same-node repaint asks | KILLED | 4 |
| A-undo-clears | undo clears the draft | KILLED | 2 |
| A-no-plain-apply | `_apply_field` drops `plain` | KILLED | 5 |
| A-swap-title-notes | branches swapped | KILLED | 12 |
| A-hint-literal | `↵ save` literal back | KILLED | 2 |
| A-hint-fixed-words | literal `ctrl+s save` | KILLED | `llr_005_2…` |
| A-no-refocus | C7 refocus dropped | KILLED | 5 (re-run on final `97ad3e64…`: 5, `restored: True`) |
| A-reload-toast | C8 wording → design's earlier one | KILLED | `llr_004_2_reload_raises…` |
| A-retry-toast-missing | no `draft kept` toast | KILLED | 2 |
| A-prefix-mut | prefix in MUT | KILLED | `c6[87,118,140]` |
| A-prefix-lost-on-set-hint | later `set_hint` drops prefix | KILLED | `c6[87,118,140]` |
| A-prefix-never | no prefix | KILLED | `c6[87,118,140]` |
| A-prefix-always | prefix with the card visible | KILLED | `c6[87,118,140]` (after this run's fix and its new visible-card arm) |
| K-ctrl-s-priority | `ctrl+s` made `priority` | KILLED | 2 (seat census, `n03h`) |
| K-ctrl-s-gone | `ctrl+s` row removed | KILLED | 25 |
| G-plain-title | `plain` dropped at the guard's title sink | KILLED | `at_015[esc]`, modal `…[esc]` |
| G-empty-placeholder | F1: placeholder for an empty title | KILLED | `llr_003_1_an_empty_title_renders_empty_guillemets` |

**Survivors closed in this run.** In the interrupted run's partial battery (`evidence/inc1b-mutation-battery-interrupted.transcript`) two mutants SURVIVED, and re-running them on the same bytes confirmed it: (1) `I-raw-title` — `store.load` already passes every title through `plain`, so through the real load path raw == shown and `…plain_alters_title` cannot tell them apart; a Layer-0 node now puts a raw control character on an in-memory node and asserts the shown value counts as clean. (2) `I-no-rediff` — a remounted `Input` re-posts `Changed` and re-diffs itself, so the title/`D` oracles of AT-002a/AT-009 never needed `show()`'s re-diff; the state segment does not re-post, so a new AT-002a [both-files] state arm is RED without it.

| Field | Value |
|---|---|
| **Mutation verdicts** | 48 mutants, per resolved node: 46 KILLED, 0 SURVIVED, 2 CRASH (`I-remount-per-key`, `I-raw-state`: the 120 s timeout kills the session, no node id resolved — declared, not counted as a named kill), 0 BAD; every restore `restored: True`; transcript `evidence/inc1b-mutation-battery.transcript` |

### Instrument RED-proof

| Instrument | Known-bad input | FAILURE it reported |
|---|---|---|
| sha256 hash-pair oracle (`_hashes`) | base tree (blur writes) | `at_001` RED in the counterfactual |
| `_failing_save` seam (E-2) | `A-clear-on-failure`, `A-no-reload` | `at_002a[zero]`, `[both]` RED |
| guard title oracle (`Static.content`) | `G-plain-title` | `at_015[esc]` RED |
| hint-line composited reader `_hint_text_and_prefix_style` | `A-prefix-mut`, `A-prefix-always` | `c6[*]` RED |
| E-6 message tap + C11 denylist | `I-blur-save` | `llr_001_2_draft_updates…` RED |
| `inc1b-mutate.py` | non-matching anchor | printed `BAD` for `A-prefix-never/-always` against the interrupted (mutated) `app.py`; that is how the corruption was found |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 6 instruments, each shown RED before its first PASS was believed |

### Emitted-form assertion

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts. (1) the map files `.mmd` / `_nodos.yml` emitted by `ctrl+s`: asserted on their bytes (sha256 pair) and on a fresh `MapStore.load` of them (`_disk`) in AT-002/AT-002a/AT-007/AT-009/AT-010. (2) the composited hint line (C6): asserted on the compositor's strips, text and the `●` segment's colour == `darkside.ALERT`, at 87/118/140. Transcripts post-processed: the operator profile path replaced by `<USERPROFILE>` in `inc1b-default-lane*.transcript` and `inc1b-related-files.transcript` (A-110); counts unchanged |

### Evidence files — under `artifact_homes.evidence` (`.dev-flow/2026-10-08-data-safety-batch/evidence/`)

| Evidence artifact | File | SHA-256 (working-tree bytes, `-text`) |
|---|---|---|
| Mutation / RED / census driver | `inc1b-mutate.py` | `40b6d1cef08c0736fe645d06ca51e33f39d5b2f74dae1c5b695b338215d1c0f2` |
| Mutation battery (48 + addendum) | `inc1b-mutation-battery.transcript` | `2889df6f28acd4df1f37d41b43260fd9573f1ff6b3337700c0ce39218731a9a8` |
| RED counterfactual | `inc1b-red-counterfactual.transcript` | `9ab03ee3b1c0cd501acc3a0510e305f64a14affacc301f07721ec1265015c0aa` |
| §5.3 regression census | `inc1b-regression-census.transcript` | `1a0f1aaefff39b3dc0e45ec431d9be6a3b673b58a63aaf7ee5867171bb6f8fcc` |
| Default lane run 2 (green) | `inc1b-default-lane.transcript` | `3a40265630e6140d900922924257c5677fadbfed1c1d2c57b5105dba47f268f8` |
| Default lane run 1 (r29 failure) | `inc1b-default-lane-1-r29.transcript` | `065a8fc0ceb7df433e5f25425e4c688d5adcc5af5a0f3790e1ece84e65d4dc4a` |
| Render script / renders 87·118·140 + 118 before | `inc1b-render.py` / `inc1b-renders.txt` | `a356f2a4ffaf7aac0961de32ea3737e9a111a189cc0a2631a4043ac4e1b9d342` / `4728f923d09a3cab739f6f6bd50b392dcba083446556830687b92ddc37c42d46` |
| Interrupted run: partial battery, RED, census, related files | `inc1b-mutation-battery-interrupted.transcript`, `inc1b-red-counterfactual-pre-final.transcript`, `inc1b-regression-census-pre-final.transcript`, `inc1b-related-files.transcript` | `cce8b8cf…faabe`, `e2c91676…6543`, `4c77fde8…8997`, `e1771dd2…961e` |

| Field | Value |
|---|---|
| **Evidence files** | 12 artifacts at the declared home with working-tree digests; index-blob digests to re-check after commit (§6) |

### Load-bearing emptiness

| Field | Value |
|---|---|
| Claim resting on an absence | LLR-001.3 / TC-001.3: no `FieldCommitted` / `field_committed` under `mapper/` and `tests/` |
| Search | `grep -rn "FieldCommitted\|field_committed" --include=*.py mapper tests` → 0 hits on the final tree |
| Positive control | the same grep on the `554314f` bytes (seen while the RED swap was live) returned 5 hits (`app.py:3344-3345`, `inspector.py:68,365,372`) |
| Conjunctive criteria | C6 = prefix shown ⟺ (card hidden AND draft): `A-prefix-never` and `A-prefix-always` separately; AT-015 = `plain` AND `markup=False`: `G-plain-title` here, `G-markup` at Inc-1a |
| Synthetic instance | `I-raw-title`: a raw-title node is synthesised in memory because the load path cannot produce one |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 removed symbols | `grep -rn "FieldCommitted\|field_committed\|_ficha_value\|_commit(" --include=*.py mapper tests` | 0 |
| B1 seat consumers | `--collect-only` grep for `ctrl+s` / `save_draft` outside the two owning files | `test_key_dispatch::n03g[ctrl+s->save_draft]`, `test_keymap::n03a[map:ctrl+s:save_draft]` — both green in the lane |
| B1 live-seat legends/keybars (§5.3 NEW) | default lane | all green; 118 before/after keybar frames in `inc1b-renders.txt` |
| B2 file moved | none | n/a |
| B3 goldens | `git ls-files \| grep -ci golden` | 1 by name (a test); green |
| A3 interface consumers | I-4 surface consumed by Inc-2 only; I-5 removed with its 3 test consumers in this increment | §5.3 (a) edits |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run; hits re-validated green in the default lane run 2 |

### Correction population

| Correction | Population | Method | Count | Edited | Left |
|---|---|---|---|---|---|
| tests driving the deleted commit path | `FieldCommitted` posters / `enter`-commits on inspector fields | design §5.3 + the census run (`inc1b-mutate.py census`) | 16 RED on base tests | all 16 (8 files) | none; `test_inc9::cd25a` needed no edit (reads the census file) |
| self-recursion census | nested callbacks in `mapper/` | `test_tc_r29…` in the lane | 1 | `restore_focus` rename | none |

| Field | Value |
|---|---|
| **Correction population** | 2 corrections enumerated before editing |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence |
|---|---|---|---|
| `FieldCommitted` / `field_committed` | 0 hits | yes (none survive) | grep above |
| `↵ save` hint literal | `grep -rn "↵ save" mapper` → 0 | yes | `A-hint-literal` KILLED |

### Signed-balance test ledger

`post = base − deleted + added` → `2887 = 2831 − 1 + 57` ✓ reconciles. Base 2831 (Inc-1a lane). Post: lane run 2 `2884 passed + 3 xfailed`. Added 57 = `test_draft_save.py` 37 + `test_inspector.py` 16 + `test_data_safety_census.py` 1 + `test_g6…` 1 (`g6b_draft_save…`) + 2 seat-parametrised arms (`n03g[ctrl+s->save_draft]`, `n03a[map:ctrl+s:save_draft]`). Deleted 1 (`g6b_field_committed…`).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | ABSENT — not yet run; owed by the orchestrator (`code-reviewer`; `ux-reviewer` for UX-1 over `inc1b-renders.txt`) |

---

## 5 · Risks

- `mapper/app.py` grows by ~190 net lines; the save/guard/failure logic is concentrated there by design (screen owns graph + store).
- Two mutants CRASH rather than resolve a node (timeout kills the session); a hang is a failure, but the battery cannot name which node caught it.
- The re-diff of text fields is carried twice (`show()` and the remounted `Input`'s `Changed`); only the state arm proves `show()`'s. If Textual stops posting `Changed` on mount, behaviour stays correct.
- `ctrl+s` reaching the screen from a focused `Input` is verified only under the Textual pilot; real-terminal delivery (Windows Terminal may intercept chords) is the operator's C14 smoke.
- One deepcopy of the whole graph per `ctrl+s` — not timed (design estimate).
- Exits other than node change (`q`, `esc`, `ctrl+q`, links, structural writes) are NOT guarded yet: Inc-2. Inc-1b must not ship alone.

---

## 6 · Pending items / spec deviations

- **Interruption and its residue (declared).** The interrupted run's battery was killed while `A-prefix-always` was applied, before its `finally` restore, and its transcript was block-buffered so it ended at `A-no-refocus`. `mapper/app.py` was left with the mutant (`if inspector.has_draft():` — prefix even with the card visible; digest `b6a6b9dc…` = that mutant's `sha256 mutated`). The C6 test still passed because its visible-card assertion ran before any repaint. Found by the driver printing `BAD` for both prefix mutants; fixed by restoring `if self.inspector_hidden and inspector.has_draft():` (bytes then equal the battery's pre-mutation `f37b33f5…`) and adding a visible-card arm (`I` back → no prefix) that kills `A-prefix-always`. The driver now runs `python -u`.
- **Run-1 lane failure** fixed (`restore_focus`), §4.
- **I-4:** `has_pending_draft()` is not built; the design lists it for its Inc-2 consumer. All other I-4 members are built; I-1, I-3, I-6 now frozen.
- **Design text vs C8:** design §2.1 step 6 still says `could not reload — leave and reopen the map`; the code follows PDR C8. Design text to be amended by the orchestrator.
- **C14 operator smoke OWED:** one real-terminal `ctrl+s` and `ctrl+q` press (§3).
- **UX-1 OWED:** `ux-reviewer` walkthrough over `evidence/inc1b-renders.txt`.
- **F2 (Inc-1a review, record only):** `evidence/inc1a-mutate.py`'s `red` mode restores from `git show HEAD:`; it should pin base `80635a1`. Not changed here. `inc1b-mutate.py` pins `554314f`.
- After commit: re-derive evidence digests from index blobs (`git show :<path> | sha256sum`).

**PDR conditions (Inc-1b parts):**

| Cond. | Status | Evidence |
|---|---|---|
| C2 `_repoint` | ✓ | `A-stay-repoints` KILLED |
| C3 `_establish_graph` / `on_mount` | ✓ | `A-assign-graph-only` KILLED; on_mount tests green in lane |
| C6 hint prefix, ALERT, 87/118/140 | ✓ | `test_c6_…[87,118,140]`; 4 prefix mutants KILLED; renders |
| C7 focus back after `ctrl+s` | ✓ | `test_c7_…`; `A-no-refocus` KILLED |
| C8 reload-failure toast | ✓ | `llr_004_2_reload_raises…`; `A-reload-toast` KILLED |
| C10 enablers + owners | ✓ declared | E-1, E-2, E-6 built here (`software-dev`); seeded second-map link (AT-011), `A` prompt driver + focusable chip (AT-014c/d), two-screen stack helper (AT-013): Inc-2, `software-dev` |
| C11 E-6 denylist | ✓ | `SAVE_BEARING` in `test_inspector.py`; primary oracle = save count + hash pair |
| C13 AT-015 through `j` | ✓ | `at_015[esc,click-markup]`, `Static.content` oracle; `G-plain-title` KILLED |
| C14 Inc-1b arms | ⚠ | same-node move ✓ (`a_move_onto_the_same_node_needs_no_guard`); E-2 third mode ✓ (`reload_raises`, `vanished_node`); esc-with-live-search, same-map link, archiving the draft's node → Inc-2; **real-terminal smoke owed to the operator** |

---

## 7 · Suggested next task

`code-reviewer` on this diff and `ux-reviewer` UX-1 over the renders (§4b); the operator's C14 terminal smoke; then C1 and Inc-2 (every other exit, `has_pending_draft`).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ⚠ | 3 source files; ⚠ declares `app.py`'s size (§2) |
| 2 | Tests written in this same increment | all | ✓ | +57 / −1 nodes, 2831 → 2887 |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | TC-L0-1, TC-L0-2, TC-001.1, TC-002.1 (§4) |
| 4 | RED counterfactual declared | `core` · `full` | ✓ | 59 RED, `inc1b-red-counterfactual.transcript`, restored |
| 5 | Reverse census declared | `core` · `full` | ✓ | 5 probes (§4) |
| 6 | `code-reviewer` passed | `core` · `full` | ⚠ | not yet run (§4b ABSENT) |
| 7 | No file from another lane touched | all | ✓ | 3 source, 9 tests, `.dev-flow` batch dirs; `prototypes/`, `mapper.db`, `fixtures/.mapper/` untouched |
| 8 | Frozen interfaces untouched | all | ✓ | I-2 consumed as amended at Inc-1a; I-4 built minus `has_pending_draft` (Inc-2) |
| 9 | Coverage claims verified on disk | all | ✓ | lane transcript, `--collect-only` |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 |
| 11 | Mutation verdicts declared per arm | all | ✓ | 48: 46 KILLED, 2 CRASH declared |
| 12 | Instrument RED-proof declared | all | ✓ | 6 instruments |
| 13 | Correction population declared | all | ✓ | 2 |
| 14 | Emitted-form assertion declared | all | ✓ | 2 artifacts |
| 15 | Independent review names somebody | all | ⚠ | ABSENT, owed |
| 16 | Evidence files declared with stored digests | all | ✓ | 12 files |

## Addendum (orchestrator, 2026-10-09) — independent reviews at the Inc-1b gate

- **§4b `code-reviewer`:** OK to advance · no HIGH; LOW F1 (1b.5 deviation: `inspector.py:750` defers `action_leave_field` via `call_later` — the synchronous call is broken, shown by mutant `I-enter-direct`; recorded here as a deviation), F2 (`g6c[field_commit]` → `g6c[draft_save]` is a second rename; net count unchanged), F3 (load-warning toasts repeat on the reload-failure arm — recommendation, not acted on); 4 mutants re-run and killed; `I-raw-state` is a NAMED kill (`test_llr_002_1_…unknown_state`, 0.5 s), not a crash; final `app.py` sha256 `97ad3e64…`.
- **UX-1 `ux-reviewer`:** approve-with-conditions — executed with the real pilot at 87/118. M1: C6 prefix missing after `M` → edit → `↵`/`esc` at 87 until the next repaint. M2: focusing a field with `tab` never names `ctrl+s`. Minors: header `● unsaved` is WARN amber while the hint prefix is ALERT red; a failed save shows two error toasts, the first with the raw `OSError`. Orchestrator ruling: M1, M2, the header colour (→ `ALERT`, operator R8 "rojo para alertar que hay contenido no guardado") and the single toast are fixed in **Inc-1c** before Inc-2.
- **C14:** the operator's real-terminal `ctrl+s`/`ctrl+q` smoke is still owed.
