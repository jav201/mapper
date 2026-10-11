# Validation — mapper — Batch 2026-10-11-reqharness-batch

> **Artifact language:** canonical English scaffold.
> Phase 4 artifact. Content owner: `qa-reviewer`, who **EVALUATES** the results of the
> validation strategy fixed in Phase 1 and **names who executed each one**; the CLOSE1
> unit (Kimi, code lane) executed the measurements and slice re-runs, the orchestrator
> owns the ONE complete gate-suite run (`C-25`).

## ✅ Verdict (read first)

- **Result:** PASS-WITH-NOTES
- **Layer 0:** 9 increments met the criterion · 24+ named reddening mutations executed
  RED (M-RG1..5, M-FN1/2, M-PR1, M-BL1..4, M-RL1, M-AU1/2, M-CH6, M-FS1, M-ID3,
  DDRFIX arms, CLOSE1 LOW-1/LOW-3/LOW-4 arms — per-increment transcripts on record)
- **Requirements:** P pass · ~~1 blocker fail~~ **LLR-RH.5.4 RE-MEASURED MET**
  after the PERF-RH unit's stat-fast-path ruling (measured, §P4 re-measurement
  below): the warm-cache budget now holds (0.44 s median vs ≤ 0.5 s at the
  5 000-event scale); every functional requirement passes its nodes
- **Black-box acceptance (Layer B):** ✓ every story's `AT` observes its outcome
  through the shipped surface (AT-077a/b/c · AT-078 · AT-079 screen arms; AT-064 ·
  AT-065 guard arms; `--audit` CLI arms driven as real subprocesses)
- **Surface-reachability (bidirectional):** ✓ all named inputs AND outputs reached
  (IFC Part A flows each name SOURCE → fn → SINK; the V10 blocks that refused the
  old FLOW syntax are fixed in the accepted form)
- **Supersession inspection:** ✓ all surviving refs negative (increment-009's
  "24 pre-existing failures" claim RETRACTED — it was the `TERM=dumb` shell
  artefact; see the correction appended to that packet)
- **Test ledger:** ✓ reconciles per the packets (base − D + A = post, recorded
  increment by increment)
- **Evidence checklist (qa-reviewer):** qa-reviewer · all rows ✓ with evidence —
  the per-increment RED transcripts (sha256-verified in the packets), the GREEN
  slice transcripts (incl. the CLOSE1 close-out captures), and this record

### Notes that keep this from being a clean PASS

1. **LLR-RH.5.4 warm-cache budget missed** — median 5.27 s vs the ≤ 0.5 s budget at
   5 000 events / 2 000 requirements on this machine; the cost is read+sha256 of
   5 000 files (the cache skips the parse only), not derivation (2 ms). Full data
   in §P4. Proposed action: re-rule the budget or key the cache on
   (name, size, mtime) — a requirements change, not a code change in this unit.
   **RESOLVED by the PERF-RH unit (2026-10-11):** the orchestrator ruled the
   stat fast path (parse cache keyed additionally on (relative name,
   st_size, st_mtime_ns, st_ino, st_dev); a full-stat match reuses the
   validated parse without reading the file, any mismatch takes the full
   path, `--audit` stays cache-OFF). Re-measured: **0.4432 s median — the
   budget holds** (§P4 re-measurement). Residual (stated, test-pinned): an
   in-place rewrite preserving size+mtime+file-id defeats the fast path;
   that writer can equally write `.git/reqharness-cache` itself (same trust
   boundary as R4); `--audit` re-reads every file and catches it.
2. **Full-suite re-run after part A is owed by the orchestrator** — the recorded
   full-suite result is the orchestrator's clean-shell run at bac7885:
   `3370 passed, 24 deselected, 3 xfailed, 12 warnings in 1743.24s (0:29:03)` —
   0 failed. A post-close1 full suite (and a re-run of `tests/test_agree_floor.py` /
   `tests/test_overflow.py` in a clean shell) belongs to the orchestrator.
