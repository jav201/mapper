# Increment 003 — `HLR-R03` field-type integrity (S-02), plus A-2, A-3 and A-9

| Field | Value |
|---|---|
| Batch | `2026-08-26-repair-batch` |
| Increment | `003` |
| Lane | not forked · owns `mapper/store.py`, `mapper/model.py`, `mapper/app.py` |
| Requirement(s) | `HLR-R03` **as amended by A-7** · `LLR-R03.1`, `LLR-R03.2`, `LLR-R03.3`, `LLR-R03.4`, `LLR-R03.5` · `LLR-R01.5` *(A-2)* · `LLR-R02.1` *(A-3, the deferred member)* |
| Acceptance | `AT-R06`, `AT-R07`, `AT-R07b`, `AT-R07c`, `AT-R08`, `AT-R09`, `AT-R15`, `AT-R17` · white-box `TC-R15` through `TC-R21`, `TC-R27`, `TC-R28`, `TC-R33`, `TC-R34`, `TC-R35` · plus increment 1's finding `F2` and increment 2b's finding `F3`, folded in |
| Agent | `software-dev` (supervised-incremental-development) |
| Date | 2026-08-27 |
| Revision | **2** — reconciled after the increment-003 code review returned **BLOCKED** on `F1`. See §0 |

---

## 0 · Revision 2 — what the code review changed

The first submission of this increment was reviewed independently and came back **BLOCKED**:
one HIGH (`F1`), four MEDIUM, six LOW. `increment-003-review.md` is that verdict, kept
unedited as the record of what was found. This revision is the response, and **every number
in §4 below is from the re-run battery over the fixed tree**, not carried over.

| Cond. | What it demanded | How it was discharged |
|---|---|---|
| **C1** (HIGH) | `resolve_document`'s walk is dead computation and `TC-R22` cannot fail; resolve it and make the gate reddenable, **with a battery arm that reddens it** | **Fix A.** The walk is *deleted*, not merely de-recursed. `TC-R35` counts `parent_of` calls and asserts **zero** — the declared subject is now in the expression. Arm **M12** reintroduces the fold and reddens `TC-R35` alone (§4) |
| **C3** | `markup=False` is the entire markup defense at both new sinks and no node pins it | Captured and asserted at **both** sinks independently; arms **M19** and **M20** each drop one and redden one node |
| **C4** | Risk 2 / pending item 2 misdescribe `TC-R15`'s residual hole | Corrected in §5 and §6 |
| **C5** | `TC-R22`/`TC-R23` collide with the ids increment 4 owns | Renumbered to `TC-R33`/`TC-R34`; `TC-R33` **relabelled a regression pin**, per C-40's corollary, since the walk it certified is gone |
| C2 | `F2`'s four sibling malformed shapes | **Declared, not guarded** — §6 item 7. Widening the guard is `F-M5`'s repair, which is fenced out of this batch, so a partial widening here would half-fix a defect another batch owns |
| C6 | the LOW nits `F6`–`F10`; hand `F11` to `security-reviewer` | **Partially applied, itemised in §2.** `F6` and `F10` applied; **`F7`, `F8` and `F9` deliberately NOT applied.** `F11` is carried to the whole-branch security pass |

**Two consequences the review anticipated and this revision carries out.** Fix A removes the
hazard that `Risk 4` and `pending item 1` described — a guard whose only regression mode was
a hang — so both are **deleted rather than carried**, exactly as the review's §4 note
instructed. And the battery was **re-run in full** rather than patched: the earlier 18-arm
run measured a tree that no longer exists, and is retained as
`mutation-battery-inc3-v1-prefix.txt` for provenance only. **It is not this increment's
evidence and no figure below comes from it.**

---

## 1 · What changed

**A sidecar field the loader cannot read as text now counts as MISSING and says so in
Spanish, instead of loading clean and quietly inflating the coverage figure the operator
plans against.** `D: 20260826` was the reported defect: it loaded as an `int`,
`missing_required` then raised `AttributeError`, `search_hits` raised `TypeError`, and
`coverage()` answered `(2, 2)` — counting the unreadable field as documented.

Four carried obligations close in the same increment, and none of them opened a file this
increment did not already own:

| Carry | Origin | Closed by |
|---|---|---|
| **A-2** the store's write side is as strict as its read side | increment 1, finding `F1` | `MapStore.save` refuses a cyclic graph **before writing anything** |
| **A-3** `Graph.resolve_document` no longer recurses | increment 1 `F5`, increment 2b pending 1 | the parent walk is **deleted** — review `F1` established it was a no-op (rev 2); the deferral record **deleted**, not emptied (D12) |
| **F2** `LLR-R01.4`'s sink-class breadth is uncertified | increment 1, finding `F2` | `TC-R09b` parametrises the home sink over five exception types |
| **F3** the factory node is a direct call, not a composed screen | increment 2b, finding `F3` | `AT-R16b` drives the composed `FactoryScreen` at depth 5000 |

### The two findings this increment produced itself

**A-9 — a predicate duplicated structurally, and the duplicate disagreed.**
`Ficha.required_coverage` re-derived "what is missing" with a bare truthiness test, while
`Ficha.missing_required`'s own docstring calls itself *"the single owner of what is
missing"*. The two agreed on every input **except a whitespace-only value**: the worklist
called it missing, the coverage figure counted it documented. That is precisely the quiet
inflation US-R03 exists to stop, sitting inside the function whose docstring claims to
prevent it. `required_coverage` now delegates.

This is **C-50's structural rider** in the field: *no assertion over output could have
caught it*, because on every other input the two expressions are the same set counted from
opposite ends. Restore the duplication and every behavioural test stays green — except one,
and the battery pinpointed exactly which (arm M8, §4).

