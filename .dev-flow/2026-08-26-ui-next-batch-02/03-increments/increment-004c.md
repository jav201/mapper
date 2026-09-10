# Increment 4c — `LLR-N07.3.4`: one regime, not two (`#D43`)

**Batch:** `2026-08-26-ui-next-batch-02` (SEALED) · **Increment:** `Inc-4c` · **Branch:** `feat/ui-next-batch-02`
**Entry commit:** `9ba2f26`, tree clean except the `.dev-flow/` spec edits · **NOT COMMITTED** — the working tree is what is gated.
**SOURCE FILE COUNT: 1** — `mapper/app.py`. Tests uncapped, as declared.
**Language:** English (engineering artifact).

---

## BLUF

The count region declares an active search at **every** graph size, `esc` clears in **all** regimes,
and the copy `Inc-4b` shipped without an owner is reconciled under its new owner. **1 source file.**

**Baseline reproduced before a line was written: `847 passed, 17 deselected, 3 xfailed`, exit 0.**
**Result: `850 passed, 17 deselected, 3 xfailed`, exit 0, zero FAILED** (default lane) and
**`867 passed, 3 xfailed`** (all markers) — both matching the declared ledger exactly. Ruff SET over
`mapper/ tests/` is **IDENTICAL** to the entry pin: 27 = 27, **zero NEW, zero GONE**.
**12 mutations fired, 12 KILLED, 12 sha256-verified restores** — after a first round that killed
only 10, whose two survivors are reported in §5 as findings and are closed.

**Three things this increment did not do that the spec asked for, or that it asked for and I
disagree with — all three are §5 findings, none is silent:**

1. **`n recorre` is NOT painted above the bound (F-1).** The Statement's third clause is not
   satisfiable without breaking a shipped, gated AST arm; the numeric threshold does not require it.
2. **Predicate 1 is NOT observable at the SHIPPED bound (F-2).** Measured: at 12002 nodes the entire
   `MapScreen` collapses — this is not a defect of the count line and it is not closable in one file.
3. **`Inc-4a`'s cost justification for the bound is stale (F-3)** by two orders of magnitude,
   re-measured and corrected in place.

---

## 1 · What changed — `mapper/app.py`, one file

### 1.1 · The count region declares an active search at every graph size

`_count_line`'s above-the-bound arm returned an empty `Text`. It now returns
`_suspended_count_line()`, which paints four facts on one row:

```
búsqueda: «riesgo» · 5 coincidencias en el mapa · esc limpiar · resaltado y recorrido suspendidos
```

- **the query**, through `darkside.fit` — a coercion sink (`HLR-COERCE`) and a cell budget in one call;
- **the whole-graph count**, from `_whole_graph_tally`;
- **the chord that works here**, glyph read from the seat via `_seat_glyph('back_or_home')`;
- **the suspension notice** — the load-bearing half.

### 1.2 · The count is taken from the cheap half of the same owner

`SearchIndex.query`'s own docstring states `len(query(q)) == len(hits(q))` **for every graph** and
says in as many words that the count line may be taken from either. Only the ORDERING was ever
expensive, so `_whole_graph_tally` reads `hits`. The acceptance compares it against the **ordered**
form, so the cheap path is checked against the expensive one and not against itself.

### 1.3 · One `SearchIndex` construction site, shared — `_search_index`

`test_the_count_and_the_paint_share_one_resolution` censuses this module for `SearchIndex(...)` call
sites and pins the total at **one**. `_whole_graph_tally` was a second, and **the arm reddened on it
before I ran a mutation**. The fix shares the constructor rather than exempting the reader: "these
two cannot disagree because of WHEN they run" is a reasoned argument, and this batch has three
recorded cases of a reasoned agreement argument surviving a mutation that broke the property.

### 1.4 · `esc` means one thing at every graph size

`_search_is_live` read `query_text.strip() and _search_order() is not None`. It now reads
`bool(self.query_text.strip())` — **the state, not the rendering detail.**

### 1.5 · The hint line grew the same third arm

`_search_hint` returns `«notice» · esc limpiar` above the bound. `sin coincidencias` there is the
lying affordance `_count_line` refuses to paint, one surface over. `on_input_submitted` no longer
excludes `None` alongside the blank query; its comment is corrected.

### 1.6 · The copy reconciliation (task item 3)

| String | Was | Now | Why |
|---|---|---|---|
| walk toast label, above bound | `Inc-4b`'s "search not evaluated" wording | `recorrido suspendido` | The region now evaluates the search and paints the whole-graph figure **in the same frame**. The old label contradicts the row above it. What is suspended is the thing the key asked for. |
| walk toast detail | `el mapa supera el límite de <N> nodos` | unchanged | Still true, still the only place the numeric bound is named on a keypress. |
| the `abrió «…»` hint prefix | unowned | unchanged, now owned | `LLR-N07.3.4` is its owner; no edit was needed for it to be consistent. |

**Is the above-the-bound toast now redundant? No — and I recommend keeping it.** The region declares
a **state** (a search is live, N matches, highlighting and walk suspended). The toast answers a
**keypress**: it tells the operator why the key they just pressed did nothing. Deleting it makes `n`
a silently swallowed keypress, which is the exact defect `_search_is_live`'s own docstring names.
What I did remove is the **overlap**: the toast no longer repeats the count, and its label no longer
contradicts the region.

### 1.7 · Docstrings corrected rather than left standing

`_search_order`'s "the question is not answered at all" and its cost paragraph were both made false
by this change. Both are rewritten (see F-3). A justification naming a mechanism that has since been
repaired is how a later reader deletes the right guard.

---

## 2 · Files modified

| File | Kind | Delta |
|---|---|---|
| `mapper/app.py` | **SOURCE (1 of 1)** | **+278/−61** — 3 constants, 4 new methods (`_search_index`, `_whole_graph_tally`, `_query_echo`, `_suspended_count_line`), 5 changed lines in existing methods; the rest is docstring, including the corrections F-2 and F-3 required |
| `tests/test_search.py` | test (uncapped) | **+313/−69** — 1 arm removed, 1 renamed + rewritten, 4 added, 2 exemption rows removed, viewport ban extended by three methods |

`.dev-flow/01-requirements.md` and `.dev-flow/state.json` carry **your** spec edits and were **not
touched**.

### 2.1 · The exact-set paint-pass arm, in the REVERSE direction

`_search_is_live` and `action_back_or_home` were **removed** from `_PASS_FREE_READERS`. They no
longer reach the resolution, and the arm's `stale` assertion fails on an exemption for a reader that
no longer exists. The opener assertion is left untouched at `{refresh_canvas, _declare_after_layout}`.
No exemption was added: `_whole_graph_tally` and `_search_index` read neither `_search_order` nor
`_search_memo`, so they do not enter the derived set.

---

## 3 · How to test

```
PYTHONUTF8=1 python -m pytest -q                 # default lane
PYTHONUTF8=1 python -m pytest -q -m ""           # all markers
PYTHONUTF8=1 python -m ruff check mapper/ tests/
```

The acceptance nodes:

| Node | Owns |
|---|---|
| `test_above_the_bound_the_count_line_declares_the_search` | `AT-054` — predicate 1, three clauses asserted separately |
| `test_at_055_esc_means_one_thing_at_every_graph_size` | `AT-055` — predicate 2, **one node, both regimes** |
| `test_below_the_bound_no_suspension_notice_is_painted` | predicate 3, swept over all three below-bound shapes |
| `test_the_suspended_declaration_is_actually_in_the_frame` | predicate 1 read from the **composited frame**, swept 60→160 |
| `test_the_hint_line_promises_esc_at_every_graph_size` | `#D38`'s rule, which the reversal must keep |

---

## 4 · Test results — from one complete run's own output

**Default lane, clean tree, nothing else touching it:**

```
850 passed, 17 deselected, 3 xfailed in 198.02s (0:03:18)
```

**All markers:**

```
867 passed, 3 xfailed in 222.70s (0:03:42)
```

**Ledger: 850 default / 867 all markers — both as declared.** Arithmetic: 847 − 1 removed + 4 added
= 850.

**Ruff SET over `mapper/ tests/`, identical scope:** `Found 27 errors.` — **zero NEW, zero GONE**
against the entry pin, compared as sorted sets with line/column stripped.

