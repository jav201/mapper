# Code Review — Inc-B55a · `45663b6` and predecessors against `3122519`

**Reviewer:** independent code-review lane, 2026-09-10.
**Tree:** `0b2fc1b`, clean on entry and byte-identical on exit (`app.py`
`fc060a30…`, `outline.py` `88a5d987…`, `layered.py` `3e081a6c…`,
`test_overflow.py` `5af28595…`). No evidence of another writer.
**Baseline:** `954 passed, 19 deselected, 3 xfailed` before and after.

## VERDICT: **BLOCK**

Two HIGH findings. `F1` is the blocker: **the increment's core defect fix can be
deleted and the entire suite stays green.** `F2` is an evidence finding, not a
regression — the product improved — but the acceptance is stated as satisfied
while the shipped behaviour fails its own clauses at sizes inside this
increment's own driven table.

Everything I measured about the *implementation* held up. The
`_rows` move is faithful, the bless documentation is exact to the character, the
`_fit` cost reasoning is right, and the `A-98` tripwire was honoured properly.
What did not hold up is a test, a claim about a test, and an arm that was
ratified and never written.

## Scope

| reviewed | not reviewed |
|---|---|
| `mapper/app.py`, `mapper/views/outline.py` in full at `0b2fc1b` | security (routed to `security-reviewer`) |
| `tests/test_overflow.py` (+506), `test_inc3_census.py`, `test_a3_census.py`, `test_repair_depth.py` diffs | register / wording of the Spanish string (routed to `ux-reviewer`) |
| `git show 57fb403:mapper/views/outline.py` line-by-line against `_rows` | `9a773e4` (Inc-CRUMB), already reviewed; excluded from the diff base |
| 12 source mutants fired and restored | `mapper/views/radial.py`, `lane.py` |
| 201,000 synthetic shapes through `_fit_declared` | whether `S-15`'s wall-clock numbers reproduce on another machine |

**Could not determine:** whether `_fit`'s wrap width `w` (from
`_canvas_width()`, floored at 20) can ever diverge from the widget's real
content width. I swept 16 terminal sizes down to `14x12` on both fixtures and
`PHYS-3` held at every one, so it does not manifest — but I did not prove it
cannot.

---

## Findings

### F1 — The settle-arming fix has no regression coverage at all  ·  **HIGH**

**Where:** `mapper/app.py:2532-2533`; arms at `tests/test_overflow.py:1377-1430`.

**What I fired.** `M0` deleted the two lines that are the entire content of
`7a973df` — `self._declared_for = None` and
`self.call_after_refresh(self._declare_after_layout)` — reverting the
increment's headline defect fix. Confirmed live at `app.py:2532`
(`pass  # MUTANT M0`). Result:

```
954 passed, 19 deselected, 3 xfailed in 231.73s
```

**Not one arm reddens.** All 11 `P1` arms pass, including the four loss sizes.

**Why.** I instrumented `_declare_after_layout`'s guard and drove outline at
every loss size and control:

```
@@ (24,20) settle_passes=2  (w,h)=(24,5) _rendered_for=(24,5) region_moved=False  held=3 exp=3
@@ (30,16) settle_passes=2  (w,h)=(30,3) _rendered_for=(30,3) region_moved=False  held=1 exp=1
@@ (32,16) settle_passes=2  (w,h)=(32,3) _rendered_for=(32,3) region_moved=False  held=1 exp=1
@@ (34,14) settle_passes=2  (w,h)=(34,1) _rendered_for=(34,1) region_moved=False  held=1 exp=1
```

The region never moves after `refresh_canvas` paints, so the settle pass never
re-renders, so arming it changes nothing observable. This is exactly `02o`'s
finding — closing `B-55` closes the trigger — and the arm's own header comment
(`test_overflow.py:1358-1364`) states it.

**The reasoning that produced the arm is half right.** `P1` as a *form* does not
depend on the trigger: it compares what the widget holds against what the
current geometry produces, and that is the correct invariant. But an invariant
that is true for an unrelated reason has no discriminating power. With the
trigger gone, `held == expected` whether or not the settle is armed. `P1` is a
true statement and a vacuous arm.

**Why it matters.** §3 discharges the shared-path risk of touching every view's
layout path with three evidence obligations. Obligation 2 — "`held == resettled`
asserted directly at all eleven sizes" — is this arm. It is the only thing
standing behind 23 lines of shared-path code plus new mutable state
`_rendered_for`, and it cannot fail. Anyone who later deletes the arming, or
breaks `_rendered_for`, ships it green.

