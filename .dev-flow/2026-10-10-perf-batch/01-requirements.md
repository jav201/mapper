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
`LayeredRenderer._tree_layout` per graph revision — byte-identical paint; (Lane M) a private cached
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
| revision token | the cache-validity key `(id(graph.edges), len(graph.edges))` — an edge append changes the length, a wholesale list replacement changes the identity, so any edge mutation invalidates automatically |
| edge-mutation census | the exhaustive list of post-construction writers of `Graph.edges`: `mapper/model.py:170` (`add_edge`, append) and `mapper/screens/map/editing.py:217-219` (`_remove_subtree`, wholesale assignment) — and no other site |
| paid render | a renderer `render` call that paints new canvas content; a settle pass whose region is already current is not paid (the `_rendered_for` guard skips it) |
| counted-operations oracle | a deterministic test oracle that counts calls/iterations (e.g. `Canvas.wire` calls, `graph.edges` iterations, `_tree_layout` invocations) — never wall-clock |
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
- `LayeredRenderer` memoises `_tree_layout` per revision token + hidden set on the renderer
  instance; a selection-only keypress does not re-layout; an edge mutation does.
- `Graph.children_of`/`parent_of` serve lookups from a private adjacency cache, token-invalidated;
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
  the token fails to invalidate — the census guard exists to make that a RED test, not a latent bug.
- Renderers are per-screen instances (`screens/map/screen.py:73-75`), so an instance-level layout
  cache cannot leak across screens.
- `_tree_layout` is a pure function of graph structure + hidden set (no `w`/`h`, no titles) —
  verified as premise 3; if it ever gains a geometry input, the memo key must be amended in the
  same increment.
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
- **Feasibility (E, S):** implementation path = clip spans in `Canvas.elbow_down`/`edge`; memoise `_tree_layout` per revision token on the renderer instance · dependencies/unknowns = none — both are internal to frozen signatures · fits one batch? = yes.
- **Evaluability (T) — behavioral, black-box:** "When I press `l` then `j` on a 2000-node map, the map repaints and the screen shows the same picture as before the fix, but the app answers in a fraction of the time."
- **Open questions:** none.
- **Classification:** `READY` — counted-operations oracle + byte-equality golden carry the threshold.

**US-PERF-002 — linear save**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = mapper operator · outcome = save performs O(N+E) dump work; the saved `.mmd` is byte-identical · why = PERF0C §7.3 measured the O(N·E) genexpr (18,003,001 iterations) and O(E) `any` scans · out of scope = the yaml sidecar emit (2.5 s, O(document) — format price), load cost.
- **Feasibility (E, S):** implementation path = private adjacency cache on `Graph` (token-invalidated, order-preserving) + one incident-membership pass in `dump`; consumers (`import_csv` orphan pass, `store._reindex`, minimap) ride it through unchanged signatures · fits one batch? = yes.
- **Evaluability (T):** "When I save a 6000-node map, the file lands as fast as writing it takes, byte-identical to what the old code wrote."
- **Classification:** `READY`.

**US-PERF-003 — one paint at mount**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = mapper operator · outcome = mount pays exactly one render; the strip still reports hidden rows correctly at the settled geometry · why = PERF0C §7.2 measured `render` ×3 (guessed-geometry paint + settle + strip-reflow repaint) · out of scope = deleting the settle pass (reintroduces B-56/B60).
- **Feasibility (E, S):** implementation path = defer the canvas render on the never-declared mount path (`_declared_for is None`); declare the strip's row budget before `canvas.update` so the settled region is stable; no new F1 attribute · fits one batch? = yes.
- **Evaluability (T):** "When I open a 2000-node map, the first paint appears once the layout settles — and the pagination strip is right, not stale."
- **Classification:** `READY`.

### 2.7 Premise evaluation (C-43) — MANDATORY, one row per premise