> **Evidence-integrity note, declared rather than buried.** Two earlier suite runs were started in
> the background and were still running when I stashed files for the ruff comparison and when the
> mutation battery mutated `app.py`. **Both runs were discarded as contaminated** and both lanes were
> re-run on a verified-clean tree with nothing else executing. The numbers above are from the clean
> runs only. `mapper/app.py` sha256 `654dba5e…`, `tests/test_search.py` sha256 `d161c3a7…`.

### 4.1 · Mutation battery — 12 arms, 12 RED, 12 sha256-verified restores

Every arm restored the file byte-for-byte; the harness asserts `sha256(after) == sha256(before)` and
asserts the fired-arm count equals the declared one. Mutated tokens are described **by position and
operation**, never spelled.

| Arm | Operation | Verdict |
|---|---|---|
| **`M-N07.3.4-a`** | the shared predicate's return expression re-conjoined with the resolution test | **KILLED** |
| **`M-N07.3.4-b`** | the notice interpolation deleted from the suspended line's tail | **KILLED** |
| `A-tally-zero` | the tally's return replaced by a literal zero | **KILLED** |
| `A-tally-viewport` | the tally's hit set narrowed by the fold state (risk A-6) | **KILLED** |
| `A-notice-leaks-below` | the notice appended to the below-bound empty-count arm | **KILLED** |
| `A-toast-unreconciled` | the walk's above-bound toast label reverted to the `Inc-4b` wording | **KILLED** |
| `A-echo-unbounded` | the echo's `fit` call replaced by an uncapped coercion | **KILLED** |
| `A-esc-never-pops` | the handler's terminal pop statement replaced by a bare return | **KILLED** |
| `A-hint-silent-above` | the hint's above-bound arm replaced by the resting hint | **KILLED** |
| **`S-second-owner`** *(strong-arm probe)* | the tally re-inlined as its own owner construction | **KILLED** |
| **`S-unexplained-reader`** *(strong-arm probe)* | a new method reading the resolution, with no exemption row | **KILLED** |
| **`S-label-dropped`** *(strong-arm probe)* | the region's label constant dropped from the line's head | **KILLED** |

Three arms are aimed at machinery I believed was already strong; the calibration instruction asked
for two. **Two of them initially SURVIVED** — see F-4 and F-5.

---

## 5 · Findings — including what the spec written today gets wrong

### F-1 · `n recorre` is not painted above the bound — a Statement clause I did not implement

`LLR-N07.3.4`'s **Statement** requires the region to name "that the walk chord traverses it" **at
every graph size**, and the declared string spells `n recorre`. **I did not paint it, and the region
declares the walk SUSPENDED instead.**

Above the bound `_walk_hits` returns on `hits is None` and toasts. A region promising `n recorre`
beside a handler that refuses is the `AT-052`/`AT-053` lying-affordance class this batch exists to
close, reproduced by the fix for it — the same defect shape `#D43` just rejected for `esc`.

Making it true instead was considered and is **structurally blocked**:

- `_walk_hits` reading a second resolution above the bound reddens
  `test_cd6a_the_walk_reads_exactly_one_resolution`, which pins `used == {"_search_order"}` by AST;
- making `_search_order` return an order above the bound unpicks `Inc-4a`'s gated `None`
  distinction — which `M-N07.3.4-a`'s own wording presumes stays.

**The numeric threshold's predicate 1 asks for the query, the count and the notice. All three ship.**
The Statement's third clause does not. **Gate decision needed:** accept the deviation, or route a
follow-up that makes the walk work above the bound (measured at 12 ms/keypress — affordable, but it
moves an invisible cursor, and the strip would have to become its only feedback).

### F-2 · Predicate 1 is NOT observable at the shipped bound — and the cause is not the count line

The trap warning was correct and the measurement is decisive. On a **genuine** 12002-node graph:

| Measurement | 118×34 | 80×24 |
|---|---|---|
| `#map-pagination` region | y=42, height 104 | y=998, height 155 |
| `rows_in(...)` returns | **0 rows** | **0 rows** |

**I wrote the meter cap, measured it, and reverted it.** A 24-step cap takes the region from 104 rows
to 2 — and it is **still** laid out at y=55 of a 34-row frame, because the real cause is elsewhere:

```
map-minimap      y= -614  h= 668     <- 76,365 characters over the root's 4001 children
map-body         y=   54  h=   1
map-canvas       y=   54  h=   1     <- the MAP itself is one row
map-pagination   y=   55  h=   2
```

**At that graph size the entire `MapScreen` has collapsed.** The canvas is one row, the hint line is
off-frame, and the count region is one of three unbounded strips. Bounding the minimap is a UX
decision about a shipped surface with `LLR-N06.2.3` claims — it belongs to the gate that just ruled
on `#D43`, not to an increment scoped to `esc` and a count line. **The revert is recorded in
`_pagination_text`'s comment so the next reader does not re-derive it.**

**What this means for the requirement, stated plainly:** predicate 1 is satisfied and verified
in-frame across a 60→160 column band whenever the bound is reached at a graph size the screen can
lay out — which is how every above-the-bound arm in this suite reaches that branch, by the
bound-moving mechanism `test_the_walk_above_the_render_bound…` established and documented. It is
**not** satisfied on a 12002-node graph, and neither is anything else on that screen. **Recommend a
`Inc-STRIPS` increment: bound the minimap, the meter and the overflow declaration together.**

### F-3 · `Inc-4a`'s cost justification for the bound is stale by two orders of magnitude

`_search_order`'s docstring argued the bound from "the search's was seconds, several times over".
Re-measured at 12002 nodes for this increment:

```
hits          0.0075s  len=6001
tree_order    0.0097s  len=12002
query         0.0122s  len=6001
len(query)==len(hits): True
```

That figure predates `tree_order`'s child-index repair (`O(N*E)` → `O(E)`), documented in
`search.py`. **The bound is worth ~12 ms per resolution, not seconds.** What still justifies it is
the RENDERER's argument — nothing is drawn, so no hit set is meaningful to it — not the search's.
Corrected in place. This is also what makes §1.2 affordable.

### F-4 · A battery gap the first round found: the viewport ban did not cover the new chain

`A-tally-viewport` — the tally narrowed by the fold set, **risk A-6 itself** — **SURVIVED round 1**.
`test_the_count_and_the_paint_share_one_resolution` bans viewport reads across
`_search_order`/`_search_hits`/`_count_line`; `LLR-N07.3.4` added a chain beside it
(`_count_line → _suspended_count_line → _whole_graph_tally → _search_index`) that the ban did not
name. The predicate-1 fixture has an empty fold set, so the mutant changed no number anywhere.

**This is the same gap that arm's own docstring records `_search_hits` having been one increment
earlier.** The ban now covers all six methods, plus two "goes through the owner" assertions. Arm
re-fired: **KILLED**.

### F-5 · A second gap: the region's label was unpinned

`S-label-dropped` **SURVIVED round 1**. With the label gone the region reads `«riesgo» · 5
coincidencias…` on a strip that also carries a page numeral and an off-canvas numeral — the quoted
string identified only by position. That is the ambiguity `SEARCH_COUNT_SUBJECT` exists to remove one
field over. Now asserted in two arms, **derived from the shipped constant**. Re-fired: **KILLED**.

### F-6 · The width budget is a FIXED cap, and it costs one row at 60 columns

`_HINT_BRANCH_CELLS` records that a fixed cap was wrong there. **The cases differ in what overflow
costs**: on `HintLine` a wrap pushed affordances out of the painted frame; here `#map-body` is
`height: 1fr` and absorbs the row, and a two-row region is as readable as a one-row one. Swept 60→160
in steps of 5: a 2000-character query costs the **same** rows as an ordinary one **from 65 up, and
one extra row at 60**. Stated rather than rounded off. A width-relative budget was written first and
**removed** — it read `self.size.width`, which raises `NoActiveAppError` on an unmounted screen (the
way three unit arms reach this code), making a pure string helper depend on a running app for one row
at the narrow end of the band.

---

## 6 · Risks

| # | Risk | Standing |
|---|---|---|
| R1 | **F-1** — the region declares the walk suspended where the Statement says it traverses | **Needs a gate ruling.** Implemented the threshold, not the Statement, and said so. |
| R2 | **F-2** — the requirement is unobservable at the shipped bound | **Open, out of scope.** Not introduced here; three unbounded strips, one of them pre-existing since before this batch. |
| R3 | The above-bound region now resolves `hits` on every strip build | Bounded at 7.5 ms at 12002 nodes, measured; only reached when a query is live AND the graph is over the bound. |
| R4 | `SEARCH_SUSPENDED_NOTICE` names two suspended things where `#D43`'s example names one | Deliberate — a notice naming only the highlighting leaves the operator to discover the walk half by pressing `n`. Reversible in one constant if the gate disagrees. |
| R5 | Copy is Spanish and unreviewed by a native-speaking operator | Same standing as every prior increment's copy. |

