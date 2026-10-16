# Requirements Document — mapper — Batch 2026-10-15-review-screen-batch

> **Artifact language.** English (`state.json` `language: en`). `shall` is the only normative keyword and appears only inside HLR/LLR statements.

> **Owed in.** `core` ✓ · `full` ✓

> **Reserved field names** (parsed literally, never translated):
> `Validation` · `Acceptance test(s)` · `Boundary catalog` · `Negative control` · `Premise evaluation` · `Fork preconditions` · `Ledger` · `Requirement` · `⏸ DEFER`

---

## 1. Introduction

### 1.1 Purpose
Derive the P1 contract for the ReqHarness REVIEW / SIGNING screen (B-134, prototype verdict 2026-10-15): variant A (list + detail) with variant C's queue as a "needs action" filter preset, two-key confirmed signing through a new headless `sign_review` orchestration, a fixed bottom release band, the informative-change badge (`⁂`), the screen's home door + keymap seat, and — per the operator's 2026-10-15 authorship decision (R6) — a self-review prohibition enforced both at the sign pre-flight and authoritatively in `derive`. Each requirement carries a testable threshold and a named negative control (mutant M-RS*).

### 1.2 Scope
In: `mapper/reqharness/signing.py` (new), `mapper/reqharness/config.py` (the `authors` map schema), `mapper/reqharness/derive.py` (the author rule + `owning batch` on the canon object), `mapper/reqharness/records.py` (`SigningRefused`), `mapper/reqharness/release.py` (the `authors_declared` rule + the `Derivation` field it needs), `mapper/screens/review.py` (new), the seat (`mapper/keymap.py`), the home door (`mapper/screens/home.py`) and the re-export (`mapper/app.py`), plus their tests. Out: the baseline/release VIEW screen, US canon + AT → test-node extraction, generated MD/HTML views, and B-124 (committer-vs-reviewer warning) · B-125 (baseline `reactivated`) · B-126 (fork-recovery UI) — each deferred, none needed by this screen.

### 1.3 Definitions, acronyms, abbreviations
| Term | Definition |
|------|------------|
| canon object | one HLR/LLR row of `REQUIREMENTS.md` (`derive.CanonObject`); the object of record |
| owning batch | the `Owning batch` column of the canon row — carried on `CanonObject.owning_batch`, it names the batch that owns the object |
| authors map | the admin-approved `authors` entry of `reqharness/config.yml`: owning-batch id → list of declared person ids |
| author | a person id listed, for an object's owning batch, in the `authors` map |
| derived state | the state `derive.derive_states` assigns: `reviewed` · `changed · review` · `pre-reviewed` · `not reviewed` · `retired` |
| designated role | the `reviewer_role` the config assigns an object's class (`config.yml` `classes`) |
| bound head | the `(roles_seq, roles_hash)` a review records; authority is read at it, never wall-clock (R2) |
| needs action | the open states `{changed · review, pre-reviewed, not reviewed}` — variant C's queue as a filter preset |
| informative mark | the `⁂` badge: `derive` raises `changed (informative)` when only an informative field changed (B-121 ruling 2) |
| facts | the `(top, who)` pair a git discovery returns, as in the roles screen |
| snapshot | the one immutable worker result the screen signs from: `(config, report, canon, derivation, release_verdict, object_id)` — read once, threaded through the entitlement check, the confirm comparison and the write |
| sign intent | what `b` arms: the object id, its current normative digest, the current head, and the snapshot — all captured together |
| SigningRefused | the named refusal exception (`records.SigningRefused`, a `ValidationError` subclass) carrying a stable reason code + message |

### 1.4 References
`spike/intake.md` (the core-gap census) · `PLAN.md` (P0; the R1–R5 orchestrator rulings) · `.dev-flow/2026-10-11-reqharness-batch` (B-119/B-121/B-122 rulings; the `reviews`, `derive`, `release`, `chain` core) · `.dev-flow/2026-10-11-fixes-batch` (the roles-screen thread-worker precedent, B-127) · `prototypes/review_screen/{NOTES.md,proto.py}` (the binding verdict + variant A copy) · `.dev-flow/BACKLOG.md` B-134.

### 1.5 Document overview
§2 context and the executed premise table · §3 five HLRs · §4 twelve LLRs and the Information Flow Contract · §5 validation · §6 appendices (open risks, the C1/C8 security answer, the Copy table) · ledger in `01-requirements-ledger.md`.

---

## 2. Overall description

### 2.1 Product perspective
The screen is a second consumer of the shipped ReqHarness core, beside the roles screen: it reads `derive` states and `release` verdicts and writes review events through `reviews.record_review` only — the same write path `derive`/`release` already consume (B4).

### 2.2 Product functions
List + detail review workbench; "needs action" filter preset; two-key confirmed signing; fixed bottom release band; informative-change badge; read-only under tamper/fork/no-registry; self-review forbidden (R6).

### 2.3 User characteristics
One operator in a terminal; a reviewer who holds one or more roles; a registry whose git may be slow.

### 2.4 Constraints
All strings English; colours from `mapper/darkside.py`; keys from `mapper/keymap.py`; never a hard-coded glyph or hex. At most 4 source files per increment. Registry text is untrusted (C8): painted only through `darkside.plain` into `rich.text.Text` sinks. `sign_review` has no CLI or entry-point exposure (no `console_scripts` entry, no `--sign` flag in `app.py`; only `screens/review.py` imports `signing`). No operator path, account name, home path, handle or noreply address in any file.

### 2.5 Assumptions and dependencies
The ReqHarness core (`config`, `chain`, `reviews`, `derive`, `release`, `identity`, `records`) is shipped and unchanged except where this batch amends it (`config.py` authors schema, `derive.py` author rule, `records.py` SigningRefused); the screen reuses the roles-screen thread-worker and paint conventions (`mapper/screens/roles.py`, HLR-RH.8); `MapperApp(tmp_path)` + `run_test` + `pilot.press` is the test driver, helpers imported from `tests/test_draft_save.py` and `tests/test_roles_screen.py`.

### 2.6 Source user stories

| ID | User Story | Source | DoR status |
|----|------------|--------|------------|
| US-RS-001 | As a reviewer, I want the review screen to show every canon object with its derived state and, for the selected object, who reviewed what at which chain head and digest, so that review state and the audit trail are one glance away. | B-134 (variant A) | READY |
| US-RS-002 | As a reviewer, I want `b` to show the content digest and chain head that will be signed and a second key to confirm, so that a keystroke never writes an immutable review record by accident. | B-134 (sub-ruling 2) | READY |
| US-RS-003 | As a reviewer, I want the screen to sign only when I hold the class's designated role at the current head and the chain verifies, and to say why otherwise, so that no keystroke can write a review I was not entitled to make, a review of a retired object, a review of an object I authored, or a review on a broken chain. | B-121 ruling 3 · B-122 ruling 2 · R1 · R6 | READY |
| US-RS-004 | As an operator, I want the review screen reachable from home by one key and its keys in the keymap seat, so that the door, the key bar and the legend never disagree. | B-134 · R4 | READY |

#### Refinement log (one block per story)

**US-RS-001 — review screen paints the derived registry**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = reviewer · outcome = a filterable object table (object · derived state · last review) with the "needs action" preset, a detail pane with full review history (WHO reviewed WHAT at WHICH head, digest ✓/✗, unentitled flagged apart), the `⁂` badge explained, and a fixed bottom release band · why = B-134 variant A (lookup + audit on one surface) · out of scope = B (board), C (as a screen), any baseline/release VIEW.
- **Feasibility (E, S):** path = read `derive.derive_states` + `release.evaluate` + `reviews.load_reviews`, paint as the prototype · unknowns = none (substrate shipped) · fits = yes.
- **Evaluability (T):** when the operator opens the review screen, the frame paints every canon object with its derived state and, on the selected object, its review history and the release band.
- **Open questions:** none.
- **Classification:** `READY`.

**US-RS-002 — two-key confirmed signing**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = reviewer · outcome = `b` paints the digest + head to be signed; only a second key (`enter`) writes through `sign_review` → `record_review` · why = a review record is immutable once written (content-named, exclusive create) · out of scope = editing a review (a correction is a new event).
- **Feasibility (E, S):** path = `b` arms a sign intent, `enter` calls `sign_review` with the confirmed intent; `sign_review` re-checks it (TOCTOU) · fits = yes.
- **Evaluability (T):** when the operator presses `b` then `enter`, the record appears and `derive` re-derives the object `reviewed`; when they press `b` and anything else, no record is written.
- **Open questions:** none (the second key is fixed as `enter` — decision recorded in the PLAN log).
- **Classification:** `READY`.

**US-RS-003 — entitlement, chain and authorship gates, every refusal named**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = reviewer · outcome = the sign path refuses (with the reason) unless the chain verifies, the viewer is declared, the viewer holds the designated role at the current head, the object is active, its class is declared, and the viewer is not an author of the object's owning batch; the screen is read-only under tamper/fork/no-registry with `b` inert and the reason shown · why = B-121 ruling 3 + B-122 ruling 2 + R1 + R6 (pre-write, named refusals, nothing written) · out of scope = strong mode (B-122 layer 3).
- **Feasibility (E, S):** path = `entitled_to_sign` + `sign_review`'s gates · fits = yes.
- **Evaluability (T):** when the viewer lacks the role or authored the object, `b`/`enter` refuses and writes nothing; when the chain is tampered, the screen is read-only and `b` is inert.
- **Open questions:** none.
- **Classification:** `READY`.

**US-RS-004 — home door and seat scope**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = operator · outcome = one key (`v`) from home opens the review screen; its keys come from the seat's new `review` scope and the door/legend/keybar agree · why = the seat is the single source (K3) · out of scope = any other screen's bindings.
- **Feasibility (E, S):** path = new `SCOPE_REVIEW` + `review-leave` group + door row; re-pin the census tests · fits = yes (the RH6a precedent; the seat lands in RS2, the screen+seat increment).
- **Evaluability (T):** when the operator presses `v` on home, the review screen opens and its key bar advertises the review-scope keys.
- **Open questions:** none (door key `v` free in the home scope — decision recorded).
- **Classification:** `READY`.

