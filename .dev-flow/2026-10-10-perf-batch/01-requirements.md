# Requirements Document — mapper — Batch 2026-10-10-perf-batch

> **Artifact language**
> This template is the canonical **English scaffold**. Generate the artifact in the batch's development language (`state.json` `language`). For Spanish batches, translate the **prose** — section headers and guidance — **and never a label**, and use `deberá` as the normative keyword (≡ `shall`). The normative RULES in this preamble are **language-independent** and enforced regardless of artifact language.

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/guides/req-template.md` and its part 2, `templates/guides/req-template.part2.md`, explain each field below and the rules that read them. It ships with the flow and is not copied into this batch.

> **Reserved field names.** The **field names and block keywords below are language-independent** — the
> validator parses them literally and they are never translated:
> `Validation` · `Acceptance test(s)` · `Boundary catalog` · `Negative control` · `Premise evaluation` · `Fork preconditions` · `Ledger` · `Requirement` · `⏸ DEFER`
> Everything else on this page — headings, guidance, the prose in every cell — is translated with the batch.
> **One strategy, not two:** the flow ships no alias table, so a translated label is read as an ABSENT one and the rule keyed on it reports a true-sounding silence.
> **And one FLOW-WIDE reserved token, read out of this artifact by `V42` no matter which template minted it:** `⏸ DEFER`. It is a MARKER rather than a field name, which is why it is stated here *and* in `/dev-flow` §Language of artifacts rather than in a per-template list — a deferral can be written in any batch artifact, including the ones that carry no block at all.

---

## 1. Introduction

### 1.1 Purpose

Specify the requirements for the performance-and-scale batch (backlog B-33/S-15 follow-up,
operator-ruled 2026-10-09/10): measured at P0 (`spike/perf-baseline.md` §1–§7), every navigation
keypress repaints the whole map (0.56–1.71 s/keypress at 2000 nodes; 23,983,998 `Canvas.wire` calls
for two keypresses on wide-2000), mount paints three times (layered `render` ncalls=3), and save is
O(N·E) in the Mermaid dump (18,003,001 genexpr iterations at N=6000). The batch ships
**behaviour-preserving remedies only** — every painted cell and every persisted byte stays identical —
across three disjoint lanes: renderer work per paint, model adjacency + serialisation, and mount
paint count.

### 1.2 Scope

Covers: (Lane R) clipping painted spans to the canvas rectangle before iterating, and memoising
`LayeredRenderer._tree_layout`'s UNSCALED layout on strong references — byte-identical paint; (Lane M) a private cached
adjacency on `Graph` invalidated on edge mutation (order- and first-match-preserving), and a linear
`mermaid.dump` orphan pass — byte-identical `.mmd` text; (Lane S) one paid render at mount with the
`_declare_after_layout` settle pass preserved — identical painted result. Numeric thresholds are
enforced by deterministic call-count / cell-count oracles; wall-clock before/after is P4 evidence
only (median of 3, `spike/perf_harness.py` / `perf0c_profile.py`).

Does NOT cover: the S-18 work budget or any degradation notice (changes what is painted — D1;
prototype round first); the dense-DAG cost of B-33 beyond these remedies (the single-visit
shared-subtree layout changes painted coordinates on multi-parent graphs — ⏸ DEFER to the S-18
prototype round, with PERF0 §2 evidence recorded in the PDR §6); B-115 / B-116 / B-117; the YAML
load cost (§7.4 — O(document), the format's own price); any interface signature change (all frozen
interfaces stay frozen, PDR §4).

### 1.3 Definitions, acronyms, abbreviations

| Term | Definition |
|------|------------|
| strong-reference validity check | the cache-validity rule for both the adjacency cache and the layout memo: a hit requires the source reference `is` the live object plus a length match (`self._adj_src is self.edges and len(self.edges) == n`; the memo keys on the `Graph`/`edges`/`nodes` objects, `root_id`, hidden set) — identity, not `id()`, carries validity, so object-identity reuse after garbage collection can never fake a hit |
| edge-mutation census | the exhaustive list of post-construction writers of `Graph.edges`: `mapper/model.py:170` (`add_edge`, append) and `mapper/screens/map/editing.py:217-219` (`_remove_subtree`, wholesale assignment) — and no other site |
| paid render | a renderer `render` call that paints new canvas content; a settle pass whose region is already current is not paid (the `_rendered_for` guard skips it) |
| counted-operations oracle | a deterministic test oracle that counts calls/iterations (e.g. `Canvas.wire` calls, `graph.edges` iterations, memo misses) — never wall-clock |
| memo-miss spy | a counter on the layout-memo HIT CHECK inside module-level `_geometry` (`views/layered.py:306`) — `_tree_layout` itself runs ~10× per two renders (`evidence/perf0c-nav.transcript:44`), so the oracle counts misses at the named check point, never layout invocations |
| unscaled layout memo | the cached result of `_tree_layout` WITHOUT the `card_w`/`gap` scaling: slot cx and level per node; the scaling is re-applied per call (O(N)) |
| wide-2000 / wide-6000 | the PERF0B harness shapes: 2000 / 6000 nodes, one parent each, root linked to every first-layer node (`.dev-flow/2026-10-10-perf-batch/spike/perf_harness.py`) |
| parity goldens | the AT-065 byte-pinned painted-line captures at 118 and 87 columns (`tests/test_mod_parity.py`, goldens + sha256) |
| golden census | `tests/test_repair_golden_census.py` — renderer output pins derived from `test_repair_depth.py` (3 renderers × 4 sizes, 12 pins) |

### 1.4 References

- `.dev-flow/BACKLOG.md` B-33 / S-15 / S-18 / S-19; B-111 (shared seams); B-115 / B-116 / B-117 (carried).
- `.dev-flow/2026-10-10-perf-batch/spike/perf-baseline.md` §1–§7 (the measurements every threshold cites); `evidence/perf0c-*.transcript` (PERF0C profiles), `evidence/perf0b-run.transcript` (user-reachable timings).
- `docs/ARCHITECTURE.md` §2–§4 (module map, dependency rules, frozen interfaces F1–F5); PDR `design/design-proposal.md` (this batch's design, cited as `PDR-2026-10-10-perf-batch#D<n>`).
- `mapper/canvas.py:107-128` (`wire`, `elbow_down`), `mapper/views/layered.py:192-258` (`_tree_layout`), `mapper/model.py:169-179` (`add_edge`, `children_of`, `parent_of`), `mapper/mermaid.py:131-159` (`dump`), `mapper/screens/map/painting.py:301-377` (`refresh_canvas`, `_declare_after_layout`), `mapper/screens/map/screen.py:201-241` (`on_mount`).
- `tests/test_repair_perf_shape.py` docstring (why wall-clock assertions are banned from the suite); `tests/test_mod_parity.py`, `tests/test_repair_golden_census.py` (the behaviour oracle); `tests/test_draft_save.py` (E-1 helpers the ATs import).

### 1.5 Document overview

§2 overall description (product perspective, source user stories with DoR, premise evaluation, fork
preconditions for the three lanes); §3 high-level requirements; §4 low-level requirements +
Information Flow Contract; §5 validation strategy; §7 the ledger (authored as a separate file,
`01-requirements-ledger.md`).

---

## 2. Overall description

### 2.1 Product perspective

mapper is a Textual 8.2.8 TUI over a `Graph` domain model; renderers turn a graph + `ViewState`
into a `rich.Text` picture; `MapScreen` repaints on every navigation key; `MapStore` persists maps
as a `.mmd` + `_nodos.yml` pair. The P0 measurement (`spike/perf-baseline.md`) located the cost:
per-keypress repaint is paint-bound (`elbow_down` walking every edge's bus row cell-by-cell through
`wire`), mount pays the same paint three times, and save pays an O(N·E) dump. All three live behind
frozen interfaces (`IRenderer.render`, `Canvas`, `Graph`, F1–F5), which is why the remedies are
internal algorithm changes with byte-identical outputs rather than contract changes.

