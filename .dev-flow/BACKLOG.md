# BACKLOG — mapper

> **Canonical cross-batch queue.** Read at Phase 0 of every batch as the source of candidate stories
> and open carries; reconciled at every batch close. One home per item — if it is open, it lives
> here and nowhere else.

| Field | Value |
|---|---|
| Last refresh | **2026-08-27** (`2026-08-26-repair-batch` close) |
| Base ref at refresh | `origin/master` = `d6b60e6` (the batch's own commits land on top) |

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
| ~~B-07~~ **DONE** `2026-08-26-repair-batch` — closed as a CLASS by `TC-R38`, an AST census over every non-constant `notify` message. | ~~**N-14 remainder**~~ — uncoerced `notify` / `_event_toast` sinks on the repo, import, template and export paths (`app.py` ~`:626 :640 :661 :666 :729 :1024 :1027 :1671 :1673`). Same class as the ones fixed in batch 01 | Inc-4 sign-off | Enumerated, not left to rediscovery |
| B-08 | **N-4 refusal shape** — userinfo URLs are refused as `REFUSED_SCHEME`; accurate outcome, misleading reason. Needs its own status word | Inc-4 sign-off | |
| B-09 | `AT-N06c` is named in `01-requirements.md` but has no dedicated node — it is genuinely discharged by two unit tests (`test_no_seat_entry_binds_tab`, `test_llr_n06_5_no_screen_binds_tab_outside_the_recorded_exceptions`); reconcile the id or retire it | PR gate L-1 | Not a coverage hole; an id-hygiene one |
| ~~B-10~~ **DONE** `2026-08-26-repair-batch` — `TC-R38` is the artifact this asked for, one batch late. | ~~The `notify(` source census~~ the security sign-off conditioned N-2/N-14 on was never written as an artifact — B-07's line list is its partial substitute and may go stale | PR gate M-2 | |
| B-11 | Security sign-off carries not yet elsewhere: M-W, M-X, M-Y, M-AE, N-11 | PR gate M-4 | Enumerated so they are findable |
| B-06 | Security minors: alternate-data-stream targets, `urlparse` vs `urlsplit`, no executable-extension policy, U+202E passes `plain()` | Inc-4 sign-off | Explicit carries, not closed quietly |

### Process carries

| # | Item | Origin |
|---|---|---|
| P-01 | **A counterfactual must include a plausible WRONG implementation, not only deletion.** Two reviewer substitutions left the suite green where deletion reddened it. Portable — belongs upstream in the flow, not only in this repo | post-mortem §2.1 |
| P-02 | Derive census input sets from the deleted code, not from strings chosen by eye | post-mortem §2.2 |
| P-03 | Re-run the C-21 increment re-cut after **every** amendment, not only the first — batch-01 exceeded the source-file budget in 3 increments partly because of this | post-mortem §2.5 |
| P-04 | Never spell a control-character escape into source or into an evidence artifact; construct it (`chr(0)`) or describe it. C-56's family, extended to comments | post-mortem §2.4 |
| P-06 | **When a structure is the single source of truth for derived artifacts, pin the WHOLE structure.** Three partial pins of the keymap seat each passed review-breaking mutations; only a full `{(scope,key): (action,label,glyph)}` set-equality spec holds. Portable | post-mortem §2.4c |
| P-07 | **Every probe needs a positive control.** A regex escape collapsed to a literal backspace byte, so a scanner matched nothing and passed on everything — silently, unlike the two parse-breaking incidents | post-mortem §2.4b |
| P-05 | Treat a flaky test as a poisoned instrument: it invalidates every counterfactual that touches it, not just its own run | post-mortem §2.3 |

---

## Shipped in `2026-08-26-repair-batch` (PR A — shipped-defect repair)

| Item | Evidence |
|---|---|
| **S-01a** a cycle in a `.mmd` crashed the app | refused at load, cycle path named in Spanish; `MapStore.save` refuses **before writing** (A-2) |
| **S-01b** renderers died on pathological depth | all three renderers iterative + capped; `resolve_document`'s recursion **deleted**, not de-recursed |
| **S-02** a non-string ficha field loaded clean and `coverage()` counted it as documented | scalars coerce, containers refused and recorded, operator told which node and field, map still loads |
| **S-07** canvas and inspector laid out off-screen whenever the rail was visible | `#map-rail` width rule; three regions disjoint and on-screen at 140×45 and 120×40 |
| **S-08** the help overlay painted 16 of 27 bindings | bindings region scrolls; all 27 reachable at three terminal sizes |
| **B-07** uncoerced `notify` / `_event_toast` sinks — *the class, not the instances* | `TC-R38` — an AST census over all 19 non-constant `notify` sites; derived, no exemption list, own vacuity guard |
| **B-10** the `notify(` source census batch 01's gate conditioned on and never wrote | `TC-R38` is that artifact, one batch late |

**Suite 245 → 429.** Ruff on the gate metric `mapper tests`: 29, unchanged (decision D13).

---

## New carries from `2026-08-26-repair-batch`

### Correctness

| # | Item | Origin | Note |
|---|---|---|---|
| B-12 | `-m slow` CI lane still unwired. The batch's own depth acceptance (16 nodes) runs **only** when someone types it | security `M5` | Run manually at this merge and green: `16 passed, 409 deselected` |
| B-13 | No suite-level wall-clock bound — nothing fails if a test **hangs** rather than fails | Inc-3 | The general form of the hazard fix A dissolved locally |
| B-14 | `test_at_r16b` is **load-sensitive**: failed once under sustained load, passes in isolation (20.4 s) and in clean full runs | Inc-4 close | Lives in the lane B-12 says nothing runs. Checked per `P-05`: no arm's verdict rests on it — `M10` reddens 4 other nodes, `M11` does not touch it |
| B-15 | `MAX_RENDER_NODES = 12000` admits ~50 s of frozen UI; render cost O(n²), measured | security `M4` | **Net improvement** — `master` has no cap and is ~1.4× slower per node. A UX judgement, not a defect |
| B-16 | `_pop_snapshot` unguarded against this batch's new raises (`MermaidError`, `MapStoreError`) | security `L5` | Unreachable today; the one `save` site resting on an invariant this batch made load-bearing |
| B-17 | `TC-R15`'s derivation and its oracle **share the predicate** `f.type in ("str", str)`, so an annotation-form change shrinks both sides at once | Inc-3 `F4` | Close by asserting the floor against fields whose annotation *mentions* `str` |
| B-18 | Three screens push `HelpScreen()` with **no scope**, resolving to `SCOPE_APP` | Inc-4 | Shadowed today by the app-level priority binding for `?`; `AT-R13` reddens if that changes |
| B-19 | `_event_toast` is safe by construction (`Text.assemble` does not parse markup) but **nothing asserts it** | Inc-4 close | A future change routing it through `notify` would be silent |
| B-20 | `_text_attributes()` recomputed once per node (`store.py:226`); `str` unreachable in `("str", str)` (`store.py:31`) | Inc-3 `F7`/`F9`, security `L4` | Declined twice with reason — cosmetic, and moving `store.py` after its battery bought a re-run for zero behavioural change |
| B-21 | `F2`'s four sibling malformed shapes still deny the map: a node entry that is a string, a node entry that is a list, the `nodes` block a list, `attachments` non-list | Inc-3 `F2` | `LLR-R03.5` covers only a malformed `fields` block. Widening is **B-01/`F-M5`'s** repair |
| B-22 | Operator identity and a Claude session UUID inside the `.dev-flow/**` battery transcripts | security `L2` | Harmless in a private repo; **a blocker for any public push** |

### Process

| # | Item | Origin |
|---|---|---|
| P-08 | **A gate that closes CONDITIONALLY has not closed.** Batch 01's security gate conditioned on a `notify` census (`B-10`); it was never written, the backlog predicted it would go stale, and one batch later the class cost **six rediscoveries across three reviews**. Either discharge the condition before merging, or the gate is a BLOCK | post-mortem §6 |
| P-09 | **A backlog entry naming a class is not a control.** Nothing reads the backlog at the moment the defect is being reintroduced. Only an executable census runs then. `B-07` enumerated the sites and the class recurred anyway | post-mortem §6 |
| P-10 | **A no-op mutation and an inert arm print the same `0` and demand opposite responses.** No-op ⇒ aim at the declaration that actually decides the property. Inert ⇒ rewrite the predicate, do not re-argue it. This batch re-argued one on arithmetic measurement refutes | post-mortem §5.2 |
| P-11 | **A negative control must be pre-registered.** `L4b`'s green is evidence only because "Expected GREEN" was written before it ran. Harnesses need an `expect: green` field so the summary stops reporting controls as inert arms | post-mortem §5.3 |
| P-12 | **A reviewer's remedy is a hypothesis.** Twice a proposed fix was written, executed and found not to work — the second time because the review had the right symptom and the wrong mechanism. Reproduce the mechanism, not the symptom | post-mortem §7 |
| P-13 | **A conjunctive criterion needs one mutation per conjunct.** `AT-R14`'s clip is two-dimensional; one arm mutated both at once and left the dimension that mattered unguarded | post-mortem §5.4 |
| P-14 | **Verify the evidence file on disk is the one the packet cites, by hash.** A sound-but-unlanded measurement is indistinguishable from one never taken | post-mortem §3 |
| P-15 | **A census's predicate must be shape-free.** `TC-R38`'s first version keyed on f-strings and missed `notify(str(exc), ...)`. A census with a shape-shaped hole does not close a class | post-mortem §6 |
| P-16 | **Recording that a tool is broken does not fix the tool.** The byte scanner's CRLF defect was documented in Inc-2b, claimed corrected in Inc-3, and still broken when Inc-4 reached for it | post-mortem §2 |

### From the merge gate (`04-validation.md`) — deferred under the tree freeze

All six touch `mapper/` or `tests/` and all six are one-expression fixes. **None was applied at the
close**, deliberately: the gate had already cleared on the tree as it stood, and the same session
had just been recorded (`P-1`) for editing a tree mid-gate. Cheapness is not a reason to move a
frozen tree.

| # | Item | Origin |
|---|---|---|
| B-23 | **`TC-R38`'s class-closure is root-bounded.** The shape dimension is closed; the *root* dimension is not — an alias or bare-name `notify` measures GREEN, and `_event_toast` is outside the walk entirely. 0 offenders and 0 aliases on the current tree, so no live defect; but the docstring's *"a new sink joins the census the moment it is written"* is false as written | gate `M-2` |
| B-24 | **`RENDERERS` hand-lists 3 of 6.** `LLR-R02.3`'s degradation bound is undeclared for `LaneRenderer`, `HybridLaneRenderer`, `RailTimelineRenderer`, and `TC-R14` iterates a 3-element hand-list that cannot report the missing fourth. `HLR-R02` verified TRUE by execution for all six at depth 5000, and the lane renderers are unreachable from `_current_renderer` — so it is latent until someone wires a lane view. Fix: `[(n, getattr(views, n)) for n in views.__all__]` | gate `M-5` |
| B-25 | **`TC-R25`/`TC-R26` assert set equality for 2 of 6 reachable help scopes.** `import`, `plug`, `repo` and `app` get no assertion in either direction. Fix: `sorted({b.scope for b in KEYMAP})` — and `TC-R26` already reaches for `KEYMAP` | gate `M-6` |
| B-26 | **`AT-R13` lacks the vacuity guard its sibling has.** `AT-R12` asserts `len(expected) >= 20`; `AT-R13` asserts nothing. If `bindings_for(SCOPE_HOME)` ever returned empty, `missing` is `[]` and the node passes having tested nothing | gate `L-4` |
| B-27 | **A comment claims a derivation that does not exist.** `test_repair_layout.py:43-44` says `WIDE_SIZES`/`NARROW_SIZE` are derived from the screen's own rule; they are literals and the arithmetic is only narrated. Failure is loud, so nothing is silently untested — but *a comment claiming derivation is worse than one admitting a sample, because it stops the next reader checking* | gate `L-5` |
| B-28 | **Two more hand-picked roots.** `TRAVERSAL_FILES` (2 files) roots `TC-R32`'s census; `DEEP_TARGETS` hand-lists 6 callables where `graph_touching_methods()` exists in the same file. Both mitigated by `TC-R29`'s whole-tree recursion census | gate `L-6` |

### Process, from the merge gate

| # | Item | Origin |
|---|---|---|
| P-17 | **Once a whole-branch gate is dispatched, the tree is FROZEN.** Findings arriving during it are queued, not applied. This session edited the tree under a running merge gate — doing to that reviewer precisely what it had instructed four reviewers not to do to it, in the same session, in writing, four times. Every measurement taken before the edits was voided and re-taken. **Knowing a rule and holding it under time pressure at the end of a long session are different capacities** | gate `P-1` |
| P-18 | **A hand-maintained census is a defect, including in a requirements table.** §6's AT/TC counts were wrong, corrected once at the re-gate (`G5`), and wrong again one increment later (`M-1`). Fourth instance in one batch of *the work was done and the record was not landed*. The count is now stated as the output of a walk over `tests/test_repair_*.py`, not maintained by hand | gate `M-1` |
| P-19 | **A hand-count in a carry is the same defect as a hand-count in a census.** `PLAN.md` said "three screens push `HelpScreen()` with no scope"; disk has five | gate `L-3` |
| P-20 | **A transcript that closes non-green must say why, in the transcript.** `mutation-battery-inc4-supplement-2.txt` closed `exit=1` and said nothing; C-46's restore proof was unmet as written until it was annotated at the close | gate `L-2` |