**The `LLR-R03.4` coverage hole — a requirement whose notice could be disabled with zero
reddening.** Every assertion this increment first wrote observed `graph.load_warnings`,
which is **the model**. The battery's app-layer arm disabled `_notice_load_warnings`
entirely and **reddened nothing**: not one node drove the shipped surface. A story whose
promise is *"the operator is told"* was covered by a list on an object.

This is **C-40 limb 1** exactly — the declared subject (the operator being told) never
appeared in any predicate's expression — and it was found by *mutation*, not by review.
Three nodes now close it: `TC-R20` (the map screen), `TC-R20b` (the discriminating
negative — a well-formed map produces no such notice), `TC-R20c` (the sala, which loads
every map on mount).

### The mechanism

- **The text-attribute set is DERIVED from the model** (`A-7`). `_text_attributes()` reads
  `Ficha.__dataclass_fields__` and returns every attribute annotated `str`. `state` is in
  that set even though `search_hits` does not join it — and arm M4 shows why that matters
  (§4).
- **Scalars coerce; containers are REFUSED** (D3). `str({})` is `"{}"`, a truthy string, so
  coercing a container would leave `coverage()` counting the malformed field as documented
  and the miscount would survive its own fix. A container becomes `""` and is recorded.
- **`None` becomes `""`**, which is the realistic hand-edited shape: a bare `title:` key is
  what YAML gives you.
- **`Graph.load_warnings`** carries one Spanish entry per malformed field,
  `campo ilegible: <node_id>.<key>`, surfaced at **both** sinks through `darkside.plain()`
  because node ids and keys both come out of a file.
- **The map still loads** (`LLR-R03.5`). A non-`dict` `fields` block does not deny the map —
  that is defect `F-M5`'s shape, which this batch refuses to reproduce.

---

## 2 · Files modified

**The budget counts SOURCE files only. Tests are not capped.**

| File | Kind | Change |
|---|---|---|
| `mapper/store.py` | source | `_text_attributes()` derived from `Ficha`; `_coerce_field()` coerces scalars and refuses containers; the non-`dict` `fields` guard; `MapStore.save` refuses a cyclic graph before writing (A-2) |
| `mapper/model.py` | source | `Graph.load_warnings` field; `Ficha.required_coverage` delegates to `missing_required` (A-9); `Graph.resolve_document`'s parent walk **deleted** (A-3, as resolved by review `F1`) |
| `mapper/app.py` | source | `MapScreen._notice_load_warnings`; the `HomeScreen` load-warning notice; `markup=False` at both sinks (`F3`) |
| `tests/test_repair_fields.py` | test | **new**, 49 nodes |
| `tests/test_repair_cycles.py` | test | +5 nodes — `TC-R09b`, increment 1's `F2` |
| `tests/test_repair_depth.py` | test | `AT-R16b` added (+1); the A-3 deferral record **deleted** (−1); the widened-derivation node renamed in place |

**Revision 2 opened no file this increment did not already own, and the source count is
unchanged at 3.** Where each fix landed, stated precisely because the byte-level claims in §4
depend on it:

| Fix | File | Nature of the change |
|---|---|---|
| `F1` / C1 | `mapper/model.py` | the parent walk **deleted** from `resolve_document`; the docstring rewritten to say the absence *is* the repair |
| `F3` / C3 | `tests/test_repair_fields.py` | `markup=False` was **already** passed at both `app.py` sinks — the defect was that **no node asserted it**. The assertion is added at both. `app.py`'s bytes are unchanged, and its sha256 is identical across both battery runs, which is the evidence for that claim |
| `F5` / C5 | `tests/test_repair_fields.py` | `TC-R22`→`TC-R33`, `TC-R23`→`TC-R34`; `TC-R33` relabelled a **regression pin** |
| C1 (new node) | `tests/test_repair_fields.py` | `TC-R35`, the walk-count gate, with its own positive control |
| `F10` | `mapper/store.py` | spelling only — net **−2 bytes**, no value changed |

**Every LOW nit, and its disposition** — itemised because re-gate finding `G5` observed that
"§2 says which" was a claim §2 did not actually keep:

| Nit | Applied? | Where / why |
|---|---|---|
| `F6` `AT-R15`'s docstring named a diamond; the fixture builds a fork | **yes** | `tests/test_repair_fields.py:469-477`, and deliberately wider than suggested: it explains why the fork is the shape arm `M18` needs, and cross-references `AT-R03b` |
| `F10` two spelling nits | **yes** | `mapper/store.py`, net **−2 bytes**, no value changed |
| `F7` `_text_attributes()` recomputed once per node | **no** | `mapper/store.py:226`. Cosmetic; hoisting changes no value |
| `F8` `TC-R16b` asserts the standard library; no node drives a real `datetime` | **no** | `tests/test_repair_fields.py:112-113`; `store.py`'s `datetime` branch stays undriven. A real gap, but a test-coverage one, and it is filed rather than rushed |
| `F9` `str` unreachable in `("str", str)` | **no** | `mapper/store.py:31`. Cosmetic |

**The three declines are one decision, and it is about evidence, not effort.** All three are
cosmetic or additive, and `F7`/`F9` would have moved `store.py` *after* its eight battery arms
had run — buying a full re-run for zero behavioural change. The re-gate then supplied the
corroboration that decision was resting on: **all eight `store.py` arm RED counts are
identical in the v1 and v2 transcripts** (28·13·3·10·8·1·8·2·1·20), which is execution-level
proof that the `F10` change was behaviourally inert — stronger evidence than this packet's own
"net −2 bytes" argument, and a cross-check the packet could have made for itself. All three
are carried to the backlog with their line addresses.

