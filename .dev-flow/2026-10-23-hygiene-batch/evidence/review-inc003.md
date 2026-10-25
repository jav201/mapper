# Independent Review — Increment 003 (lane L2a, US-Q2-001)

Roles executed: **code-reviewer** (`agents/code-reviewer.md`) + **security-reviewer** (`agents/security-reviewer.md`, trigger family C6), per the orchestrator's assignment. Reviewer did not author this increment; read-only toward the diff (two temporary mutant arms, both restored and hash-proven — below).

## Scope reviewed

- Commits: `0a94362` (feat(store): bounded map loading — D2 reader, prescan, count caps) and `37a8175` (test(dev-flow): amend the three LLR-N13.1.7 arms to LLR-Q2.1.2's typed refusal — ruling R10, ledger .14).
- Source files (the union's source surface): `mapper/osopen.py`, `mapper/store.py`, `mapper/diff.py` — **3 / 4**, budget clean, declared in packet §2.
- Test files: `tests/test_ingestion_limits.py` (new, 20 arms), `tests/test_arch_osopen_callers.py` (allow-list + `store.py`), `tests/test_repair_sidecar.py` (three arms amended by the follow-up).
- Packet: `.dev-flow/2026-10-23-hygiene-batch/03-increments/increment-003.md` (incl. the cross-batch follow-up section).
- Requirement clauses read by range: `01-requirements.md` US-Q2-001, HLR-Q2.1/Q2.2/Q2.3, LLR-Q2.1.1/.1.2/.1.3, LLR-Q2.2.1, LLR-Q2.3.1 (incl. the ledger-.14 amendment to LLR-Q2.1.2), and ledger entry LED-2026-10-23-hygiene-batch.14.

## Checks performed

### Diff vs clauses (code-reviewer lens)

- `mapper/osopen.py`: `read_capped` implements the m4 shape exactly as LLR-Q2.1.1/LLR-Q2.2.1 demand — stat, refuse `> cap`, capped `read(cap + 1)` re-check (never a full read before the re-check), NUL probe over the first `BINARY_PROBE_BYTES` bytes. `ContentReadError` messages are authored constants naming the limit; no path, no content interpolation. Constants match the C-36 freeze (8 MiB / 64 / 100,000 / 100,000 / 4 MiB / 8 KiB).
- `mapper/store.py`: both map reads routed through `read_capped` at `MAX_MAP_BYTES`; `_prescan_sidecar` is genuinely iterative (`yaml.parse` event stream, explicit depth counter — no recursion), refuses the first anchor/alias event and depth > 64 before `yaml.safe_load`; `_check_count_caps` enforces both count caps and is called from `load` and `_capped_side_graph`. Exception-tuple ordering correct (`ContentReadError` before `OSError`; `MapStoreError` not in the parser net, so refusals propagate). `MapStore.load` signature unchanged.
- `mapper/diff.py` (as committed in `0a94362`): bounded `git show` capture (streamed `stdout.read(MAX_MAP_BYTES + 1)`, `kill()` on oversize — the child is necessarily alive, blocked on the full pipe, so `kill()` cannot race an exited process), `None`-on-error contract preserved, no `diff → osopen` import (ruling R8). See the observation below on the post-merge state.
- Convention-conformance: house style kept (docstrings citing LLR/mutant ids, C6 rationale comments). Reuse: `_capped_side_graph` deliberately re-uses the store edge rather than duplicating caps in diff — justified, documented.
- Tests encode intent: discriminating boundaries everywhere (cap−1 loads / cap+1 refuses; depth 64 vs 65; at-cap passes / cap+1 refuses; NUL at byte 0, 8,191, and past-window negative; value-absence negatives in the three amended arms; `str(tmp_path) not in msg` privacy limbs inside the refusal arms).

### Live test runs (this worktree, `env -u NO_COLOR -u TERM`, `-p no:cacheprovider --color=no`)

- `tests/test_ingestion_limits.py` + `tests/test_arch_osopen_callers.py` + `tests/test_repair_sidecar.py`: **36 passed** (L2b has since landed and merged, so the four declared expected-RED arms are green here).
- `tests/test_ingestion_limits.py` alone after mutant restores: **20 passed**.

### Reviewer's own mutant arms (not the packet's battery)

| Mutant | Target before sha256 | Edit | Run | Verdict | Restore sha256 |
|---|---|---|---|---|---|
| R-INC3-A | `mapper/store.py` `71b82f164209257aff7611e4594fcae73340c129040fb5cad65a67341d79639f` | `if depth > MAX_DEPTH:` → `>=` (`mapper/store.py:728`) | `tests/test_ingestion_limits.py` → `test_at_110_depth_64_parses` FAILED | **KILLED** | `71b82f16…` identical ✓ |
| R-INC3-B | same baseline | `len(graph.edges) > MAX_EDGES` → `> MAX_EDGES + 1` (`mapper/store.py:87`) | `tests/test_ingestion_limits.py` → `test_at_113_edge_count_cap_plus_1_refuses` FAILED | **KILLED** | `71b82f16…` identical ✓ |

(Under R-INC3-B the async AT-114 arm also failed in that one full-file run; it passed in isolation under the same mutant and in the clean full-file re-run — see F4.)

### Evidence audit — digest recomputation (all stored bytes re-hashed)

| Artifact | Packet digest | Recomputed | Match |
|---|---|---|---|
| `l2a-red-2026-10-23.txt` | `f622f79c…9968d78` | same | ✓ |
| `l2a-green-2026-10-23.txt` | `89494620…86e392` | same | ✓ |
| `l2a-move-aside-2026-10-23.txt` | `ed12f777…a691ea` | same | ✓ |
| `l2a-mutation-battery-2026-10-23.txt` | `4a2ebc9c…85306f7` | same | ✓ |
| `l2a-prescan-cost-2026-10-23.txt` | `34629745…e13896` | same | ✓ |
| `l2a-privacy-grep-2026-10-23.txt` | `260a51e2…a4958b9` | same | ✓ |
| `mutate_l2a.py` | `c2e10049…641d45` | same | ✓ |
| `l2a_move_aside.sh` | `bf0879b8…471c47` | same | ✓ |
| `l2a_prescan_cost.py` | `c09352f0…40710` | same | ✓ |
| `xbatch14-red-2026-10-24.txt` | `6441d9c3…ff736` | `6441d9c3954c…937dff736` | ✓ |
| `xbatch14-green-2026-10-24.txt` | `269e1474…9dfea` | `269e1474435e…05369dfea` | ✓ |
| `xbatch14-mutant-2026-10-24.txt` | `07bde202…7f06` | `07bde202c2b5…5947a7f06` | ✓ |

12 / 12 digests match the citations.

### Transcript reads

- `l2a-red-…`: genuine RED — collection `ImportError` on the not-yet-existing D2 names + the arch allow-list arm RED on the amended-but-unlanded entry; exit 1. ✓
- `l2a-green-…`: run 1 = 21 passed / 4 deselected (the declared L2b-pending arms) in one complete run; pin runs 17 / 102 / 9 passed. ✓
- `l2a-move-aside-…`: 3 files moved aside (rename, not `git stash`), each holding arm RED with `ModuleNotFoundError` exit 4; every before/after hash pair equal. ✓
- `l2a-mutation-battery-…`: M-Q2-1 (×2 arms), M-Q2-2, M-Q2-4 all RED (KILLED) with real DID-NOT-RAISE failures printed; per-arm restore hashes equal; runner exit 0, `arms: 4 bad: 0`. ✓
- `xbatch14-red-…` (3 failed / 35 passed — the three LLR-N13.1.7 arms on pre-amendment HEAD), `xbatch14-green-…` (38 passed), `xbatch14-mutant-…` (M-Q2-1-XB14: 6 failed / 32 passed — the three amended arms plus AT-111×2 and the diff-side anchor arm). The follow-up's ruling/ledger amendment (R10, LED-.14, LLR-Q2.1.2 rationale) is coherent with the increment: tests amended not weakened — names unchanged, original size bounds kept as message-size negatives, value-absence asserted (`"x"*50_000`, `"z"*1_000` not in message). ✓

### Security lens (C6) — checks (a), (b), (c)

- **(a) Caps enforced at the named boundaries:** byte cap at both stat and re-read (`mapper/osopen.py` `read_capped`); prescan before compose in both `load` and `_capped_side_graph`; count caps called from `load` (`mapper/store.py` post-parse) and `_capped_side_graph`; diff side reaches caps only through the store edge. Verified in the diff and by the live runs above.
- **(b) Refusal messages name the limit, never a path:** all byte/depth/count messages are authored constants + the map id. **Exception — F1:** the prescan's anchor refusal interpolates the attacker-controlled anchor NAME unbounded (`mapper/store.py:724`).
- **(c) Hostile inputs driven by the reviewer** (throwaway script in the system temp dir, outside the repo; worktree imported by absolute path to avoid the stale-checkout trap the packet itself records in §5):

| # | Hostile input | Result |
|---|---|---|
| 1 | `.mmd` at 8 MiB + 78 B | typed `MapStoreError` naming `8388608`, 0.000 s, no path, no traceback |
| 2 | sidecar with 100,001 ghost nodes | typed refusal naming `100000`, 8.0 s (YAML parse of the input itself — the §5 watch-item), no hang |
| 3 | sidecar truncated mid-record | typed refusal (`m_nodos.yml unreadable` — basename only, pre-existing convention), 0.008 s |
| 4 | 10,000-deep flow-nesting bomb | typed refusal naming `depth limit (64)`, 0.009 s — no `RecursionError` |
| 5 | anchor with a **5,000-char anchor name** | typed refusal — but the message is **5,087 chars**, the anchor name interpolated whole (see F1) |
| 6 | invalid UTF-8 sidecar | typed refusal naming `UnicodeDecodeError` only, no path |

No crash, no traceback escape, no hang on any input.

- **Privacy-grep evidence audit:** `l2a-privacy-grep-2026-10-23.txt` greps the L2a-touched files for email-shaped and home-path-shaped strings; the only two hits are benign (an `example.com` comment in `mapper/osopen.py:350`, a `.invalid` fixture address in the test file); both positive controls (planted address, planted user-profile path) fired, so the absence is believed. It supports the no-path/no-account claim **at source level**; the runtime-message half of the claim is carried by the per-arm `str(tmp_path) not in msg` assertions (verified live in hostile runs 1–6: `path-in-msg=False` throughout). Sufficient for the claim as made.

### Budget / reverse-trace (V59)

- Source budget: 3 / 4 — clean; the follow-up commit adds no source file. ✓
- Every touched file names ≥1 requirement id in packet §2 `Traces to`, and each id exists in `01-requirements.md` (HLR-Q2.1/Q2.2/Q2.3, LLR-Q2.1.1/.1.2/.1.3, LLR-Q2.2.1, LLR-Q2.3.1, AT-109…AT-114, US-Q2-001 all present). The follow-up's `tests/test_repair_sidecar.py` traces to LLR-Q2.1.2 + LED-.14 via the packet's follow-up section (not the §2 table — the section is the record; acceptable). ✓

## Findings

### F1 — Prescan anchor refusal interpolates the attacker-controlled anchor name unbounded [MAJOR — security]
- **Where:** `mapper/store.py:724` (`f"are not allowed here (anchor {anchor!r})"`).
- **What:** the anchor name is sidecar-controlled content and is embedded in the operator-facing refusal with no length bound. Demonstrated live: a 5,000-char anchor name yields a 5,087-char refusal; the ceiling is only the 8 MiB file cap, so a hostile sidecar can push an ~8 MiB string into the toast/log pipeline.
- **Why it matters:** this is precisely the defect class LLR-N13.1.7 polices — "a coordinate that carries a value behaves like a value" — which the follow-up commit (37a8175) re-affirms by keeping the 2,000 / 200,000-char bounds as message-size negatives. Those bounds hold for the amended fixtures only because their anchor names are short; the new code path itself carries no bound. Naming the anchor is required by LLR-Q2.1.2 — naming it *untruncated* is not.
- **Suggested fix (for the author):** truncate in the message, e.g. `f"(anchor {anchor[:64]!r}{'…' if len(anchor) > 64 else ''})"`, and add one arm with a long anchor name asserting the message stays under a small bound while still naming the anchor prefix. The three amended arms (`'l0'`/`'big'`/`'bad'`) are unaffected by a 64-char truncation.

### F2 — CSV section of the new test file is mislabeled `AT-113` [MINOR]
- **Where:** `tests/test_ingestion_limits.py:7` (module docstring: "`test_csv_*`, AT-113") and `tests/test_ingestion_limits.py:245` (section banner "AT-113 / LLR-Q2.2.1").
- **What:** AT-113 is the **edges** arm per `01-requirements.md` HLR-Q2.1 (`AT-113 (edges)`) and the packet header — and this same file already realizes it as `test_at_113_edge_count_cap_plus_1_refuses`. The CSV arms trace to LLR-Q2.2.1 / AT-114. Two different meanings of AT-113 inside one file is traceability noise for the V2 token harvest.
- **Suggested fix:** relabel the CSV banner/docstring to `LLR-Q2.2.1` (and AT-114 where an AT is wanted).

### F3 — Packet's conjunctive-coverage claim for the stat limb is not derivable [MINOR — packet accuracy]
- **Where:** increment-003 §4, *Load-bearing emptiness* row "Conjunctive criteria" (`mapper/osopen.py` `read_capped` stat limb).
- **What:** the packet claims "any removal of the stat check lets the stat arm's 8 MiB+ file through → RED". Not so: with the stat limb deleted, the capped `read(cap + 1)` re-check still refuses the oversize file, so `test_at_109_byte_cap_stat_refuses_and_names_limit_and_map` stays green — the mutant survives. The stat limb is a fast-path/growth guard no current arm discriminates.
- **Why it matters:** a false coverage claim in the packet is a (small) false-confidence statement; the limb itself is defensible (refuse a huge file without opening it; refuse a file that shrinks between stat and read).
- **Suggested fix:** either reword the packet row to "stat limb is a fast path; the re-check limb is the enforcing conjunct for file size", or add a shrink-between-stat-and-read arm (stat reports oversize, read returns under cap → currently refuses; documents the intended conservative behavior).

### F4 — AT-114 screen arm flaked once under a full-file run [MINOR — test robustness]
- **Where:** `tests/test_ingestion_limits.py::test_at_114_csv_refusal_toast_shows_the_reason`.
- **What:** during mutant arm R-INC3-B's full-file run it failed, then passed in isolation under the same mutant and in the clean-tree full-file re-run (20 passed). The arm waits on a fixed budget of six `pilot.pause()` calls after Enter, preceded in file order by the heavy count-cap arms (~8 s of YAML work).
- **Why it matters:** an order/timing-sensitive acceptance arm will produce spurious REDs in slower environments; belongs to L2b's polish list (increment-004) rather than this gate.
- **Suggested fix:** poll for the toast with a deadline instead of a fixed pause count.

### Observation (not a finding against these two commits)
The S1 discharge as committed in `0a94362` (streamed, bounded `git show` capture) was **revised by the later L2b commit `a4d573f`** (outside this review's commit set): the capture is back on the `subprocess.run(capture_output=True)` seam — an unbounded in-memory buffering of the HEAD object — and the byte cap is now enforced on the captured texts inside `_capped_side_graph` (`mapper/store.py:747-752`, with a comment citing "disposition REVISED at the L2b gate … recorded in increment-004 section 5/6"). Increment-003 §5's "S1 DISCHARGED — BOUND (streamed)" therefore no longer describes the merged tree; the memory-boundedness of the diff side now rests on increment-004's acceptance-with-rationale. Flagged for the increment-004 reviewer and the DDR, not charged against this increment.

## Verdict

- Brief form: **approve-with-nits** (1 MAJOR + 3 MINOR open, nothing blocking; the caps hold under every hostile input I drove).
- Record form: **OK-with-notes**.

## Proposed §4b `Independent review` cell text

`code-reviewer + security-reviewer — OK-with-notes, 0 BLOCKER / 1 MAJOR / 3 MINOR · caps verified enforced at every clause-named boundary (byte stat+re-read, pre-compose prescan, count caps, store-edge-only diff side); 12/12 evidence digests re-hashed and matching; 2 reviewer mutants KILLED with hash-proven restores; 6 hostile inputs all typed refusals, no path, no crash/hang; F1 (MAJOR): prescan refusal interpolates the attacker-controlled anchor name unbounded (mapper/store.py:724) — truncate + pin in a follow-up; F2/F3/F4 MINOR (AT-113 mislabel on the CSV section, stat-limb coverage claim not derivable, AT-114 timing flake). Report: evidence/review-inc003.md`

## Evidence checklist (code-reviewer)

- [x] Diff read in full — both commits, all files (`mapper/osopen.py` +63, `mapper/store.py` +111, `mapper/diff.py` ±43, `tests/test_ingestion_limits.py` +336, `tests/test_arch_osopen_callers.py` +6, `tests/test_repair_sidecar.py` ±156, plus the `.dev-flow` records of 37a8175).
- [x] Correctness pass done (edge / None / error paths — incl. exception-tuple ordering, `kill()` liveness, decode failure → None).
- [x] Simplicity pass (no premature abstraction; `_capped_side_graph` duplication of load's parse net is justified and documented).
- [x] Reuse / duplication checked against existing utils (store edge reused per ruling R8; no re-implemented util found).
- [x] Tests reviewed for intent, not just behavior (discriminating boundaries present throughout; F2/F3/F4 are the exceptions noted).
- [x] Verdict explicit; HIGH findings: none.

## Evidence checklist (security-reviewer)

- [x] Each finding has what · where · why · recommendation and a severity.
- [x] No secret values, account names, or absolute user-profile paths in this report.
- [x] Refusal-message surface probed live (6 hostile inputs) — no path, no value materialisation except F1's anchor name.
- [x] Verdict explicit; HIGH findings: none.
- [x] No new tool/integration added — scope/blast-radius item n/a.

Evidence states: all checks above `executed`; F1–F4 `executed` (reproduced/verified), fixes `planned` (author's to apply); the observation on the S1 revision is `executed` as a read of the merged tree, disposition owned by increment-004.
