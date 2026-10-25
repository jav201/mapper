# Requirements — mapper — Batch 2026-10-23-hygiene-batch

> **Artifact language:** English. Reserved field names are never translated.
> **Ids are grouped by module:** Q1 (colour) · Q2 (ingestion limits) · Q3 (scalecheck + canvas audit).

## 1. Introduction

### 1.1 Purpose
This document is the live requirements contract for the 2026-10-23 hygiene batch: three small,
independent hardening modules ported as test/loading practices from QuickMap (source brief:
`docs/handoff-mapper/HANDOFF.md` §3 C9, C10, C11, §5 conflicts 2 and 7, §9 verdict Q5), plus the
C11 process habits applied to this batch's own increments.

### 1.2 Scope
- **In:** Q1 colour always on under `NO_COLOR`; Q2 ingestion limits on map-file loading and
  content reads; Q3 scalecheck sweep and the `Canvas.put` audit hook.
- **Out:** any visual/design change (a prototype round would be owed first — none is triggered:
  Q1 restores the already-approved colour rendering, Q3 is observational and byte-identical by
  requirement); relation maps (the S1 port strategy — the operator's map-types
  definition was APPROVED on 2026-10-23, record
  `quickmap/docs/handoff-mapper/map-types-veredicto-2026-10-23.json` outside this repo,
  so the port is no longer blocked; it was blocked per HANDOFF §9 Q2/Q8 at intake);
  the deck defects; the FTS/evidence port (C8).

### 1.3 Definitions, acronyms, abbreviations
- **Sidecar:** the per-map `NAME_nodos.yml` file holding node fields beside `NAME.mmd`.
- **Prescan:** an iterative event-stream scan over YAML parse events (never recursive) that
  refuses anchors, aliases and excessive nesting depth before the full parse.
- **Audit sink:** an optional dict-like recorder attached to a `Canvas` at construction that
  collects overprint/clip events without changing rendered output.
- **SIZES:** the five terminal sizes (80×24, 90×30, 118×34, 160×45, 200×50 cells).
- EARS templates (full level): "When `<trigger>`, the `<system>` shall `<response>`."
- C-10/C-12/C-31/C-40/C-43: dev-flow control ids (see the flow bundle).

### 1.4 References
- HANDOFF brief: `docs/handoff-mapper/HANDOFF.md` (QuickMap repo, read-only oracle) §3 C9/C10/C11,
  §5 conflicts 2 and 7, §9 verdict (operator ruling Q5 quoted there).
- QuickMap oracle code, cited as `qm:src/quickmap/model.py:39-45,424-523`,
  `qm:tests/test_scalecheck.py:35-163`, `qm:src/quickmap/solari.py:115-147`.
- `docs/ARCHITECTURE.md` (module map and frozen interfaces).
- Prior batches whose behaviour this batch preserves: `2026-10-08-data-safety-batch`
  (B-36 load safety), `2026-10-09-hygiene-batch`, `2026-10-10-csv-safety-batch`.

### 1.5 Document overview
§2 overall description, source stories, premises, fork preconditions. §3 HLRs. §4 LLRs and the
Information Flow Contract. §5 validation strategy. §6 appendices (open risks). The append-only
ledger of how this contract came to say what it says lives in `01-requirements-ledger.md`.

## 2. Overall description

### 2.1 Product perspective
mapper is a Textual terminal app: two-layer persistence (`NAME.mmd` + `NAME_nodos.yml` as truth,
SQLite as rebuildable index), headless renderers in `mapper/views/` painting into a `Canvas`
(`mapper/canvas.py`), screens in `mapper/screens/`. Textual's `App.__init__` reads the `NO_COLOR`
environment variable and appends a Monochrome line filter when set — verified at runtime
(`self.no_color = environ.pop("NO_COLOR", None) is not None` in the installed Textual source),
which today greys every approved colour in the operator's shell.

### 2.2 Product functions
- Q1: strip the `NO_COLOR` influence at app construction so colour policy is the app's own.
- Q2: bounded loading — byte caps, depth cap, anchor/alias refusal, node/edge caps on the map
  files; per-file byte cap + NUL probe on content reads (CSV import).
- Q3: a test sweep proving every renderer fits its declared (w, h) budget at the five SIZES, and
  an audit hook on `Canvas.put` that makes overprint/clip defects observable in tests.

### 2.3 User characteristics
Single-operator developer tool; the operator also runs the dev-flow harness. The operator's
shell exports `NO_COLOR=1` (commissioned ruling Q5: colour always on).

### 2.4 Constraints
- Python ≥ 3.10 (pyproject floor); Textual as shipped.
- Caps SHALL be headroomed over the repo's real maps and perf fixtures (measurements in §2.7).
- Refusals SHALL name the limit and the map id; they SHALL NOT crash, hang, or leak paths.
- Max 4 SOURCE files per increment (tests uncapped).
- Test runs strip the harness shell's ambient env: `env -u NO_COLOR -u TERM` — except the Q1
  tests, which set `NO_COLOR=1` deliberately as their input.

### 2.5 Assumptions and dependencies
- The QuickMap repo stays a read-only oracle (HANDOFF §9 Q7: frozen as reference).
- The operator's ruling Q5 stands for the whole app (no per-screen opt-out wanted).
- `yaml` (PyYAML) remains the sidecar parser; the prescan uses its event stream.
- No increment of this batch changes what any screen looks like beyond Q1 restoring colour.

### 2.6 Source user stories

| ID | User Story | Source | DoR status |
|----|------------|--------|------------|
| US-Q1-001 | As the operator, I want mapper to render in colour even when my shell exports `NO_COLOR=1`, so that the approved Darkside colour language is what I actually see. | HANDOFF §5 conflict 2, §9 Q5 (operator ruling, 2026-10-23) | READY |
| US-Q2-001 | As the operator, I want a crafted or corrupted map file to be refused with a message naming the limit, so that loading a map never crashes or hangs the session. | HANDOFF §3 C9 | READY |
| US-Q3-001 | As the operator, I want every renderer proven to fit its terminal budget at the five checked sizes and canvas overprints/clips made observable, so that geometry and paint defects are caught by tests, not by eye. | HANDOFF §3 C10 | READY |

#### Refinement log (one block per story)

**US-Q1-001 — colour always on**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = the operator · outcome = screens render with the same colour
  styles whether or not `NO_COLOR` is set in the environment · why = the approved design language
  is colour; a shell default silently greying it was accepted in QuickMap's post-mortem as a
  defect-class (its batch found all tests green while the operator saw grey) · out of scope = a
  `--no-color` opt-out (the ruling is "always on"; recorded as an open question with the ruling as
  the recommendation).
- **Feasibility (E, S):** implementation path = neutralise `NO_COLOR` in `MapperApp.__init__`
  before `App.__init__` consumes it (verified probe: Textual pops the var in `App.__init__`, and
  a prior batch's fixture docstring confirms the env is read at construction; the app constructs
  `MapperApp` in both the CLI and tests, so the constructor is the one hook that covers every
  path) · dependencies = none · fits one batch = yes (1 source file).
- **Evaluability (T) — behavioral, black-box:** "When `NO_COLOR=1` is present in the environment,
  the user observes painted screens carrying truecolor/non-monochrome styles identical to a run
  without the variable" → AT-108 (drives the real app headless under `NO_COLOR=1`, harvests
  painted segment styles, asserts colour is present and equals the no-var rendering).
- **Open questions:** none — mechanism decided by orchestrator ruling R3 (2026-10-23): neutralise
  `NO_COLOR` in `MapperApp.__init__` via env removal before the Textual base constructor; no
  `--no-color` opt-out (operator ruling Q5). Recorded as ledger entry
  `LED-2026-10-23-hygiene-batch.3`.
