# Phase checklists — mapper — Batch 2026-10-09-canon-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language.

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/docs/phase-checklists.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

> **Notice convention.** `⚠` yellow = notice: does not block, obliges you to declare the reason ·
> `✗` red = block · `✓` green = satisfied with its citation.
> **A notice that repeats for three consecutive batches becomes a rule or is retired** — decided at close.

> **Re-work counter.** Every station records how many items came **back**, from which station, and why.
> That number is the only cheap signal that a gate is theatre: if the PDR approves and the DDR keeps
> rejecting, the number says so without anyone having to argue it. It feeds the batch metrics.

---

## 1 · INTAKE — repo

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Context of use per story: user · **task** · **environment** | ✓ | US-001/US-002 maintainer · task: read the canon / keep lint clean · env: the repo (`01-requirements.md` §2.6) |
| 2 | Observable outcome stated per story | ✓ | AT-063 (canon rows on disk), AT-064 (no unused import) — §3 |
| 3 | Risk estimate: importance and criticality, used to prioritise | ✓ | low/medium; PLAN.md §Risks |
| 4 | RC-1: `origin/main` tip fetched and recorded in `PLAN.md` **before** deriving — with no `origin` remote, the local tip and the no-origin premise | ✓ | `origin/master` = `558b41522c7d` fetched before deriving (PLAN.md Header) |
| 5 | RC-2: `origin` reachable and the age of its newest commit recorded in `PLAN.md` **before** deriving (`git ls-remote --exit-code --heads origin`; V25; with no `origin` remote, RC-1 (a)'s premise line) | ✓ | `git fetch origin` succeeded; tip `558b415` (PR #13 merge, 2026-10-09) |
| 6 | "already shipped?" check per candidate story | ✓ | neither shipped: `grep -c HYG REQUIREMENTS.md` → 0; `ruff check mapper/app.py` → F401 (§2.7) |
| 7 | `flow_hash` verified against the manifest (C-45 PULL) | ⚠ | `V7` external (F1 fired); `~/.claude` not touched |
| 8 | **Triggers evaluated AND recorded — the ones that fired and the ones that did not, each with its probe (C-48)** | ✓ | PLAN.md §Triggers: B4, F1 fired; 21 not fired, each with its probe; state.json written by `--fired/--not-fired` |
| 9 | Mode declared; any change recorded in `mode_history` with its reason | ✓ | `mode: core` (operator); `mode_history` appended hygiene `core` |

⚠ backlog not refreshed at the previous close · ⚠ a story with a role but no task or environment

## 2 · ARQ — repo *(only if A1/A2/A3/A4 fired)*

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Module map updated — or "no architecture change" **with its empty diff** | n/a | n/a — station not active in this batch (A1–A4 not fired; PLAN.md §Triggers) |
| 2 | Every planned file falls under a declared module | n/a | n/a — station not active in this batch (A1–A4 not fired; PLAN.md §Triggers) |
| 3 | Interfaces that change, listed | n/a | n/a — station not active in this batch (A1–A4 not fired; PLAN.md §Triggers) |
| 4 | Lanes proposed with **disjoint FILE sets**, not just modules | n/a | n/a — station not active in this batch (A1–A4 not fired; PLAN.md §Triggers) |
| 5 | `rationale` per structural decision | n/a | n/a — station not active in this batch (A1–A4 not fired; PLAN.md §Triggers) |

⚠ a planned file under no declared module (the map is stale) · ✗ two lanes sharing even one file

## 3 · REQUIREMENTS — repo

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Each `R-NN` with its `AT` and the surface that produces it | ✓ | HLR-CAN.1 → AT-063 (REQUIREMENTS.md on disk); HLR-CAN.2 → AT-064 (mapper/app.py) |
| 2 | **Version per item** (`R-NN v3` · `AT-NNa v2`) | ✓ | every item v1, ledger empty |
| 3 | Symbols cited with `file:line`, or flagged `NEW` | ✓ | `mapper/app.py:7`, `REQUIREMENTS.md`, hygiene `01-requirements.md:126-202` cited; both test files NEW |
| 4 | Premises executed (§2.7), each with its probe | ✓ | §2.7: 4 premises, each executed |
| 5 | `shall`/`deberá` only inside statements | ✓ | `shall` only in Statement lines |
| 6 | Each UX scenario with its observable criterion | n/a | no UX scenario (D1 not fired) |
| 7 | Cites by id the design record that originated it | ✓ | B-104, B-105 (hygiene `05-close.md` §2) |
| 8 | Any premise resting on an **absence** flagged as load-bearing, with its synthetic instance (C-55) | ⚠ | premise 1 and 2 rest on absences (no HYG row, no duplicate id); synthetic instance = the RED runs at P3 (no rows → AT-063 RED; a duplicated row → uniqueness RED) |

⚠ a requirement rising in version without its `AT`/`TC` rising or being re-confirmed

## 4 · PDR — vault + Drive

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Proposal complete (objective · modules · diagrams · interfaces · **proposed test cases** · risks · rejected alternatives **where a real decision exists**, otherwise `n/a — <the decision already made, and by what>`) | n/a | n/a — station not active in this batch (A1–A4 not fired; PLAN.md §Triggers) |
| 2 | Respects the ARQ boundaries | n/a | n/a — station not active in this batch (A1–A4 not fired; PLAN.md §Triggers) |
| 3 | **Forward applicability: every output has a NAMED consumer** | n/a | n/a — station not active in this batch (A1–A4 not fired; PLAN.md §Triggers) |
| 4 | Proposed test cases observable and non-vacuous — **the reddening mutation named for each** | n/a | n/a — station not active in this batch (A1–A4 not fired; PLAN.md §Triggers) |
| 5 | Interfaces **frozen** for the fork | n/a | n/a — station not active in this batch (A1–A4 not fired; PLAN.md §Triggers) |
| 6 | UX lens applied (family D) · security lens applied (family C) | n/a | n/a — station not active in this batch (A1–A4 not fired; PLAN.md §Triggers) |
| 7 | Verdict + record **sealed** (date · verdict · participants · approved ids) | n/a | n/a — station not active in this batch (A1–A4 not fired; PLAN.md §Triggers) |

⚠ any PDR output with no consumer · ✗ no increment starts without an approved PDR **when this
station is active** — `ARQ` · `PDR` · `DDR` are **by trigger** in `core` and in
`full` alike (`/dev-flow` §Modes), and `stations_active` in `state.json` is the authority on which stations
exist in *this* batch. **A station absent by design is written `n/a — station not active in this
batch` and never left blank**: a blank is an omission, and a gate nobody owed must
not read like a gate nobody ran.

## 5 · INCREMENT — repo · ×N, one per lane

> **THIS STATION'S CHECKLIST HAS ONE HOME AND IT IS NOT HERE** — `C-50`
. **The increment gate is
> `templates/increment-template.md` §*Increment gate checklist*, copied into every
> packet at `.dev-flow/<batch_id>/03-increments/increment-<NNN>.md`. Sign it there**, with its
> `Owed in` column, its evidence column and its 16 rows.
>
> **What is still signed at this station, here:** the re-work counter above, and this station's entry
> in the sign-off list. The per-increment rows are signed in the packet, once.

## 6 · DDR — vault + Drive · *the join point*

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | What changed against the PDR, and **why** | n/a | n/a — station not active in this batch (A1–A4 not fired; PLAN.md §Triggers) |
| 2 | Frozen interfaces intact — or returned to the trunk, declared | n/a | n/a — station not active in this batch (A1–A4 not fired; PLAN.md §Triggers) |
| 3 | **Reverse census crossed between lanes** | n/a | n/a — station not active in this batch (A1–A4 not fired; PLAN.md §Triggers) |
| 4 | Every `AT` = exactly one on-disk node (C-18) | n/a | n/a — station not active in this batch (A1–A4 not fired; PLAN.md §Triggers) |
| 5 | Ledger **summed** across lanes | n/a | n/a — station not active in this batch (A1–A4 not fired; PLAN.md §Triggers) |
| 6 | Open PDR conditions discharged **by re-reading the artifact** | n/a | n/a — station not active in this batch (A1–A4 not fired; PLAN.md §Triggers) |

⚠ a lane that reached or exceeded the source budget · ✗ a lane that touched another lane's file

## 7 · VALIDATION — repo

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | **ONE complete run**, launched by the orchestrator — never stitched | | |
| 2 | Layer 0 unit · layer A white-box · layer B black-box | | |
| 3 | UX walkthrough with the **real mechanism** and the **painted** result | | |
| 4 | Representative + **boundary** + **negative** | | |
| 5 | The deliverable actually **observed** | | |
| 6 | Bidirectional surface-reachability matrix | | |
| 7 | **A NEGATIVE result names the over-breadth that makes it sound, and that over-breadth is guarded** (C-55 limb 1) | | |
| 8 | **Every probe that returned an absence carries its POSITIVE CONTROL** — the same probe, unmodified, returning a non-absence on a known-present case | | |
| 9 | Verdict `PASS` / `PASS-WITH-NOTES` / `FAIL` declared as the keyed `**Result:**` field, ONE token — the whole batch-verdict vocabulary, and not the increment gate's `BLOCK` | | |
| 10 | **Evaluation with users (ISO 9241-210): the STATE, keyed to what happened** — `performed` / `not performed — <reason>` / `not applicable — no trigger-D surface`, for each of automated walkthrough, expert inspection and evaluation with users, kept apart | | |
| 11 | `**Layer 0:**` and `**Evidence checklist (qa-reviewer):**` declared as keyed fields, the checklist naming WHO completed it | | |

## 8 · CLOSE — repo + vault

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | `(item, version)` baseline sealed | | |
| 2 | Backlog reconciled — the three moves | | |
| 3 | C-44 reconciliation across **every** repo touched, auxiliary ones included | | |
| 4 | Every artifact in its declared home, **no copies** | | |
| 5 | repo↔vault ids resolved in both directions | | |
| 6 | New controls pushed upstream (C-45): command · artifact · catalog · pushed | | |
| 7 | Re-work counted per station | | |
| 8 | **What was NOT done, declared** | | |

⚠ any commit that exists and never landed · ⚠ a notice now in its third consecutive batch — make it a rule or retire it
