# Increment CRUMB — the title-length vector, and the fifth strip underneath it

**Batch:** `2026-08-26-ui-next-batch-02` (SEALED) · **Increment:** `Inc-CRUMB` · **Branch:** `feat/ui-next-batch-02`
**Entry commit:** `57fb403` (Inc-STRIPS close) · **SOURCE FILE COUNT: 3** — `mapper/darkside.py`, `mapper/app.py`, `mapper/widgets/chrome.py`. Widened from 2 by a recorded cut amendment (§2). Tests uncapped.
**Protocol:** FULL — same collapse class. **Reviews SERIAL**, per the rule `Inc-STRIPS` earned.

---

## BLUF

`LLR-N07.3.4`'s **second vector is closed**, and the closing evidence is a **pair**:

```
title-length arms   7/7 RED pre-increment  ->  7/7 GREEN after
fanout arms        11/11 GREEN on BOTH trees (not traded for the first)

default lane : 920 passed, 19 deselected, 3 xfailed   exit 0
all markers  : 939 passed, 3 xfailed                  exit 0
ruff SET     : 27 = 27, zero NEW, zero GONE
```

Ledger `920 = 913 + 7`, all-markers `939 = 932 + 7`.

## 1 · The pre-gate

One 4000-character node title, measured before anything changed:

| | TabStrip | canvas | count region |
|---|---|---|---|
| 118x34 before | h=37 | **h=1** | on-frame |
| 80x24 before | **h=54** | y=56, **0 rows** | y=57, **0 rows** |
| 118x34 after | **h=2** | h=27 | on-frame |
| 80x24 after | **h=2** | h=15 | on-frame |

500 characters — which cost a third of the canvas at 80x24 — is now identical to the 4-character
baseline. `#map-toast` separately: a 4000-character detail rendered **36 rows** and left the canvas
**1**; now 1 row and 27.

## 2 · The cut was WIDENED, and the discovery is the reason

I stopped at the pre-gate boundary rather than pressing on, and the coordinator widened the cut.

**The crumb bound removed a mask.** Bounding the crumb correctly shortened `TabStrip` from three rows
to two — and *that reflow had been firing `KeyBar`'s corrective `on_resize` by accident*.
`KeyBar.__init__` rendered at a hard-coded **118** cells and relied on a resize to fix it; a resize
fires when the size **changes**, so a layout that hands the widget its final width immediately never
fires one.

**Measured at 35 columns:** the 118-cell render is 75 cells and wraps to **four rows** against **one**
at the true width — three rows taken from a fourteen-row frame.

**The defect predates this increment; only the mask was new.** And its own class docstring had claimed
*"renders at its MEASURED width"* ever since the hard-code was supposedly removed — the declaration
family, one more time, in code I had not written.

**Widened rather than split** because it is the same collapse class, and splitting would have held
finished work uncommitted behind a dependency — the un-landed-record failure this batch already paid
for with twelve days of `Inc-4c` limbo.

## 3 · What changed — Python first, CSS second, and that order is the rule

| # | surface | bound |
|---|---|---|
| 1 | `darkside.tab_strip`'s crumb | `_crumb_line`: budget spent from the RIGHT (tail first, then ancestors), each part cell-bounded by `fit`, remainder **declared** `+N …` |
| 2 | `_event_toast`'s detail | bounded at the seam all eleven call sites pass through |
| 3 | `KeyBar` | width resolved at construction and at mount; resize kept as the UPDATE path, not the correction path |
| 4 | stylesheet | `TabStrip` and `#map-toast` lids — **after** 1-3, never before |

**The tail is the part worth keeping**: it is the node the cursor is on, painted `INK`; the ancestors
are context in `MUT`. And what is dropped is **declared**, because `keybar`'s own docstring already
settled why — a bare ellipsis *"is a lie by omission: it says something was cut but not that anything
is missing, let alone how much"*.

### 3.1 · I reproduced F1 with my own remedy, and my own arm caught it

The first draft set `TabStrip { max-height: 2 }`. At **60 columns the tab row itself wraps** — the
tabs plus the wordmark exceed the terminal — so a 2-row lid **clipped the crumb away entirely**: the
strip reporting full height while eating the thing this increment added. That is `Inc-STRIPS`' F1,
reproduced by the remedy for it, one increment later.

Caught by this increment's own crumb-declaration arm. Ceiling is **3**: a tab row that may wrap once,
plus the one crumb row. **The tab row's wrapping below ~60 columns is pre-existing and is carried, not
introduced** — `tab_strip` sizes itself to `max(width, tabs + wordmark)`.