| Count | Value |
|---|---|
| **SOURCE files** | **3** — within the ≤4 budget |
| Test files | 3 (uncapped) |
| Doc files | 1 — this packet (outside the count) |

**Why three and not fewer.** They are exactly the set §5 of the requirements assigns to
increment 3. A-2 lands in `store.py`, A-3 and A-9 in `model.py`, the notices in `app.py` —
**no file was opened in order to close a carry.** That is the test the carries had to pass
to be closed here rather than deferred again.

**What was NOT touched, and why.**

- ✓ **Frozen interfaces untouched.** `IRenderer.render` and `Canvas` are not in this diff;
  none of the three files imports either.
- `mapper/views/**`, `mapper/widgets/rail.py`, `mapper/screens/factory.py`, `mapper/mermaid.py`
  — increments 1, 2 and 2b's set. `git status --porcelain` shows this session modified none
  of them.
- `prototypes/**` is untracked **by design and never staged**.

---

## 3 · How to test

```bash
cd C:/Users/jjgh8/Github/mapper

# the gate run — BOTH lanes; the slow lane is where AT-R17 and AT-R16b live
PYTHONUTF8=1 python -m pytest -q -p no:randomly -o addopts=

# the default (fast) lane only
PYTHONUTF8=1 python -m pytest -q -p no:randomly

# this increment alone, per node
PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_repair_fields.py \
    -p no:randomly -o addopts= -v

# the files this increment's changes are consumed by
PYTHONUTF8=1 python -m pytest tests/test_model.py tests/test_inspector.py \
    tests/test_factory.py tests/test_coverage.py -p no:randomly

# lint — the gate metric is mapper/ + tests/, never a bare `ruff check .` (D13)
python -m ruff check mapper tests
```

---

## 4 · Test results

### The two lanes

| Lane | Command | Collected | Result | Wall clock |
|---|---|---|---|---|
| **default (fast)** | `pytest -q -p no:randomly` | **394 selected, 16 deselected** | **394 passed** | ~70 s |
| both | `... -o addopts=` | **410** | **410 passed, exit 0** | **111.32 s** |

Ruff over the gate metric `mapper tests`: **29 before, 29 after** — the pre-existing figure
recorded in decision D13. A bare `ruff check .` reads 57; the other 28 are all in untracked
`prototypes/`, which is never staged.

### Signed-balance test ledger

`post = base − D + A` → **`410 = 356 − 1 + 55`** ✓ reconciled against `--collect-only`, not
against intent.

- base **356**, the tree state increment 2b handed over.
- **D = 1**, with its named successor: `test_tc_r29_the_deferral_record_is_not_stale` was
  **deleted, not emptied** (decision D12). Closing A-3 made `DEFERRED_BY_AMENDMENT_A3`
  empty, and `deferred <= census` is true for *every* census once the left side is empty —
  the staleness guard would have survived as a check that cannot fail. Its assertion was
  ported into the stronger form (`census == set()`, subtracting nothing) in the same commit,
  and that node was renamed in place to say what it now asserts.
- **A = 55.** `tests/test_repair_fields.py` 0 → **49**; `tests/test_repair_cycles.py` 20 → 25
  (`TC-R09b`, five exception types); `tests/test_repair_depth.py` +1 (`AT-R16b`), net 91.
- The 49th node in `test_repair_fields.py` is **`TC-R35`, added in revision 2** as `F1`'s
  fix. `TC-R22`/`TC-R23` were **renumbered** to `TC-R33`/`TC-R34` (`F5`/C5), which moves no
  count. Verified per file against `--collect-only`: 49 / 25 / 91.
- No test was skipped or xfailed.

### RED counterfactual — executed, not predicted

**20 arms · 0 inert · 0 failed restores · 138 RED node-verdicts**, plus a twenty-first arm
(`M21`) run at the re-gate against the `G1` fix — **143 RED across 21 arms**. One verdict **per
resolved node id**; the process exit code is never used as a verdict (C-40 rider). Baseline
and post-battery runs both resolved **410 of 410, all passed**. Every arm ran under
`PYTHONDONTWRITEBYTECODE=1` with `__pycache__` purged (C-46), and every arm's files were
restored with **sha256 returning to the pre-mutation value**.

Transcript: `03-increments/mutation-battery-inc3.txt` — started 05:57:11, finished 06:24:44
on 2026-08-27, **over the tree as fixed for the review**, whose three final hashes are the
three files' current on-disk hashes (§4, byte-scan).

