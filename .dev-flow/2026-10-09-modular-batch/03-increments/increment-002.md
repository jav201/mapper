# Increment 002 — LLR-MOD.1.1, LLR-MOD.3.1, LLR-MOD.3.2, LLR-MOD.6.1, LLR-MOD.5.2 · `A1 — shared helpers to mapper/screens/common.py (first product move)`

> **Artifact language:** English (`state.json` `language: en`).

> **Owed in.** `core` ✓ · `full` ✓

> **Where this lives:** the **repo**, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-002.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `002` (A1) |
| Lane (if the batch forked) | n/a — the spine is serial; no lanes fork before Inc-B11 |
| Requirement(s) | `LLR-MOD.1.1` (common.py owns the shared helpers + `MapHintLine`, re-exported) · `LLR-MOD.3.1` (21 names still resolve from `mapper.app`) · `LLR-MOD.3.2` (`refusal_sentence` repointed with its reader `_path_refusal`) · `LLR-MOD.6.1` (two of the four B-02 function-local imports closed) · `LLR-MOD.5.2` (extraction-riding test follow-ups) |
| Acceptance | `AT-065` (painted parity) · `AT-067`/`AT-069` pins through the suite · white-box `tests/test_mod_bodies.py` (bodies byte-identical), `tests/test_mod_parity.py` (0 painted diffs), `tests/test_mod_compat.py -k reexport` (identity) · gate: full suite 2977 passed / 0 failed |
| Agent | Product move: **Kimi (`kimi-for-coding`) unit in isolated worktree `wt-moda1`**, with its own RED + sha256-restore log (Kimi unit report, session scratch). Gate run + regression set: **orchestrator (Claude Opus 5.5)**. Independent review: `code-reviewer` (Claude Sonnet). This packet: Kimi unit MODPKT-p1. |
| Date | `2026-10-10` (commit b024a13, 00:49 −0600) |

---

## 1 · What changed