- **Classification:** READY — observable through the shipped surface (the running app), black-box
  AT stated, already-shipped check found no app-wide handling (only a test fixture that deletes
  the var and a legend-scope pin, `tests/test_help_scope.py:78-94,247-274`).

**US-Q2-001 — ingestion limits**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = the operator · outcome = an over-limit or hostile map/CSV file
  is refused with a message naming the limit (bytes, depth, anchors/aliases, node/edge count,
  binary probe); the app keeps running · why = measured: a ~4 KB sidecar nested ~2000 deep
  exhausts the C stack inside `yaml.safe_load` (caught only after the fact,
  `mapper/store.py:715-718`), and a 57 KB alias-amplified sidecar emitted 19.9 MB of warnings
  before the per-field containment fix · out of scope = limiting the `.mmd` grammar itself
  (mermaid parse depth is separately oracle'd by `tests/test_repair_depth.py`), FTS/evidence
  indexing (C8 port), attachment files (handed to the OS, never read into the app — verified by
  grep over `mapper/` read sites).
- **Feasibility (E, S):** implementation path = QuickMap's proven design, adapted: byte cap
  (re-checked after read) → iterative event-stream prescan (anchors/aliases refused naming the
  anchor; depth counted on collection start/end, refused past the cap) → full parse → post-parse
  node/edge count caps; a shared content-read helper (per-file byte cap + NUL probe over the first
  8 KiB) for the CSV import read and reusable by the map-file reads · dependencies = none ·
  fits one batch = yes (3 source files).
- **Evaluability (T) — behavioral, black-box:** "When a sidecar exceeds a cap, the user observes a
  load refusal naming the limit and the session continues" → AT-109…AT-114 (one per refusal kind,
  per the one-AT-per-branch rule; boundary arms at cap±1).
- **Open questions:** none — cap constants decided by orchestrator ruling R1 (2026-10-23):
  `MAX_NODES` = 100,000 and `MAX_EDGES` = 100,000 (the measured wide-6000 perf shape at 6,000
  nodes exceeds 1/10 of the proposed 50,000, so the caps were raised — derivation in
  LLR-Q2.1.3 and ledger entry `LED-2026-10-23-hygiene-batch.1`); `diff.py`'s git-show read takes
  the same caps per the IFC flow `q2-map-load` (owner LLR-Q2.1.2). Content-read surface ruled:
  map files + CSV import only; attachments stay OS-handed via `osopen` with no caps (ruling R2).
- **Classification:** READY — oracle design exists, caps measured against the repo's real data,
  refusal surface (typed `MapStoreError` toasts) already shipped.

**US-Q3-001 — scalecheck + canvas audit**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = the operator (and every later batch) · outcome = a test sweep
  proves each of the six renderers returns exactly h lines of at most w cells at the five SIZES;
  an audit hook records overprint and clip events so paint defects surface in tests · why = turns
  the "variable width, fixed reference" memory rule into a mechanical gate, as QuickMap's
  `test_scalecheck.py` does · out of scope = widget `render()` methods (Textual `Static`s with no
  (w,h) contract — enumerated and excluded by rule), dim-text audit events (deferred to BACKLOG as
  B-136 by orchestrator ruling R4, 2026-10-23), changing any rendered byte.
