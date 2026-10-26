# Requirements — mapper — Batch 2026-10-25-relmap-r2-batch

> **Artifact language.** English. **Owed in.** `full`.
> **Shape convention (R1 post-mortem control C-3, adopted):** this contract keeps the
> statements — US/HLR/LLR ids, premise table, IFC, validation strategy. AT bodies and the
> AT↔requirement matrix live in `01b-acceptance-design.md`; amendments, rulings and
> mutants live in `01-requirements-ledger.md`.

## 1. Introduction

### 1.1 Purpose

Specify the relation-map **views** of mapper's Darkside TUI — the R2 slice of the
relation-map port: the traceability matrix with its side-panel impact lens, the ranked
gaps view, the node sheet with FEEDS IT / A CHANGE REACHES, and the shell that lists and
opens relation maps. The batch consumes ONLY the R1-frozen headless API
(`PDR-2026-10-25-relmap-r1-batch#D3`); it ships no change to the relation model, the gap
detectors, the descriptor reader or the `--audit` surface beyond the two inherited
hardings named in scope (presentation leaf, per-line hook bound).

### 1.2 Scope

**In scope.**
- The three relation views over the frozen API, per the operator verdict
  `prototypes/round-2026-10-23/verdict-2026-10-24.json`: **matrix-panel** lens +
  **binds-glyphs** cells; **gaps-ranked** (Darkside casing, reach count column);
  **sheet-direct** node sheet (`c` shows the full chain).
- A read-only relation screen hosting the three views, rendered through the one
  `Canvas` adapter with the C10 audit hook; scalecheck sweep at the 118 reference width
  (87 checked), colour always on, English UI, Darkside only.
- The shell: Home learns to list relation maps (`.relmap.yml` descriptor + the derived
  reqharness map), routing by descriptor `kind`, keys in the keymap single seat,
  help/palette entries (MAP-TYPES §6.2).
- The R1 DDR §E residual items this batch inherits: the `relmap/text.py` presentation
  leaf (items 10-11), the per-line bound for `--audit` hook lines (item 13, B-147). The
  default-only derivation (item 12) is noted and left as the seam R5 widens.

**Out of scope.** Timeline (C5, R4) · metro (C6, R5) · FTS evidence search (C8, R3,
behind `security-check-before-tools`) · editing typed edges (OQ5, deferred past R5) ·
the US canon / AT→test table (B-141; until it exists the reqharness map is the HLR/LLR
skeleton, and the US/AT/TC-dependent views degrade as the R1 contract defines) · any
change to the tree kind.

### 1.3 Definitions, acronyms, abbreviations

- **Relation map** — the typed, multi-parent directed graph of the `reqharness` profile,
  derived read-only from the canon (R1). **Tree map** — today's `Graph`, untouched here.
- **Lens** — the side panel answering "if I change node X, which nodes need re-review?"
  (impact lens, QuickMap C3). **Sheet** — the node ficha with FEEDS IT / A CHANGE
  REACHES sections (QuickMap C12).
- **Binds glyphs** — the graduated AT→TC evidence states: ● bound · ◐ tagged · ○ none.
- **Darkside casing** — the mapper design language's label casing (sentence/title case);
  NOT QuickMap's Solari ALL-CAPS (operator note on the verdict, 2026-10-24).
- **D3 API** — the R2-consumable frozen surface of `mapper/relmap/`
  (`PDR-2026-10-25-relmap-r1-batch#D3`): `Profile`, `EdgeType`, `GapRow`, `Node`,
  `Edge`, `Problem`, `RelMap` (with `VISIT_BUDGET`, `visits`, `reach`), `build_map`,
  `Gap`, `detect_gaps`, `rank_gaps`, `default_descriptor`, `load_descriptor`,
  `discover_descriptors`, `CanonUnavailable`, `Derivation`, `derive_reqharness_map`.
- **C10** — scalecheck sweep + Canvas audit hook (hygiene batch, 2026-10-23).
- **AT / TC / HLR / LLR / US** — dev-flow traceability ids; **IFC** — Information Flow
  Contract (C-54); **EARS** — Easy Approach to Requirements Syntax.

### 1.4 References

1. `PDR-2026-10-25-relmap-r1-batch#D3` — the frozen API this batch consumes
   (`.dev-flow/2026-10-25-relmap-r1-batch/design/PDR-2026-10-25-relmap-r1-batch.md`).
2. `DDR-2026-10-25-relmap-r1-batch` §E items 10-14 — residual risks inherited here.
3. `prototypes/round-2026-10-23/verdict-2026-10-24.json` + `PROTOTYPE.md` — the operator
   verdict gating the view designs (git-ignored in the main checkout; read-only).
4. QuickMap `docs/handoff-mapper/MAP-TYPES.md` §3.4, §6.2, §7.1, §9 (R2 row) — approved
   port definition (read-only reference repo).
5. QuickMap `src/quickmap/view_matrix.py`, `view_gaps.py`, `view_sheet.py` — frozen
   layout oracles for C3/C4/C12 (read-only).
6. `docs/ARCHITECTURE.md` — the module map (amended at this batch's ARQ).
7. `tests/test_scalecheck.py`, `tests/test_canvas_audit.py` — the C10 conventions.
8. R1 post-mortem controls C-1..C-5 (`.dev-flow/2026-10-25-relmap-r1-batch/05-postmortem.md`).

### 1.5 Document overview

§2 overall description and source stories · §3 HLRs · §4 LLRs · IFC (C-54) · §5
validation strategy. AT bodies: `01b-acceptance-design.md`. Amendments:
`01-requirements-ledger.md`. Living plan: `PLAN.md`.

## 2. Overall description

### 2.1 Product perspective

mapper is a Textual TUI with one canvas. R1 added the headless relation-map kind beside
the tree kind; R2 surfaces it. The views are the three renderers the prototype round
proved (26 captures at 118×34, 10 at 87×34, operator verdict 2026-10-24), re-skinned to
Darkside tokens and drawn through `mapper/canvas.py` — the Canvas ruling of MAP-TYPES §8
stands: one canvas, never two, with the C10 audit hook.

### 2.2 Product functions

(a) Traceability matrix with side-panel impact lens and graduated binds-glyphs cells.
(b) Ranked structural gaps with reach blast-radius count. (c) Node sheet with FEEDS IT /
A CHANGE REACHES direct neighbours and the `c` full-chain view. (d) Shell listing and
opening relation maps with kind badge, routing, keys, help and palette. (e) The
`relmap/text.py` presentation leaf and the per-line `--audit` hook bound (inherited
hardings).

### 2.3 User characteristics

The operator of the mapper tool on their own repositories — keyboard-driven, reads
Darkside-rendered screens at 118 columns reference width (87 checked).

### 2.4 Constraints

Darkside only; colour always on (NO_COLOR trap documented in the prototype round);
English UI; Python ≥3.10 (no 3.12-only syntax); ≤4 SOURCE files per increment; the
`relmap` module stays headless — no Textual/Rich/`canvas`/`screens`/`widgets` imports
from `mapper/relmap/**` (its ARCHITECTURE row is unchanged apart from the new `text`
leaf inside the package); the views read only the D3 API and the descriptor surface; the
tree kind keeps every invariant it has.

### 2.5 Assumptions and dependencies

A1. The D3 API is frozen and shipped on this branch's base (`867dfd7`); the views are
its first consumer, declared at R1's intake (B4 probe). A2. The reqharness map today is
the HLR/LLR skeleton derived from `REQUIREMENTS.md` (7 gaps, reach flat at 0 — DDR §E 5);
the views must render that honest partial map without noise and must not invent US/AT/TC
data. A3. The prototype verdict is binding for layout choice; its PNGs are design
evidence, and interactions on the real Textual surface are verified by the ATs (the
prototype proves design intent — C-16 note). A4. The `.dev-flow/BACKLOG.md` R2-relevant
carries: B-140 (series), B-141 (US canon/AT table), B-142 (canon hygiene), B-147 (hook
per-line bound), B-151-B-155 (audit/descriptor hygiene and the `repo:` absolute-path
line), B-156-B-158 (flow controls).
A5. Scale coverage is deliberate: the only very-large-map arm is the cap-scale arm of
AT-137 (100,000 nodes at `MAX_NODES`, `LED-2026-10-25-r2.09`) — the windowing LLRs bound
per-render work by construction, and no other AT exercises maps past the 303-node live
skeleton class.

### 2.6 Source user stories

Intake 2026-10-25 (P0). All six stories classified READY; each states an observable
behaviour through the shipped TUI surface. Ids continue the R1 family (`US-RM-*` →
`US-RMV-*`); requirement families: `RVT` text leaf · `RVU` hook bound · `RVM` matrix ·
`RVG` gaps · `RVS` sheet · `RVH` shell.

#### US-RMV-001 — Traceability matrix with side-panel impact lens (READY)

As the operator scoping a change to a requirement, I open the relation map's matrix view
and select a node, and I observe the LLR×TC matrix with the selection's impact lens in a
separate right panel — what feeds it, a change reaches, hop markers, edge evidence
states, a `reaches N nodes` summary and the reach gauge — so I know which tests need
re-review before I touch anything. **Verdict: matrix-panel** (the band variant is
rejected: hop 2 lands on ATs, which are not columns). AT-matrix cells carry the
graduated binds glyphs ●/◐/○ — **verdict: binds-glyphs** (letters rejected: initial
collisions read as alphabet soup; the evidence name lives in the sheet/panel row).
- **Statement:** the matrix view shall render the honest node skeleton with the
  graduated binds glyphs, the selection's two-hop impact lens in a side panel (what
  feeds it, a change reaches, hop markers, edge evidence states, a reaches N nodes
  summary and the reach gauge), and shall honestly declare its missing test columns
  until the AT→test source exists.
- **Ledger:** LED-2026-10-25-r2.07 (the AT-driver seam ruling names US-RMV-001 as the
  representative view story; the seam serves AT-130…149 across US-RMV-001…004)

#### US-RMV-002 — Ranked structural gaps view (READY)

As the operator triaging the record, I open the gaps view and observe the catalogue
ranked by severity then reach, with a blast-radius **count** column, severity summary
chips (HIGH · MED · LOW · TOTAL) and the worst gap under the cursor — so the record's
loudest silence is first. **Verdict: gaps-ranked** (microbar rejected: it duplicates the
number at 8 cells of resolution; by-kind grouping stays one key away as a toggle if the
PDR wants it — a design decision, not a requirement). Kind labels render in Darkside
casing, NOT Solari ALL-CAPS (operator note, 2026-10-24).
- **Statement:** the gaps view shall render the catalogue of structural gaps ranked by
  severity then reach, with a reach count column, severity summary chips, the worst gap
  under the cursor, declared cuts and counted overflows, honest zeros and a spent-budget
  not-computed tally, and a k-toggle by-kind grouping that returns byte-identical, in
  Darkside casing.
- **Ledger:** none

#### US-RMV-003 — Node sheet: FEEDS IT / A CHANGE REACHES (READY)

As the operator inspecting one node, I open its sheet and observe the two sections with
hop-1 direct neighbours only — FEEDS IT (what a change to them does to this node) and A
CHANGE REACHES (what changing this node forces) — each row with its edge type, evidence
state and the declared cut `+NN more upstream at hop 2 — c shows the chain`; pressing
`c` shows the full chain with hop markers. The node's own gaps list under the sections.
**Verdict: sheet-direct** (stacked full-width density as default; columns rejected: they
halve the WHAT column and split attention).
- **Statement:** the node sheet shall render the focused node's feeds it and a change
  reaches sections with hop-1 direct neighbours, the edge type and evidence glyph per
  row, declared empty sections, the hop-2 cut lines, the c-toggle stacked full chain
  with per-node minimum-hop markers, and the focused node's own gaps band.
- **Ledger:** none

#### US-RMV-004 — Shell: list and open relation maps (READY)

As the operator, from Home I observe relation maps listed beside the tree maps with a
kind badge (tree / relation·reqharness), I open a `<name>.relmap.yml` descriptor or the
derived reqharness map when no descriptor exists, and I land on a read-only relation
screen with the three views, whose keys, help entries and palette entries are
discoverable through the keymap single seat (MAP-TYPES §6.2; OQ-R2 open on listing
order — see PLAN.md).
- **Statement:** Home shall list relation maps beside tree maps in one name-sorted list
  with kind badges, open a .relmap.yml descriptor or the derived reqharness map when no
  descriptor exists, and land on a read-only relation screen whose keys, help and
  palette entries derive from the keymap single seat; opening a relation map writes
  nothing.
- **Ledger:** none

#### US-RMV-005 — One presentation leaf (READY)

As the operator, the display cut and the refusal wording I meet in the views and in
`--audit` come from one leaf module (`relmap/text.py`), so wording can never drift
between two printers. Observable: a census over `mapper/relmap/**` finds exactly one
definition site for the cut, `DISPLAY_MAX` and `refusal_line`, and exactly one import
path for `refusal_line` (the double path `descriptor.refusal_line` vs the `audit.__all__`
re-export is collapsed). DDR §E 10-11; B-153.
- **Statement:** the display cut, DISPLAY_MAX and the refusal wording the operator meets
  in the views and in --audit shall come from one presentation leaf
  (mapper/relmap/text.py) — exactly one definition site for each and exactly one import
  path for refusal_line — so wording can never drift between two printers.
- **Ledger:** none

#### US-RMV-006 — Bounded `--audit` hook lines (READY)

As the operator reading `mapper --audit` output in a shared log, every structure line
respects a per-line character bound, so no fact wraps mid-line. Observable: the hook
path of `run_cli` truncates or refuses over-long producer lines at a bound decided in
this batch (B-147; DDR §E 13), with the count and verdict-prefix semantics of
`PDR-2026-10-25-relmap-r1-batch#D4` unchanged.
- **Statement:** every structure line the --audit hook prints shall respect a per-line
  bound of 240 characters decided in this batch, cut at 239 with one ellipsis after
  escaping and never mid-spelling, with the line-count bound, the verdict-prefix
  rewrite and the exit code of PDR-2026-10-25-relmap-r1-batch#D4 unchanged.
- **Ledger:** none

#### Refinement log (one block per story)

- **US-RMV-001 · Functionality:** who — the operator; outcome — the impact answer on
  screen; why — review scoping before edits; out of scope — editing, the band lens
  variant, the letters cell variant. **Feasibility:** the D3 API answers up/down/reach;
  the prototype proved the layout at 118 and 87; no unknowns beyond the PDR's renderer
  cuts. **Evaluability:** the rendered screen at 118×34 and 87×34 is the surface; ATs
  drive the real keys (arrow/enter), not a proxy. **Independent:** yes — matrix renderer
  file set disjoint from gaps/sheet. **Verdict: READY.**
