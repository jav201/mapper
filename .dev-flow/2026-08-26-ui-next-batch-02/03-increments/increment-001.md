# Increment 001 — S-6 · `HLR-CNV.1` · `LLR-COERCE.1` — paleta v2, the Canvas A3, and the coercion list

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Increment | `001` |
| Lane | none — the batch is serial (ARQ measured 0 of 21 pairs parallelisable) |
| Requirement(s) | `HLR-S06.1`, `HLR-S06.2`, `HLR-S06.3` with `LLR-S06.3.1` through `LLR-S06.3.5` · `HLR-CNV.1` with `LLR-CNV.1.1` through `LLR-CNV.1.4` · `HLR-CNV.2` with `LLR-CNV.2.1` · `HLR-COERCE` / `LLR-COERCE.1` |
| Acceptance | `AT-003`, `AT-004`, `AT-005`, `AT-006`, `AT-007`, `AT-007b`, `AT-008`, `AT-009` |
| Agent | `software-dev` (supervised-incremental-development) |
| Date | 2026-08-28 |
| Base | `5d8ee0d` on `feat/ui-next-batch-02` |

---

## 1 · What changed

**The braille edges and pill backgrounds `RadialRenderer` has been drawing all along now reach the
screen and the exported SVG, the palette gained five tokens with declared jobs and a census that
fails if any of them acquires a second, and one declared list of code points is coerced out of every
painted string.** Pre-state, executed at `5d8ee0d`: a radial map painted **0** characters in
`U+2800`–`U+28FF` while the renderer was writing 267 dots per legacy render that `Canvas.rows()`
silently discarded.

Mechanism, in the order the dependencies run:

- **`Canvas` declares `dots` and `bgs`** and `rows()` composes four layers in a declared precedence —
  an explicit cell outranks a wire, a wire outranks a braille dot, a `bgs` background applies to
  whichever glyph won, and a cell that declares its own background keeps it. Sub-cell dot
  coordinates fold to a cell and a braille bit; anything landing outside the canvas is dropped.
  `RadialRenderer`'s two instance monkey-patches are deleted and asserted gone.
- **The layer tone is guarded in `rows()`** — the one place all four layers converge, which is what a
  write-time setter would miss, because `radial.py` assigns `cv.dots[...] = hue` directly. A value
  outside the declared token set paints a declared fallback instead of failing open. The token set is
  **injected at construction**, not imported: `docs/ARCHITECTURE.md:120` declares `canvas` with
  `Depends on: —`, and that row stays true (§6, A-81).
