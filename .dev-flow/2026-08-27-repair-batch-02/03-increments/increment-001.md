# Increment 1 — `HLR-STO.1` / `LLR-STO.1.1`: the store boundary returns text where text is promised

**Batch:** `2026-08-27-repair-batch-02` · **Base ref:** `d877784` · **Branch:** `fix/repair-batch-02`
**Source files: 1 of 4** (`mapper/store.py`). Tests uncapped. `.dev-flow/**` outside the count.

> **BLUF.** `MapStore.load` promised text and delivered other types in 12 of 17 derived positions,
> and leaked four untyped exceptions on hostile input. The repair generalises the existing coercion
> ladder from one dataclass to every dataclass the serialiser round-trips, and puts a typed net
> around the two escape paths.
>
> **The code change was the cheap part.** Four successive counterfactual passes each found the
> increment's own tests certifying less than they claimed: my first battery found two INERT mutants
> (the typed nets were gated by nothing); the reviewer's first pass found the containment clause
> ungated across **every** family, proved by a mutant that survived 139 arms; its second pass found
> the fix for that still inert on 4 arms, because an undescribed sibling node's empty ficha
> satisfied the assertion graph-wide; its third found this file's record checks leaning on another
> batch's suite. **Every one of those was invisible to a green suite.** Final state: 70 arms,
> **19 mutants each reddening a named arm**, four of them the reviewer's own.

---

## 1 · What changed

**The defect.** `_text_attributes()` derived `Ficha`'s text fields from the model's own annotations
— a correct derivation, wired to exactly one of the four dataclasses `_build_sidecar` round-trips.
`Attachment`, `SchemaField` and `Document` were hand-constructed two lines below it and stayed raw.
This is the failure mode the requirement names: *a control implemented to the edge of the noun that
was named.*

Four changes, all inside `mapper/store.py`:

1. **`_text_attributes()` → `_text_fields(cls)`.** The derivation now takes the dataclass as a
   parameter; `_text_attributes()` remains as a one-line delegation because shipped tests use that
   name. A new `_coerce_text_fields(graph, owner, cls, data)` applies the existing `_coerce_field`
   ladder to every text field `cls` declares. Adding a `str` field to any of these dataclasses now
   extends the coercion automatically — which is the property that makes it a derivation rather
   than a hand list with extra steps.
2. **The three raw constructions are routed through it** — `SchemaField`, `Document`, `Attachment`.
   Their non-text fields (`required`/`template` are `bool`, `tags`/`inherited` are dicts by design)
   are passed through untouched, because `_text_fields` does not select them.
3. **Two positions that were never fields at all are coerced:** the **node id** (a mapping KEY, so it
   never passed through the field ladder) and the **field key** (only its value went through it).
   Coercing the id normalises the key TYPE so `graph.nodes`, keyed by `str`, cannot be handed an int.
   **It does not remove the phantom node** — a sidecar id matching no parsed node is still added
   alongside the parsed ones and still moves `coverage()`'s denominator; that is outside this batch's
   fence. *(An earlier revision of this packet, and of the code comment, claimed the repair removed
   the phantom. It does not. Corrected per review F4 — a false record is a defect in the evidence.)*
4. **Typed refusal (`S-11`).** `load` now raises only `MapStoreError`: a top-level non-mapping
   sidecar is refused explicitly, and two `except Exception` nets wrap the sidecar walk and the
   reindex, each re-raising `MapStoreError` untouched and chaining anything else with
   `raise ... from exc`. The nets are the OUTER guard, not the repair — the ladder is what makes
   the known shapes unreachable. The nets exist because *"the shapes we know"* is precisely the
   claim that was wrong before.

**Why the threshold is type-at-the-boundary and not consumer behaviour.** Premise `P-8`:
`Graph.search_hits` joins `a.caption or a.path`, so a poisoned `path` is observable only when
`caption` is falsy. A predicate keyed on *"`search_hits` does not raise"* is invariant under the
change it gates for half its input space — C-40 limb 1. Putting `load`'s own output in the
predicate is what makes it a gate rather than a coincidence.

### 1.1 · The finding this increment made against itself

