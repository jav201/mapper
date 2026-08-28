# Increment 002 — `LLR-N07.2.2a` · `LLR-N07.2.3` · `HLR-CNV.3` — the A3: `ViewState` and `IRenderer`

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Increment | `002` |
| Lane | none — serial batch |
| Requirement(s) | `LLR-N07.2.2a` (signature migration, byte-identical) · `LLR-N07.2.3` (the two new types) · `HLR-CNV.3` with `LLR-CNV.3.1` (focus-aware selection, carry `B-05`) |
| Acceptance | `AT-010` · white-box the `test_llr_n07_2_2a_*` and `test_llr_n07_2_3_*` nodes · `TC-020` |
| Protocol | **FULL** per `A-91` — the A3 contract |
| Agent | `software-dev` |
| Date | 2026-08-28 |
| Base | `4eaba35` (Inc-1) |

---

## 1 · What changed

**The batch's headline A3 landed: all six `render` definitions and all 27 arg-ful call
sites moved to `(graph, state)` in one increment, and the protocol they implement exists in code
for the first time.** Executed at `3fe0e4b`, `IRenderer` was a Python type **zero** times — it
survived only as prose in two comments, so the interface the batch was migrating had never been
written down.

- **`mapper/views/state.py` (new)** declares `ViewState` — frozen, every field defaulted — and
  `IRenderer` as a `runtime_checkable` Protocol. Initial roster: `selected_id`, `w`, `h`,
  `focus_owner`, `query`, `diff`.
- **`with_header` is gone, not migrated.** It was a parameter **no caller ever passed** —
  one declaration, one use, zero call sites supplying it — so the header was unconditional in fact
  and is unconditional in code. Deliberately not a `ViewState` field, which discharges the
  two-roster collision `#D2` left open.
- **`HLR-CNV.3` / carry `B-05`:** the canvas painted a full-strength selection block regardless of
  where the keyboard was, so the rail, canvas and inspector each claimed the selection at once.
  The selection is still **shown** while another region has focus — losing your place is worse than
  a soft highlight — but it stops claiming to be active.
- **One measured defect closed as a side effect, which is what the parameter object is *for*:** the
  export site passed `query` and omitted `diff`, so an SVG exported during a diff silently lost its
  tinting. Both sites now build state through one `_view_state()` constructor, so there is no second
  argument list to under-fill.

---

## 2 · Files modified

| File | Kind | Change |
|---|---|---|
| `mapper/views/state.py` | source | **new** — `ViewState`, `IRenderer`, `FOCUS_OWNERS` |
| `mapper/views/layered.py` | source | signature; `with_header` inlined; focus-aware selection tone |
| `mapper/views/lane.py` | source | three signatures |
| `mapper/views/outline.py` | source | one signature |
| `mapper/views/radial.py` | source | one signature |
| `mapper/app.py` | source | `_focus_owner()`, `_view_state()`, three call sites |
| `tests/test_a3_census.py` | test | **new** — the AST census and the protocol guards |
| `tests/test_layered.py` · `test_app.py` | test | `AT-010`, `LLR-CNV.3.1` |
| 8 further test files | test | call-site migration |
| `docs/ARCHITECTURE.md` | doc | the `ViewState` row moves `COMMITTED, NOT PRESENT` → `PRESENT` |
| `.dev-flow/**` | doc | `A-89` through `A-91`, `PLAN.md` D32–D35, `state.json` |

| Count | Value |
|---|---|
| **SOURCE files** | **6 — DECLARED BREACH**, unchanged from `#D5` |
| Test files | 11 (uncapped) |
| Doc files | 4 (outside the count) |

⚠ **The 6-file breach is the one `#D5` declared and re-ratified at the re-scope.** It cannot be cut
smaller: the gate is *"zero call sites of the old shape survive"*, and a partial migration leaves
two contracts live at once — which is risk `A-1` verbatim. Splitting by renderer would mean shipping
an increment whose own acceptance criterion is knowingly false.

---

## 3 · How to test

```bash
cd <repo root>
set PYTHONUTF8=1
python -m pytest -q
python -m pytest -q -m slow
python -m ruff check mapper/ tests/
python -m pytest tests/test_a3_census.py tests/test_layered.py -q
python -m pytest tests/test_app.py -q -k focus_owner
```

