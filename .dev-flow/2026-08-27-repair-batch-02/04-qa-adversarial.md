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

---

# Re-confirmation review — HIGH-A fix (post-fix tree, d75f0fd)

**Reviewer:** `code-reviewer`, independent re-confirmation pass. Not the author; not the QA reviewer
who raised HIGH-1; not the confirmation reviewer who raised HIGH-A.
**Target:** branch `fix/repair-batch-02`, commit **`d75f0fd`**, PR #3, diff `01d7578..d75f0fd`.
**This gates the merge.** **Date:** 2026-08-27
**Posture:** the author's evidence is a claim, not a result. Every figure below was executed in this
session against a `git archive d75f0fd` copy in my own scratchpad, `PYTHONDONTWRITEBYTECODE=1`, every
substitution guarded by an asserted hit count of exactly 1, every restore proven by sha256, every
verdict taken **per resolved arm** and never from a process exit code. Mutations are described by
position and operation, never spelled verbatim.

## Verdict — **PASS WITH CONDITIONS**. No HIGH. Two MEDIUM, three LOW.

**HIGH-A is genuinely closed, and closed with real arms rather than theatre.** I rebuilt all four
surviving mutants from the finding's own description rather than taking the author's figures: each
now reddens, at **6 / 6 / 6 / 2** RED arms, exactly the numbers `04-gate-findings-disposition.md`
claims. I then attacked the three new arms from four further directions and each is independently
killable. **MEDIUM-C's end-to-end proof, which the previous reviewer explicitly could not perform
because it required editing the tree, succeeds here**: I landed the offending annotation spellings in
`mapper/model.py` in the lab and `test_at_p02i` reddens on both.

**I hunted hard for a fifth surviving mutation, as the two passes before me each found one.** I found
one green survivor in shipped behaviour — and then **built the sibling comparison instead of
assuming the asymmetry, and it defused the finding**: the covered sibling does not gate that limb
either. It is symmetric and pre-existing, not the HIGH-A shape. I report it as a LOW and explicitly
decline to inflate it.

**What holds the conditions is record-truth, not correctness.** The rewritten `_str_map_fields`
docstring — the one rewritten to *fix* MEDIUM-B — closes by naming `test_at_p02i` as the gate for a
change that node does not gate. Executed: **0 RED of 643**. And `05-carries.md` hands the next
session a collected-count that is stale at the very tip it names, inside the carry whose whole
purpose is to stop a stale count propagating.

**No repo file was edited by this pass except this one.** At close, the lab tree is byte-identical to
pristine `d75f0fd` for every tracked file (`diff -r` against a fresh archive: no differences), and
`git status --porcelain` in the main repo is **empty** — the working-tree drift the previous pass had
to disclaim did not recur.

---

## 1 · Numbers — re-derived, not copied

| Figure | Disposition claims | **Measured here** |
|---|---|---|
| collected | 643 | **643** |
| fast lane | 626 passed / 17 deselected | **626 passed, 17 deselected**, 55.3s, exit 0 |
| slow lane | 17 passed / 626 deselected | **17 passed, 626 deselected**, 23.5s, exit 0 |
| `ruff check mapper/ tests/` | 29 (= base) | **29** |
| ruff on the three touched files | clean | **All checks passed!** |
| arm arithmetic `643 = 548 + 12 + 83` | asserted | **exact** — boundary file 84 to **96** (+12); claims file **83** = 1 + 2x41 corpus files |
| the four HIGH-A mutants | 6 / 6 / 6 / 2 | **6 / 6 / 6 / 2**, arm names matched |

---

## 2 · HIGH-A — closed. Rebuilt from scratch, per limb.

Every limb the previous pass measured at **0 RED of 548** now reddens. Whole-tree runs assert **643
resolved arms** before any verdict is read.

| Limb | Mutation (by position/operation) | RED arms | The arms |
|---|---|---|---|
| non-mapping refusal sink | guard predicate forced never to fire | **6** | all six `test_at_p02g` arms |
| ...its record | the record append replaced by a no-op, refusal kept | **6** | all six `test_at_p02g` arms |
| ...its refusal | sink returns a one-entry map of the value's repr | **6** | all six `test_at_p02g` arms |
| collision record | collision predicate forced never to fire | **2** | both `test_at_p02h` arms |
| sink record's **owner** coordinate | owner replaced by a literal | **6** | all six `test_at_p02g` arms |
| collision record's **field** coordinate | field replaced by a literal | **2** | both `test_at_p02h` arms |
| product str-map predicate matches nothing | value type in the comparison altered | **12** | 2x`test_at_p02`, 2x`test_at_p02c`, 6x`test_at_p02g`, 2x`test_at_p02h` |

The last two rows are mine, not the author's: **the record coordinates are gated too**, so the C2
defect class is not re-introduced for the new family.

**`test_at_p02g`'s three thresholds are separately gated, not one masking two.** Each threshold has
its own killing mutant above: removing the guard denies the map (the arm errors on load), returning a
repr fails the `== {}` assertion, silencing the record fails the containment assertion. Assertion
order does mask *within* a single arm — a repr-returning mutant never reaches the record assertion —
but that costs nothing, because the record assertion has its own mutant that reaches it.

**`test_at_p02i` is a real gate, killed from three independent directions:**

| Mutation | RED arms |
|---|---|
| a class's declared non-text tuple emptied | **1** — `test_at_p02i[Document]` |
| a declared name that is not a field of the class | **1** — `test_at_p02i[Ficha]` |
| a name both classified as text and declared non-text | **1** — `test_at_p02i[Attachment]` |

**MEDIUM-C, proved end-to-end — the step the previous pass could not take.** I landed the annotation
spellings the resolved predicate is still blind to, in `mapper/model.py` in the lab:

| Field landed on `Document` | RED arms |
|---|---|
| a `Mapping[str, str]` field | **1** — `test_at_p02i[Document]` |
| a `str \| None` field | **1** — `test_at_p02i[Document]` |

Both are caught. The latent mechanism MEDIUM-C described is genuinely covered by the totality guard.

**AMD-2's neutrality claim is TRUE, and I extended it past what the packet checked.** The packet
compares the spelled and resolved predicates over four dataclasses; I ran all **seven** in
`mapper/model.py`, and the classification is identical for every one (`SchemaField ()`,
`Attachment ()`, `Ficha ('fields',)`, `Node ()`, `Edge ()`, `Document ('tags','inherited')`,
`Graph ()`). Reverting either predicate — product or census — to the old spelled match reddens **0**
arms, in both directions. It is a blindness fix, not a behaviour change.

