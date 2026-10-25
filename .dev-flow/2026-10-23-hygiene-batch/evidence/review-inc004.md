# Independent Review — Increment 004 (lane L2b · US-Q2-001 · AT-109…114)

Roles executed: `code-reviewer` + `security-reviewer` (family C6) + UX lens (AT-114).
Commit under review: `a4d573f` (feat(csv): bounded CSV import + refusal-toast reason).
Reviewer independence: did not author any part of this increment; read-only toward the
diff (two mutant arms applied and hash-verifiably restored, per the review method).

## Scope reviewed

- Commit `a4d573f` in full (`git show`): 5 source files (`mapper/import_csv.py`,
  `mapper/screens/home.py`, `mapper/diff.py`, `mapper/store.py`, `mapper/osopen.py`),
  2 test files (`tests/test_arch_osopen_callers.py`, `tests/test_ingestion_limits.py`),
  the packet, and 8 evidence artifacts.
- Requirement clauses read by range in `.dev-flow/2026-10-23-hygiene-batch/01-requirements.md`:
  US-Q2-001 (lines 86, 116–143), HLR-Q2.1 (229–243), HLR-Q2.2 (245–259),
  HLR-Q2.3 (261–275), LLR-Q2.1.3 (355–365), LLR-Q2.2.1 (367–376), LLR-Q2.3.1 (378–386),
  R-015 cited at line 203. The diff implements what the clauses demand (byte cap
  re-checked post-read, 8 KiB NUL probe, typed path-free refusal naming the limit,
  typed toast branch showing `str(e)`, generic branch unchanged) — no more, no less.
- Surrounding code read for convention: `mapper/import_csv.py` (whole file),
  `mapper/osopen.py:90-149`, `mapper/screens/home.py:495-560`, `mapper/store.py:73-89,725-775`,
  `mapper/diff.py` (whole file), `mapper/screens/map/painting.py:723-741`.

## Checks performed

### Targeted test runs (never the full suite; always `env -u NO_COLOR -u TERM`)

- `tests/test_ingestion_limits.py tests/test_arch_osopen_callers.py` → **25 passed** (matches packet run 1).
- `tests/test_import_csv.py tests/test_diff.py tests/test_store.py` → **17 passed** (matches packet run 3).
- `tests/test_inc9h.py` + `tests/test_ingestion_limits.py` → **61 passed** (the seam pin the
  S1 revision is justified by is green on the revised code).
- `tests/test_inc9c.py` → **61 passed** (the notify census accepts the new toast site).

### My own mutant arms (not the packet's battery)

| Arm | File / mutation | sha256 before | sha256 after restore | Targeted run | Verdict |
|---|---|---|---|---|---|
| R1 | `mapper/import_csv.py:47` `MAX_FILE_BYTES` → `MAX_FILE_BYTES * 2` | `9b1964de…a74076ff` | `9b1964de…a74076ff` ✓ equal | `tests/test_ingestion_limits.py` → `test_csv_at_file_cap_plus_1_refuses` FAILED | **KILLED** |
| R2 | `mapper/screens/home.py:536` `{path.name!r}` → `{path}` (full-path leak) | `26482623…032499b4` | `26482623…032499b4` ✓ equal | `tests/test_ingestion_limits.py` → `test_at_114_csv_refusal_toast_shows_the_reason` FAILED (path-leak assertion) | **KILLED** |

### Evidence digest audit — 8/8 match

Recomputed `sha256sum` on the stored bytes; every digest equals the packet's
§4 Evidence files table exactly (red `a2ec6759…`, green `1faf228c…`, move-aside
`8bc6c1a6…`, battery `f6536e49…`, census `c5a333be…`, privacy `336bbfab…`,
`mutate_l2b.py` `07dcfbaf…`, `l2b_move_aside.sh` `bea5d393…`). Note: the commit
message cites older prefixes (e.g. red `8f5ff598…`); the later redaction commit
`b202856` re-pinned them — the packet's values are the current, correct ones.

### Transcript reads

- `l2b-red-2026-10-23.txt` (stored CP1252, read via iconv): genuine RED — 4 failed
  with real failure output (`DID NOT RAISE` ×2, `_csv.Error` on the uncapped tree,
  empty toast list), `exit: 1`. Consistent with an L2a tree lacking the caps/toast.
- `l2b-green-2026-10-23.txt`: 25 + 17 passed, `exit: 0`; run 2's summary
  (557 passed) comes from a same-command re-capture — the transcript itself
  documents this. Transparent, acceptable.
- `l2b-move-aside-2026-10-23.txt`: real move-aside (rename, run, restore) — not
  `git stash`; `ModuleNotFoundError` RED with exit 2/4; before/after hashes equal,
  and both equal the CURRENT tree's hashes of those files — the reviewed bytes are
  the bytes the move-aside proved.
- `l2b-mutation-battery-2026-10-23.txt` (CP1252, iconv): M-Q2-3 and M-Q2-5 both
  RED (KILLED) with verbatim failing assertions; before/after hashes equal;
  runner exit 0 with "arms: 2 bad: 0".
