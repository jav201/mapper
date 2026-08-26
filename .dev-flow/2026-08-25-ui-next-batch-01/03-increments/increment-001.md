# Increment 1 — US-N03 · one keymap seat, an executing palette, scoped help

## 1 · What changed

**BLUF: the palette went from 0/33 entries dispatching to 39/39, and the reason it was 0 turned out
to be two independent bugs, not one.** The known one was that `KeyBinding.action` held Spanish prose,
so `getattr(screen, f"action_{action}")` could never resolve. The second surfaced only because the
acceptance test presses the real key: **`ctrl+p` never opened mapper's palette at all.**

`mapper/keymap.py` is now the single source of truth. `KeyBinding` carries four separable fields —
`key` (the Textual name that binds), `glyph` (what the operator reads), `action` (the `action_*`
stem that dispatches) and `label` (Spanish prose) — plus a `group`, a `priority` flag and a derived
`scope`. Every screen's `BINDINGS` is generated from the seat by `screen_bindings(scope)`; the
keybar, the palette and the help overlay all read the same seat, filtered to the active screen's
scope.

**The escaped bug.** `MapperApp` set `COMMAND_PALETTE_ENABLE = False`. Textual's attribute is
`ENABLE_COMMAND_PALETTE`; the name the app used is one Textual never reads. So Textual's built-in
command palette owned `ctrl+p` for the whole life of the feature and mapper's palette was
unreachable from the keyboard. The superseded test called `app.action_palette()` directly and so
could not see it. Pre-fix RED is recorded in §4.

Behaviour deliberately changed, and why:
- **Four palette entries removed — two dead, two live-but-orphaned.** *Corrected after review: my
  first draft of this packet said all four were dead, and that was wrong.* Palette `j bajar` /
  `k subir` were genuinely dead (no `action_bajar`/`action_subir` ever existed). But
  `ctrl+s → save` and `tab → toggle_preview` are **live today** on `EditorScreen`
  (`editor.py:23,25`, actions at `:122,:128`). They were removed from the *seat*, not from the app:
  they still work, but nothing advertises them any more. `EditorScreen` is one of the four
  unmigrated screens, so this is recorded as a carry rather than presented as a clean removal.
- **`tab` is no longer bound by anything** (LLR-N06.5). The UX lens measured that a screen-level
  `tab` binding produces 0 focus moves in 9 presses, which would make the inspector keyboard
  unreachable in Inc-2. A unit test now asserts `tab` is absent from the seat.
- **The `f` collision is resolved by scope**: `f fábrica` is home-scope, `f alternar foco` is
  map-scope. Previously both sat in one flat list and only one could ever fire.

## 2 · Files modified

**Source (4 — ⚠ at the cap).**

| File | Change |
|---|---|
| `mapper/keymap.py` | rewritten: 4-field `KeyBinding`, `GROUP_SCOPE`, 39 bindings, `bindings_for`, `textual_bindings`, `palette_items(query, scope)`, `duplicate_chords` |
| `mapper/app.py` | `screen_bindings()`; 5 screens' hand-written `BINDINGS` replaced by generated ones + `KEY_SCOPE`; scope-aware `action_palette`/`action_help`; keybar reads the seat; the `ENABLE_COMMAND_PALETTE` fix |
| `mapper/screens/palette.py` | scope-aware; shows label + glyph; entry count line; `on_input_submitted` so `enter` works while the search box holds focus |
| `mapper/screens/help.py` | scope-aware; renders glyphs, not Textual key names |

*Why it could not be cut smaller:* the seat's shape, its consumers and the dispatch site are one
change — splitting them would leave the tree with screens binding a field that no longer exists.
`mapper/widgets/chrome.py` was moved out of this increment to Inc-3 to stay within the budget.

**Tests (uncapped):** `tests/test_keymap.py`, `tests/test_palette.py` — both rewritten.

## 3 · How to test

```
PYTHONUTF8=1 python -m pytest -q
PYTHONUTF8=1 python -m pytest -q tests/test_keymap.py tests/test_palette.py
```

## 4 · Test results — one complete run, read from its own output

```
132 passed in 10.71s          # whole suite, post-increment
```

**Ledger:** `post = base − D + A` → `132 = 88 − 6 + 50`. Reconciles exactly.
(base 88 on `695bd2d`; deleted the 4 old keymap tests and the 2 old palette tests; added 50.)

