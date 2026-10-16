# Increment 002 — RS1b · the logic (signing + the `authors_declared` release rule)

> **Artifact language.** English.

| Field | Value |
|---|---|
| Batch | `2026-10-15-review-screen-batch` |
| Increment | `002` |
| Lane (if the batch forked) | none — one lane |
| Requirement(s) | HLR-RS.2 · HLR-RS.3 · HLR-RS.5 · LLR-RS.2.1 · LLR-RS.2.2 · LLR-RS.2.4 · LLR-RS.5.1 · LLR-RS.5.2 |
| Acceptance | white-box `TC-RS-2.1.1` `TC-RS-2.1.2` `TC-RS-2.2.1` `TC-RS-2.2.2` `TC-RS-2.4.1` `TC-RS-2.4.2` |
| Agent | `software-dev` (deepseek-v4-pro) |
| Date | `2026-10-15` |

---

## 1 · What changed

RS1b — the ReqHarness **logic layer** over the RS1a data surfaces: the headless
signing orchestration (`mapper/reqharness/signing.py`) and the `authors_declared`
release rule (`mapper/reqharness/release.py`).

- `entitled_to_sign(repo, object_id, identity_email) -> (bool, reason)` — the one
  pre-flight predicate (the 10-arm truth table): chain verified (tampered/forked/
  no-registry), the git identity email resolves to EXACTLY ONE declared person
  (unknown-viewer/ambiguous-viewer), object exists (unknown-object), ACTIVE
  (retired), class declared (class-undeclared), holds the class's `reviewer_role`
  at the current head (no-role), and NOT an author of the object's owning batch
  (author) — plus the two `(True, "")` cases (entitled; blank `Owning batch`).
- `sign_review(repo, object_id, identity_email, *, confirm_digest, confirm_head,
  confirm_owning_batch=None, now=None) -> Path` — one snapshot threaded through
  entitlement → confirm → write; refuses `unapproved_config` when
  `config_digest(config) != report.policy_config_hash` (F6, before the generic
  chain refusal so a config mismatch is not folded into `tampered`); the
  `moved_object`/`moved_digest`/`moved_head`/`moved_role` TOCTOU re-checks with the
  fixed precedence (object gone → `unknown_object`; revoke losing the role →
  `moved_role` else `moved_head`); loader `ValidationError`s → `SigningRefused`
  (never a bare exception, A4); `now=None` → UTC; `already_signed` on the
  content-named collision; `review_limit` at the file-count cap; writes
  `class_id` from the canon object, `verdict="reviewed"`, `kind="human"`,
  `note=""`, `owning_batch` stored (F1).  Headless — no Textual/Rich/identity
  imports; it RECEIVES the identity email.
