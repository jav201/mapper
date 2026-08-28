# Code Review — Increment 002 — NARROW SECOND CONFIRMATION over the retraction

| Field | Value |
|---|---|
| Reviewer | `code-reviewer` (independent) — third pass, narrow scope |
| Batch | `2026-08-26-ui-next-batch-02` · branch `feat/ui-next-batch-02` · base `4eaba35` |
| Scope | the `A-96` retraction of `B-51`, plus the `N-M3` / `N-M1` / `N-M4` / `N-M6` repairs |
| Judging | `increment-002.md` §10 and `increment-002-code-review-confirmation.md` |
| Date | 2026-08-28 |
| **Verdict on the retraction** | **RETRACTION CORRECT** |
| **Gate** | **PASSES** — no HIGH. 2 MEDIUM and 4 LOW, all record-accuracy or test-hygiene |

---

## BLUF

**`B-51` was never a defect, and I reproduced that from scratch with my own probe at five terminal
sizes rather than replaying the author's.** At 80 × 24 `_apply_region_visibility` sets
`rail_hidden=True` **and** `inspector_hidden=True`, both regions get `display=False`, and
`MapScreen.focus_chain` is legitimately empty — `tab` has nowhere to go, so Textual's `_move_focus`
falls to `set_focus(None)` and the owner reads `""`. At 118 × 34 the chain is populated and
`LLR-CNV.3.1`'s threshold reproduces verbatim: press 1 → `rail`, press 2 → `inspector`. The
declared-context anchor is real and long predates the retraction. **Nothing of `B-51` should stay
carried.**

**I did not take the causal story on trust.** Three product mutants decide it, and all three landed
where the retraction predicts: disabling the auto-hide entirely (`if False:`) reddens the size arm and
leaves the 118 × 34 traversal arm **green** — so the traversal is not an artifact of the auto-hide;
raising `MIN_CANVAS_WIDTH` to 90 (which hides the regions at 118 too) reddens the traversal arm — so
region visibility is exactly the variable that decides the answer.

**All four repairs are genuinely fixed**, each mutation-verified against the specific state it claims
to forbid: 11 mutants in battery 1 and 7 escape shapes in battery 2, **18 of 18 matching prediction**,
sha256 restore clean on all five watched files.

**What I do find is a fourth instance of the class this whole thread is about.** The retraction's own
headline evidence table — reproduced in `A-96`, in §10, and in the test's docstring — publishes
`owners[0] = 'rail'` at 118 × 34. Measured over 25 runs, that pre-state is **race-dependent**: it is
`'rail'` 23/25 times with the arm's one `pilot.pause()` and `''` 25/25 once the screen settles. So the
table's first column records an unsettled state, and as published it reads as though the first `tab`
did nothing — inside the amendment written to stop measurements being published without their
conditions. The conclusion is right; the exhibit is one pause short.

---

## Environment and integrity

| Control | Evidence |
|---|---|
| No file under `mapper/`, `tests/`, `docs/` edited | real-repo `git status --short` byte-identical to the state received (21 tracked entries + 3 untracked, unchanged); `fixtures/` appears in no status line and in no diff |
| No mutating git command in the real repo | `git worktree list` in the repo → the repo alone. The one worktree I created was **inside the mirror** (`mirror/../wt4eaba35`) and is removed; `git worktree list` in the mirror now shows the mirror alone |
| Mutations | a full copy of the working tree (including `.git`, so `git ls-files` behaves) under the session scratchpad, `PYTHONDONTWRITEBYTECODE=1`, restored from in-memory bytes — never `git checkout`, which in this tree would have reverted the increment to `4eaba35` |
| Live-app probes | every probe built its own `tempfile.mkdtemp()` workspace; no `MapperApp` was ever pointed at the repo's `fixtures/` |
| Post-battery control | mirror restored → the 7 target arms green; full suite `719 passed` |

### Current state — reproduced, not accepted

