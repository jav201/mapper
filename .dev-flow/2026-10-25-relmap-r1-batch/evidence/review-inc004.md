# Review - Increment 4 (relmap adapter, snapshot fixture, adapter tests) - code + security lenses

Reviewer: `code-reviewer` (independent of the author). Scope: commits f3cded2 and ab412fc on the batch worktree
(`mapper/relmap/adapter.py` 178 lines, `tests/test_relmap_adapter.py`, `tests/fixtures/relmap/REQUIREMENTS.snapshot.md`,
`.gitattributes`, `docs/ARCHITECTURE.md` row, evidence). Diff and source read in full. Tests only, read-only toward the diff.

**Verdict: approve-with-nits.** No BLOCKER, no MAJOR. One MINOR test gap (a surviving mutant of mine) and several notes.

## Checks (state)

| Check | State | Evidence |
|---|---|---|
| `mapper.__file__` inside worktree | executed | `...\wt-r1\mapper\__init__.py` |
| Targeted tests | executed | 187 passed (adapter + gaps + isolation), 7.1 s |
| Read-only: one read, only `read_repo_text(repo/descriptor.canon, LIMIT_ROLES_YML_BYTES)`; no write, no subprocess, `us_canon`/`at_table` never opened | executed (read + `test_readonly` tally of `os.open`/`builtins.open`/`io.open`/subprocess, tree hash) | adapter.py:128-131; imports are `ast, re, dataclasses, pathlib` plus mapper modules only |
| Error mapping: `RepoReadError` -> `CanonUnavailable(cause, limit)`, `from None`, no path or exception text | executed (K1-K7 arms, `str(err)==CAUSE[Kn]`) | adapter.py:130-131 |
| D-1: candidate = `HLR-` + id minus last dotted segment; edge only when the candidate is a kept HLR; else `unlinked`; never a shorter prefix | executed (table, `test_an_unlinked_llr_is_never_attached_to_a_prefix`) | adapter.py:84-89,150-157 |
| Reported rows: note only, no node, no edge, id read back with `ast.literal_eval`; id-less report -> generic note | executed | adapter.py:68-76,161-168 |
| Qualified HLRs (`Node.unparsed`): starts-with and sibling-stem relations in one pass | read + executed; three mutants (below) | adapter.py:92-118 |
| Unsourced kinds inactive (`sourced = {HLR, LLR}`) | executed (`test_unsourced_kinds_...`; author's M-RMG-3b) | adapter.py:33,175 |
| Derived once: one read, one parse | executed (`test_canon_is_read_once_through_read_repo_text`) | adapter.py:128-132 |
| Snapshot = `git show e83e686:REQUIREMENTS.md` LF bytes | executed | base blob sha256 `b093c920...a25a` equals the fixture raw sha256 and the LF-normalised hash; 0 CR bytes in the fixture |
| Pin matches (constant, ledger `.36`, CRLF arm) | executed | `test_snapshot_sha256`, `_crlf_arm`, ledger cross-check green |
| PD-1 `-text` | executed | `.gitattributes:3` `tests/fixtures/relmap/** -text`; asserted by `test_gitattributes_keeps_the_fixture_bytes`; fresh-checkout transcript (LF and CRLF clones, 0 CR) read |
| Live-canon checks are invariants, no absolute pins | read | `test_live_invariants` asserts relations (`nodes+short+problems == counted ids`, `edges+unlinked == llrs`, edge src == D-1 stem), never counts; independent counter shares the first-`Id`-header rule |
| `cannot parse row for` tripwire | read | `test_report_line_shape_yields_id` (plain id, quote/backslash id, header-only report, trailing-text variant) |
| Evidence re-hash (8 transcripts) | executed | all 8 `inc4-*.txt` first-16 prefixes equal the packet table |
| <=4 source files | executed | 1 / 4 (`adapter.py`); test, fixture, config, doc outside the count |
| Traces | read | LLR-RMA.1.1 to .1.4, LLR-RMG.1.2, ledger `.36/.44/.48/.49/.50`, PD-1/D-2/D-4 named in packet 1 and 2; docstring cites HLR-RMA.1 and rule D-1 |
| Worktree clean after mutation | executed | `git status --short` empty after restores |

## Findings

### F1 - MINOR - the "HLR has a dot" guard in the sibling relation is not pinned by any test
- **Where:** `mapper/relmap/adapter.py:114` (`if "." in s:`).
- **What:** the contract limits the sibling relation to an HLR whose id has a dot. For a dotless HLR `s`, `s.rsplit(".", 1)[0] == s`, so removing the guard re-counts orphans the starts-with branch already counted (a reported `LLR-X.1` next to `HLR-X` would give 2, not 1). My mutant `if "." in s:` -> `if True:` SURVIVED (38 passed). The snapshot has no dotless HLR with a reported child and `test_unparsed_counts` has no such arm.
- **Fix:** add one arm to `test_unparsed_counts`: a canon with `HLR-X` and a pipe-bearing row `LLR-X.1`; assert `HLR-X` has `unparsed == 1`.

### F2 - MINOR (hand-off to Inc-5, no change here) - `Derivation.reported` carries raw, uncut ids
- **Where:** adapter.py:166 (`NOTE_UNPARSED_ROW.format(id=row_id)`); docstring lines 18-19.
- **What:** `parse_canon` accepts any `\S+` after `HLR-`/`LLR-`; `{id!r}` escapes a bidi or zero-width character and `ast.literal_eval` restores the raw character, so a note can hold a control or bidi character of any length. The docstring states the formatter cuts and escapes; that is Inc-5's obligation and nothing here tests it.
- **Fix:** Inc-5 must cut/escape `reported` and `unlinked` and carry a test with a U+202E id inside a reported row (the unsafe-id test here covers only `problems`).

### F3 - MINOR / note - `RelMapLimitError` propagates from the first `build_map`
- **Where:** adapter.py:145 (documented at 125-126).
- **What:** a 4 MiB canon can hold more than 100,000 rows, so the first call raises; the author's risk 1 says Inc-5 catches it - confirm at the Inc-5 review. Correctness: both passes see the same node set and the same unsafe/duplicate rule, so no edge can name an excluded node. Cost: first pass is O(V) over an empty edge list, final pass O(V+E), about 2x at the cap, nothing quadratic (`_unparsed_counts` is one pass over orphans times id depth, then one over HLRs). Acceptable, no change.

### F4 - MINOR / note - ledger cross-check indexing
- **Where:** `tests/test_relmap_adapter.py:94`: `text.split("batch.36 ", 1)[1]` raises `IndexError` rather than a clear failure if the ledger heading is reworded while the file exists. Add `assert "batch.36 " in text` first.

### F5 - note
- A row id that passes `_ROW_ID_RE` always has class HLR or LLR, so the builder's `unknown node kind` problem cannot fire from the canon. `unknown_status` counting kept nodes only (author issue 4) is correct.

## Mutants of my own (adapter.py only; restored from a byte copy, sha256 `cd58d797...` equal after each)

| # | Mutation | Result |
|---|---|---|
| A | `_status_word` returns the LAST word instead of the first | KILLED: `test_snapshot_census`, `test_status_words` (2 failed) |
| B | sibling stem uses the FIRST segment (`split(".",1)[0]`) instead of the last | KILLED: `test_snapshot_unparsed_counts`, `test_snapshot_gaps`, `test_unparsed_counts` (3 failed) |
| C | dot guard `if "." in s:` -> `if True:` | SURVIVED (38 passed) -> F1 |

## Opinion on the author's section 6 issues 1-8

1. Report text not retained on the map: agree; the printed note plus the tripwire is enough. Reword LLR-RMA.1.3 ("stays on the map") in the next PDR bump; no code change.
2. No `configured, not derivable in R1` note from the adapter: agree; the frozen `Derivation` has no field and the audit sources line owns it. Move the sentence to LLR-RMU.1.2 in the same bump; verify Inc-5 renders it.
3. Orphan relation for `LLR-` ids only: agree; matches the snapshot figures and is pinned (M-RMA-16).
4. `unknown_status` counts kept nodes only: agree; consistent with AT-124. State it in the contract.
5. Duplicate LLR edge drawn once; unsafe LLR neither linked nor unlinked: agree (ledger `.49`).
6. Gate V2 x7 and the docstring-name stand-ins: acceptable as station-expected reds. Caution: AT-117/119/124/125 stop blocking only because the file names them; the Inc-5 review must confirm real Layer B nodes replace the mention.
7. `build_map` twice: agree, correct, about 2x O(V+E) at the cap (F3).
8. First red run not kept: harmless (test arithmetic, adapter right); the code-absent RED was regenerated on the final test file.

Verdict: **approve-with-nits** (F1 to add with Inc-5 or earlier; F2 owed by Inc-5).
