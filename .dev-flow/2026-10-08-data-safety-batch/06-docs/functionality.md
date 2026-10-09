# Functionality — mapper — Batch 2026-10-08-data-safety-batch

> Phase 6 artifact (drafted by a Kimi `kimi-for-coding` unit; verified by the orchestrator). Audience: technical stakeholder.

## 🔑 At a glance (read first)

- **What this batch added:** an inspector **draft model with an explicit save gesture** (`ctrl+s`) that closes the stray-write class (B-36), plus the FLAKE-2 deflake (B-98) and the acceptance-test debt B-100/B-101. BACKLOG marks all four DONE (`.dev-flow/BACKLOG.md:165,208,210,211`).
- **Capabilities:** per-node in-memory draft, updated per keystroke · `ctrl+s` = one whole-graph write + one undo step · red unsaved marks (`● unsaved (N)`) · `save · discard · stay` guard on every exit · failed-save reload rule · deterministic legend own-keys test · reconciled acceptance ids.
- **How to use it:** edit any inspector field, then `ctrl+s` to save; the guard (`s`/`d`/`esc`) answers every attempted exit with a pending draft.

---

## Detail (reference)

### The draft model (US-001 / HLR-001)

An inspector edit is now a **per-node, in-memory draft**, not a write. `FichaInspector` holds `_draft: dict[str, str]` keyed by schema field, live for the life of its `MapScreen` (`mapper/widgets/inspector.py:83-87`; definition `.dev-flow/2026-10-08-data-safety-batch/01-requirements.md:36-39`). Every keystroke routes through `on_input_changed` → `_put_draft` — the one mutator of the draft (`mapper/widgets/inspector.py:479-485`, `:328-344`; HLR-001 statement `01-requirements.md:148-162`). Nothing writes on blur, `↵` (`on_input_submitted` keeps the draft, `:487-496`; HLR-005), or the `state` segment (`on_ds_segmented_changed` drafts like every other field, `:498-503`; HLR-006, operator ruling R2 — one exception would bring the stray-write back, `VERDICT-b36-prototype-2026-10-08.md:16`). `FieldCommitted` and its handler were deleted (I-5; `03-increments/increment-003.md:27`).

### The save gesture (HLR-004)

`ctrl+s` is a new map-seat key row (`mapper/keymap.py:184`) → `MapScreen.action_save_draft` → `_save_draft` (`mapper/app.py:3521-3581`). The draft is applied to a **copy** of the whole graph (`base_graph`, never a focused subgraph — R-1/LLR-004.4), written through the two-phase whole-graph `MapStore.save` in exactly **one** call guarded by `_save_or_toast` (`mapper/app.py:262-284`, call at `:3548`), with exactly **one** undo snapshot; `u` undoes the save as one step and leaves the pending draft untouched (operator rulings R3/R5, `VERDICT-...:17,19`). On success each drafted field turns clean and the draft clears (`inspector.clear_draft`, `mapper/widgets/inspector.py:295-297`).

### The unsaved marks, in red (HLR-002, operator R8)

While a draft is pending, the inspector header paints `● unsaved (N)` and each dirty field label a `●`, both in `UNSAVED_STYLE = darkside.ALERT` (`mapper/widgets/inspector.py:36`, header `:227`, marker `:246`; ALERT token `mapper/darkside.py:55`). With the card hidden (87 columns or after `I`), the hint line prefixes `● unsaved (N) · ctrl+s save` in ALERT (`mapper/app.py:3441`); a focused field's hint reads `type to draft · ctrl+s save · esc leave field` (`mapper/app.py:3870-3871`). Colour choice is the operator's verbatim ruling "Usa código de colores, como el rojo para alertar que hay contenido no guardado" (R8, `VERDICT-...:22`; state.json decisions_log PDR entry).

### The save · discard · stay guard on every exit (HLR-003, verdict R1/R4/R6)

`DraftGuardScreen` is a modal answering exactly one of `save`/`discard`/`stay` (`s`/`d`/`esc` from the `draft` seat scope, `mapper/keymap.py:246-251`; `mapper/screens/draft_guard.py:20-89`). It decides nothing and writes nothing; `MapScreen._guard_draft(proceed)` pushes it and acts on the answer (`mapper/app.py:3462-3493`). One rule covers every exit (`VERDICT-...:15` R1): node change (`app.py:3318`), leaving the map screen with `q`/`esc` (`:4935`, `:4970`), following a link (`:3799`), structural writes `a`/`x` (`:4791`, `:4841`) and `A`/`X` (`:3659`, `:3696`), and quitting — `action_quit` walks every `MapScreen` with a draft, top first, and never wedges under an open guard (`app.py:5196-5220`, `has_pending_draft`; LLR-003.5). Guard title `unsaved draft on «{title}» · {map_id}`, both parts through `darkside.plain` + `markup=False` so an ESC (0x1B) payload cannot reach the terminal (R9, `draft_guard.py:54-67`; AT-015).

