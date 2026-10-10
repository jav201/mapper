# Increment 017 — LLR-MOD.1.3, LLR-MOD.5.2 · `B7 — draft concern to the DraftsOps mixin; census follow-ups`

> **Artifact language:** English.
> **Owed in.** `core` ✓ · `full` ✓
> **Where this lives:** the repo, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-017.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `017` (B7) |
| Lane (if the batch forked) | n/a — one lane |
| Requirement(s) | `LLR-MOD.1.3` (drafts module owns its census methods) · `LLR-MOD.5.2` (extraction-riding test follow-ups land in the increment) |
| Acceptance | full suite at the B3–B9 gate · the permanent guard tests (`test_mod_bodies.py`, `test_mod_parity.py`, `test_mod_dispatch.py`) · `tests/test_draft_hygiene.py`, `tests/test_keymap.py` follow-ups |
| Agent | Product move `fd8a4e8` — orchestrator script (`mixin_move.py`, AST cut/paste; Claude Opus 5.5). Census follow-ups `5229b12` — orchestrator. Gate — orchestrator. |
| Date | `2026-10-10` |

---

## 1 · What changed

- **The draft concern moved.** The draft-handling methods of `MapScreen` moved byte-identically (AST cut/paste) from `mapper/screens/map/screen.py` into the new `mapper/screens/map/drafts.py`, which defines `class DraftsOps` (`drafts.py:20`). `screen.py` composes it as one more mixin base.
- **`test_draft_hygiene.py` follows the mixins.** `test_llr_001_2_no_read_of_the_guard_flag_outside_map_screen` no longer hard-pins the owner class: the allowed owner set is derived at runtime from `MapScreen.__mro__` (`{"MapScreen"} ∪ {mixin names whose module is mapper.screens.map}`), because `DraftsOps` now holds `_guard_draft`/`guard_open`.
- **`test_keymap.py` follows the mixins.** `test_at_n03f_bound_keys_match_the_seat_exactly` no longer assumes the framework base is `__mro__[1]` (a plain mixin since B1); it takes the first MRO class carrying `_merged_bindings`. This fixed the one failure recorded at the B1+B2 gate ("keymap base class, fixed at B7 5229b12").

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/map/drafts.py` | source | LLR-MOD.1.3 | new — `DraftsOps` mixin (205 lines) |
| `mapper/screens/map/screen.py` | source | LLR-MOD.1.3 | draft methods removed; mixin base added (−191/+4) |
| `tests/test_draft_hygiene.py` | test | LLR-MOD.5.2 | guard-flag owner set derived from the MRO (+10/−1) |
| `tests/test_keymap.py` | test | LLR-MOD.5.2 | framework base = first MRO class with `_merged_bindings` (+4/−1) |

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 4** |
| Test files | 2 (uncapped) |
| Doc files | 0 |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/   # the increment gate (orchestrator-run; transcript cited in §4)
python -B -m pytest -q -p no:cacheprovider tests/test_mod_bodies.py tests/test_mod_parity.py tests/test_mod_dispatch.py tests/test_draft_hygiene.py tests/test_keymap.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `tests/test_mod_bodies.py` (per-method byte-identity + undefined-globals) | passed — gate transcript |
| **A · white-box** ↔ LLR | `core` · `full` | `tests/test_mod_dispatch.py`, `test_draft_hygiene.py`, `test_keymap.py` | passed — gate transcript |
| **B · black-box** | `core` · `full` | AT-065 parity (`test_mod_parity.py`, both widths) | passed — gate transcript |
| **Gate** | — | full suite | **3060 passed, 24 deselected, 3 xfailed, 0 failed, exit=0** (`b3b9-gate-full-suite.transcript`) |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | none hand-applied in this increment — pure move; the suite's permanent RED controls ran inside the gate |
| Instrument | suite-owned tmp-copy mutants (see below) |
| Where it ran | the main checkout |
| Transcript | `b3b9-gate-full-suite.transcript` (GREEN); the pre-fix RED is `b1b2-gate-full-suite.transcript` (3034 passed / **1 failed**, the `test_keymap` base-class assumption — the mutation here is the B1 mixin landing under `__mro__[1]`) |
| Restore proven by | n/a — no hand mutation |
| Bytecode cache | gate run under `python -B`; suite conventions hold |
| Arms resolved at baseline | the permanent controls in force at this gate: `test_mod_bodies.py` (2 mutant kinds), `test_mod_parity.py` (1), `test_mod_dispatch.py` (3 mutant kinds) — per facts sheet |
| Verdict granularity | per resolved node id, per facts sheet |
| Arms that stayed GREEN | none recorded |

| Field | Value |
|---|---|
| **RED counterfactual** | The increment's own new assertions are the two census follow-ups. Their RED evidence is the B1+B2 gate: with the mixins landed but `test_keymap` still reading `__mro__[1]`, `b1b2-gate-full-suite.transcript` shows **1 failed** — the instrument bit before it was repaired in `5229b12`. Transcript: `.dev-flow/2026-10-09-modular-batch/evidence/b1b2-gate-full-suite.transcript`. No hand mutation, no restore digest — the RED state is a committed gate history, not a tmp edit. |

| Field | Value |
|---|---|
| **Mutation verdicts** | The pure-move battery ran inside the B3–B9 gate, per the facts sheet: `test_mod_bodies.py` — one-token body mutation in a moved method on a tmp copy → RED (KILLED); deleted import in a new module → RED (KILLED). `test_mod_parity.py` — painted-string mutant in a subprocess → RED (KILLED). `test_mod_dispatch.py` (in force since B1) — duplicated `on_*`/`action_*` names → RED; `BINDINGS` in a mixin → RED; `HintsOps` dropped from the bases → RED. Per-node transcripts live in the gate transcript; arms that stayed GREEN: none recorded. |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_keymap.py` base-class derivation | the B1 mixin landing at `__mro__[1]` | `1 failed` at the B1+B2 gate (`b1b2-gate-full-suite.transcript`) |
| `tests/test_mod_bodies.py` | one-token body mutation / deleted import (tmp copy) | RED arms per facts sheet (run at every gate) |
| `tests/test_mod_parity.py` | painted-string mutant (subprocess) | RED arm per facts sheet |
| `tests/test_mod_dispatch.py` | duplicate names / mixin BINDINGS / dropped mixin | RED arms per facts sheet |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 instruments, each shown RED before its PASS was believed (the keymap instrument's RED is the recorded B1+B2 gate failure) |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the shipped `mapper/screens/map/drafts.py` source | `test_mod_bodies.py` compares each moved method's `ast.dump` against the Inc-0 baseline JSON (`.dev-flow/2026-10-09-modular-batch/evidence/mod-bodies-baseline.json`) on disk | passed at the gate |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 1 artifact (the shipped drafts module), asserted on disk against the Inc-0 baseline |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| b3b9-gate-full-suite.transcript | .dev-flow/2026-10-09-modular-batch/evidence/b3b9-gate-full-suite.transcript | 027b617017a980f3dab46ff218e837f1e497e9b97c03c4b73cae2a0153e7e6d3 |
| b1b2-gate-full-suite.transcript | .dev-flow/2026-10-09-modular-batch/evidence/b1b2-gate-full-suite.transcript | e85dc07bb63ac1304fab58541ccf35ff52fe3ccd93f6f21581be07947dcfd343 |

| Field | Value |
|---|---|
| **Evidence files** | 2 artifacts, each at the declared home and cited with the digest of its stored bytes (`_facts/evidence-digests.md`) |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — "no read of `_draft_guard_open` outside MapScreen's mixin MRO" and "no method lost or duplicated by the move" |
| If the result is an ABSENCE, what made the search wide enough | the owner set is derived from `MapScreen.__mro__` at runtime (not hand-listed); the bodies check enumerates the full census roster against the package |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_llr_001_2_no_read_of_the_guard_flag_outside_map_screen`; `test_mod_bodies.py` exactly-once roster arms |
| Conjunctive criteria: one mutation per conjunct | no new conjunctive criterion — the move reuses the batch-standing guards |
| Synthetic instance of the absent case | the pre-B7 hard-pin (owner == `["MapScreen"]`) is itself the synthetic present case: it FAILED once the mixin landed (B1+B2 gate), i.e. the unmodified instrument reported the present case before the fix |
| **Positive control for every probe that returned an ABSENCE** | the B1+B2 gate failure is the positive control for the keymap probe; for the bodies exactly-once probe, the tmp-copy mutants (deleted/duplicated method) are the positive controls per the facts sheet |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rln "DraftsOps" tests mapper` | `tests/test_draft_hygiene.py` (re-run green in the gate), `mapper/screens/map/drafts.py`, `mapper/screens/map/screen.py` — no stale reader |
| B2 file moved on disk | `grep -n "def .*draft" mapper/screens/map/screen.py` | draft handlers gone from the core; the core keeps only lifecycle (+ the B8 deviation later) |
| B3 byte-identical golden captures this source | `grep -rl "drafts" tests/goldens/** 2>/dev/null` | not fired — no golden directory reads the module by path |
| B4 artifact produced here is consumed elsewhere | `grep -rln "drafts" mapper/screens/map/` | consumed by `screen.py` (composition) and `__init__.py` re-export chain |

| A3 | interface consumed by another module changed | `grep -rn "_draft_guard_open\|guard_open" mapper/` | only `drafts.py` + `screen.py` reads; re-validated by `test_draft_hygiene` in the gate |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1, B2, B4, A3 fired with the hits above, each re-validated green in the gate; B3 did not fire) |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| guard-flag owner may be MapScreen or any Spine B mixin | every class allowed to read `_draft_guard_open` | runtime derivation from `MapScreen.__mro__` (commit `5229b12`) | 2 at B7 (core + `DraftsOps`) | `tests/test_draft_hygiene.py:139` | none — derivation absorbs later mixins without edits |
| framework base class under mixin MRO | every class that can contribute merged bindings | runtime scan for the first MRO class with `_merged_bindings` (commit `5229b12`) | 1 | `tests/test_keymap.py:151` | none |