- `l2b-privacy-grep-2026-10-23.txt`: probe 2 (home paths/handles) clean over the
  L2b-touched files; the single email hit is the fake fixture `q2@lane.invalid`
  (a git-config test value, not a real address); both positive controls fired.
  See the security-lens section for how far this supports the no-path/no-value claim.

### Budget and trace checks

- **Source-file budget:** 5 source files (>4). §2 carries the required declaration
  (the ⚠ note under the count table, restated in §6): the 3 extra files are the
  L2b-gate revision of committed L2a deliverables, forced by pre-existing pins,
  no history mutation possible. Verified plausible: `tests/test_inc9h.py:478-490`
  genuinely monkeypatches `subprocess.run` and asserts argv+env (a `Popen` bound
  would break it); the hero pin (`tests/test_app.py:555`) and the inc9c census
  (`tests/test_inc9c.py:270`) exist and are green. The shared-file edits are
  genuinely minimal: `osopen.py` +4 lines (newline parity), `store.py` +8 lines
  (byte cap), `diff.py` the `_show` rewrite + docstring — each tied to a named pin.
- **Reverse trace (V59):** every touched source/test file names ≥1 requirement id
  in §2 `Traces to`; all cited ids exist in `01-requirements.md`
  (HLR-Q2.1/.2/.3, LLR-Q2.1.1/.1.2/.1.3, LLR-Q2.2.1, LLR-Q2.3.1, AT-109…114, R-015).
- **Tests-encode-intent:** the CSV arms assert discriminating negatives (cap+1
  refuses naming the cap value; NUL at byte 0 and at byte 8,191; NUL past the
  window NOT refused — the documented bound; the AT-114 arm asserts the reason is
  present AND `str(tmp_path)` absent). My R2 mutant confirms the path-leak
  assertion discriminates.

### Security lens (family C6) — executed checks

(a) **Caps enforced per the clauses.** The clauses (HLR-Q2.2 / LLR-Q2.2.1) define
exactly two caps for content reads — the 4 MiB byte cap (stat + post-read re-check,
TOCTOU-armed) and the 8 KiB NUL probe. Both verified live (below) and by the unit
arms. (No row/field caps exist in these clauses; the csv module's own 128 KiB field
limit is pre-existing and unrelated — observed firing, contained by the screen's
generic branch.)

(b) **Refusals name the LIMIT, never a path or value.** `ContentReadError` messages
are authored constants (`mapper/osopen.py:122-133` — no interpolation of path or
content); the stat-failure branch names only the exception type. Verified at
runtime: every typed refusal string asserted free of the file path and the temp dir.

(c) **No crash/hang on hostile input** — throwaway script outside the repo, results:

| Hostile input | Outcome |
|---|---|
| 4 MiB + 1 byte CSV | typed `ContentReadError: file exceeds the byte limit (4194304 bytes)`, instant, path-free |
| NUL at byte 0 | typed `ContentReadError: file looks binary (NUL byte in the first 8192 bytes)` |
| embedded quotes/newlines/unbalanced quote | imported cleanly (3 nodes), no hang |
| formula payload `=HYPERLINK("http://…","x")` leading cell | stored LITERALLY as a title string; never evaluated. No CSV/spreadsheet export surface exists in `mapper/` (grep: no `csv.writer`, no export), so there is no re-ingestion path — informational only |
| non-UTF-8 (`0xff`) without NUL | untyped `UnicodeDecodeError` out of `preview_csv` (see F2); no hang, path-free message |
| single 200 KB field | csv module's own `field larger than field limit (131072)` — pre-existing bound, untyped, contained by the generic branch |

(d) **Privacy grep supports the claim, with a scope note.** The transcript proves
the L2b-touched FILES carry no planted home path/handle and that the probes can
fire. The runtime no-path/no-value claim rests on stronger evidence this review
reproduced independently: the authored-constant messages, the toast's
`{path.name!r}` (name only), AT-114's `str(tmp_path) not in refusal[0]` assertion,
my R2 path-leak mutant (KILLED), and my live Pilot run below.

### UX lens (AT-114) — toast observed through the RUNNING screen

Throwaway Pilot script outside the repo (`MapperApp(tmp)` + `run_test(size=(118,34))`,
`app.notify` intercepted, `i` → type path → Enter):

- Over-cap CSV → toast: `"could not read CSV 'big.csv': file exceeds the byte limit (4194304 bytes)"`
  — appears on the running home screen, names the reason per AT-114, file NAME only,
  full path asserted absent.
- Non-UTF-8 CSV → toast: `"could not read CSV 'badenc.csv': UnicodeDecodeError"` —
  the generic branch's type-name discipline per ruling R7, path-free.
- Headless driving of the screen works in this environment; check **executed**, not blocked.

## Findings