### 2.2 Product functions

- `Canvas.elbow_down`/`edge` clip spans to the canvas rectangle before iterating (out-of-bounds
  cells were already dropped by `wire`; now the loops skip them).
- `LayeredRenderer` memoises the UNSCALED `_tree_layout` (slot cx, level per node) on the renderer
  instance keyed by strong references (`graph`/`edges`/`nodes` object identity + lengths, `root_id`,
  hidden fold set); a selection-only keypress does not re-layout; `card_w`/`gap` scaling re-applies
  per call, so resize and title edits repaint byte-identically.
- `Graph.children_of`/`parent_of` serve lookups from a private adjacency cache, strong-reference-invalidated;
  `mermaid.dump` emits parentless nodes from one O(N+E) incident-membership pass.
- `MapScreen` mount paints the map once: chrome paints immediately, the canvas render waits for the
  real geometry, and the settle pass remains armed but settles to a no-op.

### 2.3 User characteristics

A single operator role: browses and edits mind maps of hundreds to thousands of nodes through the
TUI. No administrative surface is involved; no new UI ships in this batch.

### 2.4 Constraints

- Byte-identity is the contract: every painted cell stays identical (AT-065 parity goldens + golden
  census + new output-equality tests), and `.mmd` text stays byte-identical (asserted on fixtures).
- No frozen interface changes (ARCHITECTURE §4): `Canvas` signatures, `IRenderer.render`, the
  `Graph` value-object shape, F1–F5 — bodies only; the single §4 `Graph`-row note is a trunk act at
  the join.
- No wall-clock assertions in the suite (`tests/test_repair_perf_shape.py` docstring); thresholds
  are counted-operations oracles; wall-clock is P4 evidence (median of 3, subprocess).
- UI strings English-only; colours from `mapper/darkside.py` tokens; keys from `mapper/keymap.py`;
  no operator path or account name in any file (guard A-110). This batch adds no painted string.
- pytest from the worktree root with `-p no:cacheprovider`; app-driven tests use
  `MapperApp(tmp_path)` + `run_test(size=...)` + `pilot.press` — real keys, no `post_message` or
  `.focus()` shortcuts; helpers imported from `tests/test_draft_save.py`.

### 2.5 Assumptions and dependencies

- The edge-mutation census is complete and stays complete (guarded mechanically by the AST census
  test; premise 4). If a future writer mutates `edges` in place preserving both identity and length,
  the strong-reference check fails to invalidate — the census guard exists to make that a RED test, not a latent bug.
- Renderers are per-screen instances (`screens/map/screen.py:73-75`), so an instance-level layout
  cache cannot leak across screens.
- Premise 3 was REFUTED at round 1 (`mapper/views/layered.py:192-196` — `_tree_layout(graph,
  card_w, gap, hidden)` takes `card_w`, derived from visible titles/meta and `w` at :333-342). The
  memo therefore caches the UNSCALED layout (slot cx, level per node) only; `card_w`/`gap` scaling
  re-applies per call (O(N)) — so resize and title edits repaint byte-identically with zero extra
  memo misses.
- The settle pass's purpose (heal the strip at real geometry, B-56/B60) remains necessary; the
  batch changes its cost, not its existence.
- pytest + Textual `run_test` pilot remain the test substrate (Textual 8.2.8).

### 2.6 Source user stories

| ID | User Story | Source | DoR status |
|----|------------|--------|------------|
| US-PERF-001 | As a mapper operator, I want each navigation keypress on a large map to cost at least 5× less render work than today, so that browsing a thousands-node map stays fluid. | B-33 (PERF0C §7.1: 0.56–1.71 s/keypress at 2000 nodes; 23,983,998 `wire` calls per 2 keys) | READY |
| US-PERF-002 | As a mapper operator, I want saving a large map to cost work proportional to its size, not its size times its edges, so that saves stay fast as maps grow. | B-33 (PERF0C §7.3: save 6.2 s at 6000 nodes, dump O(N·E); ~9.4–10.0 s at 12000) | READY |
| US-PERF-003 | As a mapper operator, I want opening a map to paint it once, not three times, so that open latency is not tripled by redundant paints. | B-33 (PERF0C §7.2: `render` ncalls=3 at mount; PERF0B §6: mount 4.82 s at wide-2000) | READY |

#### Refinement log (one block per story)

**US-PERF-001 — per-keypress render work**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = mapper operator · outcome = a keypress repaints with ≥ 5× fewer `wire` calls and no re-layout on selection-only moves, painting byte-identically · why = PERF0C §7.1 measured the paint phase dominant (elbow_down 4.18 s of 6.18 s profiled per repaint) · out of scope = the S-18 budget, the DAG single-visit layout (⏸ DEFER), incremental/diff repaints (bigger contract change than the measured need).
- **Feasibility (E, S):** implementation path = clip spans in `Canvas.elbow_down`/`edge`; memoise the UNSCALED `_tree_layout` on strong references (scaling re-applied per call), threaded through module-level `_geometry` · dependencies/unknowns = none — both are internal to frozen signatures · fits one batch? = yes.
- **Evaluability (T) — behavioral, black-box:** "When I press `l` then `j` on a 2000-node map, the map repaints and the screen shows the same picture as before the fix, but the app answers in a fraction of the time."
- **Open questions:** none.
- **Classification:** `READY` — counted-operations oracle + byte-equality golden carry the threshold.

**US-PERF-002 — linear save**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = mapper operator · outcome = save performs O(N+E) dump work; the saved `.mmd` is byte-identical · why = PERF0C §7.3 measured the O(N·E) genexpr (18,003,001 iterations) and O(E) `any` scans · out of scope = the yaml sidecar emit (2.5 s, O(document) — format price), load cost.
- **Feasibility (E, S):** implementation path = private adjacency cache on `Graph` (strong-reference-invalidated, order-preserving, fresh-list `children_of`) + one incident-membership pass in `dump`; consumers (`import_csv` orphan pass, `store._reindex`, minimap) ride it through unchanged signatures · fits one batch? = yes.
- **Evaluability (T):** "When I save a 6000-node map, the file lands as fast as writing it takes, byte-identical to what the old code wrote."
- **Classification:** `READY`.

**US-PERF-003 — one paint at mount**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = mapper operator · outcome = mount pays exactly one render; the strip still reports hidden rows correctly at the settled geometry · why = PERF0C §7.2 measured `render` ×3 (guessed-geometry paint + settle + strip-reflow repaint) · out of scope = deleting the settle pass (reintroduces B-56/B60).
- **Feasibility (E, S):** implementation path = keep `refresh_canvas`'s declaration order; skip only the canvas render while the region is unassigned (`canvas.size.width == 0`); first real render through the guarded/reclamp path; **GATED on spike PERFS** — else the lane leaves to B-118 · dependencies/unknowns = the spike proves ncalls = 1 with every existing mount test green · fits one batch? = yes.
- **Evaluability (T):** "When I open a 2000-node map, the first paint appears once the layout settles — and the pagination strip is right, not stale."
- **Classification:** `READY`.

### 2.7 Premise evaluation (C-43) — MANDATORY, one row per premise

