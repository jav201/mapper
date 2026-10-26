# Executive summary — mapper — Batch 2026-10-25-relmap-r2-batch

> **Artifact language:** English (`state.json` `language`).
> Phase 6 artifact. Audience: non-technical stakeholder. Status: validated (PASS-WITH-NOTES), design review approved with conditions — **both conditions discharged at the P5 close** — full suite 4226 passed / 0 failed, **not yet merged**.

## 🔑 Bottom line (read first)

- **What we delivered:** the screens for the relation map. Inside `mapper`'s terminal UI, a new read-only "relation screen" hosts three views of how the project's requirements connect — a matrix with a two-hop "what would a change here touch" lens, a ranked list of the record's gaps (groupable by kind), and a per-node sheet showing what feeds a requirement and what it reaches — plus the Home list that finds and opens relation maps, and a 240-character safety bound on the audit report's new lines.
- **Business outcome:** the questions "which requirement has nothing under it, what breaks if I change this, and where is the chain of evidence weakest?" now have answers on screen, in the tool itself, instead of in a text block at the end of a report. Nothing existing changed: the tree maps, the audit verdict and the exit code are byte-identical to before; opening a relation map writes nothing.
- **Next step:** the operator merges the branch, then runs the one check we could not run here (Python 3.10, backlog item B-165). After that the series continues with its standing plan: R3 (evidence search), R4 (timeline), R5 (metro) — and the UI batch the operator sketched from the October prototype round is queued at the next kickoff.

---

## Context (reference)

### Context
`mapper` is the tool that keeps this project's requirements, reviews and evidence honest. A five-part series (R1–R5) is building a "relation map": a living view of how requirements, acceptance checks and tests connect. R1 (previous batch) shipped the engine and a text block in the audit report — deliberately headless. This batch, R2, puts the views on screen inside the Darkside terminal UI, exactly as the operator approved them from the October prototypes.

### Problem
R1 proved the map could be derived and the gaps found, but the only window was a report block: no focus, no ranking walk, no per-node detail, no way to open it from the app's front door. The prototype round of 2026-10-23/24 settled what the screens should look like; this batch was commissioned to port those verdicts onto the real, frozen R1 engine.

### Solution
- A relation screen in the existing terminal UI with three views switched by keys: the **matrix** (one cell per requirement pair, coloured by the strongest connection, with a side panel lens that counts what a change reaches in one and two hops), the **gaps view** (every gap the record does not explain, ranked by severity then reach, regroupable by kind), and the **node sheet** (for one requirement: what feeds it, what it reaches — direct, or the full chain with one key).
- The Home front door now lists relation maps beside tree maps, opens each by its kind, and never writes to the workspace when it does.
- Every word on these screens is generated from one keymap "seat", so help, the command palette and the on-screen key bar can never drift from the keys that actually work.
- The audit report's new lines gained a 240-character bound (cut on a spelling boundary after escaping), so a hostile or broken file cannot flood or spoof the report.

### Outcomes / results
| Result | Value | Evidence state |
|---|---|---|
| Requirements verified | 72 of 72 (20 high-level, 52 detailed) | executed (`04-validation.md`) |
| Acceptance tests through the real screens | 23 of 23 | executed — real key presses on the real app, at both reference widths |
| Full automated test run | 4226 passed, 0 failed (2 skipped, 3 expected failures) | executed, one clean run by the orchestrator |
| Mutation checks (deliberately breaking the code to prove the tests notice) | 62 of 62 in the increments' batteries, plus 13 reviewer-authored mutants at the reviews and design gate — all caught | executed |
| Defects that reached the final gate | 2 escapes, both fixed before validation; both reproduced and stored this close | executed (reproduced on the pre-fix trees) |
| Design review | approved with conditions; both conditions discharged at the P5 close | executed |
| Python 3.10 compatibility | not run (no such interpreter on the machine) | not-run, B-165 |

Two small differences between the written requirements and the shipped behaviour were accepted with the shipped behaviour as the reference (the two-hatch cut mark; "characters" counted as code points). One visible change to note for scripts: a year ago the audit report taught readers to find the verdict by a prefix, not by position — that still holds; nothing about the verdict line changed this batch.

### Next steps
| Step | Owner | When |
|---|---|---|
| Merge the branch (merge was not delegated), then sync the batch to the vault | operator | next |
| Run the Python 3.10 test pass (B-165) | operator | before relying on the 3.10 floor |
| R3: evidence search · R4: timeline · R5: metro, in series order | next batches | after merge |
| The UI batch from the October prototype round (canvas follow, outline diff gutter, roles skeleton, home queue, connect-repo panel, hero margin) | next P0 | per the operator's queue |
| Build the missing sources (user stories, acceptance-to-test table) so the matrix gains its test columns | to be decided | before R5 widens the map |
