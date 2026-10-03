# Increment 054 -- Inc-EN-8: operator wording (E1-E3), copy carries, `plain()` pins for six sites, review carries

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `9198edf`, code commits `f68d083` (tests, arms first), `045b3b2` (source), then a test fix and the docs. Authority: `A-136` (appended to `01-requirements.md`, dated 2026-10-02), `VERDICT-inc-en-2026-10-02.md` Rounds 1-3 (`E1`, `E2`, `E3`, the EN-8 routing paragraph). 4 source files (cap 4, no overage): `mapper/app.py`, `mapper/screens/palette.py`, `mapper/widgets/inspector.py`, `mapper/screens/coverage.py`. No feature, key or row moved.

## 1. What changed

Operator wording, exactly as ruled:

| Item | Old | New |
|---|---|---|
| 1 `E1` | `edge of the territory` (2 sites) | `edge of the map` (the rail keeps `territory`) |
| 2 `E2` | ` Nothing was written: the file X.svg does not match this export.` | ` Nothing was written; X.svg on disk is from an earlier export.` (interpolation, coercion, leading space kept) |
| 3 `E3` | ` N/M actions   ↑↓ move   ↵ run   esc close` | ` N/M actions   ↑↓ move · ↵ run · esc close` (still seat-derived; same 44 cells) |

Copy carries from the EN-5 review:

- 4. Ficha modal field `D`: label `record`, empty value `—` in the alert style. **Choice, declared:** the modal already prints `owner —` and `created —` for empty values, so `record —` keeps one column of labels and one way to say "empty"; the alternative (drop the label and print `no record`) breaks that column. `no record` stays the term in the hero, the micro-bar and the legend (`A-131`).
- 5. `and its 1 descendant?` for the root and non-root messages (other counts plural).
- 6. `cancel` / `close` lowercase in `_PromptScreen`, `_TemplateScreen`, `_FichaScreen`, `CoverageScreen`. `CoverageScreen`'s `Select` is not in the ruling and is unchanged (declared; one word to lowercase if wanted).
- 7. `declaration not available` -> `hidden-node count unavailable`.
- 8. `from template` door note: `start with preset fields`. Rendered on the home screen at 118 and 87: 40 cells, fits, no wrap.

Code comments: `FichaInspector._rebuild` (item 20) and the `palette.py` `on_key` comment (item 21) reworded as ruled. The `CR17-F4` comment above the export sentence gained two lines saying the authorship claim is the operator's ruling (it said no claim about authorship is licensed).

Tests: `tests/test_en8.py` (new, 20 items), plus carries in `test_en3` (`▫` -> `◫`), `test_en4` (census words, full-sentence `MapIdError` arm incl. "already exists"), `test_en5` (census words; `y` NOT added, asserted), `test_en6` (arrows, dismissed value), `test_inc9m` (`not any(...)`), `test_repair_cycles` (diagnostic), `test_vocabulary_declaration` (legend map read from `A-132`, six rows, each applied). Old-wording pins followed: `test_pan` (6), `test_en5` (2), `test_export_state` (2).

## 2. Files modified

Source (4): `mapper/app.py`, `mapper/screens/palette.py`, `mapper/widgets/inspector.py`, `mapper/screens/coverage.py`. Tests: `tests/test_en8.py` (new), `test_en3`, `test_en4`, `test_en5`, `test_en6`, `test_inc9m`, `test_repair_cycles`, `test_vocabulary_declaration`, `test_pan`, `test_export_state`. Docs: `01-requirements.md` (append `A-136`), correction notes appended to records 047-052, this file. `state.json`, `prototypes/`, `mapper.db`, `fixtures/.mapper`, `fixtures/mapper.db` not touched.

## 3. Item status (A-136 discipline: every carry closed or routed)

All 22 items done; none routed. Item 22's `047` note is limited: the `EN1-REV` finding text was not in the brief, so it records only what was checked against the tree (editor labels now lowercase and pinned since EN-5; `Cancel`/`Close` lowercased here). If the EN1 review had a different leftover, it is NOT closed by that note.

| Item | Where closed |
|---|---|
| 1-3, 4-8 | source commit; arms in `tests/test_en8.py` |
| 9-14 (`EN5-REV-F2`) | `tests/test_en8.py::test_plain_site_*` (section 5) |
| 15 `EN6-REV-F2/F3` | `test_en6.py` arrows arm |
| 16 `EN4-REV-F1/F2` | `test_vocabulary_declaration.py` |
| 17 `EN4-REV-F5` / `EN5-REV-F4` | `test_en4.py`, `test_en5.py` |
| 18 `EN5-REV-F7`, 19 `EN3-REV-F3` | `test_inc9m.py`, `test_en3.py` |
| 20, 21 | `inspector.py`, `palette.py` comments |
| 22 | notes appended to 047-052 (052 carries the `EN6-REV-F1` risk reword) |

