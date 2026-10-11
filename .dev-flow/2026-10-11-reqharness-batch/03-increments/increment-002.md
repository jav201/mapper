# Increment 002 — HLR-RH.2 · HLR-RH.3 · `ReqHarness role chain: append, policy binding, verify, forks`

| Field | Value |
|---|---|
| Batch | `2026-10-11-reqharness-batch` |
| Increment | `002` |
| Lane (if the batch forked) | none — one lane; trunk units RHI2 + RHI2B (RHI2B finished and proved the increment after RHI2 timed out mid-fix) |
| Requirement(s) | HLR-RH.2 / LLR-RH.2.1 · 2.2 · 2.3 · 2.4 · 2.5 — HLR-RH.3 / LLR-RH.3.1 · 3.2 · 3.3 · 3.4 · 3.5 (incl. the R27 arms) |
| Acceptance | layer-0 unit nodes only (`01-requirements.md` §3 HLR-RH.2/HLR-RH.3; the R27(e) arms) |
| Agent | `software-dev` (Kimi, kimi-code) |
| Date | `2026-10-11` |

---

## 1 · What changed

BLUF: mapper now has the hash-chained role log — `mapper/reqharness/chain.py` —
with the one write path over `reqharness/roles.yml` (a YAML multi-document
stream, one chain event per document), the BY-`prev_hash` verification walk
from genesis, effective roles at a bound head, tamper/fork detection with the
exact status words, and the admin-approved `resolve` fork recovery. The typed
event schema treats the three optional keys (`config_hash`, `request_hash`,
`resolve_excludes`) as optional, rejected when unknown, and allowed only per
event kind.

Mechanism, per LLR:

- **LLR-RH.2.1** — `propose`: an admin's change about SOMEONE ELSE applies in
  ONE event (`requested_by == approved_by == that admin`) bound to the current
  head (R2); every append records (`roles_seq`, `roles_hash`) of the head it
  was made against and extends the chain by
  `sha256(prev_hash + "\n" + canonical_json(event_without_this_hash))`.
- **LLR-RH.2.2** — a change about the requester themselves, or by a non-admin,
  writes ONE content-keyed pending file under `reqharness/pending/` (exclusively
  created, roles.yml untouched); `approve_pending` applies it under a DIFFERENT
  admin's approval — the sole-admin self-change stays pending until a second
  admin exists (O5/R6). Nobody approves a change to themselves.
- **LLR-RH.2.3** — `effective_roles` folds the verified prefix with `<=` ON
  `roles_seq` at a bound head, never at wall-clock time; a bound head absent
  from the verified chain raises (`not verifiable`).
- **LLR-RH.2.4** — genesis (R15) and admin-approved `policy` events bind
  sha256(canonical config); a live-config mismatch yields exactly
  `config changed without approval` with the last approved policy in force and
  appends frozen, until an admin re-binds with `append_policy`.
- **LLR-RH.2.5** — an event bound to a head that does not exist in the chain
  fails verify at its walk position; `time` must be non-decreasing even under
  a consistent rewrite.
- **LLR-RH.3.1/3.2 (R27)** — the walk is BY `prev_hash` FROM genesis, NOT by
  file position: a document claiming an already-claimed parent is a fork
  sibling; two documents on one parent exclude BOTH children from authority
  deterministically regardless of document order, reported `chain forked at
  seq N`; a fork whose excluded branch has descendants is `chain broken`
  (single-event forks only this batch — B-126).
- **LLR-RH.3.4 (R27)** — the only legal continuation after a fork is an
  admin-approved `resolve` whose `prev_hash` is the CHOSEN child and whose
  `resolve_excludes` names the excluded sibling; a resolve naming a non-sibling,
  or whose chosen child fails the approval rule at its own bound head, yields
  `chain broken`; after a valid resolve the chain verifies again (R16 —
  recovery stays a documented manual procedure, `append_resolve` implements
  it; fork-recovery UI deferred B-126).
- **LLR-RH.3.3** — the status words asserted byte-for-byte (AT-079):
  `chain verified` / `config changed without approval` / `chain forked at
  seq N` / `chain broken`.