| Field | Value |
|---|---|
| **Correction population** | 2 corrections, each converted from a hand-pinned population to a runtime-derived one in this increment |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| `owner.__mro__[1]` base-class pin in `test_keymap.py` | 0 hits in `tests/test_keymap.py` | yes | replaced derivation at `tests/test_keymap.py:148-151`, green at the B3–B9 gate |

### Signed-balance test ledger

`post = base − deleted + added` — the B3–B9 gate is shared across B3–B9; a per-increment collection count was not recorded. Gate deltas: b1b2 = 3034 passed / 1 failed → b3b9 = 3060 passed / 0 failed; `5229b12` added no new test nodes (edits to existing arms only).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, read-only; group review B1–B12) · **APPROVE-WITH-NITS, 0 HIGH / 0 MED** · "No MRO shadowing; BINDINGS/CSS/@on only on the core; imports exact; patch repoints correct; census generalisations are not weakenings." 4 LOW, of which **CR-1** names this increment: `test_draft_hygiene`'s owner set was too wide → narrowed by the post-review census-repair commit (Kimi unit MODREV; its sha is not recorded in this worktree's history). CR-2/CR-3/CR-4 belong to B9/B2/B5. |

---

## 5 · Risks

- The MRO-derived owner/base sets assume every future mixin legitimately holding the flag is a `mapper.screens.map` class in `MapScreen`'s MRO — a concern module that reads the flag without being composed would be caught, but a mixin added to the MRO silently widens the allowance.
- `DraftsOps` holds shared draft state (`_guard_draft`/`guard_open`); F1/F2 freeze discipline applies and is only made mechanical at B12 (LLR-MOD.7.2).