## 4. How to test

`python -m pytest tests/test_en8.py tests/test_en6.py tests/test_en4.py tests/test_en5.py tests/test_vocabulary_declaration.py tests/test_pan.py tests/test_export_state.py -q`. By hand: pan a map to its left edge (`H`); open `ctrl+p`; press `x` on a branch of one child; press `e` on a map that exports and then grow it past the budget; open the ficha modal.

Renders at 118x34 (real app, `Pilot`; harness outside the repo):

```
E1 hint line:   |next ▸ edge of the map|
E2 notification (the toast widget was not captured; the text is the app's notification):
  map too large to export: 974852 cells, limit 350000. Focus a subtree with f and export that view. Nothing was written; crece.svg on disk is from an earlier export.
E3 palette footer:  | 33/33 actions   ↑↓ move · ↵ run · esc close|
ficha modal, record REC-7        ficha modal, no record
  |  alfa|                         |  alfa|
  |  m|                            |  m|
  |  state ok|                     |  state ok|
  |  record REC-7|                 |  record —|
  |  owner —|                      |  owner|
  |  created —|                    |  created —|
```

(In the right-hand render my fixture set `O` to an empty string, so `owner` is blank; with the key absent it prints `—`. Not a product change.)

## 5. RED / GREEN and mutants

RED on the base: scratch `git worktree` of `9198edf` under `%TEMP%` (removed), `tests/test_en8.py` and the carry edits checked out from `f68d083`, `mapper` imported from the worktree (`__file__` checked). Committed with the wording arms `xfail(strict=True)`: without `--runxfail` `8 passed, 12 xfailed`; with `--runxfail` `12 failed, 8 passed`. The 12 failures are assertion failures on the old wording (checked per test, not just counted): `edge of the territory` (2), the old export sentence (1), the old footer at both widths (2), `alfa` without the label `record` (2), `1 descendants` (2), `['Cancel']` (1), `declaration not available` (1), `map from a template` (1). The 8 passes are the six `plain()` pins (7 tests incl. `5a`/`5b`) and the plural control, green on the base by design. The carry edits to `test_en3`, `test_en4`, `test_en5`, `test_en6`, `test_inc9m`, `test_repair_cycles`, `test_vocabulary_declaration` are pins: 174 passed on the base. GREEN: `tests/test_en8.py` 20 passed.

Mutants: harness in the scratchpad (outside the repo), byte-level read and write (CRLF handled), sha256 pin per file checked after every restore (all `True`), verdict printed before the restore, `-B -W error::SyntaxWarning -x`, temp HOME.

| # | Site / mutant | Result | First failing test |
|---|---|---|---|
| S1 | archive confirmation name: drop `plain()` (`app.py` ~4615) | KILLED | `test_plain_site_1_the_archive_confirmation_name` |
| S2 | typed child title: drop `plain()` (~4546) | KILLED | `test_plain_site_2_a_typed_child_title_is_stored_coerced` |
| S3 | typed attachment target: drop `plain()` (~3447) | KILLED | `test_plain_site_3_a_typed_attachment_target_is_stored_coerced` |
| S4 | repo name in the sidebar: drop `plain()` (~1213) | KILLED | `test_plain_site_4_the_repo_name_of_an_accepted_local_path` |
| S5a | map canvas `str(exc)`: drop `plain()` (~3254) | KILLED | `test_plain_site_5a_the_map_canvas_failure_text` |
| S5b | preview canvas `str(exc)`: drop `plain()` (~1107) | KILLED | `test_plain_site_5b_the_preview_canvas_failure_text` |
| S6 | `GitHubError` text in the stages panel: drop `plain()` (~1453) | KILLED | `test_plain_site_6_a_github_error_in_the_stages_panel` |
| E1a | no-op edge site back to `territory` | KILLED | `test_e1_the_pan_edge_notice_reads_edge_of_the_map` |
| E1b | `pan_extent`-raises site back to `territory` | KILLED | `test_e1_the_unlaid_out_graph_site_says_it_too` |
| E2 | old stale-file sentence | KILLED | `test_e2_a_refused_export_says_where_the_old_file_comes_from` |
| E3 | move separator back to three spaces | KILLED | `test_e3_the_footer_is_...[size0]` |
| E3b | run separator back to three spaces | KILLED | same |
| EN6-F2 | `on_key` forwards `up`/`down` with stop (the 9f shape) | KILLED | `test_the_arrows_move_the_lit_row_and_enter_runs_it` (the actions did not fire) |
| EN6-F3 | `enter` dismisses `_items[0]` instead of the lit action | KILLED | same |
| EN4-F1a | `A-132` V41 row drifts (`↩ resume again`) | KILLED | `test_inc7_cr_r2_f3_the_declaration_EQUALS_the_document` |
| EN4-F1b | `A-132` V41 row dropped | KILLED | `test_en4_the_relabel_map_is_the_six_rows_of_a132_and_every_row_was_applied` |
| Q1 | (051 note) `connected:` drop `plain()` | KILLED | `test_inc9::test_llr_n06_2_5_notify_sites_are_coerced` |
| Q2 | (051 note) `file not found:` drop `plain()` | KILLED | same |
| S7 | (050 note) store save-time cycle sentence Spanish (`store.py` 823) | KILLED | `test_repair_fields::test_tc_r27_...` |