| Arm | Kind | File | RED | What it proves |
|---|---|---|---:|---|
| M1 | deletion | `store.py` | **28** | the coercion itself |
| **M2** | **plausible-weaker** | `store.py` | **13** | `str(v)` for every value **including containers** — the scalar rows stay GREEN; only the container discrimination is lost |
| **M3** | **plausible-weaker** | `store.py` | **3** | `str(v) if v else ""` — the falsy trap; reddens exactly the `0` and `False` rows |
| **M4** | **plausible-weaker** | `store.py` | **10** | the derived set hand-listed as *"the attributes that break today"*, `state` omitted |
| M5 | deletion | `store.py` | **8** | the malformed-field warning is recorded at all |
| M6 | deletion | `store.py` | **1** | `LLR-R03.5`'s non-`dict` `fields` guard |
| M7 | plausible-weaker | `store.py` | **8** | the warning names **both** coordinates, not just that something broke |
| **M8** | **plausible-weaker** | `model.py` | **1** | **A-9 reverted** — bare truthiness in `required_coverage` |
| M9 | plausible-weaker | `model.py` | **29** | count every required field as missing — passes `AT-R07` and destroys the figure |
| M10 | deletion | `model.py` | **5** | A-3 reverted to the shipped recursion |
| **M11** | **plausible-weaker** | `model.py` | **3** | **raise the recursion limit instead of removing recursion** |
| **M12** | **plausible-weaker** | `model.py` | **1** | **`F1`'s arm** — reintroduce the deleted parent-chain fold. Behaviour-preserving on every graph, so only a call-count gate can see it |
| **M13** | **deletion** | `app.py` | **1** | the map-screen notice — **the arm that found the hole** |
| M14 | deletion | `app.py` | **1** | the sala notice |
| M15 | plausible-weaker | `app.py` | **1** | the notice fires but **names nothing** |
| M16 | deletion | `store.py` | **2** | the save refusal itself (A-2) |
| **M17** | **plausible-weaker** | `store.py` | **1** | **refuse AFTER writing** — the poison pill is created anyway |
| **M18** | **plausible-weaker** | `store.py` | **20** | a **false** refusal (C-53) |
| **M19** | **deletion** | `app.py` | **1** | **`F3`'s arm** — drop `markup=False` at the map-screen sink; the whole C-17 defense over file-derived text |
| **M20** | **deletion** | `app.py` | **1** | **`F3`'s arm** — the same defense at the sala sink, dropped independently |
| **M21** | **deletion** | `app.py` | **5** | **`G1`'s arm, added at the re-gate** — drop `markup=False` at the **third** sink, `HomeScreen.load_or_notice`'s load-FAILURE branch. Reddens all five parametrised values of `TC-R09b` and nothing else. **Before the fix this arm measured 0 RED** |

Every mutation's application was proven by the touched file's **hash moving off its pristine
value** — not by a substring check, which a replacement sharing its first line with the
original would pass. Mutations are described here by position and operation rather than
pasted verbatim, per C-56: this packet is corpus input to the same scanners as the source.

#### The five readings that matter

**1 · M12 — the arm that exists because a reviewer, not a test, found the defect.** `F1`
established that A-3's first fix — replacing the shipped recursion with an *iterative* fold —
was **equally dead**: `documents` is graph-level, so every level of the walk rebuilt the same
mapping and returned what it started with. An implementation with the walk deleted is
indistinguishable from one that keeps it **over every graph**, which the increment's own
equivalence oracle confirmed as agreement across 173 comparisons — the strongest possible
evidence that the node could not fail.

That is C-40 limb 1 in its purest form, and it is *also* the shape the flow's own §Artifact-homes
rider warns about: **a behaviour-preserving computation cannot be separated from its absence by
any assertion over output.** The discharge is not a better output assertion; it is to change
what is observed. `TC-R35` counts calls to `Graph.parent_of` and asserts **zero**, with a
positive control first proving the counter can count — so an absence is admissible (C-55's
rider). Arm M12 reintroduces the fold and reddens exactly that node:

| Node | Verdict under M12 |
|---|---|
| `test_tc_r35_resolve_document_does_not_walk_the_parent_chain` | **RED** |
| every other node in the suite, 409 of them | GREEN |

A blast radius of exactly one is the correct size here: the mutation changes no value any
other node can observe, which is the finding.

