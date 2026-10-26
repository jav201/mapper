# DDR review, QA lens: relmap-r2-batch

**Role:** qa-reviewer (independent; authored none of the work under review) · **Batch:** 2026-10-25-relmap-r2-batch · **Date:** 2026-10-26 · **Mode:** `validation`
**Scope rows:** DDR §B rows 4 (C-18) and 5 (ledger), the P4 transcript hash, executor attributions (C-25), COND-QA-1…5, §F D-1, mutation control C-2 (my own battery), the two escaped-bug regression rows. Worktree `wt-r2`, branch feat/relmap-r2, HEAD d7bb95e.

## Gate transcript re-hash

`sha256sum evidence/p4-full-suite-cdc4491-2026-10-26.txt` = `7feaa2f1a1a1be34fd92d6b29d848057f5bc1c7b493e606162f4523d410ca330` — **MATCH**, not a blocker. I consumed the orchestrator's run (C-25); I did not rerun the suite.

## C-18 ruling (DDR §B row 4) — ruled: SATISFIED (the R1 reading)

Each multi-arm AT realises in **exactly one primary on-disk node driving the whole named chain**, and its extra arms are **contract-named supplements of that same chain**: the arms are named inside the AT's own definition (`01b-acceptance-design.md:31-266` — the "Boundary: zero-node map / 87-col arm", "Hostile-descriptor arm", "Out-of-view arm", "LF/TAB arm" clauses), not bolted on after the fact. I verified on disk that every primary and supplementary node the Layer-B table names resolves to a `def`: AT-130 `test_at130_matrix_opens_on_the_honest_skeleton` (+ `test_at130_87_column_boundary`, `test_at130_zero_node_map_boundary`) · AT-131 `test_at131_lens_summary_hop_counts_and_dimming` (+ `test_at131_87_column_boundary`) · AT-134 `test_at134_hostile_payload_on_the_live_surface` (+ `test_at134_lf_tab_payload_renders_on_one_row`) · AT-137 `test_at137_the_window_follows_the_cursor_at_87` (+ the five `test_at137_*` sweep arms) · AT-141 `test_at_141_c_chain_density_on_an_hlr` (+ the `three_level_map()` fixture arm) · AT-145 `test_llr_rvh_1_1_at_145_relation_rows_beside_tree_rows` (+ the no-descriptor and hostile-name boundaries) · AT-147 `test_llr_rvh_3_1_at_147_derived_row_opens_via_default_descriptor` (+ the missing/corrupt-canon boundaries) · AT-148 the host arms of `tests/test_relmap_shell.py` (+ the review F1/F2 arms). C-18's purpose — no AT unrealised, none ambiguous — holds; I adopt the R1 `ddr-qa.md` OP-2 recommendation verbatim: accept, and restate the rule as "every AT resolves to at least one node, and the AT id is recoverable from each node's name" — with one gap, finding F-2 below.

## Signed ledger re-verification (DDR §B row 5)

Post collect re-run by me (executor: this reviewer, 2026-10-26): `pytest -q -p no:cacheprovider --collect-only tests/` → **`4231/4255 tests collected (24 deselected)`** — equal to the record and to the gate transcript's `4226 + 2 skipped + 3 xfailed`. The record's per-file A counts (33+43+30+27+15+14+7+7+6+6+18+2+2+1+1) sum to **212**. The renamed-4 explanation verifies against the collect: `test_every_cited_test_identifier_exists` and `test_every_path_line_citation_resolves` now carry `[gaps.py0]`/`[gaps.py1]`/`[screen.py0]`/`[screen.py1]` — the corpus gained a second `gaps.py`/`screen.py` basename (`mapper/relmap/gaps.py` beside `mapper/screens/relmap/gaps.py`; `screens/relmap/screen.py` beside `screens/map/screen.py`), so the bare `[gaps.py]`/`[screen.py]` ids of the base no longer exist and their renamed counterparts sit inside A. **Named limit (finding F-3):** the base side (4023, and the D=4/A=212 split) was collected by the dev-flow worker on a clean detached worktree of `867dfd7` that no longer exists; per my scope I did not re-derive it, so the base side rests on the worker's collect, not on a transcript I could re-run.

## Mutation control C-2 — my own battery (3 mutants, all KILLED)

