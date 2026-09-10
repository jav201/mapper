# Security Review — Inc-STRIPS (`2026-08-26-ui-next-batch-02`, increment 007)

**Reviewer:** security-reviewer (independent) · **Protocol:** FULL
**Subject:** `mapper/app.py` (3 hunks) + net-new `tests/test_strips.py`
**Verdict:** **BLOCK** — **3 HIGH**

---

## BLUF

The coercion story is clean. The new `+N ramas sin mostrar` string interpolates only an
integer, the cap does not move a single title outside `darkside.plain`, and no new uncoerced
path to a rendered surface is opened. Questions 1, 2, 3 and 5 all come back clear, and
question 3 comes back clear by measurement rather than by argument.

**Three HIGHs, and they compound into one story: the frame stopped saying things, and nothing
in the suite can tell.**

1. `overflow: hidden` on `#map-minimap` silently deletes from the composited frame the very
   declaration this increment added — and the whole coverage legend with it — at ordinary
   file-chosen title lengths. The strip reports 3 rows while saying nothing.
2. **The acceptance suite is vacuous with respect to `MINIMAP_BRANCHES`.** All 6 arms pass with
   the cap set to `10**9`. Measured, not argued — a concurrent mutation harness installed that
   mutant on the tree mid-review and I ran the suite against it. The CSS clip is load-bearing
   for every arm; neither Python cap is covered by any oracle.
3. Bounding two strips does not make the collapse unreachable. `TabStrip`'s breadcrumb is a
   fourth unbounded strip on the same screen, and one 4000-character node title reproduces the
   pre-fix failure mode verbatim at 80x24: canvas 1 row **off-viewport**, count region
   **off-viewport**.

Together: the increment adds a declaration that the clip can eat (F1), ships two bounds no test
can see (F3), and leaves the collapse reachable through a strip it did not bound (F2).

**Read the tree-state incident below before acting on anything else in this document.**

---

## ⚠ Tree state during this review — a concurrent writer, and a mutant left in place

`mapper/app.py` was **rewritten repeatedly by another process while this review was running.**
This is not a finding about the code; it is a finding about the gate, and it is blocking on its
own.

Observed, timestamped:

| time | `mapper/app.py` sha256 (16) | state |
|---|---|---|
| review entry | `e839bd96fa3e1b25` | matches the declared pin |
| 14:20:55 | `87a2e65fe1cb3ed0` | changed |
| 14:21:57 | `c7b692871d51c03b` | changed |
| 14:22:03–14:22:12 | `e839bd96fa3e1b25` | back at the pin, 4 consecutive samples |
| 14:22:17–14:26 | `2c6a173ca1f64ea4` | **`MINIMAP_BRANCHES = 10**9` — a mutant, held ~4 min** |
| 14:26:57 | `3fc74fd700e10ebb` | back to `MINIMAP_BRANCHES = 24`, still ≠ pin |

The signature is a **mutation-testing harness** cycling constants (install mutant → run →
restore), consistent with the counterfactual machinery packet §4.1 describes. Consequences:

- **The declared restore-to pin for `mapper/app.py` does not hold at the close of this review,**
  and I did not break it. I wrote no tracked file. `tests/test_strips.py` is byte-identical to
  its pin (`e24f8d43…`) throughout. Every probe I ran was read-only, under
  `PYTHONDONTWRITEBYTECODE=1`, from a scratch directory outside the repo.
- **A mutant sat committable for at least four minutes.** `MINIMAP_BRANCHES = 10**9` disables
  the cap entirely: `children[:10**9]` is every child, `undrawn` is always ≤ 0, so the minimap
  is unbounded again and the new declaration **never renders at all**. A `git commit -a` in that
  window ships a neutered cap that looks like the reviewed code in every diff summary
  (`62 insertions(+), 2 deletions(-)` was identical under the mutant).
- **Both dispatched reviews were exposed.** My first probe pass ran inside the window where the
  file was being swapped, so I discarded it and re-measured under an explicit structural guard
  (`MINIMAP_BRANCHES == 24`, `METER_STEPS == 24`, both clip rules present, plus hash-unchanged-
  during-run). Every measurement in this document is from the guarded pass. The code review
  dispatched in parallel has no such guarantee unless it took the same precaution — **it should
  be asked, not assumed.**

