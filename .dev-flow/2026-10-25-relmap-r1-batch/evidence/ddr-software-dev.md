# DDR review, software-dev lens: `2026-10-25-relmap-r1-batch`

Reviewer: software-dev (independent; authored none of it). Changed nothing in the tree except transient mutants, restored and hash-verified (see NOTE). Tree: worktree `wt-r1`, HEAD `e6dc5c5`, code diff `194f885..HEAD -- mapper/ tests/`. Read: DDR draft, PDR, PLAN "P3 follow-up", `04-validation.md`, all `mapper/relmap/*.py`, the `reqharness/audit.py`, `store.py`, `yamlscan.py`, `app.py`, `search.py` diffs, the two test-guard diffs. Packets 001-005 were read through the DDR's and the validation's citations of them, not line by line.

## Verdict: approved with conditions

The code is small, readable and matches mapper conventions (frozen dataclasses, typed errors with fixed cause text, iterative traversals, node/edge caps from `osopen`). Its tests killed 3 of my 4 non-equivalent mutants. No blocker. Two conditions below are cheap and should land before the seal or be filed with an id.

Baseline run (the mandated command): `395 passed, 2 skipped in 48.09s`.

## Findings

| Sev | Where | Finding |
|---|---|---|
| MAJOR | `mapper/relmap/adapter.py:177` (test gap) | `unknown_status` counts `final.nodes` (kept nodes only, ledger `.61`). My mutant M3 (count over all input `nodes`, so a duplicate or unsafe-id row with an odd status is counted) survives the full relmap suite. `tests/test_relmap_adapter.py:237,288` never include an excluded row with an unknown status. The DDR row for `.61` is asserted, not pinned. Condition: add one arm (duplicate id with status `done`; the count must ignore it). |
| MINOR | `mapper/relmap/adapter.py:145,171` | B-146 double `build_map`. Cost is measured (~1 s at 100k rows) and the reason is real: edges must join only kept nodes, or they surface as `unknown endpoint` problems, and `unparsed` is only known after the edges. Acceptable for R1. The cure when R2 multiplies it is to let the builder take a node transform, or to split `validate_nodes` out of `build_map`; not to re-implement the duplicate and unsafe-id rules in the adapter. Residual-risk entry E.2 is accurate. |
| MINOR | `mapper/relmap/descriptor.py:134-141` | Cause K5/K6/K7 is derived by `str(exc).startswith("file exceeds" / "file looks binary" / "file is not UTF-8")` against `osopen` message text, coupling to another module's wording by prefix. Tested through real files, so a reword fails loudly, but it is the one place that classifies by message. Preferred: a `kind` attribute on `ContentReadError`. Not for R1. |
| MINOR | `mapper/relmap/descriptor.py:85-97,196`, `adapter.py:129` | `Descriptor.profile` and `Descriptor.canon` are always `REQHARNESS.name` / `CANON_NAME` (K13/K14 refuse anything else), so they are dead data today. `structure_lines` also derives the canon once with `default_descriptor()`, never with the loaded descriptor. Correct while the canon is fixed; the first non-default canon must revisit both. Frozen D2 names, so defensible. |
| MINOR | `mapper/relmap/descriptor.py:172,175,183` | `isinstance(x, str) and x == "..."` is redundant (`x == "..."` suffices). Harmless. |
| MINOR | `mapper/relmap/audit.py:234-235` and `descriptor.py:214-215` | The K5 rendering `exceeds the <limit> byte limit` exists twice (`_cause_text`, `refusal_line`). A reword must touch both. |
| MINOR | `mapper/relmap/audit.py:243-249,263-265,325`, `gaps.py:441` | Defensive branches for states profile validation makes impossible: `kinds.get(node.kind, 0)`, `types.get(...)`, the `sorted(k for k in counts if k not in PROBLEM_KINDS)` tail, `by_severity.get`. Nothing exercises them. Against the "no handling for impossible scenarios" rule; leave or trim. |
| MINOR | `mapper/relmap/adapter.py:129` | The canon byte cap is `reqharness.derive.LIMIT_ROLES_YML_BYTES`, a constant named for another file. Works; the name misleads the next reader. A one-line alias with a comment would do. |
| MINOR | `mapper/reqharness/audit.py:380-381,433` | A generic hook's line has no length bound (the count is bounded at 1000, the `verdict: ` prefix is guarded). Already B-147 and DDR §E.3. Make sure B-147 lands before any second hook caller. |
| MINOR | `tests/test_repair_artifact_claims.py` (new table and last lines) | The exception table is keyed on `(artifact.name, token)`, a bare basename. Today the name is unique in the tracked tree (checked: one `04-gate-findings-disposition.md`), so no mis-resolve is possible. The file also now ends with a stray blank line. |
| MINOR | `mapper/relmap/model.py:140-166,208-227` | `RelMap` is called immutable but holds mutable `_visits` and `_reach_memo`. Documented in the module docstring and tested, so a declared exception, not a defect. Two threads sharing one map would race on the budget; nothing in R1 does. |
| NOTE | working tree | After my mutant restores, `git status` shows `M` on 4 `relmap` files. Cause: `core.autocrlf=true` made `git checkout --` write CRLF; I converted back to LF and the SHA-256 of all 7 files equals the pre-run hash (`__init__`, `adapter`, `audit`, `descriptor`, `gaps`, `model`, `profile`: OK). `git diff --ignore-cr-at-eol` is empty. Only the index stat is dirty, the bytes are as found. Three untracked `ddr-*.md` files belong to the other reviewers. |

