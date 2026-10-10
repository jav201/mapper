# Design review record — PDR — mapper — Batch 2026-10-09-modular-batch

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
| Record id | `PDR-2026-10-09-modular-batch` |
| Reviews | `design/design-proposal.md` (drafted by Kimi K2, amended by the PDR document conditions, ledger LED .10) |
| Participants | PDR: `architect` (Claude Opus) + `qa-reviewer` (Claude Sonnet); `ux-reviewer` not owed (family D did not fire) · DDR: `architect` + `software-dev` + `qa-reviewer` |
| Date sealed | `2026-10-09` |
| **Verdict** | `approved with conditions` (C1–C9) |

---

## A · PDR checklist — preliminary design review

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Proposal complete: objective · modules and boundaries · diagrams · interfaces that change · **proposed test cases** · risks · rejected alternatives **where a real decision exists**, otherwise `n/a — <the decision already made, and by what>` (a row that can only be satisfied by inventing a second design is a row satisfied by invention) | ⚠ | all sections present; real alternatives in §6 (mechanisms B, C, lazy-read, the MapperApp-method option). Architect: the first import diagram missed edges → C3 |
| 2 | Respects the boundaries of `docs/ARCHITECTURE.md` | ✓ | matches `docs/ARCHITECTURE.md` §2/§3 TARGET rows; `evidence/p2r2-spine-probe.transcript` → `illegal edges: 0` |
| 3 | **Forward applicability:** every output has a NAMED downstream consumer | ✓ | §7 names a consumer for every output (architect :194–206; qa ✓ with the F4 count gap → C7) |
| 4 | Every requirement has foreseen coverage | ⚠ | architect ✓ (header lists every HLR/LLR); qa ⚠: LLR-MOD.5.2, 6.2, 7.1 have no §5 row and LLR-MOD.4.1 is a run, not a case → C6 |
| 5 | Proposed test cases are observable **and non-vacuous** — the reddening mutation is named for each | ⚠ | every row names its reddening mutation; AT-066's baseline is not pinned (C4), AT-065's mutant mechanism is unstated (C5), the AT layer labels are inconsistent (C3) |
| 6 | The gauntlet controls that apply are declared, with who pays for them | ✓ | every AT has its RED counterfactual; structural checks RED on tmp-copy mutants; each control is paid in the increment that lands it |
| 7 | Interfaces **frozen** for the fork are listed | ⚠ | F1, F2, F3, F5 accepted; F4 accepted with the `preview_csv` repoint corrected to `mapper.screens.home` (C1) |
| 8 | Lane plan: file sets disjoint, family-B census run per lane | ✓ | Inc-0 sub-lanes are disjoint single test files; the spine is serial; reverse census = F2 + the B12 diff (§8) |
| 9 | UX lens applied (if family D fired): interaction design reviewed | n/a | n/a — family D did not fire (PLAN.md §Triggers) |
| 10 | Security lens applied (if family C fired) | n/a | n/a — family C did not fire (PLAN.md §Triggers) |

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
| C1 | `preview_csv` repoint target is `mapper.screens.home` (read at `app.py:1090` inside `HomeScreen`), at A4; requirements premise 4 / LLR-MOD.3.2, proposal §4/§7, ARCHITECTURE §4 F4 | open — document fix by LED .10; executed at A4 | |
| C2 | AT-071 / LLR-MOD.7.1 rule: `screens/map/screen.py` may import the 11 concern modules; concerns may not import each other; nothing imports `mapper.app` | open — document fix by LED .10; executed at B12 | |
| C3 | proposal §3 first diagram's missing edges; AT-068…071 layer labels (Layer B for a maintainer story whose surface is the source tree) | open — document fix | |
| C4 | AT-066's baseline pinned: path, sha256 and the bound key the pilot presses | open — executed at B1 | |
| C5 | AT-065's mutant mechanism stated (subprocess with `PYTHONPATH` on a mutant copy, or equivalent) and its RED executed | open — executed at Inc-0 | |
| C6 | §5 rows/selectors for LLR-MOD.5.2, 6.2, 7.1; LLR-MOD.4.1 marked as a gate run | open — document fix by LED .10 | |
| C7 | one F4 count everywhere: 7 module-global repoint targets + 1 class-attribute patch (`GitHubConnector.fetch`) | open — document fix by LED .10 | |
| C8 | R-9's increment count corrected | open — document fix | |
| C9 | every §5 mutation executed RED and recorded in its increment packet | open — checked at DDR | |

---

## C · Verdict and what it means

- `approved` — the bar is met on all three axes (Coverage · Certainty · Evidence); state which.
- `approved with conditions` — list them above; each is individually dischargeable and re-read at the next gate.
- `rejected` — **returns to DESIGN, not to implementation.** Name the gap that caused it.

**Verdict sealed 2026-10-09: `approved with conditions` (C1–C9)** on Coverage ✓ · Certainty ✓ (after C1) · Evidence ✓. Architect and qa-reviewer both returned approved-with-conditions; the orchestrator merged their conditions (architect C1–C3; qa 1–6 → C4–C9). Self-approved under the standing authorization; no increment starts until C1–C3, C6–C8 (document fixes) are applied.

## D · Ids this record binds *(the glue of the repo ↔ vault split)*

| This record's decision | Id | Where it lands in the **repo** |
|---|---|---|
| D1 — mechanism A; `BINDINGS`/`DEFAULT_CSS`/`@on` and class constants only on the core class | `PDR-2026-10-09-modular-batch#D1` | ARCHITECTURE §2 `map screen` row; LLR-MOD.2.1, LLR-MOD.2.2 |
| D2 — F1 state roster freeze | `PDR-2026-10-09-modular-batch#D2` | ARCHITECTURE §4 F1; LLR-MOD.7.2 |
| D3 — F2 cross-concern method surface freeze | `PDR-2026-10-09-modular-batch#D3` | ARCHITECTURE §4 F2; LLR-MOD.7.2 |
| D4 — F3 core class surface | `PDR-2026-10-09-modular-batch#D4` | ARCHITECTURE §4 F3; LLR-MOD.2.1 |
| D5 — F4 repoint policy and per-name target map (after C1) | `PDR-2026-10-09-modular-batch#D5` | ARCHITECTURE §4 F4; LLR-MOD.3.2 |
| D6 — F5 app↔screen surface | `PDR-2026-10-09-modular-batch#D6` | ARCHITECTURE §4 F5; HLR-MOD.2 |
| D7 — spine order and fork after B11 | `PDR-2026-10-09-modular-batch#D7` | ARCHITECTURE §6; `01-requirements.md` §2.8 |
| D8 — sibling screens import `MapScreen` from `mapper.screens.map` (ARCH-1) | `PDR-2026-10-09-modular-batch#D8` | ARCHITECTURE §3; LLR-MOD.7.1 |

**What decides code lands in the repo.** A decision that fixes an interface does not stay only in the
vault: it is reflected in the requirement or in the module map, which are versioned beside the code.
