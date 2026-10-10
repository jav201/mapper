# Increment 001 — PERFG0 · `behaviour goldens captured on base 5cde04e`

> **Artifact language**
> This template is the canonical **English scaffold**. Generate the artifact in the batch's development
> language — the **prose**, and never a label. **Where that language is declared:**
> `state.json`'s `language` key in `core` and `full`. The normative RULES below are
> language-independent.

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/guides/increment-template.md` explains each field and the rules that read it. It ships with the flow and is not copied into this batch.

> **Reserved field names.** The **field names and block keywords below are language-independent** — the
> validator parses them literally and they are never translated:
> `SOURCE files` · `Instrument RED-proof` · `Correction population` · `Mutation verdicts` · `Emitted-form assertion` · `Reverse census` · `RED counterfactual` · `Independent review` · `Evidence files` · `Traces to` · `File` · `Kind` · `source` · `test` · `doc` · `config` · `generated` · `fixture` · `⏸ DEFER`

| Field | Value |
|---|---|
| Batch | `2026-10-10-perf-batch` |
| Increment | `001` |
| Lane (if the batch forked) | `trunk` · `none — pre-fork capture step (PDR condition C10)` |
| Requirement(s) | `HLR-PERF.1 · HLR-PERF.2 · LLR-PERF.1.3 · LLR-PERF.2.2` (golden provenance protocol, PDR §7) |
| Acceptance | `AT-075 · AT-075b · AT-076` (goldens their lane tests compare against) · `tests/test_perf_goldens_manifest.py` (this step's own assertion) |
| Agent | `Kimi (kimi-code/kimi-for-coding) via the kimi CLI` |
| Date | `2026-10-10` |

---

## 1 · What changed

The batch's behaviour goldens are captured and pinned on the BASE product before the
lanes fork. `tests/perf_goldens_capture.py` regenerates all 26 goldens deterministically
from the current product into `tests/goldens/perf/` and rewrites `MANIFEST.json` (per
golden: case id, base SHA `5cde04e`, sha256). Pinned: the Lane R render grid
(LLR-PERF.1.3 — layered renderer painted plain text over empty / single / deep-5000 /
wide-2000 / wide-6000 / forest / fold / panned ViewState at 118×34 and 87×34); the
AT-075/075b keypress session (wide-2000 through `MapperApp` + `run_test(size=(118,34))`,
real keys, `#map-canvas` region strips per step: open, `l,j,j,j,j`, archive `x`/`y`, `l`);
the Lane M dump grid (LLR-PERF.2.2 — `dump(parse(fixture))` for legacy/anidado/truncado,
plus wide-6000, forest, empty, single, dangling-edge); and the AT-076 golden (saved
`.mmd` bytes after an `a` add_child on a saved wide-6000 map, real keys). No file under
`mapper/` was touched (`git diff --stat 5cde04e HEAD -- mapper` is empty; verified again
at capture time).

---

## 2 · Files modified

**The budget counts SOURCE files only. Tests are not capped. Product docs and `.dev-flow/**` are outside the count.**

| File | Kind | Traces to | Change |
|---|---|---|---|
| `tests/perf_goldens_capture.py` | test | `LLR-PERF.1.3 · LLR-PERF.2.2 · AT-075 · AT-075b · AT-076` | new capture script (builders + regeneration of every golden + MANIFEST) |
| `tests/test_perf_goldens_manifest.py` | test | `HLR-PERF.1 · HLR-PERF.2` (golden provenance) | new manifest assertion: base SHA + per-golden existence/sha256 |
| `tests/goldens/perf/**` (26 files + MANIFEST.json) | fixture | `LLR-PERF.1.3 · LLR-PERF.2.2 · AT-075 · AT-075b · AT-076` | the pinned behaviour goldens (test-owned, per backlog B-108) |

| Count | Value |
|---|---|
| **SOURCE files** | **0** / 4 |
| Test files | 2 (uncapped) |
| Doc files | 0 (outside the count) |

