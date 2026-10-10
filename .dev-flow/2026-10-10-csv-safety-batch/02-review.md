# Review — mapper — Batch 2026-10-10-csv-safety-batch

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`).
> Phase 2 artifact. Reviewers (in parallel): `architect` ∥ `qa-reviewer` ∥ `security-reviewer` by trigger family C (always in `full`).

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/guides/review-template.md` explains each field below and the rules that read them. It ships with the flow and is not copied into this batch.

## ✅ Verdict (read first)

- **Gate:**
  - **Round 1** → `iterate-to-refine` → Phase 1 (5 blockers).
  - **Round 2** → `approve-with-conditions` on both artifacts (architect + qa-reviewer) → PDR with conditions, after the round-2 rulings R11–R16 were applied in this unit (ledger `LED-2026-10-10-csv-safety-batch.5`…`.10`) and the PDR was sealed.
- **Out-of-scope findings:** 2 named and routed below (B-115, B-116); plus the pre-existing
  O(N·E) orphan pass (`mapper/import_csv.py:101`) remains the design §6 watch-item already recorded — no new row.

- **Findings (round 1):** 5 blocker · 11 major · 8 minor (24 total). Both reviewers were
  read-only; the architect ran probes on temp workspaces. The orchestrator ruled R1–R10
  (table below); Kimi applied them in P1 iteration 1 (ledger `LED-2026-10-10-csv-safety-batch.2`…`.4`).
- **shall/should check:** ✓ clean (round 1) — `shall` appears in Statements only; no modal `should` in any HLR/LLR statement.
- **Two-layer (blockers):** ✗ in round 1:
  - AT-072's no-write oracle was undefined and ignored `mapper.db` / `*.tmp` (qa Q2).
  - AT-072…074's drive path cited a direct `action_save()` call, not the real import flow (qa Q3) — not genuinely black-box per (d).
  - Negative controls were not stated per layer (qa Q5).
  - Every story has an AT, both trace chains complete — unchanged.
- **Census (change-first):** done best-effort by the architect (§B of the transcript: every save
  entry point checked, `csv_collisions` does not leak through sidecar/undo/focus/deepcopy) — ⚠ the
  "no existing test breaks" claim is unproven until the P3 full-suite gate runs (qa QB3).
- **Security:** no security-reviewer findings in round 1. Family C fired (C6 input surface, C8
  painted operator ids); C8 stays enforced by LLR-CSV.2.2's `darkside.plain` routing.
- **Evidence checklists (architect / qa):** summarized below from the reviewers' transcriptions.

---

## Detail (reference)

### Findings — round 1