| Claim | Reproduced |
|---|---|
| fast `719 passed, 17 deselected` | ✓ `719 passed, 17 deselected in 60.82s`, and four more times under 4-way parallel load |
| slow `17 passed` | ✓ `17 passed, 719 deselected in 23.94s` |
| ruff `mapper/ tests/` = **28** | ✓ `Found 28 errors.` — exactly the `4eaba35` baseline |
| `ruff check fixtures/` clean | ✓ — and still vacuous: `warning: No Python files found under the given path(s)`. `N-L1` was conceded and is labelled; no action |
| Ledger `736 = 711 + 25`, 0 removed | ✓ **derived myself**, node-id diff of `--collect-only -m ""` against a `4eaba35` worktree: base 711, now 736, `comm -23` (removed) **empty**, `comm -13` (added) **exactly 25** — 15 in `test_a3_census.py`, 5 in `test_app.py`, 3 `AT-010` arms in `test_layered.py`, 2 derived `[state.py]` arms in `test_repair_artifact_claims.py`. Matches §4's table line for line |

---

## THE CLAIM — verified independently

My probe (`tempfile.mkdtemp()` per app, five sizes, six `tab` presses each, sampling
`screen.focus_chain`, `app.focused`, and every `can_focus` widget's real `focusable`):

```
SIZE (80,24)   rail_hidden=True  inspector_hidden=True
  focus_chain : []
  owners      : ['', '', '', '', '', '', '']          focused ids: [None]*7
SIZE (100,30)  rail_hidden=True  inspector_hidden=False
  focus_chain : ['insp-title','insp-state','insp-notes']
  owners      : ['', 'inspector', 'inspector', ...]
SIZE (110,30)  same as 100x30
SIZE (118,34)  rail_hidden=False inspector_hidden=False
  focus_chain : ['map-rail','insp-title','insp-state','insp-notes']
  owners      : ['', 'rail', 'inspector', 'inspector', 'inspector', 'rail', 'inspector']
  focused ids : [None,'map-rail','insp-title','insp-state','insp-notes','map-rail','insp-title']
SIZE (140,45)  identical to 118x34
```

### 1 · Is the 80 × 24 empty chain `_apply_region_visibility` doing its job, or a real defect the wide size masks?

**It is the function doing its job. There is no defect underneath, and I proved that by mutating the
product rather than by reading the code.**

The arithmetic is exact and both limbs fire at 80 columns (`RAIL_WIDTH` 24, `INSPECTOR_WIDTH` 36,
`MIN_CANVAS_WIDTH` 58): `80 − 24 − 36 = 20 < 58` hides the rail, and `80 − 36 = 44 < 58` hides the
inspector. My probe reads back exactly that state — `rail_hidden=True, inspector_hidden=True` — and
the chain is empty because both regions carry `display=False`, which prunes them and their children
from `Screen.focus_chain` (Textual walks `displayed_children`).

The intermediate band is the control that makes this a measurement rather than an assumption: at
100 × 30 and 110 × 30 **only** the rail is hidden, and the chain is exactly the three inspector fields.
The chain tracks region visibility monotonically, which is what a working auto-collapse looks like.

Three mutants close it:

| Mutant | Arm | Verdict | Reading |
|---|---|---|---|
| auto-hide disabled (`if not self._regions_pinned:` → `if False:`) | `test_the_focus_chain_is_a_function_of_terminal_size` | **RED** | the empty chain at 80 × 24 is *caused* by the auto-hide, not merely correlated |
| the same mutant | `test_llr_cnv_3_1_focus_owner_tracks_the_real_focus` | **GREEN** | the 118 × 34 traversal is **not** an artifact of the auto-hide — it survives the auto-hide's removal |
| `MIN_CANVAS_WIDTH` 58 → 90 (regions now hidden at 118 too) | `test_llr_cnv_3_1_focus_owner_tracks_the_real_focus` | **RED** | region visibility is the whole variable; make 118 narrow-by-definition and the "defect" returns |

The second and third rows together are the argument. If a real traversal defect were being masked by
width, removing the auto-hide would not leave the traversal arm green, and re-imposing hiding at 118
would not be sufficient to recreate the symptom. Both hold.

### 2 · Does `tab` at 118 × 34 satisfy `M-10` as written?

**Yes, exactly.** Keyboard-only, no `.focus()` anywhere in my probe:

```
press 1 -> app.focused = 'map-rail'    _focus_owner() = 'rail'
press 2 -> app.focused = 'insp-title'  _focus_owner() = 'inspector'   <- the inspector's FIRST field
press 3 -> 'insp-state'   press 4 -> 'insp-notes'   press 5 -> wraps to 'map-rail'
```

`M-10`'s "after 1 real `tab` from the canvas the field reads `rail`; after 2, `inspector`" reproduces
verbatim, and `insp-title` is genuinely the inspector's first field, not merely an inspector-owned one.
Identical at 140 × 45.

One qualification, which I raise as **F2/F3** below rather than as an objection: the requirement's
literal pre-state — *"from the canvas"* — is unreachable, because `#map-canvas` is `can_focus=False`
(declared as `B-53`). Both the arm and my probe substitute *nothing focused*, which is the sound
proxy (both yield owner `""`, and both enter `_move_focus` at chain index 0). The substitution is
correct; it is simply not declared anywhere.

### 3 · Is 118 × 34 legitimately the declared context of use?

**Yes, and the anchor is strong, plural, and predates the retraction by several artifacts** — so the
retraction is not resting on a size chosen after the fact to make an answer come out.

| Source | Line | Text |
|---|---|---|
| `PDR-addendum-3.md` | `:232` | `C-D27c` — **the arm runs at 118 × 34, the declared context of use, per `A-69`** |
| `PDR-addendum-3.md` | `:398` | the `C-D27e` legibility arm, also added at 118 × 34 |
| `01-requirements.md` | `:30` | the user story itself: *"reading a 128-node legacy map on a **118-column** terminal"* |
| `01-requirements.md` | `:3153` | *"**the declared context of use is 118 x 34**"* — stated as the batch-level default, correcting two arms that had declared 140 × 45 |
| `01-requirements.md` | `:3139` | *"declared context of use **118 × 34**"* |
| `01-requirements.md` | `:7515` | `A-69`, the amendment `C-D27c` cites: *"the arm runs at **118 x 34**"* |
| `01-requirements.md` | `:686` | `HLR`-level statement: *"a terminal **at least 118 columns wide**"* |

The decisive one is `:160`, written long before this increment:

> the test must drive a **wide** Pilot size, because the size is precisely what the 245-test suite was
> blind to (`_apply_region_visibility` hides the rail below ~118 columns, so the suite exercises only
> the sizes at which the bug is absent — **C-55 limb 2**)

**The batch had already recorded, in its own requirements, that `_apply_region_visibility` hides the
rail below ~118 columns and that a suite pinned to one size sees only what that size shows.** That
makes the retraction's diagnosis a rediscovery of the batch's own written finding, not a new theory —
which is about as good as corroboration gets, and it is also the sharpest indictment of the three
passes that missed it. `A-96`'s framing of this as `P-20` inverted is accurate.

### 4 · Is the retraction over-broad? Does anything remain that should stay carried?

**No — nothing of `B-51` should stay carried, and the second reviewer's stated root cause does not
survive its own measurement once the size is varied.** But two of its supporting details need
correcting so they are not carried forward as facts.

**(a) "Five widgets report `can_focus=True`" is not right — it is four, plus one that is deliberately
not focusable.** My per-widget reading at every size:

```
map-rail      display=False@80  visible=True  disabled=False  focusable=True
insp-title    display=True      visible=True  disabled=False  focusable=True
insp-state    display=True      visible=True  disabled=False  focusable=True
insp-notes    display=True      visible=True  disabled=False  focusable=True
search-input  display=False     visible=True  disabled=True   focusable=FALSE   <- at EVERY size
```

`search-input` reports `can_focus=True` on the class but `focusable=False` on the instance:
`on_mount` sets `display=False` and `disabled=True` (`app.py:1167-1169`), and the CSS agrees
(`#search-input { dock: bottom; display: none; }`, `app.py:2042`). It is the `/` search box and it is
**correctly** absent from the chain until summoned. Verified reachable and correct:

```
chain before '/' : ['map-rail','insp-title','insp-state','insp-notes']
after '/'        : display=True disabled=False focusable=True  focused='search-input'
chain after '/'  : ['map-rail','insp-title','insp-state','insp-notes','search-input']
```

So the "5 vs 0" gap that reads as alarming is really "4 focusable widgets, all pruned by hidden
ancestors, plus 1 correctly dormant". **Nothing to carry.** Recorded here so the number `5` does not
propagate.

**(b) `map-rail.focusable == True` while `display == False` — real, but not operator-reachable, and it
is a test-hygiene issue rather than a product one.** Textual's `Widget.focusable` consults
`visible` (a `visibility` check) and ignores `display`, so at 80 × 24 code *can* focus the auto-hidden
rail even though the keyboard cannot:

```
80x24  rail.display=False  rail.focusable=True  (in focus_chain: False)
       after rail.focus():  _focus_owner()='rail'   app.focused='map-rail'
       after action_toggle_rail(): rail.display=True  chain=['map-rail']
```

`_focus_owner()` will then report a region that is not on screen, and the canvas will paint the
*inactive* selection tone with no visible cause. The operator cannot get there — `tab` cannot reach a
pruned widget, and `g`/`action_focus_rail` un-hides the rail before focusing it (`app.py:1254-1256`).
**Two arms in this increment do get there**, because they run at the default 80 × 24 and call
`.focus()` directly. That is **F5** below, and fixing F5 removes the only way in. Not a product carry.

**(c) `B-54` is the right carry and it is correctly worded.** It generalises the lesson without
re-asserting the phantom.

---

## The four fix confirmations

Battery 1 — 11 mutants over the mirror, baseline green, sha256 restore verified on `app.py`,
`ARCHITECTURE.md`, `test_app.py`, `test_a3_census.py`, `test_repair_map_truth.py` after every mutant.
Battery 2 — 7 escape shapes. **18 of 18 matched prediction; the post-control returned green.**

### `N-M3` — `test_b50_the_export_carries_the_diff_the_canvas_is_showing` — **PROPERLY FIXED as coverage; it does NOT drive the real `e` key**

**Does the new arm actually cover the behaviour?** Yes, and it is the arm §6 should always have had.
Three mutants of `mapper/app.py::_view_state` / `action_export_svg`, each run against this node alone:

| Mutant | Verdict |
|---|---|
| `diff=self.diff if self.diff_active else None` → `diff=None` — the exact under-fill `#D4` exists to prevent | **RED** |
| `query=self.query_text` → `query=""` | **RED** |
| the export stops pinning `focus_owner=""` (the `replace(...)` wrapper removed) | **RED** |

The first is decisive: the confirmation pass measured `716 passed` on the **full suite** with that same
mutation. It now reddens on the arm. `N-M3` is discharged and §6's "covered" is earned.

**Does it drive the real `e` key? No.** `tests/test_app.py:399` calls `screen.action_export_svg()`
directly. `N-M5`'s repair landed on the *other* export arm — `test_an_export_never_encodes_where_the_
keyboard_was:337` now correctly does `await pilot.press("e")` — but the new `B-50` arm was written in
the same pass with the old shape, and its own assertion message says *"the shipped export never
reached the renderer"*. See **F4**. It is one line and the key path is already proven to work, so this
is hygiene, not false confidence: the arm's three assertions are about state construction and all
three discriminate.

### `N-M1` — the map-truth guard — **PROPERLY FIXED, both regressions caught, no false-fail**

`tests/test_repair_map_truth.py:170-176`, now `assert "NOT PRESENT" not in row and "NOT YET IN THE
TREE" not in row` with the backstop tightened to `assert "· **PRESENT**" in row`.

| Mutant on the `ViewState` row in `docs/ARCHITECTURE.md` | Verdict |
|---|---|
| **full phrase** — `· **COMMITTED, NOT PRESENT**` (the original H1 regression) | **RED** |
| **short phrase** — `· **NOT PRESENT**` (the `N-M1` escape; **GREEN** before this fix) | **RED** |
| `· **NOT YET IN THE TREE**` (the third phrasing the guard names) | **RED** |
| **legitimate content edit** — the roster description gains `hits` | **GREEN** ✓ no false-fail |

Both regressions are caught and the legitimate row edit passes. The tightened backstop is what closes
the near-vacuity: `"PRESENT" in row` was satisfied by the `PRESENT` inside `NOT PRESENT`;
`"· **PRESENT**" in row` is not.

### `N-M4` — `test_llr_cnv_3_1_the_parent_walk_maps_a_nested_widget_to_its_region` — **PROPERLY FIXED; it reddens now**

The confirmation pass measured `_focus_owner` **stops walking parents** → **GREEN**. Under the same
mutation (`node = getattr(node, "parent", None)` → `node = None`, so the loop cannot climb):

```
tests/test_app.py::test_llr_cnv_3_1_the_parent_walk_maps_a_nested_widget_to_its_region  FAILED
```

**RED.** `#insp-title` is a child of `#map-inspector`, so resolving it to `"inspector"` requires the
climb, and the arm asserts its own precondition (`assert title.id != "map-inspector"`) so it cannot
degenerate into a first-iteration hit. The docstring downgrade on `_expected_owner` — *"a
TRANSCRIPTION, not an independent oracle"*, naming exactly which mutants it does and does not catch —
is the honest wording, and it is now true of the code it describes.

### `N-M6` — threshold 3's two remaining escapes — **BOTH PROPERLY CLOSED**

Six shapes appended to a **tracked** file (`tests/test_export.py`) and two files created **untracked**,
each run against the census:

| Escape | Arm | Verdict |
|---|---|---|
| `renderer.render(*opts)` — **`*` splat**, the open one | threshold 3 | **RED** |
| `renderer.render(g, **opts)` — `**` splat | threshold 3 | **RED** (regression control) |
| `renderer.render(g, sel, 80, 24)` — positional old shape | threshold 3 | **RED** (regression control) |
| `renderer.render(g, selected_id=sel, w=80, h=24)` — old keyword | threshold 3 | **RED** (regression control) |
| **untracked `tests/` file** with an old-shape call, the open one | invisibility arm | **RED** |
| untracked `mapper/views/` file with an old-shape `def render` | invisibility arm | **RED** |
| *(control)* untracked `tests/` file, judged by threshold 3 alone | threshold 3 | **GREEN** — blind by design; the invisibility arm is the net, and it holds |

The `*` ban at `test_a3_census.py:220-223` carries the same reasoning as the `**` ban and is correct:
the arity is not statically knowable, so the site is unauditable and banning beats silently passing
over. The invisibility arm's `for root in ("mapper", "tests")` at `:50` closes the second. The last
row is the one worth keeping: threshold 3 alone still cannot see an untracked file, so the two arms
are load-bearing **together** — which is why the last mutant's GREEN is a correct result and not a
hole.

---

## New findings

### F1 — the retraction's own evidence table publishes a race-dependent pre-state  [MEDIUM]

- **Where:** `01-requirements.md` `A-96` (`:8039`), `increment-002.md` §10 (`:333`),
  `tests/test_app.py:137-139` — the same table in all three.
- **What:** the table publishes, at 118 × 34, `owners = ['rail','rail','inspector','inspector','inspector']`.
  Measured, 25 runs per condition:

  ```
  one  pilot.pause() after push_screen (what the arm does):
        23/25  ['rail','rail','inspector','inspector','inspector']
         2/25  ['',    'rail','inspector','inspector','inspector']
  two  pilot.pause() (screen settled):
        25/25  ['',    'rail','inspector','inspector','inspector']
  ```

  The mechanism: `MapScreen.on_mount` schedules `call_after_refresh(self._park_focus)`
  (`app.py:1208`), and `_park_focus` is `self.set_focus(None)` (`app.py:1265-1267`), while Textual's
  `AUTO_FOCUS` has already focused `#map-rail`. Sampled one pause in, the screen is usually still in
  the `AUTO_FOCUS` state; a pause later `_park_focus` has landed and the settled owner is `""`.
- **Why it matters:** as published, index 0 says the rail already held focus and index 1 says it still
  does — so the exhibit cited to prove *"press 1 gives `rail`"* reads, on its face, as *the first tab
  did nothing*. A reader checking the retraction against its own table finds them in tension. This is
  the same class as `H3` and `N-M2` — a measurement published beyond the conditions under which it was
  taken — occurring **inside the amendment written to correct that class**, which is why it is worth a
  MEDIUM rather than a nit. The retraction's *conclusion* is unaffected: I reproduced it from the
  settled state, which is the stronger reading.
- **Suggested fix:** publish the settled row and name the transient, in all three places:

  ```
  118 x 34   chain=['map-rail','insp-title','insp-state','insp-notes']
             owners=['', 'rail', 'inspector', 'inspector', 'inspector']
             (index 0 is '' once `_park_focus` has landed; sampled one pause after
              push_screen it is still AUTO_FOCUS's 'rail' -- see F2)
  ```

### F2 — the `LLR-CNV.3.1` arm does not assert its own pre-state, and passes on an undeclared race  [MEDIUM]

- **Where:** `tests/test_app.py:164-180`.
- **What:** the arm samples `seen[0]` and then asserts only `seen[1] == "rail"` and
  `seen[2] == "inspector"`. In the 23/25 ordering above, `seen[0]` is `'rail'` — the rail already has
  focus — and `seen[1] == "rail"` holds **only because `_park_focus` lands between the sample and
  `pilot.press("tab")`**, resetting focus to `None` so the tab enters the chain at index 0. Were
  `_park_focus` ever to land *after* the first tab, the tab would move `map-rail → insp-title` and
  `seen[1]` would be `'inspector'`: the arm fails, for a reason with nothing to do with
  `LLR-CNV.3.1`.
- **Not a false-confidence test.** The pair of assertions still discriminates — a `tab` that did
  nothing while the rail held focus would give `seen[2] == 'rail'` and fail — and the arm is
  mutation-proven sensitive to the real variable (`MIN_CANVAS_WIDTH` → 90 reddens it). I stressed it
  hard and found no flake: **8 sequential node runs + 10 executions under 4-way full-suite load +
  50 probe replays, zero failures**, and all four background suites returned `719 passed`. This is a
  fragility finding, not a vacuity one.
- **Why it matters anyway:** this batch has already paid twice for an arm that passed on an unstated
  timing premise (§8's flaky arm, §9's `M1`), and `A-96`'s whole lesson is *"three independent passes
  agreeing is not evidence when they share an unstated premise"*. An arm that is stable by accident
  rather than by construction is the same shape one size smaller.
- **Suggested fix** — one extra settle and one assertion, which also makes `F1`'s table true and
  discharges `F3`:

  ```python
  await pilot.pause()          # let `_park_focus` land before sampling
  assert app.focused is None, "the pre-state must be settled, not AUTO_FOCUS's transient"
  seen = [screen._focus_owner()]
  assert seen[0] == "", (
      "LLR-CNV.3.1's pre-state is 'from the canvas'; `#map-canvas` is can_focus=False "
      "(B-53), so 'nothing focused' is the reachable equivalent -- both give owner '' "
      "and both enter _move_focus at chain index 0"
  )
  ```

### F3 — `"from the canvas"` is silently modelled as `"nothing focused"`  [LOW]

- **Where:** `tests/test_app.py:176-180`; `LLR-CNV.3.1`'s statement.
- **What:** the requirement's pre-state is unreachable (`#map-canvas` is `can_focus=False`, `B-53`).
  The arm substitutes the no-focus state without saying so. The substitution is sound and I verified
  the equivalence, but this is precisely the kind of unstated premise `A-96` was written about, and
  `N-H1` flagged the unreachability without it being recorded anywhere afterwards.
