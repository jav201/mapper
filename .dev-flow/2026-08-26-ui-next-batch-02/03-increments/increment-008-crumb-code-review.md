# Code Review — `Inc-CRUMB` (increment 008)

**Batch:** `2026-08-26-ui-next-batch-02` · **Reviewer:** independent (`code-reviewer`), SERIAL, sole writer
**Tree:** `C:\Users\jjgh8\Github\mapper` @ `57fb403` + working-tree diff · Python 3.12 / Textual 8.2.8 / Windows, `PYTHONUTF8=1`

## VERDICT: **BLOCK** — 2 HIGH

The increment's *stated* headline claims all reproduce: the closing PAIR, the `F-C` two-oracle flip,
the ledger, ruff, and the `KeyBar` fix are real and verified below. The block is on the **crumb bound
itself**, which is measured against the wrong number twice — once against the wrong *width*, once
against the wrong *string*. Both defeat the bound at widths and titles the increment already tests,
and both reproduce `Inc-STRIPS`' F1 — the exact failure §3.1 claims to have caught and fixed.

---

## Scope reviewed

`git diff HEAD -- mapper/ tests/` — 395 insertions, 20 deletions across 6 files.

| file | reviewed |
|---|---|
| `mapper/darkside.py` | `tab_strip` 135-169, `_crumb_line` 171-241, `_cells` 183-190 |
| `mapper/app.py` | `_event_toast` 2149-2185, CSS 3376-3394 |
| `mapper/widgets/chrome.py` | `KeyBar` 26-88 |
| `tests/test_crumb.py` | all 208 lines, 7 arms |
| `tests/test_fold.py` | 564-589 (`F-C` flip) |
| `tests/test_overflow.py` | 829-900 (50x16 → 50x15) |

Sole-writer discipline held. Originals saved and restored byte-identical; all six restore-to pins
re-asserted at exit (transcript §Discipline); `git status --porcelain` matches the entry state;
`__pycache__` purged; `PYTHONDONTWRITEBYTECODE=1` throughout.

---

## Findings

### F1 — the crumb is budgeted against `target_width`, not the terminal width  [Severity: HIGH]

- **Where:** `mapper/darkside.py:167` (`_crumb_line(crumb, target_width)`), against `:159`
- **What:** `target_width = max(width, left_text.cell_len + len(wordmark) + 2)` — the tab row's
  *natural* width, floor **62**. Below 62 columns the crumb is handed a budget larger than the
  terminal, so the bound bounds nothing: the crumb is cell-correct against 62 and then **wraps** in a
  terminal that is narrower. `TabStrip` wants 4-6 rows against the `max-height: 3` lid.

  This is `Inc-STRIPS`' F1 reproduced by the remedy for it — the strip reporting its full height while
  silently eating what it was supposed to declare. §3.1 claims to have caught exactly this and fixed
  it by moving the lid 2 → 3; the lid was never the problem.

  It also falsifies the CSS comment at `app.py:3386-3392` and `test_crumb.py:33-40`: *"3 = a tab row
  that may wrap once, plus the one crumb row."* At ≤30 columns **the tab row wraps twice** (attack #4,
  answered: yes) and the crumb is evicted entirely.

- **Executed — rows `TabStrip` WANTS vs the 3-row lid** (4000-cell title, depth 4):

```
terminal | budget handed to crumb | rows WANTED | lid | clipped?
   118   |    118                |      2      |  3  | no
    80   |     80                |      2      |  3  | no
    62   |     62                |      2      |  3  | no
    60   |     62                |      4      |  3  | YES
    50   |     62                |      4      |  3  | YES
    40   |     62                |      5      |  3  | YES
    35   |     62                |      5      |  3  | YES
    30   |     62                |      6      |  3  | YES
```

- **Executed — what the operator actually sees** (real app, `MapperApp`, cursor at `n3`):

```
--- (35, 14) ---   TabStrip h=3   canvas h=4
   row0: ' c consultar    p repo    n'
   row1: 'construir    f fábrica    ○ mapper'
   row2: '+1 … / nivel 3'                 <- title tail CUT, no ellipsis, no declaration
--- (30, 14) ---   TabStrip h=3   canvas h=2
   row0: ' c consultar    p repo    n'
   row1: 'construir    f fábrica    ○'
   row2: 'mapper'
   CRUMB VISIBLE: False                   <- F1: full lid reported, crumb entirely eaten
```

  At 35-60 columns the visible crumb ends `nivel 3` with **no ellipsis and no `+N`** — `fit`'s
  ellipsis is in the row that got clipped, so the operator cannot tell the title was cut. That is
  precisely the "lie by omission" the docstring at `darkside.py:206-209` says the declaration exists
  to prevent.

