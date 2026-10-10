# Increment 001 — LLR-MOD.4.2, LLR-MOD.4.3, LLR-MOD.5.1 · `Inc-0 — parity golden, body baseline, source-reading tests generalised (test-only)`

> **Artifact language:** English (`state.json` `language: en`).

> **Owed in.** `core` ✓ · `full` ✓

> **Where this lives:** the **repo**, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-001.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `001` (Inc-0) |
| Lane (if the batch forked) | n/a during the batch — the spine is serial; Inc-0 itself ran as parallel test-only sub-lanes (contract §2.8) |
| Requirement(s) | `LLR-MOD.4.2 v1` (parity golden) · `LLR-MOD.4.3 v1` (body baseline) · `LLR-MOD.5.1 v1` (six source-reading tests generalised) · traces `HLR-MOD.4`, `HLR-MOD.5` |
| Acceptance | `AT-065` (painted-capture golden at 118/87 cols) · `AT-069` (per-file assertion-count baseline) · white-box `tests/test_mod_bodies.py` (LLR-MOD.4.3 oracle), `tests/test_mod_parity.py` (LLR-MOD.4.2 runner) · unit none |
| Agent | The Inc-0 test generalisation + goldens/baselines: **not recorded** in the facts sheet (Inc-0 ran as six disjoint test-only sub-lanes). The ARCHITECTURE TARGET-row fix (20c0161) and the gate run: **orchestrator (Claude Opus 5.5)**. This packet: Kimi unit MODPKT-p1. |
| Date | `2026-10-10` (commits 90e731b 00:11, 20c0161 00:38, −0600) |

---

## 1 · What changed

- **AT-065 golden captured on the pre-move commit** `23c90f1a7df85f95f868e23b98840c30f247ee93` ("chore(dev-flow): modular batch PDR -> P3"): TEXT captures of the scripted session (open a map, move, search, toggle a view, export, quit) at widths 118 and 87, stored at the evidence home (`mod_parity_118.txt`, `mod_parity_87.txt`); volatile cells normalised, steps gated on condition waits.
- **LLR-MOD.4.3 body baseline captured:** `mod-bodies-baseline.json` — per-method `ast.dump` of every census method, the oracle every later increment diffs against.
- **AT-069 baseline recorded:** `at069-baseline.json` — today's per-file assertion counts (`test_draft_hygiene.py` ≥ 9, `test_darkside_census.py` ≥ 55, `test_keymap.py` ≥ 35, `test_en5.py` ≥ 34, `test_en7.py` ≥ 37, `test_app_imports_used.py` ≥ 2) and the 14 `("mapper/app.py", line)` darkside pins.
- **Six source-reading tests generalised to the package (LLR-MOD.5.1)** before any code moves: pins locate constructs by content across `mapper/**/*.py` (or via `inspect.getfile(MapScreen)`); `test_keymap.py`'s module set is derived by `pkgutil.walk_packages` (the hand-pinned list is gone). Two new instruments ship: `tests/test_mod_bodies.py` and `tests/test_mod_parity.py`, each carrying its own tmp-copy RED controls.
- **Gate found `test_repair_map_truth` red** (8 AT-P04 owned-path arms: the ARCHITECTURE composition table declared TARGET files not yet on disk); fixed in 20c0161 by taking the TARGET rows out of the composition table — the map declares only files on disk.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `tests/test_mod_parity.py` | test | LLR-MOD.4.2 | new: re-drives the scripted session, compares painted lines against the committed goldens; painted-string mutant on a tmp copy → RED |
| `tests/test_mod_bodies.py` | test | LLR-MOD.4.3 | new: per-method `ast.dump` vs `mod-bodies-baseline.json`; exactly-once census; undefined-global check on new modules; one-token + deleted-import mutants on a tmp copy → RED |
| `tests/test_darkside_census.py` | test | LLR-MOD.5.1, HLR-MOD.5 | 14 pins generalised to "exactly one home in the package" |
| `tests/test_draft_hygiene.py` | test | LLR-MOD.5.1 | MapScreen arms parse `inspect.getfile(MapScreen)` |
| `tests/test_keymap.py` | test | LLR-MOD.5.1 | module set from `pkgutil.walk_packages(mapper)` |
| `tests/test_en5.py` | test | LLR-MOD.5.1 | pins located by content across the package |
| `tests/test_en7.py` | test | LLR-MOD.5.1 | pins located by content across the package |
| `tests/test_app_imports_used.py` | test | LLR-MOD.5.1 | unused-import scan walks the package |
| `.dev-flow/.../evidence/mod_parity_118.txt` | generated | LLR-MOD.4.2 | AT-065 golden, width 118 |
| `.dev-flow/.../evidence/mod_parity_87.txt` | generated | LLR-MOD.4.2 | AT-065 golden, width 87 |
| `.dev-flow/.../evidence/mod-bodies-baseline.json` | generated | LLR-MOD.4.3 | body baseline JSON |
| `.dev-flow/.../evidence/at069-baseline.json` | generated | LLR-MOD.5.1, HLR-MOD.5 | AT-069 per-file counts + pins |
| `docs/ARCHITECTURE.md` | doc | | TARGET rows removed from the composition table (20c0161) |
| `.dev-flow/.../evidence/inc0-gate-full-suite.transcript` | generated | LLR-MOD.4.1 | the gate run (20c0161) |

