# Increment 017 — routed finding `F3` (Inc-W1) re-measured · independent QA lens

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Finding | `F3` (Inc-W1), routed 2026-09-10 to `qa-reviewer`; pickup "Inc-CONFIRM, or the whole-branch QA gate — whichever comes FIRST" |
| Base measured | `046acea` (repo HEAD at pickup) |
| Agent | `qa-reviewer` (independent lens) |
| **Mode** | **`validation`** — a verdict over re-measured results, not a test plan |
| Date | 2026-09-19 |

**THIS REPORT AUTHORISES NOTHING BY ITSELF.** It is an independent measurement and a
recommendation. No arm is delivered, no source file is changed, and no gate is closed by it.
`software-dev` owns any implementation; the coordinator owns the decision.

---

## 0 · Verdict in one line

**`F3` IS STILL LIVE, and its structural statement holds verbatim on the current tree: exactly one of
four fixture members has its drawn-ness pinned, and a co-drop of any of the other three survives the
50-arm file AND the whole default lane on `RadialRenderer`.** The scope judgement that declined to fix
it in Inc-W1 was **correct and remains correct** — and the re-measurement shows *why*: the trigger
cannot be pinned inside `LLR-N07.2.2b` at all. It belongs to the requirement that already owns "a node
that did not reach the canvas must be declared" — `HLR-N06.3`, `B-55`'s own family.

---

## 1 · The instrument, and why its results are believable

**Mirror, not the repo.** Every measurement below was taken in the isolated, digest-verified mirror
`…\scratchpad\mirror-qa-f3`, never in `C:\Users\jjgh8\Github\mapper`. Byte identity was re-asserted at
the start of this run rather than taken from the hand-off:

```
mapper/views/radial.py    df3512af876b9ff4ac2be130e77cbdb65a30a28eb16570590f01723ccf00e920  20795  CRLF
tests/test_views_hits.py  c7e4c121e4c8972ccdc1b9812aa659c2a4fa8dd3ed4f361ec368b144f5ebaef2  22856  LF
tests/test_a3_census.py   0d06556d9c098a2957bee8bb1406798568ddcf924bd38768f88e5d261cd8fa90  32311  CRLF
```

— identical in mirror and repo at `046acea`. Every mutation harness re-pinned the base digest, printed
its verdicts **before** the restore assertion, and asserted the restored digest equals the base
(`RESTORE-OK` on every run). Final digests after all work, re-read from disk:

```
mapper/views/radial.py   df3512af876b9ff4ac2be130e77cbdb65a30a28eb16570590f01723ccf00e920
mapper/views/lane.py     098b90b4baad538e9fda51be662a52f9354781e85085496153119d289ee602ef
mapper/views/outline.py  18d80107fe33d4478577a2d1b4e713e892c1c750f4190d54b9d665ff43d82b26
mapper/views/layered.py  dca00aade523db8e62c760e8f620720a754db801b06c7556ef5f4b2fd28447f3
tests/test_views_hits.py c7e4c121e4c8972ccdc1b9812aa659c2a4fa8dd3ed4f361ec368b144f5ebaef2
```

All runs carried `PYTHONUTF8=1 PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1`. Mutants were fired
**per SITE** with the substitution count asserted **exactly 1**.

**The `.pth` trap was closed by assertion, not by hope.** Every ad-hoc probe asserts `mapper.__file__`
resolves inside the mirror before doing anything; each printed
`MIRROR-OK …\mirror-qa-f3\mapper\__init__.py`. The pytest runs were checked the same way by a
mirror-only arm, `tests/test_zz_mirror_probe.py`.

### THREE CORRECTIONS TO THE BRIEF, surfaced rather than worked around

1. **The CRLF list is incomplete.** `mapper/app.py` and `tests/test_pan.py` are not the only CRLF
   files. `mapper/views/radial.py`, `outline.py` and `layered.py` are **CRLF**; `mapper/views/lane.py`
   and `tests/test_views_hits.py` are **LF**. A `\n`-anchored mutation at `radial.py` matches **0×**.
   Check the EOL per file, not per directory.