- **Suggested fix:** the assertion message in `F2` closes this; no separate change needed.

### F4 — the new `B-50` arm does not drive the real `e` key  [LOW]

- **Where:** `tests/test_app.py:399`, `screen.action_export_svg()`; the arm's own failure message at
  `:402` says *"the shipped export never reached the renderer"*.
- **What:** `N-M5` was fixed on the sibling arm (`:337` is now `await pilot.press("e")`) but the arm
  written in the same pass kept the direct call. C-16's gloss names *"a direct `action_*` call"*
  alongside `.focus()`, and export **is** promised as a keystroke (`keymap.py:118`).
- **Why it is only LOW:** the mechanism this arm is about is state construction, its three assertions
  all discriminate (3/3 mutants RED), and the `e` binding is covered by the sibling arm. But two arms
  in one file now answer the same C-16 question differently, and the drift will read as an oversight
  later.
- **Suggested fix:** `await pilot.press("e")` in place of `screen.action_export_svg()`. The `_current_renderer`
  spy is already installed at that point, so nothing else changes. **Verified free:** I confirmed the
  real `e` key reaches the writer with the rail focused and with focus parked.

### F5 — three of this increment's new arms still run at the default 80 × 24  [MEDIUM]

- **Where:** `tests/test_app.py:203` (`..._the_parent_walk_...`), `:304`
  (`..._an_export_never_encodes_...`), `:368` (`test_b50_...`) — all `app.run_test()` with no `size=`.
