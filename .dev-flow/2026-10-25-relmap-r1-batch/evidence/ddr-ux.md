# DDR record rows - ux-reviewer (trigger D1), Phase 4 re-walk

Batch `2026-10-25-relmap-r1-batch`, worktree HEAD e6dc5c5. Surface: the `mapper --audit <repo>` structure block.
Context of use (from `pdr-ux.md`): an operator reads the audit in a terminal or CI log to decide release readiness. Environment: 80 columns, possibly `tail`/`grep`.

## Method and limits (declared)
- **Automated walkthrough: performed**, independently of the author's self-read (not consulted). Real entry: `from mapper.app import main; main()` with `--audit <repo>` in a subprocess, `PYTHONPATH` = this checkout, `env -u NO_COLOR -u TERM`, `PYTHONDONTWRITEBYTECODE=1`. Repo seeded with the test helper `registry_repo` over the snapshot canon, plus `good.relmap.yml` (`{}`), `broken.relmap.yml` (`kind: tree`), `badpath.relmap.yml` (`us_canon: ~/x`). Second run with no descriptors. Exit code 1 (unreviewed requirements), stderr empty.
- Painted result: a CLI prints plain text, so stdout is the painted result. Widths measured per line; "80 columns" is judged by character counts, not by a terminal emulator (**inspected, not exercised** for real wrapping).
- Expert inspection against PDR conditions: performed. Evaluation with users: not performed - single-operator team; no other user of this surface exists.
- Not run in this walk: gap overflow (`and K more` / its replacement; needs more than 20 gaps), the `skipped canon rows` count line (the snapshot has no excluded rows), K1-K16 refusal texts other than `unsupported kind` and `unsafe path in us_canon`, Windows console code page. Those rest on the unit/AT evidence only.

## Observed output (36 lines; account name redacted, long lines cut at 120)
```
14 verdict: not ready · unreviewed requirements
15 structure: informational - does not change the verdict or the exit code
16 structure: refused (badpath.relmap.yml): unsafe path in us_canon (outside) - descriptor skipped
17 structure: refused (broken.relmap.yml): unsupported kind - descriptor skipped
18 structure: descriptor good.relmap.yml
19 structure: profile=reqharness nodes=275 (HLR=76, LLR=199) edges=196 (refines=196) cycles=0
20 structure: sources: canon=REQUIREMENTS.md us_canon=unset at_table=unset
21 structure: gaps: 7 (HIGH=0, MED=7, LOW=0)
22 structure gap: MED · HLR WITHOUT LLR · HLR-N13.3 · reach=0 · HLR-N13.3 has no LLR under it: While the workspace hold...
29 structure note: unparsed row LLR-HYG.1.1   (x7)
36 structure note: unlinked LLRs (3): LLR-REPAIR.1, LLR-REPAIR.2, LLR-RH.6.2
```
No-descriptor run: `structure: descriptor (built-in default)`. Line 1 `repo:` prints `C:\Users\<user>\...` (pre-existing line, not part of the block).
Widths: verdict 40, summary 90, gaps line 41, gap rows 218 to 283, `identity:` 157, note rows 40 to 73.

## Criteria

| Criterion (PDR) | How exercised | Observed | State | Result |
|---|---|---|---|---|
| MAJOR-1 advisory line first | real run, line 15 | exact proposed wording, once, directly after verdict, before first `descriptor` | executed | met |
| MAJOR-2 count line vs note-line prefix | real run | `structure: skipped ...` line not triggered (no excluded rows); note lines are `structure note:` only; no one-letter-apart pair appears in this run | executed (partial) | met for what printed; count line not-run here (AT-124 covers) |
| MAJOR-3 overflow lines not masquerading as rows | `grep -c '^structure gap:'` = 7 = gaps printed; `^structure note:` = 8 = 7 rows + 1 aggregate note | overflow not reachable at 7 gaps | executed (partial) | gap arm not-run; see F-3 |
| MAJOR-4 verdict not last, found by prefix | `tail -n 1`, `grep -n '^verdict: '` | `tail -n1` returns the `unlinked LLRs` note; `verdict: ` is unique, line 14. Documented in `increment-005.md` and a code comment; **not in README/docs** (condition asked packet and README) | executed | partly met -> F-1 |
| MINOR-1 refusal names field, effect | lines 16-17 | `in us_canon`, `- descriptor skipped`, base name only, no path, no YAML echo | executed | met |
| MINOR-2 unavailable wording | not triggered | - | not-run | n/a to this walk |
| MINOR-3 qualified sentence | not triggered (no qualified gap) | - | not-run | n/a to this walk |
| MINOR-4 width | measured | identifying part (`MED`, kind, node, `reach=0`) ends at column 58, before any wrap; sentence wraps to 3-4 lines at 80; declared not guaranteed | executed (character counts) | met as declared |
| MINOR-5 `reach=` defined | grep README/docs | no definition anywhere | executed | not met -> F-2 |
| MINOR-6 labels and tokens | line 18, default run, line 20 | `descriptor (built-in default)`, `us_canon=unset at_table=unset` | executed | met |
| MINOR-7 ` · ` in titles / gap rows for reading | line 22 | still ` · `-separated; stated in the test docstring only | inspected | accepted |
| MINOR-8 worst case 8 blocks | one descriptor shown, 3 refused | refused descriptors print one line each (good); repeat-per-descriptor of gap rows not exercised | inspected | accepted (B-150) |
| B-150 observations | real run | confirmed: `unparsed row <id>` (lines 29-35) does not say why, yet the same run's `reported:` lines 6-12 give the reason (`5 cells, expected 4`); sentence repeats node id (`HLR-N13.3 ... HLR-N13.3 has no LLR`); gap rows 218-283 chars | executed | observations stand, none breaks a criterion |

## Findings
- **F-1 (minor, condition residual):** MAJOR-4 documented in the packet and code only; `tail -n 1` in CI now yields a note, and no README/operator doc says "find the verdict by `verdict: ` prefix". Wording for the operator doc: `The verdict is the line that starts with "verdict: ". Structure lines follow it; the last line of the output is no longer the verdict.`
- **F-2 (minor):** `reach=<r>` undefined on screen or in docs. Proposed: one sentence next to F-1, `reach = number of nodes linked to the gap node (both directions)` - confirm the true definition first.
- **F-3 (minor, untested here):** the overflow lines were not reachable with 7 gaps; confirm in the AT output that they no longer start with `structure gap:`/`structure note:` as rows.
- **F-4 (minor, = B-150):** `unparsed row <id>` should say why or point to the `reported:` line: `structure note: unparsed row <id> (see "reported:" above)`; the 40-character sentence repetition `HLR-N13.3 ... HLR-N13.3` is cosmetic.
- **F-5 (cosmetic, pre-existing):** `repo:` line prints the absolute path; in a shared CI log this exposes the runner's home directory. Out of scope for this batch; note only.

## Verdict: approved with conditions
All four MAJOR conditions of the PDR are visible and met on the printed block except the MAJOR-4 documentation half (F-1). No finding blocks release readiness: the verdict stays unambiguous, advisory status is on screen, and refusals say field and effect. Conditions: F-1 and F-2 as one README/operator-doc sentence (docs-only, no code); F-3 confirmed; F-4 stays in B-150.