| # | Premise, as a truth-apt proposition | Tier | Verdict | Executed evidence (command output / `file:line` — **NOT** a citation of another document) | Disposition |
|---|---|---|---|---|---|
| 1 | The baselines every threshold cites are recorded: 23,983,998 `wire` calls per 2 keypresses and `render` ×2 on wide-2000 nav; `render` ×3 and 35,975,997 `wire` calls at mount; 18,003,001 genexpr iterations + 6002 O(E) scans in save at wide-6000. | measurement | ✅ TRUE | `.dev-flow/2026-10-10-perf-batch/spike/perf-baseline.md` §7.1/§7.2/§7.3, raw rows in `evidence/perf0c-nav.transcript`, `perf0c-mount.transcript`, `perf0c-store.transcript` | relied on; thresholds indexed to these numbers |
| 2 | `Canvas.wire` bounds-checks every cell and drops out-of-bounds writes, so clipping spans to the rectangle before iterating writes exactly the same cells. | code | ✅ TRUE | `mapper/canvas.py:107-109` — `if not (0 <= x < self.w and 0 <= y < self.h): return`; spans iterated unclipped at `canvas.py:113-128` (`edge`, `elbow_down`) | relied on; the byte-safety basis of Lane R's clip |
| 3 | `LayeredRenderer._tree_layout` is a pure function of graph structure + hidden set: it reads the child index, prunes hidden ids, and walks — no `w`/`h`, no titles. | code | ✅ TRUE | `mapper/views/layered.py:192-258` (read via the explore census; `_geometry` at :306-370 holds the title/width scans, `_tree_layout` does not) | relied on; the soundness of the memo key `(id(graph), len(edges), len(nodes), root_id, frozenset(hidden))` |
| 4 | The edge-mutation census is complete: the only post-construction writers of `Graph.edges` are `add_edge` (`mapper/model.py:170`, append) and `_remove_subtree` (`mapper/screens/map/editing.py:217-219`, wholesale assignment); no `.append/.extend/.insert/.remove/.pop` exists anywhere else; every construction builds a fresh list. | code | ✅ TRUE | grep + AST census over `mapper/` executed at P1 (agent census, PERFARQ unit): `add_edge` call sites all during build (import_csv.py:90,96,111 · github.py:440,462,605,635 · store.py:929-930 · editing.py:123 · home.py:434); constructions at `mermaid.py:114-120`, `model.py:245-251` (`focus`), store load; undo (`undo.py:60-61`) replaces the whole `Graph` | relied on; the soundness basis of the `(id, len)` token; pinned mechanically by the AST census guard (LLR-PERF.2.1) |
| 5 | Renderers are per-screen instances, so an instance-level layout cache cannot leak across screens or app runs. | code | ✅ TRUE | `mapper/screens/map/screen.py:73-75` — renderers constructed per `MapScreen.__init__` | relied on |
| 6 | The settle pass exists to heal the strip at real geometry, and deleting it reintroduces a measured defect. | code | ✅ TRUE | `mapper/screens/map/painting.py:366-377` docstring — absent numeral at 50×20/60×20 ("nothing hidden" while half the map off-screen), 31×1 → 29×2 → 31×3 reflow; perf note: unguarded settle costs 0.33 s at 11999 nodes | relied on; Lane S keeps the pass |
| 7 | The next free acceptance-test number is AT-075. | measurement | ✅ TRUE | `grep -rhoE 'AT-0[0-9]{2}' REQUIREMENTS.md tests/*.py | sort -u | tail` → `AT-072`, `AT-073`, `AT-074` (max 074; AT-074 in `tests/test_csv_safety_preview.py`) | AT-075 … AT-077b assigned |

- **Premise evaluation:** 7 premise(s) · ✅ TRUE — all verified against code or executed evidence; none undecidable.

### 2.8 Fork preconditions (C-52) — MANDATORY, and the declared empty when the batch does not fork

| # | Condition (`C-52`) | Discharged? | The executed evidence |
|---|---|---|---|
| 1 | **Frozen contract** — no shared interface is touched inside a lane; one that must change returns to the trunk (trigger A3) | ✅ | PDR §4 freezes per lane: Lane R touches only bodies (`Canvas` signatures + `IRenderer.render` + `MAX_RENDER_NODES` value untouched); Lane M adds a private `_`-prefixed `compare=False` cache field (frozen `Graph` shape unchanged; the single §4 row note is a trunk act at the join); Lane S edits `on_mount`/`refresh_canvas` bodies only — F1 (no new attribute: `_declared_for is None` is the signal), F2 names/signatures, F3 `BINDINGS`/constants, F5 surface untouched. Shared seams banned to all lanes: `BINDINGS` on `screens/map/screen.py`, the `mapper/app.py` re-export block/`__all__`, `mapper/keymap.py`, `mapper/darkside.py`, ARCHITECTURE itself (B-111) |
| 2 | **Disjoint FILE sets**, not just modules — two lanes may not edit the same file, not even different regions | ✅ | Lane R = {`mapper/canvas.py`, `mapper/views/layered.py`, `tests/test_perf_paint_clip.py`, `tests/test_perf_layout_memo.py`}; Lane M = {`mapper/model.py`, `mapper/mermaid.py`, `tests/test_perf_adjacency.py`, `tests/test_perf_dump.py`}; Lane S = {`mapper/screens/map/painting.py`, `mapper/screens/map/screen.py`, `tests/test_perf_mount.py`}. Executed intersection test at P1: `R∩M = ∅ · R∩S = ∅ · M∩S = ∅` |
| 3 | **Crossed reverse census** — family B run per lane and **shared before starting**; the trunk's act, impossible from inside a lane | ✅ | Executed at P1: 23 test files assert renderer/`children_of`/`parent_of` symbols; 19 assert the mount/paint path. Load-bearing: `tests/test_mod_parity.py` (painted text — all lanes), `tests/test_repair_golden_census.py` (renderer output, Lane R), store round-trip + CSV suites (Lane M's dump/`children_of` order), B-56/B60 mount tests + AT-065 (Lane S). No lane's file set is edited by another lane's symbols |
| 4 | **One owner of the trunk** — requirements, traceability, backlog and spec are never written from a lane | ✅ | requirements/PDR/PLAN/ARCHITECTURE note/increment packets are written only by the orchestrator (this document, unit PERFARQ); lanes receive them read-only |

