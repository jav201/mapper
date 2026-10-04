# Code Review — Increment 4c (`LLR-N07.3.4`, `#D43`)

**Reviewer:** code-reviewer (independent) · **Date:** 2026-08-29
**Verdict: BLOCK** — two HIGH findings, both false-confidence test gaps on code this increment
introduced. Both have cheap fixes, one of them proven below. The shipped *behaviour* is correct and
the `esc` half of the increment is genuinely delivered and genuinely gated.

---

## Scope reviewed

- `mapper/app.py` — 1 source file, working tree vs `9ba2f26` (entry pin). +339/−136 lines.
- `tests/test_search.py` — 2 arms removed, 5 added (30 → 33 functions in the file; net +3, so
  847 → 850 is arithmetically consistent).
- `.dev-flow/…/01-requirements.md` — `LLR-N07.3.4` (new) and its gate amendment.
- `.dev-flow/…/03-increments/increment-004c.md` — read **after** forming my own view of the diff.

### Mirror fidelity and restore integrity

- `git clone --local --no-hardlinks` into scratch, working tree overlaid, `git add -N` on the mirror
  only. `git diff` for `mapper/app.py` and `tests/test_search.py` is **byte-identical** to the real
  repo's.
- Mirror reproduces the declared baseline exactly: **`850 passed, 17 deselected, 3 xfailed`**,
  confirmed by two independent full runs. Collection order is deterministic (`pytest-randomly` is not
  installed in this environment), so the baseline carries no ordering variable — see the closing note.
- Ruff over `mapper/ tests/`: **27 errors, set-identical to the entry pin** (compared as sorted
  `file + rule` sets with line/column stripped) — zero new, zero gone. Confirmed independently.
- Baseline sha256 `mapper/app.py` = `654dba5e…`, `tests/test_search.py` = `d161c3a7…`. **These match
  the two hashes the author declares in §4**, so the reported numbers come from the tree I reviewed —
  the evidence-integrity declaration about the two discarded contaminated runs is consistent with
  what I can verify.
- Every mutation below was applied to the mirror only and restored by sha256 to `654dba5e…` /
  `d161c3a7…`. **The real repo was never mutated.**

---

## What I independently reproduced from the author's battery

Six of the twelve declared arms, re-derived from the diff rather than from his table. All six
**KILLED**, matching his verdicts:

| My arm | Operation | Kills |
|---|---|---|
| MUT-A (`M-N07.3.4-a`) | shared predicate's return re-conjoined with the resolution test | `test_at_055_esc_means_one_thing_at_every_graph_size`, `test_the_hint_line_promises_esc_at_every_graph_size` |
| MUT-B (`A-tally-viewport`) | tally's hit set narrowed by the fold state | `test_the_count_and_the_paint_share_one_resolution` |
| MUT-D (`M-N07.3.4-b`) | notice interpolation deleted from the suspended line's tail | `…declares_the_search`, `…is_actually_in_the_frame` |
| MUT-F (`A-echo-unbounded`) | the 32-cell budget removed, coercion kept | `…is_actually_in_the_frame` |
| MUT-G (`S-second-owner`) | tally re-inlined as its own owner construction | `test_the_count_and_the_paint_share_one_resolution` |
| MUT-H (reverse of `S-unexplained-reader`) | a **stale** exemption re-added to the exempt set | `test_every_reader_of_the_resolution_is_inside_a_paint_pass` |

The battery is honest. Its gaps are between the arms it fired, which is what F1 and F2 below are.

---

## Findings

### F1 — Risk A-6 is **still open**: the viewport ban is hand-listed, and a new link in the count chain evades it and the entire suite  [Severity: HIGH]

- **What:** The A-6 ban is a hand-written tuple of six methods. It bans *those names* from reading
  viewport state — it does not ban the *count chain* from doing so. Any mutation that puts the
  narrowing behind a method not on the list is invisible to it.