- **US-RMV-002 · Functionality:** triage order; out of scope — the microbar variant,
  by-kind as a separate screen. **Feasibility:** `rank_gaps(limit=None)` is frozen;
  severity chips derive from the ranked list. **Evaluability:** screen shows ranked rows
  and the count column; cursor lands on the worst gap. **Independent:** yes.
  **Verdict: READY.**
- **US-RMV-003 · Functionality:** per-node answers; out of scope — columns variant,
  graph-walk rendering. **Feasibility:** `neighbourhood` is O(V+E) per focused node
  (ARCHITECTURE note); hop-2 cut is a declared display rule. **Evaluability:** the sheet
  renders direct neighbours, the cut line, the `c` chain toggle. **Independent:** yes.
  **Verdict: READY.**
- **US-RMV-004 · Functionality:** discover/open relation maps; out of scope — the
  connect-repo and build-map tab changes (uifix D1/D2 decisions belong to the UI batch),
  store db caching of derived nodes (deferred — recompute-on-open per OQ6 recommendation,
  no `mapper.db` schema change in this batch). **Feasibility:** home already globs
  `*.mmd` (`mapper/screens/home.py:209`); descriptor discovery exists
  (`discover_descriptors`, D2). **Evaluability:** home lists the badge, opening routes to
  the relation screen, keys/help/palette carry the entries. **Independent:** yes —
  touches `screens/home.py`, `app.py`, `keymap.py`, `screens/help.py`, `screens/palette.py`.
  **Verdict: READY.**
- **US-RMV-005 · Functionality:** wording singularity; out of scope — rewording any
  message. **Feasibility:** pure move inside `mapper/relmap/`; import paths known.
  **Evaluability:** AST/grep census (derived from the code — C-31) plus green suite.
  **Independent:** yes — data layer, no screen files. **Verdict: READY.**
- **US-RMV-006 · Functionality:** bounded lines; out of scope — the `repo:` absolute
  path line (B-155, its own backlog row). **Feasibility:** the hook loop lives in
  `reqharness/audit.py`; the bound is a constant plus a cut at the sink. **Evaluability:**
  a producer emitting an over-long line is truncated at the bound; D4 semantics intact.
  **Independent:** yes — `reqharness/audit.py` only. **Verdict: READY.**

### 2.7 Premise evaluation (C-43) — MANDATORY, one row per premise

Executed probes run 2026-10-25 in the worktree (`PYTHONPATH=<worktree> … python`), transcript
`evidence/p1-derivation-probe-2026-10-25.txt` (to be filed with the batch evidence).

| # | Premise | Status | Evidence |
|---|---|---|---|
| P1 | The D3 API is frozen and shipped on this batch's base (`867dfd7`) | TRUE | `mapper/relmap/model.py`, `gaps.py`, `descriptor.py`, `adapter.py` on disk; freeze record `PDR-2026-10-25-relmap-r1-batch#D3`; R2 changes none of it (ARQ commitment) |
| P2 | Today's derived map is the honest HLR/LLR skeleton | TRUE (measured) | Executed probe 2026-10-25: `derive_reqharness_map('.', default_descriptor())` → 303 nodes (85 HLR, 218 LLR), 215 `refines` edges, 0 problems, 7 gaps (all MED `hlr without llr`, reach 0, not-computed 0); no US/AT/TC nodes exist (B-141); ATs pin absolute figures only on seeded fixtures |
| P3 | The Darkside label toolkit (`plain`, `fit`, `kind_chip`, `hint_line`, tokens) exists with the cited signatures | TRUE | `mapper/darkside.py:550-561` (`plain`), `:602-621` (`fit`), `:412-415` (`kind_chip`), `:386-392` (`hint_line`), `:47-64` (tokens) |
| P4 | The one Canvas carries the C10 audit hook | TRUE | `mapper/canvas.py:96-130` (constructor `audit` mapping; `put` records `clip`/`overprint`); `:207-237` (`rows()`); convention `tests/test_scalecheck.py:132-174` |
| P5 | The Textual `run_test()` pilot idiom drives the real surface | TRUE | `tests/test_colour_always_on.py:64-70` (size tuple, `pilot.press`, `wait_for_scheduled_animations`); frame capture `:25-34` |
| P6 | The keymap seat accepts an additive scope without moving the whole-seat pin | TRUE | Precedent `SCOPE_REVIEW` addition (`mapper/keymap.py:41`); seat shape `:139-152`; whole-seat pin `tests/test_key_dispatch.py:189` (the pin assertion, `test_at_n03h…`; the `:137` → `:170` citations repaired per COND-ARCH-3, re-repaired per COND-DDR-1 at the P5 records pass, `LED-2026-10-25-r2.32`) untouched by a scope addition |
| P7 | The operator verdict binds the four view decisions | TRUE | `verdict-2026-10-24.json` (matrix-panel · binds-glyphs · gaps-ranked · sheet-direct) + operator notes (D1/D2 excluded — the uifix batch); read 2026-10-25 |
| P8 | The QuickMap C3/C4/C12 oracles are readable | TRUE | `view_matrix.py` (252 LOC), `view_gaps.py` (87), `view_sheet.py` (132) read 2026-10-25 (read-only reference repo) |
| P9 | Home's map enumeration is the single site `home.py:209` | TRUE | `mapper/screens/home.py:209` (`sorted(store.workspace.glob("*.mmd"))`); table `:300`; open route `:455-458`; MAP-TYPES §6.2 "there is no store-level list method" |
| P10 | `cut`/`DISPLAY_MAX`/`refusal_line` live where the DDR says, with two `refusal_line` paths | TRUE | `mapper/relmap/model.py:34` (`DISPLAY_MAX = 120`), `:67-71` (`cut`); `mapper/relmap/descriptor.py:211` (`refusal_line`); second path `mapper/relmap/audit.py:34` + `:209-210` (`__all__` re-export) — the double path this batch collapses (DDR §E 10-11) |
| P11 | The hook line COUNT bound (1,000) exists; no per-line bound | TRUE | `mapper/reqharness/audit.py:82` (`HOOK_LINE_LIMIT = 1000`), `:383` (`islice(…, HOOK_LINE_LIMIT + 1)`), `:430-431` (print loop); no per-line length guard — B-147, owned by RVU |
| P12 | Hostile-payload vocabulary for the C8 arms is established practice | TRUE | R1 AT-122 arm 3 (ESC + U+202E through the canon, `01-requirements.md`); dual-guard precedent `mapper/screens/draft_guard.py:54-67` — R2 adds **LF + TAB** to the vocabulary per COND-SEC-1 (`LED-2026-10-25-r2.14`): `_row_text` maps both to single spaces (`mapper/darkside.py:576`), so a hostile payload cannot forge a second rendered row, and the AT-134/AT-148 arms assert the payload renders on ONE row |

### 2.8 Fork preconditions (C-52) — MANDATORY

**The batch forks (trigger A4 fired): one trunk, then four lanes** (§6 of the module map).
Preconditions evaluated at P1; each lane's increment gate re-reads them.

| # | Precondition | Holds when | Checked |
|---|---|---|---|
| F-1 | The trunk's text-leaf increment (RVT) has landed and the R1 suite is green | LLR-RVT.1.1/.1.2 census green; `tests/test_relmap_*.py` re-counted | Inc-2 gate entry |
| F-2 | The trunk's screen-host increment has landed and the PDR has SEALED the host↔renderer surface | §4 row "RelMap screen host ↔ renderer surface" sealed; renderers build against it unchanged | each lane's entry |
| F-3 | Lane file sets are disjoint — matrix/gaps/sheet own exactly their renderer file; shell owns home/app (+6b help/palette); the keymap seat scope is TRUNK-owned (Inc-2 — the single seat gates `BINDINGS` before the lanes fork, ruling `LED-2026-10-25-r2.08`); RVU owns `reqharness/audit.py` | the §6 worksheet intersections stay empty; a lane needing a host change STOPS and re-cuts (the two exits: re-cut, or move the boundary at a new ARQ) | each lane's packet §2 |
| F-4 | The reverse census for each lane's touched symbols runs in the lane's first increment | B1 census table per lane (home/keymap/help/palette/a3-census pins named in §6) | each lane's packet §5.2 |
| F-5 | The join: every lane's ATs run on the joined tree before the DDR | the AT-driver seams exist on trunk — PROBED 2026-10-25 PASS (`evidence/p2-seam-at-driver.md`, ruling `LED-2026-10-25-r2.07`): the fixture-workspace injection point is the `MapperApp(workspace=…)` constructor argument (`mapper/app.py:250`) under a headless `run_test()` pilot; lanes 3–5 re-verify the injection at their entry, not only at the join | DDR |

## 3. High-level requirements (HLR)

Two-level decomposition per the modes table; every HLR traces to one story; statements are
EARS with `shall`. Module families: **RVM** matrix + lens · **RVG** gaps view · **RVS** node
sheet · **RVH** shell · **RVT** presentation leaf · **RVU** hook per-line bound.

### HLR-RVM.1 — The traceability matrix grid
- **Statement:** When the matrix view is active, the matrix renderer shall paint a row → column grid whose rows are the map's sourced nodes in input order and whose columns are the sourced test-side nodes (TC today; none exist on the R1 skeleton), shall draw one glyph cell per row/column pair for the strongest edge between that pair (diagonal `▪`, no edge `·`), shall distinguish the selected row and column, and shall keep the selected row and column visible by windowing with every undisplayed row and column declared in words.
- **Traces to:** US-RMV-001
- **Validation:** test — cell census and windowing assertions over `build_map`-built synthetic maps plus the derived skeleton; geometry pinned by HLR-RVM.4.
- **Verdict cited:** `d_matriz_lente = "matrix-panel"` — "lens is a SEPARATE right panel … the grid stays clean"; `d_matriz_celda = "binds-glyphs"` (verdict-2026-10-24.json; PROTOTYPE.md §D-matriz).
- **Ledger:** LED-2026-10-25-r2.31 (retrospective — its matrix renderer's severity/busy sites classified in the hue census; the census requirement itself, HLR-S06.3, is sealed in `2026-08-26-ui-next-batch-02`); LED-2026-10-25-r2.33 (its census escape's pre-fix RED, stored)

### HLR-RVM.2 — The two-hop impact lens panel
- **Statement:** When a node is selected, the lens panel shall list what feeds it (`up`, hops 1 and 2) on the left and what a change to it reaches (`down`, hops 1 and 2) on the right, each row marked with its hop (`↑1`/`↑2`/`↓1`/`↓2`), its edge type and its evidence state; and shall print the summary `change <id> reaches N nodes` with `hop 1: n direct · hop 2: m chained` and a reach gauge, where N is `RelMap.reach` and a `None` reach is shown as `not computed`, never a fabricated number.
- **Traces to:** US-RMV-001
- **Validation:** test — lens rows and summary compared against an independent in-test oracle over `RelMap.up`/`down`/`reach` (semantics frozen R1, `mapper/relmap/model.py:200-235`).
- **Verdict cited:** matrix-panel — "FEEDS IT ← / A CHANGE REACHES →, hop markers, edge evidence states, `reaches 6 nodes` summary, WARN reach gauge" (PROTOTYPE.md; `shots/png/matrix-panel.png`).
- **Ledger:** none

### HLR-RVM.3 — The honest partial map
- **Statement:** When the derived map holds no test-side nodes, the matrix body shall declare `no test columns yet — the AT→test table (B-141) feeds this view` instead of painting phantom columns, the lens shall remain fully functional over the `refines` edges that exist, and the renderer shall never display a US, AT or TC id, title or edge that the map does not contain.
- **Traces to:** US-RMV-001
- **Validation:** test — a census over the rendered text of the real derived skeleton (no `US-`/`AT-`/`TC-` tokens) plus the exact declaration line; inspection cannot prove a negative, the census can.
- **Verdict cited:** the rejected band variant — "hop 2 lands on ATs, which are not columns" (PROTOTYPE.md); R1 DDR §E 5.
- **Ledger:** none

### HLR-RVM.4 — Bounds and safe text on the real surface
- **Statement:** At the 118×34 reference and the 87×34 check sizes, the matrix renderer shall produce no more than `h` lines of at most `w` cells, shall construct its canvas with the C10 audit sink armed and accumulate zero unexplained clip or overprint events, and every label carrying canon-derived text shall be assembled markup-safe so no bracket, ESC or control character from the canon is parsed as markup or styled.
- **Traces to:** US-RMV-001
- **Validation:** test — geometry is measurable exactly; markup safety asserted by a hostile-payload arm on the live Textual surface (C-16) plus unit arms (C8/C-17).
- **Verdict cited:** MAP-TYPES §9 R2 — "re-skinned to Darkside tokens … through the canvas adapter with the C10 audit hook; scalecheck at 118 reference width".
- **Ledger:** none

### HLR-RVG.1 — The ranked gaps screen
- **Statement:** When the operator opens the gaps view of a relation map, the screen shall render one row per detected gap in the order returned by `rank_gaps` — severity HIGH, MED, LOW, then reach descending, detection order on ties — under a header naming the ranking and a tally of the gaps per severity, each row carrying its rank, gap kind, node, WHAT sentence, reach as a plain count and severity, with the cursor on the worst gap and rows that do not fit the viewport declared as cut markers, never dropped silently.
- **Traces to:** US-RMV-002
- **Validation:** test — a `run_test()` pilot AT asserts the rendered strings; the ranking order itself is pinned by R1 (`tests/test_relmap_gaps.py::test_ranking`), this HLR pins that the view renders that order unchanged.
- **Verdict cited:** `d_gaps = "gaps-ranked"` — "the microbar duplicates the count at 8 cells of resolution" (rejected; PROTOTYPE.md §D-gaps).
- **Ledger:** none

