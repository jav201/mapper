# Increment 003 — LLR-MOD.1.1, LLR-MOD.3.1, LLR-MOD.6.1 · `A2 — prompt modals to mapper/screens/prompt.py; B-02 closed`

> **Artifact language:** English (`state.json` `language: en`).

> **Owed in.** `core` ✓ · `full` ✓

> **Where this lives:** the **repo**, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-003.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `003` (A2) |
| Lane (if the batch forked) | n/a — the spine is serial |
| Requirement(s) | `LLR-MOD.1.1` (`screens/prompt.py` owns the four literal modals, re-exported) · `LLR-MOD.3.1` (imports keep resolving) · `LLR-MOD.6.1` (B-02 closed: the four function-local imports deleted) |
| Acceptance | `AT-065` parity · `AT-070`/`AT-071` dependency surface (asserted fully by the batch guard tests at B12; here: zero `mapper.app` imports under `screens/`) · white-box `tests/test_mod_bodies.py`, `tests/test_mod_parity.py`, `tests/test_arch_osopen_callers.py` · gate: full suite green (a2a3 transcript, 2987/0) |
| Agent | Product move: **Kimi (`kimi-for-coding`) unit in an isolated worktree**, RED + sha256-restore in its own log (Kimi unit report, session scratch — not stored as an evidence file). Gate: **orchestrator (Claude Opus 5.5)**. Group review: `code-reviewer` (Claude Sonnet). This packet: Kimi unit MODPKT-p1. |
| Date | `2026-10-10` (commit 02959fb, 01:10 −0600) |

---

## 1 · What changed