The first mutation battery reported **two of six mutants INERT**: removing either typed-refusal net
reddened **zero** arms. The cause is C-55 limb 2 — *a guard clause that is a no-op on today's data
is untested however green the suite*. Once the ladder covers every derived position, **no container
poison reaches the nets any more**, so the 15 container arms of `AT-P03` pass whether the nets exist
or not. The position census poisons VALUES and therefore structurally cannot produce the SHAPE
errors the nets exist for.

Closed by constructing the cases the census cannot contain, and the arms were established as
net-reaching **independently of the net** (each asserts its `__cause__` is a non-`MapStoreError`,
which is only true if an untyped exception was raised and converted):

- `test_at_p03b` — five malformed sidecar shapes (nodes as a list, a node as a scalar, schema as a
  mapping, a scalar schema item, a scalar document item). **5 arms**, all RED under the mutant.
- `test_at_p03c` — a top-level non-mapping sidecar.
- `test_at_p03d` — a synthetic fault injection on `_reindex`. **Synthetic by necessity and that is
  the discharge, not a shortcut:** with the ladder in place no constructible sidecar reaches
  `_reindex` in a failing state, so without this arm deleting that net reddens nothing at all.
- The original container arms are **relabelled in their own docstring as a regression PIN, not a
  gate** (C-40's corollary): kept, but not permitted to stand as the certification.

### 1.2 · The independent review BLOCKED this increment, and what it cost

The first verdict was **BLOCKED on one HIGH finding**, plus eight more. The HIGH was the risk I had
flagged against myself — and the reviewer showed it was **broader than my flag**: threshold 2's
containment clause (*"leaves that position `""`"*) was **ungated for every family**, not only
attachments. It proved this with a mutant that refuses a container by **destroying** the entity
after recording a warning: **139 store-facing arms and all 57 of this file's arms stayed green.**
`offenders == []` is satisfied vacuously by a drop, because a destroyed position offends nothing.

| # | Class | Finding | Disposition |
|---|---|---|---|
| F1 | **HIGH** | containment half ungated; `isinstance(a, dict)` silently destroyed a malformed attachment | **fixed** — `_mappings` refuses-and-records; `test_at_p02` pins presence; `test_at_p02b` added |
| F2 | MEDIUM | `_coerce_text_fields` hard-coded `""`, so a `kind`-less sidecar's `"text"` became `""` **and was written back to disk** | **fixed** — the dataclass's own default is used; `test_at_p01b` poisons by omission |
| F3 | MEDIUM | two raw field keys coerce to one string; the first was destroyed silently | **fixed** — `campo duplicado:` record; `test_at_p02d` |
| F4 | MEDIUM | the node-id comment claimed a repair the code does not perform | **fixed** — comment corrected; `nodo duplicado:` record; `test_at_p02d[node-ids-both-refused-collapse-onto-empty]` |
| F5 | MEDIUM | `_KEY_POSITIONS`' justification (containers) was narrower than the exclusion it granted (the whole refusal branch) | **fixed** — exclusion narrowed in prose; `test_at_p02c` drives `b"hi"` into both key positions |
| F6 | MEDIUM | `assert graph.load_warnings` was truthiness-only | **fixed** — content asserted per position; hardened again at C2 to the full record |
| F7 | LOW | the field-key warning label was a literal, so every bad key reported the same position | **fixed** — `key[{key!r}]`, owners indexed |
| F8 | LOW | one net spliced the raw exception (routinely carries a filesystem path) into operator-facing Spanish | **fixed** — `type(exc).__name__` |
| F9 | LOW | `except Exception` masks programming errors; `mapper/` has zero `logging.` hits | **accepted and recorded** — the reviewer endorsed the trade; carried to the backlog |

**Two costs worth recording rather than smoothing over.**

1. **My first F1 fix over-reached.** I routed `schema` and `documents` through `_mappings` too. That
   made three `_MALFORMED_SHAPES` arms stop raising — a behaviour change no finding asked for, which
   also removed three arms from the typed net's own counterfactual. Reverted to attachments-only:
   those families were never *silently* dropped, they escaped to the net, which is loud. The scoping
   is stated in `_mappings`' docstring so the next reader does not "fix" the inconsistency blind.
2. **My F6 fix false-failed correct code.** The naive `position.split(".")[-1]` fragment is wrong for
   `fields.value`, whose refusal is recorded under the field's KEY (`campo ilegible: A.E`), not the
   word *"value"*. C-53: a rule that false-fails correct work costs as much as one that passes wrong
   work. The map is now explicit, the exception named, and asserted total over the census.

### 1.3 · Second review round — OK WITH FIXES, four more findings

The re-review returned **OK WITH FIXES**: F1–F8 verified genuinely fixed by the reviewer's own
mutants. Four new findings, all dispositioned.

| # | Class | Finding | Disposition |
|---|---|---|---|
| G1 | MED | the F1 containment assertion was **inert on the `node.*` arms**: `MMD` declares nodes `A` and `B`, but the fixture described only `A`, so `B` loaded with a default `Ficha` whose every text field is `""` — satisfying `(position, "") in live` **graph-wide** whatever happened to `A` | **fixed** — `B` given a full sidecar entry; `_poison` re-keys `A` only so the poison cannot undo it. Proven by `M-RR2`: all 15 container arms now redden |
| G2 | MED | `any("duplicado" in w)` let a mutant **swap the two nouns and corrupt both payloads** and still pass — the same weakness class as F6 | **fixed** — each collision case declares its exact full record; `M-STO-n` now reddens |
| G3 | MED | `documento duplicado` had **zero arms** — the ungated sibling of F3/F4 | **fixed** — two arms (coercion-induced, plainly-identical); `M-STO-l` reddens both |
| G4 | LOW | `_mappings` emitted *n* byte-identical un-indexed records, against F7's own indexing | **fixed** — `{owner}.{key}[{i}]`; `M-STO-m` reddens the two-entry arm |

**The Q1 ruling, and the condition attached.** Keep `_mappings` attachments-only — measured:
schema/document item-scalars are **denied typed**, and only attachments carried the silent-loss
class. The condition was to state the asymmetry **in observable terms**, done in the helper's
docstring: *loud denial is already a report; silent discard is not*, so routing the denied families
through the helper would convert a denial into a warning.

**The Q3 ruling, and the part I had to act on.** The duplicate records are in-fence — but
`documento duplicado` **also fires with no coercion involved** (two plainly identical names, a silent
overwrite before this line). That is a strict superset of what `LLR-STO.1.1` asked for. It is now
**declared as such at the call site** and given arms for both cases. I kept it rather than reverting
— same silent-data-loss class as F3/F4, one line — but it is genuinely outside the requirement's
fence and is recorded as an out-of-fence addition, not smuggled in.

**A negative control added unprompted.** Every collision arm asserts a record is PRESENT, so a guard
firing **unconditionally** would pass all of them. `test_at_p02f` asserts a clean map records no
collision; `M-STO-o` (`if True:`) reddens exactly that arm and nothing else.

### 1.4 · Count reconciliation — the two measurements were of different mutants

The reviewer measured **3** RED arms where my packet reported **2**. Neither was wrong: they are
**different mutants**. Both are now in the battery, derived rather than typed.

| Mutant | What it does | RED arms |
|---|---|---|
| `M-STO-g` (mine) | `_mappings` drops the non-mapping entry **silently** | **2** — `test_at_p02b[attachment-item-is-a-scalar]`, `[attachment-item-is-a-string]` |
| `M-RR1` (the reviewer's) | refuses a poisoned attachment by **destroying the entry** instead of emptying its field | **3** — `test_at_p02[attachment.kind]`, `[attachment.path]`, `[attachment.caption]` |

The first mutates the *record*; the second mutates the *containment*. They gate different clauses of
threshold 2, which is exactly why they redden disjoint arm sets. **The reviewer withdrew the
discrepancy** on this analysis.

### 1.5 · Confirmation pass — **PASS**, plus two LOW carries folded

The reviewer's third pass verified G1–G4 fixed with **its own** mutants and returned **PASS**.

- **Q1 — G1 is live, and the inertness did not move.** Two independent measurements: on a clean load
  **0 of 15** container arms are satisfied without the poison (previously `node.state`/`meta`/
  `notes` were), and each `(position, "")` pair has **exactly one source**, so the `""` the assertion
  observes is uniquely attributable to the poisoned entity. Their `N1` went from **1 arm → 4**.
- **Q2 — keep `documento duplicado`, do not revert.** The in-fence and out-of-fence halves are the
  *same check*; splitting them would mean carrying raw names alongside coerced ones purely to
  preserve a known silent overwrite. Kept, still declared as a superset.
- **Q3 — `test_at_p02f` is sound and does unique work.** Their documents-guard-only mutant reddens
  exactly one arm in the whole tree: mine.

| # | Class | Carry | Disposition |
|---|---|---|---|
| C1 | LOW | `_poison`'s node.id comment claimed re-keying `A` preserves the fixture's property. Preserving `B` is **necessary but not sufficient**: re-keying removes `A` from the sidecar while `MMD` still declares it, so the parsed `A` loads with a default ficha and the empties return | **fixed, comment only** — it now states the measured behaviour, why it is harmless (`node.id` never reaches the containment assertion), and what would break if it ever did |
| C2 | LOW | the file's own record checks were still substring-based, so a corrupted **owner** coordinate with an intact leaf was caught by **8 arms in `test_repair_fields.py` and 0 here** — this increment leaned on another batch's suite for the property F6 raised | **fixed** — `_EXPECTED_REFUSAL` declares the full record per position, asserted total over the census |

**C2's fix is measured, not asserted.** Their `N5` (owner destroyed, leaf intact) reddened **zero**
arms in this file before the fix and **17** after — the 15 container arms plus both key positions.
The file now stands on its own.

Both `N1` and `N5` are folded into the battery on the reviewer's advice. `M-RR2` mutates the
*refusal value*, which the `offenders` assertions would catch in weaker form; **`N1` isolates
containment** and is the mutant that would actually have caught G1. Keeping both is the point — they
fail independently.

---

## 2 · Files modified

| File | Kind | Δ | Note |
|---|---|---|---|
| `mapper/store.py` | **source (1 of 4)** | +166 / −28 | the only source change in the whole batch |
| `tests/test_repair_store_boundary.py` | test (new, uncapped) | 492 lines | 66 nodes |
| `.dev-flow/2026-08-27-repair-batch-02/PLAN.md` | flow artifact | new | outside the budget |
| `.dev-flow/.../03-increments/increment-001.md` | flow artifact | this file | outside the budget |

Under the 4-source cap with 3 to spare. No new dependency. No file moved.

---

## 3 · How to test

```bash
cd C:/Users/jjgh8/Github/mapper
PYTHONUTF8=1 python -m pytest -q -p no:randomly -o addopts= -m "not slow"   # fast lane
PYTHONUTF8=1 python -m pytest -q -p no:randomly -o addopts= -m "slow"       # slow lane
PYTHONUTF8=1 python -m ruff check mapper/ tests/
PYTHONUTF8=1 python -m pytest tests/test_repair_store_boundary.py -q -p no:randomly -o addopts=
```

The mutation battery is detached and lives outside the repo (scratchpad `battery.py` + `mutlab/`);
it copies the tree, mutates the copy, and never opens the live repo for writing.

---

## 4 · Test results — executed, read from each run's own output

All figures below are post-review-fix. The pre-fix figures are superseded, not deleted: the first
gate measured 470/16 fast and 57 nodes, and the review's nine findings added nine arms.

| Run | Result | Exit |
|---|---|---|
| fast lane | **483 passed, 16 deselected** in 91.25s | 0 |
| slow lane | **16 passed, 483 deselected** in 38.20s | 0 |
| new file alone | **70 passed** in 2.60s | 0 |
| collection | **499 tests collected** | 0 |
| `ruff check mapper/ tests/` | **29 errors** — equal to the base measurement, all pre-existing | — |
| `ruff check` on the two touched files | **All checks passed** | 0 |

**Test ledger** `post = base − D + A` → `499 = 429 − 0 + 70`. Collected **499**; fast 483 + 16
deselected = 499 ✅.

**Blast radius.** The whole suite, both lanes, not a `-k` filter. Zero regressions: 483 − 70 = 413,
exactly the pre-existing fast-lane figure at the base ref.

### 4.0 · A pre-existing slow-lane flake, identified and reproduced

The reviewer reported one unexplained slow-lane failure (1 failed / 15 passed, the name eaten by its
command) that did not recur. **It is real, it is pre-existing, and it is not caused by this diff.**

| Probe | Result |
|---|---|
| slow lane × 10, this tree | **1 failure in 10 (10%)** — matching the reviewer's ~11% |
| the failing node | `test_repair_depth.py::test_at_r16b_the_factory_screen_survives_a_depth_5000_map_composed` |
| its failure mode | `textual.pilot.WaitForScreenTimeout: Timed out while waiting for widgets to process pending messages` |
| second load-sensitive node, forced under deliberate CPU load | `test_at_r16_the_factory_tree_survives_a_depth_5000_map` — *"the factory tree took 10.360s"* against `FACTORY_TREE_BOUND_SECONDS = 8.0` |
| negative control for that one | the same node passed at **3.97s** and **3.56s** once the load eased |
| unloaded headroom | `_tree_lines()` measures 2.6–3.4s against the 8.0s bound — only **2.4–3.0×** |

**Root cause: the slow lane asserts WALL CLOCK on a shared machine.** Two independent mechanisms —
an explicit `FACTORY_TREE_BOUND_SECONDS = 8.0` budget, and Textual Pilot's own internal screen
timeout. Both live in `tests/test_repair_depth.py`, both predate this batch, and neither is touched
by this diff. The reviewer's failure and mine occurred while **two pytest suites were running
concurrently**, which is exactly the condition that consumes 2.4× headroom.

**Two honesty notes on this measurement.** (i) The single failure in my ten runs landed on run 4,
which took 72.67s against a ~40s norm — **because my own deliberate-load experiment was running at
that moment**. I induced it; I am not claiming an independent spontaneous reproduction. (ii) The ten
runs straddled an edit to the boundary test file (deselected count moves 479 → 483 between runs 7
and 8). The slow-marked tests themselves were untouched throughout, but the hunt was not run against
a frozen tree.

**Not fixed here — deliberately.** Re-basing these bounds is not one of this batch's four defects.
Carried to the backlog with the reproduction recipe. The recommendation is to make them
load-tolerant or non-gating rather than to raise the constant, since raising it only moves the
threshold at which the same class of failure reappears.

### 4.1 · Mutation counterfactuals — per resolved arm, never the exit code

Detached lab, verdicts parsed from `junitxml` per node id, `PYTHONDONTWRITEBYTECODE=1` (C-46).
Harness self-guards, each asserted before any verdict is trusted: the substitution count must be
exactly 1 (*a mutation that never applied reads as a survivor*), the baseline must resolve exactly
66 arms and be all-green (*an arm the harness cannot see is an arm it cannot report inert*; a
baseline resolving zero arms makes its own all-green check compare `0 == 0`), and each restore is
proven by sha256 returning to the pristine value.

**The substitution guard fired for real.** The first re-run after the review fixes **aborted**:
`M-STO-a`'s site no longer existed, because the F2 fix rewrote that function. Without the guard the
mutant would have been reported as a survivor of a mutation that never applied.

Pristine `mapper/store.py` sha256 `49123c83…42ac1458`; final sha256 identical; the **live** repo file
hashes to the same value, so the battery provably never touched it.

| Mutant | Mutation, by position and operation | RED arms |
|---|---|---|
| `M-STO-a` | `_coerce_text_fields`: drop the ladder call, return raw values — **the pre-fix defect** | **20** / 70 |
| `M-STO-b` | `_coerce_field`: the container-rejection branch returns `str(value)` | **16** / 70 |
| `M-STO-c` | the node-id position: bind the raw mapping key | **3** / 70 |
| `M-STO-d` | the `fields.key` position: bind the raw key | **3** / 70 |
| `M-STO-e` | the net around the sidecar walk: re-raise instead of wrapping | **5** / 70 |
| `M-STO-f` | the net around `_reindex`: re-raise instead of wrapping | **1** / 70 |
| `M-STO-g` | **the reviewer's own F1 mutant** — `_mappings` drops the non-mapping silently | **2** / 70 |
| `M-STO-h` | `_coerce_text_fields`: hard-code the missing-key default back to `""` (the F2 regression) | **2** / 70 |
| `M-STO-i` | the field-key loop: drop the collision record (F3) | **1** / 70 |
| `M-STO-j` | the node-id loop: drop the duplicate record (F4) | **2** / 70 |
| `M-STO-k` | `_mappings`: the NOT-A-LIST branch returns empty without recording | **1** / 70 |
| `M-STO-l` | the document loop: drop the duplicate-name record (**G3**) | **2** / 70 |
| `M-STO-m` | `_mappings`: drop the entry INDEX from the record (**G4**) | **2** / 70 |
| `M-STO-n` | the collision records: **swap the nouns and corrupt both payloads** (**G2**) | **1** / 70 |
| `M-STO-o` | the collision guard fires **unconditionally** — the negative control's mutant | **1** / 70 |
| `M-RR1` | **the reviewer's G1 mutant** — destroy the poisoned attachment entry instead of emptying its field | **3** / 70 |
| `M-RR2` | `_coerce_field`: the refusal branch returns a **non-empty placeholder** instead of `""` | **16** / 70 |
| `N1` | **the reviewer's containment mutant** — destroy the NODE when a ficha text attr is refused | **4** / 70 |
| `N5` | **the reviewer's owner mutant** — destroy the owner coordinate, leave the leaf intact | **17** / 70 |

`M-STO-a` and `M-STO-b` are the requirement's two **named** weaker variants; both redden as specced.
`M-STO-g` is the mutant that **survived all 139 arms** at the first review.

**`M-RR2` is the direct proof G1 is closed.** Threshold 2 says a refused position is left EMPTY; a
refusal returning `"?"` reddens **all 15 container arms**, including the four `node.*` arms that were
inert while node `B` had no sidecar entry and its default-empty ficha satisfied the assertion
graph-wide.

**Four mutants exist only because one mutation says nothing about a neighbouring branch** (C-55 limb
2): `M-STO-k` (`_mappings`' other refusal branch), `M-STO-m` (the record's index, not its presence),
`M-STO-n` (the payload, not the noun), and `M-STO-o` (a guard firing unconditionally passes every
present-record arm).

Green arms are named rather than implied: under `M-STO-c`/`M-STO-d` exactly the three arms bound to
that position redden and the other 67 stay green, which is what a per-position census should do.
Under `M-STO-e`/`M-STO-f` the container arms of `AT-P03` stay green **by construction** — the finding
in §1.1, and the reason those arms are labelled pins rather than gates.

---

## 5 · Risks

1. **The outer nets can mask a genuine programming error** (a typo raising `AttributeError` inside
   the sidecar walk) as a user-facing Spanish *"ilegible"* notice. Accepted deliberately: a typed
   refusal degrades to a notice while an untyped one kills the screen, and `US-N13`'s «sala» loads
   every map in the workspace on mount — one malformed sidecar anywhere would take the whole mount
   down. `raise ... from exc` preserves the chain for diagnosis.
2. **`_text_attributes()` is retained as a shim.** A one-line delegation kept because shipped tests
   use the name. Watch-item, not a compat layer; it should be collapsed when those tests are next
   touched — carried to the backlog rather than done here.
3. **`_mappings` is scoped to attachments, so refusal handling is not uniform.** A malformed
   `schema`/`documents` entry escapes to the typed net (loud) rather than being refused-and-recorded.
   **Ruled by the reviewer: keep it** — measured, schema/document item-scalars are denied typed, and
   only attachments carried the silent-loss class. Loud denial is already a report; silent discard is
   not. The asymmetry is stated in observable terms in the helper's docstring, per their condition.
6. **`documento duplicado` is a declared OUT-OF-FENCE addition.** It fires for a coercion-induced
   collision, which `LLR-STO.1.1` owns — and **also for two plainly identical names, where no
   coercion is involved**, which the requirement never asked for. That case was a silent overwrite
   before this line. Kept because it is the same silent-data-loss class as F3/F4 and costs one line,
   but declared at the call site and here rather than smuggled in.
7. **The slow lane carries a pre-existing ~10% load-induced flake** (§4.0). It is not caused by this
   diff and is not fixed here. It means **any slow-lane result taken while another suite is running
   is unreliable** — including this batch's own. Carried to the backlog with its recipe.
4. **`Document` keying changed** from the raw `d.get("name")` to the coerced `doc.name`. The
   reviewer verified the falsy-drop (`0` dropped, `5` → `"5"`) is **pre-existing**, not a regression.
5. **The `except Exception` nets have no log to recover a masked programming error** — `mapper/` has
   zero `logging.` call sites. The reviewer endorsed the trade (F9); `type(exc).__name__` in the
   message is the cheapest mitigation short of introducing a logging facility this codebase lacks.
   Carried to the backlog.

---

## 6 · Pending items

- **Review status: two passes.** Pass 1 **BLOCKED** (F1 HIGH) → all nine dispositioned. Pass 2
  **OK WITH FIXES** → G1–G4 dispositioned, count reconciled, Q1/Q3 ruled. Every fix is evidenced by a
  named mutant in §4.1. **Nothing from either pass is left open.**
- **Not yet dispatched:** a confirmation pass over the G-fixes themselves. G1–G4 were fixed after the
  reviewer's last look, so their fixes carry my battery evidence but not an independent read.
- **Backlog carries:** collapse the `_text_attributes()` shim · F9's missing logging facility ·
  `create_from_template` still hand-constructs `SchemaField` with the old `f.get("kind","text")`
  shape (out of fence, flagged by the reviewer) · **the slow-lane wall-clock flake** (§4.0), with its
  reproduction recipe and the recommendation to make the bounds load-tolerant rather than larger.

## 7 · Suggested next task

**Increment 2 — `HLR-MAP.1`:** land the `docs/ARCHITECTURE.md` amendment the feature batch's ARQ
approved and never landed (C-44). Zero source files. The forward-looking `ViewState` rows land as
explicit **commitments**, never as present-tense facts — the ARQ proposal declares
`mapper/views/state.py` *"new this batch"* for a file that does not exist, and landing that verbatim
would trade a C-44 defect for a false map, in the one file the A-family triggers read as an oracle.

---

## 8 · Evidence checklist

| Item | ✓/✗ | Evidence |
|---|---|---|
| Tests / lint pass | ✓ | fast `483 passed, 16 deselected` exit 0; slow `16 passed, 483 deselected` exit 0; 499 collected; ruff 29 = base, 0 in the touched files |
| No secrets in code or output | ✓ | no env, key or token touched. F8 **removed** a leak channel: the reindex net no longer splices an exception `str` (routinely a filesystem path) into operator-facing text |
| No destructive command run without approval | ✓ | no git mutation of any kind this increment; the battery ran on a detached copy |
| File count within cap | ✓ | 1 source file of 4 |
| Counterfactual executed, not asserted | ✓ | **19 mutants**, per-arm junitxml verdicts, §4.1 — including both of the reviewer's own mutants (`M-STO-g`, `M-RR1`) and both of its confirmation mutants (`N1`, `N5`) |
| Mutations restored, proven | ✓ | sha256 back to `49123c83…42ac1458`; the live repo file hashes identically |
| Derived input set, not hand-listed (C-31) | ✓ | `_derived_positions()` walks the dataclasses' own annotations; completeness asserted by `test_tc_p01`; `_EXPECTED_REFUSAL` asserted total over the census |
| Emptiness declared (C-55) | ✓ | `_KEY_POSITIONS` partition asserted, exclusion narrowed to containers (F5); the net's no-op emptiness closed (§1.1); node `B`'s empty ficha found and filled (G1); four mutants exist purely because a neighbouring branch needed its own |
| Negative control present | ✓ | `test_at_p02f` — a clean map records no collision; `M-STO-o` (guard fires unconditionally) reddens exactly that arm |
| Ledger reconciles | ✓ | `499 = 429 − 0 + 70` |
| Independent review attached | ✓ | pass 1 **BLOCKED** (9 findings, §1.2) · pass 2 **OK WITH FIXES** (G1–G4, §1.3) · pass 3 **PASS** (C1–C2 folded, §1.5). All dispositioned, each fix carrying a named mutant |
| Known-flaky lane declared | ⚠ | §4.0 — pre-existing ~10% wall-clock flake in the slow lane, reproduced with positive and negative controls, not caused by this diff, carried to the backlog |