**Required before anything else:** stop the harness, restore `mapper/app.py` from the pin
`e839bd96fa3e1b25fd4b5f7e4b4b82d933605dac81079bcf3ba3648605e332aa`, and confirm by sha256 that
the tree the gates signed off on is the tree that gets committed. I deliberately did **not**
restore it myself: I am not the writer this round, the harness was still live, and overwriting
another process's in-flight state would have destroyed the evidence in the table above.

---

## Scope reviewed

- `git diff HEAD -- mapper/ tests/` — `mapper/app.py` +62/-2 in three hunks (`MINIMAP_BRANCHES`
  + cap + declaration, `app.py:1734-1780`; `METER_STEPS` + meter cap, `app.py:2016-2060`; two
  CSS rules, `app.py:3246-3267`) and `tests/test_strips.py` +212 (new, 6 arms).
- Packet `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-007-strips.md`.
- Coercion sink: `mapper/darkside.py:370-428` (`PRESERVED_CODE_POINTS`, `COERCION_RANGES`,
  `plain`), `darkside.py:135-175` (`tab_strip`), `darkside.py:268-281` (`step_meter`).
- Surrounding surfaces: `MapScreen.compose` (`app.py:1225-1244`), the crumb and minimap sinks in
  `refresh_canvas` (`app.py:2272-2317`), `_event_toast` and its 11 call sites
  (`app.py:2072-2083`).
- **Method:** F1, F2 and F4 are **measured** through the real compositor
  (`tests/inc3_support.frame_rows`) at both declared sizes. F3 is measured by executing
  `tests/test_strips.py` against an installed mutant. Nothing below is reasoned-only except
  where explicitly labelled.

---

## Findings

### F1 — The new overflow declaration, and the coverage legend, are silently clipped off the frame by the new `overflow: hidden` [Severity: HIGH]

- **What:** `#map-minimap { max-height: 3; overflow: hidden; }` clips at **row** granularity.
  `_minimap_text` appends the `+N ramas sin mostrar` declaration and then the four-glyph legend
  **last**, after up to 24 branch entries whose titles are file-derived and **not cell-bounded**
  (`name = darkside.plain(...)`, then `f"{name} "` — coerced, never `darkside.fit`-ed). Once the
  entries exceed three rows, the declaration and the legend fall past the clip and vanish from
  the composited frame **with no trace**. The widget's own `Text` still contains them, so every
  region-level assertion passes.

- **Where:** `mapper/app.py:1750-1780` (`_minimap_text` — the unbounded `name`, the append-last
  ordering) × `mapper/app.py:3266` (the clip).

- **Measured** (guarded pass; `frame_rows`, cursor at root; `decl_in_widget` reads
  `_minimap_text().plain`):

  | title shape | branches | size | strip h | decl on frame | legend on frame | decl in widget |
  |---|---|---|---|---|---|---|
  | `rama N` (control) | 40 | 118x34 | 3 | **True** | **True** | True |
  | 60 ASCII cells | 40 | 118x34 | 3 | **False** | **False** | True |
  | 60 ASCII cells | 40 | 80x24 | 3 | **False** | **False** | True |
  | 60 ASCII cells | **24** (no remainder) | 118x34 | 3 | n/a | **False** | n/a |
  | 30 × U+6F22 (60 cells) | 40 | 118x34 | 3 | **False** | **False** | True |
  | 30 × U+6F22 (60 cells) | 40 | 80x24 | 3 | **False** | **False** | True |
  | base + 8 × U+0301 | 40 | 118x34 | 3 | **False** | **False** | True |

  In every failing row the declaration **is** in the widget and **is not** on the frame. Sixty
  cells is not a pathological title — it is a sentence.

- **Why it matters:** two harms, and the second is the security one.
  - The **24-branch row** is the sharper case: no remainder, so nothing is "missing" by the
    increment's own accounting — yet the legend is gone and the operator reads `█ ▒ ░ ╱` with no
    key. The strip's stated job is *telling the operator which branch is at risk*; unkeyed
    glyphs cannot do it.
  - Above 24 branches the operator sees a coverage strip that **looks complete and is not**, and
    the file chose that. `app.py:1754-1760` already names this harm model in as many words — an
    uncoerced title "deceives the operator on exactly the judgement the minimap exists to
    support" — citing `U+202E` as the mechanism. This is the same harm through a second
    mechanism the coercion helper cannot cover, because **length is not a code point**.
  - It contradicts the contract the increment asserts for itself. `app.py:1742-1744` and packet
    §2.1 both state the remainder "is DECLARED rather than silently dropped … the same contract
    `_degraded` and the overflow token already keep." At 60-cell titles it is silently dropped,
    and so is a legend that was never in scope to drop at all.

