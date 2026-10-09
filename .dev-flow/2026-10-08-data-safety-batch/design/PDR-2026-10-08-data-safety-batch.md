# Design review record — PDR — mapper — Batch 2026-10-08-data-safety-batch

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
| Record id | `PDR-2026-10-08-data-safety-batch` |
| Reviews | `design/design-proposal.md` at `297bb79` (single lane) |
| Participants | `architect` + `qa-reviewer` (tester lens) + `ux-reviewer` (family D) — independent, read-only, 2026-10-08 |
| Date sealed | `2026-10-08` |
| **Verdict** | `approved with conditions` (C1–C14 below; each names when it must be discharged) |

---

## A · PDR checklist — preliminary design review

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Proposal complete: objective · modules and boundaries · diagrams · interfaces that change · **proposed test cases** · risks · rejected alternatives **where a real decision exists**, otherwise `n/a — <the decision already made, and by what>` (a row that can only be satisfied by inventing a second design is a row satisfied by invention) | ✓ | sections 1–8 filled; §8 declared empty (one lane) |
| 2 | Respects the boundaries of `docs/ARCHITECTURE.md` | ✓ | architect: no new import edge (`docs/ARCHITECTURE.md:118-135`); R-012..R-014 kept; per-increment source files 3/3/1/0/0, under the cap |
| 3 | **Forward applicability:** every output has a NAMED downstream consumer | ✓ | each output names its consumer: characteristics → Inc-1a..Inc-4; enablers E-1..E-6 → P3/P4; test cases → layers 0/A/B and the DDR; traceability → matrix |
| 4 | Every requirement has foreseen coverage | ✓ | architect: HLR-001..009 map to rows 1a.1–4.3; all 27 LLRs have a planned node or an inspection |
| 5 | Proposed test cases are observable **and non-vacuous** — the reddening mutation is named for each | ⚠ | qa: mutations mostly discriminating; conditions C11 (E-6 oracle too broad), C12 (US-004 one arm for four sites), C13 (AT-015 possibly vacuous) |
| 6 | The gauntlet controls that apply are declared, with who pays for them | ✓ | C-10/C-40 mutation per node, C-18 one node per AT, C-26 census — paid per increment by `software-dev` + reviewers |
| 7 | Interfaces **frozen** for the fork are listed | ✓ | I-1, I-2 freeze at seal; I-3, I-6 after Inc-1b; I-4 across Inc-1b→Inc-2; I-5 (`FieldCommitted`) removed; `MapStore` untouched |
| 8 | Lane plan: file sets disjoint, family-B census run per lane | ✓ | n/a — one lane (§8 declared empty) |
| 9 | UX lens applied (if family D fired): interaction design reviewed | ⚠ | ux-reviewer: approve-with-conditions — C6 (87-column visibility, operator ruled R8), C7 (focus after `ctrl+s`), C8 (reload-failure toast), C9 (title, R9) |
| 10 | Security lens applied (if family C fired) | ✓ | security lens ran across four P2 rounds on the same contract (02-review.md); the design adds no new surface beyond it — re-checked at the DDR |

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

## Conditions (PDR seal 2026-10-08) — each discharged by RE-READING the artifact, not by trusting the pass ran

