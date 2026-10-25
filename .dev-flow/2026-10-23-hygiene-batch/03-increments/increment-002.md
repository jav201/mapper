# Increment 002 — US-Q1-001 · `Colour always on — NO_COLOR neutralised in MapperApp.__init__ (lane L1)`

> **Artifact language.** Canonical **English scaffold**; generated in the batch's language.
> **Owed in.** `core` ✓ · `full` ✓ · **packet home:** `.dev-flow/2026-10-23-hygiene-batch/03-increments/increment-002.md` (repo, next to the diff it describes)

| Field | Value |
|---|---|
| Batch | `2026-10-23-hygiene-batch` |
| Increment | `002` |
| Lane (if the batch forked) | `L1 · app` |
| Requirement(s) | `US-Q1-001 · HLR-Q1.1 · LLR-Q1.1.1 (mechanism decided by ruling R3, ledger .3; no --no-color per operator ruling Q5)` |
| Acceptance | `AT-108` · unit layer-0 = `tests/test_colour_always_on.py::test_no_color_removed_before_super` · black-box = `tests/test_colour_always_on.py::test_painted_screen_byte_identical_with_and_without_no_color` |
| Agent | `software-dev` (Phase-3 lane worker, lane L1) |
| Date | `2026-10-23` |

---

## 1 · What changed

BLUF: mapper renders in colour ALWAYS. `MapperApp.__init__` now pops `NO_COLOR` from the
process environment **before** `super().__init__()` runs, so Textual's base constructor never
sees the variable and no `Monochrome` line filter can be installed. The constructor is the one
path shared by the CLI and every test, which is exactly why ruling R3 chose it over `main()`.
No `--no-color` opt-out was added (operator ruling Q5). The change is two lines: an `import os`
and the `os.environ.pop("NO_COLOR", None)` with a short comment in the file's existing comment
style — the constructor signature and every other behaviour of `mapper/app.py` are untouched.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/app.py` | source | LLR-Q1.1.1 (HLR-Q1.1) | `import os`; `os.environ.pop("NO_COLOR", None)` as the first statement of `MapperApp.__init__`, before `super().__init__()` (app.py:250-254) |
| `tests/test_colour_always_on.py` | test | LLR-Q1.1.1, HLR-Q1.1 (AT-108 arm) | NEW — `test_no_color_removed_before_super` (layer 0: variable gone from `os.environ`, no `Monochrome` in `app._filters` after construction with `NO_COLOR=1`) and `test_painted_screen_byte_identical_with_and_without_no_color` (AT-108: the composited frame serialized as (text, style) runs is byte-identical across two real `run_test` apps, one constructed with `NO_COLOR=1`, one without) |

| Count | Value |
|---|---|
| **SOURCE files** | **1 / 4** |
| Test files | 1 (new) |
| Doc files | 0 |

---

## 3 · How to test

```bash
env -u NO_COLOR -u TERM python -B -m pytest -q -p no:cacheprovider \
  tests/test_colour_always_on.py tests/test_help_scope.py