| Count | Value |
|---|---|
| **SOURCE files** | **0 / 4** — test-only increment; the contract forbids any `mapper/**` edit at Inc-0, and none was made |
| Test files | 8 (uncapped) |
| Doc files | 1 (`docs/ARCHITECTURE.md`, outside the count) |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_mod_parity.py tests/test_mod_bodies.py tests/test_draft_hygiene.py tests/test_darkside_census.py tests/test_keymap.py tests/test_en5.py tests/test_en7.py tests/test_app_imports_used.py
python -B -m pytest -q -p no:cacheprovider tests/    # the increment gate (full suite)
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | none — no unit meets the criterion | n/a |
| **A · white-box** ↔ LLR | `core` · `full` | `tests/test_mod_bodies.py`, `tests/test_mod_parity.py`, the six generalised files | see gate |
| **B · black-box** `AT-NNN` ↔ story | `core` · `full` | AT-065 golden capture (pre-move), AT-069 baseline | recorded in evidence |

**Gate (`inc0-gate-full-suite.transcript`, c8f832d8…):** `8 failed, 2972 passed, 24 deselected, 3 xfailed in 1550.19s`, `exit=1`. All 8 failures are `tests/test_repair_map_truth.py::test_at_p04_every_owned_path_exists_on_disk[…]` — the composition table declared the 7 TARGET sibling screens + `mapper/screens/map/*.py`, which matched nothing on disk. **This was the gate doing its job, not a regression**: 20c0161 removed the TARGET rows (the map declares only files on disk). A standalone post-fix re-run of the inc0 gate is not recorded; the next gate (a1, `2977 passed … exit=0`) includes the fixed ARCHITECTURE and these tests green.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | tmp-copy arms shipped inside the new instruments: (a) one-token mutation inside a moved method body; (b) a deleted import in a new module; (c) a painted-string mutant in the parity subprocess |
| Instrument | the new tests themselves, run on a tmp copy of the tree (LLR-MOD.4.3 / LLR-MOD.4.2 negative controls, contract Phase 3) |
| Where it ran | tmp copy — never the working tree |
| Transcript | per-arm stored transcripts: **not recorded** — the arms are permanent and re-execute inside every later gate |
| Restore proven by | tmp copy discarded — the product tree was never mutated |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1`, `python -B` |
| Arms resolved at baseline | not recorded as a count (the arms live inside the two new test files) |
| Verdict granularity | per resolved node id within each instrument |
| Arms that stayed GREEN | none recorded |

| Field | Value |
|---|---|
| **RED counterfactual** | The two new instruments carry their own RED arms (mutations a–c above) executed at Phase 3; per-arm transcripts are not recorded. Additionally the AT-069 negative control (one pinned darkside line duplicated into a second module → "exactly one home" fails; one pin deleted → the pin fails) was executed per the contract's Phase-3 plan; a stored transcript is not recorded. |

| Field | Value |
|---|---|
| **Mutation verdicts** | mutations (a) and (b): KILLED by `tests/test_mod_bodies.py`; mutation (c): KILLED by `tests/test_mod_parity.py`; per-arm detail and inert-arm accounting: not recorded beyond the instruments' own assertions. The duplicated-pin and deleted-pin AT-069 mutants: KILLED (contract negative control; stored transcript not recorded). |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_mod_bodies.py` | one-token body mutation + deleted import on a tmp copy | baseline diff non-empty / undefined-global report (its RED arm) |
| `tests/test_mod_parity.py` | painted-string mutant in a subprocess | painted-line diff |
| the gate itself | ARCHITECTURE TARGET rows for files not on disk | `8 failed … test_at_p04_every_owned_path_exists_on_disk` (inc0 transcript) — the honest failure above |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 3 instruments, each shown RED before its first PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| `mod_parity_118.txt` / `mod_parity_87.txt` | golden record: captured on commit `23c90f1a7df85f95f868e23b98840c30f247ee93`; sha256 of the stored bytes asserted by `tests/test_mod_parity.py` | `43af8e1e7613f23e9da0b9a3090c880c6b6f1cc0341f9befb8e032efd95fbf2d` (118) · `6ba755535f102742931c93af98a54889ea4ecc6e132f43a1db78f8461a889b9b` (87) — re-verified on disk 2026-10-10 |
| `mod-bodies-baseline.json` | pinned path read by `tests/test_mod_bodies.py` | sha256 `7c76289cb7ed2649cc01edb870bc7d49d28d1cbf15eca3e1f7947f504aec6836` — re-verified on disk |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 3 artifacts (2 goldens + the body baseline), each asserted at its stored bytes' sha256 |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| mod_parity_118.txt | .dev-flow/2026-10-09-modular-batch/evidence/mod_parity_118.txt | 43af8e1e7613f23e9da0b9a3090c880c6b6f1cc0341f9befb8e032efd95fbf2d |
| mod_parity_87.txt | .dev-flow/2026-10-09-modular-batch/evidence/mod_parity_87.txt | 6ba755535f102742931c93af98a54889ea4ecc6e132f43a1db78f8461a889b9b |
| mod-bodies-baseline.json | .dev-flow/2026-10-09-modular-batch/evidence/mod-bodies-baseline.json | 7c76289cb7ed2649cc01edb870bc7d49d28d1cbf15eca3e1f7947f504aec6836 |
| at069-baseline.json | .dev-flow/2026-10-09-modular-batch/evidence/at069-baseline.json | f6415704ac4323130ab53f8e198fba226b635645fd9b9828ad0839658bd6fe50 |
| inc0-gate-full-suite.transcript | .dev-flow/2026-10-09-modular-batch/evidence/inc0-gate-full-suite.transcript | c8f832d8bee50e2a23b528e33d15758245e842c5a13c5cf5fa9c6ac01b13cd8e |

