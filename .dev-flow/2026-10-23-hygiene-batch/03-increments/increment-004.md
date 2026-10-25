# Increment 004 — US-Q2-001 · `Q2-csv ingestion limits + the refusal toast (lane L2b: import_csv, screens/home)`

> **Artifact language.** Canonical **English scaffold**; generated in the batch's language.
> **Owed in.** `core` ✓ · `full` ✓ · **packet home:** `.dev-flow/2026-10-23-hygiene-batch/03-increments/increment-004.md`

| Field | Value |
|---|---|
| Batch | `2026-10-23-hygiene-batch` |
| Increment | `004` |
| Lane (if the batch forked) | `L2b` · `import_csv` / `screens/home` (forked from L2 at ruling R7, ledger .9) |
| Requirement(s) | `US-Q2-001 · HLR-Q2.2 · HLR-Q2.3 (verify-and-pin, m6) · LLR-Q2.2.1 · LLR-Q2.3.1 (census re-run)` |
| Acceptance | `AT-113` (CSV caps) · `AT-114` (toast through the RUNNING home screen — GREEN at this gate, review m5) · mutants `M-Q2-3`, `M-Q2-5` |
| Agent | `software-dev` (lane L2b worker) |
| Date | `2026-10-23` |

---

## 1 · What changed

BLUF: the CSV import read is capped and the refusal reason reaches the operator.
`mapper/import_csv.py` routes the operator-selected file through the frozen D2 reader —
`MAX_FILE_BYTES` (4 MiB) with the stat re-checked on the read bytes, plus the
`BINARY_PROBE_BYTES` (8 KiB) NUL probe — replacing the unbounded `path.read_text` at the old
line 39. `mapper/screens/home.py`'s CSV-import toast now has the ruling-R7 shape: a TYPED
refusal (`MapStoreError` family — here `osopen.ContentReadError`, see §6) shows the
refusal's own path-free message (`str(e)`), so the reason reaches the operator; the generic
branch keeps `type(e).__name__` for arbitrary `OSError`s. Wording only — no new module
edges (the screen already imported `mapper.store`; `ContentReadError` joins its existing
osopen allow-list entry). The four arms authored in L2a as EXPECTED RED are GREEN at this
gate, observed through the running home screen (`test_at_114_csv_refusal_toast_shows_the_reason`
asserts the toast text, review m5). This increment also carries the L2b-gate revision of
L2a deliverables forced by pre-existing pins (§5): the S1 disposition revision
(`mapper/diff.py` + `mapper/store.py`), and the reader's universal-newline parity fix
(`mapper/osopen.py`) with its docstring sweep (`tests/test_ingestion_limits.py`).

---

## 2 · Files modified

**The budget counts SOURCE files only. Tests are not capped. Product docs and `.dev-flow/**` are outside the count.**

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/import_csv.py` | source | `HLR-Q2.2 · LLR-Q2.2.1` | the CSV read routes through `read_capped(path, MAX_FILE_BYTES)`; typed path-free refusals |
| `mapper/screens/home.py` | source | `HLR-Q2.2 · ledger .9 · ruling R7 (F-UX-1)` | the CSV toast's typed branch shows `str(e)`; generic branch unchanged; wording only |
| `mapper/diff.py` | source | `HLR-Q2.1` · `LLR-Q2.1.2` (via the store edge) · S1 (ruling R9) — disposition revised at this gate | L2b-gate revision: `git show` capture back on the `subprocess.run` seam pinned by `tests/test_inc9h.py`; the byte cap refuses oversized captured text in `store._capped_side_graph` |
| `mapper/store.py` | source | `HLR-Q2.1` · `LLR-Q2.1.1/.1.2/.1.3` · S1 (ruling R9) — acceptance bound | `_capped_side_graph` gains the byte-length refusal on captured diff-side texts |
| `mapper/osopen.py` | source | `LLR-Q2.1.1 parity · the hero-pin repair` | `read_capped` reproduces universal-newline semantics (see §5) |
| `tests/test_ingestion_limits.py` | test | `AT-109…AT-114` · `LLR-Q2.1.1/.1.2/.1.3` · `LLR-Q2.2.1` | one docstring swept to the revised S1 mechanism (L2a's file, L2b's sweep — declared) |
| `tests/test_arch_osopen_callers.py` | test | `HLR-Q2.1` (ledger .6) · `HLR-Q2.2` · `LLR-Q2.2.1` (the bounded reader the two new allow-list entries import) · `LED-2026-10-23-hygiene-batch.6/.9` · `R-015` | allow-list gains `import_csv.py` and `screens/home.py` in the SAME landing as their first osopen imports (B-44) |
| `tests/test_diff.py` | test | `LLR-Q2.1.2` (diff-side refusal) · inc004-F1 (the review-findings follow-up below) · S1 seam | NEW arm `test_git_diff_undecodable_head_object_returns_none_quietly` + the inc9h seam-pin re-verification; landed in the follow-up commit `a860a27` — row added at the close gate (test file, no re-review owed; PLAN.md declares the addition) |

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 4** (this increment's own deliverables: `import_csv.py`, `screens/home.py`) |
| Test files | 3 (uncapped) |
| Doc files | 0 (outside the count) |

- ⚠ **The three additional source files** (`diff.py`, `store.py`, `osopen.py`) are NOT new
  L2b scope: they carry the L2b-gate revision of L2a deliverables (§5), forced by
  pre-existing pins outside the lane's edit set. The lane's UNION of touched source files
  is `{store, diff, osopen, import_csv, home}` = exactly the C-52 L2 set (L2a 3 + L2b 2).
  Amending the committed L2a increment was not an option (no history mutation), so the
  revision rides here, declared.

---

## 3 · How to test

```bash
# the full shared file — all 20 arms green (the four L2b arms now included):
env -u NO_COLOR -u TERM python -B -m pytest -q -p no:cacheprovider \
  tests/test_ingestion_limits.py tests/test_arch_osopen_callers.py