---

## 4 · Test results

| Lane | Result |
|---|---|
| fast | `712 passed, 17 deselected in 63.05s` — exit 0 |
| slow | `17 passed, 712 deselected in 24.43s` — exit 0 |
| ruff `mapper/ tests/` | **28** — the Inc-1 figure, **zero new** |
| ruff `fixtures/` | `All checks passed!` |

**Ruff reconciled, not accepted.** It first read **30**. Both new errors were mine — `lane.py` and
`outline.py` unpacked a `w` those two renderers never use — and both are gone. The remaining 28 were
verified byte-identical at `4eaba35` (`layered.py` `Node`, `app.py` `re`, `test_app.py` `pytest` and
`HelpScreen`).

### Signed-balance test ledger

`post = base − deleted + added` → **`712 = 694 − 0 + 18`** ✓

| Source | Added |
|---|---:|
| `tests/test_a3_census.py` (new) | +12 |
| `tests/test_layered.py` (`AT-010`, 3 arms) | +3 |
| `tests/test_app.py` (`LLR-CNV.3.1`) | +1 |
| `test_repair_artifact_claims.py` — **derived** arms | +2 |

**The last two were not written by hand and are worth naming.** That module builds its parameter set
from the citations in the artifacts, so adding a `state.py` citation to the module map *created two
arms that check it*. Confirmed by diffing collected node ids against `4eaba35` in a detached
worktree: **+2 added, 0 removed**, both `[state.py]` arms.

### The A3 census — the increment's actual gate

| Threshold | Result |
|---|---|
| 1 · migrated definitions **equal** the derived definition set | **6 of 6**, all `(self, graph, state)` |
| 2 · `**kwargs` across that set | **0**; the explicit `query` parameter left with them |
| 3 · call sites of the old shape surviving | **0** of 27 arg-ful sites |
| 4 · byte identity | every digest held; **no digest was re-baselined in this increment** |

**Instrument: `ast`, never `grep`.** `.render` names two different protocols here — Textual's
zero-arg `Widget.render()`, which must **not** migrate (25 sites), and the map renderer, which must
(27). A line-oriented count answers neither, and a grep at `3fe0e4b` returned one site more than the
AST: a mention of `renderer.render(...)` inside a docstring. The census carries that as an executed
control — it asserts the instrument sees a real call and does **not** see the docstring.

### Standing re-run obligation from Inc-1 — DISCHARGED, per node

`AT-007` and `AT-009` are Inc-1 deliverables whose whole chain this increment re-signatures, and a
byte-identity gate cannot see a chain that was already broken. Re-run, per resolved node:

```
test_at_007_a_layer_write_reaches_the_painted_output                       PASSED
test_at_008_a_background_at_the_last_cell_paints_and_one_past_it_does_not  PASSED
test_at_008_an_invalid_dot_coordinate_paints_nothing_and_raises_nothing    PASSED
test_at_007b_braille_edges_reach_the_painted_output                        PASSED
test_at_007b_the_containment_arm_nothing_the_renderer_painted_is_lost      PASSED
test_at_007b_a_single_node_graph_paints_no_braille_for_the_stated_reason   PASSED
test_at_009_the_exported_file_carries_the_canvas_layers                    PASSED
test_at_009_the_negative_control_shows_size_alone_proves_nothing           PASSED
test_at_009_the_exported_svg_carries_no_coerced_code_point                 PASSED
```

**Inc-2 does not close with either red.**

### Two defects the new tests found in themselves

Both were mine, and both are the class this batch keeps paying for:

1. **The headless-boundary check was a substring search** for `"textual"`, and it matched
   `state.py`'s own docstring *saying it imports no Textual*. A substring cannot tell an import from
   a mention. Rewritten over `ast.Import`/`ast.ImportFrom` nodes, with a positive control (a real
   import is seen) and a negative one (prose is not).
2. **`renderer_classes()` swept in `IRenderer` itself**, and a Protocol cannot be instantiated. The
   contract is not a satisfier of itself.

---

## 5 · Risks

