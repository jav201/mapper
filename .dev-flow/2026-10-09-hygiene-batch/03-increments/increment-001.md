# Increment 001 — HLR-001, HLR-002 · `declared draft-save members (B-103) and the HOME-1 kill (B-99)`

> **Artifact language:** English (`state.json` `language: en`).

> **Owed in.** `core` ✓ · `full` ✓

> **Where this lives:** the **repo**, next to the diff it describes —
> `.dev-flow/2026-10-09-hygiene-batch/03-increments/increment-001.md`. It is not synced to the vault.

| Field | Value |
|---|---|
| Batch | `2026-10-09-hygiene-batch` |
| Increment | `001` |
| Lane (if the batch forked) | n/a — one lane |
| Requirement(s) | `HLR-001 v1 / LLR-001.1, LLR-001.2` · `HLR-002 v1 / LLR-002.1` |
| Acceptance | `AT-060` · `AT-061` · `AT-062` · white-box `tests/test_draft_hygiene.py` (4 nodes) · unit none (no unit meets the layer-0 criterion) |
| Agent | product change + new test file: Kimi (`kimi-code/kimi-for-coding`, unit HYG1, isolated worktree); AT tags, mutation runs, nits, record: the orchestrator (Claude Opus 5.5) |
| Date | `2026-10-09` |

---

## 1 · What changed

**The failed-draft-save toast and the quit walk now read members that `MapScreen` declares. B-99 is confirmed paid on today's code.**

- `MapScreen` declares `_last_save_error: str | None = None`. `_save_draft` reads it directly, where it used to call `getattr(self, "_last_save_error", "")`.
- A new public method, `MapScreen.guard_open()`, reports whether a draft guard is up. `MapperApp.action_quit` calls it instead of reading the private `_draft_guard_open`.
- Nothing the user sees changes. The map screen's toast reads `could not save '<map>' (OSError) · draft kept · ctrl+s to retry`, exactly as before. The quit walk behaves as it did under `ctrl+q`, and so does the draft guard modal.
- **B-99:** the Inc-9h witness drives the home screen across two visits. It goes RED when `HOME-1` removes `HomeScreen.on_mount`'s hint refresh, and GREEN once that line is restored. The `INC9G-R8` debt was already paid by Inc-9h on 2026-10-01; what was left open was the record.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/app.py` | source | HLR-001, LLR-001.1, LLR-001.2 | declared slot in `MapScreen.__init__`; direct read in `_save_draft`; new `guard_open()` after `has_pending_draft`; `action_quit` calls it; one comment at `_save_or_toast`'s write |
| `tests/test_draft_hygiene.py` | test | LLR-001.1, LLR-001.2 | new: 2 behaviour nodes (real app, real keys) + 2 AST nodes over the `mapper/` package |
| `tests/test_draft_save.py` | test | HLR-001 | docstring tag `AT-060` on `test_llr_004_2_a_save_failure_names_ctrl_s_to_retry` |
| `tests/test_draft_exits.py` | test | HLR-001 | docstring tag `AT-061` on `test_pdr_c1_quit_while_a_node_guard_is_open_does_not_wedge` |
| `tests/test_inc9h.py` | test | HLR-002, LLR-002.1 | docstring tag `AT-062` on `test_inc9h_cr_f2_the_home_hint_follows_the_maps_when_the_screen_resumes` |

| Count | Value |
|---|---|
| **SOURCE files** | **1 / 4** |
| Test files | 4 (uncapped) |
| Doc files | 0 (outside the count; `.dev-flow/**` records only) |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_draft_hygiene.py tests/test_draft_save.py tests/test_draft_exits.py tests/test_inspector.py tests/test_g6_store_surrogates.py tests/test_inc9h.py tests/test_no_operator_paths.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | none — `guard_open()` is a one-line read, so no unit meets the criterion | n/a |
| **A · white-box** ↔ LLR | `core` · `full` | `tests/test_draft_hygiene.py` (4 nodes: LLR-001.1 ×2, LLR-001.2 ×2) | 4 passed |
| **B · black-box** `AT-NNN` ↔ story | `core` · `full` | AT-060, AT-061, AT-062 | 3 passed |
| Regression set (orchestrator, main checkout, after the nits were folded) | — | the command in §3 | **187 passed, 2 deselected, 0 failed** (`evidence/inc001-regression-set.transcript`) |

