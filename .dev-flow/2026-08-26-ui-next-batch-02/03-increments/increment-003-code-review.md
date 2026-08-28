# Code Review — Increment 3 (US-N06 «escala»)

**Verdict: BLOCK — 3 HIGH.**
Independent review, not the author. Branch `feat/ui-next-batch-02`, base `954f8f3`, increment
uncommitted in the working tree.

Every behavioural claim below carries an executed transcript. Where I could not execute, the
line says **unverified** rather than asserting.

---

## Scope reviewed

`git diff HEAD` plus the untracked new files: 21 files, +2,821 / −89.

- **Product (6 files, the declared `A-89`/`A-97` breach):** `mapper/app.py` (+206),
  `mapper/views/layered.py` (+336), `mapper/widgets/rail.py`, `mapper/views/outline.py`,
  `mapper/views/state.py`, `mapper/keymap.py`.
- **Tests/fixtures (uncapped):** `tests/inc3_support.py`, `tests/test_inc3_census.py`,
  `tests/test_fold.py`, `tests/test_overflow.py`, `tests/test_pan.py` (all new),
  `fixtures/anidado.{mmd,yml}`, plus edits to six existing test modules.
- Spec: `01-requirements.md` LLRs `N06.*` and `LLR-COERCE.2`, amendments `A-89`/`A-97`/`A-98`;
  the binding architect ruling `02j-inc3-painted-set-architect.md`; the author's packet
  `increment-003.md` (treated as a claim throughout).

### Is the diff too large to review responsibly?

**The product diff is not — the test diff is at the limit.** ~600 lines of product across six files
is reviewable line by line, and I did that. ~1,700 new lines of test are not, in one pass: I read
the acceptance-bearing predicates and the five censuses directly, and delegated a second
independent pass (mutation + vacuity) rather than skim the remainder. **I did not read every line
of `test_fold.py` and `test_pan.py`.** Findings sourced from the delegated pass are marked
*(delegated, executed)*; I independently re-verified both HIGHs that came from it.

### Working-tree integrity

All mutation was done in exports under the session scratchpad, never in
`C:\Users\jjgh8\Github\mapper`. Proof by manifest, not by `git status`:

```
$ find mapper tests fixtures -type f \( -name '*.py' -o -name '*.yml' -o -name '*.mmd' \) \
    | sort | xargs sha256sum > POST_TREE.sha256
$ diff PRE_TREE.sha256 POST_TREE.sha256   &&  echo IDENTICAL
IDENTICAL (82 files, sha256 each)
bd6a09e2e76559c85084ce57a65bd8d6c78df69a3da07840859bf5a2b54b6c23  PRE_TREE.sha256
bd6a09e2e76559c85084ce57a65bd8d6c78df69a3da07840859bf5a2b54b6c23  POST_TREE.sha256
```

The only file this review adds to the tree is the one you are reading.

---

## What is genuinely right — stated first, because most of it is

These were checked by execution and are **clean**. They are not filler; three of them are the
items the brief flagged as historically wrong in this batch.

### The re-captured digest is legitimate, minimal, and correctly bounded

Independently re-derived from a clean `git archive 954f8f3` export with the increment's renderer
applied, using a re-implementation of `_fingerprint` (so a change to `test_repair_depth.py` could
not change my oracle):

```
=== LEGACY DIGESTS: pinned-in-work vs re-derived ===
key                                base==pin_base work==pin_work  base==work   verdict
LayeredRenderer|140|45                       True           True        True   UNCHANGED
LayeredRenderer|140|8                        True           True       False   CHANGED
LayeredRenderer|300|120                      True           True        True   UNCHANGED
LayeredRenderer|80|24                        True           True        True   UNCHANGED
OutlineRenderer|... (4 keys)                 True           True        True   UNCHANGED
RadialRenderer|...  (4 keys)                 True           True        True   UNCHANGED

=== RAIL DIGESTS ===
()             base==pin True  work==pin True  base==work True
erp            base==pin True  work==pin True  base==work True
fin            base==pin True  work==pin True  base==work True
fin|rrhh       base==pin True  work==pin True  base==work True
inv|fin|rrhh   base==pin True  work==pin True  base==work True

=== (140,8) LayeredRenderer ROW-BY-ROW ===
base rows=8  work rows=8
row 0 DIFFERS
  work.startswith(base): True
  added suffix: '  ▽ 4 fuera de vista'
rows differing: 1

=== (140,8) SPAN DELTA ===
base spans=258 work spans=259
spans only in work: [(233, 253, '#f5f5f5'), ...offset-shifted duplicates...]
```

