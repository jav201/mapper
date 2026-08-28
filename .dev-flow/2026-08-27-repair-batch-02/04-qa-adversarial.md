# 04 — Adversarial whole-branch QA pass · `2026-08-27-repair-batch-02`

**Reviewer:** `qa-reviewer`, adversarial merge-gate pass.
**Branch:** `fix/repair-batch-02` · **HEAD** `8675151` · **Base** `d877784` (= `origin/master` = merge-base).
**Date:** 2026-08-27 · **Posture:** hostile to the evidence. Every figure below was re-derived in this
session from its own command output; nothing is copied from the packets.

---

## Verdict — **BLOCKED**

One **HIGH** finding. Five MEDIUM, six LOW. Twelve categories came back clean, including the two
the brief flagged as most suspect (`test_at_p02f`, `test_tc_p06b`) and the whole numeric ledger.

The HIGH is not a crash-on-mount; it is the batch's **central measurement being short by the batch's
own rule**, with a reproduced consumer crash of the same class the batch exists to close. `HLR-STO.1`
as written — *"every position that `_build_sidecar` serialises as text is an instance of `str`"* — is
not met on the merged tree.

**No repo file was edited.** All mutation work ran in a detached copy under
`scratchpad/lab/`; the base ref was read through `git worktree add` to a temp path.
`git status --porcelain` in the main tree is byte-identical before and after this pass
(2 modified, 5 untracked — unchanged).

---

## 1 · Findings

### HIGH-1 — the "derived, complete" 17-position census is short by four positions, and the missed ones reach a live screen as an untyped crash

The batch's §2.1 argument is: *the security lens hand-listed "5 families / 3 raw"; the serialiser
writes a sixth family nobody enumerated (`documents[]`), and field **keys** are raw while only their
values are coerced; the honest unit is **positions (17)**, not families.* That argument is correct and
it stops one step short of its own conclusion.

**`Document.tags` and `Document.inherited` are `dict[str, str]` — the model declares their keys and
values as text — and `_build_sidecar` round-trips both.** They are the structurally identical shape to
`Ficha.fields`, which **is** in the census, hand-added as `fields.key` / `fields.value`.

| Evidence | Location |
|---|---|
| `_build_sidecar` writes `"tags": d.tags` and `"inherited": d.inherited` | `mapper/store.py:238-246` |
| the model declares them text-valued | `mapper/model.py:82-83` — `tags: dict[str, str]`, `inherited: dict[str, str]` |
| the identical shape on `Ficha` **is** covered | `mapper/model.py:32` `fields: dict[str, str]` → `tests/test_repair_store_boundary.py:83` `out = ["node.id", "fields.key", "fields.value"]` |
| `_graph_from_sidecar` passes both through raw | `mapper/store.py` — `tags=d.get("tags", {})`, `inherited=d.get("inherited", {})` |

**Executed probe (branch tree, `PYTHONUTF8=1`):**

```
documents[0].tags VALUE = int          tags={'owner': 12345}      warnings=[]
documents[0].tags KEY = int            tags={7: 'seven'}          warnings=[]
documents[0].tags VALUE = dict         tags={'owner': {'x': 1}}   warnings=[]
documents[0].inherited VALUE = int     inherited={'a': 99}        warnings=[]
documents[0].tags = scalar str         tags='junk'                warnings=[]
documents[0].tags = int                tags=7                     warnings=[]
```

Four text positions (`document.tags.key`, `document.tags.value`, `document.inherited.key`,
`document.inherited.value`) leak a non-`str` past the boundary with **zero** `load_warnings` — plus
`tags`/`inherited` themselves can stop being mappings entirely. The census is **21**, not 17.

**It is the same S-02 / S-11 class, reproduced end-to-end.** `mapper/screens/factory.py:339`:

```python
for key in sorted(set(doc.tags) | set(_TAG_RE.findall(doc.source))):
```

with an `int` tag key:

```
RAISES: TypeError '<' not supported between instances of 'int' and 'str'
```

`factory.py:340-343` then hands `local` / `inherited` to `escape()`, which is an `AttributeError` on a
non-`str`. Same family as the pre-fix `attachment.path` → `search_hits` `TypeError` the batch used to
justify its own existence.

**The exclusion is mentioned once, on a reason that does not hold.** `mapper/store.py:272-274`:
*"`required` and `template` are `bool` and `tags`/`inherited` are dicts by design, so `_text_fields`
leaves them."* — grouping them with the `bool` fields. But `Ficha.fields` is *also* "a dict by design"
and is *not* left; it was hand-added to the census precisely because its keys and values are text. No
requirement, threshold, test, packet or decision-log row records the asymmetry.

**Why HIGH.** The census is this batch's gate. It is presented as derived and complete
(`01-requirements.md:55`, `:124` *"for each of the **17** derived positions… yields **0** non-`str`"*;
`tests/test_repair_store_boundary.py:7-12` *"THE INPUT SET IS DERIVED, NOT HAND-LISTED"*) and it is
neither: `_derived_positions()`' three structural entries and its four-class list are hand-written,
and the hand list is short by the same reasoning the batch used to grow it from 5 families to 17
positions. The batch BLOCKED itself at review pass 1 on F1 for exactly this shape — a threshold clause
ungated across a family — so HIGH is the batch's own standard applied to itself.

**Mitigations, stated so the operator can weigh a downgrade:** the crash is in `FactoryScreen`, not on
«sala» mount, so the batch's ordering argument does not apply to it; and the positions *are* named in a
code comment, so this is an incorrectly-justified exclusion rather than an unnoticed one. It is a
scope-and-evidence HIGH, not a crash-on-mount HIGH.

---

### MEDIUM-1 — `AT-P05` pins five of the six corrections; the test and the packet both say six

- `tests/test_repair_map_truth.py:111-117` — `_CORRECTED_FALSEHOODS` has **5** entries.
- `tests/test_repair_map_truth.py:122` — *"AT-P05 — the six false claims stay corrected."*
- `.dev-flow/2026-08-27-repair-batch-02/03-increments/increment-002.md:83` — *"it certifies that
  **these six corrections** survive"*.

Falsehood #6 (`increment-002.md:25` — `SearchIndex.query`'s consumer column claiming `app`) has no
pin. Mutant **M4** reintroduced it verbatim in a detached copy:

```
M4 applied: falsehood #6 (SearchIndex consumer = app) reintroduced
26 passed in 0.09s          # 0 arms red, whole tree: 36 passed, 498 deselected
```

The finding is not that the pin set is narrow — the file is explicit and correct that it is a
regression pin, not a general truth check. The finding is that **the count is stated as six in two
places and is five**, in the increment whose entire subject is a document asserting things that are
not true against disk.

---

### MEDIUM-2 — `TC-P02`, `TC-P03`, `TC-P04` have no on-disk node

`01-requirements.md:219` maps `LLR-STO.1.1` → `TC-P02`, `TC-P03`, `TC-P04`.

```
$ grep -rn "tc_p02\|tc_p03\|tc_p04" tests/
NO NODES named tc_p02/03/04
```

They exist only as comment banners over `AT-`-named nodes at
`tests/test_repair_store_boundary.py:264`, `:283`, `:324`, `:355`. **Three of the eight declared test
cases have zero addressable nodes** — and they are the three belonging to the requirement this batch
wrote from scratch because it was a phantom. C-18 (*exactly one distinct on-disk node driving the whole
named chain*) is unmet for `LLR-STO.1.1`'s entire test-case column.

Dual-direction audit result:

