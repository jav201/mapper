# Increment 010 (PERF-RH) — LLR-RH.5.4 · `Parse cache stat fast path (warm-load budget)`

| Field | Value |
|---|---|
| Batch | `2026-10-11-reqharness-batch` |
| Increment | `010` (PERF-RH) |
| Lane (if the batch forked) | none — one lane, trunk unit PERF-RH |
| Requirement(s) | LLR-RH.5.4 (warm-cache budget, P4 miss) · LLR-RH.5.3 (cache purity, amended by ruling) · orchestrator ruling (ledger LED-2026-10-11-reqharness-batch.36) |
| Acceptance | LLR-RH.5.4 re-measured ≤ 0.5 s median at 5 000 events / 2 000 requirements (same P4 protocol) · the 4 mandated fast-path nodes green · RED proof · `--audit` cache-OFF unchanged |
| Agent | `software-dev` (Kimi, kimi-code) |
| Date | `2026-10-11` |

---

## 1 · What changed

BLUF: the review parse cache gained the **stat fast path** ruled by the
orchestrator after the P4 measurement missed the LLR-RH.5.4 warm-cache budget
(5.27 s median vs ≤ 0.5 s; 4.54 s of it `load_reviews` re-reading and
sha256-hashing 5 000 immutable files because the cache key WAS the hash of
the bytes).  Re-measured with the P4 protocol: **0.4432 s median — the
budget is MET** (12× faster; `load_reviews` warm 4.54 s → 0.40 s).

Mechanism, per the ruling:

- **The fast path** (`cache.py::ParseCache.fast`, `reviews.py::_load_one`):
  review event files are immutable and content-named (the sha8 in the name is
  recomputed at read), so a warm load reuses the validated parse when
  `(relative name, st_size, st_mtime_ns, st_ino, st_dev)` ALL match a cache
  entry that previously PASSED the full check (sha256 of bytes == entry
  digest AND name sha8 check AND schema) — WITHOUT reading the file.  On
  Windows `st_ino` is the NTFS file index: an in-place rewrite keeps it, a
  delete+recreate changes it.