- **Not covered, and the near-miss is instructive:** `test_the_strips_cannot_outgrow_their_ceiling`
  asserts `region.height <= 3`. Strip height is **3 in every defective row above**, so the arm
  is green throughout. The module docstring of the file containing that arm states the
  correction — *"A region's visibility is not its content's visibility; measure what the operator
  reads, not the box it lives in"* — and applies it to `SEARCH_COUNT_SUBJECT` on
  `#map-pagination` while leaving the new minimap declaration measured by region height alone.
  **The lesson was learned one strip to the left.**

- **Regression note, labelled as reasoned rather than measured:** pre-fix, 40 × 60-cell titles
  grow the `height: auto` strip to roughly 21 rows at 118 columns, which fits a 34-row frame —
  so the legend *was* on the frame, at the canvas's expense. This increment traded a visible
  collapse for a silent omission. I did not execute that counterfactual (it needs the pre-fix
  tree installed, and the tree was already being written by someone else); it does not change
  the finding, since the post-fix behaviour is defective on its own terms.

- **Recommendation** (`software-dev`; both changes inside `_minimap_text`):
  1. **Bound each entry by cells, not just by count.** The module already owns the helper:
     ```python
     name = darkside.fit(self.graph.nodes[cid].ficha.title or cid, MINIMAP_NAME_CELLS)
     ```
     `darkside.fit` calls `plain` internally and truncates with an ellipsis, so coercion is
     preserved and the truncation becomes **visible** — which the current silent row-drop is not.
     Derive `MINIMAP_NAME_CELLS` from the same geometry `MINIMAP_BRANCHES` came from and write
     the arithmetic beside it: 24 × (name + 4 chrome cells) + legend ≤ 3 × 118.
  2. **Put the declaration and the legend ahead of the entries**, or make the entry budget the
     row remainder after reserving them — the pattern `_HINT_BRANCH_CELLS` already establishes at
     `app.py:110-125` ("the affordances outrank it"). Either way, the declaration must not be
     the first thing the clip eats.
  3. **Add the arm the ceiling arm is not** — see F3, which is the same gap seen from the test
     side.

---

### F2 — Bounding two strips does not make the collapse unreachable: `TabStrip`'s crumb reproduces it exactly, from one node title [Severity: HIGH]

- **What:** `MapScreen` composes **five** content strips outside `#map-body`. This increment
  bounds two. `TabStrip`, `#map-toast`, `HintLine` and `KeyBar` carry **no height rule** — not in
  `MapperApp.CSS`, and not as widget `DEFAULT_CSS` (`mapper/widgets/chrome.py` declares none) —
  so all four are `height: auto` and take their rows from `#map-body { height: 1fr; }`.
  `HintLine` is bounded in Python (`_HINT_BRANCHES`, `_HINT_BRANCH_CELLS`) and `KeyBar` truncates
  visibly, so those two are fine. **`TabStrip` is bounded nowhere.** `darkside.tab_strip`'s crumb
  branch (`darkside.py:165-173`) renders every part in full — its `width` parameter is consumed
  *only* by the wordmark spacer on the tab line above and never reaches the crumb — and
  `refresh_canvas` feeds it `plain(map_id)`, the link chain, and **`plain(node_title)` for the
  cursor node** (`app.py:2282-2284`). Coerced, unbounded.

- **Where:** `mapper/app.py:1227` and `app.py:2272-2284` × `mapper/darkside.py:165-173`; absence
  of a rule at `mapper/app.py:3244-3267`.

