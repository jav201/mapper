# ARQ — architect — mapper — Batch 2026-10-08-data-safety-batch

> Station: `stations/p1-arq.md` (fired on A2 and A3; B1 fired beside them). Inputs: `01-requirements.md` §2.6
> (US-001…US-004, all READY), `VERDICT-b36-prototype-2026-10-08.md` (operator verdict "C", rulings R1–R4),
> `PLAN.md` §Triggers, the standing `docs/ARCHITECTURE.md`, and the read-only B-36 prototype
> (`prototypes/b36_save/inapp.py` in the sibling prototype worktree). Output: this record plus the
> amendment to `docs/ARCHITECTURE.md` (same branch, `arq/data-safety`).

**Bottom line.** No module boundary moves and no dependency edge is added. One interface moves (A3):
`FichaInspector.FieldCommitted` is **removed** and replaced by a per-node draft that the inspector holds
and `MapScreen` pulls on `ctrl+s` or on the `save` answer of a new `save · discard · stay` modal
(`mapper/screens/draft_guard.py`, inside the existing `screens` module). US-001 cuts into two increments
(4 + 1 source files); US-002/003/004 are test/record-only (0 source files). Map approved below.

---

## 1 · Problem, restated

Today a blur or `↵` in any inspector field posts `FieldCommitted` (`mapper/widgets/inspector.py:347-365`),
and a `state` segment change posts it too (`:367-373`). `MapScreen.on_ficha_inspector_field_committed`
(`mapper/app.py:3344-3378`) pushes an undo snapshot and writes `.mmd` + `_nodos.yml` through
`_save_or_toast`; its delta gate (`:3357-3359`) cannot tell a stray keystroke from an intended edit.
Model C replaces "every blur writes" with "edits accumulate in a draft; only `ctrl+s` (or the modal's
`save`) writes". ARQ must decide who holds the draft, what replaces the message, how every exit reaches
the modal, how undo groups a save, and how the work cuts under the 4-source-file cap.

## 2 · Constraints

| Constraint | State | Value / reason |
|---|---|---|
| Source-file budget | `executed` | 4 SOURCE files per increment, tests uncapped (operator, global rule) |
| Layering bans | `executed` | `widgets` may not import `store`/`screens`/`app` and never saves (`docs/ARCHITECTURE.md` §3 `widgets` row); `screens` may not import `app` (§3) |
| Persistence interface | `executed` | whole-graph `MapStore.save(map_id, graph)`, no partial write (§4; old risk A-3 "do not add `save_field`") |
| Draft lifetime, field coverage, undo, keys | `executed` | rulings R1–R4 (verdict file) |
| Framework behaviour | `executed` | Textual 8.2.8 (`python -c "import textual; print(textual.__version__)"` → `8.2.8`); `on_*` dispatched across the MRO (prototype finding, `inapp.py` closing comments) |
| Live quit chord | `executed` | `MapperApp._merge_bindings()` keys → `['ctrl+c', 'ctrl+p', 'ctrl+q', 'question_mark']`; Textual's `ctrl+q` is `priority=True` → `MapperApp.action_quit` (`mapper/app.py:4937`) |
| Cost / latency / tokens | `n/a — local TUI, no model API, no network; the save is the same single whole-graph write as today, now issued less often` |
| Privacy | `n/a — no new data class; the draft is in-memory only and is never written on its own (R1)` |
| Deadline / team size | `n/a — one operator, one batch; does not change which design is right` |

## 3 · Decisions

### D1 · Where the draft lives — `FichaInspector` (`widgets`)

**Decision.** The inspector holds one node's draft (`node_id` + `{field: value}`), in memory, for the
widget's life — which is its `MapScreen`'s life, because the inspector is composed once
(`mapper/app.py:1589`) and `I` only hides it (`action_toggle_inspector`, `:1697-1701`).

**What it exposes (read-only to `MapScreen`, the only consumer):** `draft_node_id`, `draft_values()`
(a copy), `has_draft()`, `clear_draft()`. It also paints its own state: the dirty marker per field and
`● unsaved (N)` in the header.

**What does NOT belong to it:** writing (`widgets → store` is banned), the undo snapshot, `darkside.plain`
coercion at the sink (A-111 stays in `MapScreen`, at the apply point), deciding which exits ask, pushing
the modal, and any on-disk persistence of the draft (R1).

**Two rules inside it, both load-bearing:**
- Dirty means *differs from what the form showed* (`darkside.plain(stored)`, the value `_rows` mounts at
  `inspector.py:143,159,166`), not from the raw stored value — otherwise a node whose title `plain()`
  alters would be "dirty" with no keystroke. A field edited back to the shown value leaves the draft.