**The census derivation stays honest under extension.** Landing a plain `str` field on `Ficha`
reddens **2** arms (the new position's `test_at_p02` arm and `test_tc_p01c`) — the census grows and
the hand-written serialiser's failure to round-trip it is caught loudly, exactly as designed.

---

## 3 · MEDIUM

### MEDIUM-1 — the rewritten `_str_map_fields` docstring names a gate for a change that node does not gate; **0 RED of 643**

`mapper/store.py:120-121`, the closing sentence of the docstring rewritten in this commit *to fix
MEDIUM-B*:

> No other round-tripped dataclass declares a `dict[str, str]` today, and `test_at_p02i` fails
> loudly if one appears.

**Executed, whole tree, 643 resolved arms each:**

| Field landed in `mapper/model.py` | RED arms of 643 |
|---|---|
| a `dict[str, str]` field on `Attachment` | **0** |
| a `dict[str, str]` field on `SchemaField` | **0** |
| a second `dict[str, str]` field on `Ficha` | **0** |

`test_at_p02i` asserts `every == classified | declared`. A `dict[str, str]` field **is** classified —
`_str_map_field_names` returns it — so the guard passes, silently. The guard fires on fields that are
*neither* text nor str-map (which is what its own docstring correctly claims, and what I proved in
§2); it does not fire on a new str-map on a class the coercion does not reach. Such a field would be
neither coerced (the call site is `Document`-only) nor written (`_build_sidecar` is hand-enumerated),
so it would be silently dropped — the precise outcome MEDIUM-B was raised about.

**Why this is a MEDIUM and not a HIGH.** No shipped behaviour is left ungated by it; the cost is a
future maintainer's false reassurance, not a live defect, and no test gives false confidence about
code that exists today. **Why it is not a LOW.** It is the same sentence, the same function and the
same file as MEDIUM-B, and the correction fixed the *coercion* half while introducing a fresh false
claim in the *gate* half — and naming a specific node as the gate for something it does not gate is
structurally the "gated by `Q-high1`: 8 arms" shape that made HIGH-A a HIGH.

**Suggested fix** — say what the guard does, which is already true and already valuable:

> No other round-tripped dataclass declares a `dict[str, str]` today. `test_at_p02i` does **not**
> catch one that appears — a str-map classifies, so the guard passes; what it catches is a field that
> is neither text nor a str-map. A `dict[str, str]` on another dataclass must be routed here (or to
> its own coercion site) by hand, and `_build_sidecar` extended to write it.

**Same class, same fix, two more places.** `03-increments/increment-004.md` §1.2 and
`01-requirements.md` §7 AMD-2 both say the guard covers "every field of **every** round-tripped
dataclass". Measured: it covers **4 of the 7** dataclasses in `mapper/model.py` — `Node`, `Edge` and
`Graph` are absent from its class set, and `Node` **is** round-tripped (`node.id` is census position
1, written by `_build_sidecar`). Landing a `str` field on `Node` reddens **0 of 96** boundary arms.
The class set is the residual hand list one level above the field sets — which are properly guarded.

### MEDIUM-2 — `05-carries.md:40` propagates a stale collected-count, inside the carry that exists to stop exactly that

> 2. Re-measure `baseline.tests_collected` rather than carrying `429`; it is **548** at this batch's tip.

The tip is `d75f0fd`. **Measured: 643.** The line was authored in this commit, and the commit that
authored it is the one that took the count from 548 to 643. P-CARRY-1's entire argument is that the
next session will read a stale number and inherit a false premise; the instruction it gives hands
over a number stale by 95 arms. `04-gate-findings-disposition.md`'s own post-fix table has 643 right,
so the two artifacts in this commit disagree.

(`05-carries.md:62`'s "all 548 arms green" is **correct** — that one is explicitly historical,
describing the pre-fix measurement. Only `:40` is false against disk.)

**Suggested fix:** `548` to `643` at `:40`.

---

## 4 · LOW

### LOW-1 — the widened claims corpus buys 3 checked claims across 2 of 33 source files, and catches **0 of the 4** recorded instances it cites as its motivation

`tests/test_repair_artifact_claims.py` widened the corpus to `mapper/`. Measured:

```
authored=8  source=33  corpus=41   ->  arms = 1 + 2*41 = 83
corpus files with ZERO path:line citations : 35/41
corpus files with ZERO test identifiers    : 31/41
corpus files VACUOUS on BOTH arms          : 31/41    (62 of 83 arms assert nothing)
SOURCE files carrying any claim            : store.py (2 citations, 1 node), keymap.py (1 node)
```

**Both halves of the corpus are live** — I proved it rather than assuming (§5), so the vacuity is
aggregate, not total, and the file's own non-degeneracy arm guards it. The finding is narrower: the
`_source()` docstring motivates the widening with *"THIS IS WHERE THE FALSE CLAIMS ACTUALLY LIVED ...
the half that was missing"*, and all three of the `mapper/` instances it names were **prose** claims
("every caller catches X", "the coercion removes the phantom node", "extends any round-tripped
dataclass"). The file's two rules decide `path:line` and `test_*` only. So the widening catches **0
of the 4** recorded instances — including, pointedly, MEDIUM-1 above, which is a prose over-claim
sitting in the very file the corpus was widened to cover.

The file is **not** dishonest — it states "Prose claims are NOT checked" and argues that a checker
appearing to cover a class it cannot decide is worse than one whose limits are written down. That
argument is right, and it is why this is a LOW. What is off is only the motivating framing, which
reads as though the widening addresses the three instances. One sentence.

Nit in the same file: the `_live_nodes` docstring says the widened corpus "made this 40 arms";
measured **41** (42 counting the non-degeneracy arm).

### LOW-2 — the resolved predicate is ~430x more expensive per call, uncached, on a per-document path

Measured on the lab tree:

```
spelled  predicate: 0.8 us per call
resolved predicate: 348.5 us per call
```

`_str_map_fields(Document)` is called **once per document** inside `_graph_from_sidecar`'s loop, and
`get_type_hints` is uncached. Cost scales with the document count (~35 ms at 100 documents).
**Impact today is zero** — no sidecar in `maps/` or `fixtures/` carries a single document, and no
perf arm covers the document path — which is why this is a LOW and not a MEDIUM. One-line fix:
`functools.lru_cache` on `_str_map_fields`, the same instrument the author already applied to
`_live_nodes()` in this commit for the same reason.

### LOW-3 — `test_at_p02h` pins the collision RECORD but not which colliding key survives — and the covered sibling does not either

Changing the str-map's collision assignment from keep-last to keep-first reddens **0 of 643**. This
is the one green survivor in shipped behaviour I found, and it is the shape HIGH-A was built from —
so **I built the sibling comparison rather than assume the asymmetry**:

| Mutation | RED arms of 643 |
|---|---|
| the str-map collision keeps first, not last | **0** |
| the `Ficha.fields` collision keeps first, not last (the covered sibling) | **0** |

**Symmetric.** The new family matches its covered sibling exactly on this limb; both record the
collision, neither pins the survivor. This is therefore **not** the HIGH-A shape and **not** a
regression introduced by this commit — it is a pre-existing, shared, unpinned detail, and both
behaviours are loud. Recorded so it is countable, deliberately **not** inflated into a finding.

---

## 5 · Clean — what I attacked that came back clean

1. **The four HIGH-A mutants** — rebuilt from the finding's description, not copied: 6 / 6 / 6 / 2.
2. **The record coordinates of both new limbs** — corrupting the sink's owner (6 arms) and the
   collision's field (2 arms) each redden. C2 is not re-introduced.
3. **`test_at_p02i` killed three ways** — 1 arm each, and each names the right class.
4. **MEDIUM-C end-to-end** — `Mapping[str, str]` and `str | None` landed on `Document`: 1 arm each.
5. **AMD-2 behaviour-neutrality** — identical classification across **all seven** dataclasses;
   reverting either predicate reddens 0 arms in both directions.
6. **The claims checker is live on BOTH halves**, and its floors are live:

   | Mutation | RED arms | Arm |
   |---|---|---|
   | an authored artifact's citation pushed past EOF | **1** | the `increment-004.md` citation arm |
   | a `mapper/store.py` comment citation pushed past EOF | **1** | the `store.py` citation arm |
   | a `mapper/store.py` cited node made phantom | **1** | the `store.py` identifier arm |
   | a `mapper/keymap.py` cited node made phantom | **1** | the `keymap.py` identifier arm |
   | the **source** half of the corpus emptied | **1** | `test_the_checker_can_see_its_corpus` (arms collapse 83 to 17) |
   | the **authored** half of the corpus emptied | **1** | `test_the_checker_can_see_its_corpus` (arms collapse 83 to 67) |

   The two collapse figures matter: the non-degeneracy arm reddens **because** it asserts floors, not
   as a side effect — a corpus that looked nowhere would otherwise take 62 vacuous arms green with it.
7. **The `functools.lru_cache` on `_live_nodes()` is sound.** No arguments, `maxsize=1`, so exactly
   one collection subprocess per pytest process; `addopts` carries no xdist, so there is no
   per-worker multiplication. Measured: the whole 83-arm file runs in **1.32s** against a collection
   that alone costs 0.70s — one subprocess, not 42. No recursion hazard: the subprocess collects, and
   collection never calls `_live_nodes()`.
8. **`_EXPECTED_NON_TEXT`'s *field* sets are not a C-31 defect** — all three ways of corrupting them
   redden (§2). Only its *class* set is a live hand list (MEDIUM-1's second half).
9. **No regression across the rest of the tree.** Both lanes exit 0 at the expected counts; ruff is
   at the 29-error baseline whole-tree and clean on all three touched files.
10. **The disposition's corrected record is TRUE against disk.** Its per-limb table, its arm
    arithmetic (`643 = 548 + 12 + 83`) and both lane figures all reproduce exactly. The correction is
    marked in place rather than edited away, which is the right disposition.
11. **`01-requirements.md` §7 AMD-1 is TRUE against disk** — threshold 1 now reads 21, the `12 of 17`
    figure is explicitly scoped as historical, `M-STO-b` is extended to the map-valued fields, and
    Threshold 4 is stated. MEDIUM-A is discharged.

---

## 6 · What I could not verify

- **I did not re-run the author's full mutation battery.** I built my own (23 mutants: 10 product,
  8 test/model, 6 claims-checker, 1 sibling) and reproduced the four HIGH-A mutants by construction
  from the finding's prose. The author's other figures are taken on report and are so marked.
- **I did not test every blind spelling end-to-end.** I landed `Mapping[str, str]` and `str | None`;
  the `typing.Dict` spelling, a type alias and a quoted annotation are the same class and were
  **not** individually landed.
- **P-CARRY-1's `state.json` claims are out of scope** and I re-checked none of them except the 548
  figure at `:40` (MEDIUM-2).
- **The security review, and QA's MEDIUM/LOW carries, were out of scope for this pass.** I re-checked
  none of them.
- **I could not exercise the save side of a new `dict[str, str]` field**, because `_build_sidecar` is
  hand-enumerated and adding one requires editing the serialiser; the read-side measurements in
  MEDIUM-1 are what I executed.

---

## 7 · What blocks, and what does not

**Nothing blocks.** HIGH-A's product limbs are gated, its arms are real, MEDIUM-A/B/C are discharged,
and no shipped-behaviour mutation survived green that the covered sibling does not also leave green.

**Conditions before merge — three edited lines, no code change:**

1. **MEDIUM-1** — correct `mapper/store.py:120-121` to say what `test_at_p02i` actually gates, and
   soften "every round-tripped dataclass" in `increment-004.md` §1.2 and `01-requirements.md` §7
   AMD-2 to the four classes the guard covers.
2. **MEDIUM-2** — `548` to `643` at `05-carries.md:40`.

**Carry:** LOW-1 (one sentence of framing in the claims checker, plus the 40/41 nit), LOW-2 (cache
the resolved predicate if the document path ever carries load), LOW-3 (the shared unpinned collision
survivor — if it is ever pinned, pin it on both sites together).

---

## 8 · Evidence checklist

| Item | Mark | Executed evidence |
|---|---|---|
| Diff read in full | OK | `01d7578..d75f0fd`: `mapper/store.py` (+28/-16), both test files, all four records |
| Expected arm count asserted before any verdict | OK | 643 collected; whole-tree trials report **643 resolved arms** each; boundary file 96, claims file 83 |
| Both lanes and ruff re-derived, not copied | OK | 626/17 in 55.3s; 17/626 in 23.5s; ruff 29 whole-tree, clean on the three touched files |
| The four HIGH-A mutants rebuilt, not taken on report | OK | §2 — 6 / 6 / 6 / 2, arm names matched |
| `test_at_p02g`'s three thresholds shown separately gated | OK | §2 — a distinct mutant kills each; assertion-order masking costs nothing |
| `test_at_p02i` shown killable | OK | §2 — three mutations, 1 arm each, correct class id |
| MEDIUM-C proved END-TO-END (the step the prior pass could not take) | OK | §2 — `Mapping[str, str]` and `str \| None` landed in `model.py`: 1 arm each |
| `get_type_hints` swap shown behaviour-neutral | OK | §2 — identical classification across all **seven** dataclasses; both reverts 0 red |
| Record coordinates of the new limbs attacked | OK | §2 — owner 6 arms, field 2 arms |
| A green-surviving mutation hunted for, per the brief | **FOUND 4; 3 stand as MEDIUM-1, 1 defused** | §3 MEDIUM-1 (0/643 x3); §4 LOW-3 (0/643) |
| Sibling comparison BUILT rather than assumed | OK | §4 LOW-3 — the covered sibling is 0/643 too, so LOW-3 is symmetric, not HIGH-A |
| `_EXPECTED_NON_TEXT` checked as a C-31 input set | OK | §5.8 — field sets gated 3 ways; class set is the live hand list (MEDIUM-1) |
| Claims-checker corpus checked for vacuous arms | OK | §4 LOW-1 — 31/41 files vacuous on both arms; 2/33 source files carry a claim |
| Claims-checker shown non-vacuous on BOTH halves | OK | §5.6 — six mutants, 1 arm each; floors collapse 83 to 17 / 67 |
| `lru_cache` on `_live_nodes()` audited | OK | §5.7 — 83 arms in 1.32s, one subprocess, no xdist, no recursion |
| Records re-checked against disk | Mixed | disposition OK, AMD-1 OK, AMD-2 OK; store.py docstring FALSE (MEDIUM-1); carries `:40` FALSE (MEDIUM-2) |
| Every MEDIUM carries a recommended fix | OK | §3 — replacement sentence given for MEDIUM-1; one token for MEDIUM-2 |
| Clean categories reported as clean, not padded | OK | §5 — 11 categories; LOW-3 explicitly declined as a finding |
| No repo file edited but this one; no git mutation | OK | lab `diff -r` vs a fresh `git archive d75f0fd`: **no differences** in any tracked file; `git status --porcelain` empty |

---

# Condition-discharge review (a5db8df)

**Reviewer:** `code-reviewer`, independent condition-discharge pass. Not the author; not the QA
reviewer who raised HIGH-1; not the confirmation reviewer who raised HIGH-A; not the re-confirmation
reviewer who raised MEDIUM-1/MEDIUM-2.
**Target:** branch `fix/repair-batch-02`, commit **`a5db8df`**, PR #3, diff `d75f0fd..a5db8df`.
**Scope, deliberately narrow:** are the two conditions actually discharged, and did the discharge
break or newly over-claim anything. HIGH-A was **not** re-reviewed from scratch; the prior pass
cleared it.
**Date:** 2026-08-27
**Posture:** every figure below was executed in this session against a `git archive a5db8df` copy in
my own scratchpad, `PYTHONDONTWRITEBYTECODE=1`, every substitution guarded by an asserted hit count
of exactly 1, every restore proven by sha256, every verdict taken **per resolved arm** and never from
a process exit code. Mutations are described by position and operation, never spelled verbatim.

## Verdict — **DISCHARGED WITH NEW CONDITIONS.** No HIGH. Three new findings, all record-truth.

**Both conditions are genuinely discharged, and MEDIUM-1's second half is discharged HARDER than the
condition asked for.** The re-confirmation asked the author to *soften* the docs to the four classes
the guard covered. The author instead **derived** the class set from `mapper.model` and pinned it
with a new node — and the derivation is real, not decorative: I re-narrowed it in the lab and it
reddens; I landed a brand-new dataclass in the model and it reddens; I removed the census-position-1
class from the declared map and it reddens on two arms. `test_at_p02j` is killable in **both**
directions of its own assertion.

**The author's explicit NON-claim is honest in both directions, and I proved it with a control rather
than reading it.** A plain `str` field on the census-position-1 class still reddens **0 of 647** — the
author says so and carries it rather than claiming it fixed. The stated *reason* is also the true one:
I read `_derived_positions()` (it hard-codes `node.id` and derives text fields from `Ficha`,
`Attachment`, `SchemaField`, `Document` only) and `_build_sidecar` (`mapper/store.py:289-322`, fully
hand-enumerated), then **built the control the author did not**: the same text field landed on a
census-derived class instead reddens **2** arms. The asymmetry is caused by exactly the mechanism the
author names, and by nothing else he left out.

**I hunted for a third false claim inside the fix for a false claim, as the brief instructed and as
the two passes before me each found. There is one — and there are two more of the same family.** All
three are record-truth in prose; none gates behaviour, none gives false confidence about code that
exists, and every one is a one-token or one-sentence fix. The sharpest sits inside the claims-checker's
own docstring: the sentence rewritten to be honest about scope states a figure that **its own next
sentence contradicts and disk refutes**.

**No repo file was edited by this pass except this one.** At close, the lab tree is byte-identical to
a fresh `git archive a5db8df` (`diff -r`: no differences in any tracked file) and `git status
--porcelain` in the main repo is **empty**.

---

## 1 · Numbers — re-derived, not copied

| Figure | Packet claims | **Measured here** |
|---|---|---|
| collected | 647 | **647** |
| fast lane | 630 passed / 17 deselected | **630 passed, 17 deselected**, 55.8s, exit 0 |
| slow lane | 17 passed / 630 deselected | **17 passed, 630 deselected**, 22.9s, exit 0 |
| `ruff check mapper/ tests/` | 29 | **29** |
| ruff on the three touched files | clean | **All checks passed!** |
| boundary file | 84 to 100 | **100** |
| artifact-claims file | 83 | **83** |
| ledger `647 = 548 + 16 + 83` | asserted | **exact** — `test_at_p02i` **7** arms + `test_at_p02j` **1** |
| pristine pre-red arms | 0 | **0 of 647** |

---

## 2 · MEDIUM-1, first half — the `_str_map_fields` docstring. **DISCHARGED, and TRUE against disk.**

`mapper/store.py:120-127`. Every clause of the replacement was checked separately:

| Clause | Verified how | Result |
|---|---|---|
| "No other round-tripped dataclass declares a `dict[str, str]` today" | enumerated every field of all 7 model dataclasses | **TRUE** — only `Ficha.fields`, `Document.tags`, `Document.inherited`, and both classes are named in the paragraph above it |
| "NO TEST CATCHES ONE THAT APPEARS" | a str-map field landed on an uncovered class, whole tree | **TRUE — 0 RED of 647** |
| "a str-map CLASSIFIES, so the totality guard passes" | read the predicate; confirmed by the run above | **TRUE** |
| "what that guard catches is a field that is neither text nor a str-map" | a neither-text-nor-str-map field landed on the census-position-1 class | **TRUE — 1 RED**, `test_at_p02i[Node]` |
| "must be routed to a coercion site BY HAND and `_build_sidecar` extended" | read the `Document`-only call site and the hand-enumerated serialiser | **TRUE** |
| "0 RED of 643 (re-confirmation review, MEDIUM-1)" | attributed to that review; I re-ran one of the three at the new tip | **still 0, now of 647** |

**The over-claim is gone at all three sites the condition named.** `03-increments/increment-004.md`
§1.2 and `01-requirements.md` §7 AMD-2 both now say "every dataclass **`mapper.model` defines**" and
both carry the explicit "what it does not catch" sentence. The `test_at_p02i` docstring carries it
too — a fourth site the condition did not ask for.

## 3 · MEDIUM-1, second half — the class set. **DISCHARGED, and the derivation is real.**

Executed, whole tree, arm count asserted before every verdict:

| Mutation (by position/operation) | Arms | RED | The arms |
|---|---|---|---|
| the declared non-text map loses its entry for the census-position-1 class | 647 | **2** | `test_at_p02i[Node]`, `test_at_p02j` |
| the class derivation re-narrowed to exclude that class | **646** | **1** | `test_at_p02j` (and the `[Node]` arm vanishes — which is the point) |
| a brand-new dataclass appears in `mapper.model` | **648** | **1** | `test_at_p02j` |
| a neither-text-nor-str-map field on that class | 647 | **1** | `test_at_p02i[Node]` |

**`test_at_p02j` is killable in both directions of its own assertion** — the "missing" branch by
removing a declared entry or by adding a class to the module, the "stale" branch by narrowing the
walk. It is not a one-sided guard. The `assert derived` non-vacuity floor is covered by the same
evidence: narrowing the walk changes the collected arm count, so the walk is demonstrably live.

**`_EXPECTED_NON_TEXT`'s field sets are correct for all three newly-added classes.** Checked against
`mapper/model.py:58-98` field by field:

- `Node` — `id: str` classifies as text; `ficha: Ficha` is the only declaration. **Correct.**
- `Edge` — `parent_id`, `child_id`, `label` are all `str`; the empty tuple is **correct**.
- `Graph` — all six of `nodes`, `edges`, `root_id`, `schema`, `documents`, `load_warnings` are
  non-text, and `root_id: str | None` in particular does **not** classify under the spelled text
  predicate, so declaring it is right, not padding. **Correct, and complete** — `Graph` has exactly
  six fields.

Had any of the three been wrong, the class would have reddened on the pristine tree; it did not, and
the third assertion (`every == classified | declared`) is what would have caught it.

## 4 · MEDIUM-2 — the carried count. **DISCHARGED.**

`05-carries.md:40-44` no longer hands over a bare stale number. Measured: `548` is gone; the line now
reads "It is **643** at `d75f0fd`; at any later tip, measure it rather than trusting this sentence."
**That is TRUE as written** — it names the commit whose count it states, and instructs re-measurement
rather than copying. I considered whether stating 643 in a commit that collects 647 re-commits the
original sin and concluded it does not: the number is explicitly scoped to a named commit, which is
precisely what the original line failed to do. **Not a finding.**

The two new `05-carries.md` rows were re-measured at the new denominator rather than re-labelled:

| Carry row's claim | **Measured here** |
|---|---|
| a plain `str` field on `Node` reddens **0 of 647** | **0 RED of 647** — TRUE |
| the str-map collision keep-last vs keep-first reddens **0 of 647** | **0 RED of 647** — TRUE |

The author changed a denominator and the figure still holds under it. That is a re-run, not a
find-and-replace.

## 5 · The author's explicit NON-claim. **HONEST IN BOTH DIRECTIONS.**

The claim under test: a plain `str` field on `Node` still reddens nothing; the reason is that a `str`
field classifies as text so the guard passes *by design*, and it goes unseen one layer down because
`_derived_positions()` does not enumerate `Node` and `_build_sidecar` is hand-enumerated.

| Probe | Arms | RED | Reading |
|---|---|---|---|
| a plain text field on the census-position-1 class | 647 | **0** | the non-claim is TRUE — it still reddens nothing |
| **control:** the same field on a census-derived class | 650 | **2** | the new census position's `test_at_p02` arm and `test_tc_p01c` |

**The control is what makes this honest rather than a rationalisation.** If the reason were anything
other than the census's class enumeration, the control would have gone green too. It did not: the
identical field on a class the census *does* derive grows the census by three positions and reddens
two arms loudly. Read against source, the mechanism is exactly as stated —
`tests/test_repair_store_boundary.py:110-114` hard-codes `node.id` and then derives text fields
from `Ficha`, `Attachment`, `SchemaField` and `Document` only, and `mapper/store.py:289-322` writes a
fixed literal set of keys. Nothing is omitted from the author's account, and the gap is carried in
`05-carries.md` with the right owner (a save-path behaviour change, its own increment).

**Carrying this instead of claiming it fixed is the correct disposition**, and stating it inside the
very guard that does not catch it is better than stating it only in the packet.

---

## 6 · NEW findings — the third false claim, and two of its family

### NEW-1 — the claims-checker's own "HONEST SCOPE" rewrite states a figure disk refutes and its own next sentence contradicts. **[MEDIUM]**

`tests/test_repair_artifact_claims.py:78-88`, in the `_source()` docstring rewritten *in this commit
to discharge the framing nit*:

> What it does buy is real and small: `mapper/` carries **3** checkable citations across 2 of its 33
> files, and those are now checked instead of unread.

**Measured with the file's own two regexes over its own source corpus:**

```
source files                     : 33
keymap.py : path:line=[]                             ids=[test_keymap]
store.py  : path:line=[app.py:450, app.py:1179]      ids=[test_at_p02i]
TOTAL path:line citations        : 2
TOTAL distinct test identifiers  : 2
TOTAL checkable claims           : 4   across 2 of 33 files
```

**It is 4, not 3** — and three lines below, the *same docstring* says "the **four** citations
`mapper/` carries today all resolve" and then **enumerates all four by name**. So the file contradicts
itself within one docstring, and the false half is the half authored in this commit.

**Why this is the finding the brief predicted.** It is a false figure introduced by the correction of
a false figure, sitting in the file whose entire purpose is to catch false figures, inside a paragraph
whose first two words are "HONEST SCOPE". That is the third iteration of the pattern.

**Why it is a MEDIUM and not a HIGH, stated so it is not read as worse than it is.** It **under**-states
what the widening buys; it does not inflate it. No test is weakened, no conclusion depends on it, and
the honest half of the sentence ("the widening catches **none of** them") is TRUE and is the
load-bearing half. **Why not a LOW:** a self-contradicting count inside the claims checker leaves a
reader unable to decide which of two numbers in one docstring to believe, and the batch has already
graded this class at MEDIUM twice.

**Suggested fix — one token:** `3` to `4`. (Or, to remove the ambiguity the word "citations" is doing
in two senses here: "carries **4** checkable claims — 2 `path:line` citations and 2 `test_*`
identifiers — across 2 of its 33 files".)

### NEW-2 — `increment-004.md` §4 corrected its ledger to 647 and left two restatements of the old count behind. **[MEDIUM]**

Two lines in the file whose §4 table this commit corrected:

| Line | Says | The section it points at now says |
|---|---|---|
| `increment-004.md:244` | "The **643** above is the count **with** this file present." | the ledger three lines above reads **647** — there is no 643 above it any more |
| `increment-004.md:325` | evidence checklist: "Both lanes green, ledger reconciles — §4 — **626 + 17 = 643**" | §4 reads **630 passed**, **17 slow**, collected **647** |

Both are **internal contradictions within one file at one commit**, and both are the exact MEDIUM-2
shape — a count edited in one place, its restatement left standing — reproduced inside the commit
that discharges MEDIUM-2. Neither is marked historical; `:244` literally points upward at a number
that is no longer there, and `:325` cites a section that now disagrees with it.

**Suggested fix:** `643` to `647` at `:244`; `626 + 17 = 643` to `630 + 17 = 647` at `:325`.

**Explicitly NOT findings, and I checked each rather than assuming:** §4.1's table header "(of 643)",
`:256`'s "(548 / 643, matched)", and `:312`/`:314` all describe the HIGH-A mutation battery that
genuinely ran at `d75f0fd` against 643 arms. They are historical and **correct**. I decline to inflate
them.

### NEW-3 — the "40 arms" nit was fixed in the code and left standing in the packet. **[LOW]**

The re-confirmation's LOW-1 nit said the `_live_nodes` docstring's "40 arms" measured 41. The author
corrected it in `tests/test_repair_artifact_claims.py:129` (40 to 41) — and left the identical figure
at `increment-004.md:151` reading **40**. The two now disagree with each other.

**Measured:** `_live_nodes()` is consumed by `test_every_cited_test_identifier_exists` (**41** arms)
and by `test_the_checker_can_see_its_corpus` (1 arm) — 41 by the reviewer's own framing, 42 counting
the non-degeneracy arm. **40 is wrong on either reading.**

**Suggested fix:** `40` to `41` at `increment-004.md:151`.

### NEW-4 — the AMD-2 insertion left a run-on on an unwrapped line. **[LOW]**

`01-requirements.md:317`. The inserted sentence ends "...routing such a field is still a hand step."
and the pre-existing sentence resumes on the same physical line: "That guard protects a
**conclusion**...". The result is a ~180-character line in a file that otherwise wraps at ~100, and
"That guard" now reads as referring to the sentence just inserted rather than to `test_at_p02i`.
Readability and convention only; the content is correct. **Suggested fix:** break the line before
"That guard" and re-wrap.

---

## 7 · Clean — what I attacked that came back clean

1. **All three replacement docstrings are TRUE against disk**, clause by clause (§2) — including the
   one clause I expected to be loose ("no other round-tripped dataclass"), which is exact.
2. **The class derivation is genuinely derived** — it filters on `__module__`, so an imported
   dataclass cannot inflate it, and a newly-defined one cannot escape it (§3, 1 RED).
3. **`test_at_p02j` is killable in both branches of its assertion** (§3). Not a one-sided guard.
4. **`_EXPECTED_NON_TEXT`'s field sets are correct and complete for `Node`, `Edge` and `Graph`** (§3),
   checked field by field against `mapper/model.py`, not inferred from the green run.
5. **`test_at_p02i` grew from 4 to 7 arms and the three new ones are load-bearing** — the
   `[Node]` arm reddens on two independent mutations, and it **could not have reddened at all**
   before this fix, which is the concrete thing the discharge buys.
6. **The non-claim is honest, proven by a control the author did not build** (§5).
7. **Both `05-carries.md` figures were re-measured at the new denominator, not re-labelled** (§4).
8. **No regression.** Both lanes exit 0 at the expected counts; the pristine tree has **0** pre-red
   arms of 647; ruff is at the 29-error whole-tree baseline and clean on all three touched files.
9. **The ledger reconciles exactly** — `647 = 548 + 16 + 83`, boundary file measured at **100**,
   claims file at **83**, `test_at_p02i` at **7** and `test_at_p02j` at **1**.
10. **`05-carries.md:44` is not a repeat of MEDIUM-2** — I checked it specifically and it is true as
    written, because it names the commit its number belongs to. Declined as a finding.

## 8 · What I could not verify

- **I did not re-review HIGH-A.** The brief scoped it out and the prior pass cleared it; I re-ran the
  lanes and the pristine tree only to confirm nothing regressed.
- **I did not re-measure LOW-2's timing figures** (`0.8 µs` / `348.5 µs` / `~430x`) now carried into
  `05-carries.md:149`. They are the previous reviewer's own numbers, restated; taken on report.
- **I did not exercise the save side of a new `dict[str, str]` field**, for the same reason the prior
  pass could not: `_build_sidecar` is hand-enumerated. My MEDIUM-1 evidence is read-side.
- **I did not mutate the class walk to return empty**, so the `assert derived` floor is not directly
  killed. Narrowing the walk (§3) demonstrates it is live, which I judge sufficient; a reviewer
  wanting the floor itself pinned should say so.
- **`state.json`, the security review, and QA's other MEDIUM/LOW carries remain out of scope.** I
  re-checked none of them.
- **I did not re-verify `_source()`'s enumerated four citations resolve** beyond counting them; the
  suite's own 83 arms assert that and they are green.

## 9 · What blocks, and what does not

**Nothing blocks on correctness.** Both conditions are discharged, the second more strongly than
asked; the two new guards are real and killable; the non-claim is honest and carried with the right
owner; no shipped behaviour changed and no arm regressed.

**Conditions before merge — four edited lines, no code change:**

1. **NEW-1** — `3` to `4` in `tests/test_repair_artifact_claims.py`'s `_source()` docstring, so it
   stops contradicting its own next sentence.
2. **NEW-2** — `643` to `647` at `increment-004.md:244`; `626 + 17 = 643` to `630 + 17 = 647` at
   `increment-004.md:325`.

**Carry:** NEW-3 (`40` to `41` at `increment-004.md:151`), NEW-4 (re-wrap `01-requirements.md:317`),
and the prior pass's LOW-2 and LOW-3, which this commit correctly recorded rather than fixed.

**One observation, recorded and deliberately NOT inflated into a finding.** `05-carries.md:147` says
"The census, the coercion and the guard's class set are all derived now; **the SAVE shape is not.**"
The census is derived *within* the four classes it feeds on, but *which four classes* feed it is
itself a hand list (`tests/test_repair_store_boundary.py:110-114`) — and that hand list is the direct
cause of the 0-RED result the same table cell reports. The cell **discloses the mechanism explicitly
in its own next clause**, so no reader is misled, and the structure is pre-existing rather than
introduced by this diff. It is the natural next rung if anyone closes the save-shape carry.

## 10 · Evidence checklist

| Item | Mark | Executed evidence |
|---|---|---|
| Prior re-confirmation verdict read in full first | OK | `04-qa-adversarial.md:1028-1210`, both conditions and all three LOWs |
| Diff read in full | OK | `d75f0fd..a5db8df`: 7 files, +490/-36; `mapper/store.py` +12/-4, both test files, four records |
| Expected arm count asserted before any verdict | OK | pristine **647**, 0 pre-red; every mutation reports its own resolved count, deltas explained |
| Both lanes and ruff re-derived, not copied | OK | 630/17 in 55.8s · 17/630 in 22.9s · ruff 29 whole-tree, clean on the three touched files |
| Ledger re-derived | OK | `647 = 548 + 16 + 83`; boundary **100**, claims **83**, p02i **7**, p02j **1** |
| MEDIUM-1 first half checked clause by clause against disk | OK | §2 — six clauses, each separately verified; str-map probe **0 RED of 647** |
| The other two over-claim sites checked | OK | §2 — `increment-004.md` §1.2 and `01-requirements.md` §7 AMD-2 both corrected; a fourth site added |
| MEDIUM-1 second half: derivation proven REAL | OK | §3 — re-narrowed **1 RED**, new dataclass **1 RED**, declared entry removed **2 RED** |
| `test_at_p02j` shown killable in BOTH assertion branches | OK | §3 — "missing" branch 2 ways, "stale" branch 1 way |
| `_EXPECTED_NON_TEXT` field sets checked for the 3 new classes | OK | §3 — field by field against `mapper/model.py:58-98`; `Graph` complete at 6 |
| MEDIUM-2 checked against disk | OK | §4 — `548` gone; the replacement is true and commit-scoped; both new carry rows re-measured at 647 |
| The NON-claim verified in BOTH directions | OK | §5 — **0 RED of 647**, plus a CONTROL at **2 RED of 650** proving the stated reason is the real one |
| The author's stated reason read in source, not inferred | OK | §5 — `test_repair_store_boundary.py:110-114` and `mapper/store.py:289-322` |
| A third fresh false claim hunted for, per the brief | **FOUND — 3, one MEDIUM in the claims checker itself** | §6 NEW-1 (3 vs measured 4), NEW-2 (two stale restatements), NEW-3 (half-fixed nit) |
| Historical figures checked before being called stale | OK | §6 — §4.1, `:256`, `:312`, `:314` and `05-carries.md:44` all verified CORRECT and declined |
| Every new finding carries a recommended fix | OK | §6 — one token each for NEW-1/2/3, a re-wrap for NEW-4 |
| Clean categories reported as clean, not padded | OK | §7 — 10 categories; §9's census observation explicitly declined as a finding |
| Every substitution asserted exactly 1 hit | OK | harness asserts a hit count of exactly 1 and raises otherwise; 8 mutations, 8 assertions |
| Bytecode cache neutralised | OK | `PYTHONDONTWRITEBYTECODE=1` on every mutation run |
| Every mutation restored, proven by sha256 | OK | 4 files back to `3d39a861…` / `637d537e…` / `87402d1d…` / `a30deb52…`, matching the pre-mutation baseline |
| Mutations described by position, not spelled | OK | §2-§5 name position and operation only |
| No repo file edited but this one; no git mutation | OK | lab `diff -r` vs a fresh `git archive a5db8df`: **no differences** in any tracked file; `git status --porcelain` empty |

---

# Final verification (bef1d69)

**Reviewer:** `code-reviewer`, independent final pass. Not the author; not the QA reviewer who raised
HIGH-1; not the confirmation reviewer who raised HIGH-A; not the re-confirmation reviewer who raised
MEDIUM-1/MEDIUM-2; not the condition-discharge reviewer who raised NEW-1..NEW-4.
**Target:** branch `fix/repair-batch-02`, commit **`bef1d69`**, PR #3, diff `a5db8df..bef1d69`.
**Scope, deliberately narrow:** are NEW-1..NEW-4 discharged, did the sweep's own edits introduce
anything false, and does an independently-run numeric sweep find any live false figure. HIGH-A, the
arms and the class-set derivation were **not** re-reviewed; three passes cleared them.
**Date:** 2026-08-27
**Posture:** every figure below was executed in this session. Historical columns were re-derived from
detached `git archive` copies of `01d7578`, `d75f0fd` and `a5db8df` in my own scratchpad,
`PYTHONDONTWRITEBYTECODE=1`; the tip was measured in the worktree read-only. **No mutation work was
needed and none was done** — this diff changes no logic. No repo file was edited but this one;
`git status --porcelain` is empty at close.

## Verdict — **CLEAR TO MERGE.** No HIGH. All four conditions discharged and true against disk.

The sweep's own edits are the cleanest correction this batch has produced: **the streak of a false
figure inside the correction of a false figure is broken on the numbers.** Every cell of the rewritten
three-column post-fix table is true for the commit its column names — I re-derived all twelve measured
cells from archive copies rather than reading them. Rows 1–13 of the false-record enumeration are
accurate, the `mapper/store.py:98-130` citation is exact to the line, and both "reviewer-measured"
attributions are correct.

**Four new record-truth items remain, all prose, all one line, none blocking.** The streak is broken
on figures but not entirely on *restatements*: growing the enumeration from 6 rows to 13 left the
sentence beneath it still saying "3 of the 6" (FV-1) — the identical shape as NEW-2, one level up.
None of the four touches behaviour, weakens a test, or inflates any claim.

---

## 1 · Numbers — re-derived, not copied

| Figure | Packet claims | **Measured here (tip `bef1d69`)** |
|---|---|---|
| collected | 647 | **647** |
| fast lane | 630 passed / 17 deselected | **630 passed, 17 deselected**, 57.2s, exit 0 |
| slow lane | 17 passed / 630 deselected | **17 passed, 630 deselected**, 23.8s, exit 0 |
| `ruff check mapper/ tests/` | 29 | **Found 29 errors** |
| ruff on the touched file | clean | **All checks passed!** |
| boundary file | 100 | **100** |
| artifact-claims file | 83 | **83** |
| ledger `647 = 548 + 16 + 83` | asserted | **exact** — `p02g` **6** · `p02h` **2** · `p02i` **7** · `p02j` **1** = 16; new arms alone **16 passed** |
| corpus | 8 authored + 33 source = 41 | **8 / 33 / 41** |
| census positions | 21 | **21** (`_derived_positions()` evaluated) |
| dataclasses in `mapper.model` | 7 | **7** |

## 2 · The four conditions — each verified against disk

### NEW-1 — **DISCHARGED, and the new figure is the measured one.**

`tests/test_repair_artifact_claims.py:87` now reads "`mapper/` carries **4** checkable citations
across 2 of its 33 files". Re-derived with the file's **own two regexes** over its **own** `_source()`
corpus, not copied from the prior review:

```
source files                     : 33
keymap.py : path:line=[]                            ids=['test_keymap']
store.py  : path:line=['app.py:450','app.py:1179']  ids=['test_at_p02i']
TOTAL path:line citations        : 2
TOTAL distinct test identifiers  : 2
TOTAL checkable claims           : 4   across 2 of 33 files
```

**4 is correct**, and the docstring now agrees with its own next sentence ("the four citations
`mapper/` carries today all resolve"), which enumerates the same four. The self-contradiction is gone.

### NEW-2 — **DISCHARGED at both sites.**

| Line | Now reads | Verified |
|---|---|---|
| `increment-004.md:244` | "The **647** above is the count **with** this file present." | the ledger three lines above reads **647** — the pointer resolves |
| `increment-004.md:325` | "Both lanes green, ledger reconciles — §4 — **630 + 17 = 647**" | §4 reads 630 fast / 17 slow / 647 collected; `630 + 17 = 647` is arithmetically and empirically exact |

I re-checked the figures the prior pass **declined** to change, and it was right to decline: §4.1's
"(of 643)", `:256`'s "(548 / 643, matched)" and `:312`/`:314` all describe the HIGH-A battery that ran
at `d75f0fd`, where the tree genuinely collected **643** (archive-verified below). Historical and
correct. They were left alone. Same for `01-requirements.md:316` ("all 643 arms", attributed to the
re-confirmation review) and `05-carries.md:42-44` (explicitly commit-scoped to `d75f0fd`).

### NEW-3 — **DISCHARGED, and 41 is the right number.**

`increment-004.md:151` now reads **41 arms**, matching `tests/test_repair_artifact_claims.py:129`.
Re-derived: `_corpus()` = 8 authored artifacts + 33 `mapper/` source files = **41**, so
`test_every_cited_test_identifier_exists` has **41** arms. The two figures now agree and both are true.

### NEW-4 — **DISCHARGED, and better than the condition asked.**

`01-requirements.md:317-321`. The run-on is broken into its own paragraph, and the author went past
the readability fix: the ambiguous **"That guard"** is replaced by the explicit **"`test_at_p02i`"**,
which removes the mis-binding the finding described rather than only re-wrapping it. Measured: the
region now wraps at 88–105 chars (the ~180-char line is gone). *(The file's 431-char maximum is a
pre-existing table row at `:51`, outside this diff.)*

## 3 · The sweep's own edits — the part that mattered

### 3.1 · The three-column post-fix table (`04-gate-findings-disposition.md:134-138`). **EVERY CELL TRUE.**

I re-derived each column from a detached `git archive` of the commit that column names — not from the
packet, and not from the prior reviewers:

| Cell | Column claims | **Archive-measured** |
|---|---|---|
| `01d7578` fast / slow / collected | 531/17 · 17/531 · 548 | **531/17 · 17/531 · 548** |
| `01d7578` ledger `548 = 429 + 119` | asserted | **exact** (429 base from `01-requirements.md:12`, 413+16) |
| `d75f0fd` fast / slow / collected | 626/17 · 17/626 · 643 | **626/17 · 17/626 · 643** |
| `d75f0fd` ledger `643 = 548 + 12 + 83` | asserted | **exact** — boundary file **96** (84+12), claims file **83** |
| `a5db8df` fast / slow / collected | 630/17 · 17/630 · 647 | **630/17 · 17/630 · 647** |
| `a5db8df` ledger `647 = 548 + 16 + 83` | asserted | **exact** — boundary file **100**, claims file **83** |
| ruff, all three columns | 29 / 29 / 29 | **Found 29 errors** at each of the three commits, and **29** at the tip |

**The two mutation cells check out against the records they summarise.** `d75f0fd`'s "+4 (`MX1`,
`MX2`, `MX11`, `MX3`): 0 → 6 / 6 / 6 / 2" reproduces `increment-004.md:248-252` exactly, and the arm
counts it names are live today (`p02g` **6** arms, `p02h` **2**). `a5db8df`'s "+4 more on the derived
class set: 2 / 1 / 1 RED, and one deliberate 0 carried as an open gap" is an exact summary of the
author's own §1.7 counterfactual — four mutations at **2 / 1 / 1 / 0**, the 0 being the plain `str`
field on `Node`, and the cell **labels that 0 as a carried gap rather than folding it into the RED
tally**. That is the honest rendering.

**The "Final" column names `a5db8df`, not the tip.** Deliberate and correct — it names the commit its
numbers belong to, which is exactly the discipline MEDIUM-2 demanded. I verified the figures also hold
at `bef1d69` (§1), so nothing is stale; the label is precise, not evasive.

### 3.2 · The rows 1–13 enumeration (`05-carries.md:92-106`). **ACCURATE, and the citation is exact.**

- **Row 5's `mapper/store.py:98-130`** — verified to the line: `_str_map_fields` is defined at `:97`,
  its docstring opens at **`:98`** and its closing `"""` is at **`:130`**. The old `98-119` was
  genuinely stale (the docstring grew when MEDIUM-1's rewrite landed) and the replacement is exact.
  `mapper/store.py` is untouched between `a5db8df` and `bef1d69`, so the citation was stale at
  `a5db8df` and is correct now.
- **Rows 1–6** unchanged and still true. **Row 7** (`test_at_p02i` named as a gate it is not) sits in
  the `mapper/store.py` docstring — correct. **Row 8** (4 classes named, 7 defined) — `mapper.model`
  defines exactly **7** dataclasses, verified. **Rows 9, 11, 12, 13** name the right files.
- **Row 10** — "*3 checkable citations* where disk says 4" in `tests/test_repair_artifact_claims.py`:
  correct, and independently re-derived in §2.
- **Row 12** — "this table's own post-fix figures, stale one commit after being written": **TRUE**. The
  two-column table was written at `d75f0fd` carrying 643/626 and the very next commit collected 647.

**Both "reviewer-measured" attributions are accurate.** `05-carries.md:174` (`0.8 µs → 348.5 µs`) is
the re-confirmation reviewer's LOW-2 figure, explicitly *not* re-derived by the condition-discharge
pass (§8 of that review says so) — the tag states exactly that provenance. `05-carries.md:175`
(keep-last vs keep-first, **0 of 647**) was measured by the condition-discharge reviewer (§4 of that
review: "Measured here: 0 RED of 647 — TRUE"), so "reviewer-measured" is the correct attribution.
Note the discrimination: the adjacent `_build_sidecar` row's **0 of 647** carries **no** such tag,
because the author measured that one himself (`increment-004.md` §1.7). The tags are applied where
they belong and withheld where they do not.

### 3.3 · Everything else numeric in the diff

The `_build_sidecar` carry's rewrite is a **strengthening**, not a claim: it retracts "the census …
is derived now" in favour of "the census is derived **within** the classes it walks — but which
classes it walks is itself a hand list". I read `_derived_positions()`
(`tests/test_repair_store_boundary.py:103-124`): it hard-codes `node.id`, `fields.key`, `fields.value`
and then walks `Ficha`/`Attachment`/`SchemaField`/`Document` by name. **The retraction is true and the
previous wording was the looser one.** This is the condition-discharge review's §9 observation —
recorded there and explicitly *declined* as a finding — closed anyway. Correct disposition.

## 4 · My own sweep — every live figure in the authored artifacts

Run independently over `.dev-flow/2026-08-27-repair-batch-02/**.md` with the reviewer-authored files
excluded by the same rule the checker uses (`0*-review` / `0*-qa-*` / `0*-security-*` / `*code-review*`).
Every occurrence of every count was printed with its line and judged one by one.

**No false live figure found in the authored artifacts.** Specifically re-derived and confirmed:
647 · 630 · 17 · 29 · 100 · 96 · 84 · 83 · 41 · 33 · 21 · 16 · 12 · 8 · 7 · 6 · 2, plus the ledger
identities `429+119=548`, `548+12+83=643`, `548+16+83=647`, `548+99=647`, `6+2+7+1=16`, `1+41×2=83`,
`630+17=647`. Historical figures (548, 643, 626, 531, 429, `12 of 17`, `17→21`) are each attributed to
the commit or review that measured them; I checked the attributions rather than the numbers alone.
Source-level spot checks also hold: `model.py:82-83` is `Document.tags`/`inherited`;
`grep -rn "logging\." mapper/` returns **zero hits**.

## 5 · NEW findings — four, all record-truth, none blocking

### FV-1 — growing the enumeration from 6 rows to 13 left "3 of the 6" standing beneath it. **[MEDIUM]**

`05-carries.md:108`, the sentence immediately under the table this commit extended:

> **Note where they live: 3 of the 6 are COMMENTS in `mapper/`, not lines in `.dev-flow/`.**

The table above it now has **13** rows. "The 6" no longer points at anything on the page — the
paragraph three lines earlier explicitly speaks of "rows 7 through 13". **Measured against the table
as it now stands:** 4 of the 13 are `mapper/` comments or docstrings (rows 1, 2, 5, 7), 7 are
`.dev-flow/` lines (3, 4, 6, 9, 11, 12, 13), and **2 live in `tests/` (rows 8 and 10)**.

**This is exactly NEW-2's shape one level up** — a count edited in one place with its restatement left
standing — reproduced inside the commit that discharges NEW-2. It is *arithmetically* still true of
rows 1–6, which is why it reads as harmless; but the referent is dangling and the note now under-counts
the enumeration it annotates.

**The second-order point is the more useful one.** The note's argument is that the checker "was
structurally unable to see half the corpus" and that this was "**Fixed at close-out**: the corpus now
includes `mapper/**/*.py`". Under the 13-row table that repair is **incomplete**: rows 8 and 10 live in
`tests/`, and `_source()` returns `sorted((REPO / "mapper").rglob("*.py"))` — `tests/` is **not** in the
corpus. Two of the thirteen recorded false records sit in a directory the widened checker still cannot
read.

**Suggested fix — one sentence:** "**Note where they live: 4 of the 13 are comments or docstrings in
`mapper/`, 2 are in `tests/`, and 7 are `.dev-flow/` lines.**" and append to the "Fixed at close-out"
clause: "— `tests/` is still outside the corpus, which is where rows 8 and 10 live."

### FV-2 — a live stale figure in the claims checker itself, which the sweep's scope cannot see. **[LOW]**

`tests/test_repair_artifact_claims.py:151`:

> `# MEASURED, not guessed: the authored set carries 8 such citations today.`

**Re-derived with the file's own `_CITATION` regex over its own `_authored()` set: 10, not 8.** Traced
through history: **8 at `01d7578`** (correct when written), **10 at `d75f0fd`**, and 10 ever since —
`increment-004.md` and `05-carries.md` each added one when they landed. Stale for three commits.

Nothing breaks: the assertion beneath it is a floor (`>= 5`) and it holds. Two adjacent measured
comments in the same function are **correct** — "Measured today: 2 of each" for the source half is
exactly right (2 `path:line`, 2 `test_*`).

**Why it is worth a line rather than silence.** The sweep as recorded in `05-carries.md:87-88` scans
"every live figure, **every authored artifact**". Six of the thirteen enumerated false records live in
source files, not artifacts — which is the batch's own central lesson (FV-1) — so the instrument
proposed as the remedy reproduces the blind spot the batch spent four rounds identifying, and this is
the figure that proves it.

**Suggested fix:** `8` to `10`, and add `tests/**/*.py` and `mapper/**/*.py` to the sweep's stated
scope in `05-carries.md`.

### FV-3 — the sweep recipe is labelled "every live figure" and is not total. **[LOW]**

`05-carries.md:87-88`. `LIVE = {647, 630, 643, 626, 548, 531, 429, 100, 96, 83, 41, 40, 16, 12}` under
the comment "every live figure, every authored artifact". It omits live figures that are checkable and
decay the same way — **84** (`increment-004.md:241`, boundary at base), **21** (the census, in two
files), **17**, **33** — and it retains **40**, which this very commit corrected to 41 and which is no
longer live anywhere.

**No present falsehood follows from it**: I measured 84, 21, 17 and 33 and all four are currently
correct. The cost is forward-looking — a next session that runs the set as written performs a sweep
narrower than the totality its own comment claims. A totality claim that is not total is this batch's
signature defect, and it should not be the closing instrument of the artifact that names it.

**Suggested fix:** add `84, 21, 17, 33`, drop `40`, or re-label the comment "the count figures most at
risk" instead of "every live figure".

### FV-4 — row 13 describes itself as carrying the citation that row 5 carries. **[LOW]**

`05-carries.md:106`: "*this very row's line citation, stale after the docstring it points at grew*".
Row 13 carries no line citation; the stale `mapper/store.py:98-119` was **row 5's**. The prose above
the table gets it right ("Row 13 is this table's own citation"), and the `Where` column (`05-carries.md`)
is correct, so no reader is misled about *what* was stale — only about which row held it.

**Suggested fix:** "row 5's line citation, stale after the docstring it points at grew".

## 6 · Clean — what I attacked that came back clean

1. **All four conditions are genuinely discharged**, each verified against disk rather than read (§2);
   NEW-4 was discharged past what the condition asked.
2. **Every measured cell of the three-column post-fix table is true for the commit its column names**,
   re-derived from three archive copies (§3.1). Twelve cells, twelve matches.
3. **The `mapper/store.py:98-130` citation is exact to the line** (§3.2), and its staleness at
   `a5db8df` was real.
4. **Rows 1–13 are each accurate** in shape, location and attribution (§3.2).
5. **Both "reviewer-measured" tags are correct**, and — the discriminating check — the adjacent
   author-measured figure correctly does **not** carry one (§3.2).
6. **No false live figure anywhere in the authored artifacts** (§4). Seventeen distinct figures and
   seven ledger identities re-derived.
7. **Historical figures are attributed, not laundered.** Every 643/548/626/531 I found names the commit
   or review that measured it. The prior pass's declined items were declined correctly.
8. **The `_build_sidecar` carry's rewrite is a retraction toward the truth**, verified against
   `_derived_positions()` in source (§3.3) — it closes the observation the prior review explicitly
   declined to file.
9. **No regression.** 630/17 and 17/630 both exit 0; ruff at the 29-error baseline whole-tree and clean
   on the touched file; the sole code change in the diff is one docstring token (`3` to `4`).
10. **The streak is broken on numbers.** Four prior rounds each produced a false *figure* inside a
    correction; this one produced none. FV-1 is a stale *restatement*, not a stale measurement.

## 7 · What I could not verify

- **I did not re-review HIGH-A, the arms, or the class-set derivation.** The brief scoped them out and
  three passes cleared them; I re-ran both lanes only to confirm nothing regressed.
- **I ran no mutations.** This diff changes no logic, so a counterfactual battery would measure the
  previous commit, not this one. The `a5db8df` mutation figures in §3.1 are checked for *fidelity to
  the records they summarise*, not re-executed.
- **I did not re-measure the timing figures** (`0.8 µs` / `348.5 µs` / `~430x`). They are correctly
  tagged as taken on report, which is the honest disposition.
- **`state.json`, `04-security-review.md`, and the reviewer-authored artifacts remain out of scope**,
  as the checker's own exclusion rule requires.
- **The 24-mutant figure in the `01d7578` column** is an aggregate from earlier increments; I checked
  its consistency with the packet, not by re-running 24 mutants.

## 8 · What blocks, and what does not

**Nothing blocks.** No HIGH. All four conditions are discharged and true against disk; the sweep's own
edits introduced no false figure — the first round in five of which that can be said; no behaviour
changed, no arm regressed, no test was weakened, and the only code edit in the diff is a single
docstring token that made a self-contradicting docstring consistent.

**CLEAR TO MERGE.** FV-1 through FV-4 are prose corrections totalling four edited lines. **My
recommendation is to land them before merge if a fifth round is cheap, and to merge regardless if it is
not** — this batch has paid for four rounds, and holding a documentation-only diff on a dangling
definite article would cost more than it buys. If they are deferred, FV-1 and FV-2 should be carried in
`05-carries.md` rather than dropped, because both point at the same live structural gap: **`tests/` is
still outside the claims checker's corpus, and 2 of the 13 recorded false records live there.** That is
the honest next rung, and it is a bigger prize than any of the four lines.

## 9 · Evidence checklist

| Item | Mark | Executed evidence |
|---|---|---|
| Prior condition-discharge verdict read in full first | OK | `04-qa-adversarial.md:1368-1692`, all four NEW findings and §8's non-verifications |
| Diff read in full | OK | `a5db8df..bef1d69`: 6 files, +386/-20; every hunk of all six read |
| NEW-1 re-derived with the file's OWN two regexes | OK | §2 — 33 source files, 2 `path:line` + 2 `test_*` = **4 across 2 files**; docstring now says 4 |
| NEW-2 verified at both named lines | OK | §2 — `:244` **647** resolves upward; `:325` **630 + 17 = 647** exact |
| NEW-3 re-derived, not copied | OK | §2 — `_corpus()` = 8 + 33 = **41** arms; packet and docstring now agree |
| NEW-4 verified by measurement | OK | §2 — region wraps 88–105 chars; "That guard" replaced by explicit `test_at_p02i` |
| Post-fix table checked cell by cell against the commit each column names | OK | §3.1 — three `git archive` copies; 531/548, 626/643, 630/647, ruff 29×3, all matched |
| Rows 1–13 checked individually | OK | §3.2 — locations, attributions, and row 12's staleness claim all verified |
| `mapper/store.py:98-130` citation verified to the line | OK | §3.2 — docstring opens `:98`, closes `:130`; exact |
| Both "reviewer-measured" attributions traced to their source | OK | §3.2 — LOW-2 and condition-discharge §4; the untagged adjacent figure correctly untagged |
| Independent numeric sweep run over the authored artifacts | OK | §4 — 17 figures + 7 ledger identities re-derived; **no false live figure found** |
| Historical figures checked before being called stale | OK | §2, §4 — §4.1, `:256`, `:312`, `:314`, `01-requirements.md:316`, `05-carries.md:42-44` all correct, declined |
| Fresh false claims hunted for inside the correction | **FOUND — 4, one MEDIUM, all prose** | §5 — FV-1 (stale restatement), FV-2 (stale figure in source), FV-3 (non-total totality), FV-4 (self-reference) |
| Every new finding carries a recommended fix | OK | §5 — one sentence or one token each |
| Both lanes and ruff re-derived at the tip | OK | §1 — 630/17 in 57.2s · 17/630 in 23.8s · ruff **29**, clean on the touched file |
| Ledger re-derived | OK | §1 — `647 = 548 + 16 + 83`; boundary **100**, claims **83**, `p02g` 6 · `p02h` 2 · `p02i` 7 · `p02j` 1 |
| Clean categories reported as clean, not padded | OK | §6 — 10 categories; §7 states five things I did not verify |
| No mutation work performed on a docs-only diff | OK | §7 — none needed; archive copies read-only, tip read-only |
| No repo file edited but this one; no git mutation | OK | `git status --porcelain` **empty** at open and at close; HEAD still `bef1d69` |
