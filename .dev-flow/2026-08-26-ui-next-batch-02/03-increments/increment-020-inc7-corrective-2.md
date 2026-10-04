# Increment 020 · Inc-7 corrective pass 2 · 2026-09-28

Fixes `CR-F1` and `CR-F3` from the round-2 re-review (`increment-019`), plus the
cheap carry `INC7-CR-R2-F1`, at HEAD `0c4215a` on `feat/ui-next-batch-02`. Tree
clean before and after (`git status --porcelain` = 0 lines both times).

## What changed, per finding

### CR-F1 (HIGH) -- the declared string, and an arm that can now disagree with it

`darkside.DAMAGED_MAP_STATE` was `"dañado — ↵ ver por qué"` -- missing **mapa**
against the declared string `mapa dañado — ↵ ver por qué`
(`01-requirements.md:3846`, LLR-N13.1.5; `01b` row V22). Corrected the
constant, byte for byte, to `"mapa dañado — ↵ ver por qué"`
(`mapper/darkside.py:623`).

The arm (`tests/test_repair_cycles.py::test_llr_n13_1_5_the_card_carries_the_DECLARED_state_string`)
previously asserted `darkside.DAMAGED_MAP_STATE in painted` -- comparing the
card to the very constant under test, so a wrong constant and a wrong card
always agreed. It now derives the expected string from
`01-requirements.md`'s `LLR-N13.1.5` section directly (`_declared_card_state_string()`,
new in the test file): reads the file as bytes, decodes UTF-8 explicitly,
scopes the search between the `##### LLR-N13.1.5` heading and the next `#####`
heading, and regexes on the literal anchor
`Declared card state (Spanish, the string that ships):` -- no digit-only id
pattern anywhere in the derivation, so the `V4a`/`V4b`/`AT-007b`-suffix hazard
this batch has hit before does not apply here. The test now asserts the
derived string **equals** `darkside.DAMAGED_MAP_STATE` (so a drifted constant
fails on its own line) and that it appears in the painted card.

### CR-F3 (HIGH) -- the stale block deleted, the docstring narrowed to what is checked

Deleted the block at the old `darkside.py:557-560` claiming
`` `tests/test_home.py` DERIVES from that document and compares `` -- that
file does not exist and never did (confirmed again: `git log --all -- tests/test_home.py`
returns nothing).

Rewrote the `DECLARED_VOCABULARY` `#:` docstring (`mapper/darkside.py:557-580`):

- States the member shape plainly as a **4-tuple** `(row id, glyph, label,
  style token)` -- the old docstring said "`(row id, label, style token)`", a
  triple, while the actual annotation and every literal row have always been
  four elements.
- Names exactly what `tests/test_vocabulary_declaration.py` checks: every
  declared `(label, style)` pair is faithful to a row in `01b` sections
  3.1-3.4 (no fabricated label, no drifted style), and `V22`'s glyph is pinned
  to the glyph `01b`'s row for `PRED-VIS` names. **This sentence was true as
  WORDED but unearned as CHECKED**: at the time this was written, the pin was
  `declared["V22"] == darkside.DAMAGED_MAP_GLYPH` -- two constants in the same
  module, never reading `01b` at all. Round 3 (`INC7-CR-R3-F1`, below) closed
  that gap; see that section for the fix and its mutants.
- Names exactly what it does **not** check, with an owner for each: dropping a
  row, or renaming a row's ID while leaving its label and style untouched,
  leaves the suite green today -- **completeness** is `INC7-CR-R2-F3`, carried
  to Inc-8, which owes set equality against the document -- and the **glyph
  column** of every row but `V22` is lifted from `01b`'s prose by hand and
  unchecked against it -- that is `INC7-CR-R2-F2`, also carried to Inc-8,
  which owes a written derivation rule for it. (The "renaming a row's ID"
  precision is `INC7-CR-R3-F2`'s fix, below -- the original wording said
  merely "renaming a row," which over-claimed the gap: renaming the LABEL
  already goes RED via the faithfulness check.)
