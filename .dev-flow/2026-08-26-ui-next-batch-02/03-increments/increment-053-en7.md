# Increment 053 -- Inc-EN-7: `?` is a character in every text field (`T3`, `EN-Q3`, `B-72`)

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `0b53647`, code commits `761c0e0` and `fcebc51`. Authority: `A-135` (appended to `01-requirements.md`), `VERDICT-inc9-2026-09-30.md` Round 9 `T3`, `VERDICT-inc-en-2026-10-02.md` `EN-Q3`, `BACKLOG` `B-72`. 4 source files (cap 4, no overage): `mapper/keymap.py`, `mapper/app.py`, `mapper/widgets/inspector.py`, `mapper/screens/help.py`.

## 1. What changed

One rule: in every `Input` the key `?` inserts `?`; outside a text field `?` opens the legend; the palette's `legend` action opens it from anywhere.

- Mechanism, census first. `priority_actions` had one user (the connect-repo screen) and `check_consume_key` had one override (`_RepoInput`); `grep` over `mapper/` found no other. The seat's `?` row (`keymap.py`) is non-priority, so a focused `Input`, which consumes printable keys, already typed `?` everywhere except the connect-repo field. That field was the single exception and is removed: `_RepoInput`, `PlugRepoScreen.action_help`, its priority binding and the `priority_actions` parameter of `screen_bindings` are deleted. The connect-repo field is now a plain `Input`. `keymap.py` gains one comment on the `?` row saying why it is not priority.
- **B-72 choice: `FieldInput` is built with `select_on_focus=False`.** Focusing an inspector field now leaves the cursor at the end of the value instead of selecting all, so no single printable key replaces the whole title. Reason: the smallest change that stops the accidental overwrite, and the code has no "deliberate edit" gesture to hang a select-all on (`Tab` and `focus_field` both call `focus()`); a flag would add state to one widget. Cost declared: **B-36 is not closed** (blur still commits unconditionally), so a typed `?` is appended and saved on blur. That is a deliberate keystroke into a field the operator focused, not an overwrite.
- Footer: `? outside text fields opens this` / `legend; inside a field it types ?` (two lines because one does not fit the docked row of 39 cells). The select-all sentence is gone from the `FOOTER_LINES` comment.

## 2. Files modified

Source (4): `mapper/keymap.py`, `mapper/app.py`, `mapper/widgets/inspector.py`, `mapper/screens/help.py`. Tests: `tests/test_en7.py` (new, 31 items), `tests/test_inc9c.py` (one arm inverted). Docs: `01-requirements.md` (`A-135`), `01b-ux-decisions.md` (section 3.6 footer line and a change-table row), `BACKLOG.md` (`B-72`), this file. `state.json`, `prototypes/`, `mapper.db`, `fixtures/.mapper` not touched.

## 3. Sealed-arm changes

**Behaviour change, operator-ruled (`EN-Q3` supersedes `INC9-UX-F2`), not a label change:**

| Test | Was | Now |
|---|---|---|
| `test_inc9c_ux_f2_a_real_question_mark_in_the_repo_field_opens_the_legend` | real `?` in the connect-repo field opens the legend, titled `legend · connect repo`, and `esc` returns with the value intact | renamed `..._types_it`: real `?` leaves the screen on `PlugRepoScreen` and the value is `owner/na?` |

It is the only arm that pinned the `INC9-UX-F2` behaviour (grep of `tests/` for `priority_actions`, `_RepoInput`, `check_consume_key`: none). The arm was not weakened: it still presses the real key and now asserts the opposite outcome, and it is RED on the base.

**Help-text pin relabelled:** `test_inc8_cr_f3_the_section_headers_and_footer_EQUAL_section_3_6` reads the footer from `01b` section 3.6; the `01b` line is amended (dated, the earlier wording kept in the change table), so the pin follows without edit. It failed before the `01b` amendment and passes after. `test_inc9.py:163` (`app.set_focus(None)` before `?` on the plug screen) is unchanged and still true.

## 4. How to test

`python -m pytest tests/test_en7.py tests/test_inc9c.py tests/test_vocabulary_declaration.py tests/test_a3_census.py -q`. By hand: open a map, `tab` to the title, press `?` (title keeps its text and ends with `?`); on connect repo type `?`; on the map press `?` (legend); `ctrl+p`, type `legend`, `enter`.

Legend footer, real render, bottom of the pane (docked, 44-cell panel, same at 118x34 and 87x34):

```
|  ? outside text fields opens this|
|  legend; inside a field it types ?|
```

## 5. RED / GREEN and mutants

