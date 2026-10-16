# Increment 001 — RS1a · data layer (record + config + derive)

> **Artifact language.** English.

| Field | Value |
|---|---|
| Batch | `2026-10-15-review-screen-batch` |
| Increment | `001` |
| Lane (if the batch forked) | none — one lane |
| Requirement(s) | HLR-RS.5 · LLR-RS.5.1 · LLR-RS.5.2 · LLR-RS.2.1 (the `owning_batch` record field, F1) |
| Acceptance | white-box `TC-RS-5.1.1` `TC-RS-5.2.1` · unit nodes `test_config_refuses_an_unknown_person_in_authors` `test_config_refuses_duplicate_person_id_and_duplicate_email_sha256` `test_authors_map_changes_config_hash` `test_an_authors_less_config_hashes_byte_identically_to_today` `test_create_registry_seeds_authors_and_authors_declared` `test_record_review_roundtrips_the_optional_owning_batch` `test_derive_marks_an_authors_human_review_unentitled` `test_derive_marks_a_stored_owning_batch_mismatch_unentitled` |
| Agent | `software-dev` (deepseek-v4-pro) |
| Date | `2026-10-15` |

---

## 1 · What changed

RS1a — the ReqHarness **data layer** for the self-review prohibition (HLR-RS.5): the review record
gains an optional `owning_batch` field (F1), the config gains an optional `authors` map (validated against
`people`, part of `config_hash` when non-empty), and `derive` marks a human review `unentitled` for any of
three causes — `no_role`, `author`, `owning_batch_mismatch`. `records.py` gains `SigningRefused` (a
`ValidationError` subclass) and the stable reason-code literals. No behaviour change for a registry that
never declares authorship (empty/absent `authors` is omitted from `canonical_config`, and a legacy review
record without `owning_batch` loads and derives exactly as today). Per R18 (the re-split), `signing.py` and
`release.py` are RS1b (the logic layer) — not touched here.

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/reqharness/reviews.py` | source | HLR-RS.5 · LLR-RS.2.1 (F1) | `record_review` gains optional `owning_batch`; `ReviewEvent.owning_batch` (default `""`); `_REVIEW_KEYS` + `_REVIEW_REQUIRED_KEYS`; loader reads it optionally |
| `mapper/reqharness/records.py` | source | HLR-RS.5 · LLR-RS.2.1 | `SigningRefused(ValidationError)` with `.reason` + `.fields`; `REASON_NO_ROLE`/`REASON_AUTHOR`/`REASON_OWNING_BATCH_MISMATCH`; `Config.authors` field |
| `mapper/reqharness/config.py` | source | HLR-RS.5 · LLR-RS.5.1 | optional `authors` schema + validation (unknown person / duplicate person id / duplicate `email_sha256` refused by name); `create_registry` seeds `authors: {}`; `canonical_config` folds `authors` only when non-empty |
| `mapper/reqharness/derive.py` | source | HLR-RS.5 · LLR-RS.5.2 | `CanonObject.owning_batch`; `Derivation.unentitled_reasons` + `authors_missing`; `_unentitled_reasons` (three causes); legacy records evaluated as today |
| `tests/test_reqharness_registry.py` | test | LLR-RS.5.1/5.2 · LLR-RS.2.1 | 8 new nodes (see header) |
| `.dev-flow/2026-10-15-review-screen-batch/PLAN.md` | doc | — | R18 + Roadmap RS1a/RS1b re-cut |
| `.dev-flow/2026-10-15-review-screen-batch/01-requirements-ledger.md` | doc | — | LED `.20` |
| `.dev-flow/2026-10-15-review-screen-batch/01-requirements.md` | doc | — | §2.8 + §5.1 increment assignment |
| `.dev-flow/2026-10-15-review-screen-batch/design/design-proposal.md` | doc | — | §5 + §8 increment assignment |
| `.dev-flow/2026-10-15-review-screen-batch/evidence/rs1a-red.transcript` | generated | HLR-RS.5 · LLR-RS.5.1 · LLR-RS.5.2 | RED mutation battery |

| Count | Value |
|---|---|
| **SOURCE files** | **4 / 4** |
| Test files | 1 (uncapped) |
| Doc files | 5 (outside the count) |

- ⚠ **At exactly 4 source files:** each file is a distinct data surface (record schema · exception · config
  schema · derivation); the RS1b logic (`signing.py`, `release.py`) is the orchestrator/rule layer over them,
  split off by R18.

## 3 · How to test

```bash
env -u NO_COLOR -u TERM python -B -m pytest -q -p no:cacheprovider \
  tests/test_reqharness_*.py tests/test_no_operator_paths.py \
  tests/test_requirements_canon.py tests/test_arch_osopen_callers.py \
  tests/test_mod_deps.py