### F1 — `_show` dropped the pre-increment `UnicodeDecodeError` guard [Severity: MAJOR]
- **Where:** `mapper/diff.py:46` (the except tuple), caller `mapper/screens/map/painting.py:731`.
- **What:** the L2b rewrite captures with `text=True, encoding="utf-8"`, so decoding
  happens inside `subprocess.run`; an undecodable HEAD object (e.g. a legacy
  latin-1 committed `.mmd` — realistic in an operator's existing repo) raises
  `UnicodeDecodeError`, which the tuple `(CalledProcessError, FileNotFoundError, OSError)`
  does not catch. The pre-increment code explicitly caught `UnicodeDecodeError → None`.
- **Verified empirically** (throwaway script: git repo with a latin-1 committed
  `.mmd`): on this Windows CPython the decode fails inside subprocess's reader
  thread — a traceback is printed to stderr on every such call and the call
  degrades to `None` only accidentally via the outer `except Exception`; on POSIX
  the error propagates out of `git_diff` to `action_toggle_diff`, which has no
  handler — the documented None-on-error contract (`mapper/diff.py:26-28`) breaks
  with an uncaught exception.
- **Why it matters:** correctness regression on a reachable edge; behaviour now
  differs by platform, and Windows gets stderr traceback spam.
- **Suggested fix:** keep the pinned `subprocess.run` seam (the inc9h pin asserts
  argv+env only, NOT `text=True`) but capture bytes and decode behind a guard:
  ```python
  result = subprocess.run([...], capture_output=True, check=True, env=_git_env())
  try:
      return result.stdout.decode("utf-8")
  except UnicodeDecodeError:
      return None
  ```

### F2 — non-UTF-8 CSV refusal is untyped (reason does not reach the operator) [Severity: MINOR]
- **Where:** `mapper/osopen.py:138` (`data.decode("utf-8")`), surfaced via
  `mapper/import_csv.py:47`; toast at `mapper/screens/home.py:539-543`.
- **What:** a CSV that passes the NUL probe but is not UTF-8 raises an untyped
  `UnicodeDecodeError`; the screen's generic branch shows only the type name
  (`UnicodeDecodeError`), not a reason sentence. Observed live through the Pilot run.
- **Why it matters:** weakly against the AT-114 spirit ("the reason reaches the
  operator"); no security impact (the message is path-free; R7's generic discipline
  covers it).
- **Suggested fix (optional):** catch `UnicodeDecodeError` in `read_capped` and
  re-raise `ContentReadError("file is not UTF-8 text")` — authored, path-free,
  names the reason.

### F3 — transient, unreproduced failures of two ingestion arms during this review [Severity: MINOR — observation]
- **Where:** `tests/test_ingestion_limits.py::test_at_113_edge_count_cap_plus_1_refuses`
  and `::test_at_110_depth_64_parses`.
- **What:** each failed once (DID NOT RAISE / a parse error) in runs interleaved
  with this review's mutant arms, then passed in every subsequent run (5× single,
  paired, 2× full-file, plus the packet's transcripts) with ZERO source change in
  between. Suspected environment noise on this machine (Windows, AV/locking),
  recorded so the DDR does not mistake a future recurrence for a regression.

No other findings. Simplicity/reuse/convention: the diff matches the codebase's
heavy-rationale-comment idiom, reuses the frozen D2 reader instead of re-implementing
caps, and adds no new module edges (allow-list amended same-landing, B-44).

## Verdict

- Brief form: **approve-with-nits** (1 MAJOR / 2 MINOR open, nothing blocking).
- Record form: **OK-with-notes**.

## Proposed §4b `Independent review` cell text

`code-reviewer + security-reviewer + ux lens (AT-114) — OK-with-notes, 0 BLOCKER / 1 MAJOR / 2 MINOR · caps, path-free typed refusals and the AT-114 toast verified live via Pilot and hostile inputs; digests 8/8, RED/move-aside/battery transcripts genuine, own mutants R1/R2 KILLED, restores hash-proven; notes: F1 diff.py's _show dropped the pre-increment UnicodeDecodeError guard (decode behind the pinned seam), F2 non-UTF-8 CSV refusal untyped, F3 transient unreproduced test flake recorded.`

## Evidence checklist

- [x] Diff read in full (`git show a4d573f`; all 5 source + 2 test files).
- [x] Correctness pass done (edge / None / error paths — F1 found by reading + live probe).
- [x] Simplicity pass (no premature abstraction; revisions minimal).
- [x] Reuse / duplication checked (D2 reader reused; no re-implementation).
- [x] Tests reviewed for intent (discriminating negatives confirmed by own mutants R1/R2).
- [x] Verdict explicit (OK-with-notes); no HIGH/BLOCKER findings.

## Evidence states

- Digest audit: `executed` (8/8 match) · Transcript reads: `executed` · Own mutant
  arms: `executed` (2/2 KILLED, restores hash-verified) · Budget/trace: `executed` ·
  Security hostile-input checks: `executed` (6 inputs) · UX Pilot observation:
  `executed` · F1 live probe: `executed` · F3: `failed` to reproduce (recorded).
