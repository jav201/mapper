# Increment 5 — PASS 3, second confirmation on the round-3 tree (`LLR-N07.2.2b` / `AT-024`)

**Batch:** `2026-08-26-ui-next-batch-02` (SEALED) · **Increment:** `Inc-5`
**Confirming against:** `increment-005-code-review.md` (round 1, BLOCK, `F1` HIGH + `F2`-`F7`) and
`increment-005-code-review-confirmation.md` (round 2, BLOCK, `N1` HIGH + `N2` MEDIUM + `N3` LOW).
**Reviewed:** the UNCOMMITTED round-3 working tree at the six pinned sha256s, against `90e2a3f`.
**Reviewer:** independent of the implementer and of both prior reviewers. Harness built from scratch
for this pass; nothing was accepted on the strength of §12 having been written.

## Gate verdict

> **BLOCK — 2 HIGH surviving.**
>
> `N1` is **NOT DISCHARGED**. The exact shape round 2 named — *keep only the highest-sorted member* —
> **still survives at one of the six hit sites**, `mapper/views/lane.py:291` (`RailTimelineRenderer`'s
> `label_style`). It survives all 50 arms and the **entire 904-arm default lane, exit 0**, with a
> verdict set identical to clean.
>
> And the **next mirror is standing where round 2 predicted it would be**: no hit set of size ≥ 3 is
> rendered anywhere, so a renderer that paints only the two extremes of the hit set — dropping every
> middle member — survives at **all seven** renderer sites, also across the full lane.
>
> The pattern round 2 named has now produced its **third** instance in three rounds. It is no longer a
> finding about an instance; the report treats it as a finding about the *shape of the oracle*, and
> the recommended fix quantifies over the fixture's node set instead of naming members.

A single ~18-line replacement of one arm body closes both HIGHs and the MEDIUM below. It is
tests-only, does not move the arm count (50), does not move the census pin (59), and is **executed
below**: 25 of 25 non-equivalent mutants KILLED, the 3 residual survivors proven *equivalent* by
output digest.

---

## Entry / exit state

Pins asserted at entry, before every mutant, after every restore, and at exit:

```
06a0e9493f10bbc392bf4e175ee737f3ca1ef95cf10b996de139de7105325b39 *mapper/views/outline.py
aa462076e911c3983c4a02589094fbadd150fcfb6f1dab8d740b6fd7420f6d85 *mapper/views/radial.py
098b90b4baad538e9fda51be662a52f9354781e85085496153119d289ee602ef *mapper/views/lane.py
1e72dbdd4e94b772155f0bbd6f5bc0b4bbc1faf61169ff3e0dd23b693278d48b *tests/test_views_hits.py
8384ebfa42b47af6809b4fd9de81dbd450fa38f1d59ec2ae500035c033880e56 *tests/test_a3_census.py
3e081a6c61af9a20ec5ec94140e4258226fc0b692c65dea707701ba07c4015b5 *mapper/views/layered.py
--- git status --porcelain, identical to entry apart from THIS file ---
 M .dev-flow/state.json
 M mapper/views/lane.py
 M mapper/views/outline.py
 M mapper/views/radial.py
 M tests/test_a3_census.py
AM tests/test_views_hits.py
?? .dev-flow/.../increment-005-code-review.md
?? .dev-flow/.../increment-005-code-review-confirmation.md
?? .dev-flow/.../increment-005.md
```

**`mapper/views/layered.py` is byte-identical to `HEAD`** — §12.4's restoration claim is **TRUE**.
Verified two ways, because the naive check misleads on this tree: the worktree file is CRLF and the
index is LF (`core.autocrlf=true`), so `sha256(worktree) = 3e081a6c…` while
`sha256(git show HEAD:…) = 76fd432c…`. Normalised, both are `76fd432c88ca923f…`, `git diff HEAD` is
empty, and the file is absent from `git status`. Anyone re-checking this by comparing the two raw
digests will get a false alarm.