3. Validator blocks V7 / V15 / V16 are **environment, out of scope** (local flow
   revision drift, the `~/.claude` bundle copy, uncommitted flow-bundle state) —
   they are not under this batch or `tests/` and are listed for the operator.

---

## Full-suite result (the gate line)

```text
3370 passed, 24 deselected, 3 xfailed, 12 warnings in 1743.24s (0:29:03)
```

Orchestrator's run at `bac7885`, clean shell (no `NO_COLOR`, idle machine) — **0
failed**. (Recorded by the increment-009 correction; supersedes the retracted
`24 failed` line, which was the `TERM=dumb` shell artefact.) **A re-run of the
full suite after part A of this close-out is owed by the orchestrator** — the
close1 changes touch `mapper/reqharness/{config,audit}.py` and three test files;
their slices are green in the close-out captures below.

## P4 measurement — LLR-RH.5.4 (warm-cache derivation budget)

Measured (never asserted in the suite), synthetic registry built in the session
temp (5 000 review events over 2 000 `HLR-*` requirements, real git repo), this
machine, `NO_COLOR` unset. Transcript: `evidence/p4-timing.transcript`.

| Measurement | Samples (s) | Median (s) | Budget | Result |
|---|---|---|---|---|
| YAML loader, one 64 KB file (R21 loader, CSafeLoader; incl. event-stream scan) | 0.0170 / 0.0169 / 0.0162 / 0.0160 / 0.0215 / 0.0223 / 0.0160 | **0.0169** | — | ~20 ms per 64 KB file; 5 000 files ≈ 100 s of pure parsing without the cache |
| Cold-cache review load (cache deleted; read+hash+parse+save, 5 000 files) | 25.68 / 5.02 / 5.54 | **5.54** | paid once per new file (R-SCALE) | the 24 s first sample is the one-time on-access AV scan of fresh files; steady cold cost ≈ 5 s |
| **Warm-cache derive pipeline** (verify_chain + load_reviews warm + load_canon + derive_states, median of 3) | 5.27 / 5.25 / 5.42 | **5.27** | **≤ 0.5 s** | **MISS — see note 1** |
| of which: `load_reviews` warm (read+sha256 5 000 files, parse cached) | — | 4.54 | — | the entire cost; the cache cannot skip the read+hash (key = sha256 of bytes) |
| of which: `derive_states` over the bound objects (5 000 events → 2 000 states) | — | 0.0502 | — | derivation itself is ~2 ms; `load_canon` (2 000 rows) 0.0017 s; `verify_chain` 0.0015 s |
| `--audit <repo>` wall time, cache OFF (real subprocess, exit 0, ready) | — | **5.85** | read-only audit at scale | parses all 5 000 events per run by design (R4: audit runs cache-off) |

**Verdict for LLR-RH.5.4: NOT MET on this machine** — 5.31 s median vs ≤ 0.5 s.
The miss is I/O-bound (5 000 file reads + sha256 under Windows Defender), not
parse- or derivation-bound; CSafeLoader is already in use (R-SCALE a). This is a
measurement result, not a suite failure — the suite asserts output equality only
(LLR-RH.5.3), which passes.

### P4 re-measurement — PERF-RH unit (stat fast path, 2026-10-11)