---

## 7 · Pending items / suggested next task

1. **Gate ruling on F-1** — accept the deviation, or open a follow-up for a walk that works above the bound.
2. **`Inc-STRIPS` (proposed, new)** — bound the minimap, the pagination meter and the overflow
   declaration so `MapScreen` survives its own render bound. **F-2 is its acceptance.** This is the
   increment that would finally make `LLR-N07.3.4` predicate 1 true at 12002 nodes.
3. **Independent code review + security review**, per `#D44` — this modifies a shipped, gated
   behaviour on the chord that leaves the screen.
4. **Then `Inc-5`** — `LLR-N07.2.2b` with its threshold corrected by `#D42`.

---

## 8 · Evidence checklist

- [x] **Tests/type checks/lint pass** — `850 passed, 17 deselected, 3 xfailed` exit 0; `867 passed, 3 xfailed` all markers; ruff 27, zero NEW/GONE. Real output pasted in §4, from clean runs; two contaminated runs discarded and declared.
- [x] **No secrets in code or output** — no credentials, tokens or paths beyond the repo touched; no `.env` read or written.
- [x] **No destructive commands run without approval** — one `git stash push`/`stash pop` pair on two tracked files for the ruff entry comparison, popped and verified by `git status`; no reset, no force, no delete. **Nothing committed.**
- [x] **File count within cap** — **1 SOURCE file** (`mapper/app.py`), as declared. Tests uncapped.
- [x] **Review packet attached** — this document.
- [x] **Reverse census** — 18 touched symbols swept across the whole `tests/` tree; the only remaining `_search_is_live` / `action_back_or_home` references are in comments and docstrings, no live callers.
- [x] **Mutated tokens and hostile code points** — described by position and operation throughout; none spelled verbatim in this file.

---

# Review round 2 — code-review BLOCK cleared, security items applied

**Date:** 2026-08-29 · **Branch:** `feat/ui-next-batch-02` · **Entry:** `9ba2f26` · **nothing committed.**
**Scope unchanged:** 1 source file (`mapper/app.py`); tests uncapped.

**Exit digests, declared before any claim below is read:**

```
3aff38298f2cea33d4f891066f117f3d05614678c74bf2cf2a5333c6aa7fcea4  mapper/app.py
a257b9c1d2769a11c32856b72314a797cea87902f0cde5943b5c789f0c3be084  tests/test_search.py
```

## R2.0 · BLUF

Both HIGH findings are closed, both security mitigations are applied, both SHOULD-FIX comments are
corrected. The round-2 battery then **found two more gaps of its own** — both survivors, both sitting
between the arms the new battery fired, exactly as the four-for-four calibration warned. Both are now
closed and re-fired RED. Final battery: **7 arms, 7 KILLED**, every arm sha256-restored.

**One evidence-integrity failure of my own is declared in R2.8 and its runs were discarded, not
explained.** Two mutation batteries ran concurrently against one mirror. No verdict from either
appears in this document.

---

## R2.1 · H1 (HIGH) — the viewport ban is now DERIVED, not hand-listed

**Fixed.** The six-name tuple is gone. The set is closed transitively from `_count_line` over the same
`self.X` read map the `_PASS_FREE_READERS` arm uses 500 lines below — the algorithm the review pointed
at.

Measured on the shipped tree:

```
class parsed             : 93 methods
closure from _count_line : 8 methods
  hop 0  _count_line              leaks=[]
  hop 1  _search_order            leaks=[]
  hop 1  _suspended_count_line    leaks=[]
  hop 2  _query_echo              leaks=[]
  hop 2  _search_index            leaks=[]
  hop 2  _seat_glyph              leaks=[]
  hop 2  _whole_graph_tally       leaks=[]
  hop 3  _seat_row                leaks=[]
hand-list (round 1) missed : ['_query_echo', '_seat_glyph', '_seat_row']
total leaks reported       : 0
```

**Eight methods, zero leaks, no false positive, and three the hand-list never named** — the review's
figure reproduced exactly. `_search_hits` is deliberately **not** in this closure (the count line does
not reach it; `_view_state` does) and stays banned separately with its own stated reason.

Verdict against the mutant that walked through the round-1 list — `R2-A`, a new private helper
narrowing the tally by the fold state with the suspended region's tail pointed at it, which left
**850 passed** in round 1:

```
R2-A  KILLED  |  1 failed, 852 passed, 17 deselected, 3 xfailed
      reddened: test_the_count_and_the_paint_share_one_resolution
```

**Non-vacuity is derived too, and deliberately not a second hand-list.** The anchor is `_search_index`
— the owner every count path must reach, two hops out — chosen because it survives a mutation that
*re-routes* the tally, so a re-routing mutant trips the leak assertion rather than the anchor. The
transitive receipt is `reaching - {seed} - reads[seed]` being non-empty, plus a floor of six.

## R2.2 · H2 (HIGH) — the coercion sink on the new echo is gated

**Fixed.** New arm `test_the_query_echo_coerces_the_operators_text`, over five control classes
(U+202E, U+202D, U+200B, U+2066, U+001B), every one constructed from its number.

The arm carries the mutant as its own control: it asserts an equivalent-length raw slice **would have
carried all five through**, then asserts none reaches the painted region, then asserts the region is
still declaring the search — so the five absences mean coercion and not deletion.

```
R2-C (fit -> equivalent-length raw slice)  KILLED  |  3 failed, 850 passed
      reddened: test_the_query_echo_coerces_the_operators_text
      reddened: test_the_query_echo_bounds_rows_and_not_only_cells
      reddened: test_a_line_bearing_query_does_not_take_the_frame
```

## R2.3 · S1 / S1b (security) — the cap now bounds ROWS, and this repo owns the guard

**Fixed at the sink** — the query is line-flattened before it is fitted. `darkside.plain` is untouched:
U+000A and U+0009 stay preserved for the surfaces whose layout depends on them.

**I reproduced the defect myself rather than citing it.** At 118x34, above the bound:

| | ordinary query | line-bearing, unflattened | line-bearing, flattened |
|---|---|---|---|
| count region height | 1 | **32** | **2** |
| `#map-canvas` height | 27 | **1** | **26** |
| `esc limpiar` in painted frame | True | **False** | True |
| suspension notice in painted frame | True | **False** | True |
| echo rows | 1 | **32** | 1 |

That is the Inc-4b collapse shape one surface over, and it confirms the security review's numbers.

**Two arms, and the split is deliberate.** `test_the_query_echo_bounds_rows_and_not_only_cells` pins
the property at the sink across four floods (line breaks, tabs, 2000 ASCII, 500 wide ideographs), with
`darkside.plain` shown to KEEP both code points so the absence downstream is *this* sink's doing.
`test_a_line_bearing_query_does_not_take_the_frame` pins what the flattening BUYS, read from the
composited frame — the only claim the operator can check.

**S1b — the guard is pinned locally, not inherited. I verified both halves myself:** `textual==8.2.8`
is pinned **exactly** at `pyproject.toml:11`, and `Input._on_paste` does `event.text.splitlines()[0]`
at `textual/widgets/_input.py:758`. So the defect is unreachable today — but the defence is a
third-party implementation detail with no documented guarantee, this repo's `Input` declares neither
`max_length` nor `restrict`, and nothing asserted it. The new arms assert **our** behaviour at **our**
sink, so a version bump cannot remove the defence in silence.

```
R2-D (row flattening removed)  KILLED  |  2 failed, 851 passed
```

**The docstring's bound claim is corrected**: it now states that the cap is in cells, that the
dimension that matters is rows, that the two are not the same, and where the flattening closes it.

## R2.4 · M1 / M2 — the two misleading comments

**M1 — fixed** (`_pagination_text`). "Bounding it would not have helped" is replaced by "necessary but
not sufficient", carrying the review's converse control: minimap hidden and meter unbounded, at 80x24
all 21 visible rows are meter glyphs and the count is still off-screen; at 118x34 the same control
yields 31 readable rows with the count on the last. The comment now says the minimap and the meter are
**independent** causes and the remedy bounds all three together — which is what §7 already said.

