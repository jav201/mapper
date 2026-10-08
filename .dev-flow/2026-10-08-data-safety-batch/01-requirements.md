# Requirements Document — mapper — Batch 2026-10-08-data-safety-batch

> **Artifact language**
> This template is the canonical **English scaffold**. Generate the artifact in the batch's development language (`state.json` `language`). For Spanish batches, translate the **prose** — section headers and guidance — **and never a label**, and use `deberá` as the normative keyword (≡ `shall`). The normative RULES in this preamble are **language-independent** and enforced regardless of artifact language.

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/docs/req-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

> **Reserved field names.** The **field names and block keywords below are language-independent** — the
> validator parses them literally and they are never translated:
> `Validation` · `Acceptance test(s)` · `Boundary catalog` · `Negative control` · `Premise evaluation` · `Fork preconditions` · `Ledger` · `Requirement` · `⏸ DEFER`
> Everything else on this page — headings, guidance, the prose in every cell — is translated with the batch.
> **One strategy, not two:** the flow ships no alias table, so a translated label is read as an ABSENT one and the rule keyed on it reports a true-sounding silence.
> **And one FLOW-WIDE reserved token, read out of this artifact by `V42` no matter which template minted it:** `⏸ DEFER`. It is a MARKER rather than a field name, which is why it is stated here *and* in `/dev-flow` §Language of artifacts rather than in a per-template list — a deferral can be written in any batch artifact, including the ones that carry no block at all.

---

## 1. Introduction

