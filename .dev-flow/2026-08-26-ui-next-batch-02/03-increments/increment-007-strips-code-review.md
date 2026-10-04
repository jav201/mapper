# Code Review — Inc-STRIPS (`2026-08-26-ui-next-batch-02`, increment 007)

**Reviewer:** code-reviewer (independent) · **Protocol:** FULL
**Subject:** `git diff HEAD -- mapper/ tests/` — `mapper/app.py` (+62/-2, three hunks) and net-new
`tests/test_strips.py` (+212, 6 arms), plus the `LLR-N07.3.4` amendment and packet
`increment-007-strips.md` treated as claims to check.
**Verdict:** **BLOCK** — **3 HIGH**

---

## BLUF

**The layout collapse is genuinely fixed and the count is genuinely readable at both declared
sizes. What is not sound is the predicate that says so, and the ledger of which bound did the
work.**

Three HIGHs, all measured:

1. **The acceptance predicate is unsound in BOTH directions, demonstrated.** It reads
   `" ".join(frame_rows(screen))` — the raw whole-frame join. At **60x34** it returns **False**
   while the count is fully readable on `#map-pagination` (a mid-phrase wrap plus right-padding
   breaks the match — a **false RED**). At **50x34** it returns **True** while `#map-pagination`
   does **not** carry the suspension notice at all (the frame-wide hit comes from `HintLine`, a
   different widget — a **false GREEN on the requirement's own clause**). Predicate 1 is
   region-scoped; the arm is not.
2. **The `+N ramas sin mostrar` declaration this increment adds is invisible at 80x24 on the
   increment's own fixture, and no arm in the tree can see it under any input.** Deleting the
   declaration entirely leaves **927 passed, 3 xfailed** — the full suite, all markers.
3. **`MINIMAP_BRANCHES = 24` is neither load-bearing nor observed.** With the cap disabled the
   count is still readable at both sizes (converse control executed), and the full suite is
   **927 passed** under `MINIMAP_BRANCHES = 10**9`.

Two claims in the packet are refuted by measurement and two are confirmed:

| packet claim | verdict |
|---|---|
| §2 "three causes, **each alone sufficient**", remedied together | **Refuted for causes 1 and 3.** Only `METER_STEPS` is necessary. |
| CSS comment `app.py:3251`: capping meter + branch list is "NECESSARY AND NOT SUFFICIENT" | **Refuted.** With both Python caps in and **both CSS rules deleted**, the count is readable at 118x34 and 80x24. |
| §3 the 2 fast arms "reach the same cause" as the slow ones | **Refuted.** `METER_STEPS = 10**9` → the 2 slow arms RED, all 4 fast arms GREEN. |
| §2.2 `max-height` not `height`; no small-map tax | **Confirmed, twice.** `height: 3` reddens 5 arms; and canvas height is byte-identical with and without the new rules across a 10-size grid. |
| ledger `908 passed, 19 deselected, 3 xfailed`; ruff 27 | **Confirmed**, re-executed at the pin. |

I also **correct the security review on one point**: its F3 states "`METER_STEPS` is uncovered
too: no arm reads the meter's content." Measured, that is wrong — `METER_STEPS = 10**9` reddens
both `AT` arms. `METER_STEPS` is the one bound in this increment that has an oracle.

---

## ⚠ Process disclosure — I was the concurrent writer named in the security review

The security review (`increment-007-strips-security-review.md`, "Tree state during this review")
records `mapper/app.py` being rewritten repeatedly, names the digests
`87a2e65f` / `c7b69287` / `2c6a173c` / `3fc74fd7`, and asks that the parallel code review "be
asked, not assumed" whether it took precautions.

**Those writes were mine.** They are my mutation harness (`MUT-D`, `MUT-H`, `MUT-A`, `MUT-C` in
that order), and the four-minute `2c6a173c` window is `MUT-A` running the whole suite. I was
briefed as sole writer with the implementer stopped; I was not told a security review was live,
and I did not check. That is my error and it cost the security reviewer a discarded probe pass.

State of the disclosure:

- **Nothing was left mutated.** Every mutation is applied in a `try` with the restore in
  `finally`, and the restore asserts the digest equals the declared pin before printing.
  Verified at the close of this review:
  ```
  $ sha256sum mapper/app.py tests/test_strips.py
  e839bd96fa3e1b25fd4b5f7e4b4b82d933605dac81079bcf3ba3648605e332aa *mapper/app.py
  e24f8d4322feefe245fa26636c2b31fa2da2cc40f07f083da60559773ede331b *tests/test_strips.py
  ```
  Both match the restore-to pins. `git status --porcelain` shows the same four entries it showed
  at review entry; no `__pycache__` survives; every run used `PYTHONDONTWRITEBYTECODE=1`.
- **The security review's F3 measurement is sound despite the provenance.** It ran against
  `2c6a173c`, which is exactly `MINIMAP_BRANCHES = 10**9` and nothing else; my own independent
  run of the same mutant reproduces its result (below).
- **The gate finding stands and I second it:** two reviews were dispatched in parallel with no
  writer protocol between them. That is the coordinator's to fix, not the implementer's.

---

## Method

- Every measurement below was executed on the tree **pinned to
  `e839bd96…` / `e24f8d43…`**, asserted before and after each run.
- Mutants are installed by plain-string replacement at a **verified occurrence count** — an
  anchor matching 0 times **aborts** and is never reported as a survival. The harness normalises
  each anchor to the target file's own EOL, because **this tree mixes them**
  (`mapper/app.py` is 3386 CRLF / 0 LF; `tests/test_strips.py` is 0 CRLF / 212 LF). My first
  battery reported four spurious ABORTs for exactly this reason and is discarded.
- After writing a mutant the harness asserts the **on-disk digest equals the digest of the bytes
  it intended to install**, before any verdict is read — the false-green class packet §4.1
  discloses. Every digest below is that assertion's output.
- Verdicts are by **resolved node id**, `--color=no`, `-p no:randomly`, no `-v`/`-q`.
- Layout probes are read-only: variations are applied to in-memory class attributes
  (`MapperApp.CSS`, `MapScreen.MINIMAP_BRANCHES`, `MapScreen.METER_STEPS`) and restored, never to
  a file. Frames are read through the real compositor (`tests.inc3_support.frame_rows` /
  `rows_in`).

**Baseline, at the pin:**
```
$ python -m pytest tests/test_strips.py -m "slow or not slow" --color=no -p no:randomly
6 passed in 31.71s
$ python -m pytest tests --color=no -p no:randomly
collected 930 items / 19 deselected / 911 selected
908 passed, 19 deselected, 3 xfailed in 207.80s
$ python -m ruff check .
Found 27 errors.
```
Ledger and ruff SET both match the packet.

---

## Q1 · Is the collapse fixed, and is the fix complete? — fixed; **the causal ledger is wrong**

Built the 12002-node / 4001-fanout case myself and drove a real `/`-search through the pilot.
**Post-fix, the count is readable at both declared sizes** — that much the packet has right:

```
--- post-fix ALL THREE bounded @ 118x34
    #map-canvas   y=5  h=24   #map-minimap y=2 h=3   #map-pagination y=29 h=2
    COUNT in frame: True   NOTICE in frame: True   count on frame row 29
--- post-fix ALL THREE bounded @ 80x24
    #map-canvas   y=5  h=14   #map-minimap y=2 h=3   #map-pagination y=19 h=2
    COUNT in frame: True   NOTICE in frame: True
```

**The converse control the packet asserts but did not execute** — bound only two of the three,
one variant per cause:

| variant | 118x34 count | 80x24 count |
|---|---|---|
| all three bounded (shipped) | **True** | **True** |
| CSS + `METER_STEPS`, **`MINIMAP_BRANCHES` disabled** | **True** | **True** |
| CSS + `MINIMAP_BRANCHES`, **`METER_STEPS` disabled** | **False** | **False** |
| `MINIMAP_BRANCHES` + `METER_STEPS`, **both CSS rules deleted** | **True** | **True** |

Read off that table:

- **`METER_STEPS` is the only necessary bound.** Uncapped, the meter's 12002 glyphs fill the
  three clipped rows and the count — appended after it — falls past the clip at both sizes.
- **`MINIMAP_BRANCHES` is not necessary at all.** The stylesheet clip already holds the strip at
  3 rows whatever `_minimap_text` returns.
- **The CSS rules are not necessary for the count** either, once both Python caps are in. They
  are still defensible as defence-in-depth ("unreachable by construction"), but that is a
  different and weaker claim than the one `app.py:3251-3252` makes in capitals.

So §2's table ("each cause alone suffices, so a partial remedy is no remedy") is inherited from
`Inc-4c`'s F-2 measurement of the **pre-fix** tree and was not re-derived against the **shipped**
remedy. Two of its three rows are over-remedied. That is not a defect in the code; it is a defect
in the record, and it is what F3 below turns into a real risk.

**Nothing is under-bounded for the fanout vector.** For the crumb vector — a fourth unbounded
strip that reproduces the collapse from one long title — see security F2; I confirm it is out of
scope for a 1-source-file increment and concur it must not be half-fixed here.

---

## Q2 · `max-height` vs `height` — **the implementer is right, and I could not find a size where it starves**

**`height: 3` really is a floor.** Installed, digest-verified:

```
===== MUT-E max-height -> height (the floor bug)
  installed digest 47fb5dda == intended 47fb5dda  OK
    FAILED tests/test_strips.py::test_the_ceiling_is_not_a_floor
    FAILED tests/test_strips.py::test_a_small_map_at_a_small_terminal_keeps_its_canvas
    FAILED tests/test_overflow.py::test_b60_the_declaration_follows_the_region_to_its_settle[legacy]
    FAILED tests/test_overflow.py::test_b60_the_declaration_follows_the_region_to_its_settle[anidado]
    FAILED tests/test_overflow.py::test_the_paint_site_differences_one_set_on_a_PARTIAL_overlap
    5 failed, 96 passed, 3 xfailed
  restored e839bd96 == pin  OK
```

The three `test_overflow.py` arms §2.2 names are exactly the three that fire, **and** the two new
regression arms fire with them — so those two arms are load-bearing and not decoration. Splitting
them across two sizes (§3.1) is correct: each is red for its own reason.

**And `max-height: 3` costs the ordinary map nothing.** Same 3-branch/9-node fixture, ten sizes,
measured with the shipped stylesheet and with the two new rules deleted:

```
     size    SHIPPED can/mini/pag   NO-RULES can/mini/pag  delta
  35x14                 (2, 3, 2)               (2, 3, 2)  canvas +0
  40x12                 (1, 3, 1)               (1, 3, 1)  canvas +0
  30x10                 (1, 3, 2)               (1, 4, 2)  canvas +0
  80x10                 (1, 2, 1)               (1, 2, 1)  canvas +0
 118x9                  (2, 1, 1)               (2, 1, 1)  canvas +0
  60x8                  (1, 2, 1)               (1, 2, 1)  canvas +0
  80x24                (15, 2, 1)              (15, 2, 1)  canvas +0
 118x34                (27, 1, 1)              (27, 1, 1)  canvas +0
  80x16                 (7, 2, 1)               (7, 2, 1)  canvas +0
  80x12                 (3, 2, 1)               (3, 2, 1)  canvas +0
```

**Delta is zero at every size.** The canvas *is* 1 row at 40x12, 30x10, 80x10 and 60x8 — but it
is 1 row without the rules too, so that starvation is **pre-existing and not this increment's**.
`max-height` is the right primitive and §2.2's argument holds as written.

---

## Q3 · Is the acceptance predicate sound? — **no. Both failure directions demonstrated.** → F1

See F1. Short version: it is a raw whole-frame join, so it both fabricates and destroys matches,
and one of its two clauses is satisfiable by a widget that is not the count region.

---

## Q4 · Are the fast arms a proxy for the slow ones? — **no, and the packet says they are**

```
===== MUT-B meter cap removed  (METER_STEPS = 10**9)
  installed digest 8e87a157 == intended 8e87a157  OK
    PASSED  test_the_strips_cannot_outgrow_their_ceiling[118x34]
    PASSED  test_the_strips_cannot_outgrow_their_ceiling[80x24]
    PASSED  test_the_ceiling_is_not_a_floor
    PASSED  test_a_small_map_at_a_small_terminal_keeps_its_canvas
    FAILED  test_at_llr_n07_3_4_the_count_is_READABLE_at_the_shipped_bound[118x34]
    FAILED  test_at_llr_n07_3_4_the_count_is_READABLE_at_the_shipped_bound[80x24]
    2 failed, 4 passed
```

```
===== MUT-G css bounds removed entirely
  installed digest 6bf2d1ee == intended 6bf2d1ee  OK
    FAILED tests/test_strips.py::test_the_strips_cannot_outgrow_their_ceiling[80x24]
    1 failed, 100 passed, 3 xfailed     (test_strips + test_overflow + test_search + test_fold + test_pan)
```

The two families are **complementary, not redundant** — which is fine, and better than the packet
claims in one direction and worse in the other:

- **The slow arms catch a defect the fast ones miss:** the meter cap. The fast arms assert
  `region.height <= 3`, which `max-height: 3` guarantees regardless of what the meter renders.
- **The fast arms catch a defect the slow ones miss:** deleting both CSS rules leaves both `AT`
  arms **green** (the Python caps alone keep the count readable) and reddens exactly one fast
  arm — `ceiling[80x24]`. Note the **118x34 twin survives**, because `MINIMAP_BRANCHES = 24`
  holds the unbounded strip to 3 rows at 118 columns and does not at 80. The two CSS rules are
  therefore pinned by **one arm at one size**.

§3's "the fast structural bounds reach the same cause without paying for 12002 nodes" is not
true of causes 1 or 2. **Recommend restating it as complementarity with the coverage named**, and
adding the arms F2/F3 ask for.

---

## Q5 · Is `24` derived? — **derived at 118 columns, and wrong at the other declared size**

The arithmetic checks out at exactly one width. 3 rows × 118 = 354 cells; caption 14 + legend 37
+ a 26-cell remainder token leaves ~277 for entries at ~12 cells each ≈ 23. Measured, 24 entries
plus the declaration plus the legend land on row 3 at 118 with essentially no margin:

```
min[2] |19 ░   rama 20 ░   rama 21 ░   rama 22 ░   rama 23 ░   +3977 ramas sin mostrar   █ completa ▒ media ░ baja ╱ sin datos|
```

At **80 columns — the other declared size, and `run_test`'s own default** — 24 entries want
**5 rows** and get 3, so row 3 ends mid-list:

```
min[2] |rama 13 ░   rama 14 ░   rama 15 ░   rama 16 ░   rama 17 ░   rama 18 ░   rama 19 |
```

Entries 20-23, the `+3977 ramas sin mostrar` declaration **and the entire legend** are off-frame.
Sweeping branch count with the fixture's own short titles, the legend is lost from **20 branches
up at 80 columns**; sweeping width on the 12002-node graph, **118 is the only width in
{60, 70, 80, 100, 118} where the declaration survives at all.**

**Does the minimap keep the job it exists for?** Up to 24 branches, yes — the glyph and the name
are adjacent and coerced. Past 24 at 118 columns, yes with a declared remainder. **At 80 columns
it does not**: the operator reads coverage glyphs with **no legend key** and no statement that
anything is missing. `legacy`'s eight branches are unaffected, which is precisely why nothing in
the tree noticed. This is F2.

---

## Q6 · The declared remainder — `INK` is right, the citation is not, and nothing observes either

- **Coercion: clear.** `f"+{undrawn} ramas sin mostrar   "` interpolates `undrawn = len(children)
  - MINIMAP_BRANCHES`, an `int` from two `int`s. No file-derived substring reaches it. The slice
  is taken on the **id** list before the loop and `darkside.plain` is applied inside the loop, so
  every drawn title is still coerced and titles past the cap are never read. (Security Q1 reaches
  the same conclusion by the same reading; I concur and do not re-litigate the lane.)
- **`INK` is the right token — but `#D28` does not say so.** `01-requirements.md:2183-2186` reads:
  *"`MUT` is legal for READABLE, load-bearing text **only on `GROUND`**, where it clears the floor
  (4.43 : 1) … **Any `MUT`-on-`PANEL` readable-text seat escalates to `INK`**."* `#map-minimap`
  inherits `Screen`'s ground **today**, so the escalation clause does not fire and `MUT` would be
  legal. `app.py:1767-1772` cites the rule as though it did. The real reason is the one in the
  comment's second half — a hypothetical future `PANEL` background — plus contrast against the
  `MUT` branch names beside it. Both are good reasons; the citation is not. **LOW (F10).**
- **A related inconsistency, out of this diff:** the comment justifies `INK` by "the role it
  names the minimap caption under", and `01-requirements.md:2176` rules that caption (`V8`) to
  `INK` — yet `app.py:1750` still paints `("  cobertura   ", darkside.MUT)`. Pre-existing;
  flagged for the batch, not for this increment.
- **No oracle, either way.** `MUT-H` repaints the declaration `MUT`: **927 passed, 3 xfailed**.
  Gate checklist item "`#D28` honoured — [x]" rests on argument alone.

---

## Q7 · Did anything else regress? — no, and the reverse census is accurate

Re-swept `step_meter` · `map-minimap` · `map-pagination` · `_minimap_text` · `_pagination_text`
across `tests/`: the six files §5 names are the six that reference these surfaces. Full suite at
the pin is `908 passed, 19 deselected, 3 xfailed` (default lane) and `927 passed, 3 xfailed`
(all markers) — no pre-existing arm moved, and `test_overflow.py` is the one that fired during
development, correctly, per §2.2. **§5 and §6's ledger are accurate as written.**

---

## Findings

### F1 — The acceptance predicate is unsound in both directions: a false RED at 60 columns and a false GREEN on the requirement's own clause at 50 [Severity: HIGH]

- **What:** `tests/test_strips.py:118-126` builds
  `frame = " ".join(frame_rows(screen))` and asserts `SEARCH_COUNT_SUBJECT in frame` and
  `SEARCH_SUSPENDED_NOTICE in frame`. Three separate defects in one line:
  1. `frame_rows` returns **full-width, right-padded** rows, so a raw join inserts the padding
     into the middle of any phrase that wraps → **false RED**.
  2. The join spans the **whole frame**, so a phrase split across a wrap can be re-glued from two
     unrelated rows → **false GREEN by construction**.
  3. Predicate 1 is scoped to **the count region**; `SEARCH_SUSPENDED_NOTICE` is painted by
     **two** widgets (`_suspended_count_line`, `app.py:1934`, and `_search_hint`,
     `app.py:2598`), so the frame-wide read cannot tell them apart → **false GREEN on the clause**.

- **Where:** `tests/test_strips.py:118-126`, against `.dev-flow/…/01-requirements.md:3160-3161`
  ("**the count region** names the query, carries the whole-graph count … and carries the
  suspension notice").

- **Measured — the false GREEN, 12002 nodes, 64-char query, 50x34:**
  ```
  ### 50x34  #map-pagination y=27 h=3 (content wants 185 cells = 4 rows)
    region[0] | ▰▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱   1/12002  búsqueda:    |
    region[1] |«ramazzzzzzzzzzzzzzzzzzzzzzzzzzz…» · 0            |
    region[2] |coincidencias en el mapa · esc limpiar · resaltado|
    SHIPPED ARM  SEARCH_SUSPENDED_NOTICE in ' '.join(frame_rows) = True
    REGION       SEARCH_SUSPENDED_NOTICE on #map-pagination       = False
    notice found on 1 whole frame row(s):
      |siguiente ▸ resaltado y recorrido suspendidos ·   |
  ```
  The strip's content wants 4 rows and gets 3. The notice — **and the `▽ N fuera de vista`
  overflow declaration behind it** — are clipped off `#map-pagination` entirely. The arm passes
  because `HintLine`, a different widget, carries the string.

- **Measured — the false RED, same graph and query, 60x34:**
  ```
  ### 60x34  #map-pagination y=28 h=3 (content wants 185 cells = 4 rows)
    region[1] |«ramazzzzzzzzzzzzzzzzzzzzzzzzzzz…» · 0 coincidencias en el  |
    region[2] |mapa · esc limpiar · resaltado y recorrido suspendidos  ▽   |
    SHIPPED ARM  SEARCH_COUNT_SUBJECT in ' '.join(frame_rows) = False
    REGION       SEARCH_COUNT_SUBJECT on #map-pagination       = True
  ```
  The count is on the region and readable. The arm's predicate says False, because the join
  produces `…en el` + `  ` + `mapa…`.

- **And at 80x24 — a declared size — the arm already passes on a joining artifact.** On the
  shipped tree with the shipped fixture, `SEARCH_COUNT_SUBJECT` appears on **no single composited
  row** (`count on frame rows: []`); the whole-frame join happens to re-glue it because the wrap
  landed on the phrase's own space. Green today, at the mercy of one column of chrome.

- **Why it matters:** `LLR-N07.3.4` predicate 1 is being marked **✅ CLOSED** on this arm.
  Measured, the arm can be green at a width where the count region does not carry the notice
  — which is the "hidden state one surface over" defect the batch exists to close, closed by
  the fix for it. `MUT-C` confirms the arm cannot see the region: dropping
  `SEARCH_SUSPENDED_NOTICE` from `_suspended_count_line` leaves all **6 arms green**; the kill
  comes only from three **pre-existing** `test_search.py` arms — which reach the branch by
  **lowering `MAX_RENDER_NODES`**, the moved bound this increment exists to stop relying on.
  ```
  ===== MUT-C notice dropped from the COUNT REGION only
    installed digest 3fc74fd7 == intended 3fc74fd7  OK
      FAILED tests/test_search.py::test_above_the_bound_the_count_line_declares_the_search
      FAILED tests/test_search.py::test_the_suspended_declaration_is_actually_in_the_frame
      FAILED tests/test_search.py::test_a_line_bearing_query_does_not_take_the_frame
      3 failed, 924 passed, 3 xfailed
  ```
  So **no arm asserts predicate 1 on the count region at the shipped bound** — which is the exact
  gap the increment was chartered to close.

- **The predicate is also missing a clause the requirement spells out.** Predicate 1 requires the
  **whole-graph count `== len(SearchIndex(graph).query(q))`**. The arm asserts only that the
  *subject string* appears; the numeral is never compared. `M-N07.3.4-b`'s sibling — paint the
  count with a wrong number — is green on this arm.

- **Suggested fix — the idiom already exists in this tree, 400 lines from where it was needed.**
  `tests/test_search.py:2377-2381` records the whitespace trap and its remedy verbatim
  (*"a raw join reads `resaltado y      recorrido suspendidos` … a wrap is not a word"*).
  Reuse it, at the shipped bound:
  ```python
  from mapper.app import COUNT_REGION_ID, SEARCH_ACTIVE_LABEL
  from mapper.search import SearchIndex          # already imported by tests/test_search.py
  from tests.inc3_support import rows_in

  region = screen.query_one(f"#{COUNT_REGION_ID}").region
  rows = rows_in(screen, region)
  assert rows, f"at {size} the count region is off-viewport"
  joined = " ".join(" ".join(rows).split())      # a wrap is not a word
  tally = len(SearchIndex(graph).query("rama"))
  assert SEARCH_ACTIVE_LABEL in joined, joined   # "names the query"
  assert "rama" in joined, joined
  assert str(tally) in joined, (tally, joined)   # the clause the arm is missing
  assert SEARCH_COUNT_SUBJECT in joined, joined
  assert SEARCH_SUSPENDED_NOTICE in joined, joined
  ```
  This is red under `MUT-C`, red under `MUT-B`, and immune to both join artifacts. **It will also
  be red at 50 columns on today's tree** — correctly, and that red is F2's other half.

---

### F2 — The declaration this increment adds is invisible at 80x24 on its own fixture, and the entire 927-arm suite is blind to it [Severity: HIGH]

- **What:** `_minimap_text` caps the branch **count** but not the branch **cells**: the title is
  `darkside.plain(...)`-coerced and never `darkside.fit`-ed, and the declaration plus the legend
  are appended **last**, so they are the first things `max-height: 3` eats. At 80 columns the
  fixture's own 6-7-cell titles are already enough.

- **Where:** `mapper/app.py:1750-1780` (`_minimap_text` — unbounded `name` at `:1761`,
  declaration appended at `:1773`, legend after it) × `mapper/app.py:3266` (the clip).

- **Measured**, 12002 nodes / 4001 branches, titles `rama 0`…`rama 23`:

  | size | minimap h | content wants | legend on frame | `ramas sin mostrar` on frame |
  |---|---|---|---|---|
  | 118x34 | 3 | ~4 rows | **True** | **True** |
  | **80x24** | **3** | **~5 rows** | **False** | **False** |

  Short-title branch sweep (no hostile input at all):

  | branches | 118x34 legend | 80x24 legend |
  |---|---|---|
  | 8 (`legacy`) | True | True |
  | 16 | True | True |
  | **20** | True | **False** |
  | 24 | True | **False** |

  Width sweep on the 12002-node graph: declaration on frame at 118 only — **False at 100, 80, 70
  and 60**.

- **Why it matters:** `app.py:1742-1744` and packet §2.1 both state the remainder is *"DECLARED
  rather than silently dropped … the same contract `_degraded` and the overflow token already
  keep."* **At the second declared size it is silently dropped**, along with the key to the very
  glyphs the strip exists to communicate. The increment traded a visible collapse for an
  invisible omission on the surface it was fixing. (Security F1 reaches the same finding from the
  hostile-title direction; this is the same defect reachable with **no hostile input and no
  hostile size** — the acceptance fixture, at a declared size.)

- **And nothing can see it.** Deleting the declaration outright:
  ```
  ===== MUT-D declared remainder deleted
    installed digest 87a2e65f == intended 87a2e65f  OK
      927 passed, 3 xfailed in 267.81s        (tests/, -m "slow or not slow")
    restored e839bd96 == pin  OK
  ```
  A behaviour shipped with no oracle at all is the *"shipping an unobserved behaviour on a green
  suite"* failure `_count_line`'s own docstring (`app.py:2000-2003`) names as "the exact failure
  this batch is spending its budget to stop".

- **Suggested fix** (all inside `_minimap_text`, no new file):
  1. **Bound the entry by cells, using the helper the module already owns** — `darkside.fit`
     calls `plain` internally and truncates with a visible ellipsis, so coercion is preserved and
     the loss becomes legible instead of silent:
     ```python
     name = darkside.fit(self.graph.nodes[cid].ficha.title or cid, _MINIMAP_NAME_CELLS)
     ```
  2. **Reserve the declaration and the legend before spending on entries** — the pattern
     `_HINT_NAME_OVERHEAD` / `_HINT_NAME_MIN_CELLS` already establishes at `app.py:110-125`
     ("the affordances outrank it"). Derive the entry budget as the remainder of
     `3 × width − caption − legend − declaration`, so the declaration cannot be what the clip
     eats.
  3. **Add the frame-level arm.** At 40 branches, both declared sizes, assert
     `"ramas sin mostrar"` and the legend's `"sin datos"` appear in `frame_rows(screen)`, and
     that the frame shows exactly `MINIMAP_BRANCHES` entries — derived from the constant, not
     re-typed. Red on today's tree at 80x24; red under `MUT-A` and `MUT-D`.

---

### F3 — `MINIMAP_BRANCHES = 24` is neither load-bearing nor observed: the full suite is green with the cap disabled [Severity: HIGH]

- **What:** the cap does nothing the stylesheet is not already doing, and no arm anywhere in the
  tree can tell whether it exists.

- **Where:** `mapper/app.py:1745` (`MINIMAP_BRANCHES = 24`) and `app.py:1751`
  (`children[: self.MINIMAP_BRANCHES]`).

- **Measured, both halves:**
  ```
  ===== MUT-A minimap list cap removed  (MINIMAP_BRANCHES = 10**9)
    installed digest 2c6a173c == intended 2c6a173c  OK
      927 passed, 3 xfailed in 278.48s        (tests/, -m "slow or not slow")
    restored e839bd96 == pin  OK
  ```
  ```
  converse control, 12002 nodes, cap disabled, CSS + METER_STEPS in place:
    118x34  canvas h=24  minimap h=3  pagination h=2  COUNT True  NOTICE True
     80x24  canvas h=14  minimap h=3  pagination h=2  COUNT True  NOTICE True
  ```
  Under `10**9` the slice is every child, `undrawn` is always `<= 0`, and **the new declaration
  never renders under any input** — and the suite still reports 927 passed.

- **Why it matters:** three compounding consequences.
  1. **The increment's own §4 counterfactual cannot detect this**, because it installs the
     **whole pre-fix file** and reverts CSS and both caps together. A whole-file counterfactual
     can only say the change as a whole matters; it can never say **which part** the arms
     actually observe. Per-constant mutation takes seconds and distinguishes them.
  2. **A future edit ships green.** So does an unrestored harness — as this very review's process
     incident demonstrates: `MINIMAP_BRANCHES = 10**9` sat committable for four minutes with an
     identical `git diff --stat`.
  3. **The gate checklist over-reports.** "Counterfactual executed per arm — [x]" is true at file
     granularity and false at constant granularity, and §4's own ledger shows why: the two arms
     that redden pre-fix are the two that redden under `MUT-B` as well, so `METER_STEPS` is the
     only bound §4 actually exercised.

- **Correction to the security review, measured:** its F3 concludes "by the same structure
  `METER_STEPS` is uncovered too: no arm reads the meter's content, only its region's height."
  That is wrong. The `AT` arms read the **composited frame**, and an uncapped meter fills the
  three clipped rows and pushes the count past them — `MUT-B` reddens both, at both sizes (Q4
  above). **`METER_STEPS` is covered; `MINIMAP_BRANCHES` is not.**

- **Suggested fix:**
  1. **Add the cap-sensitive arm** described in F2's fix 3 — one arm closes F2 and F3 together.
  2. **Re-run the counterfactual per constant** and carry the resulting table in §4 in place of
     the whole-file verdict:

     | mutant | arms red |
     |---|---|
     | `MINIMAP_BRANCHES = 10**9` | **none (927 passed)** |
     | `METER_STEPS = 10**9` | `AT[118x34]`, `AT[80x24]` |
     | CSS rules deleted | `ceiling[80x24]` only |
     | `max-height` → `height` | 5 (2 new + 3 `test_overflow`) |
     | declaration deleted | **none (927 passed)** |
     | declaration `INK` → `MUT` | **none (927 passed)** |
  3. **Or delete the cap** and rely on the clip. I do **not** recommend this — the cap bounds
     `_branch_coverage_glyph`'s per-branch subtree walk and is the right place to bound the
     minimap — but if it stays, it must be observed and it must be a **cell** budget (F2).

---

### F4 — `_minimap_text` re-implements one third of the strip budget this module already owns, and repeats the mistake that budget's own comment records [Severity: MEDIUM]

- **What:** `app.py:110-125` already solves "bound a strip that lists file-derived branch titles":
  a branch cap (`_HINT_BRANCHES`), **a per-name cell cap** (`_HINT_BRANCH_CELLS`), **a reserved
  chrome overhead** (`_HINT_NAME_OVERHEAD`) and **a drop floor** (`_HINT_NAME_MIN_CELLS`).
  `MINIMAP_BRANCHES` adopts the first and skips the other three.
- **Where:** `mapper/app.py:1745-1780` against `mapper/app.py:110-125`.
- **Why it matters:** that comment states the failure this increment reproduced, in advance and
  in capitals: *"THE CELL BUDGET IS THE ROW'S REMAINDER, not a constant, and that was measured: a
  fixed 40 cells fits at 118 columns and WRAPS at 80."* `MINIMAP_BRANCHES = 24` is a fixed budget
  derived at 118 that fails at 80 (Q5, F2) — the same defect, on the strip directly above, 1600
  lines down. The batch's `#7`/`#11` posture is to reuse the settled pattern, not re-derive a
  weaker one.
- **Suggested fix:** fold into F2's fix — make the entry budget the row remainder after reserving
  the caption, the legend and the declaration, and put the arithmetic beside the constant the way
  `_HINT_*` does.

---

### F5 — Three comments now assert the opposite of the shipped code, one of them inside this increment's own hunk [Severity: MEDIUM]

- **What / where:**
  1. **`mapper/app.py:2027-2046` — inside the diff.** The paragraph beginning *"THE METER IS
     STILL UNBOUNDED HERE, DELIBERATELY, AND BOUNDING IT IS NECESSARY BUT NOT SUFFICIENT"* was
     **retained**, and the new paragraph *"THE METER IS BOUNDED HERE"* appended beneath it at
     `:2047`. The first sentence a reader meets in `_pagination_text` is now false about the code
     three lines below it. The retained block also still says a 24-step cap "takes the region to
     2 rows but it is still laid out at y=55" — a pre-fix measurement now presented as current.
  2. **`mapper/app.py:95-97`** — *"the count region WRAPS rather than clips (`#map-pagination`
     has no height rule, so it is `height: auto`) … it GROWS the strip and takes the rows from
     `#map-body`"*. It now clips (`app.py:3267`). This is the stated justification for
     `_QUERY_ECHO_CELLS`, and it is now the wrong justification: the cap's job became protecting
     the strip's **content from the clip**, not `#map-body` from the strip. (Security F5 reports
     this one; I concur and add that F1's 50x34 measurement shows the new failure mode is live —
     the echo cap is no longer sufficient there.)
  3. **`mapper/app.py:1831`** (`_query_echo`: *"a region that WRAPS"*) and
     **`tests/test_search.py:2339`** (*"`#map-pagination` has no height rule, so it is
     `height: auto` and it WRAPS"*) carry the same now-false premise.
- **Why it matters:** this increment sets its own standard at `app.py:2033-2035` — it corrects a
  wrong comment **in place** and says why, because "a reader who trusts it bounds the minimap
  alone and the count is still unreadable". Four comments one screen away were left to say the
  opposite of the shipped stylesheet.
- **Suggested fix:** strike the retained paragraph at `:2027-2046` in place (keeping the
  superseded text under a `STRUCK` header, per the batch's own convention) rather than appending
  a contradiction; amend `:95-97`, `:1831` and `test_search.py:2339` the same way.

---

### F6 — `filled = min(page, steps)` is a clamp, and the comment beside it claims a compressed scale [Severity: MEDIUM]

- **What:** `app.py:2054-2055`:
  ```python
  steps = min(per_page, self.METER_STEPS)
  filled = min(page, steps)
  ```
  `app.py:2050-2051` says *"Past the cap the bar stops being a one-to-one scale and becomes a
  compressed one."* It does not compress — it **clamps**. Compression would be
  `round(page / per_page * steps)`.
- **Where:** `mapper/app.py:2047-2055`.
- **Why it matters:** unobservable today (`page` is the literal `1` three lines up, so `filled`
  is always 1), which is exactly what makes it a trap. The reserved affordance's whole purpose is
  that someone later wires pagination — at which point `page = 5000, per_page = 12002` renders a
  **completely full** 24-block bar, i.e. the bar reports "at the end" while the numerals beside
  it read `5000/12002`. The one thing `app.py:2051-2053` promises ("the numerals carry the truth
  the bar can no longer carry") becomes a bar that actively contradicts them.
- **Suggested fix:** pick one and say which — either write the scale now,
  ```python
  filled = max(1, round(page * steps / per_page)) if per_page else 0
  ```
  or keep the clamp and correct the comment to *"`page` is the literal 1 today, so this is a
  clamp, not a scale; wiring pagination must replace it with `page * steps / per_page`."*
  Simplicity favours the second.

---

### F7 — Convention: the two caps are class attributes where every other render cap in this module is a module-level constant [Severity: LOW]

- **What:** `MINIMAP_BRANCHES` (`app.py:1745`) and `METER_STEPS` (`app.py:2019`) are `MapScreen`
  class attributes. Every other render cap here is module-level `_UPPER_SNAKE` with its
  arithmetic beside it: `_QUERY_ECHO_CELLS` (`:102`), `_HINT_BRANCHES` / `_HINT_BRANCH_CELLS` /
  `_HINT_NAME_OVERHEAD` / `_HINT_NAME_MIN_CELLS` (`:122-125`), `MAX_RENDER_NODES`.
- **Why it matters:** minor, but it changes how a test derives them — `from mapper.app import
  MapScreen; MapScreen.MINIMAP_BRANCHES` instead of the module constant every other budget arm
  imports — and the batch's rule is conformance over taste.
- **Suggested fix:** move both to module level beside `_QUERY_ECHO_CELLS`, keeping the comments
  verbatim. (Zero behaviour change; do it in the same pass as F2 so the file count does not move.)

---

### F8 — `overflow: hidden` on the two new rules is observationally inert [Severity: LOW]

- **What / where:** `mapper/app.py:3266-3267`. Removing `overflow: hidden` from **both** rules
  and keeping `max-height: 3`:
  ```
  ===== MUT-F overflow:hidden removed, max-height kept
    installed digest 9c864c88 == intended 9c864c88  OK
      101 passed, 3 xfailed        (test_strips + test_overflow + test_search + test_fold + test_pan)
  ```
  and the composited frames are identical at both declared sizes on the 12002-node graph
  (region heights, and all of count / notice / overflow-token presence).
- **Why it matters:** not a bug — but the CSS comment at `app.py:3255` argues the fix as *"a
  fixed height **plus a clip**"*, and the clip half is doing nothing measurable. Either it is
  redundant with the widget default and should go (simplicity), or it is guarding a case no arm
  reaches and the comment should name that case.
- **Suggested fix:** drop the two `overflow: hidden` declarations, or name the case they guard.
  **Do not drop them before F2's cell bound lands** — adding a clip to a strip whose content is
  not cell-bounded is how F2 came to exist, and removing one is the same decision in reverse.

---

### F9 — `#D28` is cited for an escalation the rule does not make here [Severity: LOW]

- **What / where:** `mapper/app.py:1767-1772` and packet §2.1 justify `INK` as *"the same
  load-bearing role the rule escalates"*. `01-requirements.md:2183-2186` escalates only
  **`MUT`-on-`PANEL`**; `MUT` on `GROUND` is explicitly *legal* for readable load-bearing text at
  4.43 : 1, and `#map-minimap` is on `GROUND`.
- **Why it matters:** `INK` is still the right call — for the comment's second reason (a future
  `PANEL` ground) and for contrast against the `MUT` branch names beside it. But a rule cited for
  something it does not say is how a rule gets over-applied later and kills the dim tier the same
  clause carves out an exemption to protect.
- **Suggested fix:** restate as *"`#D28` permits `MUT` here (this strip is on `GROUND`); `INK` is
  chosen anyway so the declaration survives a future `PANEL` ground and reads distinctly against
  the `MUT` names beside it."* Related, **out of this diff**: `app.py:1750` still paints the
  minimap caption `MUT` although `01-requirements.md:2176` rules `V8` to `INK` — for the batch,
  not for this increment.

---

## Evidence checklist

- [x] **Diff read in full** — `mapper/app.py` hunks at `:1734-1780`, `:2016-2060`, `:3246-3267`;
      `tests/test_strips.py:1-213`; `01-requirements.md:3162-3179`; packet §1-§7.
- [x] **Correctness pass (edge / None / error paths)** — `undrawn <= 0` guarded;
      `children_of` returns a list so the slice is safe; `steps >= 1` so `step_meter` never sees
      `total <= 0`; `filled` clamp is latently wrong (F6). No `None`/empty path introduced.
- [x] **Simplicity pass** — F3 (`MINIMAP_BRANCHES` buys nothing the clip does not),
      F8 (`overflow: hidden` inert). No premature abstraction; both caps are plain constants.
- [x] **Reuse / duplication checked against existing utils** — F4 (`_HINT_*` strip budget not
      reused), F1 fix (the `rows_in` + whitespace-collapse predicate at `test_search.py:2377`
      already exists and was re-implemented weaker).
- [x] **Tests reviewed for intent** — 8 mutants installed and digest-verified; `MUT-A`, `MUT-D`,
      `MUT-H` survive the **full 927-arm suite**; `MUT-C` survives all 6 new arms; `MUT-B` is
      killed only by the slow pair; `MUT-F` survives 101 arms; `MUT-G` is killed by one arm at
      one size; `MUT-E` is killed by 5, confirming §2.2.
- [x] **Tree restored and asserted** — `mapper/app.py` `e839bd96…`, `tests/test_strips.py`
      `e24f8d43…`, both equal to the declared pins; `__pycache__` purged;
      `PYTHONDONTWRITEBYTECODE=1` throughout; `908 passed, 19 deselected, 3 xfailed` and
      ruff `27` re-executed at the pin.
- [x] **Verdict explicit** — below.

---

## Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **Block — must fix HIGH findings before advancing**

**HIGH findings: 3 (F1, F2, F3).**

- **F1 blocks the requirement closure.** `LLR-N07.3.4` predicate 1 must not be marked ✅ CLOSED on
  a predicate that is demonstrably green at a width where the count region does not carry the
  notice, and that omits the numeric clause the predicate spells out. The fix is small and the
  idiom already exists in the tree.
- **F2 blocks the code.** The declaration the increment adds is not on the frame at 80x24 with
  the increment's own fixture — a declared size, no hostile input. Cell-bound the entry and
  reserve the declaration ahead of it.
- **F3 blocks the gate claim.** Two of the three bounds shipped have no oracle
  (`MINIMAP_BRANCHES` none at all, the CSS pair one arm at one size), and §4's whole-file
  counterfactual cannot see that. Add the arm F2 names and re-run the counterfactual per
  constant.

**What is right, and should not be re-litigated:** the collapse is fixed; `max-height` over
`height` is correct and measured (zero canvas cost across ten sizes); `METER_STEPS` is the bound
that does the work and it **is** covered by the two `AT` arms; §5's reverse census and §6's
ledger are accurate; the `AT` arms drive the shipped bound rather than a moved one, which is a
real advance over every prior above-bound arm in this batch; and the coercion story around the
new string is clean.

**Also for the coordinator, not the implementer:** two independent reviews were dispatched onto
one working tree with no writer protocol between them, and my mutation harness contaminated the
security reviewer's first probe pass. Serialise the gates, or give each reviewer a worktree.

**Handoffs:** security concerns (the `TabStrip` crumb vector, `#map-toast`, the `str(path)` export
carry) are `security-reviewer`'s and are already filed — I do not duplicate them. Whether the
minimap remains *usable* without its legend at 80 columns is a `ux-reviewer` question that F2's
fix should be re-walked against.
