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
| R5 | What `u` does while a draft is pending | `u` undoes the last SAVE and leaves the pending draft untouched | Undo acts on what was written; the draft is not written yet, and `esc`/discard already govern it (architect recommendation, ARQ 2026-10-08) |
| R6 | Following a link to another map | Counts as an exit: the `save · discard · stay` modal opens first | Same rule for every exit (R1); a link is the one exit R1 did not name |
| R7 | What `↵` does in a field | Keeps the draft and leaves the field (no write); the hint `↵ save` (`mapper/app.py:4043`) is rewritten to name `ctrl+s` | `↵` must not be a second save gesture, or the stray-write class returns through it |
| R8 | How a draft shows while the inspector is hidden (87 columns, or after `I`) | **Operator ruling 2026-10-08, verbatim:** "Marca en la línea de pista (Recomendado)" with the note "Usa código de colores, como el rojo para alertar que hay contenido no guardado." → the always-visible hint line prefixes `● unsaved (N) · ctrl+s save`, painted in the palette's alert token `ALERT` (`mapper/darkside.py:55`, `#ff4f42`) | Operator's choice at PDR (UX condition M1) |
| R9 | Guard modal title | `unsaved draft on «{title}» · {map_id}` (both through `darkside.plain`) — closest to the approved prototype frame (`unsaved draft on «raiz»`), adds the map id the security lens asked for | Orchestrator ruling at PDR (UX minor m1) |

These rulings are recorded in `PLAN.md` (Key decisions) and `state.json` `decisions_log`, and travel to the post-mortem and the vault at sync. The operator may overturn any of them.
