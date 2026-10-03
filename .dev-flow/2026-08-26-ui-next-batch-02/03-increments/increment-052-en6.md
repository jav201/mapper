# Increment 052 -- Inc-EN-6: the palette footer advertises the arrows (`N2`)

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `b5cbd39`, code commit `e5b702a`. Authority: `A-134` (appended to `01-requirements.md`), `VERDICT-inc-en-2026-10-02.md` (EN-6 row), `VERDICT-inc9-2026-09-30.md` Round 4 `N2`. 2 source files (cap 4, no overage): `mapper/keymap.py`, `mapper/screens/palette.py`.

## 1. What changed

The palette footer was ` N/M actions   ↵ run   esc close`. It now reads ` N/M actions   ↑↓ move   ↵ run   esc close`, every glyph and word from the seat.

Seat change (`keymap.py`, palette scope, 2 rows to 4): `KeyBinding("up", "↑", "move_up", "move", "palette")` and `KeyBinding("down", "↓", "move_down", "move", "palette")`, placed before `enter`. Two honest rows, not one row with a `↑↓` glyph: a single row would bind one key while its glyph claimed two. Both carry the word `move`; the footer takes the word from `move_up` and the two glyphs from the two rows.

Dispatch (`palette.py`): the arrows are now the screen's `BINDINGS` (generated from the seat) calling `action_move_up` / `action_move_down`, which share `_move(delta)` with the page keys. `on_key` now forwards only `pageup` / `pagedown`. Why: the search box binds neither arrow, so a key bubbles to the screen's bindings; keeping the old `on_key` forwarding of `up`/`down` would have made the new bindings dead (`on_key` stops and prevents the default, so the binding never runs) and the seat row would have been decoration. The behaviour is the same: clamped at both ends, the box stays focused, `↵` runs the lit row, typing and cursor keys untouched. This is the one edit to the Inc-9f forwarding and is declared as such.

Separator: the footer's existing three spaces, not the verdict's ` · `. The verdict's string was read as the order; the existing style was kept as instructed.

## 2. Files modified

Source (2): `mapper/keymap.py`, `mapper/screens/palette.py`. Tests: `tests/test_en6.py` (new, 6 items); relabelled `tests/test_keymap.py` (palette count 2 to 4), `tests/test_key_dispatch.py` (two rows in the full-tuple table), `tests/test_inc9.py` (`DECLARED_ADDED` gains the two rows). Docs: `01-requirements.md` (`A-134`), this file. `state.json`, `prototypes/`, `mapper.db`, `fixtures/.mapper` not touched.

## 3. Sealed-arm changes (labels only; none weakened)

| Test | Pin | Old to new |
|---|---|---|
| `test_keymap` `EXPECTED_PER_SCOPE` | palette seat size | 2 to 4 |
| `test_key_dispatch` `EXPECTED_SEAT` | full `(action, label, glyph, group, priority)` table | + `("palette","up")` and `("palette","down")` |
| `test_inc9` `DECLARED_ADDED` | rows added since the entry sha | + `("palette","up","move_up")`, `("palette","down","move_down")` |

Each failed before the relabel with exactly the two new rows as the difference (output read), and passes after. No legend or help count pin moved: no help screen or legend is built for the palette scope (grep: the palette scope is read only by `palette.py`). The Inc-9e footer arms (`hint_pair` for run and close, sentinel) and the Inc-9f/9g/9h palette arms pass unchanged.

## 4. How to test

`python -m pytest tests/test_en6.py tests/test_palette.py tests/test_inc9e.py tests/test_inc9f.py tests/test_keymap.py tests/test_key_dispatch.py tests/test_inc9.py -q`. By hand: `ctrl+p`, press `down`/`up`/`pagedown`, type, left arrow, `↵`.

Footer render (real `ctrl+p`, home, 14 actions), measured:
- 118x34: `' 14/14 actions   ↑↓ move   ↵ run   esc close'`, 44 cells, dialog 80 wide.
- 87x34: identical string, 44 cells, dialog 80 wide.

The dialog is a fixed 80 columns; `test_en6` asserts `len(footer) <= dialog width` at both.

## 5. RED / GREEN and mutants

RED on the base: scratch `git worktree` of `b5cbd39` under `%TEMP%` (removed), `tests/test_en6.py` copied in, strict xfail on the 3 test functions that must fail there. Without `--runxfail`: `2 passed, 4 xfailed`; with `--runxfail`: `4 failed, 2 passed` (footer at 118 and at 87, the sentinel, the seat-rows arm). The 2 passes are controls by design: on the base the arrows already worked through `on_key`, so the arrow arm and the typing arm pass there and guard the behaviour across the change. `mapper` imported from the worktree (`__file__` checked). GREEN here: `6 passed`.