**Tree discipline.** Sole writer; the implementer had stopped. **59 mutants fired** plus 5 full-suite
runs. Every mutation was applied at the **byte** level to bytes read from disk and restored in a
`finally` from those exact bytes, with all six sha256 pins re-asserted before the next fired.
`__pycache__` purged on both sides of every mutation; `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUTF8=1`
in every child process. Mutants are described **by position and operation**, never pasted verbatim
(`C-56`). Anchors are **plain strings at a known occurrence index** — no multi-line regex — because
this tree mixes line endings (`lane.py` is LF; `outline.py`, `radial.py`, `layered.py` are CRLF), and
an anchor matching zero times is treated as **BAD**, raising rather than reporting a verdict. Harness
lives outside the repository (`C:\Users\jjgh8\clde\scratch\inc5_pass3\`).

**Instrument RED-proof (`C-57`), run before any verdict was believed.** The parser resolved **zero**
arms on its first run — pytest's ANSI colouring defeated the node-id pattern — and the arm-count
assertion caught it, which is the *fourth* instance of that shape in this batch. Fixed with
`--color=no`; the assertion is kept. Then a planted control:

```
BASELINE                                    resolved=50 passed=50 red=0 skipped=0
CONTROL outline hit branch made unreachable resolved=50 red=6   KILLED
```

Every verdict below is read from **resolved node ids**, never from an exit code, and the harness
raises unless it resolves exactly **50**.

---

## Finding-by-finding on the prior rounds

| Finding | Round | Disposition |
|---|---|---|
| `F1` / `N1` — the plural arm cannot see a dropped member | 1 / 2 | **NOT DISCHARGED** → `P1`, `P2` |
| `F2` — dead `and j` conjunct in `radial.py` | 1 | **DISCHARGED** |
| `F3` / `N2` — precedence unobserved; rail trunk unobserved | 1 / 2 | **DISCHARGED** |
| `F4` — precondition skipped where the docstring promised red | 1 | **DISCHARGED** |
| `F5` — copied derivation | 1 | **DISCHARGED** |
| `F6` — BLUF overstates the operator-reachable delta | 1 | **DISCHARGED** |
| `F7` — selected-and-hit is indistinguishable | 1 | **CARRIED, correctly declared** |
| `N3` — trunk `min` shape is an equivalent mutant | 2 | **CONFIRMED**, now proven numerically |
| `N4` — "nothing else" | 2 | **SUPERSEDED** — three surviving shapes found here |

### `F1` / `N1` — **NOT DISCHARGED.** See `P1` and `P2`.

The half that *is* discharged: `SHAPE-MIN` (keep only the lowest-sorted member) is now **KILLED at 6
of 7 sites**, each by exactly the plural arm for its own renderer. The seventh, the rail trunk, is an
**equivalent mutant** — proven below, not asserted. `SHAPE-MAX` is KILLED at 6 of 7. The seventh is
**not** equivalent and **not** killed; that is `P1`.

### `F3` / `N2` — **DISCHARGED**, and the third-slot question answered

All six precedence guard sites re-fired independently (selection guard gains a not-in-hits conjunct).
**6 of 6 KILLED**, the rail trunk among them:

```
INV outline.Outline      resolved=50 red=2  KILLED  (branch + trunk)
INV radial.Radial        resolved=50 red=2  KILLED  (branch + trunk)
INV lane.Lane            resolved=50 red=2  KILLED  (branch + trunk)
INV lane.Rail(TRUNK)     resolved=50 red=1  KILLED  (trunk arm only)
INV lane.Rail(label)     resolved=50 red=1  KILLED  (branch arm only)
INV lane.Hybrid          resolved=50 red=2  KILLED  (branch + trunk)
```

The two rail rows are the proof that the parametrisation is load-bearing rather than decorative: each
rail site is killed by exactly one slot, and neither slot alone would kill both.

**Is a third slot (`other`) a distinct path in any renderer?** **No.** There are exactly six hit
sites (`outline.py:130`, `radial.py:232`, `lane.py:133`, `:228`, `:291`, `:354`). `RailTimeline` is
the only renderer that splits, and it splits `branches[0]` from `branches[1:]` — so `other`
(`branches[2]`) traverses the same statement as `hit` (`branches[1]`). The two-slot parametrisation
reaches all six sites; a third slot would add zero statement coverage. **`N2` is fully closed.**

That answer, though, is exactly where this increment goes wrong one more time — see the closing note.

### `F2` — **DISCHARGED**

`radial.py:232` is a bare membership test; the conjunct is gone and the comment at `:233-244` states
what was measured rather than the claim that was false. I did not re-derive round 2's 225-configuration
byte-identity result — round 2 built that probe independently of round 1 and both reproduced, so a
third derivation buys nothing. I did confirm the mechanism from source: `Canvas.put` (`canvas.py:103-105`)
writes under one guard and the marker `put` at `radial.py:262` targets the same `(x, y)`, so the
second write always wins.

### `F4` — **DISCHARGED**

`tests/test_views_hits.py:190` is an `assert`; the `pytest.skip` is gone. **Zero skips** in every one
of my runs: 55 fifty-arm runs and 5 full-suite runs, all reporting `skipped=0`.

### `F5` — **DISCHARGED**

One import (`tests/test_views_hits.py:45`), no copy, no agree-arm. Census re-derived from
`render_call_sites()`: the module's only arg-ful site is `('tests/test_views_hits.py', 79)` — one
site, exactly as `test_a3_census.py:185-190` states.

### `F6` — **DISCHARGED**; `F7` — **CARRIED**

The `1 of 6 → 6 of 6` claim is now item 3 of §9's `⚠` supersession list, which is what round 2 asked
for. `F7` is declared in §10 and routed to `ux-reviewer`; behaviour unchanged, and consistent with
the precedence arm rather than in tension with it.

### `N3` — **CONFIRMED, and upgraded from argument to measurement**

Round 2 reasoned that the fixture's id ordering (`first` < `hit` < `other` < `root`) makes the trunk
permanently the lowest-sorted hit, so the `min` shape at that site is an *equivalent* mutant. I proved
it rather than accepting it — digest of `(hit set, plain, spans)` over all eight subsets of
`{first, hit, other}` at w=120, for `RailTimelineRenderer`:

```
SHIPPED trunk site                a741f792c85c81f1753a956fc588cd0198ae049532afe4fd831794fac9a63cfc
MIN     at the trunk site         a741f792…a9a63cfc   EQUIVALENT MUTANT
MINMAX  at the trunk site         a741f792…a9a63cfc   EQUIVALENT MUTANT
SORTED2 at the trunk site         a741f792…a9a63cfc   EQUIVALENT MUTANT
MAX     at the trunk site         bf17ad96…2caa556d   << differs: a REAL defect, and it is KILLED
```

`N3` is correct and its "no action required" disposition is right.

---

## NEW findings

### `P1` — `SHAPE-MAX` still SURVIVES at `lane.py:291`; `N1`'s minimum-to-clear was not met [Severity: **HIGH**]

- **What:** the shape round 2 named — the hit paint reduced to the **highest**-sorted member of the
  hit set — still survives at the `RailTimelineRenderer` `label_style` site.
- **Where:** the defect is invisible to `tests/test_views_hits.py:259-280`; the surviving site is
  `mapper/views/lane.py:291`.
- **Executed:**

```
MAX outline.Outline     resolved=50 red=1  KILLED
MAX radial.Radial       resolved=50 red=1  KILLED
MAX lane.Lane           resolved=50 red=1  KILLED
MAX lane.Rail(TRUNK)    resolved=50 red=1  KILLED
MAX lane.Rail(label)    resolved=50 red=0  *** SURVIVED ***
MAX lane.Hybrid         resolved=50 red=1  KILLED
MAX layered.Layered     resolved=50 red=1  KILLED

WHOLE DEFAULT LANE, same mutant:
  CLEAN                             exit=0  904 passed, 17 deselected, 3 xfailed
  SHAPE-MAX @ lane.py:291           exit=0  904 passed, 17 deselected, 3 xfailed   SURVIVED
```

- **It is not an equivalent mutant.** Direct behavioural probe, `RailTimelineRenderer` at w=120,
  counting spans carrying `HIT_STYLE`:

```
                              shipped        with the mutant
  hits={"first","other"}      33 / 33 OK     33 / 33 OK          <-- the pair the arm drives
  hits={"hit","other"}        48 / 48 OK     20 / 48  MEMBER DROPPED
  hits={"first","hit","other"} 61 / 61 OK    33 / 61  MEMBER DROPPED
```

  A two-member hit set — the exact cardinality the arm claims to cover — loses a member, and the arm
  is green.

- **Why it survives, which is the part that matters.** The arm renders exactly **one** plural hit set,
  `{"first", "other"}`. At `lane.py:291` the loop body only ever sees `branches[1:]`, because
  `branches[0]` (`"first"`) is routed through the *separate* `main_style` statement at `:228`. So
  inside this site's domain the "two-member" hit set degenerates to the singleton `{"other"}`, and
  `max` of a singleton is that singleton. The arm's plurality is real for five sites and fictional for
  the sixth.
- **Why it matters:** §12.3 records *"keep only the highest-sorted member | 6 | **6 KILLED** — the
  shape that survived round 2"*, and §12.4 records *"battery R3 18 fired / 18 KILLED"*. Both are true
  of the 18 mutants that were fired and **false as claims about the shape**, because the site that
  survived was not among them (see `P4`). Round 2's `Minimum to clear the block` was *"re-fire the
  `max(hits)` shape against all five changed renderers — SHAPE-MAX must go from SURVIVED to KILLED"*.
  Measured, it did not, at one of the six sites. Round 2's own SHAPE-MAX table had **seven** rows and
  listed `lane.RailTimeline(label)` explicitly; round 3 reported six.
- **Suggested fix:** the arm body under `P2`. Verified: it takes this mutant from SURVIVED to
  **KILLED**, reddening `..._EVERY_member_of_the_hit_set_is_painted[lane.RailTimelineRenderer]`.

### `P2` — the arm quantifies over a chosen PAIR, not over the hit set; no set of size ≥ 3 is ever rendered [Severity: **HIGH**]

- **What:** `test_llr_n07_2_2b_EVERY_member_of_the_hit_set_is_painted` drives exactly one plural hit
  set, of size 2, both of whose members are the extremes of the sort order. Any renderer that is
  correct on every subset of size ≤ 2 and wrong on size ≥ 3 is invisible to the whole repository.
- **Where:** `tests/test_views_hits.py:259-280`.
- **Executed** — two independent shapes, each fired at all seven sites:

```
MINMAX  (paint only min(hits) and max(hits); every middle member dropped)
  outline SURVIVED · radial SURVIVED · lane.Lane SURVIVED · rail(TRUNK) SURVIVED
  rail(label) SURVIVED · hybrid SURVIVED · layered SURVIVED          7 / 7 SURVIVED

SORTED2 (paint only the first two sorted members)
                                                                     7 / 7 SURVIVED

WHOLE DEFAULT LANE, MINMAX @ outline.py:130
  exit=0  904 passed, 17 deselected, 3 xfailed   SURVIVED (verdict set identical to clean)
```

- **Not equivalent, and the defect is the catalogued one.** `OutlineRenderer` under `MINMAX`:
  `hits={"first","hit","other"}` paints **2** of the 3 declared hits (`hits={"first","other"}` paints
  2 of 2 and is green). `01-requirements.md:2456-2458` is explicit that *"reporting a count a view
  does not paint is the error class this story exists to prevent"*, and `:2753` is plural with no
  cardinality bound — *"shall paint the **nodes** carried in `state.hits`"*. A count line declaring 3
  over a canvas painting 2 is that defect.
- **Why it matters:** the arm is *named* `EVERY_member_of_the_hit_set_is_painted` and its round-3
  docstring says the rule *"is now stated over the whole class instead of over one representative"*
  and *"closes both directions at once"*. Measured, it is stated over one representative **pair**.
  Under the rubric both prior rounds applied, a test whose stated guarantee exceeds what it can
  observe is false confidence, and a reader will take the class as closed. It is not.
- **Suggested fix** — replace the arm body (docstring unchanged except as noted); **no source file
  touched**, arm count stays 50, census pin stays 59 because every render still goes through
  `_spans_at`:

```python
    from itertools import combinations

    def hit_spans(spans):
        return {s for s in spans if s[2] == HIT_STYLE}

    # EVERY node this fixture can paint, not a chosen pair.  A pair names two
    # members; the property is universal over the set.  `root` is excluded
    # because the three lane renderers iterate branches and never draw it --
    # a hit on the root is a DECLARED but unpaintable hit there (`B-55`, §10).
    HITTABLE = ("first", "hit", "other")
    singles = {m: hit_spans(_spans_at(cls, 120, {m})[1]) for m in HITTABLE}
    # Non-vacuity: an empty `singles` would make every union below `set() == set()`.
    for m, sp in singles.items():
        assert sp, f"{cls.__name__} paints NO hit-styled span for {m}; the union below is vacuous"

    _, none = _spans_at(cls, 120, set())
    for k in (2, 3):
        for combo in combinations(HITTABLE, k):
            _, painted = _spans_at(cls, 120, set(combo))
            assert painted != none, f"{cls.__name__} paints nothing for {combo}"
            expected = set().union(*(singles[m] for m in combo))
            missing = {m for m in combo if not (singles[m] <= hit_spans(painted))}
            assert hit_spans(painted) == expected, (
                f"{cls.__name__} hits={combo}: painting is not the union of the "
                f"single-member paintings; dropped={sorted(missing)}"
            )
```

- **Executed against the fix, and this is the argument for it.** Baseline stays green (50 resolved, 0
  red — the fix does not false-fail the shipped tree; the 3-member union property was measured to hold
  on all six renderers before the fix was written). Then the whole battery re-fired:

```
                     MIN   MAX   MINMAX   SORTED2
  outline           KILL  KILL    KILL     KILL
  radial            KILL  KILL    KILL     KILL
  lane.Lane         KILL  KILL    KILL     KILL
  rail(TRUNK)       equiv KILL    equiv    equiv     <- the three `equiv` are PROVEN equivalent (N3)
  rail(label)       KILL  KILL    KILL     KILL
  hybrid            KILL  KILL    KILL     KILL
  layered           KILL  KILL    KILL     KILL

  28 fired · 25 non-equivalent · 25 KILLED · 0 SURVIVED · 3 equivalent by output digest
```

  It also kills `P1` and `P3`. Recommend adjusting the docstring's *"THE ASSERTION IS AN EQUALITY OVER
  DERIVED SETS"* paragraph to say the union is taken over **every** member of a set the arm enumerates
  in full, and dropping *"closes both directions at once"* in favour of what is actually observed.

### `P3` — the hit style at `lane.py:230` can drift undetected; §2.1's stated mitigation covers 5 of 6 sites [Severity: MEDIUM]

- **What:** changing the hit style at `RailTimelineRenderer`'s `main_style` (trunk) to a different
  style survives every arm in the repository.
- **Where:** `mapper/views/lane.py:230`, against `tests/test_views_hits.py:312-339`.
- **Executed** — the same drift fired at each of the seven hit-style literals, one site at a time:

```
DRIFT outline title          KILLED (the style arm)
DRIFT radial pill            KILLED (3 arms)
DRIFT lane.Lane title        KILLED (the style arm)
DRIFT rail TRUNK main_style  resolved=50 red=0   *** SURVIVED ***
DRIFT rail label_style       KILLED (the style arm)
DRIFT hybrid row name        KILLED (the style arm)
DRIFT layered card           KILLED (the style arm)

WHOLE DEFAULT LANE, DRIFT @ lane.py:230
  exit=0  904 passed, 17 deselected, 3 xfailed   SURVIVED
```

- **Why it matters:** §2.1 **rejects a shared `HIT_STYLE` constant** and defends the six inline
  spellings on the grounds that *"the duplication is instead made **observable**"* by
  `..._every_renderer_uses_THE_SAME_hit_style`. That arm derives the introduced style set per
  **renderer class**, driving `hits={"hit"}` — which is `branches[1]`, and therefore never reaches
  `main_style`. So the `C-50` mitigation the increment chose does not cover the site this increment
  newly authored. §9's `C-14` checklist line — *"The `HIT_STYLE` literal population is 6 sites,
  enumerated in §2.1 and guarded observably rather than deduped"* — is **false as measured: 5 of 6**.
- **This is also the union assertion's vacuity flank made concrete.** With the trunk drifted,
  `hit_spans(only_first)` is **empty** for `RailTimelineRenderer`, so the union assertion degenerates
  to `X == ∅ ∪ X` and passes for free. On the shipped tree it is *not* vacuous — measured, every
  renderer yields 1–20 hit-styled spans for each of the three renders — but nothing in the arm holds
  that true.
- **Rated MEDIUM, not HIGH, and here is the reasoning I want on the record.** I considered HIGH,
  because a control's stated guarantee exceeds what it observes — the same rubric that makes `P1` and
  `P2` HIGH. It lands lower for two measured reasons: the Statement (`:2754`) requires hits be painted
  *"distinguishably from non-hit nodes"*, which a **different** style still satisfies, so a drift here
  breaks the packet's own §2.1 decision rather than the requirement; and `RailTimelineRenderer` has no
  production consumer (`F6`), so it is not operator-reachable. It is a consistency defect with a false
  checklist claim attached, not a requirement defect.
- **Suggested fix:** the `P2` arm body already closes it — verified, `FIX + DRIFT rail TRUNK` goes
  **KILLED**, reddened by the non-vacuity guard. Correct §9's `C-14` line to say what is measured, or
  extend the style arm to drive a trunk hit as well.

### `P4` — the round-3 battery mutates per renderer CLASS where round 2 mutated per SITE, and that masks survivors [Severity: MEDIUM]

- **What:** §12.3's table is *"drop-a-member in both directions across all six renderers"* — six
  mutants per family. There are **six hit sites across five changed classes plus `layered`**;
  `RailTimelineRenderer` alone holds two (`lane.py:228` trunk and `:291` label). Round 2's own
  SHAPE-MAX table had seven rows and split them. Round 3 collapsed the split, and the site that
  survived is the one that disappeared.
- **Where:** `.dev-flow/.../increment-005.md:442-459` (§12.3) and `:461-469` (§12.4).
- **Executed — the masking is demonstrable, not inferred:**

```
MAX at the rail TRUNK site only        resolved=50 red=1  KILLED
MAX at the rail LABEL site only        resolved=50 red=0  *** SURVIVED ***
MAX at BOTH rail sites (per-CLASS)     resolved=50 red=1  KILLED     <-- reports a KILL over a survivor
```

  A per-class mutant is killed by whichever of its sites is observed, and says nothing about the
  others. This is `C-31` again — an incomplete input set — one level up from where §11.1 diagnosed it:
  the *mutant* population is now the incomplete set.
- **Why it matters:** §12.4's `battery R3 18/18 KILLED` is arithmetically true and is being read as a
  coverage claim it does not support. The correct denominator for the drop-a-member families is
  **7 sites**, not 6 classes; for the precedence family it is already 6 sites and §12.3 got that one
  right.
- **Suggested fix:** state the battery's denominator as **sites**, and re-fire per site. The seven
  hit sites are `outline.py:130`, `radial.py:232`, `lane.py:133`, `lane.py:228`, `lane.py:291`,
  `lane.py:354`, `layered.py:528`. Contributing cause: §2's heading (*"five call sites"*) and §2.1
  (*"Five new call sites spell the style inline"*) both undercount — §2's own table correctly gives
  `RailTimelineRenderer` two, and §9's `C-14` line says six. See `P6`.

### `P5` — the union assertion has no non-vacuity guard [Severity: LOW]

`hit_spans(both) == hit_spans(only_first) | hit_spans(only_other)` passes when all three are empty.
Measured, it is **not vacuous today** — every renderer yields hit-styled spans for every render the
arm makes (`HybridLane` 1/1/2, `Lane` 1/1/2, `RailTimeline` 13/20/33, `Layered` 20/20/40, `Outline`
1/1/2, `Radial` 11/10/21) — but that non-emptiness is only pinned indirectly, by a *different* arm at
a *different* width (80) driving a *different* node (`"hit"`). `P3` is the shape that exploits it.
One line, and it is already in the `P2` patch: `assert sp` per member.

### `P6` — the union assertion's soundness premise is pinned at the wrong width, and is fixture-dependent [Severity: LOW]

The docstring rests the assertion on rendered text being invariant under the hit set — *"the arm above
pins exactly that"*. That arm (`:122-134`) runs at **w=80** with `hits={"hit"}`; the union arm runs at
**w=120** with `{"first"}`, `{"other"}` and `{"first","other"}`. The premise is not pinned where it is
used.

**Measured, the premise is TRUE** — text invariance holds for all six renderers at both 80 and 120,
across eight hit sets (empty, each singleton, the pair, the triple, all four nodes, and an id absent
from the graph). But it is a property of the **fixture**, not of the renderers:
`mapper/views/layered.py:598-599` computes `n_hits` and appends `tail = f" {n_hits}"`, which **does**
move the rendered text with the hit set — it is unreachable here only because nothing in `_graph()` is
folded, so `geo.pill_ids` is empty. A future fixture with a folded branch would false-fail the
text-invariance arm and silently invalidate the union comparison's offset-comparability. Worth one
sentence in the docstring naming the dependency.

### `P7` — packet arithmetic: "five call sites" against six [Severity: LOW]

§2's heading and §2.1's first line both say **five**; §9's `C-14` line says **six**; §2's own table
correctly gives `RailTimelineRenderer` two sites. Six is right. This is cosmetic on its own and is
listed because it is the same per-class framing that produced `P3` and `P4`.

---

## Supersession discipline (§12's `⚠` list)

§12 correctly declares that the latest section governs and names three superseded round-1 claims, and
the third was added on round 2's nit — that discipline is real and it is working. Four further claims
in §§1-11 are now false and **unlisted**:

1. **§7's `A-91` table**, row *"review returns zero HIGH | **pending**"*. It is not pending: §9 and
   §11 record the lane REVOKED, and this pass makes it definitive.
2. **The BLUF's `battery : 9 mutants, 9 KILLED, 0 SURVIVED`** (`:21`). Item 2 of the `⚠` list names
   only the §9 checklist line carrying the same figure; the BLUF line is a second home for it.
3. **§3's *"33 arms … Six are the derived-set guards"*** (`:106-107`). Arms are 50, and there is
   **one** derived-set guard arm (`:92-103`); the "six" was already wrong in round 1.
4. **§11.8's `arms : 44`** — superseded to 50 by §12.4. Item 1 of the `⚠` list tracks the ledger
   numbers through all three rounds but not the arm count.

And newly false as of this pass, charged above rather than here: **§12.3's SHAPE-MAX row**
(`P1`), **§12.4's `battery R3 18/18` read as coverage** (`P4`), and **§9's `C-14` line** (`P3`).

---

## §12.4's figures — re-executed, not accepted

| §12.4 claim | My measurement | Verdict |
|---|---|---|
| `904 passed, 17 deselected, 3 xfailed` exit 0 | `904 passed, 17 deselected, 3 xfailed in 202.63s` exit 0 | **TRUE** |
| all markers `921 passed, 3 xfailed` exit 0 | `921 passed, 3 xfailed in 231.96s` exit 0 | **TRUE** |
| lane arithmetic `904 + 17 = 921` | holds | **TRUE** |
| `50 arms, zero skipped` | 50 resolved node ids asserted before every verdict; `skipped=0` in 55 arm-runs and 5 full-suite runs | **TRUE** |
| census `argful 59, zeroarg 26, defs 7` | re-derived from `render_call_sites()` / `render_definitions()`: `argful 59 zeroarg 26 defs 7`; the module's only arg-ful site is `('tests/test_views_hits.py', 79)` | **TRUE** |
| ruff SET `27 = 27`, zero NEW, zero GONE | `ruff check mapper tests` inside the repository = **27**. Per-path delta derived without leaving the repository, by feeding HEAD's blob through `ruff check --stdin-filename <path> -` so config resolves at the real path: all five touched paths report **0 findings on both the HEAD content and the working content**. Delta empty in both directions | **TRUE for this increment's delta** |
| `battery R3 18 fired / 18 KILLED` | true of the 18 fired; **not** true as a coverage claim — see `P1` / `P4` | **MISLEADING** |
| `layered.py` restored to HEAD exactly | `git diff HEAD` empty; normalised digests equal | **TRUE** |

**On the ruff methodology.** §12.5 adopts round 2's warning, and it is right: an export outside the
repository resolves an ancestor configuration enabling `I001`/`I002` (70 findings against 27). The
`--stdin-filename` route above avoids the trap without needing `git stash` or a second checkout — the
file never leaves the repository's path space, so config resolution is identical on both sides.

---

## Things I attacked and could NOT break

Recorded so the surviving shapes are not read as a general verdict on the tree.

- **Painting a non-member.** `nid in hits or (hits and nid == "hit")` — an extra node painted whenever
  the hit set is non-empty — is **KILLED at 6 of 7 sites**, and by the *precedence* arm, not the
  plural one: the precedence arm compares `hits=set()` against `hits={node}`, so any hit-set-triggered
  extra paint shows up. The seventh (rail trunk) is an equivalent mutant, the extra clause being
  unreachable there. This is the arm doing more than it advertises, and it is worth knowing.
- **Wrong style at the right spans** is caught at 6 of 7 sites (`P3` is the seventh).
- **A hit id absent from the graph** is inert in all six renderers — the render is identical to the
  empty-hit render. No crash, no partial paint.
- **The precedence arm's two slots** are both load-bearing (each rail site dies to exactly one), and
  no third slot is needed.
- **The union assertion's premise** (text invariance) holds, measured at both widths over eight hit
  sets — `P6` is about where it is pinned, not about whether it is true.
- **The 3-member union property holds on the shipped tree** for all six renderers, so the `P2` fix is
  green on today's code and closes a gap rather than exposing a defect.
- **No new defect in shipped behaviour.** As in both prior rounds: the six hit sites are pure
  membership tests over a `frozenset[str]`, every style is an f-string over `darkside` colour
  literals, no file-derived text reaches a style, no signature moved. `A-91`'s "no data path / no
  security sink / no A3 change" verdicts still hold, and there is nothing to route to
  `security-reviewer`.

**One observation for `B-55`, not a finding.** A hit on the map's **root** is declared but unpaintable
in all three lane renderers — measured, `hits={"root"}` yields 0 hit-styled spans in `LaneRenderer`,
`RailTimelineRenderer` and `HybridLaneRenderer` (against 20, 1 and 13 in `layered`, `outline` and
`radial`). That is `B-55`'s "a clipped hit is an undeclared hit" in a different guise, it predates
this increment, and §10 already carries `B-55` onward. It is also why the `P2` fix's node set excludes
`root` — including it would false-fail the lane family.

---

## Evidence checklist

- [x] **Diff read in full** — `mapper/views/{outline,radial,lane}.py` diffs end to end;
      `tests/test_views_hits.py:1-339` (all 50 arms); `tests/test_a3_census.py:176-197`;
      `mapper/views/layered.py:485,525-545,588-608,636-652` and `mapper/canvas.py:103-105` as
      read-only context; `01-requirements.md:2452-2458` and `:2750-2758`; both prior reviews and
      `increment-005.md` §§1-12 in full.
- [x] **Both drop-a-member shapes re-fired at every site** — `MIN` 7/7 (6 KILLED + 1 proven
      equivalent); `MAX` 7/7 (6 KILLED, **1 SURVIVED**, `P1`). Fired **per site**, not per class.
- [x] **The next mirror constructed and found** — `MINMAX` and `SORTED2`, 7/7 SURVIVED each, plus a
      full-lane confirmation (`P2`). Non-member painting, ghost ids and all-nodes hit sets also
      driven.
- [x] **The union assertion's soundness audited** — text invariance measured at w=80 and w=120 over
      eight hit sets on all six renderers (holds); `hit_spans` non-emptiness measured (holds today,
      unguarded — `P5`); the fixture-dependence of the premise identified (`P6`).
- [x] **Six precedence inversions re-fired, trunk included** — 6/6 KILLED; third slot shown to add no
      statement coverage (`N2` closed).
- [x] **§12's figures re-executed** — 4 full-suite runs; census and ruff re-derived inside the
      repository; `layered.py` byte-identity to HEAD confirmed past the CRLF/LF trap.
- [x] **Supersession discipline audited** — four further stale claims named.
- [x] **The recommended fix executed, not proposed** — 28 mutants under the fix, 25 non-equivalent,
      **25 KILLED**, baseline stays green at 50 resolved / 0 red.
- [x] **Verdicts per resolved node id, arm count asserted first** — 50 asserted before any all-green
      was believed; the harness raises on any other count, and it fired (zero arms resolved under
      ANSI colouring) before it reported anything true.
- [x] **Tree restored** — six sha256 pins matched after the last restore; `git status --porcelain`
      identical to entry apart from this file; `__pycache__` purged; `layered.py` identical to HEAD.
- [x] **Verdict explicit** — below.

## Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **BLOCK — must fix the HIGH findings before advancing**

**HIGH findings surviving: 2** (`P1`, `P2` — one root cause, one fix).
**New findings raised: 7** (`P1` HIGH, `P2` HIGH, `P3` MEDIUM, `P4` MEDIUM, `P5` LOW, `P6` LOW,
`P7` LOW).
**Prior HIGH `F1`/`N1`: NOT DISCHARGED.**

**Minimum to clear the block:** replace the body of
`test_llr_n07_2_2b_EVERY_member_of_the_hit_set_is_painted` with the quantified form under `P2` (it
carries `P5`'s non-vacuity guard and closes `P3` as a side effect), and re-fire the drop-a-member
families **per site** — seven sites, not six classes. Tests only; the sealed `SOURCE FILE COUNT: 3`
and every `A-91` source verdict are unaffected, the arm count stays 50, and the census pin stays 59.

**Recommended in the same pass:** `P4` — restate the battery denominator as sites and re-run it that
way; `P3` — correct §9's `C-14` line to the measured 5-of-6, or extend the style arm to drive a trunk
hit; `P6`/`P7` — two sentences. `P5` is already inside the `P2` patch.

**A fourth pass is warranted, and this is what it should test.** Round 2 named the pattern precisely
— *a correct fix to the exact mutant that was named, with the mirror left standing* — and round 3
then reproduced it a third time, in the arm written to close it. The mechanism is now visible and is
worth stating so the next round can be aimed rather than repeated: **each round has generalised along
the axis it was shown and stopped there.** Round 2 was shown a *member* (`min`) and generalised to
*the other member* (`max`). Round 3 was shown a *statement* (the rail trunk, in the precedence arm)
and generalised the precedence arm to *slots*, correctly — while leaving the plural arm quantified
over two named members. The plural arm needed the same lesson the precedence arm just learned, in its
own currency: the precedence arm needed `first` because it is a different **statement**; the plural
arm needs `hit` because it is a different **member of the same statement's domain**. A fourth pass
should therefore check the *form of the oracle*, not one more instance — an assertion that names
specific inputs is the defect; an assertion quantified over an enumerated set is the fix — and should
fire its battery **per site**, since `P4` shows a per-class battery reports a KILL over a live
survivor.
