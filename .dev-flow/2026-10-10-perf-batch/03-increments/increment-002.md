# Increment 002 — Inc-R1 · Lane R — `Canvas` span clipping (byte-identical paint)

> **Artifact language.** Canonical English scaffold; the batch's development
> language is English. The normative RULES in the template preamble are
> language-independent and enforced regardless.

| Field | Value |
|---|---|
| Batch | `2026-10-10-perf-batch` |
| Increment | `002` |
| Lane (if the batch forked) | `Lane R` (renderer work per paint) |
| Requirement(s) | `HLR-PERF.1` (LLR-PERF.1.1 span clip part, the AT-075 wire-budget part, and LLR-PERF.1.3) · `LLR-PERF.1.1` · `LLR-PERF.1.3` |
| Acceptance | `AT-075` (`tests/test_perf_paint_clip.py::test_at_075_keypress_wire_budget`) · `tests/test_perf_paint_clip.py::test_wire_count_budget` · `tests/test_perf_paint_clip.py::test_bare_canvas_clip_equality` · `tests/test_perf_paint_clip.py::test_render_grid_clip_identity` |
| Agent | `Kimi (kimi-code/kimi-for-coding) via the kimi CLI` |
| Date | `2026-10-10` |

---

## 1 · What changed

`Canvas.elbow_down` and `Canvas.edge` (`mapper/canvas.py`) now clip every span
to the canvas rectangle BEFORE iterating: `edge` iterates
`range(max(0, min(y0,y1)), min(h-1, max(y0,y1)) + 1)`; `elbow_down` iterates
the vertical drop over `range(max(0, y0+1), min(ybus, h))` (bus row wired only
when `0 <= ybus < h`) and the bus row over `range(max(0, xa+1), min(xb, w))`.
Out-of-canvas cells are never visited; every skipped cell is one `wire` already
dropped (`canvas.py:107-109`, requirements premise 2), so every painted cell —
and the order the layers converge in `rows()` — stays byte-identical, at
O(painted) instead of O(span) iterations. Signatures untouched (PDR SS4 row
frozen: bodies only). Lane M's files and every banned shared seam
(`mapper/app.py` re-exports, `mapper/keymap.py`, `mapper/darkside.py`,
`screens/map/*`) are untouched.

Measured (AT-075, recorded in `evidence/r1-red.transcript` SS2): the scripted
two-keypress session (`l`, `j`) on wide-2000 at 118x34 through the real app,
wire counter reset after mount, performs **12,264 `Canvas.wire` calls** —
under the ≤ 1,200,000 cap (≈ 1/20 of the 23,983,998 baseline; actually ≈
1/1957) and matching round-2 probe p4's x-clipped order (6,547/render at
wide-2000). Painted canvas rows after open, `l`, `j` byte-equal the golden
pinned at base SHA `5cde04e`.

## 2 · Files modified

