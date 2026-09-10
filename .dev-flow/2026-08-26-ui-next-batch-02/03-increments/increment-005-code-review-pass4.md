# Increment 5 — PASS 4, the deciding pass on the FORM of the oracle (`LLR-N07.2.2b` / `AT-024`)

**Batch:** `2026-08-26-ui-next-batch-02` (SEALED) · **Increment:** `Inc-5`
**Auditing:** the round-4 working tree (§13 fold) against pass 3's diagnosis — *"an assertion that
names specific inputs is the defect, an assertion quantified over an enumerated set is the fix"*.
**Scope:** narrowed by coordinator ruling to the FORM of the oracle. A fifth round is not authorized.
**Reviewer:** independent of the implementer and of all three prior reviewers. Harness built from
scratch; nothing accepted on the strength of §13 having been written.

## Gate verdict

> **BLOCK — 1 HIGH.**
>
> Round 4's fix is **correct along the axis pass 3 named**, and I confirm it in full: the arm is now
> quantified over cardinality, the non-vacuity guard is real, the per-site denominator of 7 is right,
> the 35-mutant battery reproduces at **32 KILLED / 3 proven equivalent** on my own instrument, the
> `layered` soundness caveat is accurate, and every §13.5 figure is TRUE.
>
> **And the pattern has produced a fourth instance, one level down from where round 4 fixed it.**
> Round 4 generalised the assertion over the *cardinality* axis it was shown — every subset of size 2
> and 3 — while **narrowing the DOMAIN from four nodes to three** and justifying the narrowing on the
> lane family's behalf. That justification is true for 4 of the 7 sites and **false for the other 3**.
> `outline`, `radial` and `layered` all draw the root and all paint it as a hit today (1, 13 and 20
> hit-styled spans, measured). A renderer that drops `root` from the hit set is therefore a
> **drop-a-member defect that survives every arm in the repository** at `outline.py:130`,
> `radial.py:232` and `layered.py:528` — and across the entire 904-arm default lane, exit 0.
>
> The root is **operator-reachable**: `SearchIndex.hits("raiz")` returns `{'root'}` and
> `MapScreen._search_hits` passes it straight into `ViewState.hits`. This is not a fixture artefact.
>
> `HITTABLE = ("first", "hit", "other")` is a **hand-named domain inside a quantified assertion** —
> the same defect the fix was written to remove, moved from the assertion's inputs to the set it
> quantifies over. The fix is one derived tuple and one boundary assertion; it is executed below and
> takes all three survivors to KILLED with the baseline still green.

---

## Entry / exit state

Pins asserted at entry, before every mutant, after every restore, and at exit. `tests/test_views_hits.py`
was read and pinned at entry because round 4 changed it — the round-3 pin `1e72dbdd…` is **stale**:

```
06a0e9493f10bbc392bf4e175ee737f3ca1ef95cf10b996de139de7105325b39 *mapper/views/outline.py
aa462076e911c3983c4a02589094fbadd150fcfb6f1dab8d740b6fd7420f6d85 *mapper/views/radial.py
098b90b4baad538e9fda51be662a52f9354781e85085496153119d289ee602ef *mapper/views/lane.py
8a1105ed2eb7fa238ee7979d33d432b84b900022678b5c0fa3a377443d0f2e94 *tests/test_views_hits.py   <- round 4
8384ebfa42b47af6809b4fd9de81dbd450fa38f1d59ec2ae500035c033880e56 *tests/test_a3_census.py
3e081a6c61af9a20ec5ec94140e4258226fc0b692c65dea707701ba07c4015b5 *mapper/views/layered.py
--- git status --porcelain, identical to entry apart from THIS file ---
```

**`mapper/views/layered.py` is byte-identical to `HEAD`.** Verified past the CRLF/LF trap the prior
passes flagged: `sha256(worktree) = 3e081a6c…`, `sha256(git show HEAD:…) = 76fd432c…`, **normalised
digests equal**, `git diff HEAD` empty. Round 4's restoration claim is **TRUE**.