**M2 — corrected, and the correction is "this number is not stable", not a second number.** I swept the
same band myself and **did not reproduce either prior figure**. Full disclosure in R2.8; the docstring
now records all three sweeps, why they differ, and the one thing every sweep agrees on — delta 0 or +1,
never off-frame — which is what the `+1` assertion actually rests on.

## R2.5 · BOOKKEEPING — predicate 1 is met under a MOVED bound

Recorded as instructed, without overstatement:

> **`LLR-N07.3.4` predicate 1 is met under a moved bound, NOT at the shipped bound.** Every
> above-the-bound arm reaches the branch by lowering `MAX_RENDER_NODES`. At the genuine bound
> (12002 nodes) `rows_in(...)` returns **0 rows** at both 118x34 and 80x24, because the pre-existing
> whole-screen collapse puts the region off-viewport. The `esc` half of `#D43` is real and
> size-independent by construction; the **paint** half currently lands where no operator can read it.

**`Inc-STRIPS` is a BLOCKER on closing `LLR-N07.3.4`, not a follow-up.**

## R2.6 · Test results — final tree, single writer, nothing else executing

```
default lane   :  853 passed, 17 deselected, 3 xfailed in 193.43s (0:03:13)   exit 0
all markers    :  870 passed, 3 xfailed in 222.02s (0:03:42)                  exit 0
```

**Ledger.** Default 850 -> **853**; all-markers 867 -> **870**. Both +3, and the +3 is the three new
arms: `test_the_query_echo_coerces_the_operators_text`,
`test_the_query_echo_bounds_rows_and_not_only_cells`,
`test_a_line_bearing_query_does_not_take_the_frame`. The two gap fixes in R2.7 added **assertions to
existing arms**, not arms, so they move no count — which is why the ledger still reads +3 after them.

*The orchestrator independently measured `853 passed, 17 deselected, 3 xfailed` on this tree while I
was stopped. That reading was taken at `tests/test_search.py` = `f41a176d…`, BEFORE the two gap fixes
landed; the run above is at the exit digest `a257b9c1…` and supersedes it. Both read 853 because the
fixes added assertions rather than arms.*

**Ruff SET over `mapper/ tests/`, identical scope:** `Found 27 errors.` — compared against a clean
`9ba2f26` checkout as sorted `file + rule` sets with line and column stripped: **diff empty, zero NEW,
zero GONE.**

## R2.7 · Mutation battery round 2 — 7 arms, 7 KILLED, 7 sha256 restores

Every arm was applied to a disposable mirror only; the real repo was never mutated. The harness asserts
the mutation is not a no-op before firing, asserts `sha256(after) == sha256(before)` after restoring,
and asserts the fired-arm count equals the declared one. Mutated tokens are described by position and
operation, never spelled.

| Arm | Operation | Aimed at | Applied digest | Verdict |
|---|---|---|---|---|
| **R2-A** | a NEW private helper narrows the tally by the fold state; the suspended region's tail is pointed at it | **the newly-derived ban** | `5f10f790…` | **KILLED** |
| **R2-B** | the fold state read inside `_query_echo` — one of the three methods the hand-list never covered | **the derived ban's REACH** | `58a34e37…` | **KILLED** |
| R2-C | `fit` replaced by an equivalent-length raw slice | H2's new arm | `0d927147…` | **KILLED** |
| R2-D | the row flattening removed, coercion and cap kept | S1's new arms | `4c59b051…` | **KILLED** |
| **R2-E** | the breaks DELETED instead of spaced | *gap probe, between the two new row arms* | `94a89142…` | **SURVIVED → fixed → KILLED** |
| R2-F | the region interpolates the raw query, bypassing the echo helper | sink-vs-helper coverage | `a36f96e2…` | **KILLED** |
| **R2-G** | the region declines to declare for queries of three characters or fewer | *the composited-frame arm, believed strong* | `3000e328…` | **SURVIVED → fixed → KILLED** |

Restores confirmed identical on every arm: `3aff38298f2cea33` / `a257b9c1d2769a11` — and
`f41a176d73905050` for the five fired before the gap fixes landed.

### The two survivors — both real, both closed

**R2-E · the flattening merged the operator's tokens.** Mapping U+000A / U+0009 to *nothing* instead of
to a space keeps rows bounded and cells bounded, so **all 853 arms stayed green** — while
`alfa<break>beta` echoed as one word nobody typed. A region that misreports the query it is declaring
is the same lying-affordance class this increment exists to close. Closed by pinning the separator;
re-fired **KILLED** (`test_the_query_echo_bounds_rows_and_not_only_cells`).

**R2-G · predicate 1 had no short-query arm.** A region that declines to declare for queries of three
characters or fewer was **green on all 853 arms**, because every query fixture in this file is longer
than three. A one-character query above the bound is exactly the silence `#D43` rejected — live enough
to change what `n` does, invisible enough to have no affordance. `LLR-N07.3.3` draws the only line that
matters — **blank**, not short — so the shortest non-blank queries are now asserted with the count
checked against the owner. Re-fired **KILLED**
(`test_above_the_bound_the_count_line_declares_the_search`).

**Calibration is now five-for-five.** Every round of this increment pair, the defects have sat
*between* the arms the battery fired. Both round-2 survivors were found by the two arms aimed at
machinery I believed was already strong, which is the instruction working exactly as intended.

## R2.8 · Disclosures — what I got wrong or could not reproduce

**1 · EVIDENCE-INTEGRITY FAILURE, MINE, DECLARED RATHER THAN BURIED.** I launched a mutation battery in
the background, my session stopped, and I launched a **second** battery believing the first was dead.
It was not. Both ran against **one mirror** — verified by process listing: PID 51844 (18:30:31) with
pytest child 41856, and PID 34664 (18:40:47) with pytest child 49956. Two writers on one tree.

It was caught by a digest that did not match: the second battery recorded a baseline of `4c59b051…`
where I had verified `3aff3829…` minutes earlier — and `4c59b051…` is R2-D's applied digest, i.e. the
ghost battery's mutation was live in the tree when the second battery read its baseline.

**Every verdict from both runs is discarded. None appears above.** I killed all four processes,
destroyed the mirror, re-cloned it, verified it byte-identical to the real repo, and re-fired all seven
arms **one per foreground call, single writer**. The real repo was never mutated — digests and
`git status` unchanged throughout. This is the third instance of this collision class in this batch —
the author's two discarded runs in §4, the reviewer's own parallel-lane collision — and the **first
where two writers actually overlapped rather than one being suspected**. The batch control the code
review made binding is correct and I violated it. The harness now writes an incremental ledger so a
killed run leaves partial-but-attributable evidence instead of a zero-byte log.

**2 · M2's swept widths — three measurements, three different answers, and I reproduce NEITHER prior
figure.** The docstring said 60 only. The security review swept the same band and found five. I swept
it again on the shipped tree, 60→160 step 5, height 34, `adjuntos` above the bound:

| basis | extra row at | count |
|---|---|---|
| docstring (round 1) | 60 | 1 |
| security review | 60, 65, 85, 90, 95 | 5 |
| **mine — length 1 vs 2000** | 60, 65, 70, 110, 115, 120, 125, 130, 135 | **9** |
| **mine — six-character fixture vs itself + 2000** | 60, 65, 70, 115, 120, 125, 130, 135 | **8** |

**I did not adopt the review's five.** Which widths pay depends on how much of the row the rest of the
strip has already spent, and the strip's chrome scales with the fixture — so the *count of widths* is
not a load-bearing figure, and the docstring now says so instead of asserting a fourth number. What
every sweep agrees on, and what the `+1` assertion actually rests on: the delta is 0 or +1 at every
width measured, never more, and the declaration is never taken off-frame. Corrected in `_query_echo`'s
docstring and in the frame arm's comment.

**3 · The "76,365 characters" minimap figure in F-2 is unreconciled.** The security review measures
3,944 region-clipped composited characters over the same 668 rows. I did not re-derive either; the two
use different measurement bases (widget render vs composited frame) and neither changes F-2's
conclusion. Flagged so the next reader does not treat it as verified.

**4 · Not re-verified this round:** the Spanish copy (still unreviewed by a native-speaking operator,
carried as R5), and the six round-1 battery arms the code review did not re-fire.

**5 · `01-requirements.md` was changed by the orchestrator during this round** — re-scoping
`LLR-N07.3.4`'s Statement, recording predicate 1 under a moved bound, and adding `Inc-STRIPS` to the
cut as a blocker. **I did not edit it**, as instructed.

## R2.9 · Files modified in round 2