- **Feasibility (E, S):** implementation path = add optional `audit=None` to `Canvas.__init__`
  (additive default, observational only — QuickMap's `solari.py` pattern); the sweep derives its
  renderer set from `mapper.views`' exported roster (never hand-listed) and asserts with
  `rich.cells.cell_len` · dependencies = PDR must freeze the new constructor signature (frozen
  interface, trigger A3) · fits one batch = yes (1 source file; tests uncapped).
- **Evaluability (T) — behavioral, black-box:** "When the sweep runs, every renderer at every size
  either fits the budget or the run fails" → AT-115; "When a render runs with an audit sink
  attached, overprints are recorded and the rendered bytes are identical to a sinkless run" →
  AT-116.
- **Open questions:** none — audit events v1 = clip + overprint, with overprint defined as both
  the old and the new cell alphanumeric and different (orchestrator ruling R4, 2026-10-23; ledger
  entry `LED-2026-10-23-hygiene-batch.4`); dim-text events deferred to BACKLOG B-136; golden
  digests need no re-baselining — byte-identity is itself the requirement (LLR-Q3.2.2).
- **Classification:** READY — the interface change is why ARQ/PDR stand in this batch; the test
  practice itself is purely additive.

**C11 habits (process, not a story):** (1) a move-aside RED counterfactual per deliverable file,
executed and pasted per increment packet; (2) close the axis, not the instance (C-65); (3) every
LLR clause added by amendment names its asserting test and mutant. Applied to this batch's own
increments.

### 2.7 Premise evaluation (C-43) — MANDATORY, one row per premise

| # | Premise, as a truth-apt proposition | Tier (axiom · hypothesis · premise) | Verdict | Executed evidence (command output / `file:line` — **NOT** a citation of another document) | Disposition |
|---|---|---|---|---|---|
| 1 | Textual reads and consumes `NO_COLOR` in `App.__init__`, adding a Monochrome filter when set. | premise | ✅ TRUE | Runtime probe of the installed Textual source printed: `self.no_color = environ.pop("NO_COLOR", None) is not None` | Q1 rests on it |
| 2 | mapper contains no `NO_COLOR`/colour forcing today. | premise | ✅ TRUE | `git grep -n "NO_COLOR" origin/master -- mapper/ tests/` → hits only in `tests/test_help_scope.py` (a fixture that DELETES the var, lines 78-94, and a legend-scope pin, lines 247-274); zero hits in `mapper/` | Q1 not already shipped |
| 3 | The map-file and CSV reads are uncapped today. | premise | ✅ TRUE | `mapper/store.py:697-706` (`read_text` then bare `yaml.safe_load`), `mapper/diff.py:51-59` (`git show` stdout into `safe_load`, only `yaml.YAMLError` caught), `mapper/import_csv.py:39` (unbounded `read_text`) | Q2 rests on it |
| 4 | A small deeply-nested sidecar can exhaust the C parser stack today; the failure is caught only after the bomb runs. | premise | ✅ TRUE | `mapper/store.py:715-718` (comment recording a 4 KB sidecar nested ~2000 deep exhausting the stack inside `safe_load`); `mapper/store.py:707` catches `RecursionError` after the fact | Q2 restock |
| 5 | Measured committed maxima (loadable population: `fixtures/`, `maps/`, `tests/goldens/`, and the tracked perf-evidence workspaces under `.dev-flow/2026-10-10-perf-batch/evidence/perf0b-ws-*`): largest sidecar 1,369,835 B / 12,000 nodes; largest `.mmd` 523,879 B; largest edge count 11,999; real maps ≤ 8 nodes; YAML nesting depth ≤ 4 (anidado and legacy both measure 4 by CollectionStart counting). | premise | ✅ TRUE | Executed probe (2026-10-23, `env -u NO_COLOR -u TERM`) over the full committed population: `.dev-flow/2026-10-10-perf-batch/evidence/perf0b-ws-aa0oz3mw/p_nodos.yml` 1,369,835 B / 12,000 nodes / 0 sidecar edges, its `p.mmd` 523,879 B / 11,999 edge lines; sibling `perf0b-ws-9aj_nwaw/p_nodos.yml` 1,357,836 B / 12,000 nodes (`p.mmd` 519,509 B / 11,999 edges); `perf0b-ws-o3psv_qz/p_nodos.yml` 55,839 B / 500 nodes; `fixtures/legacy_nodos.yml` and `maps/legacy_nodos.yml` 1,536 B / 8 nodes; `fixtures/anidado_nodos.yml` 861 B / 7 nodes; `fixtures/truncado_nodos.yml` 323 B / 3 nodes; yaml-depth by CollectionStart counting: anidado = 4 (the old probe's "3" was wrong), legacy = 4; largest committed repo `.mmd` outside `.dev-flow` = `tests/goldens/perf/at076_saved_wide6000_after_add_child.mmd` 222,002 B (the `perf/dump/wide6000.mmd` copy measures 215,973 B; same wide6000 shape class). Headroom at caps 100,000/100,000: 8.3× nodes, 8.3× edges — fails R1's original ≥10× floor, passes the re-ruled ≥5× floor (ledger `LED-2026-10-23-hygiene-batch.5`); byte-cap headroom 8,388,608 ÷ 1,369,835 = 6.1× | Caps headroom (C-39) |
| 6 | QuickMap's proven cap constants are 8 MiB map bytes, depth 64, 10,000 nodes, 50,000 edges, 4 MiB per-file content bytes, 8 KiB binary probe. | premise | ✅ TRUE | `qm:src/quickmap/model.py:39-45` (`MAX_MAP_BYTES`, `MAX_DEPTH`, `MAX_NODES`, `MAX_EDGES`, `MAX_FILE_BYTES`, `BINARY_PROBE_BYTES`); refusals at `:461-475` (prescan: anchors/aliases/depth) and `:485-521` (byte re-check, count caps); content-read at `:424-437` | Q2 cap values — bytes/depth/file/probe adopted verbatim; node/edge caps SUPERSEDED for mapper by ruling R1 (ledger `LED-2026-10-23-hygiene-batch.1`): the measured wide-6000 fixture (6,000 nodes) exceeds 1/10 of QuickMap's 10,000, so mapper sets 100,000/100,000 |
| 7 | Six renderers implement `IRenderer`; the sweep's subject set is derivable from code. | premise | ✅ TRUE | `mapper/views/state.py:174-187` (Protocol), `mapper/views/__init__.py:2-13` (exported roster: Layered, Outline, Radial, Lane, RailTimeline, HybridLane); construction sites only in `mapper/views/lane.py:199`, `layered.py:693`, `radial.py:184` (asserted by `tests/test_canvas.py:206-213`) | Q3 subject set |
| 8 | `Canvas.put` silently drops out-of-bounds writes and overwrites last-write-wins; rendered rows are always exactly h×w at the Canvas level. | premise | ✅ TRUE | `mapper/canvas.py:103-107` (bounds-guarded dict assignment, no event); `rows()` at `canvas.py:182` composes over `range(h) × range(w)` | Q3 audit hook design |
| 9 | The `Canvas` constructor is a frozen interface, pinned by test and by the module map. | premise | ✅ TRUE | `docs/ARCHITECTURE.md:200` (§4 interfaces table) and `:214` (LANDED row quoting `Canvas(w, h, tones=(), fallback="")`); `tests/test_a3_census.py:658-674` (B-44) pins `inspect.signature(Canvas.__init__).parameters == ["self","w","h","tones","fallback"]` | A3 fires; PDR freezes the new signature; B-44 amended in the Q3 increment |
| 10 | Renderer output bytes are captured byte-identically by existing digests and perf goldens. | premise | ✅ TRUE | `tests/test_repair_depth.py:109` (`MASTER_LEGACY_DIGESTS`, 12 SHA-256 of `(plain, spans)`), fingerprint at `:252-254`; `tests/goldens/perf/render/*.txt` (16 byte-identical LayeredRenderer `.plain` snapshots, gated by `tests/test_perf_paint_clip.py:172`) | B3 fires; byte-identity is the golden property (LLR-Q3.2.2) |
| 11 | The base is current: the tree derives from the verified origin tip. | premise | ✅ TRUE | `git fetch origin` (2026-10-23) then `git rev-parse origin/master` = `1609bbe2…`, `git merge-base HEAD origin/master` = `1609bbe2…` = HEAD (the repo's default branch is `master`; no `origin/main` exists) | Batch base |
| 12 | Windows device-name ids are already refused for map ids and attachment paths. | premise | ✅ TRUE | `mapper/store.py:28-31` (`_RESERVED_NAMES`, incl. COM/LPT/CLOCK$ family) and `:58-61` (the operative `check_map_id` refusal); `mapper/osopen.py:107` (device names refused in any path component) | Q2 is verify-and-pin, not a rewrite |

- **Premise evaluation:** 12 premise(s) · ✅ 12 TRUE / ❌ 0 FALSE / ❓ 0 UNDECIDABLE

### 2.8 Fork preconditions (C-52) — MANDATORY, and the declared empty when the batch does not fork

Planned lanes after PDR (trigger A4 fired — three modules, disjoint files): **L1 = Q1**,
**L2 = Q2** (forked at the PDR seal into **L2a** = `store`/`diff`/`osopen` and **L2b** = `import_csv`/`screens/home` — ledger `LED-2026-10-23-hygiene-batch.9`), **L3 = Q3**. The trunk (requirements, traceability, backlog, this contract) is owned
by the worker/orchestrator and never written from a lane.

| # | Condition (`C-52`) | Discharged? | The executed evidence |
|---|---|---|---|
| 1 | **Frozen contract** — no shared interface is touched inside a lane; one that must change returns to the trunk (trigger A3) | ✅ | The only interface change is `Canvas.__init__` (Q3); L1/L2 never construct or subclass `Canvas` (verified: `Canvas(` occurs only in `mapper/views/*.py` and `mapper/canvas.py`, per premise 7/9). The new signature is frozen at PDR before lanes start; Q3 lands it as trunk work first. |
| 2 | **Disjoint FILE sets**, not just modules — two lanes may not edit the same file, not even different regions | ✅ | L1: `mapper/app.py`. L2a: `mapper/store.py`, `mapper/diff.py`, `mapper/osopen.py` (the bounded content reader's home per R-015 — `osopen.py` added to the Q2 set by ledger `LED-2026-10-23-hygiene-batch.6`). L2b: `mapper/import_csv.py`, `mapper/screens/home.py` (joined by ledger `LED-2026-10-23-hygiene-batch.9` at the PDR seal — the CSV refusal toast must show the typed refusal's message so AT-114's reason reaches the operator; PDR review F-UX-1). L3: `mapper/canvas.py`. Intersection: ∅ (4 sets listed; each ≤ 4 SOURCE files — L2a = 3, L2b = 2; L1/L3 never touch `osopen` or `screens/home`, verified by the PDR crossed census). Tests uncapped and lane-suffixed. |
| 3 | **Crossed reverse census** — family B run per lane and **shared before starting**; the trunk's act, impossible from inside a lane | ❓ | Per-lane B1/B3 probes are recorded in PLAN.md §Triggers at P0; the crossed census (L1×L2×L3 symbol sets, cross-grepped and shared) is discharged at PDR before any lane starts — recorded as PDR-gated. |
| 4 | **One owner of the trunk** — requirements, traceability, backlog and spec are never written from a lane | ✅ | This worker (dev-flow worker for the batch), with the orchestrator holding the gates; lanes receive read-only copies of the contract. |

- **Fork preconditions:** 4 lane(s) · conditions 1, 2, 4 ✅ · condition 3 ❓ owed at PDR (`⏸ PDR-gated`)

---

## 3. High-level requirements (HLR)

### HLR-Q1.1 — Colour always on
- **Traceability:** US-Q1-001
- **Ledger:** none
- **Statement:** When the `NO_COLOR` environment variable is set to any value, the mapper application shall render every screen with the same colour styles it renders when the variable is absent.
- **Rationale (informative):** operator ruling Q5 (HANDOFF §9, 2026-10-23): "colour always on — no use for black-and-white"; QuickMap's post-mortem documents the defect class (all tests green, operator sees grey).
- **Validation:** `test`
- **Executed verification:** planned node `tests/test_colour_always_on.py` (provisional — executes in Phase 3; the existing pin `tests/test_help_scope.py::test_rh6ag_ambient_no_color_cannot_desaturate_legend_samples` is subsumed, not sufficient: it strips the var in a fixture and covers only legend samples).
- **Numeric pass threshold:** with `NO_COLOR=1` set, 0 desaturated painted segments on the probed screens; rendered styles byte-equal to the no-var run.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** screens painted with truecolor styles; nothing greyed.
  - **Shipped surface:** the running app (`mapper.app:main` / `MapperApp`), observed headless through `run_test()` — the same surface the operator watches.
  - **Acceptance test(s):** AT-108
  - **Boundary catalog (QC-3):** ☐ empty ☑ boundary (variable set vs absent — the two regimes) ☑ invalid (variable set to empty string / arbitrary value) ☐ error
  - **Negative control:** remove the env handling (mutation M-Q1-1: delete the `NO_COLOR` neutralisation) → AT-108 goes RED with every painted segment desaturated; transcript pasted in the increment packet.

### HLR-Q2.1 — Bounded map-file loading
- **Traceability:** US-Q2-001
- **Ledger:** LED-2026-10-23-hygiene-batch.6
- **Statement:** When a map file (`.mmd` or `_nodos.yml`) exceeds the byte cap, nests deeper than the depth cap, contains a YAML anchor or alias, or parses to more nodes or edges than the count caps, the loader shall refuse the load with an error naming the limit and the map id, and the application shall continue running.
- **Rationale (informative):** C9 "bring the missing parts only"; measured bombs in §2.7 premises 4-5; QuickMap's `load_map` is the proven design.
- **Validation:** `test`
- **Executed verification:** planned nodes `tests/test_ingestion_limits.py` (provisional — Phase 3), one arm per refusal kind plus boundary arms at cap±1.
- **Numeric pass threshold:** 5 refusal kinds each refuse with a message containing the limit name; 0 crashes/hangs (a 10,000-deep nesting attempt returns a refusal, never `RecursionError`); under-cap fixtures (all committed maps + perf shapes) load unchanged.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** a toast/status message naming the limit; the session stays live; the map list still works.
  - **Shipped surface:** `MapStore.load` → the app's existing error toast path (`MapStoreError` handling in the screens).
  - **Acceptance test(s):** AT-109 (bytes), AT-110 (depth), AT-112 (nodes), AT-113 (edges) · anchors/aliases: `AT-111`, cited not declared — the arm is realized on disk as `tests/test_ingestion_limits.py::test_at_111_anchor_refused_names_anchor_and_map` + `::test_at_111_alias_refused`, and those node names carry lowercase `at_111`, which the V2 node tokenizer (uppercase `AT-\d+` tokens only) cannot harvest; a bare `AT-111` here would declare an id no disk token resolves (the lane header comment `AT-110/111` yields only the `AT-110` token)
  - **Boundary catalog (QC-3):** ☑ empty (sidecar absent — loads as `{}` today, preserved) ☑ boundary (cap−1 loads / cap refuses, per cap) ☑ invalid (anchor/alias, non-dict top level — existing refusal preserved) ☑ error (refusal names the limit)
  - **Negative control:** mutation M-Q2-1 (disable the prescan) → `AT-111` goes RED (anchor-amplified sidecar loads — pinned by `test_at_111_anchor_refused_names_anchor_and_map`); mutation M-Q2-2 (byte cap check removed) → AT-109 goes RED.

### HLR-Q2.2 — Bounded content reads
- **Traceability:** US-Q2-001
- **Ledger:** LED-2026-10-23-hygiene-batch.2 · LED-2026-10-23-hygiene-batch.9
- **Statement:** When the app reads file content into memory (CSV import; the map files), a file larger than the per-file content cap shall be refused, and a file whose first probe bytes contain NUL shall be refused as binary, with the reason named in the error.
- **Rationale (informative):** C9 item 2 (`qm:model.py:424-437`); `mapper/import_csv.py:39` reads the operator-selected file unbounded today. Content-read surface CONFIRMED by orchestrator ruling R2 (2026-10-23): map files + CSV import only; attachment files are handed to the OS via `osopen` and carry no caps.
- **Validation:** `test`
- **Executed verification:** planned node `tests/test_ingestion_limits.py::test_csv_*` (provisional — Phase 3).
- **Numeric pass threshold:** oversize CSV refused naming the cap; NUL-bearing CSV refused as binary; text CSV at cap−1 imports with unchanged row semantics.
- **Priority:** medium
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** the import refusal message with the reason; no partial import, no crash.
  - **Shipped surface:** the home screen's CSV-import toast (`mapper/screens/home.py`) — for a typed refusal (`MapStoreError` family) the toast shows the refusal's own message text (`str(e)` — the reason; path-free per C6); the pre-existing generic branch keeps the `type(e).__name__` discipline for arbitrary `OSError`s (orchestrator ruling R7 / ledger `LED-2026-10-23-hygiene-batch.9`; PDR review F-UX-1).
  - **Acceptance test(s):** AT-114
  - **Boundary catalog (QC-3):** ☑ boundary (cap±1) ☑ invalid (binary content) ☑ error (reason named)
  - **Negative control:** mutation M-Q2-3 (probe removed) → AT-114 goes RED on a NUL-bearing CSV.

### HLR-Q2.3 — Device-name ids stay refused
- **Traceability:** US-Q2-001
- **Ledger:** none
- **Statement:** When a map id or any path component derived from operator input matches a Windows reserved device name, the system shall refuse it with the existing reserved-name error.
- **Rationale (informative):** C9 item 3 — "already partly covered by `mp:mapper/store.py:38-50`" (premise 12); this batch verifies the coverage axis and pins it against regressions rather than rewriting it.
- **Validation:** `inspection` + `test` (regression pin on the existing suite)
- **Executed verification:** census over id→file-name sites at PDR (inspection record in the design proposal); existing refusal tests stay green (targeted probe in Phase 3, `env -u NO_COLOR -u TERM`).
- **Numeric pass threshold:** 0 new id→file-name sites found without the check; existing device-name refusal tests pass.
- **Priority:** medium
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** the existing "reserved Windows name" refusal, unchanged.
  - **Shipped surface:** `check_map_id` / `osopen.safe_local_path` error toasts.
  - **Acceptance test(s):** discharged by the existing suite (reserved-name arms named at PDR per the design proposal §5 — `tests/test_seed_safety.py` `BAD_NAMES` block + `test_seed_store_refuses_every_write_door`, and `tests/test_inc9n.py` refusal-before-open arms; the `test_store.py` example an earlier draft used here was verified absent by grep 2026-10-23); the Q2 increment packet's test ledger re-runs them; no new AT minted for unchanged behaviour.
  - **Boundary catalog (QC-3):** ☑ invalid (reserved names, case/variant forms) — covered by existing tests
  - **Negative control:** none new — the census IS the counterfactual (a found unguarded site reopens the axis).

### HLR-Q3.1 — Renderer scalecheck
- **Traceability:** US-Q3-001
- **Ledger:** LED-2026-10-23-hygiene-batch.7
- **Statement:** When any renderer renders a graph at one of the SIZES, the returned text shall be exactly h lines of at most w cells each.
- **Rationale (informative):** C10 "bring as a test practice"; QuickMap's TC-021; mapper declares overflow in words (`overflow_phrase`) — the sweep proves the budget holds anyway.
- **Validation:** `test`
- **Executed verification:** planned node `tests/test_scalecheck.py` (provisional — Phase 3); renderer set derived from `mapper.views.__all__` with a completeness guard (C-31), sizes as in SIZES, width measured with `rich.cells.cell_len`.
- **Numeric pass threshold:** 6 renderers × 5 sizes × 4 recorded states (`plain`/`folded`/`empty`/`orphan` per the state matrix recorded at `design/state-matrix.md`, derived from code per C-31 — ledger `LED-2026-10-23-hygiene-batch.7`): 100% fit; any misfit fails the sweep with renderer+size+state named.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** a green sweep; on failure, the exact renderer/size/state that misfit.
  - **Shipped surface:** the headless renderer roster (`mapper.views`), exercised exactly as screens and export consume it.
  - **Acceptance test(s):** AT-115
  - **Boundary catalog (QC-3):** ☑ boundary (80×24 minimum and 200×50 maximum sizes; folded/empty/orphan states) ☐ empty ☐ invalid ☐ error
  - **Negative control:** mutation M-Q3-1 (a renderer taught to emit h+1 lines under a size) → AT-115 goes RED naming renderer+size; the mutation is removed after the transcript.

### HLR-Q3.2 — Canvas audit hook
- **Traceability:** US-Q3-001
- **Ledger:** LED-2026-10-23-hygiene-batch.4
- **Statement:** When a `Canvas` is constructed with an audit sink, every out-of-bounds non-space write shall be recorded as a clip event and every in-bounds overwrite of an alphanumeric cell by a different alphanumeric character shall be recorded as an overprint event, and the rendered rows shall be identical to a sinkless canvas for the identical write sequence.
- **Rationale (informative):** C10's audit discipline (`qm:solari.py:115-147`); the byte-identity limb is what keeps the existing golden digests and perf goldens green without re-baselining (B3 census). Audit event set CONFIRMED as v1 = clip + overprint by orchestrator ruling R4 (2026-10-23); dim-text events are deferred to BACKLOG B-136.
- **Validation:** `test`
- **Executed verification:** planned nodes `tests/test_canvas_audit.py` (provisional — Phase 3) + the audit arm of `tests/test_scalecheck.py`.
- **Numeric pass threshold:** clip/overprint arms record the exact (x, y) of each injected defect; the byte-identity arm renders a fixed write sequence with and without the sink and asserts identical `rows()` output (plain + spans).
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** defect events visible in test output; screens visually unchanged.
  - **Shipped surface:** `Canvas` as consumed by the renderers; the sweep's audited render.
  - **Acceptance test(s):** AT-116
  - **Boundary catalog (QC-3):** ☑ boundary (write at (w−1, h−1) ok; (w, h) clips) ☑ invalid (overprint on alphanumeric; overwrite of a space is NOT an overprint — the rule's own boundary) ☐ empty ☐ error
  - **Negative control:** mutation M-Q3-2 (event recording removed) → AT-116 goes RED (injected overprint unrecorded).

---

## 4. Low-level requirements (LLR)

> Each LLR decomposes an HLR into a verifiable property at the implementation level.
> Same regime: EARS syntax owed in `full`. ID format: `LLR-<HLR>.<M>`.
> **C-36 flag:** the cap constants named below — `MAX_MAP_BYTES` (8 MiB), `MAX_DEPTH` (64),
> `MAX_NODES` (100,000), `MAX_EDGES` (100,000), `MAX_FILE_BYTES` (4 MiB), `BINARY_PROBE_BYTES`
> (8 KiB) — are **NEW — created in Phase 3** (in `mapper/store.py` and the `osopen` reader).
> `MAX_MAP_BYTES`, `MAX_DEPTH`, `MAX_FILE_BYTES` and `BINARY_PROBE_BYTES` reconcile 1:1 against
> the oracle's defined constants (`qm:src/quickmap/model.py:39-45`); `MAX_NODES`/`MAX_EDGES`
> deliberately DEVIATE from the oracle (10,000/50,000) per orchestrator ruling R1 — derivation
> and measurement in LLR-Q2.1.3 and ledger entry `LED-2026-10-23-hygiene-batch.1`.

### LLR-Q1.1.1 — Neutralise NO_COLOR at construction
- **Traceability:** HLR-Q1.1
- **Ledger:** LED-2026-10-23-hygiene-batch.3
- **Statement:** When `MapperApp` is constructed, the constructor shall remove the `NO_COLOR` variable from the process environment before invoking the Textual base constructor.
- **Rationale (informative):** Textual pops the var in `App.__init__` (premise 1), so removing it earlier leaves colour policy to the app; the constructor is the one path shared by the CLI and every test. Mechanism DECIDED by orchestrator ruling R3 (2026-10-23): env removal in `MapperApp.__init__` (not `main()`); no `--no-color` opt-out (operator ruling Q5).
- **Validation:** `test (unit)`
- **Executed verification:** planned node `tests/test_colour_always_on.py::test_no_color_removed_before_super` (provisional — Phase 3).
- **Numeric pass threshold:** after construction with `NO_COLOR=1` set, `"NO_COLOR" not in os.environ` and the app's filter list contains no Monochrome filter.
- **Negative control:** mutation M-Q1-1 (removal deleted) → the unit goes RED (var still present).
- **Boundary catalog:** ☑ boundary (var set / absent / set-empty)

### LLR-Q2.1.1 — Byte caps on map files
- **Traceability:** HLR-Q2.1
- **Ledger:** LED-2026-10-23-hygiene-batch.5
- **Statement:** When a map file's size exceeds 8 MiB (`MAX_MAP_BYTES`), the loader shall refuse with an error naming the byte limit and the map id; the cap shall be re-checked on the read bytes, not only on the stat.
- **Rationale (informative):** `qm:model.py:495-503`; TOCTOU between stat and read. 8 MiB is 6.1× the largest committed sidecar (1,369,835 B / 12,000 nodes in the tracked perf-evidence workspaces, premise 5).
- **Validation:** `test (unit)`
- **Executed verification:** planned node `tests/test_ingestion_limits.py::test_byte_cap_refuses_and_names_limit` (provisional — Phase 3).
- **Numeric pass threshold:** stat-oversize and grow-between-stat-and-read cases both refuse; cap−1 loads.
- **Negative control:** mutation M-Q2-2 (re-check removed) → arm goes RED on the grow case.
- **Boundary catalog:** ☑ boundary ☑ error

### LLR-Q2.1.2 — Prescan: anchors, aliases, depth
- **Traceability:** HLR-Q2.1
- **Ledger:** LED-2026-10-23-hygiene-batch.14
- **Statement:** When the sidecar text is scanned as a YAML event stream, the loader shall refuse on the first anchor or alias event, naming the anchor, and shall refuse when collection nesting exceeds 64 (`MAX_DEPTH`); the scan shall be iterative and shall never recurse.
- **Rationale (informative):** `qm:model.py:461-475`; depth 64 is 16× the deepest real sidecar (4); the iterative shape refuses a 10,000-deep bomb without touching the C-stack recursion limit. Ledger `LED-2026-10-23-hygiene-batch.14` (ruling R10, 2026-10-24): the sealed 2026-08-26-ui-next-batch-02's `LLR-N13.1.7` is superseded in part by this rule — its three B1 arms in `tests/test_repair_sidecar.py` are amended to assert this typed refusal (names unchanged, value-leak bounds kept as message-size negatives); the rule itself is unamended.
- **Validation:** `test (unit)`
- **Executed verification:** planned node `tests/test_ingestion_limits.py::test_prescan_*` (provisional — Phase 3).
- **Numeric pass threshold:** anchor, alias and depth-65 arms refuse naming the cause; depth-64 parses; a 10,000-nesting document returns a refusal (not `RecursionError`) in under 5 s.
- **Negative control:** mutation M-Q2-1 (prescan bypassed) → anchor/alias arms go RED.
- **Boundary catalog:** ☑ boundary (depth 64 vs 65) ☑ invalid ☑ error

### LLR-Q2.1.3 — Node and edge count caps
- **Traceability:** HLR-Q2.1
- **Ledger:** LED-2026-10-23-hygiene-batch.1 · LED-2026-10-23-hygiene-batch.5
- **Statement:** When the parsed graph holds more than 100,000 nodes (`MAX_NODES`) or 100,000 edges (`MAX_EDGES`), the loader shall refuse naming the exceeded count.
- **Rationale (informative):** amended by orchestrator ruling R1 (2026-10-23). QuickMap's 10,000/50,000 gave 1.67× node headroom over the largest measured shape — ruled too tight. Ruling: set 50,000/100,000 UNLESS a measured real map or perf fixture exceeds 1/10 of those. Executed measurement (2026-10-23, `env -u NO_COLOR -u TERM`): every `tests/perf_goldens_capture.py` builder shape constructed and counted — deep5000 = 5,000 nodes / 4,999 edges; wide2000 = 2,000 / 1,999; **wide6000 = 6,000 nodes / 5,999 edges**; forest = 6 / 4; every committed golden parsed (real maps ≤ 8 nodes; `tests/goldens/perf/dump/wide6000.mmd` = 6,000 / 5,999). Re-measured 2026-10-23 over the full committed population (ledger `LED-2026-10-23-hygiene-batch.5`): the P2 review found the population excluded the tracked perf-evidence workspaces; the largest committed map is **12,000 nodes / 11,999 edges** (`perf0b-ws-*`; sidecar 1,369,835 B, `.mmd` 523,879 B) — the densest committed shape is the 12,000-node perf workspace; real maps stay ≤ 8 nodes. R1's ≥10× floor would now force ≥120,000, so the standing authorization re-ruled the floor to **≥5×** for the caps decision; **100,000 nodes / 100,000 edges** holds **8.3×** headroom both ways and remains the smallest round pair ≥5× over the largest committed map.
- **Validation:** `test (unit)`
- **Executed verification:** planned node `tests/test_ingestion_limits.py::test_count_caps` (provisional — Phase 3; asserting test for this amended clause).
- **Numeric pass threshold:** 100,001 nodes / 100,001 edges refuse naming the count; at-cap parses. (The cap+1 arms construct minimal-field sidecars — ~16 B/node — so they fit inside the 8 MiB byte cap; documented probe bound.)
- **Negative control:** mutation M-Q2-4 (count check removed) → arm goes RED (asserting mutant for this amended clause).
- **Boundary catalog:** ☑ boundary ☑ error

### LLR-Q2.2.1 — Content-read helper: byte cap + NUL probe
- **Traceability:** HLR-Q2.2
- **Ledger:** LED-2026-10-23-hygiene-batch.2
- **Statement:** When the app reads a file's content into memory, the read shall refuse files larger than 4 MiB (`MAX_FILE_BYTES`) and shall refuse a file whose first 8 KiB (`BINARY_PROBE_BYTES`) contain a NUL byte, naming the reason in the error.
- **Rationale (informative):** `qm:model.py:424-437`; applied to `import_csv.py:39` (unbounded today) and reused by the map-file reads inside the 8 MiB map cap.
- **Validation:** `test (unit)`
- **Executed verification:** planned node `tests/test_ingestion_limits.py::test_content_read_*` (provisional — Phase 3).
- **Numeric pass threshold:** cap±1 arms; NUL at byte 0 and at byte 8,191 both refuse; a NUL-free binary-looking file over 8 KiB with a NUL at byte 8,200 is NOT refused by the probe (documented probe bound).
- **Negative control:** mutation M-Q2-3 (probe deleted) → NUL arm goes RED.
- **Boundary catalog:** ☑ boundary ☑ invalid ☑ error

### LLR-Q2.3.1 — Id-to-file census
- **Traceability:** HLR-Q2.3
- **Ledger:** none
- **Statement:** When this batch's PDR census enumerates the sites that turn operator input into file names, every site shall route through `check_map_id` or `osopen.safe_local_path`.
- **Validation:** `inspection`
- **Executed verification:** PDR census record (grep-derived site list, each with its guard) in `design/design-proposal.md`; re-verified at the Q2 increment gate.
- **Numeric pass threshold:** 0 unguarded sites; the list is derived from the code, not from memory (C-31).
- **Negative control:** the census going stale IS the counterfactual — the Q2 packet re-runs the grep and diffs the site list.
- **Boundary catalog:** ☐ none beyond the census (guard behaviour itself is pinned by existing tests)

### LLR-Q3.1.1 — The sweep derives its subject set from code
- **Traceability:** HLR-Q3.1
- **Ledger:** none
- **Statement:** The scalecheck sweep shall enumerate the renderer set from `mapper.views`' exported roster and shall fail when the enumerated set is empty or smaller than the recorded census of six.
- **Rationale (informative):** C-31 — the input set is itself an oracle; a hand-listed set cannot see a new renderer.
- **Validation:** `test (unit)`
- **Executed verification:** planned node `tests/test_scalecheck.py::test_renderer_roster_derived` (provisional — Phase 3).
- **Numeric pass threshold:** the derived roster resolves to exactly 6 renderer implementations (== 6; a derived count of 0 or < 6 fails the guard — no vacuous pass); the completeness guard arm goes RED when any one of the 6 is dropped from the export list.
- **Negative control:** drop one renderer from the export list in the mutation arm → the guard goes RED (set completeness assertion).
- **Boundary catalog:** ☑ empty (roster empty → guard fails loudly, never vacuous pass)

### LLR-Q3.1.2 — Geometry assertion mechanics
- **Traceability:** HLR-Q3.1
- **Ledger:** LED-2026-10-23-hygiene-batch.7 · LED-2026-10-23-hygiene-batch.11
- **Statement:** For each renderer, size in SIZES and state in the recorded state matrix (recorded at `design/state-matrix.md`: |states| = 4 — plain, folded, empty, orphan — derived from code per C-31; ledger `LED-2026-10-23-hygiene-batch.7`), the sweep shall assert the rendered text splits to between 1 and h lines inclusive and every line's `rich.cells.cell_len` is at most w — with one measured, recorded exception: `LayeredRenderer`'s first line (the wordmark header) is assembled against the body budget `avail = w − 2` plus a node-count meter that spills past `w` by construction (`mapper/views/layered.py` `_header_line`), so for that line the sweep shall assert the spill exactly (header `cell_len` == `(w − 2) + cell_len('{n} nodes')`) instead of bounding it at `w` — and shall report renderer, size and state on failure. *(Amended by `LED-2026-10-23-hygiene-batch.11`, ruling R10: the pre-amendment "exactly h lines, every line ≤ w" text contradicted the live tree — Layered returns `h − 4` lines on graphs smaller than the frame and its header meter spills `len('{n} nodes') − 2` cells past `w` at every size; both byte-pinned by the perf render goldens, so no golden may move to satisfy the old text.)*
- **Validation:** `test (integration)`
- **Executed verification:** realized node `tests/test_scalecheck.py::test_sweep` (2026-10-23, lane L3).
- **Numeric pass threshold:** 6 × 5 × 4 = 120 assertions per the recorded state matrix, 0 misfits; the empty state asserts the documented short-circuit (a zero-node graph returns the renderer's named empty-state short-circuit text of ≤ h lines — '(no map loaded)' for Layered/Outline/Radial, '(no repo loaded)' for the three lane-family renderers, per the state matrix; 'exactly h lines' does not hold for zero-node graphs; recorded with evidence in the matrix); for the non-empty states the line bound is 1..h (Layered renders `h − 4` lines for graphs smaller than the frame — measured) and the width bound is w per line with the Layered header meter spill asserted exactly (measured `(w − 2) + cell_len('{n} nodes')` at all five sizes; the spilled header is byte-pinned by the perf render goldens).
- **Negative control:** mutation M-Q3-1 (one renderer emits h+1 lines) → the sweep names it (the ≤ h bound is the catching assertion).
- **Boundary catalog:** ☑ boundary (min/max sizes; plain/folded/empty/orphan states)

### LLR-Q3.2.1 — Audit parameter and events
- **Traceability:** HLR-Q3.2
- **Ledger:** LED-2026-10-23-hygiene-batch.4 · LED-2026-10-23-hygiene-batch.8 · LED-2026-10-23-hygiene-batch.10
- **Statement:** `Canvas.__init__` shall accept an optional `audit` mapping parameter defaulting to None; when a mapping is supplied, `put` shall append an `(x, y)` tuple under key `clip` for every out-of-bounds write of a non-space character and under key `overprint` for every in-bounds write whose cell already holds a different alphanumeric character and whose own written character is also alphanumeric, and shall append nothing for any other write.
- **Rationale (informative):** `qm:solari.py:119-147`, single-cell adaptation (mapper's `put` writes one cell; `text()` loops via `put`, so it inherits the audit for free); `audit=None` preserves today's behaviour exactly. Event set confirmed as v1 = clip + overprint by orchestrator ruling R4 (2026-10-23) — overprint = both the old and the new cell alphanumeric and different; dim-text events are OUT of v1, deferred to BACKLOG B-136 (asserting test for the event-set clause: `tests/test_canvas_audit.py::test_events`; asserting mutant: M-Q3-2 — event append removed). The second-limb clause (ledger .8) names its own asserting mutant **M-Q3-4** — drop the alphanumeric gate (ledger `LED-2026-10-23-hygiene-batch.10`; one id, one mutation).
- **Validation:** `test (unit)`
- **Executed verification:** planned node `tests/test_canvas_audit.py::test_events` (provisional — Phase 3).
- **Numeric pass threshold:** injected clip at (w, 0) recorded once with its coordinates; injected overprint recorded; overwrite of a space and out-of-bounds space write record nothing; `wire`/`edge`/`text` audited writes behave per the same `put` path.
- **Negative control:** mutation M-Q3-2 (event append removed) → arm goes RED.
- **Boundary catalog:** ☑ boundary ☑ invalid

### LLR-Q3.2.2 — Byte-identity under audit
- **Traceability:** HLR-Q3.2
- **Ledger:** none
- **Statement:** When the same write sequence is applied to two canvases, one with and one without an audit sink, `rows()` shall return identical text (plain and spans) from both.
- **Rationale (informative):** the B3 census property — rendered bytes captured by `MASTER_LEGACY_DIGESTS` and the perf render goldens must not move (no re-baselining owed by this batch).
- **Validation:** `test (unit)`
- **Executed verification:** planned node `tests/test_canvas_audit.py::test_byte_identity` (provisional — Phase 3); plus the full existing golden/digest suites stay green (targeted probe at the Q3 gate).
- **Numeric pass threshold:** identity holds over the fixed write sequence corpus; 0 golden/digest failures attributable to the hook.
- **Negative control:** mutation M-Q3-3 (audit mutates the cell write) → arm goes RED and the digest suites would re-baseline — the mutation class the requirement exists to expose.
- **Boundary catalog:** ☑ boundary (first write vs overwrite; clipped writes)

### LLR-Q3.2.3 — The audited render is live in the sweep
- **Traceability:** HLR-Q3.2
- **Ledger:** LED-2026-10-23-hygiene-batch.12 · LED-2026-10-23-hygiene-batch.13
- **Statement:** When the scalecheck sweep renders with an audit sink injected at the `Canvas` construction sites, at least one audited canvas shall be created per non-empty render for every renderer whose paint path constructs a canvas (measured census: `LayeredRenderer`, `RadialRenderer`, `RailTimelineRenderer`), renderers that compose their text directly and construct none (`OutlineRenderer`, `LaneRenderer`, `HybridLaneRenderer`) shall be asserted to construct none — never silently skipped — and the sweep shall fail on any overprint event and on any clip event unless the rendered plain text declares overflow; for the recorded `empty` state the documented zero-node short-circuit constructs no canvas, and the sweep shall assert exactly that (zero constructions, hence zero events). *(Threshold amended by `LED-2026-10-23-hygiene-batch.12`/`.13`: measured at the L3 gates — every renderer's empty-state render short-circuits before any construction, and the construction census above is measured over the full 120-combo matrix.)*
- **Rationale (informative):** `qm:test_scalecheck.py:113-143` (TC-022) — a hook no test exercises is scaffolding; mapper's declared-overflow phrases (`overflow_phrase`, `_degraded`) are the legal-clip declaration.
- **Validation:** `test (integration)`
- **Executed verification:** realized node `tests/test_scalecheck.py::test_sweep_audit_arm` (2026-10-23, lane L3).
- **Numeric pass threshold:** ≥1 audited canvas per non-empty render for the canvas-constructing renderers (zero constructions asserted for the direct-composition renderers AND for the recorded `empty` short-circuit); 0 unexplained overprints; 0 unexplained clips on the six-renderers × SIZES matrix (measured baseline: 0 events across all 120 combos — the renderers paint cleanly).
- **Negative control:** a bounds-breaking renderer (M-Q3-1 class — writes past its own canvas without declaring overflow) → unexplained clip events → the sweep arm goes RED; M-Q3-2 (event append removed) → the unit arm `tests/test_canvas_audit.py::test_events` goes RED (a healthy render records zero events, so an append-removed mutant is pinned by the unit arm, not the sweep arm).
- **Boundary catalog:** ☑ error (unexplained events fail the sweep)

### Information Flow Contract (IFC) — C-54

**Part A — flows:**

```
FLOW: q1-env-colour
  SOURCE : the process environment (NO_COLOR)
  NODES  :
    - fn    : mapper.app.MapperApp.__init__
      owner : LLR-Q1.1.1
      in    : environment vars (NO_COLOR present/absent)
      out   : a colour-enabled app whose filter list has no Monochrome filter
  SINK   : the terminal screen (painted Text styles)
```

```
FLOW: q2-map-load
  SOURCE : workspace files NAME.mmd + NAME_nodos.yml (operator-supplied bytes)
  NODES  :
    - fn    : mapper.store.MapStore.load
      owner : LLR-Q2.1.1
      in    : file bytes (stat + re-read)
      out   : Graph, or a MapStoreError naming the exceeded limit and the map id
    - fn    : mapper.store._prescan_sidecar
      owner : LLR-Q2.1.2
      in    : sidecar text
      out   : sidecar text (pass) or a refusal naming anchor/alias/depth
    - fn    : mapper.diff.diff_against_git
      owner : LLR-Q2.1.2
      in    : sidecar bytes from git show
      out   : parsed sidecar dict, or None (existing contract) — same caps applied
  SINK   : the map screen (graph) and the status toast (refusal)
```

```
FLOW: q2-csv-import
  SOURCE : an operator-selected CSV file
  NODES  :
    - fn    : mapper.import_csv.load
      owner : LLR-Q2.2.1
      in    : file bytes (capped read + NUL probe)
      out   : Graph, or an error naming the byte cap / binary probe
  SINK   : the import preview screen
```

```
FLOW: q3-render
  SOURCE : a Graph plus a ViewState carrying w and h
  NODES  :
    - fn    : mapper.views.IRenderer.render (six implementations)
      owner : LLR-Q3.1.2
      in    : (graph, state) with state.w, state.h
      out   : Text of exactly h lines of at most w cells
    - fn    : mapper.canvas.Canvas.put (audited construction)
      owner : LLR-Q3.2.1
      in    : cell writes (x, y, ch, style)
      out   : cells dict plus clip/overprint events in the audit sink
  SINK   : the screen canvas and the export snapshot
```

**Part B — boundary decomposition:** yes — the user interface has screens a consumer addresses independently; this batch declares the two components whose outputs it touches (SYSTEM-level inputs are not further decomposed here; balancing against an undeclared parent is reported by `V12` as not-checkable, which is the honest state).

```
COMPONENT: map-view
  PARENT : SYSTEM
  SURFACE: the map screen body
  INPUTS : graph: Graph ; view-state: ViewState
  OUTPUTS:
    - id          : rendered-text
      value       : the fitted h×w Text a renderer returns for the visible graph
      address     : the return value of mapper.views.IRenderer.render
      cardinality : 1 per render call
      consumers   : mapper/screens/map/screen.py ; mapper/export.py ; tests/test_repair_depth.py ; tests/test_perf_paint_clip.py
      owner       : LLR-Q3.1.2
```

```
COMPONENT: status-toast
  PARENT : SYSTEM
  SURFACE: the app's status/toast line
  INPUTS : map-id: str ; refusal-reason: str
  OUTPUTS:
    - id          : refusal-message
      value       : the user-visible load/import refusal naming the limit and the map id
      address     : the MapStoreError message at the store boundary
      cardinality : 0..1 per load attempt
      consumers   : mapper/app.py ; mapper/screens/map/screen.py ; tests/test_store.py ; tests/test_repair_sidecar.py
      owner       : LLR-Q2.1.1
```

---

## 5. Validation strategy

### 5.1 Methods

**Layer A — white-box / functional (TC):** unit/integration tests per LLR
(`tests/test_colour_always_on.py`, `tests/test_ingestion_limits.py`,
`tests/test_canvas_audit.py`, `tests/test_scalecheck.py`), each with the C-40 RED counterfactual
named in its increment packet. Methods: `test`.
**Layer B — black-box / behavioral acceptance (AT):** AT-108…AT-116 through the shipped surfaces
(app under `run_test`, loader to toast, renderer roster as screens consume it). Method:
`acceptance`.

### 5.2 Batch acceptance criteria
- 100% of LLRs covered by at least one TC with pass result; every HLR carries ≥1 AT observing
  its outcome through the shipped surface with boundary + negative evidence.
- 0 blocker fails in validation; the full suite green under `env -u NO_COLOR -u TERM` (the
  orchestrator schedules the full run; this batch runs only targeted probes).
- No rendered byte changes: the existing golden digests and perf render goldens pass
  un-re-baselined.
- Every deliverable file carries a move-aside RED counterfactual transcript (C11 habit 1); every
  amendment LLR clause names its asserting test and mutant (C11 habit 3).
- Refusals name their limit; no crash or hang on any refused input (a refusal completes in
  bounded time).

---

## 6. Appendices (optional)

### 6.1 Extended glossary
- **Move-aside RED counterfactual:** the deliverable file is renamed aside, the targeted tests
  are run, and the failure transcript is pasted — proving the tests hold the file, not the
  intent.
- **Declared overflow:** mapper's textual overflow markers (`overflow_phrase`, `_degraded`,
  count forms) that make a clip event legal in the sweep.

### 6.2 Relevant design decisions
- Caps adopt QuickMap's constants verbatim for bytes/depth/file/probe (C-36
  fold-against-defined-vocabulary) — headroom: 6.1× bytes over the largest committed sidecar
  (1,369,835 B), 16× depth (deepest committed sidecar measures 4). `MAX_NODES`/`MAX_EDGES` deliberately deviate per orchestrator ruling R1 (2026-10-23):
  100,000/100,000, retained as the smallest round pair holding ≥5× headroom over the largest
  committed map (12,000 nodes / 11,999 edges in the tracked perf-evidence workspaces — 8.3×
  headroom both ways; premise 5 re-measured 2026-10-23 including the perf-evidence workspaces,
  ledger `LED-2026-10-23-hygiene-batch.1` amended by `LED-2026-10-23-hygiene-batch.5`).
- The audit hook is constructor-injected and observational; production construction sites are
  not touched (the sweep injects, like `qm:test_scalecheck.py:113-143`).
- `NO_COLOR` is neutralised at construction, not in `main()`, because tests construct
  `MapperApp` directly (premise 1/2 evidence).
- Q2's device-name defence is verified and pinned (census), not rewritten (premise 12).

### 6.3 Open risks
- **Security pattern scan (family C — C6 fired):** `devflow-scan-spec.py` run 2026-10-23 over
  §§1–4: controls all ok; flags `session` and `expose`. Both are vocabulary collisions, answered
  here per the scanner's instruction: `session` names the running app process ("the session
  continues"), not an authentication session — this batch touches no auth surface (C1 not fired);
  `expose` names making defects observable in tests ("the mutation class the requirement exists
  to expose"), not a network endpoint — no new crossing of the system boundary exists (C7 not
  fired). The C6 security questions, answered: (a) the new code handles operator-supplied map and
  CSV bytes at load — bounded by the byte caps, the NUL probe and the iterative prescan; (b) no
  new boundary crossings — filesystem reads are the existing three sites, now capped; no network,
  no OS-handler changes; (c) refusal messages name the limit and the map id only, never a path —
  the privacy posture of `store`/`osopen` is preserved.
- **Node/edge-cap headroom is 8.3×** over the largest committed map (12,000 nodes / 11,999
  edges — synthetic perf evidence; real maps are ≤ 8 nodes); the ≥10× floor of ruling R1 was
  re-ruled to ≥5× by the standing authorization (ledger `LED-2026-10-23-hygiene-batch.5`);
  the caps are 100,000/100,000 per ruling R1.
  If a future perf fixture needs > 100,000 nodes or edges, the cap (and LLR-Q2.1.3) move by
  amendment, with the fixture regenerated — the sweep and load tests bound the blast radius.
- **Prescan cost:** the event-stream scan adds one pass over the sidecar; the
  largest perf sidecar's (1,369,835 B / 12,000 nodes) load-time delta is measured at the L2a
  increment gate (watch-item, not a gate).
- **`diff.py` git-show read:** takes the same caps via the shared helper; its `None`-on-error
  contract is preserved (no new crash path).
- **C6 (input surface) fired:** the batch's own new code reads operator files (the prescan). The
  prescan is iterative and bounded by the byte cap; refusal messages name the map id only, never
  a path (privacy posture preserved).
- **Outgoing batch vault sync:** `2026-10-15-review-screen-batch`'s light sync is DONE — synced
  2026-10-23 (light, README only); the vault folder is the flag (orchestrator ruling R6
  correction, 2026-10-23).