| # | Premise, as a truth-apt proposition | Tier | Verdict | Executed evidence (command output / `file:line` — **NOT** a citation of another document) | Disposition |
|---|---|---|---|---|---|
| 1 | The baselines every threshold cites are recorded: 23,983,998 `wire` calls per 2 keypresses and `render` ×2 on wide-2000 nav; `render` ×3 and 35,975,997 `wire` calls at mount; 18,003,001 genexpr iterations + 6002 O(E) scans in save at wide-6000. | measurement | ✅ TRUE | `.dev-flow/2026-10-10-perf-batch/spike/perf-baseline.md` §7.1/§7.2/§7.3, raw rows in `evidence/perf0c-nav.transcript`, `perf0c-mount.transcript`, `perf0c-store.transcript` | relied on; thresholds indexed to these numbers |
| 2 | `Canvas.wire` bounds-checks every cell and drops out-of-bounds writes, so clipping spans to the rectangle before iterating writes exactly the same cells. | code | ✅ TRUE | `mapper/canvas.py:107-109` — `if not (0 <= x < self.w and 0 <= y < self.h): return`; spans iterated unclipped at `canvas.py:113-128` (`edge`, `elbow_down`) | relied on; the byte-safety basis of Lane R's clip |
| 3 | `LayeredRenderer._tree_layout` is a pure function of graph structure + hidden set: it reads the child index, prunes hidden ids, and walks — no `w`/`h`, no titles. | code | ❌ FALSE as stated (round-1 finding HIGH-A1) → corrected | `mapper/views/layered.py:192-196` — `_tree_layout(graph, card_w, gap, hidden)` takes `card_w`, which derives from visible titles/meta and `w` (`layered.py:333-342`) | corrected: the memo covers the UNSCALED layout (slot cx, level per node) with `card_w`/`gap` scaling re-applied per call — see LLR-PERF.1.2 |
| 4 | The edge-mutation census is complete: the only post-construction writers of `Graph.edges` are `add_edge` (`mapper/model.py:170`, append) and `_remove_subtree` (`mapper/screens/map/editing.py:217-219`, wholesale assignment); no `.append/.extend/.insert/.remove/.pop` exists anywhere else; every construction builds a fresh list. | code | ✅ TRUE | grep + AST census over `mapper/` executed at P1 (agent census, PERFARQ unit): `add_edge` call sites all during build (import_csv.py:90,96,111 · github.py:440,462,605,635 · store.py:929-930 · editing.py:123 · home.py:434); constructions at `mermaid.py:114-120`, `model.py:245-251` (`focus`), store load; undo (`undo.py:60-61`) replaces the whole `Graph` | relied on; the soundness basis of the strong-reference check (`self._adj_src is self.edges and len(self.edges) == n`); pinned mechanically by the AST census guard (LLR-PERF.2.1) |
| 5 | Renderers are per-screen instances, so an instance-level layout cache cannot leak across screens or app runs. | code | ✅ TRUE | `mapper/screens/map/screen.py:73-75` — renderers constructed per `MapScreen.__init__` | relied on |
| 6 | The settle pass exists to heal the strip at real geometry, and deleting it reintroduces a measured defect. | code | ✅ TRUE | `mapper/screens/map/painting.py:366-377` docstring — absent numeral at 50×20/60×20 ("nothing hidden" while half the map off-screen), 31×1 → 29×2 → 31×3 reflow; perf note: unguarded settle costs 0.33 s at 11999 nodes | relied on; Lane S keeps the pass |
| 7 | The next free acceptance-test number is AT-075. | measurement | ✅ TRUE | `grep -rhoE 'AT-0[0-9]{2}' REQUIREMENTS.md tests/*.py | sort -u | tail` → `AT-072`, `AT-073`, `AT-074` (max 074; AT-074 in `tests/test_csv_safety_preview.py`) | AT-075 … AT-077b assigned |

- **Premise evaluation:** 7 premise(s) · ✅ TRUE — all verified against code or executed evidence; none undecidable.

### 2.8 Fork preconditions (C-52) — MANDATORY, and the declared empty when the batch does not fork

| # | Condition (`C-52`) | Discharged? | The executed evidence |
|---|---|---|---|
| 1 | **Frozen contract** — no shared interface is touched inside a lane; one that must change returns to the trunk (trigger A3) | ✅ | PDR §4 freezes per lane: Lane R touches only bodies (`Canvas` signatures + `IRenderer.render` + `MAX_RENDER_NODES` value untouched); Lane M adds a private `_`-prefixed `compare=False` cache field (frozen `Graph` shape unchanged; the single §4 row note is a trunk act at the join); Lane S edits `on_mount`/`refresh_canvas` bodies only — F1 (no new attribute: the unassigned-region signal reads `canvas.size.width == 0`), F2 names/signatures, F3 `BINDINGS`/constants, F5 surface untouched. Shared seams banned to all lanes: `BINDINGS` on `screens/map/screen.py`, the `mapper/app.py` re-export block/`__all__`, `mapper/keymap.py`, `mapper/darkside.py`, ARCHITECTURE itself (B-111) |
| 2 | **Disjoint FILE sets**, not just modules — two lanes may not edit the same file, not even different regions | ✅ | Lane R = {`mapper/canvas.py`, `mapper/views/layered.py`, `tests/test_perf_paint_clip.py`, `tests/test_perf_layout_memo.py`}; Lane M = {`mapper/model.py`, `mapper/mermaid.py`, `tests/test_perf_adjacency.py`, `tests/test_perf_dump.py`}; Lane S = {`mapper/screens/map/painting.py`, `mapper/screens/map/screen.py`, `tests/test_perf_mount.py`}. Executed intersection test at P1: `R∩M = ∅ · R∩S = ∅ · M∩S = ∅` |
| 3 | **Crossed reverse census** — family B run per lane and **shared before starting**; the trunk's act, impossible from inside a lane | ✅ | Executed at P1: 23 test files assert renderer/`children_of`/`parent_of` symbols; 19 assert the mount/paint path. Load-bearing: `tests/test_mod_parity.py` (painted text — all lanes), `tests/test_repair_golden_census.py` (renderer output, Lane R), store round-trip + CSV suites (Lane M's dump/`children_of` order), B-56/B60 mount tests + AT-065 (Lane S). No lane's file set is edited by another lane's symbols |
| 4 | **One owner of the trunk** — requirements, traceability, backlog and spec are never written from a lane | ✅ | requirements/PDR/PLAN/ARCHITECTURE note/increment packets are written only by the orchestrator (this document, unit PERFARQ); lanes receive them read-only |

- **Fork preconditions:** 3 lane(s) · all four conditions discharged as declared above; the batch is the first to fork on the modular split (A4).

---

## 3. High-level requirements (HLR)