- **Where:** `tests/test_search.py:619-628` (the `for method in (...)` tuple).
- **Evidence — this is not hypothetical.** I introduced one new private helper on `MapScreen` that
  computes the tally with the hit set narrowed by the fold state, and pointed the suspended region's
  tail at it instead of `_whole_graph_tally`:

  ```
  MUT-C  →  850 passed, 17 deselected, 3 xfailed
  ```

  **The full suite is green on a count region that paints a viewport-narrowed number above the
  bound.** That is risk A-6 itself, fourth instance, reached through a link the just-extended ban does
  not name.

  **And it is an operator-visible lie, not an AST smell.** Measured on the same 12002-node graph with
  1500 matching nodes folded:

  | | value |
  |---|---|
  | whole-graph truth | **6001** |
  | shipped tally | **6001** ✓ |
  | MUT-C tally | **4501** — 1500 matches under-reported, suite green |

  The region would paint `búsqueda: «zeta» · 4501 coincidencias en el mapa` over a graph holding
  6001. That is exactly the lying affordance `US-N07` and `#D43` exist to remove, on the very surface
  this increment added to remove it.

  Note also that MUT-B (the author's own A-6 arm) is killed *only* by the AST census —
  no behavioural arm sees it, because the fixture's fold set is empty. The hand-list is the only
  thing standing between this increment and a wrong count.
- **Why it matters:** The author's own docstring records this as the third manual extension of the
  same ban (`_search_hits` one increment ago, three more names today). `C-31` says a hand-listed set
  survives every code mutation, and this is the demonstration. The next increment that adds a link
  will re-open it again, silently.
- **Suggested fix — and the answer to "should the set be DERIVED?": yes, and it is cheap, because the
  closure algorithm is already written 530 lines further down this same file**
  (`tests/test_search.py:1157-1170`, the `_PASS_FREE_READERS` arm). Seed from `_count_line` and close
  transitively over the same `self.X` read map:

  ```python
  reaching = {"_count_line"}
  while True:
      grown = {n for n in reads if n not in reaching
               and any(n in reads[x] for x in reaching if x in reads)}
      if not grown:
          break
      reaching |= grown
  for name in sorted(reaching):
      leaked = [v for v in VIEWPORT if v in reads[name]]
      assert not leaked, f"{name} narrows the count by the viewport: {leaked}"
  ```

  **I ran exactly this.** On the shipped tree it reaches
  `_count_line, _query_echo, _search_index, _search_order, _seat_glyph, _seat_row,
  _suspended_count_line, _whole_graph_tally` and reports **zero leaks** — no false positive, and it
  covers three methods the hand-list misses. Against MUT-C it reports
  `{'_region_tally': ['folded']}` — **the mutant is caught.** `_search_hits` is not in the count
  chain and should stay pinned separately as it is today.

---

### F2 — The coercion sink on the new query echo is **ungated**  [Severity: HIGH]

- **What:** `_query_echo` routes operator text through `darkside.fit`, and its docstring makes the
  coercion claim load-bearing (`HLR-COERCE`; "a right-to-left override left alive reverses the
  sentence it sits in"). Nothing in the suite enforces it. Replacing `fit` with a raw slice of the
  same length keeps every declared arm green.
- **Where:** `mapper/app.py:1833`.
- **Evidence:**

  ```
  MUT-E (fit → equivalent-length raw slice)  →  850 passed, 17 deselected, 3 xfailed
  ```

  And the claim the docstring makes is **true**, so the gap is not moot. Measured on the shipped
  `darkside.fit` versus a slice, for five control classes:

  | code point | `fit` keeps it | slice keeps it |
  |---|---|---|
  | U+202E, U+202D, U+200B, U+2066, U+001B | **no** (all replaced) | **yes** (all preserved) |

- **Why it matters:** This increment *introduces* a new operator-text sink onto a painted region.
  The author's own `A-echo-unbounded` arm removes the **cap** while keeping `fit`; nothing tests the
  complement. A later reader who simplifies the echo to a slice ships a bidi-override sink and the
  suite congratulates them. This is the "tests verify intent, not behaviour" rule failing on the
  exact line whose docstring argues intent hardest.
- **Suggested fix:** one assertion in `test_above_the_bound_the_count_line_declares_the_search`, on a
  query built with `chr(0x202E)` (constructed, never spelled):

  ```python
  screen.query_text = "zeta" + chr(0x202E) + "abc"
  painted = _count_line_text(screen)
  assert chr(0x202E) not in painted, "a bidi control reached the region"
  ```

- **Handoff:** this is security-adjacent. Flagging to `security-reviewer` rather than ruling on the
  threat model myself.

---

### F3 — The gate amendment left the Statement contradicting its own predicate 3  [Severity: MEDIUM]

You asked me to check that your amendment did not "quietly weaken the requirement into describing
whatever was built." It did not weaken it. It **over-claims** in the other direction, and no
threshold gates the over-claim.

- **What:** The amended Statement requires the system to declare the query "on the count region —
  naming the query and the whole-graph match count — **at every graph size**", and "where the walk is
  live the declaration shall name the chord that traverses the matches."
  **Below** the bound the count region paints `f"{at}/{len(hits)} {SEARCH_COUNT_SUBJECT}  "` — it
  names **neither the query nor the chord**. Meanwhile predicate 3 requires precisely that those
  below-bound strings stay **unchanged**.
- **Where:** `01-requirements.md` `LLR-N07.3.4` Statement vs. its numeric threshold 3;
  `mapper/app.py:1936-1939`.
- **Why it matters:** The clause instructs a future implementer to do something its own pass
  threshold forbids. That is the shape that produces the next `#D43`. It is a requirements defect,
  not a code defect — the shipped code matches the thresholds exactly.
- **Suggested fix:** scope the two clauses to the regime they were written for — "at graph sizes at
  which the renderer declines to paint highlights, the region shall name the query, the whole-graph
  count and what is suspended; below that bound the shipped `n/N` and `0` forms stand and the walk
  chord is named by the hint line."

**On your ruling itself — I agree with it, on all three checks you asked for:**

- **(a) The shipped copy is honest at both regimes.** Above the bound `_search_order()` is `None`, so
  no highlight paints and `_walk_hits` returns early — both halves of "resaltado y recorrido
  suspendidos" are true. `esc limpiar` is true because `_search_is_live` now reads only the query.
  Below the bound no notice is painted. I found no false statement on either row.
- **(b) It is gated.** MUT-D (notice dropped from the region's tail) reddens two arms, one of them
  the composited-frame arm. The suspension wording cannot be dropped silently.
- **(c) The amendment did not weaken the requirement** — see the over-claim above, which is the
  opposite failure and is cheap to fix.

The implementer was right to refuse. Painting `n recorre` above the bound would have been a lying
affordance, and the refusal is correctly recorded rather than absorbed.

---

### F4 — Predicate 1 is never observable in the field, and the shipped-surface arms cannot see that  [Severity: MEDIUM]

Disclosed by the author as R2/F-2, and his diagnosis is confirmed. I am recording it separately
because I judge the disclosure understates the consequence for *this* increment's acceptance.

- **What:** Every above-the-bound arm reaches the branch by lowering `MAX_RENDER_NODES` onto a small
  graph. On a real graph above the shipped bound the count region is **not in the frame at all**.
  Independently measured on a genuine 12002-node graph:

  | | 118×34 | 80×24 |
  |---|---|---|
  | `#map-pagination` region | y=42, h=104 | y=998, h=155 |
  | `rows_in(...)` | **0 rows** | **0 rows** |
  | `#map-canvas` height | 1 | 1 |

- **Where:** `tests/test_search.py` — `test_the_suspended_declaration_is_actually_in_the_frame` and
  `test_at_055_esc_means_one_thing_at_every_graph_size`, both via
  `monkeypatch.setattr(app_module, "MAX_RENDER_NODES", len(graph.nodes) - 1)`.
- **On probe 3 (A-5, "driven through the shipped surface"):** partially satisfied, and the answer is
  split. `test_the_suspended_declaration_is_actually_in_the_frame` uses the real app, `run_test`,
  `refresh_canvas()` and `rows_in` on the real `#map-pagination` region across a 60→160 band — that
  is the shipped surface, and it is the right instrument. `AT-055` drives a real `pilot.press
  ("escape")`. But `test_above_the_bound_the_count_line_declares_the_search` builds a bare
  `MapScreen(...)` outside any app and calls `screen._count_line()` — **that one is a service call**,
  not the shipped surface. It is acceptable only because the frame arm exists beside it.
- **Why it matters:** `#D43` exists to replace hidden state with a painted declaration. The `esc`
  half of that is real, size-independent by construction, and delivered. The **paint** half is
  delivered into a `Text` that, in the only regime it exists for, no operator can read. The increment
  should not be closed with predicate 1 recorded as met in the field.
- **Judgement on the scope call: deferring to `Inc-STRIPS` is RIGHT.** The collapse is pre-existing,
  it spans three widgets across CSS this increment does not own, and half-fixing it from inside a
  one-file increment scoped to `esc` and a count line would be worse. Keep the deferral; change only
  the bookkeeping — record predicate 1 as **met under a moved bound, not met at the shipped bound**,
  and make `Inc-STRIPS` a blocker on closing `LLR-N07.3.4` rather than a follow-up.

---

### F5 — `_pagination_text`'s comment misattributes the collapse, and could cost the next reader the meter cap  [Severity: LOW]

- **What:** The comment says a meter cap "would not have helped" because `#map-minimap` is the real
  cause. A measured control — minimap hidden, meter left unbounded — shows the meter is an
  **independent** cause: at 80×24 the region is 155 rows and **all 21 visible rows are meter glyphs**,
  with the count text still off-screen. At 118×34 the same control yields 31 readable rows with the
  count line on the last one.
- **Where:** `mapper/app.py:1947-1958`.
- **Why it matters:** The remedy in §7 is already correct ("bound the minimap, the meter and the
  overflow declaration **together**"), but the comment argues the meter cap is worthless. A reader
  who trusts the comment over the plan will bound the minimap alone and the count will still be
  unreadable at 80×24.
- **Suggested fix:** change "bounding it would not have helped" to "bounding it is necessary but not
  sufficient — the minimap is a second, independent collapse", and note the 80×24 control.

---

## Also reviewed — clean

- **`_PASS_FREE_READERS` removals: correct.** `_search_is_live` now reads only `query_text`, so
  neither it nor its wrapper `action_back_or_home` reaches the resolution; leaving them would fail the
  `stale` assertion. Verified in both directions: MUT-H (stale entry re-added) reddens the arm, and
  MUT-A (predicate re-reading the resolution) reddens two behavioural arms.
- **The opener assertion is untouched.** `assert openers == {"refresh_canvas",
  "_declare_after_layout"}` at `tests/test_search.py:1155`; the diff does not contain the string
  `openers` at all.
- **One `SearchIndex` constructor: confirmed.** Exactly one call site, `mapper/app.py:1777`. MUT-G
  (re-inlining a second construction) reddens the census — so the author's report that the arm caught
  his second site during development, and that he **shared rather than exempted**, is consistent with
  the machinery. Sharing was the right call.
- **`esc` parity is ONE node across TWO regimes: confirmed.**
  `test_at_055_esc_means_one_thing_at_every_graph_size` is a single test function running one
  `esc_parity` closure against both regimes, so a `_search_is_live` that consults graph size cannot
  satisfy it twice. MUT-A reddens it. This is the correct shape and it answers `M-N07.3.4-a`.
- **Copy reconciliation: agree, keep the toast.** The old label asserted the search was not
  evaluated, which the region now contradicts in the same frame; the new label names what the
  keypress actually could not do. The author's argument for keeping rather than deleting the toast is
  right — the region declares a *state*, the toast answers a *keypress*, and deleting it makes `n` a
  silently swallowed press, which is the same defect class one surface over. Gated by
  `test_the_walk_above_the_render_bound_declares_neither_zero_nor_silence`.
- **F-3 (the stale cost argument): CONFIRMED, and the increment does rest on it.** Independently
  re-measured at 12002 nodes, 40 reps after warmup: `hits` median **0.0074 s**, `query` median
  **0.0123 s** — both match the author's figures almost exactly. `tree_order` measured **0.0038 s**,
  ~2.6× *faster* than his 0.0097 s, so his number is conservative rather than inflated. The
  load-bearing equality holds: `len(query(q)) == len(hits(q)) == 6001`. "Seconds each" is stale by
  two to three orders of magnitude, and taking the count from `hits` is what makes declaring above
  the bound affordable.
- **F-6 (the fixed 32-cell cap): adequate, not a repeat of the Inc-4b failure.** The two cases differ
  in what overflow costs, and the docstring says so correctly. MUT-F (cap removed) reddens the frame
  arm, and that arm asserts a **relative** bound (`long_height <= height + 1`) swept 60→160, which is
  the right instrument — a constant ceiling would pass on an implementation that always wrapped. The
  `self.size.width` / `NoActiveAppError` reason for rejecting the width-relative form is a real
  constraint on a helper three unit arms reach unmounted. One extra row at 60 columns is a fair price
  and it is stated rather than rounded off.

---

## Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **Block — must fix HIGH findings before advancing**

**BLOCK on F1 and F2.** Both are false-confidence gaps in the gating of code this increment
introduced, both are reproduced against the full 850-arm suite, and both have concrete fixes — F1's
is proven to be clean on the shipped tree and to catch the surviving mutant. Neither requires
changing shipped behaviour.

F3 is a one-paragraph requirements edit. F4 is a bookkeeping correction to an already-correct scope
call. F5 is a comment.

**Two items folded in at the gate, neither chargeable to this increment:** (1) the batch control in
the closing note — one writer per tree, suite runs are evidence only from trees no other process can
write to; (2) the census hardening (converse `seen <= on_disk` assertion at
`tests/test_a3_census.py:42-60`, same shape at `:453`, `tests/test_fold.py:111`,
`tests/test_inc3_census.py:36`) is routed to the increment that owns the census, not to Inc-4c's fix
list.

**What is genuinely good here:** the `esc` parity node is the right shape and kills its named mutant;
the single-constructor consolidation was the right response to a reddened census; the refusal to
paint `n recorre` was correct and correctly escalated; the cost re-measurement is accurate and
load-bearing; and the F-2 diagnosis is honest about making the increment's own headline unobservable
in the field, which most authors would have buried.

---

## Evidence checklist

- [x] **Diff read in full** — `mapper/app.py` +339/−136 and `tests/test_search.py` +382/−136 read as
  diff and as shipped source; `01-requirements.md` `LLR-N07.3.4` read before the increment document.
- [x] **Correctness pass (edge / None / error paths)** — `_search_order()` `None` branch traced
  through all four consumers (`_count_line`, `_search_hint`, `_walk_hits`, `refresh_canvas`); blank
  query, empty hits and above-bound regimes each checked against the shipped strings. No false
  statement found on either regime's row.
- [x] **Simplicity pass** — three new helpers, each single-purpose and each with a stated reason to
  exist; `_search_index` is a genuine consolidation, not speculative generality. No over-engineering
  found. `_QUERY_ECHO_CELLS` is measured, not guessed.
- [x] **Reuse / duplication checked** — one `SearchIndex` construction site verified at
  `mapper/app.py:1777`; chord glyph read from the seat; `SEARCH_COUNT_SUBJECT` and
  `SEARCH_SUSPENDED_NOTICE` each spelled once and read by both surfaces.
- [x] **Tests reviewed for intent** — 6 of 12 declared arms independently reproduced (all KILLED);
  **2 new mutants written and both SURVIVED the full suite** (F1 MUT-C, F2 MUT-E).
- [x] **Verdict explicit** — BLOCK.

### What I could not verify

1. **The two discarded contaminated background runs.** I can confirm the declared sha256 pair matches
   the tree I reviewed and that the tree reproduces `850/17/3`. I cannot verify from outside that the
   two abandoned runs were the ones discarded — that rests on the author's declaration, which is
   consistent with everything I can measure.
2. **The 6 remaining battery arms** (`A-tally-zero`, `A-notice-leaks-below`, `A-toast-unreconciled`,
   `A-esc-never-pops`, `A-hint-silent-above`, `S-label-dropped`) I did not re-fire; I spot-checked the
   six I judged weakest plus two of my own.
3. **Spanish copy** has not been reviewed by a native-speaking operator — same standing as prior
   increments, correctly carried as R5.
4. **A transient 5-arm census failure on my first mirror run** — chased to ground and attributed to
   my own concurrent tooling, not to this increment. See the note below; my initial
   "order-dependent" reading of it was wrong and is corrected there.

### Note — a transient 5-arm failure I hit, chased, and attribute to my own tooling (not to Inc-4c)

Reported in full because I initially drew the wrong conclusion from it and want the record straight.

My **first** full mirror run produced `5 failed, 845 passed`, all five in `tests/test_a3_census.py`,
each a `FileNotFoundError` raised inside `pathlib`. I first hypothesised an order-dependent flake.
**That hypothesis was wrong, and so was my instrument:** `pytest-randomly` is **not installed** in
this environment (`pytest-asyncio`, `pytest-cov`, `pytest-textual-snapshot`, `pytest-timeout` only),
so `-p no:randomly` is a **silent no-op** and collection order is already deterministic. There is no
seed and no ordering variable. Any claim in this batch's history that `-p no:randomly` pins ordering
is folklore.

What it actually is: `tests/test_a3_census.py:37-39` derives its file set from `git ls-files` — **the
index** — and reads each path at `:63-64` **from disk**. Arm 1 (`:42-60`) asserts only
`on_disk <= seen` and never the converse, so a path that is in the index but absent from disk is
unguarded and crashes five arms later instead of failing by name. The five failures are exactly the
filesystem-touching arms from arm 8 onward in file order — a transient tree state, not a test
interaction.

**Attribution: my own concurrency, not the increment — and the colliding file is named.** I ran two
verification lanes in parallel, and my measurement lane created and deleted a scratch file
(`tests/test_zz_probe.py`) in the head-mirror tree while my diagnostic lane had a suite run in
flight there; the diagnostic lane caught that file appearing and vanishing **during** its run. That
is my orchestration error, and it is the same collision class the author declares for his own two
discarded contaminated runs — this batch has now hit it repeatedly. The exact five-arm FAILED
signature was also reproduced deliberately in a throwaway copy by simulating a mid-run tree mutation
(hidden files plus a staged-then-deleted ghost), so the mechanism is closed, not conjectured.

Corroborating evidence that it is not a code defect: the census file is **byte-identical** between
the entry pin and the increment tree; all 45 pairwise `<file> + test_a3_census.py` combinations are
green; the census file alone is green 25×; and two independent full runs of the increment tree give
`850 passed, 17 deselected, 3 xfailed`. **The declared baseline is sound and is not
order-dependent.** All mutation results above ran in a tree with a single writer and are unaffected.

**Batch control, adopted at this gate (binding going forward):** **a suite run is evidence only when
taken from a tree no other process can write to.** One writer per tree; every concurrent lane gets
its own disposable clone; a run that shared a tree with any other writer is discarded and re-run, not
explained. The author's discarded-runs declaration in §4 of the increment document already practised
this; it is now a control, not a courtesy.

**One genuine pre-existing weakness surfaced along the way — routed to the increment that owns the
census, NOT chargeable to Inc-4c:** the guard at `tests/test_a3_census.py:42-60` derives its file set
from the git **index** (`tracked()`, `:37-39`) but reads each path from **disk** with no existence
guard (`:63-64`; the same fault at `:453` for `docs/ARCHITECTURE.md`), and asserts only
`on_disk <= seen`, never the converse — so a tracked-but-absent path crashes five arms later as an
opaque `FileNotFoundError` instead of reddening one named arm. Adding the converse assertion
(`seen <= on_disk`) fixes it. The same one-directional shape exists at `tests/test_fold.py:111` and
`tests/test_inc3_census.py:36`. Minor, same owner: `tracked()` splits `git ls-files` output on
whitespace, so a tracked filename containing a space would yield phantom entries and the same crash —
currently harmless, as no tracked path has one.