I also fired the two guard mutants directly, and both survive for the same
reason: `M2` (`if self._rendered_for is None:` — the settle can re-render at most
once, ever) and `M1` (`_rendered_for` re-stamped after the strip update) are
each **11/11 green**.

**Smallest fix — verified, do not guess at this one.** Adding sizes does not
work: I tried extending `P1_CASES` with `((35,14),2) ((40,16),2) ((50,16),2)
((60,20),2) ((80,24),2) ((118,34),2) ((28,14),2)` and got `18 passed` both
pristine and under `M0`. The arm has to **force the trigger**, and the honest
way to force it is to restore the pre-`B-55` strip shape — a one-row strip:

```python
# Outline's strip is TWO rows since Inc-B55a (it carries the declaration).
# Shrink it to ONE -- the pre-B-55 shape -- and repaint: refresh_canvas paints
# the canvas FIRST and updates the strip LAST, so #map-body gains a row AFTER
# the canvas was painted. Only the settle pass can reconcile that frame.
screen._pagination_text = lambda: darkside.Text("z")
screen.refresh_canvas()
await pilot.pause()
# ...then P1's existing equality, unchanged.
```

Measured at the four loss sizes:

```
PRISTINE : (30,16) held=2 exp=2 OK   (32,16) 2/2 OK   (24,20) 4/4 OK   (34,14) 1/1 OK
M0       : (30,16) held=1 exp=2 RED  (32,16) 1/2 RED  (24,20) 3/4 RED  (34,14) RED
```

Red on all four with the fix reverted, green with it in place, and the gap it
reports is exactly the one-row gap §6 `C2` recorded (`3→4`, `1→2`). This is not
an artificial fixture: the substituted strip *is* the pre-fix strip.

---

### F2 — Outline hides every node and declares nothing on the canvas, at eight reachable sizes that the acceptance does not drive  ·  **HIGH** (evidence, not regression)

**Where:** the empty-frame floor, `mapper/views/outline.py:271-272`;
`AT056_SIZES` `tests/test_overflow.py:1448`; `AT057_SIZES` `:1559`.

**What I measured** on the shipped tree, applying `AT-056`'s own assertions
across a wider grid:

```
FAIL legacy  (34,14)  declared=8/8  canvas_token=False
FAIL legacy  (33,14)  declared=8/8  canvas_token=False
FAIL legacy  (28,14)  declared=8/8  canvas_token=False
FAIL legacy  (20,16)  declared=8/8  canvas_token=False
FAIL legacy  (16,14)  declared=8/8  canvas_token=False
FAIL legacy  (14,12)  declared=8/8  canvas_token=False
FAIL anidado (28,14) (33,14) (16,14) (20,16) (14,12)  declared=7/7  canvas_token=False
```