- **What:** the increment raised **`B-54`** — *"Every Pilot-driven interaction assertion must DECLARE
  its terminal size"* — and then shipped three new interaction arms that do not. At 80 × 24 both side
  regions are auto-hidden, so:
  - the parent-walk arm focuses `#insp-title` inside a `display=False` `#map-inspector`;
  - the export arm's precondition focuses a `display=False` `#map-rail` (`focusable` ignores
    `display`, per §4(b) above).

  Both are states **no keyboard can reach at that size**, so each arm establishes its precondition
  through the one door the retraction just proved is misleading. Both arms are still correct and both
  are mutation-proven RED, so this is hygiene — but it is the increment's own new carry, violated by
  the increment's own new arms, on the same day it was written.
- **Suggested fix:** add `size=(118, 34)`. **Verified free:** I patched all 8 bare `run_test()` calls
  in `tests/test_app.py` to `size=(118, 34)` in the mirror — `13 passed`, identical to baseline — then
  restored. No arm depends on the narrow size except `test_the_focus_chain_is_a_function_of_terminal_size`,
  which declares both sizes explicitly and is the point.

### F6 — §9's `H2` mechanism, *"the rail holds focus on mount"*, is a transient  [LOW]

- **Where:** `increment-002.md` §9 `H2` row; `mapper/app.py:1795-1797`; `tests/test_app.py:287-288`.
- **What:** `_park_focus` deliberately parks focus at `None` after mount, and my settled measurement is
  owner `''` at **every** size. The rail holds focus only in the window between `AUTO_FOCUS` and
  `_park_focus` — the same window as `F1`.
