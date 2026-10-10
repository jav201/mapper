# Increment 004 — LLR-CSV.1.1 / LLR-CSV.3.1 · `Discharge the DDR review conditions`

> **Artifact language:** English.
> **Owed in.** `core` ✓ · `full` ✓
> **Where this lives:** the repo, `.dev-flow/2026-10-10-csv-safety-batch/03-increments/increment-004.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-10-csv-safety-batch` |
| Increment | `004` (CSVI4) |
| Lane (if the batch forked) | n/a — one lane · discharges the architect/qa conditions raised at the DDR review |
| Requirement(s) | `LLR-CSV.1.1` (dump-once oracle) · `LLR-CSV.3.1` (effective M3, round-trip titles) · the DDR review conditions (architect MED-1 / LOW-3 / LOW-4, qa MED-1 / MED-2 / LOW-3/4) |
| Acceptance | the modular move oracle's "changed" freeze retired with a loss-arm negative control; the boundary-guard comment corrected; the dump-once node shown RED under two `store.save` mutations; mutation M3 retargeted to an effective, executed mutation (ledger `LED-2026-10-10-csv-safety-batch.11`); the inc1 transcript completed (baseline GREEN re-run + M4 with its own immediate restore); DDR §E rows and this packet written |
| Agent | Kimi (`kimi-code/kimi-for-coding`) via the kimi CLI — worker unit CSVI4 |
| Date | `2026-10-10` |

---

## 1 · What changed