- **Four literal modals moved to `mapper/screens/prompt.py` (new, 246 lines):** `_PromptScreen`, `_ConfirmScreen`, `_TemplateScreen`, `_FichaScreen` — bodies byte-identical (AST-checked against the Inc-0 baseline).
- **`mapper/app.py` shrinks by ~225 lines**; the modal names stay re-exported so every `from mapper.app import _PromptScreen` site resolves with identity (LLR-MOD.3.1).
- **B-02 closed (LLR-MOD.6.1):** the last cycle-dodging function-local import (`factory.py`'s `from mapper.app import _PromptScreen`, ex-:504) is deleted; `factory.py` imports `_PromptScreen` at module level from `screens/prompt.py`. After this commit, zero `mapper.app` imports exist anywhere under `mapper/screens/` (both AST forms, any scope) — verified by probe below.
- `screens/factory.py` (+3/−3) follows the modals; `docs/ARCHITECTURE.md` records the landed `screens/prompt` row.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/prompt.py` | source | LLR-MOD.1.1 | new — owns the four literal modals |
| `mapper/app.py` | source | LLR-MOD.1.1, LLR-MOD.3.1 | ~225 lines cut; re-exports keep the names |
| `mapper/screens/factory.py` | source | LLR-MOD.6.1 | module-level `_PromptScreen` import from `screens/prompt.py`; B-02 back-edge deleted |
| `tests/test_arch_osopen_callers.py` | test | LLR-MOD.6.1, LLR-MOD.5.2 | caller census follows the moved modal |
| `docs/ARCHITECTURE.md` | doc | | `screens/prompt` row records the landed file |

| Count | Value |
|---|---|
| **SOURCE files** | **3 / 4** |
| Test files | 1 (uncapped) |
| Doc files | 1 (outside the count) |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_mod_bodies.py tests/test_mod_parity.py tests/test_arch_osopen_callers.py
python -B -m pytest -q -p no:cacheprovider tests/    # the increment gate (full suite)
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | none meeting the criterion standalone | n/a |
| **A · white-box** ↔ LLR | `core` · `full` | `tests/test_mod_bodies.py` (byte-identical), `tests/test_mod_parity.py` (0 diffs), `tests/test_arch_osopen_callers.py` | passed |
| **B · black-box** `AT-NNN` ↔ story | `core` · `full` | AT-065 painted session | passed |

**Gate (`a2a3-gate-full-suite.transcript`, 79ea316f…):** `2987 passed, 24 deselected, 3 xfailed in 1538.62s`, `exit=0`. **Honest note:** the orchestrator ran one gate over A2 **and** A3 together — no A2-only gate transcript exists; the 2987/0 result covers both increments.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | the Kimi unit's own RED (mutation of the moved surface + sha256 restore) — recorded in the unit's log in session scratch, **not stored** as an evidence file |
| Instrument | Kimi unit hand in its isolated worktree |
| Where it ran | the A2 worktree — no other session reading it |
| Transcript | not recorded at the evidence home (unit log in session scratch) |
| Restore proven by | sha256 equality in the unit log (per the facts sheet: "each with its RED + sha256 restore in its own log") |
| Bytecode cache | `python -B`, `-p no:cacheprovider` |
| Arms resolved at baseline | not recorded |
| Verdict granularity | per node id (unit log) |
| Arms that stayed GREEN | not recorded |

| Field | Value |
|---|---|
| **RED counterfactual** | none stored — a pure code move whose only stored RED artifact is the permanent gate control set (below); the unit-level RED ran and was restored byte-identically per the facts sheet, but its bytes are not recorded. |

| Field | Value |
|---|---|
| **Mutation verdicts** | In force at this gate, from Inc-0: `tests/test_mod_bodies.py` (one-token body mutation + deleted import on a tmp copy → RED) and `tests/test_mod_parity.py` (painted-string mutant → RED). `tests/test_mod_dispatch.py` is **not yet** in force (lands at B1). Increment-specific mutation battery: none stored. |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_mod_bodies.py` | one-token body mutation / deleted import on tmp copy | baseline diff / undefined-global report (Inc-0 RED arms, permanent) |
| `tests/test_mod_parity.py` | painted-string mutant in subprocess | painted-line diff (Inc-0 RED arm, permanent) |
| `tests/test_arch_osopen_callers.py` | a restored function-local `mapper.app` import (the LLR-MOD.6.1 negative control, executed on a tmp copy at Phase 3) | the caller census reports the back-edge |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 3 instruments; the two permanent ones were shown RED at Inc-0, the caller census's RED arm is the LLR-MOD.6.1 negative control (tmp-copy, Phase 3; stored transcript not recorded) |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the painted screen through the scripted session | `tests/test_mod_parity.py` vs `mod_parity_118.txt`/`mod_parity_87.txt` | 0 diffs at both widths (gate 2987/0) |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 1 artifact, asserted on the emitted painted lines |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| a2a3-gate-full-suite.transcript | .dev-flow/2026-10-09-modular-batch/evidence/a2a3-gate-full-suite.transcript | 79ea316f511a8a7e8514e01351d13fec2aa3c9070c4f087df46f99aa8499dff1 |

| Field | Value |
|---|---|
| **Evidence files** | 1 artifact (the shared A2+A3 gate), digest of its stored bytes re-verified on disk 2026-10-10 — match |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes: "zero `mapper.app` imports under `mapper/screens/`" — the closed B-02 state |
| If the result is an ABSENCE, what made the search wide enough | both AST import forms (`import mapper.app` any alias, `from mapper.app import …`), any scope, over `mapper/screens/**.py` |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `tests/test_arch_osopen_callers.py` (later reinforced by `tests/test_mod_deps.py` at B12) |
| Conjunctive criteria: one mutation per conjunct | the B-02 RED = one restored function-local import per mutant (LLR-MOD.6.1 negative control) |
| Synthetic instance of the absent case | a tmp-copy module with a restored function-local import |
| **Positive control for every probe that returned an ABSENCE** | A1's still-open back-edge was the known-present case the same probe class caught between A1 and A2; after this commit the probe's non-absent output is the module-level `factory.py` import from `screens/prompt.py` |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `git grep -ln "_PromptScreen\|_ConfirmScreen" 02959fb -- mapper/` | readers: `mapper/app.py` (re-export), `screens/factory.py` (module-level import), `screens/prompt.py` — all in-tree, suite green |
| B2 file moved on disk | `git show 02959fb:mapper/app.py \| grep -c "^class _PromptScreen\|^class _ConfirmScreen"` | 0 — modal classes gone from `app.py` |
| B3 byte-identical golden | not applicable | not fired |
| B4 artifact produced here is consumed elsewhere | `screens/prompt.py` consumed by `app.py` (re-export) and `factory.py` | consumers in-tree |

| A3 | interface consumed by another module changed | `git grep -n "from mapper.app import\|import mapper.app" 02959fb -- mapper/screens/` | **0 code hits** — only docstring mentions at `common.py:7`/`prompt.py:7`; B-02 closed |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1, B2, B4, A3 fired; B3 not applicable). All hits re-validated green at the gate |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| B-02 function-local imports | every function-local `mapper.app` import in `screens/` | premise 6 census, re-run after A1 | 1 remaining (`factory.py` `_PromptScreen`) | 1 | none — B-02 fully closed |

