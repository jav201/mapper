# Increment 001 — HLR-CSV.1 · LLR-CSV.1.1 / LLR-CSV.1.2 / LLR-CSV.1.3 · `The store refuses what its loader refuses (round-trip save check)`

> **Artifact language:** English.
> **Owed in.** `core` ✓ · `full` ✓
> **Where this lives:** the repo, `.dev-flow/2026-10-10-csv-safety-batch/03-increments/increment-001.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-10-csv-safety-batch` |
| Increment | `001` (CSVI1) |
| Lane (if the batch forked) | n/a — one lane · increment 1 owns `model` + `store` (ruling R10 / architect B3) |
| Requirement(s) | `HLR-CSV.1` · `LLR-CSV.1.1` · `LLR-CSV.1.2` · `LLR-CSV.1.3` (+ the unit round-trip nodes of `LLR-CSV.3.1`) |
| Acceptance | unit layer 0 in `tests/test_csv_safety_store.py` (§3); AT-072 is increment 2's and is NOT claimed here (ruling R8/R14: the store layer's controls are its own unit nodes) |
| Agent | Kimi (`kimi-code/kimi-for-coding`) via the kimi CLI — worker unit CSVI1 |
| Date | `2026-10-10` |

---

## 1 · What changed

- **`MapStore.save` now refuses, before writing any byte, any graph whose saved form would not load back as the same graph** (LLR-CSV.1.1, ruling R2 as amended by R11). After the existing cycle guard and the single `mermaid.dump`, the new `_check_round_trip(graph, mmd_text)` parses the exact text about to be persisted through the store's own loader (`mermaid.parse`) and raises `MapStoreError` — a plain-language reason naming the rule — when the parse raises (multiple parents / the dump does not re-parse) or when the reparse differs in the node-id set or the edge set as (parent, child) pairs. The ROOT is NOT compared (ruling R11 / B-117: a forest's root drifts on reparse); edge MULTIPLICITY is compared via sorted pair lists, because `dump`'s `emitted` dedup turns exact duplicate edges into a silent row loss a set comparison would accept (intended superset of the loader, architect A5). The check runs before the two-phase write (LLR-CSV.1.2) and the check's `mmd_text` IS the persisted string (one dump per save, ruling R12). The shipped surface the user reaches is unchanged: `_save_or_toast` already toasts the exception type and returns `False`.
- **`Graph` gains the collision-record carrier increment 2 fills** (ruling R10): frozen value types `CsvRow(line_no, raw_id)` / `CsvCollision(slug, rows)` and one defaulted field `csv_collisions: list[CsvCollision] = field(default_factory=list, compare=False, repr=False)` — `Graph.__eq__`/`repr` do not change. Nothing reads it yet.
- **`Graph.multi_parent_ids()`** (child ids appearing as the child of more than one edge, first-appearance order) — kept for the preview's multi-parent sentence only; the store check does not use it (ruling R2).

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/model.py` | source | LLR-CSV.1.1 (predicate kept per R2), HLR-CSV.2 enabler | `CsvRow` + `CsvCollision` frozen dataclasses; `Graph.csv_collisions` defaulted field (`compare=False, repr=False`); `Graph.multi_parent_ids()`; removed the pre-existing dead `typing.Any` import (ruff F401, flagged by this increment's verification command) |
| `mapper/store.py` | source | LLR-CSV.1.1, LLR-CSV.1.2 | `MapStore._check_round_trip` (new) + one call in `save` between `dump` and the sidecar build — the round-trip refusal before any byte is written |
| `tests/test_csv_safety_store.py` | test | LLR-CSV.1.1, LLR-CSV.1.2, LLR-CSV.1.3, LLR-CSV.3.1 | new — 8 nodes (§4) |
| `.dev-flow/2026-10-10-csv-safety-batch/evidence/inc1-red.transcript` | generated | LLR-CSV.1.1/1.2/1.3 | RED-proof transcript (§4) |

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 4** (`mapper/model.py`, `mapper/store.py`) |
| Test files | 1 (`tests/test_csv_safety_store.py`) |
| Doc files | 1 (this packet + the evidence transcript — outside the count) |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_csv_safety_store.py tests/test_store.py tests/test_import_csv.py tests/test_repair_cycles.py
ruff check mapper/store.py mapper/model.py tests/test_csv_safety_store.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `tests/test_csv_safety_store.py` (8 new) + re-run pins `tests/test_store.py`, `tests/test_import_csv.py`, `tests/test_repair_cycles.py` | **55 passed in 4.54s** (§3 command, this worktree) |

New node ids:

- `tests/test_csv_safety_store.py::test_save_refuses_multi_parent_graph` — two-row, three-way and auto-id collision shapes (each also asserts the workspace digests are unchanged)
- `tests/test_csv_safety_store.py::test_save_refuses_cycle_still` — cyclic `a → b → a` and self-parent `a → a` (LLR-R01.5 guard kept verbatim, "cycle")
- `tests/test_csv_safety_store.py::test_save_refuses_unparsable_dump` — a node title containing a newline ("would not re-open")
- `tests/test_csv_safety_store.py::test_save_refuses_reparse_structure_mismatch` — an edgeless node titled `a --> b` (node-id set changes) and exact duplicate edges (edge multiset changes)
- `tests/test_csv_safety_store.py::test_refused_save_changes_no_workspace_byte` — LLR-CSV.1.2 oracle: OVERWRITES a pre-existing map; sha256 of every workspace file (recursive `rglob`, incl. `mapper.db` and any `*.tmp`) unchanged, file set unchanged, `.mmd` bytes identical, no `*.tmp`
- `tests/test_csv_safety_store.py::test_save_accepts_legacy_forest_after_edit` — LLR-CSV.1.3: legacy pair `graph TD\n    a\n    b --> c\n` hand-written as the old app would, loaded (root `a`), edited (child `d` added), saved without raising, reloaded with equal node-id and edge sets
- `tests/test_csv_safety_store.py::test_save_load_roundtrip_valid_trees` — tree with edge label and a child-first-declared tree; identical nodes, edges, root, titles
- `tests/test_csv_safety_store.py::test_save_load_roundtrip_empty_and_single_node` — empty graph and single node save and re-open

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | (M1) deleted the `self._check_round_trip(graph, mmd_text)` call in `MapStore.save`; (M1b) moved that call to after `mmd_tmp.replace(mmd_path)`; (M4) re-added the root comparison (`reparsed.root_id != graph.root_id`) as the first comparison of `_check_round_trip`; (M-cyc) deleted the pre-existing cycle guard |
| Instrument | hand edit of the product file, applied and reverted by explicit copy (`cp /tmp/store_inc1_backup.py mapper/store.py`); every restore checked by sha256 |
| Where it ran | this worktree |
| Transcript | `.dev-flow/2026-10-10-csv-safety-batch/evidence/inc1-red.transcript` (relative paths only) |
| Restore proven by | sha256 of `mapper/store.py` returned to `293c521e12874a61901cd0f54de7f0ea3a4febd2f51a20177f22769e94ad7773` after every mutation |
| Bytecode cache | run with `python -B` |
| Arms resolved at baseline | 4 mutations × their named nodes (below) |
| Verdict granularity | per node id |
| Arms that stayed GREEN | under M4 every tree fixture stayed green (the child-first fixture pins its real root via `child_first.root_id = "top"` before saving, so only the forest node reddens — matching LLR-CSV.1.3's claim) |

RED outputs (verbatim tails from the transcript):

- M1 + `-k "multi_parent or unparsable or reparse_structure"` → `3 failed, 5 deselected` — `test_save_refuses_multi_parent_graph`, `test_save_refuses_unparsable_dump`, `test_save_refuses_reparse_structure_mismatch` each `FAILED` (the fixtures save; the negative controls' paired oracles then bite or the raise never happens).
- M1b + `-k refused_save_changes_no_workspace_byte` → `1 failed` — `test_refused_save_changes_no_workspace_byte` `FAILED` (the target `.mmd` digest changes because the fixture overwrites a pre-existing map).
- M4 + `-k legacy_forest` → `1 failed` — `test_save_accepts_legacy_forest_after_edit` `FAILED` (the check reports the forest's root drift `a → b` and refuses a map that opens today).
- M-cyc + `-k cycle_still` → `1 failed` — `test_save_refuses_cycle_still` `FAILED`.

| Field | Value |
|---|---|
| **RED counterfactual** | M1 (delete the round-trip check) reddens the three named LLR-CSV.1.1 nodes; M1b (move the check after the first temp replace) reddens the LLR-CSV.1.2 no-write oracle node; M4 (re-add the root comparison) reddens the LLR-CSV.1.3 forest node while tree fixtures stay green; deleting the cycle guard reddens `test_save_refuses_cycle_still`. Transcript at `evidence/inc1-red.transcript`; restore digest `293c521e…7773` returned after every mutation |

| Field | Value |
|---|---|
| **Mutation verdicts** | 4 mutants, all KILLED per node id (M1 → 3 nodes RED, M1b → 1, M4 → 1, M-cyc → 1); arms that stayed GREEN: named above (tree/empty/single round-trip nodes under M1b/M4/M-cyc, cycle node under M1 — none of them the mutated check's own target); restored byte-identical (sha256) and the full §3 run re-run GREEN (55 passed) |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_csv_safety_store.py` (the new nodes) | M1/M1b/M4/M-cyc product mutations (above) | `FAILED … DID NOT RAISE` / oracle mismatch — verbatim tails in the transcript |
| `ruff check mapper/store.py mapper/model.py tests/test_csv_safety_store.py` | the pre-existing dead `typing.Any` import in `mapper/model.py` | `F401 … imported but unused` — fixed by removing the dead import, then `All checks passed!` |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 2 instruments, each shown RED before its PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the persisted `.mmd` bytes on a refused overwrite | `test_refused_save_changes_no_workspace_byte` compares `(workspace / "keep.mmd").read_bytes()` before/after the refused save | byte-identical (assertion passed) |
| the workspace file set + digests | `_digests(workspace)` = `{relative path: sha256}` for every file via `rglob("*")`, compared before/after every refused fixture | equal dicts, empty `*.mmd`/`*.tmp` globs (assertions passed) |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts, each asserted against its emitted form |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| inc1-red.transcript | .dev-flow/2026-10-10-csv-safety-batch/evidence/inc1-red.transcript | `44ad41e56a39e1aa7264ecd834ed072736142edbeb9f637895e61d90680c2b77` |

