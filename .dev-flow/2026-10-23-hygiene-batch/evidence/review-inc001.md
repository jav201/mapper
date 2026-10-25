# Code Review — Increment 001 (lane L3, US-Q3-001)

Reviewer role: `code-reviewer` (independent Phase-3 increment gate; not the author).
Date: 2026-10-24.

## Scope reviewed

- Commit: `345e46d` — `feat(canvas): Canvas audit hook (frozen D1) + scalecheck sweep … (AT-115/116)`.
- Source files touched: **1** — `mapper/canvas.py` (the `audit=None` hook; `put` event recording).
- Test files: `tests/test_canvas_audit.py` (new), `tests/test_scalecheck.py` (new), `tests/test_a3_census.py` (B-44 pin + arg-ful pin 83 → 86, amended).
- Docs (outside the budget): `docs/ARCHITECTURE.md`, `.dev-flow/**` (requirements, ledger, PLAN, state matrix, packet, evidence).
- Tree state: files under review are byte-identical between `345e46d` and the current HEAD (`git diff 345e46d HEAD -- <paths>` empty), so the live tree was usable for test-intent arms.

## Checks performed

### 1. Requirements conformance (method step 2)

Read in `.dev-flow/2026-10-23-hygiene-batch/01-requirements.md`: US-Q3-001 (:145), HLR-Q3.1 (:277), HLR-Q3.2 (:293), LLR-Q3.1.1 (:388), LLR-Q3.1.2 (:399, as amended by ledger .11), LLR-Q3.2.1 (:409), LLR-Q3.2.2 (:420), LLR-Q3.2.3 (:431, as amended by .12/.13), AT-115/AT-116 acceptance blocks.

The diff implements exactly these clauses:

- `mapper/canvas.py:96-130` — trailing `audit=None`; `put` appends `(x, y)` under `clip` for out-of-bounds non-space writes and under `overprint` for in-bounds writes where held char is a *different* alphanumeric and the new char is alphanumeric; nothing otherwise; sinkless path semantically identical to the pre-increment guard. Matches LLR-Q3.2.1/.2, no more, no less.
- `tests/test_scalecheck.py` — roster derived from `mapper.views.__all__` with empty/<6/changed guards (LLR-Q3.1.1); 1..h lines + per-line `cell_len ≤ w` with the Layered header spill asserted *exactly* as `(w−2) + cell_len('{n} nodes')` + overflow declaration (`_check_geometry`, amended LLR-Q3.1.2); audit arm pins the measured construction census and zero unexplained events (amended LLR-Q3.2.3).
- `tests/test_canvas_audit.py` — event set + both overprint limbs + clip space-gate + coordinates (LLR-Q3.2.1); plain+spans byte-identity with/without sink (LLR-Q3.2.2).
- `tests/test_a3_census.py` — B-44 pin now `["self","w","h","tones","fallback","audit"]` (frozen D1, A3 discipline); arg-ful pin 83 → 86 with the three sweep sites itemized.

### 2. Diff + surrounding code read (method step 3)

