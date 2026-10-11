# Validation — mapper — Batch 2026-10-10-perf-batch

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`); for Spanish batches **translate the prose, never a label** — the reserved field names are declared in §✅ Verdict and are read literally.
> Phase 4 artifact. Content owner: `qa-reviewer`, who **EVALUATES** the results of the validation strategy fixed in Phase 1, **names who executed each one** and returns the rows; the orchestrator writes `04-validation.md` (`stations/shared-homes-roles.md` §Delegation). The ONE complete gate-suite run is the orchestrator's (`C-25`); a sub-agent consumes the result and never owns the run.

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/guides/validation-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

## ✅ Verdict (read first)

> **Reserved field names.** The **field names and block keywords below are language-independent** — the
> validator parses them literally and they are never translated:
> `Result` · `Layer 0` · `Evidence checklist` · `⏸ DEFER`
> Everything else on this page — headings, guidance, the prose in every cell — is translated with the batch.
> **One strategy, not two:** the flow ships no alias table, so a translated label is read as an ABSENT one and the rule keyed on it reports a true-sounding silence.
> **And one FLOW-WIDE reserved token, read out of this artifact by `V42` no matter which template minted it:** `⏸ DEFER`. It is a MARKER rather than a field name, which is why it is stated here *and* in `/dev-flow` §Language of artifacts rather than in a per-template list — a deferral can be written in any batch artifact, including the ones that carry no block at all.
>
> **And so are the three verdict tokens** `PASS` · `PASS-WITH-NOTES` · `FAIL`, which are VALUES and not prose.
> A Spanish batch writes `- **Result:** PASS`, not `- **Resultado:** aprobado`: the label, the tokens and the
> reviewer-identity tokens below are the machine's vocabulary.

- **Result:** PASS-WITH-NOTES
- **Layer 0:** 4 unit(s) met the criterion · 4 carry a named reddening mutation (span clip, layout memo, adjacency cache, linear dump — every negative control executed RED with a sha256-verified byte-identical restore)
- **Requirements:** 8/8 pass (2 surviving HLR-PERF + 6 surviving LLR-PERF; HLR-PERF.3 / LLR-PERF.3.1–3.2 WITHDRAWN to B-118, marked below) · 0 blocker fails
- **Black-box acceptance (Layer B):** ✓ every story's `AT` observes its outcome through the shipped surface (boundary + negative) — US-PERF-003 and AT-077/077b are withdrawn with Lane S, marked
- **Surface-reachability (bidirectional):** ✓ all named inputs AND outputs/deliverables reached/observed at the surface
- **Supersession inspection (read off the P3 packets):** ✓ all surviving refs negative (the crossed census at the DDR proved Lane R never touched Lane M's files and vice versa; `mapper/views/layered.py` is Lane R's own file by plan — M-M3 recorded per lane, `git diff 5cde04e unit/perfm1 -- mapper/views` empty)
- **Test ledger:** ✓ reconciles (`base − D + A = post` → 3157 − 0 + 66 = 3223)
- **Evidence checklist (qa-reviewer):** PENDING — the rows and re-derived numbers are in place for the orchestrator's qa-reviewer pass

> If every line is ✓, the Detail below is reference only. Any ⚠/✗ → read the matching part.

**Verdict reason (3 lines):** all 8 surviving requirements pass with executed counted-operations oracles and every painted byte / `.mmd` byte identical to the base-pinned goldens (26 goldens + MANIFEST, captured on base `5cde04e` before the lanes forked); the ledger reconciles (3157 − 0 + 66 = 3223; collected 3226, 24 deselected by `pyproject.toml`) and the join gate closed green (run 2: 3223 passed / 3 xfailed / 0 failed). The notes: ① B-120 — the layout memo covers the render path only, three module-level readers still lay out per key (declared scoping, backlog row exists) · ② load is unchanged (2.32 → 2.22 s, 1.05×) because it is YAML-scan-bound — out of this batch's scope, carried as a finding (backlog row proposed, none existed) · ③ Lane S / US-PERF-003 withdrawn to B-118 by a pre-written ruling after spike PERFS was inconclusive. None blocks the gate. **FINAL full-suite gate at the closing SHA: `PERF_FINAL_GATE_PENDING`** (orchestrator fills this row).

---

## Detail (reference)

### Layer 0 — unit

| Unit | Which criterion | Node id | Result |
|---|---|---|---|
| `Canvas.elbow_down` / `Canvas.edge` span clip (`mapper/canvas.py`) | clipped spans write EXACTLY the cells the pre-change loops wrote, at O(painted) iterations; the two-keypress scripted session (`l`,`j`) on wide-2000 at 118×34 performs ≤ 61,500 `wire` calls (measured 12,264; baseline 23,983,998) | `tests/test_perf_paint_clip.py::test_bare_canvas_clip_equality` (+9 `elbow` params · `test_bare_canvas_clip_equality_edge` ×4 · `…_paints_something`) · `::test_wire_count_budget` · `::test_render_grid_clip_identity` | pass |
| the UNSCALED `_tree_layout` memo on `LayeredRenderer` (`mapper/views/layered.py`) | five selection-only keypresses cost exactly 1 memo miss; every painted step byte-equals the base golden; a hit re-applies `card_w`/`gap` scaling in O(N) | `tests/test_perf_layout_memo.py::test_memo_miss_spy` · `::test_at_075b_memo_misses_and_golden` · `::test_memo_invalidation_arms[resize\|title\|fold\|focus\|undo\|add_child\|round_trip]` · `::test_memo_id_reuse` · `::test_nodes_writer_census` | pass |
| `Graph` private adjacency cache (`mapper/model.py`) | cached `children_of`/`parent_of` equal the linear-scan reference at every step of the mutation script (incl. two wholesale `edges` replacements with no lookup between — `id()`-recycle arm); ≤ 1 full edge pass for 100 warm lookups; fresh list per call | `tests/test_perf_adjacency.py::test_cache_mutation_script_equality` · `::test_cache_counted_ops` · `::test_mid_rebuild_failure_leaves_token_invalid` | pass |
| `mermaid.dump` LOCAL incident pass (`mapper/mermaid.py`) | ONE dump call on wide-6000 iterates `graph.edges` 11,998 = 2·E times (bound 2·E + 4; baseline 18,003,000); scaling ratio 2.000 ∈ [1.8, 2.2]; orphan/dangling semantics byte-equal the base goldens | `tests/test_perf_dump.py::test_dump_counted_ops_scaling_ratio` · `::test_dump_fixture_goldens` · `::test_at_076_real_save_dump_budget` | pass |

**Measured by mutation, never by line coverage.** For each unit, name the mutation and paste the RED:

| Unit | Mutation applied | RED observed? | Transcript |
|---|---|---|---|
| span clip | M-R1a — clip removed entirely → `wire` count back to **23,983,998** vs cap 61,500 (also RED at the earlier 1,200,000 cap) | yes — `1 failed`; restore sha256-equal (`d354bd46…4838a2`) | `evidence/r1-red.transcript` (sha256 `61da2b990cd286b33cc7876b3e781a642d53fbe378dd60e9eae21d2385679f14`) |
| span clip | M-R1b — clip upper bound clamped to `min(xb, w-1)` (drops one in-bounds cell) | yes — byte-grid / bare-`Canvas` equality RED | `evidence/r1-red.transcript` |
| span clip | y-only clip (bus row not x-clipped) · clip removed · clip span WIDENED (partial-regression probe, 88,226 ≈ 7.2× the measured 12,264 — the pre-tightening 1,200,000 cap would have passed it) | yes — all three RED under the tightened cap; restores sha256-equal | `evidence/ddr2-red.transcript` (sha256 `b5a08f19f35594259270578b8eb95996ce26deb8eb1358897c6e5bdc39b1f3b0`) |
| layout memo | M-R2 — no memo (hit check disabled) → open alone costs 4 misses | yes — `assert 4 == 1`; restore sha256-equal (`3e34fd90…e04743`) | `evidence/r2-red.transcript` (sha256 `82695d1e7c5717da2518a1f1274854fc5e01c97e96be2c587ee431a026dca5cc`) |
| layout memo | M-R2c — cache the SCALED layout (key drops `card_w`/`gap`) → the `resize` AND `title` arms RED (the `[title]` arm gained a renderer-level full-text compare — the region-clipped compare is header-only at 118×34 for its fixture) | yes — both arms RED; restore sha256-equal | `evidence/ddr2-red.transcript` §2 |
| layout memo | M-R2d — key on `id(graph)` instead of the strong reference → documented non-deterministic on this interpreter: address reuse 0/2000 forced allocations, the `id()`-keyed mutant NEVER went RED; safety rests on the strong-reference construction (the entry pins the old graph) + Lane M's two-replacement script — recorded, not fabricated (ruling R13 escape) | not observable on this interpreter — declared | `evidence/r2-red.transcript` (forced-reuse probe, 8/8 green) |
| layout memo | M-R2e — a planted `nodes`-dict writer site → the Lane R nodes-writer census RED | yes | `evidence/r2-red.transcript` (mutation 5) |
| adjacency cache | M-M1a — bypass the cache → counted-ops RED (100 full passes) · M-M1b — `len`-only key + same-length wholesale replacement → equality RED (stale results) | yes — both | `evidence/m1-red.transcript` (sha256 `b20178d3778670fc747740eb16656c4c2d515e19cd5edadcefaabbb19e87a91f`) |
| adjacency cache | token-before-index rebuild ordering (the P3 code-review MED) → `children_of('n3')` drifted from the reference | yes — `1 failed`; fixed in `cd9cad2` (token last), the new node `test_mid_rebuild_failure_leaves_token_invalid` reddens under the old order; restore sha256-equal | `evidence/m1b-red.transcript` (sha256 `55b425bdc501b6a0c3f57ab8b09e67a6611340cd355bc6f609bd843b422bd5a6`) |
| adjacency cache | M-M1c — 13 in-place/alias `edges` forms planted one per form (`setitem\|slice\|del\|iadd\|imul\|sort\|reverse\|clear\|extend\|insert\|remove\|pop\|alias`) → census guard RED each time | yes — every form detected | `evidence/m1-red.transcript` |
| linear dump | M-M2a — restore the per-node `any()` scan → counted arm RED (1,125,750 visits vs bound 3,002 on wide-1500; AT-076 RED at 18,009,001 vs bound 12,004) | yes | `evidence/m2-red.transcript` (sha256 `c84b8c031d35864118fb8b5ff03af7d3b19dc53c8090d2e3422de84856328d96`) |
| linear dump | M-M2b — orphan emission loop reordered → `orphan-order` byte arm RED (dangling-solo arm RED under the dangling mutant) | yes — both | `evidence/m2-red.transcript` |
| goldens manifest | one golden byte flipped → manifest sha256 arm RED (instrument proof for the behaviour oracle itself) | yes — `1 failed`; byte-identical restore | `evidence/g0-capture.transcript` (sha256 `9ca89f126ccee8cf3058cfa602df63db2d723c5e22572ae460fc58cc3cabfad3`) |

### UX walkthrough — only if trigger family D fired

| Criterion (when the user does X, they observe Y) | Driven with the REAL mechanism | Painted result asserted | Verdict |
|---|---|---|---|
| not applicable — family D did not fire | — | — | — |

**Mechanism used:** `none — inspected only`

| Act | What it is | Performed? |
|---|---|---|
| Automated walkthrough | the criteria above, driven through the REAL mechanism | `not applicable — no trigger-D surface` |
| Expert inspection | a cognitive walkthrough against declared criteria, by a reviewer and not a user | `not applicable — no trigger-D surface` |
| Evaluation with users | real users of the system, doing the tasks named in the context of use | `not applicable — no trigger-D surface` |

- **Method:** trigger family D did not fire. The batch is behaviour-preserving performance work: it adds no painted string, no input surface, no new screen. That the picture the operator sees is unchanged is proven by the byte-identity oracle instead: every painted step of the AT-075/075b scripted session byte-equals the golden pinned at base SHA `5cde04e` before the lanes forked (`tests/goldens/perf/at075_075b_wide2000_118x34.txt`, MANIFEST sha256-pinned), and the full render grid + the pre-existing AT-065 parity goldens + `test_repair_golden_census.py` stay green.
- **Participants or population:** none — not applicable.
- **Evidence of the evaluation:** none — not applicable (the walkthrough was skipped because family D did not fire, not because a criterion was dropped).
- **Limits:** this establishes nothing about real-user UX because, by design, no user-facing surface changed; the goldens bound the claim to the scripted sessions' steps and the captured widths (118×34 render grid, 118×34 and 87×34 parity).

### Layer A — functional (white-box): per-requirement results
> `TC-NNN` ↔ LLR/HLR. `Result` = pass / fail. `Evidence` = command output, observed behavior, inspection note, or analysis result.
> All gate evidence is the orchestrator's join gate run 2 (`evidence/join-gate-run2-full-suite.transcript` — **3223 passed, 24 deselected, 3 xfailed in 1802.10s, exit=0**, sha256 `16efbc896201a2dcec3412c282420467064ff6a31144422cc2280eca69080124`); per-node measured numbers are quoted from the lane transcripts below. Selector counts re-collected at `3b84e2c` (HEAD; the gate tree's product+tests are byte-identical to HEAD's — only `.dev-flow/` records differ).

| Req | Method | Executed verification | Numeric threshold | Result | Evidence |
|-----|--------|-----------------------|-------------------|--------|----------|
| HLR-PERF.1 | test | `python -B -m pytest -q -p no:cacheprovider tests/test_perf_paint_clip.py::test_at_075_keypress_wire_budget tests/test_perf_paint_clip.py::test_wire_count_budget tests/test_perf_paint_clip.py::test_bare_canvas_clip_equality tests/test_perf_paint_clip.py::test_render_grid_clip_identity tests/test_perf_layout_memo.py::test_at_075b_memo_misses_and_golden tests/test_perf_layout_memo.py::test_memo_miss_spy` | exit 0; two keypresses (`l`,`j`) on wide-2000 at 118×34 ≤ 61,500 `wire` calls — **measured 12,264** (baseline 23,983,998; cap = 5× measured, DDR qa LOW-4); memo spy reads exactly 1 miss across 5 selection-only keypresses; 0 byte diffs on the fixture grid and the parity goldens | pass | measured in `evidence/r1-red.transcript` §2 + `evidence/ddr2-red.transcript` §1 (`wire calls … : 12264 (baseline 23983998, cap 61500)`); gate run 2 transcript; byte oracle: `tests/goldens/perf/**` MANIFEST — **executed by: orchestrator** (gate), sub-agent (count re-collection) |
| HLR-PERF.2 | test | `python -B -m pytest -q -p no:cacheprovider tests/test_perf_adjacency.py::test_cache_mutation_script_equality tests/test_perf_adjacency.py::test_cache_counted_ops tests/test_perf_adjacency.py::test_edges_writer_census tests/test_perf_adjacency.py::test_census_in_place_forms tests/test_perf_dump.py::test_at_076_real_save_dump_budget tests/test_perf_dump.py::test_dump_counted_ops_scaling_ratio tests/test_perf_dump.py::test_dump_fixture_goldens` | exit 0; ONE `mermaid.dump` on wide-6000 iterates edges 11,998 = 2·E ≤ 2·E + 4 (baseline 18,003,000); scaling ratio 2.000 ∈ [1.8, 2.2]; 100 warm cached lookups scan edges ≤ 1 full pass; AT-076's persisting-save dump = 12,000 ≤ 12,004 and the saved `.mmd` byte-equals the golden; 0 byte diffs on all 8 dump goldens | pass | `evidence/m2-red.transcript` (measured counts + GREEN/RED); `evidence/m1-red.transcript` (post-restore whole-file `17 passed`); gate run 2 transcript |
| HLR-PERF.3 | — | **WITHDRAWN to B-118** (2026-10-10, ledger `LED-2026-10-10-perf-batch.3`) — spike unit PERFS inconclusive (mount renders 2× before AND after the prototype at 118×34/87×34, final canvas byte-identical, wide-2000 unmeasured after the unit timed out); `tests/test_perf_mount.py` was never created; the parity gate named in the requirement stays green inside the full suite | — | withdrawn | `evidence/perfs-spike.transcript` (sha256 `2bdbcdd33cbeebfbb280964bdde83911270f63c96126243c6afbd2d263a6a3ff`), `evidence/perfs-check-green.txt`, `evidence/perfs-baseline.json`, `spike/perfs-prototype.diff`; backlog B-118 |
| LLR-PERF.1.1 | test (unit) | `python -B -m pytest -q -p no:cacheprovider tests/test_perf_paint_clip.py::test_wire_count_budget tests/test_perf_paint_clip.py::test_bare_canvas_clip_equality` (17 nodes in the file) | exit 0; clipped loops visit no out-of-canvas cell; bare-`Canvas` equality vs in-test reference copies of the pre-change loops on every shape (`x1 < x0`, fully off-canvas, `ybus` above/below, negative pan); 12,264 ≤ 61,500 | pass | `evidence/r1-red.transcript`; `evidence/ddr2-red.transcript` §3–§5 (y-only / removed / widened-span mutants all RED under the tightened cap); gate run 2 transcript |
| LLR-PERF.1.2 | test (unit) | `python -B -m pytest -q -p no:cacheprovider tests/test_perf_layout_memo.py::test_memo_miss_spy tests/test_perf_layout_memo.py::test_memo_invalidation_arms tests/test_perf_layout_memo.py::test_nodes_writer_census` (26 nodes in the file) | exit 0; 5 selection-only keypresses → exactly 1 miss; `resize`/`title` arms 0 extra misses + byte-identical repaint (scaling re-applies); `fold`/`focus`/`undo`/`add_child` miss exactly once; round trip 0 extra misses; the declared 2-writer `nodes` census holds, every banned form planted REDs it | pass | `evidence/r2-red.transcript`; `evidence/ddr2-red.transcript` §2 (M-R2c reddens both arms); gate run 2 transcript |
| LLR-PERF.1.3 | test | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_parity.py tests/test_repair_golden_census.py tests/test_perf_paint_clip.py::test_render_grid_clip_identity` | exit 0; 0 parity-golden line diffs (118/87 columns); 0 census-pin failures; 0 fixture-grid cell diffs vs the unclipped reference render | pass | gate run 2 transcript (all three files inside the 3223); goldens `tests/goldens/perf/**` (base SHA `5cde04e`, MANIFEST sha256) |
| LLR-PERF.2.1 | test (unit) | `python -B -m pytest -q -p no:cacheprovider tests/test_perf_adjacency.py::test_cache_mutation_script_equality tests/test_perf_adjacency.py::test_cache_counted_ops` (18 nodes in the file) | exit 0; 0 equality mismatches across the mutation script incl. the two-replacement no-lookup stretch; warm counted ops ≤ 1 edge pass (baseline uncached 100 passes); `children_of` returns a fresh list | pass | `evidence/m1-red.transcript`; `evidence/m1b-red.transcript` (the token-ordering regression arm); gate run 2 transcript |
| LLR-PERF.2.2 | test (unit) | `python -B -m pytest -q -p no:cacheprovider tests/test_perf_dump.py::test_dump_counted_ops_scaling_ratio tests/test_perf_dump.py::test_dump_fixture_goldens` (3 nodes in the file) | exit 0; 11,998 = 2·E ≤ 2·E + 4 per dump; ratio 2.000 ∈ [1.8, 2.2]; 0 byte diffs on every fixture golden incl. the dangling-edge case; orphan emission order = node-dict order | pass | `evidence/m2-red.transcript`; gate run 2 transcript |
| LLR-PERF.2.3 | inspection | `git diff 5cde04e unit/perfm1 -- mapper/views` on the Lane M branch BEFORE the join — **empty** (recorded per lane at the DDR, ruling R17); Lane R legitimately edits `mapper/views/layered.py` (its own file); `grep -rn "_child_index" mapper/views/` — per-render builds present; 0 new cross-module imports of cache names | exit 0; 0 bytes under `mapper/views/` from Lane M; the model cache stays `_`-private to `mapper/model.py` | pass | `design/DDR-2026-10-10-perf-batch.md` B3 (the crossed census, quoted empty diffs) |
| LLR-PERF.3.1 | — | **WITHDRAWN to B-118** with HLR-PERF.3 (ledger `LED-2026-10-10-perf-batch.3`) — the former test 077 node was never created (`tests/test_perf_mount.py` does not exist) | — | withdrawn | `evidence/perfs-spike.transcript`; backlog B-118 |
| LLR-PERF.3.2 | — | **WITHDRAWN to B-118** with HLR-PERF.3 (ledger `LED-2026-10-10-perf-batch.3`) — the former test 077b node was never created; the B-56/B60 settle-pass heal it was to pin remains covered by the pre-existing strip tests inside the full suite | — | withdrawn | `evidence/perfs-spike.transcript`; backlog B-118 |

**A worked example — text to read, never rows of your record.** It sits in a fence so that nothing has to be deleted: a row copied out of it would claim a verification nobody ran. Write your own rows in the table above.

```text
| *(example)* HLR-001 | test | `pytest … -k TC-001` | exit 0 | | |
| *(example)* LLR-001.1 | test (unit) | `…` | `…` | | |
```

### Layer B — behavioral (black-box) acceptance

| US | Acceptance test (`AT-NNN`) | Surface driven | Deliverable observed (path / element) | repr · boundary · negative | Result |
|----|----------------------------|----------------|---------------------------------------|----------------------------|--------|
| US-PERF-001 | AT-075 — `tests/test_perf_paint_clip.py::test_at_075_keypress_wire_budget` (17 nodes in the file); AT-075b — `tests/test_perf_layout_memo.py::test_at_075b_memo_misses_and_golden` (26 nodes) | the real app — `MapperApp(tmp_path)` + `app.run_test(size=(118,34))` + `pilot.press(...)` real keys (`_open`/`_press` helpers imported from `tests/test_draft_save.py`) on a generated wide-2000 map | the `#map-canvas` region strips after open, `l`, `j` (AT-075, wire counter reset after mount) and open + `l,j,j,j,j`, archive `x`/`y`, `l` (AT-075b) — every painted step byte-equal to the golden pinned at base SHA `5cde04e`; the counted `wire` calls and the `_layout_misses` spy read through the shipped surface | repr: pressing `l`/`j` repaints with ≥ 5× less render work and the picture is exactly the same (12,264 vs 23,983,998 calls = 1,957×; 1 memo miss per 5 keypresses) · boundary: fold/unfold, resize, a widening-title edit, focus toggle, undo, add-child via real keys, an outline↔radial↔layered round trip — each repaints correctly (arm rows in Layer A) · negative: M-R1a/M-R1b (clip), M-R2/M-R2b/M-R2c (memo), M-M1a/M-M1b (cache) — each executed RED, sha256-verified restore | pass |
| US-PERF-002 | AT-076 — `tests/test_perf_dump.py::test_at_076_real_save_dump_budget` (3 nodes) | the real persisting gesture — open a SAVED generated wide-6000 map, add a child with the `a` action through real keys (persists via `_save_or_toast`, `screens/map/editing.py:111-124`), counting wrapper on `mapper.mermaid.dump` itself | the saved `.mmd` bytes after the edit — byte-equal to the golden pinned at base SHA `5cde04e` (pinned to the map AFTER the edit); ONE dump call iterating 12,000 ≤ 2·E + 4 edges (baseline 18,009,001 for the same gesture) | repr: saving a large map costs work proportional to its size and the file opens identically · boundary: forest (orphan order pinned), deep chain 5000, a dangling edge (incident counting covers it), empty/single graphs dump exactly as today · negative: M-M2a (per-node scan → count RED), M-M2b (orphan reorder → byte RED), M-M1b (stale cache → equality RED) — each executed RED | pass |
| US-PERF-003 | AT-077 / AT-077b — **WITHDRAWN to B-118** (ledger `LED-2026-10-10-perf-batch.3`); the nodes were never created; the story row is kept, marked | — | — | — | withdrawn |

### Bidirectional surface-reachability matrix (extends A-5)
> Every named INPUT dimension AND every named OUTPUT/deliverable is exercised/observed through the handler — not only the service API.

| Direction | US dimension / deliverable | Service param / producer | Reached/observed at surface? | TC / AT | Status |
|-----------|---------------------------|--------------------------|------------------------------|---------|--------|
| input | US-PERF-001 real navigation keystrokes (`l`/`j`) | `pilot.press(...)` on the mounted map screen | yes | AT-075, AT-075b | ✓ |
| output | US-PERF-001 the painted canvas region strips | `#map-canvas` region strips vs the pinned text golden (118×34) | yes | AT-075, AT-075b | ✓ |
| input | US-PERF-002 the real persisting edit gesture | the `a` add_child action through real keys → `_save_or_toast` | yes | AT-076 | ✓ |
| output | US-PERF-002 the saved `.mmd` deliverable | `MapStore.save` → `mermaid.dump` bytes on disk vs the pinned golden | yes | AT-076 | ✓ |
| input | US-PERF-001 structural repaint triggers (fold/resize/title/focus/undo/add-child/round-trip) | real keys and scripted gestures through the shipped screen | yes | `test_memo_invalidation_arms` (7 arms) | ✓ |
| output | US-PERF-001/US-PERF-002 the byte-identity oracle itself | 26 goldens + MANIFEST under `tests/goldens/perf/` (captured at base `5cde04e` before the fork) | yes | `tests/test_perf_goldens_manifest.py` (2 nodes) | ✓ |

### Signed-balance test ledger
> `post = base − D + A`. State counts in collected / passed-lean / passed-full form.

| base | − D | + A | = post | actual collected | passed-lean / full | reconciles? |
|------|-----|-----|--------|------------------|--------------------|-------------|
| 3157 passed + 3 xfailed (base `5cde04e`, run at the join in `../perf-base`) | 0 — `git diff -U0 5cde04e HEAD -- tests \| grep '^-.*def test_'` prints nothing (no test function deleted or rewritten; 2 test files MODIFIED — `tests/test_a3_census.py` pin 65 → 80, `tests/test_repair_store_boundary.py` — 0 functions removed) | 66 (derived: post − base + D = 3223 − 3157 + 0; re-collected at `3b84e2c`: `test_perf_paint_clip.py` 17 + `test_perf_layout_memo.py` 26 + `test_perf_adjacency.py` 18 + `test_perf_dump.py` 3 + `test_perf_goldens_manifest.py` 2 = 66 — matches exactly) | 3223 passed + 3 xfailed = 3226 | 3226 (`3223 passed, 24 deselected, 3 xfailed in 1802.10s`, join gate run 2) | 3223 / 3223 + 19 slow (slow lane, `evidence/join-slow-lane.transcript` — `19 passed, 3231 deselected in 52.45s`, sha256 `63d6a2c89abd789b5bcb6ee20969658558d8f40b41de4b4c8fa9ee9eb5e922b1`) | yes |

- Gate evidence: `evidence/join-gate-run2-full-suite.transcript` — **3223 passed, 24 deselected, 3 xfailed, 0 failed in 1802.10s, exit=0** (sha256 `16efbc896201a2dcec3412c282420467064ff6a31144422cc2280eca69080124`). The 24 deselected are the `slow`/`network` markers (`pyproject.toml`).
- Run history: join gate run 1 at product `42b79c7` — `1 failed, 3222 passed` — the single failure was the A3 census pin (`tests/test_a3_census.py::test_tc_a3_the_census_cardinalities_are_PINNED`), fixed test-only in `084d7b7` (pin 65 → 80 for the byte-identity arms' arg-ful renders); run 2 at the same product tree re-ran the whole suite green (evidence committed at `b5e7cce`). **FINAL full-suite gate at the closing SHA: `PERF_FINAL_GATE_PENDING`.**
- Arithmetic: 3157 − 0 + 66 = 3223 (passed-lean) and 3160 − 0 + 66 = 3226 (collected) — both reconcile.

### Gaps detected
| ID | Requirement | Gap | Severity | Proposed action |
|----|-------------|-----|----------|-----------------|
| G-001 | HLR-PERF.1 (scoping) | the layout memo covers the render path only — `painted_ids` (`mapper/views/layered.py:495`), `pan_extent` (`:509`) and the pan clamp's `layered_geometry` reader (`mapper/screens/map/panning.py:277`) still lay out on every selection-only key | minor (declared scoping, ledger `LED-2026-10-10-perf-batch.5`) | backlog B-120 — thread the renderer memo into the three module-level readers (screen-side files, outside this batch's lanes) |
| G-002 | HLR-PERF.2 (out of scope) | load wall-clock unchanged (2.32 → 2.22 s, 1.05×): `MapStore.load` is 100% YAML `safe_load` of the metadata sidecar (5.41 s of 5.62 s cumulative under profiler at wide-6000, `spike/perf-baseline.md` §7.4) — no batch code lies on that path | minor | backlog row proposed (none existed) — B-121: sidecar parse cost (lazy/metadata-only parse or a cheaper codec) in a store-side batch; the P4 table states it as out of scope |
| G-003 | HLR-PERF.3 / US-PERF-003 | mount still renders 2–3×; the single-render design was not proven by spike PERFS | major → resolved as withdrawal | backlog B-118 — measure wide-2000 first, then design a single-render mount that keeps `refresh_canvas`'s ordering and the settle pass intact |
| G-004 | LLR-PERF.1.2 (M-R2d) | the `id()`-recycle mutant cannot be reddened on this interpreter (address reuse 0/2000 forced allocations); safety is by construction + Lane M's two-replacement script, not by a RED memo test (ruling R13 escape, recorded at the DDR C4) | minor (accepted, declared) | leave as declared; re-visit only on a runtime that recycles addresses |

### Escaped-bug regression (if a defect escaped the suite)

| Regression id (`AT-NNN` / `TC-NNN`) | Pre-fix run (evidence it FAILED) | Pre-fix RED kind (value / shape) | Post-fix value-discriminating? (QC-2) | Post-fix result | Reconciled node |
|-------------------------------------|----------------------------------|----------------------------------|----------------------------------------|-----------------|-----------------|
| TC-A3 — `tests/test_a3_census.py::test_tc_a3_the_census_cardinalities_are_PINNED` | join gate run 1, `evidence/join-gate-run1-full-suite.transcript` (sha256 `06a24f17c296ae015c7d981003862f85774eef7f54004a265e0f3c21a3890756`) — `1 failed, 3222 passed` | value: the pinned renderer cardinality 65 vs the 80 arg-ful renders the byte-identity arms legitimately add — the pin was stale the moment the new arms landed; the failure is the pin working, not a product defect | yes — the pin asserts an exact cardinality (65 → 80 in the test-only fix `084d7b7`); any future drift fails it again | join gate run 2: 3223 passed / 0 failed | `tests/test_a3_census.py::test_tc_a3_the_census_cardinalities_are_PINNED` |

### Evidence checklist — qa-reviewer (full)
> Attach `qa-reviewer`'s completed evidence checklist (items in `agents/qa-reviewer.md`), each marked ✓/✗ with one-line evidence. An unchecked or evidence-less item blocks the gate.

**Who executed what:**
- **The orchestrator (Claude Opus 5.5)** ran the ONE complete gate suite (C-25): join gate run 1 (`42b79c7`) and run 2 (`evidence/join-gate-run2-full-suite.transcript`, 3223 passed / 0 failed) plus the slow lane (`evidence/join-slow-lane.transcript`, 19 passed). It owns every gate transcript cited above and the P4 wall-clock measurement (`evidence/p4-wallclock.transcript`, DeepSeek `deepseek-v4-pro`).
- **Workers (Kimi `kimi-for-coding`)** built every increment (trunk capture + lanes R and M in parallel worktrees), executed each lane's negative-control transcripts (r1/r2/m1/m1b/m2-red), and drafted this file (P4, this unit).
- **The sub-agent (Kimi, this file's drafter)** re-collected every selector count (`--collect-only`, none collects 0), re-derived the ledger arithmetic, ran the function-level deleted-test check (`git diff -U0 5cde04e HEAD -- tests | grep '^-.*def test_'` → no output), and re-hashed every cited evidence file with the declared sha256 command.
- **The `qa-reviewer`** review cell is **PENDING** — the orchestrator's qa-reviewer pass fills the cell and the checklist marks after re-reading.

| # | Item | ✓/✗ | Evidence |
|---|---|---|---|
| 1 | Acceptance criteria as outcomes | ✓ | AT-075/075b/076 observe the outcomes through the shipped surface (Layer B); AT-077/077b withdrawn, marked |
| 2 | Explicit Expected | ✓ | every Layer A row carries its numeric threshold with the measured value (12,264 / 1 miss / 11,998 = 2·E / ratio 2.000 / 0 byte diffs); gate 3223 / 3 xfailed / 0 failed |
| 3 | Edge cases | ✓ | bare-`Canvas` shapes (`x1 < x0`, off-canvas, `ybus` above/below, negative pan); panned ViewState + fold in the render grid; forest/dangling-edge/empty/single dump fixtures; the two-replacement no-lookup cache stretch; 87×34 reflow parity |
| 4 | Regression checklist | ✓ | gate run 2 transcript (3223/0 failed) + slow lane (19 passed) + the byte-identity oracle (26 goldens + MANIFEST + parity + census, all inside the gate) |
| 5 | Exit criteria | ✓ | 100% of the surviving HLR/LLR covered with a pass; every AT GREEN with an executed RED; 0 failed; the withdrawn 3.x rows are marked, not silently dropped |
| 6 | No PII / secrets | ✓ | no operator paths, no home paths, no account names written anywhere in this artifact |
| 7 | Mode + executor per result | ✓ | "executed by: orchestrator" on the gate rows; sub-agent counts marked as re-collection |
| 8 | Layer B with boundary + negative | ✓ | US-PERF-001/002 rows each carry repr/boundary/negative; US-PERF-003 marked withdrawn |
| 9 | Bidirectional reachability | ✓ | 6 inputs/outputs, all ✓ |
| 10 | Ledger | ✓ | 3157 − 0 + 66 = 3223; collected 3226 (24 deselected); 0 test functions deleted (function-level check re-run by the drafter) |
| 11 | No unfilled template | ✓ | this checklist pasted; example rows left fenced, not copied |

**Reviewer cell:** PENDING — the orchestrator's qa-reviewer (independent, read-only) re-reads this file, verifies the re-derived numbers against the cited transcripts, and stamps APPROVE / conditions here.
