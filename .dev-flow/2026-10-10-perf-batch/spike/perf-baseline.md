# PERF0 — performance measurement baseline (batch `2026-10-10-perf-batch`)

Measurement spike for backlog row **B-33** (`S-15` / `M-H3`): `MAX_RENDER_NODES`
bounds node COUNT, not WORK. **Nothing under `mapper/` or `tests/` was changed
by this spike** — the only artifacts are this file, `spike/perf_harness.py`,
and raw transcripts under `evidence/`.

All numbers produced on this worktree, headless, viewport **118×34** (the
renderers' public API: `Renderer().render(graph, ViewState(selected_id=root,
w=118, h=34))`), each case in a subprocess with a **120 s hard cap** (a case
that exceeds it is recorded TIMEOUT, never a hang). Timed cases: median of 3
reps (min/max reported); reps beyond the first are skipped once a rep exceeds
15 s ("adaptive reps", noted per row). Phase-B classification cases ran 1-rep
in a 6-wide pool purely to classify TIMEOUT vs completed; the one survivor
under 30 s (`sweep-N100_moderate` radial) was re-run clean.

## Reproduce

From the repo root:

```
# any single number
python .dev-flow/2026-10-10-perf-batch/spike/perf_harness.py render --shape p51 --renderer layered --reps 3

# the full matrix (phase A sequential timed + phase B concurrent classification)
python .dev-flow/2026-10-10-perf-batch/spike/perf_harness.py sweep

# cProfile of one render
python .dev-flow/2026-10-10-perf-batch/spike/perf_harness.py profile --shape p73 --renderer layered