- **Why it matters:** the increment's own thesis is that a strip must be bounded *in the cells the
  terminal actually has*. Below 62 columns it is bounded in cells the terminal does not have. 35x14
  and 50x15 are sizes **this suite already drives** (`test_crumb.py:195`, `test_overflow.py:866`) —
  the defect ships under arms that pass beside it.

- **Suggested fix** — one line; the terminal width is already the parameter:

```python
# mapper/darkside.py:167
-        return Text.assemble(line, "\n", _crumb_line(crumb, target_width))
+        # The TERMINAL's width, not the tab row's natural width: `target_width`
+        # floors at ~62 (tabs + wordmark), so below that it is a budget the
+        # frame does not have and the crumb wraps past the lid.
+        return Text.assemble(line, "\n", _crumb_line(crumb, width))
```

  `_crumb_line` already handles `width <= 0` via its own 118 fallback (`darkside.py:214`), so no
  caller changes. **Verified in memory** (no file touched): with this applied the crumb renders in
  **1 row at every width 30-60** tested.

---

### F2 — the budget is measured on the unescaped string and rendered escaped  [Severity: HIGH]

- **Where:** `mapper/darkside.py:238` and `:240` — `escape(part)` / `escape(tail_text)`, measured at
  `:222` and `:227` via `_cells(...)` on the **unescaped** text.
- **What:** every part is measured, then `escape()`d, then rendered. `rich.markup.escape` turns
  `[b]` into `\[b]` — **+1 cell per markup-shaped bracket run**, added *after* the budget was spent.
  A file-derived title carrying tag-shaped substrings (`[draft]`, `[WIP]`, `[b]`, `[/]` — ordinary in
  node titles) inflates the crumb up to ~30% past its declared bound.

  Unlike F1 this breaches the lid at the **shipped sizes the closing arm itself drives**:

```
=== does the escape under-count breach the 3-row lid at shipped sizes? ===
  w=118 tail='[b]'*n  crumb_cells= 153 (budget 118)  strip rows=4  BREACH
  w=118 tail='[/]'*n  crumb_cells= 153 (budget 118)  strip rows=4  BREACH
  w= 80 tail='[b]'*n  crumb_cells= 102 (budget  80)  strip rows=4  BREACH
  w= 60 tail='[b]'*n  crumb_cells=  78 (budget  62)  strip rows=5  BREACH
```

  Across widths 20-89 the bound is exceeded at **70 of 70 widths** with a `[b]`-bearing tail
  (worst observed +4 cells at width 24).

- **The escape is also wrong on its own terms.** `Text.assemble` with `(str, style)` tuples appends
  **literal** text — it does not parse markup. So the escape has no sink to protect and its backslash
  is painted:

