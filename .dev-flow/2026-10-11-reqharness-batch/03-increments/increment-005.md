# Increment 005 — HLR-RH.6 / HLR-RH.7 · `Baselines + release rules + the read-only --audit entry`

| Field | Value |
|---|---|
| Batch | `2026-10-11-reqharness-batch` |
| Increment | `005` (RH5) |
| Lane (if the batch forked) | none — one lane; this worktree IS the batch trunk, RH5 merged at `03a85b2` |
| Requirement(s) | HLR-RH.6 / HLR-RH.7 · LLR-RH.6.1–6.2 · LLR-RH.7.1–7.3 · rulings R1/R4/R5/R13/R14/R24/R26/R27a/R27c/R27d/R20 · AT-080 / AT-081 |
| Acceptance | layer-0 unit nodes + the e2e CLI nodes (the executed verification named in `01-requirements.md` §3 for HLR-RH.6/HLR-RH.7) |
| Agent | `software-dev` (Kimi, kimi-code) |
| Date | `2026-10-11` |

---

## 1 · What changed

BLUF: the ReqHarness core can now freeze, diff and judge a registry.
Three new modules — `baseline.py` (the named, commit-bound, dirty-flagged
freeze and the five-class diff), `release.py` (the hard-coded mandatory
rules plus the config rules, with `safe_verify` folding schema refusals
into status words), `audit.py` (the read-only report) — plus the
`--audit` branch in `app.py` and a one-line `identity.py` nit. Tests:
`tests/test_reqharness_baseline.py` (2 nodes), `tests/test_reqharness_release.py`
(5 nodes), one new Windows-only node in `tests/test_reqharness_identity.py`.

Mechanism, per LLR:

- **LLR-RH.6.1 (R13/R27a)** — `Baseline.create` snapshots the current
  derivation (objects with id/class/normative-digest/state, the verified
  chain head, the review file set, the creation time) under
  `reqharness/baselines/<name>.yml`, bound to the repo's commit SHA from a
  read-only `git rev-parse HEAD` and a `dirty` flag from read-only
  `git status --porcelain --no-optional-locks`. The dirty flag is taken
  ONLY here, in the operator's own repo, at create time — `--audit` runs
  NO `git status` (R27a); the flag is recorded and refuses nothing. The
  name is confined (`..`, separators refused), an existing baseline of the
  same name is never overwritten, and no-repo / unverifiable-registry
  states are named refusals, never a partial freeze. Git tagging stays a
  manual act (O9). The freeze refuses to run over a broken chain or an
  unverifiable derivation (`snapshot` raises the named refusal).
- **LLR-RH.6.2 (R13/R24)** — `diff` classifies every union id as
  `new` / `changed` (the normative digest moved) / `retired` /
  `unchanged` / `deleted` — the last including a review file present in
  the baseline's frozen set but absent from disk — for both
  baseline-vs-baseline and baseline-vs-now. The `reactivated` class and
  the review-state progression are **deferred (B-125)**: R24 trimmed this
  batch to five classes plus the dirty flag.
- **LLR-RH.7.1 (R1/R5/R14)** — `evaluate` ANDs the three hard-coded
  mandatory rules — `chain_verified`, `policy_verified`,
  `signers_in_force` — then every rule declared in `config.yml` (config
  may ADD rules, never remove the mandatory three). Verdicts are exact
  strings: `ready` or `not ready · <reason>`; a broken chain, a policy
  mismatch or an unknown recorded head yields EXACTLY
  `not ready · registry not verifiable`; an unentitled review alone never
  blocks. `safe_verify` is the shared seam: a schema `ValidationError`
  from a tampered or hand-added document (a hand-added genesis lacking
  `config_hash`) becomes the status `chain broken` — or
  `config changed without approval` when the refusal names the config —
  never an exception escaping the evaluation (this is the RH2 review LOW
  nit, discharged here).
