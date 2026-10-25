# PDR record rows - ux-reviewer (trigger D1)

Batch `2026-10-25-relmap-r1-batch`, worktree HEAD c1f3e01. Surface: the `mapper --audit <repo>` text block (LLR-RMU.1.1 to .1.4).
Context of use: an operator or reviewer reads the audit in a terminal or a CI log to decide release readiness.
Task: find the verdict, then decide whether any structure finding matters. Environment: 80-column terminal or a CI log pane, possibly piped through `tail`/`grep`, diffed between runs.

## Method and limits (declared)
- State of evidence: **inspected, not exercised.** The block does not exist yet (Inc-5). I read HLR-RMU.1, LLR-RMU.1.1 to .1.4, the line-format table, the gap sentence templates, LLR-RML.1.2/.1.5 causes, AT-120..AT-129 and `mapper/reqharness/audit.py` (`render`, `run_cli`).
- I ran the existing report once on the worktree (no registry): lines are lower-case `key: value`; `WARNING:` and `reported:` exist; the verdict is the last line and uses ` · ` (`not ready · no registry yet`). The `identity:` line is already about 190 characters, so wrapping at 80 columns is existing behaviour. Everything below about the new block is judged from the specified formats, not from printed output.
- Expert inspection against the declared context: **performed** (this file). Automated walkthrough: **not performed - nothing to drive until Inc-5.** Evaluation with users: **not performed - single-operator team; no other user of this surface exists.**
- Not covered: colour (the audit is plain text), Windows console code-page rendering of ` · ` and `…` (the existing verdict already uses ` · `, so the risk is inherited), the printed gap text of the 7 unsourceable kinds (formatter evidence only, per OQ-R1-2).

## Findings

### MAJOR-1 - LLR-RMU.1.2 / HLR-RMU.1: nothing says the block is advisory; `gaps: 7 (MED=7)` right after a ready verdict reads as a contradiction
The block follows the verdict line. A reader scanning for readiness sees `HIGH`/`MED` counts below a green verdict and cannot tell whether they gate. The requirement states "does not change the verdict" only in prose, never on the screen.
Proposed: the first block line carries it, once per run (before the first `descriptor` label):
`structure: informational - does not change the verdict or the exit code`
Add it to the line-format table; it does not start with `verdict: `, so AT-122 stays valid.

