# Independent review - Increment 002 (relmap gaps), commit 121e653

Reviewer: code-reviewer (not the author). Read-only toward the diff; only gaps.py was mutated, each time restored and hash-verified.

## Scope reviewed
`mapper/relmap/gaps.py` (131 lines, read in full), `tests/test_relmap_gaps.py` (arms read for the edge/type filters), the comment-only `model.py` docstring hunk, ledger `.44`-`.51`, LLR-RMG.1.1/.1.2/.1.3, QuickMap oracle `gaps.py`, evidence hashes.

## Verified
- `mapper.__file__` resolves inside the worktree. Targeted run (gaps + model + profile): 119 passed (evidence state: executed).
- gaps.py sha256 `eeb3b1cd...` equals the packet; the four `inc2-*.txt` digests equal the packet's (executed).
- Generic over `map.profile.gaps`: no kind, edge or gap literal; only `ACTIVE`, `QUALIFIER`, `SEVERITIES`. Activation is `all(kind in m.sourced for kind in row.needs)`. Eligibility is exact `== "active"`. Reach is taken only through `m.reach`, so the visit budget is shared. No `down`/`up`/`_reach_memo`/`visits` read in the file. `reach_not_computed` is counted when `reach` returns `None`, and those gaps rank with 0. `rank_gaps` returns all gaps ranked plus the count (the author's issue 1: consistent with LLR-RMG.1.3 "returns (ranked, reach_not_computed)" and ledger .51(2); acceptable, Inc-5 reads the first `limit`).
- Endpoint safety: `m.node(other)` cannot be `None` because `build_map` drops edges with unknown endpoints.
- model.py hunk: docstring only, no code line changed (git show 121e653). Wording now matches the code.
- Ledger .44-.51: each carries requirement, date, test and mutant; every test named in .51 exists. Back-pointers in LLR-RMG.1.1/.1.3 cite .51. Source files 1/4 (gaps.py), model.py declared comment-only. Traces complete for HLR-RMG.1 / LLR-RMG.1.1-.3.

## Findings

### F1 - MAJOR - the edge-type filter in `_lacks` is untested (surviving mutant)
- Where: `mapper/relmap/gaps.py:61-62` (`if e.type != row.edge: continue`).
- What: Mutant D (replace the condition with `e.type == "x"`, so every edge of any type counts as a link) leaves all 50 tests GREEN. The packet's claim "15/15 killed" does not cover the conjunct "edge is of the row's type".
- Why it matters: this is the core of every `lacks_in` / `lacks_out` row. Without it an LLR that has only a `refines` edge from its HLR would count as verified, and a US with any incoming edge would count as covered. A regression would hide real HLR/LLR/US gaps while the suite stays green: a false-confidence test set. The author's own load-bearing-emptiness table lists conjunct mutants but names no type-filter mutant.
- Fix: add an arm to `test_llr_not_verified_positive_and_negative` (or a new test), e.g. nodes `HLR1`, `LLR1`, edge `Edge("HLR1","LLR1","refines")`, `sourced=("HLR","LLR","TC")`: assert `LLR1` IS reported as `LLR NOT VERIFIED`. Add the symmetric case for `lacks_out` (a TC with an outgoing edge of another type is still an ORPHAN TC if the profile allows one). Re-run mutant D and show it RED.

### F2 - MINOR - catalogue row flags are silently ignored by two patterns
- Where: `gaps.py:_cycles` and `_unevidenced` (lines 42-47, 70-76); the module docstring says only "eligible row".
- What: `eligible`, `open` and the `unparsed` qualifier are applied only in `_lacks`. A profile row with `pattern="edge_unevidenced"` and `eligible=True` fires on retired nodes with no error. No shipped row does this, and `Profile.__post_init__` does not refuse it.
- Fix: one sentence in the module docstring ("`eligible`/`open` and the qualifier apply to `lacks_*` rows only"). A construction refusal is optional.

### F3 - MINOR - `_fill` would raise KeyError on a template slot the pattern does not supply
- Where: `gaps.py:34-35` (`values[m.group(1)]`).
- What: e.g. a `lacks_*` row whose sentence uses `<src>` raises a bare `KeyError` at detection. Shipped templates are consistent, so this is latent only.
- Fix: leave the slot text as is (`values.get(name, m.group(0))`) or validate slots in `Profile.__post_init__`.

### F4 - MINOR - verification names drift from the contract
- Where: LLR-RMG.1.3 "Executed verification" names `::test_rank_limit_none`; the tests are `test_rank_limit_none_ranks_every_band` and `test_rank_limit_none_stays_inside_the_budget`.
- Fix: update the LLR text to the exact node ids, or rename a test (Inc-5 traceability checks are by id).

### F5 - MINOR (style) - long lines
- `gaps.py` `rank_gaps` docstring first line (about 130 chars) and the `model.py` docstring line "traversal ... nothing is memoised for" (about 105 chars). Wrap.

## Mutants (own choice, run on tests/test_relmap_gaps.py, restored after each; final sha256 `eeb3b1cd...` identical to the start, and `git diff` showed the file back at the committed content)
| Id | Mutation | Result |
|---|---|---|
| A | `before < limit` -> `before <= limit` (band boundary of the bounded ranking) | KILLED: `test_rank_computes_reach_only_for_the_bands_needed_to_fill_the_limit` |
| B | qualifier threshold `unparsed > 0` -> `> 1` | KILLED: `test_gap_sentence_qualified` |
| C | peer test inverted (`!=` -> `==`) | KILLED: 3 tests (`test_hlr_without_llr_positive_and_negative`, `test_peer_kind_restricts_the_linking_edge`, `test_withdrawn_only_llr_is_not_a_gap`) |
| D | drop the edge-type filter in `_lacks` | SURVIVED: 50 passed (F1) |

## Evidence states
Re-hash of gaps.py and the four transcripts: executed, equal. Targeted test run: executed, 119 passed. Mutants A-D: executed. Layer B (AT-118, AT-125): n/a, lands at Inc-5. Packet 4b `Independent review` was "pending" before this report.

## Verdict: iterate
`BLOCK-UNTIL: F1` (one added test arm, then re-run mutant D RED). Everything else is correct against LLR-RMG.1.1-.3, and F2-F5 are non-blocking nits that can be taken in the same pass. Re-read of the added arm and a re-run of mutant D are owed to discharge it; this verdict authorises nothing until then.

Text for packet 4b cell: `code-reviewer · iterate (BLOCK-UNTIL: F1) · F1 MAJOR open: surviving mutant D (edge-type filter in _lacks untested); F2-F5 MINOR`.