| id | From | Condition | Discharge point |
|---|---|---|---|
| C1 | architect MAJOR-1 | `ctrl+q` (priority) while a node-change guard is open must not leave `_quit_walk_open` set forever: `_guard_draft` reports "busy" and the walk ends clearing the flag (or `ctrl+q` is refused with a toast); planned TC: `j` opens guard → `ctrl+q`, `esc`, `ctrl+q` again still guards or exits; mutation "walk does not clear the flag" | before Inc-2 starts (design row 2.3) |
| C2 | architect MINOR-2 | `_repoint(target)` defined (target exists in `self.graph`, set `nav.cursor`, `refresh_canvas`) and listed in I-4 | before Inc-1b starts |
| C3 | architect MINOR-3 | row 1b.9 names the cursor `on_mount` passes to `_establish_graph` (`None` = root) and what stays in `on_mount` (session resume `app.py:1638-1643`, error-branch notify) | before Inc-1b starts |
| C4 | architect MINOR-4 | AT-009 wording (pre-save value), US-001 summary, I-3 seat count 75 | **discharged at seal** — ledger `.63`, design §4 |
| C5 | architect MINOR-5 | R-5 records that `f` (leave focus) with a draft opens the guard | **discharged at seal** — design R-5 |
| C6 | ux M1 | hint line prefixes `● unsaved (N) · ctrl+s save` in `ALERT` while the inspector is hidden (operator R8); UX-1 renders 87/118/140 and asserts it | Inc-1b |
| C7 | ux M2 | after `ctrl+s` inside a field, focus returns to that field (`app.focused` is the same input; typing continues there) | Inc-1b |
| C8 | ux M3 | reload-failure toast states the cost: `could not reload · draft kept · leaving needs d (discard)` (` · ` separators) | Inc-1b |
| C9 | ux m1 | guard title `unsaved draft on «{title}» · {map_id}` (R9) | Inc-1a |
| C10 | qa C1 | enablers named with owners: seeded link to a second map (AT-011), seeded attachment + `A` prompt driver + focusable chip (AT-014c/d), two-screen stack helper (AT-013) | Inc-1b / Inc-2 packets |
| C11 | qa C2 | E-6 asserts a denylist of save-bearing paths, not "no message except `Left`"; primary oracle stays the `store.save` count + hash pair | Inc-1b |
| C12 | qa C3 | US-004: delayed-scroll arms for `tests/test_help_scope.py:93`, `tests/test_repair_layout.py:118`, `tests/test_en7.py:246`, or each declared a surviving mutant with its reason | Inc-3 |
| C13 | qa C4 | AT-015: executed RED with `plain()` dropped; the oracle reads the Static's source content, not rendered cells | Inc-1a |
| C14 | qa m1–m6 | arms for the four LLR boundaries (esc with live search, same-node move, same-map link, archiving the draft's own node); E-2 third mode for TC-004.2c; AT-012 observable confirmed at its RED; parametrised ids `at_014a..d`; AT-042 mutation aimed at `HelpScreen`; language/palette censuses (`tests/test_inc9.py:387-389`, `tests/test_inc9e.py:303`) run at Inc-1a; one manual `ctrl+s`/`ctrl+q` press in the operator's real Windows terminal recorded at Inc-1b | per increment packet |

Unresolved operator-owned items: none (R8 ruled by the operator 2026-10-08).

## Condition discharge log (orchestrator)

| id | Discharged | Evidence (re-read, not trusted) |
|---|---|---|
| C1 | ✅ Inc-2 U7 | `MapperApp.action_quit` ends the walk when a guard is already open; `tests/test_draft_exits.py::test_pdr_c1_quit_while_a_node_guard_is_open_does_not_wedge` (RED proven) |
| C2, C3 | ✅ before Inc-1b | design rows 1b.14a / 1b.9 (`5f1f4e1`) |
| C4, C5 | ✅ at seal | ledger `.63`, design R-5 |
| C6 | ✅ Inc-1b + Inc-1c U1 | hidden-card prefix in `ALERT`, renders 87/118/140, repaint when the card hides again |
| C7 | ✅ Inc-1b | focus returns to the edited field after `ctrl+s` (UX-1 executed) |
| C8 | ✅ Inc-1b | reload-failure toast wording (UX-1 inspected) |
| C9 | ✅ Inc-1a | guard title `unsaved draft on «{title}» · {map_id}` |
| C10 | ✅ Inc-1b / Inc-2 | enablers named in packets 003/005 |
| C11 | ✅ Inc-1b | E-6 denylist oracle |
| C12 | ✅ Inc-3 | per-site delayed-scroll arms or declared survivors (packet 001) |
| C13 | ✅ Inc-1a + Inc-1b | AT-015 executed RED with `plain()` dropped; oracle reads `Static.content` |
| C14 | ✅ (corrected at DDR) | the first log entry claimed discharge while three boundary arms were missing (caught by the DDR architect lens); now realised: `tests/test_ddr_esc_search.py`, `tests/test_ddr_same_map_link.py`, `tests/test_ddr_archive_own.py` (ledger .68); E-2 third mode and AT-012 observable in Inc-1b/Inc-2 packets; **operator real-terminal smoke 2026-10-09** (`human:Javier`): `ctrl+s` saved without freezing the terminal and `ctrl+q` raised the guard — verbatim "Todod funcionó, continuemos." |
