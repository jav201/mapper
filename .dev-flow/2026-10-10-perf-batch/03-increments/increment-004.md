# Increment 004 — Inc-R2 · Lane R — unscaled `_tree_layout` memo (counted layout computations)

> **Artifact language.** Canonical English scaffold; the batch's development
> language is English. The normative RULES in the template preamble are
> language-independent and enforced regardless.

| Field | Value |
|---|---|
| Batch | `2026-10-10-perf-batch` |
| Increment | `004` |
| Lane (if the batch forked) | `Lane R` (renderer work per paint) |
| Requirement(s) | `HLR-PERF.1` (LLR-PERF.1.2 memo part and LLR-PERF.1.3) · `LLR-PERF.1.2` · `LLR-PERF.1.3` |
| Acceptance | `AT-075b` (`tests/test_perf_layout_memo.py::test_at_075b_memo_misses_and_golden`) · `tests/test_perf_layout_memo.py::test_memo_miss_spy` · `tests/test_perf_layout_memo.py::test_memo_invalidation_arms` (7 arms) · `tests/test_perf_layout_memo.py::test_memo_id_reuse` · `tests/test_perf_layout_memo.py::test_nodes_writer_census` (+16 planted-form arms) |
| Agent | `Kimi (kimi-code/kimi-for-coding) via the kimi CLI` |
| Date | `2026-10-10` |

---

## 1 · What changed

`mapper/views/layered.py`: the scaling-free core `_tree_layout_unscaled`
(in-order leaf slots + level per node) is memoised on the OWNING
`LayeredRenderer` INSTANCE and passed into module-level `_geometry` as an
argument (ruling R12: no module-global memo state, which would leak across
screens and pin `Graph`s). The key is strong references compared with `is` plus
lengths — `graph`, its `edges` list (+len), its `nodes` dict (+len), `root_id`,
`hidden` — so in-place appends (same list, new length) miss, wholesale
replacement misses, and allocator address reuse cannot fake a hit because the
entry itself pins the old graph. A hit re-uses the UNSCALED slots and re-applies
the `card_w`/`gap` scaling per call in O(N): a resize or a widening-title edit
changes the scaling, never the slots. The miss spy is the named instance
counter `LayeredRenderer._layout_misses`, incremented at the hit check inside
`_geometry` (`_tree_layout` itself runs ~10x per two renders,
`evidence/perf0c-nav.transcript:44`, so invocations are not countable).
Module-level callers `painted_ids`/`pan_extent` pass no memo and always compute
fresh. Rendered bytes are unchanged (AT-075/075b goldens still byte-match,
pinned at base SHA `e7d433d`).

Measured (AT-075 session, `evidence/r2-red.transcript` §1): BEFORE, the
wide-2000 nav session cost **10 `_tree_layout` computations per 2 renders**
(perf0c-nav profile). AFTER, open + five selection-only keypresses at 118x34
through the real app cost exactly **1** layout computation; the archive
structural edit costs exactly **1 more** (2 total). Selection-only navigation
went from ~5 computations per render to zero; every painted step byte-equals
the base golden.

## 2 · Files modified

