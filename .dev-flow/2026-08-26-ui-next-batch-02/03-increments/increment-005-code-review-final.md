# Increment 5 — FINAL confirmation pass, scoped to `Q1`'s axis

**Batch:** `2026-08-26-ui-next-batch-02` (SEALED) · **Increment:** `Inc-5`
**Auditing:** the round-5 working tree (§15 fold) against pass 4's `Q1` — *the DOMAIN the oracle
quantifies over, and root inclusion per renderer family.*
**Scope:** strictly `Q1`'s axis, under the coordinator's **terminal boundary**.
**Reviewer:** independent of the implementer and of all four prior reviewers. Harness built from
scratch outside the repository; nothing accepted on the strength of §15 or pass 4 having been written.

## Gate verdict

> **PASS — 0 HIGH on `Q1`'s axis.**
>
> `Q1` is **closed**, and closed by the mechanism §15.1 claims. The domain is genuinely derived —
> no literal member list survives anywhere in the arm. The floor is right. The `B-55` boundary is
> sound per family at the width it is used, and it is **the sole catcher** of the drop-`root` defect:
> I defeated the boundary assertion and watched all three previously-killed mutants come back to life,
> which is pass 4's absorption warning demonstrated rather than repeated. 42 fired / 35 KILLED /
> 7 equivalent reproduces **exactly**, survivor-for-survivor, on an independent instrument. Every
> §15.3 figure is TRUE.
>
> **And I found one thing outside `Q1`'s axis**, at the next quantifier out: **width**. The arm derives
> `singles` at w=120 only, and the sibling arms that backstop the members the boundary does not
> guard run at **w=80**. A defect that drops `first` or `hit` only at w ≥ 100 is therefore *absorbed*
> by the derivation and *unseen* by the siblings. Fired at `radial.py:232`: both shapes **survive all
> 50 arms and the entire 904-arm default lane, exit 0**, and both are proven **non-equivalent** by
> output digest. `other` and `root` at the same site are KILLED — because those two are the only
> members with a w=120 observation outside the absorbing arm.
>
> This is **outside `Q1`** and it does not block. `Q1` was a *flat* drop of a hand-named member; the
> domain axis is closed against every flat drop I could construct (21 fired, 18 KILLED, 3 proven
> equivalent). The residue needs a *second* quantifier — width — to become live. Per the terminal
> boundary the renderer changes commit as-is and this becomes the split micro-increment's charter,
> stated in §7 below **with its fix already executed and green**.

---

## Entry / exit state

Six pins asserted at entry, before every mutant, after every restore, and at exit. All matched the
values in the dispatch, unchanged:

```
06a0e9493f10bbc392bf4e175ee737f3ca1ef95cf10b996de139de7105325b39 *mapper/views/outline.py
aa462076e911c3983c4a02589094fbadd150fcfb6f1dab8d740b6fd7420f6d85 *mapper/views/radial.py
098b90b4baad538e9fda51be662a52f9354781e85085496153119d289ee602ef *mapper/views/lane.py
316cb19d2ffaacb0432a922b3126d6588c36eb9754e5d3d04b215463d5e4e37a *tests/test_views_hits.py
8384ebfa42b47af6809b4fd9de81dbd450fa38f1d59ec2ae500035c033880e56 *tests/test_a3_census.py
3e081a6c61af9a20ec5ec94140e4258226fc0b692c65dea707701ba07c4015b5 *mapper/views/layered.py
--- git status --porcelain, identical to entry apart from THIS file ---
```

**`mapper/views/layered.py` is byte-identical to `HEAD`.** Verified past the CRLF/LF trap three ways:
`git diff HEAD -- mapper/views/layered.py` empty; the file absent from `git diff HEAD --name-only`;
normalised digests equal (`worktree 3e081a6c…` raw, `HEAD 76fd432c…` raw, **both `76fd432c…`
normalised**). Round 5's restoration claim is **TRUE**.

