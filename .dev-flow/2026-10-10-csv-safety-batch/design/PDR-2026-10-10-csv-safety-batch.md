# Design review record — PDR — mapper — Batch 2026-10-10-csv-safety-batch

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
| Record id | `PDR-2026-10-10-csv-safety-batch` |
| Reviews | `design/design-proposal.md` (drafted by Kimi) amended by the round-1 rulings R1–R10 (`LED-2026-10-10-csv-safety-batch.2`…`.4`) and the round-2 rulings R11–R16 (`LED-2026-10-10-csv-safety-batch.5`…`.10`) |
| Participants | PDR: `architect` (Claude Opus) + `qa-reviewer` (Claude Sonnet). **`ux-reviewer` not separately run:** family D fired for copy only — one pinned sentence in the existing refusal panel (HLR-CSV.2) plus one pinned toast in the existing notify slot (LLR-CSV.2.3) — and both strings are fixed verbatim in the requirements and asserted byte-for-byte by AT-073 / AT-072b/c/d, so there is no interaction design to review beyond the reviewed copy. · DDR: `architect` + `software-dev` + `qa-reviewer` |
| Date sealed | `2026-10-10` |
| **Verdict** | `approved with conditions` (C1–C6) |

---

## A · PDR checklist — preliminary design review

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Proposal complete: objective · modules and boundaries · diagrams · interfaces that change · **proposed test cases** · risks · rejected alternatives **where a real decision exists**, otherwise `n/a — <the decision already made, and by what>` | ✓ | all sections present and amended through round 2 (§2a round-trip scope, §2a complexity, §4 preview/save rows, §5 fixture expectations, §6 forest/fallback/caveats, §7 characteristics); real alternatives in §6 (silent disambiguation, second return value, check-only-store, check-only-preview, predicate in `mermaid`/duplicated, persisting the record) — each rejected for cause |
| 2 | Respects the boundaries of `docs/ARCHITECTURE.md` | ✓ | the store check lives in `store` (which already imports `mermaid` — no new edge); the predicate and the record live in `model` (inbound-only module, no new imports); `screens` reads them via its declared `model` edge; `model.py` ownership named in increment 1 (ruling R10 / architect B3) |
| 3 | **Forward applicability:** every output has a NAMED downstream consumer | ✓ | §7 names a consumer for every output; the round-2 additions are consumed too — the forest regression (LLR-CSV.1.3) by increment 1, the pinned toast + `s`-keypress refusal by increment 2, the P4 perf measurement (≤ 25 % of `MapStore.save` wall time, median of 3) by the increment-1 packet / `04-validation.md` |
| 4 | Every requirement has foreseen coverage | ✓ | the proposal header lists every HLR/LLR incl. the round-2 addition LLR-CSV.1.3; each §5 row names its fixture set; the round-1 coverage gaps (empty-CSV panel, self-parent, collision shapes) were closed by R9/R1 and are unchanged by round 2 |
| 5 | Proposed test cases are observable **and non-vacuous** — the reddening mutation is named for each | ✓ | every §5 row names its reddening mutation, now incl. M4 (re-add the root comparison → the forest regression RED, ruling R11); AT-072's control is corrected to the record-keyed M2c — the store-side M1 provably cannot redden it (ruling R14); the refusal timing, the no-prompt assertion and the pinned toast text are pinned per node (ruling R15) |
| 6 | The gauntlet controls that apply are declared, with who pays for them | ✓ | per-layer controls (ruling R8, corrected by R14): store layer = M1/M1b/M3/M4 on `tests/test_csv_safety_store.py`; preview layer = M2/M2b/M2c on `tests/test_csv_safety_preview.py`; each RED executed as a transcript in the increment that lands it (lesson B-112(2)); M1b's fixture overwrites a pre-existing map (ruling R6) |
| 7 | Interfaces **frozen** for the fork are listed | ✓ | §4 freezes: `Graph` (defaulted field `csv_collisions`, `compare=False, repr=False`, + `multi_parent_ids()` + `CsvCollision`/`CsvRow` — additive), `preview_csv` (signature and `Graph` return type — the F4 contract), `_ImportPreviewScreen` (class, constructor, `#import-preview-canvas`, the "could not draw the preview" header), `MapStore.save` (signature + LLR-R01.5 cycle message), `_save_or_toast` (False + toast contract, unchanged) |
| 8 | Lane plan: file sets disjoint, family-B census run per lane | ✓ | one lane, two sequential increments; increment 1 = `{mapper/model.py, mapper/store.py, tests/test_csv_safety_store.py}`, increment 2 = `{mapper/import_csv.py, mapper/screens/import_preview.py, tests/test_csv_safety_preview.py}` — pairwise disjoint; the P1 reverse census (40 files reference the touched symbols) is recorded in §6 |
| 9 | UX lens applied (if family D fired): interaction design reviewed | ⚠ | family D fired for copy only — one pinned sentence in the existing refusal panel + one pinned toast in the existing notify slot; **ux-reviewer not separately run** because there is no interaction change to review: both strings are fixed verbatim in HLR-CSV.2 / LLR-CSV.2.3 (English, `darkside.plain`-routed, no path/account name) and asserted byte-for-byte by AT-073 / AT-072b/c/d; the refusal's placement at the `s` keypress — before the save-as prompt — was reviewed as qa MED-3 / ruling R15 |
| 10 | Security lens applied (if family C fired) | ✓ | family C fired (C6 — the CSV is an input surface; C8 — the sentence paints operator-supplied ids): every interpolated piece passes `darkside.plain`, styling from `mapper/darkside.py` tokens only; the R15 toast is fixed English copy with no interpolated operator data; guard A-110 (`tests/test_no_operator_paths.py`) must stay green at the P3 gate |

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
| C1 | R11 document fixes: the root removed from the round-trip comparison everywhere (`01-requirements.md` §1.3, HLR-CSV.1 Statement/threshold, LLR-CSV.1.1 Statement); LLR-CSV.1.3 + `test_save_accepts_legacy_forest_after_edit` + mutation M4 added; B-117 appended to `BACKLOG.md`; fallback stated (§6.3 / proposal §6) | **applied in this unit — re-read at DDR** | `01-requirements.md` §1.3 `loader invariants` row; HLR-CSV.1; LLR-CSV.1.1; LLR-CSV.1.3; `.dev-flow/BACKLOG.md` B-117 |
| C2 | R12 document fixes: complexity stated honestly (`dump` is O(N·E) at `mapper/mermaid.py:152-153`, B-33 territory); the check parses the exact text written (one `dump` per save); the ≤ 25 %-of-`save`-wall-time threshold on a 6 000-node wide tree recorded as a P4 measurement (median of 3), not a suite assertion | **applied in this unit — re-read at DDR; the P4 measurement itself is owed at P4 as evidence** | HLR-CSV.1 rationale; LLR-CSV.1.1 Statement; proposal §2a complexity; PLAN.md increment 1 |
| C3 | R13 document fixes: the root-collision fixture paints the COLLISION sentence at the preview; its cycle refusal is a store unit case; HLR-CSV.2 boundary, LLR-CSV.2.2 boundary, §5.2, §6.3 and proposal §5/§6 agree | **applied in this unit — re-read at DDR** | HLR-CSV.2 rationale + boundary catalog; LLR-CSV.2.2 boundary catalog; proposal §5 AT-073 row, §6 root-collision bullet |
| C4 | R14 document fixes: no text claims M1 reddens AT-072; AT-072's negative control is the record-keyed M2c; the store layer's controls are its unit nodes (M1, M1b) — HLR-CSV.1, LLR-CSV.1.1, §5.1 and proposal §5 corrected | **applied in this unit — re-read at DDR** | HLR-CSV.1 Negative control; LLR-CSV.1.1 Negative control; §5.1 AT-072; proposal §5 AT-072 row |
| C5 | R15 document fixes: the refusal pinned AT the `s` keypress, before the save-as prompt, same toast mechanism at the call site, no exception; pinned toast severity `error`, text exactly `the CSV has colliding ids — nothing was saved; see the preview`; AT-072/072b/c/d drive `i`, path, `enter`, `s` and assert no prompt pushed + the toast + the sha256 oracle; AT-074 still types the name | **applied in this unit — re-read at DDR; executed by increment 2's nodes** | LLR-CSV.2.3 Statement/Executed verification/threshold; proposal §4 preview row, §5 AT-072/072b/c/d rows; PLAN.md increment 2 |
| C6 | R16 document fixes: the `splitlines()` caveat in LLR-CSV.2.1; the mutation-id glossary (M1, M1b, M2, M2b, M2c, M3, M4) and the finding/ruling id families in §6.1; no id reused | **applied in this unit — re-read at DDR** | LLR-CSV.2.1 Statement (caveat); `01-requirements.md` §6.1; proposal §5 mutation list, §6 glossary bullet |

