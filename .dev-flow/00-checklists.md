# Phase checklists — mapper — Batch 2026-08-18-batch-01

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language.

> **Who signs these.** `qa-reviewer` signs one checklist **per station**, not only at validation — that is
> what makes review and re-work *visible* instead of assumed. Each item carries **executed evidence**:
> a node id, command output, or a `file:line`. **An item without a citation is asserted, not satisfied.**

> **Notice convention.** `⚠` yellow = notice: does not block, obliges you to declare the reason ·
> `✗` red = block · `✓` green = satisfied with its citation.
> **A notice that repeats for three consecutive batches becomes a rule or is retired** — decided at close.

> **Home follows the station** (see §Artifact homes in `/dev-flow`): intake · requirements · increment ·
> validation → **repo**. PDR · DDR → **vault + Drive**. Close → both.

> **Re-work counter.** Every station records how many items came **back**, from which station, and why.
> That number is the only cheap signal that a gate is theatre: if the PDR approves and the DDR keeps
> rejecting, the number says so without anyone having to argue it. It feeds the batch metrics.

---

## 1 · INTAKE — repo

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Context of use per story: user · **task** · **environment** | | |
| 2 | Observable outcome stated per story | | |
| 3 | Risk estimate: importance and criticality, used to prioritise | | |
| 4 | RC-1: `origin/main` tip fetched and recorded in `PLAN.md` **before** deriving | | |
| 5 | "already shipped?" check per candidate story | | |
| 6 | `flow_hash` verified against the manifest (C-45 PULL) | | |
| 7 | **Triggers evaluated AND recorded — the ones that fired and the ones that did not, each with its probe (C-48)** | | |
| 8 | Mode declared; any change recorded in `mode_history` with its reason | | |

⚠ backlog not refreshed at the previous close · ⚠ a story with a role but no task or environment

## 2 · ARQ — repo *(only if A1/A2/A3/A4 fired)*

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Module map updated — or "no architecture change" **with its empty diff** | | |
| 2 | Every planned file falls under a declared module | | |
| 3 | Interfaces that change, listed | | |
| 4 | Lanes proposed with **disjoint FILE sets**, not just modules | | |
| 5 | `rationale` per structural decision | | |

⚠ a planned file under no declared module (the map is stale) · ✗ two lanes sharing even one file

## 3 · REQUIREMENTS — repo

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Each `R-NN` with its `AT` and the surface that produces it | | |
| 2 | **Version per item** (`R-NN v3` · `AT-NNa v2`) | | |
| 3 | Symbols cited with `file:line`, or flagged `NEW` | | |
| 4 | Premises executed (§2.7), each with its probe | | |
| 5 | `shall`/`deberá` only inside statements | | |
| 6 | Each UX scenario with its observable criterion | | |
| 7 | Cites by id the design record that originated it | | |
| 8 | Any premise resting on an **absence** flagged as load-bearing, with its synthetic instance (C-55) | | |

⚠ a requirement rising in version without its `AT`/`TC` rising or being re-confirmed

## 4 · PDR — vault + Drive

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Proposal complete (objective · modules · diagrams · interfaces · **proposed test cases** · risks · rejected alternatives) | | |
| 2 | Respects the ARQ boundaries | | |
| 3 | **Forward applicability: every output has a NAMED consumer** | | |
| 4 | Proposed test cases observable and non-vacuous — **the reddening mutation named for each** | | |
| 5 | Interfaces **frozen** for the fork | | |
| 6 | UX lens applied (family D) · security lens applied (family C) | | |
| 7 | Verdict + record **sealed** (date · verdict · participants · approved ids) | | |

⚠ any PDR output with no consumer · ✗ no increment starts without an approved PDR

## 5 · INCREMENT — repo · ×N, one per lane

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | **≤4 SOURCE files** (tests uncapped) | | |
| 2 | Tests written in this same increment | | |
| 3 | **Layer 0** where the criterion applies (cyclomatic ≥3 **or** crosses a declared boundary) | | |
| 4 | RED counterfactual captured **in my own tree** and restored **by hash** | | |
| 5 | Reverse census (family B) on every touched symbol | | |
| 6 | `code-reviewer` passed — a HIGH blocks | | |
| 7 | 7-section review packet | | |
| 8 | No file belonging to another lane touched | | |
| 9 | **Load-bearing emptiness declared** — is any claim resting on the tree holding no instance of some case? (C-55) | | |
| 10 | Mutation verdicts **per resolved arm**, inert arms named — never the process exit code | | |

⚠ **at exactly 4 source files — declare why it could not be cut smaller** · ✗ a frozen interface touched inside a lane (return to the trunk)

✗ a guard clause that is a **no-op on today's data** — untested however green the suite; discharge it with a synthetic instance of the absent case

## 6 · DDR — vault + Drive · *the join point*

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | What changed against the PDR, and **why** | | |
| 2 | Frozen interfaces intact — or returned to the trunk, declared | | |
| 3 | **Reverse census crossed between lanes** | | |
| 4 | Every `AT` = exactly one on-disk node (C-18) | | |
| 5 | Ledger **summed** across lanes | | |
| 6 | Open PDR conditions discharged **by re-reading the artifact** | | |

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
| 9 | Verdict `PASS` / `FAIL` / `PASS-WITH-NOTES` | | |

⚠ **evaluation with real users: state explicitly that it was not performed** (ISO 9241-210)

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