- **The `H2` defect and its fix are entirely real; only the stated route is wrong,** and the true route
  is better. Measured keyboard-only at 118 × 34, no `.focus()`:

  ```
  settled owner: ''
  press 'tab' -> owner='rail'  focused='map-rail'
  press 'e'   -> reached the writer: True
                 exported tone == FOCUSED tone : True
                 focused vs inactive tones differ : True
  ```

  So `tab` then `e` — or `g` then `e`, `keymap.py:124` binds `g` → `focus_rail` — is a plain operator
  sequence that would have shipped an SVG in the inactive tone without the `replace(..., focus_owner="")`
  pin. **The fix is load-bearing on a reachable path**, which is a stronger justification than the one
  recorded.
- **Suggested fix:** replace *"the rail holds focus on mount"* with *"`tab` (or `g`) moves focus to the
  rail, after which `e` still exports"* in the §9 row, the source comment, and the test docstring.

---

## What I confirm about §10's own self-assessment

- **The `P-20`-inverted framing is exactly right, and better-founded than §10 claims.** The batch had
  already written down at `01-requirements.md:160` that `_apply_region_visibility` hides the rail below
  ~118 columns and that the suite was therefore blind. The retraction is not a new theory; it is the
  batch's own recorded finding, applied to a place three passes forgot to apply it.