- **Fork preconditions:** 3 lane(s) · all four conditions discharged as declared above; the batch is the first to fork on the modular split (A4).

---

## 3. High-level requirements (HLR)

### HLR-PERF.1 — a keypress repaints with ≥ 5× less render work, byte-identically
- **Traceability:** US-PERF-001
- **Ledger:** LED-2026-10-10-perf-batch.1
- **Statement:** When the operator presses a navigation key on a mounted map, the system shall repaint the canvas with at least 5× fewer `Canvas.wire` calls than the measured baseline for the same shape (23,983,998 calls for two keypresses on wide-2000), shall not recompute the layered tree layout when only the selection moved, and shall paint byte-identically to the pre-change renderer for every graph the loader admits.
- **Rationale (informative):** PERF0C §7.1 measured the paint phase dominant (`elbow_down` walks every edge's bus row cell-by-cell; 4.18 s of 6.18 s profiled per repaint) and §7.1/§2 measured the layout recomputed on every repaint. Clipping skips exactly the out-of-bounds iterations `wire` would have dropped (premise 2); the memo skips layout only when the revision token and hidden set are unchanged (premise 3).
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_perf_paint_clip.py` and `tests/test_perf_layout_memo.py` (nodes to be created: AT-075, AT-075b, the byte-identity grid); gate: `tests/test_mod_parity.py` + `tests/test_repair_golden_census.py` stay green.
- **Numeric pass threshold:** exit code 0; the two-keypress scripted sequence at wide-2000 (118×34) performs ≤ 4,800,000 `wire` calls (≥ 5× below 23,983,998); `_tree_layout` executes exactly once across five selection-only keypresses; 0 byte differences on the fixture grid and the parity goldens.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** pressing `l`/`j` on a 2000-node map repaints instantly-in-comparison and the picture is exactly the same; folding/unfolding, resizing and editing still repaint correctly.
  - **Shipped surface:** `MapScreen` navigation (`mapper/keymap.py` map scope) → `refresh_canvas` → `LayeredRenderer.render` → `Canvas`.
  - **Acceptance test(s):** AT-075, AT-075b
  - **Boundary catalog (QC-3):** ☑ empty — an empty map (root `None`) and a single-node map render identical text with clip + memo active ☑ boundary — deep chain 5000, wide 6000, forest (≥ 2 parentless nodes), a multi-parent DAG built directly (rendered byte-identically, never saved) ☑ invalid — none applies (no input surface changes) ☑ error — the renderer failure path ("could not draw the map") still paints.
  - **Negative control:** M-R1a (remove the span clip) → AT-075 RED (wire count back to ~24 M); M-R2 (drop the memo) → AT-075b RED (layout recomputed per key); M-R1b (off-by-one clip) → byte-identity grid RED.

---

### HLR-PERF.2 — save performs O(N+E) dump work, byte-identically
- **Traceability:** US-PERF-002
- **Ledger:** LED-2026-10-10-perf-batch.1
- **Statement:** When a map is saved, the system shall perform dump work proportional to N+E (one incident-membership pass replacing the per-node edge rescan), shall serve `Graph.children_of`/`parent_of` lookups from a cache invalidated on every edge mutation, and shall write `.mmd` text byte-identical to the pre-change dumper.
- **Rationale (informative):** PERF0C §7.3 measured the O(N·E) dump (18,003,001 genexpr iterations ≈ N²/2 and 6002 O(E) `any` scans at N=6000; `parent_of` 6000 × O(E) adding 0.49 s). The consumers of the O(E)-per-call lookups — the minimap (`painting.py:472,519`), navigation, search, editing, `import_csv`'s orphan pass (`import_csv.py:110`), `store._reindex` (`store.py:994`) — all ride the cache through unchanged signatures; the renderers keep their own per-render index (≤ 0.37 ms, PERF0 §1) and are pinned as unchanged by LLR-PERF.2.3.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_perf_adjacency.py tests/test_perf_dump.py` (nodes to be created: the cache equality/counted-ops/census nodes, the dump fixture nodes, AT-076); existing store/CSV suites re-run at the join.
- **Numeric pass threshold:** exit code 0; saving wide-6000 iterates `graph.edges` ≤ 3·(N+E) times in total (vs 18,003,001 + 6002·E baseline); 100 mixed cached lookups after warm-up scan edges ≤ 1 full pass; `.mmd` bytes equal the pinned goldens on every fixture (0 diffs).
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** saving a large map is as fast as writing the bytes; the saved file opens and diffs identically to a pre-change save.
  - **Shipped surface:** `MapScreen` save (`ctrl+s` → `_save_or_toast` → `MapStore.save` → `mermaid.dump`).
  - **Acceptance test(s):** AT-076
  - **Boundary catalog (QC-3):** ☑ empty — an empty graph dumps `graph TD\n` exactly as today; single node ☑ boundary — forest (≥ 2 parentless nodes; orphan emission order preserved), deep chain 5000, wide 6000, a multi-parent DAG built directly (dumped byte-identically; the store still refuses to save it per the csv-safety batch) ☑ invalid — none applies ☑ error — none applies.
  - **Negative control:** M-M2a (restore the per-node `any()` scan) → AT-076 RED (iteration count); M-M1a (bypass the cache) → counted-ops node RED; M-M1b (len-only cache key + same-length wholesale replacement) → equality node RED (stale results); M-M2b (emission order change) → fixture bytes RED.

---

### HLR-PERF.3 — mount paints once, identically
- **Traceability:** US-PERF-003
- **Ledger:** LED-2026-10-10-perf-batch.1
- **Statement:** When a map screen mounts, the system shall perform exactly one paid canvas render before the first settled paint (baseline 3), shall still paint all chrome (rail, minimap, inspector, crumb) on the first pass, and shall preserve the settle pass so the pagination strip reports hidden rows at the real settled geometry.
- **Rationale (informative):** PERF0C §7.2 measured three renders: a guessed-geometry paint before the compositor assigns the canvas region, a settle pass at the real region, and a re-armed pass because the strip's row count moves the region after `canvas.update` (`painting.py:686-706`). The design defers the canvas render on the never-declared mount path and declares the strip's row budget (content-derived) before `canvas.update`, making the settled region stable — one paid render, same painted result, and the B-56/B60 heal (premise 6) is kept, not deleted.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_perf_mount.py` (nodes to be created: AT-077, AT-077b, the chrome arm); gate: `tests/test_mod_parity.py` (its scripted session opens a map) stays green.
- **Numeric pass threshold:** exit code 0; mounting wide-2000 at 118×34 calls the current renderer's `render` exactly once between `push_screen` and the settled first paint (vs 3); the painted canvas + strip equal the pinned golden (0 diffs); at 87×34 and 60×20 the strip reports the correct hidden-row numeral after mount.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** opening a 2000-node map shows the first paint after one render's worth of waiting (not three), and the pagination strip is immediately correct.
  - **Shipped surface:** `MapperApp` → `push_screen(MapScreen)` → `on_mount`/`refresh_canvas`/`_declare_after_layout`.
  - **Acceptance test(s):** AT-077, AT-077b
  - **Boundary catalog (QC-3):** ☑ empty — mounting the 1-node error graph (a refused map) still paints the error screen ☑ boundary — 87×34 and 60×20 reflow geometries, single-node map, wide-2000 ☑ invalid — none applies ☑ error — the load-error path paints as today.
  - **Negative control:** M-S1 (restore the eager pre-layout canvas render) → AT-077 RED (render ncalls=2); M-S2 (neuter the settle pass) → AT-077b RED (absent numeral returns); M-S3 (deferral skips chrome painting) → chrome arm RED.

---

## 4. Low-level requirements (LLR)

> Each LLR decomposes an HLR into a verifiable property at the implementation level.
> Same regime: EARS syntax owed in `full`, recommended in `core`. ID format: `LLR-<HLR>.<M>`.

### LLR-PERF.1.1 — spans are clipped to the canvas rectangle before iterating
- **Traceability:** HLR-PERF.1
- **Ledger:** LED-2026-10-10-perf-batch.1
- **Statement:** The `Canvas.elbow_down` and `Canvas.edge` span loops (`mapper/canvas.py:113-128`) shall compute the intersection of each span with the canvas rectangle (`0 <= x < self.w`, `0 <= y < self.h`) before iterating, so no loop visits a cell `wire` would drop — every written cell stays exactly the set `wire` writes today, at O(painted) instead of O(span) iterations.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_perf_paint_clip.py -k wire_count` (node to be created, Inc-R1).
- **Numeric pass threshold:** the two-keypress scripted sequence (`l`, `j`) on wide-2000 at 118×34 performs ≤ 4,800,000 `wire` calls total (≥ 5× below the measured baseline 23,983,998); the clipped render's bytes equal the unclipped reference render on the full fixture grid — 0 differences.
- **Negative control:** M-R1a (remove the clip) → wire count back to ~24 M → RED. M-R1b (off-by-one bound) → byte-grid RED.
- **Boundary catalog:** ☑ empty — empty/single-node maps render identical text ☑ boundary — deep chain 5000 (spans exceed the canvas height), wide 6000 (bus rows exceed the width), forest, a multi-parent DAG built directly, spans starting/ending out of bounds on both sides ☑ error — none applies.

### LLR-PERF.1.2 — `_tree_layout` is memoised per graph revision and hidden set
- **Traceability:** HLR-PERF.1
- **Ledger:** LED-2026-10-10-perf-batch.1
- **Statement:** `LayeredRenderer` shall cache `_tree_layout` results on the renderer instance keyed `(id(graph), len(graph.edges), len(graph.nodes), graph.root_id, frozenset(hidden_ids))`, recomputing only when the key changes — so a selection-only keypress reuses the layout (identical output, since the function is pure in exactly these inputs, premise 3) and an edge or node mutation, a root change, or a fold change recomputes.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_perf_layout_memo.py -k layout_once` (node to be created, Inc-R2) — five selection-only keypresses (`l,j,j,j,j`) on wide-2000 with a spy on the layout entry point.
- **Numeric pass threshold:** `_tree_layout` executes exactly once across the five-keypress sequence; after an edge mutation through real keys (archive a subtree) plus one keypress it has executed once more; painted output after every key byte-equals the pinned golden — 0 diffs.
- **Negative control:** M-R2 (drop the memo) → layout executed 5× → RED. M-R2b (never invalidate) → post-edit painted diff RED (stale layout).
- **Boundary catalog:** ☑ empty — a single-node map memoises trivially and repaints identically ☑ boundary — fold/unfold (hidden set changes → recompute), title-only ficha edit (key unchanged → repaint byte-identical), wide 6000, deep chain 5000 ☑ error — a graph swap (new `id`) always misses the cache.

### LLR-PERF.1.3 — paint stays byte-identical (the behaviour oracle)
- **Traceability:** HLR-PERF.1
- **Ledger:** LED-2026-10-10-perf-batch.1
- **Statement:** After Lane R lands, every pinned painted-output oracle shall remain green unchanged: the AT-065 parity goldens (118 and 87 columns, sha256-pinned), the `test_repair_golden_census.py` pins (3 renderers × 4 sizes), and the new fixture grid (empty map, single node, deep chain 5000, wide 6000, forest, multi-parent DAG built directly) rendered with clipping active equals the reference render with clipping disabled — 0 cell differences.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_parity.py tests/test_repair_golden_census.py tests/test_perf_paint_clip.py -k identity` (the last node created in Inc-R1).
- **Numeric pass threshold:** exit code 0; 0 golden-line diffs; 0 census-pin failures; 0 fixture-grid cell diffs.
- **Negative control:** M-R1b (off-by-one clip dropping or adding an in-bounds cell) → fixture grid RED; any paint-affecting drift in `views/layered.py` or `canvas.py` → parity/census RED.
- **Boundary catalog:** ☑ empty ☑ boundary ☑ invalid (the multi-parent DAG — rendered identically though never loadable) — the full grid; error class rides HLR-PERF.1's failure-path arm.

### LLR-PERF.2.1 — `Graph` serves adjacency lookups from a token-invalidated private cache
- **Traceability:** HLR-PERF.2
- **Ledger:** LED-2026-10-10-perf-batch.1
- **Statement:** `Graph.children_of` and `Graph.parent_of` (`mapper/model.py:172-179`) shall return results from a private adjacency cache (`_`-prefixed fields, `compare=False, repr=False`) that is rebuilt when the validity token `(id(self.edges), len(self.edges))` changes — preserving today's exact semantics: `children_of` returns child ids in edge-list order; `parent_of` returns the FIRST matching parent or `None` — so every consumer (minimap, navigation, search, editing, coverage, factory, lane view, `import_csv`'s orphan pass, `store._reindex`) is faster through unchanged signatures.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_perf_adjacency.py -k cache` (nodes to be created, Inc-M1): the mutation-script equality arm (build wide-6000 → warm → `add_edge` → wholesale `edges` replacement simulating the archive path → `focus()` subgraph; cached results equal the linear-scan reference at every step, order- and first-match-exact) and the counted-ops arm (a counting wrapper on `graph.edges`; 100 mixed lookups after warm-up visit ≤ 1 full scan in total).
- **Numeric pass threshold:** 0 equality mismatches across the mutation script; total edge visits in the counted-ops arm ≤ `len(edges)` (baseline uncached: 100 × `len(edges)`).
- **Negative control:** M-M1a (bypass the cache) → counted-ops RED. M-M1b (key on `len` only; wholesale-replace with a same-length list) → equality RED (stale). M-M1c (any new `edges` writer site) → the census guard below RED.
- **Boundary catalog:** ☑ empty — empty graph: lookups return `[]`/`None` exactly as today ☑ boundary — single node, deep chain 5000, wide 6000, forest, multi-parent DAG (a child of two parents returns the FIRST parent), lookups after each mutation class ☑ invalid — none applies ☑ error — none applies.
  Plus the census guard: an AST-derived test asserts the edge-mutation census (writers of `.edges` ⊆ {`model.py:170` append, `editing.py:217-219` assignment}); M-M1c reddens it — this is the cache-invalidation tripwire named as the batch's main risk in the PDR §6.

### LLR-PERF.2.2 — `mermaid.dump` emits parentless nodes in one linear pass
- **Traceability:** HLR-PERF.2
- **Ledger:** LED-2026-10-10-perf-batch.1
- **Statement:** `mermaid.dump` (`mapper/mermaid.py:152-158`) shall determine orphan (parentless AND childless) nodes by membership in one incident-id set built in a single O(N+E) pass — replacing the per-node `any(e.parent_id == node.id or e.child_id == node.id for e in graph.edges)` rescan — while preserving emission order (node-dict iteration order), the `emitted` dedup set semantics, label escaping, and the trailing newline byte-for-byte.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_perf_dump.py -k counted` and `-k fixtures` (nodes to be created, Inc-M2) — the counted-ops arm runs through the real save path (`MapStore.save` on wide-6000, counting wrapper on `graph.edges`) and the fixture arm pins `dump` bytes for `fixtures/legacy.mmd`, `fixtures/anidado.mmd`, `fixtures/truncado.mmd`, wide-6000, forest, empty and single-node graphs.
- **Numeric pass threshold:** total `graph.edges` iterations during save ≤ 3·(N+E) (baseline: 18,003,001 genexpr visits + 6002 O(E) scans at N=6000); 0 byte differences on every fixture golden.
- **Negative control:** M-M2a (restore the per-node `any()` scan) → counted arm RED. M-M2b (reorder the orphan loop or touch dedup/escaping) → fixture bytes RED.
- **Boundary catalog:** ☑ empty — empty graph dumps exactly `graph TD\n` ☑ boundary — single node (pure orphan), forest (multiple orphans, order pinned), deep chain 5000 (no orphans), wide 6000, duplicate-edge dedup unchanged ☑ invalid — none applies ☑ error — none applies.