### 2.7 Premise evaluation (C-43) — MANDATORY, one row per premise

| # | Premise, as a truth-apt proposition | Tier | Verdict | Executed evidence (command output / `file:line` — **NOT** a citation of another document) | Disposition |
|---|---|---|---|---|---|
| 1 | The next free acceptance-test number is `AT-090`. | low | ✅ TRUE | `grep -rohE "\bAT-[0-9]+" .dev-flow/*/01-requirements.md tests/*.py \| sort -u \| tail -3` → `AT-087`, `AT-088`, `AT-089`; no `AT-090` or higher anywhere. New: `AT-090`…`AT-102`. | relied on (AT numbering) |
| 2 | `mapper/screens/review.py` and `mapper/reqharness/signing.py` do not exist; the `screens` row names its files literally and lacks `review.py`, while the `reqharness` row owns `mapper/reqharness/*.py` by glob. | low | ✅ TRUE | `ls mapper/screens/review.py mapper/reqharness/signing.py` → `No such file or directory` (both); `docs/ARCHITECTURE.md` §2 `screens` row lists 16 literal paths ending `home.py`, `roles.py` (no `review.py`); §2 `reqharness` row `Paths it owns` = `mapper/reqharness/*.py`. | relied on (ARQ F1; the map amendment lands in RS2) |
| 3 | The core already provides `record_review`, `next_seq`, `object_digests`, `load_canon`, `verify_chain().head` and `effective_roles` — the only primitives `sign_review` needs. | high | ✅ TRUE | `reviews.py:142` `record_review`, `:206` `next_seq`; `derive.py:178` `object_digests`, `:155` `load_canon`; `chain.py:144-150` `ChainReport.head`, `:285` `effective_roles`. | relied on (LLR-RS.2.1) |
| 4 | The review record's free-text `verdict` field is written as the literal `"reviewed"` and is not read by `derive`. | low | ✅ TRUE | `tests/test_reqharness_registry.py:142` (`verdict="reviewed"`, the shared `_record_review` helper); `derive.py` `derive_states` reads only `normative_digest`, `informative_digest`, `kind`, `reviewer`, `roles_seq`/`roles_hash` — no `verdict` read. | relied on (LLR-RS.2.1 fixes `verdict="reviewed"`) |
| 5 | The keymap seat binds no `v`, `b`, or `4` chord, and `enter` only in `list`/`nav`/`palette` — so the new door key and review-scope keys collide with nothing the review screen inherits. | low | ✅ TRUE | `grep -nE '"v"|"b"|"4"' mapper/keymap.py` → no hits; `grep -n '"enter"' mapper/keymap.py` → lines 165 (`list`), 173 (`nav`), 240 (`palette`) only. | relied on (LLR-RS.4.1) |
| 6 | `mapper/screens/roles.py` is the thread-worker + Text-sink precedent the review screen copies. | low | ✅ TRUE | `roles.py:522` `@work(thread=True)`, `:528` `on_worker_state_changed` (generation + `is_attached`), `:48` `darkside.plain` into `Text` sinks (the module docstring). | relied on (LLR-RS.1.4, LLR-RS.1.3) |
| 7 | `records.py` already defines `ValidationError` (and `YamlRefusal`), but no `SigningRefused` — the new refusal exception belongs there, beside `ValidationError`. | low | ✅ TRUE | `records.py:13` `ReqHarnessError`, `:17` `ValidationError(ReqHarnessError, ValueError)`, `:25` `YamlRefusal(ValidationError)`; no `SigningRefused` symbol anywhere (`grep -rn "SigningRefused" mapper/ tests/` → no hits). | relied on (LLR-RS.2.1 places `SigningRefused` in `records.py`) |
| 8 | `parse_canon` reads the `Owning batch` column but DROPS it, and `CanonObject` carries no `owning_batch` field — the R6 author rule needs it carried. | high | ✅ TRUE | `derive.py:148` (`if name not in ("id", "owning batch")`), `derive.py:71-79` (`CanonObject` fields `id, class_id, fields, line`). Load-bearing ABSENCE (C-55): the author rule's synthetic instance is a canon fixture whose row carries an `Owning batch` value. | relied on (LLR-RS.5.2 adds the field) |
| 9 | `config.py` `validate_config` does not reject duplicate person ids or duplicate `email_sha256`, and `roles.py:242` takes the first identity match — the m2 ambiguity gap. | high | ✅ TRUE | `config.py:290-301` (people loop — no uniqueness check; roles DO get one at `config.py:307`); `roles.py:242` (first match). Load-bearing ABSENCE (C-55). | relied on (LLR-RS.2.2 m2 arm; LLR-RS.5.1) |

- **Premise evaluation:** 9 premise(s) · ✅ TRUE 9 / ❌ FALSE 0 / ❓ UNDECIDABLE 0.

### 2.8 Fork preconditions (C-52) — MANDATORY, and the declared empty when the batch does not fork

| # | Condition (`C-52`) | Discharged? | The executed evidence |
|---|---|---|---|
| 1 | **Frozen contract** — no shared interface is touched inside a lane | ✅ | One lane. The seat change (RS2, screen + seat) is additive (new scope + door key); no existing `KeyBinding` moves. RS1's core edits are additive too (`config.py` gains `authors`; `derive.py` gains `owning_batch`; `records.py` gains `SigningRefused`). |
| 2 | **Disjoint FILE sets**, not just modules | ✅ | One lane; **RS1a — data** (`reqharness/reviews.py`, `reqharness/records.py`, `reqharness/config.py`, `reqharness/derive.py`), **RS1b — logic** (`reqharness/signing.py`, `reqharness/release.py`) and **RS2** (`screens/review.py`, `keymap.py`, `app.py`, `home.py`) touch disjoint files, sequentially (R18 re-split). |
| 3 | **Crossed reverse census** — family B per lane | ✅ | Premise 5's grep is the key census; §2 of the ARQ note enumerates the seat consumers; `grep -rln "ReviewScreen\|SCOPE_REVIEW" tests/` → no pre-existing hit. |
| 4 | **One owner of the trunk** | ✅ | This document, the ledger and `PLAN.md` are written only by the P1 unit. |

- **Fork preconditions:** none — this batch runs one lane (declared empty; the four conditions hold trivially, evidenced above).

---

## 3. High-level requirements (HLR)

### HLR-RS.1 — The review screen paints the derived registry, variant A
- **Traceability:** US-RS-001
- **Ledger:** LED-2026-10-15-review-screen-batch.1, LED-2026-10-15-review-screen-batch.4, LED-2026-10-15-review-screen-batch.6, LED-2026-10-15-review-screen-batch.9, LED-2026-10-15-review-screen-batch.10, LED-2026-10-15-review-screen-batch.13, LED-2026-10-15-review-screen-batch.19
- **Statement:** When the review screen is opened, the system shall paint a filterable table of every canon object — object id, derived state (read from `derive.derive_states`, never recomputed) and last review — beside a detail pane that, for the selected object, shows who reviewed what at which chain head with each recorded digest marked ✓ (matches the current normative digest) or ✗ (stale), unentitled reviews flagged apart, and the `⁂ changed (informative)` badge explained; the "needs action" filter preset shall list exactly the open states `{changed · review, pre-reviewed, not reviewed}`; and a fixed band at the bottom shall paint the release rules and verdict (from `release.evaluate`). The object table shall be the `ReviewList` widget, which shall not own `enter` (the screen owns `enter`). An empty canon shall paint the empty-canon text in the detail pane, not a blank panel. Under a tampered or forked chain, or with no registry, the screen shall paint every derived state as `not verifiable`, the release panel shall name the failing mandatory rules, and the screen shall be read-only with the reason shown.
- **Rationale (informative):** B-134 variant A is the only layout that answers both mandated questions — "every object with its derived state" and "who reviewed what at which head and digest" — on one surface; its filter subsumes variant C's queue. The release readiness is a registry-level fact, so it lives in a fixed band, not a layout opinion.
- **Validation:** `test`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_review_screen.py`
- **Numeric pass threshold:** 0 failed; every screen AT (AT-090…AT-102) passes at both `(118, 34)` and `(87, 34)`; the painted frame (not an `update()` argument) carries every canon object id, the derived-state words, and the release verdict text.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** the frame lists every canon object with its derived state and last review; the selected object's history shows digest ✓/✗ and unentitled reviews apart; the `⁂` badge is explained; the bottom band shows the release rules and verdict.
  - **Shipped surface:** the real app — `v` from home, `MapperApp(tmp_path)`, the screen's `ReviewList` and detail/band Statics.
  - **Acceptance test(s):** AT-090, AT-091, AT-092, AT-096, AT-099
  - **Boundary catalog (QC-3):** ☑ empty (no review events: `not reviewed`; no canon rows: the empty-canon text) ☑ boundary (retired object excluded; an informative mark on a reviewed object; a 2 000-object canon) ☑ invalid (unentitled human review counted apart) ☑ error (tampered/forked/no-registry → `not verifiable`)
  - **Negative control:** M-RS1 (states recomputed in the screen instead of read from `derive` — a wrong state is painted), M-RS2 (the "needs action" preset omits one open state), M-RS3 (a file-derived string painted without `darkside.plain`).

### HLR-RS.2 — Signing is two-key and writes through the core only
- **Traceability:** US-RS-002
- **Ledger:** LED-2026-10-15-review-screen-batch.1, LED-2026-10-15-review-screen-batch.2, LED-2026-10-15-review-screen-batch.9, LED-2026-10-15-review-screen-batch.11, LED-2026-10-15-review-screen-batch.12, LED-2026-10-15-review-screen-batch.17, LED-2026-10-15-review-screen-batch.20
- **Statement:** When the reviewer presses `b`, the system shall capture a sign intent — the object id, the current normative digest, the current head, and one worker snapshot — and show the digest and head that will be signed; only a second, distinct key (`enter`) shall write a review, through `sign_review`, which shall orchestrate `load_config` → `verify_chain` → `load_canon` → `object_digests` → the entitlement pre-flight → `next_seq` → `record_review`, and shall refuse — raising `SigningRefused` and writing nothing — on a broken/tampered/forked chain or no registry, an unknown or non-declared or ambiguous viewer, a viewer without the class's designated role at the current head, an unknown, retired or class-undeclared object, a viewer who is an author of the object's owning batch, or a confirmed object/digest/head that no longer equals the current ones (TOCTOU between `b` and `enter`).
- **Rationale (informative):** a review record is immutable once written (content-named, exclusive create; a correction is a NEW event), so the confirmation key is the only guard between a keystroke and a permanent record. R1: the sign path is a new headless `signing.py` leaf (it imports `derive`, which imports `reviews` — a cycle if it sat in `reviews.py`).
- **Validation:** `test`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_signing.py tests/test_review_screen.py`
- **Numeric pass threshold:** 0 failed; AT-093 drives `b` then `enter`, re-reads the file `sign_review` wrote, feeds it to `derive.derive_states`, and asserts the object derives `reviewed`; pressing `b` and then any other key writes no file; the record's `kind` is `human`, its `verdict` is `reviewed`, and its `note` is `""`; `sign_review` raises `SigningRefused` with a stable reason code on every refusal.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** `b` shows the digest + head and asks for confirmation; `enter` signs and the object re-derives `reviewed`; any other key after `b` writes nothing.
  - **Shipped surface:** the real app's `b`/`enter` keys → `sign_review` → the `reqharness/reviews/*.yml` file, re-read by `derive`.
  - **Acceptance test(s):** AT-093, AT-098, AT-100, AT-101
  - **Boundary catalog (QC-3):** ☑ boundary (confirm is a second key; `b` alone writes nothing; a cold `enter` writes nothing) ☑ error (TOCTOU: object/digest/head moved between `b` and `enter`) ☐ empty (n/a — there is always a selected object) ☐ invalid (n/a)
  - **Negative control:** M-RS4 (`b` writes directly, no confirm — a file appears after one key), M-RS5 (the TOCTOU re-check removed — a stale digest/head is signed).