### HLR-PERF.1 — a keypress repaints with ≥ 5× less render work, byte-identically
- **Traceability:** US-PERF-001
- **Ledger:** LED-2026-10-10-perf-batch.1, LED-2026-10-10-perf-batch.2
- **Statement:** When the operator presses a navigation key on a mounted map, the system shall repaint the canvas with at least 5× fewer `Canvas.wire` calls than the measured baseline for the same shape (23,983,998 calls for two keypresses on wide-2000), shall not recompute the unscaled layered tree layout when only the selection moved, and shall paint byte-identically to the pre-change renderer for every graph the loader admits.
- **Rationale (informative):** PERF0C §7.1 measured the paint phase dominant (`elbow_down` walks every edge's bus row cell-by-cell; 4.18 s of 6.18 s profiled per repaint) and §7.1/§2 measured the layout recomputed on every repaint. Clipping skips exactly the out-of-bounds iterations `wire` would have dropped (premise 2); the memo skips the unscaled layout only when the strong-reference key is unchanged (premise 3 corrected — the key excludes every geometry input, so `card_w`/`gap` scaling re-applies per call).
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_perf_paint_clip.py::test_at_075_keypress_wire_budget tests/test_perf_paint_clip.py::test_wire_count_budget tests/test_perf_paint_clip.py::test_bare_canvas_clip_equality tests/test_perf_paint_clip.py::test_render_grid_clip_identity tests/test_perf_layout_memo.py::test_at_075b_memo_misses_and_golden tests/test_perf_layout_memo.py::test_memo_miss_spy` (nodes created in Inc-R1/Inc-R2); gate: `tests/test_mod_parity.py` + `tests/test_repair_golden_census.py` stay green.
- **Numeric pass threshold:** exit code 0; the two-keypress scripted sequence at wide-2000 (118×34) performs ≤ 1,200,000 `wire` calls (tightened from 4,800,000 — ≈ 1/20 of the measured 23,983,998 — so a one-axis-only clip, which re-walks the dominant bus-row spans, fails the cap); the memo-miss spy reads exactly 1 miss across five selection-only keypresses; 0 byte differences on the fixture grid and the parity goldens.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** pressing `l`/`j` on a 2000-node map repaints instantly-in-comparison and the picture is exactly the same; folding/unfolding, resizing and editing still repaint correctly.
  - **Shipped surface:** `MapScreen` navigation (`mapper/keymap.py` map scope) → `refresh_canvas` → `LayeredRenderer.render` → `Canvas`.
  - **Acceptance test(s):** AT-075, AT-075b
  - **Boundary catalog (QC-3):** ☑ empty — an empty map (root `None`) and a single-node map render identical text with clip + memo active ☑ boundary — deep chain 5000, wide 6000, forest (≥ 2 parentless nodes), a multi-parent DAG built directly (rendered byte-identically, never saved) ☑ invalid — none applies (no input surface changes) ☑ error — the renderer failure path ("could not draw the map") still paints.
  - **Negative control:** M-R1a (remove the span clip) → AT-075 RED (wire count back to ~24 M); M-R2 (drop the memo) → AT-075b RED (a miss per keypress); M-R1b (clip bound clamped to `min(xb, w-1)` — drops one in-bounds cell) → byte-identity grid RED.

---

### HLR-PERF.2 — save performs O(N+E) dump work, byte-identically
- **Traceability:** US-PERF-002
- **Ledger:** LED-2026-10-10-perf-batch.1, LED-2026-10-10-perf-batch.2
- **Statement:** When a map is saved, the system shall perform dump work proportional to N+E (one incident-membership pass replacing the per-node edge rescan), shall serve `Graph.children_of`/`parent_of` lookups from a cache invalidated on every edge mutation, and shall write `.mmd` text byte-identical to the pre-change dumper.
- **Rationale (informative):** PERF0C §7.3 measured the O(N·E) dump (18,003,001 genexpr iterations ≈ N²/2 and 6002 O(E) `any` scans at N=6000; `parent_of` 6000 × O(E) adding 0.49 s). The consumers of the O(E)-per-call lookups — the minimap (`painting.py:472,519`), navigation, search, editing, `import_csv`'s orphan pass (`import_csv.py:110`), `store._reindex` (`store.py:994`) — all ride the cache through unchanged signatures; the renderers keep their own per-render index (≤ 0.37 ms, PERF0 §1) and are pinned as unchanged by LLR-PERF.2.3.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_perf_adjacency.py::test_cache_mutation_script_equality tests/test_perf_adjacency.py::test_cache_counted_ops tests/test_perf_adjacency.py::test_edges_writer_census tests/test_perf_adjacency.py::test_census_in_place_forms tests/test_perf_dump.py::test_at_076_real_save_dump_budget tests/test_perf_dump.py::test_dump_counted_ops_scaling_ratio tests/test_perf_dump.py::test_dump_fixture_goldens` (nodes created in Inc-M1/Inc-M2); existing store/CSV suites re-run at the join.
- **Numeric pass threshold:** exit code 0; ONE `mermaid.dump` call on wide-6000 iterates `graph.edges` ≤ 2·E + c times (c a small constant; vs the 18,003,001 + 6002·E baseline); the scaling ratio count(2N)/count(N) ∈ [1.8, 2.2]; 100 mixed cached lookups after warm-up scan edges ≤ 1 full pass; `.mmd` bytes equal the pinned goldens on every fixture (0 diffs).
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** saving a large map is as fast as writing the bytes; the saved file opens and diffs identically to a pre-change save.
  - **Shipped surface:** `MapScreen` edit-then-persist gesture (a ficha edit persisting via `_save_or_toast`, `screens/map/editing.py` → `MapStore.save` → `mermaid.dump`).
  - **Acceptance test(s):** AT-076
  - **Boundary catalog (QC-3):** ☑ empty — an empty graph dumps `graph TD\n` exactly as today; single node ☑ boundary — forest (≥ 2 parentless nodes; orphan emission order preserved), deep chain 5000, wide 6000, a multi-parent DAG built directly (dumped byte-identically; the store still refuses to save it per the csv-safety batch), a graph with a DANGLING edge (incident counting covers it) ☑ invalid — none applies ☑ error — none applies.
  - **Negative control:** M-M2a (restore the per-node `any()` scan) → AT-076 RED (iteration count); M-M1a (bypass the cache) → counted-ops node RED; M-M1b (drop the `is`-check — `len`-only key — + same-length wholesale replacement) → equality node RED (stale results); M-M2b (emission order change) → fixture bytes RED.

---

### HLR-PERF.3 — mount paints once, identically
- **Traceability:** US-PERF-003
- **Ledger:** LED-2026-10-10-perf-batch.1, LED-2026-10-10-perf-batch.2
- **Statement:** When a map screen mounts, the system shall perform exactly one paid canvas render before the first settled paint (baseline 3) by skipping only the canvas render while the canvas region is unassigned (`canvas.size.width == 0`) — `refresh_canvas`'s declaration order stays byte-for-byte — and routing the first real render through the normal guarded/reclamp path; it shall still paint all chrome (rail, minimap, inspector, crumb) on the first pass, and shall preserve the settle pass so the pagination strip reports hidden rows at the real settled geometry. **GATED:** this requirement activates only if spike unit PERFS proves render ncalls = 1 at mount with every existing mount test green; if the spike fails, Lane S leaves the batch to backlog **B-118** and HLR-PERF.3 / LLR-PERF.3.1–3.2 / AT-077 / AT-077b are withdrawn.
- **Rationale (informative):** PERF0C §7.2 measured three renders: a guessed-geometry paint before the compositor assigns the canvas region, a settle pass at the real region, and a re-armed pass because the strip's row count moves the region after `canvas.update` (`painting.py:686-706`). The round-1 mechanism (declare the strip's row budget before `canvas.update` + defer on `_declared_for is None`) was withdrawn — contradicted by the code (round-1 finding B4: `_declared_for is None` is set on every `refresh_canvas`, `painting.py:701`; the reordering breaks the strip-heal ordering, measured 6 failing tests at `painting.py:668-673`; the deferred render would run in the settle pass, which swallows exceptions at `:351-357` and skips `_reclamp_pan`). The replacement candidate skips only the canvas render at zero width and is gated on the spike; the B-56/B60 heal (premise 6) is kept, not deleted.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_perf_mount.py::test_at_077_mount_render_once tests/test_perf_mount.py::test_at_077b_strip_numeral tests/test_perf_mount.py::test_chrome_paints_at_mount` (nodes created in Inc-S1, only if the gate passes); gate: `tests/test_mod_parity.py` (its scripted session opens a map) stays green.
- **Numeric pass threshold:** exit code 0; mounting wide-2000 at 118×34 calls the current renderer's `render` exactly once between `push_screen` and the settled first paint (vs 3); the painted canvas + strip equal the pinned golden — captured on base SHA `5cde04e`, sha256-recorded (0 diffs); at 87×34 and 60×20 the strip reports the correct hidden-row numeral after mount.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** opening a 2000-node map shows the first paint after one render's worth of waiting (not three), and the pagination strip is immediately correct.
  - **Shipped surface:** `MapperApp` → `push_screen(MapScreen)` → `on_mount`/`refresh_canvas`/`_declare_after_layout`.
  - **Acceptance test(s):** AT-077, AT-077b
  - **Boundary catalog (QC-3):** ☑ empty — mounting the 1-node error graph (a refused map) still paints the error screen ☑ boundary — 87×34 and 60×20 reflow geometries, single-node map, wide-2000 ☑ invalid — none applies ☑ error — the load-error path paints as today.
  - **Negative control:** M-S1 (restore the eager canvas render while the region is unassigned) → AT-077 RED (render ncalls=2); M-S2 (neuter the settle pass) → AT-077b RED (absent numeral returns); M-S3 (deferral skips chrome painting) → chrome arm RED.

---

## 4. Low-level requirements (LLR)

> Each LLR decomposes an HLR into a verifiable property at the implementation level.
> Same regime: EARS syntax owed in `full`, recommended in `core`. ID format: `LLR-<HLR>.<M>`.

### LLR-PERF.1.1 — spans are clipped to the canvas rectangle before iterating
- **Traceability:** HLR-PERF.1
- **Ledger:** LED-2026-10-10-perf-batch.1, LED-2026-10-10-perf-batch.2
- **Statement:** The `Canvas.elbow_down` and `Canvas.edge` span loops (`mapper/canvas.py:113-128`) shall compute the intersection of each span with the canvas rectangle (`0 <= x < self.w`, `0 <= y < self.h`) before iterating, so no loop visits a cell `wire` would drop — every written cell stays exactly the set `wire` writes today, at O(painted) instead of O(span) iterations.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_perf_paint_clip.py::test_wire_count_budget tests/test_perf_paint_clip.py::test_bare_canvas_clip_equality` (nodes created in Inc-R1). The unit oracle is bare-`Canvas` equality: the clipped methods write exactly the cells the pre-change loops wrote, the reference loops being copies kept INSIDE the test file — never a `Canvas` flag.
- **Numeric pass threshold:** the two-keypress scripted sequence (`l`, `j`) on wide-2000 at 118×34 performs ≤ 1,200,000 `wire` calls total (≈ 1/20 of the measured baseline 23,983,998 — tightened from 4,800,000 so a one-axis-only clip, which re-walks the dominant bus-row spans, fails the cap; the exact clipped count is recorded at execution in `04-validation.md`); the clipped render's bytes equal the unclipped reference render on the full fixture grid and on every bare-`Canvas` shape — 0 differences.
- **Negative control:** M-R1a (remove the clip) → wire count back to ~24 M → RED. M-R1b (clip upper bound clamped to `min(xb, w-1)` — drops one in-bounds cell) → byte-grid and bare-`Canvas` equality RED.
- **Boundary catalog:** ☑ empty — empty/single-node maps render identical text ☑ boundary — deep chain 5000 (spans exceed the canvas height), wide 6000 (bus rows exceed the width), forest, a multi-parent DAG built directly, spans starting/ending out of bounds on both sides, a panned ViewState and a folded subtree in the render grid; bare-`Canvas` shapes: `x1 < x0` (degenerate span), spans fully off-canvas, `ybus` above and below the canvas, negative pan origin ☑ error — none applies.

