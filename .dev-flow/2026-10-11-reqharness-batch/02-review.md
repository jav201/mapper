# Review — mapper — Batch 2026-10-11-reqharness-batch

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`).
> Phase 2 artifact. Reviewers (in parallel): `architect` ∥ `qa-reviewer` ∥ `security-reviewer` by trigger family C (always in `full`).

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/guides/review-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

## ✅ Verdict (read first)

- **Gate:**
  - **Round 1** → `iterate-to-refine` → Phase 1. The security reviewer returned ITERATE with
    **BLOCK-UNTIL F1–F3** (config outside the chain; tail truncation verifies clean; self-declared
    time → backdating); the architect returned `iterate` on both artifacts (5 high, 8 major, 4 low);
    the qa-reviewer returned `iterate` on REQ / `approve-with-conditions` on the PDR (4 high,
    15 medium, 8 low). The orchestrator ruled R1–R14 plus the re-planned increments and the
    repo-root ruling D13 (`RH-rulings-r1.md`, held in the orchestrator's temp area, not committed).
  - Round 2 is owed next over the amended contract + PDR.
  - **Round 2** → `iterate-to-refine` (text-only) → Phase 1. The architect returned `iterate`
    (3 high, 4 med, low + probes); the qa-reviewer returned `approve-with-conditions` (2 med,
    4 low); the security reviewer returned `approve-with-conditions` (G1 + conditions). The
    orchestrator ruled R15–R26 (`RH-rulings-r2.md`, held in the orchestrator's temp area, not
    committed), applied at P1 iteration 2 (units RH3/RH3B, ledger `.18`…`.29`). Deferred with
    backlog rows: B-124 (committer-vs-reviewer email warning), B-125 (baseline `reactivated` +
    review-state progression), B-126 (fork-recovery UI).
- **Out-of-scope findings:** none routed to backlog this round; two residual risks are stated in
  the design's threat model instead (full consistent rewrite by a writer with repo access →
  B-122 layer 3, follow-up; git anchoring of genesis, follow-up).

- **Findings (round 1):** 3 blocker (security F1–F3, block-until) · 9 high · 23 major · 12 low
  (47 total across the three reviewers). All three reviewers were read-only; the architect and
  the security reviewer ran executed probes (CSafeLoader scalar coercion; field-boundary
  concatenation ambiguity; cache key behaviour).
- **shall/should check:** ✓ clean (round 1) — `shall` appears in Statements only; no modal
  `should` inside any HLR/LLR statement. Ruling R14 re-checked the numeric thresholds
  (exit-code-0 is not a threshold; every threshold is now a count, byte-exact string, or
  measured budget).
- **Two-layer (blockers):** ✗ in round 1, fixed by the rulings:
  - US-RH-002 had no genuine black-box AT — AT-080 asserted only report sections + exit code
    and was misnamed `test_audit_cli_on_seeded_repo` (qa H3) → **R14** re-specifies AT-080 with
    one object per state and exact per-state counts; **AT-082/AT-083** born for pending
    resolution and fork recovery (qa H2).
  - The token/glyph census and the "never yaml.load" claim had no oracle (qa H4) → **R10/R14**
    give both a source census + executed loader tests.
  - Negative controls and boundary rows were incomplete (qa MED) → **R14** extends the boundary
    catalog and pins a reddening mutation per control.
- **Census (change-first):** best-effort by the architect (merge-order fork shapes, pending
  storage gaps, subprocess surfaces); ⚠ the "no existing test breaks" claim stays unproven
  until the P3 full-suite gate — not claimed anywhere (architect LOW carried into R14/R11).
- **Security:** ⚠ 10 findings (F1–F10), F1–F3 block-until; all answered by R1–R13.
- **Evidence checklists (architect / qa / security):** summarized below from the reviewers'
  transcriptions (`RH-rulings-r1.md`).

---

## Detail (reference)

Reviewer ids follow the orchestrator's transcription of the round-1 review
(`RH-rulings-r1.md`, held in the orchestrator's temp area, not committed): the architect
numbered its findings H1–H5 (high), M1–M8 (major), LOW (four items); the qa-reviewer numbered
its H1–H4 (high), MED (fifteen items), LOW (eight items); the security reviewer numbered
F1–F10. All three were independent and read-only.

### Findings — round 1

| ID | Reviewer | Severity | Area / Req | What | Recommendation / ruling | Status |
|----|----------|----------|------------|------|------------------------|--------|
| H1 | architect | high | HLR-RH.1/2, config | `config.yml` (classes, normative fields, release rules, people→roles) sits OUTSIDE the chain: a hand edit to the policy itself verifies clean and takes effect. | **R1** — config is bound by admin-approved `policy` events in `roles.yml` carrying sha256(canonical config); mismatch → `config changed without approval`, last approved policy stays in force; the three mandatory release rules are hard-coded in the core. | applied (P1 iter 1, ledger .3) |
| H2 | architect | high | §3.2 hash algorithm | "Canonical hashing" breaks on real YAML: CSafeLoader coerces `2026-10-11T09:00:00Z`→datetime, `no`/`on`→bool, empty→None (json.dumps then fails); and `sha256("ab"+"c") == sha256("a"+"bc")` — a field-boundary ambiguity. | **R2+R3** — typed schema (all fields `str` except `seq: int`; writer quotes scalars; unknown/missing keys rejected), NFC normalisation, and canonical serialisation = JSON sorted keys / no whitespace / ensure_ascii=False; the normative digest is sha256 of the canonical JSON of `{field: value}` — never concatenation. | applied (ledger .4/.5) |
| H3 | architect | high | LLR-RH.5.3, cache | The cache is keyed name+size+mtime: an mtime-preserving rewrite (coarse mtime on Drive/FAT) reuses a stale parse and CAN change a verdict; the "integrity" claim is false. | **R4** — cache keyed by sha256(file bytes) inside `.git/reqharness-cache/` (local, never tracked, no `.git/info/exclude` write); `--audit` runs cache-OFF and writes nothing; deleting the cache changes no output (tested). | applied (ledger .6) |
| H4 | architect | high | HLR-RH.4/5, release | One unentitled review blocks every release forever, and `signers_in_force` is tautological (a closing review qualified by definition). | **R5** — an unentitled review counts as `pre-reviewed`, flagged `unentitled`, never blocks by itself; `not verifiable` is reserved for chain/policy breaks and unknown heads; precedence table explicit; the mandatory rules become chain verified · policy verified · closing reviews signed by a role in force at the bound head. | applied (ledger .7) |
| H5 | architect | high | HLR-RH.2, pending | Pending requests have no home: nothing persists them, nothing resolves them, restart loses them. | **R6** — `reqharness/pending/<yyyymmdd>-<sha8>.yml`, one file per request; the roles screen resolves with `a`/`r` (admin only, never one's own); the resolution is a chain event referencing the request hash; the file is not deleted (resolution derived from the chain); survives restart. | applied (ledger .8) |
| M1 | architect | major | chain `time` | `time` is self-asserted by the event author — backdating is free. | **R2** — authority is evaluated at the bound head (`roles_seq`), NOT wall-clock; chain `time` must be non-decreasing. (Backdating within the chain remains possible for a committer — see F3 residual, threat model layer 3.) | applied (ledger .4) |
| M2 | architect | major | HLR-RH.3, fork | The fork outcome depends on merge order (a 3-way merge can resolve silently), and there is no recovery procedure. | **R7** — two events with the same `prev` → BOTH children excluded from authority, deterministically; reported `chain forked at seq N`; recovery = admin re-appends the intended change on the head (documented + tested). | applied (ledger .9) |
| M3 | architect | major | review file names | Names like `0001-hlr-rh-1.yml` collide across branches and reveal nothing about content. | **R8** — review and pending files named `<yyyymmdd>-<sha8 of canonical content>.yml`, exclusive create. | applied (ledger .10) |
| M4 | architect | major | subprocess, ARCH §1 | Contradiction: identity needs `git config`, but ARCH §1 bans git-CLI crossings except `diff`; the cache + `.git/info/exclude` writes contradict "writes only under reqharness/"; `--audit` in CI must write nothing. | **R4** (cache moves inside `.git/`, no exclude write) + **R11** (git read-only allowlist amended into ARCH §1/§2/§3 in the increment that creates the module; identity = repo-local then global `git config`; tests inject identity). | applied (ledger .6/.13) |
| M5 | architect | major | path confinement | Path containment reinvents its own rule instead of reusing the sanctioned one. | **R8** — `reqharness/` confinement reuses `mapper.osopen.confine_reason` / `is_link` (stdlib-only import; ARCH §3 amended); `..`, links and junctions refused. | applied (ledger .10) |
| M6 | architect | major | HLR-RH.5, precedence | State precedence is ambiguous: can a newer pre-review downgrade a qualifying human review? Can a stale-digest review close? | **R5** — precedence table: a newer pre-review never downgrades a qualifying human review on the same digest; any review on a stale digest does not close. | applied (ledger .7) |
| M7 | architect | major | HLR-RH.6, baselines | Baselines ignore the dirty tree (a SHA pinned on uncommitted work claims too much), deleted canon ids are unclassified, retired→active is unnamed. | **R13** — record `dirty: true|false` from `git status --porcelain`, refuse nothing; classes become new · changed · unchanged · retired · deleted · reactivated; review-state progression stated. | applied (ledger .15) |
| M8 | architect | major | increments, PLAN | RH5 also edits `screens/home.py`; the band is built in RH6 but asserted in RH5; no increment owns the identity reader or the pending store; repo-root discovery for RolesScreen is unspecified (`MapperApp(workspace)` is a maps dir). | **Increments ruling + D13** — six re-planned increments (config+schema+canonical; chain+policy+head binding+fork; identity reader+git allowlist+ARCH amendment; reviews+pending+cache+derived states; baselines+release+`--audit`; roles screen+home seat incl. `screens/home.py`); the connected repo = the git work tree containing the workspace, discovered with `git rev-parse --show-toplevel`; no repo → the screen says so and offers nothing. | applied (ledger .17; PLAN §Key decisions) |
| LOW-a | architect | low | `--audit`, app.py | `--audit` output must survive the UTF-8 stdout re-wrap at `app.py:328`. | **R11/R14** — the audit branch prints and exits before the TUI path; the branch sits ahead of the re-wrap (asserted by AT-080's subprocess node). | applied |
| LOW-b | architect | low | ARCH §2 screens row | Only `screens/roles.py` gains the reqharness edge — the ARCH `screens` row must name it. | **R11** — the ARCH amendment plan names `screens` → `reqharness` with `roles.py` as the edge; written in the identity/ARQ increment, not claimed earlier. | applied |
| LOW-c | architect | low | §2.1 C1 wording | "Review events are authorized at WRITE time" is false — there is no review write API this batch. | **R11** — sentence corrected: reviews are re-checked at release/derive time; nothing is authorized at write time this batch. | applied |
| LOW-d | architect | low | REQ §2.8 row 4 | Row 4 claims an ARQ amendment that is not in `docs/ARCHITECTURE.md`. | **R11** — §2.8 row 4 reworded: the amendment is OWED in the increment that creates the module (staleness rule), not claimed as present. | applied |
| QH1 | qa-reviewer | high | HLR-RH.2, pending | Pending storage undefined; no restart arm; resolution undefined. | **R6** (pending file store + `a`/`r` + restart arm in AT-082). | applied (ledger .8) |
| QH2 | qa-reviewer | high | HLR-RH.8 | No approve/reject keys or AT for pending resolution. | **R6+R14** — `a` approve / `r` reject, admin only, never one's own; AT-082 born. | applied (ledger .8/.16) |
| QH3 | qa-reviewer | high | US-RH-002, AT-080 | US-RH-002 has no real black-box AT: AT-080 asserts only sections + exit code and is misnamed `test_audit_cli_on_seeded_repo`. | **R14** — AT-080 renamed `test_at_080_*`: one object per state, exact per-state counts, pre-reviews and unentitled counted separately, the informative-edit mark, numeric exit-code thresholds. | applied (ledger .16) |
| QH4 | qa-reviewer | high | AT-077, census | The token/glyph census and "never yaml.load" have no oracle. | **R10/R14** — token oracle = monkeypatch the darkside token, assert the paint changes + a source census for hex/glyph literals in `screens/roles.py`; "never yaml.load" source census + fallback-loader test (LLR-RH.1.1, LLR-RH.8.5). | applied (ledger .5/.12/.16) |
| QM1 | qa-reviewer | med | boundary catalog | Missing: deleted/corrupted review file, malformed YAML (roles.yml, review, pending, config), large registry cold vs warm equality, LLR-RH.1.1 disjointness untested. | **R9/R14** — all four added to the boundary catalogs with fixtures (LLR-RH.1.1 disjointness arm, LLR-RH.3.5 limits, LLR-RH.5.3 cache equality). | applied (ledger .11/.16) |
| QM2 | qa-reviewer | med | cache identity | "Cache identity" — what makes a cached parse THE parse of that file is unstated. | **R4** — the key is sha256(file bytes): identity by content. | applied (ledger .6) |
| QM3 | qa-reviewer | med | `--audit` side effects | Audit CLI side effects unbounded (writes, cache). | **R4** — `--audit` runs cache-off and writes nothing; the workspace digest is unchanged (tested). | applied (ledger .6) |
| QM4 | qa-reviewer | med | canon row | An unparseable canon row is silently skipped. | **R14** — a canon row the reader cannot parse is REPORTED (named line), never silently skipped (LLR-RH.5.1 boundary). | applied (ledger .16) |
| QM5 | qa-reviewer | med | withdrawn marker | The withdrawn marker is undefined. | **R14** — canon status starting with `withdrawn` → `retired` (LLR-RH.5.1). | applied (ledger .16) |
| QM6 | qa-reviewer | med | deleted canon id | A canon id present in a baseline but deleted from the canon is unclassified. | **R13/R14** — the `deleted` class (LLR-RH.6.2). | applied (ledger .15/.16) |
| QM7 | qa-reviewer | med | state semantics | State semantics gaps around precedence and unentitled counting. | **R5/R14** — precedence table + separate unentitled count (LLR-RH.5.1, AT-080). | applied (ledger .7/.16) |
| QM8 | qa-reviewer | med | prototype B divergence | The tampered state must make the matrix read-only (space inert); the band shows event count + head + viewer + pending detail; AT-078's viewer identity is unspecified; only 118 cols tested. | **R14** — all folded into AT-077b/AT-078/AT-079 + LLR-RH.8.1/8.2/8.3: viewer identity pinned by fixture, sizes 118 AND 87. | applied (ledger .16) |
| QM9 | qa-reviewer | med | genesis copy | The genesis copy `genesis — declared at registry creation` is asserted only in a core test. | **R14** — genesis copy asserted on screen in AT-077a. | applied (ledger .16) |
| QM10 | qa-reviewer | med | AT-077 | AT-077 is a triple job (open/paint + band + markup). | **R14** — AT-077 split: `test_at_077a` (open + matrix + genesis copy), `test_at_077b` (band detail), `test_at_077c` (markup/plain + painting sinks + English-only census). | applied (ledger .16) |
| QM11 | qa-reviewer | med | LLR-RH.7.2 | The escaping-path node is named but not in the executed verification. | **R14** — `tests/test_reqharness_release.py::test_audit_cli_refuses_escaping_repo_path` named in LLR-RH.7.2. | applied (ledger .10/.16) |
| QL1 | qa-reviewer | low | thresholds | "exit code 0" is not a numeric threshold. | **R14** — numeric thresholds explicit everywhere (counts, byte-exact strings, measured budget). | applied (ledger .16) |
| QL2 | qa-reviewer | low | M-CH5 | M-CH5 misses the `<` vs `<=` flip. | **R14** — M-CH5 defined as the boundary flip (`<` ↔ `<=`) at the event-time comparison (LLR-RH.2.3). | applied (ledger .16) |
| QL3 | qa-reviewer | low | M-AU1 | The subprocess timeout value is unstated. | **R14** — subprocess timeout 60 s (LLR-RH.7.2, M-AU1). | applied (ledger .16) |
| QL4 | qa-reviewer | low | home doors | The home door count 7→8 regression has no row. | **R14** — LLR-RH.8.1 asserts the door list grows by exactly one (`R roles`); the count is fixture-pinned. | applied (ledger .16) |
| QL5 | qa-reviewer | low | English-only oracle | "English copy" has no oracle. | **R14** — a source census of user-visible strings in `screens/roles.py` for non-ASCII letters except the glyph set (LLR-RH.8.5). | applied (ledger .16) |
| F1 | security-reviewer | blocker | HLR-RH.1 | `config.yml` outside the chain holds the policy — the highest-value file is the least protected. | **R1** — policy events bind the config by sha256(canonical config); mismatch blocks release with `config changed without approval`. | applied (ledger .3) |
| F2 | security-reviewer | blocker | chain verify | Tail truncation — and a full rewrite from genesis — verifies clean. | **R2** — every review event, pending request and baseline records the chain head (`roles_seq` + `roles_hash`); verify fails if any recorded head is not in the current chain. | applied (ledger .4) |
| F3 | security-reviewer | blocker | chain `time` | Time is self-declared → backdating of grants/reviews. | **R2** — authority at the bound head, non-decreasing `time`; residual stated (a writer with repo access can still rewrite chain + every review consistently → layer 3, B-122 follow-up). | applied (ledger .4) |
| F4 | security-reviewer | high | cache | The cache claim (integrity follows from name+size+mtime) is false. | **R4** — content-keyed cache; integrity follows from the content key; the claim is reworded. | applied (ledger .6) |
| F5 | security-reviewer | high | C8, painting | `plain()` does not escape markup — the safety comes from painting into `rich.text.Text`, not from `plain()`. | **R10** — file-derived text reaches the screen only through `Text(...)`/`Text.append` sinks; a census enforces it; the `plain()` sentence corrected. | applied (ledger .12) |
| F6 | security-reviewer | high | input limits | No size/depth/count limits; YAML anchors/aliases and duplicate keys are accepted. | **R9** — ≤ 64 KB review/pending, ≤ 4 MB roles.yml, ≤ 100 000 review files; anchors/aliases and duplicate keys rejected; deep-nesting errors caught as in `mapper/store.py:706-720`; malformed/oversize reported by name. | applied (ledger .11) |
| F7 | security-reviewer | high | reviewer binding | A review file's signer is not bound to the committer who committed it. | **R11** — `--audit` reads `git log --format=... -- reqharness/reviews/<file>` and WARNS on committer-email mismatch (report only). | applied (ledger .13) |
| F8 | security-reviewer | high | file names | File names derived from caller input; no exclusive create; link/junction traversal possible. | **R8** — names derived from canonical content only; exclusive create (O_EXCL); links/junctions refused via `osopen.is_link`. | applied (ledger .10) |
| F9 | security-reviewer | high | PII | Emails in config are personal data. | **R12** — config stores `email_sha256` (sha256 of the lowercased email); display names in clear; the git email is matched by hash; a personal-data note is documented. | applied (ledger .14) |
| F10 | security-reviewer | high | deleted review | Deleting a review file is undetected. | **R2/R14** — baselines record the review set; a baseline-vs-now comparison reports `deleted` for vanished ids (LLR-RH.6.2); unknown recorded heads → `not verifiable`. | applied (ledger .4/.15) |

### Orchestrator rulings R1–R14 (round 1 → P1 iteration 1)

| Ruling | Answers findings | Disposition |
|--------|------------------|-------------|
| R1 — policy in the chain: `config.yml` is bound by admin-approved `policy` events in `roles.yml` carrying sha256(canonical config); a mismatch → `config changed without approval`, the last approved policy stays in force, release blocked. Mandatory, non-configurable release rules hard-coded in the core (chain verified · policy verified · every closing review signed by a role in force at its bound head); config can ADD rules, never remove these. | H1, F1 | applied (`LED-….3`; HLR-RH.1/2/7, LLR-RH.2.4, LLR-RH.7.1) |
| R2 — head binding: every review event, pending request and baseline records the roles-chain head (`roles_seq` + `roles_hash`); verify fails if any recorded head is not in the current chain (detects tail truncation and genesis rewrites). Authority is evaluated at the bound head (seq), NOT wall-clock; chain `time` non-decreasing; a review bound to an unknown head → `not verifiable`. Residual risk stated: a writer with repo access can rewrite chain + every review consistently — B-122 layer 3 (signed commits) is the follow-up; git anchoring of genesis is a follow-up too. | H2 (with R3), M1, F2, F3, F10 (with R13) | applied (`.4`) |
| R3 — strict canonical form: typed schema for every file (all fields `str` except `seq: int`; unknown keys and missing keys rejected; the writer always quotes scalars), Unicode NFC normalisation; canonical serialisation for hashing = JSON sorted keys, no whitespace, ensure_ascii=False, after NFC; the normative digest = sha256 of that canonical JSON of `{field: normalised value}` (whitespace collapsed, Markdown cell unescaped) — never concatenation. | H2 | applied (`.5`) |
| R4 — cache by content: the parse cache is keyed by sha256(file bytes) (read + hash, skip the parse) and lives INSIDE `.git/reqharness-cache/` (local, never tracked, no `.git/info/exclude` write); deleting it changes no output (tested); `--audit` runs with the cache OFF and writes nothing anywhere (workspace digest unchanged, tested). Integrity follows from the content key — the claim is reworded. | H3, M4 (cache limb), F4, QM2, QM3 | applied (`.6`) |
| R5 — unentitled review: a review whose signer did not hold the designated role at its bound head counts as `pre-reviewed`, flagged `unentitled`, and never blocks the release by itself; `not verifiable` is reserved for chain/policy breaks and unknown heads. Model reviews (`kind: model`, self-declared — the design says so) are pre-review only. Precedence: a newer pre-review never downgrades a qualifying human review on the same digest; any review on a stale digest does not close. | H4, M6, QM7 | applied (`.7`) |
| R6 — pending requests: `reqharness/pending/<yyyymmdd>-<sha8>.yml`, one file per request (requested by, change, bound head). The roles screen resolves them: `a` approve / `r` reject (admin only; never one's own); the resolution is a chain event referencing the request hash; a resolved request is derived from the chain (the file is not deleted). Survives restart (AT arm closes and reopens the app). A non-admin's `a` shows "a is unavailable (needs an admin)". | H5, QH1, QH2 | applied (`.8`) |
| R7 — fork: two events with the same `prev` → both children excluded from authority (deterministic on every clone), reported `chain forked at seq N`; recovery: an admin re-appends the intended change on top of the head (documented procedure + test). | M2 | applied (`.9`) |
| R8 — file names + paths: review and pending files named `<yyyymmdd>-<sha8 of canonical content>.yml`, written with exclusive create; `reqharness/` path confinement reuses `mapper.osopen.confine_reason` / `is_link` (reqharness may import osopen — stdlib-only; ARCH §3 amended); `..`, links and junctions refused. | M3, M5, F8, QM11 (escaping node) | applied (`.10`) |
| R9 — limits: ≤ 64 KB per review/pending file, ≤ 4 MB roles.yml, ≤ 100 000 review files; YAML anchors/aliases rejected; duplicate keys rejected; RecursionError/ValueError caught as in `mapper/store.py:706-720`; a malformed or oversize file is reported (named), never silently skipped. | F6, QM1 (limbs) | applied (`.11`) |
| R10 — painting: file-derived text reaches the screen only through `rich.text.Text(...)`/`Text.append` sinks (never `Static(str)`, markup=True widgets, notify markup, help text); a census test enforces it; the `plain()` sentence corrected (the safety is the Text sink; `plain()` preserves content). | F5, QH4 (token limb), LOW-c | applied (`.12`) |
| R11 — git read-only allowlist: amend `docs/ARCHITECTURE.md` (§1 crossings + §2 module row + §3 rules — written in the increment that creates the module, not claimed earlier): `mapper/reqharness/` may run read-only `git rev-parse`, `git config --get user.name|user.email`, `git status --porcelain` (dirty flag), `git log --format=... -- reqharness/reviews/<file>` (committer email of a review — `--audit` WARNS on mismatch, report only). Identity = repo-local then global `git config`; tests inject identity. | M4, F7, LOW-a/b/c/d | applied (`.13`) |
| R12 — emails: `config.yml` stores `email_sha256` (sha256 of the lowercased email), display names in clear; matching hashes the git email. A personal-data note is documented. | F9 | applied (`.14`) |
| R13 — baselines: record `dirty: true|false` (from `git status --porcelain`) and refuse nothing; the diff classes: new · changed · unchanged · retired · deleted · reactivated (retired→active); review-state progression (reviewed in base → still reviewed / changed · review / …). | M7, QM6, F10 (baseline limb) | applied (`.15`) |
| R14 — QA items: AT-080 renamed `test_at_080_*` with a fixture holding one object per state and exact counts per state, pre-reviews and unentitled counted separately, the informative-edit mark; token oracle = monkeypatch the darkside token and assert the paint changes + a source census for hex/glyph literals in `screens/roles.py`; "never yaml.load" source census + fallback-loader test; boundary catalog adds deleted/corrupted review file, malformed YAML (roles.yml, review, pending, config), large registry cold vs warm equality, canon unparseable row → reported line, withdrawn marker = canon status starting with `withdrawn`, deleted canon id → `deleted` class; the tampered state makes the matrix read-only (space inert, message); the band shows event count, head hash, viewer identity and pending detail as in prototype B; screen ATs at 118 AND 87 columns; genesis copy asserted on screen; AT-077 split by job (a/b/c); an escaping-path node; numeric thresholds explicit; M-CH5 = the `<`/`<=` flip mutation; M-AU1 subprocess timeout 60 s; home door-count regression listed; English-only oracle = a source census of user-visible strings in `screens/roles.py` for non-ASCII letters except the glyph set. | QH3, QH4, QM1, QM4–QM11, QL1–QL5, M8 (RH5/RH6 merge limb), LOW-a, QM8 | applied (`.16`) |
| D13 — repo root: the connected repo = the git work tree containing mapper's current workspace, discovered with `git rev-parse --show-toplevel`; `mapper --audit <repo>` overrides; no repo → the roles screen says so and offers nothing to edit. | M8 (repo-root limb) | applied (`.17`) |
| Increments (≤ 4 source files each, re-planned): (1) config + schema + canonical form; (2) chain (genesis, policy, append, verify, fork, head binding); (3) identity reader + git allowlist + ARCH amendment; (4) reviews + pending stores + content-keyed cache + derived states; (5) baselines + release rules + `--audit` (read-only); (6) roles screen (matrix B + band + a/r + read-only tamper) + home seat + `screens/home.py`. | M8 | applied (PLAN §Roadmap; design §8) |

### shall / should check
Clean (round 1): `shall` in Statements only; no modal `should` inside any HLR/LLR statement. The
round-1 amendments add no modal verb.

### Two-layer acceptance review (blockers)

| Story / Req | (a) AT present | (b) deliverable+method named | (c) both chains | (d) black-box pure | Status |
|-------------|----------------|------------------------------|-----------------|--------------------|--------|
| US-RH-001 / HLR-RH.2, HLR-RH.8 | yes | yes | yes | no in round 1 — pending storage/resolution had no AT and no keys (H5/QH1/QH2) | blocker → fixed by R6 (AT-082) |
| US-RH-002 / HLR-RH.4, HLR-RH.5 | yes | yes | yes | no in round 1 — AT-080 asserted sections + exit code only, misnamed (QH3) | blocker → fixed by R14 (AT-080 re-specified) |
| US-RH-003 / HLR-RH.6, HLR-RH.7 | yes | yes | yes | no in round 1 — same AT-080 weakness | blocker → fixed by R14 |

### Supersession census (change-first)
Best-effort by the architect over the round-1 spec: no frozen seam is touched by the rulings
(the keymap seat stays single-increment-owned; the ARCH amendment is a declared trunk act inside
the re-planned identity increment). Reservations: the "no existing test breaks" claim stays
unproven until the P3 full-suite gate — the requirements claim nothing there. The increment
gate must confirm the home door count row and the `screens/home.py` edit inside the roles-screen
increment (M8).

### Security review summary
Family C fired (C1 auth, C4 trust surface, C6 input surface, C8 markup over file-derived text).
The security reviewer returned ITERATE with BLOCK-UNTIL F1–F3; the rulings close F1–F10
(R1–R13). Two residuals are stated, not fixed: a writer with repo access can rewrite chain +
every review consistently (threat-model layer 3; B-122 signed commits is the follow-up), and
chain `time` remains self-declared within a verified chain (bounded by head binding: authority
is at the bound head, and non-decreasing time is verified). Guard A-110 (no operator paths /
account names in tracked files) is unaffected — the design stores emails only as hashes.

### Evidence checklists — architect · qa-reviewer · security-reviewer

**architect (round 1):**
- ✓ constraints stated (headless core, zero mapper deps, one screen, prototype verdict B-123);
- ✓ defects probed on temp workspaces (H2: CSafeLoader coercion probe `2026-10-11T09:00:00Z`→datetime,
  `no`/`on`→bool, empty→None, `json.dumps` failure; the `"ab"+"c" == "a"+"bc"` concatenation ambiguity);
- ✗ H1 config bypasses the chain (fixed by R1); ✗ H3 cache key can change a verdict (fixed by R4);
- ✗ H4 release blocked forever by one unentitled review (fixed by R5); ✗ H5 pending homeless (fixed by R6);
- ✓ placement respected ARCHITECTURE §3 except the M4 contradiction (fixed by R11);
- ✓ the re-planned increments are ≤ 4 source files each and give the identity reader and the
  pending store an owner (M8).

**qa-reviewer (round 1):**
- ✗ pending storage undefined, no restart arm (QH1 — fixed by R6); ✗ no approve/reject keys or AT (QH2 — fixed by R6/R14);
- ✗ AT-080 not a real black-box AT, misnamed (QH3 — fixed by R14); ✗ token/glyph census and
  "never yaml.load" without oracle (QH4 — fixed by R10/R14);
- ✗ boundary gaps: deleted/corrupted review file, malformed YAML across all four file kinds,
  cold-vs-warm equality, disjointness (QM1 — fixed by R9/R14);
- ✗ cache identity, audit side effects, unparseable canon row, withdrawn marker, deleted canon id,
  state precedence (QM2–QM7 — fixed by R4/R13/R14);
- ✗ prototype B divergences: read-only tamper state, band detail, viewer identity, 118-only sizing,
  genesis copy on screen, AT-077 triple job (QM8–QM10 — fixed by R14);
- ✗ escaping-path node, numeric thresholds, M-CH5 `<`/`<=`, M-AU1 timeout, home door regression,
  English-only oracle (QM11, QL1–QL5 — fixed by R14).

**security-reviewer (round 1):**
- ✗ F1 config outside the chain (fixed by R1); ✗ F2 tail truncation / genesis rewrite verifies clean
  (fixed by R2); ✗ F3 self-declared time → backdating (fixed by R2, residual stated);
- ✗ F4 cache claim false (fixed by R4); ✗ F5 `plain()` does not escape markup (fixed by R10);
- ✗ F6 no limits, aliases, duplicate keys (fixed by R9); ✗ F7 reviewer not bound to committer
  (fixed by R11 — warn-only); ✗ F8 names from content, O_EXCL, link/junction (fixed by R8);
- ✗ F9 emails are personal data (fixed by R12); ✗ F10 deleted review undetected (fixed by R2/R13).


---

## Round 2 (2026-10-11) — over the round-1-amended contract + PDR

Reviewer ids follow the orchestrator's transcription of the round-2 review
(`RH-rulings-r2.md`, held in the orchestrator's temp area, not committed): the architect
numbered its findings A1–A3 (high), A4–A7 (med), LOW (probe items); the qa-reviewer numbered
its MED-1/MED-2 and LOW-1…LOW-4; the security reviewer numbered G1 (with conditions). All
three were independent and read-only; the architect and the security reviewer ran executed
probes (YAML scalar coercion; CSafeLoader anchor/duplicate-key acceptance).

### Findings — round 2

| ID | Reviewer | Severity | Area / Req | What | Recommendation / ruling | Status |
|----|----------|----------|------------|------|------------------------|--------|
| A1 | architect | high | §3.2 genesis, LLR-RH.1.2 | Genesis hashes itself (`roles_hash` = own head — a circular binding) and a fresh registry has no policy event: a policy change could be "undone" by reverting to genesis — a new backdating hole. | **R15** — genesis records `roles_hash: "GENESIS"` (no self-reference) and carries `config_hash` = sha256(canonical config at creation); `create_registry` is policy-bound from the first document; M-CF1 arm (genesis without `config_hash` fails). | applied (P1 iter 2, ledger .18) |
| A2 | architect | high | §3.2 fork recovery, HLR-RH.3 | Fork recovery by "admin re-appends on the head" contradicts verify: after a fork the head is ambiguous, and a re-appended event lands on a child the exclusion already rejected. | **R16** — the only legal continuation is a `resolve` event (admin-approved, `prev_hash` = the chosen child, naming the excluded sibling's hash); after a valid resolve the chain verifies again; recovery stays a documented manual procedure (fork-recovery UI deferred, B-126); M-FR1 redefined. | applied (ledger .19) |
| A3 | architect | high | LLR-RH.4.2, review binding | A revoked reviewer can bind a NEW review to an older head where they still held the role — bound-head role checking alone cannot see it (a new backdating hole). | **R17** — stated residual: `--audit` WARNS (non-blocking) when a review's bound head precedes a later revocation of its signer's role (a core comparison over the chain, no git); layer 3 remains the strong answer. | applied (ledger .20) |
| A4 | architect | med | §3.2 schema | `roles_seq` int contradicts "all fields str except seq"; time comparison needs one exact format. | **R18** — all scalars `str` except `seq`/`roles_seq` int; every field isinstance-checked; `time` matches exactly `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`; non-decreasing compares are string compares over that one format. | applied (ledger .21) |
| A5 | architect | med | HLR-RH.1/LLR-RH.2.4 | A fresh registry has no policy event — the live config is unbound until the first hand `policy` event (closed by R15's genesis `config_hash`). | **R15** (same ruling — the genesis limb). | applied (ledger .18) |
| A6 | architect | med | ARCH amendment | The `docs/ARCHITECTURE.md` amendment must land at increment 1 — the module row is the increments' dependency contract, not a closing garnish. | **R19** — the amendment (§1 crossings + §2 module row + §3 rules incl. the osopen inbound edge) is written inside increment 1. | applied (ledger .22) |
| A7 | architect | med | §3.6 allowlist | One `git log` pass per review file does not scale (a census showed the per-file subprocess cost). | **R20** — `git log` leaves the allowlist entirely; the committer-vs-reviewer email warning is deferred (B-124); the allowlist is reduced and hardened. | applied (ledger .23; deferred B-124) |
| LOW | architect | low | §3.3 naming, §3.5 loader | sha8 is 32 bits — exclusive create makes a collision an error, not a silent overwrite (accepted, stated). Probes: quoted values load as clean `str`, unquoted coerce; CSafeLoader silently accepts anchors/aliases and duplicate keys — rejecting them needs a custom loader subclass at some speed cost. | **R21 (+R8's exclusive create)** — the collision failure mode is accepted by construction; a CUSTOM LOADER SUBCLASS on CSafeLoader/SafeLoader rejects anchors/aliases and duplicate keys at compose time; fixtures prove both; the speed cost is measured at P4 against the 0.5 s budget (trade-off stated). | applied (ledger .24) |
| MED-1 | qa-reviewer | med | boundary catalog | Boundary items still without exact nodes + fixtures: a deleted/corrupted review file at derive time; syntax-malformed YAML for config/roles.yml/review/pending; a corrupt cache file. | **R26** — exact nodes + fixtures for all of them: each of the four file kinds refused by name; a corrupted review file derives no state (reported by name); a corrupt cache file is bounded to a re-parse/rebuild, never a verdict change. | applied (ledger .29) |
| MED-2 | qa-reviewer | med | AT-081 | The new diff classes are weakly controlled — no mutant pins `deleted` apart from `retired`, and the dirty flag has no mutant. | **R24/R26** — M-BL3 (`deleted` collapsed into `retired`) and M-BL4 (dirty flag forced) added; AT-081 re-specified over five mutations. | applied (ledger .27/.29) |
| LOW-1 | qa-reviewer | low | M-CH5 | Wording: the CORRECT code uses `<=`, the mutant flips it to `<`, and it must compare `roles_seq`, not event time. | **R26** — M-CH5 defined precisely: correct `<=` on `roles_seq`, mutant `<`; LLR-RH.2.3 wording corrected. | applied (ledger .29) |
| LOW-2 | qa-reviewer | low | M-AU1 | The M-AU1 control must state `subprocess.run(timeout=60)` and count `TimeoutExpired` as FAIL. | **R26** — M-AU1 defined: `--audit` ignored → TUI starts → `subprocess.run(timeout=60)` raises `TimeoutExpired`, counted as FAIL. | applied (ledger .29) |
| LOW-3 | qa-reviewer | low | home door regression | The door-count regression checklist must name the existing home tests it guards. | **R26** — LLR-RH.8.1's checklist names the existing home tests (door count +1). | applied (ledger .29) |
| LOW-4 | qa-reviewer | low | band at 87 cols | The tampered-band assertion at 87 columns may be optional — but only if marked. | **R26** — the 87-column tampered-band arm is marked OPTIONAL (not silently dropped). | applied (ledger .29) |
| G1 | security-reviewer | high | git inside an untrusted repo | A repo's `core.fsmonitor` can execute code on `git status`; and a plain `git status` refreshes `.git/index`, breaking "audit writes nothing". | **R20** — every git call: argv list, `shell=False`, 10 s timeout, prefix `git --no-pager -c core.fsmonitor= -c core.hooksPath=<platform null>`, env with `GIT_OPTIONAL_LOCKS=0` and inherited `GIT_DIR`/`GIT_WORK_TREE`/`GIT_CONFIG*` stripped; fixtures: a `core.fsmonitor` sentinel stays absent after `--audit`; `.git/index` byte-identical after `--audit`; a census of the exact argv shapes. | applied (ledger .23) |

### Orchestrator rulings R15–R26 (round 2 → P1 iteration 2)

| Ruling | Answers findings | Disposition |
|--------|------------------|-------------|
| R15 — genesis: `roles_hash: "GENESIS"` (no self-reference) + `config_hash` = sha256(canonical config at creation); `create_registry` is policy-bound from the first document; later policy changes are `policy` events; the live config compares against the newest verified policy-bearing event. | A1, A5 | applied (`LED-….18`; HLR-RH.1, LLR-RH.1.2/2.4) |
| R16 — fork: both children excluded; the only legal continuation is a `resolve` event (admin-approved, `prev_hash` = chosen child, names the excluded sibling's hash); after a valid resolve the chain verifies again; recovery is a DOCUMENTED manual procedure this batch (no UI automation — deferred, B-126); the core implements and tests `resolve`. | A2 | applied (`.19`; HLR-RH.3, LLR-RH.3.4) |
| R17 — old-head binding: stated residual; `--audit` WARNS when a review's bound head precedes a later revocation of its signer's role (core comparison, no git); layer 3 remains the strong answer. | A3 | applied (`.20`; LLR-RH.4.2) |
| R18 — schema: all scalars `str` except `seq`/`roles_seq` int; `time` exactly `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`; non-decreasing time compares those strings; isinstance on every field. | A4 | applied (`.21`; LLR-RH.1.1/1.3) |
| R19 — the `docs/ARCHITECTURE.md` amendment (module row, §3 rules: reqharness may import osopen and stdlib/PyYAML only; screens/roles.py may import reqharness; the git read-only crossing) lands IN increment 1. | A6 | applied (`.22`; LLR-RH.7.3) |
| R20 — the git allowlist, reduced and hardened: only `git rev-parse --show-toplevel` / `rev-parse HEAD`, `git config --get user.name|user.email`, `git status --porcelain --no-optional-locks`; argv list, `shell=False`, 10 s timeout, the hardened prefix and stripped env; the committer-vs-reviewer email warning is DEFERRED (B-124). | G1, A7 | applied (`.23`; LLR-RH.7.3; deferred B-124) |
| R21 — a custom loader subclass (on CSafeLoader when available) rejects anchors/aliases and duplicate keys at compose time; fixtures prove both; its cost is measured at P4 against the 0.5 s budget (trade-off stated). | LOW (probe) | applied (`.24`; LLR-RH.1.1) |
| R22 — the loader recomputes sha8 over the canonical content of every review/pending file; a name mismatch is reported by name and non-closing; M-FN2 skips the check → its node reddens. | security limb | applied (`.25`; LLR-RH.4.6) |
| R23 — residuals and privacy: the threat model lists a deleted review detected only against a baseline that listed it; truncation of unbound tail events verifies clean; `reviewer` is free text; old-head binding (R17); a consistent full rewrite (layer 3). `email_sha256` is pseudonymised personal data (unsalted, dictionary-reversible); the jurisdiction question goes to the operator. | security round 2 | applied (`.26`; LLR-RH.1.4/4.4, PDR §2.1) |
| R24 — baselines trimmed: new · changed · unchanged · retired · deleted plus the `dirty` flag; `reactivated` and review-state progression DEFERRED (B-125); mutants M-BL3 + M-BL4. | MED-2, weight | applied (`.27`; HLR-RH.6, LLR-RH.6.1/6.2; deferred B-125) |
| R25 — increment 6 splits: 6a = roles screen matrix + home seat + band + pending by `space` (AT-077a/b/c, AT-078, AT-079); 6b = admin `a`/`r` resolution (AT-082); AT-083 keeps detection + exclusion on screen, recovery core-only. | weight | applied (`.28`; HLR-RH.8, LLR-RH.8.1/8.6, PLAN) |
| R26 — QA items: exact nodes + fixtures for syntax-malformed YAML in each of the four file kinds, a corrupted review file at derive time, a corrupt cache file; M-CH5 = correct `<=` on `roles_seq`, mutant `<`; M-AU1 = `subprocess.run(timeout=60)` with `TimeoutExpired` counted as FAIL; the door-count checklist names the existing home tests; the tampered-band 87-column arm is optional (marked). | MED-1, LOW-1…LOW-4 | applied (`.29`; HLR-RH.2/7, LLR-RH.1.1/2.3/3.5/5.1/5.3/7.2/8.1/8.3) |

### Weight assessment (round 2)

Drifting heavy. **Kept this batch:** policy binding (R1/R15), head binding (R2), pending + `a`/`r`
(R6), the content-keyed cache (R4), email hashing (R12), input limits (R9). **Deferred with backlog
rows:** the committer-vs-reviewer email warning (F7/G2/A7 → **B-124**), fork-recovery automation
(**B-126**), the baseline `reactivated` class + review-state progression (**B-125**). **Split:**
increment 6 → 6a/6b (R25).

### Deferred at round 2 (marked, not deleted)

- Committer-vs-reviewer email warning — **deferred (B-124)** (R20 removed `git log` from the
  allowlist; the warning needs one `git log --name-only` pass).
- Baseline `reactivated` class + review-state progression — **deferred (B-125)** (R24 trimmed the
  diff classes; the ids stay in the glossary).
- Fork-recovery UI automation — **deferred (B-126)** (R16: recovery is a core `resolve` event plus
  a documented manual procedure).

### shall / should check (round 2)
Clean (round 2): the R15–R26 amendments add no modal verb; `shall` stays in Statements only, and
every new threshold is a count, a byte-exact string, or the P4 measured budget.

### Security review summary (round 2)
Family C fired again. The security reviewer returned `approve-with-conditions`; G1 (git inside an
untrusted repo) is answered by R20's hardened allowlist + the sentinel/`.git/index`-byte-identical
fixtures. Residuals are stated per R23 (baseline-bounded deletion detection, unbound-tail truncation,
free-text `reviewer`, old-head binding, layer 3) and the privacy note names `email_sha256`
pseudonymised, unsalted, dictionary-reversible — jurisdiction to the operator. Guard A-110 (no
operator paths / account names in tracked files) is unaffected.


---

## Round 3 (2026-10-11) — targeted, over the round-2-amended contract + PDR

All three reviewers were independent and read-only; all three returned
`approve-with-conditions` with **no HIGH findings**. The round was targeted at the
round-2 rulings' new surface: the verify/fork/resolve semantics (R16/R26), the R20 git
hardening, the R26 QA items (whose LOW-3 the round-2 record claimed applied but had not),
and the scope line.

### Findings — round 3

| ID | Reviewer | Severity | Area / Req | What | Recommendation / ruling | Status |
|----|----------|----------|------------|------|------------------------|--------|
| A-MED | architect (Claude Opus) | med | LLR-RH.3.1 + proposal §3.2 `verify` | Verify still says "recompute every link in order; duplicate `prev_hash` → broken from that document", which fails on the in-order chain parent, childA, childB, resolve (the resolve's `prev_hash` is the chosen child — already claimed). | **R27e** — specify verify as a WALK BY `prev_hash` from genesis, not file position; a document whose `prev_hash` matches an already-claimed parent is a fork sibling; a sibling is tolerated from authority only when a later valid `resolve` names it in `resolve_excludes`; state the multi-event excluded-branch case. | applied (ledger .30) |
| A-LOW-1 | architect (Claude Opus) | low | `01-requirements.md` §1.2 scope line 33 | The scope line says "all fields `str` except `seq: int`" and omits `roles_seq: int` (R18 made both int). | **R27f** — fix the scope line to `seq`/`roles_seq: int`. | applied (ledger .30) |
| A-LOW-2 | architect (Claude Opus) | low | LLR-RH.3.4 | A `resolve` could legitimate a fork child that was never itself approvable (e.g. self-approved, or approved by a non-admin at that child's bound head). | **R27e** — a `resolve` is valid only when the chosen child itself passes the approval rule at its own bound head; M-FR4 reddens it. | applied (ledger .30) |
| QA-LOW-3 | qa-reviewer (Claude Sonnet) | low | LLR-RH.8.1 | The round-2 ruling (R26) claimed the door-count regression checklist "names the existing home tests" — it names none. | **R27g** — name them from `grep -rln "door" tests/` + reading the home screen tests: the count assertion `tests/test_inc9c.py::test_inc9c_ux_f4_home_reads_its_labels_from_the_seat` (`len(doors) == 6`), the bar-paint `tests/test_inc9e.py::test_inc9e_l3_the_home_bar_paints_the_doors_first`, the strip under a re-keyed seat `tests/test_inc9f.py::test_inc9f_r3_cr_f3_home_keeps_its_letters_and_active_mark_under_a_rekeyed_seat`, the dispatch of every home door row `tests/test_key_dispatch.py::test_at_n03g_each_key_dispatches_its_own_advertised_action`, and the pinned-seat census `tests/test_inc9.py::test_cd25_the_pinned_entry_seat_is_not_vacuous` + `tests/test_inc9.py::test_cd25a_the_seat_diff_is_exactly_what_inc9_declares` (the 6 home door rows of `ENTRY_ROWS`). | applied (ledger .30) |
| S-H1 | security (Claude Opus) | med | LLR-RH.7.3 git hardening | `git status` can still run commands via `filter.<name>.clean` from the repo's own `.git/config` + a committed `.gitattributes` (no fixed `-c` disables arbitrary filter names); and inside an untrusted repo the audit's read-only surface is wider than needed. | **R27a/b** — `--audit` runs NO `git status` at all (the dirty flag is `Baseline.create`-only, in the operator's own repo; residual stated: "baseline creation trusts the repo's `.git/config`"); the prefix pins `core.fsmonitor=false` (a value, not an empty override) and `core.hooksPath=<os.devnull>`. | applied (ledger .30) |
| S-H2 | security (Claude Opus) | med | LLR-RH.7.3 git resolution | On Windows, `git` resolved bare can be picked up from the audited repo's cwd (a planted `git.exe`). | **R27c** — resolve `git` ONCE to an absolute path with `NoDefaultCurrentDirectoryInExePath=1` during resolution and `shutil.which` over an explicit PATH excluding the repo; invoke `<abs git> -C <repo>` (never `cwd=<repo>`); an argv-census arm asserts the absolute executable. | applied (ledger .30) |
| S-H3 | security (Claude Opus) | med | LLR-RH.7.3 hooks | `core.hooksPath` from the repo could redirect hooks. | **R27b** — the prefix carries `-c core.hooksPath=<os.devnull>`. | applied (ledger .30) |
| S-H4 | security (Claude Opus) | med | LLR-RH.7.3 / LLR-RH.7.2 | `include.path`/`includeIf` only READ config; `core.sshCommand`/`credential.helper`/`diff.external` are not invoked by these read-only commands; `core.pager` is covered by `--no-pager`; a `safe.directory` refusal must become a named "no repo" result, not a crash. | **R27d** — stated as verified limits in LLR-RH.7.3; a `safe.directory` refusal (or any git non-zero) → the named result `no repo` on screen + audit, never a crash, exercised by `test_safe_directory_refusal_is_named_no_repo_not_a_crash`. | applied (ledger .30) |

### Orchestrator ruling R27 (round 3 → P1 iteration 3, one ruling, seven limbs)

| Limb | Disposition |
|------|-------------|
| R27a — `--audit` runs NO `git status`; the dirty flag is taken only by `Baseline.create`, which runs in the operator's own repo; residual stated: "baseline creation trusts the repo's `.git/config`". | applied (`.30`; HLR-RH.6, LLR-RH.6.1, LLR-RH.7.2, LLR-RH.7.3, PDR §2.1, proposal §3.6) |
| R27b — the prefix uses `-c core.fsmonitor=false -c core.hooksPath=<os.devnull>` (a fixed value disables fsmonitor under any filter name; the hooks path is neutralised). | applied (`.30`; LLR-RH.7.3, proposal §3.6) |
| R27c — `git` is resolved ONCE to an absolute path with `NoDefaultCurrentDirectoryInExePath=1` set during resolution (and `shutil.which` with an explicit PATH that excludes the repo), invoked as `<abs git> -C <repo> …` (no `cwd=<repo>`); an argv-census arm asserts the absolute executable; M-ID2 reddens a relative/planted resolution. | applied (`.30`; LLR-RH.7.3, proposal §3.6) |
| R27d — a `safe.directory` refusal (or any git non-zero) → the named result `no repo` (screen + audit), never a crash, with `test_safe_directory_refusal_is_named_no_repo_not_a_crash`; M-AU3 reddens a raising path. | applied (`.30`; LLR-RH.7.2, LLR-RH.7.3, LLR-RH.8.1) |
| R27e — verify walks the chain BY `prev_hash` from genesis; a document whose `prev_hash` matches an already-claimed parent is a fork sibling; single-event forks only in this batch — a fork whose excluded branch has descendants → `chain broken` (multi-event branch recovery deferred to B-126); a `resolve` is valid only when the chosen child passes the approval rule at its own bound head; tests: `test_verify_walks_by_prev_hash_in_order_fork_resolve`, `test_resolve_naming_non_sibling_is_invalid`, `test_multi_event_excluded_branch_is_broken`; mutants M-FR3/M-FR4. | applied (`.30`; HLR-RH.3, LLR-RH.3.1/3.2/3.4, proposal §3.2) |
| R27f — the scope line reads `seq`/`roles_seq: int` (R18). | applied (`.30`; `01-requirements.md` §1.2) |
| R27g — the door-count regression checklist names the existing home tests (the six ids of finding QA-LOW-3). | applied (`.30`; LLR-RH.8.1) |

### Round-3 notes

**Weight assessment (round 3).** Light. No new deferrals; B-124/B-125/B-126 stand. The
round-3 items are precision fixes to round-2 rulings (R20→R27a/b/c/d, R16/R26→R27e,
R18→R27f, R26→R27g) plus three new test arms and four new mutation ids (M-FR3, M-FR4,
M-AU3, M-ID2).

**shall / should check (round 3).** Clean: the R27 amendments add no modal verb outside
Statements; every new threshold is a count, a byte-exact string, or a named result word.

**Security review summary (round 3).** Family C fired again (C1/C4/C6/C8). The security
reviewer returned `approve-with-conditions` with the H1–H4 items above — all answered by
R27a–R27d; no HIGH. Residuals stated per R23 + R27a ("baseline creation trusts the
repo's `.git/config`"). Guard A-110 (no operator paths / account names in tracked files)
is unaffected.

**Verdict (round 3).** All three reviewers: `approve-with-conditions`, no HIGH. With R27
applied, the PDR is sealed in the same unit (see `design/PDR-2026-10-11-reqharness-batch.md`).
