# PLAN — mapper — Batch 2026-10-11-reqharness-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language.
> **Owed in.** `core` ✓ · `full` ✓
> Seeded by `/dev-flow-init` step 4 at both levels; the living plan is owed at every gate
> that follows (`/dev-flow` §Living plan is the rule's home).

> **Field guide:** `templates/guides/plan-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

The living compendium of this batch: where-we-are · objective · per-story/per-station status ·
roadmap + increment plan · key decisions · risks/watch-items · conventions honored ·
out-of-scope carries · test ledger · decision log (the human-readable mirror of `state.json`).
**Create at batch open and update at every gate and significant checkpoint** — the
orchestrator presents the full plan in-conversation at each phase gate.

## Header

| Field | Value |
|---|---|
| Project | mapper |
| Batch | 2026-10-11-reqharness-batch |
| Objective | ReqHarness (B-107): mapper becomes the harness for dev-flow's human-auditable artifacts. This batch delivers a coherent vertical slice: the headless domain core (`mapper/reqharness/` — config, hash-chained role log, registry with normative digests, derived review states, baselines, release rules, YAML I/O) + the roles screen (matrix variant B, prototype verdict B-123 already given) + a minimal read-only status surface (recommended folded into the roles screen chrome). Follow-up batches: review/signing screen and baseline/release view (prototype rounds first), US canon + AT → test-node extraction, generated views, dev-flow ledger proposal (D12). |
| Standing authorization | Quoted from `.dev-flow/state.json` `standing_authorization` (asked 2026-10-10/11): "ReqHarness decisions B-119/B-121/B-122/B-123 approved by the operator 2026-10-10/11; batch opened on their answer full + autónomo + merge" — mode `full + autonomous + merge (Recommended)`. Conditions: merge only after a final independent PR-level qa-reviewer pass over the whole diff comes back clean (a HIGH finding blocks regardless); TUI design changes need a prototype verdict first — the roles screen has one (B-123, variant B); every OTHER new screen goes back to the operator as a prototype round before implementation. Worker model per state.json: Kimi primary, DeepSeek for bounded units, Claude for reviews. |
| First gate | <owed at the first gate run — the orchestrator fills the exit code and the `V7` line> |
| Premises / RC-1 | No network in this unit, so `origin/main` could not be fetched; the batch's base is `state.json` `base_ref` = `fb1d4ce6118b57a540bd67bd2115e5400b356870` (close commit of `2026-10-10-perf-batch`). Premises the batch rests on: (1) the B-119/B-121/B-122 rulings and the B-123 prototype verdict stand as written in `.dev-flow/BACKLOG.md`; (2) the roles-screen prototype renders (`prototypes/roles_screen/`) are the accepted design source for variant B; (3) the requirement canon `REQUIREMENTS.md` (~190 rows) is the first registry population candidate in a later batch — this batch ships the empty-but-usable mechanism, not the populated canon. |

## Triggers

The trigger evaluation `state.json`'s `triggers.record` points at: one row per trigger evaluated, fired or not.

| Id | Verdict | Probe output |
|---|---|---|
| A1 | fired | New package `mapper/reqharness/` is not on disk at intake (`ls mapper/reqharness` → No such file or directory). The ARQ amendment (§2 `reqharness` row + §3 dependency rows) is owed before P1 per the staleness rule; the PDR §2 proposes the rows, the trunk writes them at ARQ. |
| A2 | fired | ≥2 modules touched: new `reqharness` + `screens` (roles.py) + `app` (audit branch + re-export) + `keymap` (the `roles` scope — a declared-seat edit owned by exactly one increment, RH5, the data-safety Inc-1 precedent). |
| A3 | fired | Interfaces other modules consume change: the new core surface is consumed by `screens`/`app`; `app.main()` gains the `--audit` branch; the seat's scope set grows (read by every screen through `bindings_for`/`textual_bindings`). No `docs/ARCHITECTURE.md` §4 frozen row is touched (PDR §4). |
| A4 | not fired | No parallel increments: one lane, RH1–RH6 sequential (PDR §8 declared empty; the four C-52 conditions answered there). |
| B1 | fired | Reverse census at P1: the symbols this batch adds (`reqharness.*`, `RolesScreen`, the `roles` scope) are asserted by no existing test file — `grep -rl` over `tests/` matches only this batch's not-yet-created files. New screen modules follow the F4 rule. |
| B2 | not fired | No file moves: every touched product file is new; no rename, no relocated module (`grep` of the batch's file set against the read-globs finds no old path). |
| B3 | not fired | No byte-identical-golden source touched: the batch's file set is disjoint from every source `tests/goldens/**` captures. |
| B4 | not fired | No artifact another component consumes: `reqharness/` files are read only by this batch's own core, screen, and CLI; nothing outside the batch reads the format this batch writes. |
| C1 (auth) | fired | The batch builds an identity/authorization mechanism: role-approval rules (admin-only, no self-approval), reviewer identity from git `user.name`/`user.email`, the release block on a signer without the role in force. Spoofing limits stated honestly in LLR-RH.4.4 (git identity is self-claimed; file + chain can be rewritten together by any committer — strong mode is the named follow-up). |
| C2 (secrets) | not fired | No secrets handling: the new files hold people, roles, digests, and review metadata only. |
| C3 (external integration) | not fired | No external integration: no network; the only subprocess is a read-only `git rev-parse HEAD` (the `mapper/diff.py` precedent). |
| C4 (sensitive/trust surface) | fired | New versioned files at the connected-repo root (`reqharness/`) that the release rule reads. What trusts them: the release evaluation and the roles screen only. What crosses the workspace boundary: nothing — local files only. Who can write them: any committer; the chain proves *approved* role changes, not file provenance. |
| C5 (destructive DB) | not fired | No database touched: the SQLite store is untouched by the batch; `reqharness/` is YAML files only. |
| C6 (input surface) | fired | New parsed inputs: `config.yml`, `roles.yml`, `reviews/*.yml`, `baselines/*.yml`, and the `--audit <repo>` argument. All parsing is `yaml.safe_load` only; every path is confined to the repo root (`resolve()` + prefix check; escaping symlinks refused); malformed input degrades to named validation errors or a broken-chain state, never silent acceptance. |
| C7 (network exposure) | not fired | Nothing listens, connects, or fetches: local files only. |
| C8 (markup over file-derived text) | fired | File-derived names/ids/roles/notes are painted in the roles screen; LLR-RH.8.4 coerces every one through `darkside.plain` before painting (the `github` module precedent). |
| D1 | fired | New user-visible surface: the roles screen — prototype verdict B-123 (variant B) already given, so no prototype round is owed. The status surface is folded into the roles screen footer band (ruling O2), so no second screen class is born. Review/signing and baseline/release views are follow-up batches with prototype rounds first. |
| D2 | not fired | The prototype was built in the target technology — `prototypes/roles_screen/proto.py` runs on the real Textual 8.2.8 stack (`run_test` + `save_screenshot`), not a mock-up; no re-prototype owed. |
| E1 | fired | ≥3 stories / ≥3 planned increments: US-RH-001…003 and increments RH1–RH6. |
| E2 | fired | High risk declared at intake: identity spoofing + the new trust surface are declared risks (`spike/intake.md` §Risks, carried into PLAN.md §Risks). |
| E3 | not fired | No client deliverable and no regulated context: an internal tooling batch. |
| F1 | fired | Flow currency: the local flow hash differs from the manifest (C-45 PULL) — stated next to the RC-1 line at intake; no network in this unit, so the flow could not be refreshed. |
| F2 | not fired | The backlog IS refreshed: B-119/B-121/B-122 (2026-10-10) and B-123 (2026-10-11) were recorded before this batch opened. |

_Alignment: this table mirrors `state.json` `triggers` (`evaluated_at` 2026-10-11T00:59:14; fired A1·A2·A3·B1·C1·C4·C6·C8·D1·E1·E2·F1; not fired A4·B2·B3·B4·C2·C3·C5·C7·D2·E3·F2)._

## Where we are

P1 iteration 1 complete (unit RH2, worker Kimi): the round-1 review is recorded in `02-review.md`
(three independent read-only reviewers — architect Claude Opus, qa-reviewer Claude Sonnet, security
reviewer Claude Opus; verdict `iterate-to-refine`, security BLOCK-UNTIL F1–F3), and the orchestrator's
rulings R1–R14 + D13 are applied to the design proposal (`design/design-proposal.md`), the live
contract (`01-requirements.md`), the ledger (entries `.3`…`.17`, one per ruling) and this PLAN.
No product or test change was made.

P1 iteration 2 complete (units RH3/RH3B, worker Kimi): the round-2 review is recorded in
`02-review.md` (architect `iterate` text-only — A1–A3 high; qa-reviewer + security-reviewer
`approve-with-conditions`), and the orchestrator's rulings R15–R26 are applied to the same
documents (ledger entries `.18`…`.29`, one per ruling) and this PLAN. The weight assessment
deferred three items with backlog rows: B-124 (committer-vs-reviewer email warning), B-125
(baseline `reactivated` + review-state progression), B-126 (fork-recovery UI); increment 6
splits into 6a/6b (R25). No product or test change was made. Owed next: the P1 gate re-run
over the round-2-amended contract + PDR.

P1 iteration 3 complete (unit RH4, worker Kimi): the round-3 targeted review is recorded in
`02-review.md` (all three read-only reviewers `approve-with-conditions`, no HIGH), and the
orchestrator's ruling R27 (seven limbs, one ledger entry `.30`) is applied to the live contract
(`01-requirements.md` — verify walks BY `prev_hash`, the git hardening R27a–R27d with the named
`no repo` result, the scope fix `roles_seq: int`, the named home-door tests), the ledger, the
design proposal and this PLAN; the PDR (`design/PDR-2026-10-11-reqharness-batch.md`) is filled
and sealed in the same unit: verdict `approved with conditions`, self-approved under the
standing authorization. No product or test change was made. Owed next: the P1 gate re-run over
the round-3-amended contract + sealed PDR.

## Objective

Restated from `state.json` `batch_objective` and BACKLOG B-107/B-119/B-121/B-122/B-123:
mapper becomes the harness for dev-flow's human-auditable artifacts. This batch
ships the vertical slice — headless domain core (`mapper/reqharness/`: config,
hash-chained admin-approved role log with genesis and tamper detection, persistent
versioned registry with normative-field digests and derived review states,
baselines + diff, release-rule evaluation, YAML as the only source of truth) plus
the roles screen (matrix variant B, already prototyped and accepted) plus a minimal
read-only status surface (recommended: folded into the roles screen chrome). The
batch is usable end to end: a team can create a registry, hold roles, and read the
release verdict — with nothing in it that later batches must redesign.

## Per-story / per-station status

| Story / station | Status | Notes |
|---|---|---|
| Station P0 (intake) | drafted | PLAN + `spike/intake.md`; no code |
| US-R / HLR-R canon | pending P1 | Dedup'd US-R1…R12 / HLR-R1…R14 live in the unified-gallery notes §4; P1 adopts the subset this slice covers |
| RH1 config + schema + canonical form | planned | ≤4 new source files; headless, stdlib + YAML + osopen; typed schema, canonical JSON, email_sha256 (rulings R3/R12) |
| RH2 chain | planned | genesis carrying `config_hash` (R15) · policy events binding the config (R1) · admin-only approval · no self-approval · head binding (R2) · fork exclusion + `resolve`-event recovery (R7/R16) · exact-format time schema (R18) · limits (R9) |
| RH3 identity reader + git allowlist + ARCH amendment | planned | `identity.py` (repo-local then global git config); the REDUCED, HARDENED read-only allowlist — no `git log` — + `osopen` edge amended into ARCH §1/§2/§3 HERE as the first build act (R11/R19/R20) |
| RH4 reviews + pending stores + content-keyed cache + derived states | planned | immutable content-named review files + exclusive create + the loader's sha8 content check (R8/R22) · pending files + a/r resolution derivation (R6) · `.git/reqharness-cache/` parse cache (R4) · derived states under the R5 precedence |
| RH5 baselines + release rules + `--audit` (read-only) | planned | dirty flag + FIVE diff classes (R13/R24 — `reactivated` deferred, B-125) · hard-coded mandatory rules (R1/R5) · `--audit` cache-off, writes nothing (R4); AT-080/AT-081 subprocess nodes |
| RH6a roles screen + home seat | planned | variant B per B-123 · band detail (event count, head hash, viewer, pending) · pending by `space` · read-only tamper/fork state (R14) · keymap `roles` scope + home door + `screens/home.py` row — all owned here (AT-077a/b/c, AT-078, AT-079) |
| RH6b admin a/r resolution | planned | split out of RH6 by R25 (the weight assessment) — `a`/`r` pending resolution (AT-082) |
| Review/signing screen | follow-up batch | prototype round first |
| Baseline/release view | follow-up batch | prototype round first |
| US canon + AT → test-node extraction (D2/D5/D7–D11) | follow-up batch | read-only dev-flow adapter pinned by template revision |
| Generated MD/HTML views | follow-up batch | generated, never a second source |
| D12 dev-flow ledger proposal | follow-up batch (O7) | a change proposed TO dev-flow |

## Roadmap + increment plan

The increments of the slice, RE-PLANNED per the round-1 `Increments` ruling (each ≤4 source files,
tests in the same increment; full capability/risk detail in `spike/intake.md` + PDR §8):

1. **RH1 — Config + schema + canonical form** — `mapper/reqharness/__init__.py`, `model.py`,
   `config.py`, `canonical.py` + `tests/test_reqharness_config.py` (typed schema, disjointness,
   genesis creation, canonical JSON + NFC, email_sha256; rulings R3/R12).
2. **RH2 — Chain** — `mapper/reqharness/chain.py` + `tests/test_reqharness_chain.py` (genesis
   carrying `config_hash` (R15), policy events binding the config, append + approval rules, head
   binding + non-decreasing exact-format time (R18), verify, fork exclusion + `resolve`-event
   recovery (R16), effective roles at a bound head (`<=` on `roles_seq`, M-CH5), input limits;
   R1/R2/R7/R9).
3. **RH3 — Identity reader + git allowlist + ARCH amendment** — `mapper/reqharness/identity.py` +
   `tests/test_reqharness_identity.py` + the `docs/ARCHITECTURE.md` §1/§2/§3 amendment written HERE
   as the increment's first build act (read-only allowlist reduced and hardened per R20 — no
   `git log`; `reqharness` module row naming `screens/roles.py`'s edge, the `osopen`
   inbound edge; R11/R19 — not claimed earlier).
4. **RH4 — Reviews + pending stores + content-keyed cache + derived states** —
   `mapper/reqharness/reviews.py`, `pending.py`, `derive.py`, `cache.py` +
   `tests/test_reqharness_registry.py` (content-named immutable review files with exclusive create,
   pending files + resolution derivation, normative/informative digests, derived states under the R5
   precedence, `.git/reqharness-cache/` parse cache; R4/R6/R8).
5. **RH5 — Baselines + release rules + `--audit` (read-only)** — `mapper/reqharness/baseline.py`,
   `release.py`, `audit.py` + the `app.main()` `--audit` branch (4 source files incl. the app.py
   one-line branch, ahead of the `app.py:328` stdout re-wrap) + `tests/test_reqharness_baseline.py`
   + `tests/test_reqharness_release.py` + AT-080/AT-081 subprocess nodes (dirty flag, FIVE diff
   classes — `reactivated` deferred, B-125, hard-coded mandatory rules, cache-off +
   writes-nothing; R1/R4/R13/R14/R24).
6. **RH6a — Roles screen + home seat** — `mapper/screens/roles.py`, the `mapper/keymap.py` seat edit,
   the `mapper/app.py` re-export + home wiring, and the `screens/home.py` door row (ALL owned here —
   M8 answered) + `tests/test_roles_screen.py` (AT-077a/b/c, AT-078, AT-079: matrix B, band detail,
   pending by `space`, read-only tamper/fork state, 118 AND 87 columns).
6b. **RH6b — Admin `a`/`r` resolution** — the pending-resolution keys land in the same screen module
   but gate separately (AT-082), split out of the old increment 6 by round-2 ruling R25 (the weight
   assessment). AT-083 (fork) keeps detection + exclusion on screen; recovery is core-only (R16),
   fork-recovery UI deferred (B-126).

Follow-up batches and their order: review/signing screen (prototype first) →
US canon + AT table (adapter spike) → baseline/release view (prototype first) →
generated views → dev-flow proposals (D12). Out entirely: D3 evidence capture
(gated on security-check-before-tools) and B-122 optional strong mode.

## Key decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-11 (P0) | Recommended slice = headless domain core + roles screen (variant B) + status surface folded into the roles chrome | Only combination that ships a usable vertical slice without a prototype round; everything else either needs a prototype (review/signing, baseline/release) or touches dev-flow (D12, D7/D9 proposals) |
| 2026-10-11 (P0) | `mapper/reqharness/` proposed as a headless module: stdlib + YAML only, zero mapper deps; `screens`/`app` may import it; no Textual | Matches the `views` headless precedent; keeps the core testable without an event loop and the ARCHITECTURE §3 row writable at ARQ |
| 2026-10-11 (P0) | Open questions O1–O9 (registry layout, log append format, genesis copy, admin edit path, removal glyph, D12 timing, registry root, baseline identity) held for the orchestrator | They shape file formats (RH2/RH3) and screen copy (RH5) — cheaper to rule at P0/P1 than to retrofit |
| 2026-10-11 (P1) | O1 registry layout — DERIVED registry: no `registry.yml`; objects derive from the canon (`REQUIREMENTS.md` HLR/LLR rows) + review events; only baselines persist the derivation | A parallel registry file would drift from the canon the first hand edit (the defect B-119 D1 exists to prevent); canon stays the single source (B-121 ruling 1) |
| 2026-10-11 (P1) | O2 status surface — folded into the roles screen footer band (chain status, pending counts, release verdict); no new screen class, no prototype round owed | The only combination that avoids a second prototype round; the band is where variant B already puts pending + chain status (B-123) |
| 2026-10-11 (P1) | O3 genesis copy — the first event paints verbatim as "genesis — declared at registry creation" (`approved_by: genesis`, `note: "declared at registry creation"`) | Operator ruling; closes the prototype's open wording question |
| 2026-10-11 (P1) | O4 append format — `roles.yml` is a YAML multi-document stream, one chain event per document (P0 ruling); merge-conflict risk accepted, operational one-owner mitigation; the merge-fork shape is a boundary fixture (M-CH4) | Ruled by the orchestrator at P0; a re-open needs a measured conflict rate |
| 2026-10-11 (P1) | O5 admin edit path — an admin's change to SOMEONE ELSE applies in ONE key: one chain event with `requested_by = approved_by = that admin`; a change to oneself or by a non-admin stays pending | Operator ruling; the chain records fast-path and two-key approvals identically, so the audit trail never distinguishes them |
| 2026-10-11 (P1) | O6 removal glyph — pending add ◐ · pending remove ◌ (both already in the darkside glyph vocabulary) | Operator ruling; variant B only modelled adds (◐) — removals needed a second pending glyph |
| 2026-10-11 (P1) | O7 D12 — written THIS batch as a 06-docs document at P6 (proposal TO dev-flow; adoption is outside this repo) | Operator ruling; the ledger derivation consumes this batch's derived states and release semantics (PDR §3.4) |
| 2026-10-11 (P1) | O8 registry root — `reqharness/` at the connected repo root; CLI `mapper --audit <repo>` (through the existing `mapper = "mapper.app:main"` console entry) | Operator ruling (gallery recommendation); no new entry point registered |
| 2026-10-11 (P1) | O9 baseline identity — baselines named + bound to the repo commit SHA (read-only `git rev-parse HEAD`), frozen under `reqharness/baselines/<name>.yml`; git tags stay a manual act | Operator ruling; baseline-vs-now and baseline-vs-baseline diff classify new / changed / retired / unchanged |
| 2026-10-11 (RH1B) | R-SCALE (scale spike folded): YAML loading via `yaml.CSafeLoader` when available, `yaml.SafeLoader` otherwise — never `yaml.load` with any other loader; review event files immutable (append-only event store); local git-ignored parse cache `.reqharness-cache/reviews.json` (name+size+mtime → parsed event, parsing only, pure accelerator — deleting it changes no result); warm-cache budget ≤ 0.5 s (median of 3) to derive 5 000 events / 2 000 requirements — a P4 measurement, not a suite wall-clock assertion; the cache's key/location were superseded by ruling R4 at P1 iteration 1 and it lands with the re-planned reviews+pending+cache increment (RH4; `cache.py`, ≤4 source files) | Orchestrator ruling on the corrected spike verdict (both 20 000-file cases timed out > 120 s; 5 000 files = 2.3 s/load; AV cold-scan ~60 s cold / ~9 s warm recorded as observation only); ledger LED-2026-10-11-reqharness-batch.2 |

| 2026-10-11 (P1 iter 1) | R1 — the config is bound by the chain: admin-approved `policy` events in `roles.yml` carry sha256(canonical config); a mismatch → `config changed without approval`, last approved policy in force, release blocked; three mandatory release rules hard-coded in the core (config may add, never remove) | Round-1 architect H1 + security F1 (block-until); ledger `.3` |
| 2026-10-11 (P1 iter 1) | R2 — head binding: every review event, pending request and baseline records `roles_seq` + `roles_hash`; verify fails on any recorded head not in the chain (truncation/rewrite detection); authority at the bound head, never wall-clock; `time` non-decreasing; residual: a consistent rewrite by a writer with repo access → B-122 layer 3 follow-up; genesis git anchoring follow-up | Round-1 security F2/F3 (block-until) + architect M1; ledger `.4` |
| 2026-10-11 (P1 iter 1) | R3 — strict canonical form: typed schema (all `str` except `seq: int`; unknown/missing keys rejected; writer quotes scalars), NFC, canonical JSON (sorted keys, no whitespace, ensure_ascii=False); normative digest = sha256 of the canonical JSON of `{field: value}` — never concatenation | Round-1 architect H2 (CSafeLoader coercion probe; `"ab"+"c"` ambiguity); ledger `.5` |
| 2026-10-11 (P1 iter 1) | R4 — the parse cache is keyed by sha256(file bytes) and lives INSIDE `.git/reqharness-cache/` (no `.git/info/exclude` write); deleting it changes no output; `--audit` runs cache-OFF and writes nothing (workspace digest unchanged) | Round-1 architect H3 + security F4 + qa QM2/QM3; supersedes the R-SCALE cache key/location; ledger `.6` |
| 2026-10-11 (P1 iter 1) | R5 — unentitled reviews count as `pre-reviewed`, flagged `unentitled`, never block alone; `not verifiable` reserved for chain/policy breaks + unknown heads; explicit precedence table (a newer pre-review never downgrades a qualifying human review on the same digest; stale-digest reviews never close); model reviews self-declared | Round-1 architect H4/M6 + qa QM7; ledger `.7` |
| 2026-10-11 (P1 iter 1) | R6 — pending requests: `reqharness/pending/<yyyymmdd>-<sha8>.yml`, one file per request; `a` approve / `r` reject (admin only, never one's own); resolution is a chain event referencing the request hash; the file stays (derived from the chain); survives restart; non-admin `a` → "a is unavailable (needs an admin)" | Round-1 architect H5 + qa QH1/QH2; AT-082 born; ledger `.8` |
| 2026-10-11 (P1 iter 1) | R7 — fork: two events with the same `prev` → BOTH children excluded from authority deterministically, reported `chain forked at seq N`; recovery = admin re-appends on the head (documented + tested) | Round-1 architect M2; AT-083 born; ledger `.9` |
| 2026-10-11 (P1 iter 1) | R8 — review/pending files named `<yyyymmdd>-<sha8 of canonical content>.yml`, exclusive create; confinement reuses `mapper.osopen.confine_reason`/`is_link` (the core's one inbound mapper edge); `..`/links/junctions refused | Round-1 architect M3/M5 + security F8; ledger `.10` |
| 2026-10-11 (P1 iter 1) | R9 — limits: ≤ 64 KB per review/pending file, ≤ 4 MB roles.yml, ≤ 100 000 review files; anchors/aliases + duplicate keys rejected; RecursionError/ValueError caught as in `store.py:706-720`; malformed/oversize reported by name | Round-1 security F6 + qa QM1; ledger `.11` |
| 2026-10-11 (P1 iter 1) | R10 — markup safety is the SINK: file-derived text paints only into `rich.text.Text(...)`/`Text.append` (never `Static(str)`, markup=True widgets, notify markup, help text); census enforced; the `plain()` sentence corrected | Round-1 security F5 + qa QH4 + architect LOW-c; ledger `.12` |
| 2026-10-11 (P1 iter 1) | R11 — git read-only allowlist amended into ARCH §1/§2/§3 in the identity increment (not claimed earlier): `rev-parse` (`--show-toplevel`, `HEAD`), `git config --get`, `status --porcelain`, `log --format=... -- reviews/<file>` (committer mismatch → audit WARNS, report only); identity repo-local then global; tests inject identity | Round-1 architect M4/LOW-a…d + security F7; ledger `.13` |
| 2026-10-11 (P1 iter 1) | R12 — config stores `email_sha256` (lowercased); display names in clear; git email matched by hash; personal-data note documented | Round-1 security F9; ledger `.14` |
| 2026-10-11 (P1 iter 1) | R13 — baselines record `dirty: true|false` (porcelain) and refuse nothing; diff classes: new · changed · unchanged · retired · deleted · reactivated; review-state progression stated | Round-1 architect M7 + qa QM6 + security F10; ledger `.15` |
| 2026-10-11 (P1 iter 1) | R14 — QA bundle: AT-080 → `test_at_080_*` (one object per state, exact counts, unentitled separate, informative mark); AT-077 split a/b/c; AT-082/AT-083 born; 118 AND 87 columns; genesis copy on screen; band detail; read-only tamper; token/glyph/yaml.load/English censuses; boundary catalog extended; numeric thresholds explicit; M-CH5 = `<`↔`<=` flip; M-AU1 timeout 60 s; home door 7→8 row | Round-1 qa QH3/QH4/QM1–QM11/QL1–QL5 + architect M8/LOW-a; ledger `.16` |
| 2026-10-11 (P1 iter 1) | D13 — the connected repo = the git work tree containing the workspace (`git rev-parse --show-toplevel`); `--audit <repo>` overrides; no repo → the screen says so and offers nothing | Round-1 architect M8 (repo-root limb); ledger `.17` |
| 2026-10-11 (P1 iter 1) | Increments re-planned (six, ≤4 source files each): config+schema+canonical · chain · identity+allowlist+ARCH amendment · reviews+pending+cache+derived states · baselines+release+`--audit` · roles screen+home seat (seat + `screens/home.py` owned by the screen increment) | Round-1 architect M8; PLAN §Roadmap; PDR §8 |
| 2026-10-11 (P1 iter 2) | R15 — genesis records `roles_hash: "GENESIS"` (no self-reference) + `config_hash` = sha256(canonical config at creation); `create_registry` is policy-bound from the first document; the live config compares against the newest verified policy-bearing event | Round-2 architect A1/A5; ledger `.18` |
| 2026-10-11 (P1 iter 2) | R16 — fork recovery is a `resolve` event (admin-approved, `prev_hash` = the chosen child, names the excluded sibling's hash); after a valid resolve the chain verifies again; recovery is a documented manual procedure — fork-recovery UI deferred (B-126) | Round-2 architect A2; ledger `.19` |
| 2026-10-11 (P1 iter 2) | R17 — old-head binding is a stated residual: `--audit` WARNS (non-blocking) when a review's bound head precedes a later revocation of its signer's role (core comparison, no git); layer 3 remains the strong answer | Round-2 architect A3; ledger `.20` |
| 2026-10-11 (P1 iter 2) | R18 — exact schema: all scalars `str` except `seq`/`roles_seq` int; every field isinstance-checked; `time` matches exactly `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`; non-decreasing time compares those strings | Round-2 architect A4; ledger `.21` |
| 2026-10-11 (P1 iter 2) | R19 — the `docs/ARCHITECTURE.md` amendment (module row, §3 rules, the git read-only crossing) lands as the first build act of the identity increment (RH3) — the module row is the increments' dependency contract, not a closing garnish | Round-2 architect A6; ledger `.22` |
| 2026-10-11 (P1 iter 2) | R20 — the git allowlist reduced and hardened: only `rev-parse --show-toplevel`/`HEAD`, `config --get user.name|user.email`, `status --porcelain --no-optional-locks`; argv list, `shell=False`, 10 s timeout, the hardened prefix, stripped env; the committer-vs-reviewer email warning is DEFERRED (B-124) | Round-2 security G1 + architect A7; ledger `.23` |
| 2026-10-11 (P1 iter 2) | R21 — a custom loader subclass on CSafeLoader/SafeLoader rejects anchors/aliases and duplicate keys at compose time; fixtures prove both; its speed cost is measured at P4 against the 0.5 s budget (trade-off stated) | Round-2 security/qa probes; ledger `.24` |
| 2026-10-11 (P1 iter 2) | R22 — the loader recomputes sha8 over the canonical content of every review/pending file; a name mismatch is reported by name and non-closing (M-FN2) | Round-2 security limb; ledger `.25` |
| 2026-10-11 (P1 iter 2) | R23 — residuals + privacy stated: deleted review detected only against a baseline that listed it; unbound-tail truncation verifies clean; `reviewer` is free text; old-head binding; layer 3. `email_sha256` = pseudonymised personal data (unsalted, dictionary-reversible); jurisdiction to the operator | Round-2 security review; ledger `.26` |
| 2026-10-11 (P1 iter 2) | R24 — baselines trimmed to five diff classes (new · changed · unchanged · retired · deleted) + the `dirty` flag; `reactivated` + review-state progression DEFERRED (B-125); mutants M-BL3/M-BL4 | Round-2 weight assessment + qa MED-2; ledger `.27` |
| 2026-10-11 (P1 iter 2) | R25 — increment 6 splits: 6a = roles screen (matrix + home seat + band + pending by `space`: AT-077a/b/c, AT-078, AT-079); 6b = admin `a`/`r` resolution (AT-082); AT-083 keeps detection + exclusion on screen, recovery core-only | Round-2 weight assessment; ledger `.28` |
| 2026-10-11 (P1 iter 2) | R26 — QA items: exact nodes + fixtures for syntax-malformed YAML in each of the four file kinds, a corrupted review file at derive time, a corrupt cache file; M-CH5 = correct `<=` on `roles_seq`, mutant `<`; M-AU1 = `subprocess.run(timeout=60)` + `TimeoutExpired` = FAIL; the door-count checklist names the existing home tests; the 87-column tampered-band arm is optional (marked) | Round-2 qa MED-1/MED-2/LOW-1…4; ledger `.29` |
| 2026-10-11 (P1 iter 3) | R27 — round-3 precision fixes: verify WALKS BY `prev_hash` from genesis (a document claiming an already-claimed parent is a fork sibling; a sibling survives only behind a `resolve` naming it in `resolve_excludes`; a multi-event excluded branch → `chain broken`, recovery deferred B-126; a `resolve` is valid only when the chosen child passes the approval rule at its own bound head); `--audit` runs NO `git status` (dirty flag is `Baseline.create`-only; residual "baseline creation trusts the repo's `.git/config`"); the git prefix pins `-c core.fsmonitor=false -c core.hooksPath=<os.devnull>`; `git` is resolved ONCE to an absolute path (`NoDefaultCurrentDirectoryInExePath=1`, explicit PATH excluding the repo) and invoked `<abs git> -C <repo>`; a `safe.directory` refusal or any git non-zero → the named result `no repo`, never a crash; the scope line reads `seq`/`roles_seq: int`; the door-count checklist names the guarded home tests (six ids). New tests ×3, new mutants M-FR3/M-FR4/M-AU3/M-ID2 | Round-3 architect A-MED/A-LOW-1/A-LOW-2 + qa LOW-3 + security H1–H4 (all approve-with-conditions, no HIGH); ledger `.30`; PDR sealed in the same unit |
| 2026-10-11 (CLOSE3) | Operator directive — remove the operator's name, handle, personal paths and employer/client names from all projects; placeholders `username_subject`/`<owner>`/`<org>` | Operator directive issued 2026-10-11 and executed by scrub commits `9ec5814`, `ef644cb`, `3a177c2`; recorded as increment 011 (CLOSE3 record-only) and carried as the Traces-to of that packet's scrub rows |

## Risks / watch-items

- Layer-3 residual (round-1 ruling R2, stated not fixed): a writer with full repo access can rewrite the chain, every review, and every recorded head CONSISTENTLY, defeating every mechanism this batch ships — likelihood: inherent for sha256-without-signatures · mitigation: NONE in this batch; stated in LLR-RH.4.4 and the PDR §2.1 threat model; B-122 strong mode (signed commits / CODEOWNERS / branch protection) and git anchoring of genesis are the named follow-ups.
- Identity spoofing — likelihood: inherent · mitigation: state the limit honestly (git identity is self-claimed; anyone with commit access can write a review file naming someone else); reviews are re-checked at derive/release time (nothing is "authorized at write time" — there is no review write API this batch); the committer-vs-reviewer email warning is DEFERRED (B-124 — round-2 ruling R20 removed `git log` from the allowlist); B-122 strong mode is the named upgrade, out of scope.
- Old-head binding (round-2 ruling R17, stated residual) — a revoked reviewer can bind a NEW review to an older head where they still held the role · mitigation: `--audit` WARNS (non-blocking) when a review's bound head precedes a later revocation of its signer's role (a core comparison over the chain, no git); layer 3 remains the strong answer.
- Other round-2 residuals (ruling R23, stated in the PDR threat model): a deleted review is detected only against a baseline that listed it; truncation of tail events no review or baseline has bound yet verifies clean; `reviewer` is free text; `email_sha256` is pseudonymised personal data (unsalted, dictionary-reversible) — the jurisdiction question goes to the operator.
- YAML merge conflicts on the append-only role log in parallel PRs — likelihood: medium once the registry is in use · mitigation: ruling R7/R16 — a merge fork degrades to a DETERMINISTIC exclusion of both children (`chain forked at seq N`), never silent authority; the only legal continuation is a `resolve` event (admin-approved, core-tested); recovery stays a documented manual procedure — fork-recovery UI deferred (B-126); O4's format ruling stands.
- Performance on large canons — likelihood: low this batch (~190-row canon), real in the US-canon batch · mitigation: ruling R-SCALE + R4 + R21 — the custom loader subclass on CSafeLoader (compose-time anchor/duplicate rejection at some speed cost, measured at P4 against the 0.5 s budget — the trade-off is stated there), immutable review events + the content-keyed cache in `.git/reqharness-cache/` (cold cost once per new file), and the LLR-RH.5.4 warm-cache budget (≤ 0.5 s median of 3 for 5 000 events / 2 000 requirements, measured at P4, not asserted in the suite); no full-canon recompute API; D11 depth cap already bounds review depth.
- Git inside an untrusted repo (round-2 ruling R20) — a repo's `core.fsmonitor` can execute code on `git status`, and a plain `git status` refreshes `.git/index`, breaking "audit writes nothing" · mitigation: the hardened allowlist — argv list, `shell=False`, 10 s timeout, the `git --no-pager -c core.fsmonitor= -c core.hooksPath=<platform null>` prefix, `GIT_OPTIONAL_LOCKS=0`, inherited `GIT_DIR`/`GIT_WORK_TREE`/`GIT_CONFIG*` stripped — pinned by the sentinel-absent, `.git/index`-byte-identical and argv-census fixtures.
- sha8 is 32 bits (round-2 architect LOW) — a name/content collision is possible · mitigation: accepted by construction — exclusive create turns a collision into an ERROR, never a silent overwrite (R8); stated, not hidden.
- Antivirus cold-scan on first read — likelihood: high on this Windows machine for freshly written files (spike observation: ~60 s cold / ~9 s warm for a 20 000-file read) · mitigation: the parse cache pays the cold cost once per new file; no suite wall-clock assertion depends on cold reads.
- Parse-cache poisoning — likelihood: low · mitigation: bounded by construction (R4): the key is the file's sha256 (read + hash, skip the parse), the cache lives inside `.git/` (never tracked, no exclude write), it stores parsing only, and deleting it changes no result (a test asserts equal outputs with and without — LLR-RH.5.3, mutation M-RG5).
- Module-map drift — likelihood: low if sequenced · the ARCH §1/§2/§3 amendment (module row, hardened git allowlist without `git log`, `osopen` edge, `screens` row naming `roles.py`) is written as the first build act of the identity increment per R11/R19/R20, not claimed earlier; the staleness rule is satisfied because the amendment lands before the increments that rely on it are validated.
- Screen-copy/census drift — likelihood: low · guarded by the R14 censuses: token oracle (monkeypatched darkside token changes the paint), hex/glyph source census, painting-sink census, English-only oracle (LLR-RH.8.5, AT-077c).
- Scope creep toward rev3's full artifact chain (EV attachments, trace guards, gap detector) — the rulings (B-119 D1, B-121) subsume the direction but this batch's slice is config+roles+registry+release only; rev3 extras are follow-up batch material.

## Conventions honored

- All UI strings in English (operator ruling 2026-09-29); colours read from `mapper/darkside.py` tokens, glyphs/keys from `mapper/keymap.py` — never hard-coded.
- No operator path or Windows account name in any tracked file (guard A-110); external sources cited by neutral label ("Codex+Kimi plan rev3, 2026-09-11").
- Screens land as one module per screen with `KEY_SCOPE` + `BINDINGS` generated from the keymap seat; the seat is edited by exactly one increment.
- Tests drive the app with `MapperApp(tmp_path)` + `run_test` + real `pilot.press`; RED proof (revert → FAIL → byte-identical restore via sha256 → GREEN) per increment.
- pytest run from the worktree root with `-p no:cacheprovider`, single test files only.

## Out-of-scope carries

- Review/signing screen and baseline/release view — follow-up batches, each with a prototype round first (standing authorization condition).
- US canon + AT → test-node extraction, dev-flow read-only adapter (D5), graduated edge (D2), (batch,id) keys (D7), tolerant `(retired)` parser (D9), owner enum (D10), depth cap (D11) — follow-up batch; adapter spike on template revision detection owed first.
- Generated MD/HTML views — follow-up batch (generated, never a second source).
- D12 dev-flow ledger derivation + D7/D9 structured-field proposals — documents proposed TO dev-flow (O7 decides if the write-up happens this batch or later).
- D3 evidence capture `e` — out; later, gated on the security-check-before-tools skill and an allowlist.
- B-122 optional strong mode (CODEOWNERS + branch protection + signed commits) — out; the honest identity-spoofing statement travels in the requirements instead.
- Round-2 deferrals (marked, not deleted): B-124 committer-vs-reviewer email warning (one `git log --name-only` pass) · B-125 baseline `reactivated` class + review-state progression · B-126 fork-recovery UI.
- rev3 phase-2 items (term harmonisation, OOXML bindings, attachments) — not part of the operator's rulings.

## Test ledger

| Suite / command | Last run | Result |
|---|---|---|
| none — P0 intake unit (docs only, no product/test change) | 2026-10-11 | n/a; first ledger entries owed at RH1 |
