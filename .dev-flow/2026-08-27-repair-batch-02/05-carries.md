# Carries out of `2026-08-27-repair-batch-02`

Two records the next session must inherit rather than rediscover, plus the standing
riders. **Recorded because an unlanded fact is indistinguishable from one nobody found** (C-44).

---

## P-CARRY-1 — commit `8675151` puts the FEATURE batch's artifacts on this branch

**Measured, not argued:**

```
$ git show --stat 8675151 | tail -3
 .../2026-08-26-ui-next-batch-02/state-parked.json  |   81 +
 .dev-flow/state.json                               |  183 +-
 15 files changed, 13526 insertions(+), 112 deletions(-)

$ grep -c "2026-08-27-repair-batch-02" .dev-flow/state.json
0
```

**What it is.** `8675151` ("docs: land the ui-next-batch-02 PDR artifacts (C-44 discharge)") was
already on `fix/repair-batch-02` when this batch resumed — it is **not** this batch's work. It
carries ~13.5k lines of the *feature* batch's PDR artifacts and rewrites `.dev-flow/state.json`.

**Why it matters on merge.** `state.json` never mentions this batch. Its `batch_id` is
`2026-08-26-ui-next-batch-02`, `current_station` is `PDR`, `phase_status` is `awaiting-gate`, and
`baseline.tests_collected` is `429`. So after this PR merges, **`master`'s canonical state file
asserts that the current batch is a REJECTED, PARKED one, at a gate it did not pass, against a test
baseline that is three increments stale.** That is precisely the C-44 failure mode the flow
documents: the next session reads that file to orient itself and inherits a false premise (C-43).

**Deliberately NOT untangled here.** Rewriting or splitting `8675151` is history surgery on a shared
branch, and rebasing it out would discard a legitimate C-44 discharge that the feature batch needs.
The correct owner is the **batch close**, which is where `state.json` is rewritten anyway.

**What the next session must do**, in order:
1. Rewrite `.dev-flow/state.json` to describe the batch actually in flight — do not append to the
   parked record, replace it, and keep `previous_batch` pointing at this one with its merge SHA.
2. Re-measure `baseline.tests_collected` rather than carrying `429`. **Re-measure it — do not copy
   this line either.** It first read `548`, the count at `01d7578`, and was already stale when
   written: the very commit that authored it took the count to **643**. A carry whose whole purpose
   is to stop a stale number propagating shipped a stale number (re-confirmation review, MEDIUM-2).
   It is **643** at `d75f0fd`; at any later tip, measure it rather than trusting this sentence.
3. Record `8675151`'s provenance in the feature batch's own PLAN, so its artifacts are not
   re-derived on the assumption they never landed.

---

## P-CARRY-2 — the false-record defect, and the check that catches part of it

**This batch produced the same defect three times**, each caught by a human reader at review cost:

| # | The claim | Reality |
|---|---|---|
| 1 | a comment: *"every caller in the product catches `MapStoreError`"* | `grep -rn "except MapStoreError" mapper/` outside `store.py` returns **nothing**; both real callers catch bare `Exception` |
| 2 | a comment: coercing the node id removes the phantom duplicate node | it normalises the key TYPE only; the phantom still moves `coverage()`'s denominator |
| 3 | a map correction note **quoting verbatim** the falsehood it replaced | the regression pin cannot tell a value reported from one declared, and reddened on its own note (C-56) |

An independent QA pass then found a fourth shape: **three node citations naming tests that do not
exist**, one of them inside the disposition row of the finding about false records.

**A FIFTH shape arrived at close-out, and it is the one that matters most.** The independent
confirmation review found `04-gate-findings-disposition.md` recording the `dict[str, str]` refusal
sink and collision record as *"gated by `Q-high1`: 8 arms"*. **Reproduced in this session before
being fixed:** four mutants that break those two limbs left **all 548 arms green**, and `Q-high1`'s
8 arms are every one a *scalar-ladder* arm. The row described the code and was read as describing
the coverage — the batch's own HIGH-1 defect class one level down: a new family given its covered
sibling's implementation but not its sibling's gate.

**The enumeration, not a total** — three registers in this batch count this class differently and a
single number would be wrong the moment the corpus grows.

**Read rows 7 through 13 before drawing the lesson.** Four consecutive review rounds each found *a
false figure inside the correction of a false figure* — rows 7, 10 and 11 sit literally inside the
text that fixed the row above them, and row 10 is in a paragraph headed *HONEST SCOPE*. Rows 12 and
13 were found by **neither a human nor a reviewer**: they came from a mechanical sweep of every live
number across these artifacts, run because vigilance had demonstrably failed to converge four times
running. Row 13 is this table's own citation, stale because the docstring it points at grew.