# home-screen behavioural pins (the cheap set) + csv/diff/store pins:
env -u NO_COLOR -u TERM python -B -m pytest -q -p no:cacheprovider \
  tests/test_app.py tests/test_keymap.py tests/test_inc9.py tests/test_inc9c.py \
  tests/test_inc9d.py tests/test_inc9e.py tests/test_inc9f.py tests/test_inc9g.py \
  tests/test_inc9h.py tests/test_inc9i.py tests/test_inc9m.py \
  tests/test_import_csv.py tests/test_diff.py tests/test_store.py
# device-name census pins (m6 / LLR-Q2.3.1):
env -u NO_COLOR -u TERM python -B -m pytest -q -p no:cacheprovider \
  tests/test_seed_safety.py tests/test_inc9n.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `test_csv_*` — cap+1 refuses naming the cap; cap−1 loads (≈323k distinct rows); NUL at byte 0 / at byte 8,191 refuse as binary; NUL past the probe window imports | 5 passed (2 were already green at L2a; 3 turned green here) |
| **B · black-box** | `core` · `full` | `AT-114` — the NUL-bearing CSV driven through the RUNNING home screen (`MapperApp` + `run_test`), the toast text asserted: `could not read CSV 'bom.csv': … NUL …`, file name shown, full path absent | 1 passed (GREEN at this gate, review m5) |
| **A · regression pin** | `core` · `full` | home-screen behavioural pins: 557 passed / 0 failed across `test_app`, `test_keymap`, `test_inc9*` (the cheap set); csv/diff/store pins 17 passed; device-name census pins (m6) 163 passed | all green |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | two — the M-Q2-3 probe shrink and the M-Q2-5 toast revert (below); plus the two move-asides |
| Instrument | project code: `evidence/l2b_move_aside.sh` and `evidence/mutate_l2b.py` (C-40 runner modeled on `mutate_l3.py`, tightened: an expected-RED arm that SURVIVES counts as bad), run by the lane worker on THIS worktree |
| Where it ran | **the wt-l2 worktree on branch `lane/l2`, run by the lane worker (sub-agent) — no other lane's tree** |
| Transcript | `evidence/l2b-move-aside-2026-10-23.txt`, `evidence/l2b-mutation-battery-2026-10-23.txt` |
| Restore proven by | **file hash returned to its pre-mutation value** — every before/after pair equal in the transcripts |
| Bytecode cache | run with `PYTHONDONTWRITEBYTECODE=1` (C-46) |
| Arms resolved at baseline | move-asides: 2 files × holding arms; battery: **2** resolved nodes (M-Q2-3, M-Q2-5) |
| Verdict granularity | per resolved node id, printed per arm |
| Arms that stayed GREEN | **none** |