- **LLR-RH.7.2 (R4/R14/R27a/R27d)** — `mapper --audit <repo>
  [--baseline <name>]`: discovers the connected repo with
  `git rev-parse --show-toplevel` (the argument overrides; a maps dir's
  repo is its containing work tree), confines the path through
  `mapper.osopen.confine_reason` BEFORE any file is read (unknown or
  escaping path → named refusal), verifies the chain, derives the states,
  evaluates the rules and renders the report — chain status, the exact
  per-state counts (pre-reviews and unentitled counted separately, the
  informative mark shown, the R17 old-head WARN lines, the canon reader's
  reported lines), the identity-ceiling sentence, the verdict, and the
  baseline diff (with `deleted review:` lines) when `--baseline` is given.
  Read-only means READ-ONLY: the parse cache is OFF
  (`ParseCache.disabled()`), nothing anywhere is written, and no
  `git status` runs (R27a) — the fixture's `.git/index` is byte-identical
  after a run. A `safe.directory` refusal or ANY git non-zero exit becomes
  the NAMED result `no repo` (R27d), never a crash. Exit 0 on `ready`,
  1 otherwise, 2 on usage error; the branch sits in `app.main` ahead of
  the `app.py:328` UTF-8 stdout re-wrap, leaving the normal TUI start
  untouched; the subprocess test carries a 60 s timeout.
- **LLR-RH.7.3 nit (R20/R27c)** — `identity._which_git` on Windows now
  tries ONLY the PATHEXT-extensioned git names, never a bare extensionless
  `git`, so a planted extensionless file ahead of the real git on PATH can
  never win (the reviewed RH3 nit, folded into this unit by the
  orchestrator). POSIX is unchanged (exactly `git`).

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/reqharness/baseline.py` | source | HLR-RH.6 · LLR-RH.6.1/6.2 · R13/R24/R27a | the freeze (`Baseline.create`, name confinement, no-overwrite, named no-repo/unverifiable refusals) and the five-class `diff` (incl. deleted review files via the frozen review set); `snapshot`/`freeze_objects` |
| `mapper/reqharness/release.py` | source | HLR-RH.7 · LLR-RH.7.1 · R1/R5/R14 | `evaluate` (the mandatory three ANDed with the config rules, exact verdict strings) and `safe_verify` (the schema-refusal → status ladder — the RH2 review LOW nit) |
| `mapper/reqharness/audit.py` | source | HLR-RH.7 · LLR-RH.7.2 · R4/R14/R27a/R27d | the read-only `audit()` + `render()`: confinement before any read, cache OFF, the named `no repo` report, the per-state counts, the `--baseline` diff section |
| `mapper/app.py` | source | HLR-RH.7 · LLR-RH.7.2 | `_run_audit_cli` and its `if "--audit" in sys.argv` dispatch, ahead of the stdout re-wrap and the TUI start (kind note: small edit) |
| `mapper/reqharness/identity.py` | source | LLR-RH.7.3 · R20/R27c | the RH3 review LOW nit: the extensionless `git` candidate dropped from the Windows PATH walk (kind note: nit) |
| `tests/test_reqharness_baseline.py` | test | HLR-RH.6 · LLR-RH.6.1/6.2 | the freeze+diff node and the AT-081 CLI node (5/5 fixture mutations through the real subprocess) |
| `tests/test_reqharness_release.py` | test | HLR-RH.7 · LLR-RH.7.1/7.2 | the verdict node (5/5 byte-exact fixtures), the hand-added-document node (the RH2 nit), the AT-080 counts node, the escaping-repo confinement node, the git-refusal → named `no repo` node |
| `tests/test_reqharness_identity.py` | test | LLR-RH.7.3 · R27c | the Windows-only `test_windows_resolution_skips_extensionless_git` node (the RH3 nit) (kind note: edit) |
| `.dev-flow/2026-10-11-reqharness-batch/evidence/rh5-red.transcript` | generated | HLR-RH.7 · HLR-RH.4 (RED proof) | the 7-arm driver log and its verbatim output |

| Count | Value |
|---|---|
| **SOURCE files** | **5 / 4** (`baseline.py`, `release.py`, `audit.py` + the `app.py` edit + the `identity.py` nit) — over the 4-file cap by one, see §6 |
| Test files | 2 new + 1 node added (uncapped) |
| Doc files | 0 |

- At exactly 4 source files: the increment owns the freeze/diff/rule/
  audit slice; the `app.py` edit is the CLI surface the LLR names, and the
  `identity.py` one-liner is the orchestrator-folded reviewed RH3 nit.

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_baseline.py tests/test_reqharness_release.py tests/test_reqharness_identity.py
```