### The failed-save reload rule (LLR-004.2)

On a raising store: the undo stack is restored whole (never popped), the map is **reloaded from disk** through the screen's own load path (`store.load` → `_establish_graph`, `mapper/app.py:3561-3576`), and the draft is **re-diffed against disk** — fields whose value reached disk turn clean, the rest stay drafted. Nothing on that path writes the map. If the reload itself fails, the pre-save in-memory graph is kept and one error toast reads `could not reload · draft kept · leaving needs d (discard)` (`app.py:3570-3575`). Otherwise one toast names the map and the exception **type** only: `could not save '<map>' (<ErrorType>) · draft kept · ctrl+s to retry` (`app.py:3564-3569`; `_save_or_toast(..., toast=False)`, Inc-1c U4). This single rule replaced an earlier disk-hash classification design as unsound (P2 round 3; operator ruling 'Simplificar y seguir', state.json decisions_log).

### The FLAKE-2 fix (US-004 / B-98 / HLR-009)

The legend own-keys flake was the **test instrument**, not the product: Textual 8.2.8 `Widget.scroll_to` defaults `immediate=False`, queuing `_scroll_to` via `call_after_refresh`; under load the queued call landed inside the next key's measurement window, making an inert key (`left`) read as effective (`spike/FLAKE-2-spike.md:15-17`). Fix: `immediate=True` + a settle assertion at the four `scroll_to(animate=False)` sites, plus an injected-delay regression arm (`delay_deferred_scroll` / `late_scroll`, adapted from `spike/red_green_flake2.py`) — deterministic RED 2/2 before, GREEN 2/2 after (`spike/FLAKE-2-spike.md:29-38`; increment-001.md §1; BACKLOG B-98 DONE `.dev-flow/BACKLOG.md:208`).

### The acceptance-test debt closed (US-002 / US-003 / B-100 / B-101)

- **AT-044** (doubled `?` opens no second legend) realised as `tests/test_double_question_mark.py::test_at_044_a_doubled_question_mark_opens_one_legend` (HLR-007, LLR-007.1; `.dev-flow/BACKLOG.md:210`).
- **AT-025b** (a damaged map declares itself on its own card) reconciled to the five `LLR-N13.1.5` nodes and joined into one node in Inc-6 (`tests/test_repair_cycles.py:501…664`; increment-006.md §1).
- **AT-041** reconciled to `test_at_r12_pressing_help_presents_every_map_binding`; **AT-042**'s largest-set arm reconciled and its two missing arms minted (`test_tc_r25_…[app]`, `test_tc_r25b_a_screen_declaring_no_scope_presents_the_app_set`); **AT-033/034/035 retired** with the deferred US-N14 (HLR-008; `.dev-flow/BACKLOG.md:211`; increment-004.md §1).

### Components / modules touched

| Module | Role in this batch |
|--------|--------------------|
| `mapper/widgets/inspector.py` | the draft seat (`_draft`, `_put_draft`, `draft_values`, `clear_draft`), per-keystroke drafting, `● unsaved (N)` header + field markers in ALERT |
| `mapper/app.py` | `_save_draft`/`action_save_draft` (one write, one undo, failure reload), `_guard_draft` + every guarded exit, hint-line unsaved prefix, quit walk |
| `mapper/screens/draft_guard.py` | new `DraftGuardScreen` modal (save · discard · stay; ESC-safe title) |
| `mapper/keymap.py` | `ctrl+s` → `save_draft` map-seat row; new `draft` modal seat scope (`s`/`d`/`esc`) |
| `mapper/darkside.py` | no change — colours read from existing tokens (ALERT) |
| `tests/test_draft_save.py`, `tests/test_draft_exits.py` etc. | AT-001…AT-015 acceptance nodes; FLAKE-2 deflake in `tests/test_help_scope.py`; AT-044/AT-042/AT-025b nodes |

### Evidence

- Gate: one complete run on `cab8181` — **2920 passed, 24 deselected, 3 xfailed, EXIT_CODE=0** (`.dev-flow/2026-10-08-data-safety-batch/04-validation.md:9`; test ledger 2800 → 2923 collected, `:15`).
- Requirements: 36/36 (9 HLR + 27 LLR) verified, 0 blocker fails (`04-validation.md:11`).
- Operator real-terminal smoke (PDR C14): performed 2026-10-09 — `ctrl+s` saved without freezing, `ctrl+q` raised the guard; verdict PASS-WITH-NOTES with accepted residuals A-13…A-15, F5 (`04-validation.md:18,253,261-264`).