## 4 · `F-C` closed by accident, BOOKED deliberately

Bounding the toast routed its detail through `darkside.fit`, which **coerces** as well as truncates —
so the `FactoryScreen` chrome sink `F-C` named stopped leaking. Nobody set out to close it.

**Two-oracle evidence:** `test_the_factory_tree_coerces_the_titles_it_paints`, re-scoped from
asserts-OPEN to asserts-CLOSED, is **RED on the pre-`Inc-CRUMB` tree** and **GREEN after**. The clause
that used to stand there had itself instructed the next reader to re-scope it to the whole frame on
the day the leak stopped — so the arm was written to be flipped, and this is that day.

**`Inc-REPAIR`'s scope drops `F-C`**, recorded there and in the carry ledger. A defect closed by
accident still gets a deliberate record; otherwise the next increment either re-fixes it or reports it
open.

## 5 · An arm re-calibrated by re-sweeping, not by nudging

`test_the_paint_site_differences_one_set_on_a_PARTIAL_overlap` stood on a **narrow band** — its
docstring records that 50x16 was found by sweeping 56 sizes x 3 folds for the state where a fold hides
something, the viewport *independently* hides something, and the naive sum disagrees with the truth.
Giving the canvas rows back moved the band out from under it, and **the arm failed for exactly the
right reason** ("the viewport hides nothing beyond the fold").

I re-ran that search rather than adjusting the number: the four clauses now hold at **28 sizes**, and
at that width for heights 10-15. **50x15** is the nearest member — same width, same intent, and the
same discriminating values the old row produced (`naive=8` against `truth=6`).

## 6 · The closing evidence — a PAIR, because one verdict cannot close two vectors

```
POST-INCREMENT   title-length  7 arms, 7 PASSED
                 fanout       11 arms, 11 PASSED
PRE-INCREMENT    title-length  7 arms, 0 PASSED, 7 RED
                 fanout       11 arms, 11 PASSED
```

A single green run would be consistent with having broken the fanout vector and not noticing — which
is a state this requirement has already been in once. All three source files were installed from
`HEAD` with **each digest asserted before any verdict was read**, and restored with the digests
re-asserted.

## 7 · Gate checklist

- [x] **Tests / lint pass** — `920 / 939`, exit 0 both lanes; ruff SET-identical 27 = 27. Tree sha256-pinned before and after.
- [x] **Closing evidence is a pair** — §6, both directions, digests asserted.
- [x] **Python bound before CSS lid** — §3, and §3.1 records what happened when I briefly got the ceiling wrong.
- [x] **`F-C` booked with two-oracle evidence** — §4.
- [x] **Reverse census** — `tab_strip` (`test_darkside`), `_event_toast` (`test_search`), `TabStrip` (`test_fold`), `crumb` (`test_darkside`, `test_fold`); all green.
- [x] **Source file count** — 3 of 3 per the amendment, cap is 4.
- [ ] **Independent code review** — SERIAL, dispatched first.
- [ ] **Security review** — SERIAL, dispatched only after the code review returns.

## 8 · Carries

- **`open_blocks` for `LLR-N07.3.4` flips at this close** — both vectors now measure closed, on the
  paired evidence in §6.
- `R1`/`R2`/`R3` from `Inc-STRIPS` ride here and are **not** yet addressed — they are documentary and
  belong to whoever next edits these comments.
- **New, and carried rather than fixed:** `TabStrip`'s tab row wraps below ~60 columns. Pre-existing,
  outside this cut, and now the only unbounded content left on that strip.

## 9 · Round 2 — the code review, and a bound measured against the wrong number twice

**BLOCK, 2 HIGH.** Every headline claim reproduced — the closing pair, the `F-C` two-oracle flip, the
ledger, ruff, the `KeyBar` fix. The block was on **the crumb bound itself**, and both defects are the
same shape: the budget was honest and it was measured against the wrong thing.

### 9.1 · `F1` (HIGH) — budgeted against `target_width`, not the terminal

I passed `target_width` to `_crumb_line`. That is the **tab row's natural width** —
`max(width, tabs + wordmark)`, floor **62** — so below 62 columns the crumb received a budget
**larger than the frame**. It was then cell-correct against 62 and wrapped anyway.