(a) the old value really was stale (`base == pin_base`, `base != work`); (b) **exactly one row
differs**, the header, `work` starts with `base`, and the delta is exactly `  ▽ 4 fuera de vista`;
(c) the other 11 legacy digests and all 5 rail digests are **byte-unchanged**, so they were
verified rather than re-captured. Span delta is one new `INK` span over the suffix plus the
offset shift it forces. The claim in the re-capture comment matches the measurement verbatim.
**No finding.**

### `painted_ids` applies BOTH restrictions and shares one `_geometry` with `render`

`mapper/views/layered.py:315-330` (`_title_image`) carries the row bound
(`0 <= y < geo.body_h and y < geo.row_limit`) **and** the column bound
(`0 <= cx + 2 + j < geo.avail`), and `render` paints the title at `cx + 2` (`layered.py:440`,
`"▐ " + title`), so the offset matches. Both consumers call one `_geometry`. My re-implementation
of the predicate agrees with the shipped `painted_ids` at all 12 sizes tested.

**`painted_ids` does consume pan** — via `geo.place`, which subtracts `pan_x`/`pan_y` after the
shipped `max(0, ...)` clamp, in the order the docstring claims. I verified the declared set equals
a **pan-aware anchored trace of the composited frame** at live non-zero pan:

```
term=(60, 24) rend=(60,11)  1xL -> pan_x=  8 |declared|= 5 |traced|= 5 EQ=True
term=(70, 24) rend=(70,12)  2xL -> pan_x= 16 |declared|= 7 |traced|= 7 EQ=True
term=(80, 24) rend=(80,13)  2xL -> pan_x= 16 |declared|= 8 |traced|= 8 EQ=True
pan_graph (60,20) keys=LLJJ -> pan=(16,8)   |declared|= 5 |traced|= 5 EQ=True
```

The architect's risk row 5 is discharged **in the product**. It is *not* discharged in the tests —
see M3.

### `B-57` is CORRECT; amendment `A-98` is wrong, and so is the architect's own `MUT-B` row

`A-98` states `(30, 6)` discriminates the dropped-column mutant. Measured on `legacy`, holding
`_geometry` fixed so the only difference is the column predicate:

```
      size  |correct|  |MUT-B|  discriminates-B
  30x6              1        1  False
  30x8              3        4  True    B-extra: ['inv']
  30x12             6        8  True    B-extra: ['alm', 'inv']
  50x12             8        8  False
 140x8              4        4  False
```

At `(30, 6)` the row bound alone leaves one node and the column bound cannot change the answer.
The author is right, and right about the remedy: `tests/test_overflow.py:44-54` adds
`(30, 12, ())` / `(30, 12, ("erp",))` and asserts `len(driven) == 6`.