**Escaped-bug RED (the `ENABLE_COMMAND_PALETTE` typo), captured before the fix:**
```
FAILED tests/test_palette.py::test_ctrl_p_opens_darkside_palette
FAILED tests/test_palette.py::test_at_n03c_palette_is_scoped_to_the_active_screen
FAILED tests/test_palette.py::test_at_n03b_selecting_a_palette_entry_executes_it
FAILED tests/test_palette.py::test_at_n03b_negative_empty_query_result_dispatches_nothing
4 failed, 46 passed
textual.css.query.NoMatches: No nodes match '#palette-input' on
    CommandPalette(id='--command-palette', classes='--textual-command-palette -ready')
```
The id in that error is Textual's own palette — direct evidence the wrong widget owned `ctrl+p`.

**C-40 counterfactual — executed, per resolved arm.**
Baseline arm count for `AT-N03a`: **39 resolved, 39 passed** (a harness that resolves zero arms
would make its own all-green check compare 0 == 0 and pass, so this is asserted first).

Mutation, described by position and operation rather than pasted: in the seat's `view` group, the
`m` binding's **third field** (the action stem) was replaced by its fourth field (the Spanish
label). Result:

```
FAILED tests/test_keymap.py::test_at_n03a_every_binding_resolves_to_a_real_action[map:m:cobertura]
FAILED tests/test_keymap.py::test_palette_items_filters_by_scope_and_query
FAILED tests/test_palette.py::test_at_n03c_palette_is_scoped_to_the_active_screen
FAILED tests/test_palette.py::test_at_n03b_selecting_a_palette_entry_executes_it
4 failed, 46 passed
```
**Exactly 1 of the 39 `AT-N03a` arms reddened — the mutated one.** The other 38 stayed green, which
is the discrimination a per-arm verdict exists to show; an aggregate exit code could not have said
this.

**Restore, and a trap worth naming.** The first restore attempt reported
`RESTORE FAILED`: sha256 `36d58b6e…` against a pre-mutation `d7cb0d5e…` — while the full suite ran
**132 passed**. The content was correct; Python's text-mode write had translated the whole file
LF→CRLF (213 CRLF, 0 bare LF). Had the green suite been taken as proof, a whole-file line-ending
flip would have shipped in the diff. Normalised back to LF and re-verified:
`sha256 = d7cb0d5e9a302221c1cbacfe6f0168b79414db1f0440999cefccc44c9eb3b035`, matching pre-mutation
byte-for-byte. `__pycache__` was purged and the suite re-run green afterwards (C-46: the green run
*after* the battery is the proof, not the hash alone).

## 5 · Risks

| # | Risk | Status |
|---|---|---|
| 1 | Removing 4 advertised-but-dead keys is a visible behaviour change. | Intended; it is the story. Recorded here so it is not discovered as a regression. |
| 2 | `ctrl+p` and `?` are now non-priority, where `RepoScreen`/`PlugRepoScreen` had them priority. | **My original rationale here was wrong and the reviewer measured it.** I claimed a priority `?` fires before a focused `Input`. On textual 8.2.8 it does not: with an `Input` focused, `screen._binding_chain` comes back with the printable-key binding stripped from *every* namespace, so `_check_bindings` returns `False` and the key falls through to `Input._on_key` — `priority=True` and `priority=False` behave identically (`help_opened=False, value='?'` in both). Dropping priority was a **no-op for that symptom**. The shipped behaviour is still correct, and `escape` on `PlugRepoScreen` still returns home with the input focused — verified, not assumed. |
| 3 | Four modal screens (`FactoryScreen`, `EditorScreen`, `SettingsScreen`, `CoverageScreen`) still hold local `BINDINGS`. | Declared, not hidden: `keymap.UNMIGRATED_SCREENS` names them, and it is a backlog carry. Their help shows app-scope only. |
| 4 | `_ImportPreviewScreen`'s `s` key is now seat-declared; it is a single letter on a screen with no input. | Unchanged from before. |

## 6 · Pending items

- `MapStore.load` raises `KeyError` on a sidecar attachment missing `path:` (security F-M5) — carry.
- `mapper/screens/factory.py:343` imports from `mapper.app` (ARQ A-7) — carry; fixing it silently was rejected.
- The four unmigrated modal screens — carry.

## 7 · Suggested next task

Increment 2 — US-N01: `mapper/widgets/inspector.py`, `mapper/model.py` (the single
missing-required-fields owner), `mapper/app.py` (the taller recompose), `mapper/views/layered.py`
(delete the duplicate ficha strip).

## 8 · Code-review round 2 — the gate that actually caught things

The independent `code-reviewer` returned **blocked** with 5 HIGH findings. It broke the palette
**twice while the suite stayed green**, which is the single most valuable result of this increment.
All five are fixed; each fix is verified by re-running the reviewer's own counterexample.

