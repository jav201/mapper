# Design review record — PDR — mapper — Batch 2026-10-15-review-screen-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language.

> **Owed in.** `core` by trigger · `full` ✓
> **Source:** `/dev-flow-init` step 4's seed-by-level table, which is this fact's one home. A level marked `—` **does not owe this artifact, and its absence is not an omission**; `by trigger` means the station exists only when the `triggers` block fired, and `stations_active` in `state.json` is the authority for *this* batch. Where a SECTION or a gate row is owed more narrowly than the artifact, it says so on the row.

> **Where this lives: the VAULT + Drive.** It is **sealed** and **cited by id** from the repo.
> A record in Drive has no diff, no PR and no CI — that is a real boundary of the design, not an
> oversight. The seal is what compensates: **if this record changes after the seal it is a NEW version
> with a NEW id**, never a silent edit, and the requirement that cited the old id keeps pointing at the
> old one — which is exactly the signal you want to see.

> **Notice convention.** `⚠` yellow = notice, declare the reason and continue · `✗` red = block ·
> `✓` green = satisfied **with its evidence cited**. Without a citation an item is asserted, not satisfied.

| Field | Value |
|---|---|
| Record id | `PDR-2026-10-15-review-screen-batch` |
| Reviews | `design/design-proposal.md` (id `PDR-2026-10-15-review-screen-batch`) + `design/arq-note.md` |
| Participants | PDR: `architect` (Claude Opus) + `qa-reviewer` (Claude Sonnet) + `ux-reviewer` (Claude Sonnet) + `security-reviewer` (Claude Opus) · DDR: `architect` + `software-dev` + `qa-reviewer` |
| Date sealed | `2026-10-15` |
| **Verdict** | `approved with conditions` |

---

## A · PDR checklist — preliminary design review

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Proposal complete: objective · modules and boundaries · diagrams · interfaces that change · **proposed test cases** · risks · rejected alternatives **where a real decision exists**, otherwise `n/a — <the decision already made, and by what>` | ✓ | `design/design-proposal.md` §1 (objective/scope, `:19`) · §2 modules (`:27`) · §3 diagrams (`:45`) · §4 interfaces + freeze (`:97`) · §5 test cases (`:112`) · §6 risks + rejected alternatives (`:154`, "where a real decision existed", rulings R1–R17) · §7 forward-applicability (`:180`). |
| 2 | Respects the boundaries of `docs/ARCHITECTURE.md` | ✓ | `design/arq-note.md` §1 (`:12`) — 0 new edges, 0 boundary moves; §1.2 (`:24`) lists the whole map diff (items 1–5). |
| 3 | **Forward applicability:** every output has a NAMED downstream consumer | ✓ | `design/design-proposal.md` §7 (`:180`) names the consumer + where it reads for each of the 9 outputs. |
| 4 | Every requirement has foreseen coverage | ✓ | `design/design-proposal.md` §5 (`:112`) maps TC-RS-*/AT-090…107 → LLR/HLR; `01-requirements.md` §5.1 (exact node names) + §5.2 (per-story AT coverage). |
| 5 | Proposed test cases are observable **and non-vacuous** — the reddening mutation is named for each | ✓ | `design/design-proposal.md` §5 (`:112`) names a mutant per row (M-RS1…M-RS33); the PDR QA review (Q1–Q9) tightened the vacuous arms (AT-099 counter, AT-101 middle/last row, AT-092 two fixtures). |
| 6 | The gauntlet controls that apply are declared, with who pays for them | ✓ | `design/design-proposal.md` §10 (`:354`) maps each C1/C8 threat → closing requirement or residual; the PDR names `security-reviewer` + `ux-reviewer` participants; each increment's RED proof is the per-increment control. |
| 7 | Interfaces **frozen** for the fork are listed | ✓ | `design/design-proposal.md` §4 (`:97`) lists the not-touched invariants (`reviews.record_review`/`next_seq`/`load_reviews`, `chain.*`, `release.evaluate`/`safe_verify`, `identity.py`, the §6.6 strings, goldens); one lane, no fork (`01-requirements.md` §2.8). |
| 8 | Lane plan: file sets disjoint, family-B census run per lane | ✓ | One lane, serial RS1a → RS1b → RS2 (`design/design-proposal.md` §8, `:196`; `PLAN.md` Roadmap); §2.8 conditions 2–3 evidence the disjoint sets + crossed census. |
| 9 | UX lens applied (if family D fired): interaction design reviewed | ✓ | `design/design-proposal.md` §9 (`:202`) — context, before/after renders at 118/87, observable criteria, judgement items J1–J3; §9.7 (`:345`) records the PDR UX conditions U1–U4 applied (elision, ACCENT/ALERT tokens, loading key bar, prototype-copy provenance + the 87-col render fix). |
| 10 | Security lens applied (if family C fired) | ✓ | `design/design-proposal.md` §10 (`:354`) — threat map corrected at PDR: F1 owning-batch mismatch (`:360-361`), F2 seed rule, F3/F4/F5/F6 rows, impersonation/agent-signing/confinement residuals stated. `01-requirements.md` §6.3 (`:427`+). |