Note also that **`02j`'s table is wrong in the other direction** — it records `30x6 MUT-B
|declared| = 0`. Dropping a restriction cannot shrink the declared set; that probe was buggy.
`A-98` and `02j`'s mutant table should both be corrected. *(Spec/architecture defect, not a code
defect — no gate impact on this increment.)*

### `B-58` is CORRECT: `LLR-COERCE.2`'s headline threshold is inert

`darkside.plain` is `str.translate` over a map whose every value is a single character, so it is
1:1 and length-preserving; `_clip` truncates by index. The commutation is therefore an identity
regardless of coercion order. Executed against the **uncoerced** `_fit` at `954f8f3`:

```
[base] commutation over 176868 pairs: disagreements = 0
[base] code points where len(plain(c)) != 1 over U+0000..U+10FFF: 0
[base] leaked-code-point: _fit('a\x01b', 8) = 'a\x01b     '   control byte survives: True
[base] split-at-width:    _fit(balanced, 6) = 'ab\u202ecd…'   unterminated overrides = 1
[work] leaked-code-point: _fit('a\x01b', 8) = 'a�b     '      control byte survives: False
[work] split-at-width:    _fit(balanced, 6) = 'ab�cd…'        unterminated overrides = 0
```

The stated numeric threshold cannot fail; the discriminating arms are the leaked-code-point and
split-at-width ones. **The author acted on this correctly** — `tests/test_inc3_census.py:131`
labels a separate arm "THE DISCRIMINATING ARM", and the near-inert arm is documented as such in
its own docstring rather than sold as the oracle. The requirement text should be corrected.

### Fold ownership genuinely moved — the rename is not grep-satisfaction

`LLR-N06.2.1` says the rail shall not hold a collapsed set of its own. Executed census of every
reference in the product:

```
mapper/app.py:1136        self.folded: frozenset[str] = frozenset()      # __init__
mapper/app.py:1312-1313   self.folded = (self.folded - {nid} ...)        # action_collapse_branch
mapper/app.py:1586        folded=self.folded,                            # -> ViewState
mapper/app.py:1614        rail.show(self.graph, self.nav.cursor, self.folded)
mapper/widgets/rail.py:41 self.folded: frozenset[str] = frozenset()
mapper/widgets/rail.py:47 self.folded = folded                           # in show(), only writer
mapper/widgets/rail.py:83,225   read-only
```

`toggle` is deleted, the type is `frozenset` (no in-place mutation possible), the single writer is
`show()`, and `show()` has exactly one call site — inside `refresh_canvas`, which
`action_collapse_branch` always calls. **`MapScreen` is genuinely the single owner and the rail's
copy cannot go stale relative to the canvas.** No finding on the substantive question.

### Also verified clean *(delegated, executed)*

- The five censuses are **genuinely derived** (git `ls-files` → AST → executed shape filter;
  live `importlib` for the `painted_ids` participation pin, asserted `== {"mapper.views.layered"}`)
  and each guards non-emptiness before evaluating. Only `ENTRY_MAP_SEAT`
  (`tests/test_inc3_census.py:341`) is hand-typed; it was checked against the real base and
  matches exactly.
- Both "provably equivalent mutant" claims are **real equivalence**, not a missing oracle
  (clamp `E<W`: 164,800 triples, 0 disagreements, and provable; coercion ordering: 200,000 pairs,
  0 disagreements, because every replacement has length 1).
- The fixture-neutering defect class the author caught in themselves **does not have a surviving
  sibling**: removing the copy in `install()` makes the affected tests error loudly
  (`MapStoreError: Map not found` ×6) rather than pass on a one-node graph.
- Suite: **784 passed, 17 deselected (`slow`), 0 failed, 0 skipped.** No silent skips.

---

## Findings

### F1 — `_canvas_size`'s short-region branch declares a node painted when zero cards are painted  [Severity: HIGH]

- **Where:** `mapper/app.py:1368-1369`; carry note at `tests/test_overflow.py:259-266`.
- **What:** when the canvas region is real but no taller than the header, the branch returns
  `h = region.height` instead of `region.height - 1`. `row_limit = h - 1` then believes canvas
  row 0 survives, when the two-row header has already consumed the entire region. `painted_ids`
  declares a node painted that leaves no trace at all.
- **Executed** (frame rows are the composited region, exactly what the operator sees):

```
  legacy term=(31, 18)  canvas=(31,2) region.h=2 declared=['erp'] anchored=[]   <<< OVER-DECLARED
        row0: '◆ mapper · árbol legacy▰▰▰▰▰8  '
        row1: 'nodos  ▽ 7 fuera de vista      '
  legacy term=(50, 14)  canvas=(50,2) region.h=2 declared=['erp'] anchored=[]   <<< OVER-DECLARED
  legacy term=(100, 10) canvas=(64,2) region.h=2 declared=['erp'] anchored=[]   <<< OVER-DECLARED
  legacy term=(80, 24)  canvas=(80,14) region.h=15  declared == anchored (8 of 8)   OK
```

  Eight of eight nodes are hidden; the indicator declares **7**. Two independent oracles (the
  shipped `inc3_support.oracle_traced` and my anchored positional one) agree the truth is 8.
- **Why it matters:** this is the story's promise inverted by the mechanism that exists to keep it,
  and **the recorded carry bounds the wrong axis.** `tests/test_overflow.py:263-266` states the
  affected band is "exactly 20..29 columns of canvas". The failure is driven by
  `region.height <= HEADER_ROWS`, i.e. **short** terminals — `(50, 14)` and `(100, 10)` are
  ordinary geometries far outside the declared band. The docstring claim at `app.py:1360-1367`
  that this branch "is only for the first paint, before layout has given the widget a region" is
  false: layout had given it a real 2-row region in all three cases.
- **Suggested fix:** a region that cannot hold a body row has zero paintable rows, so say so
  once, in `_canvas_size`, and let `_geometry`/`_title_image` inherit it:

```python
region = self.query_one("#map-canvas", Static).region
if not region.height:                       # genuinely pre-layout
    return w, max(5, size.height - 8)