# MapScreen mount -> first paint
python .dev-flow/2026-10-10-perf-batch/spike/perf_harness.py mount --shape tree51 --size 118 34 --reps 3
```

Raw transcripts (relative paths): `evidence/perf0-sweep.transcript`,
`evidence/perf0-profile-p51-layered.transcript`,
`evidence/perf0-profile-p73-layered.transcript`,
`evidence/perf0-mount.transcript`, `evidence/perf0-store-roundtrip.transcript`.

## Shapes

| shape | construction | N | E |
|---|---|---|---|
| p51 | 5 layers × 10/layer, fully connected across boundaries (=`tests/test_repair_perf_shape.py` fixture) | 51 | 410 |
| p73 | 6 layers × 12/layer, fully connected (`01-requirements.md` ~L4271 demonstration, S-15) | 73 | 732 |
| tree51 | 5 layers × 10/layer, k=1 (single parent per node — survives the store round-trip) | 51 | 50 |
| sweep-N50_{sparse,moderate,dense} | 7 layers × 7/layer, k=1 / k=4 / k=7 | 50 | 49 / 175 / 301 |
| sweep-N100_* | 11 layers × 9/layer, k=1 / 4 / 9 | 100 | 99 / 369 / 819 |
| sweep-N197_* | 14 layers × 14/layer, k=1 / 4 / 14 | 197 | 196 / 742 / 2562 |
| sweep-N401_* | 20 layers × 20/layer, k=1 / 4 / 20 | 401 | 400 / 1540 / 7620 |
| chain1000 | one chain, depth 1000 | 1000 | 999 |

k = outgoing edges per node to the next layer (children j..j+k-1 mod P); the
root links to every first-layer node in all sweep shapes.

## 1. Headline timings (median seconds, 118×34; † = 1 rep after early-stop)

| shape | N | E | layered | outline | radial |
|---|---|---|---|---|---|
| p51 | 51 | 410 | 1.702 (1.62–1.71) | 1.057 (1.01–1.10) | 0.226 (0.21–0.24) |
| p73 | 73 | 732 | 54.83† | 31.26† | 5.546 (5.05–6.06) |
| tree51 | 51 | 50 | 0.0052 (0.0048–0.0058) | 0.0075 (0.0063–0.0159) | 0.0096 (0.0080–0.0105) |
| chain1000 | 1000 | 999 | 0.016 (0.014–0.019) | 0.027 (0.023–0.032) | 0.017 (0.014–0.022) |
| sweep-N50_sparse | 50 | 49 | 0.0065 | 0.0070 | 0.0072 |
| sweep-N50_moderate | 50 | 175 | 0.374 (0.35–0.38) | 0.349 (0.34–0.37) | 0.075 (0.056–0.076) |
| sweep-N50_dense | 50 | 301 | 12.43 (12.06–12.61) | 9.059 (9.05–9.48) | 1.578 (1.54–1.68) |
| sweep-N100_sparse | 100 | 99 | 0.0049 | 0.0072 | 0.0089 |
| sweep-N100_moderate | 100 | 369 | TIMEOUT | TIMEOUT | 22.44† |
| sweep-N100_dense | 100 | 819 | TIMEOUT | TIMEOUT | TIMEOUT |
| sweep-N197_sparse | 197 | 196 | 0.0081 | 0.0059 | 0.0093 |
| sweep-N197_moderate | 197 | 742 | TIMEOUT | TIMEOUT | TIMEOUT |
| sweep-N197_dense | 197 | 2562 | TIMEOUT | TIMEOUT | TIMEOUT |
| sweep-N401_sparse | 401 | 400 | 0.0105 | 0.0123 | 0.0172 |
| sweep-N401_moderate | 401 | 1540 | TIMEOUT | TIMEOUT | TIMEOUT |
| sweep-N401_dense | 401 | 7620 | TIMEOUT | TIMEOUT | TIMEOUT |

TIMEOUT = one rep did not finish inside the 120 s cap. `index_build_s` (the
adjacency + parent index every renderer builds per pass) was ≤ 0.37 ms for
every shape — the index build is noise, never the cost.

Reading the table:

- **Node count is a non-predictor.** chain1000 (1000 nodes) renders in 5–27 ms
  in every view; N50_dense (50 nodes) takes 1.6–12.4 s. Fitted over the 19
  completed sweep points: `time ~ E^a` gives **a = 2.06** (per renderer:
  layered 1.86, outline 1.72, radial 2.48) while `time ~ N^b` gives
  **b = −1.58** — N *anti*-predicts.
- **E is the better predictor but still not the driver.** p51 (E=410, 5
  layers) takes 1.7 s while sweep-N50_dense (E=301, 7 layers) takes 12.4 s —
  at similar E the *deeper* graph is 7× slower. What grows multiplicatively
  with depth is the number of **paths**: p73 has 12^5 ≈ 250 k root-to-leaf
  paths. The fitted exponent over E is an artefact of E and path-count being
  correlated along this sweep; path count (equivalently: layered depth ×
  branching) is the quantity that predicts cost.
- **73 nodes / 732 edges cost 54.8 s in layered, 31.3 s in outline, 5.5 s in
  radial at 118×34** — reproduced against the recorded 72.5 s at 80×24
  (same order, different viewport). Every one of the 73 nodes is far under
  `MAX_RENDER_NODES = 12000`; the cap waves all of it through.

## 2. Where the time goes (cProfile)

### p51, layered — 3.78 s under profiler (1.70 s wall)

Top by cumulative and tottime agree; the render is one hot sink:

| function | file:line | ncalls | tottime | cumtime |
|---|---|---|---|---|
| `render` | `mapper/views/layered.py:541` | 1 | 0.001 | 3.781 |
| `elbow_down` | `mapper/canvas.py:119` | 50 | 2.537 | 3.657 |
| `wire` | `mapper/canvas.py:107` | 14,851,300 | 1.120 | 1.120 |
| `_geometry` | `mapper/views/layered.py:306` | 1 | 0.000 | 0.112 |
| `_tree_layout` | `mapper/views/layered.py:192` | 1 | 0.000 | 0.112 |
| `walk` | `mapper/views/layered.py:217` | 1 | 0.060 | 0.111 |

`Graph.children_of` / `Graph.parent_of` call count in the pure layered render:
**zero** — the renderer builds its own adjacency index and never touches the
O(E) model lookups. (`children_of` *is* called on the mount path, by the
minimap: `painting.py:472` `_branch_coverage_glyph` and `:519` `_minimap_text`
— one O(E) scan per top-level branch per repaint. For a tree that is cheap;
for a wide DAG it would be `branches × E`.)

### p73, layered — 131.1 s under profiler (54.8 s wall)

| function | file:line | ncalls | tottime | cumtime |
|---|---|---|---|---|
| `render` | `mapper/views/layered.py:541` | 1 | 0.002 | 131.06 |
| `elbow_down` | `mapper/canvas.py:119` | 72 | 88.15 | 128.14 |
| `wire` | `mapper/canvas.py:107` | **533,922,768** | 39.99 | 39.99 |
| `_geometry` | `mapper/views/layered.py:306` | 1 | 0.000 | 2.92 |
| `_tree_layout` | `mapper/views/layered.py:192` | 1 | 0.000 | 2.91 |
| `walk` | `mapper/views/layered.py:217` | 1 | 1.57 | 2.91 |

`children_of` / `parent_of` call count: **zero** again.

**Mechanism (measured, both shapes):** `_tree_layout`'s `walk`
(`mapper/views/layered.py:217-241`) has no cross-path memoisation — a node
reachable by k paths is laid out k times, and every visit consumes fresh leaf
slots, so coordinates inflate with the path count (271 k path-visits of
internal nodes for p73; each of the 10 leaves is re-slotted ~27 k times). The
paint phase then runs `Canvas.elbow_down` (`mapper/canvas.py:119`) per node,
which walks a horizontal bus row cell-by-cell through `Canvas.wire`
(`mapper/canvas.py:107`) across the inflated span: 534 M `wire` calls for a
canvas that physically holds ~3.8 k cells. Layout (2.9 s) and paint (128 s)
are BOTH exponential in depth; paint dominates because it is O(paths × span)
on top of O(paths) layout.

## 3. Mount path (MapScreen mount → first paint, `App.run_test`, 118×34)

| graph | result |
|---|---|
| tree51 (51 nodes / 50 edges, loadable tree) | **0.295 s median** (0.295–0.303, 3 reps) |
| p51 DAG (51 nodes / 410 edges) | 0.176 s median — **but this is the load-ERROR path** |

Measured with `MapperApp(ws)` + `run_test(size=(118,34))` +
`push_screen(MapScreen(map_id))`, polling `screen._rendered_for` (set at the
end of the first `refresh_canvas`), median of 3, each rep a fresh workspace.

**Finding: the S-15 shape cannot reach MapScreen at all.** `MapStore.load`
parses the `.mmd` with `mapper/mermaid.py:85`, which **refuses multi-parent
nodes** ("node 'n1_1' has multiple parents (out of MVP scope)"). `MapScreen.on_mount`
(`mapper/screens/map/screen.py:208-218`) catches that, substitutes a 1-node
error graph and paints "error loading map". So in the shipped app:

- the 0.176 s figure above is the mount cost of a *refused* map, not a render;
- the honest app-level mount number for a 51-node map the app accepts is
  **0.295 s** (tree51), of which the layered render itself is 5 ms — the rest
  is rail, inspector, minimap, crumb and Textual overhead inside the first
  `refresh_canvas`;
- the 54.8 s layered render of p73 is reachable only by calling the renderer
  directly (as `01-requirements.md` did) — e.g. import/CSV preview paths that
  build graphs without the parser — not by opening a saved map.

## 4. Candidate remedies (HYPOTHESES — no code changed)

Ranked by expected gain, each tied to the measurement above. All are design
inputs for the follow-on batch (`S-18`/`S-19`/`B-33`); none was implemented.

1. **Memoise the `_tree_layout` walk across paths (HYPOTHESIS, large gain).**
   Lay out each node once (`pos` settled on first visit, children centred from
   memoised child positions). Evidence: p73 `walk` does 271 k internal-node
   visits for 73 nodes and the slot inflation it causes is what turns
   `elbow_down` spans into 534 M `wire` calls; on single-path graphs (chain,
   trees, sparse lane) the same code is already linear and fast. A
   DAG-correct single layout would collapse both the 2.9 s layout and most of
   the 128 s paint for p73-class shapes. Must define behaviour for diamonds
   (a node with two parents cannot sit under both — first-parent placement +
   declared trade-off is one option; this is a design ruling, not a bug fix).
2. **Bound the painted span, not the node count (HYPOTHESIS, large gain,
   the S-18 work budget).** Count edges visited / cells written during the
   walk and stop with a declared degradation when the budget is spent —
   `MAX_RENDER_NODES` (`mapper/views/layered.py:18`, `outline.py:17`,
   `radial.py:31`) demonstrably waves p73 through at 73 of 12000 nodes.
   Evidence: section 1 table. Falsifiable per the `#D24` gate: the fixture
   must name its renderer and carry one where k > 0.
