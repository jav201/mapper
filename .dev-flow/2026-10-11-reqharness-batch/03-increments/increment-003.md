# Increment 003 — HLR-RH.7 / HLR-RH.4 · `Identity reader and the hardened read-only git allowlist`

| Field | Value |
|---|---|
| Batch | `2026-10-11-reqharness-batch` |
| Increment | `003` |
| Lane (if the batch forked) | none — one lane, trunk unit RHI3 |
| Requirement(s) | HLR-RH.7 / LLR-RH.7.3 · LLR-RH.4.4 · R11/R20/R27a–d (identity + hardened git allowlist) |
| Acceptance | layer-0 unit nodes only (LLR-RH.7.3 is a layer-A inspection LLR executed inside the unit file — `01-requirements.md` §3/§4) |
| Agent | `software-dev` (Kimi, kimi-code) |
| Date | `2026-10-11` |

---

## 1 · What changed

BLUF: mapper now has the ReqHarness core's identity and git seam —
`mapper/reqharness/identity.py` — the ONLY module allowed to spawn
subprocesses. It reads reviewer identity from git config (repo-local first,
then global), discovers the repo root and HEAD, and exposes the dirty-flag
source — through one hardened seam over an exact five-row read-only
allowlist, reduced and hardened per round-2 ruling R20 and round-3 ruling R27.

Mechanism, per LLR:

- **LLR-RH.7.3 (R20/R27)** — the allowlist, as argv tails after the hardened
  prefix: `rev-parse --show-toplevel`, `rev-parse HEAD`, `config --get
  user.name`, `config --get user.email`, and `--no-optional-locks status
  --porcelain`. A tail not in the set is a programmer error refused loudly at
  the call site (`ValueError`), and the source-census node derives the shipped
  set from the AST so the guard cannot drift silently. Every call is an argv
  list with `shell=False`, a 10 s timeout, prefixed `<abs git> --no-pager -c
  core.fsmonitor=false -c core.hooksPath=<os.devnull> -C <repo>` — never
  `cwd=<repo>` — over an env carrying `GIT_OPTIONAL_LOCKS=0` with inherited
  `GIT_DIR`/`GIT_WORK_TREE`/`GIT_CONFIG*` stripped. `git` is resolved ONCE
  per repo to an ABSOLUTE path (`NoDefaultCurrentDirectoryInExePath=1` during
  resolution; `shutil.which` over a PATH that excludes the audited repo — a
  planted `git.exe` in the repo's cwd can never win, R27c).
- **R27a/b** — the audit path (repo-root/HEAD/identity) runs NO `git status`
  at all; the one status row is `Baseline.create`-only and carries the same
  fsmonitor/hooks pins as every other call. The module docstring states the
  residual: `git status` still trusts the repo's `.git/config` (a
  `filter.<name>.clean` can run on it) — exactly why the row is
  Baseline.create-only.
- **R27d** — a `safe.directory` refusal, or ANY git non-zero exit (timeout
  included), degrades to the named result `no repo` (module constant), never
  a crash; identity degradation is an empty `Identity`, a value, not an
  exception.
- **LLR-RH.4.4** — `read(repo)` uses git's own precedence: one `config --get`
  per field, repo-local then global; unset fields come back empty. The honest
  ceiling is stated: this identity is SELF-CLAIMED and spoofable by any
  committer; the chain proves integrity and approval, not authorship. The
  `reviewer` field of a review event is free text elsewhere — identity is the
  git config, never proven from the file.