RED on the base: scratch `git worktree` of `0b53647` under `%TEMP%` (removed), `tests/test_en7.py` and the inverted `test_inc9c` arm copied in, a plugin outside the repo marks 7 test-name families `xfail(strict=True)`. Without `--runxfail`: `18 passed, 14 xfailed`; with `--runxfail`: `14 failed, 18 passed`. The 14: connect-repo at 118 and 87 (2), inspector title/notes/schema field at both widths (6), no priority `?` binding (1), no `_RepoInput` exception (1), footer copy (1), painted legend footer at both widths (2), the inverted `test_inc9c` arm (1). The 18 passes are controls by design: search, palette box and prompts type `?`, and `?` opens the legend on map, home and factory and from the palette, on the base too; they guard the behaviour across the change. `mapper` imported from the worktree (`__file__` checked). A first draft of the painted-footer arm compared to `FOOTER_LINES`, which made it pass on the base; the strict xfail caught it and it now compares to the literal sentence. The later switch from `.render()` to `.content` changes only the accessor, not the string; the RED run above was on the `.render()` draft of that one arm and was not repeated after the switch (NOT re-measured). GREEN: `32 passed` (31 + the inverted arm).

Mutants: harness in the scratchpad (outside the repo), byte-level read and write with CRLF handling, sha256 pin checked after every restore (all `restored True`, final pins True), verdict printed before the restore, `-B -W error::SyntaxWarning -x`, temp HOME.

| # | Mutant | Result | First failing test (`-x`) |
|---|---|---|---|
| M1 | connect-repo priority `help` binding and `action_help` restored | KILLED by the structural arm only | `test_no_screen_binds_the_question_mark_at_priority`; 26 behavioural items passed |
| M2 | `_RepoInput` release restored | KILLED by the structural arm only | `test_the_connect_repo_field_has_no_question_mark_exception`; 27 others passed |
| M3 | M1 and M2 together (the pre-EN-7 mechanism) | KILLED, behaviourally | `test_question_mark_in_the_connect_repo_field_types...[size0]` |
| M4 | inspector select-all restored | KILLED | `test_question_mark_in_an_inspector_field_appends...[insp-title-size0]` |
| M5 | help footer reverted | KILLED | `test_the_footer_states_the_rule_and_fits_the_docked_row` |
| M6 | outside-field `?` seat row removed | KILLED by the legend arm | `test_question_mark_outside_a_field_opens_the_legend[map-size0]` (run with `-k`; with the full set it died earlier, at collection of `test_inc9c`, `StopIteration`) |
| M7 | seat `?` row made priority | KILLED | `test_no_screen_binds_the_question_mark_at_priority` |

7 run, 7 killed, 0 survived. M1 and M2 alone are behaviourally equivalent to the new state on the connect-repo field (either half of the old pair does nothing without the other), so only the structural arms kill them; declared, and M3 (both) is killed behaviourally.

## 6. Test results

- Full default lane, once, uninterrupted, last step, on `fcebc51` (code and tests; this docs commit follows): `2725 passed, 24 deselected, 3 xfailed` (0 failed) in 1305.98 s, `python -B -W error::SyntaxWarning -m pytest -q -rf -p no:cacheprovider`, temp HOME and USERPROFILE, git identity from environment variables. Baseline 2694 plus 31 new items; the inverted arm is a rename, not an addition.
- Lane history, declared: a first full lane on `761c0e0` ended `2 failed, 2723 passed` (`test_a3_census` cardinalities: my footer arm called a zero-arg `.render()`, adding a 37th site against a pin of 36). Not a flake. Fixed by reading `Static.content` (no new site) instead of changing the sealed pin; that lane is not counted. FLAKE-1 and FLAKE-4 did not occur in the counted lane.
- Affected suites run alone before the lane (12 files, 405 items): the only 2 failures were the two sealed pins above.
- Ruff 0.8.4, programmatic set difference on (file, code, message) between `0b53647` in a scratch worktree and this tree over the 6 changed source and test files: 1 and 1, new: none, fixed: none.
- Cf characters (U+2011 included) in the changed files: 0; account-name grep: 0. No `prototypes/`, `mapper.db`, `fixtures/.mapper` or `state.json` staged. No `git stash`. The EN-5 and EN-6 reviewers' worktrees under `%TEMP%` were not touched (still listed).

## 7. Risks, unmeasured, next

- Risk: `B-36` stays open. Blur still commits the value unconditionally, so a stray `?` typed into a focused field is saved. The overwrite is gone; the one-keystroke save is not.
- Risk: `select_on_focus=False` applies to every inspector field. An operator who relied on tab-then-type-to-replace must now clear the field. Chosen on purpose; named for the operator to confirm.
- Prompts keep Textual's select-on-focus (`save as` has a default name that typing replaces); `?` there replaces the default like any key. Not changed: outside the `B-72` ruling.
- NOT measured: widths other than 118 and 87; a pasted `?`; a real terminal's key encoding for `?` (Pilot sends `question_mark`); POSIX.
- Suggested next: `B-36` (dirty-since-focus flag), the follow-on design item.