- `release.py` gains `RULE_AUTHORS_DECLARED` and the rule evaluation: fails when
  `derivation.authors_missing` is non-empty (an active object whose owning batch
  is blank or absent from `authors`).  `config.py`'s `_DEFAULT_RELEASE_RULES`
  seeds `authors_declared` ENABLED (the one-line RS1a-deferred seed, R18).

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/reqharness/signing.py` | source | HLR-RS.2/3/5 · LLR-RS.2.1/2.2/2.4 | `entitled_to_sign` (10-arm truth table) + `sign_review` (orchestration, TOCTOU, `unapproved_config`, `already_signed`, `review_limit`) + the signing reason-code literals |
| `mapper/reqharness/release.py` | source | HLR-RS.5 · LLR-RS.5.1 | `RULE_AUTHORS_DECLARED` + the `known` entry (`not derivation.authors_missing`) + `__all__` |
| `mapper/reqharness/config.py` | source | HLR-RS.5 · LLR-RS.5.1 (F2) | the one-line seed: `_DEFAULT_RELEASE_RULES` gains `"authors_declared"` |
| `tests/test_reqharness_signing.py` | test | LLR-RS.2.1/2.2/2.4 | 13 nodes (see §4) |
| `tests/test_reqharness_registry.py` | test | LLR-RS.5.1/5.2 | `test_authors_declared_release_rule_fails_when_batch_has_no_authors` + the ENABLED half of `test_create_registry_seeds_authors_and_authors_declared` |
| `tests/test_reqharness_release.py` | test | HLR-RS.5 · LLR-RS.5.1 (re-baselining) | a local `_seed` that uses the parent batch's release rules (see Risks) |
| `.dev-flow/2026-10-15-review-screen-batch/evidence/rs1b-red.transcript` | generated | HLR-RS.2 · HLR-RS.3 · LLR-RS.2.1 | the 9-mutant RED battery |

| Count | Value |
|---|---|
| **SOURCE files** | **2** (+1 one-line `config.py` seed, itemised) |
| Test files | 3 (uncapped) |
| Doc files | 2 (this packet + the transcript) |

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
| 0 · unit | core · full | `test_entitled_to_sign_requires_the_designated_role_at_the_current_head` · `test_entitled_to_sign_truth_table_includes_retired_and_class_undeclared` · `test_entitled_to_sign_refuses_an_author_of_the_object_batch` · `test_entitled_to_sign_truth_table_chain_arms` · `test_entitled_to_sign_truth_table_identity_and_object_arms` · `test_sign_review_writes_a_record_that_derive_reads_as_reviewed` · `test_sign_review_refuses_on_tampered_or_forked_or_no_registry` · `test_sign_review_freezes_the_clock_via_now` · `test_sign_review_refuses_an_unapproved_config` · `test_sign_review_refuses_when_the_object_digest_head_or_role_moved` · `test_sign_review_refuses_already_signed_identical_content` · `test_sign_review_refuses_at_the_review_file_count_limit` · `test_sign_review_has_no_cli_or_entry_point_exposure` | 13 passed |
| A · white-box | core · full | `test_authors_declared_release_rule_fails_when_batch_has_no_authors` · `test_create_registry_seeds_authors_and_authors_declared` | 2 passed |

GREEN line (full gate run): `129 passed, 1 warning in 92.52s` · `ruff check mapper/reqharness` → `All checks passed!`

### RED counterfactual — executed, not predicted

Every mutant: mutate → node RED → restore (sha256 equal) → GREEN. Full transcript at
`evidence/rs1b-red.transcript`.

| Mutation | RED node | Result |
|---|---|---|
| M-RS5 — delete the TOCTOU re-check block | `test_sign_review_refuses_when_the_object_digest_head_or_role_moved` | RED → sha256 equal → GREEN |
| M-RS6 — drop the role check in `entitled_to_sign` | `test_entitled_to_sign_requires_the_designated_role_at_the_current_head` | RED → sha256 equal → GREEN |
| M-RS7 — drop the active/retired check | `test_entitled_to_sign_truth_table_includes_retired_and_class_undeclared` | RED → sha256 equal → GREEN |
| M-RS8 — drop the chain check | `test_entitled_to_sign_truth_table_chain_arms` | RED → sha256 equal → GREEN |
| M-RS14 — coerce an unknown object id | `test_entitled_to_sign_truth_table_identity_and_object_arms` | RED → sha256 equal → GREEN |
| M-RS19 — drop the author check | `test_entitled_to_sign_refuses_an_author_of_the_object_batch` | RED → sha256 equal → GREEN |
| M-RS22 — raise a bare `ValidationError` instead of `SigningRefused` | `test_sign_review_refuses_already_signed_identical_content` | RED → sha256 equal → GREEN |
| M-RS29 — drop the `unapproved_config` check | `test_sign_review_refuses_an_unapproved_config` | RED → sha256 equal → GREEN |
| M-RS23 — plant a `--sign` token in `app.py` | `test_sign_review_has_no_cli_or_entry_point_exposure` | RED → sha256 equal → GREEN |

## 5 · Risks

- **The `authors_declared` seed re-baselines the parent batch's release tests.**
  Seeding `authors_declared` into `_DEFAULT_RELEASE_RULES` (F2) makes `release.evaluate`
  return `not ready · authors_declared` for any fresh registry with active objects and
  empty `authors` — so `tests/test_reqharness_release.py`'s five "all green / exit-0"
  arms broke.  The PLAN (R18) recorded only the transient `unknown release rule` state,
  not this permanent "fails open" consequence.  Resolution (itemised): the parent
  release test file gained a local `_seed` that seeds the parent batch's release rules
  (`all_active_reviewed`, `chain_verified`, `signers_in_force`) — HLR-RH.7's fixtures
  predate `authors_declared` and should not exercise a rule from THIS batch.  Flagged
  for the orchestrator.
- **`confirm_owning_batch` is an additive optional parameter** on `sign_review`
  (default `None`, skipped when absent).  The documented signature lists
  `confirm_digest`/`confirm_head`/`now`; the object's owning batch is NOT encoded in
  the normative digest, so the `moved_object` TOCTOU arm is otherwise unreachable.
  The RS2 screen passes it from its sign-intent snapshot; the unit test passes it
  directly.  Spec clarification recorded.
- `no_role` / `author` reason codes are shared with `derive`'s `unentitled` causes
  (imported from `records.py`); the signing-specific codes live in `signing.py`
  (touching `records.py` is outside this unit's two-source-file boundary).
- `unapproved_config` (F6) is checked BEFORE the generic chain refusal, so a config
  digest mismatch is `unapproved_config` while a pure chain-link tamper stays `tampered`.

## 6 · Pending items / spec deviations

- `test_reqharness_release.py` re-baselining (the local `_seed`) is a touched file
  beyond the named set, itemised above.
- The `moved_object` / `confirm_owning_batch` optional parameter (spec clarification).
- RS2 (screen + seat) is the only module allowed to import `signing` (pinned by
  `test_sign_review_has_no_cli_or_entry_point_exposure`).

## 7 · Suggested next task

RS2 — `mapper/screens/review.py` (new) + `mapper/keymap.py` (the `review` scope) +
`mapper/screens/home.py` (the `v` door) + `mapper/app.py` (re-export), with
`tests/test_review_screen.py` and the itemised census pin re-baselines.

---

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | ≤4 source files | ✓ | 2 source files + 1 one-line `config.py` seed (§2) |
| 2 | Tests written in this same increment | ✓ | 13 new nodes in `test_reqharness_signing.py` + 2 in `test_reqharness_registry.py` |
| 3 | Layer 0 written | ✓ | `entitled_to_sign` truth table + `sign_review` orchestration unit nodes |
| 4 | RED counterfactual | ✓ | 9 mutants, transcript `evidence/rs1b-red.transcript` |
| 5 | Reverse census | ✓ | no external consumer of `signing` (pinned by AST); `authors_missing` consumed by `release` |
| 6 | code-reviewer passed | ⚠ | **Independent review PENDING** (this unit) |
| 7 | No file from another lane touched | ✓ | one lane |
| 8 | Frozen interfaces untouched | ✓ | `reviews.record_review`/`next_seq`/`load_reviews`/`chain.*` unchanged |
| 9 | Coverage verified on disk | ✓ | 129 passed gate run |
| 10 | Load-bearing emptiness | ✓ | only `screens/review.py` may import `signing` (AST: currently none) |
| 11 | Mutation verdicts | ✓ | 9 mutants KILLED (RED), each restored sha256-equal |
| 12 | Instrument RED-proof | ✓ | pytest nodes shown failing before passing |
| 13 | Correction population | — none (no correction) |
| 14 | Emitted-form assertion | — none (no emitted artifact beyond the transcript) |
| 15 | Independent review names somebody | ⚠ | PENDING |
| 16 | Evidence files | ✓ | `evidence/rs1b-red.transcript` (9/9 sha256-equal restores) |

---

## Code-review follow-up (RS1b, REQUEST-CHANGES — BLOCK-UNTIL F1/F2)

Reviewer returned REQUEST-CHANGES with six findings; each fixed, RED-proven (revert → RED → sha256-identical restore → GREEN) and appended to `evidence/rs1b-red.transcript`.

| Finding | Severity | Fix | RED node | Product files |
|---|---|---|---|---|
| F1 | HIGH | Pure `_entitlement(report, config, canon, viewer, object_id) -> (bool, code)`; `sign_review` uses its OWN snapshot — `safe_verify`/`load_config`/`load_canon` each run EXACTLY once (no second load); retired/class-undeclared order canonical | `test_sign_review_loads_config_chain_and_canon_exactly_once` (mutant: re-introduce `entitled_to_sign`) | `signing.py` |
| F2 | HIGH | Census scans `mapper/` + `tests/`, catches absolute + package-qualified + relative forms; allowlist `screens/review.py` + this test file | `test_signing_import_forms_are_all_detected` (mutant: drop the package-qualified branch) | `test_reqharness_signing.py` |
| F3 | MED | `confirm_owning_batch` is a REQUIRED keyword (no default) — orchestrator-accepted spec clarification (R20, Ledger `.23`); LLR-RS.2.1 signature amended | `test_sign_review_confirm_owning_batch_is_a_required_keyword` (mutant: restore `= None`) | `signing.py` |
| F4 | MED | Re-checks in the documented order `moved_object` → `moved_digest` → `moved_head` → `moved_role`; object+digest both moved → `moved_object` | `test_sign_review_refuses_when_the_object_digest_head_or_role_moved` (mutant: digest first) | `signing.py` |
| F5 | MED | Two entitled signers, different content, same object → two files, both load, duplicate `seq` tolerated | `test_two_signers_different_content_both_write_and_duplicate_seq_is_tolerated` (mutant: `record_review` rejects duplicate seq) | — (verification node) |
| F6 | LOW | Typed `ReviewLimitError` / `AlreadySignedError` in `records.py`, raised by `reviews.py`, mapped by TYPE in `signing.py` | `test_sign_review_maps_typed_review_errors_not_message_text` (mutant: message-text classification) | `records.py`, `reviews.py`, `signing.py` |

- **New test nodes** (5): `test_sign_review_loads_config_chain_and_canon_exactly_once`, `test_signing_import_forms_are_all_detected`, `test_sign_review_confirm_owning_batch_is_a_required_keyword`, `test_two_signers_different_content_both_write_and_duplicate_seq_is_tolerated`, `test_sign_review_maps_typed_review_errors_not_message_text` (plus the reordered `moved_object` precedence arm inside the existing moved test). `tests/test_reqharness_signing.py` → 18 nodes.
- **Transcript** (appended "Code-review follow-up" section): `sha256 20b8ae9b276965e34e5fdee64c9f8a258ca14efd21f96aee45d971d24c0298a7`.
- **Gate run**: `139 passed` (one pre-existing, load-sensitive failure — `test_nesting_event_stream_refuses_lexically_bypassed_shapes` — passes alone; see §4 note). `ruff check mapper/reqharness tests/test_reqharness_signing.py` → `All checks passed!`.
- **Pending**: the code-reviewer's re-review (independent review still open at the increment gate).

### RS1b re-review (RS1B-FIX2) — F2 re-opened, then closed

The re-review found the F2 census still incomplete.  `_imports_signing` counted a
relative import only when the importing file sat directly in `mapper/reqharness/`,
so a level-1 relative import elsewhere (`from .reqharness import signing` in
`mapper/app.py`) and a level-2 relative import (`from ..reqharness.signing import
sign_review` in `mapper/screens/x.py`) escaped, and dynamic imports
(`importlib.import_module("…reqharness.signing")`, `__import__(…)`) were not caught.
Fix: `_imports_signing` now resolves EVERY relative `ImportFrom` to its absolute
dotted name from the importing file's package (`_resolve_relative`: climb
`level - 1` packages, then append `module`) and fails on any string literal
containing `reqharness.signing`.  `test_signing_import_forms_are_all_detected` gains
the two relative forms (each planted with the right pseudo-path) and one
`import_module` / one `__import__` arm.  RED-proven (revert → RED → sha256-identical
restore → GREEN), appended to `evidence/rs1b-red.transcript`.

## Independent review — final (Claude Opus, code-reviewer)

APPROVE-WITH-NITS at b907571; F1 (one snapshot) CLOSED at eccc13c, F2 (exposure test) CLOSED at b907571, F3–F6 verified. Remaining LOW nits ACCEPTED by the orchestrator as residuals of a test that guards against ACCIDENTAL exposure (deliberate evasion is a code-review matter): attribute access `import mapper.reqharness as rh; rh.signing`, `getattr(rh, "signing")`, `importlib.import_module(".signing", "mapper.reqharness")`, and `from mapper.reqharness import *` (inert today: the package `__init__` has no `__all__` naming `signing`).

### Evidence files

| Evidence artifact | Path | SHA-256 |
|---|---|---|
| RED battery (RS1b incl. the review follow-ups) | `.dev-flow/2026-10-15-review-screen-batch/evidence/rs1b-red.transcript` | `16e5199d9b2146cdd24756e599fc60ee36a03cc6225465d7a74771646a24eb58` |

| Field | Value |
|---|---|
| **Evidence files** | `evidence/rs1b-red.transcript` |
| **Independent review** | code-reviewer — APPROVE-WITH-NITS (Claude Opus); see "Independent review — final" above |
