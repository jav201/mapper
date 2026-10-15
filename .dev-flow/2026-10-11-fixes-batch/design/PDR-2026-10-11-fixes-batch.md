# Design review record — PDR — mapper — Batch 2026-10-11-fixes-batch

> **Artifact language.** English (`state.json` `language: en`).

> **Owed in.** `core` by trigger (PDR active in this batch's `stations_active`) · `full` ✓
> **Source:** `/dev-flow-init` step 4's seed-by-level table, which is this fact's one home. `stations_active` in `state.json` is the authority for *this* batch.

> **Where this lives: the VAULT + Drive** once sealed (published by `/dev-flow-sync`); staged here under `design/` until then. It is **sealed** and **cited by id** from the repo. If this record changes after the seal it is a NEW version with a NEW id (`PDR-2026-10-11-fixes-batch-v2`), never a silent edit.

> **Notice convention.** `⚠` yellow = notice, declare the reason and continue · `✗` red = block · `✓` green = satisfied **with its evidence cited**. Without a citation an item is asserted, not satisfied.

> **Status: SEALED 2026-10-15** — `approved with conditions`. Reviewed by `architect` (Claude Opus), `qa-reviewer` with a light security lens (DeepSeek) and `ux-reviewer` (Claude Sonnet). The conditions are applied in the requirements and design now; implementation-side conditions are verified at the increment gates (section C).

| Field | Value |
|---|---|
| Record id | `PDR-2026-10-11-fixes-batch` |
| Reviews | `PDR-2026-10-11-fixes-batch` proposal: `design/design-proposal.md` (with `design/arq-note.md`) |
| Participants | PDR: `architect` (Claude Opus) + `qa-reviewer` with the light security lens (DeepSeek) + `ux-reviewer` (Claude Sonnet) (D1 fired) |
| Date sealed | `2026-10-15` |
| **Verdict** | `approved with conditions` |

---

## A · PDR checklist — preliminary design review

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Proposal complete: objective · modules and boundaries · diagrams · interfaces that change · **proposed test cases** · risks · rejected alternatives **where a real decision exists**, otherwise `n/a — <the decision already made, and by what>` (a row that can only be satisfied by inventing a second design is a row satisfied by invention) | ✓ | Objective §1 (`design/design-proposal.md:19`), modules §2 (`:25`), diagrams §3 (`:36`), interfaces §4 (`:64`), test cases §5 (`:75`), risks and rejected alternatives §6 (`:126`). Real decisions have rows (slugify `""`, hoist, cache location, catch set); the rest is `n/a — decided by R1-R6`. |
| 2 | Respects the boundaries of `docs/ARCHITECTURE.md` | ✓ | `design/arq-note.md:13-35` (§1: map script run, `unclaimed: ['mapper/screens/roles.py']`, 0 new edges, `test_repair_map_truth.py` 42 passed). Boundary respected; the stale map (F1) is amended at increment 003 together with `docs/ARCHITECTURE.md:113` (C3). |
| 3 | **Forward applicability:** every output has a NAMED downstream consumer | ✓ | Forward-applicability table, `design/design-proposal.md:152-165` (§7): every output names its consumer (increment implementers, `architect`, `qa-reviewer`, `ux-reviewer`, DDR, P4). The map-amendment row now names increment 003 itself. |
| 4 | Every requirement has foreseen coverage | ✓ | `design/design-proposal.md:75-124` (§5) cites the LLR/AT id on every row; `01-requirements.md:419-447` (§5.1/5.2) maps US-FX-001..006 to AT-084..AT-089. LLR-FX.1.1..FX.6.1 each carry an executed-verification line. TC-FX-3.3 and TC-FX-S1 accepted as test-only additions. |
| 5 | Proposed test cases are observable **and non-vacuous** — the reddening mutation is named for each | ✓ | Each TC row in `design/design-proposal.md:79-124` names its reddening mutant (M-FX1..M-FX17); the key-bar case adds M-FX17 and the `,Alpha,` / `,,` arm of TC-FX-1.3 is a threshold of LLR-FX.1.3, reddened by M-FX3 (`01-requirements.md`, LLR-FX.1.3, LLR-FX.4.3). AT-084/085/087 assert painted frame text, not `update()` args (`01-requirements.md` §5.1, C-32). |
| 6 | The gauntlet controls that apply are declared, with who pays for them | ✓ | `design/design-proposal.md:123` (gauntlet: Layer 0 declared once for the batch; per-increment RED proof with the sha256 restore check, paid in the increment packets) and `PLAN.md` §Triggers (A2, A3, B1, B3, B4, C1, C6, D1, E1 fired, each with its probe). |
| 7 | Interfaces **frozen** for the fork are listed | ✓ | `design/design-proposal.md:64-73` (§4 interface table, last column) and `:167-169` (§8): `n/a` for the fork because the batch does not fork; the invariants not to touch are listed (`parse`, `_check_round_trip` comparison set, `identity.py`, the four Static ids, key scope, all goldens). |
| 8 | Lane plan: file sets disjoint, family-B census run per lane | ✓ | `design/design-proposal.md:167-169` (§8): one lane, serial 001 to 004; 001 and 002 share `mapper/mermaid.py`, so the plan is serial and no lane table is owed; `01-requirements.md:132` (§2.8) declares the fork preconditions discharged. Family-B census per increment: `design/arq-note.md` §2 end (B1/B3/B4). |
| 9 | UX lens applied (if family D fired): interaction design reviewed | ⚠ | UX lens applied by `ux-reviewer` (Claude Sonnet): `design/design-proposal.md:171-302` (§9) and the rulings table §9.4 (`:292`). Notice, not a block: the blank loading window is evidenced `executed (injected delay)` only; real-user evaluation is `not performed — one-person team`. J3 accepted as a key-bar subtraction (LLR-FX.4.3, M-FX17); J4 no extra signal; J1 and J5 to the backlog (B-129, B-128). |
| 10 | Security lens applied (if family C fired) | ✓ | Security lens applied by `qa-reviewer` with the light security pass (DeepSeek): `design/design-proposal.md:304` (§10) and `01-requirements.md:462` (§6.3). CSV hostile-cell matrix: every resulting id matches `[\w-]+`; thread boundary: the same three allow-listed git calls, `identity.py` untouched; the `row-N` collision surface is named in §6.3 (C8). BOM and quoted embedded newline are pre-existing (B-130, B-131). |

**No increment starts without an approved PDR.**

---

## B · DDR checklist — detailed design review · **and the JOIN point when the batch forked**

*Not owed at this record.* The DDR is a separate station (`DDR-2026-10-11-fixes-batch`) written before formal validation; this batch does not fork, so the join items reduce to the reverse-census and golden-drift checks `PLAN.md` §Triggers lists.

---

## C · Verdict and what it means

- `approved` — the bar is met on all three axes (Coverage · Certainty · Evidence); state which.
- `approved with conditions` — list them; each is individually dischargeable and re-read at the next gate.
- `rejected` — **returns to DESIGN, not to implementation.** Name the gap that caused it.

**Verdict: `approved with conditions`** — Coverage, Certainty and Evidence all met on the proposal as reviewed; no blocker. The conditions below are **applied now** in the requirements, ledger and design (the document-side ones are already in the files cited); the implementation-side ones are **verified at the increment gates** where the code lands.

| # | Condition | Source | Where it landed | State |
|---|---|---|---|---|
| C1 | The worker RETURNS the facts; `on_worker_state_changed` (SUCCESS) applies them with the generation and `is_mounted` checks; NO `call_from_thread` (exit-time hang) | architect, R7 | LLR-FX.4.1, premise 6, §6.3 (LED .14); proposal §3 diagram, §6, §10; ARQ note §3; M-FX13 reworded | document applied; code at the increment 003 gate |
| C2 | F2 corrected: a map loaded from disk takes its root from `parse`, so the hoist does not fire on resave and bytes stay the same; it fires only for in-session roots (CSV import; `editing.py:221`); B-117 stops future drift and cannot repair maps already drifted | architect, R7 | LLR-FX.3.1 "Disk effect" line (LED .15); ARQ note §4 F2; proposal §6 risk row | applied |
| C3 | Increment 003 also amends `docs/ARCHITECTURE.md:113` (`roles.py` in the `screens` row's paths, "`roles.py` owns `RolesScreen`" in its ownership prose, `RolesScreen` in its exposes list) and the `mermaid` row note citing batch `2026-10-11-fixes-batch` | architect, R7 | ARQ note §1.2 item 3; proposal §7 | owed at the increment 003 gate (not edited here) |
| C4 | Key-bar subtraction: until the first facts arrive the key bar shows only navigation and `Esc`; with a painted-frame test and mutant | ux-reviewer, R8 | LLR-FX.4.3, TC-FX-4.3, M-FX17 (LED .16) | document applied; code at the increment 003 gate |
| C5 | AT-084/085/087 assert painted frame text, not `update()` args (C-32) | ux-reviewer, R8 | requirements §5.1 (LED .16) | document applied; code at the increment 001 and 003 gates |
| C6 | Walkthrough honesty: the blank window is `executed (injected delay)` only; real-user evaluation `not performed — one-person team`; no extra status-line signal in this batch | ux-reviewer, R8 | proposal §9.4 (LED .16) | applied |
| C7 | Threshold arm on LLR-FX.1.3 / TC-FX-1.3: `,Alpha,` then `,,` gives ids `{alpha, row-1}` | qa-reviewer, R9 | LLR-FX.1.3, TC-FX-1.3 (LED .17) | document applied; code at the increment 001 gate |
| C8 | One sentence in requirements §6.3 naming the `row-N` collision surface (cross-ref design §10 / §9.1(d)) | qa-reviewer, R9 | requirements §6.3 (LED .17) | applied |

Not conditions, routed: the `store` to `mermaid` map gap (ARQ F3c) is B-132; the doubled discovery start (ARQ F3b) is a DDR item; the prototype round for a visible roles loading state (J5) is B-128; the `? ` prefix on top-level import rows (J1) is B-129; CSV BOM `utf-8-sig` is B-130; CSV quoted embedded newline is B-131; an optional large-forest dump scaling test is a note in proposal §5.

---

## D · Ids this record binds *(the glue of the repo ↔ vault split)*

| This record's decision | Id | Where it lands in the **repo** |
|---|---|---|
| ARQ F1: map amendment (`roles.py`, `mermaid` notes) lands in increment 003 | `PDR-2026-10-11-fixes-batch#D1` | `docs/ARCHITECTURE.md` §2 (rows `screens`, `mermaid`) |
| Hand-back through the worker's return and `on_worker_state_changed` | `PDR-2026-10-11-fixes-batch#D2` | LLR-FX.4.1 |
| `on_unmount` cancel not added; the framework's cancel stands, the hand-back guard is owned | `PDR-2026-10-11-fixes-batch#D3` | LLR-FX.4.1, M-FX13 |
| F2 corrected (no resave reorder; no repair of already drifted maps) | `PDR-2026-10-11-fixes-batch#D4` | LLR-FX.3.1 |
| J1-J5 rulings (J3 key-bar subtraction; J4 no signal; J1, J5 backlog) | `PDR-2026-10-11-fixes-batch#D5` | LLR-FX.4.3, backlog B-128, B-129 |
| TC-FX-3.3 and TC-FX-S1 accepted as test-only additions | `PDR-2026-10-11-fixes-batch#D6` | proposal §5; increments 002, 001 |

**What decides code lands in the repo.** A decision that fixes an interface does not stay only in the vault: it is reflected in the requirement or in the module map, which are versioned beside the code.

## E · Amendments after the seal

| # | Amendment | Ledger |
|---|---|---|
| E1 | Condition C1's hand-back check reads `is_attached`, not `is_mounted`: in Textual 8.2.8 `is_mounted` stays True after a pop. Sealed text kept; this row supersedes the guard name. | LED-2026-10-11-fixes-batch.18 |
