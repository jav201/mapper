# Increment 5 — Independent code review (`LLR-N07.2.2b` / `AT-024`)

**Batch:** `2026-08-26-ui-next-batch-02` (SEALED) · **Increment:** `Inc-5`
**Reviewed:** the UNCOMMITTED working tree against `90e2a3f`. Reviewer is independent of the implementer.
**Protocol claimed:** `A-91` lighter lane, conditional on **zero HIGH** from this review.

## Gate verdict

> **BLOCK — 1 HIGH.**
> Because a HIGH stands, the `A-91` lighter lane **does not apply to this increment**; the full protocol is restored.

The implementation itself is correct and I found **no defect in shipped behaviour**. The HIGH is an
acceptance-strength finding: the arms that close `AT-024` cannot see the error class `AT-024` was
written to prevent. The fix is small (§F1 carries the patch shape) and does not touch the sealed
3-file source cut.

---

## Scope reviewed

| Path | Reviewed |
|---|---|
| `mapper/views/outline.py` | full diff, `:52`, `:130-136` |
| `mapper/views/radial.py` | full diff, `:112`, `:229-244`, plus `:254` and `mapper/canvas.py:103-105` for the overwrite semantics |
| `mapper/views/lane.py` | full diff, `:113`, `:133-139`, `:180`, `:226-232`, `:289-296`, `:322`, `:351-357` |
| `tests/test_views_hits.py` | all 264 lines, all 33 arms |
| `tests/test_a3_census.py` | the `58 -> 59` pin and its itemised reason, `:182-194` |
| `.dev-flow/.../increment-005.md` | read in full; every numeric claim re-executed, not accepted |
| `01-requirements.md` `LLR-N07.2.2b` | `:2750-2795`, and the `AT-024` boundary row at `:2456-2458` |

**Tree discipline.** I was the only writer. Eight mutants were fired; every one was restored from the
original bytes in a `finally` block and asserted byte-identical by sha256 before the next fired, with
`__pycache__` purged on both sides of every mutation and `PYTHONDONTWRITEBYTECODE=1` set throughout.
Mutations are described by position and operation only (`C-56`). Final state, executed after the
reviewer's own scratch files were deleted:

```
06a0e9493f10bbc392bf4e175ee737f3ca1ef95cf10b996de139de7105325b39 *mapper/views/outline.py
ac8c9ced82f60c202f158e552d2d6c36dae0e7cbe54df96029c9025978fce0c9 *mapper/views/radial.py
098b90b4baad538e9fda51be662a52f9354781e85085496153119d289ee602ef *mapper/views/lane.py
--- status ---
 M .dev-flow/state.json
 M mapper/views/lane.py
 M mapper/views/outline.py
 M mapper/views/radial.py
 M tests/test_a3_census.py
A  tests/test_views_hits.py
?? .dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-005.md
```

All three pins match. `git status --porcelain` is identical to the entry state.

---

## Findings

### F1 — `AT-024` never drives a hit set with more than one member; a renderer that paints ONE of N hits ships green [Severity: HIGH]

- **Where:** `tests/test_views_hits.py:90-95` (`_spans_at` / `_spans`), and every arm that calls them —
  `:126`, `:141`, `:160`, `:200-213`, `:230-234`, `:251-256`. Every single call passes a hit set of
  size 0 or 1: `set()`, `{"hit"}`, `{"first"}`, `{"other"}`. **`|hits| >= 2` is never rendered anywhere
  in the file.**
- **What:** the requirement is plural — *"shall paint the **nodes** carried in `state.hits`"*
  (`01-requirements.md:2753`). The acceptance verifies only the singular case. A renderer that paints
  exactly one member of the hit set and ignores the rest satisfies all 33 arms.
