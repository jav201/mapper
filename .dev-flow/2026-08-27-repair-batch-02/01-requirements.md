# 01 — Requirements · `2026-08-27-repair-batch-02`

> **Scope: exactly the four shipped defects the `ui-next-batch-02` PDR second pass found, under
> that batch's standing rule — _this batch repairs exactly what its own stories make newly
> reachable, and nothing more._** Interposed by operator decision at the feature batch's PDR gate,
> on the precedent of `2026-08-26-repair-batch`. Artifact language: **English**; UI strings
> **Spanish**.

**Base ref (RC-1):** `d8777840313145fec341687f0081afd7230c755b` = `HEAD` = `origin/master` =
merge-base. Verified clean by `git fetch origin` before any derivation.

**Baseline suite:** **429 collected** — fast lane 413 passed / 16 deselected, slow lane 16 passed /
413 deselected, both exit 0. `ruff check mapper/ tests/` = **29** (pre-existing). Every figure
executed in this session, read from its own captured output (C-19 / C-25).

---

## 1 · Why this batch exists

The feature batch `2026-08-26-ui-next-batch-02` was REJECTED at its PDR second pass with twelve
blockers. **Four of them are not requirement defects — they are shipped defects on `master`, and
no amount of requirements folding fixes them.** They are lifted here so the feature batch's
amendment set 3 can shrink to genuine requirement work.

The ordering argument is the load-bearing one: **`US-N13`'s «sala» loads every map in the workspace
on mount.** A map carrying a non-string in any text position therefore reaches consumers *without
the operator opening anything*. The store boundary must be sound **before** that story ships, not
alongside it.

**Explicitly OUT of this batch — parked by operator rider:** `S-18` (the mount work-budget /
deadline mechanism). It is a design item for the feature batch's PDR, which already carries the
pre-authorised A3 change to the renderer contract; the deadline hook belongs in that redesign,
**designed once, not patched into three private copies of the walk**. This batch may land the
honest 51-node measurement fixture and nothing more.

---

## 2 · Premise table (C-43)

Executed against `d877784` in this session. **Citing a document is not evidence.**

