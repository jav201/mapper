# Requirements ledger — mapper — Batch 2026-10-11-reqharness-batch

> Append-only. Entries are added in chronological order and never rewritten. The live
> contract is `01-requirements.md`; this file records how it came to say what it says.
> Every entry names the requirement it amends; every requirement names its entries. `V26`
> compares the two sets of pairs both ways.

_No entries yet. The first amendment to the live contract writes the first one, in the
shape the field guide's §7 shows (`req-template.md` in the guide directory init prints), and nothing
above this line is ever edited._

---

### LED-2026-10-11-reqharness-batch.1 — initial contract authored at P1

- **Requirement:** HLR-RH.1, HLR-RH.2, HLR-RH.3, HLR-RH.4, HLR-RH.5, HLR-RH.6, HLR-RH.7, HLR-RH.8, HLR-RH.9, LLR-RH.1.1, LLR-RH.1.2, LLR-RH.2.1, LLR-RH.2.2, LLR-RH.2.3, LLR-RH.3.1, LLR-RH.3.2, LLR-RH.3.3, LLR-RH.4.1, LLR-RH.4.2, LLR-RH.4.3, LLR-RH.4.4, LLR-RH.5.1, LLR-RH.5.2, LLR-RH.6.1, LLR-RH.6.2, LLR-RH.7.1, LLR-RH.7.2, LLR-RH.8.1, LLR-RH.8.2, LLR-RH.8.3, LLR-RH.8.4, LLR-RH.9.1
- **Date:** 2026-10-11
- **What changed:** initial authoring of the live contract at P1 (ARQ design + requirements unit RH1, worker Kimi). Establishes the RH namespacing (US-RH-001…003 · HLR-RH.1…9 · LLR-RH.n.m), the AT assignment AT-077…AT-081 (next free after the verified maximum AT-076), the objects-of-record ruling (HLR/LLR rows of `REQUIREMENTS.md`; US canon + AT table explicitly FOLLOW-UP), the operator P0 rulings O1–O9 as design facts (YAML multi-document role stream with hash chain; `reviews/` one file per event; genesis copy "genesis — declared at registry creation"; admin one-key apply to others / self+non-admin pending; pending glyphs ◐ add / ◌ remove; status band in the roles footer; baselines named + commit SHA under `reqharness/baselines/`, tags manual; `mapper --audit <repo>`; D12 as a 06-docs document this batch), the five derived states plus the `changed (informative)` mark, the release verdict strings (`ready` / `not ready · <reason>` / `not ready · registry not verifiable`), and the identity-spoofing ceiling stated as a requirement (LLR-RH.4.4).
- **Why:** the batch's objective (B-107; rulings B-119/B-121/B-122, prototype verdict B-123) is the ReqHarness vertical slice; every threshold is either a byte-exact string/count oracle or an inspection verdict at the gate that owns it, and every test row names the reddening mutation the PDR §5 declares for it.
- **Evidence:** `01-requirements.md` §2.7 premises 1–6, each with executed evidence (pyyaml dependency line; the AT-number grep topping at AT-076; the `duplicate_chords()` probe showing `R` free on home before/after the door row; `darkside.py:550` `def plain`; the `[project.scripts]` console entry; `git cat-file -t c00dfe9…` → `commit`); design `design/design-proposal.md` §2 (modules/ARQ rows) §3.2 (hash algorithm) §3.4 (state + release semantics) §5 (test cases with mutations M-CF1/2, M-CH1–5, M-RG1–4, M-BL1/2, M-RL1, M-AU1, M-RS1–4) §6 (rejected alternatives); triggers per `state.json` `triggers` (fired A1·A2·A3·B1·C1·C4·C6·C8·D1·E1·E2·F1), mirrored in PLAN.md §Triggers.

### LED-2026-10-11-reqharness-batch.2 — orchestrator ruling R-SCALE folded into the contract

- **Requirement:** HLR-RH.5, LLR-RH.1.1, LLR-RH.3.3, LLR-RH.5.3 (new), LLR-RH.5.4 (new)
- **Date:** 2026-10-11
- **What changed:** folds the scale spike (`spike/rhs-scale.md`, corrected this unit) and orchestrator
  ruling R-SCALE into the design and the contract. (a) YAML loading uses `yaml.CSafeLoader` when
  available, falling back to `yaml.SafeLoader` — never `yaml.load` with any other loader; amends
  LLR-RH.1.1's "safe_load only" clause, §1.2 scope, §2.4 constraints, the PDR §1/§2 C6/§3.5. (b) Review
  event files are IMMUTABLE once written (append-only event store — a correction is a new event);
  mapper keeps a LOCAL, git-ignored parse cache `<repo>/.reqharness-cache/reviews.json` keyed by file
  name + size + mtime → parsed event, invalidated per entry, with `.reqharness-cache/` added to the
  connected repo's `.git/info/exclude` (or documented for `.gitignore`) — cold cost paid once per new
  file; new LLR-RH.5.3. (c) Numeric budget: with a warm cache, deriving all object states for 5 000
  review events and 2 000 requirements completes in ≤ 0.5 s (median of 3) on this machine — a P4
  measurement, not a wall-clock assertion in the suite; the cache is a pure accelerator (deleting it
  changes no result — a test asserts equal outputs with and without); new LLR-RH.5.4. (d) The cache
  never feeds the release verdict without re-validating each event's digest/role semantics (it caches
  PARSING only); mutation M-RG5 added to the PDR §5. LLR-RH.3.3's numeric threshold gains an explicit
  0-mismatch count (validator V4). The spike verdict is corrected: both 20 000-file cases TIMED OUT
  (> 120 s, not measured); 5 000 files take 2.3 s per load with the pure-Python loader; the ~60 s cold
  / ~9 s warm first-read figures are recorded as an antivirus-scan OBSERVATION, not a measurement;
  CSafeLoader measured ~6× faster (0.27 s → 0.044 s for 1 000 docs). The cache lands with the registry
  increment RH3 (`cache.py`, ≤4 source files); PLAN.md §Roadmap and §Risks updated (AV cold-scan risk;
  cache poisoning bounded).
- **Why:** the original spike verdict ("all measured cases sit far inside any interactive budget",
  "20,000 review files load in nanoseconds") was false and could not stand as the design's performance
  basis; R-SCALE is the orchestrator's binding ruling on loader, immutability, cache, and budget.
