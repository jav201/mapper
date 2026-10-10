# Increment 003 — LLR-CSV.1.1 / LLR-CSV.1.2 / LLR-CSV.2.2 / LLR-CSV.2.3 · `Close the code-review nits with tests and mutation evidence`

> **Artifact language:** English.
> **Owed in.** `core` ✓ · `full` ✓
> **Where this lives:** the repo, `.dev-flow/2026-10-10-csv-safety-batch/03-increments/increment-003.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-10-csv-safety-batch` |
| Increment | `003` (CSVI3) |
| Lane (if the batch forked) | n/a — one lane · closes the nits of increments 1 (`model` + `store`) and 2 (`import_csv` + `screens/import_preview.py`) |
| Requirement(s) | `LLR-CSV.1.1` · `LLR-CSV.1.2` · `LLR-CSV.2.2` · `LLR-CSV.2.3` (the nits' trace anchors; no new behavior) |
| Acceptance | the two code reviews' APPROVE-WITH-NITS findings closed: one new test node (LOW-2), one docstring contract (LOW-1), one behavior-neutral comment (LOW-4), one packet relabel (LOW-5), and recorded mutation evidence (LOW-3, MED-1 a–d, LOW-1) |
| Agent | Kimi (`kimi-code/kimi-for-coding`) via the kimi CLI — worker unit CSVI3 |
| Date | `2026-10-10` |

---

## 1 · What changed

- **LOW-2 (review of increment 1): a test now proves "dump once, and the text written is the text checked".** `test_save_writes_the_bytes_dump_returned_and_dumps_once` monkeypatches `mapper.mermaid.dump` with a counting wrapper — the patch target is the module attribute, because `MapStore.save` binds `dump` with a function-body import (`from .mermaid import CYCLE_ARROW, dump`, `mapper/store.py:861`) — and asserts the wrapper ran exactly once for one `save` and that the text read back from the written `.mmd` equals the text `dump` returned (universal-newline read: `write_text` translates `"\n"` to os.linesep on write, so byte-equality holds modulo that platform translation).
- **LOW-1 (review of increment 2): the docstring of `test_markup_in_id_is_painted_verbatim` now states exactly what it guards.** It cannot fail merely by removing `darkside.plain` (`Text.assemble` never parses markup); it bites on a switch of the rendering path to a markup-aware one — `Text.from_markup` / `Static(markup=True)`. That mutation is executed in §4 and goes RED.
- **LOW-4: one-line comment at `splitlines()` in `mapper/import_csv.py`** — the only product change this increment is allowed: `line_num` also counts `\x0b \x0c \x1c-\x1e \x85` U+2028 U+2029 as line breaks (ruling R16). Behavior-neutral.
- **LOW-5: the increment-002 packet's "M2 flavor 2" is relabelled the empty-CSV control** (the mutation that paints a generic refusal on an empty CSV); the increment-001/002 `Independent review` cells now name the reviewer and verdict.
- **No product behavior changed.** Every other nit closes with tests or recorded mutation evidence against the committed increment-1/2 code.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/import_csv.py` | source | LLR-CSV.2.1 (ruling R16 caveat) | one-line comment at the `splitlines()` call — the increment's ONLY product change (LOW-4) |
| `tests/test_csv_safety_store.py` | test | LLR-CSV.1.1, LLR-CSV.1.2 | new node `test_save_writes_the_bytes_dump_returned_and_dumps_once` (LOW-2) |
| `tests/test_csv_safety_preview.py` | test | LLR-CSV.2.2 | docstring of `test_markup_in_id_is_painted_verbatim` now names its guard — a switch to `Text.from_markup` / `Static(markup=True)` (LOW-1) |
| `.dev-flow/2026-10-10-csv-safety-batch/evidence/inc3-red.transcript` | generated | LLR-CSV.1.1/1.2/2.2/2.3 | RED-proof transcript (§4) |
| `.dev-flow/2026-10-10-csv-safety-batch/03-increments/increment-001.md` | doc | review closure | `Independent review` cell filled; gate checklist items 6/15 resolved |
| `.dev-flow/2026-10-10-csv-safety-batch/03-increments/increment-002.md` | doc | review closure | same review-cell fill; "M2 flavor 2" relabelled the empty-CSV control (LOW-5) |

| Count | Value |
|---|---|
| **SOURCE files** | **1 / 4** (`mapper/import_csv.py`, comment-only) |
| Test files | 2 (`tests/test_csv_safety_store.py`, `tests/test_csv_safety_preview.py`) |
| Doc files | 3 (this packet + the two prior packets' review cells; outside the source count) |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_csv_safety_store.py tests/test_csv_safety_preview.py tests/test_import_csv.py tests/test_repair_store_boundary.py
ruff check mapper/import_csv.py tests/test_csv_safety_store.py tests/test_csv_safety_preview.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `tests/test_csv_safety_store.py` + `tests/test_csv_safety_preview.py` re-run with `tests/test_import_csv.py` + `tests/test_repair_store_boundary.py` pins | **129 passed in 8.99s** (§3 command, this worktree) |

New node ids:

- `tests/test_csv_safety_store.py::test_save_writes_the_bytes_dump_returned_and_dumps_once` — LLR-CSV.1.1/1.2 (LOW-2): with `mapper.mermaid.dump` wrapped by a counting monkeypatch, one `save` calls `dump` exactly once and the `.mmd` text read back equals the text the wrapper saw `dump` return — the bytes written ARE the bytes checked, one dump per save

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | (LOW-3) edges compared as a SET in `MapStore._check_round_trip`; (MED-1a) precedence swapped, cycle before collision; (MED-1b) one word of the neutral cycle sentence changed; (MED-1c) Oxford comma in the three-way list; (MED-1d) toast severity `error` → `warning`; (LOW-1) refusal panel rendered with `Text.from_markup` |
| Instrument | hand edit of the product file, applied and reverted by explicit copy (`cp <backup> <product>`); every restore checked by sha256 |
| Where it ran | this worktree |
| Transcript | `.dev-flow/2026-10-10-csv-safety-batch/evidence/inc3-red.transcript` (relative paths only) |
| Restore proven by | sha256 of `mapper/store.py` returned to `293c521e12874a61901cd0f54de7f0ea3a4febd2f51a20177f22769e94ad7773` and of `mapper/screens/import_preview.py` to `2e40feb83ee27deb04cae2127cbf6efb8cdaef7552095a4cb0b6485fcdf2955e` after every mutation; `mapper/import_csv.py` to `68a98bc87c2c5110f52a8e6dcc706dade6c0e139b290faefd093a9d6df5ad4a1` after the comment revert |
| Bytecode cache | run with `python -B` |
| Arms resolved at baseline | 6 mutations × their named nodes (below); MED-1e (drop one edge in a copy of the flow) skipped — not a product mutation: the record is keyed on rows, not edges, and a mutated input copy exercises nothing the shipped code does; the working path is pinned by AT-074's save-and-reopen oracle |
| Verdict granularity | per node id |

RED outputs (verbatim tails from the transcript):

- LOW-3 + `-k "reparse_structure_mismatch"` → `1 failed, 8 deselected` — `test_save_refuses_reparse_structure_mismatch` `FAILED` (the duplicate-edge case no longer refuses: a set comparison accepts the reparse that silently drops the duplicate row).
- MED-1a + `-k "colliding_cyclic"` → `1 failed, 11 deselected` — `test_colliding_cyclic_csv_paints_the_collision_sentence` `FAILED` (the cycle sentence wins, violating collision > cycle).
- MED-1b + `-k "neutral_cycle_sentence"` → `1 failed, 11 deselected` — `test_cycle_csv_paints_the_neutral_cycle_sentence` `FAILED` (the pinned sentence is no longer painted verbatim).
- MED-1c + `-k "three_way_collision"` → `1 failed, 11 deselected` — `test_three_way_collision_uses_list_grammar` `FAILED` (Oxford comma painted).
- MED-1d + `-k "at_072_refused"` → `1 failed, 1 passed, 10 deselected` — `test_at_072_refused_save_toasts_and_writes_nothing` `FAILED` on the severity assertion the node already carried (`kw.get("severity") == "error"` — no new assertion was needed).
- LOW-1 + `-k "markup_in_id"` → `1 failed, 11 deselected` — `test_markup_in_id_is_painted_verbatim` `FAILED`: the markup-aware switch raises `rich.errors.MarkupError` on the verbatim-shaped id (`closing tag '[/BOLD]' doesn't match any open tag`) — the test bites on the rendering-path switch its docstring now names.
- LOW-4 revert protocol: reverting the one-line comment is behavior-neutral by construction — the new node stays GREEN (`1 passed, 8 deselected`), the restore is byte-identical (sha256 above); the behavioral RED evidence for this increment's tests is the six mutations.

| Field | Value |
|---|---|
| **RED counterfactual** | 6 mutants, all KILLED per node id; MED-1e declared not-a-product-mutation with reason; LOW-4 revert recorded honestly as behavior-neutral. Transcript at `evidence/inc3-red.transcript`; restore digests returned after every mutation |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_csv_safety_store.py` / `tests/test_csv_safety_preview.py` (the named nodes) | the six product mutations (above) | `FAILED` — refusal lost / precedence flipped / sentence reworded / Oxford comma / severity weakened / markup interpreted — verbatim tails in the transcript |
| `ruff check mapper/import_csv.py tests/test_csv_safety_store.py tests/test_csv_safety_preview.py` | the authored files | `All checks passed!` (green at baseline) |

| Field | Value |
|---|---|
| **Instrument RED-proof** | the pytest nodes shown RED under every mutation before the PASS was believed; ruff green at baseline |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the written `.mmd` | the file text read back from the workspace equals the text the counting `dump` wrapper returned (emitted bytes, modulo platform newline translation) | equal (assertion passed) |
| the `#import-preview-canvas` Static's rendered text | the sentence-family nodes assert against `Static.render().plain` | the exact pinned sentences found (assertions passed) |
| the toast | `app.notify` captured via `_capture_notices`, asserted as `(message, severity=error, markup=False)` | the pinned text fired exactly once (assertion passed) |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 3 artifacts, each asserted against its emitted form |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| inc3-red.transcript | .dev-flow/2026-10-10-csv-safety-batch/evidence/inc3-red.transcript | `408847ffe02de9f9264199df3bf117c4ebb196b9d26cc5542fc184bd253a33bb` |

| Field | Value |
|---|---|
| **Evidence files** | `evidence/inc3-red.transcript` — baseline hashes, six RED runs + the LOW-4 revert protocol, restores and sha256 checks, final 129-passed GREEN |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | no — every mutation is applied to and restored from the committed product code; the "no product behavior changed" claim is the sha256-equality record |
| If the result is an ABSENCE, what made the search wide enough | n/a |
| Guard labelled as protecting a CONCLUSION, not a behaviour | the LOW-1 docstring now names the conclusion it protects (a rendering-path switch to a markup-aware Text) |
| Conjunctive criteria: one mutation per conjunct | per-conjunct: edge multiset (LOW-3) · precedence (MED-1a) · cycle wording (MED-1b) · list grammar (MED-1c) · toast severity (MED-1d) · markup-safe rendering (LOW-1) |
| Synthetic instance of the absent case | each mutation IS the synthetic instance of its regression |
| **Positive control for every probe that returned an ABSENCE** | AT-074 remains the positive control for the no-write oracle's complement; the GREEN re-run after every restore is the positive control for the instruments |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | the mutations touch only `store._check_round_trip` and `screens/import_preview.py` internals — both files' public surfaces (`MapStore.save`, `_ImportPreviewScreen`) are pinned by the §3 re-run pins | 129 passed |
| B2 file moved on disk | n/a — no file moved | not fired |
| B3 byte-identical golden captures this source | n/a — no golden reads the touched code | not fired |
| B4 artifact produced here is consumed elsewhere | the transcript is consumed by the increment packet and batch close only | n/a |

| A3 | interface consumed by another module changed | no — the only product change is a comment; `preview_csv`, `MapStore.save` and `_ImportPreviewScreen` keep their signatures |

| Field | Value |
|---|---|
| **Reverse census** | 4 probes considered (B1 fired via the §3 pins, re-validated green; B2, B3, B4 did not fire; A3 unchanged) |

### Correction population — enumerated BEFORE the first site was edited

| Field | Value |
|---|---|
| **Correction population** | none — one behavior-neutral comment added; no pre-existing defect corrected |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|---|---|---|---|
| n/a — no marker superseded | n/a | n/a | n/a |

### Signed-balance test ledger

`post = base − deleted + added` → `129 = 128 + 1 − 0` ✓ reconciles (128 pre-existing nodes across the four §3 files, 1 added in `tests/test_csv_safety_store.py`, 0 deleted).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | **PENDING** — this increment closes increments 1/2's reviews; the re-review of those closures is dispatched by the orchestrator |

---

## 5 · Risks

- The LOW-2 byte-equality is asserted on the universal-newline read because `write_text` translates newlines on Windows; a future switch to byte-mode writes would make the raw-bytes form stricter — the test comment records this.
- MED-1e (drop-one-edge) was reviewed and deliberately not executed as a mutation; if a later review wants the flow-level experiment anyway, it belongs in a test-side fixture, not as a product mutation.

## 6 · Pending items / spec deviations

- The P4 numeric perf measurement (ruling R12) — evidence only, owed at validation.
- `ARCHITECTURE.md` §4 `Graph` row amendment (ruling R10 / architect B3) — owed at batch close.
- Re-review of this increment's nit closures — dispatched by the orchestrator (§4b).

## 7 · Suggested next task

Validation/close: the P3 full-suite gate, the P4 perf evidence, `04-validation.md` + `05-close.md`, and the orchestrator's re-review of the closed nits.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 1 / 4 (§2, comment-only) |
| 2 | Tests written in this same increment | all | ✓ | 1 new node in `tests/test_csv_safety_store.py` |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | 1 node, 129 passed (§3) |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | 6 mutations + LOW-4 revert protocol, transcript + restore digests (§4) |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 4 probes (§4) |
| 6 | `code-reviewer` passed | `core` · `full` | ⚠ | re-review of the nit closures PENDING (§4b) |
| 7 | No file from another lane touched | all | ✓ | one lane; files = §2 |
| 8 | Frozen interfaces untouched | all | ✓ | `preview_csv` / `MapStore.save` / `_ImportPreviewScreen` signatures unchanged — the only product delta is a comment |
| 9 | Coverage claims verified **on disk** | all | ✓ | 129 passed here (§3 command) |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 |
| 11 | **Mutation verdicts** declared | all | ✓ | §4 — 6 mutants KILLED per node id; MED-1e declared not-a-product-mutation |
| 12 | **Instrument RED-proof** declared | all | ✓ | §4 — pytest nodes (+ ruff green at baseline) |
| 13 | **Correction population** declared | all | ✓ | §4 (none) |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4 (written `.mmd` text + rendered Static text + captured toast) |
| 15 | **Independent review** names somebody | all | ⚠ | re-review PENDING (§4b) — dispatched by the orchestrator |
| 16 | **Evidence files** declared | all | ✓ | §4 — `evidence/inc3-red.transcript` with sha256 |
