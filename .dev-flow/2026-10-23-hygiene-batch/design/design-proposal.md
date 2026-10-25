# Design proposal — mapper — Batch 2026-10-23-hygiene-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language
> The normative rules below are language-independent. **Where that language is declared:**
> `state.json`'s `language` key in `core` and `full`.

> **Reserved field names.** The **field names and block keywords below are language-independent** — the
> validator parses them literally and they are never translated:
> `Design proposal` · `7 · Forward-applicability table` · `⏸ DEFER`
> Everything else on this page — headings, guidance, the prose in every cell — is translated with the batch.
> **One strategy, not two:** the flow ships no alias table, so a translated label is read as an ABSENT one and the rule keyed on it reports a true-sounding silence.
> **Why a HEADING is reserved here and a FIELD NAME everywhere else:** `C-49`'s artifact is the §7 TABLE, and a rule that read a summary bullet instead of the rows would be reading a claim about the table rather than the table. `V52` therefore keys on this document's own H1 and on the §7 heading, which is why both are on the machine plane. **And one FLOW-WIDE reserved token, read out of this artifact by `V42` no matter which template minted it:** `⏸ DEFER`.

> **Owed in.** `core` by trigger · `full` ✓
> **Source:** `/dev-flow-init` step 4's seed-by-level table, which is this fact's one home. A level marked `—` **does not owe this artifact, and its absence is not an omission**; `by trigger` means the station exists only when the `triggers` block fired, and `stations_active` in `state.json` is the authority for *this* batch. Where a SECTION or a gate row is owed more narrowly than the artifact, it says so on the row.

> **Where this lives: the VAULT + Drive**, not the repo — it is deliberation, and its traceability to
> code is weak. It is **cited by id** from the repo (`PDR-<batch_id>#D<n>`), never copied.
> What binds code — a frozen interface, a design characteristic — also lands in the **repo**, in the
> requirement or in `docs/ARCHITECTURE.md`. *The vault keeps the deliberation; the repo keeps the commitment.*

> **The forward-applicability rule (ISO/IEC/IEEE 15288).** Everything below must be NAMED as the input
> of a later activity. **If a section of this proposal is nobody's input, delete it — it does not belong
> in the PDR.** That rule is what allows this document to cost half the batch without being waste.

| Field | Value |
|---|---|
| Id | `PDR-2026-10-23-hygiene-batch` |
| Requirements covered | `US-Q1-001 / US-Q2-001 / US-Q3-001 · HLR-Q1.1, Q2.1-Q2.3, Q3.1-Q3.2 · LLR-Q1.1.1, Q2.1.1-2.1.3, Q2.2.1, Q2.3.1, Q3.1.1-3.1.2, Q3.2.1-3.2.3` |
| Modules touched (from `docs/ARCHITECTURE.md`) | `app · store · diff · import_csv · osopen · screens/home · canvas` (per docs/ARCHITECTURE.md) |
| Triggers that fired | `A2 · A3 · A4 · B1 · B3 · C6 · D1 · E1` |
| Author / reviewers | `architect` · `qa-reviewer` (drafted by the dev-flow worker author pass 2026-10-23) |

---

## 1 · Objective and scope

**Q1 (US-Q1-001, HLR-Q1.1, LLR-Q1.1.1, AT-108, mutant M-Q1-1).** Colour is always on: the
`NO_COLOR` environment variable is neutralised in `MapperApp.__init__` before the Textual base
constructor runs, so no Monochrome filter can be installed by the environment. Mechanism is
decided by ruling R3 — this design implements it, it does not re-litigate it.

**Q2 (US-Q2-001, HLR-Q2.1-Q2.3, LLR-Q2.1.1-2.1.3 / Q2.2.1 / Q2.3.1, AT-109…AT-114, mutants
M-Q2-1…M-Q2-4).** Ingestion is capped and refuses loudly: maps ≤ 8 MiB / depth 64 / 100,000 nodes
and 100,000 edges (ruling R1, re-derived 8.3× over the largest committed map of 12,000 nodes /
11,999 edges — ledger .5); CSV attachments ≤ 4 MiB with an 8 KiB binary probe; every refusal is a
typed `MapStoreError` that names the limit and the map id, never a path (C6); anchor/alias and
depth violations are caught by a prescan before the recursive build (M-Q2-1).