1. **`query` is transitional.** The renderer should receive resolved id sets, never a predicate it
   interprets — and there are two live definitions of "what matches" in this tree that disagree
   (`P-18`). `Inc-4` replaces it with `hits`. Until then `layered` still interprets a string.
2. **The search-highlight surface has ZERO test coverage.** Executed: no test anywhere passes
   `query=` or `diff=` — only `app.py` at three sites. That is why the migration is safe to make
   byte-identically, and it is also a hole `Inc-4` must close rather than inherit.
3. **`focus_owner` widens the app's behaviour** in a way no digest can see: the digests all render
   through the default `""`. `AT-010` is what covers the non-default arms.
4. **Adding a field to `ViewState` is additive by construction** — but only while every field keeps
   a default. The moment one does not, the next increment's addition becomes a migration.

---

## 6 · Pending items / spec deviations

| id | Item |
|---|---|
| `A-92` | **`HLR-CNV.3` was assigned to no increment.** §5.4 describes Inc-2 as "signature only, behaviour-neutral" while §3.3 headers it "Inc-1 and Inc-2", and `AT-010`/`TC-020` were traced with no owner — the same orphan class as `AT-009`. Landed here: §5.4's declared 6-file set for Inc-2 is **exactly** the set `HLR-CNV.3` needs, with nothing added. "Behaviour-neutral" is scoped to the **default** `ViewState`, which is what makes the byte-identity gate and the focus-aware tone compatible |
| `A-93` | `with_header` removed rather than migrated — dead parameter, zero call sites. Discharges `#D2`'s open two-roster collision; `ARCHITECTURE-proposed-at-ARQ.md:235,275` still name it and are owed the strike |
| `B-44` | **DISCHARGED** — the module map's `canvas` row is now pinned against `inspect.signature`, not prose |
| `B-50` | The export-during-diff fix is a **behaviour change** shipped inside a "behaviour-neutral" increment. Deliberate, `#D4`'s stated motivation, and covered — but it is the one thing in Inc-2 a byte-identity gate cannot see |
| V-5 | `LLR-N07.2.3`'s provisional `tests/test_view_state.py` landed inside `tests/test_a3_census.py` — one file for one census |

---

## 7 · Suggested next task

**`Inc-3` — US-N06 «escala» (pan, fold, overflow) plus `LLR-COERCE.2` as widened by `A-89`.** It
carries the `B-47` fold: the coercion guarantee must quantify over **every** renderer feeding an
operator-visible sink, derived rather than named, so the batch's security story stops being
conditional on which view the operator is in. Declared 5-source-file breach.

---

## 8 · RED counterfactual — executed, per arm

| Field | Value |
|---|---|
| Where it ran | a **detached copy** in the session scratchpad, never the repo |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` |
| Arms resolved at baseline | **208**, asserted green before any verdict was trusted |
| Verdict granularity | per resolved node id; the process exit code is never read |
| Restore proven by | sha256 back to pre-mutation on all **10** touched files after every mutant |
| Post-battery control | `208/208 green` |

| Mutant | Verdict | Arms |
|---|---|---:|
| `M-N07.2.2a-a` — ONE definition reverted to the old shape | **RED** | 7 |
| `M-KWARGS` — a definition keeps `**kwargs` beside the new shape | **RED** | 2 |
| `M-CALLSITE` — ONE call site reverted to the old keyword shape | **RED** | 2 |
| `M-N07.2.3-b` — a `ViewState` field made required | **RED** | 7 |
| `M-FROZEN` — `ViewState` unfrozen | **RED** | 2 |
| `M-B05-a` — the selection tone made constant again | **RED** | 2 |
| `M-B05-b` — the UNKNOWN owner dims | **RED** | 5 |
| `M-FOCUSWIRE` — the screen reports a constant owner | **RED** | 1 |
| `M-HEADLESS` — `views/state.py` imports Textual | **RED** | 1 |
| `M-B44` — the map row drops the tone parameters | **RED** | 1 |
| `M-N07.2.3-a` as first written | **GREEN — INERT**, and the mutation was at fault | 0 |

**The inert result was my mutation, not a weak guard, and chasing it produced the better
evidence.** I had mutated the signature guard's own condition to `if False`, which makes the guard
trivially pass and demonstrates nothing — a mutation shaped to succeed. The property
`M-N07.2.3-a` actually names is that **`isinstance` alone is green on an unmigrated tree**, so the
honest probe reverts a signature in the **product** and asks which of the two thresholds notices:

```
ONE renderer's signature reverted in the PRODUCT:
  threshold 2  isinstance / member presence : PASSED
  threshold 3  signature equality           : FAILED