- **"Three independent passes agreeing is not evidence when they share an unstated premise"** is the
  right lesson and I could not have improved on it. It also predicts `F1` and `F2`, which is why I
  raise them rather than let them ride: the premise there is `_park_focus` winning a race, and it is
  still unstated.
- **Round 11's six mutants are real and I re-derived four of them independently** (constant owner and
  the parent walk via `N-M4`; the export dropping `diff` via `N-M3`; the map row's shorter phrasing via
  `N-M1`; the `*` splat via `N-M6`). I add three of my own on the retraction's causal claim — the two
  auto-hide mutants and `MIN_CANVAS_WIDTH` → 90 — which round 11 does not contain and which are the
  ones that actually decide whether a defect is hiding under the wide size.
- **Retracting a recorded defect on your own measurement was the right call and the evidence carries
  it.** Three earlier readings agreed and were wrong together; refusing to add a fourth agreement is
  the correct instinct, and the `B-54` generalisation means the batch keeps the lesson without keeping
  the phantom.

---

## Evidence checklist

- [✓] **Diff read in full** — `mapper/app.py:1120-1260, 1340-1410, 1778-1807`; `tests/test_app.py:1-442`
      entire; `tests/test_a3_census.py:42-60, 198-232`; `tests/test_repair_map_truth.py:150-176`;
      `docs/ARCHITECTURE.md:159`; `increment-002.md` and the confirmation pass entire.