- **LLR-RH.3.5 (R9/R26)** — every parsed file is confined
  (`mapper.osopen.confine_reason`: `..`, links and junctions refused), size-
  limited (≤ 64 KB event files, ≤ 4 MB roles.yml — named limits from
  `config.py`), and refused BY NAME on malformed/oversize input; reading is
  `read_event_file`, the reviews increment's shared reader.
- **Residuals stated, not hidden (R23)** — tail truncation of a head no
  review/pending/baseline has bound yet verifies clean (head binding covers
  only bound heads); a writer with repo access can rewrite chain, reviews and
  recorded heads together and defeat every mechanism this module ships
  (layer 3 — B-122 strong mode is the named follow-up).

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/reqharness/chain.py` | source | HLR-RH.2 / HLR-RH.3 | new module: the chain reader/writer/verifier — schema, walk, roles fold, append paths (`propose`, `approve_pending`, `append_policy`, `append_resolve`), statuses, confinement and limits |
| `mapper/reqharness/records.py` *(named `model.py` when this increment landed; renamed at the batch gate fix — increment-009 — so historical `model.py:<line>` citations in older artifacts stay unambiguous)* | source | HLR-RH.2 | one small edit: the `ChainEvent` frozen value object (optional `config_hash` / `request_hash` / `resolve_excludes` fields) |
| `tests/test_reqharness_chain.py` | test | LLR-RH.2.1–2.5 · LLR-RH.3.1–3.5 | the fourteen named layer-0 nodes, incl. the R27(e) arms |

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 4** |
| Test files | 1 (uncapped) |
| Doc files | 0 |

- At 2 source files: the chain is one mechanism and lives in one module; the
  only RH1 touch is the `ChainEvent` value object the typed schema returns.

---

## 3 · How to test

```bash
python -m pytest -p no:cacheprovider tests/test_reqharness_chain.py tests/test_reqharness_config.py tests/test_no_operator_paths.py
ruff check mapper/reqharness/ tests/test_reqharness_chain.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `test_admin_applies_to_someone_else_in_one_event`, `test_self_change_and_non_admin_stay_pending`, `test_effective_roles_at_time_t`, `test_policy_event_binds_config`, `test_head_binding_unknown_head_not_verifiable`, `test_hand_edit_breaks_chain_and_keeps_last_verified`, `test_merge_fork_is_detected`, `test_fork_resolve_event_recovers`, `test_fork_recovery_reappend_on_head`, `test_verify_walks_by_prev_hash_in_order_fork_resolve`, `test_resolve_naming_non_sibling_is_invalid`, `test_multi_event_excluded_branch_is_broken`, `test_resolve_chosen_child_must_pass_approval_rule`, `test_input_limits_reported_by_name` | 14 passed |
| **A · white-box** | | none owed (no dedicated AT for HLR-RH.2/3) | — |
| **B · black-box** | | none owed (screen ATs are RH6a/6b) | — |

Guards: `tests/test_reqharness_config.py` + `tests/test_no_operator_paths.py`
6 passed with the chain file (20 passed across the three named files);
ruff clean on `mapper/reqharness/` and `tests/test_reqharness_chain.py`.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | nine arms, one per named negative control: M-CH1 (one-event admin apply routed to the pending store), M-CH2 (self-approval of a pending request allowed), M-CH3 (per-document hash recompute skipped), M-CH4 (fork deduped by seq), M-CH5 (the `<=`→`<` flip on the `roles_seq` boundary), M-P1 (policy check skipped), M-HB1 (unknown bound heads accepted), M-FR1 (non-sibling resolve exclusion accepted), M-FR2 (a fork child kept in authority) |
| Instrument | project code, own hand via `.dev-flow/2026-10-11-reqharness-batch/evidence/rh2-red-driver.sh`; restore checked by sha256 |
| Where it ran | **my own worktree** |
| Transcript | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh2-red.transcript` |
| Restore proven by | **file hash returned to its pre-mutation value** (sha256 before == after, per arm, printed in the transcript) |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` on every run |
| Arms resolved at baseline | **9** |
| Verdict granularity | per resolved node id / instrument, printed per arm |
| Arms that stayed GREEN | none — every arm RED |

