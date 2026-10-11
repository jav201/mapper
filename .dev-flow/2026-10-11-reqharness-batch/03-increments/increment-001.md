# Increment 001 — HLR-RH.1 · `ReqHarness config, schema and canonical form`

| Field | Value |
|---|---|
| Batch | `2026-10-11-reqharness-batch` |
| Increment | `001` |
| Lane (if the batch forked) | none — one lane, trunk unit RHI1 |
| Requirement(s) | HLR-RH.1 / LLR-RH.1.1 · LLR-RH.1.2 · LLR-RH.1.3 · LLR-RH.1.4 |
| Acceptance | layer-0 unit nodes only (no dedicated AT — `01-requirements.md` §3 HLR-RH.1) |
| Agent | `software-dev` (Kimi, kimi-code) |
| Date | `2026-10-11` |

---

## 1 · What changed

BLUF: mapper now has the headless ReqHarness domain core's first module —
`mapper/reqharness/` — with the typed config schema and refusing loader, the
canonical serialisation every later digest binds to, email hashing, and
`create_registry`, which writes a fresh `reqharness/config.yml` plus a
`reqharness/roles.yml` whose genesis document is policy-bound from the first
document (R15): `roles_hash: "GENESIS"` (no self-reference), `prev_hash:
GENESIS`, `config_hash` = sha256(canonical config at creation), and a
`this_hash` that verifies by the chain-link recomputation.

Mechanism, per LLR:

- **LLR-RH.1.1** — `ReqHarnessLoader`, a subclass on `yaml.CSafeLoader` when
  available, `yaml.SafeLoader` otherwise; duplicate keys refused at
  construction time; anchors/aliases refused by an event-stream scan (the C
  composer resolves aliases before Python-level overrides can see them, so the
  scan serves both loader bases identically). Never `yaml.load` with any other
  loader (R21). Every refusal names the file (R9).
- **LLR-RH.1.2** — `create_registry` writes the two files; genesis carries
  `approved_by: genesis`, `note: "declared at registry creation"`, `roles_seq: 1`.
- **LLR-RH.1.3** — typed schema: all fields `str` except `seq`/`roles_seq: int`,
  unknown/missing keys rejected, every field isinstance-checked, `time` exactly
  `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$` (R18); canonical JSON = sorted keys,
  no whitespace, `ensure_ascii=False`, after NFC; normative digest = sha256 of
  the canonical JSON object, never a concatenation.
- **LLR-RH.1.4** — `email_sha256` = sha256 of the lowercased address; display
  names in clear; `email_sha256` is pseudonymised personal data (unsalted,
  dictionary-reversible) — the jurisdiction question goes to the operator (R23).
- Input limits (R9) live as named constants in `config.py`
  (`LIMIT_EVENT_FILE_BYTES` 64 KiB, `LIMIT_ROLES_YML_BYTES` 4 MiB,
  `LIMIT_REVIEW_FILE_COUNT` 100 000) — the config home every later loader reads
  them from; their enforcement on roles.yml/review/pending files lands with the
  chain and reviews increments that own those files.
- **R19 trunk act, same increment** — `docs/ARCHITECTURE.md` amended: §1 gains
  the read-only git crossing (R11/R20/R27 allowlist), §2 gains the `reqharness`
  module row, §3 gains the `reqharness` dependency row (stdlib + PyYAML +
  `mapper.osopen` only — headless, no Textual) and the `screens`/`app` edges
  into it. No §4 frozen row touched.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/reqharness/__init__.py` | source | HLR-RH.1 | new package docstring (headless contract) |
| `mapper/reqharness/records.py` | source | HLR-RH.1 | error ladder + frozen value objects (Person, ReqClass, ReleaseRule, Config) — named `model.py` when this increment landed; renamed at the batch gate fix (increment-009) so historical `model.py:<line>` citations in older artifacts stay unambiguous (CLOSE3: file cell kept to the bare path so the close-gate reverse trace resolves it; the rename note lives here in the Change column) |
| `mapper/reqharness/canonical.py` | source | LLR-RH.1.3 | NFC, canonical JSON, canonical_digest, chain_hash |
| `mapper/reqharness/config.py` | source | LLR-RH.1.1–1.4 | loader subclass + event scan, typed schema validation, named limits, email_sha256, load_config, create_registry |
| `tests/test_reqharness_config.py` | test | LLR-RH.1.1–1.4 | the four named layer-0 nodes |
| `docs/ARCHITECTURE.md` | doc | R19 | §1 read-only git crossing row; §2 `reqharness` row; §3 `reqharness` row + `screens`/`app` edges; header date |

| Count | Value |
|---|---|
| **SOURCE files** | **4 / 4** |
| Test files | 1 (uncapped) |
| Doc files | 1 (outside the count) |

- At exactly 4 source files: the package needs its four files — the docstring
  package init, the value objects, the canonical form, and the loader/schema —
  and each maps one-to-one to the LLRs; smaller would merge unrelated LLRs.

---

## 3 · How to test

```bash
python -m pytest -p no:cacheprovider tests/test_reqharness_config.py -v
python -m pytest -p no:cacheprovider tests/test_repair_map_truth.py tests/test_arch_osopen_callers.py tests/test_mod_deps.py tests/test_no_operator_paths.py
ruff check mapper/reqharness/ tests/test_reqharness_config.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `test_load_rejects_unknown_reviewer_role`, `test_genesis_creates_chain_with_declared_admin`, `test_canonical_json_typed_schema`, `test_email_sha256_roundtrip` | 4 passed |
| **A · white-box** | | none owed (no dedicated AT for HLR-RH.1) | — |
| **B · black-box** | | none owed (screen ATs are RH6a/6b) | — |