**The honest conclusion is not "be more careful."** It is that prose counts about a moving tree decay
on every commit, and the only instrument that caught them at the tail was one that **re-derives**
rather than re-reads. The sweep is cheap and repeatable, and the next session should run it before
trusting any figure below:

```
# every live figure, every authored artifact, printed with its line, judged one by one
LIVE = {647, 630, 643, 626, 548, 531, 429, 100, 96, 83, 41, 40, 16, 12}
```

| # | Shape | Where | Found by |
|---|---|---|---|
| 1 | *"every caller catches `MapStoreError`"* | `mapper/store.py` comment | security gate (F2) |
| 2 | the node-id coercion removes the phantom node | `mapper/store.py` comment | Inc-1 review (F4) |
| 3 | a map correction note quoting its own falsehood verbatim | artifact | C-56 pin |
| 4 | three node citations naming tests that do not exist | artifacts | whole-branch QA |
| 5 | *"adding a `dict[str, str]` to ANY round-tripped dataclass extends the coercion"* | `mapper/store.py:98-130` docstring | confirmation review (MEDIUM-B) |
| 6 | *"same sink and same collision handling … gated by `Q-high1`"* | disposition row | confirmation review (HIGH-A) |
| 7 | *"`test_at_p02i` fails loudly if one appears"* — **inside the rewrite that fixed #5** | `mapper/store.py` docstring | re-confirmation review (MEDIUM-1) |
| 8 | the guard's own CLASS set: 4 classes named, 7 defined | `tests/test_repair_store_boundary.py` | re-confirmation review (MEDIUM-1b) |
| 9 | a carry stating a count stale at the tip it names | `05-carries.md` | re-confirmation review (MEDIUM-2) |
| 10 | *"3 checkable citations"* where disk says 4 — **inside the paragraph headed HONEST SCOPE** | `tests/test_repair_artifact_claims.py` | condition-discharge review (NEW-1) |
| 11 | two restatements of a superseded count left behind by the correction of that count | `increment-004.md` | condition-discharge review (NEW-2) |
| 12 | this table's own post-fix figures, stale one commit after being written | `04-gate-findings-disposition.md` | **the numeric sweep** (no reviewer flagged it) |
| 13 | this very row's line citation, stale after the docstring it points at grew | `05-carries.md` | **the numeric sweep** |

**Note where they live: 3 of the 6 are COMMENTS in `mapper/`, not lines in `.dev-flow/`.** The
checker as landed read only the artifacts, so it was structurally unable to see half the corpus.
**Fixed at close-out: the corpus now includes `mapper/**/*.py`**, with its own non-degeneracy floor
so a rename cannot silently empty it.

**And #6 is NOT mechanisable by this checker, which is the honest boundary.** *"X is gated"* is a
claim about what a **mutation** does; settling it requires **running** the mutation, which no text
checker can do. The mechanical guard for that class is at the **product** level — one arm per limb
(`test_at_p02g`, `test_at_p02h`) and the totality assertion `test_at_p02i`. This is written into
the checker's own docstring, because a checker that appears to cover a class it cannot decide is
worse than one whose limits are stated.

**PARTLY MECHANISED — landed this batch.** `tests/test_repair_artifact_claims.py` checks the two
claim shapes that are unambiguously decidable:
1. every `` `path:line` `` citation in this batch's **authored** artifacts resolves to a real file
   with at least that many lines;
2. every `test_*` identifier cited resolves to a collected node (or the stem of a parametrized one).

It reproduced the QA pass's hand-found phantom on its first run -- a node id left stale in an
increment packet after the test it named was renamed and parametrised. **The id is described here
rather than spelled**: this file is itself corpus the checker reads, so writing the dead token would
re-introduce it — C-56, and the checker reddened on exactly that when this paragraph first named it.
Its three counterfactual arms each redden with byte-exact restores.

**Deliberately NOT mechanised, and this is the honest boundary.** Claims 1–3 above are *prose about
semantics*. Deciding them needs the meaning of the claim, and a checker that guessed would
false-fail correct work — which costs as much as passing wrong work (C-53). **This checker itself
false-failed twice before it worked**: once treating bare basenames as missing files (65 false
findings), once resolving an ambiguous basename to a different batch's `increment-001.md` and
reporting 6 valid citations as past-EOF. A probe is code and needs verifying like any other.

