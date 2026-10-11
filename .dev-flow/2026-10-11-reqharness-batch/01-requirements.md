# Requirements Document — mapper — Batch 2026-10-11-reqharness-batch

> **Artifact language**
> This template is the canonical **English scaffold**. Generate the artifact in the batch's development language (`state.json` `language`). For Spanish batches, translate the **prose** — section headers and guidance — **and never a label**, and use `deberá` as the normative keyword (≡ `shall`). The normative RULES in this preamble are **language-independent** and enforced regardless of artifact language.

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/guides/req-template.md` and its part 2, `templates/guides/req-template.part2.md`, explain each field below and the rules that read them. It ships with the flow and is not copied into this batch.

> **Reserved field names.** The **field names and block keywords below are language-independent** — the
> validator parses them literally and they are never translated:
> `Validation` · `Acceptance test(s)` · `Boundary catalog` · `Negative control` · `Premise evaluation` · `Fork preconditions` · `Ledger` · `Requirement` · `⏸ DEFER`
> Everything else on this page — headings, guidance, the prose in every cell — is translated with the batch.
> **One strategy, not two:** the flow ships no alias table, so a translated label is read as an ABSENT one and the rule keyed on it reports a true-sounding silence.
> **And one FLOW-WIDE reserved token, read out of this artifact by `V42` no matter which template minted it:** `⏸ DEFER`. It is a MARKER rather than a field name, which is why it is stated here *and* in `/dev-flow` §Language of artifacts rather than in a per-template list — a deferral can be written in any batch artifact, including the ones that carry no block at all.

---

## 1. Introduction

### 1.1 Purpose

Specify the requirements for the ReqHarness batch (`2026-10-11-reqharness-batch`): mapper becomes the
harness for dev-flow's human-auditable artifacts (backlog B-107; operator rulings B-119 D1, B-121, B-122;
prototype verdict B-123; orchestrator P0 rulings in `state.json` `decisions_log`, 2026-10-11; round-1
review rulings R1–R14 + D13 applied at P1 iteration 1, ledger `LED-2026-10-11-reqharness-batch.3`…`.17`).
This document is the live contract for the batch's vertical slice: the headless domain core
(`mapper/reqharness/`), the roles screen (matrix variant B), and the D12 proposal document.

### 1.2 Scope

**In scope.** (1) The headless package `mapper/reqharness/`: typed-schema configuration load/validate
with genesis creation (all fields `str` except `seq`/`roles_seq: int` — R18; unknown/missing keys rejected; the writer
always quotes scalars — R3); the hash-chained role log (YAML multi-document stream, one approved event
per document, admin-only approval, no self-approval, genesis declared once and carrying `config_hash`
= sha256(canonical config at creation) — a policy-bound registry from the first document, R15)
extended by admin-approved
`policy` events binding sha256(canonical config) (R1), by head binding on every event, review, pending
request and baseline (`roles_seq` + `roles_hash` — R2), and by deterministic fork exclusion with a
`resolve`-event recovery (R7/R16 — fork-recovery UI deferred, B-126); review events (one immutable YAML file per event under `reqharness/reviews/`,
named `<yyyymmdd>-<sha8 of canonical content>.yml` with exclusive create — R8, with the loader's
sha8 content check — R22, bound to the object's
normative digest AND the chain head, role-checked at the bound head, model reviews recorded as
self-declared pre-review); pending requests (one file per request under `reqharness/pending/`, resolved
by `a`/`r` into chain events referencing the request hash — R6); derived object states (`reviewed` ·
`changed · review` · `pre-reviewed` · `not reviewed` · `retired`, plus a visible `changed (informative)`
mark) under the explicit R5 precedence table; baselines (named + commit SHA + `dirty` flag under
`reqharness/baselines/`, diff two baselines or baseline-vs-now over five classes — R13/R24, `reactivated`
+ review-state progression deferred, B-125); release-rule
evaluation with the hard-coded mandatory rules and the `not ready · registry not verifiable` block; the
read-only `mapper --audit <repo>` CLI entry (cache OFF, writes nothing — R4); a content-keyed parse
cache inside `.git/reqharness-cache/` (R4); an identity reader over the read-only git allowlist
(R11); strict input limits (R9); YAML loading via `yaml.CSafeLoader` when available, `yaml.SafeLoader`
otherwise — never `yaml.load` with any other loader (ruling R-SCALE a + R21 — a custom loader
subclass rejects duplicate keys at construction time and anchors/aliases by an event-stream
pre-scan before construction; enforced by a source census +
fallback-loader test, R14). (2) The roles screen (`mapper/screens/roles.py`, matrix variant B) with the
status band in its footer, `a`/`r` pending resolution, and the read-only tampered/forked state,
reachable from home by one key. (3) The D12 proposal document (06-docs, P6).

**Objects of record: the HLR/LLR rows of `REQUIREMENTS.md` only.** The **US canon and the AT →
test-node table are FOLLOW-UP** (B-next-2: the dev-flow read-only adapter, D2 graduated edge, D7
(batch,id) keys, D8/D9 parsers, D10 owner enum, D11 depth cap — each with its own spike/pinning work).

**Out of scope.** Review/signing screen and baseline/release view (follow-up batches, prototype rounds
first); US canon + AT extraction; generated MD/HTML views; evidence capture `e` (D3); B-122 optional
strong mode (CODEOWNERS + branch protection + signed commits) — the layer-3 residual (a full consistent
rewrite by a writer with repo access) is stated honestly in LLR-RH.4.4 and the PDR threat model
instead; git anchoring of genesis (R2 follow-up); rev3 phase-2 items. **Deferred at round 2 (marked,
not deleted):** the committer-vs-reviewer email warning (**deferred, B-124** — R20 removed `git log`
from the allowlist); the baseline `reactivated` class + review-state progression (**deferred, B-125** —
R24); fork-recovery UI automation (**deferred, B-126** — R16: recovery is a core `resolve` event plus a
documented manual procedure).

### 1.3 Definitions, acronyms, abbreviations

| Term | Definition |
|------|------------|
| canon | The single source file an object's content lives in — for this batch, `REQUIREMENTS.md` (HLR/LLR rows). |
| chain event | One YAML document in `reqharness/roles.yml`: a genesis, policy, grant, revoke, resolution, or resolve event with requester, approver, hashes (R16 adds `resolve`). |
| genesis | The first chain event, declaring the first admin once, at registry creation; it records `roles_hash: "GENESIS"` (no self-reference) and `config_hash` = sha256(canonical config at creation), so the registry is policy-bound from the first document (R15). |
| policy event | An admin-approved chain event carrying `config_hash` = sha256(canonical config); binds the live config to the chain (R1). |
| head binding | The recording of the roles-chain head (`roles_seq` + `roles_hash`) an event, review, pending request or baseline was made against (R2). |
| bound head | The chain head recorded by head binding; authority is evaluated AT the bound head, never at wall-clock time. |
| `time` | A chain/review/pending time field; matches exactly `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`; non-decreasing comparisons are string compares over that one exact format (R18). |
| canonical JSON | `json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)` over NFC-normalised values (R3). |
| normative digest | sha256 of the canonical JSON of `{field: normalised value}` over the object's normative fields — never a concatenation (R3). |
| normative fields | The per-class field set whose change invalidates a review (config-declared; e.g. `statement`). |
| informative fields | Fields whose change leaves a visible `changed (informative)` mark without invalidating (e.g. `rationale`). |
| roles in force | The role set derived from the longest VERIFIED chain prefix at a given bound head. |
| pre-review | A review that never closes the state: a self-declared model review, or one whose signer held no reviewer role at its bound head. |
| unentitled | The flag on a pre-review whose signer held no designated role at its bound head (R5); reported and counted, never blocking alone. |
| pending request | A proposed role change (self-change or non-admin) held as one file under `reqharness/pending/`, resolvable by an admin with `a`/`r` (R6). |
| resolution event | A chain event (action `resolution`) referencing a pending request's sha256; the request's resolved state is derived from the chain (R6). |
| chain fork | Two events claiming the same `prev_hash`; BOTH children are excluded from authority, reported `chain forked at seq N` (R7); the only legal continuation is a `resolve` event (R16). |
| resolve event | An admin-approved chain event whose `prev_hash` is the chosen fork child and which names the excluded sibling's hash; after a valid resolve the chain verifies again (R16). |
| old-head binding | A stated residual (R17): a revoked reviewer binds a new review to an older head where they still held the role; `--audit` WARNS (a core comparison over the chain, no git). |
| email_sha256 | sha256 of the lowercased email — the only form in which config stores an email (R12). |
| registry (derived) | The in-memory object set derived from the canon + review events + chain; persisted only as baselines. |
| baseline | A named freeze of the derivation (objects, digests, states, chain head, review file set, commit SHA, dirty flag). |
| deleted / reactivated | Baseline diff classes: an id in the baseline but absent from the canon (`deleted`) (R13/R24). `reactivated` (retired → active) is **deferred (B-125)** — R24 trimmed this batch to five classes plus the `dirty` flag; review-state progression is deferred with it. |
| audit | The headless report over a repo's `reqharness/` state: chain status, derived states, release verdict — read-only, cache OFF. |

### 1.4 References

- `.dev-flow/BACKLOG.md`: B-107 (product direction), B-119 (gallery verdict, D1 registry ruling), B-121
  (review-registry mechanism), B-122 (roles mechanism + protection), B-123 (roles screen = matrix B).
- `design/design-proposal.md` (`PDR-2026-10-11-reqharness-batch`) — the ARQ design this contract cites
  per requirement (§2 modules, §2.1 threat model, §3.2 hash algorithm + policy/head binding, §3.3
  formats, §3.4 semantics + precedence, §3.5 performance, §3.6 identity allowlist, §5 test cases);
  round-1 rulings R1–R14 + D13 applied to both documents at P1 iteration 1 (unit RH2).
- `docs/ARCHITECTURE.md` §1/§2/§3 — amended with the `reqharness` module row, the hardened read-only
  git allowlist, and the `osopen` inbound edge in increment 1 (R11/R19/R20), not claimed earlier; the
  `screens` row names `roles.py` as the reqharness edge.
- `REQUIREMENTS.md` — the requirement canon whose HLR/LLR rows are this batch's objects of record.
- `spike/intake.md` (P0) · `spike/rhs-scale.md` (scale, corrected) · `prototypes/roles_screen/NOTES.md`
  (variant B, B-123 verdict) · Codex+Kimi plan rev3, 2026-09-11 (conceptual source, neutral label).
- Round-1 review record: `02-review.md` of this batch (rulings R1–R14 + D13, findings H/M/QM/F).

### 1.5 Document overview

§2 overall description (perspective, functions, users, constraints, assumptions, user stories, premise
evaluation, fork preconditions). §3 high-level requirements HLR-RH.1…9. §4 low-level requirements
LLR-RH.n.m + the IFC. §5 validation strategy. §6 appendices. §7 the ledger (separate file).

---

## 2. Overall description

### 2.1 Product perspective

ReqHarness sits beside the existing mapper: a new headless module (`mapper/reqharness/`, stdlib + PyYAML
only, zero outbound mapper deps except `mapper.osopen` for confinement — no Textual/Rich — the `views`
headless precedent, extended per R8) that reads and writes a `reqharness/` directory at the connected
repo's root, plus one new screen (`mapper/screens/roles.py`) that paints the role matrix and the status
band, and one CLI branch (`mapper --audit <repo>`) in `app.main()`. `screens` and `app` may import the
core; the core imports nothing in mapper except `mapper.osopen`. The connected repo is the git work
tree containing mapper's current workspace, discovered with `git rev-parse --show-toplevel` (D13);
`mapper --audit <repo>` overrides; no repo → the roles screen says so and offers nothing to edit. The
design commitments live in `PDR-2026-10-11-reqharness-batch`; this document is the requirement contract
on top of them.

### 2.2 Product functions

1. Create a registry: write `reqharness/config.yml` (people with `email_sha256`, roles, classes,
   normative fields, release rules) and `reqharness/roles.yml` with the single genesis event.
2. Hold roles as approved chain events; bind the config by admin-approved `policy` events (R1); apply
   an admin's change to someone else in one key; hold self-changes and non-admin proposals as pending
   files resolvable with `a`/`r` (R6); detect hand edits, policy mismatches, unknown bound heads and
   merge forks deterministically, keeping the last verified roles and last approved policy in force.
3. Record review events bound to normative digests and chain heads; derive per-object review states
   from the canon + reviews + chain under the R5 precedence table.
4. Freeze baselines (named + commit SHA + dirty flag) and diff them (two baselines, or baseline vs
   now: new / changed / retired / unchanged / deleted — R13/R24; `reactivated` deferred, B-125).
5. Evaluate release rules — the three hard-coded mandatory rules plus config-added rules — and report
   `ready` / `not ready · <reason>` through the core, the screen's status band, and the read-only
   `mapper --audit <repo>` CLI.
6. Paint the roles screen (matrix B) with the footer status band (event count, head hash, viewer
   identity, pending detail, chain status, verdict), `a`/`r` resolution, and a read-only tampered/
   forked state; driven by the keymap seat and darkside tokens.
7. Propose (document only) that dev-flow's 05-close human review ledger be derived from the registry (D12).

### 2.3 User characteristics

- **admin** — holds the `admin` role; the only role that approves chain events and resolves pending
  requests (never their own); uses the roles screen.
- **reviewer** — holds a class-designated reviewer role (e.g. `req-reviewer`); their review events close
  object states when made at a bound head where they held the role; one person may hold several roles.
- **board** — reads release readiness from the audit CLI / status band; needs no mapper interaction
  beyond reading.
- **model identities** (Claude/Kimi) — may record reviews; `kind: model` is self-declared and these are
  always pre-review, never closing a state (B-121 ruling 3; R5).

### 2.4 Constraints

- The core is headless: stdlib + PyYAML only; **no Textual, no Rich, no mapper imports except
  `mapper.osopen`** (confinement reuse — R8); the screen coerces file-derived strings through
  `darkside.plain` and paints only into `rich.text.Text(...)`/`Text.append` sinks (C8; R10).
- YAML loading exclusively through a CUSTOM LOADER SUBCLASS on `yaml.CSafeLoader` when available,
  falling back to `yaml.SafeLoader` — never `yaml.load` with any other loader (C6; ruling R-SCALE a +
  R21 — the subclass rejects duplicate keys at construction time and anchors/aliases by an
  event-stream pre-scan before construction; source census +
  fallback-loader test per R14; its speed cost is measured at P4 against the LLR-RH.5.4 budget).
- Every path under `reqharness/` is confined with the ONE containment rule — `mapper.osopen.confine_reason`
  / `is_link` (`..`, links and junctions refused — R8); the CLI argument `<repo>` is confined the same
  way before any file is read.
- Input limits (R9): ≤ 64 KB per review/pending file, ≤ 4 MB roles.yml, ≤ 100 000 review files;
  malformed or oversize files are reported BY NAME, never silently skipped; RecursionError/ValueError
  are caught as in `mapper/store.py:706-720`.
- No network, no OS-handler, no subprocess writes; the only subprocesses are the hardened read-only
  git allowlist (R11/R20/R27): `git rev-parse --show-toplevel` / `HEAD`, `git config --get
  user.name|user.email` (repo-local then global), and — only inside `Baseline.create` — `git status
  --porcelain --no-optional-locks` (`--audit` runs NO `git status`, R27a); every call an argv list
  with `shell=False`, a 10 s timeout, the `<abs git> --no-pager -c core.fsmonitor=false -c
  core.hooksPath=<os.devnull> -C <repo>` form — `git` resolved ONCE to an absolute path by walking
  PATH itself (the audited repo, the cwd, `.` and empty entries excluded — compared resolved; then
  `git` + each PATHEXT extension on Windows, fallback `.COM;.EXE;.BAT;.CMD`, first existing regular
  file wins) — never `shutil.which` (F4 HIGH: before Python 3.12 it searches `.` on Windows) (never
  `cwd=<repo>`, R27c) — `GIT_OPTIONAL_LOCKS=0`, and inherited
  `GIT_DIR`/`GIT_WORK_TREE`/`GIT_CONFIG*` stripped; a `safe.directory` refusal (or any git non-zero
  exit) becomes the named result `no repo`, never a crash (R27d); the committer-vs-reviewer email
  warning is **deferred (B-124)**.
- All UI strings in English (operator ruling 2026-09-29; source-census oracle per R14); colours from
  `mapper/darkside.py` tokens, glyphs/keys from the `mapper/keymap.py` seat — never hard-coded.
- Identity = repo-local then global `git config` (R11) — self-claimed and spoofable by any committer;
  stated honestly, never presented as authentication (C1 ceiling; strong mode is a named follow-up,
  out of scope; the layer-3 residual is stated in LLR-RH.4.4).
- One increment owns the keymap seat edit and the `screens/home.py` door row (the roles-screen
  increment); pytest runs from the worktree root with `-p no:cacheprovider`, single test files only.

### 2.5 Assumptions and dependencies

- PyYAML ≥ 6.0 is a declared runtime dependency (`pyproject.toml` `dependencies`) — no new dependency
  is added by this batch.
- The local `git` CLI is available for the read-only allowlist (the `diff` module precedent, extended
  per R11); tests inject identity via repo-local config.
- The `REQUIREMENTS.md` HLR/LLR table shape is stable within this batch; the tolerant canon adapter is
  follow-up (D5/D9). A row the minimal reader cannot parse is REPORTED by line (R14), never guessed
  and never silently skipped.
- The console entry `mapper = "mapper.app:main"` (`pyproject.toml` `[project.scripts]`) is the audit
  CLI's surface; no new entry point is registered; the `--audit` branch runs after the UTF-8 stdout
  re-wrap (so the report prints in UTF-8).

### 2.6 Source user stories

| ID | User Story | Source | DoR status |
|----|------------|--------|------------|
| US-RH-001 | As an admin, I want role changes to be approved chain events applied from the roles screen (one key for changes to others, pending for my own), the config bound by policy events, and pending requests resolvable with two keys, so that the team's authority is auditable, a hand edit can never silently grant a role or change the policy, and the audit trail keeps every request. | B-122 + B-123 + rulings R1/R6 (P0 rulings O3/O5/O6) | READY |
| US-RH-002 | As a reviewer, I want my review bound to the requirement's content digest and the chain head, checked against the roles in force at that head, so that an edited requirement visibly needs review again, a truncated or rewritten chain is detected, and a review I was not entitled to make never counts. | B-119 D1 + B-121 rulings 2–3 + rulings R2/R5 | READY |
| US-RH-003 | As a board member, I want a release verdict and baseline diffs derived from these artifacts, read through an audit CLI that writes nothing, so that release readiness is read from evidence, not asserted. | B-119 D1 + B-122 ruling 2 + rulings R4/R13 | READY |

#### Refinement log (one block per story)

**US-RH-001 — auditable roles**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = admin · outcome = role changes land as hash-chained approved events
  bound to heads; the config is bound by `policy` events; the matrix shows ● ◐ ◌ ○; a hand edit or
  policy mismatch shows `config changed without approval` with the last verified roles and last
  approved policy in force; pending requests persist as files and resolve with `a`/`r` into chain
  events · why = B-122's protection story + R1/R6 · out of scope = strong mode (CODEOWNERS/signed
  commits), the review/signing screen.
- **Feasibility (E, S):** implementation path = `reqharness/{config,canonical,chain,pending}.py` +
  `mapper/screens/roles.py` (variant B per B-123; prototype renders exist) · dependencies/unknowns =
  none — prototype verdict already given · fits one batch? = yes.
- **Evaluability (T) — behavioral, black-box:** "When I press `space` on a cell as an admin, the role
  lands; as a non-admin the same key shows a pending glyph and a file appears under `reqharness/pending/`;
  when I press `a` on it as another admin the resolution lands as a chain event; when the file is
  hand-edited the footer says the chain is broken and the old roles stay."
- **Open questions:** none (O3/O5/O6 ruled at P0; R1/R6 at round 1).
- **Classification:** `READY`.

**US-RH-002 — digest-bound review**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = reviewer · outcome = a review closes an object's state only while the
  normative digest matches, the recorded chain head exists, and the signer held the reviewer role at
  the bound head; model reviews and unentitled signers derive `pre-reviewed` (flagged, counted,
  never blocking alone); informative edits mark without invalidating · why = B-121 rulings 2–3 +
  R2/R5 · out of scope = evidence capture (D3), review/signing UI.
- **Feasibility (E, S):** implementation path = `reqharness/{reviews,derive,cache}.py` over the HLR/LLR
  canon · dependencies/unknowns = the minimal canon row reader (this batch; adapter is follow-up) ·
  fits one batch? = yes.
- **Evaluability (T):** "When the requirement's statement changes after my review, the object reads
  `changed · review`; when only its rationale changes, it stays `reviewed` with an informative mark;
  when the chain is truncated past my review's recorded head, the registry reads `not verifiable`."
- **Open questions:** none.
- **Classification:** `READY`.

**US-RH-003 — evidence-based release**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = board member · outcome = `mapper --audit <repo>` (and the screen's
  status band) report chain status, per-state counts (pre-reviews and unentitled counted separately),
  and `ready` / `not ready · <reason>`; baselines freeze the state + commit SHA + dirty flag and diff
  new / changed / retired / unchanged / deleted (`reactivated` + review-state progression deferred,
  B-125 — R24); the audit writes nothing and runs with the cache OFF · why = B-119 D1 + B-122 ruling 2 + R4/R13 · out of scope = the baseline/release VIEW
  (prototype owed), git tagging (manual, per P0 ruling O9).
- **Feasibility (E, S):** implementation path = `reqharness/{baseline,release,audit}.py` + the
  `app.main()` `--audit` branch · dependencies/unknowns = the read-only git allowlist (R11) · fits one
  batch? = yes.
- **Evaluability (T):** "When I run `mapper --audit .` on a repo with an unreviewed requirement, the
  verdict is `not ready · unreviewed requirements`, the exit code is 1, and every file in the repo
  hashes to the same digest after the run as before."
- **Open questions:** none (O9 ruled: baselines named + commit SHA under `reqharness/baselines/`, tags
  manual).

### 2.7 Premise evaluation (C-43) — MANDATORY, one row per premise

| # | Premise, as a truth-apt proposition | Tier | Verdict | Executed evidence (command output / `file:line` — **NOT** a citation of another document) | Disposition |
|---|---|---|---|---|---|
| 1 | PyYAML ≥ 6.0 is a runtime dependency of this project. | low | ✅ TRUE | `grep -n "pyyaml" pyproject.toml` → `pyyaml>=6.0,` inside `[project] dependencies` (lines 11–14). | relied on (core's only third-party dep) |
| 2 | The next free acceptance-test number after every existing AT is `AT-077`. | low | ✅ TRUE | `grep -ohE "AT-[0-9]+" REQUIREMENTS.md tests/*.py \| sort -u` → highest `AT-076` (in `tests/test_perf_*.py`); `REQUIREMENTS.md` tops out at `AT-069`. New ATs: `AT-077`…`AT-083` (AT-082/AT-083 born at P1 iteration 1 per R6/R7 + R14). `AT-077` is an umbrella id only, realised by its split jobs AT-077a · AT-077b · AT-077c — each of those drives a node on disk; the bare umbrella number is never itself a declared acceptance id. | relied on (AT numbering) |
| 3 | The chord `R` is free on the `home` scope of the keymap seat. | low | ✅ TRUE | Executed probe: home chords today `['c','enter','f','i','j','k','n','p','q','r','s','t']`; `duplicate_chords()` → `[]`; appending `KeyBinding("R","R","roles","roles","doors")` → `duplicate_chords()` still `[]` (`R` exists only in `map` scope, where cross-scope reuse is legitimate per the seat's own docstring). | relied on (HLR-RH.8 home key) |
| 4 | `darkside.plain` exists and is the sanctioned content-preserving coercion at the paint boundary. | low | ✅ TRUE | `grep -n "def plain" mapper/darkside.py` → `550:def plain(value: object) -> str:`; ARCHITECTURE §3 `github` row already depends on it. Round-1 ruling R10 corrects the claim: `plain()` preserves content; markup safety comes from painting into `rich.text.Text` sinks (LLR-RH.8.4/8.5). | relied on (LLR-RH.8.4) |
| 5 | The console entry `mapper` dispatches to `mapper.app:main`. | low | ✅ TRUE | `grep -n "project.scripts" -A1 pyproject.toml` → `mapper = "mapper.app:main"`. | relied on (LLR-RH.7.2 CLI surface) |
| 6 | The batch's base commit `fb1d4ce…` exists locally (no network in this unit; `origin/main` unfetchable). | high | ✅ TRUE | `git cat-file -t fb1d4ce6118b57a540bd67bd2115e5400b356870` → `commit` (executed at P0 per PLAN.md RC-1). | relied on (RC-1 premise) |
| 7 | `mapper.osopen` exposes the confinement helpers the R8 ruling mandates reusing. | low | ✅ TRUE | `grep -n "def confine_reason\|def is_link" mapper/osopen.py` → `127:def is_link(info: os.stat_result) -> bool:` and `163:def confine_reason(text: str, workspace: Path) -> tuple[Path | None, str]:`. | relied on (R8 path confinement) |
| 8 | The deep-nesting/oversize error ladder the R9 ruling mandates reusing exists in the store. | low | ✅ TRUE | `sed -n '704,722p' mapper/store.py` → `except (yaml.YAMLError, ValueError, RecursionError)` with the measured ValueError/RecursionError commentary. | relied on (R9 limits) |

- **Premise evaluation:** 8 premise(s) · ✅ TRUE 8 / ❌ FALSE 0 / ❓ UNDECIDABLE 0.

### 2.8 Fork preconditions (C-52) — MANDATORY, and the declared empty when the batch does not fork

| # | Condition (`C-52`) | Discharged? | The executed evidence |
|---|---|---|---|
| 1 | **Frozen contract** — no shared interface is touched inside a lane; one that must change returns to the trunk (trigger A3) | ✅ | One lane, no forks. The only shared-surface touches are DECLARED trunk acts: the ARQ §1/§2/§3 amendment (written inside increment 1 per R11/R19/R20 — it is OWED there, not claimed as present) and the keymap seat edit + `screens/home.py` door row (owned by exactly one increment, the roles-screen increment 6a). All §4 frozen rows untouched — `PDR-2026-10-11-reqharness-batch` §4. |
| 2 | **Disjoint FILE sets**, not just modules — two lanes may not edit the same file, not even different regions | ✅ | Trivially: one lane. Per-increment file sets in `PDR-2026-10-11-reqharness-batch` §8; no two increments share a source file. |
| 3 | **Crossed reverse census** — family B run per lane and **shared before starting**; the trunk's act, impossible from inside a lane | ✅ | Executed at P1 over the opening spec: the symbols this batch adds (`reqharness.*`, `RolesScreen`, the `roles` scope) are asserted by no existing test file (`grep -rl` over `tests/` matches only this batch's not-yet-created files). |
| 4 | **One owner of the trunk** — requirements, traceability, backlog and spec are never written from a lane | ✅ | This document, the PDR, the ARQ amendment and PLAN.md are written only by the orchestrator's trunk units (RH1 = ARQ + P1; RH2 = round-1 rulings application). |

- **Fork preconditions:** none — this batch runs one lane (declared empty; the four conditions each hold trivially and are evidenced above).

---

## 3. High-level requirements (HLR)

### HLR-RH.1 — Configuration, genesis and policy binding
- **Traceability:** US-RH-001
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.3, LED-2026-10-11-reqharness-batch.5, LED-2026-10-11-reqharness-batch.14, LED-2026-10-11-reqharness-batch.18
- **Statement:** When a registry is created in a repository, the system shall write a valid `reqharness/config.yml` (people with `email_sha256` and display names in clear, roles, classes with reviewer roles and normative/informative field sets, release rules) and a `reqharness/roles.yml` whose first event is the genesis declaration of the first admin, recording `roles_hash: "GENESIS"` (no self-reference) and `config_hash` = sha256(canonical config at creation) so the registry is policy-bound from the first document (R15); when a config is loaded, the system shall reject schemas whose class reviewer-role is not a declared role, naming the class and role, and shall reject unknown keys, missing keys, YAML anchors/aliases and duplicate keys; the live config shall be bound to the chain by admin-approved `policy` events carrying sha256(canonical config) — when the live config's canonical hash does not equal the newest verified policy-bearing event's `config_hash`, the system shall declare the state `config changed without approval`, keep the last approved policy in force, and block the release.
- **Rationale (informative):** B-122: roles and policy live in `reqharness/`, edited from the app, never by hand; round-1 ruling R1 (config bypassed the chain — the highest-value file was the least protected); the genesis event is the chain's declared root (P0 ruling O3 — copy "genesis — declared at registry creation"); R3 (typed schema, canonical form); R12 (emails are personal data — stored only as hashes); R15 (a fresh registry had no policy event — genesis now carries the creation-time config hash, closing the backdating hole).
- **Validation:** `test`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_config.py` (nodes `test_genesis_creates_chain_with_declared_admin`, `test_load_rejects_unknown_reviewer_role`, `test_canonical_json_typed_schema`, `test_email_sha256_roundtrip`).
- **Numeric pass threshold:** 0 failed tests in the file; the genesis document verifies with `roles_hash: "GENESIS"` and binds the creation-time config hash (the fresh registry is policy-bound — a genesis without `config_hash` fails, mutation M-CF1 arm); the invalid-fixture load raises a validation error naming `class=HLR role=nosuch` (mutation M-CF2 goes RED if the cross-check is dropped); the `{"a":"ab","b":"c"}` vs `{"a":"a","b":"bc"}` canonical-JSON digests differ (M-CJ1 RED on concatenation); the written config contains no clear-text email (M-EH1 RED).
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** a freshly created registry loads clean; a config pointing a class at an undeclared role is refused with the offending pair named; a hand-edited config is detected through the policy binding with the last approved policy in force.
  - **Shipped surface:** `mapper/reqharness/config.py` + `canonical.py` (`create_registry` / `load_config` / canonical serialisation).
  - **Acceptance test(s):** covered by the LLR layer-0 nodes; no dedicated AT (no user-visible surface beyond the screen, which AT-077a exercises end to end).
  - **Boundary catalog (QC-3):** ☑ empty (no config → clean, named error) ☑ invalid (unknown reviewer role) ☑ error (malformed YAML → loader error surfaced as a validation failure, never a traceback into the UI) ☑ invalid (unknown/missing key, anchor/alias, duplicate key) ☑ error (datetime/bool-shaped scalar under the typed schema)
  - **Negative control:** M-CF1 (genesis `prev_hash` changed) · M-CF2 (reviewer-role cross-check removed) · M-CJ1 (concatenation hashing) · M-EH1 (clear-text email) — each executed RED at the increment's RED proof.

### HLR-RH.2 — Approved role chain with head binding and pending resolution
- **Traceability:** US-RH-001
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.3, LED-2026-10-11-reqharness-batch.4, LED-2026-10-11-reqharness-batch.8, LED-2026-10-11-reqharness-batch.10, LED-2026-10-11-reqharness-batch.29
- **Statement:** When a role change is proposed, the system shall append at most one chain event, approved only by a holder of `admin` in the roles in force at the current head; an admin's change about another person shall be applied in one event (`requested_by = approved_by = that admin`); a change about oneself, or proposed by a non-admin, shall be written as a pending request file under `reqharness/pending/` and write nothing to `roles.yml`; every chain event shall record the head it was made against (`roles_seq` + `roles_hash`) and chain `time` shall be non-decreasing; effective roles shall derive from the verified chain prefix folded up to a bound head — never at wall-clock time; an admin shall resolve a pending request with `a` (approve) or `r` (reject), never their own, and the resolution shall be a chain event referencing the request's sha256, from which the resolved state is derived.
- **Rationale (informative):** B-122 rulings 1 and genesis rule; P0 ruling O5 (one key for others, pending for self / non-admins); R2 (head binding — tail truncation and genesis rewrites otherwise verify clean; wall-clock authority is backdatable); R6 (pending had no home — no persistence, no resolution, lost on restart).
- **Validation:** `test`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_chain.py` (nodes `test_admin_applies_to_someone_else_in_one_event`, `test_self_change_and_non_admin_stay_pending`, `test_effective_roles_at_time_t`, `test_policy_event_binds_config`, `test_head_binding_unknown_head_not_verifiable`, `test_fork_recovery_reappend_on_head`).
- **Numeric pass threshold:** 0 failed tests; the one-key apply writes exactly 1 event with `requested_by == approved_by`; the pending paths write 0 bytes to `roles.yml` and exactly 1 pending file each; `effective_roles(bound_head)` for a head before a later grant excludes that grant; a resolution event carries the request's sha256.
- **Priority:** high
- **Acceptance (black-box):**
  - **Observable outcome:** the matrix shows the change land (●) for an admin acting on others, a pending glyph (◐/◌) for self-changes and non-admin proposals that survives restart, and `a`/`r` landing the resolution as a chain event.
  - **Shipped surface:** `mapper/reqharness/chain.py` (append + policy + verify) + `pending.py` (request store), painted by `mapper/screens/roles.py`.
  - **Acceptance test(s):** AT-078 (propose semantics) · AT-082 (a/r resolution, restart arm).
  - **Boundary catalog (QC-3):** ☑ boundary (sole admin's own-role change pending until a second admin exists) ☑ invalid (non-admin approve attempt; non-admin `a` → "a is unavailable (needs an admin)") ☑ boundary (resolution of one's own request refused) ☑ boundary (the boundary at `roles_seq` == event seq is inclusive — the correct code compares with `<=` ON `roles_seq`; M-CH5 flips it to `<` — R26)
  - **Negative control:** M-CH1 (two-event path forced) · M-CH2 (self-approval allowed) · M-CH5 (`<=` on `roles_seq` flipped to `<` at the bound-head fold) · M-P1 (policy hash check skipped) · M-HB1 (unknown bound heads accepted) · M-PR1 (non-admin resolution lands).

### HLR-RH.3 — Tamper, truncation, policy and fork detection
- **Traceability:** US-RH-001, US-RH-003
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.4, LED-2026-10-11-reqharness-batch.9, LED-2026-10-11-reqharness-batch.11, LED-2026-10-11-reqharness-batch.19, LED-2026-10-11-reqharness-batch.30
- **Statement:** When `reqharness/roles.yml` fails verification — a hand edit anywhere in the file, a policy mismatch, a decreasing `time`, an event bound to a head that does not exist in the chain, or two documents claiming the same `prev_hash` after a merge — the system shall keep the last verified roles and last approved policy in force, declare the state `config changed without approval`, and report the first broken document; verification walks the chain BY `prev_hash` from genesis, NOT by file position (R27) — a document whose `prev_hash` matches an already-claimed parent is a fork sibling, tolerated from authority only when a later valid `resolve` names it in `resolve_excludes`, and a fork whose excluded branch has descendants (a multi-event excluded branch) breaks the chain — multi-event branch recovery is **deferred (B-126)**; a `resolve` is valid only when the chosen child itself passes the approval rule at its own bound head (R27); when two events share a `prev_hash`, BOTH children shall be excluded from authority deterministically and the state reported as `chain forked at seq N`; recovery shall be a `resolve` event — admin-approved, whose `prev_hash` is the chosen child and which names the excluded sibling's hash — after which the chain verifies again; recovery remains a DOCUMENTED manual procedure this batch (fork-recovery UI is **deferred, B-126**); input limits shall be enforced on every parsed file (≤ 64 KB per review/pending file, ≤ 4 MB roles.yml, ≤ 100 000 review files) with malformed or oversize files reported BY NAME, never silently skipped.
- **Rationale (informative):** B-122 ruling 1: a hand edit breaks the chain; mapper ignores it and keeps the last approved roles; R2 (truncation/rewrite detection via head binding); R7 (merge-order-dependent fork outcomes — the fork now degrades to a deterministic exclusion, never silent authority); R16 (fork recovery is a `resolve` event naming the chosen child and the excluded sibling — the re-append procedure becomes a documented manual act, and fork-recovery UI is deferred, B-126); R9 (unbounded input: no limits, aliases, duplicate keys); R27 (verify is a walk BY `prev_hash` — the file-position reading fails on parent, childA, childB, resolve; a sibling survives only behind a `resolve` that names it; a multi-event excluded branch is broken, its recovery deferred to B-126; the chosen child must pass the approval rule at its own bound head).
- **Validation:** `test`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_chain.py` (nodes `test_hand_edit_breaks_chain_and_keeps_last_verified`, `test_merge_fork_is_detected`, `test_head_binding_unknown_head_not_verifiable`, `test_fork_resolve_event_recovers`, `test_input_limits_reported_by_name`, `test_verify_walks_by_prev_hash_in_order_fork_resolve`, `test_resolve_naming_non_sibling_is_invalid`, `test_multi_event_excluded_branch_is_broken` — the last three are the R27 arms).
- **Numeric pass threshold:** 0 failed tests; the tamper fixture's effective roles equal the last verified prefix exactly; verify names the spliced document; the fork fixture excludes both children on EVERY document order; the in-order fork + resolve fixture verifies clean; a resolve naming a non-sibling fails verify; the multi-event excluded-branch fixture reports `chain broken`; each oversize/malformed fixture is refused with the file named.
- **Priority:** high
- **Acceptance (black-box):**
  - **Observable outcome:** after a hand edit, the roles screen shows the old (verified) roles, the footer band reads `config changed without approval`, and the release verdict is `not ready · registry not verifiable`; a forked chain paints `chain forked at seq N`; recovery is a core `resolve` event (documented manual procedure — fork-recovery UI deferred, B-126).
  - **Shipped surface:** `mapper/reqharness/chain.py` + the footer band of `mapper/screens/roles.py`.
  - **Acceptance test(s):** AT-079 (tampered read-only state) · AT-083 (fork exclusion + recovery).
  - **Boundary catalog (QC-3):** ☑ invalid (hand-edited `roles.yml`) ☑ boundary (forked chain after a merge — two events, one `prev_hash`, both orders) ☑ error (truncated tail; genesis rewrite) ☑ error (oversize/anchor/duplicate-key/deeply-nested file → named refusal) ☑ boundary (in-order fork + `resolve` recovering — R27) ☑ invalid (`resolve` naming a non-sibling — R27) ☑ error (multi-event excluded branch → `chain broken` — R27)
  - **Negative control:** M-CH3 (hash recompute skipped) · M-CH4 (fork deduped by seq) · M-HB1 (unknown bound heads accepted) · M-FR1 (fork resolved by keeping a child) · M-FR4 (a `resolve` legitimates a chosen child that fails the approval rule at its own bound head — R27) · M-LM1 (size limit skipped).

### HLR-RH.4 — Review events bound to content digests and chain heads
- **Traceability:** US-RH-002
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.4, LED-2026-10-11-reqharness-batch.7, LED-2026-10-11-reqharness-batch.10
- **Statement:** When a review event is recorded under `reqharness/reviews/` — one immutable file per event, named `<yyyymmdd>-<sha8 of canonical content>.yml`, written with exclusive create — the system shall bind it to the normative-field digest of the object, the reviewer identity, and the chain head (`roles_seq` + `roles_hash`); a review shall close an object's state only if the signer held the class-designated reviewer role in the verified chain at its bound head and the recorded head exists in the current chain; a review by a self-declared model (`kind: model`) or by a signer without the role at its bound head shall be recorded as pre-review, flagged `unentitled` where applicable, and shall never close the state or block the release by itself.
- **Rationale (informative):** B-119 D1 (review bound to content digest) + B-121 rulings 2–3 (normative/informative; role-bound approval; model reviews are pre-review); R2 (a review bound to a truncated-away head is `not verifiable` — deletion and truncation become detectable); R5 (one unentitled review must not block every release forever); R8 (content-derived names, exclusive create, link/junction refusal).
- **Validation:** `test`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_registry.py` (nodes `test_normative_edit_needs_review_informative_marks_only`, `test_review_by_signer_without_role_in_force_is_pre_reviewed`, `test_model_review_never_closes_state`, `test_review_file_naming_and_exclusive_create`, `test_identity_reader_repo_local_then_global`).
- **Numeric pass threshold:** 0 failed tests; informative-only edit keeps `reviewed` in 100% of fixture rows and raises the mark; signer-without-role and model fixtures derive `pre-reviewed` and do NOT block release; a duplicate file name fails the exclusive create; a review bound to an unknown head derives `not verifiable`.
- **Priority:** high
- **Acceptance (black-box):**
  - **Observable outcome:** editing a requirement's statement after review flips it to `changed · review`; editing only its rationale leaves `reviewed` with a visible informative mark; the audit report counts pre-reviews and unentitled reviews separately.
  - **Shipped surface:** `mapper/reqharness/reviews.py` + `derive.py`; readout via `mapper --audit <repo>`.
  - **Acceptance test(s):** AT-080 (per-state counts in the report).
  - **Boundary catalog (QC-3):** ☑ boundary (review by someone without the role AT THAT BOUND HEAD — later grants must not retro-authorize) ☑ invalid (review by a model) ☑ boundary (normative vs informative edit) ☑ error (deleted/corrupted review file; review bound to an unknown head) ☑ boundary (file-name collision on exclusive create) ☑ invalid (link/junction under `reqharness/`)
  - **Negative control:** M-RG1 (informative fields folded into the normative digest) · M-RG2 (role checked against today's head instead of the bound head) · M-RG3 (model reviews close) · M-FN1 (caller-supplied file names) · M-HB1 (unknown bound heads accepted).

### HLR-RH.5 — Derived object states under the precedence table
- **Traceability:** US-RH-002, US-RH-003
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.2, LED-2026-10-11-reqharness-batch.4, LED-2026-10-11-reqharness-batch.6, LED-2026-10-11-reqharness-batch.7
- **Statement:** When states are derived for the canon objects (HLR/LLR rows of `REQUIREMENTS.md`), each object shall carry exactly one of `reviewed` · `changed · review` · `pre-reviewed` · `not reviewed` · `retired`, under the explicit precedence: `not verifiable` (chain/policy breaks, unknown recorded heads) dominates every outcome; a newer pre-review never downgrades a qualifying human review on the same digest; a review on a stale digest never closes; unentitled reviews are flagged and counted apart; retired objects are excluded from the release rule; an empty registry derives zero states; a genesis-only chain verifies clean; an unparseable canon row is reported by line, never silently skipped; review events are immutable once written (a correction is a new event) and parsing is accelerated by a content-keyed cache inside `.git/reqharness-cache/` — keyed by sha256(file bytes), a pure accelerator whose deletion changes no result (LLR-RH.5.3) — with the warm-cache derivation budget of LLR-RH.5.4.
- **Rationale (informative):** B-121 ruling 2 + D9's `(retired)` tolerance in its minimal form (a withdrawn requirement — canon status starting with `withdrawn` — is `retired`, never an error); R5 (ambiguous precedence); R4 (the mtime-keyed cache could change a verdict — content key + `.git/` location + audit cache-off); the spike (`spike/rhs-scale.md`) measured 2.3 s per load at 5 000 review files with the pure-Python loader and timeouts at 20 000.
- **Validation:** `test`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_registry.py` (node `test_derived_states_boundary_catalog` + `test_review_parse_cache_is_pure_accelerator`).
- **Numeric pass threshold:** 0 failed tests; the boundary fixture's state map matches the expected set exactly (5-state partition; `all_active_reviewed` vacuously true at 0 objects); 0 derived-state differences between cache-present and cache-deleted runs across the fixture set (100% equal).
- **Priority:** high
- **Acceptance (black-box):**
  - **Observable outcome:** the audit report's per-state counts partition the canon ids; a withdrawn requirement appears under `retired`, not under any active state; pre-reviews and unentitled reviews have their own counts.
  - **Shipped surface:** `mapper/reqharness/derive.py` + `cache.py`; readout via `mapper --audit <repo>`.
  - **Acceptance test(s):** AT-080 (counts in the report), AT-081 (`retired` classification in a diff).
  - **Boundary catalog (QC-3):** ☑ empty (empty registry) ☑ boundary (genesis only) ☑ boundary (withdrawn requirement → `retired`; marker = canon status starting with `withdrawn`) ☑ error (unparseable canon row → reported line) ☑ boundary (large registry cold vs warm cache equality) ☑ invalid (poisoned cache entry — bounded to a re-parse, never a verdict change)
  - **Negative control:** M-RG4 (retired ids counted as active) · M-RG5 (cache feeds the verdict without re-validation) · M-RG2 (precedence inverted — a pre-review downgrades a qualifying review).

### HLR-RH.6 — Baselines with dirty flag and five diff classes
- **Traceability:** US-RH-003
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.15, LED-2026-10-11-reqharness-batch.16, LED-2026-10-11-reqharness-batch.27, LED-2026-10-11-reqharness-batch.30
- **Statement:** When a baseline is created, the system shall freeze the current derivation (objects, digests, states, chain head, review file set) under `reqharness/baselines/<name>.yml` bound to the repository's current commit SHA (read-only `git rev-parse HEAD`) and a `dirty: true|false` flag from read-only `git status --porcelain --no-optional-locks` — the dirty flag is taken ONLY here, in the operator's own repo at `Baseline.create`; `--audit` runs NO `git status` (R27a), and the stated residual is "baseline creation trusts the repo's `.git/config`" — recording the flag and refusing nothing; the system shall diff two baselines, or a baseline against the current state, classifying every object as new / changed / unchanged / retired / deleted (in the baseline, absent from the canon); the `reactivated` class (retired → active) and the review-state progression (reviewed in base → still reviewed / changed · review) are **deferred (B-125)** — round-2 ruling R24 trimmed this batch's classes.
- **Rationale (informative):** B-119 D1 (baselines freeze the review state); P0 ruling O9 (named + commit SHA under `reqharness/baselines/`); R13 (a SHA pinned on uncommitted work claimed too much; deleted ids were unclassified); R14 (F10: a deleted review/row is now reported `deleted`); R24 (the weight assessment deferred `reactivated` + review-state progression to B-125 — five classes plus the dirty flag ship this batch); R27a (the audit path never runs `git status` — inside an untrusted repo a committed `.gitattributes` filter or a planted `git` on the PATH could run code, so the dirty flag is baseline-only and the residual is stated, not fixed).
- **Validation:** `test`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_baseline.py` (node `test_baseline_freezes_commit_sha_and_diffs` + AT node `test_at_081_baseline_vs_now_reports_new_changed_retired`).
- **Numeric pass threshold:** 0 failed tests; the frozen file's `commit` equals the fixture repo's `git rev-parse HEAD`; the `dirty` flag equals the fixture's porcelain state; the diff classifies all five fixture mutations correctly.
- **Priority:** medium
- **Acceptance (black-box):**
  - **Observable outcome:** `mapper --audit <repo> --baseline v0` lists the new, changed, retired and deleted objects since the freeze, with the baseline's `dirty` flag.
  - **Shipped surface:** `mapper/reqharness/baseline.py` via the audit CLI.
  - **Acceptance test(s):** AT-081.
  - **Boundary catalog (QC-3):** ☑ boundary (baseline vs now with new / changed / retired / deleted objects) ☑ boundary (dirty tree at freeze — recorded, refused nothing)
  - **Negative control:** M-BL1 (commit SHA omitted) · M-BL2 (classification by id presence only) · M-BL3 (`deleted` collapsed into `retired`) · M-BL4 (dirty flag forced).

### HLR-RH.7 — Release-rule evaluation and the read-only audit entry
- **Traceability:** US-RH-003
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.3, LED-2026-10-11-reqharness-batch.7, LED-2026-10-11-reqharness-batch.13, LED-2026-10-11-reqharness-batch.16, LED-2026-10-11-reqharness-batch.17, LED-2026-10-11-reqharness-batch.29, LED-2026-10-11-reqharness-batch.35
- **Statement:** When release readiness is evaluated, the system shall apply the three hard-coded mandatory rules — chain verified, policy verified, every closing review signed by a role in force at its bound head — then every rule declared in `config.yml`, and report `ready`, or `not ready · <reason>`; a broken chain, a policy mismatch, or an unknown recorded head shall yield exactly `not ready · registry not verifiable`; an unentitled review alone shall NOT block the release; the `mapper --audit <repo>` CLI shall print the chain status, the per-state counts (pre-reviews and unentitled counted separately), and the verdict, exiting 0 on `ready` and 1 otherwise, without starting the TUI, with the parse cache OFF and without writing anything anywhere; the connected repo shall be the git work tree containing the current workspace (`git rev-parse --show-toplevel`), overridable by the `<repo>` argument, which is confined before any file is read; `ready` does NOT mean every object was reviewed — that guarantee holds only when `config.yml` declares the `all_active_reviewed` rule (D6: the hard-coded mandatory rules are chain verified · policy verified · every closing review signed by a role in force at its bound head; `all_active_reviewed` is a config-declared rule, not a hard-coded one).
- **Rationale (informative):** B-122 ruling 2 (release blocks) + B-119 D1 (the board decides from these artifacts); P0 ruling O8 (CLI name and argument); R1/R5 (mandatory rules; unentitled never blocks alone); R4 (a CI-safe audit writes nothing); R11 (identity + dirty flag come from the read-only allowlist); R14 (numeric exit-code thresholds; 60 s subprocess timeout); D13 (the workspace is a maps dir — the repo is its containing work tree).
- **Validation:** `test`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_release.py` (nodes `test_release_rules_and_verdicts`, `test_at_080_audit_report_counts_every_state_exactly`, `test_audit_cli_refuses_escaping_repo_path`) + `tests/test_reqharness_identity.py`.
- **Numeric pass threshold:** 0 failed tests; each fixture verdict matches its expected string byte-for-byte; CLI exit codes {0,1} correct on both fixtures; the subprocess completes within a 60 s timeout; the workspace sha256 digest is identical before and after the audit run.
- **Priority:** high
- **Acceptance (black-box):**
  - **Observable outcome:** the command prints the verdict an operator can paste into a release discussion; a broken chain is unmistakable; nothing in the repo changes as a side effect.
  - **Shipped surface:** `mapper/reqharness/release.py` + `audit.py` + `identity.py` via the `mapper` console script's `--audit` branch (after the UTF-8 stdout re-wrap).
  - **Acceptance test(s):** AT-080.
  - **Boundary catalog (QC-3):** ☑ error (broken chain / policy mismatch / unknown head → `registry not verifiable`) ☑ empty (0-object registry → `ready` when the other rules pass) ☑ boundary (unentitled review alone → evaluable, not `not verifiable`) ☑ invalid (escaping/unknown repo path → refused before any file is read) ☑ boundary (no repo → the screen says so and offers nothing)
  - **Negative control:** M-RL1 (one rule unevaluated) · M-AU1 (`--audit` ignored by `main()` → the TUI launches → `subprocess.run(timeout=60)` raises `TimeoutExpired`, counted as FAIL) · M-AU2 (confinement after reading).

### HLR-RH.8 — Roles screen with status band, a/r resolution and read-only tamper state
- **Traceability:** US-RH-001
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.8, LED-2026-10-11-reqharness-batch.12, LED-2026-10-11-reqharness-batch.16, LED-2026-10-11-reqharness-batch.17, LED-2026-10-11-reqharness-batch.28
- **Statement:** When the operator opens the roles screen from home with the seat-bound key, the system shall paint the matrix variant B (people × roles; ● in force · ◐ pending add · ◌ pending remove · ○ not held), move the cursor cell to cell, propose changes inline with `space`, resolve pending with `a` (approve) / `r` (reject) — admin only, never one's own, a non-admin's `a` showing "a is unavailable (needs an admin)" — and show in the footer status band the chain event count, the head hash, the viewer identity, the pending detail, the chain status and the release verdict; in a tampered or forked state the matrix shall be read-only — `space` inert with a message; every file-derived string painted shall pass through `darkside.plain` into `rich.text.Text` sinks only; all colours and glyphs shall come from `darkside` tokens and the keymap seat; when no repo is discoverable the screen shall say so and offer nothing to edit.
- **Rationale (informative):** B-123 verdict (variant B); P0 ruling O2 (status band in the roles footer); R6 (a/r resolution keys); R10/R5-sec (markup safety is the Text sink, not `plain()`); R14 (prototype-B divergences: band detail, viewer identity, read-only tamper, 118 AND 87 columns, genesis copy on screen, home door 7→8); D13 (repo discovery).
- **Validation:** `test`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_roles_screen.py` (nodes `test_at_077a_roles_screen_opens_from_home_and_paints_matrix`, `test_at_077b_status_band_shows_chain_head_viewer_and_pending`, `test_at_077c_file_derived_text_paints_through_text_sinks`, `test_at_078_non_admin_toggle_pends_admin_applies_in_one_key`, `test_at_079_tampered_chain_paints_broken_state_and_blocks_release`, `test_at_082_admin_resolves_pending_with_a_and_r`, `test_at_083_forked_chain_paints_excluded_and_recovers`).
- **Numeric pass threshold:** 0 failed tests; at 118×34 AND 87×34 the painted matrix contains every seeded person × role cell with the expected glyph; the band shows all six elements in verified AND pending-bearing states; the home door list grows by exactly one (`R roles`); app-driven with `MapperApp(tmp_path)` + `run_test` + real `pilot.press` keys only.
- **Priority:** high
- **Acceptance (black-box):**
  - **Observable outcome:** the whole team's authority surface at a glance; the three hard states (verified / pending / tampered) readable without explanation; pending resolvable in one key by an admin.
  - **Shipped surface:** `mapper/screens/roles.py` (`RolesScreen`), `mapper/keymap.py` (`roles` scope + home door `R`), `mapper/app.py` re-export + home wiring, `screens/home.py` (door row — owned by this increment).
  - **Acceptance test(s):** AT-077a · AT-077b · AT-077c · AT-078 · AT-079 · AT-082 · AT-083.
  - **Boundary catalog (QC-3):** ☑ boundary (tampered/forked state painting + read-only matrix) ☑ invalid (markup payload in a person name painted literally) ☑ boundary (non-admin `a` unavailability message) ☑ boundary (87-column layout) ☑ empty (no repo → nothing to edit)
  - **Negative control:** M-RS1 (hard-coded colour/glyph) · M-RS1b (raw string through a markup sink) · M-RS2 (band element dropped) · M-RS3 (admin self-toggle applies) · M-RS4 (tampered roles painted) · M-PR1 (non-admin resolution lands).

### HLR-RH.9 — D12 proposal document
- **Traceability:** US-RH-003
- **Ledger:** LED-2026-10-11-reqharness-batch.1
- **Statement:** When station P6 runs, the system shall ship a 06-docs document proposing that dev-flow's 05-close human review ledger be derived from the ReqHarness registry, naming the derived states, the precedence table, and the release-rule semantics it consumes, and marking dev-flow adoption as outside this repository.
- **Rationale (informative):** B-119 D12: the ledger derivation is a proposed dev-flow change; P0 ruling O7 (written this batch, as a document, at P6).
- **Validation:** `inspection`
- **Executed verification:** inspection of the 06-docs document against PDR §3.4 (states + precedence + release semantics it must reference) at the P6 gate.
- **Numeric pass threshold:** 0 unresolved inspection findings; the document exists under `.dev-flow/06-docs/` and references the batch's state semantics by id.
- **Priority:** low
- **Acceptance (black-box):**
  - **Observable outcome:** a reader can trace each proposed ledger field to a derived state or rule in §3.4 of the PDR.
  - **Shipped surface:** `.dev-flow/06-docs/` (document only — no repo code).
  - **Acceptance test(s):** none — inspection at P6.
  - **Boundary catalog (QC-3):** none — a document deliverable; no input classes apply.
  - **Negative control:** none — inspection has no executed RED side.

---

## 4. Low-level requirements (LLR)

> Each LLR decomposes an HLR into a verifiable property at the implementation level. EARS syntax,
> `full` mode. ID format: `LLR-RH.n.m`.

### LLR-RH.1.1 — Config schema validation and loader census
- **Traceability:** HLR-RH.1
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.2, LED-2026-10-11-reqharness-batch.5, LED-2026-10-11-reqharness-batch.11, LED-2026-10-11-reqharness-batch.21, LED-2026-10-11-reqharness-batch.24, LED-2026-10-11-reqharness-batch.29, LED-2026-10-11-reqharness-batch.33
- **Statement:** The `config.py` loader shall validate that every class's `reviewer_role` is one of the declared roles and that normative and informative field sets are disjoint lists of strings, raising a validation error that names the offending class and value; the typed schema shall reject unknown keys, missing keys, and non-`str` scalars except `seq: int` and `roles_seq: int`, and shall isinstance-check every field; `time` fields shall match exactly `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`; parsing shall use a CUSTOM LOADER SUBCLASS on `yaml.CSafeLoader` when available, falling back to `yaml.SafeLoader` — never `yaml.load` with any other loader (orchestrator rulings R-SCALE a + R21 — the subclass rejects duplicate keys at construction time and anchors/aliases by an event-stream pre-scan before construction, because the C composer resolves aliases before Python-level overrides can see them; enforced by a source census over `mapper/reqharness/` plus a fallback-loader test); the subclass's speed cost is measured at P4 against the LLR-RH.5.4 budget.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_config.py::test_load_rejects_unknown_reviewer_role` + the `test_never_yaml_load_source_census` node in `tests/test_reqharness_registry.py`.
- **Numeric pass threshold:** `assert exit code 0`; invalid fixture rejected with both names in the message; valid fixture round-trips; the census finds 0 `yaml.load(`/`FullLoader` occurrences; the disjointness fixture rejected.
- **Negative control:** M-CF2 (cross-check removed) · M-YC1 (a load routed through `yaml.load`) — executed RED.
- **Boundary catalog:** ☑ invalid (unknown role) ☑ error (malformed YAML) ☑ error (syntax-malformed YAML in EACH of the four file kinds — config, roles.yml, a review, a pending file — each refused with the file named, R26) ☑ invalid (unknown/missing key, anchor/alias, duplicate key) ☑ invalid (normative/informative overlap — the disjointness fixture) ☑ invalid (datetime/bool/empty-shaped scalar or malformed `time` under the typed schema — R18)

### LLR-RH.1.2 — Genesis creation with policy binding from the first document
- **Traceability:** HLR-RH.1
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.4, LED-2026-10-11-reqharness-batch.18
- **Statement:** The `create_registry` path shall write `roles.yml` as a one-document YAML stream whose event carries `approved_by: genesis`, `note: "declared at registry creation"`, `prev_hash: GENESIS`, `roles_seq: 1`, `roles_hash: "GENESIS"` (NO self-reference), `config_hash` = sha256 of the canonical serialisation of the normalised config fields at creation, and a `this_hash` that verifies — a policy-bound registry from the first document (R15); the UI paints this event as `genesis — declared at registry creation`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_config.py::test_genesis_creates_chain_with_declared_admin`
- **Numeric pass threshold:** `assert exit code 0`; `verify(roles.yml)` returns clean on the fresh file; the painted string equals the ruled copy (asserted on screen by AT-077a).
- **Negative control:** M-CF1 (`prev_hash` altered) — executed RED.
- **Boundary catalog:** ☑ empty (fresh registry)

### LLR-RH.1.3 — Typed schema and strict canonical form
- **Traceability:** HLR-RH.1
- **Ledger:** LED-2026-10-11-reqharness-batch.5, LED-2026-10-11-reqharness-batch.21
- **Statement:** Every reqharness file shall conform to the typed schema: all fields `str` except `seq: int` and `roles_seq: int`, unknown keys rejected, missing keys rejected, every field isinstance-checked, `time` fields matching exactly `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$` (R18), the writer always quoting scalars, values NFC-normalised before hashing; the canonical serialisation for hashing shall be JSON with sorted keys, no whitespace, `ensure_ascii=False`, after NFC; the normative digest shall be sha256 of that canonical JSON of `{field: normalised value}` — never a concatenation.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_config.py::test_canonical_json_typed_schema`
- **Numeric pass threshold:** `assert exit code 0`; a datetime-shaped scalar, a bare `no`, and an unquoted empty value are each rejected; the `{"a":"ab","b":"c"}` and `{"a":"a","b":"bc"}` field sets hash differently (100% distinct).
- **Negative control:** M-CJ1 (concatenation of values hashed instead of the canonical JSON object) — executed RED.
- **Boundary catalog:** ☑ boundary (the field-boundary pair above) ☑ error (ISO-8601 / bool / empty scalars under the typed schema)

### LLR-RH.1.4 — Email hashing
- **Traceability:** HLR-RH.1
- **Ledger:** LED-2026-10-11-reqharness-batch.14, LED-2026-10-11-reqharness-batch.26
- **Statement:** `config.yml` shall store each person's email only as `email_sha256` (sha256 of the lowercased email); display names stay in clear; the identity reader's git email shall be matched by the same hash; the design documents the personal-data note: `email_sha256` is PSEUDONYMISED personal data — unsalted, dictionary-reversible — and the jurisdiction question goes to the operator (R23).
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_config.py::test_email_sha256_roundtrip`
- **Numeric pass threshold:** `assert exit code 0`; the round-trip fixture matches by hash; a clear-text email regex over the written config finds 0 matches.
- **Negative control:** M-EH1 (email stored in clear) — executed RED.
- **Boundary catalog:** ☑ boundary (mixed-case email → lowercased before hashing)

### LLR-RH.2.1 — Admin one-key apply to another person
- **Traceability:** HLR-RH.2
- **Ledger:** LED-2026-10-11-reqharness-batch.1
- **Statement:** The chain append path shall accept an admin's grant/revoke about another person as ONE event with `requested_by == approved_by == that admin`, appending it to the current head with a recomputed `this_hash` and the current head recorded as `roles_seq`/`roles_hash`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_chain.py::test_admin_applies_to_someone_else_in_one_event`
- **Numeric pass threshold:** `assert exit code 0`; event count grows by exactly 1; both identity fields equal the admin id; the recorded `roles_hash` equals the previous head.
- **Negative control:** M-CH1 (two-event path forced) — executed RED.
- **Boundary catalog:** none beyond the shared chain fixtures.

### LLR-RH.2.2 — Pending rules and the pending file store
- **Traceability:** HLR-RH.2
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.8
- **Statement:** The append path shall write a pending request file under `reqharness/pending/<yyyymmdd>-<sha8>.yml` (requested by, change, bound head), writing nothing to `roles.yml`, when the proposed change is about the requester themselves or the requester holds no `admin` role in the roles in force; a pending self-change shall become appendable once a second admin exists.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_chain.py::test_self_change_and_non_admin_stay_pending`
- **Numeric pass threshold:** `assert exit code 0`; `roles.yml` bytes identical before/after both pending paths; exactly 1 pending file per request; the second-admin arm appends successfully.
- **Negative control:** M-CH2 (self-approval allowed) — executed RED.
- **Boundary catalog:** ☑ boundary (sole-admin self-change until second admin)

### LLR-RH.2.3 — Effective roles at a bound head
- **Traceability:** HLR-RH.2
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.4, LED-2026-10-11-reqharness-batch.16, LED-2026-10-11-reqharness-batch.29, LED-2026-10-11-reqharness-batch.31
- **Statement:** The `effective_roles(bound_head)` derivation shall fold only verified-prefix events whose OWN `seq` is `<=` the bound head's `seq`, so a grant never retro-authorizes a review bound to an earlier head; the boundary comparison uses `<=` ON the event's own `seq` — never on `roles_seq` (an event at seq k+1 records `roles_seq` k, so a `roles_seq` fold would leak it into head k) and never on event time — one exact comparison, R26); mutation M-CH5 is defined as the flip of that correct `<=` to `<`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_chain.py::test_effective_roles_at_time_t`
- **Numeric pass threshold:** `assert exit code 0`; the pre-grant head excludes the granted role, the post-grant head includes it; a grant at seq k+1 is NOT in force at head k even though its `roles_seq` is k; the boundary instant (bound `seq` == the grant event's own `seq`) includes the event.
- **Negative control:** M-CH5 (the correct `<=` on the event's own `seq` flipped to `<` at the bound-head fold) — executed RED.
- **Boundary catalog:** ☑ boundary (bound `seq` exactly at the grant event's own `seq` — inclusive)

### LLR-RH.2.4 — Policy events bind the config
- **Traceability:** HLR-RH.2
- **Ledger:** LED-2026-10-11-reqharness-batch.3, LED-2026-10-11-reqharness-batch.18
- **Statement:** Appending a `policy` event (admin in force required) shall record `config_hash` = sha256 of the canonical serialisation of the normalised config fields; the genesis event carries the creation-time `config_hash` too (R15), so a fresh registry is policy-bound from the first document; at load and release, the live config's canonical hash shall be compared with the newest verified policy-bearing event's (genesis or `policy`) `config_hash` — a mismatch yields the state `config changed without approval`, keeps the last approved policy in force, and blocks the release.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_chain.py::test_policy_event_binds_config`
- **Numeric pass threshold:** `assert exit code 0`; the hand-edited-config fixture derives `config changed without approval`; the release verdict is `not ready · registry not verifiable`; the unedited fixture stays clean.
- **Negative control:** M-P1 (policy hash check skipped) — executed RED.
- **Boundary catalog:** ☑ invalid (hand-edited config) ☑ boundary (config extended by an added release rule — requires a new policy event)

### LLR-RH.2.5 — Head binding and non-decreasing time
- **Traceability:** HLR-RH.2
- **Ledger:** LED-2026-10-11-reqharness-batch.4, LED-2026-10-11-reqharness-batch.21
- **Statement:** Every chain event shall record the head it was made against (`roles_seq` + `roles_hash`); chain `time` shall be non-decreasing across the verified prefix, compared as strings over the one exact format `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$` (R18); an event whose recorded head does not exist in the current chain shall make verification fail (`not verifiable`), detecting tail truncation and full rewrites from genesis.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_chain.py::test_head_binding_unknown_head_not_verifiable`
- **Numeric pass threshold:** `assert exit code 0`; the truncated-tail fixture and the genesis-rewrite fixture both fail verify; the decreasing-time fixture fails verify; intact fixtures stay clean.
- **Negative control:** M-HB1 (unknown bound heads accepted) — executed RED.
- **Boundary catalog:** ☑ error (tail truncation) ☑ error (full rewrite from genesis) ☑ error (decreasing time)

### LLR-RH.3.1 — Verify and last-verified prefix over canonical links
- **Traceability:** HLR-RH.3
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.4, LED-2026-10-11-reqharness-batch.5, LED-2026-10-11-reqharness-batch.30
- **Statement:** The verifier shall walk the chain BY `prev_hash` from genesis — NOT by file position (R27): starting from `prev_hash: GENESIS`, each document's recorded `prev_hash` must be the walk's current head and its recomputed link (`sha256(prev_hash + "\n" + canonical_json(event_without_this_hash))`, canonical JSON per LLR-RH.1.3) becomes the new head; a document whose `prev_hash` matches an already-claimed parent (a hash the walk has already passed) is a **fork sibling**, not a continuation — a sibling is excluded from authority and tolerated only when a later valid `resolve` names it in `resolve_excludes` (LLR-RH.3.4); the walk rejects unknown actions; requires `time` non-decreasing over the R18 exact-format string compares; requires every event's recorded (`roles_seq`, `roles_hash`) to point at a real prefix head (an event bound to a missing head → `not verifiable`); the first failed link, unknown action, decreasing time, unknown bound head, or un-resolved sibling yields CHAIN BROKEN reported at that document; a fork whose excluded branch has descendants (a multi-event excluded branch) yields CHAIN BROKEN — multi-event branch recovery is **deferred (B-126)**; all derived authority shall come from the longest verified prefix only; `reqharness/roles.yml` parsing shall be confined by `mapper.osopen.confine_reason` (`..`, links and junctions refused).
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_chain.py::test_hand_edit_breaks_chain_and_keeps_last_verified` + the R27 arms `test_verify_walks_by_prev_hash_in_order_fork_resolve` and `test_multi_event_excluded_branch_is_broken`
- **Numeric pass threshold:** `assert exit code 0`; broken document equals the spliced document at its walk position; the in-order parent→childA→childB→resolve fixture verifies clean; the multi-event excluded-branch fixture reports `chain broken`; effective roles equal the prefix fold exactly.
- **Negative control:** M-CH3 (recompute skipped) · M-FR3 (verify walks by file position, so a reordered-but-valid chain mis-walks) — executed RED.
- **Boundary catalog:** ☑ invalid (hand-edited `roles.yml`) ☑ invalid (escaping path / link / junction under `reqharness/`) ☑ boundary (in-order fork + `resolve` — R27) ☑ error (multi-event excluded branch → `chain broken` — R27)

### LLR-RH.3.2 — Merge-fork detection with deterministic exclusion
- **Traceability:** HLR-RH.3
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.9, LED-2026-10-11-reqharness-batch.30
- **Statement:** The verifier shall detect two documents claiming the same `prev_hash` (the parallel-PR merge shape): in the BY-`prev_hash` walk (LLR-RH.3.1) the second document to claim a parent the walk has already passed is a **fork sibling**, excluded from authority with its parent-bound sibling deterministically on every clone regardless of document order, and reported `chain forked at seq N`; a sibling is tolerated from authority only when a later valid `resolve` names it in `resolve_excludes` (LLR-RH.3.4); a fork whose excluded branch has descendants (a multi-event excluded branch) yields `chain broken` — multi-event branch recovery is **deferred (B-126)** (R27).
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_chain.py::test_merge_fork_is_detected` + the R27 arms `test_verify_walks_by_prev_hash_in_order_fork_resolve` and `test_multi_event_excluded_branch_is_broken`
- **Numeric pass threshold:** `assert exit code 0`; both fork children are reported AND excluded in both document orders (2/2 orders agree); the single-event fork behind a valid `resolve` verifies clean; the multi-event excluded-branch fixture reports `chain broken`.
- **Negative control:** M-CH4 (fork deduped by seq) · M-FR3 (verify walks by file position) — executed RED.
- **Boundary catalog:** ☑ boundary (forked chain after a merge, both document orders) ☑ boundary (in-order fork + `resolve` — R27) ☑ error (multi-event excluded branch → `chain broken` — R27)

### LLR-RH.3.3 — Tamper state word
- **Traceability:** HLR-RH.3
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.2
- **Statement:** When verification fails, the chain status exposed to screens and the audit CLI shall be exactly `config changed without approval`.
- **Validation:** `test (unit)`
- **Executed verification:** asserted inside `tests/test_reqharness_chain.py::test_hand_edit_breaks_chain_and_keeps_last_verified` and AT-079's band assertion.
- **Numeric pass threshold:** 0 mismatched strings; the string compares equal (byte-for-byte) in both layers.
- **Negative control:** M-CH3 (with verify skipped the word never appears) — executed RED.
- **Boundary catalog:** none (a constant, covered by the tamper fixtures).

### LLR-RH.3.4 — Fork recovery by a resolve event
- **Traceability:** HLR-RH.3
- **Ledger:** LED-2026-10-11-reqharness-batch.9, LED-2026-10-11-reqharness-batch.19, LED-2026-10-11-reqharness-batch.30
- **Statement:** After a fork, the only legal continuation shall be a `resolve` event — admin-approved by a holder of `admin` in the roles in force at the CHOSEN CHILD's bound head, whose `prev_hash` is the CHOSEN fork child and which names the excluded sibling's hash — and the `resolve` is valid ONLY when the chosen child itself passes the approval rule at its own bound head (`approved_by` held `admin` in force at that child's bound head; a fork child that was never legitimately approvable cannot be legitimized by `resolve` — R27); after a valid `resolve` the chain shall verify clean and authority shall return (R16); recovery remains a DOCUMENTED manual procedure in the module docstring this batch — fork-recovery UI automation is **deferred (B-126)**; the procedure is exercised by test.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_chain.py::test_fork_resolve_event_recovers` + the R27 arms `test_verify_walks_by_prev_hash_in_order_fork_resolve` and `test_resolve_naming_non_sibling_is_invalid`
- **Numeric pass threshold:** `assert exit code 0`; the recovered chain verifies with exactly the resolve event beyond the fork point; a resolve naming a non-sibling (a hash that is not one of the fork's children) fails verify; a resolve whose chosen child fails the approval rule at its own bound head fails verify.
- **Negative control:** M-FR1 (fork resolved by keeping a child / naming the wrong sibling) · M-FR4 (a `resolve` legitimates a chosen child that fails the approval rule at its own bound head — R27) — executed RED.
- **Boundary catalog:** ☑ boundary (recovery on the forked fixture via `resolve`) ☑ invalid (`resolve` naming a non-sibling — R27) ☑ invalid (`resolve` choosing a child that fails the approval rule at its own bound head — R27)

### LLR-RH.3.5 — Input limits and named refusals
- **Traceability:** HLR-RH.3
- **Ledger:** LED-2026-10-11-reqharness-batch.11, LED-2026-10-11-reqharness-batch.29, LED-2026-10-11-reqharness-batch.33
- **Statement:** The loaders shall enforce: ≤ 64 KB per review/pending file, ≤ 4 MB `roles.yml`, ≤ 100 000 review files; YAML anchors/aliases rejected by an event-stream pre-scan before construction and duplicate keys rejected at construction time by the custom loader subclass (R21); `RecursionError`/`ValueError` caught as in `mapper/store.py:706-720`; a malformed or oversize file shall be reported BY NAME, never silently skipped.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_chain.py::test_input_limits_reported_by_name`
- **Numeric pass threshold:** `assert exit code 0`; each of the 5 refusal fixtures (oversize review, oversize roles.yml, anchor/alias, duplicate keys, deep nesting) raises the named validation error carrying the file name — 5/5 named; plus a syntax-malformed YAML fixture in EACH of the four file kinds (config, roles.yml, review, pending) — 4/4 named (R26).
- **Negative control:** M-LM1 (size limit skipped) — executed RED.
- **Boundary catalog:** ☑ boundary (64 KB review file accepted / 64 KB + 1 refused) ☑ error (4 MB roles.yml limit) ☑ error (deep nesting → RecursionError caught, named) ☑ error (syntax-malformed YAML in each of the four file kinds — named, R26) ☑ invalid (anchor/alias, duplicate keys)

### LLR-RH.4.1 — Normative digest binding and informative mark
- **Traceability:** HLR-RH.4
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.5
- **Statement:** The digest module shall hash the object's normative fields (config-declared per class) into the normative digest — sha256 of the canonical JSON of `{field: normalised value}`, never a concatenation — and the informative fields into a separate informative digest; a review event records the normative digest at review time; a normative mismatch re-opens the state, an informative-only mismatch raises the `changed (informative)` mark without changing the state.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_registry.py::test_normative_edit_needs_review_informative_marks_only`
- **Numeric pass threshold:** `assert exit code 0`; both edit classes across all fixture rows classify as specified (100%).
- **Negative control:** M-RG1 (informative folded into normative) — executed RED.
- **Boundary catalog:** ☑ boundary (normative vs informative edit)

### LLR-RH.4.2 — Signer role in force at the bound head
- **Traceability:** HLR-RH.4
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.7, LED-2026-10-11-reqharness-batch.20
- **Statement:** A human review shall close an object's state only when the signer held the class-designated reviewer role in the VERIFIED chain at the review's BOUND HEAD and the recorded head exists; otherwise the event derives `pre-reviewed`, is flagged `unentitled` when the signer held no designated role at all, and never blocks the release by itself; a chain/policy break or unknown head still yields `not verifiable`; the audit report shall WARN when a review's bound head precedes a LATER revocation of its signer's role (old-head binding — a core comparison over the chain, no git; a stated residual, R17 — layer 3 remains the strong answer).
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_registry.py::test_review_by_signer_without_role_in_force_is_pre_reviewed`
- **Numeric pass threshold:** `assert exit code 0`; the retro-authorization fixture derives `pre-reviewed` and the release stays evaluable (not `not verifiable` on that account alone).
- **Negative control:** M-RG2 (role checked against today's head instead of the bound head) — executed RED.
- **Boundary catalog:** ☑ boundary (review by someone without the role at that bound head) ☑ boundary (unentitled review alone → release still evaluable) ☑ boundary (old-head binding → a WARN line in the audit report, non-blocking — R17)

### LLR-RH.4.3 — Model reviews are self-declared pre-review
- **Traceability:** HLR-RH.4
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.7
- **Statement:** A review event with `kind: model` — a self-declared kind, stated as such wherever the kind is named — shall derive `pre-reviewed` regardless of digest match or signer, and shall never satisfy a release rule.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_registry.py::test_model_review_never_closes_state`
- **Numeric pass threshold:** `assert exit code 0`; state is `pre-reviewed` and the release verdict is not `ready`.
- **Negative control:** M-RG3 (model reviews close) — executed RED.
- **Boundary catalog:** ☑ invalid (review by a model)

### LLR-RH.4.4 — Identity source and its ceiling
- **Traceability:** HLR-RH.4
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.13, LED-2026-10-11-reqharness-batch.26
- **Statement:** Reviewer identity shall be read by the identity reader from repo-local `git config user.name` / `user.email`, falling back to global config (tests inject repo-local identity); the `reviewer` field of a review event is FREE TEXT — identity is the git config, never proven from the file; the documentation and the audit report shall state that this identity is self-claimed and spoofable by any committer, that the chain proves integrity and approval, not authorship, and that the residual layer-3 risk — a full consistent rewrite of chain + every review by a writer with repo access — is answered by B-122's strong mode (signed commits), a named follow-up, with git anchoring of genesis also follow-up.
- **Validation:** `inspection` (docstring + report footer text, cross-read at P2)
- **Executed verification:** `grep` census at P2 over `mapper/reqharness/` for the ceiling sentence; the audit report fixture contains it; `tests/test_reqharness_identity.py` asserts the repo-local-then-global precedence.
- **Numeric pass threshold:** 0 missing-ceiling findings.
- **Negative control:** none — an honesty statement, not a mechanism.
- **Boundary catalog:** none.

### LLR-RH.4.5 — Head binding on review events
- **Traceability:** HLR-RH.4
- **Ledger:** LED-2026-10-11-reqharness-batch.4
- **Statement:** Every review event and every pending request shall record the chain head it was made against (`roles_seq` + `roles_hash`); derivation shall treat a review whose recorded head is not in the current chain as `not verifiable` input — a deleted review is detected through baselines (`deleted` class), and a truncated or rewritten chain is detected through the missing head.
- **Validation:** `test (unit)`
- **Executed verification:** asserted inside `tests/test_reqharness_registry.py::test_derived_states_boundary_catalog` (unknown-head arm) and `tests/test_reqharness_chain.py::test_head_binding_unknown_head_not_verifiable`.
- **Numeric pass threshold:** `assert exit code 0`; the unknown-head review fixture drives `not verifiable`; 0 silently-ignored unknown heads.
- **Negative control:** M-HB1 (unknown bound heads accepted) — executed RED.
- **Boundary catalog:** ☑ error (review bound to a truncated-away head)

### LLR-RH.4.6 — Review and pending file naming with exclusive create and content check
- **Traceability:** HLR-RH.4
- **Ledger:** LED-2026-10-11-reqharness-batch.10, LED-2026-10-11-reqharness-batch.25
- **Statement:** Review and pending files shall be named `<yyyymmdd>-<sha8 of canonical content>.yml` — derived from canonical content only, never from caller-supplied slugs — and written with exclusive create (a second write under the same name fails); the loader shall recompute sha8 over the canonical content of every review/pending file, and a mismatch with the file name shall be reported BY NAME and non-closing (R22); links and junctions under `reqharness/` shall be refused via `mapper.osopen.is_link`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_registry.py::test_review_file_naming_and_exclusive_create`
- **Numeric pass threshold:** `assert exit code 0`; every fixture file matches the name shape; the collision fixture fails; the link/junction fixture is refused; the name/content-mismatch fixture is reported by name and derives no state.
- **Negative control:** M-FN1 (caller-supplied file names) · M-FN2 (the sha8 content check skipped) — executed RED.
- **Boundary catalog:** ☑ boundary (name collision on exclusive create) ☑ boundary (name/content mismatch → named report, non-closing — R22) ☑ invalid (link/junction under `reqharness/`)

### LLR-RH.5.1 — Five-state derivation under the precedence table
- **Traceability:** HLR-RH.5
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.4, LED-2026-10-11-reqharness-batch.7, LED-2026-10-11-reqharness-batch.29
- **Statement:** The derivation shall assign each canon object exactly one state — `reviewed` · `changed · review` · `pre-reviewed` · `not reviewed` · `retired` — retired for canon ids whose status starts with `withdrawn`, `not reviewed` when no review event names the id, `pre-reviewed` when only pre-reviews apply, `changed · review` when reviews exist but none matches the current normative digest, `reviewed` only on a qualified closing review (LLR-RH.4.2); the precedence shall hold: `not verifiable` dominates; a newer pre-review never downgrades a qualifying human review on the same digest; a stale-digest review never closes; unentitled reviews are counted apart; a canon row the reader cannot parse is REPORTED by line and derives no state.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_registry.py::test_derived_states_boundary_catalog`
- **Numeric pass threshold:** `assert exit code 0`; fixture state map equals the expected partition exactly; the unparseable-row fixture produces exactly 1 reported line and 0 guessed states.
- **Negative control:** M-RG4 (retired counted active) · M-RG2 (precedence inverted) — executed RED.
- **Boundary catalog:** ☑ empty (empty registry — zero states, release rule vacuous) ☑ boundary (genesis-only chain verifies) ☑ boundary (withdrawn marker = status starting with `withdrawn`) ☑ error (unparseable canon row → reported line) ☑ error (a corrupted review file at derive time → reported by name, derives no state — R26)

### LLR-RH.5.2 — Retired exclusion
- **Traceability:** HLR-RH.5
- **Ledger:** LED-2026-10-11-reqharness-batch.1
- **Statement:** The `all_active_reviewed` rule shall consider only non-retired objects; a registry whose active objects are all reviewed is `ready` on this rule even when retired objects are unreviewed.
- **Validation:** `test (unit)`
- **Executed verification:** arm inside `tests/test_reqharness_registry.py::test_derived_states_boundary_catalog` and `tests/test_reqharness_release.py::test_release_rules_and_verdicts`.
- **Numeric pass threshold:** both arms pass (exit 0).
- **Negative control:** M-RG4 — executed RED.
- **Boundary catalog:** ☑ boundary (withdrawn requirement)

### LLR-RH.5.3 — Review parse cache (content-keyed, pure accelerator, audit cache-off)
- **Traceability:** HLR-RH.5
- **Ledger:** LED-2026-10-11-reqharness-batch.2, LED-2026-10-11-reqharness-batch.6, LED-2026-10-11-reqharness-batch.29
- **Statement:** Review event files under `reqharness/reviews/` shall be treated as immutable once written (an append-only event store — a correction is a new event); the loader shall keep a LOCAL parse cache INSIDE `.git/reqharness-cache/` (never tracked; no `.git/info/exclude` write), keyed by sha256(file bytes) — read + hash, skip the parse; the cache shall cache PARSING only — every consumer re-validates each event's digest/role semantics before a cached parse can influence a derived state or the release verdict — and shall be a pure accelerator: deleting it changes no result; `--audit` shall run with the cache OFF and write nothing anywhere (the workspace digest is unchanged).
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_registry.py::test_review_parse_cache_is_pure_accelerator` (cache on/off derive equal states; a content-modified event re-parses by its new key; a poisoned cache entry and a corrupt cache file cannot change a verdict — both bounded to a re-parse; the large-registry fixture derives equal states cold and warm).
- **Numeric pass threshold:** `assert exit code 0`; 0 derived-state differences between cache-present and cache-deleted runs across the fixture set (100% equal); the audit fixture's workspace digest is identical before/after.
- **Negative control:** M-RG5 (cache feeds the verdict without re-validation) — executed RED.
- **Boundary catalog:** ☑ boundary (content-modified event file — new key, re-parsed) ☑ invalid (poisoned cache entry — bounded to a re-parse, never a verdict change) ☑ error (corrupt cache file — bounded to a re-parse / rebuild, never a verdict change — R26) ☑ boundary (large registry cold vs warm equality)

### LLR-RH.5.4 — Warm-cache derivation budget (P4 measurement)
- **Traceability:** HLR-RH.5
- **Ledger:** LED-2026-10-11-reqharness-batch.2, LED-2026-10-11-reqharness-batch.36
- **Statement:** With a warm parse cache, deriving all object states for 5 000 review events and 2 000 requirements shall complete in ≤ 0.5 s (median of 3 runs) on this machine; this budget is a P4 validation measurement, never a wall-clock assertion inside the test suite — the suite asserts only output equality (LLR-RH.5.3), and the measured figure is recorded in `04-validation.md` at P4.
- **Validation:** `analysis` (measured at P4; suite-side oracle is LLR-RH.5.3's equality assertion)
- **Executed verification:** P4 measurement transcript in `04-validation.md` (median of 3 warm-cache derivations over the 5 000-event / 2 000-requirement fixture, recorded with the command and its output).
- **Numeric pass threshold:** median ≤ 0.5 s over 3 runs at P4; 0 suite tests assert wall-clock.
- **Negative control:** none — a measurement, not a mechanism.
- **Boundary catalog:** none (a performance measurement over the §3.5 budget).

### LLR-RH.6.1 — Baseline freeze with commit SHA and dirty flag
- **Traceability:** HLR-RH.6
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.15, LED-2026-10-11-reqharness-batch.27, LED-2026-10-11-reqharness-batch.30
- **Statement:** `Baseline.create` shall snapshot objects (id, class, normative digest, state), the verified chain head, the review file set, the creation time, the repository's current commit SHA from a read-only `git rev-parse HEAD`, and `dirty: true|false` from read-only `git status --porcelain --no-optional-locks` — the dirty flag is taken ONLY here (R27a: `--audit` runs NO `git status`; the residual "baseline creation trusts the repo's `.git/config`" is stated in PDR §2.1), writing `reqharness/baselines/<name>.yml`; git tagging stays a manual act (P0 ruling O9); the dirty flag is recorded and refuses nothing.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_baseline.py::test_baseline_freezes_commit_sha_and_diffs`
- **Numeric pass threshold:** `assert exit code 0`; frozen `commit` equals the fixture repo's HEAD; frozen `dirty` equals the fixture's porcelain state on both a clean and a dirty tree.
- **Negative control:** M-BL1 (SHA omitted) · M-BL4 (dirty flag forced / porcelain skipped) — executed RED.
- **Boundary catalog:** ☑ boundary (dirty tree at freeze — recorded, refused nothing)

### LLR-RH.6.2 — Baseline diff classification over five classes
- **Traceability:** HLR-RH.6
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.15, LED-2026-10-11-reqharness-batch.16, LED-2026-10-11-reqharness-batch.27
- **Statement:** The diff shall classify each union id as `new` (absent from the baseline), `changed` (normative digest moved), `retired` (active → retired), `unchanged`, or `deleted` (in the baseline, absent from the canon — including a deleted review file via the baseline's review set), for both baseline-vs-baseline and baseline-vs-current comparisons, with the `dirty` flag recorded at freeze. The `reactivated` class (retired → active) and the review-state progression (reviewed in base → still reviewed / changed · review / pre-reviewed) are **deferred (B-125)** — round-2 ruling R24 trimmed this batch's classes to five plus the dirty flag; the ids stay in the glossary, marked, not deleted.
- **Validation:** `test (unit)` + `test (e2e)` (AT-081 through the CLI)
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_baseline.py::test_at_081_baseline_vs_now_reports_new_changed_retired`
- **Numeric pass threshold:** `assert exit code 0`; all five mutated fixture objects classify correctly through the real subprocess CLI (5/5).
- **Negative control:** M-BL2 (presence-only classification) · M-BL3 (`deleted` collapsed into `retired`) — executed RED.
- **Boundary catalog:** ☑ boundary (baseline vs now with new / changed / retired / deleted objects) ☑ boundary (dirty flag recorded, refused nothing)

### LLR-RH.7.1 — Release-rule evaluation with hard-coded mandatory rules
- **Traceability:** HLR-RH.7
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.3, LED-2026-10-11-reqharness-batch.7
- **Statement:** The evaluator shall apply the three hard-coded mandatory rules — chain verified, policy verified, every closing review signed by a role in force at its bound head — then AND every rule declared in `config.yml` (config may ADD rules, never remove the mandatory three); the verdict shall be `ready` or `not ready · <reason>`, with a broken chain, a policy mismatch, or an unknown recorded head yielding exactly `not ready · registry not verifiable`; an unentitled review alone shall NOT block the release; numeric thresholds shall be explicit per fixture.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_release.py::test_release_rules_and_verdicts`
- **Numeric pass threshold:** `assert exit code 0`; all fixture verdicts match byte-for-byte (5/5 fixtures: unreviewed, broken chain, policy mismatch, unentitled-alone, all-green).
- **Negative control:** M-RL1 (one rule unevaluated) — executed RED.
- **Boundary catalog:** ☑ error (broken chain / policy mismatch / unknown head) ☑ boundary (unentitled alone → evaluable) ☑ empty (0-object registry)

### LLR-RH.7.2 — Audit CLI (read-only, confined, cache-off, timed)
- **Traceability:** HLR-RH.7
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.6, LED-2026-10-11-reqharness-batch.10, LED-2026-10-11-reqharness-batch.16, LED-2026-10-11-reqharness-batch.17, LED-2026-10-11-reqharness-batch.29, LED-2026-10-11-reqharness-batch.30, LED-2026-10-11-reqharness-batch.34
- **Statement:** `mapper --audit <repo>` shall run headless: discover the connected repo with `git rev-parse --show-toplevel` (the `<repo>` argument overrides; `MapperApp(workspace)` is a maps dir — the repo is its containing work tree), load and verify the chain, derive states, evaluate release rules, print chain status + per-state counts (pre-reviews and unentitled counted separately) + verdict (+ `--baseline <name>` diff when given), and exit 0 on `ready`, 1 otherwise — with the parse cache OFF and without writing anything anywhere; `--audit` runs NO `git status` (the dirty flag is `Baseline.create`-only — R27a); a `safe.directory` refusal or ANY git non-zero exit (timeout included) yields the NAMED result `no repo` on both the screen and the audit report — never a crash, exercised by test (R27d); the branch runs AFTER the UTF-8 stdout re-wrap (so the report prints in UTF-8); an unknown or escaping repo path is refused before any file is read via `mapper.osopen.confine_reason`; the subprocess test uses a 60 s timeout.
- **Validation:** `test (e2e)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_release.py::test_at_080_audit_report_counts_every_state_exactly` and `tests/test_reqharness_release.py::test_audit_cli_refuses_escaping_repo_path` + the R27d node `test_safe_directory_refusal_is_named_no_repo_not_a_crash`
- **Numeric pass threshold:** `assert exit code 0` of the pytest nodes; subprocess exit codes {0,1} on the fixtures; stdout contains all three report sections; the subprocess completes within 60 s; the workspace sha256 digest is identical before/after; the `safe.directory` fixture prints the named result `no repo` and exits without a traceback.
- **Negative control:** M-AU1 (`--audit` ignored → TUI starts → `subprocess.run(timeout=60)` raises `TimeoutExpired`, counted as FAIL — R26) · M-AU2 (confinement after reading) · M-AU3 (a git non-zero raises instead of becoming `no repo` — R27d) — executed RED.
- **Boundary catalog:** ☑ invalid (repo path outside the allowed root / escaping symlink) ☑ boundary (no repo → the NAMED result `no repo`, headless and on screen — a `safe.directory` refusal lands here too, never a crash; R27d)

### LLR-RH.7.3 — Identity reader and the hardened git read-only allowlist
- **Traceability:** HLR-RH.7
- **Ledger:** LED-2026-10-11-reqharness-batch.13, LED-2026-10-11-reqharness-batch.22, LED-2026-10-11-reqharness-batch.23, LED-2026-10-11-reqharness-batch.30, LED-2026-10-11-reqharness-batch.32
- **Statement:** `mapper/reqharness/identity.py` shall read identity from repo-local `git config --get user.name` / `user.email`, falling back to global config; tests inject repo-local identity; the ONLY subprocesses the core may run are the read-only allowlist — reduced and hardened per R20 and R27: `git rev-parse --show-toplevel`, `git rev-parse HEAD`, `git config --get user.name|user.email` (the core and `--audit` run NO `git status` — the dirty flag is `Baseline.create`-only, R27a, whose stated residual is "baseline creation trusts the repo's `.git/config`"); `git` is resolved ONCE to an ABSOLUTE path by walking PATH itself — each directory that resolves to the audited repo, the current working directory, `.` or an empty entry is skipped (compared resolved), then `git` plus each PATHEXT extension is tried on Windows (PATHEXT fallback `.COM;.EXE;.BAT;.CMD`), plain `git` on POSIX, the first existing regular file wins — NOT `shutil.which` (before Python 3.12 it searches `.` on Windows regardless of `NoDefaultCurrentDirectoryInExePath` — review finding F4 HIGH), so a `git.exe` planted in the audited repo's cwd can never win — and every call is an argv list with `shell=False`, a 10 s timeout, the prefix `<abs git> --no-pager -c core.fsmonitor=false -c core.hooksPath=<os.devnull> -C <repo>` (a fixed `-c core.fsmonitor=false` disables fsmonitor under ANY filter name; `-c core.hooksPath=<os.devnull>` neutralises a repo's hooks path; `--no-pager` covers `core.pager`; `include.path`/`includeIf` only READ config, and `core.sshCommand`/`core.credential`/`core.diff.external` are not invoked by these read-only commands — R27b/c/H4), `GIT_OPTIONAL_LOCKS=0`, and inherited `GIT_DIR`/`GIT_WORK_TREE`/`GIT_CONFIG*` stripped (never `cwd=<repo>`); an argv-census arm asserts the executable is absolute; the committer-vs-reviewer email warning (a `git log` pass) is **deferred (B-124)** — `git log` is NOT in the allowlist; the ARCH amendment (§1 crossings + §2 module row naming `screens/roles.py`'s edge + §3 rules incl. the `osopen` inbound edge) is written in increment 1 (R19), not claimed earlier.
- **Validation:** `test (unit)` + `inspection` (allowlist census)
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_identity.py` + a source census over `mapper/reqharness/` for subprocess calls outside the allowlist + the R20/R27 fixtures: a repo whose `.git/config` sets `core.fsmonitor` to a sentinel command → the sentinel stays ABSENT after `--audit`; `.git/index` byte-identical after `--audit` (no `git status` runs at all in the audit path); a census of the exact argv shapes asserting the ABSOLUTE executable, the `-c core.fsmonitor=false -c core.hooksPath=<os.devnull>` pins and the `-C <repo>` form (no `cwd=<repo>`); a repo whose cwd carries a planted `git.exe` and an explicit PATH without it → resolution still finds the real git; a `safe.directory` refusal → the named result `no repo`, never a crash (with `test_safe_directory_refusal_is_named_no_repo_not_a_crash`).
- **Numeric pass threshold:** `assert exit code 0`; the census finds 0 non-allowlist `subprocess` calls; repo-local config beats global in the precedence fixture; the fsmonitor sentinel stays absent and `.git/index` is byte-identical after `--audit`; every argv census row carries an absolute executable.
- **Negative control:** M-ID1 (only the global config read) · M-ID2 (resolution honours a `git` on the repo cwd / a relative executable reaches the census — R27c) — executed RED.
- **Boundary catalog:** ☑ boundary (repo-local set / global fallback) ☑ boundary (committer-email mismatch warn — **deferred, B-124**; the `git log` allowlist row leaves with it) ☑ error (`safe.directory` refusal → named `no repo`, never a crash — R27d) ☑ invalid (planted `git.exe` in the audited repo's cwd never resolves — R27c)

### LLR-RH.8.1 — Screen bindings, matrix paint, genesis copy, door count
- **Traceability:** HLR-RH.8
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.16, LED-2026-10-11-reqharness-batch.17, LED-2026-10-11-reqharness-batch.28, LED-2026-10-11-reqharness-batch.29, LED-2026-10-11-reqharness-batch.30
- **Statement:** `RolesScreen` shall declare `KEY_SCOPE = SCOPE_ROLES` and `BINDINGS = screen_bindings(SCOPE_ROLES)`; the home screen shall offer the `R` door bound in the seat and the `screens/home.py` door row (owned by this increment) shall grow by exactly one entry; the matrix shall paint ● ◐ ◌ ○ using darkside glyph tokens and token colours only; the genesis event shall paint verbatim as `genesis — declared at registry creation`; the layout shall hold at 118 AND 87 columns; when no repo is discoverable (including a `safe.directory` refusal, R27d) the screen shall say so and offer nothing to edit.
- **Validation:** `test (e2e)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_roles_screen.py::test_at_077a_roles_screen_opens_from_home_and_paints_matrix`
- **Numeric pass threshold:** `assert exit code 0`; every seeded cell glyph present in the painted text at BOTH 118×34 and 87×34 (100% of cells); `duplicate_chords()` remains empty with the new seat rows; the home door list grows by exactly 1 — and the door-count regression checklist NAMES the existing home tests it guards (door count +1 — R26, named in round 3): the count assertion `tests/test_inc9c.py::test_inc9c_ux_f4_home_reads_its_labels_from_the_seat` (`len(doors) == 6` → 7), the bar-paint `tests/test_inc9e.py::test_inc9e_l3_the_home_bar_paints_the_doors_first`, the strip under a re-keyed seat `tests/test_inc9f.py::test_inc9f_r3_cr_f3_home_keeps_its_letters_and_active_mark_under_a_rekeyed_seat`, the dispatch of every home door row `tests/test_key_dispatch.py::test_at_n03g_each_key_dispatches_its_own_advertised_action`, and the pinned-seat census `tests/test_inc9.py::test_cd25_the_pinned_entry_seat_is_not_vacuous` + `tests/test_inc9.py::test_cd25a_the_seat_diff_is_exactly_what_inc9_declares` (the 6 home door rows of `ENTRY_ROWS` — the screen increment re-bases these pins with the `R roles` row, exactly one census declares the addition, the data-safety E-7 precedent).
- **Negative control:** M-RS1 (hard-coded glyph/hex) — executed RED.
- **Boundary catalog:** ☑ boundary (87-column layout) ☑ empty (no repo → nothing to edit — a `safe.directory` refusal lands here too, R27d)

### LLR-RH.8.2 — Propose semantics, pending glyphs and the read-only tamper state
- **Traceability:** HLR-RH.8
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.16
- **Statement:** `space` on a cell shall propose an add (◐) or remove (◌) inline; as admin on another person the proposal applies immediately through the chain append (LLR-RH.2.1); on oneself or as a non-admin it records a pending request (LLR-RH.2.2) and the on-disk `roles.yml` is unchanged; in a tampered or forked state the matrix shall be read-only — `space` inert, painting the read-only message.
- **Validation:** `test (e2e)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_roles_screen.py::test_at_078_non_admin_toggle_pends_admin_applies_in_one_key` (propose arms) and `::test_at_079_tampered_chain_paints_broken_state_and_blocks_release` (read-only arm).
- **Numeric pass threshold:** `assert exit code 0`; disk bytes unchanged after both pending paths; one event after the admin path; `space` writes nothing in the tampered state.
- **Negative control:** M-RS3 (admin self-toggle applies) · M-RS4 (tampered roles painted) — executed RED.
- **Boundary catalog:** ☑ boundary (sole-admin self-toggle pending) ☑ boundary (tampered read-only state — space inert + message)

### LLR-RH.8.3 — Footer status band detail
- **Traceability:** HLR-RH.8
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.16, LED-2026-10-11-reqharness-batch.29
- **Statement:** The roles screen footer shall always show: the chain event count, the head hash, the viewer identity (from the injected/repo-local git config), the pending detail (count + newest request), the chain status (`✓ verified` / `config changed without approval` / `chain forked at seq N`), and the release verdict word.
- **Validation:** `test (e2e)`
- **Executed verification:** band assertions inside `tests/test_roles_screen.py::test_at_077b_status_band_shows_chain_head_viewer_and_pending` and `::test_at_079_tampered_chain_paints_broken_state_and_blocks_release`.
- **Numeric pass threshold:** `assert exit code 0`; all six band elements present in verified, pending-bearing AND tampered states (6/6 each; the tampered-band assertion at 87 columns is OPTIONAL per R26 — marked, not silently dropped).
- **Negative control:** M-RS2 (band element dropped) — executed RED.
- **Boundary catalog:** ☑ boundary (tampered/forked state band — the 87-column tampered-band arm is optional, R26)

### LLR-RH.8.4 — Markup safety: Text sinks plus plain coercion
- **Traceability:** HLR-RH.8
- **Ledger:** LED-2026-10-11-reqharness-batch.1, LED-2026-10-11-reqharness-batch.12
- **Statement:** Every string painted by the roles screen that originated in a file under `reqharness/` (person names, ids, roles, notes, status words) shall be coerced through `darkside.plain` and painted ONLY into `rich.text.Text(...)` / `Text.append` sinks — never `Static(str)`, markup=True widgets, notify markup, or help text — so markup payloads render literally; `plain()` is a content-preserving coercion, not the safety mechanism (the sink is — R10).
- **Validation:** `test (e2e)`
- **Executed verification:** markup-payload arm of `tests/test_roles_screen.py::test_at_077c_file_derived_text_paints_through_text_sinks`.
- **Numeric pass threshold:** `assert exit code 0`; a `[bold]` payload in a person name paints literally in the captured screen text.
- **Negative control:** M-RS1b (raw string through a markup sink) — executed RED.
- **Boundary catalog:** ☑ invalid (markup payload in a name)

### LLR-RH.8.5 — Painting-sink, token/glyph and English-only censuses
- **Traceability:** HLR-RH.8
- **Ledger:** LED-2026-10-11-reqharness-batch.12, LED-2026-10-11-reqharness-batch.16
- **Statement:** A census test shall enforce: (a) no hex colour or glyph literal hard-coded in `screens/roles.py` (token oracle: monkeypatch a darkside token and assert the painted style changes); (b) no file-derived paint path bypassing the Text sinks of LLR-RH.8.4; (c) no non-ASCII letters in user-visible strings of `screens/roles.py` outside the sanctioned glyph set; (d) the "never yaml.load" census of LLR-RH.1.1 stays green.
- **Validation:** `test (e2e)`
- **Executed verification:** census arms of `tests/test_roles_screen.py::test_at_077c_file_derived_text_paints_through_text_sinks`.
- **Numeric pass threshold:** `assert exit code 0`; 0 census violations in each of the four arms; the token-monkeypatch arm observes a changed paint style.
- **Negative control:** M-RS1 (a hard-coded hex/glyph) · M-RS1b (a non-Text sink) — executed RED.
- **Boundary catalog:** ☑ invalid (injected census violation per arm)

### LLR-RH.8.6 — a/r pending resolution keys
- **Traceability:** HLR-RH.8
- **Ledger:** LED-2026-10-11-reqharness-batch.8, LED-2026-10-11-reqharness-batch.28
- **Statement:** On a pending request, `a` shall approve and `r` shall reject, landing a chain event that references the request's sha256 (the pending file is not deleted; the resolution is derived from the chain); resolution shall be admin-only and never one's own; a non-admin's `a` shall show exactly "a is unavailable (needs an admin)"; the resolution shall survive an app restart.
- **Validation:** `test (e2e)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_roles_screen.py::test_at_082_admin_resolves_pending_with_a_and_r`
- **Numeric pass threshold:** `assert exit code 0`; both resolutions land as chain events carrying the request hash; the non-admin message is byte-exact; the pending file remains on disk after resolution; the restart arm reopens the app and observes the derived resolution.
- **Negative control:** M-PR1 (non-admin resolution lands) — executed RED.
- **Boundary catalog:** ☑ boundary (own-request resolution refused) ☑ boundary (restart arm) ☑ invalid (non-admin `a`)

### LLR-RH.9.1 — D12 document content
- **Traceability:** HLR-RH.9
- **Ledger:** LED-2026-10-11-reqharness-batch.1
- **Statement:** The 06-docs document shall propose the ledger derivation: each 05-close human review ledger entry derived from registry review events, citing the batch's derived states, the precedence table, and the release-rule semantics (PDR §3.4) by id, and shall state that dev-flow adoption is outside this repository.
- **Validation:** `inspection`
- **Executed verification:** P6 gate inspection against PDR §3.4 and §7 (this document's row naming the D12 consumer).
- **Numeric pass threshold:** 0 unresolved findings.
- **Negative control:** none — document deliverable.
- **Boundary catalog:** none.

### Information Flow Contract (IFC) — C-54

- **Part A — flows:**

```text
FLOW: config-load
  SOURCE: reqharness/config.yml (YAML, CSafeLoader/SafeLoader; typed schema; email_sha256)
  - fn : config.py::load_config
    owner : LLR-RH.1.1
  - fn : canonical.py (NFC + canonical digest)
    owner : LLR-RH.1.3
  SINK: chain.py policy binding (LLR-RH.2.4) + release.py rule evaluator + derive.py class config

FLOW: role-chain
  SOURCE: reqharness/roles.yml (YAML multi-document stream; ≤ 4 MB; anchors/duplicate keys rejected)
  - fn : chain.py::verify
    owner : LLR-RH.3.1
  - fn : chain.py::effective_roles
    owner : LLR-RH.2.3
  - fn : osopen.confine_reason (R8 path confinement)
    owner : LLR-RH.3.1
  SINK: derive.py (roles in force at bound heads) · release.py (chain_verified, policy_verified) · RolesScreen footer band

FLOW: review-derivation
  SOURCE: REQUIREMENTS.md canon rows + reqharness/reviews/*.yml (immutable; content-named; parse cache .git/reqharness-cache/ — LLR-RH.5.3, parsing only)
  - fn : reviews.py canon/event readers
    owner : LLR-RH.4.1
  - fn : cache.py parse cache
    owner : LLR-RH.5.3
  - fn : derive.py state derivation
    owner : LLR-RH.5.1
  SINK: release.py (mandatory rules + config rules) · audit.py report · baselines

FLOW: pending-resolution
  SOURCE: reqharness/pending/*.yml (one file per request; content-named; exclusive create)
  - fn : pending.py pending store
    owner : LLR-RH.2.2
  - fn : chain.py resolution events
    owner : LLR-RH.8.6
  SINK: derive.py (resolved state from the chain) · RolesScreen pending detail

FLOW: identity
  SOURCE: git config (repo-local then global) · git rev-parse --show-toplevel / HEAD · git status --porcelain --no-optional-locks  (hardened read-only allowlist, R11/R20)
  - fn : identity.py git identity resolution
    owner : LLR-RH.4.4
  SINK: chain.py append path · baseline.py (commit, dirty) · audit.py report (the committer-mismatch WARN is deferred, B-124)

FLOW: baseline-diff
  SOURCE: reqharness/baselines/<name>.yml + current derivation + git rev-parse HEAD + git status --porcelain (read-only)
  - fn : baseline.py::create/diff
    owner : LLR-RH.6.1
  SINK: audit.py report (--baseline mode)

FLOW: audit-cli
  SOURCE: argv (--audit <repo> [--baseline <name>]); repo = git rev-parse --show-toplevel (D13)
  - fn : app.main audit branch (after the UTF-8 stdout re-wrap, so the report prints in UTF-8)
    owner : LLR-RH.7.2
  - fn : audit.py::audit (cache OFF, writes nothing)
    owner : LLR-RH.7.2
  SINK: stdout report + process exit code {0,1}

FLOW: roles-screen
  SOURCE: chain.py + derive.py + release.py + identity.py (in-memory domain objects)
  - fn : screens/roles.py RolesScreen (darkside.plain coercion into rich Text sinks ONLY — R10)
    owner : LLR-RH.8.1
  SINK: terminal canvas (rich Text via darkside tokens) and reqharness/roles.yml + reqharness/pending/ through the core's append APIs ONLY
```

- **Part B — boundary decomposition:** no — no component of the boundary is addressable on its own: the CLI, the screen, and the core are one process over one `reqharness/` directory; the only independently addressable surface is the file set itself, which the confinement rule (LLR-RH.7.2, reusing `osopen.confine_reason`) guards.

---

## 5. Validation strategy

### 5.1 Methods

> **Two layers** (per the Two-layer validation rule). Every batch declares BOTH:
> - **Layer A — white-box / functional (`TC-NNN`):** validates the HLR/LLR mechanism (the HOW). Methods: `test`, `inspection`, `analysis`.
> - **Layer B — black-box / behavioral acceptance (`AT-NNN`):** validates the user story's outcome through the shipped surface (the WHAT). Method: `acceptance`.

- **Layer A (test):** `tests/test_reqharness_config.py` · `tests/test_reqharness_chain.py` ·
  `tests/test_reqharness_registry.py` · `tests/test_reqharness_identity.py` ·
  `tests/test_reqharness_baseline.py` · `tests/test_reqharness_release.py` — every LLR-RH.* maps to at
  least one named node in these files (exact `file::test` ids in §3/§4 above). **Layer A (inspection):**
  LLR-RH.4.4 (identity ceiling), LLR-RH.7.3 (allowlist census), LLR-RH.9.1 (D12 document).
- **Layer B (acceptance):** AT-077a · AT-077b · AT-077c · AT-078 · AT-079 (roles screen increment 6a —
  matrix B, band detail, `space` propose semantics, read-only tamper state — driven with
  `MapperApp(tmp_path)` + `run_test(size=(118,34))` AND `(87,34)` + real
  `pilot.press` keys, helpers imported from `tests/test_draft_save.py`) · AT-082 (increment 6b — admin
  `a`/`r` resolution) · AT-083 (fork detection + exclusion on screen; recovery is core-only per R16/R25)
  · AT-080 · AT-081 (audit CLI,
  driven as a real subprocess through the console entry, `subprocess.run(timeout=60)`,
  `TimeoutExpired` counted as FAIL). Numbering verified at P1:
  highest pre-existing AT anywhere is AT-076 (premise 2); AT-082/AT-083 born at P1 iteration 1.
- Every AT/TC row in the PDR §5 names its reddening mutation; each increment's RED proof executes one.

### 5.2 Batch acceptance criteria

- 100% of LLRs (LLR-RH.1.1 … LLR-RH.9.1) covered by at least one test node with a pass result, or an
  inspection verdict at the gate that owns it (LLR-RH.4.4 at P2, LLR-RH.7.3 at its increment, LLR-RH.9.1 at P6).
- 0 blocker fails in validation; no requirement without an assigned validation method.
- Every user story (US-RH-001…003) has ≥1 passing black-box AT observing its outcome through the
  shipped surface, with boundary + negative evidence: US-RH-001 → AT-077a/b/c, AT-078, AT-079,
  AT-082, AT-083; US-RH-002 → AT-080 (exact per-state counts) + the LLR layer-0 nodes; US-RH-003 →
  AT-080/AT-081.
- Each increment lands with its RED proof: revert product change → new test FAILS → sha256-verified
  byte-identical restore → GREEN, transcript printed.
- The ARQ amendment (`reqharness` §1/§2/§3 rows + hardened git allowlist + osopen edge, R11/R19/R20) is
  written in increment 1, before the increments that rely on it are validated (staleness rule).

---

## 6. Appendices (optional)

### 6.1 Extended glossary
Mutation ids (each names ONE thing; no reuse): M-CF1 (genesis `prev_hash` altered) · M-CF2
(reviewer-role cross-check removed) · M-CJ1 (concatenation hashing) · M-EH1 (clear-text email) ·
M-P1 (policy hash check skipped) · M-CH1 (two-event path forced) · M-CH2 (self-approval allowed) ·
M-CH3 (hash recompute skipped) · M-CH4 (fork deduped by seq) · M-CH5 (the correct `<=` on
`roles_seq` flipped to `<` at the bound-head fold — R26) · M-HB1 (unknown bound heads accepted) ·
M-FR1 (resolve keeping the excluded child / naming the wrong sibling — R16) · M-FR2 (fork
child kept in authority — AT-083) · M-FR3 (verify walks by file position, not by `prev_hash` — R27) ·
M-FR4 (a `resolve` legitimates a chosen child that fails the approval rule at its own bound head —
R27) · M-LM1 (size limit skipped) · M-RG1 (informative folded into
normative) · M-RG2 (role checked at today's head) · M-RG3 (model reviews close) · M-RG4 (retired
counted active) · M-RG5 (cache feeds the verdict) · M-ID1 (only global config read) · M-ID2
(resolution honours a `git` on the repo cwd / a relative executable reaches the census — R27c) · M-FN1
(caller-supplied file names) · M-FN2 (sha8 content check skipped — R22) · M-BL1 (commit SHA omitted) ·
M-BL2 (presence-only classification) · M-BL3 (`deleted` collapsed into `retired`) · M-BL4 (dirty flag
forced) · M-RL1 (one rule unevaluated) · M-AU1 (`--audit` ignored → TUI starts →
`subprocess.run(timeout=60)` raises `TimeoutExpired`, counted as FAIL) · M-AU2 (confinement after
reading) · M-AU3 (a git non-zero raises instead of becoming the named `no repo` — R27d) · M-YC1 (a load routed through `yaml.load`) · M-PR1 (non-admin resolution lands) · M-RS1
(hard-coded colour/glyph) · M-RS1b (raw string through a markup sink) · M-RS2 (band element dropped)
· M-RS3 (admin self-toggle applies) · M-RS4 (tampered roles painted). Finding ids (round 1):
architect H1–H5/M1–M8/LOW-a…d; qa-reviewer QH1–QH4/QM1–QM11/QL1–QL5; security F1–F10. Finding ids
(round 2): architect A1–A7 (+ LOW probe items); qa-reviewer MED-1/MED-2/LOW-1…LOW-4; security G1
(+ LOW items). Rulings: R1–R14 + D13 + R15–R26 (all in `02-review.md` of this batch).

### 6.2 Relevant design decisions
`PDR-2026-10-11-reqharness-batch` §2.1 (threat model with the layer-3 residual) · §3.2 (hash chain +
policy binding + head binding + fork) · §3.3 (worked formats) · §3.4 (state + release semantics +
precedence) · §3.5 (performance) · §3.6 (identity allowlist) · §6 (rejected alternatives).

### 6.3 Open risks
Layer-3 residual: a full consistent rewrite of chain + every review + every recorded head by a writer
with repo access defeats the mechanism — stated in LLR-RH.4.4 and the PDR threat model; B-122 strong
mode (signed commits) and git anchoring of genesis are the named follow-ups (R2). Identity spoofing
ceiling (LLR-RH.4.4) · YAML merge conflicts on the append-only stream (fork fixture M-CH4/M-FR1 is the
degraded-mode guard, R7/R16) · canon parse drift (minimal reader; an unparseable row is reported, R14;
adapter follow-up) · scale: ruling R-SCALE + R4 answer the spike numbers (loader, immutability,
content-keyed cache, LLR-RH.5.4 P4 budget) — the R21 custom loader's speed cost is measured there
against the 0.5 s budget (the stated trade-off) · antivirus cold-scan on first file read (documented
observation ~60 s cold / ~9 s warm; the cache pays it once per new file) · **round-2 residuals (R23,
stated in the PDR threat model):** a deleted review is detected only against a baseline that listed
it; truncation of tail events no review or baseline has bound yet verifies clean (head binding covers
only bound heads); old-head binding (R17 — a revoked reviewer binds a new review to an older head;
`--audit` WARNS, layer 3 remains the strong answer); `reviewer` is free text (identity is git
config); `email_sha256` is pseudonymised personal data — unsalted, dictionary-reversible — and the
jurisdiction question goes to the operator · **round-3 residuals (R27, stated in the PDR threat
model):** baseline creation trusts the repo's `.git/config` (the dirty flag is `Baseline.create`-only;
`--audit` runs NO `git status`); a `safe.directory` refusal degrades to the named `no repo` result
rather than escalating.

### 6.4 Phase-1 reconciliation log — moved to the ledger (§7)
### 6.5 Requirement amendments — moved to the ledger (§7)

---

## 7. The ledger — authored as a SEPARATE FILE

The fence below is the ledger's seed: `devflow-init.py` writes it to `01-requirements-ledger.md`. The
shape of an entry is in the field guide. The live entries are
`LED-2026-10-11-reqharness-batch.1`…`.30` (`.1` initial authoring; `.2` R-SCALE; `.3`…`.16` rulings
R1–R14; `.17` ruling D13; `.18`…`.29` round-2 rulings R15–R26; `.30` round-3 ruling R27 — one entry
per ruling, grouped by ruling).

```markdown
# Requirements ledger — mapper — Batch 2026-10-11-reqharness-batch

> Append-only. Entries are added in chronological order and never rewritten. The live
> contract is `01-requirements.md`; this file records how it came to say what it says.
> Every entry names the requirement it amends; every requirement names its entries. `V26`
> compares the two sets of pairs both ways.

_No entries yet. The first amendment to the live contract writes the first one, in the
shape the field guide's §7 shows (`req-template.part2.md` in the guide directory init prints), and nothing
above this line is ever edited._
```