2. **The mirror as handed over could not run the suite at all.** `tests/test_a3_census.py::tracked`
   shells `git ls-files … cwd=REPO`, and the mirror is not a git repository, so **collection ERRORED**
   — `renderer_classes()` is derived through that call, so `test_views_hits.py` could not even be
   collected. Closed with `git init` + `git add -A` **inside the mirror**, so the derivation still
   DRIVES the derived set, from the mirror's own tree. It returned the shipped six renderers.
3. **The mirror carried only `mapper/`, `tests/`, `pyproject.toml`.** The default lane also reads
   `docs/ARCHITECTURE.md`, `fixtures/`, `maps/` and `.dev-flow/`. The first three were copied in;
   `.dev-flow/` was not, which leaves **6 baseline-failing arms** that are pure mirror infrastructure
   and touch no renderer (§2.1). Every lane comparison below is taken against that same baseline.

**The instrument was shown RED before any PASS from it was believed** (`C-57`). Each candidate arm in
§4 is reported GREEN on the clean tree and RED on named mutants — and one candidate was **refuted by
measurement** (§4.2) and is recorded as refuted rather than quietly dropped.

---

## 2 · What I re-measured, and what it returned

### 2.1 · Baseline, mirror, clean tree

| Run | Executor | Result |
|---|---|---|
| `tests/test_views_hits.py` | **this reviewer, in the mirror** | **50 passed** in 0.39 s — still the 50-arm file the finding names |
| whole default lane | **this reviewer, in the mirror** | **1118 passed, 6 failed, 21 deselected, 3 xfailed** in 372.77 s |

The 6 baseline failures are `tests/test_repair_artifact_claims.py` (2),
`tests/test_repair_golden_census.py` (3) and `tests/test_fold.py::test_no_tracked_file_spells_a_coerced_code_point_INCLUDING_the_artifacts` (1)
— all read `.dev-flow/` state the mirror does not carry. **Verified by direct re-run on the clean
tree**: `test_fold` fails with
`FileNotFoundError: …\mirror-qa-f3\.dev-flow\_scan_probe.md`. **Mirror artefacts, not tree defects**,
and constant across every run below.

I did **not** run the lane in the repo: the ONE complete gate-suite run belongs to the orchestrator
(`C-25`).

### 2.2 · The finding's own mutant, relocated and re-fired

The finding names `radial.py:221`. **That line no longer exists** — `radial.py` moved three times since
(`f828d7b`, `540123c`, `e15fed8`). The co-drop site today is:

```
mapper/views/radial.py:298        title = darkside.plain(node.ficha.title)[:18]
```

one occurrence, CRLF-terminated. The mutant is the finding's own shape — a member neither DRAWN nor
PAINTED above the width threshold:

```python
title = "" if (w >= 100 and nid == "<member>") else darkside.plain(node.ficha.title)[:18]
```

It is **not equivalent**: at w ≥ 100 `RadialRenderer` draws an empty title for that member. The pad
cell at `j == 0` is overwritten unconditionally by the marker `put`, so the member emits **zero**
hit-styled spans, falls out of `hittable`, and the `B-55` boundary's `else` limb then compares
*not-painted* against *not-drawn* — `False == False`.

### 2.3 · The 50-arm file — the shipped instrument

| Co-dropped member | `tests/test_views_hits.py` | Verdict |
|---|---|---|
| `root` | 50 passed | **SURVIVED** |
| `first` | 50 passed | **SURVIVED** |
| `hit` | 50 passed | **SURVIVED** |
| `other` | 1 failed, 49 passed | **KILLED** — `test_llr_n07_2_2b_a_hit_outside_the_first_branch_is_painted_too[radial.RadialRenderer]` |

