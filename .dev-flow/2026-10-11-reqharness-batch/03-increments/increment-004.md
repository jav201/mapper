# Increment 004 — HLR-RH.4 / HLR-RH.5 · `Reviews + pending stores + content-keyed cache + derived states`

| Field | Value |
|---|---|
| Batch | `2026-10-11-reqharness-batch` |
| Increment | `004` (RH4) |
| Lane (if the batch forked) | none — one lane, trunk unit RHI4 |
| Requirement(s) | HLR-RH.4 / HLR-RH.5 · LLR-RH.4.1–4.6 · LLR-RH.5.1–5.3 · rulings R4/R5/R6/R8/R22 |
| Acceptance | layer-0 unit nodes (the executed verification named in `01-requirements.md` §3 for HLR-RH.4/HLR-RH.5) |
| Agent | `software-dev` (Kimi, kimi-code) |
| Date | `2026-10-11` |

---

## 1 · What changed

BLUF: the ReqHarness core now derives the registry. Four new modules —
`reviews.py` (the immutable, content-named review event store), `pending.py`
(the pending-request read side with the resolution DERIVED from the chain),
`cache.py` (the content-keyed parse cache inside `.git/reqharness-cache/`),
`derive.py` (the canon reader + the five-state derivation under the R5
precedence table) — plus three small `chain.py` edits the design's R6
requires. Tests: `tests/test_reqharness_registry.py`, 9 nodes.

Mechanism, per LLR:

- **LLR-RH.4.1/4.2/4.3 (R5)** — `derive.py` binds a review to the object's
  NORMATIVE digest (sha256 of the canonical JSON of `{field: normalised
  value}` over the config-declared normative fields — never a concatenation,
  never folded with the informative fields) and to the chain head
  (`roles_seq` + `roles_hash`). A human review closes only when the signer
  held the class's `reviewer_role` in the VERIFIED chain at the BOUND HEAD
  (`effective_roles(report, roles_seq, roles_hash)` — never today's head);
  `kind: model` is self-declared and always pre-review. A newer pre-review
  never downgrades a qualifying human review on the same digest
  (precedence 2); a stale digest never closes; unentitled reviews are
  counted apart (by review file name) and never block alone; the informative
  edit raises the visible `changed (informative)` mark without touching the
  state. R17 old-head binding is a non-blocking WARN line.
- **LLR-RH.4.5/4.6 (R8/R22)** — review files are one immutable event per
  file, named `<yyyymmdd>-<sha8 of canonical content>.yml` from canonical
  content only (no name parameter — M-FN1), exclusively created; the loader
  recomputes sha8 over the canonical content of every file — a mismatch is
  reported BY NAME and non-closing. Links/junctions under `reqharness/` are
  refused via `mapper.osopen.confine_reason`/`is_link` (the one containment
  edge); the ≤ 64 KB / ≤ 100 000-file limits reuse the chain's confined
  reader and the shared `scan_event_dir`.
- **LLR-RH.5.1/5.2** — the minimal canon reader parses the
  `REQUIREMENTS.md` table by its header row (`Id`/`Status` required; every
  other column becomes a field, so a fixture canon can carry a `Rationale`
  column the informative digest binds to). Withdrawn ids (status starting
  with `withdrawn`) derive `retired` and are excluded from active counts; an
  unparseable row is REPORTED by line and derives no state; an empty canon
  derives zero states on a genesis-only chain. `not verifiable` (chain/policy
  break, unknown recorded heads) dominates every outcome — the derivation
  returns `verifiable=False` with empty states.
- **LLR-RH.5.3 (R4)** — the parse cache lives inside
  `.git/reqharness-cache/reviews.json`, keyed by sha256(file bytes), caching
  PARSING only: a cached parse that fails the schema or the R22 name check
  is busted and re-parsed from the bytes, so a poisoned entry or a corrupt
  cache file is bounded to a re-parse — never a verdict change — and
  deleting the cache changes no result. It is active only where `.git`
  exists (its declared home); `ParseCache.disabled()` is the audit state
  (cache OFF, writes nothing — `--audit` lands in RH5).
- **R6 (HLR-RH.2 arm)** — `pending.py` derives each request's resolution by
  replaying the VERIFIED chain prefix for an event referencing the request's
  canonical digest: a `grant`/`revoke` applying the held change is
  `approved`, a `resolution` event (empty change) is `rejected`, else
  `pending`. The file stays on disk; the derivation survives restarts. The
  three required `chain.py` edits: `approve_pending` now appends the change
  WITH `request_hash = <request digest>`; a new `reject_pending` appends the
  `resolution` event with an empty change; `_OPTIONAL_BY_ACTION` admits
  `request_hash` on `grant`/`revoke` (the key appears only on the events
  that need it — a grant/revoke that lands a pending request).

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/reqharness/reviews.py` | source | HLR-RH.4 · LLR-RH.4.5/4.6 · R8/R9/R22 | the review event store: `record_review` (content-named, exclusive create), `load_reviews`/`scan_event_dir` (named refusals, sha8 recompute, cache-accelerated), `ReviewEvent`/`ReviewScan` |
| `mapper/reqharness/pending.py` | source | HLR-RH.2 arm · R6/R8/R22 | the pending read side: `list_pending`/`load_pending` (schema + name/content check), `resolution()` — the chain-derived a/r derivation |
| `mapper/reqharness/cache.py` | source | HLR-RH.5 · LLR-RH.5.3 · R4 | the content-keyed parse cache inside `.git/reqharness-cache/`: `ParseCache.open/disabled`, bust+re-parse on failed re-validation, corrupt-file rebuild |
| `mapper/reqharness/derive.py` | source | HLR-RH.5 · LLR-RH.4.1/4.2/4.3 · R5/R14/R17 | the canon reader (`parse_canon`/`load_canon`, header-row column mapping, named unparseable rows) and `derive_states` — the five-state partition under the explicit precedence table |
| `mapper/reqharness/chain.py` | source | LLR-RH.2.2 · R6 (required by the design) | `approve_pending` appends `request_hash`; new `reject_pending` (resolution event, empty change); `_OPTIONAL_BY_ACTION` admits `request_hash` on grant/revoke (kind note: small edit) |
| `tests/test_reqharness_registry.py` | test | HLR-RH.4/HLR-RH.5 | the 9 named layer-0 nodes (8 from the requirements' executed verification + the R6 pending-resolution node) |
| `tests/test_arch_osopen_callers.py` | test | R8/R19 (the ARQ amendment already on disk) · LLR-RH.7.2 | **pre-existing trunk failure fixed**: the AST census allowlist gains the `reqharness/chain.py` → `confine_reason` and `reqharness/reviews.py` → `confine_reason`/`is_link` rows the amended ARCHITECTURE §3 declares as the core's single inbound edge; the merged RH2/RH3 trunk left this census stale and it failed on every run (kind note: census allowlist) |
| `.dev-flow/2026-10-11-reqharness-batch/evidence/rh4-red.driver.sh` + `rh4-red.transcript` | generated | HLR-RH.4 · HLR-RH.5 (RED proof) | the 8-arm driver and its verbatim output |

| Count | Value |
|---|---|
| **SOURCE files** | **5 / 4** (`reviews.py`, `pending.py`, `cache.py`, `derive.py` + `chain.py`) — over the 4-file cap by one, see §6 |
| Test files | 1 new + 1 census-row fix (uncapped) |
| Doc files | 0 — the ARQ amendment is already on disk from the batch's ARQ act (R19) |

- At exactly 4 source files: the increment owns the review/pending/cache/
  derivation slice; each module is a distinct LLR cluster with one public
  surface, and `chain.py`'s write path stays the only place roles.yml grows.

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_registry.py
```

Full slice verification (the unit's command):

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_*.py tests/test_no_operator_paths.py tests/test_arch_osopen_callers.py tests/test_mod_deps.py
ruff check
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `test_normative_edit_needs_review_informative_marks_only`, `test_review_by_signer_without_role_in_force_is_pre_reviewed`, `test_model_review_never_closes_state`, `test_review_file_naming_and_exclusive_create`, `test_derived_states_boundary_catalog`, `test_review_parse_cache_is_pure_accelerator`, `test_never_yaml_load_source_census`, `test_identity_reader_repo_local_then_global`, `test_pending_resolution_derived_from_chain_reference` | 9 passed |

### GREEN — executed now, from the worktree root

```bash

$ python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_*.py tests/test_no_operator_paths.py tests/test_arch_osopen_callers.py tests/test_mod_deps.py
59 passed in 11.99s
$ ruff check mapper/reqharness/ tests/test_reqharness_registry.py tests/test_arch_osopen_callers.py
All checks passed!
```
(CLOSE1 close-out, appended: the slice was re-run after the security-nit fixes; the claimed count above is backed by the close-out transcript `.dev-flow/2026-10-11-reqharness-batch/evidence/rh4-green-close1.transcript`, cited in the evidence table below.)

(59 = the 9 new nodes + RH1/RH2/RH3's 41 + the four guard files; the
`test_arch_osopen_callers.py` arm was failing on the merged trunk before
this increment — see §2.)

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | eight arms, one per named negative control: M-RG1 (informative folded into the normative digest), M-RG2 (role checked at today's head), M-RG3 (model reviews close), M-RG4 (withdrawn id not retired), M-RG5 (cached parse feeds the verdict — no bust/re-parse), M-FN1 (file named from a caller-side slug), M-FN2 (sha8 content check skipped), M-PR1 (non-admin resolution lands) |
| Instrument | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh4-red.driver.sh`; restore checked by sha256 per arm |
| Where it ran | **my own worktree** |
| Transcript | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh4-red.transcript` |
| Restore proven by | **file hash returned to its pre-mutation value** (sha256 before == after, printed per arm in the transcript) |
| Bytecode cache | `-B` / `PYTHONDONTWRITEBYTECODE=1` on every run |
| Arms resolved at baseline | **8** |
| Verdict granularity | per node id, printed per arm |
| Arms that stayed GREEN | none — every arm RED |

| Arm | RED evidence (transcript line) | Node it reddened | Restore digest (sha256, before == after) |
|---|---|---|---|
| M-RG1 | line 19: `FAILED …::test_normative_edit_needs_review_informative_marks_only` | `test_normative_edit_needs_review_informative_marks_only` | `fe56ec169d86…0f132` byte-identical → 9 passed |
| M-RG2 | line 30: `FAILED …::test_review_by_signer_without_role_in_force_is_pre_reviewed` (`'reviewed' == 'pre-reviewed'`) | `test_review_by_signer_without_role_in_force_is_pre_reviewed` | `fe56ec169d86…0f132` byte-identical → 9 passed |
| M-RG3 | line 41: `FAILED …::test_model_review_never_closes_state` | `test_model_review_never_closes_state` | `fe56ec169d86…0f132` byte-identical → 9 passed |
| M-RG4 | line 52: `FAILED …::test_derived_states_boundary_catalog` | `test_derived_states_boundary_catalog` | `fe56ec169d86…0f132` byte-identical → 9 passed |
| M-RG5 | line 63: `FAILED …::test_review_parse_cache_is_pure_accelerator` | `test_review_parse_cache_is_pure_accelerator` | `f6da682de3b4…8344b7` byte-identical → 9 passed |
| M-FN1 | line 74: `FAILED …::test_review_file_naming_and_exclusive_create` (`'20261011-0000000e.yml' == '20261011-d304f98e.yml'`) | `test_review_file_naming_and_exclusive_create` | `f6da682de3b4…8344b7` byte-identical → 9 passed |
| M-FN2 | line 85: `FAILED …::test_review_file_naming_and_exclusive_create` | `test_review_file_naming_and_exclusive_create` | `f6da682de3b4…8344b7` byte-identical → 9 passed |
| M-PR1 | line 95: `FAILED …::test_pending_resolution_derived_from_chain_reference` (`DID NOT RAISE ValidationError`) | `test_pending_resolution_derived_from_chain_reference` | `c57838caf6d2…1a0fd98` byte-identical → 9 passed |

Full digests at every restore point: `derive.py`
`fe56ec169d86d41cba1a102a94ec8eec4b621c375bd9a6074ecf0dd59270f132`,
`reviews.py` `f6da682de3b4499ac58535dd3b22fa826342690bd89ebdb325ef3d99378344b7`,
`chain.py` `c57838caf6d22506ca5e927b9a5b0f564fa7106ddf0258d02bf818e271a0fd98`.

### Conditions this increment discharges

| Condition (review finding) | Ruling | Where discharged here |
|---|---|---|
| Round-1 architect H4 (normative/informative digests; unentitled never blocks) | R5 | LLR-RH.4.1/4.2 nodes + M-RG1/M-RG2 arms |
| Round-1 architect M6 (precedence ambiguity) | R5 | the explicit precedence in `derive_states` (`not verifiable` dominates; newer pre-review never downgrades; stale digest never closes) + boundary-catalog node |
| Round-1 qa QM7 (model reviews) | R5 | LLR-RH.4.3 node + M-RG3 arm (the fixture's model signer HOLDS the role — `kind` alone keeps it a pre-review) |
| Round-1 architect M3/M5 + security F8 (content-named files, exclusive create, confinement) | R8 | LLR-RH.4.6 node + M-FN1 arm + the junction-refusal arm |
| Round-2 security limb (sha8 recomputed at read) | R22 | the name/content-mismatch arms of M-FN2 (review and pending) — reported by name, non-closing |
| Round-1 architect H5 + qa QH1/QH2 (pending persistence + resolution) | R6 | `pending.resolution` + the R6 node (approve/reject/restart/own-request/non-admin arms) + M-PR1 arm |
| Round-1 architect H3 + security F4 + qa QM2/QM3 (cache) | R4 | LLR-RH.5.3 node: cache on/off/deleted/poisoned/corrupt/content-modified arms, all bounded to a re-parse + M-RG5 arm |
| Round-1 security F6 + qa QM1 (limits, named refusals) | R9 | the shared `scan_event_dir` (≤ 100 000 files, link refusal) + the confined ≤ 64 KB reader; syntax-malformed review/pending kinds named in the boundary node |
| Round-2 qa MED-1 (corrupted review file at derive time; corrupt cache file) | R26 | boundary-catalog + pure-accelerator nodes |

- The architect findings H1/H2 (policy binding, canonical form) are
  DISCHARGED BY RH1/RH2 — not by this one; claiming them here would be false.

### Residuals (stated, not fixed)

- Identity is self-claimed and spoofable by any committer (LLR-RH.4.4
  ceiling — discharged by RH3); the layer-3 risk stays answered by B-122's
  strong mode, a named follow-up.
- The parse cache is keyed by sha256(file bytes) but a writer with repo
  access can rewrite a review AND its name consistently (layer 3 — same
  answer as the chain).
- `reviewer` is free text; entitlement is the role at the bound head, never
  proven from the file.
- The LLR-RH.5.4 warm-cache budget (≤ 0.5 s median for 5 000 events / 2 000
  requirements) is a P4 measurement, not a suite assertion — the suite
  asserts output equality only (LLR-RH.5.3), per the ruling.

### Evidence files — bytes at a declared home, verbatim, hash-verified

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED-proof transcript (account name redacted to `<profile>` per A-110) | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh4-red.transcript` | `b2f6d82d03b91cc1f8f8954918fe4b13694c1508c6c7c7f0ab611372caf54a10` |
| RED-proof driver (the instrument) | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh4-red.driver.sh` | `519c503fbb7870f81b613cd65b43e6f7eaac87981343992f5cac0addf98c3621` |
| CLOSE1 close-out GREEN re-run (V56: the claimed count sits in a cited transcript) | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh4-green-close1.transcript` | `a88671c9273b4dfd2a8731bc5b0aa6a354075563a01c199240871e2bff931522` |

_Re-pinned after a personal-path scrub of the transcript (orchestrator, 2026-10-11)._

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | reviewed by `code-reviewer` — verdict recorded in the batch's independent review rounds (`02-review.md`); findings discharged via the rulings named in this packet |

---

## 5 · Risks

- The review `seq` is allocated by re-scanning the reviews directory
  (`next_seq`); at the batch's scale (~190-row canon, human-paced reviews)
  the scan is trivial, and the cache amortizes it in real registries. A
  pathological many-thousand-event registry would amortize via the cache.
- `parse_canon` maps columns by the header row; a canon table that renames
  the `Id`/`Status` columns derives zero objects plus a named header report
  (never a silent wrong answer). The tolerant canon adapter is follow-up
  (D5/D9) by ruling.
- The bulk fixture (250 events) exercises cold/warm equality at suite scale;
  the 5 000-event budget remains the P4 measurement (LLR-RH.5.4).

## 6 · Pending items / spec deviations

- **Source-file cap: 5 where the cap is 4.** RH4's source surface is
  `cache.py`, `derive.py`, `pending.py`, `reviews.py` **+ `chain.py`**.
  Reason: the pending request's resolution is DERIVED from the chain by
  replaying verified chain events (R6), so the write side that lands a
  resolution — `approve_pending` appending the change with `request_hash`,
  the new `reject_pending` appending the `resolution` event, and
  `_OPTIONAL_BY_ACTION` admitting `request_hash` on grant/revoke — belongs in
  the chain verifier, not in a fifth module that would have to reach into
  chain-internal append machinery. `pending.py` stays the read side.
- **Merge resolution (trunk fb4ea82 × unit/rh4, 2026-10-11):** the trunk's
  security fixes are kept verbatim — genesis pinned to walk position 1 in
  `_check_event`, the `_passes_approval` genesis shortcut holding only with no
  prefix, `_roles_in_force` folding on the event's own `seq <= bound_seq`,
  `config_hash` required on genesis/policy. rh4's resolution logic is added
  on top: `_pending_digest`, `reject_pending`, `request_hash` on
  approve/grant/revoke. The one textual conflict was the optional-key comment
  block; combined so both behaviours hold (config_hash REQUIRED on
  genesis/policy per F3; request_hash on `resolution` AND on grant/revoke
  that land one per R6). Post-merge RED proof both sides still bite:
  M-CH6 → `test_genesis_only_at_position_one` RED, M-PR1 →
  `test_pending_resolution_derived_from_chain_reference` RED, each restored
  byte-identical (evidence `rh4-merge-red.transcript` in this batch's
  evidence home).
- `test_identity_reader_repo_local_then_global` exists in BOTH
  `tests/test_reqharness_identity.py` (RH3, LLR-RH.7.3) and this file
  (HLR-RH.4's executed verification lists it among the registry nodes). The
  two implementations are independent fixtures over the same public seam; no
  shared state, no import of one test into another (which would double-
  collect).
- One pre-existing trunk failure was fixed inside this unit's mandated
  verification surface: `tests/test_arch_osopen_callers.py`'s osopen-import
  census was left stale by the merged RH2/RH3 trunk (the ARQ amendment
  declared the `reqharness` → `osopen` edge but the AST allowlist was never
  updated). The fix adds the two declared rows — a test-census edit, no
  product change. Flagged for the orchestrator since it touches a file
  outside the increment's named set; it is required for the unit's own
  verification command to pass.
- Release-rule evaluation over these states (`all_active_reviewed`, the
  `not ready · …` verdicts, AT-080) is RH5 — this increment stops at the
  derivation boundary on purpose.

## 7 · Suggested next task

Continue the batch per `PLAN.md` — RH5 (baselines + release rules +
`--audit`) consumes `derive.Derivation` directly; RH6a paints it.

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | ≤4 source files | ⚠ | 5/4 — over the cap by one (`chain.py` counted in full); reason in §6 |
| 2 | Tests written in this same increment | ✓ | `tests/test_reqharness_registry.py` |
| 3 | Layer 0 written where the criterion applies | ✓ | 9 nodes, §4 |
| 4 | RED counterfactual declared | ✓ | 8 arms, transcript + restore digests, §4 |
| 5 | Security conditions discharged mapped to findings | ✓ | H3/H4/M6/QM7/F8/R22/R26 table, §4 |
| 6 | `code-reviewer` passed | ⚠ | PENDING — §4b |
| 7 | No file from another lane touched | ✓ | one lane; only this increment's files (+ the flagged stale-census fix, §6) |
| 8 | Frozen interfaces untouched | ✓ | no ARQ §4 row changed; no keymap/seat edit |
| 9 | Coverage claims verified on disk | ✓ | GREEN line from a run executed now; claims cite the transcript |
| 10 | Residuals stated honestly | ✓ | identity ceiling, layer 3, free-text reviewer, P4 budget, §4/§5 |
| 11 | Evidence files declared | ✓ | 2 rows with sha256 |
| 12 | Independent review names somebody | ⚠ | PENDING |

---

## 8 · Code-review follow-up (RHFIX4 — REQUEST-CHANGES remediation)

| Field | Value |
|---|---|
| **Review** | Independent code review (Claude Sonnet) — REQUEST-CHANGES on RH4 |
| **Transcript** | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh4fix-red.transcript` — sha256 `29198921dbdcfd3d3d2109b9a4fdefdf363dffe050af3bd0f1e2480fccc1298e` |

### Findings → fixes

| Finding | Fix | New test node(s) |
|---|---|---|
| H1 — a pending request could be resolved twice (`approve_pending`/`reject_pending` appended without checking the verified chain for an event already referencing the `request_hash`) | `_check_request_open` scans the verified prefix for the digest before any append; refusal `request already resolved` (double approve, reject-after-approve and approve-after-reject are the same refusal) | `tests/test_reqharness_chain.py::test_pending_request_resolved_once` |
| H2 — `cache.py` cached the RAW parse before validation, so a refused file (e.g. unquoted `time: 2026-10-11` → a YAML date) parked a non-serialisable value in the store and `save()` could raise `TypeError` | `parse` remembers nothing; the consumer validates (typed schema + R22 name check) and calls the new `remember()` — the ONLY store path; `save()` catches `(OSError, TypeError, ValueError)` and never raises | `tests/test_reqharness_registry.py::test_review_cache_caches_validated_parses_only` |
| M1 — the write side loaded pending files with its own schema and no R22 name/content check | `approve_pending`/`reject_pending` now use the read side's ONE shared validator (`pending.load_pending`) — a name/content-mismatched file is refused by name | `tests/test_reqharness_chain.py::test_pending_resolution_refuses_name_content_mismatch` |
| M2 — the pending schema/validator was duplicated in `chain.py`; `reviews.check_int` duplicated `config.check_int` | the validator lives only in `pending.py`; `chain.py` imports it LAZILY inside `_pending_request` (a module-level import would close the cycle `chain ↔ pending`, since `pending.py` imports `PENDING_DIR`/`ChainReport`/`read_event_file` from chain); chain's duplicate `_load_pending`/`_pending_digest`/`_PENDING_KEYS`/`_check_exact_keys` are removed; `reviews.py` imports `check_int` from `config` (read-only; `config.py` untouched) | covered by the two chain nodes above |
| L1 — `cache.py`'s docstring overclaimed ("caches PARSING ONLY … bounded to a re-parse") while the code cached raw parses | the docstring now states what the cache holds (validated parses keyed by content hash) and the residual explicitly: a poisoned entry requires local `.git` write access and is bounded by the later schema + name checks; the file NAME pins only sha8 while the cache key is full sha256 — a deliberate sha8 collision could alias two names (R22's 32-bit pin) | docstring-only (plus the H2 node guards the mechanism) |
| L2 — the cache file was capped by `LIMIT_ROLES_YML_BYTES` (4 MB), too small to persist at the 100 000-review scale | new named constant `LIMIT_CACHE_FILE_BYTES = 64 * 1024 * 1024`; `save(*, limit=...)` accepts an injected limit for the guard test | `tests/test_reqharness_registry.py::test_review_cache_size_guard_is_separate_limit` |
| L3 — stray `where_kind` in `record_review`; free-text fields written without a type check | `where_kind` removed; `record_review` type-checks `verdict`, `reviewer` and `object_id` with `check_str` before any write | `tests/test_reqharness_registry.py::test_record_review_type_checks_text_fields` |

### RED proof

Per file (each fix group reverted to HEAD, its node run RED, restored
byte-identical by sha256, run GREEN); commands, outputs and restore digests
in the transcript above. Final verification: `69 passed` on
`tests/test_reqharness_*.py tests/test_no_operator_paths.py
tests/test_arch_osopen_callers.py tests/test_mod_deps.py` + `ruff check
mapper/reqharness` clean.

### Source-file cap (M3)

5/4 — approved by the orchestrator under the standing authorization:
pending resolution belongs in the chain verifier; recorded.
