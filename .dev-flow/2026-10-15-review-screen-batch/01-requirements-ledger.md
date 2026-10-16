# Requirements ledger — mapper — Batch 2026-10-15-review-screen-batch

> Append-only. Entries are added in chronological order and never rewritten. The live
> contract is `01-requirements.md`; this file records how it came to say what it says.
> Every entry names the requirement it amends; every requirement names its entries. `V26`
> compares the two sets of pairs both ways.

### LED-2026-10-15-review-screen-batch.1 — initial contract authored at P1

- **Requirement:** HLR-RS.1, HLR-RS.2, HLR-RS.3, HLR-RS.4, LLR-RS.1.1, LLR-RS.1.2, LLR-RS.1.3, LLR-RS.1.4, LLR-RS.2.1, LLR-RS.2.2, LLR-RS.2.3, LLR-RS.4.1
- **Date:** 2026-10-15
- **What changed:** initial authoring of the live contract from the four READY stories (B-134 verdict). Establishes the RS namespace (HLR-RS.1…4, LLR-RS.n.m), the acceptance ids AT-090…AT-097 (next free after the verified maximum AT-089), three increments (RS1 signing core · RS2 screen · RS3 seat/home/app), and mutants M-RS1…M-RS17.
- **Why:** the batch objective is the B-134 verdict; every threshold is a painted-frame string, a file-count/byte-count, or a named refusal, and each LLR names the mutant that reddens it.
- **Evidence:** `01-requirements.md` §2.7 premises 1–6, each with executed output (AT-number grep; `ls` of the two new files; `file:line` of `record_review`/`next_seq`/`object_digests`/`load_canon`/`head`/`effective_roles`; the `verdict="reviewed"` helper; the keymap `grep` for `v`/`b`/`4`/`enter`; `roles.py`'s worker/paint `file:line`s); `design/arq-note.md` §1.1 for the module-map census.

### LED-2026-10-15-review-screen-batch.2 — ruling R1: the signing core is a new `signing.py` leaf with named refusals

- **Requirement:** HLR-RS.2, HLR-RS.3, LLR-RS.2.1, LLR-RS.2.2, LLR-RS.2.3
- **Date:** 2026-10-15
- **What changed:** `mapper/reqharness/signing.py` (new, leaf of `derive`/`reviews`, no cycle) exposes `entitled_to_sign(repo, object_id, viewer) -> (bool, reason)` and `sign_review(repo, object_id, viewer, *, confirm_digest, confirm_head) -> record`. Pre-write checks, all named refusals: chain verified (not tampered/forked/no registry), viewer identity known and declared, viewer holds the designated role for that object type at the CURRENT head (B-121: only the designated role marks reviewed; one person may hold several roles), the object exists and is active (not retired), and the digest + head the user CONFIRMED still equal the current ones (TOCTOU between `b` and confirm → named refusal, nothing written). Writes through the existing `reviews.record_review` (immutable, exclusive create, content-named). A model review is never written by this path (human only); model reviews remain pre-review (derive's rule).
- **Why:** the one core gap (pre-write entitlement + digest/head binding) must live in a new module because `sign_review` imports `derive`, which imports `reviews` — a cycle if it sat in `reviews.py`. The orchestrator's R1 overrides the P0 spike's draft signature (`class_id`/`verdict`/`kind`/`note` params) in favour of `verdict="reviewed"`, `kind="human"`, class derived from the id prefix, and the two TOCTOU confirm parameters.
- **Evidence:** `spike/intake.md` core-gap census; `reviews.py:142`/`:206`, `derive.py:178`/`:155`, `chain.py:144-150`/`:285`; `tests/test_reqharness_registry.py:142` (`verdict="reviewed"`).

### LED-2026-10-15-review-screen-batch.3 — ruling R2: self-review is not forbidden; stated as an open question

- **Requirement:** HLR-RS.3
- **Date:** 2026-10-15
- **What changed:** no self-review prohibition for reviews in this batch. The core's no-self-approval rule (`chain._passes_approval`) applies to role changes, not reviews; B-122's "nobody approves their own change" is about role changes. Review entitlement is "holds the class's reviewer_role at the current head" alone; the canon object carries no author field. Recorded in §6.2 as an open question for the operator, not a requirement.
- **Why:** no ruling exists for reviews, and adding an author field to canon objects is out of scope.
- **Evidence:** `chain.py:304-331` (`_passes_approval` on role-change actions only); `derive.py` `CanonObject` has no author field.

### LED-2026-10-15-review-screen-batch.4 — ruling R3: the screen is variant A exactly as prototyped

- **Requirement:** HLR-RS.1, LLR-RS.1.1, LLR-RS.1.2, LLR-RS.1.3, LLR-RS.1.4
- **Date:** 2026-10-15
- **What changed:** `mapper/screens/review.py` = variant A exactly as prototyped (port the prototype's layout and copy; all UI copy English; no new strings beyond the prototype without a prototype verdict). Reads derived states from `derive`, the release verdict from `release.evaluate`, and paints through `Text` sinks only (registry text is untrusted). Git/identity discovery OFF the UI thread using the `roles.py` pattern (worker returns facts; applied in `on_worker_state_changed` with generation + `is_attached`), keys inert until first facts. Tampered/forked/no-registry → read-only with the reason, `b` inert with the reason.
- **Why:** the prototype verdict (variant A + the four sub-rulings) is binding and already validated in the target framework (D2 not fired), so no prototype round is owed; the copy and layout are the accepted design source.
- **Evidence:** `prototypes/review_screen/NOTES.md` §Verdict + `proto.py` `body_list_detail`/`_review_lines`/`_rule_table`; `roles.py:522-528` (worker), `:48` (Text sinks).

### LED-2026-10-15-review-screen-batch.5 — ruling R4: the seat is a home door + keymap scope in one increment

- **Requirement:** HLR-RS.4, LLR-RS.4.1
- **Date:** 2026-10-15
- **What changed:** a home door + keymap scope for the review screen in ONE increment (RS3) that owns the seat edit (keymap/home/app), with the guarded census pins moved and itemised. New `SCOPE_REVIEW` scope (+ `review-leave` group) and one home door key `v` (free in the home scope), `home.py` `_DOOR_NOTES` + `action_review`, `mapper.app` re-exports `ReviewScreen`. The increment order RS1 → RS2 → RS3 means the seat's `review`-scope actions resolve on `ReviewScreen` before the seat row lands.
- **Why:** the seat is the single source (K3); one owner increment stops two lanes from editing `keymap.py` (the RH6a precedent), and the door key must be free in the home scope.
- **Evidence:** `design/arq-note.md` §2 (seat consumer census); `keymap.py` `GROUP_SCOPE`/`GROUP_HEADER`/`KEYMAP`; `home.py:377-401` (`_DOOR_NOTES`/`_empty_text`); `tests/test_key_dispatch.py:177-179`, `tests/test_keymap.py:123,148`.

### LED-2026-10-15-review-screen-batch.6 — ruling R5: out of scope

- **Requirement:** HLR-RS.1
- **Date:** 2026-10-15
- **What changed:** out of scope: baseline/release VIEW, US canon extraction, generated views, B-124/B-125/B-126. The review screen signs and browses; it does not diff commit-vs-reviewer (B-124), show baselines (B-125) or recover forks (B-126 — the screen is read-only under fork, recovery stays core-only).
- **Why:** none of these is needed by the B-134 verdict; each has its own follow-up (prototype round first where a verdict is not yet given).
- **Evidence:** `spike/intake.md` §OUT; `PLAN.md` §Out-of-scope carries.

### LED-2026-10-15-review-screen-batch.7 — ruling R6: self-review is forbidden; authorship per owning batch in config

- **Requirement:** HLR-RS.5, LLR-RS.5.1, LLR-RS.5.2, HLR-RS.3, LLR-RS.2.2
- **Date:** 2026-10-15
- **What changed:** the operator decided 2026-10-15 to forbid self-review now (overriding R2's "open question"). `reqharness/config.yml` gains an admin-approved `authors` map (owning-batch id → list of declared person ids; validated: known people, unique; part of `config_hash`, so a change needs an approved `policy` event like any config change). The canon row's existing `Owning batch` column gives each object its batch, carried on `CanonObject.owning_batch`. `entitled_to_sign` refuses — with a named reason — when the signer's person id is an author of the object's owning batch. `derive` applies the SAME rule authoritatively: a human review whose reviewer is an author of the object's batch counts `unentitled` (never `reviewed`), so a hand-written record cannot bypass the screen. A batch with no `authors` entry = authorship not recorded → signing allowed; config may add an optional release rule `authors_declared` (fails when an active object's batch has no `authors` entry) — like `all_active_reviewed`, never mandatory.
- **Why:** the security reviewer's m7 accepted a permissive default only as an explicit operator decision; the operator made it before P3.
- **Evidence:** `REQUIREMENTS.md:5` (`Owning batch` column); `derive.py:148` (the column is dropped today — premise 8); `config.py:290-301` (no person/email uniqueness check — premise 9).

### LED-2026-10-15-review-screen-batch.8 — ruling R7: the seat merges into RS2 (screen + seat); RS3 dropped

- **Requirement:** HLR-RS.4, LLR-RS.4.1
- **Date:** 2026-10-15
- **What changed:** the QA BLOCKER (RS2 cannot go green before RS3) is resolved by merging the seat into RS2. New plan: RS1 core = `signing.py` (new) + `config.py` (authors) + `derive.py` (author rule) + `records.py` (`SigningRefused`) — 4 source files; RS2 screen + seat = `review.py` (new) + `keymap.py` + `home.py` + `app.py` — 4 source files. RS3 is dropped. Every guarded pin RS2 moves is itemised in §6.3 (the `test_inc9.py` OPENERS/HELP_SCREENS/CHROME_LEXICON/ENTRY_ROWS censuses, `test_cd25b`, `test_legend_design`, `test_repair_map_truth.py` via the ARCHITECTURE row, the door-count pins, A3/darkside censuses).
- **Why:** the door/`KEY_SCOPE`/bindings land with the screen, so the screen's ATs and the seat rows arrive in one increment and no increment depends on a later one.
- **Evidence:** QA review MAJOR-2 (the pin list); `docs/ARCHITECTURE.md` §2 `screens` row; `tests/test_inc9.py:79,132,376,715`.

### LED-2026-10-15-review-screen-batch.9 — ruling R8: one worker does all disk/git work; the sign intent captures one snapshot

- **Requirement:** HLR-RS.1, HLR-RS.2, LLR-RS.1.4, LLR-RS.2.3
- **Date:** 2026-10-15
- **What changed:** the worker runs ALL disk/git work (identity + `verify_chain` + `load_canon` + `derive` + `release.evaluate`) returning one immutable snapshot; `sign_review` (a disk write) also runs in a worker; results applied in `on_worker_state_changed` (generation + `is_attached`), as in `roles.py`. The thread is recorded per call, so a test asserts each ran off the UI thread (QA MAJOR-4). `b` arms a sign intent capturing `object_id`, digest, head and the snapshot; `enter` re-reads identity, re-verifies the chain and canon, and refuses unless object/digest/head/role-at-head/authorship all still match (QA MAJOR-5, sec m3).
- **Why:** the roles worker returned only git facts; `verify_chain`/`load_canon`/`derive`/`evaluate`/`sign_review` would otherwise run on the UI thread (`roles.py:543-549`).
- **Evidence:** `roles.py:522-528`; QA MAJOR-4/MAJOR-5; sec m3.

### LED-2026-10-15-review-screen-batch.10 — ruling R9: the 2 000-object scale LLR and the cold-`enter` AT

- **Requirement:** HLR-RS.1, LLR-RS.1.5
- **Date:** 2026-10-15
- **What changed:** new LLR-RS.1.5: a 2 000-object canon fixture; the `ReviewList` scrolls so the cursor row stays in view (after 1 999 `down` the selected id is in the painted frame); the bottom band stays on the last rows; one repaint after a cursor move ≤ 50 ms median of 5 (measured — recorded at P4, asserted in the suite at a generous ×10 bound, never a tight wall-clock assert). The widget is named `ReviewList`; `enter` is owned by the screen, so a cold `enter` does nothing (AT-098: 0 writes, no other action).
- **Why:** QA MAJOR-3 — no requirement/threshold existed for 2 000 objects; a DataTable/ListView binding `enter` could fire a second action.
- **Evidence:** QA MAJOR-3.

### LED-2026-10-15-review-screen-batch.11 — ruling R10: refusals are `SigningRefused` with a reason code; `now` names the clock

- **Requirement:** HLR-RS.2, LLR-RS.2.1, LLR-RS.2.4
- **Date:** 2026-10-15
- **What changed:** `sign_review` returns the written `Path` on success and raises `SigningRefused` (a `ValidationError` subclass in `records.py`) with a stable reason code + message on ANY refusal, including the `FileExistsError` on the content-named file (reason `already_signed`) and the review-file count limit (`review_limit`); the screen shows the message on the hint line. `sign_review(..., now=None)` → UTC now; tests pass a fixed `now`. Every record field is specified: `note=""`, `class_id` from the canon object (not the id prefix). Two signers: different content → both files, duplicate `seq` harmless; identical content → `SigningRefused(already_signed)` (one AT). The inherited confinement race is a stated residual.
- **Why:** QA MAJOR-6 (raise-vs-return unspecified; `now` not a parameter) and sec m4/m5/m6.
- **Evidence:** `records.py:13-25` (the `ValidationError`/`YamlRefusal` ladder); `config.py:65` (`LIMIT_REVIEW_FILE_COUNT`); `reviews.py:199` (the `FileExistsError` site).

### LED-2026-10-15-review-screen-batch.12 — ruling R11: active + class-declared object; one identity match; no CLI entry point

- **Requirement:** HLR-RS.2, HLR-RS.3, LLR-RS.2.2, LLR-RS.2.4
- **Date:** 2026-10-15
- **What changed:** sec MAJOR-1 — `entitled_to_sign` requires the object ACTIVE (not withdrawn/retired) and its class declared; the truth table gains `(False, retired)` and `(False, class-undeclared)` arms. sec MAJOR-2 — reworded: the path writes `kind: human` but cannot PROVE a human pressed the key (an agent in the operator's shell inherits the operator's git identity); `sign_review` has NO CLI/entry-point exposure (no `console_scripts` entry, no `--sign` flag in `app.py`, only `screens/review.py` imports `signing`), pinned by a grep/AST test. sec m1 — the impersonation residual moves into HLR-RS.3 too (§6.3 no longer says "answered" for it). sec m2 — exactly ONE declared person must match the viewer identity; zero/several → named refusal; config validation refuses duplicate person ids / duplicate `email_sha256`.
- **Why:** sec MAJOR-1/MAJOR-2, m1, m2.
- **Evidence:** `config.py:290-301` (no uniqueness check); `roles.py:242` (first match); `chain.py:144-150` (head).

### LED-2026-10-15-review-screen-batch.13 — ruling R12: QA minors — payload list, cell-width truncation, 118/87 for every AT, the Copy table

- **Requirement:** HLR-RS.1, LLR-RS.1.1, LLR-RS.1.2, LLR-RS.1.3, LLR-RS.2.3
- **Date:** 2026-10-15
- **What changed:** the hostile payload list is ESC, U+202E, U+200B, NEL, wide CJK, combining (no surrogates — they cannot exist in UTF-8); truncation is by cell width, not `len`; every screen AT renders at both 118 and 87; AT-094 adds an undeclared viewer, no git identity and no registry; AT-091 asserts all three open states present; after a sign in the "needs action" preset the cursor moves to the next row (or stays on the last); the exact set of new UI strings (armed hint, refusals, empty canon) is listed in §6.6 "Copy" and goes to the operator for a verdict at PDR — nothing outside that table may appear.
- **Why:** QA minors.
- **Evidence:** §6.6; QA review "MINOR".

### LED-2026-10-15-review-screen-batch.14 — copy verdict (operator 2026-10-15, "Aprobado"): two string changes + the any-key-cancels rule

- **Requirement:** LLR-RS.2.3
- **Date:** 2026-10-15
- **What changed:** the operator returned the §6.6 Copy-table verdict **`Aprobado`** with exactly two changes, the other 12 strings unchanged:
  - Before `SIGN-ARMED` = `sign <object> at head <hash> — press enter to confirm, any other key to cancel` → After `sign <object> · digest <sha8> · head <hash> — enter confirms, any other key cancels` (now carries the digest, as `<sha8>`).
  - Before `REFUSE-MOVED` = `cannot sign: the content or head moved — press b to re-arm` → After `cannot sign: something changed since b (object, content, head or role) — press b to re-arm`.
  The verdict's binding rule: while armed, ANY key other than `enter` — including `escape` **and** `q` — cancels the arm and does NOT leave the screen. LLR-RS.2.3 amended accordingly (the `q`-while-armed arm added; armed `escape`/`q` cancel, not-armed `q`/`escape` leave). This also closes re-check **Minor 3** (SIGN-ARMED carries the digest) and the `q` half of the semantics.
- **Why:** the copy table was pinned at P2 (QA-m6) and owed a verdict at PDR; the operator gave it, and the armed-state key semantics had to follow it.
- **Evidence:** §6.6 (updated strings + verdict note); `02-review.md` §"Copy verdict"; LLR-RS.2.3 statement/negative control.

### LED-2026-10-15-review-screen-batch.15 — P2 re-check minors 1/2/4/5 + blank-`Owning batch` cell + truth-table arm count

- **Requirement:** LLR-RS.1.5, LLR-RS.2.1, LLR-RS.2.2, LLR-RS.2.3, HLR-RS.5, LLR-RS.5.1, LLR-RS.5.2
- **Date:** 2026-10-15
- **What changed:**
  - **Minor 1** — AT-101 gains a negative control, mutant **M-RS25** (cursor reset to row 0 instead of moving to the next row). LLR-RS.2.3 negative control + §5.1.
  - **Minor 2** — LLR-RS.1.5's wall-clock repaint is demoted to a P4 measurement only; the suite asserts a non-flaky **counted-operations bound** ("the number of painted rows per repaint does not grow with N"). Statement + threshold rewritten.
  - **Minor 4** — REFUSE-MOVED covers object/content/head/role; each re-check failure maps to one `SigningRefused` reason code — `moved_object` · `moved_digest` · `moved_head` · `moved_role` (LLR-RS.2.1 statement, LLR-RS.2.3 statement, §6.3 TOCTOU note).
  - **Minor 5** — LLR-RS.1.5 now states `ReviewList` binds NO `enter` (the screen owns it) + mutant **M-RS26** (`ReviewList` binds `enter`).
  - **Blank `Owning batch` cell** — declared the same as "batch not in `authors`": authorship not recorded, signing allowed, no review marked `unentitled` on that ground. Stated in HLR-RS.5, LLR-RS.2.2, LLR-RS.5.1, LLR-RS.5.2.
  - **Truth-table arm count** — reconciled to 10 `(False, reason)` arms + 1 `(True, "")`; LLR-RS.2.2's threshold "9 arms plus the author arm" corrected to 10; `PLAN.md` roadmap (RS1) agrees.
  - **Why:** the P2 re-check (approve-with-conditions) left these five conditions open; each is closed with a named mutant or an explicit declaration.
- **Evidence:** `02-review.md` §"P2 re-check"; LLR-RS.1.5/2.1/2.2/2.3, HLR-RS.5, LLR-RS.5.1/5.2 (amended text).

### LED-2026-10-15-review-screen-batch.16 — PDR UX review (U1–U4): elision, armed style, loading key bar, prototype copy provenance

- **Requirement:** LLR-RS.1.3, LLR-RS.1.4, LLR-RS.2.3
- **Date:** 2026-10-15
- **What changed:**
  - **U1** — long ids/names elide the MIDDLE of `<object>` and `<viewer>` (cell-width aware, `…`), never the tails `enter confirms, any other key cancels` / `press b to re-arm`; AT-103 at 87 arming on the longest id asserts the tail is present (negative control M-RS31 — the elision cuts the tail instead of the middle).
  - **U2** — the armed hint line and the armed row use the `darkside` ACCENT token; refusals (`cannot sign: …`) use the roles-screen refusal ALERT/WARN token; no new tokens or chrome; asserted in the painted frame (AT-104; negative control M-RS32 — the style token dropped).
  - **U3** — while loading the key bar advertises only `escape` (the roles-screen precedent); when tampered/no-registry `b` is hidden; while armed the bar reads `enter sign · any other key cancel`; bar labels come from existing keymap descriptions, and any new label is added to §6.6 marked `key-bar label`.
  - **U4** — the strings outside the §6.6 table (filter line, `release readiness`, `release readiness — BLOCKED`, the `⁂ informative mark …` legend, `b mark reviewed — …`, `object detail`, `statement`, `digest now`, `review history`, `not verifiable`) come from the operator-approved PROTOTYPE; §6.6 lists them "from the approved prototype"; AT-105 pins that the screen paints no string outside §6.6 ∪ the prototype set (negative control M-RS30); the §9.1 87-col render is fixed (73 cells inside a 71-cell border) and 87 renders are scroll-trimmed.
- **Why:** the ux-reviewer (Claude Sonnet) approved with conditions; each closes on the existing `darkside` tokens, the keymap seat and §6.6 rather than on new chrome.
- **Evidence:** §6.6 (updated); LLR-RS.1.3/1.4/2.3 (amended); `design/design-proposal.md` §9 (fixed 87 render, scroll-trimmed note).

### LED-2026-10-15-review-screen-batch.17 — PDR security review (F1–F6): owning-batch record field, seed rule, sign-in-flight, unapproved config

- **Requirement:** HLR-RS.2, HLR-RS.5, LLR-RS.2.1, LLR-RS.2.3, LLR-RS.5.1, LLR-RS.5.2
- **Date:** 2026-10-15
- **What changed:**
  - **F1 (HIGH)** — the review record STORES the object's owning batch at sign time (new `owning_batch` field on `record_review`'s payload, LLR-RS.2.1); `derive` treats a human review whose stored owning batch differs from the object's current cell as NOT counting (`unentitled`, distinct reason `owning_batch_mismatch` — LLR-RS.5.2). The cell is NOT added to the digest (that would invalidate existing reviews). Records written before this batch lack the field → evaluated as today (legacy). §10's "self-review residual: none" is corrected to a stated residual.
  - **F2 (MED)** — `create_registry` seeds new registries with an empty `authors` map and `authors_declared` ENABLED; the rule fails on any active object whose owning batch is blank OR absent from `authors`; an unknown owning batch is reported by name; batch ids compared after NFC normalisation (exact otherwise — no case folding); signing itself stays allowed when authorship is not recorded (LLR-RS.5.1, HLR-RS.5).
  - **F3 (MED)** — stated residual in HLR-RS.5 + new backlog item B-135 ("a change to `authors` needs a second admin").
  - **F4 (LOW)** — stated residual: one human declared twice with two emails.
  - **F5 (LOW)** — the screen disarms on the UI thread before starting the sign worker; at most one sign in flight; `b`/`enter` inert while it runs; AT-106 + negative control M-RS28.
  - **F6 (LOW)** — `sign_review` refuses unless `config_digest(config) == report.policy_config_hash` (reason code `unapproved_config`) (LLR-RS.2.1).
- **Why:** the security-reviewer (Claude Opus) approved with conditions; F1 was BLOCK-UNTIL before RS1 and is the only overclaim corrected.
- **Evidence:** LLR-RS.2.1/2.3/5.1/5.2, HLR-RS.2/5 (amended); `design/design-proposal.md` §10 (threat map corrected); `.dev-flow/BACKLOG.md` B-135.

### LED-2026-10-15-review-screen-batch.18 — PDR architecture review (A1–A8): RS1 split, identity-in-signing, safe_verify, ScrollView

- **Requirement:** LLR-RS.1.4, LLR-RS.1.5, LLR-RS.2.1, LLR-RS.2.2, LLR-RS.5.1, LLR-RS.5.2
- **Date:** 2026-10-15
- **What changed:**
  - **A1** — RS1 is split: **RS1a** = `signing.py` (new), `config.py`, `derive.py`, `records.py`; **RS1b** = `release.py` (the `authors_declared` rule + the `Derivation` field it needs; if `derive.py` must change for that field, the change lands in RS1a). RS2 unchanged (`review.py`, `keymap.py`, `home.py`, `app.py`).
  - **A2** — `authors` is optional; absent AND empty are both omitted from `canonical_config`, so existing registries keep their `config_hash`; test that an existing config's digest is unchanged; the new duplicate-id/duplicate-email refusals can reject configs that load today (acceptable — no external users; stated) (LLR-RS.5.1).
  - **A3** — `entitled_to_sign`/`sign_review` take the git IDENTITY (email), hash it and resolve to exactly one declared person inside `signing`; zero/several → named refusal; truth table stays 10 false arms (LLR-RS.2.2, `arq-note.md` §3).
  - **A4** — loader `ValidationError`s (`verify_chain`, `load_config`, `load_canon`) become `SigningRefused`/`(False, code)` via `release.safe_verify` or equivalent — never a bare exception into the worker (LLR-RS.2.1).
  - **A5** — ARCHITECTURE amendments: §3 `screens` row names `review.py` as allowed to import `reqharness`; the `reqharness` row exposes `entitled_to_sign`, `sign_review`, the `authors` schema, and "only `screens/review.py` imports `signing`"; `arq-note.md` §1.2 item 2 retargets RS3 → RS2 (`arq-note.md`).
  - **A6** — `ReviewList` base = a line-based `ScrollView` with `render_line` (binds no keys); the counted-operations bound = `render_line` calls per cursor move (LLR-RS.1.5).
  - **A7** — sign data flow explicit: identity re-read + chain re-verify run INSIDE the sign worker; the sign result passes the same generation + `is_attached` guard; one sign in flight (F5); a successful sign bumps the generation and re-runs the snapshot (LLR-RS.1.4).
  - **A8** — the author rule is retroactive (live `authors` map, not the map at the review's bound head) → recorded as a decision; `derive`'s docstring names `unentitled`'s three causes (role · author · owning-batch mismatch); `audit.py` counts them together (LLR-RS.5.2).
- **Why:** the architect (Claude Opus) approved with conditions; the split keeps every increment ≤ 4 source files and RS1b is the `release.py` change RS1's fifth file needed.
- **Evidence:** `PLAN.md` (roadmap split + decision-log rows); LLR-RS.1.4/1.5/2.1/2.2/5.1/5.2 (amended); `design/arq-note.md` §1.2/§3 (amended).

### LED-2026-10-15-review-screen-batch.19 — PDR QA review (Q1–Q9 + minors): pin lists, render-window asserts, reason-code literals, fixtures

- **Requirement:** HLR-RS.1, HLR-RS.4, LLR-RS.1.1, LLR-RS.1.2, LLR-RS.1.3, LLR-RS.1.4, LLR-RS.1.5, LLR-RS.2.1, LLR-RS.2.2, LLR-RS.2.4, LLR-RS.4.1
- **Date:** 2026-10-15
- **What changed:**
  - **Q1** = A1 (the RS1 split — covered by LED `.18`).
  - **Q2** — pin-list additions: `tests/test_mod_parity.py:56-62` home golden sha256 (new `v` door, RH6a precedent); `tests/test_darkside_census.py:~413` severity sites `== 54` + ADJUDICATED rows; `tests/test_app_imports_used.py:50-58` `ReviewScreen` allowance; `tests/test_a3_census.py` — says exactly why it moves (render-protocol census) or is removed; `tests/test_inc9.py:132` adds a `"ReviewScreen"` opener (`~:127`).
  - **Q3** — AT-090/091 at 87×34 fit ~4 rows: at 87 assert per scroll window (scroll and assert each window), keep the 118 arm on the full 10-object fixture.
  - **Q4** — AT-099 names the counter (`render_line` calls per move) + mutant **M-RS27** ("repaint all N rows per move").
  - **Q5** — AT-101/M-RS25 vacuous on row 0: sign a middle row (k≥1) + a last-row case.
  - **Q6** — AT-096 payloads add markup brackets (`[bold]x[/]`, `[/]`) (roles precedent `test_roles_screen.py:361`).
  - **Q7** — AT-094: no git identity → REFUSE-VIEWER; no registry → REFUSE-CHAIN with status `no registry yet` (mapped explicitly; no new strings).
  - **Q8** — AT-092/M-RS10: two fixtures (ready / not ready), each asserted equal to `release.evaluate(...).text`.
  - **Q9** — M-RS13 popped-screen test (copy `tests/test_fixes_roles_thread.py:~200` late SUCCESS on a dead screen); AT-107 recorders on `verify_chain`, `load_canon`, `derive_states`, `release.evaluate`, `sign_review`, patched where the screen looks them up, asserting a NON-EMPTY record.
  - **QA minors** — move M-RS5/M-RS14 to TC-RS-2.2.2 / TC-RS-2.1.2; M-RS24 hash-differs assertion into TC-RS-5.1.1; test that an authors-less config hashes byte-identically to today; pin literal reason-code strings; precedence `moved_role` vs `moved_head` (a revoke moves the head: report `moved_role` when the role is lost, else `moved_head`) and `moved_object` vs `unknown_object` (object gone → `unknown_object`); each truth-table arm a single-failure fixture; a canon id whose prefix differs from its class; mutant `b`, `down`, `enter` writes 0 files (M-RS33).
- **Why:** the qa-reviewer (Claude Sonnet) approved with conditions; each closes a vacuous or under-pinned assertion with a named mutant or fixture.
- **Evidence:** `PLAN.md` (RS2 pin list completed); LLR-RS.1.1/1.2/1.3/1.4/1.5/2.1/2.2/2.4, HLR-RS.1/4 (amended); §5.1 (AT/TC/M-RS lists extended).

### LED-2026-10-15-review-screen-batch.20 — ruling R18: RS1 re-split by layer (RS1a = data, RS1b = logic)

- **Requirement:** HLR-RS.2, HLR-RS.5, LLR-RS.2.1, LLR-RS.5.1, LLR-RS.5.2
- **Date:** 2026-10-15
- **What changed:** RS1 is re-cut BY LAYER (after the RS1a stop report). **RS1a = the data layer**: `reviews.py` (the optional `owning_batch` record field, F1), `records.py` (`SigningRefused(ValidationError)` + the stable reason-code literals `no_role`/`author`/`owning_batch_mismatch`), `config.py` (the optional `authors` schema + duplicate person-id/`email_sha256` refusal; `create_registry` seeds `authors: {}`; absent AND empty `authors` omitted from `canonical_config`), `derive.py` (`unentitled` with three causes, `owning_batch` on `CanonObject`, legacy records evaluated as today). **RS1b = the logic**: `signing.py` (new) + `release.py` (the `authors_declared` rule). Consequence recorded: seeding the `authors_declared` release-rule id into `_DEFAULT_RELEASE_RULES` makes `release.evaluate` return `unknown release rule 'authors_declared'` until RS1b's `release.py` registers it, so RS1a seeds `authors: {}` and the `authors_declared` ENABLED seed + rule land in RS1b.
- **Why:** `signing.py` is orchestration/entitlement logic over the data surfaces; the `owning_batch` record field is data (F1) that must land before the logic reads it. Splitting by layer keeps every increment ≤ 4 source files AND separates "what is stored/validated/derived" from "the decision path that orchestrates them".
- **Evidence:** `PLAN.md` Roadmap (RS1a/RS1b re-cut) + decision-log R18; `01-requirements.md` §2.8 (disjoint file sets) + §5.1 (Layer A test files); `design/design-proposal.md` §8.

### LED-2026-10-15-review-screen-batch.21 — security re-verification follow-up (RS1a gate): H1/M2/L1/L2 fixes

- **Requirement:** HLR-RS.5 · LLR-RS.5.1 · LLR-RS.5.2 · LLR-RS.2.1 (F1)
- **Date:** 2026-10-15
- **What changed:** The security reviewer returned REQUEST-CHANGES at the RS1a gate (F1 still OPEN). Four fixes landed: **H1 (HIGH)** — with `authors` declared (non-empty), a human review whose record has no `owning_batch` (absent or `""`) is now `unentitled` with a new stable reason `owning_batch_missing` (literal added to `records.py` beside the others); when `authors` is empty/absent, behaviour is exactly as today. **M2 (MED)** — the canon `Owning batch` cell is NFC-normalised in `parse_canon` (via the package `nfc()`), so a decomposed batch id in the cell compares against the NFC config key and cannot evade the author rule. **L1 (LOW)** — duplicate person ids inside one batch's `authors` list are refused by name in `validate_config`. **L2 (LOW)** — `test_an_authors_less_config_hashes_byte_identically_to_today` now pins the pre-RS1a authors-less `config_hash` as a constant (`PRE_RS1A_AUTHORS_LESS_DIGEST`), computed from `git show 05c516a~1:mapper/reqharness/config.py` loaded as a separate module.
- **Why:** F1's probe — an author who hand-writes a legacy-format review record and then blanks or moves the object's `Owning batch` cell still derives `reviewed`, because the missing field skipped the mismatch check; a decomposed cell evaded the NFC config-key comparison; duplicate author ids were accepted; and the empty-vs-absent digest comparison was vacuous against a shared drift.
- **Evidence:** 4 new test nodes in `tests/test_reqharness_registry.py` (`test_derive_marks_a_legacy_review_without_owning_batch_unentitled_when_authors_declared`, `test_derive_a_legacy_review_without_owning_batch_stays_reviewed_without_authors`, `test_derive_nfc_normalises_the_owning_batch_cell`, `test_config_refuses_a_duplicate_person_id_in_one_authors_list`) + the re-pinned `test_an_authors_less_config_hashes_byte_identically_to_today`; RED proofs appended to `evidence/rs1a-red.transcript` (§5–§8); `24 passed` in `tests/test_reqharness_registry.py`.

### LED-2026-10-15-review-screen-batch.22 — M1 residual: moving the `Owning batch` cell (no code)

- **Requirement:** HLR-RS.5 (self-review prohibition) — stated residual
- **Date:** 2026-10-15
- **What changed:** Stated residual (no code): an author who can edit the canon can move an object's `Owning batch` cell to a batch they are not listed for BEFORE signing; including the cell in the digest does not stop it, because the author signs after the move. Mitigations: canon edits are git/PR-reviewed; `authors_declared` requires every batch to be declared; full closure needs per-object authorship (the operator chose per-batch, R6).
- **Why:** Per-batch authorship is the operator's chosen granularity (R6); a per-object author field was rejected as a schema change across every canon fixture.
- **Evidence:** `design/design-proposal.md` §10 (new M1 row) · `design/PDR-2026-10-15-review-screen-batch.md` §E (Amendments after the seal) · `.dev-flow/BACKLOG.md` B-135 (note).

### LED-2026-10-15-review-screen-batch.23 — RS1b code-review follow-up (F1–F6): single snapshot, import census, required keyword, moved precedence, two signers, typed refusals

- **Requirement:** LLR-RS.2.1 · LLR-RS.2.4 · LLR-RS.2.2
- **Date:** 2026-10-15
- **What changed:** The independent RS1b code review returned REQUEST-CHANGES (BLOCK-UNTIL F1, F2). Six fixes landed:
  - **F1 (HIGH)** — `signing.py` extracts a PURE `_entitlement(report, config, canon, viewer, object_id) -> (bool, code)`; `entitled_to_sign` loads once and calls it, and `sign_review` calls it with ITS OWN snapshot — `safe_verify`/`load_config`/`load_canon` each run EXACTLY once per sign (no second load for the role/author decision). The retired/class-undeclared ordering is now canonical in the single helper.
  - **F2 (HIGH)** — the exposure census now scans every `.py` under `mapper/` AND `tests/`, and catches the absolute (`from mapper.reqharness.signing import x`, `import mapper.reqharness.signing`), package-qualified (`from mapper.reqharness import signing`) and relative (`from . import signing`, `from .signing import x`, level 1 inside `mapper/reqharness/`) forms. Allowlist: `screens/review.py` (RS2, not yet written) + `tests/test_reqharness_signing.py`.
  - **F3 (MED, SPEC CLARIFICATION)** — `confirm_owning_batch` becomes a REQUIRED keyword (no default). Orchestrator-accepted stricter internal API; no user-visible change (the RS2 screen passes its sign-intent owning batch). LLR-RS.2.1's signature text amended.
  - **F4 (MED)** — the TOCTOU re-checks run in the documented order `moved_object` (owning batch) → `moved_digest` → `moved_head` → `moved_role`; an object AND digest both moved reports `moved_object`. Docstring and code now agree.
  - **F5 (MED)** — new node: two different entitled signers sign the SAME object with different content → two review files, both load, duplicate `seq` tolerated.
  - **F6 (LOW)** — `records.py` gains typed `ReviewLimitError` / `AlreadySignedError` (`ValidationError` subclasses); `reviews.py` raises them; `signing.py` maps them BY TYPE (not message text) to `review_limit` / `already_signed`.
- **Why:** F1/F2 were BLOCK-UNTIL correctness/security pins; F3 records the stricter internal API as an accepted deviation; F4 fixes a docstring/code disagreement; F5/F6 close under-pinned boundary cases.
- **Evidence:** `tests/test_reqharness_signing.py` (18 nodes; 5 new); RED proofs appended to `evidence/rs1b-red.transcript` ("Code-review follow-up"); `increment-002.md` "Code-review follow-up" section.