**The structural statement, reproduced exactly.** The one member with independent drawn-ness pinning
is `other`; the arm moved from `test_views_hits.py:190` to **`:192`** (`assert title in plain`), but it
is the same arm and still the only one. `root`, `first` and `hit` have none, and all three co-drops
walk through.

The `B-55` boundary now lives at `test_views_hits.py:341–360`, generalised by Inc-W1 from `root` alone
to every member:

```
341:    drawn, _ = _spans_at(cls, 120, set())
344:            assert TITLES[m] in drawn,       # painted => drawn
354:            assert TITLES[m] not in drawn,   # drawn   => painted   (contrapositive)
```

Two implications and no trigger. **The generalisation was a real improvement against paint-only drops
and did nothing at all against co-drops** — widening an equivalence widens the `False == False` hole
with it.

### 2.4 · The whole default lane — all three co-drops SURVIVE

| Mutant (`radial.py:298`) | Default lane, mirror | Renderer arms reddened |
|---|---|---|
| co-drop `first` (`sha=d1360c17…`) | 7 failed, 1117 passed, 24 deselected, 3 xfailed, 388.90 s | **ZERO** |
| co-drop `hit` (`sha=7b9962f3…`) | 7 failed, 1117 passed, 24 deselected, 3 xfailed, 391.90 s | **ZERO** |
| co-drop `root` (`sha=225024d1…`) | 7 failed, 1117 passed, 24 deselected, 3 xfailed, 388.16 s | **ZERO** |

The identical 7 failures in all three runs are the 6 baseline mirror artefacts **plus**
`tests/test_a3_census.py::test_tc_a3_no_source_file_is_invisible_to_the_census`. **That seventh one is
my own instrument, and the attribution is measured, not argued:** the only untracked file under
`tests/` or `mapper/` is my candidate arm `tests/test_zz_f3_candidate.py`, and staging it turns that
census arm **GREEN (1 passed)** on the clean tree.

**So: not one renderer-behaviour arm in the entire default lane observes any of the three co-drops.**
The finding's claim — measured at 904 arms — reproduces at **1127 arms run**.

### 2.5 · Where the exposure actually is — measured across the derived set

I did not assume `radial` is special. The same co-drop shape was fired at the analogous site in every
other renderer file, per site, digest restored and re-asserted each time.

| Site | Member dropped | `test_views_hits.py` | Verdict |
|---|---|---|---|
| `lane.py:122` (`LaneRenderer`) | `first` / `hit` | 1 failed, 49 passed | **KILLED** — `…EVERY_member_of_the_hit_set_is_painted[lane.LaneRenderer]` |
| `lane.py:335` (`HybridLaneRenderer`) | `first` / `hit` | 9 failed, 41 passed | **KILLED** (9 arms) |
| `outline.py:251` | `root` / `first` | 9 failed, 41 passed | **KILLED** (9 arms) |
| `layered.py:594` | `root` / `first` | 1 failed, 49 passed | **KILLED** — `…EVERY_member_of_the_hit_set_is_painted[layered.LayeredRenderer]` |
| **`radial.py:298`** | **`root` / `first` / `hit`** | **50 passed** | **SURVIVED** |

**Honest limitation, stated rather than smoothed over:** the `outline` and `HybridLaneRenderer`
mutants reddened *nine* arms each — far more collateral than a clean single-member co-drop should
produce, so those two mutants perturbed more than the one member. **I have NOT established that
`outline` and `HybridLaneRenderer` are immune**, only that *this* mutant dies there. A subtler co-drop
at those sites is **not-run**.

What **is** established is the positive: **`RadialRenderer` is exposed, and it is one of the three
renderers `app.py` actually constructs** — `app.py:1247–1249` builds Layered, Outline and Radial; the
lane family is constructed nowhere and reaches no operator sink, which is the reason
`tests/test_inc3_census.py` itself gives for the lane's absence from the `painted_ids` census. **The
live exposure sits on an operator-reachable renderer.**