**Q3 (US-Q3-001, HLR-Q3.1-Q3.2, LLR-Q3.1.1-3.1.2 / Q3.2.1-3.2.3, AT-115 / AT-116, mutants
M-Q3-1…M-Q3-3).** A render sweep proves the six renderers stay inside their viewport at five
terminal sizes across the four recorded states (6 × 5 × 4 = 120 assertions, state matrix in
`design/state-matrix.md`), and a canvas audit records every clip and overprint so AT-116 can prove
byte-identity of the rendered output with and without the sink (LLR-Q3.2.2) — no golden
re-baselining anywhere.

**This design will NOT:** add a `--no-color` opt-out (ruled out by R3 + the Q5 operator ruling);
cap OS-handed attachments (ruling R2); emit dim-text audit events in v1 (BACKLOG B-136, ruling R4);
re-baseline any golden (byte-identity is the oracle, LLR-Q3.2.2); change what any renderer paints
(the audit observes; it does not steer).

## 2 · Modules and boundaries

| Module | What it owns here | What it exposes | What it must NOT reach into |
|---|---|---|---|
| `app` (L1) | `NO_COLOR` neutralisation in `MapperApp.__init__` before the Textual base constructor. | Same public surface as today. | Must not touch renderer internals or the colour pipeline beyond the env neutralisation. |
| `store` (L2) | Byte cap (`MAX_MAP_BYTES`, stat + re-check on the read bytes), count caps (`MAX_NODES`/`MAX_EDGES`), depth/anchor/alias prescan, typed path-free refusals. | `MapStore.load` signature unchanged; refusals raised as `MapStoreError` naming limit + map id. | Reads file content **only** through the osopen bounded reader (D2); no direct `open()`. |
| `diff` (L2) | Applies the same caps to diff-side map loads; `None`-on-error contract survives. | Same signature; `None` still means "could not load". | No import of `osopen` — capped reads reach `diff` only through `store`'s `_prescan_sidecar` over the existing `diff → store` edge (`mapper/diff.py:11` already imports `MapStore`); the `ALLOWED_OUTSIDE_APP` pin (`tests/test_arch_osopen_callers.py`) forbids a third osopen edge (PDR condition N3, discharged at the seal). |
| `import_csv` (L2) | `MAX_FILE_BYTES` cap + `BINARY_PROBE_BYTES` binary detection via the same reader. | CSV import entry points unchanged. | Reaching into `store` stays **forbidden** — which is exactly why the reader lives in `osopen` (R-015). |
| `screens/home` (L2b) | The CSV-import refusal toast: for a typed refusal (`MapStoreError` family) it interpolates the refusal's own message text (`str(e)`, path-free per C6) so the reason reaches the operator (AT-114); the generic branch keeps `type(e).__name__` for arbitrary `OSError`s. | Same screen surface as today. | Must not reach into `store`/`import_csv` internals — wording only (ruling R7, ledger .9). |
| `osopen` (L2) | The bounded content reader — NEW public name + constants frozen at PDR (**D2**); the only file-content door for `store` + `import_csv`. | The reader name, `MAX_MAP_BYTES`, `MAX_DEPTH`, `MAX_NODES`, `MAX_EDGES`, `MAX_FILE_BYTES`, `BINARY_PROBE_BYTES`. | Stays stdlib-only; no `model`/`store` imports; no other module gains an osopen edge. |
| `canvas` (L3) | Optional trailing `audit=None` sink on `Canvas.__init__`; `put` records clips and overprints per ruling R4 (ledger .8). | `Canvas(w, h, tones=(), fallback="", audit=None)` — **frozen signature D1**. | No rendering logic changes; renderers stay untouched. |

- Boundaries respected as declared in `docs/ARCHITECTURE.md`: **✓** (no boundary moves; two inbound
  edges into osopen per the ARQ commitment — `store.py` + `import_csv.py` added to the
  `ALLOWED_OUTSIDE_APP` allow-list in the same landing). `screens/home.py` carries wording only —
  it gains no osopen/store edge (it already imports `preview_csv` and `safe_local_path` read-only).

## 3 · Diagrams

Text flows mirroring the contract's IFC Part A.

**Q1 — q1-env-colour:**

```
process env (NO_COLOR=1 possible)
  → MapperApp.__init__  [L1: os.environ.pop("NO_COLOR") before super().__init__]
  → Textual App base constructor   (no Monochrome filter can be installed)
  → painted screens byte-equal with/without NO_COLOR=1   (AT-108, M-Q1-1)
```