Measured by the reviewer: at 30 columns the crumb wanted six rows and the lid **ate it entirely**; at
35-60 the visible line ended mid-title with **neither ellipsis nor `+N`**, because `fit`'s ellipsis
sat in the clipped row. **That is the "lie by omission" the declaration exists to prevent — and
`Inc-STRIPS`' F1 for the third time, in the increment whose §3.1 claims to have caught it.**

One-line fix: pass `width`. Verified across 30-118: **one row at every width**.

### 9.2 · `F2` (HIGH) — measured unescaped, rendered escaped

The budget was spent on the raw string and the line rendered through `escape`, which adds a cell per
markup-shaped bracket run **after** the arithmetic. A `[b]`-bearing title breached the lid at
**70 of 70 widths** from 20 to 89 — *including both widths this module's closing arm drives*, which
pass only because their fixture titles are letter runs.

And the escape was wrong on its own terms: `Text.assemble` with `(str, style)` tuples appends literal
text and parses no markup, so the backslash was **painted**. No coercion is lost — `MapScreen` applies
`plain` to every part before it arrives and `fit` applies it again.

### 9.3 · `F4` — the arm whose absence let `F1` ship

Every other arm here drives 118 and 80: the two widths at which `F1` is invisible. Added a
narrow-width arm, and its floor is **measured, not estimated**: below **31** columns the *tab row
alone* needs three rows and evicts the crumb however well the crumb is bounded. The reviewer put that
boundary at ≤33; direct measurement puts it at 31, and the arm drives 35-60.

### 9.4 · `F3` — my re-calibration was unnecessary, and its stated reason was false

I moved the overlap arm 50x16 → 50x15 and recorded that 16 rows "no longer hides anything beyond the
fold". **On the delivered tree 50x16 passes.** The reason was true at the moment I measured it — the
`KeyBar` fix had not landed yet and later restored the geometry — and false of what I shipped.

**Reverted to zero diff on that file.** Keeping an unnecessary change with a false justification would
have been worse than the change itself, and `test_overflow.py` is now untouched by this increment.

### 9.5 · `F6` — `except Exception` where one exception was meant

`KeyBar._width` swallowed everything; a bare `except` there would silently restore the 118-cell render
the class exists to stop producing. Now `except NoActiveAppError`, which is the real contract —
confirmed by locating it in `textual.dom` after my first import guess was wrong and ruff caught the
unused import.

### 9.6 · Round-2 evidence

```
default lane : 924 passed, 19 deselected, 3 xfailed   exit 0
all markers  : 943 passed, 3 xfailed                  exit 0
ruff SET     : 27 = 27, zero NEW, zero GONE
THE PAIR     : title-length 11/11 RED pre -> 11/11 GREEN post
               fanout       11/11 GREEN on BOTH trees
```

Ledger `924 = 920 + 4`, all-markers `943 = 939 + 4` — the narrow-width arm at four widths.

**Carried, not fixed:** `F5` (`_CRUMB_DROP_CELLS` is one cell short at three-digit drop counts —
unreachable, the crumb is capped at three elements) and `F7` (`_event_toast` measures in `len` where
the module's unit is cells — not live, `room` caps the `fit` target). Both recorded with the
reviewer's reproductions.

- [x] **Independent code review** — **BLOCK, 2 HIGH**, folded here.
- [x] **Security review** — SERIAL, run after the code review returned. **SIGN-OFF, 0 HIGH.**

## 10 · Round 3 — the security review, and a coercion gain I had not claimed

**SIGN-OFF, 0 HIGH.** The review found the increment did more than §3 claimed. Removing `escape()`
was safe on all three limbs, and it is a net coercion **improvement**: four crumb producers —
`app.py:807` (a filename), `app.py:936` (a repo name), `app.py:1235` (the link chain),
`factory.py:351` (a Factory title) — previously reached the frame under `escape` alone, which
coerces nothing. They are now coerced through `fit` → `plain`. I had described `F2` purely as a
correctness fix; it was also a security fix, and I did not know that until a reviewer said so.

On the requirement, verbatim: *"On `LLR-N07.3.4`'s `open_blocks`: from the security side there is no
remaining objection. The title-length vector is measured closed at every width from 20 to 200 with
the hostile fixture."*

**`F1` (MEDIUM), carried:** `TabStrip.__init__` renders the crumb at a 118-cell fallback rather than
the terminal's width. Not live. See §11 — I tried to refute this and confirmed it instead.

**Five LOW, carried:** `F2` the code review's `F5` reachability *reason* is false (`dropped` grows
~2N with link-follow depth — the finding is still unreachable, but not for the stated reason);
`F3` the export handler's `except` arm uses `self.notify`, bypassing the bounded seam; `F4`
`factory.py:350` pre-escapes; `F5` `_event_toast` measures the label with `len()`; `F6` the export
toast still paints the username — **exposure UNCHANGED by this increment**, carried as pre-existing.