- **Measured** (guarded pass; cursor is root at open, so one hostile root title suffices):

  | root title | size | TabStrip h | `#map-canvas` | `#map-pagination` |
  |---|---|---|---|---|
  | 4 chars (control) | 118x34 | 2 | h=27 @ y3 | y30 on-frame |
  | 500 chars | 80x24 | 9 | **h=9** @ y10 | y19 on-frame |
  | 4000 chars | 118x34 | 37 | **h=1** @ y30 | y31 on-frame |
  | **4000 chars** | **80x24** | **54** | **h=1 @ y55 — OFF-VIEWPORT** | **y56 — OFF-VIEWPORT** |

  The last row is the packet's own pre-gate table (§1: `80x24 | y=714 h=1 0 rows | y=715 0 rows |
  count readable: False`) reproduced with **one node title instead of a 12002-node graph**.
  Degradation is smooth and starts early: 500 characters already costs a third of the canvas at
  80x24.

- **Why it matters:** this is the direct answer to question 4 — **the new bound is not
  sufficient.** The stylesheet comment at `app.py:3253-3254` states the right principle ("a strip
  whose height is its content is one long title away from doing it again … makes the collapse
  unreachable by construction") and then applies it to two of the four unbounded strips. The one
  it skipped is the one that takes a raw ficha title. Consequences:
  - **`LLR-N07.3.4` predicate 1 is not closed.** The count region is off-viewport for a
    reachable input. Packet §7's "`LLR-N07.3.4`'s **block is resolved** — to be marked in
    `state.json.open_blocks` at close" would record a requirement as satisfied while a one-field
    map file violates it. **That marking is what this finding blocks.**
  - **The threat model is unchanged from the one that motivated the batch:** an attacker-supplied
    map renders the operator's UI unusable. The payload got *smaller* — 4 KB in one `title:`
    field rather than a 4001-way fanout.
  - `darkside.plain` preserves `U+0009` and `U+000A` by design (`darkside.py:370`), so any future
    sink that lets a title's newlines through gets a row multiplier for free. A **cell-width**
    bound closes both the length and the newline vector; a character-count bound closes neither.

- **Recommendation:** own this as its **own increment** — it is out of scope for a 1-source-file
  layout increment and must not be half-fixed from inside it.
  1. Bound the crumb where it is built, in `darkside.tab_strip`: give the crumb line the visible
     truncation `keybar` already performs, budgeting `width` across the parts and reserving cells
     for the last (the cursor title, which is `INK` and load-bearing).
  2. Bound the strip in the stylesheet too — `TabStrip { max-height: 2; overflow: hidden; }` —
     for the same "necessary and not sufficient" reason `app.py:3251-3254` gives for the other
     two. **But land the Python bound first or in the same pass:** adding `overflow: hidden` to a
     strip whose content is not cell-bounded is precisely how F1 came to exist.
  3. Re-scope the §7 carry: predicate 1 is closed **against the fanout vector**. Say it in those
     words rather than "resolved", and open the crumb vector as the successor block.

---

### F3 — The acceptance suite is vacuous with respect to `MINIMAP_BRANCHES`: all 6 arms pass with the cap disabled [Severity: HIGH]

- **What:** with `MINIMAP_BRANCHES = 10**9` installed — the cap fully neutered, the minimap
  unbounded in Python again, and the new declaration **never rendered under any input** —
  `tests/test_strips.py` reports **`6 passed in 43.99s`**.

- **Where:** `tests/test_strips.py` (all 6 arms) against `mapper/app.py:1745`.

- **Measured, and the provenance is exact:** the mutation harness described in the incident
  section installed this mutant on the tree; I ran the suite against it read-only. `app.py`
  sha256 was `2c6a173ca1f64ea4` immediately before **and** immediately after the run (unchanged
  throughout), and `sed -n '1745p'` confirmed `MINIMAP_BRANCHES = 10**9` in the file under test.
  Command: `python -m pytest tests/test_strips.py -p no:cacheprovider -q -m ""`.

- **Why every arm survives it:** the **CSS clip alone** satisfies all six predicates.
  - `test_the_strips_cannot_outgrow_their_ceiling` asserts `region.height <= 3` — `max-height: 3`
    guarantees that no matter what `_minimap_text` returns.
  - The two `AT` arms assert `SEARCH_COUNT_SUBJECT` and `SEARCH_SUSPENDED_NOTICE` are in the
    frame — which the clip guarantees by holding both strips at 3 rows, whatever the caps do.
  - The two `max-height`-regression arms drive 3-branch maps, far below any cap.
  So the suite pins **the stylesheet** and pins **neither Python bound**. By the same structure
  `METER_STEPS` is uncovered too: no arm reads the meter's content, only its region's height.

- **Why the packet's counterfactual could not catch this — and this is the transferable lesson:**
  §4 installs the **whole pre-fix file**, which reverts the CSS and the Python caps *together*.
  A counterfactual at whole-file granularity can only tell you the change as a whole matters; it
  can never tell you **which half** the arms actually detect. It is exactly the "moved bound"
  error the module docstring warns about, one level up: the packet's §4 is a strong control
  aimed at the wrong granularity. Per-constant mutation is what distinguishes them, and it takes
  seconds — as this finding demonstrates.

- **Why it is HIGH rather than a test-hygiene note:** the increment's security-relevant claim is
  that a hostile map can no longer hide the count and that the hidden remainder is *declared*.
  Both halves of that claim rest on the two caps, and **neither cap has an oracle**. Combined
  with F1 — where the declaration is silently clipped even when the cap works — the entire
  "declare the remainder" mechanism is both broken and unverified. A future edit to
  `MINIMAP_BRANCHES` (or a mutation harness that forgets to restore, per the incident above)
  ships green.

- **Recommendation:**
  1. **Add a content-level arm that reads the frame, not the region.** It closes F1 and F3 at
     once. Predicate: at 40 branches with 60-cell titles, at both declared sizes,
     `"ramas sin mostrar"` and the legend's `"sin datos"` appear in `frame_rows(screen)`. It is
     red on today's tree — I have measured that it is — and it dies under the `10**9` mutant.
  2. **Add a cap-sensitive arm.** At 40 short-titled branches assert the frame shows exactly
     `MINIMAP_BRANCHES` entries and declares `+16`, deriving both from the constant so the arm
     is a derivation and not a second copy. This is what makes `10**9` red.
  3. **Re-run the counterfactual per constant, not per file.** Mutate `MINIMAP_BRANCHES` and
     `METER_STEPS` independently and record which arms redden for each. The packet's §4 ledger
     should carry that table, not just the whole-file verdict.

---

### F4 — `#map-toast` is unbounded and paints file-derived text; it is also the strip carrying the live path-leak carry [Severity: MEDIUM]