- Goldens live under `tests/goldens/perf/`, not `.dev-flow/` (backlog B-108 is the lesson).

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_perf_goldens_manifest.py
ruff check tests/perf_goldens_capture.py tests/test_perf_goldens_manifest.py
python -B tests/perf_goldens_capture.py   # regeneration; run twice, sha256 must not change
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | — | none (no product code in this step) |
| **A · white-box** | `core` · `full` | `tests/test_perf_goldens_manifest.py::test_manifest_names_base_sha_5cde04e` | 1 passed |
| **B · black-box** | `core` · `full` | `tests/test_perf_goldens_manifest.py::test_every_golden_exists_and_matches_its_sha256` | 1 passed |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | flipped one byte (first byte, `b[0] ^= 1`) of the golden `tests/goldens/perf/dump/empty.mmd` on disk, copy kept at `/tmp/g0-empty.mmd.bak` |
| Instrument | project code: own hand via a python one-liner; restore checked by hash against `MANIFEST.json` |
| Where it ran | **my own tree / worktree** |
| Transcript | `.dev-flow/2026-10-10-perf-batch/evidence/g0-capture.transcript` §6: `FAILED tests/test_perf_goldens_manifest.py::test_every_golden_exists_and_matches_its_sha256 — golden drifted: dump/empty.mmd: f3b67fe0… != 228e1f41…`, `1 failed, 1 passed`, exit 1 |
| Restore proven by | **file hash returned to its pre-mutation value**: `228e1f41f3c2674cf342c6df608dd87f63c034682c6575017585c9eec08ceb37` == manifest sha256 (`BYTE-IDENTICAL RESTORE: True`, transcript §7) |
| Bytecode cache | run with `python -B` and `-p no:cacheprovider` |
| Arms resolved at baseline | 2 |
| Verdict granularity | per node id: `test_every_golden_exists_and_matches_its_sha256` → KILLED by the one-byte golden flip; `test_manifest_names_base_sha_5cde04e` → stayed GREEN (the flip did not touch the base-SHA field — expected, it is a different conjunct) |
| Arms that stayed GREEN | `test_manifest_names_base_sha_5cde04e` — named; it asserts a different field of the manifest |

| Field | Value |
|---|---|
| **RED counterfactual** | one byte flipped in `tests/goldens/perf/dump/empty.mmd` → `test_every_golden_exists_and_matches_its_sha256` RED · transcript `.dev-flow/2026-10-10-perf-batch/evidence/g0-capture.transcript` §6 · restore digest `228e1f41…ceb37` (§7) |