| Direction | Result |
|---|---|
| requirement id → node | `TC-P01` ✓ · **`TC-P02` ✗** · **`TC-P03` ✗** · **`TC-P04` ✗** · `TC-P05` ✓ · `TC-P06` ✓ · `TC-P07` ✓ · `TC-P08` ✓ · `AT-P01`…`AT-P07` **all ✓**, one distinct driving node each |
| node → requirement id | **no orphans.** Every `test_at_p0*` / `test_tc_p0*` node maps to an id the requirements define (the `b`/`c`/`d`/`f` suffixed nodes are declared sub-variants) |

---

### MEDIUM-3 — three phantom test nodes are cited as evidence, one of them inside the very row that corrects a phantom claim

The brief asked whether any false record of the F4 class remains. **Three do**, and none is in the
suite — `grep -rn "at_p02e\|tc_p19\|tc_p21" tests/` returns nothing, and
`git log --all -S` finds no commit that ever contained them.

| Cited node | Cited at | Role it is given |
|---|---|---|
| `test_at_p02e` | `increment-001.md:97` · `increment-001-code-review.md:651` | **F4's own disposition row** — *"**fixed** — comment corrected; `nodo duplicado:` record; `test_at_p02e`"* |
| `test_tc_p19` | `increment-001-code-review.md:337` | cited as an existing exemplar the fix should copy — *"pin the expected string per family the way `test_tc_p19` does"* |
| `test_tc_p21` | `increment-001-code-review.md:460` | **load-bearing in the reverse-census "verified clean" table** — *"the new coercion adds **no** warning on a well-formed map, which `test_tc_p21` independently pins"* |

The two node-id collision cases actually live inside `test_at_p02d`'s parametrize
(`tests/test_repair_store_boundary.py:471-479`); there is no `p02e`.

`test_tc_p21` is the worst of the three: it is the *sole* cited support for a reverse-census row
being marked clean, and it does not exist. That row's property — no warning on a well-formed map — is
in fact the one LOW-2 shows is carried entirely by `test_repair_fields.py`, so the review reached the
right conclusion by citing a node that was never written.

---

### MEDIUM-4 — `G4` has two limbs, one landed, and the confirmation pass declares `G1`–`G4` fixed

`increment-001-code-review.md:722-723` — the suggested fix, both limbs in one sentence:

> `f"campo ilegible: {owner}.{key}[{i}]"` from an `enumerate`, **and give the node-id owner the raw
> key's `repr` the way `key[{key!r}]` does.**

Limb 1 landed (`mapper/store.py:129`). **Limb 2 did not.** `mapper/store.py:318` still reads:

```python
nid = _coerce_field(graph, "node", "id", raw_nid)
```

— the bare literal, while the field-key position two blocks down does it correctly at `:345`
(`f"key[{key!r}]"`). `tests/test_repair_store_boundary.py:136` bakes the un-attributable form into the
oracle: `"node.id": "campo ilegible: node.id"`.

**Executed — two distinct refused node ids:**

```
G4 limb 2 -- two DISTINCT refused node ids (b'h1', b'h2'):
    campo ilegible: node.id
    campo ilegible: node.id
    nodo duplicado: '' <- b'h2'
```

Two byte-identical records; the operator cannot tell which ids were refused, and the `duplicado` line
names only the second. That is precisely the F7/G4 diagnostic defect, live at the node-id position.

`increment-001-code-review.md:816` — the PASS verdict — states *"`G1`–`G4` are fixed, and each is
gated by a mutant I built."* Neither half holds for G4: half the fix is absent, and the confirmation
pass names mutants for G1 (`N1`), G3 (`N3`/`N4`) and C2 (`N5`) but **none for G2 or G4**. This is the
one place where the independent review's final verdict rests on a claim that is false against disk.

---

### MEDIUM-5 — 13,526 undeclared lines of another batch's artifacts ride on the branch, and `state.json` ends with no record of this batch at all

The brief described the branch as base + uncommitted worktree. It is not: `fix/repair-batch-02`
carries commit `8675151`, on no other branch.

```
$ git show -s --format="%an %ad %s" 8675151
jav201  Thu Aug 27 11:52:55 2026 -0600  docs: land the ui-next-batch-02 PDR artifacts (C-44 discharge)
 14 files: .dev-flow/2026-08-26-ui-next-batch-02/**  (13,343 lines)
     plus: .dev-flow/state.json                       (183 +/-)
```

```
$ grep -rn "8675151\|land the ui-next-batch-02\|C-44 discharge" .dev-flow/2026-08-27-repair-batch-02/
NOT MENTIONED ANYWHERE IN THIS BATCH'S ARTIFACTS

$ grep -c "2026-08-27-repair-batch-02" .dev-flow/state.json
0
```

Nothing in `01-requirements.md` §6, `PLAN.md` §6, `PLAN.md` §9's sixteen decision rows, or any
increment packet declares it. On merge, `master`'s `.dev-flow/state.json` will read:

- `batch_id: "2026-08-26-ui-next-batch-02"` — a batch **REJECTED at PDR and parked**
- `current_station: "PDR"`, `phase_status: "awaiting-gate"`
- `baseline.tests_collected: 429` — stale the moment this merges (the tree collects **534**)
- **no** `mode_history` entry, **no** `decisions_log` entry, **no** `previous_batch` update, and no
  mention anywhere of `2026-08-27-repair-batch-02`

The batch that is being merged leaves no trace in the file its own `AT-P07` reads as an oracle. That is
a C-44-shaped record defect produced by a batch whose third defect *is* C-44.