- **What:** `#map-toast` has no height rule either, and `_event_toast(label, detail)` paints
  `detail` in full. Several call sites pass a file-derived node title: `app.py:2349`
  (`"guardado"`), `2394`, `2415`, `3071` (`"archivado"`). All `darkside.plain`-coerced, none
  length-bounded.
- **Where:** `mapper/app.py:2072-2083`; sinks at `2349`, `2394`, `2415`, `3071`, `3000`.
- **Measured** at 118x34: 500-char detail → toast **6 rows**, canvas 22; 4000-char detail →
  toast **36 rows**, canvas **1 row**.
- **Why it matters:** same class as F2 with a smaller blast radius — it needs an operator action
  (save / archive / open attachment) and clears on the next toast, so it is degradation rather
  than a persistent collapse. **MEDIUM for that reason.** It compounds the live carry, though:
  `app.py:3000` is `self._event_toast("exportado", str(path))` — an absolute workspace path,
  **uncoerced** (`str(path)`, not `darkside.plain(path)`), which on a Windows install contains
  the operator's user directory. An unbounded strip renders that leak across many rows instead
  of one.
- **This increment neither touches nor worsens the carry** — see question 5 below. Recorded here
  only because the same missing bound governs both.
- **Recommendation:** carry with F2 into the strip-bounding increment. Bound `detail` with
  `darkside.fit(detail, <remainder>)` at the `_event_toast` seam — one place, all 11 sites — then
  add `#map-toast { max-height: 2; overflow: hidden; }` **after** the Python bound, never before.
  Route `app.py:3000` through `darkside.plain` while there; the path leak itself stays under its
  existing carry.

---

### F5 — A load-bearing comment now states the opposite of the shipped stylesheet [Severity: LOW]

- **What:** `app.py:94-97` reads: *"the count region **WRAPS rather than clips**
  (`#map-pagination` has **no height rule**, so it is `height: auto`). An unbounded echo therefore
  does not overflow the strip — it GROWS the strip and takes the rows from `#map-body`."* After
  this increment `#map-pagination` has `max-height: 3; overflow: hidden` (`app.py:3267`) and does
  the opposite: it clips, and an over-long echo is now *dropped* rather than *grown*.
- **Where:** `mapper/app.py:94-97`, the rationale block for `_QUERY_ECHO_CELLS`.
- **Why it matters:** it is the stated justification for a security-relevant cap. A reader who
  trusts it concludes the cap's only job is protecting `#map-body`, and may relax or remove it —
  at which point the echo is silently clipped instead, which is F1's failure mode on a second
  strip. The increment holds itself to exactly this standard elsewhere: `app.py:2027-2030`
  corrects a wrong comment **in place** and says why.
