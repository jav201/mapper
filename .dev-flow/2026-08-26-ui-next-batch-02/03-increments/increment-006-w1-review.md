# Code Review — Inc-W1 (confirmation pass, scoped to the design call)

**Batch:** `2026-08-26-ui-next-batch-02` · **Increment:** `Inc-W1` · **Repo:** `C:\Users\jjgh8\Github\mapper`
**Reviewer:** `code-reviewer` (independent) · **Date:** 2026-09-10
**Scope:** the design call and its correctness. NOT a re-audit of the renderers.

---

## BLUF

**W1 is genuinely closed, and the `TITLES` derivation is sound rather than circular — both
independently proven, not taken on the packet's word.** The two shapes that survived everything
before this increment (`WIDE drop first`, `WIDE drop hit` at `radial.py:232`) were re-fired by this
pass against the pre-increment oracle and the post-increment oracle: **SURVIVED → KILLED**, and the
killing arm is the generalised boundary itself, at exactly one node id.

I am nonetheless **BLOCKING on one HIGH finding**, and it is not the mechanism — it is a declaration.
The increment is titled *"the last hand-spelled thing removed"*, its gate checklist carries a checked
`[x] Derived, not named — the domain AND the titles`, and the in-code comment at
`tests/test_views_hits.py:282` reads `THE DOMAIN AND THE TITLES BOTH COME FROM THE FIXTURE, spelled
nowhere`. Seven lines below that comment, **the domain is spelled**:

```python
ALL = ("root", "first", "hit", "other")      # tests/test_views_hits.py:289
```

The increment derived the titles and left the ids. That is the same "correct fix to the exact
instance named, mirror left standing" shape that blocked Inc-5 twice. The fix is one line, and I
verified it green with W1 still killed.

---

## Scope reviewed

| | |
|---|---|
| Diff | `tests/test_views_hits.py`, one hunk, `@@ -279,7 +279,15 @@` and `@@ -293,18 +301,33 @@` — read in full |
| Arm | `test_llr_n07_2_2b_EVERY_member_of_the_hit_set_is_painted`, lines 226–342 |
| Source files | **0** — `git status --porcelain -- mapper/` empty, confirmed |
| Entry pins | all four sha256 pins matched at entry AND at exit; `layered.py` no diff vs HEAD |

---

## 1 · Is the `TITLES` derivation sound, or circular?

**Sound. Not circular.** The packet's §2.1 claim survives audit. Traced rather than accepted:

**The read path carries no product transformation.** `_graph()` is authored in this module
(`tests/test_views_hits.py:50-71`). It reaches product code only through `mapper.model` —
`Graph`, `Node`, `Ficha`, `Edge`. I read all four:

- `Graph.add_node` (`mapper/model.py:141-144`) is `self.nodes[node.id] = node` — verbatim storage.
- `Graph.nodes` is a plain `dict[str, Node]` (`model.py:93`).
- `Ficha` is a plain `@dataclass` with `title: str = ""` and **no `__post_init__`** (`model.py:26-32`).

So `fixture.nodes[m].ficha.title` is byte-identical to the string literal on the line above it in the
same file. The derivation is an identity over the test's own input. **`mapper.views.*` — the artifact
under verification — is nowhere on that path.**

**The assertion stays independent, in the direction that matters.** The boundary is
`(m in hittable) == (TITLES[m] in drawn)`. `TITLES[m]` supplies only the **key**; both sides of the
equality are read out of **rendered output** (`hittable` from spans, `drawn` from `t.plain`).
`HIT_STYLE` is pinned at module level (`:36`) and never imported from a renderer. The reader-as-oracle
defect would be `TITLES = {m: extract_from(rendered)}`. This is the opposite: it is the input.

**Where the claim is looser than its own wording, honestly stated.** The docstring says `HIT_STYLE`
"is pinned in this module and never imported from a renderer." True — but it is built from
`darkside.INK` / `darkside.STEP`, the same design-system tokens the renderers read. A change to those
tokens moves both sides together. That is a shared-vocabulary dependency rather than a mirror,
`darkside` has its own census, it is **pre-existing and untouched by W1**, and it does not affect the
W1 verdict. Noting it so the boundary claim is not read as broader than it is.

**Verdict on the design call: the derivation is legal, and the coordinator's ruling was right to
allow it.** A test may say what it asked for. This says what it asked for.

---

## 2 · Does the generalised boundary actually close W1? — proven by mutation

Built the mutants myself. Site `radial.py:232` is `elif nid in hits:` (anchor verified: **1**
occurrence in the file — not zero).

