# PLAN — `2026-08-26-repair-batch` (PR A) · four shipped defects

> **Living compendium.** Updated at every gate. Artifact language **English**; UI strings **Spanish**.

---

## 1 · BLUF

**This batch exists because the feature batch's PDR gate found that the ground was not solid.** Four
defects already on `master` were reproduced with executed transcripts, two of them fatal to the
application. The operator chose to repair them as a small, separately-reviewable PR before any feature
work lands on top.

The argument for splitting was that **a smaller diff is a sharper gate** — batch 1's precedent is that
the PR-level gate is where the serious things get caught. That argument only holds if this PR stays
small, so the scope is fenced hard: **no frozen interface moves in this batch.**

---

## 2 · Objective

| Field | Value |
|---|---|
| Batch id | `2026-08-26-repair-batch` |
| Branch | `fix/shipped-defects-repair` |
| Base | `origin/master` = `d6b60e6` |
| Baseline suite | **245 passed, exit 0** (`pytest -q -p no:randomly`, one complete run) |
| Mode | `full` — operator asked for batch 1's gate protocol explicitly |
| Successor | `2026-08-26-ui-next-batch-02`, **parked** at its PDR gate with all artifacts retained |

### The four defects

| id | Defect | Story |
|---|---|---|
| S-01a | a cycle in a `.mmd` is accepted, then `RecursionError` kills the app | US-R01 |
| S-01b | a depth-500 acyclic chain `RecursionError`s in 0.01 s | US-R02 |
| S-02 | a non-string ficha field loads clean, breaks every consumer, and **`coverage()` counts it as documented** | US-R03 |
| S-07 | canvas and inspector laid out off-screen whenever the rail is visible | US-R04 |
| S-08 | `?` paints **16 of 27** bindings, dropping the whole `view` group | US-R05 |

---

## 3 · Scope fence

**IN:** exactly the five stories above.

**OUT, and deliberately so:** `IRenderer.render` and `Canvas` are **not** touched — they stay
byte-for-byte as they are on `master`. The `ViewState` migration, the `dots`/`bgs` layer work, the
palette-v2 tokens and all five feature stories belong to the parked batch. `prototypes/**` is never
touched and never staged.

**The rule the operator accepted for the successor batch:** *it repairs exactly what its own stories
make newly reachable, and nothing more.* S-01 and S-02 qualified because US-N13's sala loads every map
in the workspace on mount, which makes both reachable without opening anything.

---

## 4 · Triggers

| id | Verdict | Probe |
|---|---|---|
| **A3** interface change | **NOT FIRED** | Deliberate: §3's fence. No signature in `docs/ARCHITECTURE.md` §4 moves. |
| A1, A4 | NOT FIRED | No module created, no boundary moved, no parallel lanes (0 of 6 pairs disjoint). |
| **B1** shared surface | **FIRED** | `store.load`, the renderers and `HelpScreen` are asserted by tests owned by other requirements. Reverse census owed **derived, not eyeballed** — the feature batch's census was measured 6 files short doing exactly that. |
| B2 | NOT FIRED | No file moves. |
| B3 | NOT FIRED | `ls tests/goldens` → no such directory. |
| **B4** artifact consumed downstream | **FIRED** | `store.load`'s `Graph` is consumed by every screen and renderer. |
| **C** security | **FIRED** | A new refusal path over file-derived text, and a new error message that renders file-derived content. Re-run over the diff at every gate. |
| **D1** visible surface | **FIRED** | S-07 and S-08 are both painted surfaces. |
| E1 | FIRED | 5 stories, 4 increments. |
| F | NOT FIRED | Flow rev46, V7 green. |

---

## 5 · Increments

| Inc | Content | SOURCE | Status |
|---|---|---|---|
| 1 | S-01a cycle refusal | 4 | **PASS WITH CONDITIONS** (F1 → backlog, F2 → closed in Inc-3) |
| 2 | S-01b depth safety | 3 | superseded by Inc-2b |
| 2b | A-6 widened derivation | 3 | **CLOSED** — battery complete, all conditions discharged |
| 3 | S-02 field integrity + A-2 + A-3 | 3 | in progress |
| 4 | S-07 + S-08 | 2 | pending |