```

**The pair discriminates**, and the requirement's warning is confirmed rather than restated:
`runtime_checkable` checks member presence only, every renderer had a `render` attribute before the
migration, and threshold 3 is what carries the contract.

**`M-B05-b` is the other result worth reading.** Making the *unknown* owner dim reddens `AT-010`'s
default arm **and all four `LayeredRenderer` byte-identity digests** — which is the mechanical
demonstration that `focus_owner=""` reproducing today's paint is exactly what lets a behaviour
change and a byte-identity gate coexist in one increment.

### A flaky test, found by the harness and fixed rather than re-run

The battery **refused to report any verdict** on its first attempt: its baseline was not green, and
`test_llr_cnv_3_1_focus_owner_tracks_the_real_focus` had failed. It then passed in isolation five
times out of five, and the full target set passed at 216. So: **flaky, not order-dependent** — a
single `pilot.pause()` yields once, and on a slow pass no widget has taken focus yet, so every
sample reads the unknown owner and the "it changed" assertion fails for a reason unrelated to the
code under test.

Fixed by waiting, bounded, for a real focus before sampling — so a genuine never-focuses regression
still fails rather than hanging. Verified stable across **8** consecutive runs. A flaky acceptance
test is worse than no test: it teaches people to re-run instead of look, and the harness asserting
its own baseline is the only reason this surfaced at all.

**Harness debt paid at the same time:** `import battery` was re-executing round 1's entire mutant
loop on every later round, silently doubling the cost of rounds 4, 5 and 6. The helpers now live in
an import-safe module.

---

## 9 · Review response — BLOCK on 3 HIGH, all fixed, and one exposed a shipped defect

`code-reviewer` returned **BLOCK** with 3 HIGH, 6 MEDIUM, 4 LOW. **All three HIGH were real and I
reproduced each before fixing.** Verdict at `increment-002-code-review.md`.

| Finding | Sev | Disposition |
|---|---|---|
| **H1** the inverted map-truth guard is vacuous, and it replaced a working one | HIGH | **FIXED.** Confirmed by running the new assertion against the **baseline** document — the exact state it claims to forbid — where it **PASSED**. It split the whole document on the first occurrence of the filename, which sits in the prose preamble **131 lines above the row**, so the 400-char window never reached what it checked. Now anchored on the row, and the mutant round 7 lacked is added: reverting the row reddens it |
| **H2** the export leaks live keyboard focus into the SVG | HIGH | **FIXED.** Measured: the rail holds focus on mount, so `_view_state()` handed the export `focus_owner='rail'` and a **routine** export painted the selection in the *inactive* tone. Three controls missed it — the digests render a default state, the `AT-009` tests build their own `ViewState`, and §6 did not list it. Export now pins `focus_owner=""`, and a new arm drives the shipped export action and asserts the tone it hands the writer |
| **H3** `27` published where the truth is `34` | HIGH | **FIXED, and my correction was wrong first too.** I measured 27, then wrote five more call sites in my own `AT-010` arms, then published the pre-measurement figure — into `docs/ARCHITECTURE.md`, which this repo treats as an oracle. The reviewer derived 32; after the H2 fix it is **34**. The counts are now **pinned in the suite** and the map row narrates none. **The pin went red within a minute of being written**, at 32, because H2 added two sites — the argument for pinning rather than narrating, made by the pin itself |
| **M1** the flaky focus test is not fixed, only less flaky | MED | **FIXED — and the cause was not tolerance.** Under load `app.focused` is still `None` after **five seconds**: `MapScreen` sometimes never focuses anything, so no timeout could fix it. The arm now asserts the **derivation** against an independent recomputation at each step, which holds whether or not anything has focus. Stable across 6 sequential and 5 parallel runs |
| **M2** the acceptance passes because focus is **lost**, not moved | MED | **FIXED, and it exposed a shipped defect.** Measured deterministically over three runs: the real `tab` key yields `['rail','','','','','','']` — focus dropped, never traversed. `LLR-CNV.3.1`'s recorded pre-state `M-10` **does not reproduce**, and `len(set(seen)) > 1` was satisfied by the loss. The loose assertion is gone; the requirement's real threshold is pinned as a **strict xfail** so it fails loudly the day traversal is fixed. Carried as **`B-51`**, routed to `qa-reviewer` |
| **M3** threshold 3 blind to `**` splat, positional args, untracked files | MED | **FIXED** — a splat is banned as unauditable, `len(args) > 2` is an offender, and a new arm fails if any product source is invisible to `git ls-files`. `AsyncFunctionDef` added to the definition walk |
| **M4** `>= 20`, a floor in the requirement that abolished floors | MED | **FIXED** — `== 25` |
| **M5** the frozen arm can pass for the wrong reason | MED | **FIXED** — construction moved outside the `raises` block, exception narrowed to `FrozenInstanceError`; the battery confirms it now reddens instead of absorbing a required-field mutation |
| **M6** `"canvas"` is an unreachable branch | MED | **DECLARED** — `#map-canvas` is `can_focus=False`, so the focused tone is reached via `""`. Kept (correct once the canvas is focusable) and recorded in the source |
| **L1** definitions derive 7, not 6 | LOW | **FIXED** — 7 is correct and pinned, with its reason: `IRenderer.render` lives under `mapper/views/` and must satisfy the shape it declares |
| **L2** fake CSS selectors compared as strings | LOW | **FIXED** — bare ids; the old form silently compared `"#None"` for unnamed widgets |
| **L3** `FOCUS_OWNERS` duplicated by `_FOCUS_REGIONS` | LOW | **FIXED** — a new arm fails if the two rosters drift |
| **L4** a modal makes the canvas paint the focused tone | LOW | **CARRIED** as `B-52`; the canvas is occluded, so no visible harm today |

