# Code Review — Increment 002 — CONFIRMATION PASS over the post-fix tree

| Field | Value |
|---|---|
| Reviewer | `code-reviewer` (independent) — confirmation pass, second reviewer |
| Batch | `2026-08-26-ui-next-batch-02` · branch `feat/ui-next-batch-02` · base `4eaba35` |
| Judging | `increment-002-code-review.md` (BLOCK, 3 HIGH / 6 MED / 4 LOW) against `increment-002.md` §8–§9 |
| Date | 2026-08-28 |
| **Verdict** | **BLOCK — the three original HIGH are all genuinely discharged, but one NEW HIGH was introduced by the M2 fix** |

---

## BLUF

**All three blocking HIGH findings are discharged, and I proved each one rather than accepting it.**
H1's guard now reddens on the exact regression it names; H2's export is genuinely focus-independent
through the shipped action and the arm fails without the fix; H3's three counts (34 / 25 / 7) are
correct — I re-derived every one with my own instrument, off the filesystem rather than off
`git ls-files`.

**The increment is blocked on one thing the fixes introduced.** The M2 repair replaced a loose
assertion with a `strict=True` xfail whose docstring — and the recorded requirement amendment `A-94`
that quotes it — claim it "fails loudly the day traversal is fixed". Executed under a simulated
B-51 repair: **it stays red, so the alarm never fires.** That is the H1 class one level up — a guard
that cannot fire on the event it names — and it is now written into a requirement amendment.

Two record-accuracy defects sit alongside it: `B-51`'s recorded *mechanism* is falsified by the very
test that cites it, and §6's `B-50` says the increment's one declared behaviour change is "covered"
when the full suite stays green with that behaviour reverted.

---

## Environment and integrity

| Control | Evidence |
|---|---|
| No file under `mapper/`, `tests/`, `docs/` edited | real-repo `git status --short` byte-identical to the state received; 7 key files sha256-compared against my mirror after every mutation — all `OK` |
| No mutating git command in the repo | `git worktree list` → the repo only; the one worktree I created was inside the **mirror** and removed |
| `fixtures/` unchanged | sha256 of all 4 files identical before and after (`84941a2b…`, `1fcc9a64…`, `88f4b0e4…`, `60934d83…`) |
| Mutations | a full copy of the working tree (including `.git`, so `git ls-files` behaves) under the session scratchpad, `PYTHONDONTWRITEBYTECODE=1` |
| Live-app probes | every probe used `tempfile.mkdtemp()`; the repo's `fixtures/` was never a workspace |
| Post-battery control | mirror restored → `716 passed, 17 deselected, 1 xfailed` |

### Current state — reproduced, not accepted

| Claim | Reproduced |
|---|---|
| fast `716 passed, 17 deselected, 1 xfailed` | ✓ `716 passed, 17 deselected, 1 xfailed in 58.02s` |
| slow `17 passed` | ✓ `17 passed, 717 deselected in 23.99s` |
| ruff `mapper/ tests/` = **27**, zero new | ✓ `Found 27 errors.` — and I diffed the finding *set* against `4eaba35` in a detached worktree: the **only** delta is `tests/test_app.py: F401 pytest imported but unused`, removed. The author's "−1 is the pre-existing `pytest` F401 the new xfail consumes" is **exactly right**, line for line |
| `ruff check fixtures/` clean | ✓ — but see **N-L1**: `warning: No Python files found under the given path(s)`. The control is vacuous |

---

## Per-finding confirmation

### H1 — the inverted map-truth guard — **DISCHARGED**

The guard is now anchored on the row (`line.startswith("| **\`ViewState\` parameter object**")`),
not on a document-wide `split("state.py")`. Five mutants, executed against
`tests/test_repair_map_truth.py::test_at_p05b_a_forward_commitment_is_never_written_present_tense`:

| Mutant | Verdict | Reading |
|---|---|---|
| **A** — the row replaced with the **verbatim `4eaba35` row** (the exact regression the docstring names) | **RED** | ✓ **the finding is discharged** — this is the case that passed before |
| **C** — legitimate content edit to the row's description cell (`hits` added to the roster) | **GREEN** | ✓ no false-fail on a legitimate row edit |
| **E** — `mapper/views/state.py` removed from disk | **RED** | ✓ the existence half is live |
| **D** — cosmetic edit to the row's *label* (`**\`ViewState\`** parameter object`) | RED | brittle-but-loud; see **N-L3** |
| **B** — row regressed to `· **NOT PRESENT**` (no `COMMITTED, ` prefix) | **GREEN** | ✗ **residual hole — see N-M1** |