Full diff of `345e46d` read. Surrounding code read for convention/conformance: `mapper/canvas.py` (whole file, 237 lines), `mapper/views/layered.py:480-710` (`painted_ids`, `_header_line`, `render` — header is composed outside the canvas, which is why its `cell_len` may exceed `w`; the test's exact-arithmetic pin matches the measured composition), `mapper/views/__init__.py` (roster of 6), `mapper/views/state.py` (`ViewState` fully-defaulted frozen dataclass, `folded` field), `tests/perf_goldens_capture.py:100-125` (reused builders). Docstring and test conventions match the repo's established style (LLR ids + asserting mutants named in docstrings).

### 3. Test-intent spot check — two OWN mutant arms (method step 5)

Target `mapper/canvas.py`, pre-mutation sha256 `decab49cb8b0043046a6a61c140c00fbbd285c3932a080d224d645a09dea765d` (note: identical to the packet's move-aside pre/post digest — cross-confirms the stored bytes).

| Arm | Mutation (one edit) | Command (targeted file only) | Result | Verdict |
|---|---|---|---|---|
| M-R1 (own) | clip space-gate dropped: `… and ch and ch != " ":` → `… and ch:` (`mapper/canvas.py:116`) | `env -u NO_COLOR -u TERM python -m pytest -q -p no:cacheprovider --color=no tests/test_canvas_audit.py` | exit 1 — `test_events` RED: phantom clip `(4, 1)` recorded for the out-of-bounds space | **KILLED** |
| M-R2 (own) | bounds off-by-one: `0 <= x < self.w` → `0 <= x <= self.w` in `put` (`mapper/canvas.py:115`) | same, `tests/test_canvas_audit.py` | exit 1 — `test_events` + `test_text_and_wire_paths_share_put_and_default_sink_is_none` RED (clip at x==w swallowed) | **KILLED** |

Restores: file copied back from a pre-mutation byte copy after each arm; sha256 re-computed `decab49c…dea765d` after both restores (== pre-mutation). Backup and run logs deleted afterwards. Neither arm is in the packet's battery (M-Q3-1…4).

Intent assessment: `test_events` carries discriminating negatives for **all four** conjuncts of the overprint rule — held-gate (space then letter at (0,0)), new-gate (M-Q3-4 arm: alnum over `│` at (2,0)), difference-gate (same-char A→A), and the clip space-gate — plus exact coordinates. No false-confidence tests found.

### 4. Evidence audit (method step 6)

Digest table — all recomputed with `sha256sum` over the stored bytes:

| File (under `.dev-flow/2026-10-23-hygiene-batch/evidence/`) | Packet digest | Recomputed | Match |
|---|---|---|---|
| `l3-red-2026-10-23.txt` | `55af8900…1cce77c` | same | ✓ |
| `l3-sweep-measurement-probe-2026-10-23.txt` | `5d0a7bae…f0af47` | same | ✓ |
| `l3-green-2026-10-23.txt` | `b646a255…2106e4` | same | ✓ |
| `l3-move-aside-2026-10-23.txt` | `60a1faa0…f5d125` | same | ✓ |
| `l3-mutation-battery-2026-10-23.txt` | `f022b5a1…dd139e` | same | ✓ |
| `mutate_l3.py` | `afef7aa7…97a479` | same | ✓ |
| `l3-b3-golden-census.txt` | `48450c4b…a3ff83` | same | ✓ |

Transcript reads:

- **RED** (`l3-red-2026-10-23.txt`): genuine failure — 5 failed / 1 passed, exit 1. The audit arms fail with `TypeError: Canvas.__init__() got an unexpected keyword argument 'audit'` on base; `test_sweep` fails with the *sealed* oracle ("exactly h lines, ≤ w") against the live tree (Layered h−4 lines + header spill, etc.) — exactly the measurement ruling R10 records; the committed test carries the amended oracle. Consistent with the packet.
- **Move-aside** (`l3-move-aside-2026-10-23.txt`): 5 per-file invocations, each exit 2 at collection (`mapper.canvas` unimportable), pre/post sha256 equal, "RESTORE PROVEN". Move-aside, not stash. ✓
- **GREEN** (`l3-green-2026-10-23.txt`): one complete run, 146 passed / 15 deselected. The packet's "exit 0" is consistent with the all-pass line, but the transcript does not itself record the exit code (sibling transcripts do) — see F1.
- **Mutation battery** (`l3-mutation-battery-2026-10-23.txt`): M-Q3-1…M-Q3-4 all RED (KILLED) on their named nodes; per-arm before/after digests equal.
- **B3 census** (`l3-b3-golden-census.txt`): 93 passed, `exit=0` recorded.

### 5. Golden double-proof (P3 station extra check)

**No new byte-identical golden baseline was minted by this increment.** Evidence: `git diff 345e46d^ 345e46d --name-only -- tests/goldens` returns zero paths (the commit touches 17 files, none under `tests/goldens/`). `l3-b3-golden-census.txt` is a *re-run transcript* of the pre-existing byte-pinned suites, not a new baseline. Independent confirmation: I re-ran those two suites at the current tree (whose files under review are byte-identical to `345e46d`) — `tests/test_repair_depth.py` + `tests/test_perf_paint_clip.py`: **93 passed, 15 deselected**, reproducing the transcript's count with the committed goldens un-re-baselined. Re-derivation from the parent ref was therefore not owed.

### 6. Source-file budget (method step 7)

1 SOURCE file (`mapper/canvas.py`) of ≤4 — clean; no ⚠ statement owed. Packet §2 declares 1/4. ✓

### 7. Reverse trace (V59, method step 8)

Every touched source/test file names ≥1 id in packet §2 `Traces to`, and each id exists in `01-requirements.md` (verified by grep + range reads): `mapper/canvas.py` → LLR-Q3.2.1/.2 ✓; `tests/test_canvas_audit.py` → LLR-Q3.2.1/.2 ✓; `tests/test_scalecheck.py` → LLR-Q3.1.1/.2, Q3.2.3 ✓; `tests/test_a3_census.py` → LLR-Q3.2.1, Q3.2.3 ✓.

### 8. Lens pass (correctness / simplicity / reuse / convention)

- Correctness: sinkless `put` path is semantically identical to the pre-increment guard (empty-ch no-op, bounds drop). Out-of-bounds empty-ch and space writes record nothing; in-bounds overprint requires both alnum limbs and difference — all four limbs test-pinned. No reachable None/error paths introduced (`audit` defaults to None; only `setdefault` on the injected mapping).
- Simplicity: 15-line hook at the single write convergence; no abstraction beyond the LLR. The sweep's helpers (`_roster`, `_states`, `_check_geometry`) are single-use but read linearly; not over-engineered.
- Reuse: builders imported from `tests/perf_goldens_capture.py` rather than duplicated; `painted_ids`/`overflow_phrase`/`OVERFLOW_TOKEN` reused from `mapper.views.layered` instead of re-derived. B4 probe re-verified: `audit=` appears in `mapper/` only at the constructor itself (sink consumed by tests only, ARQ commitment holds).
- Convention: docstrings, id-citation style, and census-pin amendment format match the repo's established patterns (incl. the B-44 row discipline in `tests/test_a3_census.py:315`).

## Findings

### F1 — GREEN gate transcript does not record its exit code [Severity: MINOR]
- **What:** `l3-green-2026-10-23.txt` ends at "146 passed, 15 deselected, 4 warnings in 22.51s"; unlike the move-aside and census transcripts (`exit: 2` / `exit=0`), the claimed `exit 0` in packet §4 is not in the stored bytes.
- **Where:** `.dev-flow/2026-10-23-hygiene-batch/evidence/l3-green-2026-10-23.txt:16`
- **Why it matters:** the all-pass line is consistent with exit 0, so the claim is very likely true — but the packet cites the transcript as the proof of "one complete run, exit 0", and the transcript under-records by one line. Evidence-hygiene only; nothing about the code is implicated.
- **Suggested fix:** for future gate transcripts, append `; echo "exit=$?"` (with `set -o pipefail` when piping) as the sibling transcripts already do. No re-run owed for this increment.

No other findings. In particular: no correctness defects, no false-confidence tests (2 own mutants + the packet's 4-arm battery all KILLED), no over-engineering, no duplication, no convention drift.

## Verdict

- Brief form: **approve-with-nits** (one MINOR open, nothing blocking).
- Record form: **OK-with-notes**.

## Proposed §4b `Independent review` cell text

`code-reviewer — OK-with-notes, 0 BLOCKER / 0 MAJOR / 1 MINOR · full diff read against amended LLR-Q3.1.2/Q3.2.3; evidence digests 7/7 match; no new golden minted (tests/goldens untouched) and the B3 census independently re-run green (93 passed); 2 own mutants on mapper/canvas.py (clip space-gate, bounds off-by-one) both KILLED with hash-proven restores; sole nit F1: green transcript omits its recorded exit code`

## Evidence checklist (role file)

- [x] Diff read in full (`mapper/canvas.py:81-130`, `tests/test_canvas_audit.py:1-77`, `tests/test_scalecheck.py:1-174`, `tests/test_a3_census.py:312-330,679-684`, `docs/ARCHITECTURE.md` canvas rows).
- [x] Correctness pass done (bounds/empty-ch/space/held-vs-new limbs; sinkless path equivalence).
- [x] Simplicity pass (no premature abstraction found).
- [x] Reuse/duplication checked against existing utils (builders + layered helpers reused).
- [x] Tests reviewed for intent (all four overprint conjuncts carry discriminating negatives; 2 own mutants KILLED).
- [x] Verdict explicit (OK-with-notes); zero HIGH/BLOCKER findings.