**Supporting measurement — drawn vs painted, per renderer, per member, across widths 80/100/120/160/200:**
`lane`, `hybrid` and `rail` draw **no root label at any width**; `outline`, `layered` and `radial` draw
and paint all four. `rail` draws `other` only from w = 100 upward (the clip the arm at `:192` already
documents).

---

## 3 · Judgement on the scope reasoning, and the right owner

**I AGREE WITH INC-W1'S SCOPE JUDGEMENT**, and the re-measurement upgrades it from a defensible
deferral to the correct call. Inc-W1 wrote: *"The class is DRAWING, not hit-painting. `LLR-N07.2.2b` is
about painting hits distinguishably; widening the arm to police what each renderer draws would pull a
different requirement into a tests-only micro-increment."* That is right, and the measurement shows
something stronger.

**The trigger cannot be asserted from inside `LLR-N07.2.2b` at all — for `root`.** I tried. A
leave-one-out consensus over the derived renderer set (§4.1) pins `first`, `hit` and `other` with no
hand-named member — but it **cannot** pin `root`, because the derived set genuinely disagrees about the
root, and the disagreement is a design property rather than a clip (measured at five widths). No
oracle computed from renders alone can distinguish "the lane family legitimately omits the root" from
"radial dropped it". Distinguishing them needs a statement of **what each renderer is contracted to
draw** — precisely the different requirement Inc-W1 declined to import.

**The right owner is the DECLARATION requirement, `HLR-N06.3` / `LLR-N06.3.x`, under which `B-55` is
already carried.** The requirements file already records this hole in those words — *"`outline` and
`radial` hide nodes and declare nothing"* (`01-requirements.md:8974`) — and the tree already ships its
derivation: `tests/test_inc3_census.py::painted_ids_exporters()`, pinned by
`test_a98_the_declaring_renderers_are_pinned_as_an_equality` to exactly
`{mapper.views.layered, mapper.views.outline, mapper.views.radial}` — **exactly the three
operator-reachable renderers**, with `lane`'s absence justified by unreachability rather than by
omission, and with `test_a89_the_reached_set_is_pinned_so_wiring_lane_up_pulls_it_in` as the tripwire
for the day that changes. That set is not an accidental proxy: it is a pinned, non-empty-guarded,
tripwired derivation that already means "the renderers that owe the operator a declaration".

**Ownership recommendation:** route the remedy to the `HLR-N06.3` / `B-55` family as a declaration
arm; leave `LLR-N07.2.2b`'s assertions alone. Add one pointer comment in `test_views_hits.py` naming
the arm that carries the trigger, so the next reader of that `else` limb does not re-derive this.

---

## 4 · The remedy I would accept

**Direct answer to "is pinning the three unpinned members the right shape?" — NO.** Pinning `root`,
`first` and `hit` by name is the same defect one generation on. This file's own history is four rounds
of exactly that migration — a named member, a named member list, a named cardinality, a named domain —
and a hand-named drawn-ness roster would be generation five. It would also be **wrong per renderer**:
any such roster must special-case the lane family's root, which is how rosters start rotting.

**What must assert the trigger:** *a source outside the render being judged*. The catalog's form — *an
invariant arm must ASSERT THE TRIGGER ACTUALLY OCCURRED before asserting the invariant* — is met here
by asserting **the node reached the canvas** from a surface that is not that same render's span set.

### 4.1 · `TC-F3-A` — leave-one-out consensus (cross-renderer, no declaration surface needed)

For each renderer `c`, `required(c) = ⋂ drawn(d)` over every **other** derived renderer `d`; assert
`required(c) ⊆ drawn(c)`, with `len(required(c)) >= 3` asserted first so the arm cannot go vacuous.
Nothing is hand-named — not the member, not the renderer, not the cardinality. The renderer under test
is excluded from its own requirement, so its own co-drop cannot shrink it.

**Mutants it must kill (measured in the mirror; proof-of-kill, NOT a delivery):**