- The draft is overlaid when rows are **built** (`_rows`), including the `state` segment's active index
  (R2). The prototype re-applied it after `_rebuild`; that was a hack around the fact that
  `refresh_canvas` rebuilds the inspector on every repaint (`app.py:3281`).

**Alternatives.** (a) `MapScreen` owns the draft, inspector posts a message per keystroke — rejected:
per-keystroke traffic, a `show()` signature change, "what is dirty" and "how it is painted" split across
two modules, and growth of a 4957-line file. (b) New pure module `mapper/draft.py` — rejected: a ~30-line
dict with an id does not earn a module, an A1 and a source file out of a 4-file budget. **Re-open** when a
second surface (documents editor, a second inspector) needs the same draft. Recorded as **R-012**.

### D2 · `FieldCommitted` — removed, not reshaped (trigger A3)

**Census** (`grep -rn "FieldCommitted\|field_committed" --include=*.py mapper tests`, 2026-10-08):

| Site | Role |
|---|---|
| `mapper/widgets/inspector.py:68` | class definition |
| `mapper/widgets/inspector.py:365` | producer — `_commit`, reached from `on_input_submitted` `:347` and `on_input_blurred` `:351` |
| `mapper/widgets/inspector.py:372` | producer — `on_ds_segmented_changed` (`state`) |
| `mapper/app.py:3344-3378` | **the one product consumer** — `MapScreen.on_ficha_inspector_field_committed` |
| `tests/test_inspector.py:103, :162` | test consumer — posts the message as the "edit reached the screen" injection point |
| `tests/test_g6_store_surrogates.py:133, :152, :176` | test consumer — surrogate coercion (A-111) through the real message |
| `tests/test_worklist_safety.py:254` | test consumer |

**Decision.** Producer, class and handler are deleted in the same increment (Inc-1). `MapScreen` gets
`action_save_draft` (seat row `ctrl+s` → `save_draft`) and one internal save routine that: reads
`inspector.draft_values()`; pushes **one** snapshot; applies each field through `plain()`; calls
`_save_or_toast` **once**; on success sets `base_graph`, calls `inspector.clear_draft()` and toasts; on
failure restores the graph and keeps the draft. The three test files are re-pointed to "draft + `ctrl+s`"
(B1 — they are not US-001's own tests, so the re-point is a declared B1 consequence, not a silent edit).
The A-111 surrogate test keeps its intent: the coercion now sits on the save routine's apply step.

**Why pull, not a reshaped message.** A posted message cannot return the save's result, yet the draft may
be cleared only if the write succeeded, and the modal's `save → then leave` needs the write finished before
the exit runs. A method call gives both for free. **Why delete rather than keep:** a live handler is a
second save path one `post_message` away — the defect class B-36 closes. Recorded as **R-013**.

**Secondary consumers of the old semantics (same file, Inc-1):** the hint `"↵ save"` at
`mapper/app.py:4043` (and its comment at `:4040`, "MapScreen binds no ctrl+s") becomes false and must read
the `save_draft` glyph from the seat (`_seat_glyph`, `:3623`). Tests whose oracle is "type, `↵`/blur,
file changed" must be found by census at PDR, from this candidate set (files referencing the inspector ids
or the message, with their persistence-oracle count): `test_g6_store_surrogates.py` 23,
`test_worklist_safety.py` 14, `test_fold.py` 3, `test_inspector.py` 3, `test_en7.py` 2, `test_app.py` 1,
`test_inc9d.py` 1, `test_legend_design.py` 0. State: `planned`.

### D3 · How the `save · discard · stay` modal is reached from every exit (R1)

One modal: `DraftGuardScreen(title) -> ModalScreen[str]` in `mapper/screens/draft_guard.py`, dismissed with
`"save" | "discard" | "stay"`, keys from a new modal seat scope `draft` (`s` · `d` · `escape`, R4), title
painted with `markup=False` (SEC-H2, as `_ConfirmScreen` does, `app.py:385-401`). It imports `design` and
`keymap` only — no `screens → app` edge. One `MapScreen` method owns the decision for every exit: "if a
draft is pending, push the guard, then on `save` (success only) or `discard` run the continuation; on
`stay` or a failed save, run nothing". Recorded as **R-014**.