At these sizes `AT-056`'s new `PHYS-4` conditional (`if len(declared) == total:
assert OVERFLOW_TOKEN in canvas`) is RED, and `AT-057`'s `AGREE-1` is RED. None
of them appear in `AT056_SIZES` or `AT057_SIZES` — although `(34,14)` and
`(28,14)` are both rows of §6 `C2`'s eleven-size driven table, and `(34,14)` is
driven by `P1`.

**This is not a regression.** Pre-increment both surfaces were silent; now the
strip declares and the canvas does not. Strictly better. And the behaviour is a
defensible trade — `outline.py:264-270` argues it honestly, and the alternative
(an empty canvas) is worse.

**What is wrong is the record.** §4 states `AT-056` and `AT-057` as ratified
clauses; §7's checklist has no carry for the frames where they do not hold. The
docstring names `(34,14)` by measurement, so the shape was known during
implementation. An operator at a 34-column terminal reads a canvas that, under
`LLR-N06.3.3`, asserts the map is fully shown while eight of eight nodes are
hidden. That claim being *half* fixed is worth a line in the record; today there
is none.

**Smallest fix — pick one:**

- *(minimal, in scope)* Add `(34,14)` to `AT056_SIZES` with the ratified shape
  asserted rather than assumed — `declared == total and OVERFLOW_TOKEN not in
  canvas and OVERFLOW_TOKEN in strip` — so the accepted fallback is pinned and a
  future change to the floor reddens instead of sliding. Plus a `B-` carry.
- *(product fix, `Inc-B55b`)* When the full declaration does not fit, fall back
  to the bare token instead of to silence — `◆ mapper · outline ▽` is 20 cells
  and fits at `(34,14)` where the full sentence needs two rows. Note this breaks
  `AGREE-2`'s parse (`_declared_total` returns `None` with no numeral), so the
  arm needs the numeral clause guarded on the numeral being present.

---

### F3 — `PHYS-4`'s change is a trade, not a strengthening; control 13 does not cover it  ·  **MEDIUM**

**Where:** `tests/test_overflow.py:1515-1532`.

**The claim tested.** The comment says the conditional "is a STRENGTHENING and
so needs no independent pass (control 13)". It is not. The change **removed**
`declared < total` and **added** `declared == total → token on canvas`. The
removed clause caught a defect the added one does not.

**Demonstrated by construction.** `M9` mutates `_fit`'s budget test
`if used + cost > h:` → `>=`, a one-row over-cut. At `anidado (32,16)` — a size
`AT-056` actually drives:

| | pristine | under `M9` |
|---|---|---|
| `declared / total` | `6 / 7` | `7 / 7` |
| canvas token | present | present |
| old bound `declared < total` | GREEN | **RED** |
| new conditional | GREEN | GREEN |

A perfect discriminator, given up. `AT-056` caught `M9` at **none** of its ten
parametrizations. The suite still caught it — `AT-057`'s `AGREE-1` at `(35,14)`
and `P1` at `(34,14)` — so nothing ships broken today. But the specific
justification used to skip an independent pass is false.

Note `PHYS-3` (`declared == frame_hidden`) also passes under `M9`, and cannot
help: the declaration and the frame move together under an over-cut, so the
equality is self-consistent. The clause that *would* catch it is `PHYS-1` —
which is `F4`.

**Smallest fix:** amend the comment to state the trade honestly, and route the
lost coverage to `PHYS-1` (`F4`) rather than leaving it implied.

---

### F4 — The ratified `PHYS-1` / `PHYS-2` pilot arm does not exist on disk  ·  **MEDIUM**

**Where:** increment record §4, row "pinned pilot"; nothing in `tests/`.

`grep` over `tests/` for `PHYS-1`, `PHYS-2`, `maximal`, `lines[:0]`, "cannot
show" returns only two *comments* inside `AT-056`. No arm asserts "nothing
emitted the canvas cannot show" or "the cut is maximal".

The record names this exact failure at line 146: *"this batch already carries
`AT-005`/`AT-006` with no node on disk and therefore no way to verify them."*
§7's checklist does not list the pilot arm either, so it would close unnoticed.

It is also the arm that would restore `F3`'s lost coverage: an over-cut emits
fewer physical rows than the region holds, an under-cut more.

**Smallest fix:** write the arm, or strike the row from §4 with a recorded
reason. Not both silently.

---

### F5 — `_fit_declared`'s third pass, and the degradation its docstring describes, are unreachable  ·  **LOW**

**Where:** `mapper/views/outline.py:239-278`.

**What I fired.** You called this boundary untested and asked me not to accept
it. I ran the real `_fit` over **141,000 systematic** shapes (`w` 10–59, `h`
1–11, title lengths 1–40, 1–13 nodes) and **60,000 randomized** ones (widths
8–90, heights 1–30, up to 400 nodes, five header shapes, ragged indents and
title lengths), instrumenting the loop's `hidden` sequence and exit:

```
{'fixed': 56888, 'max_passes': 2, 'floor': 1186, 'zero': 1926}   EXHAUSTED: 0
```

**Zero non-convergence, and no shape ever needed more than two passes.** The
`return kept` after the `for` — the branch the docstring describes as "a
pathological frame degrades to a slightly stale numeral rather than looping" —
was never reached. The mechanism is monotonicity: appending the token strictly
lengthens the header, so the fit shrinks monotonically and `hidden` is
non-decreasing; the only thing that can change between pass 1 and pass 2 is the
numeral's digit count, and a second digit-boundary crossing was not reachable.

**The loop itself is load-bearing, and that is confirmed.** `M5` (`range(3)` →
`range(1)`) reddens `AT-057` at `(30,16)` with *"canvas says 7, strip says 8"*.
So your "the loop is not decoration" holds, measured. It is the *third* pass and
the exhaustion contract that are unreachable.

**And `AGREE-3` would probably not catch it if it ever were reached.** In the
exhaustion case the canvas paints `hidden_{n-1}` while `painted_ids` — and
therefore the strip — reports `hidden_n`. That is an `AGREE-2` failure, and
`AGREE-2` is driven at three sizes on one fixture. I confirmed the analogous
shape empirically on the *floor* path: in all 2,507 floor cases in my systematic
sweep, the canvas carries no numeral while the strip declares a nonzero one —
canvas/strip disagreement, 2507/2507.

**Smallest fix:** no code change. Soften the docstring to what is measured —
"bounded at three passes; no measured shape needs more than two" — and drop the
assertion about a degradation nobody has reached. Under this batch's own rule
that docstrings are claims, an unreachable branch described as a behaviour is a
claim without evidence.

---

### F6 — `AT-058` names three renderers instead of deriving them  ·  **LOW**

**Where:** `tests/test_overflow.py:1242-1245`.

**Your seam question, answered.** The catch is at the right place and I verified
it: `_unpainted_ids` has exactly **one** production call site
(`_pagination_text`, `app.py:2219`) — every other reference is a test — so
catching `LookupError` there is the narrowest placement that keeps `TC-R08`'s
survival property. Correct as built.

**Reachability:** `app.py` constructs only `LayeredRenderer`, `OutlineRenderer`
and `RadialRenderer`, all three registered, so `LookupError` cannot be raised by
production code today and `"declaración no disponible"` is dead in the shipped
app. That is fine — and the backstop is real:
`test_a89_the_reached_set_is_pinned_so_wiring_lane_up_pulls_it_in`
(`test_inc3_census.py:228`) pins `reached_renderers()` as an **equality** over
those three, so wiring a fourth renderer reddens an arm and that increment
inherits the registration obligation. The `AT-058` docstring's claim about this
is accurate — verified, not taken on trust.

**The residual.** `AT-058` hardcodes the three rather than deriving from that
pinned set. If a fourth renderer is wired and `A-89`'s pin is updated without
`AT-058` being updated too, the missing entry ships as a user-visible Spanish
string rather than failing a test. Two pins that must move together, only one of
which is derived.

**Smallest fix:** in `test_at058_an_unregistered_renderer_raises_…`, assert that
the set of renderers the screen builds resolves through `_painted_ids_for`
without raising, derived from the same census `A-89` pins, instead of listing
three identities. Keep the three identity assertions — they catch wiring a view
to the *wrong* view's `painted_ids`, which a derived check cannot.

---

### F7 — Design answer: the token has one home, the *sentence* has three  ·  **LOW**

**Your question 3, answered directly: the call is right, the home is wrong, and
you solved the smaller half of the problem.**

The reasoning for importing `OVERFLOW_TOKEN` is sound — one token, one home, and
`_declared_total` parses that exact shape, so divergence gives one
operator-facing numeral two grammars (`02m` §7.3). Keep the sharing. But the
*edge* `outline → layered` is backwards for a shared vocabulary item: neither
view owns it, and `radial` at `Inc-B55b` will import from `layered` too, making
`layered` a constants module by accident rather than by decision.

**And the token was the easy half.** What `_declared_total` actually parses is
the sentence, and the sentence is duplicated verbatim:

- `layered.py:395` — `f"  {OVERFLOW_TOKEN} {unpainted} fuera de vista"`
- `outline.py:243` — `f"  {OVERFLOW_TOKEN} {hidden} fuera de vista"`
- `app.py:2224` — `f"{OVERFLOW_TOKEN} {len(hidden)} fuera de vista "` *(leading
  space dropped, trailing space added)*

Three spellings of one grammar, none pinned against the others. Sharing the
token does not prevent the failure `02m` §7.3 names; sharing the sentence would.

**On `MAX_RENDER_NODES`: the inconsistency does not matter, and the reason is
the interesting part.** It is triplicated across `layered`, `outline` and
`radial`, and all three comments claim "a test keeps the three values in step".
**That claim is TRUE** — `tests/test_repair_depth.py:831` derives
`module.MAX_RENDER_NODES` per module and pins them as an equality. A duplicated
constant *with a pin* is a different object from a duplicated sentence *without*
one. So the two choices are not inconsistent in the way that matters; what is
inconsistent is that the higher-risk duplicate (the sentence, which an operator
reads and a regex parses) is the unpinned one.

**Smallest fix — `Inc-B55b`, not this cut** (it is a 3-file change): one
`declaration_text(n) -> str` beside the token in a module both views already
depend on (`views/state.py` plays that role, or a new `views/declaration.py`),
with `app.py` calling it too. Then `_declared_total`'s regex has exactly one
producer. If that is deferred, the minimum today is a pin asserting the three
spellings agree.

---

### F8 — Two prose claims spot-checked; one is off by one  ·  **LOW**

You asked me to check at least two measured claims. I checked four.

1. **§6.6: "a second regime was added at 11999 nodes — the largest graph
   `outline` will actually render".** The bound is `len(graph.nodes) >
   MAX_RENDER_NODES` (`outline.py:74`), so **12000 renders**, and the repo's own
   `test_tc_r14_a_map_at_the_bound_still_draws` asserts it. The largest is 12000,
   not 11999. Harmless to the measurement — 11999 is inside the rendering regime
   — but the superlative is wrong.
2. **§6.5's structural claim** that `_declare_after_layout` repaints only the
   canvas and the strip while `refresh_canvas` also rebuilds the minimap, rail,
   inspector and tab strip — **verified** against `app.py`.
3. **The `(140,8)` bless comment** — verified exactly, see below.
4. **§6.6's cost attribution** — independently corroborated, see below.

---

## Verified — stated because you asked for a check, not for reassurance

**The `_rows` move is faithful.** I diffed `git show
57fb403:mapper/views/outline.py`'s `render` body against the new `_rows` clause
by clause: same `subtree_counts` memoisation, same `visiting` cycle guard and its
`ValueError`, same `own` "sin acta" predicate, same reversed-children LIFO
producing pre-order, same selection-painted-over-hit precedence, same `meta`
fallback, same `B-47`/`A-89` coercion site. The only changes are structural —
`list[Text]` → `list[tuple[str | None, Text]]`, the two early returns becoming
`(rows, short_circuit)` pairs, and the degraded branch returning `[]` for rows so
`painted_ids` answers `frozenset()`. No transcription slip. Independently
corroborated: three of four `OutlineRenderer` golden digests are byte-identical
across the increment.

**The re-blessed digest's documentation is exact to the character.** I rendered
`legacy` through both the pre-increment and current `OutlineRenderer` at all four
golden sizes:

```
(140,45) rows 9→9  differing_rows=[]   fp_matches_pin=True
(80,24)  rows 9→9  differing_rows=[]   fp_matches_pin=True
(140,8)  rows 8→8  differing_rows=[0]  fp_matches_pin=True
    old: '◆ mapper · outline'
    new: '◆ mapper · outline  ▽ 1 fuera de vista'
    prefix=True  suffix='  ▽ 1 fuera de vista'
