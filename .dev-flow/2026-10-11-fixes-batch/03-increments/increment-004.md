# Increment 004 — US-FX-005 / US-FX-006 · Test-only guards for B-110 and B-113

| Field | Value |
|---|---|
| Batch | `2026-10-11-fixes-batch` |
| Increment | `004` |
| Lane (if the batch forked) | none — one lane |
| Requirement(s) | `HLR-FX.5`, `HLR-FX.6` · `LLR-FX.5.1`, `LLR-FX.6.1` |
| Acceptance | `AT-088` · `AT-089` |
| Agent | `software-dev` |
| Date | `2026-10-11` |

---

## 1 · What changed

Two test-only guards, 0 source files. `AT-088` spies on
`mapper.screens.map.exporting.pan_extent` (the export concern's own module-global reader)
while a real layered export runs, asserting both the artifact and a non-zero read count —
so a re-bind of `exporting.py` to `layered.pan_extent` turns the node RED. `AT-089` retypes
`LEAK_EXCEPTIONS` in `tests/test_inc9c.py` from `(file, expr)` to `(file, lineno, expr)`,
updates both consumers (the undeclared-leak census and the stale-exception check) to compare
the full record, and adds a negative control proving a second `str(exc)` site in an excused
file is still reported.

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `tests/test_export_state.py` | test | HLR-FX.5 · LLR-FX.5.1 · AT-088 | Added `test_exporting_reads_pan_extent_through_its_own_module_global` (async spy, delegates to the real reader, `raising=False` install). |
| `tests/test_inc9c.py` | test | HLR-FX.6 · LLR-FX.6.1 · AT-089 | `LEAK_EXCEPTIONS` retyped `(file, lineno, expr)` at `home.py:175`, `screens/map/screen.py:214`, `common.py:213`; `_undeclared` helper + census consumer compare the full record; stale consumer compares `(p, n, e)`; added `test_at_089_a_second_leak_site_in_an_excused_file_is_still_flagged`. |
| `.dev-flow/2026-10-11-fixes-batch/evidence/inc004-red.transcript` | doc | — | RED-proof transcript (M-FX15, M-FX16) with restore digests. |

| Count | Value |
|---|---|
| **SOURCE files** | **0 / 4** |
| Test files | 2 (uncapped) |
| Doc files | 1 (outside the count) |

## 3 · How to test

```bash
env -u NO_COLOR -u TERM python -B -m pytest -q -p no:cacheprovider tests/test_export_state.py tests/test_inc9c.py tests/test_en8.py
ruff check tests/test_export_state.py tests/test_inc9c.py
```

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **B · black-box** `AT-088` / `AT-089` | `core` · `full` | `tests/test_export_state.py::test_exporting_reads_pan_extent_through_its_own_module_global` · `tests/test_inc9c.py::test_at_089_a_second_leak_site_in_an_excused_file_is_still_flagged` | 2 passed |
| **A · white-box** `sec_f1` census + stale | `core` · `full` | `tests/test_inc9c.py -k "sec_f1 or at_089"` | 14 passed |

### GREEN line (full verification)

```
env -u NO_COLOR -u TERM python -B -m pytest -q -p no:cacheprovider tests/test_export_state.py tests/test_inc9c.py tests/test_en8.py
101 passed
```

### RED table (per mutant, with restore digests)

| Mutant | Mutation applied | Node made RED | Restore digest (sha256) | Restored = pre-mutation |
|---|---|---|---|---|
| M-FX15 | `exporting.py` reads `layered.pan_extent` (import + call site) | `tests/test_export_state.py::test_exporting_reads_pan_extent_through_its_own_module_global` — spy count 0, `AssertionError` | `mapper/screens/map/exporting.py` → `a0e7ccf6987237355921751ece7407ff7882b189297a9113f73de982317ebd93` | yes (byte-identical) |
| M-FX16 | census comparison keyed `(file, expr)` again (`_undeclared`) | `tests/test_inc9c.py::test_at_089_a_second_leak_site_in_an_excused_file_is_still_flagged` — second site absorbed, `AssertionError` | `tests/test_inc9c.py` → `c539e5d1339f9a07f819f53a27d8acabff309ad8df7d5e501c708eef04b4b366` | yes (byte-identical) |

### Evidence files

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| inc004 RED transcript | `.dev-flow/2026-10-11-fixes-batch/evidence/inc004-red.transcript` | `5414cc6a2d036391c45374ab0cb87dc559035b35ba456977df65fe2273e857c6` |

### Instrument RED-proof

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `test_exporting_reads_pan_extent_through_its_own_module_global` | M-FX15 (re-bind to `layered.pan_extent`) | `AssertionError: the export never read the pan extent through mapper.screens.map.exporting.pan_extent … assert []` |
| `test_at_089_a_second_leak_site_in_an_excused_file_is_still_flagged` | M-FX16 (census keyed `(file, expr)`) | `AssertionError: … Left contains one more item: ('mapper/screens/home.py', 412, 'str(exc)')` |

### Mutation verdicts

- M-FX15 → `test_exporting_reads_pan_extent_through_its_own_module_global`: KILLED (spy count 0, the exact assertion fails; artifact still written — the positive control confirms the zero count is the discriminating signal, not a crash).
- M-FX16 → `test_at_089_a_second_leak_site_in_an_excused_file_is_still_flagged`: KILLED (the second `str(exc)` record is absorbed; the `undeclared == [second]` assertion fails).

## 4b · Independent review

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet) — APPROVE-WITH-NITS, 0 HIGH; both LOW nits fixed in the follow-up commit (actionable stale-key message; AT-089 picks any declared carry) — 59 passed in `tests/test_inc9c.py` after the fix |

## 5 · Risks

- The leak key is now line-sensitive: moving any of the three excused `notify` calls
  (`home.py:175`, `screens/map/screen.py:214`, `common.py:213`) reddens
  `test_inc9c_sec_f1_every_leak_exception_is_still_real` — accepted, fail-loud by design
  (declared in LLR-FX.6.1).

## 6 · Pending items / spec deviations

- None. `BACKLOG.md` B-113 points at `tests/test_inc9q.py`; the registry lives in
  `tests/test_inc9c.py` (correction noted in the ledger, LED-2026-10-11-fixes-batch.13).

## 7 · Suggested next task

Batch close: run the increment gates and the full single-file suite sweep, then the close
checklist (`05-close.md`).