Control green before and after; `docs/ARCHITECTURE.md` sha256 back to `743a84e9…`.

### H2 — the export leaking live keyboard focus — **DISCHARGED, both halves**

**(a) Independence, through the shipped path.** I reverted the `replace(..., focus_owner="")` to the
pre-fix shape in the mirror and ran the new arm:

```
=== CONTROL ===                                    1 passed
=== MUTANT: export drops focus_owner='' ===
E  AssertionError: assert '#f5f5f5 on #262626' == 'bold #000000 on #1783ff'
FAILED tests/test_app.py::test_an_export_never_encodes_where_the_keyboard_was
=== POST-CONTROL ===                               1 passed
```

The arm reddens without the fix, with **exactly** the tone pair the first reviewer measured. Not a
tautology.

**(b) The `diff`-carrying behaviour is intact.** This is the half that could have been silently
broken by `replace()`, so I captured the actual `ViewState` the **shipped** `action_export_svg`
hands the renderer, with a live diff and a live query set:

```
live _focus_owner() before export: 'rail'
--- ViewState handed to the renderer BY THE SHIPPED EXPORT ---
  selected_id  = root      query = hij      diff = FakeDiff      focus_owner = ''   w=80 h=14
```

`diff`, `query` and `selected_id` all survive; only `focus_owner` is pinned. **`#D4`/`B-50`'s
motivation is preserved.** I also confirmed the real `e` key reaches the same writer and paints the
same focused tone — so the property holds on the keystroke path too, not just the method call.

### H3 — the published cardinality — **DISCHARGED; 34 / 25 / 7 all correct**

Re-derived with **my own** AST census, walking the filesystem with `rglob` rather than `git ls-files`
so tracked-ness could not hide anything, and cross-tagging each site with its tracked-ness:

```
ARGFUL  .render call sites: ON-DISK=34  TRACKED-ONLY=34
ZERO-ARG .render call sites: ON-DISK=25  TRACKED-ONLY=25
DEFINITIONS under mapper/views: ON-DISK=7  TRACKED=7   (all ['self','graph','state'])
```

All three pins are right. The provenance also checks out: the first reviewer's 32 plus the two
`LayeredRenderer().render(...)` sites the H2 fix added at `tests/test_app.py:299,300` = 34.

**Is pinning the right call, or does it just move the staleness?** It is the right call, and I
tested the thing that would decide it — *does a drift actually redden the pin, in both directions*:

| Drift | Pin verdict |
|---|---|
| one arg-ful call site **added** | **RED** |
| one renderer definition **removed** (`outline.py::render` renamed) | **RED** |

So round 10 does close what round 9's two mis-shaped mutations failed to test, and the author's
self-diagnosis ("a weaker assertion cannot fail — that is a tautology, not a mutation") is correct.
Staleness is not merely moved: a narrated number in `docs/ARCHITECTURE.md` is contradicted by
nothing, while a pinned one is contradicted by the suite on the next commit that drifts. And the map
row now narrates **none** — verified in the diff. This also restores the repo's own convention
(`test_darkside_census.py:279`).

### M1 — the flaky focus test — **DISCHARGED for flakiness, PARTIALLY for discriminating power**

**Stress under parallel load — the only condition that ever reproduced it.** Six concurrent
full-suite runs, each in its own copy of the tree (16 cores), and under that contention 14 sequential
runs of the three focus/export arms:

```
runs 1-14 : 2 passed, 1 xfailed   (every run)
background: load1..load6 -> 716 passed, 17 deselected, 1 xfailed  (each)
```

**20 under-load executions of the arm, zero failures.** And it is timing-independent *by
construction*, not by luck: the arm no longer waits for focus, it asserts the derivation at each
step, which holds whether or not anything is focused. That is the right shape and it is a real fix.

The partial is **N-M4**: `_expected_owner()` is a line-for-line transcription of `_focus_owner()`'s
walk, so it is not the "independent recomputation" §9 and `A-94` call it.

