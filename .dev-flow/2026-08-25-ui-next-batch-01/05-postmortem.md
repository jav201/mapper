# 05 — Post-mortem · `2026-08-25-ui-next-batch-01` · variant A «taller», P1

## BLUF

**The batch shipped all five P1 stories, grew the suite from 88 to 210, and found seven defects that
already existed on `main` and that the previous suite structurally could not see.** Every one of
them lived in the gap between *"the action ran"* and *"the key the operator presses reaches the
action"* — which is exactly the gap a static SVG prototype cannot show and a test that calls
`action_*` directly cannot cross.

**The most important result is not a feature. It is that two independent reviews each broke a
control while my suite stayed green**, and in both cases my own counterfactual had already run and
had convinced me the control was gated.

---

## 1 · What worked

**Driving the real key instead of the action.** This one discipline (control C-16, forced by premise
P-10 coming back FALSE) found four separate pre-existing bugs. `ctrl+p` never opened mapper's
palette at all — `MapperApp` set `COMMAND_PALETTE_ENABLE`, a name Textual never reads — and the
superseded test could not see it because it called `action_palette()` directly.

**Executing premises instead of trusting the brief.** Thirteen premises were run against disk at
Phase 0. Eleven held. P-10 (the prototype verifies interactions) came back FALSE and reshaped every
acceptance test in the batch. P-9 (the module map is current) came back FALSE — 10 of 30 tracked
files fell under no declared module — and ARQ fired on its own.

**Parallel review lenses with genuinely different instruments.** The architect worked from the
module map, QA from the oracle design, security by *executing attacks*, UX by *measuring painted
cells*. They did not overlap and each found something the others did not. The security lens did not
argue that path traversal was possible; it launched `calc.exe` and `powershell.exe`.

**The per-arm counterfactual verdict.** Recording which arms redden, not just a pass/fail, is what
made M2 legible: clamping the state setter so it ignores its argument reddens 3 of 4 arms and leaves
the default-valued one green. That is C-10 measured rather than asserted.

**Hash-verified restores.** Twice a green suite hid a broken tree state and only the hash caught it.

---

## 2 · What did not work

### 2.1 · My counterfactuals tested deletion, not weakening — the batch's main lesson

I deleted the workspace confinement check, saw three tests redden, and recorded the control as
gated. The security sign-off then found **two substitutions that left the suite 24/24 green**:

- `if ".." in target` — satisfied every negative case in the file, because all of them were
  `..`-relative traversals. Absolute paths to `calc.exe` and `powershell.exe` launch again.
- `str(resolved).startswith(str(root))` — nothing in the suite distinguished a real ancestor from a
  shared string prefix, so `<root>-exfil` passes as inside `<root>`.

**The generalisation, and it is the one worth carrying:** *deleting* a control is the mutation that
is easiest to write and the least likely to happen. The realistic regression is the next editor
**changing the expression** — a "simplification", a "faster check", a refactor. A counterfactual
that only deletes measures the wrong failure mode.

**Proposed control (portable, for the catalog):** when a predicate implements a *policy* rather than
a computation — containment, an allowlist, an authorisation — the counterfactual set must include at
least one **plausible wrong implementation**, not only the empty one. The test for whether the set
is adequate: can you write a version of this check that a competent engineer might plausibly commit,
which the suite accepts?

### 2.2 · My reverse census was incomplete, and the suite caught what the census did not

For the removal of `LayeredRenderer`'s ficha strip I grepped two of its distinctive strings,
concluded nothing asserted it, and recorded that as premise P-12. A third string — `"cobertura"` —
was asserted by `tests/test_legacy_fixture.py:27`, which broke at the increment. The census was
keyed on strings I chose by eye rather than derived from the deleted code.

### 2.3 · A flaky gate nearly shipped

`AT-N04a` passed **1 run in 3**. The focus request and the inspector rebuild were two scheduled
callbacks racing on frame timing. It was found only because I re-ran the file after an unrelated
fix. It also silently corrupted an earlier measurement: counterfactual M7 appeared to redden
`AT-N04a` as well as its target, and I recorded that as "over-reporting" when the real cause was
almost certainly the flake. **A flaky test does not merely fail sometimes — it poisons every
counterfactual that touches it.** Fixed by ordering the focus request causally (the inspector
applies a pending request at the end of the rebuild that creates the rows) rather than by adding
another pause.

### 2.4 · I wrote a literal NUL byte into source. Twice.

While implementing the fix for a NUL-byte crash, the escape sequence in my explanatory comment
collapsed into an actual NUL — first in `mapper/osopen.py`, the module defending against exactly
that, then again in the test. Both were caught only because Python refused to parse the file.

**This is C-56's family** (an evidence artifact carrying the payload it describes) extended to
source comments: *writing about a control character keeps producing the control character.* The
discharge is the same shape as C-56's — describe it, or construct it programmatically (`chr(0)`),
never spell the escape into a file.

### 2.5 · The file budget was exceeded three times

Increments 2, 3 and 4 touched 6, 5 and 5 source files against a cap of 4. Each was declared with a
reason in §2 of its packet and marked ✗ on its checklist rather than waved through. The honest
reading: **the cut was made before the PDR conditions landed**, and those conditions added
single-purpose files (the coercion helper, the `HintLine` setter, the `DsChip` fix) that could not
sensibly be split into increments of their own. The C-21 re-cut was performed for the AT set but
**not** re-performed after Amendment 2 added HLR-N06. That is the process gap.

### 2.6 · A counterfactual that never ran was nearly filed as evidence