**Q2 — q2-map-load:**

```
map id → MapStore.load
  → osopen bounded reader (D2): stat ≤ MAX_MAP_BYTES → re-check on read bytes (capped re-read)
  → prescan (L2, new): anchors/aliases refused · depth ≤ MAX_DEPTH (M-Q2-1)
  → node/edge count ≤ MAX_NODES / MAX_EDGES (M-Q2-4)
  → parse+build → Graph
refusal path: typed MapStoreError(limit + map id, no path) → screens toast (AT-109…112, M-Q2-2/-1/-4)
```

**Q2 — q2-csv-import:**

```
attachment → import_csv
  → osopen bounded reader (D2): size ≤ MAX_FILE_BYTES · binary probe ≤ BINARY_PROBE_BYTES (M-Q2-3)
  → CSV parse → rows
refusal path: typed MapStoreError(limit + map id) → screens toast (AT-113/114)
```

**Q3 — q3-render:**

```
fixture graph (state ∈ {plain, folded, empty, orphan}; state-matrix.md)
  → ViewState(w, h) with (w, h) ∈ SIZES
  → renderer from mapper.views.__all__ (roster derived, completeness guard — LLR-Q3.1.1)
  → Canvas(w, h, audit=sink)  [D1]
  → sweep: exactly/≤ h lines × ≤ w cells × 120 combos (AT-115, M-Q3-1)
  → audit: every clip/overprint explained; rows() byte-identical with/without sink (AT-116, M-Q3-2/-3)
```

## 4 · Interfaces that change — and which ones FREEZE

| Interface | Current | After | Consumers | **Frozen for the fork?** |
|---|---|---|---|---|
| `Canvas.__init__` | `Canvas(w, h, tones=(), fallback="")` | `Canvas(w, h, tones=(), fallback="", audit=None)` — `put` appends `(x,y)` under `clip` for out-of-bounds non-space writes and under `overprint` for in-bounds writes where the held cell is a different alphanumeric AND the written character is alphanumeric (ruling R4 + ledger .8) | 3 production construction sites pass nothing: `mapper/views/lane.py:199`, `mapper/views/layered.py:693`, `mapper/views/radial.py:184`; B-44 pin `tests/test_a3_census.py:658-674` (amends, same landing); `docs/ARCHITECTURE.md` canvas rows :200/:214 | **YES — D1** (`PDR-2026-10-23-hygiene-batch#D1`). Lands as trunk work first, then lanes fork. |
| osopen bounded content reader | does not exist (caps live nowhere yet) | NEW public name + constants freeze at PDR — **D2** (`PDR-2026-10-23-hygiene-batch#D2`); lives in `mapper/osopen.py`, imported by `store` + `import_csv` only (R-015) | `mapper/store.py`, `mapper/import_csv.py`; `tests/test_arch_osopen_callers.py` `ALLOWED_OUTSIDE_APP` gains `store.py` + `import_csv.py` (same landing) | **YES — D2**. Name + constants frozen at PDR; the L2 lane consumes, it does not rename. |
| `MapStore.load` internal read path | full read, no caps | no signature change; read path routed through the D2 reader; refusal surface unchanged — typed `MapStoreError`, path-free | all existing `load` callers | NO freeze needed — signature untouched. |

**Every OTHER interface is untouched in-lane.** A lane needing an interface change returns to the
trunk — that is trigger **A3**.

**A frozen interface is not touched inside a lane.** If a lane needs to change one, the work returns to
the trunk — that is trigger **A3**.

## 5 · Proposed test cases