### Battery rounds 9 and 10

Round 9: **132 arms green first, 6 of 8 RED**, sha256 restore on 9 files, `132/132` after.

The two GREEN were **mis-shaped mutations of mine, for the third time in this batch**: I tried to
test the pinned counts by *loosening* them to a floor. A weaker assertion cannot fail — that is a
tautology, not a mutation. Round 10 asks what a pin actually answers, *does a drift redden it*:

| Mutant | Verdict |
|---|---|
| one arg-ful call site **added** | **RED** |
| one renderer definition **removed** | **RED** |

**The recurring lesson, now three times over:** when a mutant comes back inert, the first hypothesis
should be that the mutation was shaped to succeed — not that the guard is weak.

**Final state:** fast `716 passed, 17 deselected, 1 xfailed`; slow `17 passed`; ruff **27** (baseline
28; the −1 is the pre-existing `pytest` import the new xfail consumes; **zero new**).
*(Superseded by §10: the xfail is gone, so ruff is back at exactly 28.)*

---

## 10 · Confirmation pass — 3 HIGH discharged, 1 new HIGH, and a RETRACTION

The confirmation pass discharged all three original HIGH — each mutation-verified against the exact
state it forbids — and blocked on **one new HIGH my own M2 fix introduced**.

| Finding | Disposition |
|---|---|
| **N-H1** the strict xfail cannot fire on the event it names | **FIXED — by retracting the premise.** See below |
| **N-M2** `B-51`'s recorded mechanism is falsified by the test citing it | **RETRACTED with it** |
| **N-M3** §6 claimed `B-50` "covered"; the suite was green with it reverted | **FIXED** — a new arm captures the state the shipped `e` key hands the renderer and asserts `diff`, `query` and `focus_owner`. Reverting the fix reddens it |
| **N-M1** the map guard pinned one phrasing; `"NOT PRESENT"` walked through | **FIXED** — matches the concept, and the backstop no longer accepts the `PRESENT` inside `NOT PRESENT` |
| **N-M4** `_expected_owner` is a transcription, not an independent oracle | **FIXED + DECLARED** — claim downgraded in the docstring, and a new arm focuses `#insp-title` so the parent walk is executed. It now catches "stops walking parents", which the reviewer had measured GREEN |
| **N-M5** the export arm called `action_export_svg()` directly | **FIXED** — `pilot.press("e")`, the binding `keymap.py` declares |
| **N-M6** `*` splat and untracked test files escaped threshold 3 | **FIXED** — both closed |
| **N-L1** `ruff check fixtures/` inspects nothing | **CONCEDED**; kept only as a tree-cleanliness signal, labelled |
| **N-L2 / N-L3** | accepted as recorded |