**2 · M11 — the depth acceptance does NOT catch a recursion-limit raise.** This is the arm
the requirements predicted in §4 (*"green to 500, dead at 5000, and it moves the crash
rather than fixing it"*). With the limit raised to 6000 inside `resolve_document`:

| Node | Verdict under M11 |
|---|---|
| `test_at_r17_resolve_document_survives_a_depth_5000_chain` | **GREEN** — the limit-raise rescues it |
| `test_at_r16b_the_factory_screen_survives_a_depth_5000_map_composed` | **GREEN** — likewise |
| `test_tc_r29_no_recursive_graph_traversal_anywhere_in_mapper` | **RED** — the AST derivation |
| `test_tc_r34_a_cyclic_parent_chain_is_still_answered` | **RED** — the cycle |
| `test_tc_r35_resolve_document_does_not_walk_the_parent_chain` | **RED** — *new in rev 2* |

**Had A-3's acceptance rested on its depth-5000 nodes alone, this batch would have shipped a
recursion-limit raise as a fix.** What catches it is the AST derivation increment 2b built,
the cycle node, and — since revision 2 — the walk-count gate; **none of the three is a depth
test.** Increment 2b recorded the same shape for the rail and the factory; this is its third
instance, and the first where the depth node was the *only* thing a reader would have
expected to catch it. Note the interaction with reading 1: `TC-R35` was added to close `F1`
and it independently strengthened this arm from 2 RED to 3, which is the argument for
preferring a gate over a pin wherever one can be written.

**3 · M4 — `state` is consumed after all, and by another batch's tests.** The A-7 amendment
justified deriving the set by saying `state` is joined by *no consumer*. That is true of
`search_hits` and **false of the application**: hand-listing the set to the attributes that
break today reddens `tests/test_inspector.py::test_at_n01b_state_persists_for_every_value`
across all four of its values, plus four `layered` byte-identity goldens, plus `TC-R15` and
`AT-R07c`. The mechanism is that an attribute outside `_text_attributes()` is never passed
to the `Ficha` constructor at all, so it silently reverts to its default and **state
persistence — a shipped feature owned by another requirement — breaks.**

So the derived set is load-bearing for existing behaviour, not only for this increment's own
acceptance. This is trigger **B1's reverse census confirmed by execution** rather than by
grep, and it makes the case for A-7 stronger than the amendment that argued it.

**4 · M17 — only the discriminating negative catches a refusal that writes first.** Moving
the cycle check to *after* the two `_atomic_write` calls leaves
`test_tc_r27_save_refuses_a_cyclic_graph_with_the_load_message` **GREEN** — it raises
`MapStoreError` with the right message — while the poison pill is created anyway. Exactly
one node reddens: `test_tc_r28_the_refused_save_leaves_no_file_behind`, which asserts the
file that must **not** exist. A refusal that raises after writing is the defect A-2 exists to
repair, and "it raised" is not evidence against it.

**5 · M18 — a false refusal costs 20 nodes.** Widening the cycle test to flag any node with
more than one child refuses legitimate maps, and reddens `AT-R15` together with nineteen
nodes across `test_rail.py`, `test_app.py`, `test_worklist_safety.py` and the rail's
byte-identity goldens. C-53 prices a false failure as high as passing wrong work; here it is
measured at twenty nodes, none of which is a cycle test.

#### The arms that reddened exactly one node

Seven arms are single-node, and each is a deliberate design point rather than thin coverage:

- **M8** reddens only `test_coverage_never_counts_an_unreadable_field_as_documented` at its
  whitespace-only row. That row **is** A-9: it is the single input class on which the two
  predicates disagreed, so a one-node blast radius is the correct size of the defect.
- **M13** and **M14** redden `TC-R20` and `TC-R20c` respectively — one sink each, which is
  what makes them independent guards rather than one guard counted twice.
- **M15** reddens `TC-R20` while the notice still fires, proving the node asserts the
  message's **content** through the surface and not merely that something was notified.
- **M6** reddens `TC-R18` alone — `LLR-R03.5`'s promise that a malformed field never denies
  the map.
- **M12** reddens `TC-R35` alone, for the reason given in reading 1: the mutation is
  behaviour-preserving, so one node is the whole population that *can* see it.
- **M19** and **M20** redden `TC-R20` and `TC-R20c` respectively — the same one-sink-each
  independence as M13/M14, and deliberately so: the two `notify` calls are separate call
  sites, and a single arm covering both would not prove they are independently defended.

#### What revision 2 removed from this section, and why

The first submission carried a subsection here titled *"the arm whose failure mode is a HANG"*.
It described `M12`-as-then-defined — deleting `resolve_document`'s `seen` set — producing
**0 RED in the full suite** and surfacing only as a 15 s timeout in a bounded solo run. It
concluded, correctly, that the guard's only regression mode was a hang: **CI would not fail,
it would stop.** That was carried as Risk 4 and pending item 1.

**Fix A dissolves the hazard rather than mitigating it.** With the parent walk deleted there
is no chain to re-visit, so there is no `seen` set to guard and no hang to guard against.
The review's own §4 note instructed that Risk 4 and pending item 1 be **deleted, not
carried**, and they are. The lesson is kept in the post-mortem, because the *general* shape —
a guard whose regression mode is a hang is a guard CI cannot enforce — outlives this
particular guard, and increment 2b's rail iteration-count pin is the pattern that answers it.

### Load-bearing emptiness — C-55

| Field | Value |
|---|---|
| Does any claim rest on the tree holding NO instance of some case? | **Yes, two.** `test_tc_r21_a_well_formed_map_records_no_warnings` asserts `load_warnings == []`, and `TC-R20b` asserts no notice is produced |
| Why the absence is not vacuous | both are **discriminating negatives with a positive twin**: `TC-R19` asserts the same list is non-empty and exactly right for a malformed map, and `TC-R20` asserts the notice fires. Arms M5 and M7 redden the positive twin; M13 reddens `TC-R20`. A loader that warned about everything reddens `TC-R21`; one that warned about nothing reddens `TC-R19` |
| Positive control for every probe returning an ABSENCE | `test_tc_r28`'s "no file exists" is paired with `AT-R15`, which requires the same two paths to **exist** after a well-formed save — so the probe that reports absence is demonstrated able to report presence |
| Conjunctive criterion, one mutation per conjunct | `HLR-R03` is *coerces text* **and** *does not count the unreadable as documented*. M1/M3 mutate the first; M2/M8/M9 mutate the second |
| Synthetic instance of the case the tree lacks | `TC-R18` builds a non-`dict` `fields` block, and `TC-R34` builds a cyclic parent chain — neither is producible by `_build_sidecar`, both are producible by a human editing `_nodos.yml` |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| **B1** symbols asserted by **other** tests | `grep -rl` for `load_warnings`, `_text_attributes`, `_coerce_field`, `required_coverage`, `missing_required`, `resolve_document`, `search_hits`, `coverage` across `tests/` | **FIRED.** `required_coverage` and `search_hits` → `tests/test_model.py`; `missing_required` → `tests/test_inspector.py`; `resolve_document` → `tests/test_factory.py`. All green, and **confirmed by execution**: arm M4 reddened `test_inspector.py` and arm M18 reddened `test_rail.py`, `test_app.py`, `test_worklist_safety.py` |
| **B4** artifact consumed downstream | `grep -rln` across `mapper/` | **FIRED.** `required_coverage` is consumed by `mapper/screens/coverage.py` and `mapper/widgets/inspector.py`; `resolve_document` by `mapper/screens/factory.py`; `load_warnings` by `app.py`. **A-9 changes what all three of those surfaces report for a whitespace-only value** — deliberately, and in the direction of agreeing with the worklist |
| B2 file moved on disk | `git status --porcelain \| grep ^R` | did not fire — no renames |
| B3 byte-identical golden captures this source | `ls tests/goldens` | did not fire — no such directory. The rail and `layered` digests live as sha256 constants inside `tests/test_repair_depth.py`, and arms M4 and M18 both reddened them |
| A3 interface consumed by another module changed | signatures of `load`, `save`, `coverage`, `missing_required`, `required_coverage`, `resolve_document` | **empty** — `required_coverage`'s body changed, its signature did not |

### Byte-scan — every file this increment touched

Executed after the battery, so these are the bytes that will be committed.

| File | Bytes | BOM | bare CR | TAB | ESC | other control bytes | UTF-8 | endings | trailing-ws lines |
|---|---:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| `mapper/store.py` | 16 454 | ✗ | 0 | 0 | 0 | none | ✓ | CRLF | 0 |
| `mapper/model.py` | 9 223 | ✗ | 0 | 0 | 0 | none | ✓ | CRLF | 0 |
| `mapper/app.py` | 80 779 | ✗ | 0 | 0 | 0 | none | ✓ | CRLF | 0 |
| `tests/test_repair_fields.py` | 25 378 | ✗ | 0 | 0 | 0 | none | ✓ | LF | 0 |
| `tests/test_repair_cycles.py` | 16 519 | ✗ | 0 | 0 | 0 | none | ✓ | CRLF | 0 |
| `tests/test_repair_depth.py` | 69 731 | ✗ | 0 | 0 | 0 | none | ✓ | CRLF | 0 |

sha256 of the three source files: `1b1b9e2b…c4e84707`, `3d39a861…c4468688`,
`fae8e89d…592af7bf` — **identical to the three digests the revision-2 battery restored to**
(transcript, final block), so the scanned bytes and the measured bytes are the same bytes.

**The trailing-whitespace column is measured correctly here**, unlike increment 2b's probe:
`\r` is stripped *before* splitting on `\n`, so a pure-CRLF file is not reported as having
one trailing-whitespace line per line. Increment 2b recorded that its own scanner reported
this falsehood; the correction is applied rather than re-inherited.

Non-ASCII code points are all intentional — Spanish accented vowels and `¿`/`ñ`, the guillemets
`«»`, `§`, `·`, em dash, ellipsis, `→`, `↩`, `↵`, and the box-drawing and block glyphs the TUI
paints with. **No `U+2028`/`U+2029`, no zero-width, no bidi controls.**

---

## 5 · Risks

1. **A container's content is discarded, not preserved.** An operator who wrote a list into a
   ficha field meant something by it; we replace it with `""` and tell them which field was
   unreadable. Decision D3 chose this over coercion because `str({})` is truthy and would
   have kept the miscount alive through its own fix. The information is lost from the ficha
   but **not** from the operator, who is named the node and the key.
2. **`TC-R15`'s derivation and its own oracle share a predicate.** *(Rewritten in revision 2;
   review finding `F4` measured that the first version of this risk was wrong in both
   directions.)* `TC-R15` **does** assert `derived == expected` by name, and that assertion
   reddens on single-member loss — the "future work" the first submission filed here was
   already shipped. **The actual residual hole is a different shape.** Both sides compute
   membership with the same predicate `f.type in ("str", str)`, so an annotation-form change
   such as `state: str | None` **shrinks both sides simultaneously** and `derived == expected`
   still holds. Only the `len >= 4` floor stands against that, and it stands **only while
   `Ficha` has exactly four `str` attributes**: add a fifth text attribute *and* change one to
   `str | None`, and the node is green with a member silently dropped from the coercion set —
   which per arm M4 means it is never passed to the `Ficha` constructor and reverts to its
   default. This is C-31's shape: an oracle whose input set is derived by the very predicate
   it is meant to certify.
