# Validation — mapper — Batch 2026-10-15-review-screen-batch

> **Artifact language:** English (`state.json` `language: en`).
> Phase 4 artifact. Content owner: `qa-reviewer` (Claude Sonnet), who evaluated the results of the Phase-1 validation strategy, named who executed each one and returned the rows; the orchestrator wrote this file. The ONE complete gate-suite run is the orchestrator's (`C-25`); the reviewer consumed its result and did not own it.

> **Owed in.** `core` ✓ · `full` ✓

## ✅ Verdict (read first)

> **Reserved field names.** `Result` · `Gate run` · `Layer 0` · `Evidence checklist` · `⏸ DEFER` are read literally by the validator; the three verdict tokens are `PASS` · `PASS-WITH-NOTES` · `FAIL`.

- **Result:** `PASS-WITH-NOTES`
- **Gate run:** ``3543 passed, 24 deselected, 3 xfailed, 13 warnings in 2029.79s (0:33:49)` — 0 failed; clean shell, code at ff6262f (847231b + gate record); the 24 deselected are the `slow` and `network` markers`
- **Layer 0:** 33 named reddening mutations (M-RS1…M-RS33) — each executed RED with its sha256 restore check, in the increment packets (RS1a: M-RS18, M-RS24 + H1/M2/L1/L2/L-b; RS1b: M-RS5–8, M-RS14, M-RS19, M-RS22, M-RS23, M-RS29 + the F1–F6 review-fix mutants; RS2: M-RS1–4, M-RS9–13, M-RS15–17, M-RS20, M-RS21, M-RS25–28, M-RS30–33)
- **Requirements:** 17/17 pass (5 HLR + 12 LLR) · 0 blocker fails
- **Black-box acceptance (Layer B):** ✓ every story's `AT` observes its outcome through the shipped surface (boundary + negative): US-RS-001…004 → AT-090…107
- **Surface-reachability (bidirectional):** ✓ all named inputs AND outputs/deliverables reached/observed at the surface (matrix below); 0 gaps
- **Supersession inspection (read off the P3 packets):** ✓ all surviving refs negative — every guarded census pin moved with the seat and the screen (the keymap/dispatch/`ENTRY_ROWS`/door-list pins, the darkside census 54→87, the home-parity golden +9→+10 / +11→+12, the `test_reqharness_release.py` local `_seed`); no live dependency on the old behaviour found
- **Test ledger:** ✓ reconciles — base 3432 passed → post 3533 passed, measured `+101 / −0` at the DDR (collected 3435 → 3536); later DDR-fix and RS2 follow-up commits added further nodes on top (see ledger)
- **Evidence checklist (qa-reviewer):** `qa-reviewer (Claude Sonnet) · 9 of 9 rows ✓ with evidence`

**Full suite (orchestrator, clean shell, merged code):**
``3543 passed, 24 deselected, 3 xfailed, 13 warnings in 2029.79s (0:33:49)` — 0 failed; clean shell, code at ff6262f (847231b + gate record); the 24 deselected are the `slow` and `network` markers`

**Why PASS-WITH-NOTES and not PASS.** Every requirement passes and no blocker is open. The notes: (1) real-user evaluation `not performed — one-person team`; (2) no success message after signing — left as an open operator decision (any new copy would need a prototype verdict, so the screen signs silently and the cursor move is the only confirmation); (3) the watch item `tests/test_reqharness_config.py::test_nesting_event_stream_refuses_lexically_bypassed_shapes` is load-sensitive (failed once under concurrent load during RS1b, passes alone; not touched by this batch); (4) the stated residuals — M1 (an author who can edit the canon can move the `Owning batch` cell before signing), F3/B-135 (admin-author self-approval), F4 (one human twice), agent-driven signing, impersonation, the inherited confinement race, and the exit-time thread residual B-133 (extended by DDR C4: a confirmed sign can finish writing after pop/quit) — are carried, not fixed. None is a failing requirement, so not FAIL.

---

## Detail (reference)

### Layer 0 — unit