- **Five tokens land in `darkside.py`** with their jobs in the module docstring: `SAGE`, `TEAL`,
  `VIOLET`, plus `ASH` (`#D10`'s promotion of the undeclared `#a3a3a3` that shipped inside
  `radial.py`'s `_GREYS`) and `PULSE` (the busy job `#D10` requires). `mapper/app.py:879`'s loading
  spinner retones off the severity hue.
- **`COERCION_RANGES` is declared once** and `_CONTROL_MAP` is derived from it, widening `plain()`
  from **63 to 235** covered code points — exactly Unicode's `Cc`, `Cf`, `Zl` and `Zp` classes minus
  the two declared preservations `U+0009` and `U+000A`. The class-derived form replaced a
  hand-picked one during review; see §8.
- **`darkside.time_row` coerces its own inputs**, because the repo screen feeds it a git branch name
  and a commit subject — the widest input surface in the product, authored by anyone who has landed
  a commit in a repository the operator opens.
- **The user-reachable surface**: the map canvas repainted on the real `r` key
  (`map 'r' -> toggle_radial`), and `export.save_svg`'s written file.

---

## 2 · Files modified

| File | Kind | Change |
|---|---|---|
| `mapper/canvas.py` | source | `dots`/`bgs` declared; `_braille()` fold; `_tone()` guard; `rows()` composes four layers |
| `mapper/darkside.py` | source | 5 tokens + jobs docstring; `tokens()`, `tone_set()`, `semantic_tokens()`, `SURFACES`; `COERCION_RANGES` and the derived `_CONTROL_MAP` |
| `mapper/views/radial.py` | source | monkey-patches deleted; tone policy passed; `ASH` consumed; title coerced before slicing |
| `mapper/app.py` | source | one line — the loading rung retones to `PULSE` |
| `tests/test_canvas.py` | test | **new** — 30 nodes |
| `tests/test_darkside_census.py` | test | **new** — 20 nodes |
| `tests/test_radial.py` | test | +4 nodes (`AT-007b` and its arms) |
| `tests/test_export.py` | test | +3 nodes (`AT-009` and its controls) |
| `tests/test_repair_depth.py` | test | 4 predicted-red digests re-baselined, with the reason recorded in-file |
| `docs/ARCHITECTURE.md` | doc | the `Canvas dots/bgs` row moves from `COMMITTED, NOT PRESENT` to `PRESENT` |
| `.dev-flow/.../01-requirements.md` | doc | amendment set 4, `A-77` through `A-83` |

| Count | Value |
|---|---|
| **SOURCE files** | **4 / 4** ⚠ |
| Test files | 5 (uncapped) |
| Doc files | 2 (outside the count) |

⚠ **At exactly 4 source files, which is the number §5.4 declares for this increment.** It cannot be
cut smaller: `LLR-COERCE.1` widens `plain()`, which `LLR-CNV.1.4`'s token set and `LLR-CNV.2.1`'s
SVG threshold both quantify over; `HLR-CNV.1` is unobservable until `radial.py` stops monkey-patching
the layers it writes; and `#D10`'s two dispositions land in `darkside.py` and `app.py` respectively.
Splitting would ship a census asserting against a list no increment had created — the exact defect
`HLR-COERCE` was promoted to a requirement to prevent.

---

## 3 · How to test

```bash
cd C:/Users/jjgh8/Github/mapper
set PYTHONUTF8=1
python -m pytest -q                    # fast lane
python -m pytest -q -m slow            # slow lane
python -m ruff check mapper/ tests/
python -m ruff check fixtures/
python -m pytest tests/test_canvas.py tests/test_darkside_census.py -q
```

---

## 4 · Test results

**One complete run per lane; the counts below are read from those runs' own output.**

| Lane | Result (post-review-fix, the run this packet is signed against) |
|---|---|
| fast | `691 passed, 17 deselected in 62.85s` — exit 0 |
| slow | `17 passed, 691 deselected in 23.48s` — exit 0 |
| ruff `mapper/ tests/` | **28** errors (baseline **29**) |
| ruff `fixtures/` | `All checks passed!` |

| Layer | Nodes | Result |
|---|---|---|
| **0 · unit** — `Canvas._braille`/`_tone`/`rows` (branching, and they cross a declared module boundary); `darkside.plain`, `tokens` | `tests/test_canvas.py` (30), `tests/test_darkside_census.py` coercion nodes | 30 + 6 passed |
| **A · white-box** `TC` ↔ LLR | the `test_tc_cnv_*`, `test_llr_s06_*`, `test_llr_coerce_*` nodes | all passed |
| **B · black-box** `AT` ↔ story | `AT-003`, `AT-004`, `AT-005`, `AT-006` (census over the shipped tree) · `AT-007`, `AT-008` (`rows()`) · `AT-007b` (`RadialRenderer` at 80 × 24) · `AT-009` (the written SVG) | all passed |

**Ruff reconciled rather than accepted.** 29 → 28 is **−1 and zero new**: the removed error is
`tests/test_export.py`'s pre-existing unused `Path` import, which `_disk_braille`'s annotation now
consumes. `mapper/darkside.py`'s two errors (`F401 timedelta`, `F841 running`) were verified
byte-identical at `5d8ee0d`. All eight other touched files: `All checks passed!`

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Where it ran | a **detached copy** of the tree in the session scratchpad — never the repo, so no concurrent reader was contaminated |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` on every run (C-46) |
| Arms resolved at baseline | **145**, asserted before any verdict was trusted, and asserted all-green first |
| Verdict granularity | **per resolved node id**; the process exit code is never read |
| Restore proven by | **sha256 back to the pre-mutation value** on all five mutated files, after every single mutant |
| Post-battery control | full re-run `145/145 green` at the end of each round |

| Mutant (described by operation, never by pasted token) | Verdict | Arms |
|---|---|---:|
| `M-CNV.2-a` compose dots at the **wrong precedence**, so braille overwrites the node cards | **RED** | 7 |
| `M-CNV.2-b` draw braille only where the cell was already blank | **GREEN — correctly benign** | 0 |
| `M-PRECEDENCE-BG` a cell's own background stops outranking the `bgs` layer | **RED** | 5 |
| `M-TONE` delete the tone guard; the layer value passes straight through | **RED** | 10 |
| `M-BOUNDS` delete the out-of-bounds dot guard | **RED** | 1 |
| `M-SPAN` append every cell through an explicit empty style | **GREEN — proven equivalent** | 0 |
| `M-COERCE.1-a` build the map from the shipped ranges instead of the declared list | **RED** | 4 |
| `M-COERCE.1-b` declare the range list a second time in a test module | **RED** | 1 |
| `M-COERCE.1-c` drop the carriage-return code point from the C0 range | **RED** | 2 |
| `M-S06.3.5-a` give both severity tokens the single shared job *"severity"* | **RED** | 1 |
| `M-WARNJOB` restore the *in flight* limb to `WARN`'s declared job | **RED** | 1 |
| `M-TITLE` stop coercing the radial title before slicing | **RED** | 1 |
| `M-HEX` alter one v2 token's hex | **RED** | 4 |
| `M-PULSE` retone the busy site back to the severity hue | **RED** | 1 |

**Arms that stayed GREEN, named rather than left in a transcript: `M-CNV.2-b` and `M-SPAN`, and
both are accounted for.** `M-CNV.2-b` is the mutant §3.3's own table requires to pass — braille is
*added*, nothing is lost, and that is not a defect. `M-SPAN` was **inert for a reason worth
recording**: the first version of `rows()` carried a defensive branch whose comment claimed
`Text.append(ch, "")` records a span while `Text.append(ch)` does not. **Measured — it is false.**
Rich tests `if style:`, so no-style, empty-string and `None` are indistinguishable. The branch was
dead weight and the comment asserted something untrue; both are gone, and `M-SPAN` is now inert
*because the two implementations are genuinely equivalent*, which is the honest reason.

**Three mutants reported NOT APPLIED before they reported anything else, and that is the harness
working.** Two byte patterns used bare line feeds against a **CRLF** tree (406 CRLF, 0 bare LF in
`darkside.py`) and one targeted a block whose exact bytes differed. A mutation that never ran is
textually indistinguishable from one that ran and changed nothing; only the substitution-count
assertion separates them, and here it did so three times.

### Load-bearing emptiness (C-55)

| Field | Value |
|---|---|
| Does a claim rest on the tree holding NO instance of some case? | **Yes, two — and one was live** |
| **(1) The out-of-bounds guard** | It was a **no-op**: `rows()` only ever *looks up* in-range cells, so an out-of-range entry left in the folded mask is never painted and no assertion over painted output can separate the two implementations. `M-BOUNDS` reddened **nothing** in round 1. Discharged by giving the guard its own observable — asserting on `_braille()`'s returned mask directly — after which `M-BOUNDS` reddens. |
| **(2) The undeclared-hue clause** | *"the hue set equals the declared token set"* is satisfied by an **empty** difference today only because `ASH` closed the one undeclared hue. Guarded by asserting the derived hue set is **non-empty** before comparing, and by the register's totality clause. |
| Positive control for every absence-returning probe | The monkey-patch census asserts its regex matches two synthetic positives and rejects a near-miss before reporting zero offenders; the bounds test asserts a **known-present** in-range dot survives the same unmodified fold; `AT-009`'s zero-braille reading is admissible only because the sibling control shows the same oracle producing a non-zero count on the radial artifact. |
| Conjunctive criteria | `HLR-CNV.2` is a conjunction — *count > 0* **and** *containment*. One mutation per conjunct: `M-CNV.2-a` reddens the containment limb while leaving *count > 0* green, which is precisely why the second limb exists. |

### Reverse census — trigger family B

| Probe | Result |
|---|---|
| **B1** — symbols asserted by other requirements' tests | `Canvas` appears in **12** test files, `.rows(` in 4, `.dots` in 3. Every one re-validated: the full suite is green and the only intentional movement is the four digests below. |
| **B2** — file moved on disk | **NOT FIRED.** No file changed location; `git status` shows 9 modified and 4 added, 0 renamed. |
| **B3** — byte-identical golden captures a touched source | **FIRED.** `MASTER_LEGACY_DIGESTS` (`tests/test_repair_depth.py`) pins 3 renderers × 4 sizes. Derived prediction *before* the change: all 4 `RadialRenderer` keys red, all 8 `Layered`/`Outline` keys green. **Measured after: exactly that.** Re-baselined one key at a time with the reason recorded in-file; no predicted-green digest was recaptured. Independently corroborated by the repair batch's pre-placed guard `test_at_p06_radial_is_pinned_at_every_size_so_the_feature_batch_reddens_four`, which passes. |
| **B4** — artifact consumed elsewhere | **FIRED.** `rows()`'s bytes are consumed by `export.save_svg`. Asserted on the **written file** by `AT-009`, not merely permitted. |
| **A3** — interface consumed by another module changed | **FIRED (the second, `Canvas`, per `#D9`/R-016).** `Canvas.__init__` gains two defaulted parameters — additive and widening. Every construction site left unset keeps today's behaviour byte-for-byte, which the 8 held digests prove. `docs/ARCHITECTURE.md` §4 updated to `PRESENT`. |

### Signed-balance test ledger

`post = base − deleted + added` → **`691 = 630 − 0 + 61`** ✓ reconciles.

Per-file, measured by `--collect-only`, not counted by hand:

| File | Collected | Added |
|---|---:|---:|
| `tests/test_canvas.py` (new) | 32 | +32 |
| `tests/test_darkside_census.py` (new) | 21 | +21 |
| `tests/test_radial.py` | 5 | +4 |
| `tests/test_export.py` | 4 | +3 |
| `tests/test_darkside.py` | 17 | +1 |
| | | **+61** |

Slow lane unchanged at 17; total collected **708**. Six of the 61 were added by the review
response: four in `test_canvas.py`, one in `test_darkside_census.py`, one in `test_darkside.py`.

---

## 5 · Risks

1. **`PULSE` sits 25.06 CIEDE2000 from `ALERT`** — closer than `WARN` does at 45.36. Judged
   sufficient on a lightness separation of 0.50 vs 0.27, but it is the ruling's main perceptual risk
   and it is owed a read at 118 × 34 before the batch closes (`B-42`).
2. **The ux lens dissented on the whole approach** and would have spent no hue at all. Its ladder was
   not adopted because it declines `#D10`'s *"assign the job"* clause (an A3 re-open) and because its
   `PENDING` rung measures 3.95:1, which sealed `#D28` forbids. If the operator prefers that reading,
   it is a PDR question, not a Phase-3 one.
3. **`WARN` was narrowed**, which is a behaviour change to a shipped token's contract. Two sites were
   affected and both are handled: one retoned, one registered. A third site appearing later reddens
   the census rather than passing silently.
4. **The tone guard's fallback can mask a typo.** A tone that is a legitimate-looking hex but not a
   declared token now paints `MUT` rather than that hex. This is the intended trade — failing open
   was the defect — but it means a mistyped token degrades quietly rather than loudly.
5. **`Inc-2` changes the signature of every function on the `AT-007`/`AT-009` chain** under a
   byte-identity gate that compares a renderer against itself. A byte-identity gate cannot see a
   chain that was already broken. `AT-007` and `AT-009` are therefore re-run obligations for `Inc-2`,
   which must not close with either red.

---

## 6 · Pending items / spec deviations

| id | Item |
|---|---|
| `A-77` | `#D10`'s busy-token disposition contradicted itself inside one LLR; the NEW-TOKEN reading was ruled to govern, with `ASH` and `PULSE` named and measured. Both lens verdicts are landed at `02i-inc1-busy-token-architect.md` and `02i-inc1-busy-token-ux.md`. |
| `A-78` | `WARN` loses *"or in flight"* — **this was a gate blocker**: `LLR-S06.3.5`'s own *"sites classifying as both `== 0`"* threshold was unsatisfiable by any implementation while the clause stood. |
| `A-79` | The exception register is **2** after Inc-1, not the 1 the threshold names. |
| `A-80` | `COERCION_RANGES`' C0 row was **incomplete** — it omits `U+000D`, 29 points where its own label implies 30. Adopting it verbatim NARROWED shipped coverage. |
| `A-81` | The tone set is injected, not imported, because the module map declares `canvas` with no dependencies. |
| `A-82` | *"semantic token pairs"* is now decidable via `SURFACES`; the addendum's 13.99 and 20.18 both reproduce exactly. |
| `B-38` | `views/lane.py:67` paints a running step in `WARN` — registered, **closed by Inc-5**. |
| `B-39` | `screens/factory.py`'s `.factory-tag` blue — registered, **closed by Inc-9**. |
| `B-40` | The loading ladder's PENDING rung is 1.65:1 on `PANEL`, below the 3:1 non-text floor — a three-state indicator ships as two-state. Out of `#D10`'s scope. |
| `B-41` | `MUT`/`WORDMARK` and `ASH`/`PULSE` each collapse at the 16-colour rung. Declared limits; not auto-reachable. |
| `B-42` | `PULSE`/`ALERT` at 25.06 owes a perceptual read at the declared context of use. |
| V-5 | Test-path reconciliation: the census landed in `tests/test_darkside_census.py`, not `tests/test_darkside.py` as the provisional `Executed verification` lines say. |

---

## 7 · Suggested next task

**`Inc-2` — `ViewState` + the `IRenderer` A3, signature only, behaviour-neutral.** It is the batch's
declared 6-source-file breach and the only increment that touches all four renderers at once. It
carries `Inc-1`'s standing re-run obligation: `AT-007` and `AT-009` must both be green at its close,
because a byte-identity gate comparing a renderer against itself cannot see a chain that was already
broken. `HLR-CNV.3` (focus-aware selection, carry `B-05`) rides with it, since `ViewState.focus_owner`
is the field it needs.

---

## 8 · Review response — both gates, every finding dispositioned

`code-reviewer` returned **BLOCK** on one HIGH. `security-reviewer` returned **sign-off for Inc-1**
with one MEDIUM gated before merge, and raised two HIGHs that are **outside this increment's change
set**. Verdicts at `increment-001-code-review.md` and `increment-001-security-review.md`.

**A HIGH is never self-cleared**, so every fix below was re-run through the mutation battery to
prove the remedy itself goes RED (rounds 4 and 5), and a confirmation review pass runs over the
post-fix tree.

| Finding | Sev | Disposition |
|---|---|---|
| **CR-F1** composing a background onto a **theme name** destroys the foreground | HIGH | **FIXED.** Verified independently before fixing: `get_style("frame")` resolves a colour, `get_style("frame on …")` returns `color=None`. Replaced with a `_COMPOSABLE` allowlist; a name or an existing background now keeps what it had. `"frame"` is the default of `wire`, `edge` and `elbow_down`, so the reviewer is right that the module hands itself the defective input. New arm added; battery round 5 reddens 2 arms on revert |
| **CR-F7** the background check was case-sensitive | LOW | **FIXED, then the fix itself DELETED.** Round 4 measured the case-insensitive `_HAS_BG` **INERT** — the allowlist already rejects any form of `on`, so the check could not change an outcome. Removed rather than kept |
| **CR-F2** two ARCHITECTURE rows describe one constructor | MED | **FIXED** at `docs/ARCHITECTURE.md:68`. The reviewer also found that `test_repair_map_truth.py` pins that row as **prose** and imports nothing, so it can never observe `Canvas.__init__` — carried as `B-44` |
| **CR-F4 / SEC-F7** the injected tone policy has no enforcement | MED / LOW | **FIXED.** Both reviewers asked for the same guard independently. The monkey-patch census banned whole-attribute assignment but not the **subscript** write, which is the form the real writers use. New derived census; reverting `radial.py`'s policy reddens it |
| **CR-F5** three register rows contradict the jobs the palette declares | MED | **FIXED IN TWO STAGES, and it overturned one of my own amendments.** `lane.py:67`'s branch is `if state == "pending"` — CI *pending* is `WARN`'s job verbatim; **I mis-judged it by reading its label (`" run"`) instead of its condition**, so `A-79` was wrong and is corrected by `A-86`. The first pass registered three sites and **missed two more of the same shape**, which the confirmation pass found: `lane.py`'s third behind-slot (in `_mini_timeline`, and worse than its siblings — it paints one `ALERT` block even when behind is 0) and `"sin acta"` painted `ALERT` in one file and `WARN` in another with **both rows conforming**. Register is now **6** |
| **CR-F6** `TOKEN_JOB` was a second hand-typed copy of the jobs | MED | **FIXED IN TWO STAGES.** The parser landed first, but the *totality* did not: the claim still quantified over the 4 adjudicated tokens while `darkside.py` asserts the one-job rule over all **14**, so the confirmation pass's `M-C` — two non-adjudicated tokens given one job in the product — was **GREEN**. Now `test_at_003_no_two_tokens_declare_the_same_job` quantifies over all 14, and `M-C` reddens |
| **CR-F3** the blue census covers 8 of 50 sites | MED | **NOT widened — and the name was fixed instead.** `LLR-S06.3.3`'s own Touched-symbols line enumerates the eight literal sites and quantifies over those, so the implementation matches its requirement; the gap is in the **requirement**. Test renamed to `…no_blue_LITERAL_ships…` with the scope stated. Carried as `B-43` |
| **CR-F8** the dot tie-break was undeclared | LOW | **DECLARED** in `_braille`'s docstring. Round 5: inverting it reddens a digest, so it was pinned all along — undeclared, not unguarded |
| **CR-F9** the packet said 62 covered code points | LOW | **FIXED** — 63, and now 235 |
| **CR-F10** the sweep used a non-recursive glob and a floor | LOW | **FIXED** — `rglob`, a set comparison against the tracked files, and a **value** sweep as well as a name sweep |
| **CR-F11** `HEX` could not see an 8-digit colour | LOW | ~~FIXED~~ → **NOT discharged at the first attempt; corrected at the confirmation pass.** Swapping `\b` for a negative lookahead repaired **nothing** — both forms fail on an alpha-suffixed literal for the same reason, because the 7th character *is* a hex digit. The prescribed regex was wrong and I applied it faithfully instead of executing it. Now `{6}(?:{2})?` plus the control the finding asked for |
| **SEC-F3** `AT-009`'s oracle validated the list against itself | MED, gated pre-merge | **FIXED, and it is the most important fix here.** `banned` came from the same constant `_CONTROL_MAP` comes from, so `leaked == []` held **for any value of `COERCION_RANGES`**. Replaced by an oracle keyed on `unicodedata` — something this project does not write. Round 4 proves it: clipping a declared range now reddens `AT-009`, which was impossible before |
| **SEC-F4** the list was under-inclusive by 150 `Cf` points | MED | **FIXED by widening to the classes.** `COERCION_RANGES` is now exactly `Cc ∪ Cf ∪ Zl ∪ Zp` minus two declared preservations — 235 points, up from 85. The `U+E0020` TAG block is the reason it matters: those render as nothing, map 1:1 onto ASCII, and reached the exported SVG as a payload invisible to the operator. A new test re-derives the list from `unicodedata` and asserts equality **in both directions** |
| **SEC-F5** git commit subject/author painted uncoerced | MED | **FIXED inside `time_row`**, not at the call site, so the next caller cannot forget — the shape `hint_line` and `fit` already use. New guard with a positive control; round 4 reddens on revert |
| **SEC-F6** the tone policy's own default reproduced the fail-open | LOW | **FIXED.** `Canvas` now refuses `tones=` without `fallback=`. Prevention with no detection is not a control |
| **SEC-F8** the two truncators disagree on cells vs code points | LOW | **CARRIED** as `B-45`. Out of Inc-1's scope |
| **SEC-F1** `_ConfirmScreen` renders a ficha title through a **markup-parsing** sink on the archive confirmation | HIGH | **NOT Inc-1's.** Predates the branch; Inc-1's only `app.py` change is one style argument. A stray closing tag raises `MarkupError` while composing the dialog that gates subtree archival, and `[@click=…]` injects a live action span. **Batch-close blocker**, needs an id and an owning increment — surfaced to the operator |
| **SEC-F2** `views/outline.py` and `views/lane.py` are uncoerced, and **outline feeds `save_svg`** | HIGH | **NOT Inc-1's, and it is a scope gap in the sealed spec.** `LLR-COERCE.2` is scoped verbatim to `views/layered.py::_fit`; outline and lane belong to **no increment**. Measured: a hostile title through outline or layered produces an SVG that is **not well-formed XML**. `AT-009`'s guarantee holds only in radial view, and **layered is the default renderer**. **Batch-close blocker** — surfaced to the operator |

### Battery rounds 4 and 5 — the remedies are themselves falsifiable

| Reverted remedy | Verdict | Arms |
|---|---|---:|
| `CR-F1` — compose onto a theme name again | **RED** | 2 |
| `SEC-F6` — accept a policy with no fallback | **RED** | 1 |
| `CR-F8` — invert the dot tie-break | **RED** | 1 |
| `SEC-F4` — drop the TAG block from the list | **RED** | 1 |
| `SEC-F4` — clip the invisible operators back by four | **RED** | 2 (incl. `AT-009`) |
| `SEC-F5` — `time_row` stops coercing | **RED** | 1 |
| `CR-F6` — give two tokens one job **in the product** | **RED** | 1 |
| `CR-F4` — a view writes a layer with no policy | **RED** | 1 |
| `CR-F7` — make the background check case-sensitive | **GREEN — INERT** | 0 |

Baseline 151 arms, all green before any verdict was trusted; sha256 restore verified on six files
after every mutant; `151/151` green after each round. **The one inert result was acted on**: it is
why `_HAS_BG` no longer exists.

**Two mutations reported NOT APPLIED before reporting anything else, for the third and fourth time
in this increment** — `canvas.py` is LF and `darkside.py` is CRLF, and a pattern written for one
matches nothing in the other. The harness now normalises the ending rather than hand-picking it.
Every occurrence was caught by the substitution-count assertion, never by noticing a suspicious
result.

---

## 9 · Confirmation pass — the HIGH is discharged, and it found a defect in the remedy

`code-reviewer` re-ran independently over the post-fix tree: **"OK with the listed fixes applied
first — the HIGH is discharged, no HIGH survives."** It re-derived every number from an archived
`5d8ee0d` rather than reading them here, executed seven mutations of its own in a detached copy, and
returned **0 HIGH · 7 MEDIUM · 6 LOW**. Verdict at `increment-001-code-review-confirmation.md`.

### The finding that matters most is against me, and it is recorded verbatim

**`N-1` — the comment justifying the HIGH's remedy contained a fabricated measurement.** It read
*"Measured on rich 15.0.0: `get_style("frame")` → colour `#262626`."* That figure came from a probe
that had **constructed `Console(theme=Theme({"frame": "#262626"}))` and then observed it.** I built
the world I was claiming to measure.

Re-measured on a plain `Console`, which is what `export.save_svg` actually uses:

```
'frame'             -> color=None  bg=None       frame=True
'frame on #121212'  -> color=None  bg=#121212    frame=True
'frame' in rich DEFAULT_STYLES: False       literal "frame" in textual 8.2.8: 0 hits
```

**So the HIGH does not reproduce in this tree.** `frame` is the ECMA-48 attribute and carries no
colour; the pre-fix composition lost nothing and *added* the background. The guard is kept — both
reviewers want it, `views/layered.py` already computes `"frame"` as an edge tone, and `Inc-2` routes
all four renderers through here — but it is **forward-looking, not a repair**, and the comment now
says so, including what the earlier claim got wrong.

In an increment whose central argument is *"an oracle built from the list can never detect that the
list is short"*, writing a self-supplied oracle into production source and labelling it *measured*
is the same defect in the same increment. It is the one finding here I would not have caught alone.

### Dispositions

| Finding | Fix |
|---|---|
| **N-1** fabricated measurement in production source | **FIXED** — both the source comment and the test docstring now state what a plain `Console` returns, and that the guard is forward-looking |
| **N-2** the published contract was still unqualified | **FIXED** in `canvas.py`'s class docstring and `docs/ARCHITECTURE.md:160`; the over-claiming test renamed to `…_a_background_reaches_a_composable_winner` |
| **N-3** `CR-F11` reported FIXED while unchanged | **FIXED** — `HEX` now matches 6 **or** 8 digits, with the control the original finding asked for |
| **N-4** the third behind-slot still CONFORMING | **FIXED** — registered, `Inc-5` |
| **N-5** `"sin acta"` in two severity tokens, both conforming | **FIXED** — registered, `Inc-7` |
| **N-6** the layer-write census is file-granular | **DECLARED**, with its two limits written into the docstring; the receiver-bound form carried as `B-48` |
| **N-7** the one-job claim covered 4 of 14 tokens | **FIXED** — now quantified over all 14; the reviewer's `M-C` reddens |
| **N-8** the parser over-captured its last token | **FIXED** — terminates on a column-0 line as well |
| **N-9** the file contradicted itself about `lane.py:67` | **FIXED** — the docstring no longer names it as in-flight work |
| **N-10** the background drop is silent | **DECLARED** in the class docstring |
| **N-11** `ruff check fixtures/` inspects nothing | **CONCEDED** — `fixtures/` holds no `.py` file, so it passes vacuously. Kept in §3 only as a *tree-cleanliness* check and labelled; the property that matters is `git status --short -- fixtures/` empty, which holds |
| **N-12** the Unicode equality is version-pinned | **DECLARED** — a Unicode upgrade reddens it deliberately; re-derive, do not widen the oracle |
| **N-13** ZWJ/ZWNJ coerced, breaking emoji and Persian/Indic text | **CARRIED** as `B-49`. Note it predates the widening: those entered with the 85-point list, not with `A-84` |

### Battery round 6 — the confirmation remedies are falsifiable too

| Reverted remedy | Verdict | Arms |
|---|---|---:|
| `M-C` — two tokens given one job **in the product**, neither adjudicated | **RED** | 1 |
| `N-8` — parser terminates at end-of-docstring again | **RED** | 1 |
| `N-3` — `HEX` blind to an alpha-suffixed literal again | **RED** | 1 |
| `N-4` — the third behind-slot back to CONFORMING | **RED** | 2 |

Baseline 154 arms, all green first; sha256 restore verified on **eight** files after every mutant;
`154/154` green after the round. `M-C` was **GREEN** before this round and is RED after, which is
the whole point of running the reviewer's own mutation rather than trusting the fix.

One first attempt was rejected by its own test: a `len(job) < 120` bound intended to catch the
over-capture **false-failed `ASH`**, whose real job is 162 characters across three wrapped lines. A
length bound is a proxy; the oracle is now the trailing paragraph's own text. A rule that
false-fails correct work costs as much as one that passes wrong work.

**Final state:** fast `694 passed, 17 deselected`; slow `17 passed`; ruff **28**; ledger
`694 = 630 − 0 + 64`.

---

## Increment gate checklist

| # | Item | ✓ | Evidence |
|---|---|---|---|
| 1 | ≤4 source files, or reason declared | ✓ | 4/4, reason in §2 |
| 2 | Tests written in this same increment | ✓ | 5 test files, +55 nodes |
| 3 | Layer 0 written where the criterion applies | ✓ | `tests/test_canvas.py` — `_braille`, `_tone`, `rows` all branch and cross a declared boundary |
| 4 | RED counterfactual captured **and restored by hash** | ✓ | 14 mutants, 12 RED; sha256 restore verified on 5 files after every mutant; `145/145` post-battery |
| 5 | Reverse census run on every touched symbol | ✓ | §4, B1–B4 and A3, non-firing recorded with its probe |
| 6 | `code-reviewer` passed — a HIGH blocks | ✓ | BLOCK on 1 HIGH → fixed → **confirmation pass: "the HIGH is discharged, no HIGH survives"**, 0 HIGH remaining. A HIGH was never self-cleared |
| 7 | No file from another lane touched | ✓ | batch is serial; no lanes |
| 8 | Frozen interfaces untouched, or authorised | ✓ | the `Canvas` A3 is `#D9`/R-016, PDR-approved; `IRenderer.render` untouched — that is `Inc-2` |
| 9 | Coverage claims verified **on disk** | ✓ | every node named here was run; counts read from the runs' own output |
| 10 | Load-bearing emptiness declared, with its synthetic instance | ✓ | §4 — two found, one was live and is discharged |
| 11 | Mutation verdicts recorded **per arm**, inert arms named | ✓ | §4 table; `M-CNV.2-b` and `M-SPAN` named and explained |
