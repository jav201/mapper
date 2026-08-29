# Code Review — Increment 4b (`#D5b` seat + walk, `LLR-N06.2.4`, `E1b`/`E1c`, `#D38`)

**Verdict: BLOCK.** Two HIGH findings, both false-confidence tests on the increment's
headline behaviour. The shipped code is correct in both cases — neither finding is a
live defect — but the arms that are presented as covering them cannot fail on the
defect they name, and I demonstrated that with mutations that survive the full suite.
The fixes are small and one of them I validated end-to-end.

Everything else in this increment held up under adversarial probing, including four of
the five declared spec corrections. Detail below, including what I could not verify.

---

## Scope reviewed

Working tree of `C:/Users/jjgh8/Github/mapper` at branch `feat/ui-next-batch-02`,
entry commit `a971432`, nothing committed.

| File | Δ | Read |
|---|---|---|
| `mapper/app.py` | +262/−~24 | full diff |
| `mapper/keymap.py` | +15/−1 | full diff |
| `tests/test_search.py` | +551 | full diff |
| `tests/test_fold.py` | +193 | full diff |
| `tests/test_inc4_census.py` | +119 (staged) | full file |
| `tests/test_inc3_census.py` | +57/−~6 | full diff |
| `tests/test_a3_census.py` | +16/−4 | full diff |
| `tests/test_key_dispatch.py`, `tests/test_keymap.py` | +17 | full diff |

### Mutation environment

`git clone --local --no-hardlinks` to scratch, working-tree state of `mapper/`,
`tests/` and `.dev-flow/` overlaid, index reconciled with `git add -N` (mirror only).

**Fidelity established BEFORE any mutation:** `843 passed, 17 deselected, 3 xfailed`,
exit 0, zero FAILED — identical to the declared baseline. Ruff over `mapper/ tests/`
reports 27, matching the entry pin.

**The real repository was never mutated.** `git status --porcelain` at end of review is
byte-for-byte what it was at session start, and `mapper/app.py` hashes
`5dce66dc21bd1f70466a679b4f44d481c6af0e3848f5e1f92498375656a7a12b` — the same digest
the mirror baseline carries. Every mirror mutation was restored and verified by sha256
before the next was applied.

---

## Findings

### F1 — The walk's "cursor is not in the hit set" branch is dead to the entire suite [Severity: HIGH]

- **What:** `_walk_hits` has two ways to choose the first target. The `in hits` path is
  pinned thoroughly by `AT-022`. The `else` path — the one that runs whenever the
  cursor is not itself a match — is **never executed by any test in the suite**, and no
  arm constrains it.

- **Where:** `mapper/app.py:2444-2445`

- **Evidence (two independent mutations, both survive the full lane):**

  | Mutation | Result |
  |---|---|
  | else-branch endpoints swapped (forward walk lands on the last hit, backward on the first) | `843 passed, 17 deselected, 3 xfailed` |
  | else-branch body replaced by `raise AssertionError` | `843 passed, 17 deselected, 3 xfailed` |

  The second is decisive: the branch is not merely under-asserted, it is **never
  reached**. Making it raise changes nothing.

- **Why it matters:** This is the *primary* entry into the feature, not a corner. Nothing
  in `on_input_submitted` moves the cursor onto a hit, so an operator who searches for
  something away from where they are standing takes the `else` branch on their very
  first `n`. `AT-022` does not exercise it because on the `adjuntos` fixture the resting
  cursor happens to be a match (`riesgo-root` is in the hit set), so `tree_ordered.index(start)`
  resolves and the walk enters through the `in hits` path every time. The increment's
  §4.8 ledger claims "16 mutations, 16 RED"; that claim does not extend here, and the
  ledger is load-bearing gate evidence. `AT-022` presents itself as the walk's acceptance,
  so a reader reasonably concludes the walk is pinned. It is pinned on one of its two
  entry paths.

  The shipped semantics are correct — forward-from-outside should land on the first hit,
  backward-from-outside on the last — so this blocks on missing coverage, not on a defect.