Full slice verification (the unit's command, from the transcript):

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_config.py tests/test_reqharness_chain.py tests/test_reqharness_identity.py tests/test_reqharness_registry.py tests/test_reqharness_yaml_census.py tests/test_reqharness_baseline.py tests/test_reqharness_release.py tests/test_no_operator_paths.py
python -B -m pytest -q -p no:cacheprovider tests/test_app.py tests/test_app_imports_used.py tests/test_mod_compat.py
ruff check mapper/reqharness mapper/app.py tests/test_reqharness_baseline.py tests/test_reqharness_release.py tests/test_reqharness_identity.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit / e2e CLI** | `core` · `full` | `test_baseline_freezes_commit_sha_and_diffs`, `test_at_081_baseline_vs_now_reports_new_changed_retired`, `test_release_rules_and_verdicts`, `test_verify_hand_added_document_becomes_status_not_exception`, `test_at_080_audit_report_counts_every_state_exactly`, `test_audit_cli_refuses_escaping_repo_path`, `test_audit_report_names_no_repo_on_git_refusal`, `test_identity_reader_repo_local_then_global`, `test_git_resolution_absolute_and_path_pinned`, `test_git_resolution_excludes_repo_and_cwd`, `test_windows_resolution_skips_extensionless_git`, `test_unresolvable_repo_path_is_named_no_repo_not_a_crash`, `test_failed_git_resolution_is_not_cached`, `test_safe_directory_refusal_is_named_no_repo_not_a_crash`, `test_fsmonitor_sentinel_absent_after_hardened_calls`, `test_git_index_byte_identical_after_audit_path_calls`, `test_allowlist_source_census_no_non_allowlisted_subprocess` | 17 passed |

(2 baseline + 5 release + 10 identity; the 10 identity nodes carry the
RH3 LLR-RH.7.3 surface plus this increment's nit node.)

### GREEN — executed now, from the worktree root

```bash

$ python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_baseline.py tests/test_reqharness_release.py tests/test_reqharness_identity.py
17 passed in 7.07s
```
(CLOSE1 close-out, appended: the slice was re-run after the security-nit fixes; the claimed count above is backed by the close-out transcript `.dev-flow/2026-10-11-reqharness-batch/evidence/close1-green-slice.transcript (the wide close-out re-run that covers this increment's verification command; the narrow 3-file capture rh5-green-close1.transcript also on record)`, cited in the evidence table below.)

The transcript's post-restore verification (same product state): `54
passed` on the full reqharness slice, `87 passed` on the app/compat
guard files, and the in-scope `ruff check` clean.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | seven arms, one per named negative control: M-BL1 (commit SHA omitted), M-BL2 (classification by id presence only — digest comparison disabled), M-BL3 (`deleted` collapsed into `retired`), M-BL4 (dirty flag forced, porcelain skipped), M-RL1 (`policy_verified` dropped from the mandatory census), M-AU2 (repo confinement moved after the reads), M-AU1 (`--audit` ignored by `main()` → the TUI launches → `subprocess.run(timeout=60)` raises `TimeoutExpired`, counted as FAIL — R26) |
| Instrument | `sed` one-liners per arm; restore checked by sha256 per arm |
| Where it ran | **the batch trunk (this worktree)** |
| Transcript | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh5-red.transcript` |
| Restore proven by | **file hash returned to its pre-mutation value** (sha256 before == after, printed per arm in the transcript) |
| Bytecode cache | `-B` / `PYTHONDONTWRITEBYTECODE=1` on every run |
| Arms resolved at baseline | **7** |
| Verdict granularity | per node id, printed per arm |
| Arms that stayed GREEN | none — every arm RED |

| Arm | RED evidence (transcript line) | Node it reddened | Restore digest (sha256, before == after) |
|---|---|---|---|
| M-BL1 | line 18: `FAILED …::test_baseline_freezes_commit_sha_and_diffs` (`AssertionError`) | `test_baseline_freezes_commit_sha_and_diffs` | `b96c233cd1d98…3e128eda` byte-identical |
| M-BL2 | line 27: `FAILED …::test_baseline_freezes_commit_sha_and_diffs` | `test_baseline_freezes_commit_sha_and_diffs` | `b96c233cd1d98…3e128eda` byte-identical |
| M-BL3 | lines 35–36: `FAILED …::test_baseline_freezes_commit_sha_and_diffs` + `FAILED …::test_at_081_baseline_vs_now_reports_new_changed_retired` | both baseline nodes | `b96c233cd1d98…3e128eda` byte-identical |
| M-BL4 | line 45: `FAILED …::test_baseline_freezes_commit_sha_and_diffs` | `test_baseline_freezes_commit_sha_and_diffs` | `b96c233cd1d98…3e128eda` byte-identical |
| M-RL1 | line 54: `FAILED …::test_release_rules_and_verdicts` | `test_release_rules_and_verdicts` | `736c4bd599c9…d2e51da` byte-identical |
| M-AU2 | line 64: `FAILED …::test_audit_cli_refuses_escaping_repo_path` (`AttributeError`) | `test_audit_cli_refuses_escaping_repo_path` | `62662375af1c…eb00c6c` byte-identical |
| M-AU1 | line 77: `FAILED …::test_at_080_audit_report_counts_every_state_exactly` (`TimeoutExpired` after 60 s — the TUI hung) | `test_at_080_audit_report_counts_every_state_exactly` | `2d3a252080d0…45ff204` byte-identical |

Full digests at every restore point: `baseline.py`
`b96c233cd1d9828f43d5bac9a9ca5740c3fafaf29f4d5f7899a1a66c3e128eda`,
`release.py` `736c4bd599c9e1a9f0c01145d78722c3e72d60e5c6b06f82437090d95d2e51da`,
`audit.py` `62662375af1cd0674759b02c64b89e0905fa7a263a6f37a28b7bb2e5eeb00c6c`,
`app.py` `2d3a252080d05821a7902462817de0b05924b2dd9ce7dc6c9b5dc6fd945ff204`,
`identity.py` `188bf8605f111cfe0f12033bc0aa5d2ab0471f7c332d7e7a60686b05b0d7315c`.

### Conditions this increment discharges

| Condition (review finding) | Ruling | Where discharged here |
|---|---|---|
| RH2 review LOW — a schema `ValidationError` from a tampered/hand-added document could escape the release evaluation as an exception instead of a status | R14 | `release.safe_verify` (the refusal → `chain broken` / `config changed without approval` ladder) + `test_verify_hand_added_document_becomes_status_not_exception` |
| RH3 review LOW — on Windows the PATH walk also tried a bare extensionless `git`, so a planted extensionless file could win resolution | R27c | the `identity.py` nit + `test_windows_resolution_skips_extensionless_git` (planted-extensionless-arm, Windows-only) |

### Residuals (stated, not fixed)

- Identity is self-claimed and spoofable by any committer (LLR-RH.4.4
  ceiling — discharged by RH3); the audit report prints the
  identity-ceiling sentence on every run; the layer-3 risk stays answered
  by B-122's strong mode, a named follow-up.
- Baseline creation trusts the repo's `.git/config` (R27a's stated
  residual): the dirty flag comes from `git status` inside the operator's
  own repo; `--audit` never runs it.
- The dirty flag is recorded and refuses nothing — a dirty freeze is a
  fact on the report, not an error.

### Evidence files — bytes at a declared home, verbatim, hash-verified

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| CLOSE1 close-out GREEN re-run (V56: the claimed count sits in a cited transcript) | `.dev-flow/2026-10-11-reqharness-batch/evidence/close1-green-slice.transcript` | `b3b510a33e99b4ec7abfb2775cf511a57ee13782191106bdf14661712973a089` |

_Re-pinned after a personal-path scrub of the transcript (orchestrator, 2026-10-11)._
| RED-proof transcript (account name redacted to `<profile>` per A-110) | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh5-red.transcript` | `9d443d387c4d1f7c3de86df331a841ffc7bb278caa6da252e1df7990df806eb9` |

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | reviewed by `code-reviewer` — verdict recorded in the batch's independent review rounds (`02-review.md`); findings discharged via the rulings named in this packet |

---

## 5 · Risks

- `Baseline.create` shells out to `git rev-parse HEAD` and
  `git status --porcelain` in the operator's own repo; the stated R27a
  residual (`.git/config` trust) bounds this to a repo the operator
  already trusts, and the audit path never runs it.
- The audit report renders file-derived strings (canon ids, review names,
  reported lines) as plain text lines; the report is a CLI print, not a
  TUI paint, so no markup sink exists on this path.
- `snapshot` re-derives the registry on every `--baseline` diff; at the
  batch's scale (~190-row canon) this is trivial and the audit path keeps
  the cache OFF by rule (R4), so the cost is bounded cold-parse time.

## 6 · Pending items / spec deviations

- **Source-file cap: 5 where the cap is 4.** RH5's source surface is
  `baseline.py`, `release.py`, `audit.py` **+ the `app.py` CLI edit + the
  `identity.py` nit**. Reason: the `--audit` branch in `app.main` is the
  LLR-RH.7.2-named CLI surface (it cannot live in the core without a
  console-entry reach-around), and the `identity.py` one-liner is the
  reviewed RH3 nit the orchestrator folded into this unit. Approved by the
  orchestrator under the standing authorization; recorded.
- **Merge (trunk `03a85b2`):** the orchestrator merged RH5
  (`ba24ed3`) into the batch trunk in this worktree; no textual conflicts
  — RH5 only added files plus the two small edits.
- `ruff check mapper` reports 7 PRE-EXISTING errors in files this
  increment never touched (`mapper/darkside.py`, `mapper/diff.py`,
  `mapper/office.py`, `mapper/screens/factory.py`,
  `mapper/screens/settings.py`); the in-scope scan
  (`mapper/reqharness mapper/app.py` + the three test files) is clean.
  Flagged for the orchestrator; not fixed here (outside the unit's named
  set).
- **Deferred items respected:** the `reactivated` diff class and the
  review-state progression stay **deferred (B-125)** per R24 — five
  classes plus the dirty flag ship; the committer-vs-reviewer email
  warning stays **deferred (B-124)** — `git log` remains outside the
  allowlist.

## 7 · Suggested next task

Continue the batch per `PLAN.md` — RH6a/RH8 paint the derivation, the
verdict and the named `no repo` state on the roles screen; the P4
measurements land in `04-validation.md`.

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | ≤4 source files | ⚠ | 5/4 — over the cap by one (`app.py` edit + folded `identity.py` nit); reason in §6, orchestrator-approved |
| 2 | Tests written in this same increment | ✓ | `tests/test_reqharness_baseline.py`, `tests/test_reqharness_release.py` + the identity nit node |
| 3 | Layer 0 written where the criterion applies | ✓ | 17 nodes, §4 |
| 4 | RED counterfactual declared | ✓ | 7 arms, transcript + restore digests, §4 |
| 5 | Security conditions discharged mapped to findings | ✓ | RH2-nit and RH3-nit table, §4 |
| 6 | `code-reviewer` passed | ⚠ | PENDING — §4b |
| 7 | No file from another lane touched | ✓ | one lane (this trunk); only this increment's files |
| 8 | Frozen interfaces untouched | ✓ | no ARQ §4 row changed; no keymap/seat edit; no darkside token edit |
| 9 | Coverage claims verified on disk | ✓ | GREEN line from a run executed now; claims cite the transcript |
| 10 | Residuals stated honestly | ✓ | identity ceiling, `.git/config` trust, dirty-flag-records-nothing, §4/§5 |
| 11 | Evidence files declared | ✓ | 1 row with sha256 |
| 12 | Independent review names somebody | ⚠ | PENDING |

## 8 · Code-review follow-up (RHFIX5)

`code-reviewer` (Claude Sonnet) returned REQUEST-CHANGES on RH5. The
orchestrator's rulings and the fixes, all inside the increment's named
source set (`baseline.py`, `audit.py`, `identity.py`, `app.py` CLI branch):

| Finding | Ruling | Fix | Nodes |
|---|---|---|---|
| H1 (HIGH) | `Baseline.load` iterated `document["objects"]` before typing it — `objects: null` / `objects: 5` crashed `mapper --audit --baseline` with a traceback; validate every field, defence in depth in the CLI | `objects` is isinstance-checked as a list before the row loop (rows were already typed); `_run_audit_cli` catches `Exception` around the audit call → one line `audit: internal error (<ExceptionType>)` on stderr, exit 1, no traceback | `test_baseline_load_refuses_untyped_objects_and_bad_name`, `test_audit_cli_baseline_schema_violation_is_named_not_a_traceback` |
| M1 | `_confine_repo` checked the path against its own parent (vacuous) and refused `..`; the repo argument is the operator's choice | `_confine_repo` resolves the argument as given (relative / `..` allowed), refuses a LINK in the argument by name, requires an existing directory; the toplevel comes from `git rev-parse --show-toplevel`; `baseline.confinement_sweep` confines every registry read under `<toplevel>/reqharness/` and `REQUIREMENTS.md` — a file or link resolving outside is refused by name. `Baseline.load`/`_write` confinement re-homed onto `_resolve_inside` (same rule) because the osopen-import census pins baseline/audit out of osopen | `test_audit_cli_resolves_relative_repo_argument`, `test_audit_cli_refuses_baseline_link_escaping_repo` (existing escaping-repo test kept green) |
| M2 | a missing / non-UTF-8 `REQUIREMENTS.md` hid the chain status | `audit()` catches the canon `ValidationError`: the report still prints the chain/policy status and the per-state counts it can compute, plus the named not-ready line `canon unreadable: <reason>`; exit 1 | `test_audit_report_prints_chain_status_when_canon_unreadable` |
| L1 | doubled `audit: audit:` prefix | one prefix only — the refusal messages no longer carry it (the CLI adds it); exact line asserted | `test_audit_cli_refusal_line_has_one_prefix` |
| L2 | `Baseline.load` did not validate `name` | loaded `name` carries `create`'s rule: no `/`, `\`, `..` | `test_baseline_load_refuses_untyped_objects_and_bad_name` |
| L3 | `_which_git` on Windows with empty `PATHEXT` tried no names | empty/unset `PATHEXT` falls back to `.COM;.EXE;.BAT;.CMD` | `test_windows_resolution_falls_back_when_pathext_empty` |
| L4 | — (no code) | **Ruling: retired-before-changed precedence is intended.** `diff` classifies `retired` when the object turned retired even if its normative digest also moved; a withdrawal dominates the digest comparison (precedence 3 of the diff, matching the derivation's R5 table where `retired` is assigned before any review/digest state). | stated here, per the finding |

RED proof: each fix reverted alone (product change only), its node(s)
confirmed FAIL, the file restored byte-identically (sha256 compared
against the green-state backup), the node GREEN again. Evidence:
`evidence/rh5fix-red.transcript`, sha256
`b28943f3bb4ee967d69d317e5e466c42963f7e76ac6d19606a5549e3e384d08c`.
Note on the M1 link node: at the pre-fix tree it stays GREEN because the
pre-existing `Baseline.load` confinement refused the escaping symlink by
itself — the sweep is defence in depth over the config/roles/reviews/canon
reads; the relative-argument node is the one that reddens (the vacuous
`_confine_repo` actively refused `..`).

Verification (restored tree):
`python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_*.py
tests/test_no_operator_paths.py tests/test_app.py tests/test_mod_compat.py
tests/test_arch_osopen_callers.py tests/test_mod_deps.py` → **89 passed**;
`ruff check mapper/reqharness mapper/app.py` → clean. Not committed (the
orchestrator commits).

### Re-review follow-up (RHFIX5B)

The Sonnet re-review REQUEST-CHANGES on RH5 reopened one HIGH and one LOW,
both fixed in `mapper/reqharness/baseline.py` only (source set respected —
RH6a is another lane):

| Finding | Fix | Nodes |
|---|---|---|
| HIGH: `--baseline` name traversal — `mapper --audit . --baseline ../../../outside/y` opened and PARSED a file outside the toplevel (the name rule ran only on the stored `name` field after reading; `_resolve_inside` treated `..` as a plain component and never checked the final path) | `create`'s name rule (new `_check_baseline_name`) is applied to the INCOMING `name` at the TOP of `Baseline.load` and `Baseline._write`, before any path is built | `test_audit_cli_baseline_name_traversal_is_refused_by_name` (both `/` and `\` spellings, real console entry in a subprocess with an `outside/y.yml` marker: exit 1, `refused (name)`, the marker NOT in stdout/stderr, no traceback) |
| LOW: `_resolve_inside` returned the lexical path | `_resolve_inside` asserts the FINAL RESOLVED path is under the resolved root (`refused (outside)`) and returns the resolved path | `test_resolve_inside_refuses_lexical_dotdot_escape` |

M2 confirmation (no code change): `test_audit_report_prints_chain_status_when_canon_unreadable`
already drives a VALID registry plus an unreadable `REQUIREMENTS.md` (missing, then
non-UTF-8) through the real console entry to the `canon unreadable: <reason>` line —
verified GREEN; the node needed no addition.

RED proof (both new nodes, product change reverted to HEAD, restored
byte-identically): `evidence/rh5fix-red.transcript` (appended RHFIX5B
section; pre-fix RED output shows the outside file was parsed —
`missing key(s): commit, created, dirty, ...`).

Verification (restored tree):
`python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_baseline.py
tests/test_reqharness_release.py tests/test_no_operator_paths.py tests/test_app.py`
→ **30 passed**; `ruff check mapper/reqharness` → clean. Not committed
(the orchestrator commits).

---

## 9 · DDR follow-up note (ARCH C2 — appended, not a rewrite)

This increment's §1 and §2 said the `--audit` branch sits in `app.main` "ahead
of" the `app.py:328` UTF-8 stdout re-wrap. The corrected ruling is that the
branch runs **AFTER** the UTF-8 stdout re-wrap, so the report prints in UTF-8
(ledger `LED-2026-10-11-reqharness-batch.34`; PDR DDR amendments §A row 7). The
live contract (`01-requirements.md` LLR-RH.7.2, the IFC FLOW audit-cli, §2.5)
and the design proposal (§2 module table, §3.1, §4) now state the corrected
order. The shipped `app.main` branch already re-wraps first; nothing in §1–§8
was rewritten.