(300,120) rows 9→9 differing_rows=[]   fp_matches_pin=True
```

Every clause of the bless comment holds — one key, one row, row count unchanged,
old row 0 a prefix of the new, suffix exactly as stated, three keys predicted
green and byte-identical. Given §6.6's own record of a bless computed by the
wrong method, this one was computed right.

**`_fit`'s budget stop is correct and the per-call `Console` is not a hot-path
concern.** The loop measures at most `kept + 1` lines and `kept ≤ h`, so the
`12002`-node bound is never walked — as claimed. Measured cost:
`Console(width=…, no_color=True)` is **14.5 µs**; `render_lines` of one line is
**30 µs**. `_fit` runs at most 3× per `_fit_declared` × 2 call sites (`render`
and `painted_ids`) = **6 constructions = 87 µs per frame**, against `_rows`
walks costing ~150 ms on the largest graph outline renders. The constructor is
0.06% of the measured cost. **Do not cache it** — a module-level `Console` would
be shared mutable state on the render path for no measurable gain.

**§6.6's cost attribution is independently corroborated.** I instrumented the
guard across the full suite: **2,055 settle passes, 269 of which re-render
(13%)** — and **zero** of those at the four loss sizes after an `o` press. So at
those sizes the whole settle-pass cost is `_pagination_text` → `_unpainted_ids` →
`_rows`, exactly as §6.6 attributes it. The re-render path is *not* dead code
overall: it fires on genuine geometry moves (`(80,15)` vs `(80,16)`, `(58,26)` vs
`(58,23)`, `(30,17)` vs `(30,22)`, and 266 more), so `_rendered_for` guards a
real path. Your decision not to memoise `_rows` — a cache being a second
staleness mechanism in an increment about two things disagreeing — is the right
call, and carrying it to `Inc-REPAIR` with the number attached is the right shape.

**`_rendered_for` has exactly two writers and they are the only two writers of
`#map-canvas` content** (`app.py:1712` and `app.py:2454`), both of which set it.
Verified by grep over every `#map-canvas` reference. No third path exists today,
which is why `M1` and `M2` were no-ops rather than defects.

