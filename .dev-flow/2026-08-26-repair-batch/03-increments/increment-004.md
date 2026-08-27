# Increment 004 — `HLR-R04` (S-07) and `HLR-R05` (S-08)

| Field | Value |
|---|---|
| Batch | `2026-08-26-repair-batch` |
| Increment | `004` — the last two shipped defects |
| Lane | not forked · owns `mapper/app.py` (`MapperApp.CSS`) and `mapper/screens/help.py` |
| Requirement(s) | `HLR-R04` · `LLR-R04.1` **as amended by A-10** · `HLR-R05` · `LLR-R05.1`, `LLR-R05.2` |
| Acceptance | `AT-R10`, `AT-R10b`, `AT-R11`, `AT-R12`, `AT-R13`, `AT-R14` · white-box `TC-R22`, `TC-R23`, `TC-R24`, `TC-R25`, `TC-R26` |
| Agent | `software-dev` (supervised-incremental-development) |
| Date | 2026-08-27 |

---

## 1 · What changed

**The canvas and the inspector are back on screen whenever the rail is shown, and the help
overlay now reaches all 27 bindings instead of painting 16 and dropping the `view` group in
silence.** Both defects were reproduced by execution before a line of fix was written, and in
both cases the measurement changed the design.

### S-07 — the rail had no width rule at all

`MapperApp.CSS` declared `#map-canvas` and `#map-inspector` and **nothing for `#map-rail`**, so
the rail took the full width of `#map-body` and pushed everything else off the terminal:

| Terminal | `#map-rail` | `#map-canvas` | `#map-inspector` |
|---|---|---|---|
| 140×45 | x=0 **w=140** | x=140 w=1 | x=141 w=36 → right **177** |
| 120×40 | x=0 **w=120** | x=120 w=1 | x=121 w=36 → right **157** |
| 100×24 | w=0 *(auto-collapsed)* | x=0 w=64 | x=64 w=36 → fits |

The 100×24 row is why `HLR-R04` is scoped *"when the rail is displayed"*: below
`MIN_CANVAS_WIDTH` the screen hides the rail on its own, so the layout already held there. That
row became `AT-R10b`, the discriminating negative — without it, `AT-R10`'s RED would only tell
us *some* layout assertion fails, not that it fails **because of the rail's width**.

**The 24 in the stylesheet is a LITERAL and not an interpolation of `RAIL_WIDTH`.** That is the
whole content of `LLR-R04.1`: `TC-R22` asserts the two agree, and a value the stylesheet derived
from the constant could never disagree with it. An f-string here would have turned the
requirement's gate into an identity — C-40 limb 1, self-inflicted.

### S-08 — 40 rows of body under a 28-row cap with no way to scroll

`SCOPE_MAP` carries 27 bindings in 5 groups, which `_render_keymap` renders as 40 rows. The
dialog was `height: auto; max-height: 28`, so the surplus was clipped away and **the entire
11-member `view` group fell off the bottom** — measured, not inferred.

The bindings now live in a `VerticalScroll`; the **title does not scroll with them**, because the
title is the one row that tells the operator which scope they are reading. That is also what
`LLR-R05.1` asks for by its own wording: the *bindings region* shall be scrollable, not the
dialog.

### A-10 — a false premise in the requirement, found by executing it

`LLR-R04.1` names **`MapScreen.CSS`** as the touched symbol. **`MapScreen` has no CSS block.**
The sibling `#map-canvas` and `#map-inspector` rules live on `MapperApp.CSS`, and adding a second
stylesheet for one rule would fork the convention for no gain. The rule joined its siblings and
the **spec's premise was corrected rather than the code bent to fit it** (C-43).

`TC-R22` found this by failing on its first run against the real tree. Its first correction was
then *also* wrong: `assert not hasattr(MapScreen, "CSS")` is **False**, because Textual's `Screen`
base defines `CSS = ""` and the name resolves to an inherited empty string. **That is C-15's
inherited-attribute trap verbatim** — existence satisfied while denoting the wrong object — and
it cost one run to find. The honest predicate is `"CSS" not in MapScreen.__dict__`.

---

## 2 · Files modified

**The budget counts SOURCE files only. Tests are not capped.**

