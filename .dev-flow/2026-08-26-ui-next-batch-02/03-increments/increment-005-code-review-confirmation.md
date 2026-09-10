# Increment 5 — CONFIRMATION PASS on the post-fix tree (`LLR-N07.2.2b` / `AT-024`)

**Batch:** `2026-08-26-ui-next-batch-02` (SEALED) · **Increment:** `Inc-5`
**Confirming against:** `increment-005-code-review.md` (**BLOCK — 1 HIGH**, findings `F1`-`F7`)
**Reviewed:** the UNCOMMITTED post-fix working tree at the five pinned sha256s, against `90e2a3f`.
**Reviewer:** independent of both the implementer and the round-1 reviewer. Nothing was accepted on
the strength of the corrective pass having run; every finding was re-executed with a harness built
from scratch for this pass.

## Gate verdict

> **BLOCK — 1 HIGH.**
> `F1` is **PARTIALLY DISCHARGED**. The `min(hits)` shape it named is now killed in all five changed
> renderers, executed and confirmed. The **mirror shape of the same error class survives**: a renderer
> that drops the FIRST member of the hit set and paints the last one satisfies all 44 arms, and
> survives a 199-arm run across twelve test files. The gate closing `AT-024` still cannot see half of
> the error class `AT-024` is catalogued against.
>
> The fix is **one line** in one test file, touches no source file, and does not move the census pin.

`A-91`'s lighter lane remains revoked, as §11 already records.

---

## Entry / exit state

Pins asserted at entry, and again after the last mutation was restored:

```
06a0e9493f10bbc392bf4e175ee737f3ca1ef95cf10b996de139de7105325b39 *mapper/views/outline.py
aa462076e911c3983c4a02589094fbadd150fcfb6f1dab8d740b6fd7420f6d85 *mapper/views/radial.py
098b90b4baad538e9fda51be662a52f9354781e85085496153119d289ee602ef *mapper/views/lane.py
7972d95f20558a897c0d12521786b7c1d37fc79e4768f75092b4d73e3ed1ce8c *tests/test_views_hits.py
8384ebfa42b47af6809b4fd9de81dbd450fa38f1d59ec2ae500035c033880e56 *tests/test_a3_census.py
3e081a6c61af9a20ec5ec94140e4258226fc0b692c65dea707701ba07c4015b5 *mapper/views/layered.py   (read-only 6th renderer, mutated by me, restored)
--- git status --porcelain, identical to entry apart from THIS file ---
 M .dev-flow/state.json
 M mapper/views/lane.py
 M mapper/views/outline.py
 M mapper/views/radial.py
 M tests/test_a3_census.py
AM tests/test_views_hits.py
?? .dev-flow/.../increment-005-code-review.md
?? .dev-flow/.../increment-005.md
```

