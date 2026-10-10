# Increment 009 — A7 · LLR-MOD.1.1, LLR-MOD.3.2 · `_ImportPreviewScreen moved to mapper/screens/import_preview.py; the LayeredRenderer patch follows its reader`

> **Artifact language:** English.

> **Owed in.** `core` ✓ · `full` ✓

> **Where this lives:** the repo, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-009.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `009` (A7) |
| Lane (if the batch forked) | n/a — serial spine, no lane |
| Requirement(s) | `LLR-MOD.1.1 v1` · `LLR-MOD.3.1` · `LLR-MOD.3.2 v1` · `HLR-MOD.1, 3` |
| Acceptance | `AT-065` (painted parity) · `LLR-MOD.4.1` (full suite at the gate) · `LLR-MOD.4.3` (`tests/test_mod_bodies.py`) · `LLR-MOD.3.2` bite: the repointed `LayeredRenderer` patch site in `tests/test_en8.py` |
| Agent | Product move by a **Kimi (`kimi-for-coding`) unit** in an isolated worktree, with its own RED + sha256 restore in its own log (session scratch — not committed, see §6). Gate run by the **orchestrator**. |
| Date | `2026-10-09/10` (commit dated 2026-10-10) |

---

## 1 · What changed

**`_ImportPreviewScreen` now lives in `mapper/screens/import_preview.py` (101 lines); `mapper/app.py` shed 77 lines; the `LayeredRenderer` monkeypatch now targets the module that actually reads the name.**

- `_ImportPreviewScreen` cut whole from `app.py` into `mapper/screens/import_preview.py`; `mapper/app.py` keeps the re-export (LLR-MOD.1.1/LLR-MOD.3.1).
- **Patch repoint (LLR-MOD.3.2, PDR C1/ARCH-10):** `tests/test_en8.py`'s `LayeredRenderer` patch site (test_en8.py:332) is retargeted from `mapper.app` to `screens/import_preview.py`'s module-global — the reader is `_ImportPreviewScreen` through the CSV-import path, **not** the panning/render concern. `screens/import_preview.py` binds `LayeredRenderer` at module level from its true home, so the patch bites exactly as before.
- `import_preview.py` imports `MapScreen` from `mapper.screens.map` (it constructs one) — never from `mapper.app` (LLR-MOD.1.1/LLR-MOD.6.2).
- `docs/ARCHITECTURE.md` TARGET rows updated.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/app.py` | source | LLR-MOD.1.1, LLR-MOD.3.1 | _ImportPreviewScreen body deleted (−77 lines); re-export kept |
| `mapper/screens/import_preview.py` | source | LLR-MOD.1.1, LLR-MOD.3.2 | new — _ImportPreviewScreen whole (101 lines) + module-level `LayeredRenderer` binding |
| `docs/ARCHITECTURE.md` | doc | | TARGET rows amended (6 lines) |
| `tests/test_en8.py` | test | LLR-MOD.3.2 | the `LayeredRenderer` patch site repointed to `screens/import_preview.py` (5 lines) |

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 4** |
| Test files | 1 (uncapped) |
| Doc files | 1 (`docs/ARCHITECTURE.md`, outside the count) |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider            # the orchestrator's gate command (verbatim from the transcript; A6+A7+A4 shared gate)
python -B -m pytest -q -p no:cacheprovider tests/test_en8.py   # the repointed LayeredRenderer patch must still bite
```

---

## 4 · Test results

A6, A7 and A4 share one gate transcript (`a6a7a4-gate-full-suite.transcript`, run at `45007da`, spine-A complete). Cited verbatim: **`2 failed, 3018 passed, 24 deselected, 3 xfailed in 1567.24s (0:26:07)`**. Both failures name **A4-moved** code, not A7's:

- `FAILED tests/test_inc9m.py::test_inc9m_s1_one_helper_is_imported_by_the_three_callers` — third `safe_local_path` caller is now `screens/home.py`, fixed in `689d537`.
- `FAILED tests/test_repair_artifact_claims.py::test_every_path_line_citation_resolves[store.py]` — `store.py` comment cited `app.py:548`, fixed in `689d537`.