3. **The notice concatenates every warning into one line.** A sidecar with many malformed
   fields produces one long toast. It is bounded by the number of fields, not by input
   length, and every segment is `darkside.plain()`-scrubbed — but it is not paginated.
4. *(Deleted in revision 2.)* The first submission carried a risk here about
   `resolve_document`'s `seen` set being guarded by a node that **hangs rather than reddens**.
   Fix A deletes the parent walk, so there is no chain to re-visit, no `seen` set, and no
   hang. The review's §4 note instructed this be **deleted, not carried**; it is. The general
   lesson — *a guard whose only regression mode is a hang is a guard CI cannot enforce* — is
   kept in the post-mortem, where it applies beyond this one guard. The numbering is left in
   place so the review's references still resolve.
5. **A-9 changes what two other surfaces report.** `mapper/screens/coverage.py` and
   `mapper/widgets/inspector.py` both consume `required_coverage`, so a whitespace-only field
   now reads as missing there too. This is the intended direction — they now agree with the
   worklist — but it is a behavioural change in files this increment does not open, and it is
   asserted only through `test_model.py` and this increment's own coverage node.
7. **`F2` — the non-`dict` guard is hand-bounded to `fields`; four sibling shapes still deny
   the map.** Condition C2, taken as *declare* rather than *widen*. The four shapes the review
   measured are named here in full, because `F2`'s stated purpose for allowing the declare
   option was *"so the next reader inherits the measurement rather than the impression"* — and
   a later batch has no reason to open `increment-003-review.md`:

   | # | Malformed shape | Still denies the map |
   |---|---|---|
   | 1 | a node entry that is a **string** | yes |
   | 2 | a node entry that is a **list** | yes |
   | 3 | the **`nodes` block** itself a list | yes |
   | 4 | `attachments` non-list, or an attachment missing `kind` | yes |

   `LLR-R03.5` promises only that a malformed **`fields`** block does not deny the map, and
   that is what is delivered. **Widening the guard is `F-M5`'s repair, fenced out of this
   batch** (§6 item 6), so guarding one more shape here would half-fix a defect another batch
   owns — and would leave three of the four open regardless.