env -u NO_COLOR -u TERM python -B -m ruff check mapper/reqharness
```

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| 0 · unit | core · full | `test_config_refuses_an_unknown_person_in_authors` · `test_config_refuses_duplicate_person_id_and_duplicate_email_sha256` · `test_authors_map_changes_config_hash` · `test_an_authors_less_config_hashes_byte_identically_to_today` · `test_create_registry_seeds_authors_and_authors_declared` · `test_record_review_roundtrips_the_optional_owning_batch` · `test_derive_marks_an_authors_human_review_unentitled` · `test_derive_marks_a_stored_owning_batch_mismatch_unentitled` | 8 passed |
| A · white-box | core · full | TC-RS-5.1.1 → the 5 config nodes; TC-RS-5.2.1 → the 2 derive nodes | 7 passed |

GREEN line (full gate run): `115 passed, 1 warning in 101.31s` · `ruff check mapper/reqharness` → `All checks passed!`

### RED counterfactual — executed, not predicted

| Mutation | RED node | RED verdict | Restore digest (sha256, byte-identical) |
|---|---|---|---|
| M-RS24 — delete the `authors` fold from `canonical_config` | `test_authors_map_changes_config_hash` | FAILED (`fa46d573…74b != fa46d573…74b`) | `e7fd2c02…3a72` EQUAL |
| M-RS18 — `if False and …` the `author` arm in `_unentitled_reasons` | `test_derive_marks_an_authors_human_review_unentitled` | FAILED (`'reviewed' == 'pre-reviewed'`) | `78c35103…67a9` EQUAL |
| F1 — `if False and …` the `owning_batch_mismatch` arm | `test_derive_marks_a_stored_owning_batch_mismatch_unentitled` | FAILED (`'reviewed' == 'pre-reviewed'`) | `78c35103…67a9` EQUAL |
| m2 — delete the duplicate `email_sha256` refusal loop | `test_config_refuses_duplicate_person_id_and_duplicate_email_sha256` | FAILED (`DID NOT RAISE ValidationError`) | `4c85ce32…caad` EQUAL |

Every mutant: mutate → node RED → restore (sha256 equal) → GREEN. Full transcript at
`evidence/rs1a-red.transcript` (sha256 `525fac9a…1895cf`).

### Reverse census — trigger family B, and A3

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by other tests | `grep -rl "SigningRefused\|owning_batch\|REASON_AUTHOR\|REASON_OWNING_BATCH_MISMATCH\|config.authors" tests/` | `tests/test_reqharness_registry.py` only (this increment's additions) |
| B2 file moved on disk | n/a (no file moves) | none |
| B3 byte-identical golden captures this source | `grep` goldens for the new symbols | none (no golden captures `reqharness`) |
| B4 artifact produced here consumed elsewhere | `grep -rn "owning_batch\|config.authors\|SigningRefused" mapper/ --include=*.py` minus owning modules | none — `authors_missing`/`unentitled_reasons` are produced by `derive` and consumed by RS1b's `release.py` (not yet written) |
| A3 interface consumed by another module changed | `Config.authors`, `ReviewEvent.owning_batch`, `Derivation.unentitled_reasons`/`authors_missing` are additive | no external reader outside `derive`/`config`/`reviews`/`records` |

## 5 · Risks

- `Derivation.unentitled_reasons` / `authors_missing` are produced but not yet consumed — RS1b's
  `release.py` (`authors_declared`) is the consumer; a baseline `Derivation` reconstruction in
  `baseline.py:252` does not copy them (harmless: baselines never read those fields).
- Seeding `authors_declared` ENABLED is deferred to RS1b (R18): adding the rule id to
  `_DEFAULT_RELEASE_RULES` now makes `release.evaluate` return `unknown release rule 'authors_declared'`.
- The new duplicate-person-id / duplicate-`email_sha256` refusals can reject a config that loads today
  (accepted — no external users; stated in LLR-RS.5.1).

## 6 · Pending items / spec deviations

- `authors_declared` ENABLED seed (config `_DEFAULT_RELEASE_RULES`) + the `release.py` rule → RS1b.
- The `entitled_to_sign`/`sign_review` truth table + `moved_*`/`already_signed`/`review_limit`/
  `unapproved_config` reason codes → RS1b (`signing.py` + the remaining `records.py` reason literals).

## 7 · Suggested next task

RS1b — `mapper/reqharness/signing.py` (new) + `mapper/reqharness/release.py` (`authors_declared`),
with `tests/test_reqharness_signing.py` and `test_authors_declared_release_rule_fails_when_batch_has_no_authors`.

---

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | ≤4 source files | ✓ | 4 source files (§2) |
| 2 | Tests written in this same increment | ✓ | 8 new nodes in `test_reqharness_registry.py` |
| 3 | Layer 0 written | ✓ | config validation + derive unit nodes |
| 4 | RED counterfactual | ✓ | 4 mutants, transcript `evidence/rs1a-red.transcript` |
| 5 | Reverse census | ✓ | B1/B4/A3 probes above, no external consumers |
| 6 | code-reviewer passed | ⚠ | **Independent review PENDING** (this unit) |
| 7 | No file from another lane touched | ✓ | one lane |
| 8 | Frozen interfaces untouched | ✓ | `reviews.record_review`/`load_reviews`/`chain.*`/`release.evaluate` unchanged |
| 9 | Coverage verified on disk | ✓ | 115 passed gate run |
| 10 | Load-bearing emptiness | ✓ | premise 7 (no pre-existing `SigningRefused`/`owning_batch`) verified by B1 grep |
| 11 | Mutation verdicts | ✓ | 4 mutants KILLED (RED), arms named |
| 12 | Instrument RED-proof | ✓ | the pytest nodes shown failing before passing |
| 13 | Correction population | — none (no correction) |
| 14 | Emitted-form assertion | — none (no emitted artifact beyond the transcript) |
| 15 | Independent review names somebody | ⚠ | PENDING |
| 16 | Evidence files | ✓ | `evidence/rs1a-red.transcript` sha256 `525fac9a…1895cf` |

---

## Security re-verification follow-up (RS1a gate — `security-reviewer` REQUEST-CHANGES on F1)

The independent security review returned REQUEST-CHANGES: **F1 still OPEN** — a human review whose
record has no `owning_batch` skipped the mismatch check, so an author who hand-writes an old-format
record and then blanks or moves the object's `Owning batch` cell still derived `reviewed`. Four fixes
landed in RS1a (same 3 source files, within the original 4-file budget) plus one stated residual:

| # | Fix | Files | Test node |
|---|---|---|---|
| H1 (HIGH) | With `authors` declared, a human review lacking `owning_batch` (absent or `""`) derives `unentitled` with new reason `owning_batch_missing`; when `authors` is empty/absent, behaviour is unchanged | `derive.py` `_unentitled_reasons`, `records.py` (`REASON_OWNING_BATCH_MISSING`) | `test_derive_marks_a_legacy_review_without_owning_batch_unentitled_when_authors_declared` · `test_derive_a_legacy_review_without_owning_batch_stays_reviewed_without_authors` |
| M2 (MED) | The canon `Owning batch` cell is NFC-normalised in `parse_canon`, so a decomposed batch id cannot evade the author rule | `derive.py` `parse_canon` | `test_derive_nfc_normalises_the_owning_batch_cell` |
| L1 (LOW) | Duplicate person ids inside one batch's `authors` list are refused by name | `config.py` `validate_config` | `test_config_refuses_a_duplicate_person_id_in_one_authors_list` |
| L2 (LOW) | The authors-less `config_hash` is pinned to the pre-RS1a digest as a constant | `tests/test_reqharness_registry.py` | `test_an_authors_less_config_hashes_byte_identically_to_today` (re-pinned) |
| M1 (MED, no code) | Stated residual: an author who can edit the canon can move an object's `Owning batch` cell to a batch they are not listed for before signing (per-batch authorship is the operator's chosen granularity; full closure needs per-object authorship) | `design/design-proposal.md` §10 · `design/PDR-…md` §E · `.dev-flow/BACKLOG.md` B-135 | — |

**RED proof** (revert → RED → sha256-identical restore → GREEN) appended to
`evidence/rs1a-red.transcript` §5–§8. Restore digests: `derive.py` `cb12f9e4…5316`, `config.py`
`ce397107…185c` (both byte-identical after each restore). `tests/test_reqharness_registry.py` →
`24 passed`. Gate checklist items 6 and 15 are discharged by this review (`security-reviewer`).

| File | Kind |
|---|---|
| `mapper/reqharness/derive.py` | source |
| `mapper/reqharness/config.py` | source |
| `mapper/reqharness/records.py` | source |
| `tests/test_reqharness_registry.py` | test |
| `design/PDR-2026-10-15-review-screen-batch.md` · `design/design-proposal.md` · `01-requirements-ledger.md` · `PLAN.md` · `evidence/rs1a-red.transcript` · `.dev-flow/BACKLOG.md` | doc |

## Security re-verification, second pass (Claude Opus, security-reviewer)

Verdict APPROVE-WITH-NITS, **F1 CLOSED** — 10/10 adversarial probes fail closed (legacy record with blanked / moved / NFD / undeclared cell; forged `owning_batch` = another batch or ""; whitespace/case variants; registries without `authors` unchanged); the pinned pre-change digest `fa46d573…074b` recomputed from the pre-RS1a tree and equal. L-a (cell moved before signing) = the stated M1 residual (PDR §E, design §10, B-135). L-b fixed by the orchestrator: `reviews.py` NFC-normalises the stored `owning_batch` on read; node `test_a_stored_owning_batch_is_nfc_normalised_on_read` (a HAND-WRITTEN NFD record — the writer already stores NFC) is RED with the normalisation removed and GREEN restored (sha256 equal); `tests/test_reqharness_registry.py` 25 passed. The reviewer reported one accidental scratch file written into `tests/` and deleted at once; `git status` confirmed clean before this follow-up.

### Evidence files

| Evidence artifact | Path | SHA-256 |
|---|---|---|
| RED battery (RS1a, 4 mutants; current bytes, the cited `525fac9a…` was the pre-follow-up capture; re-pinned `2026-10-16` after the Q3 digest-verification append) | `.dev-flow/2026-10-15-review-screen-batch/evidence/rs1a-red.transcript` | `94dbc09195ab2979b39f3d40153ac539a4d44c5a4bd25b5d6b0ede46cca73fe1` |

| Field | Value |
|---|---|
| **Evidence files** | `evidence/rs1a-red.transcript` |
| **Independent review** | code-reviewer — PENDING record (RS1a and RS1b are merged and reviewed per PLAN; the RS1b verdict is recorded in increment-002) |