### MAJOR-2 - LLR-RMU.1.2: `structure: notes ...` (count line) and `structure note: ...` (note lines) differ by one letter
Two line kinds with near-identical prefixes defeat grep and eyeball scanning. The count line also uses internal vocabulary: `excluded`, `unknown_status`, `reach_not_computed` (snake case, unlike the report's spaced words such as `unentitled reviews`) with no hint of what was excluded from what.
Proposed: `structure: skipped 3 canon rows (duplicate id=1, unsafe id=2); unknown status=1; reach not computed=2` with each part printed only when its count > 0. Keep `structure note:` for note lines. Update the AT-124 exact-line oracle.

### MAJOR-3 - LLR-RMU.1.2: overflow lines masquerade as data rows
`structure gap: … and K more` shares the prefix of a gap row, so `grep -c '^structure gap:'` over-counts by one; same for `structure note: … and K more`. "more" also does not say the hidden ones are the lowest-ranked.
Proposed: `structure: gaps shown 20 of 23 (3 lowest-ranked not shown)` and `structure: notes shown 10 of 14 (4 not shown)`, so `structure gap:` and `structure note:` stay strictly one row, one item.

### MAJOR-4 - LLR-RMU.1.1 / LLR-RMU.1.2: the verdict is no longer the last line of output
Today `render` ends with `verdict:`. A CI step that does `tail -n 1` now reads a structure line. The design justifies prefix-based tests, not operator habits.
Proposed condition: state in the packet and the README that the verdict line is found by prefix `verdict: ` and is no longer last, and let the MAJOR-1 header carry the same message on screen. Moving the block before the verdict is rejected by the design for byte-compatibility; do not reopen.

### MINOR-1 - LLR-RMU.1.2 refusal causes: the cause does not say which field, or what the effect is
`structure: refused (x.relmap.yml): unsafe path (outside)` does not say whether `us_canon` or `at_table` was at fault; `source value is not text` does not say which key; `exceeds the byte limit` gives no limit; "refused" does not say the descriptor's block is skipped.
Proposed: `structure: refused (<base name>): <cause> - descriptor skipped`; K17 as `unsafe path in us_canon (outside)`; K16 as `source.<key> is not text`; K5 as `exceeds the <N> byte limit` with N rendered from `MAX_MAP_BYTES`. K-ids stay out of the text (agreed: fixed strings only).

### MINOR-2 - LLR-RMU.1.1: `structure: unavailable (<exception type name>)` is opaque
`unavailable (ValueError)` gives no action. Existing convention in `run_cli` is `audit: internal error (<Type>)`.
Proposed: `structure: unavailable (internal error: <Type>)`. The two fixed lines `(no repository)` and `(no registry)` are clear as specified.

### MINOR-3 - LLR-RMU.1.2 / LLR-RMG.1.1: qualified sentence has a plural bug and jargon
`(1 canon rows unparsed or unlinked near this id)` is ungrammatical at n=1; "unparsed" is internal. AT-125 pins the literal.
Proposed: `(canon rows near this id could not be parsed or linked: 1)`; update AT-125 and the M-RMG-4 oracle. This is wording, not a catalogue change (kinds, severities, templates untouched).

### MINOR-4 - LLR-RMU.1.2: width at 80 columns
Gap rows start with about 60 fixed characters (`structure gap: MED · HLR WITHOUT LLR · HLR-CAN.1 · reach=0 · `), the sentence repeats the node id, and the title is cut at 120, so rows reach about 210 characters; unlinked-LLR notes (5 ids of up to 120) can approach the 1,000-character bound of AT-129. Wrapping is not a defect by itself (`identity:` already wraps), and severity-first, node-second is the right order for scanning.
Proposed: state in the packet that width is not guaranteed and that the first 40 characters carry severity, kind and node; optionally cut the title to 60 in gap sentences only. Not a blocker.

### MINOR-5 - LLR-RMU.1.2: `reach=<r>` is undefined on screen
A reader cannot tell whether reach counts upstream, downstream or both. Proposed: document it once in the README or the header. Low priority.

### MINOR-6 - LLR-RMU.1.2: label and sources tokens are ambiguous
`structure: descriptor default` reads as a file name: use `structure: descriptor (built-in default)`. `us_canon=not configured` puts a space inside a `key=value` token and breaks `awk`/`cut`: use `us_canon=unset at_table=unset`.

### MINOR-7 - LLR-RMU.1.2: ` · ` inside user-derived text
Titles may contain ` · `, so the fixed columns of a gap row are not machine-splittable. Acceptable for a human-first line; state in the packet that gap rows are for reading, not parsing.

### MINOR-8 - HLR-RMU.1: bounds are per descriptor
8 blocks times about 32 lines each is about 260 lines in the worst case. State the worst case in the packet or add a global cap; not required for approval since the normal case is one block.

## Checks that pass (no action)
- Prefix and casing: lower-case `key: value` and `structure ...` prefixes match the existing report (`repo:`, `chain:`, `reported:`); severity words `HIGH`/`MED`/`LOW` follow the existing uppercase-marker habit of `WARNING:`; all text is English.
- Severity and counts at a glance: `gaps: G (HIGH=h, MED=m, LOW=l)` always prints all three; the zero-omission rule in the summary line is stated once.
- Forged verdict: no new line may start with `verdict: ` (AT-122), so no structure line is a verdict by prefix. Semantic confusion is MAJOR-1.
- Determinism: LLR-RMU.1.4 fixes kinds, edge types, descriptors, notes and ties to stable orders; AT-128 compares four hash seeds. Condition: no timestamp, absolute path or elapsed time enters the block (the sources line already prints the configured string only).
- Empty, error and clean states each have a line (empty canon, no repo, no registry, canon K1-K7, descriptor K1-K17, descriptor overflow).

## Criteria

| Criterion | How exercised | Observed | State | Result |
|---|---|---|---|---|
| Block is advisory and cannot be read as the verdict | spec read | no on-screen statement | planned | fails -> MAJOR-1 |
| Verdict findable | spec read | prefix `verdict: `, no longer last | planned | condition -> MAJOR-4 |
| Prefix and casing consistent | spec vs `render` | consistent | planned | pass |
| Counts and severity at a glance | spec read | all three severities always printed | planned | pass |
| Notes and refusal wording self-explanatory | spec read | partly opaque | planned | MAJOR-2, MINOR-1, MINOR-2 |
| 80-column width | spec read | rows about 210 chars, wrap | planned | MINOR-4 (not a blocker) |
| Determinism | spec read + AT-128 | specified | planned | pass |
| Empty and error states | spec read | present | planned | pass |

## Verdict: approved with conditions
Conditions, to be applied to the LLR text before Inc-5 (none adds scope):
1. MAJOR-1 header line and MAJOR-4 note (verdict found by prefix, no longer last).
2. MAJOR-2 and MAJOR-3 renames (count line, overflow lines), with the AT-124 and AT-122/AT-120 oracles updated to the new literals.
The MINOR items are advisory; MINOR-1, -2, -3 and -6 are cheap wording changes best folded into the same edit.
Re-walk owed at Phase 4: run `mapper --audit` over the snapshot fixture and one crafted descriptor, read the real printed block at 80 columns, and mark each criterion `executed`.