```

---

## 4 · Test results

| Layer | Owning node(s) | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `tests/test_colour_always_on.py::test_no_color_removed_before_super` | 1 | 1 passed |
| **A · white-box** | — | 0 | n/a (single-node mechanism; byte-identity is the white-box observable but is claimed at layer B) |
| **B · black-box** | AT-108 via `test_painted_screen_byte_identical_with_and_without_no_color` (two real apps through `run_test`, painted frame compared byte-for-byte) | 1 | 1 passed |

One complete gate run: **2 passed, exit 0** (`evidence/l1-green-2026-10-23.txt`, sha256
`21d67a695fdfda0b986f02dffa316479405743692191fac1319d837969ee0a8d`).
Byte-pinned must-stay-green: `tests/test_help_scope.py` **52 passed** (the RH6AG ambient
`NO_COLOR` fixture at :78-94 and the legend pin at :247-274 hold un-amended).

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | base tree: `mapper/app.py` restored to its pre-neutralisation bytes (sha256 `637bd1c94cc64ccbfaf1ebf37a459c0f750dab1f68710d93a94b9a03f38090d8`) and the increment's two new tests run against it — both RED; separately, the deliverable file `mapper/app.py` MOVED ASIDE (C-20 move-aside, never stash) |
| Instrument | project code: hand + `evidence/mutate_l1.py` (battery); move-aside by rename |
| Where it ran | the lane worktree `wt-l1` on `lane/l1`, run by the lane worker (orchestrator-spawned); no other lane's tree was read or written |
| Transcript | `evidence/l1-red-2026-10-23.txt` (base RED, sha256 `9486c32c6784991cff5b4d0718e81407c225f2f4091f98785478ed85bc5bed52`); `evidence/l1-move-aside-2026-10-23.txt` (sha256 `e90af6ec9965c30fa7c9d1b8e3580bf1b4350a8a158e1973f110734c98ca02f5`) |
| Restore proven by | file hash returned to its pre-mutation value — move-aside: `7ec4dba61dc8ec8d1ffc20dd62a3082001e6ca988e8592b723153b6b3d7c2152` before == after ("RESTORE PROVEN" in the transcript); battery: per-arm `before`/`after` digests identical to `7ec4dba…` |
| Bytecode cache | runs used `-B` / `PYTHONDONTWRITEBYTECODE=1` (C-46) |
| Arms resolved at baseline | base RED: 2 arms, both failed (exit 1); move-aside: 2 test modules in one invocation, exit 2 — `ModuleNotFoundError: No module named 'mapper.app'` at collection, so the absence reds the session at import (same shape as increment-001's move-aside) |
| Verdict granularity | per resolved node id / per file invocation |
| Arms that stayed GREEN | none |

| Field | Value |
|---|---|
| **RED counterfactual** | the increment's own new assertions fail on base: `test_no_color_removed_before_super` — `NO_COLOR` still present in `os.environ` after construction; `test_painted_screen_byte_identical_with_and_without_no_color` — the painted frame bytes differ with vs. without `NO_COLOR=1` (transcript above); with `mapper/app.py` moved aside, both holding modules go RED at import — restore digest `7ec4dba61dc8ec8d1ffc20dd62a3082001e6ca988e8592b723153b6b3d7c2152` |

| Field | Value |
|---|---|
| **Mutation verdicts** | 2 arms, both RED (KILLED), transcript `evidence/l1-mutation-battery-2026-10-23.txt` (sha256 `4995c97b09e25ad732a7e2ca3654dc3278f29f5ef0f0f72f546917de7b20e6ce`), runner `evidence/mutate_l1.py` (sha256 `18c88416c361ee0150e2acbc85782089c3fae7d8a77426fc94a02176f00edbda`): **M-Q1-1** — the neutralisation deleted (`os.environ.pop("NO_COLOR", None)` → `pass`, app.py:254) → `test_no_color_removed_before_super` RED · **M-Q1-1** (same edit, second arm) → `test_painted_screen_byte_identical_with_and_without_no_color` RED. Restores hash-proven per arm; arms that stayed GREEN: none |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `pytest` (the new suite) | the increment's new tests on the base tree | 2 failed, exit 1 — `l1-red-2026-10-23.txt` |
| the painted-frame probe (`_painted_frame`) | the base tree, where the `set` app's filter list carries Textual's `Monochrome` | the same serialization returned UNEQUAL bytes for `set` vs `absent` (`At index 38 diff: b'7' != b'1'`) before its first PASS was believed |
| `evidence/mutate_l1.py` | anchor/restore self-checks (count != 1 → `BAD (anchor count …)`; restore digest mismatch → `BAD (restore not proven)`) | the runner reports its own inapplicability instead of passing (same discipline as `mutate_l3.py`, proven there); every arm's `before`/`after` digests printed in the transcript |
| the privacy grep | a synthetic line carrying an email + handle + home path | the probe printed the hit (positive control) before reporting the authored files CLEAN |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 instruments, each shown RED before its first PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the process environment after construction | `assert "NO_COLOR" not in os.environ` with `NO_COLOR=1` set pre-construction | passed — the emitted env, not the intent |
| the app's line-filter list | `assert not any(isinstance(f, Monochrome) for f in app._filters)` | passed — no Monochrome filter object in the emitted list |
| the composited frame, serialized as `(text, style)` runs per strip, utf-8 | `assert frames["set"] == frames["absent"]` over two real `run_test` apps | passed — the emitted frames are byte-identical |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 3 artifacts, each asserted against the form its producer emitted |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| base RED transcript | `.dev-flow/2026-10-23-hygiene-batch/evidence/l1-red-2026-10-23.txt` | `9486c32c6784991cff5b4d0718e81407c225f2f4091f98785478ed85bc5bed52` |
| GREEN gate transcript | `…/evidence/l1-green-2026-10-23.txt` | `21d67a695fdfda0b986f02dffa316479405743692191fac1319d837969ee0a8d` |
| move-aside counterfactual | `…/evidence/l1-move-aside-2026-10-23.txt` | `e90af6ec9965c30fa7c9d1b8e3580bf1b4350a8a158e1973f110734c98ca02f5` |
| mutation battery + runner | `…/evidence/l1-mutation-battery-2026-10-23.txt` + `…/evidence/mutate_l1.py` | `4995c97b09e25ad732a7e2ca3654dc3278f29f5ef0f0f72f546917de7b20e6ce` (transcript) · `18c88416c361ee0150e2acbc85782089c3fae7d8a77426fc94a02176f00edbda` (runner) |

| Field | Value |
|---|---|
| **Evidence files** | 4 artifacts (5 files), each at the declared home and cited with the digest of its stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — "no `Monochrome` filter is active" is an absence over `app._filters`, and "the frame holds no desaturated style" is an absence over the serialized strips |
| If the result is an ABSENCE, what made the search wide enough | the filter assertion reads the WHOLE emitted filter list (not a sample); the frame assertion covers EVERY strip and segment of the composited screen at the gate size, both apps |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_no_color_removed_before_super` — its docstring names the LLR and the failure mode, so a future "improvement" cannot silently drop the absence assertion |
| Conjunctive criteria: one mutation per conjunct | the env-removal conjunct and the no-filter conjunct share one reddening mutation (M-Q1-1) — they are one mechanism observed at two points of the same construction, not two independent defences; the byte-identity arm is the independent second line and carries its own M-Q1-1 arm |
| Synthetic instance of the absent case | the base tree IS the synthetic instance: with the neutralisation absent, the filter is present and the frame desaturates — both recorded in the RED transcript |
| **Positive control for every probe that returned an ABSENCE** | the base-tree run returned the NON-absent output (filter present, frames unequal); the mutation battery re-produced it per arm |