### LLR-PERF.1.2 — the UNSCALED `_tree_layout` is memoised on strong references
- **Traceability:** HLR-PERF.1
- **Ledger:** LED-2026-10-10-perf-batch.1, LED-2026-10-10-perf-batch.2
- **Statement:** `LayeredRenderer` shall cache the UNSCALED layout result of `_tree_layout` — the slot cx and level per node, with `card_w`/`gap` scaling NOT applied — keyed by strong references compared with `is`: the `Graph` object, its `edges` list (+ `len`), its `nodes` dict (+ `len`), `graph.root_id`, and the hidden (fold) set; a hit re-applies the `card_w`/`gap` scaling in O(N) per call. Because the key holds strong references, object-identity reuse (`id()` recycling after garbage collection) can never fake a hit. The memo lives in module-level `_geometry` (`mapper/views/layered.py:306`), so it threads through every render path unchanged.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_perf_layout_memo.py::test_memo_miss_spy tests/test_perf_layout_memo.py::test_memo_invalidation_arms` (nodes created in Inc-R2) — the spy counts memo MISSES at the named hit-check point inside `_geometry` (`_tree_layout` itself runs ~10× per two renders, `evidence/perf0c-nav.transcript:44`, so invocations are not countable). Arms, each a named product mutation: `resize` (window resize → 0 extra misses, repaint byte-identical), `title` (ficha title edit that widens `widest` → 0 extra misses, repaint byte-identical — scaling re-applies), `fold` (fold/unfold → +1 miss), `focus` (focus toggle → miss), `undo` (undo builds a NEW `Graph` → miss — the identity-reuse arm), `add_child` (a child added via real keys → +1 miss), `round_trip` (outline ↔ radial ↔ layered switch → byte-identical paint).
- **Numeric pass threshold:** five selection-only keypresses (`l,j,j,j,j`) on wide-2000 at 118×34 cost exactly 1 memo miss; the `fold` and `add_child` arms each add exactly 1; painted output after every arm byte-equals the pinned golden — 0 diffs.
- **Negative control:** M-R2 (drop the memo) → 1 miss per keypress → RED. M-R2b (never invalidate — fixed key) → post-edit painted diff RED (stale layout).
- **Boundary catalog:** ☑ empty — a single-node map memoises trivially and repaints identically ☑ boundary — fold/unfold, resize, a title-only ficha edit that widens `widest` (0 misses, byte-identical repaint), focus toggle, undo (new `Graph`), add-child via real keys, an outline↔radial↔layered round trip, wide 6000, deep chain 5000 ☑ error — a graph swap always misses (a new `Graph` object is never `is` the cached one); a same-length wholesale `edges` replacement with no lookup in between still misses — identity, not length, carries validity.

### LLR-PERF.1.3 — paint stays byte-identical (the behaviour oracle)
- **Traceability:** HLR-PERF.1
- **Ledger:** LED-2026-10-10-perf-batch.1, LED-2026-10-10-perf-batch.2
- **Statement:** After Lane R lands, every pinned painted-output oracle shall remain green unchanged: the AT-065 parity goldens (118 and 87 columns, sha256-pinned), the `test_repair_golden_census.py` pins (3 renderers × 4 sizes), and the new fixture grid (empty map, single node, deep chain 5000, wide 6000, forest, multi-parent DAG built directly) rendered with clipping active equals the reference render with clipping disabled — 0 cell differences.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_parity.py tests/test_repair_golden_census.py tests/test_perf_paint_clip.py::test_render_grid_clip_identity` (the last node created in Inc-R1). The reference render is produced by copies of the pre-change `elbow_down`/`edge` span loops kept inside the test file — never a `Canvas` flag.
- **Numeric pass threshold:** exit code 0; 0 golden-line diffs; 0 census-pin failures; 0 fixture-grid cell diffs.
- **Negative control:** M-R1b (clip upper bound clamped to `min(xb, w-1)` — drops an in-bounds cell) → fixture grid RED; any paint-affecting drift in `views/layered.py` or `canvas.py` → parity/census RED.
- **Boundary catalog:** ☑ empty ☑ boundary — the full grid: empty map, single node, deep chain 5000, wide 6000, forest, multi-parent DAG built directly, spans starting/ending out of bounds on both sides, a panned ViewState and a folded subtree ☑ invalid (the multi-parent DAG — rendered identically though never loadable) ☑ error — rides HLR-PERF.1's failure-path arm.

