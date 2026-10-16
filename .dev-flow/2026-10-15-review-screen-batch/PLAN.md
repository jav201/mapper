# PLAN — mapper — Batch 2026-10-15-review-screen-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language.
> **Owed in.** `core` ✓ · `full` ✓
> Seeded by `/dev-flow-init` step 4 at both levels; the living plan is owed at every gate
> that follows (`/dev-flow` §Living plan is the rule's home).

> **Field guide:** `templates/guides/plan-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.
> **Two header labels are read literally and are never translated:** `Standing authorization` and `Last updated`; the field guide names their readers.

The living compendium of this batch: where-we-are · objective · per-story/per-station status ·
roadmap + increment plan · key decisions · risks/watch-items · conventions honored ·
out-of-scope carries · test ledger · decision log (the human-readable mirror of `state.json`).
**Create at batch open and update at every gate and significant checkpoint** — the
orchestrator presents the full plan in-conversation at each phase gate.

## Header

| Field | Value |
|---|---|
| Project | mapper |
| Batch | 2026-10-15-review-screen-batch |
| Objective | Implement the ReqHarness REVIEW / SIGNING screen (B-134): variant A (list + detail) per the 2026-10-15 prototype verdict, variant C's queue as a "needs action" filter preset, two-key confirmed signing through the existing `reviews.record_review` API, a bottom release band, and the informative-change badge — plus its home door + keymap seat and the signing write-path core increment. |
| Last updated | PDR sealed 2026-10-15 — verdict `approved with conditions`; the four PDR reviews (UX · Security · Architecture · QA) folded in as rulings R14–R17; RS1 split into RS1a/RS1b; P3 next |
| Standing authorization | Read from silence (the runtime cannot prompt): autonomy over the gates this unit commissions; merge NOT granted (the default). The commission's own words name the scope (implement the B-134 verdict) and the worker model; they are silent on merge, so the default stands. Recorded as read from silence, not as quoted words. |
| First gate | not yet run — P0 has no gate run; the first gate exit code and its `V7` line are owed at the P0 gate |
| Premises / RC-1 | No network in this unit, so `origin/main` could not be fetched and `git ls-remote` could not run (RC-1/RC-2). `base_ref` = `a5fd158a3657f5167fc815cdaafe9e30ef7b39ab` — the 40-hex `master` HEAD and the branch point of `feat/review-screen-batch` (verified `git rev-parse master`). Premises the batch rests on: (1) the B-134 prototype verdict and its four sub-question rulings (`prototypes/review_screen/NOTES.md` §Verdict, dated 2026-10-15) stand as written; (2) the ReqHarness core (`mapper/reqharness/{config,chain,reviews,derive,release,identity,records,canonical,cache,baseline,pending}.py`) is already shipped on `master` and is this screen's substrate; (3) the roles screen (`mapper/screens/roles.py`, HLR-RH.8) is the closest precedent for the seat, band and paint conventions this screen reuses. |

## Triggers

The trigger evaluation `state.json`'s `triggers.record` points at: one row per trigger evaluated, fired or not.
(`state.json` `triggers` is still the declared absence — this evaluation is for the orchestrator to record with
`devflow-init.py --fired A2,A3,B4,C1,C8,D1,E1,F1 --not-fired A1,A4,B1,B2,B3,C2,C3,C4,C5,C6,C7,D2,E2,E3,F2`.)

| Id | Verdict | Probe output |
|---|---|---|
| A1 | not fired | `judged` — no new package and no boundary move: the new screen `mapper/screens/review.py` joins the existing `mapper/screens/` package already mapped in `docs/ARCHITECTURE.md` (the `screens` row names `roles.py`; `review.py` becomes a second name on the SAME reqharness edge, a row amendment not a boundary move). |
| A2 | fired | ≥2 modules touched: new `screens/review.py` + `keymap.py` (the `review` scope seat) + `app.py` (re-export + home wiring) + `screens/home.py` (door row). |
| A3 | fired | Interface another module consumes changes: the seat's scope set grows (a new `review` scope read by every screen through `bindings_for`/`textual_bindings`); `app` re-exports `ReviewScreen`; `screens/home.py` gains a door row. Precedent: ReqHarness batch A3. |
| A4 | not fired | `judged` — no parallel increments: one lane, RS1–RS2 sequential (see Roadmap; RS3 merged into RS2, R7). |
| B1 | not fired | `grep -rl "ReviewScreen\|SCOPE_REVIEW" tests/` → matches only this batch's not-yet-created files; the symbols this batch adds are asserted by no existing test. |
| B2 | not fired | `judged` — no file moves: every touched product file is new or edited in place; no rename, no relocated module. |
| B3 | not fired | `judged` — no byte-identical-golden source touched: the batch's file set is disjoint from every source `tests/goldens/**` captures. |
| B4 | fired | The signing write path produces `reqharness/reviews/*.yml`, consumed by the already-shipped `derive.derive_states` (`derive.py:208`) and `release.evaluate` (`release.py:90`). `grep -n "load_reviews\|ReviewScan" mapper/reqharness/derive.py mapper/reqharness/release.py` → hits. Obliges the output-then-consume AT (C-12): the AT must drive the sign key, re-read the file the screen wrote, and feed THAT to `derive`. |
| C1 (auth) | fired | `judged` — identity/authorization: the screen signs as the viewer (git identity, `identity.read`) and must refuse a signer without the class's reviewer role before writing (a pre-flight entitlement check). |
| C2 (secrets) | not fired | `judged` — no secrets handling. |
| C3 (external integration) | not fired | `judged` — no network, no external tool; the only subprocesses remain the existing read-only git allowlist (`identity.py`), unchanged. |
| C4 (sensitive/trust surface) | not fired | `judged` — no NEW trusted file class: the review files and their trust relationship to the release rule already exist from the parent batch; this batch writes more of an existing class through the existing API. |
| C5 (destructive DB) | not fired | `judged` — no database touched. |
| C6 (input surface) | not fired | `judged` — no new parsed input format: the core's loaders (`config.py`, `chain.py`, `reviews.py`) are unchanged; the screen consumes their already-validated output. |
| C7 (network exposure) | not fired | `judged` — nothing listens, connects or fetches. |
| C8 (markup over file-derived text) | fired | `judged` — the screen paints file-derived names/ids/notes/digests/status words; every one must pass through `darkside.plain` into `rich.text.Text` sinks (the roles-screen precedent, LLR-RH.8.4/8.5). |
| D1 | fired | New user-visible surface: the review/signing screen — prototype verdict (variant A) already given 2026-10-15, so no prototype round is owed. |
| D2 | not fired | The prototype was built in the target technology — `prototypes/review_screen/proto.py` runs on the real Textual 8.2.8 stack (`run_test` + `save_screenshot`), per `NOTES.md` §Verification. |
| E1 | fired | ≥3 planned increments (RS1 signing core · RS2 review screen · RS3 seat+home+app). |
| E2 | not fired | `judged` — no high risk declared at intake: the risky mechanism (immutability, head binding, role checks) already exists and was validated in the parent full batch; the operator's confirmation-key ruling already addresses the immutability concern at the UI level. |
| E3 | not fired | `judged` — internal tooling; no client deliverable and no regulated context. |
| F1 | fired | Flow currency (C-45 PULL): no network in this unit, so the flow hash could not be compared to the manifest / refreshed — stated next to the RC-1 line. |
| F2 | not fired | `judged` — the backlog IS refreshed: the B-134 verdict (2026-10-15) was recorded before this batch opened (`a5fd158`). |

_Alignment: fired `A2 A3 B4 C1 C8 D1 E1 F1` (8) · not fired `A1 A4 B1 B2 B3 C2 C3 C4 C5 C6 C7 D2 E2 E3 F2` (15)._
_Station consequence: A2/A3 fire → ARQ turns on, and with it PDR and DDR — the orchestrator's `--fired` write takes those three into `stations_active` and seeds their `by trigger` artifacts. `stations_active` is currently seeded with the core base set `P0 P1 P2 P3 P4 P5` only._

## Where we are

PDR (design review) — this unit. The four PDR reviews (ux-reviewer · security-reviewer · architect · qa-reviewer)
returned `approved` / `approved with conditions`; every finding was folded into the contract, the ledger
(LED `.16`–`.19`), this plan (rulings R14–R17, the RS1a/RS1b split) and the design record
(`design/PDR-2026-10-15-review-screen-batch.md`, sealed `approved with conditions`). No product or test
change was made. Owed next: the P3 increments RS1a → RS1b → RS2.

## Objective

Restated from `state.json` `batch_objective` and BACKLOG B-134: the ReqHarness REVIEW / SIGNING screen —
variant A (list + detail), with variant C's queue as a "needs action" filter preset, two-key confirmed signing
(`b` shows the content digest + chain head that will be signed; a second key confirms — a review record is
immutable once written), the release readiness in a fixed bottom band (mandatory rules + verdict), and the
informative-change mark as a badge (`⁂`) on the object explained in the detail pane. Reached from home by one
key, driven by the keymap seat and darkside tokens, signing through the existing `reviews.record_review` API —
nothing in it that later batches must redesign.

## Per-story / per-station status

| Story / station | Status | Notes |
|---|---|---|
| Station P0 (intake) | done | `PLAN.md` + `spike/intake.md` written; no code |
| Station ARQ (module map) | done | `design/arq-note.md`; F1: the `screens` row must gain `mapper/screens/review.py` (RS2 owns the amendment); `signing.py` auto-claimed by the `reqharness` glob; 0 new edges |
| Station P1 (requirements) | done | US-RS-001…004, HLR-RS.1…4, LLR-RS.n.m, AT-090…097; ledger `.1`…`.6` |
| Review/signing screen story (B-134) | READY | contract derived; the P1 `01-requirements.md` is the live contract |
| P3 increments RS1a–RS1b–RS2 | planned | see Roadmap (RS3 dropped — seat merged into RS2, R7; RS1 split into RS1a/RS1b, R16/A1) |

## Roadmap + increment plan

Three increments, each ≤ 4 source files (tests uncapped, same increment). The P2 review merged the seat into RS2 (QA BLOCKER) and added the authorship core to RS1 (R6); the PDR split RS1 into RS1a/RS1b (A1 — RS1 was 5 source files with `release.py`); the P3 re-split (R18) re-cut RS1a/RS1b BY LAYER:

1. **RS1a — the data layer** — `mapper/reqharness/reviews.py` (the review record gains an optional `owning_batch` field: `record_review(..., owning_batch=...)` writes it; `_REVIEW_KEYS`/`_validate_review`/`ReviewEvent` accept it; records without it load exactly as today), `mapper/reqharness/records.py` (`SigningRefused(ValidationError)` + the stable reason-code literals), `mapper/reqharness/config.py` (optional `authors` schema + validation incl. duplicate person id / duplicate `email_sha256`; `create_registry` seeds `authors: {}`; absent AND empty `authors` omitted from `canonical_config`), `mapper/reqharness/derive.py` (`unentitled` with three causes — role · author · owning-batch mismatch; `owning_batch` on `CanonObject`; legacy records evaluated as today) — **4 source files** + additions to `tests/test_reqharness_registry.py` (the config `authors` + derive author nodes + the review-record `owning_batch` round-trip). **No existing test/pin moves.**
    ⚠ **At 4 source files** — each file is a distinct data surface (record schema · exception · config schema · derivation); the RS1b logic (`signing.py`, `release.py`) is the orchestrator/rule layer over them.
2. **RS1b — the logic** — `mapper/reqharness/signing.py` (new) + `mapper/reqharness/release.py` (the `authors_declared` rule + the `authors_declared` ENABLED seed in `_DEFAULT_RELEASE_RULES`) — **2 source files** + `tests/test_reqharness_signing.py` + additions to `tests/test_reqharness_registry.py` (`test_authors_declared_release_rule_fails_when_batch_has_no_authors`, and the `authors_declared` ENABLED half of `test_create_registry_seeds_authors_and_authors_declared`). `entitled_to_sign(repo, object_id, identity_email) -> (bool, reason)` (10 `(False, reason)` arms + 1 `(True, "")`) and `sign_review(repo, object_id, identity_email, *, confirm_digest, confirm_head, now=None) -> Path`, orchestrating `load_config` → `verify_chain` → `config_digest == policy_config_hash` → `load_canon` → `object_digests` → the entitlement pre-flight → `next_seq` → `record_review` (bound head; `class_id` from the canon object, `note=""`, `owning_batch` stored). Helpers reused from `tests/test_reqharness_registry.py`.
3. **RS2 — review screen + seat** — `mapper/screens/review.py` (new), `mapper/keymap.py` (new `review` scope + `review-leave` group + home door `v`), `mapper/app.py` (re-export `ReviewScreen`), `mapper/screens/home.py` (`_DOOR_NOTES["v"]` + `action_review`) — **4 source files** + `tests/test_review_screen.py` + the re-pinned censuses. Variant A list + detail (`ReviewList` = a line-based `ScrollView` with `render_line` that binds NO keys; "needs action" preset; detail pane; bottom band; `⁂` badge; empty-canon/empty-history text); `b` arms a sign intent → `enter` disarms and signs through `sign_review` (one sign in flight); read-only under tamper/fork; ALL disk/git work in one thread worker returning one snapshot. Helpers imported from `tests/test_draft_save.py` and `tests/test_roles_screen.py`.
    ⚠ **At 4 source files** — the seat edit is owned by exactly one increment (the RH6a precedent), and merging it into RS2 is the BLOCKER fix (the screen's ATs and the seat rows must land together).
    **Existing tests/pins it moves, itemised (QA MAJOR-2, completed per Q2):** `tests/test_inc9.py` `HELP_SCREENS` completeness (`:79`) + `OPENERS == HELP_SCREENS` (`:132`, adds a `"ReviewScreen"` opener ~`:127`), `CHROME_LEXICON` (`:376`), `ENTRY_ROWS` census (`:715`), `test_cd25b` (`:745`; also `tests/test_inc4_census.py:80`, `tests/test_help_scope.py:676`); `tests/test_inc9c.py` door list (`:437`) + `test_inc9c_k1_home_door_list_reads_browse_and_build` (`:413`); `tests/test_inc9e.py` L1 doors (`:103`) + `test_inc9e_l3_the_home_bar_paints_the_doors_first` (`:238`); `tests/test_en5.py` `test_the_home_door_notes_read_in_english` (`:170`); `tests/test_en8.py` `test_item8_the_template_door_says_what_it_does` (`:221`); `tests/test_legend_design.py`; `tests/test_repair_map_truth.py` (the ARCHITECTURE `screens`-row amendment); `tests/test_keymap.py::test_at_n03a_every_binding_resolves_to_a_real_action` (`:123`) + `::test_at_n03f_bound_keys_match_the_seat_exactly` (`:148`); `tests/test_key_dispatch.py` whole-seat count (`:177-179`); `tests/test_mod_parity.py:56-62` home golden sha256 (new `v` door, RH6a precedent); `tests/test_darkside_census.py:~413` severity sites `== 54` + ADJUDICATED rows; `tests/test_app_imports_used.py:50-58` `ReviewScreen` allowance; `tests/test_a3_census.py` (states why it moves — render-protocol census — or is removed). Also owns the `docs/ARCHITECTURE.md` `screens`-row + `app`-row + `KEYMAP` seat-row amendment (ARQ §1.2, before `review.py` is created — ARQ F1).

## Key decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-15 (P0) | Mode `core` (recommended; seeded `core`) | Not a client deliverable and no regulated context (E3 not fired); the signing write path exercises the existing `reviews.record_review` API already validated in the parent full batch; the security-relevant controls fire by trigger (C1/C6/C8) regardless of mode. The orchestrator may promote to `full` for continuity with the parent ReqHarness batch (which ran `full`) if it wants the 3-lens + 06-docs rigour over the immutable write path. |
| 2026-10-15 (P0) | The signing core is a NEW `mapper/reqharness/signing.py`, not an addition to `reviews.py` | `sign_review` imports `derive` (for `object_digests`/`load_canon`); `derive` imports `reviews` (`ReviewScan`) — putting it in `reviews.py` closes a cycle. |
| 2026-10-15 (P0) | B-124/B-125/B-126 stay OUT | The screen signs, it does not diff commit-vs-reviewer (B-124); no baseline view (B-125); read-only under fork, recovery stays core-only (B-126). Re-open only if a P1 finding requires one. |
| 2026-10-15 (P0) | No "self-signing" rule for reviews — the canon object has no author field | The core's no-self-approval rule applies to ROLE changes (`chain._passes_approval`), not reviews; review entitlement is "holds the class's reviewer_role" alone. Adding an author field to canon objects is out of scope. |
| 2026-10-15 (P1) | **R1** — signing core is a NEW `mapper/reqharness/signing.py` (leaf of `derive`/`reviews`, no cycle): `entitled_to_sign(repo, object_id, viewer) -> (bool, reason)` and `sign_review(repo, object_id, viewer, *, confirm_digest, confirm_head) -> record` | Orchestrator ruling. Pre-write checks, all named refusals: chain verified (not tampered/forked/no registry), viewer identity known and declared, viewer holds the DESIGNATED role for that object type at the CURRENT head (B-121: only the designated role marks reviewed; one person may hold several roles), the object exists and is active (not retired), and the digest + head the user CONFIRMED still equal the current ones (TOCTOU between `b` and confirm → named refusal, nothing written). Writes through the existing `reviews.record_review` (immutable, exclusive create, content-named). A model review is never written by this path (human only); model reviews remain pre-review (derive's rule). Ledger `.2`. |
| 2026-10-15 (P1) | **R2** — self-review is NOT forbidden in this batch (no ruling exists for reviews; B-122's "nobody approves their own change" is about role changes) | Stated as an open question for the operator in §6.2, not a requirement. Ledger `.3`. |
| 2026-10-15 (P1) | **R3** — screen `mapper/screens/review.py` = variant A exactly as prototyped | Port the prototype's layout and copy (all UI copy English; no new strings beyond the prototype without a prototype verdict), reading derived states from `derive`, release verdict from `release.evaluate`, painting through `Text` sinks only (registry text is untrusted), git/identity discovery OFF the UI thread using the `roles.py` pattern (worker returns facts; applied in `on_worker_state_changed` with generation + `is_attached`), keys inert until first facts; tampered/forked/no-registry → read-only with the reason, `b` inert with the reason. Ledger `.4`. |
| 2026-10-15 (P1) | **R4** — seat: a home door + keymap scope for the review screen in ONE increment that owns the seat edit (keymap/home/app), with the guarded census pins moved and itemised | Orchestrator ruling. New `SCOPE_REVIEW` scope + `review-leave` group + one home door key; increment order RS1 → RS2 → RS3 so the seat's actions resolve on `ReviewScreen` first. Ledger `.5`. |
| 2026-10-15 (P1) | **R5** — out of scope: baseline/release VIEW, US canon extraction, generated views, B-124/B-125/B-126 | The review screen signs and browses; it does not diff commit-vs-reviewer (B-124), show baselines (B-125) or recover forks (B-126). Ledger `.6`. |
| 2026-10-15 (P1) | The second confirmation key is `enter` (`b` arms, `↵` confirms); the home door key is `v` | The prototype verdict fixed "a second key" without naming it, and `b` is the in-screen sign key, not the door. `v` is free in the home scope (`c p n t i f r R s j k enter q`). Both recorded here, not in a prototype verdict (no new string beyond the prototype's copy). |
| 2026-10-15 (P2) | **R6** — self-review is FORBIDDEN now (operator decision 2026-10-15), authorship per owning batch in `config.yml` | Overrides R2. `config.yml` gains an admin-approved `authors` map (owning-batch id → list of declared person ids; validated: known people, unique; part of `config_hash`, so a change needs an approved `policy` event). `entitled_to_sign` refuses an author by name; `derive` marks an author's hand-written human review `unentitled` (never `reviewed`); optional release rule `authors_declared`. Ledger `.7`. |
| 2026-10-15 (P2) | **R7** — the seat merges into RS2 (screen + seat); RS3 dropped | QA BLOCKER fix: RS2 cannot go green before RS3 (the ATs press `b`/`4`/`enter`/`v`; `KEY_SCOPE` and the door land in the same increment now). RS1 = signing + config + derive + records (4); RS2 = review + keymap + home + app (4). Guarded pins itemised in the Roadmap and §6.3. Ledger `.8`. |
| 2026-10-15 (P2) | **R8** — one thread worker runs ALL disk/git work (identity + `verify_chain` + `load_canon` + `derive` + `release.evaluate`) returning one immutable snapshot; `sign_review` also in a worker; the sign intent captures `object_id`+digest+head+snapshot | QA MAJOR-4/MAJOR-5, sec m3. Thread recorded per call. `enter` re-reads identity and re-verifies; `up`/`down`/`4`/re-discovery cancel the arm; armed `escape` cancels, not-armed `escape` leaves. Ledger `.9`. |
| 2026-10-15 (P2) | **R9** — scale LLR (2 000-object canon) + the cold-`enter` AT | QA MAJOR-3. `ReviewList` named; cursor kept in view after 1 999 `down`; band stays on last rows; repaint ≤ 50 ms median of 5 (recorded at P4, ×10 bound in the suite). `enter` owned by the screen. Ledger `.10`. |
| 2026-10-15 (P2) | **R10** — refusals are `SigningRefused` (a `ValidationError` subclass in `records.py`) with a stable reason code; `sign_review(..., now=None)` → UTC now | QA MAJOR-6, sec m4/m5/m6. `FileExistsError` → `already_signed`; count limit → `review_limit`; `note=""`, `class_id` from the canon object; two-signers semantics stated. Ledger `.11`. |
| 2026-10-15 (P2) | **R11** — active + class-declared object; exactly ONE identity match; no CLI entry point | sec MAJOR-1/MAJOR-2, m1, m2. Truth table + retired/class-undeclared arms; duplicate person id / `email_sha256` refused; the impersonation residual moves into HLR-RS.3. Ledger `.12`. |
| 2026-10-15 (P2) | **R12** — QA minors: payload list, cell-width truncation, 118/87 for every AT, the §6.6 Copy table | ESC/U+202E/U+200B/NEL/wide CJK/combining (no surrogates); AT-094 adds undeclared viewer / no git identity / no registry; AT-091 asserts all 3 open states; the exact new-strings set goes to the operator at PDR. Ledger `.13`. |
| 2026-10-15 (P2 re-check) | **R13** — copy verdict `Aprobado` (two string changes) + the any-key-cancels rule + the five minors closed | The operator approved §6.6 with exactly two changes: `SIGN-ARMED` = `sign <object> · digest <sha8> · head <hash> — enter confirms, any other key cancels`; `REFUSE-MOVED` = `cannot sign: something changed since b (object, content, head or role) — press b to re-arm`. While armed, ANY key other than `enter` (incl. `escape` and `q`) cancels the arm and does NOT leave. Minors: AT-101 negative control M-RS25; LLR-RS.1.5 non-flaky counted-operations bound (wall-clock P4 only); REFUSE-MOVED maps to `moved_object`/`moved_digest`/`moved_head`/`moved_role`; LLR-RS.1.5 states `ReviewList` binds NO `enter` + M-RS26; blank `Owning batch` = authorship not recorded; truth table = 10 `(False, reason)` arms. Ledger `.14`/`.15`. |
| 2026-10-15 (PDR · UX) | **R14** — ux-reviewer (Claude Sonnet) `approved with conditions`: U1 elide the middle of `<object>`/`<viewer>` (tails never cut) · U2 armed hint/row in ACCENT, refusals in the roles-screen ALERT/WARN · U3 loading key bar advertises only `escape`, `b` hidden when tampered, armed bar label · U4 the extra strings come from the approved prototype (listed in §6.6 "from the approved prototype", pinned by AT-105) | Each closes on existing tokens/keymap/§6.6, no new chrome. New ATs 103–105 + mutants M-RS30/31/32. Ledger `.16`. |
| 2026-10-15 (PDR · Security) | **R15** — security-reviewer (Claude Opus) `approved with conditions`, BLOCK-UNTIL F1 before RS1: F1 the record STORES the object's owning batch at sign time; `derive` treats a stored-owning-batch mismatch as `unentitled` (reason `owning_batch_mismatch`); no digest change; legacy records evaluated as today · F2 `create_registry` seeds `authors: {}` + `authors_declared` ENABLED; the rule fails on blank/absent owning batch, NFC-normalised · F3 admin-author self-approval residual → B-135 · F4 one human twice → residual · F5 disarm on the UI thread, one sign in flight, `b`/`enter` inert (AT-106) · F6 refuse unless `config_digest == policy_config_hash` (reason `unapproved_config`) | Corrects §10's "self-review residual: none" overclaim. New reason codes `owning_batch_mismatch`/`unapproved_config`; mutants M-RS28/29. Ledger `.17`. |
| 2026-10-15 (PDR · Architecture) | **R16** — architect (Claude Opus) `approved with conditions`: A1 split RS1 → RS1a (`signing.py`,`config.py`,`derive.py`,`records.py`) + RS1b (`release.py`); RS2 unchanged · A2 `authors` optional; absent AND empty omitted from `canonical_config` (existing digests unchanged) · A3 `entitled_to_sign`/`sign_review` take the git identity email, resolve inside `signing` · A4 loader `ValidationError`s → `SigningRefused` via `release.safe_verify` · A5 ARCHITECTURE `screens`/`reqharness` rows + arq-note §1.2 item 2 RS3→RS2 · A6 `ReviewList` = line-based `ScrollView` + `render_line`; counted ops = `render_line` calls per move · A7 sign worker does the identity re-read + chain re-verify inside, same generation guard, bump + re-snapshot · A8 author rule retroactive; `unentitled` has three causes | Ledger `.18`. |
| 2026-10-15 (PDR · QA) | **R17** — qa-reviewer (Claude Sonnet) `approved with conditions`: Q1 = A1 · Q2 pin-list additions (`test_mod_parity.py` golden sha256, `test_darkside_census.py` severity `== 54` + ADJUDICATED, `test_app_imports_used.py` allowance, `test_a3_census.py` reason-or-remove, `test_inc9.py:132` opener) · Q3 87-col ATs assert per scroll window · Q4 AT-099 counter = `render_line` calls per move + M-RS27 · Q5 AT-101 signs a middle + last row · Q6 AT-096 markup brackets · Q7 AT-094 no-git-identity → REFUSE-VIEWER, no-registry → REFUSE-CHAIN `no registry yet` · Q8 AT-092 two fixtures · Q9 M-RS13 popped-screen + AT-107 non-empty recorders · minors (M-RS5/14/24 moves, reason-code literals, `moved_role`/`moved_head` and `moved_object`/`unknown_object` precedence, single-failure truth-table arms, canon-id≠class-prefix, `b`/`down`/`enter` writes 0 files) | Mutants M-RS27/M-RS33. Ledger `.19`. |
| 2026-10-15 (P3, after the RS1a stop report) | **R18** — RS1 re-split by layer: **RS1a = the data layer** (`reviews.py`, `records.py`, `config.py`, `derive.py` — 4 source files), **RS1b = the logic** (`signing.py` new + `release.py` — 2 source files). `signing.py` moves OUT of RS1a into RS1b (it is the orchestration/entitlement logic); `reviews.py` moves IN to RS1a (the `owning_batch` record field is data — F1). `config.py`/`derive.py` stay in RS1a. One consequence recorded: seeding the `authors_declared` release-rule id into `_DEFAULT_RELEASE_RULES` makes `release.evaluate` return `unknown release rule 'authors_declared'` until RS1b's `release.py` registers it — so RS1a seeds `authors: {}` (the data map) and the `authors_declared` ENABLED seed lands in RS1b with the rule. | Ledger `.20`. |
| 2026-10-15 (RS1a gate · security re-verification) | **R19** — the security reviewer's F1 follow-up (REQUEST-CHANGES) is fixed in RS1a: **H1** a human review lacking `owning_batch` is `unentitled` (`owning_batch_missing`) when `authors` is declared; **M2** the canon `Owning batch` cell is NFC-normalised in `parse_canon`; **L1** duplicate person ids in one `authors` list are refused by name; **L2** the authors-less `config_hash` is pinned to the pre-RS1a digest as a constant; **M1** is a stated residual (an author who can edit the canon can move the `Owning batch` cell to a batch they are not listed for before signing — per-batch authorship is the operator's chosen granularity). | Ledger `.21`/`.22`. |
| 2026-10-15 (RS1b code review · follow-up) | **R20** — the independent RS1b code review returned REQUEST-CHANGES (BLOCK-UNTIL F1/F2); six fixes landed (see Ledger `.23`). **F3 is an orchestrator-accepted SPEC CLARIFICATION:** `sign_review`'s `confirm_owning_batch` becomes a REQUIRED keyword argument (no default) — a stricter internal API with no user-visible change (the RS2 screen passes its sign-intent owning batch). Recorded here as the ruling's home; LLR-RS.2.1's signature text amended accordingly. | Ledger `.23`. |

## Risks / watch-items

- **Immutability** — a review record, once written, is immutable (content-named, exclusive create; a correction
  is a NEW event). Mitigation: the operator's confirmation-key ruling (`b` shows digest + head, a second key
  confirms) is the ONLY guard between a keystroke and a permanent record — it must be implemented exactly, and
  the AT must drive the second key and assert the record only then.
- **Self-signing** — FORBIDDEN by R6 (operator decision 2026-10-15): the `authors` map records authorship
  per owning batch, `entitled_to_sign` refuses an author, and `derive` marks an author's hand-written review
  `unentitled`. A batch with no `authors` entry = authorship not recorded → signing allowed; the optional
  `authors_declared` release rule can fail it.
- **Signing on a tampered/forked chain** — `sign_review` refuses when `verify_chain` is not `STATUS_VERIFIED`;
  the screen paints the tamper state read-only (the roles-screen precedent). Likelihood low (core-enforced).
- **Concurrent signers** — review files have no append lock (unlike `roles.yml`'s `.roles.lock`); exclusive
  create turns an identical-content collision into `SigningRefused(already_signed)`, and two different reviews
  of one object are two distinct content-named files (duplicate `seq` harmless — nothing reads `seq`) resolved
  by the R5 precedence at derive. Likelihood low (one TUI). The inherited confinement race (`confine_reason` →
  `mkdir` → `open`) is an accepted core residual.
- **A model review counting only as pre-review** — `kind` is self-declared; `derive` already treats
  `kind: model` as pre-review (LLR-RH.4.3). The screen must NOT let a model review close a state; it surfaces
  the kind honestly.

## Conventions honored

- All UI strings in English; colours from `mapper/darkside.py` tokens, glyphs/keys from `mapper/keymap.py` — never hard-coded.
- No operator path, account name, home path, handle or noreply address in any tracked file; `owner` stays OMITTED (guard A-110).
- Screens land as one module per screen with `KEY_SCOPE` + `BINDINGS` from the keymap seat; the seat edit is owned by exactly one increment (RS2).
- Tests drive the app with `MapperApp(tmp_path)` + `run_test` + real `pilot.press`; helpers reused from `tests/test_draft_save.py`; RED proof (revert → FAIL → sha256-identical restore → GREEN) per increment.
- pytest from the worktree root with `-p no:cacheprovider`, single test files only.

## Out-of-scope carries

- Baseline/release VIEW screen — follow-up batch, prototype round first.
- US canon + AT → test-node extraction, generated MD/HTML views — follow-up batches.
- B-124 (committer-vs-reviewer email warning) · B-125 (baseline `reactivated` + review-state progression) · B-126 (fork-recovery UI) — deferred; the review screen does not need them.
- (superseded by R6) — authorship per owning batch is now IN scope (the `authors` config map); a per-object author field remains out of scope.

## Gate notices and runtime absences

- none yet — the first gate has not run.

## Test ledger

| Suite / command | Last run | Result |
|---|---|---|
| none — P0 intake unit (docs only, no product/test change) | 2026-10-15 | n/a; first ledger entries owed at RS1 |