### The retraction — `A-96`

**`B-51` is not a defect. `A-94` was wrong, and so was the carry it created.** The confirmation pass
correctly showed my xfail could never fire; chasing *why* showed the premise under it was false.

```
size        focus_chain                                          owners after 4 real tabs
80 x 24     []                                                   ['rail', '', '', '', '']
118 x 34    ['map-rail','insp-title','insp-state','insp-notes']   ['rail','rail','inspector', ...]
140 x 45    ['map-rail','insp-title','insp-state','insp-notes']   ['rail','rail','inspector', ...]
```

At **118 × 34, the batch's declared context of use**, press 1 gives `rail` and press 2 gives
`inspector` — **`M-10` verbatim**. The empty chain at 80 × 24 is `_apply_region_visibility`
**working**: it auto-hides the rail and the inspector below `MIN_CANVAS_WIDTH`, so nothing focusable
remains. There was nothing to traverse because nothing was displayed.

**Three passes compounded this rather than catching it,** which is the part worth recording. The
original acceptance passed at the default size for the wrong reason; the gate review correctly
showed the assertion was vacuous and I concluded the *behaviour* was broken; the confirmation pass
correctly identified `focus_chain == []` — **also measured only at the default size** — and I wrote
it down as a root cause. **Nobody varied the one parameter that decided the answer.** Three
independent passes agreeing is not evidence when they share an unstated premise.

**This is `P-20` inverted, inside the batch that recorded `P-20`.** There the suite ran only at sizes
where a real defect was absent; here at a size that manufactured one. Carried as **`B-54`**: a
Pilot-driven interaction assertion must declare its terminal size, because two of this app's three
regions are size-conditional.

`LLR-CNV.3.1`'s threshold is now asserted directly, at the declared size, and **passes**.

### Battery round 11 — the corrected arms are falsifiable

A passing acceptance is only evidence if something can make it fail. 55 arms green first; **6 of 6
RED**; sha256 restore on 6 files; `55/55` after.

| Mutant | Verdict | Arms |
|---|---|---:|
| `_focus_owner` returns a constant | **RED** | 2 |
| `_focus_owner` stops walking parents | **RED** | 2 |
| both size probes forced to the same size | **RED** | 1 |
| the export drops the active `diff` again | **RED** | 1 |
| the map row regresses under the shorter phrasing | **RED** | 1 |
| a `*` splat call site appears | **RED** | 1 |

**Final state:** fast `719 passed, 17 deselected`; slow `17 passed`; ruff **28** — exactly the
`4eaba35` baseline, **zero new**; `fixtures/` clean. Ledger `736 = 711 + 25`, **0 removed**, every
added node id enumerated against a detached worktree at `4eaba35`.

---

## 11 · Retraction check — **RETRACTION CORRECT**, gate PASSES, and a fourth instance found

A third, narrow pass verified the retraction independently rather than replaying my measurements.
Verdict at `increment-002-retraction-check.md`: **RETRACTION CORRECT · no HIGH · gate PASSES.**

**It settled the causal question with three mutants I had not run**, which is what turns the
retraction from an argument into evidence:

| Mutant | Arm | Verdict | Reading |
|---|---|---|---|
| the auto-hide disabled | the size arm | **RED** | the empty 80 × 24 chain is *caused* by the auto-hide |
| the auto-hide disabled | the 118 × 34 traversal arm | **GREEN** | the traversal is **not** an artifact of hiding — it survives its removal |
| `MIN_CANVAS_WIDTH` 58 → 90 | the traversal arm | **RED** | region visibility is the whole variable |