**Proposed next step, spelled out so it is actionable rather than aspirational.** A third rule is
decidable and would have caught claim 1: **a comment or artifact line containing a quantified claim
about the tree (`every`/`no`/`none`/`all`) AND a greppable symbol must carry an executed probe
beside it.** Cheap form: require such lines to cite a command or a `file:line`, and check the
citation with the machinery already landed here. That is a rule change, so it belongs upstream in
the flow (C-45 PUSH), not in this project's tests — recorded here for whoever takes it.

**Review artifacts are excluded from the checker by design.** They are authored by independent
reviewers; editing their evidence to satisfy a check would corrupt the record this batch is judged
on. Their claims are theirs to stand behind. Two of the three phantom citations QA found live in
reviewer-authored files and are **left untouched**, noted rather than edited.

---

## Standing riders inherited by the feature batch

- **RIDER-1** — before the feature batch's **third** PDR fold, audit the fold against the **lenses'
  own condition lists**, never the amendment table. That instrument dropped conditions **twice**.
- **RIDER-2** — `S-18` (the render work-budget mechanism) returns as a design item at the feature
  batch's PDR, together with the pre-authorised A3 renderer-contract change. This batch landed the
  measurement only: **51 nodes, 410 edges → 2.3066s**, no budget asserted.
- **B3 is FIRED**, which turns on C-24 (golden drift named in the census) for the feature batch.
  `RadialRenderer` is pinned at all four sizes, so its Inc-1 **reddens four pins by construction** —
  an expected re-baseline, not a regression.

## Backlog carries (code)

| Item | Note |
|---|---|
| slow-lane wall-clock flake, ~10% | `FACTORY_TREE_BOUND_SECONDS = 8.0` and Textual Pilot's own timeout. **Confirmed pre-existing at `d877784`** by the QA gate, with zero branch code present. Make the bounds load-tolerant or non-gating; raising the constant only moves the threshold where the same class reappears. |
| `load_warnings` is unbounded | A million malformed entries produce a million strings. The fix changes a record format **18 tests pin**, so it wants its own increment. |
| `_text_attributes()` shim | One-line delegation kept because shipped tests use the name; collapse when those tests are next touched. |
| `create_from_template` | Still hand-constructs `SchemaField` with the old `f.get("kind","text")` shape — out of this batch's fence. |
| **`_build_sidecar` is hand-enumerated — the last hand list in the chain** | **Measured, not argued: a plain `str` field landed on `Node` reddens 0 of 647.** It classifies as text, so the totality guard passes by design; it goes unseen because `_derived_positions()` enumerates the text fields of `Ficha`/`Attachment`/`SchemaField`/`Document` while `Node` contributes only the structural `node.id`, and the serialiser would never write it. The coercion and the guard's class set are derived now, and the census is derived **within** the classes it walks — but **which classes it walks is itself a hand list** (`_derived_positions()`), and **the SAVE shape is not derived at all.** Those are the two rungs still standing, and they are the direct cause of the 0 above. Closing them means deriving `_build_sidecar` from the model — a behaviour change to the save path, so it wants its own increment. |
| A new `dict[str, str]` on another dataclass | Classifies, so `test_at_p02i` passes; the coercion call site is `Document`-only and the serialiser would not write it. Routing one is a **hand step** — now stated at every site that cites the guard, rather than implied to be automatic (re-confirmation review, MEDIUM-1). |
| The resolved predicate is ~430x more expensive per call | `0.8 µs → 348.5 µs` **(reviewer-measured; not re-derived here)**, uncached, called once per document (`~35 ms` at 100 documents). **Zero impact today** — no shipped sidecar carries a document and no perf arm covers that path — so it is carried rather than pre-optimised. One-line `lru_cache` if the document path ever carries load. |
| The str-map collision does not pin WHICH key survives | Keep-last vs keep-first reddens 0 of 647 **(reviewer-measured; not re-derived here)** — **and the covered sibling `Ficha.fields` is identical**, so this is symmetric and pre-existing, not a gap this batch opened. If it is ever pinned, pin both sites together. |
| no logging facility | `grep -rn "logging\." mapper/` → zero hits, so a masked programming error is unrecoverable. Mitigated, not fixed, by carrying `type(exc).__name__` in the message. |
| `TC-P02`/`P03`/`P04` are nominal | The `AT-` chain is complete with one distinct driving node each; the `TC-` layer exists as comment banners only. |
