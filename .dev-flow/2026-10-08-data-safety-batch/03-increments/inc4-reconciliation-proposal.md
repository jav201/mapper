# Inc-4 reconciliation proposal — AT-044, AT-042's two arms, and the reconciliation

> **Status:** PROPOSAL — the orchestrator applies the reconciliation from this file.
> Nothing in this file edits `mapper/`; the two test nodes are committed by this increment,
> and the traceability edits below are applied by the orchestrator.

## 1. On-disk node mapping (one row per reconciled id)

| id | on-disk node id (grep-verified) |
|---|---|
| AT-025b | `tests/test_repair_cycles.py::test_llr_n13_1_5_a_broken_map_is_distinguishable_from_a_healthy_EMPTY_one` (plus the four siblings `test_llr_n13_1_5_…` at `:543`, `:575`, `:624`, `:664`) |
| AT-041 | `tests/test_repair_layout.py::test_at_r12_pressing_help_presents_every_map_binding` (`def` at `tests/test_repair_layout.py:276`) |
| AT-042 (largest-set arm) | `tests/test_repair_layout.py::test_tc_r25_the_presented_set_equals_the_keymap_set_in_both_directions` (`def` at `:451`, parametrised `map`/`home`) |
| AT-033 | `RETIRED — travels with US-N14 (#D23)` |
| AT-034 | `RETIRED — travels with US-N14 (#D23)` |
| AT-035 | `RETIRED — travels with US-N14 (#D23)` |

**AT-042's two owed arms (LLR-008.3) — new nodes minted by this increment, not reconciliations:**

| arm | on-disk node id |
|---|---|
| smallest set (`SCOPE_APP`, 2 rows) | `tests/test_repair_layout.py::test_tc_r25_the_presented_set_equals_the_keymap_set_in_both_directions[app]` |
| no-scope screen | `tests/test_repair_layout.py::test_tc_r25b_a_screen_declaring_no_scope_presents_the_app_set` |

**AT-044 — new node minted by this increment:**

| id | on-disk node id |
|---|---|
| AT-044 | `tests/test_double_question_mark.py::test_at_044_a_doubled_question_mark_opens_one_legend` |

Line-number note: the prior citations `tests/test_repair_layout.py:274` (AT-041) and `:441` (AT-042
largest set) were the pre-edit lines; the `def` lines above are grep-verified on this branch's file
after the increment's edits. The NODE NAMES are the load-bearing identifiers.

---

## 2. Proposed text to apply

### (a) Ledger entry — append to `01-requirements-ledger.md` (next number: `.64`)