A note on the worker's run. Kimi's own regression run reported `3 failed` in `test_c6_a_hidden_card_hands_the_draft_to_the_hint_line_in_alert[87|118|140]` and called them "pre-existing on HEAD". **The orchestrator could not reproduce that.**
- The same nodes passed 3/3 in the main checkout at HEAD, and 3/3 in the worker's tree with the change.
- The whole regression set then passed with nothing else running: 185 passed, 0 failed, in the worktree.
- The worker's failures coincided with the orchestrator's concurrent B-99 mutation run on the same machine. This is recorded as load-induced timing, and not as a defect in HEAD. The worker's report is kept verbatim in `evidence/inc001-kimi-unit-report.transcript`.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | `mapper/app.py` replaced by `git show HEAD:mapper/app.py` (the base) |
| Instrument | `hyg1_mutate.py` (orchestrator script, session scratch); restore checked by sha256 |
| Where it ran | worktree `unit/hyg1` (the battery), then the main checkout after the nits (re-run) |
| Transcript | `evidence/inc001-mutation-battery.transcript` (section "RED counterfactual"), `evidence/inc001-red-after-nits.transcript` |
| Restore proven by | sha256 equal before and after. The battery: equal, `True`. After the nits: `4b47adcf…c89978` = `4b47adcf…c89978` |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1`, `python -B` |
| Arms resolved at baseline | 4 (asserted: 4 FAILED lines named) |
| Verdict granularity | per node id (4 `FAILED` lines) |
| Arms that stayed GREEN | none |

| Field | Value |
|---|---|
| **RED counterfactual** | `mapper/app.py` set to its base bytes (`git show HEAD:mapper/app.py`, whole-file revert of this increment's change) → all 4 new nodes of `tests/test_draft_hygiene.py` FAILED · transcripts `.dev-flow/2026-10-09-hygiene-batch/evidence/inc001-mutation-battery.transcript` and `inc001-red-after-nits.transcript` · restore digest `4b47adcf1c5d5629f8749dffb225d395e0193a09762f3c3712c135760cc89978` (post-nit file) |

| Field | Value |
|---|---|
| **Mutation verdicts** | Battery run on the pre-nit increment file. The mutated lines are unchanged by the nits; only the `guard_open` docstring moved. Each mutant was restored byte-identical. Transcript `.dev-flow/2026-10-09-hygiene-batch/evidence/inc001-mutation-battery.transcript`. Results: **M1** `_save_draft`: `darkside.plain(self._last_save_error or "error")` → `darkside.plain("error")`, KILLED by `AT-060` (the toast assertion reads `(error)`). **M2** `action_quit`: `if screen.guard_open():` → `if False:`, KILLED by `AT-061` (`assert _guards(app) == 1` → `0 == 1`: the walk wedges, as LED .1 states). **M3** `guard_open`: `return self._draft_guard_open` → `return False`, KILLED by `AT-061` and by `test_llr_001_2_guard_open_follows_the_guard`. **HOME-1** `HomeScreen.on_mount`: the hint-refresh line removed, KILLED by `AT-062` (`'↵ open map' not in …` fails), restore sha256 `873832e9…90cb` equal, transcript `.dev-flow/2026-10-09-hygiene-batch/evidence/b99-home1-mutation.transcript`. Arms that stayed GREEN: none. |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_draft_hygiene.py` (AST + behaviour) | the base `app.py` (no declaration, `getattr` read, private cross-class read, no `guard_open`) | `4 failed in 1.27s`, 4 FAILED lines (`inc001-red-after-nits.transcript`) |
| `hyg1_mutate.py` / `b99_mutate.py` | each mutant's anchor is asserted to occur exactly once before it is applied | `target occurrences: 1` printed per mutant; the first B-99 attempt failed loudly (`occurrences: 0`, CRLF), so a mis-anchored mutant aborts and does not pass silently |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 2 instruments, each shown RED before its first PASS was believed (see the table above) |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the failed-save toast | `AT-060`: `messages[-1] == f"could not save {map_id!r} (OSError) · draft kept · ctrl+s to retry"` on the captured notification | passed; under M1 it failed (`(error)`) |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 1 artifact (the toast text), asserted against the notification as emitted |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| b99-home1-mutation.transcript | .dev-flow/2026-10-09-hygiene-batch/evidence/b99-home1-mutation.transcript | 70d9a66b1b8db0265ea7366958bae959385a4f3057c2dcd49bdd1c2c522b8e3a |
| inc001-mutation-battery.transcript | .dev-flow/2026-10-09-hygiene-batch/evidence/inc001-mutation-battery.transcript | e876a58252b3a6c1bc338a49ec99edf3866e0dfce40b50ed51542ca948446793 |
| inc001-red-after-nits.transcript | .dev-flow/2026-10-09-hygiene-batch/evidence/inc001-red-after-nits.transcript | 9f753421ff4f5fa001570f0b540127e431d8b75818b59ba1851b2a7326fe4b9d |
| inc001-kimi-unit-report.transcript | .dev-flow/2026-10-09-hygiene-batch/evidence/inc001-kimi-unit-report.transcript | 1fe1e991322ca7059dd566d4657dcbc9276129d30c797deda84cddb52be8e2c4 |
| inc001-regression-set.transcript | .dev-flow/2026-10-09-hygiene-batch/evidence/inc001-regression-set.transcript | 0759cb9664e135b3345662c47434203b8f054f1621fe0c37850843b8dcf9a19d |