- **Recommendation:** amend in place alongside F1, keeping the superseded text per the batch's
  convention. New reasoning: `_QUERY_ECHO_CELLS` now protects the strip's *content* from the
  clip, not `#map-body` from the strip.

---

## Cleared — the four questions that came back with no finding

**Q1 · Is `+N ramas sin mostrar` safe, and did the cap disturb the coercion around it?**
**Clear, verified by reading the sink.** The literal is ASCII Spanish declared inline at
`app.py:1773`; its single interpolation is `undrawn = len(children) - self.MINIMAP_BRANCHES`, an
`int` derived from two `int`s — no file-derived substring reaches it. It enters
`darkside.Text.assemble` as a `(str, style)` pair with a constant style, and `Text` does not parse
markup (`darkside.plain`'s docstring, `darkside.py:421-424`), so it is not a markup sink.
**The cap did not move a title outside coercion and cannot drop a coercion call:** `children_of`
returns a `list` (`model.py:149-150`); the slice `children[: self.MINIMAP_BRANCHES]` is taken on
the **id** list *before* the loop, and `darkside.plain` is applied *inside* the loop at
`app.py:1761` — so it is applied to exactly the titles that are drawn, and to all of them. Titles
past index 24 are not truncated, not partially rendered, and not passed to any sink; they are
never read. The invariant "every title on this surface passed through `plain`" is strictly
preserved. *(Coercion clearance only — the same unbounded `name` is F1's mechanism.)*

**Q2 · Does truncation open a NEW uncoerced path — `_branch_coverage_glyph`, the legend?**
**No.** `_branch_coverage_glyph` (`app.py:1700-1732`) returns a glyph from the closed literal set
`{█, ▒, ░, ╱}` and a style from a module constant; no file-derived string leaves it. It reads
`ficha.fields.get("D", "")` for a percentage only — counted, never rendered. The legend
(`app.py:1774-1779`) is eight literal/constant pairs. The cap **reduces** this function's call
count from one-per-branch to at most 24 — a strict reduction in surface — and narrows one
availability path as a side effect: a dangling edge in branch 25+ can no longer raise `KeyError`
into the guarded block at `app.py:2306-2309`, so the minimap degrades to empty less often. *(The
`OutlineRail.render` sink named at `app.py:2298-2305` remains carried and is untouched here.)*

**Q3 · Can `overflow: hidden` split a wide or combining character at the clip boundary?**
**No — measured, not argued.** The clip is **vertical and row-granular**: whole rows are dropped,
so no grapheme is bisected. Checked at 30 × `U+6F22` (2-cell ideographs, 60 cells per title) and
at base-plus-eight-`U+0301` titles, at both declared sizes: every composited row ends on a
complete grapheme, no row terminates on a combining mark, and no `U+FFFD` or cell-accounting
corruption appears at the boundary. Frame cell width stays exactly 118 / 80 throughout — the
varying *character* counts per row (88–118 at 118 cells wide) are the expected consequence of
2-cell and 0-cell characters, not damage. Horizontal clipping is unchanged by this increment.
**The meaning-change risk is real but lives at the row granularity, and it is F1** — a title
wrapped across the row-3 boundary loses its tail with no ellipsis, and the legend loses
everything.

**Q5 · Any secret, path, or user-identifying data newly reaching a rendered surface?**
**None. The carry is neither touched nor worsened, confirmed against the diff.** The three
`mapper/app.py` hunks are `_minimap_text` (1734-1780), `_pagination_text` (2016-2060) and the CSS
block (3246-3267). `_event_toast` and all 11 of its call sites are byte-identical, including
`app.py:3000`'s `str(path)` — the export toast that renders an absolute workspace path containing
the operator's user directory. The new string carries an integer count of undrawn branches: graph
shape, not identity. Nothing else newly reaches a surface. **The carry stands exactly where it
stood, and F4 records only that the strip it paints on shares F2's missing bound.** *(No secret
value appears anywhere in this artifact; the leak is referenced by `file:line` and by description
only.)*

---

## Verdict

- [ ] OK to ship
- [ ] OK to ship with the listed mitigations applied first
- [x] **Block — must fix HIGH findings before ship**

**HIGH findings: 3 (F1, F2, F3).** They block different things, and the split is deliberate:

- **F1 and F3 block the code.** Both were introduced by this increment. F1 silently removes an
  operator safety declaration from the frame at attacker-chosen input; F3 shows that no arm in
  the tree — including this increment's own — can see either Python bound. One new frame-level
  arm closes both, and it must be red on today's tree before it counts.
- **F2 blocks a claim, not the code.** The crumb collapse is pre-existing and correctly out of
  scope for a 1-source-file layout increment. What cannot ship is packet §7's "`LLR-N07.3.4`'s
  block is **resolved**" and the matching `state.json.open_blocks` marking: predicate 1 holds
  against the **fanout** vector and fails against the **title-length** vector, measured
  off-viewport at 80x24. Re-scope the carry in those words and open the successor block.
- **The tree-state incident blocks the commit itself**, independently of all five findings.
  Restore `mapper/app.py` from the pin and confirm by sha256 before anything is committed, and
  ask the parallel code reviewer whether its reading was guarded.
- F4 rides into the successor increment with F2; F5 is amended in place with F1.

Everything else here is sound, and two things are better than sound. The minimap and meter caps
are correct as far as they go, and bounding those two strips closed a real newline-driven row
multiplier (`darkside.plain` preserves `U+000A`) that had no bound before. The gap is that
"unreachable by construction" was asserted over two strips out of four, that the clip added to
reach it eats the declaration it was paired with, and that the suite cannot tell.

---

## Evidence checklist

- [x] **Each finding has what · where · why · recommendation** — F1 `app.py:1750-1780 × :3266`;
      F2 `app.py:1227, 2272-2284 × darkside.py:165-173`; F3 `tests/test_strips.py × app.py:1745`;
      F4 `app.py:2072-2083, :3000`; F5 `app.py:94-97`.
- [x] **Each finding has a severity rating** — F1 HIGH, F2 HIGH, F3 HIGH, F4 MEDIUM, F5 LOW. The
      HIGH/MEDIUM line for F4 is argued explicitly (needs an operator action, self-clearing), and
      F3's promotion above test-hygiene is argued explicitly (both security claims rest on
      unoracled constants).
