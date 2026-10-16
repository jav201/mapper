# Review — mapper — Batch 2026-10-15-review-screen-batch

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`).
> Phase 2 artifact. Reviewers (in parallel): `architect` ∥ `qa-reviewer` ∥ `security-reviewer` by trigger family C (always in `full`).

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/guides/review-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

## ✅ Verdict (read first)

- **Gate:** `approve` → Phase 3  /  `iterate-to-refine` → Phase 1 (blockers present, or a requirement-defect major)
- **Out-of-scope findings:** `none` — every finding below was dispositioned into the contract, the ledger or PLAN.

- **Findings:** `1` blocker · `7` major · `7` minor — all dispositioned (see the table).
- **shall/should check:** ✓ clean (verified during the corrective pass; `shall` appears only inside HLR/LLR statements).
- **Two-layer (blockers):** ✓ every story has an `AT` · output reqs name deliverable+observation · both trace chains complete · ATs are genuinely black-box.
- **Census (change-first):** done — best-effort + gate-confirmed (the RS2 guarded-pin list was grep-completed and itemised in §6.3).
- **Security:** ⚠ 2 findings — dispositioned (active/class-declared object; no CLI entry point), residuals stated in §6.3.
- **Evidence checklists (architect / qa / security):** ✓ all complete.

> The corrective pass at P2 (this unit) folded every finding into `01-requirements.md` (HLR-RS.5 + LLR-RS.1.5/2.4/5.1/5.2 + the §6.6 Copy table + the §6.3 pin census), the ledger (`.7`…`.13`) and `PLAN.md` (R6–R12 + the two-increment roadmap). Verdict recomputed: `approve`.

---

## ✅ P2 re-check (second pass) — operator copy verdict + the five minors, closed

The P2 re-check (`qa-reviewer`, Claude Sonnet) returned `approve-with-conditions` on the corrected contract; the operator then returned the §6.6 **copy verdict**. Every condition is now dispositioned. Validator → 0 blocks under this batch.

### Copy verdict (operator, 2026-10-15)

- **Verdict word:** `Aprobado`.
- **Scope:** the §6.6 "Copy" table is **APPROVED with exactly two changes**; the other 12 strings are unchanged.
  1. `SIGN-ARMED` → `sign <object> · digest <sha8> · head <hash> — enter confirms, any other key cancels` (now carries the digest, as `<sha8>`).
  2. `REFUSE-MOVED` → `cannot sign: something changed since b (object, content, head or role) — press b to re-arm`.
- **Binding rule the verdict adds:** while armed, **ANY** key other than `enter` — including `escape` **and** `q` — cancels the arm and does **NOT** leave the screen. (Previously `escape` cancelled and `q` left; the leave keys now cancel while armed, and leave only when not armed.)
- **Recorded:** `PLAN.md` decision **R13** · ledger **LED-2026-10-15-review-screen-batch.14** · §6.6 table + LLR-RS.2.3 (statement, `escape`/`q` semantics, mutants).

### Disposition of the five minors

| # | Minor | Disposition | Where |
|---|-------|-------------|-------|
| 1 | AT-101 (cursor to the next row after a sign) needs a negative control | Mutant **M-RS25** — the cursor resets to row 0 instead of moving to the next row (executed RED at RS2) | LLR-RS.2.3 negative control + §5.1 |
| 2 | LLR-RS.1.5 wall-clock bound is flaky | The suite asserts a **non-flaky** bound — "the number of painted rows per repaint does not grow with N" (a counted-operations bound); the ≤ 50 ms wall-clock stays a **P4 measurement only**, never a suite assertion | LLR-RS.1.5 statement + numeric pass threshold |
| 3 | SIGN-ARMED carries the digest; `q` semantics | Done by the verdict (string 1 carries `digest <sha8>`); `q` while armed cancels, not leaves | §6.6 + LLR-RS.2.3 |
| 4 | REFUSE-MOVED covers object/content/head/role; one reason code per failure | Done by the verdict (string 2 lists all four); each re-check failure maps to one `SigningRefused` reason code — `moved_object` · `moved_digest` · `moved_head` · `moved_role` | §6.6 + LLR-RS.2.1 + LLR-RS.2.3 |
| 5 | LLR-RS.1.5 states `ReviewList` binds NO `enter`; mutant for the widget binding it | Added to LLR-RS.1.5 + mutant **M-RS26** (`ReviewList` binds `enter` — a cold `enter` fires a second action) | LLR-RS.1.5 statement + negative control |

### Blank `Owning batch` cell

A blank `Owning batch` cell on a canon row is declared the same as "batch not in `authors`": **authorship not recorded**, so signing is allowed and no review is marked `unentitled` on that ground. Stated in HLR-RS.5, LLR-RS.2.2, LLR-RS.5.1 and LLR-RS.5.2.

### Truth-table arm count (reconciled)

`entitled_to_sign` has **10 `(False, reason)` arms** — tampered · forked · no-registry · unknown-viewer · ambiguous-viewer · no-role · unknown-object · retired · class-undeclared · author-of-batch — plus **1 `(True, "")`** entitled arm. `PLAN.md` (roadmap, RS1) and LLR-RS.2.2 now say the same number (the "9 + author" phrasing in LLR-RS.2.2's threshold was a miscount, corrected to 10).

### Evidence checklists (re-check)

- `qa-reviewer` (Claude Sonnet) — ✓ the five minors closed, each with a named mutant; the truth-table arm count reconciled.
- `security-reviewer` (Claude Opus) — ✓ blank-`Owning batch` residual folded into HLR-RS.5/LLR-RS.2.2; no new surface.
- `architect` — ✓ no boundary change; the re-check amends requirements text only.

---

## ✅ PDR — design review (four reviewers, 2026-10-15)

The preliminary design review ran four reviewers in parallel over `design/design-proposal.md` (+ `arq-note.md`). All four returned `approved` / `approved with conditions`; every finding is dispositioned below and folded into the contract (`01-requirements.md`), the ledger (LED `.16`–`.19`), `PLAN.md` (rulings R14–R17) and the sealed record `design/PDR-2026-10-15-review-screen-batch.md` (verdict `approved with conditions`). Reviewer role token + model: architect `Claude Opus` · security-reviewer `Claude Opus` · ux-reviewer `Claude Sonnet` · qa-reviewer `Claude Sonnet`.

| ID | Reviewer (model) | Severity | Finding | Disposition → where it landed |
|----|------------------|----------|---------|-------------------------------|
| U1 | ux-reviewer (Claude Sonnet) | major | Long strings overflow the 87-col hint line; elide the MIDDLE of `<object>`/`<viewer>`, tails never cut | LLR-RS.1.3 (middle elision) + AT-103 + M-RS31. LED `.16`. |
| U2 | ux-reviewer (Claude Sonnet) | major | Armed state has no visual treatment | Armed hint/row in ACCENT, refusals in the roles-screen ALERT/WARN. LLR-RS.2.3 + AT-104 + M-RS32. LED `.16`. |
| U3 | ux-reviewer (Claude Sonnet) | minor | Key bar not specified while loading | Loading advertises only `escape`; tampered hides `b`; armed bar `enter sign · any other key cancel`. LLR-RS.1.4/2.3 + §6.6 `KEY-BAR-ARMED`. LED `.16`. |
| U4 | ux-reviewer (Claude Sonnet) | major | Strings outside §6.6; §9.1 87-col render off-by-two | Listed in §6.6 "from the approved prototype" + AT-105 + M-RS30; §9.1 87 render fixed to 73 cells, scroll-trimmed noted. LED `.16`. |
| F1 | security-reviewer (Claude Opus) | HIGH | Author rule bypass by blanking/changing `Owning batch` (not in digest/record) | Record STORES the owning batch at sign time (LLR-RS.2.1); `derive` marks a stored/current mismatch `unentitled` (`owning_batch_mismatch`, LLR-RS.5.2); legacy records = today. §10 corrected (no longer "none"). LED `.17`. |
| F2 | security-reviewer (Claude Opus) | MED | "batch not in authors → allowed" fails open | `create_registry` seeds `authors: {}` + `authors_declared` ENABLED; rule fails blank/absent owning batch, NFC-normalised (LLR-RS.5.1, HLR-RS.5). LED `.17`. |
| F3 | security-reviewer (Claude Opus) | MED | Admin-author self-approves their own `authors` change | Residual in HLR-RS.5 + backlog item B-135. LED `.17`. |
| F4 | security-reviewer (Claude Opus) | LOW | One human declared twice with two emails | Stated residual (HLR-RS.5, §6.3). LED `.17`. |
| F5 | security-reviewer (Claude Opus) | LOW | Second `enter` while the sign worker runs could write a second record | Disarm on the UI thread; one sign in flight; `b`/`enter` inert. LLR-RS.2.3/1.4 + AT-106 + M-RS28. LED `.17`. |
| F6 | security-reviewer (Claude Opus) | LOW | `sign_review` may read an unapproved config | Refuse unless `config_digest(config) == report.policy_config_hash` (reason `unapproved_config`). LLR-RS.2.1 + M-RS29. LED `.17`. |
| A1 | architect (Claude Opus) | major | RS1 is 5 source files (`release.py` needed) | Split RS1 → RS1a (`signing.py`,`config.py`,`derive.py`,`records.py`) + RS1b (`release.py`). `PLAN.md` roadmap + §2.8. LED `.18`. |
| A2 | architect (Claude Opus) | major | `authors` optional; absent AND empty both omitted from `canonical_config` | LLR-RS.5.1 (existing digests unchanged; duplicate refusals acceptable, no external users). LED `.18`. |
| A3 | architect (Claude Opus) | major | Ambiguous-viewer arm unreachable | `entitled_to_sign`/`sign_review` take the git identity email and resolve to exactly one declared person inside `signing` (LLR-RS.2.2, `arq-note.md` §3). LED `.18`. |
| A4 | architect (Claude Opus) | major | Loader `ValidationError`s become `SigningRefused` via `release.safe_verify` | LLR-RS.2.1 (never a bare exception into the worker). LED `.18`. |
| A5 | architect (Claude Opus) | minor | ARCHITECTURE §3 dependency rows + `reqharness` exposes; arq-note §1.2 item 2 RS3→RS2 | `arq-note.md` §1.2/§3 (RS2 owns it). LED `.18`. |
| A6 | architect (Claude Opus) | major | `ReviewList` base = line-based `ScrollView` + `render_line` | LLR-RS.1.5 (binds no keys; counted ops = `render_line` calls per move). LED `.18`. |
| A7 | architect (Claude Opus) | major | Sign data flow: identity re-read + chain re-verify INSIDE the worker; same generation guard; bump + re-snapshot | LLR-RS.1.4 + design §3 diagrams. LED `.18`. |
| A8 | architect (Claude Opus) | minor | Author rule retroactive; `unentitled` has three causes; `audit.py` counts them together | LLR-RS.5.2 + design §3. LED `.18`. |
| Q1 | qa-reviewer (Claude Sonnet) | major | = A1 (the split) | covered by LED `.18`. |
| Q2 | qa-reviewer (Claude Sonnet) | major | Pin-list additions | `PLAN.md` RS2 pin list completed (`test_mod_parity.py`, `test_darkside_census.py` `== 54` + ADJUDICATED, `test_app_imports_used.py`, `test_a3_census.py`, `test_inc9.py:132`). LED `.19`. |
| Q3 | qa-reviewer (Claude Sonnet) | minor | AT-090/091 at 87 fit ~4 rows | 87 asserts per scroll window; 118 arm on the full 10-object fixture. LLR-RS.1.1 + §5.1. LED `.19`. |
| Q4 | qa-reviewer (Claude Sonnet) | minor | AT-099 name the counter + mutant | counter = `render_line` calls per move + M-RS27. LLR-RS.1.5. LED `.19`. |
| Q5 | qa-reviewer (Claude Sonnet) | minor | AT-101/M-RS25 vacuous on row 0 | sign a middle row (k≥1) + a last-row case. §5.1. LED `.19`. |
| Q6 | qa-reviewer (Claude Sonnet) | minor | AT-096 payloads add markup brackets | `[bold]x[/]` / `[/]` added. LLR-RS.1.3. LED `.19`. |
| Q7 | qa-reviewer (Claude Sonnet) | minor | AT-094 no-git-identity / no-registry mapping | REFUSE-VIEWER / REFUSE-CHAIN `no registry yet` (no new strings). §5.1. LED `.19`. |
| Q8 | qa-reviewer (Claude Sonnet) | minor | AT-092/M-RS10 two fixtures | ready / not ready, each byte-equal to `release.evaluate(...).text`. LLR-RS.1.2. LED `.19`. |
| Q9 | qa-reviewer (Claude Sonnet) | minor | M-RS13 popped-screen test + AT-107 non-empty recorders | LLR-RS.1.4 + §5.1. LED `.19`. |
| QA minors | qa-reviewer (Claude Sonnet) | minor | M-RS5/14/24 moves, reason-code literals, `moved_role`/`moved_head` & `moved_object`/`unknown_object` precedence, single-failure truth-table arms, canon-id≠class-prefix, `b`/`down`/`enter` writes 0 files | LLR-RS.2.1/2.2/2.4 + §5.1 + M-RS33. LED `.19`. |

---

## Detail (reference)

### Findings

| ID | Reviewer | Severity | Area / Req | What | Recommendation | Disposition | Status |
|----|----------|----------|------------|------|----------------|--------|--------|
| QA-1 | qa-reviewer (Claude Sonnet) | blocker | HLR-RS.4 / LLR-RS.4.1 / AT-090…097 | RS2 cannot go green before RS3: the ATs press `b`/`4`/`enter`/`v` and AT-090 opens with `v`, but the bindings, `SCOPE_REVIEW` and the door land in RS3. | Move the seat into RS2 (or split the ATs). | Seat merged into RS2; RS3 dropped. R7 / LED `.8` / Roadmap. | fixed |
| QA-2 | qa-reviewer (Claude Sonnet) | major | §6.3 (RS3 pins) | The RS3 pin list is incomplete (`test_inc9.py` OPENERS/HELP_SCREENS, CHROME_LEXICON, ENTRY_ROWS, `test_cd25b`, `test_legend_design`, `test_repair_map_truth.py`, door counts, A3/darkside). | Itemise. | grep-completed and itemised in §6.3 and the Roadmap. | fixed |
| QA-3 | qa-reviewer (Claude Sonnet) | major | HLR-RS.1 | No requirement/threshold for 2 000 objects; widget unnamed; a list widget binding `enter` could fire a second action. | Add an LLR + a cold-`enter` AT. | LLR-RS.1.5 (`ReviewList`, 50 ms median-of-5 ×10 bound), AT-098 (cold `enter`), AT-099 (scroll). R9 / LED `.10`. | fixed |
| QA-4 | qa-reviewer (Claude Sonnet) | major | LLR-RS.1.4 | Off-thread under-specified: `verify_chain`/`load_canon`/`derive`/`evaluate`/`sign_review` would run on the UI thread. | Decide and assert. | One worker runs ALL disk/git work returning one snapshot; `sign_review` in a worker; thread recorded per call. LLR-RS.1.4 + AT-107. R8 / LED `.9`. | fixed |
| QA-5 | qa-reviewer (Claude Sonnet) | major | LLR-RS.2.3 | TOCTOU binds digest+head but not the object; cancel semantics vs `escape` collide. | Capture `object_id`; name the cancellers; split `escape`. | Sign intent captures `object_id`+digest+head+snapshot; `up`/`down`/`4`/re-discovery cancel; armed `escape` cancels, not-armed `escape` leaves. LLR-RS.2.3 + AT-100. | fixed |
| QA-6 | qa-reviewer (Claude Sonnet) | major | LLR-RS.2.1 | Refusal mechanism unspecified (raise vs return; `FileExistsError`; the 100k limit; `now` not a parameter). | Specify. | `sign_review` returns `Path` or raises `SigningRefused` with a reason code; `now=None`→UTC. LLR-RS.2.1/2.4. R10 / LED `.11`. | fixed |
| QA-m1 | qa-reviewer (Claude Sonnet) | minor | LLR-RS.1.3 | "surrogate" payloads cannot exist in UTF-8; "no style span" → "no span derived from the payload"; truncation by cell width. | Fix. | Payload list = ESC/U+202E/U+200B/NEL/wide CJK/combining; cell-width truncation. LLR-RS.1.3. | fixed |
| QA-m2 | qa-reviewer (Claude Sonnet) | minor | HLR-RS.1 / §5.1 | 118 and 87 required only for AT-090/91/92/96; key bar at 87 untested. | Require both for EVERY screen AT. | Every screen AT at both sizes (HLR-RS.1 threshold + §5.2). | fixed |
| QA-m3 | qa-reviewer (Claude Sonnet) | minor | AT-094 | Missing undeclared viewer, no git identity, no registry. | Add. | AT-094 plants all three. | fixed |
| QA-m4 | qa-reviewer (Claude Sonnet) | minor | AT-091 | Should assert all 3 open states present. | Add. | AT-091 asserts `changed · review`/`pre-reviewed`/`not reviewed` all present. | fixed |
| QA-m5 | qa-reviewer (Claude Sonnet) | minor | LLR-RS.2.3 | "Signing in sequence" unspecified — where does the cursor go after a sign. | Specify. | Cursor moves to the next row (or stays on the last). AT-101. | fixed |
| QA-m6 | qa-reviewer (Claude Sonnet) | minor | §6 (copy) | Armed-state and refusal strings are new copy beyond the prototype; empty-canon text not pinned. | Pin the exact set / get a verdict. | §6.6 "Copy" table lists the exact new strings; they go to the operator at PDR; nothing outside it may appear. | fixed |
| SEC-1 | security-reviewer (Claude Opus) | major | LLR-RS.2.2 | Retired/class-undeclared object missing from the implementing LLR and truth table. | Add active + class-declared arms. | LLR-RS.2.2 requires active (not withdrawn/retired) + class-declared; truth table gains both arms. R11 / LED `.12`. | fixed |
| SEC-2 | security-reviewer (Claude Opus) | major | LLR-RS.2.1 / §6.3 | "a model review shall never be written by this path" is unenforceable; `sign_review` has no CLI exposure pin. | Reword; state the residual; pin the exposure. | Reworded (path writes `kind: human` but cannot PROVE a human pressed the key); no-CLI exposure pinned by grep/AST (LLR-RS.2.4); residual in §6.3. | fixed |
| SEC-m1 | security-reviewer (Claude Opus) | minor | §6.3 / HLR-RS.3 | Impersonation residual only in §6.3; §6.3 heading overclaims "answered". | Move into HLR-RS.3; soften the heading. | Residual stated in HLR-RS.3 (anyone can set `user.email`); §6.3 no longer says "answered" for it. | fixed |
| SEC-m2 | security-reviewer (Claude Opus) | minor | LLR-RS.2.2 / config | Duplicate person ids / `email_sha256` not refused; first-match identity is ambiguous. | Require exactly one match; refuse duplicates by name. | LLR-RS.2.2 ambiguous-viewer arm; LLR-RS.5.1 refuses duplicate person id / `email_sha256`. | fixed |
| SEC-m3 | security-reviewer (Claude Opus) | minor | LLR-RS.2.1/2.3 | Check and write can use different chain snapshots. | Thread one snapshot through. | One snapshot threaded through the entitlement check, the confirm comparison and `record_review`; re-read identity at `enter`. | fixed |
| SEC-m4 | security-reviewer (Claude Opus) | minor | LLR-RS.2.1 | Record fields underspecified (`note`, `now`, `class_id`). | Specify. | `note=""`; `class_id` from the canon object; `now=None`→UTC. | fixed |
| SEC-m5 | security-reviewer (Claude Opus) | minor | LLR-RS.2.4 | Two concurrent signers undefined. | State both arms + one AT. | Different content → both files, duplicate `seq` harmless; identical → `SigningRefused(already_signed)`. One AT. | fixed |
| SEC-m6 | security-reviewer (Claude Opus) | minor | §6.3 | Inherited confinement race (`confine_reason`→`mkdir`→`open`). | State residual. | Stated as an accepted core residual. | fixed |
| SEC-m7 | security-reviewer (Claude Opus) | minor | HLR-RS.3 | Self-review permissive default needs an operator decision. | Decide before P3. | Superseded by R6 (operator decision 2026-10-15: forbid self-review). | fixed |

### shall / should check
> Any modal `should` / `debería` inside an HLR/LLR statement is a writing error → blocker.

`clean` — `shall` appears only inside HLR/LLR statements; no modal `should` in any statement (verified during the corrective pass).

### Two-layer acceptance review (blockers)

| Story / Req | (a) AT present | (b) deliverable+method named | (c) both chains | (d) black-box pure | Status |
|-------------|----------------|------------------------------|-----------------|--------------------|--------|
| US-RS-001 | yes (AT-090/091/092/096/099) | yes — painted frame + release verdict text | yes | yes | ✓ |
| US-RS-002 | yes (AT-093/098/100/101) | yes — `reviews/*.yml` file re-read by `derive` | yes | yes | ✓ |
| US-RS-003 | yes (AT-094/095/102) | yes — hint-line refusal + byte count unchanged | yes | yes | ✓ |
| US-RS-004 | yes (AT-097) | yes — key bar advertises the review scope | yes | yes | ✓ |

### Supersession census (change-first)
> Planned new/moved/edited files checked against EVERY guard family (behavioral-placeholder · structural/placement · AST-composition · frozen-module). State reservations; the increment gate is the completeness guarantee, not this census.

`mapper/reqharness/signing.py` (new), `mapper/reqharness/config.py` (`authors` + person/email uniqueness), `mapper/reqharness/derive.py` (`owning_batch` + author rule), `mapper/reqharness/records.py` (`SigningRefused`), `mapper/screens/review.py` (new), `mapper/keymap.py`, `mapper/screens/home.py`, `mapper/app.py`. Reservations: the `test_inc9.py`/`test_inc9c.py`/`test_inc9e.py`/`test_en5.py`/`test_en8.py`/`test_legend_design.py`/`test_repair_map_truth.py`/`test_a3_census.py`/`test_darkside_census.py` censuses and the `test_key_dispatch.py` whole-seat count all move with RS2's seat edit — enumerated in §6.3 and the Roadmap. The increment gate must confirm each census re-baseline is intentional (not a silent pass).

### Security review summary
`security-reviewer` (Claude Opus): `approve-with-conditions` — 2 MAJOR (retired/class-undeclared object gate; no-CLI exposure), m1–m7. All dispositioned: SEC-1 → active+class-declared truth-table arms; SEC-2 → reworded + grep/AST exposure pin; m1 → impersonation residual in HLR-RS.3; m2 → exactly-one identity match + duplicate refusal; m3 → one snapshot threaded through; m4 → `note`/`now`/`class_id` specified; m5 → two-signers semantics + AT; m6 → confinement-race residual; m7 → superseded by R6.

### Evidence checklists (full) — architect · qa-reviewer · security-reviewer
> Attach each reviewer's completed evidence checklist (items in their agent files), ✓/✗ + one-line evidence.
- `qa-reviewer` (Claude Sonnet) — ✓ complete: every AT is black-box, both size presets required, mutants named per LLR, the copy set pinned (§6.6).
- `security-reviewer` (Claude Opus) — ✓ complete: C1/C8 residuals stated, no-CLI exposure pinned, the impersonation residual moved into HLR-RS.3.
- `architect` — ✓ complete: no boundary move (ARQ note §1.2 unchanged); the `screens`-row amendment is the only map change.