| Field | Value |
|---|---|
| **Evidence files** | 5 artifacts, each at the declared home and cited with the digest of its stored bytes (`devflow-evidence.py --root .`) |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes: "no read of `_draft_guard_open` outside `MapScreen`" and "no `getattr` read of `_last_save_error`" |
| If the result is an ABSENCE, what made the search wide enough | the AST walk covers every `.py` under the `mapper` package, not only `app.py` |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_llr_001_2_no_read_of_the_guard_flag_outside_map_screen`, `test_llr_001_1_last_save_error_is_declared_and_never_read_through_getattr` (their docstrings say so, and the latter names its `vars()`/`__dict__` blind spot) |
| Conjunctive criteria: one mutation per conjunct | LLR-001.2 has two conjuncts: no outside read, and `action_quit` calls `guard_open`. The base file violates both, and the 4-node RED shows each node failing. A separate mutant per conjunct was not run for the AST node. |
| Synthetic instance of the absent case | the base `app.py` itself (holds `screen._draft_guard_open` at `:5217` and the `getattr` read at `:3565`) |
| **Positive control for every probe that returned an ABSENCE** | on the base file, the same unmodified AST probes reported the present cases (`FAILED … no_read_of_the_guard_flag_outside_map_screen`, `FAILED … never_read_through_getattr`) |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rn "_draft_guard_open\|_last_save_error\|guard_open" tests --include=*.py` | only `tests/test_draft_hygiene.py` (this increment). `_save_or_toast` is parsed by `tests/test_g6_store_surrogates.py`; its signature and call sites are unchanged, and that file passed in the regression set |
| B2 file moved on disk | none moved | n/a — not fired |
| B3 byte-identical golden captures this source | `find tests -type d -iname "*golden*"` | no golden directory — not fired |
| B4 artifact produced here is consumed elsewhere | none produced | not fired |