Move-aside RED (C11 habit 1), per deliverable file:

| File moved aside | Holding arms | Result | Restore |
|---|---|---|---|
| `mapper/import_csv.py` | `tests/test_ingestion_limits.py` + `tests/test_import_csv.py` | RED — `ModuleNotFoundError: No module named 'mapper.import_csv'` (exit 2) | hash-equal ✓ |
| `mapper/screens/home.py` | `tests/test_ingestion_limits.py::test_at_114_csv_refusal_toast_shows_the_reason` + `tests/test_app.py` | RED — `ModuleNotFoundError: No module named 'mapper.screens.home'` (exit 4) | hash-equal ✓ |

| Field | Value |
|---|---|
| **RED counterfactual** | the move-asides above + the L2b RED gate below + the mutation battery — each made THIS increment's own assertions fail; transcripts at `evidence/l2b-move-aside-2026-10-23.txt` (sha256 8bc6c1a6…), `evidence/l2b-red-2026-10-23.txt` (sha256 a2ec6759…), `evidence/l2b-mutation-battery-2026-10-23.txt` (sha256 f6536e49…); restores hash-proven |

| Field | Value |
|---|---|
| **Mutation verdicts** | M-Q2-3 — `osopen.py` probe anchor `… in data[:probe]` → `… in data[:1]` (probe shrunk) · **KILLED** on `test_csv_nul_at_last_probe_byte_refuses_as_binary` (the byte-8,191 NUL loads under the shrunk probe → DID NOT RAISE) · M-Q2-5 — `home.py` toast `{refusal}` → `{type(refusal).__name__}` (type-name-only) · **KILLED** on `test_at_114_csv_refusal_toast_shows_the_reason` (the toast carries no "NUL" reason) · arms that stayed GREEN: **none** · runner: `evidence/mutate_l2b.py` (sha256 07dcfbaf…) · transcript sha256 f6536e49… |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| the L2b RED gate | the four arms on the L2a tree (caps absent, toast type-name-only) | 4 failed — `DID NOT RAISE` / empty toasts, `evidence/l2b-red-2026-10-23.txt` |
| the mutation runner | the two anchored mutants | per-arm `RED (KILLED)` verdicts; a SURVIVING arm would count bad (runner exit 1) |
| the toast-text arm as the M-Q2-5 oracle | the type-name-only mutant | the arm's `"NUL" in refusal[0]` assertion fails — verbatim in the battery transcript |
| the privacy grep | a planted address/home path through the SAME probes | both probes fired on the planted cases, `evidence/l2b-privacy-grep-2026-10-23.txt` |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 instruments, each shown RED (or fired) before its first PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the home-screen toast (observed through the running screen) | the intercepted `app.notify` text asserted: starts `could not read CSV 'bom.csv': `, contains `NUL` (the reason), contains no `str(tmp_path)` | `"could not read CSV 'bom.csv': file looks binary (NUL byte in the first 8192 bytes)"` — the refusal's own message, AT-114 green |
| the CSV refusal message (unit level) | `str(caught.value)` contains `str(MAX_FILE_BYTES)` (cap+1 arm) / `"binary"` (NUL arms) | both present, path-free |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts, each asserted against the emitted form |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED transcript | `.dev-flow/2026-10-23-hygiene-batch/evidence/l2b-red-2026-10-23.txt` | `a2ec6759322a58aab4cd52836abfe81f5304c1086b5d3abfe948b18cea886029` |
| GREEN transcript | `.dev-flow/2026-10-23-hygiene-batch/evidence/l2b-green-2026-10-23.txt` | `1faf228c36530b7468bd7f21b5e6da9ff867e6bb2555c0c70e2ab00b236759ce` |
| move-aside transcript | `.dev-flow/2026-10-23-hygiene-batch/evidence/l2b-move-aside-2026-10-23.txt` | `8bc6c1a6a75ec2d7715b0971a7f847738f34e72a65fc3437bfef4da0d67ae31d` |
| mutation battery transcript | `.dev-flow/2026-10-23-hygiene-batch/evidence/l2b-mutation-battery-2026-10-23.txt` | `f6536e4923321b080447a65c88028fa30958823f05b9de43fde2e45a377b89b2` |
| device-census transcript (m6) | `.dev-flow/2026-10-23-hygiene-batch/evidence/l2b-device-census-2026-10-23.txt` | `c5a333be8e1b22d55e52b0ad79fdaaab78e90d8d9dd5d58982c910c8c5fe99b4` |
| privacy grep transcript | `.dev-flow/2026-10-23-hygiene-batch/evidence/l2b-privacy-grep-2026-10-23.txt` | `336bbfabc8e3babb2c319390041516ffff6fecc66e829887578f88ca83a59071` |
| mutation runner | `.dev-flow/2026-10-23-hygiene-batch/evidence/mutate_l2b.py` | `07dcfbaf8042619db3f68962fd009ca3fcb6e5c70d25deeb5b2b1be6dca62f2d` |
| move-aside runner | `.dev-flow/2026-10-23-hygiene-batch/evidence/l2b_move_aside.sh` | `bea5d3937e11abaeb66c7fa44bc2a180a13ae569143fd803ae256186d82c87cc` |

