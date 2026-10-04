# Increment 055 -- Inc-EN-9: no `?` where the only control is a text field (E4), review carries

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `9105abc`. Authority: `A-137` (appended to `01-requirements.md`, dated 2026-10-03), `VERDICT-inc-en-2026-10-02.md` Round 4 (`E4`, `EN7-REV-F1`) and its routing paragraph, plus the coordinator's EN-8 review items `EN8-REV-F1` to `F7`. Source files: 3 (`mapper/keymap.py`, `mapper/app.py`, `mapper/screens/coverage.py`; expected 2, ceiling 4, approved by the coordinator for the EN-8 items; no overage). Commits: `1881eee` and `4425472` (tests, arms first, `xfail(strict=True)`), `136d0fc` (E4 source), `3bd603e` (EOL restore), then the F2/F6/F7 fix and the docs.

## 1. What changed

**E4 (operator): connect-repo no longer lists `?`.** On a screen whose only focusable control is a text field the key bar and the legend do not list `?`, because `?` always types there. `ctrl+p palette` stays on the bar; the palette still lists and runs `legend`.

Design chosen (seat-derived, no painted string edited): `keymap.TEXT_ONLY_SCOPES = {SCOPE_PLUG: ("help",)}` maps a scope to the app-scope actions its field swallows.

