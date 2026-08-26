# BACKLOG — mapper

> **Canonical cross-batch queue.** Read at Phase 0 of every batch as the source of candidate stories
> and open carries; reconciled at every batch close. One home per item — if it is open, it lives
> here and nowhere else.

| Field | Value |
|---|---|
| Last refresh | **2026-08-25** (`2026-08-25-ui-next-batch-01` close) |
| Base ref at refresh | `origin/master` = `695bd2d` (the batch's own commits land on top) |

---

## Shipped in `2026-08-25-ui-next-batch-01`

| Item | Evidence |
|---|---|
| US-N01 edición in-situ — editable inspector, schema labels, required-empty flags, persisted | `df74da1` |
| US-N02 adjuntos — add / open / remove behind a confined OS-handler boundary | `f37d824`, `52d77bb` |
| US-N03 keymap único — one seat, executing palette, scoped help, visible keybar truncation | `167e97b`, `0b69fe2` |
| US-N04 worklist de cobertura — jump + focus the gap, cycle next-missing | `48a8e68` |
| US-N05 seguridad — confirm every destructive action, app-level undo | `48a8e68` |
| HLR-N06 focus model — adopted mid-batch; live-region signal, escape hatch, collapsible regions | `0b69fe2` |
| The double ficha render, and `HintLine` having no setter | `df74da1` |

---

## Open — carried forward

### Next batch (already decided)

- **Batch 2 · variant B «atlas»** — canvas pan, fold/expand pills, minimap + viewport, braille edges
  (fixes the dead `Canvas.rows()` dots), search hit count. Prototype: `prototypes/ui_next/`, variant B.
- **Batch 3 · variant C «plano»** — repo screen re-tinted to darkside: dimension spans, extension
  leaders, hatch gaps, titleblock, save-repo-as-map.

### Correctness carries

| # | Item | Origin | Note |
|---|---|---|---|
| B-01 | `MapStore.load` raises `KeyError` on a sidecar attachment missing `path:` — one malformed node denies the **whole map** | security review F-M5 | Not a new defect; outside batch-01's file budget |
| B-02 | `mapper/screens/factory.py:343` imports `mapper.app._PromptScreen` — the one live dependency-ban violation | ARQ finding A-7 | Fixing it silently was explicitly rejected; it needs its own decision |
| B-03 | ~20 legacy `rich.markup.escape` call sites in `app.py`'s other renderers emit **visible backslashes** — the escape is a no-op in a `Text` path | security review F-M2 | `darkside.plain()` now exists as the replacement |
| B-04 | Four modal screens (`FactoryScreen`, `EditorScreen`, `SettingsScreen`, `CoverageScreen`) still hold local `BINDINGS` | batch-01 Inc-1 | `keymap.UNMIGRATED_SCREENS` names them; two tests fence the list |
| B-05 | The canvas's selection block is painted by a focus-unaware frozen renderer, so the global "at most one ACCENT run" invariant is unreachable | Amendment 3 | Close it in batch 2, which reworks that renderer anyway |
| B-07 | **N-14 remainder** — uncoerced `notify` / `_event_toast` sinks on the repo, import, template and export paths (`app.py` ~`:626 :640 :661 :666 :729 :1024 :1027 :1671 :1673`). Same class as the ones fixed in batch 01 | Inc-4 sign-off | Enumerated, not left to rediscovery |
| B-08 | **N-4 refusal shape** — userinfo URLs are refused as `REFUSED_SCHEME`; accurate outcome, misleading reason. Needs its own status word | Inc-4 sign-off | |
| B-09 | `AT-N06c` is named in `01-requirements.md` but has no dedicated node — it is genuinely discharged by two unit tests (`test_no_seat_entry_binds_tab`, `test_llr_n06_5_no_screen_binds_tab_outside_the_recorded_exceptions`); reconcile the id or retire it | PR gate L-1 | Not a coverage hole; an id-hygiene one |
| B-10 | The `notify(` source census the security sign-off conditioned N-2/N-14 on was never written as an artifact — B-07's line list is its partial substitute and may go stale | PR gate M-2 | |
| B-11 | Security sign-off carries not yet elsewhere: M-W, M-X, M-Y, M-AE, N-11 | PR gate M-4 | Enumerated so they are findable |
| B-06 | Security minors: alternate-data-stream targets, `urlparse` vs `urlsplit`, no executable-extension policy, U+202E passes `plain()` | Inc-4 sign-off | Explicit carries, not closed quietly |

### Process carries

| # | Item | Origin |
|---|---|---|
| P-01 | **A counterfactual must include a plausible WRONG implementation, not only deletion.** Two reviewer substitutions left the suite green where deletion reddened it. Portable — belongs upstream in the flow, not only in this repo | post-mortem §2.1 |
| P-02 | Derive census input sets from the deleted code, not from strings chosen by eye | post-mortem §2.2 |
| P-03 | Re-run the C-21 increment re-cut after **every** amendment, not only the first — batch-01 exceeded the source-file budget in 3 increments partly because of this | post-mortem §2.5 |
| P-04 | Never spell a control-character escape into source or into an evidence artifact; construct it (`chr(0)`) or describe it. C-56's family, extended to comments | post-mortem §2.4 |
| P-05 | Treat a flaky test as a poisoned instrument: it invalidates every counterfactual that touches it, not just its own run | post-mortem §2.3 |
