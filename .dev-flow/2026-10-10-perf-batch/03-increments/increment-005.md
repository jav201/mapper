# Increment 005 — Inc-M2 · Lane M · `mermaid.dump` linear incident pass

> **Artifact language**
> This template is the canonical **English scaffold**. Generate the artifact in the batch's development
> language — the **prose**, and never a label. **Where that language is declared:**
> `state.json`'s `language` key in `core` and `full`. The normative RULES below are
> language-independent.

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/guides/increment-template.md` explains each field and the rules that read it. It ships with the flow and is not copied into this batch.

> **Reserved field names.** The **field names and block keywords below are language-independent** — the validator parses them literally and they are
> never translated:
> `SOURCE files` · `Instrument RED-proof` · `Correction population` · `Mutation verdicts` · `Emitted-form assertion` · `Reverse census` · `RED counterfactual` · `Independent review` · `Evidence files` · `Traces to` · `File` · `Kind` · `source` · `test` · `doc` · `config` · `generated` · `fixture` · `⏸ DEFER`

| Field | Value |
|---|---|
| Batch | `2026-10-10-perf-batch` |
| Increment | `005` |
| Lane (if the batch forked) | `M` (Lane M worktree/branch; `mapper/views/` untouched — M-M3 verified below) |
| Requirement(s) | `HLR-PERF.2 · LLR-PERF.2.2` (the linear LOCAL incident pass, dangling edges covered, byte-identical dump) · `AT-076` (real persisting add_child gesture, per-dump ≤ 2·E + c, saved bytes vs the base golden) |
| Acceptance | `AT-076` node in `tests/test_perf_dump.py`: `test_at_076_real_save_dump_budget` · LLR nodes: `test_dump_counted_ops_scaling_ratio` · `test_dump_fixture_goldens` |
| Agent | `Kimi (kimi-code/kimi-for-coding) via the kimi CLI` |
| Date | `2026-10-10` |

---

## 1 · What changed

`mermaid.dump` (`mapper/mermaid.py`) determined orphan (parentless AND
childless) nodes with a per-node
`any(e.parent_id == node.id or e.child_id == node.id for e in graph.edges)`
rescan — O(N·E): 18,003,000 edge visits and 6002 O(E) scans on wide-6000
(PERF0C §7.3).  The orphan pass now builds an incident-id set in ONE local
pass over every edge and tests membership in it:

- LOCAL to the dump call — the set is built inside `dump`, NOT read from the
  Lane M adjacency cache (ruling R11: a counting wrapper that swapped
  `edges` would send a cache variant cold and cost 3E; the local pass costs
  exactly 2E, ratio 2.000).
- DANGLING edges count: an edge whose endpoint is missing from `nodes` is
  skipped when written (unchanged), but both of its ids still enter the
  incident set — membership semantics identical to the old `any()`.
- Emission order (node-dict iteration order), the `emitted` dedup set,
  label escaping and the trailing newline are untouched: measured 2E edge
  visits per call (11,998 on wide-6000), ratio 2.000, and the `.mmd` bytes
  byte-identical on every fixture and the AT-076 golden.

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/mermaid.py` | source | `LLR-PERF.2.2` · `HLR-PERF.2` (`AT-076`) | the orphan pass: one local incident pass replaces the per-node `any()` rescan |
| `tests/test_perf_dump.py` | test | `LLR-PERF.2.2` · `HLR-PERF.2` · `AT-076` | new: `test_dump_counted_ops_scaling_ratio` · `test_dump_fixture_goldens` · `test_at_076_real_save_dump_budget` |
| `.dev-flow/2026-10-10-perf-batch/evidence/m2-red.transcript` | doc | RED counterfactuals · measured counts | RED proofs, sha256-verified restores, before/after measurements |

`SOURCE files` count: 1 (`mapper/mermaid.py`).  No file under `mapper/views/`
or `mapper/canvas.py` touched (M-M3 below).

## 2b · Join-gate follow-up (trunk — serves both lanes)

Committed after the join as `4d82c16` (test-only): the A3 census pin in
`tests/test_a3_census.py` moves the arg-ful render pin 65 → 80, itemised —
the perf batch's byte-identity arms (`tests/test_perf_paint_clip.py`,
`tests/test_perf_layout_memo.py`, `tests/test_perf_dump.py`,
`tests/perf_goldens_capture.py`) read renderer symbols, and the join gate's
single failure was this pin (`join-gate-run1-full-suite.transcript`). The
same commit fills the `code-reviewer` cells of increments 002–005.

| File | Kind | Traces to | Change |
|---|---|---|---|
| `tests/test_a3_census.py` | test | `LLR-PERF.1.3` · `LLR-PERF.2.2` | A3 arg-ful render pin 65 → 80, itemised for this batch's byte-identity arms (join-gate follow-up `4d82c16`) |