**The budget counts SOURCE files only.**

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/canvas.py` | source | `LLR-PERF.1.1` · `LLR-PERF.1.3` · `HLR-PERF.1` (AT-075) | clip `elbow_down`/`edge` spans to the canvas rectangle before iterating (bodies only; signatures frozen) |
| `tests/test_perf_paint_clip.py` | test | `LLR-PERF.1.1` · `LLR-PERF.1.3` · `AT-075` | new: bare-`Canvas` equality vs in-test reference copies of the pre-change loops; render-grid identity vs the base goldens (builders imported from `tests/perf_goldens_capture.py`); wire-count budget + AT-075 black-box session with the counting wrapper and post-mount counter reset |
| `.dev-flow/2026-10-10-perf-batch/evidence/r1-red.transcript` | doc | RED counterfactuals · measured count | commands + outputs of the GREEN verification, the measured wire count, and the three RED proofs (relative paths) |

| Count | Value |
|---|---|
| **SOURCE files** | **1** / 4 |
| Test files | 1 (uncapped) |
| Doc files | 1 transcript (outside the count) |

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_perf_paint_clip.py tests/test_perf_goldens_manifest.py tests/test_mod_parity.py tests/test_repair_golden_census.py
ruff check mapper/canvas.py tests/test_perf_paint_clip.py
```

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `tests/test_perf_paint_clip.py::test_bare_canvas_clip_equality` (+9 elbow params · `test_bare_canvas_clip_equality_edge` ×4 · `test_bare_canvas_clip_equality_paints_something`) | passed |
| **0 · unit** | `core` · `full` | `tests/test_perf_paint_clip.py::test_render_grid_clip_identity` | passed |
| **0 · unit** | `core` · `full` | `tests/test_perf_paint_clip.py::test_wire_count_budget` | passed — 12,264 ≤ 1,200,000 |
| **A/B · black-box** | `core` · `full` | `tests/test_perf_paint_clip.py::test_at_075_keypress_wire_budget` | passed — count under cap AND canvas rows byte-equal the base golden after open/`l`/`j` |
| gate | | `tests/test_perf_goldens_manifest.py` (2) · `tests/test_mod_parity.py` (3) · `tests/test_repair_golden_census.py` (7) | 29 passed total |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation 1 | M-R1b: bus upper bound clamped to `min(xb, w-1)` (drops one in-bounds cell) → `test_bare_canvas_clip_equality` RED at `test_bare_canvas_clip_equality[case1]` (bus past the right edge); 8 in-bounds shapes stayed green |
| Mutation 2 | Y-ONLY clip (bus x-loop unclipped) → `test_at_075_keypress_wire_budget` RED: 23,983,998 calls > 1,200,000 cap (painted-byte conjunct stayed green by design — the count conjunct reddens) |
| Mutation 3 | M-R1a: clip removed entirely (HEAD body) → `test_wire_count_budget` RED: 23,983,998 calls |
| Instrument | project code mutated in the worktree; each restore checked by sha256 |
| Where it ran | this worktree (Lane R's branch) |
| Transcript | `.dev-flow/2026-10-10-perf-batch/evidence/r1-red.transcript` |
| Restore proven by | sha256 before == after for every mutation: `d354bd46424a0a8d2f459b6d56903eb0df96baff8164a9e74e5b92e3d14838a2` |
| Bytecode cache | `python -B` and `-p no:cacheprovider` throughout |
| Arms resolved | M-R1b killed by the bare-`Canvas` equality oracle (named); y-only killed by the AT-075 wire cap (named); M-R1a killed by the layer-0 counted oracle (named) |

| Field | Value |
|---|---|
| **RED counterfactual** | 3 named mutations, each executed → RED on its named node, byte-identical sha256 restore, re-run GREEN |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `test_bare_canvas_clip_equality` (reference-loop equality) | M-R1b mutant (one in-bounds cell dropped) | `AssertionError` at `tests/test_perf_paint_clip.py:143`, 1 failed / 8 passed |
| `test_at_075_keypress_wire_budget` (wire-cap + golden) | y-only-clip mutant | `AssertionError: 23983998 wire calls ... exceeds the cap 1200000` |
| `test_wire_count_budget` (layer-0 counted oracle) | unclipped HEAD body | `AssertionError: 23983998 ... exceeds the cap 1200000` |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 3 instruments each shown RED before their PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the painted canvas rows (app session) | `test_at_075_keypress_wire_budget` compares the `#map-canvas` region strips after open/`l`/`j` against the pinned golden `tests/goldens/perf/at075_075b_wide2000_118x34.txt` (base SHA `5cde04e`) | equal — 0 diffs (29 passed, transcript §1) |
| the rendered grid text | `test_render_grid_clip_identity` re-renders all 16 grid cases with the capture script's builders and compares to `tests/goldens/perf/render/*.txt` | 0 diffs; plus the multi-parent DAG clipped-vs-reference render equal |
| `Canvas` layer dicts | `test_bare_canvas_clip_equality*` compares `cells`/`bits`/`dots`/`bgs`/`_wire_tones` of clipped vs reference canvases | 0 differences across all 13 shapes |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 3 artifacts, each asserted against the form its producer emits |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED proofs + GREEN verification + measured count | `.dev-flow/2026-10-10-perf-batch/evidence/r1-red.transcript` | recorded at the DDR |

| Field | Value |
|---|---|
| **Evidence files** | 1 transcript; the shipped `mapper/canvas.py` sha256 `d354bd46…4838a2` is quoted inside it |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Resting on an absence? | no — the clip's byte-identity rests on `wire`'s bounds-check (a PRESENCE, pinned by premise 2 and exercised by every equality case); the reference loops are copies in the test file, so no product flag can disable the oracle |
| Guard labelled as protecting a CONCLUSION? | the `test_bare_canvas_clip_equality_paints_something` guard proves the in-bounds reference shapes paint real content (against a vacuous both-empty equality) |
| Conjunctive criteria | the wire-cap nodes carry two conjuncts (count; painted bytes). The y-only mutant reddens ONLY the count conjunct while keeping bytes green — proving the painted-byte conjunct is not carried by the count, and vice versa (transcript §4) |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by other tests | `grep -rl "elbow_down\|\.edge(" tests/ mapper/` | renderers in `mapper/views/` call `elbow_down`; `tests/test_mod_parity.py` + `tests/test_repair_golden_census.py` pin painted output — both re-run GREEN in §1 |
| B3 byte-identical golden captures this source | `tests/test_perf_goldens_manifest.py` + `test_render_grid_clip_identity` | every render golden re-compared against the CURRENT product: 0 diffs |
| B4 artifact consumed elsewhere | `grep -rl "goldens/perf" tests/` | `tests/test_perf_goldens_manifest.py`, `tests/test_perf_paint_clip.py` (this increment); `tests/test_perf_layout_memo.py` / `tests/test_perf_dump.py` at Inc-R2/M1/M2 (per PDR §7) |
| A3 | `Canvas` signatures unchanged; bodies only | `git diff 5cde04e -- mapper/canvas.py` touches only the two method bodies |

| Field | Value |
|---|---|
| **Reverse census** | 4 probes run (B1 · B3 · B4 · A3), each with its command and verdict |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population | Enumeration method | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| span loops to clip | the loops `Canvas.elbow_down` and `Canvas.edge` iterate | requirements premise 2 + `grep` over `mapper/` for canvas span writers | 2 (`canvas.py:113-128`) | 2 | `wire`/`put`/`text` keep their own per-cell bounds checks — clipping them would change nothing and is out of the requirement |

| Field | Value |
|---|---|
| **Correction population** | 2 sites, enumerated before editing; nothing else in `mapper/` iterates an unclipped span |

### Signed-balance test ledger

`post = base − deleted + added` → `1 = 0 − 0 + 1` SOURCE file changed; `1 = 0 − 0 + 1` new test file ✓ reconciles

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, read-only) **APPROVE**, 0 HIGH/MED — every clip border walked against base `5cde04e`; the test's reference loops match the old bodies line for line; 2 LOW (opposite-sides off-canvas case optional; a redundant alias) |

