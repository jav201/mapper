# Design review record — PDR — mapper — Batch 2026-10-10-perf-batch

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
| Record id | `PDR-2026-10-10-perf-batch` |
| Reviews | `design/design-proposal.md` (drafted by Kimi) amended by the round-1 rulings R1–R9 (`LED-2026-10-10-perf-batch.2`), the Lane S withdrawal at the spike gate (`LED-2026-10-10-perf-batch.3`) and the round-2 rulings R10–R18 (`LED-2026-10-10-perf-batch.4`) |
| Participants | PDR: `architect` (Claude Opus) + `qa-reviewer` (Claude Sonnet). **`ux-reviewer` not owed:** trigger D1 did not fire — every remedy is behaviour-preserving (byte-identical paint and bytes), so there is no interaction design to review. · DDR: `architect` + `software-dev` + `qa-reviewer` |
| Date sealed | `2026-10-10` |
| **Verdict** | `approved with conditions` (C1–C10) |

---

## A · PDR checklist — preliminary design review

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Proposal complete: objective · modules and boundaries · diagrams · interfaces that change · **proposed test cases** · risks · rejected alternatives **where a real decision exists**, otherwise `n/a — <the decision already made, and by what>` | ✓ | all sections present and amended through round 2 (§2 module map, §4 frozen-interface rows, §5 AT/unit rows, §6 risk bullets, §7 forward-applicability, §8 lane plan); real alternatives rejected for cause in §6 (memoising full `_geometry` on the ViewState, renderer consumption of the model cache, the Lane S mechanisms) |
| 2 | Respects the boundaries of `docs/ARCHITECTURE.md` | ✓ | no §2/§3 boundary moves; the model cache is private to `model` (`_`-prefixed, `compare=False, repr=False` — the `csv_collisions` precedent, no new outbound dependency); the layout memo lives inside `views` on the renderer instance; the one §4 `Graph`-row note is a trunk act at the join, never inside a lane |
| 3 | **Forward applicability:** every output has a NAMED downstream consumer | ✓ | §7 names a consumer for every output incl. the round-2 additions — M-R2c/d/e and the nodes-writer census by Inc-R2, the AT-076 add_child gesture + `mermaid.dump` wrapper by Inc-M2, the per-lane M-M3 record by the DDR; the withdrawn Lane S rows name B-118 as their consumer |
| 4 | Every requirement has foreseen coverage | ✓ | the surviving contract (HLR-PERF.1/2, LLR-PERF.1.1–1.3, 2.1–2.3) maps to §5 rows and the four new test files; PERF.3.x was withdrawn to B-118 with its coverage (`LED-2026-10-10-perf-batch.3`) and §5.2 is scoped to the survivors (ruling R15) |
| 5 | Proposed test cases are observable **and non-vacuous** — the reddening mutation is named for each | ✓ | every §5 row names its reddening mutation, now incl. M-R2c (the `resize`/`title` arms — round-2 qa finding 1), M-R2d (`id(graph)` key, forced address reuse with the ruling R13 determinism escape) and M-R2e (the Lane R `nodes`-writer census guard); AT-076's gesture is a real persisting action (`a` add_child) so the oracle cannot pass vacuously (ruling R10); the `undo` arm no longer relies on non-deterministic allocator reuse (ruling R13) |
| 6 | The gauntlet controls that apply are declared, with who pays for them | ✓ | surviving controls per lane: Lane R = M-R1a/b, M-R2/b/c/d/e on `tests/test_perf_paint_clip.py` + `tests/test_perf_layout_memo.py`; Lane M = M-M1a/b/c, M-M2a/b, M-M3 on `tests/test_perf_adjacency.py` + `tests/test_perf_dump.py`; M-M3 is recorded per lane at the DDR and is not a Lane R control (ruling R17); no M-S* controls — withdrawn with Lane S; each RED executed as a transcript in the increment that lands it |
| 7 | Interfaces **frozen** for the fork are listed | ✓ | §4 freezes: `Canvas` (`wire`/`edge`/`elbow_down`/`put`/`text`/`rows` signatures), `IRenderer.render(graph, selected_id, w, h, **kwargs) -> Text`, `Graph` (value-object shape; the cache is `_`-prefixed and absent from `__eq__`/`repr`), `mermaid.parse`/`dump`/`slugify`, `MapScreen`/`refresh_canvas` (Lane S withdrawn — untouched), `MAX_RENDER_NODES`'s value, `keymap.py`/`darkside.py`; the layout memo is instance-private state, not an interface |
| 8 | Lane plan: file sets disjoint, family-B census run per lane | ✓ | lanes R and M fork in parallel worktrees off the stamped trunk: R = {`mapper/canvas.py`, `mapper/views/layered.py`, `tests/test_perf_paint_clip.py`, `tests/test_perf_layout_memo.py`}, M = {`mapper/model.py`, `mapper/mermaid.py`, `tests/test_perf_adjacency.py`, `tests/test_perf_dump.py`} — `R∩M = ∅` (executed intersection test at P1); Lane S withdrawn to B-118 (D1); family-B reverse census executed at P1 (23 test files on renderer/`children_of`/`parent_of` symbols) |
| 9 | UX lens applied (if family D fired): interaction design reviewed | ⚠ | family D did not fire for this scope (D1) — every remedy is behaviour-preserving: byte-identical paint and bytes are the batch's oracle (LLR-PERF.1.3); **ux-reviewer not owed** — there is no interaction change to review |
| 10 | Security lens applied (if family C fired) | ✓ | family C did not fire (no input surface, no painted operator ids, no network, no new painted string); guard A-110 (`tests/test_no_operator_paths.py`) unaffected; no home-path/account-name surface added |

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