**No increment starts without an approved PDR.**

---

## B · DDR checklist — detailed design review · **and the JOIN point when the batch forked**

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | What changed against the PDR, **and why** | — | owed at the DDR gate (the batch did not fork). |
| 2 | Frozen interfaces still intact — or the work returned to the trunk and it is declared | — | owed at the DDR gate. |
| 3 | **Reverse census CROSSED between lanes** (the one check impossible from inside a lane) | — | one lane — no crossing owed. |
| 4 | Every `AT-NNN` realises in **exactly one** on-disk node (C-18) | — | owed at P3/DDR. |
| 5 | Test ledger **summed** across lanes, reconciled | — | one lane — owed at DDR. |
| 6 | No lane touched another lane's file | — | one lane — trivially satisfied. |
| 7 | Source-file budget: any lane that reached or exceeded 4, reviewed here | — | RS1a (4), RS1b (1), RS2 (4) — all ≤ 4 (`PLAN.md` Roadmap). |
| 8 | **Every open PDR condition discharged one by one, by RE-READING the artifact** | — | the conditions below are **design** conditions, applied now (this record); the implementation conditions are verified at the increment gates. |

**A conditional verdict is not an authorisation.** Each condition below is discharged by reading the
artifact that was supposed to change — not by trusting that the corrective pass ran.

| # | Condition left open at PDR | Discharged? | The artifact line that proves it |
|---|---|---|---|
| C-1 (U1) | Elide the MIDDLE of `<object>`/`<viewer>`; tails never cut | ✓ (design, applied now) | `01-requirements.md` LLR-RS.1.3 statement + AT-103 + M-RS31; `design/design-proposal.md` §9.7. |
| C-2 (U2) | Armed hint/row in ACCENT; refusals in the roles-screen ALERT/WARN | ✓ (design, applied now) | `01-requirements.md` LLR-RS.2.3 + AT-104 + M-RS32; §6.6 style note. |
| C-3 (U3) | Loading key bar advertises only `escape`; armed bar label | ✓ (design, applied now) | `01-requirements.md` LLR-RS.1.4/2.3 + §6.6 `KEY-BAR-ARMED`. |
| C-4 (U4) | §6.6 "from the approved prototype" list; 87-col render fixed | ✓ (design, applied now) | `01-requirements.md` §6.6 + AT-105 + M-RS30; `design/design-proposal.md` §9.1 (73-cell border). |
| C-5 (F1) | Record stores the owning batch; `derive` marks a mismatch `unentitled`; §10 corrected | ✓ (design, applied now); **re-verified by the security reviewer at the RS1a gate** | `01-requirements.md` LLR-RS.2.1/5.2 + reason `owning_batch_mismatch`; `design/design-proposal.md` §10. |
| C-6 (F2) | `create_registry` seeds `authors: {}` + `authors_declared` ENABLED; NFC-normalised | ✓ (design, applied now) | `01-requirements.md` LLR-RS.5.1 + HLR-RS.5. |
| C-7 (F3/F4) | Residuals stated + B-135 | ✓ (applied now) | `01-requirements.md` HLR-RS.5 + §6.3; `.dev-flow/BACKLOG.md` B-135. |
| C-8 (F5) | Disarm before the worker; one sign in flight | ✓ (design, applied now) | `01-requirements.md` LLR-RS.2.3/1.4 + AT-106 + M-RS28. |
| C-9 (F6) | Refuse unless `config_digest == policy_config_hash` (`unapproved_config`) | ✓ (design, applied now) | `01-requirements.md` LLR-RS.2.1 + M-RS29. |
| C-10 (A1) | RS1 split → RS1a/RS1b | ✓ (applied now) | `PLAN.md` Roadmap (RS1a/RS1b/RS2) + §2.8 condition 2. |
| C-11 (A2) | `authors` absent AND empty both omitted from `canonical_config` | ✓ (design, applied now) | `01-requirements.md` LLR-RS.5.1. |
| C-12 (A3) | Signing takes the git identity email, resolves inside `signing` | ✓ (applied now) | `01-requirements.md` LLR-RS.2.2; `design/arq-note.md` §3. |
| C-13 (A4) | Loader `ValidationError`s → `SigningRefused` via `release.safe_verify` | ✓ (design, applied now) | `01-requirements.md` LLR-RS.2.1. |
| C-14 (A5) | ARCHITECTURE §3 dependency rows + arq-note §1.2 item 2 → RS2 | ✓ (applied now) | `design/arq-note.md` §1.2 (items 1–5) + §3. |
| C-15 (A6) | `ReviewList` = `ScrollView` + `render_line`; counted ops = `render_line` calls per move | ✓ (design, applied now) | `01-requirements.md` LLR-RS.1.5 + M-RS27. |
| C-16 (A7) | Identity re-read + chain re-verify INSIDE the sign worker; generation guard; bump + re-snapshot | ✓ (design, applied now) | `01-requirements.md` LLR-RS.1.4; `design/design-proposal.md` §3. |
| C-17 (A8) | Author rule retroactive; `unentitled` three causes | ✓ (design, applied now) | `01-requirements.md` LLR-RS.5.2; `design/design-proposal.md` §3. |
| C-18 (Q1–Q9 + minors) | Pin lists, render-window asserts, reason-code literals, fixtures, mutants M-RS27/M-RS33 | ✓ (design, applied now); **implementation conditions verified at the increment gates** | `01-requirements.md` §5.1; `PLAN.md` Roadmap (RS2 pin list completed per Q2). |

