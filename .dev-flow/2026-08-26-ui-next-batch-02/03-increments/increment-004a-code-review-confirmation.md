# Code Review — Increment 004a · CONFIRMATION PASS (round 2)

| Field | Value |
|---|---|
| Reviewer | `code-reviewer`, independent confirmation. Author does not self-clear |
| Branch / entry | `feat/ui-next-batch-02` @ `5f4816c`, **nothing committed** |
| Under confirmation | `increment-004a-code-review.md` F1 (HIGH), F2 (HIGH), and M1 / M2 / F7 |
| Author's response | `increment-004a.md` §"Review round 2" (R0–R8) |
| Method | isolated `git clone --local --no-hardlinks` mirror + working-tree overlay; **14 mutations executed**, per-arm verdicts, sha256 restores |
| Real repo | **never mutated** — 5 source digests identical at start and finish |
| **Verdict** | **PASS** — both HIGHs discharged. 5 NEW findings, none HIGH |

---

## 0 · BLUF

**Both HIGH findings are genuinely discharged, and I confirmed them by executing
mutations rather than by reading the author's table.** All six candidate shapes redden
against the rebuilt arm; the perf fix is output-identical over 380 independently
constructed cases including cycles, self-loops, diamonds, dangling edges and a
4000-deep chain, with no hang and no `RecursionError`.

**The author was right to decline the round-1 suggested fix, and I proved it.** Applied
verbatim to unmutated source, that predicate is **RED** — it would have reddened correct
code. The substitute is better targeted, not weaker.

**But the rebuilt arm still has one seam, and I constructed the defect through it.**
Narrowing the hit set inside `_search_hits` — one level below the pinned `hits=`
argument — makes the count and the paint disagree on the shipped `adjuntos` fixture
(count says 5, paint highlights 4) and passes the **entire fast lane: 818 passed,
exit 0, zero FAILED**. That is the same defect class the increment claims to have
closed, relocated by one method. It is a **MEDIUM**, not a HIGH: the shipped code is
correct, the LLR's named target is now genuinely banned, and the fix is one token.

---

## 1 · Mirror fidelity — established BEFORE any mutation

The previous reviewer's harness blocked every file edit. Mine did not, so nothing here
rests on trust.

| Step | Result |
|---|---|
| `git clone --local --no-hardlinks` → mirror at `5f4816c` | ok |
| Working-tree overlay of `mapper/` + `tests/` | **all `.py` digests byte-identical to the real repo** |
| First mirror run | `1 failed, 817 passed` — `test_a3_census` only |
| Cause | **mirror artifact, not a defect.** The A3 census reads the git index; `tests/inc4_support.py` and `tests/test_search.py` are staged in the real repo, untracked in a fresh clone. Reproduced the real index state with `git add -N` |
| **Baseline after index fix** | **`818 passed, 17 deselected, 3 xfailed`, exit 0** — exact reproduction of the brief |

**Digest cross-check.** My mirror's pre-battery digests match the author's declared
values exactly — independent evidence that we measured the same tree and that the
author's own restores were clean:

```
app.py          a2b621256c22e533   (author declared a2b621256c22e533)
search.py       77836620bbddec54   (author declared 77836620bbddec54)
test_search.py  bd035104c012dee8   (author declared bd035104c012dee8)
```

---

## 2 · H2 — the shared-resolution arm · **DISCHARGED**

### 2.1 · The six shapes, re-executed (author's table NOT taken on trust)

Node: `test_the_count_and_the_paint_share_one_resolution`. One verdict **per resolved
arm**, arm count asserted at 1 before any verdict was trusted; never the process exit
code. Every mutation described by position and operation; no mutated token spelled.