### Reverse census — trigger family B, and A3

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rl "MapperApp" tests/` | 20+ files (`test_app.py`, `test_help_scope.py`, `tests/inc3_support.py`, …) — every one constructs `MapperApp(workspace)` through the UNCHANGED constructor; the byte-pinned ambient pin `tests/test_help_scope.py` re-run green (52 passed) |
| B2 file moved on disk | n/a — no file moved (the move-aside was restored, hash-proven) | none |
| B3 byte-identical golden captures this source | `grep -rn "MapperApp" tests/goldens/` | 0 hits — `tests/goldens/` holds renderer perf text (L3's pins), no `app.py` byte-pin |
| B4 artifact produced here is consumed elsewhere | `grep -rn "MapperApp(" mapper/` | the only construction outside tests is `mapper/app.py:355` (`main()`), same file — no cross-module consumer of a changed symbol |
| A3 interface consumed by another module changed | constructor signature diff (`git diff mapper/app.py`) | signature untouched — only the body gained the env pop; zero interface change |

NO_COLOR / no_color census (executed before the GREEN landing, per the lane brief):
`grep -rn "NO_COLOR\|no_color" mapper/ tests/` returns exactly five site groups — (1) the new
neutralisation `mapper/app.py:251,254`; (2) the deliberate Rich Console pin
`mapper/views/outline.py:311` (`Console(..., no_color=True)` INSIDE a renderer — explicitly out
of L1's edit set; flipping it would redden the Outline byte-identity digests); (3) the same
idiom in `tests/test_overflow.py:1887` (test-side renderer fixture, likewise untouched); (4) the
RH6AG ambient fixture + legend pin in `tests/test_help_scope.py:79-94,247-274` (byte-pinned
must-stay-green, 52 passed); (5) this increment's new `tests/test_colour_always_on.py`. No other
site exists, so no second edit was owed — the axis (environment → constructor → filter list) is
closed at the single decided point.

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run of B1 · B2 · B3 · B4 · A3, each with its command and its verdict, + the NO_COLOR census — every hit re-validated as lane-owned, byte-pinned must-stay-green, or an out-of-set deliberate pin |

### Correction population — enumerated BEFORE the first site was edited

| Field | Value |
|---|---|
| **Correction population** | none — no correction (the neutralisation is new behaviour mandated by ruling R3, not a fix to a previously asserted wrong claim); no site enumeration owed (C-14 n/a) |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|---|---|---|---|
| none — no superseded marker in this increment | n/a | n/a | n/a |

### Signed-balance test ledger

`post = base − deleted + added` → L1-scoped: 2 = 2 new nodes − 0 deleted ✓ reconciles against
the gate run; byte-pinned must-stay-green `tests/test_help_scope.py` 52 passed un-amended.
Full-suite reconciliation is owned by the orchestrator after the lanes join (one complete run).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer — Kimi K3 subagent executing agents/code-reviewer.md · OK-with-notes, 0 BLOCKER / 0 MAJOR / 1 MINOR · 2 reviewer-chosen mutants KILLED with hash-proven restores, 5/5 evidence digests match, RED/move-aside/GREEN transcripts genuine; F1 MINOR: declared NO_COLOR set-empty boundary regime has no test arm — full report .dev-flow/2026-10-23-hygiene-batch/evidence/review-inc002.md` |