Reviewer ids follow the orchestrator's transcription of the round-1 review
(`CSV-review-r1.md`, held in the orchestrator's temp area, not committed): architect
requirements `A1`–`A6`,

| ID | Reviewer | Severity | Area / Req | What | Recommendation / ruling | Status |
|----|----------|----------|------------|------|------------------------|--------|
| A1 | architect | blocker | LLR-CSV.2.2, HLR-CSV.2 | A collision that violates no loader rule still loses a row silently: two rows slug to the same id, both with empty parent — `import_csv.py:73` overwrites, save and reload succeed, first row gone. LLR-CSV.2.2 paints only "whenever the preview graph violates a loader invariant" ⇒ nothing painted; US-CSV-002 unmet. | **R1:** any non-empty `Graph.csv_collisions` alone paints the collision sentence (precedence first) and makes `action_save` refuse via the existing toast, whether or not a loader rule is violated. | applied in iteration 1 |
| A2 | architect | blocker | HLR-CSV.2, boundary catalog | The root-collision fixture is a CYCLE, not multi-parent (probe: `multi_parent=[]`, `find_cycle=['a-b','c','a-b']`, save says "the map has a cycle"; the orphan loop `import_csv.py:97-102` closes it). LLR-CSV.1.1's threshold unsatisfiable as written; HLR-CSV.2 needs a precedence rule. | **R3:** reclassify the fixture as a cycle case; precedence collision > multi-parent > cycle. | applied |
| A3 | architect | major | HLR-CSV.2 (cycle sentence) | `slugify("")` returns `"n"` (`mermaid.py:51`), so an empty parent slugifies to `n`: every top-level row points at node `n`, ids `!!!`/`???` both → `n`, a valid CSV whose root id is `N` becomes a self-cycle n→n, top-level rows get the `? ` parked prefix; the cycle sentence wrongly blames "the parent column". | **R4:** the empty-slug family → backlog **B-115**. **R3:** the cycle sentence is reworded neutral ("the import builds a cycle"), not blaming the parent column. | applied / routed |
| A4 | architect | major | HLR-CSV.1, LLR-CSV.1.1 | Unsupported-syntax refusal (`mermaid.py:108`) IS reachable from a Graph: a title with `\n` dumps to an unparsable `.mmd` (verified). Also an orphan node titled `a --> b` re-parses as a spurious edge — silent corruption (verified). HLR-CSV.1 says "any graph that violates a loader invariant". | **R2:** the store check becomes a round trip — refuse when `mermaid.parse(mermaid.dump(G))` raises OR yields a different structure. | applied |
| A5 | architect | minor | LLR-CSV.1.1 | Rule I1 counts edges; `dump` drops exact duplicate edges (`mermaid.py:148` region) and the reparse succeeds — a same-parent collision saves and loses a row today. Refusing it is right: declare it an intended superset of the loader. | **R2:** covered by the round-trip check; declared an intended superset in HLR-CSV.1's rationale. | applied |
| A6 | architect | minor | CSV import order | A CSV listing a child before its root is refused as a cycle because the first row becomes the root (`import_csv.py:98`) — pre-existing. | **R4:** out of scope → backlog **B-116** (define row order or fix). | routed |
| B1 | architect | major | proposal §2a | The claim that refusals 1 and 4–8 cannot be violated by a `Graph` is false for refusal 1 (see A4). | **R10:** §2a corrected — refusal 1 is reachable from a Graph. | applied |
| B2 | architect | major | proposal §4 (import-preview row) | Which sentence wins when several predicates fire: key the branch on `csv_collisions` first; keep the "could not draw the preview" header pinned by `test_tc_r08b`. | **R3/R10:** precedence collision > multi-parent > cycle; header kept; header + sentence asserted together (QB4). | applied |
| B3 | architect | minor | PLAN.md, `01-requirements.md` §4 IFC | PLAN.md increment 1 and the interface owners name only `store.py`; the design also touches `mapper/model.py`; the new field changes `Graph.__eq__`; `ARCHITECTURE.md` §4 `Graph` row amendment is owed at close. | **R10:** increment 1 names `mapper/model.py` + `mapper/store.py`; `csv_collisions` is `compare=False, repr=False`; ARCHITECTURE amendment recorded as owed at close. | applied |
| Q1 | qa-reviewer | blocker | LLR-CSV.1.1, LLR-CSV.2.2 | A slug collision does not always produce a multi-parent node (`import_csv.py:57-73,101`): two colliding rows with no parent column (incl. the auto-id fixture), or one with a parent and one without ⇒ `multi_parent_ids()` empty ⇒ preview draws normally, row silently lost. LLR-CSV.1.1 lists the auto-id collision among must-raise fixtures — a contradiction. | **R1:** keyed on `csv_collisions`, not on `multi_parent_ids()`; new boundary items + tests for each collision shape. | applied |
| Q2 | qa-reviewer | blocker | AT-072, LLR-CSV.1.2 | "Empty workspace" is wrong — `mapper.db` always exists (`store.py:392`) and a save may leave `*.tmp`; the no-write oracle is undefined. | **R6:** sha256 snapshot of every file in the workspace dir (`iterdir()`, recursive, incl. `mapper.db` and `*.tmp`) before/after; file set and every digest unchanged; no sidecar appeared. Same oracle at store level. | applied |
| Q3 | qa-reviewer | major | AT-072…074, §5.1 | The drive path was cited wrongly — `tests/test_seed_safety.py:107-117` `_open_import` drives `i`, path, enter, `s`, name, enter through the home screen; §5.1 cited `test_g6_store_surrogates.py:555-600`, which pushes the screen and calls `action_save()` directly. | **R5:** AT-072…074 use `_open_import`. | applied |
| Q4 | qa-reviewer | major | LLR-CSV.2.1 | "1-based line number" is undefined for blank rows / CRLF. | **R7:** line numbers come from `csv.DictReader.line_num`; fixtures include a blank line and a CRLF file; the evidence CSV's rows are 5 and 6. | applied |
| Q5 | qa-reviewer | major | negative controls | Controls are mixed — mutation M2 reddens AT-073 but AT-072 stays green; not stated per layer. | **R8:** each layer names the test that reddens when ONLY its check is removed. | applied |
| Q6 | qa-reviewer | major | M1b, LLR-CSV.1.2 | M1b bites only if the fixture overwrites an existing map — say so. | **R6:** M1b's fixture explicitly overwrites an existing map, so a check moved after any write turns RED. | applied |
| Q7 | qa-reviewer | minor | HLR-CSV.2 | The three-way list grammar is unpinned. | **R9:** pinned to exactly `rows 2, 3 and 4` (no Oxford comma) in the sentence template. | applied |
| Q8 | qa-reviewer | minor | HLR-CSV.2 boundary | Mapping incomplete — the empty-CSV panel (root None) is untested; self-parent via the parent column is not under HLR-CSV.2. | **R9:** both added to the boundary catalog with fixtures. | applied |
| Q9 | qa-reviewer | minor | `01-requirements.md` ~:134 | Typo `` `READY`. `` (stray period after the code span, inconsistent with the other classification lines). | **R9:** fixed. | applied |
| QB1 | qa-reviewer | blocker | proposal §5 | Same gap as Q1 — §5 names only multi-parent fixtures; the `refresh_canvas` branch is predicate-only. | **R1:** the preview branch keys on `csv_collisions` first; new tests for each collision shape. | applied |
| QB2 | qa-reviewer | major | proposal §5, AT-072 | The AT-072 oracle is weak (as Q2). | **R6:** same sha256 oracle. | applied |
| QB3 | qa-reviewer | major | proposal §6 | "No existing test breaks" is plausible but unproven (spot-checked `_diamond`, `test_tc_r08b`, trees in `test_legend_design.py` / `test_repair_depth.py` / `test_search.py`, `test_pan.py:173`). | **R10:** not claimed — verified by the P3 full-suite gate. | applied |
| QB4 | qa-reviewer | major | proposal §5, AT-073 | Assert the panel header and the sentence together for the collision case. | **R10:** AT-073 asserts "could not draw the preview" AND the sentence. | applied |
| QB5 | qa-reviewer | minor | `import_csv.py:101` | The O(N·E) orphan pass → backlog is fine. | Kept as the design §6 watch-item (pre-existing; no new row this round). | recorded |
| QB6 | qa-reviewer | minor | proposal §4 (`Graph` row) | The new dataclass field affects `Graph ==` / repr. | **R10:** `field(default_factory=list, compare=False, repr=False)`. | applied |

**Verified sound by the architect (probed on temp workspaces):** no partial write
(`store.py:822-850` validates, dumps, writes two temp files, replaces, reindexes); traceability
complete; every save entry point checked (`import_preview.py:88`, `factory.py:217`,
`map/editing.py:51,77,124,147`, `undo.py:64`, `drafts.py:141`; `store.create` builds trees;
`add_child` makes unique ids; no reparent action; `github.py` never saves) — the new refusal
breaks no legitimate path; `csv_collisions` does not leak (`_build_sidecar` serializes named
fields; undo via dump+yaml; `focus()` drops it; deepcopy copies a loaded graph); the G6-C-F4
pattern's ATs genuinely drive the real app.

### Orchestrator rulings R1–R10 (round 1 → P1 iteration 1)

| Ruling | Answers findings | Disposition |
|--------|------------------|-------------|
| R1 — any collision blocks: non-empty `csv_collisions` alone paints the collision sentence (precedence over multi-parent and cycle) and makes `action_save` refuse via the existing toast without writing — whether or not a loader rule is violated (two parentless rows / one parented + one not / auto-id). New boundary items + tests. | A1, Q1, QB1 | applied (`LLR-CSV.2.3` new; tests `test_at_072b/c/d_*`) |
| R2 — the store check is a round trip: refuse, before any byte, when `mermaid.parse(mermaid.dump(G))` raises OR yields a different structure (node-id set, edge set as (parent, child) pairs, root). Covers multi-parent, cycle, unsupported syntax (newline title), `-->` title re-parsing as a spurious edge, duplicate edges dropped by `dump` (intended superset). `Graph.multi_parent_ids()` kept — the preview's multi-parent sentence still needs it. Reason names the rule in plain language. O(N+E) plus one dump/parse. HLR-CSV.1 scoped to "every graph whose saved form would not load back as the same graph". | A4, A5 | applied (HLR-CSV.1, LLR-CSV.1.1, §2a) |
| R3 — the cycle sentence is neutral (no "the parent column"); root-collision fixture reclassified as a cycle case; precedence collision > multi-parent > cycle. | A2, A3 | applied (HLR-CSV.2, LLR-CSV.2.2, boundary catalog) |
| R4 — out of scope, to backlog: `slugify("") == "n"` family → **B-115**; child-before-root refused as a cycle → **B-116**. | A3, A6 | routed (BACKLOG.md) |
| R5 — AT drive path is `_open_import` (`tests/test_seed_safety.py:107-117`: `i`, path, enter, `s`, name, enter from the home screen). | Q3 | applied (§5.1, HLR-CSV.3) |
| R6 — the no-write oracle: sha256 snapshot of every file in the workspace dir (`iterdir()`, recursive, incl. `mapper.db` and `*.tmp`) before/after the refused save; file set + digests unchanged; no `_nodos.yml`/`.mmd` appeared. Same oracle at store level (LLR-CSV.1.2); M1b's fixture overwrites an existing map. | Q2, QB2, Q6 | applied (HLR-CSV.1, LLR-CSV.1.2, proposal §5) |
| R7 — line numbers from `csv.DictReader.line_num`; fixtures include a blank line and a CRLF file; the evidence CSV's rows are 5 and 6. | Q4 | applied (HLR-CSV.2, LLR-CSV.2.1) |
| R8 — negative controls per layer: store-check-only removal reddens `test_save_refuses_*` + AT-072; preview record/branch-only removal reddens AT-073 (AT-072 stays green). | Q5 | applied (per-requirement Negative control fields) |
| R9 — grammar pinned: three-way example exactly `rows 2, 3 and 4` (no Oxford comma); boundary additions: empty CSV panel (root None), self-parent via the parent column; typo `` `READY`. `` fixed. | Q7, Q8, Q9 | applied |
| R10 — `csv_collisions` is `field(default_factory=list, compare=False, repr=False)`; PLAN.md and the interface owners name `mapper/model.py` in increment 1; §2a's refusal-1 claim corrected; the panel keeps its header, asserted together with the sentence; "no existing test breaks" verified by the P3 full-suite gate, not claimed; `ARCHITECTURE.md` §4 `Graph` row amendment owed at close. | B1, B2, B3, QB3, QB4, QB6 | applied |

### shall / should check
Clean (round 1): `shall` in Statements only; no modal `should`/`debería` inside any HLR/LLR statement.

### Two-layer acceptance review (blockers)

| Story / Req | (a) AT present | (b) deliverable+method named | (c) both chains | (d) black-box pure | Status |
|-------------|----------------|------------------------------|-----------------|--------------------|--------|
| US-CSV-001 / HLR-CSV.1 | yes | yes | yes | no in round 1 — AT-072's oracle undefined (Q2) | blocker (Q2) → fixed by R6 |
| US-CSV-002 / HLR-CSV.2 | yes | yes | yes | no in round 1 — drive path cited a direct `action_save()` call (Q3); collision-without-violation unpainted (A1/Q1) | blocker (Q3, A1) → fixed by R1, R5 |
| US-CSV-003 / HLR-CSV.3 | yes | yes | yes | no in round 1 — same drive path (Q3) | major (Q3) → fixed by R5 |

### Supersession census (change-first)
Best-effort census executed by the architect (§B of the transcription): every save entry point,
every `csv_collisions` leak path, every `preview_csv` caller (8 direct test callers + home) checked —
no legitimate path breaks. Reservations: the spot checks do NOT prove the whole suite stays green —
**the P3 full-suite gate is the guarantee** (QB3, ruling R10). The increment gate must confirm the
two new test files plus the re-run pins (`test_repair_cycles.py` `test_tc_r08b`, G6 toast-wording
nodes, `test_import_csv.py`, `test_mod_compat.py` F4 surface).

### Security review summary
No security-reviewer findings in round 1. Family C fired (C6 — the CSV file is an input surface;
C8 — the refusal sentence paints operator-supplied ids). C8 stays enforced by LLR-CSV.2.2: every
interpolated piece passes `darkside.plain`, styling from `mapper/darkside.py` tokens only; guard
A-110 (`tests/test_no_operator_paths.py`) must stay green at the P3 gate.

### Evidence checklists — architect · qa-reviewer

**architect (round 1):**
- ✓ constraints stated (loader frozen, no new UI, toast shows type only);
- ✓ defect reproduced on temp workspaces (A1 probe: colliding save+reload succeeds, first row gone; A2 probe: root-collision is a cycle; A4 probes: newline title unparsable, `a --> b` title re-parses as an edge);
- ✓ placement respected ARCHITECTURE §3 (predicate in `model`; no new dependency edges);
- ✗ refusal-1 claim in §2a (false — fixed by R10);
- ✗ increment-1 file set missing `mapper/model.py` (fixed by R10);
- ✓ no partial write confirmed (`store.py` two-phase write);
- ✓ `csv_collisions` leak census (sidecar / undo / focus / deepcopy) — no leak;
- ✓ alternatives table present and rejected for cause.

**qa-reviewer (round 1):**
- ✓ G/W/T shape of the proposed tests;
- ✗ no-write oracle undefined, ignored `mapper.db`/`*.tmp` (Q2 — fixed by R6);
- ✗ AT drive path not black-box (Q3 — fixed by R5);
- ✗ negative controls not per layer (Q5 — fixed by R8);
- ✗ boundary mapping incomplete: empty-CSV panel, self-parent (Q8 — fixed by R9);
- ✗ line-number semantics undefined for blank/CRLF (Q4 — fixed by R7);
- ✗ "no existing test breaks" unproven (QB3 — fixed by R10);
- ✓ no PII / operator-path surface beyond the C8-guarded ids;
- ✓ reachability of every refusal from a `Graph` argued (A4 corollary).

---

## Round 2

Reviewer ids follow the orchestrator's transcription of the round-2 review
(`CSV-review-r2.md`, held in the orchestrator's temp area, not committed): round-1
architect requirements `A1`–`A6` continue as `A7`; round-1 proposal findings `B1`–`B4`
continue as `B5`–`B6`; the qa-reviewer numbered its round-2 findings `1`–`7`. Both
reviewers were read-only; the architect probed on a temp workspace
(`scratchpad/probe/rt.py`, HEAD fbd9459). Round-1 items were confirmed resolved: A1
(LLR-CSV.2.3), A2 (cycle reclassified, precedence), A3/A6 (B-115/B-116), A4 (R2),
qa HIGH-1 (record-first preview), HIGH-2 (sha256 oracle incl. `mapper.db`/`*.tmp`),
ATs via `_open_import`, `line_num` blank/CRLF fixtures, the `rows 2, 3 and 4` grammar.

### Findings — round 2

| ID | Reviewer | Severity | Area / Req | What | Recommendation / ruling | Status |
|----|----------|----------|------------|------|------------------------|--------|
| A7 (= B4) | architect | high | round-trip check, HLR-CSV.1 / proposal §2a, §4 (`design-proposal.md:121-129,174`) | The round trip compares the root; `parse` makes the root the first parentless node in text order and `dump` writes all edges first, edgeless parentless nodes after (`mapper/mermaid.py:135-158`), so any forest (≥2 parentless nodes) changes root on reparse. Probe: legacy `a` / `b --> c` loads today with root `a`; the proposed check reports `root a->b` and refuses EVERY save of such a map (all save paths: `editing.py:51,77,124,147`, `undo.py:64`, `drafts.py:141`, `factory.py:217`) with no in-app repair. Trees are safe (child-first declared tree round-trips; the root is determined by the edge set). | **R11:** compare the node-id set and the edge set ((parent, child) pairs) only — NOT the root; the drift is pre-existing → backlog **B-117**; add a regression requirement + test: a legacy forest loads, is edited (a child added) and saves (new LLR-CSV.1.3, `test_save_accepts_legacy_forest_after_edit`, mutation M4). | applied (ledger .5; BACKLOG B-117) |
| B5 | architect | med | complexity, proposal §2a / LLR-CSV.1.1 | "O(N+E) plus one dump/parse" is wrong — `dump` is already O(N·E) (`mapper/mermaid.py:152-153`); nothing requires the check's `mmd_text` to be the text written (else `dump` runs twice per save). | **R12:** state the complexity honestly (`dump`'s parentless-node loop is O(N·E) — B-33 territory, not fixed here); require one `dump` per save — the check parses the exact text written; numeric threshold: the added parse costs ≤ 25 % of `MapStore.save` wall time for a 6 000-node wide tree, measured once at P4 (median of 3) as evidence — NOT a wall-clock suite assertion. | applied (ledger .6) |
| B6 | architect | low | LLR-CSV.2.3 wording | The preview refuses "through `_save_or_toast`", but that helper toasts only when `store.save` RAISES — a record-keyed refusal raises nothing. | **R15 (merged with qa 3):** the refusal emits its own toast at the call site, at the `s` keypress, before the prompt; pinned text + severity. | applied (ledger .9) |
| 1 | qa-reviewer | high | HLR-CSV.2 boundary vs LLR-CSV.2.2 / precedence | The root-collision expectation contradicts itself: HLR-CSV.2's boundary says the CYCLE sentence paints; LLR-CSV.2.2 and the precedence rule give the COLLISION sentence (the fixture's `csv_collisions` record is non-empty). | **R13:** fix the HLR-CSV.2 boundary text and the proposal §5 fixtures to agree — the preview paints the COLLISION sentence; the store-level refusal of that graph (it IS a cycle) remains a store unit case. | applied (ledger .7) |
| 2 | qa-reviewer | med | HLR-CSV.1 / LLR-CSV.1.1 negative controls, AT-072 | AT-072's negative control cannot go RED as claimed: its CSV has a non-empty record, so LLR-CSV.2.3 refuses before the store; removing the store check (M1) leaves AT-072 green; the toast shows the exception type only, so AT-072 cannot tell which layer refused. | **R14:** AT-072 is the PREVIEW-layer acceptance; its negative control is removing the preview refusal (record-keyed, M2c). The STORE layer's controls are its unit nodes only (M1, M1b). Correct HLR-CSV.1 / LLR-CSV.1.1 so no text claims M1 reddens AT-072. | applied (ledger .8) |
| 3 | qa-reviewer | med | LLR-CSV.2.3, `action_save` timing | WHEN `action_save` refuses is unpinned: at `s` (then `_open_import`'s typing into `#prompt-input` fails with `NoMatches`) or after the name (then the refusal must raise inside `_save_or_toast`, exception type named)? | **R15:** pin refusal AT the `s` keypress, BEFORE the save-as prompt (no name is asked for a save that cannot happen), by the same toast mechanism at the call site, no exception raised; pinned toast: severity `error`, text exactly `the CSV has colliding ids — nothing was saved; see the preview`; AT-072/072b/c/d drive `i`, path, `enter`, `s` through `_open_import`'s first steps and assert no prompt pushed + the toast + the workspace sha256 oracle unchanged; AT-074 still types the name. | applied (ledger .9) |
| 4 | qa-reviewer | med | round trip vs loader breadth | The round trip is broader than the loader: `dump` skips edges whose endpoint is missing; `parse` takes the root from text order — graphs with unusual root/edge order that save today could be refused; no fallback stated. | **R11 (root excluded — the found instance) + a stated fallback recorded in §6.3 / proposal §6:** if the P3 full-suite gate finds a graph that saves on master today but the new check refuses, the batch returns to design with that fixture. | applied (ledger .5; fallback stated) |
| 5 | qa-reviewer | med | perf budget | No numeric time/size threshold for the added parse; `dump`'s orphan loop is already O(N·E). | **R12:** the ≤ 25 %-of-`save`-wall-time threshold on a 6 000-node wide tree, measured once at P4 (median of 3) as evidence — not a suite assertion. | applied (ledger .6) |
| 6 | qa-reviewer | low | `line_num` semantics | `str.splitlines()` also splits on `\x0b`, `\x0c`, `\x1c`–`\x1e`, `\x85`, `\u2028`, `\u2029`, so `line_num` can differ from editor line numbers. | **R16:** one-line caveat in LLR-CSV.2.1 (no fixture required). | applied (ledger .10) |
| 7 | qa-reviewer | low | id hygiene | "A.6" and "M2" were each reused for two different things. | **R16:** a short glossary of mutation ids (M1, M1b, M2, M2b, M2c, M3, M4) in `01-requirements.md` §6.1; finding ids and ruling ids enumerated there; no id reused. | applied (ledger .10) |

### Orchestrator rulings R11–R16 (round 2 → applied in this unit)

| Ruling | Answers findings | Disposition |
|--------|------------------|-------------|
| R11 — the round trip compares the NODE-ID SET and the EDGE SET ((parent, child) pairs) only — NOT the root. `parse` takes the root from text order and `dump` writes edges before parentless nodes, so a forest's root drifts on reload (pre-existing). Regression requirement + test: a legacy forest (`a` / `b --> c`) loads, is edited (a child added) and saves (LLR-CSV.1.3, `test_save_accepts_legacy_forest_after_edit`, M4). Drift → backlog **B-117**. | A7/B4, qa 4 | applied (`LED-2026-10-10-csv-safety-batch.5`; B-117) |
| R12 — the check parses the exact `.mmd` text `save` is about to write (one `dump` per save — the same string is written); complexity stated honestly: `dump` is already O(N·E) in its parentless-node loop (`mapper/mermaid.py:152-153`, B-33 territory, not fixed here). Numeric threshold: the added parse costs ≤ 25 % of `MapStore.save` wall time for a 6 000-node wide tree, measured once at P4 as evidence (median of 3) — NOT a wall-clock assertion in the suite. | B5, qa 5 | applied (`.6`) |
| R13 — a root-row slug collision has a non-empty `csv_collisions`, so the COLLISION sentence wins (precedence collision > multi-parent > cycle). HLR-CSV.2 boundary text and proposal §5 fixtures fixed to agree; the store-level refusal of that graph (it is a cycle) remains a store unit case. | qa 1 | applied (`.7`) |
| R14 — AT-072 is the PREVIEW-layer acceptance; its negative control is removing the preview refusal (record-keyed, M2c). The STORE layer's controls are its unit nodes only (M1, M1b). HLR-CSV.1 / LLR-CSV.1.1 wording corrected so no text claims M1 reddens AT-072. | qa 2 | applied (`.8`) |
| R15 — `_ImportPreviewScreen.action_save` refuses at the `s` keypress, BEFORE pushing the save-as prompt (no name is asked for a save that cannot happen), by the same toast mechanism at the call site (no exception raised): severity `error`, text exactly `the CSV has colliding ids — nothing was saved; see the preview`. AT-072/072b/c/d drive `i`, path, `enter`, `s` through `_open_import`'s first steps, then assert: no prompt screen pushed, the toast text, the workspace sha256 oracle unchanged. AT-074 (valid CSV) still types the name. | qa 3, B6 | applied (`.9`) |
| R16 — one-line caveat that `str.splitlines()` also splits on `\x0b` `\x0c` `\x1c`–`\x1e` `\x85` `\u2028` `\u2029`, so `line_num` counts those as line breaks (no fixture required); a short glossary of mutation ids (M1, M1b, M2, M2b, M2c, M3, M4) in §6.1; no id reused for two things. | qa 6, qa 7 | applied (`.10`) |

### shall / should check (round 2)
Clean: the round-2 amendments add no modal verb to any Statement beyond `shall`.

### Security review summary (round 2)
No new security-reviewer findings. Family C still fires on the same surfaces (C6 input, C8 painted ids); R15's pinned toast is fixed English copy routed through `darkside.plain` — it carries no operator path, account name or CSV-derived text, so guard A-110 is unaffected.

### Verdict round 2
Both reviewers returned **approve-with-conditions** on both artifacts (`01-requirements.md`
+ `design/design-proposal.md`). The orchestrator merged their conditions into rulings
R11–R16; Kimi applied them to the contract, ledger, proposal and PLAN.md in this unit and
the PDR was sealed `approved with conditions` — conditions: the R11–R16 document fixes,
applied here and to be re-read at the DDR. Self-approved under the standing authorization.