| Field | Value |
|---|---|
| **Evidence files** | 8 artifacts, each at the declared home and cited with the digest of its stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — the toast's typed branch assumes the typed refusals' messages are authored path-free forever (C6/LLR-Q2.2.1); and the allow-list assumes no third reader importer |
| If the result is an ABSENCE, what made the search wide enough | the inc9c census walks every `notify(` call in the product ASTs; the arch census walks every module's imports — both derived, not sampled |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `tests/test_inc9c.py::test_inc9c_sec_f1_census_no_notify_interpolates_a_raw_exception_or_path` (guards the conclusion "no toast paints a raw exception/path") + the arch allow-list arm |
| Conjunctive criteria: one mutation per conjunct | M-Q2-3 kills the probe-window conjunct (byte-8,191 arm); the byte-0 arm covers the probe-existence conjunct; the cap conjunct is covered by `test_csv_at_file_cap_plus_1_refuses` (a cap removal lets the 4 MiB+ file through → RED) |
| Synthetic instance of the absent case | the M-Q2-5 mutant is the synthetic type-name-only toast; the planted privacy-grep inputs are the synthetic leaks |

### Reverse census — trigger family B, and A3

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rl "read_capped\|ContentReadError\|preview_csv" tests/` | `tests/test_ingestion_limits.py` (this lane's file) + `tests/test_import_csv.py` (asserts `preview_csv` behaviour — re-run green) |
| B2 file moved on disk | the move-aside protocol above | the only consumers are the holding arms run |
| B3 byte-identical golden captures this source | `grep -rl "import_csv\|home" tests/goldens/` | no hits pinning these sources |
| B4 artifact produced here is consumed elsewhere | `grep -rn "preview_csv" mapper/` | `screens/home.py` (the only caller — the toast site) and `screens/import_preview.py` renders the graph — unchanged contracts |
| A3 interface consumed by another module changed | `preview_csv(path: Path) -> Graph` | unchanged — same signature, same `Graph()`-on-empty contract; only the read path gained caps |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run of B1 · B2 · B3 · B4 · A3, each with its command and its verdict — no foreign consumer broken |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| the L2b-gate revision of L2a deliverables | every pre-existing pin touching the L2a-touched seams | the L2b pin sweep (`tests/test_app.py … tests/test_inc9m.py`, `test_import_csv.py`, `test_diff.py`, `test_store.py`) BEFORE the revision | 3 pins failed (hero, inc9h, inc9c) | 3 source files revised + 1 test docstring swept | none — each revision maps to a named pin |

| Field | Value |
|---|---|
| **Correction population** | 1 correction population (the pin sweep), enumerated before the first revision site was edited |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|---------------------|
| the Popen-based bounded capture (increment-003's first S1 realization) | 0 `Popen` hits in `mapper/diff.py` | yes | `grep -n Popen mapper/diff.py` — empty; the docstring of `test_diff_side_oversize_head_yields_none` swept to the accepted bound |

### Signed-balance test ledger

`post = base − deleted + added` → no test added or deleted in L2b (it owns no test file);
`tests/test_ingestion_limits.py` +20 arms landed in increment-003; the arch allow-list +2
entries here → `post = base + 1 file` ✓ reconciles

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer + security-reviewer + qa (UX lens, AT-114) — Kimi K3 subagent executing agents/code-reviewer.md + agents/security-reviewer.md · OK-with-notes, 0 BLOCKER / 1 MAJOR / 2 MINOR · caps, path-free typed refusals and the AT-114 toast verified live through the running screen via Pilot plus hostile inputs; digests 8/8 match; 2 reviewer-chosen mutants KILLED with hash-proven restores; 5 source files with the over-4 reason declared in §2; F1 MAJOR: diff.py _show dropped the pre-increment UnicodeDecodeError guard (mapper/diff.py:46) — decode behind the pinned seam owed to author; F2 MINOR: non-UTF-8 CSV refusal untyped; F3 MINOR: transient unreproduced test flake recorded — full report .dev-flow/2026-10-23-hygiene-batch/evidence/review-inc004.md` |