**Tree discipline.** Sole writer. **122 mutants fired** plus 4 full-suite lanes and 12 read-only
render probes. Every mutation applied at the **byte** level to bytes read from disk and restored in a
`finally` from those exact bytes, all six pins re-asserted before the next fired. `__pycache__`
purged on both sides of every mutation; `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUTF8=1` in every child
process. Mutants described **by position and operation**, never pasted verbatim (`C-56`). Anchors are
**plain strings at a known occurrence index**; an anchor matching fewer times than its index raises
**BAD** rather than reporting a verdict. Harness outside the repository
(`C:\Users\jjgh8\clde\scratch\inc5_pass4\`).

**Instrument RED-proof (`C-57`), run before any verdict was believed.**

```
BASELINE                                     resolved=50 passed=50 red=0 skipped=0
CONTROL outline hit branch made unreachable  resolved=50 red=6  KILLED
```

Every verdict is read from **resolved node ids** with `--color=no`; the harness raises unless it
resolves exactly **50**.

**Anchor → line resolution, asserted rather than assumed** (this is the `P4` denominator, re-derived):

```
S1 outline.py cond->130  style->136     S5 lane.py    cond->291  style->294
S2 radial.py  cond->232  style->245     S6 lane.py    cond->354  style->357
S3 lane.py    cond->133  style->138     S7 layered.py cond->528  style->539
S4 lane.py    cond->228  style->230
```

---

## 1 · Is the quantification complete over its declared domain?

**Over its DECLARED domain: yes, completely. The declared domain is the defect.**

`HITTABLE` has three members and the arm iterates `k in (2, 3)` — that is **every** subset of size
≥ 2, exhaustively. There is no cardinality gap. Size-1 is pinned by the non-vacuity guard plus three
other arms; size-0 is pinned by `painted != none` and, for a spurious unconditional hit style, by the
sealed threshold arm. **Nothing about cardinality goes unasserted.**

The domain itself is hand-named, and the reason given for excluding `root` does not hold at 3 of the
7 sites. Measured — shipped tree, hit-styled spans at w=120 for each single-node hit set:

```
                              root   first    hit   other
  outline.OutlineRenderer        1       1      1       1     <- DRAWS and PAINTS the root
  radial.RadialRenderer         13      11     18      10     <- DRAWS and PAINTS the root
  layered.LayeredRenderer       20      20     20      20     <- DRAWS and PAINTS the root
  lane.LaneRenderer              0       1      1       1     <- never draws it  (B-55)
  lane.RailTimelineRenderer      0      13     28      20     <- never draws it  (B-55)
  lane.HybridLaneRenderer        0       1      1       1     <- never draws it  (B-55)
```

`"Raiz del mapa" in plain` at w=120 is `True` for exactly `outline`, `radial`, `layered` and `False`
for the three lane renderers. So the docstring's claim — *"the three lane renderers iterate branches
and never draw it… including it would false-fail the lane family"* — is **exactly true for the lane
family and inapplicable to the other three**, where including `root` costs nothing and buys the
observation. The exclusion is applied uniformly across a parametrisation whose justification is
site-specific. That is `P4`'s per-class-versus-per-site collapse, reappearing inside the fix for `P4`.

## 2 · Is the non-vacuity guard real?

**Yes.** `assert sp` fires per member before any union is taken, so `expected` is a union of
non-empty sets and `X == ∅ ∪ X` cannot arise. Executed: it is what kills the trunk style DRIFT
(`P3`) at `lane.py:230`, which is the shape that previously exploited the vacuity flank. Confirmed
below at `DRIFT S4 … red=1 KILLED`.

One residual flank, recorded as an observation and **not** as a finding because I could not build a
survivor from it: if all three single-member paintings were the *same* span set, a drop-a-member
mutant would still satisfy the union. Measured, they are pairwise distinct on all six renderers, and
`..._the_paint_is_keyed_on_WHICH_node_is_a_hit` pins that independently. Not live.

## 3 · Is the per-site denominator right? — 7 sites, and the battery reproduces

**Seven, and there is no eighth.** Swept `mapper/views/` for every consumer of `state.hits`; every
hit-membership test that drives a **style** is one of the seven above. `layered.py:598-599` is an
eighth *consumer* but it drives **text**, not style, and it is the subject of §4 below — correctly
outside the paint denominator.

**35 declared mutants re-fired PER SITE on my own harness — §13.4 reproduces exactly:**

```
                       MIN     MAX    MINMAX   SORTED2   DRIFT
  S1 outline.py:130    KILL    KILL    KILL     KILL     KILL
  S2 radial.py:232     KILL    KILL    KILL     KILL     KILL
  S3 lane.py:133       KILL    KILL    KILL     KILL     KILL
  S4 lane.py:228       surv    KILL    surv     surv     KILL
  S5 lane.py:291       KILL    KILL    KILL     KILL     KILL
  S6 lane.py:354       KILL    KILL    KILL     KILL     KILL
  S7 layered.py:528    KILL    KILL    KILL     KILL     KILL

  35 fired · 32 KILLED · 3 survivors, all at S4 · resolved=50 on every run
```

`P1`'s survivor (`MAX` at `lane.py:291`) is **KILLED**. `P2`'s `MINMAX`/`SORTED2` are **KILLED**
everywhere they can act. `P3`'s trunk drift is **KILLED**, by the non-vacuity guard.

**The 3 equivalences independently re-proven by output digest, over a domain strictly larger than
round 4's** — 4 nodes × all 16 subsets × 3 widths (80/100/120) = 48 renders, hashing `(w, hit set,
plain, spans)` — with `MAX` as the **positive control that must differ**:

```
S4 lane.py:228 (RailTimelineRenderer)     shipped = 950274bb52fd79e3
  MIN      950274bb52fd79e3  SAME      EQUIVALENT
  MINMAX   950274bb52fd79e3  SAME      EQUIVALENT
  SORTED2  950274bb52fd79e3  SAME      EQUIVALENT
  MAX      cfa2bdf742b7721c  DIFFERS   <- positive control fires; the probe is not blind
```

§13.4's equivalence claim is **CONFIRMED**, and on a broader domain than it was made on.

## 4 · Is the soundness premise still honest?

**Yes — the caveat is accurate, and I verified the mechanism rather than the sentence.**

`mapper/views/layered.py:588` opens `for nid in geo.pill_ids:`, and `:598-599` computes
`n_hits = len(_descendants(index, nid) & hit_ids)` and appends `tail = f" {n_hits}"`. That **is** a
hit-set-dependent change to rendered **text**, and it is exactly what would break the union
comparison's offset-comparability. It is unreachable here because `pill_ids` is
`[nid for nid in visible if nid in state.folded and …]` (`:265`) and the fixture never sets `folded`.

**The premise itself is measured TRUE where it is used**, closing pass 3's `P6` (the premise was
pinned only at w=80): rendered text is invariant under the hit set for **all six renderers, at
w=80, 100 and 120, across all 16 subsets of the four nodes**. Zero breaks.

## 5 · §13's figures — re-executed, not accepted

| §13.5 claim | My measurement | Verdict |
|---|---|---|
| `904 passed, 17 deselected, 3 xfailed` exit 0 | `904 passed, 17 deselected, 3 xfailed in 213.10s` exit 0 | **TRUE** |
| all markers `921 passed, 3 xfailed` exit 0 | `921 passed, 3 xfailed in 244.41s` exit 0 | **TRUE** |
| lane arithmetic `904 + 17 = 921` | holds | **TRUE** |
| `50 arms, zero skipped` | 50 resolved node ids asserted before **every** verdict (the harness raises on any other count); `skipped=0` measured at baseline and at the fixed baseline; no `skipped` in any of the 4 lane summaries | **TRUE** |
| census `argful 59, zeroarg 26, defs 7` | re-derived from `render_call_sites()` / `render_definitions()`: `argful 59 zeroarg 26 defs 7` | **TRUE** |
| ruff SET `27 = 27`, zero NEW, zero GONE | `ruff check mapper tests` **inside** the repository = **27**. Per-path delta via `ruff check --isolated --stdin-filename <path> -` on **both** sides: all five touched paths report **0 findings** on HEAD content and on working content (`test_views_hits.py` is new at HEAD). Delta empty both directions | **TRUE for this increment's delta** |
| battery `R4 35 fired, 32 KILLED, 3 proven equivalent` | reproduced exactly, per site, on an independent harness; the 3 equivalences re-proven on a larger domain with a positive control | **TRUE as stated** |
| `layered.py` restored to HEAD exactly | `git diff HEAD` empty; normalised digests equal | **TRUE** |
| §13.6's three packet corrections | §2 heading and §2.1 now say **six**; the `C-14` line now admits **5 of 6** and names why; ⚠ list items 4-7 present | **TRUE** |

**One qualification on the battery row.** `32 KILLED, 0 real survivors` is true of the five shapes
fired. It is **not** a coverage claim about the drop-a-member class — the *shape* population is now
the incomplete set, one level down from where §13.3 correctly fixed the *site* population. `N1` below
is what that costs.

---

## NEW finding

### `Q1` — the arm quantifies over a hand-named DOMAIN; a drop-`root` defect survives the whole repository at 3 of 7 sites [Severity: **HIGH**]

- **What:** `HITTABLE = ("first", "hit", "other")` names its members. A renderer that drops `root`
  from the hit set — the same drop-a-member defect class that has blocked three rounds — is invisible
  to every arm in the repository at three sites, two of which this increment authored.
- **Where:** `tests/test_views_hits.py:282` (the `HITTABLE` tuple) and `:278-281` (the justification).
  The surviving sites are `mapper/views/outline.py:130`, `mapper/views/radial.py:232`,
  `mapper/views/layered.py:528`.
- **Executed** — the shape fired **per site**, membership narrowed to exclude the root:

```
NOROOT  S1 outline.py:130    resolved=50 red=0  *** SURVIVED ***
NOROOT  S2 radial.py:232     resolved=50 red=0  *** SURVIVED ***
NOROOT  S3 lane.py:133       resolved=50 red=0      SURVIVED (equivalent)
NOROOT  S4 lane.py:228       resolved=50 red=0      SURVIVED (equivalent)
NOROOT  S5 lane.py:291       resolved=50 red=0      SURVIVED (equivalent)
NOROOT  S6 lane.py:354       resolved=50 red=0      SURVIVED (equivalent)
NOROOT  S7 layered.py:528    resolved=50 red=0  *** SURVIVED ***

WHOLE DEFAULT LANE, same mutant:
  CLEAN                            exit=0  904 passed, 17 deselected, 3 xfailed
  NOROOT @ outline.py:130          exit=0  904 passed, 17 deselected, 3 xfailed   SURVIVED
  NOROOT @ layered.py:528          exit=0  904 passed, 17 deselected, 3 xfailed   SURVIVED
```

- **Three of the seven are NOT equivalent mutants**, proven by output digest over 48 renders with
  `MAX` as the positive control (the four lane sites ARE equivalent, exactly as the docstring says):

```
  S1 outline   shipped cd89dbe4e39ab761   NOROOT 2ceb0c3df878bb55   DIFFERS  REAL DEFECT
  S2 radial    shipped aeafd48545345040   NOROOT 9f2de7bc9dd26306   DIFFERS  REAL DEFECT
  S7 layered   shipped 09f048d815924c8b   NOROOT 4cfc86341f3fd8b3   DIFFERS  REAL DEFECT
  S3/S4/S5/S6  shipped ==== NOROOT ==== SAME                        EQUIVALENT (B-55 holds)
```

- **The root is operator-reachable, so this is a requirement defect and not a fixture curiosity:**

```
  SearchIndex(g).hits('raiz')  -> {'root'}        g.root_id == 'root'
  SearchIndex(g).hits('mapa')  -> {'root'}
  MapScreen._search_hits() -> ViewState(hits=...) at app.py:2205
```

  `01-requirements.md:2753` is *"shall paint the **nodes** carried in `state.hits`"* with no
  exclusion for the root, and `:2456-2458` names *"reporting a count a view does not paint"* as the
  error class this story exists to prevent. A search matching only the root's title paints a count of
  1 over a canvas that paints 0 — in `outline`, `radial` and `layered`, which are the three
  operator-reachable renderers (`F6`).

- **Why it matters, and why it is the same finding a fourth time.** The arm is named
  `EVERY_member_of_the_hit_set_is_painted`. Round 4 moved the naming out of the *assertion* and into
  the *domain the assertion quantifies over*, which leaves the guarantee exactly as wide as the names
  someone remembered. Pass 3's rule — *an assertion that names specific inputs is the defect* —
  applies unchanged to a quantifier whose set is a literal.

  The `B-55` route is also a mis-route rather than a carry. `B-55` is *"a clipped hit is an undeclared
  hit"*, which is true of the lane family, where the root is never drawn. `outline`, `radial` and
  `layered` **do** draw the root and **do** paint it; there is nothing for `B-55` to carry there, so
  filing the exclusion under it puts a live gap behind a closed door.

- **Suggested fix — derive the domain per renderer, and assert the `B-55` boundary instead of
  assuming it.** Tests only; no source file touched; the arm count stays 50 and the census pin stays
  59, because every render still goes through `_spans_at`. Replace the body from `def hit_spans` to
  the end of the arm:

```python
    def hit_spans(spans):
        return {s for s in spans if s[2] == HIT_STYLE}

    # THE DOMAIN IS DERIVED PER RENDERER, NOT NAMED.  A previous revision
    # hard-coded ("first", "hit", "other") and justified excluding `root` on the
    # lane family's behalf -- true there, and BLIND for the other three:
    # `outline`, `radial` and `layered` all DRAW the root and DO paint it as a
    # hit (measured: 1, 13 and 20 hit-styled spans), and a renderer that drops
    # `root` from the hit set survived every arm in this repository at
    # `outline.py:130`, `radial.py:232` and `layered.py:528`.  A domain that
    # names its members is the same defect as an assertion that names its
    # inputs, one level down.
    ALL = ("root", "first", "hit", "other")
    singles = {m: hit_spans(_spans_at(cls, 120, {m})[1]) for m in ALL}
    hittable = tuple(m for m in ALL if singles[m])

    # NON-VACUITY, and it is a FLOOR, not a filter: `hittable` is read off the
    # paint, so without this the domain could shrink to nothing and every union
    # below would pass for free.
    assert len(hittable) >= 3, (
        f"{cls.__name__} paints a hit-styled span for only {hittable}; the "
        "unions below would be vacuous"
    )
    # THE `B-55` BOUNDARY IS ASSERTED, NOT ASSUMED, and it is what stops the
    # derivation above from silently absorbing a dropped member: a node this
    # renderer DRAWS and the state DECLARES as a hit must be painted.  The three
    # lane renderers iterate branches and never draw the root, so a root hit is
    # declared-but-unpaintable there (`B-55`, §10) -- and that is read off the
    # rendered text rather than off a list of class names.
    drawn, _ = _spans_at(cls, 120, set())
    assert ("root" in hittable) == ("Raiz del mapa" in drawn), (
        f"{cls.__name__} draws the root ({'Raiz del mapa' in drawn}) but paints "
        f"a root hit ({'root' in hittable}); a DRAWN node that is a declared hit "
        "must be painted -- see B-55"
    )

    _, none = _spans_at(cls, 120, set())
    for k in range(2, len(hittable) + 1):
        for combo in combinations(hittable, k):
            _, painted = _spans_at(cls, 120, set(combo))
            assert painted != none, f"{cls.__name__} paints nothing for {combo}"
            expected = set().union(*(singles[m] for m in combo))
            dropped = sorted(m for m in combo if not (singles[m] <= hit_spans(painted)))
            assert hit_spans(painted) == expected, (
                f"{cls.__name__} hits={combo}: the painting is not the union of "
                f"the single-member paintings; dropped={dropped}"
            )
```

  The boundary assertion is the load-bearing half. Without it the derivation would *absorb* the
  defect: under `NOROOT` at `outline`, `singles["root"]` goes empty, `root` drops out of `hittable`,
  and the unions pass for free. With it, the renderer still draws the root while no longer painting
  it, and the arm reddens.

- **Executed against the fix — this is the argument for it, not a proposal:**

```
  FIX baseline                       resolved=50 red=0 skipped=0   (no false-fail on shipped code)

  FIX NOROOT  S1 outline.py:130      red=1  KILLED     <- was SURVIVED
  FIX NOROOT  S2 radial.py:232       red=1  KILLED     <- was SURVIVED
  FIX NOROOT  S7 layered.py:528      red=1  KILLED     <- was SURVIVED
  FIX NOROOT  S3/S4/S5/S6            red=0  survives   <- correct: proven equivalent
  FIX MIN/MAX/MINMAX/SORTED2/DRIFT   all 35 verdicts UNCHANGED from the round-4 battery

  42 fired under the fix · 35 KILLED · 7 survivors, all 7 proven equivalent by digest
```

  Domains widen to 4 nodes for `outline`/`radial`/`layered` (subsets of size 2, 3 and 4) and stay at
  3 for the lane family. Wall clock on the 50-arm file is unchanged within noise.

---

## Things I attacked and could NOT break

Recorded so `Q1` is not read as a general verdict on the tree.

- **The cardinality quantification.** `k in (2, 3)` over a 3-set is exhaustive; I could not construct
  a cardinality-shaped survivor within the declared domain.
- **The non-vacuity guard.** Real, load-bearing, and it is what kills the trunk DRIFT. The
  identical-singles flank is not live — the three single-member paintings are pairwise distinct on
  all six renderers.
- **The per-site denominator.** Seven, confirmed by an independent sweep; no eighth paint site.
  Every anchor resolved to exactly the line §13.3 claims.
- **The three residual equivalences.** Re-proven on a strictly larger domain (16 subsets × 3 widths)
  with a positive control that fires. §13.4 is honest.
- **The soundness premise.** Text invariance measured TRUE at w=80, 100 and 120 across all 16
  subsets on all six renderers — closing pass 3's `P6`, which was that the premise was pinned only at
  80. The `layered` folded-pill caveat names the real mechanism (`layered.py:588-599`, gated on
  `geo.pill_ids`, empty because the fixture sets no `folded`).
- **Every §13.5 figure.** Re-executed independently; all TRUE, with the one stated qualification on
  reading the battery total as coverage.
- **No new defect in shipped behaviour.** As in all three prior rounds: the seven hit sites are pure
  membership tests over a `frozenset[str]`, every style is an f-string over `darkside` colour
  literals, no file-derived text reaches a style, no signature moved. `A-91`'s "no data path / no
  security sink / no A3 change" verdicts hold; nothing to route to `security-reviewer`.
  **`Q1` is a defect in the oracle, not in the renderers — the shipped tree paints the root correctly
  in all three renderers that draw it.**

**One stale citation, not a finding.** Pass 3 records the module's only arg-ful census site as
`('tests/test_views_hits.py', 79)`; round 4's arm body moved it to **81**. The pinned *count* (59) is
what the census asserts and it is unchanged.

---

## Evidence checklist

- [x] **Diff read in full** — `tests/test_views_hits.py:1-363` (all 50 arms, the round-4 arm body at
      `:227-304` line by line); all seven hit sites and their surrounding branches in
      `mapper/views/{outline,radial,lane,layered}.py`; `layered.py:485,520-545,588-605,628-648` and
      `mapper/search.py:38-100`, `mapper/app.py:2091-2130,2179-2205` as read-only context;
      `increment-005.md` §§2, 9, 13 and pass 3 in full.
- [x] **Correctness pass (edge / None / error paths)** — size-0, size-1, size-≥2, ghost ids, the
      whole-graph hit set, and the root, at three widths on six renderers.
- [x] **Quantification audited over its declared domain** — complete on cardinality; **incomplete on
      the domain itself** (`Q1`).
- [x] **Non-vacuity guard audited** — real; the identical-singles flank measured and not live.
- [x] **Per-site denominator verified** — 7, no eighth; every anchor resolved to its claimed line.
- [x] **35-mutant battery re-fired PER SITE on an independent harness** — 32 KILLED / 3 survivors,
      reproducing §13.4 exactly.
- [x] **The 3 equivalences independently re-proven by output digest** — 48 renders, positive control
      (`MAX`) fires.
- [x] **A sixth shape constructed and fired per site** — `NOROOT`, 7/7 SURVIVED; 4 proven equivalent,
      **3 proven real** (`Q1`), plus two full-lane confirmations.
- [x] **Soundness premise verified at the width it is used** — text invariance TRUE at 80/100/120
      over 16 subsets; the `layered` caveat's mechanism read from source.
- [x] **§13.5's figures re-executed** — 4 full-suite lanes; census and ruff re-derived inside the
      repository (`--isolated` both sides); `layered.py` byte-identity past the CRLF/LF trap.
- [x] **The recommended fix executed, not proposed** — 42 mutants under the fix, 35 KILLED, 7 proven
      equivalent, baseline green at 50 resolved / 0 red.
- [x] **Verdicts per resolved node id, arm count asserted first** — 50 asserted before any all-green
      was believed; `--color=no`; the planted control reddened 6 arms before anything was reported true.
- [x] **Tree restored** — six sha256 pins matched after the last restore; `git status --porcelain`
      identical to entry apart from this file; `__pycache__` purged; `layered.py` identical to `HEAD`.
- [x] **Verdict explicit** — below.

## Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **BLOCK — must fix the HIGH finding before advancing**

**HIGH findings: 1** (`Q1`). **New findings raised: 1.** No MEDIUM, no LOW.
**Pass 3's `P1`, `P2`, `P3`, `P4`, `P5`, `P6`, `P7`: all DISCHARGED, each verified by measurement.**

**Is the oracle's FORM now sound?** **No — not yet, and the specific thing still wrong with it is
this:** round 4 removed the naming from the *assertion* and left it in the *domain the assertion
quantifies over*. `HITTABLE = ("first", "hit", "other")` is a literal three-element set standing
where the fixture's four hittable nodes belong, and its stated justification is a property of the
three lane renderers applied to all six. The consequence is measured, not argued: a drop-`root`
mutant survives all 50 arms and the entire 904-arm lane at `outline.py:130`, `radial.py:232` and
`layered.py:528`, the root is reachable in `state.hits` from an ordinary search, and those three are
the operator-reachable renderers. Everything else about the form **is** sound — the cardinality
quantification is exhaustive, the non-vacuity guard is real and load-bearing, the per-site
denominator of 7 is right, the equivalence proofs are honest, and the soundness caveat is accurate.
The gap is one axis wide, and the fix above closes it: **derive the domain from what each renderer
paints, and assert the `B-55` boundary rather than assuming it.**

**Minimum to clear the block:** apply the arm body under `Q1` (verified: baseline green, three
survivors to KILLED, all 35 prior verdicts unchanged), and re-fire the drop-a-member families
including the drop-`root` shape, per site. Tests only; the sealed `SOURCE FILE COUNT: 3` and every
`A-91` source verdict are unaffected, arm count stays 50, census pin stays 59.

**For the coordinator, plainly.** This increment is at four BLOCKs and a soft cap of three was already
surfaced at §13.7. Every one of the four rounds has found **zero defects in shipped behaviour** — the
renderers have been correct since round 1, and they are correct now. What keeps failing is the oracle,
and it has now failed at four successive levels of the same structure: the assertion's inputs, the
mutant population's sites, the assertion's cardinality, and now the domain it quantifies over. The
fix for `Q1` is one derived tuple and one boundary assertion, and it is already executed and green
in this report. But a fifth round is not authorized, this pass was told to stop the increment if it
found anything new, and it found something new that is operator-reachable. **Returning to the
operator with the fix in hand and the decision theirs.**