### HLR-RVG.2 — Darkside casing, never Solari ALL-CAPS
- **Statement:** Every label the gaps view renders from catalogue data — gap kinds, severity tally words, field-band headers, cut markers and the empty-state line — shall be presented in Darkside casing (lowercase sentence case, per the `darkside` module's own conventions), never in the QuickMap/Solari ALL-CAPS the prototype screenshot shows.
- **Traces to:** US-RMV-002
- **Validation:** test — a census test over the renderer source plus rendered-string assertions; casing is a case-only transform, so a set derived from the shipped catalogue (C-31) keeps it honest.
- **Verdict cited:** PROTOTYPE.md operator-verdict orchestrator note (2026-10-24): "the gaps view's ALL-CAPS kind labels follow QuickMap's Solari casing; the implementation follows Darkside casing rules."
- **Ledger:** none

### HLR-RVG.3 — Canon-derived text renders markup-safe
- **Statement:** Every string the gaps view renders that originates in the repository canon — node ids, titles and the sentences built from them — shall be coerced through `darkside.plain` and the shared row coercion before painting, shall be painted with explicit-style `Text` or `markup=False` sinks only, and a payload carrying markup brackets, ESC or control characters shall render literally with no style leak and no parse error.
- **Traces to:** US-RMV-002
- **Validation:** test — hostile-payload AT arm on the composited frame (style runs inspected) plus a painter unit arm; C8/C-17 mandatory at Phase 1.
- **Verdict cited:** C8/C-17 batch mandate; repo precedent `mapper/screens/draft_guard.py:54-58`.
- **Ledger:** none

### HLR-RVS.1 — Node identity header
- **Statement:** When the sheet view renders for the focused node, the top of the view shall identify the node by its id and title on one bold line and its kind badge on the line below, with every canon-derived field assembled markup-safe.
- **Traces to:** US-RMV-003
- **Validation:** test (pilot-rendered sheet at 118×34 and 87×34; header strings and chip asserted).
- **Verdict cited:** `d_ficha = "sheet-direct"`; header form in `shots/png/sheet-direct.png`. Reconciled to the D3 model: `Node` carries no source field (`mapper/relmap/model.py:42-49`), so the prototype's `TC · tests/…` second segment is not portable — the R2 header is id · title + kind chip (OQ-SHEET-7, ruled: kind chip only).
- **Ledger:** LED-2026-10-25-r2.31 (retrospective — its sheet renderer's severity/busy sites classified in the hue census and its gap-head word in the chrome lexicon; the census requirements themselves, HLR-S06.3 and `A-112`, are sealed in earlier batches); LED-2026-10-25-r2.33 (its census escape's pre-fix RED, stored)

### HLR-RVS.2 — FEEDS IT / A CHANGE REACHES, direct neighbours honestly
- **Statement:** The sheet shall render two banded sections — `feeds it — what a change to them does to this node` (upstream, `map.up`) and `a change reaches — what changing this node forces` (downstream, `map.down`) — listing every direct neighbour with its hop marker (`↑1`/`↓1`), the connecting edge type, the neighbour id and the edge's evidence-state glyph, and a section with no neighbours shall render a declared empty line rather than disappearing.
- **Traces to:** US-RMV-003
- **Validation:** test (row content per section asserted against an in-test oracle computed from `up`/`down`/`edges`).
- **Verdict cited:** PROTOTYPE.md §D-ficha; MAP-TYPES §3.4 (C12) — "FEEDS IT and A CHANGE REACHES come free with the engine".
- **Ledger:** none

### HLR-RVS.3 — Declared cut and the `c` full-chain density
- **Statement:** In the default direct density the sheet shall declare the hop-2 cut as a hatch line `╌╌ +NN more upstream at hop 2 — c shows the chain` (NN zero-padded, omitted at count zero, with the symmetric downstream line when non-zero), and pressing `c` shall switch the sheet to the stacked density showing the full chain with per-node minimum-hop markers (`↑N`/`↓N`), with the density declared in the crumb and the `next ▸` note line.
- **Traces to:** US-RMV-003
- **Validation:** test (cut count against an independent hop-2 oracle; `c` driven as a real key on the pilot; note line and crumb asserted).
- **Verdict cited:** US-RMV-003; `shots/png/sheet-direct.png` (cut line, both widths); PROTOTYPE.md — "sheet-stacked with the full chain as the `c` view; sheet-direct as the default density".
- **Ledger:** none

### HLR-RVS.4 — The node's own gaps under the sections
- **Statement:** The sheet shall close with a `gaps on this node` band listing every gap whose subject is the focused node, one row per gap with the gap kind in the failure tone and the gap sentence beside it, cut to the available width with a declared ellipsis.
- **Traces to:** US-RMV-003
- **Validation:** test (rows asserted equal to an independent filter of `detect_gaps` output over the D3 model).
- **Verdict cited:** `! VERIFIES WITHOUT EVIDENCE …` row in `sheet-direct.png`; "plus the node's own gaps" (PROTOTYPE.md §D-ficha).
- **Ledger:** none

### HLR-RVS.5 — Markup-safe label assembly (C8/C-17 sink)
- **Statement:** Every label that carries canon-derived text shall be assembled markup-safe — coerced through `darkside.plain` and placed into `Text` with explicit styles or `markup=False` — so bracket, ESC and control-char payloads render literally with no style leak and no parse error.
- **Traces to:** US-RMV-003
- **Validation:** test (hostile-payload arm on the real screen: payload rendered byte-literal, no unintended ACCENT/ALERT/WARN span, no raise).
- **Verdict cited:** C8/C-17 mandatory at Phase 1; precedent `mapper/screens/draft_guard.py:54-63`.
- **Ledger:** none

### HLR-RVS.6 — Width and overflow discipline, never silent loss
- **Statement:** At the 118-column reference and the 87-column check the sheet shall paint every row inside the canvas width (long values cut with one trailing ellipsis), and section rows that do not fit the viewport shall be counted on a declared final line rather than silently dropped.
- **Traces to:** US-RMV-003
- **Validation:** test (sweep at (118, 34) and (87, 34) with the C10 canvas-audit hook armed: zero `clip`/`overprint` entries; overflow arm asserts the counted line).
- **Verdict cited:** 87-col evidence `shots/png87/sheet-direct.png`; QuickMap lineage `view_sheet.py:122-128` ("rows past the height are counted on the last line, never cut silently").
- **Ledger:** none

### HLR-RVH.1 — Home lists relation maps beside tree maps with a kind badge
- **Statement:** Home shall list every `<workspace>/*.relmap.yml` descriptor beside the existing `<workspace>/*.mmd` tree maps in one name-sorted recents table, each relation row carrying a kind badge `relation·reqharness` in the tree rows' chip style.
- **Traces to:** US-RMV-004
- **Validation:** test — the observable outcome is the rendered recents table on the real Textual surface (AT-145); badge values pinned by a census (TC-RM-22).
- **Verdict cited:** MAP-TYPES §6.2 — "Home learns to also glob `*.relmap.yml`, shows a kind badge … keeps recents/hero as they are".
- **Ledger:** none

### HLR-RVH.2 — Opening routes by descriptor kind; relation maps open read-only
- **Statement:** Opening a listed map shall route by its kind: a tree map shall open the existing `MapScreen`, and a relation map shall open a read-only relation screen hosting the three ported renderers, with no draft, save, archive, edit or `osopen`-launch action bound on it.
- **Traces to:** US-RMV-004
- **Validation:** test — `run_test()` pilot presses `↵` on each row kind and asserts which screen is on top (AT-146); read-only asserted as the absence of write bindings in the relmap scope (BINDINGS census).
- **Verdict cited:** MAP-TYPES §6.2 — "Screen routing by descriptor `kind` … Relation maps open read-only … without drafts."
- **Ledger:** none

### HLR-RVH.3 — No descriptor: the derived reqharness map opens
- **Statement:** When no `<workspace>/*.relmap.yml` descriptor exists, Home shall list one derived relation row — named by the canon stem — produced by `derive_reqharness_map(workspace, default_descriptor())`, and opening it shall derive the map at open time; when descriptors exist, each descriptor is one row and no derived row appears.
- **Traces to:** US-RMV-004
- **Validation:** test — pilot opens the derived entry over a fixture workspace and asserts the honest HLR/LLR skeleton renders with no invented US/AT/TC content (AT-147).
- **Verdict cited:** R1 ruling OQ-R1-1 (default descriptor); US-RMV-004.
- **Ledger:** none

### HLR-RVH.4 — The relation screen host through the single keymap seat
- **Statement:** The relation screen shall compose its chrome (crumb, keybar, view canvas), switch the three views on `1`/`2`/`3`, re-derive the map on open and on `r`, leave on `q` (with `escape` as a quiet alias), and move the selection with the cursor keys, with every bound key, help entry and palette entry derived from the single keymap seat.
- **Traces to:** US-RMV-004
- **Validation:** test — pilot drives the real keys and asserts the rendered chrome and view swaps (AT-148); seat conformance pins BINDINGS == seat (TC-RM-25); help/palette carry the scope (AT-149).
- **Verdict cited:** Prototype chrome (`shots/png/matrix-panel.png` bottom bar: `view 1 matrix 2 gaps 3 sheet · lens enter impact on node · app ? all keys · q quit`).
- **Ledger:** LED-2026-10-25-r2.31 (retrospective — its scope's 13 seat rows declared in the Inc-9 seat diff and its seat words in the chrome lexicon; `CD-25a` and `A-112` are sealed in earlier batches); LED-2026-10-25-r2.33 (its seat-census escapes' pre-fix REDs, stored)

### HLR-RVH.5 — A refused or hostile descriptor never crashes the shell
- **Statement:** A descriptor or canon that refuses to load shall surface its fixed refusal line and leave Home and the app intact, and every descriptor/canon-derived label the host renders shall be assembled markup-safe.
- **Traces to:** US-RMV-004
- **Validation:** test — hostile-payload arms on the real surface (AT-148 hostile arm, AT-145 name arm) plus the markup-safety sink census (TC-RM-27).
- **Verdict cited:** R1 LLR-RML.1.5 (closed cause set K1–K17); C6/C8 family; MAP-TYPES §6.3.
- **Ledger:** none

### HLR-RVT.1 — The presentation leaf
- **Statement:** The presentation primitives `cut`, `DISPLAY_MAX` and `refusal_line` shall be defined in exactly one leaf module inside `mapper/relmap/`, and every consumer inside the package — `model`, `descriptor`, `adapter`, `audit` — shall import them from that leaf; the `audit` re-export of `refusal_line` shall be dropped so one name has one import path; and the move shall change no rendered byte.
- **Traces to:** US-RMV-005
- **Validation:** test — an AST census (derived from the code, C-31) asserts one definition site and one import path per name; a byte-identity probe over the R1 refusal/golden surfaces asserts no wording change.
- **Verdict cited:** R1 DDR §E 10-11 (B-153) — "Move `cut`, `DISPLAY_MAX` (and consider `refusal_line`) to a leaf `relmap/text.py` in the R2 PDR, before R2 adds a second printer"; "nothing pins which one tests use."
- **Ledger:** none

### HLR-RVU.1 — Bounded `--audit` hook lines
- **Statement:** The `run_cli` hook path shall bound every printed hook line to a per-line
  character bound of 240 (ruling `LED-2026-10-25-r2.02`), cutting longer lines after the
  escape pass with a declared ellipsis, the cut never splitting an escape spelling, while
  the line-count bound (1,000), the `verdict: ` prefix rewrite, the fixed no-repo/no-registry
  lines and the exit code remain exactly as frozen by D4.
- **Traces to:** US-RMV-006
- **Validation:** test — a producer emitting over-long lines is cut at the bound; the D4 behaviours are asserted unchanged by the R1 suite plus new arms.
- **Verdict cited:** R1 DDR §E 13 (B-147) — "A generic hook has no per-line length bound … decide in R2."
- **Ledger:** LED-2026-10-25-r2.02

## 4. Low-level requirements (LLR)

Every LLR traces to one HLR; `shall` only inside statements; draft-time verification cites
disk (`file:line`, probed 2026-10-25) or carries an explicit `assumed — verify in Phase N`
flag; a negative control names the mutation that reddens the asserting arm.

### LLR-RVM.1.1 — Rows, labels and paging
- **Statement:** When the matrix renders, the renderer shall paint one row per sourced node in `RelMap.nodes` input order, each label a right-aligned row number, a space and the node id cut to an id field between 8 and 12 cells (`darkside.fit`), and shall window the row set to keep the selected node visible, centring the window on the selection where the ends allow.
- **Traces to:** HLR-RVM.1
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_matrix.py`
- **Draft-time verification:** id-field constants and label shape ported from `qm:view_matrix.py:43-63` (ID_MIN=8, ID_MAX=12); window centring `qm:view_matrix.py:72-76`; `darkside.fit` at `mapper/darkside.py:602`; node input order `mapper/relmap/model.py:135-136`.
- **Negative control:** M-RVM-1 (drop row windowing) → a selection below the fold leaves no selected row painted; `test_window_declarations` RED.
- **Ledger:** LED-2026-10-25-r2.09 (the cap-scale arm asserts this windowing at the 100,000-node cap)

### LLR-RVM.1.2 — Cells: one glyph per pair, strongest edge wins
- **Statement:** When a row and column share at least one edge, the cell shall show the glyph of the profile edge type of the winning edge, chosen by an ALERT-class edge (evidence missing or in cycle) before a plain one and then by profile edge-type order; the diagonal shall be `▪`, an empty pair `·`, a graduated-evidence edge type (`binds`) shall render `●` bound or `◐` tagged, and the selection's row and column shall carry the focus tint; a row whose AT node has no binds edge at all shall bear a `○` badge in the label gutter, ALERT when the node is open and MUT when it is closed or historical.
- **Traces to:** HLR-RVM.1
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_matrix.py`
- **Draft-time verification:** ranking rule `qm:view_matrix.py:66-69` (`_rank`); graduation fields `mapper/relmap/model.py:53-58` (`Edge.evidence_missing`, `Edge.in_cycle`) and `mapper/relmap/profile.py:90` (`binds`, evidence "graduated"); node `open` flag `mapper/relmap/model.py:48`. The exact reqharness glyph table (verifies → `✓`, binds → `●`/`◐`, refines → `•`, covers → `≡`) is orchestrator-accepted (OQ-M3) and frozen at the PDR; the mechanism is independent of the table.
- **Negative control:** M-RVM-2 (render the missing-evidence backfill initial — the rejected binds-letters variant) → the cell census sees letters and goes RED.
- **Ledger:** LED-2026-10-25-r2.22

### LLR-RVM.1.3 — Window declarations, ruler and legend
- **Statement:** When rows or columns do not fit the viewport, the renderer shall declare the row window as `NN–NN / N` centred on a flap under the grid and the hidden column count as `NN out of view` at the top right, shall paint the two-digit column ruler (tens over ones) above the grid, and shall paint the legend line naming the evidence glyphs (`✓ verifies · ! evidence missing · · no verifies edge`, Darkside casing), cut to the viewport width.
- **Traces to:** HLR-RVM.1
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_matrix.py`
- **Draft-time verification:** declaration formats and ruler `qm:view_matrix.py:96-104,137-141`; legend `qm:view_matrix.py:142-148` re-cased per Darkside (lowercase precedents `mapper/darkside.py:315` `KEYBAR_MORE = "all keys"`, `mapper/screens/home.py:300` headers); the 87-col cut legend visible in `shots/png87/matrix-panel.png`.
- **Negative control:** M-RVM-1 (drop the `NN out of view` declaration) → the 87-column arm records unexplained C10 clips; `test_geometry_audit_sweep` RED.
- **Ledger:** none

### LLR-RVM.2.1 — Lens rows: rings, hop markers, evidence states
- **Statement:** When a node is selected, the lens shall list the `up` ring under `what feeds it ←` and the `down` ring under `a change reaches →`, each member once, in edge input order, marked `↑1`/`↓1` for direct neighbours and `↑2`/`↓2` for nodes reached through a drawn hop-1 member of the same direction; each row shall name the edge type (Darkside casing) and node id with its evidence-state glyph (`✓` evidence on file, `!` evidence missing, `●`/`◐` for graduated binds), overflow members shall be counted as `+NN more`, and at lens widths below 60 cells the hop-2 columns shall fold away leaving `↑1`/centre/`↓1` — `lens width` here means the view's viewport width (`state.width`) (`LED-2026-10-25-r2.21`).
- **Traces to:** HLR-RVM.2
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_matrix.py`
- **Draft-time verification:** ring construction `qm:view_matrix.py:152-166` (`_rings`: second ring through first-ring parents only, each node once); hop folding threshold `qm:view_matrix.py:179`; `+NN more` `qm:view_matrix.py:229-232`; edge input order `mapper/relmap/model.py:200-206`; hop markers and layout evidence `shots/png/matrix-panel.png` (prototype `↑1 REFINES` is Solari casing — Darkside lowercase pinned here, OQ-M4 accepted).
- **Negative control:** M-RVM-5 (draw hop-2 members whose hop-1 parent is not on screen) → a synthetic 3-chain oracle sees an orphaned hop-2 row; RED.
- **Ledger:** LED-2026-10-25-r2.21; LED-2026-10-25-r2.22; LED-2026-10-25-r2.23

### LLR-RVM.2.2 — Summary and reach gauge
- **Statement:** When a node is selected, the lens shall print `change <id> reaches N nodes` above `hop 1: n direct · hop 2: m chained`, where N is `RelMap.reach(id)`, n is the count of direct `down` members and m is the count of chained hop-2 members; when `reach` returns `None` (budget spent) the count shall render `not computed` in WARN with the gauge empty, and on a computed map the gauge fill shall be proportional to reach against the greatest reach on the map. When `reach` is `None` the summary row reads ` change <id>: not computed` in WARN — the whole mandated words kept on the row; the gauge is empty (`LED-2026-10-25-r2.21`).
- **Traces to:** HLR-RVM.2
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_matrix.py`
- **Draft-time verification:** `reach -> int | None` and the budget `mapper/relmap/model.py:33,208-214` and R1 contract LLR-RMM.2.2; summary and gauge evidence `shots/png/matrix-panel.png` (`change LLR-REPAIR.2 reaches 6 nodes`, `hop 1: 2 direct · hop 2: 4 chained`, WARN gauge); 87-col truncation `shots/png87/matrix-panel.png`.
- **Negative control:** M-RVM-7 (coerce a `None` reach to `0`) → the budget-spent arm sees a fabricated `0`; `test_lens_reach_not_computed` RED.
- **Ledger:** LED-2026-10-25-r2.21

### LLR-RVM.2.3 — Neighbourhood dimming while focus is on
- **Statement:** When the lens focus is on, the renderer shall dim (FAINT) every grid row and column label outside `RelMap.neighbourhood(selection, 2)`, shall call `neighbourhood` for the selected node only, and shall render every row and column undimmed when focus is off.
- **Traces to:** HLR-RVM.2
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_matrix.py`
- **Draft-time verification:** dimming rule `qm:view_matrix.py:93,102,114`; the focused-node-only rule R1 LLR-RMM.2.2 (`01-requirements.md:346`); `neighbourhood` semantics `mapper/relmap/model.py:229-235`.
- **Negative control:** M-RVM-6 (call `neighbourhood` per painted row) → a counting wrapper sees n calls for n rows; RED.
- **Ledger:** LED-2026-10-25-r2.10 (the black-box dimming arm of AT-131/AT-132 asserts this on the real screen)

### LLR-RVM.3.1 — Zero test columns: the declared empty state
- **Statement:** When the map sources no test-side node kind, the matrix body shall paint the sourced rows with no column ruler and shall declare `no test columns yet — the AT→test table (B-141) feeds this view` where the column header would sit, and the rendered text shall contain no US, AT or TC id, title or edge name that the map does not contain.
- **Traces to:** HLR-RVM.3
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_matrix.py`
- **Draft-time verification:** today's skeleton is HLR+LLR with `refines` only — `mapper/relmap/profile.py:87-90` pairs `("US","HLR"),("HLR","LLR")` with US unsourced (R1 DDR §E 5); live figures measured 2026-10-25 (premise P2): 303 nodes, 215 `refines` edges, 7 gaps; the declaration wording is orchestrator-accepted (OQ-M1) and ruled at the R2 design review.
- **Negative control:** M-RVM-8 (paint an empty `·` column per row regardless of sourced kinds) → the census finds a phantom column block; `test_skeleton_honesty` RED.
- **Ledger:** none

### LLR-RVM.3.2 — Empty and unknown-selection states
- **Statement:** When the map holds zero nodes or the selection names no node on the map, the matrix shall print `no node on record` and the lens shall print nothing but the same state; and when the selection has no `up` and no `down` members, the lens shall print `╌╌╌ relates to nothing` in ALERT.
- **Traces to:** HLR-RVM.3
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_matrix.py`
- **Draft-time verification:** both states ported from `qm:view_matrix.py:85-87,176-178` and `:244-246` (re-cased per Darkside; hatch `╌` at `:45`); defined empty results for unknown ids `mapper/relmap/model.py:200-206,229-232`.
- **Negative control:** M-RVM-9 (raise on an unknown selection id) → the unknown-selection arm errors; RED.
- **Ledger:** none

### LLR-RVM.4.1 — Geometry with the C10 audit hook armed
- **Statement:** When the renderer is invoked at the 118×34 reference and the 87×34 check sizes, it shall return no more than `h` lines of at most `w` cells each, shall construct its `Canvas` with the audit mapping injected and accumulate zero overprint events and zero clip events that are not declared in the rendered text in words, and shall cut every label to its seat before painting rather than relying on clipping.
- **Traces to:** HLR-RVM.4
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_matrix.py`
- **Draft-time verification:** audit semantics `mapper/canvas.py:96-130`; rows production `mapper/canvas.py:207-237` (`rows()` returns `list[Text]`); sweep idiom `tests/test_scalecheck.py:132-174`; the size pair from the batch brief; label pre-cutting `qm:view_matrix.py:190,207` and `darkside.fit` `mapper/darkside.py:602`.
- **Negative control:** M-RVM-10 (drop the label pre-cut, lean on `put` clipping) → clips with no `out of view` declaration; RED.
- **Ledger:** none

### LLR-RVM.4.2 — Markup-safe label assembly (C8/C-17 sink)
- **Statement:** Every label that carries canon-derived text (node ids, titles, kind and edge-type names) shall be routed through `darkside.plain` and placed in explicit-style `Text` or `markup=False` sinks, so a payload of brackets, ESC or control characters renders literally with no style leak and no markup parse error.
- **Traces to:** HLR-RVM.4
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_matrix.py` (unit arms); AT-134 arm (live Textual surface)
- **Draft-time verification:** `darkside.plain` `mapper/darkside.py:550-561` (control-char coercion, deliberately not `rich.markup.escape` — safety comes from never handing file-derived text to a markup sink); sink precedents `mapper/screens/draft_guard.py:54-67` and `mapper/screens/common.py:213,261-264`; `Canvas.put`/`rows()` paint explicit styles (`mapper/canvas.py:130,211-235`) — the canvas is safe by construction, so the seam is label assembly in `base.py`. Width cuts apply to the COERCED string; coercion is never applied to a previously fitted label (the C-10 order — `LED-2026-10-25-r2.06`).
- **Negative control:** M-RVM-11 (assemble a label with raw canon text in a markup-parsing sink) → the hostile arm of AT-134 sees a parse error or a leaked style; RED.
- **Ledger:** LED-2026-10-25-r2.06

### LLR-RVG.1.1 — Data source: detect, rank whole catalogue, render that order
- **Statement:** The gaps renderer shall obtain its rows by calling `detect_gaps(map)` and then `rank_gaps(map, gaps, None)`, shall render the ranked list from the first member of the returned tuple and the not-computed count from the second member, and shall paint the rows in exactly the returned order without re-sorting, filtering or inventing rows. — NOTE (`LED-2026-10-25-r2.24`): under the frozen D1 surface the host ranks once and hands the ranked tuple via `state.gaps`; the shipped renderer paints `state.gaps` order unchanged and re-issues the host's own deterministic memoized ranking call solely to derive the not-computed count the tuple does not carry.
- **Traces to:** HLR-RVG.1
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_gaps_view.py` (planned); ranking oracle itself `tests/test_relmap_gaps.py::test_ranking` (R1, unchanged)
- **Draft-time verification:** `mapper/relmap/gaps.py:90-104` (`detect_gaps`), `:107-138` (`rank_gaps(m, gaps, limit)` returns `(ranked, reach_not_computed)`; severity band then reach descending, ties keep detection order); R1 contract LLR-RMG.1.3; D3 freeze PDR D3 row.
- **Negative control:** M-RVG-1 — re-sort rows by node id (or skip `rank_gaps`) → the severity/reach sequence goes RED.
- **Ledger:** LED-2026-10-25-r2.24

### LLR-RVG.1.2 — Header, tally chips and field band
- **Statement:** The renderer shall paint a header line reading `gaps — what the record does not say` at the left and `ranked by severity, then reach ↓` at the right, a tally row of exactly four chip groups — `high`, `med`, `low`, `total`, each followed by its actual gap count, all four always rendered even at zero — and a field band labelling the columns `no`, `gap`, `node`, `what`, `reach`, `status` in that order.
- **Traces to:** HLR-RVG.1
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_gaps_view.py` (planned); AT-135 asserts the same strings on the real screen
- **Draft-time verification:** layout evidence `shots/png/gaps-ranked.png` and `png87/gaps-ranked.png`; QuickMap oracle `view_gaps.py:35-61`; the always-four-chips rule is a deliberate ruling (a zero count is honest, not omitted).
- **Negative control:** M-RVG-2 — drop the `total` chip (or tally from a different list than the rendered rows) → `total 7` against 7 rows goes RED.
- **Ledger:** none

### LLR-RVG.1.3 — Row anatomy, cursor on the worst gap, severity tokens, no microbar
- **Statement:** Each row shall carry, in field-band order: a zero-padded two-digit rank, the gap kind label, the gap's node id, its WHAT sentence, its reach rendered as a zero-padded three-digit plain count, and its severity word; the renderer shall highlight exactly the row whose index the host passes as the cursor — the cursor being the view's OWN row index on the view's row axis (the ranked-gap row list for this view), which the host moves within `[0, row_count(state))` per the frozen D1 surface, clamped at the ends with no wraparound, and whose initial value shall place the cursor on the first-ranked row at view open; and the view shall not paint any reach microbar or gauge — the count column is the only reach visual.
- **Traces to:** HLR-RVG.1
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_gaps_view.py` (planned); AT-135 (cursor), AT-137 (window follows the cursor)
- **Draft-time verification:** row anatomy `view_gaps.py:72-85`; cursor default 0 and highlight band `view_gaps.py:26-28,73-76`; microbar rejection (verdict); severity token mapping HIGH→ALERT, MED→INK, LOW→MUT over `mapper/darkside.py:47-64`;
WARN is scoped to reach/severity-attention signals ONLY — the matrix lens reach gauge
(LLR-RVM.2.2), the `not computed` state (LLR-RVM.2.2) and the sheet's tagged-binds `◐`
glyph (LLR-RVS.2.3) — and no tally word, chip or other chrome uses WARN (scope ruling
`LED-2026-10-25-r2.05`); MED→INK is orchestrator-accepted (OQ-G2).
- **Negative control:** M-RVG-3 (unpadded reach, or a bar glyph) → the `000`/`006` literal assertions go RED; M-RVG-4 (initial cursor on the last row) → AT-135's highlight assertion RED.
- **Ledger:** LED-2026-10-25-r2.05 · LED-2026-10-25-r2.18 (the cursor-axis ruling from the Inc-2 independent review: per-view row axis through the D1 `row_count` entry, host-clamped, no wrap)

### LLR-RVG.1.4 — Viewport window, cut markers, WHAT drop rule, audit-clean clipping
- **Statement:** When the ranked rows do not fit the viewport the renderer shall follow the cursor with a window whose rows-above and rows-below are declared as cut markers, a WHAT value that does not fit shall end with a single ellipsis glyph, and when the available WHAT width falls below its minimum the WHAT column shall be dropped whole rather than truncated; every painted line shall stay inside the canvas width and height and the canvas-audit sink shall record no clip and no overprint at the reference and check widths.
- **Traces to:** HLR-RVG.1
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_gaps_view.py` (planned); `tests/test_relmap_scalecheck.py` (planned, the R2 sweep at 118×34 and 87×34 with the audit sink injected)
- **Draft-time verification:** window/markers `view_gaps.py:63-70` (`+NN above` / `+NN more`, Darkside-cased); WHAT minimum and drop-whole rule `view_gaps.py:21-22,56-59,79-80` (`WHAT_MIN = 12`); audit hook `mapper/canvas.py:96-130`; width discipline `darkside.shown_cells`/`fit` (`mapper/darkside.py:587-621`).
- **Negative control:** M-RVG-5 (clamp the window to the first page) → the cursor driven to the last row leaves the window; RED. M-RVG-6 (truncate WHAT below its minimum instead of dropping) → the 87-column arm RED.
- **Ledger:** LED-2026-10-25-r2.19

### LLR-RVG.1.5 — By-kind mode (SHIPPED per the orchestrator ruling; toggled by `k`)
- **Statement:** When the operator presses `k` to toggle the view's grouping mode, the renderer shall regroup the same ranked catalogue into one band per gap kind in catalogue order, each band headed by its kind label, a count of its rows and the band's worst severity, with the member rows under their own band keeping their global rank numbers, and a hint line naming the grouping.
- **Traces to:** HLR-RVG.1
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_gaps_view.py` (planned); AT-136 on the real screen (shipped per ruling — not contingent)
- **Draft-time verification:** design evidence `shots/png/gaps-by-kind.png`; catalogue order source `mapper/relmap/gaps.py:92-93` (iterates `map.profile.gaps` in table order). The prototype's by-kind PNG shows a possible first-band/row misalignment — the LLR pins each band over exactly its own rows; flagged for the PDR to confirm. The toggle SHIPS (`LED-2026-10-25-r2.01`); the PDR freeze covers only the glyph/table details, and the `k` binding is pinned in LLR-RVH.4.1.
- **Negative control:** M-RVG-7 — bands sorted by row count instead of catalogue order → the band sequence goes RED.
- **Ledger:** LED-2026-10-25-r2.01; LED-2026-10-25-r2.20

### LLR-RVG.2.1 — Kind labels in Darkside casing, census-guarded
- **Statement:** The renderer shall render every gap kind label by lower-casing the catalogue value — a case-only transform whose result is otherwise byte-identical to the kind string — and no source file of the gaps renderer shall contain a string literal equal to an ALL-CAPS spelling of any shipped catalogue kind.
- **Traces to:** HLR-RVG.2
- **Validation method:** test — rendered strings + AST census · **Asserting tests:** `tests/test_relmap_gaps_view.py` (planned)
- **Draft-time verification:** catalogue kinds as data `mapper/relmap/profile.py:93-108`; census idiom (derived set, C-31) `tests/test_relmap_isolation.py::test_engine_names_no_kind`.
- **Negative control:** M-RVG-8 — restore `.upper()` (or hard-code one kind literal) → the rendered `us without at` assertion and the census go RED.
- **Ledger:** none

### LLR-RVG.2.2 — All other chrome in Darkside casing
- **Statement:** The tally words, the field-band headers, the cut markers, the empty-state line, the header and the view hint shall be authored in lowercase sentence case, matching the casing of every other Darkside chrome surface.
- **Traces to:** HLR-RVG.2
- **Validation method:** inspection + test · **Asserting tests:** `tests/test_relmap_gaps_view.py` (planned); AT-135/AT-137 assert the literals on the real screen
- **Draft-time verification:** Darkside casing evidence `mapper/darkside.py:139` (tab doors), `:318-349` (keybar), `:667-712` (vocabulary labels), `:739-744` (view names); the prototype bottom bar (all lowercase); empty-state `no gaps on record` (re-cased from `view_gaps.py:19,44-46`).
- **Negative control:** M-RVG-9 — author one chrome string in caps → the casing arm RED.
- **Ledger:** none

### LLR-RVG.2.3 — Honest reach: flat `000` rendered as computed; not-computed declared on the tally
- **Statement:** The renderer shall paint the reach value exactly as ranked — including `000` for every gap on today's HLR/LLR skeleton where reach is computed and flat at zero — shall not substitute a dash, a blank or any placeholder for a computed zero, and when the ranking reports a not-computed count greater than zero the tally row shall append a marker declaring how many gaps' reach was not computed.
- **Traces to:** HLR-RVG.2
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_gaps_view.py` (planned); AT-138 (budget-spent and empty-map arms)
- **Draft-time verification:** flat-reach fact R1 DDR §E 5 + live probe (P2: 7 gaps, reach 0, not-computed 0); not-computed semantics `mapper/relmap/gaps.py:128-136`; budget/`None` typing `mapper/relmap/model.py:33,193-196,208`.
- **Negative control:** M-RVG-10 (computed-zero rendered as `-`) → the all-`000` skeleton arm RED; M-RVG-11 (drop the not-computed marker) → the budget-spent arm of AT-138 RED.
- **Ledger:** none

### LLR-RVG.3.1 — The markup-safe label sink (C8/C-17)
- **Statement:** Every canon-derived string painted by the gaps renderer — node id, title text inside the WHAT sentence, kind and qualifier counts — shall pass through `darkside.plain` and the shared single-row coercion before painting, and shall reach the screen only through explicit-style `Text` assembly or `markup=False` sinks; no markup-parsing sink shall receive a raw repository-derived string.
- **Traces to:** HLR-RVG.3
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_gaps_view.py` (planned); AT-139 (composited-frame arm)
- **Draft-time verification:** `darkside.plain` `mapper/darkside.py:550-561`; row coercion `_row_text` `:576-584`; `fit` `:602-621`; the sentence is canon-derived (title cut to `DISPLAY_MAX` by the adapter, R1); the RVT text leaf is orchestrator-owned and lands in trunk Inc-1 (first, before any renderer lane forks — PLAN.md Inc-1), so this sink reads the frozen leaf names from the start, never a not-yet-existing module; `markup=False`-alone insufficiency `mapper/screens/draft_guard.py:54-58`; `kind_chip` escaping precedent `mapper/darkside.py:412-414`. Width cuts apply to the COERCED string; coercion is never applied to a previously fitted label (the C-10 order — `LED-2026-10-25-r2.06`).
- **Negative control:** M-RVG-12 (remove the `plain()` pass) → an ESC payload leaks into the frame; RED. M-RVG-13 (markup-parsing sink) → the `[bold]` payload styles the frame; RED.
- **Ledger:** LED-2026-10-25-r2.06, LED-2026-10-25-r2.13

### LLR-RVS.1.1 — Header layout over the D3 node
- **Statement:** The sheet shall paint the header as exactly two rows — row 0 bold INK `<id> · <title>`, row 1 the `darkside.kind_chip(kind)` badge — where `<id>` and `<title>` come from `RelMap.node(focused)` coerced through `darkside.plain`, and no source/path segment shall be painted because the D3 `Node` exposes none; on today's reqharness skeleton the title is the canon statement already value-cut at `DISPLAY_MAX` (120) by the adapter.
- **Traces to:** HLR-RVS.1
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_sheet.py`
- **Draft-time verification:** `Node` fields `mapper/relmap/model.py:42-49`; `RelMap.node` `:197-198`; `kind_chip` `mapper/darkside.py:412-415`; `plain` `:550-561`; `DISPLAY_MAX = 120` `mapper/relmap/model.py:34`; adapter title cut `mapper/relmap/adapter.py:134-142`.
- **Negative control:** M-RVS-1 (header assembled into a markup sink without `plain`) → the hostile arm of AT-144 RED.
- **Ledger:** none

### LLR-RVS.1.2 — Darkside casing on canon-derived labels
- **Statement:** Canon-derived label text on the sheet — edge-type names and gap-kind names — shall render in Darkside casing (lowercase: `refines`, `verifies`, `binds`, `hlr without llr`), not in the catalogue's stored ALL-CAPS and not in the prototype PNG's caps, which followed QuickMap's Solari casing; fixed copy (section bands, note lines) is authored lowercase and is not transformed; node ids are identifiers, not labels, and keep their case.
- **Traces to:** HLR-RVS.1
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_sheet.py`
- **Draft-time verification:** catalogue kinds stored caps `mapper/relmap/profile.py:93-108`; Darkside casing `mapper/darkside.py:739-745` (`VIEW_NAMES` lowercase), `mapper/screens/home.py:300`; operator note PROTOTYPE.md:175-176. Ruled: the PNG's rendered lowercase governs over the caps transcription in PROTOTYPE.md's quote (OQ-SHEET-1 accepted).
- **Negative control:** M-RVS-2 (render `e.type`/`g.kind` verbatim) → census RED on any caps label.
- **Ledger:** none

### LLR-RVS.2.1 — FEEDS IT rows
- **Statement:** The `feeds it` section shall list `RelMap.up(focused)` in edge input order, one row per neighbour as `↑1 <edge type> <neighbour id><glyph>` — hop marker and edge type in VIOLET, neighbour id INK coerced through `plain` — where the edge type and glyph come from the connecting `Edge` looked up in `RelMap.edges` between the focused node and the neighbour.
- **Traces to:** HLR-RVS.2
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_sheet.py`
- **Draft-time verification:** `up` `mapper/relmap/model.py:200-202`; `edges` `:177`; VIOLET `mapper/darkside.py:25,58`; row grammar `view_sheet.py:48-53`.
- **Negative control:** M-RVS-3 (look the edge up in the wrong direction) → row-content oracle RED on an asymmetric-edge fixture.
- **Ledger:** none

### LLR-RVS.2.2 — A CHANGE REACHES rows
- **Statement:** The `a change reaches` section shall list `RelMap.down(focused)` in edge input order as `↓1 <edge type> <neighbour id><glyph>`, same assembly rules as LLR-RVS.2.1 with the `↓1` marker.
- **Traces to:** HLR-RVS.2
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_sheet.py`
- **Draft-time verification:** `down` `mapper/relmap/model.py:204-206`; direction semantics R1 LLR-RMM.2.1 (`refines` change-downstream; `verifies`/`binds`/`covers` upstream).
- **Negative control:** M-RVS-4 (swap up/down between the sections) → both row tests RED on an asymmetric fixture.
- **Ledger:** none

### LLR-RVS.2.3 — Evidence-state glyph column
- **Statement:** Each neighbour row shall carry exactly one evidence glyph by edge type: `refines` (evidence not required, MAP-TYPES §3.3) carries none; `verifies`/`covers` carry `✓` in SAGE when the edge is evidenced and `!` in ALERT when `evidence_missing` or `in_cycle`; `binds` carries the graduated `●` in SAGE when evidenced and `◐` in WARN when `evidence_missing`; the `○` no-binds-edge badge is a matrix row badge and shall not appear on sheet rows.
- **Traces to:** HLR-RVS.2
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_sheet.py`
- **Draft-time verification:** `Edge.evidence_missing`/`in_cycle` `mapper/relmap/model.py:52-58`; graduated semantics MAP-TYPES §3.2; tokens `mapper/darkside.py:18-23,59-61`; PNG rows `↑1 VERIFIES LLR-N16.2.1 !`, `↓1 BINDS AT-062 ●`. The `◐` WARN tone is one of the three WARN-scoped signals (lens gauge, `not computed`, this glyph) — no other sheet chrome uses WARN (`LED-2026-10-25-r2.05`).
- **Negative control:** M-RVS-5 (glyph keyed on the neighbour's kind instead of the edge state) → table RED on a disagreeing fixture.
- **Ledger:** LED-2026-10-25-r2.05; LED-2026-10-25-r2.22

### LLR-RVS.2.4 — Honest empty sections
- **Statement:** Both neighbour sections and the gaps section shall always paint their band, and a section with zero rows shall paint one declared empty line `╌╌ none on record` in MUT immediately under its band instead of rendering nothing.
- **Traces to:** HLR-RVS.2
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_sheet.py`
- **Draft-time verification:** empty-line grammar ported from `view_sheet.py:62-63,79-80` (hatch `╌` at `:19`), copy lowercased per LLR-RVS.1.2; FAINT is not a Darkside token — MUT used (`mapper/darkside.py:15,52`); QuickMap omits empty sections (`view_sheet.py:105-107`) — declaring them is the Darkside-honesty deviation (OQ-SHEET-3 accepted).
- **Negative control:** M-RVS-6 (skip an empty section) → the empty-state arm RED on a sink/leaf-node fixture.
- **Ledger:** none

### LLR-RVS.3.1 — The declared hop-2 cuts
- **Statement:** In direct density the `feeds it` section shall end with the cut line `╌╌ +NN more upstream at hop 2 — c shows the chain` — two hatch chars, space, `+` and the hop-2 upstream count zero-padded to two digits, lowercase words, em-dash — where the count is the number of distinct nodes whose minimum up-distance from the focused node is exactly 2; the `a change reaches` section shall carry the symmetric `╌╌ +NN more downstream at hop 2 — c shows the chain` at a non-zero count; and each line shall be omitted when its count is 0.
- **Traces to:** HLR-RVS.3
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_sheet.py`
- **Draft-time verification:** exact PNG text `╌╌╌╌ +01 more upstream at hop 2 — c shows the chain` at both widths (the PNG's four hatch chars and lowercase words govern, OQ-SHEET-1 accepted; the downstream symmetry is OQ-SHEET-2 accepted); counting via `neighbourhood(focused, 2) − neighbourhood(focused, 1)` filtered to up-reachable (behavioural spec, implementation-free); `neighbourhood` `mapper/relmap/model.py:229-245`; on today's skeleton every count is 0 (one-hop `refines` chains) — the `+01` arm needs a synthetic 3-level fixture.
- **Negative control:** M-RVS-7 (count hop-2 nodes reachable through either direction) → the count disagrees with the independent up-only oracle.
- **Ledger:** LED-2026-10-25-r2.25

### LLR-RVS.3.2 — Stacked density, the full chain
- **Statement:** In stacked density the two sections shall list every distinct node reachable from the focused node through `up` (feeds it) or `down` (a change reaches) respectively, each row marked with its minimum-hop marker `↑N`/`↓N` (N ≥ 1), ordered by hop then edge input order, with direct rows unchanged from direct density; a node reachable from both directions renders under both sections; computation shall go through the D3 query surface (`up`/`down` layering or `neighbourhood(focused, k)` for the focused node only), never by walking renderer-private adjacency.
- **Traces to:** HLR-RVS.3
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_sheet.py`
- **Draft-time verification:** `neighbourhood` semantics `mapper/relmap/model.py:229-245`; R1 note "a view calls it for the focused node only"; stacked evidence `↑2 REFINES HLR-N16.1` in `sheet-stacked.png`; depth is unbounded minimum-hop with the counted-line rule (LLR-RVS.6.2) as the safety valve (OQ-SHEET-6 accepted).
- **Negative control:** M-RVS-8 (hop marker shows BFS depth through both directions mixed) → markers disagree with per-direction minimum hops on a diamond fixture.
- **Ledger:** LED-2026-10-25-r2.25

### LLR-RVS.3.3 — The `c` density toggle and its declarations
- **Statement:** Pressing `c` on the sheet view shall toggle direct ↔ stacked density (default direct), and the density shall be declared in the view tag — crumb `reqharness / relmap / sheet · direct only` ↔ `… · stacked chain` — and in the `next ▸` note line rendered through `darkside.hint_line`: direct `direct feeders only — the chain is one key away, and the cut is declared`, stacked `feeds it and a change reaches come free from the engine (§3.4 C12)`; the key binding and crumb slot are host-owned (RVH), the density state and note text are renderer-owned (RVS), split per the host↔renderer surface frozen at the R2 design review.
- **Traces to:** HLR-RVS.3
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_sheet.py`
- **Draft-time verification:** `hint_line` `mapper/darkside.py:386-392`; both note strings and crumb tags verbatim in the sheet PNGs; `c` named in US-RMV-003 and the keybar of every relmap PNG.
- **Negative control:** M-RVS-9 (toggle flips the note but not the row set) → the AT-141 arm sees direct rows under a `stacked chain` tag.
- **Ledger:** LED-2026-10-25-r2.20

### LLR-RVS.4.1 — Gaps on this node
- **Statement:** The `gaps on this node` band shall list every gap from the host-supplied gap rows whose subject equals the focused node id, in detection order, as `! <kind>  <sentence>` with the kind in bold ALERT and the sentence in ASH/MUT, both coerced through `plain` and cut to the row width with one trailing ellipsis; the gap rows are consumed as given (the sheet neither re-ranks nor re-detects), and a `Gap.reach` of 0 — the honest value on today's skeleton — is not displayed on this view.
- **Traces to:** HLR-RVS.4
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_sheet.py`
- **Draft-time verification:** `Gap` shape `mapper/relmap/gaps.py:36-42`; sentence templates `mapper/relmap/profile.py:93-108`; ellipsis cut via `darkside.fit` (`mapper/darkside.py:602-621`).
- **Negative control:** M-RVS-10 (filter gaps by severity instead of node) → another node's gap appears or nothing shows.
- **Ledger:** none

### LLR-RVS.5.1 — Markup-safety sink (C8/C-17)
- **Statement:** The sheet painters shall route every canon-derived string through `darkside.plain` and assemble labels as `rich.text.Text` with explicit style tokens (or a `markup=False` sink), so a payload containing `[`, `]`, ESC or control characters renders byte-literal, paints no unintended style span, and raises no markup parse error; `base.py` is the single assembly point the renderers use, so the sink is one seam.
- **Traces to:** HLR-RVS.5
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_sheet.py`
- **Draft-time verification:** `plain` incl. `_CONTROL_MAP` `mapper/darkside.py:550-561`; dual-guard precedent `mapper/screens/draft_guard.py:54-63`, `mapper/screens/common.py:213,260-265`; canvas explicit styles `mapper/canvas.py:114-130,207-237`. Width cuts apply to the COERCED string; coercion is never applied to a previously fitted label (the C-10 order — `LED-2026-10-25-r2.06`).
- **Negative control:** the hostile arm itself (M-RVS-1 family) turns any raw-sink mutation RED; asserted at AT-144.
- **Ledger:** LED-2026-10-25-r2.06

### LLR-RVS.6.1 — Width discipline at 118 and 87
- **Statement:** Every row the sheet paints shall fit the canvas width exactly with `darkside.fit` (pad or single-ellipsis cut), at both (118, 34) and (87, 34); with the C10 audit hook armed during the acceptance run the audit mapping shall record zero `clip` and zero `overprint` entries for the painted frame.
- **Traces to:** HLR-RVS.6
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_sheet.py`
- **Draft-time verification:** `fit` contract `mapper/darkside.py:602-621`; C10 hook `mapper/canvas.py:85-130`; 87-col evidence `png87/sheet-direct.png`; sweep convention `tests/test_scalecheck.py:27`.
- **Negative control:** M-RVS-11 (paint the raw title instead of `fit(title, w)`) → the 87-col arm RED (clip entry or wrapped row).
- **Ledger:** LED-2026-10-25-r2.19

### LLR-RVS.6.2 — Overflow is counted, never silent
- **Statement:** When the sheet's rows exceed the viewport height the painter shall paint rows to the last visible line and replace the remainder with one counted line `… +NN more` in MUT, so no row is dropped without a count; the exact wording is RVT-owned (`relmap/text.py`, US-RMV-005) and the sheet consumes it through the single leaf.
- **Traces to:** HLR-RVS.6
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_sheet.py`
- **Draft-time verification:** QuickMap lineage `view_sheet.py:122-128`; overflow reachable in stacked density on an HLR with many LLRs; RVT ownership per US-RMV-005.
- **Negative control:** M-RVS-12 (drop rows past the viewport with no counted line) → the many-LLR arm RED.
- **Ledger:** LED-2026-10-25-r2.09, LED-2026-10-25-r2.10 (the cap-scale arm and the
  black-box arms of AT-141/AT-143 assert the counted line on the real screen);
  LED-2026-10-25-r2.19 (the renderer default-body convention)

### LLR-RVS.7.1 — Read-only evidence labels
- **Statement:** The sheet shall render evidence and source references as plain text labels only and shall never open, launch or link them: `mapper/screens/relmap/sheet.py` (and its `base.py` painters) shall contain no `osopen` import or call and no clickable attachment construction.
- **Traces to:** HLR-RVH.2 (re-traced from HLR-RVS.2 by `LED-2026-10-25-r2.04` — the
  read-only posture substance belongs to the shell family)
- **Validation method:** inspection (AST/grep census in the asserting test) · **Asserting tests:** `tests/test_relmap_sheet.py`
- **Draft-time verification:** batch contract ("read-only: evidence names are labels, not openable attachments in R2"); MAP-TYPES §6.2 read-only posture; census idiom per US-RMV-005.
- **Negative control:** the census itself — any later `osopen` import in the module turns it RED.
- **Ledger:** LED-2026-10-25-r2.04

### LLR-RVH.1.1 — Home enumerates `*.relmap.yml` beside `*.mmd`
- **Statement:** Home's recents build shall enumerate `sorted(workspace.glob("*.relmap.yml"))` together with the existing `sorted(workspace.glob("*.mmd"))` and shall render one table row per map across both patterns.
- **Traces to:** HLR-RVH.1
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_shell.py`
- **Draft-time verification:** `mapper/screens/home.py:209` (single enumeration site per MAP-TYPES §6.2); table `mapper/screens/home.py:300`; rows with `key=map_name` `:369-374`.
- **Negative control:** M-RVH-1 — glob only `*.mmd` → the relation row absent; AT-145 arm 1 RED.
- **Ledger:** LED-2026-10-25-r2.26; LED-2026-10-25-r2.27

### LLR-RVH.1.2 — Kind badge values and Darkside casing
- **Statement:** The kind cell of a tree row shall keep its existing values (`legacy` or `concept`, chip style `INK on STEP`), and the kind cell of a relation row shall read exactly `relation·reqharness` in the same chip style, in Darkside casing (no ALL-CAPS).
- **Traces to:** HLR-RVH.1
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_shell.py`
- **Draft-time verification:** tree chip precedent `mapper/screens/home.py:352-358` (`Text.assemble((f" {kind} ", f"{darkside.INK} on {darkside.STEP}"))`); tokens `mapper/darkside.py:48-57`; Solari ALL-CAPS rejected (operator note).
- **Negative control:** M-RVH-2 — badge rendered ALL-CAPS → character-exact census RED.
- **Ledger:** none

### LLR-RVH.1.3 — Listing order: one list, sorted by name across kinds
- **Statement:** The recents table shall present tree and relation maps in one list sorted by map name regardless of kind, with the kind badge — not list position — as the kind distinguisher.
- **Traces to:** HLR-RVH.1
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_shell.py` (order arm)
- **Draft-time verification:** sort site `mapper/screens/home.py:209`; MAP-TYPES §6.2 "keeps recents/hero as they are". Orchestrator ruling: the recommended answer is ACCEPTED (OQ-R2) — one name-sorted list; the badge distinguishes kinds.
- **Negative control:** M-RVH-3 — relation rows appended after all tree rows → order arm RED.
- **Ledger:** none

### LLR-RVH.2.1 — Open routing by kind
- **Statement:** Pressing the seat's open key on a relation row shall push `RelMapScreen` for that descriptor, and on a tree row shall push `MapScreen(map_id)` exactly as today.
- **Traces to:** HLR-RVH.2
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_shell.py`
- **Draft-time verification:** tree route `mapper/screens/home.py:455-458`; row value → name `:412-417`; seat open binding `mapper/keymap.py` (`enter` → `open_selected`). `RelMapScreen` does not exist on disk yet — path `mapper/screens/relmap/screen.py` per the ARQ commitment (planned, not assumed: first verified when trunk Inc-2 lands, its gate entry).
- **Negative control:** M-RVH-4 — relation row routed to `MapScreen` → pilot assert on the active screen RED.
- **Ledger:** LED-2026-10-25-r2.26

### LLR-RVH.2.2 — The relation screen is read-only
- **Statement:** The relmap scope shall bind no draft, save, archive, edit, or `osopen`-launch action, and the relation screen shall implement no write path to the store.
- **Traces to:** HLR-RVH.2
- **Validation method:** inspection · **Asserting tests:** `tests/test_relmap_shell.py` (BINDINGS census over SCOPE_RELMAP)
- **Draft-time verification:** write-action vocabulary from the map scope groups `mapper/keymap.py:69-72,188-198`; MAP-TYPES §6.2 read-only posture.
- **Negative control:** M-RVH-5 — any write action added to a relmap group → the BINDINGS census RED.
- **Ledger:** none

### LLR-RVH.2.3 — No store or `mapper.db` change
- **Statement:** Opening or refreshing a relation map shall derive the map in memory from canon and descriptor and shall make no call that writes `mapper.db` or any tree store table.
- **Traces to:** HLR-RVH.2
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_shell.py`
- **Draft-time verification:** derive entry point `mapper/relmap/adapter.py:121`; recompute-on-open ruling R-019 (no `mapper.db` schema change in this batch).
- **Negative control:** M-RVH-6 — open path persists derived nodes → instrumented save-count arm RED.
- **Ledger:** none

### LLR-RVH.3.1 — The default descriptor derives the map when none exists
- **Statement:** When the workspace holds no `*.relmap.yml`, Home shall list one derived relation row named by the canon stem (`requirements` for `REQUIREMENTS.md`) whose map is produced by `derive_reqharness_map(workspace, default_descriptor())`, and opening that row shall land on the relation screen with that derivation; when descriptors exist, each descriptor is one row and the derived row does not appear. The derived row is listed only while the default canon's file is present at the workspace root; a workspace with no descriptor and no canon lists tree rows only (AT-145 boundary (a)) (`LED-2026-10-25-r2.29`).
- **Traces to:** HLR-RVH.3
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_shell.py`
- **Draft-time verification:** `mapper/relmap/descriptor.py:94-95` (`default_descriptor()`); `descriptor.py:200-208` (`discover_descriptors`, at most 8, sorted, overflow count); schema truth table R1 LLR-RML.1.2. The workspace-as-repo seam is RULED, not assumed
(`LED-2026-10-25-r2.03`; executed probe 2026-10-25, `evidence/p2-seam-workspace-repo.md`):
the descriptor and canon resolve relative to the workspace root — `Path(workspace)/canon`
(`mapper/relmap/adapter.py:129`), flat `os.listdir(workspace)` discovery
(`mapper/relmap/descriptor.py:200-208`) — git is never consulted on this path, and a
missing or unreadable canon surfaces the closed-set `unavailable` cause, never a crash.
The rule is pinned in LLR-RVH.3.3.
- **Negative control:** M-RVH-7 — the no-descriptor arm derives with a hard-coded non-default descriptor → the derivation-args probe RED.
- **Ledger:** LED-2026-10-25-r2.03; LED-2026-10-25-r2.26; LED-2026-10-25-r2.29

### LLR-RVH.3.2 — Recompute-on-open and `r` refresh
- **Statement:** The relation screen shall derive its map at open time and shall re-derive it from the same descriptor and canon when the operator presses `r`, and the refreshed map shall replace the rendered state of all three views.
- **Traces to:** HLR-RVH.3, HLR-RVH.4
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_shell.py`
- **Draft-time verification:** R-019; derive seam `mapper/relmap/adapter.py:121`; `RelMap.visits` gives a visible per-derivation observable (`mapper/relmap/model.py:193-194`).
- **Negative control:** M-RVH-8 — `r` re-renders from the cached derivation without calling `derive_reqharness_map` → the monkeypatched derive-count arm RED.
- **Ledger:** none

### LLR-RVH.3.3 — Workspace-as-repo: the canon resolves at the workspace root
- **Statement:** When Home or the relation screen derives the relation map from a workspace, the descriptor and canon paths shall resolve relative to the workspace root passed to the app — never against the process working directory and never through an upward search — the derivation shall not require the workspace to be a git repository, and when the canon is missing or unreadable the derivation shall yield the closed-set `unavailable` cause (K1–K17, e.g. K3 `file not found`, K7 `is not UTF-8 text`) so the shell renders the fixed refusal line — the app shall remain alive and shall never crash on a non-repo or canon-less workspace.
- **Traces to:** HLR-RVH.3
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_shell.py`; AT-147 workspace-as-repo arm
- **Draft-time verification:** executed probe 2026-10-25 (`evidence/p2-seam-workspace-repo.md`, ruling `LED-2026-10-25-r2.03`): a bare (non-git) directory with a valid canon derives cleanly and byte-identically with no `.git`, an empty `.git`, or a real `git init`; a missing canon raises `CanonUnavailable(cause='file not found')` (K3) which the shell path renders as the `unavailable` refusal state, not an exception; the resolution base is `Path(workspace)/"REQUIREMENTS.md"` (`mapper/relmap/adapter.py:129`) with flat `os.listdir(workspace)` descriptor discovery (`mapper/relmap/descriptor.py:200-208`) — no `.git` consultation exists on this path. Scope note: the R1-frozen `--audit` CLI hook's own git gating (`structure: unavailable (no repository)`, `mapper/reqharness/audit.py:378-379`) is the RVU/D4 surface and is NOT governed by this LLR.
- **Negative control:** M-RVH-16 — make the screen derivation consult `.git` / require a repository → the non-repo fixture arm fails; RED. M-RVH-17 — let the raw exception escape on a missing canon instead of the closed-set cause → the app-lives arm RED.
- **Ledger:** LED-2026-10-25-r2.03

### LLR-RVH.4.1 — The additive `relmap` keymap scope
- **Statement:** The seat shall declare `SCOPE_RELMAP = "relmap"`, register its groups in `GROUP_SCOPE` and `GROUP_HEADER`, and bind exactly: `1`/`2`/`3` to the matrix/gaps/sheet view switch, the cursor keys to selection movement, `enter` to the lens focus, `c` to the chain toggle, `k` to the by-kind grouping toggle, `r` to refresh, `q` to leave and `escape` as a quiet leave alias, with no chord bound twice inside the scope; and the view-specific chords (`enter`/`c`/`k`) shall be inert no-ops when the active view is not their home view — or at most flash the crumb note — never acting on a non-home view, per the operator-approved static bar (COND-UX-1).
- **Traces to:** HLR-RVH.4
- **Validation method:** test · **Asserting tests:** `tests/test_keymap.py` (additive SCOPE_RELMAP conformance); the AT-148 out-of-view arm (`01b-acceptance-design.md`)
- **Draft-time verification:** scope constants `mapper/keymap.py:27-41`; uniqueness rule `:25` + `duplicate_chords()` `:488` (`LLR-N03.6` — citations repaired per COND-ARCH-3, re-repaired per COND-DDR-1 at the P5 records pass, `LED-2026-10-25-r2.32`); `KeyBinding` shape `:139-152`; `q`/`esc` leave precedent in map scope `:230-231`; app-scope `?`/`ctrl+p` inherited by every scope via `bar_group_order` `:127-131,317-321`. The `k` binding is now normative in the Statement above;
the seat addition is part of this trunk increment —
the keymap single seat gates `BINDINGS` before the lanes fork (ARC-02 move
`LED-2026-10-25-r2.08`). The out-of-view inert clause is design-narrative level: any richer
answer is a seat change and trunk-owned.
- **Negative control:** M-RVH-9 — a second binding on one chord in the scope → uniqueness conformance RED. M-RVH-19 — a view-specific chord (`enter`/`c`/`k`) acting on a non-home view (or leaving home-view state reachable off-home) → the AT-148 out-of-view arm RED.
- **Ledger:** LED-2026-10-25-r2.01, LED-2026-10-25-r2.08, LED-2026-10-25-r2.12, LED-2026-10-25-r2.15, LED-2026-10-25-r2.17, LED-2026-10-25-r2.32 (the COND-DDR-1 re-repair of this block's drifted draft-time citations, records-only)

### LLR-RVH.4.2 — The screen's BINDINGS and keybar come from the seat
- **Statement:** `RelMapScreen` shall set `KEY_SCOPE = SCOPE_RELMAP`, generate `BINDINGS` via `screen_bindings(SCOPE_RELMAP)`, and paint the keybar from `keybar_groups(SCOPE_RELMAP)` through `groups_for_keybar`, so the bar, the palette and the help legend read the same seat rows.
- **Traces to:** HLR-RVH.4
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_shell.py`
- **Draft-time verification:** `mapper/screens/common.py:184-203`; `mapper/keymap.py:385-408`; precedent `mapper/screens/map/screen.py:22,26,169`.
- **Negative control:** M-RVH-10 — a hand-written binding on the screen outside the seat → seat-equality RED.
- **Ledger:** LED-2026-10-25-r2.08 (trunk-owned per the ARC-02 move)

### LLR-RVH.4.3 — Compose, crumb, and view switching through the frozen surface
- **Statement:** `RelMapScreen` shall compose a `TabStrip` crumb naming the descriptor (or derived entry) and the active view, a `KeyBar`, and one view canvas; pressing `1`/`2`/`3` shall swap the active renderer among matrix, gaps and sheet by calling the host↔renderer surface frozen at the R2 PDR, and the crumb shall name the active view after each switch; the crumb's toggle-state word shall be the ACTIVE view's own word — the host stores each view's word per view, so switching views never shows another view's word and switching back restores it.
- **Traces to:** HLR-RVH.4
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_shell.py`
- **Draft-time verification:** crumb precedent `mapper/screens/map/screen.py:150-152`; chrome widgets `mapper/widgets/chrome.py:40,87`; prototype crumb `reqharness / relmap / matrix · panel lens` and bottom bar. The host↔renderer surface itself is frozen at the R2 PDR (this LLR pins only that switching crosses it).
- **Negative control:** M-RVH-11 — `2` swaps the canvas without updating the crumb → crumb assert RED; the per-view word rule: a crumb that paints another view's toggle word (or drops the restored word on return) → the Inc-2 review arms RED.
- **Ledger:** LED-2026-10-25-r2.18 (the per-view crumb-word ruling from the Inc-2 independent review); LED-2026-10-25-r2.20

### LLR-RVH.4.4 — Help and palette carry the relmap scope
- **Statement:** The help overlay opened from the relation screen shall render the `SCOPE_RELMAP` entries, and the command palette shall offer the relmap actions, both derived from the seat with no hand-written entries.
- **Traces to:** HLR-RVH.4
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_shell.py`
- **Draft-time verification:** `mapper/app.py:274-296` (`action_palette` pushes `CommandPalette(scope)`; `action_help` reads the screen's `KEY_SCOPE` — a `KEY_SCOPE` is sufficient, no app change required; closed when Inc-2 lands the host and 6b asserts it, AT-149); `mapper/screens/help.py:223`; `mapper/screens/palette.py:36`; `mapper/keymap.py:475` (`palette_items` — the phantom `screens/palette.py:432` citation repaired per COND-UX-3, `LED-2026-10-25-r2.17`; the line re-repaired per COND-DDR-1 at the P5 records pass, `LED-2026-10-25-r2.32`).
- **Negative control:** M-RVH-12 — a hand-added help row → help-vs-seat equality RED.
- **Ledger:** LED-2026-10-25-r2.17, LED-2026-10-25-r2.32 (the COND-DDR-1 re-repair of this block's drifted draft-time citation, records-only)

### LLR-RVH.5.1 — Refusal path: fixed refusal line, no crash
- **Statement:** When a descriptor fails `load_descriptor` or the canon fails `derive_reqharness_map`, the shell shall show the fixed refusal line from the presentation leaf (`refusal_line(base_name, cause)`; RVT-owned wording) as its notice and shall leave Home and the app running; the refusal text shall come from the closed cause set and shall never be `str(exc)`, a path, an anchor name or a YAML snippet.
- **Traces to:** HLR-RVH.5
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_shell.py`
- **Draft-time verification:** `mapper/relmap/descriptor.py:211-216` (`refusal_line`, base cut to 120 — moves to the RVT leaf); `DescriptorError`/`RepoReadError` `:63-83`; `CanonUnavailable` `mapper/relmap/adapter.py:43-46`; toast-without-path precedent `mapper/screens/home.py:465-471`, `_refusal_toast` `mapper/screens/common.py:205-213`.
- **Negative control:** M-RVH-13 — refusal path renders `str(exc)` → closed-set census RED; M-RVH-14 — refusal path re-raises → app-lives arm RED.
- **Ledger:** LED-2026-10-25-r2.26; LED-2026-10-25-r2.28

### LLR-RVH.5.2 — Markup-safety sink for host-rendered canon/descriptor text
- **Statement:** Every label the host renders that carries descriptor- or canon-derived text (derived-entry name, crumb name, refusal notice, badge) shall be assembled markup-safe — via `darkside.plain(...)`, pre-escaped content with `markup=False`, or explicit-style `Text` — so a bracket, ESC or control-character payload renders literally with no style leak and no markup parse error.
- **Traces to:** HLR-RVH.5
- **Validation method:** test · **Asserting tests:** `tests/test_relmap_shell.py`
- **Draft-time verification:** the frozen four-sink seam is `darkside._row_text`/`fit` — `plain` + LF/TAB/CR → single space (`mapper/darkside.py:576-621`, COND-SEC-1, `LED-2026-10-25-r2.14`); bare `plain` preserves LF/TAB by design (`mapper/darkside.py:550-561`), which is why the seam is the `_row_text`/`fit` wording and not `plain` alone; precedent `mapper/screens/draft_guard.py:57`, `mapper/screens/common.py:213,264`; name escape precedent `mapper/screens/home.py:109,370`; hostile fixture pattern R1 AT-122 arm 3 + the R2 LF/TAB arms (P12, `01-requirements.md:261`).
- **Negative control:** M-RVH-15 — host label assembled with f-string markup on raw descriptor text → the hostile arm RED. M-RVH-18 — a sink that lets LF/TAB through unpainted-as-space → the AT-148 one-row hostile arm RED.
- **Ledger:** LED-2026-10-25-r2.14; LED-2026-10-25-r2.26

### LLR-RVT.1.1 — One definition site per presentation primitive
- **Statement:** `mapper/relmap/text.py` shall define `cut(text: str) -> str`, `DISPLAY_MAX` and `refusal_line(base_name: str, cause: str, limit: int | None = None) -> str`, and `mapper/relmap/model.py`, `descriptor.py`, `adapter.py` and `audit.py` shall import these names from `text` and shall not define or re-export any of them.
- **Traces to:** HLR-RVT.1
- **Validation method:** test — AST census · **Asserting tests:** `tests/test_relmap_text.py` (planned); `tests/test_relmap_isolation.py` re-counted
- **Draft-time verification:** current locations `mapper/relmap/model.py:34,67-71` (`DISPLAY_MAX`, `cut`), `mapper/relmap/descriptor.py:211` (`refusal_line`); the four importing modules per the ARCHITECTURE internal-ordering amendment; census derived from the ASTs (C-31), not hand-listed. The re-points land in two trunk increments per the orchestrator ruling at the PDR seal (COND-ARCH-2/COND-QA-1, `LED-2026-10-25-r2.16`): Inc-1a re-points `model`/`descriptor`/`audit` (and drops the `audit.__all__` re-export); Inc-1b re-points `adapter` (`adapter.py:29` today imports `cut` from `model`).
- **Negative control:** M-RVT-1 — a second `def cut` left behind in `model.py` → the definition-site count is 2; RED.
- **Ledger:** LED-2026-10-25-r2.16

### LLR-RVT.1.2 — One import path for `refusal_line`; consumers re-pointed in the same increment
- **Statement:** The `mapper/relmap/audit.py` re-export of `refusal_line` (its `__all__` line) shall be dropped, every consumer and test shall import `refusal_line` from the leaf, and a reader census over the old import paths (`relmap.model.cut`, `relmap.model.DISPLAY_MAX`, `relmap.descriptor.refusal_line`, `relmap.audit.refusal_line`) shall find zero remaining references in the increment that re-points each reader — per the orchestrator ruling at the PDR seal the move is two trunk increments, each byte-identical at exit (COND-ARCH-2/COND-QA-1, `LED-2026-10-25-r2.16`): Inc-1a re-points `model`/`descriptor`/`audit` and drops the `audit.__all__` re-export (census zero over `relmap.model.DISPLAY_MAX`, `relmap.descriptor.refusal_line`, `relmap.audit.refusal_line`; the one remaining old-path reader `relmap.model.cut` at `mapper/relmap/adapter.py:29` is declared to Inc-1b); Inc-1b re-points `adapter` (census zero over `relmap.model.cut`).
- **Traces to:** HLR-RVT.1
- **Validation method:** test — grep census · **Asserting tests:** `tests/test_relmap_text.py` (planned); `tests/test_relmap_isolation.py` re-counted
- **Draft-time verification:** the double path today: `mapper/relmap/audit.py:34` (import) + `:209-210` (`__all__` re-export); nothing pins which path tests use (DDR §E 11); reader-census idiom per the B1 family.
- **Negative control:** M-RVT-2 — one test still imports `refusal_line` from `mapper.relmap.audit` (the live old path the census names is `mapper.relmap.descriptor`, the double path `descriptor` vs `audit.__all__` being collapsed) → the census RED.
- **Ledger:** LED-2026-10-25-r2.11 (the three re-pointed R1 test files enumerated in PLAN Inc-1a; the census names the descriptor path), LED-2026-10-25-r2.16

### LLR-RVT.1.3 — The move changes no rendered byte
- **Statement:** The moved `cut`, `DISPLAY_MAX` and `refusal_line` shall reproduce the R1 behaviour exactly — the refusal-line rendering, the 120-character value cut and the prescan-golden surfaces stay byte-identical — verified on the base before the edit and on the result after it.
- **Traces to:** HLR-RVT.1
- **Validation method:** test — byte-identity probe · **Asserting tests:** `tests/test_relmap_text.py` (planned); the R1 suite `tests/test_relmap_*.py` + `tests/test_prescan_refusal_goldens.py` green unchanged
- **Draft-time verification:** behaviour contracts: `mapper/relmap/model.py:67-71` (`cut` at `DISPLAY_MAX` with one-ellipsis ending), `mapper/relmap/descriptor.py:211-216` (refusal format, base cut to 120); golden precedent (capture-on-base before the edit): R1's D6/D7 pattern (`tests/test_prescan_refusal_goldens.py`, snapshot sha256 pin).
- **Negative control:** M-RVT-3 — the moved `cut` drops the ellipsis → the byte-identity probe and the R1 snapshot arms RED.
- **Ledger:** none

### LLR-RVU.1.1 — Per-line bound on hook lines after the escape pass
- **Statement:** In the `run_cli` hook path, after a hook line has been escaped by the report escaper, any line longer than the per-line bound of 240 characters (ruling `LED-2026-10-25-r2.02`) shall be cut at 239 with one trailing ellipsis, the cut shall never split an escape spelling — if the 239-character boundary lands inside a `\xNN` or `\uXXXX` spelling, the cut shall back to the spelling start — and the cut shall never re-expose a `verdict: ` prefix to line start; the line-count bound, the `verdict: ` prefix rewrite, the fixed no-repo/no-registry lines and the exit code shall remain exactly as `PDR-2026-10-25-relmap-r1-batch#D4` froze them.
- **Traces to:** HLR-RVU.1
- **Validation method:** test · **Asserting tests:** `tests/test_hook_line_bound.py` (AT-152 · TC-RM-30) + `tests/test_relmap_audit.py` (the R1 snapshot arms as amended by `LED-2026-10-25-r2.30` — qualifier content asserted on the D5 `structure_lines` seam, the bound asserted on the emitted form)
- **Draft-time verification:** hook path `mapper/reqharness/audit.py:372-383` (`_hook_lines`, `islice(…, HOOK_LINE_LIMIT + 1)`), `:430-431` (print loop); count bound `:82` (`HOOK_LINE_LIMIT = 1000`); escape pass: the lines are printed through the report's escaper (R1 LLR-RMU.1.2 sink contract). The bound value 240 and the C-42 order (cut after escaping, predicate over the EMITTED form) are RULINGS (`LED-2026-10-25-r2.02`), measured against the R1 worst-case line (≈298 lines report, refusal line cut at 120 — premise P10/P11); the PDR freezes only the ellipsis glyph. The P10/P11 premise note is SUPERSEDED in its measurement scope per `LED-2026-10-25-r2.30` (it covered the refusal line (120) and the report length (≈298 lines), not the longest `structure_lines` sentence — the two 271/277-cell R1 snapshot gap lines; the PDR's risk #6 carried exactly this contingency).
- **Negative control:** M-RVU-1 — cut before escaping (byte-counting escape sequences) → an arm with escapes near the boundary sees a miscounted line; RED. M-RVU-2 — the cut re-exposes `verdict: ` → the prefix-exclusivity arm RED. M-RVU-3 — cut inside an escape spelling instead of backing to its start → the AT-152 straddling-payload arm RED.
- **Ledger:** LED-2026-10-25-r2.02, LED-2026-10-25-r2.30

### Information Flow Contract (IFC) — C-54

**Part A (Flow).** Every information flow names SOURCE → NODES → SINK, each node with its owner LLR.

```
FLOW: rm-map-to-view (matrix)
  SOURCE : RelMap (D3, PDR-2026-10-25-relmap-r1-batch#D3) + host MatrixState (select, focus)
  NODES  :
    - fn    : row/window assembly (rows, labels, paging)
      owner : LLR-RVM.1.1
    - fn    : window declarations, ruler and legend
      owner : LLR-RVM.1.3
    - fn    : cell painter (one glyph per pair, strongest edge wins)
      owner : LLR-RVM.1.2
    - fn    : neighbourhood dimming while focus is on
      owner : LLR-RVM.2.3
    - fn    : lens rows (rings, hop markers, evidence states)
      owner : LLR-RVM.2.1
    - fn    : lens summary and reach gauge
      owner : LLR-RVM.2.2
    - fn    : markup-safe label assembly (base.py)
      owner : LLR-RVM.4.2
    - fn    : Canvas + C10 audit
      owner : LLR-RVM.4.1
  SINK   : the host body Static (screen.py) + the C10 audit dict (test-only)

FLOW: rm-graph-to-gaps-screen
  SOURCE : RelMap in memory
  NODES  :
    - fn    : detect_gaps/rank_gaps (R1-owned) consumed read-only
      owner : LLR-RVG.1.1
    - fn    : gaps header, tally chips and field band
      owner : LLR-RVG.1.2
    - fn    : row anatomy, cursor on the worst gap, severity tokens
      owner : LLR-RVG.1.3
    - fn    : viewport window, cut markers, WHAT drop rule
      owner : LLR-RVG.1.4
    - fn    : by-kind grouping on `k` (SHIPPED per ruling LED-2026-10-25-r2.01)
      owner : LLR-RVG.1.5
    - fn    : casing transform — kind labels
      owner : LLR-RVG.2.1
    - fn    : casing transform — other chrome
      owner : LLR-RVG.2.2
    - fn    : honest-reach + not-computed marker
      owner : LLR-RVG.2.3
    - fn    : markup-safe label assembly
      owner : LLR-RVG.3.1
  SINK   : RelMapScreen compose (host chrome owned by RVH)

FLOW: rm-node-to-sheet
  SOURCE : RelMap.up/down/edges/node/neighbourhood + host gap rows + host focus/c/binding slots
  NODES  :
    - fn    : header layout over the D3 node
      owner : LLR-RVS.1.1
    - fn    : FEEDS IT section rows
      owner : LLR-RVS.2.1
    - fn    : A CHANGE REACHES section rows
      owner : LLR-RVS.2.2
    - fn    : evidence-state glyph column
      owner : LLR-RVS.2.3
    - fn    : declared hop-2 cuts
      owner : LLR-RVS.3.1
    - fn    : stacked density, the full chain
      owner : LLR-RVS.3.2
    - fn    : the `c` density toggle and its declarations
      owner : LLR-RVS.3.3
    - fn    : gaps on this node
      owner : LLR-RVS.4.1
    - fn    : width discipline at 118 and 87
      owner : LLR-RVS.6.1
    - fn    : overflow counted, never silent
      owner : LLR-RVS.6.2
    - fn    : markup-safe assembly
      owner : LLR-RVS.5.1
  SINK   : RelMapScreen compose (slots host-owned by RVH; surface frozen at the R2 PDR)

FLOW: rm-files-to-home-and-screen (shell)
  SOURCE : workspace dir listing · descriptor file bytes · canon text · seat KEYMAP
  NODES  :
    - fn    : home enumerates `*.relmap.yml` beside `*.mmd`
      owner : LLR-RVH.1.1
    - fn    : kind badge values and Darkside casing
      owner : LLR-RVH.1.2
    - fn    : listing order — one list sorted by name across kinds
      owner : LLR-RVH.1.3
    - fn    : load_descriptor (R1 D2 producer)
      owner : LLR-RVH.5.1
    - fn    : default descriptor derives the map when none exists
      owner : LLR-RVH.3.1
    - fn    : recompute-on-open and `r` refresh
      owner : LLR-RVH.3.2
    - fn    : open routing by kind
      owner : LLR-RVH.2.1
    - fn    : relation screen read-only posture
      owner : LLR-RVH.2.2
    - fn    : no store or `mapper.db` change
      owner : LLR-RVH.2.3
    - fn    : seat scope declaration + chord bindings (SCOPE_RELMAP)
      owner : LLR-RVH.4.1
    - fn    : BINDINGS + keybar generated from the seat
      owner : LLR-RVH.4.2
    - fn    : help + palette from the seat
      owner : LLR-RVH.4.4
    - fn    : host chrome labels (markup-safe)
      owner : LLR-RVH.5.2
  SINK   : #home-recents rows · the pushed RelMapScreen

FLOW: rm-text-leaf (RVT)
  SOURCE : value strings (titles, sentences, base names) inside mapper/relmap
  NODES  :
    - fn    : cut/DISPLAY_MAX/refusal_line definition site in relmap/text.py
      owner : LLR-RVT.1.1
    - fn    : one import path for refusal_line + consumer re-pointing
      owner : LLR-RVT.1.2
    - fn    : byte-identity of the moved primitives
      owner : LLR-RVT.1.3
  SINK   : descriptor refusals, adapter titles, audit lines, and the R2 renderers' value cuts (consumers:
           LLR-RVS.1.1/.4.1/.6.2, LLR-RVG.3.1, LLR-RVM.4.2, LLR-RVH.5.1 — all read through the one leaf)

FLOW: audit-hook-lines (RVU)
  SOURCE : hook producer lines (UNESCAPED, R1 D5)
  NODES  :
    - fn    : escape pass (R1-owned) + per-line cut at the bound
      owner : LLR-RVU.1.1
  SINK   : stdout through run_cli (D4 semantics unchanged)
```

**Part B (boundary decomposition).** The relation screen's boundary has independently addressable
components — a user interface with panels — so each declares PARENT, INPUTS ⊆ PARENT.INPUTS, per-output
`address`/`consumers`/`owner`:

```
COMPONENT RelMapScreen (PARENT: the TUI screen; INPUTS: RelMap, Derivation, seat rows, viewport (w,h))
  - crumb          address "crumb"            consumers: operator (reads)      owner: LLR-RVH.4.3
  - keybar         address "keybar"           consumers: operator              owner: LLR-RVH.4.2
  - matrix region  address "view.1"           consumers: operator, AT-130..134 owner: LLR-RVM.*
  - lens panel     address "view.1.lens"      consumers: operator, AT-131/132  owner: LLR-RVM.2.*
  - gaps region    address "view.2"           consumers: operator, AT-135..139 owner: LLR-RVG.*
  - sheet region   address "view.3"           consumers: operator, AT-140..144 owner: LLR-RVS.*
  - notice/refusal address "notice"           consumers: operator, AT-145..148 owner: LLR-RVH.5.*
  - home rows      address "home.recents"     consumers: operator, AT-145..147 owner: LLR-RVH.1.*
consumers : none — for the C10 audit dict (test-only instrumentation, not an operator surface); every
            component above is INDEXED POSITIONALLY by none (no positional consumers).
```

## 5. Validation strategy

### 5.1 Methods

- **Layer A (white-box, TC-NNN ↔ LLR):** unit painters and censuses per renderer
  (`tests/test_relmap_matrix.py`, `test_relmap_gaps_view.py`, `test_relmap_sheet.py`,
  `test_relmap_shell.py`, `test_relmap_text.py`, `test_hook_line_bound.py`), the AST/grep
  censuses (definition sites, import paths, kind literals, casing, `osopen` absence, seat
  conformance), and the C10 geometry/audit sweeps at (118, 34) and (87, 34).
- **Layer B (black-box, AT-NNN ↔ US):** Textual `run_test()` pilots on the real surface
  (`tests/test_colour_always_on.py:64-70` idiom), driving REAL keys (C-16: no `.focus()`
  proxies), every AT moving a non-default value (C-10), with boundary + negative arms;
  bodies in `01b-acceptance-design.md`.
- **RED counterfactual + reviewer mutants (C-2):** each named negative control (M-RVM/RVM…)
  is the declared reddening mutation for its arm; each independent review records one
  reviewer-authored mutant.
- **Guard set (C-1):** every targeted run includes `tests/test_fold.py` and
  `tests/test_repair_artifact_claims.py`; pre-commit adds `tests/test_no_operator_paths.py`.
  Runs: `PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 python -m
  pytest -q -p no:cacheprovider <files>`, after proving `mapper.__file__` resolves in the
  worktree. Targeted only — the full suite is the P4/orchestrator run, as R1 did.

### 5.2 Batch acceptance criteria

1. All 52 LLRs (20 HLRs) carry at least one asserting on-disk test, per the census
   re-counted by script at the P1 amendment (command and output in the ledger measurement
   `LED-2026-10-25-r2-census`; the pre-amendment artifact held 51 LLRs and the contract
   claimed 26/52 — both corrected) — Phase 3 mints the nodes;
   `AT-130…AT-152` reconcile to collected nodes at Phase 4, V-5 provisional until then.
2. The three views render the operator-verdict layouts at 118×34 with the 87×34 check and a
   zero-unexplained-event C10 sweep.
3. The honest partial map renders without phantom US/AT/TC content on the live worktree canon
   (premise P2 figures, AT-147 census).
4. The text-leaf census finds one definition site and one import path; the R1 suite is green
   unchanged (byte-identity probe).
5. The hook per-line bound is applied after escaping with D4 semantics intact.
6. The security scan (family C) verdict is recorded in §6.3 with every flag answered; the
   hostile-payload arms render literally with no style leak.

## 6. Appendices

### 6.3 Open risks

- **Security pattern scan (family C — C6 + C8 fired):** `devflow-scan-spec.py` run 2026-10-25
  over §§1–4 (89,842 bytes; all 5 control rows ok): `security_required: true`, flags
  `token`, `truncate`, `schema change`, `form`, `escape`, `expose` — all vocabulary
  collisions, answered here per the scanner's instruction: `token` names the Darkside colour
  tokens and the keymap seat data (no credential, session or CSRF token exists); `truncate`
  names the display cut (`cut`/`DISPLAY_MAX`, one-ellipsis width discipline) and the RVU
  per-line bound — presentation operations on already-parsed data, never a database
  truncation; `schema change` names the RULING that `store`/`mapper.db` gain NO relation
  tables (R-019) — the negation of a schema change; `form` names the descriptor's data shape
  and EARS sentence forms, not a web form (no C1/C3/C7 surface); `escape` names the report
  escaper the hook lines pass through (R1 sink contract) and `darkside.plain`'s control-char
  coercion — the C8/C-17 mitigation itself (LLR-RVM.4.2, RVG.3.1, RVS.5.1, RVH.5.2), never
  an escape of a security boundary; `expose` names the module-map "what it EXPOSES" column (a
  public API), not a network endpoint. C6 questions answered: (a) new code surfaces the
  R1-hardened read paths to the screen — every descriptor read goes through the D2-frozen
  `load_descriptor` (prescan K8/K9, byte cap K5, confinement) and the canon through
  `derive_reqharness_map`'s own `lstat` + capped reader; the shell adds NO new file read —
  it consumes those seams and presents refusals (LLR-RVH.5.1); (b) no new boundary crossing:
  workspace file reads only, no network, no subprocess, no OS handler (`osopen` is banned on
  this screen, LLR-RVS.7.1); (c) refusal text is the closed K1–K17 set rendered by the one
  leaf, never `str(exc)`, a path or a YAML snippet. C8 answered: the screens render
  canon-derived text only through the frozen `_row_text`/`fit` seam (plain +
  LF/TAB/CR → single space, COND-SEC-1, `LED-2026-10-25-r2.14`) with hostile-payload AT arms
  per view, the LF/TAB arms asserting the payload renders on ONE row.
- **The host↔renderer surface is not yet frozen.** Three renderer lanes draft against a
  surface that exists only as an ARQ commitment; fork precondition F-2 makes the PDR seal the
  condition of any lane starting. Slippage re-serializes the lanes, it does not silently
  break them.
- **The by-kind toggle SHIPS** (LLR-RVG.1.5 + AT-136 + the `k` binding, ruling
  `LED-2026-10-25-r2.01`); the PDR freezes only the glyph/table details.
- **The two seams once flagged `assumed — verify in Phase 2` are DISCHARGED by executed
  probes** (2026-10-25): the AT-driver host push + fixture injection (fork precondition F-5)
  works on today's code — `MapperApp(workspace=…)` (`mapper/app.py:250`) under a headless
  `run_test()` pilot reaches Home and lists the fixture relation row
  (`evidence/p2-seam-at-driver.md`, ruling `LED-2026-10-25-r2.07`) — and the
  workspace-as-repo derivation path (LLR-RVH.3.1, rule pinned in LLR-RVH.3.3) resolves the
  canon at the workspace root with git never consulted and a closed-set `unavailable` state
  on a missing canon (`evidence/p2-seam-workspace-repo.md`, ruling `LED-2026-10-25-r2.03`).
- **Today's skeleton limits what the views can show:** no test columns (matrix declares it),
  hop-2 chains are one level deep at most, all gaps tie at reach 0, and 7 of 8 catalogue
  kinds are inert until B-141 lands. The views are specified to render this honestly; the
  richer arms run on in-test synthetic maps.
- **The per-line hook bound is RULED at 240**, applied after escaping (the C-42 emitted-form
  order) with a no-mid-spelling cut (`LED-2026-10-25-r2.02`); a wrong bound false-fails long
  refusal/canon lines, which the R1 golden surfaces will catch at the increment gate.
- **B-155 out of scope:** the pre-existing `repo:` absolute-path line in `--audit` prints a
  runner's home directory in shared logs; RVU must not "fix" it silently — it is its own
  backlog row.