### HLR-RS.3 — Only the designated role, at the current head, on a verified chain, signs
- **Traceability:** US-RS-003
- **Ledger:** LED-2026-10-15-review-screen-batch.1, LED-2026-10-15-review-screen-batch.2, LED-2026-10-15-review-screen-batch.3, LED-2026-10-15-review-screen-batch.7, LED-2026-10-15-review-screen-batch.12
- **Statement:** Before writing a review, the system shall verify that the chain is verified (not tampered, forked or absent), that the viewer is a known, declared person (exactly one declared person matching the git identity — zero or several shall be a named refusal), that the viewer holds the class's designated `reviewer_role` in the roles in force at the current head (one person may hold several roles), that the object exists, is active (not withdrawn/retired) and its class is declared, and that the object, digest and head the operator confirmed still equal the current ones; each failure shall be a named refusal that writes nothing. A model review shall never be written by this path; model reviews remain pre-review in `derive`.
- **Rationale (informative):** B-121 ruling 3 (only the designated role marks reviewed) + B-122 ruling 2 (release blocks on a broken chain) + R1 (all refusals named, pre-write, nothing written). The residual that the screen is read-only under fork (recovery is core-only, B-126) is inherited from the roles-screen precedent.
- **Validation:** `test`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_signing.py tests/test_review_screen.py`
- **Numeric pass threshold:** 0 failed; `entitled_to_sign` returns `(False, <named reason>)` for each of: tampered chain, forked chain, no registry, unknown viewer id, ambiguous viewer (several matches), viewer without the role, unknown object id, retired object, class-undeclared object, author-of-batch; `sign_review` writes nothing in each; AT-094, AT-095 and AT-102 pass.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** a viewer without the role, a retired object, an author-of-batch viewer, or a broken chain each refuse with the reason on the hint line and write nothing; the tampered screen is read-only.
  - **Shipped surface:** the real app's `b` key and hint line; the `reqharness/reviews/` directory (byte count unchanged).
  - **Acceptance test(s):** AT-094, AT-095, AT-102
  - **Boundary catalog (QC-3):** ☑ boundary (one person, several roles — any one suffices) ☑ invalid (retired object; unknown object id; undeclared viewer; no git identity) ☑ error (tampered; forked; no registry) ☐ empty (n/a)
  - **Negative control:** M-RS6 (the role check dropped — an unentitled viewer signs), M-RS7 (the active check dropped — a retired object signs), M-RS8 (the chain check dropped — a tampered chain signs).

### HLR-RS.4 — The review screen has a home door and a keymap scope
- **Traceability:** US-RS-004
- **Ledger:** LED-2026-10-15-review-screen-batch.1, LED-2026-10-15-review-screen-batch.5, LED-2026-10-15-review-screen-batch.8, LED-2026-10-15-review-screen-batch.19
- **Statement:** The keymap seat shall declare a new `review` scope (with a `review-leave` leave group) and one home door key (`v`); the home screen shall paint that door and open the review screen from it; and `mapper.app` shall re-export `ReviewScreen`; the door's key and name shall be the seat's, so the door, the key bar, the palette and the legend never disagree.
- **Rationale (informative):** the seat is the single source for chords (US-N03 / K3); the door and scope land in the screen+seat increment (RS2), so the guarded census pins move once and itemised.
- **Validation:** `test`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_keymap.py tests/test_key_dispatch.py tests/test_review_screen.py`
- **Numeric pass threshold:** 0 failed; AT-097 opens the screen by `v` from home and asserts the key bar advertises the review-scope keys; `test_at_n03a_every_binding_resolves_to_a_real_action` and `test_at_n03f_bound_keys_match_the_seat_exactly` pass with the new scope; `test_key_dispatch.py`'s whole-seat count pin re-baselines.
- **Priority:** medium
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** pressing `v` on home opens the review screen, whose key bar advertises exactly the review-scope keys.
  - **Shipped surface:** the real app — home screen door, the review screen's key bar.
  - **Acceptance test(s):** AT-097
  - **Boundary catalog (QC-3):** ☑ boundary (the door key `v` is free in the home scope) ☐ empty (n/a) ☐ invalid (n/a) ☐ error (n/a)
  - **Negative control:** M-RS16 (the door row dropped from the seat — `v` opens nothing; the census pin fails).

### HLR-RS.5 — Self-review is forbidden; authorship per owning batch in config
- **Traceability:** US-RS-003
- **Ledger:** LED-2026-10-15-review-screen-batch.7, LED-2026-10-15-review-screen-batch.15, LED-2026-10-15-review-screen-batch.17, LED-2026-10-15-review-screen-batch.20, LED-2026-10-15-review-screen-batch.21, LED-2026-10-15-review-screen-batch.22
- **Statement:** The system shall forbid self-review: the config shall declare an admin-approved `authors` map (owning-batch id → list of declared person ids), part of `config_hash` so a change needs an approved `policy` event; `entitled_to_sign` shall refuse — with a named reason — when the signer's person id is listed as an author of the object's owning batch; and `derive` shall apply the same rule authoritatively, counting a human review whose reviewer is an author of the object's owning batch as `unentitled` (never `reviewed`), so a hand-written record cannot bypass the screen. A batch with no `authors` entry — or an object whose `Owning batch` cell is blank — shall mean authorship not recorded, and signing shall be allowed; `create_registry` shall seed new registries with an empty `authors` map and the release rule `authors_declared` ENABLED, which fails when an active object's owning batch is blank or absent from `authors` (F2). Residual (F3): an admin-author can approve their own `authors` change (self-approved policy) — stated, and carried as B-135. Residual (F4): one human declared twice with two emails.
- **Rationale (informative):** the operator's 2026-10-15 decision (R6) overrides the earlier "no self-review rule" open question (R2): self-review is forbidden now. The canon row's existing `Owning batch` column gives each object its batch, so authorship is recorded per batch, not per object.
- **Validation:** `test`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_signing.py tests/test_reqharness_registry.py tests/test_review_screen.py`
- **Numeric pass threshold:** 0 failed; `entitled_to_sign` refuses a declared author of the object's batch by name; `derive.derive_states` marks an author's hand-written human review `unentitled` (the object never derives `reviewed`); `validate_config` refuses an `authors` entry naming an unknown person id; `create_registry` seeds `authors: {}` + `authors_declared` ENABLED, and the rule fails when an active object's batch has no `authors` entry.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** an author-of-batch viewer pressing `b`/`enter` sees the named refusal on the hint line and writes nothing.
  - **Shipped surface:** the real app's `b`/`enter` keys and hint line.
  - **Acceptance test(s):** AT-102
  - **Boundary catalog (QC-3):** ☑ boundary (a batch with no `authors` entry → signing allowed) ☑ invalid (author-of-batch viewer; `authors` naming an unknown person) ☑ error (n/a) ☐ empty (n/a)
  - **Negative control:** M-RS18 (the author rule dropped from `derive` — a hand-written author review derives `reviewed`), M-RS19 (the author check dropped from `entitled_to_sign` — an author signs through the screen).

---

## 4. Low-level requirements (LLR)

### LLR-RS.1.1 — The `ReviewList` reads derived states and the filter has a "needs action" preset
- **Traceability:** HLR-RS.1
- **Ledger:** LED-2026-10-15-review-screen-batch.1, LED-2026-10-15-review-screen-batch.4, LED-2026-10-15-review-screen-batch.13, LED-2026-10-15-review-screen-batch.19
- **Statement:** The `ReviewScreen` shall build its object list — a `ReviewList` widget — from `derive.derive_states` (`Derivation.states`, `informative_marks`, `unentitled`, `pre_reviewed`, `reported`) and `reviews.load_reviews` — never by re-deriving — and shall paint columns `object` · `derived state` · `last review`; the filter key shall cycle `all → needs action → reviewed → changed · review → pre-reviewed → not reviewed → retired`, where `needs action` selects exactly the open states `{changed · review, pre-reviewed, not reviewed}` and a state column cell for an object carrying the informative mark shall append the `⁂` badge. `ReviewList` shall not bind `enter`: the screen owns `enter`, so a cold `enter` (not armed) shall write nothing and take no other action. An empty canon shall paint the empty-canon text, not a blank panel.
- **Validation:** `test (integration)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_review_screen.py::test_at_090_review_screen_opens_from_home_and_paints_the_registry tests/test_review_screen.py::test_at_091_needs_action_filter_preset_lists_only_open_objects tests/test_review_screen.py::test_at_098_cold_enter_does_nothing`
- **Numeric pass threshold:** 0 failed; the painted frame lists every canon object id and its `derive` state word; cycling to `needs action` shows 0 objects whose state is `reviewed` or `retired` and all three open states (`changed · review`, `pre-reviewed`, `not reviewed`) are present in the fixture; a fixture with an informative mark paints `⁂` on that object's state cell; a cold `enter` writes 0 files and changes no painted surface. At 87×34 the ATs assert per scroll window (scroll and assert each window); the full 10-object fixture arm runs at 118 (Q3).
- **Negative control:** M-RS1 (recompute the state in the screen) and M-RS2 (the preset misses `pre-reviewed`) — each executed RED at RS2.
- **Boundary catalog:** ☑ empty (no canon rows: the empty-canon text, no crash) ☑ boundary (retired object; informative mark) ☑ invalid (unentitled review) ☐ error (n/a)

### LLR-RS.1.2 — The detail pane shows the review history and the bottom band the release verdict
- **Traceability:** HLR-RS.1
- **Ledger:** LED-2026-10-15-review-screen-batch.1, LED-2026-10-15-review-screen-batch.4, LED-2026-10-15-review-screen-batch.13, LED-2026-10-15-review-screen-batch.19
- **Statement:** The detail pane shall paint, for the selected object, each review event as `#N <time> <reviewer> (<kind>) head <seq>:<hash>` with the recorded digest marked ✓ (equal to the current normative digest) or ✗ (stale — content changed), human reviews whose signer held no designated role at their bound head flagged apart as unentitled, and, when `derive` raises the informative mark, a line explaining `⁂ changed (informative)`; the fixed bottom band shall paint the release rules and the exact verdict text from `release.evaluate` (with the mandatory rules named on the not-verifiable arm). With an empty canon the detail pane shall paint the empty-canon text, and with no review event for the selected object it shall paint the empty-history text.
- **Validation:** `test (integration)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_review_screen.py::test_at_092_detail_pane_shows_history_digest_verdicts_and_informative_badge`
- **Numeric pass threshold:** 0 failed; a fixture with a stale-digest review and a model review paints the stale digest `✗`, the model review `(model)`, and the informative badge line; the band carries `verdict` from `release.evaluate` — byte-equal to `VERDICT_READY` or `not ready · <reason>` as the fixture dictates (two fixtures, ready / not ready, each asserted equal to `release.evaluate(...).text` — Q8).
- **Negative control:** M-RS9 (a stale digest painted `✓`) and M-RS10 (the band verdict hard-coded instead of read from `release.evaluate`).
- **Boundary catalog:** ☑ boundary (model review; unentitled human review) ☑ empty (no review event: the empty-history text; no canon rows: the empty-canon text) ☑ error (tampered: derived states suspended) ☐ invalid (n/a)

