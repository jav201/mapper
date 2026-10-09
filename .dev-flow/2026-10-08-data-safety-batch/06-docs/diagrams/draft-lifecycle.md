# Diagram — draft lifecycle of one inspector field — Batch 2026-10-08-data-safety-batch

> Phase 6 artifact (drafted by a Kimi `kimi-for-coding` unit; verified by the orchestrator). One Mermaid `stateDiagram` of a single inspector field's lifecycle, per US-001 / HLR-001…HLR-006. Every state and transition names a real symbol, grep-verified in `mapper/` (verification table below the diagram).

```mermaid
stateDiagram-v2
    [*] --> clean_shown : FichaInspector shows _shown_value(field)\n(mapper/widgets/inspector.py:313)

    clean_shown --> dirty : keystroke on_input_changed -> _put_draft\n(inspector.py:479-485; draft dict :87,:328)
    clean_shown --> dirty : state segment on_ds_segmented_changed -> _put_draft\n(inspector.py:498-503; HLR-006)
    dirty --> clean_shown : edited back to shown value: _put_draft pops the field\n(inspector.py:339; LLR-001.3)
    dirty --> dirty : ↵ keeps draft, leaves field\n(on_input_submitted :487-496; R7/HLR-005)

    dirty --> saved_clean : ctrl+s KeyBinding("ctrl+s",...,"save_draft")\n(keymap.py:184) -> action_save_draft -> _save_draft\n(app.py:3521-3557) -> _save_or_toast store.save (:3548)\n-> inspector.clear_draft() (:3553; one write, one undo :3543-3544)

    dirty --> guard_open : ANY exit: _guard_draft(proceed)\n(app.py:3462-3493) — node change (:3318),\nq/esc (:4935,:4970), link (:3799), a/x (:4791,:4841),\nA/X (:3659,:3696), ctrl+q walk (:5220)
    guard_open --> saved_clean : s = action_save -> dismiss("save")\n(draft_guard.py:82-83; keymap.py:249)\n-> _save_draft() True -> proceed (app.py:3482-3484)
    guard_open --> clean_shown : d = action_discard -> dismiss("discard")\n(draft_guard.py:85-86; keymap.py:250)\n-> inspector.clear_draft() -> proceed (app.py:3487-3489)
    guard_open --> dirty : esc = action_stay -> dismiss("stay")\n(draft_guard.py:88-89; keymap.py:251)\n-> on_hold, nothing proceeds (app.py:3490-3491)

    saved_clean --> dirty : keystroke (_put_draft, as above)
    clean_shown --> [*] : node has no draft: draft_node_id None\n(inspector.py:343-344)

    dirty --> failed_save : store.save raises inside _save_or_toast\n(app.py:262-284 -> False at :3548)
    failed_save --> reloaded_rediffed : _snapshots restored (:3561) ->\nstore.load (:3564) -> _establish_graph (:3576);\ndraft re-diffed vs disk (inspector.py:100-107):\nvalues on disk turn clean, rest stay dirty
    failed_save --> failed_save : reload ALSO raises: pre-save graph kept,\none toast "could not reload · draft kept ·\nleaving needs d (discard)" (app.py:3570-3575)
    reloaded_rediffed --> dirty : fields whose value did not reach disk\nstay drafted, marked ● unsaved (ALERT)
```

## Verification — every symbol grep-verified in `mapper/`

| Symbol used in diagram | Verified at | Command |
|---|---|---|
| `FichaInspector._draft` / `draft_node_id` | `mapper/widgets/inspector.py:83-87` | `grep -n "_draft_node_id\|_draft" mapper/widgets/inspector.py` |
| `_shown_value` | `mapper/widgets/inspector.py:313` | `grep -n "_shown_value" mapper/widgets/inspector.py` |
| `_put_draft` (insert/pop) | `mapper/widgets/inspector.py:328-344` | `grep -n "_put_draft" mapper/widgets/inspector.py` |
| `on_input_changed` (keystroke) | `mapper/widgets/inspector.py:479-485` | `grep -n "on_input_changed" mapper/widgets/inspector.py` |
| `on_input_submitted` (`↵` keeps draft) | `mapper/widgets/inspector.py:487-496` | `grep -n "on_input_submitted" mapper/widgets/inspector.py` |
| `on_ds_segmented_changed` (`state`) | `mapper/widgets/inspector.py:498-503` | `grep -n "on_ds_segmented_changed" mapper/widgets/inspector.py` |
| draft re-diff on re-show | `mapper/widgets/inspector.py:100-107` | `grep -n "re-diffs\|_shown_value(f)" mapper/widgets/inspector.py` |
| `clear_draft` | `mapper/widgets/inspector.py:295-297` | `grep -n "clear_draft" mapper/widgets/inspector.py` |
| `ctrl+s` → `save_draft` binding | `mapper/keymap.py:184` | `grep -n 'KeyBinding("ctrl+s"' mapper/keymap.py` |
| `s`/`d`/`esc` → `save`/`discard`/`stay` | `mapper/keymap.py:249-251` | `grep -n "SCOPE_DRAFT" mapper/keymap.py` |
| `UNSAVED_STYLE = darkside.ALERT` (● marks) | `mapper/widgets/inspector.py:36` | `grep -n "UNSAVED_STYLE" mapper/widgets/inspector.py` |
| `DraftGuardScreen` + `action_save/discard/stay` | `mapper/screens/draft_guard.py:20,82-89` | `grep -n "action_save\|action_discard\|action_stay\|class DraftGuardScreen" mapper/screens/draft_guard.py` |
| `_guard_draft` (guard decision point) | `mapper/app.py:3462-3493` | `grep -n "_guard_draft" mapper/app.py` |
| guarded exits (node change, q/esc, link, a/x, A/X) | `mapper/app.py:3318,3799,3659,3696,4791,4841,4935,4970` | `grep -n "_guard_draft" mapper/app.py` |
| quit walk | `mapper/app.py:5196-5220` | `grep -n "_quit_walk_open\|has_pending_draft" mapper/app.py` |
| `action_save_draft` / `_save_draft` | `mapper/app.py:3521-3581` | `grep -n "action_save_draft\|def _save_draft" mapper/app.py` |
| `_save_or_toast` (guarded store.save) | `mapper/app.py:262-284,3548` | `grep -n "_save_or_toast" mapper/app.py` |
| failure path: snapshots restore / `store.load` / `_establish_graph` / reload-failure toast | `mapper/app.py:3561-3576` | `grep -n "_establish_graph\|could not reload" mapper/app.py` |
| one error toast on failure | `mapper/app.py:3564-3569,3580` | `grep -n "could not save\|draft kept" mapper/app.py` |

Requirement ids: HLR-001…006 (`.dev-flow/2026-10-08-data-safety-batch/01-requirements.md:148-242`), operator rulings R1–R9 (`VERDICT-b36-prototype-2026-10-08.md:15-23`). Acceptance nodes AT-001…AT-015 verify each transition through the shipped surface (`01-requirements.md:298-317`).
