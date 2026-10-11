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


## 6. User-reachable scale (PERF0B orchestrator measurements, verbatim)

Source: `evidence/perf0b-run.transcript`. Each case one subprocess, 120 s
cap, viewport 118×34. Mount = MapScreen mount → first paint, median of 3.
Navigation keypress = press → `_rendered_for` change + settle, median of 5
(keys per shape: wide `l,j,j,j,j`; deep/balanced `l,l,l,l,l`). Search cycle
= `slash`, type "node", `enter`, until repaint settles, one gesture.

**MapScreen mount (median s):**

| shape | N=500 | N=2000 | N=6000 | N=12000 |
|---|---|---|---|---|
| wide | 0.62 | 4.82 | TIMEOUT (>150 s) | TIMEOUT |
| deep | 0.44 | 1.33 | 4.89 | TIMEOUT |
| balanced | not measured * | not measured * | 4.59 | TIMEOUT |

\* balanced 500/2000 not measured — harness hang after prior in-process
apps; other shapes unaffected.

**Navigation keypress (median s, per key):** 0.40–0.48 at 500;
0.56–1.71 at 2000; 1.59–1.89 at 6000.

**Search cycle (median s):** 0.85–0.87 at 500; 1.37–3.47 at 2000;
3.05–3.12 at 6000.

**MapStore save/load (median s, no UI):** N=12000 ≈ 9.4–10.0 save /
4.5–4.8 load. **CSV import preview:** 12000 rows in 1.74–1.77 s.

**Reachability defect (recorded separately, backlog — NOT part of this
profile):** a CSV whose ids slugify to the same id yields a multi-parent
node; it previews and saves, then re-open fails with MapStoreError
(ParseError). Evidence: `evidence/perf0b-slug-reach.transcript`. Data-safety
issue: the store persists a graph its own loader refuses.

Reading: every user-reachable path is linear-ish in N up to ~6000 nodes and
then falls off a cliff (wide/balanced TIMEOUT at 12000; deep already at
12000). The reachable worst case is ~5 s per interaction, not the 55–131 s
of the dense-DAG profiles in §2 — those DAGs cannot be opened as saved maps
at all (§3). Still: a 5 s keypress at 6000 nodes and any wide map ≥ ~12000
nodes wedging the app are user-visible defects.

## 7. Hot path (PERF0C cProfile, transcripts `evidence/perf0c-*.transcript`)

All cases in a fresh subprocess, profiler wall times inflated ~3–6× vs §6.
Paths below are repo-relative (third-party shown package-relative). One
navigation keypress = full `refresh_canvas` → layered `render` repaint.

### 7.1 Navigation (`l` then `j` on mounted wide-2000; profiler wall 16.4 s)

TOP 10 BY CUMULATIVE:

| # | function | file:line | ncalls | tottime | cumtime |
|---|---|---|---|---|---|
| 1 | `_run` | asyncio/events.py:86 | 670 | 0.0012 | 7.2420 |
| 2 | `<method 'run' of '_contextvars.Context' objects>` | ~:0 | 670 | 0.0012 | 7.2420 |
| 3 | `invoke` | textual/_callback.py:62 | 735 | 0.0009 | 7.0785 |
| 4 | `_invoke` | textual/_callback.py:45 | 735 | 0.0021 | 7.0451 |
| 5 | `_process_messages_loop` | textual/message_pump.py:634 | 273 | 0.0028 | 6.4253 |
| 6 | `_dispatch_message` | textual/message_pump.py:707 | 453 | 0.0014 | 6.3566 |
| 7 | `_on_message` | textual/message_pump.py:810 | 353 | 0.0012 | 6.2734 |
| 8 | `on_event` | textual/message_pump.py:802 | 214 | 0.0002 | 6.2655 |
| 9 | `run_app` | textual/app.py:2178 | 12 | 0.0000 | 6.2592 |
| 10 | `_process_messages` | textual/app.py:3364 | 12 | 0.0000 | 6.2591 |

TOP 10 BY TOTTIME:

| # | function | file:line | ncalls | tottime | cumtime |
|---|---|---|---|---|---|
| 1 | `elbow_down` | mapper/canvas.py:119 | 3998 | 4.1793 | 5.9962 |
| 2 | `wire` | mapper/canvas.py:107 | 23983998 | 1.8148 | 1.8150 |
| 3 | `wait_inner` | textual/_win_sleep.py:97 | 36 | 0.1569 | 0.1161 |
| 4 | `GetQueuedCompletionStatus` (builtin) | ~:0 | 208 | 0.1151 | 0.1151 |
| 5 | `str.translate` (builtin) | ~:0 | 68445 | 0.0672 | 0.0672 |
| 6 | `render` | mapper/views/layered.py:541 | 2 | 0.0433 | 6.1768 |
| 7 | `_title_image` | mapper/views/layered.py:373 | 16000 | 0.0291 | 0.1370 |
| 8 | `builtins.max` (builtin) | ~:0 | 104400 | 0.0285 | 0.0533 |
| 9 | `builtins.len` (builtin) | ~:0 | 272513 | 0.0227 | 0.0253 |
| 10 | `from_rich_style` | textual/style.py:352 | 8567 | 0.0211 | 0.0447 |