| Mutant | `TC-F3-A` |
|---|---|
| clean tree | **GREEN** |
| `radial.py:298` co-drop `first` | **RED** |
| `radial.py:298` co-drop `hit` | **RED** |
| `radial.py:298` co-drop `other` | **RED** |
| `layered.py:594` co-drop `first` | **RED** |
| `lane.py:122` and `lane.py:335` co-drops | **RED** |
| `radial.py:298` co-drop **`root`** | **GREEN — it does NOT kill it** |

**Declared limitations.** (i) It cannot reach `root`, for the reason in §3. (ii) A consensus oracle is
defeated by a **correlated** drop of the same member across enough renderers to empty the
intersection; the floor turns that into a red arm rather than a silent pass, but the message would
then name vacuity, not the defect. That correlated two-renderer mutant is **not-run**.

### 4.2 · `TC-F3-B` — REFUTED BY MEASUREMENT, recorded so it is not re-proposed

The obvious candidate — assert the canvas-derived drawn set equals `painted_ids(...)` for the
renderers that ship it — **kills nothing.** Measured: on all four `radial` co-drops it stayed GREEN,
because `radial.painted_ids` is computed from the very `title_cells` replay the mutant empties. The
declaration drops the node in lock-step with the canvas, so both surfaces agree while the node
vanishes. **That is the `False == False` shape one level up.** Recorded precisely because it looks
like the right answer.

### 4.3 · `TC-F3-C` — the declaration asserted against the FIXTURE (recommended)

Not "does the declaration match this render", but **"a 4-node map in a 120×24 frame hides nothing, so
every declaring renderer must declare every node painted"**. The fixture is the test's own input, so
this is an independent expectation, not a mirror of the artifact under verification:

```python
for module in painted_ids_exporters():        # the SHIPPED derivation, pinned by A-98
    assert set(module.painted_ids(_graph(), ViewState(w=120, h=24))) == set(_graph().nodes)
```

with the exporter set asserted non-empty (already done by
`test_a98_the_participation_census_input_is_non_empty`) and a floor of 3 declaring renderers.

**Mutants it must kill (measured; proof-of-kill, NOT a delivery):**

| Mutant | `TC-F3-C` |
|---|---|
| clean tree (53 arms incl. the shipped 50) | **GREEN** |
| `radial.py:298` co-drop `root` | **RED** |
| `radial.py:298` co-drop `first` | **RED** |
| `radial.py:298` co-drop `hit` | **RED** |
| `radial.py:298` co-drop `other` | **RED** |
| `outline.py:251` co-drops | **RED** |

It kills **all four**, including the `root` case no cross-renderer oracle can reach, and for the right
reason: under the mutant `radial`'s header honestly declares **1 hidden** on a frame where nothing
needs hiding — `HLR-N06.3`'s own defect, and operator-visible.

**Declared limitation:** a second-order mutant that drops the drawing **and** falsifies the
declaration defeats `TC-F3-C`. That shape is a direct `B-55` violation and is the business of the
`AT-059` / `AT-057` declared-set-equals-frame arms. **I did not fire it — `not-run`.**

### 4.4 · The shape I would accept, in one sentence

**`TC-F3-C` as the delivered arm, in the `HLR-N06.3` / `B-55` family (`tests/test_inc3_census.py` or
wherever the declaration arms live), reusing `painted_ids_exporters()` rather than a fresh `hasattr`
sweep; `TC-F3-A` optional as a cheap cross-renderer backstop that also covers the lane family the day
it is wired up; and a pointer comment at `test_views_hits.py:354` naming the arm that carries the
trigger — so the `else` limb stops looking self-sufficient.** No change to `LLR-N07.2.2b`'s assertions
is needed or wanted.