### LLR-RS.1.3 — File-derived text paints through `darkside.plain` into `Text` sinks, truncated by cell width, at 118 and 87 columns
- **Traceability:** HLR-RS.1
- **Ledger:** LED-2026-10-15-review-screen-batch.1, LED-2026-10-15-review-screen-batch.4, LED-2026-10-15-review-screen-batch.13, LED-2026-10-15-review-screen-batch.16, LED-2026-10-15-review-screen-batch.19
- **Statement:** Every file-derived string — object id, class id, reviewer, note, digest, head hash, status word — shall be coerced through `darkside.plain` and painted only into `rich.text.Text` sinks (table cells, detail lines, band lines, hint); no `Static(str)` with markup, no interpolated raw text into a markup-parsed string, and no hard-coded glyph or hex colour; long ids and digests shall truncate by CELL WIDTH (never by `len` of the Python string) with the ellipsis; a long `<object>` or `<viewer>` in the armed hint shall elide the MIDDLE (cell-width aware, `…`) so the tails `enter confirms, any other key cancels` and `press b to re-arm` are never cut (U1); the screen shall render without wrapping at both `(118, 34)` and `(87, 34)` for every screen AT (87 renders are scroll-trimmed), and the fixed band shall never reflow; and the screen shall paint NO string outside the §6.6 table ∪ the approved-prototype set (U4).
- **Validation:** `test (integration)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_review_screen.py::test_at_096_screen_paints_file_derived_text_through_text_sinks_only tests/test_review_screen.py::test_at_103_armed_hint_elides_the_middle_and_keeps_the_tail tests/test_review_screen.py::test_at_105_screen_paints_no_string_outside_the_copy_table_or_prototype`
- **Numeric pass threshold:** a hostile registry (object id and reviewer name built with `chr()` — ESC, U+202E, U+200B, NEL, wide CJK, combining, and the markup brackets `[bold]x[/]` / `[/]`) paints those bytes literally with no ESC byte and no style span derived from the payload (C-56/C-8); the painted frame at `(87, 34)` carries the release band with no wrap. Surrogates are never planted (they cannot exist in UTF-8). AT-103 arms the longest id at 87 and asserts the tail `enter confirms, any other key cancels` is present; AT-105 asserts every painted literal is a member of §6.6 ∪ the prototype set.
- **Negative control:** M-RS3 (one file-derived string painted without `darkside.plain`), M-RS11 (a `Text` sink swapped for a markup `Static(str)`), M-RS31 (the elision cuts the tail instead of the middle — the `enter confirms` tail is cut at 87), M-RS30 (a string painted outside §6.6 ∪ the prototype set) — each executed RED.
- **Boundary catalog:** ☑ invalid (ESC / U+202E / U+200B / NEL / wide CJK / combining / markup-bracket payload) ☑ boundary (long id truncated with ellipsis by cell width; the longest id armed at 87) ☐ empty (n/a) ☐ error (n/a)

### LLR-RS.1.4 — All disk and git work runs in one thread worker, returning one immutable snapshot
- **Traceability:** HLR-RS.1
- **Ledger:** LED-2026-10-15-review-screen-batch.1, LED-2026-10-15-review-screen-batch.4, LED-2026-10-15-review-screen-batch.9, LED-2026-10-15-review-screen-batch.16, LED-2026-10-15-review-screen-batch.18, LED-2026-10-15-review-screen-batch.19
- **Statement:** The `ReviewScreen` shall run ALL disk/git work in a Textual thread worker started at mount and resume (the `roles.py` pattern): `identity.repo_root`, `identity.read`, `verify_chain`, `load_canon`, `derive.derive_states` and `release.evaluate` — returning ONE immutable snapshot (`config`, `report`, `canon`, `derivation`, `release_verdict`) — and shall apply it on the UI thread in `on_worker_state_changed` only when the worker state is SUCCESS and after the generation and `is_attached` checks; the thread shall be recorded per call (so a test can assert each call ran off the UI thread). The sign worker (A7) shall run the identity re-read and the chain re-verify INSIDE itself (not on the UI thread), call `sign_review` (a disk write), and hand its result back through the SAME generation + `is_attached` guard; a successful sign shall bump the generation and re-run the snapshot worker (output-then-consume). While the screen is loading, the key bar shall advertise only `escape`; every other key (`up`, `down`, `4`, `b`, `enter`) shall be inert while `escape` keeps its action; a tampered, forked or no-registry result shall paint the read-only state with its reason and make `b` inert (and hide `b` from the key bar) with that reason (U3).
- **Validation:** `test (integration)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_review_screen.py::test_at_095_tampered_or_forked_chain_is_read_only_with_the_reason tests/test_review_screen.py::test_at_107_worker_runs_all_disk_and_git_work_off_thread`
- **Numeric pass threshold:** with a gated `identity._run_git` the git calls are recorded off the main thread; `verify_chain`/`load_canon`/`derive_states`/`release.evaluate`/`sign_review` are each recorded on a worker thread, patched where the screen looks them up, asserting a NON-EMPTY record (thread name/identity differs from the UI thread per call — Q9); with the gate closed the painted surfaces are empty and the key bar advertises only `escape`; a late result on a popped screen is discarded (no paint, no notification, no exception — M-RS13); a tampered chain paints `not verifiable` and `b` writes 0 bytes.
- **Negative control:** M-RS12 (discovery run synchronously on mount), M-RS13 (the generation/`is_attached` guard dropped — a late result on a dead screen paints), M-RS28 (the disarm-before-worker removed — a second `enter` while the sign worker runs writes a second record).
- **Boundary catalog:** ☑ empty (no repo) ☑ boundary (screen popped before the worker returns) ☑ error (tampered/forked chain) ☐ invalid (n/a)

