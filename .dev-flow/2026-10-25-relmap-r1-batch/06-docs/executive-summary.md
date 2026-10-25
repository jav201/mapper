# Executive summary — mapper — Batch 2026-10-25-relmap-r1-batch

> **Artifact language:** English (`state.json` `language`).
> Phase 6 artifact. Audience: non-technical stakeholder. Status: validated (PASS-WITH-NOTES), design review approved with conditions, **not yet merged**.

## 🔑 Bottom line (read first)

- **What we delivered:** a first, read-only "map of how requirements connect" inside `mapper`: it reads the project's requirements file, works out which requirement leads to which, and lists the places where the chain has a hole. The result is printed as a new block at the end of the existing `mapper --audit` report.
- **Business outcome:** for the first time the audit answers "which high-level requirements have nothing under them, and which rows could not be read?" without anyone checking by hand. On this repository it reports 7 requirements with nothing under them, 7 rows it could not read and 3 detailed requirements linked to no parent. It changes no existing result: the report, the verdict and the exit code are the same as before.
- **Next step:** the operator merges the branch, then runs the one check we could not run here (Python 3.10, backlog item B-148). After that, the next batch (R2) can put screens on top of this foundation.

---

## Context (reference)

### Context
`mapper` is the tool that keeps this project's requirements, reviews and evidence honest. A larger series (R1 to R5) adds a "relation map": a view of how requirements, acceptance checks and tests connect. This batch is R1, the first and deliberately smallest slice: no screen, only the engine and one report block.

### Problem
Requirements are only useful if each one can be followed downwards (to the detail that implements it) and each acceptance check leads to a test. Until now a gap in that chain was found by reading. Nothing in the tool listed gaps, ranked them, or said that part of the requirements file could not be understood.

### Solution
- A small engine that holds the connections between requirements, follows them in either direction, and finds gaps from a fixed list of gap kinds. Eight kinds are defined; today only one kind occurs for real, because the user-story and acceptance-to-test sources do not exist yet.
- A reader that builds this map from the project's own requirements file and never changes that file.
- A new block in `mapper --audit`, labelled "informational": it never changes the verdict or the exit code. Everything it prints from the repository is cut to a safe length and has control characters made visible, so a hostile file cannot disguise itself as a verdict.
- Optional settings files (`*.relmap.yml` in the repository root) are read under strict limits. A bad one is refused with a fixed one-line reason and never stops the audit.

### Outcomes / results
| Result | Value | Evidence state |
|---|---|---|
| Requirements verified | 35 of 35 | executed (`04-validation.md`) |
| Acceptance checks run through the real command | 12 of 12 | executed |
| Full automated test run | 4017 passed, 0 failed (2 skipped, 3 expected failures) | executed, one run by the orchestrator |
| Mutation checks (deliberately breaking the code to prove the tests notice) | 100 of 100 caught; 4 further weaknesses found by independent reviewers, each now closed | executed |
| Defects that reached the final gate | 3, all fixed; they came from file-wide rules checked only at the last step | executed (reproduced) |
| Python 3.10 compatibility | not run (no such interpreter on the machine) | not-run, B-148 |

Three small differences between the written requirements and the shipped behaviour were accepted, with the shipped behaviour as the reference (D-1 to D-3). One visible change: the `verdict:` line is no longer the last line of the audit output. A script that read the last line must read the line that starts with `verdict:`.

### Next steps
| Step | Owner | When |
|---|---|---|
| Merge the branch (merge was not delegated), then sync the batch to the vault | operator | next |
| Run the Python 3.10 test pass (B-148) | operator | before relying on the 3.10 floor |
| R2: screens for the map (matrix, gaps view, node sheet); its design review carries the open design items from this batch | next batch | after merge |
| Create the missing sources (user stories, acceptance-to-test table) and clean the 7 unreadable requirement rows (B-141, B-142) | to be decided | before R2 has more than the requirement skeleton to show |