| Id | Layer (0 unit / A white / B black / UX) | What it asserts | **The mutation that would turn it RED** |
|---|---|---|---|
| `tests/test_colour_always_on.py::test_no_color_removed_before_super` | 0 | `NO_COLOR` is gone from `os.environ` after `MapperApp` construction; no Monochrome filter active | M-Q1-1 — delete the neutralisation |
| `tests/test_colour_always_on.py` black-box arm | B (AT-108) | painted screens byte-equal with vs. without `NO_COLOR=1` in the environment | M-Q1-1 — delete the neutralisation |
| `tests/test_ingestion_limits.py::test_byte_cap_refuses_and_names_limit` | 0 (AT-109) | both the stat path and the grow-between-stat-and-read path refuse, naming the byte limit; text CSV at cap−1 loads | M-Q2-2 — remove the cap or the re-check |
| `tests/test_ingestion_limits.py::test_prescan_*` | 0 (AT-111) | depth-64 graph parses; anchor/alias graphs and depth-65 graphs refuse; a 10,000-deep graph refuses in < 5 s without RecursionError | M-Q2-1 — remove the prescan (or its depth check) |
| `tests/test_ingestion_limits.py::test_count_caps` | 0 (AT-112/AT-113) | 100,001 nodes / 100,001 edges refuse; exactly-at-cap parses | M-Q2-4 — raise or drop the count cap (asserting mutant for ledger .1/.5) |
| `tests/test_ingestion_limits.py::test_csv_*` | 0 (AT-113/AT-114) | CSV at 4 MiB ± 1 byte; NUL at byte 0 / at byte 8,191 refuses as binary | M-Q2-3 — remove the size cap or shrink the probe |
| `tests/test_ingestion_limits.py` screen arm | B (AT-109…114) | ≥ 1 arm per refusal kind driven through the running screen, asserting the toast text (review m5). Toast consumers verified by grep 2026-10-23: `mapper/screens/construct.py:57` and `mapper/screens/common.py:_save_or_toast` — `app.py` does **not** consume `MapStoreError`; this corrects the lane plan's expectation and is recorded here and in the PDR record — those are the save/create surfaces; the LOAD refusals (AT-109…112) surface through `mapper/screens/home.py:169-181` and `mapper/screens/map/screen.py:208-215`, which catch generic `Exception`, and the CSV refusal (AT-114) through `mapper/screens/home.py:524-530` (review F-UX-2) — the screen arms drive these three sites | M-Q2-1…4 per refusal kind; store-level arms remain as TCs |
| `tests/test_scalecheck.py::test_renderer_roster_derived` | 0 (AT-115) | roster from `mapper.views.__all__` == 6, with a completeness guard against an empty/changed roster | drop one renderer from the export list |
| `tests/test_scalecheck.py::test_sweep` | A (AT-115) | 6 × 5 × 4 = 120 geometry assertions over the recorded state matrix (`design/state-matrix.md`) | M-Q3-1 — break one renderer's bounds handling |
| `tests/test_scalecheck.py::test_sweep_audit_arm` | A | ≥ 1 audited canvas per render; unexplained overprints/clips fail the arm | M-Q3-2 — swallow an audit event |
| `tests/test_canvas_audit.py::test_events` | 0 (AT-116) | clip/overprint coordinates recorded; space-writes and old-alphanumeric→space record nothing — incl. the R4 second limb: the **new** character must be alphanumeric (m3) | M-Q3-4 — drop the alphanumeric gate (second-limb asserting mutant, ledger .10); M-Q3-2 — event append removed — reddens the event-set arms |
| `tests/test_canvas_audit.py::test_byte_identity` | 0 (AT-116) | `rows()` byte-identical with vs. without the audit sink | M-Q3-3 — let the sink touch the buffer |
| HLR-Q2.3 device-name pin — existing suite | A | DOS/reserved device names refused at every write door. **Verified by grep 2026-10-23 (correction to review m6):** `tests/test_store.py` contains **no** reserved-name arms (grep for `reserved`/`CON`/`NUL`/`check_map_id`/`is_reserved` returns nothing) — the pin actually lives in `tests/test_seed_safety.py` (`BAD_NAMES` incl. `CON` at :42; `test_seed_store_refuses_every_write_door` :230-249 covering save/create/create_seed/create_from_template with `NUL.txt`/`com1`/`lpt9`), the device-name family in `tests/test_inc9n.py` (`DEVICES` list :59-62; refusal-before-open arms :257-283), with `tests/test_en4.py:37` and `tests/test_seed2.py:167` as census-recorded neighbours; the osopen gate itself is `mapper/osopen.py:104-107` (`PureWindowsPath.is_reserved()` per component) | drop the reserved check in osopen — the seed-safety arms redden |
| RED counterfactual — `mapper/app.py` | 0/A | move-aside RED proof (C11 habit 1): `mapper/app.py` renamed aside → `test_colour_always_on.py` + the `test_help_scope.py` ambient pin go RED | n/a — the counterfactual IS the mutation; transcript pasted in the L1 increment packet |
| RED counterfactual — `mapper/store.py` | 0/A | moved aside → ingestion arms + the existing load suite go RED | n/a — transcript in the L2 packet |
| RED counterfactual — `mapper/diff.py` | 0/A | moved aside → diff arms go RED | n/a — transcript in the L2 packet |
| RED counterfactual — `mapper/import_csv.py` | 0/A | moved aside → CSV arms go RED | n/a — transcript in the L2 packet |
| RED counterfactual — `mapper/osopen.py` | 0/A | moved aside → reader arms + `tests/test_arch_osopen_callers.py` go RED | n/a — transcript in the L2 packet |
| RED counterfactual — `mapper/canvas.py` | 0/A | moved aside → audit arms + B-44 pin + golden digests go RED | n/a — transcript in the L3 packet |