| # | Condition left open at PDR | Discharge status | The artifact line that proves it |
|---|---|---|---|
| C1 | R10 document fixes: AT-076's drive gesture is the `a` add_child action through real keys on a saved map (ficha edits are drafts — `drafts.py:138` deepcopy; the snapshot `dump` is bound at import, `undo.py:10`); the counting wrapper wraps `mapper.mermaid.dump` itself (`store.py:861` call-time import); the golden is pinned to the map AFTER the edit; archive/attachments are boundary fixtures | **applied in this unit — re-read at DDR; the node executes in Inc-M2** | `01-requirements.md` §5.1 AT-076, HLR-PERF.2 shipped surface; proposal §5 AT-076 row |
| C2 | R11 document fixes: the linear dump is a LOCAL incident pass (one pass over the edges building the incident set inside the dump call), NOT the adjacency cache; bound per dump call ≤ 2E + c; scaling ratio count(2N)/count(N) ∈ [1.8, 2.2] | **applied in this unit — re-read at DDR** | HLR-PERF.2 Statement; LLR-PERF.2.2 Statement; proposal §4 MermaidImporter/Exporter row |
| C3 | R12 document fixes: the layout memo lives on the `LayeredRenderer` INSTANCE (`screen.py:73`; the import preview's fresh renderer per paint, `import_preview.py:103`, simply misses) and is passed into module-level `_geometry` as an argument — no module-global state; the spy is the named instance counter `_layout_misses` | **applied in this unit — re-read at DDR** | LLR-PERF.1.2 Statement/Executed verification; glossary `memo-miss spy`; proposal §4 `IRenderer.render` row, §5 AT-075b row |
| C4 | R13 document fixes: the `resize`/`title` arms are reddened by M-R2c (cache the SCALED layout — key drops `card_w`/`gap`); the `undo` arm is a plain "new Graph object misses" check plus M-R2d (`id(graph)` key) exercised by a node forcing address reuse (drop the old graph, `gc.collect()`, allocate a same-shape graph, assert a miss) — with the escape that if reuse cannot be forced deterministically the node says so and keeps only the plain check | **applied in this unit — re-read at DDR; the M-R2d escape clause is decided at Inc-R2 execution** | LLR-PERF.1.2 Executed verification/Negative control; §6.1 mutations M-R2c/M-R2d; proposal §5 `test_memo_invalidation_arms` + `test_memo_id_reuse` rows |
| C5 | R14 document fixes: Lane R carries its own AST census guard on `nodes` dict writers (declared set: `model.py` `add_node` `model.py:165`, `screens/map/editing.py` wholesale `editing.py:216`), mirroring Lane M's `edges` guard; control M-R2e → `test_nodes_writer_census` | **applied in this unit — re-read at DDR; the node is created in Inc-R2** | LLR-PERF.1.2 Statement/Negative control; §6.1 mutation M-R2e; proposal §5 `test_nodes_writer_census` row |
| C6 | R15 document fixes: §5.2 scoped to the surviving LLRs (PERF.1.x, 2.x) and controls (M-R1a/b, M-R2/b/c/d/e, M-M1a/b/c, M-M2a/b, M-M3 — no M-S*); the AT-077/077b golden line left with the Lane S withdrawal | **applied in this unit — re-read at DDR** | `01-requirements.md` §5.2 first two bullets + golden provenance bullet |
| C7 | R16 document fixes: the wire-cap rationale names the y-only failure — "a y-only clip fails the cap", the x-axis carries the whole gain (a correct x-only clip ≈ 0.5 M estimated PASSES; probe p4 one render at wide-2000, 118×34: no clip 524,313 · x-only 6,547 · y-only 524,313 · x+y 6,547); the exact count and geometry are measured and recorded at execution (expected order: thousands per render) | **applied in this unit — re-read at DDR; the exact-count measurement is owed at execution as evidence in `04-validation.md`** | HLR-PERF.1 Numeric pass threshold; LLR-PERF.1.1 Numeric pass threshold; §5.1 AT-075 |
| C8 | R17 document fixes: M-M3 (`git diff 5cde04e -- mapper/views` empty) runs on the Lane M branch BEFORE the join; the DDR records it PER LANE — it is not a Lane R control (Lane R legitimately edits `mapper/views/layered.py`) | **applied in this unit — re-read at DDR; the per-lane record is produced at the join** | LLR-PERF.2.3 Executed verification; §6.1 mutation M-M3; proposal §8 join plan step (3b) |
| C9 | R18 document fixes: the census alias form documents its limits — aliasing through function arguments, containers, or attributes on other objects is NOT detected | **applied in this unit — re-read at DDR** | LLR-PERF.2.1 census-guard paragraph; proposal §5 census row |
| C10 | The goldens-at-base capture is owed BEFORE the lanes fork: AT-075 painted lines, AT-075b painted lines, AT-076 `.mmd` bytes (pinned to the map AFTER the add_child edit) — captured on base SHA `5cde04e` (pre-remedy) at the trunk, base SHA + sha256 per golden (the AT-065 precedent); the wire counter resets after mount | **NOT yet executed — owed at the trunk before the fork; verified at the DDR provenance check** | `01-requirements.md` §5.2 golden provenance; PLAN.md fork plan step (0) |

---

## C · Verdict and what it means

- `approved` — the bar is met on all three axes (Coverage · Certainty · Evidence); state which.
- `approved with conditions` — list them above; each is individually dischargeable and re-read at the next gate.
- `rejected` — **returns to DESIGN, not to implementation.** Name the gap that caused it.

**Verdict sealed 2026-10-10: `approved with conditions` (C1–C10)** on Coverage ✓ (after R15: the
surviving requirements have foreseen coverage; the withdrawn Lane S scope left cleanly to B-118) ·
Certainty ✓ (after R10/R13: every AT's control is reachable, named and non-vacuous) · Evidence ✓
(after R16/C10: thresholds are measurements with an owner and a recording point, not assertions).
Round 1 iterated (R1–R9 applied, `LED-2026-10-10-perf-batch.2`); the Lane S spike gate resolved to
withdrawal (B-118, `LED-2026-10-10-perf-batch.3`); round 2 returned approve-with-conditions on both
artifacts from both reviewers with no HIGH findings, and the orchestrator's rulings R10–R18 were
applied to the contract, ledger, proposal and PLAN.md in the same unit that sealed this record
(`LED-2026-10-10-perf-batch.4`). **Self-approved under the standing authorization** (`state.json`
`batch_objective`, quoted in PLAN.md). No lane forks until C10 (the goldens-at-base capture) is
executed at the trunk; C1–C9 are re-read at the DDR.

## D · Ids this record binds *(the glue of the repo ↔ vault split)*

| This record's decision | Id | Where it lands in the **repo** |
|---|---|---|
| D1 — the batch forks TWO disjoint lanes, R and M, in parallel worktrees off the stamped trunk; Lane S is WITHDRAWN to backlog B-118 (spike PERFS inconclusive) with HLR-PERF.3 / LLR-PERF.3.1–3.2 / AT-077/077b; `R∩M = ∅`; the trunk owns the join (DDR) | `PDR-2026-10-10-perf-batch#D1` | PLAN.md fork plan; `design/design-proposal.md` §8; `.dev-flow/BACKLOG.md` B-118; HLR-PERF.3 Status |
| D2 — the unscaled `_tree_layout` memo (slot cx, level per node; `card_w`/`gap` scaling re-applied per call) lives per `LayeredRenderer` INSTANCE, keyed by strong references (`graph is`, `edges is` + len, `nodes is` + len, `root_id`, hidden fold set) and passed into module-level `_geometry` as an argument — no module-global state; the spy is the named instance counter `_layout_misses`; Lane R guards its `nodes`-writer census (M-R2e) | `PDR-2026-10-10-perf-batch#D2` | LLR-PERF.1.2; §6.1 mutations M-R2/b/c/d/e; `tests/test_perf_layout_memo.py` rows |
| D3 — `Graph` serves `children_of`/`parent_of` from a private adjacency cache (`_`-prefixed, `compare=False, repr=False`), valid only while `self._adj_src is self.edges and len(self.edges) == n`; `children_of` returns a fresh list; the edge-mutation census is guarded by an AST test (writers ⊆ {`model.py` `add_edge`, `editing.py` `_remove_subtree`}; every in-place form + aliases flagged, limits documented) | `PDR-2026-10-10-perf-batch#D3` | LLR-PERF.2.1; `tests/test_perf_adjacency.py` rows; `docs/ARCHITECTURE.md` §4 `Graph` row (trunk amendment at the join) |
| D4 — `mermaid.dump` determines orphan membership by one LOCAL incident pass over every edge (dangling edges included), not the adjacency cache; bound per dump call ≤ 2E + c, scaling ratio [1.8, 2.2]; AT-076 drives the `a` add_child gesture through real keys with the counting wrapper on `mapper.mermaid.dump` itself | `PDR-2026-10-10-perf-batch#D4` | HLR-PERF.2; LLR-PERF.2.2; §5.1 AT-076; `tests/test_perf_dump.py` rows |
| D5 — the behaviour oracle is pre-change goldens captured at base SHA `5cde04e` BEFORE the fork (base SHA + sha256 per golden, AT-065 precedent) + the untouched AT-065 parity goldens and `test_repair_golden_census.py` pins; every remedy paints byte-identically | `PDR-2026-10-10-perf-batch#D5` | LLR-PERF.1.3; §5.2 golden provenance; `tests/test_mod_parity.py`; `tests/test_repair_golden_census.py` |

**What decides code lands in the repo.** A decision that fixes an interface does not stay only in the
vault: it is reflected in the requirement or in the module map, which are versioned beside the code.