19 run, 19 killed. **History declared:** the first draft of S1 SURVIVED: the store coerces a title on its way in, so a saved-and-reloaded title never reached the confirmation raw and the arm exercised nothing. Fixed in a separate test commit (the raw title is put on the node in memory after the map loads); S1 is KILLED after it. The `EN4-F1a` mutant edits the requirement, not the product; the old hand-written map would not have noticed it (it was independent of `A-132`). Mutants that edit `store.py` and the requirements file are harness-only edits, restored by pin; `store.py` is not an EN-8 source file.

## 6. Test results

- Targeted before the lane: `tests/test_en8.py`, `test_en3`-`test_en6`, `test_inc9m`, `test_repair_cycles`, `test_vocabulary_declaration`, `test_pan`, `test_export_state`, `test_palette`, `test_darkside_census`, `test_inc3_census`, `test_a3_census`, `test_inc9`, `test_key_dispatch`: three old-wording pins failed after the source change (`test_export_state` stale sentence, `test_en5` door note and plural) and were updated; then green.
- Ruff 0.8.4, programmatic set difference on (file, code, message), `9198edf` in a scratch worktree vs this tree, over the 14 changed `.py` files: 1 and 1, new: none, gone: none.
- Cf characters (U+2011 included) in every changed file: 0 (one raw U+202E written by an editor tool into `tests/test_en8.py` was found by the grep and replaced by an escape before the first commit); account-name grep: 0. No `prototypes/`, `mapper.db`, `fixtures/.mapper`, `fixtures/mapper.db` or `state.json` staged. No `git stash`. The EN-7 reviewer's worktrees (`en7-rev`) were not touched; my scratch worktree was removed.
- Full-lane result: below.

## 7. Risks, unmeasured, next

- Risk: `E2` now asserts where the file comes from, which `is_file()` does not license (the `CR17-F4` argument). It is the operator's ruling; a directory or a hand-dropped file at that path would be called "from an earlier export". Declared, not mitigated.
- Risk: `record —` is shown in the alert style; if the operator wanted the plain `no record` words there, it is a one-line change.
- NOT measured: the ficha modal and the palette at widths other than 118 (the footer is the same 44 cells as before; the fit arm in `test_en6` still runs at 118 and 87); the export toast as a painted widget (text only); `Select` and any other capitalised binding label outside the ruling; POSIX.
- Suggested next: `EN-7` review items from the coordinator, then close the Inc-EN line.

## Full-lane result

`2746 passed, 24 deselected, 3 xfailed` (0 failed) in 1308 s, `python -B -W error::SyntaxWarning -m pytest -q -rf -p no:cacheprovider`, uninterrupted, last step, on `8952a2a` (all code and tests; this note follows). Baseline 2725 plus 21 new items (`test_en8.py` 20, `test_vocabulary_declaration.py` 1). Temp HOME and USERPROFILE, git identity from environment, no network. FLAKE-1 and FLAKE-4 did not occur.

Lane history, declared: a first full lane ended `1 failed, 2745 passed` (`test_inc9d::test_inc9d_sec_f1_a_missing_tilde_path_paints_no_profile_path`, "path not supported"). It re-failed alone three times and passed once my USERPROFILE was written correctly: my env file had lost the backslashes of the temp profile path, so `~` expansion produced an unsupported path. An environment fault of mine, not code and not a flake; that lane is not counted. The counted lane is the one above.