if region.height <= self.HEADER_ROWS:       # real, but the header fills it
    return w, 1                             # row_limit == 0 -> nothing declared painted
return w, region.height - (self.HEADER_ROWS - 1)
```

  and re-derive the carry note against the *height* axis, with the 72-size sweep rather than nine.

---

### F2 — the forbidden naive-fold-sum survives at the paint site; the overflow suite cannot see it  [Severity: HIGH]

- **Where:** `tests/test_overflow.py:271` (TC-039) and `:336-376` (TC-038). *(delegated, executed;
  mechanism corroborated by me directly.)*
- **What:** `LLR-N06.3.1` forbids adding a fold count to a viewport count. A "sum" cannot be
  expressed in a set-returning helper — it only manifests where a **count** is taken, which is
  `MapScreen._pagination_text`. Mutating exactly there:

```
=== MUTANT ===  painted strip : '▰▱▱▱▱▱▱   1/7  ▽ 6 fuera de vista'
=== CLEAN  ===  painted strip : '▰▱▱▱▱▱▱   1/7  ▽ 4 fuera de vista'
true hidden: 4    naive sum: 6
... all 10 tests in tests/test_overflow.py PASS
```

- **Why it matters:** TC-039's own docstring says it was "WRITTEN BECAUSE A MUTANT SURVIVED" and
  that "an inert predicate gets rewritten, not re-argued" — but it reads
  `screen._unpainted_ids()` (`:294`), the helper, **one layer below the surface the mutant
  changes**. TC-038 is the only test that reads the painted strip, and it never assigns
  `screen.folded`, so it runs at `folded = frozenset()` where the naive sum and the truth
  coincide. The rewrite landed one layer short of the mutant it was written for. That is a test
  giving false confidence about the exact clause it names — the HIGH criterion.
- **Suggested fix:** one line in TC-038, driving its existing strip assertion through the nested
  fold TC-039 already constructs:

```python
screen.folded = frozenset({"ops", "log"})   # naive sum 6, truth 4
screen.refresh_canvas()
await pilot.pause()
strip = "".join(rows_in(screen, screen.query_one("#map-pagination").region))
assert f"{len(screen._unpainted_ids())} fuera de vista" in strip
assert "6 fuera de vista" not in strip
```

---

### F3 — `B-56` understates its own defect: the declaration is absent, not merely stale, and it does not close at the first keypress  [Severity: HIGH]

- **Where:** `mapper/app.py:1220-1236` (the carry note), `:1176-1214` (`on_mount` →
  `refresh_canvas`).
- **What:** the overflow declaration is computed inside `refresh_canvas`, which `on_mount` calls
  **before layout**, and nothing recomputes it afterwards. The packet bounds this as *"the FIRST
  paint … the strip declared 4 hidden on a screen hiding 7 … Every later repaint is correct, so
  the window is one frame, closing at the first keypress."* Both halves of that bound are wrong
  as measured.
- **Executed**, after mount plus seven `pilot.pause()` calls (so: not the first frame):

```
map      term       keys   header/strip/TRUE  ->  after keys
legacy   (30, 20)   j      2/2/7 (ok=False)  ->  2/2/7   <<< STILL WRONG AFTER KEYPRESS
legacy   (30, 20)   jk     2/2/7 (ok=False)  ->  2/2/7   <<< STILL WRONG AFTER KEYPRESS
legacy   (50, 20)   j      None/None/4       ->  None/None/4   <<< STILL WRONG
legacy   (60, 20)   j      None/None/4       ->  None/None/4   <<< STILL WRONG
anidado  (50, 20)   j      2/2/4             ->  2/2/4   <<< STILL WRONG
legacy   (50, 20)   II     None/None/4       ->  4/4/4 (ok=True)
```

  and a single forced repaint, changing no state, corrects every case:

```
A) does one forced refresh_canvas() fix the declaration?
legacy  (40,20) rend=(40,6)  declared-hidden 2    TRUE 7  ->  7 (true 7)  FIXED
legacy  (50,20) rend=(50,7)  declared-hidden None TRUE 4  ->  4 (true 4)  FIXED
legacy  (60,20) rend=(60,9)  declared-hidden None TRUE 4  ->  4 (true 4)  FIXED
anidado (40,20) rend=(40,7)  declared-hidden 3    TRUE 5  ->  5 (true 5)  FIXED
anidado (60,20) rend=(60,9)  declared-hidden 2    TRUE 4  ->  4 (true 4)  FIXED
```

- **Why it matters:** three things the carry does not say.
  1. **The indicator is absent, not wrong.** At `legacy` 50x20 and 60x20 — ordinary sizes — half
     the map is off screen and the operator is told **nothing at all**. "Declared 4 when 7" is a
     miscount; "declared nothing when 4 are hidden" is the requirement's unwanted behaviour
     verbatim, and `LLR-N06.3.3`'s "absent means nothing is hidden" contract makes the absence
     *actively misleading* rather than merely incomplete.
  2. **The window does not close at the first keypress.** `j` and `j k` leave it stale: on
     `legacy` the initial cursor is the root, `next_sibling()` returns `None`, and no repaint
     occurs. The window is "until some action happens to call `refresh_canvas`", which for a
     reader who is just *looking at the map* — the whole of US-N06's use case — may be never.
  3. Consequently the cost/benefit in the carry is priced against the wrong defect. The two arms
     it declines to pay (`LLR-CNV.3.1`'s parent-walk, `B-50`'s export) are being weighed against
     "one stale frame"; they are actually being weighed against "the story's headline indicator is
     absent on the operator's first and possibly only look".
- **I am not ruling that the carry decision is wrong** — routing the fix through `HLR-CNV.3` may
  well be right. I am ruling that **a carry recorded with a measurement this far off cannot be
  accepted as evidence**, which is the same standard the increment applies to itself at
  `test_repair_depth.py:104` ("a red pin is evidence, a re-captured pin is a claim").
- **Suggested fix (either is acceptable):**
  - *Re-measure and re-bound the carry* before the gate: state that the indicator is **absent**
    at ≥2 ordinary sizes, that ordinary navigation does not clear it, and that one post-layout
    repaint clears it in 8/8 measured cases. Then re-take the carry decision on those numbers.
  - *Or* close it without touching focus, by recomputing only the declaration after layout —
    the two red arms are about `refresh_canvas`'s focus side effects, and the declaration does
    not need them:

```python
self.call_after_refresh(self._park_focus)
self.call_after_refresh(
    lambda: self.query_one("#map-pagination", Static).update(self._pagination_text())
)
```

    This leaves the canvas header stale for one frame (a smaller, honestly-bounded carry) while
    the strip — the surface the operator reads — is correct. **Unverified:** I did not execute
    that this leaves `LLR-CNV.3.1` and `B-50` green; the author should.

---

### F4 — one NEW ruff error, masked by a coincidental removal  [Severity: MEDIUM]

- **Where:** `tests/test_pan.py:16`.
- **What:** compared by *file + code*, not by total, against a fresh `git archive 954f8f3` export
  using the same ruff (0.8.4):

```
base total: Found 46 errors.     work total: Found 46 errors.
--- NEW in work ---
tests\test_pan.py:  F401 [*] `tests.inc3_support.height_offset` imported but unused
--- GONE from base ---
mapper\views\layered.py:  F401 [*] `mapper.model.Node` imported but unused
```

  (the `layered.py` one disappeared because `_matches` now uses `Node`).
- **Why it matters:** the gate condition is "**zero new**", not "same total". The unchanged total
  is a coincidence of one addition cancelling one removal, and reading only the count is exactly
  the kind of aggregate check this batch keeps removing. *(My count is 46, not the 28 in the
  brief — different ruff version or scope; the base/work delta is what the gate turns on and it
  is version-independent.)*
- **Suggested fix:** delete the unused import, or use `height_offset` in the test that was
  presumably meant to call it — check which, because an unused `height_offset` import suggests a
  pan test that was meant to measure its own size offset (`B-54`'s machinery) and does not.

---

### F5 — the shipped painted-trace oracle is unanchored and cannot distinguish colliding titles  [Severity: MEDIUM]

- **Where:** `tests/inc3_support.py:171-183` — `if image.strip() and any(image in row for row in rows)`.
- **What:** the predicate is "this substring appears **somewhere** in **some** row". When
  `card_w` floors at 9 the title budget is 6 cells, so distinct titles clip to the same image and
  the oracle traces them all off one card. Executed on `pan_graph` at 80x24, pan_x=24:

```
c2: place=(72,12)  row_ok=True   col_img='nive'  declared=True
c3: place=(72,16)  row_ok=False  col_img='nive'  declared=False
c4: place=(72,20)  row_ok=False  col_img='nive'  declared=False
c7: place=(72,32)  row_ok=False  col_img='nive'  declared=False
   -> unanchored oracle traces 21, anchored oracle traces 16, product declares 16
