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
This document states the requirements for batch `2026-10-08-data-safety-batch` of **mapper**. It turns four READY user stories (US-001…US-004) into a two-level decomposition — high-level requirements (HLR) and low-level requirements (LLR) — each with a validation method, an executed verification, a numeric pass threshold, a boundary catalog and a negative control, plus the Information Flow Contract that binds the draft's producers to its consumers.

### 1.2 Scope
In scope:
- **US-001** — the inspector's draft-and-explicit-save model (operator verdict "C" on B-36): no durable write without `ctrl+s`, a visible unsaved state, a `save · discard · stay` guard on every exit, a two-phase whole-graph write with torn-pair detection, `↵`-keeps-draft, and full field coverage including `state`.
- **US-002** — realise the AT-044 node (a doubled `?` opens no second legend) and reconcile AT-025b to the existing `LLR-N13.1.5` damaged-card nodes.
- **US-003** — reconcile AT-041/AT-042 to their on-disk nodes and retire AT-033/034/035 (they travel with the deferred US-N14).
- **US-004** — deflake the legend own-keys paint race (FLAKE-2) by making the four `scroll_to` call sites immediate and settled.

Out of scope: the «lente» feature (US-N14), the render-budget redesign (B-33), the inspector-adjacent B-31/B-32 findings, and the `R-009` `app.py` boundary move. No product behaviour change for US-002/003/004.

### 1.3 Definitions, acronyms, abbreviations
| Term | Definition |
|------|------------|
| draft | the per-node, in-memory set of unsaved inspector edits `{field: value}`, held by `FichaInspector` for the life of its `MapScreen` |
| dirty | a field whose draft value differs from the value the form showed for it (`darkside.plain(stored)`) |
| save gesture | `ctrl+s`, or the `save` answer of the save · discard · stay guard |
| guard | the `DraftGuardScreen` modal that returns one of `save`, `discard`, `stay` |
| sidecar | the `_nodos.yml` file written beside the `.mmd` map by `MapStore.save` |
| HLR / LLR | high-level / low-level requirement |
| AT / TC | black-box acceptance test (Layer B) / white-box functional test (Layer A) |
| FichaInspector | `mapper/widgets/inspector.py` — the editable inspector widget |
| MapScreen | `mapper/app.py` — the screen that owns the graph and the store |

### 1.4 References
- `VERDICT-b36-prototype-2026-10-08.md` — operator verdict "C" and rulings R1–R7 (binding for US-001).
- `02-arq-architect.md` — module map decisions R-012…R-014, increments Inc-1…Inc-4, risks A-8…A-12.
- `docs/ARCHITECTURE.md` — §4 interfaces, §5 decisions, §6 worksheet.
- `spike/FLAKE-2-spike.md` — US-004's mechanism and the four `scroll_to` sites.
- `.dev-flow/BACKLOG.md` — B-36 / B-100 / B-101 / B-98.

### 1.5 Document overview
§2 describes the product and carries the source stories, premise evaluation and fork preconditions. §3 states the HLRs; §4 decomposes them into LLRs and carries the Information Flow Contract. §5 states the validation strategy. §6 holds appendices and open risks. §7 is the ledger, authored as a separate file.

---

## 2. Overall description

### 2.1 Product perspective
mapper is a single terminal TUI for editing `.mmd` mind-maps and their `_nodos.yml` sidecar. This batch closes the stray-write class in the inspector (draft + explicit save) and hardens the help-legend tests against flakes and traceability drift; US-002/003/004 carry no product behaviour change.

### 2.2 Product functions
Draft-and-explicit-save editing of inspector fields; a visible unsaved state; a save · discard · stay guard on every exit; one whole-graph write and one undo step per save; `↵` keeps the draft; every field (including `state`) routes through the draft; legend-node reconciliation; the deflake of the own-keys test.

### 2.3 User characteristics
A single operator of the terminal mapping tool (the author/maintainer), keyboard-first. No roles, permissions, or multi-user surface.

### 2.4 Constraints
Textual 8.2.8 (its `Widget.scroll_to` defaults `immediate=False`, which drives US-004); Windows; the 4-source-file-per-increment cap; English UI.

### 2.5 Assumptions and dependencies
The operator verdict "C" (2026-10-08) is binding for US-001; the deferred US-N14 carries AT-033/034/035 out of scope; US-004's fix is test-side only (the product is correct); the keymap seat and the draft surface are the only code surfaces touched.

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
- **Feasibility (E, S):** implementation path = grep each id's definition in `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md`, then grep `tests/` for a realising node. Findings: `AT-041` / `AT-042` are realised under other names (`test_at_r12_pressing_help_presents_every_map_binding` `tests/test_repair_layout.py:274`; `test_tc_r25` / `test_tc_r26` `:441` / `:456`; and the Inc-8 node at `tests/test_help_scope.py:327`); `AT-033` / `AT-034` / `AT-035` are NOT on disk and `tests/test_lens.py` does not exist (`ls tests/test_lens.py` → no such file). dependencies/unknowns = one factual discrepancy (below). fits one batch? yes.
- **Evaluability (T) — behavioral, black-box:** *(Definitional/inspectional — no shipped surface is involved; this is traceability work, not behaviour.)* "When the maintainer greps `tests/` for each declared AT id, each id is either resolved to a named on-disk node or retired with a ledger entry."
- **Open questions:** B-101 attributes `AT-033` / `AT-034` / `AT-035` to **US-N13**, but the canonical traceability table (`.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md:6089-6090`) assigns them to **US-N14**, which is DEFERRED (`#D23`). Their absence is therefore expected, not a defect. Which attribution is correct, and does the disposition become "retire the ids" rather than "realise them"?
- **Classification:** `READY` (orchestrator ruling at the P0 gate, 2026-10-08, under the standing autonomous authorization) — the canonical record settles the attribution: `AT-033`/`AT-034`/`AT-035` belong to `US-N14 (DEFERRED)` (`.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md:6090`, `#D23`), so they are RETIRED from this batch's obligation and travel with US-N14; `AT-041` is reconciled to `tests/test_repair_layout.py:274` and `AT-042` is partially realised (`:441`, `:456`, with its smallest-set and no-scope arms owed as new nodes). The B-101 row is corrected in `.dev-flow/BACKLOG.md`.

**US-004 — the legend paint-race flake (`B-98` / `FLAKE-2`)**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = the maintainer · outcome = the flaky legend own-keys test is understood and made deterministic · why = a flaky test is a poisoned instrument (P-05) that invalidates every counterfactual touching it, and the whole-branch gate is the next place it fires · out of scope = product behaviour (B-98: a paint race, not a logic failure).
- **Feasibility (E, S):** implementation path = test-side, measured. The test's own setup `pane.scroll_to(y=pane.max_scroll_y // 2, animate=False)` (`tests/test_help_scope.py:365`) defaults to `immediate=False` in Textual 8.2.8 (P-6), so the scroll is queued and can land inside the next key's measurement window (`before`/`after` at `:367`/`:371`), making an inert key read as `effective`. Fix = `immediate=True` at all four `scroll_to` sites (`tests/test_help_scope.py:93`, `:365`; `tests/test_en7.py:246`; `tests/test_repair_layout.py:118`, P-7) plus a settle assertion before sampling. fits one batch? yes — test-only, no product change.
- **Evaluability (T) — behavioral, black-box:** "When the legend own-keys test is run N times under full-lane load, the maintainer observes a deterministic pass and a written record of which mechanism was removed."
- **Open questions:** the mechanism is unconfirmed; needs reproduction under the load condition that flaked it (full lane).
- **Classification:** `READY` after the spike (2026-10-08, `spike/FLAKE-2-spike.md`). The intake's reflow hypothesis is REFUTED. Finding: the test's own setup `pane.scroll_to(y=max//2, animate=False)` (`tests/test_help_scope.py:365`) defaults to `immediate=False` in Textual 8.2.8 (verified by `inspect.signature`), so the scroll can land inside the NEXT key's measurement window and an inert key (`left`) reads as effective. Reproduced 1/90 and 3/120 under CPU load; forced RED 2/2 by delaying only that queued scroll. Fix is test-side: `immediate=True` plus a settle assertion before sampling `before`. Same pattern at `tests/test_help_scope.py:93`, `tests/test_en7.py:246`, `tests/test_repair_layout.py:118` — in scope. Product is correct.

### 2.7 Premise evaluation (C-43) — MANDATORY, one row per premise

