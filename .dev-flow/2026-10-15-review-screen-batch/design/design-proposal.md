# Design proposal — mapper — Batch 2026-10-15-review-screen-batch

> **Artifact language.** English (`state.json` `language: en`).
> **Owed in.** `core` by trigger · `full` ✓ (PDR fired: A2, A3, D1, E1 — `PLAN.md` §Triggers).
> **Written against:** `01-requirements.md` (P2-reviewed + re-checked + PDR-amended), `01-requirements-ledger.md` (LED .1–.19), rulings R1–R17 (`PLAN.md` §Decision log), `design/arq-note.md` (the module map), and the B-134 prototype verdict (`prototypes/review_screen/NOTES.md`).
> **Proportionate on purpose:** where the requirements already hold the design (§6.2, §6.3, the IFC §4, the ARQ note), this cites it instead of restating it. §9 and §10 are the two lenses the fired triggers owe (D1 UX, C1/C8 security).
> **Evidence rule:** every render below was produced by running the prototype headless (Rich `Console` export of `proto.py`'s `_status_line` / `body_list_detail` / `_release_panel` over the real `darkside` tokens) — or is marked **hand-composed** where the prototype does not paint that state. No product or test file was edited to produce this document.

| Field | Value |
|---|---|
| Id | `PDR-2026-10-15-review-screen-batch` |
| Requirements covered | US-RS-001…004, HLR-RS.1…5, LLR-RS.1.1…1.5, LLR-RS.2.1…2.4, LLR-RS.4.1, LLR-RS.5.1…5.2, AT-090…107; rulings R1–R17 |
| Modules touched (from `docs/ARCHITECTURE.md`) | `reqharness` (new `signing.py`; `config.py`, `derive.py`, `records.py`, `release.py` amended) · `screens` (new `review.py`; `home.py` amended) · `keymap` · `app` (re-export only) |
| Triggers that fired | A2 · A3 · B4 · C1 · C8 · D1 · E1 |
| Author / reviewers | `software-dev` (author) · `architect` · `qa-reviewer` · `ux-reviewer` (D1 fired) · `security-reviewer` (C1/C8 fired) |

---

## 1 · Objective and scope

Implement the ReqHarness **REVIEW / SIGNING screen** (B-134, prototype verdict 2026-10-15: variant A list + detail, with variant C's queue as a "needs action" filter preset) and its **headless signing core**, in three serial increments: **RS1a** (signing core + authorship), **RS1b** (the `release.py` `authors_declared` rule) then **RS2** (screen + seat). The screen reads derived states from `derive.derive_states` (never re-derived), the release verdict from `release.evaluate`, and signs only through a new `signing.sign_review` orchestration that writes via the existing `reviews.record_review` API. Two-key confirmed signing (`b` arms, `enter` confirms), a fixed bottom release band, the `⁂` informative badge, and — per the operator's authorship decision (R6) — a self-review prohibition enforced at the pre-flight (`entitled_to_sign`) and authoritatively in `derive`.

**Will not do:** the baseline/release VIEW screen, US-canon extraction, generated MD/HTML views, B-124 (committer-vs-reviewer email warning), B-125 (baseline `reactivated`), B-126 (fork-recovery UI). Each stays out; none is needed by this screen.

---

## 2 · Modules and boundaries

| Module | What it owns here | What it exposes | What it must NOT reach into |
|---|---|---|---|
| `reqharness/signing.py` (new) | the pre-flight predicate and the orchestrated write path | `entitled_to_sign(repo, object_id, identity_email) -> tuple[bool, str]`, `sign_review(repo, object_id, identity_email, *, confirm_digest, confirm_head, now=None) -> Path` (A3: takes the git identity email, resolves to exactly one declared person inside `signing`) | Textual, Rich, `screens/**`, `app` |
| `reqharness/config.py` | the optional `authors` map schema (batch id → person ids) + person/email uniqueness; `authors` folded into `canonical_config` ONLY when present and non-empty (A2: absent and empty both omitted, so existing digests are unchanged) | `validate_config`, `canonical_config`, `config_digest`, `create_registry` (seeds `authors: {}` + `authors_declared` ENABLED) | unchanged from today |
| `reqharness/derive.py` | `CanonObject.owning_batch` (no longer dropped) + the author rule + the stored-owning-batch mismatch arm in `derive_states` (three causes of `unentitled`: role · author · owning-batch mismatch) | `CanonObject` (one new field), `derive_states`, `parse_canon` | unchanged edges (still a leaf importing `reviews`) |
| `reqharness/records.py` | `SigningRefused(ValidationError)` with a `reason` code + interpolation fields | `SigningRefused` | unchanged |
| `reqharness/release.py` (RS1b) | the `authors_declared` release rule + the `Derivation` field it needs | `evaluate`, `safe_verify` (loader `ValidationError` → `SigningRefused`) | unchanged edges |
| `screens/review.py` (new) | the variant-A screen: `ReviewList`, detail pane, bottom band, `b`/`enter` sign intent, the one-thread worker | `ReviewScreen`, `ReviewList`, `KEY_SCOPE = SCOPE_REVIEW` | direct writes to `reviews/` or `roles.yml` — it signs only through `signing.sign_review` |
| `keymap.py` | `SCOPE_REVIEW = "review"`, the `review` group + `review-leave` group, review-scope rows (`up`/`down`/`4`/`b`/`enter`), leave rows (`q`/`escape`), the home door `v` | the seat rows (additive only) | nothing new |
| `screens/home.py` | `_DOOR_NOTES["v"]` + `action_review` | the door (push `ReviewScreen`) | nothing new |
| `app.py` | re-export `ReviewScreen` | `ReviewScreen` in `__all__` | nothing new |

- Boundaries respected as declared in `docs/ARCHITECTURE.md`: ✓ — no boundary moves and no dependency edge is added (`arq-note.md` §1). The map owes the one F1 amendment (append `mapper/screens/review.py` to the `screens` row's paths + exposes) and the two seat notes, landed by RS2 (the file's increment) before the file is created (`arq-note.md` §1.2).

---

## 3 · Diagrams

Two viewpoints apply: **state dynamics** (the worker → screen hand-off, and the sign → refresh cycle) and **information** (the data the sign path threads). The rest are already held in `01-requirements.md` §4 (the Information Flow Contract) and `arq-note.md` §3.

**Review screen, state dynamics** (the only new state: `_snap`, `_gen`, `_armed`):

```text
push v ── compose (chrome + 4 Statics + hint) ── on_mount ─┐
                                                            ├─ _start(): gen += 1, one worker(gen)
                          on_screen_resume (fires at push)─┘    thread: repo_root, identity.read,
                                                                 verify_chain, load_config, load_canon,
                                                                 load_reviews, derive_states,
                                                                 release.evaluate  →  ONE _Snapshot
                                                                 ▼
  _snap is None ── keys up/down/4/b/enter inert; escape/q leave ── worker RETURNS; on_worker_state_changed(SUCCESS)
                                                                   │ applied on the UI thread; if gen != latest or not is_attached: drop
                                                                   ▼
                                               _snap = snap; _paint() (list + detail + band)
   b (armed only when entitled) ── _armed = SignIntent(object_id, digest, head, _snap)
                                  ── hint = SIGN-ARMED (digest[:8], head hash), ACCENT token
   enter (armed) ── DISARM on the UI thread (F5) ── start ONE sign worker (at most one in flight):
                     the worker re-reads identity + re-verifies chain/canon INSIDE itself (A7),
                     then signing.sign_review(root, object_id, identity_email,
                                              confirm_digest, confirm_head)
                     ── result applied through the SAME generation + is_attached guard
                     ── success bumps the generation and re-runs the snapshot worker
   any other key (armed) incl. escape/q ── cancel the arm, stay on the screen
   q/escape (not armed) ── leave (pop to home)
```

**Sign path, information** (one snapshot threaded through the entitlement check, the TOCTOU comparison and the write — sec m3; the re-read + re-verify run INSIDE the sign worker — A7):

```text
b: capture  (object_id, normative_digest, report.head, _Snapshot)
enter: DISARM on the UI thread, then the sign worker:
       identity re-read (identity.read) + verify_chain, re-checked against the SAME _Snapshot
       sign_review(repo, object_id, identity_email, confirm_digest, confirm_head, now):
         load_config → verify_chain (refuse !report.ok)
         → refuse unless config_digest(config) == report.policy_config_hash (unapproved_config)
         → load_canon (refuse unknown id) → object_digests → entitled_to_sign (refuse (False, code))
         → compare confirm_digest/confirm_head + object/role-at-head (refuse moved_*)
         → next_seq → record_review(class_id from canon, verdict="reviewed", kind="human",
                                     note="", reviewer=viewer, owning_batch=stored, head)
         → Path   |   raise SigningRefused(code, message, **fields)
       result applied through generation + is_attached; success bumps generation
refresh: _start() re-runs the one worker; derive re-reads the written file (B4 output-then-consume)
```

**`ReviewList`** is a line-based `ScrollView` exposing `render_line`; it binds NO keys (A6), and the counted-operations bound is the number of `render_line` calls per cursor move (AT-099, M-RS27). **`unentitled`** has three causes in `derive` (A8): `no_role` · `author` · `owning_batch_mismatch`, counted together by `audit.py`.

---

## 4 · Interfaces that change — and which ones FREEZE

| Interface | Current | After | Consumers | **Frozen for the fork?** |
|---|---|---|---|---|
| config `authors` map (A3) | absent; `_CONFIG_KEYS` = `{version, people, roles, classes, release_rules}` | optional `authors: {batch_id: [person_id, …]}`; validated (unknown person refused, duplicates in `people` refused); folded into `canonical_config` | `derive` (author rule), `signing` (author arm), `release` (`authors_declared` rule), the config censuses | n/a — one lane (`01-requirements.md` §2.8) |
| `derive.CanonObject` / `parse_canon` | `owning batch` column dropped at `derive.py:148`; no field | carries `owning_batch: str`; `derive_states` marks an author's human review `unentitled` | `signing` (author arm), the derivation tests | n/a |
| `records.SigningRefused` (new) | none | `SigningRefused(ValidationError)` with `.reason` (code) + `.fields` (interpolation) | `signing` (raises), `screens/review.py` (maps code → §6.6 string) | n/a |
| `signing` public API (new) | none | `entitled_to_sign`, `sign_review` — headless, **no CLI/entry-point exposure** | `screens/review.py` only (pinned by grep/AST, LLR-RS.2.4) | n/a |
| keymap seat | no `review` scope; `v` free in home | `SCOPE_REVIEW`, `review` + `review-leave` groups, review rows, home door `v` | every screen via `screen_bindings`/`groups_for_keybar`; the seat census tests | additive; no existing `KeyBinding` moves |
| `ReviewScreen` / `ReviewList` (new) | none | `ReviewScreen` (KEY_SCOPE `review`), `ReviewList` (no `enter` binding), `app` re-export | `screens/home.py` (`action_review`), `app.py` | n/a |

**Not touched inside this batch (the invariants the tests defend):** `reviews.record_review` / `next_seq` / `load_reviews` (the write path is unchanged — `sign_review` calls it), `chain.verify_chain` / `effective_roles` / `propose` / `approve_pending` / `reject_pending`, `release.evaluate` / `safe_verify`, `identity.py` (the hardened git allowlist is read, never edited), every on-screen string except the §6.6 set, all `roles.yml`/`reviews/*.yml`/config goldens.

---

## 5 · Proposed test cases

All names are the ones fixed in `01-requirements.md` §5.1 / the LLR executed-verification lines; `pytest -p no:cacheprovider`, single files, from the worktree root. Layer: 0 unit · A white-box · B black-box (`AT`) · UX. Each mutant below is named at authoring time, not execution time.

### Increment RS1a — the data layer (`reviews.py`, `records.py`, `config.py`, `derive.py`; additions to `tests/test_reqharness_registry.py`)

### Increment RS1b — the logic (`signing.py` new, `release.py`; new `tests/test_reqharness_signing.py` + additions to `tests/test_reqharness_registry.py`)

| Id | Layer | What it asserts | **Mutation that turns it RED** |
|---|---|---|---|
| TC-RS-2.2.1 | 0 | `entitled_to_sign` truth table: 10 `(False, reason)` arms (tampered/forked/no-registry/unknown-viewer/ambiguous-viewer/no-role/unknown-object/retired/class-undeclared/author-of-batch) + `(True, "")` for the entitled case (incl. a person holding two roles, one designated) + `(True, "")` for a blank-`Owning batch` object | **M-RS6** (role check dropped), **M-RS7** (active check dropped), **M-RS8** (chain check dropped), **M-RS19** (author check dropped) |
| TC-RS-2.1.1 | 0 | `sign_review` returns a `Path` whose file `derive` re-reads as `reviewed` (B4 output-then-consume); record `kind=="human"`, `verdict=="reviewed"`, `note==""`, `class_id` from the canon object | **M-RS5** (TOCTOU re-check removed), **M-RS14** (unknown object id coerced) |
| TC-RS-2.1.2 | 0 | every refusal raises `SigningRefused` with a stable reason code and writes nothing; a fixed `now` appears verbatim in the record `time` | **M-RS22** (bare `ValidationError` without a reason code) |
| TC-RS-2.4.1 | 0 | identical-content double sign → `SigningRefused(already_signed)`; the count limit → `SigningRefused(review_limit)` | M-RS22 |
| TC-RS-2.4.2 | 0 | no CLI/entry-point exposure: no `console_scripts`, no `--sign` flag, only `screens/review.py` imports `signing` (grep/AST) | **M-RS23** (a `console_scripts` entry / `--sign` flag added) |
| TC-RS-2.2.2 | 0 | the `moved_*` TOCTOU codes: object/digest/head/role moved between arm and confirm → one reason code each, nothing written | **M-RS5** |
| TC-RS-5.1.1 | 0 | `validate_config` refuses an `authors` entry naming an unknown person id, a duplicate person id, and a duplicate `email_sha256` (by name) | **M-RS24** (`authors` left out of `canonical_config` — `config_hash` unchanged) |
| TC-RS-5.2.1 | 0 | `derive_states` marks an author's hand-written human review `unentitled`; the object never derives `reviewed`; blank `owning_batch` → no author rule | **M-RS18** (author rule dropped from `derive`) |

### Increment RS2 — review screen + seat (`screens/review.py` new; `keymap.py`, `home.py`, `app.py`; new `tests/test_review_screen.py` + the re-pinned censuses)

| Id | Layer | What it asserts | **Mutation that turns it RED** |
|---|---|---|---|
| **AT-090** | B | `v` from home opens the screen; the frame lists every canon object id + its `derive` state word + last review; the `⁂` badge explained; the band carries the verdict | M-RS1 (states recomputed in the screen) |
| **AT-091** | B | the "needs action" preset lists exactly the open states (0 `reviewed`/`retired`, all three open states present) | M-RS2 (preset misses `pre-reviewed`) |
| **AT-092** | B | detail pane: `#N <time> <reviewer> (<kind>) head <seq>:<hash>`, digest ✓/✗, model review `(model)`, unentitled flagged apart, `⁂` line; band verdict byte-equal to one of the two verdict forms | M-RS9 (stale digest painted ✓), M-RS10 (band verdict hard-coded) |
| **AT-093** | B | `b` paints digest + head; `enter` writes exactly one file; `derive` re-reads it as `reviewed`; `b` then any other key writes nothing | M-RS4 (`b` signs directly), M-RS15 (cold `enter` signs) |
| **AT-094** | B | `b` refuses (with the reason) when the viewer lacks the role / object retired / viewer undeclared / no git identity / no registry | M-RS6, M-RS7, M-RS8 |
| **AT-095** | B | tampered/forked chain → read-only, every state `not verifiable`, band names the failing mandatory rules, `b` inert | M-RS12 (discovery synchronous), M-RS13 (generation/`is_attached` guard dropped) |
| **AT-096** | B | hostile registry (ESC / U+202E / U+200B / NEL / wide CJK / combining) paints literally, no ESC byte, no style span; no wrap at 87 | M-RS3 (one string not `plain`ed), M-RS11 (markup `Static(str)`) |
| **AT-097** | B | `v` from home opens the screen; the key bar advertises exactly the review-scope keys; the seat census pins re-baseline | M-RS16 (door dropped), M-RS17 (scope group omitted from `GROUP_SCOPE`) |
| **AT-098** | B | a cold `enter` writes 0 files and changes no painted surface | M-RS26 (`ReviewList` binds `enter`) |
| **AT-099** | B | 2 000 objects: after 1 999 `down` the selected id is in the frame; the band stays on the last rows; the painted-row count of one cursor-move repaint is constant across N (counted-operations bound) | M-RS20 (follow-the-cursor scroll removed) |
| **AT-100** | B | armed `escape`/`q` cancels and stays; not-armed `q`/`escape` leaves | M-RS21 (armed `escape`/`q` leaves) |
| **AT-101** | B | after a sign in the preset the cursor moves to the next row (or stays on the last) | **M-RS25** (cursor reset to row 0) |
| **AT-102** | B | an author-of-batch viewer pressing `b`/`enter` sees the named refusal and writes nothing | M-RS19 |
| **AT-107** | B | gated `identity._run_git` records the git calls off the main thread; `verify_chain`/`load_canon`/`derive_states`/`release.evaluate`/`sign_review` each recorded on a worker thread | M-RS12, M-RS13 |

**Layer 0 applies** to `entitled_to_sign` (the 10-arm decision → cyclomatic complexity ≥ 3) and `sign_review` (orchestration crossing the `records`/`reviews`/`derive` boundaries). **Declared once for the batch:** every increment runs its own RED proof with the sha256 restore check; the mutants above are named, and none is a hope. The exact on-disk node names are in `01-requirements.md` §5.1 (AT-100 renamed `test_at_100_escape_or_q_cancels_the_arm_and_leaves_only_when_not_armed`).

**Existing tests each increment moves (itemised — the guarded pins):** RS1 adds nodes to `tests/test_reqharness_registry.py` (no existing node references `signing`/`SigningRefused` — premise 7). RS2 moves the whole-seat and door/legend pins enumerated in `01-requirements.md` §6.3 (the `test_inc9.py` OPENERS/HELP_SCREENS/CHROME_LEXICON/ENTRY_ROWS censuses, `test_cd25b`, `test_inc9c.py` door list, `test_inc9e.py`, `test_en5.py`, `test_en8.py`, `test_legend_design.py`, `test_repair_map_truth.py` via the ARCHITECTURE row, `test_keymap.py` n03a/n03f, `test_key_dispatch.py` whole-seat count, A3/darkside censuses).

---

## 6 · Risks and rejected alternatives

**Risks**

| Risk | Likelihood / impact | Mitigation |
|---|---|---|
| A review record is immutable once written; one keystroke could be permanent | low but irreversible | the two-key confirm (`b` then `enter`) is the only guard; AT-093 drives the second key and asserts the record only then; M-RS4/M-RS15 pin both single-key failure modes |
| The 2 000-object scale makes the list repaint cost grow | high if the widget repaints all N rows per move | `ReviewList` repaints a constant, cursor-sized window (the LLR-RS.1.5 counted-operations bound, AT-099); the wall-clock stays a P4 measurement only |
| A moved object/digest/head/role between `b` and `enter` | possible | `sign_review` re-checks all four with a named `moved_*` code; one snapshot threaded through (sec m3) |
| The seat moves a dozen guarded census pins (RS2) | certain, low impact each | the pins are itemised in §6.3; each re-baseline is confirmed intentional at the increment gate, not a silent pass |
| Self-review | an author signs their own object | R6: refused at `entitled_to_sign` (author arm) and authoritatively in `derive` (never `reviewed`) |
| Impersonation / agent-driven signing | possible, self-claimed git identity | residual stated in HLR-RS.3/§6.3, not fixed; the two-key confirm guards only the TUI (sec m6/MAJOR-2) |
| The inherited confinement race (`confine_reason` → `mkdir` → `open`) | low | accepted core residual (sec m6), not fixed here |

**Rejected alternatives — only where a real decision existed** (rulings R1–R17 hold the rest)

| Alternative considered | Why it was rejected |
|---|---|
| Authorship as a **per-object author field** on the canon row (an `author` column) | Rejected by R6: the canon has no author column, and adding one to every row is a schema change across every canon fixture. Per-batch authorship answers the self-review question at the granularity the operator actually controls (who owns a batch), without a per-object schema change. |
| Authorship as a **canon column** interpreted by `derive` alone (no config map) | Rejected: a free-text column is not policy-bound; the config `authors` map is part of `config_hash`, so an authorship change needs an approved `policy` event like any config change — an enforceable, auditable declaration rather than prose. |
| Authorship via **`git blame`** on the canon file | Rejected: blame is slow, non-deterministic under rename/history rewrites, and depends on git history the ReqHarness core deliberately does not consult (the allowlist is read-only identity + root discovery). A config map is exact and offline. |
| `signing.py` folded into `reviews.py` | Rejected (R1): `sign_review` imports `derive`, which imports `reviews` — a cycle. A new leaf module keeps the dependency graph acyclic. |
| The queue (variant C) as a separate screen | Rejected (prototype verdict): C hides the audit trail; its queue becomes the "needs action" filter preset of variant A. |

---

## 7 · Forward-applicability table — **the section that makes this document honest**

| Output of this PDR | Named consumer downstream | Where the consumer will read it |
|---|---|---|
| Design characteristics: `entitled_to_sign`/`sign_review` signatures, the 10-arm table, the reason-code vocabulary, the `moved_*` TOCTOU codes | increment RS1 implementer (`software-dev`) | §3-§5 here; LLR-RS.2.1/2.2; `arq-note.md` §3 |
| Design characteristics: `ReviewScreen`/`ReviewList` shape, the one-thread worker, the arm/cancel state, the copy-string mapping | increment RS2 implementer | §3 state sketch; LLR-RS.1.4/2.3; §6.6 |
| Enablers: the 2 000-object canon fixture, the hostile-payload fixture, the shared `_seed`/`_add_ana`/`_grant_reviewer`/`_digests`/`_record_review`/`_derive` helpers | Phase 3 and validation (P4) | §5 here; `tests/test_reqharness_registry.py`; LLR-RS.1.5/1.3 |
| Proposed test cases TC-RS-* and the named mutants M-RS1…M-RS33 | layers 0/A/B of each increment; DDR item 5; validation | §5 here; each increment packet's RED counterfactual |
| Before/after renders (§9) and the judgement items | `ux-reviewer` at PDR; the validation walkthrough (P4) | §9 here |
| Security note (§10: threat → requirement/residual map) | `security-reviewer` at PDR; DDR | §10 here; `01-requirements.md` §6.3 |
| Design → requirement traceability (HLR/LLR/AT ↔ TC ↔ mutant ↔ file) | the traceability matrix and the DDR | the §5 tables, which cite the LLR id on every row |
| The ARCHITECTURE amendment (F1: `screens` row gains `review.py`) | increment RS2; `architect` at the ARQ gate | `arq-note.md` §1.2 |
| Reverse census (B1/B4) per increment | each increment packet; DDR items 3/5 | `arq-note.md` §2; `PLAN.md` §Triggers |

---

## 8 · Parallelisation plan

The batch does **not** fork: one lane, serial RS1a → RS1b → RS2 (the increments touch disjoint source files — RS1a is the data layer, RS1b the logic, RS2 the screen; RS2's screen calls RS1b's `signing` API, so RS1b must land before RS2 — A4 did not fire because the plan is serial). `01-requirements.md` §2.8 declares the fork preconditions discharged trivially. No lane table is owed.

---

## 9 · UX section (D1)

**Context of use.** *User:* one operator in a terminal; a reviewer who holds one or more roles. *Tasks:* (a) open the screen (`v` from home) and see every canon object with its derived state; (b) select an object and read who reviewed what at which head and digest; (c) sign a "needs action" object with a two-key confirm. *Environment:* terminal of variable width; the harness reference is 118 × 34 and the narrow bound is 87 × 34 (every screen AT passes at both). *Constraint:* no new chrome beyond the §6.6 copy; colours from `darkside` tokens, keys from the seat.

**Renders.** Produced by running the prototype headless — `proto.py`'s `_status_line` / `body_list_detail` / `_release_panel` over the real `darkside` tokens (the same functions that produced the prototype's `shots/*.svg`) — except where marked **hand-composed** (states the prototype does not paint: the composite "needs action" preset, the armed sign hint, the author refusal, the empty canon).

### 9.1 List + detail with history (prototype, `--state mixed`, `filt=all`, selection on `HLR-RH.2`)

118 columns (prototype run):

```text
 chain  ✓ verified  registry 10 objects  4 reviewed  2 changed · review  2 pre-reviewed  1 not reviewed  1 retired  1 unentitled review  viewer reviewer-2 (req-reviewer)

 filter  all  (10 of 10)   4 cycles: all → reviewed → changed · review → pre-reviewed → not reviewed → retired

 object                        state                                      last review
 ─────────────────────────────────────────────────────────────────────────────────────
   HLR-RH.1                    reviewed           ⁂                       ana · h4
 ▸ HLR-RH.2                    changed · review                           ana · h3
   HLR-RH.4                    reviewed                                   ana · h4
   HLR-RH.7                    pre-reviewed                               kimi-code · h4
   LLR-RH.7.1                  pre-reviewed                               qa-1 · h2
   LLR-RH.8.1                  changed · review                           reviewer-2 · h2
   US-001                      reviewed                                   ana · h4
   US-002                      not reviewed                               —
   US-010                      reviewed                                   ana · h4
   LLR-RH.9.2                  retired                                    —
╭────────────────────────────────────── object detail ──────────────────────────────────────╮
│ HLR-RH.2                                            · HLR → reviewer role req-reviewer    │
│ statement  review registry: canon, digests, baselines                                     │
│ digest now 2956c0784963   (bound head 4:3f9ac1d2)                                         │
│ review history                                                                            │
│ #1 2026-10-04  ana (human)  head 3:3f9ac1d2                                               │
│       digest 9a41f0c2d7eb ✗ stale — content changed                                       │
│  b  mark reviewed — reviewer-2 holds req-reviewer — the record binds the id, the digest… │
╰───────────────────────────────────────────────────────────────────────────────────────────╯
 ⁂ informative mark   ✓/✗ digest matches / stale   b sign — refused with the reason when you lack the role

 release readiness
 chain_verified       ✓  roles.yml verifies clean
 policy_verified      ✓  live config matches the approved policy
 signers_in_force     ✓  closing reviews signed by a role in force
 all_active_reviewed  ✗  5 objects open
 docs_current         ✓  docs generated from source, not a second copy
 verdict                 not ready · unreviewed requirements
```

87 columns — the same shapes, no wrap; the detail pane and the band truncate by cell width (prototype run); 87 renders are scroll-trimmed (the list is scrolled per window, never reflowed):

```text
 chain  ✓ verified  registry 10 objects  4 reviewed  2 changed · review  2 pre-reviewed
 1 not reviewed  1 retired  1 unentitled review  viewer reviewer-2 (req-reviewer)

 object                    state                                 last review
 ─────────────────────────────────────────────────────────────────────────────
 ▸ HLR-RH.2                changed · review                      ana…
   HLR-RH.7                pre-reviewed                          kim…
   LLR-RH.7.1              pre-reviewed                          qa-…
   US-002                  not reviewed                          —
╭──────────────────────────── object detail ────────────────────────────╮
│ HLR-RH.2                            · HLR → reviewer role req-reviewer│
│ statement  review registry: canon, dige…                              │
│ digest now 2956c0784963   (bound head 4:3f9ac1d2)                     │
│ #1 2026-10-04  ana (human)  head 3:3f9ac1d2                           │
│       digest 9a41f0c2d7eb ✗ stale — content changed                   │
╰───────────────────────────────────────────────────────────────────────╯
 release readiness
 chain_verified       ✓  roles.yml verifies clean
 all_active_reviewed  ✗  5 objects open
 verdict                 not ready · unreviewed requirements
```

### 9.2 "needs action" preset — **hand-composed** (the prototype's filter cycle has no composite preset; the preset is the requirements' WHERE-clause over the open states). The mixed fixture's five open objects:

```text
 filter  needs action  (5 of 10)   4 cycles: all → needs action → reviewed → changed · review → pre-reviewed → not reviewed → retired

 object                        state                                      last review
 ▸ HLR-RH.2                    changed · review                           ana · h3
   HLR-RH.7                    pre-reviewed                               kimi-code · h4
   LLR-RH.7.1                  pre-reviewed                               qa-1 · h2
   LLR-RH.8.1                  changed · review                           reviewer-2 · h2
   US-002                      not reviewed                               —
```

Signing in this preset moves the cursor to the next row after a successful sign (AT-101).

### 9.3 Armed sign — **hand-composed** (the prototype signs immediately on `b`; the two-key arm is the batch's addition). Hint line after `b`, selection on `HLR-RH.2`:

```text
 sign HLR-RH.2 · digest 2956c078 · head 3f9ac1d2 — enter confirms, any other key cancels
```

`enter` signs; any other key — including `escape` and `q` — cancels the arm and stays on the screen.

### 9.4 Refusal (author of the object's batch) — **hand-composed**. Hint line after `enter`, viewer `reviewer-2` who authored `HLR-RH.2`'s batch:

```text
 cannot sign: reviewer-2 authored this object's batch
```

(The other twelve refusal/empty strings are the §6.6 table, unchanged; they paint on the same hint line or detail pane, byte-exact.)

### 9.5 Tampered chain, read-only — prototype run, `--state tampered` (118 shown; 87 identical modulo cell-width truncation):

```text
 chain  config changed without approval  registry not verifiable — every derived state is suspended  viewer ana (req-reviewer+safety-lead)

 object                             state                                               last review
   HLR-RH.1                         not verifiable                                      —
   HLR-RH.2                         not verifiable                                      —
   … (every object) …
╭────────────────────────────────────── object detail ──────────────────────────────────────╮
│ derived states are suspended — the chain does not verify                                 │
╰───────────────────────────────────────────────────────────────────────────────────────────╯

 release readiness — BLOCKED
 chain_verified       ✗  roles.yml does not verify
 policy_verified      ✗  live config matches no approved policy event
 signers_in_force     ✗  no bound head can be trusted
 all_active_reviewed  —  not evaluated
 docs_current         —  not evaluated
 verdict                 not ready · registry not verifiable
```

`b` is inert with the reason; the screen is read-only.

### 9.6 Empty canon — **hand-composed**. Detail pane when the canon has no rows:

```text
 no canon objects
```

(with no review event for a selected object, the detail pane paints `no review event names this id`.)

**Observable UX criteria** (each checkable in the validation walkthrough against the real mechanism): (1) `v` opens the screen and the frame lists every object with its `derive` state word — never a recomputed one (AT-090); (2) the "needs action" preset shows exactly the open states (AT-091); (3) `b` shows the digest + head and only `enter` writes (AT-093); (4) any other key after `b` — including `escape`/`q` — cancels and stays (AT-100); (5) the tampered screen is read-only with the reason (AT-095); (6) hostile file text paints literally with no escape or style span (AT-096).

**Judgement items for the reviewer:**

- **J1.** The armed hint shows the digest as `<sha8>` (8 hex), not the full 64-hex digest — per the operator's copy verdict. The full digest is still what the record writes. Accept the `sha8` display?
- **J2.** While armed, `q`/`escape` cancel the arm instead of leaving — a deliberate deviation from "`q` always leaves". Accept the arm-cancels rule (the operator's verdict) over the leave-consistency expectation?
- **J3.** The "needs action" preset is a filter, not a reordered list — reviewed and retired objects disappear entirely. Accept the filter semantics (variant C's queue as a WHERE-clause), or open a follow-up for a separate queue view?

### 9.7 PDR UX conditions applied (U1–U4)

- **U1** — the armed hint elides the MIDDLE of `<object>`/`<viewer>` (cell-width aware, `…`); the tails `enter confirms, any other key cancels` / `press b to re-arm` are never cut (AT-103, M-RS31).
- **U2** — the armed hint line and the armed row use the `darkside` ACCENT token; refusals use the roles-screen ALERT/WARN token (AT-104, M-RS32). No new tokens or chrome.
- **U3** — while loading the key bar advertises only `escape`; tampered/no-registry hides `b`; armed bar reads `enter sign · any other key cancel` (§6.6 `KEY-BAR-ARMED`).
- **U4** — the strings outside §6.6 come from the operator-approved prototype (listed in §6.6 "from the approved prototype"); AT-105 pins that the screen paints nothing outside §6.6 ∪ that set; the §9.1 87-col render is fixed (73-cell border, no clip) and 87 renders are scroll-trimmed.

---

## 10 · Security section (C1, C8)

The fired triggers are `session` (C1 — identity/authorization) and `markup over file-derived text` (C8). The questions and answers are in `01-requirements.md` §6.3; this section maps each threat to the requirement that closes it, or the stated residual.

| Threat | Requirement that closes it | Residual (if any) |
|---|---|---|
| **Impersonation** — a registry or an actor sets `user.email` to a declared reviewer's address and signs as them | HLR-RS.3 + LLR-RS.2.2: exactly ONE declared person may match the git identity; zero/several → named refusal | git identity is self-claimed (LLR-RH.4.4); the chain proves integrity and approval, not authorship. B-122 strong mode is the named follow-up. Stated, not fixed. |
| **Agent-driven signing** — an agent in the operator's shell inherits the operator's git identity and calls `sign_review` | LLR-RS.2.4: `sign_review` has NO CLI/entry-point exposure (no `console_scripts`, no `--sign` flag, only `screens/review.py` imports `signing`), pinned by grep/AST | the path writes `kind: human` but cannot PROVE a human pressed the key; the two-key confirm guards only the TUI. Stated, not fixed. |
| **Self-review** — an author signs their own object | HLR-RS.5 + LLR-RS.5.1/5.2: the config `authors` map (part of `config_hash`), refused at `entitled_to_sign`, enforced authoritatively in `derive` (`unentitled`, never `reviewed`) | **not none (F1, corrected).** `derive` also marks `unentitled` a review whose STORED owning batch (the sign-time record field) differs from the object's current cell (reason `owning_batch_mismatch`); the rule is retroactive (live `authors` map), and a record written before this batch lacks the field → evaluated as today. The earlier "self-review residual: none" was an overclaim. |
| **Author-rule bypass by blanking the `Owning batch` cell** (F1) | LLR-RS.2.1 + LLR-RS.5.2: the record STORES the owning batch at sign time; `derive` refuses a stored/current mismatch | the cell is NOT added to the digest (it would invalidate existing reviews); legacy records without the field are evaluated as today. |
| **Author-rule bypass by MOVING the `Owning batch` cell** (M1, security re-verification) | — | **stated residual.** An author who can edit the canon can move an object's `Owning batch` cell to a batch they are not listed for BEFORE signing; including the cell in the digest does not stop it, because the author signs after the move. Mitigations: canon edits are git/PR-reviewed; `authors_declared` requires every batch to be declared; full closure needs per-object authorship (the operator chose per-batch authorship, R6). |
| **Authorship not declared fails open** (F2) | LLR-RS.5.1 + HLR-RS.5: `create_registry` seeds `authors: {}` + `authors_declared` ENABLED; the rule fails a blank/absent owning batch (unknown batch named, NFC-normalised) | signing itself stays allowed when authorship is not recorded — release then reads not-ready. |
| **Admin-author self-approves their own `authors` change** (F3) | — | stated residual (self-approved policy), carried as B-135 ("a change to `authors` needs a second admin"). |
| **One human declared twice with two emails** (F4) | — | stated residual. |
| **A second `enter` while the sign worker runs** (F5) | LLR-RS.2.3 + LLR-RS.1.4: the screen disarms on the UI thread first; at most one sign in flight; `b`/`enter` inert (AT-106, M-RS28) | none. |
| **Signing against an unapproved config** (F6) | LLR-RS.2.1: `sign_review` refuses unless `config_digest(config) == report.policy_config_hash` (reason `unapproved_config`, M-RS29) | none. |
| **TOCTOU** — object/digest/head/role moves between `b` and `enter` | LLR-RS.2.1/2.3: `sign_review` re-checks all four with a named `moved_*` code; one snapshot threaded through the entitlement check, the confirm comparison and `record_review` | none. |
| **Broken / tampered / forked chain** | HLR-RS.3 + LLR-RS.2.1: `sign_review` refuses when `report.ok` is False, naming the status; the screen is read-only with `b` inert | fork recovery is core-only (B-126); the screen never recovers, it only refuses. |
| **Retired object** | LLR-RS.2.2: the `retired` arm; an active check precedes the role check | none. |
| **Terminal escapes / markup injection** (C8) | LLR-RS.1.3: every file-derived string passes `darkside.plain` into `rich.text.Text` sinks; AT-096 plants ESC/U+202E/U+200B/NEL/wide-CJK/combining + `[bold]x[/]`/`[/]` payloads and asserts they paint literally | none — no render mode on this screen interprets markup (the roles-screen R10 precedent). |
| **Concurrent signers** | LLR-RS.2.4: different content → two content-named files, duplicate `seq` harmless; identical content → `SigningRefused(already_signed)` | none beyond the inherited confinement race. |
| **Confinement race** (`confine_reason` → `mkdir` → `open`) | — | accepted core residual (sec m6); inherited from `reviews.record_review`, not introduced or fixed here. |

**Review route.** `01-requirements.md` §6.3 names `security-reviewer` for C1/C8; the batch fired C1/C8, so this proposal records the security lens here (§10) and the PDR names `security-reviewer` a participant.

---

*End of design proposal.*
