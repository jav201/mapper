# Increment 002 — LLR-FX.3.1, LLR-FX.3.2 · `dump` writes the declared root first (B-117)

> **Owed in.** `core` ✓ · `full` ✓

| Field | Value |
|---|---|
| Batch | `2026-10-11-fixes-batch` |
| Increment | `002` |
| Lane (if the batch forked) | n/a — one lane |
| Requirement(s) | US-FX-003 · HLR-FX.3 · LLR-FX.3.1, 3.2 (B-117) |
| Acceptance | AT-086 · white-box TC-FX-3.1, 3.2, 3.3 · visit bound (AT-076) |
| Agent | `software-dev` |
| Date | `2026-10-15` |

---

## 1 · What changed

`dump` now writes the declared root's line right after `graph TD` when that root is written, is no written edge's child, and is not the first parentless node of the text; otherwise the bytes are exactly today's. A forest saved through the store re-opens with the root it had (a forest set up in-session, e.g. CSV import). The decision reuses bookkeeping gathered inside the two existing edge passes (written ids, written children, parents in write order); no third pass over `graph.edges`. A map loaded from disk takes its root from `parse`, so on resave the hoist does not fire and its bytes do not change (PDR F2 correction). `parse` and the node-set/edge-multiset comparison of `_check_round_trip` are unchanged; its docstring no longer claims the root drifts.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/mermaid.py` | source | LLR-FX.3.1 | `dump`: bookkeeping in pass 1, orphan list built once from `graph.nodes`, conditional root-first insert, docstring |
| `mapper/store.py` | source | LLR-FX.3.2 | `_check_round_trip` docstring only (no code) |
| `tests/test_fixes_forest_root.py` | test | HLR-FX.3 | new: 20 nodes incl. AT-086, 8 parametrised shape cases, TC-FX-3.3 undo-snapshot node |
| `tests/test_csv_safety_store.py` | test | LLR-FX.3.2 | `test_save_accepts_legacy_forest_after_edit` gains `assert reloaded.root_id == loaded.root_id == "a"` and a comment |
| `tests/test_perf_dump.py` | test | LLR-FX.3.2 | `orphan-order` arm gains `ordered.root_id = "root"` |
| `.dev-flow/2026-10-11-fixes-batch/evidence/inc002-red.transcript` | doc | | RED/restore transcript |

Pin moves, itemised. (1) `tests/test_perf_dump.py::test_dump_fixture_goldens`, `orphan-order` arm: the line `ordered.root_id = "root"` was added after the `add_edge`; the expected bytes `graph TD\n    root[raiz] --> kid\n    zeta\n    alfa\n` did not move. Why: the arm's declared root was `zeta` (first node added), which text order does not elect, so the hoist would move it; declaring `root` keeps the arm pinning orphan order. (2) `tests/test_csv_safety_store.py::test_save_accepts_legacy_forest_after_edit` gained one assertion (a new check; no existing check relaxed). No golden file changed.

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 4** (`store.py` docstring only) |
| Test files | 3 (uncapped) |
| Doc files | 1 (outside the count) |

---

## 3 · How to test

```bash
cd <worktree>
env -u NO_COLOR -u TERM python -m pytest -p no:cacheprovider tests/test_fixes_forest_root.py tests/test_perf_dump.py tests/test_csv_safety_store.py tests/test_mermaid.py
ruff check mapper/mermaid.py mapper/store.py tests/test_fixes_forest_root.py tests/test_perf_dump.py tests/test_csv_safety_store.py
```

---

## 4 · Test results