- Dropped the old "`NO COUNT IS WRITTEN ANYWHERE ... tests/test_vocabulary_declaration.py
  checks it against the document on every run`" sentence -- verified false
  (no test in that file calls `len()` on either side; see the ruled-out check
  below) and itself an instance of the exact defect `CR-F3` is about.
- Kept "nothing here may be edited without the row in `01b` moving first" and
  the STYLE-IS-A-TOKEN-NAME and compound-row (`A-103`) paragraphs unchanged --
  neither was named as wrong.

No test file changes were needed for `CR-F3`: the `#:` lines are plain
comments, not a runtime `__doc__` string (confirmed: `grep -rn "test_home\.py\|__doc__"`
shows only `test_darkside_census.py` reading the unrelated *module*-level
`darkside.__doc__`, never this attribute), so nothing in the suite asserts
this text and nothing needed updating to match the rewrite.

### INC7-CR-R2-F1 (MEDIUM) -- the A-102 guards, each proven to matter on its own

The round-2 finding: the `not in damaged` clause on the hero path
(`app.py:648`, `if graph is not None and last_map not in damaged:`) and the
resume path (`app.py:705`, `if map_id and node_id and map_id not in damaged
and resume_graph is not None:`) were each individually removable without
reddening anything. The existing arm for this branch
(`test_llr_n13_1_5_no_OTHER_surface_paints_a_damaged_map_as_healthy`) drives
both surfaces through `roto`, a map whose *load raises* -- `load_or_notice`
returns `None` for that fixture, so `graph is not None` is already `False`
and the `not in damaged` clause never runs.

Added `test_inc7_cr_r2_f1_the_A102_guard_hides_a_LOAD_WARNING_map_too`
(parametrized `surface in ["hero", "resume"]`), using the same
monkeypatched-`MapStore.load` fixture as
`test_llr_n13_1_5_a_LOAD_WARNING_also_reaches_the_card`: a map that **loads
successfully but records a load warning**. `load_or_notice` still returns a
graph for that map, so it is `damaged` **only** through the clause each guard
exists to enforce -- this is the fixture that actually exercises them. No
`app.py` change; behaviour was already correct, only untested.

## Mutation table

Mutation discipline followed throughout: sha256 pinned before each mutation,
byte-level replace, named test run and verdict printed **before** restoring,
byte-level restore, sha256 re-verified against the pin. No probe files left
outside pytest; no scratch files written inside the repo.

| # | Mutant | File : sha256 pin | Test run | Verdict | Restored, sha ok |
|---|---|---|---|---|---|
| 1 | `CR-F1`: `DAMAGED_MAP_STATE` reverted to the OLD wrong value (`"dañado — ↵ ver por qué"`, missing `mapa`) | `mapper/darkside.py` : `d60272fa4c01...` | `test_llr_n13_1_5_the_card_carries_the_DECLARED_state_string` | **RED** -- `AssertionError: darkside.DAMAGED_MAP_STATE is 'dañado — ↵ ver por qué' but 01-requirements.md's LLR-N13.1.5 declares 'mapa dañado — ↵ ver por qué'` | yes |
| 1b | same file, fix restored | `mapper/darkside.py` : `d60272fa4c01...` | same test | **GREEN** -- `1 passed, 32 deselected` | yes (this is the fix state, no further restore) |
| 2 | `INC7-CR-R2-F1` hero: `app.py:648` guard narrowed from `if graph is not None and last_map not in damaged:` to `if graph is not None:` | `mapper/app.py` : `e14c8d77bb63...` | `test_inc7_cr_r2_f1_the_A102_guard_hides_a_LOAD_WARNING_map_too` | **RED on `[hero]`, GREEN on `[resume]`** -- `1 failed, 1 passed`; failure: `the hero surface presents a map that loaded with a WARNING as if it were usable` | yes |
| 3 | `INC7-CR-R2-F1` resume: `app.py:705` guard narrowed from `if map_id and node_id and map_id not in damaged and resume_graph is not None:` to `if map_id and node_id and resume_graph is not None:` | `mapper/app.py` : `e14c8d77bb63...` | same test | **RED on `[resume]`, GREEN on `[hero]`** -- `1 failed, 1 passed`; failure: `the resume surface presents a map that loaded with a WARNING as if it were usable` | yes |