A7's own surface shipped clean: `test_en8.py` (the repointed patch site) passed in the gate — the `LayeredRenderer` patch still bites through `screens/import_preview.py`.

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** (LLR-MOD.4.3 bodies oracle) | `core` · `full` | `tests/test_mod_bodies.py` | passed within the gate run (_ImportPreviewScreen's methods exactly once, `ast.dump`-equal to baseline) |
| **A · white-box** ↔ LLR | `core` · `full` | `tests/test_en8.py` (repointed patch) | passed within the gate run — the patch bites through the new module-global |
| **B · black-box** AT-065 ↔ painted screen | `core` · `full` | `tests/test_mod_parity.py` (widths 118/87) | 0 painted-line diffs within the gate run |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | none committed unique to this increment — a pure move plus one patch repoint; the Kimi unit's own RED + sha256 restore lives in its session log (§6); the permanent controls below ran inside the gate |
| Instrument | in-force permanent RED controls: `tests/test_mod_bodies.py` (one-token body mutation / deleted import on a tmp copy → RED) and `tests/test_mod_parity.py` (painted-string mutant → RED); the bite of the repointed `LayeredRenderer` site is `test_en8.py` itself |
| Where it ran | the Kimi unit's isolated worktree (unit-level); the orchestrator's gate environment (suite) |
| Transcript | `a6a7a4-gate-full-suite.transcript` (suite); the unit-level RED transcript is not committed — not recorded here. No A1-style explicit repoint transcript exists for this repoint — not recorded. |
| Restore proven by | the unit's sha256 restore check (its own log); tmp-copy mutants for the permanent controls |
| Bytecode cache | `python -B`, `-p no:cacheprovider` (gate command verbatim) |
| Arms resolved at baseline | not recorded per arm for this gate |
| Verdict granularity | suite pass/fail per node |
| Arms that stayed GREEN | not recorded |

| Field | Value |
|---|---|
| **RED counterfactual** | none separate committed beyond the in-force permanent controls — the repoint's RED side is LLR-MOD.3.2's guard design (a skipped repoint stops the patch biting while the rest of the suite passes); that guard test (`test_mod_compat.py -k patch_guard`) lands at B12, so at this gate the bite evidence is `test_en8.py` passing through the repointed module-global. |

| Field | Value |
|---|---|
| **Mutation verdicts** | No separate mutation battery. In force at this gate: `test_mod_bodies.py` + `test_mod_parity.py`, both GREEN on the shipped tree. Not yet in force: `test_mod_dispatch.py` (B1), `test_mod_compat.py` patch-guard + `test_mod_deps.py` (B12). Per-arm granularity beyond suite pass/fail: not recorded. |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_en8.py` | (design-level known-bad) a patch left pointing at `mapper.app.LayeredRenderer` after the reader moved | the batch's premise-4 census named this exact silent-failure mode; the repoint prevents it, and the suite bites through the new target — the A1 analogue (`a1-red-patch-repoint.transcript`) demonstrated the same instrument RED for the A1 repoint |
| `tests/test_mod_bodies.py` | (tmp-copy) one-token body mutation / deleted import | RED per its Inc-0 negative controls — proven before this increment, GREEN here |
| `tests/test_mod_parity.py` | (tmp-copy) painted-string mutant | RED per LLR-MOD.4.2's negative control — proven before this increment, 0 diffs here |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 3 instruments — the repoint instrument's RED is demonstrated by the A1 analogue transcript; the two permanent oracles proven RED earlier |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| `mapper/screens/import_preview.py` + pruned `mapper/app.py` (on-disk AST) | `tests/test_mod_bodies.py` — per-method `ast.dump` against the Inc-0 baseline, exactly-once across the package | passed (within the 3018) |
| the repointed patch surface | `test_en8.py` reads `LayeredRenderer` from `screens/import_preview.py`'s module-global and observes the patched value through the shipped CSV-import screen | passed within the gate run |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts (moved AST, repointed patch surface), asserted on disk |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| a6a7a4-gate-full-suite.transcript | .dev-flow/2026-10-09-modular-batch/evidence/a6a7a4-gate-full-suite.transcript | 94ac4057a8e042076a939e885522e4e6d8f0dedf3d72e24ec11f79f5820068ec |
| a1-red-patch-repoint.transcript (the A1 analogue of this increment's repoint instrument) | .dev-flow/2026-10-09-modular-batch/evidence/a1-red-patch-repoint.transcript | e4d781c3331a85e4366fa1733c6758d6148fca4e360f5d312f803842d351f257 |

| Field | Value |
|---|---|
| **Evidence files** | 2 artifacts, cited with the digest of their stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes: "no census method lost or duplicated" (bodies oracle); and "nothing under `screens/` imports `LayeredRenderer` (or any patch name) from `mapper.app`" — review-verified here, AST-enforced only at B12 (⚠) |
| If the result is an ABSENCE, what made the search wide enough | every `*.py` under the package root for the oracle; `grep -rn "from mapper.app import" mapper/screens/` for the import ban |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `tests/test_mod_bodies.py` docstring (exactly-once conclusion); from B12, `test_mod_deps.py`/`test_mod_compat.py` docstrings for the import/patch-guard absences |
| Conjunctive criteria: one mutation per conjunct | body mutation and lost-import arms are separate (LLR-MOD.4.3); repoint-correctness and no-import-ban are separate guards (B12) |
| Synthetic instance of the absent case | the oracle's tmp-copy mutants; the B12 guard tests add synthetic import/repoint arms |
| **Positive control for every probe that returned an ABSENCE** | the 2 gate FAILED nodes on A4's half — the same probes report present (stale) cases |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rl "from mapper.app import" tests` (premise 2: 68 files) | all still resolve via the re-export — 3018 passed includes every importer |
| B2 file moved on disk | readers of _ImportPreviewScreen at the old `app.py` path | none found — no census test pinned this class by path; not fired |
| B3 byte-identical golden captures this source | `grep mapper/app.py tests/goldens/**` | no golden captures source bytes — not fired |
| B4 artifact produced here is consumed elsewhere | `grep -rn "LayeredRenderer" mapper tests` | the reader is now `screens/import_preview.py` (module-global); the only patch site (test_en8.py:332) targets it and bites |

| A3 | interface consumed by another module changed | the `LayeredRenderer` patch surface moved from `mapper.app` to `screens/import_preview.py` | `test_en8.py` green at the gate through the repointed module-global |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run: A3 fired by design (the repoint) and verified by the green patch-carrying test; B1/B4 re-validated; B2/B3 not fired |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| `LayeredRenderer` patch site must target the name's reader | the 8 patch targets of premise 4 | premise 4's full census over every patch form in `tests/` (P0, before any move) | 7 module-global names / 16 sites total | this increment: `LayeredRenderer` ×1 (test_en8.py:332) → `screens/import_preview.py` | `preview_csv` ×2 (A4, next); the rest landed earlier (A1, B0) |

| Field | Value |
|---|---|
| **Correction population** | 1 correction, enumerated at P0 (premise 4) before the first site was edited |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| `LayeredRenderer` read through `mapper.app` | 0 surviving reads in product code (the re-exported name is not the reader) | yes — the reader binds it at module level in `screens/import_preview.py` | `test_en8.py` repoint (5 lines); gate green |

### Signed-balance test ledger

`post = base − deleted + added` → per-increment **collected** counts are not recorded (gate transcripts record passed/failed). Executed progression: 3003 passed / 2 failed (A5b gate) → **3018 passed / 2 failed** (this shared gate). ⚠ not recorded where the ledger's exact terms are unavailable.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, read-only) · group review **A2–A4+B0** · **APPROVE-WITH-NITS, 0 HIGH** · every moved class/function of the pre-batch `app.py` (33 names) byte-identical (AST) in its new module; re-exports complete; **every patch repointed to its reader** (this increment's `LayeredRenderer` repoint included); no back-edges/cycles. 3 MED (vacuous census scans) → repaired post-review (unit MODREV); 1 LOW carried. |

