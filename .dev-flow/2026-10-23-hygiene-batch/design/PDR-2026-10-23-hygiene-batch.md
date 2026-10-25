# Design review record — PDR — mapper — Batch 2026-10-23-hygiene-batch

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
| Record id | `PDR-2026-10-23-hygiene-batch` |
| Reviews | `design/design-proposal.md` (`PDR-2026-10-23-hygiene-batch`) · lanes L1/L2a/L2b/L3 to be joined at DDR |
| Participants | PDR: `architect — Kimi K3 subagent executing agents/architect.md · approved with conditions` · `qa-reviewer — Kimi K3 subagent executing agents/qa-reviewer.md · approve` · `security-reviewer — Kimi K3 subagent executing agents/security-reviewer.md · approve with conditions` · `ux-reviewer — Kimi K3 subagent executing agents/ux-reviewer.md · approve with conditions` (second pass + PDR review executed 2026-10-23; evidence `evidence/recheck-{architect,qa,security,ux}.md`) · DDR: `architect` + `software-dev` + `qa-reviewer` — at the DDR station |
| Date sealed | `2026-10-23` |
| **Verdict** | `approved with conditions` — sealed 2026-10-23; one condition rides open: S1 (LOW) discharged at the L2a increment gate (§B row 4); N3 and F-UX-1 discharged AT the seal by rulings R8/R7 (§B rows 2-3); second-pass minors N1/N2/n1–n4/F-UX-2 fixed in the trunk records at the seal (§B row 5) |

---

## A · PDR checklist — preliminary design review

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Proposal complete: objective · modules and boundaries · diagrams · interfaces that change · **proposed test cases** · risks · rejected alternatives **where a real decision exists**, otherwise `n/a — <the decision already made, and by what>` (a row that can only be satisfied by inventing a second design is a row satisfied by invention) | ✓ | `evidence/recheck-architect.md` Row 1 (proposal complete, real rejections only) · `evidence/recheck-qa.md` §2 (mutant coverage table per LLR — no LLR lacks an asserting test; the two n4 positive arms restated at the seal) |
| 2 | Respects the boundaries of `docs/ARCHITECTURE.md` | ✓ | `evidence/recheck-architect.md` Row 2 — boundaries respected (no moves; two osopen edges); its one ⚠ (N3) discharged at the seal: proposal §2 `diff` row now bars a `diff → osopen` import (ruling R8, pinned by `tests/test_arch_osopen_callers.py`) |
| 3 | **Forward applicability:** every output has a NAMED downstream consumer | ✓ | `evidence/recheck-qa.md` Row 3 — §7 forward applicability: five output rows, every one with a named consumer and reading location |
| 4 | Every requirement has foreseen coverage | ✓ | `evidence/recheck-architect.md` Row 4 — header id list matches the contract exactly (3 US / 6 HLR / 11 LLR independently counted); §1 maps every chain to its lane; §5 carries every AT-108…116 into a proposed case |
| 5 | Proposed test cases are observable **and non-vacuous** — the reddening mutation is named for each | ✓ | `evidence/recheck-qa.md` Row 5 — every §5 row names its reddening mutation or the move-aside counterfactual; the two missing positive boundary arms (n4) restated in proposal §5 at the seal |
| 6 | The gauntlet controls that apply are declared, with who pays for them | ✓ | `evidence/recheck-qa.md` Row 6 — C11 RED counterfactuals declared at authoring time with packet owners; B-44 same-landing discipline declared twice; byte-pinned must-stay-green list |
| 7 | Interfaces **frozen** for the fork are listed | ✓ | `evidence/recheck-architect.md` Row 7 — D1 construction-site census re-run (exactly 3 hits), B-44 pin read, D2 osopen surface read (reader name NEW, frozen at this seal) |
| 8 | Lane plan: file sets disjoint, family-B census run per lane | ✓ | `evidence/recheck-architect.md` Row 8 — file sets disjoint, orphan/double-ownership check clean; at the seal the sets forked to L1/L2a/L2b/L3 (ruling R7, ledger .9) and the census re-run covers `screens/home.py` (proposal §8) |
| 9 | UX lens applied (if family D fired): interaction design reviewed | ✓ | `evidence/recheck-ux.md` — D1 FIRED and the ux lens ran: UX-1…4, UX-6, UX-7 ✓; UX-5 ✗ → **F-UX-1** (major: CSV refusal reason cannot reach the operator; fixing file owned by no lane) discharged AT the seal by ruling R7 (§B row 3); **F-UX-2** (minor: toast-consumer census named the save/create surfaces for the load path) fixed in proposal §5/§8 at the seal (§B row 5) |
| 10 | Security lens applied (if family C fired) | ✓ | `evidence/recheck-security.md` TASK B — every row-10 claim verified (bounded readers stdlib-only; no new attack surface — zero-hit probe; §2 NOT-reach limbs machine-enforced; A-110 clean); m4 adoption verified (TASK A); the one new finding **S1** (LOW) is the seal's single carried condition (§B row 4) |