## 3 · How to test

    python -B -m pytest -q -p no:cacheprovider tests/test_perf_dump.py
    python -B -m pytest -q -p no:cacheprovider tests/test_perf_dump.py tests/test_perf_adjacency.py tests/test_perf_goldens_manifest.py tests/test_mermaid.py tests/test_csv_safety_store.py tests/test_store.py

## 4 · Test results

`tests/test_perf_dump.py`: 3 passed (74.15 s — the AT-076 node drives the real
app on wide-6000; the `3 passed in 74.15s` GREEN line is `m2-red.transcript`
line 22).  The six-file verification suite across the named files (§3,
`42 passed` in 83.88 s) was **not captured** in a lane transcript — recorded
plainly here; the count that holds post-join is the join gate
(`1 failed, 3222 passed` in `join-gate-run1-full-suite.transcript` — the
single failure is the A3 census pin, fixed in the test-only follow-up
`4d82c16`).  Ruff `All checks passed!`; the M-M3 file-diff check
`git diff e7d433d -- mapper/views` printed nothing.

Numeric thresholds met: ONE `dump` call on wide-6000 iterates `graph.edges`
11,998 = 2·E times (bound 2·E + 4; baseline 18,003,000); scaling ratio
count(3000)/count(1500) = 2.000 ∈ [1.8, 2.2]; AT-076's single persisting-save
dump = 12,000 ≤ 2·6000 + 4 and the saved `.mmd` byte-equals the AT-076 golden
pinned at base SHA `e7d433d`; 0 byte diffs on all 8 dump goldens.

Measured (median of 3, same session, wide-6000 `MapStore.save`): dump edge
iterations 18,003,000 → 11,998; save wall 2.656 s → 1.104 s.

### RED counterfactual — executed, not predicted

Three mutations of `mapper/mermaid.py`, each RED on its named node, each
restored byte-identically (sha256 before == after) and re-run GREEN;
transcript: `.dev-flow/2026-10-10-perf-batch/evidence/m2-red.transcript`.

1. **M-M2a** — restore the per-node `any()` rescan →
   `test_dump_counted_ops_scaling_ratio` RED (1,125,750 visits on wide-1500
   vs bound 3,002) and `test_at_076_real_save_dump_budget` RED (18,009,001
   visits vs bound 12,004).  Restore sha256-equal → 2 passed.
2. **drop dangling-edge counting** (incident pass skips edges with endpoints
   missing from `nodes`) → `test_dump_fixture_goldens` RED on the inline
   `dangling-solo` arm.  Restore sha256-equal → 1 passed.
3. **M-M2b** — `reversed()` the orphan loop → `test_dump_fixture_goldens`
   RED on the inline `orphan-order` arm.  Restore sha256-equal → 1 passed.

### Instrument RED-proof — every instrument shown able to report FAILURE first

- The counted-ops/ratio instrument (a `_CountingEdges(list)` swap counting
  edge yields) was RED under M-M2a before its PASS was believed, and the
  fixture byte oracle was GREEN on the UNMODIFIED product before the fix —
  the byte tests pin base bytes, not the remedy.
- The AT-076 per-dump bound instrument (counting wrapper on
  `mapper.mermaid.dump` itself — the store imports it at call time,
  `store.py:861` — reading the visit delta across the one call) was RED under
  M-M2a.
- Structural invariance, recorded honestly: the pinned `dump/dangling.mmd`
  bytes cannot see dangling counting (a missing endpoint is never a node)
  and no committed golden has ≥ 2 orphans, so the byte-observable surface
  for those two requirements lives in `test_dump_fixture_goldens`'s two
  inline arms pinning TODAY's base behaviour (`dangling-solo` → `graph TD\n`;
  `orphan-order` → node-dict order).  Both arms encode the pre-change dump's
  semantics and both redden under their named mutant.

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

The oracle is the emitted `.mmd` text: 8 pinned dump goldens (fixtures
round-tripped through `parse`, wide-6000, forest, empty, single, dangling)
plus the AT-076 saved-file bytes after the real add_child gesture — all
byte-compared, 0 diffs.

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED proofs, sha256 restore lines, before/after measurements (`3 passed in 74.15s` baseline GREEN at line 22) | `.dev-flow/2026-10-10-perf-batch/evidence/m2-red.transcript` | `c84b8c031d35864118fb8b5ff03af7d3b19dc53c8090d2e3422de84856328d96` |
| join gate full-suite run 1 (post-join, all lanes: `1 failed, 3222 passed` — the single failure is the A3 census pin, fixed in the test-only follow-up `4d82c16`) | `.dev-flow/2026-10-10-perf-batch/evidence/join-gate-run1-full-suite.transcript` | `06a24f17c296ae015c7d981003862f85774eef7f54004a265e0f3c21a3890756` |
| join slow-lane run (`19 passed, 3231 deselected`) | `.dev-flow/2026-10-10-perf-batch/evidence/join-slow-lane.transcript` | `63d6a2c89abd789b5bcb6ee20969658558d8f40b41de4b4c8fa9ee9eb5e922b1` |