| Field | Value |
|---|---|
| **Correction population** | 1 correction — the last B-02 import, enumerated at P0 and re-verified after A1 |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| modal classes + the function-local `_PromptScreen` import in `mapper/app.py` / `factory.py` | 0 definition / 0 function-local import hits at 02959fb | yes | probe output above; gate 2987/0 |

### Signed-balance test ledger

`post = base − deleted + added` → collected per-layer counts are not recorded; gate trajectory: 2977 passed (a1) → **2987 passed / 0 failed** (a2a3, covering A2 + A3).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, read-only) — group review **A2–A4 + B0**, covering this increment · **APPROVE-WITH-NITS, 0 HIGH** · every moved class/function of the pre-batch `app.py` (33 names) byte-identical (AST) in its new module; re-exports complete; no back-edges/cycles. 3 MED (vacuous census scans: `test_inc9c:570`, `test_inc9o:338-345`, `test_inc9p:348` + `test_inc9q:387` still hand-listed) → repaired by the post-review census-repair commit (Kimi unit MODREV). 1 LOW (leak-exception key granularity, pre-existing coarseness — carried). |

---

## 5 · Risks

- The 3 MED vacuous-scan findings mean some census arms did not yet see the new homes at this point; they were repaired post-review — between this increment and that repair, a move could theoretically hide behind a hand-listed scan.
- `prompt.py` and `common.py` hold no `mapper.app` import now, but a future modal added to `app.py` and imported function-local would re-open B-02; the B12 `test_mod_deps.py` ban is the durable guard.

## 6 · Pending items / spec deviations

- MED census-scan repairs deferred to the post-review MODREV commit (recorded in §4b); no deviation from the contract.
- None open against this increment.

## 7 · Suggested next task

A3 (increment 004): `ConstructScreen` → `mapper/screens/construct.py`.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 3 / 4 |
| 2 | Tests written in this same increment | all | ✓ | test_arch_osopen_callers.py follow-up in 02959fb |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | n/a — no unit meets the criterion |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | §4 — none stored; permanent controls in force; unit-level RED per facts sheet |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | §4 — 5 probes, 4 fired, 0 code hits for the banned edge |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b — group A2–A4+B0, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | serial spine, single lane |
| 8 | Frozen interfaces untouched | all | ✓ | body-preserving move; F1–F5 freeze intact |
| 9 | Coverage claims verified **on disk** | all | ✓ | gate transcript 2987/0 cited verbatim |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 — the zero-import absence + positive control |
| 11 | **Mutation verdicts** declared | all | ✓ | §4 — permanent controls listed; none stored for this increment |
| 12 | **Instrument RED-proof** declared | all | ✓ | §4 — 3 instruments |
| 13 | **Correction population** declared | all | ✓ | §4 — the last B-02 import |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4 — painted session on emitted lines |
| 15 | **Independent review** names somebody | all | ✓ | §4b — `code-reviewer` group review |
| 16 | **Evidence files** declared | all | ✓ | §4 — 1 file, sha256 re-verified |