| Field | Value |
|---|---|
| **Evidence files** | `evidence/inc1-red.transcript` — baseline hashes, all four RED runs, restores and sha256 checks, final 55-passed GREEN (sha256 of the stored bytes cited above) |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | no — every refusal is a synthetic in-memory graph built by the test; the census claim (no existing test saves a graph the check refuses) is the P3 full-suite gate's, not this increment's |
| If the result is an ABSENCE, what made the search wide enough | n/a |
| Guard labelled as protecting a CONCLUSION, not a behaviour | n/a |
| Conjunctive criteria: one mutation per conjunct | per-conjunct: structure refusal (M1) · pre-write placement (M1b) · root exclusion (M4) · cycle guard kept (M-cyc) |
| Synthetic instance of the absent case | each fixture graph IS the synthetic instance of a refused save |
| **Positive control for every probe that returned an ABSENCE** | the same oracle digests change under M1b (positive control that the digest probe sees writes) and stay equal on every refused fixture |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rlE "MapStore\|preview_csv\|_ImportPreviewScreen" tests/` | 40 files (executed at P1, design §6); this increment only ADDS a refusal and additive model members — the §3 re-run pins (`test_store.py`, `test_import_csv.py`, `tests/test_repair_cycles.py` — the preview/CSV/cycle consumers) stay green |
| B2 file moved on disk | n/a — no file moved | not fired |
| B3 byte-identical golden captures this source | n/a — no golden reads store/model bytes | not fired |
| B4 artifact produced here is consumed elsewhere | `MapStore.save`'s pair is consumed by `MapStore.load` (B4 fired at intake) | the LLR-CSV.1.3 forest node exercises exactly that consume path |

| A3 | interface consumed by another module changed | `grep -rn "csv_collisions\|multi_parent_ids\|CsvCollision\|CsvRow" mapper/ tests/` outside their definitions | no consumer yet — the field is filled and read in increment 2 only |

| Field | Value |
|---|---|
| **Reverse census** | 4 probes run (B1 and B4 fired with the hits above, re-validated green by the §3 run; B2, B3 did not fire; A3 additive, zero consumers) |

### Correction population — enumerated BEFORE the first site was edited

| Field | Value |
|---|---|
| **Correction population** | none — this increment adds behaviour; the one incidental correction (dead `typing.Any` import in `mapper/model.py`) was enumerated by `ruff check` on the touched files before the test file was written |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|---|---|---|---|
| dead `typing.Any` import in `mapper/model.py` | `grep -n "Any" mapper/model.py` → only the removed import line | yes — `ruff check` clean | `mapper/model.py` |

### Signed-balance test ledger

`post = base − deleted + added` → `55 = 47 + 8 − 0` ✓ reconciles (47 pre-existing nodes across the four files, 8 added in `tests/test_csv_safety_store.py`, 0 deleted).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | **PENDING** — the orchestrator dispatches it (per the unit brief) |

---

## 5 · Risks

- The round trip is broader than today's enumerated loader guarantees; if the P3 full-suite gate finds a graph that saves on master but the new check refuses, the batch returns to design with that fixture (qa MED-4 fallback, design §6).
- `dump`'s parentless-node loop is O(N·E) (B-33 territory) and NOT fixed here; the P4 perf evidence (added parse ≤ 25 % of `MapStore.save` wall time on a 6 000-node wide tree, median of 3) is owed at validation, per ruling R12.
- Forest root drift is pre-existing and now pinned accepted by `test_save_accepts_legacy_forest_after_edit`; fixing the drift itself is backlog B-117.

## 6 · Pending items / spec deviations

- The P4 numeric perf measurement (ruling R12) — evidence only, owed at validation.
- `ARCHITECTURE.md` §4 `Graph` row amendment (ruling R10 / architect B3) — owed at batch close.

## 7 · Suggested next task

Increment 2 — `preview_csv` records the collisions into `Graph.csv_collisions` and `_ImportPreviewScreen` paints the refusal sentence + refuses at the `s` keypress (AT-072/073/074).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 2 / 4 (§2) |
| 2 | Tests written in this same increment | all | ✓ | 8 nodes in `tests/test_csv_safety_store.py` |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | 8 unit nodes, 55 passed (§3) |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | M1 / M1b / M4 / M-cyc, transcript + restore digest (§4) |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 4 probes (§4) |
| 6 | `code-reviewer` passed | `core` · `full` | ⚠ | PENDING — orchestrator dispatches (§4b) |
| 7 | No file from another lane touched | all | ✓ | one lane; files = §2 |
| 8 | Frozen interfaces untouched | all | ✓ | `MapStore.save` signature and cycle-guard message unchanged; `Graph` field/method additive with `compare=False, repr=False` |
| 9 | Coverage claims verified **on disk** | all | ✓ | 55 passed here (§3 command) |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 |
| 11 | **Mutation verdicts** declared | all | ✓ | §4 — 4 mutants KILLED per node id |
| 12 | **Instrument RED-proof** declared | all | ✓ | §4 — pytest nodes + ruff |
| 13 | **Correction population** declared | all | ✓ | §4 (ruff-enumerated dead import) |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4 (.mmd bytes + workspace digest map) |
| 15 | **Independent review** names somebody | all | ⚠ | PENDING (§4b) — dispatched by the orchestrator |
| 16 | **Evidence files** declared | all | ✓ | §4 — `evidence/inc1-red.transcript` with sha256 |