---

## C · Verdict and what it means

**`approved with conditions`** — the bar is met on all three axes:

- **Coverage** — every HLR/LLR has a named test node and a named mutant (M-RS1…M-RS33); every AT realises in exactly one node (`01-requirements.md` §5.1).
- **Certainty** — each reddening mutation is named at authoring time, and the PDR QA review (Q1–Q9) closed the vacuous/under-pinned arms (AT-099 counter, AT-101 middle+last row, AT-092 two fixtures, AT-094 explicit mappings).
- **Evidence** — the proposal's renders were produced by running the prototype headless (marked hand-composed otherwise), and the map-truth/seat censuses are grep-completed (`arq-note.md` §1–§2).

The **design** conditions (U1–U4, F1–F6, A1–A8, Q1–Q9) are applied now — reflected in the contract, the ledger (LED `.16`–`.19`) and `PLAN.md` (R14–R17). Two conditions are verified later, not now: **F1** is re-verified by the security reviewer at the **RS1a gate**; the **implementation** conditions (the pin-list re-baselines, the new ATs/TCs/mutants) are verified at the **increment gates** (RS1a → RS1b → RS2).

---

## D · Ids this record binds *(the glue of the repo ↔ vault split)*

| This record's decision | Id | Where it lands in the **repo** |
|---|---|---|
| D1 — the record stores the object's owning batch at sign time | `PDR-2026-10-15-review-screen-batch#D1` | `01-requirements.md` LLR-RS.2.1 (record fields) + LLR-RS.5.2 (the mismatch arm) |
| D2 — `entitled_to_sign`/`sign_review` take the git identity email | `PDR-2026-10-15-review-screen-batch#D2` | `01-requirements.md` LLR-RS.2.2 + `design/arq-note.md` §3 |
| D3 — `create_registry` seeds `authors: {}` + `authors_declared` ENABLED | `PDR-2026-10-15-review-screen-batch#D3` | `01-requirements.md` LLR-RS.5.1 + HLR-RS.5 |
| D4 — `ReviewList` = line-based `ScrollView` + `render_line` | `PDR-2026-10-15-review-screen-batch#D4` | `01-requirements.md` LLR-RS.1.5 |
| D5 — the `authors` schema + signing API are the `reqharness` row's exposes | `PDR-2026-10-15-review-screen-batch#D5` | `docs/ARCHITECTURE.md` §3 (RS2 owns the amendment, `arq-note.md` §1.2) |

**What decides code lands in the repo.** A decision that fixes an interface does not stay only in the
vault: it is reflected in the requirement or in the module map, which are versioned beside the code.

---

## E · Amendments after the seal

| Date | Amendment | What changed |
|---|---|---|
| 2026-10-15 | Security re-verification follow-up (RS1a gate, `security-reviewer` returned REQUEST-CHANGES on F1) | F1 re-verified at the RS1a gate and found still OPEN. Four fixes landed in RS1a and one residual is stated: **H1** — with `authors` declared, a human review whose record lacks `owning_batch` derives `unentitled` (new reason `owning_batch_missing`); **M2** — the canon `Owning batch` cell is NFC-normalised in `parse_canon`; **L1** — duplicate person ids in one batch's `authors` list are refused by name; **L2** — the authors-less `config_hash` is pinned to the pre-RS1a digest as a constant; **M1 (residual, no code)** — an author who can edit the canon can move an object's `Owning batch` cell to a batch they are not listed for before signing (per-batch authorship is the operator's chosen granularity; full closure needs per-object authorship). See `design/design-proposal.md` §10 and `.dev-flow/BACKLOG.md` B-135. |