### M2 — the acceptance passing because focus is lost — **PARTIALLY, and it introduced N-H1**

The loose `len(set(seen)) > 1` is gone — correct, and the diagnosis behind it is right. But the
replacement's central claim is false. See **N-H1**.

### M3 — threshold 3's escapes — **PARTIALLY**

Six escape shapes, each appended to a tracked file in the mirror and run against the whole census:

| Escape | Verdict |
|---|---|
| `renderer.render(g, **opts)` — `**` splat | **CLOSED** — threshold 3 RED |
| `renderer.render(g, sel, w, h)` — positional old shape | **CLOSED** — threshold 3 RED |
| `renderer.render(g, selected_id=sel)` — old-shape keyword | **CLOSED** — threshold 3 RED |
| **untracked product source** under `mapper/views/` with an old-shape `def render` | **CLOSED** — the new invisibility arm RED |
| tracked renderer at a **nested** path `mapper/views/sub/nested.py` | **CLOSED** — `git ls-files 'mapper/views/*.py'` does match across `/`; four arms RED |
| `ast.AsyncFunctionDef` | walked (`:68`) |
| **`renderer.render(*opts)` — `*` splat** | **OPEN** — threshold 3 green. See **N-M6** |
| **untracked TEST file** with an old-shape call site | **OPEN** — `15 passed`. See **N-M6** |

### M4 — the floor — **DISCHARGED.** `== 25`, at `test_a3_census.py:123` and `:225` (see N-L2).

### M5 — the frozen arm — **DISCHARGED, mutation-verified in both directions**

| Mutant | Verdict |
|---|---|
| a `ViewState` field made **required** (the case the old shape absorbed) | **RED** — `test_..._is_frozen` now fails with `TypeError` escaping the `raises` block, plus `..._constructs_with_no_arguments` |
| `ViewState` **unfrozen** | **RED** — `Failed: DID NOT RAISE` |

The narrowing to `dataclasses.FrozenInstanceError` and the construction moved outside the block are
both correct, and the arm is no longer absorbable.

### M6 / L1–L4 — accepted as dispositioned

`M6`/`B-53` and `L4`/`B-52` are declared and carried. `L1` is right — 7 is the honest number and I
derived it. `L2`'s bare-id rewrite is verified working through the real wiring (`insp-title` →
`'inspector'` via the parent walk; `map-rail` → `'rail'`). `L3`'s new arm reddens on drift: adding
`("map-toast", "toast")` to `_FOCUS_REGIONS` → `test_llr_cnv_3_1_the_two_focus_owner_rosters_cannot_drift`
**RED**.

### B-51 — **PARTIALLY. The conclusion is right; the recorded mechanism is wrong**

**The conclusion holds and I confirm it independently: `M-10` does not reproduce, `tab` does not
traverse focus on `MapScreen`, and `LLR-CNV.3.1`'s threshold is unmeetable on this tree.** The record
is right about the thing that matters.

But the *evidence* the record publishes is condition-dependent, and the condition is the one the
xfail arm itself uses:

```
prefocus=False (4 runs): owners=['rail','','','','','','']   ids=['map-rail',None,...]
                         ... and one run gave ['','','','','','','']  — nothing ever focused
prefocus=True  (3 runs): owners=['rail','rail','rail','rail','rail','rail','rail']
                         ids   =['map-rail','map-rail',...]   — focus STICKS, it is not dropped
```

`A-94`, `A-95`'s `B-51` row and `mapper/app.py::_focus_owner`'s docstring all state, unconditionally,
that tab "**DROPS** it — `map-rail` then `None`, deterministically". That is true only when nothing
was explicitly focused. **`tests/test_app.py::test_llr_cnv_3_1_the_declared_tab_traversal_threshold`
pre-focuses `#map-rail` and therefore cannot produce the sequence its own docstring cites.**

The real invariant, which I measured and which is the one `qa-reviewer` needs:

```
screen.focus_chain : []          <-- EMPTY, in both conditions
focusable widgets  : map-rail, insp-title, insp-state, insp-notes, search-input
```

**There is nothing to traverse to** — the screen's focus chain is empty even though five widgets
report `can_focus=True`. "Drops" and "sticks" are two surface readings of that one cause. See
**N-M2**.