---

## 5 · Risks

- **S1 (PDR security finding, ruling R9) — DISPOSITION REVISED at the L2b gate: ACCEPTED
  WITH RATIONALE.** Increment-003 recorded BOUND (streamed `git show` via `Popen`). The L2b
  pin sweep found `tests/test_inc9h.py::test_inc9h_sec_f5_git_show_in_diff_runs_in_the_no_prompt_english_environment`
  — a pre-existing pin outside the lane's edit set that asserts the `git show` invocation
  goes through the `subprocess.run` seam (env-seam guard); bounding requires `Popen`, which
  breaks the pin. Revising under the ruling's own either/or, the gate ACCEPTS the finding
  with rationale: the capture stays on the pinned seam; the map cap is enforced on the
  captured texts instead (`_capped_side_graph` refuses over-8 MiB HEAD texts → `None`), so
  no capped byte ever reaches a parser or an index; the accepted residual is one transient
  buffer of a `git` object from the operator's own repository — the same class of exposure
  as running `git show` in a terminal, rated LOW by the PDR. One-line justification:
  *bounding broke a load-bearing pin, and the cap the stream would enforce is enforced one
  call later with zero interface change.* Asserted by `test_diff_side_oversize_head_yields_none`
  (still green). The increment-003 record stands corrected by this entry; the DDR reads both.
- **Reader newline parity (found by the same pin sweep).** `read_capped`'s binary read
  kept `\r\n`, breaking the `_mmd_hash` sync check (false "map out of sync" load warning)
  and with it `tests/test_app.py::test_home_screen_renders_hero_when_maps_exist`. The
  reader now reproduces the universal-newline semantics of the text-mode reads it
  replaces. Re-verified: hero pin green; all 20 ingestion arms re-green.
- **The inc9c census and the typed toast.** `tests/test_inc9c.py`'s notify census flags any
  toast interpolating a raw exception name; its declared-carry registry
  (`LEAK_EXCEPTIONS`) lives in that file, which the lane may not edit. The site binds the
  typed refusal as `refusal` (outside the heuristic name set) with an inline comment
  declaring the same safety class as the three existing carries (typed, authored,
  path-free). A registry entry for the site was expected at the trunk join — §6;
  discharged there as impossible by construction (F-SD-1): the inline declaration
  is the carry — commit `78d51a2`.
- **Contamination check (CAUTION clause).** `git status` before this packet: only the
  lane's own files (L2b deliverables + the declared L2a revision) — **no foreign edits
  found in wt-l2**; no incident to declare.

---

## 6 · Pending items / spec deviations

- **CSV refusals are typed `osopen.ContentReadError`, not `MapStoreError`** (carried from
  increment-003 §6 — restated here as the L2b half): R-015 forbids `import_csv → store`, so
  the reader's own typed error is the refusal family for CSV; it subclasses `OSError`,
  names the limit, and the toast's typed branch shows `str(e)`. HLR-Q2.2's "MapStoreError
  family" wording wants a close-time reconciliation (or a trunk decision to move the
  refusal base type).
- **`tests/test_inc9c.py` `LEAK_EXCEPTIONS` — settled at the trunk join (commit `78d51a2`, F-SD-1):**
  no registry entry for the new toast site (`mapper/screens/home.py`, the typed
  CSV-refusal branch) is possible by construction — `_leaky` never flags `refusal`, so
  the key would redden the staleness check on arrival; the site's inline declaration is
  the carry, and the comment there says so.
- **`store.py` imports six osopen names** (carried from increment-003 §6 — the DDR
  reconciles the ARQ "ONE name" phrasing against the D2 exposure).
- **The L2b increment's commit touches 5 source files, 2 of them L2b's own** — the other 3
  are the declared L2a revision (§5); the lane union equals the C-52 L2 set exactly.