| Field | Value |
|---|---|
| **Evidence files** | 5 artifacts, each at the declared home and cited with the digest of its stored bytes (all five re-hashed on disk 2026-10-10 — match) |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes: AT-069's "exactly one home per pin" and LLR-MOD.4.3's "every census method exactly once across the package" |
| If the result is an ABSENCE, what made the search wide enough | the whole `mapper/**/*.py` package (content-based pin search), not a path list |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `tests/test_mod_bodies.py` exactly-once arms; `test_darkside_census.py` one-home pins |
| Conjunctive criteria: one mutation per conjunct | duplicated pin (two homes) and deleted pin each have their own mutant (AT-069 negative control) |
| Synthetic instance of the absent case | the duplicated-pin tmp copy and the deleted-pin product mutant |
| **Positive control for every probe that returned an ABSENCE** | the same pins resolve to their one present home on the unmodified tree (2972 passed at the gate) |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | n/a — no product symbol moved (test-only increment) | not fired |
| B2 file moved on disk | n/a | not fired |
| B3 byte-identical golden captures this source | the goldens capture `mapper/app.py` output — their reader is `tests/test_mod_parity.py` (new here) | reader is the new instrument itself |
| B4 artifact produced here is consumed elsewhere | `mod-bodies-baseline.json` / goldens / `at069-baseline.json` → read by `tests/test_mod_bodies.py`, `tests/test_mod_parity.py`, and the B12 compat tests | consumers in-tree |

| A3 | interface consumed by another module changed | n/a | not fired |