### LLR-PERF.2.3 — the renderers keep their own adjacency build (A3 boundary pinned)
- **Traceability:** HLR-PERF.2
- **Ledger:** LED-2026-10-10-perf-batch.1
- **Statement:** No renderer shall consume the model cache this batch: `mapper/views/*.py` shall keep building their per-render `_child_index` (measured ≤ 0.37 ms/pass, PERF0 §1), and the model cache shall be private to `model` (`_`-prefixed, absent from any module's public imports) — so Lane M's A3 surface is exactly the unchanged `children_of`/`parent_of` semantics and nothing else.
- **Validation:** `inspection`
- **Executed verification:** `grep -rn "_child_index" mapper/views/` (present, per-render) and an AST check that no module imports a public adjacency name from `mapper/model.py` beyond today's set; executed at the Inc-M1/M2 gates.
- **Numeric pass threshold:** 0 new cross-module imports of cache names; 0 renderer files changed by Lane M (file-set check at the DDR).
- **Negative control:** M-M3 (wire a renderer to the model cache) → the import-census check RED (and the fork's disjointness/A3 ruling violated — returns the increment to the trunk).
- **Boundary catalog:** none — an internal boundary pin; the reason no input class applies is that no behaviour changes.

### LLR-PERF.3.1 — mount performs exactly one paid canvas render
- **Traceability:** HLR-PERF.3
- **Ledger:** LED-2026-10-10-perf-batch.1
- **Statement:** `MapScreen.on_mount` (`screens/map/screen.py:201-241`) shall not trigger a canvas render on the never-declared mount path (`_declared_for is None` — the canvas region does not exist yet), painting all chrome (rail, minimap, inspector, crumb) as today; the first paid render happens in `_declare_after_layout` at the real geometry, and `refresh_canvas` shall declare the pagination strip's row budget before `canvas.update` so the settled region is stable — the re-armed settle pass finds `region == _declared_for` and the `_rendered_for` guard performs no second render. No new `MapScreen` attribute is added (F1 census unchanged).
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_perf_mount.py -k at077` and `-k chrome` (nodes to be created, Inc-S1) — mount wide-2000 at 118×34 with a counting wrapper on the current renderer's `render`; poll until the first settled paint plus one tick; assert rail/minimap/inspector/crumb content on the first pass.
- **Numeric pass threshold:** `render` called exactly once between `push_screen` and the settled first paint (baseline 3, PERF0C §7.2); chrome assertions 0 diffs; canvas + strip bytes equal the pinned golden.
- **Negative control:** M-S1 (restore the eager pre-layout render) → render ncalls=2 → RED. M-S3 (deferral also skips chrome) → chrome arm RED.
- **Boundary catalog:** ☑ empty — mounting the 1-node error graph (refused map) still paints the error screen on the same path ☑ boundary — 87×34, 60×20, single-node map, wide-2000, a map opened right after a resize ☑ invalid — none applies ☑ error — the load-error path paints as today.

### LLR-PERF.3.2 — the settle pass still heals the strip at real geometry
- **Traceability:** HLR-PERF.3
- **Ledger:** LED-2026-10-10-perf-batch.1
- **Statement:** The `_declare_after_layout` settle pass shall remain armed from `refresh_canvas` and shall still re-declare the canvas and the pagination strip whenever the region differs from `_declared_for` — preserving the B-56/B60 heal (the strip reports hidden rows at the real settled geometry; the 31×1 → 29×2 → 31×3 reflow converges) — with its settled render a no-op by the `_rendered_for` guard, not by deletion.
- **Validation:** `test (e2e)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_perf_mount.py -k at077b` (node to be created, Inc-S1) — mount at 87×34 and at 60×20, assert the strip's hidden-row numeral at the settled geometry matches the pinned golden text.
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
  - Graph private adjacency cache — owner: LLR-PERF.2.1 (token (id(edges), len(edges)))
  - mermaid.dump orphan pass (mapper/mermaid.py) — owner: LLR-PERF.2.2
  - consumers through unchanged signatures: import_csv orphan pass (:110) · store._reindex (:994) ·
    painting.py:472,519 · navigation · searching · editing · coverage · factory · lane view
SINK: O(1) lookups (was O(E) per call) and byte-identical .mmd text
```

```text
FLOW mount-to-first-paint
SOURCE: MapperApp push_screen(MapScreen)
NODES:
  - MapScreen.on_mount (mapper/screens/map/screen.py) — owner: LLR-PERF.3.1 (defers the canvas render;
    chrome paints; no new F1 attribute)
  - refresh_canvas strip-first declaration (mapper/screens/map/painting.py) — owner: LLR-PERF.3.1
  - _declare_after_layout settle pass (mapper/screens/map/painting.py) — owner: LLR-PERF.3.2 (kept;
    settled render is a _rendered_for no-op)
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
byte-identity grid), `tests/test_perf_layout_memo.py` (TC: layout-once + invalidation arms),
`tests/test_perf_adjacency.py` (TC: mutation-script equality, counted-ops, AST census guard),
`tests/test_perf_dump.py` (TC: counted-ops through the real save, fixture byte-goldens),
`tests/test_perf_mount.py` (TC: chrome arm), plus inspection for LLR-PERF.2.3.

Layer B — acceptance tests through the real app (`MapperApp(tmp_path)` + `run_test(size=...)` +
`pilot.press`, real keys; helpers imported from `tests/test_draft_save.py`; generated wide/deep
fixture maps built by the test into a tmp workspace):

- **AT-075** (US-PERF-001 / HLR-PERF.1, LLR-PERF.1.1): open a generated wide-2000 tree map at
  118×34; press `l` then `j`; a counting wrapper on `Canvas.wire` asserts ≤ 4,800,000 calls for the
  two keypresses (≥ 5× below the measured baseline 23,983,998); the settled painted lines equal the
  pinned golden. Negative control M-R1a (clip removed) → RED; M-R1b → byte-golden RED.
- **AT-075b** (US-PERF-001 / LLR-PERF.1.2): same map; press `l,j,j,j,j`; `_tree_layout` executed
  exactly once; each repaint byte-equal the golden; then archive a subtree with real keys, press a
  key, layout recomputed once more. Negative control M-R2 → RED; M-R2b → post-edit diff RED.
- **AT-076** (US-PERF-002 / HLR-PERF.2, LLR-PERF.2.2): open a generated wide-6000 map; press
  `ctrl+s` through the real save flow with a counting wrapper on `graph.edges`; total edge iterations
  ≤ 3·(N+E) during save; the saved `.mmd` bytes equal the pinned golden. Negative control M-M2a →
  RED; M-M2b → fixture bytes RED. Wall-clock recorded at P4 as evidence (baseline save 6.2 s
  profiled / ~9.4–10.0 s wall at 12000), never asserted.
- **AT-077** (US-PERF-003 / HLR-PERF.3, LLR-PERF.3.1): mount the wide-2000 map at 118×34; the
  renderer's `render` is called exactly once until the settled first paint (baseline 3); rail,
  minimap, inspector, crumb painted on the first pass; canvas + strip byte-equal the golden.
  Negative control M-S1 → RED (ncalls=2); M-S3 → chrome RED.
- **AT-077b** (US-PERF.003 / LLR-PERF.3.2): mount at 87×34 and 60×20; the strip reports the correct
  hidden-row numeral at the settled geometry (the B-56/B60 scenario). Negative control M-S2 → RED.

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
- P4 evidence: wall-clock before/after table (median of 3, subprocess, `spike/perf_harness.py` /
  `perf0c_profile.py`) for keypress, mount and save against the §6/§7 baselines — evidence, not gate.

---

## 6. Appendices (optional)

### 6.1 Extended glossary
**Mutation ids** (the negative-control changes of §4/§5 — one id, one meaning):

| Id | Mutation | Reddens |
|----|----------|---------|
| M-R1a | Remove the span clip in `Canvas.elbow_down`/`edge` | AT-075 (`wire` count back to ~24 M) |
| M-R1b | Off-by-one clip bound (e.g. `<= self.w`) | byte-identity grid (LLR-PERF.1.3), AT-075 golden |
| M-R2 | Drop the `_tree_layout` memo | AT-075b (layout recomputed per key) |
| M-R2b | Never invalidate the layout cache (fixed token) | AT-075b post-edit arm (stale layout diff) |
| M-M1a | Bypass the adjacency cache in `children_of`/`parent_of` | `tests/test_perf_adjacency.py -k cache` counted-ops arm |
| M-M1b | Key the cache on `len(edges)` only; wholesale-replace with a same-length list | `-k cache` equality arm (stale results) |
| M-M1c | Add any new `Graph.edges` writer site | the AST census guard (LLR-PERF.2.1) |
| M-M2a | Restore the per-node `any()` orphan scan in `mermaid.dump` | AT-076 counted arm |
| M-M2b | Reorder the orphan loop / touch dedup or escaping in `dump` | AT-076 / `-k fixtures` byte-goldens |
| M-M3 | Wire a renderer to the model cache | LLR-PERF.2.3 import census (A3 — returns the increment to the trunk) |
| M-S1 | Restore the eager pre-layout canvas render in `on_mount` | AT-077 (render ncalls=2) |
| M-S2 | Neuter the `_declare_after_layout` settle pass | AT-077b (absent numeral returns) |
| M-S3 | Make the mount deferral skip chrome painting too | `tests/test_perf_mount.py -k chrome` |

### 6.2 Relevant design decisions
The per-lane decisions, the deferred items (S-18 budget; single-visit DAG layout — ⏸ DEFER with
PERF0 §2 evidence for the prototype round) and the rejected alternatives are recorded in
`design/design-proposal.md` §1/§6 (PDR-2026-10-10-perf-batch) and mirrored in the HLR rationales.

### 6.3 Open risks
Cache invalidation is the main risk: the `(id, len)` token is sound only while the edge-mutation
census holds — guarded mechanically (M-M1c) plus the mutation-script equality arm. Lane R byte-identity
rests on premise 2 (`wire` drops out-of-bounds cells) and premise 3 (layout purity) — both pinned by
executed tests, not by the premises' word. Lane S's deferral must not regress the error-graph paint or
the chrome (M-S3, AT-065's scripted open). Out-of-scope carries: S-18 work budget, B-33 dense-DAG
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
