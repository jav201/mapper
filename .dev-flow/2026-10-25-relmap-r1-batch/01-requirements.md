# Requirements — mapper — Batch 2026-10-25-relmap-r1-batch

> **Artifact language:** English. Reserved field names are never translated.
> **Ids are grouped by module:** RMP (profile table) · RMM (read model) · RMG (gap detection) · RML (bounded relation-file reads) · RMA (canon adapter) · RMU (`--audit` lines).

## 1. Introduction

### 1.1 Purpose
The live requirements contract for relation-map port R1: the headless core of a second map KIND for mapper — a typed, multi-parent, read-only relation graph — plus its first profile (`reqharness`, the traceability graph), derived from mapper's own requirements canon and surfaced as structural-gap lines in `mapper --audit`. Source: QuickMap handoff `qm:docs/handoff-mapper/HANDOFF.md` §3 C1/C2/C9/C12, §5, §9 (strategy S1) and `qm:docs/handoff-mapper/MAP-TYPES.md` (approved 2026-10-23, record `map-types-veredicto-2026-10-23.json`).

### 1.2 Scope
- **In:** `mapper/relmap/` — the per-profile table (a), the read model (b), gap detection (c), the read-only canon adapter and the `.relmap.yml` descriptor (d), `--audit` structural lines (e); the extraction of the YAML prescan to a shared leaf so the descriptor reads under the same C9 limits.
- **Out:** every screen, view, matrix, lens, gaps *view*, node sheet (R2, prototype verdict already given); evidence search (R3); timeline and typed date parse (R4); the `lineage` profile, metro, `<name>_map.yml` data files (R5); editing typed edges (deferred past R5, OQ5); the US canon and the AT→test table themselves (follow-up "B-next-2" — R1 derives what exists and says exactly what it cannot); any change to the tree kind (`Graph`, `store` behaviour, `mermaid`).

### 1.3 Definitions, acronyms, abbreviations
- **Relation map:** the new map kind — typed multi-parent directed graph parameterised by a *profile*. **Tree map:** today's `Graph` kind; unchanged.
- **Profile:** a data table — node kinds, edge types (allowed `(src kind, dst kind)` pairs, direction of change, evidence rule), gap catalogue (per row: severity, a pattern from a closed set of four, the sourced kinds it needs, a sentence template). R1 ships one: `reqharness`.
- **Direction of change:** an edge type is *downstream* when a change flows `src → dst`; for every other type the edge is reversed (`dst → src`). `down(n)` = where a change at `n` flows; `up(n)` = what feeds `n`. **Reach(n)** = number of nodes reachable through `down`.
- **Graduated edge** (B-119 D2, `binds` AT→TC): ● bound = edge with evidence · ◐ tagged = edge without evidence · ○ none = no edge.
- **Sourced kind:** a node kind whose canon source is configured and readable; a gap kind that names an unsourced kind is inactive (honest partial map, no noise).
- **Unlinked LLR:** a canon LLR whose id resolves to no HLR under derivation rule D-1 (LLR-RMA.1.2).
- **Prescan:** iterative YAML event scan refusing anchors/aliases and excess nesting before any compose (hygiene batch, `LLR-Q2.1.2`).
- **Closed cause set (K1–K17):** the fixed strings a refusal or an `unavailable` line may print (LLR-RML.1.5, .1.1, .1.2, .1.3); a cause is never `str(exc)`, a path, an anchor name or a YAML snippet.
- **Orphan row:** a canon row that is not a node under its own id — a row `parse_canon` reported, or an unlinked LLR. **`DISPLAY_MAX`:** 120 characters; a longer repository-derived value is cut to 120 characters in total, the last being `…`, BEFORE escaping (LED .44).
- **Snapshot canon:** `tests/fixtures/relmap/REQUIREMENTS.snapshot.md`, a byte copy of the repository canon taken at the P1 probe (digest in ledger entry LED-2026-10-25-relmap-r1-batch.4, corrected by entry .36: the pin is the LF-normalised sha256); the only input against which absolute counts are asserted.
- EARS templates (full level): "When `<trigger>`, the `<system>` shall `<response>`."
- C-10 / C-12 / C-31 / C-35 / C-36 / C-39 / C-40 / C-43: dev-flow control ids (flow bundle).

