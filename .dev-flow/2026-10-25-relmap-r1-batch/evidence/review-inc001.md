# Code Review — Increment 1 (relmap-r1): profile table and typed multi-parent read model

Reviewer: `code-reviewer` (independent of the author). Commit 75cf7f4 in the batch worktree. Read-only toward the diff; only this file written.

## Scope reviewed
`mapper/relmap/{__init__,profile,model}.py` in full; tests `test_relmap_{profile,model,isolation}.py` (node list and the arms the mutants touched); packet `increment-001.md`; LLRs RMP.1.1/1.2/2.1, RMM.1.1-1.3, 2.1/2.2, 3.1; PDR conditions C1 (shared budget, "not computed") and D-1 (tripwire + int memo).

## Checks
- `mapper.__file__` resolves inside the worktree (executed). Targeted run, 3 files: **127 passed** (the packet's 132 includes the 5 osopen-guard nodes) (executed).
- Evidence re-hash (executed, `sha256sum`): inc1-green-first `3d85b30b…`, inc1-guards `b46995a0…`, inc1-red-code-absent `25fdbe2c…`, inc1-red-mutants-battery `b8e59c14…` — all four equal the packet's §4 digests. Source digests equal the packet's restore digests (`2a759d01…` profile.py, `6ebcf7ea…` model.py).
- SOURCE files 3/4 (`__init__.py` zero bytes, `profile.py`, `model.py`): within cap.
- Trace: every LLR named in the packet header has code in `model.py`/`profile.py` and a named test node; the §2 table traces match the contract. No orphan.
- Python 3.10 by reading: `from __future__ import annotations` makes `X | None` and `tuple[...]` annotation-only; no `match`, `tomllib`, `StrEnum`, `Self`, `except*`, `itertools.batched`; `deque`, `collections.abc.Iterable`, `dataclasses.replace` are 3.10-safe. No finding.

## Correctness (against the LLRs)
- Multi-parent graph, input order kept, immutable `RelMap`, six problem kinds, nothing raised except the cap error (`model.py:257-260`, checked before any validation): correct.
- Direction: `downstream` selects origin/target once (`model.py:303-308`); `up` is the exact mirror of `down`; both in edge input order. Correct.
- Tarjan (`model.py:77-128`): iterative, low-link update on pop before the root test, self-loop recognised, members and components in input order. Correct by reading and by the 3-node, 2-disjoint, self-loop, ring-100k tests. `in_cycle` correct, including the edge between two cycles (`:301`).
- `reach` (`:207-226`): BFS with a `seen` set, int memo, ONE per-map counter; budget checked before each expansion, abandoned traversal memoises nothing and returns `None`; a memo hit draws nothing. Matches C1 and D-1. Visits spent on an abandoned traversal stay spent (sticky exhaustion), which is the stated contract.
- Caps +/-1 tested for nodes and edges.

## Findings

### F1 — Problem subjects carry unbounded raw ids  [MINOR]
- **Where:** `model.py:270` (`Problem("unsafe id", n.id)`), `:281` (`f"{e.src}->{e.dst}"`).
- **What:** the subject of an `unsafe id` problem is the raw id, which by definition may be empty, over `ID_MAX`, or contain control characters; an edge subject concatenates two such raw values. The model stores them verbatim.
- **Why it matters:** safe only because Inc-5's `format_structure` is contracted to cut and escape; a map held by any other caller (R2 strip, log) holds a 10 MB string per problem. Not a defect of this increment's contract (AT-124 prints no excluded value).
- **Fix (optional):** store `cut(...)` for the subject, or add one sentence to the `Problem` docstring: "subject is unescaped, uncut input; the formatter cuts and escapes".

### F2 — Docstring calls `down` "the one counted seam", but `down` counts nothing  [MINOR]
- **Where:** `model.py:14`.
- **What:** the counter is incremented inside `reach` (`:220`); `down` is only the single adjacency read that the test tripwire wraps. A reader could take `down` as the budget seam and add an uncounted traversal in Inc-2.
- **Fix:** reword: "every traversal expands a node by calling `down`, and `reach` counts each expansion; `rank_gaps` must go through `reach`".

### F3 — Duplicate edges kept silently  [MINOR]
- **Where:** `model.py:280-290`.
- **What:** two identical `(src,dst,type)` edges both stay in `edges`, `up` and `down`. `reach` is unaffected (distinct nodes), `neighbourhood` unaffected (set); only edge counts (`edges=196` in AT-117) would double. The contract has no problem kind for it, so keeping them is the literal reading; Inc-4's deriver emits unique pairs from the canon.
- **Fix:** none now; record as a stated silent choice next to item 4 of packet §6.

### F4 — `Profile.__post_init__` does not validate `EdgeType.evidence` or duplicate names  [MINOR]
- **Where:** `profile.py:56-72`.
- **What:** `evidence` is a free string (`"none"|"optional"|"required"|"graduated"` only in a comment); two edge types of the same name make `types = {t.name: t ...}` in `build_map` silently keep the last. `REQHARNESS` is the only profile in R1 (R5 adds `lineage`), so nothing misfires today.
- **Fix (optional, when R5 lands):** refuse an `evidence` outside the four words and duplicate type names, mirroring the severity refusal the author already added.

### F5 — `sourced` is not checked against `profile.node_kinds`  [MINOR]
- **Where:** `model.py:316`.
- **What:** `frozenset(sourced)` accepts any string; a typo yields a kind that is "sourced" with no nodes, so a `needs` row fires on an empty kind (`US WITHOUT AT` needs `US` sourced). The contract is silent. Inc-4 builds the set from constants, so low risk.
- **Fix:** none required; state it as a contract-silent choice or intersect with `kinds` (one line).

No BLOCKER. No MAJOR.

## Mutants of my own
Applied one at a time in `model.py`/`profile.py` only, run on the 3 targeted files with `-x`, restored from the in-memory original, file sha256 re-verified equal after each.

| # | Mutation | Result |
|---|---|---|
| M1 | `reach`: budget exhausted `return None` -> `break` (partial count returned and memoised) | KILLED: `test_reach_budget_per_row` (assert `None` is seen) |
| M2 | `in_cycle`: `comp_of.get(e.dst) == comp_of[e.src]` -> `True` (any edge leaving a cycle member flagged) | KILLED: `test_cycle_three_nodes_flags_each_cycle_edge_and_still_loads` |
| M3 | duplicate-id branch disabled | KILLED: `test_problem_duplicate_id` |
| M4 | `neighbourhood` runs one hop too many | KILLED: `test_neighbourhood_hops` |
| M5 | `profile.py` `verifies` loses the `TC->HLR` pair | KILLED: `test_edge_table` |

5/5 killed, 0 survived, 5/5 restored (hash equal). M1 is killed only by the 1.6 s per-row arm; that is correct (it is the arm that exercises exhaustion), not a weakness.

Tests encode intent: the arms name the failure they guard (tripwire on `down`, int-memo, no-recursion at the 100,000 cap, planted violations for every census, synthetic `LOOPY` profile for the cycle case reqharness cannot form). No vacuous test found among those read.

## Opinions on the author's open items (packet §6)
1. **`cut` = 119 chars + `…` (120 total): agree, keep.** AT-129 asserts "<= 120 characters before escaping and ends `…`", and 120 total satisfies it; the other reading (120 + `…` = 121) would break that AT. The boundary test 120/121 holds either way. One wording slip in the numeric threshold of the audit-lines LLR ("a 121-character id prints 120 characters and `…`") reads as 121 total; the ledger note should say "120 characters in total, the last being `…`", so Inc-5's golden is not minted off the wrong count.
2. **Memo arm samples every 7th row: accept.** Full per-row calls on a 2,000-node chain cost 2,001,000 expansions (1,000 over budget), so the LLR's literal text is unsatisfiable; the M-RMM-10 kill (set-valued memo) needs only that retained values be `int`. Amend the LLR wording to "a 2,000-node chain, sampled rows" (the author's proposal).
3. **No stdlib-ban census for `subprocess`/network/repo-write in relmap: defer to Inc-3, agree.** LLR-RMP.2.1 permits the stdlib without exception and the package does no I/O at Inc-1 (the only non-stdlib import is `mapper.osopen` constants). Add it with the first file-touching descriptor via a ledger entry; track it so it is not lost (backlog line at batch close if Inc-3 does not fold it).
4. **Silent-contract choices: all acceptable.** Subject `<src>-><dst>`; duplicate only against accepted ids; cycles on the authored `src->dst` graph (sound because premise 5 makes the kind graph a DAG over those pairs, and `reach`/`neighbourhood` use the change-direction graph separately); severity refusal in `Profile` (stricter than contract, harmless, tested). Record them in the ledger as readings, plus F3 and F5.

## Convention and simplicity
Matches mapper style (frozen dataclasses, `from __future__ import annotations`, typed returns, short module docstrings naming the LLR). No speculative generality; the only helper (`_cycles`) is single-use but too large to inline. No duplication of an existing util found (`osopen` caps are imported, not redefined).

## Verdict
- [x] OK to advance — approve-with-nits (no BLOCKER/MAJOR; F1-F5 MINOR, optional; file the ledger notes for items 1-2 before Inc-5 mints goldens)
- [ ] BLOCK-UNTIL
- [ ] Block

Evidence states: tests run `executed`; mutants `executed`; hash checks `executed`; Python 3.10 floor by reading `executed` (by reading only; a real 3.10 run is `not-run`, as the packet states); security and suite-wide gaps `n/a` (other lanes).

§4b cell text: `code-reviewer` · approve-with-nits · no HIGH raised (F1-F5 MINOR); 5/5 own mutants killed and restored by hash.