| File | Kind | Change |
|---|---|---|
| `mapper/app.py` | source | one rule added to `MapperApp.CSS`: `#map-rail { width: 24; height: 100%; }`, with the comment recording the measured pre-fix geometry and why the 24 is a literal |
| `mapper/screens/help.py` | source | `VerticalScroll` around the bindings `Static`; `#help-bindings` rule; dialog `height: auto` → `90%`; `VerticalScroll` added to the `textual.containers` import |
| `tests/test_repair_layout.py` | test | **new**, 15 nodes |

| Count | Value |
|---|---|
| **SOURCE files** | **2** — well within the ≤4 budget |
| Test files | 1 (uncapped) |

**What was NOT touched.** ✓ Frozen interfaces absent — `IRenderer.render` and `Canvas` are not in
this diff and neither file imports either. No file owned by increments 1, 2, 2b or 3 was opened.
`prototypes/**` remains untracked by design and is never staged.

---

## 3 · How to test

```bash
cd C:/Users/jjgh8/Github/mapper

# the gate run — BOTH lanes
PYTHONUTF8=1 python -m pytest -q -p no:randomly -o addopts=

# this increment alone, per node
PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_repair_layout.py \
    -p no:randomly -o addopts= -v

# the neighbours most likely to notice a layout change
PYTHONUTF8=1 python -m pytest tests/test_rail.py tests/test_app.py -p no:randomly

# lint — the gate metric is mapper/ + tests/, never a bare `ruff check .` (D13)
python -m ruff check mapper tests
```

---

## 4 · Test results

| Lane | Command | Collected | Result | Wall clock |
|---|---|---|---|---|
| both | `pytest -q -p no:randomly -o addopts=` | **425** | **425 passed, exit 0** | 102.9 s |
| this increment | `tests/test_repair_layout.py` | **15** | **15 passed** | 4.9 s |

Ruff over the gate metric `mapper tests`: **29 before, 29 after** — the pre-existing figure from
decision D13, unchanged by this increment.

### Signed-balance test ledger

`post = base − D + A` → **`425 = 410 − 0 + 15`** ✓ reconciled against `--collect-only`.

- base **410**, the tree state increment 3 handed over after its own re-gate.
- **D = 0.** No test was deleted, rewritten or renamed. No existing node changed its id.
- **A = 15**, all in the new `tests/test_repair_layout.py`. No test was skipped or xfailed.

### RED counterfactual — executed, not predicted

Two runs. The main battery is `mutation-battery-inc4.txt` (8 arms); the supplement is
`mutation-battery-inc4-supplement.txt` (3 arms), run because the main one reported two arms
inert and **an inert arm is a result to investigate, not a footnote**. Both baselines resolved
**425 of 425, all passed**; both post-battery suites came back **425/425, `not passed: none`**;
**0 failed restores** across both, every file's sha256 returning to its pre-mutation value.

| Arm | Kind | File | RED | What it proves |
|---|---|---|---:|---|
| L1 | deletion | `app.py` | **5** | the `#map-rail` rule itself |
| **L2** | **plausible-weaker** | `app.py` | **4** | **`width: 1fr` on the rail** — the requirements' declared arm. On-screen **and** disjoint, so a layout test asserting only those two passes while the rail eats half the canvas |
| **L3** | **plausible-weaker** | `app.py` | **4** | the declared width **off by one** — the CSS and `RAIL_WIDTH` drift apart, which is the whole of `LLR-R04.1` |
| ~~L4~~ | ~~deletion~~ | `help.py` | **0** | **retired — a no-op mutation.** See below |
| ~~L5~~ | ~~plausible-weaker~~ | `help.py` | **0** | **retired — a no-op mutation.** See below |
| L6 | deletion | `help.py` | **5** | the scrolling container itself |
| **L7** | **plausible-weaker** | `help.py` | **4** | **present every binding of every scope** — passes "nothing is missing" completely, and is a different defect wearing the same green |
| **L8** | **the oracle's own arm** | `test_repair_layout.py` | **1** | **read the whole frame instead of the dialog's region.** `AT-R14` alone |
| **L4b** | **negative control** | `help.py` | **0 — predicted** | plain `Vertical` **keeping** the `overflow-y` rule |
| **L4c** | **deletion** | `help.py` | **3** | plain `Vertical` **and** no `overflow-y` — S-08 restored |
| **L5b** | **plausible-weaker** | `help.py` | **1** | make today's 27 **fit**, so nothing scrolls |