**GREEN line (executed):** `326 passed in 141.54s` over `test_fixes_forest_root`, `test_mermaid`, `test_perf_dump`, `test_perf_goldens_manifest`, `test_csv_safety_store`, `test_csv_safety_preview`, `test_fixes_csv_import`, `test_no_operator_paths`, `test_requirements_canon`, `test_draft_save`, `test_g6_store_surrogates`, `test_inc9`, `test_inc9r`, `test_en4`, `test_canvas_header_charge`, `test_inc3_census`, `test_inc4_census`; and `128 passed` over the remaining `dump` consumers (`test_inc9e`, `test_mod_bodies`, `test_mod_compat`, `test_repair_cycles`, `test_search`). `ruff check` on the five touched files: `All checks passed!`

**One failure outside this increment, found while looking for undo tests:** `tests/test_a3_census.py::test_tc_a3_the_census_cardinalities_are_PINNED` and `test_llr_n07_2_2a_the_widget_protocol_was_not_swept_into_the_migration` report `derived 38 zero-arg sites against a pinned 37`. The 38th site is `tests/test_fixes_csv_import.py:39` (`.render().plain`, increment 001's test helper); increment 001 did not run this file. Not touched here (outside the file set); owner: orchestrator (move the pin 37 to 38, or change the helper). That census also requires new test files to be staged (`git add`); the new file here is.

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** TC-FX-3.1 | `core` · `full` | `test_b117_reproduction_bytes`, `test_orphan_root_is_not_declared_twice`, `test_edge_parent_root_gets_a_standalone_line_first`, `test_every_parentless_node_set_as_root_reparses_to_itself` (8 parametrised: 8 of 8), `test_root_already_elected_by_text_order_changes_nothing` (3), `test_empty_and_single_node_graphs_are_unchanged`, `test_root_that_is_a_written_child_is_not_hoisted`, `test_root_whose_only_edge_dangles_stays_unwritten`, `test_root_id_absent_from_nodes_leaves_the_text_unchanged` | passed |
| **A · white-box** TC-FX-3.2, 3.3, bound | `core` · `full` | `test_save_accepts_legacy_forest_after_edit`, `test_dump_fixture_goldens`, `test_undo_snapshot_of_a_forest_restores_the_declared_root` (dump + `_build_sidecar` + `_graph_from_sidecar`, the `undo.py` path), `test_dump_counted_ops_scaling_ratio`, `test_at_076_real_save_dump_budget` | passed |
| **B · black-box** AT-086 | `core` · `full` | `test_at_086_forest_root_survives_save_and_reload` (`MapStore.save` then `load`; the saved `.mmd` names `a[Alpha]` first, once) | passed |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | M-FX6, M-FX6b, M-FX6c, M-FX7, M-FX12, tabled below |
| Instrument | own Python harness kept outside the repo; verdicts read from a junit XML per node id; restore checked by sha256 |
| Where it ran | my own worktree, one lane |
| Transcript | `.dev-flow/2026-10-11-fixes-batch/evidence/inc002-red.transcript` |
| Restore proven by | sha256 of `mapper/mermaid.py` returned to the pre-mutation value after every mutant (`equal=True`) and the named nodes were GREEN again; the backup was taken after the baseline block was green and deleted at the end (`== backups deleted`) |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider` |
| Arms resolved at baseline | 10 named nodes, 10 PASSED in the baseline block (32 nodes seen, none failing) |
| Verdict granularity | per resolved node id |
| Arms that stayed GREEN | none |

| Mutant | Mutation (position and operation) | Nodes RED | Restore digest (equal to pre) |
|---|---|---|---|
| M-FX6 | `dump`: the `lines.insert(1, rline)` and `emitted.add(rline)` pair replaced by `pass` (hoist removed) | AT-086, `test_b117_reproduction_bytes`, `test_orphan_root_is_not_declared_twice`, `test_edge_parent_root_gets_a_standalone_line_first`, undo node, `test_save_accepts_legacy_forest_after_edit` (+ 6 parametrised) | `mermaid.py` 23e1e1f2ed6b…ab30b6 |
| M-FX6b | `emitted.add(rline)` dropped (orphan root declared twice) | AT-086, `test_b117_reproduction_bytes`, `test_orphan_root_is_not_declared_twice` (+ 1 parametrised) | equal |
| M-FX6c | `root_id not in written_children` guard dropped (a child root is hoisted) | `test_root_that_is_a_written_child_is_not_hoisted` | equal |
| M-FX7 | hoist fires whenever the root is not a written child (the "not text-first" test dropped; the root line is effectively always written) | `test_dump_fixture_goldens`, `test_at_076_real_save_dump_budget` (+ 2 parametrised byte-stability arms) | equal |
| M-FX12 | a third walk over `graph.edges` computes the written children | `test_dump_counted_ops_scaling_ratio`, `test_at_076_real_save_dump_budget` | equal |

M-FX6 reddens the new root assertion in `test_save_accepts_legacy_forest_after_edit` (LLR-FX.3.2). M-FX7 is a different failure from M-FX6: the goldens and AT-076 bytes drift instead of the root. M-FX6b and M-FX6c are two extra mutants I added for the duplicate-declaration and child-root guards.

**Declared deviation.** The first harness run read verdicts from `-v` text and reported three nodes as MISSING under M-FX7, because Textual's shutdown noise can share a line with the status. The harness was changed to read junit XML and the transcript was regenerated whole; the transcript on disk is the second run. A hand mutation attempt at M-FX7 during diagnosis failed on a line-ending anchor and changed nothing (digest checked).

| Field | Value |
|---|---|
| **RED counterfactual** | M-FX6, M-FX6b, M-FX6c, M-FX7, M-FX12 by position and operation as tabled; every restore digest equals the pre-mutation digest |
| **Mutation verdicts** | 5 mutants, 5 KILLED, 0 SURVIVED, 0 BAD (every anchor applied exactly once) |

### Instrument RED-proof

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| the node set (pytest) | the five mutants above, planted in `dump` | `FAILED` per node id in the transcript |
| the verdict reader | the first `-v` text reader on M-FX7 | reported MISSING instead of a verdict, which is how it was found unfit and replaced by junit XML |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 2 instruments, each shown able to report a failure before its pass was believed |

### Emitted-form assertion

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| saved `forest.mmd` re-read from disk | AT-086: second line is `    a[Alpha]`, `saved.count("a[Alpha]") == 1`, `MapStore.load(...).root_id == "a"` | passed |
| `dump` text | exact-bytes assertions in the TC-FX-3.1 nodes | passed |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts, each asserted against the form its producer emitted |

### Evidence files

| Evidence artifact | Path | SHA-256 |
|---|---|---|
| RED/restore transcript | `.dev-flow/2026-10-11-fixes-batch/evidence/inc002-red.transcript` | `bd7c5cdbac38e46120d9a82609484b16bc45448d657879feb2243360e0ea53b2` |

| Field | Value |
|---|---|
| **Evidence files** | 1 artifact at the declared home, cited with the digest of its stored bytes |

### Load-bearing emptiness (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes: "no duplicated declaration for an orphan root" rests on a fixture having an orphan root |
| Synthetic instance of the absent case | `test_orphan_root_is_not_declared_twice` builds one (`a[Alpha]` as orphan root) |
| Positive control for every probe that returned an ABSENCE | M-FX6b (duplicate emitted) turns `count == 1` RED |

### Reverse census — trigger family B (re-run at the increment cut)

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by other tests | `grep -rl "mermaid.dump\|dump_mermaid\|\bdump(" tests/*.py` | `perf_goldens_capture`, `test_csv_safety_store`, `test_fixes_csv_import`, `test_fixes_forest_root`, `test_inc9e`, `test_mermaid`, `test_mod_bodies`, `test_mod_compat`, `test_perf_dump`, `test_repair_cycles`, `test_search`; all run green (326 + 128 passed); only the two pins in §2 moved |
| B2 file moved on disk | `git diff --name-status --diff-filter=RD HEAD -- mapper tests` | empty |
| B3 golden drift | `git diff HEAD --stat -- tests/goldens` empty; `ls tests/goldens/perf/dump` = 8 files, all compared byte-for-byte by `test_dump_fixture_goldens` (green); `sha256sum` of `at076_saved_wide6000_after_add_child.mmd` equals the `HEAD` blob (`48115eb4…fd0ffd267`) and `test_at_076_real_save_dump_budget` is green | 0 golden changes |
| B4 artifact consumed elsewhere | `grep -rln "dump_mermaid" mapper` | `screens/map/undo.py` (snapshot, covered by TC-FX-3.3), `store.py` (save and round trip, covered by AT-086 and the csv-safety suite) |

| Field | Value |
|---|---|
| **Reverse census** | 4 probes (B1-B4) run with commands; 0 regressions; the visit bound passes unchanged (`<= 2E + 4`) |

### Correction population

| Field | Value |
|---|---|
| **Correction population** | none — one docstring sentence ("root drifts") replaced; `grep -c "root drifts" mapper/store.py` → 0 |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence |
|---|---|---|---|
| "a forest's root drifts on reparse" | 0 hits in `mapper/` | yes | `grep -rn "root drifts" mapper` |

### Signed-balance test ledger

`post = base − deleted + added`: 20 added (the new file; 11 of them are parametrised cases), 0 deleted; 2 existing nodes strengthened or re-fixtured, count unchanged.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (DeepSeek, independent of the author) — APPROVE-WITH-NITS, 0 HIGH / 0 MED; LOW-1 `mapper/store.py` docstring re-wrapped; LOW-2 not a defect (the `15 passed` premise counts two files); LOW-3 test name kept — renaming would desync the RED transcript that cites it, and the reviewer marked it optional |

---

## 5 · Risks

- A map already drifted on disk stays drifted: the declared root was never stored (PDR F2). Only maps whose root was set in-session (CSV import, `editing.py:221` after a root delete) benefit.
- A hoisted root that is an edge parent now appears as a standalone line before its edge line. `parse` accepts it (tested); a hand reader sees one extra line.
- `dump` now builds one list of orphans (previously streamed); a few words per orphan.

## 6 · Pending items / spec deviations

- Out-of-scope failure: `test_a3_census` pin 37 vs 38 caused by increment 001's helper (§4).
- Declared deviation about the first RED harness reader (§4).
- Independent review: recorded in §4b (APPROVE-WITH-NITS, 0 HIGH / 0 MED); reconciled at the DDR seal 2026-10-15.

## 7 · Suggested next task

Increment 003 (B-127: roles screen discovery on a worker thread).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 2 source files (§2) |
| 2 | Tests written in this same increment | all | ✓ | `tests/test_fixes_forest_root.py` + 2 pin moves |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | §4 layer 0 row |
| 4 | RED counterfactual declared | `core` · `full` | ✓ | §4, transcript sha256 cited |
| 5 | Reverse census declared | `core` · `full` | ✓ | §4 reverse census |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b: code-reviewer (DeepSeek) APPROVE-WITH-NITS, 0 HIGH / 0 MED |
| 7 | No file from another lane touched | all | ✓ | one lane; `git status` shows only the §2 files |
| 8 | Frozen interfaces untouched | all | ✓ | `dump(graph) -> str` signature unchanged; `parse` untouched |
| 9 | Coverage claims verified on disk | all | ✓ | node names resolved by the baseline run |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 table |
| 11 | Mutation verdicts declared per arm | all | ✓ | §4 table |
| 12 | Instrument RED-proof declared | all | ✓ | §4 |
| 13 | Correction population declared | all | ✓ | §4 |
| 14 | Emitted-form assertion declared | all | ✓ | §4 |
| 15 | Independent review names somebody | all | ✓ | §4b: DeepSeek (code-reviewer), independent of the author |
| 16 | Evidence files declared | all | ✓ | §4, sha256 |
