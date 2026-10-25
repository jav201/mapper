# Increment 003 — US-Q2-001 · `Q2-core ingestion limits (lane L2a: store, diff, osopen)`

> **Artifact language.** Canonical **English scaffold**; generated in the batch's language.
> **Owed in.** `core` ✓ · `full` ✓ · **packet home:** `.dev-flow/2026-10-23-hygiene-batch/03-increments/increment-003.md`

| Field | Value |
|---|---|
| Batch | `2026-10-23-hygiene-batch` |
| Increment | `003` |
| Lane (if the batch forked) | `L2a` · `store` / `diff` / `osopen` (forked from L2 at ruling R7, ledger .9) |
| Requirement(s) | `US-Q2-001 · HLR-Q2.1, Q2.3 · LLR-Q2.1.1, Q2.1.2, Q2.1.3 (ruling R1, ledger .1/.5) · LLR-Q2.2.1 (reader half) · LLR-Q2.3.1 (census re-run, L2b ledger)` |
| Acceptance | `AT-109` (bytes) · `AT-110` (depth) · `AT-111` (anchors/aliases) · `AT-112` (nodes) · `AT-113` (edges, synthetic surface) · `AT-114` screen arm AUTHORED, expected RED at this gate (PDR §B row 6) · unit layer-0 = `tests/test_ingestion_limits.py` |
| Agent | `software-dev` (lane L2a worker) |
| Date | `2026-10-23` |

---

## 1 · What changed