### 2.1 · The decisive control — the same mutant against both oracles

| Mutant at `radial.py:232` | vs **pre-increment** oracle (`HEAD`) | vs **Inc-W1** oracle |
|---|---|---|
| `WIDE drop first` (`w >= 100`) | **SURVIVED** — 50 passed | **KILLED** — 1 failed, 49 passed |
| `WIDE drop hit` (`w >= 100`) | **SURVIVED** — 50 passed | **KILLED** — 1 failed, 49 passed |

Both killed by exactly one node id, and it is the arm this increment edited:

```
tests/test_views_hits.py::test_llr_n07_2_2b_EVERY_member_of_the_hit_set_is_painted[radial.RadialRenderer]
```

W1 was live, and this increment is what closes it. **Not inherited from the packet — re-measured.**

### 2.2 · The full 8-mutant sweep at the site, all KILLED

| | root | first | hit | other |
|---|---|---|---|---|
| **FLAT drop** | KILLED (1) | KILLED (2) | KILLED (3) | KILLED (2) |
| **WIDE drop** (`w>=100`) | KILLED (1) | **KILLED (1)** | **KILLED (1)** | KILLED (2) |

*(parenthesis = failing arms)*. Note the WIDE column: `root`, `first`, `hit` each die to **one arm
only** — the generalised boundary. Nothing else in the 50 sees them. That is the increment's load
being carried, and it is measurable rather than argued.

### 2.3 · The boundary holds exactly, 6 renderers × 4 members

Measured `drawn` against `hittable` at w=120 for every pair — the equality is exact everywhere, no
member relies on slack:

| Renderer | root | first | hit | other |
|---|---|---|---|---|
| `HybridLaneRenderer` | 0=0 | 1=1 | 1=1 | 1=1 |
| `LaneRenderer` | 0=0 | 1=1 | 1=1 | 1=1 |
| `RailTimelineRenderer` | 0=0 | 1=1 | 1=1 | 1=1 |
| `LayeredRenderer` | 1=1 | 1=1 | 1=1 | 1=1 |
| `OutlineRenderer` | 1=1 | 1=1 | 1=1 | 1=1 |
| `RadialRenderer` | 1=1 | 1=1 | 1=1 | 1=1 |

---

## Findings

### F1 — the DOMAIN is still hand-spelled, while the comment, the checklist and the title all say it is not  [Severity: HIGH]

- **What:** `TITLES` was derived from the fixture; `ALL` was not. The increment applied the
  coordinator's ruling to the titles and left the ids — and then declared the job finished.
- **Where:** `tests/test_views_hits.py:289` (`ALL = ("root", "first", "hit", "other")`), contradicted
  by the comment at `:282`, by the packet's gate checklist line 116, and by the increment's own title.
- **Why it matters:** three separate reasons, in order of weight.
  1. **A checked gate box is false.** `[x] Derived, not named — the domain AND the titles… No literal
     member list or title string survives inside the quantifier.` A literal member list survives, on
     the line between the two derived things. Under the batch's own "fail loud" rule, a checked box
     that is false is worse than an unchecked one.
  2. **The drift it leaves is asymmetric, and the silent half is the dangerous half.** A **rename** in
     `_graph()` is loud — `fixture.nodes[m]` raises `KeyError`. An **addition** is silent: a fifth node
     stays outside `ALL`, therefore outside the domain, outside the B-55 boundary, and outside the
     unions. **That is W1's own failure mode** — a member the derivation never sees — reinstated one
     level up, in the increment written to end it.
  3. **It is the batch's recurring shape at generation six.** Inc-5's five rounds were: a named member
     → a named member list → a named cardinality → a named domain. W1 found the fifth. `ALL` is the
     sixth, and it is sitting in the diff.
- **Suggested fix** — one line. The tuple is a drop-in: `tuple(fixture.nodes)` is
  `('root', 'first', 'hit', 'other')`, identical members, identical order (verified).

```python
    fixture = _graph()
    ALL = tuple(fixture.nodes)          # was: ("root", "first", "hit", "other")
    TITLES = {m: fixture.nodes[m].ficha.title for m in ALL}
```

- **Fix verified by this pass, not proposed blind:**

| | clean run | `WIDE drop first` | `WIDE drop hit` |
|---|---|---|---|
| Inc-W1 as written | 50 passed | KILLED | KILLED |
| **with F1 fix applied** | **50 passed** | **KILLED** | **KILLED** |

- Also correct the comment at `:282` and the packet's line 116 in the same edit — or the next reviewer
  audits the same sentence again.

---