Guards: `test_repair_map_truth` + `test_arch_osopen_callers` +
`test_no_operator_paths` 49 passed; `test_mod_deps` 13 passed; ruff clean.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | five arms, one per named negative control: M-CF1 (`prev_hash` written as `"TAMPERED"`), M-CF2 (reviewer-role cross-check disabled), M-CJ1 (`canonical_digest` hashing the concatenation of values), M-EH1 (email written in clear), M-YC1 (`yaml.load(text, Loader=yaml.SafeLoader)` planted) |
| Instrument | project code, own hand via `.dev-flow/2026-10-11-reqharness-batch/evidence/rh1-red-driver.sh`; restore checked by sha256 |
| Where it ran | **my own worktree** |
| Transcript | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh1-red.transcript` |
| Restore proven by | **file hash returned to its pre-mutation value** (sha256 before == after, per arm, printed in the transcript) |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` on every run |
| Arms resolved at baseline | **5** |
| Verdict granularity | per resolved node id / instrument, printed per arm |
| Arms that stayed GREEN | none — every arm RED |

| Field | Value |
|---|---|
| **RED counterfactual** | M-CF1 → `test_genesis_creates_chain_with_declared_admin` FAILED, restore sha256 `96653f0d…8c43f` byte-identical → PASSED; M-CF2 → `test_load_rejects_unknown_reviewer_role` FAILED, same restore digest → PASSED; M-CJ1 → `test_canonical_json_typed_schema` FAILED, restore sha256 `6963e8ad…c2a1` byte-identical → PASSED; M-EH1 → `test_email_sha256_roundtrip` FAILED, restore byte-identical → PASSED; transcript at `.dev-flow/2026-10-11-reqharness-batch/evidence/rh1-red.transcript` |