| File | Change |
|---|---|
| `mapper/app.py` | `_query_echo` — line-flattening at the sink; docstring bound claim corrected (cells vs rows); swept evidence corrected; local-guard rationale recorded. `_pagination_text` — meter comment corrected to "necessary but not sufficient". **1 source file, as scoped.** |
| `tests/test_search.py` | viewport ban DERIVED by closure; 3 new arms; 2 gap-fix assertion blocks; the frame arm's sweep comment corrected. Tests uncapped. |
| `.dev-flow/…/increment-004c.md` | this section. |

## R2.10 · Evidence checklist — round 2

- [x] **Tests / type checks / lint pass** — `853 passed, 17 deselected, 3 xfailed` exit 0; `870 passed, 3 xfailed` all markers; ruff 27, SET-identical to `9ba2f26` (diff empty). Real output pasted in R2.6, from a tree with zero other writers, verified by process count.
- [x] **No secrets in code or output** — no credentials, tokens or paths beyond the repo; no `.env` read or written. No hostile code point spelled verbatim in this file: all named as `U+XXXX`.
- [x] **No destructive commands run without approval** — deletions confined to my own scratchpad (`rm -rf` on the disposable mirror and its logs) and `Stop-Process` on my own four runaway battery processes. **Nothing in the repo deleted, reset, forced or committed.**
- [x] **File count within cap** — **1 SOURCE file** (`mapper/app.py`). Tests uncapped, as scoped.
- [x] **Review packet attached** — this section.
- [x] **Battery integrity** — 7 arms declared, 7 fired, count asserted by the harness; 7 sha256 restores verified identical; two contaminated concurrent runs discarded and declared in R2.8.

---

# Review round 3 — independent confirmation pass · **VERDICT: BLOCK**

**Date:** 2026-08-29 · **Branch:** `feat/ui-next-batch-02` · **Entry:** `9ba2f26` · **nothing committed.**
**Conducted by:** a fresh `code-reviewer` with no round-1 or round-2 context, dispatched by the
orchestrator under the standing rule that **a HIGH is never self-cleared**.

## R3.0 · BLUF

**Inc-4c does NOT commit.** Round-1 `F1` is **narrowed, not closed**: the viewport ban is now genuinely
derived, and the derivation is correct over the edges it walks — but it closes only over `self.X` reads
**inside `MapScreen`**, so a module-level helper taking the screen as a parameter is invisible on both
of its axes at once. The reviewer built that helper and the whole default lane stayed green on a tree
whose count region lies. That is **risk `A-6`, fifth instance**, and the round-1 finding's own sentence
is still true.

Everything else in scope is **genuinely closed**, each confirmed by the reviewer's own mutation rather
than by reading the round-2 transcript: H2, S1/S1b, and both round-2 survivors (`R2-E`, `R2-G`).

**No shipped behaviour needs to change.** `mapper/app.py` is correct. Every finding is about what the
suite would let a later reader do to it.

## R3.1 · HIGH — `H1-R`: the derived ban closes only over `self.X` edges inside `MapScreen`

The reviewer **reproduced R2.1 exactly** from the code — 93 methods parsed, the same 8-method closure
from `_count_line`, 0 leaks, and `_query_echo` / `_seat_glyph` / `_seat_row` genuinely present where the
round-1 hand-list had missed them. The derivation also demonstrates its own RED: a viewport read added
to `_query_echo` reddens `test_the_count_and_the_paint_share_one_resolution` at
`tests/test_search.py:679`, naming both the method and the attribute.

**The gap is the closure's reach, not its arithmetic.** The read map is built from `self.X` reads only
(`tests/test_search.py:1257-1259`) and keyed on `MapScreen` methods only (`:1261-1262`). A module-level
function that receives the screen as a parameter contains no `self.` and is not a method — it is
invisible on **both** axes simultaneously.

Measured, one module-level function in `mapper/app.py` with `_whole_graph_tally` routed through it:

```
tests/test_search.py   36 passed   (per-arm: all green, census arm included)
full default lane      853 passed, 17 deselected, 3 xfailed in 194.47s
```

The declared baseline, digit for digit, on a tree whose region lies — measured at 12002 nodes with 1500
matching nodes folded: **truth 6001, painted 4501**. Round 1's exact numbers, reached through a link the
derived ban does not cross.

**Fix proven in both directions** by the reviewer: let the closure cross the class boundary — module-level
functions join the read map, bare-name calls become edges. Shipped tree + fix → `1 passed`, no false
positive. Mutant + fix → `AssertionError: '_visible_matches' is in the count chain and reads ['folded']`.

## R3.2 · Closures independently confirmed — per-arm verdicts, not exit codes

| Arm | Operation | Verdict | Reddened |
|---|---|---|---|
| MUT-1 | viewport read in `_query_echo` | **KILLED** | census arm (`:679`) |
| MUT-4 | `R2-E`: separator deleted, not spaced | **KILLED** | `…bounds_rows_and_not_only_cells` (`:1062`) |
| MUT-5 | `R2-G`: silent for queries of 3 chars or fewer | **KILLED** | `…count_line_declares_the_search` (`:922`) |
| MUT-6 | `S1`: row flattening removed | **KILLED** | `…bounds_rows…` (`:1041`) **and** `…does_not_take_the_frame` (`:2290`) |
| MUT-7 | `H2`: `fit` replaced by an equivalent-length raw slice | **KILLED** | `…coerces_the_operators_text` (`:980`) |

Confirmed alongside: H2's control is the right shape and does discriminate whole-echo deletion; `S1` is
at the correct sink, with `darkside.plain` untouched and `PRESERVED_CODE_POINTS` still the two expected
code points; `textual==8.2.8` is pinned **exactly** at `pyproject.toml:11` (pin re-verified); the frame
arm's bound is **relative** to the ordinary query at the same size rather than a constant; `R2-G`'s count
is checked against the *ordered* owner form (`:926`); `LLR-N07.3.3`'s blank line matches
`mapper/app.py:1972`; and `_search_hits`'s exclusion from the closure is soundly reasoned.

## R3.3 · Further findings — all test-strength, none shipped behaviour

| id | Sev | Finding | Fix |
|---|---|---|---|
| **F-B** | MEDIUM | The coercion arm cannot tell coercion from **truncation**. A mutant that cuts the echo at the first coerced point **SURVIVED 36/36** — a query echoes as its own prefix, and the coerced code point is reachable through the real paste path, which strips only line breaks. Same lying-affordance class as `R2-E`, one sink over. Shipped code is correct. | one added containment assertion |
| **F-D** | MEDIUM | `_search_hits` carries a *one-method* ban with no closure (`:689-690`) — weaker than the hand-list just deleted. | seed the corrected closure from both owners; measured 9 methods, zero leaks, free |
| **F-C** | MEDIUM | `VIEWPORT` (`:615`) is still a hand-list with **no non-vacuity anchor**: rename the attributes and every leak assertion passes on every method forever. | one-line subset assertion against the derived read map; passes today |
| **F-E** | LOW | The flattening table duplicates `darkside.PRESERVED_CODE_POINTS` and the arm asserts only a subset (`:1024`), so growth there silently reopens `S1`. | derive the table, or tighten the subset to equality |
| **F-F** | LOW | R2.1's "non-vacuity is derived too, and deliberately not a second hand-list" **overstates**. The transitive receipt at `:675` is derived; `:673-674` is a two-name pin plus a magic floor. Correct practice for an anchor — the record should simply say so. | correct the sentence |

## R3.4 · MIRROR-FIDELITY TRAP — a batch-level evidence finding

**`git clone --local --no-hardlinks` does not produce a byte-identical mirror of this repo.** With
`core.autocrlf=true`, the clone re-materialises tracked files with CRLF while parts of the source working
tree hold LF — `mapper/search.py` is 5910 B at source and 6032 B in the clone, different sha256.
Overlaying only `app.py` / `test_search.py` by hand **hides** this, because those two are then byte-exact.

**Both round-1 reviews and both author batteries used that method.** Their overlaid files are byte-exact,
so **their verdicts stand**; but any claim resting on the *rest* of the tree rested on converted sources.
The confirmation reviewer discarded the clone, rebuilt by `tar` copy, and verified **all 236 tracked files
byte-for-byte** before firing a single arm, reproducing the baseline at `853 passed, 17 deselected,
3 xfailed in 194.47s`.