| Unit | Which criterion | Node id | Result |
|---|---|---|---|
| config `authors` schema + validation | LLR-RS.5.1 | `tests/test_reqharness_registry.py::{test_config_refuses_an_unknown_person_in_authors, test_config_refuses_duplicate_person_id_and_duplicate_email_sha256, test_authors_map_changes_config_hash, test_an_authors_less_config_hashes_byte_identically_to_today, test_create_registry_seeds_authors_and_authors_declared}` | pass |
| `derive` author rule + owning-batch mismatch | LLR-RS.5.2 | `tests/test_reqharness_registry.py::{test_derive_marks_an_authors_human_review_unentitled, test_derive_marks_a_stored_owning_batch_mismatch_unentitled}` | pass |
| review-record `owning_batch` round-trip | LLR-RS.2.1 (F1) | `tests/test_reqharness_registry.py::test_record_review_roundtrips_the_optional_owning_batch` | pass |
| security re-verification H1/M2/L1/L2/L-b | HLR-RS.5 · LLR-RS.5.1/5.2 | `tests/test_reqharness_registry.py::{test_derive_marks_a_legacy_review_without_owning_batch_unentitled_when_authors_declared, test_derive_a_legacy_review_without_owning_batch_stays_reviewed_without_authors, test_derive_nfc_normalises_the_owning_batch_cell, test_config_refuses_a_duplicate_person_id_in_one_authors_list, test_a_stored_owning_batch_is_nfc_normalised_on_read}` | pass |
| `entitled_to_sign` truth table | LLR-RS.2.2 | `tests/test_reqharness_signing.py::{test_entitled_to_sign_requires_the_designated_role_at_the_current_head, test_entitled_to_sign_truth_table_includes_retired_and_class_undeclared, test_entitled_to_sign_refuses_an_author_of_the_object_batch, test_entitled_to_sign_truth_table_chain_arms, test_entitled_to_sign_truth_table_identity_and_object_arms}` | pass |
| `sign_review` orchestration | LLR-RS.2.1 | `tests/test_reqharness_signing.py::{test_sign_review_writes_a_record_that_derive_reads_as_reviewed, test_sign_review_refuses_on_tampered_or_forked_or_no_registry, test_sign_review_freezes_the_clock_via_now, test_sign_review_refuses_an_unapproved_config, test_sign_review_refuses_when_the_object_digest_head_or_role_moved}` | pass |
| `sign_review` typed refusals + exposure | LLR-RS.2.4 | `tests/test_reqharness_signing.py::{test_sign_review_refuses_already_signed_identical_content, test_sign_review_refuses_at_the_review_file_count_limit, test_sign_review_has_no_cli_or_entry_point_exposure}` | pass |
| RS1b code-review follow-up F1–F6 | LLR-RS.2.1/2.2/2.4 | `tests/test_reqharness_signing.py::{test_sign_review_loads_config_chain_and_canon_exactly_once, test_signing_import_forms_are_all_detected, test_sign_review_confirm_owning_batch_is_a_required_keyword, test_two_signers_different_content_both_write_and_duplicate_seq_is_tolerated, test_sign_review_maps_typed_review_errors_not_message_text}` | pass |
| `ReviewList` + filter + `_elide_middle`/`_take_cells` | LLR-RS.1.1/1.3/1.5 | `tests/test_review_screen.py::{test_at_090…, test_at_091…, test_at_098…, test_at_099…, test_at_103…}` (18 canonical ATs) | pass |
| seat (keymap + door) | LLR-RS.4.1 | `tests/test_keymap.py`, `tests/test_key_dispatch.py`, `tests/test_review_screen.py::test_at_097…` | pass |

**Measured by mutation, never by line coverage.** Mutant text and the restore hash are in the packets; the transcripts are under `evidence/`.

| Unit | Mutation applied | RED observed? | Transcript |
|---|---|---|---|
| config `authors` | M-RS24 (drop the `authors` fold from `canonical_config`); m2 (drop the duplicate-email refusal loop) | yes | `evidence/rs1a-red.transcript` |
| `derive` author rule | M-RS18 (author arm gated off); F1 (`owning_batch_mismatch` arm gated off) | yes | `evidence/rs1a-red.transcript` |
| security H1/M2/L1/L2/L-b | revert each fix | yes — legacy-without-owning-batch unentitled; NFC cell; duplicate person id; pinned digest; NFC-on-read | `evidence/rs1a-red.transcript` §5–§8 |
| `entitled_to_sign` | M-RS5–8, M-RS14, M-RS19 | yes — each truth-table arm killed | `evidence/rs1b-red.transcript` |
| `sign_review` | M-RS22 (bare `ValidationError`), M-RS23 (`--sign` planted), M-RS29 (`unapproved_config` dropped) | yes | `evidence/rs1b-red.transcript` |
| RS1b F1–F6 review fixes | each reverted | yes | `evidence/rs1b-red.transcript` (Code-review follow-up) |
| screen paint / arm / confirm / scroll / seat | M-RS1–4, 9–13, 15–17, 20, 21, 25–28, 30–33 (22 mutants) | yes — 9 initially-GREEN mutants drove test strengthening then RED | `evidence/rs2-red.transcript` |