**The budget counts SOURCE files only.**

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/views/layered.py` | source | `LLR-PERF.1.2` · `LLR-PERF.1.3` · `HLR-PERF.1` (`AT-075b`) | unscaled `_tree_layout` memo on the renderer instance (strong-reference key, scaling re-applied per call); `_layout_misses` spy at the hit check inside `_geometry` |
| `tests/test_perf_layout_memo.py` | test | `LLR-PERF.1.2` · `LLR-PERF.1.3` · `AT-075b` | new: miss-spy layer-0 node; AT-075b real-app session (miss counts + golden bytes); the seven named invalidation arms; M-R2d address-reuse node (ruling R13); the `Graph.nodes` writer census + 16 planted-form detector arms (ruling R14) |
| `.dev-flow/2026-10-10-perf-batch/evidence/r2-red.transcript` | doc | RED counterfactuals · measured counts | commands + outputs of the GREEN runs, the before/after measurement, and the five mutation proofs (relative paths) |
| `tests/test_a3_census.py` | test | `LLR-PERF.1.3 · LLR-PERF.2.2` | join-gate follow-up `4d82c16`: arg-ful render pin 65 → 80, the 15 new byte-identity render sites itemised in the pin's comment |

| Count | Value |
|---|---|
| **SOURCE files** | **1** / 4 |
| Test files | 1 (uncapped) |
| Doc files | 1 transcript (outside the count) |

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_perf_layout_memo.py tests/test_perf_paint_clip.py tests/test_perf_goldens_manifest.py tests/test_mod_parity.py tests/test_repair_golden_census.py
ruff check mapper/views/layered.py tests/test_perf_layout_memo.py
```

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `tests/test_perf_layout_memo.py::test_memo_miss_spy` | passed — 5 repeated renders cost exactly 1 miss, byte-identical |
| **A/B · black-box** | `core` · `full` | `tests/test_perf_layout_memo.py::test_at_075b_memo_misses_and_golden` | passed — open + `l,j,j,j,j` cost 1 miss; archive + `l` cost 2; every painted step byte-equals the golden pinned at base SHA `e7d433d` |
| **A/B · black-box** | `core` · `full` | `tests/test_perf_layout_memo.py::test_memo_invalidation_arms[resize\|title\|fold\|focus\|undo\|add_child\|round_trip]` | passed — scaling-only changes 0 extra misses + byte-identical repaint; structural changes miss exactly once; round trip 0 extra misses |
| **0 · unit** | `core` · `full` | `tests/test_perf_layout_memo.py::test_memo_id_reuse` | passed — a new `Graph` object always misses |
| gate | | `test_nodes_writer_census` + 16 planted-form arms | passed — the declared two-writer census holds; every banned in-place/alias form is detected |
| gate | | the §3 four-file run (`55 passed total`) | **not captured** in a lane transcript — recorded plainly here; the counts that hold are this packet's own RED transcript (`1 passed` per GREEN run at `r2-red.transcript` lines 55/60/70/77/102/119, `2 passed` post-restore at line 156) and, post-join, the join gate (`1 failed, 3222 passed` in `join-gate-run1-full-suite.transcript` — the single failure is the A3 census pin, fixed in the test-only follow-up `4d82c16`; the failures in this packet's own transcript are the five deliberate RED mutations, §RED counterfactual) |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation 1 | M-R2 (no memo, `cached = None`) → `test_at_075b_memo_misses_and_golden` RED: `AssertionError: open cost 4 misses, want exactly 1` (`tests/test_perf_layout_memo.py:121`) |
| Mutation 2 | M-R2b (drop the `hidden` key conjunct) → `test_memo_invalidation_arms[fold]` RED: `assert 1 == (1 + 1)` (`tests/test_perf_layout_memo.py:260`) — the fold re-render hit the stale entry |
| Mutation 3 | M-R2c (cache the SCALED pos, key unchanged) → `test_memo_invalidation_arms[resize]` RED at its renderer-level byte compare (`tests/test_perf_layout_memo.py:202`). `[title]` stayed green and is RECORDED PLAINLY: measured, at 118x34 the fold-tree canvas is header-only (every card lies outside the viewport in both mutant and fresh), so the arm's region-clipped byte compare cannot see geometry drift that never reaches the viewport; the `resize` arm's full-text `.plain` compare does see it and reddens |
| Mutation 4 | M-R2d (key on `id(graph)`, strong reference dropped) → the address-reuse node could NOT be driven RED deterministically on this interpreter, RECORDED PLAINLY per the glossary escape clause (`01-requirements.md:498`, ruling R13): 8/8 runs green, a 2000-allocation forced-reuse probe measured 0 address collisions (the old graph IS collected — verified by `weakref` — but its address is never recycled into the next same-shape `Graph`), and `[undo]` stays green because the undo snapshot pins the old graph. The shipped strong-reference key makes the reuse it would exploit un-fakeable BY CONSTRUCTION |
| Mutation 5 | M-R2e (planted `setitem` `nodes` writer site, transiently in the scanned package) → `test_nodes_writer_census` RED: extra item `('mapper/views/layered.py', '_planted_m2re_writer', 'setitem')` (`tests/test_perf_layout_memo.py:562`) |
| Instrument | project code mutated in the worktree; each restore checked by sha256 |
| Where it ran | this worktree (Lane R's branch) |
| Transcript | `.dev-flow/2026-10-10-perf-batch/evidence/r2-red.transcript` |
| Restore proven by | sha256 before == after for every mutation: `3e34fd90426b30fc9dbdf4dc8ade90de8ba7404ab232c58283c124d6e8e04743` |
| Bytecode cache | `python -B` and `-p no:cacheprovider` throughout |
| Arms resolved | M-R2 killed by the AT-075b counted oracle (named); M-R2b killed by the `[fold]` arm (named); M-R2c killed by the `[resize]` arm (named; `[title]` blindness measured and recorded); M-R2d documented non-deterministic on this interpreter with the measured probe (escape clause); M-R2e killed by the census guard (named) |

| Field | Value |
|---|---|
| **RED counterfactual** | 5 named mutations: 3 executed → RED on their named nodes, 1 executed → RED on its named node with the sibling arm's blindness measured and recorded, 1 executed → documented non-deterministic with the measured probe — every restore sha256-verified, every node re-run GREEN |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `test_at_075b_memo_misses_and_golden` (miss-count + golden) | M-R2 mutant (no memo) | `AssertionError: open cost 4 misses, want exactly 1` |
| `test_memo_invalidation_arms[fold]` (structural-input arm) | M-R2b mutant (`hidden` dropped from the key) | `AssertionError: folding a branch must miss exactly once` |
| `test_memo_invalidation_arms[resize]` (scaling-only arm) | M-R2c mutant (scaled pos cached) | `AssertionError` at the renderer-level byte compare (`:202`) |
| `test_nodes_writer_census` (writer tripwire) | M-R2e mutant (planted `setitem` writer) | `AssertionError` listing the planted site (`:562`) |
| `test_memo_id_reuse` (identity node) | M-R2d mutant (`id()` key) | kept GREEN on this interpreter — the measured 0-collision probe and the pinning analysis are recorded in the transcript §4 instead of a fabricated RED |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 instruments each shown RED before their PASS was believed; the fifth documented as non-deterministic-on-this-interpreter with its measurement, not asserted |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the painted canvas rows (app session) | `test_at_075b_memo_misses_and_golden` compares the `#map-canvas` region strips after open / each keypress / archive against the pinned golden `tests/goldens/perf/at075_075b_wide2000_118x34.txt` (base SHA `e7d433d`) | equal — 0 diffs across all 7 painted steps |
| the rendered grid text | `test_memo_invalidation_arms[resize\|title]` compares full `render().plain` text against a fresh renderer's paint | byte-identical (and this is the exact conjunct M-R2c reddens) |
| the folded/unfolded canvas | `test_memo_invalidation_arms[fold]` | unfold repaints byte-identically to the unfolded map |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 3 artifacts, each asserted against the form its producer emits |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED proofs + GREEN verifications + before/after measurement | `.dev-flow/2026-10-10-perf-batch/evidence/r2-red.transcript` | `82695d1e7c5717da2518a1f1274854fc5e01c97e96be2c587ee431a026dca5cc` |
| join gate full-suite run 1 (post-join, all lanes: `1 failed, 3222 passed` — the single failure is the A3 census pin, fixed in the test-only follow-up `4d82c16`) | `.dev-flow/2026-10-10-perf-batch/evidence/join-gate-run1-full-suite.transcript` | `06a24f17c296ae015c7d981003862f85774eef7f54004a265e0f3c21a3890756` |
| join slow-lane run (`19 passed, 3231 deselected`) | `.dev-flow/2026-10-10-perf-batch/evidence/join-slow-lane.transcript` | `63d6a2c89abd789b5bcb6ee20969658558d8f40b41de4b4c8fa9ee9eb5e922b1` |

| Field | Value |
|---|---|
| **Evidence files** | 3 artifacts at the declared home, each sha256-pinned; the shipped `mapper/views/layered.py` sha256 `3e34fd90…e04743` is quoted inside the lane transcript |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Resting on an absence? | no — the byte-identity rests on a PRESENCE (`_tree_layout_unscaled` reads exactly the key's inputs: child index, `nodes`, `edges`, `root_id`, hidden set; each key conjunct is armed by a named arm). The census guard is an AST scan with documented limits (aliasing through arguments/containers/attributes is not detected, stated in the node) |
| Guard labelled as protecting a CONCLUSION? | the 16 planted-form arms prove the detector flags every banned form (against a vacuous never-fires census); the miss-spy layer-0 node proves the counter counts misses, not invocations |
| Conjunctive criteria | the AT-075b node carries two conjuncts (miss count; painted bytes). M-R2 reddens the count conjunct while the painted bytes stay correct — proving the count is not carried by the bytes. M-R2c reddens `resize` through the byte conjunct while the miss count stays green — the two instruments fail independently (transcript §5, §7) |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by other tests | `grep -rl "_layout_misses\|_tree_layout_unscaled" tests/ mapper/` | the spy and the memo are read only by `tests/test_perf_layout_memo.py`; `painted_ids`/`pan_extent` keep calling `_geometry` with no memo — both re-run GREEN in §1 |
| B3 byte-identical golden captures this source | `tests/test_perf_goldens_manifest.py` + `test_render_grid_clip_identity` | every render golden re-compared against the CURRENT product: 0 diffs (the re-comparison runs are the `1 passed`/`2 passed` GREEN lines of `r2-red.transcript`; the lane-wide 55-run was not captured — §4 gate row) |
| B4 artifact consumed elsewhere | `grep -rl "goldens/perf" tests/` | `tests/test_perf_layout_memo.py` (this increment) plus the Inc-R1 consumers; the AT-075/075b golden bytes are untouched |
| A3 | `git diff` of `mapper/views/layered.py` vs HEAD | bodies/docstrings + the memo block only; `_tree_layout` (module-level single-call form) signature kept for the no-memo callers and the test oracles |

| Field | Value |
|---|---|
| **Reverse census** | 4 probes run (B1 · B3 · B4 · A3), each with its command and verdict |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population | Enumeration method | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| unscaled layout to memoise | the scaling-free layout core | `_tree_layout` split into `_tree_layout_unscaled` (pure: slots + level) + scaling; the memo caches exactly the pure part | 1 (`layered.py:192-262` + hit check at `layered.py:407-443`) | 1 | the per-call derived state (`widest`, squeeze, pills, pan, body rows) reads titles/width/diff and is re-derived per call — caching it would be M-R2c's exact defect |

| Field | Value |
|---|---|
| **Correction population** | 1 site, enumerated before editing; everything below the hit check stays per-call by construction |

### Signed-balance test ledger

`post = base − deleted + added` → `1 = 0 − 0 + 1` SOURCE file changed; `1 = 0 − 0 + 1` new test file ✓ reconciles

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, read-only) **APPROVE-WITH-NITS**, 0 HIGH/MED — key complete for every input of the unscaled layout (edges/nodes/root/folds; focus builds a new Graph); title/resize/theme only rescale; add child, archive, undo, fold miss; `_geometry` callers compatible; LOWs: parameter naming, O(N) rescale per hit, edges rely on frozen `Edge` + no in-place writers |

---

## 5 · Risks

- The memo key must track every input `_tree_layout_unscaled` reads. A future
  read of new graph state without a key conjunct is a stale-layout defect the
  seven arms catch only if an arm names that input — the `Graph.nodes` writer
  census (ruling R14) guards the in-place-mutation side, and M-R2b's executed
  RED shows one dropped conjunct is caught by its arm.
- M-R2d could not be executed RED on this interpreter; the soundness it would
  test rests on the strong-reference key's construction argument (ruling R13),
  not on a demonstrated failure. A future runtime where addresses are recycled
  would make the `id()`-keyed mutant fail there; the shipped key cannot.
- M-R2c's `[title]` arm is viewport-blind at this fixture (header-only canvas at
  118x34): a geometry-only drift invisible in the emitted canvas bytes would
  not be caught by that arm — the `[resize]` arm's full-text compare is the
  covering instrument and is named in the transcript.