It also found the anchor is stronger than I claimed: `01-requirements.md:160` **already recorded**,
before this increment, that `_apply_region_visibility` hides the rail below ~118 columns and that the
suite was therefore blind to it. The retraction rediscovered the batch's own written finding — which
is corroboration, and also the sharpest available statement of how three passes missed it.

### The fourth instance, and it is inside the amendment written to name the class

**`F1`/`F2` — my retraction's own headline table published a race-dependent pre-state.**
`on_mount` schedules `call_after_refresh(self._park_focus)` (focus → `None`) while `AUTO_FOCUS` has
already focused `#map-rail`. Sampled one `pilot.pause()` in, the screen is usually still in the
`AUTO_FOCUS` state — **23 runs in 25** — so the table published `owners[0] = 'rail'`, which reads as
though the first `tab` did nothing. Settled, it is `''` **25 of 25**.

The arm passed because `_park_focus` won an undeclared race. Fixed: it settles twice, asserts
`app.focused is None`, and asserts the `''` pre-state — so the published measurement and the
asserted one are now the same state. Corrected in `A-96`, in §10 and in the docstring.

| Finding | Disposition |
|---|---|
| **F1** the table publishes an unsettled pre-state | **FIXED** in all three places |
| **F2** the arm never asserted its own pre-state | **FIXED** — two settles plus an explicit assertion |
| **F3** *"from the canvas"* silently modelled as *"nothing focused"* | **DECLARED** in the assertion message; `#map-canvas` is `can_focus=False` (`B-53`), so this is the reachable equivalent |
| **F4** the `B-50` arm called the action directly | **FIXED** — `pilot.press("e")`, matching its sibling |
| **F5** three new arms ran at the default 80 × 24 | **FIXED** — `size=(118, 34)`. My own `B-54`, violated by my own arms, the day I raised it |
| **F6** §9's `H2` mechanism was a transient | **FIXED** — the real route is `tab` (or `g`) then `e`, which is a **stronger** justification: the defect was reachable by a plain operator sequence, not only in a mount window |

**Also corrected in the record:** the "five widgets report `can_focus=True`" figure carried from the
confirmation pass is really **four focusable plus one deliberately dormant** — `search-input` is
`display=False, disabled=True` until `/` summons it, verified reachable and correct. **Nothing of
`B-51` remains carried.**

**Final state:** fast `719 passed, 17 deselected`; slow `17 passed`; ruff **28** — exactly the
`4eaba35` baseline, zero new. Focus arms stable across 5-way parallel load after the timing change.

---

## Increment gate checklist

| # | Item | ✓ | Evidence |
|---|---|---|---|
| 1 | ≤4 source files, or reason declared | ⚠ | 6 — the breach `#D5` declared; reason in §2 |
| 2 | Tests written in this same increment | ✓ | +18 nodes, 11 test files |
| 3 | Layer 0 written where the criterion applies | ✓ | `_focus_owner` branches and crosses a declared boundary — `test_llr_cnv_3_1_*` |
| 4 | RED counterfactual captured and restored by hash | ✓ | battery round 7 — §8 |
| 5 | Reverse census run on every touched symbol | ✓ | the AST census IS the reverse census for `.render` |
| 6 | `code-reviewer` passed — a HIGH blocks | ✓ | BLOCK on 3 HIGH → fixed → confirmation pass discharged all three and raised 1 new HIGH → fixed by **retracting a false premise** → narrow third pass: **RETRACTION CORRECT, no HIGH, gate PASSES**. No HIGH was ever self-cleared |
| 7 | No file from another lane touched | ✓ | serial batch |
| 8 | Frozen interfaces untouched, or authorised | ✓ | this IS the pre-authorised A3; map row promoted to `PRESENT` |
| 9 | Coverage claims verified on disk | ✓ | per-node output pasted, counts from the runs' own output |
| 10 | Load-bearing emptiness declared | ✓ | §5.2 — the zero-coverage `query` surface is why byte-identity is safe here |
| 11 | Mutation verdicts per arm, inert arms named | ✓ | §8 |