### UX walkthrough — trigger family D fired (the review/signing screen is a new user-visible surface)

Driven by the `qa-reviewer` (Claude Sonnet) and the `ux-reviewer` (Claude Sonnet), headless, at both `(118, 34)` and `(87, 34)` (the reference widths), through the real app.

**UX reviewer — real screen at 118 and 87.**

| Criterion (when the user does X, they observe Y) | Driven with the REAL mechanism | Painted result asserted | Verdict |
|---|---|---|---|
| The screen lays out list + detail + fixed bottom band without wrapping, at both widths | `v` from home, `MapperApp(tmp_path)` + `run_test(size=…)` | painted frame (list rows, detail pane, band), no wrap at 118 or 87 | ✓ |
| Armed state is ACCENT: the hint line and the marked list row carry the `darkside` accent token | `b` | painted hint + armed row token | ✓ |
| While armed, any other key cancels and stays (incl. `escape` and `q`); not-armed `q`/`escape` leaves | `b` then `x`/`5`/`space`/`escape`/`q` | 0 review files written; screen still up | ✓ |
| Refusals paint in red (the roles-screen ALERT/WARN token) | `b` on a refused object | painted hint in the alert token | ✓ |
| Tampered/forked/no-registry chain is read-only with the reason, `b` inert and hidden | tampered fixture | painted `not verifiable`, `b` hidden, 0 bytes written | ✓ |
| Empty canon paints the empty-canon text, not a blank panel | empty-canon fixture | painted `no canon objects` | ✓ |

**QA reviewer — the black-box acceptance chain.**

| Act | Driven with the REAL mechanism | Observed | Verdict |
|---|---|---|---|
| home → `v` → "needs action" → `b` → `enter` | real `pilot.press` keys | exactly 1 review file written; re-read by `derive` → object derives `reviewed` | ✓ |
| author refused | `b`/`enter` as an author-of-batch viewer | REFUSE-AUTHOR on the hint line; 0 files written | ✓ |
| tampered registry read-only | tampered fixture | read-only with the reason; `b` inert; 0 bytes written | ✓ |

**Mechanism used:** a UI test driver (Textual `run_test(size=(118,34))` and `(87,34)` + `pilot.press`).

| Act | What it is | Performed? |
|---|---|---|
| Automated walkthrough | the criteria above, driven through the REAL mechanism | performed |
| Expert inspection | a cognitive walkthrough against declared criteria, by a reviewer and not a user | performed — the PDR `ux-reviewer` (Claude Sonnet) review, `design/PDR-2026-10-15-review-screen-batch.md`, and the RS2 UX follow-up (U1–U5, `increment-003.md` §10) |
| Evaluation with users | real users of the system, doing the tasks named in the context of use | not performed — one-person team |

- **Method:** headless drive of the shipped screen by the reviewer at both widths; the painted frame is asserted (`_plain` / `_render_text` of the widget, the `tests/test_roles_screen.py` pattern), never an `update()` argument.
- **Participants or population:** none (no user evaluation).
- **Evidence of the evaluation:** AT-090…AT-107 painted-frame nodes and `evidence/rs2-red.transcript`, `evidence/rs2-green.transcript`, `evidence/rs2-fix-green.transcript`.
- **Limits:** real-user evaluation is `not performed — one-person team`. The no-success-message-after-signing behaviour is left as an open operator decision (the cursor move to the next row is the only confirmation); nothing here establishes that a real operator finds that acceptable.

### Layer A — functional (white-box): per-requirement results