- The committer-vs-reviewer email warning (`git log` pass) stays **DEFERRED
  (B-124)** and `git log` is NOT in the allowlist.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/reqharness/identity.py` | source | LLR-RH.7.3 · LLR-RH.4.4 · R20/R27a–d | the identity reader + hardened read-only git allowlist (new module) |
| `tests/test_reqharness_identity.py` | test | LLR-RH.7.3 · LLR-RH.4.4 · R20/R27a–d | the six named layer-0 nodes (precedence, resolution/argv census, safe-directory, fsmonitor sentinel, index byte-identical, source census) |

| Count | Value |
|---|---|
| **SOURCE files** | **1 / 4** |
| Test files | 1 (uncapped) |
| Doc files | 0 — the ARQ amendment is OWED in increment 1 (R19), not here |

- At exactly 1 source file: the increment owns exactly one module — the
  subprocess seam. Its four public surfaces (identity, repo root, HEAD,
  dirty flag) all bind to the same hardened `_run_git` call, so any split
  would duplicate the seam or merge an unrelated LLR.

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_identity.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `test_identity_reader_repo_local_then_global`, `test_git_resolution_absolute_and_path_pinned`, `test_safe_directory_refusal_is_named_no_repo_not_a_crash`, `test_fsmonitor_sentinel_absent_after_hardened_calls`, `test_git_index_byte_identical_after_audit_path_calls`, `test_allowlist_source_census_no_non_allowlisted_subprocess` | 6 passed |

### GREEN — executed now, from the worktree root

```bash
$ python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_identity.py
......                                                                   [100%]
6 passed in 1.49s
```

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | four arms, one per named negative control: M-FS1 (drop the `-c core.fsmonitor=false` pin, R27b), M-ID2 (resolve `git` bare/relative, R27c), M-AU3 (a git non-zero raises instead of degrading to `no repo`, R27d), M-ID1 (read only the global config, LLR-RH.4.4) |
| Instrument | project code, own hand; restore checked by sha256 per arm |
| Where it ran | **my own worktree** |
| Transcript | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh3-red.transcript` |
| Restore proven by | **file hash returned to its pre-mutation value** (sha256 before == after, per arm, printed in the transcript) |
| Bytecode cache | `-B` / `PYTHONDONTWRITEBYTECODE` on every run |
| Arms resolved at baseline | **4** |
| Verdict granularity | per resolved node id / instrument, printed per arm |
| Arms that stayed GREEN | none — every arm RED |

| Arm | RED evidence (transcript) | Node it reddened | Restore digest (sha256, before == after) |
|---|---|---|---|
| M-FS1 | `FAILED tests/test_reqharness_identity.py::test_fsmonitor_sentinel_absent_after_hardened_calls` — sentinel file appeared | `test_fsmonitor_sentinel_absent_after_hardened_calls` | `891c44f6…6ebab8` byte-identical → 6 passed |
| M-ID2 | `AssertionError: executable is not absolute: 'git'` | `test_git_resolution_absolute_and_path_pinned` | `891c44f6…6ebab8` byte-identical → 6 passed |
| M-AU3 | `subprocess.CalledProcessError … FAILED … test_safe_directory_refusal_is_named_no_repo_not_a_crash` | `test_safe_directory_refusal_is_named_no_repo_not_a_crash` | `891c44f6…6ebab8` byte-identical → 6 passed |
| M-ID1 | `ValueError: git call outside the read-only allowlist: ['config', '--get', '--global', 'user.name']` → `FAILED … test_identity_reader_repo_local_then_global` | `test_identity_reader_repo_local_then_global` | `891c44f6…6ebab8` byte-identical → 6 passed |

Full digest of `mapper/reqharness/identity.py` at every restore point:
`891c44f6b3d1fece52d71d4f60effd0863ca7a7e90936e96e2f16e8f756ebab8`.

### Conditions this increment discharges

| Condition (review finding) | Ruling | Where discharged here |
|---|---|---|
| **Security G1** (round 2, high): a repo's `core.fsmonitor` can execute code on `git status`; a plain `git status` refreshes `.git/index`, breaking "audit writes nothing" | R20 | the fsmonitor-sentinel node (sentinel stays ABSENT after the hardened calls), the index byte-identical node (`.git/index` sha256 before == after on the audit path), and the argv-census node pinning `shell=False`/10 s timeout/stripped env on every call |
| **Security H1** (round 3, S-H1): `git status` can run commands via `filter.<name>.clean` from the repo's own `.git/config` + committed `.gitattributes` | R27a/b | the audit path runs NO `git status` at all (the argv census asserts the status tail never appears on the audit path); the status row is `Baseline.create`-only and carries `core.fsmonitor=false`; the residual is stated in the docstring, not fixed |
| **Security H2** (round 3, S-H2): on Windows a bare `git` can resolve from the audited repo's cwd (planted `git.exe`) | R27c | one-shot ABSOLUTE resolution with `NoDefaultCurrentDirectoryInExePath=1` over a repo-free PATH; the M-ID2 arm reddens the executable assertions |
| **Security H3** (round 3, S-H3): a repo's `core.hooksPath` could redirect hooks | R27b | the fixed `-c core.hooksPath=<os.devnull>` pin on every call, asserted per-argv by the census node |
| **Security H4** (round 3, S-H4): `include.path`/`includeIf` only READ; `core.sshCommand`/`credential.helper`/`diff.external` not invoked by read-only commands; `core.pager` covered by `--no-pager`; a `safe.directory` refusal must become the named `no repo`, not a crash | R27d | `--no-pager` on every argv; the safe-directory node feeds git's own `GIT_TEST_ASSUME_DIFFERENT_OWNER` (real refusal, real exit 128) and asserts the named `no repo` on every audit-path query with no exception — M-AU3 reddens it |

