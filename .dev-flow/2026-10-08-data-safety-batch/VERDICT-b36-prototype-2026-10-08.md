# Verdict — B-36 inspector save model · 2026-10-08

**Round:** prototype round for US-001 ← B-36, four variants mounted in the real app (`prototypes/b36_save/`, untracked), captured at 118 columns, gallery published 2026-10-08 (private artifact).

**Operator verdict, verbatim:** "C"

**C — draft + explicit save.** Edits accumulate in a per-node draft and survive leaving the field; nothing is written until `ctrl+s`. Dirty fields carry a marker and the inspector header shows `● unsaved (N)`. Changing node with a pending draft opens `save · discard · stay`.

Measured on the prototype (sha256 of `.mmd` and `.yml` against the start state, two runs, identical): one stray `n` then leaving the field → **not written**; deliberate edit + `ctrl+s` → written. Today's model (D) → written after the stray key.

## Open points the prototype left, decided by the orchestrator (standing autonomous authorization, 2026-10-08)

| # | Point | Ruling | Why |
|---|---|---|---|
| R1 | How long a draft lives | Per node, in memory, for the life of the map screen. Leaving the map screen or quitting the app with a pending draft opens the same `save · discard · stay` modal. A draft is never persisted to disk on its own. | One rule for every exit is easier to learn than three; a draft written to disk would be a second save path, which is the defect class being closed |
| R2 | Which fields go through the draft | Every inspector field, including the `state` segmented control (the prototype still committed it immediately) | A model with one exception teaches the operator that some edits are instant, which brings the stray-write back |
| R3 | What `u` undoes | One `ctrl+s` as one step (all fields it wrote) | Undo granularity matches the save gesture the operator made |
| R4 | Modal keys | `s` save · `d` discard · `esc` stay | As prototyped; `esc` keeps its app-wide meaning of "back out, change nothing" |

These rulings are recorded in `PLAN.md` (Key decisions) and `state.json` `decisions_log`, and travel to the post-mortem and the vault at sync. The operator may overturn any of them.
