# Executive summary — mapper — Batch 2026-08-26-ui-next-batch-02

> Phase 6 artifact. Owner role: `presentation-builder` — drafted by `deepseek-v4-pro`, verified by the orchestrator. Audience: non-technical stakeholder. 1-2 pages.

## 🔑 Bottom line (read first)

- **What we delivered:** the map editor now explains itself — a `?` legend on every screen, a fully English interface, and hardened safety for connecting repositories and opening attachments — on top of a canvas you can pan and search, and a home screen that shows each map's own shape.
- **Business outcome:** the product no longer shows Spanish UI or the operator's filesystem paths to an outsider, no longer silently overwrites a map with the same name, and refuses any unsafe repository URL or file path *before* it can do damage.
- **Next step:** merge is done; run `/dev-flow-sync` to upload the artifacts, then pick up the next batch from the backlog (B-36, B-79…B-97) and decide what to do with the leftover remote branch.

---

## Context (reference)

### Context

`mapper` is a terminal application (a Textual TUI) for building and navigating concept maps / knowledge graphs. This batch — the second `ui-next` batch (predecessor `2026-08-25-ui-next-batch-01`) — is the tail end of a longer effort: earlier batches shipped the editable inspector, attachments, a single key map, and coverage worklist. This one finishes the UI surface and hardens the parts that touch the outside world.

### Problem

Three things hurt:

1. **No legend.** Nothing told the operator which keys worked in which screen; the same `?` key did different things (or nothing) depending on where you were.
2. **Spanish UI.** The interface was mixed-language, and several sealed tests still pinned Spanish words.
3. **Unsafe outside-world access.** Typing a repository URL or a file path could reach the filesystem or run a subprocess with hostile text; a map id could write outside the workspace or overwrite an existing map; a `\r`/`\n` in notes could silently corrupt them.

### Solution

In business terms: the app now **explains each screen** (legend with the real keys and glyphs), **speaks one language** (English), and **refuses anything unsafe by default** — a typed repository URL or path is checked against a closed allow-list and rejected before anything runs; a map id is confined to the workspace and never overwrites; every piece of text that came from a file is cleaned before it is drawn.

### Outcomes / results

| Outcome | Measured value | Source |
|---------|----------------|--------|
| Test suite grew | **429 collected → 2797 passed** (units differ: the baseline counted deselected nodes) | `04-validation.md` (baseline `PLAN.md:405` → `gate-run-master-tree.txt`) |
| Final gate | **2797 passed, 0 failed** (24 deselected, 3 expected-failure) | `gate-run-master-tree.txt` |
| Whole-branch security sign-off | **PASS, 0 HIGH findings** | `VERDICT-merge-2026-10-03.md`, `state.json` `MERGED_2026-10-03` |
| Safety probes | **396 hostile runs, 0 escapes** (Inc-SEED security review) | `state.json:1016` (`A-113`) |
| Coercion coverage | every file-derived string coerced before paint | `HLR-COERCE`, `A-111` |

> Security numbers are the batch's own recorded figures, not estimates. No row is estimated.

### Next steps

1. **Sync (now):** run `/dev-flow-sync` to upload the artifacts to the Obsidian vault.
2. **Operator decision (pending, `M3` "decide after the merge"):** the remote branch `origin/feat/ui-next-batch-02` still carries the intermediate commits that the squash merge kept out of master.
3. **Next batch (next):** pull from the backlog — the deferred residuals B-79…B-97 (path/URL hardening, toast layout, hidden-field focus) plus B-36 (inspector data-loss) and the one open flake FLAKE-2.

---

*Drafted by `deepseek/deepseek-v4-pro` (via `opencode run`), to be verified by the orchestrator. No `presentation-builder` agent ran for this artifact. Every number is cited to a repo file or the attached gate transcript; none is invented.*