**Tree discipline.** I was the only writer; the implementer had stopped. 24 mutations were fired.
Every one was applied to bytes read from disk and restored in a `finally` from those exact original
bytes, with sha256 asserted equal before the next fired. `__pycache__` purged on both sides of every
mutation, `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUTF8=1` in every child process. Mutations are
described **by position and operation** and are not pasted verbatim (`C-56`). Mutation is applied at
the **byte** level, not through text-mode I/O, because this tree mixes LF and CRLF files and newline
translation would have rewritten lines the mutation never touched. Harness lives outside the repo
(`C:\Users\jjgh8\clde\scratch\inc5_confirm\`); `.pytest_cache/` and `.ruff_cache/` are pre-existing
and git-ignored.

**Instrument RED-proof (`C-57`), executed before any verdict was read.** The harness asserts the
resolved arm count (44) before believing any all-green, and a planted control ran first:

```
BASELINE                                          resolved=44 passed=44 red=0
CONTROL outline hit branch made unreachable       resolved=44 passed=38 red=6
   RED  ..._every_renderer_paints_hits[outline.OutlineRenderer]
   RED  ..._the_paint_is_keyed_on_WHICH_node_is_a_hit[outline.OutlineRenderer]
   RED  ..._a_hit_outside_the_first_branch_is_painted_too[outline.OutlineRenderer]
   RED  ..._a_hit_on_the_FIRST_branch_is_painted_too[outline.OutlineRenderer]
   RED  ..._EVERY_member_of_the_hit_set_is_painted[outline.OutlineRenderer]
   RED  ..._every_renderer_uses_THE_SAME_hit_style
[restore ok] mapper/views/outline.py sha256=06a0e949...25325b39
```

Verdicts below are read from **resolved node ids**, never from the process exit code.

---

## Finding-by-finding

### `F1` (HIGH) — **PARTIALLY DISCHARGED. The HIGH stands.**

**The half that is discharged.** I constructed the `min(hits)` shape myself for each of the five
changed renderer classes — the membership test at each hit site replaced by an equality against the
lowest-sorted member of the hit set — and fired each independently. All are now **KILLED**, each by
exactly the arm added for it:

```
SHAPE-MIN  outline.OutlineRenderer     resolved=44 passed=43 red=1
   RED  ..._EVERY_member_of_the_hit_set_is_painted[outline.OutlineRenderer]
SHAPE-MIN  radial.RadialRenderer       resolved=44 passed=43 red=1
   RED  ..._EVERY_member_of_the_hit_set_is_painted[radial.RadialRenderer]
SHAPE-MIN  lane.LaneRenderer           resolved=44 passed=43 red=1
   RED  ..._EVERY_member_of_the_hit_set_is_painted[lane.LaneRenderer]
SHAPE-MIN  lane.RailTimeline(label)    resolved=44 passed=43 red=1
   RED  ..._EVERY_member_of_the_hit_set_is_painted[lane.RailTimelineRenderer]
SHAPE-MIN  lane.HybridLaneRenderer     resolved=44 passed=43 red=1
   RED  ..._EVERY_member_of_the_hit_set_is_painted[lane.HybridLaneRenderer]
SHAPE-MIN  layered.LayeredRenderer     resolved=44 passed=43 red=1   (6th renderer, outside the diff)
   RED  ..._EVERY_member_of_the_hit_set_is_painted[layered.LayeredRenderer]
[restore ok] all files, sha256 matched
```

§11.1's table reproduces. `MUT-F/G/H` are dead. That part of the block is genuinely cleared.

**The half that is not.** The new arm is **one-sided**. It fixes the one-member render it compares
against — `{"first"}` — and asserts only that the two-member picture differs from *that* one. A
renderer that drops the first member and paints the last satisfies it: `both` paints `other`,
`only_one` paints `first`, the two differ, the arm is green. Executed as SHAPE-MAX — the same
positional edit, equality against the **highest**-sorted member instead of the lowest:

```
SHAPE-MAX  outline.OutlineRenderer     resolved=44 passed=44 red=0   *** SURVIVED ***
SHAPE-MAX  radial.RadialRenderer       resolved=44 passed=44 red=0   *** SURVIVED ***
SHAPE-MAX  lane.LaneRenderer           resolved=44 passed=44 red=0   *** SURVIVED ***
SHAPE-MAX  lane.RailTimeline(trunk)    resolved=44 passed=44 red=0   *** SURVIVED ***
SHAPE-MAX  lane.RailTimeline(label)    resolved=44 passed=44 red=0   *** SURVIVED ***
SHAPE-MAX  lane.HybridLaneRenderer     resolved=44 passed=44 red=0   *** SURVIVED ***
SHAPE-MAX  layered.LayeredRenderer     resolved=44 passed=44 red=0   *** SURVIVED ***
[restore ok] all files, sha256 matched
```

**Seven for seven, including the one renderer that was already compliant before the increment.**
Widened to the whole style-observing surface — twelve test files, 199 resolved arms — the verdict set
is **identical to baseline** (the three non-PASSED arms in both columns are the batch's pre-existing
`test_fold` XFAILs, confirmed as XFAIL by name):

```
WIDE BASELINE                                    resolved=199 passed=196 (+3 xfail)
SHAPE-MAX outline paints only the last member    resolved=199 passed=196 (+3 xfail)  SURVIVED
SHAPE-MAX rail-label paints only the last member resolved=199 passed=196 (+3 xfail)  SURVIVED
```

That is not an accident of my fixture. Executed: outside `tests/test_views_hits.py`, **every** hit set
rendered anywhere in the repository is a singleton — `test_fold.py:898` `{"f"}`, `test_layered.py:167`
`{injected}`, `test_layered.py:178` `{"c"}`. The plural case is driven by exactly one arm, and that
arm looks in one direction only.

**Why this keeps the HIGH rather than becoming a fresh MEDIUM.** It is not an adjacent gap; it is the
same error class, at the same gate, with the same consequence. `01-requirements.md:2456-2458` is
indifferent to *which* member is dropped: a count line declaring N over a canvas painting 1 is the
defect whether the survivor is the first hit or the last. The arm's own docstring claims more than it
verifies — *"A renderer that paints only ONE member and ignores the rest therefore satisfied the
entire file"* — and a reader will take that class as closed. It is half closed. Under the rubric,
a test whose stated guarantee exceeds what it can observe is false confidence, and the cost of
closing it properly is one line.

**Suggested fix** — one added render and one added assertion; no source file touched:

```python
    _, none       = _spans_at(cls, 120, set())
    _, only_first = _spans_at(cls, 120, {"first"})
    _, only_other = _spans_at(cls, 120, {"other"})
    _, both       = _spans_at(cls, 120, {"first", "other"})
    assert both != none, f"{cls.__name__} paints nothing for a two-member hit set"
    assert both != only_first, (
        f"{cls.__name__} paints the same picture for one hit and for two: "
        "members beyond the first are dropped"
    )
    assert both != only_other, (
        f"{cls.__name__} paints a two-member hit set exactly like the LAST member "
        "alone: the first member is dropped"
    )
```

With both directions pinned, **any** renderer painting exactly one of the two members is killed — it
must paint `first` or `other`, and each is now compared against. Verified against the shapes above:
the third assertion is what reddens SHAPE-MAX, including at the rail-timeline trunk. Note for the
docstring: say *"a renderer that paints only one member — whichever one"*, so the claim matches the
observation.

**Census impact: none.** The census counts arg-ful `render(...)` **call sites** by `(file, line)`, and
the whole module has exactly one — re-derived: `[('tests/test_views_hits.py', 79)]`, the call inside
`_spans_at`. Adding calls **to** `_spans_at` cannot move the `59` pin.

---

### `F2` (MEDIUM) — **DISCHARGED**, and independently re-measured

`radial.py:232` now reads as a bare membership test; the conjunct is gone and the comment at
`:233-244` states what was measured instead of the claim that was false.

I reproduced the byte-identity result rather than accepting it. My probe is my own — 225
configurations (`w` in 60/80/100/120/160 × `h` in 12/24/40 × 5 hit sets × 3 selections), hashing
`(plain, [(start, end, str(style)), ...])` — run in a child process against the shipped bytes, then
against the same file with the trailing conjunct re-added at that position (the pre-fix shape):

```
SHIPPED (no conjunct)  : configs=225 sha256=d359957f7d7a8f55af3b52e3f41b77fa6a48e13613ea83ce863a0c9e1236682d
PRE-FIX (with conjunct): configs=225 sha256=d359957f7d7a8f55af3b52e3f41b77fa6a48e13613ea83ce863a0c9e1236682d
[restore ok] mapper/views/radial.py sha256=aa462076...20f6d85
```

Identical. **The F2 edit changed no emitted output** — the question item 3 asked. My digest differs
from the round-1 reviewer's because the configuration grid is mine, not theirs; the equality is the
claim, and it holds independently.

I also checked the mechanism rather than trusting the equality. `Canvas.put` (`mapper/canvas.py:103-105`)
writes `self.cells[(x, y)] = (ch, style)` under one guard — in-bounds **and** `ch` truthy. The pill
loop's `j == 0` cell is `(x, y)`; the marker `put` at `radial.py:262` targets the same `(x, y)` with a
non-empty glyph, so the two puts pass or fail the guard together and the second always wins. The
replacement comment is accurate, and it restores parity with `layered.py:539`.

---

### `F3` (MEDIUM) — **PARTIALLY DISCHARGED.** One of the six precedence sites is still unobserved

The arm exists and it is real. Six inversion mutants — the selection guard at each site gaining a
not-in-hits conjunct, so a node that is both selected and a hit takes the hit paint:

```
INV  outline.OutlineRenderer    resolved=44 passed=43 red=1  RED ..._selection_is_painted_ON_TOP_of_a_hit[outline.OutlineRenderer]
INV  lane.LaneRenderer          resolved=44 passed=43 red=1  RED ..._selection_is_painted_ON_TOP_of_a_hit[lane.LaneRenderer]
INV  lane.RailTimeline(trunk)   resolved=44 passed=44 red=0  *** SURVIVED ***
INV  lane.RailTimeline(label)   resolved=44 passed=43 red=1  RED ..._selection_is_painted_ON_TOP_of_a_hit[lane.RailTimelineRenderer]
INV  lane.HybridLaneRenderer    resolved=44 passed=43 red=1  RED ..._selection_is_painted_ON_TOP_of_a_hit[lane.HybridLaneRenderer]
INV  radial.RadialRenderer      resolved=44 passed=43 red=1  RED ..._selection_is_painted_ON_TOP_of_a_hit[radial.RadialRenderer]
[restore ok] all files, sha256 matched
```

Five of six killed — the two the round-1 reviewer fired are among them, so §11.3's claim is true as
far as it goes. **The sixth is a real, killable coverage gap.** The arm always selects node `hit`,
which is `branches[1]`. `RailTimelineRenderer` routes `branches[0]` through `main_style`, a separate
statement rewritten by this diff (`lane.py:226-231`), and no arm ever selects the trunk. This is
§3.3's own lesson — *the trunk is a different code path* — recurring one arm later, in the arm added
to close `F3`. Round 2 fired two precedence mutants where six sites exist, which is the same
incomplete-input-set shape `§11.1` correctly diagnoses as `C-31`.

**Suggested fix:** drive the selection on the trunk as well as on a later branch, e.g. parametrise the
arm over `sel in ("first", "hit")`, or add a second pair of renders with `selected="first"`,
`hits={"first"}`. Either kills the surviving mutant. (Arm count moves 44 → 50 if parametrised; the
census pin does not move, same reason as `F1`.)

**Vacuity flank, recorded but NOT charged against this increment.** The arm asserts an *equality*
between two renders, so it also passes when the selection paints nothing distinguishable at all.
Executed: neutralising the selection style at `outline.py:127` and at `lane.py:353` leaves the arm
green, and leaves the **whole 199-arm, twelve-file surface** green:

```
VAC-WIDE outline selection paint neutralised     resolved=199 passed=196 (+3 xfail)  SURVIVED
VAC-WIDE hybridlane selection paint neutralised  resolved=199 passed=196 (+3 xfail)  SURVIVED
```

Selection styling is shipped behaviour that predates `Inc-5` and is outside this diff, so this is a
pre-existing repository gap, not a defect the fold introduced. It is worth knowing that the new
precedence arm does **not** close it, and that the equality direction is the reason.

---

### `F4` (MEDIUM) — **DISCHARGED**

`tests/test_views_hits.py:190` is an `assert`, the `pytest.skip` is gone, and the docstring at
`:176-194` now describes what the code does. Verified by mutation rather than by reading: a clip
mutant at `lane.py:286` narrowing `max_label` to zero produces a **FAILED**, not a SKIPPED, and it is
the precondition clause that fires, with the promised message:

```
tests\test_views_hits.py:190: AssertionError: RailTimelineRenderer no longer draws the third branch
at 120 columns, so this arm has stopped measuring the paint and is measuring the clip.
See B-55: a clipped hit is an UNDECLARED hit
FAILED ..._a_hit_outside_the_first_branch_is_painted_too[lane.RailTimelineRenderer]
1 failed, 5 passed in 0.19s
[restore ok] mapper/views/lane.py sha256=098b90b4...9ee602ef
```

Zero skips in the full default lane, so no green escape hatch is held open anywhere.

---

### `F5` (MEDIUM) — **DISCHARGED**

`tests/test_views_hits.py:45` imports the one derivation
(`from tests.test_a3_census import renderer_classes`); the copied `tracked` / `renderer_classes` are
gone, the now-meaningless equality arm is gone, and `importlib` / `subprocess` / `Path` are gone with
them (`:28-29` records why). `tests/__init__.py` exists, so this is a package import and not a
sys.path accident. Arm arithmetic reconciles: 33 − 1 + 6 + 6 = **44**, resolved and counted.
No duplicate collection of the census module: the full lane's totals move by exactly the same net
`+11` (`887 → 898`), which they could not if `test_a3_census` were being collected twice.

---

### `F6` (LOW) — **DISCHARGED**

§11.6 states the operator-reachable movement as **1 of 3 → 3 of 3**, names the three lane renderers as
having no production consumer, and keeps the derived set as-is with the right justification.

One nit, not a re-open: the round-1 BLUF text at `:13-15` is unedited, and the superseded-claims note
at `:277-280` names only two claims (the ledger and the checklist line) — the BLUF's `1 of 6 → 6 of 6`
is a third. §11 governs by declaration and §11.6 carries the correct number, so a reader who follows
the governance note is not misled; add it to the named list if the packet is touched again for any
other reason.

---

### `F7` (LOW) — **CARRIED, correctly declared**

§11.7 declares it unfixed and routes it to `ux-reviewer`; §10's third bullet carries the same content
with the `layered` precedent. Nothing was silently folded in. I confirm the behaviour is unchanged:
in all six renderers a selected node keeps its selection block whether or not it is a hit — which is
exactly what the new precedence arm now pins, so `F7` and the `F3` arm are consistent with each other
rather than in tension.

---

## §11 figures — re-executed, not accepted

Both lanes run once each, from the tree sha256-pinned before the run and re-pinned after, with
`-p no:cacheprovider` and no writers other than pytest.

| §11.8 claim | My measurement | Verdict |
|---|---|---|
| `898 passed, 17 deselected, 3 xfailed` | `898 passed, 17 deselected, 3 xfailed in 207.89s` exit 0 | **TRUE** |
| all markers `915 passed, 3 xfailed` | `915 passed, 3 xfailed in 233.89s` exit 0 | **TRUE** |
| lane arithmetic `898 + 17 = 915` | holds | **TRUE** |
| `44 arms, zero skipped` | 44 resolved node ids, 44 PASSED; zero `skipped` in either full lane | **TRUE** |
| census `argful 59, zeroarg 26, defs 7` | re-derived from `render_call_sites()` / `render_definitions()`: `argful 59 zeroarg 26 defs 7` | **TRUE** |
| the pin did not move because `selected` is a defaulted parameter | the module's only arg-ful site is `('tests/test_views_hits.py', 79)` — one site, as claimed | **TRUE** |
| ruff SET `27 = 27`, zero NEW, zero GONE | `ruff check mapper tests` = **27**, and `ruff check` over all five touched paths = **All checks passed** — so the delta from `90e2a3f` is empty in both directions. `90e2a3f`'s own 27 / SET-identity to `9ba2f26` is Inc-4c's pinned figure, which I did not re-derive | **TRUE for this increment's delta** |
| `898 = 887 − 1 + 12` | consistent with 33 → 44 arms and the retired agree-arm | **TRUE** |

**A methodology warning for whoever re-runs the ruff comparison.** Comparing ruff across directories
is not valid here. Linting a `git archive` of `9ba2f26` extracted outside the repository enables an
extra rule family (`I001`/`I002`) inherited from an ancestor configuration that the repository
directory does not resolve — 70 findings there against 27 here, and a spurious "NEW `I001` in
`tests/test_views_hits.py`". `--show-settings` shows the two rule sets differing. Any future SET
comparison must be run **inside** `C:\Users\jjgh8\Github\mapper` (Inc-4c's `git stash` approach was
right for this reason), or restricted to per-file findings as I did above.

Round-1 claims I re-checked and found honest: §11.3's own admission that *"every predicate
demonstrated able to go RED — 9 mutants, 9 KILLED"* was **overstated** is correct and is stated
plainly; the `⚠` note at `:277-280` does supersede the round-1 ledger rather than editing it away.

---

## NEW findings raised by this pass

### `N1` — the plural arm is one-sided; dropping the FIRST member of the hit set is invisible [Severity: HIGH]

Recorded above under `F1`, because it is that finding's unresolved half rather than a separate defect.
Where: `tests/test_views_hits.py:241-248`. Evidence: 7/7 SHAPE-MAX mutants survive 44 arms; 2/2 survive
199 arms across twelve files. Fix: the three-assertion form given under `F1`. **This is the only
finding blocking the gate.**

### `N2` — `RailTimelineRenderer`'s trunk precedence branch is unobserved [Severity: MEDIUM]

Where: `mapper/views/lane.py:226-231`, against `tests/test_views_hits.py:252-268`. Newly-authored
logic in this diff whose inversion survives all 44 arms, because the precedence arm only ever selects
`branches[1]`. Not operator-reachable today (`F6`), which is why it is MEDIUM and not higher. Fix
under `F3` above. Recommend fixing in the same pass as `N1`, since both are edits to the same two
arms.

### `N3` — the fixture makes `branches[0]` permanently the lowest-sorted hit id [Severity: LOW]

`_graph()`'s ids are `first` < `hit` < `other` < `root`, and the trunk is `first`. So at the trunk site
the `min(hits)` shape is an **equivalent mutant** for every hit set this file drives — it survived my
SHAPE-MIN run for that reason, not because of a gap. Worth knowing before anyone reads that single
SURVIVED line as a defect, and worth a fixture note: an id ordering that decouples "is the trunk" from
"is the lowest-sorted hit" would make the two properties separable. This is the `C-57` fixture-symmetry
concern applied to id ordering rather than to titles. No action required for this increment.

### `N4` — nothing else

I attacked the fold for a defect it introduced and did not find one. Specifically checked and clean:
the `F2` source edit is output-neutral over 225 configurations (measured, above); the `F5` import is a
real package import with no duplicate collection and no module-level side effect beyond what the copy
already did; `_spans_at`'s new `selected` parameter is threaded correctly and leaves `_spans`'
call shape untouched; the five hit branches remain pure membership tests over a `frozenset[str]` with
no file-derived text reaching any style, so `A-91`'s no-security-sink verdict still holds on the
amended tree and there is nothing to route to `security-reviewer`.

---

## Evidence checklist

- [x] **Diff read in full** — `mapper/views/{outline,radial,lane}.py` diffs end to end,
      `tests/test_views_hits.py:1-299`, `tests/test_a3_census.py:178-194`, plus `canvas.py:103-105`,
      `layered.py:485,528` and `views/__init__.py` as read-only context, and both the round-1 review
      and `increment-005.md` in full.
- [x] **`F1` re-executed, not trusted** — the `min(hits)` shape rebuilt from scratch per renderer;
      5/5 changed classes KILLED (+ `layered`), each by the named arm.
- [x] **New arms attacked for vacuity** — the plural arm falls to SHAPE-MAX (7/7, 199-arm wide run);
      the precedence arm holds against 5 of 6 inversions and is blind to the trunk, and its equality
      direction is blind to the selection paint disappearing entirely.
- [x] **New defect from the fold hunted** — `radial.py` output byte-identical across 225
      configurations; `F5`'s import verified as a package import with no double collection. None found.
- [x] **`F3`/`F4`/`F5`/`F6`/`F7` checked in the TREE and in the PACKET** — `F4` proved by mutation
      (FAILED with the promised message, not SKIPPED); `F5` proved by the arm arithmetic and the
      absent copy; `F7` confirmed declared in two places.
- [x] **Packet honesty checked** — every §11.8 figure re-executed; all reproduce. One methodology
      caveat added about cross-directory ruff comparison.
- [x] **Verdicts per resolved node id, arm count asserted first** — 44 asserted before any all-green
      was believed; the harness raises rather than reporting on a resolved count it did not expect.
- [x] **Tree restored** — six sha256 pins matched after the last restore; `git status --porcelain`
      identical to entry apart from this file; `__pycache__` purged.
- [x] **Verdict explicit** — below.

## Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **BLOCK — must fix the HIGH before advancing**

**HIGH findings surviving: 1** (`F1` / `N1` — the same finding, half-closed).
**New findings raised: 3** (`N1` HIGH, `N2` MEDIUM, `N3` LOW).

**Minimum to clear the block:** add the third assertion to
`test_llr_n07_2_2b_EVERY_member_of_the_hit_set_is_painted` so the two-member picture is pinned against
**both** one-member pictures, and re-fire the `max(hits)` shape against all five changed renderers —
SHAPE-MAX must go from SURVIVED to KILLED. Tests only; the sealed `SOURCE FILE COUNT: 3` and every
`A-91` source verdict are unaffected, and the census pin stays at 59.

**Recommended in the same pass:** `N2` — give the precedence arm a trunk selection, so the sixth
inversion mutant dies with the other five. `N3` and the `F6` nit are notes, not work.

A third confirmation pass is warranted on the amended tree, and it should re-fire **both** shapes plus
the six inversions, because the pattern this increment keeps producing is a correct fix to the exact
mutant that was named, with the mirror of that mutant left standing.