### LLR-RS.1.5 — The list scrolls 2 000 objects with the cursor kept in view and a bounded repaint
- **Traceability:** HLR-RS.1
- **Ledger:** LED-2026-10-15-review-screen-batch.10, LED-2026-10-15-review-screen-batch.15, LED-2026-10-15-review-screen-batch.18, LED-2026-10-15-review-screen-batch.19
- **Statement:** The `ReviewList` shall be a line-based `ScrollView` with a `render_line` method (A6) that binds NO keys, and it shall scroll so the cursor row stays in view: on a 2 000-object canon fixture, after 1 999 `down` presses the selected object id shall be in the painted frame; the bottom release band shall remain on the last rows. `ReviewList` shall bind NO `enter` (the screen owns it): the widget exposes the navigation rows and the cursor, never a confirmation action. A repaint after a cursor move shall paint a constant, cursor-sized window of rows — the counted-operations bound is the number of `render_line` calls per cursor move (Q4), which shall NOT grow with N — and the wall-clock repaint (≤ 50 ms, median of 5) shall be measured and recorded at P4 as a MEASUREMENT ONLY, never asserted in the suite (a tight wall-clock assertion is flaky and is forbidden).
- **Validation:** `test (integration)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_review_screen.py::test_at_099_two_thousand_objects_scroll_with_the_cursor_in_view`
- **Numeric pass threshold:** 0 failed; the selected id is in the painted frame after 1 999 `down`; the band paints the last rows; the suite asserts the counted-operations bound — the number of `render_line` calls of a single cursor-move repaint is constant across N (1 000 vs 2 000 objects), not proportional to N; the P4 transcript records the measured median repaint (≤ 50 ms) as a measurement only.
- **Negative control:** M-RS20 (the follow-the-cursor scroll removed — after 1 999 `down` the selected id is not in the frame), M-RS26 (`ReviewList` binds `enter` — a cold `enter` on the widget fires a second action the screen never asked for), M-RS27 (`render_line` repaints all N rows per move — the `render_line` call count grows with N).
- **Boundary catalog:** ☑ boundary (2 000 objects; the last row) ☐ empty (n/a — empty canon is AT-090's arm) ☐ invalid (n/a) ☐ error (n/a)

### LLR-RS.2.1 — `sign_review` orchestrates the core, returns the written `Path`, and raises `SigningRefused`
- **Traceability:** HLR-RS.2
- **Ledger:** LED-2026-10-15-review-screen-batch.1, LED-2026-10-15-review-screen-batch.2, LED-2026-10-15-review-screen-batch.11, LED-2026-10-15-review-screen-batch.15, LED-2026-10-15-review-screen-batch.17, LED-2026-10-15-review-screen-batch.18, LED-2026-10-15-review-screen-batch.19, LED-2026-10-15-review-screen-batch.23, LED-2026-10-15-review-screen-batch.20, LED-2026-10-15-review-screen-batch.21
- **Statement:** `sign_review(repo, object_id, identity_email, *, confirm_digest, confirm_head, confirm_owning_batch, now=None)` shall call `load_config`, `verify_chain` (refuse when `report.ok` is False, naming the status), refuse unless `config_digest(config) == report.policy_config_hash` (reason code `unapproved_config`, F6), `load_canon`, resolve the object (refuse an unknown id), compute `object_digests`, run the entitlement check (refuse with its reason), compare `confirm_owning_batch`/`confirm_digest`/`confirm_head` to the current object, digest and `report.head` and re-check the role-at-head against the current snapshot (refuse on any mismatch with a named reason code — `moved_object` · `moved_digest` · `moved_head` · `moved_role`, checked in THAT order; precedence: an object gone is `unknown_object`, a revoke that loses the role is `moved_role` else `moved_head`), then `next_seq` and `record_review` with `class_id` from the canon object (not the id prefix), `verdict="reviewed"`, `kind="human"`, `note=""`, `reviewer=viewer`, the object's owning batch stored as `owning_batch` (F1), and the current head — returning the written `Path`. `now=None` shall mean UTC now (`datetime.now(timezone.utc)`), and tests shall pass a fixed `now` to freeze the clock. On any refusal the function shall raise `records.SigningRefused` (a `ValidationError` subclass) carrying a stable reason code + message, and write nothing; the loader `ValidationError`s (`verify_chain`, `load_config`, `load_canon`) shall be converted to `SigningRefused`/`(False, code)` via `release.safe_verify` or equivalent — never a bare exception into the worker (A4). The role/author decision runs on the same snapshot through a pure `_entitlement` helper (one load of `safe_verify`/`load_config`/`load_canon` per sign), and the review store's typed refusals (`ReviewLimitError`, `AlreadySignedError`) map to `review_limit`/`already_signed` by type.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_signing.py::test_sign_review_writes_a_record_that_derive_reads_as_reviewed tests/test_reqharness_signing.py::test_sign_review_refuses_on_tampered_or_forked_or_no_registry tests/test_reqharness_signing.py::test_sign_review_freezes_the_clock_via_now tests/test_reqharness_signing.py::test_sign_review_refuses_an_unapproved_config`
- **Numeric pass threshold:** the returned path exists; `derive.derive_states` over the re-read scan derives the object `reviewed` (B4 output-then-consume); each refusal raises `SigningRefused` with a reason code and writes nothing; the record's `kind == "human"`, `verdict == "reviewed"`, `note == ""`, `class_id` equals the canon object's `class_id` (a canon id whose prefix differs from its class still writes the canon `class_id`), and `owning_batch` equals the object's owning batch at sign time; a fixed `now` appears verbatim in the record's `time`; `config_digest(config) != report.policy_config_hash` raises `SigningRefused` with `unapproved_config` and writes nothing.
- **Negative control:** M-RS5 (the TOCTOU re-check removed), M-RS14 (an unknown object id coerced instead of refused), M-RS29 (the `unapproved_config` check removed — an unapproved config is signed) — each executed RED.
- **Boundary catalog:** ☑ error (tampered/forked/no-registry) ☑ invalid (unknown object id) ☑ boundary (record at the current head) ☐ empty (n/a)

### LLR-RS.2.2 — `entitled_to_sign` is the one pre-flight predicate, with a 10-arm truth table
- **Traceability:** HLR-RS.3, HLR-RS.5
- **Ledger:** LED-2026-10-15-review-screen-batch.1, LED-2026-10-15-review-screen-batch.2, LED-2026-10-15-review-screen-batch.7, LED-2026-10-15-review-screen-batch.12, LED-2026-10-15-review-screen-batch.15, LED-2026-10-15-review-screen-batch.18, LED-2026-10-15-review-screen-batch.19, LED-2026-10-15-review-screen-batch.23
- **Statement:** `entitled_to_sign(repo, object_id, identity_email) -> (bool, reason)` (A3: it takes the git IDENTITY email, hashes it and resolves to EXACTLY ONE declared person inside `signing`) shall return `(True, "")` only when the chain verifies, the identity resolves to exactly one declared person (zero or several → named refusal), the object exists, is ACTIVE (not withdrawn/retired) and its class is declared, the resolved viewer holds the class's `reviewer_role` in `effective_roles(report)` at the current head (one person may hold several roles), and the viewer is NOT an author of the object's owning batch; otherwise it shall return `(False, <named reason>)` naming exactly the failing check, and it shall write nothing. An object whose `Owning batch` cell is blank — like a batch with no `authors` entry — shall mean authorship not recorded, so no author refusal applies and signing is allowed on that ground.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_signing.py::test_entitled_to_sign_requires_the_designated_role_at_the_current_head tests/test_reqharness_signing.py::test_entitled_to_sign_truth_table_includes_retired_and_class_undeclared tests/test_reqharness_signing.py::test_entitled_to_sign_refuses_an_author_of_the_object_batch`
- **Numeric pass threshold:** 0 failed; a truth table of 10 `(False, reason)` arms — tampered/forked/no-registry/unknown-viewer/ambiguous-viewer/no-role/unknown-object/retired/class-undeclared/author-of-batch — each arm a SINGLE-failure fixture, plus `(True, "")` for the entitled case (including a person holding two roles, one of which is the designated one), and `(True, "")` for a blank-`Owning batch` object whose signer is otherwise entitled.
- **Negative control:** M-RS6 (role check dropped), M-RS7 (active/retired check dropped), M-RS8 (chain check dropped), M-RS19 (author check dropped).
- **Boundary catalog:** ☑ boundary (several roles) ☑ invalid (retired object; unknown object; class-undeclared object; ambiguous viewer) ☑ error (tampered/forked/no-registry) ☐ empty (n/a)

### LLR-RS.2.3 — `b` arms a sign intent; only `enter` writes; the intent is re-checked and cancellable
- **Traceability:** HLR-RS.2
- **Ledger:** LED-2026-10-15-review-screen-batch.1, LED-2026-10-15-review-screen-batch.2, LED-2026-10-15-review-screen-batch.9, LED-2026-10-15-review-screen-batch.13, LED-2026-10-15-review-screen-batch.14, LED-2026-10-15-review-screen-batch.15, LED-2026-10-15-review-screen-batch.16, LED-2026-10-15-review-screen-batch.17
- **Statement:** The `ReviewScreen` shall, on `b`, capture a sign intent — `object_id`, the current normative digest, the current head, and the one worker snapshot — and paint the digest (as `<sha8>`) and head on the hint line in the `darkside` ACCENT token, with the armed row in the list marked in the same token (U2); only `enter` in the armed state shall sign: `enter` shall DISARM on the UI thread first, then start the sign worker (F5), which re-reads the identity and re-verifies the chain and canon inside itself (A7) and calls `sign_review` with that intent, refusing (via the refusal shown on the hint line in the roles-screen ALERT/WARN token) unless object, digest, head, role-at-head and authorship all still match the snapshot, with each re-check failure mapped to one reason code (`moved_object` · `moved_digest` · `moved_head` · `moved_role` — all painted as the single REFUSE-MOVED string). At most one sign shall be in flight, and `b`/`enter` shall be inert while the sign worker runs. While armed, ANY key other than `enter` — `up`, `down`, `4`, re-discovery (a resumed/refreshed worker), and any other key, **including `escape` and `q`** — shall cancel the arm without writing and shall NOT leave the screen; `q`/`escape` shall leave the screen (return home) only when NOT armed. While armed the key bar shall read `enter sign · any other key cancel` (U3). After a successful sign in the "needs action" preset the cursor shall move to the next row, or stay on the last row when signing the last.
- **Validation:** `test (integration)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_review_screen.py::test_at_093_b_shows_digest_and_head_and_enter_signs_through_sign_review tests/test_review_screen.py::test_at_100_escape_or_q_cancels_the_arm_and_leaves_only_when_not_armed tests/test_review_screen.py::test_at_101_signing_moves_the_cursor_to_the_next_row tests/test_review_screen.py::test_at_104_armed_state_and_refusals_use_the_darkside_tokens tests/test_review_screen.py::test_at_106_second_enter_while_the_sign_worker_runs_is_inert`
- **Numeric pass threshold:** after `b` the frame carries the digest and head in the ACCENT token; after `enter` exactly one review file exists and `derive` re-derives `reviewed`; after `b` then any other key (including `escape` and `q`), 0 files are written and the screen is NOT left; a `b`, `down`, `enter` sequence writes 0 files (M-RS33); not-armed `q`/`escape` leaves the screen; a second `enter` while the sign worker runs writes no second record; after a sign in the preset the cursor is on the next row (or the last).
- **Negative control:** M-RS4 (`b` signs immediately), M-RS15 (the armed state ignored — `enter` signs from a cold screen), M-RS21 (armed `escape`/`q` leaves the screen instead of cancelling), M-RS25 (after a sign the cursor resets to row 0 instead of moving to the next row — AT-101's negative control), M-RS28 (the disarm-before-worker removed — a second `enter` writes a second record), M-RS32 (the armed hint/row painted without the ACCENT token — the style dropped), M-RS33 (an armed `down` fails to cancel — `b`, `down`, `enter` writes a record).
- **Boundary catalog:** ☑ boundary (second key; cold `enter`; last row) ☑ error (TOCTOU — object/digest/head/role moved between `b` and `enter`) ☐ empty (n/a) ☐ invalid (n/a)

### LLR-RS.2.4 — Refusals are `SigningRefused` with a reason code; no CLI entry point; two signers are defined
- **Traceability:** HLR-RS.2, HLR-RS.3
- **Ledger:** LED-2026-10-15-review-screen-batch.11, LED-2026-10-15-review-screen-batch.12, LED-2026-10-15-review-screen-batch.19, LED-2026-10-15-review-screen-batch.23
- **Statement:** `sign_review` shall return the written `Path` on success and raise `SigningRefused` (a `ValidationError` subclass in `records.py`) with a stable reason code + message on ANY refusal, including the `FileExistsError` on the content-named file (the same content signed twice → reason code `already_signed`) and the review-file count limit (`LIMIT_REVIEW_FILE_COUNT`, reason code `review_limit`); the screen shall paint the message on the hint line. `sign_review` shall have NO CLI or entry-point exposure: no `console_scripts` entry in `pyproject.toml`, no `--sign` flag in `mapper/app.py`, and only `mapper/screens/review.py` (plus the test file that tests `signing` itself) imports `signing` (pinned by a grep/AST test). Two concurrent signers are defined: different content → both content-named files written, the duplicate `seq` harmless (nothing reads `seq`); identical content → `SigningRefused(already_signed)`. The review store's refusals are TYPED (`ReviewLimitError`, `AlreadySignedError`) and mapped by type, never by message text. The inherited confinement race (`confine_reason` → `mkdir` → `open`) is an accepted core residual, not fixed here.
- **Validation:** `test (unit)` · `inspection`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_signing.py::test_sign_review_refuses_already_signed_identical_content tests/test_reqharness_signing.py::test_sign_review_refuses_at_the_review_file_count_limit tests/test_reqharness_signing.py::test_sign_review_has_no_cli_or_entry_point_exposure`
- **Numeric pass threshold:** 0 failed; identical-content double sign raises `SigningRefused` with `already_signed`; the count limit raises `SigningRefused` with `review_limit`; the grep/AST asserts no `console_scripts` entry and no `--sign` flag and only `screens/review.py` importing `signing`.
- **Negative control:** M-RS22 (a refusal raised as a bare `ValidationError` without a reason code) and M-RS23 (a `console_scripts` entry or `--sign` flag added).
- **Boundary catalog:** ☑ boundary (two signers, different content) ☑ invalid (two signers, identical content → `already_signed`) ☑ error (count limit) ☐ empty (n/a)

### LLR-RS.4.1 — The seat gains a `review` scope and a home door, in the screen+seat increment
- **Traceability:** HLR-RS.4
- **Ledger:** LED-2026-10-15-review-screen-batch.1, LED-2026-10-15-review-screen-batch.5, LED-2026-10-15-review-screen-batch.8, LED-2026-10-15-review-screen-batch.19
- **Statement:** `mapper/keymap.py` shall declare `SCOPE_REVIEW = "review"`, a `review` group and a `review-leave` group (added to `GROUP_SCOPE`/`GROUP_HEADER`), the review-scope rows (`up` prev object · `down` next object · `4` cycle filter · `b` confirm-to-sign · `enter` confirm) and the leave rows (`q`/`escape` → home), plus one home door `KeyBinding("v", "v", "review", "review", "doors")`; `mapper/screens/home.py` shall add `"v": "opens the review screen"` to `_DOOR_NOTES` and an `action_review` that pushes `ReviewScreen`; `mapper/app.py` shall re-export `ReviewScreen`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_keymap.py tests/test_key_dispatch.py tests/test_review_screen.py::test_at_097_review_scope_binds_through_the_seat_and_home_opens_by_v`
- **Numeric pass threshold:** `test_at_n03a_every_binding_resolves_to_a_real_action` and `test_at_n03f_bound_keys_match_the_seat_exactly` pass with the new scope; `test_key_dispatch.py`'s whole-seat count re-baselines; `v` from home opens `ReviewScreen` and its key bar advertises the review-scope glyphs.
- **Negative control:** M-RS16 (the door row dropped) and M-RS17 (the `review` scope group omitted from `GROUP_SCOPE` — the key bar paints nothing for it).
- **Boundary catalog:** ☑ boundary (new scope; door key free in home) ☐ empty (n/a) ☐ invalid (n/a) ☐ error (n/a)

### LLR-RS.5.1 — The config `authors` map is validated and part of `config_hash`
- **Traceability:** HLR-RS.5
- **Ledger:** LED-2026-10-15-review-screen-batch.7, LED-2026-10-15-review-screen-batch.15, LED-2026-10-15-review-screen-batch.17, LED-2026-10-15-review-screen-batch.18, LED-2026-10-15-review-screen-batch.20, LED-2026-10-15-review-screen-batch.21
- **Statement:** `reqharness/config.yml` shall gain an optional `authors` map (owning-batch id → list of declared person ids); `validate_config` shall refuse an `authors` entry naming an unknown person id (by name), shall refuse duplicate person ids and duplicate `email_sha256` in `people` (the m2 gap), and shall include `authors` in `canonical_config` ONLY when the map is present and non-empty — an absent AND an empty `authors` are both omitted, so existing registries keep their `config_hash` unchanged (A2) — and any change to `authors` needs an approved `policy` event like any config change. `create_registry` shall seed new registries with an empty `authors` map and the release rule `authors_declared` ENABLED (F2): the rule fails on any active object whose owning batch is blank OR absent from `authors`, and reports an unknown owning batch by name; batch ids are compared after NFC normalisation (exact otherwise — no case folding). A missing `authors` entry (or map) — or an object whose `Owning batch` cell is blank — shall mean authorship not recorded; signing itself stays allowed when authorship is not recorded. The new duplicate-id/duplicate-email refusals can reject configs that load today (acceptable — no external users; stated).
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_registry.py::test_config_refuses_an_unknown_person_in_authors tests/test_reqharness_registry.py::test_config_refuses_duplicate_person_id_and_duplicate_email_sha256 tests/test_reqharness_registry.py::test_authors_map_changes_config_hash tests/test_reqharness_registry.py::test_an_authors_less_config_hashes_byte_identically_to_today tests/test_reqharness_registry.py::test_create_registry_seeds_authors_and_authors_declared`
- **Numeric pass threshold:** 0 failed; an `authors` entry naming an unknown person raises `ValidationError` naming that id; a duplicate person id and a duplicate `email_sha256` each raise by name; two configs differing only in `authors` hash differently; a config with no `authors` (and one with an empty `authors`) hashes byte-identically to today; `create_registry` seeds `authors: {}` and `authors_declared` ENABLED, and the rule fails on a blank/absent owning batch (unknown batch named, NFC-normalised).
- **Negative control:** M-RS24 (the `authors` map left out of `canonical_config` — a change to `authors` does not change `config_hash`; the M-RS24 hash-differs assertion lives in TC-RS-5.1.1).
- **Boundary catalog:** ☑ boundary (a batch with no `authors` entry → signing allowed; empty `authors` omitted from `canonical_config`) ☑ invalid (unknown person in `authors`; duplicate person id; duplicate `email_sha256`) ☐ empty (n/a) ☐ error (n/a)

### LLR-RS.5.2 — `derive` applies the author rule authoritatively
- **Traceability:** HLR-RS.5
- **Ledger:** LED-2026-10-15-review-screen-batch.7, LED-2026-10-15-review-screen-batch.15, LED-2026-10-15-review-screen-batch.17, LED-2026-10-15-review-screen-batch.18, LED-2026-10-15-review-screen-batch.20, LED-2026-10-15-review-screen-batch.21
- **Statement:** `derive.py` shall carry the canon row's `Owning batch` column on `CanonObject.owning_batch` (no longer dropped), and `derive_states` shall count a human review whose `reviewer` is an author of the object's `owning_batch` as `unentitled` — the object shall never derive `reviewed` from it — so a hand-written review record cannot bypass the screen's self-review refusal; it shall also count as `unentitled` (distinct reason `owning_batch_mismatch`) a human review whose STORED owning batch (the record field F1) differs from the object's current cell, and a review whose reviewer held no designated role at its bound head (`no_role`). `unentitled` therefore has three causes — role · author · owning-batch mismatch — and `audit.py` counts them together (A8). The author rule is RETROACTIVE: it reads the live `authors` map, not the map at the review's bound head (a recorded decision). An object whose `owning_batch` is blank (or whose batch has no `authors` entry) has no author set, so no review is marked `unentitled` on that ground. A record written before this batch lacks the `owning_batch` field → evaluated as today (legacy).
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_reqharness_registry.py::test_derive_marks_an_authors_human_review_unentitled tests/test_reqharness_registry.py::test_authors_declared_release_rule_fails_when_batch_has_no_authors tests/test_reqharness_registry.py::test_derive_marks_a_stored_owning_batch_mismatch_unentitled`
- **Numeric pass threshold:** 0 failed; a hand-written human review whose reviewer is an author of the object's batch yields `unentitled` and the object does not derive `reviewed`; a review whose stored owning batch differs from the object's current cell yields `unentitled` with reason `owning_batch_mismatch`; the `authors_declared` rule fails when an active object's batch has no `authors` entry, and is absent (does not fail) when not declared.
- **Negative control:** M-RS18 (the author rule dropped from `derive` — an author's hand-written review derives `reviewed`).
- **Boundary catalog:** ☑ invalid (an author's hand-written human review; a stored-owning-batch mismatch) ☑ boundary (a non-author human review still derives `reviewed`) ☐ empty (n/a) ☐ error (n/a)

### Information Flow Contract (IFC) — C-54

- **Part A — flows:**

```text
FLOW: review-screen-load
  SOURCE: git rev-parse --show-toplevel / git config --get user.name / user.email (hardened allowlist, unchanged) + REQUIREMENTS.md canon + reqharness/config.yml + roles.yml + reviews/*.yml
  - fn : screens/review.py::ReviewScreen — one Textual thread worker runs identity.repo_root + identity.read + verify_chain + load_canon + derive.derive_states + release.evaluate, returning one immutable snapshot (applied in on_worker_state_changed, generation + is_attached)
    owner : LLR-RS.1.4
  - fn : derive.py::derive_states + reviews.py::load_reviews (states, history, marks, unentitled — read, never re-derived)
    owner : LLR-RS.1.1
  - fn : release.py::evaluate (the fixed bottom band's rules + verdict)
    owner : LLR-RS.1.2
  - fn : screens/review.py paint — darkside.plain into rich Text sinks ONLY, truncated by cell width
    owner : LLR-RS.1.3
  SINK: the terminal canvas (rich Text via darkside tokens)

FLOW: review-sign
  SOURCE: the sign intent the operator confirmed on screen (b then enter): object_id + normative digest + head + the one snapshot
  - fn : screens/review.py action_sign (b arms the intent; enter re-reads identity, re-verifies, then calls sign_review in a worker)
    owner : LLR-RS.2.3
  - fn : reqharness/signing.py::entitled_to_sign (chain + identity + role-at-head + active + class-declared + authorship)
    owner : LLR-RS.2.2
  - fn : reqharness/signing.py::sign_review (verify_chain → load_canon → object_digests → TOCTOU → next_seq → record_review; returns Path or raises SigningRefused)
    owner : LLR-RS.2.1
  SINK: reqharness/reviews/*.yml (immutable, content-named, exclusive create), re-read by derive.derive_states and release.evaluate
```

- **Part B — boundary decomposition:** no — no component of the boundary is addressable on its own by a consumer in this batch: the screen, the seat and the core are one process over one `reqharness/` directory; the only independently addressable surface is the file set, which the existing confinement rule (`osopen.confine_reason`, R8) already guards, and the screen's new `review` scope is addressed only by `ReviewScreen`. `sign_review` is a headless library function with no CLI/entry-point surface (LLR-RS.2.4).

---

## 5. Validation strategy

### 5.1 Methods

> **Two layers** (per the Two-layer validation rule). Every batch declares BOTH:
> - **Layer A — white-box / functional (`TC-NNN`):** validates the HLR/LLR mechanism (the HOW). Methods: `test`, `inspection`, `analysis`.
> - **Layer B — black-box / behavioral acceptance (`AT-NNN`):** validates the user story's outcome through the shipped surface (the WHAT). Method: `acceptance`.

- **Layer A (test):** `tests/test_reqharness_registry.py` (RS1a — the config `authors` + derive author/mismatch nodes + the review-record `owning_batch` round-trip), `tests/test_reqharness_signing.py` (RS1b — every LLR-RS.2.* / `entitled_to_sign` / `sign_review` gate), and the seat tests `tests/test_keymap.py` + `tests/test_key_dispatch.py` (RS2). Helpers reused from `tests/test_reqharness_registry.py` (`_seed`, `_add_ana`, `_grant_reviewer`, `_digests`, `_record_review`, `_derive`).
- **Layer B (acceptance), exact node names** (each node's docstring carries its bare `AT-NNN` token, the form `V2` resolves):
  - AT-090 → `tests/test_review_screen.py::test_at_090_review_screen_opens_from_home_and_paints_the_registry`
  - AT-091 → `tests/test_review_screen.py::test_at_091_needs_action_filter_preset_lists_only_open_objects`
  - AT-092 → `tests/test_review_screen.py::test_at_092_detail_pane_shows_history_digest_verdicts_and_informative_badge`
  - AT-093 → `tests/test_review_screen.py::test_at_093_b_shows_digest_and_head_and_enter_signs_through_sign_review`
  - AT-094 → `tests/test_review_screen.py::test_at_094_b_refuses_when_the_viewer_lacks_the_role_or_the_object_is_retired`
  - AT-095 → `tests/test_review_screen.py::test_at_095_tampered_or_forked_chain_is_read_only_with_the_reason`
  - AT-096 → `tests/test_review_screen.py::test_at_096_screen_paints_file_derived_text_through_text_sinks_only`
  - AT-097 → `tests/test_review_screen.py::test_at_097_review_scope_binds_through_the_seat_and_home_opens_by_v`
  - AT-098 → `tests/test_review_screen.py::test_at_098_cold_enter_does_nothing`
  - AT-099 → `tests/test_review_screen.py::test_at_099_two_thousand_objects_scroll_with_the_cursor_in_view`
  - AT-100 → `tests/test_review_screen.py::test_at_100_escape_or_q_cancels_the_arm_and_leaves_only_when_not_armed`
  - AT-101 → `tests/test_review_screen.py::test_at_101_signing_moves_the_cursor_to_the_next_row`
  - AT-102 → `tests/test_review_screen.py::test_at_102_b_refuses_when_the_viewer_authored_the_object_batch`
  - AT-103 → `tests/test_review_screen.py::test_at_103_armed_hint_elides_the_middle_and_keeps_the_tail`
  - AT-104 → `tests/test_review_screen.py::test_at_104_armed_state_and_refusals_use_the_darkside_tokens`
  - AT-105 → `tests/test_review_screen.py::test_at_105_screen_paints_no_string_outside_the_copy_table_or_prototype`
  - AT-106 → `tests/test_review_screen.py::test_at_106_second_enter_while_the_sign_worker_runs_is_inert`
  - AT-107 → `tests/test_review_screen.py::test_at_107_worker_runs_all_disk_and_git_work_off_thread`

  The screen ATs (AT-090…AT-107) assert on the **painted frame** — `_plain` / `_render_text` of the widget, the `tests/test_roles_screen.py` pattern, never on the arguments of an `update()` call (C-32) — and every one drives the real app (`MapperApp(tmp_path)` + `run_test(size=(118,34))` **and** `(87,34)` + real `pilot.press` keys, helpers imported from `tests/test_draft_save.py`). AT-093 (and the signing unit nodes) re-read the file `sign_review` wrote and feed THAT to `derive` (B4 output-then-consume). AT-097 drives `v` from home. AT-094 also plants an undeclared viewer, no git identity (→ REFUSE-VIEWER), and no registry (→ REFUSE-CHAIN with status `no registry yet`) — mapped explicitly, no new strings. AT-091 asserts all three open states present. AT-090/091 at 87 assert per scroll window; the full 10-object fixture arm runs at 118 (Q3). AT-092 uses two fixtures (ready / not ready) each byte-equal to `release.evaluate(...).text` (Q8). AT-096 payloads add the markup brackets `[bold]x[/]` / `[/]` (Q6). AT-099's counter is `render_line` calls per move (Q4). AT-100 drives the `escape` **and** `q` arms (any key other than `enter` cancels the arm and does not leave; not-armed `q`/`escape` leaves). AT-101 signs a middle row (k≥1) and a last-row case (Q5), its negative control M-RS25 (cursor reset to row 0). AT-103 arms the longest id at 87 and asserts the `enter confirms, any other key cancels` tail is present. AT-104 asserts the armed hint/row use the ACCENT token and refusals the roles-screen ALERT/WARN token. AT-105 asserts every painted literal is in §6.6 ∪ the prototype set. AT-106 asserts a second `enter` while the sign worker runs writes no second record. AT-107 recorders on `verify_chain`/`load_canon`/`derive_states`/`release.evaluate`/`sign_review`, patched where the screen looks them up, asserting a NON-EMPTY record (Q9).
- Every LLR names its reddening mutant (M-RS1…M-RS33); each increment executes at least one of its own at the RED proof, with the sha256 restore check.

### 5.2 Batch acceptance criteria
- 100% of LLR-RS.* covered by a named node, each with a pass result.
- 0 blocker fails; no requirement without a validation method.
- Every user story has ≥ 1 passing AT: US-RS-001 → AT-090/091/092/096/099 · US-RS-002 → AT-093/098/100/101 · US-RS-003 → AT-094/095/102 · US-RS-004 → AT-097.
- **Width coverage (Q1).** Every screen AT runs at BOTH `(118, 34)` and `(87, 34)` OR is declared single-width with a reason — no AT is silently single-width.
  - **Both widths** (their assertion reads the painted frame / hint / band / detail / list row, whose layout differs by width): AT-090, AT-091, AT-092, AT-093, AT-095, AT-096, AT-100, AT-101, AT-103 (the `test_at_103_armed_hint_elides_the_middle_and_keeps_the_tail` node), AT-104 (the two painted `test_at_104_the_painted_*` nodes). These are `@pytest.mark.parametrize("width", [118, 87])`.
  - **118 only — logic / behaviour, no width-dependent painted assertion** (declared here, not parametrised): AT-094 (refusal reason codes — the hint's before/after template segments never elide, so the asserted words are width-independent), AT-097 (seat/binding — the key-bar glyphs derive from the seat, not the layout), AT-098 (a cold `enter` writes nothing — the before/after frame comparison is at one fixed width), AT-099 (scroll-to-cursor is vertical/height; the `render_line` count is width-independent), AT-102 (the author refusal — width-independent), AT-105 (the literal census — no rendering), AT-106 (a second `enter` is inert — internal state), AT-107 (the worker runs off-thread — thread names, not painting).
  - **AT-103's both-ends arm** (`test_at_103_the_painted_armed_hint_elides_the_middle_of_a_long_object`) is 118-only: "both ends survive" needs a wide elision budget — at 87 only one head + one tail cell fit, so that property is inherently wide-width; the 87 tail arm is the parametrised `test_at_103_armed_hint_elides_the_middle_and_keeps_the_tail`.
- The operator-path guard (`tests/test_no_operator_paths.py`) stays green; no hard-coded glyph or hex outside `darkside.py`/`keymap.py`.
- Each increment lands with its RED proof (revert product change → new test FAILS → sha256-verified byte-identical restore → GREEN, transcript printed).

---

## 6. Appendices (optional)

### 6.1 Extended glossary
See §1.3.

### 6.2 Relevant design decisions
- **`signing.py` is a new leaf, not an addition to `reviews.py`.** `sign_review` imports `derive` (`load_canon`/`object_digests`), which imports `reviews`; putting it in `reviews.py` closes a cycle. (R1, overrides the P0 spike's draft signature.)
- **The second confirmation key is `enter`.** The prototype verdict fixed "a second key" without naming it; `b` arms, `enter` confirms, any other key cancels — a record is immutable, so the confirm is a deliberate chord, not a single keystroke. (Decision recorded in PLAN.)
- **The door key is `v`.** Free in the home scope (home owns `c p n t i f r R s j k enter q`); the prototype's `b` is the in-screen sign key, not the door.
- **Self-review is forbidden now (R6).** The operator's 2026-10-15 decision overrides R2 (which had left it as an open question): authorship is recorded per batch in the config `authors` map, refused at `entitled_to_sign`, and enforced authoritatively in `derive`.
- **The signing path is headless.** `sign_review` has no CLI or entry point; an agent in the operator's shell inherits the operator's git identity and could call it, but the TUI's two-key confirm is the human-facing guard, and the path cannot prove a human pressed the key (§6.3 C1 residual).

### 6.3 Open risks
- **Immutability.** A review record is immutable once written; the confirm key is the only guard. The AT must drive the second key and assert the record only then (M-RS4).
- **TOCTOU between `b` and `enter`.** The object, digest, head or role can move after `b` is pressed; `sign_review` re-checks all four before writing (R1's refusal), each mapped to a named reason code (`moved_object`/`moved_digest`/`moved_head`/`moved_role`, painted as the one REFUSE-MOVED string), so a moved object/digest/head/role is a named refusal, nothing written (M-RS5). The sign intent threads one snapshot through the entitlement check, the confirm comparison and `record_review` (sec m3).
- **Impersonation (C1) — NOT fully answered, stated as a residual.** git identity is self-claimed: anyone can set `user.email` to a declared reviewer's address and sign as them (sec m1). The chain proves integrity and approval, not authorship; an agent running in the operator's shell inherits the operator's git identity (sec MAJOR-2). B-122 strong mode remains the named follow-up, out of scope. The `SigningRefused` path cannot prove a human pressed the key — the two-key confirm guards only the TUI.
- **Security questions (C1/C8) — answered by the mechanism, not by trust:**
  - *C1 — a crafted registry cannot make the screen sign for someone else.* The signer identity is read from git (`identity.read`) and matched to a declared person (`email_sha256`), the same as `roles.py`; `entitled_to_sign` refuses an unknown/undeclared/ambiguous viewer, so a registry cannot name an arbitrary viewer and have the screen sign as them. The viewer is the matched person id, never a string read from the registry.
  - *C1 — a crafted registry cannot make the screen sign a retired object.* `entitled_to_sign` checks the object exists and is active (not `status` starting with `withdrawn`); a retired object is refused with a named reason.
  - *C1 — a crafted registry cannot make the screen sign on a broken chain.* `sign_review` refuses when `verify_chain(repo).ok` is False (tampered, forked, or no registry), naming the status; the screen is read-only and `b` is inert with that reason.
  - *C8 — a crafted registry cannot inject terminal escapes or markup.* Every file-derived string passes through `darkside.plain` into `rich.text.Text` sinks (LLR-RS.1.3); AT-096 plants ESC/U+202E/U+200B/NEL/wide-CJK/combining payloads in object ids and reviewer names and asserts they paint literally with no style span and no ESC byte. No render mode interprets markup on this screen (the `roles.py` R10 precedent).
  - *C1 residual (stated, not fixed).* git identity is self-claimed (LLR-RH.4.4); the chain proves integrity and approval, not authorship. B-122 strong mode remains the named follow-up, out of scope. The inherited confinement race (`confine_reason` → `mkdir` → `open`) is an accepted core residual (sec m6).
- **PDR residuals (F1/F3/F4, stated).** F1 — a human review whose stored owning batch (the sign-time record field) differs from the object's current cell is `unentitled` in `derive` (reason `owning_batch_mismatch`); the earlier "self-review residual: none" was an overclaim and is corrected. F3 — an admin-author can approve their own `authors` change (self-approved policy), carried as B-135. F4 — one human declared twice with two emails. Each is a stated residual, not a fix in this batch.
- **Existing tests each increment moves (itemised — the guarded pins RS2 owns):**
  - RS1: `tests/test_reqharness_registry.py` gains the config-`authors` and derive-author nodes; no existing node references `signing` or `SigningRefused` (premise 7); `config.py`/`derive.py`/`records.py` edits are additive, and their existing nodes stay green.
  - RS2 (screen + seat) — the whole-seat census and door/legend pins:
    - `tests/test_inc9.py` `HELP_SCREENS` completeness (`assert len(HELP_SCREENS) >= 7`, line 79) and `OPENERS == HELP_SCREENS` (line 132) — break as soon as `ReviewScreen` gains a `KEY_SCOPE` (the RolesScreen precedent, line 127).
    - `tests/test_inc9.py` `CHROME_LEXICON` (line 376) — any new label word must be in the lexicon.
    - `tests/test_inc9.py` `ENTRY_ROWS` census (`assert len(ENTRY_ROWS) == 60`, line 715) — new review-scope rows + the `v` door row move it.
    - `tests/test_inc9.py` `test_cd25b_no_chord_collides_on_entry_or_on_exit` (line 745; also `tests/test_inc4_census.py:80`, `tests/test_help_scope.py:676`).
    - `tests/test_inc9c.py` home door list (`len(doors) == 7`, line 437) and `test_inc9c_k1_home_door_list_reads_browse_and_build` (line 413).
    - `tests/test_inc9e.py` L1 doors-as-seat-actions (line 103) and `test_inc9e_l3_the_home_bar_paints_the_doors_first` (line 238).
    - `tests/test_en5.py` `test_the_home_door_notes_read_in_english` (line 170 — exact `_DOOR_NOTES` dict) and `tests/test_en8.py` `test_item8_the_template_door_says_what_it_does_not_what_it_is_called` (line 221).
    - `tests/test_legend_design.py` — the legend (a new scope row changes the legend rows).
    - `tests/test_repair_map_truth.py` — parses `docs/ARCHITECTURE.md` §2 `Paths it owns`; adding `mapper/screens/review.py` to the `screens` row (ARQ §1.2) is required before the file is created.
    - `tests/test_keymap.py` `test_at_n03a_every_binding_resolves_to_a_real_action` (line 123) and `test_at_n03f_bound_keys_match_the_seat_exactly` (line 148); `tests/test_key_dispatch.py` whole-seat count (line 177-179).
    - A3/darkside censuses: `tests/test_a3_census.py` and `tests/test_darkside_census.py` — the new scope/rows enter the censuses.

### 6.4 Phase-1 reconciliation log — moved to the ledger (§7)

### 6.5 Requirement amendments — moved to the ledger (§7)

### 6.6 Copy — the EXACT set of new UI strings

> These are the only new UI strings this batch may paint. **Operator copy verdict 2026-10-15: `Aprobado`** — the table is approved with exactly two changes (`SIGN-ARMED`, `REFUSE-MOVED` below); the other 12 strings are unchanged. Nothing outside this table may appear on the screen. While armed, ANY key other than `enter` (including `escape` and `q`) cancels the arm and does not leave the screen (LLR-RS.2.3).

| String id | Exact UI string (English) | Where painted |
|---|---|---|
| SIGN-ARMED | `sign <object> · digest <sha8> · head <hash> — enter confirms, any other key cancels` | hint line, after `b` |
| REFUSE-CHAIN | `cannot sign: registry not verifiable (<status>)` | hint line |
| REFUSE-VIEWER | `cannot sign: <viewer> is not a declared person` | hint line |
| REFUSE-AMBIGUOUS | `cannot sign: several people match your git identity — declare exactly one` | hint line |
| REFUSE-NO-ROLE | `cannot sign: <viewer> does not hold the <role> role at this head` | hint line |
| REFUSE-OBJECT | `cannot sign: unknown object <object>` | hint line |
| REFUSE-RETIRED | `cannot sign: <object> is retired` | hint line |
| REFUSE-CLASS | `cannot sign: <object>'s class is not declared` | hint line |
| REFUSE-AUTHOR | `cannot sign: <viewer> authored this object's batch` | hint line |
| REFUSE-MOVED | `cannot sign: something changed since b (object, content, head or role) — press b to re-arm` | hint line |
| REFUSE-DUP | `cannot sign: this content was already signed` | hint line |
| REFUSE-LIMIT | `cannot sign: the review-file limit is reached` | hint line |
| EMPTY-CANON | `no canon objects` | detail pane, empty canon |
| EMPTY-HISTORY | `no review event names this id` | detail pane, no history |
| KEY-BAR-ARMED | `enter sign · any other key cancel` | key bar, while armed (key-bar label) |

> **Style rules (U2/U3).** The armed hint line and the armed list row are painted with the `darkside` ACCENT token; refusals (`cannot sign: …`) use the roles-screen ALERT/WARN token; while loading the key bar advertises only `escape`, and when tampered/no-registry `b` is hidden. No new tokens or chrome.

> **From the approved prototype (U4).** These strings are NOT new — they come from the operator-approved `prototypes/review_screen/` verdict (its copy is covered by that verdict) — and are listed here only so AT-105 can pin that the screen paints nothing outside §6.6 ∪ this set: the filter line (`filter  all  (N of N)  4 cycles: …`), `release readiness`, `release readiness — BLOCKED`, the legend `⁂ informative mark …` and `b mark reviewed — …`, `object detail`, `statement`, `digest now`, `review history`, and `not verifiable`. 87-col renders are scroll-trimmed.

---

## 7. The ledger — authored as a SEPARATE FILE

`01-requirements-ledger.md` holds LED-2026-10-15-review-screen-batch.1 … .19.