- The architect findings H1–H4 of round 1 are DISCHARGED BY OTHER
  INCREMENTS (rulings R1–R5: policy binding, canonical form, cache,
  precedence) — not by this one; claiming them here would be false.

### Residuals (stated, not fixed)

- Identity is self-claimed and spoofable by any committer (LLR-RH.4.4
  ceiling); the layer-3 risk — a full consistent rewrite of chain + every
  review by a writer with repo access — is answered by B-122's strong mode
  (signed commits), a named follow-up; git anchoring of genesis also
  follow-up.
- `git status` (the `Baseline.create` row only) still trusts the repo's
  `.git/config` — a `filter.<name>.clean` can run on it; this is the stated
  PDR residual and the reason `--audit` runs no status (R27a).
- The committer-vs-reviewer email warning is DEFERRED (B-124); `git log`
  is not in the allowlist.

### Evidence files — bytes at a declared home, verbatim, hash-verified

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED-proof transcript (account name redacted to `<profile>` per A-110) | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh3-red.transcript` | `4ee004c631672f7d2b3106a90d65be4dbd04f43db50cdb6a08c09581bccc25be` |

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | reviewed by `code-reviewer` — verdict recorded in the batch's independent review rounds (`02-review.md`); findings discharged via the rulings named in this packet |

---

## 5 · Risks

- The one-shot git-resolution cache (`_GIT_CACHE`) is keyed by resolved repo
  path; a fixture that swaps the repo at the same path within one process
  would keep the old resolution. Real callers (audit per repo invocation)
  never hit this; tests inject fresh paths.
- The 10 s timeout is a named constant; a pathologically slow `git` on a
  huge repo degrades to `no repo` rather than hanging — by design (R27d),
  but it also means a slow repo is indistinguishable from a broken one.

## 6 · Pending items / spec deviations

- None in this increment. Consumers of the seam (`chain.py`, `baseline.py`,
  `audit.py`) land in their own increments per `01-requirements.md` §3; the
  deferred B-124 warning stays out of the allowlist.

## 7 · Suggested next task

Continue the batch per `PLAN.md` — the chain increment (RH2 mechanisms:
append, policy binding, verify) consumes this seam only through its public
surface.

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | ≤4 source files | ✓ | 1/4, §2 |
| 2 | Tests written in this same increment | ✓ | `tests/test_reqharness_identity.py` |
| 3 | Layer 0 written where the criterion applies | ✓ | 6 nodes, §4 |
| 4 | RED counterfactual declared | ✓ | 4 arms, transcript + restore digests, §4 |
| 5 | Security conditions discharged mapped to findings | ✓ | G1 + S-H1–S-H4 table, §4 |
| 6 | `code-reviewer` passed | ⚠ | PENDING — §4b |
| 7 | No file from another lane touched | ✓ | one lane; only this increment's files |
| 8 | Frozen interfaces untouched | ✓ | no ARQ §4 row changed; no keymap/seat edit (that seat belongs to the roles-screen increment 6a) |
| 9 | Coverage claims verified on disk | ✓ | GREEN line from a run executed now; claims cite the transcript |
| 10 | Residuals stated honestly | ✓ | identity ceiling + status residual + B-124 deferral, §4/§5 |
| 11 | Evidence files declared | ✓ | 1 row with sha256 |
| 12 | Independent review names somebody | ⚠ | PENDING |


---

## Code-review follow-up (RHFIX23)

Code review of increments 002/003 (Claude Sonnet) returned REQUEST-CHANGES;
unit RHFIX23 applied the identity-side rulings F4–F7. Backups were taken only
after the fix was GREEN; every restore is verified byte-identical (sha256)
in the transcript.

| Finding | Severity | Fix | Node(s) | Negative control |
|---|---|---|---|---|
| **F4 cwd exclusion** — git resolution relied on `shutil.which` + a process-wide `NoDefaultCurrentDirectoryInExePath` mutation; before Python 3.12 `shutil.which` searches `.` on Windows regardless of that variable | HIGH | `_which_git` walks the filtered PATH itself: each directory that resolves to the audited repo, the current working directory, `.` or an empty entry is skipped — compared resolved — then `git` + each PATHEXT extension is tried on Windows (`git` on POSIX), first existing regular file wins; the env mutation and `shutil.which` are gone | `test_git_resolution_excludes_repo_and_cwd` — `monkeypatch.chdir(repo)` with planted `git.cmd`/`git.exe` (harmless scripts) in the repo, the repo FIRST on PATH and an empty PATH entry behind it; the resolved executable is absolute and not inside the repo | M-ID3 — repo/cwd exclusions removed → the planted executable wins → RED |
| **F5 env leak** — only `GIT_DIR`/`GIT_WORK_TREE`/`GIT_CONFIG*` were stripped; `GIT_INDEX_FILE`, `GIT_COMMON_DIR`, `GIT_OBJECT_DIRECTORY`, ... reached the child | MED | `_git_env` strips EVERY inherited `GIT_*` key, then sets `GIT_OPTIONAL_LOCKS=0` — the only `GIT_*` key the child ever sees | `test_git_resolution_absolute_and_path_pinned` extended — `GIT_INDEX_FILE`/`GIT_COMMON_DIR`/`GIT_OBJECT_DIRECTORY` injected into the parent env; the per-argv env census asserts no child key starts with `GIT_` except `GIT_OPTIONAL_LOCKS` | F5a — strip narrowed to the pre-fix set → the injected keys reach the child env → RED |
| **F6 resolve crash** — `Path.resolve()`/`expanduser()` were unguarded: a NUL-byte path raised instead of degrading | MED | `_resolve_path` catches `(OSError, ValueError, RuntimeError)` and returns None; `_resolve_git` degrades an unresolvable repo path to `no repo` | `test_unresolvable_repo_path_is_named_no_repo_not_a_crash` — a repo path with a NUL byte → `no repo` on every query, `Identity("", "")`, no exception | F6a — unguarded `repo.resolve()` restored → the NUL path raises → RED |
| **F7 failed-resolution cache** — `_GIT_CACHE` stored `None`, so a transient PATH failure stuck for the process lifetime | MED | only successful resolutions are stored; a failed one re-resolves on the next call | `test_failed_git_resolution_is_not_cached` — PATH emptied (first resolution fails → `no repo`), PATH repaired → the same repo resolves without a new process | F7a — the failed resolution cached → the repaired call still says `no repo` → RED |

- Consequence absorbed in this file: F5 strips git's own
  `GIT_TEST_ASSUME_DIFFERENT_OWNER` from the child env, so
  `test_safe_directory_refusal_is_named_no_repo_not_a_crash` now injects the
  refusal hook BELOW the `_git_env` seam (the git invocation is untouched —
  the refusal and its exit 128 stay real, not mocked).
- Ledger: `LED-2026-10-11-reqharness-batch.31` records the unit (F2 owns the
  amendment; F1/F3 and F4–F7 are listed there as shipped in the same unit).
- RED transcript: `.dev-flow/2026-10-11-reqharness-batch/evidence/rh23fix-red.transcript`
  — sha256 `8fe8f8b8152b2abd21c901adf34325665375295a418bf161ed8a05b6f5547647`.
- Verification after all restores: `python -B -m pytest -q -p no:cacheprovider
  tests/test_reqharness_chain.py tests/test_reqharness_identity.py
  tests/test_reqharness_config.py tests/test_no_operator_paths.py` — 35
  passed; `ruff check` clean.

---

## 9 · DDR follow-up note (ARCH C1 — appended, not a rewrite)

The RHFIX23 F4 fix in §Code-review follow-up above (git resolved by walking PATH
itself, excluding the repo / cwd / `.` / empty entries; PATHEXT fallback
`.COM;.EXE;.BAT;.CMD`; `shutil.which` and the `NoDefaultCurrentDirectoryInExePath`
mutation dropped) is now reflected in the live contract: `01-requirements.md`
LLR-RH.7.3 + §2.4, `design/design-proposal.md` §1/§2.1/§3.6/§5, and the PDR DDR
amendments (`C-R27c`) — ledger `LED-2026-10-11-reqharness-batch.32`. The
anchor/alias loader wording (event-stream pre-scan before construction, not "at
compose time") is synced the same way — ledger `.33`. This increment's shipped
code (`identity.py`) already matched the corrected wording; nothing in §1–§7 was
rewritten.