| # | Premise, as a truth-apt proposition | Tier | Verdict | Executed evidence (command output / `file:line` — **NOT** a citation of another document) | Disposition |
|---|---|---|---|---|---|
| P-1 | B-36's blur-commit-with-no-confirmation defect is still live on this tree | premise | ✅ TRUE | `mapper/widgets/inspector.py:351-352` `on_input_blurred` → `_commit(event.input)`; `_commit` (`:354-365`) posts `FieldCommitted` unconditionally; the handler's delta gate (`mapper/app.py:3357-3359`) only suppresses no-op edits, so a real keystroke still commits on blur | — |
| P-2 | A doubled `?` does not stack a second legend (AT-044's behaviour) holds on this tree | premise | ✅ TRUE | `mapper/keymap.py:269` `MODAL_SCOPES=(SCOPE_PALETTE, SCOPE_HELP)`; `bindings_for` excludes app scope for modal scopes (`:287`, `:294`); the `SCOPE_HELP` seat has no `question_mark` (`tests/test_help_scope.py:491-504`); grep `doubled` in `tests/` → 0 hits (no node realises AT-044 today) | — |
| P-3 | The N13.3 damaged-card behaviour holds and is already tested on this tree | premise | ✅ TRUE | `mapper/app.py:697` `damaged` set; `load_or_notice` (`:699-727`) records both raise and load-warning; the damaged card paints `DAMAGED_MAP_GLYPH` / `DAMAGED_MAP_STATE` (`app.py:887-890`; `mapper/darkside.py:665` / `:857`); nodes at `tests/test_repair_cycles.py:501,543,575,624,664` | — |
| P-4 | FLAKE-2's test still carries the race the spike measured: the setup `pane.scroll_to(y=pane.max_scroll_y // 2, animate=False)` with Textual's default `immediate=False` | measured | ✅ TRUE | `grep -n "scroll_to(y=pane.max_scroll_y // 2, animate=False)" tests/test_help_scope.py` → `365`; `inspect.signature(Widget.scroll_to)` → `immediate: bool = False` (Textual 8.2.8); the flake is recorded in `.dev-flow/2026-08-26-ui-next-batch-02/state-snapshot-at-close.json` `FLAKES_OPEN` (archived at rollover); spike `spike/FLAKE-2-spike.md`: reproduced 1/90 and 3/120 under load, the intake's reflow hypothesis REFUTED | US-004 proceeds on the measured mechanism |
| P-5 | The canonical cross-batch backlog is `.dev-flow/BACKLOG.md` (no lane file designates otherwise) | premise | ✅ TRUE | `state.json` `artifact_homes.backlog` = `repo:.dev-flow/BACKLOG.md`; the four story sources B-36 / B-100 / B-101 / B-98 all resolve to rows there | — |
| P-6 | Textual 8.2.8 `Widget.scroll_to` defaults `immediate=False`, so an `animate=False` call is queued rather than applied | premise | ✅ TRUE | `python -B -c "from textual.widget import Widget; import inspect; print(inspect.signature(Widget.scroll_to))"` → `scroll_to(self, x=None, y=None, *, animate=True, …, immediate: 'bool' = False, release_anchor=True)` | — |
| P-7 | The four `scroll_to(..., animate=False)` call sites without `immediate=True` are the complete affected set for US-004 | premise | ✅ TRUE | grep `scroll_to(` in `tests/` → `tests/test_help_scope.py:93` (in `_harvest`, `:64`), `tests/test_help_scope.py:365` (`test_hlr_n16_4_legend_declares_its_own_keys`, `:328`), `tests/test_en7.py:246` (`test_the_painted_legend_ends_with_the_rule`, `:235`), `tests/test_repair_layout.py:118` | — |
| P-8 | `MapStore.save(map_id, graph)` writes both `.mmd` and `_nodos.yml` in one call (no partial-write path) | premise | ✅ TRUE | `mapper/store.py:809` `def save(self, map_id, graph)`; `_build_sidecar` (`:469`) builds the sidecar inside `save` | — |

- **Premise evaluation:** 8 premise(s) · 8 ✅ TRUE · 0 ❌ FALSE · 0 ❓ UNDECIDABLE. RC-1/RC-2 were executed by the orchestrator at P0 and are recorded in `PLAN.md` (Premises / RC-1): `origin/master` = `07dd930` = merge-base of the batch branch; `git ls-remote --exit-code --heads origin` exit 0.

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

### HLR-001 — no durable write without an explicit save gesture
- **Traceability:** US-001
- **Ledger:** LED-2026-10-08-data-safety-batch.1, LED-2026-10-08-data-safety-batch.2, LED-2026-10-08-data-safety-batch.12, LED-2026-10-08-data-safety-batch.15, LED-2026-10-08-data-safety-batch.10, LED-2026-10-08-data-safety-batch.19, LED-2026-10-08-data-safety-batch.20, LED-2026-10-08-data-safety-batch.45, LED-2026-10-08-data-safety-batch.47
- **Statement:** When the operator edits a ficha field in the inspector, the system shall retain the edit only in a per-node draft, shall update that draft on every `Input.Changed` (each keystroke), and shall write the map and its sidecar to disk only when the operator issues the explicit save gesture (`ctrl+s`, or the `save` answer of the save · discard · stay guard).
- **Rationale (informative):** B-36 — a single keystroke on a focused field currently rewrites both files on blur; the delta gate is invariant under a real keystroke. Model C closes the stray-write class by construction.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_save.py` (provisional file; the node is minted at Phase 3 — V-5).
- **Numeric pass threshold:** exit code 0; every AT node green.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** after one stray key, a blur and a cursor change, the map's `.mmd` and `_nodos.yml` are byte-identical to before and the inspector shows the field unsaved; after `ctrl+s`, both files are written; and typing in a field then pressing `ctrl+s` without leaving the field writes the typed text.
  - **Shipped surface:** the map screen's inspector and the `ctrl+s` key.
  - **Acceptance test(s):** AT-001, AT-010
  - **Boundary catalog (QC-3):** ☑ empty — a node with no edits has no draft, so `ctrl+s` writes nothing; ☑ boundary — an edit returned to the shown value leaves the draft (no write); ☑ invalid — a value `darkside.plain` alters (a lone surrogate) is coerced before the write; ☑ error — a failing store reloads the map from disk and keeps the unwritten fields as draft (LLR-004.2).
  - **Negative control:** on today's code AT-001 goes RED: `on_input_blurred` (`inspector.py:351`) → `_commit` → `FieldCommitted` → `on_ficha_inspector_field_committed` (`app.py:3344`) writes both files on a real keystroke, so the sha256 differs. The executed RED counterfactual (C-40) is owed at Phase 3 when the node is minted.

### HLR-002 — the inspector makes the unsaved state visible
- **Traceability:** US-001
- **Ledger:** LED-2026-10-08-data-safety-batch.57
- **Statement:** While a node has a draft whose field values differ from the values the form showed, the system shall mark each changed field and shall show `● unsaved (N)` in the inspector header.
- **Rationale (informative):** without a visible unsaved state, the operator cannot tell a pending edit from a persisted one, and the guard would ask about an invisible draft.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_save.py -k unsaved` (provisional; Phase 3).
- **Numeric pass threshold:** exit code 0; the header shows `● unsaved (N)` with N equal to the changed-field count.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** after editing one field, the inspector header shows `● unsaved (1)` and the edited field carries a marker; editing a second field shows `● unsaved (2)`.
  - **Shipped surface:** the inspector header and its per-field rows.
  - **Acceptance test(s):** AT-003
  - **Boundary catalog (QC-3):** ☑ empty — a node with no edits shows no `● unsaved`; ☑ boundary — an edit returned to the shown value clears the count to `0`; ☐ invalid ☐ error.
  - **Negative control:** on today's code AT-003 goes RED: the inspector header (`inspector.py:141`) paints no unsaved count and no field carries a marker. Executed RED owed at Phase 3.

### HLR-003 — every exit asks before dropping a draft
- **Traceability:** US-001
- **Ledger:** LED-2026-10-08-data-safety-batch.4, LED-2026-10-08-data-safety-batch.8, LED-2026-10-08-data-safety-batch.26, LED-2026-10-08-data-safety-batch.31, LED-2026-10-08-data-safety-batch.36, LED-2026-10-08-data-safety-batch.41, LED-2026-10-08-data-safety-batch.45, LED-2026-10-08-data-safety-batch.47, LED-2026-10-08-data-safety-batch.48, LED-2026-10-08-data-safety-batch.49, LED-2026-10-08-data-safety-batch.53, LED-2026-10-08-data-safety-batch.55, LED-2026-10-08-data-safety-batch.57
- **Statement:** When the operator leaves the edited node or the map screen while a draft is pending — by changing node, leaving the map screen, following a link, quitting, or issuing a structural write (`a` add child, `x` archive, `A` add attachment, `X` remove attachment) — the system shall present the save · discard · stay guard before proceeding and shall proceed only on its answer. A killed terminal or crash is not an exit: the draft is lost by design and nothing is written (R1).
- **Rationale (informative):** R1 — one rule for every exit; R6 — following a link is the exit R1 did not name. ARCH-M3 — a structural write with a pending draft would otherwise apply the write after the draft's node changed, so the guard must open before the write, not after. R1 — a killed terminal writes nothing, so no guard is owed there.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_save.py -k guard` (provisional; Phase 3).
- **Numeric pass threshold:** exit code 0; every exit path presents the guard exactly once.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** after an edit, changing node, pressing `q`/`esc`, following a link, pressing `ctrl+q`, or issuing a structural write (`a`/`x`/`A`/`X`) presents the guard; `discard` (`d`) drops the draft and proceeds; `stay` (`esc`) aborts the exit; `save` (`s`) writes then proceeds.
  - **Shipped surface:** the save · discard · stay guard modal, reached from the map screen and the app.
  - **Acceptance test(s):** AT-004 (node change), AT-005a/AT-005b (leave map screen via `q`/`esc`), AT-011 (follow a link via `↵`), AT-012 (quit), AT-013 (quit with a lower map screen holding a draft — a Layer-A injection test of LLR-003.5), AT-014a–AT-014d (structural write via `a`/`x`/`A`/`X`), AT-015 (guard title with an ESC payload)
  - **Boundary catalog (QC-3):** ☑ empty — no draft ⇒ no guard, the exit proceeds; ☑ boundary — a draft pending on a lower map screen under a pushed screen is still guarded at quit; ☐ invalid ☑ error — a failing `save` reloads the map from disk per LLR-004.2, then the guard holds at `stay`.
  - **Negative control:** on today's code AT-004/AT-005/AT-011/AT-012/AT-013/AT-014 go RED: node change, `q`/`esc`, link-follow, `ctrl+q` and the structural writes proceed without presenting any guard. Executed RED owed at Phase 3.

### HLR-004 — one save gesture is one whole-graph write and one undo step
- **Traceability:** US-001
- **Ledger:** LED-2026-10-08-data-safety-batch.3, LED-2026-10-08-data-safety-batch.11, LED-2026-10-08-data-safety-batch.17, LED-2026-10-08-data-safety-batch.21, LED-2026-10-08-data-safety-batch.23, LED-2026-10-08-data-safety-batch.33, LED-2026-10-08-data-safety-batch.34, LED-2026-10-08-data-safety-batch.42, LED-2026-10-08-data-safety-batch.43, LED-2026-10-08-data-safety-batch.45, LED-2026-10-08-data-safety-batch.53, LED-2026-10-08-data-safety-batch.54, LED-2026-10-08-data-safety-batch.56
- **Statement:** When the operator issues the save gesture, the system shall write the map and its sidecar exactly once through the two-phase whole-graph `MapStore.save` (which detects a torn write), shall record exactly one undo snapshot, and shall clear each drafted field once the value on disk equals it.
- **Rationale (informative):** R3 — undo granularity matches the save gesture; risk A-10 — a failed save must not leave drafted values in the graph for a later structural write to persist.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_save.py -k save` (provisional; Phase 3).
- **Numeric pass threshold:** exit code 0; one `ctrl+s` produces exactly one write of both files and one undo step.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** `ctrl+s` rewrites both files once, and `u` restores the state before that save (all fields together); on a failing store the map is reloaded from disk and the draft keeps exactly the fields whose value did not reach disk (LLR-004.2).
  - **Shipped surface:** the `ctrl+s` key, the map's `.mmd`/`_nodos.yml` files, and the `u` undo key.
  - **Acceptance test(s):** AT-002, AT-002a, AT-009
  - **Boundary catalog (QC-3):** ☑ empty — `ctrl+s` with no draft is a no-op; ☑ boundary — a multi-field draft is one save, one undo step; ☐ invalid ☑ error — a failing store reloads the map from disk and keeps the unwritten fields as draft (LLR-004.2).
  - **Negative control:** on today's code AT-002 goes RED: `ctrl+s` is not bound (the seat has no `save_draft` row), and no draft exists to save. Executed RED owed at Phase 3.

### HLR-005 — `↵` keeps the draft and leaves the field; the hint names `ctrl+s`
- **Traceability:** US-001
- **Ledger:** LED-2026-10-08-data-safety-batch.5, LED-2026-10-08-data-safety-batch.53
- **Statement:** When the operator presses `↵` in an inspector field, the system shall leave the field and retain the draft without writing, and the inspector hint shall name `ctrl+s` as the save key.
- **Rationale (informative):** R7 — `↵` must not be a second save gesture, or the stray-write class returns through it.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_save.py -k enter` (provisional; Phase 3).
- **Numeric pass threshold:** exit code 0; `↵` produces no write and the field loses focus.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** typing then `↵` leaves the field focused elsewhere, the files are unchanged, and the hint reads `… ctrl+s save …` instead of `↵ save`.
  - **Shipped surface:** the inspector's `↵` key and the hint line.
  - **Acceptance test(s):** AT-006
  - **Boundary catalog (QC-3):** ☑ empty — `↵` in a field with no edit leaves the field and writes nothing; ☑ boundary — `↵` after editing back to the shown value leaves no draft; ☐ invalid ☐ error.
  - **Negative control:** on today's code AT-006 goes RED: `on_input_submitted` (`inspector.py:347-349`) calls `_commit`, which writes; the hint reads `↵ save` (`app.py:4043`). Executed RED owed at Phase 3.

### HLR-006 — every field, including `state`, routes through the draft
- **Traceability:** US-001
- **Ledger:** LED-2026-10-08-data-safety-batch.2, LED-2026-10-08-data-safety-batch.39, LED-2026-10-08-data-safety-batch.53
- **Statement:** While editing any inspector field, the system shall route every field value — the `state` segment included — through the draft, and shall commit no field immediately. Attachment chips are not inspector fields (their edits route through prompts, not the form), so they are excluded from the draft (ARQ D5).
- **Rationale (informative):** R2 — a model with one exception teaches the operator that some edits are instant, which brings the stray-write back.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_save.py -k state` (provisional; Phase 3).
- **Numeric pass threshold:** exit code 0; a `state` change writes nothing until the save gesture.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** changing the `state` segment marks the field unsaved and writes nothing until `ctrl+s`.
  - **Shipped surface:** the inspector's `state` segment.
  - **Acceptance test(s):** AT-007
  - **Boundary catalog (QC-3):** ☑ empty — no `state` change ⇒ no draft; ☑ boundary — a `state` change to the shown value is not dirty; ☐ invalid ☐ error.
  - **Negative control:** on today's code AT-007 goes RED: `on_ds_segmented_changed` (`inspector.py:367-373`) posts `FieldCommitted("state", …)` immediately, which writes. Executed RED owed at Phase 3.

### HLR-007 — the shipped behaviours are guarded by their declared nodes
- **Traceability:** US-002
- **Ledger:** LED-2026-10-08-data-safety-batch.7, LED-2026-10-08-data-safety-batch.12, LED-2026-10-08-data-safety-batch.15, LED-2026-10-08-data-safety-batch.22, LED-2026-10-08-data-safety-batch.30, LED-2026-10-08-data-safety-batch.57
- **Statement:** When the operator presses the help chord twice from a map, the system shall present exactly one legend without growing the screen stack; and when a workspace map fails to load, the system shall declare that damaged state on that map's own card while every other card keeps its true values.
- **Rationale (informative):** B-100 — the behaviours hold today but are unguarded (AT-044) or guarded under a different id (N13.3), so a regression ships silently.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_double_question_mark.py` (provisional, new file — the re-cut in ARQ §5 keeps AT-044 out of `tests/test_help_scope.py`); plus the reconciled `LLR-N13.1.5` nodes `python -B -m pytest -q -p no:cacheprovider tests/test_repair_cycles.py -k n13_1_5`.
- **Numeric pass threshold:** exit code 0; the screen stack length is unchanged after the second `?`.
- **Priority:** medium
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** a doubled `?` leaves exactly one legend on the stack; a damaged map's card declares `DAMAGED_MAP_STATE` while healthy cards keep their values.
  - **Shipped surface:** the help legend (the `?` chord) and the home card table.
  - **Acceptance test(s):** AT-044, AT-025b
  - **Boundary catalog (QC-3):** ☑ empty — a single `?` opens exactly one legend (no-op second); ☑ boundary — the second `?` while the legend is already up; ☐ invalid ☑ error — the damaged-card declaration for a map that raises or records a load warning.
  - **Negative control:** AT-044 goes RED today only as an absent node (no on-disk node realises it — grep `doubled` in `tests/` → 0 hits); the behaviour itself holds (P-2). The mutation the node must redden on is binding `?` in the help seat (or letting the help legend inherit the app chord), which opens a second legend. AT-025b is already green under `LLR-N13.1.5` (P-3), so its reconciliation has no executed RED side — declared, and the absence of a RED side is why it is written as a reconciliation, not a new node (LED-…7).

### HLR-008 — every declared acceptance id resolves to a node or is retired
- **Traceability:** US-003
- **Ledger:** LED-2026-10-08-data-safety-batch.7, LED-2026-10-08-data-safety-batch.13, LED-2026-10-08-data-safety-batch.12, LED-2026-10-08-data-safety-batch.14, LED-2026-10-08-data-safety-batch.15, LED-2026-10-08-data-safety-batch.22, LED-2026-10-08-data-safety-batch.28
- **Statement:** Every declared acceptance id that this batch carries shall be resolved to an on-disk test node or retired, so that the traceability record matches what the suite guards.
- **Rationale (informative):** B-101 — a declared id with no node is a test the next refactor deletes without reddening anything (C-18).
- **Validation:** `inspection`
- **Executed verification:** grep each id's definition in `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md` and grep `tests/` for a realising node; the observable condition is the reconciliation list below.
- **Numeric pass threshold:** every id in {AT-041, AT-042, AT-033, AT-034, AT-035} is either resolved or retired with a ledger entry.
- **Priority:** medium
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** the maintainer greps `tests/` for each declared AT id and finds each one resolved to a named node or retired (definitional/inspectional — no shipped surface).
  - **Shipped surface:** the traceability record (`.dev-flow/BACKLOG.md` and this batch's ledger).
  - **Acceptance test(s):** AT-041 (reconciled), AT-042 (partially realised — two arms owed as new nodes); AT-033, AT-034, AT-035 (retired)
  - **Boundary catalog (QC-3):** none — inspection (structural review of the traceability record, no input class applies).
  - **Negative control:** none — inspection (no executed arm); the observable condition is the absence each grep records. The reconciliation is a match between an id and an existing node, verified by grep at draft time.

### HLR-009 — the legend own-keys test is deterministic
- **Traceability:** US-004
- **Ledger:** LED-2026-10-08-data-safety-batch.12, LED-2026-10-08-data-safety-batch.15, LED-2026-10-08-data-safety-batch.16, LED-2026-10-08-data-safety-batch.32, LED-2026-10-08-data-safety-batch.49
- **Statement:** The legend own-keys test shall position its scroll pane immediately and settle it before any key is sampled, so that the test passes deterministically under load.
- **Rationale (informative):** FLAKE-2 — a queued `scroll_to` landing inside the next key's measurement window made an inert key read as effective; a poisoned instrument invalidates every counterfactual touching it.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_help_scope.py::test_hlr_n16_4_legend_declares_its_own_keys` (provisional until the fix lands; the four sites are reconciled at Phase 4).
- **Numeric pass threshold:** exit code 0; the injected-delay regression arm is GREEN (its RED is the executed counterfactual `spike/red_green_flake2.py` 2/2, not a second run of the same committed node — a single committed node cannot be both RED and GREEN).
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** the own-keys test, run under the spike's late-landing fixture, fails on the current code and passes with `immediate=True` and a settle assertion.
  - **Shipped surface:** the test itself (`tests/test_help_scope.py:328` and its three sibling `scroll_to` sites).
  - **Acceptance test(s):** AT-008 (a test-instrument check — the acceptance is of the instrument's determinism, not of product behaviour)
  - **Boundary catalog (QC-3):** ☑ empty — the pane already at the target offset (scroll is a no-op); ☑ boundary — the mid-range position `max_scroll_y // 2` the fixture delays; ☐ invalid ☑ error — a scroll that never lands (the settle assertion fails loud).
  - **Negative control:** AT-008's RED is recorded as an executed counterfactual, not a committed RED/GREEN pair: `spike/red_green_flake2.py` fails 2/2 on the current step (`work but not painted: ['ctrl+pagedown','left','right']`) and passes 2/2 with `immediate=True`. Executed in the spike, 2026-10-08; the regression arm is minted at Phase 3.

### 3.1 Black-box acceptance tests (Layer B)

AT ids in this contract are batch-local: they restart at 001 per batch, and ids from other batches (`AT-025b`, `AT-033`/`AT-034`/`AT-035`, `AT-041`/`AT-042`, `AT-044`) are cited with their batch path `.dev-flow/2026-08-26-ui-next-batch-02/`. Surfaces name keys, screens and files only — no internal symbol names. The observation method for every AT is stated once in §5.1 (`obs`): a Textual `App.run_test` pilot pressing real keys; sha256 of the map's `.mmd` and `_nodos.yml` before and after the scenario; "written once" = the hash pair changes exactly once.

| id | story | surface | stimulus | assertion | RED today |
|----|-------|---------|----------|-----------|-----------|
| AT-001 | US-001 | the map screen inspector and the `ctrl+s` key | one stray key, then blur + cursor change | the `.mmd` and `_nodos.yml` are byte-identical to before and the field shows unsaved | yes — blur writes both files on a real keystroke (sha256 differs) |
| AT-002 | US-001 | the `ctrl+s` key, the map's `.mmd`/`_nodos.yml` files, and the `u` undo key | `ctrl+s` after an edit; then `u` | the files are UNCHANGED before `ctrl+s` and written ONCE after; `u` restores the pre-save state | yes — `ctrl+s` is unbound, no draft exists |
| AT-002a | US-001 | Layer-A fault-injection test — declared seam: the store's save raises (two arms: after writing zero files; after writing both files) | an edit in two fields, then `ctrl+s` against the raising store | the map is reloaded from disk; zero-files arm: both files byte-identical and both fields still marked unsaved; both-files arm: both files carry the edit and the draft is empty (every field equals disk); in both arms the hash pair changes at most once (no write from failure handling) | yes — mutation "keep the in-memory graph instead of reloading" leaves the both-files arm's fields dirty; mutation "clear the draft on any failure" empties it in the zero-files arm |
| AT-003 | US-001 | the inspector header and its field rows | edit one field, then a second | the header shows `● unsaved (1)` then `● unsaved (2)` and each edited field carries a marker | yes — no unsaved count, no markers |
| AT-004 | US-001 | the save · discard · stay guard modal (keys `s`/`d`/`esc`) | node change with a pending draft | the guard presents once; `save`/`discard` proceed, `stay` aborts | yes — changing node runs with no guard; mutation "`stay` re-points anyway" moves the cursor |
| AT-005a | US-001 | the save · discard · stay guard modal (keys `s`/`d`/`esc`) | leaving the map screen with `q` with a pending draft | the guard presents once; `save`/`discard` pop the map screen (`len(app.screen_stack)` drops by one), `stay` keeps it | yes — `q` leaves the map with no guard; mutation "`stay` falls through" pops the screen (stack depth drops) |
| AT-005b | US-001 | the save · discard · stay guard modal (keys `s`/`d`/`esc`) | leaving the map screen with `esc` with a pending draft | the guard presents once; `save`/`discard` pop the map screen (`len(app.screen_stack)` drops by one), `stay` keeps it | yes — `esc` leaves the map with no guard; mutation "`stay` falls through" pops the screen (stack depth drops) |
| AT-006 | US-001 | the inspector's `↵` key and the hint line | `↵` in a dirty field | the files are unchanged, focus leaves the field, and the hint names `ctrl+s` | yes — `↵` writes, the hint reads `↵ save` |
| AT-007 | US-001 | the `state` segment in the inspector | change the `state` segment | the field marks unsaved and nothing writes until `ctrl+s` | yes — a `state` change writes immediately |
| AT-008 | US-004 | the own-keys test file `tests/test_help_scope.py:328` | the injected-delay fixture — a delayed positioning `scroll_to` that lands inside the next key's measurement window | the loop reports no `work but not painted` (`effective == painted`) and passes deterministically | yes — fails 2/2 under the fixture (recorded executed counterfactual `spike/red_green_flake2.py`) |
| AT-009 | US-001 | the `u` undo key and the inspector header | edit a field, `ctrl+s`, then `u`, then leave the field (focus-out) | the last save is undone, the header re-paints `● unsaved (1)` recomputed against the restored stored value, and the draft's VALUES remain untouched | yes — today there is no draft; mutation "markers not recomputed after `u`" leaves `● unsaved (N)` diffed against the pre-`u` values |
| AT-010 | US-001 | the map screen inspector and the `ctrl+s` key | type in a field, then press `ctrl+s` without leaving the field | the typed text is in both `.mmd` and `_nodos.yml` | yes — a draft that updated only on blur/submit would save without the typed text, so AT-010 reddens on that mutation |
| AT-011 | US-001 | the save · discard · stay guard modal (keys `s`/`d`/`esc`) | pressing `↵` (open card) on a node that links to another map, with a pending draft | the guard presents before the push; `save`/`discard` push the linked map (`len(app.screen_stack)` grows by one), `stay` keeps the stack depth | yes — opening a linked map pushes with no guard; mutation "push before the guard answers" grows the stack under the modal |
| AT-012 | US-001 | the save · discard · stay guard modal (keys `s`/`d`/`esc`) | quitting (`ctrl+q`) with a pending draft | the guard presents once; `save`/`discard` exit the app (`app.is_running` false), `stay` keeps it running (`app.is_running` true) | yes — `ctrl+q` exits with no guard; mutation "quit proceeds on `stay`" stops the app |
| AT-013 | US-001 | the quit walk (Layer-A injection test of LLR-003.5 — a defensive invariant, reachable only by injecting the lower screen's draft) | a stack of two map screens, the lower one holding a pending draft (injected), then `ctrl+q` | `action_quit` walks every `MapScreen` and guards the lower screen's draft before exit | yes — quitting walks no lower screen's draft |
| AT-014a | US-001 | the save · discard · stay guard modal (keys `s`/`d`/`esc`) and the map's `.mmd`/`_nodos.yml` files | an add-child write (`a`) with a pending draft | the guard presents before the write, and the draft's values never reach either file through the write | yes — `a` writes immediately with no guard; mutation "guard opened after the write" changes the hash pair before the answer |
| AT-014b | US-001 | the save · discard · stay guard modal (keys `s`/`d`/`esc`) and the map's `.mmd`/`_nodos.yml` files | an archive write (`x`) with a pending draft | the guard presents before the write, and the draft's values never reach either file through the write | yes — `x` writes immediately with no guard; mutation "guard opened after the write" changes the hash pair before the answer |
| AT-014c | US-001 | the save · discard · stay guard modal (keys `s`/`d`/`esc`) and the map's `.mmd`/`_nodos.yml` files | an add-attachment write (`A`) with a pending draft | the guard presents before the write, and the draft's values never reach either file through the write | yes — `A` writes immediately with no guard; mutation "guard opened after the write" changes the hash pair before the answer |
| AT-014d | US-001 | the save · discard · stay guard modal (keys `s`/`d`/`esc`) and the map's `.mmd`/`_nodos.yml` files | a remove-attachment write (`X`) with a pending draft | the guard presents before the write, and the draft's values never reach either file through the write | yes — `X` writes immediately with no guard; mutation "guard opened after the write" changes the hash pair before the answer |
| AT-015 | US-001 | the guard modal title | a map id or node title carrying an ESC (0x1B) payload | the rendered title is scanned and carries no 0x1B byte (the payload is coerced), so no control effect reaches the terminal | yes — a title built with `markup=False` alone (without `plain()`) passes ESC, so AT-015 reddens on that mutation |
| AT-044 (.dev-flow/2026-08-26-ui-next-batch-02/) | US-002 | the help legend (the `?` chord) | press the help chord (`?`) twice from a map | exactly one legend; the screen stack does not grow | yes — only as an absent node today; the mutation it must redden on is binding `?` in the help seat (or letting the legend inherit the app chord), which opens a second legend |
| AT-025b (.dev-flow/2026-08-26-ui-next-batch-02/) | US-002 | the home card table | open a workspace holding a map that fails to load | that map's card declares the damaged state; every other card keeps its true values | none — already green under the existing damaged-card nodes (reconciliation, no executed RED) |
| AT-041 (.dev-flow/2026-08-26-ui-next-batch-02/) | US-003 | the traceability record (`tests/test_repair_layout.py:274`) — inspection · reconciliation | reconcile the declared id to its on-disk node | resolves to `test_at_r12_pressing_help_presents_every_map_binding` | none — inspection (reconciliation, no executed arm) |
| AT-042 (.dev-flow/2026-08-26-ui-next-batch-02/) | US-003 | the traceability record (`tests/test_repair_layout.py:441`) — inspection · reconciliation; two new nodes (LLR-008.3) | reconcile the largest-set arm; realise the smallest-set (`app`) and no-scope-screen arms as new nodes | the largest-set arm resolves to `test_tc_r25`; the two missing arms are new nodes | none for the reconciliation; the two new arms go RED as absent nodes today |
| AT-033, AT-034, AT-035 (.dev-flow/2026-08-26-ui-next-batch-02/) | US-003 | the traceability record — inspection · retired | retire the three ids with a ledger entry | the three ids carry no obligation in this batch's Atlas | none — inspection (retired; ids absent by design) |

---

## 4. Low-level requirements (LLR)

> Each LLR decomposes an HLR into a verifiable property at the implementation level.
> Same regime: EARS syntax owed in `full`, recommended in `core`. ID format: `LLR-<HLR>.<M>`.

### LLR-001.1 — the inspector holds the per-node draft
- **Traceability:** HLR-001
- **Ledger:** LED-2026-10-08-data-safety-batch.2
- **Statement:** The `FichaInspector` shall hold one node's draft — `draft_node_id`, `draft_values()`, `has_draft()`, `clear_draft()` — in memory for the widget's life, and shall never persist the draft on its own.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_inspector.py -k draft` (provisional until Phase 3; the draft surface is `NEW — created in Phase 3`).
- **Numeric pass threshold:** exit code 0; `draft_values()` returns a copy and `has_draft()` is false after `clear_draft()`.
- **Negative control:** none — the draft surface does not exist today (`grep -rn "draft_values\|has_draft\|clear_draft" mapper/widgets/inspector.py` → 0 hits), so the RED side is owed when the surface is minted at Phase 3.
- **Boundary catalog:** ☑ empty — a node with no edits ⇒ `has_draft()` false; ☑ boundary — editing a field back to the shown value clears it from the draft; ☐ invalid ☐ error.

### LLR-001.2 — text fields update the draft on every keystroke and post nothing
- **Traceability:** HLR-001
- **Ledger:** LED-2026-10-08-data-safety-batch.6, LED-2026-10-08-data-safety-batch.20, LED-2026-10-08-data-safety-batch.50
- **Statement:** When an inspector text field changes, blurs, or is submitted, the `FichaInspector` shall update the draft on every `Input.Changed` (each keystroke) and shall post no `FieldCommitted`; each draft entry shall be keyed to the node of the input that sent the change (never the re-pointed node), so a stale `Input.Changed` arriving after `show()` re-points cannot write another node's draft.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_inspector.py -k draft` (provisional until Phase 3).
- **Numeric pass threshold:** exit code 0; blur, submit and each keystroke produce no `FieldCommitted` message and no file write, and the draft holds the value typed so far.
- **Negative control:** on today's code the current behaviour (blur/submit posts `FieldCommitted`, `inspector.py:347-365`) is the RED side; the assertion is inverted once the draft lands.
- **Boundary catalog:** ☑ empty — blur with no edit changes nothing; ☑ boundary — blur after editing back to the shown value leaves no dirty field; ☐ invalid ☐ error.

### LLR-001.3 — `FieldCommitted` removed in one increment (A3)
- **Traceability:** HLR-001
- **Ledger:** LED-2026-10-08-data-safety-batch.6, LED-2026-10-08-data-safety-batch.9, LED-2026-10-08-data-safety-batch.18, LED-2026-10-08-data-safety-batch.29, LED-2026-10-08-data-safety-batch.40, LED-2026-10-08-data-safety-batch.44
- **Statement:** The `FichaInspector.FieldCommitted` message, its producer, and `MapScreen.on_ficha_inspector_field_committed` shall be removed in the same increment, leaving no live producer or consumer; and the seven docstring/test-name lines that mention `FieldCommitted` (`tests/test_g6_store_surrogates.py:8,105,109,111,113`, `tests/test_inspector.py:61`, `mapper/app.py:3345`) shall be renamed in the same increment.
- **Validation:** `inspection`
- **Executed verification:** `grep -rn "FieldCommitted\|field_committed" --include=*.py mapper tests` → 0 hits post-increment. Pre-state executed 2026-10-08: 17 lines (10 code sites). Code sites: `mapper/widgets/inspector.py:68,365,372`, `mapper/app.py:3344`, `tests/test_inspector.py:103,162`, `tests/test_g6_store_surrogates.py:133,152,176`, `tests/test_worklist_safety.py:254`. Docstring/test-name lines (7): `tests/test_g6_store_surrogates.py:8,105,109,111,113`, `tests/test_inspector.py:61`, `mapper/app.py:3345` (the `FieldCommitted` type annotation). The 0-line post-state threshold is meetable only if those docstrings, the comment and the test name `test_g6b_field_committed_...` are renamed in the same increment — removing the code sites alone leaves 7 matching lines.
- **Numeric pass threshold:** 0 references post-increment.
- **Negative control:** none — inspection (structural review); the observable condition is the absence the census greps for.
- **Boundary catalog:** none — inspection.

### LLR-001.4 — `ctrl+s` pulls the draft and saves once
- **Traceability:** HLR-001
- **Ledger:** LED-2026-10-08-data-safety-batch.27, LED-2026-10-08-data-safety-batch.45, LED-2026-10-08-data-safety-batch.54
- **Statement:** The `KEYMAP` seat shall gain a map-scope row binding `ctrl+s` to `save_draft` (glyph `ctrl+s`, label `save`), and when the operator presses `ctrl+s`, `MapScreen.action_save_draft` shall read `inspector.draft_values()` and persist the applied draft through `MapStore.save` exactly once; a failure is handled by LLR-004.2 (reload from disk, keep the unwritten fields as draft).
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_save.py -k save` (provisional; `action_save_draft` is `NEW — created in Phase 3`, and the `ctrl+s → save_draft` seat row is `NEW — created in Phase 3`).
- **Numeric pass threshold:** exit code 0; one `ctrl+s` issues one `store.save` call.
- **Negative control:** on today's code `ctrl+s` is unbound (the `KEYMAP` seat has no `save_draft` row, `mapper/keymap.py:137-263`) — the RED side is the missing gesture. Executed RED owed at Phase 3.
- **Boundary catalog:** ☑ empty — `ctrl+s` with no draft writes nothing; ☑ boundary — a multi-field draft is applied in one save; ☐ invalid ☑ error — a failing save reloads from disk and keeps the unwritten fields (LLR-004.2).

### LLR-002.1 — dirty means differs from the shown value
- **Traceability:** HLR-002
- **Ledger:** LED-2026-10-08-data-safety-batch.38
- **Statement:** A field shall be dirty when its draft value differs from the value the form showed for it (`darkside.plain(stored)`), and the `FichaInspector` shall overlay the draft when it builds `_rows`. For the `state` segment the shown value is `STATE_VALUES[active]`, where `active = STATE_VALUES.index(ficha.state) if ficha.state in STATE_VALUES else 0` — a node whose stored state is unknown shows `ok` (index 0) and is not dirty.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_inspector.py -k dirty` (provisional until Phase 3).
- **Numeric pass threshold:** exit code 0; a node whose `plain()`-coerced title equals the stored title is not dirty on open.
- **Negative control:** the stored-vs-shown distinction is the load-bearing rule — a test that flags a node dirty solely because `plain(stored) != stored` goes RED on a node whose title `plain()` alters (`darkside.plain` strips control points, `darkside.py:550-561`). Executed RED owed at Phase 3.
- **Boundary catalog:** ☑ empty — a freshly opened node is not dirty; ☑ boundary — an edit back to the shown value clears dirty; ☑ invalid — a value that `plain()` alters is compared against its coerced form; ☐ error.

### LLR-002.2 — the header and per-field markers paint the unsaved state
- **Traceability:** HLR-002
- **Ledger:** LED-2026-10-08-data-safety-batch.50
- **Statement:** The `FichaInspector` shall paint a dirty marker on each changed field and `● unsaved (N)` in its header while a draft is pending, and shall update those markers without remounting the focused field (a per-keystroke `show()` → `_rebuild` remount destroys the focused `Input` and leaves a stale `Input.Changed`).
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_inspector.py -k unsaved` (provisional until Phase 3).
- **Numeric pass threshold:** exit code 0; N equals the count of dirty fields.
- **Negative control:** on today's code the header (`inspector.py:141` `_header`) paints no unsaved count, so the assertion is RED today. Executed RED owed at Phase 3.
- **Boundary catalog:** ☑ empty — no draft ⇒ no `● unsaved`; ☑ boundary — N increments and decrements with the dirty count; ☐ invalid ☐ error.

### LLR-003.1 — the guard modal returns one of three answers
- **Traceability:** HLR-003
- **Ledger:** LED-2026-10-08-data-safety-batch.4, LED-2026-10-08-data-safety-batch.8, LED-2026-10-08-data-safety-batch.24, LED-2026-10-08-data-safety-batch.27, LED-2026-10-08-data-safety-batch.37, LED-2026-10-08-data-safety-batch.53
- **Statement:** The `DraftGuardScreen` (new, `mapper/screens/draft_guard.py`) shall dismiss with exactly one of `save` (`s`), `discard` (`d`), or `stay` (`esc`), bound from a new `draft` modal scope (`SCOPE_DRAFT = "draft"`, `GROUP_SCOPE["draft"] = SCOPE_DRAFT`, `MODAL_SCOPES` widened to include `SCOPE_DRAFT`), and shall paint a title composed of `darkside.plain(<map id>)` plus `darkside.plain(<node title as stored>)` with `markup=False` — the title names the map the operator is about to leave, and `plain()` strips every control character (`darkside.py:550`) that `markup=False`'s `Content` strip leaves in (which drops BEL/BS/VT/FF/CR only, `textual/content.py:56-62`, so ESC passes).
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_save.py -k modal` (provisional; `DraftGuardScreen` is `NEW — created in Phase 3`).
- **Numeric pass threshold:** exit code 0; the modal returns exactly the token for the key pressed.
- **Negative control:** the hostile-title case is the RED side, two payloads: (1) a title carrying `[@click=…]` must render literally — no parse, no click-binding (SEC-H2; `_ConfirmScreen` precedent `app.py:384-401`); (2) an ESC (0x1B) payload must reach the terminal with no control effect — `plain()` coerces it, `markup=False` alone would not. Executed RED owed at Phase 3.
- **Boundary catalog:** ☑ empty — no title; ☑ boundary — a title with markup brackets; ☑ boundary — a title carrying an ESC (0x1B) payload; ☐ invalid ☑ error — a title carrying a lone surrogate is `plain()`-coerced.

### LLR-003.2 — the node-change guard sits at the one re-pointing site
- **Traceability:** HLR-003
- **Ledger:** LED-2026-10-08-data-safety-batch.4, LED-2026-10-08-data-safety-batch.45, LED-2026-10-08-data-safety-batch.55
- **Statement:** Before re-pointing the inspector to a new node, `MapScreen.refresh_canvas` shall present the guard when a draft is pending and shall re-point only on `save` or `discard`.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_save.py -k node_change` (provisional until Phase 3).
- **Numeric pass threshold:** exit code 0; a cursor move with a pending draft presents the guard and `stay` restores the cursor.
- **Negative control:** on today's code a cursor move re-points immediately with no guard (`app.py:3281`, the only `.show(` call on the inspector). Executed RED owed at Phase 3.
- **Boundary catalog:** ☑ empty — no draft ⇒ the cursor moves unguarded; ☑ boundary — a cursor move onto the same node needs no guard; ☐ invalid ☑ error — a failing `save` reloads the map from disk per LLR-004.2, then the guard holds at `stay`.

### LLR-003.3 — leaving the map screen is guarded
- **Traceability:** HLR-003
- **Ledger:** LED-2026-10-08-data-safety-batch.4, LED-2026-10-08-data-safety-batch.45, LED-2026-10-08-data-safety-batch.55
- **Statement:** `MapScreen.action_home` and the pop branch of `MapScreen.action_back_or_home` shall present the guard when a draft is pending and shall pop only on `save` or `discard`.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_save.py -k leave` (provisional until Phase 3).
- **Numeric pass threshold:** exit code 0; `q`/`esc` with a pending draft presents the guard and `stay` keeps the map open.
- **Negative control:** on today's code `action_home` (`app.py:4683-4684`) and the pop branch of `action_back_or_home` (`app.py:4719`) pop with no guard. Executed RED owed at Phase 3.
- **Boundary catalog:** ☑ empty — no draft ⇒ the pop proceeds; ☑ boundary — `esc` with a live search clears the search (no draft involved); ☐ invalid ☑ error — a failing `save` reloads the map from disk per LLR-004.2, then the guard holds at `stay`.

### LLR-003.4 — following a link is guarded
- **Traceability:** HLR-003
- **Ledger:** LED-2026-10-08-data-safety-batch.4, LED-2026-10-08-data-safety-batch.25, LED-2026-10-08-data-safety-batch.45, LED-2026-10-08-data-safety-batch.55
- **Statement:** When following a link pushes a second `MapScreen`, the system shall present the guard first when a draft is pending. The link guard is unconditional (R6), never deferred.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_save.py -k link` (provisional until Phase 3).
- **Numeric pass threshold:** exit code 0; opening a linked map with a pending draft presents the guard before the push.
- **Negative control:** on today's code `action_open_ficha` pushes the linked `MapScreen` with no guard (`app.py:3566`). Executed RED owed at Phase 3.
- **Boundary catalog:** ☑ empty — no draft ⇒ the push proceeds; ☑ boundary — a link to the same map; ☐ invalid ☑ error — a failing `save` reloads the map from disk per LLR-004.2, then the guard holds at `stay`.

### LLR-003.5 — quitting guards every pending map screen
- **Traceability:** HLR-003
- **Ledger:** LED-2026-10-08-data-safety-batch.4, LED-2026-10-08-data-safety-batch.31, LED-2026-10-08-data-safety-batch.48, LED-2026-10-08-data-safety-batch.55
- **Statement:** `MapperApp.action_quit` shall walk the screen stack, guard every `MapScreen` with a pending draft — a lower (non-top) `MapScreen` under a pushed screen included — and shall not be re-entrant.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_save.py -k quit` (provisional until Phase 3).
- **Numeric pass threshold:** exit code 0; a second `ctrl+q` while the guard is up does not stack a second modal.
- **Negative control:** on today's code `MapperApp.action_quit` (`app.py:4937-4938`) exits immediately with no guard. Executed RED owed at Phase 3.
- **Boundary catalog:** ☑ empty — no draft on any screen ⇒ quit proceeds; ☑ boundary — a draft on a lower (non-top) `MapScreen` is still guarded; ☐ invalid ☑ error — a failing `save` reloads the map from disk per LLR-004.2, then the guard holds at `stay`.

### LLR-003.6 — a structural write with a pending draft opens the guard first
- **Traceability:** HLR-003
- **Ledger:** LED-2026-10-08-data-safety-batch.26, LED-2026-10-08-data-safety-batch.36, LED-2026-10-08-data-safety-batch.45, LED-2026-10-08-data-safety-batch.55
- **Statement:** Before any structural write — `action_add_child` (`a`), `action_archive` (`x`), `action_add_attachment` (`A`), `action_remove_attachment` (`X`) — the `MapScreen` shall present the guard when a draft is pending and shall run the write only on `save` or `discard`; on `stay` the write is aborted. The draft is never in `self.graph` until saved, so the guard must open before the write, not after it.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_save.py -k structural` (provisional until Phase 3).
- **Numeric pass threshold:** exit code 0; a structural write with a pending draft presents the guard, and the draft's values never reach the `.mmd`/`_nodos.yml` files through the write.
- **Negative control:** on today's code `action_add_child` (`app.py:4545`), `action_archive` (`app.py:4592`), `action_add_attachment` (`app.py:3487`) and `action_remove_attachment` (`app.py:3490`) write the whole graph immediately with no guard. Executed RED owed at Phase 3.
- **Boundary catalog:** ☑ empty — no draft ⇒ the write proceeds unguarded; ☑ boundary — a structural write that removes the draft's node; ☐ invalid ☑ error — a failing `save` reloads the map from disk per LLR-004.2, then the guard holds at `stay`.

### LLR-004.1 — one snapshot and one write per save
- **Traceability:** HLR-004
- **Ledger:** LED-2026-10-08-data-safety-batch.3, LED-2026-10-08-data-safety-batch.45, LED-2026-10-08-data-safety-batch.54
- **Statement:** The save routine shall call `_push_snapshot` exactly once before applying all drafted fields and `MapStore.save` exactly once after.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_save.py -k one_snapshot` (provisional until Phase 3).
- **Numeric pass threshold:** exit code 0; one save adds exactly one entry to `_snapshots` and issues one `store.save`.
- **Negative control:** on today's code the field-commit path pushes a snapshot per field (`app.py:3362` inside the per-commit handler), so a multi-field edit is RED against "one snapshot". Executed RED owed at Phase 3.
- **Boundary catalog:** ☑ empty — `ctrl+s` with no draft pushes nothing; ☑ boundary — a multi-field draft is one snapshot; ☐ invalid ☑ error — a failed save discards the snapshot pushed for it in memory (no pop through `_pop_snapshot`, no write), leaving the undo stack as it was before the save (LLR-004.2).

### LLR-004.2 — success clears the draft; a failure reloads from disk and keeps what did not reach it
- **Traceability:** HLR-004
- **Ledger:** LED-2026-10-08-data-safety-batch.23, LED-2026-10-08-data-safety-batch.45, LED-2026-10-08-data-safety-batch.46, LED-2026-10-08-data-safety-batch.52, LED-2026-10-08-data-safety-batch.54, LED-2026-10-08-data-safety-batch.58
- **Statement:** On a successful save the system shall set `base_graph`, call `inspector.clear_draft()`, and toast. On a failed save the system shall reload the map from disk through `MapStore.load` (the entry `MapScreen` already uses, `mapper/app.py:1623`; a missing sidecar loads as `{}`, `mapper/store.py:698-700`), re-establish the view exactly as the screen's own load path does (`mapper/app.py:1622-1636`: `base_graph` and `self.graph` set to the reloaded graph, `_notice_load_warnings` surfaced, `self.nav` rebuilt as a new `NavigationModel`; `focus_active` cleared, since a focused view is a subgraph of `base_graph`, `app.py:3912-3914`; the cursor kept when its node still exists, otherwise moved to the root as `_pop_snapshot` does, `app.py:3528-3529`), discard the snapshot pushed for this save in memory, keep the draft and re-diff it against the reloaded values (LLR-002.1), hold any guard at `stay`, and toast an error naming `ctrl+s`. If the reload itself raises, the system shall restore the pre-save graph and view in memory by the same re-establishment, with no store call, keep the draft, and toast an error telling the operator to leave and reopen the map. A draft entry whose node no longer exists in the reloaded graph shall be dropped with a warning naming the field, and no second guard shall open while one is held at `stay`. Failure handling shall perform no write to the map's `.mmd` or `_nodos.yml`; the reload's rebuild of the derived index (`MapStore.load` → `_reindex`, `mapper/store.py:783`, `:926-965`) is a cache refresh, not an operator-visible write.
- **Rationale (informative):** disk is the truth after any failure. A field whose value reached disk re-diffs as clean on its own and a field whose value did not stays dirty, so no phase classification is needed.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_save.py -k failure` (provisional until Phase 3); the fault-injection seam (AT-002a) makes the store's save raise after writing zero files and after writing both files.
- **Numeric pass threshold:** exit code 0; zero-files arm: both files byte-identical, every drafted field still dirty; both-files arm: both files carry the edit, the draft is empty; both arms: the hash pair changes at most once and the undo stack length equals its pre-save length.
- **Negative control:** on today's code a failed save leaves the applied mutation in `self.graph` (`mapper/app.py:3362-3375`), which a later structural save would persist (risk A-10). The discriminating mutations are named in AT-002a. Executed RED owed at Phase 3.
- **Boundary catalog:** ☑ empty — `ctrl+s` with no draft is a no-op; ☑ boundary — a multi-field draft where only some values reach disk keeps exactly the others; ☑ boundary — a missing sidecar on reload; ☑ boundary — the cursor's node is gone after the reload (cursor to root, no second guard); ☑ boundary — a draft entry whose node is gone (dropped with a warning); ☑ boundary — focus was active (cleared); ☐ invalid ☑ error — the reload itself raises (pre-save graph and view restored in memory, draft kept, no map-file write).

### LLR-004.3 — `u` undoes the last save and leaves the draft
- **Traceability:** HLR-004
- **Ledger:** LED-2026-10-08-data-safety-batch.3, LED-2026-10-08-data-safety-batch.11, LED-2026-10-08-data-safety-batch.33, LED-2026-10-08-data-safety-batch.35
- **Statement:** While a draft is pending, `u` shall undo the last save and leave the pending draft's values untouched, recomputing only the dirty markers against the restored stored values.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_save.py -k undo` (provisional until Phase 3).
- **Numeric pass threshold:** exit code 0; after `u`, the restored values are re-diffed against the restored stored values and the pending draft survives.
- **Negative control:** the control is the dirty-marker re-diff, not the absent draft: after `u` restores the graph, each field's marker must be recomputed against the value the restored form shows — a mutation that leaves the markers diffed against the pre-`u` values goes RED. Today `u` (`_pop_snapshot`, `app.py:3517-3533`) replaces `self.graph` wholesale with no marker re-diff. Executed RED owed at Phase 3.
- **Boundary catalog:** ☑ empty — `u` with no snapshot toasts "nothing to undo"; ☑ boundary — `u` where the cursor's node disappears fires the node-change guard; ☐ invalid ☐ error — a failed `u` while a draft is pending is a residual (risk A-10): it restores the graph but leaves the draft unresolved, recorded rather than mitigated.

### LLR-004.4 — the write stays whole-graph
- **Traceability:** HLR-004
- **Ledger:** none
- **Statement:** The save shall write through the whole-graph `MapStore.save(map_id, graph)` and shall add no partial-write path.
- **Validation:** `inspection`
- **Executed verification:** inspect the save call site for `MapStore.save(map_id, graph)`; the observable condition is that no `save_field`-style partial write is introduced. `mapper/store.py:809` `def save(self, map_id, graph)` writes the whole graph (sidecar built inside at `:469`).
- **Numeric pass threshold:** 0 new partial-write call sites.
- **Negative control:** none — inspection (structural review); the observable condition is the absence of a partial-write path.
- **Boundary catalog:** none — inspection.

### LLR-005.1 — `↵` leaves the field and retains the draft
- **Traceability:** HLR-005
- **Ledger:** LED-2026-10-08-data-safety-batch.5
- **Statement:** When the operator presses `↵` in an inspector field, the `FichaInspector` shall leave the field and retain the draft without writing.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_inspector.py -k enter` (provisional until Phase 3).
- **Numeric pass threshold:** exit code 0; `↵` produces no write and focus leaves the field.
- **Negative control:** on today's code `on_input_submitted` (`inspector.py:347-349`) calls `_commit`, which posts `FieldCommitted` and writes — the RED side. Executed RED owed at Phase 3.
- **Boundary catalog:** ☑ empty — `↵` in a field with no edit leaves the field and writes nothing; ☑ boundary — `↵` after editing back to the shown value leaves no draft; ☐ invalid ☐ error.

### LLR-005.2 — the hint names `ctrl+s`, read from the seat
- **Traceability:** HLR-005
- **Ledger:** LED-2026-10-08-data-safety-batch.5
- **Statement:** The hint at `mapper/app.py:4043` shall name the `save_draft` glyph read from the seat (`_seat_glyph`, `app.py:3623`) instead of the literal `↵ save`.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_save.py -k hint` (provisional; the `save_draft` seat row is `NEW — created in Phase 3`).
- **Numeric pass threshold:** exit code 0; the hint reads `ctrl+s save` (the seat glyph and label for `save_draft`).
- **Negative control:** on today's code the hint reads `↵ save` (`app.py:4043`, comment `:4040`) and the seat has no `save_draft` row — the RED side. Executed RED owed at Phase 3.
- **Boundary catalog:** ☑ empty — no missing field ⇒ the hint is not painted; ☑ boundary — the hint on a node with a missing required field; ☐ invalid ☐ error.

### LLR-006.1 — the `state` segment routes through the draft
- **Traceability:** HLR-006
- **Ledger:** LED-2026-10-08-data-safety-batch.2
- **Statement:** When the `state` segment changes, the `FichaInspector` shall update the draft and shall post no immediate `FieldCommitted`.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_inspector.py -k state` (provisional until Phase 3).
- **Numeric pass threshold:** exit code 0; a `state` change writes nothing until the save gesture.
- **Negative control:** on today's code `on_ds_segmented_changed` (`inspector.py:367-373`) posts `FieldCommitted("state", …)` immediately — the RED side. Executed RED owed at Phase 3.
- **Boundary catalog:** ☑ empty — no `state` change ⇒ no draft; ☑ boundary — a `state` change back to the shown value is not dirty; ☐ invalid ☐ error.

### LLR-006.2 — the draft keys cover every ficha field
- **Traceability:** HLR-006
- **Ledger:** LED-2026-10-08-data-safety-batch.2
- **Statement:** The draft shall be keyed by schema keys plus the pseudo-keys `title`, `notes` and `state`.
- **Validation:** `inspection`
- **Executed verification:** inspect the draft's key set against `FichaInspector._commit`'s field mapping (`inspector.py:357-364`, `title`/`notes`/schema-key) and `on_ds_segmented_changed`'s `state` (`:367-373`); the observable condition is that every editable surface has a draft key.
- **Numeric pass threshold:** every editable field (`title`, `notes`, each schema key, `state`) has a draft key.
- **Negative control:** none — inspection (structural review).
- **Boundary catalog:** none — inspection.

### LLR-007.1 — the doubled-`?` node realises AT-044
- **Traceability:** HLR-007
- **Ledger:** LED-2026-10-08-data-safety-batch.7, LED-2026-10-08-data-safety-batch.53
- **Statement:** A test node shall press `question_mark` twice from a map and assert the screen stack does not grow.
- **Validation:** `test (e2e)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_double_question_mark.py` (provisional; the file is `NEW — created in Phase 3`, placed in its own file per the ARQ §5 re-cut).
- **Numeric pass threshold:** exit code 0; `len(app.screen_stack)` is unchanged after the second `?`.
- **Negative control:** the assertion holds today (grep `doubled` in `tests/` → 0 hits, so the node is new coverage, not a fix — P-2); the mutation the node must redden on is binding `?` in the help seat (or letting the help legend inherit the app chord), which opens a second legend. Executed RED owed at Phase 3.
- **Boundary catalog:** ☑ empty — a single `?` opens exactly one legend; ☑ boundary — a second `?` with the legend already up; ☐ invalid ☐ error.

### LLR-007.2 — AT-025b reconciles to the `LLR-N13.1.5` nodes
- **Traceability:** HLR-007
- **Ledger:** LED-2026-10-08-data-safety-batch.7
- **Statement:** AT-025b shall be reconciled to the existing `LLR-N13.1.5` nodes (`tests/test_repair_cycles.py:501,543,575,624,664`) with no new node.
- **Validation:** `inspection`
- **Executed verification:** the nodes exist and assert the damaged-card declaration (`tests/test_repair_cycles.py:501,543,575,624,664`); the reconciliation is a mapping recorded in `.dev-flow/BACKLOG.md` and the traceability matrix.
- **Numeric pass threshold:** AT-025b resolves to ≥1 of those nodes by id in the Atlas.
- **Negative control:** none — the behaviour is already green under `LLR-N13.1.5` (P-3); a reconciliation of an existing id to an existing node has no executed RED side (declared).
- **Boundary catalog:** none — inspection.

### LLR-008.1 — AT-041 and AT-042's largest-set arm reconcile to their on-disk nodes
- **Traceability:** HLR-008
- **Ledger:** LED-2026-10-08-data-safety-batch.7, LED-2026-10-08-data-safety-batch.13, LED-2026-10-08-data-safety-batch.28
- **Statement:** AT-041 shall be reconciled to its on-disk node `tests/test_repair_layout.py:274` (`test_at_r12_pressing_help_presents_every_map_binding`). AT-042's largest-set arm (`map`, 27 rows) shall be reconciled to `tests/test_repair_layout.py:441` (`test_tc_r25_the_presented_set_equals_the_keymap_set_in_both_directions`, parametrised `SCOPE_MAP` and `SCOPE_HOME`). The two missing arms of AT-042 — the smallest-set arm (`app`, 2 rows) and the screen-that-declares-no-scope arm — have no on-disk node and are realised as new nodes under LLR-008.3.
- **Validation:** `inspection`
- **Executed verification:** the nodes exist at the cited lines (verified by grep, 2026-10-08); `test_tc_r25` is parametrised `SCOPE_MAP`/`SCOPE_HOME` only (no `app` arm, `tests/test_repair_layout.py:440`) and `test_tc_r26` asserts the foreign-scope negative (`:456`), so neither covers AT-042's smallest-set or no-scope arm; the reconciliation is recorded in `.dev-flow/BACKLOG.md` and the traceability matrix.
- **Numeric pass threshold:** AT-041 resolves to a cited node by id in the Atlas; AT-042's largest-set arm resolves to a cited node by id.
- **Negative control:** none — inspection; a reconciliation of an existing id to an existing node has no executed RED side.
- **Boundary catalog:** none — inspection.

### LLR-008.3 — AT-042's smallest-set and no-scope-screen arms are new nodes
- **Traceability:** HLR-008
- **Ledger:** LED-2026-10-08-data-safety-batch.28, LED-2026-10-08-data-safety-batch.51
- **Statement:** Two new test nodes shall realise AT-042's missing arms: one driving the smallest set (app scope, 2 rows) through the keymap set equality, and one driving a screen that declares no scope. The no-scope screen falls through the `HelpScreen` default (`scope=SCOPE_APP`, `mapper/screens/help.py:288`), so its presented set is `bindings_for(SCOPE_APP)` — the same 2 rows (`ctrl+p` palette, `?` legend) as the smallest-set arm; the two arms differ only by the constructor path (no scope argument vs the explicit `SCOPE_APP`), not by a different expected set. Verified by probe: `bindings_for('app')` = 2 rows (2026-10-08). Each node asserts the presented set equals the keymap set in both directions.
- **Validation:** `test (e2e)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_repair_layout.py -k tc_r25` (provisional until the two parametrised arms are added to `test_tc_r25`, `tests/test_repair_layout.py:441`).
- **Numeric pass threshold:** exit code 0; the `app` (2-row) arm and the no-scope-screen arm each pass.
- **Negative control:** the two arms go RED today only as absent nodes (no `app` arm exists in `test_tc_r25`, `tests/test_repair_layout.py:440`); the behaviour holds (P-2), so the arms are new coverage, not a fix. Executed RED owed at Phase 3.
- **Boundary catalog:** ☑ empty — a scope whose `bindings_for` returns nothing presents no rows (unreached by any shipped screen: the no-scope screen still presents the app's 2 rows); ☑ boundary — the smallest set (`app`, 2 rows) against the largest (`map`, 27 rows); ☐ invalid ☐ error.

### LLR-008.2 — AT-033/034/035 are retired
- **Traceability:** HLR-008
- **Ledger:** LED-2026-10-08-data-safety-batch.7
- **Statement:** AT-033, AT-034 and AT-035 shall be retired with a ledger entry, travelling with the deferred US-N14 (`#D23`).
- **Validation:** `inspection`
- **Executed verification:** the canonical attribution `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md:6089-6090` assigns the three ids to US-N14 (deferred); the retirement is recorded in `.dev-flow/BACKLOG.md`.
- **Numeric pass threshold:** the three ids carry no obligation in this batch's Atlas.
- **Negative control:** none — inspection; the ids are absent from `tests/` by design (US-N14 deferred), not by defect.
- **Boundary catalog:** none — inspection.

### LLR-009.1 — the four `scroll_to` sites are immediate and settled
- **Traceability:** HLR-009
- **Ledger:** none
- **Statement:** The four `scroll_to(..., animate=False)` call sites (`tests/test_help_scope.py:93`, `:365`; `tests/test_en7.py:246`; `tests/test_repair_layout.py:118`) shall pass `immediate=True` and assert the settled scroll offset before sampling.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_help_scope.py::test_hlr_n16_4_legend_declares_its_own_keys tests/test_en7.py::test_the_painted_legend_ends_with_the_rule tests/test_repair_layout.py` (reconciled from the real tree at Phase 4).
- **Numeric pass threshold:** exit code 0; the settle assertion holds and the own-keys test passes under the injected-delay fixture.
- **Negative control:** AT-008's RED side is the current code — the spike's `red_green_flake2.py` fails 2/2 on the current step and passes 2/2 with `immediate=True` (spike, 2026-10-08).
- **Boundary catalog:** ☑ empty — the pane already at the target offset; ☑ boundary — the mid-range position `max_scroll_y // 2` the fixture delays; ☐ invalid ☑ error — a scroll that never lands (the settle assertion fails loud).

### LLR-009.2 — the injected-delay regression arm
- **Traceability:** HLR-009
- **Ledger:** LED-2026-10-08-data-safety-batch.53
- **Statement:** A regression arm shall apply the spike's late-landing fixture and run the own-keys loop, passing with `immediate=True` and a settle assertion.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_help_scope.py -k n16_4` (provisional until Phase 3; the fixture is `NEW — created in Phase 3`, adapted from `spike/red_green_flake2.py`).
- **Numeric pass threshold:** exit code 0; the committed arm is GREEN, and its RED is the executed counterfactual `spike/red_green_flake2.py` (2/2 on the current step), not a second run of the same committed node — one committed node cannot be both RED and GREEN.
- **Negative control:** the fixture delays only the test's own positioning `_scroll_to` call, emulating load; the counterfactual `spike/red_green_flake2.py` fails 2/2 on the current step (spike §4, 2026-10-08) and passes 2/2 with `immediate=True`.
- **Boundary catalog:** ☑ empty — the fixture with the pane at the target offset; ☑ boundary — the delayed mid-range call; ☐ invalid ☐ error.

### Information Flow Contract (IFC) — C-54

> Part A in every batch; Part B when the system's boundary has components a consumer can address independently. The block syntax, its fields and the rules that read them are in `templates/ifc-template.md`, which ships with the flow and is not copied into this batch.

- **Part A — flows:**

```
FLOW: draft_save
  SOURCE : operator keystroke / `state` segment change in a focused inspector field
  NODES  :
    - fn    : FichaInspector.on_input_submitted / on_input_blurred → draft update
      owner : LLR-001.2
      in    : Input widget value + node_id
      out   : per-node draft {field: value}
    - fn    : FichaInspector.on_ds_segmented_changed → draft["state"]
      owner : LLR-006.1
      in    : DsSegmented.Changed index
      out   : draft["state"]
    - fn    : FichaInspector._rows → dirty markers + header overlay
      owner : LLR-002.1
      in    : draft + shown values (darkside.plain(stored))
      out   : painted rows (per-field marker, ● unsaved (N))
    - fn    : MapScreen.action_save_draft → pull + apply
      owner : LLR-001.4
      in    : inspector.draft_values()
      out   : graph fields mutated via darkside.plain
    - fn    : MapScreen._push_snapshot + store.save (disk-classified on failure) → store.save
      owner : LLR-004.1
      in    : graph
      out   : one undo snapshot + one on-disk write
  SINK   : mapper map `.mmd` + `_nodos.yml` on disk (whole-graph write)
```

- **Part B — boundary decomposition:** yes — the inspector form is a UI surface whose fields a consumer (a test) addresses independently by widget id, and the guard modal is dismissed with one of three addressable string tokens.

```
COMPONENT: inspector_form
  PARENT : SYSTEM
  SURFACE: MapScreen inspector panel (variant A «taller»)
  INPUTS : node: Node|None ; schema: list[SchemaField]
  OUTPUTS:
    - id          : field_inputs
      value       : one editable surface per ficha value, shown via darkside.plain(stored)
      address     : widget ids #insp-title, #insp-field-{key}, #insp-notes, #insp-state
      cardinality : 3 + len(schema)
      consumers   : mapper/app.py
                    tests/test_inspector.py
                    tests/test_g6_store_surrogates.py
                    tests/test_worklist_safety.py
      owner       : LLR-002.1
    - id          : unsaved_header
      value       : "● unsaved (N)" count in the inspector header
      address     : #insp-header
      cardinality : 1
      consumers   : tests/test_inspector.py
      owner       : LLR-002.2
    - id          : draft_surface
      value       : draft_node_id / draft_values() / has_draft() / clear_draft()
      address     : FichaInspector.draft_values ; FichaInspector.has_draft ; FichaInspector.clear_draft ; FichaInspector.draft_node_id
      consumers   : mapper/app.py::MapScreen
      owner       : LLR-001.1
```

```
COMPONENT: draft_guard
  PARENT : SYSTEM
  SURFACE: save · discard · stay modal (DraftGuardScreen)
  INPUTS : title: str
  OUTPUTS:
    - id          : choice
      value       : exactly one of "save" | "discard" | "stay"
      address     : DraftGuardScreen dismissal value (ModalScreen[str])
      cardinality : 1
      consumers   : mapper/app.py::MapScreen ; mapper/app.py::MapperApp.action_quit
      owner       : LLR-003.1
```

> **IFC consumers created in Phase 3** (`tests/test_draft_save.py`, `MapScreen.action_save_draft`, the exit guards) are added to the consumer lists in the increment that creates them; until then each output names the existing file that will host them (validator `V14` resolves consumers against today's tree).
>
> **IFC note.** `address` on `field_inputs` is a family of widget-id literals (`#insp-title`, `#insp-field-{key}`, `#insp-notes`, `#insp-state`); `{key}` is a schema-key interpolation, so the set is bounded by the schema and is a COMPUTED-address site. The `draft_surface` and `draft_guard` addresses name code symbols and a token set that a literal grep cannot follow; they are recorded for human comparison against the surface, per `ifc-template.md` §3 limb 3. The two `NEW — created in Phase 3` consumers do not exist on disk at draft time and are owed when the increment that mints them lands.

---

## 5. Validation strategy

### 5.1 Methods

> **Two layers** (per the Two-layer validation rule). Every batch declares BOTH:
> - **Layer A — white-box / functional (`TC-NNN`):** validates the HLR/LLR mechanism (the HOW). Methods: `test`, `inspection`, `analysis`.
> - **Layer B — black-box / behavioral acceptance (`AT-NNN`):** validates the user story's outcome through the shipped surface (the WHAT). Method: `acceptance`.

> **Observation method (`obs`) — stated once, referenced by every AT:** each AT is observed through a Textual `App.run_test` pilot that presses the real keys (typing, `ctrl+s`, `↵`, `q`/`esc`, `ctrl+q`, the guard's `s`/`d`/`esc`), never through posted messages or direct setters; the map's `.mmd` and `_nodos.yml` are hashed (sha256) before and after the scenario; "written once" = the hash pair changes exactly once across the scenario. Failing-store arms inject the failure by monkeypatching the screen's store `save` to raise after writing after writing zero or both files (AT-002a, a declared Layer-A fault-injection seam).

| Requirement | Layer | Method | Verification |
|---|---|---|---|
| HLR-001…006 (US-001) | A | `test` (unit/integration) | LLR-001.x…LLR-006.x, each with an executed verification and a numeric threshold |
| HLR-001…006 (US-001) | B | acceptance | AT-001…AT-007, AT-009…AT-015 (with AT-005a/005b, AT-014a–014d split per key); AT-002a and AT-013 are declared Layer-A injection tests and are verified under Layer A through the shipped inspector surface and the `.mmd`/`_nodos.yml` files (`obs`) |
| HLR-007 (US-002) | A + B | `test` (e2e) + `inspection` | LLR-007.1 (new AT-044 node) + LLR-007.2 (reconcile AT-025b); AT-044, AT-025b |
| HLR-008 (US-003) | A | `inspection` + `test` (e2e) | LLR-008.1/008.2 reconcile/retire ids (inspection); LLR-008.3 mints AT-042's two new arms (test); AT-041 reconciled, AT-042's largest-set arm reconciled + two arms owed, AT-033/034/035 retired |
| HLR-009 (US-004) | A + B | `test` (integration) | LLR-009.1/009.2 deflake + injected-delay regression; AT-008 |

- **Layer A default:** every LLR validated by `test`/`analysis` names its exact executed verification (a pytest node id) and a numeric pass threshold; `inspection` LLRs name the file/line and the observable condition.
- **Layer B:** every user story has ≥1 `AT-NNN` observing its outcome through the shipped surface — with the exception of US-003, whose acceptance is definitional/inspectional (a reconciliation of ids to nodes, no shipped surface), as declared in its refinement block; and US-004, whose AT-008 accepts the determinism of the test instrument rather than product behaviour (a test-instrument check, not a shipped surface).

> **Out-of-LLR regression obligations (Inc-1):** (a) the reverse-census re-point of the three test files that post `FieldCommitted` — `tests/test_inspector.py:103,162`, `tests/test_g6_store_surrogates.py:133,152,176`, `tests/test_worklist_safety.py:254` — re-pointed to drive typing + `ctrl+s` through the pilot (never a posted message), including `tests/test_g6_store_surrogates.py:150,203,331`; (b) the whole-seat pin `tests/test_key_dispatch.py:137` (`test_at_n03h_the_whole_seat_matches_its_specification`), which must absorb the new map-scope `ctrl+s` row and the `draft` scope; (c) the keymap census pins `tests/test_keymap.py:34-44,63,87-95,298` and `tests/test_inc9.py:695-703,707`, which the new keymap symbols (`SCOPE_DRAFT = "draft"`, `GROUP_SCOPE["draft"] = SCOPE_DRAFT`, `MODAL_SCOPES` widened, the map-scope `ctrl+s` row) redden; and (d) the ARQ D2 persistence-oracle census candidates `tests/test_en7.py:62-80,182`, `tests/test_app.py:31`, `tests/test_fold.py:1016,1253`, `tests/test_inc9d.py:124-487` (`↵` on inspector fields), whose "type, `↵`/blur, file changed" oracles the draft model re-points. All are owed in Inc-1 as regression obligations, not as new LLRs.

### 5.2 Batch acceptance criteria
- 100% of LLRs have an assigned validation method; every `test`/`analysis` LLR carries an executed verification and a numeric pass threshold.
- Every user story has ≥1 black-box `AT-NNN` (US-003's is inspectional by declared exception), with boundary + negative evidence.
- 0 blocker fails; no requirement names a symbol, constant or check that is neither verified nor flagged `NEW`/`assumed`.
- US-004's four `scroll_to` sites carry `immediate=True` + a settle assertion, and the injected-delay regression arm is RED before the fix and GREEN after.
- The whole-branch gate is green with FLAKE-2 fixed first (merit order Inc-3), so the instrument the gate runs is honest.
- Dual traceability holds: every HLR traces to a US, every LLR to a parent HLR, and both chains (`US → AT → outcome`, `US → HLR → LLR → TC`) are complete, as derived by `V10`/`V21` into the Atlas.

---

## 6. Appendices (optional)

### 6.1 Extended glossary
- **Whole-graph write** — `MapStore.save(map_id, graph)` persists the entire graph plus its sidecar in one call; there is no field-level write path.
- **Seat** — `mapper/keymap.py`, the single keymap source read by the keybar, the legend, the palette and the screen `BINDINGS`.

### 6.2 Relevant design decisions
- R-012 — the draft lives in `FichaInspector` (`widgets`), not `MapScreen` and not a new module (ARQ §D1).
- R-013 — `FieldCommitted` is removed, not reshaped; `MapScreen` pulls the draft synchronously (ARQ §D2).
- R-014 — the guard modal is `mapper/screens/draft_guard.py` (ARQ §D3).

### 6.3 Open risks

- **Security scan (`devflow-scan-spec.py`): the P0 scan (2026-10-08) flagged `escape`; the P1 scan (re-run 2026-10-08, rule 7) exit 1 → `security_required: true`, flagged `token`, `form`, `escape`; the P1-iteration-1 scan (re-run 2026-10-08) flags `token`, `hash`, `form`, `escape`.** All four are ordinary vocabulary, recorded anyway and declared per C-53, never reworded: `token` is the guard modal's dismissal token (`save`/`discard`/`stay`, LLR-003.1) and the `draft_guard` `choice` output; `hash` is the sha256 observation method (§5.1 `obs` — the `.mmd`/`_nodos.yml` hash pair); `form` is the inspector form / "the value the form showed" (HLR-002, LLR-002.1, §1.3); `escape` is the Esc key of the guard (`esc` stay), the legend seat, and the ESC-payload negative (AT-015). None names a sensitive surface. The batch's security questions: (1) US-001 changes WHEN the inspector writes the map and its sidecar — the write path must stay a two-phase whole-graph write with torn-pair detection, and confined (B-75 check-then-write, `MapStore._write_tmp` hard-link B-84 are adjacent, not in scope); (2) no new parser, network or secret surface. The `security-reviewer` lens runs at PDR over US-001's write path.
- **US-001 depends on an operator verdict** on a prototype round (standing rule 2026-09-04); P0 stays open for US-001 until it arrives — delivered 2026-10-08 ("C").
- **A-8** (a base `on_*` handler survives and double-commits): the change is in-place, no subclass; the sha256 AT on `.mmd` + `_nodos.yml` reddens a surviving base handler.
- **A-9** (the draft is wiped by the per-repaint rebuild): overlay in `_rows` and guard at `app.py:3281`.
- **A-10** (a failed save leaves drafted values in `self.graph`): every failure reloads the map from disk, or restores the pre-save graph in memory when the reload raises (LLR-004.2), so no drafted value survives in `self.graph` for a later structural save to persist, and failure handling never writes.
- **A-11** (a killed terminal or crash while a draft is pending): not an exit — loss is accepted by design (R1, the draft is never persisted on its own) and nothing is written. Excluded explicitly, not mitigated.
- **A-12** (the modal paints a file-derived title): title composed of `darkside.plain(map_id)` + `darkside.plain(node title)` with `markup=False` (LLR-003.1); `plain()` strips the control characters (ESC included) that `markup=False`'s content strip leaves in.
- **A-13** (a typed-ahead `d` while the guard is up): the discard is accepted as a residual — it loses a draft but never writes (R2-minors; recorded, not mitigated).
- **A-14** (a save whose files reached disk but whose store call raised, e.g. inside `_reindex`): the reload shows the edit as clean, but no undo step exists for it — accepted under the operator's ruling (failure handling never pushes or writes); recorded, not mitigated.
- **A-15** (the store's `_reindex` fails on save and again on reload): the pre-save graph is restored in memory while disk holds the edit; the error toast tells the operator to leave and reopen the map, and a structural write before reopening would revert disk — accepted as a residual of a double index failure; recorded, not mitigated.

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
```