| Req | Method | Executed verification | Numeric threshold | Result | Evidence |
|-----|--------|-----------------------|-------------------|--------|----------|
| HLR-RS.1 | test | `tests/test_review_screen.py` | 0 failed; every object id + derived-state word + release verdict in the painted frame | pass | M-RS1, 2, 3, 9, 10, 11, 12, 13, 20, 26, 27 |
| LLR-RS.1.1 | test | `::test_at_090…`, `::test_at_091…`, `::test_at_098…` | needs-action = exactly `{changed · review, pre-reviewed, not reviewed}`; cold `enter` writes 0 files | pass | M-RS1, 2, 26 |
| LLR-RS.1.2 | test | `::test_at_092…` | stale digest `✗`, model review `(model)`, `⁂` badge line, band byte-equal to `release.evaluate(...).text` (two fixtures) | pass | M-RS9, 10 |
| LLR-RS.1.3 | test | `::test_at_096…`, `::test_at_103…`, `::test_at_105…` | hostile payload paints literally, no ESC/style span; 87-col tail intact; every literal in §6.6 ∪ prototype | pass | M-RS3, 11, 30, 31 |
| LLR-RS.1.4 | test | `::test_at_095…`, `::test_at_107…` | all disk/git off the UI thread; tampered read-only; late result on popped screen dropped | pass | M-RS12, 13, 28 |
| LLR-RS.1.5 | test | `::test_at_099…` | cursor in frame after 1 999 `down`; `render_line` count constant across N | pass | M-RS20, 26, 27 |
| HLR-RS.2 | test | `tests/test_reqharness_signing.py tests/test_review_screen.py` | `b` then `enter` signs and derives `reviewed`; `b` then any other key writes no file; `kind=human`, `verdict=reviewed`, `note=""` | pass | M-RS4, 5, 15, 21, 25, 28, 33 |
| LLR-RS.2.1 | test | `tests/test_reqharness_signing.py::test_sign_review_*` | returns written `Path`; `derive` re-reads `reviewed`; every refusal raises `SigningRefused` and writes nothing; `now` frozen | pass | M-RS5, 14, 29 |
| LLR-RS.2.2 | test | `tests/test_reqharness_signing.py::test_entitled_to_sign_*` | 10 `(False, reason)` arms + `(True, "")` (incl. two roles, blank owning-batch) | pass | M-RS6, 7, 8, 19 |
| LLR-RS.2.3 | test | `tests/test_review_screen.py::{test_at_093…,test_at_100…,test_at_101…,test_at_104…,test_at_106…}` | armed ACCENT hint; `enter` writes one file; any-other-key cancels; `b,down,enter` writes 0; cursor moves to next row; second `enter` inert | pass | M-RS4, 15, 21, 25, 28, 32, 33 |
| LLR-RS.2.4 | test + inspection | `tests/test_reqharness_signing.py::{test_sign_review_refuses_already_signed…,test_sign_review_refuses_at_the_review_file_count_limit,test_sign_review_has_no_cli_or_entry_point_exposure}` | `already_signed` / `review_limit` by type; no `console_scripts` / `--sign`; only `screens/review.py` imports `signing` | pass | M-RS22, 23 |
| HLR-RS.3 | test | `tests/test_reqharness_signing.py tests/test_review_screen.py` | each refusal named, writes nothing; tampered screen read-only | pass | M-RS6, 7, 8 |
| HLR-RS.4 | test | `tests/test_keymap.py tests/test_key_dispatch.py tests/test_review_screen.py::test_at_097…` | `v` opens the screen; key bar advertises the review-scope glyphs; seat counts re-baseline | pass | M-RS16, 17 |
| LLR-RS.4.1 | test | `::test_at_097…` + `test_at_n03a/n03f`, whole-seat count | seat rows resolve; door key free in home scope | pass | M-RS16, 17 |
| HLR-RS.5 | test | `tests/test_reqharness_registry.py tests/test_reqharness_signing.py tests/test_review_screen.py` | author refused by name; author's hand-written review `unentitled`; `create_registry` seeds `authors:{}` + `authors_declared` ENABLED | pass | M-RS18, 19, 24 |
| LLR-RS.5.1 | test | `tests/test_reqharness_registry.py::test_config_*` `test_create_registry_*` `test_authors_declared_*` | unknown person refused by name; duplicate id/email refused; `authors` in `config_hash`; absent AND empty omitted | pass | M-RS24 |
| LLR-RS.5.2 | test | `tests/test_reqharness_registry.py::test_derive_*` | author review `unentitled`; stored-owning-batch mismatch `unentitled` (`owning_batch_mismatch`); legacy evaluated as today | pass | M-RS18 |