---

## On the `.focus()` decision against C-16 — **I uphold the author, and the same test breaks the other half of the control**

C-16 verbatim (`.dev-flow/04-validation.md:45`):

> ✗ A proxy **in place of the interaction** (a direct setter, `.focus()` instead of the real keys) is
> not evidence **of the interaction** (C-16).

with the batch-01 gloss: *"Every `AT` drives the real mechanism (`pilot.press`), never `.focus()` or
a direct `action_*` call, **where the story promises a keystroke**."*

**The author's claim is correct.** C-16 bans a proxy standing in for the interaction *under test*.
`test_an_export_never_encodes_where_the_keyboard_was` is about the export's state construction; no
keystroke is promised for *establishing* focus. And the arm does not merely assume the precondition
— it asserts it (`assert screen._focus_owner() not in ("", "canvas")`), which is exactly what turns
`.focus()` from a proxy into a verified precondition. Upheld.

**But the same test violates the clause the author did not argue.** It calls
`screen.action_export_svg()` directly, while its docstring claims it "drives the **SHIPPED** export
action". Export *is* promised as a keystroke — `mapper/keymap.py:118`,
`KeyBinding("e", "e", "export_svg", "exportar svg", "view")` — and I verified the real key works:

```
focus owner: 'rail'
REAL KEY 'e' reached the writer? True
exported tone: bold #000000 on #1783ff
```

`pilot.press("e")` would satisfy C-16's letter at zero cost and strengthen the arm. See **N-M5**.

---

## NEW findings

### N-H1 — the strict xfail's alarm cannot fire on the event it names  [Severity: HIGH]

- **Where:** `tests/test_app.py::test_llr_cnv_3_1_the_declared_tab_traversal_threshold`; the claim is
  repeated in `01-requirements.md` `A-94` and in `increment-002.md` §9's M2 row.
- **What:** The arm's docstring: *"strict means this arm FAILS LOUDLY when it starts passing, forcing
  the requirement, the carry and this test to be reconciled together rather than drifting apart."*
  `A-94`: *"so it fails loudly the day traversal is fixed rather than being quietly forgotten."*

  It cannot. `LLR-CNV.3.1`'s threshold is defined **from the canvas** — *"after 1 real `tab` press
  **from the canvas**, the field reads `"rail"`; after 2, `"inspector"`"*. The test's pre-state is
  `screen.query_one("#map-rail").focus()` — **from the rail**. One tab from the rail cannot leave the
  field reading `"rail"` under any working traversal, so `(first, second) == ("rail", "inspector")`
  is unreachable in the repaired world.

- **Executed**, replaying the arm's own body with `tab` replaced by a correct traversal
  (`map-rail → insp-title → …`), i.e. the world the docstring says makes it start passing:

  ```
  Simulated B-51 REPAIR: tab traverses rail -> insp-title -> ...
  A) the arm's OWN pre-state (#map-rail focused, per its body):
     after tab1='inspector'  after tab2='inspector'
     -> arm asserts ('rail','inspector') => STILL FAILS (alarm SILENT)
  B) the requirement's pre-state ('from the canvas' -- unreachable, #map-canvas
     is can_focus=False, B-53; nearest proxy = inspector):
     after tab1='inspector'  after tab2='inspector'
     -> STILL FAILS (alarm SILENT)
  ```

- **Why it matters:** This is the **H1 class recurring one level up**. H1 was blocked because a guard
  passed on the exact regression it named; this guard *stays red* on the exact repair it names, so it
  is a tripwire nobody can trip. Worse, the false property is now written into a **recorded
  requirement amendment** (`A-94`) and a **carry** (`B-51`) — the artifacts the A-family triggers
  read — so a future reader will believe a reconciliation is guaranteed that is not. And `strict=True`
  cuts the other way too: the arm *would* xpass, and fail spuriously, if the rail ever gained a second
  focusable child — an event that has nothing to do with `B-51`.