**The `A-98` tripwire was honoured, not spent.** The set was widened to
`{layered, outline}`, the docstring rewritten to say why, `radial`'s absence
stated as the remaining hole with its `Inc-B55b` owner, and `lane`'s absence
distinguished by a different reason with its own pinned arm named. No `-k`
exclusion. This is what the gate asked for.

**The `A-3` census works.** It caught my own untracked probe file the moment I
dropped `tests/zz_probe.py` into the tree
(`test_tc_a3_no_source_file_is_invisible_to_the_census` went red). The
cardinality pins were updated with itemised reasons for both the `+1` arg-ful and
`+1` zero-arg site, and the zero-arg classification is correct —
`canvas.render()` is a widget being asked what it holds, not a renderer
invocation.

**`test_tc_038` was strengthened, not weakened.** The one removed assertion
(*"the outline view declares nothing"*) was replaced by a stronger positive plus
an explicit vacuity guard (`assert hidden, "nothing is hidden in outline at this
size; vacuous"`), with `radial` taking over the `None` case. The only deletion in
506 lines of test diff, and it is an upgrade.

**Mutation results, full table.** All restored byte-identically.

| mutant | change | caught by |
|---|---|---|
| `M0` | settle arming removed (`7a973df` reverted) | **NOTHING — 954 pass** |
| `M1` | `_rendered_for` re-stamped after the strip update | nothing (no-op: geometry unchanged there) |
| `M2` | guard → `if self._rendered_for is None` | nothing (settle never re-renders anyway) |
| `M5` | `_fit_declared` loop → 1 pass | `AT-057` `AGREE-2` @ `(30,16)` ✓ |
| `M6` | empty-frame floor removed | `P1` non-degeneracy @ `(34,14)` ✓ |
| `M8` | cut back to a logical slice (`cost = 1`) | 5 arms ✓ |
| `M9` | `_fit` over-cut by one row (`>` → `>=`) | `AT-057` @ `(35,14)`, `P1` @ `(34,14)` ✓ — **not `AT-056`** |
| `M10` | `_fit` under-cut by one row | `test_c53` golden only — no semantic arm |
| `M11` | `_declared` counts rows not nodes | nothing — **equivalent mutant** |