**Live arms: 9. Negative controls: 1. Retired as no-ops: 2. Total RED verdicts: 27.**
One verdict **per resolved node id**; the process exit code is never used as a verdict (C-40
rider). Every arm ran under `PYTHONDONTWRITEBYTECODE=1` with `__pycache__` purged, and mutations
are described here by position and operation rather than pasted, per C-56.

#### The two inert arms were not inert TESTS — they were no-op MUTATIONS

This is the increment's main finding, and the distinction matters because the two call for
opposite responses. C-40 says an inert arm means *rewrite the predicate, do not re-argue it*.
That applies when the mutation genuinely changed the thing the predicate claims to certify. Here
it had not:

| Arm | What it changed | Why nothing could redden |
|---|---|---|
| **L4** | deleted `overflow-y: auto` from `#help-bindings` | **`VerticalScroll.DEFAULT_CSS` already declares `overflow-y: auto`.** The pane kept scrolling. Verified by reading the framework's own default, not inferred |
| **L5** | raised `max-height` 28 → 44 | **`height: 90%` binds first** at every size under test — 90 % of 45 is 40, and 40 < 44 — so the dialog never changed size |

This is **C-55 limb 2** exactly: *mutating a stage is not mutating the pipeline.* Both arms aimed
at a declaration that was not the one deciding the property. The response was to aim at the
declaration that was, and the supplement is that run.

**`L4b` and `L4c` are a PAIR and are only meaningful together**, which is why they were authored
and executed as one unit:

- **`L4b` swaps in a plain `Vertical` while KEEPING the CSS rule → 0 RED, and that was
  pre-registered as the expected outcome** in the arm's own `proves` text before it ran. Its
  greenness is the evidence: `#help-bindings { overflow-y: auto }` **overrides** `Vertical`'s
  `overflow: hidden hidden`, so the pane still scrolls. **The CSS rule is therefore a genuine
  second guard, not the redundancy `L4` made it look like.** The harness prints `L4b` under
  `INERT ARMS` because it counts RED verdicts; that label is mechanically correct and
  substantively wrong, and it is recorded here rather than left to mislead a later reader.
- **`L4c` removes both sources at once → 3 RED**, `AT-R12` at all three sizes. That is S-07's
  sibling defect restored in full and caught in full.

**`L5b` reddens exactly one node — `TC-R24` — and that node is a vacuity guard.** `TC-R24`
asserts `virtual_size.height > region.height` *before* asserting `max_scroll_y > 0`, with the
message *"the fixture no longer produces more bindings than fit; this node would pass without
testing anything"*. Make today's 27 bindings fit and it is that first assertion that fires. This
is the requirements' declared arm — *"green now, silently re-broken by the next binding added"* —
and the guard that catches it is the one written specifically so the test cannot pass vacuously.

#### L8 — the arm that decides whether any other S-08 result is worth reading

`AT-R14` exists because the oracle needed one. Measured **before** the fix, on the shipped tree:

| Oracle | Bindings reported missing at 140×45 | Verdict |
|---|---:|---|
| `Screen.render_line(y)` | **27 of 27** | **false-fails a correct implementation** — it renders the screen's own line, never the composited frame |
| the content widget's own `render_lines` | **0 at every size** | **vacuous** — the `Static` really does render all 27 rows; `max-height` clips them, and a widget's own paint cannot see a *reachability* defect |
| composited frame **clipped to the dialog** | **11 — the whole `view` group** | correct |
| the same read **unclipped** | **10** | under-reports by one |

The unclipped read is wrong by exactly one word: `HelpScreen` is a `ModalScreen` with
`background: #000000 70%`, and `MapScreen`'s keybar shows through the backdrop donating
`cobertura`. **An unclipped oracle therefore passes a fix that still hides a binding.** `L8`
removes the clip and `AT-R14` reddens alone — which is what makes every `AT-R12` figure above
admissible.

Two details of `AT-R14` were forced by measurement rather than chosen:

1. **It compares whole rows, not substrings.** `cobertura 100%` is painted outside the dialog at
   y=11 while `cobertura` is a legitimate binding label — a substring test collides.
2. **Its sentinel set is derived at runtime, never hand-listed** (C-31). The hand-picked sentinel
   tried first (`finanzas`) was measured to sit *under* the dialog, absent from both the clipped
   and the unclipped read, and therefore discriminating nothing.

### Load-bearing emptiness — C-55

| Field | Value |
|---|---|
| Does any claim rest on an absence? | **Yes.** `AT-R14` limb (b) asserts that **no** row painted outside the dialog appears in the clipped read |
| Positive control for that absence | **limb (a), in the same node**: the set of rows outside the region must be **non-empty**, or limb (b) is vacuous. Measured: 9 non-blank rows below/above the band plus 3 beside it |
| Conjunctive criterion, one mutation per conjunct | `HLR-R05` is *present every binding* **and** *drop none without declaring it*. `L6`/`L4c` mutate reachability; `L7` mutates the set; `L5b` mutates the need to scroll at all |
| The case the tree does not contain | `AT-R10b` builds the terminal size at which the rail is **absent** — the other half of "when the rail is displayed", which no other node exercises |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| **B1** symbols asserted by **other** tests | `grep -rl` for `#map-rail`, `#map-canvas`, `#map-inspector`, `RAIL_WIDTH`, `HelpScreen`, `help-dialog`, `help-content` across `tests/` | **FIRED.** `RAIL_WIDTH` and the region ids → `tests/test_rail.py`; `HelpScreen` → `tests/test_app.py`. **All green after the change**, and confirmed by execution: the full suite moved 410 → 425 with **0 pre-existing nodes changing verdict** |
| **B4** artifact consumed downstream | `grep -rln` across `mapper/` | **FIRED.** `#map-rail` is queried by `MapScreen._apply_region_visibility` and `refresh_canvas`; `_chrome_width()` feeds the canvas width. `AT-R10` asserts that relation directly rather than restating it |
| B2 file moved on disk | `git status --porcelain \| grep ^R` | did not fire — no renames |
| B3 byte-identical golden captures this source | rail/`layered` sha256 constants in `tests/test_repair_depth.py` | **did not fire** — and this is worth stating: the rail's own **rendered content** is unchanged, only its allotted width. Arms L1–L3 reddened **no** golden, which is the evidence |
| A3 interface consumed by another module changed | `HelpScreen.__init__`, `_render_keymap` signatures | **empty** — `compose`'s body changed, no signature did |

### Byte-scan — every file this increment touched

Executed after both batteries, so these are the bytes that will be committed.

| File | Bytes | BOM | bare CR | TAB | ESC | other control | UTF-8 | endings | trailing-ws lines |
|---|---:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| `mapper/app.py` | 81 296 | ✗ | 0 | 0 | 0 | none | ✓ | CRLF | 0 |
| `mapper/screens/help.py` | 3 180 | ✗ | 0 | 0 | 0 | none | ✓ | CRLF | 0 |
| `tests/test_repair_layout.py` | 20 055 | ✗ | 0 | 0 | 0 | none | ✓ | LF | 0 |

sha256: `3476bdf5…b9b001a5`, `832f6922…50a89fde`, `516a8756…84e8878a` — **identical to the
digests both batteries restored to**, so the scanned bytes and the measured bytes are the same
bytes. Measured with a **corrected** scanner: the one in the session scratchpad still reports one
trailing-whitespace line per line for a CRLF file, the falsehood increment 2b recorded, and it is
fixed rather than re-inherited. Non-ASCII code points are Spanish accented vowels and `·` only;
no `U+2028`/`U+2029`, no zero-width, no bidi controls.

---

## 5 · Risks

1. **`#help-bindings`'s `overflow-y: auto` looks redundant and is not.** `VerticalScroll` already
   supplies it, so a reader tidying the stylesheet would delete it and every test would stay
   green — arm `L4` is precisely that experiment, and it measured 0 RED. What the rule actually
   guards is the *other* mutation: swapping the container for a plain `Vertical`, where the rule
   overrides `overflow: hidden` and keeps the pane reachable (`L4b`). **The comment in the CSS
   does not currently say this**, and a rule whose purpose is invisible is a rule that gets
   removed. Carried to §6.