| Field | Value |
|---|---|
| **RED counterfactual** | M-CH1 → `test_admin_applies_to_someone_else_in_one_event` FAILED, restore sha256 `48ae4fe0…52e8a` byte-identical → PASSED; M-CH2 → `test_self_change_and_non_admin_stay_pending` FAILED, same restore digest → PASSED; M-CH3 → `test_hand_edit_breaks_chain_and_keeps_last_verified` FAILED, restore byte-identical → PASSED; M-CH4 → `test_merge_fork_is_detected` FAILED, restore byte-identical → PASSED; M-CH5 → `test_effective_roles_at_time_t` FAILED, restore byte-identical → PASSED; M-P1 → `test_policy_event_binds_config` FAILED, restore byte-identical → PASSED; M-HB1 → `test_head_binding_unknown_head_not_verifiable` FAILED, restore byte-identical → PASSED; M-FR1 → `test_resolve_naming_non_sibling_is_invalid` FAILED, restore byte-identical → PASSED; M-FR2 → `test_merge_fork_is_detected` FAILED, restore byte-identical → PASSED; transcript at `.dev-flow/2026-10-11-reqharness-batch/evidence/rh2-red.transcript` |

| Field | Value |
|---|---|
| **Mutation verdicts** | M-CH1 KILLED at `test_admin_applies_to_someone_else_in_one_event` · M-CH2 KILLED at `test_self_change_and_non_admin_stay_pending` · M-CH3 KILLED at `test_hand_edit_breaks_chain_and_keeps_last_verified` · M-CH4 KILLED at `test_merge_fork_is_detected` · M-CH5 KILLED at `test_effective_roles_at_time_t` · M-P1 KILLED at `test_policy_event_binds_config` · M-HB1 KILLED at `test_head_binding_unknown_head_not_verifiable` · M-FR1 KILLED at `test_resolve_naming_non_sibling_is_invalid` · M-FR2 KILLED at `test_merge_fork_is_detected` — transcript `evidence/rh2-red.transcript`; restore digests above |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| pytest node `test_admin_applies_to_someone_else_in_one_event` | pending-store routing (M-CH1) | `1 failed` — see transcript |
| pytest node `test_self_change_and_non_admin_stay_pending` | self-approval allowed (M-CH2) | `1 failed` |
| pytest node `test_hand_edit_breaks_chain_and_keeps_last_verified` | hash recompute skipped (M-CH3) | `1 failed` |
| pytest node `test_merge_fork_is_detected` | fork deduped (M-CH4); child kept in authority (M-FR2) | `1 failed` (both arms) |
| pytest node `test_effective_roles_at_time_t` | `<=`→`<` on `roles_seq` (M-CH5) | `1 failed` |
| pytest node `test_policy_event_binds_config` | policy check skipped (M-P1) | `1 failed` |
| pytest node `test_head_binding_unknown_head_not_verifiable` | unknown bound heads accepted (M-HB1) | `1 failed` |
| pytest node `test_resolve_naming_non_sibling_is_invalid` | non-sibling exclusion accepted (M-FR1) | `1 failed` |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 8 instruments, each shown RED before its PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| `reqharness/roles.yml` grant event | the appended document's `roles_hash`/`prev_hash` == the previous verified head's `this_hash`, and ONE new document only | equal; 3 documents total (genesis, policy, grant) |
| `reqharness/roles.yml` after a hand edit | recomputed link vs the spliced document's `this_hash` | mismatch → `config changed without approval` at document 3; `effective_roles` == the last verified prefix only |
| `reqharness/pending/<name>.yml` | name matches `\d{8}-[0-9a-f]{8}\.yml`; roles.yml bytes unchanged | 2 pending files, exactly 1 per request; roles.yml byte-identical |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 3 artifacts, each asserted against the bytes on disk |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED-proof transcript (relative paths; worktree redacted per A-110) | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh2-red.transcript` | `9996b326d0caf13f112b16c92495effc1f00201495b372a2d18cf3278803b3d3` |
| RED-proof driver script | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh2-red-driver.sh` | `bb6f2c253db529b5e7d910b97e6a6bda1ec7619e8b1902044cdc8ede17a59842` |

