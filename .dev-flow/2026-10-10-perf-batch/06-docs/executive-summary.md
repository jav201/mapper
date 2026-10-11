# Executive summary — mapper — Batch `2026-10-10-perf-batch`

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`).
> Phase 6 artifact. Owner: `presentation-builder`. Audience: non-technical stakeholder. 1-2 pages.

## 🔑 Bottom line (read first)

- **What we delivered:** the app is now 3.5–4× faster to open, browse and save on large maps — and up to 48× faster on the worst-render cases — with the screen and the saved files provably byte-for-byte identical to before.
- **Business outcome:** maps of thousands of nodes stay fluid to browse (a navigation keypress went from ~1.8 s to ~0.4 s measured) and safe to save, on the exact same product the operator already knows — zero retraining, zero migration, zero visible change.
- **Next step:** the carried items, in priority order: B-118 (opening still paints 2–3× — the one remaining latency lever on open), B-120 (three per-key layout computations still run outside the new cache), B-121 (opening large maps is bound by the metadata-file parser — proposed backlog row).

---

## Context (reference)

### Context

This batch is the follow-up the backlog had been waiting for (B-33): the previous modularisation batch ended by measuring that a 73-node pathological map took 72.5 s to render and that `MAX_RENDER_NODES` bounds the drawn node count, not the work done. Before touching anything, this batch measured precisely where the time goes on real maps (the P0 spike: profiles and timings of open, browse, save and load at 2000–12000 nodes) and then changed only what those measurements indicted.

### Problem

On a 2000-node map, every navigation keypress repainted the whole map (0.6–1.9 s), opening took 4.8 s and painted three times, and saving a 6000-node map cost work proportional to nodes × edges (6.2 s) because the save format's writer re-scanned every edge for every node. The user-visible symptom: the app degrades with map size far faster than the map size grows.

### Solution

Four surgical, behaviour-preserving changes inside the renderer and the store: paint only the part of each line that fits on screen (skip exactly the cells that would be discarded anyway), remember the map's layout between keypresses instead of recomputing it ~10× per repaint, answer "what are the children of this node?" from a precomputed index instead of scanning all edges, and write saved files in one pass instead of one scan per node. The discipline that makes this safe: every threshold is a counted operation measured before and after (never a stopwatch assertion in the test suite), and every painted screen and saved file is compared byte-for-byte against golden copies made from the OLD code before any change — 26 golden files, all identical.

### Outcomes / results

| Case | Before | After | Speed-up |
|---|---|---|---|
| Open a 2000-node map | 4.89 s | 1.24 s | **3.9×** |
| Navigation keypress `l` | 1.75 s | 0.43 s | **4.1×** |
| Navigation keypress `j` | 1.78 s | 0.47 s | **3.8×** |
| Save a 6000-node map | 3.01 s | 0.87 s | **3.5×** |
| Worst-case dense render (p51) | 1.45 s | 0.03 s | **48.5×** |
| Open a 6000-node map (load) | 2.32 s | 2.22 s | 1.05× — unchanged, see below |

(Median of 3, old and new interleaved on the same machine, `evidence/p4-wallclock.transcript`; deterministic call-count oracles in the suite measured the work itself: 23,983,998 → 12,264 paint calls per two keypresses, 18,003,000 → 11,998 edge visits per save.)

- **Safety net grew, never shrank:** 3157 → 3223 tests passing, 0 failing, 0 tests removed (66 new guard tests, each proven able to fail by deliberately breaking the code and watching it fail, with a byte-identical restore).
- **Process milestone:** the first batch to run two work streams in parallel worktrees (two lanes, disjoint file sets, verified at the merge) — the parallelisation the previous batch was built to enable.
- **Honest scope:** opening still paints 2–3× (a design idea failed its proof-of-concept and was shelved to the backlog by a pre-written rule rather than shipped unproven); loading large maps is bound by the metadata-file parser and was left untouched, now recorded as the next lever.

### Next steps

1. **B-118 — open paints once, not 2–3×** (the largest remaining open-latency lever): measure the 2000-node case first, then design a single-render open that keeps the layout fixes intact. Travels with the shelved requirement set.
2. **B-120 — finish the layout cache** (screen-side, small): three per-key computations still run outside the new cache; threading them in is a contained follow-up.
3. **B-121 (proposed) — load speed**: opening is bound by parsing the metadata sidecar (100% of the profiled cost); a lazy or cheaper parse is a store-side follow-up.
4. Housekeeping before the batch folder archives: the architecture map's `Graph` row note (a one-line trunk act) and the deferred flow-template lessons (spike budgets, golden line-ending policy) recorded in the post-mortem.