### 1.1 Purpose
*(Informative text. Describes the document's objective.)*

### 1.2 Scope
*(What this batch covers and what it does NOT cover.)*

### 1.3 Definitions, acronyms, abbreviations
| Term | Definition |
|------|------------|
| | |

### 1.4 References
*(Related documents, standards, external tickets.)*

### 1.5 Document overview
*(How this document is structured.)*

---

## 2. Overall description

### 2.1 Product perspective
*(How the change fits into the larger system.)*

### 2.2 Product functions
*(High-level list of functional capabilities.)*

### 2.3 User characteristics
*(Roles, permissions, expected experience levels.)*

### 2.4 Constraints
*(Technological, regulatory, business.)*

### 2.5 Assumptions and dependencies
*(What we take for granted. If an assumption fails, the batch is invalidated.)*

### 2.6 Source user stories

| ID | User Story | Source | DoR status |
|----|------------|--------|------------|
| US-001 | As the operator using mapper, I want an inspector edit to require an explicit save gesture, so that one stray keystroke cannot durably overwrite a map and its sidecar without my intent. | B-36 (UX2-C-01) | READY |
| US-002 | As the maintainer, I want the shipped behaviours — a doubled `?` opens no second legend, and an unsummarisable map declares itself on its own card — guarded by their declared on-disk acceptance nodes, so a future regression cannot ship silently. | B-100 | READY |
| US-003 | As the maintainer, I want every declared acceptance id reconciled to an on-disk node or retired, so the traceability record matches what the suite actually guards. | B-101 | READY |
| US-004 | As the maintainer, I want the legend paint-race flake understood and deflaked, so the whole-branch gate is not invalidated by a poisoned instrument. | B-98 (FLAKE-2) | READY |

#### Refinement log (one block per story)

**US-001 — one keystroke durably overwrites a map and its sidecar (`B-36` / `UX2-C-01`)**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = the operator editing a ficha in the inspector · outcome = an edit is durably persisted only through an explicit save gesture, never a stray blur · why = a single keystroke on a focused field currently rewrites both `.mmd` and sidecar on blur, and has already fired on this repository's own tracked fixtures (`.dev-flow/BACKLOG.md:165`) · out of scope = the «lente» feature (US-N14), the render-budget redesign (B-33), and the inspector-adjacent B-31 / B-32 findings.
- **Feasibility (E, S):** implementation path = located. `mapper/widgets/inspector.py:351-352` `on_input_blurred` calls `_commit(event.input)`; `_commit` (`inspector.py:354-365`) posts `FieldCommitted(..., widget.value)` regardless of delta; `mapper/app.py:3344-3378` `on_ficha_inspector_field_committed` carries a delta gate at `app.py:3357-3359` that is invariant under the defect (a real keystroke changes the value); persistence via `_save_or_toast` (`app.py:229`). `select_on_focus=False` already landed (`inspector.py:55`, the B-72 half). Candidate remedies (B-36): a dirty-since-focus flag (`Input.Changed`), or dropping `on_input_blurred` and keeping the shipped `on_input_submitted` (`inspector.py:347-349`). dependencies/unknowns = the DESIGN choice of which gesture, not the mechanism. fits one batch? yes — small code surface (inspector + its screen handler).
- **Evaluability (T) — behavioral, black-box:** "When the operator focuses a ficha field, types exactly one key, then blurs without submitting, the user observes that the map and its sidecar are NOT rewritten on disk and no saved toast appears until an explicit save gesture."
- **Open questions:** which affordance (submit-only vs dirty-since-focus flag vs confirm-on-blur), and whether it applies to every field or only text fields. This is a TUI design ruling: per the standing operator rule (2026-09-04), a prototype round with real renders and the operator's verdict is required BEFORE implementation.
- **Classification:** `READY` — operator verdict 2026-10-08: **"C"** (draft + explicit save, `VERDICT-b36-prototype-2026-10-08.md`), with orchestrator rulings R1–R4 on draft lifetime, field coverage, undo granularity and modal keys. Behaviour-level criterion: when the operator presses one stray key in a focused inspector field and then moves focus or selects another node, the map's `.mmd` and `.yml` are byte-identical to before and the inspector shows the field as unsaved; when they press `ctrl+s`, both files are written once.

**US-002 — realise AT-044 and locate the N13.3 card node (`B-100`)**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = the maintainer · outcome = the shipped behaviours are guarded by on-disk nodes mapped to their declared ids · why = the behaviours hold today but are unguarded (AT-044) or guarded under a different id (N13.3), so a regression ships silently · out of scope = any product behaviour change (no code fix expected).
- **Feasibility (E, S):** implementation path = (a) N16.3 / AT-044: behaviour holds by construction — `MODAL_SCOPES = (SCOPE_PALETTE, SCOPE_HELP)` (`mapper/keymap.py:269`) makes `bindings_for("help")` (`keymap.py:294`) return only the help seat (`escape`/`q`/`up`/`down`/`pageup`/`pagedown`/`home`/`end`; `tests/test_help_scope.py:491-504`), so a second `?` binds to nothing and no second legend stacks; write the missing node in `tests/test_help_scope.py` (press `question_mark` twice, assert the screen stack does not grow). (b) N13.3: behaviour holds and is already tested under `LLR-N13.1.5` (`tests/test_repair_cycles.py:501,543,575,624,664`); the declared id `AT-025b` is not mapped to any node by id, so reconcile it to those nodes. dependencies/unknowns = none. fits one batch? yes (test-only).
- **Evaluability (T) — behavioral, black-box:** "When the operator presses the help chord twice from a map, the user observes exactly one legend and the screen stack does not grow; and when a workspace holds a map that fails to load, the user observes that map's card declares the damaged state while every other card keeps its true values."
- **Open questions:** for N13.3, is the disposition to reconcile `AT-025b` to the existing `LLR-N13.1.5` nodes (id hygiene), or to mint a dedicated `AT-025b` node?
- **Classification:** `READY` — both halves are "write/reconcile the test", not "fix", and feasibility is established.

**US-003 — reconcile the five node-less acceptance ids (`B-101`)**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✗
- **Functionality (V, N):** user = the maintainer · outcome = each declared-but-node-less AT id is resolved to an on-disk node or retired · why = the traceability record must match what the suite guards (C-18); a declared id with no node is a test the next refactor deletes without reddening anything · out of scope = changing behaviour.
- **Feasibility (E, S):** implementation path = grep each id's definition in `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md`, then grep `tests/` for a realising node. Findings: `AT-041` / `AT-042` are realised under other names (`test_at_r12_pressing_help_presents_every_map_binding` `tests/test_repair_layout.py:274`; `test_tc_r25` / `test_tc_r26` `:441` / `:456`; and the Inc-8 nodes at `tests/test_help_scope.py:139,147,327`); `AT-033` / `AT-034` / `AT-035` are NOT on disk and `tests/test_lens.py` does not exist (`ls tests/test_lens.py` → no such file). dependencies/unknowns = one factual discrepancy (below). fits one batch? yes.
- **Evaluability (T) — behavioral, black-box:** *(Definitional/inspectional — no shipped surface is involved; this is traceability work, not behaviour.)* "When the maintainer greps `tests/` for each declared AT id, each id is either resolved to a named on-disk node or retired with a ledger entry."
- **Open questions:** B-101 attributes `AT-033` / `AT-034` / `AT-035` to **US-N13**, but the canonical traceability table (`.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md:6089-6090`) assigns them to **US-N14**, which is DEFERRED (`#D23`). Their absence is therefore expected, not a defect. Which attribution is correct, and does the disposition become "retire the ids" rather than "realise them"?
- **Classification:** `READY` (orchestrator ruling at the P0 gate, 2026-10-08, under the standing autonomous authorization) — the canonical record settles the attribution: `AT-033`/`AT-034`/`AT-035` belong to `~~US-N14~~ DEFERRED` (`.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md:6090`, `#D23`), so they are RETIRED from this batch's obligation and travel with US-N14; `AT-041`/`AT-042` are reconciled to their existing nodes (`tests/test_repair_layout.py:274`, `:441`, `:456`). The B-101 row is corrected in `.dev-flow/BACKLOG.md`.

**US-004 — the legend paint-race flake (`B-98` / `FLAKE-2`)**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✗ · S ✓ · T ✓
- **Functionality (V, N):** user = the maintainer · outcome = the flaky legend own-keys test is understood and made deterministic · why = a flaky test is a poisoned instrument (P-05) that invalidates every counterfactual touching it, and the whole-branch gate is the next place it fires · out of scope = product behaviour (B-98: a paint race, not a logic failure).
- **Feasibility (E, S):** implementation path = UNESTABLISHED — the mechanism is a hypothesis, not a finding. Test at `tests/test_help_scope.py:327-390`. Hypothesis (see §2.7 P-4): `effective` is read by pressing every key in a live-derived `universe` (`test_help_scope.py:349-352`) and comparing `(pane.scroll_offset, screen_stack, screen, focused)` before/after (`:367-373`); `left` enters `universe` via the `VerticalScroll` pane's framework bindings (`mapper/screens/help.py:73-75`, `overflow-y: auto` at `help.py:51`) but is not a `SCOPE_HELP` declaration, so it can be `effective` (a horizontal-scroll reflow race) yet never `painted` (`:383-384`). fits one batch? needs a spike / reproduction first.
- **Evaluability (T) — behavioral, black-box:** "When the legend own-keys test is run N times under full-lane load, the maintainer observes a deterministic pass and a written record of which mechanism was removed."
- **Open questions:** the mechanism is unconfirmed; needs reproduction under the load condition that flaked it (full lane).
- **Classification:** `READY` after the spike (2026-10-08, `spike/FLAKE-2-spike.md`). The intake's reflow hypothesis is REFUTED. Finding: the test's own setup `pane.scroll_to(y=max//2, animate=False)` (`tests/test_help_scope.py:365`) defaults to `immediate=False` in Textual 8.2.8 (verified by `inspect.signature`), so the scroll can land inside the NEXT key's measurement window and an inert key (`left`) reads as effective. Reproduced 1/90 and 3/120 under CPU load; forced RED 2/2 by delaying only that queued scroll. Fix is test-side: `immediate=True` plus a settle assertion before sampling `before`. Same pattern at `tests/test_help_scope.py:93`, `tests/test_en7.py:246`, `tests/test_repair_layout.py:118` — in scope. Product is correct.

### 2.7 Premise evaluation (C-43) — MANDATORY, one row per premise

| # | Premise, as a truth-apt proposition | Tier | Verdict | Executed evidence (command output / `file:line` — **NOT** a citation of another document) | Disposition |
|---|---|---|---|---|---|
| P-1 | B-36's blur-commit-with-no-confirmation defect is still live on this tree | premise | ✅ TRUE | `mapper/widgets/inspector.py:351-352` `on_input_blurred` → `_commit(event.input)`; `_commit` (`:354-365`) posts `FieldCommitted` unconditionally; the handler's delta gate (`mapper/app.py:3357-3359`) only suppresses no-op edits, so a real keystroke still commits on blur | — |
| P-2 | A doubled `?` does not stack a second legend (AT-044's behaviour) holds on this tree | premise | ✅ TRUE | `mapper/keymap.py:269` `MODAL_SCOPES=(SCOPE_PALETTE, SCOPE_HELP)`; `bindings_for` excludes app scope for modal scopes (`:287`, `:294`); the `SCOPE_HELP` seat has no `question_mark` (`tests/test_help_scope.py:491-504`); grep `doubled` in `tests/` → 0 hits (no node realises AT-044 today) | — |
| P-3 | The N13.3 damaged-card behaviour holds and is already tested on this tree | premise | ✅ TRUE | `mapper/app.py:697` `damaged` set; `load_or_notice` (`:699-727`) records both raise and load-warning; the damaged card paints `DAMAGED_MAP_GLYPH` / `DAMAGED_MAP_STATE` (`app.py:887-890`; `mapper/darkside.py:665` / `:857`); nodes at `tests/test_repair_cycles.py:501,543,575,624,664` | — |
| P-4 | FLAKE-2's mechanism is the hypothesis named in US-004 (a framework key, not a seat declaration, entering `effective` under a reflow race) | hypothesis | ✅ TRUE (node present) / ❓ UNDECIDABLE (unchanged-since-flake) | node present at `tests/test_help_scope.py:327-390` and matches B-98's "work but not painted: ['left']" shape | `not established`: the authoritative `FLAKES_OPEN` record is NOT in the current top-level `.dev-flow/state.json` (no such key; only `.dev-flow/BACKLOG.md:208` cites it), so "unchanged since the flake" cannot be SHA-verified here |
| P-5 | The canonical cross-batch backlog is `.dev-flow/BACKLOG.md` (no lane file designates otherwise) | premise | ✅ TRUE | `state.json` `artifact_homes.backlog` = `repo:.dev-flow/BACKLOG.md`; the four story sources B-36 / B-100 / B-101 / B-98 all resolve to rows there | — |

- **Premise evaluation:** 5 premise(s) · 4 ✅ TRUE · 0 ❌ FALSE · 1 ❓ UNDECIDABLE (P-4's "unchanged since the flake" half). RC-1/RC-2 note: `origin` exists (`git remote -v` → `https://github.com/jav201/mapper.git`) but the fetch/rebase and `git ls-remote` limbs were NOT executed in this draft (network access is forbidden); the orchestrator should record the verified `origin/main` tip before derivation.

### 2.8 Fork preconditions (C-52) — MANDATORY, and the declared empty when the batch does not fork

| # | Condition (`C-52`) | Discharged? | The executed evidence |
|---|---|---|---|
| 1 | **Frozen contract** — no shared interface is touched inside a lane; one that must change returns to the trunk (trigger A3) | n/a | not applicable — the batch runs one lane; the A3 interface change (if the design chooses remedy (a)) is settled on the trunk, not in a lane |
| 2 | **Disjoint FILE sets**, not just modules — two lanes may not edit the same file, not even different regions | n/a | not applicable — single lane; no per-lane file sets exist to intersect |
| 3 | **Crossed reverse census** — family B run per lane and **shared before starting**; the trunk's act, impossible from inside a lane | n/a | not applicable — single lane; the B1 reverse census is run once on the trunk (§2.6 / PLAN.md Triggers) |
| 4 | **One owner of the trunk** — requirements, traceability, backlog and spec are never written from a lane | n/a | not applicable — the trunk (this batch's worktree) is the sole author; no lane writes spec/backlog |

- **Fork preconditions:** none — this batch runs one lane

---

## 3. High-level requirements (HLR)

### HLR-001 — `<Short title>`
- **Traceability:** US-001
- **Ledger:** none
- **Statement:** When `<trigger>`, the system shall `<response>`. *(Current state only. If you are about to write "because measured …", stop: the obligation belongs here, the measurement belongs in a ledger entry.)*
- **Rationale (informative):** *(why this requirement exists — `should` may technically be used here informally, but avoid it to prevent confusion.)*
- **Validation:** `test` | `demo` | `inspection` | `analysis`
- **Executed verification:** *(required if `test`/`analysis`. e.g. `npm run typecheck`, `vitest run TC-001`, `worst-case gain-staging sum analysis`.)*
- **Numeric pass threshold:** *(required if `test`/`analysis`. e.g. `0 errors`, `peak post-limiter ≤ −6 dBFS`.)*
- **Priority:** high | medium | low
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** *(what the user observes)*
  - **Shipped surface:** *(the handler / screen / CLI that produces it)*
  - **Acceptance test(s):** AT-001
  - **Boundary catalog (QC-3):** `<☐ empty ☐ boundary ☐ invalid ☐ error — tick each class that gets an AT/TC, or: none — and the reason no input class applies>`
  - **Negative control:** `<the executed input on which this verification GOES RED, or: none — and why it has no executed RED side>`

---

## 4. Low-level requirements (LLR)

> Each LLR decomposes an HLR into a verifiable property at the implementation level.
> Same regime: EARS syntax owed in `full`, recommended in `core`. ID format: `LLR-<HLR>.<M>`.

### LLR-001.1 — `<Short title>`
- **Traceability:** HLR-001
- **Ledger:** none
- **Statement:** The `<component>` shall `<verifiable technical response>`.
- **Validation:** `test (unit)` | `test (integration)` | `test (e2e)` | `inspection` | `analysis`
- **Executed verification:** *(required if `test`/`analysis`. e.g. `vitest run src/lib/audio/masterBus.test.ts -t TC-001`; `gain-sum analysis vs the compressor threshold`.)*
- **Numeric pass threshold:** *(required if `test`/`analysis`. e.g. `assert exit code 0`; `peak ≤ −6 dBFS`; `RMS error < 0.01`.)*
- **Negative control:** `<the executed input on which this verification goes RED, or: none — and why it has no executed RED side>`
- **Boundary catalog:** `<☐ empty ☐ boundary ☐ invalid ☐ error — tick each class that gets an AT/TC, or: none — and the reason no input class applies>`

### Information Flow Contract (IFC) — C-54

> Part A in every batch; Part B when the system's boundary has components a consumer can address independently. The block syntax, its fields and the rules that read them are in `templates/ifc-template.md`, which ships with the flow and is not copied into this batch.

- **Part A — flows:** `<one fenced FLOW block per information flow: SOURCE, NODES (each node with exactly one owner, an LLR above — split a node two LLRs own), SINK>`
- **Part B — boundary decomposition:** `<yes — one fenced COMPONENT block per component | no — and why no component of the boundary is addressable on its own>`

---

## 5. Validation strategy

### 5.1 Methods

> **Two layers** (per the Two-layer validation rule). Every batch declares BOTH:
> - **Layer A — white-box / functional (`TC-NNN`):** validates the HLR/LLR mechanism (the HOW). Methods: `test`, `inspection`, `analysis`.
> - **Layer B — black-box / behavioral acceptance (`AT-NNN`):** validates the user story's outcome through the shipped surface (the WHAT). Method: `acceptance`.

### 5.2 Batch acceptance criteria
- *(e.g.: 100% of LLRs covered by at least one TC with pass result.)*
- *(e.g.: 0 blocker fails in validation.)*
- *(e.g.: test coverage >= X% where applicable.)*
- *(e.g.: no requirement without an assigned validation method.)*
- *(e.g.: every user story has ≥1 passing `AT-NNN` black-box acceptance test observing its outcome through the shipped surface — with boundary + negative evidence.)*

---

## 6. Appendices (optional)

### 6.1 Extended glossary
### 6.2 Relevant design decisions
### 6.3 Open risks

- **Security scan (`devflow-scan-spec.py`, 2026-10-08): `security_required: true`, flag `escape`.** The one match is §2.6 US-002's feasibility line, where `escape` names the Esc key of the legend seat, not input sanitisation. Recorded as C6 FIRED by the scanner (triggers only raise). The batch's security questions: (1) US-001 changes WHEN the inspector writes the map and its sidecar — the write path must stay atomic and confined (B-75 check-then-write, `MapStore._write_tmp` hard-link B-84 are adjacent, not in scope); (2) no new parser, network or secret surface. The `security-reviewer` lens runs at PDR over US-001's write path.
- **US-001 depends on an operator verdict** on a prototype round (standing rule 2026-09-04); P0 stays open for US-001 until it arrives.
### 6.4 Phase-1 reconciliation log — moved to the ledger (§7)

### 6.5 Requirement amendments — moved to the ledger (§7)

---

## 7. The ledger — authored as a SEPARATE FILE

The fence below is the ledger's seed: `devflow-init.py` writes it to `01-requirements-ledger.md`. The shape of an entry is in the field guide.

```markdown
# Requirements ledger — mapper — Batch 2026-10-08-data-safety-batch

> Append-only. Entries are added in chronological order and never rewritten. The live
> contract is `01-requirements.md`; this file records how it came to say what it says.
> Every entry names the requirement it amends; every requirement names its entries. `V26`
> compares the two sets of pairs both ways.

_No entries yet. The first amendment to the live contract writes the first one, in the
shape the field guide's §7 shows (`req-template.md` in the guide directory init prints), and nothing
above this line is ever edited._
```
