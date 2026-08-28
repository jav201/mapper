# Increment 4 — HIGH-A: the `dict[str, str]` refusal sink and collision record get a gate

**Batch:** `2026-08-27-repair-batch-02` · **Base ref:** `d877784` · **Branch:** `fix/repair-batch-02`
**Increment base:** `01d7578` (the four-defect repair commit, PR #3) · **Language:** English

> **BLUF.** The independent confirmation review of `01d7578` came back **BLOCKED** with one new HIGH:
> the fix for HIGH-1 gave the new `dict[str, str]` family its covered sibling's *implementation* but
> not its sibling's *gate*, and `04-gate-findings-disposition.md` recorded those limbs as gated when
> they were gated by nothing. **I reproduced the finding before fixing it** — four mutants, **0 RED
> arms of 548 each**. After this increment the same four mutants redden **6 / 6 / 6 / 2**. The false
> disposition record is corrected in place rather than edited away, and it is the **sixth** recorded
> instance of this batch's false-record class — the enumeration is in `05-carries.md`.

---

## 1 · What changed

**One source file, three test arms, four corrected records.** The product behaviour was already
correct: HIGH-A is a *false-confidence* HIGH, not a crash HIGH. Nothing here changes what
`MapStore.load` does for any input — it changes what the suite can *see*.

### 1.1 · The finding, reproduced before it was fixed

`_coerce_str_map` (`mapper/store.py:127-145`) has three limbs. Before this increment only the scalar
ladder had an arm:

| Limb | Mutation applied | RED arms, whole tree (548) |
|---|---|---|
| the scalar ladder on keys and values | `Q-high1` (revert to raw pass-through) | **8** — gated |
| the non-mapping refusal sink | `MX1` — the guard block removed entirely | **0** |
| …its record | `MX2` — the record line deleted, refusal kept | **0** |
| …its refusal | `MX11` — the guard returns the value's repr instead of refusing | **0** |
| the collision record | `MX3` — the record block deleted, assignment kept | **0** |

```
COLLECTED: 548 (expected 548)
BASELINE:  pre-red arms: 0

=== MX1  :: non-mapping guard removed entirely ===              RED ARMS: 0
=== MX2  :: refusal becomes silent (record line deleted) ===    RED ARMS: 0
=== MX11 :: non-mapping coerced to its repr ===                 RED ARMS: 0
=== MX3  :: collision record deleted ===                        RED ARMS: 0
```

Run in my own scratchpad lab (`git archive 01d7578`), `PYTHONDONTWRITEBYTECODE=1`, every substitution
guarded by an asserted hit count of exactly 1, every restore proven by sha256 returning to the
pristine pin `4a36fdf26391ada2` (C-40, C-46). **Mutations are described here by position and
operation, never spelled verbatim** — this packet is corpus the id-scanner and the batch's own
artifact-claims checker read (C-56).

**Why the existing arms could not see it.** The census poisons *positions* — `document.tags.key` and
`document.tags.value` — and the poison helper always writes a **dict** into the field. So no arm
anywhere made `tags` or `inherited` stop being a mapping, and no arm ever put two colliding keys in
one. Both shapes are named in HIGH-1's own evidence and neither was carried into the fix's test set.
`Q-high1` reverts the whole construction, so its 8 arms are **all ladder arms**; it cannot
distinguish the other two limbs.

**The asymmetry is the finding.** `Ficha.fields` — the sibling the entire HIGH-1 argument rests on —
has an arm per limb. The new family had one of three. That is HIGH-1 one level down: the census grew,
the implementation grew with it, and the gate did not.

### 1.2 · The fix — one arm per limb, derived so a third field extends them

- `test_at_p02g` — a non-mapping str-map is **refused, recorded, and does not deny the map**.
  Three thresholds in one arm, each a different mutant's death. Parametrized over
  `_str_map_field_names(Document)` × three malformed shapes → **6 arms**.
- `test_at_p02h` — two raw keys that coerce to one string are **recorded**. → **2 arms**.
  The expected record string was **executed against the implementation**, not read off the format
  string (C-42).
- `test_at_p02i` — **the totality guard**, and the durable one. Every field of every dataclass
  **`mapper.model` defines** must be text, a str-map, or **explicitly declared** non-text.
  → **7 arms**, one per class, over a class set **derived from the module**.
- `test_at_p02j` — the class set itself is the model's, not a remembered subset. → **1 arm**.

  > **Corrected at the re-confirmation gate (MEDIUM-1).** As first written this guard hand-listed
  > **four** classes while the module defines **seven**, so a `str` field landed on `Node` — census
  > position 1, written by `_build_sidecar` — reddened **0 of 643**. The hand list had simply moved
  > up one level, from the field sets to the class set. The class set is now derived, and
  > `test_at_p02j` pins it. **And what this guard does NOT catch is now stated wherever it is
  > cited:** a new `dict[str, str]` on another dataclass *classifies*, so the guard passes — three
  > such fields measured at **0 RED of 643**.

### 1.3 · MEDIUM-C — the derivation was a textual annotation match, in BOTH the product and its census

`_str_map_fields` matched the annotation's *spelling*. Under `from __future__ import annotations`
that reads `Dict[str, str]`, `Mapping[str, str]`, `dict[str, str] | None`, a type alias and a quoted
annotation as **non-matches** — and the test's census predicate was byte-identical, so such a field
would have fallen out of the coercion **and** out of the census **together**, with no arm reddening.
HIGH-1's exact mechanism, latent.

Both predicates now resolve the annotation. **Executed — the swap changes no classification:**

```
class        old (spelled)            new (resolved)           identical
SchemaField  ()                       ()                       True
Attachment   ()                       ()                       True
Ficha        ('fields',)              ('fields',)              True
Document     ('tags', 'inherited')    ('tags', 'inherited')    True
```

**A resolved predicate is still not total, and that is why `test_at_p02i` exists.**
`Mapping[str, str]` remains neither text nor str-map. The tree contains **no such field today** —
which is precisely the C-55 condition: the guard is a no-op on the current tree, so it was
discharged against a **synthetic** case rather than an argument:

```
fields           : ['aliases', 'name', 'tags', 'template']
classified       : ['name', 'tags']
declared non-text: ['template']
UNCLASSIFIED     : ['aliases']            # aliases: Mapping[str, str]

GUARD VERDICT: RED  <-- unclassified field(s) ['aliases'] -- classify it or declare it
```

Its docstring says it **protects a conclusion, not a behaviour**, so the next reader does not file it
as an implementation detail and improve it away.

### 1.4 · The records that were false against disk

| # | Record | Was | Now |
|---|---|---|---|
| MEDIUM-B | `mapper/store.py` `_str_map_fields` docstring | *"adding another `dict[str, str]` field to **any** round-tripped dataclass extends the coercion automatically"* | Narrowed to what disk shows: the function has **exactly one call site**, `Document`-only. `Ficha.fields` is coerced at its own site with different record coordinates. |
| HIGH-A | `04-gate-findings-disposition.md` | *"same ladder, **same sink and same collision handling** … Gated by `Q-high1`: 8 arms"* | Corrected **in place, with the correction marked**, plus a per-limb table naming what actually gates each. |
| MEDIUM-A | `01-requirements.md` threshold 1 | *"each of the **17** derived positions"* | **21**, with the pre-fix `12 of 17` kept as an explicitly *historical* figure. Recorded as **AMD-1** (§7). |
| — | my own first draft of this correction | cited `increment-002.md` | `increment-004.md` — 002 and 003 already exist. Caught by reading the directory, and it would have been a **seventh** instance. |

**The `mapper/` call-site probe, executed:**

```
$ grep -rn "_coerce_str_map" mapper/          -> definition + ONE call site (store.py:350)
$ grep -rn "_str_map_fields"  mapper/         -> definition + ONE use, `_str_map_fields(Document)`
```

### 1.5 · Why Threshold 4 is a new threshold and not a clause folded into Threshold 2

Folding it in would have re-created the defect it closes. Threshold 2 is stated over **positions**,
and every position poison writes a mapping into the field — so a threshold-2 clause about the
map-valued fields would *still* have had no arm that makes `tags` stop being a mapping. A
two-subject acceptance is where this project has lost a threshold before. The requirement comes out
**larger**, which is C-43's constructive disposition.

### 1.6 · The artifact-claims checker — widened where the defects actually live, and its limit stated

`tests/test_repair_artifact_claims.py` read only `.dev-flow/`. **Three of the six recorded instances
were comments in `mapper/`**, so the checker was structurally unable to see half its own corpus. The
corpus now includes `mapper/**/*.py`, with its own non-degeneracy floor so a rename cannot silently
empty it. The two decidable rules are unchanged; only the corpus widened.

**Verified non-false-failing before landing** (C-53 — run a new rule over a corpus you believe is
*correct*): the four citations `mapper/` carries today all resolve, and both basenames are
unambiguous. `_live_nodes()` is now cached — the widened corpus made it 40 arms, and an uncached
collection subprocess per arm added minutes for an answer that cannot change within a run.

**And the honest boundary, written into the checker's docstring:** HIGH-A's false record is
**not mechanisable here**. *"X is gated"* is a claim about what a **mutation** does; settling it
requires **running** the mutation. The mechanical guard for that class is at the product level —
`test_at_p02g`, `test_at_p02h`, `test_at_p02i`. A checker that appeared to cover a class it cannot
decide would be worse than one whose limits are stated.

### 1.7 · Re-confirmation gate — conditions discharged, and one claim I could NOT make

The independent re-confirmation of `d75f0fd` returned **PASS WITH CONDITIONS, no HIGH**. Both
conditions are discharged below. **Both findings were reproduced here before being fixed.**

| Condition | Reproduced | Discharge |
|---|---|---|
| **MEDIUM-1** — the docstring rewritten *to fix* MEDIUM-B named `test_at_p02i` as the gate for a case it does not gate | a `dict[str, str]` landed on `Attachment`: **0 RED of 643** | the sentence now says what the guard does **and does not** catch, at all three sites that cited it (`mapper/store.py`, this packet §1.2, `01-requirements.md` AMD-2) |
| **MEDIUM-1, second half** — the guard's **class set** was a hand list: 4 classes, module defines 7 | a `str` field landed on `Node`: **0 RED of 643** | the class set is **derived from the module**; `test_at_p02j` pins it |
| **MEDIUM-2** — `05-carries.md` carried a count stale at the tip it names | read against disk: said `548`, tip collects `643` | corrected, and the line now says *re-measure*, not a number to copy |

**Counterfactual for the two new guards — per resolved arm, whole tree, 647 asserted:**

| Mutation | RED arms | The arms |
|---|---|---|
| `Node` dropped from the declared non-text map | **2** | `test_at_p02i[Node]`, `test_at_p02j` |
| the class derivation re-narrowed to exclude `Node` | **1** | `test_at_p02j` — the class set is genuinely pinned |
| a `dict[str, int]` field landed on `Node` | **1** | `test_at_p02i[Node]` — a field that is neither text nor str-map now reddens; before the class-set fix it could not, because `Node` was not in the set |
| **a plain `str` field landed on `Node`** | **0** | **nothing. See below.** |

> **What I did NOT close, stated because the whole finding was an over-claim.** The reviewer's
> measured case — a `str` field on `Node` — **still reddens nothing**, and deriving the class set did
> not change that. A `str` field *classifies as text*, so the totality guard passes by design. It
> goes unseen for a different reason one layer down: `_derived_positions()` enumerates the text
> fields of `Ficha`, `Attachment`, `SchemaField` and `Document`, while `Node` contributes only the
> structural `node.id` — and `_build_sidecar` is hand-enumerated, so such a field would never be
> written at all. **That is a real remaining gap and it is carried, not fixed here**: closing it means
> deriving the serialiser's shape from the model, which is a behaviour change to the save path and
> belongs in its own increment. What the class-set fix genuinely buys is the two rows above it.

---

## 2 · Files modified

| File | Kind | Change |
|---|---|---|
| `mapper/store.py` | **source (1)** | `_str_map_fields` resolves annotations; docstring narrowed to the truth |
| `tests/test_repair_store_boundary.py` | test | census predicate resolved; `test_at_p02g`, `test_at_p02h`, `test_at_p02i` added |
| `tests/test_repair_artifact_claims.py` | test | corpus widened to `mapper/`; source-half floor; node collection cached |
| `.dev-flow/…/01-requirements.md` | artifact | census 17 → 21; `M-STO-b` scope; **Threshold 4**; §7 AMD-1 + AMD-2 |
| `.dev-flow/…/04-gate-findings-disposition.md` | artifact | the false "gated by" row corrected in place |
| `.dev-flow/…/05-carries.md` | artifact | the six-instance enumeration; the mechanisation boundary |
| `.dev-flow/…/03-increments/increment-004.md` | artifact | this packet |

**Source-file budget: 1 of 4.** Tests are uncapped; `.dev-flow/**` artifacts are outside the count.

---

## 3 · How to test

```bash
export PYTHONUTF8=1
python -m pytest -q -p no:randomly -o addopts= -m "not slow"   # fast lane
python -m pytest -q -p no:randomly -o addopts= -m "slow"       # slow lane
python -m pytest -q --collect-only -p no:randomly -o addopts=  # ledger
ruff check mapper/ tests/
python -m pytest -q -p no:randomly -o addopts= tests/test_repair_store_boundary.py \
  -k "p02g or p02h or p02i"                                    # the new arms alone
```

---

## 4 · Test results — executed, read from each run's own output

| Measure | At `d75f0fd` (pre-condition) | **Final (conditions discharged)** |
|---|---|---|
| collected | 643 | **647** |
| fast lane | 626 passed, 17 deselected, exit 0 | **630 passed, 17 deselected**, exit 0 |
| slow lane | 17 passed, 626 deselected, exit 0 | **17 passed, 630 deselected**, exit 0 |
| the new arms alone | 12 passed | **16 passed** |
| `ruff check mapper/ tests/` | 29 | **29** — unchanged from base |
| ruff on the three touched files | clean | **All checks passed!** |

**Ledger — `post = base − D + A`, derived and then measured:**

| Term | Value | Derivation |
|---|---|---|
| base (`01d7578`) | 548 | measured |
| D (deletions) | 0 | no test removed |
| A — boundary arms | +16 | `test_at_p02g` 6 · `test_at_p02h` 2 · `test_at_p02i` **7** (one per model dataclass) · `test_at_p02j` 1 |
| A — artifact-claims file | +83 | 1 corpus arm + 41 × 2, where 41 = 8 authored artifacts + 33 `mapper/` source files |
| **post** | **647** | 548 + 99; boundary file 84 → **100** |

**The checker's corpus includes this packet**, so writing it adds two arms to the count it reports —
a reflexive property worth naming rather than discovering. The 643 above is the count **with** this
file present.

### 4.1 · Mutation counterfactual — per resolved arm, never the exit code

| Mutant | Limb attacked | RED arms **before** (of 548) | RED arms **after** (of 643) |
|---|---|---|---|
| `MX1` | non-mapping guard removed | **0** | **6** — every `test_at_p02g` arm |
| `MX2` | refusal made silent | **0** | **6** — every `test_at_p02g` arm |
| `MX11` | non-mapping coerced to its repr (`M-STO-b` on the map field) | **0** | **6** — every `test_at_p02g` arm |
| `MX3` | collision record deleted | **0** | **2** — both `test_at_p02h` arms |

Both batteries assert the resolved arm count before trusting any verdict (548 / 643, matched), assert
the baseline resolves **0** pre-red arms, and prove every restore by sha256 — pristine pins
`4a36fdf26391ada2` (pre) and `d88064cf864c9c4a` (post).

**The post-fix battery ran on a copy taken one docstring edit before the final tree.** Stated rather
than hidden: the two `mapper/store.py` files are **AST-identical once docstrings are stripped**
(`ast.dump` sha256 `6e07eb756e774d8b52a58ea9` on both), so no arm's verdict can differ.

**One harness defect found and reported, not papered over:** my summary-line extraction grabs the
last stdout line, which is sometimes a Textual task-cancellation warning rather than pytest's
summary. **The per-arm verdicts are unaffected** — they are computed from the parsed `FAILED` node
set and the asserted-green baseline, not from that line.

**One process error, caught and corrected:** I compared the lab copy against the tree **while the
battery was mid-mutation**, and read a difference that was the harness's own applied mutant. The
comparison was invalid, not the tree; it was re-run after the battery completed. Never read an
artifact another session is writing — recorded because it nearly became a finding about the fix.

---

## 5 · Risks

| Risk | Assessment |
|---|---|
| `get_type_hints` resolves at call time and can raise on an unresolvable annotation | Bounded: called only on four module-level dataclasses whose annotations are builtins. A future unresolvable annotation raises **loudly** at load, which is the desired direction — and `test_at_p02i` reddens first. |
| `_EXPECTED_NON_TEXT` is a hand-listed exception set | Deliberate, and it is the *exception* list, not the input set. Both directions are asserted: a declared name that is not a field also fails. |
| The checker's widened corpus could false-fail on a future `mapper/` comment | Real and intended — that is the point of the check. Ambiguity resolves to `None` and reports, rather than guessing. |
| Behaviour change | **None.** Classification is identical before and after; the product's coercion is untouched. |

---

## 6 · Pending items

- **`state.json` still describes the parked feature batch** (P-CARRY-1) — `batch_id`
  `2026-08-26-ui-next-batch-02`, `current_station` `PDR`, `tests_collected` **429**. On merge,
  master's canonical state file would assert something false. Owned by the batch close, **not yet
  landed** — this is the C-44 item and it is deliberately after the code re-confirmation.
- Every carry in `05-carries.md` stands: `TC-P02`/`TC-P03`/`TC-P04` nominal, unbounded
  `load_warnings`, the slow-lane wall-clock flake, no logging facility.
- MEDIUM-1 (the sixth falsehood without an arm) and MEDIUM-2/3/5 from the whole-branch QA pass remain
  dispositioned as carries; this increment did not re-open them.

---

## 7 · Suggested next task

Land the `state.json` close record (P-CARRY-1), then merge and sync. After that, the first code item
is the unbounded `load_warnings` — it changes a record format 18 arms pin, so it wants its own
increment.

---

## 8 · Evidence checklist

| Item | ✓/✗ | Evidence |
|---|---|---|
| The HIGH was reproduced before being fixed | ✓ | §1.1 — 4 mutants, 0 RED of 548 each, in my own lab |
| Every new arm's counterfactual executed, per resolved arm | ✓ | §4.1 — 6 / 6 / 6 / 2, arms named |
| Baseline asserted non-degenerate before any verdict | ✓ | both batteries: collected 548 / 643 asserted, 0 pre-red arms |
| Every mutation restored, proven by hash | ✓ | sha256 `4a36fdf26391ada2` / `d88064cf864c9c4a` |
| Mutations run where no other session reads | ✓ | scratchpad `lab/` and `lab2/`, never the repo tree |
| Bytecode cache neutralised | ✓ | `PYTHONDONTWRITEBYTECODE=1` in both batteries (C-46) |
| Mutations described by position, not spelled | ✓ | §1.1 (C-56) |
| The tree-vs-lab delta proven immaterial | ✓ | §4.1 — AST-identical with docstrings stripped |
| A guard that is a no-op today discharged synthetically | ✓ | §1.3 — `Mapping[str, str]` probe goes RED (C-55) |
| The predicate swap proven classification-neutral | ✓ | §1.3 — 4 of 4 identical |
| New checker rule run over a corpus believed correct | ✓ | §1.6 — 4 citations resolve, basenames unambiguous (C-53) |
| False records corrected in place, not edited away | ✓ | §1.4 — correction marked and dated |
| Source-file budget | ✓ | 1 of 4 |
| Both lanes green, ledger reconciles | ✓ | §4 — 626 + 17 = 643 |
| Secrets | ✓ | none touched; no credential, path or token in any diff |