File under test for all three: `mapper/screens/relmap/gaps.py`, pristine sha256 `f340bddd00ed66aee19894cf05b37da4f2ffccb27c6a741de6976e8e90c3411f` (BEFORE, all arms). Pristine copy kept in a scratch dir outside the repo, deleted after. Runs by me on this tree; restore sha256 verified EQUAL after every arm; final `tests/test_hook_line_bound.py` **7 passed**; `git status --porcelain mapper/` empty. Line numbers refer to the pristine file.

| Mutant | Site | RED node ids | Restored = BEFORE? |
|---|---|---|---|
| M-QA-1 window clamp pinned (`off = max(0, min(n - slot, at - slot // 2))` → `off = 0`) | `gaps.py:110` | `test_at137_the_window_follows_the_cursor_at_87` · `test_at137_window_follows_the_cursor_and_declares_every_cut_row` · `test_at137_cap_scale_100k_map_renders_at_118_and_87` · `test_rvg_1_2_total_chip_counts_the_rendered_rows` · `test_rvg_2_3_budget_spent_declares_not_computed` (5 failed, 547 passed) | EQUAL ✓ |
| M-QA-2 ranked order reversed (`range(off, end)` → `range(end - 1, off - 1, -1)`) | `gaps.py:270` | `test_rvg_1_1_rendered_order_is_the_ranked_order` · `test_rvg_1_3_row_anatomy_at_full_width` · `test_rvg_1_3_the_cursor_highlights_the_ranked_row` · `test_at137_the_window_follows_the_cursor_at_87` · `test_at137_window_follows_the_cursor_and_declares_every_cut_row` · `test_at137_cap_scale_100k_map_renders_at_118_and_87` (6 failed, 546 passed) | EQUAL ✓ |
| M-QA-3 by-kind member order reversed (`idxs[:take]` → `idxs[::-1][:take]`; selection narrowed to `test_relmap_gaps_view.py` + `test_relmap_shell.py`, the files carrying the by-kind chain) | `gaps.py:304` | `test_rvg_1_5_by_kind_bands_match_the_membership_oracle` · `test_rvg_1_5_member_rows_keep_their_global_ranks` · `test_at136_by_kind_through_the_app` (3 failed, 67 passed) | EQUAL ✓ |