**Declared here, at authoring time, not at execution time.** A proposed case whose reddening mutation
cannot be named is not yet a test case — it is a hope. Layer 0 applies where the unit has cyclomatic
complexity ≥3 **or** transforms data crossing a declared module boundary.

## 6 · Risks and rejected alternatives

> **Rejected alternatives are owed WHERE A REAL DECISION EXISTS**, otherwise `n/a — <the decision already made, and by what>` — an existing pattern, a frozen interface, a prior ADR. **Do not fabricate a second design to fill this section:** two invented options make an arbitrary pick look deliberated, which is worse than one honest constraint. (the same ruling as `agents/architect.md` §Evidence checklist and the PDR row — one obligation, three stations, and closing it at one of them is `C-14`.)

| Alternative considered | Why it was rejected |
|---|---|
| Reader in a NEW `mapper/ingest.py` module; or reader exported BY `store` | Rejected by **R-015** — one more boundary to guard, and exporting it from `store` breaks the `import_csv → store` import ban. See `docs/ARCHITECTURE.md` R-015. The reader lives in `osopen`, which both may already use. |
| `--no-color` opt-out / a filter-override mechanism | Rejected by ruling **R3** + the operator ruling on question Q5 (ledger .3): the requirement is "colour always on", an opt-out is a way back to the defect. |
| Dim-text audit events in v1 | Deferred to BACKLOG **B-136** (ruling R4, ledger .4). v1 records only clip/overprint coordinates; richer events are backlog, not scope. |
| Design note (review m4, **adopted**): the bounded reader reads at most cap+1 bytes — `f.read(MAX + 1)`, refuse on overflow — the oracle's capped shape at `qm:src/quickmap/model.py:498-505`. **Never** a full read before the re-check; LLR-Q2.1.1's "re-checked on the read bytes" is implemented as this capped re-read. | Adopted, not rejected — recorded so the DDR checks the reader against this shape, not against a full-read assumption. |
| **Risk:** the prescan adds one pass over the sidecar | Watch-item: load-time delta measured at the L2 gate; the prescan refuses early, so the cost lands on refusing inputs and one cheap pass on accepting ones. |
| **Risk:** `diff.py`'s None-on-error contract must survive the shared caps | AT/TC arms cover it: a capped-out diff-side load must still yield `None`, not a raise — asserted in the L2 suite. |
| **Discovered while deriving the state matrix:** dangling-edge graphs crash OutlineRenderer (`mapper/views/outline.py:214-218`, KeyError) | Out of scope for the sweep (direct-construction only — `mermaid.parse` materialises both endpoints at `mapper/mermaid.py:86-87`); backlog candidate named at the batch close. |

*(Recording the rejection is what stops the same option being re-proposed in three batches.)*

## 7 · Forward-applicability table — **the section that makes this document honest**

| Output of this PDR | Named consumer downstream | Where the consumer will read it |
|---|---|---|
| design characteristics (frozen signatures D1/D2, the capped-read shape of §6 note 4) | Phase-3 increments L1/L2/L3, read at each increment gate | increment packets + this proposal §4 |
| enablers (state matrix `design/state-matrix.md`, perf-fixture corpus) | Phase 3 L3 + validation (AT-115) | `design/state-matrix.md` + `tests/perf_goldens_capture.py` builders |
| proposed test cases | layers 0/A/B and the DDR | §B checklist 4-5 of the DDR + the lane test ledgers |
| design → requirement traceability | the traceability matrix and the DDR | the batch traceability matrix + `PDR-2026-10-23-hygiene-batch.md` §A row 4 |
| crossed reverse census (§8 below) | PDR record §B + DDR re-check | `PDR-2026-10-23-hygiene-batch.md` §B + DDR checklist row 3 |

- ⚠ Any row whose consumer column is empty: **remove the output, or explain why it is being produced.** (None empty.)

## 8 · Parallelisation plan *(only if the batch forks)*