- **Suggested fix** — pin the *measured* invariant, which a repair genuinely reddens, and stop
  claiming the unreachable threshold is the tripwire:

  ```python
  def test_b51_map_screen_has_no_focus_chain_to_traverse(...):
      """B-51's ROOT CAUSE, pinned. Five widgets report can_focus=True and the
      chain is empty, so `tab` has nowhere to go -- which is why it reads as
      'dropped' with no explicit focus and 'stuck' with one. Reddens the day
      the chain is repaired, which is the reconciliation event."""
      assert [w.id for w in screen.focus_chain] == []
      assert {w.id for w in screen.walk_children() if w.can_focus} == {
          "map-rail", "insp-title", "insp-state", "insp-notes", "search-input"}
  ```

  Keep the threshold arm if you want the requirement transcribed, but drive it from a **reachable**
  pre-state and correct the docstring's evidence (see N-M2), or drop the "fails loudly" claim from
  the arm, from `A-94` and from §9.

### N-M2 — `B-51`'s recorded mechanism is falsified by the test that cites it  [Severity: MEDIUM]

- **Where:** `01-requirements.md` `A-94` (the `owners=['rail','','',…]` block and *"it drops it"*),
  `A-95`'s `B-51` row, `mapper/app.py::_focus_owner` docstring, and the xfail arm's docstring.
- **What / measured:** see **B-51** above. With the rail explicitly focused — the xfail arm's own
  setup — the sequence is `['rail','rail','rail','rail','rail','rail','rail']`, not
  `['rail','','','','','','']`. The `'', '', …` sequence needs the *no-explicit-focus* condition, and
  even there it is not fully deterministic: one of my four runs produced `['','','','','','','']`
  (nothing ever focused), so "deterministically over three runs" is under-sampled.
- **Why it matters:** the carry is routed to `qa-reviewer`, who will start from the recorded
  mechanism. "Focus is dropped" and "the rail swallows tab" point at different root causes; the
  actual cause is neither — it is `screen.focus_chain == []`. A wrong mechanism in a recorded
  amendment costs the next agent a diagnosis they should not have to redo. This is the same class as
  H3 (a measurement published beyond the conditions under which it was taken).
- **Suggested fix:** state both conditions and the cause in `A-94`, and correct the two docstrings:
  *"`tab` cannot traverse because `MapScreen.focus_chain` is empty (5 widgets report
  `can_focus=True`); with no explicit focus this reads as `map-rail → None`, with the rail focused it
  reads as `map-rail` held indefinitely."*

### N-M3 — §6 says `B-50` is "covered"; the full suite is green with it reverted  [Severity: MEDIUM]

- **Where:** `increment-002.md` §6, `B-50`: *"The export-during-diff fix is a behaviour change …
  Deliberate, `#D4`'s stated motivation, and **covered**"*.
- **Executed**, full fast suite, mutating `mapper/app.py::_view_state`:

  ```
  MUTANT: diff=None                          -> 716 passed, 17 deselected, 1 xfailed
  MUTANT: diff=None AND query=""             -> 716 passed, 17 deselected, 1 xfailed
  ```

  Corroborated statically: `grep -rn "diff=" tests/` and `grep -rn "query=" tests/` return **zero**
  hits outside `query_one`/`query_text`.
- **Why it matters:** the increment's **one declared behaviour change** — and the measured defect
  that justified the whole parameter object — has no executed coverage, so the under-fill can return
  silently. §6 says "covered"; §5.2 of the same document says *"no test anywhere passes `query=` or
  `diff=`"*. The two contradict each other, and gate item 10 was ticked on §5.2. The behaviour itself
  is **correct** — I measured it directly through the shipped export — so this is a false coverage
  claim, not a live bug.
- **Suggested fix:** strike "and covered" from `B-50`, or add the one arm that earns the word — the
  export probe I ran is three lines: capture the `ViewState` the export hands the renderer and assert
  `state.diff is not None` with `diff_active` set.

### N-M1 — the H1 guard pins one phrasing; `"NOT PRESENT"` walks straight through  [Severity: MEDIUM]

- **Where:** `tests/test_repair_map_truth.py:161-171`
- **Measured:** rewriting the row's marker to `· **NOT PRESENT**` (no `COMMITTED, ` prefix) —
  semantically the same regression the guard exists to stop — leaves the arm **GREEN**.
  `assert "COMMITTED, NOT PRESENT" not in row` matches one literal, and the backstop
  `assert "PRESENT" in row` is satisfied by the `PRESENT` **inside** `NOT PRESENT`, so it is
  near-vacuous.