```
  _crumb_line(["anc", "[draft] node"], 80).plain
  ->  'anc / \[draft] node'          <- operator sees the backslash
```

  Coercion is not lost by removing it: `app.py:2384` already applies `darkside.plain(part)` to every
  segment before it arrives, and `fit` calls `plain()` again (`darkside.py:499`). The escape is the
  third pass, and the only one that corrupts. (The visible backslash is **pre-existing**; the *budget
  overrun* is new with this increment's bound.)

- **Why it matters:** this is the increment's own collapse class, reachable at 118x34 and 80x24 —
  the two sizes `test_the_crumb_cannot_outgrow_its_ceiling` drives — by changing one character in a
  node title. The arm passes only because its fixture titles are `R`/`y` runs.

- **Suggested fix:**

```python
# mapper/darkside.py:238,240
-        rendered.append((escape(part), MUT))
+        rendered.append((part, MUT))
...
-    rendered.append((escape(tail_text), INK))
+    rendered.append((tail_text, INK))
```

  Drop the `escape` import if `tab_strip` is its last user. **Verified in memory**: the backslash
  disappears and the overrun goes to zero. With F1 + F2 both applied, a sweep of widths 24-129 × 4
  hostile titles (`[b]`-runs, 4000 `T`, 2000 CJK, 4000 `[`) leaves `rows > 3` only at **widths ≤ 33**,
  where the pre-existing tab-row wrap dominates — the carry already declared in §8. Everything this
  increment owns is then in bound.

---

### F3 — the 50x16 → 50x15 re-calibration's stated reason does not reproduce  [Severity: MEDIUM]

- **Where:** `tests/test_overflow.py:857-866` and packet §5
- **What:** the docstring records that after `Inc-CRUMB` *"16 rows no longer hides anything beyond the
  fold — the viewport clause above stopped being satisfiable."* Measured on the delivered tree, 50x16
  still hides two nodes beyond the fold and still discriminates:

```
=== all four clauses + the strip assertion, post-increment tree ===
  (50, 16): fold_hidden=4 view_hidden=2 naive=8 truth=6  -> WOULD PASS (strip_total=6 truth=6)
  (50, 15): fold_hidden=4 view_hidden=2 naive=8 truth=6  -> WOULD PASS (strip_total=6 truth=6)
```

- **Why it matters:** the arm at 50x15 is *sound* — attack #6 answered: it asserts all four
  discriminating clauses inline (`:885`, `:886`, `:891`, `:899`), so it cannot silently degrade into
  a non-discriminating row, and `naive=8 truth=6` is confirmed. The defect is documentary: a test
  docstring now tells the next reader something false about why the number moved. This batch has
  already paid twice for the declaration family (`KeyBar`'s docstring, §2; the `F-C` clause, §4) —
  booking a third instance into a test comment is the same failure.
- **Suggested fix:** either restore 50x16 (it passes) or replace the rationale with the measured
  reason. If the failure was against an *intermediate* tree, say so explicitly — "failed against the
  pre-`KeyBar`-fix draft; 50x16 passes on the delivered tree, moved to 50x15 as the swept-band
  centre" — rather than a claim about the delivered tree that the delivered tree contradicts.

---

### F4 — no arm drives `TabStrip` height below 62 columns  [Severity: MEDIUM]

- **Where:** `tests/test_crumb.py:29` (`SIZES = [(118,34),(80,24)]`), `:102-120`, `:132`
- **What:** `test_the_crumb_cannot_outgrow_its_ceiling` runs only at 118x34 and 80x24 — both ≥ 62,
  the two widths where F1 is invisible. The declaration arm runs at 60x24 but asserts only that `…`
  and `+` appear, never the strip height. The `KeyBar` arm visits 35x14 and asserts `KeyBar` height
  but not `TabStrip`. The suite therefore *stands on* the sizes where the bound fails without ever
  measuring the bound there.
- **Why it matters:** this is why F1 shipped. It is also the coverage gap that lets F1 regress
  silently after it is fixed.
- **Suggested fix:** extend the ceiling arm's sizes and add a no-eviction clause — this goes RED on
  the current tree and GREEN with F1 applied:

```python
SIZES = [(118, 34), (80, 24), (50, 16), (35, 14)]
...
        # BOUNDED IS NOT ENOUGH IF THE LID EATS IT: below ~62 columns the tab
        # row wraps, so a crumb budgeted to anything wider than the terminal is
        # clipped away and the strip reports full height over nothing.
        painted = " ".join(rows_in(screen, strip))
        assert "…" in painted or "+" in painted, (
            f"at {size} the crumb was clipped out of the strip entirely; "
            "the bound is being computed against a width the frame lacks"
        )
```

---

### F5 — `_CRUMB_DROP_CELLS = 8` is one cell short at 3-digit drop counts  [Severity: LOW]

- **Where:** `mapper/darkside.py:176`, spent at `:217` and `:225`
- **What:** the reserve assumes the declaration costs ≤ 8 cells. `"+N " + "… / "` is 7 cells for
  N < 10 and 8 for 10 ≤ N < 100, but **9 for N ≥ 100** and 10 for N ≥ 1000. Swept: overruns by
  exactly 1 cell at depth 150 across widths 20-89 (165 cases), e.g. `+150 … / TAILTAILTAI…` = 21
  cells against a 20-cell budget.
- **Why it is LOW, not HIGH:** unreachable in the app as shipped. `app.py:2383` builds the crumb as
  `_current_crumb() + [node_title]` and `_current_crumb` (`app.py:1702-1706`) returns at most two
  elements, so `dropped ≤ 2`. This is a latent gap in a general-purpose helper, not a live defect —
  but the helper is written as if general.
- **Suggested fix:** compute the reserve instead of constant-folding it, or state the assumption:

```python
-    if used + cost + _CRUMB_DROP_CELLS > budget:
+    drop_cost = _cells(f"+{len(crumb) - 1 - len(kept)} … / ")
+    if used + cost + max(_CRUMB_DROP_CELLS, drop_cost) > budget:
```

  (Cheaper alternative: a comment at `:176` recording that the constant assumes a 2-digit drop count,
  which `_current_crumb` guarantees.)

---

### F6 — `except Exception` where `NoActiveAppError` is the actual contract  [Severity: LOW]

- **Where:** `mapper/widgets/chrome.py:73`
- **What:** the `try/except` **is doing real work** — attack #3 answered. Verified: constructing
  `KeyBar` with no active app raises `textual.app.NoActiveAppError` from `self.app`. But
  `except Exception` also swallows any future failure inside `self.app.size`, silently restoring the
  118-cell render this increment exists to remove.
- **Suggested fix:** `from textual.app import NoActiveAppError` and narrow `except NoActiveAppError:`.

---

### F7 — `_event_toast` measures in `len()` while the module's rule is cells  [Severity: LOW]

- **Where:** `mapper/app.py:2172-2176`
- **What:** `room` uses `len(label)` and the cap uses `min(room, len(detail))`, in the same increment
  that introduces `_cells` specifically because *"a cell budget written in characters bounds
  nothing"* (`darkside.py:186-188`).
- **Why it is LOW:** it is not a live defect. `room` caps the `fit` target, so the render can never
  exceed `room` cells regardless of what `len` reports; the only effect is that a wide-character
  detail is truncated shorter than it needed to be. **Verified** — the toast holds at 1 row at every
  width and with CJK content, and the widget is full-width so `self.size.width` is the correct source:

```
  screen.w=118 toast w=118 room=107 -> rows=1        screen.w=50 toast w=50 room=39 -> rows=1
  CJK detail, w=80: rows=1 ' probado   中中中…'       CJK detail, w=50: rows=1
```
- **Suggested fix:** use `_cells` for symmetry with the crumb, or note at `:2176` why `len` is
  sufficient here (the `min` against `room` is the real bound).

---

## Attacks that FAILED — these parts are correct

| # | attack | result |
|---|---|---|
| 2 | `_cells` vs `len` | **Correct.** `Text(s).cell_len` handles CJK, combining marks and emoji. Swept: bound holds exactly (39/40, 79/80 cells) for `中`×300, `e+U+0301`×300, `😀`×200. |
| 3 | `KeyBar` still renders at 118 | **No such path found.** `KeyBar` is full-width at 118/80/60/35 (`region.width == screen.width`), so `self.app.size.width` is an exact proxy, not a correctable estimate. Construction + mount + resize covers first paint. `try/except` is load-bearing. |
| 5 | `F-C` flip real and durable | **Real, two-oracle reproduced.** RED on the pre-increment tree, GREEN after (transcript below). Durable: the arm asserts `frame_leak == []` over the whole composited frame, so a regression in the `fit` coercion path reports RED with a named reason. |
| 6 | overflow arm discrimination | **Still discriminates.** Four clauses asserted inline; `naive=8` vs `truth=6` confirmed at 50x15. (Its *rationale* is F3.) |
| 7 | the closing PAIR | **Reproduced exactly.** |

---

## Executed transcripts

**Digest gate (entry and exit) — all six pins byte-identical, no-op hazard excluded**

```
5d2e9c885386fd490629d1428a57f4214e26b9b7370d4374f9ab63a743a5f2bc  mapper/app.py
8feddb28763b332f7fc5fa392c77dadc39469be11bfe423e631c37679416f628  mapper/darkside.py
6910306adee8b82c49ae2859837ee3c879a1588d25aabab43e2819714cbfac52  mapper/widgets/chrome.py
05b1e730b49b72f6402d49a1d9c41a8f6c15112a38020c2cdb486af09ade0af4  tests/test_crumb.py
9a310d34edd9d585ffa5c6d39d76f003db9f0915362a77fdc40adf8c66627302  tests/test_fold.py
d50041adb99f631482d14b1436498dd7df1baa354923e9cdd426b12ff0f464f4  tests/test_overflow.py
```

Mutant install asserted before any verdict was read (Windows/POSIX no-op hazard):

```
git checkout HEAD -- mapper/app.py mapper/darkside.py mapper/widgets/chrome.py
ASSERTION: git diff HEAD --stat -- <3 files>  ->  empty
  OK: mutant installed, worktree == HEAD for all 3
on-disk digests after checkout (all differ from the pins):
  16e527763297588edbce1e4f70abd82b498c62268851deb257335e8130a09f9b  mapper/app.py
  ac5b56b1d8bfe166f3ba6b3bed3c3b2d0b730310dd61ac4a22c1b698a8d93304  mapper/darkside.py
  54ccdecb5b8c00323977d9bc6736af23254ff484af2b30841d0d0118a18bdfcd  mapper/widgets/chrome.py
tests/ untouched -> post-increment arms run against pre-increment source
```

**The closing PAIR (packet §6) — reproduced**

```
PRE-INCREMENT   pytest tests/test_crumb.py  -m "slow or not slow"   ->  7 failed          RED  7/7
                pytest tests/test_strips.py -m "slow or not slow"   -> 11 passed          GREEN 11/11
POST-INCREMENT  pytest tests/test_crumb.py                          ->  7 passed          GREEN 7/7
                pytest tests/test_strips.py + 2 arms                -> 11 passed, 2 desel  GREEN
```

**`F-C` two-oracle (packet §4) — reproduced**

```
PRE   tests/test_fold.py::test_the_factory_tree_coerces_the_titles_it_paints  -> 1 failed
POST  same node id, -m "slow or not slow"                                     -> 2 passed (with the overflow arm)
```

**Ledger and lint (packet §7)**

```
pytest -p no:randomly --color=no -q
  920 passed, 19 deselected, 3 xfailed in 203.95s   exit 0     <- matches §BLUF
python -m ruff check .
  Found 27 errors.  (23 F401 unused-import, 4 F841 unused-variable)  <- matches "27 = 27"
```

**Restore**

```
originals copied back; all six digests re-asserted == pins (above)
git status --porcelain identical to entry state
__pycache__ directories under mapper/ and tests/: 0
```

---

## Evidence checklist

- [x] **Diff read in full** — `mapper/darkside.py:135-241`, `mapper/app.py:2149-2185` + `3376-3394`, `mapper/widgets/chrome.py:26-88`, `tests/test_crumb.py:1-208`, `tests/test_fold.py:564-589`, `tests/test_overflow.py:829-900`.
- [x] **Correctness pass (edge / None / error paths)** — F1 (narrow widths), F2 (bracket-bearing titles), F5 (3-digit drop counts), F6 (`NoActiveAppError`); `_crumb_line`'s `if not crumb` guard and `width <= 0` fallback both exercised.
- [x] **Simplicity pass** — no premature abstraction found. `_cells` and the three constants are each used and each named for a measured reason. The one *removable* piece is `escape` (F2), which is redundant against `plain()` at two prior seams.
- [x] **Reuse / duplication checked** — `_crumb_line` correctly reuses `fit`; `_event_toast` reuses `fit`; `KeyBar._width` reuses `darkside.keybar`'s width parameter. F7 is the one unit inconsistency (`len` where `_cells` exists).
- [x] **Tests reviewed for intent** — the 7 new arms encode WHY (canvas rows, count readable in its own region, declaration present); the overflow arm asserts its own discriminating preconditions inline. Gaps: F4 (no narrow-width height arm), F2 (fixture titles cannot reach the escape path), F3 (false rationale).
- [x] **Verdict explicit** — BLOCK, below.

---

## Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **BLOCK — must fix HIGH findings before advancing**

**HIGH count: 2** (F1, F2). Both are one-line fixes in `mapper/darkside.py`, both verified in memory,
and together they bring every width ≥ 34 into bound — leaving only the tab-row wrap the packet
already carries in §8.

`LLR-N07.3.4`'s `open_blocks` should **not** flip on this close: the paired evidence in §6 is genuine
and reproduced, but it was collected only at 118x34 and 80x24, and the vector it claims to close is
still reachable below 62 columns (F1) and at 118x34 with a bracket-bearing title (F2).

Recommended order: F1 + F2 (source), then F4's arm as the regression oracle — it goes RED on the
current tree and GREEN with F1 applied, which is the two-oracle standard this batch already runs on.
F3 is a docstring correction. F5-F7 are recommendations.

Handoffs: no security concern found in this diff — F2's `escape` removal touches a coercion-adjacent
path and is flagged for the SERIAL `security-reviewer` that follows, with the note that `plain()` is
already applied at `app.py:2384` and inside `fit` (`darkside.py:499`). No suite/functional gap for
`qa-reviewer` beyond F4.