3. **One shared walk + adjacency index in `Graph` (HYPOTHESIS, moderate
   gain).** `Graph.children_of` is O(E) per call (`mapper/model.py:149-150`)
   and is re-scanned per call by `Graph.focus`, the minimap
   (`painting.py:472,519`) and rail code; three renderers each rebuild
   `_child_index` per render (measured ≤ 0.37 ms — cheap per pass, but the
   O(E) *per-call* lookups on the mount path are `branches × E` per repaint).
   A cached adjacency on `Graph` (invalidated on edge mutation) removes the
   repeated O(E) scans. Evidence: store-roundtrip + profile zero-count shows
   the renderers already avoid it; the mount path does not.
4. **Skip out-of-view work in `elbow_down`/`wire` (HYPOTHESIS, small-to-
   moderate gain).** `wire` bounds-checks per cell but the *loop* still runs
   the full inflated span; clipping bus spans to the canvas rectangle before
   iterating would cut the 534 M loop iterations even where coordinates stay
   inflated. Evidence: p73 profile, 39.99 s tottime inside `wire` alone.
5. **Memoise layout per graph revision (HYPOTHESIS, small gain for repaint-
   heavy sessions).** Mount paints 2× already (`refresh_canvas` + the
   `_declare_after_layout` settle pass, the latter guarded by `_rendered_for`).
   With remedy 1 the per-render cost is small for admissible graphs, so this
   only matters if remedy 2's budget lands high.

## 5. What this spike did NOT do

- No change under `mapper/` or `tests/` (`git status` clean outside
  `.dev-flow/2026-10-10-perf-batch/`).
- No RED proof: that ritual guards a *product change*; this unit changes none
  (measurement spike only), so there is nothing to revert and re-run.
- Phase-B TIMEOUT rows are classifications from 1-rep concurrent runs; their
  value is "exceeds 120 s", not a timing.