Full pins: `mapper/darkside.py` = `d60272fa4c015eda59619137cb5fab509870e9d4637bfb587360998bec594b77`;
`mapper/app.py` = `e14c8d77bb63628b37a4eb4624114ea566e8b80356266fb21f65c54751ab28eb`.
Both verified restored (sha matched the pin) immediately after each mutant's
verdict was recorded, and `git status --porcelain` showed only the intended
diff (`darkside.py`, `test_repair_cycles.py`) throughout -- `app.py` never
appears in `git diff` at any point, confirming the two `app.py` mutants left
no trace.

## Tests run

Targeted: `tests/test_repair_cycles.py` + `tests/test_vocabulary_declaration.py`
-> **38 passed** (the prior 36, plus the 2 new `INC7-CR-R2-F1` parametrized
cases).

Full default lane, once:

```
8 failed, 1160 passed, 20 deselected, 3 xfailed in 302.57s (0:05:02)
```

`FLAKE-1` (`test_llr_cnv_3_1_the_parent_walk_maps_a_nested_widget_to_its_region`,
`assert '' == 'inspector'`) **did not fire this run** -- absent from the
failure list.

The 8 failures are **all** in `tests/test_agree_floor.py`
(`test_at057_floor_the_strip_carries_the_declaration_the_canvas_drops[legacy]`,
`[anidado]`; `test_at057_above_the_floor_the_canvas_still_declares[legacy]`,
`[anidado]`; `test_radial_agree1_holds_at_every_frame_including_the_narrow_corner[legacy]`,
`[anidado]`; `test_the_narrow_grid_really_does_reach_a_floor_in_outline[legacy]`,
`[anidado]`), all `ZeroDivisionError: division by zero` inside
`HomeScreen._sparkline_text` (`app.py:579`, `idx = min(len(bars) - 1, int(c /
max_count * (len(bars) - 1)))` with `max_count == 0`). **This is a NEW
observation, not a claim from this increment's own scope**, so it was
verified rather than assumed: `git stash` of both changed files, then
`pytest tests/test_agree_floor.py -q` on the **unmodified HEAD `0c4215a`**
reproduces the identical 8 failures with the identical traceback, then the
stash was popped back. It predates this pass, is untouched by either diff
file (`darkside.py`, `test_repair_cycles.py`), and looks date-dependent
(the fixtures' recorded `mtime`s vs. `date.today()` == 2026-09-28 driving
`counts` to all-zero). **Not fixed here** -- out of this pass's three-item
scope (`CR-F1`, `CR-F3`, `INC7-CR-R2-F1`) and touching `_sparkline_text` would
be a fourth, undeclared source change. Flagging for the coordinator as a new,
unscoped, date-sensitive defect, distinct from `FLAKE-1`.

## Ruff

Baseline captured from `ruff check --output-format=concise` at unmodified
HEAD `0c4215a`: **27 distinct errors**, 29 output lines (27 error lines + the
`Found 27 errors` and `[*] N fixable` summary lines -- this reconciles the
prompt's "29 errors" against the tool's own "Found 27 errors" line: the
"29" was the previous reviewer counting output *lines*, not error *entries*).

After this pass's changes: `diff` of the two `--output-format=concise` captures
is **empty** -- identical 27-error, 29-line set, byte for byte. Zero new
errors; the SET is unchanged, not merely the count.

## Files modified

- `mapper/darkside.py` -- `DAMAGED_MAP_STATE` corrected; `DECLARED_VOCABULARY`
  docstring narrowed (stale block deleted, 4-tuple shape stated, carries
  named).
- `tests/test_repair_cycles.py` -- `CR-F1` arm now derives its expectation
  from `01-requirements.md`; new `INC7-CR-R2-F1` parametrized arm for the
  hero/resume A-102 guards.

Two files, both inside the 4-file source/test cap this pass declared as
expected; `.dev-flow/state.json` was not touched (coordinator updates it
after review).

## Carries left open (not touched by this pass)