| Lane | Modules / layer | Files it owns | Agent |
|---|---|---|---|
| **L1 = Q1** | `app` / B | `mapper/app.py` (+ new `tests/test_colour_always_on.py`) | dev-flow worker lane L1 |
| **L2a = Q2-core** | `store · diff · osopen` / 0+A (3 SOURCE files) | `mapper/store.py`, `mapper/diff.py`, `mapper/osopen.py` (+ new `tests/test_ingestion_limits.py`; amends `tests/test_arch_osopen_callers.py` allow-list in the same landing) | dev-flow worker lane L2a |
| **L2b = Q2-csv** | `import_csv · screens/home` / B (2 SOURCE files) | `mapper/import_csv.py`, `mapper/screens/home.py` (the CSV refusal toast wording per ruling R7 — no new tests of its own beyond the shared `tests/test_ingestion_limits.py` screen arm) | dev-flow worker lane L2b |
| **L3 = Q3** | `canvas` / A | `mapper/canvas.py` (+ new `tests/test_scalecheck.py`, `tests/test_canvas_audit.py`; amends B-44 pin in `tests/test_a3_census.py:658-674` in the same landing) | dev-flow worker lane L3 |

- `modules(lane_i) ∩ modules(lane_j) = { }` — or same domain / different layers with the interface frozen: **✓** (three module families, zero overlap; the two cross-lane interfaces D1/D2 freeze before the fork)
- **File sets are disjoint** (not just modules — two lanes may not edit the same file, not even different regions): **✓** (L1: 1 source; L2a: 3 source; L2b: 2 source; L3: 1 source; amendments ride in the owning lane's landing only)
- Family-B reverse census run **per lane and shared** before forking: **✓** — see the crossed census block below
- Trunk-only artifacts (requirements · traceability · backlog · SPEC) are written **only** by the trunk: **✓** (this proposal, the PDR record and the state matrix are trunk artifacts; lanes land code + tests only)

**Crossed reverse census (C-52 condition 3, ruling R5) — executed 2026-10-23.** Per lane, the
touched symbols' reverse-grep over `mapper/` + `tests/` found every asserting file classified as
lane-owned new test, same-landing amendment, or byte-pinned must-stay-green:

- **Lane-owned new tests:** L1 `tests/test_colour_always_on.py`; L2 `tests/test_ingestion_limits.py`; L3 `tests/test_scalecheck.py`, `tests/test_canvas_audit.py`.
- **Same-landing amendments:** `tests/test_a3_census.py` B-44 :658-674 (L3); `tests/test_arch_osopen_callers.py` `ALLOWED_OUTSIDE_APP` (L2).
- **Byte-pinned must-stay-green:** `tests/test_repair_depth.py` MASTER_LEGACY_DIGESTS :109 + fingerprint :252-254; `tests/test_perf_paint_clip.py:172` 16 render goldens; `tests/test_help_scope.py` NO_COLOR fixture :78-94 + legend pin :247-274.
- **Crossed matrix ∅ for write hazards.** The only cross-lane presences are read-only:
  - L2a's `MapStoreError` is consumed by `mapper/screens/construct.py:57` and `mapper/screens/common.py:_save_or_toast` — **not** `app.py`; the LOAD refusals (AT-109…112) surface through `mapper/screens/home.py:169-181` and `mapper/screens/map/screen.py:208-215` (generic-`Exception` catches, invisible to a `MapStoreError` grep — review F-UX-2), and the CSV refusal (AT-114) through `mapper/screens/home.py:524-530`, which L2b edits (wording only; no new module edges — home.py already imports `preview_csv`, `safe_local_path`, `TEMPLATES` read-only).
  - L3-adjacent `mapper/views/outline.py:311` `no_color=True` is a deliberate Rich Console pin inside a renderer, explicitly out of L1's edit set — flipping it would redden the Outline byte-identity digests.
  - L2 path-privacy + typed-refusal pins at `tests/test_repair_store_boundary.py:884` and :401-431 are named as L2 constraints.
  - **No unexpected hits.**

L2b's `screens/home.py` edit touches one toast string; every behavioural pin that drives the home
screen (`tests/test_inc9*.py`, `tests/test_app.py`, `tests/test_keymap.py` and the other home-screen
suites listed by `grep -rl "HomeScreen" tests/`) stays green and is re-run at the L2b gate.

**Census verdict:** census complete, lanes may fork after the seal.
