# Review — mapper — Batch 2026-10-10-perf-batch

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`).
> Phase 2 artifact. Reviewers (in parallel): `architect` ∥ `qa-reviewer` by trigger family C (always in `full`).

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/guides/review-template.md` explains each field below and the rules that read them. It ships with the flow and is not copied into this batch.

## ✅ Verdict (read first)

- **Gate:**
  - **Round 1** → `iterate-to-refine` → Phase 1 (contract + PDR amended; no security findings; the
    Lane S mechanism was contradicted by the code and is replaced under a spike gate).
  - Round 2 → pending (owed after this iteration's amendments are re-reviewed).

- **Findings (round 1):** 6 high · 13 med · 5 minor (24 total). Both reviewers were read-only; the
  architect ran probes on the scratchpad (`probe/p1.py`, `p2.py`). The orchestrator ruled R1–R9
  (table below); Kimi applied them to the contract, ledger, PLAN and PDR in P1 iteration 1
  (ledger `LED-2026-10-10-perf-batch.2`).
- **shall/should check:** ✓ clean (round 1) — `shall` appears in Statements only; no modal `should` inside any HLR/LLR statement.
- **Two-layer (blockers):** ✗ in round 1 — AT-076 was not genuinely black-box: on the map screen
  `ctrl+s` is `save_draft` (`mapper/keymap.py:184`) and with no draft it saves nothing
  (`drafts.py:131-132`), so the iteration oracle counted 0 and passed trivially (finding A2) →
  fixed by R3 (real persisting gesture through `_save_or_toast`). Every story has an AT; both trace
  chains are complete — unchanged.
- **Census (change-first):** done best-effort by the architect (§B of the transcript: edge-mutation
  census re-verified with the widened in-place forms; mount-path contradictions measured, 6 failing
  tests) — ⚠ the "no existing test breaks" claim stays unproven until the DDR full-suite gate.
- **Security:** not run — trigger family C did not fire (no input surface, no painted operator ids,
  no network; the batch adds no painted string). No security-reviewer findings in round 1.
- **Evidence checklists (architect / qa):** summarized below from the reviewers' transcriptions.

---

## Detail (reference)

### Findings — round 1

Reviewer ids follow the orchestrator's transcription of the round-1 review
(`PERF-review-r1.md`, held in the orchestrator's temp area, not committed): architect requirements
findings `A1`–`A6`, architect PDR findings `B1`–`B6` (B1 carries two parts), qa-reviewer findings
`HIGH-1`, `MED-2`…`MED-9`, `LOW-10`…`LOW-12`. HEAD at review: `56d32ce`.

| ID | Reviewer | Severity | Area / Req | What | Recommendation / ruling | Status |
|----|----------|----------|------------|------|------------------------|--------|
| A1 | architect | high | premise 3, LLR-PERF.1.2 | Premise 3 is false: `_tree_layout(graph, card_w, gap, hidden)` takes `card_w` (`views/layered.py:192-196`), derived from visible titles/meta and `w` (`:333-342`); the memo key goes stale on resize and on a title edit that widens `widest`; the boundary row (`01-requirements.md:273`) asserts the opposite of the truth. | **R1** — memoise the UNSCALED layout on strong references; scaling re-applied per call; arms for resize and widest-title edit. | applied (iteration 1) |
| A2 | architect | high | AT-076, LLR-PERF.2.2 | AT-076 is vacuous: on the map screen `ctrl+s` is `save_draft` (`keymap.py:184`); with no draft it returns without saving (`drafts.py:131-132`) → count 0, passes trivially; with a draft the save runs on `copy.deepcopy(base_graph)` (`drafts.py:138`) plus a snapshot `dump`. | **R3** — AT-076 drives a REAL save path: an edit gesture that persists via `_save_or_toast` (`screens/map/editing.py`). | applied |
| A3 | architect | high | HLR-PERF.2 threshold | ≤ 3·(N+E) is wrong: simulated fix on wide-6000 — `MapStore.save` alone 35,994 edge iterations vs threshold 35,997 (3 margin); the snapshot dump + sidecar adds 11,998 → the real gesture reds a correct fix. | **R3** — assert per `mermaid.dump` call ≤ 2E + c AND a scaling ratio count(2N)/count(N) ∈ [1.8, 2.2]. | applied |
| A4 | architect | med | M-R1b, LLR-PERF.1.3 | M-R1b is an equivalent mutant: clipping at `<= self.w` only adds a call `wire` drops (`canvas.py:107-109`). | **R5** — the control drops an in-bounds cell (e.g. `min(xb, w-1)`). | applied |
| A5 | architect | med | golden provenance | Pinned goldens must be generated from pre-change code at the trunk before the fork. | **R7** — capture on base SHA `5cde04e`, base SHA + sha256 per golden; wire counter resets after mount. | applied |
| A6 | architect | low | LLR-PERF.2.3 | Inaccurate as written: `views/lane.py:121,211,330` already call `children_of`. | **R8** — reword "Lane M imports no new cache name into `mapper/views/`"; M-M3 = file-diff check. | applied |
| B1a | architect | med | Lane M cache soundness | Sound today by accident: `Edge` frozen (`model.py:66`); writers only `model.py:170` and `editing.py:217`; no in-place forms in `mapper/`; tests append or replace wholesale. `id()` can be reused after free — avoided today only because `_remove_subtree` calls `children_of` BEFORE reassigning (`editing.py:213`). | **R2** — strong ref + `self._adj_src is self.edges and len == n`; census guard widened (sort/reverse/clear/`__setitem__`/slice/del/`+=`/`*=` + aliases); `children_of` returns a fresh list (`painting.py:519` binds it). | applied |
| B1b | architect | med | Lane M linear dump | Incident counting must cover every edge as incident, incl. dangling (today's `any()` does, `mermaid.py:152`). | **R3** — dangling-edge fixture in the byte-golden set. | applied |
| B2 | architect | high | Lane R memo | Memo the UNSCALED `pos` (slot cx, level), independent of `card_w`; re-apply `step` per call (O(N)); key: graph `is`, edges `is`+len, nodes `is`+len, root_id, hidden — strong refs; `_geometry` is module-level (`layered.py:306`) so the memo threads through it; arms: resize, widening title edit, fold, focus toggle, undo, outline/radial round trip. | **R1** — as stated; the round trip is extended to outline↔radial↔layered. | applied |
| B3 | architect | low | span clip design | APPROVE — only tightens loop bounds; junction endpoints by unchanged `wire`, masks OR, tone first-write-wins (`canvas.py:107-128`); the reference "clip off" render lives in the test as a copy of the old method, never a `Canvas` flag. | **R5** — bare-`Canvas` equality shapes: `x1<x0`, spans fully off-canvas, `ybus` above/below, negative pan. | applied |
| B4 | architect | high | Lane S mechanism | The proposed mechanism is contradicted by the code: `_declared_for is None` is set on every `refresh_canvas` (`painting.py:701`); "strip first" breaks the ordering rule (measured 6 failing tests, `painting.py:668-673`); the deferred render would run in the settle pass which swallows exceptions (`:351-357`) and skips `_reclamp_pan`. | **R4** — WITHDRAWN; new candidate: keep ordering; skip only the canvas render while `canvas.size.width == 0`; first render through the guarded/reclam path. GATED on spike PERFS proving ncalls=1 at mount with every existing mount test green; else Lane S → B-118. | applied (withdrawn + gated) |
| B5 | architect | low | disjointness, census guard | APPROVE; the census guard should assert "edges writers ⊆ declared set". | **R2** — the guard asserts the writers set ⊆ {`model.py` `add_edge`, `editing.py` `_remove_subtree`}. | applied |
| B6 | architect | med | increments ≤ 2 source files | APPROVE with conditions: join adds goldens pinned pre-change at trunk + the Lane S spike result. | **R7, R4** — provenance pinned; gate recorded in PLAN/design. | applied |
| HIGH-1 | qa-reviewer | high | layout-memo key | Same as A1/B2: the key is unsound; add resize and widest-title-edit arms with named mutations. | **R1** — arms `resize` and `title` in `test_memo_invalidation_arms[...]`. | applied |
| MED-2 | qa-reviewer | med | selector ambiguity | `-k at077` selects at077b, `-k at075` selects at075b; `-k identity`/`cache`/`counted` substring-match other files. | **R6** — every verification names exact `file::test` node ids. | applied |
| MED-3 | qa-reviewer | med | layout-once spy location | `_tree_layout` ran 10× for 2 renders (`evidence/perf0c-nav.transcript:44`); a name spy on the layout entry can never read 1. | **R1** — count memo MISSES at the named hit-check point in LLR-PERF.1.2. | applied |
| MED-4 | qa-reviewer | med | cache-token id reuse | Same as B1a: strong ref + `is`; mutation-script arm with two wholesale replacements and no lookup between (id reuse). | **R2** — in `test_cache_mutation_script_equality`. | applied |
| MED-5 | qa-reviewer | med | census guard too narrow | In-place `edges[i]=e`, `del`, `+=`, `.sort()` keep id and len — the guard misses them; aliases (`x = expr.edges` then x mutated) too. | **R2** — one mutation per form in `test_census_in_place_forms[setitem|slice|del|iadd|imul|sort|reverse|clear|extend|insert|remove|pop|alias]`. | applied |
| MED-6 | qa-reviewer | med | span clip test coverage | No test for `Canvas.edge`; nothing panned or negative. | **R5** — bare-`Canvas` equality for BOTH methods; a panned ViewState and a fold in the render grid. | applied |
| MED-7 | qa-reviewer | med | golden provenance | Capture on the base SHA before any remedy; record base SHA + sha256 per golden; reset the wire counter after mount so mount calls don't count toward the two-keypress budget. | **R7** — provenance protocol in §5.2; counter reset in AT-075. | applied |
| MED-8 | qa-reviewer | med | AT coverage | AT-065 uses a tiny seed map; AT-075b's post-edit arm covers archive only. | **R1** — arms `add_child` (real keys) and `undo` (new Graph = the id-reuse case). | applied |
| MED-9 | qa-reviewer | med | M-M3 cannot redden | Renderers already call `children_of` (`:313`). | **R8** — M-M3 is the file-diff check `git diff 5cde04e -- mapper/views` empty. | applied |
| LOW-10 | qa-reviewer | low | optional coverage | Minimap/outline byte test over a forest and a multi-parent graph. | Included (cheap): `tests/test_perf_adjacency.py::test_minimap_outline_forest_dag_bytes`. | applied |
| LOW-11 | qa-reviewer | low | P4 wall-clock plan | Base and head must run on the same machine and session, interleaved; raw runs into `04-validation.md`. | **R9** — P4 protocol pinned in §5.2. | applied |
| LOW-12 | qa-reviewer | low | wall-clock assertions | None asserted — correct; AT-077's poll-until-settled is a condition wait (acceptable). | Recorded; no change. | recorded |

**Verified sound by the architect (probed):** the baselines every threshold cites match the
transcripts (23,983,998 wire / 2 keys; 35,975,997 wire + render ncalls=3 at mount; 18,003,001
genexpr / 6002 `any` / 6000 `parent_of`); the canvas is viewport-sized (`views/layered.py:614`) so
the clip bites; the 4.8 M cap is loose (a one-axis clip passes) → tightened to 1,200,000 with the
derivation from the baseline stated; the edge-mutation census holds today (writers ⊆ the declared
set; no in-place forms; no aliases); the Lane S contradictions measured (6 failing tests on the
strip-first reordering).

### Orchestrator rulings R1–R9 (round 1 → P1 iteration 1)

| Ruling | Answers findings | Disposition |
|--------|------------------|-------------|
| R1 — Lane R layout memo: memoise the UNSCALED layout (slot cx, level per node) keyed by strong references compared with `is` — graph object, `edges` list (+len), `nodes` dict (+len), `root_id`, hidden fold set; re-apply `card_w`/`gap` scaling per call (O(N)); thread the memo through module-level `_geometry`; the spy counts memo MISSES at the named hit-check point; arms (each a named mutation): resize, widest-title edit, fold, focus toggle, undo (new Graph), add-child via real keys, outline↔radial↔layered round trip; premise 3 corrected. | A1, B2, HIGH-1, MED-3, MED-8 | applied (`LLR-PERF.1.2`, premise 3, HLR-PERF.1) |
| R2 — Lane M adjacency cache: strong ref, hit iff `self._adj_src is self.edges and len(self.edges) == n`; `children_of` returns a fresh list; the census guard (AST over `mapper/`) asserts writers of `edges` ⊆ {`model.py` `add_edge`, `screens/map/editing.py` `_remove_subtree`} and flags `edges[i]=`, slice assignment, `del`, `+=`, `*=`, `.sort`, `.reverse`, `.clear`, `.extend`, `.insert`, `.remove`, `.pop` and aliases, one mutation per form; the mutation script gains two wholesale replacements with no lookup between (id reuse). | B1a, B5, MED-4, MED-5 | applied (`LLR-PERF.2.1`) |
| R3 — Lane M linear dump: incident counting covers every edge incl. dangling (fixture); AT-076 drives a REAL save path (an edit gesture persisting via `_save_or_toast`, not bare `ctrl+s` with no draft); oracle per `mermaid.dump` call ≤ 2E + c AND scaling ratio count(2N)/count(N) ∈ [1.8, 2.2]; `.mmd` byte-identical vs a golden. | A2, A3, B1b | applied (`LLR-PERF.2.2`, HLR-PERF.2, AT-076) |
| R4 — Lane S: the proposed mechanism is WITHDRAWN; new candidate: keep `refresh_canvas` ordering unchanged, skip only the canvas render while the region is unassigned (`canvas.size.width == 0`), route the first real render through the guarded/reclamp path. GATED on spike unit PERFS (render ncalls = 1 at mount, every existing mount test green); if the spike fails, Lane S leaves the batch to the backlog (B-118). Both branches written into PLAN.md and the PDR. | B4, B6 | applied (`HLR-PERF.3`, `LLR-PERF.3.1`, gated) |
| R5 — span clip tests: bare-`Canvas` unit equality of the clipped `elbow_down` and `edge` vs a reference copy of the OLD methods kept in the test file (never a `Canvas` flag): `x1<x0`, spans fully off-canvas, `ybus` above/below the canvas, negative pan; the render grid gains a panned ViewState and a fold; M-R1b replaced by a non-equivalent mutant (`min(xb, w-1)` drops an in-bounds cell); the wire-count cap tightened so a one-axis clip fails (numbers stated from the baseline: 23,983,998 → cap 1,200,000). | A4, B3, MED-6 | applied (`LLR-PERF.1.1`, `LLR-PERF.1.3`, §6.1) |
| R6 — every executed verification names exact node ids (`file::test`), no `-k` substrings. | MED-2 | applied (all `Executed verification` fields) |
| R7 — goldens for AT-075/075b/076/077 are captured on the BASE SHA `5cde04e` (pre-remedy) at the trunk before the lanes fork, recorded with base SHA + sha256 per golden (as AT-065 does); the wire counter resets after mount. | A5, B6, MED-7 | applied (§5.1 AT-075, §5.2) |
| R8 — reword `LLR-PERF.2.3` to "Lane M imports no new cache name into `mapper/views/`"; M-M3 becomes a file-diff check (`git diff 5cde04e -- mapper/views` empty on the Lane M branch). | A6, MED-9 | applied (`LLR-PERF.2.3`, §6.1) |
| R9 — P4 wall-clock plan: base and head on the same machine and session, interleaved runs, median of 3, raw runs pasted into `04-validation.md`. | LOW-11 | applied (§5.2, PDR §7) |

### shall / should check
Clean (round 1): `shall` in Statements only; no modal `should` inside any HLR/LLR statement.

### Two-layer acceptance review (blockers)

| Story / Req | (a) AT present | (b) deliverable+method named | (c) both chains | (d) black-box pure | Status |
|-------------|----------------|------------------------------|-----------------|--------------------|--------|
| US-PERF-001 / HLR-PERF.1 | yes | yes | yes | yes | ✓ |
| US-PERF-002 / HLR-PERF.2 | yes | yes | yes | no in round 1 — AT-076's `ctrl+s` drive path saved nothing (A2) → fixed by R3 | blocker (A2) → fixed |
| US-PERF-003 / HLR-PERF.3 | yes | yes | yes | yes (pending the spike gate) | ✓ (gated) |

### Supersession census (change-first)
Best-effort census executed by the architect (§B of the transcription): the edge-mutation census
re-verified with the widened in-place forms (writers ⊆ the declared set today; every in-place form
would be flagged); every `children_of` consumer checked for the fresh-list change (`painting.py:519`
binds the result); the mount-path reordering measured (6 failing tests — the reason R4 withdraws
the mechanism). Reservations: the spot checks do NOT prove the whole suite stays green — **the DDR
full-suite gate is the guarantee**. The increment gate must confirm the four new test files plus the
re-run pins (`test_mod_parity.py`, `test_repair_golden_census.py`, store round-trip + CSV suites,
the B-56/B60 mount tests).

### Security review summary
Not run — trigger family C did not fire (no input surface, no painted operator ids, no network,
no new painted string). Guard A-110 (`tests/test_no_operator_paths.py`) unaffected; the batch adds
no painted string and no home-path/account-name surface.

### Evidence checklists — architect · qa-reviewer

**architect (round 1):**
- ✓ baselines re-verified against the transcripts (wire counts, render ncalls, genexpr counts);
- ✓ premise 3 refuted against `layered.py:192-196,333-342` (probe: `card_w` from titles/meta + `w`);
- ✓ AT-076 vacuity reproduced (`ctrl+s` = `save_draft`, no-op without a draft, `drafts.py:131-132`);
- ✓ the ≤3·(N+E) threshold shown unsatisfiable (simulated fix: 35,994 vs 35,997 on save alone);
- ✓ M-R1b shown equivalent (clip at `<= self.w` only adds a call `wire` drops);
- ✓ cache soundness today accidental (`_remove_subtree` calls `children_of` before reassigning, `editing.py:213`);
- ✗ Lane S mechanism contradicted by the code (fixed by R4 — withdrawn + gated);
- ✓ census re-verified with the widened forms; no in-place writers today.

**qa-reviewer (round 1):**
- ✓ baselines verified against the transcripts; the canvas is viewport-sized so the clip bites;
- ✗ the 4.8 M cap loose (a one-axis clip passes) → tightened to 1,200,000 (fixed by R5);
- ✗ selector ambiguity (`-k at077` selects at077b; `-k identity`/`cache`/`counted` cross-match) → exact node ids (fixed by R6);
- ✗ layout-once spy location undefined (`_tree_layout` 10× per 2 renders) → memo misses at a named point (fixed by R1);
- ✗ census guard too narrow (in-place forms keep id+len) → widened + one mutation per form (fixed by R2);
- ✗ no `Canvas.edge` test, nothing panned/negative → bare-`Canvas` equality shapes (fixed by R5);
- ✗ golden provenance and mount-charged wire counter (fixed by R7);
- ✗ AT-075b post-edit arm covers archive only → add-child + undo arms (fixed by R1);
- ✗ M-M3 unreddenable → file-diff check (fixed by R8);
- ✓ P4 protocol and LOW-12 recorded (fixed by R9 / no change).
