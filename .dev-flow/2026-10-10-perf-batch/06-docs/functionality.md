# Functionality — mapper — Batch `2026-10-10-perf-batch`

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`).
> Phase 6 artifact. Owner: `docs-writer`. Audience: **the maintainer**. There is no user-visible change: the batch's contract is byte-identity — every painted cell and every `.mmd` byte is identical to the base goldens pinned at `5cde04e` (AT-065 parity, `tests/test_perf_goldens_manifest.py`, `tests/test_repair_golden_census.py`).

## 🔑 At a glance (read first)

- **What this batch added:** four work-reduction mechanisms inside the renderer and the store — span clipping in `Canvas`, an unscaled-layout memo on `LayeredRenderer`, a private adjacency cache on `Graph`, and a one-pass incident set in `mermaid.dump` — shipping byte-identical output at 1,956× fewer `wire` calls per keypress, 1 memoised layout per session, ≤ 1 edge pass per 100 cached lookups, and 2·E edge visits per dump (was ~N²/2).
- **Capabilities:** large-map navigation repaints in ~0.4 s instead of ~1.8 s (measured) · saving a 6000-node map is 3.5× faster · the dense p51 render is 48× faster · EVERYTHING the operator sees is provably unchanged (byte-pinned goldens).
- **How to use it:** nothing to operate — the mechanisms are automatic. To maintain them, respect the invariants below; the guards fail loudly if you don't.

---

## Detail (reference)

### How it works (flow)

**1. The span clip (`mapper/canvas.py:113-141`, LLR-PERF.1.1).** `Canvas.edge` and `Canvas.elbow_down` used to iterate every cell of a span, relying on `Canvas.wire` to drop out-of-bounds writes. They now intersect each span with the canvas rectangle (`0 <= x < self.w`, `0 <= y < self.h`) BEFORE iterating: `edge` walks `range(max(0, min(y0,y1)), min(h-1, max(y0,y1)) + 1)`; `elbow_down` walks the vertical drop over `range(max(0, y0+1), min(ybus, self.h))` (bus row wired only when `0 <= ybus < h`) and the bus row over `range(max(0, xa+1), min(xb, self.w))`. Every skipped cell is one `wire` would have dropped, so the painted result — cells and the order layers converge in `rows()` — is byte-identical, at O(painted) instead of O(span) iterations. This is where the 23,983,998 → 12,264 wire-call reduction comes from: the x-axis carries the whole gain (a y-only clip is byte-count-identical to no clip — round-2 probe p4).

**2. The unscaled-layout memo (`mapper/views/layered.py:192-218, 350-431`, LLR-PERF.1.2).** `_tree_layout` was recomputed ~10× per two renders (measured, `evidence/perf0c-nav.transcript:44`) because module-level callers needed it repeatedly. The scaling-free core `_tree_layout_unscaled(graph, hidden)` — in-order leaf slots + level per node — is now memoised on the OWNING `LayeredRenderer` INSTANCE and passed into module-level `_geometry` as the `layout_memo` argument (there is NO module-global memo state — a global would leak across screens and pin `Graph`s). The memo key is strong references compared with `is` plus lengths: the `Graph` object, its `edges` list (+`len`), its `nodes` dict (+`len`), `root_id`, and the hidden (fold) set. On a hit, the `card_w`/`gap` scaling re-applies per call in O(N) — so a resize or a widening-title edit changes the scaling, never the slots, and costs 0 extra misses. The spy is the named instance counter `LayeredRenderer._layout_misses`, incremented at the hit check. Each `MapScreen` holds one renderer (`screens/map/screen.py:73`); the import preview builds a fresh renderer per paint (`screens/import_preview.py:103`) and simply misses. SCOPING (B-120): the memo covers the render path only — `painted_ids` (`layered.py:495`), `pan_extent` (`:509`) and the pan clamp's reader (`screens/map/panning.py:277`) pass no memo and always compute fresh.

**3. The `Graph` adjacency cache (`mapper/model.py:125-214`, LLR-PERF.2.1).** `children_of`/`parent_of` used to scan all edges per call — O(E) each, and the dump path paid O(N·E). The `Graph` dataclass now carries four private fields (`_`-prefixed, `compare=False, repr=False`): `_adj_src` (a STRONG reference to the `edges` list the index was built from), `_adj_len`, `_adj_children` (parent → child ids in edge-list order), `_adj_parents` (child → first parent, `setdefault` — first-match semantics preserved). Validity is the token `_adj_src is self.edges and len(self.edges) == _adj_len`: the `len` half catches `add_edge`'s in-place append, the `is` half catches wholesale replacement — and because the token pins the old list, allocator `id()` recycling after garbage collection can never fake a hit. On a miss the index rebuilds in one O(E) pass. `children_of` returns a FRESH list per call (callers may bind and mutate it — `painting.py:519` does). All consumers (minimap, navigation, search, editing, coverage, factory, lane view, `import_csv`'s orphan pass, `store._reindex`) ride the cache through unchanged signatures.

**4. The linear dump (`mapper/mermaid.py:131-160`, LLR-PERF.2.2).** `dump` used to test every node for orphanhood with `any(e.parent_id == node.id or e.child_id == node.id for e in graph.edges)` — O(N·E): 18,003,000 edge visits + 6002 full scans on wide-6000. It now builds an incident-id set in ONE local pass over every edge and tests membership. Three load-bearing choices: the pass is LOCAL to the `dump` call, NOT the Lane M adjacency cache (a counting wrapper that swapped `edges` would send a cache variant cold and cost 3E — round-2 probe p3: local = exactly 2E, ratio 2.000); DANGLING edges count toward membership (an edge whose endpoint is missing from `nodes` is skipped when written, unchanged, but its ids still enter the set — semantics identical to the old `any()`); emission order (node-dict iteration order), the `emitted` dedup set, label escaping and the trailing newline are byte-for-byte unchanged. Measured: 11,998 = 2·E edge visits per dump, scaling ratio 2.000.

### The invariants — and the guards that pin them

| Invariant | Guard (fails loudly) |
|---|---|
| the clipped loops write exactly the cells the pre-change loops wrote | `test_bare_canvas_clip_equality` (+`edge` ×4 +`paints_something`) — reference copies of the OLD loops live IN the test file, never a `Canvas` flag; `test_render_grid_clip_identity` over the full fixture grid (empty/single/deep-5000/wide-2000/wide-6000/forest/DAG/panned/fold at 118×34 and 87×34) |
| a selection-only keypress never recomputes the unscaled layout | `test_memo_miss_spy` (1 miss per 5 keypresses), `test_at_075b_memo_misses_and_golden` (byte oracle), `test_memo_invalidation_arms[resize\|title\|fold\|focus\|undo\|add_child\|round_trip]` |
| the `nodes` dict writers stay exactly {`model.py` `add_node`, `editing.py` wholesale} | `test_nodes_writer_census` (+16 planted-form arms) — the memo key relies on the `nodes` dict |
| the `edges` list writers stay exactly {`model.py` `add_edge` (append), `editing.py` `_remove_subtree` (wholesale)} | `test_edges_writer_census` + `test_census_in_place_forms[setitem\|slice\|del\|iadd\|imul\|sort\|reverse\|clear\|extend\|insert\|remove\|pop\|alias]` — 13 in-place/alias forms, one mutation per form |
| cached lookups equal the linear-scan reference through EVERY mutation class, incl. `id()` recycling | `test_cache_mutation_script_equality` (two wholesale replacements back to back, NO lookup between), `test_mid_rebuild_failure_leaves_token_invalid` (the token must be assigned only after the rebuild) |
| `dump` output bytes never drift | `test_dump_fixture_goldens` (legacy/anidado/truncado/wide-6000/forest/empty/single/dangling, base-pinned) + `test_dump_counted_ops_scaling_ratio` (≤ 2·E + c per call, ratio ∈ [1.8, 2.2]) |
| every behaviour golden stays byte-pinned to base `5cde04e` | `test_perf_goldens_manifest.py` (base SHA + per-golden sha256) + AT-065 parity + `test_repair_golden_census.py` — all inside the full-suite gate |
| Lane M never moves cache cost into the renderers | M-M3 file-diff check `git diff 5cde04e -- mapper/views` empty on the Lane M branch — recorded per lane at the DDR (`_child_index` per-render builds stay in `mapper/views/`) |

### How to add a mutation path to `edges` / `nodes` safely

Both caches are invalidated by IDENTITY, not by event — so the only sound writers are the two census-declared ones per collection, and the guards exist precisely to keep it that way:

1. **Prefer the existing writers.** Add a node through `Graph.add_node` (`mapper/model.py:165`) and an edge through `Graph.add_edge` (`:170`) — the cache-token's `len` half catches appends automatically. Remove a subtree the way `screens/map/editing.py` does: wholesale-assign `graph.edges`/`graph.nodes` (`editing.py:216-219`) — the `is` half catches replacement. Nothing else needs to know the caches exist.
2. **If a new writer is genuinely required** (e.g. an in-place `edges.sort()` for a new feature): add the writer to the census declaration FIRST and extend `test_census_in_place_forms` / the planted arms in the same commit — the guard reads the declared set, so the test update and the writer land together and the gate fails until both do. Then decide invalidation: in-place forms keep `id` and may keep `len` — they do NOT invalidate the token, so you must either route through wholesale replacement or widen the token (and the M-M1b stale-cache test will tell you if you got it wrong).
3. **Never key either cache on `id()`** — allocator addresses recycle after `gc.collect()`; both keys pin strong references instead. The M-R2d memo mutant (key on `id(graph)`) is the worked example: unreddenable on this interpreter, unsafe by construction anywhere.
4. **Never give a renderer the model cache.** The renderers keep their own per-render `_child_index` (≤ 0.37 ms/pass, measured) — M-M3 returns any Lane-M-style edit under `mapper/views/` to the trunk.
5. **For the layout memo:** any new INPUT of the unscaled layout (it currently reads exactly: child index, hidden set, graph identity — see the comment at `mapper/views/layered.py:292`) belongs in the memo key. Anything that only changes `card_w`/`gap` (resize, widest title, theme) must NOT be keyed — scaling re-applies per hit. Add an arm to `test_memo_invalidation_arms` in the same commit.

### Components / modules touched

| Module | Role in this batch |
|--------|--------------------|
| `mapper/canvas.py` | span clip in `edge`/`elbow_down` (LLR-PERF.1.1) — bodies only, signatures frozen |
| `mapper/views/layered.py` | `_tree_layout_unscaled` memo on the renderer instance, threaded through `_geometry` (LLR-PERF.1.2); renderers keep their own adjacency build (LLR-PERF.2.3 pin) |
| `mapper/model.py` | `Graph` private adjacency cache with the strong-reference validity token (LLR-PERF.2.1) |
| `mapper/mermaid.py` | `dump` builds its incident set in one local O(N+E) pass (LLR-PERF.2.2) |
| `tests/test_perf_paint_clip.py` (17 nodes) · `tests/test_perf_layout_memo.py` (26) · `tests/test_perf_adjacency.py` (18) · `tests/test_perf_dump.py` (3) · `tests/test_perf_goldens_manifest.py` (2) | the guard files above — 66 nodes, +66 in the suite ledger (3157 → 3223) |
| `tests/perf_goldens_capture.py` + `tests/goldens/perf/**` (MANIFEST + 26 goldens) | deterministic regeneration of every behaviour golden from the current product; base SHA `5cde04e` + sha256 per golden (PDR C10); `-text` line-ending rule in `.gitattributes` (`2c64f76`) |
| `tests/test_a3_census.py` (M) · `tests/test_repair_store_boundary.py` (M) | gate follow-ups: the A3 pin 65 → 80 → 82 — first for the byte-identity arms' arg-ful renders (`084d7b7`), then for the DDR title-arm fix's 2 added render sites (`e5a2a7f`); a store-boundary expectation updated |

### Usage / examples

```bash
# the guard files (single files only, from the worktree root)
python -B -m pytest -q -p no:cacheprovider tests/test_perf_paint_clip.py
python -B -m pytest -q -p no:cacheprovider tests/test_perf_layout_memo.py
python -B -m pytest -q -p no:cacheprovider tests/test_perf_adjacency.py
python -B -m pytest -q -p no:cacheprovider tests/test_perf_dump.py
# regenerate the goldens (run twice — sha256 must not change; requires the -text rule)
python -B tests/perf_goldens_capture.py
```

### Diagrams

none — this batch changed no structure; the four mechanisms live inside existing functions.

### Evidence checklist — docs-writer

- ✓ all four mechanisms read from the shipped source (`mapper/canvas.py:113-141`, `mapper/views/layered.py:192-218/350-431`, `mapper/model.py:125-214`, `mapper/mermaid.py:131-160`), not memory · ✓ measured numbers quoted from `evidence/r1-red.transcript` (12,264), `evidence/r2-red.transcript` (memo arms), `evidence/m1-red.transcript` / `m1b-red.transcript`, `evidence/m2-red.transcript` (11,998 = 2·E), `evidence/p4-wallclock.transcript` (3.9×/4.1×/3.8×/3.5×/48.5×/1.05×) · ✓ invariants table matches the guard files' node names and the requirements' negative controls · ✓ writer-census recipe matches `01-requirements.md` LLR-PERF.2.1/1.2 and the DDR crossed census · ✓ no user-visible change claimed — byte-pinned goldens cited · ✓ no operator paths, home paths or account names in this artifact.