| Field | Value |
|---|---|
| **Evidence files** | 2 artifacts, each at the declared home, cited with the digest of its stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — "single-event forks only": the walk treats an excluded branch with descendants as `chain broken` and defers multi-event branch recovery (B-126) |
| If the result is an ABSENCE, what made the search wide enough | the multi-event arm constructs the positive instance: parent → {childA, childB}, childB → grandchild, and asserts `chain broken` at the descendant's document (`test_multi_event_excluded_branch_is_broken`) |
| Guard labelled as protecting a CONCLUSION, not a behaviour | none beyond the batch's standing census tests (run as guards, not claimed here) |
| Conjunctive criteria: one mutation per conjunct | 9 controls, 9 single-conjunct mutations, per-arm verdicts above |
| Synthetic instance of the absent case | the grandchild fixture above IS the synthetic multi-event excluded branch |
| **Positive control for every probe that returned an ABSENCE** | the multi-event fixture is the positive control for the "no multi-event recovery" absence |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rl "reqharness" tests/` | `tests/test_reqharness_config.py` + `tests/test_reqharness_chain.py` (this increment's own) |
| B2 file moved on disk | `tests/test_no_operator_paths.py` (tracked-file census) | passed in the 20-run |
| B3 byte-identical golden captures this source | `grep -r "reqharness" tests/goldens/` | 0 hits |
| B4 artifact produced here is consumed elsewhere | `grep -rl "reqharness" mapper/ --include=*.py` | only `mapper/reqharness/` itself (consumers land RH3+) |

| A3 | interface consumed by another module changed | `grep -rn "from mapper" mapper/reqharness/` | `mapper.reqharness.*` only + the `mapper.osopen` edge declared in ARCH §3 (now actually used by `chain.py`) |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1 · B2 · B3 · B4 · A3), each with its command and verdict in the table above |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population | Enumeration method | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| the RHI2 schema bug: optional keys treated as required | `mapper/reqharness/chain.py::_validate_event` | the 13 RED nodes all failed at `missing key(s): request_hash, resolve_excludes` | 1 | 1 | 0 |

| Field | Value |
|---|---|
| **Correction population** | 1 correction, enumerated from the failure signature before editing |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|---|---|---|---|
| none | 0 hits | — | — |

### Signed-balance test ledger

`post = base − deleted + added` → `2 = 0 − 0 + 2` (chain.py new + the model.py
`ChainEvent` addition) ✓ reconciles

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | reviewed by `code-reviewer` — verdict recorded in the batch's independent review rounds (`02-review.md`); findings discharged via the rulings named in this packet |

---

## 5 · Risks

- The fork walk evaluates candidate resolves in (`seq`, file-index) order and
  takes the first fully valid one; two simultaneously valid resolves on the
  same fork are not distinguished (the first in that order wins) — a manual
  cleanup question, not a verification hole: any invalid resolve present makes
  the state `chain broken`, so a mixed pair cannot silently pass.
- `append_resolve` re-walks the file through `_inspect` without the policy
  gate by design (a fork freezes authority at the pre-fork prefix; the policy
  comparison is meaningless mid-fork), but it also means a policy mismatch
  cannot block fork recovery — recovery is the one append allowed in a
  non-verified state besides `append_policy`'s re-bind.
- Sole-admin fork recovery requires the resolver to hold admin at the chosen
  child's bound head; a fork created by the only admin's self-approved branch
  cannot be resolved by that same admin (approval rule) — documented manual
  recovery still needs a second admin, same as sole-admin self-changes (O5).

## 6 · Pending items / spec deviations

- Multi-event excluded-branch recovery is deferred (B-126) by requirement; the
  state is `chain broken`, deterministic on every clone.
- Fork-recovery UI is deferred (B-126); recovery is the documented manual
  procedure of the `chain.py` module docstring, implemented and tested by
  `append_resolve` and `test_fork_recovery_reappend_on_head`.
- The `resolution` action (pending-request digest binding via `request_hash`)
  is in the schema and the approval rule, but no append path writes it yet —
  it lands with the reviews increment (R6 machinery).

## 7 · Suggested next task

RH3 — reviews (`mapper/reqharness/reviews.py`): the review file store, closing
reviews signed by a role in force at the bound head, the `resolution` action
consuming pending requests.

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | ≤4 source files | ✓ | 2/2, §2 |
| 2 | Tests written in this same increment | ✓ | `tests/test_reqharness_chain.py` |
| 3 | Layer 0 written where the criterion applies | ✓ | 14 nodes, §4 |
| 4 | RED counterfactual declared | ✓ | 9 arms, transcript + restore digests, §4 |
| 5 | Reverse census declared | ✓ | §4 table |
| 6 | `code-reviewer` passed | ⚠ | PENDING — §4b |
| 7 | No file from another lane touched | ✓ | one lane; `git status` shows only this increment's files |
| 8 | Frozen interfaces untouched | ✓ | no §4 row of ARCH changed; `tests/test_no_operator_paths.py` passed |
| 9 | Coverage claims verified on disk | ✓ | every claim cites a run in the transcript |
| 10 | Load-bearing emptiness declared | ✓ | single-event-fork limit + its positive control |
| 11 | Mutation verdicts declared | ✓ | per-arm KILLED, §4 |
| 12 | Instrument RED-proof declared | ✓ | 8 instruments |
| 13 | Correction population declared | ✓ | 1 (the RHI2 schema bug) |
| 14 | Emitted-form assertion declared | ✓ | 3 artifacts |
| 15 | Independent review names somebody | ⚠ | PENDING |
| 16 | Evidence files declared | ✓ | 2 rows with sha256 |


---

## Code-review follow-up (RHFIX23)

Code review of increments 002/003 (Claude Sonnet) returned REQUEST-CHANGES;
unit RHFIX23 applied the chain-side rulings F1–F3. Backups were taken only
after the fix was GREEN; every restore is verified byte-identical (sha256)
in the transcript.

| Finding | Severity | Fix | Node(s) | Negative control |
|---|---|---|---|---|
| **F1 forged admin** — `_passes_approval` returned True for `action == "genesis"` at ANY position and `_check_event` never pinned genesis to position 1: a seq-2 `genesis` by a non-admin (valid links, valid head binding) verified clean and minted an admin (reviewer reproduced: `effective_roles` → eve admin) | HIGH | the exact identity `(event.action == "genesis") == (position == 1)` in `_check_event` (a hand-edit class refusal, `config changed without approval`, at the offending document); the `_passes_approval` genesis shortcut moved under "no prefix" (`return not prefix`) | `test_genesis_only_at_position_one` (forged seq-2 genesis by eve → chain broken at document 2, no extra admin; mirror arm: a non-genesis action can never occupy position 1) | M-CH6 — pin removed + unconditional shortcut restored → the forged genesis verifies clean, eve becomes admin → RED |
| **F2 fold leak** — `effective_roles` folded on `event.roles_seq <= bound_seq`, so an event at seq k+1 (roles_seq k) leaked into head k | MED (ruling: filter on `seq`) | `_roles_in_force` folds on the event's OWN `seq <= bound_seq` (LED-2026-10-11-reqharness-batch.31 amends LLR-RH.2.3: statement, threshold, boundary catalog; back-pointer added) | `test_effective_roles_at_time_t` amended — head 2 now excludes the grant (seq 3, roles_seq 2); the ruling fixture (a grant at seq 2 is NOT in force at head 1) added; the boundary (bound seq == the grant's own seq) stays inclusive | M-CH5 — the `<=`→`<` flip on the event's own `seq` → RED |
| **F3 unbound policy** — `config_hash` was optional on `genesis` and `policy` events, so a policy could bind nothing | MED | `_validate_event` refuses a `genesis`/`policy` document without `config_hash` at the typed schema — named by file AND document (R9); the chain can never verify under a policy that binds nothing (the refusal is the schema class, the named `ValidationError`, not a chain status word) | `test_policy_event_requires_config_hash` (genesis arm: document 1; policy arm: document 2) | F3a — requirement removed → both fixtures pass silently → RED |

- Ledger: `LED-2026-10-11-reqharness-batch.31` (F2; the entry records F1/F3
  and the identity-side F4–F7 as shipped in the same unit).
- RED transcript: `.dev-flow/2026-10-11-reqharness-batch/evidence/rh23fix-red.transcript`
  — sha256 `8fe8f8b8152b2abd21c901adf34325665375295a418bf161ed8a05b6f5547647`.
- Verification after all restores: `python -B -m pytest -q -p no:cacheprovider
  tests/test_reqharness_chain.py tests/test_reqharness_identity.py
  tests/test_reqharness_config.py tests/test_no_operator_paths.py` — 35
  passed; `ruff check` clean.
