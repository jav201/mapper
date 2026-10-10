# Increment 003 — Inc-M1 · Lane M · `Graph` strong-reference adjacency cache

> **Artifact language**
> This template is the canonical **English scaffold**. Generate the artifact in the batch's development
> language — the **prose**, and never a label. **Where that language is declared:**
> `state.json`'s `language` key in `core` and `full`. The normative RULES below are
> language-independent.

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/guides/increment-template.md` explains each field and the rules that read it. It ships with the flow and is not copied into this batch.

> **Reserved field names.** The **field names and block keywords below are language-independent** — the
> validator parses them literally and they are never translated:
> `SOURCE files` · `Instrument RED-proof` · `Correction population` · `Mutation verdicts` · `Emitted-form assertion` · `Reverse census` · `RED counterfactual` · `Independent review` · `Evidence files` · `Traces to` · `File` · `Kind` · `source` · `test` · `doc` · `config` · `generated` · `fixture` · `⏸ DEFER`

| Field | Value |
|---|---|
| Batch | `2026-10-10-perf-batch` |
| Increment | `003` |
| Lane (if the batch forked) | `M` (Lane M worktree/branch; `mapper/views/` untouched — M-M3 verified below) |
| Requirement(s) | `HLR-PERF.2 · LLR-PERF.2.1` (the cached adjacency, the census guard, the related boundary items) · `LOW-10` (minimap/outline byte stability) |
| Acceptance | `AT-…` nodes in `tests/test_perf_adjacency.py`: `test_cache_mutation_script_equality` · `test_cache_counted_ops` · `test_edges_writer_census` · `test_census_in_place_forms[setitem\|slice\|del\|iadd\|imul\|sort\|reverse\|clear\|extend\|insert\|remove\|pop\|alias]` · `test_minimap_outline_forest_dag_bytes` |
| Agent | `Kimi (kimi-code/kimi-for-coding) via the kimi CLI` |
| Date | `2026-10-10` |

---

## 1 · What changed

`Graph.children_of`/`Graph.parent_of` (`mapper/model.py`) now serve from a private
adjacency cache built in one O(E) pass: `_adj_src` (a STRONG reference to the
`edges` list the index was built from), `_adj_len` (the length recorded at build
time), `_adj_children` (parent → child ids in edge-list order) and `_adj_parents`
(child → first parent, `setdefault`, preserving the old linear scan's first-match
semantics on multi-parent graphs).  A hit requires the token
`_adj_src is self.edges and len(self.edges) == _adj_len`: the `len` half catches
`add_edge`'s in-place append, the `is` half catches wholesale replacement — and
because the token pins the old list, `id()` recycling after garbage collection can
never fake a hit (the PDR's main-risk ruling).  `children_of` returns a FRESH list
per call (`list(...)` — callers may bind and mutate it, `painting.py:519`).

The four cache fields are dataclass fields with `compare=False, repr=False`,
`init=False` — the `csv_collisions` precedent: `Graph.__eq__` and `repr` are
byte-for-byte what they were, every existing constructor call is untouched, and
the new fields are classified in the `tests/test_repair_store_boundary.py`
totality guard (`_EXPECTED_NON_TEXT[Graph]`, with a comment; `_adj_parents` is
annotated `Mapping[str, str]` precisely so it classifies as neither text nor
str-map there — a bare `dict[str, str]` annotation would classify as a str-map
and trip the guard's exclusivity assertion).

The soundness tripwire is the AST census guard in
`tests/test_perf_adjacency.py`: the set of post-construction writers of
`.edges` under `mapper/` must equal {`model.py` `Graph.add_edge` (append),
`screens/map/editing.py` `EditingOps._remove_subtree` (wholesale assignment)},
and every in-place form (`edges[i]=`, slice, `del`, `+=`, `*=`, `.sort`,
`.reverse`, `.clear`, `.extend`, `.insert`, `.remove`, `.pop`) plus the alias
form (`x = <expr>.edges` then `x` mutated — DOCUMENTED LIMITS per ruling R18:
aliasing through function arguments, containers, or attributes on other objects
is NOT detected) is flagged, one planted mutation per parametrized arm in a tmp
copy of the package.  LLR-PERF.2.3 is pinned by inspection, not code: Lane M
touches zero bytes under `mapper/views/` (M-M3 file-diff check below).

---

## 2 · Files modified

**The budget counts SOURCE files only. Tests are not capped. Product docs and `.dev-flow/**` are outside the count.**

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/model.py` | source | `LLR-PERF.2.1` | private adjacency cache (`_adj_src`/`_adj_len`/`_adj_children`/`_adj_parents`, `compare=False, repr=False`, `init=False`) + `_adjacency()`; `children_of`/`parent_of` serve from it (fresh list; first-match) |
| `tests/test_perf_adjacency.py` | test | `LLR-PERF.2.1` · `LOW-10` | new: mutation-script equality (two length-preserving wholesale replacements back-to-back, no lookup between; add_edge; focus; fresh-list; forest/multi-parent/empty/deep-5000) · counted ops (500 warmed lookups ≤ 1 full scan) · AST census guard + 13 in-place-form arms · minimap/outline byte-stability over forest + multi-parent DAG |
| `tests/test_repair_store_boundary.py` | test | `LLR-PERF.2.1` (cache fields must not change equality/repr) | totality guard: the four cache fields classified non-text on `Graph` (csv-safety precedent) |

| Count | Value |
|---|---|
| **SOURCE files** | **1** / 4 |
| Test files | 2 (uncapped) |
| Doc files | 0 (outside the count) |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_perf_adjacency.py tests/test_perf_goldens_manifest.py tests/test_repair_store_boundary.py tests/test_model.py tests/test_mod_parity.py
ruff check mapper/model.py tests/test_perf_adjacency.py tests/test_repair_store_boundary.py
git diff --stat 5cde04e -- mapper/views   # M-M3: must print nothing
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | — | none separate (the AT nodes above are the unit layer) |
| **A · white-box** | `core` · `full` | `tests/test_perf_adjacency.py::test_cache_mutation_script_equality` · `::test_cache_counted_ops` · `::test_edges_writer_census` · `::test_census_in_place_forms[...]` (13 arms) | 16 passed |
| **B · black-box** | `core` · `full` | `tests/test_perf_adjacency.py::test_minimap_outline_forest_dag_bytes` (real app, real keys) + the named gate files (`test_perf_goldens_manifest.py` 2 · `test_repair_store_boundary.py` 102 · `test_model.py` 5 · `test_mod_parity.py` 3) | 113 passed; **129 passed overall, 0 failed** |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | M-M1a: hit check → `if False:` (cache bypass) · M-M1b: `self._adj_src is self.edges` → `self._adj_src is not None` (len-only key) · fresh-list: `return list(children.get(node_id, ()))` → `return children.get(node_id, [])` · M-M1c: each of the 13 in-place/alias forms planted at the end of `mapper/model.py` |
| Instrument | project code: own hand via the driver `.dev-flow/2026-10-10-perf-batch/evidence/m1-red.driver.py` (kept next to the transcript for DDR re-execution); restore checked by sha256 against a byte-copy kept next to the transcript |
| Where it ran | **my own tree / worktree** |
| Transcript | `.dev-flow/2026-10-10-perf-batch/evidence/m1-red.transcript` — 16 cycles, each: mutation applied → named node FAILED (exit 1) → restore → sha256 before == after → GREEN |
| Restore proven by | **sha256 equality per cycle**, full 64-hex digests recorded in the transcript; post-restore whole-file run: 17 passed |
| Bytecode cache | run with `python -B` and `-p no:cacheprovider` |
| Arms resolved at baseline | 17 |
| Verdict granularity | per node id: `test_cache_counted_ops` → KILLED by M-M1a; `test_cache_mutation_script_equality` → KILLED by M-M1b AND by the fresh-list mutant; `test_edges_writer_census` → KILLED by each of the 13 planted forms; `test_census_in_place_forms[...]` → each arm plants its own form in a tmp copy (self-reddening by design); `test_minimap_outline_forest_dag_bytes` stayed GREEN under every product mutant (byte-stability pin — a cache-order drift, not a bypass, is its named killer) |
| Arms that stayed GREEN | `test_minimap_outline_forest_dag_bytes` under M-M1a/M-M1b/fresh-list — expected: its oracle is painted bytes, and the mutants do not change painted output on these small graphs |

| Field | Value |
|---|---|
| **RED counterfactual** | 16 mutation cycles, all RED with byte-identical sha256 restore · transcript `.dev-flow/2026-10-10-perf-batch/evidence/m1-red.transcript` |

| Field | Value |
|---|---|
| **Mutation verdicts** | M-M1a → `test_cache_counted_ops` RED · M-M1b → `test_cache_mutation_script_equality` RED (the length-preserving two-replacement stretch: the len-only key stale-hits after replacement 1) · fresh-list → `test_cache_mutation_script_equality` RED · M-M1c × 13 forms → `test_edges_writer_census` RED per form |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_perf_adjacency.py` (counted-ops oracle) | cache bypass (M-M1a) | `assert g.edges.visits <= len(g.edges)` — 500,000 visits vs budget 1,000 |
| `tests/test_perf_adjacency.py` (mutation-script equality) | len-only key (M-M1b) / cached-list return (fresh-list) | children/parent drift vs the linear-scan reference / `junk-id` leaked into the next lookup |
| `tests/test_perf_adjacency.py` (census guard) | one planted in-place form per arm (M-M1c) | `in-place edges mutation found: [form] at model.py:_m` |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 3 instruments shown RED before their PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| minimap / outline painted text | `Text.plain` of `MapScreen._minimap_text(40)` and `OutlineRenderer().render(...)` over a forest (opened in the real app through `MapperApp` + real keys) and a multi-parent DAG, before vs after cache warm-up + wholesale `edges` replacement, and vs a fresh uncached copy | byte-identical across all three (`test_minimap_outline_forest_dag_bytes`) |
| `tests/test_mod_parity.py` painted goldens (pre-existing, this lane must not drift them) | pytest over the pinned 118/87-col parity files | 3 passed |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts, each asserted against the form its producer emits |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED-proof transcript (16 cycles, commands + outputs + full sha256 digests) | `.dev-flow/2026-10-10-perf-batch/evidence/m1-red.transcript` | recorded at the DDR |
| RED-proof driver (re-executes all 16 cycles on demand; stdout-only tails so the transcript carries the real failure lines) | `.dev-flow/2026-10-10-perf-batch/evidence/m1-red.driver.py` | recorded at the DDR |

| Field | Value |
|---|---|
| **Evidence files** | 2 artifacts at the declared home; every cycle's restore digest quoted verbatim inside the transcript |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | the census guard's power rests on there being NO in-place writer of `.edges` anywhere under `mapper/` — an absence |
| If the result is an ABSENCE, what made the search wide enough | the census is AST-derived over EVERY `*.py` under the package (not a grep of remembered sites), asserts the writer set EQUALS the declared two (both directions, so an emptied census fails too), and the 13 parametrized arms each plant a distinct in-place form in a tmp copy — one mutation per guard row, so a guard branch that silently stops firing reddens its arm |
| Guard labelled as protecting a CONCLUSION, not a behaviour | the census protects the CONCLUSION that the strong-reference token is a sound validity check (requirement row 4) — it is the tripwire named as the batch's main risk in PDR §6 |
| Conjunctive criteria: one mutation per conjunct | the equality node's conjuncts (id-reuse stretch / add_edge / focus / fresh-list / boundary shapes) each have a named reddening mutation: M-M1b, (append is covered by the len half — drop `_adj_len` from the token and the add_edge step serves stale), new-Graph, fresh-list mutant |
| Synthetic instance of the absent case | every `test_census_in_place_forms[...]` arm synthesizes its absent case in a tmp package copy |
| **Positive control for every probe that returned an ABSENCE** | `test_census_in_place_forms` is exactly that for the census; `test_cache_counted_ops` asserts `visits > 0` so a counting wrapper that observed nothing cannot pass vacuously |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rlE "children_of\|parent_of" tests/` | 20+ test files consume the unchanged signatures; `tests/test_mod_parity.py`, `test_model.py`, the store/CSV suites re-run green in §4 |
| B2 file moved on disk | n/a — no file moved; `mapper/model.py` edited in place | — |
| B3 byte-identical golden captures this source | `tests/test_mod_parity.py` parity goldens (painted output) | 3 passed, 0 golden-line diffs |
| B4 artifact produced here is consumed elsewhere | the cache is private to `model.py` (`_`-prefixed); `grep -rn "_adj_" mapper/` outside model.py | no consumer — by design (LLR-PERF.2.3) |
| A3 | `git diff --stat 5cde04e -- mapper/views` | **empty** (M-M3, recorded per lane at the DDR); `grep -rn "_child_index" mapper/views/` still present per-render, untouched |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1 · B2 · B3 · B4 · A3), each with its command and verdict |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population | Enumeration method | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| adjacency lookups served from a cache | the two lookup methods `children_of`/`parent_of` (`mapper/model.py:172-179` at base) | the requirement's own census of consumers (minimap, navigation, search, editing, coverage, factory, lane view, `import_csv` orphan pass, `store._reindex`) — all ride unchanged signatures | 2 methods, 1 source file | `mapper/model.py` | every other site left untouched: renderers keep their own per-render `_child_index` (LLR-PERF.2.3 pins this — moving the cache's cost into `views` is M-M3) |

| Field | Value |
|---|---|
| **Correction population** | one correction, 1 source file, enumerated from the requirement before the edit |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|---|---|---|---|
| none — no superseded marker introduced | 0 hits | yes | n/a |

### Signed-balance test ledger

`post = base − deleted + added` → `tests/test_perf_adjacency.py` +1 (17 nodes) · `tests/test_repair_store_boundary.py` 0 ±0 (one tuple extended in place; node count unchanged) · goldens 0 ±0 · source +1 (`mapper/model.py`, edited)  ✓ reconciles

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | PENDING — orchestrator assigns `code-reviewer` at the batch gate |

---

## 5 · Risks

- The census alias form states its limits in both the guard docstring and the
  requirement (ruling R18): aliasing through function arguments, containers, or
  attributes on other objects is NOT detected.  That hole is accepted because the
  declared writer set is also pinned positively (writers == declared, both
  directions) — a new writer must appear as a writer site even when the alias
  detector misses its mutation.
- `Graph` deepcopy/pickle now carries the cache fields; the strong-reference token
  stays correct under deepcopy (the copied `_adj_src` and copied `edges` remain
  the same object via the memo, so a carried cache is still valid; an invalid
  carried cache simply rebuilds).  No product site pickles `Graph` today.

## 6 · Pending items / spec deviations

- None for Inc-M1.  (LLR-PERF.2.2 / `tests/test_perf_dump.py` is Inc-M2, the next
  Lane M increment; LOW-10 is included here per the design proposal.)

## 7 · Suggested next task

Inc-M2 (Lane M): `mapper/mermaid.py` linear incident pass (dangling edges covered)
+ `tests/test_perf_dump.py` (per-dump ≤ 2·E + c, scaling ratio [1.8, 2.2], fixture
goldens incl. dangling-edge, AT-076 through a real persisting edit gesture via
`_save_or_toast`).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 1 source file (`mapper/model.py`); `git diff --stat 5cde04e -- mapper` = 1 file |
| 2 | Tests written in this same increment | all | ✓ | `tests/test_perf_adjacency.py` (17 nodes, transcript GREEN line) |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | the AT nodes are the unit layer (16 + 1 black-box) |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | 16 cycles, all RED, sha256-verified restore; transcript §per-cycle |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 5 probes in the table above |
| 6 | `code-reviewer` passed | `core` · `full` | ⚠ | PENDING — named in §4b |
| 7 | No file from another lane touched | all | ✓ | Lane R owns `mapper/views/` + `mapper/canvas.py`: zero bytes touched (`git diff 5cde04e -- mapper/views` empty, `mapper/canvas.py` untouched) |
| 8 | Frozen interfaces untouched | all | ✓ | `children_of`/`parent_of` signatures, order and first-match semantics unchanged; `Graph.__eq__`/`repr` unchanged (new fields `compare=False, repr=False`); goldens manifest + parity green |
| 9 | Coverage claims verified **on disk** | all | ✓ | 129 passed across the five named files; per-node RED transcripts on disk |
| 10 | Load-bearing emptiness declared | all | ✓ | table above — the census absence, its wideness, and its positive controls |
| 11 | **Mutation verdicts** declared | all | ✓ | M-M1a · M-M1b · fresh-list · M-M1c ×13 — each with its RED node id |
| 12 | **Instrument RED-proof** declared | all | ✓ | 3 instruments shown RED before their PASS was believed |
| 13 | **Correction population** declared | all | ✓ | one correction, enumerated before the edit |
| 14 | **Emitted-form assertion** declared | all | ✓ | painted `.plain` bytes before/after cache + vs uncached copy; parity goldens |
| 15 | **Independent review** names somebody | all | ⚠ | PENDING in §4b (orchestrator assigns) |
| 16 | **Evidence files** declared | all | ✓ | `.dev-flow/2026-10-10-perf-batch/evidence/m1-red.transcript` |