## 6 · Pending items / spec deviations

- The post-review census-repair commit (Kimi unit MODREV) that narrowed CR-1 is not present in this worktree's git history — its sha is **not recorded**; its content is described only by the facts sheet.

## 7 · Suggested next task

B8 — the nav concern to `NavOps` (`increment-018`).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 2 / 4 |
| 2 | Tests written in this same increment | all | ✓ | `5229b12` — `tests/test_draft_hygiene.py`, `tests/test_keymap.py` |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `test_mod_bodies.py` at the gate |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | B1+B2 gate `1 failed` pre-fix (§4) |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 5 probes (§4) |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | one lane |
| 8 | Frozen interfaces untouched | all | ✓ | bodies byte-identical per `test_mod_bodies` |
| 9 | Coverage claims verified **on disk** | all | ✓ | 3060 passed at the gate |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 |
| 11 | **Mutation verdicts** declared | all | ✓ | bodies/parity/dispatch arms KILLED (§4) |
| 12 | **Instrument RED-proof** declared | all | ✓ | 4 instruments (§4) |
| 13 | **Correction population** declared | all | ✓ | 2 corrections (§4) |
| 14 | **Emitted-form assertion** declared | all | ✓ | shipped `drafts.py` vs Inc-0 baseline |
| 15 | **Independent review** names somebody | all | ✓ | group review B1–B12 |
| 16 | **Evidence files** declared | all | ✓ | 2 files with sha256 |