**Do not lean on the floor at `test_views_hits.py:298` (`len(hittable) >= 3`).** It is
cardinality-shaped, and the measurement refutes the tempting story about it: `layered` dies with 4
hittable while `radial` survives with 4 — so whatever protects the other renderers, it is **not** the
floor. I did not isolate which sub-assertion of `…EVERY_member_of_the_hit_set_is_painted` fired in
those kills; that is **not-run**, and worth one probe before anyone reasons from it.

---

## 5 · What I did NOT run — explicit

| Not run | Why |
|---|---|
| The gate suite in the repo | The ONE complete gate-suite run belongs to the orchestrator (`C-25`). I ran only in my mirror. |
| The `slow` lane (`-m slow`) and the `network` lane | Out of this finding's scope; deselected by `addopts` and left deselected. |
| `.dev-flow/`-reading arms (`test_repair_artifact_claims`, `test_repair_golden_census`, `test_fold`'s artifact sweep) | 6 arms fail in the mirror for want of `.dev-flow/`; mirror infrastructure, constant across all runs, touch no renderer. |
| A subtler co-drop at `outline.py:251` and `lane.py:335` | My mutant there reddened 9 arms — too coarse to establish immunity. Their exposure is **undetermined**, not cleared. |
| The correlated two-renderer co-drop that would defeat `TC-F3-A` | Named as a declared limitation, not measured. |
| The second-order mutant that drops the drawing AND falsifies the declaration (defeats `TC-F3-C`) | Belongs to the `AT-059`/`AT-057` declared-set arms; not fired. |
| Isolating which sub-assertion of `…EVERY_member_of_the_hit_set_is_painted` kills the `layered` and `lane` co-drops | Would change how the `>= 3` floor is described; left as an open probe. |
| Driving the TUI itself (Textual pilot) | The observable used is the renderer's own `Text` and its shipped `painted_ids` — the objects `app.py` consumes — not the terminal surface. |
| Any implementation | `software-dev` owns delivery. The candidate arms exist ONLY in my mirror, as `tests/test_zz_f3_candidate.py`. |
| Anything in `FLAKE-1`, `.gitattributes`/`autocrlf`, `SEC-F4`, the socket-level guard, or the 016/017 export-budget work | Excluded by the brief. The CRLF observation in §1 is a measurement fact needed to anchor a mutation, **not** an `autocrlf` opinion. |

---

## 6 · Evidence checklist

| Item | ✓/✗ | Evidence |
|---|---|---|
| Acceptance criteria use Given/When/Then | **n/a — a validation verdict over an existing arm, not a new-feature AC set** | — |
| Test cases have explicit Expected, not vague "works" | ✓ | Every row in §2.3–§2.5 and §4 carries the exact arm id and exact pass/fail counts. |
| Edge cases include empty, boundary, invalid, error | ✓ | Empty title (the mutant); the `w >= 100` boundary; the 4-vs-3 `hittable` cardinality boundary; the collection ERROR handled in §1. |
| Regression checklist exists | ✓ | §2.5 fires the same mutant at every renderer in the derived set; clean-tree GREEN asserted before every RED. |
| Exit criteria stated | ✓ | §4.4 — the arm, its home, and the four mutants it must kill. |
| No real PII / secrets | ✓ | Fixture is `tests/test_views_hits.py::_graph()`; no credentials, no client data. |
| Mode declared at the top | ✓ | Header row — **`validation`**. |
| Every case carries a result or one of the seven states; each executed result NAMES its executor | ✓ | All runs above: **executed by this reviewer (`qa-reviewer`) in the mirror**. Orchestrator-owned runs: **not-run here** (§5). |
| Layer B (black-box) through the shipped surface | ✓ partial | Observed through `IRenderer.render` and the shipped `painted_ids` — the same surfaces `app.py` consumes. The terminal itself was not driven; declared in §5. |
| Bidirectional surface-reachability | ✓ | Inputs (hit set, width, selection) driven through the handler; outputs (spans, plain text, declared painted set) read out of the render, never out of the source. |
| No unfilled template | ✓ | No placeholder that names nothing; the single `n/a` carries its reason. |
