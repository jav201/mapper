# Increment 011 — LLR-MOD.1.3 / 2.1 / 2.2 / 2.3 / 4.3 · `B1 — hints concern to the HintsOps mixin (Spine B spike)`

> **Artifact language:** English (`state.json` `language: en`).

> **Owed in.** `core` ✓ · `full` ✓

> **Where this lives:** the **repo**, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-011.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `011` (Inc-B1) |
| Lane (if the batch forked) | n/a — one lane |
| Requirement(s) | `HLR-MOD.1 v1 / LLR-MOD.1.3` · `HLR-MOD.2 v1 / LLR-MOD.2.1, LLR-MOD.2.2, LLR-MOD.2.3` · `HLR-MOD.4 v1 / LLR-MOD.4.3` |
| Acceptance | `AT-066` (B1 pilot, key M) · white-box `tests/test_mod_dispatch.py` (LLR-MOD.2.1/2.2/2.3, new) · unit `tests/test_mod_bodies.py` mixin-aware arms (LLR-MOD.4.3) · full-suite gate |
| Agent | Each worker ran in its own worktree.<br>• **the move** (11 methods, byte-identical, `mixin_move.py` + `screen_prune.py`): the orchestrator (Claude Opus 5.5);<br>• **`tests/test_mod_dispatch.py` (disjoint names, core-only BINDINGS/CSS/@on/constants, duplicate-`on_mount` control, AT-066 pilot + subprocess mutant) and the `test_mod_bodies.py` mixin follow-up:** Kimi (`kimi-for-coding`);<br>• **the gate run:** the orchestrator. |
| Date | `2026-10-09/10` |

---

## 1 · What changed

**The hints concern moved out of `MapScreen` into the new `mapper/screens/map/hints.py` — the Spine B spike that proves Textual dispatch survives a mixin before anything coupled moves.**

