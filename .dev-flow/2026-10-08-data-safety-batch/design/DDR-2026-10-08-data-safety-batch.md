# Design review record — DDR — mapper — Batch 2026-10-08-data-safety-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language.

> **Owed in.** `core` by trigger · `full` ✓
> **Source:** `/dev-flow-init` step 4's seed-by-mode table, which is this fact's one home. A mode marked `—` **does not owe this artifact, and its absence is not an omission**; `by trigger` means the station exists only when the `triggers` block fired, and `stations_active` in `state.json` is the authority for *this* batch. Where a SECTION or a gate row is owed more narrowly than the artifact, it says so on the row.

> **Where this lives: the VAULT + Drive.** It is **sealed** and **cited by id** from the repo.
> A record in Drive has no diff, no PR and no CI — that is a real boundary of the design, not an
> oversight. The seal is what compensates: **if this record changes after the seal it is a NEW version
> with a NEW id**, never a silent edit, and the requirement that cited the old id keeps pointing at the
> old one — which is exactly the signal you want to see.

> **Notice convention.** `⚠` yellow = notice, declare the reason and continue · `✗` red = block ·
> `✓` green = satisfied **with its evidence cited**. Without a citation an item is asserted, not satisfied.

| Field | Value |
|---|---|
| Record id | `DDR-2026-10-08-data-safety-batch` |
| Reviews | the shipped code `07dd930..0a16d90` against `design/design-proposal.md` (single lane) |
| Participants | `architect` + `qa-reviewer` (independent, read-only, 2026-10-09); `software-dev` lens covered by the per-increment `code-reviewer` gates |
| Date sealed | `2026-10-09` |
| **Verdict** | `approved with conditions` → conditions D1–D5 discharged 2026-10-09 (below) |

---

## A · PDR checklist — preliminary design review

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Proposal complete: objective · modules and boundaries · diagrams · interfaces that change · **proposed test cases** · risks · rejected alternatives **where a real decision exists**, otherwise `n/a — <the decision already made, and by what>` (a row that can only be satisfied by inventing a second design is a row satisfied by invention) | ✓ | eight deviations, each justified (architect): Inc-1 split, I-2 `map_id`, 1b.5 `call_later`, AT-044 mutation, Inc-1c, ALERT (R8), single toast, Z2 re-announce |
| 2 | Respects the boundaries of `docs/ARCHITECTURE.md` | ✓ | I-1…I-6 signatures intact; I-5 removed; `_save_or_toast(toast=)` additive |
| 3 | **Forward applicability:** every output has a NAMED downstream consumer | ✓ | n/a — one lane, no fork |
| 4 | Every requirement has foreseen coverage | ✓ | every bare AT id resolves to exactly one node; AT-025b given a joined node; AT-042 a declared multi-arm reconciliation (ledger .67) |
| 5 | Proposed test cases are observable **and non-vacuous** — the reddening mutation is named for each | ✓ | 2808 → 2915 collected before the DDR fixes, executed `--collect-only`; DDR adds +9 nodes (packet increment-006) |
| 6 | The gauntlet controls that apply are declared, with who pays for them | ✓ | n/a — one lane |
| 7 | Interfaces **frozen** for the fork are listed | ✓ | source files per increment 0/3/3/0/2 — under the cap; Inc-1b ⚠ for `app.py` size, declared |
| 8 | Lane plan: file sets disjoint, family-B census run per lane | ✓ | C1–C14 re-read by the architect lens; C14 found NOT discharged and corrected (ledger .68) |
| 9 | UX lens applied (if family D fired): interaction design reviewed | | |
| 10 | Security lens applied (if family C fired) | | |

**No increment starts without an approved PDR.**

---

## B · DDR checklist — detailed design review · **and the JOIN point when the batch forked**

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | What changed against the PDR, **and why** | | |
| 2 | Frozen interfaces still intact — or the work returned to the trunk and it is declared | | |
| 3 | **Reverse census CROSSED between lanes** (the one check impossible from inside a lane) | | |
| 4 | Every `AT-NNN` realises in **exactly one** on-disk node (C-18) | | |
| 5 | Test ledger **summed** across lanes, reconciled | | |
| 6 | No lane touched another lane's file | | |
| 7 | Source-file budget: any lane that reached or exceeded 4, reviewed here | | |
| 8 | **Every open PDR condition discharged one by one, by RE-READING the artifact** | | |

**A conditional verdict is not an authorisation.** Each condition below is discharged by reading the
artifact that was supposed to change — not by trusting that the corrective pass ran.

| # | Condition left open at PDR | Discharged? | The artifact line that proves it |
|---|---|---|---|

---

## C · Verdict and what it means

- `approved` — the bar is met on all three axes (Coverage · Certainty · Evidence); state which.
- `approved with conditions` — list them above; each is individually dischargeable and re-read at the next gate.
- `rejected` — **returns to DESIGN, not to implementation.** Name the gap that caused it.

## D · Ids this record binds *(the glue of the repo ↔ vault split)*

| This record's decision | Id | Where it lands in the **repo** |
|---|---|---|
| `<D1 — frozen interface X>` | `<PDR-…#D1>` | `<requirement R-NNN vN / docs/ARCHITECTURE.md>` |

**What decides code lands in the repo.** A decision that fixes an interface does not stay only in the
vault: it is reflected in the requirement or in the module map, which are versioned beside the code.

## DDR conditions (2026-10-09) — discharged by re-reading the artifact

| id | Condition | Discharged by |
|---|---|---|
| D1 | C14's three boundary arms (esc with a live search, same-map link, archiving the draft's own node — save/discard) | `tests/test_ddr_esc_search.py`, `tests/test_ddr_same_map_link.py`, `tests/test_ddr_archive_own.py` (Kimi units, RED each); ledger `.68`; PDR log row C14 corrected |
| D2 | records aligned with the code (C8 toast text, R8 ALERT, AT-044 `priority=True`) | `01-requirements.md` LLR-004.2 / HLR-007, design step 6 / diagram / TC-004.2b / §5.3; ledger `.66` |
| D3 | `docs/ARCHITECTURE.md` describes the shipped code | rows for `FieldCommitted` (REMOVED), draft surface and `DraftGuardScreen` (PRESENT, `map_id`), Inc-1c worksheet row, A-13…A-15 pointer |
| D4 | AT-042 / AT-025b one node each | AT-025b joined node `test_at_025b_…` (Kimi unit, RED); AT-042 declared multi-arm reconciliation; ledger `.67` |
| D5 | the operator's real-terminal smoke attributed | `human:Javier`, PDR log row C14 (verbatim quote); carried into `04-validation.md` |
| QA-3 | TC-009.1 missing; `I-remount-per-key` unproven | TC-009.1 `tests/test_help_scope.py::test_tc_009_1_settle_assertion_fails_loud_when_the_scroll_never_lands` (Kimi unit, RED: `DID NOT RAISE`); `I-remount-per-key` re-run recorded in packet increment-006 |

**External block, not this batch's:** validator `V7` reports the installed flow bundle's `SKILL.md` differs from its own manifest (modified 2026-10-09 07:24 outside this batch — the flow's rev101 work in another session). Recorded, not acted on: the flow installation is not this project's tree.
