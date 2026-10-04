# Increment 5 — `LLR-N07.2.2b`: every renderer paints its hits (`AT-024`)

**Batch:** `2026-08-26-ui-next-batch-02` (SEALED) · **Increment:** `Inc-5` · **Branch:** `feat/ui-next-batch-02`
**Entry commit:** `90e2a3f` (Inc-4c close), tree clean at entry · **NOT COMMITTED** — the working tree is what is gated.
**SOURCE FILE COUNT: 3** — `views/outline.py`, `views/radial.py`, `views/lane.py`. Exactly the sealed cut. Tests uncapped.
**Protocol: LIGHTER lane (`A-91`)** — see §7 for the executed justification. Battery NOT skipped.
**Language:** English (engineering artifact).

---

## BLUF

Five renderers now paint `state.hits` distinguishably; `layered` already did. The derived renderer
set goes from **1 of 6 compliant to 6 of 6**, measured by the `#D42` observable (style spans), and
`AT-024` finally has a node on disk.

```
default lane : 887 passed, 17 deselected, 3 xfailed   exit 0
all markers  : 904 passed, 3 xfailed                  exit 0
ruff SET     : 27 = 27 vs 9ba2f26, zero NEW, zero GONE
battery      : 9 mutants, 9 KILLED, 0 SURVIVED, 0 BAD, 9 sha256-verified restores
```

**Ledger: `887 = 854 - 0 + 33`**, and the 33 is exactly the arm count of the one new test file.
All-markers moves by the same +33 (871 → 904). Lane arithmetic holds independently: `887 + 17 = 904`.

**Three things this increment found that it was not looking for, none of them silent:**

1. **A mutant SURVIVED the first battery** — `RailTimelineRenderer`'s TRUNK path was unobserved by
   all 27 arms. An arm was added *because* the mutant survived, not because the gap looked plausible.
2. **The sealed `#D42` threshold does not catch a paint-everything renderer.** Executed: two
   paint-everything mutants are killed by **exactly one arm**, and it is not the sealed one. The
   sealed threshold is kept as the gate and a discriminating negative ships beside it (§3.2).
3. **B-55 cannot be closed in this increment's budget** — it needs a 4th source file and a change to
   a shipped gated behaviour. Measured, not estimated (§6).

---

## 1 · The pre-gate, executed before a line was written

The renderer set is **derived** (tracked files under `mapper/views/`, classes defining `render`,
`Protocol` subclasses excluded **by the flag, not by name** — `#D42`), and asserted **non-empty
before anything is evaluated**.

```
derived renderer set: 6 classes
fixture positive control: exactly one node matches -- ['hit']

  lane.HybridLaneRenderer    text_differs=False  spans_differ=False
  lane.LaneRenderer          text_differs=False  spans_differ=False
  lane.RailTimelineRenderer  text_differs=False  spans_differ=False
  layered.LayeredRenderer    text_differs=False  spans_differ=True   <- the ONE compliant renderer
  outline.OutlineRenderer    text_differs=False  spans_differ=False
  radial.RadialRenderer      text_differs=False  spans_differ=False

COMPLIANT   (1): ['layered.LayeredRenderer']
PRE-FIX RED (5): [the other five]
```

This reproduces the `#D42` table on today's tree from a **fixture built from the rule**, not copied
from the sealed table. Post-fix the same probe returns **COMPLIANT (6), PRE-FIX RED (0)**.

**`text_differs=False` on all six, before and after.** That is `#D42`'s finding standing up under
re-execution: a hit is painted by STYLE and never by adding characters, so the parked "the rendered
text differs" threshold would have **false-failed a correct implementation** (`C-53`).

### 1.1 · One correction to the sealed record, found by executing it

`#D42`'s table describes its probe as driving `state.query="ana"` against `""`. **`ViewState` has no
`query` field** — `HLR-N07.1` removed it precisely so a renderer evaluates no predicate of its own,
and my first probe raised `TypeError` on all six. The table's *verdicts* are correct and reproduce
exactly; only its description of the driver is stale. Today the sole driver is `hits`. Recorded here
rather than corrected in the sealed document.

## 2 · What changed — SIX hit sites, three files

Each site gains one branch. The style is `f"{darkside.INK} on {darkside.STEP}"` — **the style
`layered` already used**, not a new token.

| File | Renderer | Site |
|---|---|---|
| `views/outline.py` | `OutlineRenderer` | the `walk()` title branch |
| `views/radial.py` | `RadialRenderer` | the node-pill character loop |
| `views/lane.py` | `LaneRenderer` | the branch-title append |
| `views/lane.py` | `RailTimelineRenderer` | `main_style` (trunk) **and** `label_style` (every other branch) |
| `views/lane.py` | `HybridLaneRenderer` | the row-name append |

**Precedence: selection is painted ON TOP of a hit**, which is the order `layered` already uses
(`layered.py:628`, "selection highlight on top"). Not invented here.

### 2.1 · Why no shared `HIT_STYLE` constant — a decision, not an oversight