## 11 · Round 4 — a declaration audit I opened myself, after the sign-off

Nobody asked for this round. The security review's `F1` described a defect structurally identical to
the `KeyBar` one I had just fixed, four lines away, and I went to fix it. Three measurements later I
had not fixed it and had found something else.

**I was wrong twice on the way, and both errors are the batch's own recurring shapes.**

1. I claimed `TabStrip` "never touches the 118 fallback" — that `118` is `_KEYBAR_FALLBACK_CELLS`,
   private to `KeyBar`. False: `darkside._crumb_line:223` is `budget = width if width > 0 else 118`,
   a **second, independently hardcoded** 118.
2. I then claimed the init render was **unbounded**, off a probe showing `width=0` producing the full
   crumb. False, and false for a C-31 reason: my fixture's crumb was 27 cells, which fits under a
   118-cell bound *and* under no bound at all, so **the input could not discriminate the hypotheses**.
   Re-run at 400 cells per part: `width=0` → **117 cells**. Bounded, exactly as the review said.

**`F1` stands as the reviewer wrote it, and is not live** — but the *reason* it is not live is not
the one either of us assumed, and that is §11's actual finding.

### 11.1 · The mechanism in `KeyBar`'s docstring was false — measured

`chrome.py` and `test_crumb.py` both stated: *"a resize fires when the size CHANGES, so a layout that
hands this widget its final width immediately never fires one and the 118-cell render stands."*

Both clauses are refuted. Reconstructing the pre-fix widget in-process (`keybar_mechanism.py`,
`keybar_why.py` — the delivered tree was never edited):

```
arm                                          keybar  canvas  keybar() called with
A  pre-fix shape (no on_mount)                    4       1  [118, 35, 118, 35]
B  pre-fix shape, on_resize ALSO removed          4       1  [118, 118]
C  delivered shape                                1       4  [35, 35, 35, 35, 35, 35]
```

Arm A: **the corrective call at the true width DID fire, and the widget is still 4 rows.** Measuring
what the widget *holds* rather than what it was *called with* settles it:

```
PRE-FIX   region=35x4  held=30cells/1row  first painted row: 'nav j siguiente … +32  ? todas'
DELIVERED region=35x1  held=30cells/1row  first painted row: 'nav j siguiente … +32  ? todas'
```

**The pre-fix widget paints byte-identical text and holds the corrected render.** The 118-cell render
does not stand; the *auto-height computed from it when layout ran* stands, and a later `update()`
does not re-run that calculation. Three canvas rows were taken by a widget whose text was correct.

The fix is unaffected and validated (arm C). Only its stated reason was wrong — and wrongly it would
have sent the next reader hunting a missing resize event that is present. Corrected in both places,
and the test docstring now says why the arm asserts **region height** rather than painted text: *the
painted text is identical across the defect and cannot fail.* That is a C-57 instrument note, in the
arm, permanently.

This also retires my own §11 probe's inference. `tabstrip_liveness.py` concluded "not live" from
*a corrective call was made*, which arm A proves does not entail correction. The verdict survives on
different evidence: content is superseded (measured above) and height is clamped by `TabStrip`'s
`max-height: 3` lid. **The lid is load-bearing for the init path** — which is what Inc-REPAIR must
fix, and is a sharper instruction than "add a width argument".

### 11.2 · Evidence re-measured on the post-edit tree

The edits are prose only — docstrings and comments, `_KEYBAR_FALLBACK_CELLS = 118` carried through
both sides of the edit unchanged. Because I edited a tree that had already been signed off, the full
set was re-run rather than inherited:

```
default lane : 924 passed, 19 deselected, 3 xfailed   exit 0   (unchanged)
all markers  : 943 passed, 3 xfailed                  exit 0   (unchanged)
ruff SET     : base parsed=27 declared=27 / work parsed=27 declared=27
               19 (file,rule) pairs both sides — SET-IDENTICAL, zero NEW, zero GONE
               positive control: reports NEW on a planted entry — OK
THE PAIR     : 22 passed = title-length 11/11 + fanout 11/11
```