8. **The save refusal makes `save` fallible where callers may not expect it.**
   `MapStore.save` can now raise `MapStoreError` for a graph the caller built in memory.
   `_ImportPreviewScreen.action_save` is the door A-2 exists for and it is guarded, but any
   future caller that treats `save` as infallible inherits a new raise site.

---

## 6 · Pending items / spec deviations

1. *(Discharged in revision 2, not carried.)* The first submission carried "`TC-R23` guards by
   hanging, not by reddening". Fix A removes the guard and the hazard together — see Risk 4.
   **The suite-level wall-clock bound it proposed is still worth having** and is re-filed as
   item 8 below, where it belongs: as a general CI property, not as this node's mitigation.
2. **`TC-R15`'s derivation and its oracle share a predicate** (Risk 2, as rewritten). To close
   it, assert the floor against the count of *all* `Ficha` fields whose annotation **mentions**
   `str` in any form — a different predicate from the one the derivation uses, which is the
   point. The first submission's version of this item proposed work that was already shipped;
   review finding `F4` measured that and it is corrected here rather than restated.
3. **The A-7 amendment's justification is now known to be partly wrong.** It argued the set
   must be derived because `state` is joined by **no consumer**; arm M4 measured that `state`
   is consumed by the inspector's persistence path and by four `layered` goldens. The
   *conclusion* stands and is stronger than the argument that produced it, but the amendment
   text should be corrected at the batch close so a later reader does not inherit the false
   premise (C-43: a hypothesis is not verified by having been written down).
4. **`-m slow` CI lane still unwired.** Increment 2b's Risk 7. This increment adds two more
   nodes to that lane (`AT-R17`, `AT-R16b`), so the consequence of running only the default
   lane grows: **`AT-R17`, `AT-R16b` and the whole `AT-R16` family stop being tested.**
5. **The `master` goldens still have no checked-in regeneration tool.** Increment 2b pending
   item 6, unchanged.
6. **`F-M5` — one malformed node denying a whole map — remains open** and is deliberately
   out of this batch's fence. `LLR-R03.5` refuses to *reproduce* it; it does not repair it.
7. *(Moved to Risk 7 — nothing is planned here, so it is a risk and not a pending item.
   Re-gate finding `G4`.)*
8. **`layered`'s `KeyError` on a disconnected cyclic component** — increment 2b pending item
   5, still named for increment 2's owner, untouched here.
9. **No suite-level wall-clock bound.** Re-filed from the deleted item 1: nothing in CI fails
   if a future change makes any test hang rather than fail. This increment no longer has a
   node with that failure mode, but the property is worth owning batch-wide.

---

## 7 · Suggested next task

**Increment 4 — `HLR-R04` + `HLR-R05` (S-07 and S-08),** the last two defects, owning
`mapper/app.py`'s `MapScreen.CSS` and `mapper/screens/help.py`. Two source files.

Three things to carry into it:

1. **`AT-R14` is the oracle's own guard and must be written first.** `HelpScreen` is a
   `ModalScreen` with a translucent backdrop, so an unclipped compositor read composites
   `MapScreen`'s keybar through it and counts `m cobertura` as a legend row — **measured, and
   it is the orchestrator's own recorded error.** The oracle must be region-clipped to the
   `HelpScreen` subtree before any `AT-R12` result is believed.
2. **The expected binding set is derived from `keymap.bindings_for(scope)`, never
   hand-listed** (C-31), and `AT-R12`'s plausible-weaker arm is *raise `max-height` to a
   number that fits today's 27* — green now, silently re-broken by the next binding added.
3. **`AT-R10`'s plausible-weaker arm is `width: 1fr` on the rail** — on-screen and disjoint,
   and it steals half the canvas. A layout arm that only deletes the CSS rule does not
   distinguish those.