Serial — Inc-1/Inc-3 share `store.py` and `model.py`; Inc-3/Inc-4 share `app.py`. Every increment is
inside the ≤4 source-file budget, which is itself evidence the split was cut at the right size.

---

## 6 · Controls this batch is paying for

| Control | How it lands here |
|---|---|
| **Plausible-weaker mutations** (batch 1's main lesson, backlog P-01) | §4 of the requirements names nine, one per predicate, **before** implementation. Deletion alone is not accepted. |
| **False-refusal arms** (C-53) | Two predicates get an arm that must show the fix does **not** reject correct input: an acyclic diamond must still load; a well-formed map's coverage figure must be unchanged. |
| **Per-arm verdicts** (C-40 rider) | One verdict per resolved node id, never the process exit code. |
| **Region-clipped oracles** (C-32) | `AT-R14` exists solely to prove the legend oracle reads only the widget under test — the orchestrator's own S-08 oracle failed this and counted another widget's keybar. |
| **Derived input sets** (C-31) | The legend's expected set comes from `keymap.bindings_for`; the traversal set for depth safety comes from an AST walk. Neither is hand-listed. |
| **Cache-aware restores** (C-46) | Mutations run under `PYTHONDONTWRITEBYTECODE=1`; restores verified by sha256; a green suite immediately after the battery is the proof, not the hash. |
| **No control bytes** (batch 1 §2.4) | Byte-scan every touched file before each commit. |

---

## 7 · Decision log

| # | Decision | Why |
|---|---|---|
| D1 | Split the repair from the features (operator's choice, my recommendation) | Bundling repair and features makes the merge gate judge both in one diff. Batch 1 showed the PR gate is where the serious defects surface. |
| D2 | **No frozen interface moves in this batch** | Otherwise the "small, sharp gate" argument that justified the split evaporates. |
| D3 | **Coerce scalars, reject containers** for S-02 rather than failing the load | Failing the load on a numeric date would reproduce `F-M5`'s shape — one malformed node denying a whole map — which is an open carry, not a pattern to copy. `str({})` is truthy, so containers must be rejected rather than coerced, or the miscount survives the fix. |
| D4 | LLR-R01.4 scoped to the **sink class**, not to the two exception types known today | Batch 1 §2.1b: a requirement naming specific cases gets satisfied at those cases' boundary while the siblings keep the defect. |
| D5 | **A-7 — widen `HLR-R03` from `Ficha.fields` to a set DERIVED from `Ficha`'s annotations** *(taken autonomously; recorded per the kickoff decision-recording grant)* | Executed probe: a non-string `title` or `meta`, and a bare `title:` key that YAML reads as `None`, all break `search_hits` by the identical mechanism. **Fourth instance** of the hand-bounded-set pattern A-6 recorded. `state` is the discriminating negative — no consumer joins it — which is precisely why the set is derived rather than widened by hand. Costs no extra file: the same loop in `_graph_from_sidecar`. |
| D6 | **A-8 — relabel `AT-R07`; a container DENIES the map rather than miscounting** *(autonomous)* | Executed: `fields.D = {}` raises `sqlite3.ProgrammingError` from `_reindex`, which cannot bind a `dict`. The acceptance text stands (it describes post-fix behaviour) but the pre-fix cause was wrong, so `AT-R07`'s RED would have been recorded for the wrong reason — C-40's *"a typo'd mutation also fails, for the wrong reason"* applied to a counterfactual. D3's `str({})`-is-truthy reasoning is unaffected. |
| D7 | **Re-run the whole mutation battery rather than resume from the failed arm** *(autonomous)* | Two harness faults halted it mid-run. One continuous transcript against one baseline is the evidence artifact; splicing partial runs is what C-19 forbids. Cost ~40 min, paid deliberately. |
| D8 | **Move the mutation harness OUT of the repository it mutates** *(autonomous)* | Three separate incidents left a mutation applied on disk. The structural cause is an untracked mutator living beside the tracked files it edits, so `git status` cannot distinguish its damage from the increment's own work. |
| D9 | **Enumerate every id in the §6 traceability table** *(autonomous)* | The table used en-dash ranges while the sentence beneath it asserted no ranges appeared in the document. An en-dash range is no more scannable than a dotted one (C-56); the claim and the table now agree. |
| D10 | **Re-run Inc-2b's F1 arm at the plausible value before accepting the increment** *(autonomous)* | The battery ran the cap at an extreme (1); the reviewer's condition named `[3, 9]`. A conditional verdict is not an authorisation, and the condition was discharged in form but not in substance. Cost ~2 min; it is the difference between an arm that proves the pin and one that proves the file is readable. |
| D11 | **A-9 — `required_coverage` delegates to `missing_required` instead of re-deriving it** *(autonomous)* | Found by increment 3's own coverage regression. The two predicates disagreed on a whitespace-only value: `missing_required` called it missing, `coverage()` counted it documented — the quiet inflation US-R03 exists to stop, sitting inside the function whose docstring calls itself *"the single owner of what is missing"*. Structural duplication of a predicate (C-50): no assertion over output could have caught it, because on every other input the two agree. Fixed rather than carried — it is two lines in a file the increment already owns, and weakening the new test to match the drift would have been the worse failure. |
| D12 | **Delete the A-3 deferral record rather than empty it** *(autonomous)* | Closing A-3 made `DEFERRED_BY_AMENDMENT_A3` empty, and `deferred <= census` is true for *every* census once the left side is empty — the staleness guard would have survived as a check that cannot fail. Its assertion was ported into the stronger form (`census == set()`, subtracting nothing) in the same commit; the ledger records the deletion with its named successor. |
| D13 | **Ruff's gate metric is `mapper/ + tests/`, not `ruff check .`** *(autonomous, recorded because the briefed premise looked wrong)* | Bare `ruff check .` reads **57**; the briefed pre-existing figure is **29**. Executed: `mapper/` 11 + `tests/` 18 = 29, and the other 28 are all in untracked `prototypes/`, which is never staged. The premise held; its scope was simply never written down. |

---

## 8 · Postmortem obligation carried from the operator

The orchestrator's **own** artifact errors are recorded as findings at the same standard batch 1 was
held to: the A3 reverse census being 6 files short, the S-08 oracle reading another widget's pixels,
the P-19 arithmetic, and an S-02 reproduction that first returned a plausible all-clear because the
fixture used the wrong sidecar shape.

---

## 9 · Increment gates

### Inc-1 · HLR-R01 cycle refusal — **PASS WITH CONDITIONS** (no HIGH)

Reviewed independently by `code-reviewer`; **4 source files** (`model.py`, `mermaid.py`, `store.py`,
`app.py`), +132/−40, plus a new 381-line test file. Suite **265 passed, exit 0**; ledger
`265 = 245 − 0 + 20` reconciles on collected counts. Ruff **29 before, 29 after** — verified by the
reviewer's own stash, not taken from the author.

**What the reviewer established independently rather than accepting:** `Graph.find_cycle()` was fuzzed
over **4000 random digraphs against a Kahn topological-sort oracle sharing no code with it — 0
mismatches**, every returned path re-validated as a real edge-walk, and termination confirmed to a
50 000-deep chain in 44 ms. The back-edge vs re-visit distinction — the thing that makes a diamond
legitimate and `a→b→c→a` a cycle — holds in the code, not just in the packet.

**All three self-disclosed weaknesses checked out as disclosed**, and one came back *stronger* than the
author claimed: no constant can pass both `TC-R07` and `AT-R02`, because `AT-R02` asserts the two
messages **differ** before asserting their content — so it is unkillable-by-constant structurally, not
by fixture luck. The reviewer also ran an arm the author never declared (an order-normalising, per-input
but *wrong* transform) to prove the oracle set is order-sensitive and not merely constant-sensitive.

**Conditions carried:**

| # | Finding | Condition |
|---|---|---|
| **F1** | **The refusal made the store's read side stricter than its write side.** A cyclic CSV can still be *saved*; the very next load — the one `action_save` itself triggers — raises, so the file is a permanent poison pill listed with 0 nodes and no in-app repair. **On `master` that file at least loaded.** | Restate D-4 to name the persisted-unloadable consequence, and file the symmetric `MapStore.save` refusal to the backlog. Not fixed here — Inc-1 does not grow. |
| **F2** | **`LLR-R01.4`'s sink-class *breadth* is uncertified on `HomeScreen.on_mount`.** The reviewer narrowed the handler to the type this batch produces and **zero nodes reddened across the whole `tests/` tree.** The code is correct today; nothing stops a future narrowing — which is the exact failure the LLR's own rationale cites. | Arm it (parametrize `TC-R09`) **before Inc-3 lands**, since Inc-3 re-touches `app.py` and would inherit an unarmed guard. |
| F3–F5 | duplicate cycle-path spelling; a census row that is vacuously true (there is **no** `except ParseError` anywhere, so nothing was preserved); `Graph.resolve_document` recurses over `parent_of` and sits **outside** Inc-2's `views/`-scoped AST walk | recommendations; F5 goes to the batch as a decision, not an omission |

**Ruling on the out-of-scope guard: keep it.** The reviewer reproduced the `_ImportPreviewScreen`
crash independently and confirmed `import_csv.preview_csv` never touches `mermaid.parse`, so the
refusal provably cannot reach that door. Carrying it would have shipped batch 1 §2.1b's exact shape
knowingly, with the reproduction already in hand.

**Operational finding — the Inc-2 tree hangs the suite.** The reviewer's clean 265-pass run was taken
while `mapper/views/` was still byte-identical to `master`; a later re-run **hung past 300 s** against
Inc-2's rewritten renderers. Not attributable to Inc-1 — the reviewer closed its own evidence cleanly by
re-running this increment's non-Textual plane (**15 passed in 0.22 s**). Flagged to Inc-2's gate.

### Inc-2 · HLR-R02 depth safety — **BLOCKED on a HIGH**, closed by Inc-2b

`code-reviewer` blocked on **F1**: `OutlineRail.visible_rows`'s inner `walk` is a recursive `Graph`
traversal that raises `RecursionError` at depth 5000, runs inside `OutlineRail.render()` — which
Textual's compositor calls, **outside** `refresh_canvas`'s `try/except` — and was owned by no
increment in §5. Reproduced by the orchestrator with a positive control (depth 3 → 4 rows; 500 → OK;
5000 → `RecursionError`).

**The code in Inc-2's diff was correct.** The reviewer established that independently and generously:
`_leaves` equivalence re-derived against the real `master` source over 14 shapes — **515 node
comparisons, 0 mismatches**, adding five re-convergent shapes the author's set lacked; output identity
across **105 cells** with **0 differing**; and M5/M10 re-executed node-for-node, confirming that with
the recursion limit raised from inside the render the deep-chain test **stays green** and only the
frame-counting probe and the AST derivation catch it. The defect was in **my requirement**, not in the
implementation.

### Inc-2b · A-6 — **CLOSED · PASS WITH CONDITIONS, all discharged**

Superseded the block recorded below. The battery ran to completion —
**14 arms, 0 inert, 0 failed restores, 72 RED node-verdicts, post-battery 356/356, every
sha256 restore `True`** (`03-increments/mutation-battery.txt`) — and the packet's checklist was
filled from that transcript rather than from intent.

`code-reviewer` returned **PASS WITH CONDITIONS** (`increment-002b-review.md`); checklist item 6
is discharged by that artifact. The four conditions, each verified by **re-reading the artifact**
rather than by trusting the corrective pass ran:

| # | Condition | Discharge |
|---|---|---|
| F1 HIGH | pin the indent cap through a call, re-run arm N7 with a cap in `[3, 9]` | Fix ✓ (`test_repair_depth.py:1175` reads `RAIL_WIDTH - 4` through the code). **Arm ✗ as run** — the battery mutated the cap to **1**, an extreme, not the plausible value. Re-run in increment 3's scratchpad at **cap → 6**: `test_tc_r30_the_indent_cap_cannot_change_a_rendered_row` **RED**, baseline 356/356, restore hash-verified. Now genuinely met. |
| F2 MEDIUM | remove the rail's false refusal | ✓ `_missing_walk` (`rail.py:112`) |
| F3 MEDIUM | declare the factory node's asymmetry; carry a composed-screen node to Inc-3 | ✓ discharged **in Inc-3** — docstring declared, `test_at_r16b_the_factory_screen_survives_a_depth_5000_map_composed` added |
| F4 MEDIUM | `darkside.plain` at `factory.py:246` | ✓ done, with the reason in the comment. The other 11 `escape(...)` sites go to `security-reviewer` as a C-17 sweep |

**The F1 arm is this batch's second instance of one lesson**, and it is the one the postmortem owes:
*a plausible-weaker arm that was not weak enough.* The plausible mutation is **a number that looks
like it fits**, not an extreme — cap → 1 breaks six nodes loudly, cap → 6 breaks exactly one, and it
is the second that a real regression would look like.

### Inc-2b · the block this superseded (retained for the record)

The implementer first **stopped before writing any code**, correctly, because closing the widened
derivation honestly required crossing a fence — and in doing so found the pattern's **fourth**
instance and two further members (`screens/factory.py:177`, `model.py:97`). Scope call: option B.

It then implemented, and the work looks substantial and right. **But the increment cannot be
accepted, because its evidence does not exist:**

| Gate item | State |
|---|---|
| Packet §4 Test results · §5 Risks · §6 Pending · §7 Next | literally the word **`placeholder`** |
| Mutation battery | `scratch/mutation-log.txt` is **0 lines** — the battery never ran, or wrote nothing |
| `scratch/` deletion (instructed) | **not done** — 11 files still untracked in the repo root |
| `out.txt` | loose and untracked in the repo root |

**This is the flow's own hard rule, not a preference:** *a phase gate never accepts an artifact still
in unfilled-template form; remaining placeholders mean the phase did not actually run.* Validator `V1`
blocks on the same condition. An increment whose counterfactuals were never executed has **no
evidence that any of its predicates can fail** — which is precisely C-40, and precisely the property
this batch exists to enforce.

**Disposition:** resume the increment to run the battery and complete the packet. The code is not
under suspicion; the evidence is missing, and the two are not interchangeable.

---

## Session 5 (2026-08-27) — Inc-3 re-gate, Inc-4 preparation

**Where we are.** Increments 1, 2, 2b and 3 are code-complete on
`fix/shipped-defects-repair`, nothing committed. Full suite **410 passed, exit 0** (111.3 s);
fast lane **394 passed, 16 deselected**; `ruff check mapper tests` = **29**, the pre-existing
figure from decision D13. Increment 4 is designed and measured but **not started** — it is
held behind the Inc-3 re-gate rather than run in parallel, because adding even a test file
moves the collected node count and would corrupt the reviewer's ledger check mid-run.

### The evidence-integrity incident, found at re-verification

The increment-3 code review returned **BLOCKED** on `F1` (HIGH). The author fixed the tree
and re-ran the battery — and **the v2 transcript was never landed in `03-increments/`.** The
file the packet pointed at was the superseded 18-arm run over a tree that no longer existed:
its pinned hashes for `store.py` and `model.py` did not match disk.

| | v1 (was on disk, cited by the packet) | v2 (was in the scratchpad only) |
|---|---|---|
| arms | 18 | **20** |
| baseline | 409 | **410** |
| RED verdicts | 134 | **138** |
| `store.py` final hash | `7f50f248…` | **`1b1b9e2b…`** ← matches disk |
| `model.py` final hash | `d1cb6160…` | **`3d39a861…`** ← matches disk |

Caught by comparing the transcript's pinned hashes against an independent `sha256sum`.
**Nothing was re-measured to fix it** — the measurement was sound, only unlanded. v2 is now
`mutation-battery-inc3.txt`; v1 is retained as `mutation-battery-inc3-v1-prefix.txt` for
provenance and is explicitly **not** evidence.

**Decision (autonomous, recorded per the standing authorization):** reconcile the packet to
revision 2 and re-gate, rather than gate the packet as found. Gating an artifact whose
evidence pointer is stale is the defect this batch exists to stop, and it is indistinguishable
to any later reader from evidence that was never produced (C-44).

### Decisions taken without asking, this session

| # | Decision | Reason |
|---|---|---|
| D14 | Discharge `F1` via **fix A** (delete the walk) rather than fix B | A bounded no-op is still a no-op, and it was carrying a guard whose only regression mode was a hang. Fix A dissolves Risk 4 instead of mitigating it |
| D15 | **Delete** Risk 4 and pending item 1 rather than carry them | The review's §4 note instructs exactly this when C1 closes via fix A |
| D16 | **Decline** LOW nits `F7` and `F9`; declare the declining in §2 | Both cosmetic, neither changes a value. Applying them would move `store.py` after its eight battery arms ran, buying a re-run for zero behavioural change. Carried to the backlog with their line addresses |
| D17 | `F2` (C2) **declared as a risk, not guarded** | Widening the non-`dict` guard is `F-M5`'s repair, which is fenced out of this batch; a partial widening half-fixes a defect another batch owns |
| D18 | Keep **both** battery transcripts on disk, clearly named | The review's C1 demanded a new arm; having both runs makes the before/after auditable rather than asserted |
| D19 | Write a **corrected** byte scanner rather than re-use the scratchpad's | The existing `bytescan.py` still reports one trailing-whitespace line per line for a CRLF file. Increment 2b recorded that falsehood; re-inheriting it would be the third instance |

### Increment 4 — designed and measured, not yet written

Both defects reproduced by execution before any fix was drafted (C-35).

**S-07.** `MapScreen.CSS` declares `#map-canvas` and `#map-inspector` and **no `#map-rail`
rule at all**, so the rail takes the whole terminal:

| Terminal | `#map-rail` | `#map-canvas` | `#map-inspector` |
|---|---|---|---|
| 140×45 | x=0 **w=140** | x=140 w=1 | x=141 w=36 → right=**177**, off-screen |
| 120×40 | x=0 **w=120** | x=120 w=1 | x=121 w=36 → right=**157**, off-screen |
| 100×24 | w=0 (auto-collapsed) | x=0 w=64 | x=64 w=36 → fits |

The 100×24 row is the discriminating negative: the rail auto-collapses there, so the layout
already holds and `AT-R10`'s RED is attributable to the rail's WIDTH rather than to "some
layout assertion somewhere".

**S-08 — and the oracle is the finding.** Three candidate oracles were compared on the same
frame; each is wrong in a different direction, and none of the wrongness is visible by reading:

| Oracle | Missing at 140×45 | Verdict |
|---|---|---|
| `Screen.render_line(y)` | 27 of 27 | **false-fails a correct implementation** — it renders the screen's own line, not the composited frame |
| the content widget's own `render_lines` | **0 at every size** | **vacuous** — the `Static` really does render all 27 rows; `max-height` clips them with no scroll, and a widget's own paint cannot see a reachability defect |
| composited frame **clipped to the dialog region** | **11 — the whole `view` group** | correct |
| the same read **unclipped** | 10 | under-reports by exactly one word, `cobertura`, donated by `MapScreen`'s keybar through the 70 % backdrop |

`AT-R14` therefore compares **whole rows, not substrings** (`cobertura 100%` is painted
outside the dialog while `cobertura` is a legitimate binding label) and derives its sentinel
set at runtime — a hand-picked one (`finanzas`) was measured to sit *under* the dialog,
absent from both reads, discriminating nothing.

**Fix prototyped outside the tree** (subclassing, not editing, since a reviewer holds the
measurement lock): the bindings region becomes a `VerticalScroll` with the title fixed above
it — which is what `LLR-R05.1` asks for, the bindings *region*, not the dialog. Measured
`max_scroll_y` 14 at 140×45 and 21 at 100×24, **0 bindings missing after scrolling at all
three sizes**.

**Test set drafted (11 nodes), staged in the scratchpad.** Two gaps caught while drafting,
both of which would have shipped green: `AT-R12` alone is one-directional (a panel dumping
all 48 bindings satisfies "nothing missing"), and `TC-R25` alone shares `bindings_for` with
the code it certifies — so `TC-R26` reaches past that to the full `KEYMAP`.

### Carries opened this session

1. `mapper/store.py:226` — `_text_attributes()` recomputed once per node (`F7`, declined here).
2. `mapper/store.py:31` — `str` unreachable in `("str", str)` (`F9`, declined here).
3. **Five** screens push `HelpScreen()` with **no scope**, resolving to `SCOPE_APP` — `app.py:774`,
   `app.py:825`, `app.py:1090`, `screens/factory.py:489`, `screens/settings.py:95`. *(Said "three"
   until the merge gate counted them: finding `L-3`. A hand-count in a carry is the same defect as
   a hand-count in a census.)* Shadowed
   today by the app-level priority binding for `?`. `AT-R13` reddens if that shadowing changes.
   Repairing the call sites is outside this batch's fence.
4. `scratch/` and `out.txt` are **already absent** from the tree, but go into `.gitignore` at
   the close anyway — they were the surface of two prior incidents.
