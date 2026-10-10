# Increment 010 — A4 · LLR-MOD.1.1, LLR-MOD.3.2 · `HomeScreen moved to mapper/screens/home.py; preview_csv follows its reader; spine A complete`

> **Artifact language:** English.

> **Owed in.** `core` ✓ · `full` ✓

> **Where this lives:** the repo, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-010.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `010` (A4) |
| Lane (if the batch forked) | n/a — serial spine, no lane |
| Requirement(s) | `LLR-MOD.1.1 v1` · `LLR-MOD.3.1` · `LLR-MOD.3.2 v1` · `HLR-MOD.1, 3, 4` |
| Acceptance | `AT-065` (painted parity) · `LLR-MOD.4.1` (full suite at the gate) · `LLR-MOD.4.3` (`tests/test_mod_bodies.py`) · `LLR-MOD.3.2` bite: the repointed `preview_csv` patch sites in `tests/test_inc9c.py` / `tests/test_inc9n.py` |
| Agent | Product move by a **Kimi (`kimi-for-coding`) unit** in an isolated worktree, with its own RED + sha256 restore in its own log (session scratch — not committed, see §6). Gate follow-up `689d537` (test_inc9m third caller, store.py symbol citation, transcript) and the gate run by the **orchestrator**. |
| Date | `2026-10-09/10` (commits dated 2026-10-10) |

---

## 1 · What changed

**`HomeScreen` now lives in `mapper/screens/home.py` (533 lines); `mapper/app.py` shed 516 lines and stands at 307 — spine A is complete: every sibling screen is out of the monolith.**