Same synthetic generator, session temp and median-of-3 protocol as the P4 run
above; the parse cache gained the stat fast path by orchestrator ruling
(LED-2026-10-11-reqharness-batch.36): `(relative name, st_size, st_mtime_ns,
st_ino, st_dev)` ALL match an entry that previously passed the full check →
the validated parse is reused WITHOUT reading the file; any mismatch (or
missing stat field) → full path (read, sha256, typed schema, R22 name check,
then the entry's stat tuple is refreshed). `--audit` stays cache-OFF, full
verification, unchanged. Full data: `evidence/p4-timing.transcript`.

| Measurement | Samples (s) | Median (s) | Budget | Result |
|---|---|---|---|---|
| Cold-cache review load (cache deleted; read+hash+parse+save, 5 000 files) | 4.71 / 4.72 / 4.66 | **4.71** | paid once per new file (R-SCALE) | unchanged from P4 (~5 s) — the fast path does not touch the cold cost |
| **Warm-cache derive pipeline** (verify_chain + load_reviews warm + load_canon + derive_states, median of 3) | 0.437 / 0.443 / 0.462 | **0.443** | **≤ 0.5 s** | **MET** (was 5.27 s — a 12× improvement) |
| of which: `load_reviews` warm (stat-only fast path, no read/hash; hit re-validated on CPU) | 0.398 / 0.406 / 0.394 | 0.398 | — | was 4.54 s; the remaining cost is 5 000 `os.stat` calls + schema/R22 re-validation under on-access AV |
| of which: `derive_states` (5 000 events → 2 000 states) | — | 0.044 | — | unchanged; `load_canon` 0.005 s; `verify_chain` 0.002 s |
| `--audit <repo>` wall time, cache OFF (real subprocess, exit 0, `verdict: ready`) | — | **5.61** | read-only audit at scale | unchanged by design (R4): parses all 5 000 events per run |

**Verdict for LLR-RH.5.4 after re-measurement: MET on this machine** — 0.4432 s
median vs ≤ 0.5 s. Residual (stated, test-pinned in
`tests/test_reqharness_cache_fastpath.py`): a local writer preserving
size+mtime+file-id while changing bytes in place defeats the fast path — that
writer can equally write `.git/reqharness-cache` itself (same trust boundary
as R4); `--audit` and release evaluation via audit are unaffected.

## LLR-RH.9.1 — D12 document content (P6 inspection)

Owed at P6: the 06-docs document proposes the ledger derivation (each 05-close
human review ledger entry derived from registry review events, citing the batch's
derived states, the precedence table and the release-rule semantics PDR §3.4 by
id) and states dev-flow adoption is outside this repository. Numeric threshold:
0 unresolved findings. **Status at CLOSE1: owed at P6 — the D12 proposal document
is a 06-docs deliverable produced at the batch's end; not yet inspectable.**
(Folded from `04-validation-notes.md`, now deleted.)

---

## Detail (reference)

### Layer 0 — unit (per-requirement results; nodes and evidence)

| Req | Method | Executed verification | Result | Evidence |
|---|---|---|---|---|
| HLR-RH.1 / LLR-RH.1.1–1.4 | test | `tests/test_reqharness_config.py` — 11 nodes (loader refusals, schema, genesis, canonical form, email hashing; CLOSE1 arms: exact `nesting too deep` message, config 64 KB cap) | pass | `rh4-green-close1.transcript` (99 passed, slice) · `rh1-red.transcript` · `close1-red.transcript` |
| HLR-RH.2 / LLR-RH.2.x | test | `tests/test_reqharness_chain.py` — 21 nodes (chain walk, pending resolution, input limits; CLOSE1 arms: exact depth-refusal message) | pass | `rh2-red.transcript` · `rh23fix-red.transcript` · `close1-red.transcript` |
| HLR-RH.3 | test | `tests/test_reqharness_chain.py` verify/effective-roles nodes | pass | `rh2-red.transcript` |
| HLR-RH.4 / LLR-RH.4.x | test | `tests/test_reqharness_registry.py` — 9 named nodes (states, pre-review, informative mark, naming, cache purity, census) | pass | `rh4-red.transcript` (M-RG1..5 · M-FN1/2 · M-PR1 RED) · `rh4-green-close1.transcript` |
| HLR-RH.5 / LLR-RH.5.1–5.3 | test | `tests/test_reqharness_registry.py` derive/cache nodes | pass | as above |
| LLR-RH.5.4 | measurement | §P4 re-measurement above | **MET (0.4432 s ≤ 0.5 s)** | `p4-timing.transcript` |
| HLR-RH.6 / LLR-RH.6.x | test | `tests/test_reqharness_baseline.py` — baseline create/diff/classification | pass | `rh5-green-close1.transcript` |
| HLR-RH.7 / LLR-RH.7.x | test | `tests/test_reqharness_release.py` — 14 nodes (verdicts, `--audit` confinement/refusals; CLOSE1 node: `_visible` escapes NBSP/combining/variation selectors) | pass | `rh5-red.transcript` · `close1-red.transcript` |
| HLR-RH.8 / LLR-RH.8.x · AT-077a/b/c · AT-078 · AT-079 | test | `tests/test_roles_screen.py` + `test_inc9*`/`test_en5`/`test_keymap`/`test_key_dispatch` — screen matrix, footer band, markup/sink/census oracles | pass | `rh6a-green-close1.transcript` (308) · `rh7-green-close1.transcript` (454) |
| AT-064 · AT-065 (guards) | test | `tests/test_app_imports_used.py` · `tests/test_mod_parity.py` (goldens re-pinned, itemised) | pass | increment-009 §4–5 |
| SEC F1/F2 · QA C1–C6 · ARCH C3/C5 (DDRFIX) | test | `tests/test_reqharness_config.py` event-stream arms · `tests/test_reqharness_release.py` escaper arms · mutant catalogue M-CH6/M-FS1/M-ID3 | pass | `ddrfix-red.transcript` · `ddrfix-c-red.transcript` · increment-008 packet |
| CLOSE1 LOW-1/LOW-3/LOW-4 | test + RED | exact-message depth refusal · `_visible` widening · config byte cap — each RED-proven by revert → restore (sha256) | pass | `close1-red.transcript` · LOW-2 residual in PDR §E |

### Layer 0 — measured by mutation

Per-increment RED tables with per-arm digests live in each packet (§4/§5); the
transcripts under `evidence/` carry the per-arm `FAILED` lines and the
byte-identical restore hashes. CLOSE1 arms: LOW-1 (3 nodes reddened), LOW-4
(`DID NOT RAISE`), LOW-3 (escape mismatch) — transcript `close1-red.transcript`.

### UX walkthrough

Trigger family D did not fire for this batch (headless core + one screen whose
acceptance is driven by the piloted TUI tests above). Mechanism used: a UI test
driver (`run_test(size=...)` + real key presses) for the screen arms; CLI
subprocess for `--audit`.

### Signed-balance test ledger

Per the packets: each increment records its own base/−D/+A/post line; the
orchestrator's full-suite line above is the gate result (3370 passed at bac7885;
a post-close1 re-run is owed, see note 2).

