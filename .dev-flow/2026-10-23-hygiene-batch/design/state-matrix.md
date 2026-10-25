# State matrix — mapper render sweep — Batch 2026-10-23-hygiene-batch

> **Provenance.** Derived from code per **C-31** on 2026-10-23; bound by ledger entry
> **LED-2026-10-23-hygiene-batch.7** (finding F3); consumed by **LLR-Q3.1.2** and acceptance test
> **AT-115**. This artifact is the explicit state matrix the scalecheck sweep keys on — it exists
> so the sweep's states are recorded deliberation, not an inline frozenset in a test.

**Binding.** |states| = **4**. The sweep threshold is **6 renderers × 5 sizes × 4 states = 120
geometry assertions**. The renderer roster is derived from `mapper.views.__all__` per C-31, and
the sweep fails loudly on an empty or changed roster (LLR-Q3.1.1). Sizes SIZES = 80x24, 90x30,
118x34, 160x45, 200x50.

---

## States

| State | Definition (code-derived) | Source (file:line) | Assertion form in the sweep |
|---|---|---|---|
| `plain` | A small connected concept graph (e.g. the `anidado` fixture parse) rendered with default `ViewState(w, h)`. | `tests/perf_goldens_capture.py` builders · `mapper/views/state.py:61-101` | Between 1 and `h` lines (Layered renders `h − 4` for graphs smaller than the frame — measured), each ≤ `w` cells (measured with `rich.cells.cell_len`), with the one recorded exception of Layered's wordmark header: its node-count meter spills past `w` by construction and the sweep asserts the spill exactly — header `cell_len` == `(w − 2) + cell_len('{n} nodes')` (erratum of the original "exactly h lines" cell, ruling R10 / ledger `.11`, measured 2026-10-23; the spilled header is byte-pinned by the perf goldens). |
| `folded` | `build_fold_tree()` with `folded=frozenset({"mid"})`. Read **only** by LayeredRenderer (`mapper/views/layered.py:158-168, 382-387`); for the other five renderers the sweep proves **fold-invariance** — byte-identical to `plain` on the same graph. | `tests/perf_goldens_capture.py:115-125, 158-165` · `mapper/views/layered.py:158-168, 382-387` | Same geometry assertion; per-renderer applicability in the matrix below. |
| `empty` | Zero-node graph (`build_empty()`). Every renderer short-circuits to ≤ 2 named lines. | `tests/perf_goldens_capture.py:70-72` · `mapper/views/layered.py:660-661` ("(no map loaded)") · `mapper/views/outline.py:147-149` · `mapper/views/radial.py:177-178` · `mapper/views/lane.py:117-119, 181-185, 326-328` | The documented short-circuit: ≤ `h` lines, ≤ `w` cells, the named text present. "Exactly `h` lines" does **not** hold for zero-node graphs — recorded here so the sweep asserts the short-circuit, not `h`. |
| `orphan` | A tree unreachable from `root_id` (add a disconnected parentless tree; cf. `build_forest()`). Chosen because all six renderers answer it without crashing: Layered lays every parentless tree side-by-side (`layered.py:248-260`); Outline walks from `root_id` only (`outline.py:285`) — orphan nodes silently un-painted; Radial declares them unpainted in the header (`radial.py:421`); lane renderers never show them. | `tests/perf_goldens_capture.py:102-112` · `mapper/views/layered.py:248-260` · `mapper/views/outline.py:285` · `mapper/views/radial.py:421` | Same geometry assertion on the rendered text (lines ≤ `h`, cells ≤ `w`). |

## Per-renderer applicability matrix

Sources: `mapper/views/state.py:61-101` field usage — `selected_id`/`hits` are read by all six;
`folded`/`diff`/`focus_owner`/`pan` are read by Layered only.

| Renderer | `plain` | `folded` | `empty` | `orphan` |
|---|---|---|---|---|
| Layered | ● reacts | ● reacts | ● reacts | ● reacts |
| Outline | ● reacts | ○ exercised-no-op (proves fold-invariance) | ● reacts | ● reacts |
| Radial | ● reacts | ○ exercised-no-op | ● reacts | ● reacts |
| Lane | ● reacts | ○ exercised-no-op | ● reacts | ● reacts |
| RailTimeline | ● reacts | ○ exercised-no-op | ● reacts | ● reacts |
| HybridLane | ● reacts | ○ exercised-no-op | ● reacts | ● reacts |

● reacts — the renderer's output is expected to depend on the state.
○ exercised-no-op — the state is exercised through this renderer and the output must be
byte-identical to `plain` on the same graph (the invariance proof).

## Excluded / discovered while deriving

- **(a) Dangling-edge graphs** — an edge whose child id ∉ `graph.nodes` crashes OutlineRenderer
  (`mapper/views/outline.py:214-218`, KeyError). Direct-construction only: `mermaid.parse`
  materialises both endpoints at `mapper/mermaid.py:86-87`, so the parser cannot produce one.
  Kept **out** of the sweep states. Candidate **BACKLOG** item, named for the batch close.
- **(b) `panned` and over-limit (`MAX_RENDER_NODES` degradation `_degraded`)** — real states but
  out of the v1 matrix. Extension path noted: adding both would grow |states| to 6
  (threshold 6 × 5 × 6 = 180). Deferred by this ruling-style note, not by silence.
- **(c) Canvas construction census (measured 2026-10-23 at the L3 GREEN gate, ledger `.13`)** —
  only `LayeredRenderer`, `RadialRenderer` and `RailTimelineRenderer` construct a `Canvas`
  on non-empty renders (the audit sink's injection sites); `OutlineRenderer`, `LaneRenderer`
  and `HybridLaneRenderer` compose their `Text` directly and construct none across the whole
  matrix. The sweep's audit arm asserts the census exactly (≥1 audited canvas where a site
  exists; zero constructions asserted where none does).

## Binding

|states| = 4 — `plain`, `folded`, `empty`, `orphan`. Sweep threshold: 6 renderers × 5 sizes ×
4 states = **120 assertions**. The roster is derived from `mapper.views.__all__` (C-31) and the
sweep fails loudly on an empty or changed roster (LLR-Q3.1.1). Amending this matrix is a design
change: it re-opens the PDR, it is not a lane-level tweak.