BLUF: map-file loading is capped and refuses loudly. `mapper/osopen.py` ships the frozen
**D2** surface: `MAX_MAP_BYTES` (8 MiB), `MAX_DEPTH` (64), `MAX_NODES`/`MAX_EDGES`
(100,000/100,000), `MAX_FILE_BYTES` (4 MiB), `BINARY_PROBE_BYTES` (8 KiB), plus the bounded
reader **`read_capped`** (stat ≤ cap, then a capped `read(cap + 1)` re-read — never a full
read before the re-check, m4's adopted shape) and the typed, path-free `ContentReadError`.
`mapper/store.py` routes both map-file reads through the reader, prescans the sidecar as an
iterative YAML event stream before `yaml.safe_load` (anchors/aliases refused naming the
anchor; nesting over 64 refused; a 10,000-deep bomb is a typed refusal in milliseconds,
never `RecursionError`), and refuses graphs over the count caps — every refusal a typed
`MapStoreError` naming the LIMIT and the map id, never a path (C6).
`mapper/diff.py` gets the same caps through the existing `diff → store` edge only (ruling
R8: no `diff → osopen` import), and its `git show` capture is now **bounded** (PDR
security finding **S1 discharged here, ruling R9: BOUND** — see §5). `MapStore.load`'s
signature is unchanged; the `None`-on-error diff contract survives (a capped-out diff-side
load yields `None`). `tests/test_arch_osopen_callers.py`'s derived allow-list gains
`store.py` in the SAME landing as the first reader import (B-44 discipline, ledger .6).

---

## 2 · Files modified

**The budget counts SOURCE files only. Tests are not capped. Product docs and `.dev-flow/**` are outside the count.**

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/osopen.py` | source | `HLR-Q2.1 · HLR-Q2.2 · LLR-Q2.1.1 · LLR-Q2.2.1` | D2 frozen constants; `read_capped` bounded reader; `ContentReadError` (typed, path-free) |
| `mapper/store.py` | source | `HLR-Q2.1 · LLR-Q2.1.1/.1.2/.1.3` | reads routed through the reader; `_prescan_sidecar`; `_check_count_caps`; `_capped_side_graph` (the diff-side door) |
| `mapper/diff.py` | source | `HLR-Q2.1 · LLR-Q2.1.2 (via the store edge) · S1 (ruling R9)` | bounded `git show` capture (stream, abort past `MAX_MAP_BYTES + 1`); old-graph build through `store._capped_side_graph`; `yaml` import leaves diff |
| `tests/test_ingestion_limits.py` | test | `AT-109…AT-114 · LLR-Q2.1.1/.1.2/.1.3 · LLR-Q2.2.1` | NEW — 20 arms (16 L2a-green at this gate + 4 authored, expected RED until L2b) |
| `tests/test_arch_osopen_callers.py` | test | `HLR-Q2.1` (ledger .6 — osopen joins the L2 set) · `LLR-Q2.2.1` (reader half — the allow-list pins `store.py`'s first bounded-reader import) · `LED-2026-10-23-hygiene-batch.6` · `R-015` | `ALLOWED_OUTSIDE_APP` gains `store.py` (same landing as the first reader import) |
| `tests/test_repair_sidecar.py` | test | `LLR-Q2.1.2` (the typed prescan refusal the arms now assert) · ruling R10 · `LED-2026-10-23-hygiene-batch.14` (the cross-batch follow-up below) | the three `LLR-N13.1.7` arms amended in place to assert the typed prescan refusal (names unchanged, value-leak bounds kept); landed in `37a8175` — row added at the close gate (test file, no re-review owed; PLAN.md declares the addition) |

| Count | Value |
|---|---|
| **SOURCE files** | **3 / 4** |
| Test files | 3 (uncapped) |
| Doc files | 0 (outside the count) |

- ✗ If a file belongs to another lane's file set, stop: lanes may not share a file. — none touched outside the L2a set (the arch test amendment is the declared same-landing census pin; L2b adds its own two entries in increment-004).

---

## 3 · How to test

```bash
# L2a arms (the four L2b-pending arms deselected — declared expected RED here):
env -u NO_COLOR -u TERM python -B -m pytest -q -p no:cacheprovider \
  tests/test_ingestion_limits.py tests/test_arch_osopen_callers.py \
  --deselect tests/test_ingestion_limits.py::test_csv_at_file_cap_plus_1_refuses \
  --deselect tests/test_ingestion_limits.py::test_csv_nul_at_byte_0_refuses_as_binary \
  --deselect tests/test_ingestion_limits.py::test_csv_nul_at_last_probe_byte_refuses_as_binary \
  --deselect tests/test_ingestion_limits.py::test_at_114_csv_refusal_toast_shows_the_reason
# pins:
env -u NO_COLOR -u TERM python -B -m pytest -q -p no:cacheprovider \
  tests/test_diff.py tests/test_import_csv.py tests/test_store.py \
  tests/test_repair_store_boundary.py tests/test_csv_safety_store.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `tests/test_ingestion_limits.py` byte-cap (stat / TOCTOU / cap−1), prescan (anchor / alias / depth-64 / depth-65 / 10,000-deep < 5 s), count caps (nodes cap+1 / edges cap+1 synthetic / at-cap), diff (clean-HEAD positive control / anchor-HEAD → None / oversize-HEAD → None) | 16 passed |
| **A · white-box** | `core` · `full` | privacy/path arms inside every refusal arm (`str(tmp_path) not in msg`, limit + map id in msg) + `tests/test_arch_osopen_callers.py` | 5 passed (arch file) |
| **B · black-box** | `core` · `full` | `AT-114` screen arm — **AUTHORED, EXPECTED RED at this gate** (PDR §B row 6: green only after L2b lands the toast wording); verified RED in the l2a-red transcript | declared RED |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | three, one per deliverable file — see the move-aside table and the mutation battery below |
| Instrument | project code: `evidence/l2a_move_aside.sh` (hash before/after, restore proven) and `evidence/mutate_l2a.py` (C-40 runner modeled on `mutate_l3.py`), both run by the lane worker on THIS worktree |
| Where it ran | **the wt-l2 worktree on branch `lane/l2`, run by the lane worker (sub-agent) — no other lane's tree** |
| Transcript | `evidence/l2a-move-aside-2026-10-23.txt`, `evidence/l2a-mutation-battery-2026-10-23.txt` |
| Restore proven by | **file hash returned to its pre-mutation value** — every before/after pair equal, printed in the transcripts |
| Bytecode cache | run with `PYTHONDONTWRITEBYTECODE=1` (C-46) |
| Arms resolved at baseline | move-asides: 3 files × their holding arms; battery: **4** resolved nodes (M-Q2-1 ×2, M-Q2-2, M-Q2-4) |
| Verdict granularity | per resolved node id, printed per arm |
| Arms that stayed GREEN | **none** — every counterfactual went RED |

Move-aside RED (C11 habit 1), per deliverable file:

| File moved aside | Holding arms | Result | Restore |
|---|---|---|---|
| `mapper/store.py` | `tests/test_ingestion_limits.py` + `tests/test_store.py` | RED — `ModuleNotFoundError: No module named 'mapper.store'` (exit 4) | hash-equal ✓ |
| `mapper/diff.py` | `tests/test_ingestion_limits.py::test_diff_side_clean_head_still_diffs` + `tests/test_diff.py` | RED — `ModuleNotFoundError: No module named 'mapper.diff'` (exit 4) | hash-equal ✓ |
| `mapper/osopen.py` | `tests/test_arch_osopen_callers.py` + `tests/test_ingestion_limits.py` | RED — `ModuleNotFoundError: No module named 'mapper.osopen'` (exit 4) | hash-equal ✓ |

| Field | Value |
|---|---|
| **RED counterfactual** | the move-asides above + the mutation battery below — each made THIS increment's own new assertions fail; transcripts at `evidence/l2a-move-aside-2026-10-23.txt` (sha256 ed12f777e4fb…) and `evidence/l2a-mutation-battery-2026-10-23.txt` (sha256 4a2ebc9c78d0…); restore digests printed per arm, all equal to their pre-mutation digests |

| Field | Value |
|---|---|
| **Mutation verdicts** | M-Q2-1 — `store.py` event-loop anchor `for event in yaml.parse(yml_text):` → `for event in []:` (prescan bypassed) · **KILLED** on `test_at_111_anchor_refused_names_anchor_and_map` AND `test_at_110_depth_65_refuses_naming_depth_limit` (DID NOT RAISE) · M-Q2-2 — `osopen.py` re-check `if len(data) > cap:` → `if False and …` · **KILLED** on `test_at_109_byte_cap_grow_between_stat_and_read_refuses` · M-Q2-4 — `store.py` node-cap comparison `> MAX_NODES` → `> MAX_NODES + 1` · **KILLED** on `test_at_112_node_count_cap_plus_1_refuses` · arms that stayed GREEN: **none** · runner: `evidence/mutate_l2a.py` (sha256 c2e10049d1db…) · transcript sha256 4a2ebc9c78d0… |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| the test arms themselves | run on the base tree at the RED gate | `ImportError: cannot import name 'BINARY_PROBE_BYTES' from 'mapper.osopen'` — collection error, `evidence/l2a-red-2026-10-23.txt` |
| the arch allow-list (amended early, B-44) | the amended `ALLOWED_OUTSIDE_APP` before any importer existed | `AssertionError … Right contains 1 more item: {'store.py': …}` — RED at the RED gate, same transcript |
| the mutation runner | a surviving mutant is the known-bad input; runner exit mapping | per-arm `RED (KILLED)` / `GREEN (SURVIVED)` / `CRASH/BAD` verdicts printed; first capture's hang was caught (see §5) |
| the privacy grep | a planted address/path through the SAME probe | fired on `someone@example.com` and `C:\Users\<user>\file.txt`, `evidence/l2a-privacy-grep-2026-10-23.txt` |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 instruments, each shown RED (or fired) before its first PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the refusal message strings (the operator-facing emitted form) | `str(caught.value)` asserted per arm: `str(MAX_MAP_BYTES)`/`"depth limit"`/`"'x'"`/`"nodes"`/`str(MAX_NODES)`/`"edges"`/`str(MAX_EDGES)` present; `str(tmp_path)` absent | all arms green — every refusal names the limit + map id and carries no path |
| the typed diff-side refusal (emitted as `None`) | `git_diff(...) is None` on anchor-HEAD and oversize-HEAD; `is not None` on clean-HEAD | `None`, `None`, `DiffResult` — exactly the None-on-error contract |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts (refusal message text; the diff-side None), each asserted against the emitted form |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED transcript | `.dev-flow/2026-10-23-hygiene-batch/evidence/l2a-red-2026-10-23.txt` | `f622f79c63eca92f16456ba6287bc78ffe2c12eb74bed17ed0126b9759968d78` |
| GREEN transcript | `.dev-flow/2026-10-23-hygiene-batch/evidence/l2a-green-2026-10-23.txt` | `89494620ac40e3c2b3a94c03ae0e891bc03bb42060342cbaad79d7a67986e392` |
| move-aside transcript | `.dev-flow/2026-10-23-hygiene-batch/evidence/l2a-move-aside-2026-10-23.txt` | `ed12f777e4fb0b73488900922b58a4c17703c149ce7ef3def03d3a1e8fa691ea` |
| mutation battery transcript | `.dev-flow/2026-10-23-hygiene-batch/evidence/l2a-mutation-battery-2026-10-23.txt` | `4a2ebc9c78d097c243307f9735c1431b4ab6c402faa015e94391ff90f85306f7` |
| prescan cost transcript | `.dev-flow/2026-10-23-hygiene-batch/evidence/l2a-prescan-cost-2026-10-23.txt` | `346297453a1539442a678c2b0d7ead10a66f7242b8b5aa8738270623c0e13896` |
| privacy grep transcript | `.dev-flow/2026-10-23-hygiene-batch/evidence/l2a-privacy-grep-2026-10-23.txt` | `260a51e2102e7b44463d43b4beb89eb7317dc29f38adc975f32760ae0a4958b9` |
| mutation runner | `.dev-flow/2026-10-23-hygiene-batch/evidence/mutate_l2a.py` | `c2e10049d1db5b3a52c6f6ea531b8b13ce84b44cc4547f3a7b6e2365fc641d45` |
| move-aside runner | `.dev-flow/2026-10-23-hygiene-batch/evidence/l2a_move_aside.sh` | `bf0879b8489d8ad776af159868b4f0e51e11257a307b734dff2120f4b3471c47` |
| prescan probe script | `.dev-flow/2026-10-23-hygiene-batch/evidence/l2a_prescan_cost.py` | `c09352f052b11782bc1ebd3cf642eda46ae9fafe5d5063918b69b8bf84540710` |

| Field | Value |
|---|---|
| **Evidence files** | 8 artifacts, each at the declared home and cited with the digest of its stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — (1) the EDGES cap is unreachable through `load` (`mermaid.parse` builds trees: a child may not repeat a parent, so edges ≤ nodes − 1 ≤ nodes); (2) no third importer of the osopen reader exists outside `{store, import_csv}` |
| If the result is an ABSENCE, what made the search wide enough | (1) the structural argument + the synthetic-graph arm; (2) the AST-derived census walks every `mapper/**/*.py` — it cannot miss a file, and it fails LOUD (assert `seen == ALLOWED_OUTSIDE_APP`) |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `tests/test_arch_osopen_callers.py::test_outside_app_only_the_allowed_names_are_imported_from_osopen` (the allow-list arm — the conclusion it protects: the reader has exactly two importers) |
| Conjunctive criteria: one mutation per conjunct | the byte cap is conjunctive (stat limb + re-check limb): M-Q2-2 kills the re-check limb; the stat limb is covered by `test_at_109_byte_cap_stat_refuses_and_names_limit_and_map` (reworded 2026-10-24 per review inc003-F3: the stat limb is a FAST PATH — refuse an oversize file without opening it, and refuse one that shrank between stat and read; the capped re-read re-check is the enforcing conjunct for size, killed by M-Q2-2. Deleting the stat check alone does NOT redden the stat arm — the re-check still refuses the 8 MiB+ file — so the original "any removal → RED" wording was not derivable) |
| Synthetic instance of the absent case | (1) `test_at_113_edge_count_cap_plus_1_refuses` builds a 2-node / 100,001-edge Graph and drives `_check_count_caps` directly; (2) the M-Q2-4 mutant IS a synthetic third state of the count comparison |

### Reverse census — trigger family B, and A3

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rl "_prescan_sidecar\|_capped_side_graph\|read_capped\|_check_count_caps\|ContentReadError" tests/` | only `tests/test_ingestion_limits.py` (this lane's file) — no other test asserts the new symbols |
| B2 file moved on disk | the move-aside protocol above | the only consumers of the three source files are the holding arms run |
| B3 byte-identical golden captures this source | `grep -rl "store\.py\|diff\.py\|osopen\.py" tests/goldens/` | no hits — no golden captures these sources |
| B4 artifact produced here is consumed elsewhere | `grep -rn "MapStore.load\|git_diff" mapper/ --include=*.py` | `screens/home.py` + `screens/map/screen.py` (catch generic `Exception` — the typed refusals flow into the same sinks; wording unchanged), `diff` consumed by screens — signatures unchanged |
| A3 interface consumed by another module changed | `MapStore.load` / `preview_csv` / `git_diff` signatures | unchanged — `load` and `git_diff` keep their signatures and contracts; the D1/D2 freezes untouched (D2 realized, not renamed) |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run of B1 · B2 · B3 · B4 · A3, each with its command and its verdict — B1 1 hit (own lane file), B2 3 move-asides, B3 0 hits, B4 consumers re-validated (generic-Exception sinks unaffected), A3 no interface change |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| the osopen importer allow-list (ledger .6, B-44) | every module outside `osopen`/`app` importing any osopen name | the AST walk in `tests/test_arch_osopen_callers.py` itself (`_sources()` over `mapper/**/*.py`) | 8 importing modules | 1 (`store.py` added to the allow-list) | 7 pre-existing entries untouched — the census is derived, not hand-listed |

| Field | Value |
|---|---|
| **Correction population** | 1 correction, enumerated with its method before the first site was edited — the population IS the derived AST census |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|---------------------|
| the pre-cap read path (`mmd_path.read_text` / `yml_path.read_text` in `load`) | 0 hits in `mapper/store.py` | yes | `grep -n "read_text" mapper/store.py` — only the session-state read at the former :975 remains (outside R2's content-read surface: map files + CSV) |

### Signed-balance test ledger

`post = base − deleted + added` → `tests/test_ingestion_limits.py` is NEW (+1 file, 20 arms); `tests/test_arch_osopen_callers.py` amended in place (+1 allow-list entry); no test deleted → `post = base + 1 file` ✓ reconciles

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer + security-reviewer — Kimi K3 subagent executing agents/code-reviewer.md + agents/security-reviewer.md · OK-with-notes, 0 BLOCKER / 1 MAJOR / 3 MINOR · caps verified enforced at every clause-named boundary; 12/12 evidence digests re-hashed and matching; 2 reviewer-chosen mutants KILLED with hash-proven restores; 6 hostile inputs all typed refusals naming the limit, no path, no crash/hang; F1 MAJOR: prescan refusal interpolates the attacker-controlled anchor name unbounded (mapper/store.py:724) — truncate + pin owed to author; F2/F3/F4 MINOR: AT-113 mislabel on the CSV test section, stat-limb coverage claim not derivable, AT-114 timing flake — full report .dev-flow/2026-10-23-hygiene-batch/evidence/review-inc003.md` |

---

## 5 · Risks

- **S1 (PDR security finding, ruling R9) — DISCHARGED, decision: BOUND.** The diff-side
  `git show` capture was a full in-memory read before any cap. Decision: **bound it** —
  `Popen` with a streamed `stdout.read(MAX_MAP_BYTES + 1)`, killing the child and
  returning `None` past the cap. One-line justification: the capture is the only read of
  operator/commit-history-controlled content with no size precondition, and `MAX_MAP_BYTES`
  is the map cap the same bytes must pass on the working-tree side — an oversize HEAD
  object degrades to "no diff" (`None`) instead of buffering an arbitrarily large hostile
  object, with zero interface change. Asserted by
  `test_diff_side_oversize_head_yields_none`. Recorded in PLAN Risks discharge.
- **Prescan cost (watch-item, measured — not a gate).** On the equivalent of the largest
  committed sidecar — `build_wide(12000)` saved via MapStore, **1,398,062 B / 12,000
  nodes / 11,999 edges** (the `perf0b-ws-*` dirs are not in this worktree; same shape and
  counts per ledger .5) — median full load 8,509 ms, median prescan pass 3,540 ms
  (**+3.54 s per load, 41.6%** of the load, 5 reps). Real maps (≤ 8 nodes) pay ~0. A
  backlog candidate exists (CSafeLoader, or a scanner-only prescan) if a real map ever
  approaches the perf shapes; recorded in §6.
- **Expected-RED arms (declared, PDR §B row 6).** `test_csv_at_file_cap_plus_1_refuses`,
  `test_csv_nul_at_byte_0_refuses_as_binary`,
  `test_csv_nul_at_last_probe_byte_refuses_as_binary` and
  `test_at_114_csv_refusal_toast_shows_the_reason` are authored in this file and are RED
  until L2b lands `import_csv`'s cap and the toast wording. They do not block this gate;
  L2b must turn them green.
- **Discarded first mutation-battery capture.** Its M-Q2-2 arm fixture was a single
  8 MiB source line; under the surviving mutant the mermaid edge regex backtracked
  catastrophically on it (caught by the global 120 s pytest timeout configuration). The
  capture was discarded, the cap fixtures rebuilt from comment lines (parser-safe under
  ANY surviving mutation), the tree restored to the pre-mutation hashes (verified), and
  the battery re-run from scratch — the transcript on disk is the second, complete run.
- **Discarded first prescan-cost capture.** The standalone probe resolved `mapper` from a
  stale checkout on `sys.path` (`C:\Users\<user>\Github\mapper`) instead of the worktree
  (wrong `parents` index); discarded, corrected, re-run. The pytest runs were never
  affected (pytest puts the rootdir first).
- **Contamination check (CAUTION clause).** `git status` before the packet: only the
  lane's own files are modified/untracked — **no foreign edits found in wt-l2**; no
  incident to declare.

---

## 6 · Pending items / spec deviations

- **CSV refusals are typed `osopen.ContentReadError`, not `MapStoreError`** (this file's
  `test_csv_*` arms assert `ContentReadError`). HLR-Q2.2's "typed refusal (MapStoreError
  family)" cannot be realized literally from `import_csv`: R-015 forbids the
  `import_csv → store` import, so the reader's own typed, path-free error is the refusal
  family for CSV. `ContentReadError` subclasses `OSError`, names the limit, and the L2b
  toast's typed branch shows `str(e)` for it. For map loads the refusals ARE
  `MapStoreError`, exactly as HLR-Q2.1 requires. Flagged for the DDR/close reconciliation.