Six new hit sites spell the style inline (`RailTimelineRenderer` holds TWO -- trunk and label -- which §2's table shows and this sentence undercounted until round 4). A shared constant was considered and **rejected on
`C-50`'s own terms**: `layered.py:539` already spells this style inline, and `darkside.py:286`
spells it inline too, so a new constant would have created a **second home**, not one — and closing
that properly means editing `layered.py` and `darkside.py`, taking the increment to 5 source files
past a sealed 3-file cut.

The duplication is instead made **observable**:
`test_llr_n07_2_2b_every_renderer_uses_THE_SAME_hit_style` derives, per renderer, the style set a hit
*introduces*, and asserts the union is exactly one style and that it is the named one. Guarded in
both directions. `M9` proves it reddens on drift.

## 3 · The arms, and why each exists

33 arms in `tests/test_views_hits.py`. Six are the derived-set guards; the rest parametrise over the
derived set, so **a seventh renderer is covered without anyone editing this file**.

### 3.1 · The sealed threshold

`test_llr_n07_2_2b_every_renderer_paints_hits` — the `#D42` threshold verbatim: spans with a
non-empty hit set differ from spans with an empty one. RED on 5 of 6 pre-fix.

### 3.2 · The discriminating negative, and the measurement that justifies it

**The sealed threshold is satisfied in full by a renderer that paints EVERY node whenever any search
is active.** Its spans do move. It is also wrong, because the Statement says hits are painted
*"distinguishably from NON-HIT nodes"*.

`test_llr_n07_2_2b_the_paint_is_keyed_on_WHICH_node_is_a_hit` renders two different single-element
hit sets: a correct renderer paints a different picture for each, a paint-everything renderer paints
the identical picture for both.

**Executed, and this is the whole argument for the arm existing:**

| mutant | arms reddened |
|---|---|
| `M7-outline-paint-everything` | **1** — `the_paint_is_keyed_on_WHICH_node_is_a_hit[outline]` |
| `M8-radial-paint-everything` | **1** — `the_paint_is_keyed_on_WHICH_node_is_a_hit[radial]` |

The sealed threshold stays GREEN on both. Without this arm both mutants ship.

### 3.3 · The arm that exists because a mutant survived

`test_llr_n07_2_2b_a_hit_on_the_FIRST_branch_is_painted_too`.

The first battery fired `M4`, which stops `RailTimelineRenderer` painting a hit on the **trunk**
(`branches[0]`, a different code path from every other branch). **It SURVIVED all 27 arms.** The
which-node arm compares hit-on-first against hit-on-other, and those still differ when only the
trunk's paint is dead — one of them simply paints nothing. A whole shipped path was unobserved with
every arm green. With the arm added, `M4` is killed by exactly it.

### 3.4 · An arm corrected by measurement, not by argument

`..._a_hit_outside_the_first_branch_is_painted_too` first drove **80 columns** and FAILED on
`RailTimelineRenderer`. It was **not** a paint defect: at 80 columns that renderer never draws the
third branch at all — `max_label` clips it and the title is absent from the rendered text. Measured
across widths:

```
w= 80  hit(slot1)_differs=True  other(slot2)_differs=False  Cronograma_in_text=False
w=100  hit(slot1)_differs=True  other(slot2)_differs=True   Cronograma_in_text=True
w=120 .. 200                    other(slot2)_differs=True   Cronograma_in_text=True
```

Asserting a style over a node the renderer never drew measures the clip, not the paint. The arm now
drives 120 and **asserts its own precondition first** (the title is present), so if a later change
re-clips it the precondition reddens with a message saying so, instead of the style assertion failing
and reading as a paint defect. It is also a live instance of `B-55`: **a clipped hit is an
undeclared hit.**

## 4 · Mutation verdicts — per RESOLVED ARM, never the exit code

Baseline **33 arms resolved, 33 PASSED**, asserted before any verdict was believed. Harness negative
control: a planted failing test must be reported FAILED — it was.

| id | subject | verdict | arms reddened |
|---|---|---|---|
| `M1` | outline stops painting hits | **KILLED** | 5 |
| `M2` | radial stops painting hits | **KILLED** | 5 |
| `M3` | LaneRenderer paints a hit exactly like a non-hit | **KILLED** | 5 |
| `M4` | RailTimeline paints a TRUNK hit like a non-hit | **KILLED** | 1 (§3.3's arm) |
| `M5` | RailTimeline paints a NON-TRUNK hit like a non-hit | **KILLED** | 3 |
| `M6` | HybridLane paints a hit like a non-hit | **KILLED** | 5 |
| `M7` | outline paints EVERY node when any hit exists | **KILLED** | 1 (§3.2) |
| `M8` | radial paints EVERY node when any hit exists | **KILLED** | 1 (§3.2) |
| `M9` | outline uses a different hit style from the other five | **KILLED** | 1 (§2.1) |

**9 fired, 9 KILLED, 0 SURVIVED, 0 BAD.** Every restore asserted byte-identical by sha256 before the
next mutant fired; all three source files verified against their pre-battery pins afterwards, and the
full suite ran green immediately after (`C-46`: the restore hash is not the proof, the green suite
is). Mutations are described by position and operation and are **not** pasted verbatim (`C-56`).

## 5 · Instrument RED-proof (`C-57`)

Three instruments, and **all three reported a falsehood before they reported anything true**:

1. **The pre-gate probe** raised `TypeError` on all six renderers — it drove a `ViewState` field that
   does not exist (§1.1). Corrected before any verdict was read.
2. **The battery's arm parser resolved ZERO arms** on its first run: `-v` and `-q` cancel, pytest fell
   back to dot-progress, and the per-arm lines never printed. The **arm-count assertion caught it** —
   without it the all-green check would have compared `0 == 0`, which is the third instance of that
   exact shape in this batch. The assertion is kept now that it has fired.
   A second defect in the same parser: the node-id pattern assumed `/` and Windows pytest prints `\`.
3. **The ruff comparator** (carried from the Inc-4c relay) asserts `parsed == declared` on both sides
   before comparing, and carries a positive control that must report a planted entry as NEW.

**Emitted-form assertion (`C-42`).** The observable is read from the producer's own structured
output — `Text.spans`, the renderer's emitted style objects — and never from a substring search over
the rendered string. `str(span.style)` is used so the comparison is over the emitted style value
rather than over object identity. The `text_differs=False` arm exists precisely to pin that the
picture carries no character-level encoding of a hit.

## 6 · `B-55` — measured, and NOT closed here

The `B-55` limb is real and it is **routed onward with evidence rather than folded in silently**.
Closing it means giving `outline` and `radial` a `painted_ids`, and:

- `app.py:1588` gates on `if self._current_renderer() is not self.renderer: return None`, and
  `app.py:52` imports `painted_ids` **by name** from `views.layered`. Routing per renderer means
  editing `app.py` — a **4th source file**, past the sealed 3-file cut.
- It changes the shipped `HLR-N06.3` hidden-count declaration in two views that currently declare
  nothing — a **gated behaviour change**, not a presentational one, which would also revoke this
  increment's `A-91` lighter lane.
- `test_a98_exactly_one_renderer_declares_its_painted_set` pins `== {mapper.views.layered}` as an
  EQUALITY, by design, so it reddens the moment a second renderer joins and forces this decision.
  It is behaving correctly and is left red-on-purpose-free by not touching it.

The participation census is **unchanged and still passing**; this increment adds fresh evidence to
`B-55` (§3.4: a clipped hit is an undeclared hit) without discharging it.

## 7 · `A-91` lighter lane — the executed justification

Both conditions are evaluated, not assumed:

| Condition | Verdict | Evidence |
|---|---|---|
| touches **no data path** | ✓ | the diff changes only `style=` arguments inside `render()`; no store, no file I/O, no schema field, no persistence, no network |
| introduces **no security sink** | ✓ | every style string is built from `darkside` palette constants; **no file-derived text enters a style**. Titles remain coerced by the pre-existing `darkside.plain` / `escape` calls, untouched |
| **no A3 contract change** | ✓ | no `render` signature moved; `test_a3_census` signature clause green |
| review returns **zero HIGH** | *pending* | any HIGH restores the full protocol for this increment |
| battery | ✓ | never skipped — 9/9, §4 |

## 8 · Reverse census (`B1`), swept before the gate

`grep -rl` per touched renderer class across the whole `tests/` tree:

| symbol | asserting test files |
|---|---|
| `OutlineRenderer` | `test_canvas`, `test_inc3_census`, `test_outline`, `test_repair_depth`, `test_repair_golden_census` |
| `RadialRenderer` | `test_canvas`, `test_export`, `test_inc3_census`, `test_radial`, `test_repair_depth`, `test_repair_golden_census` |
| the three lane renderers | `test_inc3_census`, `test_lane` |

`test_repair_golden_census` and `test_export` are the two style-sensitive observers (`C-24`: a
byte-identity golden, and SVG export which snapshots styles). **Neither drifted** — both lanes are
green, and the change is inert whenever `hits` is empty, which is every render those observers drive.

### 8.1 · Two census pins fired, and both were correct to fire

1. **`test_tc_a3_no_source_file_is_invisible_to_the_census`** failed the first full run: the new test
   file was **untracked**, and every census derives from `git ls-files`. This is the guard Inc-3 built
   for exactly this hole, working as designed. Fixed by tracking the file.
2. **`test_tc_a3_the_census_cardinalities_are_PINNED`** then failed: 59 arg-ful `render(...)` call
   sites against a pinned 58. Bumped to 59 **with an itemised reason**, per the convention the pin's
   own comment sets — and noted there that the count is **+1 and not +6**, because the arms
   parametrise over the derived set and share one helper, so it does not move when a seventh
   renderer joins.

**This pin has now caught a real drift in two consecutive increments**, which is the argument for
keeping it as an equality rather than softening it to a floor.

## 9 · Gate checklist

- [x] **Tests / type checks / lint pass** — `887 passed, 17 deselected, 3 xfailed` exit 0; `904 passed, 3 xfailed` all markers; ruff SET-identical to `9ba2f26`, 27 = 27, zero NEW / zero GONE. One complete run each, from a tree sha256-pinned before and after both lanes; one earlier run discarded because the tree moved under it (§8.1).
- [x] **Counterfactual executed** — 5 of 6 renderers RED pre-fix on the sealed threshold, §1.
- [x] **Every predicate demonstrated able to go RED** — 9 mutants, 9 KILLED, per-arm verdicts, §4.
- [x] **Derived input set, non-empty asserted before evaluation** (`C-31`) — §1, and the guard arm.
- [x] **Instrument RED-proof** (`C-57`) — three instruments, three reported falsehoods, §5.
- [x] **Emitted-form assertion** (`C-42`) — spans, not substrings, §5.
- [x] **Reverse census** (`B1`/`C-26`) — §8, including the two style-sensitive golden observers.
- [x] **Correction population** (`C-14`) — the `#D42` driver correction (§1.1) is recorded here only; the sealed document is NOT edited post-seal. The `HIT_STYLE` literal population is 6 sites, enumerated in §2.1. **This line was FALSE as written for three rounds: the style arm covered 5 of 6** -- it drives `branches[1]` and never reached `RailTimelineRenderer`'s trunk, so a drift there survived every arm. Measured and closed in round 4 (§13).
- [x] **No secrets in code or output** — the diff adds palette constants and style branches only.
- [x] **No destructive commands** — the battery mutates and restores under sha256; `rmdir` (not `rm -rf`) was used for the authorised debris removal, and it refuses non-empty directories by construction.
- [x] **Source file count within the sealed cut** — 3 of 3, cap is 4.
- [x] **Independent review** — returned **BLOCK, 1 HIGH**. Folded in §11. **The `A-91` lighter lane is REVOKED**; the full protocol is restored for this increment, including a confirmation pass on the post-fix tree.

> ⚠ **§§1-9 above are ROUND 1, and §11 is ROUND 2.** Where they differ, the LATEST section governs —
> §12 over §11 over §§1-9. Round-1 claims superseded outright, named rather than edited away:
> 1. the ledger — `887`/`904` → `898`/`915` (§11.8) → **`904`/`921`** (§12.4);
> 2. the checklist line *"every predicate demonstrated able to go RED"*, which §11.3 records as
>    **overstated** — and §12.1 shows was still overstated in round 2;
> 3. the BLUF's *"1 of 6 compliant to 6 of 6"* — the **operator-reachable** movement is
>    **1 of 3 → 3 of 3** (§11.6). Added here on the confirmation pass's nit, which was correct that
>    the round-2 supersession list named only two of the three.
>
> **Four more, added at round 4 because pass 3 audited this list and found it incomplete —
> the supersession list was itself a claim that named its members rather than enumerating them:**
> 4. the BLUF's `battery : 9 mutants, 9 KILLED` — a **second home** for the figure item 2 tracks;
>    the running total is `R1 9/9 · R2 7/7 · R3 18/18 · R4 35 fired / 32 KILLED / 3 equivalent`;
> 5. §3's *"33 arms … Six are the derived-set guards"* — arms are **50**, and there is **one**
>    derived-set guard arm; the "six" was wrong in round 1 as well;
> 6. §11.8's `arms : 44` — superseded to **50** by §12.4;
> 7. §7's `A-91` row *"review returns zero HIGH | pending"* — **not** pending: the lane is REVOKED.

## 11 · Round 2 — the independent review's fold

**The review returned `BLOCK — 1 HIGH`, and the HIGH was right.** It found no defect in shipped
behaviour; it found that the arms closing `AT-024` could not see the error class `AT-024` exists to
prevent.

### 11.1 · `F1` (HIGH) — the gate never drove a hit set with more than one member

The Statement is **plural** — *"shall paint the **nodes** carried in `state.hits`"*. All 33 of my
arms drove a hit set of size 0 or 1, so a renderer painting exactly ONE member and dropping the rest
satisfied the entire file. That is precisely the catalogued error class: *"reporting a count a view
does not paint"* (`01-requirements.md:2456-2458`). A count line declaring N over a canvas painting 1
**is** that defect, and my gate was blind to it.

This is `C-31` exactly: the arithmetic was sound, every code mutation I fired was killed, and the
oracle was still weak because **the INPUT SET was incomplete**. My round-1 battery could not have
found it — mutating the code never reveals a missing input.

**The reviewer executed it rather than arguing it:** three mutants reducing each renderer's paint to
the lowest-sorted hit member — outline, radial, rail-label — **all SURVIVED, 0 arms red**.

**Fix:** one parametrised arm, `..._EVERY_member_of_the_hit_set_is_painted`, driving a two-member hit
set and asserting the picture differs from the one-member picture. **No source file touched.**

**Re-fired on the amended tree, extended from the reviewer's three renderers to all five:**

| mutant | round 1 | round 2 |
|---|---|---|
| `F1-outline-only-min` | SURVIVED | **KILLED** (1 arm) |
| `F1-radial-only-min` | SURVIVED | **KILLED** (1 arm) |
| `F1-lane-only-min` | SURVIVED | **KILLED** (1 arm) |
| `F1-rail-only-min` | SURVIVED | **KILLED** (1 arm) |
| `F1-hybrid-only-min` | SURVIVED | **KILLED** (1 arm) |

Each is killed by exactly the arm added for it.

### 11.2 · `F2` (MEDIUM) — a dead conjunct, and a comment of mine that was FALSE

`radial.py`'s hit branch was guarded `... and j`, with a comment claiming it kept the leading pad cell
out of the highlight and that "the branch tint below owns that cell". **Both halves were false.** Cell
`j == 0` is `(x, y)`, and the marker `put` after the loop overwrites it unconditionally for every
node, hit or not. The reviewer proved it twice: the conjunct-drop mutant survived, and a direct output
probe over **225 configurations** returned byte-identical spans, same sha256 both sides.

It guarded nothing and diverged from `layered` — the renderer §2 claims to follow — for no reason.
**Fixed:** conjunct removed, false claim replaced with what was measured. A false explanatory comment
in shipped source is the same class as this batch's earlier fabricated measurement in production
source, and this one was mine.

### 11.3 · `F3` (MEDIUM) — precedence was unobserved by the whole repository

**No test anywhere set `selected_id` and `hits` together.** Five newly-authored branch orderings
shipped unobserved; two precedence-inverting mutants survived a **185-arm run across twelve test
files**. My round-1 checklist line *"every predicate demonstrated able to go RED — 9 mutants, 9
KILLED"* was **overstated**, and the review said so correctly: the battery fired nothing at the branch
ordering. **Fixed:** `..._selection_is_painted_ON_TOP_of_a_hit`, parametrised over all six. Both
precedence mutants now KILLED.

### 11.4 · `F4` (MEDIUM) — a skip where the docstring promised a red

The width precondition called `pytest.skip` while its own docstring and §3.4 both claimed it
*"reddens with a message that says so"*. It did not — the run stayed green, and the pinned ledger
carries no skip count, so a silent conversion would have surfaced nowhere. **Fixed:** it is an
`assert`. All six renderers draw the third branch at 120 columns today, so no green escape hatch is
held open.

### 11.5 · `F5` (MEDIUM) — a copy whose justification its own guard cancelled

`tracked` / `renderer_classes` were copied from `test_a3_census.py` and justified as independence. The
review showed that justification was **cancelled by the equality arm guarding it**: on a re-scope this
module would not keep working — the equality arm would redden. **Fixed:** the module imports the one
derivation; the copy and the now-meaningless equality arm are gone.

### 11.6 · `F6` (LOW) — a framing correction to my own BLUF

Three of the five changed renderers have **no production consumer**: `app.py` instantiates only
`LayeredRenderer`, `OutlineRenderer` and `RadialRenderer`; the three lane renderers are exported but
unreached. The Statement scopes to *"every view **the operator can reach**"*, so the
**operator-visible** movement is **1 of 3 → 3 of 3**, not the BLUF's 1 of 6 → 6 of 6. Deriving the
wider set stays correct — a renderer wired up later is covered for free — but the BLUF's number
measured the derived set, not the reachable one, and it also lowers the blast radius.

### 11.7 · `F7` (LOW) — carried, not fixed

A selected node that is also a hit is indistinguishable from a selected non-hit, in all five renderers
and in shipped `layered`. Already declared in §10; the review confirms it is sane and matches
`layered`. **Routed to `ux-reviewer` as a carry** — changing it here would be a silent, unrequested
UX change.

### 11.8 · Round-2 evidence, re-measured on the amended tree

```
default lane : 898 passed, 17 deselected, 3 xfailed   exit 0
all markers  : 915 passed, 3 xfailed                  exit 0
ruff SET     : 27 = 27 vs 9ba2f26, zero NEW, zero GONE
battery      : round 1  9 mutants / 9 KILLED
               round 2  7 mutants / 7 KILLED  (5x F1 shape, 2x F3 shape)
arms         : 44, zero skipped
```

**Ledger: `898 = 887 - 1 + 12`** — the agree-arm retired by `F5`, six plural arms and six precedence
arms added. All-markers moves by the same net `+11` (904 → 915). `898 + 17 = 915` holds independently.

**A ruff regression I introduced in the fold and caught before the gate:** removing the copied
derivation left `importlib` and `subprocess` unused, and the SET comparator reported **2 NEW `F401`**.
Fixed by dropping the imports; the SET is identical again. The comparator earned its keep — the raw
count alone (27 → 29) would have been easy to read past.

**The census pin did NOT move.** `F1` and `F3` both reuse `_spans_at`, and `selected_id` was folded
into it as a **defaulted parameter** rather than a second helper, so the arg-ful call-site count stays
59. Re-derived rather than assumed: `argful 59, zeroarg 26, defs 7`.

**Tree discipline.** Every mutant restored from original bytes and asserted byte-identical by sha256
before the next fired; `__pycache__` purged both sides; `PYTHONDONTWRITEBYTECODE=1`. The final lanes
ran from a tree pinned before and after; one earlier full run was **discarded, not explained**,
because the import cleanup moved the tree under it.

- [x] **Confirmation pass on the post-fix tree** — returned **BLOCK, 1 HIGH surviving** (`N1`). Folded in §12.

## 12 · Round 3 — the confirmation pass, and the pattern it named

**The confirmation pass returned `BLOCK — 1 HIGH surviving`, and its closing sentence matters more
than the defect it found:**

> *"the pattern this increment keeps producing is a correct fix to the exact mutant that was named,
> with the mirror of that mutant left standing."*

That is exactly right, it is the second instance in two rounds, and round 3 is written against the
**axis** rather than against the representative.

### 12.1 · `N1` (HIGH) — my `F1` fix was one-sided

The round-2 arm compared the two-member picture against `{"first"}` **alone**. A renderer dropping the
FIRST member and painting the last therefore passed: `both` paints `other`, `only_one` paints `first`,
the two differ, green. The reviewer executed the mirror shape — keep only the **highest**-sorted
member — and it **SURVIVED on seven of seven renderers**, and survived a 199-arm run across twelve
test files.

It survived on `layered` too — the renderer that was compliant *before* this increment — so the gap
was never about my new code. It was about the oracle.

**The fix is stated over the class.** The hit-styled spans of a two-member render must equal the
**UNION** of the hit-styled spans of the two single-member renders. That is decidable only because the
rendered TEXT is invariant under the hit set — which §3's own `text_differs` arm pins — so span
offsets are comparable across renders. It closes both directions at once: dropping either member loses
spans, painting anything extra gains them. The two inequalities are kept underneath as diagnostics, so
a failure names WHICH member was dropped.

### 12.2 · `N2` (MEDIUM) — this file's own lesson, recurring inside the fix for it

The round-2 precedence arm always selected `branches[1]`. `RailTimelineRenderer` routes `branches[0]`
through `main_style` — a separate statement this increment rewrote — so its inversion **survived all
44 arms** while the other five died. That is §3.3's trunk-versus-branch lesson happening again, one
arm later, inside the arm written to close the previous finding. The slot is now a **parameter**
(`trunk` / `branch`) rather than a fixed id.

### 12.3 · The round-3 battery — the AXIS, enumerated

18 mutants: drop-a-member in **both** directions across **all six** renderers (`layered` included,
though outside the diff, because the same arms cover it), plus **all six** precedence guard sites.

| family | fired | verdict |
|---|---|---|
| keep only the lowest-sorted member | 6 | **6 KILLED** |
| keep only the highest-sorted member | 6 | **6 KILLED** — the shape that survived round 2 |
| precedence inverted, per guard site | 6 | **6 KILLED**, the rail **trunk** among them |

**18 fired, 18 KILLED, 0 SURVIVED.** Each drop-a-member mutant reddens exactly the plural arm for its
own renderer; each inversion reddens exactly the precedence arm for its own renderer and slot.

**One mutant reported `BAD` and was re-fired rather than counted.** The radial inversion's multi-line
anchor matched zero times — a mutant that never applied has **no verdict**, and reading it as a
survivor would have been as wrong as reading it as a kill. Re-anchored on a plain string at a known
occurrence index (line endings cannot defeat that), it is **KILLED**, reddening both slots.

### 12.4 · Round-3 evidence

```
default lane : 904 passed, 17 deselected, 3 xfailed   exit 0
all markers  : 921 passed, 3 xfailed                  exit 0
ruff SET     : 27 = 27, zero NEW, zero GONE
battery      : R1 9/9 · R2 7/7 · R3 18/18 KILLED
arms         : 50, zero skipped
```

**Ledger: `904 = 898 + 6`** — the precedence arm parametrised over two slots (6 → 12 arms).
All-markers moves by the same +6 (915 → 921); `904 + 17 = 921` holds independently. The census pin did
**not** move: still `argful 59, zeroarg 26, defs 7`, because every new render goes through `_spans_at`.

`mapper/views/layered.py` was mutated by this battery and is **restored to HEAD exactly** —
`git diff HEAD -- mapper/views/layered.py` is empty and its sha256 matches its pre-battery pin. It is
**not** part of this increment's diff.

### 12.5 · Findings accepted without acting, each with its reason

- **`N3` (LOW)** — the fixture's ids make `branches[0]` permanently the lowest-sorted hit, so at the
  trunk the `min` shape is an *equivalent mutant*. Correct, and it is why one round-3 line reads
  KILLED-by-the-plural-arm rather than by the trunk arm. Left as a fixture note: an id ordering that
  decouples "is the trunk" from "is the lowest-sorted hit" would separate the two properties. No arm
  depends on the coupling.
- **The `F6` nit** — the round-1 BLUF's `1 of 6 → 6 of 6` is a third superseded claim; added to the
  `⚠` list above.
- **The reviewer's ruff methodology warning is CORRECT and supersedes my §11.8 note.** Comparing ruff
  across directories is invalid here: an export outside the repository resolves an ancestor
  configuration enabling `I001`/`I002` (70 findings against 27) — the same trap the Inc-4c relay hit
  from the other side. Every SET comparison in rounds 2 and 3 ran **inside** the repository with
  `--isolated` on both sides, which is why they reproduce.
- **The `F3` vacuity flank** — the precedence arm is an equality, so it also passes if the selection
  paint disappears entirely. Confirmed pre-existing (selection styling predates this increment and is
  outside the diff), recorded, **not** closed here.

- [x] **Second confirmation pass** — returned **BLOCK, 2 HIGH** (`P1`, `P2`) plus five more. Folded in §13.

## 13 · Round 4 — the third instance of one pattern, and the pattern is mine

Pass 3 returned `BLOCK — 2 HIGH` and named the mechanism rather than the defect:

> *"each round has generalised along the axis it was shown, and stopped there. Round 2 was shown a
> member (`min`) and generalised to the other member (`max`). Round 3 was shown a statement (the rail
> trunk) and generalised the precedence arm to slots — correctly — while leaving the plural arm
> quantified over two named members."*

**That is a true description of three consecutive rounds of my work.** Each fix was correct, executed,
and aimed at the instance in front of it. **An assertion that names its inputs is the defect; an
assertion quantified over an enumerated set is the fix** — and round 4 is written that way.

### 13.1 · `P1` (HIGH) — the named shape still survived, at a site my battery could not see

`SHAPE-MAX` still survived at `lane.py:291` (`RailTimelineRenderer`'s `label_style`), through all 50
arms **and the entire 904-arm default lane, exit 0**. Not an equivalent mutant: at that site a
two-member hit set loses a member (48 hit-styled spans → 20).

**Why it survived is the whole lesson.** The round-3 arm rendered exactly one plural hit set,
`{"first", "other"}` — and at that site `first` routes through the *separate* `main_style` statement,
so inside the branch loop the "two-member" set **degenerates to a singleton**, and `max` of a
singleton is that singleton. The arm's plurality was real at five sites and fictional at the sixth.

### 13.2 · `P2` (HIGH) — no hit set of size ≥ 3 existed anywhere in the repository

Two further shapes — paint only the two extremes (`MINMAX`), paint only the first two in sort order
(`SORTED2`) — **survived at all seven sites**, and across the full lane. A renderer correct on every
subset of size ≤ 2 and wrong at size ≥ 3 was invisible to the entire suite.

**The fix quantifies.** The arm now enumerates the fixture's hittable nodes and asserts, for **every**
subset of size 2 and 3, that the hit-styled spans equal the union of its members' single-member spans
— with a **non-vacuity guard** (`P5`) asserting each member paints something, because otherwise the
union degenerates to `X == ∅ ∪ X` and passes for free. That guard is exactly how `P3`'s drift hid.

### 13.3 · `P4` (MEDIUM) — my battery's denominator was wrong, and it masked the survivor

Round 3 fired per renderer **class**; there are **seven hit sites across six classes**, and
`RailTimelineRenderer` holds two. A per-class mutant is killed by whichever of its sites is observed
and says nothing about the others — pass 3 demonstrated it directly:

```
MAX at the rail TRUNK site only     KILLED
MAX at the rail LABEL site only     *** SURVIVED ***
MAX at BOTH rail sites (per-CLASS)  KILLED   <- reports a KILL over a live survivor
```

So §12.4's `battery R3 18 fired / 18 KILLED` was arithmetically true of the 18 fired and **misleading
as coverage**. This is `C-31` one level up from where §11.1 diagnosed it: the *mutant population* was
the incomplete set. **Round 4's battery is per SITE.**

### 13.4 · The round-4 battery — 7 sites × 5 shapes

| shape | fired | KILLED | equivalent |
|---|---|---|---|
| keep only the lowest-sorted member (`MIN`) | 7 | 6 | 1 |
| keep only the highest-sorted member (`MAX`) | 7 | **7** | 0 |
| keep only the two extremes (`MINMAX`) | 7 | 6 | 1 |
| keep only the first two sorted (`SORTED2`) | 7 | 6 | 1 |
| hit-style DRIFT per site (`P3`) | 7 | **7** | 0 |

**35 fired, 32 KILLED, 0 real survivors.** `P1`'s survivor (`MAX` at `lane.py:291`) is KILLED,
`P2`'s two shapes are KILLED everywhere they can act, and `P3`'s trunk drift is KILLED.

**The three residual survivors are PROVEN equivalent, not argued.** All three sit at the trunk site,
where the fixture's id ordering makes `first` permanently the lowest-sorted hit, so `min`, `{min,max}`
and `sorted[:2]` all contain it. Proof by output digest over **24 renders** (8 subsets × 3 widths),
with `MAX` as the **positive control that must differ** — without it the probe could report
equivalence because it is blind rather than because they are equal:

```
SHIPPED   b908d7b4175e8a8a...
MIN       b908d7b4175e8a8a...  EQUIVALENT
MINMAX    b908d7b4175e8a8a...  EQUIVALENT
SORTED2   b908d7b4175e8a8a...  EQUIVALENT
MAX       0ec8532bbaa5e866...  DIFFERS   <- positive control fires
```

That is `N3`, confirmed by my own instrument rather than inherited.

### 13.5 · Round-4 evidence

```
default lane : 904 passed, 17 deselected, 3 xfailed   exit 0
all markers  : 921 passed, 3 xfailed                  exit 0
ruff SET     : 27 = 27, zero NEW, zero GONE
battery      : R1 9/9 · R2 7/7 · R3 18/18 · R4 35 fired, 32 KILLED, 3 proven equivalent
arms         : 50, zero skipped
```

Arm count and ledger are **unchanged** from round 3 — the fix replaced an arm body and added no arm —
so `904 = 898 + 6` still holds and the census pin stays 59. `mapper/views/layered.py` was mutated
again by this battery and is restored to `HEAD` exactly.

### 13.6 · Corrections applied to THIS packet, because pass 3 audited it

- **§2 / §2.1** said *"five call sites"*. There are **six** — `RailTimelineRenderer` holds two, which
  §2's own table always showed. Corrected (`P7`).
- **§9's `C-14` line** claimed the six-site `HIT_STYLE` population was *"guarded observably"*.
  **It was false for three rounds: the style arm covered 5 of 6**, because it drives `branches[1]` and
  never reaches the trunk. Corrected in place, and closed by round 4's `DRIFT` family (`P3`).
- **Four further stale claims** are added to the `⚠` supersession list, which pass 3 correctly found
  incomplete: my round-3 list tracked the ledger but not the BLUF's battery figure, the arm count, or
  §3's *"33 arms / six derived-set guards"*.

### 13.7 · ⚠ SOFT CAP REACHED — surfaced, not worked around

**This increment has taken three BLOCK verdicts** (round 1 `F1`; round 2 `N1`; round 3 `P1`/`P2`).
The flow's soft cap is **3 blocks per increment → surface to the coordinator**, so this packet stops
here rather than dispatching a fourth review on my own authority.

**Root cause, stated plainly and not diluted:** every fix was aimed at the instance a reviewer named,
and the reviewers kept finding its neighbour. The defect was never in the shipped renderers — all four
rounds found **zero defects in shipped behaviour** — it was in the *form of my oracles*, three times
over. The correction is the one pass 3 stated, now applied: quantify over an enumerated set, and fire
the battery per site rather than per class.

- [x] **Third confirmation pass (pass 4)** — dispatched under coordinator ruling 2026-09-10, narrowly briefed to audit the FORM of the oracle. Returned **BLOCK, 1 HIGH (`Q1`, new)**. Recorded in §14. **NOT fixed here** — §14.3.

## 14 · Pass 4 — the deciding pass, and it found a fourth level

Pass 4 **discharged all seven of pass 3's findings**, each by measurement, and confirmed round 4's fix
along the axis it was aimed at: the cardinality quantification is exhaustive, the non-vacuity guard is
real and load-bearing, the 7-site denominator is right with no eighth site, the three equivalences are
honest — re-proven on a *larger* domain (16 subsets × 3 widths) with a positive control that fires —
the `layered` soundness caveat names the real mechanism, and **every §13.5 figure is TRUE**.

**And it found `Q1`: the same defect a fourth time, one level down.**

### 14.1 · `Q1` (HIGH) — the fix moved the naming from the assertion into the DOMAIN

Round 4 removed the hand-named inputs from the *assertion* and left them in the *set the assertion
quantifies over*: `HITTABLE = ("first", "hit", "other")`. A literal three-element tuple stands where
the fixture's **four** hittable nodes belong, and its stated justification — the lane renderers never
draw the root — is a property of **three** renderers applied to all six.

**Measured, not argued.** Single-node hit sets at w=120, hit-styled spans:

```
                          root  first   hit  other     draws the root?
  outline.OutlineRenderer    1      1     1      1     YES -- and paints it
  radial.RadialRenderer     13     11    18     10     YES -- and paints it
  layered.LayeredRenderer   20     20    20     20     YES -- and paints it
  lane.Lane / Rail / Hybrid  0      -     -      -     no  -- B-55 holds here
```

A drop-`root` mutant therefore **survives all 50 arms and the entire 904-arm default lane, exit 0**, at
`outline.py:130`, `radial.py:232` and `layered.py:528` — proven non-equivalent by output digest, while
the four lane sites are proven equivalent. **And the root is operator-reachable:**
`SearchIndex.hits("raiz") -> {'root'}`, passed straight into `ViewState.hits` at `app.py:2205`.

Those three are exactly the **operator-reachable** renderers (`F6`). `01-requirements.md:2753` is
plural with no root exclusion, and `:2456-2458` names *"reporting a count a view does not paint"* as
the error class this story exists to prevent — which is what a root-only search would do.

**The `B-55` route was also a mis-route, and that is the sharper half.** `B-55` is *a clipped hit is an
undeclared hit* — true of the lane family, where the root is never drawn. `outline`, `radial` and
`layered` **do** draw it and **do** paint it, so there was nothing for `B-55` to carry there. Filing
the exclusion under it put a live gap behind a closed door. Mine.

### 14.2 · The pattern, stated at the level it actually operates

Four rounds, four levels of one structure; each fix correct, each one axis short:

| round | naming removed from | naming left in |
|---|---|---|
| 2 | the mutant that was named (`min`) | the other member (`max`) |
| 3 | the assertion's members | the mutant population's **sites** (per-class firing) |
| 4 | the assertion's **cardinality** | the **domain** it quantifies over |
| — | *(the fix pass 4 hands over)* | derive the domain; assert the `B-55` boundary |

**Zero defects in shipped behaviour across all four rounds.** The renderers have been correct since
round 1 and are correct now — including on the root, which all three drawing renderers paint properly.
Every block has been about the oracle.

### 14.3 · STOPPED — not fixed, and deliberately

Pass 4 hands over an **executed** fix: baseline green at 50 resolved / 0 red, the three survivors go to
KILLED, all 35 prior verdicts unchanged, 42 fired / 35 KILLED / 7 proven equivalent. It is tests-only
and keeps `SOURCE FILE COUNT: 3`, the arm count at 50, and the census pin at 59. Its shape is: derive
the domain per renderer from what that renderer actually paints, then **assert** the `B-55` boundary
(a node the renderer DRAWS and the state declares a hit must be painted) instead of assuming it — the
boundary assertion being the load-bearing half, since a bare derivation would silently absorb the
defect.

**It is NOT applied here.** The coordinator ruling of 2026-09-10 authorised pass 4 on the explicit
condition that **anything new stops the increment and returns to the operator, and that a fifth round
is not authorized.** Applying a reviewer's fix and re-firing the battery would be round 5 under another
name. The fix is recorded; the decision is the operator's.

**One stale citation, corrected rather than left:** pass 3 recorded the module's only arg-ful census
site at `test_views_hits.py:79`; round 4's arm body moved it to **81**. The census asserts the *count*
(59), which is unchanged.

## 10 · Carries

- **`B-55` NOT closed** — routed with measured cost (§6): needs `app.py` as a 4th source file and a
  gated behaviour change. Recommend its own increment.
- **`LLR-N07.3.4` remains OPEN, blocked on `Inc-STRIPS`** (coordinator ruling 2026-09-10, recorded in
  `state.json.p3_progress.open_blocks`). Inc-5 does not touch it and does not close it.
- **A pre-existing collision, observed and deliberately NOT fixed:** in `layered`, the unfocused
  selection style is `INK on STEP` — **byte-identical to its hit style** — and the focused selection
  block overwrites a hit entirely. So a selected node that is also a hit is indistinguishable from a
  selected non-hit. This is shipped behaviour that predates the increment; the five renderers changed
  here inherit the same precedence deliberately (§2), because diverging from it would have been a
  silent, unrequested UX change. Worth a UX ruling.
- The `--help/.mapper` debris directory was removed under coordinator authorisation; `rmdir` proved
  both levels empty. Git never tracked it.

## 15 · Round 5 — `Q1` closed, under a terminal boundary

Coordinator ruling 2026-09-10 (option 1): apply pass 4's **executed** fix and re-fire narrowly, then
**one** final confirmation pass scoped strictly to `Q1`'s axis. The ruling names it plainly as a fifth
review and authorises it because *the situation changed* — pass 4 handed over a measured fix rather
than a hypothesis, and `Q1` is operator-reachable, so accepting it would have booked a known-blind
oracle on a live path. **Terminal boundary: anything outside `Q1`'s axis and Inc-5 splits instead.**

### 15.1 · The fix — derive the domain, and ASSERT the boundary

`HITTABLE` is gone. The arm now derives its domain per renderer from what that renderer actually
paints, and asserts the `B-55` boundary rather than assuming it:

```
ALL = ("root", "first", "hit", "other")
hittable = tuple(m for m in ALL if singles[m])      # derived, not named
assert len(hittable) >= 3                            # a FLOOR, not a filter
assert ("root" in hittable) == ("Raiz del mapa" in drawn)   # the B-55 boundary
for k in range(2, len(hittable) + 1): ...            # every subset, every cardinality
```

**The boundary assertion is the load-bearing half**, and this is the part worth keeping in mind: a
bare derivation would have *absorbed* the defect. Under a drop-`root` mutant, `singles["root"]` goes
empty, `root` falls out of `hittable`, and every union passes for free. The boundary arm makes the
renderer state both facts at once — it still draws the root, and it no longer paints it — so the arm
reddens. It reads the boundary off the **rendered text**, not off a list of class names, so it stays
true if a renderer changes family.

### 15.2 · The narrow re-fire — 7 sites × 6 shapes

| shape | fired | KILLED | equivalent |
|---|---|---|---|
| `MIN` / `MINMAX` / `SORTED2` | 21 | 18 | 3 (trunk) |
| `MAX` | 7 | 7 | 0 |
| `DRIFT` | 7 | 7 | 0 |
| **`NOROOT`** (new) | 7 | **3** | 4 (lane family) |

**42 fired, 35 KILLED, 7 survivors — reproducing pass 4's pre-verified 42/35/7 exactly.**
`NOROOT` is now KILLED at `outline.py:130`, `radial.py:232` and `layered.py:528` — the three sites
where it survived every arm and the whole 904-arm lane. All 35 prior verdicts are unchanged.

**All seven survivors proven equivalent, each with a positive control that fired** — output digest
over the FULL node set, 16 subsets × 3 widths = **48 renders per site**:

```
lane.py:228 Rail-TRUNK   MIN / MINMAX / SORTED2   EQUIVALENT
lane.py:133 Lane         NOROOT                   EQUIVALENT
lane.py:228 Rail-TRUNK   NOROOT                   EQUIVALENT
lane.py:291 Rail-label   NOROOT                   EQUIVALENT
lane.py:354 Hybrid       NOROOT                   EQUIVALENT
lane.py:{133,228,291,354}  MAX(control)           DIFFERS  <- all four controls fire
```

The four `NOROOT` equivalences are `B-55` holding exactly where it is true: those renderers iterate
branches and never draw the root, so excluding it changes nothing there. That is now **measured per
site** rather than asserted per family — which is the mis-route lesson applied to itself.

### 15.3 · Round-5 evidence

```
default lane : 904 passed, 17 deselected, 3 xfailed   exit 0
all markers  : 921 passed, 3 xfailed                  exit 0
ruff SET     : 27 = 27, zero NEW, zero GONE
battery      : R1 9/9 · R2 7/7 · R3 18/18 · R4 35/32 · R5 42 fired, 35 KILLED, 7 proven equivalent
arms         : 50, zero skipped
```

Arm count, ledger and census pin all **unchanged** — the fix replaced an arm body and added no arm, so
`904 = 898 + 6` holds and the pin stays 59.

### 15.4 · The two controls this increment earned, recorded for `engineering-rules.md`

Both are in `state.json.p3_progress.controls_for_engineering_rules` alongside the per-site battery
control, ids marked pending because `docs/engineering-rules.md` does not exist until phase 6.

1. **An oracle's blind spots migrate outward one quantifier at a time — review the DOMAIN, not just
   the assertion.** The ladder, one rung per round, every fix correct and every one a rung short:
   the assertion's inputs (`min` → `max` survived 7/7) → the battery's population (per-class firing
   reported a KILL over a live survivor) → the assertion's cardinality (no hit set of size ≥ 3 existed
   anywhere) → the domain quantified over (a hand-named tuple; drop-`root` survived 3 of 7 sites and
   the whole lane). **Zero defects in shipped behaviour in any round.**
2. **A gap routed to the wrong owner is a gap behind a closed door.** Citing `B-55` for the root
   exclusion made a live gap look like an accepted carry — already known, already owned, so nobody
   re-examined whether it covered the case filed under it. It covered the lane family and not the
   three operator-reachable renderers. Check a carry's scope per member of the affected population,
   not per family, and where the justification is a property of the artifact, assert it from the
   artifact.

- [ ] **Final confirmation pass** — scoped strictly to `Q1`'s axis. DISPATCHED under the terminal
      boundary: anything outside that axis and Inc-5 splits rather than iterating again.

## 16 · Final pass — `Q1` CLOSED, and the split

**Verdict: PASS, 0 HIGH on `Q1`'s axis.** The fifth independent pass confirmed the round-5 fix by the
mechanism §15.1 claims, and confirmed it the hard way rather than by reading it.

### 16.1 · What the pass proved, that I had only asserted

- **The domain is genuinely derived** — no literal member list survives inside the quantifier;
  `hittable` reproduces the measured paint on all six renderers at 80/100/120.
- **The boundary assertion is the SOLE catcher of drop-`root`, proven by DEFEATING it.** The reviewer
  rewrote the boundary predicate into a tautology and re-fired: all three `NOROOT` KILLs **reverted to
  SURVIVED**. Pass 4's absorption warning is therefore a measured property of this tree, not a
  cautionary sentence in a docstring — and the load-bearing half is load-bearing in fact.
- **The `B-55` proxy is sound against truncation**, which is the failure mode a literal invites: the
  longest-prefix probe returns **13/13** for the three renderers that draw the root and **0/13** for
  the lane family, at every width. The lane family's `False` is not a clipping artefact.
- **42 fired / 35 KILLED / 7 equivalent reproduces survivor-for-survivor**, with all seven
  equivalences re-proven over **864 renders** per digest against four positive controls that fire.
- **Three EXTRA flat drop-shapes** (`NOFIRST`/`NOHIT`/`NOOTHER`) fired per site: 21 fired, 18 KILLED,
  3 proven equivalent. **Zero flat drop-a-member survivors anywhere in the tree.**
- Every §15.3 figure re-executed and **TRUE**.

**Fifth round running with zero defects in shipped behaviour.** The renderers have been correct since
round 1.

### 16.2 · `W1` — outside the axis, so it SPLITS rather than iterating

The pass found one thing outside `Q1`'s axis, at the next quantifier out: **the width at which the
domain is measured.**

The arm derives `singles` at **w=120**. The `B-55` boundary re-externalises that derivation for
**`root` alone**. The other three members are backstopped by sibling arms — and those run at **w=80**:

| member | pinned outside the absorbing arm by | width |
|---|---|---|
| `root` | the `B-55` boundary | 120 |
| `other` | `..._a_hit_outside_the_first_branch_is_painted_too` | 120 |
| `first` | `..._a_hit_on_the_FIRST_branch...` / `..._keyed_on_WHICH...` | **80** |
| `hit` | the sealed threshold / `..._keyed_on_WHICH...` | **80** |

So a drop of `first` or `hit` that bites only at w ≥ 100 falls out of `hittable`, leaves the floor
satisfied at 3, never touches the boundary (which speaks only of `root`), and the unions then quantify
over a domain the defect has already emptied. **Executed at `radial.py:232`** — the one site whose
enclosing closure has the width in scope — both shapes **survive all 50 arms and the entire 904-arm
default lane, exit 0**, and both are **proven non-equivalent** by digest. `other` and `root` at the
same site are KILLED, because those two are the only members with a w=120 observation outside the
absorbing arm. The kill/survive split maps one-to-one onto the table above.

**It is genuinely a different quantifier, not `Q1` restated:** no flat shape reaches it, and `Q1`'s
axis is closed against every flat drop across all four members and all seven sites.

**Per the coordinator's terminal boundary, `W1` is NOT fixed here.** Inc-5 closes with the renderer
changes — which five independent rounds confirm correct — and `W1` becomes a recorded tests-only
micro-increment, `Inc-W1`, slotted in the cut. Its charter is in §16.3, with the fix pre-verified by
the pass that found it.

### 16.3 · `Inc-W1` charter (tests only)

Generalise the `B-55` boundary from one member to **all four**, so every member the derivation can
drop is re-externalised against what the renderer actually draws:

```
for _m in ALL:
    assert (_m in hittable) == (TITLES[_m] in drawn)
```

then re-fire the drop-a-member family **width-conditioned as well as flat**, per site.
No source file; arm count stays 50; census pin stays 59.

**Pre-verified by the final pass:** precondition **24/24** on the shipped tree (4 members × 6
renderers, zero mismatches), baseline green at 50 resolved / 0 red, both `W1` survivors → **KILLED**,
and `Q1`'s kill preserved. It also subsumes the floor asymmetry §2 noted — a four-member renderer that
drops one member no longer slips past on `len(hittable) == 3`.

**One open design call, deliberately left to the implementer:** `TITLES` is a second spelling of the
fixture's titles. Deriving it from `_graph()` instead is a design decision, not a correctness one —
and given this increment's history, a second hand-maintained map is exactly the shape worth a second
look before it lands.

### 16.4 · The ladder gains a fifth rung

`§15.4`'s control is amended in `state.json`: the blind spot migrated outward once more, from the
**domain** to the **width at which the domain is measured** — assertion inputs → battery sites →
cardinality → domain → **the conditions under which the domain is derived**. Five rounds, five rungs,
every fix correct and every one a rung short, and not one defect in the shipped code.

- [x] **Final confirmation pass** — **PASS**, 0 HIGH on `Q1`'s axis; `W1` recorded outside it and split.