### Gaps detected

| ID | Requirement | Gap | Severity | Proposed action |
|---|---|---|---|---|
| G-CLOSE1-1 | LLR-RH.5.4 | warm-cache derive 5.31 s > 0.5 s budget at 5 000 events on this machine (I/O-bound: read+sha256 of 5 000 files; parse cached, derivation ~2 ms) | major | **RESOLVED by the PERF-RH unit (2026-10-11):** orchestrator ruling LED-…-batch.36 — the parse cache gained the stat fast path (name, size, mtime_ns, ino, dev; full check on mismatch; `--audit` uncached); re-measured 0.4432 s median — budget MET; residual stated (in-place same-stat rewrite) and test-pinned |
| G-CLOSE1-2 | full suite | post-close1 full-suite run owed (orchestrator-owned per C-25) | minor | orchestrator re-runs after committing part A |

### Evidence checklist — qa-reviewer (full)

- Per-increment RED transcripts with sha256 restore digests: ✓ (`evidence/*-red.transcript`)
- GREEN slice transcripts incl. CLOSE1 close-out captures: ✓ (`rh4/rh5/rh6a/rh7-green-close1.transcript`, `close1-green-slice.transcript`)
- P4 timing transcript: ✓ (`evidence/p4-timing.transcript`)
- Security nits (K3 re-check) RED proof: ✓ (`evidence/close1-red.transcript`)
- PDR §E residual for LOW-2: ✓ (`design/PDR-2026-10-11-reqharness-batch.md`)
- increment-009 correction + orchestrator gate line: ✓ (packet + this record)