- `INC7-CR-R2-F2` (glyph-column fidelity beyond `V22`) -- Inc-8.
- `INC7-CR-R2-F3` (vocabulary completeness / set equality) -- Inc-8.
- `INC7-CR-R2-F4` -- merged with `INC7-SEC-R2-F2`.
- `INC7-SEC-R2-F1` -- carry to tester / next sala increment.
- `INC7-SEC-R2-F2` -- carry with `N-C2`, `F4`.
- `INC7-SEC-R2-F3` -- `B-64` re-basing.
- Routed `table.clear()` item (`app.py:724-725`) -- qa-reviewer, not Inc-7.
- `INC7-CR-R3-F3` -- the `test_agree_floor.py` `ZeroDivisionError` in
  `_sparkline_text`, below. **Not fixed. Goes to the operator**, not to a
  further Inc-7 pass -- see "Round 3", below.

## Round 3 (2026-09-28)

The code-lens-only round 3 review (see "Next", above, in this file's original
form) returned **BLOCK-UNTIL `INC7-CR-R3-F1`**. `CR-F1` and `INC7-CR-R2-F1`
were both CONFIRMED by the reviewer's own mutants, including one guard this
pass had not itself run (`app.py:655`, the mmd-fallback hero guard). The
apparent "two strings for V22" question (the Glyph column's embedded card
string vs. the separate Label column) was ruled legitimate -- 01b's own
columns, not drift.

### INC7-CR-R3-F1 (HIGH, same class as `CR-F3`) -- FIXED

**The false claim:** this file's own §CR-F3 write-up (and `darkside.py`'s
docstring) said `V22`'s glyph is "pinned to the glyph `01b`'s row ... names."
**Why it was false:** the assert backing that sentence,
`test_llr_n16_2_1_the_damaged_map_row_is_declared_and_not_deferred`'s
`declared["V22"] == darkside.DAMAGED_MAP_GLYPH`, compares two constants that
both live in `darkside.py` -- `declared` is built from
`darkside.DECLARED_VOCABULARY` and `DAMAGED_MAP_GLYPH` sits a few lines below
it in the same module. Nothing in `tests/` read `⊘` out of `01b` itself.
Measured: the reviewer's mutant E (both glyphs changed to `X`, in tandem)
left the suite at **38 passed**, unchanged.

**Fix (option b -- make the claim true by derivation), in
`tests/test_vocabulary_declaration.py`:**

- Added `_v22_glyph_cell_from_01b()`: reads `01b-ux-decisions.md` as bytes,
  decodes UTF-8 explicitly, and searches with `_V22_ROW =
  re.compile(r"^\|\s*V22\s*\|(.*?)\|", re.M)` -- anchored on the **literal id
  cell** `V22`, not the shared suffix-aware `V\d+[a-z]?` pattern used for the
  many-row walk elsewhere in the file (that pattern is fine for a walk; this
  derivation has exactly one row to name). Asserts loudly if the row is
  missing.
- Added `_first_backtick_token()`: pulls the first backtick-quoted token out
  of that cell, asserting loudly if none is found or the token is empty --
  the parse does not degrade silently.
- In `test_llr_n16_2_1_the_damaged_map_row_is_declared_and_not_deferred`,
  **kept** the existing `declared["V22"] == darkside.DAMAGED_MAP_GLYPH`
  assert unchanged, and **added** a second, independent assert:
  `_first_backtick_token(_v22_glyph_cell_from_01b()) ==
  darkside.DAMAGED_MAP_GLYPH`. The added assert has nothing on its left-hand
  side that comes from `darkside`.

**Mutants run (sha256-pinned, byte-level, restored, re-verified):**

| # | Mutant | File : pin | Test | Verdict | Restored ok |
|---|---|---|---|---|---|
| 4 | Only `01b`'s `V22` glyph changed to `X` (`darkside.py` untouched) | `01b-ux-decisions.md` : `c4cb2ad59a22...` | `test_llr_n16_2_1_the_damaged_map_row_is_declared_and_not_deferred` | **RED** -- `AssertionError: 01b's V22 row gives the glyph 'X' but darkside.DAMAGED_MAP_GLYPH is '⊘'` | yes |
| 5 | Mutant E: BOTH `darkside.py` glyphs changed to `X` in tandem (`DECLARED_VOCABULARY`'s `V22` entry AND `DAMAGED_MAP_GLYPH`; `01b` untouched) | `mapper/darkside.py` : `2da709ba185b...` | same test | **RED** -- `AssertionError: 01b's V22 row gives the glyph '⊘' but darkside.DAMAGED_MAP_GLYPH is 'X'` | yes |