| id | position · operation | verdict |
|---|---|---|
| **V1** | `_count_line`, the line taking the resolved order → resolves for itself via the owner, helper reference removed *(the historical defect)* | **RED** |
| **V2** | `_count_line` → an independent resolution added **beside** the retained helper call | **RED** |
| **V3** | V2, the added path scoped to the viewport *(the A-6 defect)* | **RED** |
| **V4** | `_count_line` → helper stays pure, the count line narrows its result by the fold set | **RED** |
| **V5** | `MapScreen` → a **new fourth consumer** resolving independently *(Inc-4b's shape)* | **RED** |
| **V6** | `_view_state`, the hit argument → narrowed at the seam while the count stays pure | **RED** |

```
variants run: 6   RED: 6   INERT: 0
post-battery app.py sha256 a2b621256c22e533  identical=True
```

**The author's table is accurate.** The three shapes that passed the old arm (V2, V3, V4)
now redden, as do V5 and V6. Round-1 F1 is genuinely closed for every shape it named.

### 2.2 · Was declining the `_view_state` ban correct? · **YES — executed, not argued**

Round 1 suggested banning `folded`/`pan_x`/`pan_y` from `_view_state`. I applied that
predicate **verbatim** to the arm and ran it against **unmutated** source:

| mutation | verdict |
|---|---|
| the round-1 predicate applied as written, source untouched | **RED** |

`_view_state` reads all three legitimately at `app.py:1891-1893` — handing the viewport
to the renderer is its whole job. **The round-1 fix would have reddened correct code.**
The author's correction stands, and the substitute — banning `_count_line` (where the
LLR's wording actually lands) and pinning `hits=` structurally — targets the defect
rather than a proxy for it. **This is the right call, and better than what I would have
been confirming.**

### 2.3 · NEW-1 · The ban stops one method short of its own claim · **MEDIUM**

**Where:** `tests/test_search.py:610` (the ban tuple) vs `mapper/app.py:1871-1873`.

The ban covers `_search_order` and `_count_line`. The chain from resolution to the
pinned argument is `_search_order` → **`_search_hits`** → `_view_state.hits=`.
`_search_hits` is the one link under no ban — it is checked only for membership
(`:616`).

I moved the narrowing into it and ran the arm:

| id | position · operation | arm | full lane |
|---|---|---|---|
| **C1** | `_search_hits`, its body → the derivation narrowed by the fold set; every named surface untouched, `hits=` still a bare call | **GREEN — slips** | **818 passed, exit 0, zero FAILED** |

**This is not a harmless mutant.** Executed on the shipped `adjuntos` fixture, for each
of the three hits that are foldable branches:

```
fold 'riesgo-root' : count N=5 | shipped paint 5 | C1 paint 4   DISAGREE
fold 'b'           : count N=5 | shipped paint 5 | C1 paint 4   DISAGREE
fold 'c'           : count N=5 | shipped paint 5 | C1 paint 4   DISAGREE
```

The collapsed node is still drawn, so it loses its highlight while the count still
counts it — the count and the paint disagree on screen, which is the defect US-N07
exists to close. The arm's own docstring says the `hits=` pin exists so "the hit set
cannot be filtered by [the viewport]"; the pin is on the **argument**, one level above
where the derivation lives.

**Why MEDIUM and not HIGH.** The shipped code is correct. `LLR-N07.2.1`'s named target —
the count computation — is now genuinely banned in both its methods. The gate went from
closing 2 of 5 probed shapes to 7 of 8. This is a residual seam, not an ungated headline.

**Suggested fix — one token,** and unlike the round-1 snippet it is free, because
`_search_hits` reads no viewport state today:

```python
for method in (MapScreen._search_order, MapScreen._search_hits, MapScreen._count_line):
```

`_view_state` correctly stays out.

### 2.4 · NEW-4 · The constructed-once census reads a bare Name · **LOW**

| id | position · operation | arm |
|---|---|---|
| **C2** | `MapScreen` → a fourth consumer reaching the owner through a local alias, so the census sees no `Name` call | **GREEN — slips** |

An inherent limit of any AST census, and a contrived shape. Recorded for completeness,
not as something to fix — the `search_hits` raw-resolver census already covers the
realistic bypass.

---

## 3 · H1 — the perf fix · **DISCHARGED**

### 3.1 · Output identity, independently derived

The pre-fix algorithm was reconstructed **in my probe** (per-node `children_of`, no early
return, membership set rebuilt inside the comprehension), so no file was edited between
readings.

| suite | cases | mismatches |
|---|---|---|
| Hostile fixtures × 8 queries — 4-cycle, self-loop, diamond, dangling edge, disconnected component, all-at-once, empty graph, single node, root self-loop, **4000-deep chain** | 80 | **0** |
| Randomised differential — 300 graphs × 4 queries, cyclic multigraphs with phantom edges | 1200 | **0** |
| `tree_order` compared directly | 10 fixtures | **0** |

`shipped == fixed : True`. The documented `len(query(q)) == len(hits(q))` invariant was
asserted on **every** case and held.

**No hang, no `RecursionError`.** The 4000-deep chain resolves in **0.0047 s** — the walk
is iterative with an explicit `seen` set, so depth costs nothing. Blank and whitespace
queries return in **0.0000 s**, confirming the early return.

### 3.2 · The memo — probed hardest, as the author asked

| id | position · operation | arm | verdict |
|---|---|---|---|
| **D** | `_open_paint_pass`, its body → made a no-op, so the memo outlives its pass | memo arm | **RED** |
| **E** | `_search_order`, the size comparison → bound raised so it is never reached | bound arm | **RED** |
| **F** | `search.query`, the empty-hit early return → deleted | no-walk arm | **RED** |

**Can the memo serve a stale result? Yes — but only where the author says it can.**
Executed: an in-place graph mutation inside one pass (object identity unchanged, query
unchanged) **does** serve a stale order; across a pass boundary it does not. That is the
memo behaving as designed. The question is whether a live path reaches it.

**Settle-chase: NOT a stale path.** `_declare_after_layout` calls `_open_paint_pass()` at
its own top (`app.py:1573`) before re-scheduling, so each chase pass resolves fresh. The
protocol holds there.

**Every graph mutator repaints — verified by census.** The ficha editor mutates
`node.ficha` in place and calls `refresh_canvas()` at `app.py:1994`, dropping the memo.
The one non-repainting mutator (`action_factory`, `app.py:652`) is on a different screen
and builds its own graph. **I could not construct a live stale paint, and I say so.**

### 3.3 · NEW-2 · Two readers sit outside any pass, and the pin does not see them · **MEDIUM**

**Where:** `mapper/app.py:1463` (`_pan`), `:2308` (`action_export_svg`); pin at
`tests/test_search.py:818-819`.

AST census of every method reaching the resolver:

```
OK       refresh_canvas          1896   opens a pass
OK       _declare_after_layout   1545   opens a pass
NO-PASS  _pan                    1463   reaches _view_state
NO-PASS  action_export_svg       2308   reaches _view_state
```

The structural pin names **only** `refresh_canvas` and `_declare_after_layout`. It asserts
those two mention `_open_paint_pass`; it does **not** assert that every reader is inside a
pass. So the memo's stated contract ("every repaint opens a pass") is narrower in the
predicate than in the prose — the same shape as round-1 F1, on a different construct.

**Not live today** (§3.2), so MEDIUM rather than HIGH. But `Inc-4b` adds a fourth consumer
bound to a keypress, and a keypress handler is exactly the shape of the two that already
sit outside. **Suggested fix:** invert the pin — census every method that reaches
`_view_state` / `_count_line` / `_search_order` and assert it either opens a pass or is
itself one of the resolver helpers.

### 3.4 · NEW-3 · `_search_order` hands out the memo's own list · **LOW**

**Where:** `mapper/app.py:1857`, `:1860`.

Executed: a consumer that mutates what it was handed corrupts every later read in the
same pass.

```
first read                          : ['a', 'b', 'c']
after a consumer mutated its result : ['a', 'b']    (is the same object: True)
```

Today's three consumers are read-only, so this is latent. `Inc-4b`'s next-match walk is
the plausible first mutator. **Suggested fix:** store and return a `tuple`, or return
`list(memo[2])`.

---

## 4 · M1 — the `n` ordinal · **DISCHARGED**

**Derived, not spelled — confirmed.** `expected()` computes the cursor's place from an
**independently constructed** `SearchIndex(screen.graph).query(QUERY)`, not from the
screen's `_search_order()`, so it gates that the two agree.

**The fixture-dependence claim is verified by execution:**

```
adjuntos root id        : 'riesgo-root'
resolved order          : ['riesgo-root', 'b', 'd', 'e', 'c']
fresh screen count line : '1/5 coincidencias en el mapa'
cursor moved off a hit  : '0/5 coincidencias en el mapa'
```

`adjuntos` reads **1/5**, exactly as declared, because the root matches by id. A spelled
`0/N` would have been wrong.

**The non-vacuity guard is real.** `assert seen == set(range(0, len(order) + 1))` forces
every ordinal *and* the `0` to be observed, so the loop cannot pass having stayed in one
branch. It also independently constrains the range, so a 0-based implementation would
disagree at every hit rather than sliding through. `MR-6` (ordinal replaced by a constant)
is a live gate.

---

## 5 · M2 — the pin over the dedup · **DISCHARGED**

**The self-guard is real, and it is the discriminating one.** Executed on the graph the
test builds:

```
tree walk                  : ['r', 'c', 'd', 'a', 'b']
insertion order            : ['r', 'a', 'b', 'c', 'd', 'island']
incomplete under tree      : ['c', 'd', 'a', 'b']
incomplete under insertion : ['a', 'b', 'c', 'd', 'island']

guard 1  walked != insertion                     True
guard 2  incomplete subsets DIFFER               True   <- the one that matters
guard 3  the filter drops something              True
guard 4  the unreachable node is excluded        True
agreement asserted AFTER all four                True
```

Guard 2 is asserted **before** the agreement, so a walk that ignored the tree cannot pass.
**C-55 limb 2 is satisfied** — the pin is not vacuous.

Confirmed live by mutation:

| id | position · operation | verdict |
|---|---|---|
| **B** | `_incomplete_order`, the child push → pushed in the opposite order | **RED** |
| **C** | `_incomplete_order` → the tree walk replaced by dict-insertion order | **RED** |

**The judgement call is sound.** `_incomplete_order` is US-N04's shipped ordering, outside
this increment's acceptance. Pinning it here at zero behavioural risk and carrying the
dedup is the correct call in a pass whose purpose is clearing two blocks. I would have
made the same call.

---

## 6 · F7 — the LF/CRLF reversal · **The author's reversal is CORRECT; both rounds missed the real change**

Measured at byte level on the committed blob and on the working tree
(counts are `CRLF` / `LF-only`):

| file | HEAD blob `5f4816c` | working tree |
|---|---|---|
| `mapper/search.py` | 0 / 14 | 0 / 122 |
| `mapper/views/state.py` | 0 / 97 | 0 / 117 |
| `mapper/app.py` | 0 / 2552 | **2673 / 0** |
| `mapper/views/layered.py` | 0 / 666 | **663 / 0** |

**The author is right:** `search.py` was already LF at `5f4816c` — 0 CRLF. Round 1's F7
("newly introduced by this increment") is **false**, and the retraction is correct.

**NEW-5 · But the actual change runs the other way · LOW.** At `5f4816c` the whole repo
was LF. In the working tree, **`mapper/app.py` and `mapper/views/layered.py` have been
converted wholesale to CRLF**; `search.py` is the one that stayed as it was. Neither round
described this. It is **not a gate**: `core.autocrlf=true` and `git diff --numstat` shows
`125/4` and `16/19`, so the diff is not churned and the change is invisible to git. The
author's carry to a repo-wide `.gitattributes` pass is still the right disposition — it
should just name `app.py` and `layered.py` rather than `search.py`.

---

## 7 · Mutation ledger — 14 executed, all restored by sha256

```
pre  app.py           a2b621256c22e533
pre  search.py        77836620bbddec54
pre  test_search.py   bd035104c012dee8

V1 V2 V3 V4 V5 V6      RED    (shared-resolution arm)
C1 C2                  GREEN  (slips -- NEW-1, NEW-4)
A                      RED    (round-1 predicate on correct code)
B  C                   RED    (walk-agreement pin)
D                      RED    (memo pass boundary)
E                      RED    (renderer bound)
F                      RED    (empty-hit early return)

arms run: 14   expected arm count asserted at 1 per run   INERT: 0
post app.py           a2b621256c22e533  identical=True
post search.py        77836620bbddec54  identical=True
post test_search.py   bd035104c012dee8  identical=True
```

Every verdict read **per resolved arm** from the report line, never from the process exit
code. Full-lane runs used for C1 only, where the question was suite-wide blindness.

---

## 8 · What I could NOT verify — stated, not glossed

- **I could not construct a live stale paint through the memo.** §3.2 records what I
  tried: in-place ficha edits (repaint at `app.py:1994`), the settle-chase (opens its own
  pass), the graph-mutator census, and the two pass-less readers. NEW-2 is therefore a
  latent protocol gap, **not** a live defect, and is filed as such.
- **I did not re-run ruff.** The entry/exit set identity (19 pairs / 27 findings) is
  accepted from the brief and the author's R5.
- **I did not re-measure the perf numbers.** Round 1 measured them, the author
  re-measured them, and both agree; I confirmed the property that matters for correctness
  — **output identity** — over 1280 cases of my own construction. The `-m slow` lane was
  not run.
- **I did not re-verify MR-1, MR-2, MR-8, MR-9, MR-10 individually.** V1–V6 and A–F cover
  the same predicates from the reviewer's side; the author's remaining rows are accepted
  on evidence consistent with the digests I measured.
- **`.dev-flow/**` was not reviewed for content**, only this file written into it. No
  mutated token and no hostile code point is spelled anywhere above; every mutation is
  described by position and operation, and no probe literal entered this artifact.

---

## 9 · Evidence checklist

- [x] **Mirror established and fidelity proven BEFORE mutating** — `818 passed, 17
      deselected, 3 xfailed`, exit 0; index state reconciled and the cause named.
- [x] **Diff read in full** — `mapper/search.py:1-123`, `mapper/app.py:1440-1994`,
      `:2244-2340`, `tests/test_search.py:471-887`.
- [x] **Correctness pass** — cycles, self-loops, diamonds, dangling edges, disconnected
      components, 4000-deep chain, empty and single-node graphs; `len(query)==len(hits)`
      asserted on all 1280 cases.
- [x] **Every HIGH re-probed by executed mutation, not by reading the author's table** —
      14 mutations, per-arm verdicts, arm count asserted, sha256 restores proven.
- [x] **The author's decline independently adjudicated** — mutation A, RED on correct code.
- [x] **Tests reviewed for intent** — NEW-1 (ban one method short of its claim), NEW-2
      (pin narrower than the protocol); M1 and M2 self-guards confirmed non-vacuous by
      execution.
- [x] **Real repo never mutated** — 5 source digests identical at start and finish;
      `git status` unchanged at 19 entries.
- [x] **Verdict explicit** — below.

---

## 10 · Verdict

| Finding | Status |
|---|---|
| **F1 (HIGH)** — shared-resolution arm does not gate what it claims | **DISCHARGED** |
| **F2 (HIGH)** — quadratic walk in the repaint path | **DISCHARGED** |
| **M1** — the `n` ordinal ungated | **DISCHARGED** |
| **M2** — `tree_order` / `_incomplete_order` pin | **DISCHARGED** |
| **F7** — LF/CRLF reversal | **Reversal CORRECT** (see NEW-5) |

**NEW findings**

| id | finding | severity |
|---|---|---|
| **NEW-1** | The viewport ban stops one method short of its own claim; narrowing inside `_search_hits` makes count and paint disagree and passes the whole lane | **MEDIUM** |
| **NEW-2** | Two readers (`_pan`, `action_export_svg`) sit outside any paint pass; the structural pin names only the two repaint entry points | **MEDIUM** |
| **NEW-3** | `_search_order` returns the memo's own list; an aliasing consumer corrupts the pass | **LOW** |
| **NEW-4** | The constructed-once census reads a bare `Name` and misses an aliased construction | **LOW** |
| **NEW-5** | `app.py` and `layered.py` were converted LF→CRLF on disk; `search.py` is the one that did not change | **LOW** |

- [ ] Block — must fix HIGH findings before advancing
- [x] **OK with the listed fixes applied first**

**No HIGH remains.** Both blocking findings are genuinely discharged, verified by
executed mutation on a tree proven to reproduce the reviewed state. The author's one
declined fix was the right call and I proved it rather than accepting it.

**Recommended before advancing** — NEW-1 is one token in an existing tuple and closes the
last seam on the increment's headline invariant; NEW-2 is the pin `Inc-4b` will need,
since `Inc-4b` adds exactly the shape that already sits outside the protocol. NEW-3 is
three characters and removes a trap the next increment is positioned to fall into.

**Credit.** The round-2 work is materially stronger than round 1's suggestion would have
produced. Declining a reviewer's snippet because it reddens correct code, measuring that
rather than asserting it, and replacing it with a targeted structural pin is the right
engineering call — and the `_view_state` read census, the derived `n` oracle and the M2
self-guard are all above the bar. The two MEDIUMs above are the same class of gap one
level deeper, not a failure of the thinking.

## PASS