### F2 — the substring boundary now runs at ZERO clip margin on `RadialRenderer`  [Severity: MEDIUM]

- **What:** `TITLES[m] in drawn` is a substring test, so it is only sound while every fixture title
  survives every renderer's clip whole. Generalising the boundary from `root` alone to all four
  members moved the binding member from the **shortest** title to the **longest** — and consumed the
  entire margin.
- **Where:** `tests/test_views_hits.py:326` against `mapper/views/radial.py:221`
  (`title = darkside.plain(node.ficha.title)[:18]`).
- **Why it matters:** measured headroom per renderer at w=120 (longest title still wholly present):

| Renderer | max whole title | fixture's longest (`analisis de riesgo`, 18) | margin |
|---|---|---|---|
| `RadialRenderer` | **18** | 18 | **0** |
| `LayeredRenderer` | 23 | 18 | 5 |
| the other four | 59+ | 18 | ample |

  Before this increment the boundary keyed on `"Raiz del mapa"` (13) — margin 5 on radial. It is now
  **0**. I reproduced the consequence: with the `hit` slot at **19** characters, `RadialRenderer`
  false-fails with `draw=False, paint=True` and a message that **accuses the renderer** of a B-55
  violation it did not commit. `C-53` prices a false-fail exactly as high as passing a wrong one.
  The sting is that deriving `TITLES` was sold as making fixture edits safe in one place — and a
  title edit is precisely what trips this.
- **Suggested fix:** follow this file's own precedent at `:192`, which already separates "not drawn"
  from "clipped" with its own message. Add the precondition before the boundary so the two failure
  modes stay distinguishable:

```python
    # THE BOUNDARY IS A SUBSTRING TEST, so it is sound only while no fixture title
    # outgrows a renderer's clip.  Measured: `radial.py:221` clips at [:18] and the
    # longest title is exactly 18 -- zero margin.  Asserted, not assumed, because a
    # clipped title reddens the boundary with a message blaming the renderer.
    for m in ALL:
        if m in hittable:
            assert TITLES[m] in drawn, (
                f"{cls.__name__} paints a {m} hit but the fixture's title "
                f"{TITLES[m]!r} does not survive this renderer's clip whole; this "
                "arm has stopped measuring the paint and is measuring the clip"
            )
```

  (then the existing `for m in ALL: assert (m in hittable) == (TITLES[m] in drawn)` keeps its meaning
  and can only fire for the reason its message states).

---

### F3 — the boundary is an EQUIVALENCE, and a co-drop mutant walks through it and the whole 904-arm lane  [Severity: MEDIUM]

- **What:** my own attack line, not the packet's. `(m in hittable) == (TITLES[m] in drawn)` is
  satisfied by `False == False`. A mutant that stops **drawing** a member as well as **painting** it
  therefore passes the boundary rather than reddening it.
- **Where:** boundary at `tests/test_views_hits.py:325-330`; mutant built at `mapper/views/radial.py:221`.
- **Measured:**

```
CO-DROP first @ radial.py:221 (w>=100)   -- 50-arm file      SURVIVED  (50 passed)
CO-DROP first @ radial.py:221 (w>=100)   -- FULL default lane SURVIVED  (904 passed, 17 deselected, 3 xfailed)
```

  The mutant is not equivalent — it makes `RadialRenderer` draw an empty title for `first` at w ≥ 100,
  a real and visible behaviour change — and nothing in the repository reddens.
- **Why it matters:** the increment's stated argument is that "a bare derivation would silently ABSORB
  the defect." The generalised boundary closes the **drop-paint** half of that absorption channel. The
  **drop-both** half is still open, reachable by the same width-conditioned mechanism, at the adjacent
  line of the same function. The reason it stays open is structural and worth naming: the boundary is
  only as strong as the independent pinning of `drawn`, and **exactly one of four members has its
  drawn-ness pinned** — `other` / `"Cronograma"`, by the sibling arm at `:192`. `root`, `first` and
  `hit` have none.
- **This does not invalidate W1's closure** (§2 stands on its own) and the defect class is *drawing*,
  not *hit-painting*, so it is arguably outside this file's `AT-024` charter.
- **Suggested fix:** do **not** widen this arm — that would be scope creep into a different
  requirement. Two honest options:
  1. Declare it in §5 Carries in the words above, so no later reader believes the absorption channel
     is fully closed; **and**
  2. route the coverage gap to `qa-reviewer` (a renderer can stop drawing a node's title entirely at
     w ≥ 100 with 904 arms green — that is a suite-level hole, not an oracle-design one).