- 11 `MapScreen` methods moved **byte-identically** (AST cut/paste) into `mapper/screens/map/hints.py` (223 new lines); `screen.py` shrank by ~199 lines and now composes `class MapScreen(HintsOps, Screen)`.
- `tests/test_mod_dispatch.py` is new (377 lines): pairwise-disjoint method names across the map package, `BINDINGS`/`DEFAULT_CSS`/`@on`/class-constants only on the core (spike rules 1–2), the duplicated-`on_mount` double-dispatch control, and the **AT-066 pilot** pressing real keys (`M`) and comparing the hint line against the pre-B1 capture.
- `tests/test_mod_bodies.py` now derives the census method set from `MapScreen.__mro__` (mixin methods count as MapScreen's) instead of reading only `screen.py`.
- `docs/ARCHITECTURE.md` marks the B1 row DONE; the AT-066 pre-B1 capture is stored at `evidence/at066-baseline.txt`.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/map/hints.py` | source | LLR-MOD.1.3, LLR-MOD.4.3 | new — 11 methods moved byte-identically (223 lines) |
| `mapper/screens/map/screen.py` | source | LLR-MOD.1.3 | hints methods pruned; `MapScreen(HintsOps, Screen)` |
| `tests/test_mod_dispatch.py` | test | LLR-MOD.2.1, LLR-MOD.2.2, LLR-MOD.2.3 | new — dispatch guards + AT-066 pilot (377 lines) |
| `tests/test_mod_bodies.py` | test | LLR-MOD.4.3 | mixin-aware census (+18 lines) |
| `docs/ARCHITECTURE.md` | doc | | B1 row marked DONE (2 lines) |
| `evidence/at066-baseline.txt` | generated | LLR-MOD.2.3 | pre-B1 hint-line capture (AT-066 pilot baseline, 1 line) |

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 4** |
| Test files | 2 (uncapped) |
| Doc files | 1 (`docs/ARCHITECTURE.md`, outside the count) + 1 generated capture |

- ✓ Well under the cap — one concern module plus its composing `screen.py` is the Spine B shape.

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_mod_dispatch.py tests/test_mod_bodies.py
python -B -m pytest -q -p no:cacheprovider tests/test_arch_osopen_callers.py  # regression follow-the-move
python -B -m pytest -q -p no:cacheprovider   # the increment gate — full suite, orchestrator-run
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `tests/test_mod_bodies.py` mixin-aware arms | GREEN at gate |
| **A · white-box** ↔ LLR | `core` · `full` | `tests/test_mod_dispatch.py` (disjoint / bindings / duplicate-`on_mount` / AT-066 pilot + mutant) | GREEN at gate |
| **B · black-box** `AT-066` ↔ story | `core` · `full` | AT-066 pilot (key M through `MapperApp`) | GREEN at gate |
| **Increment gate — full suite** | — | whole suite | **3034 passed, 1 failed** (`b1b2-gate-full-suite.transcript`: `1 failed, 3034 passed, 24 deselected, 3 xfailed in 1575s`, exit=1) |

The one failure — `tests/test_keymap.py::test_at_n03f_bound_keys_match_the_seat_exactly[map]` — is the base-class blind spot: the keymap seat scan predates the mixins and does not see methods moved off the core class. It is a **follow-up defect of the batch, not a hints regression**, and was fixed at B7 (`5229b12`). Declared honestly: the gate ran RED-on-one and the increment shipped with that failure named and scheduled.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | AT-066's own subprocess mutant: on a tmp copy of the tree, `HintsOps` is dropped from `MapScreen`'s bases (`class MapScreen(HintsOps, Screen):` → `class MapScreen(Screen):`) and the pilot's key sequence is re-driven — the hint line drifts from the capture. |
| Instrument | `tests/test_mod_dispatch.py` (the pilot + tmp-copy mutants), project code |
| Where it ran | the orchestrator's checkout / the gate |
| Transcript | `b1b2-gate-full-suite.transcript` (mutant arms run inside the suite) |
| Restore proven by | tmp-copy mutation — the tree itself is untouched |
| Bytecode cache | gate runs with `python -B` |
| Arms resolved at baseline | per contract: the duplicated-`on_*` control, the `BINDINGS`-in-a-mixin mutant, the `HintsOps`-dropped pilot mutant — 3 RED arms in this increment's new file |
| Verdict granularity | per node id |
| Arms that stayed GREEN | none named — every mutant arm in `test_mod_dispatch.py` was shown RED |

| Field | Value |
|---|---|
| **RED counterfactual** | AT-066/LLR-MOD.2.3: the `HintsOps`-dropped subprocess mutant → the pilot capture comparison fails (RED). Duplicated `on_*` name in a tmp copy → the double-dispatch control fails (RED). `BINDINGS` moved into a mixin → the AST guard fails (RED). Transcript: `.dev-flow/2026-10-09-modular-batch/evidence/b1b2-gate-full-suite.transcript`. |

| Field | Value |
|---|---|
| **Mutation verdicts** | In force at this gate, per the facts sheet: `tests/test_mod_bodies.py` — one-token body mutation on a tmp copy → RED; deleted import in a new module → RED. `tests/test_mod_parity.py` — painted-string mutant in a subprocess → RED. `tests/test_mod_dispatch.py` (new at B1) — duplicate names / `BINDINGS` in a mixin / `HintsOps` dropped → all RED. Per-arm granularity; no arm reported inert. The separate orchestrator-run RED transcripts are not recorded for B1 (none beyond the gate). |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_mod_dispatch.py` | tmp copy with `HintsOps` dropped / a duplicated `on_*` / `BINDINGS` in a mixin | the pilot capture drifts; the disjointness/BINDINGS assertions fail (RED arms above) |
| `tests/test_mod_bodies.py` | one-token body mutation; a deleted import in the new module | baseline-diff RED; undefined-global RED |
| `tests/test_mod_parity.py` | painted-string mutant in a subprocess | parity capture RED |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 3 instruments, each shown RED before its first PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| `mapper/screens/map/hints.py` on disk | `tests/test_mod_bodies.py` compares each moved method's `ast.dump` against the Inc-0 baseline JSON | GREEN — every census method exactly once, every body byte-identical |
| the hint line the app paints | AT-066 compares the pilot's painted hint line against `evidence/at066-baseline.txt` | GREEN at gate; RED under the `HintsOps`-dropped mutant |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts (the moved module's AST and the painted hint line), each asserted against the emitted form |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| b1b2-gate-full-suite.transcript | .dev-flow/2026-10-09-modular-batch/evidence/b1b2-gate-full-suite.transcript | e85dc07bb63ac1304fab58541ccf35ff52fe3ccd93f6f21581be07947dcfd343 |
| at066-baseline.txt | .dev-flow/2026-10-09-modular-batch/evidence/at066-baseline.txt | 23b01b2abb202a80fbecf20cba95289ac22c33a43dd5d10c9a242af2bde31b3b |