- [✓] **Correctness pass** — five terminal sizes probed with a fresh instrument, per-widget
      `display`/`visible`/`disabled`/`focusable` captured, six `tab` presses each, `focus_chain` and
      `app.focused` read at every step; the `/` search path and the `escape` path traced (the empty
      chain after `escape` is the screen being popped to `HomeScreen`, not a defect).
- [✓] **Causality tested, not assumed** — auto-hide disabled, and `MIN_CANVAS_WIDTH` raised, in both
      directions against both arms.
- [✓] **Simplicity pass** — no premature abstraction in the repairs. `_view_state` + `replace(...)` is
      the minimal correct shape; the census's `elif` chain is readable and each branch carries its
      reason.
- [✓] **Reuse / duplication** — no new duplication introduced by the retraction's arms.
- [✓] **Tests reviewed for intent** — 18 mutants across two batteries, 18/18 matching prediction,
      sha256 restore verified on 5 files after every mutant, post-control green.
- [✓] **Ledger derived independently** — node-id `comm` diff against a `4eaba35` worktree: 711 → 736,
      0 removed, 25 added, all enumerated.
- [✓] **Stress** — 8 sequential runs of the focus/export arms, 10 more under 4-way full-suite load,
      50 probe replays; zero failures.
- [✓] **Repo integrity** — real repo `git status` unchanged, no worktree left behind, `fixtures/`
      untouched, every live app on `tempfile.mkdtemp()`.