- **Suggested fix:**

  ```python
  assert "NOT PRESENT" not in row and "NOT YET IN THE TREE" not in row, (...)
  assert "· **PRESENT**" in row
  ```

  and add the mutant (`row → "· **NOT PRESENT**"` must go RED) to the battery.

### N-M4 — `_expected_owner` is a transcription, not an independent recomputation  [Severity: MEDIUM]

- **Where:** `tests/test_app.py::_expected_owner`; the claim is in §9's M1 row and in `A-94`
  (*"an independent recomputation"*).
- **What:** it re-implements `_focus_owner`'s parent walk line for line over the same
  `_FOCUS_REGIONS`, so any bug in the walk is reproduced by the oracle. Mutation-tested:

  | Mutant | Verdict |
  |---|---|
  | `_focus_owner` returns a constant `"rail"` (`M-FOCUSWIRE`) | **RED** ✓ |
  | `_view_state` stops wiring `focus_owner` through | **RED** ✓ |
  | **`_focus_owner` stops walking parents** | **GREEN** ✗ |

  The arm is genuinely non-vacuous — it catches "ignores `app.focused`" and "not wired through" — but
  it cannot catch a defect in the walk itself, and the walk's only real consumer (a child of
  `#map-inspector` → `"inspector"`, which I verified works: `insp-title` → `'inspector'`) is driven by
  **no** executed test. The arm only ever observes `'rail'` and `''`.