- **Any mismatch (or missing stat field) → the full path**, unchanged in
  strength: confined ≤ 64 KB read, sha256, typed schema, R22 name check;
  `remember` then refreshes the entry with the new stat tuple.  A fast-path
  hit is still re-validated on CPU (schema + R22 over the cached document —
  no I/O, ~0.08 s per 5 000 files); a hit that fails is dropped with
  `bust_name` and re-parsed from the bytes — a poisoned entry degrades to a
  re-parse, never a verdict change (M-RG5's guarantee is unchanged).
- **The stat tuple is taken without a second confinement walk**: the name
  comes from the confined `scan_event_dir` listing (a directory entry name
  carries no separators), so `_file_stat` is a plain `os.stat(...,
  follow_symlinks=False)` plus the shared `is_link` refusal — a link or an
  unstatable file falls through to the full path, where the confined reader
  refuses it BY NAME.  (A per-file `confine_reason` walk measured 2.9 s per
  5 000 files — it would have negated the ruling.)
- **Persistence** is versioned: the store is now `{"v": 2, "docs": {sha:
  doc}, "stat": {name: [stat, sha]}}`; a v1/foreign/corrupt file is bounded
  to a rebuild exactly as R26 already promises.  `ParseCache.disabled()`
  (the `--audit` state) is untouched: cache OFF, full verification, writes
  nothing.  The `roles.yml`/`config.yml` loads are not changed.
- **Re-measurement** (`evidence/p4-timing.transcript`, appended): same
  synthetic generator, session temp, real git repo, median of 3.  Warm
  derive pipeline 0.437/0.443/0.462 s → **0.4432 s median ≤ 0.5 s — MET**;
  cold load unchanged (~4.7 s, paid once per new file); `--audit` wall 5.61 s,
  cache OFF by design, `verdict: ready`, 2 000/2 000 objects reviewed.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/reqharness/cache.py` | source | LLR-RH.5.3/5.4 · ruling LED-…-batch.36 | the stat fast path: v2 persisted store (`docs` + `stat`), `fast(name, stat)`, `remember(..., name=, stat=)` records the stat tuple, `bust` purges the stat index, new `bust_name` |
| `mapper/reqharness/reviews.py` | source | LLR-RH.5.3/5.4 · ruling LED-…-batch.36 | `_file_stat` (plain `os.stat` + `is_link`, no confinement walk), `_load_one` tries the fast path before the read; full path unchanged and still re-validates every sha-keyed hit |
| `tests/test_reqharness_cache_fastpath.py` | test | LLR-RH.5.4 · ruling | the 5 mandated nodes (below) |
| `tests/test_reqharness_registry.py` | test | LLR-RH.5.3 (RHFIX4 H2 node) | the H2 node's persisted-store inspection follows the v2 payload (`store["docs"]`) — the invariant it pins is unchanged |
| `.dev-flow/2026-10-11-reqharness-batch/evidence/perf-rh-red.transcript` | generated | RED proof | revert → RED → byte-identical restore (sha256) → GREEN |
| `.dev-flow/2026-10-11-reqharness-batch/evidence/p4-timing.transcript` | generated | LLR-RH.5.4 | re-measurement appended (same protocol as P4) |
| `01-requirements-ledger.md` · `01-requirements.md` · `04-validation.md` · `design/PDR-…-reqharness-batch.md` · `docs/ARCHITECTURE.md` | doc | the ruling + residual | ledger LED-…-batch.36 with the LLR-RH.5.4 back-pointer; P4 table + verdict updated (MET, stated honestly); PDR DDR-amendments residual row; ARQ reqharness notes row |

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 4** (`cache.py`, `reviews.py`) |
| Test files | 1 new + 1 inspection-line update (uncapped) |
| Doc files | 5 amended + 3 increment packets re-pinned (V41) |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_cache_fastpath.py
```

Full slice verification (the unit's command):

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_*.py tests/test_roles_screen.py tests/test_app.py tests/test_no_operator_paths.py
ruff check mapper/reqharness
```

---

## 4 · Test results

| Layer | Owned in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `test_warm_load_skips_unchanged_file_bytes`, `test_same_size_same_mtime_new_file_id_takes_full_path`, `test_changed_size_or_mtime_takes_full_path`, `test_same_size_same_mtime_same_inode_rewrite_is_the_residual`, `test_fast_path_results_identical_with_cache_deleted` | 5 passed |

### GREEN — executed now, from the worktree root

```bash
$ env -u NO_COLOR -u TERM python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_cache_fastpath.py tests/test_reqharness_registry.py
17 passed in 3.78s
$ ruff check mapper/reqharness
All checks passed!
```

Full unit slice (the command in §3), executed now from the worktree root:

```bash
$ env -u NO_COLOR -u TERM python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_*.py tests/test_roles_screen.py tests/test_app.py tests/test_no_operator_paths.py
121 passed, 1 warning in 53.73s
$ ruff check mapper/reqharness
All checks passed!
```

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | the product change reverted to HEAD (`git show HEAD:…` — read-only), the new test file kept |
| Instrument | manual, transcript below |
| Where it ran | **this worktree** |
| Transcript | `.dev-flow/2026-10-11-reqharness-batch/evidence/perf-rh-red.transcript` |
| Restore proven by | **file hashes returned to their pre-mutation values** (sha256 before == after, printed in the transcript) |
| Arms resolved at baseline | **3 of 5 nodes redden** (the other two — the new-file-id catch and the cache-deleted equality — also pass on the old code, which always re-reads; they pin behaviour the ruling keeps, not the new mechanism) |
| Verdict granularity | per node id |

| Node | RED evidence (transcript) | Restore (sha256 before == after) |
|---|---|---|
| `test_warm_load_skips_unchanged_file_bytes` | `FAILED … read_event_file called for unchanged file` | `cache.py` `76080da9…638e20`, `reviews.py` `0367ce84…ab062` byte-identical → 5 passed |
| `test_changed_size_or_mtime_takes_full_path` | `FAILED …` (same mechanism: no stat tuple is ever recorded) | same digests → 5 passed |
| `test_same_size_same_mtime_same_inode_rewrite_is_the_residual` | `FAILED …` (same) | same digests → 5 passed |

### Residuals (stated, not fixed)

- **The in-place rewrite (the ruling's residual, test-pinned):** a writer
  who preserves size+mtime+file-id while changing bytes in place is served
  the stale validated parse — on Windows `st_ino` is the NTFS file index and
  an in-place rewrite keeps it.  That writer can equally write
  `.git/reqharness-cache` itself (the same trust boundary as R4); `--audit`
  is cache-OFF, re-reads every file, and catches the change (the node proves
  exactly this).  Recorded in the ledger entry, the PDR DDR amendments and
  `04-validation.md`.
- The TOCTOU race between the scandir listing and the fast-path stat needs a
  stat tuple collision on a swapped file to matter — the same layer-3 trust
  class as the residual above; the full path re-confines before any read.

### Evidence files — bytes at a declared home, verbatim, hash-verified

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED-proof transcript (personal paths scrubbed to `<home>`) | `.dev-flow/2026-10-11-reqharness-batch/evidence/perf-rh-red.transcript` | `5e70027fe1c6d811777349e8e3bfcc50b6108bda96f7cbe2382dd8df97038c38` |
| P4 re-measurement (appended to the P4 transcript) | `.dev-flow/2026-10-11-reqharness-batch/evidence/p4-timing.transcript` | `4e11c17c59d8547dfd4dc74e94370685e16409a043f3087e4d7b3345fe0dbfe7` |

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | owed to the orchestrator (post-batch close-out unit); the ruling itself IS the orchestrator's recorded review of the P4 gap (G-CLOSE1-1) |

---

## 5 · Risks

- The stat fast path keys on `st_mtime_ns` granularity: a filesystem with
  coarse mtime stamps widens the in-place-rewrite residual window (a rewrite
  landing inside the same stamp with the same size+ino is invisible).  The
  file id and the stated residual bound it; NTFS (this machine) carries
  100 ns stamps.
- The persisted store doubled its read cost (stat index); at the 100 000-file
  scale the index is ~10 MB of JSON — bounded by the cache's own 64 MB limit
  (L2), and a rebuild on any format surprise is R26-bounded.
- Cold load is deliberately untouched (~4.7 s at 5 000 files under on-access
  AV); the fast path only removes the *re*-read on warm loads.

## 6 · Pending items / spec deviations

- **V41 re-pins (mandated by the unit):** the orchestrator's personal-path
  scrub changed the bytes of three close-out transcripts; the citations in
  `increment-004/005/006/007.md` are re-pinned to the on-disk sha256 (one
  note line per packet).  The batch validator now reports **0 blocks under
  this batch** (V7/V15/V16 are environment, ignored per the unit).
- `pending.py` is NOT in this increment: its loader (`list_pending`) does not
  share the cache path (it reads through `config.load_pending` directly), so
  the ruling's "reviews.py (and pending.py only if its loader shares the
  path)" leaves it untouched.
- The measurement scripts (fastbuild/p4_measure) lived in the session temp
  per the P4 protocol and are not tracked; the transcript records their
  commands and verbatim output.

## 7 · Suggested next task

The orchestrator: commit the trunk (all PERF-RH files + the four V41
re-pins), record the gate-suite re-run owed by note 2 of `04-validation.md`,
and close the batch — every requirement now passes or is MET by measurement.

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | ≤4 source files | ✓ | 2/4 (`cache.py`, `reviews.py`) |
| 2 | Tests written in this same increment | ✓ | `tests/test_reqharness_cache_fastpath.py` |
| 3 | Layer 0 written where the criterion applies | ✓ | 5 nodes, §4 |
| 4 | RED counterfactual declared | ✓ | revert → 3 nodes RED → byte-identical restore (sha256), transcript §4 |
| 5 | Security conditions discharged mapped to findings | ✓ | the ruling's residual stated + test-pinned; M-RG5's re-validation guarantee unchanged |
| 6 | `code-reviewer` passed | ⚠ | owed to the orchestrator (§4b) |
| 7 | No file from another lane touched | ✓ | one lane |
| 8 | Frozen interfaces untouched | ✓ | no ARQ §4 row changed; no keymap/seat edit |
| 9 | Coverage claims verified on disk | ✓ | GREEN lines from runs executed now; the budget verdict cites the transcript |
| 10 | Residuals stated honestly | ✓ | in-place rewrite residual + TOCTOU note, §4/§5 |
| 11 | Evidence files declared | ✓ | 2 rows with sha256 |
| 12 | Independent review names somebody | ⚠ | the ruling is the orchestrator's; §4b |