| Field | Value |
|---|---|
| **Mutation verdicts** | none — no mutation battery in this increment |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_perf_goldens_manifest.py` (sha256 comparison) | one golden byte flipped | `AssertionError: golden drifted: dump/empty.mmd: f3b67fe0…09ae0 != 228e1f41…eb37` (transcript §6) |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 1 instrument shown RED before its PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| `tests/goldens/perf/**` (26 goldens) | `python -B tests/perf_goldens_capture.py` run twice; per-file sha256 compared across runs | `DOUBLE-CAPTURE EQUAL: all 27 files byte-identical across runs 1 and 2` (transcript §3) |
| `tests/goldens/perf/MANIFEST.json` | every recorded sha256 re-computed from the stored bytes | `2 passed` (pytest, transcript §5) |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts, each asserted against the form its producer emitted |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| capture/verification transcript | `.dev-flow/2026-10-10-perf-batch/evidence/g0-capture.transcript` | recorded at the DDR |

| Field | Value |
|---|---|
| **Evidence files** | 1 artifact at the declared home; the 26 goldens' digests are quoted verbatim inside it (each re-verified against the stored bytes at capture time) |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | no — the step adds artifacts; it pins presence, not absence |
| If the result is an ABSENCE, what made the search wide enough | n/a |
| Guard labelled as protecting a CONCLUSION, not a behaviour | the manifest test pins digests, not the code that produced them; the lane tests own the code-side comparison |
| Conjunctive criteria: one mutation per conjunct | the manifest test's two conjuncts (base SHA; per-golden sha256) are asserted per entry; the RED proof flipped a golden byte, covering the sha256 conjunct only — the base-SHA conjunct stayed green by design |
| Synthetic instance of the absent case | n/a |
| **Positive control for every probe that returned an ABSENCE** | n/a — no absence claimed |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rl "goldens/perf" tests/` | `tests/test_perf_goldens_manifest.py` (this step); the lane tests (`test_perf_paint_clip.py`, `tests/test_perf_layout_memo.py`, `tests/test_perf_dump.py`, created in the lanes) will read these goldens — declared at PDR §7 |
| B2 file moved on disk | `grep -rl "perf_goldens_capture" tests/` | `tests/test_perf_goldens_manifest.py` does not import it; the capture script is standalone; lanes import its builders (declared in its docstring) |
| B3 byte-identical golden captures this source | `grep -l "mapper" tests/goldens/perf/MANIFEST.json` | the manifest records `captured_by: tests/perf_goldens_capture.py` |
| B4 artifact produced here is consumed elsewhere | `grep -rl "goldens/perf" tests/ mapper/` | consumers: `tests/test_perf_goldens_manifest.py` now; the four lane test files at Inc-R1/R2/M1/M2 (per PDR §5) |
| A3 | no interface consumed by another module changed | no product symbol touched |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1 · B2 · B3 · B4 · A3), each with its command and verdict; downstream lane consumers are named from the PDR, not assumed |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population | Enumeration method | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| none — no correction | — | — | 0 | — | — |

| Field | Value |
|---|---|
| **Correction population** | none — no correction |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| none | 0 hits | yes | n/a |

### Signed-balance test ledger

`post = base − deleted + added` → `26 = 0 − 0 + 26` goldens (plus 1 manifest, 2 test files)  ✓ reconciles

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | PENDING — orchestrator assigns `code-reviewer` at the batch gate |

---

## 5 · Risks

- The AT-075/075b golden captures the `#map-canvas` region strips; a lane-side change to
  the canvas widget id or the screen layout would make the *comparison* in the lane test
  drift, not this manifest — the manifest only pins bytes on disk.
- The capture script drives the real app at wide-2000/wide-6000; regeneration is slow
  (tens of seconds) by design and must not be added to the default pytest lane.

## 6 · Pending items / spec deviations

- None. (AT-077/077b goldens are not owed: Lane S withdrew to B-118, ledger
  `LED-2026-10-10-perf-batch.3`.)

## 7 · Suggested next task

Fork Lane R (Inc-R1: `mapper/canvas.py` span clip + `tests/test_perf_paint_clip.py`)
and Lane M (Inc-M1: `mapper/model.py` adjacency cache + `tests/test_perf_adjacency.py`)
against these goldens; the lanes' byte-equality arms read `tests/goldens/perf/**`.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 0 source files (transcript §1: `git diff --stat 5cde04e HEAD -- mapper` empty) |
| 2 | Tests written in this same increment | all | ✓ | `tests/test_perf_goldens_manifest.py` (2 nodes, transcript §5) |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ⚠ | none — no product code; capture step only (declared) |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | one golden byte flipped → RED; transcript §6; restore digest §7 |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 5 probes in the table above |
| 6 | `code-reviewer` passed | `core` · `full` | ⚠ | PENDING — named in §4b |
| 7 | No file from another lane touched | all | ✓ | no lane exists yet; `git status` shows only new tests/ files |
| 8 | Frozen interfaces untouched | all | ✓ | no file under `mapper/` touched |
| 9 | Coverage claims verified **on disk** | all | ✓ | every golden's sha256 computed from stored bytes (transcript §4–§5) |
| 10 | Load-bearing emptiness declared | all | ✓ | table above — none claimed |
| 11 | **Mutation verdicts** declared | all | ✓ | none — no mutation battery |
| 12 | **Instrument RED-proof** declared | all | ✓ | sha256 oracle shown RED on a flipped byte (§6) |
| 13 | **Correction population** declared | all | ✓ | none — no correction |
| 14 | **Emitted-form assertion** declared | all | ✓ | double-capture equality + pytest over emitted bytes |
| 15 | **Independent review** names somebody | all | ⚠ | PENDING in §4b (orchestrator assigns) |
| 16 | **Evidence files** declared | all | ✓ | `.dev-flow/2026-10-10-perf-batch/evidence/g0-capture.transcript` |