| Field | Value |
|---|---|
| **Reverse census** | 2 probes relevant (B3, B4), both resolved — the widened scan surface (17 source-reading files at P0, premise 3) is the increment's own subject, asserted by the generalised tests |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| path-pinned source reads that must generalise to the package | the source-reading test files of premise 3 | `grep -rln 'app\.py"\|app\.__file__\|inspect\.getsource' tests` (P0 premise 3) | 17 files, 6 in scope (the other 11 read `app.py` for other reasons) | 6 test files | none — the 2 new instruments cover the moved-construct oracles |
| AT-P04 composition rows for files not on disk | TARGET rows in the ARCHITECTURE composition table | the gate's 8 failures | 8 | 8 rows removed (20c0161) | none |

| Field | Value |
|---|---|
| **Correction population** | 2 corrections, each enumerated before its first site was edited (the 8 rows by the gate itself) |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| TARGET rows in the ARCHITECTURE composition table | 0 surviving owned-path arms | yes | inc0 gate: 8 failed → 20c0161 → a1 gate 2977 passed, exit=0 |

### Signed-balance test ledger

`post = base − deleted + added` → exact collected counts per layer are **not recorded**; the gate transcripts give the passed-count trajectory: P0 base 2941 passed / 3 xfailed (contract LLR-MOD.4.1) → inc0 gate 2972 passed / 8 failed (AT-P04 arms) → a1 gate 2977 passed / 0 failed (first gate on the fixed ARCHITECTURE).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | none separate — test-only increment, no product change (facts sheet, verbatim instruction: "none separate (test-only, no product change) — say so"). No reviewer ran and none is named here; the permanent mutation controls of §4 are the increment's executable review, and the batch's `code-reviewer` group reviews begin at A2–A4+B0, after Inc-0. Declared consequence: the flow's V36 grammar reads this cell as EMPTY, and this packet accepts that [x] rather than name a reviewer who did not run. |

---

## 5 · Risks

- The 8 gate failures were expected-by-design (TARGET rows ahead of code), but they teach that `test_repair_map_truth` is the guard against a lying map: any future increment that adds a map row before the file exists will see it at the gate.
- The parity goldens freeze today's behaviour including any latent defect in the scripted session; a deliberate behaviour change must re-capture with an amended requirement.
- The six generalised tests scan the package by content — a construct renamed in product code fails a pin loudly (intended), but a *new* accidental second home also fails loudly (AT-069 boundary).

## 6 · Pending items / spec deviations

- The gate's 8 failures were repaired by a docs commit (20c0161) inside the same increment, not by landing code early — no deviation.
- None open.

## 7 · Suggested next task

A1 (increment 002): shared helpers → `mapper/screens/common.py`, first product move of the spine.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 0 / 4 — test-only; contract forbids `mapper/**` edits at Inc-0 |
| 2 | Tests written in this same increment | all | ✓ | 8 test files in 90e731b (6 generalised + test_mod_bodies + test_mod_parity) |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | n/a — no unit meets the criterion; new instruments are white-box |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | §4 — tmp-copy arms inside the two new instruments + AT-069 duplicated/deleted pin |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | §4 — B3/B4 resolved; no product symbol touched |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b — none separate (test-only), per the facts sheet |
| 7 | No file from another lane touched | all | ✓ | one lane; Inc-0 sub-lanes held disjoint test files |
| 8 | Frozen interfaces untouched | all | ✓ | no product file edited |
| 9 | Coverage claims verified **on disk** | all | ✓ | gate transcript counts cited verbatim |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 — one-home / exactly-once absences |
| 11 | **Mutation verdicts** declared | all | ✓ | §4 — (a)(b)(c) KILLED; per-arm stored transcripts not recorded (arms are permanent) |
| 12 | **Instrument RED-proof** declared | all | ✓ | §4 — 3 instruments shown RED |
| 13 | **Correction population** declared | all | ✓ | §4 — 2 corrections, P0 census + gate enumeration |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4 — goldens + body baseline, sha256 on disk |
| 15 | **Independent review** names somebody | all | ⚠ | §4b — "none separate" per the facts sheet; V36 reads the cell as empty and this packet accepts that [x] rather than fabricate a reviewer |
| 16 | **Evidence files** declared | all | ✓ | §4 — 5 files, sha256 re-verified on disk |