### 1.4 References
- `qm:docs/handoff-mapper/HANDOFF.md` §3 C1, C2, C9, C12; §5 conflicts 2, 4, 5, 7, 8; §9 verdict. `qm:docs/handoff-mapper/MAP-TYPES.md` §2 (engine), §3 (profile), §5–§6 (source, files, cycles, evidence), §7.1 (catalogue), §9 (R1 plan), §10 (OQ1–OQ8, all accepted).
- QuickMap oracle (read-only): `qm:src/quickmap/model.py` (`Map` `:242-423`, cycles `:608-634`), `qm:src/quickmap/gaps.py`, `qm:tests/test_model.py`, `qm:tests/test_gaps.py`; port audit `m4-port-audit.md` (scratch, 2026-10-24): lineage constants at `qm:model.py:28-31,290` become profile tables.
- `docs/ARCHITECTURE.md` (amended by this batch's ARQ: rows `relmap`, `yamlscan`, R-016, R-017, §6 worksheet). Canon reader `mp:mapper/reqharness/derive.py:134-215` (`parse_canon`, `load_canon`, `CanonObject`). Hygiene-batch limits `mp:mapper/osopen.py:84-150`, prescan `mp:mapper/store.py:712-749`, audit CLI `mp:mapper/reqharness/audit.py:363-394`, dispatch `mp:mapper/app.py:344-352`.
- Prior batches whose behaviour this batch preserves: `2026-10-23-hygiene-batch` (limits, A-110), `2026-10-11-reqharness-batch` (audit, canon).

### 1.5 Document overview
§2 description, stories, premises, fork preconditions. §3 HLRs. §4 LLRs and the Information Flow Contract. §5 validation strategy. §6 appendices (decisions, open risks, security scan). The append-only ledger is `01-requirements-ledger.md` (empty at draft).

## 2. Overall description

### 2.1 Product perspective
mapper holds one map kind today: a tree (`Graph`: single parent, cycles refused at parse and save, `mermaid` + `_nodos.yml` as truth). ReqHarness derives *review* state per canon row (`derive_states`) but nothing builds *structure*: one TC verifying several LLRs, one LLR derived from an HLR and verified by several TCs, an AT bound to a test node. R1 adds a second kind beside the tree — never a mutation of it (S1) — as a headless package that computes structure from files and is read-only by contract.

### 2.2 Product functions
Profile table → read model (up/down by change direction, reach, neighbourhood, cycles reported) → gap catalogue ranked by severity then reach → adapter deriving the reqharness map from `REQUIREMENTS.md` (HLR/LLR skeleton) → `--audit` lines.

### 2.4 Constraints
Python ≥ 3.10 (`mp:pyproject.toml:9`); PyYAML ≥ 6.0 only; headless (no Textual, no Rich); English strings; max 4 SOURCE files per increment; the module map is checked against the tree (premise 11); `mapper.__file__` must resolve inside the worktree before a test run is trusted (premise 12).

### 2.6 Source user stories

| ID | User Story | Source | DoR status |
|----|------------|--------|------------|
| US-RM-001 | As the operator, I want mapper to know the typed traceability graph of its own requirements — which LLR refines which HLR, with US/AT/TC joining as their canon lands — so the structure the tree cannot hold is queryable and `mapper --audit` states what it derived. | HANDOFF §3 C1 · MAP-TYPES §2–§3, §5, §6.1 (staging note) | READY |
| US-RM-002 | As the operator, I want structural holes in that graph (HLR without LLR; cycle; and, when their sources exist, US without AT, open AT without test, unevidenced `verifies`, tagged-only AT, LLR not verified, orphan TC) ranked by severity then reach, so I see which hole reaches furthest. | HANDOFF §3 C2 · MAP-TYPES §7.1 (OQ8 accepted) | READY |
| US-RM-003 | As the operator, I want `mapper --audit <repo>` to print those structural lines beside the review state, without starting the TUI and without changing the release verdict, so CI and terminal see structure and review together. | HANDOFF §3 C2 "Needs", §S1 step 3 · MAP-TYPES §9 R1 | READY |
| US-RM-004 | As the operator, I want a crafted or oversized relation descriptor refused with a message naming the limit, so reading one never hangs or crashes the audit. | HANDOFF §3 C9 · MAP-TYPES §2.1 "Ingestion hardening applies to all relation files" | READY |

#### Refinement log (one block per story)

**US-RM-001 — the traceability graph**
- **INVEST:** I ✓ (after US-RM-004's limits only for the descriptor) · N ✓ · V ✓ · E ✓ · S ✓ (5 increments across the batch) · T ✓ (audit counts line).
- **Functionality:** user = the operator · outcome = a derived graph whose counts and unlinked entries are stated · out of scope = US/AT/TC nodes (no canon yet), any view. **Feasibility:** QuickMap's `Map` is 3.10-clean (premise 3); the unknown HLR→LLR link is now measured (premises 1–2). **Evaluability:** AT-117, AT-119, AT-124 through `mapper --audit` over fixture repos (exact figures against the snapshot canon; invariants against the live one).

**US-RM-002 — ranked structural gaps**
- **INVEST:** all ✓. **Evaluability gap, declared:** through the only shipped surface (`--audit` over the canon) one catalogue kind can be sourced — HLR WITHOUT LLR. The ranking and the other seven kinds are exercised at Layer A on the `mapper.relmap` API with synthetic fixtures; their black-box AT waits on the batch that lands their canon (B-next-2) or on R2's gaps view (open question OQ-R1-2, recommended: accept). The one reachable kind carries AT-118 and AT-125 (qualified sentence).

**US-RM-003 — audit lines** — INVEST ✓; observable in stdout and exit code; AT-120, AT-122, AT-126, AT-128, AT-129; the raising-callable arm is Layer A (TC-RM-02).

**US-RM-004 — bounded descriptor** — INVEST ✓; a refusal is a printed line, never a crash; AT-121 (one arm per cause of the closed set K1–K17; cap±1 as comment-padded valid YAML), AT-127 (discovery).

### 2.7 Premise evaluation (C-43) — MANDATORY, one row per premise

| # | Premise, as a truth-apt proposition | Tier | Verdict | Executed evidence (command output / `file:line`) | Disposition |
|---|---|---|---|---|---|
| 1 | The canon (`REQUIREMENTS.md`) carries no parent column; the HLR→LLR link is derivable only from id structure, by dropping the last dotted segment of an LLR id. | premise | ✅ TRUE | `evidence/p1-canon-derivation-probe-2026-10-25.txt`: 76 HLR / 199 LLR parsed; header columns are `status`, `statement` only; 196 of 199 LLR ids resolve to an existing HLR by rule D-1; 0 duplicate ids | Rule D-1 (LLR-RMA.1.2) |
| 2 | Not every canon row parses: `parse_canon` reports rows whose cell count differs from the header (pipe inside a statement). | premise | ✅ TRUE | same transcript: 7 reported rows (`LLR-HYG.1.1`, `LLR-CAN.1.1`, `LLR-CAN.1.2`, `HLR-RH.6`, `LLR-RH.6.1`, `LLR-RH.7.3`, `LLR-Q3.1.2`); because `HLR-RH.6` is among them, `LLR-RH.6.2` is unresolved; the other two unresolved ids are `LLR-REPAIR.1`, `LLR-REPAIR.2` (no `HLR-REPAIR`) | LLR-RMA.1.3: reported, never guessed; unlinked listed, no edge |
| 3 | QuickMap's `model.py`/`gaps.py` use no construct past Python 3.10. | premise | ✅ TRUE | `evidence/p1-premise-probes-2026-10-25.txt` P-b: both parse under `ast.parse(feature_version=(3, 10))`. A real 3.10 run is NOT possible here (no 3.10 interpreter) — LLR-RMM.1.1's AST floor guard is the in-repo proxy | Port; the real 3.10 run is `not-run` (no 3.10 interpreter, no CI) — the AST floor plus a banned-stdlib-name census is the in-repo proxy, and an operator-run 3.10 check is a Phase 4 item |
| 4 | The oracle tests are green and portable as oracles. | premise | ✅ TRUE | P-j: `tests/test_model.py tests/test_gaps.py` → 123 passed in 13.91s (3.12.7) | Oracles for LLR-RMM/RMG; ports are re-derived, never copied (QuickMap fixtures are lineage-shaped) |
| 5 | In the approved `reqharness` profile a cycle is impossible once edge pairs are validated: the kind graph is a DAG. | premise | ✅ TRUE | P-c: topological order `AT, US, TC, HLR, LLR` exists over the six approved `(src, dst)` pairs | TRACEABILITY CYCLE stays in the catalogue (approved) and the engine; its RED case uses a synthetic profile (LLR-RMM.3.1, RMG.1.1) and the limit is stated, not hidden |
| 6 | MAP-TYPES §3.2 contradicts itself on `binds`: the normative rule (`change_downstream = ("refines",)`) makes `binds` upstream, but the row's prose says "a changed AT reaches the bound test node" (downstream). | premise | ✅ TRUE | P-d: under the rule a change at LLR1 reaches `AT1, TC1` (the lens question MAP-TYPES §3.4 states: "which TCs and ATs need re-review?"); under the prose reading it reaches `TC1` only | R1 implements the NORMATIVE rule; the prose is flagged for correction (OQ-R1-4, ledger-free: no clause of this contract changes) |
| 7 | The C9 constants and reader are importable from `osopen`. | premise | ✅ TRUE | P-f: `read_capped`, `ContentReadError`, `MAX_MAP_BYTES` (8388608), `MAX_DEPTH` (64), `MAX_NODES` (100000), `MAX_EDGES` (100000), `confine_reason(text, workspace)` all present, plus `is_link` (`osopen.py:205`), which LLR-RML.1.5 uses | LLR-RML.1.1, RMM.1.3 |
| 8 | The prescan is a method that uses no instance state, so it can be extracted without behaviour change. | premise | ✅ TRUE | P-e: `MapStore._prescan_sidecar` (`store.py:712-749`) has 0 `self.<attr>` uses; its two callers are `store.py:769` and `:820` | LLR-RML.1.4 |
| 9 | `run_cli` has one caller outside its definition and tests assert the verdict by line prefix, not by position. | premise | ✅ TRUE | P-g: only `mapper/app.py:352`; `tests/test_reqharness_release.py:675,764` select `line.startswith("verdict: ")`; the A3 pin is `tests/test_a3_census.py:329` (`== 86` ARG-FUL `.render(...)` attribute calls over tracked `mapper/` and `tests/`; lines :300-312 are historical commentary), and `test_tc_a3_no_source_file_is_invisible_to_the_census` (:36-55) requires every new file to be `git add`ed before a run | LLR-RMU.1.1 appends AFTER the verdict line; B1 census owed at Inc-5 (relmap adds no `.render(` attribute call; new files staged first) |
| 10 | No relation descriptor and no `relmap`/`yamlscan` file exists on the tree. | premise | ✅ TRUE | P-h, P-i: `git ls-files '*.relmap.yml'` and `mapper/relmap`, `mapper/yamlscan.py` → empty | Input class is new: consumers re-derived by content (§4 fixture-content census, LLR-RML.1.2) |
| 11 | `docs/ARCHITECTURE.md` §2's path column is checked against the tree. | premise | ✅ TRUE | P-k: a first draft listing `mapper/relmap/*.py` failed `tests/test_repair_map_truth.py::test_at_p04_every_owned_path_exists_on_disk` ×9; re-worded, 90 passed | LLR-RMP.2.1 (paths written into the row as each file lands) |
| 12 | The editable install may point at another checkout, so a worktree test run proves nothing until `mapper.__file__` is probed. | premise | ✅ TRUE | Without `PYTHONPATH` the probe printed `mapper resolves inside the worktree: False`; with `PYTHONPATH` set to the worktree: `True` (both transcripts under `evidence/`) | Every targeted run states the probe |
| 13 | The base is current. | premise | ✅ TRUE | `git fetch origin` 2026-10-25; `origin/master` = `HEAD` = merge-base = `194f885`; `git ls-remote --heads origin` answered, newest commit 2026-10-24 | RC-1 / RC-2 |
| 14 | The relation graph derivable today is far below the caps. | premise | ✅ TRUE | transcript: 275 nodes / 196 edges vs `MAX_NODES = MAX_EDGES = 100000` | Caps are abuse bounds, not a sizing decision |

- **Premise evaluation:** 14 premise(s) · ✅ 14 TRUE / ❌ 0 FALSE / ❓ 0 UNDECIDABLE

### 2.8 Fork preconditions (C-52) — MANDATORY, and the declared empty when the batch does not fork

No fork: trigger A4 not fired. The five increments are a dependency chain over one package (`profile` ← `model` ← `gaps` ← `adapter` ← `audit`); `docs/ARCHITECTURE.md` §6 records why `modules(A) ∩ modules(B) ≠ ∅` for every adjacent pair and why no lane runs beside another. One agent owns the trunk and the lanes alike.

- **Fork preconditions:** 0 lane(s) · declared empty — not applicable

---

## 3. High-level requirements (HLR)

### HLR-RMP.1 — The reqharness profile is a table
- **Traceability:** US-RM-001
- **Ledger:** LED-2026-10-25-relmap-r1-batch.2, LED-2026-10-25-relmap-r1-batch.10, LED-2026-10-25-relmap-r1-batch.13
- **Statement:** The relation-map package shall declare the `reqharness` profile as data — five node kinds (US, HLR, LLR, AT, TC); four edge types (`refines`, `covers`, `verifies`, `binds`), each with its allowed (source kind, destination kind) pairs, its direction of change and its evidence rule; and the gap catalogue of eight kinds, each with its severity, its pattern from a closed set of four, its needed sourced kinds and its sentence template — and the engine shall name no node kind, edge type or gap kind except through the profile it was given.
- **Rationale (informative):** MAP-TYPES §2.2/§3; the port audit's finding B1/B2 (QuickMap hard-codes `LINEAGE`, `NEEDS_EVIDENCE`, a second divergent literal at `model.py:290`).
- **Validation:** `test`
- **Executed verification:** planned `tests/test_relmap_profile.py`, `tests/test_relmap_isolation.py` (provisional — Phase 3).
- **Numeric pass threshold:** 5 kinds, 4 edge types, 6 allowed pairs, 8 catalogue rows; 0 kind, edge-type or gap-kind string literals in `model.py` and `gaps.py` (AST census).
- **Priority:** high
- **Acceptance (black-box):**
  - **Observable outcome:** the `--audit` summary line names `profile=reqharness` and counts nodes by kind and edges by type, all from the table; a kind or type with a zero count is omitted from the parentheses (stated once, LLR-RMU.1.2).
  - **Shipped surface:** `mapper --audit <repo>`.
  - **Acceptance test(s):** AT-117
  - **Boundary catalog (QC-3):** ☑ empty (US, AT and TC have zero nodes: omitted from the summary, never printed as gaps) ☑ invalid (descriptor naming another profile — AT-121) ☐ error
  - **Negative control:** mutation M-RMP-1 (an engine module hard-codes `"refines"` in place of the profile's downstream set) → the AST census test goes RED; M-RMP-5 (a catalogue severity cell changed) → the ranking arm goes RED.

### HLR-RMP.2 — The relation kind is isolated from the tree kind
- **Traceability:** US-RM-001
- **Ledger:** LED-2026-10-25-relmap-r1-batch.11, LED-2026-10-25-relmap-r1-batch.16, LED-2026-10-25-relmap-r1-batch.65
- **Statement:** The relation-map package shall import none of the tree kind's modules, and no module outside the package and `mapper/app.py` shall import the package (`reqharness.audit` receives its callable from `app`), so that tree maps keep every invariant they have today.
- **Rationale (informative):** S1 — "a KIND beside the tree, never a mutation of it"; ARCHITECTURE R-016.
- **Validation:** `test` (AST census over the shipped tree) + `inspection` (§2 row)
- **Executed verification:** planned `tests/test_relmap_isolation.py`.
- **Numeric pass threshold:** 0 forbidden edges over every `mapper/**.py`; the existing tree-kind suites pass unchanged (targeted: `test_store.py`, `test_mermaid*.py`, `test_ingestion_limits.py`).
- **Priority:** high
- **Acceptance (black-box):**
  - **Observable outcome:** none through a shipped surface — `MapStore.load` is a library API, not a shipped surface. **Layer A only, declared:** TC-RM-01 pins that a cyclic tree map is still refused at load, exactly as today (a regression pin — it gates nothing new, and says so; no AT).
  - **Shipped surface:** none in R1 (in-process `MapStore.load`).
  - **Acceptance test(s):** none — TC-RM-01 (Layer A)
  - **Boundary catalog (QC-3):** ☑ invalid (cycle in a tree map) ☐ others n/a
  - **Negative control:** mutation M-RMP-2 (a `model.py` import of `relmap`) → the isolation census goes RED; M-RMP-4 (the tree loader stops refusing a cycle) → TC-RM-01 goes RED.

### HLR-RMM.1 — A typed multi-parent graph, built under the profile
- **Traceability:** US-RM-001
- **Ledger:** LED-2026-10-25-relmap-r1-batch.9, LED-2026-10-25-relmap-r1-batch.10, LED-2026-10-25-relmap-r1-batch.13
- **Statement:** When given a node list, an edge list and a profile, the model builder shall return a read-only graph that holds every valid node and edge — including a node with more than one parent — and shall report each invalid element as a typed problem, excluding it, instead of raising; and if the input exceeds the node or edge cap it shall refuse, naming the limit.
- **Rationale (informative):** MAP-TYPES §2.1 ("validates every loaded/derived edge against the profile"); C9 item 1 (counts).
- **Validation:** `test`
- **Executed verification:** planned `tests/test_relmap_model.py` (ported oracles: `qm:test_model.py` load/validate arms, re-derived over the reqharness profile).
- **Numeric pass threshold:** 6 problem kinds each reported once per offending element with the rest of the graph intact; cap+1 refuses, cap loads.
- **Priority:** high
- **Acceptance (black-box):**
  - **Observable outcome:** counts on the summary line equal an independent count of the fixture canon, and `nodes + skipped = parsed rows` (skipped rows are counted on the `structure: skipped N canon rows` line; "parsed rows" are the objects `parse_canon` returned — rows whose id matched `_ROW_ID_RE` and whose cell count matched the header); a multi-parent fixture is not possible through the canon, so the multi-parent property is Layer A.
  - **Shipped surface:** `mapper --audit <repo>`.
  - **Acceptance test(s):** AT-117, AT-124
  - **Boundary catalog (QC-3):** ☑ empty (canon with zero rows: `nodes=0`, no error) ☑ boundary (cap±1) ☑ invalid (six problem kinds, each counted on the notes line, never listed by value) ☑ error (cap refusal)
  - **Negative control:** mutation M-RMM-1 (drop the disallowed-pair check) → the problem-kind arms go RED.

### HLR-RMM.2 — Queries follow the direction of change
- **Traceability:** US-RM-001
- **Ledger:** none
- **Statement:** The graph shall answer `up`, `down`, `reach` and `neighbourhood` for every node according to the profile's direction-of-change table, deterministically and without mutating the graph.
- **Rationale (informative):** MAP-TYPES §2.1/§3.2; premise 6 fixes the `binds` reading to the normative rule.
- **Validation:** `test`
- **Executed verification:** planned `tests/test_relmap_model.py` (`qm:test_model.py` direction/reach/neighbourhood oracles, re-derived).
- **Numeric pass threshold:** for the four-type fixture, change at an LLR reaches exactly its verifying TCs and the ATs bound to them; change at a US reaches its HLRs, their LLRs, its covering ATs and their bound TCs (premise 6 transcript).
- **Priority:** high
- **Acceptance (black-box):**
  - **Observable outcome:** Layer A only in R1 — no shipped surface prints `up`/`down`/`reach` for a node (R2's lens does). Declared, not hidden.
  - **Shipped surface:** the `mapper.relmap` API (in-process); the first end-to-end observation is R2.
  - **Acceptance test(s):** none in R1 — carried to R2 (OQ-R1-2)
  - **Boundary catalog (QC-3):** ☑ empty (isolated node: reach 0) ☑ boundary (`hops` = 0, 1, beyond diameter) ☑ invalid (unknown node id → defined result) ☐ error
  - **Negative control:** mutation M-RMM-2 (reverse `change_downstream`) → direction arms go RED.

### HLR-RMM.3 — Cycles are reported, never refused
- **Traceability:** US-RM-002
- **Ledger:** none
- **Statement:** If the edge set contains a directed cycle, the graph shall record it, flag each cycle edge, and still load; the detection shall not recurse.
- **Rationale (informative):** HANDOFF §5.4 and MAP-TYPES §6.3: tree refuses, relation reports. Premise 5: with the approved pairs a cycle cannot arise from the canon, so the guarantee is the engine's and a synthetic profile exercises it.
- **Validation:** `test`
- **Executed verification:** planned `tests/test_relmap_model.py::test_cycle_*` over a synthetic profile that allows a loop.
- **Numeric pass threshold:** a 3-cycle and a self-loop are reported; a 100,000-node chain loads without `RecursionError`.
- **Priority:** medium
- **Acceptance (black-box):** none through the shipped surface (premise 5: unreachable from the canon). **Layer A only**, declared with the premise.
- **Boundary catalog (QC-3):** ☑ empty (acyclic) ☑ boundary (self-loop, two disjoint cycles) ☑ error (deep chain)
- **Negative control:** mutation M-RMM-3 (raise on cycle) → the report arms go RED.

### HLR-RMG.1 — The reqharness gap catalogue, ranked
- **Traceability:** US-RM-002
- **Ledger:** LED-2026-10-25-relmap-r1-batch.3, LED-2026-10-25-relmap-r1-batch.10, LED-2026-10-25-relmap-r1-batch.13
- **Statement:** The gap detector shall report every gap of the approved reqharness catalogue whose node kinds are sourced, each with severity, kind, node, a sentence and reach, ranked by severity (HIGH, MED, LOW) and then by reach, descending, and a gap whose node has canon rows the adapter could not parse or link under its id shall say so in its sentence.
- **Rationale (informative):** MAP-TYPES §7.1 (OQ8 accepted), §6.1 staging note. `UNDATED, CANNOT BE PLACED` is timeline-only and is R4's.
- **Validation:** `test`
- **Executed verification:** planned `tests/test_relmap_gaps.py` (`qm:test_gaps.py` ranking/detector oracles, re-derived).
- **Numeric pass threshold:** 8 catalogue kinds, each with a positive and a negative arm; ranking arms on a fixture with ≥ 2 severities and ≥ 2 reaches within one severity; the snapshot canon yields 7 gaps of which exactly 2 are qualified.
- **Priority:** high
- **Acceptance (black-box):**
  - **Observable outcome:** the audit prints `MED · HLR WITHOUT LLR` for an active HLR with no LLR and prints nothing for one with LLRs; a retired HLR is not reported; a gap on an HLR with unparsed or unlinked canon rows under its id is still printed, its sentence qualified.
  - **Shipped surface:** `mapper --audit <repo>`.
  - **Acceptance test(s):** AT-118, AT-125
  - **Boundary catalog (QC-3):** ☑ empty (no HLR: zero gaps) ☑ boundary (an active HLR whose only LLR is withdrawn is NOT a gap — the withdrawn LLR is traversed; LLR-RMG.1.2) ☑ invalid (status word outside the five: ineligible, counted) ☐ error
  - **Negative control:** mutation M-RMG-1 (drop the status eligibility) → AT-118 goes RED on the retired-HLR arm; M-RMG-4 (drop the qualifier) → AT-125 goes RED.

### HLR-RML.1 — Relation files are read under the shipped limits
- **Traceability:** US-RM-004
- **Ledger:** LED-2026-10-25-relmap-r1-batch.1, LED-2026-10-25-relmap-r1-batch.5, LED-2026-10-25-relmap-r1-batch.6, LED-2026-10-25-relmap-r1-batch.10, LED-2026-10-25-relmap-r1-batch.13, LED-2026-10-25-relmap-r1-batch.20
- **Statement:** When a relation descriptor is a link or not a regular file, exceeds the byte cap, contains a YAML anchor or alias, nests deeper than the depth cap, is binary or not valid UTF-8 text, is not valid YAML, or names an unsupported kind, profile, source or path, the reader shall refuse it with one of the 17 fixed causes of the closed set (K1–K17) and the file's base name, evaluate at most 8 descriptors, and continue the audit.
- **Rationale (informative):** C9 — "ingestion hardening applies to all relation files" (MAP-TYPES §2.1). Reuse, not reinvention: the hygiene batch's reader, constants and prescan.
- **Validation:** `test`
- **Executed verification:** planned `tests/test_relmap_descriptor.py`; the store arms of `tests/test_ingestion_limits.py` stay green and byte-identical.
- **Numeric pass threshold:** 17 causes each refuse with their own fixed text; a comment-padded valid descriptor at cap−1 loads; 9 descriptors → 8 evaluated and 1 overflow line; 0 crashes.
- **Priority:** high
- **Acceptance (black-box):**
  - **Observable outcome:** a `structure: refused (<base name>): <cause> - descriptor skipped` line whose cause is one of K1–K17 (rendered as in LLR-RMU.1.2); the review report above it is unchanged; exit code unchanged.
  - **Shipped surface:** `mapper --audit <repo>` with a crafted `<repo>/*.relmap.yml`.
  - **Acceptance test(s):** AT-121, AT-127
  - **Boundary catalog (QC-3):** ☑ empty (zero-byte descriptor → K11) ☑ boundary (cap−1 loads / cap+1 K5; total collection depth 64 loads / 65 refused K9 (the top-level mapping counts as depth 1); 8 / 9 descriptors) ☑ invalid (anchor, alias, non-mapping top level, `profile: [x]`, `source` not a mapping, unknown profile, `..` path, symlink, directory, `a: [`) ☑ error (non-UTF-8, big integer, multi-document stream)
  - **Negative control:** mutation M-RML-1 (skip the prescan) → AT-121's anchor arm goes RED; M-RML-7 (skip the `lstat` check) → AT-121's link arm goes RED.

### HLR-RMA.1 — The adapter derives the map from the canon, read-only and honest
- **Traceability:** US-RM-001
- **Ledger:** LED-2026-10-25-relmap-r1-batch.4, LED-2026-10-25-relmap-r1-batch.10, LED-2026-10-25-relmap-r1-batch.13, LED-2026-10-25-relmap-r1-batch.63, LED-2026-10-25-relmap-r1-batch.64
- **Statement:** When asked for the reqharness relation map of a repository, the adapter shall read the requirements canon through the bounded repository-file reader and the one canon parser, derive one node per HLR/LLR row and one `refines` edge per LLR whose id resolves to an HLR, list every row it could not parse and every LLR it could not link without guessing either, record on each HLR how many such rows sit under its id, mark US, AT and TC as unsourced, and write nothing.
- **Rationale (informative):** MAP-TYPES §5 (derived read-only) and §6.1 staging; premises 1–2 measured what the canon can and cannot give.
- **Validation:** `test`
- **Executed verification:** planned `tests/test_relmap_adapter.py` — exact figures (76/199/196, 7 reported, 3 unlinked) against the snapshot canon (C-35, executed against the real input as it stood at P1); against the LIVE `REQUIREMENTS.md` only invariants checked by an independent line counter.
- **Numeric pass threshold:** snapshot canon → 275 nodes, 196 edges, 7 reported, 3 unlinked; live canon → the invariants of LLR-RMA.1.1/.1.2 (no absolute count pinned); `git status` identical before and after.
- **Priority:** high
- **Acceptance (black-box):**
  - **Observable outcome:** the summary line counts and `structure note:` lines naming each reported row by id and the unlinked LLRs.
  - **Shipped surface:** `mapper --audit <repo>`.
  - **Acceptance test(s):** AT-117, AT-119, AT-124
  - **Boundary catalog (QC-3):** ☑ empty (canon file without HLR/LLR rows: empty map, no error) ☑ boundary (LLR id with no dot; id `LLR-X.1` whose parent is `HLR-X`; status `Active` or `active (partial)`; status empty or unknown) ☑ invalid (pipe-bearing row; duplicate ids, counted) ☑ error (canon missing, link, non-regular, binary, non-UTF-8, over the cap → `unavailable (canon: <K>)`)
  - **Negative control:** mutation M-RMA-1 (resolve an unlinked LLR to the nearest HLR prefix) → AT-119 goes RED (an edge appears that the canon does not support).

### HLR-RMU.1 — `--audit` carries the structural lines
- **Traceability:** US-RM-003
- **Ledger:** LED-2026-10-25-relmap-r1-batch.7, LED-2026-10-25-relmap-r1-batch.10, LED-2026-10-25-relmap-r1-batch.11, LED-2026-10-25-relmap-r1-batch.12, LED-2026-10-25-relmap-r1-batch.13, LED-2026-10-25-relmap-r1-batch.19, LED-2026-10-25-relmap-r1-batch.20, LED-2026-10-25-relmap-r1-batch.29, LED-2026-10-25-relmap-r1-batch.30, LED-2026-10-25-relmap-r1-batch.35, LED-2026-10-25-relmap-r1-batch.42, LED-2026-10-25-relmap-r1-batch.44
- **Statement:** When `mapper --audit <repo>` runs, it shall print, after the existing report, a bounded block of structure lines — an informational header, a summary, the sources, the ranked gaps, the skipped-rows line and the derivation notes — byte-identical from run to run, with every repository-derived value cut to 120 characters and then escaped like the rest of the report, and shall leave the exit code and every existing report line unchanged.
- **Rationale (informative):** MAP-TYPES §9 R1 "(ii) gaps + audit lines"; C2 "Needs: a line in `mapper --audit`".
- **Validation:** `test`
- **Executed verification:** planned `tests/test_relmap_audit.py` (subprocess, like `tests/test_reqharness_release.py`).
- **Numeric pass threshold:** existing audit tests pass unchanged; identical exit code with and without structural gaps (on a fixture whose `--audit` exits 0); ≤ 20 gap lines plus one overflow line; ≤ 10 note lines plus one overflow line; runs under two pre-picked `PYTHONHASHSEED` values (0 and 2, LED .30) print identical bytes.
- **Priority:** high
- **Acceptance (black-box):**
  - **Observable outcome:** the block on stdout, after the existing report; same exit code; no raw control character; no forged `verdict: ` line; no value longer than 120 characters before escaping; the first block line says the block is informational; the verdict is found by the prefix `verdict: ` and is no longer the last line of the output.
  - **Shipped surface:** `mapper --audit <repo>` (subprocess).
  - **Acceptance test(s):** AT-117, AT-120, AT-122, AT-126, AT-128, AT-129 (the raising-callable arm is Layer A: TC-RM-02)
  - **Boundary catalog (QC-3):** ☑ empty (no canon; no repository; no registry — one fixed `unavailable` line each) ☑ boundary (20 / 21 gaps; 120 / 121 characters) ☑ invalid (U+0301 and U+FE0F in an id, ESC and U+202E in a statement, U+2028 in a descriptor ignored key, a combining mark in a descriptor base name) ☑ error (callback raises — Layer A)
  - **Negative control:** mutation M-RMU-1 (print raw) → AT-122 goes RED per arm; M-RMU-2 (callback exception escapes) → TC-RM-02 goes RED; M-RMU-4 (call the hook for the no-repo report) → AT-126 goes RED; M-RMU-8 (exit 1 when a structural gap exists) → AT-120 goes RED.

---

## 4. Low-level requirements (LLR)

> Each LLR decomposes one HLR. ID format `LLR-<HLR>.<M>`. **C-36 flag:** the constants named here reconcile to `osopen` (premise 7); the profile names (`refines`, `covers`, `verifies`, `binds`), the six problem kinds and the eight catalogue kinds are **NEW — created in Phase 3** and tabulated below (truth tables) so no acceptance literal is a phantom.

### LLR-RMP.1.1 — The reqharness profile content
- **Traceability:** HLR-RMP.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.2, LED-2026-10-25-relmap-r1-batch.7, LED-2026-10-25-relmap-r1-batch.47
- **Statement:** The `reqharness` profile shall hold exactly these two tables, and `Profile` shall be a frozen value. Edge types:

| Edge | Allowed (src → dst) | A change flows | Evidence rule |
|---|---|---|---|
| `refines` | US→HLR · HLR→LLR | src → dst (downstream) | none |
| `covers` | AT→US | dst → src | optional |
| `verifies` | TC→LLR · TC→HLR | dst → src | required |
| `binds` | AT→TC | dst → src | graduated |

  Gap catalogue (DATA; patterns are a closed set — `cycle`, `lacks_in(kind, edge)`, `lacks_out(kind, edge[, peer kind])` and `edge_unevidenced(edge)`; `eligible` = the node's status is `active`; `open` = the node's `open` field is true):

| Gap kind | Severity | Pattern | Needs sourced | Sentence template (`<title>` cut to 120) |
|---|---|---|---|---|
| `TRACEABILITY CYCLE` | HIGH | `cycle` (node = first member, reach = reach of the first member) | — | `cycle of <n> nodes through <id>` |
| `US WITHOUT AT` | HIGH | `lacks_in(US, covers)`, eligible | US, AT | `<id> has no covering AT: <title>` |
| `OPEN AT WITHOUT TEST` | HIGH | `lacks_out(AT, binds)`, eligible, open | AT, TC | `<id> is open and bound to no test: <title>` |
| `VERIFIES WITHOUT EVIDENCE` | HIGH | `edge_unevidenced(verifies)` (node = the edge's src) | TC | `<src> verifies <dst> with no evidence` |
| `AT TAGGED ONLY` | MED | `edge_unevidenced(binds)` (node = the edge's src) | AT, TC | `<src> is tagged to <dst> with no evidence` |
| `LLR NOT VERIFIED` | MED | `lacks_in(LLR, verifies)`, eligible | LLR, TC | `<id> has no verifying TC: <title>` |
| `HLR WITHOUT LLR` | MED | `lacks_out(HLR, refines, LLR)`, eligible | HLR, LLR | `<id> has no LLR under it: <title>` |
| `ORPHAN TC` | LOW | `lacks_out(TC, verifies)` | TC | `<id> verifies nothing: <title>` |

- **Validation:** `test (unit)`
- **Executed verification:** `tests/test_relmap_profile.py` (provisional): `test_edge_table`, `test_catalogue_table` (cell by cell).
- **Numeric pass threshold:** 4 edge-type rows, 6 allowed pairs and 8 catalogue rows, equal cell by cell to the tables above (1 downstream type, 3 upstream; HIGH 4, MED 3, LOW 1); 1 `FrozenInstanceError` on assignment.
- **Negative control:** M-RMP-3 (flip `verifies` to downstream) → RED; M-RMP-5 (change one catalogue severity) → `test_catalogue_table` RED. **Boundary catalog:** ☑ invalid (a profile with an edge type or catalogue row whose kinds are not in `node_kinds` is refused at construction).

### LLR-RMP.1.2 — The engine is profile-blind
- **Traceability:** HLR-RMP.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.2
- **Statement:** The model and gaps modules shall contain no string literal equal to a node kind, an edge type or a gap kind of any shipped profile; the gap detectors in `gaps.py` shall be generic over the profile's catalogue table.
- **Validation:** `test (AST census)`
- **Executed verification:** `tests/test_relmap_isolation.py::test_engine_names_no_kind` — the literal set is DERIVED from the shipped profiles (C-31: 5 kinds + 4 edge types + 8 gap kinds), guarded by `len(set) >= 17`.
- **Numeric pass threshold:** 0 literals in `model.py`/`gaps.py`; the planted-violation arm finds ≥ 1.
- **Negative control:** M-RMP-1. **Boundary catalog:** ☑ empty-set guard (a census over an empty set is refused).

### LLR-RMP.2.1 — No edge between the kinds
- **Traceability:** HLR-RMP.2
- **Ledger:** LED-2026-10-25-relmap-r1-batch.5, LED-2026-10-25-relmap-r1-batch.15, LED-2026-10-25-relmap-r1-batch.16, LED-2026-10-25-relmap-r1-batch.46, LED-2026-10-25-relmap-r1-batch.57
- **Statement:** The relation-map package shall import, at any scope, only the standard library, PyYAML, and these `mapper` names: its own modules, from `mapper.osopen` the seven names `read_capped`, `ContentReadError`, `MAX_MAP_BYTES`, `MAX_NODES`, `MAX_EDGES`, `confine_reason`, `is_link`, `mapper.yamlscan`, and from `mapper.reqharness.derive` the names `parse_canon`, `CanonObject`, `LIMIT_ROLES_YML_BYTES`; `mapper/relmap/__init__.py` shall re-export nothing; every module that imports the package shall be `mapper/app.py` or inside the package; and, in the SAME increment that adds each importer, the ARCHITECTURE §2 `relmap` row shall list the path of every package file that exists, both `osopen` rows (§2 exposes, §3 inbound) shall name the importer, and the allow-list in `tests/test_arch_osopen_callers.py` shall gain its entry: Inc-1 `relmap/model.py` (`MAX_NODES`, `MAX_EDGES`); Inc-3 `yamlscan.py` (`MAX_DEPTH`, which `store.py` stops importing) and `relmap/descriptor.py` (`read_capped`, `ContentReadError`, `MAX_MAP_BYTES`, `confine_reason`, `is_link`).
- **Validation:** `test (AST census, derived from the tree)`
- **Executed verification:** `tests/test_relmap_isolation.py`; `tests/test_arch_osopen_callers.py` (exact set equality, run at every increment's exit); the existing `tests/test_repair_map_truth.py` and `tests/test_mod_*.py` gate the §2 row.
- **Numeric pass threshold:** 0 forbidden imports; §2 row paths = files on disk; allow-list equality holds after each of Inc-1 and Inc-3.
- **Negative control:** M-RMP-2; M-RMP-6 (`relmap/model.py` imports `MAX_NODES` without its allow-list entry) → `test_arch_osopen_callers` RED. **Boundary catalog:** ☑ function-local imports are counted (both import forms).

### LLR-RMM.1.1 — Builder, value shapes and floor
- **Traceability:** HLR-RMM.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.3, LED-2026-10-25-relmap-r1-batch.13, LED-2026-10-25-relmap-r1-batch.16, LED-2026-10-25-relmap-r1-batch.25, LED-2026-10-25-relmap-r1-batch.37, LED-2026-10-25-relmap-r1-batch.49, LED-2026-10-25-relmap-r1-batch.50, LED-2026-10-25-relmap-r1-batch.70, LED-2026-10-25-relmap-r1-batch.71, LED-2026-10-25-relmap-r1-batch.73
- **Statement:** `build_map(profile, nodes, edges, *, sourced)` shall return an immutable `RelMap` holding nodes and edges in input order, accepting any number of parents per node. `Node` shall be a frozen value with `id: str`, `kind: str`, `title: str = ""`, `status: str = "active"`, `open: bool = False`, `unparsed: int = 0`; `Edge` a frozen value with `src: str`, `dst: str`, `type: str`, `evidence_missing: bool = False` (graduated: ● an edge with evidence → False, ◐ a tagged edge without evidence → True, ○ no edge) and `in_cycle: bool = False` (set by the builder only). Every shipped `relmap` module shall parse under the Python 3.10 grammar and use no standard-library name introduced after 3.10. `RelMap.nodes` and `RelMap.edges` shall be tuples in input order, and `RelMap.node(id) -> Node | None` shall look a node up by id (the shapes R2 consumes; LED .37).
- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_model.py::test_multi_parent_and_order`, `::test_value_defaults`; `tests/test_relmap_isolation.py::test_py310_floor` (`ast.parse(feature_version=(3, 10))` plus a banned-name census over `mapper/relmap/*` and `mapper/yamlscan.py`, keyed on qualified names and `import` forms so a legitimate 3.10 call is not flagged: `enum.StrEnum`, `typing.Self`, `typing.assert_never`, `typing.LiteralString`, `tomllib`, `ExceptionGroup`, `itertools.batched`, `datetime.UTC`, `pathlib.Path.walk`; `os.walk` is allowed). The real run on a 3.10 interpreter is `not-run — no 3.10 interpreter on this machine, no CI`; an operator-run 3.10 check is a Phase 4 validation item.
- **Numeric pass threshold:** a node with 3 parents keeps 3 incoming edges; iteration order = input order; the six defaults above; the banned-name census finds 0 names and its planted-violation arm finds ≥ 1.
- **Negative control:** M-RMM-4 (sort nodes) → order arm RED; M-RMM-7 (plant `import tomllib` in a relmap module) → `test_py310_floor` RED. **Boundary catalog:** ☑ empty lists.

### LLR-RMM.1.2 — The six problem kinds
- **Traceability:** HLR-RMM.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.9, LED-2026-10-25-relmap-r1-batch.17, LED-2026-10-25-relmap-r1-batch.29, LED-2026-10-25-relmap-r1-batch.47, LED-2026-10-25-relmap-r1-batch.48, LED-2026-10-25-relmap-r1-batch.49, LED-2026-10-25-relmap-r1-batch.44, LED-2026-10-25-relmap-r1-batch.69, LED-2026-10-25-relmap-r1-batch.73
- **Statement:** The builder shall record one `Problem(kind, subject)` per offending element and exclude it, for exactly these kinds (the operator sees their counts per kind on the `structure: skipped N canon rows` line, never a subject value — LLR-RMU.1.2):

| Kind | Fires when | Excluded |
|---|---|---|
| `duplicate id` | a node id repeats | the later node |
| `unsafe id` | an id is empty, over 200 characters, or not `str.isprintable()` | the node |
| `unknown node kind` | a node kind is not in the profile | the node |
| `unknown edge type` | an edge type is not in the profile | the edge |
| `unknown endpoint` | an edge endpoint is not an accepted node | the edge |
| `disallowed pair` | the (src kind, dst kind) is not an allowed pair of that edge type | the edge |

- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_model.py::test_problem_*` (one arm per row, plus a mixed input, plus a U+2028-id arm that is `unsafe id` as a builder input).
- **Numeric pass threshold:** a mixed input with one element per kind yields 6 problems and a graph of the valid remainder.
- **Negative control:** M-RMM-1. **Boundary catalog:** ☑ an id with U+202E, U+200B (zero-width space) or ESC is `unsafe id` (excluded here, upstream of the escaper, and counted); U+2028 in a CANON id splits the line in `parse_canon` (`text.splitlines()`), so that row becomes a reported row (a note), never an `unsafe id`; as a builder input (Layer A) an id with U+2028 is `unsafe id` (LED .29). An id containing NBSP or any other whitespace fails `derive._ROW_ID_RE` (`^(HLR|LLR)-\S+$`), so `parse_canon` skips that row silently: it is neither a node nor reported nor counted, and is not an R1 gap.

### LLR-RMM.1.3 — Caps
- **Traceability:** HLR-RMM.1
- **Ledger:** none
- **Statement:** If the node count exceeds `osopen.MAX_NODES` or the edge count exceeds `osopen.MAX_EDGES`, `build_map` shall raise `RelMapLimitError` whose message names the limit, before building any index.
- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_model.py::test_caps` (cap loads, cap+1 refuses; constants read from `osopen`, never retyped).
- **Numeric pass threshold:** 100,000 nodes load; 100,001 raise naming `100000`.
- **Negative control:** M-RMM-5 (cap check removed) → RED. **Boundary catalog:** ☑ cap±1.

### LLR-RMM.2.1 — Direction of change
- **Traceability:** HLR-RMM.2
- **Ledger:** none
- **Statement:** For every edge `(src, dst, type)` the graph shall put `dst` in `down(src)` and `src` in `up(dst)` when the profile lists `type` as downstream, and `src` in `down(dst)` and `dst` in `up(src)` otherwise.
- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_model.py::test_direction_per_edge_type` (ported from `qm:test_model.py` `test_tc039_*`, re-derived) over a profile that makes each type downstream in turn.
- **Numeric pass threshold:** the premise-6 figures: LLR1 → {AT1, TC1}; US1 → {AT1, HLR1, LLR1, TC1}.
- **Negative control:** M-RMM-2. **Boundary catalog:** ☑ both orientations per type.

### LLR-RMM.2.2 — Reach, neighbourhood, immutability
- **Traceability:** HLR-RMM.2
- **Ledger:** LED-2026-10-25-relmap-r1-batch.8, LED-2026-10-25-relmap-r1-batch.28, LED-2026-10-25-relmap-r1-batch.32, LED-2026-10-25-relmap-r1-batch.37, LED-2026-10-25-relmap-r1-batch.39, LED-2026-10-25-relmap-r1-batch.45
- **Statement:** `reach(n)` shall equal the count of distinct nodes reachable through `down` excluding `n`; `neighbourhood(n, hops)` shall return `n` and every node within `hops` steps through `up` or `down` as a `frozenset[str]`; `up(n)` and `down(n)` shall return a `tuple[str, ...]` of ids in edge input order; all four shall be iterative (an explicit stack or queue, no recursion), return a defined empty result (`0`, the empty set, the empty tuple) for an unknown id, and leave the graph unchanged. Any memo of reach shall store counts (an integer per node or per cycle component), never a per-node reachable set. **One visit budget per `RelMap` (`VISIT_BUDGET = 2,000,000` node expansions over the object's lifetime, readable as `RelMap.visits`) is drawn on by every `reach` traversal, including the ones `rank_gaps` makes; every such traversal reads adjacency through `down` (the single counted seam); a traversal that would pass the budget is abandoned, nothing is memoised for it, and `reach` returns `None` ("not computed") instead of an `int` — never a hang and never a partial count. `neighbourhood` is not on the budget (it is O(V+E) per call): a view calls it for the focused node only.** `reach` is therefore typed `int | None`; `None` occurs only after the budget is spent (LED .39).
- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_model.py::test_reach_*`, `::test_neighbourhood_*` (ported from `qm:model.py:366-384`), `::test_reach_chain_at_cap` (a 100,000-node chain, the `MAX_NODES` shape: the head's `reach` is 99,999 with no `RecursionError`), `::test_reach_memo_is_counts` (a 2,000-node chain, sampled rows (LED .45): every retained memo value is an `int`, so no per-node set survives; the kill for M-RMM-10 needs no 100,000-node memory), `::test_reach_budget_per_row` (`reach` called for EVERY node of the 100,000-node chain, the per-row call a view would make: `visits <= VISIT_BUDGET`, at least one `None`, nothing raises; a counting wrapper installed on `RelMap.down` raises an `AssertionError` tripwire at `VISIT_BUDGET + 1` calls, so an unbounded traversal fails after about two million calls — no elapsed-time assertion and no out-of-memory kill; LED .32, .39).
- **Numeric pass threshold:** diamond fixture reach = 3 (no double count); `hops=0` → `{n}`; the chain head's reach = 99,999 with no `RecursionError` (a 30 s test timeout may exist as a last resort, never as an assertion); per-row `reach` over the whole chain ends with `visits <= 2,000,000` and at least one `None`.
- **Negative control:** M-RMM-6 (count paths not nodes) → diamond arm RED; M-RMM-8 (recursive implementation) → the chain arm RED; M-RMM-10 (cache the reachable set) → `test_reach_memo_is_counts` RED; M-RMM-11 (`reach` bypasses the shared budget) → `test_reach_budget_per_row` RED on the tripwire. **Boundary catalog:** ☑ unknown id.

### LLR-RMM.3.1 — Iterative cycle detection
- **Traceability:** HLR-RMM.3
- **Ledger:** none, LED-2026-10-25-relmap-r1-batch.47
- **Statement:** The builder shall compute the strongly connected components of size > 1 and every self-loop with an explicit stack, expose them as `cycles`, set `in_cycle` on each edge inside one, and never raise for a cycle.
- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_model.py::test_cycle_*` over a synthetic profile allowing `X→X`/`X→Y→X` (premise 5: the reqharness profile cannot form one).
- **Numeric pass threshold:** 2 disjoint cycles → 2 components; 100,000-node chain → 0 cycles, no `RecursionError`.
- **Negative control:** M-RMM-3. **Boundary catalog:** ☑ self-loop.

### LLR-RMG.1.1 — The detectors
- **Traceability:** HLR-RMG.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.2, LED-2026-10-25-relmap-r1-batch.3, LED-2026-10-25-relmap-r1-batch.23, LED-2026-10-25-relmap-r1-batch.43, LED-2026-10-25-relmap-r1-batch.51, LED-2026-10-25-relmap-r1-batch.52
- **Statement:** `detect_gaps(map)` shall be generic over `map.profile.gaps` (LLR-RMP.1.1): for each catalogue row whose needed kinds are all in `map.sourced` it shall evaluate the row's pattern — exactly the four implemented patterns `cycle`, `lacks_in`, `lacks_out`, `edge_unevidenced` — and emit one `Gap(severity, kind, node, sentence, reach)` per hit, the sentence filled from the row's template; for a `lacks_*` hit on a node with `unparsed > 0` the sentence shall end ` (canon rows near this id could not be parsed or linked: <n>)` with `<n>` = that count.
- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_gaps.py` — one positive and one negative arm per catalogue row over a synthetic fixture that sources all five kinds; `::test_gap_sentence_qualified`; the kind list is compared to MAP-TYPES §7.1 minus the R4 row.
- **Numeric pass threshold:** 8 kinds; `Gap` severities ∈ {HIGH, MED, LOW}; a qualified hit with `unparsed = 2` ends `(canon rows near this id could not be parsed or linked: 2)`, one with `unparsed = 0` carries no qualifier.
- **Negative control:** M-RMG-2 (swap two severities in the profile catalogue) → ranking arm RED; M-RMG-4 (drop the qualifier) → qualified arm RED. **Boundary catalog:** ☑ each row at 0 and 1 occurrences.

### LLR-RMG.1.2 — Activation and eligibility
- **Traceability:** HLR-RMG.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.3, LED-2026-10-25-relmap-r1-batch.4, LED-2026-10-25-relmap-r1-batch.13, LED-2026-10-25-relmap-r1-batch.23, LED-2026-10-25-relmap-r1-batch.33, LED-2026-10-25-relmap-r1-batch.50
- **Statement:** A gap kind whose Needs are not all sourced shall report nothing, and a node shall be eligible for the "eligible" rows only when its `status` is exactly `active`; every other status word — the four known ones, an empty word and an unknown word — is ineligible, and an ineligible node shall still count in `up`, `down` and `reach`. An active HLR whose only LLR is withdrawn has an outgoing `refines` edge and is therefore not a gap; a map with no HLR yields zero `HLR WITHOUT LLR` gaps.
- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_gaps.py::test_unsourced_kind_is_silent`, `::test_retired_node_not_reported_but_traversed`, `::test_withdrawn_only_llr_is_not_a_gap`; and, at Inc-4 in `tests/test_relmap_adapter.py` (it needs the adapter and the snapshot fixture, which land in Inc-4), `::test_snapshot_gaps` (the snapshot canon map; LED .33).
- **Numeric pass threshold:** the snapshot-canon map (HLR, LLR sourced; US/AT/TC not; asserted at Inc-4) yields only `HLR WITHOUT LLR`: 7 gaps, all MED, on `HLR-N13.3`, `HLR-N16.3`, `HLR-N16.4`, `HLR-REPAIR.1`, `HLR-S06.2`, `HLR-CAN.1`, `HLR-RS.3`, of which `HLR-CAN.1` and `HLR-REPAIR.1` end `(canon rows near this id could not be parsed or linked: 2)` and the other five carry no qualifier. The live canon asserts only that the count equals an independent count of active HLRs with no LLR id under them.
- **Negative control:** M-RMG-1; M-RMG-3 (ignore `sourced`) → `test_unsourced_kind_is_silent` (Inc-2, synthetic) and the snapshot arm (Inc-4) report `US WITHOUT AT` noise → RED; M-RMG-6 (treat a withdrawn LLR as no child) → `test_withdrawn_only_llr_is_not_a_gap` RED. **Boundary catalog:** ☑ status `deferred`, `superseded`, `withdrawn`, `split`, empty, `Active` (lower-cased upstream by LLR-RMA.1.1).

### LLR-RMG.1.3 — Ranking and the work bound
- **Traceability:** HLR-RMG.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.8, LED-2026-10-25-relmap-r1-batch.28, LED-2026-10-25-relmap-r1-batch.32, LED-2026-10-25-relmap-r1-batch.37, LED-2026-10-25-relmap-r1-batch.39, LED-2026-10-25-relmap-r1-batch.51, LED-2026-10-25-relmap-r1-batch.52
- **Statement:** `rank_gaps(map, gaps, limit)` (`limit: int | None`; `None` ranks every band, still inside the budget) shall order by severity HIGH, MED, LOW, then by reach descending, keeping detection order (which is input order) for ties; reach shall be computed iteratively, once per node (memoised as a count, never a set), once per cycle component (through its first member), and only for the gaps in the severity bands needed to fill `limit` printed lines; the node visits of a ranking are drawn from the map's ONE visit budget shared with `RelMap.reach` (LLR-RMM.2.2: `VISIT_BUDGET = 2,000,000`, readable as `RelMap.visits`), and the gaps whose `reach` returned `None` shall rank with reach 0 and be returned as a count (`reach_not_computed`).
- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_gaps.py::test_ranking` (ported from `qm:test_gaps.py`), `::test_rank_visit_cap` (a hub shape inside the 100,000 caps: 50,000 gaps sharing one 50,000-node downstream set; asserts `map.visits <= 2,000,000` and `reach_not_computed > 0`, with the `RelMap.down` tripwire of LLR-RMM.2.2 — no elapsed-time or memory kill), `::test_rank_100k_sinks` (100,000 gaps of reach 0), `::test_rank_limit_none_ranks_every_band` and `::test_rank_limit_none_stays_inside_the_budget` (`limit=None` ranks all bands and stays inside the budget; LED .32, .37, .39, .52).
- **Numeric pass threshold:** [MED reach 5, HIGH reach 0, MED reach 9] → [HIGH 0, MED 9, MED 5]; equal keys keep order; the hub shape ends with `visits <= 2,000,000`, `reach_not_computed > 0` and no recursion; the 100,000-sink shape ends with `reach_not_computed = 0` and `visits <= 2,000,000`.
- **Negative control:** M-RMG-2; M-RMG-5 (no visit bound, reach recomputed per gap) → the hub arm trips the `down` wrapper after 2,000,001 calls, RED (about two million calls, not 2.5×10^9). **Boundary catalog:** ☑ ties ☑ bound reached.

### LLR-RML.1.1 — Reading a descriptor
- **Traceability:** HLR-RML.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.5, LED-2026-10-25-relmap-r1-batch.6, LED-2026-10-25-relmap-r1-batch.13, LED-2026-10-25-relmap-r1-batch.21, LED-2026-10-25-relmap-r1-batch.31, LED-2026-10-25-relmap-r1-batch.41, LED-2026-10-25-relmap-r1-batch.66
- **Statement:** `load_descriptor(path, repo)` shall read the file through `read_repo_text` (LLR-RML.1.5), run `yamlscan.prescan` on the text, then `yaml.safe_load` (a `YamlLimitError` of kind `anchor` is K8 and of kind `depth` is K9), and shall raise `DescriptorError(cause)` with `cause` one of the fixed strings K1–K7 (LLR-RML.1.5) or K8 `contains YAML anchors or aliases`, K9 `nests deeper than the depth limit`, K10 `not valid YAML`; the printed message is the cause and the file's BASE NAME only — never `str(exc)`, a path, an anchor name or a YAML snippet. Every failure of the prescan (`yaml.parse`) or of `safe_load` — `yaml.YAMLError` (including `ConstructorError` for an unhashable key and `ComposerError` for a multi-document stream), `ValueError` (an integer over the 4,300-digit limit) and `RecursionError` — is K10. The closed table `CAUSE` (K1–K17 → fixed text) shall be read-only (`types.MappingProxyType`), so no caller can rewrite the set at run time.
- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_descriptor.py` (one arm per cause K1–K10; `::test_cause_is_read_only` (item assignment on `CAUSE` raises `TypeError`); cap−1 loads with a comment-padded VALID descriptor of exactly `MAX_MAP_BYTES − 1` bytes — a sparse or zero-filled file is refused as binary by the NUL probe before the cap matters, so it is K6, not a cap arm; cap+1 → K5; the real constant, never a monkeypatched cap).
- **Numeric pass threshold:** K1–K10 → 10 distinct messages each equal to its fixed string; total collection depth 64 loads, 65 refused (the top-level mapping counts as depth 1) → K9; a hostile YAML snippet, a syntactically invalid descriptor (`a: [`, which fails in the prescan) and a 5,000-digit integer print only K10; a UTF-8 BOM before valid YAML loads; `tests/test_reqharness_yaml_census.py` stays green (`safe_load` only).
- **Negative control:** M-RML-1; M-RML-2 (path in message) → RED; M-RML-10 (format `str(exc)` on a parse failure) → the hostile-snippet arm RED; M-RML-15 (a net that omits the prescan call) → the `a: [` arm RED; M-RML-17 (`CAUSE` a plain `dict`) → `test_cause_is_read_only` RED. **Boundary catalog:** ☑ cap±1, depth ±1, multi-document stream, big integer.

### LLR-RML.1.2 — Descriptor schema (truth table)
- **Traceability:** HLR-RML.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.5, LED-2026-10-25-relmap-r1-batch.6, LED-2026-10-25-relmap-r1-batch.13, LED-2026-10-25-relmap-r1-batch.37, LED-2026-10-25-relmap-r1-batch.43
- **Statement:** The descriptor shall be accepted or refused by this table; any other top-level key is kept as a note `descriptor key ignored: <key>` (the key `str()`-coerced, cut to 120), never an error:

| Input | Result |
|---|---|
| no descriptor file in the repo root | the default descriptor, returned by `default_descriptor()`: `Descriptor(profile="reqharness", canon="REQUIREMENTS.md", us_canon=None, at_table=None, ignored_keys=())` |
| top level is not a mapping (a list, a scalar, an empty file, a comment-only file) | K11 `not a mapping` |
| `kind` present and not the string `relation` | K12 `unsupported kind` |
| `profile` present and not the string `reqharness` (including `lineage`, a list, a number) | K13 `unsupported profile` (`lineage` waits for R5) |
| `source` present and not a mapping | K15 `source is not a mapping` |
| `source.canon` present and not the string `REQUIREMENTS.md` | K14 `unsupported canon source` |
| `source.us_canon` / `source.at_table` set | accepted; the path is confined (LLR-RML.1.3); the adapter notes "configured, not derivable in R1" |
| a `source.us_canon` / `source.at_table` value that is not a string | K16 `source.<key> is not text` (`<key>` is `us_canon` or `at_table`) |

- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_descriptor.py::test_schema_table` (one arm per row, plus `profile: [x]`, `profile: {a: b}`, `kind: [1]`, `source: [1]`, an empty file).
- **Numeric pass threshold:** 8 rows → 8 verdicts; `profile: [x]` is K13 (0 `TypeError`); an empty file is K11.
- **Negative control:** M-RML-3 (accept `lineage`) → RED; M-RML-11 (compare `profile` with `in` over a set without a type check) → the `profile: [x]` arm raises, RED. **Boundary catalog:** ☑ empty mapping `{}` (accepted: all defaults).

### LLR-RML.1.3 — Descriptor paths
- **Traceability:** HLR-RML.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.6, LED-2026-10-25-relmap-r1-batch.41, LED-2026-10-25-relmap-r1-batch.43
- **Statement:** The descriptor's `us_canon` and `at_table` strings shall pass `osopen.confine_reason(text, repo)` before any filesystem call and shall otherwise be refused as K17 `unsafe path in <field> (<reason>)` with `<field>` one of `us_canon`, `at_table` and `<reason>` one of `allow_list`, `colon`, `normalised`, `outside`, `link`, `unreadable`; R1 shall not open them. `read_repo_text` is a file-type guard, not a confinement: the batch that first opens `us_canon` or `at_table` shall call `osopen.confine_reason` again at open time and then `read_repo_text`.
- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_descriptor.py::test_paths_confined` (absolute, UNC, `..`, device name, drive-letter, reparse-link arms taken from `tests/test_inc9n.py`'s vocabulary).
- **Numeric pass threshold:** 5 unsafe forms refused as K17, 1 relative form accepted; 0 file opens and 0 `stat` calls for a UNC string (monkeypatched `open` and `os.stat` raise).
- **Negative control:** M-RML-4 (skip confinement) → RED. **Boundary catalog:** ☑ reserved device names.

### LLR-RML.1.4 — The prescan moves, its wording does not
- **Traceability:** HLR-RML.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.1, LED-2026-10-25-relmap-r1-batch.14, LED-2026-10-25-relmap-r1-batch.15, LED-2026-10-25-relmap-r1-batch.35, LED-2026-10-25-relmap-r1-batch.53, LED-2026-10-25-relmap-r1-batch.54, LED-2026-10-25-relmap-r1-batch.55
- **Statement:** `mapper/yamlscan.py` shall hold the one iterative prescan, define `ANCHOR_NAME_DISPLAY` (40) and be the only importer of `osopen.MAX_DEPTH` (`store.py` stops importing it), and raise `YamlLimitError(Exception)` — not a `ValueError` or `yaml.YAMLError` subclass — carrying `kind` (`anchor` or `depth`), `shown` (the anchor name cut at `ANCHOR_NAME_DISPLAY` characters plus `…` when cut; empty for depth) and `limit` (the integer `MAX_DEPTH`) for the first anchor/alias or for nesting past `MAX_DEPTH`; `MapStore` shall call it from both former call sites (`load`, `_capped_side_graph`), convert `YamlLimitError` into `MapStoreError` inside the existing `try`, ahead of the `(yaml.YAMLError, ValueError, RecursionError)` net, so every refusal string is byte-identical to the one it replaces; a `yaml.YAMLError` from `yaml.parse` still propagates to the callers' net. Byte-identity is pinned BEFORE the move by a characterization golden captured on the base commit: the exact strings of 4 refusals (short anchor, alias, a 5,000-character anchor — 40 characters plus `…` —, nesting depth 65) × 2 call sites (`MapStore.load`, and `_capped_side_graph` called directly because `git_diff` turns every refusal into `None`) = 8 strings. **Provenance (LED .35):** the 8 constants are generated by RUNNING the base code (not typed): the capture command and the base SHA are recorded in the Inc-3 packet, and the golden is committed ALONE, before the commit that edits `store.py`, so the golden commit itself (with `store.py` untouched) is the GREEN-on-base evidence.
- **Validation:** `test`
- **Executed verification:** `tests/test_prescan_refusal_goldens.py` (NEW, lands in Inc-3 before the move, on the base `store.py`: GREEN there, RED when a refusal is reworded — the C-40 counterfactual); `tests/test_ingestion_limits.py` unchanged (it asserts substrings and `len(msg) <= 160`, NOT byte identity — the golden is the byte-identity limb); `tests/test_yamlscan.py` for the leaf (`test_limit_error_is_not_valueerror`); a census that `store.py` no longer defines the prescan logic.
- **Numeric pass threshold:** 8 of 8 strings equal the golden byte for byte before and after the move; 0 changes to `tests/test_ingestion_limits.py`; 10,000-deep nesting refused in milliseconds, no `RecursionError`.
- **Negative control:** M-RML-6 (reword the fixed text of the anchor refusal, `are not allowed here` → `are not permitted here`) → the golden goes RED while `tests/test_ingestion_limits.py` stays GREEN (ledger .53; the `{shown!r}` → `{shown}` form turns two old arms RED as well, so it is not the golden's distinguishing mutant); M-RML-5 (leaf drops the alias check) → the store's anchor/alias arms, the golden and the descriptor's K8 arm go RED; M-RML-12 (`YamlLimitError` derives `ValueError`) → `tests/test_yamlscan.py::test_limit_error_is_not_valueerror` goes RED; the golden does not see it, because `_prescan_sidecar` catches `YamlLimitError` itself ahead of the net (ledger .54). **Boundary catalog:** ☑ depth 64/65, anchor named truncated at 40.
- **Out of scope (BACKLOG B-144):** `reqharness/config.py` keeps its own prescan; ARCHITECTURE R-017 records it, and its fold into the leaf is a later batch.

### LLR-RML.1.5 — Repository file reads and the closed read causes
- **Traceability:** HLR-RML.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.5, LED-2026-10-25-relmap-r1-batch.6, LED-2026-10-25-relmap-r1-batch.26, LED-2026-10-25-relmap-r1-batch.34, LED-2026-10-25-relmap-r1-batch.35, LED-2026-10-25-relmap-r1-batch.41, LED-2026-10-25-relmap-r1-batch.43
- **Statement:** `read_repo_text(path, cap)` shall be the only way the relation-map package reads a repository file (the canon and every discovered descriptor; `us_canon` and `at_table` are never opened): it shall `os.lstat` the path, refuse a link or reparse point (`osopen.is_link`) and any non-regular file before any open, then open the path once (`os.open` read-only, `O_NONBLOCK` where present), compare the `os.fstat` identity (`st_dev`, and `st_ino` only when both inode values are non-zero, because some network and FAT mounts report 0) and regular-file type with the `lstat` result and refuse a mismatch as K2, close it, and read through `osopen.read_capped(path, cap)` with `cap` = `MAX_MAP_BYTES` for a descriptor and `derive.LIMIT_ROLES_YML_BYTES` for the canon, and shall raise `RepoReadError(cause)` (also carrying `limit`, the integer cap it was given, used only to render K5 as `exceeds the <N> byte limit`; the stored cause text stays `exceeds the byte limit`) with `cause` one of: K1 `is a link` · K2 `is not a regular file` · K3 `file not found` · K4 `could not read file` · K5 `exceeds the byte limit` · K6 `looks binary` · K7 `is not UTF-8 text` (K5–K7 classified from the prefix of the `ContentReadError` text; any other `OSError` is K4). A hard-linked regular file is read (the read is read-only). The window between the identity check and `read_capped`'s own open is accepted: it needs write access to the audited repository, and the read stays read-only and capped.
- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_descriptor.py::test_read_repo_text_*` over the canon name and a descriptor name: a symlink, or on Windows a directory junction (`mklink /J`, which needs no privilege and is a reparse point `osopen.is_link` is meant to catch) created by the test (`blocked`, never a silent skip, only if neither can be created), a directory, a missing file, an unreadable file, cap−1 (comment-padded valid text) and cap+1 (this arm INSTRUMENTS the read — it wraps the file object, or monkeypatches `open`, to record the bytes requested and asserts at most `cap + 1`, because a mutant that reads the whole file and then compares raises the same K5 text and the result alone cannot kill M-RML-8), a NUL byte, invalid UTF-8; a FIFO arm on platforms that have `mkfifo` (`n/a — Windows` stated), and an identity-mismatch arm (a monkeypatched `os.fstat` returning another inode → K2) and an `st_ino = 0` arm (both inodes 0: the file is read, not K2).
- **Numeric pass threshold:** 7 causes → 7 fixed strings; 0 `open` calls for a link, a directory or a FIFO (monkeypatched `open` raises); the canon cap equals the value `load_canon` enforced.
- **Negative control:** M-RML-7 (skip the `lstat` check) → the link and directory arms RED; M-RML-8 (read the whole file before the size check) → the cap+1 arm's bytes-read assertion RED (not its K5 result); M-RML-14 (skip the identity comparison) → the mismatch arm RED; M-RML-16 (refuse when an inode is 0) → the `st_ino = 0` arm RED. **Boundary catalog:** ☑ cap±1 ☑ link ☑ directory ☑ identity mismatch.

### LLR-RML.1.6 — Discovery and the descriptor census
- **Traceability:** HLR-RML.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.5, LED-2026-10-25-relmap-r1-batch.13, LED-2026-10-25-relmap-r1-batch.33
- **Statement:** The audit shall list the entries of the repository root (`Path(report.repo)`) whose name ends in `.relmap.yml` (case-sensitive), sorted by code-point order, evaluate at most 8 of them and print `structure: refused: more descriptors than the limit (8)` once when more exist; a matching entry that is a link, a directory or any non-regular file is refused as K1 or K2 under its base name; with no matching entry the default descriptor applies once; a refused descriptor yields its refusal line and no map block; the canon map is derived once per `--audit` run and shared by every block. **Census (batch rule, B1 miss of the hygiene batch):** the input class `*.relmap.yml` is NEW and its consumers are re-derived by CONTENT, not by file name: the readers of a repo-root `*.yml` today are `reqharness` config readers keyed on `reqharness/*.yml`, so `tests/test_reqharness_*` fixtures are searched for a root-level `*.relmap.yml` they would now trip over — recorded at Inc-3 (premise 10 found none tracked).
- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_descriptor.py::test_repo_root_census` (derived: scans the root, asserts the rule against a tmp repo with 0, 1, 2, 8, 9 descriptors, a directory and a link named `x.relmap.yml`) and, at Inc-5 in `tests/test_relmap_audit.py` (it runs through `structure_lines`, which lands in Inc-5), `::test_canon_derived_once` (monkeypatched `parse_canon` call count = 1 across 3 descriptors; LED .33).
- **Numeric pass threshold:** 9 descriptors → 8 evaluated + 1 overflow line; name order; 2 descriptors → 2 blocks; `parse_canon` called once.
- **Negative control:** M-RML-9 (derive per descriptor) → the once-arm RED; M-RML-13 (no count cap) → the 9-descriptor arm RED. **Boundary catalog:** ☑ 0, 1, 8, 9 descriptors ☑ non-regular entry.

### LLR-RMA.1.1 — Nodes from the canon
- **Traceability:** HLR-RMA.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.4, LED-2026-10-25-relmap-r1-batch.5, LED-2026-10-25-relmap-r1-batch.13, LED-2026-10-25-relmap-r1-batch.22, LED-2026-10-25-relmap-r1-batch.24, LED-2026-10-25-relmap-r1-batch.31, LED-2026-10-25-relmap-r1-batch.36, LED-2026-10-25-relmap-r1-batch.61, LED-2026-10-25-relmap-r1-batch.72
- **Statement:** `derive_reqharness_map(repo, descriptor)` shall read `<repo>/REQUIREMENTS.md` through `read_repo_text` (LLR-RML.1.5), parse it with `reqharness.derive.parse_canon`, and create one node per returned object, with `kind` = its class (`HLR`/`LLR`), `title` = its statement (whitespace collapsed, at most 120 characters, ending `…` when cut), `status` = the first word of its Status cell lower-cased (the empty word for an empty cell), `open = False`, in canon order, and shall set `sourced = {HLR, LLR}`; a status word outside {active, deferred, superseded, withdrawn, split} keeps the node, makes it ineligible and is counted as `unknown_status` (only nodes the builder kept are counted: a duplicate or unsafe id is a builder problem, never a node, LED .61); an unreadable canon raises `CanonUnavailable(cause)` with `cause` one of K1–K7; a canon with no HLR/LLR row yields an empty map and no error. The reader is stricter than `reqharness.derive.load_canon` BY DESIGN: a symlinked or non-regular canon is `unavailable (canon: is a link)` here while the review report may still count it, because a read-only structure report must not follow a link out of an untrusted clone (security F1); the divergence is recorded in the ARCHITECTURE `relmap` row.
- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_adapter.py::test_snapshot_census` (the snapshot canon, C-35: exact figures); `::test_live_invariants` (the live `REQUIREMENTS.md` against an independent line counter: `nodes = counted HLR/LLR table rows − reported`, no node carries a reported row's id; the live figures are recorded in the packet as evidence, never asserted); `::test_status_words` (`Active`, `active (partial)`, empty, `done`); `::test_canon_causes` (one arm per K1–K7 over the canon); `::test_snapshot_sha256` (the fixture `tests/fixtures/relmap/REQUIREMENTS.snapshot.md` is created in Inc-4, and its LF-normalised sha256 (`bytes.replace(b"\r\n", b"\n")`, then sha256) equals `b093c9203f0fe75f218298f56cc723a812902a1f4979424c8c2cb931bd39a25a` — the digest of `git show HEAD:REQUIREMENTS.md`; entry .4's `93b18472…` is the digest of the CRLF working copy and is corrected by entry .36 — the test carries the value as a constant and cross-checks the ledger text while the batch folder exists, so a quiet edit cannot change every exact oracle; `::test_snapshot_sha256_crlf_arm` hashes a CRLF-rewritten copy of the fixture and must give the same value; `.gitattributes` also carries `tests/fixtures/relmap/** -text` (defence in depth; the LF-normalised hash is the authoritative pin); Inc-4 exit runs `test_snapshot_sha256` from a fresh LF checkout).
- **Numeric pass threshold:** snapshot → 275 nodes; first node `HLR-CNV.1`; every snapshot `status` ∈ {active, deferred, superseded, withdrawn, split}; `Active` → `active`, `active (partial)` → `active`, `` and `done` → ineligible, counted.
- **Negative control:** M-RMA-2 (second canon reader) → the "one reader" arm (the adapter's `parse_canon` call count over a monkeypatch = 1) RED; M-RMA-6 (skip the last table row) → the live-invariant arm RED; M-RMA-7 (append a byte to the fixture) → `test_snapshot_sha256` RED; M-RMA-9 (hash the raw bytes) → the CRLF arm RED. **Boundary catalog:** ☑ empty canon; ☑ every K1–K7 cause.

### LLR-RMA.1.2 — Rule D-1 and the unlinked list
- **Traceability:** HLR-RMA.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.4
- **Statement:** For each LLR id the adapter shall drop the last dot-separated segment of the part after `LLR-`, prefix `HLR-`, and emit a `refines` edge from that HLR to the LLR only when that id is a node of class `HLR`; an LLR with no dot, or whose candidate is absent or not an HLR, shall be listed as unlinked and given no edge.
- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_adapter.py::test_rule_d1_table` (truth table below), the snapshot census and the live invariants.

| LLR id | Candidate | Candidate present? | Result |
|---|---|---|---|
| `LLR-Q2.1.1` | `HLR-Q2.1` | yes | edge |
| `LLR-001.1` | `HLR-001` | yes | edge |
| `LLR-REPAIR.1` | `HLR-REPAIR` | no | unlinked |
| `LLR-X` | (no dot) | — | unlinked |
| `LLR-RH.6.2` | `HLR-RH.6` | no (row unparsed) | unlinked |

- **Numeric pass threshold:** snapshot canon → 196 edges, 3 unlinked (`LLR-REPAIR.1`, `LLR-REPAIR.2`, `LLR-RH.6.2`); live canon → `edges + unlinked = LLR nodes` and every edge's source is the D-1 candidate of its target.
- **Negative control:** M-RMA-1. **Boundary catalog:** ☑ the five rows.

### LLR-RMA.1.3 — Reported rows are never guessed, but they qualify
- **Traceability:** HLR-RMA.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.3, LED-2026-10-25-relmap-r1-batch.4, LED-2026-10-25-relmap-r1-batch.18, LED-2026-10-25-relmap-r1-batch.23, LED-2026-10-25-relmap-r1-batch.58, LED-2026-10-25-relmap-r1-batch.60
- **Statement:** The adapter shall carry every row `parse_canon` reported, in order, as one derivation note per row whose printed text is the row's id read from its report line (`unparsed row <id>`; a report line that yields no id prints `unparsed canon line`; `Derivation.reported` holds exactly this printed text, repository-derived and uncut, and the full report text is not retained: Layer A reads it from `parse_canon`, LED .58), shall create no node and no edge from a reported row, and shall set `Node.unparsed` of each HLR node to the number of orphan rows related to it: an orphan row is a reported row whose id is read from its report line (`cannot parse row for '<id>'`; a line that yields no id contributes nothing) or an unlinked LLR (only `LLR-` ids count: a reported `HLR-` row is a note and relates to no HLR, LED .60), and `LLR-<t>` is related to `HLR-<s>` when `<t>` starts with `<s>.`, or when `<s>` contains a dot and the orphan's rule-D-1 candidate stem equals `<s>` minus its last dot-separated segment.
- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_adapter.py::test_reported_rows_are_notes` (a pipe-bearing row fixture; plus the snapshot count 7) and `::test_unparsed_counts`, `::test_report_line_shape_yields_id` (a tripwire: the text `parse_canon` reports for a pipe-bearing row still contains `cannot parse row for '<id>'`, so a rewording in `derive.py` fails loudly instead of zeroing `unparsed`).
- **Numeric pass threshold:** snapshot canon → 7 reported-row notes, in canon order, `unparsed row LLR-HYG.1.1` … `unparsed row LLR-Q3.1.2`; the node ids `HLR-RH.6`, `LLR-RH.6.1` absent; `HLR-CAN.1.unparsed = 2` (`LLR-CAN.1.1`, `LLR-CAN.1.2`), `HLR-REPAIR.1.unparsed = 2` (`LLR-REPAIR.1`, `LLR-REPAIR.2`), 0 on the five other gap HLRs.
- **Negative control:** M-RMA-3 (re-parse the row by splitting on the first 4 pipes) → RED; M-RMA-5 (count only the starts-with branch) → the `HLR-REPAIR.1` arm RED. **Boundary catalog:** ☑ a row with fewer cells than the header ☑ a report line with no id.

### LLR-RMA.1.4 — Staged sources and read-only
- **Traceability:** HLR-RMA.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.59
- **Statement:** The adapter shall record US, AT and TC as unsourced, shall perform no write, spawn no process and open no file other than the canon; a configured `us_canon` / `at_table` is never opened and the adapter emits no note for it: the audit's sources line shows the configured string (LED .59).
- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_adapter.py::test_readonly` (tmp repo tree hash before/after; monkeypatched `subprocess` and `open(…, 'w')` raise); `tests/test_relmap_isolation.py` (no `subprocess` import).
- **Numeric pass threshold:** 0 writes, 0 processes, 0 extra opens.
- **Negative control:** M-RMA-4 (adapter opens `us_canon`) → RED. **Boundary catalog:** ☑ both set.

### LLR-RMU.1.1 — The hook
- **Traceability:** HLR-RMU.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.11, LED-2026-10-25-relmap-r1-batch.13, LED-2026-10-25-relmap-r1-batch.16, LED-2026-10-25-relmap-r1-batch.35, LED-2026-10-25-relmap-r1-batch.38, LED-2026-10-25-relmap-r1-batch.41, LED-2026-10-25-relmap-r1-batch.42, LED-2026-10-25-relmap-r1-batch.43, LED-2026-10-25-relmap-r1-batch.62, LED-2026-10-25-relmap-r1-batch.67, LED-2026-10-25-relmap-r1-batch.75
- **Statement:** `reqharness.audit.run_cli(argv, extra_lines=None)` shall, when `extra_lines` is given, print after the existing report: for the no-repo report (`report.chain_status == identity.NO_REPO`) the line `structure: unavailable (no repository)`, for the no-registry report (`report.chain_status == NO_REGISTRY`) the line `structure: unavailable (no registry)` — told apart by `chain_status`, never by verdict text — and for every other report the lines returned by one call of `extra_lines(Path(report.repo))` — `report.repo` being the repository root `audit` resolved — each through the report's escaper and consuming at most 1,000 lines from the callable (when a 1,001st exists it is not printed and one line `structure: output truncated at 1000 lines` follows); the exit code shall be the same as without the hook; if `build_map` raises `RelMapLimitError` inside the derivation, `structure_lines` prints the header and one line `structure: unavailable (canon: over the node or edge limit)` (LED .62); if the callable raises, `run_cli` shall print one line `structure: unavailable (internal error: <exception type name>)` and return the same code; when `audit` itself refuses (the `--baseline` refusal, or any exception before a report exists) no structure line is printed and the callable is not called; `app.py` shall pass `relmap.audit.structure_lines`, and `reqharness` shall import nothing from `relmap`. The `verdict: ` line is no longer the last line of the output: a reader finds it by the prefix `verdict: ` (the first block line says so on screen, LLR-RMU.1.2; the ARCHITECTURE `relmap` row and the Inc-5 packet repeat it for CI steps that read the last line).
- **Validation:** `test`
- **Executed verification:** Layer A, in-process: `tests/test_relmap_audit.py::test_tc_rm_02_raising_callable` (`run_cli(argv, extra_lines=raiser)` with `capsys`; the raising arm is not reachable from the shipped CLI). `::test_tc_rm_03_refusal_path` (`run_cli(['--audit', <repo>, '--baseline', <unknown name>], extra_lines=spy)`: the refusal on stderr, exit code 1, the spy never called, 0 structure lines on stdout), `::test_hook_line_bound` (a generator yielding 5,000 lines: 1,000 printed, then the truncation line, and the generator is not exhausted). Layer B: AT-120, AT-126 (subprocess). `tests/test_reqharness_release.py` and `tests/test_reqharness_modgraph.py` unchanged and green (the reverse census of the 16 `--audit` subprocess sites — 10 print the block, 6 are refused before the hook — is in the design proposal §5.2); the A3 pin `tests/test_a3_census.py:329` (`== 86`) must not move: relmap and its tests add no `.render(` attribute call, and every new file is `git add`ed before a targeted run.
- **Numeric pass threshold:** a raising callable → exit code identical to the no-hook run, 1 `unavailable` line, no traceback on stderr; no-repo and no-registry reports → exactly 1 fixed line each and 0 calls of the callable; the `--baseline` refusal → 0 calls and 0 structure lines (TC-RM-03).
- **Negative control:** M-RMU-2 (callback exception escapes) → TC-RM-02 RED; M-RMU-4 (call the hook for the no-repo report) → AT-126 RED; M-RMU-10 (call the hook, or print structure lines, on the baseline refusal path) → TC-RM-03 RED; M-RMU-12 (consume the hook output without a bound) → `test_hook_line_bound` RED. **Boundary catalog:** ☑ `extra_lines=None` is byte-identical to today (the compatibility limb).

### LLR-RMU.1.2 — Line formats
- **Traceability:** HLR-RMU.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.3, LED-2026-10-25-relmap-r1-batch.4, LED-2026-10-25-relmap-r1-batch.6, LED-2026-10-25-relmap-r1-batch.7, LED-2026-10-25-relmap-r1-batch.9, LED-2026-10-25-relmap-r1-batch.13, LED-2026-10-25-relmap-r1-batch.17, LED-2026-10-25-relmap-r1-batch.18, LED-2026-10-25-relmap-r1-batch.20, LED-2026-10-25-relmap-r1-batch.27, LED-2026-10-25-relmap-r1-batch.38, LED-2026-10-25-relmap-r1-batch.40, LED-2026-10-25-relmap-r1-batch.42, LED-2026-10-25-relmap-r1-batch.43, LED-2026-10-25-relmap-r1-batch.44, LED-2026-10-25-relmap-r1-batch.48, LED-2026-10-25-relmap-r1-batch.56, LED-2026-10-25-relmap-r1-batch.59, LED-2026-10-25-relmap-r1-batch.68, LED-2026-10-25-relmap-r1-batch.75, LED-2026-10-25-relmap-r1-batch.76
- **Statement:** `structure_lines(repo)` — a thin wrapper over the pure formatter `format_structure(relmap, gaps, notes, refusals)` — shall return these lines, per block in this order, using the profile's kind and edge names. The returned lines are repository-derived and UNESCAPED: the sink escapes them (`run_cli` does, through the report's escaper) and any other caller (an R2 status strip, a log) must escape too; `format_structure` itself performs the 120-character cut, so a caller that bypasses `structure_lines` still gets cut values (LED .40). A kind or edge type with a zero count is omitted from its parentheses, and a zero total prints with no parentheses (stated here once). Every repository-derived value printed (ids, titles, statements, descriptor base names, `us_canon`/`at_table` values, ignored keys, reported-row text) is cut to 120 characters, ending `…` when cut, BEFORE escaping.

| Line | Form |
|---|---|
| informational header | `structure: informational - does not change the verdict or the exit code` — the first line `structure_lines` returns, once per run, before the first `descriptor` label (also before a refusal, an overflow or an `unavailable (canon: …)` line); the fixed lines `run_cli` itself prints (`no repository`, `no registry`, `internal error`, `output truncated`) carry none |
| block label | `structure: descriptor <base name>`, or `structure: descriptor (built-in default)` when no descriptor file exists |
| summary | `structure: profile=reqharness nodes=<N> (<KIND>=<n>, …) edges=<E> (<type>=<e>, …) cycles=<C>` (profile order) |
| sources | `structure: sources: canon=REQUIREMENTS.md us_canon=<path or unset> at_table=<path or unset>` — `<path>` is the configured string as written in the descriptor (cut and escaped), never the resolved `Path`, so no absolute repository or home path is printed; a configured `~/x` is refused as K17 `unsafe path in us_canon (outside)` and never reaches this line |
| gap total | `structure: gaps: <G> (HIGH=<h>, MED=<m>, LOW=<l>)` (all three always printed) |
| gap | `structure gap: <SEVERITY> · <KIND> · <node> · reach=<r> · <sentence>` (≤ 20; the sentence is the profile template, LLR-RMP.1.1; `reach` is the number of distinct nodes downstream of `<node>` (LLR-RMM.2.2), 0 when not computed) |
| gap overflow | `structure: gaps shown <X> of <Y> (<Z> lowest-ranked not shown)` (only when G > 20, so X = 20; its prefix is `structure: `, never `structure gap:`, so `grep -c '^structure gap:'` counts rows) |
| skipped-rows line | `structure: skipped <N> canon rows (<kind>=<n>, …); unknown status=<u>; reach not computed=<r>` — each part printed only when its count > 0 (the `skipped` part when N > 0), parts joined by `; ` after `structure: `, the line omitted when all are 0; counts only, never a value; `<N>` counts the builder's problems by kind, unsafe-id rows included |
| note | `structure note: <text>`, in this order: one `unparsed row <id>` per reported row (id cut to 120), one line for the unlinked LLRs (first 5 ids then `and <K> more`), the ignored descriptor keys (a configured `us_canon` / `at_table` has no note: the sources line shows it, LED .59); at most 10 note lines, and when more exist the first 10 in that order print followed by `structure: notes shown 10 of <Y> (<Z> not shown)` with `<Z>` the number dropped. Snapshot canon: 7 + 1 = 8 of 10 |
| refusal | `structure: refused (<base name>): <cause> - descriptor skipped` — `<cause>` is the fixed text of K1–K17 with K5 rendered `exceeds the <N> byte limit` (`<N>` = `MAX_MAP_BYTES` for a descriptor), K16 `source.<key> is not text` and K17 `unsafe path in <field> (<reason>)` naming the field, never a value |
| descriptor overflow | `structure: refused: more descriptors than the limit (8)` |
| canon problem | `structure: unavailable (canon: <cause K1–K7>)` (K5 rendered `exceeds the <N> byte limit` with `<N>` = `LIMIT_ROLES_YML_BYTES`) |

- **Reading notes (UX; documented, not guaranteed):** the width is not guaranteed — a gap row starts with about 60 fixed characters and reaches about 210, so the first 40 characters carry severity, kind and node; gap rows are for reading, not parsing (a title may contain ` · `); the worst case is about 298 lines (8 blocks × 37 lines: label, summary, sources, gap total, 20 gaps, gap overflow, skipped-rows line, 10 notes, notes overflow — plus the header and the descriptor overflow), each line at most 1,000 characters.

- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_audit.py::test_line_formats` — against `format_structure` with a synthetic multi-severity, multi-reach map (this is the only evidence for the HIGH, LOW and reach-above-0 renderings of the 7 kinds the canon cannot source; stated, not hidden) — and `::test_format_structure_cuts_inside` (`format_structure` called DIRECTLY with a 1 MiB id, a 1 MiB label and a 1 MiB sources value: every returned line is at most 1,000 characters and each value ends `…` at 120, so the cut lives inside the frozen function, not in the wrapper), `::test_refusal_line_hostile_name` (`refusal_line` called directly with a base name carrying U+0301 and with a 300-character base name: cut to 120, ends `…`), `::test_header_first` (the header is the first line and appears once) and `::test_snapshot_run` (a tmp repo carrying the snapshot canon: `nodes=275 (HLR=76, LLR=199) edges=196 (refines=196) cycles=0`, `gaps: 7 (HIGH=0, MED=7, LOW=0)`, 2 qualified sentences); the live-repo run records its figures in the packet and asserts invariants only.
- **Numeric pass threshold:** a configured `us_canon: docs/us.md` prints `docs/us.md` and no absolute path (a marker string in the repository path never appears); `us_canon: ~/x` prints a K17 refusal and no home path; the snapshot run prints exactly the figures above; 21 gaps → 20 + overflow; 11 notes → 10 + overflow; a 121-character id prints 120 characters in total, the last being `…` (LED .44); an empty canon prints `nodes=0 edges=0 cycles=0` and `gaps: 0 (HIGH=0, MED=0, LOW=0)`.
- **Negative control:** M-RMU-3 (no gap cap) → the 21-gap arm RED; M-RMU-5 (skip the 120-character cut) → AT-129 RED; M-RMU-7 (drop the skipped-rows line) → AT-124 RED; M-RMU-11 (move the cut from `format_structure` into `structure_lines`) → `test_format_structure_cuts_inside` RED; M-RMU-13 (`refusal_line` skips the cut) → `test_refusal_line_hostile_name` RED; M-RMU-14 (drop the informational header) → `test_header_first` and AT-120 RED. **Boundary catalog:** ☑ 0, 20, 21 gaps ☑ 10 / 11 notes ☑ 120 / 121 characters.

### LLR-RMU.1.3 — Escaping and the exit code
- **Traceability:** HLR-RMU.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.7, LED-2026-10-25-relmap-r1-batch.12, LED-2026-10-25-relmap-r1-batch.17, LED-2026-10-25-relmap-r1-batch.29, LED-2026-10-25-relmap-r1-batch.74
- **Statement:** Every line returned by the hook shall reach stdout only through the audit's escaper, so no control, bidi, combining or variation-selector character from the canon or a descriptor reaches the terminal raw, and no printed line other than the release verdict starts with `verdict: `; and no structural gap or refusal shall change the exit code, which stays the release verdict's. Ids with an unprintable character are excluded upstream (`unsafe id`, LLR-RMM.1.2) and counted; the escaper's own surface is the printable-but-spoofing set — combining marks, variation selectors — in ids, and any control or separator character inside a statement or title, a descriptor base name or a configured path.
- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_audit.py::test_escaped_and_no_forged_verdict` (one arm per surface: id with U+0301, id with U+FE0F, statement with ESC and U+202E, descriptor base name with U+0301, and a descriptor ignored key named `"\u2028verdict: ready"`; plus a Layer A arm that runs `run_cli` in-process with a hook returning `format_structure` over a synthetic map whose gap title carries U+2028 and `verdict: ready`), `::test_exit_code_unchanged` (an exit-0 fixture ± a gap ± a refused descriptor).
- **Numeric pass threshold:** 0 raw `\x1b`/U+202E/U+2028/U+0301/U+FE0F in stdout; exactly one line starts with `verdict: `; exit codes equal (0 in all three). U+2028 cannot reach a title through the canon (`parse_canon` splits lines at it), so it is carried by the descriptor ignored key (the printed item is the KEY NAME) and by the Layer A arm.
- **Negative control:** M-RMU-1 (print raw) → each arm RED on its own. **Boundary catalog:** ☑ the five surfaces above.

### LLR-RMU.1.4 — Determinism and one derivation
- **Traceability:** HLR-RMU.1
- **Ledger:** LED-2026-10-25-relmap-r1-batch.13, LED-2026-10-25-relmap-r1-batch.19, LED-2026-10-25-relmap-r1-batch.30, LED-2026-10-25-relmap-r1-batch.33
- **Statement:** The stdout of `mapper --audit` shall be byte-identical across runs and across `PYTHONHASHSEED` values: kinds and edge types in profile order, descriptors in code-point order of their base names (one labelled block each), notes and unlinked ids in canon order, ties in detection order (= node input order), a cycle's first member the first in node input order, and no output derived from set or dict-hash order; and `structure_lines` shall derive the canon map once per call.
- **Validation:** `test`
- **Executed verification:** `tests/test_relmap_audit.py::test_byte_stable` (the same fixture run in subprocesses under `PYTHONHASHSEED=0` and `PYTHONHASHSEED=2`, bytes compared; the two seeds are PRE-PICKED because a recorded probe (`evidence/p2-closure-probe-2026-10-25.txt`) shows the 17-name set iterating `LLR` before `HLR` under seed 0 and `HLR` before `LLR` under seed 2, the only relative order visible in the output; the Inc-5 packet re-proves them by running M-RMU-6 for real and recording that the two stdout byte strings differ) and `tests/test_relmap_audit.py::test_canon_derived_once` (moved here from the descriptor tests: it runs through `structure_lines`; LED .33).
- **Numeric pass threshold:** 2 runs → identical bytes; 3 descriptors → 3 labelled blocks in name order and 1 `parse_canon` call.
- **Negative control:** M-RMU-6 (build the kind, edge-type and gap-kind lists of the output by iterating a `set` of the 17 profile names) → the byte-stability arm RED (only the relative order of `HLR` and `LLR` shows in the output; the two seeds are chosen by probe so that order differs between them, not left to chance). **Boundary catalog:** ☑ two pre-picked seeds ☑ three descriptors.

### Information Flow Contract (IFC) — C-54

**Part A — flows:**

```
FLOW: rm-descriptor
  SOURCE : <repo>/*.relmap.yml (operator-supplied bytes; zero or more files)
  NODES  :
    - fn    : mapper.relmap.descriptor.read_repo_text
      owner : LLR-RML.1.5
      in    : path of a matching root entry
      out   : text, or RepoReadError(K1–K7)
    - fn    : mapper.relmap.descriptor.load_descriptor
      owner : LLR-RML.1.1
      in    : text
      out   : Descriptor value, or DescriptorError(K1–K10) naming cause + base name
    - fn    : mapper.yamlscan.prescan
      owner : LLR-RML.1.4
      in    : descriptor text
      out   : nothing, or YamlLimitError(kind, detail)
    - fn    : mapper.relmap.descriptor (schema + path confinement)
      owner : LLR-RML.1.2
      in    : parsed mapping
      out   : accepted Descriptor or refusal (table)
  SINK   : the adapter (accepted) / a `structure: refused` line (refused)
```

```
FLOW: rm-canon-to-graph
  SOURCE : <repo>/REQUIREMENTS.md
  NODES  :
    - fn    : mapper.relmap.descriptor.read_repo_text
      owner : LLR-RML.1.5
      in    : canon path
      out   : text, or RepoReadError(K1–K7)
    - fn    : mapper.reqharness.derive.parse_canon
      owner : LLR-RMA.1.1
      in    : canon text
      out   : (CanonObject tuple, reported rows)
    - fn    : mapper.relmap.adapter.derive_reqharness_map
      owner : LLR-RMA.1.2
      in    : CanonObject tuple, Descriptor
      out   : node specs, `refines` edge specs by rule D-1, notes (reported rows, unlinked LLRs)
    - fn    : mapper.relmap.model.build_map
      owner : LLR-RMM.1.2
      in    : node specs, edge specs, Profile, sourced kinds
      out   : RelMap (up/down/reach/cycles) + Problems; or RelMapLimitError (LLR-RMM.1.3)
  SINK   : RelMap value in memory
```

```
FLOW: rm-graph-to-audit
  SOURCE : RelMap + derivation notes
  NODES  :
    - fn    : mapper.relmap.gaps.detect_gaps / rank_gaps
      owner : LLR-RMG.1.1
      in    : RelMap
      out   : ranked Gap list
    - fn    : mapper.relmap.audit.structure_lines (thin wrapper over format_structure)
      owner : LLR-RMU.1.2
      in    : RelMap, Gap list, notes, refusals
      out   : list of text lines, values cut to 120 characters
    - fn    : mapper.reqharness.audit.run_cli (extra_lines hook + escaper)
      owner : LLR-RMU.1.3
      in    : lines
      out   : escaped lines on stdout; unchanged exit code
  SINK   : stdout of `mapper --audit <repo>`
```

**Part B — boundary decomposition:** not owed. The question — does the system's boundary have components a consumer can address independently? — is **no** for R1: the shipped boundary is one CLI emitting one report. R2's in-process consumers of the `mapper.relmap` API are declared when R2 opens (they are consumers of a Python API, not addressable components of this boundary).

---

## 5. Validation strategy

### 5.1 Methods
**Layer A — white-box (TC):** `tests/test_relmap_{profile,isolation,model,gaps,descriptor,adapter,audit}.py` and `tests/test_yamlscan.py`, each with the C-40 RED counterfactual in its increment packet (move-aside for each new source file; one named mutation per new assertion). Oracles ported from QuickMap are re-derived over the reqharness profile.
**Layer B — black-box (AT):** AT-117…AT-122 and AT-124…AT-129 (`AT-123` is retired: it drove `MapStore.load`, a library API, and is now the Layer A pin TC-RM-01) — every one through `mapper --audit` as a subprocess over tmp fixture repos built with the git-repo-plus-registry helpers of `tests/test_reqharness_release.py` (`_seed`, `_git_repo`, `_write_canon`, `_audit_cli`; reused by IMPORT in `tests/_relmap_fixtures.py`, never copied — LED .35). Layer B evidence first exists at Inc-5 (the hook lands there); Inc-3 and Inc-4 carry in-process Layer A stand-ins with the same figures. Method: `acceptance`. Each AT drives a NON-default value (C-10) and asserts its exit-0 precondition where the exit code is part of the claim. **Layer A on the in-process surface, named as such:** TC-RM-01 (cyclic tree map still refused), TC-RM-02 (raising callable) and TC-RM-03 (the `--baseline` refusal path prints no structure line and never calls the hook).

### 5.2 Batch acceptance criteria
- Every LLR has ≥ 1 TC passing; every HLR with a shipped surface has ≥ 1 AT with boundary + negative evidence; HLR-RMM.2, HLR-RMM.3, HLR-RMP.2 and 7 of 8 catalogue kinds are Layer A only, declared (OQ-R1-2); the HIGH/LOW/reach renderings of the 7 unsourceable kinds have formatter evidence only (`format_structure`, LLR-RMU.1.2).
- Absolute counts are asserted only against the snapshot canon; the live canon gets invariants (R4). The real Python 3.10 run is `not-run` (no interpreter, no CI) and goes to Phase 4 as an operator-run check.
- The tree kind is untouched: `tests/test_ingestion_limits.py` and the tree suites pass unchanged; no file under `mapper/` other than `store.py`, `reqharness/audit.py`, `app.py` and the new files changes.
- Targeted runs only, `env -u NO_COLOR -u TERM`, `mapper.__file__` probed inside the worktree (premise 12); the orchestrator schedules the one full run.
- `tests/test_no_operator_paths.py` green before every commit.

### 5.3 Acceptance tests (Layer B bodies)

> Common frame: a tmp git repo with a verifiable registry chain (helpers above), `REQUIREMENTS.md` set per row, run as `mapper --audit <repo>` in a subprocess with the R26 timeout; "snapshot" = `tests/fixtures/relmap/REQUIREMENTS.snapshot.md` written as the repo's canon. "Block" = the lines this batch adds after the `verdict:` line. Every row names a negative control (mutant) that turns it RED.

| AT | Given | When | Then (observable) | How observed | Negative control |
|---|---|---|---|---|---|
| AT-117 (RMP.1, RMM.1, RMA.1) | the snapshot canon, no descriptor | audit | the summary line is exactly `structure: profile=reqharness nodes=275 (HLR=76, LLR=199) edges=196 (refines=196) cycles=0`; a second fixture of 3 HLR + 2 LLR (non-default) prints `nodes=5 (HLR=3, LLR=2)` and no US/AT/TC term | stdout line equality | M-RMA-1 (199 edges), M-RMA-6 (274 nodes) |
| AT-118 (RMG.1) | a canon with an active HLR with no LLR, an active HLR with one LLR, a retired (`withdrawn`) HLR with none, an active HLR whose only LLR is `withdrawn` | audit | exactly one gap line, `MED · HLR WITHOUT LLR` on the first HLR; none for the other three | stdout | M-RMG-1, M-RMG-6 |
| AT-119 (RMA.1) | the snapshot canon | audit | exactly 8 note lines: 7 `structure note: unparsed row <id>` (`LLR-HYG.1.1`, `LLR-CAN.1.1`, `LLR-CAN.1.2`, `HLR-RH.6`, `LLR-RH.6.1`, `LLR-RH.7.3`, `LLR-Q3.1.2`, in canon order) and one listing `LLR-REPAIR.1, LLR-REPAIR.2, LLR-RH.6.2`; no overflow line; `edges=196` (no edge invented for them) | stdout notes + summary | M-RMA-1, M-RMA-3 |
| AT-120 (RMU.1) | a fixture whose `--audit` exits 0 (asserted first, with ≥ 1 active HLR lacking an LLR) | audit with and without a refused descriptor | exit code 0 in both; every line up to and including `verdict:` equals the golden captured on the base commit; the block follows and its first line is `structure: informational - does not change the verdict or the exit code` | return code + stdout prefix | M-RMU-8 (exit 1 when a structural gap exists), M-RMU-14 (no header) |
| AT-121 (RML.1) | one descriptor per cause K1, K2, K5–K17 (K1 as a symlink or, on Windows, a directory junction (`mklink /J`), K2 as a directory; `blocked` only if none can be created; K5 at cap+1; cap−1 as a loading control; K9 at total collection depth 65, depth 64 loading (the top-level mapping counts as depth 1)); K3 and K4 cannot be produced for a descriptor that was just listed and are Layer A (`test_read_repo_text_*`) | audit | `structure: refused (<base name>): <that cause's text> - descriptor skipped` for each (K5 `exceeds the <MAX_MAP_BYTES> byte limit`, K16 `source.<key> is not text`, K17 `unsafe path in <field> (<reason>)`); no path, anchor name or YAML snippet in stdout; audit continues, exit code unchanged | stdout | M-RML-1, M-RML-7, M-RML-10, M-RML-11 |
| AT-122 (RMU.1) | five hostile fixtures: an id with U+0301, an id with U+FE0F, a statement with ESC and U+202E on an active HLR with no LLR (so it reaches the gap sentence), a descriptor base name with U+0301, and a descriptor whose top-level ignored key is named by the YAML double-quoted string `"\u2028verdict: ready"` (the forge scenario; the printed item is the key name) (ids with U+202E, ESC or U+200B are excluded upstream as `unsafe id` and counted: AT-124; U+2028 in a canon row splits the line in `parse_canon` and makes a reported row, so only the descriptor key can carry it to the terminal) | audit | stdout has no raw ESC, U+202E, U+2028, U+0301, U+FE0F; exactly one line starts with `verdict: ` | stdout scan, per arm | M-RMU-1 (each arm RED alone) |
| AT-124 (RMM.1, RMA.1) | a canon with one duplicate id, one id with U+202E, one id with U+200B (both match `\S+`), one row whose id contains NBSP (skipped by the canon reader), one with `Done` status | audit | `structure: skipped 3 canon rows (duplicate id=1, unsafe id=2); unknown status=1`; `nodes + skipped = parsed rows`, where parsed rows are the objects `parse_canon` returned (the NBSP row is not among them); no excluded value printed | stdout line equality | M-RMM-1, M-RMU-7 |
| AT-125 (RMG.1) | a canon with `HLR-X.1` (no LLR) plus pipe-bearing `LLR-X.1.1` (unparsed) | audit | the gap sentence ends `(canon rows near this id could not be parsed or linked: 1)`; the snapshot run shows the qualifier on `HLR-CAN.1` and `HLR-REPAIR.1` only | stdout | M-RMG-4, M-RMA-5 |
| AT-126 (RMU.1) | (a) a directory that is not a git repo, (b) a git repo with no registry, (c) a repo whose `REQUIREMENTS.md` is a symlink / over the cap / binary, with a path-like marker string in the repo path | audit each | (a) one line `structure: unavailable (no repository)`; (b) `structure: unavailable (no registry)`; (c) `structure: unavailable (canon: <K>)`; the marker never appears in stdout; exit codes equal the no-hook runs | stdout + return code | M-RMU-4, M-RML-7 |
| AT-127 (RML.1) | 9 root descriptors named `a…i.relmap.yml` (valid), plus a directory `x.relmap.yml` in a second fixture | audit | 8 labelled blocks in name order, then `structure: refused: more descriptors than the limit (8)`; the directory is `structure: refused (x.relmap.yml): is not a regular file - descriptor skipped` | stdout | M-RML-13, M-RML-9 |
| AT-128 (RMU.1) | the snapshot canon plus 3 descriptors | audit under `PYTHONHASHSEED=0` and `PYTHONHASHSEED=2` (two pre-picked seeds, LED .30) | the two stdout byte strings are equal | bytes equality | M-RMU-6 |
| AT-129 (RMU.1) | (a) a descriptor with a 1 MiB unknown top-level key (printed as an ignored-key note), (b) a `us_canon` of 255 characters (the longest `confine_reason` accepts; probed 2026-10-25: 255 ok, 300 `unreadable`), (c) a canon statement of 5,000 characters on a gap HLR, (d) an unlinked LLR id of 200 characters | audit | each of those four printed values is ≤ 120 characters before escaping and ends `…`; no line exceeds 1,000 characters | max line length + suffix | M-RMU-5 |

Layer A pins named here, not ATs: **TC-RM-01** (a tree map with a cycle is still refused by `MapStore.load`; negative control M-RMP-4; it gates nothing new) **TC-RM-02** (`run_cli` with a raising callable prints one `structure: unavailable (internal error: <type>)` line, same exit code, no traceback; negative control M-RMU-2) and **TC-RM-03** (`run_cli` on the `--baseline` refusal path prints the refusal on stderr, no structure line, and never calls the hook; negative control M-RMU-10).

### 5.4 Traceability matrix (two-way)

| US | HLR | LLR | AT (Layer B) | TC (Layer A) |
|---|---|---|---|---|
| US-RM-001 | RMP.1 | RMP.1.1, RMP.1.2 | AT-117 | test_relmap_profile, test_relmap_isolation |
| US-RM-001 | RMP.2 | RMP.2.1 | — (Layer-A-only, declared) | TC-RM-01, test_relmap_isolation |
| US-RM-001 | RMM.1 | RMM.1.1, .1.2, .1.3 | AT-117, AT-124 | test_relmap_model |
| US-RM-001 | RMM.2 | RMM.2.1, .2.2 | — (Layer-A-only, declared; first end-to-end observation is R2) | test_relmap_model |
| US-RM-002 | RMM.3 | RMM.3.1 | — (Layer-A-only, declared: premise 5) | test_relmap_model |
| US-RM-002 | RMG.1 | RMG.1.1, .1.2, .1.3 | AT-118, AT-125 | test_relmap_gaps |
| US-RM-004 | RML.1 | RML.1.1–.1.6 | AT-121, AT-127 | test_relmap_descriptor, test_yamlscan, test_prescan_refusal_goldens |
| US-RM-001 | RMA.1 | RMA.1.1–.1.4 | AT-117, AT-119, AT-124 | test_relmap_adapter |
| US-RM-003 | RMU.1 | RMU.1.1–.1.4 | AT-120, AT-122, AT-126, AT-128, AT-129 | TC-RM-02, TC-RM-03, test_relmap_audit |

Reverse: AT-117 ← RMP.1/RMM.1/RMA.1 · AT-118 ← RMG.1 · AT-119 ← RMA.1 · AT-120 ← RMU.1 · AT-121 ← RML.1 · AT-122 ← RMU.1 · AT-124 ← RMM.1/RMA.1 · AT-125 ← RMG.1 · AT-126 ← RMU.1 · AT-127 ← RML.1 · AT-128 ← RMU.1 · AT-129 ← RMU.1. Accepted evidence gap, per story: US-RM-001's "queryable" outcome (RMM.2) and US-RM-002's cycle clause (RMM.3) reach no shipped surface in R1.

---

## 6. Appendices

### 6.1 Extended glossary
- **Honest partial map:** unsourced kinds produce neither nodes nor gaps. **Rule D-1:** HLR→LLR by id structure — a convention, not canon content, so it lives in the adapter and announces its unlinked remainder.

### 6.2 Relevant design decisions
- Separate kind, own package (R-016); shared prescan leaf (R-017); hook injected so `reqharness` stays upstream; lines appended after the verdict so no existing line moves.
- `status` first word decides eligibility; `deferred` HLRs are not reported (deferred means not yet built).
- Gap `reach` is `down`-reach (QuickMap's definition). On the HLR/LLR skeleton every reported node is a sink, so ties are the rule and the order inside a severity is canon order; richer ranking appears when TC/AT arrive (open risk below).

### 6.3 Open risks
- **Security pattern scan (family C — C6 fired):** `devflow-scan-spec.py` run 2026-10-25 over §§1–4 (52,458 bytes; all 4 controls ok): `security_required: true`, flags `hash`, `form`, `expose` — all vocabulary collisions, answered here per the scanner's instruction: `hash` names the test's before/after tree digest (LLR-RMA.1.4) and no credential or password hashing exists; `form` names the shape of an id or a line ("both import forms", "line formats"), not a web form; `expose` names the module-map column "what it EXPOSES" (a public API), not a network endpoint — no auth (C1), secrets (C2) or network (C7) surface is touched. C6 questions answered: (a) new code handles operator-supplied descriptor bytes and the canon — every file the package reads goes through `lstat` (links, reparse points and non-regular files refused) and `osopen.read_capped` (LLR-RML.1.5), bounded by the byte cap, the NUL/UTF-8 checks and the iterative prescan; at most 8 descriptors are read and the canon is derived once; (b) no new boundary crossing: repository file reads only, no network, no subprocess, no OS handler; (c) refusal and `unavailable` text is drawn from the closed set K1–K17 of fixed strings — never `str(exc)`, a directory path, an anchor name or a YAML snippet — and everything repository-derived is cut to 120 characters, then escaped at the print boundary.
- **Rule D-1 is a convention.** 3 of 199 LLRs do not resolve (two have no HLR of that stem; one lost its parent to a pipe-bearing row). Fixing the canon rows (escape the pipes; rename the two REPAIR ids or add `HLR-REPAIR`) is a canon-hygiene follow-up, not R1's (BACKLOG).
- **TRACEABILITY CYCLE cannot fire from the canon** (premise 5); it protects future profiles and hand-written relation files.
- **Reach is flat on the skeleton:** all 7 live gaps tie at reach 0; ranking earns its keep when TC/AT/US join (OQ-R1-8).
- **No real 3.10 run is possible on this machine and there is no CI:** the real run is `not-run`; the AST floor guard plus the banned-stdlib-name census is the proxy, and an operator-run 3.10 check is a Phase 4 item.
- **Two copies of one prescan rule remain:** `reqharness/config.py` keeps its own (it echoes the YAML error text and may import only `osopen`); folding it into the leaf is BACKLOG B-144, not this batch.
- **Reach is bounded, not free:** ranking visits at most 2,000,000 nodes (LLR-RMG.1.3); a hub-shaped graph near the caps ranks the uncomputed gaps with reach 0 and says so on the count line.
- **Extracting the prescan touches `store.py`** (the highest-census file of the hygiene batch): mitigated by byte-identity as the requirement and `tests/test_ingestion_limits.py` as the unchanged oracle.