The first ruff run compared whole trees and reported 6 GONE pairs, **all under `prototypes/`** — a
scope artifact of the baseline export, not a regression. Re-run at equal scope (`mapper tests`) on
both sides: identical. Recording the false-alarm because a scope mismatch that resolves to "fine" is
the one most likely to be waved through next time.

### 11.3 · Carried from this round

- **118 is spelled twice** — `chrome._KEYBAR_FALLBACK_CELLS` and the `darkside._crumb_line:223`
  literal. Two modules carry the declared context independently and nothing makes them agree. The
  batch's own control says *anything spelled twice will drift*. De-duplication is structural →
  **Inc-REPAIR**. A cross-reference comment is in place so the next reader finds the twin.
- **`F1`** → Inc-REPAIR, with the corrected instruction: bound the init path in Python so
  `max-height: 3` stops being the thing that saves it.

**Process disclosure:** I opened this round unprompted on a signed-off tree. The tree the security
reviewer signed is not byte-identical to the tree now. Prose-only, evidence re-measured and
identical — but a post-sign-off edit is not mine to self-clear, and the close was held for a ruling.

### 11.4 · The construction proof — the sign-off transfers by evidence

Coordinator ruling: close under (a), conditioned on Inc-4c's instrument — **AST-with-docstrings-
stripped byte-identity** across the divergence. Docstrings are deleted from the tree, the dump is
taken without attributes (so re-flowed prose cannot shift a line number into the digest), and
comments never enter an AST at all.

**No artifact of the signed tree survives** — it was uncommitted, and `_confirm/head/` turned out to
be a mid-Inc-CRUMB snapshot, not HEAD. So arm 1 reconstructs the signed files by reversing the three
recorded edits. That is circular on its own: an *unrecorded* executable edit would sit in both
versions and cancel. **Arm 2 exists to close exactly that gap**, against the commit itself.

```
ARM 1 -- signed (reconstructed) vs current, sha256(ast, docstrings stripped)

  mapper/widgets/chrome.py  signed  f1dba13b83748e33bc4dd9137b96d9b8e4b4b82359e8e4f79e94b6b2a4501702
                            current f1dba13b83748e33bc4dd9137b96d9b8e4b4b82359e8e4f79e94b6b2a4501702
                            text delta +826 chars   -> IDENTICAL
  tests/test_crumb.py       signed  1cd89affad3c039813cccd6866015bff6c8612b3ba6aec41b0eb257c81ebf87f
                            current 1cd89affad3c039813cccd6866015bff6c8612b3ba6aec41b0eb257c81ebf87f
                            text delta +187 chars   -> IDENTICAL

ARM 2 -- current vs commit 57fb403, every executable delta line, no exceptions

  +from textual.dom import NoActiveAppError
  +_KEYBAR_FALLBACK_CELLS = 118
  -        self.update(darkside.keybar(self.groups))
  +        self.update(darkside.keybar(self.groups, width=self._width()))
  -        return self.size.width or 118
  +        if self.size.width:
  +            return self.size.width
  +        try:
  +            return self.app.size.width or _KEYBAR_FALLBACK_CELLS
  +        except NoActiveAppError:
  +            return _KEYBAR_FALLBACK_CELLS
  +        self.update(darkside.keybar(self.groups, width=self._width()))
  +    def on_mount(self) -> None:

  lines outside Inc-CRUMB's declared scope: NONE
```

**PROOF HOLDS — prose-only.** The security sign-off transfers to the current tree by evidence.

**Arm 2 produced three false fails before it was right, all from MY declarations, none from the code:**

1. Its oracle was `_confirm/head/` — which has `_width` but no `on_mount`, no `NoActiveAppError` and
   no `_KEYBAR_FALLBACK_CELLS`. A **mid-increment working snapshot I had labelled "HEAD".** Re-pointed
   at the commit through `git show`, so the working tree is never touched.
2. Its expectation was `only-in-current == ['_width', 'on_mount']`. Wrong: `_width` **already exists
   at HEAD** as `return self.size.width or 118`. Inc-CRUMB changed its BODY; only `on_mount` is a new
   name. A function-NAME set cannot see a changed body — too coarse an instrument for the claim,
   replaced by a structural unparse diff.
3. That diff then flagged a bare `+` — a blank separator line from `unparse` — as an undeclared
   change. Loosened to ignore whitespace-only lines, and recorded rather than quietly widened.

Each cost an investigation and each was C-53: **a false fail costs as much as a false pass.** And the
first failure the instrument reported was about my own snapshot labelling, not about the code — which
is the arm doing its job (C-57).