Call counts: `Graph.children_of` 36, `Graph.parent_of` 1 — negligible.
Per repaint: layered `render` ×2 (one per key), rail `render` ×2,
`_minimap_text` ×2, inspector `show`/`_rebuild` ×2/6 — each O(N) but small.

**Diagnosis (nav):** the renderer dominates, and within it the paint phase:
`elbow_down` walks every edge's bus row cell-by-cell through `wire`
(24 M `wire` calls for 2 keypresses — O(painted cells) per repaint). The
cost is **per-keypress O(N)**: each key triggers a full-canvas layered
repaint (`render` ncalls == keys pressed), so latency scales with N
(matches §6: 0.4 s at 500 → 1.7 s at 2000 → 1.9 s at 6000). Rail/minimap/
inspector refreshes are linear and minor; the model lookups
(children_of/parent_of) are noise. Not O(N·E) — edges ≈ N in every
reachable (tree) shape.

### 7.2 Mount (wide-2000, push_screen → first paint; profiler wall 15.8 s)

TOP 10 BY CUMULATIVE:

| # | function | file:line | ncalls | tottime | cumtime |
|---|---|---|---|---|---|
| 1 | `_run` | asyncio/events.py:86 | 271 | 0.0003 | 11.5710 |
| 2 | `<method 'run' of '_contextvars.Context' objects>` | ~:0 | 271 | 0.0004 | 11.5392 |
| 3 | `invoke` | textual/_callback.py:62 | 366 | 0.0004 | 11.4522 |
| 4 | `_invoke` | textual/_callback.py:45 | 366 | 0.0006 | 11.4496 |
| 5 | `_process_messages` | textual/message_pump.py:562 | 107 | 0.0002 | 11.2497 |
| 6 | `_dispatch_message` | textual/message_pump.py:707 | 272 | 0.0009 | 11.2348 |
| 7 | `render` | mapper/views/layered.py:541 | 3 | 0.0603 | 8.7740 |
| 8 | `elbow_down` | mapper/canvas.py:119 | 5997 | 5.9295 | 8.5394 |
| 9 | `_on_message` | textual/message_pump.py:810 | 223 | 0.0009 | 8.1470 |
| 10 | `on_event` | textual/message_pump.py:802 | 135 | 0.0001 | 8.1426 |

TOP 10 BY TOTTIME:

| # | function | file:line | ncalls | tottime | cumtime |
|---|---|---|---|---|---|
| 1 | `elbow_down` | mapper/canvas.py:119 | 5997 | 5.9295 | 8.5394 |
| 2 | `wire` | mapper/canvas.py:107 | 35975997 | 2.6070 | 2.6072 |
| 3 | `need_more_tokens` | yaml/scanner.py:145 | 358132 | 0.1555 | 0.3004 |
| 4 | `check_token` | yaml/scanner.py:113 | 218080 | 0.1182 | 1.1708 |
| 5 | `stale_possible_simple_keys` | yaml/scanner.py:279 | 372128 | 0.1174 | 0.1174 |
| 6 | `forward` | yaml/reader.py:99 | 148023 | 0.0931 | 0.1064 |
| 7 | `fetch_value` | yaml/scanner.py:545 | 14004 | 0.0883 | 0.1411 |
| 8 | `str.translate` (builtin) | ~:0 | 90700 | 0.0849 | 0.0849 |
| 9 | `parse_node` | yaml/parser.py:273 | 28009 | 0.0829 | 0.3760 |
| 10 | `scan_plain` | yaml/scanner.py:1270 | 16005 | 0.0810 | 0.2302 |

Call counts: `Graph.children_of` 17, `Graph.parent_of` 0. Layered
`render` **×3** (three paint passes before first paint: `refresh_canvas` +
the `_declare_after_layout` settle pass, matching §4 remedy 5's
"mount paints 2×+" observation — here 3×). `elbow_down` 5997 = 3 × 1999
edges; `wire` 36 M calls. `MapStore.load` 1.85 s (yaml scan/parse of the
saved files).

**Diagnosis (mount):** renderer dominates (~8.8 s cumulative of 11.6), and
it is **O(N) per paint pass × 3 passes** on mount — the same `elbow_down`/
`wire` paint cost as navigation, paid three times up front. Second: store
yaml load ~1.8 s (yaml scanner functions fill the tottime list below
`wire`). Textual layout/wrap (`divide`, `_wrap_and_format`, content spans)
is the remainder. Rail/minimap/inspector each paint once and are minor.
The O(N) model lookups (children_of 17 calls) are noise; `missing_required`
18 002 calls ≈ 9 per node × 2 passes, still minor.