**Binding for the remainder of this batch:** a mirror is not a mirror until it is verified byte-for-byte
across the whole tree. This joins the one-writer-per-tree rule as a standing evidence control, and it is
a candidate for upstream push under `C-45` — it is stack-portable to any Windows checkout with
`autocrlf` on.

## R3.5 · Orchestrator's own verification of the round-2 tree

Re-run rather than trusted, before the reviewer was dispatched:

```
default lane   :  853 passed, 17 deselected, 3 xfailed in 200.07s   exit 0
all markers    :  870 passed, 3 xfailed in 227.70s                  exit 0
sha256 mapper/app.py        3aff38298f2cea33…   (matches declared exit digest)
sha256 tests/test_search.py a257b9c1d2769a11…   (matches declared exit digest)
```

**Ruff SET over `mapper/ tests/`, identical scope:** baseline **27**, working tree **27**, **zero NEW,
zero GONE**. The comparator asserts `parsed base=27 work=27` **before** comparing.

**Two disclosures of the orchestrator's own, declared rather than buried:**

1. **A vacuous comparison, caught by an adjacent count.** The first set-comparison ran a broken `sed`
   that produced two **empty** sets; `diff` duly reported them "identical". It was visible only because
   the entry counts were printed beside the verdict. This is the `0 == 0` shape already recorded twice in
   this batch's harness disclosures — third instance, and the reason the rebuilt comparator asserts its
   parse count before it is allowed to compare.
2. **A broken line-ending probe.** `grep -c $'\r'` reported **0** for all four files measured, including
   two that are CRLF throughout. The uniform answer across heterogeneous inputs was the tell; the byte
   sizes contradicted it. Re-measured in Python over raw bytes: working `app.py` is CRLF (3318),
   working `search.py` is LF (0), and the `git archive` baseline is CRLF for both — so **`git archive`
   converts too**, not only `git clone`. The ruff SET result is unaffected (the sets matched exactly, and
   ruff's rule set here is line-ending-insensitive), but the baseline must **not** be described as
   byte-faithful. Recorded so no later reader inherits that claim.

## R3.6 · Gate position

**BLOCK.** One HIGH survives; `Inc-4c` is not committed and the tree is left exactly as round 2 finished
it — digests unchanged, nothing staged. The unmet exit-criteria axis is **Certainty**: the derived ban is
a real improvement over the hand-list but is still not falsifiable against the class of link the finding
names, and the reviewer demonstrated a green full lane over a lying region.

Awaiting the coordinator's ruling on whether to fix in-increment (the five fixes are small, and four of
the five are one line each) or to re-scope, this being the **second** round on the same HIGH.

---

# Round 3 — fixes applied · awaiting the narrow third pass

**Date:** 2026-08-29 · **Branch:** `feat/ui-next-batch-02` · **Entry:** `9ba2f26` · **nothing committed.**
**Authorised by coordinator ruling, 2026-08-29:** fix in-increment (one source file, zero
shipped-behaviour change, the `H1-R` fix proven in both directions, four one-liners), then a third pass
scoped ONLY to `H1-R` and `F-B`.

**Exit digests, declared before any claim below is read:**

```
c0709eabb0453d3263e9fc80a4131c5393fd9a6e608a17569086972c79e4f21a  mapper/app.py
6a7e736a4e7b1a22dc1a0dfe55e2da20facc5c6d94c1be5813a864244a0298fa  tests/test_search.py
```

## R3F.1 · The HIGH — the closure now spans BOTH planes

`_count_chain(src, seeds)` replaces the `MapScreen`-keyed, `self.X`-valued map. Two changes, and both
were required — either alone leaves the mutant invisible:

* **the map spans both planes** — `MapScreen` methods *and* module-level functions of `mapper/app.py`.
  For a method `reads[name]` is its `self.X` reads; for a module-level helper it is **every** attribute
  read, because there the screen arrives as a parameter and has no privileged spelling;
* **the chain advances on two edge kinds** — an attribute read **and** a bare-name call, the latter
  being the only way a helper is reached at all.

**Counterfactual, executed on a byte-verified mirror, restore confirmed identical:**

```
MUT-2  (module-level `_visible_matches(screen, ids)` reading the fold state,
        with `_whole_graph_tally` routed through it)        KILLED
  reddened: test_the_count_and_the_paint_share_one_resolution
  AssertionError: `_visible_matches` is in the count chain and reads ['folded']
  applied  c0709eab… -> 70006371…      restored -> c0709eab…   (byte-identical)
```

**THE BOUNDARY, STATED RATHER THAN CLAIMED — recorded at the coordinator's instruction, because this
ban has now been evaded four times and the sentence that names the blind spot is what saves the sixth
instance.** The derivation is carried in `_count_chain`'s own docstring so it travels with the code:

> **It sees:** `MapScreen` methods; module-level functions in `mapper/app.py`; and the edges between
> them in either direction (method to helper, helper back to method).
>
> **It does NOT see:** a helper defined in ANOTHER module; an attribute reached by `getattr` or a
> subscript rather than a dotted read; a call dispatched through a variable, a dict of callables, or a
> bound-method reference; a method resolved on a different class; or a viewport value passed in as a
> plain ARGUMENT rather than read off an object.

Each of those is a live fifth escape and **none is guarded**. That is the honest statement of reach.

## R3F.2 · `C-55` discharge — the crossing is a NO-OP on today's tree

`mapper/app.py` contains no module-level helper inside the count chain, so the new edge kind changes
nothing today and would be **untested however green the suite**. That absence is exactly what made the
ban evadable, so it cannot also be the reason not to test the fix. New arm
`test_the_count_chain_closure_crosses_the_class_boundary` constructs the case the tree lacks, with
**both** controls:

* **positive** — the reviewer's mutant in miniature: the helper is reached, and the fold-state read is
  reported;
* **negative** — same topology, same edge, benign read: the helper is still reached and **no** leak is
  reported, so the arm discriminates instead of flagging every helper.

This is the batch's only new test node, and the whole of the `+1` in the ledger below.

## R3F.3 · The four remaining findings

| id | Fix | Evidence |
|---|---|---|
| **F-B** | the coercion arm asserts the query's **TAIL**, not only its head | **MUT-8 KILLED** — echo cut at the first coerced point; the region declared `«zeta»`, a query nobody typed. Applied `eebc05dc…`, restored `c0709eab…` byte-identical |
| **F-D** | `_search_hits` seeded into the SAME closure; its separate one-method ban deleted | it was weaker than the hand-list the round-2 work removed |
| **F-C** | `VIEWPORT` given a non-vacuity anchor — `set(VIEWPORT) <= reads_by_method["_view_state"]` | without it, renaming the attributes leaves every leak assertion passing forever: a `C-31` vacuous INPUT SET, invisible to every code mutation |
| **F-E** | the flattening table is **derived** from `darkside.PRESERVED_CODE_POINTS` at the sink, and the arm iterates that owner | the sink no longer duplicates the frozenset that decides it; a code point added there is flattened here by construction rather than reopening the row bound silently |
| **F-F** | the overstatement corrected in place | the transitive receipt IS derived; the two names and the floor are a **PIN** — correct practice for an anchor, but not a derivation, and round 2 called it one |

`F-E` is the round's only shipped-source change beyond docstrings, and it is behaviour-identical today:
`PRESERVED_CODE_POINTS` is exactly the two code points the table used to spell.

## R3F.4 · Test results — one clean run, tree pinned before AND after

```
default lane   :  854 passed, 17 deselected, 3 xfailed in 198.82s   exit 0
all markers    :  871 passed, 3 xfailed in 220.54s                  exit 0
TREE UNCHANGED THROUGHOUT   (sha256 of both sources pinned pre-run and post-run, diff empty)
```

**Ledger.** Default 853 -> **854**; all-markers 870 -> **871**. Both **+1**, and the +1 is the single
new arm named in R3F.2. The other four fixes added assertions to existing arms, so they move no count.

**Ruff SET over `mapper/ tests/`, identical scope, against a clean `9ba2f26` export:** base **27**,
work **27**, **zero NEW, zero GONE**. The comparator asserts `parsed base=27 work=27` **before** it is
allowed to compare.

## R3F.5 · Disclosures — three, all mine, none buried

1. **A vacuous set comparison that reported success over nothing.** The first ruff comparator ran a
   broken `sed`, produced two EMPTY sets, and `diff` duly called them identical. Visible only because
   the entry counts were printed beside the verdict. Third instance of the `0 == 0` shape in this batch.
   The rebuilt comparator asserts its parse count first; a parse failure now refuses to compare.