- Prescan cost watch-item (+3.54 s on the 12k-node perf shape, measured at the L2a gate)
  stands; backlog candidate if it ever matters.

---

## 7 · Suggested next task

**Lane close / DDR** — the lanes join: the DDR re-reads the S1 revision (increment-003 §5
vs increment-004 §5), the `ContentReadError`-vs-`MapStoreError` reconciliation, the osopen
import-name census, and the trunk-owned `LEAK_EXCEPTIONS` entry; then batch validation
(AT-109…114 through the full suite).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 2 / 4 own deliverables + 3 declared L2a-revision files; lane union = the C-52 L2 set — `SOURCE files` table and its ⚠ note |
| 2 | Tests written in this same increment | all | ✓ | L2b owns no test file by design (PDR §B row 6); the four L2b arms authored in increment-003 turn green here |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `test_csv_*` unit arms green (`l2b-green-…` run 1: 25 passed) |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | L2b RED gate (`l2b-red-…`, sha256 a2ec6759…, 4 failed); move-asides (`l2b-move-aside-…`, 8bc6c1a6…); battery (`l2b-mutation-battery-…`, f6536e49…) — restores hash-proven |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 5 probes in the Reverse census table |
| 6 | `code-reviewer` passed — declared in **§4b** | `core` · `full` | ⚠ | §4b = `pending — orchestrator schedules` (runtime has no reviewer sub-agents; PLAN.md gate-notices records the orchestrator holds the gates) |
| 7 | No file from another lane touched | all | ✓ | `git status` shows only L2 files; the arch/inc9c records are declared same-landing/trunk-owed amendments, not other lanes' files |
| 8 | Frozen interfaces untouched (or returned to the trunk) | all | ✓ | D1/D2 untouched; `preview_csv`/`git_diff`/`MapStore.load` signatures unchanged |
| 9 | Coverage claims verified **on disk**, not from intent | all | ✓ | all §4 numbers from the transcripts' actual outputs |
| 10 | Load-bearing emptiness declared, with its synthetic instance (C-55) | all | ✓ | typed-message path-freeness assumption + M-Q2-5 synthetic + planted privacy inputs |
| 11 | **Mutation verdicts** declared — per arm | all | ✓ | 2/2 KILLED (M-Q2-3, M-Q2-5), none GREEN, per-arm in the Mutation verdicts cell |
| 12 | **Instrument RED-proof** declared | all | ✓ | 4 instruments, each RED/fired before its PASS was believed |
| 13 | **Correction population** declared | all | ✓ | 1 population (the L2b pin sweep), enumerated before the first revision |
| 14 | **Emitted-form assertion** declared | all | ✓ | the observed toast text + the unit-level refusal messages asserted verbatim |
| 15 | **Independent review** names somebody | all | ⚠ | `pending — orchestrator schedules` (the only form this runtime offers) |
| 16 | **Evidence files** declared | all | ✓ | 8 artifacts, paths + stored-byte digests in the Evidence files table |

---

## Review-findings follow-up — 2026-10-24 (independent review `evidence/review-inc004.md` — code-reviewer + security-reviewer + UX lens)