| # | Finding | Fix | Verification |
|---|---|---|---|
| F1 | `MapperApp.BINDINGS` was the one list that escaped the seat. Its hand-written `q → quit` was bound app-wide, so on the plug and import-preview screens — neither of which declares `q` — pressing `q` **quit the app**, discarding an unsaved import, while palette and help advertised no such key. | `BINDINGS = screen_bindings(SCOPE_APP)`; `q` now quits only in home scope, where it is advertised. | Pilot: `app still running after 'q' on PlugRepoScreen: True`, `screen: PlugRepoScreen`. |
| F2 | `HelpScreen` borrowed the `palette` scope, so it bound `enter → run_selected` — a method it does not define. A silent no-op, invisible to `AT-N03a` because that scope's owner is `CommandPalette`. | New `SCOPE_HELP` with its own two bindings. | Pilot: `HelpScreen has action_run_selected: False`; bound keys `['escape', 'q']`; `esc` dismisses. |
| F3 | The completeness fence was `>= 33` against 39 declared — **6 bindings of slack**. Deleting 6 map bindings gave `126 passed, 0 failed` while the palette silently lost `f`, `o`, `r`, `e`, `=`, `x`. | Exact per-scope counts in `EXPECTED_PER_SCOPE`. | Counterfactual A re-run: the same 6 deletions now give `FAILED test_keymap_completeness_guard — 1 failed, 52 passed`. |
| F4 | `AT-N03a` checked the `action` field only — never `key`, never `glyph`. Corrupting a glyph kept the suite at **132 green** while help, palette and keybar all advertised a chord that does nothing. | Two new tests: bound-keys-match-the-seat (reading Textual's real merged bindings, with the framework's own contribution subtracted **derived from the base class**, not hand-listed), and glyph fidelity. | Counterfactual B re-run: the same glyph corruption now gives `FAILED test_glyph_is_a_plausible_display_form_of_its_key`. |
| F5 | `test_llr_n06_5_no_screen_binds_tab` asserted a universal that is **false in the tree** — `settings.py:52` and `editor.py:25` both bind `tab`. | Split into the seat half and a real tree walk over every `Screen` subclass, with `TAB_BINDING_EXCEPTIONS` naming the two known offenders, plus a fence asserting those exceptions are still real. | Both tests green; a new `tab` binding on any other screen now reddens. |

Medium and low findings also applied: `duplicate_chords` gained a **positive control** (gutting its
body to `return []` previously left the suite green); `KEY_GROUPS` was deleted in favour of a derived
`keybar_groups()`; all three keybar call sites now use one convention; `UNMIGRATED_SCREENS` stopped
being decoration and is now the exception list two tests quantify over; the modal-scope policy moved
into the seat as `MODAL_SCOPES` so screens and tests read one source instead of each passing a flag.

**A process failure of my own, recorded rather than tidied away.** Reverting counterfactual A, I mixed
`git stash` and `git checkout --` on a dirty tree; the stash was consumed and **the mutation was not
reverted** — the six bindings stayed deleted. The suite still reported mostly-green, so only the
sha256 check caught it. The file was repaired by re-inserting the six lines and re-verified to
`ddb71dc86c481db5d6d2a60b757a9fa81a87becc1a12210fe8603de47a14c07c`. Every later counterfactual used
the same write-and-revert mechanism in both directions, never git. This is the second time in one
increment that a hash check caught something a green suite hid.

**Honesty note on this round:** the fixes were verified by me re-running the reviewer's own
counterexamples and two fresh pilots. They were **not** re-confirmed by an independent second review
pass. Post-fix suite: **146 passed**.

## Evidence checklist

- ✓ Tests pass — `132 passed in 10.71s`, one complete run, §4.
- ✓ No secrets in code or output — no credential, token or path outside the repo appears in the diff.
- ✓ No destructive command run without approval — the only mutation was the C-40 counterfactual, reverted and hash-verified (§4).
- ✓ File count within cap — 4 source files, at the cap, with the reason stated in §2.
- ✓ Review packet attached — this document.
- ✓ Frozen interfaces untouched — `IRenderer.render`, `MapStore`, `Graph` do not appear in the diff (`git diff --stat`: only `keymap.py`, `app.py`, `screens/palette.py`, `screens/help.py` + 2 test files + the module map).
- ✓ Counterfactual executed per arm, restore hash-verified — §4.
- ✓ Nothing under `prototypes/` modified or staged — `git status` shows it untracked-as-found.