### LLR-PERF.2.1 — `Graph` serves adjacency lookups from a strong-reference private cache
- **Traceability:** HLR-PERF.2
- **Ledger:** LED-2026-10-10-perf-batch.1, LED-2026-10-10-perf-batch.2
- **Statement:** `Graph.children_of` and `Graph.parent_of` (`mapper/model.py:172-179`) shall serve results from a private adjacency cache (`_`-prefixed fields, `compare=False, repr=False`) whose validity is a strong-reference check: a hit requires `self._adj_src is self.edges and len(self.edges) == n` — so `id()` recycling after garbage collection can never fake a hit. `children_of` returns a FRESH list per call (callers may bind and mutate it, `painting.py:519`). Semantics stay exactly today's: child ids in edge-list order; `parent_of` returns the FIRST matching parent or `None` — so every consumer (minimap, navigation, search, editing, coverage, factory, lane view, `import_csv`'s orphan pass, `store._reindex`) is faster through unchanged signatures.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_perf_adjacency.py::test_cache_mutation_script_equality tests/test_perf_adjacency.py::test_cache_counted_ops` (nodes created in Inc-M1) — the mutation script builds wide-6000, warms the cache, then runs TWO wholesale `edges` replacements back to back with NO lookup in between (the old list is freed and its `id()` may be reused by the new list — identity, not `id`, must carry validity), plus `add_edge` and a `focus()` subgraph; cached results equal the linear-scan reference at every step, order- and first-match-exact; a caller that binds the returned list and mutates it gets fresh-list semantics.
- **Numeric pass threshold:** 0 equality mismatches across the mutation script (incl. the two-replacement no-lookup stretch); total edge visits in the counted-ops arm ≤ `len(edges)` (baseline uncached: 100 × `len(edges)`).
- **Negative control:** M-M1a (bypass the cache) → counted-ops RED. M-M1b (drop the `is`-check — `len`-only key — then a same-length wholesale replacement) → equality RED (stale). M-M1c (any new `edges` writer site) → the census guard RED.
- **Boundary catalog:** ☑ empty — empty graph: lookups return `[]`/`None` exactly as today ☑ boundary — single node, deep chain 5000, wide 6000, forest, multi-parent DAG (a child of two parents returns the FIRST parent), lookups after each mutation class, a caller that binds the returned list and mutates it ☑ invalid — none applies ☑ error — none applies.
  Plus the census guard: an AST-derived test over `mapper/` asserts the edge-mutation census — the set of post-construction writers of `.edges` ⊆ {`model.py` `add_edge` (append), `screens/map/editing.py` `_remove_subtree` (wholesale assignment)} — and flags every in-place form (`edges[i] =`, slice assignment, `del`, `+=`, `*=`, `.sort`, `.reverse`, `.clear`, `.extend`, `.insert`, `.remove`, `.pop`) plus aliases (`x = <expr>.edges` with `x` then mutated); the guard carries one mutation per form (`tests/test_perf_adjacency.py::test_census_in_place_forms[setitem|slice|del|iadd|imul|sort|reverse|clear|extend|insert|remove|pop|alias]`). M-M1c reddens it — this is the cache-invalidation tripwire named as the batch's main risk in the PDR §6.

### LLR-PERF.2.2 — `mermaid.dump` emits parentless nodes in one linear pass
- **Traceability:** HLR-PERF.2
- **Ledger:** LED-2026-10-10-perf-batch.1, LED-2026-10-10-perf-batch.2
- **Statement:** `mermaid.dump` (`mapper/mermaid.py:152-158`) shall determine orphan (parentless AND childless) nodes by membership in one incident-id set built in a single O(N+E) pass over EVERY edge — including dangling edges (an edge whose endpoint is missing from `nodes`, which `dump` skips when writing but whose incident ids still count) — replacing the per-node `any(e.parent_id == node.id or e.child_id == node.id for e in graph.edges)` rescan, while preserving emission order (node-dict iteration order), the `emitted` dedup set semantics, label escaping, and the trailing newline byte-for-byte.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_perf_dump.py::test_dump_counted_ops_scaling_ratio tests/test_perf_dump.py::test_dump_fixture_goldens` (nodes created in Inc-M2) — the counted-ops arm counts `graph.edges` iterations inside ONE `mermaid.dump` call on wide-N and wide-2N; the fixture arm pins `dump` bytes for `fixtures/legacy.mmd`, `fixtures/anidado.mmd`, `fixtures/truncado.mmd`, wide-6000, forest, empty and single-node graphs, and a graph with a dangling edge.
- **Numeric pass threshold:** ONE `mermaid.dump` call on wide-6000 iterates `graph.edges` ≤ 2·E + c times (c a small constant; baseline: 18,003,001 genexpr visits + 6002 O(E) scans); the scaling ratio count(2N)/count(N) ∈ [1.8, 2.2] (linear — a correct fix doubles, never quadruples); 0 byte differences on every fixture golden.
- **Negative control:** M-M2a (restore the per-node `any()` scan) → counted arm RED. M-M2b (reorder the orphan loop or touch dedup/escaping) → fixture bytes RED.
- **Boundary catalog:** ☑ empty — empty graph dumps exactly `graph TD\n` ☑ boundary — single node (pure orphan), forest (multiple orphans, order pinned), deep chain 5000 (no orphans), wide 6000, duplicate-edge dedup unchanged, a graph with a DANGLING edge (incident counting covers it; the edge is not written but its endpoints count toward membership) ☑ invalid — none applies ☑ error — none applies.