## 6 · Pending items / spec deviations

- LLR-PERF.1.2's M-R2d negative control is documented as
  non-deterministic-on-this-interpreter (escape clause exercised and recorded,
  transcript §4) rather than executed RED. No other deviations.
- The AT-075/075b golden file this increment reads was pinned by the trunk at
  PERFG0 (base SHA `e7d433d`).

## 7 · Suggested next task

Trunk DDR join with Lane M (the batch gate): independent `code-reviewer` pass
on increments 001–004, then the DDR's cross-lane golden re-verification.

## 8 · DDR follow-up — unit PERFDDR2 (DDR conditions applied)

The DDR reviewers (architect Claude Opus + qa Claude Sonnet) returned
approve-with-conditions; the test-affecting conditions were applied in unit
PERFDDR2 (this unit), test files only — no product byte changed permanently:

| Condition | Fix | Proof |
|---|---|---|
| qa MED-2 — the `[title]` arm was blind to M-R2c (viewport-clipped canvas compare, header-only at 118×34) | the arm gains a RENDERER-LEVEL full-text compare (`screen.renderer.render(screen.graph, state).plain` vs a fresh `LayeredRenderer` at the app's own `_view_state`); the app-level canvas compare stays alongside | M-R2c now reddens BOTH `[title]` and `[resize]`; restore sha256-verified (`3e34fd90…e04743`) — `evidence/ddr2-red.transcript` §2 |
| qa LOW-4 — the wire cap dated from the unclipped baseline | `WIRE_CAP` 1,200,000 → **61,500** = 5× the measured 12,264 (61,320, rounded up), derivation in the node docstring and in HLR-PERF.1 / LLR-PERF.1.1 (`01-requirements.md`, ledger `LED-2026-10-10-perf-batch.5`) | y-only clip RED (23,983,998), removed clip RED (23,983,998), widened-span clip RED (88,226 ≈ 7.2×) — `evidence/ddr2-red.transcript` §3–§5; restores sha256-verified (`d354bd46…4838a2`) |

Transcript: `.dev-flow/2026-10-10-perf-batch/evidence/ddr2-red.transcript`,
sha256 `b5a08f19f35594259270578b8eb95996ce26deb8eb1358897c6e5bdc39b1f3b0`.
The remaining conditions are documentary and live in `01-requirements.md`
(rewording + `(withdrawn, B-118)` markings + ledger `.5`), `.dev-flow/BACKLOG.md`
(B-120) and the DDR itself (C4 ⚠, B5 ledger sum with `GATE_JOIN2_PENDING`,
participants, goldens line-endings note).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files | all | ✓ | 1 SOURCE file (`mapper/views/layered.py`); §2 count table |
| 2 | Tests written in this same increment | all | ✓ | `tests/test_perf_layout_memo.py` — 26 nodes |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `test_memo_miss_spy` · `test_nodes_writer_census` + 16 planted-form arms |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | 5 named mutations — M-R2/M-R2b/M-R2c( resize)/M-R2e executed RED on their named nodes; M-R2d documented non-deterministic with its measurement; every restore sha256-verified — transcript §3–§7 |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 4 probes in the table above |
| 6 | `code-reviewer` passed | `core` · `full` | ⚠ | PENDING — named in §4b |
| 7 | No file from another lane touched | all | ✓ | only `mapper/views/layered.py` + this lane's test; `git status` shows no `model.py`/`mermaid.py`/`screens/` change |
| 8 | Frozen interfaces untouched | all | ✓ | `_tree_layout` module-level signature kept; `keymap.py`/`darkside.py`/`app.py` re-export block untouched; no new painted string |
| 9 | Coverage claims verified **on disk** | all | ✓ | every painted step byte-equals the pinned golden; the render-grid goldens re-compared (per-run GREEN lines in `r2-red.transcript`; the lane-wide 55-run was not captured — §4) |
| 10 | Load-bearing emptiness declared | all | ✓ | table above — census scan limits stated; planted-form guards named; count/byte conjuncts fail independently |
| 11 | **Mutation verdicts** declared | all | ✓ | M-R2 killed (AT-075b count RED), M-R2b killed (`[fold]` RED), M-R2c killed (`[resize]` RED; `[title]` blindness measured), M-R2d documented (escape clause), M-R2e killed (census RED) — per named node |
| 12 | **Instrument RED-proof** declared | all | ✓ | 4 instruments fed known-bad mutants first; the fifth's non-determinism measured, not asserted |
| 13 | **Correction population** declared | all | ✓ | 1 site enumerated before editing |
| 14 | **Emitted-form assertion** declared | all | ✓ | canvas region strips, full render text, folded canvas — each asserted on the emitted form |
| 15 | **Independent review** names somebody | all | ⚠ | PENDING in §4b (orchestrator assigns) |
| 16 | **Evidence files** declared | all | ✓ | `.dev-flow/2026-10-10-perf-batch/evidence/r2-red.transcript` (sha256 quoted in §4) |