| Exit | Choke point (evidence) | How the guard is reached |
|---|---|---|
| Node change (j/k/h/l, rail, `n`/`N`, `M`, worklist jump, add child, …) | `refresh_canvas` re-points the inspector at **one** site, `app.py:3281` (`grep -n "\.show(" mapper/app.py` → `:3281` inspector, `:3282` rail) | Before `show()`: if `draft_node_id` ≠ the new cursor, do not re-point; push the guard. `stay` restores the cursor; `save`/`discard` re-point. Guarding the choke point covers every cursor-moving action by construction instead of by enumeration (prototype did this inside `show()` via a widget message; moving it to the screen keeps the decision out of the widget). |
| Leave the map screen | `action_home` (`q`, `app.py:4683-4684`) and the pop branch of `action_back_or_home` (`esc`, `:4719`); the palette dispatches the same `action_*` methods (`:4920-4927`) | Both pops go through the guard. |
| Follow a link to another map | `app.py:3566` pushes a second `MapScreen` | **ARQ recommends** guarding it (PDR/UX to rule): the lower screen keeps a graph that a linked edit can make stale, and saving a draft from it would write that stale graph. |
| Quit the app | `ctrl+q` (Textual default, priority) → `MapperApp.action_quit` (`app.py:4937`) | `MapperApp.action_quit` walks `screen_stack` for every `MapScreen` with a draft and guards each before `exit()`; not re-entrant (a second `ctrl+q` while the guard is up does not stack another). `HomeScreen.action_quit` (`:1056`) needs no guard: no `MapScreen` is on the stack beneath home. |
| Terminal killed / crash | none | Draft lost by design (R1: never persisted on its own). Declared, not mitigated. |
| A screen pushed over the map (help, palette, coverage, documents) | — | Not an exit: the `MapScreen` is alive, so the draft survives (R1). |

### D4 · How `u` groups one save (R3)

Undo is the per-map snapshot stack on `MapperApp.undo_stacks` (`app.py:3496-3503`, `:4902`), pushed by
`_push_snapshot` (`:3505`). The save routine calls `_push_snapshot()` **exactly once** before applying all
drafted fields, and `_save_or_toast` exactly once after — so one `u` (`_pop_snapshot`, `:3517`) restores the
state before that `ctrl+s`, all fields together. On a failed save the pushed snapshot is popped again, so a
failed `ctrl+s` leaves no undo step. **Open for PDR (UX, not boundary):** `u` with a draft pending — ARQ's
recommendation is that `u` acts on saved state only and the draft survives, re-diffed against the restored
values; if the cursor's node disappears, the node-change guard fires.

### D5 · Other writers while a draft is pending

Structural actions (`a`, `x`, `A`, `X`, `u`) keep writing the whole graph immediately — they are already
explicit gestures, and the draft is **not** in `self.graph` until saved, so they never carry it. That is
also why a failed save must restore the graph (risk A-10). Attachments are not inspector fields (they go
through prompts), so R2 does not reach them.

## 4 · `docs/ARCHITECTURE.md` amendment (this branch)

- Header: last amended by this batch, with an amendment note stating **no boundary move, no new edge, one
  A3**, and that every new row is a commitment, not a present-tense claim.
- §2: `widgets` row gains the draft (and what it must not do); `screens` row gains `DraftGuardScreen`
  (planned); the stale `app.py` fact corrected (1709 lines / eleven → 4957 / ten, re-executed); one rule
  added: paths outside `mapper/` (`tests/`, `docs/`, `.dev-flow/`, `fixtures/`, `prototypes/`) are classified
  by file, so the staleness rule does not fire on test edits while the parallelisation rule still applies.
- §3: **unchanged** — `screens` already may import `design` and `keymap`; `app` already may import
  `screens` and `widgets`. Dependency direction stays `app → screens → {design, keymap}`,
  `app → widgets → {design, model, keymap}`.
- §4: `KEYMAP` seat marked in motion (Inc-1: `ctrl+s`, `draft` modal scope); `FieldCommitted` row (present,
  to be removed, full consumer census); new rows for the inspector draft surface and `DraftGuardScreen`.
- §5: R-012 (draft owner), R-013 (remove, pull), R-014 (modal in `screens`).
- §6: this batch's worksheet and risks A-8…A-12 replace the superseded batch-01 worksheet.

## 5 · Planned file set per story and the increment cut

| Story | Source files | Test / record files |
|---|---|---|
| US-001 | `mapper/widgets/inspector.py`, `mapper/keymap.py`, `mapper/screens/draft_guard.py` *(new)*, `mapper/app.py` | `tests/test_inspector.py`, `tests/test_g6_store_surrogates.py`, `tests/test_worklist_safety.py`, `tests/test_key_dispatch.py` (whole-seat pin `:137`), a new draft-save AT file, plus whatever the D2 census adds |
| US-002 | none | a new test file for AT-044 (doubled `?`); AT-025b reconciled to `tests/test_repair_cycles.py:501…664` in the ledger |
| US-003 | none | ledger + `.dev-flow/BACKLOG.md` (AT-041/042 reconciled, AT-033/034/035 retired) |
| US-004 | none | `tests/test_help_scope.py:93,365`, `tests/test_en7.py:246`, `tests/test_repair_layout.py:118` |