### LLR-PERF.2.3 — the renderers keep their own adjacency build (A3 boundary pinned)
- **Traceability:** HLR-PERF.2
- **Ledger:** LED-2026-10-10-perf-batch.1, LED-2026-10-10-perf-batch.2
- **Statement:** No renderer shall consume the model cache this batch, and Lane M shall not move the cache's cost into `views`: `mapper/views/*.py` shall keep building their per-render `_child_index` (measured ≤ 0.37 ms/pass, PERF0 §1) and shall import NO new cache name from `mapper/model.py` — the model cache stays private to `model` (`_`-prefixed, absent from any module's public imports) — so Lane M's A3 surface is exactly the unchanged `children_of`/`parent_of` semantics and nothing else.
- **Validation:** `inspection`
- **Executed verification:** `git diff 5cde04e -- mapper/views` on the Lane M branch — empty (file-diff check, executed at the Inc-M1/Inc-M2 gates and the DDR); plus `grep -rn "_child_index" mapper/views/` (present, per-render).
- **Numeric pass threshold:** the Lane M branch changes zero bytes under `mapper/views/`; 0 new cross-module imports of cache names.
- **Negative control:** M-M3 (any Lane M edit under `mapper/views/`, e.g. wiring a renderer to the model cache) → the file-diff check non-empty → RED (and the fork's disjointness/A3 ruling violated — returns the increment to the trunk).
- **Boundary catalog:** none — an internal boundary pin; the reason no input class applies is that no behaviour changes.

### LLR-PERF.3.1 — mount performs exactly one paid canvas render
- **Traceability:** HLR-PERF.3
- **Ledger:** LED-2026-10-10-perf-batch.1, LED-2026-10-10-perf-batch.2
- **Statement:** `MapScreen.on_mount` (`screens/map/screen.py:201-241`) shall not trigger a canvas render while the canvas region is unassigned (`canvas.size.width == 0`), painting all chrome (rail, minimap, inspector, crumb) as today; `refresh_canvas`'s declaration order stays byte-for-byte (the round-1 strip-first reordering is withdrawn — finding B4); the first paid render happens at the real geometry through the normal guarded path (pan re-clamped via `_reclamp_pan`, `_rendered_for` set), and the `_declare_after_layout` settle pass remains armed — its settled render is a no-op by the `_rendered_for` guard, not by deletion. No new `MapScreen` attribute is added (F1 census unchanged). **GATED** like HLR-PERF.3: active only if spike unit PERFS proves render ncalls = 1 at mount with every existing mount test green; else Lane S leaves to backlog **B-118** and this requirement is withdrawn.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_perf_mount.py::test_at_077_mount_render_once tests/test_perf_mount.py::test_chrome_paints_at_mount` (nodes created in Inc-S1, only if the gate passes) — mount wide-2000 at 118×34 with a counting wrapper on the current renderer's `render`; poll until the first settled paint plus one tick; assert rail/minimap/inspector/crumb content on the first pass.
- **Numeric pass threshold:** `render` called exactly once between `push_screen` and the settled first paint (baseline 3, PERF0C §7.2); chrome assertions 0 diffs; canvas + strip bytes equal the pinned golden.
- **Negative control:** M-S1 (restore the eager pre-layout render) → render ncalls=2 → RED. M-S3 (deferral also skips chrome) → chrome arm RED.
- **Boundary catalog:** ☑ empty — mounting the 1-node error graph (refused map) still paints the error screen on the same path ☑ boundary — 87×34, 60×20, single-node map, wide-2000, a map opened right after a resize ☑ invalid — none applies ☑ error — the load-error path paints as today.

### LLR-PERF.3.2 — the settle pass still heals the strip at real geometry
- **Traceability:** HLR-PERF.3
- **Ledger:** LED-2026-10-10-perf-batch.1, LED-2026-10-10-perf-batch.2
- **Statement:** The `_declare_after_layout` settle pass shall remain armed from `refresh_canvas` and shall still re-declare the canvas and the pagination strip whenever the region differs from `_declared_for` — preserving the B-56/B60 heal (the strip reports hidden rows at the real settled geometry; the 31×1 → 29×2 → 31×3 reflow converges) — with its settled render a no-op by the `_rendered_for` guard, not by deletion.
- **Validation:** `test (e2e)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_perf_mount.py::test_at_077b_strip_numeral` (node created in Inc-S1; gated like LLR-PERF.3.1 — only if spike PERFS passes) — mount at 87×34 and at 60×20, assert the strip's hidden-row numeral at the settled geometry matches the pinned golden text.
- **Numeric pass threshold:** 0 diffs on the strip text at both geometries; the pass is still armed (a synthetic region change still triggers a re-declare — exercised by the 60×20 reflow fixture).
- **Negative control:** M-S2 (neuter the settle pass) → the absent numeral returns → RED.
- **Boundary catalog:** ☑ boundary — 87×34 and 60×20 are the load-bearing reflow cases; the rest rides LLR-PERF.3.1.

### Information Flow Contract (IFC) — C-54

> Part A in every batch; Part B when the system's boundary has components a consumer can address independently. The block syntax, its fields and the rules that read them are in `templates/ifc-template.md`, which ships with the flow and is not copied into this batch.

- **Part A — flows:**

```text
FLOW keypress-to-paint
SOURCE: the operator's navigation keypress (mapper/keymap.py map scope)
NODES:
  - MapScreen.refresh_canvas (mapper/screens/map/painting.py) — owner: existing surface
  - LayeredRenderer._tree_layout memo (mapper/views/layered.py) — owner: LLR-PERF.1.2
  - Canvas.elbow_down/edge span loops (mapper/canvas.py) — owner: LLR-PERF.1.1
SINK: the painted canvas (byte-identical per LLR-PERF.1.3; parity goldens pin it)
```

```text
FLOW graph-to-adjacency
SOURCE: Graph.edges (mapper/model.py) — the only writers: add_edge (:170), _remove_subtree (editing.py:217-219)
NODES:
  - Graph private adjacency cache — owner: LLR-PERF.2.1 (validity: _adj_src is self.edges and len(self.edges) == n)
  - mermaid.dump orphan pass (mapper/mermaid.py) — owner: LLR-PERF.2.2
  - consumers through unchanged signatures: import_csv orphan pass (:110) · store._reindex (:994) ·
    painting.py:472,519 · navigation · searching · editing · coverage · factory · lane view
SINK: O(1) lookups (was O(E) per call) and byte-identical .mmd text
```

```text
FLOW mount-to-first-paint
SOURCE: MapperApp push_screen(MapScreen)
NODES:
  - MapScreen.on_mount (mapper/screens/map/screen.py) — owner: LLR-PERF.3.1 (refresh_canvas runs;
    canvas render skipped while the region is unassigned — canvas.size.width == 0; chrome paints;
    no new F1 attribute)
  - refresh_canvas declaration order unchanged (mapper/screens/map/painting.py) — owner: LLR-PERF.3.1
    (the round-1 strip-first reordering is withdrawn — finding B4)
  - _declare_after_layout settle pass (mapper/screens/map/painting.py) — owner: LLR-PERF.3.2 (kept;
    first real render through the guarded/reclamp path; settled render is a _rendered_for no-op)
SINK: the settled first paint: one paid render, correct strip numeral (B-56/B60 heal preserved)
```

- **Part B — boundary decomposition:** no — no component of the boundary is addressable on its own; the flows are exercised end to end by the ATs through the shipped app.

---

## 5. Validation strategy

### 5.1 Methods

> **Two layers** (per the Two-layer validation rule). Every batch declares BOTH:
> - **Layer A — white-box / functional (`TC-NNN`):** validates the HLR/LLR mechanism (the HOW). Methods: `test`, `inspection`, `analysis`.
> - **Layer B — black-box / behavioral acceptance (`AT-NNN`):** validates the user story's outcome through the shipped surface (the WHAT). Method: `acceptance`.

Layer A — unit/integration tests in `tests/test_perf_paint_clip.py` (TC: wire-count oracle,
bare-`Canvas` clip equality against in-test reference copies of the old span loops, byte-identity
grid with a panned ViewState and a fold), `tests/test_perf_layout_memo.py` (TC: memo-miss spy at the
named hit-check point + seven named invalidation arms), `tests/test_perf_adjacency.py` (TC:
mutation-script equality incl. the two-replacement no-lookup stretch, counted-ops, widened AST census
guard with one mutation per in-place form, optional LOW-10 minimap/outline byte test over a forest
and a multi-parent DAG), `tests/test_perf_dump.py` (TC: per-dump counted-ops + scaling ratio,
fixture byte-goldens incl. a dangling-edge fixture), `tests/test_perf_mount.py` (TC: chrome arm —
gated), plus the file-diff inspection for LLR-PERF.2.3. **Every verification names exact node ids
(`file::test`) — no `-k` substring selectors** (round-1 finding MED-2: `-k at077` also selects
at077b; `-k identity`/`cache`/`counted` match other files).

Layer B — acceptance tests through the real app (`MapperApp(tmp_path)` + `run_test(size=...)` +
`pilot.press`, real keys; helpers imported from `tests/test_draft_save.py`; generated wide/deep
fixture maps built by the test into a tmp workspace):

- **AT-075** (US-PERF-001 / HLR-PERF.1, LLR-PERF.1.1): `tests/test_perf_paint_clip.py::test_at_075_keypress_wire_budget` —
  open a generated wide-2000 tree map at 118×34; press `l` then `j`; a counting wrapper on `Canvas.wire`
  (counter RESET after mount so mount paints are not charged to the keypress budget) asserts
  ≤ 1,200,000 calls for the two keypresses (≥ 5× below — ≈ 1/20 of — the measured baseline 23,983,998;
  tightened from 4,800,000 so a one-axis-only clip fails; the exact clipped count is recorded at
  execution in `04-validation.md`); the settled painted lines equal the golden pinned at base SHA
  `5cde04e` with sha256 (the AT-065 precedent). Negative control M-R1a (clip removed) → RED; M-R1b → byte-golden RED.
- **AT-075b** (US-PERF-001 / LLR-PERF.1.2): `tests/test_perf_layout_memo.py::test_at_075b_memo_misses_and_golden` —
  same map; press `l,j,j,j,j`; the memo-miss spy at the named hit-check point inside `_geometry`
  reads exactly 1 miss (`_tree_layout` itself runs ~10× per two renders, `evidence/perf0c-nav.transcript:44`,
  so invocations are not countable); each repaint byte-equal the golden; then archive a subtree with
  real keys, press a key: exactly 1 more miss. Negative control M-R2 → RED; M-R2b → post-edit diff RED.
- **AT-076** (US-PERF-002 / HLR-PERF.2, LLR-PERF.2.2): `tests/test_perf_dump.py::test_at_076_real_save_dump_budget` —
  open a generated wide-6000 map and SAVE THROUGH A REAL PERSISTING GESTURE (a ficha edit that
  persists via `_save_or_toast`, `screens/map/editing.py` — NOT bare `ctrl+s` with no draft, which
  saves nothing, `drafts.py:131-132`); a counting wrapper on `graph.edges` bounds ONE
  `mermaid.dump` call to ≤ 2·E + c iterations (the scaling ratio count(2N)/count(N) ∈ [1.8, 2.2] is
  pinned by the unit node); the saved `.mmd` bytes equal the golden pinned at base SHA `5cde04e`.
  Negative control M-M2a → RED; M-M2b → fixture bytes RED. Wall-clock recorded at P4 as evidence
  (baseline save 6.2 s profiled / ~9.4–10.0 s wall at 12000), never asserted.
- **AT-077** (US-PERF-003 / HLR-PERF.3, LLR-PERF.3.1): `tests/test_perf_mount.py::test_at_077_mount_render_once` —
  **GATED on spike PERFS**; mount the wide-2000 map at 118×34; the renderer's `render` is called
  exactly once until the settled first paint (baseline 3); rail, minimap, inspector, crumb painted
  on the first pass; canvas + strip byte-equal the golden. Negative control M-S1 → RED (ncalls=2);
  M-S3 → chrome RED.
- **AT-077b** (US-PERF-003 / LLR-PERF.3.2): `tests/test_perf_mount.py::test_at_077b_strip_numeral` —
  **GATED on spike PERFS**; mount at 87×34 and 60×20; the strip reports the correct hidden-row
  numeral at the settled geometry (the B-56/B60 scenario). Negative control M-S2 → RED.

### 5.2 Batch acceptance criteria
- 100% of LLRs (PERF.1.1 … PERF.3.2) covered by at least one executed test with pass result, each
  with an executed negative control (M-R1a/b, M-R2/b, M-M1a/b/c, M-M2a/b, M-M3, M-S1/2/3) recorded
  as a transcript.
- AT-075, AT-075b, AT-076, AT-077, AT-077b pass through `MapperApp` + `run_test` with real keys;
  every AT owns a node distinct from its LLR nodes.
- The behaviour oracle stays green untouched: `tests/test_mod_parity.py` (AT-065 goldens) and
  `tests/test_repair_golden_census.py` — byte-identical, not re-baselined.
- No requirement without an assigned validation method; no wall-clock assertion in the suite; no
  painted string carrying an operator path or account name (guard A-110 stays green); no lane edits a
  frozen seam (file-set check at the DDR).
- Boundary evidence: empty map, single node, deep chain 5000, wide 6000, forest (≥ 2 parentless
  nodes), multi-parent DAG built directly (render/dump/cache only, never saved), edge mutations after
  the cache is warm (`add_edge` and wholesale replacement), a title-only ficha edit, fold/unfold,
  87×34 and 60×20 reflow geometries, the 1-node error graph at mount — each named by a fixture in
  the four new test files.
- Golden provenance: every new golden (AT-075, AT-075b, AT-076, AT-077/077b — painted lines,
  canvas+strip, `.mmd` bytes) is captured on the BASE SHA `5cde04e` (pre-remedy) at the trunk BEFORE
  the lanes fork, and recorded with base SHA + sha256 per golden (the AT-065 precedent); the wire
  counter resets after mount so mount paints are not charged to the keypress budget.
- P4 evidence: wall-clock before/after for keypress, mount and save against the §6/§7 baselines —
  base and head measured on the SAME machine and session, interleaved runs, median of 3,
  subprocess (`spike/perf_harness.py` / `perf0c_profile.py`); the raw runs are pasted into
  `04-validation.md` — evidence, not gate.

---

## 6. Appendices (optional)

### 6.1 Extended glossary
**Mutation ids** (the negative-control changes of §4/§5 — one id, one meaning):

| Id | Mutation | Reddens |
|----|----------|---------|
| M-R1a | Remove the span clip in `Canvas.elbow_down`/`edge` | AT-075 (`wire` count back to ~24 M) |
| M-R1b | Clamp the clip upper bound to `min(xb, w-1)` — drops one in-bounds cell (the round-1 `<= self.w` form was an EQUIVALENT mutant, finding MED-A4) | byte-identity grid (LLR-PERF.1.3), `tests/test_perf_paint_clip.py::test_bare_canvas_clip_equality`, AT-075 golden |
| M-R2 | Drop the unscaled-layout memo | AT-075b (a memo miss per keypress) |
| M-R2b | Never invalidate the layout cache (fixed key) | AT-075b post-edit arm + `test_memo_invalidation_arms[fold|add_child]` (stale layout diff) |
| M-M1a | Bypass the adjacency cache in `children_of`/`parent_of` | `tests/test_perf_adjacency.py::test_cache_counted_ops` |
| M-M1b | Drop the `is`-check (key on `len(edges)` only); wholesale-replace with a same-length list | `tests/test_perf_adjacency.py::test_cache_mutation_script_equality` (stale results) |
| M-M1c | Add any new `Graph.edges` writer site, or one in-place form per guard row (`edges[i]=`, slice, `del`, `+=`, `*=`, `.sort`, `.reverse`, `.clear`, `.extend`, `.insert`, `.remove`, `.pop`, alias) | `tests/test_perf_adjacency.py::test_edges_writer_census` + `test_census_in_place_forms[...]` |
| M-M2a | Restore the per-node `any()` orphan scan in `mermaid.dump` | AT-076 + `test_dump_counted_ops_scaling_ratio` (count RED, ratio ≈ 4) |
| M-M2b | Reorder the orphan loop / touch dedup or escaping in `dump` | AT-076 / `tests/test_perf_dump.py::test_dump_fixture_goldens` byte-goldens |
| M-M3 | Any Lane M edit under `mapper/views/` (e.g. wiring a renderer to the model cache) | LLR-PERF.2.3 file-diff check: `git diff 5cde04e -- mapper/views` non-empty (A3 — returns the increment to the trunk) |
| M-S1 | Restore the eager canvas render while the region is unassigned | AT-077 (render ncalls=2) |
| M-S2 | Neuter the `_declare_after_layout` settle pass | AT-077b (absent numeral returns) |
| M-S3 | Make the mount skip swallow chrome painting too | `tests/test_perf_mount.py::test_chrome_paints_at_mount` |

### 6.2 Relevant design decisions
The per-lane decisions, the deferred items (S-18 budget; single-visit DAG layout — ⏸ DEFER with
PERF0 §2 evidence for the prototype round) and the rejected alternatives are recorded in
`design/design-proposal.md` §1/§6 (PDR-2026-10-10-perf-batch) and mirrored in the HLR rationales.

### 6.3 Open risks
Cache invalidation is the main risk: the strong-reference tokens (`is` + `len`, for both the
adjacency cache and the layout memo) are sound only while the edge-mutation census holds — guarded
mechanically (M-M1c, one mutation per in-place form) plus the mutation-script equality arm with the
two-replacement no-lookup stretch (the `id()`-reuse case). Lane R byte-identity rests on premise 2
(`wire` drops out-of-bounds cells) and the CORRECTED premise 3 (the memo covers the UNSCALED layout;
scaling re-applies per call) — both pinned by executed tests, not by the premises' word. Lane S is
gated: if spike PERFS cannot prove render ncalls = 1 at mount with every existing mount test green,
Lane S leaves the batch to backlog B-118 and HLR-PERF.3 is withdrawn with it. Out-of-scope carries: S-18 work budget, B-33 dense-DAG
beyond these remedies (72.5 s p73-class shapes reachable only via CSV preview), B-115/B-116/B-117.

### 6.4 Phase-1 reconciliation log — moved to the ledger (§7)

### 6.5 Requirement amendments — moved to the ledger (§7)

---

## 7. The ledger — authored as a SEPARATE FILE

The fence below is the ledger's seed: `devflow-init.py` writes it to `01-requirements-ledger.md`. The shape of an entry is in the field guide.

```markdown
# Requirements ledger — mapper — Batch 2026-10-10-perf-batch

> Append-only. Entries are added in chronological order and never rewritten. The live
> contract is `01-requirements.md`; this file records how it came to say what it says.
> Every entry names the requirement it amends; every requirement names its entries. `V26`
> compares the two sets of pairs both ways.

_No entries yet. The first amendment to the live contract writes the first one, in the
shape the field guide's §7 shows (`req-template.part2.md` in the guide directory init prints), and nothing
above this line is ever edited._
```