- [✓] **Verdict explicit** — below.

---

## Verdict

### On the retraction

**RETRACTION CORRECT.** `B-51` was never a defect. The 80 × 24 empty focus chain is
`_apply_region_visibility` working exactly as specified — both side regions auto-hidden below
`MIN_CANVAS_WIDTH`, so `focus_chain` is legitimately empty and `tab` has nothing to traverse — and
there is no defect underneath it that the wide size masks, which I established by mutating the
auto-hide in both directions rather than by inspection. `LLR-CNV.3.1`'s threshold reproduces verbatim
at 118 × 34, which is unambiguously this batch's declared context of use across seven artifacts
including the user story itself. The retraction is **not over-broad**: the second reviewer's
`focus_chain == []` was a true measurement with a false root cause, its "five focusable widgets" is
really four-plus-one-deliberately-dormant, and nothing in it should stay carried. `B-54` is the right
generalisation and is correctly worded.

### On the four fixes

| Finding | Confirmed | Evidence |
|---|---|---|
| `N-M3` | **FIXED** — real coverage; **does not** drive the real `e` key (**F4**) | 3/3 mutants RED, incl. the `diff=None` the full suite absorbed |
| `N-M1` | **FIXED** | full phrase RED, short phrase RED, third phrasing RED, legitimate row edit GREEN |
| `N-M4` | **FIXED — it reddens now** | the exact mutation the prior pass measured GREEN is RED |
| `N-M6` | **FIXED, both halves** | `*` splat RED, untracked `tests/` file RED, four regression controls RED |

### Gate

- [ ] OK to advance
- [x] **OK with the listed fixes applied first** — none blocking; `F1`, `F2`, `F5` recommended in the
      same pass because all three are the same class and all three are cheap
- [ ] Block

**No HIGH. The increment passes the gate.** `N-H1` is genuinely dissolved rather than papered over —
the unreachable-threshold xfail is gone, and what replaced it is a directly-asserted threshold that a
product mutation reddens. The A3 itself I found no reason to re-open: 719 fast, 17 slow, ruff exactly
28 with zero new, ledger `736 = 711 + 25` with 0 removed, all derived under my own hand.

The two MEDIUMs are worth fixing before this closes, and they are the same finding twice: **`F1`** (the
retraction's headline table publishes a pre-state that is one `pilot.pause()` from being true) and
**`F2`** (the arm that table describes never asserts that pre-state, and passes because `_park_focus`
wins an undeclared race). Both are the class `A-96` exists to name, appearing inside `A-96` — which is
not a reason to distrust the retraction, but is a reason to finish it. **`F5`** is the increment's own
`B-54` applied to the increment's own new arms, and I verified the fix costs nothing.

**Recommended order:** `F2` (which discharges `F1` and `F3` with it) → `F5` → `F4` → `F6`.