---

## 5 · Risks

- The clip assumes `wire`'s bounds-check stays the drop rule for out-of-bounds
  cells (premise 2). Any future change to `wire` that writes out-of-bounds
  cells breaks the equivalence silently — the AT-065 parity goldens, the
  golden census and the render-grid identity catch painted drift at the DDR.
- The wire budget counts `Canvas.wire` app-wide (canvas + minimap). A future
  second unclipped span painter would be caught by the same budget node.

## 6 · Pending items / spec deviations

- LLR-PERF.1.2 (the `_tree_layout` memo, AT-075b, `tests/test_perf_layout_memo.py`)
  is Inc-R2 — not this increment. The AT-075/075b golden file this increment
  reads was pinned by the trunk at PERFG0.

## 7 · Suggested next task

Inc-R2 (Lane R): `mapper/views/layered.py` unscaled-layout memo +
`tests/test_perf_layout_memo.py` (memo-miss spy `_layout_misses` + the seven
named arms). Then the trunk's DDR join with Lane M.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files | all | ✓ | 1 SOURCE file (`mapper/canvas.py`); §2 count table |
| 2 | Tests written in this same increment | all | ✓ | `tests/test_perf_paint_clip.py` — 17 nodes |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `test_bare_canvas_clip_equality*` · `test_render_grid_clip_identity` · `test_wire_count_budget` |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | 3 named mutations, each executed RED on its named node with sha256-verified restore — transcript §3–§6 |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 4 probes in the table above |
| 6 | `code-reviewer` passed | `core` · `full` | ⚠ | PENDING — named in §4b |
| 7 | No file from another lane touched | all | ✓ | only `mapper/canvas.py` + this lane's test; `git status` shows no `model.py`/`mermaid.py`/`screens/` change |
| 8 | Frozen interfaces untouched | all | ✓ | `Canvas` signatures unchanged (bodies only); `keymap.py`/`darkside.py`/`app.py` re-export block untouched; no new painted string |
| 9 | Coverage claims verified **on disk** | all | ✓ | 16 render goldens + the AT-075 golden re-compared against stored bytes (29 passed) |
| 10 | Load-bearing emptiness declared | all | ✓ | table above — no absence claimed; the paints-something guard is named |
| 11 | **Mutation verdicts** declared | all | ✓ | M-R1a killed (count RED), M-R1b killed (equality RED), y-only killed (cap RED) — per named node |
| 12 | **Instrument RED-proof** declared | all | ✓ | 3 instruments, each fed a known-bad mutant first |
| 13 | **Correction population** declared | all | ✓ | 2 sites enumerated before editing |
| 14 | **Emitted-form assertion** declared | all | ✓ | painted strips, rendered grid text, layer dicts — each asserted on the emitted form |
| 15 | **Independent review** names somebody | all | ⚠ | PENDING in §4b (orchestrator assigns) |
| 16 | **Evidence files** declared | all | ✓ | `.dev-flow/2026-10-10-perf-batch/evidence/r1-red.transcript` |