- [x] **No secret values in this output** — the export path leak is referenced as `app.py:3000`
      and by description; no path, username or value is reproduced.
- [x] **Verdict explicit** — BLOCK, 3 HIGH, with the code / claim / commit split stated.
- [x] **New tool or integration scope and blast radius** — **N/A, asserted rather than assumed:**
      the diff adds no dependency, import, network call, subprocess, filesystem write or external
      connector. `git diff HEAD -- mapper/ tests/` is three in-place hunks plus one test module;
      the only new module-level names are two `int` class constants.
- [x] **Findings measured, not reasoned** — F1/F2/F4 executed against the real compositor via
      `tests/inc3_support.frame_rows` at 118x34 and 80x24; F3 executed as a pytest run against a
      recorded mutant with the file hash pinned before and after. The single reasoned claim
      (F1's pre-fix counterfactual) is labelled as reasoned in place.
- [x] **Measurements guarded against the concurrent writer** — the reported pass asserts
      `MINIMAP_BRANCHES == 24`, `METER_STEPS == 24` and both clip rules present in the imported
      tree, and asserts `app.py`'s sha256 unchanged across the run (`3fc74fd700e10ebb` before and
      after). An earlier unguarded pass was discarded rather than reported.
- [x] **`C-56` honoured** — hostile and non-ASCII code points named as `U+202E`, `U+6F22`,
      `U+0301`, `U+000A`, `U+0009`, `U+FFFD`; none written verbatim.
- [x] **Sole-writer discipline — I wrote no tracked file.** `tests/test_strips.py` is byte-identical
      to its pin (`e24f8d4322feefe245fa26636c2b31fa2da2cc40f07f083da60559773ede331b`) at entry and
      exit. **`mapper/app.py` does NOT match its pin at exit, and the cause is a concurrent
      mutation harness, not this review** — full timestamped evidence in the tree-state incident
      section above. All probes ran read-only under `PYTHONDONTWRITEBYTECODE=1` from a scratch
      directory outside the repo and wrote no `__pycache__`; the one pytest invocation used
      `-p no:cacheprovider`. Pre-existing bytecode was deliberately left in place — purging
      another process's live state would itself be a mutation by the writer who is not supposed
      to make any.