The first attempt at mutation M4 inserted unreachable code, broke the parse, and produced **no test
output at all**; the grep silently matched nothing. Only noticing the empty output prevented a
mutation that never executed being recorded as proof that the gate holds. This is the corpus's
"a mutation that never applied reads as a survivor" trap, in its inverse form.

---

## 3 · Defects found that pre-dated the batch

| # | Defect | Found by |
|---|---|---|
| 1 | `ctrl+p` never opened mapper's palette; Textual's built-in owned the chord | an AT pressing the real key |
| 2 | 0 of 33 palette entries could dispatch | the story itself |
| 3 | `q` quit the app from two screens, discarding an unsaved import | code review |
| 4 | `escape` while typing popped the map and discarded the text | UX lens |
| 5 | `m cobertura` was cut off the keybar entirely (216 cells rendered at 118) | UX lens |
| 6 | `x` destroyed a non-root subtree unconfirmed; undo died on leaving the map | the story |
| 7 | path traversal launched files outside the workspace | security lens, executed |

Plus two found in code the batch itself wrote, by review rather than by me: `MapperApp.BINDINGS`
escaping the seat, and `HelpScreen` binding a method it does not define.

---

## 4 · Metrics

| Metric | Value |
|---|---|
| Stories delivered | 5 of 5 P1, plus HLR-N06 adopted mid-batch |
| Tests | 88 → 210 (+123, −6 superseded) |
| Increments | 6, cut as 5 commits |
| Source files over budget | 3 increments (6, 5, 5 vs cap 4), each declared |
| Counterfactuals executed | 12, all restores hash-verified |
| Counterfactuals that were themselves defective | 2 (one never ran; one poisoned by a flaky test) |
| Review lenses | 5 (architect, qa, security ×2, ux, code-review) |
| Blocking findings from review | 5 HIGH (code review) + 2 blockers (security sign-off) |
| Mutations found by reviewers that left my suite green | **3** |
| Requirement amendments | 3, all recorded Before → After |
| Frozen-interface changes | 0 |

---

## 5 · Decisions taken autonomously

Per the kickoff authorisation, these were decided rather than asked, and are recorded here, in
`PLAN.md` §9 and in `state.json`:

| # | Decision | Why |
|---|---|---|
| D1 | Mode `full` | The operator asked for the full V-model and granted merge authority. |
| D3 | No fork into parallel lanes | `mapper/app.py` is in 5 of 6 increments; file sets are not disjoint. |
| D4 | Delete `LayeredRenderer`'s ficha strip rather than suppress it | Suppressing it needed a new `render` kwarg — a frozen-interface change, out of scope. |
| D5 | Adopt **HLR-N06** (focus model) into this batch | The taller skeleton has three interactive regions and no requirement said which one is live. Specification of the story, not new scope. |
| D6 | Discharge U-M2 minimally — two toggles and a width threshold | Not batch 2's pan/fold work. |
| D7 | Drop the global "one ACCENT run" invariant (Amendment 3) | Unreachable without passing focus into a frozen renderer; asserting it would false-fail correct code. |
| D8 | Carry, not fix: `MapStore.load` KeyError, the `screens → app` back-edge, ~20 legacy escape sites | Outside the stories' budget; fixing the back-edge silently was explicitly rejected. |
| D9 | Cut increments 5 and 6 together | 3 source files combined; splitting meant two increments editing the same file for related reasons. |

---

## 6 · Items proposed for the next batch

1. **Batch 2 (variant B «atlas») as planned** — canvas pan, fold/expand pills, minimap + viewport,
   braille edges, search hit count. It should also close the canvas's focus-unaware selection tone
   (Amendment 3's carry), since it is reworking that renderer anyway.
2. **A plausible-wrong-implementation counterfactual for every policy predicate** (§2.1). This is the
   batch's main lesson and it is portable — it belongs upstream in the flow, not only here.
3. **Derive census input sets from the deleted code**, not from strings chosen by eye (§2.2).
4. **`MapStore.load` raises `KeyError` on a malformed sidecar** — a node missing `path:` denies the
   whole map. Security finding F-M5, carried.
5. **`mapper/screens/factory.py:343` imports from `mapper.app`** — the one live dependency-ban
   violation. ARQ finding A-7, carried; fixing it silently was rejected.
6. **~20 legacy `rich.markup.escape` sites** in `app.py`'s other renderers emit visible backslashes.
7. **Four unmigrated modal screens** (`FactoryScreen`, `EditorScreen`, `SettingsScreen`,
   `CoverageScreen`) still hold local `BINDINGS`; `keymap.UNMIGRATED_SCREENS` names them and two
   tests fence them.
8. **Re-run the C-21 increment re-cut after every amendment**, not only after the first (§2.5).
9. **Security minors** carried from the sign-off: ADS targets, `urlparse` vs `urlsplit`, an
   executable-extension policy, U+202E passing `plain()`.

---

## 7 · Working-file reconciliation (C-44)

| File / area | State |
|---|---|
| All `mapper/**` and `tests/**` changes | ✅ committed across 7 commits on `feat/ui-next-batch-01` |
| `docs/ARCHITECTURE.md` | ✅ committed (ARQ amendment + the S-M6 allowlist narrowing) |
| `.dev-flow/2026-08-25-ui-next-batch-01/**` | ✅ committed |
| `prototypes/ui_next/` | 📋 **left untracked ON PURPOSE** — a parallel prototyping round owns it; never staged by this batch, verified at every commit |
| Counterfactual mutations (12) | 🗑️ all reverted, each restore confirmed by sha256 |
| Scratch probes | 🗑️ written to the system temp directory, never to the repo |

`git status --short` at close shows only `?? prototypes/ui_next/`, which is the pre-existing state
this batch found and deliberately did not touch.