| A3 | interface consumed by another module changed | `grep -rn "guard_open\|_draft_guard_open" mapper --include=*.py` | `mapper/app.py` only — not fired |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1 · B2 · B3 · B4 · A3). B1 found 1 shared surface (`test_g6_store_surrogates.py` parses `_save_or_toast`), and it was re-validated green in the regression set. The other four did not fire, each with its probe above. |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| reads of `MapScreen`'s private guard flag from outside the class | every attribute read of `_draft_guard_open` outside `MapScreen` | `grep -rn "_draft_guard_open" mapper --include=*.py` (P0 premise 2, before the change) | 1 | `app.py:5217` | none |
| `getattr` reads of the error slot | every `getattr(..., "_last_save_error", …)` | `grep -rn "_last_save_error" mapper` (P0 premise 1) | 1 | `app.py:3565` | none |

| Field | Value |
|---|---|
| **Correction population** | 2 corrections, each enumerated by grep at P0 (`01-requirements.md` §2.7) before the first site was edited |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| `screen._draft_guard_open` outside `MapScreen` | 0 hits | yes | AST node green |
| `getattr(self, "_last_save_error"` | 0 hits | yes | AST node green |

### Signed-balance test ledger

`post = base − deleted + added` → `2927 = 2923 − 0 + 4`  ✓ reconciles (collected, `pytest --collect-only -q`: `2927/2951 tests collected (24 deselected)`; base 2923 is the data-safety close count)

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, independent of the author Kimi) · APPROVE-WITH-NITS, 0 HIGH / 0 MED / 3 LOW · all three folded into this increment: **CR-1** the AT tags became their own docstring paragraph; **CR-2** the `guard_open` docstring was split into a summary plus a B-103 line; **CR-3** the AST visitor was hoisted out of the loop, with `enclosing` per file. The RED counterfactual was re-run after the nits (`inc001-red-after-nits.transcript`). |

---

## 5 · Risks

- The AST guards do not see a read through `vars()`/`__dict__` or a `getattr(screen, "_draft_guard_open")`. This is stated in the test docstrings. The behaviour nodes (AT-061, `guard_open_follows_the_guard`) still catch a broken walk.
- `_save_or_toast` still writes the slot on non-`MapScreen` screens (`factory.py:219`, `app.py:1169`). The write is unread there, and a comment says so (LED .2).
- `ruff check mapper/app.py` reports `F401 re imported but unused` at `app.py:7`. **That is pre-existing on master**: the diff does not touch imports, so it is left alone (surgical).

## 6 · Pending items / spec deviations

- `test_c6_a_hidden_card_hands_the_draft_to_the_hint_line_in_alert` failed under machine load in the worker's run, and passed alone and in the regression set. This is a watch item and not a backlog row, because it was not reproduced. If it fails at the P4 full run, it becomes a FLAKE row.
- The pre-existing `F401` at `app.py:7` → backlog candidate at close (B-103-adjacent hygiene).

## 7 · Suggested next task

P4: the full suite, then the core close (backlog B-99 and B-103 marked DONE).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 1 / 4 (§2) |
| 2 | Tests written in this same increment | all | ✓ | `tests/test_draft_hygiene.py` (4 nodes) |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | n/a: no unit at cyclomatic ≥3 or crossing a module boundary |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | §4 RED counterfactual (4/4 FAILED on base, digest restored) |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | §4 Reverse census (5 probes) |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b APPROVE-WITH-NITS, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | one lane |
| 8 | Frozen interfaces untouched | all | ✓ | none frozen; `_save_or_toast`'s signature unchanged |
| 9 | Coverage claims verified **on disk** | all | ✓ | 187 passed in the main checkout (§4); 2927 collected |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 Load-bearing emptiness |
| 11 | **Mutation verdicts** declared | all | ✓ | M1, M2, M3, HOME-1 all KILLED, per node |
| 12 | **Instrument RED-proof** declared | all | ✓ | 2 instruments |
| 13 | **Correction population** declared | all | ✓ | 2 corrections, P0 greps |
| 14 | **Emitted-form assertion** declared | all | ✓ | the toast text (AT-060) |
| 15 | **Independent review** names somebody | all | ✓ | `code-reviewer` (§4b) |
| 16 | **Evidence files** declared | all | ✓ | 5 files with sha256 |