```

  I found this by having my own unanchored oracle produce a false disagreement; the product was
  right and the oracle was wrong. Re-running with a positional oracle restored agreement at every
  size and pan I tested.
- **Why it matters:** the oracle **over-traces**, which weakens `PRED-2` (`declared ⊆ traced`) —
  and `PRED-2` is the predicate `02j`'s table relies on to redden `MUT-A` (placed-not-painted). An
  over-tracing oracle makes spurious declared ids easier to "confirm". It has not gone wrong at the
  six shipped configurations (the delegated pass confirms the AT does redden under `MUT-B`), so
  this is a latent weakening, not an active false pass.
- **Suggested fix:** anchor to the columns the oracle already computes — no new coupling, it does
  not import `_geometry`:

```python
ink = [(cx + 2 + j, ch) for j, ch in enumerate(title)
       if 0 <= cx + 2 + j < avail and ch.strip()]
if ink and any(all(x < len(row) and row[x] == ch for x, ch in ink) for row in rows):
    traced.add(nid)
```

---

### F6 — the oracle takes no pan, and no configuration pans, so the pan × overflow identity has no oracle  [Severity: MEDIUM]

- **Where:** `tests/inc3_support.py:171` (signature `oracle_traced(graph, folded, w, rows)`),
  `tests/test_overflow.py:44-54` (`CONFIGURATIONS` is `(w, h, folded)` — no pan component).
- **What:** the architect's risk row 5 says "`painted_ids` must consume the same pan offsets
  `render` does, or the declared set is correct only for an un-panned canvas". The **product**
  discharges it; the **acceptance** does not, because the oracle subtracts no pan and therefore
  cannot be run panned at all.
- **Why it matters:** pan is half of the story. `AT-015`/`AT-016` verify the declaration only on a
  canvas that has never moved, so a future edit to `geo.place` would be caught by no acceptance
  arm. I verified by execution (transcript in "What is genuinely right") that the product is
  correct under pan today — so this is a **coverage gap, not a live defect**, and it is the reason
  it is MEDIUM rather than HIGH.
- **Suggested fix:** widen the oracle to `oracle_traced(graph, folded, w, rows, pan_x=0, pan_y=0)`
  with the one-line `cx -= pan_x; y -= pan_y`, and add one `(w, h, folded, pan)` row to
  `CONFIGURATIONS` where `pan_extent` reports live travel — bumping the asserted cardinality to 7
  so the row cannot be silently dropped.

---

### F7 — `inc3_support.pan_graph()`'s docstring is a false measurement  [Severity: MEDIUM]

- **Where:** `tests/inc3_support.py:51-58` — *"A map that overflows the canvas in BOTH axes at the
  declared 118x34."*
- **Executed** `pan_extent` on that exact fixture:

```
  118x34: max_pan_x=0   max_pan_y=1
  118x25: max_pan_x=0   max_pan_y=10
   80x24: max_pan_x=27  max_pan_y=11
   60x20: max_pan_x=47  max_pan_y=15