- **Why it matters:** this is precisely the error class `AT-024` is catalogued against. From the
  boundary catalog at `01-requirements.md:2456-2458`: *"reporting a count a view does not paint is the
  error class this story exists to prevent."* A view that paints 1 while the count line declares N is
  that error, exactly — and the gate closing `AT-024` cannot see it. The five call sites shipped here
  are all correct membership tests, so nothing is broken today; what is missing is the arm that keeps
  it that way. It is also the live shape of the next plausible feature (a "current match" distinguished
  from "other matches", which `AT-022`'s walk already implies), so this is not a contrived risk.
- **Executed.** Three independent single-conjunct mutants, one per renderer family, each reducing the
  paint to the lowest-sorted member of the hit set. All three **SURVIVED**:

```
MUT-F outline paints only min(hits):              resolved=127 passed=127 red=0
MUT-G radial paints only min(hits):               resolved=138 passed=138 red=0
MUT-H railtimeline label paints only min(hits):   resolved=138 passed=138 red=0
[restore ok] mapper/views/outline.py sha256=06a0e949...25325b39
[restore ok] mapper/views/radial.py  sha256=ac8c9ced...78fce0c9
[restore ok] mapper/views/lane.py    sha256=098b90b4...9ee602ef
```

  (arm sets: `test_views_hits`, `test_outline`, `test_lane`, `test_radial`, `test_search`,
  `test_layered`, `test_fold`, `test_inc3_census`, and for F/G/H also `test_export` /
  `test_repair_golden_census`.)

- **Suggested fix** — one arm, parametrised over the derived set like its siblings, no source file
  touched, sealed cut unaffected:

```python
@pytest.mark.parametrize("cls", renderer_classes(), ids=...)
def test_llr_n07_2_2b_EVERY_member_of_the_hit_set_is_painted(cls):
    """|hits| > 1 is the ordinary case for a live query, and it was unobserved.

    A renderer that paints only one member satisfies every singular arm while
    the count line declares N -- the error class AT-024 is catalogued against.
    """
    _, none = _spans_at(cls, 120, set())
    _, only_a = _spans_at(cls, 120, {"first"})
    _, both = _spans_at(cls, 120, {"first", "other"})
    assert both != none
    assert both != only_a, (
        f"{cls.__name__} paints the same picture for one hit and for two: "
        "a second member of the hit set reaches no style decision"
    )
```

  Drive it at 120, not 80, for the same measured reason `:200` gives; reuse that arm's
  `Cronograma`-present precondition (see F4 for how that precondition should report).

---

### F2 — `radial.py:232`'s `and j` conjunct is provably dead, and its comment states a behaviour that does not exist [Severity: MEDIUM]

- **Where:** `mapper/views/radial.py:232` (`elif nid in hits and j:`) and the comment at `:233-236`.
- **What:** the comment claims the conjunct *"keeps the leading pad cell out of the highlight so the
  pill still reads as a pill; the branch tint below owns that cell for every other node."* Neither
  half is true. The cell at `j == 0` is `(x, y)`, and `radial.py:254` unconditionally does
  `cv.put(x, y, marker, marker_style)` after the loop. `Canvas.put` (`mapper/canvas.py:103-105`)
  assigns into `self.cells` with no precedence check, so **the marker overwrites whatever the loop
  wrote at `j == 0`, for every node, hit or not**. The conjunct changes nothing observable, and no arm
  covers the cell it "excludes" because there is nothing there to cover.
- **Why it matters:** three costs, none of them fatal. (i) A reader who trusts the comment believes
  the pill's pad cell is a live design decision; it is not, and a future edit that removes the marker
  overwrite would silently activate a branch nobody has ever seen render. (ii) It is a gratuitous
  divergence from `layered.py:538-540`, which the packet §2 names as the pattern being followed —
  `layered` paints the hit style for **all** `j`, including `j == 0`. (iii) It costs the diff a
  conjunct and four comment lines that carry a false claim.
- **Executed.** Dropping the conjunct is invisible to the suite *and* to the renderer's own output:

```
MUT-A (drop the trailing conjunct on the hit guard):
  resolved=128 passed=128 red=0   SURVIVED
  [restore ok] mapper/views/radial.py sha256=ac8c9ced...78fce0c9

Direct output probe, 225 configurations (w in 60/80/100/120/160 x h in 12/24/40
x 5 hit sets x 3 selections), comparing (plain, [(start, end, str(style)), ...]):
  BASELINE sha256 e9fb0d9b3242318834a76b5c716462b184b43bb66fa5c05c72a822e610dc9b5f
  MUTANT   sha256 e9fb0d9b3242318834a76b5c716462b184b43bb66fa5c05c72a822e610dc9b5f
```

  Byte-identical. This is dead logic, not an uncovered behaviour — so it cannot be closed by adding
  an arm, only by deleting the conjunct or by making the claim true.
- **Suggested fix:** drop the conjunct and the comment's second and third sentences —
  `elif nid in hits:` — which also restores parity with `layered.py:538`. If the pad-cell exclusion is
  genuinely wanted, it has to be expressed where it can take effect (`marker_style`), and then it needs
  an arm; do not keep an inert conjunct standing in for an intention.

---

### F3 — selection-over-hit precedence, the increment's one explicit design decision, is unobserved by every arm in the repository [Severity: MEDIUM]

- **Where:** the ordering itself at `outline.py:126/130`, `lane.py:130/133`, `lane.py:226/228`,
  `lane.py:289/291`, `lane.py:351/354`, `radial.py:230/232`; the claim at packet §2
  (*"Precedence: selection is painted ON TOP of a hit ... Not invented here"*), restated in six
  in-code comments.
- **What:** **no test anywhere sets `selected_id` and `hits` at the same time.** Every arm in
  `tests/test_views_hits.py` constructs `ViewState(w=..., h=24, hits=...)` (`:91`), leaving
  `selected_id` at its `None` default. Inverting the precedence — making a hit win over the selection —
  is green.
- **Why it matters:** the ordering is newly-authored logic in five places, and the outline comment
  (`:131-134`) states the exact harm it prevents: *"losing your place is worse than losing one
  highlight."* Nothing in the suite defends that. It also means the packet's gate checkbox
  *"Every predicate demonstrated able to go RED — 9 mutants, 9 KILLED"* (§9) is **overstated**: the
  battery fired no mutant against the branch ordering, and the two I fired both survive.
- **Executed.** Both inversions, run against 12 test files:

```
MUT-D outline hit-over-selection      (guard gains a not-in-hits conjunct):
  resolved=185 passed=185 red=0   SURVIVED
MUT-E hybridlane hit-over-selection   (same operation, lane.py:351):
  resolved=185 passed=185 red=0   SURVIVED
[restore ok] mapper/views/outline.py sha256=06a0e949...25325b39
[restore ok] mapper/views/lane.py    sha256=098b90b4...9ee602ef
```

- **Suggested fix:** one non-parametrised arm is enough, since the property is uniform:

```python
def test_llr_n07_2_2b_selection_is_painted_ON_TOP_of_a_hit():
    """The precedence is a decision, not an accident, so it is pinned.

    Inverting it in outline and in the hybrid lane was green across 185 arms.
    """
    for cls in renderer_classes():
        _, sel_only = _spans_at_sel(cls, 120, hits=set(), sel="hit")
        _, sel_hit  = _spans_at_sel(cls, 120, hits={"hit"}, sel="hit")
        assert sel_hit == sel_only, (
            f"{cls.__name__} lets the hit style overwrite the selection block"
        )
```

  This needs a `_spans_at_sel` that also passes `selected_id`; folding `selected_id` into `_spans_at`
  as a defaulted parameter keeps the census pin at 59 (one call site), so the `58 -> 59` bump does not
  move again.

---

### F4 — the width precondition SKIPS where the docstring and packet §3.4 both say it REDDENS [Severity: MEDIUM]

- **Where:** `tests/test_views_hits.py:203-207` (`pytest.skip(...)`) against its own docstring at
  `:195-198` — *"the precondition reddens with a message that says so"* — and packet §3.4, same claim.
- **What:** a failed precondition produces `SKIPPED`, not `FAILED`. The run stays green and the exit
  code stays 0.
- **Why it matters:** the packet's ledger is pinned as `887 passed, 17 deselected, 3 xfailed` — **there
  is no skip count in it**, so an arm silently converting to SKIPPED would not surface in the one
  number the gate reads. Under rule 12 (*fail loud*), a green channel is the wrong home for "this arm
  stopped measuring what it claims to". The damage is bounded rather than fatal: if this arm skips for
  `RailTimelineRenderer`, `test_llr_n07_2_2b_every_renderer_paints_hits[lane.RailTimelineRenderer]`
  still exercises the non-trunk `label_style` path, because fixture node `hit` is `branches[1]`. So
  this is a documentation falsehood plus a silent-degradation channel with a backstop, not a coverage
  hole.
- **Executed.** A clip mutant on `lane.py:286` narrowing `max_label`:

```
PASSED  ..._a_hit_outside_the_first_branch_is_painted_too[lane.HybridLaneRenderer]
PASSED  ..._a_hit_outside_the_first_branch_is_painted_too[lane.LaneRenderer]
PASSED  ..._a_hit_outside_the_first_branch_is_painted_too[layered.LayeredRenderer]
PASSED  ..._a_hit_outside_the_first_branch_is_painted_too[outline.OutlineRenderer]
PASSED  ..._a_hit_outside_the_first_branch_is_painted_too[radial.RadialRenderer]
SKIPPED [1] tests\test_views_hits.py:203: RailTimelineRenderer does not draw the
        third branch at 120 columns, ...
LAST: 32 passed, 1 skipped in 0.28s
[restore ok] mapper/views/lane.py sha256=098b90b4...9ee602ef
```

  Green run, exit 0, one arm silently stopped measuring — the shape §3.4 says it prevents.
- **Suggested fix:** either make the precondition an `assert title in plain, "<message>"` as the
  docstring promises, or keep the skip and correct the docstring and §3.4 to say *skips*, **and** pin
  the skip count in the ledger (`887 passed, 0 skipped, 17 deselected, 3 xfailed`) so a conversion is
  visible. I recommend the assert: at 120 columns all six renderers draw the third branch today, so
  the assert is green on the current tree and there is no reason to hold a green escape hatch open.

---

### F5 — `tracked` and `renderer_classes` are copy-pasted from `test_a3_census`, and the stated reason for the copy is cancelled by the arm that guards it [Severity: MEDIUM]

- **Where:** `tests/test_views_hits.py:40-43` vs `tests/test_a3_census.py:37-39`;
  `tests/test_views_hits.py:46-62` vs `tests/test_a3_census.py:315-334`;
  the guard at `tests/test_views_hits.py:115-122`.
- **What:** the docstring at `:48-52` justifies the duplication as *"this module must keep working if
  that census is re-scoped."* But `test_at024_the_two_derivations_agree` asserts set equality between
  the two — so if the census is re-scoped, this module does **not** keep working; that arm reddens.
  The independence the copy is bought for is spent by the arm that guards the copy.
- **Why it matters:** rule 3 / `C-50`. ~20 duplicated lines whose only stated benefit is unreachable,
  and one arm of the 33 that is a near-tautology: it can go red only if a human edits one of two
  byte-equivalent functions. It is not *vacuous* — it would catch a real one-sided edit, and the
  codebase has precedent for exactly this pattern
  (`test_a3_census.py:401` pins `FOCUS_OWNERS` against `_FOCUS_REGIONS`) — but that precedent guards
  two *independently motivated* structures, not a copy of one function.
- **Suggested fix:** `from tests.test_a3_census import renderer_classes, tracked` (the module already
  imports from that path at `:117`, so the import mechanics are proven), delete the two copies and the
  agree-arm. Arm count drops 33 → 32 and coverage is unchanged; the ledger and the `887` arithmetic
  move by the same 1. If the copy is kept deliberately, replace the docstring's rationale with the
  true one ("pinned equal on purpose; drift is a red arm").

---

### F6 — three of the five changed renderers are not views the operator can reach; the BLUF's `1 of 6 -> 6 of 6` overstates the delivered delta [Severity: LOW]

- **Where:** packet BLUF (*"The derived renderer set goes from 1 of 6 compliant to 6 of 6"*) against
  `mapper/app.py:49-56` and `:1193-1195`.
- **What:** `app.py` instantiates only `LayeredRenderer`, `OutlineRenderer`, `RadialRenderer`.
  `LaneRenderer`, `RailTimelineRenderer` and `HybridLaneRenderer` are exported from
  `mapper/views/__init__.py:2` and have **no production consumer anywhere** — executed,
  `grep -rn` for the three class names across every non-test `.py` returns only `lane.py` and
  `views/__init__.py`.
- **Why it matters:** the Statement's scope clause is *"in every view **the operator can reach**"*
  (`01-requirements.md:2754`). Deriving the wider set is right and I am not asking for it to be
  narrowed — but the operator-visible movement is `1 of 3 -> 3 of 3`, not `1 of 6 -> 6 of 6`, and the
  §3.4 width-clip investigation that shaped an arm was conducted on a renderer nobody can open. It
  also lowers the blast radius the `A-91` justification is priced against, which is worth stating
  correctly rather than leaving implied.
- **Suggested fix:** one sentence in the BLUF: *"three of the six (the lane family) have no production
  consumer today; the operator-reachable movement is 1 of 3 to 3 of 3."*

---

### F7 — a node that is both selected and a hit is indistinguishable from a selected non-hit, in all five renderers [Severity: LOW]

- **Where:** the five `if selected / elif hit` chains listed in F3.
- **What:** selection wins and paints `bold {GROUND} on {ACCENT}`, so the hit information is dropped
  for that node. Read strictly against *"paint the nodes carried in `state.hits` distinguishably from
  non-hit nodes"*, that node is not painted distinguishably.
- **Why it matters:** it is a real, if minor, gap against the Statement's literal wording. I am rating
  it LOW rather than blocking because it is (i) sane — the selection block is the stronger signal and
  the operator is already looking at that node, (ii) an exact match for shipped `layered` behaviour
  (`layered.py:628-647`), and (iii) **declared** by the packet at §10 with a request for a UX ruling.
  Behaviour is sane in all five: I verified each chain guards selection first, and radial additionally
  paints the marker with the selection block at `:246-247`.
- **Suggested fix:** none in this increment. Endorse the packet's §10 carry and route it to
  `ux-reviewer` for the ruling, noting that `layered`'s unfocused selection style is byte-identical to
  the hit style so the collision already exists in the one operator-reachable renderer that painted
  hits before today.

---

## Claims I checked and found TRUE

Recorded because the packet asked to be treated as claims, and these survived.

| Packet claim | Verdict | Evidence |
|---|---|---|
| The sealed `#D42` threshold does not catch a paint-everything renderer, and exactly one arm does | **TRUE, and it is the *only* arm** | I built both mutants myself. `MUT-B outline paint-everything: resolved=33 passed=32 red=1 -> the_paint_is_keyed_on_WHICH_node_is_a_hit[outline.OutlineRenderer]`; `MUT-C radial paint-everything: resolved=33 passed=32 red=1 -> ...[radial.RadialRenderer]`. The sealed threshold arm stayed GREEN on both. §3.2's table reproduces exactly. |
| The census pin `58 -> 59` is correct and the itemised reason is true | **TRUE** | Re-derived independently: `argful 59 zeroarg 26 defs 7`. The single new arg-ful site is `tests/test_views_hits.py:91`, which is `_spans_at` — one site, not six, exactly as `test_a3_census.py:185-190` states. |
| Default-lane ledger `887 passed, 17 deselected, 3 xfailed` | **TRUE** | `887 passed, 17 deselected, 3 xfailed in 205.72s`, one clean run on the pinned tree. Zero skips, which independently corroborates that F4's arm is not currently firing. |
| 33 arms in the new file, all green, resolved per node id | **TRUE** | `-rA --tb=no -q` resolved 33 named node ids, 33 `PASSED`, `33 passed in 0.25s`. Arm count asserted before the all-green was believed, per the instrument's own `C-57` lesson. |
| `A-91`: no data path | **TRUE** | The diff changes only `style=` arguments and adds one `hits = state.hits` binding per `render`. No store, no file I/O, no schema field, no persistence, no network. |
| `A-91`: no security sink — no file-derived text reaches a style | **TRUE** | `ViewState.hits` is `frozenset[str]` (`views/state.py:90`) and is used **only** in `in` membership tests at the six sites. Every style string is an f-string over `darkside.INK` / `STEP` / `GROUND` / `ACCENT` / `MUT`, which are module-level colour literals (`darkside.py:45-51`). No node id, title or meta is interpolated into any style. Title coercion (`darkside.plain` at `outline.py:125` and `radial.py:221`, `escape` in `lane.py`) is untouched by the diff. **No `C-17` markup/style sink is introduced — nothing to route to `security-reviewer`.** |
| `A-91`: no A3 contract change | **TRUE** | No `render` signature moved; `test_llr_n07_2_2a_*` and `test_llr_n07_2_3_every_renderer_signature_equals_graph_and_state` are green in the full run above, and `defs == 7` re-derived. |
| The style-equality arm is a real guard, not a tautology | **TRUE (analysed, not executed)** | `:255` takes the styles a hit *introduces* as a set difference, so a renderer that painted its hit style unconditionally somewhere else would introduce nothing and trip `assert all(introduced.values())` at `:258`; a renderer that drifted to a different style trips `every == {HIT_STYLE}` at `:262`. Guarded in both directions as claimed. `HIT_STYLE` at `:35` is spelled independently rather than imported from the renderers, which is the right call. |

## Things I attacked and could not break

- The derived-set guard (`:105-113`) — floor of 6, `_is_protocol` exclusion by flag not by name. Correct, and it is what stops all 30 parametrised arms going vacuous.
- The `text_differs` arm (`:139-152`). It is the right pin for `#D42`'s correction and it is not redundant with the spans arm.
- The trunk arm (`:217-234`). §3.3's account of why it exists checks out: with only the trunk's paint dead, the which-node arm compares "paints nothing" against "paints something", which still differ.
- Precedence against `layered`. §2's citation is accurate — `layered.py:628` is the "selection highlight on top" pass, and it does overwrite a hit. The five new chains order it the same way.
- Style token. `f"{darkside.INK} on {darkside.STEP}"` is the style `layered.py:539` already used. Not a new token, and §2.1's decision not to introduce a shared constant is sound on `C-50`'s own terms — a fourth spelling would have created a second home, and the drift is instead made observable.

---

## Evidence checklist

- [x] **Diff read in full** — `mapper/views/{outline,radial,lane}.py`, `tests/test_views_hits.py:1-264`, `tests/test_a3_census.py:178-194`, plus `mapper/canvas.py:103-105` and `mapper/views/layered.py:520-560,615-650` as read-only context.
- [x] **Correctness pass (edge / None / error paths)** — `hits` defaults to `frozenset()`; empty-hit renders are inert, which is what keeps the two style-sensitive golden observers (`test_repair_golden_census`, `test_export`) green. Both confirmed green in the full run. `radial.py:232`'s dead conjunct found here (F2).
- [x] **Simplicity pass** — F2 (inert conjunct), F5 (duplicated derivation). No premature abstraction found; §2.1's refusal to add a `HIT_STYLE` constant is the right call and is defended with the right reasoning.
- [x] **Reuse / duplication checked** — F5. The style token reuses `layered`'s spelling rather than inventing one.
- [x] **Tests reviewed for intent, not behaviour** — 8 mutants fired by me, 5 of which the packet's battery did not try; **4 survived** (F1 x3, F2, F3 x2 — MUT-A/D/E/F/G/H). Packet claims re-derived, not accepted.
- [x] **Security lane** — no `C-17` sink; nothing routed to `security-reviewer`.
- [x] **Tree restored** — all three sha256 pins match; `git status --porcelain` identical to entry.
- [x] **Verdict explicit** — below.

## Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **BLOCK — must fix the HIGH before advancing**

**HIGH count: 1 (F1).**

`A-91`'s lighter lane was conditional on this review returning zero HIGH. It did not, so **the full
protocol is restored for `Inc-5`**, including the confirmation pass.

**Minimum to clear the block:** add the F1 arm (multi-member hit set) and re-run the battery's
`min(hits)` shape against it — MUT-F/G/H must go from SURVIVED to KILLED. That is a tests-only change
and does not touch the sealed 3-file source cut, so the increment's `SOURCE FILE COUNT: 3` and the
`A-91` "no data path / no security sink / no A3 change" verdicts all still hold on the amended tree.

**Recommended in the same pass** (each is small, none blocks on its own): F2 delete the inert
conjunct and its false comment; F3 add the precedence arm; F4 turn the skip into an assert. F5 and F6
are cleanups; F7 is a carry for `ux-reviewer`.

**Note on the census pin.** F1, F3 and F5 all move `tests/test_views_hits.py`. F1's arm reuses
`_spans_at` (no new site); F3's arm needs `selected_id` — fold it into `_spans_at` as a defaulted
parameter rather than adding a second render helper, and the `59` pin does not move. F5, if taken,
removes no render call site either. Re-derive before believing that.