Nothing found in: error-handling consistency (every refusal is a fixed string, never `str(exc)` of repository content, the hook never changes the exit code), hook bounding (`islice(..., LIMIT + 1)` is lazy and correct), the `verdict: ` forge guard, the `yamlscan` extraction (byte-identity golden present, typed error deliberately not a `ValueError`), osopen allow-list amendments landed with the imports.

## Mutants (mine, in `mapper/relmap/*.py`; full `tests/test_relmap_*.py`)

| # | File and change | Result |
|---|---|---|
| M1 | `gaps.py` `if limit is None or before < limit` to `<=` | KILLED: `test_relmap_gaps.py::test_rank_computes_reach_only_for_the_bands_needed_to_fill_the_limit` |
| M2 | `audit.py` `unlinked[:UNLINKED_SHOWN]` to `[:UNLINKED_SHOWN + 1]` | KILLED: `test_relmap_audit.py::test_notes_come_in_the_stated_order_and_the_unlinked_line_shows_five_ids` |
| M3 | `adapter.py:177` count `unknown_status` over `nodes` instead of `final.nodes` | **SURVIVED** (395 passed). Finding MAJOR above |
| M4 | `descriptor.py` `startswith("file looks binary")` to `startswith("file looks")` | SURVIVED, equivalent (no other `osopen` message begins `file looks`); not counted against the tests |
| M5 | `audit.py` `len(texts) > MAX_NOTE_LINES` to `>=` | KILLED: `test_note_cap_is_ten_with_an_overflow_line[10-False]` |

Restore: `git checkout --` after each, then CRLF to LF, then `sha256sum -c` against the pre-run hashes: all 7 OK.

Test quality overall: assertions are on exact strings and counts, boundaries are tested at cap and cap+1, the byte-stable test is mutant-proven. M3 is an exception to the "100 of 100 killed" claim, which describes the batch's own battery, not all behaviour.

## Opinions on the open points

- **OP-2 (C-18, multi-node ATs).** Keep as built. The intent of "exactly one on-disk node" is that an AT is not realised twice by independent proofs that can drift. AT-121 (one parametrised function plus a controls function) and AT-122 (six arms over one run) are one observation each, split so each arm can go RED alone; folding would let one failing arm hide the others. The Layer A stand-ins are labelled as such in their docstrings. Condition: the seal text says "one realisation, several assertions", with §B row 4 as the map of the primary Layer B node per AT.
- **OP-7 (first failing transcript not stored).** Accept. The three failures are re-derivable from the DDR's test ids and causes, the fixes carry executed mutants (ledger `.69`/`.71`), and the green run is stored with its hash. Attach the transcript only if it still exists in the session log; do not re-run the pre-fix tree to produce one.
- **OP-8 (Python 3.10 `not-run`).** Accept the AST floor guard and the banned-name census as a proxy, conditionally: the seal says "floor unproven on 3.10" and B-148 stays open with an owner. The changed code uses no `match`, no `except*`, no 3.11-only stdlib names I could find, and annotations are behind `from __future__ import annotations`, so the proxy is reasonable.
- **OP-10 (contract wording drift, B-149).** BACKLOG suffices. The drift is in note wording; the shipped behaviour is covered by executed tests and recorded as G-004. Amending a sealed contract before the seal adds nothing the DDR does not already record. Condition: B-149 states that the shipped behaviour is normative, so nobody "fixes" the code toward the old wording.

Also, briefly: OP-6 (`_CITATION_EXCEPTIONS`): keep the declared table; it is explicit, its "still needed" arm retires stale rows, and it leaves the guard's rule alone (option A changes a guard's semantics). OP-11 (`cut` in `model.py`): move it before R2 freezes more names. It is a 5-line pure function that `descriptor` and `audit` import through the graph module; a leaf module is cheaper now than after R2's views import `model` for presentation. Not a seal condition.

## Residual risk list completeness (DDR §E)

Complete for what was found, with three additions: (a) M3, `unknown_status` over excluded rows is unpinned; (b) `Descriptor.profile`/`.canon` and the single default-descriptor derivation are constant by K13/K14 and must be revisited at the first non-default canon; (c) the `ContentReadError` prefix coupling at `descriptor.py:134-141`. Entry E.2 (double build) is accurate and its trigger ("before R2's views multiply it") is the right one.

## Conditions for approval

1. Add the missing arm for ledger `.61` (an excluded row with an unknown status is not counted), or record M3 in §E as a known unpinned behaviour with a backlog id.
2. Add items (a)-(c) above to §E, or file them in BACKLOG.