---

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|
| 1 | ≤ budget source files, or reason declared | ✓ | **3 source files** (`store.py`, `model.py`, `app.py`), §2 — exactly the set §5 of the requirements assigns to increment 3; no file opened to close a carry |
| 2 | Tests written in this same increment | ✓ | `tests/test_repair_fields.py` **new, 49 nodes**; `tests/test_repair_cycles.py` +5; `tests/test_repair_depth.py` +1/−1 |
| 3 | Layer 0 written where the criterion applies | ✓ | `TC-R15` (derivation), `TC-R16`/`TC-R16b` (coercion, 7 nodes), `TC-R17` (containers, 4 nodes), **`TC-R35`** (the A-3 gate — `parent_of` call count, with its own positive control), `TC-R33` and `TC-R33b` (the equivalence pins, **labelled pins not gates** per C-40's corollary), `TC-R34` |
| 4 | RED counterfactual captured **and restored by hash** | ✓ | **20 arms, 0 inert, 0 failed restores, 138 RED node-verdicts**; §4 matrix; every arm's sha256 returned to its pre-mutation value; baseline **and** post-battery both **410/410 passed**; all arms `PYTHONDONTWRITEBYTECODE=1` with `__pycache__` purged. Transcript `03-increments/mutation-battery-inc3.txt` |
| 5 | Reverse census run on every touched symbol | ✓ | §4 census: **B1 fired** (`test_model.py`, `test_inspector.py`, `test_factory.py`) and **confirmed by execution** via arms M4 and M18; **B4 fired** (`screens/coverage.py`, `widgets/inspector.py`, `screens/factory.py`); B2, B3 did not fire, with their probes recorded |
| 6 | `code-reviewer` passed — a HIGH blocks | ⚠ | **Run, and it BLOCKED.** `increment-003-review.md`: one HIGH (`F1`), four MEDIUM, six LOW. All conditions are discharged in §0 and the battery re-run in full over the fixed tree. **This revision is submitted for RE-GATE and is not self-approved** — the ⚠ stands until an independent pass over the post-fix diff returns clean |
| 7 | No file from another lane touched | ✓ | `git status --porcelain`: this session modified `store.py`, `model.py`, `app.py` and the three test files. `views/**`, `rail.py`, `factory.py`, `mermaid.py` carry other increments' work and were read only |
| 8 | Frozen interfaces untouched | ✓ | `IRenderer.render` and `Canvas` are not in this diff; none of the three files imports either |
| 9 | Coverage claims verified **on disk**, not from intent | ✓ | ledger `410 = 356 − 1 + 55` reconciled against `--collect-only` per file (49 / 25 / 91); every node id cited in §4 is copied from the battery transcript, not from the test source |
| 10 | Load-bearing emptiness declared, with its positive control (C-55) | ✓ | §4 C-55 table — two absences (`TC-R21`, `TC-R20b`), each with a positive twin that a mutation reddens; `TC-R28`'s absence paired with `AT-R15`'s presence |
| 11 | Mutation verdicts recorded **per arm**, inert arms named | ✓ | §4 matrix, one row per resolved arm, node ids never exit codes. **`INERT ARMS: none`** and **`FAILED RESTORES: none`** printed by the run itself; M11's and M12's GREEN nodes are named explicitly rather than omitted |
| 12 | Working files reconciled | ✓ | the harness (`battery3.py`), its recovery tool (`recover.py`) and the raw transcript live in the session scratchpad; only the transcript is copied into `03-increments/`. `scratch/` and `out.txt` go to `.gitignore` at the batch close |
| 13 | Harness lives outside the tree it mutates | ✓ | `battery3.py` is under the scratchpad, not in the repo — the structural fix for increment 2b's defects 4 and 5. A `recover.py` pinning the three pristine sha256 values was added so a mid-arm kill is recoverable **without the killed process's memory** |
| 14 | Mutations described by position, not pasted verbatim (C-56) | ✓ | §4 describes each arm by operation and site; no mangled token or dotted id range appears in this packet |
| 15 | The evidence transcript on disk is the one this packet cites | ✓ | **Found broken and repaired at re-gate.** The v2 transcript had been produced (scratchpad, 06:24:44) but **never landed in `03-increments/`**, so the file the packet pointed at was the superseded 18-arm run over a tree that no longer existed. Landed as `mutation-battery-inc3.txt`; the v1 kept as `mutation-battery-inc3-v1-prefix.txt`. Verified by the three final hashes in the transcript matching an **independent** `sha256sum` of the three source files on disk |

---

## 8 · Re-gate disposition (revision 3)

The independent re-gate over revision 2 returned **PASS** — zero HIGH, three MEDIUM, three LOW,
all recommendations (`increment-003-regate.md`). Every one is closed here rather than carried,
because the reviewer's own disposition note asked for `G1` and `G3` before increment 4 opens
`app.py`, and the rest cost a line each.

| # | Sev | Finding | Closed by |
|---|:--:|---|---|
| **G1** | MED | the increment opened **three** new `notify` sinks, not two; the load-failure branch at `app.py:452-457` carried `markup=False` over file-derived text with **no node asserting it**. Measured at 0 RED | `TC-R09b`'s stub now **captures** kwargs instead of discarding them, and asserts `markup is False` after asserting the hit list is non-empty. New arm **`M21`**: **5 RED**, all five parametrised values, nothing else |
| **G2** | MED | `TC-R35`'s docstring claimed a walk *"of any kind"* reddens it; measured false for a walk that inlines the parent lookup | Docstring **narrowed to what the expression asserts** — a walk routed through `Graph.parent_of`. The residual (an inlined `self.edges` scan) is named in the docstring and filed against `TC-R29`'s family |
| **G3** | MED | §4's fast-lane row still read `393 / 16` from the 409-node tree | Corrected to **394 / 16**. `393 + 16 = 409` is what gave it away, and it falsified §0's claim that every §4 number came from the re-run |
| **G4** | LOW | C2's declaration named one of the four measured shapes | All four now tabulated in **Risk 7**, and moved out of §6 since nothing is planned |
| **G5** | LOW | §0 claimed "§2 says which" nits were applied; §2 covered three of five. The requirements' traceability row never recorded the renumbering | §2 now tabulates all five with dispositions (`F6` and `F10` applied, `F7`/`F8`/`F9` not). `01-requirements.md` §6 carries the id-reallocation note and its TC count moves 32 → 38 |
| **G6** | LOW | the superseded transcript described itself as authoritative | A `SUPERSEDED BY` banner heads `mutation-battery-inc3-v1-prefix.txt`, naming its hashes as **pre-fix** and unusable for verifying a restore |

**`G1` is the finding worth carrying into the post-mortem, and not for its size.** This
increment's §1 cites increment 1's `F2` — *a sink-class guard that was correct and unasserted* —
as a **closed** carry, and then added a sibling sink in the same file with the same unasserted
property, which increment 2b's `F3` had already named a second time. Three occurrences, one
mechanism: **a `notify` stub spelled `lambda msg, **kw: ...` silently discards the only thing
defending the sink.** Closing an instance is not closing a class, and the batch has now paid for
that distinction three times.

**What the re-gate gave back that this packet should have derived itself.** All eight `store.py`
arm RED counts are **identical across the v1 and v2 transcripts** (28·13·3·10·8·1·8·2·1·20).
That is execution-level proof the `F10` spelling change was behaviourally inert — strictly
stronger than §2's "net −2 bytes" argument, and it was available to the author the moment both
transcripts sat side by side.