- **Shared helpers moved to `mapper/screens/common.py` (new, 277 lines):** hint-string constants (`COUNT_REGION_ID`, `PAN_INERT_HINT`, `SEARCH_*`, …), `map_hint`/`home_hint`, `MapHintLine`, `screen_bindings`, `keybar_groups`, `_refusal_toast`, `_save_or_toast`, `_path_refusal` — bodies byte-identical (AST), verified by `tests/test_mod_bodies.py` against the Inc-0 baseline.
- **`mapper/app.py` shrinks by ~272 lines** and keeps a re-export block, so all 68 `from mapper.app import …` sites resolve with object identity (LLR-MOD.3.1).
- **B-02 partially closed (LLR-MOD.6.1):** `screens/factory.py` and `screens/settings.py` now import `keybar_groups`/`_save_or_toast` at module level from `screens/common.py`; the remaining function-local `from mapper.app import _PromptScreen` in factory.py stays until A2 by design.
- **Patch repoint (LLR-MOD.3.2):** `common.py` binds `refusal_sentence` at module level from `mapper.osopen` and `_path_refusal` reads it; the suite's patch site in `tests/test_inc9q.py:394` is repointed from `mapper.app` to the `common` module — proven by the RED transcript below.
- Extraction-riding test follow-ups land in the same commit: `test_search.py` source-set follow-up, `test_inc9c.py`/`test_inc9q.py` one-home arms, `test_mod_parity.py` module-list follow-up (LLR-MOD.5.2).

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/common.py` | source | LLR-MOD.1.1, LLR-MOD.3.2 | new — owns the shared helpers, hint constants, `MapHintLine`; binds `refusal_sentence` |
| `mapper/app.py` | source | LLR-MOD.1.1, LLR-MOD.3.1 | ~272 lines cut; re-export block added |
| `mapper/screens/factory.py` | source | LLR-MOD.6.1 | module-level helper import from `screens/common.py`; B-02 back-edge for the moved helpers closed |
| `mapper/screens/settings.py` | source | LLR-MOD.6.1 | module-level `keybar_groups` import from `screens/common.py` |
| `tests/test_search.py` | test | LLR-MOD.5.2 | source-set follow-up riding the extraction |
| `tests/test_inc9c.py` | test | LLR-MOD.5.2 | one-home arm extension |
| `tests/test_inc9q.py` | test | LLR-MOD.3.2 | `refusal_sentence` patch site repointed to the `common` module-global |
| `tests/test_arch_osopen_callers.py` | test | LLR-MOD.5.2 | caller census follow-up |
| `tests/test_mod_parity.py` | test | LLR-MOD.4.2 | painted-module list follows the move |
| `docs/ARCHITECTURE.md` | doc | | `screens/common` row records the landed file |
| `.dev-flow/.../evidence/a1-red-patch-repoint.transcript` | generated | LLR-MOD.3.2 | the RED proof (below) |
| `.dev-flow/.../evidence/a1-regression-set.transcript` | generated | LLR-MOD.4.1 | orchestrator regression set |

| Count | Value |
|---|---|
| **SOURCE files** | **4 / 4** — at the cap: the destination module, `app.py` (re-export), and the two B-02 callers are the exact surface of a behaviour-preserving move of these helpers; cutting it smaller would split one logical extraction |
| Test files | 5 (uncapped) |
| Doc files | 1 (outside the count) |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_mod_bodies.py tests/test_mod_parity.py tests/test_inc9q.py tests/test_search.py tests/test_arch_osopen_callers.py
python -B -m pytest -q -p no:cacheprovider tests/    # the increment gate (full suite)
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | none meeting the criterion standalone | n/a |
| **A · white-box** ↔ LLR | `core` · `full` | `tests/test_mod_bodies.py` (byte-identical bodies), `tests/test_mod_parity.py` (0 diffs vs the Inc-0 golden) | passed |
| **B · black-box** `AT-NNN` ↔ story | `core` · `full` | AT-065 through the painted session at 118/87 | passed |

**Gate (`a1-gate-full-suite.transcript`, 1ff9243b…):** `2977 passed, 24 deselected, 3 xfailed in 1546.29s`, `exit=0`. **Regression set (`a1-regression-set.transcript`, 0eddbdae…):** 873 passed / 0 failed — every test naming a moved name + the census/mod instruments.

The only failing transcript cited in this packet is `a1-red-patch-repoint.transcript` — the deliberate RED capture, `1 failed` **by construction** (the mutation it records). Both gate/regression transcripts hold 0 failed.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | the `refusal_sentence` patch in `tests/test_inc9q.py` put **back on `mapper.app`** (the pre-A1 patch target) — the repoint skipped |
| Instrument | Kimi unit's own hand in worktree `wt-moda1` (orchestor-recorded transcript) |
| Where it ran | the A1 worktree `wt-moda1` — no other session reading it |
| Transcript | `.dev-flow/2026-10-09-modular-batch/evidence/a1-red-patch-repoint.transcript` |
| Restore proven by | `restored; sha256 462111a2c2906532ea08b290731829a50770994245469767094e9f3b8fc7fd5f -> 462111a2c2906532ea08b290731829a50770994245469767094e9f3b8fc7fd5f equal=yes` |
| Bytecode cache | `python -B`, `-p no:cacheprovider` |
| Arms resolved at baseline | 8 (`tests/test_inc9q.py -k cr_f1`: `1 failed, 7 passed, 59 deselected`) |
| Verdict granularity | per node id (`FAILED tests/test_inc9q.py::test_inc9q_cr_f1_the_attachment_paths_use_the_shared_mapping`) |
| Arms that stayed GREEN | the 7 sibling nodes — they do not touch the patch site |

| Field | Value |
|---|---|
| **RED counterfactual** | Transcript: `a1-red-patch-repoint.transcript`. With the patch site back on `mapper.app`: `AttributeError: <module 'mapper.app'> has no attribute 'refusal_sentence'` → `1 failed, 7 passed`. Restore byte-identical (`equal=yes`), re-run `8 passed`. |

| Field | Value |
|---|---|
| **Mutation verdicts** | repoint-skipped mutant: **KILLED** by `test_inc9q_cr_f1_the_attachment_paths_use_the_shared_mapping` (the only arm that names the patch). Arms that stayed GREEN: the 7 siblings (named above). In force at this gate, from Inc-0: `tests/test_mod_bodies.py` (one-token body mutation + deleted import on a tmp copy → RED) and `tests/test_mod_parity.py` (painted-string mutant → RED) — permanent controls; per-arm stored transcripts: not recorded. `tests/test_mod_dispatch.py` is **not yet** in force (lands at B1). |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_inc9q.py` (repointed patch site) | patch put back on `mapper.app` | `AttributeError … has no attribute 'refusal_sentence'` (a1-red-patch-repoint.transcript) |
| `tests/test_mod_bodies.py` | one-token body mutation / deleted import on tmp copy | baseline diff / undefined-global report |
| `tests/test_mod_parity.py` | painted-string mutant in subprocess | painted-line diff |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 3 instruments, each shown RED before its PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the painted screen through the scripted session | `tests/test_mod_parity.py` compares emitted painted lines vs `mod_parity_118.txt`/`mod_parity_87.txt` | 0 diffs at both widths (gate 2977/0) |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 1 artifact (the painted session), asserted on the emitted lines |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| a1-gate-full-suite.transcript | .dev-flow/2026-10-09-modular-batch/evidence/a1-gate-full-suite.transcript | 1ff9243b124556616f1c21a31826a4286f3117a4b1cff362b4aefab2cd3d071f |
| a1-red-patch-repoint.transcript | .dev-flow/2026-10-09-modular-batch/evidence/a1-red-patch-repoint.transcript | e4d781c3331a85e4366fa1733c6758d6148fca4e360f5d312f803842d351f257 |
| a1-regression-set.transcript | .dev-flow/2026-10-09-modular-batch/evidence/a1-regression-set.transcript | 0eddbdae88cd4aeff1416fb9a3daabb2236d49826634fc5c39ec38a2de1cad29 |