---

## C · Verdict and what it means

- `approved` — the bar is met on all three axes (Coverage · Certainty · Evidence); state which.
- `approved with conditions` — list them above; each is individually dischargeable and re-read at the next gate.
- `rejected` — **returns to DESIGN, not to implementation.** Name the gap that caused it.

**Verdict sealed 2026-10-10: `approved with conditions` (C1–C6)** on Coverage ✓ (after C1: every
requirement incl. LLR-CSV.1.3 has foreseen coverage) · Certainty ✓ (after C4/C5: every AT's control
is reachable and pinned) · Evidence ✓ (after C2: thresholds are measurements with an owner, not
assertions). Both round-2 reviewers returned approve-with-conditions on both artifacts; the
orchestrator merged their findings into rulings R11–R16, all applied to the contract, ledger,
proposal and PLAN.md in the same unit that sealed this record (ledger
`LED-2026-10-10-csv-safety-batch.5`…`.10`). **Self-approved under the standing authorization**
(`state.json` `batch_objective`, quoted in PLAN.md); no increment starts until C1–C6 are applied —
they are — and each is re-read at the DDR.

## D · Ids this record binds *(the glue of the repo ↔ vault split)*

| This record's decision | Id | Where it lands in the **repo** |
|---|---|---|
| D1 — the check is the round trip in `MapStore.save` (`mapper/store.py`): `parse(dump(G))` must reproduce the node-id set and the edge set ((parent, child) pairs); refusal names the rule in plain language; `Graph.multi_parent_ids()` stays in `model` for the preview's multi-parent sentence only | `PDR-2026-10-10-csv-safety-batch#D1` | HLR-CSV.1; LLR-CSV.1.1; `docs/ARCHITECTURE.md` §4 (amendment owed at close, ruling R10) |
| D2 — the collision record rides the returned `Graph`: `csv_collisions: list[CsvCollision] = field(default_factory=list, compare=False, repr=False)` with frozen `CsvCollision(slug, rows)` / `CsvRow(line_no, raw_id)`; line numbers via `csv.DictReader.line_num` | `PDR-2026-10-10-csv-safety-batch#D2` | HLR-CSV.2; LLR-CSV.2.1; `docs/ARCHITECTURE.md` §4 `Graph` row (owed at close) |
| D3 — the preview refuses at the `s` keypress, BEFORE the save-as prompt, by the same toast mechanism at the call site (no exception raised): severity `error`, pinned text `the CSV has colliding ids — nothing was saved; see the preview`; no name is asked for a save that cannot happen | `PDR-2026-10-10-csv-safety-batch#D3` | LLR-CSV.2.3; PLAN.md D3 pin |
| D4 — sentence precedence collision > multi-parent > cycle; the root-collision fixture paints the COLLISION sentence at the preview (non-empty record) and is refused as a cycle at the store (a store unit case) | `PDR-2026-10-10-csv-safety-batch#D4` | HLR-CSV.2; LLR-CSV.2.2 |
| D5 — the round trip does NOT compare the root: a forest's root drifts on reparse (`dump` writes edges before parentless nodes, `parse` takes the first parentless node in text order) — pre-existing, B-117; LLR-CSV.1.3 + mutation M4 pin the exclusion; the P3-gate fallback (a found break returns to design) is stated | `PDR-2026-10-10-csv-safety-batch#D5` | HLR-CSV.1; LLR-CSV.1.1; LLR-CSV.1.3; `.dev-flow/BACKLOG.md` B-117 |

**What decides code lands in the repo.** A decision that fixes an interface does not stay only in the
vault: it is reflected in the requirement or in the module map, which are versioned beside the code.