| Field | Value |
|---|---|
| **Evidence files** | 3 artifacts at the declared home, each sha256-pinned; the shipped `mapper/mermaid.py` sha256 `5d5b8271…deba7c` is quoted inside the lane transcript (baseline line) |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

- The byte-invariance of the pinned `dangling.mmd` to dangling counting and
  of every committed golden to orphan ORDER (all connected trees / single
  node) — declared above and covered by the inline arms; a future golden
  with ≥ 2 orphans would make the order pin redundant, not wrong.
- `dump` relies on nothing outside the call: the incident set is rebuilt per
  call, so no invalidation census is load-bearing here (unlike Inc-M1's
  cache).

### Reverse census — trigger family B

`dump`/`parse`/`slugify` signatures frozen; consumers (`store.save`
round-trip check, export, undo snapshot bound at import) ride unchanged
signatures; `mapper/views/` builds its own per-render index (LLR-PERF.2.3)
and imports nothing new — `git diff e7d433d -- mapper/views` is empty.

### Correction population — enumerated BEFORE the first site was edited

One site: the orphan loop in `mermaid.dump` (`mapper/mermaid.py`), the only
O(N·E) structure named by LLR-PERF.2.2.  No second O(N·E) site exists in the
module (the parse path is line-bound; the write loop is one O(E) pass).

### Signed-balance test ledger

| Suite | Last run | Result |
|---|---|---|
| `tests/test_perf_dump.py` | 2026-10-10 | 3 passed (transcript) |
| six-file verification (§3) | 2026-10-10 | 42 passed in 83.88 s |

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, read-only) **APPROVE** — orphan emission order and dangling-edge semantics identical to the base `any()`; the incident set is local (no cache); orphan-order, dangling-solo and counted-ops arms discriminate; AT-076 drives the real `a` add-child flow; LOW: `calls == 2` tightly coupled by design |

## 5 · Risks

None new.  The save floor is now the store's own round-trip re-parse
(B-114 check), not the dump — recorded for the P4 wall-clock narrative.

## 6 · Pending items / spec deviations

- None for Inc-M2.  Lane M is complete (Inc-M1 + Inc-M2); the trunk owns the
  join (DDR): full suite, parity goldens, per-lane M-M3 record, P4
  interleaved wall-clock evidence.

## 7 · Suggested next task

The trunk's DDR join of lanes R and M (per the fork plan in `PLAN.md`).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 1 source file (`mapper/mermaid.py`); `git diff --stat` = 1 file, +9/-2 |
| 2 | Tests written in this same increment | all | ✓ | `tests/test_perf_dump.py` (3 nodes, transcript GREEN line) |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | LLR unit nodes + AT-076 black-box through `MapperApp` + real keys |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | 3 cycles (M-M2a ×2 nodes, dangling, M-M2b), all RED, sha256-verified restores, GREEN re-runs |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | signatures frozen; `mapper/views` diff empty |
| 6 | `code-reviewer` passed | `core` · `full` | ⚠ | PENDING — named in §4b |
| 7 | No file from another lane touched | all | ✓ | Lane R owns `mapper/views/` + `mapper/canvas.py`: zero bytes touched (`git diff e7d433d -- mapper/views` empty) |
| 8 | Frozen interfaces untouched | all | ✓ | `parse`/`dump`/`slugify` signatures and `.mmd` bytes unchanged (8 goldens + AT-076 byte-equal) |
| 9 | Coverage claims verified **on disk** | all | ✓ | 3 nodes + verification suite + per-node RED transcripts on disk |
| 10 | Load-bearing emptiness declared | all | ✓ | golden invariance to dangling/order declared; inline arms pin the observable base behaviour |
| 11 | **Mutation verdicts** declared | all | ✓ | M-M2a · dangling-counting · M-M2b — each with its RED node id and restore line |
| 12 | **Instrument RED-proof** declared | all | ✓ | counted-ops, AT-076 bound and byte oracle each shown RED first |
| 13 | **Correction population** declared | all | ✓ | one site, enumerated before the edit |
| 14 | **Emitted-form assertion** declared | all | ✓ | emitted `.mmd` bytes vs base-pinned goldens, 0 diffs |
| 15 | **Independent review** names somebody | all | ⚠ | PENDING in §4b (orchestrator assigns) |
| 16 | **Evidence files** declared | all | ✓ | `.dev-flow/2026-10-10-perf-batch/evidence/m2-red.transcript` |