**The honest half, credited:** `increment-003.md:136-138` states plainly that *"`B3`'s correction was
already committed before this increment (it landed at the feature batch's un-park). This increment
does not create it; it **pins** it."* `AT-P07`'s deliverable is correctly attributed. The undeclared
part is the other 13.3k lines and the batch pointer.

---

### LOW-1 — `increment-001.md` carries two stale node counts that contradict its own mutant table

| Claim | Location | Measured |
|---|---|---|
| `tests/test_repair_store_boundary.py` — "492 lines \| 66 nodes" | `increment-001.md:194` | **600 lines, 70 collected** |
| harness self-guard: "the baseline must resolve exactly **66** arms" | `increment-001.md:275` | the same section's mutant table (`:287-305`) reports every verdict as **`/70`** |

Both cannot describe the final battery. `N5` is reported reddening 17 arms *after* the C2 fix, which is
part of the 70 — so the `66` is stale, not the `70`. Superseded figures are kept deliberately elsewhere
in this batch (`PLAN.md` §7, §8 D-R8) and marked as superseded; these two are not marked.

---

### LOW-2 — no negative control for `campo ilegible` inside the batch's own file; the property is carried entirely by a previous batch's suite

**Mutant M1** — prepend an unconditional `graph.load_warnings.append(f"campo ilegible: {node_id}.{key}")`
to `_coerce_field`, leaving all return behaviour correct. Every clean field now reports itself
unreadable.

```
tests/test_repair_store_boundary.py :  70 passed          # 0 arms red
whole fast lane                     :  32 failed, 485 passed, 17 deselected
```

All 32 red arms are in `tests/test_repair_depth.py` and `tests/test_repair_fields.py`. The arms that
actually catch it are `test_repair_fields.py::test_tc_r21_a_well_formed_map_records_no_warnings` and
`::test_tc_r20b_a_well_formed_map_produces_no_such_notice` — **another batch's suite**, which is exactly
the C2 finding this increment claims to have closed (`increment-001.md:178-180`, *"The file now stands
on its own."*). It stands on its own for the record-*content* direction (N5, 17 arms); it does not for
the false-positive direction. `test_at_p02f` covers only `duplicado`, never `ilegible`.

**Not a hole in the gate** — the suite catches it loudly, and the gate is the suite. The finding is that
the packet's claim is broader than what was measured.

---

### LOW-3 — an undeclared-by-test behaviour change: a missing attachment `kind`/`path` becomes `""` silently

| Ref | Behaviour on `attachments: [{kind: img}]` (no `path`) |
|---|---|
| base `d877784` | `MapStore.load` raises bare `KeyError: 'path'` |
| branch | `Attachment(kind='img', path='', caption='')`, `load_warnings=[]` |

Both executed. The direction is right for S-11 and it *is* declared in prose at the `Attachment(...)`
comment in `mapper/store.py`. But **no arm gates it** — `test_at_p01b` covers absence only for
`schema.kind` and `documents.kind` — and it takes the silent-discard route the batch's own F1 finding
condemns for `_mappings` (*"silent discard is not a report"*). A future edit restoring the direct index
reddens nothing.

---

### LOW-4 — `M-STO-a` count reconciliation

My re-run of the requirement's named `M-STO-a` (drop the ladder call in `_coerce_text_fields`, return
raw values; substitution count asserted = 1) reddens **21** arms; `increment-001.md:287` reports **20**.
Higher, not lower — the arm set is stronger than claimed. Flagged only because this batch's standard is
that every figure be derived, and because a one-arm drift between the packet's battery and a clean
re-run is worth someone's attention before the same harness is reused.

---

### LOW-5 — `M-RR2` names two incompatible mutants inside one document

| Location | Definition | Count |
|---|---|---|
| `increment-001-code-review.md:732` | *"`M-RR2` (my original **drop** mutant)"* — `attachment.{kind,path,caption}` | **3 failed, 145 passed** |
| `increment-001-code-review.md:875` | *"`M-RR2` (refusal returns `"?"`)… it mutates the **refusal value**"* | **all 15** |

Different mutation, different arm set, no note that the designation was reused. `:875`'s version is the
one that matches the author's packet (`increment-001.md:303`, 16/70) and my own re-run. The
consequence is that `:631` — *"the limb is real on the other 12 (see `M-RR2` below)"* — forward-
references evidence that, at the line it points to, reports 3 rather than 15.

---

### LOW-6 — the review quotes itself saying something it never said

`increment-001-code-review.md:918`:

> My re-review flagged this as **"one of us has the wrong count"**; neither of us did.

```
$ grep -rn "one of us has the wrong count" .dev-flow/
(no matches — exit 1)
```

The re-review's actual words at `:732` are *"**3 arms, not the 2 your summary reports**; worth
reconciling against `M-STO-g`'s shape."* A self-quotation of a sentence that was never written, in the
paragraph whose subject is withdrawing a false discrepancy.

Credit where due: the withdrawal itself is honest — the superseded claim is still visible verbatim at
`:732` rather than rewritten, and all three verdicts (BLOCKED `:9` → OK WITH FIXES `:523` → PASS
`:815`) are preserved in place. Only the quotation is invented.

---

## 2 · Reconciled numbers — derived in this session, not copied

| Figure | Claimed | **Measured here** | Command |
|---|---|---|---|
| fast lane | 517 passed / 17 deselected | **517 passed, 17 deselected**, 157.03s, exit 0 | `pytest -q` |
| slow lane | 17 passed / 517 deselected | **17 passed, 517 deselected**, 38.38s, exit 0 | `pytest -q -p no:randomly -o addopts= -m slow` |
| collection (branch) | 534 | **534** | `pytest -q --collect-only -p no:randomly -o addopts=` |
| collection (base `d877784`) | 429 | **429** | same, in the `git worktree` at base |
| `test_repair_store_boundary.py` | 70 | **70** | per-file collect |
| `test_repair_map_truth.py` | 26 | **26** | per-file collect |
| `test_repair_golden_census.py` | 7 | **7** | per-file collect |
| `test_repair_perf_shape.py` | 2 | **2** | per-file collect |
| ledger `534 = 429 + 105` | ✓ | **✓** — 70+26+7+2 = 105 | arithmetic on the above |
| `ruff check mapper/ tests/` (branch) | 29 | **29** | `python -m ruff check mapper/ tests/` |
| `ruff check mapper/ tests/` (base) | 29, unchanged | **29** | same, in the base worktree |
| ruff on the five touched/new files | clean | **All checks passed** | explicit file list |
| `LLR-PERF.1` measurement | 51 nodes, 410 edges, 2.3066s | **51 nodes, 410 edges, 2.3187s** | `pytest tests/test_repair_perf_shape.py -s -m slow` |

**Every ledger figure in the batch reconciles.** No numeric finding.

---

## 3 · Clean categories — what was checked, and what came back clean

### 3.1 · The pre-fix measurement is honest and independently reproducible

I copied the batch's own `tests/test_repair_store_boundary.py` unchanged into a `git worktree` at
`d877784` and ran it against the pre-fix source:

```
43 failed, 27 passed in 7.52s
```

- `test_at_p01` reddens on **exactly 12 of 17** arms — `node.id`, `fields.key`, `attachment.{kind,path,caption}`,
  `schema.{key,label,kind}`, `document.{name,source,path,kind}`. **The "12 of 17 leak" claim stands.**
- `test_at_p03` reddens on **exactly 4** arms — `attachment.{kind,path,caption}`, `document.name`.
  **The "4 untyped leaks (`ProgrammingError` ×3, `TypeError` ×1)" claim stands.**

Premises P-1 and P-3 are confirmed by execution, not citation.

### 3.2 · The requirement-named weaker variants really redden

| Mutant | Packet | **Re-run here** |
|---|---|---|
| `M-STO-a` — drop the ladder call in `_coerce_text_fields` | 20 RED | **21 RED** (see LOW-4) |
| `M-STO-b` — container-rejection branch returns `str(value)`, warning kept | 16 RED | **16 RED — exact** |
| `M-MAP-a` — declare the unbuilt `mapper/views/state.py` as an owned path | 1 RED | **1 RED — exact**, `test_at_p04[views-mapper/views/state.py]` |

### 3.3 · The F1 containment clause is genuinely gated, not vacuous

Two destruction mutants written from scratch, not from the packet's list:

| Mutant | RED arms |
|---|---|
| drop the whole document when any of its text fields is non-`str` | **5** |
| reset the whole ficha to defaults instead of coercing | **4** |

The `(position, "") in live` clause at `tests/test_repair_store_boundary.py:310` does the work claimed
of it. The vacuity F1 identified is closed for containers.

*Residual note, not a finding:* `test_at_p01`'s arms carry **no** containment half — only
`offenders == []`. Under the document-drop mutant the four `test_at_p01[document.*]` arms pass
vacuously and are rescued entirely by their `test_at_p02[document.*]` siblings. The coverage holds; the
per-arm independence does not.

### 3.4 · The operator rider is honoured — no budget, no deadline, no abort

`tests/test_repair_perf_shape.py` asserts only: node count (`:70`, `:85`), the **derived** edge count
(`:72`), root presence (`:73`), non-empty render (`:91`). `elapsed` (`:89`) appears in exactly one
place — inside `print()` at `:92-96`.

Grep for `budget|deadline|abort|timeout|SECONDS|perf_counter|elapsed|max_.*seconds` across the entire
diff (`mapper/`, `docs/`, all four new test files) returns **only** docstring prose and that one
`perf_counter` pair. `mapper/store.py` contains no timing of any kind. **Nothing smuggles a deadline
mechanism in.** `S-18` stays parked.

### 3.5 · The slow-lane flake — SETTLED. The batch's belief is correct; its UNVERIFIED marker can be retired

`PLAN.md:142-145` and `increment-001.md` §4.0 record as **UNVERIFIED BY EITHER PARTY** whether the
flake predates `d877784`. I checked it via `git worktree add` to a temp path — the main tree was never
touched (`git status` byte-identical throughout).

| Condition (base ref `d877784`, zero branch code present) | Result |
|---|---|
| unloaded, 6 sequential runs | **6/6 clean**, 36.58s–42.12s |
| two concurrent base slow lanes | **both clean**, 40.07s / 40.70s |
| under 16 deliberate CPU-load processes, run 1 | **FAILED `test_repair_depth.py::test_at_r16b_the_factory_screen_survives_a_depth_5000_map_composed`**, 84.13s |
| same load, runs 2–3 | passed, 66.80s / 38.24s |

**That is the exact node the batch names, failing at the base ref, with none of this batch's code
present.** The flake predates `d877784`. The batch's argument was sound and is now a measurement; the
backlog carry (make the bounds load-tolerant rather than larger) stands.

### 3.6 · The derived census is complete against `_build_sidecar`'s *scalar* positions

Read `_build_sidecar` (`mapper/store.py:230-262`) against every dataclass in `model.py`:
3 schema + 4 document + 1 `node.id` + 4 ficha + 2 field key/value + 3 attachment = **17** ✓. No
`str | None` or `Optional[str]` text field is missed by `_text_fields`' `spec.type in ("str", str)`
test. `Edge.label` and `Graph.root_id` live in the `.mmd`, not the sidecar — correctly out of scope.
**The gap is the `dict[str, str]` positions only (HIGH-1), not the scalars.**

### 3.7 · C-31 audit — no arm claims a derivation it does not perform, except the one in HIGH-1

Genuinely derived: `_derived_positions()` (walks dataclass annotations) · `_composition_rows()` /
`_declared_paths()` (parses the map's table — **19** owned paths → 19 arms, verified by printing them)
· `_census()` / `_sizes()` (`ast`-parses `MASTER_LEGACY_DIGESTS` and `GOLDEN_SIZES`).

Hand-listed **and declared as constructed cases**, correctly: `_MALFORMED_SHAPES`,
`_MALFORMED_ITEM_LISTS`, `_COLLISIONS`, `_CORRECTED_FALSEHOODS`. These are the shapes the value census
structurally cannot reach; claiming derivation for them would be the false record, and the batch does
not.

The one exception is HIGH-1: `_derived_positions()`' three structural entries and its four-class list
are hand-written, and that hand list is short.

### 3.8 · `_EXPECTED_REFUSAL` — the brief's suspicion, answered

It is a hand-written **expectation** map, not a hand-listed **input set**. C-31 governs input sets, so
it is not the smuggled oracle the brief suspected, and the totality assertion at
`tests/test_repair_store_boundary.py:250` makes a newly-derived position fail loudly rather than skip.

**Its honest limit, which the file does not overstate:** its 17 values encode what the implementation
emits, so a *wrong-but-total* map would pass iff the implementation matched it. It is a
change-detector — which is precisely what earns it the N5 catch (17 arms) — not a specification oracle.
The requirement only mandates *"appends a `campo ilegible:` record"*; the coordinates are the file's own
strengthening. Sound as built.

### 3.9 · `test_at_p02f` and `test_tc_p01c` are not vacuous

- `test_at_p02f` does exactly the work claimed: an unconditionally-firing collision guard reddens it
  and nothing else. Its scope is `duplicado` only — see LOW-2 for what that leaves uncovered.
- `test_tc_p01c` is a **harness self-guard**, correctly labelled. It asserts the `_KEY_POSITIONS`
  exclusion is container-specific (a `dict` is unhashable and cannot occupy a mapping key), that every
  other position genuinely *can* be poisoned, that the two sets partition the census, and that
  `_EXPECTED_REFUSAL` is total. It cannot redden on a product mutation and does not claim to.

### 3.10 · `test_tc_p06b` is exactly what it says it is

It pins the literal `12` and is labelled a regression pin, with the real gate above it in
`test_tc_p06`: `len(census) == len(renderers) × len(sizes)`, **plus** every grid cell asserted present
(a product can match by coincidence while one renderer is double-pinned). Not a hidden literal.
`test_tc_p06c`'s `distinct == 10` is likewise a declared observation, with its rationale recorded.

### 3.11 · The batch's own out-of-fence declarations are accurate

- **`documento duplicado` fires without coercion** — confirmed. `documents` is a YAML **list**, so two
  plainly identical names coexist. Correctly declared out-of-fence at the call site, at `PLAN.md` D-R10,
  and at `increment-001.md` risk 6.
- **`nodo duplicado` / `campo duplicado` fire only on coercion or refusal collisions** — confirmed. YAML
  cannot carry two identical string keys in one mapping, so no non-coercion case exists. Correctly
  claimed in-fence.
- **The unprompted negative control** (`test_at_p02f`) is declared at `PLAN.md` D-R12.

Both self-declared out-of-fence additions check out. The undeclared ones are MEDIUM-4 and LOW-3.

### 3.12 · Working-tree integrity

`git status --porcelain` in `C:\Users\jjgh8\Github\mapper` before and after this pass:

```
 M docs/ARCHITECTURE.md
 M mapper/store.py
?? .dev-flow/2026-08-27-repair-batch-02/
?? tests/test_repair_golden_census.py
?? tests/test_repair_map_truth.py
?? tests/test_repair_perf_shape.py
?? tests/test_repair_store_boundary.py
```

Byte-identical. No `checkout`, `stash`, `reset`, `commit` or any other mutating git operation was run
in the main tree. The base ref was read through `git worktree add` to a scratchpad path; all mutation
work ran on a detached `cp -r` copy with `PYTHONDONTWRITEBYTECODE=1` and every substitution guarded by
an asserted count of exactly 1.

---

## 4 · What blocks, and what does not

**Blocks (return to operator):**

1. **HIGH-1** — extend the census to `document.tags.{key,value}` and `document.inherited.{key,value}`,
   *or* record the exclusion as a declared, justified scope decision with the requirement's threshold
   reworded to match. What is not acceptable is the present state: a threshold that says *every* text
   position, a census presented as derived and complete, and four positions outside it that reproduce
   the defect the batch exists to close.

**Should be fixed before merge but do not block on their own** (MEDIUM-1 … MEDIUM-5):

- MEDIUM-1, MEDIUM-2, MEDIUM-3 are record corrections — `six` → `five`; delete or write the three
  phantom node citations; name the `TC-P02/03/04` nodes. Cheap, and they are exactly the class of
  defect this batch exists to repair.
- **MEDIUM-4 is the one worth a second look.** It is the only finding where the independent review's
  PASS rests on something false against disk, and half of G4's fix is genuinely missing. Either land
  limb 2 (`f"id[{raw_nid!r}]"` at `store.py:318`, mirroring `:345`) and update
  `_EXPECTED_REFUSAL["node.id"]`, or record G4 as partially dispositioned. Promote to HIGH if the
  operator holds the review's verdict to the same standard the batch holds its own records to.
- MEDIUM-5 needs an operator ruling on whether the feature batch's PDR artifacts and the `state.json`
  pointer belong on this merge at all.

**Carry, do not gate** (LOW-1 … LOW-6).

### What I could not verify

- **Nothing material was left unverified.** The one item the batch itself recorded as UNVERIFIED — the
  slow-lane flake's provenance — I settled (§3.5).
- Two things I did *not* re-derive from scratch, and say so rather than imply coverage: the batch's
  **19-mutant Inc-1 battery** was spot-checked at three mutants (`M-STO-a`, `M-STO-b`, `M-MAP-a`) plus
  four of my own, not re-run in full; and the **`M-RR2`/`N1`/`N5` arm counts** are taken from the
  packet except where §3.2 and §3.3 state a measured figure.
- `test_tc_p06c`'s `distinct == 10` and the `MASTER_LEGACY_DIGESTS` contents are verified only by the
  suite passing — I did not independently recompute the twelve digests.

---

## 5 · Evidence checklist

| Item | ✓/✗ | Evidence |
|---|---|---|
| Every claimed figure re-derived, not copied | ✓ | §2 — all 13 rows executed this session |
| Dual traceability audited both directions | ✓ | §MEDIUM-2 table — 3 orphan requirement ids, 0 orphan node ids |
| Vacuity hunt executed with real mutants | ✓ | M1, M4, M-STO-a, M-STO-b, M-MAP-a, M-DOC-DROP, M-FICHA-RESET — 7 mutants, all substitution-guarded |
| Weakest arms attacked specifically | ✓ | `test_at_p02f` §3.9 · `test_tc_p06b` §3.10 · `AT-P05` pins MEDIUM-1 · `test_tc_p01c` §3.9 · `_EXPECTED_REFUSAL` §3.8 |
| C-31 input-set audit | ✓ | §3.7 — one violation, and it is HIGH-1 |
| Scope fence swept | ✓ | §3.11 clean on the declared items; MEDIUM-5 and LOW-3 undeclared |
| Honesty audit of the three packets + the code review | ✓ | MEDIUM-1, MEDIUM-3, MEDIUM-4, LOW-1, LOW-5, LOW-6 — every cited node name and load-bearing figure checked against disk |
| Every node name cited in the record resolves on disk | ✗ | **3 phantoms** — MEDIUM-3 |
| Operator rider verified | ✓ | §3.4 — grep + line-by-line read of the assertions |
| Base-ref questions settled with `git worktree`, no working-tree mutation | ✓ | §3.5, §3.1, §3.12 |
| Pre-fix measurement independently reproduced | ✓ | §3.1 — 43 failed / 27 passed at `d877784` |
| Every finding carries `file:line` or pasted output | ✓ | §1 |
| Clean categories reported as clean, not padded | ✓ | §3 — 12 categories |
| No repo file edited; no PII, secrets or real credentials | ✓ | §3.12; all fixtures synthetic (`Alpha`/`Beta`, `d1`, `p.png`) |

---

# Confirmation review — HIGH-1 fix (post-fix tree)

**Reviewer:** `code-reviewer`, independent confirmation pass. Not the author; not the QA reviewer who
raised HIGH-1.
**Target:** branch `fix/repair-batch-02`, commit **`01d7578`**, PR #3. **This gates the merge.**
**Date:** 2026-08-27 · **Posture:** the author's evidence is a claim, not a result. Every figure below
was executed in this session against a `git archive 01d7578` copy under `scratchpad/lab/`.

## Verdict — **BLOCKED**. One **NEW HIGH**.

**HIGH-1's product defect is genuinely closed.** Every text position of a loaded `Document` is `str`,
refusals are recorded, and the reproduced `factory.py:339` consumer crash no longer occurs. The census
is **21** and I proved it exact from the serialiser's own output, not from the model. `Q-high1` is not
vacuous — it reproduces at **exactly 8 arms**. The four secondary gate fixes are each gated by a real
arm.

**But the fix's own refusal sink and collision record have ZERO arms in 548.** Four mutants that
break `dict[str, str]` coercion — including the requirement's own named MUST-GO-RED variant applied to
the map-valued field — leave the entire tree green. The disposition records these limbs as gated. That
is HIGH-1's defect class one level down: a new family given its covered sibling's *implementation* but
not its sibling's *gate*.

**No repo file was edited by this pass.** All mutation work ran on a detached copy with
`PYTHONDONTWRITEBYTECODE=1`, every substitution guarded by an asserted count of exactly 1 and every
restore verified by sha256. `mapper/store.py` and `tests/test_repair_store_boundary.py` in the lab copy
are byte-identical to `01d7578` at the end of the pass (measured, EOL-normalised).

---

## 1 · The new finding

### HIGH-A — the `dict[str, str]` refusal sink and collision record are gated by nothing; four mutants that break them leave all 548 arms green

`_coerce_str_map` (`mapper/store.py:115-133`) has three limbs. Only one of them has an arm.

| Limb | `mapper/store.py` | Mutant | RED arms, **whole tree (548)** |
|---|---|---|---|
| the scalar ladder on keys and values | `:127`, `:132` | `Q-high1` (author's), `MX4`, `MX5` | **8**, 4, 4 — gated |
| **the non-mapping refusal sink** | `:122-124` | **`MX1`** drop the guard entirely | **0** |
| **…its record** | `:123` | **`MX2`** refusal becomes silent | **0** |
| **…its refusal** | `:124` | **`MX11`** return `{"": str(value)}` | **0** |
| **the collision record** | `:128-131` | **`MX3`** drop the record | **0** |

```
=== MX1-drop-nondict-guard  [tests/] ===     RED ARMS: 0    548 passed in 123.17s
=== MX2-nondict-silent      [tests/] ===     RED ARMS: 0    548 passed in 128.69s
=== MX3-drop-collision-record [tests/] ===   RED ARMS: 0    548 passed in 135.92s
=== MX11-nondict-returns-raw [tests/] ===    RED ARMS: 0    548 passed in 126.87s
```

**Each mutant is a real behaviour change, not a cosmetic one.**

- **`MX1`** converts *"the map loads, with the malformed field refused and recorded"* into ***"the whole
  map is DENIED"***. Executed under `MX1`, on the same probe shapes QA's HIGH-1 evidence used:
  ```
  tags = scalar str   -> MapStoreError: no se pudo leer la ficha de m: m_nodos.yml ilegible (AttributeError)
  tags = int          -> MapStoreError: no se pudo leer la ficha de m: m_nodos.yml ilegible (AttributeError)
  tags = list         -> MapStoreError: no se pudo leer la ficha de m: m_nodos.yml ilegible (AttributeError)
  inherited = list    -> MapStoreError: no se pudo leer la ficha de m: m_nodos.yml ilegible (AttributeError)
  ```
  A hand-edited `tags: junk` makes the map unloadable, and no arm anywhere notices.
- **`MX2`** is `LLR-STO.1.1` threshold 2 verbatim — *"appends a `campo ilegible:` record"* — deleted.
  It is also the batch's own F1 standard, quoted at `mapper/store.py:154`: *"Loud denial is already a
  report; silent discard is not."*
- **`MX11`** is the requirement's **named weaker variant `M-STO-b`** (`01-requirements.md:134-135`,
  *"let containers coerce via `str(value)`… must go RED"*) applied to the map-valued field. It goes
  **green**.
- **`MX3`** silently drops one of two colliding tag keys; on the next `save` the operator's tag is gone
  from disk. That is the exact loss `_coerce_str_map`'s own comment (`:118-120`) says it prevents.

**The asymmetry is the finding.** `Ficha.fields` is the sibling the whole HIGH-1 argument rests on, and
its three analogous limbs each redden — I built them to make the comparison rather than assume it:

| Analogue mutant on `Ficha.fields` | RED arms (548) | The arm that catches it |
|---|---|---|
| `MY1` — non-dict guard's record deleted (`store.py:388`) | **1** | `tests/test_repair_fields.py::test_tc_r18_a_non_dict_fields_block_does_not_deny_the_map` |
| `MY3` — non-dict block coerced to its repr | **1** | same node |
| `MY2` — collision record deleted (`store.py:405-407`) | **1** | `test_repair_store_boundary.py::test_at_p02d[field-keys-coerce-together]` |

So the covered sibling has an arm per limb; the new family has an arm for one limb of three. **This is
structurally HIGH-1**: the census grew, the implementation grew with it, and the *gate* did not.

**Why the existing arms cannot see it.** The census poisons *positions*
(`document.tags.key` / `.value`), and `_poison` (`tests/test_repair_store_boundary.py:229-235`) always
writes a **dict** into the field — `{value: "t"}` or `{"t": value}`. No arm in the file ever makes
`tags` or `inherited` stop being a mapping, and no arm ever puts two colliding keys in one. Both shapes
are named in HIGH-1's own evidence (`04-qa-adversarial.md:54-55`, *"`tags`/`inherited` themselves can
stop being mappings entirely"*) and neither was carried into the fix's test set.

**The record that is false against disk.** `04-gate-findings-disposition.md:29-33`:

> `_coerce_str_map` runs the same ladder, **same sink and same collision handling** on both sides. …
> Gated by `Q-high1`: **8 arms**.

`Q-high1` reverts the whole construction to raw pass-through, so it reddens on the *ladder* limb and
cannot distinguish the other two. Reproduced exactly, per-arm:

```
=== Q-high1-replica  [tests/test_repair_store_boundary.py] ===
RED ARMS: 8      8 failed, 76 passed in 3.57s
  test_at_p01[document.tags.key]        test_at_p01[document.tags.value]
  test_at_p01[document.inherited.key]   test_at_p01[document.inherited.value]
  test_at_p02[document.tags.value]      test_at_p02[document.inherited.value]
  test_at_p02c[document.tags.key]       test_at_p02c[document.inherited.key]
```

All eight are ladder arms. The sink and the collision handling are described as gated and are gated by
nothing — which is the C-55 limb-2 / F1 / G2 standard this batch applied to itself three times.

**Severity.** HIGH under the *false-confidence* limb, not the crash limb. The shipped behaviour is
**correct**; there is no live product defect here. What is defective is the evidence: a control the
disposition presents as gated, whose deletion 548 arms cannot see, in the exact place a HIGH was just
raised for the same reason. It is the same category the batch assigned its own HIGH-1 — *"a
scope-and-evidence HIGH, not a crash-on-mount HIGH"*.

**Suggested fix — three arms, derived over `_str_map_field_names(Document)` so a future field extends
them. I wrote and executed them; on the shipped tree 8 pass, and each surviving mutant dies:**

```python
_BAD_STR_MAPS = {"scalar-str": "junk", "int": 7, "list": [1, 2]}

@pytest.mark.parametrize("field_name", _str_map_field_names(Document))
@pytest.mark.parametrize("case", sorted(_BAD_STR_MAPS))
def test_at_p02g_a_non_mapping_str_map_is_refused_and_recorded(tmp_path, field_name, case):
    s = copy.deepcopy(BASE_SIDECAR)
    s["documents"][0][field_name] = _BAD_STR_MAPS[case]
    graph = _write(tmp_path, s).load("m")            # must NOT deny the map
    doc = next(iter(graph.documents.values()))
    assert getattr(doc, field_name) == {}            # refused, not coerced to a repr
    assert f"campo ilegible: document[0].{field_name}" in graph.load_warnings

@pytest.mark.parametrize("field_name", _str_map_field_names(Document))
def test_at_p02h_a_str_map_key_collision_is_recorded(tmp_path, field_name):
    s = copy.deepcopy(BASE_SIDECAR)
    s["documents"][0][field_name] = {1: "from-int", "1": "from-str"}
    graph = _write(tmp_path, s).load("m")
    assert f"campo duplicado: document[0].{field_name}.'1' <- '1'" in graph.load_warnings
```

```
shipped tree                  -> 8 passed in 0.52s
MX1  (drop non-dict guard)    -> 6 failed, 2 passed
MX2  (refusal silent)         -> 6 failed, 2 passed
MX3  (collision silent)       -> 2 failed, 6 passed
MX11 (map coerced to repr)    -> 6 failed, 2 passed
```

(The `campo duplicado` string is the one the implementation actually emits at `store.py:129-131`;
I executed it rather than reading it off the format string.)

---

## 2 · MEDIUM

### MEDIUM-A — the requirement still says the census is **17**; the code, the test and the disposition all say **21**

`01-requirements.md` is authoritative for `HLR-STO.1` / `LLR-STO.1.1` and was never amended:

```
:122  count was wrong twice already (5 families → 6; 17 positions).
:123- **Threshold 1 (coercion):** for each of the **17** derived positions, poisoning it with a
:124  coercible scalar and loading yields **0** non-`str` positions. Measured pre-fix: **12 of 17 leak**.
```

against `mapper/store.py` (the commit message: *"The census is 21, not 17"*),
`tests/test_repair_store_boundary.py:20` (*"The census is **21**"*) and
`04-gate-findings-disposition.md:27`. HIGH-1's stated remedy offered two routes — extend the census
**or** *"record the exclusion … with the requirement's threshold reworded to match"*
(`04-qa-adversarial.md:518-522`). The census was extended and the threshold was not reworded, so the
requirement now understates its own gate by four positions. In a batch whose third defect is a record
that is false against disk, in the requirement the census is measured against.

**Suggested fix:** `17` → `21` at `:123-124`, and amend `:122`'s history line to
`(5 families → 6; 17 positions → 21)`, which is the correction the test docstring already carries.

### MEDIUM-B — `store.py:105-106` claims a generality the code does not have (fourth instance of the F2 class)

```python
# mapper/store.py:105-106
Derived here so the exclusion cannot return: adding another `dict[str, str]`
field to any round-tripped dataclass extends the coercion automatically.
```

**`_coerce_str_map` has exactly one call site, and it is `Document`-only** (`store.py:338-341`;
repo-wide grep confirms no other). Executed against the shipped tree:

- `Ficha.fields` is still hand-wired at `store.py:384-408` — it does **not** go through `_coerce_str_map`.
- `SchemaField` (`:323-328`) and `Attachment` (`:424`) are built from `_coerce_text_fields` plus explicit
  kwargs, so a `dict[str, str]` added to either would be neither coerced nor read — silently dropped.

`_str_map_fields` genuinely returns `('fields',)` for `Ficha` — the derivation is right, and nothing
calls it. This is the same *"a false premise in a comment I wrote"* defect F2 fixed in this very commit,
and by the disposition's own count (`04-gate-findings-disposition.md:60`) it would be the fourth
instance in this batch.

**Suggested fix:** narrow the sentence to what is true — *"…extends `Document`'s coercion
automatically; `Ficha.fields` is coerced by its own site in `_graph_from_sidecar`, and no other
round-tripped dataclass declares one"* — or route `Ficha.fields` through `_coerce_str_map` and make the
claim true. The second is a behaviour change (the two sites emit different record coordinates, which
18 arms pin), so the comment correction is the surgical option.

### MEDIUM-C — the derivation is a **textual** annotation match, and the test shares the identical predicate, so both would go blind together

`store.py:111` and `tests/test_repair_store_boundary.py:91` are byte-identical predicates. Executed on
a probe dataclass under `from __future__ import annotations`:

```
annotation written as       spec.type                 CAUGHT by _str_map_fields?
  dict[str, str]            'dict[str, str]'          True
  dict[str,str]             'dict[str, str]'          True     <- compiler normalises
  dict[str,  str]           'dict[str, str]'          True     <- compiler normalises
  Dict[str, str]            'Dict[str, str]'          False
  StrMap  (type alias)      'StrMap'                  False
  Mapping[str, str]         'Mapping[str, str]'       False
  dict[str, str] | None     'dict[str, str] | None'   False
  "dict[str, str]" (quoted) "'dict[str, str]'"        False
```

`_text_fields` has the same shape: `str | None` is not caught. **Not a present-tense defect** — I
verified every field of all four round-tripped dataclasses uses the exact spellings, and the
serialised-census cross-check in §3.2 comes back exact. The finding is that the *test's* census is
derived by the *same rule as the product*, so a future field spelled any of the four "False" ways would
fall out of the coercion **and** out of the census simultaneously, and no arm would redden. That is
HIGH-1's precise mechanism, latent.

**Suggested fix** — a drop-in that produces an identical result today (executed):

```python
import typing
def _str_map_fields(cls: type) -> tuple[str, ...]:
    hints = typing.get_type_hints(cls)
    return tuple(n for n in cls.__dataclass_fields__ if hints[n] == dict[str, str])
```
```
  SchemaField  text=['key','label','kind']            strmap=[]                     other=['required']
  Attachment   text=['kind','path','caption']         strmap=[]                     other=[]
  Ficha        text=['title','state','meta','notes']  strmap=['fields']             other=['attachments']
  Document     text=['name','source','path','kind']   strmap=['tags','inherited']   other=['template']
```

Plus one **totality** arm: every field of `(Ficha, Attachment, SchemaField, Document)` must be
classified as text, as a str-map, or by an explicitly declared non-text set — so a field spelled a new
way fails loudly instead of vanishing. The file already asserts totality for `_EXPECTED_REFUSAL` over
positions (`:304`); this is the same guard one level up, over model *fields*, and it is the guard whose
absence is what let HIGH-1 exist.

---

## 3 · Clean — what was attacked, and what came back clean

### 3.1 · HIGH-1's product defect is CLOSED — QA's own probe shapes, re-run

Fifteen shapes, executed against `01d7578`. **Every text position of a loaded `Document` is `str`, and
every refusal is RECORDED:**

```
tags value = int         -> tags={'owner': '12345'}    NONSTR=NONE  warnings=[]
tags key = int           -> tags={'7': 'seven'}        NONSTR=NONE  warnings=[]
tags value = dict        -> tags={'owner': ''}         NONSTR=NONE  warnings=['campo ilegible: document[0].tags.owner']
tags value = list        -> tags={'owner': ''}         NONSTR=NONE  warnings=['campo ilegible: document[0].tags.owner']
tags key = bytes         -> tags={'': 'x'}             NONSTR=NONE  warnings=["campo ilegible: document[0].tags[b'hi']"]
inherited value = int    -> inherited={'a': '99'}      NONSTR=NONE  warnings=[]
inherited key = int      -> inherited={'5': 'five'}    NONSTR=NONE  warnings=[]
tags = scalar str        -> tags={}                    NONSTR=NONE  warnings=['campo ilegible: document[0].tags']
tags = int               -> tags={}                    NONSTR=NONE  warnings=['campo ilegible: document[0].tags']
tags = list              -> tags={}                    NONSTR=NONE  warnings=['campo ilegible: document[0].tags']
tags = None              -> tags={}                    NONSTR=NONE  warnings=['campo ilegible: document[0].tags']
inherited = scalar str   -> inherited={}               NONSTR=NONE  warnings=['campo ilegible: document[0].inherited']
inherited = list         -> inherited={}               NONSTR=NONE  warnings=['campo ilegible: document[0].inherited']
tags = nested dict val   -> tags={'owner': ''}         NONSTR=NONE  warnings=['campo ilegible: document[0].tags.owner']
```

**The reproduced consumer crash is gone.** `factory.py:339-343` driven directly with a loaded graph:

```
int tag key     OK  keys=['7', 'x']       warnings=[]
int tag value   OK  keys=['owner', 'x']   warnings=[]
```

Pre-fix this was `TypeError: '<' not supported between instances of 'int' and 'str'`.

*Recorded as a LOW, not padded:* a YAML-null `tags:` produces `campo ilegible: document[0].tags` where
the scalar ladder maps `None` → `""` silently (`store.py:62-63`). Asymmetric, but loud and
non-destructive, and `_build_sidecar` never emits null — so it only reaches a hand-edited file.

### 3.2 · The census is **21** and EXACT — proved from the serialiser's output, not from the model

I built a fully-populated `Graph`, ran `MapStore._build_sidecar` on it, and enumerated every leaf of
the real serialised structure independently of `_derived_positions()`:

```
SERIALISED text leaves (21):
  attachment.caption  attachment.kind  attachment.path
  document.inherited.key  document.inherited.value  document.kind  document.name
  document.path  document.source  document.tags.key  document.tags.value
  fields.key  fields.value  node.id  node.meta  node.notes  node.state  node.title
  schema.key  schema.kind  schema.label

NON-text leaves (correctly out of the census): [('document.template','bool'), ('schema.required','bool')]

derived census (21) == serialised text leaves (21)?  True
in census but not serialised: []      serialised but not in census: []
```

**There is no third hand exclusion.** The only two leaves outside the census are `bool`. I also checked
for container-typed fields carrying text that round-trip: there are none — `Ficha.attachments`
(`list[Attachment]`) and `Graph.schema` (`list[SchemaField]`) decompose into covered scalar positions,
`Graph.documents` is keyed by the already-covered `document.name`, and `Edge.label` / `Graph.root_id`
live in the `.mmd`, not the sidecar. `Graph.load_warnings` (`list[str]`) is not serialised.

*Residual, recorded not padded:* `_derived_positions()` still opens with three **hand-written**
structural entries (`:102`), including `fields.key`/`fields.value` where `_str_map_field_names(Ficha)`
would derive them. It produces the right answer today and is coupled to a hand-written `_build_sidecar`
rather than silently diverging from it, so it is a LOW, not the third exclusion — but it is the one
place the file's "derived, not hand-listed" claim is still literally untrue.

### 3.3 · `_KEY_POSITIONS`' new derivation is CORRECT, and it is itself gated

The predicate at `:136` selects exactly `('node.id', 'fields.key', 'document.tags.key',
'document.inherited.key')` — 4 of 21, leaving 17 container-poisonable. Checked directly:

- **`schema.key` is correctly NOT excluded.** It is a `str` field named `key`, not a mapping key; it
  does not start with `"document."`, so the predicate leaves it in `_container_poisonable()`, where
  `test_at_p02[schema.key]` and `test_at_p03[schema.key]` exercise it. Confirmed in the resolved list.
- The `or`/`and` precedence reads as intended: `A or B or (C and D)`.
- **The predicate is gated both ways:**

```
=== MX9-keypos-also-excl-value (drop the .key suffix test) ===   RED ARMS: 1
    test_tc_p01c_the_container_exclusion_is_justified_not_merely_declared
=== MX10-keypos-hand-list-old (revert to ("node.id","fields.key")) ===  RED ARMS: 5
    test_tc_p01c · test_at_p02[document.tags.key] · test_at_p02[document.inherited.key]
    test_at_p03[document.tags.key] · test_at_p03[document.inherited.key]
```

The claim at `04-gate-findings-disposition.md:31-33` that hand-listing *"would have silently omitted
the new pair"* is right, and `test_tc_p01c` is the arm that would have caught it.

*Latent, LOW:* a future `str` field on `Document` literally named `key` would produce the position
`document.key`, which `startswith("document.") and endswith(".key")` would wrongly exclude. Same
textual-predicate family as MEDIUM-C.

### 3.4 · `Q-high1` is NOT vacuous — reproduced at exactly 8 arms

Built from scratch (revert `tags`/`inherited` to `d.get(name, {})` raw pass-through), substitution count
asserted 1: **8 failed, 76 passed**, arm names listed in §1. The author's figure is exact.

I also decomposed it, which the author did not: `MX4` (value not coerced) → 4 arms, `MX5` (key not
coerced) → 4 arms, `MX6` (drop `inherited` from the derivation) → 2 arms, `MX7` (`_str_map_fields`
returns empty) → 4 arms, `MX8` (owner coordinate corrupted to `XXXX`) → 4 arms. Every ladder limb is
independently gated, and the record's **owner coordinate** is gated too — the C2 defect is not
re-introduced for the new family.

### 3.5 · Blast radius of the two shared-fixture changes — clean

- **`_KEY_POSITIONS` and `BASE_SIDECAR` are module-private.** Repo-wide grep: every reference is inside
  `tests/test_repair_store_boundary.py`. No other file imports either.
- **Populating `BASE_SIDECAR`'s `tags`/`inherited` weakened nothing.** Structurally it cannot: every
  assertion in the file is position-keyed (`(position, "") in live`, `_EXPECTED_REFUSAL[position]`), and
  the new observations carry positions that did not exist before this commit; `offenders == []` is
  strictly strengthened by more observations. Empirically, the batch's own named mutants are **not**
  weaker on the post-fix tree — `M-STO-a` reddens **21** whole-tree (QA measured 21), `M-STO-b` reddens
  **27** whole-tree (QA measured 16 on the boundary file alone).
- *Recorded as an observation, not a finding:* the population is **inert**. Emptying `tags`/`inherited`
  back to `{}` reddens **0 of 84**. Contrast the `B` node entry at `:62-68`, which the file documents as
  load-bearing *after measuring it* (review G1). The `tags`/`inherited` population carries no comment
  and no weight — harmless, but it is not doing the work the `B` precedent set the standard for.

### 3.6 · The four other gate fixes in the same commit — each gated, none regressed

| Fix | Mutant I built | RED arms | Arm |
|---|---|---|---|
| security F1 — reads pulled inside a net | `Q-f1a` drop `UnicodeDecodeError` from the except | **2** | `test_at_p03e[mmd-invalid-utf8]`, `[sidecar-invalid-utf8]` |
| security F1 — `RecursionError` | `Q-f1b` drop it from the parser net | **1** | `test_at_p03e[parser-recursion]` |
| MEDIUM-4 — indexed node-id label | `Q-med4` revert `:373` to the bare `"id"` | **1** | `test_at_p02c[node.id]` |
| F7 — `__cause__ is None` guard | `Q-f7` delete the `isinstance(sidecar, dict)` guard | **1** | `test_at_p03f_the_top_level_type_guard_is_distinguishable_from_the_net` |

**F2's corrected comment is TRUE against disk.** `grep -rn "except MapStoreError" mapper/` outside
`store.py` returns nothing (exit 1). Both `load` callers are at `mapper/app.py:449` and `:1176`, and the
comment's citations `app.py:450` / `app.py:1179` point at their `except Exception` lines — the correct
coordinates for what the sentence claims. `_EXPECTED_REFUSAL["node.id"]` was updated in step with the
MEDIUM-4 fix (`tests/…:175` → `"campo ilegible: node.id[b'hi']"`).

### 3.7 · Numbers reconcile

| Figure | Disposition claims | **Measured here** |
|---|---|---|
| collected | 548 | **548** |
| fast lane | 531 passed / 17 deselected | **531 passed, 17 deselected**, 99.12s, exit 0 |
| slow lane | 17 passed / 531 deselected | **17 passed, 531 deselected**, 43.90s, exit 0 |
| `test_repair_store_boundary.py` | — | **84 passed** |
| `ruff check mapper/ tests/` | 29 (= base) | **29** |
| ruff on the five touched files | clean | **All checks passed!** |
| derived census | 21 | **21**, set-exact vs the serialiser (§3.2) |
| `Q-high1` | 8 arms | **8 arms**, arm names matched |

---

## 4 · What blocks, and what does not

**Blocks:**

1. **HIGH-A** — add the three arms in §1 (verified: 8 pass on the shipped tree; MX1/MX2/MX11 → 6 red,
   MX3 → 2 red). *Or*, if the operator judges the sink and collision limbs out of the fix's declared
   scope, correct `04-gate-findings-disposition.md:29-33` to say what `Q-high1` actually gates — the
   ladder — and carry the two ungated limbs explicitly. What is not acceptable is the present state: a
   HIGH raised *because* a control's coverage was asserted and absent, closed by a fix whose own
   controls are asserted gated and are not.

**Should be fixed before merge, do not block alone:** MEDIUM-A (`17` → `21` in the requirement — one
line, and it is the batch's own defect class), MEDIUM-B (one comment sentence), MEDIUM-C (the
`get_type_hints` swap plus a totality arm; this is the durable fix for the class that produced HIGH-1
twice).

**Carry:** the LOWs in §3.1, §3.2, §3.3 and §3.5.

## 5 · What I could not verify

- **The working tree moved under me, and it is not what I reviewed.** `git status --porcelain` in
  `C:\Users\jjgh8\Github\mapper` was **empty** when this pass began and now reports
  ` M .dev-flow/…/03-increments/increment-001.md`, `?? .dev-flow/…/05-carries.md`, and
  `?? tests/test_repair_artifact_claims.py` (mtimes 17:47–17:51, during this pass). **I created none of
  them** — I ran only read-only `git show` / `git status` / `grep` in the main tree, and every
  experiment ran on a detached `git archive 01d7578` copy. **This verdict covers commit `01d7578` and
  nothing else**; a new test file and an edited increment packet are outside it and un-reviewed.
- I did **not** re-run the author's full 24-mutant battery. I built **22 mutants of my own** and
  reproduced six of the author's by name (`Q-high1`, `Q-f1a`, `Q-f1b`, `Q-med4`, `Q-f7`, plus `M-STO-a`
  and `M-STO-b`); the rest are taken on report and are so marked.
- MEDIUM-C is a **latent** defect. I proved the predicate is blind to five annotation spellings and that
  the test shares the predicate; I did **not** land a field spelled one of those ways in `mapper/model.py`
  to observe the silent miss end-to-end, because that requires editing the repo.
- QA's MEDIUM-1/2/3/5 and the six LOWs are dispositioned as carries and were **out of scope for this
  pass**; I re-checked none of them.

## 6 · Evidence checklist

| Item | ✓/✗ | Evidence |
|---|---|---|
| Diff read in full | ✓ | `mapper/store.py:1-657`, `tests/test_repair_store_boundary.py:1-713`, `mapper/model.py:1-240` |
| HIGH-1's probe shapes independently re-run | ✓ | §3.1 — 15 shapes, all `str`, all refusals recorded |
| Census re-derived from the serialiser, not the model | ✓ | §3.2 — set-exact 21 vs 21, 0 in either difference |
| Derivation predicate attacked | ✓ | §MEDIUM-C — 8 annotation spellings executed, 5 fall out |
| `_KEY_POSITIONS` predicate checked both directions | ✓ | §3.3 — `MX9` 1 arm, `MX10` 5 arms; `schema.key` correctly retained |
| `Q-high1` reproduced, not taken on report | ✓ | §3.4 — 8 arms, arm names matched |
| A green-surviving mutation was hunted for, per the brief | ✗ **FOUND — 4** | `MX1`, `MX2`, `MX3`, `MX11` — 0 red of **548** each |
| Sibling comparison built rather than assumed | ✓ | `MY1`/`MY2`/`MY3` — 1 arm each on `Ficha.fields` |
| Every HIGH carries a recommended fix, executed | ✓ | §1 — 8 pass shipped; 6/6/2/6 red under the four mutants |
| Blast radius reverse-grepped | ✓ | §3.5 — module-private; `FX` fixture-empty mutant 0 red |
| Four secondary gate fixes checked | ✓ | §3.6 — 2/1/1/1 arms; F2 comment verified against disk |
| Every figure executed, none copied | ✓ | §3.7 |
| Clean categories reported as clean, not padded | ✓ | §3 — 7 categories |
| No repo file edited; no git mutation in the main tree | ✓ | detached `git archive` copy; lab `store.py` + boundary file byte-identical to `01d7578` (EOL-normalised) at close |