- **`store.py` imports six names from osopen** (the reader, the error, four constants),
  where the ARQ commitment's "ONE name" phrasing anticipated only the reader. The design
  proposal §2 freezes the constants as part of the D2 exposure, and the count/depth caps
  must be read where the checks live (store). The derived allow-list records the actual
  set; the ARQ row is the DDR's to reconcile.
- **Prescan +3.54 s on the 12,000-node perf shape** (§5) — backlog candidate
  (CSafeLoader / scanner-only prescan) if it ever matters; real maps are unaffected.
- **The edges cap is structurally unreachable through `load`** (`mermaid.parse` trees) —
  pinned synthetically via `_check_count_caps`; declared under Load-bearing emptiness.
- The AT-114 screen arm and the three `preview_csv`-level cap arms stay RED until L2b —
  declared in §5, tracked by increment-004.

---

## 7 · Suggested next task

**L2b (increment 004)** — `mapper/import_csv.py`: route the CSV read through
`read_capped(path, MAX_FILE_BYTES)`; `mapper/screens/home.py`: the typed-refusal toast
shows `str(e)` (ruling R7, F-UX-1), generic branch keeps `type(e).__name__`; allow-list
gains `import_csv.py` + `screens/home.py`; the four expected-RED arms must turn GREEN;
mutants M-Q2-3/M-Q2-5; device-name pinning arms named in the L2b test ledger (m6).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 3 / 4 — `SOURCE files` table above |
| 2 | Tests written in this same increment | all | ✓ | `tests/test_ingestion_limits.py` new; arch allow-list amended same landing |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | 16 unit arms green (`l2a-green-2026-10-23.txt` run 1: 21 passed incl. arch) |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | base-tree RED (`l2a-red-…`, sha256 f622f79c…); move-asides (`l2a-move-aside-…`, ed12f777…); battery (`l2a-mutation-battery-…`, 4a2ebc9c…) — restores hash-proven |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 5 probes in the Reverse census table, all verdicts recorded |
| 6 | `code-reviewer` passed — declared in **§4b** | `core` · `full` | ⚠ | §4b = `pending — orchestrator schedules` (runtime has no reviewer sub-agents; PLAN.md gate-notices records the orchestrator holds the gates) |
| 7 | No file from another lane touched | all | ✓ | `git status` shows only L2a-owned files + the declared arch-test amendment |
| 8 | Frozen interfaces untouched (or returned to the trunk) | all | ✓ | D1 (`Canvas.__init__`) untouched; D2 realized as `read_capped` (name minted per the lane brief, declared the D2 realization) — `MapStore.load`/`git_diff`/`preview_csv` signatures unchanged |
| 9 | Coverage claims verified **on disk**, not from intent | all | ✓ | all §4 numbers from the transcripts' actual outputs |
| 10 | Load-bearing emptiness declared, with its synthetic instance (C-55) | all | ✓ | edges-cap unreachability + third-importer absence; synthetic Graph arm; M-Q2-4 as the synthetic third state |
| 11 | **Mutation verdicts** declared — per arm | all | ✓ | 4/4 KILLED, none GREEN, per-arm in the Mutation verdicts cell |
| 12 | **Instrument RED-proof** declared | all | ✓ | 4 instruments, each RED/fired before its PASS was believed |
| 13 | **Correction population** declared | all | ✓ | 1 correction (the allow-list), AST-enumerated before the edit |
| 14 | **Emitted-form assertion** declared | all | ✓ | refusal message strings + the diff-side `None` asserted on the emitted form |
| 15 | **Independent review** names somebody | all | ⚠ | `pending — orchestrator schedules` (the only form this runtime offers) |
| 16 | **Evidence files** declared | all | ✓ | 8 artifacts, paths + stored-byte digests in the Evidence files table |