**Tree discipline.** Sole writer. **75 mutants fired** (63-shape battery, 5 absorption probes, 3
boundary-defeat probes, 4 fix-proof probes) plus 5 full-suite lanes, 1 planted control, and 3
read-only render probes. Every mutation applied at the **byte** level to bytes captured once at
harness import and restored in a `finally` from those exact bytes; all six pins re-asserted before
the next fired. `__pycache__` purged on both sides of every mutation; `PYTHONDONTWRITEBYTECODE=1` and
`PYTHONUTF8=1` in every child process. Anchors are **plain strings at a known occurrence index** —
`elif bid in hits:` occurs three times in `lane.py` with identical indentation (S3/S5/S6), and the
harness raises **BAD** rather than reporting a verdict if an anchor's occurrence count is below its
index. Mutants described by **position and operation**. Harness outside the repository
(`C:\Users\jjgh8\clde\scratch\inc5_final\`).

**Instrument RED-proof (`C-57`), run before any verdict was believed.**

```
BASELINE                            resolved=50 counts={'PASSED': 50} rc=0   skipped=0
CONTROL outline hit branch dead     resolved=50 red=6   KILLED
```

Every verdict is read from **resolved node ids** with `--color=no`; the harness raises unless it
resolves exactly **50**. It raised zero times across all 75 fires.

**Anchor → line resolution, asserted rather than assumed** (independently re-derived; matches pass 4):

```
S1 outline.py cond->130  style->136     S5 lane.py    cond->291  style->294
S2 radial.py  cond->232  style->245     S6 lane.py    cond->354  style->357
S3 lane.py    cond->133  style->138     S7 layered.py cond->528  style->539
S4 lane.py    cond->228  style->230
```

---

## 1 · Is the domain genuinely derived, and is the derivation trustworthy?

**Derived: yes, genuinely.** `tests/test_views_hits.py:282-284` binds `ALL` as the fixture's four node
ids, computes `singles[m]` by **rendering** each single-member hit set, and takes `hittable` as the
members that produced a hit-styled span. `HITTABLE` is gone; no literal member list survives inside
the quantifier. The measurement reproduces pass 4's table exactly, and I extended it to three widths:

```
w=120                       root  first   hit  other   hittable                       "Raiz del mapa" in drawn
outline.OutlineRenderer        1      1     1      1    ('root','first','hit','other')  True
radial.RadialRenderer         13     11    18     10    ('root','first','hit','other')  True
layered.LayeredRenderer       20     20    20     20    ('root','first','hit','other')  True
lane.LaneRenderer              0      1     1      1    ('first','hit','other')         False
lane.RailTimelineRenderer      0     13    28     20    ('first','hit','other')         False
lane.HybridLaneRenderer        0      1     1      1    ('first','hit','other')         False
```

**Trustworthy against the absorption pass 4 warned about — for `root`, and by exactly the claimed
mechanism.** Fired per site, membership narrowed to exclude the root:

```
NOROOT  S1 outline.py:130    resolved=50 red=1  KILLED
NOROOT  S2 radial.py:232     resolved=50 red=1  KILLED
NOROOT  S7 layered.py:528    resolved=50 red=1  KILLED
NOROOT  S3/S4/S5/S6          resolved=50 red=0  survives  (proven equivalent, §4)
```

**The boundary assertion is what fires**, and it says so in its own words. The failing node id and
assertion, read off the run:

```
tests/test_views_hits.py::test_llr_n07_2_2b_EVERY_member_of_the_hit_set_is_painted[outline.OutlineRenderer]
>       assert ("root" in hittable) == ("Raiz del mapa" in drawn), (
E       AssertionError: OutlineRenderer draws the root (True) but paints a root hit (False);
E                       a DRAWN node that is a declared hit must be painted -- see B-55
```

Identical shape at `radial.RadialRenderer` and `layered.LayeredRenderer`. **One arm reddens, and it is
the right one.**

**Is it the SOLE catcher, or does something else catch it?** I answered this by defeating the
assertion rather than reasoning about it — rewriting the boundary predicate into a tautology
(comparing the derived side with itself) and re-firing the same three mutants:

```
boundary DEFEATED, shipped source     red=0   (the defeat itself does not redden -- control)
boundary DEFEATED + NOROOT S1         red=0   *** SURVIVED -- the boundary is the SOLE catcher ***
boundary DEFEATED + NOROOT S2         red=0   *** SURVIVED -- the boundary is the SOLE catcher ***
boundary DEFEATED + NOROOT S7         red=0   *** SURVIVED -- the boundary is the SOLE catcher ***
```

**Nothing else in the repository catches it.** §15.1's claim that a bare derivation would *absorb*
the defect is not an argument in a docstring — it is a measured property of this tree, and the
boundary assertion is the whole of what stands between the arm and vacuity on the root.

**Generalised: does the derivation absorb a drop of the OTHER three members?** Inside this arm, yes —
and every such shape is nonetheless killed elsewhere in the file. Fired per site as three extra
shapes beyond the required six:

```
                    NOFIRST  NOHIT   NOOTHER
  S1 outline.py:130   KILL    KILL    KILL
  S2 radial.py:232    KILL    KILL    KILL
  S3 lane.py:133      KILL    KILL    KILL
  S4 lane.py:228      KILL    surv    surv     <- trunk is `first`; the others cannot act (equivalent)
  S5 lane.py:291      surv    KILL    KILL     <- label path is branches[1:]; `first` cannot act (equivalent)
  S6 lane.py:354      KILL    KILL    KILL
  S7 layered.py:528   KILL    KILL    KILL

  21 fired · 18 KILLED · 3 survivors, all three proven EQUIVALENT by digest (§4)
```

The catchers are the sibling arms — `..._a_hit_on_the_FIRST_branch_is_painted_too` for `first`, the
sealed threshold and `..._keyed_on_WHICH_node...` for `hit`, `..._a_hit_outside_the_first_branch...`
for `other`. **Zero flat drop-a-member survivors anywhere in the tree.** The domain axis is closed.

That delegation is where the residue lives, and it is a *width* seam rather than a domain seam — §7.

## 2 · Is the floor (`>= 3`) right?

**Yes, and it does not false-fail.** Measured at the width the arm uses, `len(hittable)` is
**3, 3, 3, 4, 4, 4** across the six renderers — every one at or above the floor, none at risk.

- **Could a renderer legitimately paint fewer than 3 and be failed wrongly?** Not at w=120. It *can*
  at w=80 — `RailTimelineRenderer` derives `('first','hit')` there, because `max_label` clips the
  third branch to nothing (the mechanism `..._a_hit_outside_the_first_branch...` already records).
  The arm never renders at 80, so this is not live. And if a future change ever clipped the third
  branch at 120, **two** arms redden with messages that name the clip — the floor here, and that
  sibling's `assert title in plain` precondition, which was deliberately converted from a `skip` to an
  assert for this reason. It fails loud, which is the right behaviour.
- **Could a renderer paint 3 while dropping one and pass?** For the lane family, **no** — they sit at
  exactly 3, so any drop takes them to 2 and trips the floor. For `outline`/`radial`/`layered`, which
  sit at 4, **yes structurally**: a drop leaves 3 and the floor is satisfied. That is not a defect in
  the floor — a non-vacuity floor is not a drop-detector, and it does not claim to be — but it does
  mean the four-member renderers are guarded **only** by the boundary (root) and by the sibling arms
  (the other three). That asymmetry is the door the §7 finding walks through.

The floor is correctly documented as *"a FLOOR, not a filter"* and correctly placed **before** the
unions. No finding.

## 3 · Is the `B-55` boundary assertion correct per family?

**Yes — sound for all six renderers at the width it is used, and I checked the failure mode the
literal invites rather than only the value it returns.**

The risk in a literal proxy is truncation: a renderer that *draws* the root under a clipped title
would report `False`, permit `root` to leave `hittable`, and absorb exactly the defect the assertion
exists to catch. Measured as the **longest prefix of `"Raiz del mapa"` present in the no-hit plain
text**, at three widths:

```
                            w=80    w=100   w=120
  outline.OutlineRenderer   13/13   13/13   13/13   full title, no clipping regime
  radial.RadialRenderer     13/13   13/13   13/13   full title
  layered.LayeredRenderer   13/13   13/13   13/13   full title
  lane.LaneRenderer          0/13    0/13    0/13   not even a one-character prefix
  lane.RailTimelineRenderer  0/13    0/13    0/13   not even a one-character prefix
  lane.HybridLaneRenderer    0/13    0/13    0/13   not even a one-character prefix
```

The lane family's `False` is **not** a truncation artefact — the root's title does not reach the
canvas at all, in any prefix form, at any width in the batch's declared range. And the three
renderers that do draw it draw it whole, with no clipping regime anywhere near 120. So
`"Raiz del mapa" in drawn` is a faithful proxy for *"this renderer draws the root"* on all six today,
and the equality holds in both directions with zero mismatches. `B-55` is being cited where it is
**true** — the lane renderers iterate branches, never draw the root, and a root hit is
declared-but-unpaintable there — which is the mis-route pass 4 named, corrected.

Reading the boundary off the rendered text rather than off a list of class names is also the right
call structurally: a renderer that changed family would change what the assertion expects of it
automatically. **No finding.**

## 4 · The battery, re-fired — 42 fired / 35 KILLED / 7 equivalent

**Reproduced exactly, and survivor-for-survivor**, on an independent harness, verdicts per resolved
node id:

```
                        MIN     MAX    MINMAX  SORTED2  DRIFT   NOROOT
  S1 outline.py:130     KILL    KILL    KILL    KILL    KILL    KILL
  S2 radial.py:232      KILL    KILL    KILL    KILL    KILL    KILL
  S3 lane.py:133        KILL    KILL    KILL    KILL    KILL    surv
  S4 lane.py:228        surv    KILL    surv    surv    KILL    surv
  S5 lane.py:291        KILL    KILL    KILL    KILL    KILL    surv
  S6 lane.py:354        KILL    KILL    KILL    KILL    KILL    surv
  S7 layered.py:528     KILL    KILL    KILL    KILL    KILL    KILL

  42 fired · 35 KILLED · 7 survivors · resolved=50, skipped=0 on every run
```

The survivor set is **identical** to §15.2's: `NOROOT` at S3/S4/S5/S6 and `MIN`/`MINMAX`/`SORTED2` at
the S4 trunk. `NOROOT` is KILLED at exactly the three sites where it survived every arm and the whole
904-arm lane before round 5.

**All seven independently re-proven equivalent by output digest, over a domain larger than either
prior pass used** — 6 renderers × 16 subsets of the four nodes × 3 widths (80/100/120) × 3 selections
(`None`, `first`, `root`) = **864 renders per digest**, hashing `(renderer, w, selection, hit set,
plain, spans)`. The three extra drop-member survivors from §1 are proven the same way. Four positive
controls, one per affected site, **must** differ:

```
SHIPPED                                       1577d686d8b30b86

  survivor NOROOT   S3 lane.py:133            1577d686d8b30b86  EQUIVALENT
  survivor MIN      S4 lane.py:228 (trunk)    1577d686d8b30b86  EQUIVALENT
  survivor MINMAX   S4 lane.py:228 (trunk)    1577d686d8b30b86  EQUIVALENT
  survivor SORTED2  S4 lane.py:228 (trunk)    1577d686d8b30b86  EQUIVALENT
  survivor NOROOT   S4 lane.py:228 (trunk)    1577d686d8b30b86  EQUIVALENT
  survivor NOHIT    S4 lane.py:228 (trunk)    1577d686d8b30b86  EQUIVALENT
  survivor NOOTHER  S4 lane.py:228 (trunk)    1577d686d8b30b86  EQUIVALENT
  survivor NOFIRST  S5 lane.py:291            1577d686d8b30b86  EQUIVALENT
  survivor NOROOT   S5 lane.py:291            1577d686d8b30b86  EQUIVALENT
  survivor NOROOT   S6 lane.py:354            1577d686d8b30b86  EQUIVALENT

  control  MAX      S3 lane.py:133            c56ee9e2dbbf8994  DIFFERS
  control  MAX      S4 lane.py:228 (trunk)    16b47a7fc4c1f942  DIFFERS
  control  MAX      S5 lane.py:291            01f3a85f3d0e7c0d  DIFFERS
  control  MAX      S6 lane.py:354            4a7f45464975089c  DIFFERS

  unexpected = []
```

**All ten equivalences hold; all four controls fire.** The probe is not blind, and §15.2's equivalence
claim is honest — the four `NOROOT` equivalences are `B-55` holding exactly where it is true,
measured per site rather than asserted per family.

## 5 · §15.3's figures — re-executed, not accepted

| §15.3 claim | My measurement | Verdict |
|---|---|---|
| default lane `904 passed, 17 deselected, 3 xfailed` exit 0 | `904 passed, 17 deselected, 3 xfailed in 207.26s` exit 0 | **TRUE** |
| all markers `921 passed, 3 xfailed` exit 0 | `921 passed, 3 xfailed in 230.30s` exit 0 | **TRUE** |
| lane arithmetic `904 + 17 = 921` | holds | **TRUE** |
| `50 arms, zero skipped` | 50 resolved node ids asserted before **every** one of 75 verdicts (the harness raises on any other count); `skipped=0` measured at baseline and on every fire | **TRUE** |
| ruff SET `27 = 27`, zero NEW, zero GONE | `ruff check mapper tests` **inside** the repository = **27 errors**. Per-path delta via `--isolated --stdin-filename <path> -` on **both** sides: all six touched paths report **0 findings** on HEAD content and on working content (`test_views_hits.py` is new at HEAD). Delta empty in both directions | **TRUE** |
| census `argful 59, zeroarg 26, defs 7` | re-derived from `render_call_sites()` / `render_definitions()`: `argful 59, zeroarg 26, defs 7` | **TRUE** |
| battery `42 fired, 35 KILLED, 7 proven equivalent` | reproduced exactly, per site, survivor-for-survivor, on an independent harness; all 7 equivalences re-proven over 864 renders with positive controls that fire | **TRUE** |
| `layered.py` restored to HEAD exactly | `git diff HEAD` empty; absent from `--name-only`; normalised digests equal | **TRUE** |
| arm count unchanged at 50, census pin unchanged at 59 | both measured unchanged | **TRUE** |

**One qualification, the same one pass 4 attached and it still applies one level out.** `35 KILLED, 7
proven equivalent` is true of the **six shapes fired**. It is not a coverage claim about every
drop-shaped defect — §7 is what that costs, now on the width quantifier rather than the domain one.

## 6 · Things I attacked and could NOT break

- **The derivation.** Genuinely derived; no literal member list inside the quantifier. `hittable`
  reproduces the measured paint on all six renderers at all three widths.
- **The boundary assertion.** Real, correct per family, sound as a proxy at 120 with no truncation
  regime anywhere near it, and **the sole catcher** of drop-`root` — proven by defeating it and
  watching three KILLs revert to SURVIVED.
- **The floor.** Correct at the width used; no false-fail available; fails loud in the one direction
  it could ever be wrong, and a sibling arm's precondition reddens alongside it.
- **The cardinality quantification.** `k in range(2, len(hittable)+1)` is exhaustive over the derived
  domain — sizes 2/3/4 for the three four-member renderers, 2/3 for the lane family. No gap.
- **The non-vacuity guard.** Load-bearing; it is what kills the trunk `DRIFT` at `lane.py:230`.
- **The per-site denominator.** Seven; every anchor resolved to exactly the line claimed.
- **Flat drop-a-member, all four members × all seven sites.** 28 fires between `NOROOT` and the three
  extra shapes; **zero real survivors**, seven proven equivalent.
- **Every §15.3 figure.** Re-executed independently; all TRUE.
- **No new defect in shipped behaviour, for the fifth round running.** The seven hit sites remain pure
  membership tests over a `frozenset[str]`; every style is an f-string over `darkside` colour
  literals; no file-derived text reaches a style; no signature moved. `A-91`'s "no data path / no
  security sink / no A3 change" verdicts hold; **nothing to route to `security-reviewer`.** The
  finding below is a defect in the oracle, not in the renderers.

---

## 7 · OUTSIDE `Q1`'s axis — the charter for the split micro-increment

### `W1` — the derivation and its backstops are evaluated at DIFFERENT WIDTHS, so a width-conditioned drop of `first` or `hit` is absorbed and unseen [Severity: **HIGH**, **non-blocking** under the terminal boundary]

- **What.** The arm derives `singles` at **w=120** only. The `B-55` boundary re-externalises that
  derivation for **`root` alone**. The other three members are backstopped by sibling arms, and those
  run at a **different width**:

```
  member   pinned OUTSIDE the absorbing arm by                              at width
  root     the B-55 boundary, inside this arm but read off `drawn`            120
  other    ..._a_hit_outside_the_first_branch_is_painted_too                  120
  first    ..._a_hit_on_the_FIRST_branch_is_painted_too / ..._keyed_on_WHICH   80
  hit      the sealed threshold / ..._keyed_on_WHICH / ..._SAME_hit_style      80
```

  (`..._selection_is_painted_ON_TOP_of_a_hit` runs at 120 but asserts `sel_and_hit == sel_only` —
  *sameness* — so it cannot see a dropped paint and is not a backstop.)

  So for `first` and `hit` there is **no observation at 120 outside the arm that absorbs them**. A
  defect that drops one of those members only at w ≥ 100 falls out of `hittable`, leaves
  `len(hittable) == 3` (floor satisfied), leaves the boundary untouched (it speaks only of `root`),
  and the unions then quantify over a domain the defect has already emptied.

- **Where.** The oracle: `tests/test_views_hits.py:282-284` (derivation at 120) and `:302-307` (the
  boundary, scoped to `root`). The surviving site: `mapper/views/radial.py:232` — the only one of the
  seven whose enclosing closure (`tag()`, defined at `radial.py:180`, inside `render` which binds
  `w` at `:109`) has the width in scope, so the shape is expressible at a **real shipped site**.

- **Executed.** Membership narrowed to drop one member only when the canvas is 100 columns or wider:

```
  WIDE-DROP first (w>=100)  S2 radial.py:232   resolved=50 red=0  *** SURVIVED ***
  WIDE-DROP hit   (w>=100)  S2 radial.py:232   resolved=50 red=0  *** SURVIVED ***
  WIDE-DROP other (w>=100)  S2 radial.py:232   resolved=50 red=1      KILLED
  WIDE-DROP root  (w>=100)  S2 radial.py:232   resolved=50 red=1      KILLED
  flat-DROP first (control) S2 radial.py:232   resolved=50 red=1      KILLED

  WHOLE DEFAULT LANE:
    CLEAN                            exit=0  904 passed, 17 deselected, 3 xfailed
    WIDE-DROP first @ radial.py:232  exit=0  904 passed, 17 deselected, 3 xfailed   SURVIVED
    WIDE-DROP hit   @ radial.py:232  exit=0  904 passed, 17 deselected, 3 xfailed   SURVIVED
```

  **The kill/survive split maps one-to-one onto the table above** — `other` and `root` die because
  they have a 120 observation; `first` and `hit` survive because they do not; the flat drop dies
  because the 80 sibling sees it. That is the diagnosis confirmed by construction, not inferred.

- **Both are REAL defects, not equivalent mutants** — output digest over 864 renders, with `MAX` as
  the positive control:

```
  SHIPPED            1577d686d8b30b86
  WIDE-DROP first    82a4173538e94d61   DIFFERS  REAL DEFECT
  WIDE-DROP hit      b5e891f4e3a5a4e1   DIFFERS  REAL DEFECT
  MAX (control)      3af1b7425b3ce427   DIFFERS  <- control fires
```

- **Why it matters.** `radial` is one of the three operator-reachable renderers (`F6`), it already
  performs width-dependent layout, and this file's own history records a width-conditioned paint
  discovery — `..._a_hit_outside_the_first_branch...` exists because the third branch is invisible
  below 100 columns. A real terminal is far more often ≥ 100 wide than 80, so the surviving shape
  bites in the **common** regime and is silent in the one the siblings observe. That is
  `AT-024`'s catalogued error class exactly — a view reporting a count it does not paint — reachable
  from an ordinary search, and green across 904 arms.

- **Why it is OUTSIDE `Q1`.** `Q1` was a *flat* drop of a *hand-named* member, and that axis is
  closed: 28 flat drop-a-member fires, zero real survivors, and the boundary proven to be the sole
  and sufficient catcher for `root`. `W1` needs a **second** quantifier the review ladder has not
  reached — **width** — and it is unreachable by any flat shape. The ladder recorded in §15.4 gains
  one rung: the assertion's inputs → the battery's sites → the assertion's cardinality → the domain
  quantified over → **the width at which the domain is measured**.

- **Charter, with the fix already executed and green.** Generalise the boundary from one member to
  all four, so every member is re-externalised against what the renderer draws rather than only the
  root. Tests only; no source file touched; arm count stays 50; census pin stays 59. Two edits inside
  `test_llr_n07_2_2b_EVERY_member_of_the_hit_set_is_painted`, replacing the root-scoped boundary:

```python
    drawn, _ = _spans_at(cls, 120, set())
    TITLES = {"root": "Raiz del mapa", "first": "Presupuesto",
              "hit": "analisis de riesgo", "other": "Cronograma"}
    # Asserted for EVERY member, not just the root: the derivation above reads
    # `hittable` off the paint, so any member a renderer stops painting silently
    # leaves the domain.  The boundary is the anti-absorption device and it has
    # to cover everything the derivation can drop -- the sibling arms that
    # backstopped `first` and `hit` run at w=80 and cannot see a drop that only
    # bites at 120.  Measured: a w>=100 drop of `first` or `hit` at
    # `radial.py:232` survived all 50 arms and the whole 904-arm lane.
    for _m in ALL:
        assert (_m in hittable) == (TITLES[_m] in drawn), (
            f"{cls.__name__} draws {_m} ({TITLES[_m] in drawn}) but paints "
            f"a {_m} hit ({_m in hittable}); a DRAWN node that is a declared hit "
            "must be painted -- see B-55"
        )
```

  **Pre-verified — expressible, green, and it closes the gap:**

```
  precondition: (m in hittable) == (TITLES[m] in drawn) on the SHIPPED tree,
                4 members x 6 renderers at w=120  ->  24/24 agree, zero mismatches

  FIX baseline (shipped source)      resolved=50 red=0 skipped=0   GREEN, no false-fail
  FIX WIDE-DROP first (w>=100)       resolved=50 red=1  KILLED     <- was SURVIVED
  FIX WIDE-DROP hit   (w>=100)       resolved=50 red=1  KILLED     <- was SURVIVED
  FIX NOROOT           (regression)  resolved=50 red=1  KILLED     <- Q1's kill preserved
  FIX flat-DROP other  (regression)  resolved=50 red=2  KILLED
```

  The generalisation also subsumes the floor asymmetry noted in §2: a four-member renderer that drops
  one member no longer slips past on `len(hittable) == 3`.

  **Recommended scope for the split:** this one arm body, plus a re-fire of the drop-a-member family
  **width-conditioned as well as flat**, per site. The `TITLES` map is a second spelling of the
  fixture's titles and the micro-increment should decide whether to derive it from `_graph()` instead
  — I did not, because it is a design call for the implementer, not a correctness one.

---

## Evidence checklist

- [x] **Diff read in full** — `tests/test_views_hits.py:1-378` (all 50 arms; the round-5 arm body at
      `:227-319` line by line, and every sibling arm's width and assertion direction tabulated); all
      seven hit sites and their surrounding branches in `mapper/views/{outline,radial,lane,layered}.py`
      (`outline.py:113-141`, `radial.py:108-133,180-248`, `lane.py:125-145,220-235,283-300,345-365`,
      `layered.py:522-545`); `increment-005.md` §15 and pass 4 in full.
- [x] **Correctness pass (edge / None / error paths)** — sizes 0 through 4, all 16 subsets, three
      widths, three selections, on all six renderers; the root; the clip regimes at 80 and 100.
- [x] **Domain audited: genuinely derived** — no literal member list inside the quantifier; `hittable`
      reproduces the measured paint on all six renderers at 80/100/120.
- [x] **Derivation trustworthiness proven by DEFEATING the guard** — boundary rewritten to a tautology;
      all three `NOROOT` KILLs revert to SURVIVED; the defeat itself is green on shipped code. The
      boundary is the **sole** catcher.
- [x] **Floor audited** — `len(hittable)` measured 3/3/3/4/4/4 at 120; no false-fail; the one
      direction it can be wrong fails loud, alongside a sibling precondition.
- [x] **`B-55` proxy audited per family AND against truncation** — longest-prefix probe at three
      widths: 13/13 for the three that draw the root, 0/13 for the lane family. Sound both directions.
- [x] **42 fired / 35 KILLED / 7 equivalent re-fired per site on an independent harness** —
      reproduced exactly, survivor-for-survivor.
- [x] **All seven equivalences independently re-proven by output digest** — 864 renders per digest,
      four positive controls, all fire; zero unexpected results.
- [x] **Three EXTRA drop-member shapes fired per site** (`NOFIRST`/`NOHIT`/`NOOTHER`) — 21 fired,
      18 KILLED, 3 proven equivalent; zero flat drop-a-member survivors in the tree.
- [x] **A width-conditioned shape constructed and fired** — 2 real survivors, proven non-equivalent by
      digest, confirmed across the whole 904-arm lane (`W1`).
- [x] **§15.3's figures re-executed** — 5 full-suite lanes; census and ruff re-derived inside the
      repository (`--isolated` both sides); `layered.py` byte-identity past the CRLF/LF trap.
- [x] **The charter's fix executed, not proposed** — precondition 24/24, baseline green at 50/0,
      both survivors to KILLED, `Q1`'s kill preserved.
- [x] **Verdicts per resolved node id, arm count asserted first** — 50 asserted before every one of
      75 fires; `--color=no`; the planted control reddened 6 arms before anything was believed.
- [x] **Tree restored** — six sha256 pins matched after the last restore; `git status --porcelain`
      identical to entry apart from this file; `__pycache__` purged; `layered.py` identical to `HEAD`.
- [x] **Verdict explicit** — below.

## Verdict

- [x] **OK to advance — PASS**
- [ ] OK with the listed fixes applied first
- [ ] Block

**PASS. HIGH findings on `Q1`'s axis: 0. HIGH findings outside it: 1 (`W1`), non-blocking under the
terminal boundary.**

**(a) `Q1`'s axis is CLOSED.** The domain is genuinely derived per renderer with no literal member
list surviving inside the quantifier; the floor is right and cannot false-fail at the width used; the
`B-55` boundary is correct per renderer family, sound as a proxy against truncation at 80/100/120,
and proven to be the **sole** catcher of the drop-`root` defect by defeating it and watching three
KILLs revert to SURVIVED; the 42/35/7 battery reproduces exactly and survivor-for-survivor with all
seven equivalences re-proven over 864 renders against controls that fire; every flat drop-a-member
shape across all four members and all seven sites is killed; and every §15.3 figure is TRUE.

**(b) I did find something outside that axis: `W1`.** The arm measures its domain at **w=120** while
the sibling arms that backstop `first` and `hit` — the two members the boundary does not cover — run
at **w=80**, so a drop of either that bites only at w ≥ 100 is absorbed by the derivation and invisible
to the backstops. Fired at `mapper/views/radial.py:232`, both shapes survive all 50 arms and the whole
904-arm default lane at exit 0, and both are proven non-equivalent by digest; `other` and `root` at the
same site die, because those are the only members with a w=120 observation outside the absorbing arm.
**Charter for the split micro-increment:** generalise the `B-55` boundary from `root` to every member
of `ALL`, asserting `(m in hittable) == (TITLES[m] in drawn)` for all four, then re-fire the
drop-a-member family **width-conditioned as well as flat**, per site. Tests only; no source file
touched; arm count stays 50 and the census pin stays 59. Pre-verified in §7: precondition 24/24 on the
shipped tree, baseline green at 50 resolved / 0 red, both survivors to KILLED, and `Q1`'s kill
preserved.

**For the coordinator, plainly.** The renderer changes are correct and should commit — that is now
five independent rounds finding **zero defects in shipped behaviour**. Round 5's oracle fix is real,
correctly reasoned, and its load-bearing half is load-bearing in fact and not only in the docstring.
`W1` is the same pattern one rung further out, and it is genuinely a different quantifier rather than
`Q1` restated: no flat shape reaches it. It is narrower than `Q1` was — it needs a width-conditioned
defect rather than any drop — but it is operator-reachable in the regime real terminals actually run
in, so it is worth the recorded micro-increment rather than a carry.