---

### F4 — a hand-spelled title survives one arm above the one that removed hand-spelled titles  [Severity: LOW]

- **What:** `title = "Cronograma"` — the exact class of literal the coordinator's ruling abolished.
- **Where:** `tests/test_views_hits.py:183`.
- **Why it matters:** rename `other`'s title in `_graph()` and this arm false-fails on all six
  renderers with `"no longer draws the third branch at 120 columns"` — a message that misdescribes
  what happened. Same failure shape F1 describes, in the arm next door.
- **Suggested fix:** `title = _graph().nodes["other"].ficha.title` — or fold it in when F1 is applied,
  since both are the same edit in spirit.

---

### F5 — the arm's docstring understates its own coverage  [Severity: LOW]

- **What:** the docstring says *"For each subset of size 2 and 3"*; the loop is
  `range(2, len(hittable) + 1)`.
- **Where:** `tests/test_views_hits.py:251` vs `:333`.
- **Why it matters:** stale in the safe direction, but it is prose drifting from a derived truth — the
  batch's signature defect. Measured: with `root` now in the domain, `LayeredRenderer`,
  `OutlineRenderer` and `RadialRenderer` reach `hittable=4` and exercise cardinalities **[2, 3, 4]`;
  the three lane renderers reach `hittable=3` and exercise **[2, 3]**.
- **Suggested fix:** "for every subset of size 2 up to `len(hittable)`, which is 3 on the lane family
  and 4 on the three renderers that draw the root."
- *(Adjacent, pre-existing, not in this diff: `_graph()`'s docstring at `:51` says "FOUR branches"
  where the fixture has four **nodes** and three branches. Flagging only; out of scope.)*

---

## 3 · Is the 14-survivor equivalence claim honest? — re-proved on a sample

Built an **independent** digest instrument (my own hashing scheme; my `SHIPPED` is `52a1c5ee9f4c6cfe`,
the packet's is `c231ba3f3d6d0e12` — different instruments, same grid). Grid re-derived
independently and lands on the packet's figure exactly: 6 renderers × 16 subsets × 3 widths
(80/100/120, spanning the mutants' own 100-column boundary) × 3 selections = **864 renders**.

Sampled 5 of the 14 claimed survivors, with a positive control at every site:

| Mutant | site | claimed | **re-proved** | digest |
|---|---|---|---|---|
| drop `root` | `lane.py:228` rail-trunk (S4) | EQUIVALENT | **EQUIVALENT** | `52a1c5ee…` |
| drop `hit` | `lane.py:228` rail-trunk (S4) | EQUIVALENT | **EQUIVALENT** | `52a1c5ee…` |
| drop `first` | `lane.py:291` rail-label (S5) | EQUIVALENT | **EQUIVALENT** | `52a1c5ee…` |
| drop `root` | `lane.py:133` LaneRenderer (S3) | EQUIVALENT | **EQUIVALENT** | `52a1c5ee…` |
| drop `root` | `lane.py:354` HybridLane (S6) | EQUIVALENT | **EQUIVALENT** | `52a1c5ee…` |
| **ctrl MAX** | `lane.py:228` | DIFFERS | **DIFFERS** | `1d48cef5…` |
| **ctrl MAX** | `lane.py:291` | DIFFERS | **DIFFERS** | `634d7893…` |
| **ctrl MAX** | `lane.py:133` | DIFFERS | **DIFFERS** | `70676f1b…` |
| **ctrl MAX** | `lane.py:354` | DIFFERS | **DIFFERS** | `c471cd05…` |

**Every sampled verdict matches, and all four controls fire.** The stated reasons check out against
the source: the lane family never draws the root; `lane.py:228` handles `branches[0]` only
(`main_branch = branches[0]`, `:222`); `lane.py:291` iterates `branches[1:]` (`:249`).

**An instrument failure worth recording, because it is the pass's own `C-56` lesson.** My first
digest run passed a POSIX `/tmp` path to a Windows interpreter. Every invocation returned the *same
error string*, so every mutant compared equal and printed `EQUIVALENT` — a clean sweep of false
survivals. **The positive controls are what caught it**: four rows that must differ, didn't. I added a
hard guard (`renders=864` must appear or the run aborts as BROKEN, never as SURVIVED) and re-ran. This
is the same defect class as an anchor matching zero times, and it is the argument for controls in one
line.

---

## 4 · Packet figures — every one verified independently

| Claim | Verified | How |
|---|---|---|
| `904 passed, 17 deselected, 3 xfailed` | **CONFIRMED**, exit 0 | direct clean run, 208.70s |
| all markers `921 passed, 3 xfailed` | **CONFIRMED**, exit 0 | `-m ""`, 233.81s |
| ruff SET `27 = 27`, zero NEW, zero GONE | **CONFIRMED** | `--isolated` **both sides**, run **inside** the repo; HEAD side via `git show`, restored + sha-asserted. Set-diff, not a count compare: `NEW=none`, `GONE=none`, `SET-IDENTICAL: True` |
| 50 arms, zero skipped | **CONFIRMED** | `--collect-only` → 50 collected; `-rs` → `50 passed`, no skip line |
| census `argful 59, zeroarg 26, defs 7` | **CONFIRMED** | pinned and asserted in `tests/test_a3_census.py:191/197/201`; green in both runs. `fixture = _graph()` is not a `.render(` call, so the pin correctly does not move |
| `git status -- mapper/` empty | **CONFIRMED** | `--porcelain -- mapper/` → no output |
| `layered.py` byte-identical to HEAD | **CONFIRMED** | `git diff --stat` → empty (CRLF-normalised comparison) |
| battery `56 = 2 × 4 × 7` | **arithmetic and site count check out** | 7 hit sites derived independently: `lane.py:133/228/291/354`, `outline.py:130`, `radial.py:232`, `layered.py:528`. Survivor table sums to 14 |

**Sole-writer discipline held.** Every mutation restored from original bytes inside a `finally`,
sha256-asserted byte-identical after each cycle, `__pycache__` purged, `PYTHONDONTWRITEBYTECODE=1`,
`--color=no` throughout, plain-string anchors at verified occurrence indices (`elif bid in hits:`
occurs **3** times in `lane.py` — asserted and indexed, never blind-replaced).

**Final pin state — all MATCH:**

```
MATCH tests/test_views_hits.py   0e1e6d1a8b97b099…
MATCH mapper/views/outline.py    06a0e9493f10bbc3…
MATCH mapper/views/radial.py     aa462076e911c398…
MATCH mapper/views/lane.py       098b90b4baad538e…
MATCH mapper/views/layered.py    (no diff vs HEAD)
```

---

## Evidence checklist

- [x] **Diff read in full** — `tests/test_views_hits.py`, both hunks, plus the whole 402-line file and all 7 hit sites in `mapper/views/`.
- [x] **Correctness pass (edge / None / error paths)** — boundary measured exactly across 6×4; clip edge found at 19 chars (F2); equivalence-form edge found and exploited (F3).
- [x] **Simplicity pass** — the diff is one derivation plus one loop replacing one assertion. No premature abstraction; the loop is the right shape. F1 makes it *simpler*, not more clever.
- [x] **Reuse / duplication checked** — `_graph()` reused rather than re-spelled (the increment's point); residual duplication found at `:289` (F1) and `:183` (F4).
- [x] **Tests reviewed for intent** — the arm encodes WHY (a dropped member must be re-externalised against what was drawn); proven able to go RED by 8 killed mutants at S2, and proven to have *newly* gained that ability by the HEAD-vs-Inc-W1 control.
- [x] **Verdict explicit** — below.

---

## Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **Block — must fix the HIGH finding before advancing**

**HIGH count: 1** (F1). MEDIUM: 2 (F2, F3). LOW: 2 (F4, F5).

**What the block is and is not.** It is **not** a block on the mechanism: W1 is closed, proven by a
mutant that was SURVIVED against the old oracle and is KILLED against the new one, and the derivation
is sound. It **is** a block on a declaration — a gate box checked `[x]` for a property the code does
not have, over the one construct (`ALL`, the domain) that W1 was about. The remedy is one verified
line plus two sentence corrections. F2 should be fixed in the same edit (it costs five lines and
removes a false-fail whose message would blame the renderer). F3 should be **declared as a carry and
routed to `qa-reviewer`**, not fixed here — widening this arm into drawing coverage would be scope
creep.

**On the `TITLES` derivation, explicitly:** the derivation of `TITLES` from `_graph()` is **sound, not
circular** — `_graph()` is test-owned, `mapper.model` stores the title verbatim with no
transformation on the read path, the artifact under verification (`mapper/views/*`) is nowhere on
that path, and `TITLES` supplies only the key while both sides of the assertion are read from
rendered output.

---

### Routing

- `qa-reviewer` — F3: a `RadialRenderer` co-drop at w ≥ 100 survives the full 904-arm lane; three of
  four fixture members have no independent drawn-ness pin.
- `security-reviewer` — nothing. Tests-only, zero source files, no new external surface, no secrets.