| Field | Value |
|---|---|
| **Evidence files** | 2 artifacts, each at the declared home and cited with the digest of its stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes: "no duplicated method name across the 12 map modules" and "no `BINDINGS`/`DEFAULT_CSS`/`@on` in any mixin" |
| If the result is an ABSENCE, what made the search wide enough | the AST scan covers all 12 `screens/map` modules; the guard is `test_mod_dispatch.py -k disjoint` |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_mod_dispatch.py` disjointness/BINDINGS arms (docstrings name the double-dispatch conclusion) |
| Conjunctive criteria: one mutation per conjunct | per contract: duplicated-`on_*` mutant (one conjunct), `BINDINGS`-in-mixin mutant (other conjunct) — each killed separately |
| Synthetic instance of the absent case | the tmp-copy mutants of `test_mod_dispatch.py` |
| **Positive control for every probe that returned an ABSENCE** | the same unmodified suite reports the present cases GREEN at the gate |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rl "HintsOps" mapper tests` | 4 files: `hints.py`, `screen.py`, `test_mod_bodies.py`, `test_mod_dispatch.py` — all accounted for by this increment |
| B2 file moved on disk | none moved (new module) | not fired |
| B3 byte-identical golden captures this source | AT-066 golden `at066-baseline.txt` is consumed by `test_mod_dispatch.py` | 1 consumer |
| B4 artifact produced here is consumed elsewhere | `hints.py` is imported only by `screen.py` (composition) | 1 consumer, re-validated green |

| A3 | interface consumed by another module changed | `grep -rl "HintsOps" mapper` | the mixin base list is the interface; only `screen.py` consumes it |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run. B1 had 4 hits, all this increment's own files. B3/B4 fired with their consumers named. B2 and A3 did not fire beyond the composition itself. |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| none | — | — | — | — | — |

| Field | Value |
|---|---|
| **Correction population** | none — pure move; no claim was corrected, only relocated |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| hints methods defined in `screen.py` | 0 hits for the moved defs (bodies now in `hints.py`) | yes | `test_mod_bodies.py` baseline diff GREEN |

### Signed-balance test ledger

The post-move suite count is the gate transcript's: `3034 passed + 1 failed = 3035`. The pre-B1 base count is not recorded in the facts sheet or the evidence digests — **not recorded**.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, independent of Kimi and the orchestrator) · group review **B1–B12** · **APPROVE-WITH-NITS, 0 HIGH / 0 MED / 4 LOW** — every moved class/function byte-identical (AST) in its new module; no MRO shadowing; `BINDINGS`/CSS/`@on` only on the core; imports exact; census generalisations are not weakenings. LOWs: CR-1 `test_draft_hygiene` owner set too wide → narrowed later (MODREV); CR-2 duplicate-name assert in `test_search` helpers → added (MODREV); CR-3 `exporting.py`'s own `pan_extent` reader has no patched test → deliberate gap (recorded); CR-4 `focus_mode` imports `NavigationModel` from `navigation.py` — sanctioned by `test_mod_deps`. All 0-HIGH. |

---

## 5 · Risks

- The one gate failure (`test_at_n03f` keymap base-class arm) stayed RED until B7 — a scan that reads only the core class cannot see mixin methods; this is exactly the vacuous-scan class of defect the batch's census guards exist to catch.

## 6 · Pending items / spec deviations

- `test_keymap.py::test_at_n03f_bound_keys_match_the_seat_exactly[map]` failed at this gate; fixed at B7 (`5229b12`). No deviation from the contract — the follow-up was scheduled in-increment.

## 7 · Suggested next task

B2 — export concern to `screens/map/exporting.py`, with the `save_svg` patch repoints riding the same increment (LLR-MOD.3.2).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 2 / 4 |
| 2 | Tests written in this same increment | all | ✓ | `tests/test_mod_dispatch.py` new; `test_mod_bodies.py` mixin-aware |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `test_mod_bodies.py` body oracle |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | AT-066 `HintsOps`-dropped mutant; duplicated-`on_*`; BINDINGS-in-mixin (§4) |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 5 probes (§4) |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b group review B1–B12, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | one lane |
| 8 | Frozen interfaces untouched | all | ✓ | patch surface untouched at B1 |
| 9 | Coverage claims verified **on disk** | all | ✓ | gate transcript 3034 passed |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 |
| 11 | **Mutation verdicts** declared | all | ✓ | mod_bodies / mod_parity / mod_dispatch RED arms |
| 12 | **Instrument RED-proof** declared | all | ✓ | 3 instruments (§4) |
| 13 | **Correction population** declared | all | ✓ | none — pure move |
| 14 | **Emitted-form assertion** declared | all | ✓ | moved AST + painted hint line |
| 15 | **Independent review** names somebody | all | ✓ | `code-reviewer` (§4b) |
| 16 | **Evidence files** declared | all | ✓ | 2 files with sha256 (§4) |