### 7.3 MapStore.save wide-6000 (6.2 s under profiler)

TOP 10 BY CUMULATIVE (full top-15 in transcript):

| # | function | file:line | ncalls | tottime | cumtime |
|---|---|---|---|---|---|
| 1 | `save` | mapper/store.py:810 | 1 | 0.0005 | 6.2060 |
| 2 | `dump` | mapper/mermaid.py:131 | 1 | 0.0217 | 3.0748 |
| 3 | `builtins.any` (builtin) | ~:0 | 6002 | 1.2606 | 3.0434 |
| 4 | `safe_dump` | yaml/__init__.py:263 | 1 | 0.0001 | 2.5334 |
| 5 | `dump_all` | yaml/__init__.py:215 | 1 | 0.0085 | 2.5334 |
| 6 | `represent` | yaml/representer.py:26 | 1 | 0.0008 | 2.5247 |
| 7 | `serialize` | yaml/serializer.py:46 | 1 | 0.0011 | 2.2126 |
| 8 | `serialize_node` | yaml/serializer.py:78 | 84009 | 0.2525 | 2.1568 |
| 9 | `<genexpr>` | mapper/mermaid.py:153 | 18003001 | 1.7857 | 1.7857 |
| 10 | `emit` | yaml/emitter.py:111 | 102017 | 0.1048 | 1.7257 |

**Diagnosis (save):** two O(N²) sins in the mermaid dump
(`mapper/mermaid.py:153`): the genexpr runs 18 003 001 times (~N²/2 for
N=6000) and the `builtins.any` above it cumulates 3.04 s over only 6002
calls — each call scans O(E), so the edge-emission loop is **O(N·E)**
(≈ O(N²) on trees). `Graph.parent_of` 6000 calls × O(E) scan adds 0.49 s
— also O(N·E). The yaml emit of the metadata sidecar is 2.5 s, plain
O(document). Store/yaml component dominates; renderer untouched (no UI).

### 7.4 MapStore.load wide-6000 (5.6 s under profiler)

TOP 10 BY TOTTIME (cumulative top-15 in transcript):

| # | function | file:line | ncalls | tottime | cumtime |
|---|---|---|---|---|---|
| 1 | `need_more_tokens` | yaml/scanner.py:145 | 1074132 | 0.4628 | 0.8888 |
| 2 | `stale_possible_simple_keys` | yaml/scanner.py:279 | 1116128 | 0.3468 | 0.3468 |
| 3 | `check_token` | yaml/scanner.py:113 | 654080 | 0.3408 | 3.4612 |
| 4 | `forward` | yaml/reader.py:99 | 444023 | 0.2798 | 0.3189 |
| 5 | `parse_node` | yaml/parser.py:273 | 84009 | 0.2458 | 1.1063 |
| 6 | `scan_plain` | yaml/scanner.py:1270 | 48005 | 0.2372 | 0.6826 |
| 7 | `fetch_more_tokens` | yaml/scanner.py:156 | 132014 | 0.2082 | 2.3912 |
| 8 | `peek` | yaml/reader.py:87 | 1611919 | 0.2030 | 0.2030 |
| 9 | `scan_to_next_token` | yaml/scanner.py:752 | 132014 | 0.1773 | 0.4705 |
| 10 | `get_mark` | yaml/reader.py:114 | 318033 | 0.1718 | 0.3429 |

**Diagnosis (load):** 100% yaml `safe_load` of the metadata sidecar
(5.41 s of 5.62 cumulative; every tottime row is the yaml scanner/parser).
Mapper's own code is invisible (`find_cycle` ×1). Component: store/yaml.
O(document size) — unavoidable for the format, but it is the entire cost.

### 7.5 Summary across cases

| case | dominant component | complexity |
|---|---|---|
| navigation keypress | renderer paint (`elbow_down`/`wire`, full repaint per key) | per-keypress O(N) |
| mount | renderer paint ×3 passes, then store/yaml load | O(N) × passes + O(doc) |
| store save | mermaid dump O(N·E) genexpr + `any`; then yaml emit | O(N·E) ≈ O(N²) on trees |
| store load | yaml scanner/parser only | O(document) |

No reachable case shows O(N·E) in the *render* path — trees have E≈N and
the minimap/rail model scans stay linear; the only measured O(N·E) is in
`MapStore.save`'s mermaid dump. Consistent with §6: UI paths degrade
linearly up to ~6000 nodes, then wide/balanced hit the §1 path-count wall
(not reachable via saved maps, but reachable via CSV preview — §6 backlog).