Full pins: `01b-ux-decisions.md` =
`c4cb2ad59a22998427123de05fc0d9fe313db41bc42cae7b2c02a2d72de81607`;
`mapper/darkside.py` =
`2da709ba185b4a1ebc6e9d59e458ecf73a6662dbf742cbfab26e92a616f68b67`. Both
verified restored (sha matched the pin) immediately after each mutant's
verdict was recorded. `git status --porcelain` showed only the intended diff
(`darkside.py`, `test_vocabulary_declaration.py`) throughout --
`01b-ux-decisions.md` never appears in `git diff` at any point, confirming
mutant 4 left no trace.

Mutant E specifically is now killed: with the reviewer's exact mutation
re-applied (both glyphs to `X`, in tandem, `01b` untouched), the new,
document-independent assert reddens, because `01b`'s real row still says
`⊘` while `darkside` now says `X`.

### INC7-CR-R3-F2 (LOW, folded into the same edit) -- FIXED

The docstring (and this file's §CR-F3 write-up) said "renaming a row" leaves
the suite green, without saying renaming *what part* of a row. Renaming a
row's **label** already goes RED via
`test_llr_n16_2_1_every_declared_row_is_FAITHFUL_to_the_document` (the label
would then appear nowhere in `01b`'s doc-derived label set). Only renaming a
row's **ID** -- leaving its label and style untouched -- leaves the suite
green, since nothing checks id-to-id correspondence. Reworded both
`darkside.py`'s docstring and this file's §CR-F3 section (above) to say "row's
ID," not "row." No test change needed -- this was a wording-only overclaim,
and the underlying gap (`INC7-CR-R2-F3`, completeness) is unchanged and still
Inc-8's.

### INC7-CR-R3-F3 -- out of scope, not fixed here

The `test_agree_floor.py` `ZeroDivisionError` inside `HomeScreen._sparkline_text`
(`app.py:579`), first surfaced under this file's original "Tests run" section
and reproduced there on unmodified HEAD `0c4215a`. Per the coordinator's
explicit instruction for this round: **not fixed**. It goes to the operator,
not to a further Inc-7 corrective pass -- fixing it would be source change
outside this round's two-item scope (`INC7-CR-R3-F1`, `INC7-CR-R3-F2`) and
outside `app.py` entirely, which this round did not touch.

### Tests run (round 3)

Targeted only, per the coordinator's instruction (`tests/test_vocabulary_declaration.py`
+ `tests/test_repair_cycles.py`; the full lane was not re-run -- no product
code changed, only a test file and a docstring):

```
38 passed
```

(unchanged from the pre-round-3 count -- the two mutants above prove the new
asserts can fail; the unmutated tree, correctly, still passes all 38.)

### Ruff (round 3)

`ruff check --output-format=concise` compared against the same baseline
capture used for the first pass of this increment (27 distinct errors / 29
output lines, unmodified HEAD `0c4215a`): `diff` is **empty**. Zero new
errors, identical set.

## Commits

1. `8eb62d9` -- `fix(sala): Inc-7 corrective pass 2 -- the declared string, derived from the document; the docstring narrowed to what is checked`
2. `e0a17d2` -- `docs(state): Inc-7 corrective pass 2 -- increment record with mutation table and lane figures`
3. `6cbbeff` -- `fix(sala): Inc-7 round 3 -- V22's glyph pin now derives from 01b, not from darkside against itself`
4. This file's round-3 update (docs).

## Next

Round 3's `INC7-CR-R3-F1` and `INC7-CR-R3-F2` are DISCHARGED. `INC7-CR-R3-F3`
(the `_sparkline_text` `ZeroDivisionError`) is unfixed by design this round
and belongs to the operator. Whatever the coordinator schedules after this --
a round 4 confirmation or a close-out -- is the next step; this pass stops at
its own boundary and does not start it. The security lens remains not owed
again: round 3 touched no sink (a test file's parsing/assertions and a
docstring wording fix only).