**No increment starts without an approved PDR.**

---

## B · DDR checklist — detailed design review · **and the JOIN point when the batch forked**

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | What changed against the PDR, **and why** | | filled at the DDR, after the lanes join |
| 2 | Frozen interfaces still intact — or the work returned to the trunk and it is declared | | filled at the DDR — D1/D2 integrity re-checked there |
| 3 | **Reverse census CROSSED between lanes** (the one check impossible from inside a lane) | | discharged at PDR — see the condition row below; re-verified at the DDR |
| 4 | Every `AT-NNN` realises in **exactly one** on-disk node (C-18) | | filled at the DDR |
| 5 | Test ledger **summed** across lanes, reconciled | | filled at the DDR |
| 6 | No lane touched another lane's file | | filled at the DDR |
| 7 | Source-file budget: any lane that reached or exceeded 4, reviewed here | | filled at the DDR — L2a owns 3, L2b owns 2 source files (L2b wording-only); every lane at (not over) budget after the ruling-R7 fork |
| 8 | **Every open PDR condition discharged one by one, by RE-READING the artifact** | | filled at the DDR |

**A conditional verdict is not an authorisation.** Each condition below is discharged by reading the
artifact that was supposed to change — not by trusting that the corrective pass ran.

| # | Condition left open at PDR | Discharged? | The artifact line that proves it |
|---|---|---|---|
| 1 | C-52 condition 3 — crossed reverse census per lane and shared, before the fork | yes — recorded in `design/design-proposal.md` §8 (executed 2026-10-23) | proposal §8 "Crossed reverse census (C-52 condition 3, ruling R5)" block: lane-owned new tests, same-landing amendments (test_a3_census.py B-44 :658-674; test_arch_osopen_callers.py ALLOWED_OUTSIDE_APP), byte-pinned must-stay-green (test_repair_depth.py :109, :252-254; test_perf_paint_clip.py:172; test_help_scope.py :78-94, :247-274); crossed matrix ∅ for write hazards; read-only presences: MapStoreError consumed by screens/construct.py:57 + screens/common.py:_save_or_toast (NOT app.py — plan corrected), outline.py:311 no_color pin out of L1's edit set; verdict "census complete, lanes may fork after the seal" — re-run at the seal over the forked sets (L1/L2a/L2b/L3): `screens/home.py` presences recorded (proposal §8 — wording-only edit, no new module edges; home-screen behavioural pins re-run at the L2b gate); the F-UX-2 load-surface correction (home.py:169-181 + map/screen.py:208-215) folded in |
| 2 | N3 (architect, minor) — proposal §2 `diff` row readable as licensing a third `diff → osopen` edge | yes — amended at the seal: the row now bars the import — capped reads reach `diff` only through `store`'s `_prescan_sidecar` over the existing `diff → store` edge (`mapper/diff.py:11`); pinned by `tests/test_arch_osopen_callers.py` (ruling R8) | proposal §2 `diff` row; `evidence/recheck-architect.md` Row 2 |
| 3 | F-UX-1 (ux, major) — the CSV refusal toast shows the exception type name only, so AT-114's reason cannot reach the operator; the fixing file (`mapper/screens/home.py`) was owned by no lane | yes — orchestrator ruling R7 (2026-10-23): `screens/home.py` joins the Q2 lane; L2 forked into L2a {store, diff, osopen} + L2b {import_csv, screens/home}, each ≤ 4 SOURCE files; typed refusal shows `str(e)` (path-free per C6), the generic branch keeps `type(e).__name__`; AT-114 observed through the running screen per m5 | contract §2.8 condition 2 + HLR-Q2.2 shipped surface; ledger `LED-2026-10-23-hygiene-batch.9` (asserting test `tests/test_ingestion_limits.py` screen arm; mutant M-Q2-5); proposal §8 L2a/L2b rows |
| 4 | S1 (security, LOW) — the diff-side `git show` capture is a full in-memory read before any cap can re-check | **open — carried to the L2a increment gate** (ruling R9): the gate decides — bound the capture (stream stdout, abort after `MAX_MAP_BYTES + 1`) or record acceptance with rationale; a one-line note in the L2a increment packet suffices; it must not pass silently | `evidence/recheck-security.md` S1; PLAN.md Risks/watch-items |
| 5 | N1, N2 (architect) · n1–n4 (qa) · F-UX-2 (ux) — second-pass record drift | yes — fixed in the trunk records at the seal (2026-10-23): N1 (contract :601 prescan figure; PLAN prescan row + probe-row superseding note) · N2 (premise 5 evidence cell re-cited to `at076_saved_wide6000_after_add_child.mmd` 222,002 B) · n1 (LLR-Q3.1.2 threshold names both empty-state texts) · n2 (proposal §5 `DEVICES` :59-62) · n3 (mutant M-Q3-4 minted — ledger .10) · n4 (proposal §5 restates the cap−1 / depth-64 positive arms) · F-UX-2 (proposal §5 + §8 name the load surfaces home.py:169-181 + map/screen.py:208-215) | the artifact lines cited in each cell; `evidence/recheck-*.md` new-findings tables |
| 6 | L2a/L2b test sequencing — `tests/test_ingestion_limits.py` (L2a-owned) carries the AT-114 screen arm, which asserts L2b's toast wording | yes — declared: the arm is required green only after BOTH L2a and L2b land (it fails mid-fork by construction); the DDR re-runs the full suite; L2b owns no test file — it is a wording-only lane | proposal §8 L2a/L2b rows + census block |

