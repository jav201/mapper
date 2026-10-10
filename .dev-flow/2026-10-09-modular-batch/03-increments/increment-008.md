# Increment 008 — A6 · LLR-MOD.1.1 · `PlugRepoScreen moved to mapper/screens/plug_repo.py`

> **Artifact language:** English.

> **Owed in.** `core` ✓ · `full` ✓

> **Where this lives:** the repo, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-008.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `008` (A6) |
| Lane (if the batch forked) | n/a — serial spine, no lane |
| Requirement(s) | `LLR-MOD.1.1 v1` · `LLR-MOD.3.1` · `HLR-MOD.1, 3` |
| Acceptance | `AT-065` (painted parity) · `LLR-MOD.4.1` (full suite at the gate) · `LLR-MOD.4.3` (`tests/test_mod_bodies.py`) · unit `tests/test_mod_parity.py -k parity` |
| Agent | Product move by a **Kimi (`kimi-for-coding`) unit** in an isolated worktree, with its own RED + sha256 restore in its own log (session scratch — not committed, see §6). Gate run by the **orchestrator**. |
| Date | `2026-10-09/10` (commit dated 2026-10-10) |

---

## 1 · What changed

**`PlugRepoScreen` now lives in `mapper/screens/plug_repo.py` (70 lines); `mapper/app.py` shed 54 lines and re-exports the name.**

- `PlugRepoScreen` cut whole from `app.py` into `mapper/screens/plug_repo.py`; `mapper/app.py` keeps the re-export (LLR-MOD.1.1/LLR-MOD.3.1).
- `plug_repo.py` imports `RepoScreen` from `mapper.screens.repo` — never from `mapper.app` and never `MapScreen` (LLR-MOD.1.1, ARCH-9: it pushes `RepoScreen`, which A5b already moved). Test-enforcement of that edge lands with `test_mod_deps.py` at B12; verified here by review and by the green suite.
- `docs/ARCHITECTURE.md` TARGET rows updated; `test_app_imports_used.py` source set follows the package.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/app.py` | source | LLR-MOD.1.1, LLR-MOD.3.1 | PlugRepoScreen body deleted (−54 lines); re-export kept |
| `mapper/screens/plug_repo.py` | source | LLR-MOD.1.1 | new — PlugRepoScreen whole (70 lines) |
| `docs/ARCHITECTURE.md` | doc | | TARGET rows amended (4 lines) |
| `tests/test_app_imports_used.py` | test | LLR-MOD.5.2 | source set follows the package |

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 4** |
| Test files | 1 (uncapped) |
| Doc files | 1 (`docs/ARCHITECTURE.md`, outside the count) |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider            # the orchestrator's gate command (verbatim from the transcript; A6+A7+A4 shared gate)
```

---

## 4 · Test results

A6, A7 and A4 share one gate transcript (`a6a7a4-gate-full-suite.transcript`, run at `45007da`, spine-A complete). Cited verbatim: **`2 failed, 3018 passed, 24 deselected, 3 xfailed in 1567.24s (0:26:07)`**. Both failures name **A4-moved** code, not A6's:

- `FAILED tests/test_inc9m.py::test_inc9m_s1_one_helper_is_imported_by_the_three_callers` — the third `safe_local_path` caller is now `screens/home.py` (A4's move), fixed in `689d537`.
- `FAILED tests/test_repair_artifact_claims.py::test_every_path_line_citation_resolves[store.py]` — a `store.py` comment cited `app.py:548` (A4's move), fixed in `689d537`.

A6's own surface shipped clean: the two failures contain no `plug_repo` reference, and the transcript header says both are "pointing at moved code" of the home-screen extraction. **This increment carries no open failure.**

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** (LLR-MOD.4.3 bodies oracle) | `core` · `full` | `tests/test_mod_bodies.py` | passed within the gate run (PlugRepoScreen's methods exactly once, `ast.dump`-equal to baseline) |
| **A · white-box** ↔ LLR | `core` · `full` | `test_app_imports_used.py` + the moved-source readers | passed within the gate run |
| **B · black-box** AT-065 ↔ painted screen | `core` · `full` | `tests/test_mod_parity.py` (widths 118/87) | 0 painted-line diffs within the gate run |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | none unique to this increment — a pure move; the Kimi unit's own RED + sha256 restore lives in its session log (§6); the permanent controls below ran inside the gate |
| Instrument | in-force permanent RED controls: `tests/test_mod_bodies.py` (one-token body mutation / deleted import on a tmp copy → RED) and `tests/test_mod_parity.py` (painted-string mutant → RED) |
| Where it ran | the Kimi unit's isolated worktree (unit-level); the orchestrator's gate environment (suite) |
| Transcript | `a6a7a4-gate-full-suite.transcript` (suite); the unit-level RED transcript is not committed — not recorded here |
| Restore proven by | the unit's sha256 restore check (its own log); tmp-copy mutants for the permanent controls |
| Bytecode cache | `python -B`, `-p no:cacheprovider` (gate command verbatim) |
| Arms resolved at baseline | not recorded per arm for this gate |
| Verdict granularity | suite pass/fail per node |
| Arms that stayed GREEN | not recorded |

| Field | Value |
|---|---|
| **RED counterfactual** | none separate committed beyond the in-force permanent controls — no new assertion in this increment; the bodies oracle + parity mutant are the executable "the move changed nothing" controls. |

| Field | Value |
|---|---|
| **Mutation verdicts** | No separate mutation battery. In force at this gate: `test_mod_bodies.py` + `test_mod_parity.py`, both GREEN on the shipped tree. Not yet in force: `test_mod_dispatch.py` (B1), the B12 structure/deps/compat/census arms. Per-arm granularity beyond suite pass/fail: not recorded. |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_mod_bodies.py` | (tmp-copy) one-token body mutation / deleted import | RED per its Inc-0 negative controls — proven before this increment, GREEN here |
| `tests/test_mod_parity.py` | (tmp-copy) painted-string mutant | RED per LLR-MOD.4.2's negative control — proven before this increment, 0 diffs here |
| the gate's census readers | (at this very gate, A4's half) stale caller/citation pins | 2 FAILED lines naming A4-moved code — proving the suite reports moved-code rot on this tree |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 3 instruments — the two permanent oracles proven RED earlier, and the census readers printing 2 FAILED at this shared gate |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| `mapper/screens/plug_repo.py` + pruned `mapper/app.py` (on-disk AST) | `tests/test_mod_bodies.py` — per-method `ast.dump` against the Inc-0 baseline, exactly-once across the package | passed (within the 3018) |
| the re-export of `PlugRepoScreen` | `from mapper.app import PlugRepoScreen` resolves to the new module's object | passed within the gate run |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts (moved AST, re-export surface), asserted on disk |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| a6a7a4-gate-full-suite.transcript | .dev-flow/2026-10-09-modular-batch/evidence/a6a7a4-gate-full-suite.transcript | 94ac4057a8e042076a939e885522e4e6d8f0dedf3d72e24ec11f79f5820068ec |

| Field | Value |
|---|---|
| **Evidence files** | 1 artifact (shared with increments 009 and 010), cited with the digest of its stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes: "no census method lost or duplicated" (bodies oracle); and "no `mapper.app` import in `plug_repo.py`" — review-verified here, test-enforced only at B12 (⚠) |
| If the result is an ABSENCE, what made the search wide enough | every `*.py` under the package root for the oracle; `grep -n "import" mapper/screens/plug_repo.py` for the import shape |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `tests/test_mod_bodies.py` docstring (exactly-once conclusion) |
| Conjunctive criteria: one mutation per conjunct | body mutation and lost-import arms are separate (LLR-MOD.4.3) |
| Synthetic instance of the absent case | the oracle's own tmp-copy mutants; the B12 deps test later adds the synthetic `mapper.app` import arm (AT-071 negative control) |
| **Positive control for every probe that returned an ABSENCE** | the 2 gate FAILED nodes on A4's half — the same probes report present (stale) cases |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rl "from mapper.app import" tests` (premise 2: 68 files) | all still resolve via the re-export — 3018 passed includes every importer |
| B2 file moved on disk | readers of PlugRepoScreen at the old `app.py` path | none found — no census test pinned this class by path; not fired |
| B3 byte-identical golden captures this source | `grep mapper/app.py tests/goldens/**` | no golden captures source bytes — not fired |
| B4 artifact produced here is consumed elsewhere | `grep -rn "PlugRepoScreen" mapper tests` | consumed via `mapper/app.py` re-export (`screens/factory.py` constructs it); gate green |

| A3 | interface consumed by another module changed | `plug_repo.py` → `screens.repo.RepoScreen` import edge (new) | the suite's import resolution green; the edge's shape (`RepoScreen`, not `MapScreen`, not `mapper.app`) verified by the group review, test-enforced at B12 |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run: none fired for this class; B1/B4 re-validated green; the new A3 edge named for B12 enforcement |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| none — a pure move with no repoint and no census follow-up of its own | n/a | n/a | 0 | 0 | n/a |

| Field | Value |
|---|---|
| **Correction population** | none — no correction in this increment (the repo/home edges were handled by A5b/A4) |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| PlugRepoScreen defined in `mapper/app.py` | 0 surviving stale refs (re-export is the sanctioned positive ref) | yes — re-export is LLR-MOD.3.1's required shape, not a stale one | gate green; group review "re-exports complete" |

### Signed-balance test ledger

`post = base − deleted + added` → per-increment **collected** counts are not recorded (gate transcripts record passed/failed). Executed progression: 3003 passed / 2 failed (A5b gate) → **3018 passed / 2 failed** (this shared gate). ⚠ not recorded where the ledger's exact terms are unavailable.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, read-only) · group review **A2–A4+B0** · **APPROVE-WITH-NITS, 0 HIGH** · every moved class/function of the pre-batch `app.py` (33 names) byte-identical (AST) in its new module; re-exports complete; every patch repointed to its reader; no back-edges/cycles. 3 MED (vacuous census scans) → repaired post-review (unit MODREV); 1 LOW carried. |

---

## 5 · Risks

- The `plug_repo → screens.repo` import edge is correct by review and green suite, but its **test enforcement is deferred to B12** (`test_mod_deps.py`, AT-071) — a regression between A6 and B12 would be caught by nothing automatic. Same ⚠ as increments 006–007.
- The shared A6+A7+A4 gate means this increment's isolation is argued from a joint transcript; its surface is small (one class, no patch targets) and the joint failures name only A4-moved code.

## 6 · Pending items / spec deviations

- The Kimi unit's own RED + sha256 restore log is session scratch, not committed — its content is not recorded here (only its existence, per the facts sheet).
- None else open.

## 7 · Suggested next task

A7: `_ImportPreviewScreen` → `mapper/screens/import_preview.py`, with the `LayeredRenderer` patch repointed to its true reader (the CSV-import path — PDR C1/ARCH-10).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 2 / 4 |
| 2 | Tests written in this same increment | all | ⚠ | only `test_app_imports_used.py`'s source-set line followed the move — no new assertion was needed for a pure move with no patch target; stated honestly |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `tests/test_mod_bodies.py` passed in the gate |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | §4 — in-force permanent controls; no new assertion of its own |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | §4 — 5 probes, none fired; new A3 edge named for B12 |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b — group review A2–A4+B0, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | serial spine, one lane |
| 8 | Frozen interfaces untouched (or returned to the trunk) | all | ✓ | re-export surface preserved |
| 9 | Coverage claims verified **on disk** | all | ✓ | shared gate on the shipped tree: 3018 passed / 2 failed, cited verbatim |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 — incl. the ⚠ on the B12-deferred deps ban |
| 11 | **Mutation verdicts** declared | all | ✓ | §4 — bodies + parity in force; later arms named as not-yet |
| 12 | **Instrument RED-proof** declared | all | ✓ | §4 — 3 instruments |
| 13 | **Correction population** declared | all | ✓ | §4 — none, with reason |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4 — moved AST + re-export on disk |
| 15 | **Independent review** names somebody | all | ✓ | §4b — `code-reviewer` (Claude Sonnet) |
| 16 | **Evidence files** declared | all | ✓ | §4 — 1 file with sha256 |