- **architect MED-1: the modular move oracle's "changed" check is retired as a gate.** `tests/test_mod_bodies.py` no longer carries `DECLARED_CHANGES`; `test_llr_mod_4_3_bodies_match_baseline` asserts only `missing == []` and `duplicated == []`. The move's purpose — no body edited by the move — was proven and sealed when `2026-10-09-modular-batch` closed; a permanent "changed" freeze would tax every later batch, and per-batch declarations would become permanent exemptions. The ruling and its date are recorded in the test's docstring. `baseline_diff` still computes `changed`, and the existing one-token RED arm still proves the oracle sees a one-token drift. The modular batch's baseline file was NOT edited.
- **architect MED-1, loss arm: a new executed negative control.** `test_llr_mod_4_3_red_a_deleted_moved_method_reddens_missing` deletes one moved `MapScreen` method from a tmp copy of the package and asserts the diff comes back `missing` non-empty — the RED proof that retiring the "changed" freeze did not take loss detection down with it (no prior arm covered deletion → `missing`).
- **architect LOW-3: the totality-guard comment no longer overclaims.** `tests/test_repair_store_boundary.py:699-703` now states that ONLY `line_no` (`CsvRow`) and `rows` (`CsvCollision`) are declared non-text, that `raw_id`/`slug` are `str` and classify as text, and that none of the four fields is written to the sidecar.
- **qa MED-1: the dump-once node is shown RED-able, twice.** Two mutations of `MapStore.save` each redden `test_save_writes_the_bytes_dump_returned_and_dumps_once`: (M-dump2) a second bare `dump(graph)` call; (M-dumpwrite) the write persists a second `dump(graph)` instead of the checked `mmd_text`. Both restored byte-identically (sha256) and re-run GREEN.
- **qa MED-2: mutation M3 is retargeted to an effective mutation and executed.** Titles persist in the `_nodos.yml` sidecar (`_build_sidecar` in `mapper/store.py`), not the `.mmd` label — the original M3 wording ("make `mermaid.dump` omit node titles") was vacuous (`dump` never wrote titles) and never executed. M3 now reads "drop the title from `_build_sidecar`" in HLR-CSV.3 / LLR-CSV.3.1 / §6.1 (`01-requirements.md`), with ledger entry `LED-2026-10-10-csv-safety-batch.11` and the back-pointer on both requirements' `Ledger:` lines; the mutation is executed RED against the round-trip nodes and AT-074.
- **qa LOW-3/4: the inc1 transcript is completed.** inc1's baseline GREEN command is re-run (`tests/test_csv_safety_store.py` → `9 passed`; inc1 recorded `8 passed` before increment 3's dumps-once node existed), and M4 is re-run with its OWN immediate restore sha256 (inc1's transcript had M4 share its restore with M-cyc).
- **architect LOW-4 and LOW-2 are recorded in the DDR, not "fixed".** Forests keep their root drift on reload (B-117) and `test_save_accepts_legacy_forest_after_edit` accepts it by design (node set / edge set / titles asserted after reload, never the root). LOW-2 (the refusal's substring coupling to the parse message, `mapper/store.py:832`) is recorded in DDR B1 as accepted/optional, not fixed.
- **No product behavior changed.** Every product mutation in §4 was applied to and restored from `mapper/store.py` by explicit copy, with sha256 equality recorded after every restore.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `tests/test_mod_bodies.py` | test | LLR-CSV.2.2, LLR-CSV.2.3 (DDR architect MED-1) | `DECLARED_CHANGES` removed; `test_llr_mod_4_3_bodies_match_baseline` gates `missing`/`duplicated` only (ruling + date in its docstring); new node `test_llr_mod_4_3_red_a_deleted_moved_method_reddens_missing`; module docstring RED-controls paragraph updated |
| `tests/test_repair_store_boundary.py` | test | LLR-CSV.1.1 (DDR architect LOW-3) | comment at the `_EXPECTED_NON_TEXT` csv-safety entries: only `line_no`/`rows` declared non-text; `raw_id`/`slug` classify as text; none written to the sidecar |
| `.dev-flow/2026-10-10-csv-safety-batch/01-requirements.md` | doc | LLR-CSV.3.1 (qa MED-2) | M3 retargeted in HLR-CSV.3 / LLR-CSV.3.1 negative controls and the §6.1 glossary; `LED-…-batch.11` back-pointer on both `Ledger:` lines |
| `.dev-flow/2026-10-10-csv-safety-batch/01-requirements-ledger.md` | doc | LLR-CSV.3.1 (qa MED-2) | new entry `LED-2026-10-10-csv-safety-batch.11` |
| `.dev-flow/2026-10-10-csv-safety-batch/design/DDR-2026-10-10-csv-safety-batch.md` | doc | all six conditions | B1 records the oracle retirement (superseding the `DECLARED_CHANGES` row) and LOW-2 as accepted/optional; new §E with the six review-condition rows; Verdict stays `PENDING-REVIEW` |
| `.dev-flow/2026-10-10-csv-safety-batch/evidence/inc4-red.transcript` | generated | LLR-CSV.1.1 / 3.1, DDR conditions | RED-proof transcript (§4) |
| `.dev-flow/2026-10-10-csv-safety-batch/03-increments/increment-004.md` | doc | this packet | — |

| Count | Value |
|---|---|
| **SOURCE files** | **0 / 4** — tests and docs only; no product file changed |
| Test files | 2 (`tests/test_mod_bodies.py`, `tests/test_repair_store_boundary.py`) |
| Doc files | 5 (requirements, ledger, DDR, transcript, this packet) |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_mod_bodies.py tests/test_csv_safety_store.py tests/test_csv_safety_preview.py tests/test_repair_store_boundary.py
ruff check tests/test_mod_bodies.py tests/test_csv_safety_store.py tests/test_repair_store_boundary.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | the four §3 files | **128 passed in 10.95s** (§3 command, this worktree) |

New node ids:

- `tests/test_mod_bodies.py::test_llr_mod_4_3_red_a_deleted_moved_method_reddens_missing` — DDR architect MED-1: on a tmp copy of the package, deleting one moved `MapScreen` method makes the baseline diff come back `missing` non-empty — the executed RED proof for the oracle's loss arm after the "changed" freeze retires.

Modified nodes (behavior-neutral):

- `tests/test_mod_bodies.py::test_llr_mod_4_3_bodies_match_baseline` — now gates `missing`/`duplicated` only; docstring carries the architect DDR MED-1 ruling (2026-10-10).

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | (qa MED-1, M-dump2) `MapStore.save` calls `mermaid.dump` a second time; (qa MED-1, M-dumpwrite) `MapStore.save` writes a second `dump(graph)` instead of the checked `mmd_text`; (qa MED-2, M3-effective) the `title` key dropped from `_build_sidecar`; (qa LOW-3/4) M4 re-run — root comparison re-added to `_check_round_trip` |
| Instrument | hand edit of `mapper/store.py`, applied and reverted by explicit copy (`cp /tmp/store_inc4_backup.py mapper/store.py`); every restore checked by sha256 |
| Where it ran | this worktree |
| Transcript | `.dev-flow/2026-10-10-csv-safety-batch/evidence/inc4-red.transcript` (relative paths only) |
| Restore proven by | sha256 of `mapper/store.py` returned to `293c521e12874a61901cd0f54de7f0ea3a4febd2f51a20177f22769e94ad7773` after EVERY mutation (three restores) |
| Bytecode cache | run with `python -B` |
| Arms resolved at baseline | M-dump2 + `-k dumps_once` → `1 failed, 8 deselected`; M-dumpwrite + `-k dumps_once` → `1 failed, 8 deselected`; M3-effective + `-k roundtrip` → `1 failed, 1 passed, 7 deselected` and `test_at_074_valid_csv_saves_and_reopens_identical` → `1 failed`; M4 + `-k legacy_forest` → `1 failed, 8 deselected` |
| Verdict granularity | per node id |

RED outputs (verbatim tails from the transcript):

- M-dump2 + `-k dumps_once` → `FAILED tests/test_csv_safety_store.py::test_save_writes_the_bytes_dump_returned_and_dumps_once` — `1 failed, 8 deselected` (the counting wrapper saw two dumps for one save).
- M-dumpwrite + `-k dumps_once` → same node `FAILED` — `1 failed, 8 deselected` (the persisted text no longer IS the checked text; two dumps per save).
- M3-effective + `-k roundtrip` → `FAILED tests/test_csv_safety_store.py::test_save_load_roundtrip_valid_trees` — `1 failed, 1 passed, 7 deselected`; `test_at_074_valid_csv_saves_and_reopens_identical` → `FAILED` — `1 failed in 1.65s` (titles lost on reload: they live in the sidecar, not the `.mmd` label).
- M4 + `-k legacy_forest` → `FAILED tests/test_csv_safety_store.py::test_save_accepts_legacy_forest_after_edit` — `1 failed, 8 deselected` (the root comparison refuses a forest that opens today; inc1's transcript had this arm share its restore with M-cyc — this re-run carries its own immediate restore sha256).
- The oracle-retirement arms (architect MED-1) are self-proving: both negative controls run a mutant on a tmp copy INSIDE the node (one-token rename → `changed` non-empty; method deletion → `missing` non-empty), so each arm IS its own executed RED proof: `tests/test_mod_bodies.py` → `5 passed`.
- Transcript completeness (qa LOW-3/4): inc1's baseline GREEN command re-run — `python -B -m pytest -q -p no:cacheprovider tests/test_csv_safety_store.py` → `9 passed in 0.26s` (inc1 recorded `8 passed` before increment 3's dumps-once node; the re-run is recorded honestly at today's count).

| Field | Value |
|---|---|
| **RED counterfactual** | 4 product mutations, all KILLED per node id (2× dump-once, effective M3, M4 re-run) + 2 self-proving oracle negative controls; every restore byte-identical (sha256). Transcript at `evidence/inc4-red.transcript` |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_csv_safety_store.py::test_save_writes_the_bytes_dump_returned_and_dumps_once` | the two dump-once mutations | `FAILED` — two dumps per save / written text ≠ checked text |
| `tests/test_csv_safety_store.py` round-trip nodes + `tests/test_csv_safety_preview.py::test_at_074…` | the effective-M3 mutation | `FAILED` — reloaded titles lost |
| `tests/test_csv_safety_store.py::test_save_accepts_legacy_forest_after_edit` | the M4 mutation | `FAILED` — a forest that opens today is refused |
| `ruff check tests/test_mod_bodies.py tests/test_csv_safety_store.py tests/test_repair_store_boundary.py` | the authored files | `All checks passed!` (green at baseline) |

| Field | Value |
|---|---|
| **Instrument RED-proof** | every named pytest node shown RED under its mutation before the PASS was believed; ruff green at baseline |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the written `.mmd` | the file text read back equals the text the counting `dump` wrapper returned (one dump per save) | equal (assertion passed at baseline) |
| the reloaded graph's titles | the round-trip nodes and AT-074 assert the titles that come back from `MapStore.load` | identical (assertions passed at baseline) |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts, each asserted against its emitted form |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| inc4-red.transcript | .dev-flow/2026-10-10-csv-safety-batch/evidence/inc4-red.transcript | `399f99f00fa08eeafb31112dbc4a60148d3fd0d38cfb24dae0c1a38b8ebdc94e` |

| Field | Value |
|---|---|
| **Evidence files** | `evidence/inc4-red.transcript` — baseline hashes, four RED runs with per-mutation restores and sha256 checks, inc1 baseline GREEN re-run, final 128-passed GREEN |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | no — every product mutation is applied to and restored from the committed product code; the "no product behavior changed" claim is the sha256-equality record (`293c521e…7773` after every restore) |
| If the result is an ABSENCE, what made the search wide enough | n/a |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_llr_mod_4_3_bodies_match_baseline`'s docstring now names the conclusion (the move's no-edit purpose, sealed at `2026-10-09-modular-batch` close) and why the freeze retired |
| Conjunctive criteria: one mutation per conjunct | per-conjunct: dump count (M-dump2) · written = checked text (M-dumpwrite) · sidecar title persistence (M3-effective) · root exclusion (M4) · loss detection (method-deletion arm) |
| Synthetic instance of the absent case | each mutation IS the synthetic instance of its regression |
| **Positive control for every probe that returned an ABSENCE** | the GREEN re-run after every restore is the positive control for the instruments |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | the mutations touch only `MapStore.save` / `_build_sidecar` internals — the store's public surface is pinned by the §3 re-run (128 passed, incl. `tests/test_store.py`'s own consumers of `save`/`load` in the wider suite, not re-run here per unit scope) | 128 passed |
| B2 file moved on disk | n/a — no file moved | not fired |
| B3 byte-identical golden captures this source | n/a — no golden reads the touched code (the modular batch's baseline JSON was NOT edited) | not fired |
| B4 artifact produced here is consumed elsewhere | the transcript is consumed by this packet, DDR §E and batch close only | n/a |

| A3 | interface consumed by another module changed | no — `MapStore.save`/`load` signatures unchanged; the only test-surface changes are the retired freeze, the corrected comment, and one new node in another batch's guard file (cross-batch guard, the DDR's own subject) |

| Field | Value |
|---|---|
| **Reverse census** | 4 probes considered (B1 fired via the §3 pins; B2–B4 did not fire; A3 unchanged) |

### Correction population — enumerated BEFORE the first site was edited

| Field | Value |
|---|---|
| **Correction population** | none — no pre-existing product defect corrected; the increment retires a guard mechanism and corrects one comment |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|---|---|---|---|
| `DECLARED_CHANGES` (tests/test_mod_bodies.py) | `grep -rn DECLARED_CHANGES --include="*.py"` → no hit outside the historical transcripts/DDR narrative | yes — the gate no longer references it; the DDR B1 row records the retirement and supersedes the row | `tests/test_mod_bodies.py` (definition removed); DDR B1 amendment; `evidence/inc4-red.transcript` |

### Signed-balance test ledger

`post = base − deleted + added` → `128 = 127 + 1 − 0` ✓ reconciles (127 pre-existing nodes across the four §3 files, 1 added in `tests/test_mod_bodies.py`, 0 deleted — one node modified behavior-neutrally).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `qa-reviewer` (Claude Sonnet) + architect (Claude Opus), read-only, re-review at the DDR seal: both **APPROVED** — qa re-read `evidence/inc4-red.transcript` (M-dump2, M-dumpwrite, M3-effective, M4 with restores) and LED .11; architect re-read `tests/test_mod_bodies.py:244-262` and the new missing-arm, the boundary comment, and the DDR forest-root rows; two wording LOWs applied at the seal |

---

## 5 · Risks

- The retired "changed" freeze means a future batch that MOVES a body without editing it is still caught (`missing`/`duplicated`), but an intentionally edited moved body no longer trips this oracle — drift evidence remains available via `baseline_diff`'s `changed` arm on demand, and the one-token arm keeps that arm honest.
- M4's re-run records `9 passed` for inc1's baseline GREEN command where inc1 recorded `8 passed` — the difference is increment 3's dumps-once node, and the transcript says so; no claim relies on the counts matching.

## 6 · Pending items / spec deviations

- The P4 numeric perf measurement (ruling R12) — evidence only, owed at validation.
- `ARCHITECTURE.md` §4 `Graph` row amendment (ruling R10 / architect B3) — owed at batch close.
- DDR Verdict `PENDING-REVIEW` — the orchestrator seals after re-review (§4b).

## 7 · Suggested next task

Validation/close: the P3 full-suite gate, the P4 perf evidence, `04-validation.md` + `05-close.md`, and the orchestrator's DDR seal after re-reviewing §E.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 0 / 4 (§2 — tests and docs only) |
| 2 | Tests written in this same increment | all | ✓ | 1 new node in `tests/test_mod_bodies.py` |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | 1 node, 128 passed (§3) |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | 4 mutations + 2 self-proving arms, transcript + restore digests (§4) |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 4 probes (§4) |
| 6 | `code-reviewer` passed | `core` · `full` | ⚠ | re-review at DDR seal PENDING (§4b) |
| 7 | No file from another lane touched | all | ✓ | one lane; files = §2 |
| 8 | Frozen interfaces untouched | all | ✓ | `MapStore.save`/`load` signatures unchanged — zero product delta |
| 9 | Coverage claims verified **on disk** | all | ✓ | 128 passed here (§3 command) |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 |
| 11 | **Mutation verdicts** declared | all | ✓ | §4 — 4 mutants KILLED per node id + 2 self-proving oracle arms |
| 12 | **Instrument RED-proof** declared | all | ✓ | §4 — pytest nodes (+ ruff green at baseline) |
| 13 | **Correction population** declared | all | ✓ | §4 (none) |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4 (written `.mmd` text; reloaded titles) |
| 15 | **Independent review** names somebody | all | ⚠ | re-review PENDING (§4b) — dispatched by the orchestrator at the DDR seal |
| 16 | **Evidence files** declared | all | ✓ | §4 — `evidence/inc4-red.transcript` with sha256 |