| Inc | Content | Source files | Parallel with |
|---|---|---|---|
| Inc-1 | US-001: draft, `ctrl+s`, one-snapshot save, `FieldCommitted` removed, node-change guard, modal | 4 (at cap) | Inc-4; Inc-3 conditionally (D2 census) |
| Inc-2 | US-001: leave-screen, link-follow (if ruled), quit guards | 1 (`app.py`) | Inc-3, Inc-4 — **not** Inc-1 (shares `app` and consumes Inc-1's surface) |
| Inc-3 | US-004 deflake | 0 | Inc-1 (conditional), Inc-2, Inc-4 |
| Inc-4 | US-002 + US-003 | 0 | all, **after the re-cut**: AT-044 in its own file, not `tests/test_help_scope.py` |

**Merit order:** Inc-3 → Inc-1 → Inc-2 → Inc-4. FLAKE-2 lives in a file the whole-branch gate runs; fixing
the instrument first keeps Inc-1's gate honest. A4 stays not-fired if the batch keeps one lane; the table
says where a second lane would be legal, not that one is owed.

## 6 · Risks

| Risk | Kind | Mitigation |
|---|---|---|
| A base `on_*` handler survives and double-commits (MRO dispatch) | operational | in-place change, no subclass; sha256 AT on `.mmd` + `_nodos.yml` |
| Draft wiped by the per-repaint rebuild | operational | overlay in `_rows`; guard at `app.py:3281` |
| Failed save leaves draft values in `self.graph`, written later by a structural save | data integrity | restore graph + pop snapshot on failure; AT with a failing store |
| An exit not guarded (`ctrl+q`, link-follow) silently drops a draft | UX / data loss (unsaved only) | guard method shared by all exits; ATs per exit; Inc-2 closes before merge |
| Modal paints a hostile title | security | `markup=False` (SEC-H2); security-reviewer at PDR |
| `ctrl+s` swallowed by the terminal (XON/XOFF) | operational | `executed` on the prototype (verdict: "deliberate edit + `ctrl+s` → written", two runs); Textual runs the tty raw |
| Inc-1 at the cap leaves no headroom | budget | R-014's reopen clause: fold the modal into `app.py` (3 files) if a fifth source file appears |
| Lock-in | n/a — no new dependency | — |

## 7 · What would change this map

- A second editing surface needs drafts → R-012 reopens, the draft moves to `model` or its own module (A1).
- A fifth source file is needed in Inc-1 → R-014 reverses (modal into `app.py`).
- The operator rules that a draft must survive leaving the screen (overturning R1) → the draft's owner
  moves to `MapperApp` (like `undo_stacks`), and the widget only renders it.
- PDR rules link-follow is not an exit → D3's link row drops; the stale-graph risk is then accepted in writing.

## Evidence checklist

- ✓ Constraints stated, each `executed` or `n/a — <reason>` — §2 table.
- ✓ 2+ alternatives where a real decision exists — D1 (3 owners), D2 (remove vs reshape), D3/R-014 (screens file vs `app.py`).
- ✓ Non-applying constraints marked `n/a — <reason>` — cost/latency, privacy, deadline, lock-in.
- ✓ Recommendation tied to constraints — D1 to the widget ban + file budget; D2 to the save-result ordering; R-014 to R-009 and `#D9`.
- ✓ Risks listed (operational, security, data integrity, budget, lock-in) — §6 and `docs/ARCHITECTURE.md` A-8…A-12.
- ✓ Cost / latency — `n/a — local TUI; one whole-graph write per explicit save, fewer writes than today`.
- ✗→n/a Diagram — `n/a — the flow is one choke point per exit, given as the D3 table; no new module graph to draw`.
- ✓ What would change the recommendation — §7.
- ✓ A3 consumer census with grep evidence, tests included — D2 table (`grep -rn "FieldCommitted\|field_committed"`).
- ✓ Map is checkable: every planned file falls under a declared module (`mapper/widgets/*.py`, `mapper/keymap.py`, `mapper/screens/*.py`, `mapper/app.py`); test/record files classified by file per the new §2 rule.
- ✓ Parallelisation rule applied mechanically — §5 and `docs/ARCHITECTURE.md` §6 pair table.
- n/a Two-layer requirements (US→AT→outcome, US→HLR→LLR→TC) — `n/a — ARQ runs before derivation; the map defines the HLR sections that carry them`.
- `planned` B1 test census for "type, `↵`/blur, file changed" oracles — candidate set in D2, run at PDR.

ARQ: approve-map