- `HomeScreen` cut whole from `app.py` into `mapper/screens/home.py`; `mapper/app.py` keeps the re-export (LLR-MOD.1.1/LLR-MOD.3.1). Verified on disk: `git show 45007da:mapper/app.py | wc -l` → **307**.
- **Patch repoint (LLR-MOD.3.2, PDR C1):** the two `preview_csv` patch sites — `tests/test_inc9c.py:114` and `tests/test_inc9n.py:285` — are retargeted from `mapper.app` to `screens/home.py`'s module-global: the reader is `HomeScreen` (it read the name at the old `app.py:1090`), **not** `_ImportPreviewScreen`.
- `home.py` imports `MapScreen` from `mapper.screens.map` (it constructs one at five sites) — never from `mapper.app` (LLR-MOD.1.1/LLR-MOD.6.2, the MOD-REQ2 reorder's whole point).
- Gate follow-up `689d537`: `test_inc9m.py`'s third `safe_local_path` caller is `screens/home.py` (was `app.py`); a `store.py` comment citing `app.py:548` now cites by symbol; the gate transcript recorded.
- `docs/ARCHITECTURE.md` records spine A complete.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/app.py` | source | LLR-MOD.1.1, LLR-MOD.3.1 | HomeScreen body deleted (−516 lines) → 307 lines; re-export kept |
| `mapper/screens/home.py` | source | LLR-MOD.1.1, LLR-MOD.3.2 | new — HomeScreen whole (533 lines) + module-level `preview_csv` binding |
| `mapper/store.py` | source | LLR-MOD.5.2 | 2 comment lines: citation by symbol, not `app.py:548` (`689d537`) |
| `docs/ARCHITECTURE.md` | doc | | TARGET rows amended; spine A recorded complete |
| `tests/test_inc9c.py` | test | LLR-MOD.3.2 | `preview_csv` patch site repointed (`:114`) + source-set lines |
| `tests/test_inc9n.py` | test | LLR-MOD.3.2, LLR-MOD.5.2 | `preview_csv` patch site repointed (`:285`) + package scan (`45007da`) |
| `tests/test_app_imports_used.py` | test | LLR-MOD.5.2 | source set follows the package |
| `tests/test_arch_osopen_callers.py` | test | LLR-MOD.5.2 | launcher-set line follows the move |
| `tests/test_inc9m.py` | test | LLR-MOD.5.2 | third `safe_local_path` caller = `screens/home.py` (`689d537`) |
| `evidence/a6a7a4-gate-full-suite.transcript` | generated | LLR-MOD.4.1 | the gate transcript, recorded (`689d537`) |

| Count | Value |
|---|---|
| **SOURCE files** | **3 / 4** |
| Test files | 5 (uncapped) |
| Doc files | 1 (`docs/ARCHITECTURE.md`, outside the count) |
| Generated | 1 (gate transcript) |

- ✓ Under the cap: `app.py` + the new module are the move; `store.py` is the gate-mandated citation repair.

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider            # the orchestrator's gate command (verbatim from the transcript)
python -B -m pytest -q -p no:cacheprovider tests/test_inc9m.py tests/test_repair_artifact_claims.py   # the two failing files, post-fix
python -B -m pytest -q -p no:cacheprovider tests/test_inc9c.py tests/test_inc9n.py   # the repointed preview_csv patch sites must still bite
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** (LLR-MOD.4.3 bodies oracle) | `core` · `full` | `tests/test_mod_bodies.py` | passed within the gate run (HomeScreen's methods exactly once, `ast.dump`-equal to baseline) |
| **A · white-box** ↔ LLR | `core` · `full` | `test_inc9m`, `test_repair_artifact_claims[store.py]`, `test_inc9c`, `test_inc9n` | RED at the gate (2 failures, both this increment's); after `689d537`: **re-run of the two files green** (transcript header) |
| **B · black-box** AT-065 ↔ painted screen | `core` · `full` | `tests/test_mod_parity.py` (widths 118/87) | 0 painted-line diffs within the gate run |

Gate (`a6a7a4-gate-full-suite.transcript`, run at `45007da`): **`2 failed, 3018 passed, 24 deselected, 3 xfailed in 1567.24s (0:26:07)`** — cited verbatim, including the failures, **both this increment's**:

- `FAILED tests/test_inc9m.py::test_inc9m_s1_one_helper_is_imported_by_the_three_callers` — named `app.py` as the third `safe_local_path` caller; it is now `screens/home.py`.
- `FAILED tests/test_repair_artifact_claims.py::test_every_path_line_citation_resolves[store.py]` — a `store.py` comment cited `app.py:548`.

Transcript header: "2 failures, both pointing at moved code: test_inc9m named app.py as the third safe_local_path caller (now screens/home.py); a store.py comment cited app.py:548. Fixed in the next commit; re-run of the two files green." Both fixes are in `689d537`, part of this increment.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | none committed unique to this increment — a pure move plus two patch repoints; the Kimi unit's own RED + sha256 restore lives in its session log (§6); the permanent controls below ran inside the gate |
| Instrument | in-force permanent RED controls: `tests/test_mod_bodies.py` (one-token body mutation / deleted import on a tmp copy → RED) and `tests/test_mod_parity.py` (painted-string mutant → RED); the bite of the repointed `preview_csv` sites is `test_inc9c.py`/`test_inc9n.py` themselves |
| Where it ran | the Kimi unit's isolated worktree (unit-level); the orchestrator's gate environment (suite) |
| Transcript | `a6a7a4-gate-full-suite.transcript` (suite); the unit-level RED transcript is not committed — not recorded here. No A1-style explicit repoint transcript exists for the preview_csv repoint — not recorded. |
| Restore proven by | the unit's sha256 restore check (its own log); tmp-copy mutants for the permanent controls |
| Bytecode cache | `python -B`, `-p no:cacheprovider` (gate command verbatim) |
| Arms resolved at baseline | not recorded per arm for this gate |
| Verdict granularity | suite pass/fail per node (2 FAILED node ids named above) |
| Arms that stayed GREEN | not recorded |

| Field | Value |
|---|---|
| **RED counterfactual** | none separate committed beyond the in-force permanent controls — the two gate FAILED nodes (named above) are this increment's own honest RED evidence: both pinned moved code and both were fixed within the increment (`689d537`). |

| Field | Value |
|---|---|
| **Mutation verdicts** | No separate mutation battery. In force at this gate: `test_mod_bodies.py` + `test_mod_parity.py`, both GREEN on the shipped tree. Not yet in force: `test_mod_dispatch.py` (B1), `test_mod_compat.py` patch-guard + `test_mod_deps.py` + `test_mod_structure.py` (B12). Per-arm granularity beyond suite pass/fail: not recorded. |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_inc9m.py` | third caller moved from `app.py` to `screens/home.py` | `FAILED …test_inc9m_s1_one_helper_is_imported_by_the_three_callers` at this gate |
| `tests/test_repair_artifact_claims.py` | `store.py` comment citing stale `app.py:548` | `FAILED …[store.py]` at this gate |
| `tests/test_mod_bodies.py` | (tmp-copy) one-token body mutation / deleted import | RED per its Inc-0 negative controls — proven before this increment, GREEN here |
| `tests/test_mod_parity.py` | (tmp-copy) painted-string mutant | RED per LLR-MOD.4.2's negative control — proven before this increment, 0 diffs here |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 instruments — two printed FAILURE at this very gate, the two permanent oracles were proven RED earlier |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| `mapper/screens/home.py` + pruned `mapper/app.py` (on-disk AST) | `tests/test_mod_bodies.py` — per-method `ast.dump` against the Inc-0 baseline, exactly-once across the package | passed (within the 3018) |
| the pruned `mapper/app.py` line count | `git show 45007da:mapper/app.py \| wc -l` | **307** — matches the facts sheet ("app.py 307 lines") |
| the repointed patch surface | `test_inc9c.py` / `test_inc9n.py` read `preview_csv` from `screens/home.py`'s module-global and observe the patched value | passed within the gate run |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 3 artifacts (moved AST, pruned app.py, repointed patch surface), asserted on disk |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| a6a7a4-gate-full-suite.transcript | .dev-flow/2026-10-09-modular-batch/evidence/a6a7a4-gate-full-suite.transcript | 94ac4057a8e042076a939e885522e4e6d8f0dedf3d72e24ec11f79f5820068ec |

| Field | Value |
|---|---|
| **Evidence files** | 1 artifact (shared with increments 008 and 009), cited with the digest of its stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes: "no census method lost or duplicated" (bodies oracle); "no `Screen` subclass left in `app.py` other than `MapperApp`" — the dedicated `-k b0` structure node lands at B12 (⚠); "nothing under `screens/` imports patch names from `mapper.app`" — AST-enforced at B12 (⚠) |
| If the result is an ABSENCE, what made the search wide enough | every `*.py` under the package root (oracle); `grep -rn "from mapper.app import" mapper/screens/` (import ban) |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `tests/test_mod_bodies.py` docstring (exactly-once conclusion) |
| Conjunctive criteria: one mutation per conjunct | body mutation and lost-import arms are separate (LLR-MOD.4.3); the B12 structure/deps guards add one synthetic arm per banned shape |
| Synthetic instance of the absent case | the oracle's tmp-copy mutants; the B12 guards' synthetic arms |
| **Positive control for every probe that returned an ABSENCE** | the 2 gate FAILED nodes — the same unmodified probes reported the present (stale) cases |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rl "from mapper.app import" tests` (premise 2: 68 files) | all still resolve via the re-export — 3018 passed includes every importer |
| B2 file moved on disk | readers of HomeScreen / the `preview_csv` name at the old `app.py` path | **fired**: `test_inc9m` (third caller), `store.py` citation — both fixed in `689d537`; the two `preview_csv` patch sites followed the reader (`45007da`) |
| B3 byte-identical golden captures this source | `grep mapper/app.py tests/goldens/**` | no golden captures source bytes — not fired |
| B4 artifact produced here is consumed elsewhere | `grep -rn "preview_csv\|HomeScreen" mapper tests` | `HomeScreen` consumed via `mapper/app.py` re-export (`screens/factory.py`); `preview_csv` read at `screens/home.py` — its two patch sites bite |

| A3 | interface consumed by another module changed | the `preview_csv` patch surface moved from `mapper.app` to `screens/home.py` | `test_inc9c.py` / `test_inc9n.py` green at the gate through the repointed module-global |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run: B2 and A3 fired (all repaired in-increment), B1/B4 re-validated, B3 not fired |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| `preview_csv` patch sites must target the name's reader | the 8 patch targets of premise 4 | premise 4's full census over every patch form in `tests/` (P0, before any move) | 7 module-global names / 16 sites total | this increment: `preview_csv` ×2 (`test_inc9c.py:114`, `test_inc9n.py:285`) → `screens/home.py` | none — this was the last outstanding module-global repoint (refusal_sentence A1, MAX_RENDER_NODES/save_svg/pan_extent/SearchIndex B0, LayeredRenderer A7); `GitHubConnector.fetch` needs none (class patch, ARCH-11) |
| pins citing moved home-screen code | every test/comment naming `app.py` callers or lines | premise 3's census + the gate's FAILED lines | the 2 that fired | `test_inc9m.py`, `store.py` (`689d537`) | rest already generalised |

| Field | Value |
|---|---|
| **Correction population** | 2 corrections, each enumerated before the first site was edited (premise 4 at P0; the gate re-enumerated the second) |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| `preview_csv` / third caller / `app.py:548` read through `mapper.app` | 2 stranded refs at the gate | yes — 0 surviving stale refs after `45007da` + `689d537`; re-run of the two files green | gate transcript FAILED lines; `689d537` diff |

### Signed-balance test ledger

`post = base − deleted + added` → per-increment **collected** counts are not recorded (gate transcripts record passed/failed). Executed progression: 3003 passed / 2 failed (A5b gate) → **3018 passed / 2 failed** (this gate, spine A complete) → 3034 (B1+B2 gate). ⚠ not recorded where the ledger's exact terms are unavailable.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, read-only) · group review **A2–A4+B0** · **APPROVE-WITH-NITS, 0 HIGH** · every moved class/function of the pre-batch `app.py` (33 names) byte-identical (AST) in its new module; re-exports complete; **every patch repointed to its reader** (this increment's `preview_csv` repoint included); no back-edges/cycles. 3 MED (vacuous census scans) → repaired post-review (unit MODREV); 1 LOW carried. |

---

## 5 · Risks

- With spine A complete, `app.py` (307 lines) holds only `MapperApp` + re-exports — but the **dedicated structure guard (`-k spine_a` / AT-068) lands at B12**; until then the "every sibling screen owns its names" claim rests on the suite, the bodies oracle and the review.
- The two gate failures were the same path/citation rot class as A5b's — caught by the gate, fixed in-increment; the residual risk is rot in something no gate reads (mitigated mechanically at B12 by the census re-run, LLR-MOD.7.2).

## 6 · Pending items / spec deviations

- The Kimi unit's own RED + sha256 restore log is session scratch, not committed — its content is not recorded here (only its existence, per the facts sheet).
- None else open.

## 7 · Suggested next task

B1: the hints concern moves to the `HintsOps` mixin — the Spine B spike with the dispatch guards (`test_mod_dispatch.py`, LLR-MOD.2.1–2.3) and the AT-066 pilot.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 3 / 4 — app.py + home.py are the move; store.py is the gate-mandated citation repair |
| 2 | Tests written in this same increment | all | ✓ | patch repoints + census follow-ups in `45007da`; `test_inc9m` fix in `689d537` |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `tests/test_mod_bodies.py` passed in the gate |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | §4 — in-force permanent controls + the gate's own 2 FAILED nodes |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | §4 — 5 probes; B2 and A3 fired and repaired |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b — group review A2–A4+B0, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | serial spine, one lane |
| 8 | Frozen interfaces untouched (or returned to the trunk) | all | ✓ | patch surface repointed per PDR C1, not redesigned |
| 9 | Coverage claims verified **on disk** | all | ✓ | gate on the shipped tree: 3018 passed / 2 failed, cited verbatim; app.py = 307 lines verified |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 — incl. the ⚠ on B12-deferred guards |
| 11 | **Mutation verdicts** declared | all | ✓ | §4 — bodies + parity in force; later arms named as not-yet |
| 12 | **Instrument RED-proof** declared | all | ✓ | §4 — 4 instruments, 2 printed FAILURE at this gate |
| 13 | **Correction population** declared | all | ✓ | §4 — premise-4 census (P0); the preview_csv repoint completes the module-global set |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4 — moved AST, 307-line app.py, repointed patch surface |
| 15 | **Independent review** names somebody | all | ✓ | §4b — `code-reviewer` (Claude Sonnet) |
| 16 | **Evidence files** declared | all | ✓ | §4 — 1 file with sha256 |