```

  At the size the docstring names, **horizontal pan is dead** and vertical travel is one cell.
  The cause is structural: `_geometry` shrinks `card_w` until the leaves fit `avail`, so
  `extent_x <= avail` unless `card_w` floors at 9. On the shipped fixtures horizontal pan is live
  only below ~50 columns:

```
  legacy   w=30  max_pan_x=17     legacy   w=50  max_pan_x=0
  legacy   w=40  max_pan_x= 7     legacy   w=118 max_pan_x=0
```

- **Why it matters:** a shared fixture whose docstring states a measured property it does not have
  is how a driver ends up exercising a no-op while looking like it exercised the feature — the
  defect class the author already caught once in this increment. *(The delegated pass reports the
  pan ATs guard themselves with `assert extent_x > span_x`, so I do **not** believe an arm is
  currently vacuous — the docstring is the finding.)* It is also worth surfacing as product
  feedback: `H`/`L` are inert at most realistic widths, and the operator gets
  `"borde del territorio"` on a map that visibly overflows vertically.
- **Suggested fix:** correct the docstring to the measured sizes, or resize the fixture until the
  claim is true at 118x34; and assert the property in the fixture rather than describing it.

---

### F8 — `HEADER_ROWS = 2` is pinned against width only, on one fixture's node count  [Severity: MEDIUM]

- **Where:** `tests/test_overflow.py:234-266` — the sweep is `for w in (30, 50, 58, 80, 140, 300)`
  on the 8-node `legacy` fixture.
- **What:** the header length also grows with `len(str(len(graph.nodes)))` and with the unpainted
  numeral, and at `w = 30` the margin is one cell *(delegated, executed)*:

```
nodes=  10 hidden=  7 hdr_len=56 2*avail=56 rows=2
nodes= 100 hidden= 97 hdr_len=58 2*avail=56 rows=3  <-- HEADER_ROWS=2 IS WRONG
nodes=1000 hidden=997 hdr_len=60 2*avail=56 rows=3  <-- HEADER_ROWS=2 IS WRONG
```

- **Why it matters:** the pin's own comment presents `HEADER_ROWS` as "a measurement and not
  folklore" (`app.py:1341-1348`), and the sweep begins at exactly the width where the invariant
  starts holding. Combined with F1, the constant is false on two axes the pin does not vary.
- **Suggested fix:** parametrise the pin over node count as well as width — the graph builders
  (`_balanced`, `_chain`) already exist — and derive the asserted `HEADER_ROWS` from the measured
  header rather than asserting a literal `2`.

---

### F9 — AT-016's non-degeneracy guard is tautological  [Severity: MEDIUM]

- **Where:** `tests/test_overflow.py:481` *(delegated, executed)*.
- **What:** `assert len({(w, h, folded) for w, h, folded in driven}) == 6` re-checks the literal
  `CONFIGURATIONS` table; `driven` is appended purely from the loop variables, so the assertion
  cannot observe the *results*. Forcing all six configurations to identical results still passes.
- **Why it matters:** the comment states the guard's purpose is that "all six agreeing on 8-of-8
  would be six copies of one case" — the assertion as written cannot detect that, so it reads as
  an anti-vacuity guard while being one itself.
- **Suggested fix:** assert over the *outcomes*, e.g.
  `assert len({(len(declared), len(traced)) for ... in results}) >= 3`, or assert directly that at
  least one configuration hides something and at least one hides nothing.

---

### F10 — the fold pill token is declared "ONCE" and then re-typed in the rail  [Severity: LOW]

- **Where:** `mapper/views/layered.py:19-25` vs `mapper/widgets/rail.py:226`.
- **What:** the constant's comment says the tokens are "each declared ONCE here" because "two
  copies of a token agree on the day they are written and drift the first time one is edited" —
  and `rail.py:226` writes `marker = "▸ "` literally, on the other surface showing the same fold
  state.
- **Why it matters:** small, but the comment makes a claim the code next door falsifies, and the
  rail marker and the canvas pill are precisely the two surfaces this LLR exists to keep in step.
- **Suggested fix:** import `FOLD_PILL_TOKEN` in `rail.py`, or drop the "declared ONCE" clause from
  the comment so it stops asserting something untrue.

---

### F11 — `render` duplicates the painted-set comprehension instead of reusing one helper  [Severity: LOW]

- **Where:** `mapper/views/layered.py:414-416` vs `:340-342`.
- **What:** the same expression `frozenset(nid for nid in ... if _title_image(graph, geo, nid).strip())`
  is written twice — once in `render` for the header numeral, once in `painted_ids`.
- **Why it matters:** they share `_geometry` and `_title_image`, so a drift is unlikely to change
  behaviour — but the module's own stated design principle is "one computation instead of two that
  agree today", and this is two.
- **Suggested fix:** `def _painted(graph, geo) -> frozenset[str]` on `_geometry`'s output; `render`
  and `painted_ids` both call it.

---

### F12 — navigation is fold-unaware: the cursor can enter a folded branch and disappear from both surfaces  [Severity: LOW]

- **Where:** `mapper/app.py:1805-1814` (`first_child` / `parent` / siblings via
  `NavigationModel`, which walks the graph); `mapper/widgets/rail.py:83`;
  `mapper/views/layered.py:517` (`if selected_id and selected_id in pos`).
- **What:** `NavigationModel` has no notion of `folded`, so `l` (first child) descends into a
  folded branch. The node is then absent from the canvas (`pos` excludes hidden nodes) and absent
  from the rail (which skips folded descendants), while the inspector and the crumb show it.
  Pressing `z` there mutates `self.folded` with no observable effect anywhere.
- **Why it matters:** no crash and no wrong count — `_hidden_ids` and `pill_ids` handle nesting
  correctly, and folding an already-hidden node changes nothing the operator can see. But for a
  story whose promise is that nothing is hidden without being declared, the *selection* going
  invisible is a coherence gap, and a silent `z` is the one case `LLR-N06.2.2`'s "nada que plegar"
  toast does not cover.
- **Suggested fix:** out of this increment's scope — carry it. If cheap: have
  `action_collapse_branch` return early with the same toast when
  `nid in _hidden_ids(index, self.folded)`.

---

### F13 — smaller items, no action required this increment  [Severity: LOW]

- `mapper/views/layered.py:504` — the removed-node ghost block applies `pan_y` (`gy = tree_bottom
  + 1 - geo.pan_y`) but not `pan_x`, so the diff footer does not pan horizontally with the tree.
  Plausibly intentional; undocumented.
- `mapper/views/layered.py:383-389` — `render` uses `geo.index` with no `None` check. Safe only
  because `render`'s two early returns exactly mirror `_geometry`'s two `None` cases; nothing pins
  that correspondence. One `assert geo is not None` (or a census over the two guards) makes the
  invariant visible.
- `mapper/views/layered.py:275-279` — `widest = max(... for nid in visible)` raises `ValueError`
  on an empty `visible`, reachable only if every node is hidden, which requires a cycle.
  `painted_ids` and `pan_extent` are called from `_reclamp_pan`/`_unpainted_ids` **outside**
  `refresh_canvas`'s try/except, so it would escape the sink guard. **Unverified** — I did not
  construct a loadable cyclic graph, and `OutlineRail._rows` already rejects cycles, so this may be
  unreachable.
- *(delegated)* `tests/inc3_support.py:176` — the oracle uses `card_w - 3` where the product's
  `title_width` also subtracts the changed-chip length; would disagree under `diff_active`, which
  no configuration exercises.
- *(delegated)* `tests/test_inc3_census.py:66` — `truncators()` walks only `tree.body`, so a
  truncator defined as a method escapes the census.
- *(delegated)* `tests/test_overflow.py:306` — TC-040 kills its mutant by crash
  (`KeyError: 'log'`), so `assert counts == [4]` never evaluates. Killed, but not for the
  documented reason; worth a note so the next reader does not trust the stated oracle.

---

## Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **Block — must fix HIGH findings before advancing**

**F1** and **F2** are straightforward defects with cheap, local fixes. **F3** is a judgement call I
am escalating rather than deciding: the carry may be the right call, but not on the numbers
currently recorded — re-measure it, then re-take the decision.

The rest of the increment is, on the evidence, unusually solid: the digest discipline held under
independent re-derivation, both of the author's contradictions of the spec (`B-57`, `B-58`) are
correct and were acted on rather than merely reported, the ownership migration is real, and the
censuses are genuinely derived. **The three HIGHs all sit in the same place — the boundary between
the geometry and the frame it claims to describe** — which is worth noting as a pattern rather than
three unrelated bugs.

---

## Evidence checklist

- [x] **Diff read in full** — product diff read line by line (`mapper/app.py`,
      `views/layered.py`, `widgets/rail.py`, `views/state.py`, `views/outline.py`, `keymap.py`);
      test diff read at the acceptance-bearing predicates and censuses, **not** line by line for
      `test_fold.py` / `test_pan.py` (stated in Scope).
- [x] **Correctness pass (edge / None / error paths)** — F1 (short region), F12 (cursor into a
      fold), F13 (empty `visible` → `ValueError` outside the sink guard; `geo is None`).
- [x] **Simplicity pass** — F11 (duplicated comprehension); `_geometry` extraction judged a sound
      pure move, confirmed by 11 of 12 digests byte-unchanged.
- [x] **Reuse / duplication checked** — F10 (`▸` re-typed in `rail.py:226` against its own
      "declared ONCE" comment); `_matches` and `_clip` correctly funnel their call sites.
- [x] **Tests reviewed for intent, not just behaviour** — F2 (TC-039 tests one layer below its
      named mutant), F5 (unanchored oracle), F6 (no pan arm), F9 (tautological guard),
      F7/F8 (fitted fixtures and pins).
- [x] **Verdict explicit** — BLOCK, 3 HIGH.
- [x] **Working tree unmodified and proven** — manifest sha256 `bd6a09e2…` identical pre/post over
      82 files; all mutation performed in scratchpad exports.