2. **A restore that was semantically right and BYTE-WRONG.** The first mutation harness used
   `read_text`/`write_text`, which round-trips CRLF to LF on this checkout: the restore left the file
   correct to read and **12bf8457…** where the baseline was **c0709eab…**. **The sha256 restore assert
   caught it, which is the entire reason that assert exists.** Harness rebuilt on binary I/O with the
   file's own line ending detected from its bytes; the mirror was rebuilt and both mutants re-fired,
   each restore then confirmed byte-identical. **No verdict in this document comes from the
   LF-normalised mirror.**

3. **I EDITED A FILE WHILE A LANE WAS READING THE TREE.** Correcting the C-56 offender below, I wrote
   to `.dev-flow/` while the all-markers lane was mid-run. That run reported `1 failed, 870 passed` and
   **is discarded, not explained** — the tree moved under it, which disqualifies it whatever it said.
   Both lanes were then re-run from a frozen tree, and that run pins the sources before AND after to
   prove it. This is the fourth collision-class instance in this batch and the second by an
   orchestrator; the control was already binding and I broke it anyway.

## R3F.6 · A finding AGAINST the confirmation review's own artifact (`C-56`)

`increment-004c-code-review-confirmation.md` **spelled U+200B verbatim** — one occurrence, in a line
quoting a query — despite the dispatch instruction to name hostile code points as `U+XXXX`. The repo's
own sweep `test_no_tracked_file_spells_a_coerced_code_point_INCLUDING_the_artifacts` caught it, which
is precisely `C-56`'s claim: **an evidence transcript is corpus a scanner reads, and a mutation spelled
in a transcript has not been reverted.** Corrected to the bracketed named form; the sweep passes.

Recorded as a finding rather than a tidy-up because it is the guard working on a REVIEW artifact, which
is the case `C-56` was written for and the one nobody expects to trip.

## R3F.7 · Batch control added — mirrors, alongside one-writer-per-tree

**A mirror is not a mirror until it is verified byte-for-byte across the whole tree.**
`git clone --local --no-hardlinks` re-materialises tracked files with CRLF under `core.autocrlf=true`,
and **`git archive` converts too** — measured here: `mapper/search.py` is 5910 B (LF) in the working
tree and 6032 B (CRLF) in both derivations, different sha256, while `mapper/app.py` is CRLF in the
working tree itself. This tree is genuinely mixed, so a whole-tree assumption in either direction is
wrong.

**The control:** create evidence mirrors with autocrlf disabled (`git -c core.autocrlf=false clone`) or
by byte-preserving copy, then **verify every file's digest against the source before firing any arm**;
and do mutation I/O in **binary**, never through `read_text`/`write_text`. It is recorded here beside
the one-writer-per-tree rule so the two travel together, per the coordinator's ruling.

`docs/engineering-rules.md` does not exist in this project, so these controls currently live scattered
across increment records. Creating it as the controls home is **approved for the batch's docs/close
phase** and is carried in the backlog until then.

## R3F.8 · Files modified in round 3

| File | Change |
|---|---|
| `mapper/app.py` | `_query_echo` — flattening table DERIVED from `darkside.PRESERVED_CODE_POINTS`; docstring records why the duplicate was a defect. **1 source file, scope unchanged.** |
| `tests/test_search.py` | `_app_source` + `_count_chain` (both planes, both edge kinds, boundary docstring); the census arm reseeded from both owners with the `VIEWPORT` anchor and the corrected receipt sentence; 1 new synthetic crossing arm; the coercion arm's tail assertion; the flattening arm derived from its owner. Tests uncapped. |
| `.dev-flow/…/increment-004c-code-review-confirmation.md` | one verbatim U+200B replaced by its named form (`C-56`) |
| `.dev-flow/state.json` | Phase-3 cut synced to the amended `01-requirements.md` order (`Inc-5` then `Inc-STRIPS`), with authority + supersession recorded; parse guard run after the write |
| `.dev-flow/…/increment-004c.md` | this section |

## R3F.9 · Evidence checklist — round 3

- [x] **Tests / type checks / lint pass** — `854 passed, 17 deselected, 3 xfailed` exit 0; `871 passed, 3 xfailed` all markers; ruff SET-identical to `9ba2f26`, zero NEW / zero GONE. One clean run, from a tree pinned before and after; one contaminated run discarded and declared in R3F.5.
- [x] **No secrets in code or output** — no credentials, tokens or paths beyond the repo; no `.env` read or written. No hostile code point spelled verbatim in this file; mutations described by position and operation.
- [x] **No destructive commands run without approval** — deletions confined to my own scratchpad (the disposable mirror). **Nothing in the repo deleted, reset, forced or committed.**
- [x] **File count within cap** — **1 SOURCE file** (`mapper/app.py`). Tests uncapped, as scoped.
- [x] **Review packet attached** — this section.
- [x] **Counterfactuals** — 2 arms fired (`MUT-2`, `MUT-8`), both KILLED, both on a byte-verified mirror, both restores confirmed identical by sha256; harness asserts each mutation is not a no-op before firing.
- [x] **`C-55` discharged** — the new edge kind is a no-op on today's tree and is tested synthetically, with a positive AND a negative control.

---

# Pass 3 — narrow confirmation · **VERDICT: PASS** · Inc-4c may commit

**Date:** 2026-08-29 · Fresh independent reviewer, scoped by coordinator ruling to **`H1-R` and `F-B`
only**. Mirror built by byte-preserving copy, **91/91 files verified byte-for-byte**, binary I/O, every
restore sha256-asserted, one writer, arms one at a time. **The repo was never written to.**

## P3.1 · `H1-R` — CLOSED

The round-2 escape, rebuilt independently by the reviewer, is dead:

```
MUT-A  (module-level helper reading the fold state, tally routed through it)   RED
       tests/test_search.py:835
       AssertionError: `_visible_matches` is in the count chain and reads ['folded']
       applied digest 700063714bf3 -- independently reproduces R3F.1's figure
```

Derivation measures **9 reached, 0 leaks, 96 callables, helper plane exactly 3** — confirming both
`F-D`'s fold-in and R3F.2's no-op premise. Supporting: renaming the attribute reddens at `:792`, so the
`VIEWPORT` anchor is live and `F-C` was a real finding; `F-F`'s corrected PIN-vs-derivation sentence
reads accurately.

## P3.2 · The boundary statement was CONSTRUCTED, and one clause was FALSE

The reviewer did not accept the blind-spot list — it built four of the clauses:

| Arm | Clause | Declared | Measured |
|---|---|---|---|
| `MUT-B` | bound-method reference | not seen | **RED — it IS seen** |
| `MUT-D` | `getattr` | not seen | GREEN — accurate |
| `MUT-C2` | viewport as plain ARGUMENT | not seen | GREEN, 37/37 — accurate |
| `MUT-J` | helper in another module | not seen | GREEN, 37/37 — accurate |

**Corrected in `_count_chain`'s docstring.** A bound-method reference is a *dotted read* — the very edge
kind the closure walks — so the clause was removed. **Overstating one's own blindness is not the safe
error it appears to be:** it sends the next reader hunting where the guard already works, which is the
opposite of what the boundary statement exists to do.

**The finding worth carrying, and it sharpens the ruling that produced this statement:** two surviving
clauses are **this file's existing idiom**, not exotic shapes. `app.py:1516-1517,1535-1536` already
writes `self._clamp_pan(self.pan_x, ...)` — viewport as a plain argument. And the count chain **already
crosses a module boundary today**: `_query_echo`, inside the closure, calls `darkside.fit` at
`:1880-1883`. Ranked likelihood for a sixth instance: **another module > plain argument > another class
(11 unwalked) > `getattr`**. That ranking is now in the docstring.

## P3.3 · `F-B` — CLOSED, with its scope stated rather than claimed

```
MUT-E  (cut at the first coerced point)      RED at :1142
MUT-F  (drop the tail's last character)      RED
MUT-G  (head and tail kept, middle elided)   GREEN
```

The two anchors separate coercion from truncation **at the echo's boundaries, not in general** — a
two-anchor containment is blind to elision strictly between them. On this fixture the only interior span
is the hostile run itself, **whose removal IS the coercion being asserted**, so `MUT-G` is the arm's
honest limit and not a defect: a third anchor there would assert the absence the arm exists to allow.
The comment now says exactly this instead of claiming the general property.

## P3.4 · Out of scope — surfaced, NOT blockers, carried to backlog

Per the ruling, these were reported without opening a fourth round:

- **O-1 (MEDIUM)** — a derivation flagging *every* helper as reached still passes the crossing arm. Both
  controls assert membership POSITIVELY, so they discriminate on the **read** axis only; the **reach**
  axis is unguarded. R3F.2's "discriminates instead of flagging every helper" was **not backed, and is
  corrected in this pass**. Fix (backlog): add an unreachable orphan helper and assert it is absent from
  the closure. Over-reach direction is the safe one.
- **O-2 (MEDIUM) — a mirror trap the R3F.7 byte check STRUCTURALLY CANNOT CATCH, because the bytes are
  identical.** The repo is pip-installed **editable** (`_editable_impl_mapper.pth` puts the repo root
  permanently on `sys.path`) and `tests/` is a package — so a mirror run guarding only on
  `mapper.__file__` can silently execute the **repo's** test module against the mirror's source. The
  reviewer's own first `MUT-A` did exactly that. `cp -r` also copies `__pycache__`, whose `.pyc` carries
  the repo's `co_filename`. **Control: assert the TEST MODULE's `__file__` as well as the package's, and
  purge bytecode caches before firing.** The reviewer re-fired the whole battery after fixing both;
  verdicts unchanged. **This supersedes the sufficiency of R3F.7's check and joins it as batch control.**
- **O-3 (LOW)** — `len(helper_plane) >= 3` sits exactly on today's value (3 module-level defs), so it is
  a floor with no headroom.

## P3.5 · What pass 3 could NOT verify — stated, not glossed

1. **The 854/871 ledger.** The reviewer's mirror holds 91 of 236 tracked files and omits `.dev-flow/`,
   so its own lane reports 46 failures, **all** in `test_inc3_census.py` / `test_repair_*.py`, which read
   the `.dev-flow` corpus the mirror lacks — mirror-scope artifacts, not defects. The ledger rests on the
   orchestrator's own clean run (R3F.4), which pinned the tree before and after.
2. **R3F.4's `+1`** — the round-2 tree is not preserved; whole-increment net vs HEAD is +5/−1 test
   functions.
3. **The ruff SET** — not re-run in pass 3; rests on R3F.4.
4. **That `MUT-C2` yields an operator-visible wrong number** — the ban is structurally blind and 37/37
   pass, which is what the finding rests on; the probe took the default argument and showed 12002 either
   way.
5. Everything outside `H1-R` / `F-B`, by scope.

## P3.6 · Corrections applied before commit

All three are accuracy fixes to claims **I** made, and none changes a predicate:

| # | Correction | Where |
|---|---|---|
| 1 | "bound-method reference" removed from the NOT-seen list; the construct-don't-reason note and the likelihood ranking added | `_count_chain` docstring |
| 2 | the `F-B` claim scoped to "at the echo's boundaries", with `MUT-G` named as the honest limit | coercion arm comment |
| 3 | R3F.2's negative-control claim corrected — read axis yes, reach axis no | crossing arm docstring |

## P3.7 · Gate position

**PASS.** No HIGH survives on either scoped finding. Both exit-criteria axes that were unmet are now
met: **Certainty** (the escape is dead, the counterfactual executed and reproduced independently, the
boundary measured rather than asserted) and **Evidence** (every claim carries an executed transcript or
a `file:line`). Inc-4c is cleared to commit.

## P3.8 · Relay re-measurement, 2026-09-10 — the gate evidence re-run before commit

The gated tree sat uncommitted for **twelve days**. Evidence is not inherited across that gap: all
three figures were **re-measured on today's bytes**, from a tree pinned before and after, and all
three reproduce the round-3 result exactly.

| Measurement | R3F.4 (2026-08-29) | Relay (2026-09-10) | Verdict |
|---|---|---|---|
| default lane | `854 passed, 17 deselected, 3 xfailed` exit 0 | `854 passed, 17 deselected, 3 xfailed` exit 0, 210.34s | **reproduces** |
| all markers (`-o addopts=`) | `871 passed, 3 xfailed` exit 0 | `871 passed, 3 xfailed` exit 0, 234.76s | **reproduces** |
| ruff SET over `mapper/ tests/` vs a clean `9ba2f26` export | 27 = 27, zero NEW / zero GONE | 27 = 27, **19 `(file, rule)` pairs**, zero NEW / zero GONE | **reproduces** |

The lane arithmetic holds independently: `854 + 17 deselected = 871`.

**Tree frozen through both lanes.** `mapper/app.py` and `tests/test_search.py` were sha256-pinned
before the first lane started and again after the second finished; both digests are unchanged, so
neither run read a tree that moved under it. `__pycache__` was purged before the first lane (**C-46**:
a same-size restore is invisible to a digest check but not to the bytecode cache).

### P3.8.1 · The pass-3 digest divergence, reconciled

`increment-004c-code-review-pass3.md` pins the verified bytes. Against today's tree:

- **`mapper/app.py` — `c0709eab…`, MATCHES pass 3 exactly.** The gated source file is byte-unchanged
  since the verdict.
- **`tests/test_search.py` — differs from the pass-3 pin.** The divergence is **§P3.6 of this
  document**: three corrections applied *after* the verdict and recorded there before commit, all
  three in this file, all three prose — a docstring, a comment, a docstring. No predicate moved, which
  §P3.6 states as the reason it listed them.

**Stated as a limit rather than glossed:** the pass-3 bytes of `test_search.py` are **not
recoverable** — the file was never committed, `git stash list` is empty, and none of the 11 dangling
blobs in the object store hashes to the pinned digest. So "the delta is prose-only" rests on §P3.6's
own contemporaneous record plus today's byte census below, and is **not** re-derived from the two
sides. Anyone wanting that derivation cannot have it from this repository.

What *is* executed on today's bytes, and stands on its own:

```
mapper/app.py        : 153466 bytes, 375 non-ASCII, 3326 CRLF, 0 bare LF
tests/test_search.py : 130065 bytes, 159 non-ASCII, 2612 CRLF, 0 bare LF
```

Both files are uniformly CRLF with no mixed endings, and the repo's own artifact sweep
(`test_no_tracked_file_spells_a_coerced_code_point_INCLUDING_the_artifacts`) is inside the 854 and
green on exactly these bytes.

### P3.8.2 · Two instrument defects found in the relay's OWN ruff comparator

Both were found before any verdict was believed, which is the only reason they are reportable
(**C-57**).

1. **Config-discovery contamination — the baseline was measuring a different rule set.** The clean
   `9ba2f26` export was materialised under `/tmp`, and ruff walks *upward* for configuration: from
   that path it resolved a config enabling `I001`, which is **not** in ruff's default set, and
   reported `Found 70 errors` against the repo's 27. The two sides were never comparable. Confirmed
   by `--show-settings` (`I001` present in the export's resolved rules, absent in the repo's), and
   closed by running **both** sides `--isolated --no-cache`, which removes discovery entirely. Both
   then report 27.
2. **ANSI colour broke the parse, and the parse returned silently empty.** Ruff colourises even when
   redirected, so a rule-code regex over the raw log matched **zero** entries on both sides — the
   `0 == 0` shape that R3F.5 disclosure 1 already caught once in this increment, reproduced by me on
   a different instrument. Closed with `--output-format=concise` plus explicit SGR stripping.

**The comparator now refuses to compare before it asserts its own parse count** (`parsed == declared`
on each side, 27 and 27), and carries a **positive control**: a synthetic entry planted into the work
set must be reported as NEW. It is, so a `zero NEW / zero GONE` verdict from it is a measurement and
not a silence. The export it reads is itself digest-verified — all **236** blobs `git hash-object`
byte-identical to `9ba2f26`, materialised with `core.autocrlf=false` (**B-53**: both `clone --local`
and `git archive` re-materialise CRLF with autocrlf on, which would have made every file differ).

### P3.8.3 · A staleness in this document's own BLUF, left standing and named

The BLUF reports `850 / 867` and calls them "matching the declared ledger exactly". Those are
**round-1** figures. Rounds 2 and 3 each added an arm, and the gate closed at **854 / 871** (R3F.4) —
the numbers this relay reproduced. The BLUF was never updated as the rounds landed.

It is **not** edited here. Rewriting a gated artifact's headline after its verdict is the same move
that produced the digest anomaly §P3.8.1 exists to explain, and this document's own R3F.5 disclosure 3
records what editing a tree mid-gate costs. The correction is recorded instead: **the increment's
result is `854 / 871`; any figure in this document not carrying a round label is round 1.**