| Field | Value |
|---|---|
| **Evidence files** | 3 artifacts, each at the declared home with the digest of its stored bytes (all three re-hashed on disk 2026-10-10 — match) |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes: "no `mapper.app` import from `screens/` for the moved helpers" (B-02 partial) |
| If the result is an ABSENCE, what made the search wide enough | both AST import forms, any scope, over all of `mapper/screens/**.py` (LLR-MOD.6.1 checker) |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `tests/test_arch_osopen_callers.py` + the LLR-MOD.6.1 dependency arms |
| Conjunctive criteria: one mutation per conjunct | the repoint mutant (LLR-MOD.3.2) is separate from the back-edge check (LLR-MOD.6.1) |
| Synthetic instance of the absent case | the RED transcript restores the banned patch shape; a restored function-local import is the LLR-MOD.6.1 tmp-copy mutant |
| **Positive control for every probe that returned an ABSENCE** | factory.py:504's remaining `from mapper.app import _PromptScreen` is the known-present case the same probe still sees (it closes at A2, not here) |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `git grep -l "keybar_groups\|MapHintLine\|_save_or_toast" b024a13 -- tests/` | 6 test files import the moved names (via `mapper.app`) — all green at the gate |
| B2 file moved on disk | `git show b024a13:mapper/app.py \| grep -c "^class MapHintLine\|^def keybar_groups\|^def _save_or_toast"` | 0 — definitions gone from `app.py`; only the re-export block remains |
| B3 byte-identical golden captures this source | goldens capture painted output, not this source | not fired |
| B4 artifact produced here is consumed elsewhere | `screens/common.py` consumed by `app.py` (re-export), `factory.py`, `settings.py` | consumers in-tree, suite green |

| A3 | interface consumed by another module changed | `git grep -n "refusal_sentence" b024a13 -- mapper/screens/common.py tests/test_inc9q.py` | `common.py:30` binds it from `osopen`, `:277` reads it; `test_inc9q.py:394` patches the `common` module-global |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1, B2, B4, A3 fired; B3 not applicable). Every hit re-validated green at the gate |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| B-02 function-local imports of the moved helpers | every function-local `mapper.app` import in `screens/` | premise 6 census (`grep -n "    import" … \| grep mapper`) | 4 total, 2 riding the moved helpers | factory.py + settings.py | the `_PromptScreen` one stays until A2 — its home moves there |

| Field | Value |
|---|---|
| **Correction population** | 1 correction (the B-02 subset), enumerated at P0 before the first site was edited; the A2 remainder is deliberate sequencing, not a leftover |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| helper definitions in `mapper/app.py` | 0 definition hits at b024a13 | yes — only re-exports survive | test_mod_bodies byte-identity green; gate 2977/0 |

### Signed-balance test ledger

`post = base − deleted + added` → collected per-layer counts are not recorded; gate trajectory: 2972 passed (inc0, pre-ARCH-fix) → **2977 passed / 0 failed** at the a1 gate.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, independent of the Kimi unit and the orchestrator) · **APPROVE-WITH-NITS, 0 HIGH / 2 LOW** · CR-1 (narrow `test_search` source set) → done at B0; CR-2 (doc wording) → carried as wording nit, no behaviour impact. |

---

## 5 · Risks

- B-02 is only half-closed: `factory.py`'s function-local `_PromptScreen` import remains a live back-edge until A2; anything merging between A1 and A2 must not "fix" it prematurely (LLR-MOD.5.2's sequencing).
- The `refusal_sentence` repoint makes `common.py` the patch home; a future module that binds a private copy of the name silently kills the patch (the LLR-MOD.3.2 guard test exists for this — it lands with the batch guard tests at B12).

## 6 · Pending items / spec deviations

- CR-2 (doc wording) carried from the review; closed later in the batch (not recorded which increment).
- None open against this increment.

## 7 · Suggested next task

A2 (increment 003): the four literal modals → `mapper/screens/prompt.py`, closing B-02 completely.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 4 / 4 — reason stated in §2 |
| 2 | Tests written in this same increment | all | ✓ | 5 test files in b024a13 |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | n/a — no unit meets the criterion; byte-identity + parity carry the layer |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | §4 — repoint-skipped mutant, transcript + restore digest |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | §4 — 5 probes, 4 fired |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b — APPROVE-WITH-NITS, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | serial spine, single lane |
| 8 | Frozen interfaces untouched | all | ✓ | F1–F5 freeze sealed at PDR; move is body-preserving |
| 9 | Coverage claims verified **on disk** | all | ✓ | gate transcript 2977 passed cited verbatim |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 — B-02 partial absence + positive control |
| 11 | **Mutation verdicts** declared | all | ✓ | §4 — KILLED, 7 named GREEN siblings; permanent controls listed |
| 12 | **Instrument RED-proof** declared | all | ✓ | §4 — 3 instruments |
| 13 | **Correction population** declared | all | ✓ | §4 — B-02 subset enumerated at P0 |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4 — painted session on emitted lines |
| 15 | **Independent review** names somebody | all | ✓ | §4b — `code-reviewer` (Claude Sonnet) |
| 16 | **Evidence files** declared | all | ✓ | §4 — 3 files, sha256 re-verified |