`M11` is genuinely equivalent: `_fit` returns a prefix, so the header is in both
`rows` and `kept` or in neither, and the `if nid` filter cancels. Not a finding —
but `_declared`'s filter is currently redundant, and the docstring
(*"Rows without a node id do not count"*) describes a distinction the code cannot
make. `M10` is worth noting on its own: an under-cut — content emitted into a
void, the original `B-55` shape — is caught only by a golden hash, not by any
semantic arm. That is the same hole `F4`'s missing `PHYS-1` would close.

---

## Evidence checklist

- [x] **Diff read in full.** `3122519..0b2fc1b` — `app.py` +134, `outline.py`
      +375/-146, four test files. `9a773e4` excluded as Inc-CRUMB.
- [x] **Correctness pass.** Empty-frame floor, cycle guard, short-circuit paths,
      `LookupError` seam, `_rendered_for` writers, `w`/`h` source asymmetry.
- [x] **Simplicity pass.** `F5` (unreachable third pass), `M11` (redundant
      filter), `_fit`'s `Console` measured and cleared.
- [x] **Reuse / duplication.** `F7` — token shared, sentence triplicated,
      `MAX_RENDER_NODES` triplicated but pinned.
- [x] **Tests reviewed for intent.** 12 mutants fired; `F1`, `F3`, `F4` are the
      results.
- [x] **Verdict explicit.** BLOCK on `F1`; `F2` requires a recorded carry or an
      extended arm before close.
- [x] **Tree restored.** Byte-identical to `0b2fc1b`, `__pycache__` purged,
      `954 passed` re-confirmed post-restore.

## What must happen before this advances

1. **`F1`** — land a `P1` arm that reddens with the settle arming removed. The
   forced-trigger recipe above is verified to do so at all four loss sizes.
   Until then the increment's own evidence obligation 2 is undischarged.
2. **`F2`** — either extend `AT-056`/`AT-057` to pin the ratified silent-canvas
   fallback, or record it as a carry in §7. Not neither.
3. **`F3` / `F4`** — correct the `PHYS-4` comment to state the trade, and either
   write the `PHYS-1` pilot arm or strike it from §4 with a reason.

`F5`–`F8` are recommendations and do not block.