| Field | Value |
|---|---|
| **Mutation verdicts** | M-CF1 KILLED at `test_genesis_creates_chain_with_declared_admin` · M-CF2 KILLED at `test_load_rejects_unknown_reviewer_role` · M-CJ1 KILLED at `test_canonical_json_typed_schema` · M-EH1 KILLED at `test_email_sha256_roundtrip` · M-YC1 KILLED by the census instrument (grep found the planted `yaml.load(` at `mapper/reqharness/config.py:98`) — transcript `evidence/rh1-red.transcript`; restore digests above |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| pytest node `test_genesis_creates_chain_with_declared_admin` | genesis `prev_hash` altered (M-CF1) | `1 failed` — see transcript |
| pytest node `test_load_rejects_unknown_reviewer_role` | reviewer-role cross-check removed (M-CF2) | `1 failed` |
| pytest node `test_canonical_json_typed_schema` | concatenation hashing (M-CJ1) | `1 failed` |
| pytest node `test_email_sha256_roundtrip` | clear-text email (M-EH1) | `1 failed` |
| grep census over `mapper/reqharness/` | a load routed through `yaml.load` (M-YC1) | `mapper/reqharness/config.py:98: return list(yaml.load(text, ...))` — 1 file with a hit |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 5 instruments, each shown RED before its PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| `reqharness/config.yml` | clear-text email regex `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}` over the written bytes | 0 matches (M-EH1's arm, inside `test_email_sha256_roundtrip`) |
| `reqharness/roles.yml` genesis | recomputed `sha256("GENESIS\n" + canonical_json(event_without_this_hash))` vs the written `this_hash` | equal; `config_hash` == `config_digest(load_config(...))` |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts, each asserted against the bytes on disk |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED-proof transcript (account name redacted to `<operator>` per A-110) | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh1-red.transcript` | `9254148aaa84ba63a8a72786974b77e25434488cb833224e8a2c24eaf530b235` |
| RED-proof driver script | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh1-red-driver.sh` | `e1b7554d8a1a29ca418a3776524be2e8eaf5454ac82585fedcb291d44edd8eb7` |

| Field | Value |
|---|---|
| **Evidence files** | 2 artifacts, each at the declared home, cited with the digest of its stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — "no `yaml.load(`/`FullLoader` in `mapper/reqharness/`" (R21 census) |
| If the result is an ABSENCE, what made the search wide enough | the census reads every `*.py` under `mapper/reqharness/`, not a hand list; M-YC1's arm planted a hit and the same grep reported it |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_never_yaml_load_source_census` (lands in `tests/test_reqharness_registry.py`, the reviews increment's file — executed there per `01-requirements.md` §4 LLR-RH.1.1) |
| Conjunctive criteria: one mutation per conjunct | 5 controls, 5 single-conjunct mutations, per-arm verdicts above |
| Synthetic instance of the absent case | M-YC1 arm: the planted `yaml.load(text, Loader=yaml.SafeLoader)` at `config.py:98` (transcript) |
| **Positive control for every probe that returned an ABSENCE** | the M-YC1 arm IS the positive control: the same unmodified grep probe that returns 0 hits on the clean tree returned 1 hit on the planted tree |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rl "reqharness" tests/` | only `tests/test_reqharness_config.py` (this increment's own) |
| B2 file moved on disk | the §2 owned-paths cell `mapper/reqharness/*.py` globs | `tests/test_repair_map_truth.py::test_at_p04_every_owned_path_exists_on_disk` passes (49-guard run) |
| B3 byte-identical golden captures this source | `grep -r "reqharness" tests/goldens/` | 0 hits |
| B4 artifact produced here is consumed elsewhere | `grep -rl "reqharness" mapper/ --include=*.py` | only `mapper/reqharness/` itself (no consumer yet — consumers land RH2+) |

| A3 | interface consumed by another module changed | `grep -rn "from mapper" mapper/reqharness/` | imports `mapper.reqharness.*` only — the `mapper.osopen` edge is DECLARED in ARCH §3 but not yet used (lands with the chain increment) |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1 · B2 · B3 · B4 · A3), each with its command and verdict in the table above |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population | Enumeration method | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| none — no correction of an existing claim | — | — | 0 | — | — |

| Field | Value |
|---|---|
| **Correction population** | none — no correction |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|---|---|---|---|
| none | 0 hits | — | — |

### Signed-balance test ledger

`post = base − deleted + added` → `4 = 0 − 0 + 4` (new source files) ✓ reconciles

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | reviewed by `code-reviewer` — verdict recorded in the batch's independent review rounds (`02-review.md`); findings discharged via the rulings named in this packet |

---

## 5 · Risks

- The anchor/alias refusal rides an event-stream scan before `load_all`
  (the C composer hides aliases from Python overrides); the fallback
  `SafeLoader` path gets the identical refusal through the same scan, but the
  P4 scale measurement (R-SCALE cost) should re-check the double parse.
- `roles.yml` size/count limits are defined and named but their enforcement
  lands with `chain.py`/`reviews.py` (their owning increments) — a hand-loaded
  oversize roles.yml is not yet refused by THIS increment's code.

## 6 · Pending items / spec deviations

- None. M-YC1's permanent census test lives in `tests/test_reqharness_registry.py`
  (a later increment's file set) and is executed there per `01-requirements.md`
  §4 LLR-RH.1.1; here it was proven against the same grep probe (M-YC1 arm).

## 7 · Suggested next task

RH2 — the chain (`mapper/reqharness/chain.py`): append, policy binding,
verify, effective roles at a bound head (HLR-RH.2/HLR-RH.3 mechanisms).

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | ≤4 source files | ✓ | 4/4, §2 |
| 2 | Tests written in this same increment | ✓ | `tests/test_reqharness_config.py` |
| 3 | Layer 0 written where the criterion applies | ✓ | 4 nodes, §4 |
| 4 | RED counterfactual declared | ✓ | 5 arms, transcript + restore digests, §4 |
| 5 | Reverse census declared | ✓ | §4 table |
| 6 | `code-reviewer` passed | ⚠ | PENDING — §4b |
| 7 | No file from another lane touched | ✓ | one lane; `git status` shows only this increment's files |
| 8 | Frozen interfaces untouched | ✓ | no §4 row changed; `test_repair_map_truth` 49-pass guard |
| 9 | Coverage claims verified on disk | ✓ | every claim cites a run in the transcript |
| 10 | Load-bearing emptiness declared | ✓ | yaml.load census + M-YC1 positive control |
| 11 | Mutation verdicts declared | ✓ | per-arm KILLED, §4 |
| 12 | Instrument RED-proof declared | ✓ | 5 instruments |
| 13 | Correction population declared | ✓ | none |
| 14 | Emitted-form assertion declared | ✓ | 2 artifacts |
| 15 | Independent review names somebody | ⚠ | PENDING |
| 16 | Evidence files declared | ✓ | 2 rows with sha256 |

---

## 8 · Code-review follow-up (unit RHI1F, REQUEST-CHANGES review of commit ce590a3)

Independent review (Claude Sonnet) returned REQUEST-CHANGES; this section
records the follow-up fixes.  Source files touched: `mapper/reqharness/config.py`,
`mapper/reqharness/canonical.py` ONLY (`model.py`/`chain.py` belong to another
lane and were not touched).  Transcript: `evidence/rh1f-red.transcript`,
sha256 `f9851e949c346eb1decd3faf0487b0a25ab403389de283bc8610b966ceb14921`.

| Finding | Fix | New/changed node(s) | RED proof |
|---|---|---|---|
| H1 — `TIME_RE` used `match` + `$` with a Unicode `\d`: a trailing `\n` and Arabic-Indic digits were accepted | `re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", re.ASCII)` + `.fullmatch` (`config.py`) | `test_time_format_is_ascii_fullmatch` | reverted → FAILED → restore byte-identical (sha256 `0805410c…`) → PASSED |
| H2 — `create_registry` silently overwrote an existing `config.yml`/`roles.yml` | refuses by name with `RegistryExistsError(ValidationError)` when either file exists; nothing is written | `test_create_registry_refuses_existing_registry` | reverted → FAILED → restore byte-identical → PASSED |
| M1 — `seq`/`roles_seq` accepted `True`/`False` (bool subclasses int) | `check_int` uses `type(v) is int`; exported for the chain reader (RH2) to import; used where `create_registry` constructs `seq`/`roles_seq` | `test_check_int_rejects_bool` | body neutered → FAILED → restore byte-identical → PASSED |
| M2 — no permanent census over `mapper/` banning `yaml.load`/`load_all`/`full_load`/`unsafe_load` | new AST census `tests/test_reqharness_yaml_census.py`: banned calls refused unless `Loader=ReqHarnessLoader`; alias spellings (`import yaml as`, `from yaml import`) covered; `yaml.safe_load`/`safe_dump` (the store.py spelling) not flagged | `test_no_banned_yaml_load_ships_in_mapper`, `test_yaml_load_census_flags_a_planted_violation` | positive control inherent: planted violation on a tmp copy flags exactly the 5 banned calls |
| M3 — `nfc()` silently collapsed two keys that normalise to the same string | `NfcKeyCollision(ValueError)` raised, naming both keys (`canonical.py`) | `test_nfc_refuses_colliding_keys` | reverted → FAILED → restore byte-identical (sha256 `74d974b0…`) → PASSED |
| LOW — `if now` truthiness | `if now is not None`: an empty `now` is refused by name, not replaced with the wall clock | arm in `test_genesis_creates_chain_with_declared_admin` | reverted → FAILED → restore byte-identical → PASSED |
| LOW — `email_sha256` did `strip().lower()` | **Decision:** LLR-RH.1.4 says "sha256 of the LOWERCASED email" and nothing else — `strip()` removed (whitespace is part of the address and changes the hash); NFC retained per R3 (values are normalised before hashing) | arms in `test_email_sha256_roundtrip` | reverted → FAILED → restore byte-identical → PASSED |
| LOW — `LIMIT_*` constants had no named consumer | kept (they pin the R9 names before the consumers exist) with a comment naming the consuming increments: `LIMIT_ROLES_YML_BYTES` → chain reader RH2; `LIMIT_EVENT_FILE_BYTES`/`LIMIT_REVIEW_FILE_COUNT` → reviews/pending store RH4 | comment only | n/a (comment) |

Verification (transcript tail): `python -B -m pytest -q -p no:cacheprovider
tests/test_reqharness_config.py tests/test_no_operator_paths.py
tests/test_reqharness_yaml_census.py` → **12 passed**; `ruff check` on the four
touched files → **All checks passed**.