Mutants: harness in the scratchpad (outside the repo), byte-level read and write, sha256 pin checked after every restore (all `restored True`, final pins True), verdict printed before the restore, `-B -W error::SyntaxWarning -x`, temp HOME. Suites: `test_en6`, `test_palette`, `test_inc9e`, `test_inc9f`, `test_keymap`, `test_key_dispatch`.

| # | Mutant | Result | First failing test (`-x`) |
|---|---|---|---|
| M1 | footer without the move pair | KILLED | `test_en6` footer order, 118 |
| M2 | hand-written `↑↓` and `move` in the footer | KILLED | `test_en6` sentinel (glyphs `UU`/`DD`, labels `zz-*`) |
| M3 | `move_down` steps 2 | KILLED | `test_en6` arrows arm |
| M4 | `move_up` steps down | KILLED | `test_en6` arrows arm |
| M5 | `on_key` swallows every key (breaks typing) | KILLED | `test_en6` arrows arm (the typing arm is the intended guard; it was not reached under `-x`) |
| M6 | `down` handled in `on_key` AND by the binding (double move) | KILLED | `test_en6` arrows arm (`4 == 2`) |
| M7 | seat drops the `down` row | KILLED | `test_en6` footer arms (`KeyError` from `hint_pair`) |
| M8 | the two rows carry different words | KILLED | `test_en6` single-word arm |

8 run, 8 killed, 0 survived.

## 6. Test results

- Full default lane, once, uninterrupted, last step, on `e5b702a` (code and tests; docs-only commits follow): `2694 passed, 24 deselected, 3 xfailed` (0 failed) in 1619.8 s, `python -B -W error::SyntaxWarning -m pytest -q -rf -p no:cacheprovider`, temp HOME and USERPROFILE, git identity from environment variables. Baseline 2686: the 6 new `test_en6` items account for 2692; the other 2 are inferred, not measured, to be per-row cases of seat-conformance tests that parametrize over `KEYMAP` (two new rows).
- Lane history, declared: a first full lane ended `6 failed, 2688 passed`. Five were `tests/test_github.py` `Author identity unknown` (my environment fault: the temp HOME had no git identity, the same fault `increment-048` recorded). One was `test_inc9c` `...components_scroll_and_every_tab_stop_is_on_screen[size0]` (`tab stops off screen ... DsPagination`), the layout-timing check `increment-048` also saw. That lane is not counted. Re-running those tests with identity set, three times: 9 passed once, 9 passed once, and once `[size1]` of the same test failed again, so it is intermittent. It sits on the components sheet, which this increment does not touch. NOT measured: the same test repeated on `b5cbd39`, so "pre-existing intermittent" is the inference from `increment-048` plus the untouched screen. The second full lane (above) was clean.
- Ruff 0.8.4, programmatic set difference on (file, code, message) between `b5cbd39` in a scratch worktree and this tree over the 5 changed files that exist on both: 0 and 0, new: none.
- Cf characters (U+2011 included) in the 6 committed files and the 2 docs: 0; account-name grep: 0. No `prototypes/`, `mapper.db`, `fixtures/.mapper` or `state.json` staged. No `git stash`. The EN-5 reviewer's worktrees under `%TEMP%` were not touched.

## 7. Risks, unmeasured, next

- Risk: the arrows now depend on Textual's binding resolution rather than `on_key`. If a future Textual gives `Input` an `up`/`down` binding, the box would eat them; the `test_en6` arrows arm (real keys) would redden.
- Risk: `pageup` / `pagedown` stay undeclared in the seat and unadvertised, as before.
- NOT measured: widths other than 118 and 87 (the dialog is a fixed 80, the footer 44); the footer from a map-opened palette (the string is scope-independent, but the render was taken from home); POSIX.
- Left for later: `EN-7` (`?` in text fields).
- Suggested next: `EN-7`.

## Correction note (EN-8, 2026-10-02)

Appended; nothing above was rewritten. `EN6-REV-F1`: the dispatch paragraph ("the search box binds neither arrow") and the first risk ("if a future Textual gives `Input` an `up`/`down` binding, the box would eat them") are not accurate. `Input` already inherits `up` / `down` bindings (`scroll_up` / `scroll_down`, from `ScrollableContainer`, Textual 8.2.8); they raise `SkipAction` because a one-line `Input` cannot scroll, so the keys fall through to the palette's seat bindings. The risk is that an `Input` that becomes vertically scrollable, or a Textual that drops the `SkipAction` path, would eat the arrows. `tests/test_en6.py` now records that `action_move_up` / `action_move_down` fire (`EN6-REV-F2`) and that `enter` dismisses with the lit action (`EN6-REV-F3`). The `palette.py` comment was reworded the same way. `EN6-REV-F4`: the footer separators are ` · ` (`A-136`, `E3`), superseding the three-space sentence of `A-134`.