2. **The dialog's `height: 90%` is doing the sizing, and `max-height: 28` now rarely binds.**
   At 140×45, `90%` is 40 and the cap clips to 28; at a much taller terminal the cap governs, and
   at a short one `90%` does. Two declarations sharing one responsibility is how `L5` came to
   measure nothing, and the next person to tune the dialog's size will meet the same ambiguity.
3. **`AT-R12`'s scroll loop is bounded at 60 iterations** and calls `pytest.fail` if the pane
   never reaches its scroll limit. That is deliberate — a scroll that does not terminate must be
   a red, not a hang, which is the lesson increment 3's `TC-R23` paid for — but the bound is a
   magic number that will need raising if the keymap grows several-fold.
4. **`AT-R12` and `AT-R13` drive `pane.scroll_to(...)` directly rather than pressing a key.**
   The requirement is that the content be *reachable*, and no binding currently scrolls the help
   pane, so there is no key to press. If a scroll binding is ever added, these nodes should drive
   it instead — otherwise they verify the mechanism while the operator's actual route goes
   untested (C-16's shape).
5. **Three screens push `HelpScreen()` with no scope argument**, resolving to `SCOPE_APP`, which
   would present 2 bindings instead of the screen's own. Those paths are shadowed today by the
   app-level priority binding for `?`. `AT-R13` asserts the scope explicitly and reddens if that
   shadowing ever changes, but **the call sites are not repaired here** — they are outside this
   batch's fence.
6. **`TC-R25`/`TC-R26` read the panel's rendered `Text`, not painted pixels.** That is the right
   layer for set equality — binding *labels* are not unique (`volver` names three bindings,
   `cerrar` three), so a foreign row is not always distinguishable from a wanted one once it is
   text on a screen. But it means the set is asserted one layer below the surface, and only
   `AT-R12`'s completeness check crosses that gap.

---

## 6 · Pending items / spec deviations

1. ~~Amendment `A-10` needs writing into the requirements.~~ **Done at the increment close** —
   `01-requirements.md` §7 now carries `A-10` with its Before → After text and the executed probe.
   **`A-9` was found missing in the same sweep** and written too: increment 3 allocated the id and
   described the change in its packet but never recorded the amendment, which is the same omission
   the re-gate caught one row down in §6's traceability table (`G5`). Two ids allocated, two
   amendments unwritten — worth naming as a pattern in the post-mortem rather than a slip.
2. **Say in the CSS why `#help-bindings`'s `overflow-y` is not redundant** (Risk 1). One comment
   line, and it is the difference between a guard and a line someone deletes on a tidy-up.
3. **Collapse `height: 90%` / `max-height: 28` to one governing declaration** (Risk 2), or state
   in a comment which governs when.
4. **A scroll binding for the help pane** would let `AT-R12` drive the operator's real route
   (Risk 4). Not this increment's to add — it is a new binding, which is feature work.
5. **The three unscoped `HelpScreen()` call sites** (Risk 5) — backlog, outside the fence.
6. **`-m slow` CI lane still unwired** — increment 2b's Risk 7, increment 3's pending item 4,
   unchanged. This increment adds nothing to that lane.
7. **No suite-level wall-clock bound** — increment 3's pending item 9, unchanged. `AT-R12`'s own
   60-iteration bound is a local answer to the same hazard, not a general one.

---

## 7 · Suggested next task

**Close the batch.** All four shipped defects (S-01, S-02, S-07, S-08) are repaired and gated.
What remains is the whole-branch work, in this order:

1. **`security-reviewer` over the full diff vs `origin/master`** — the C-family triggers fired at
   intake (a new refusal path over file-derived text, new error messages rendering file-derived
   content, and now a fourth `notify` sink family). The re-gate handed over `F11` explicitly.
2. **An adversarial PR-level `qa-reviewer` pass over the whole merged diff** — dual traceability
   intact, no cross-increment regression, every gate carry discharged.
3. **`.gitignore` gains `scratch/` and `out.txt`** as part of this batch. Neither exists in the
   tree today; both were the surface of prior mutation-left-on-disk incidents, so the entry is
   preventive.
4. **Commit with explicit paths** — never `prototypes/`, never `mapper.db` — push, PR, merge,
   then `/dev-flow-sync`.

The post-mortem owes four items this increment sharpened: the harness-defect catalogue, the
no-op-mutation distinction found here, the `notify`-stub sink-class pattern that recurred three
times, and the dead-computation lesson from increment 3.

---

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|
| 1 | ≤ budget source files, or reason declared | ✓ | **2 source files** — `mapper/app.py`, `mapper/screens/help.py`; §2 |
| 2 | Tests written in this same increment | ✓ | `tests/test_repair_layout.py`, **new, 15 nodes** |
| 3 | Layer 0 written where the criterion applies | ✓ | `TC-R22` (the CSS/constant agreement), `TC-R23` (declared vs painted width), `TC-R25` ×2 scopes (set equality), `TC-R26` (foreign-scope intruders) |
| 4 | RED counterfactual captured **and restored by hash** | ✓ | **11 arms across two runs · 27 RED · 0 failed restores**; both baselines and both post-battery runs **425/425**; every sha256 returned to its pre-mutation value. `mutation-battery-inc4.txt`, `mutation-battery-inc4-supplement.txt` |
| 5 | Inert arms named and **investigated, not excused** | ✓ | `L4` and `L5` diagnosed as **no-op mutations** (framework default; a binding sibling declaration), retired, and replaced by `L4c`/`L5b` which redden 3 and 1. `L4b` is a **pre-registered negative control** whose greenness is the evidence — §4 |
| 6 | Reverse census run on every touched symbol | ✓ | §4 census: **B1 fired** (`test_rail.py`, `test_app.py`), **B4 fired** (`_apply_region_visibility`, `refresh_canvas`, `_chrome_width`); B2, B3 did not fire with their probes recorded. Confirmed by execution: 410 → 425 with **0 pre-existing nodes changing verdict** |
| 7 | The acceptance oracle is itself guarded | ✓ | `AT-R14`, both limbs, plus arm **`L8`** which removes the clip and reddens it alone. Three candidate oracles were measured and two rejected — §4 |
| 8 | Frozen interfaces untouched | ✓ | `IRenderer.render` and `Canvas` absent from the diff; neither file imports either |
| 9 | Coverage claims verified **on disk**, not from intent | ✓ | ledger `425 = 410 − 0 + 15` reconciled against `--collect-only`; every node id in §4 copied from the battery transcripts |
| 10 | Load-bearing emptiness declared with its positive control (C-55) | ✓ | §4 C-55 table — `AT-R14`'s limb (b) absence paired with limb (a)'s non-emptiness requirement, measured at 12 rows |
| 11 | Spec premise executed, not read (C-43) | ✓ | **`A-10`** — `LLR-R04.1` names `MapScreen.CSS`, which does not exist; found by `TC-R22` failing on its first real run. The `hasattr` correction was **also** wrong (C-15 inherited attribute) and is recorded in the docstring |
| 12 | `code-reviewer` passed — a HIGH blocks | ⚠ | **Run, and it BLOCKED on one HIGH.** `increment-004-review.md`. Both blocking conditions discharged by execution in §8 (`L8a`/`L8b` split the clip conjuncts, `TC-R36`+`L5r` make the inert arm live); all three LOW recommendations applied. **Submitted for the whole-branch pass, not self-approved** — the ⚠ stands until that returns clean |
| 13 | Harness lives outside the tree it mutates | ✓ | `battery4.py`, `battery4b.py` and `recover4.py` are under the session scratchpad; the repo holds only the two transcripts. `recover4.py` pins the three pristine sha256 values and verified clean before launch |
| 14 | Mutations described by position, not pasted verbatim (C-56) | ✓ | §4 describes each arm by operation and site; no mangled token or dotted id range appears in this packet |

---

## 8 · Gate discharge (revision 2)

The independent gate returned **BLOCKED** on one HIGH (`increment-004-review.md`). Both blocking
conditions are discharged by execution below, and the three LOW recommendations are applied.
The evidence is `mutation-battery-inc4-supplement-2.txt`.

| # | Sev | Finding | Discharge |
|---|:--:|---|---|
| **F1** | **HIGH** | `AT-R14` did not guard the **column** clip. Its limb (b) intersected `rstrip`ped outside-rows with width-**padded** inside-rows — **0 of 28 rows even eligible to match** — so the limb passed by padding rather than by clipping. And `L8` mutated both clip conjuncts at once, so its single RED was attributable to the row clip alone | `AT-R14` now carries **four limbs**: (a) outside-rows exist, (b) exactly `region.height` rows — the y clip, (c) every row exactly `region.width` wide — **the x clip**, (d) the intersection with **both sides `rstrip`ped**. `L8` split into **`L8a`** (x slice removed → **1 RED, `AT-R14`**) and **`L8b`** (y slice removed → **1 RED, `AT-R14`**). Each conjunct now carries its own arm |
| **F2** | MED | the `L5` "no-op mutation" diagnosis was **false** — `max-height` governs at the wide sizes, not `height: 90%`, and the arm grows the dialog 28 → 40 rows. `L5` was a genuinely **inert arm** | Taken as C-40 instructs — *rewrite the predicate, do not re-argue it*. **`TC-R36`** asserts which declaration governs the dialog's height at each size, and **`L5r`** re-runs the identical mutation: **1 RED, `TC-R36[cap-governs]`**. It also discharges pending item 3's ambiguity |
| `F3` | LOW | `AT-R12`'s membership is substring, and 2 of 27 labels are substrings of others | Documented in its docstring, naming both pairs and pointing at `TC-R25` as the owner of exact `(glyph, label)` equality |
| `F4` | LOW | `TC-R22`'s `__dict__` guard covered `CSS` but not `DEFAULT_CSS` / `CSS_PATH` | All three are checked |
| `F5` | LOW | pending item 1 mis-stated what was left of `A-10`, and cited the wrong requirement | `A-10` was written to §7 (not §6.5) before the review ran. The requirement **body** at `01-requirements.md:188` belongs to `HLR-R04`, and that is what still carried the stale citation |

**The `F1` fix strengthened a node already green on the correct tree, so no other verdict moved.**
That is the expected shape, and it was confirmed rather than assumed.

### What the reviewer measured that this packet had not

The review re-executed `L2`, `L7`, `L8`, `L4b` and `L4c` and reproduced every declared RED set
node-for-node, and independently verified the `L4` no-op diagnosis against
`VerticalScroll.DEFAULT_CSS`. It also re-derived the regression claim **by construction** rather
than by inference — reverting both source edits on an isolated copy, running the pre-existing 410,
then the full 425. That is a stronger proof than this packet's own before/after counts, and the
technique is worth reusing.

---

## 9 · Whole-branch security fixes folded in at the close

The security sign-off returned **CLEAR TO MERGE**, 0 HIGH. Two MEDIUM findings were fixed here
rather than carried, and one was **misattributed in a way only execution could reveal**.

### M1 / M3 — the markup sink class, closed as a class

`M1` found two more sinks passing `markup=False` with **no test asserting it**, proven by a
mutation that reddened nothing. `M3` found a sixth carrying no keyword at all. Counting the earlier
passes, that is **six occurrences of one mechanism across three reviews** — increment 1's `F2`,
increment 2b's `F3`, the increment-3 re-gate's `G1`, and now `M1` (twice) and `M3` — and every time
the response was to arm one more sink by hand.

**Closing instances does not close a class.** `TC-R38` walks the AST of every module under
`mapper/`, collects every `notify` call whose first argument is an **interpolating** f-string, and
requires `markup=False` at each. Seventeen sites; thirteen needed the keyword and got it.

Three properties earn it the name:

- **The site set is derived, never hand-listed** (C-31) — a new sink joins the census the moment it
  is written, which is exactly what six rounds of hand-listing failed to achieve.
- **There is deliberately no exemption list.** An allowlist is itself a hand-listed set that rots,
  and no toast in this application wants markup rendering, so the rule is blanket and the exemption
  set empty. That removes a judgement call that would otherwise need re-making at every new sink.
- **It carries its own vacuity guard** — `scanned >= 15`. A broken AST walk finds zero sites and
  reports a clean census; the floor makes that impossible (C-55's rider — an absence is admissible
  only if the probe can produce a presence).

Counterfactual, executed on a copy outside the repo: dropping the keyword at **one** of the
seventeen sites reddens `TC-R38` and names the exact `file:line`. Ruff unchanged at 29.

### M2 — a real defect, and the review's attribution was wrong

The sign-off reported that `_coerce_field`'s `str(value)` raises on an over-long integer, denying
the map, and proposed guarding it there. **That guard was written, executed, and measured
unreachable.**

CPython caps integer **parsing** as well as formatting, and PyYAML's own constructor calls
`int(token)` — so a sidecar field with more than `sys.get_int_max_str_digits()` digits raises inside
`yaml.safe_load`, **before the coercion ladder runs at all**. The reviewer's probe
(`load() RAISED ValueError`) is consistent with both mechanisms; only running the proposed fix
separated them. That is the flow's own rule about reviewer remedies — *a remedy is a hypothesis, and
a hypothesis is not verified by having been written down* — met for the second time in this batch.

**And the correct fix is narrower than the one requested.** Treating an unparseable sidecar as
absent would open the map with every ficha blank, and `MapStore.save` would then write that back
over the operator's real data. One unparseable field denying a map is `F-M5`'s shape, fenced out of
this batch. So the refusal **stays**; what changed is that it is now typed, Spanish and names the
file — `MapStoreError`, with its `ValueError` cause preserved — instead of escaping untyped.
`TC-R37` asserts exactly that, with a discriminating negative one digit under the limit that loads
normally, so the refusal is attributable to the length rather than to a malformed fixture.

### Carried knowingly, not fixed

| # | Finding | Disposition |
|---|---|---|
| `M4` | `MAX_RENDER_NODES = 12000` admits ~50 s of frozen UI; render cost is O(n²), measured | **Accepted.** It is a *net improvement* — `master` has no cap at all and is ~1.4× slower per node. Lowering it is a UX judgement about a pathological local file, not a defect in this batch. Backlog |
| `M5` | `-m 'not slow'` deselects this batch's own depth acceptance and no CI lane exists | **Run manually as a merge step**, and it is green: `16 passed, 409 deselected`. The two-lane CI workflow goes to the backlog |
| `L1` | `.env` not gitignored | **Fixed** — `.env`, `.env.*`, plus `scratch/` and `out.txt` |
| `L2` | operator identity and a session UUID inside the `.dev-flow/**` battery transcripts | **Accepted for a private repo**, and flagged in the backlog as a blocker for any public push |
| `L4` | `_text_attributes()` recomputed once per node | Backlog — the same nit as increment 3's declined `F7` |
| `L5` | `_pop_snapshot` unguarded against the batch's new raises | Backlog. Unreachable today — snapshots are built from an acyclic in-memory graph — but it is the one `save` site whose safety now rests on an invariant this batch made load-bearing |

### An observed flake, recorded rather than shrugged off

`test_at_r16b_the_factory_screen_survives_a_depth_5000_map_composed` **failed once**, in a
post-battery suite run immediately after three mutation arms had driven three full suites back to
back. It passes in isolation (1 passed, 20.4 s) and in clean full runs (429 passed, twice). It is
therefore **load-sensitive, not regressed** — but a depth-5000 node whose verdict depends on ambient
machine state is a weak gate, and per `M5` it runs only in the manual slow lane. Backlog.

### Final numbers after the fold

| | |
|---|---|
| Suite, both lanes | **429 passed, exit 0** (118.1 s) |
| Ruff `mapper tests` | **29** — unchanged |
| Ledger | `429 = 425 − 0 + 4` — `TC-R36` (×2 sizes), `TC-R37`, `TC-R38` |
| Source files touched at the close | `mapper/app.py`, `mapper/screens/factory.py`, `mapper/store.py` |

**Source-file count for this increment is now 5** — `app.py` and `help.py` for the two defects,
plus `app.py`/`factory.py`/`store.py` for the security fold. That exceeds the ≤4 budget, and the
reason is declared rather than hidden: the fold is a **merge-gate response over the whole branch**,
not increment-4 scope creep. Cutting it into a sixth increment would have meant opening the same
three files again for the same findings.