- **Suggested fix:** downgrade the claim to what it is ("asserted against a transcription, which
  catches wiring but not the walk"), and add one arm that focuses `#insp-title` and asserts
  `_focus_owner() == "inspector"` — that covers the parent walk with a real, reachable state.

### N-M5 — the export arm calls `action_export_svg()` directly when the real key works  [Severity: MEDIUM]

- **Where:** `tests/test_app.py:293`; docstring claims *"This drives the SHIPPED export action"*.
- **Measured:** `pilot.press("e")` reaches the writer and produces the identical focused tone
  (`bold #000000 on #1783ff`). C-16's gloss names "a direct `action_*` call" alongside `.focus()`,
  and export **is** promised as a keystroke (`keymap.py:118`).
- **Why it matters:** small, but this is the control the batch already paid for once, and the fix is
  one line. As written the arm cannot see a broken `e` binding, which is part of "the shipped export".
- **Suggested fix:** `await pilot.press("e")` in place of `screen.action_export_svg()`.

### N-M6 — two of M3's escapes remain open  [Severity: MEDIUM]

1. **`*` splat.** `renderer.render(*opts)` passes threshold 3. The author banned `**` splat with the
   right argument — *"the keyword names are not statically knowable, so this site is UNAUDITABLE"* —
   and that argument applies verbatim to `*args`. (The cardinality pin reddens incidentally, but that
   only forces someone to bump the pin.)
2. **Untracked test files.** `test_tc_a3_no_source_file_is_invisible_to_the_census` sweeps
   `mapper/` only, while threshold 3 sweeps `tests/` too. Executed: an untracked test file carrying
   `renderer.render(g, selected_id=sel, w=80, h=24)` → **`15 passed`**. The precondition is live right
   now — `tests/test_a3_census.py` is itself untracked (`?? tests/test_a3_census.py`).
- **Suggested fix:** add `or any(isinstance(a, ast.Starred) for a in node.args)` to threshold 3, and
  extend the invisibility arm's `on_disk` set to `tests/` as well as `mapper/`.

### N-L1 — `ruff check fixtures/` is a vacuous control

`warning: No Python files found under the given path(s)` — `All checks passed!` is guaranteed. It is
carried in §4 as a result. Either drop it or point it at a path that has Python in it.

### N-L2 — `len(zeroarg) == 25` is pinned twice

`test_a3_census.py:123` (inside the PINNED arm) and `:225` (the false-failure arm). Two literals to
update on the next legitimate widget addition. Keep `:225` for its distinct message; derive it from a
single module-level constant.

### N-L3 — the H1 guard is brittle on a cosmetic row-label edit

Moving the bold in the row's first cell makes `next(...)` return `None` and reddens the arm. The
failure is loud and correctly worded ("the ViewState row is gone from the module map"), so this is
pinning working as intended — recorded so nobody treats it as a surprise.

---

## What I confirm about §8/§9's own self-assessment

- **The round-9 → round-10 correction is sound and I verified it independently.** Testing a pin by
  loosening it is a tautology, and round 10 asks the right question. Both round-10 mutants reddened
  the pin under my own hand.
- **The three "my mutation was at fault" admissions are honest, not evasive** — in each case the
  underlying guard is genuinely strong, which I confirmed by mutating the *product* rather than the
  guard: `M-N07.2.3-a`, `M-N07.2.3-b`, `M-FROZEN`, `M-B05-a` (3 arms RED on a constant tone),
  `M-FOCUSWIRE` all redden.
- **§9's H3 row is the most honest thing in the packet** — "FIXED, and my correction was wrong first
  too", with the pin going red within a minute of being written. That is the argument for pinning,
  made by the pin. I found no reason to doubt it.

---

## Evidence checklist

- [✓] **Diff read in full** — `git diff 4eaba35 -- mapper/ tests/ docs/` across `app.py`,
      `ARCHITECTURE.md`, `test_app.py`, `test_export.py`, `test_repair_map_truth.py`, plus
      `mapper/views/state.py:1-88` and `tests/test_a3_census.py:1-389` read entire.
- [✓] **Correctness pass** — export path traced end to end through the shipped action and the real
      `e` key with a live diff and query; `_focus_owner` walked against every focusable widget, against
      `app.focused is None`, and against both pre-focus conditions; `focus_chain` measured.
- [✓] **Simplicity pass** — `replace(..., focus_owner="")` is the minimal correct fix; `_view_state`
      is the right shape; no premature abstraction found in the fixes. Nits only (N-L2).
- [✓] **Reuse / duplication** — `_expected_owner` vs `_focus_owner` (**N-M4**); the doubled `== 25`
      (**N-L2**); pinning re-aligned with `test_darkside_census.py:279`.
- [✓] **Tests reviewed for intent** — 22 mutants executed across 8 files, every one restored by
      sha256; the three HIGH each probed against the specific state they claim to forbid.
- [✓] **Counts re-derived independently** — own instrument, filesystem walk, tracked-ness cross-tagged.
- [✓] **Load stress** — 6-way parallel, 20 under-load executions of the focus/export arms.
- [✓] **Verdict explicit** — below.

---

## Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **Block — must fix the HIGH before advancing**

**The three original HIGH are discharged. I want that on the record, because the work behind them is
good:** the map-truth guard now reddens on the regression it names and does not false-fail on a
legitimate row edit; the export is genuinely focus-independent through the shipped action *and* the
real key, with the `diff`-carrying behaviour intact; and the three cardinalities are correct under my
own instrument, pinned in the suite, narrated nowhere. `M4`, `M5`, `L2`, `L3` are cleanly discharged
and mutation-verified. `M1`'s flakiness is fixed structurally, not by tolerance — 20 executions under
6-way load, zero failures. `M3` closed four of six escapes. `B-51`'s conclusion is right.

**It is blocked on one new HIGH, introduced by the M2 fix.** `N-H1`: the strict xfail cannot fail on
the event it names — proven by replaying the arm under a working traversal, where it stays red — and
that false property has been written into requirement amendment `A-94` and carry `B-51`. This is the
same failure class as H1, and this pass exists precisely because a HIGH is never self-cleared.

Two record-accuracy findings should be fixed in the same pass, because they are about the same carry
and the same artifacts: **`N-M2`** (`B-51`'s recorded mechanism is falsified by the test that cites
it; the real cause is `focus_chain == []`) and **`N-M3`** (§6 claims `B-50` is "covered"; the full
suite is green with the behaviour reverted, contradicting §5.2 of the same document).

None of this re-opens the migration. The A3 itself is complete and correct: 7 definitions, 34 arg-ful
call sites, 25 widget sites, zero old-shape survivors including splat and positional forms, byte
identity held, ruff delta exactly the one line claimed. **Fix `N-H1`, correct the two records, and
this increment passes the gate.**

**Recommended order:** `N-H1` → `N-M2` → `N-M3` → `N-M1` → `N-M6` → `N-M4`/`N-M5` → LOWs.