No arm stayed GREEN — the ranked-order-equality, window-follows-cursor and by-kind-oracle claims central to the Layer-B QA rows are not vacuous. (M-QA-3's narrowed selection is disclosed in the table; the mutant is local to the gaps renderer, so no other file can redden.)

## Executor attributions (C-25 scan)

No row claims a run its executor did not make. The one gate run is the orchestrator's; the increment mutation batteries are the batch workers', with every cited transcript present on disk under `evidence/`; the base/post collects, the skip probes and the UX walkthrough are the dev-flow worker's and are declared as such; the independent reviews exist as `evidence/review-inc00*.md`. The qa-reviewer checklist's authorship (worker under standing authorization) is disclosed in the record, as R1 required.

## Escaped-bug regressions (state: `inspection` — I did not re-break them)

Both fixes are value-discriminating pins, confirmed by code read: (1) the census amendment pins `assert len(sites) == 94` at `tests/test_darkside_census.py:516` with the 12 sites itemised at `:318-510` — reverting `2e83cf6` reddens; the seat words and the 13 `relmap` rows are pinned in `tests/test_inc9.py:392` (`CHROME_LEXICON`) and `:689-733` (`DECLARED_ADDED`). (2) the privacy guard reads the account name from `$USERNAME` at run time (`tests/test_no_operator_paths.py:120-132`), so any profile segment in any tracked file turns it RED — the discriminator is the guard itself. The evidence hole this leaves is finding F-1.

## COND-QA-1…5 — dispositions (each re-read at the named artifact line, not the DDR summary)

| # | Disposition | What I re-read |
|---|---|---|
| COND-QA-1 | **discharged — confirmed** | `design/design-proposal.md:108-109,190` names `mapper/relmap/adapter.py:29` as the fourth live consumer of the old paths and declares the 4+1 Inc-1a/1b split; `PLAN.md:133-134` carries both rows; packets 001a/1b + the AT-150 census close it |
| COND-QA-2 | **discharged — confirmed** | `03-increments/increment-002.md:11,53,99` — the whole-seat pin `test_key_dispatch.py` re-runs in Inc-2's trio (`188 passed` with both seat pins), the pin not moved |
| COND-QA-3 | **discharged — confirmed** | `03-increments/increment-004.md:327-349` records the 10× budget as a packet measurement; `evidence/p3-inc004-measure.txt:4-9` carries it (median 0.005 s, budget 0.048 s); no committed assert reads a clock |
| COND-QA-4 | **discharged — confirmed** | `tests/test_relmap_shell.py:143-155` — the counting wrapper captures the real function (`:149`) and calls it (`:153`), replacing nothing; the derive-args arm at `:168`; `increment-002.md:249` and `increment-006.md:258-259` record the discharges |
| COND-QA-5 | **discharged — confirmed** | `tests/test_relmap_sheet.py:131-132` `three_level_map()` (US-T → HLR-T → LLR-T) and the stacked arms `:557-575` rendering `↑2` + the note flip; `increment-005.md:129` (M-RVS-9 killed by the synthetic arm, the live one-hop arm explicitly NOT the kill) and `:255` |

## §F D-1 — ratified: TWO hatch chars (the normative Statement wins)

`mapper/screens/relmap/sheet.py:181-183,189-191` paints `╌╌ +NN more upstream/downstream at hop 2` — two hatch chars; the normative Statement (`01-requirements.md:636-641`, per `increment-005.md:256`) says two, and LLR-RVS.2.4's empty-line grammar agrees; the committed tests pin these exact lines. The draft-time verification's "four hatch chars" was a draft artifact citing the prototype PNG, not the norm. `increment-005.md:238,256` (review-inc005 F3) asked the DDR to ratify two so the ambiguity does not resurface at the join — **I ratify two**, matching the DDR draft's §F D-1.

## Findings

| # | Sev | Finding | Needed to close |
|---|---|---|---|
| F-1 | MAJOR | **No stored pre-fix RED for the two escaped regressions** (the R1 F-1 analogue). Run 1's three census failures and run 2's privacy failure have no transcript; their identities live in `PLAN.md:21` and `05-postmortem.md`, and the A-110 pre-image survives only as the parent of `cdc4491`. The post-fix pins are value-discriminating (verified by inspection above), but a "pre-fix RED" with no artifact is asserted, not shown. | Reconstruct cheaply and store under `evidence/` with a named executor: the three census nodes on a detached checkout of `2e83cf6^`; the A-110 node on the `cdc4491` parent tree (both RED by construction). Or record the accepted gap with the operator's ruling at the seal. Owner: dev-flow worker / orchestrator. |
| F-2 | MINOR | **AT-148's supplementary host arms are not id-greppable** (the R1 F-7 analogue). `test_llr_rvh_3_2_open_derives_once_and_r_rederives` (`tests/test_relmap_shell.py:143`), the `test_review_f1/f2_*` arms and the `test_llr_rvh_5_*` arms carry no `at_148` marker; every other multi-arm AT's arms do. The AT→node mapping for the batch's most multi-arm AT is table-maintained, not mechanical. | Add the id to the arms' names/docstrings, or ride a BACKLOG id — cosmetic. Owner: software-dev. |
| F-3 | MINOR | **The ledger's base side is not re-derivable on this tree** (named limit, as the record itself names for the superseded runs). Post side reproduces exactly (`4231 collected (24 deselected)`, run by me); A's per-file counts sum to 212 and the renamed-4 explanation verifies in the collect; but base 4023 and the D=4/A=212 split rest on the dev-flow worker's collect on a removed clean worktree of `867dfd7`. | Store the base collect's node-id list with the batch records at the seal (one file), or accept as a named limit. Owner: dev-flow worker. |

## Verdict: approved with conditions

Coverage, balance, attributions, conditions and both deviations hold under re-reading; no blocker. One condition gates the seal:

1. **F-1** — store the two escaped-regression pre-fix REDs (executor named) or record the accepted gap with the operator's ruling.

F-2 and F-3 are minor and may ride BACKLOG ids; they do not gate the seal. (Record vocabulary per the DDR: `approved` / `approved with conditions` / `rejected`.)