| # | Premise | Tier | Verdict | Executed evidence |
|---|---|---|---|---|
| P-1 | `S-02` is **live**: the repair batch's `_coerce_field` does not cover every file-derived text position | premise | ✅ **TRUE** | `grep -n "_coerce_field" mapper/store.py` → definition at `:39`, applied at **exactly two sites**, `:235` and `:239`. Boundary census below: **12 of 17** positions leak a non-`str`. |
| P-2 | `LLR-STO.1.1` — the requirement `C-2` and `C-3` depend on — **does not exist** | premise | ✅ **TRUE** | `grep -n "LLR-STO\.1\.1" .dev-flow/2026-08-26-ui-next-batch-02/*.md` → **24 occurrences, every one prose; `grep "^#\+ .*LLR-STO"` returns nothing.** |
| P-3 | `MapStore.load` leaks non-`MapStoreError` exception types on hostile input (`S-11`) | premise | ✅ **TRUE** | Boundary census: a container poison yields `sqlite3.ProgrammingError` ×3 and `TypeError` ×1 **from `load` itself**. |
| P-4 | `docs/ARCHITECTURE.md` was never amended, though `PLAN.md` §7 records ARQ as approved with the map amended | premise | ✅ **TRUE** | Live map `:58` and `:136` still declare `IRenderer.render(graph, selected_id, w, h, **kwargs) -> Text`, marked **frozen: yes**; `R-010` still reads *"stays frozen through this batch"*. No `ViewState`, no `Protocol`, no `runtime_checkable`. |
| P-5 | The repo has **no** byte-identity goldens (trigger `B3`'s recorded non-activation) | premise | ❌ **FALSE** | The probe `ls tests/goldens` → no such directory is **correct as executed**, but its **input set was wrong** (C-31). `tests/test_repair_depth.py:93` declares `MASTER_LEGACY_DIGESTS`; derived count **12** pins = 3 renderers × 4 `GOLDEN_SIZES`. |
| P-6 | `RadialRenderer` is among the pinned renderers, so the feature batch's Inc-1 reddens pins **by construction** | premise | ✅ **TRUE** | Derived: `renderers pinned: ['LayeredRenderer','OutlineRenderer','RadialRenderer']`; sizes `(80,24) (140,8) (140,45) (300,120)`. Inc-1's job is to make `Canvas.rows()` honour `dots`/`bgs`, which is exactly what `RadialRenderer` paints. |
| P-7 | The coercion position set can be **derived** rather than hand-listed | premise | ✅ **TRUE** | `MapStore._build_sidecar` (`store.py:156-189`) is the serialiser's own declaration of every round-tripped position, and the sqlite DDL (`store.py:116-149`) independently declares the same columns as `TEXT`. Two independent derivations of one set. |
| P-8 | *"No consumer raises"* is an unsound threshold for this defect | premise | ✅ **TRUE — measured** | `Graph.search_hits` joins `a.caption or a.path` (`model.py`), so a poisoned `path` is observable **only when `caption` is falsy**. Two of my own probes disagreed until this was found; the divergence is the short-circuit, not an error. **Observability is data-dependent, so the threshold must be type-at-the-boundary.** |

### 2.1 · The derived boundary census — this batch's central measurement

Input set derived from `_build_sidecar`'s written shape, **not hand-listed** (C-31). Poisoned with
both a faithfully-coercible scalar (`int`) and a container (`dict`). Positive control first, because
a probe that cannot report a non-absence proves nothing (C-55 rider).

```
POSITIVE CONTROL — clean map: 22 text positions checked, non-str = NONE

position poisoned      int -> non-str at boundary     dict -> non-str at boundary
------------------------------------------------------------------------------------------
node.id                LEAKS: node.id                 clean
node.title             clean                          clean
node.state             clean                          clean
node.meta              clean                          clean
node.notes             clean                          clean
fields.key             LEAKS: fields.key              clean
fields.value           clean                          clean
attachment.kind        LEAKS: attachment.kind         LOAD-LEAK ProgrammingError
attachment.path        LEAKS: attachment.path         LOAD-LEAK ProgrammingError
attachment.caption     LEAKS: attachment.caption      LOAD-LEAK ProgrammingError
schema.key             LEAKS: schema.key              LEAKS: schema.key
schema.label           LEAKS: schema.label            LEAKS: schema.label
schema.kind            LEAKS: schema.kind             LEAKS: schema.kind
document.name          LEAKS: document.name           LOAD-LEAK TypeError
document.source        LEAKS: document.source         LEAKS: document.source
document.path          LEAKS: document.path           LEAKS: document.path
document.kind          LEAKS: document.kind           LEAKS: document.kind
------------------------------------------------------------------------------------------
positions leaking a non-str past the boundary:  int=12  dict=6  of 17
```

**Two corrections to the record this census forces.**

1. **The "5 families / 3 raw" figure carried by `02e` is itself hand-listed and short.** The
   serialiser writes a **sixth** family nobody enumerated — `documents[]` (`name`, `source`, `path`,
   `kind`) — and **field _keys_** are used raw while only their values are coerced. The honest unit
   is **positions (17)**, not families.
2. **`D18` of the feature batch is WRONG.** Its `SATISFIED-EXTERNALLY` strike of `S-02` is
   withdrawn by this batch's `§4` amendment record, not silently.

---

## 3 · Requirements

### 3.1 · `HLR-STO.1` — the store boundary returns text where text is promised

> **`MapStore.load` shall return a `Graph` in which every position that `_build_sidecar` serialises
> as text is an instance of `str`.**

- **Traceability:** feature-batch `S-02` / security condition `C-2`; makes `LLR-N13.1.5`'s
  containment stand on something.
- **Acceptance tests:** `AT-P01`, `AT-P02`, `AT-P03`.
- **Method:** test (unit + boundary).

**Why the threshold is type-at-the-boundary and not consumer behaviour.** Premise P-8: observability
is data-dependent (`caption or path`). A predicate keyed on *"`search_hits` does not raise"* passes
or fails on a sibling field's truthiness, which means it is **invariant under the change it gates**
for half its input space — C-40 limb 1. Putting `MapStore.load`'s own output in the predicate is
what makes it a gate rather than a coincidence.

##### `LLR-STO.1.1` — every serialised text position is coerced *(the requirement that did not exist)*

> **`MapStore.load` shall apply the scalar-coercion ladder to every text position enumerated by
> `MapStore._build_sidecar`, and shall raise only `MapStoreError` for any input it rejects.**

- **Traceability:** `HLR-STO.1`; security conditions `C-2`, `C-12`; finding `S-11`.
- **Position set — DERIVED, never hand-listed (C-31):** the set is computed by walking
  `_build_sidecar`'s output shape. A test that hand-lists positions is rejected: the hand-listed
  count was wrong twice already (5 families → 6; 17 positions).
- **Threshold 1 (coercion):** for each of the **17** derived positions, poisoning it with a
  coercible scalar and loading yields **0** non-`str` positions. Measured pre-fix: **12 of 17 leak**.
- **Threshold 2 (containers are refused, never coerced):** a container in any position leaves that
  position `""` **and appends a `campo ilegible:` record to `graph.load_warnings`**. A container
  must not coerce — `str({})` is `"{}"`, a truthy string, so `coverage()` would keep counting the
  malformed field as documented and the miscount would survive its own fix.
- **Threshold 3 (typed refusal):** `MapStore.load` raises **only** `MapStoreError`. Measured
  pre-fix: **4 untyped leaks** (`sqlite3.ProgrammingError` ×3, `TypeError` ×1).
- **Named weaker variant `M-STO-a` (must go RED):** coerce only the positions the *current* tests
  poison. This is the defect being repaired — a control implemented to the edge of the noun that was
  named — so the derived-set arm must redden it.
- **Named weaker variant `M-STO-b` (must go RED):** let containers coerce via `str(value)`. Passes
  threshold 1, fails threshold 2, and re-introduces the silent miscount.
- **Executed verification:** `tests/test_repair_store_boundary.py`; thresholds above.

### 3.2 · `HLR-MAP.1` — the module map is true against the tree

> **`docs/ARCHITECTURE.md` shall describe the tree as it is, and shall mark every committed-but-
> unimplemented contract as such.**

- **Traceability:** feature-batch blocker `ARQ-1`; C-44.
- **Acceptance tests:** `AT-P04`, `AT-P05`. **Method:** test (unit) + inspection.

##### `LLR-MAP.1.1` — the ARQ amendment lands, with forward-looking rows marked

- The four provably-false rows ARQ found are corrected: `MapStore.load`/`save`/`_reindex`
  signatures, the non-existent `Canvas.dline`, `search`'s real dependencies, and the fact that
  **`app` does not import `search`**.
- **`IRenderer` is described as it is** — prose, not code — until the feature batch's Inc-2 promotes
  it to a `Protocol`.
- **The `ViewState` contract is recorded as a COMMITMENT, not a present-tense fact.** The ARQ
  proposal's `:58` reads *"`mapper/views/state.py`, new this batch"* for a file that does not exist.
  Landing that verbatim would trade a C-44 defect for a false map — **and the map is the oracle the
  A-family triggers read.** It lands under an explicit *committed at PDR · lands in
  `2026-08-26-ui-next-batch-02` Inc-2* marker.
- **Threshold:** every path the map declares exists on disk; **0** present-tense claims about
  symbols absent from the tree.
- **Named weaker variant `M-MAP-a` (must go RED):** land the proposal verbatim. The declared path
  `mapper/views/state.py` does not exist, so the path arm reddens.
- **Executed verification:** `tests/test_repair_map_truth.py`.

### 3.3 · `HLR-GOLD.1` — the byte-identity pin census is derived, and `B3` is corrected

> **The batch record shall state, from a derivation rather than a literal, which byte-identity pins
> exist and which of them the feature batch's Inc-1 reddens by construction.**

- **Traceability:** feature-batch blocker `GOLD-1` / `B3-FALSE`; controls C-24, C-31, C-48.
- **Acceptance tests:** `AT-P06`, `AT-P07`. **Method:** test (unit) + analysis.

##### `LLR-GOLD.1.1` — the pin census is derived from the test module

- **Threshold:** the census is computed by parsing `MASTER_LEGACY_DIGESTS`, and equals
  `len(renderers) × len(GOLDEN_SIZES)`. Derived at `d877784`: **12** = 3 × 4. **The literal 18
  carried by the architect lens is corrected here.**
- **Threshold:** the census names `RadialRenderer` as pinned at **all four** sizes.
- **Named weaker variant `M-GOLD-a` (must go RED):** hand-write the number. The derivation arm
  reddens when a pin is added or removed; a literal does not.
- **Executed verification:** `tests/test_repair_golden_census.py`.

##### `LLR-GOLD.1.2` — trigger `B3`'s non-activation record is corrected

- `B3` is recorded **FIRED** in `state.json`, with the reason naming the wrong input set — not
  merely flipped. **C-48: a non-activation is evidence, and a false one is a defect in the
  evidence.** Recording *why* the probe was wrong is what stops the same probe being re-run.
- `B3` firing turns on **C-24** (golden drift named in the census) for the feature batch.

### 3.4 · `LLR-PERF.1` — the honest 51-node fixture, and nothing more

> **A measurement fixture reproducing the layered-DAG cost shape shall land, with no budget, no
> deadline and no abort mechanism.**

- **Operator rider, recorded verbatim in intent:** `S-18` stays a design item for the feature
  batch's PDR. This batch lands the *measurement*, not the *control*.
- **Threshold:** the fixture builds the 5-layer × 10-per-layer shape (**51 nodes**) and records its
  render cost. It is marked `slow` and asserts **no** budget — a fixture that asserted one would be
  the bolted-in mechanism the rider forbids.
- **Executed verification:** `tests/test_repair_perf_shape.py`, `slow` lane.

---

## 4 · Amendment to the feature batch's record (not silent)

| Token | Before | After |
|---|---|---|
| `D18` (feature batch) | *"`S-01` and `S-02` are struck as `SATISFIED-EXTERNALLY`; security conditions `C-1` and `C-2` are discharged by execution."* | **`S-02`'s strike is WITHDRAWN.** `S-01` and `C-1` stand. `C-2` is **re-opened** and discharged by `HLR-STO.1` here. |
| `B3` trigger | `not_fired`, probe `ls tests/goldens` | **FIRED**, with the input-set error recorded |
| `02e` "5 families / 3 raw" | hand-listed | **superseded by the 17-position derived census** |
| architect "18 pins" | literal | **superseded by the derived 12** |

---

## 5 · Traceability

| Requirement | Method | Test cases | Acceptance |
|---|---|---|---|
| `HLR-STO.1` | test | `TC-P01` | `AT-P01`, `AT-P02`, `AT-P03` |
| `LLR-STO.1.1` | test | `TC-P02`, `TC-P03`, `TC-P04` | `AT-P01`, `AT-P02`, `AT-P03` |
| `HLR-MAP.1` | test + inspection | `TC-P05` | `AT-P04`, `AT-P05` |
| `LLR-MAP.1.1` | test | `TC-P05` | `AT-P04`, `AT-P05` |
| `HLR-GOLD.1` | test + analysis | `TC-P06` | `AT-P06`, `AT-P07` |
| `LLR-GOLD.1.1` | test | `TC-P06` | `AT-P06` |
| `LLR-GOLD.1.2` | inspection | `TC-P07` | `AT-P07` |
| `LLR-PERF.1` | test (slow) | `TC-P08` | — measurement only, by rider |

**Acceptance, black-box:**

| id | Observable outcome | Surface |
|---|---|---|
| `AT-P01` | a map poisoned at **any** derived position loads with every text position `str` | `MapStore.load` |
| `AT-P02` | a container in any position is refused, recorded in `load_warnings`, and never coerced | `MapStore.load` |
| `AT-P03` | every rejected input raises **`MapStoreError`**, never a bare `TypeError`/`ProgrammingError` | `MapStore.load` |
| `AT-P04` | every path `docs/ARCHITECTURE.md` declares exists on disk | the map file |
| `AT-P05` | the map makes **0** present-tense claims about symbols absent from the tree | the map file |
| `AT-P06` | the pin census is derived and equals 12, naming `RadialRenderer` at four sizes | `tests/test_repair_depth.py` |
| `AT-P07` | `state.json` records `B3` FIRED with its input-set reason | `state.json` |

---

## 6 · Increment plan

| Inc | Content | Source files |
|---|---|---|
| **1** | `HLR-STO.1` — the derived-set coercion + typed refusal | **1** (`mapper/store.py`) |
| **2** | `HLR-MAP.1` — land the ARQ amendment, forward rows marked | **0** source (`docs/ARCHITECTURE.md` is a product doc, outside the budget) |
| **3** | `HLR-GOLD.1` + `LLR-PERF.1` — derived pin census, `B3` correction, 51-node fixture | **0** source (tests + records only) |

Serial. Inc-1 owns the only source change in the batch.