- **Evidence:** `spike/rhs-scale.md` (corrected verdict + recommendation, timeout rows marked "not
  measured (timeout)"); `evidence/rhs-scale.transcript` (TIMEOUT after 120s lines); design
  `design/design-proposal.md` §1 (scope) §2 (`cache.py` in the module row) §3.5 (measured budget +
  R-SCALE) §5 (M-RG5 row) §6 (AV cold-scan + cache-poisoning risks; "cache derived states" rejected
  alternative) §7 (performance row) §8 (RH3 = registry + digest + derive + cache); `01-requirements.md`
  §1.2 · §2.4 · HLR-RH.5 · LLR-RH.1.1 · LLR-RH.3.3 · LLR-RH.5.3/5.4 · IFC FLOW review-derivation ·
  §6.3; PLAN.md §Key decisions (R-SCALE row) §Roadmap (RH3) §Risks.


---

### LED-2026-10-11-reqharness-batch.3 — ruling R1: the config is bound by policy events in the chain

- **Requirement:** HLR-RH.1, HLR-RH.2, HLR-RH.7, LLR-RH.2.4 (new), LLR-RH.7.1
- **Date:** 2026-10-11
- **What changed:** `config.yml` (classes, normative fields, release rules, people→roles) is bound by
  admin-approved `policy` events in `roles.yml` carrying sha256(canonical config); a mismatch →
  `config changed without approval`, the last approved policy stays in force, release blocked.
  New LLR-RH.2.4 (policy append + mismatch semantics, node `test_policy_event_binds_config`, mutation
  M-P1). HLR-RH.7/LLR-RH.7.1 gain the hard-coded mandatory rules — chain verified · policy verified ·
  every closing review signed by a role in force at its bound head — with config able to ADD rules,
  never remove these. HLR-RH.1's statement, scope (§1.2) and boundary catalog extended; §3.4 of the
  PDR gains the policy row of the release semantics.
- **Why:** architect finding H1 + security finding F1 (block-until): the config sat outside the chain —
  the highest-value file was the least protected; a hand edit to the policy verified clean and took
  effect.
- **Evidence:** `02-review.md` round 1 (H1, F1 rows; ruling R1); PDR §3.2 (`policy` event in the chain
  definition) §3.3 (worked policy document) §3.4 (release semantics) §5 (`test_policy_event_binds_config`
  row, M-P1); `01-requirements.md` HLR-RH.1/2/7 · LLR-RH.2.4/7.1 · §1.2 · §1.3 (policy event).

### LED-2026-10-11-reqharness-batch.4 — ruling R2: head binding on every event, review, pending request and baseline

- **Requirement:** HLR-RH.2, HLR-RH.3, HLR-RH.4, HLR-RH.5, LLR-RH.1.2, LLR-RH.2.3, LLR-RH.2.5 (new), LLR-RH.3.1, LLR-RH.4.5 (new), LLR-RH.5.1
- **Date:** 2026-10-11
- **What changed:** every review event, pending request and baseline records the roles-chain head it was
  made against (`roles_seq` + `roles_hash`); verify fails if any recorded head is not in the current
  chain (detects tail truncation and rewrites from genesis). Authority is evaluated at the bound head
  (seq), NOT at wall-clock time; chain `time` must be non-decreasing; a review bound to a missing head
  → `not verifiable`. New LLR-RH.2.5 (`test_head_binding_unknown_head_not_verifiable`, M-HB1) and
  LLR-RH.4.5 (head binding on review events/pending; unknown-head arm of the boundary catalog); LLR-RH.2.3
  and LLR-RH.3.1 reworded from time-T to bound-head folding; LLR-RH.1.2's genesis carries `roles_seq: 1`;
  LLR-RH.5.1's precedence table gains the `not verifiable` dominance row; HLR statements and §1.3
  definitions (head binding, bound head) updated. Residual risk stated: a writer with repo access can
  still rewrite chain + every review consistently — B-122 layer 3 (signed commits) is the follow-up;
  git anchoring of genesis is a follow-up, not this batch.
- **Why:** security findings F2 (block-until — tail truncation/full rewrite verified clean) and F3
  (block-until — self-declared time → backdating); architect findings H2 (with R3) and M1; qa F10 limb.
- **Evidence:** `02-review.md` round 1 (F2, F3, M1 rows; ruling R2); PDR §2.1 (threat-model layers 2–3
  with the stated residual) §3.2 (`verify`/`authority`/`fork` rewrite) §3.3 (worked head-bound formats)
  §3.4 (precedence row 1) §5 (`test_head_binding_unknown_head_not_verifiable`, M-HB1);
  `01-requirements.md` HLR-RH.2/3/4/5 · LLR-RH.1.2/2.3/2.5/3.1/4.5/5.1 · §1.3.

### LED-2026-10-11-reqharness-batch.5 — ruling R3: strict canonical form and typed schema

- **Requirement:** HLR-RH.1, LLR-RH.1.1, LLR-RH.1.3 (new), LLR-RH.3.1, LLR-RH.4.1
- **Date:** 2026-10-11
- **What changed:** typed schema for every file — all fields `str` except `seq: int`, unknown keys and
  missing keys rejected, the writer always quotes scalars — with Unicode NFC normalisation; canonical
  serialisation for hashing = JSON with sorted keys, no whitespace, ensure_ascii=False, after NFC; the
  normative digest = sha256 of that canonical JSON of `{field: normalised value}` (whitespace collapsed,
  Markdown cell unescaped) — never concatenation. New LLR-RH.1.3 (`test_canonical_json_typed_schema`,
  M-CJ1, with the `{"a":"ab","b":"c"}` vs `{"a":"a","b":"bc"}` boundary pair); LLR-RH.1.1 gains the
  typed-schema clauses; LLR-RH.3.1's link formula re-cited to canonical JSON per LLR-RH.1.3; LLR-RH.4.1
  reworded from "concatenation of field values" to the canonical-JSON digest; §1.3 gains canonical
  JSON / normative digest definitions; premise rows 7–8 added to §2.7.
- **Why:** architect finding H2 (with R2/R4): "canonical hashing" broke on real YAML — CSafeLoader coerces
  `2026-10-11T09:00:00Z`→datetime, `no`/`on`→bool, empty→None (json.dumps then fails); and
  `sha256("ab"+"c") == sha256("a"+"bc")` is a field-boundary ambiguity.
- **Evidence:** `02-review.md` round 1 (H2 row; ruling R3); PDR §3.2 (canonical/this_hash rewrite) §3.3
  (typed-schema preamble + the worked normative-digest example) §5 (`test_canonical_json_typed_schema`,
  M-CJ1) §6 (concatenation/YAML hashing rejected alternative); `01-requirements.md` HLR-RH.1 ·
  LLR-RH.1.1/1.3/3.1/4.1 · §1.3 · §2.7 premises 7–8.

### LED-2026-10-11-reqharness-batch.6 — ruling R4: the parse cache is content-keyed and lives inside .git/

- **Requirement:** HLR-RH.5, LLR-RH.5.3, LLR-RH.7.2
- **Date:** 2026-10-11
- **What changed:** the parse cache is keyed by sha256(file bytes) — read + hash, skip the parse — and
  lives INSIDE `.git/reqharness-cache/` (local, never tracked, no `.git/info/exclude` write); deleting
  it changes no output (tested); `--audit` runs with the cache OFF and writes nothing anywhere (the
  workspace digest is unchanged — tested). LLR-RH.5.3 is rewritten accordingly (superseding the R-SCALE
  name+size+mtime key and the `.reqharness-cache/` location of LED.2); HLR-RH.5's statement and §1.2/§2
  cite the new location; LLR-RH.7.2 gains the cache-off + digest-unchanged clauses and the boundary
  catalog gains the large-registry cold-vs-warm equality arm. The integrity claim is reworded: integrity
  follows from the content key.
- **Why:** architect finding H3 + security finding F4: the mtime key could reuse a stale parse and change
  a verdict (mtime is coarse on Drive/FAT; a preserve-mtime rewrite defeats it); the "integrity" claim
  was false. qa QM2 (cache identity) and QM3 (audit side effects) answered by the same ruling.
- **Evidence:** `02-review.md` round 1 (H3, QM2, QM3, F4 rows; ruling R4); PDR §3.5 (R4 bullets
  replacing the R-SCALE cache bullet) §6 (mtime-keyed cache rejected alternative);
  `01-requirements.md` HLR-RH.5 · LLR-RH.5.3/7.2 · §1.2.

### LED-2026-10-11-reqharness-batch.7 — ruling R5: unentitled reviews are pre-review, flagged, and never block alone

- **Requirement:** HLR-RH.4, HLR-RH.5, HLR-RH.7, LLR-RH.4.2, LLR-RH.4.3, LLR-RH.5.1, LLR-RH.7.1
- **Date:** 2026-10-11
- **What changed:** a review whose signer did not hold the designated role at its bound head counts as
  `pre-reviewed` and is flagged `unentitled`; it never blocks the release by itself. `not verifiable` is
  reserved for chain/policy breaks and unknown heads. Model reviews (`kind: model`) are self-declared —
  the design and requirements say so — and are pre-review only. Precedence table explicit: a newer
  pre-review never downgrades a qualifying human review on the same digest; any review on a stale digest
  does not close. LLR-RH.4.2/4.3/5.1/7.1 and HLR-RH.4/5/7 reworded; the PDR §3.4 gains the precedence
  table and the `unentitled` count; `signers_in_force` is replaced in the mandatory rules by "every
  closing review signed by a role in force at its bound head" (the tautology removed); AT-080 counts
  pre-reviews and unentitled separately.
- **Why:** architect findings H4 (one unentitled review blocked every release forever; `signers_in_force`
  tautological) and M6 (precedence ambiguous); qa QM7.
- **Evidence:** `02-review.md` round 1 (H4, M6, QM7 rows; ruling R5); PDR §3.4 (precedence table) §5
  (AT-080 count arms); `01-requirements.md` HLR-RH.4/5/7 · LLR-RH.4.2/4.3/5.1/7.1 · §1.3 (unentitled).

### LED-2026-10-11-reqharness-batch.8 — ruling R6: pending requests have a home and two resolution keys

- **Requirement:** HLR-RH.2, HLR-RH.8, LLR-RH.2.2, LLR-RH.8.6 (new)
- **Date:** 2026-10-11
- **What changed:** `reqharness/pending/<yyyymmdd>-<sha8>.yml`, one file per request (requested by,
  change, bound head). The roles screen resolves them: `a` approve / `r` reject (admin only; never one's
  own); the resolution is a chain event referencing the request hash; a resolved request is derived from
  the chain (the file is not deleted). Survives restart (AT-082 closes and reopens the app). A non-admin's
  `a` shows exactly "a is unavailable (needs an admin)". New LLR-RH.8.6 (node
  `test_at_082_admin_resolves_pending_with_a_and_r`, M-PR1); LLR-RH.2.2 reworded from "return a pending
  request" to the pending FILE store; HLR-RH.2/8 and US-RH-001 updated; new AT-082 born; PDR §3.3 gains
  the worked pending file.
- **Why:** architect finding H5 (pending had no home) + qa findings QH1 (pending storage undefined, no
  restart arm) and QH2 (no approve/reject keys or AT).
- **Evidence:** `02-review.md` round 1 (H5, QH1, QH2 rows; ruling R6); PDR §3.3 (pending worked example)
  §5 (AT-082 row, M-PR1) §6 (delete-to-resolve rejected alternative);
  `01-requirements.md` HLR-RH.2/8 · LLR-RH.2.2/8.6 · US-RH-001 · §5.1.

### LED-2026-10-11-reqharness-batch.9 — ruling R7: forks exclude both children deterministically, with a documented recovery

- **Requirement:** HLR-RH.3, LLR-RH.3.2, LLR-RH.3.4 (new)
- **Date:** 2026-10-11
- **What changed:** two events with the same `prev` → both children excluded from authority
  (deterministic on every clone, both document orders), reported as `chain forked at seq N`; recovery:
  an admin re-appends the intended change on top of the head (documented procedure + test). New
  LLR-RH.3.4 (`test_fork_recovery_reappend_on_head`, M-FR1); LLR-RH.3.2 reworded from "longest verified
  prefix wins" to both-children exclusion; HLR-RH.3 and the band wordings updated; new AT-083 born; PDR
  §3.2 gains the `fork` line and §6 the rejected alternative (merge-order resolution).
- **Why:** architect finding M2: the fork outcome depended on merge order (a 3-way merge can resolve
  silently) and there was no recovery procedure.
- **Evidence:** `02-review.md` round 1 (M2 row; ruling R7); PDR §3.2 (fork line) §5
  (`test_merge_fork_is_detected` both-orders arm, `test_fork_recovery_reappend_on_head`, M-FR1/M-FR2,
  AT-083) §6 (rejected alternative); `01-requirements.md` HLR-RH.3 · LLR-RH.3.2/3.4.

### LED-2026-10-11-reqharness-batch.10 — ruling R8: file names from canonical content, exclusive create, osopen confinement

- **Requirement:** HLR-RH.2, HLR-RH.4, LLR-RH.4.6 (new), LLR-RH.7.2
- **Date:** 2026-10-11
- **What changed:** review and pending files named `<yyyymmdd>-<sha8 of canonical content>.yml`,
  written with exclusive create; `reqharness/` path confinement reuses `mapper.osopen.confine_reason` /
  `is_link` (reqharness may import osopen — stdlib-only; ARCH §3 amended); `..`, links and junctions
  refused. New LLR-RH.4.6 (`test_review_file_naming_and_exclusive_create`, M-FN1); LLR-RH.7.2 gains the
  escaping-path node (`test_audit_cli_refuses_escaping_repo_path`, M-AU2); HLR-RH.2/4 and §2.4 updated;
  premise 7 added to §2.7. The name shape replaces `0001-hlr-rh-1.yml` everywhere (PDR §3.3 worked
  example renamed).
- **Why:** architect findings M3 (names like `0001-…` collide across branches and reveal nothing about
  content) and M5 (path containment reinvented its own rule); security finding F8 (names from caller
  input, no exclusive create, link/junction traversal).
- **Evidence:** `02-review.md` round 1 (M3, M5, F8, QM11 rows; ruling R8); PDR §3.3 (renamed worked
  files) §5 (`test_review_file_naming_and_exclusive_create`, M-FN1; `test_audit_cli_refuses_escaping_repo_path`)
  §2 (osopen inbound edge); `01-requirements.md` HLR-RH.2/4 · LLR-RH.4.6/7.2 · §2.4 · §2.7 premise 7.

### LED-2026-10-11-reqharness-batch.11 — ruling R9: input limits, alias/duplicate rejection, named refusals

- **Requirement:** HLR-RH.3, LLR-RH.1.1, LLR-RH.3.5 (new)
- **Date:** 2026-10-11
- **What changed:** ≤ 64 KB per review/pending file, ≤ 4 MB roles.yml, ≤ 100 000 review files; YAML
  anchors/aliases rejected; duplicate keys rejected; RecursionError/ValueError caught as in
  `mapper/store.py:706-720`; a malformed or oversize file is reported BY NAME, never silently skipped.
  New LLR-RH.3.5 (`test_input_limits_reported_by_name`, M-LM1, 5 refusal fixtures); LLR-RH.1.1 gains
  the anchor/duplicate-key clauses; HLR-RH.3 and §2.4 updated; premise 8 added to §2.7; boundary
  catalogs gain the limit arms.
- **Why:** security finding F6 (no size/depth/count limits, aliases, duplicate keys); qa QM1 boundary
  gaps (malformed YAML across the file kinds).
- **Evidence:** `02-review.md` round 1 (F6, QM1 rows; ruling R9); PDR §2.1 (layer 0) §5
  (`test_input_limits_reported_by_name`, M-LM1); `01-requirements.md` HLR-RH.3 · LLR-RH.1.1/3.5 · §2.4 ·
  §2.7 premise 8.

### LED-2026-10-11-reqharness-batch.12 — ruling R10: markup safety is the Text sink, not plain()

- **Requirement:** HLR-RH.8, LLR-RH.8.4, LLR-RH.8.5 (new)
- **Date:** 2026-10-11
- **What changed:** file-derived text reaches the screen only through `rich.text.Text(...)` /
  `Text.append` sinks — never `Static(str)`, markup=True widgets, notify markup, or help text; a census
  enforces it; the `plain()` sentence corrected (`plain()` preserves content; it does not escape markup —
  the sink is the safety). New LLR-RH.8.5 (census arms: hex/glyph literals, sink census, English-only
  oracle); LLR-RH.8.4 reworded; premise 4 of §2.7 corrected; PDR §2.1 C8 and §6 updated; AT-077c born
  around the painting arms.
- **Why:** security finding F5 (`plain()` does not escape markup — the safety came from painting into
  `Text`); qa QH4 (token/glyph census had no oracle); architect LOW-c ("authorized at WRITE time" false —
  no review write API this batch; corrected in the same pass).
- **Evidence:** `02-review.md` round 1 (F5, QH4, LOW-c rows; ruling R10); PDR §2.1 C8 · §5 (AT-077c,
  M-RS1b) §6 (`plain`-as-mechanism rejected); `01-requirements.md` HLR-RH.8 · LLR-RH.8.4/8.5 · §2.4 ·
  §2.7 premise 4.

### LED-2026-10-11-reqharness-batch.13 — ruling R11: the git read-only allowlist and the identity reader

- **Requirement:** HLR-RH.7, LLR-RH.4.4, LLR-RH.7.3 (new)
- **Date:** 2026-10-11
- **What changed:** `docs/ARCHITECTURE.md` (§1 crossings + §2 module row naming `screens/roles.py`'s
  reqharness edge + §3 rules incl. the `osopen` inbound edge) is amended in the increment that creates
  the module — written, not claimed earlier. `mapper/reqharness/` may run read-only `git rev-parse`
  (`--show-toplevel`, `HEAD`), `git config --get user.name|user.email`, `git status --porcelain`
  (dirty flag), `git log --format=... -- reqharness/reviews/<file>` (committer email of a review —
  `--audit` WARNS on mismatch, report only). Identity = repo-local then global `git config`; tests
  inject identity. New LLR-RH.7.3 (`tests/test_reqharness_identity.py`, allowlist census, M-ID1);
  LLR-RH.4.4 reworded; HLR-RH.7 updated; §2.4/§2.8 row 1 corrected (LOW-d); §1.5 references updated.
- **Why:** architect finding M4 (subprocess contradiction — identity needs `git config` but ARCH §1
  banned git-CLI crossings except `diff`; cache + `.git/info/exclude` writes contradicted "writes only
  under reqharness/"; `--audit` in CI must write nothing) + security finding F7 (reviewer not bound to
  the committer) + LOW-a/b/c/d.
- **Evidence:** `02-review.md` round 1 (M4, F7, LOW-a…d rows; ruling R11); PDR §1 (allowlist sentence)
  §2 (identity.py row) §3.6 (allowlist table + ARCH amendment plan) §5 (`test_identity_reader_repo_local_then_global`,
  M-ID1); `01-requirements.md` HLR-RH.7 · LLR-RH.4.4/7.3 · §2.4 · §2.8.

### LED-2026-10-11-reqharness-batch.14 — ruling R12: emails stored only as hashes

- **Requirement:** HLR-RH.1, LLR-RH.1.4 (new)
- **Date:** 2026-10-11
- **What changed:** `config.yml` stores `email_sha256` (sha256 of the lowercased email), display names
  in clear; the identity reader matches the git email by the same hash; a personal-data note is
  documented in the PDR. New LLR-RH.1.4 (`test_email_sha256_roundtrip`, M-EH1); HLR-RH.1 and the §3.3
  worked config updated.
- **Why:** security finding F9: emails in config are personal data.
- **Evidence:** `02-review.md` round 1 (F9 row; ruling R12); PDR §3.3 (email_sha256 worked config) §5
  (`test_email_sha256_roundtrip`, M-EH1); `01-requirements.md` HLR-RH.1 · LLR-RH.1.4 · §1.3 (email_sha256).

### LED-2026-10-11-reqharness-batch.15 — ruling R13: baselines record the dirty flag and diff six classes

- **Requirement:** HLR-RH.6, LLR-RH.6.1, LLR-RH.6.2
- **Date:** 2026-10-11
- **What changed:** record `dirty: true|false` (from `git status --porcelain`) and refuse nothing; the
  diff classes become new · changed · unchanged · retired · deleted · reactivated (retired→active),
  with deleted covering canon ids absent from the current canon (and deleted review files via the
  baseline's review set — the F10 limb); review-state progression (reviewed in base → still reviewed /
  changed · review / pre-reviewed) stated. LLR-RH.6.1/6.2 and HLR-RH.6 reworded; §1.3 gains the
  deleted/reactivated definitions; PDR §3.3 (worked baseline with `dirty` + `review_files`) and §3.4
  (diff paragraph) updated; AT-081 extended to six mutations.
- **Why:** architect finding M7 (dirty tree, deleted ids, retired→active unclassified) + qa QM6 +
  security F10 (baseline limb).
- **Evidence:** `02-review.md` round 1 (M7, QM6, F10 rows; ruling R13); PDR §3.3 §3.4 §5 (AT-081 six
  classes, M-BL2); `01-requirements.md` HLR-RH.6 · LLR-RH.6.1/6.2 · §1.3.

### LED-2026-10-11-reqharness-batch.16 — ruling R14: the QA bundle (AT re-specs, censuses, boundary catalog, thresholds)

- **Requirement:** HLR-RH.6, HLR-RH.7, HLR-RH.8, LLR-RH.2.3, LLR-RH.6.2, LLR-RH.7.2, LLR-RH.8.1, LLR-RH.8.2, LLR-RH.8.3, LLR-RH.8.5
- **Date:** 2026-10-11
- **What changed:** AT-080 renamed `test_at_080_audit_report_counts_every_state_exactly` — one object
  per state, exact per-state counts, pre-reviews and unentitled counted separately, the informative
  mark, numeric exit-code thresholds {0,1}, 60 s subprocess timeout, workspace-digest-unchanged oracle;
  `test_audit_cli_on_seeded_repo` retired from the contract (superseded). Token oracle = monkeypatch
  the darkside token and assert the paint changes + a source census for hex/glyph literals in
  `screens/roles.py` (LLR-RH.8.5); "never yaml.load" source census + fallback-loader test (LLR-RH.1.1);
  boundary catalog adds deleted/corrupted review file, malformed YAML (roles.yml, review, pending,
  config), large registry cold vs warm equality, canon unparseable row → reported line, withdrawn
  marker = canon status starting with `withdrawn`, deleted canon id → `deleted`; the tampered state
  makes the matrix read-only (space inert, message — LLR-RH.8.2, AT-079); the band shows event count,
  head hash, viewer identity and pending detail as in prototype B (LLR-RH.8.3, AT-077b); screen ATs at
  118 AND 87 columns (LLR-RH.8.1); genesis copy asserted on screen (AT-077a); AT-077 split by job —
  AT-077a open+paint+genesis, AT-077b band detail, AT-077c markup/sink/census oracles; numeric
  thresholds explicit everywhere; M-CH5 redefined as the `<`↔`<=` flip mutation (LLR-RH.2.3); M-AU1
  timeout 60 s (LLR-RH.7.2); home door-count 7→8 regression row (LLR-RH.8.1); English-only oracle =
  a source census of user-visible strings in `screens/roles.py` for non-ASCII letters except the glyph
  set (LLR-RH.8.5); viewer identity pinned by injected repo-local git config (AT-077b/AT-078); §6.1
  mutation glossary added (no id reused).
- **Why:** qa-reviewer findings QH3, QH4, QM1, QM4–QM11, QL1–QL5; architect M8 (RH5/RH6 merge limb)
  and LOW-a.
- **Evidence:** `02-review.md` round 1 (QH3/QH4, QM1–QM11, QL1–QL5, M8 rows; ruling R14); PDR §5 (the
  full re-specified AT table: AT-077a/b/c, AT-078, AT-079, AT-080, AT-081, AT-082, AT-083 with
  mutations M-CH5, M-AU1, M-RS1–4, M-PR1, M-FR2); `01-requirements.md` HLR-RH.6/7/8 · LLR-RH.2.3/6.2/
  7.2/8.1/8.2/8.3/8.5 · §5.1 · §6.1.

### LED-2026-10-11-reqharness-batch.17 — ruling D13: the connected repo is the containing git work tree

- **Requirement:** HLR-RH.7, HLR-RH.8, LLR-RH.7.2, LLR-RH.8.1
- **Date:** 2026-10-11
- **What changed:** the connected repo = the git work tree containing mapper's current workspace,
  discovered with `git rev-parse --show-toplevel`; `mapper --audit <repo>` overrides; no repo → the
  roles screen says so and offers nothing to edit. LLR-RH.7.2 gains the discovery + override +
  headless-refusal clauses (`test_audit_cli_refuses_escaping_repo_path` arm); LLR-RH.8.1/HLR-RH.8 gain
  the no-repo screen state; §2.1 updated; PDR §3.1/§3.6 cite the discovery command.
- **Why:** architect finding M8 (repo-root discovery for RolesScreen unspecified — `MapperApp(workspace)`
  is a maps dir).
- **Evidence:** `02-review.md` round 1 (M8 row; ruling D13); PDR §3.1 (repo subgraph label) §3.6
  (allowlist row) §8; `01-requirements.md` HLR-RH.7/8 · LLR-RH.7.2/8.1 · §2.1.

### LED-2026-10-11-reqharness-batch.18 — ruling R15: genesis records `roles_hash: "GENESIS"` and carries `config_hash`

- **Requirement:** HLR-RH.1, LLR-RH.1.2, LLR-RH.2.4
- **Date:** 2026-10-11
- **What changed:** the genesis event records `roles_hash: "GENESIS"` (no self-reference) and
  `config_hash` = sha256(canonical config at creation); `create_registry` therefore produces a
  policy-bound registry from the first document; at load/release the live config hash is compared
  with the newest verified policy-bearing event's (genesis or `policy`) `config_hash`. New mutation
  arm M-CF1: a genesis without `config_hash` fails. HLR-RH.1 · LLR-RH.1.2 · LLR-RH.2.4 reworded;
  §1.3 genesis definition updated; PDR §3.2 (genesis block) + §6 (rejected alternative row).
- **Why:** architect finding A1 HIGH (genesis hashes itself — a circular binding — and a fresh
  registry had no policy event: a policy change could be "undone" by reverting to genesis, a new
  backdating hole).
- **Evidence:** `02-review.md` round 2 (A1 row; ruling R15); PDR §3.2 §6; `01-requirements.md`
  HLR-RH.1 · LLR-RH.1.2/2.4 · §1.3.

### LED-2026-10-11-reqharness-batch.19 — ruling R16: fork recovery is a `resolve` event

- **Requirement:** HLR-RH.3, LLR-RH.3.4
- **Date:** 2026-10-11
- **What changed:** after both fork children are excluded, the only legal continuation is a
  `resolve` event — admin-approved, `prev_hash` = the chosen child, naming the excluded sibling's
  hash — after which the chain verifies again; recovery remains a DOCUMENTED manual procedure this
  batch (fork-recovery UI automation deferred, B-126); the re-append recovery wording and the
  `test_fork_recovery_reappend_on_head` node are replaced by `resolve` and
  `test_fork_resolve_event_recovers`; M-FR1 redefined (resolve keeping the excluded child / naming
  the wrong sibling). §1.3 gains the `resolve event` definition; PDR §3.2 (fork block) §5
  (recovery node row) §6 (recovery risk).
- **Why:** architect finding A2 HIGH (fork recovery by re-append contradicted verify — a re-appended
  event lands on a head whose child set is ambiguous) + security finding on recovery authority.
- **Evidence:** `02-review.md` round 2 (A2 row; ruling R16); PDR §3.2 §5 §6; `01-requirements.md`
  HLR-RH.3 · LLR-RH.3.4 · §1.3.

### LED-2026-10-11-reqharness-batch.20 — ruling R17: `--audit` warns on old-head binding

- **Requirement:** LLR-RH.4.2
- **Date:** 2026-10-11
- **What changed:** stated residual — a revoked reviewer can bind a NEW review to an older head
  where they still held the role; `--audit` WARNS (non-blocking) when a review's bound head precedes
  a later revocation of its signer's role, as a core comparison over the chain (no git); layer 3
  remains the strong answer. LLR-RH.4.2 gains the WARN clause + boundary row; §1.3 gains the
  old-head-binding definition; PDR §2.1 (layer-2 residual).
- **Why:** architect finding A3 HIGH (binding to an old head is a new backdating hole — bound-head
  role checking alone cannot see it).
- **Evidence:** `02-review.md` round 2 (A3 row; ruling R17); PDR §2.1; `01-requirements.md`
  LLR-RH.4.2 · §1.3.

### LED-2026-10-11-reqharness-batch.21 — ruling R18: exact schema — `str` scalars, `seq`/`roles_seq` int, one exact time format

- **Requirement:** LLR-RH.1.1, LLR-RH.1.3, LLR-RH.2.5
- **Date:** 2026-10-11
- **What changed:** all scalar fields are `str` except `seq` and `roles_seq` (int); every field is
  isinstance-checked; `time` fields match exactly `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`;
  non-decreasing time compares those strings over the one exact format (no datetime coercion —
  CSafeLoader turns ISO-8601 into datetime otherwise). LLR-RH.1.1/1.3 reworded; §1.3 gains the
  `time` definition; §2.4 loader bullet + LLR-RH.2.5 cite it; PDR §3.2 (event block).
- **Why:** architect finding A4 MED (`roles_seq` int vs "all str except seq" was contradictory; time
  comparison needs one exact format).
- **Evidence:** `02-review.md` round 2 (A4 row; ruling R18); PDR §3.2; `01-requirements.md`
  LLR-RH.1.1/1.3 · LLR-RH.2.5 · §1.3 · §2.4.

### LED-2026-10-11-reqharness-batch.22 — ruling R19: the ARCHITECTURE amendment lands in increment 1

- **Requirement:** LLR-RH.7.3
- **Date:** 2026-10-11
- **What changed:** the `docs/ARCHITECTURE.md` amendment (§1 crossings with the read-only git
  allowlist; §2 module row for `reqharness`, naming `screens/roles.py` on the screens edge; §3 rules
  — reqharness imports osopen and stdlib/PyYAML only, screens/roles.py may import reqharness, the
  git read-only crossing) is written inside increment 1, not claimed earlier. LLR-RH.7.3 states it;
  §1.4 reference + §2.8 row 1 + §5.2 updated; PDR §3.6 (amendment paragraph) §7 §8.
- **Why:** architect finding A6 MED (the amendment must land at increment 1 — the module row is the
  increments' dependency contract, not a closing garnish).
- **Evidence:** `02-review.md` round 2 (A6 row; ruling R19); PDR §3.6 §7 §8; `01-requirements.md`
  LLR-RH.7.3 · §1.4 · §2.8 · §5.2.

### LED-2026-10-11-reqharness-batch.23 — ruling R20: the git allowlist reduced and hardened

- **Requirement:** LLR-RH.7.3
- **Date:** 2026-10-11
- **What changed:** the allowlist drops `git log` entirely (the committer-vs-reviewer email warning
  is deferred, B-124) and keeps only `git rev-parse --show-toplevel` / `rev-parse HEAD`, `git
  config --get user.name|user.email`, `git status --porcelain --no-optional-locks`; every call is an
  argv list with `shell=False`, a 10 s timeout, the prefix `git --no-pager -c core.fsmonitor= -c
  core.hooksPath=<platform null>`, `GIT_OPTIONAL_LOCKS=0`, and inherited `GIT_DIR`/`GIT_WORK_TREE`/
  `GIT_CONFIG*` stripped (a repo's `core.fsmonitor` can execute code on `git status`, and a plain
  `git status` refreshes `.git/index`, breaking "audit writes nothing"). New fixtures: a
  `core.fsmonitor` sentinel stays absent after `--audit`; `.git/index` byte-identical after
  `--audit`; a census of the exact argv shapes. §1.2 deferral note; §2.4 constraint bullet reworded;
  PDR §3.6 (allowlist table + hardening paragraph).
- **Why:** security finding G1 (git inside an untrusted repo — `core.fsmonitor` code execution on
  `git status`; `git status` refreshes `.git/index`, breaking the read-only claim) + architect A7
  (one `git log` per review file does not scale).
- **Evidence:** `02-review.md` round 2 (G1/A7 rows; ruling R20); PDR §3.6; `01-requirements.md`
  LLR-RH.7.3 · §1.2 · §2.4.

### LED-2026-10-11-reqharness-batch.24 — ruling R21: a custom loader subclass rejects anchors/aliases and duplicate keys at compose time

- **Requirement:** LLR-RH.1.1
- **Date:** 2026-10-11
- **What changed:** YAML loading runs through a custom loader subclass on `yaml.CSafeLoader` when
  available, falling back to `yaml.SafeLoader` — never `yaml.load` with any other loader; the
  subclass rejects anchors/aliases and duplicate keys at COMPOSE time (CSafeLoader alone silently
  accepts both — rejecting them needs the subclass at some speed cost); fixtures prove both; the
  cost is measured at P4 against the 0.5 s budget (the trade-off stated there). §2.4 loader bullet
  reworded; PDR §3.5 (loader bullet) §2.1 C6.
- **Why:** security probe LOW (CSafeLoader silently accepts anchors/aliases and duplicate keys —
  rejecting them needs a custom loader subclass at some speed cost).
- **Evidence:** `02-review.md` round 2 (LOW probe row; ruling R21); PDR §3.5 §2.1; `01-requirements.md`
  LLR-RH.1.1 · §2.4.

### LED-2026-10-11-reqharness-batch.25 — ruling R22: the loader recomputes sha8 over file content

- **Requirement:** LLR-RH.4.6
- **Date:** 2026-10-11
- **What changed:** the loader recomputes sha8 over the canonical content of every review/pending
  file; a mismatch with the file name is reported BY NAME and non-closing; a renamed/tampered file
  cannot close a state. New mutation M-FN2 (skip the sha8 content check → the mismatch fixture
  passes silently → RED); M-FN1 keeps its exclusive-create meaning. LLR-RH.4.6 gains the check
  clause + boundary row; §1.2 in-scope bullet; §6.1 glossary; PDR §5 (naming node row).
- **Why:** security finding G-row limb + qa-reviewer boundary review (a name/content mismatch must
  never close silently).
- **Evidence:** `02-review.md` round 2 (ruling R22); PDR §5; `01-requirements.md` LLR-RH.4.6 · §1.2
  · §6.1.

### LED-2026-10-11-reqharness-batch.26 — ruling R23: residuals and the privacy note recorded

- **Requirement:** LLR-RH.1.4, LLR-RH.4.4
- **Date:** 2026-10-11
- **What changed:** the threat model and the requirements list as stated residuals: a deleted review
  is detected only against a baseline that listed it; truncation of tail events no review or
  baseline has bound yet verifies clean; `reviewer` is free text (identity is git config); old-head
  binding (R17); a consistent full rewrite (layer 3). `email_sha256` is described as PSEUDONYMISED
  personal data — unsalted, dictionary-reversible — and the jurisdiction question goes to the
  operator. LLR-RH.1.4 gains the privacy note; PDR §2.1 (layer-1/2/3 residuals + personal-data
  paragraph); `01-requirements.md` §6.3 open risks.
- **Why:** security review round 2 (residuals must be stated, not hidden; the personal-data
  classification of an unsalted email hash must be explicit).
- **Evidence:** `02-review.md` round 2 (ruling R23); PDR §2.1; `01-requirements.md` LLR-RH.1.4 · §6.3.

### LED-2026-10-11-reqharness-batch.27 — ruling R24: baselines trimmed to five classes plus the dirty flag

- **Requirement:** HLR-RH.6, LLR-RH.6.1, LLR-RH.6.2
- **Date:** 2026-10-11
- **What changed:** the diff classes are new · changed · unchanged · retired · deleted plus the
  `dirty` flag; `reactivated` (retired → active) and the review-state progression are DEFERRED
  (B-125) — marked, not deleted (the ids stay in the §1.3 glossary). New mutants M-BL3 (`deleted`
  collapsed into `retired`) and M-BL4 (dirty flag forced); AT-081 re-specified over five mutations.
  HLR-RH.6 renamed (five classes) · LLR-RH.6.2 reworded · §1.2/§2.2/§1.3 updated; PDR §3.4 §5
  (AT-081/M-BL rows).
- **Why:** the round-2 weight assessment (drifting heavy — the batch keeps policy binding, head
  binding, pending + a/r, content cache, email hashing, input limits; the baseline surface is
  trimmed).
- **Evidence:** `02-review.md` round 2 (weight assessment; ruling R24); PDR §3.4 §5;
  `01-requirements.md` HLR-RH.6 · LLR-RH.6.1/6.2 · §1.2/2.2/1.3.

### LED-2026-10-11-reqharness-batch.28 — ruling R25: increment 6 splits into 6a and 6b

- **Requirement:** HLR-RH.8, LLR-RH.8.1, LLR-RH.8.6
- **Date:** 2026-10-11
- **What changed:** the roles-screen increment splits: 6a = the roles screen (matrix + home seat +
  footer band + pending requests by `space`: AT-077a/b/c, AT-078, AT-079) and 6b = the admin `a`/`r`
  resolution (AT-082); AT-083 (fork) keeps detection + exclusion on screen, recovery core-only.
  The shipped-surface ownership and the §5.1 layer-B listing name the split; PDR §7/§8 and PLAN.md
  increments re-planned.
- **Why:** the round-2 weight assessment (split increment 6 — the screen and the resolution keys
  are separately gateable).
- **Evidence:** `02-review.md` round 2 (weight assessment; ruling R25); PDR §7 §8;
  `01-requirements.md` HLR-RH.8 · LLR-RH.8.1/8.6 · §5.1 · PLAN.md.

### LED-2026-10-11-reqharness-batch.29 — ruling R26: the QA items (exact nodes, fixtures, mutation definitions)

- **Requirement:** HLR-RH.2, HLR-RH.7, LLR-RH.1.1, LLR-RH.2.3, LLR-RH.3.5, LLR-RH.5.1, LLR-RH.5.3, LLR-RH.7.2, LLR-RH.8.1, LLR-RH.8.3
- **Date:** 2026-10-11
- **What changed:** exact nodes + fixtures for syntax-malformed YAML in EACH of the four file kinds
  (config, roles.yml, review, pending), a corrupted review file at derive time (reported by name,
  derives no state), a corrupt cache file (bounded to a re-parse/rebuild, never a verdict change);
  M-CH5 defined precisely — the correct code compares with `<=` ON `roles_seq` (never event time),
  the mutant flips it to `<`; the M-AU1 control uses `subprocess.run(timeout=60)` with
  `TimeoutExpired` counted as FAIL; the home door-count regression checklist NAMES the existing home
  tests it guards; the tampered-band assertion at 87 columns is OPTIONAL (marked, not silently
  dropped).
- **Why:** qa-reviewer round 2 (MED-1 boundary items without exact nodes; MED-2 AT-081 new classes
  weakly controlled; LOW-1 M-CH5 wording; LOW-2 the timeout control; LOW-3 the regression checklist
  names; LOW-4 the optional 87-col band).
- **Evidence:** `02-review.md` round 2 (MED-1/MED-2/LOW-1…4 rows; ruling R26); PDR §5;
  `01-requirements.md` HLR-RH.2/7 · LLR-RH.1.1/2.3/3.5/5.1/5.3/7.2/8.1/8.3 · §6.1.

### LED-2026-10-11-reqharness-batch.30 — ruling R27: round-3 precision fixes (verify by `prev_hash`, git hardening, `no repo`, scope, named home tests)

- **Requirement:** `01-requirements.md` §1.2 scope; HLR-RH.3; HLR-RH.6; LLR-RH.3.1, LLR-RH.3.2, LLR-RH.3.4, LLR-RH.6.1, LLR-RH.7.2, LLR-RH.7.3, LLR-RH.8.1
- **Date:** 2026-10-11
- **What changed:**
  - **R27e — verify walks BY `prev_hash`.** LLR-RH.3.1/3.2/3.4 re-specified: verify is a walk by
    `prev_hash` from genesis, not by file position (the old "recompute every link in order; duplicate
    `prev_hash` → broken" reading failed on parent, childA, childB, resolve). A document whose
    `prev_hash` matches an already-claimed parent is a fork sibling; a sibling is tolerated from
    authority only when a later valid `resolve` names it in `resolve_excludes`; a fork whose excluded
    branch has descendants (multi-event) → `chain broken`, recovery **deferred (B-126)**; a `resolve`
    is valid only when the chosen child itself passes the approval rule at its own bound head. New
    tests: `test_verify_walks_by_prev_hash_in_order_fork_resolve`,
    `test_resolve_naming_non_sibling_is_invalid`, `test_multi_event_excluded_branch_is_broken`;
    new mutants M-FR3 (file-position walk) and M-FR4 (`resolve` legitimates an unentitled child).
  - **R27a — no `git status` in `--audit`.** The dirty flag is taken only by `Baseline.create`,
    which runs in the operator's own repo; residual stated: "baseline creation trusts the repo's
    `.git/config`" (HLR-RH.6, LLR-RH.6.1, LLR-RH.7.2, LLR-RH.7.3; the LLR-RH.7.3 allowlist drops
    the `git status` row from the core/audit path).
  - **R27b — hardened prefix.** Every git call carries `-c core.fsmonitor=false -c
    core.hooksPath=<os.devnull>` (a fixed value disables fsmonitor under any filter name; the
    hooks path is neutralised; `--no-pager` covers `core.pager`; `include.path`/`includeIf` only
    read config; `core.sshCommand`/`credential.helper`/`diff.external` are not invoked by these
    read-only commands).
  - **R27c — absolute git resolution.** `git` is resolved ONCE to an absolute path with
    `NoDefaultCurrentDirectoryInExePath=1` set during resolution and `shutil.which` over an
    explicit PATH excluding the repo (a planted `git.exe` in the audited repo's cwd never wins);
    invoked as `<abs git> -C <repo>` — never `cwd=<repo>`; an argv-census arm asserts the absolute
    executable; new mutant M-ID2.
  - **R27d — `no repo` is named, never a crash.** A `safe.directory` refusal (or any git non-zero,
    timeout included) → the named result `no repo` on screen + audit, exercised by
    `test_safe_directory_refusal_is_named_no_repo_not_a_crash`; new mutant M-AU3.
  - **R27f — scope line.** §1.2 now reads `seq`/`roles_seq: int` (the R18 schema).
  - **R27g — the home tests are named.** LLR-RH.8.1's door-count checklist names the guarded
    tests (the R26 record claimed the naming; it lands here): the count assertion
    `tests/test_inc9c.py::test_inc9c_ux_f4_home_reads_its_labels_from_the_seat` (`len(doors) == 6`),
    `tests/test_inc9e.py::test_inc9e_l3_the_home_bar_paints_the_doors_first`,
    `tests/test_inc9f.py::test_inc9f_r3_cr_f3_home_keeps_its_letters_and_active_mark_under_a_rekeyed_seat`,
    `tests/test_key_dispatch.py::test_at_n03g_each_key_dispatches_its_own_advertised_action`, and
    the pinned-seat census `tests/test_inc9.py::test_cd25_the_pinned_entry_seat_is_not_vacuous` +
    `tests/test_inc9.py::test_cd25a_the_seat_diff_is_exactly_what_inc9_declares` — the screen
    increment re-bases these pins with the `R roles` row (the data-safety E-7 precedent: exactly one
    census declares the addition).
  - Design proposal (`design/design-proposal.md` §3.2 `verify`/`fork`, §3.6 allowlist, §5 test rows)
    amended in the same unit; the PDR is sealed with R27 as its final review amendment.
- **Why:** round 3 (targeted; all three read-only reviewers approve-with-conditions, no HIGH) —
  architect MED verify-vs-resolve wording + LOW scope + LOW resolve entitlement; qa-reviewer LOW-3
  the unnamed home tests; security H1–H4 (filter.clean via .gitattributes, planted `git.exe`,
  `core.hooksPath`, `safe.directory`).
- **Evidence:** `02-review.md` round 3 (findings A-MED/A-LOW-1/A-LOW-2, QA-LOW-3, S-H1…S-H4;
  ruling R27 limbs a–g); `01-requirements.md` HLR-RH.3 · HLR-RH.6 · LLR-RH.3.1/3.2/3.4 ·
  LLR-RH.6.1 · LLR-RH.7.2 · LLR-RH.7.3 · LLR-RH.8.1 · §1.2 · §6.1 · §6.3; PDR §B condition table;
  `design/design-proposal.md` §3.2 §3.6 §5.


---

### LED-2026-10-11-reqharness-batch.31 — code-review follow-up RHFIX23: the bound-head fold filters on the event's own `seq`

- **Requirement:** LLR-RH.2.3
- **Date:** 2026-10-11
- **What changed:** `_roles_in_force` folded with `event.roles_seq <= bound_seq`; an event at
  seq k+1 records `roles_seq` k, so it leaked into the fold at head k — a grant never
  retro-authorizes a review bound to an earlier head, but the old comparison let exactly that
  happen. The fold now filters on `event.seq <= bound_seq` (the verified chain pins every
  event's `seq` to its walk position, so this is the same set for the approval rule and one
  event tighter at the bound-head boundary — the leak disappears). LLR-RH.2.3's statement,
  numeric threshold, negative control (M-CH5 is now the `<=`→`<` flip on the event's own
  `seq`) and boundary catalog reworded; the test node `test_effective_roles_at_time_t` gained
  the ruling fixture (a grant at seq 2 is NOT in force at head 1) and the head-2 arm now
  asserts the grant (seq 3, `roles_seq` 2) is excluded. The same follow-up (unit RHFIX23)
  shipped F1 (the genesis-position pin `(event.action == "genesis") == (position == 1)` in
  `_check_event`, the `_passes_approval` genesis shortcut held to no-prefix, node
  `test_genesis_only_at_position_one`, mutant M-CH6), F3 (`config_hash` REQUIRED on `genesis`
  and `policy` events at the typed schema, node `test_policy_event_requires_config_hash`) in
  `mapper/reqharness/chain.py`, and F4–F7 in `mapper/reqharness/identity.py` (git resolved by
  walking the filtered PATH with the repo/cwd/`.`/empty entries excluded, compared resolved;
  every inherited `GIT_*` stripped from the child env; `(OSError, ValueError, RuntimeError)`
  caught around every `resolve()`; a failed resolution no longer cached).
- **Why:** code review of increments 002/003 (Claude Sonnet) REQUEST-CHANGES — F2 ruling:
  "a grant never retro-authorizes a review bound to an earlier head"; the `roles_seq` fold
  broke exactly that sentence.
- **Evidence:** `03-increments/increment-002.md` / `increment-003.md` "Code-review
  follow-up" sections; `evidence/rh23fix-red.transcript` (7 RED arms, restore-by-sha256;
  sha256 `8fe8f8b8152b2abd21c901adf34325665375295a418bf161ed8a05b6f5547647`);
  `01-requirements.md` LLR-RH.2.3.

---

### LED-2026-10-11-reqharness-batch.32 — DDR ruling ARCH C1 (git): `git` is resolved by walking PATH, not `shutil.which`

- **Requirement:** LLR-RH.7.3
- **Date:** 2026-10-11
- **What changed:** the git-resolution clause is corrected to match the shipped code
  (`mapper/reqharness/identity.py::_which_git`): `git` is resolved ONCE to an ABSOLUTE path
  by walking PATH itself — each directory that resolves to the audited repo, the current
  working directory, `.` or an empty entry is skipped (compared resolved), then `git` plus
  each PATHEXT extension is tried on Windows (PATHEXT fallback `.COM;.EXE;.BAT;.CMD`), plain
  `git` on POSIX, the first existing regular file wins. `shutil.which` + the process-wide
  `NoDefaultCurrentDirectoryInExePath` mutation are GONE — review finding F4 HIGH: before
  Python 3.12 `shutil.which` searches `.` on Windows regardless of that variable. §2.4
  constraint bullet reworded the same way; the IFC identity flow is unchanged (it names the
  commands, not the resolver).
- **Why:** the round-3 ruling R27c wrote the resolution as `shutil.which` over an explicit
  PATH; the code-review follow-up (RHFIX23, finding F4) replaced that with a PATH walk that
  cannot be defeated by a `git.exe` planted in the repo's cwd, and the live contract still
  described the pre-fix mechanism.
- **Evidence:** `mapper/reqharness/identity.py` (`_which_git`, the PATHEXT fallback and the
  repo/cwd/`.`/empty-entry exclusion); `03-increments/increment-003.md` "Code-review
  follow-up" (F4 row, M-ID3); `evidence/rh23fix-red.transcript` (F4/M-ID3 arm); PDR DDR
  amendments (C-R27c); `design/design-proposal.md` §1/§2.1/§3.6/§5.

### LED-2026-10-11-reqharness-batch.33 — DDR ruling ARCH C1 (loader): anchors/aliases refused by an event-stream pre-scan, not "at compose time"

- **Requirement:** LLR-RH.1.1, LLR-RH.3.5
- **Date:** 2026-10-11
- **What changed:** the loader-mechanism phrase "anchors/aliases and duplicate keys rejected
  at compose time" is corrected to match the shipped code (`mapper/reqharness/config.py`):
  duplicate keys are refused at construction time (the `construct_mapping` hook), while
  anchors/aliases are refused by an event-stream PRE-SCAN before construction — because the C
  composer resolves aliases before Python-level overrides can see them, one `yaml.parse`
  scan serves both loader bases with identical behaviour. LLR-RH.1.1 and LLR-RH.3.5
  statements, §1.2 scope and §2.4 constraint bullets all reworded; `design/design-proposal.md`
  C6 and §3.5 reworded the same way.
- **Why:** the requirement said "at compose time" for both refusals, which misstates where the
  anchor/alias refusal actually happens (a pre-scan, not the compose hook); the ledger `.24`
  ruling R21 wording also carried the loose phrase.
- **Evidence:** `mapper/reqharness/config.py` (`load_documents` pre-scan over `yaml.parse`;
  `construct_mapping` duplicate check); `design/design-proposal.md` C6/§3.5; PDR DDR
  amendments.

### LED-2026-10-11-reqharness-batch.34 — DDR ruling ARCH C2 (audit): the `--audit` branch runs AFTER the UTF-8 stdout re-wrap

- **Requirement:** LLR-RH.7.2
- **Date:** 2026-10-11
- **What changed:** the audit-branch ordering clause is corrected from "ahead of the UTF-8
  stdout re-wrap (`app.py:328`)" to "AFTER the UTF-8 stdout re-wrap" — the branch re-wraps
  stdout to UTF-8 first, then runs the audit, so the report prints in UTF-8. The IFC
  FLOW audit-cli NODES line is corrected the same way; the design proposal's module table,
  §4 `app.main` row and the §3.1 diagram label follow; `increment-005.md` gains a follow-up
  note (append-only).
- **Why:** the plan said the branch sat AHEAD of the re-wrap, but the shipped branch re-wraps
  first so the report text is UTF-8-safe; the contract described the wrong order.
- **Evidence:** `design/design-proposal.md` §2 module table + §4 + §3.1; `03-increments/
  increment-005.md` follow-up note; PDR DDR amendments (§A row 7).

### LED-2026-10-11-reqharness-batch.35 — DDR residual note (release): `ready` ≠ every object reviewed unless `all_active_reviewed` is declared

- **Requirement:** HLR-RH.7
- **Date:** 2026-10-11
- **What changed:** HLR-RH.7's statement gains the residual clarification: `ready` does NOT
  mean every object was reviewed — that guarantee holds only when `config.yml` declares the
  `all_active_reviewed` rule; the three hard-coded mandatory rules are chain verified ·
  policy verified · every closing review signed by a role in force at its bound head, and
  `all_active_reviewed` is a config-declared (default) rule, not a hard-coded one (D6 as
  designed). The same clarification is recorded in the PDR DDR amendments. (Approver ≠
  requester is enforced in the verify walk — a code-lane fact, recorded in the PDR DDR
  amendments only, no requirement-text change.)
- **Why:** the release semantics could be misread as "ready implies every object reviewed";
  D6 makes `all_active_reviewed` config-declared, so a config that omits it may be `ready`
  with unreviewed objects — the residual is stated, not hidden.
- **Evidence:** `config.py` `_DEFAULT_RELEASE_RULES` (config-declared, not hard-coded);
  PDR §D D6; PDR DDR amendments; `01-requirements.md` HLR-RH.7.

### LED-2026-10-11-reqharness-batch.36 — ruling: the parse cache STAT FAST PATH (LLR-RH.5.4 budget miss)

- **Requirement:** LLR-RH.5.4 (this entry is named in the requirement's Ledger line)
- **Date:** 2026-10-11
- **What changed:** the review parse cache (`mapper/reqharness/cache.py`, R4 /
  LLR-RH.5.3) gains a STAT FAST PATH by orchestrator ruling (unit PERF-RH):
  review/pending event files are immutable and content-named (the sha8 in the
  name is recomputed at read), so a warm load reuses the validated parse when
  `(relative name, st_size, st_mtime_ns, st_ino, st_dev)` ALL match a cache
  entry that previously PASSED the full check (sha256 of bytes == entry digest
  AND name sha8 check AND schema) — WITHOUT reading the file.  Any mismatch (or
  a missing stat field) falls through to the full path (read, hash, validate,
  then the entry's stat tuple is refreshed); cache entries record the stat
  tuple in the persisted store (format v2: `{"v": 2, "docs": {sha: doc},
  "stat": {name: [stat, sha]}}`; a v1/foreign file is bounded to a rebuild, as
  R26 already promises for corrupt files).  A fast-path hit is still
  re-validated on CPU (typed schema + R22 name check — no I/O); a hit that
  fails is dropped via `bust_name` and re-parsed from the bytes, so a poisoned
  entry degrades to a re-parse, never a verdict change.  `--audit` keeps the
  cache OFF (full verification, unchanged); the `roles.yml`/`config.yml` loads
  are untouched.  Measured re-run of the P4 protocol (same synthetic
  generator, session temp, median of 3): warm-cache derive pipeline
  **0.4432 s median vs the ≤ 0.5 s budget — MET** (was 5.27 s; `load_reviews`
  warm 4.54 s → 0.40 s).  New layer-0 nodes: `tests/test_reqharness_cache_
  fastpath.py` (5 nodes: warm load reads no bytes; same-size/same-mtime/new-
  file-id change caught; changed size or mtime takes the full path; cache
  deleted → identical results; the residual pinned).
- **Residual (stated, test-pinned):** a local writer who can preserve
  size+mtime+file-id while changing bytes in place (possible on Windows: an
  in-place rewrite keeps the NTFS file index that `st_ino` reports) defeats
  the fast path — the stale validated parse is served without a read.  That
  writer can equally write `.git/reqharness-cache` itself (the same trust
  boundary as R4); `--audit` and release evaluation via audit are unaffected
  (the audit state is cache-OFF and re-reads every file).  Recorded in the
  PDR DDR amendments.
- **Why:** the P4 measurement (LED-…-batch.2's LLR-RH.5.4) missed the budget —
  5.27 s median vs ≤ 0.5 s, 4.54 s of it `load_reviews` re-reading and
  sha256-hashing 5 000 files on every warm load because the cache key WAS the
  hash of the bytes; derivation itself is ~50 ms.  Skipping the read+hash for
  unchanged files is the only route to the budget; the stat tuple (with the
  file id, not just name+size+mtime) is the strongest practical identity key,
  and its failure mode is bounded to the existing layer-3 trust answer.
- **Evidence:** `evidence/p4-timing.transcript` (re-measurement appended);
  `evidence/perf-rh-red.transcript` (RED proof: product reverted to HEAD → 3
  of 5 new nodes FAIL → restore byte-identical by sha256 → 5 passed);
  `tests/test_reqharness_cache_fastpath.py`; `04-validation.md` §P4
  re-measurement; PDR DDR amendments.