---

## 5 · Risks

- The repoint's dedicated AST guard (`test_mod_compat.py -k patch_guard`) lands at B12; until then a vacuous repoint would be caught only by `test_en8.py` ceasing to bite — which is itself a suite failure, so the window is narrow but real.
- The shared A6+A7+A4 gate means this increment's isolation is argued from a joint transcript; its own failure surface (one class, one patch site) is clean in it.

## 6 · Pending items / spec deviations

- The Kimi unit's own RED + sha256 restore log is session scratch, not committed — its content is not recorded here (only its existence, per the facts sheet).
- None else open.

## 7 · Suggested next task

A4: `HomeScreen` → `mapper/screens/home.py` — the last sibling screen; the `preview_csv` patch sites (test_inc9c.py:114, test_inc9n.py:285) follow their reader; spine A completes.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 2 / 4 |
| 2 | Tests written in this same increment | all | ✓ | `test_en8.py` patch repoint (5 lines) |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `tests/test_mod_bodies.py` passed in the gate |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | §4 — permanent controls + the repoint instrument's A1 analogue |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | §4 — 5 probes; A3 fired by design |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b — group review A2–A4+B0, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | serial spine, one lane |
| 8 | Frozen interfaces untouched (or returned to the trunk) | all | ✓ | patch surface repointed per PDR C1, not redesigned |
| 9 | Coverage claims verified **on disk** | all | ✓ | shared gate on the shipped tree: 3018 passed / 2 failed, cited verbatim |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 — incl. the ⚠ on B12-deferred guards |
| 11 | **Mutation verdicts** declared | all | ✓ | §4 — bodies + parity in force; later arms named as not-yet |
| 12 | **Instrument RED-proof** declared | all | ✓ | §4 — 3 instruments |
| 13 | **Correction population** declared | all | ✓ | §4 — premise-4 census (P0) |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4 — moved AST + repointed patch surface on disk |
| 15 | **Independent review** names somebody | all | ✓ | §4b — `code-reviewer` (Claude Sonnet) |
| 16 | **Evidence files** declared | all | ✓ | §4 — 2 files with sha256 |