---

## Cross-batch follow-up — 2026-10-24 (post-close; ledger LED-2026-10-23-hygiene-batch.14)

**The crossed census behind the batch merge missed a B1 consumer of the
prescan.** This increment's reverse census (§5 and the gate table) re-derived
which tests exercise `store.py` — but scoped to the L2a lane's own arms in
`tests/test_ingestion_limits.py`. It never asked the question the OTHER way for
pre-existing anchor-bearing fixtures anywhere in the suite. Three B1 arms in
`tests/test_repair_sidecar.py` (`test_llr_n13_1_7_refusal_warnings_carry_coordinates_not_values`,
`test_llr_n13_1_7_a_huge_scalar_origin_is_bounded_too`,
`test_llr_n13_1_7_a_coordinate_that_carries_a_value_is_bounded_too`) feed
sidecars built on YAML anchors (`&l*`/`&big`/`&bad` + aliases) through `load`
and assert the post-compose repair path's bounded warning records — exactly the
materialisation LLR-Q2.1.2's prescan now refuses before compose. The
orchestrator's clean full-suite run after the merge caught it (3 failed / 3568
passed, `evidence/full-suite-after-merge-2026-10-23.txt`).

**Ruling R10 (2026-10-24):** LLR-Q2.1.2 stands unamended; LLR-N13.1.7 is
superseded in part (the typed early refusal discharges its intent — nothing
amplified is materialised, the message names coordinates, never values). The
three tests are amended to assert the typed refusal — names unchanged, original
value-leak bounds kept as size negatives on the message — not weakened or
deleted (their owning batch `2026-08-26-ui-next-batch-02` is sealed and not
edited). Asserting mutant M-Q2-1-XB14 (anchor refusal dropped in
`_prescan_sidecar`) executed 2026-10-24: all three amended tests go RED on the
old repair path. Evidence: `evidence/xbatch14-red-2026-10-24.txt` (sha256
6441d9c3…ff736), `xbatch14-green-2026-10-24.txt` (sha256 269e1474…9dfea),
`xbatch14-mutant-2026-10-24.txt` (sha256 07bde202…7f06).