- **Suggested fix:** one arm, using the fixture that already exists. Place the cursor on
  a node that is *asserted* not to be in the hit set, then check both directions:

  ```python
  async def test_at_022b_the_walk_enters_from_outside_the_hit_set(tmp_path):
      """The FIRST press when the cursor is not itself a match — the common entry.

      `n` must land on the first hit in tree order and `N` on the last; the
      `in hits` arm of AT-022 cannot reach this branch, because the resting
      cursor on this fixture is itself a hit.
      """
      ...
      order = [nid for nid in expected_tree_order(screen.graph) if nid in found]
      outsider = next(n for n in screen.graph.nodes if n not in found)
      assert outsider not in order, "SELF-GUARD: the cursor must start outside"

      await submit(pilot, QUERY)
      screen.nav.cursor = outsider
      screen.refresh_canvas()
      await pilot.press("n"); await pilot.pause()
      assert screen.nav.cursor == order[0]

      screen.nav.cursor = outsider          # re-enter from outside
      screen.refresh_canvas()
      await pilot.press("N"); await pilot.pause()
      assert screen.nav.cursor == order[-1]
  ```

  Both mutations above go RED against this. Note the second half is the half that
  matters: swapping the two endpoints is the natural typo, and only the `N` limb sees it.

---

### F2 — `AT-047` cannot fail on the re-close defect it exists to catch [Severity: HIGH]

- **What:** `_unfold_onto`'s docstring makes an explicit behavioural promise — *"The
  branch is NOT re-closed when the walk moves past it."* `AT-047` is nominally that
  promise's arm. It does **one** further press, and on this fixture that press does not
  move past the branch — it moves to the next hit *inside* the same branch. An
  implementation that re-closes an opened branch whenever the walk advances therefore
  passes `AT-047` unchanged, because it re-opens the branch on the same press.

- **Where:** `tests/test_fold.py:1083-1095` (the further press and the pill assertions)

- **Evidence:**

  Measured on the shipped tree — the walk lands on `d`, `AT-047`'s further press goes to
  `e`, and `e` is still hidden under the opened branch `b`:

  ```
  landed on d, opened ['b']
  AT-047's one further press lands on: e | still inside the opened branch? True
  walked out to: c | outside: True
  ```

  Mutation: re-add the previously-opened set to `folded` at the start of the next
  `_unfold_onto` call — i.e. re-close on advance, the exact behaviour the docstring
  disclaims. Result on `AT-046`/`AT-047` at both declared sizes: **4 passed**. The
  mutant is not killed.

  With the predicate strengthened to walk *out* of the branch before reading the frame,
  the same mutant repaints the pill and is caught:

  ```
  walked out to: c | outside: True
  PILLS: ['Contratos en …', 'Auditoria']
    pill repainted for b -> True     # RED under the mutant
  ```

  and on the shipped tree the same strengthened predicate reads `pill repainted for b ->
  False`, i.e. it passes for the right reason.

- **Why it matters:** §4.8's `M4` ("the opened set re-added to `folded` after the
  repaint", 2 failed) is a genuine mutant but a degenerate one — it corrupts the very
  frame it just painted, which *any* frame-reading assertion catches. It does not
  demonstrate what `P-047.1` claims to demonstrate. The realistic defect — re-close when
  the walk advances — is the one the docstring rules out in prose and the one nothing can
  see. This is the "green before any code was written" hazard the batch exists to stop,
  landing on the predicate written to close it.

- **Suggested fix:** replace the single press with a walk that is *asserted* to leave the
  branch, then read the frame:

  ```python
  # ONE FURTHER PRESS is not enough: the next hit can be inside the SAME
  # branch, so the fold is re-opened and a re-closing implementation is
  # indistinguishable.  Walk until the cursor is OUTSIDE, asserted reached.
  for _ in range(len(SearchIndex(screen.graph).query(screen.query_text)) + 2):
      if screen.nav.cursor not in hidden:
          break
      await pilot.press("n")
      await pilot.pause()
  assert screen.nav.cursor not in hidden, "never walked out of the opened branch"
  ```

  then the existing `_pill_titles` assertions unchanged. I ran this; it is RED under the
  mutant and green on the shipped tree.