All rows are consumed from the merged-tree full-suite run (the orchestrator's ``3543 passed, 24 deselected, 3 xfailed, 13 warnings in 2029.79s (0:33:49)` — 0 failed; clean shell, code at ff6262f (847231b + gate record); the 24 deselected are the `slow` and `network` markers`), not re-run by this record.

### Layer B — behavioral (black-box) acceptance

| US | Acceptance test (`AT-NNN`) | Surface driven | Deliverable observed (path / element) | repr · boundary · negative | Result |
|----|----------------------------|----------------|---------------------------------------|----------------------------|--------|
| US-RS-001 | AT-090 `…::test_at_090_review_screen_opens_from_home_and_paints_the_registry` | `v` from home | painted list: every object id + derived state; empty canon paints `no canon objects` | ✓ · ✓ retired, `⁂` badge · ✓ tampered → `not verifiable` | pass |
| US-RS-001 | AT-091 `…::test_at_091_needs_action_filter_preset_lists_only_open_objects` | `4` cycle filter | painted frame: all three open states, 0 reviewed/retired | ✓ · ✓ · ✓ M-RS2 | pass |
| US-RS-001 | AT-092 `…::test_at_092_detail_pane_shows_history_digest_verdicts_and_informative_badge` | select object | detail pane: digest ✓/✗, unentitled apart, `⁂` explained, band byte-equal to `evaluate` | ✓ · ✓ model/unentitled · ✓ M-RS9/10 | pass |
| US-RS-001 | AT-096 `…::test_at_096_screen_paints_file_derived_text_through_text_sinks_only` | hostile registry | payload bytes painted literally, no ESC, no style span | ✓ · ✓ · ✓ M-RS3/11 | pass |
| US-RS-001 | AT-099 `…::test_at_099_two_thousand_objects_scroll_with_the_cursor_in_view` | 1 999 `down` | cursor id in painted frame; `render_line` count constant in N | ✓ · ✓ · ✓ M-RS20/27 | pass |
| US-RS-002 | AT-093 `…::test_at_093_b_shows_digest_and_head_and_enter_signs_through_sign_review` | `b` then `enter` | `reqharness/reviews/*.yml` written; `derive` re-reads `reviewed` | ✓ · ✓ second key · ✓ any-other-key → 0 files | pass |
| US-RS-002 | AT-098 `…::test_at_098_cold_enter_does_nothing` | `enter` cold | 0 files written, no surface change | ✓ · ✓ · ✓ M-RS15/26 | pass |
| US-RS-002 | AT-100 `…::test_at_100_escape_or_q_cancels_the_arm_and_leaves_only_when_not_armed` | `b` then `escape`/`q` | 0 files, screen stays; not-armed leaves | ✓ · ✓ · ✓ M-RS21 | pass |
| US-RS-002 | AT-101 `…::test_at_101_signing_moves_the_cursor_to_the_next_row` | sign a middle/last row | cursor on next row (or stays on last) | ✓ · ✓ · ✓ M-RS25 | pass |
| US-RS-003 | AT-094 `…::test_at_094_b_refuses_when_the_viewer_lacks_the_role_or_the_object_is_retired` | `b` as unentitled viewer | REFUSE on hint; 0 files; undeclared/no-git/no-registry arms | ✓ · ✓ · ✓ M-RS6/7 | pass |
| US-RS-003 | AT-095 `…::test_at_095_tampered_or_forked_chain_is_read_only_with_the_reason` | tampered fixture | `not verifiable`, `b` inert/hidden, 0 bytes | ✓ · ✓ · ✓ M-RS8 | pass |
| US-RS-003 | AT-102 `…::test_at_102_b_refuses_when_the_viewer_authored_the_object_batch` | `b`/`enter` as author | REFUSE-AUTHOR, 0 files | ✓ · ✓ · ✓ M-RS19 | pass |
| US-RS-004 | AT-097 `…::test_at_097_review_scope_binds_through_the_seat_and_home_opens_by_v` | `v` from home | screen opens; key bar advertises review-scope glyphs | ✓ · ✓ door key free · ✓ M-RS16/17 | pass |

### Bidirectional surface-reachability matrix

| Direction | US dimension / deliverable | Service param / producer | Reached/observed at surface? | TC / AT | Status |
|-----------|---------------------------|--------------------------|------------------------------|---------|--------|
| input | the `v` door key | `home.py` `_DOOR_NOTES`/`action_review` | yes — `pilot.press("v")` | AT-097 | ✓ |
| input | the `b` arm + `enter` confirm keys | `ReviewScreen` sign intent | yes — `pilot.press` | AT-093, 098, 100 | ✓ |
| input | a hostile registry (object id / reviewer name) | `load_canon` → `darkside.plain` | yes — painted frame | AT-096 | ✓ |
| input | a tampered/forked/no-registry chain | `verify_chain` report | yes — read-only paint | AT-095 | ✓ |
| input | a 2 000-object canon | `ReviewList.render_line` | yes — cursor kept in view | AT-099 | ✓ |
| output | the review record `reqharness/reviews/*.yml` | `sign_review` → `record_review` | yes — file on disk, re-read by `derive` | AT-093 | ✓ |
| output | the derived-state words + release verdict | `derive.derive_states` / `release.evaluate` | yes — painted frame | AT-090/092 | ✓ |
| output | the key bar / legend / door agreement | keymap seat | yes — painted key bar | AT-097 | ✓ |

### Signed-balance test ledger

| base | − D | + A | = post | actual collected | passed-lean / full | reconciles? |
|------|-----|-----|--------|------------------|--------------------|-------------|
| 3432 passed (previous batch's gate line, `2026-10-11-fixes-batch`) | 0 | 101 (81 product + 20 census/seat/doc parametrised) | 3533 | 3536 collected (3533 passed + 3 xfailed; 24 deselected) | 3533 passed (default selection) | ✓ yes |

The `+101 / −0` is the DDR's measured delta: `pytest --collect-only -q` at `6121987` (a detached worktree, removed afterwards) → `3435/3459` (24 deselected); at HEAD → `3536/3560` (24 deselected); `comm` of the two node lists → **+101 added, 0 removed**. The 81 product nodes are 13 (RS1a) + 19 (RS1b) + 49 (RS2); the +20 over the 81 are census/seat/doc-driven parametrised nodes grown by the seat edit and the new `.dev-flow` artifacts (`test_keymap.py` +9, `test_repair_artifact_claims.py` +4, `test_inc9.py` +2, `test_inc9c.py` +2, `test_en5.py` +1, `test_app_imports_used.py` +1, `test_repair_map_truth.py` +1). **Later follow-up commits added further nodes on top of the +101** — the DDR-fix nodes (the C1/C2 signing fix, the Q1 width-parametrisation, the Q2 hostile-hint arm) and the RS2 review/UX follow-ups (N1/N2, F1–F6, U1–U5) landed after the DDR measurement; the final count is the orchestrator's full-suite line above, not the DDR's snapshot.

### Gaps detected
| ID | Requirement | Gap | Severity | Proposed action |
|----|-------------|-----|----------|-----------------|
| G-001 | test ledger | the `+101 / −0` is a DDR-time snapshot; later follow-up nodes are counted only by the final full-suite line | minor | declared, not a failure |
| G-002 | HLR-RS.1/2 | no success message after signing — the operator must decide whether a silent sign (cursor move only) is acceptable | minor | open operator decision; any new copy needs a prototype verdict |
| G-003 | HLR-RS.1 | real-user evaluation `not performed — one-person team` | minor | the operator owns the "does a real reviewer find this usable" judgement |

### Escaped-bug regression (if a defect escaped the suite)

Not applicable — the defects this batch shipped were caught in-review (RS2's seven finishing defects, `increment-003.md` §1) and by the full-suite gate (the truncator-census failures, 20 failed at `b549ca5` → fixed at `b9e7fa7`); each regression node has its RED-on-base proof in `evidence/rs2-red.transcript` and the DDR §B row 8.

### Evidence checklist — qa-reviewer (full)

| # | Item | ✓/✗ | Evidence |
|---|------|-----|----------|
| 1 | Every HLR/LLR has a result row | ✓ | Layer A: 5 HLR + 12 LLR rows |
| 2 | Every US has a passing AT | ✓ | Layer B: AT-090…107 across US-RS-001…004 |
| 3 | Every AT is one on-disk node | ✓ | DDR row 4: 18 ATs in 18 canonical nodes |
| 4 | Each unit has a named reddening mutation, RED observed | ✓ | Layer 0 mutation table; 33 mutants |
| 5 | Full suite executed and 0 failed | ✓ | ``3543 passed, 24 deselected, 3 xfailed, 13 warnings in 2029.79s (0:33:49)` — 0 failed; clean shell, code at ff6262f (847231b + gate record); the 24 deselected are the `slow` and `network` markers` (orchestrator run) |
| 6 | Walkthrough driven through the real mechanism, painted text asserted | ✓ | UX walkthrough tables (both widths) |
| 7 | Evidence honesty: `not performed — one-person team`; no success message — open decision | ✓ | UX limits; §G-002 |
| 8 | Test ledger reconciled | ✓ | `+101 / −0` measured at the DDR, + follow-ups declared |
| 9 | No secrets or personal paths in artifacts | ✓ | `tests/test_no_operator_paths.py` green in the full suite |