**Lesson for the census discipline (Q2.3.1's own C-31 shape):** a rule that
refuses an input CLASS must re-derive its consumer tests by FIXTURE CONTENT
(here: grep the suite for anchor/alias syntax in sidecar builders), not only by
import surface — the import surface (`store.py` callers) was censused and
passed, while the fixture-content consumers three modules over were not.

---

## Review-findings follow-up — 2026-10-24 (independent reviews `evidence/review-inc003.md` — code-reviewer + security-reviewer)

**inc003-F1 (MAJOR — prescan anchor refusal interpolated the attacker-controlled anchor name unbounded) — DISPOSITION: fixed.**
- Requirement it serves: LLR-Q2.1.2 (the refusal names the anchor — it now names it TRUNCATED, which the clause does not forbid) + LLR-N13.1.7 (a coordinate that carries a value behaves like a value).
- Fix (inside the L2a set): `mapper/store.py` — new constant `ANCHOR_NAME_DISPLAY = 40` (stated bound, with the rationale comment); `_prescan_sidecar` renders the name as `anchor[:40]` plus `"…"` when longer. Source files this follow-up: 1 (`mapper/store.py`) of ≤4.
- Asserting test (RED → GREEN, C11): `tests/test_ingestion_limits.py::test_at_111_anchor_name_in_refusal_is_bounded` — a 5,000-char anchor: message length ≤ 160, the 40-char prefix present, the ellipsis present, the remainder absent, no path.
- Asserting mutant (executed 2026-10-24, restore hash-proven): truncation reverted to verbatim `{anchor!r}` → the arm RED; before/after sha256 of `mapper/store.py` both `d5461aff…24992174`.
- Evidence (sha256 of stored bytes, account name redacted to `<user>` per A-110): `evidence/fu-inc003-f1-anchor-bound-red-2026-10-24.txt` (`e391fbb4…d5d912`, 1 failed, `exit=1` — the full 5,000-char name in the message), `evidence/fu-inc003-f1-anchor-bound-green-2026-10-24.txt` (`6e940c6d…d5b46`, 4 passed anchor/alias arms, `exit=0`), `evidence/fu-inc003-f1-anchor-bound-mutant-2026-10-24.txt` (`dc6fa213…0c54a`, 1 failed, `exit=1`).

**inc003-F2 (MINOR — the CSV section of `tests/test_ingestion_limits.py` was mislabeled AT-113) — DISPOSITION: fixed.**
Traceability hygiene only (test-file docstring + section banner relabeled to LLR-Q2.2.1, with a note that AT-113 is the edges arm and AT-114 the toast arm). No behavioral arm is owed for a label correction — C11's test+mutant requirement applies to behavior-bearing fixes; the V2 token harvest now maps the CSV arms to their real authority. Files: `tests/test_ingestion_limits.py` only.

**inc003-F3 (MINOR — the §4 "Conjunctive criteria" claim for the stat limb was not derivable) — DISPOSITION: fixed.**
The packet row itself is reworded in place (see §4): the stat limb is a fast path, the re-read re-check is the enforcing conjunct, and the original "any removal → RED" wording is struck. No code or test change.

**inc003-F4 (MINOR — the AT-114 screen arm flaked once under a full-file run during the review) — DISPOSITION: accepted with reason; not chased.**
The flake reproduced nowhere: it passed in isolation under the same mutant and in every clean full-file re-run before and after this follow-up, with zero source change between occurrences — consistent with the reviewer's own environment-noise suspicion. The suggested fix (poll for the toast with a deadline instead of six fixed `pilot.pause()` calls) is a test-robustness polish, deliberately NOT applied here: per the orchestrator's instruction this follow-up does not chase flakes, and touching the AT-114 arm risks re-opening the L2b gate the increment closed. Recorded so a future recurrence is not mistaken for a regression (the increment-004 review independently observed the same class of transience as its F3).