---

## 5 · Risks

- The neutralisation mutates the process environment (it must — Textual reads the variable at
  construction). If a future embedding constructs `MapperApp` inside a process that deliberately
  wants `NO_COLOR` honoured for OTHER Rich/Textual output, the pop removes it globally. Accepted
  by ruling R3: the constructor is the app's colour-policy point, "colour always on" is the
  product decision (operator ruling Q5).
- The black-box arm captures the frame after `pilot.wait_for_scheduled_animations()` because
  `motion.pulse_cursor` breathes the canvas opacity for 300 ms on every repaint — a mid-breath
  capture samples a time-varying blend, not a stable screen. If a future repaint path schedules
  a LONGER animation, the wait still settles it; if the pulse is removed, the wait is a no-op.
  The RED arms do not depend on the settle (the Monochrome desaturation differs regardless).
- No contamination incident: `git status` in `wt-l1` showed only this lane's own files
  (app.py, the new test, evidence, this packet) — no foreign edits detected during the gate.

---

## 6 · Pending items / spec deviations

- None against spec. Recorded observations for the trunk: the NO_COLOR census found a second
  deliberate `no_color=True` Console pin at `tests/test_overflow.py:1887` (renderer fixture,
  same idiom as the declared `mapper/views/outline.py:311` pin) — left untouched, out of L1's
  edit set; no action owed.
- Trunk watch-item carried: full-suite run once after the lanes join (orchestrator-owned).

---

## 7 · Suggested next task

