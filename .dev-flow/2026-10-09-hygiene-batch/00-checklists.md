# Phase checklists — mapper — Batch 2026-10-09-hygiene-batch

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
| 1 | Context of use per story: user · **task** · **environment** | ✓ | US-001 maintainer · task: change the draft-save path without silent breakage · env: the repo; US-002 operator · task: trust the backlog · env: the dev-flow record (`01-requirements.md` §2.6) |
| 2 | Observable outcome stated per story | ✓ | each story has its observable outcome in its refinement block (`01-requirements.md` §2.6) and AT-060/061/062 |
| 3 | Risk estimate: importance and criticality, used to prioritise | ✓ | both LOW risk (B-103 rows are code-review LOWs; B-99 a record defect); PLAN.md §Risks |
| 4 | RC-1: `origin/main` tip fetched and recorded in `PLAN.md` **before** deriving — with no `origin` remote, the local tip and the no-origin premise | ✓ | `origin/master` = `903e0f0e46f6` fetched before deriving; PLAN.md Header |
| 5 | RC-2: `origin` reachable and the age of its newest commit recorded in `PLAN.md` **before** deriving (`git ls-remote --exit-code --heads origin`; V25; with no `origin` remote, RC-1 (a)'s premise line) | ✓ | `git ls-remote --exit-code --heads origin master` → `903e0f0…`, newest commit 2026-10-09 13:02 -0600; PLAN.md Header |
| 6 | "already shipped?" check per candidate story | ⚠ | US-002 IS already shipped in code (Inc-9h witness, 2026-10-01); the story is reframed as executed re-verification + record closure (PLAN.md Key decisions). US-001: `app.py:3565`/`:5217` still show the defects (§2.7) |
| 7 | `flow_hash` verified against the manifest (C-45 PULL) | ⚠ | `V7`: `SKILL.md` hash ≠ manifest — external, F1 fired, recorded; `~/.claude` not touched (another session owns rev101) |
| 8 | **Triggers evaluated AND recorded — the ones that fired and the ones that did not, each with its probe (C-48)** | ✓ | PLAN.md §Triggers: 1 fired (F1), 22 not fired, each with its probe; `state.json.triggers` written by `devflow-init.py --fired/--not-fired` |
| 9 | Mode declared; any change recorded in `mode_history` with its reason | ✓ | `mode: core` (operator); `mode_history` appended the outgoing `full` batch |

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
| 1 | Each `R-NN` with its `AT` and the surface that produces it | ✓ | HLR-001 → AT-060, AT-061 (map screen toast + guard modal); HLR-002 → AT-062 (home hint line) — `01-requirements.md` §3 |
| 2 | **Version per item** (`R-NN v3` · `AT-NNa v2`) | ✓ | every item is v1: first issue in this batch, no amendment yet (ledger empty) |
| 3 | Symbols cited with `file:line`, or flagged `NEW` | ✓ | `app.py:299`, `:3565`, `:5217`, `:786`, `tests/test_inc9h.py:504` cited; `guard_open()` and `tests/test_draft_hygiene.py` are NEW |
| 4 | Premises executed (§2.7), each with its probe | ✓ | §2.7: 4 premises, each with its executed grep/file:line |
| 5 | `shall`/`deberá` only inside statements | ✓ | `shall` appears only in Statement lines (`grep -n shall 01-requirements.md`) |
| 6 | Each UX scenario with its observable criterion | n/a | no UX scenario: behaviour-preserving (D1 not fired) |
| 7 | Cites by id the design record that originated it | ✓ | B-103 (data-safety DDR/code-review LOWs), B-99 (`INC9G-R8`, ui-next-02 `04-validation.md:189`) |
| 8 | Any premise resting on an **absence** flagged as load-bearing, with its synthetic instance (C-55) | ⚠ | premise 4 rests on an absence (no test reads the two attributes): load-bearing for B1 only; synthetic instance = the grep pattern matches `screen._draft_guard_open` in `mapper/app.py:5217`, so the probe can fire |

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