```markdown
### LED-2026-10-08-data-safety-batch.64 — Inc-4 — AT-044 and AT-042's two arms realised on disk
- **Requirement:** HLR-007, HLR-008, LLR-007.1, LLR-007.2, LLR-008.1, LLR-008.2, LLR-008.3
- **Date:** 2026-10-08
- **What changed:** AT-044 is realised as `tests/test_double_question_mark.py::test_at_044_a_doubled_question_mark_opens_one_legend`; AT-042's smallest-set arm is realised as `tests/test_repair_layout.py::test_tc_r25_...[app]` and its no-scope arm as `test_tc_r25b_a_screen_declaring_no_scope_presents_the_app_set`. AT-041 and AT-042's largest-set arm reconcile to `test_at_r12_pressing_help_presents_every_map_binding` and `test_tc_r25_the_presented_set_equals_the_keymap_set_in_both_directions` respectively; AT-025b reconciles to the five `LLR-N13.1.5` nodes; AT-033/034/035 are retired and travel with US-N14 (`#D23`).
- **Why:** C-18 — every declared acceptance id now resolves to a named on-disk node or a retirement, so a future refactor that deletes a node reddens the traceability record. The two new AT-042 arms were absent nodes (the design's `LLR-008.3`), and AT-044 had no node of its own.
- **Evidence:** grep-verified `def` lines — `tests/test_repair_cycles.py:501,543,575,624,664`, `tests/test_repair_layout.py:276` (`test_at_r12…`), `tests/test_repair_layout.py:451` (`test_tc_r25`), `tests/test_repair_layout.py:468` (`test_tc_r25b`); the increment's RED battery (see `03-increments/inc4-reconciliation-proposal.md` §3).
```

### (a2) Ledger note — the AT-044 mutation the design names is INERT (found at Inc-4 RED)

```markdown
### LED-2026-10-08-data-safety-batch.65 — Inc-4 RED — AT-044's discriminating mutation is `priority=True`, not the design's two
- **Requirement:** LLR-007.1, HLR-007
- **Date:** 2026-10-08
- **What changed:** LLR-007.1's negative control and §3.1's AT-044 "RED today" cell now name the mutation that actually opens a second legend — making the app-scope `question_mark → help` binding `priority=True` — instead of "bind `?` in the help seat" / "drop `SCOPE_HELP` from `MODAL_SCOPES`".
- **Why:** executed at Inc-4: both design-named mutations leave the node GREEN, because `HelpScreen` defines no `action_help` (the binding dispatches to a missing method and returns False) and the modal binding chain (`_modal_binding_chain`) cuts the app off. A `priority=True` app chord is checked from the App down (`_check_bindings(priority=True)` uses `_binding_chain`, not `_modal_binding_chain`), so it reaches `MapperApp.action_help` and stacks a second legend. This is the existing defect class `test_no_screen_binds_the_question_mark_at_priority` guards (the `?` row is deliberately non-priority, `mapper/keymap.py:268-271`).
- **Evidence:** `03-increments/inc4-reconciliation-proposal.md` §3 — mutation battery, hash-restored.
```

> If the orchestrator prefers one entry, fold `.65` into `.64`; the split keeps "what was realised"
> separate from "what the mutation is". Both are append-only and never rewrite earlier entries.

### (b) BACKLOG rows B-100 / B-101 — mark DONE

Proposed replacement rows (the DONE convention is the `~~id~~` strike + `**DONE**` + batch + summary,
as used by `~~B-72~~`):

```markdown
| ~~B-100~~ **DONE** `2026-10-08-data-safety-batch` — AT-044 realised as `tests/test_double_question_mark.py::test_at_044_a_doubled_question_mark_opens_one_legend`; AT-025b reconciled to the five `LLR-N13.1.5` nodes in `tests/test_repair_cycles.py:501…664` | `HLR-N16.3`'s `AT-044` (a doubled `?` does not stack a second legend) was never realised as a node; `HLR-N13.3` was already covered under `LLR-N13.1.5` | `2026-10-08-data-safety-batch` US-002 |
| ~~B-101~~ **DONE** `2026-10-08-data-safety-batch` — AT-041 → `test_at_r12_pressing_help_presents_every_map_binding`; AT-042 largest-set → `test_tc_r25_…`, smallest-set → `test_tc_r25_…[app]`, no-scope → `test_tc_r25b_a_screen_declaring_no_scope_presents_the_app_set` (all `tests/test_repair_layout.py`); AT-033/034/035 RETIRED, travel with US-N14 (`#D23`) | Acceptance ids with no on-disk node by id (validator `V2` at close, 2026-10-08); AT-033/034/035 belong to the DEFERRED US-N14 | `2026-10-08-data-safety-batch` US-003 |
```

### (c) §3.1 row changes in `01-requirements.md`

Two rows change. (The same AT-044 mutation wording also appears in HLR-007's negative control and
LLR-007.1's negative control; those two are flagged below but only the §3.1 row is given verbatim here.)

**AT-044 row** — replace the current "RED today" cell (the tail: "…the mutation it must redden on is
binding `?` in the help seat (or letting the legend inherit the app chord), which opens a second legend") with:

> yes — only as an absent node today; the mutation it reddens on is making the app-scope `?` binding `priority=True`, which makes the app chord reachable from the modal legend and opens a second legend. (The design's two named mutations — "bind `?` in the help seat" and "drop `SCOPE_HELP` from `MODAL_SCOPES`" — are INERT, executed at Inc-4: `HelpScreen` defines no `action_help` and the modal binding chain cuts the app off.)

**AT-042 row** — replace the "assertion" cell ("the largest-set arm resolves to `test_tc_r25`; the two
missing arms are new nodes") and the "RED today" cell ("none for the reconciliation; the two new arms
go RED as absent nodes today") with:

> assertion: the largest-set arm resolves to `test_tc_r25_the_presented_set_equals_the_keymap_set_in_both_directions`; the smallest-set arm is `test_tc_r25_…[app]` and the no-scope arm is `test_tc_r25b_a_screen_declaring_no_scope_presents_the_app_set`.
>
> RED today: none for the reconciliation (no executed arm); the two new arms were absent nodes — each is killed by a mutation aimed at `HelpScreen` (PDR condition C14): the no-scope arm by changing the `HelpScreen` default `scope=SCOPE_APP` (`mapper/screens/help.py:288`), the `[app]` arm by forcing `self.scope` to a non-app constant in `HelpScreen.__init__`.

---

## 3. RED evidence (mutation battery, copy-and-restore)

Every mutation is a transient one-site edit of a `mapper/` file, hash-restored byte-identical. The
commands below ran from the worktree root with `python -B -m pytest -q -p no:cacheprovider`.

### 3.1 AT-044 — `test_at_044_a_doubled_question_mark_opens_one_legend`

Baseline (GREEN): `1 passed`.

**Mutation 1 — "bind `?` in the help seat"** (design-named). Added
`KeyBinding("question_mark", "?", "help", "legend", "help")` to the `help` group of
`mapper/keymap.py`. Result: **GREEN — INERT** (`1 passed`). The binding dispatches to `action_help`,
which `HelpScreen` does not define.

**Mutation 2 — "drop `SCOPE_HELP` from `MODAL_SCOPES`"** (design-named). Changed
`MODAL_SCOPES = (SCOPE_PALETTE, SCOPE_HELP, SCOPE_DRAFT)` to `(SCOPE_PALETTE, SCOPE_DRAFT)`.
Result: **GREEN — INERT** (`1 passed`). The legend inherits the app `?` chord but again dispatches to a
missing `action_help`.

**Mutation 3 — the discriminating mutation (RED).** Changed the app-scope row
`KeyBinding("question_mark", "?", "help", "legend", "app")` to `priority=True`. Result: **RED**:

```
>       assert app.screen is legend, "the second ? closed or replaced the legend"
E       AssertionError: the second ? closed or replaced the legend
E       assert HelpScreen(classes='-docked') is HelpScreen(classes='-docked')
FAILED tests/test_double_question_mark.py::test_at_044_a_doubled_question_mark_opens_one_legend
1 failed in 0.88s
```

A priority app chord is checked App-down, so it reaches `MapperApp.action_help` and stacks a second
legend. sha256 of `mapper/keymap.py` before and after restore:
`8555441e0f14be59a2866f7c4e14ce987aa3c5e4243cf4b6e289dd5be0df7e23` (identical).

### 3.2 AT-042 no-scope arm — `test_tc_r25b_a_screen_declaring_no_scope_presents_the_app_set`

Baseline (GREEN): `1 passed` (`-k tc_r25b`).

**Mutation — change the `HelpScreen` default `scope=SCOPE_APP` → `SCOPE_HELP`** (`mapper/screens/help.py:288`).
The design names `SCOPE_MAP`, but `SCOPE_MAP` is not imported in `help.py` (a literal `SCOPE_MAP` there
raised `NameError` at import; recorded). `SCOPE_HELP` is the already-imported modal-scope constant and
carries the same discriminating property: the no-scope default is no longer `SCOPE_APP`. Result: **RED**:

```
>       assert _rendered_pairs(screen=HelpScreen()) == expected
E       AssertionError: assert {('end', 'to ...'close'), ...} == {('?', 'legen...', 'palette')}
E         Extra items in the left set: ('end', 'to bottom'), ('pageup', 'page up'), ('↓', 'scroll down'), ('pagedown', 'page down'), ('q', 'close')...
FAILED tests/test_repair_layout.py::test_tc_r25b_a_screen_declaring_no_scope_presents_the_app_set
1 failed, 19 deselected in 0.25s
```

sha256 of `mapper/screens/help.py` before and after restore:
`17011f2faa38ec2435cc2924dcc97ad24d708b299b5f21ca6859bbf1e8ed093a` (identical).

### 3.3 AT-042 smallest-set arm — `test_tc_r25_the_presented_set_equals_the_keymap_set_in_both_directions[app]`

Baseline (GREEN): `1 passed` (`-k tc_r25`, 4 selected).

**Mutation — force `self.scope` to a non-app constant** (`mapper/screens/help.py`, `HelpScreen.__init__`:
`self.scope = scope` → `self.scope = SCOPE_HELP`), so the panel presents a fixed set regardless of the
scope argument. Result: **RED**:

```
>       assert _rendered_pairs(scope) == expected
E       AssertionError: assert {('end', 'to ...'close'), ...} == {('?', 'legen...', 'palette')}
E         Extra items in the left set: ('pagedown', 'page down'), ('esc', 'close'), ('home', 'to top'), ('end', 'to bottom'), ('↓', 'scroll down')...
FAILED tests/test_repair_layout.py::test_tc_r25_the_presented_set_equals_the_keymap_set_in_both_directions[app]
1 failed in 0.24s
```

(An alternative one-site edit — `_render_keymap`'s `entries = bindings_for(self.scope)` →
`bindings_for(SCOPE_HELP)` — also reddens, but via `KeyError: 'help'`, because the entries and the
`bar_group_order(self.scope)` grouping then disagree. The `self.scope` forcing is the clean form of the
same "presented set ignores the argument" defect, so it is the recorded RED.)

sha256 of `mapper/screens/help.py` before and after restore:
`17011f2faa38ec2435cc2924dcc97ad24d708b299b5f21ca6859bbf1e8ed093a` (identical).

`git status` after the battery: only `M tests/test_repair_layout.py` and `?? tests/test_double_question_mark.py`
— `mapper/` has no diff.

---

## 4. Test counts (green, restored tree)

| file | result |
|---|---|
| `tests/test_double_question_mark.py` | `1 passed` |
| `tests/test_repair_layout.py` | `20 passed` (was 18; +1 `test_tc_r25[app]` arm, +1 `test_tc_r25b`) |
| `tests/test_help_scope.py` | `50 passed` |

`tests/test_repair_layout.py -k tc_r25`: `4 passed` (`[map]`, `[home]`, `[app]`, `test_tc_r25b`).