Land lanes L2a (Q2-core: `store.py`, `diff.py`, `osopen.py`) and L2b (Q2-csv: `import_csv.py`,
`screens/home.py`), then join all lanes for the orchestrator-owned full-suite run and the
independent review station.

---

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|
| 1 | ≤4 source files, or reason declared | ✓ | 1 SOURCE file (`mapper/app.py`) — §2 |
| 2 | Tests written in this same increment | ✓ | `tests/test_colour_always_on.py` (new in this increment) |
| 3 | Layer 0 written where the criterion applies | ✓ | `test_no_color_removed_before_super` — construction crosses the Textual base boundary, env+filter conjuncts |
| 4 | **RED counterfactual** declared | ✓ | base RED + move-aside transcripts with digests — §4 |
| 5 | **Reverse census** declared | ✓ | 5 probes + A3 + the NO_COLOR census — §4 |
| 6 | `code-reviewer` passed — declared in §4b | ⚠ | `pending — orchestrator schedules` — recorded in §4b, not yet run |
| 7 | No file from another lane touched | ✓ | `git status` shows only L1-owned files (app.py + new test + L1 evidence/packet) |
| 8 | Frozen interfaces untouched (or returned to the trunk) | ✓ | D1/D2 untouched; constructor signature unchanged; `tests/test_help_scope.py` 52 passed |
| 9 | Coverage claims verified **on disk**, not from intent | ✓ | every LLR names a realized node; the gate run executed them (2 passed) |
| 10 | Load-bearing emptiness declared, with its synthetic instance (C-55) | ✓ | §4 table — base tree + M-Q1-1 as positive controls |
| 11 | **Mutation verdicts** declared — per arm, inert arms named, registry ids cited | ✓ | M-Q1-1 × 2 arms, both RED (KILLED), restores hash-proven — §4 |
| 12 | **Instrument RED-proof** declared | ✓ | 4 instruments shown RED first — §4 |
| 13 | **Correction population** declared | ✓ | none — no correction (declared, not omitted) — §4 |
| 14 | **Emitted-form assertion** declared | ✓ | 3 emitted artifacts asserted — §4 |
| 15 | **Independent review** names somebody | ⚠ | `pending — orchestrator schedules` — the declared pending state, not an empty cell |
| 16 | **Evidence files** declared | ✓ | 4 artifacts (5 files) with stored-bytes digests — §4 |

---

## Review-findings follow-up — 2026-10-24 (independent review `evidence/review-inc002.md`)

**inc002-F1 (MINOR — the declared `NO_COLOR=""` set-empty boundary regime had no test arm) — DISPOSITION: fixed.**
- Requirement it serves: LLR-Q1.1.1 (the declared boundary catalog "var set / absent / set-empty") + HLR-Q1.1.
- Fix (test file only, inside this increment's set): `tests/test_colour_always_on.py::test_no_color_removed_before_super` parametrized over `["1", "", "an arbitrary value"]` — the set-empty arm is `test_no_color_removed_before_super[]`. Both existing assertions kept per arm.
- No RED arm owed: the gap was coverage on already-correct, value-independent code (`os.environ.pop("NO_COLOR", None)`), so a RED-before-GREEN pair is not meaningful; the discriminating proof is the mutant below.
- Asserting mutant (executed 2026-10-24, restore hash-proven): **M-Q1-1** — the pop deleted in `mapper/app.py:MapperApp.__init__` → all three parametrized arms RED (including the new set-empty one) plus the black-box arm; before/after sha256 of `mapper/app.py` both `7ec4dba6…7c2152`.
- Evidence (sha256 of stored bytes, account name redacted to `<user>` per A-110): `evidence/fu-inc002-f1-no-color-empty-arm-green-2026-10-24.txt` (`c3323afd…4cd6112`, 4 passed, `exit=0`), `evidence/fu-inc002-f1-no-color-empty-arm-mutant-2026-10-24.txt` (`cb1ea894…cd91010`, 4 failed, `exit=1`). Both transcripts record their exit codes (the inc001-F1 process fix).