**inc004-F1 (MAJOR — `_show` dropped the pre-increment `UnicodeDecodeError` guard) — DISPOSITION: fixed.**
- Requirement it serves: `git_diff`'s None-on-error contract (`mapper/diff.py:23-28`) on the `subprocess.run` seam pinned by `tests/test_inc9h.py::…sec_f5…` (INC9G-SEC-F5) — the same seam the S1 revision above accepts.
- Fix (inside the L2b set): `mapper/diff.py::_show` — `text=True, encoding="utf-8"` removed from the pinned invocation (the pin asserts argv+env only, verified green after the change); the capture is bytes, and the decode happens behind the seam under the restored `except UnicodeDecodeError → None` guard. Source files this follow-up: 2 (`mapper/diff.py`, `mapper/osopen.py` — the inc004-F2 fix below) of ≤4.
- Asserting test (RED → GREEN, C11): `tests/test_diff.py::test_git_diff_undecodable_head_object_returns_none_quietly` — a real git repo whose HEAD `.mmd` is latin-1 bytes: `git_diff` returns None WITHOUT raising and without the reader-thread exception surfacing (the arm carries `@pytest.mark.filterwarnings("error::pytest.PytestUnhandledThreadExceptionWarning")`, which makes the Windows manifestation — the swallowed thread decode failure the reviewer observed — fatal, and on POSIX the raw `UnicodeDecodeError` propagation fails the call directly). The first test draft asserted only `is None`, which passed on the broken capture because the Windows reader thread swallows the error and `stdout` comes back `None` "accidentally" — the filterwarnings mark is what makes the arm discriminating on this platform.
- Asserting mutant (executed 2026-10-24, restore hash-proven): the `except UnicodeDecodeError` limb dropped (unguarded `result.stdout.decode`) → the arm RED; before/after sha256 of `mapper/diff.py` both `55bbed06…cc6a2`.
- Evidence (sha256 of stored bytes, account name redacted to `<user>` per A-110): `evidence/fu-inc004-f1-decode-guard-red-2026-10-24.txt` (`c39e9e44…6ddd3`, 1 failed, `exit=1`), `evidence/fu-inc004-f1-decode-guard-green-2026-10-24.txt` (`70063e23…45c0`, 5 passed, `exit=0`), `evidence/fu-inc004-f1-decode-guard-mutant-2026-10-24.txt` (`afb20c8c…324bc`, 1 failed, `exit=1`).

**inc004-F2 (MINOR — non-UTF-8 CSV refusal was untyped; the operator saw only the exception type name) — DISPOSITION: fixed (stays inside L2b's file set, so no BACKLOG entry is owed).**
- Requirement it serves: LLR-Q2.2.1's typed, authored, path-free refusal family + AT-114 (the reason reaches the operator).
- Fix: `mapper/osopen.py::read_capped` — bytes that pass the byte cap and the NUL probe but are not valid UTF-8 now refuse with the typed authored constant `ContentReadError("file is not UTF-8 text")` instead of a bare `UnicodeDecodeError`. `mapper/osopen.py` is one of the five files of this increment's set. `MapStore.load` already maps `ContentReadError` to its typed `MapStoreError` (the first except clause), so map reads keep their refusal family; the home screen's typed toast branch now shows the reason sentence for non-UTF-8 CSVs too.
- Asserting test (RED → GREEN, C11): `tests/test_ingestion_limits.py::test_csv_non_utf8_refuses_typed_naming_the_reason` — a latin-1 CSV through `preview_csv` refuses typed, names "UTF-8", carries no path.
- Asserting mutant (executed 2026-10-24, restore hash-proven): the `except UnicodeDecodeError` limb dropped (bare decode) → the arm RED; before/after sha256 of `mapper/osopen.py` both `58153cc4…c200579`.
- Evidence (sha256 of stored bytes, redacted): `evidence/fu-inc004-f2-utf8-refusal-red-2026-10-24.txt` (`397e2a05…63bac`, 1 failed, `exit=1` — bare `UnicodeDecodeError` out of `preview_csv`), `evidence/fu-inc004-f2-utf8-refusal-green-2026-10-24.txt` (`39a33614…44e27`, 7 passed CSV arms, `exit=0`), `evidence/fu-inc004-f2-utf8-refusal-mutant-2026-10-24.txt` (`f4dcdb99…0dc87`, 1 failed, `exit=1`).

**inc004-F3 (MINOR — two ingestion arms failed once each during the review, unreproduced) — DISPOSITION: accepted with reason; not chased.**
`test_at_113_edge_count_cap_plus_1_refuses` and `test_at_110_depth_64_parses` each failed once in runs interleaved with the reviewer's mutant arms and passed in every subsequent run (the reviewer's own 5× single / paired / 2× full-file re-runs, both L2a/L2b packets' transcripts, and this follow-up's final targeted run — 56 passed, `fu-followup-targeted-2026-10-24.txt`, sha256 `717cdae8…518f58`) with zero source change between occurrences. Consistent with the reviewer's environment-noise (Windows AV/locking) suspicion. Recorded so the DDR does not mistake a future recurrence for a regression.

**Follow-up verification sweep (all fixes landed): the six orchestrator-named test files plus the inc9h seam pin, one run, never the full suite** — 56 passed, `exit=0`: `evidence/fu-followup-targeted-2026-10-24.txt` (sha256 `717cdae8…518f58`). The seam pin `test_inc9h_sec_f5…` is green on the revised `_show`, confirming the inc9h justification in §5 stands.