---

## C · Verdict and what it means

- **Verdict: `approved with conditions` — sealed 2026-10-23.** One condition rides open: S1 (LOW), discharged at the L2a increment gate (§B row 4). N3 and F-UX-1 were discharged AT the seal by rulings R8/R7 (§B rows 2-3); the second-pass minors N1/N2/n1–n4/F-UX-2 were fixed in the trunk records at the seal (§B row 5). The second P2 pass (F1/F2/F3, m1–m4 verified; m5/m6 carried) is merged in `02-review.md`.
- What approval means: the D1/D2 interface freeze binds (§D below) — D1 lands as trunk work first, then lanes **L1/L2a/L2b/L3** fork on the disjoint file sets of proposal §8 (L2a: 3 SOURCE files; L2b: 2); every checklist row above is reviewer-confirmed with its evidence file cited; the DDR re-reads the S1 disposition when the lanes join.

## D · Ids this record binds *(the glue of the repo ↔ vault split)*

| This record's decision | Id | Where it lands in the **repo** |
|---|---|---|
| D1 — frozen interface: `Canvas(w, h, tones=(), fallback="", audit=None)`; `put` audits `clip` (out-of-bounds non-space) and `overprint` (in-bounds, held cell a different alphanumeric AND written char alphanumeric — ruling R4); 3 construction sites pass nothing | `PDR-2026-10-23-hygiene-batch#D1` | `docs/ARCHITECTURE.md` §4 canvas rows :200/:214 + the B-44 pin amendment in `tests/test_a3_census.py:658-674` (requirement LLR-Q3.2.1, ledger .4/.8) |
| D2 — frozen interface: the osopen bounded content reader's public name + its constants (`MAX_MAP_BYTES`, `MAX_DEPTH`, `MAX_NODES`, `MAX_EDGES`, `MAX_FILE_BYTES`, `BINARY_PROBE_BYTES`); lives in `mapper/osopen.py`, imported by `store` + `import_csv` only | `PDR-2026-10-23-hygiene-batch#D2` | `docs/ARCHITECTURE.md` §3 osopen row + R-015's freeze note + the `ALLOWED_OUTSIDE_APP` amendment in `tests/test_arch_osopen_callers.py` (requirements HLR-Q2.2 / LLR-Q2.2.1, ledger .2) |

**What decides code lands in the repo.** A decision that fixes an interface does not stay only in the
vault: it is reflected in the requirement or in the module map, which are versioned beside the code.