- `bindings_for` omits them for that scope. The legend and the screen `BINDINGS` read it, so "help shows exactly the keys that work here" is true again.
- `textual_bindings` (the screen's `BINDINGS`) does NOT filter: connect-repo keeps its `question_mark` binding. The listing changes, the dispatch does not. A first draft filtered it too; the full lane then failed `test_inc9` twice (the derived help-screen set dropped to 6 and `PlugRepoScreen` became an unmatched opener), which exposed that the binding still fires once focus has left the field (`test_hlr_n16_1_every_help_route_carries_its_scope[PlugRepoScreen]` presses it for real). Changing dispatch was not what `E4` ruled, so the binding stays. That lane is not counted.
- `groups_for_keybar` omits them from the bar. It takes no scope today, so it derives the scope from the groups it is given: exactly one non-app scope among them. No call site changed (`app.py`, `factory.py`, `settings.py` call it as before).
- `palette_items` reads a private `_scope_rows` that does not filter, so the palette keeps `legend` on connect-repo. Chosen over an exclusion list in `app.py`: the rule lives in the seat, next to the rows it describes.

Rendered key bar of connect-repo (read from `KeyBar.content.plain`), before and after:

| width | before (`9105abc`) | after |
|---|---|---|
| 118 | `connect repo esc back   global ctrl+p palette  ? legend` | `connect repo esc back   global ctrl+p palette` |
| 87 | `connect repo esc back   global ctrl+p palette  ? legend` | `connect repo esc back   global ctrl+p palette` |

**Review carries.** `EN7-REV-F2`: dated correction appended to `A-135` (the palette's legend action reaches the legend from every seat-migrated screen; the coverage and editor modals have none), `B-82`. `EN7-REV-F3`: correction note on record 053 (no prompt pre-fills a value; select-on-focus is moot for prompts; verified by reading every `Input(` in the tree). `EN7-REV-F4`: **option chosen: relabel.** At 87 the inspector has a 0x0 region (the field's own `display` is still `True`, so `assert field.display` would have claimed nothing), so the 87 params of `test_question_mark_in_an_inspector_field_appends_and_keeps_the_content` are declared a programmatic-focus control in the docstring, and a region assertion pins which params are reachable (area > 0 at 118, == 0 at 87). `B-83` records the live path (`M` at 87 focuses the hidden `#insp-field-D` and typed text goes into it; measured on the base source and on this tree: same).

**EN-8 review items (coordinator).** `F1`: four records restored to LF in the index (`3bd603e`), `git ls-files --eol` 4 `i/crlf` / 385 `i/lf` before, 0 / 389 after (the `i/none` file unchanged); `git diff --ignore-cr-at-eol` empty. My own commits write LF into the index (`i/lf` on every touched file, checked). `F2`: `tests/test_overflow.py` comment "two widths sooner (34 -> 32)", note on record 049. `F3`/`F4`/`F5`: correction notes on records 048, 054, 047. `F6`: the ficha modal paints `owner —` / `created —` for an EMPTY value too (`fields.get("O") or "—"`). `F7`: the coverage `Select` binding label is `select`. No key, row or feature moved.

## 2. Files modified

**Sealed pins touched, declared (two):** (1) `tests/test_keymap.py::test_at_n03f_bound_keys_match_the_seat_exactly` required what a screen binds to equal `bindings_for(scope)`; the second counted lane failed on `[plug]` because connect-repo still binds `question_mark` but no longer lists it. The arm stays an equality: it now adds the keys `TEXT_ONLY_SCOPES` declares for that scope, so a bound key outside the seat's declaration still reddens it. Choice declared: the alternative was to drop the binding too, which needs `test_inc9` to lose `PlugRepoScreen` from its derived set and its opener table and drops the one real-key pin of plug's `?` outside a field; not what `E4` ruled. (2) `test_llr_n16_1_2_every_help_screen_declares_a_scope` required each help screen's scope to offer at least 3 rows through `bindings_for`; connect-repo now offers 2 (`esc`, `ctrl+p`), so the floor is 2, with a comment naming `E4`. The arm still catches an empty or one-row scope.

Source (3): `mapper/keymap.py`, `mapper/app.py` (two lines, `F6`), `mapper/screens/coverage.py` (one label, `F7`). Tests: `tests/test_en9.py` (new, 22 items), `tests/test_en7.py` (docstring and region pin), `tests/test_overflow.py` (comment), `tests/test_inc9.py` (one sealed pin relabelled, below). Docs: `01-requirements.md` (`A-137`, `A-135` correction), `BACKLOG.md` (`B-82`, `B-83`), correction notes on records 047, 048, 049, 053, 054, this file. `state.json`, `prototypes/`, `mapper.db`, `fixtures/.mapper`, `fixtures/mapper.db` not touched.

## 3. How to test

`python -B -W error::SyntaxWarning -m pytest -q -rf tests/test_en9.py tests/test_en7.py` (temp HOME and USERPROFILE, git identity from environment variables). By hand: open connect repo (`p` on home); the bar has no `?`; typing `?` types it; `ctrl+p`, `legend`, `enter` opens the legend without a `?` row.

## 4. RED / GREEN and mutants

RED on the base: scratch `git worktree` of `1881eee`/`4425472` (base source `9105abc` plus the tests) under `%TEMP%` (removed), `mapper` imported from the worktree (`__file__` checked). Default run: `10 passed, 7 xfailed`. With `--runxfail`: `7 failed, 10 passed` (bar x2, palette-opened legend x2, `bindings_for`, relabelled sentinel x2). The ten GREEN-on-base arms are the pins: other screens (home, map, factory, repo; 8 items), the settings sentinel control (2). `F6`/`F7` arms were written after their fix and are shown RED by mutant only (below), not by a base worktree; declared.

Mutants (harness in `%TEMP%`, outside the repo; byte-level read and write; sha256 pin per file re-checked after restore, all `True`; verdict printed before the restore):

| # | Mutant | Result | Killed by |
|---|---|---|---|
| M1 | exclusion removed (`TEXT_ONLY_SCOPES = {}`) | KILLED (8 failed) | the bar arms x2, the legend arms x2, `bindings_for`, sentinel plug x2, the binding pin |
| M2 | exclusion widened to every scope | KILLED (10 failed) | the other-screens arm (the legend-row regex; home, map, factory, repo at both widths), the settings sentinel x2. Declared: a first version of that arm asserted `"legend" in text`, which the legend footer satisfies on its own; M2 then died only on the short-bar screens (repo, settings). The arm now matches the `?  legend` key row |
| M3 | bar filter keyed on the painted glyph `?` instead of the seat action | KILLED (4 failed) | the relabelled-seat sentinel (plug x2); the repo arm x2 (the glyph filter also hid `?` on repo, a wider-scope effect). The bar arm alone does NOT kill it |
| M4 | palette reads `bindings_for` | KILLED (7 failed) | `bindings_for` arm, palette-opened legend arms, EN-7 palette-legend arms |
| M8 | `textual_bindings` reads the filtered rows (the first draft) | KILLED (3 failed) | the binding pin, and the two `test_inc9` derivation arms the lane had caught |
| M5 | `F6`: owner `get("O", "—")` | KILLED | `test_the_ficha_modal_shows_a_dash_for_an_empty_owner_and_created[]` |
| M6 | `F6`: created `get("Y", "—")` | KILLED | same |
| M7 | `F7`: `Select` back | KILLED | `test_every_coverage_binding_label_is_lowercase` |

M1-M4 and M8 were run on the final tree (`keymap.py` sha256 `848d243d...` pinned, restored `True`). 8 run, 8 killed, 0 survived.

## 5. Test results

- Full default lane, once, uninterrupted, last step, on `3fef871` (all code and tests; this docs commit follows): `2768 passed, 24 deselected, 3 xfailed` (0 failed) in 1343.48 s, `python -B -W error::SyntaxWarning -m pytest -q -rf -p no:cacheprovider`, temp HOME and USERPROFILE (real backslashes), git identity from environment variables. Baseline 2746 plus the 22 items of `test_en9.py`. FLAKE-1 and FLAKE-4 did not occur.
- Lane history, declared, none counted: (1) a lane started on `c7008db` was killed by me when the coordinator's EN-8 items arrived (its source was about to change). (2) The next lane, on `c7008db`, ended `2 failed, 2762 passed`: `test_inc9::test_llr_n16_1_1_the_screen_set_is_derived_and_large_enough` and `test_every_derived_help_screen_has_an_opener`, because the first draft also dropped connect-repo's `question_mark` binding (section 1). Fixed by keeping the binding. (3) The next, on `9feff3e`, ended `1 failed, 2767 passed`: `test_keymap::test_at_n03f_bound_keys_match_the_seat_exactly[plug]` (a bound key the seat no longer lists); the arm was relabelled (section 2). Not flakes: both were mine.
- Affected suites run alone before each lane: `test_en9`, `test_en7`, `test_inc9`, `test_keymap`, `test_palette`, `test_key_dispatch`, `test_help_scope`.
- Ruff 0.8.4, programmatic set difference on (file, code, message) between `9105abc` in a scratch worktree (removed) and this tree over the 7 changed source and test files: 1 and 1, new: none, fixed: none.
- Cf characters (U+2011 included) in every changed file: 0; account-name grep: 0. `git ls-files --eol`: 390 `i/lf`, 1 `i/none`, 0 `i/crlf`. No `prototypes/`, `mapper.db`, `fixtures/.mapper`, `fixtures/mapper.db` or `state.json` staged. No `git stash`. The EN-8 reviewer's worktree under `%TEMP%` was not touched (still listed).
- Declared slip: eight of the nine commits before this one carry the repository's configured author identity (`jav201`), not an environment one: the identity variables were exported per shell call and were missing in most commit calls. Only `3fef871` uses the environment identity. No file content is affected; the instruction named a temp HOME and an identity via env, and the commits do not fully honour the second half.

## 6. Risks, unmeasured, next

- Risk: `groups_for_keybar` infers the scope from its groups. A caller that passes groups of two concrete scopes gets no filtering (silently the old behaviour). Today every caller passes `keybar_groups(scope)`.
- Risk: `darkside.keybar` folds a long bar into `... +N  ? all keys` with a hard-coded `?` (`help_key`). Connect-repo's bar is two short groups and does not fold at 87 or 118, so this is not reached; a future text-only scope with a long bar would still print `?` in the fold marker. NOT measured at widths below 87.
- NOT measured: a real terminal's key encoding for `?`; POSIX; the legend of connect-repo at widths other than 118 and 87.
- Pre-existing, recorded: `B-82` (coverage and editor modals have no legend route), `B-83` (`M` at 87 focuses a hidden field).
- Suggested next: EN-10 as the coordinator routes it; `B-36` (blur commits unconditionally) remains the follow-on design item.

## Correction notes (Gate-1, 2026-10-03)

Appended; nothing above was rewritten.

`EN9-REV-F1` (over-claim in section 1): the bullet on `textual_bindings` says the connect-repo `?` binding "still fires once focus has left the field". Measured at Gate-1: Tab, shift+Tab and a click all leave focus on `#repo-input`; only `app.set_focus(None)` clears it. Read the claim as: the binding is reachable only programmatically today (the test `test_hlr_n16_1_every_help_route_carries_its_scope[PlugRepoScreen]` presses `?` after `set_focus(None)`). The dispatch decision stands (`E4` ruled the listing, not dispatch); only the reach was over-stated. The `keymap.textual_bindings` docstring was reworded to match.

`EN9-REV-F2` (stale clause in section 1): the first bullet ends "The legend and the screen `BINDINGS` read it". Drop "and the screen `BINDINGS`": the legend reads `bindings_for`; the screen `BINDINGS` read `textual_bindings`, which does not filter (the next bullet says so).

`EN9-REV-F3` (pin): a unit arm now asserts `groups_for_keybar` returns no `?` row for `['app', 'plug']` (app group first) and for `['plug', 'app']`, with positive controls. It kills the mutant "scope taken from the first group" (see `increment-056-gate1.md`).