---

### F3 — `esc` and the hint line disagree about what "a live search" is, above the render bound [Severity: MEDIUM]

- **What:** Two guards describe the same state and are written differently.
  `on_input_submitted` decides whether to promise `esc limpiar` with
  `self.query_text.strip() and order is not None`; `action_back_or_home` decides whether
  to clear with `self.query_text.strip()` alone. Above `MAX_RENDER_NODES` the two
  disagree.

- **Where:** `mapper/app.py:2770` (the clear guard) against `mapper/app.py:2254` (the
  hint guard)

- **Evidence** (measured, bound moved via monkeypatch as `§1.6 C`'s own arm does):

  ```
  ABOVE BOUND, search submitted
    hint      : 'navega con j/k/h/l · ↵ ficha · / buscar'
    count line: ' ▰▱▱▱▱▱   1/6 ...'        (no `coincidencias` subject)
    query_text: 'riesgo'
  after 1st escape:
    still on map? True
    query_text  : ''
    hint        : 'navega con j/k/h/l · ↵ ficha · / buscar'   (unchanged)
  after 2nd escape: still on map? False
  ```

  Nothing is painted above the bound, so the first `escape` clears a query that was
  never visible, changes no pixel, and does not leave the map. The operator's keypress
  is silently swallowed and they must press `escape` twice.

- **Why it matters:** This is the inverse of the defect `#D38` was written to fix. `#D38`'s
  own rationale, quoted in the handler's docstring, is that the hint promises
  `esc limpiar` and the handler must keep the promise. Above the bound the hint promises
  nothing, and the handler acts anyway — an affordance firing where none was advertised,
  with no painted feedback. The new third state (§1.6 C) was added precisely so the
  unanswered-question case would stop being conflated with the empty case; this is the
  one surface where that separation was not carried through.

- **Suggested fix:** give the two sites one predicate, matching the increment's own
  one-owner discipline:

  ```python
  def _search_is_live(self) -> bool:
      """What both `esc` and the hint line mean by "a search is live".

      Above the renderer's bound the question was never answered, so there is
      nothing painted to clear and nothing to promise: the two surfaces must
      agree, or `esc` acts where no affordance was advertised.
      """
      return bool(self.query_text.strip()) and self._search_order() is not None
  ```

  then `if self._search_is_live():` in `action_back_or_home`, and the same call in
  `on_input_submitted`. Note this adds `action_back_or_home` and `_search_is_live` to the
  derived `reaching` set, so both need `_PASS_FREE_READERS` entries — which is the arm
  working as designed. If instead the intent is that a query above the bound *is* live,
  the hint must say so and the third state needs a hint variant; either resolution is
  fine, but the two guards must not stay independent.

---

### F4 — `C-D6a`'s "no boolean expression" rule is escapable without a `BoolOp` [Severity: LOW]

- **What:** The arm is presented as making `M-N07.3-a` *unwritable*. The teeth are
  actually `used == {"_search_order"}`; the `BoolOp` check is a coarse second belt. A
  second result set whose name misses the regex `hits|matches|search_order|search_memo|lens`
  and which is combined without `and`/`or` — tuple concatenation, `dict.fromkeys`,
  `itertools.chain` — satisfies both assertions.

- **Where:** `tests/test_search.py:1682-1692`

- **Why it matters:** Only the strength of the claim, not the code. "Unwritable" is
  stronger than what is enforced; "the two named shapes are unwritable" is accurate. The
  rule is genuinely load-bearing in the other direction — it already caught a real
  `title or nid` fallback on its first run, and the author lifted it into `_branch_name`
  rather than weakening the rule, which is the right call.

- **Suggested fix:** documentation only. Soften the docstring's "cannot be expressed in
  the handler at all" to name what is actually forbidden, or widen the vocabulary regex
  to include a generic result-set suffix (`_set$|_ids$`). No code change.

---

## The five declared spec corrections, judged

**(1) The exemption table — real, not a widening to dodge the obligation. Accepted.**

I removed the `_walk_hits` entry from `_PASS_FREE_READERS`: the arm goes RED at the
`unexplained` assertion. The exemption is load-bearing, not decorative.

On the reasons themselves:
- `_walk_hits` — **the claim survives scrutiny.** I tried to construct a stale read and
  could not. The memo is keyed on graph identity and query text; `_open_paint_pass` runs
  at the top of every `refresh_canvas`, so any repaint drops it. That closes the loop: to
  change the resolution's inputs you must either change the query text or the graph
  object (both break the key, forcing a fresh resolve), or mutate the graph in place —
  and if a repaint followed that mutation the memo is already gone, while if no repaint
  followed, the frame on screen is equally stale and the walk still agrees with what the
  operator is looking at. Fold is explicitly not an input to `_search_order`, so the
  auto-open cannot desynchronise it either. **No path exists where the walk's resolution
  and the painted frame disagree.**
- `on_input_submitted` — verifiably true: `refresh_canvas()` is called on the line above,
  so the read hits that pass's own memo.
- `action_next_hit` / `action_prev_hit` — pure bookkeeping, forced by the transitive
  closure, and identical in kind to the four pre-existing `action_pan_*` entries. Honest
  rather than padding.

Four rows is what the derivation demands once one keypress-bound consumer declines to
open a pass. The obligation was discharged, not evaded.

**(2) The third state — a necessary consequence of Inc-4a's `None`, not scope creep.
Accepted, with the caveat in F3.** Inc-4a chose `None` over an empty order specifically so
that "unanswered" and "answered zero" could not be confused; a walk that grew an
empty-result toast inherits that distinction whether or not the sealed text names it, and
`E1c`'s body («q» no aparece en este mapa) is a false claim above the bound. The guard is
correctly placed on the toast and on the hint line — `test_the_walk_above_the_render_bound_declares_neither_zero_nor_silence`
pins both, including the negative that the hint must not read `sin coincidencias`. The
copy is new and no `shall` clause owns it; the author flagged it for the gate rather than
absorbing it, which is the correct handling. **The one place the guard was not carried
through is `esc` — that is F3.**

**(3) The toast collision — genuinely pinned, not asserted in prose. Accepted.**

Mutation: `declaring = not self._rebind_declared` → `declaring = True` (declare on every
press). Three arms go RED **at three different assertions**:

```
test_at_023_e1b_and_e1c_are_painted_differently        -> assert e1b != declaration
test_at_023_e1c_routes_the_operators_query_through_plain -> assert "0 coincidencias" in painted
test_at_051b_the_rebind_is_declared_exactly_once       -> assert <label> not in second
```

Both predicates hold as written, and the interaction is load-bearing in both directions:
`AT-051b`'s "second toast" *is* `E1b`, and `AT-023` consumes press one deliberately and
says so. This is the paired-arms-fail-at-different-assertions discipline actually working.

**(4) `C-D6a` closed structurally — the right call. Accepted, see F4.** Declining `02l`
§8.3(a)'s `active_hits` attribute is well-argued: adding it would create a second owner of
"what matches" on the screen Inc-4a spent an increment giving one owner, which is the
defect `US-N07` exists to close. The AST rule is not too strong in any way that matters —
it will fire on innocent future edits, but the documented escape (lift into a helper) is
proven to work, and the `title or nid` catch is evidence the rule bites rather than
decorates. It is mildly too weak, which is F4, and that is a wording fix.

**(5) `AT-047`'s pill oracle — the stem deviation is sound; the *press count* is not.**

The deviation from `02l` §7.9 is **not** weaker in the direction that matters, and I
verified this rather than reasoning about it. The oracle reads `_PILL` matches out of the
painted canvas rows, so it is a frame read, not a model read. Its failure mode under
clipping is a false *green* on `P-047.1` — but that same condition is a false *red* on
`P-047.2`, the positive control, which runs on the same frame at the same width. The
vacuity mode is covered by the control. Measured: stems are `Contra` / `Audito`, mutually
distinguishing, and the clipped pill reads `'Contratos en …'`, so six characters survive
at both widths. Forcing an opened branch closed and repainting is detected (`detect b
Contra -> True`), so `P-047.1` is not vacuous.

The positive control is real, exactly as `LLR-N06.2.4` PRED-C requires: branch `c` is
folded, never walked into, and its pill is asserted still painted from the frame.

**What is wrong is not the oracle but what it is pointed at** — one press does not leave
the branch. That is F2.

---

## Also reviewed

- **Walk correctness.** Wrap in both directions is right and `AT-022` pins it derivedly
  (`len(hits) + 1` presses, never a literal, with a self-guard that `tree_order !=
  dict_order` on the live fixture). The `_search_order` tuple is never mutated — the walk
  only calls `.index()`, `len()` and subscripts, and
  `test_the_resolution_cannot_be_corrupted_by_the_caller` covers the handout. The
  not-in-hit-set entry is F1.

- **`LLR-N06.2.4` predicate shapes.** PRED-A reads `painted_ids` from the renderer's
  returned set; PRED-B uses `oracle_traced` (clipped-and-visible title trace) at both
  declared sizes, and `AT-022` re-asserts both on *every* step, not just the last. PRED-C
  reads the frame and never `MapScreen.folded`. All three are the settled shapes.

- **`_unfold_onto` building a child index per call — justified, leave it.** It is guarded
  by `if not self.folded`, runs once per keypress, and is strictly cheaper than repeated
  `Graph.children_of` scans. Memoising it would be speculative optimisation on a
  keypress-frequency path. Nested folds are handled correctly: every folded start is
  tested independently, so a fold inside a fold opens both. `self.folded` is rebound, not
  mutated in place.

- **The six new helpers — each earns its place.** `_walk_toast` is where the declaration-
  precedence rule lives, and MUT-4 proves it is pinned; `_search_hint` takes the resolved
  order as an argument so it cannot describe a different answer from its caller's;
  `_branch_name` exists for a stated structural reason; `_seat_glyph`/`_seat_label` are
  thin but avoid repeating the `None` guard at seven call sites, and `P-052.2` limb (b)
  actually tests that the read is at call time. This is not abstraction the LLRs did not
  ask for.

- **`esc` (`#D38`) — the two arms fail independently. Confirmed.** `AT-053` ARM 1 asserts
  `app.screen is screen` plus the hit style gone from the rendered spans; ARM 2 asserts
  `app.screen is not screen`. An implementation that never pops fails ARM 2; one that
  always pops fails ARM 1. Neither can hide behind the other. The `hit_image` span
  oracle is the right instrument — a substring probe genuinely cannot tell "this node is
  a hit" from "some title contains those letters" — and it is correctly itemised as the
  57→58 argful bump in `test_a3_census`.

  **The removed branch was genuinely dead.** `if self.source_crumb: pop else: pop` has
  identical statements on both sides; deleting it is provably behaviour-preserving. Not a
  behaviour change.

- **Census work.** `test_inc4_census.py` pins declared-equals-measured in both directions
  and asserts the rebind as an identity on the key, so a drop-and-replace could not
  satisfy it. The `test_inc3_census.py` repair — freezing Inc-3's exit as a literal rather
  than reading the live seat — is the correct fix and is spelled as a literal rather than
  derived as `ENTRY | DECLARED_DIFF`, which would have made the assertion a tautology. The
  retained live-collision arm carries an honest note about what it now actually checks.
  The `test_a3_census` 57→58 bump is itemised with its reason. This is all sound.

- **Declared risks, judged.** Risk 1 (per-instance declaration) — correct trade; process-wide
  class state shared across tests is worse. Risk 2 (declaration lingers on the search-live
  path) — real, matches every other toast in the product, acceptable as declared. Risks 4
  and 5 (whitespace-only query treated as never-searched for `E1b` and `esc`) — I measured
  this: `query_text` stays `'   '`, the hint promises nothing, and `esc` pops. Coherent
  with `LLR-N07.3.3`, where the count line already paints blank and never-searched
  identically. **No finding.** Risk 6 (stem oracle) — the clipping concern is correctly
  identified and correctly guarded; the concern the risk does *not* raise is F2.

---

## What I could not verify

- **The slow lane (17 passed).** Not run — three minutes per fast-lane pass already, and
  nothing in this diff touches the depth-5000 acceptance path. Taken from the brief.
- **Ruff NEW/GONE set identity.** I confirmed the mirror reports **27** errors over
  `mapper/ tests/`, matching the entry pin, but did not diff the finding sets code-by-code
  against `a971432`. The count agreeing is consistent with the declared zero-NEW/zero-GONE
  but is not the same claim.
- **The other 12 rows of §4.8's mutation table.** I re-ran four by choosing my own
  mutants rather than replaying the author's; two of my four survived (F1, F2). I did not
  attempt to reproduce M1, M3, M5–M8, M11–M13, M15, M16. Given that two self-chosen
  mutations survived, **the "16 mutations, 16 RED" line should be read as evidence about
  the sixteen mutants chosen, not as a mutation-adequacy claim about the increment.**
- **Coercion / security surface.** Out of my lane. `E1c` and `_branch_name` route
  file-derived and operator-derived text through `darkside.plain()`, and `M7` targets
  exactly that, which looks right to me — but `security-reviewer` owns the judgement, and
  the `.dev-flow/**` census reach noted in the brief is theirs to re-run.

---

## Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **Block — must fix HIGH findings before advancing**

**F1 and F2 must land before this increment advances.** Both are test-only changes; no
production code needs to move for either. F3 is a MEDIUM I would want fixed in the same
pass, because it is a two-line consolidation and it is the last surface where the new
third state was not carried through. F4 is a docstring correction.

To be explicit about proportion: this is a rigorous increment and most of what it claims,
it earns. The `_PASS_FREE_READERS` derivation, the toast-collision pinning, the census
repair and the `esc` arm independence all held up against deliberate attack. The block is
narrow — the two arms guarding the walk's most common entry path and the fold's stated
no-re-close promise cannot fail on the defects they name, and the increment's own
mutation ledger reads as though they can.

---

## Evidence checklist

- [✓] **Diff read in full** — `mapper/app.py` (+262), `mapper/keymap.py` (+15/−1),
      `tests/test_search.py` (+551), `tests/test_fold.py` (+193),
      `tests/test_inc4_census.py` (+119), plus the three census/dispatch files.
- [✓] **Correctness pass (edge / None / error paths)** — wrap both directions verified;
      `None`-above-bound path measured; whitespace-query path measured; not-in-hit-set
      path found dead (F1); nested folds traced through `_unfold_onto`.
- [✓] **Simplicity pass** — six new helpers each justified; `_unfold_onto`'s per-call
      child index justified; no premature abstraction found.
- [✓] **Reuse / duplication checked** — `DEFAULT_MAP_HINT` correctly de-duplicates three
      copies; `_seat_*` reads the shipped seat rather than a second copy; the removed
      `if source_crumb: pop else: pop` confirmed genuinely dead.
- [✓] **Tests reviewed for intent** — four self-chosen mutations run: 2 RED
      (exemption removal, always-declare), 2 SURVIVED (F1, F2). Plus one reachability
      probe (F1) and two behavioural probes (F3, pill-oracle validation).
- [✓] **Mirror fidelity established before mutating** — `843 passed, 17 deselected,
      3 xfailed`, matching the declared baseline.
- [✓] **Real repository unmutated** — `git status --porcelain` identical to session
      start; `mapper/app.py` sha256 `5dce66dc…a12b` unchanged; every mirror mutation
      restored and sha256-verified before the next.
- [✓] **Verdict explicit** — BLOCK on F1 and F2.
