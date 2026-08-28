# Code Review — Increment 001, CONFIRMATION PASS over the post-fix tree

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Increment | `001` |
| Base | `5d8ee0d` on `feat/ui-next-batch-02` |
| Reviewer | `code-reviewer` (independent confirmation; every disposition re-executed, none accepted) |
| Date | 2026-08-28 |
| Environment | Python 3.12 · rich 15.0.0 · textual 8.2.8 · Windows · `PYTHONUTF8=1` |
| **Verdict** | **OK with the listed fixes applied first — the HIGH is discharged, no HIGH survives** |

---

## 0 · Rules of engagement, honoured

No file under `mapper/`, `tests/` or `docs/` was modified. No mutating git command was run
(`git status --short` is byte-for-byte identical before and after this pass). Every mutation ran in a
detached copy at `…/scratchpad/probe`, with `PYTHONDONTWRITEBYTECODE=1`, restored via
`git checkout --` in that copy and confirmed clean after each. The `5d8ee0d` baseline was extracted
with `git archive` into `…/scratchpad/base`, never a worktree in the repo. No live `MapperApp` was
started and `fixtures/` was never opened by anything but `pytest`'s own tracked reads —
`git status` shows `fixtures/` unmodified.

## 1 · Baseline and current state — REPRODUCED, all six numbers

| Claim | Measured here | |
|---|---|---|
| `5d8ee0d` fast lane | `630 passed, 17 deselected` | ✓ |
| `5d8ee0d` ruff `mapper/ tests/` | `Found 29 errors` | ✓ |
| current fast lane | `691 passed, 17 deselected in 54.86s` | ✓ |
| current slow lane | `17 passed, 691 deselected in 23.84s` | ✓ |
| current ruff `mapper/ tests/` | `Found 28 errors` | ✓ |
| ledger `691 = 630 − 0 + 61` | canvas **32**, census **21**, radial **5**, export **4**, darkside **17** by `--collect-only`; `32+21+4+3+1 = 61` | ✓ exact |

`ruff check fixtures/` — see **N-11**; it passes because it inspects nothing.

---

## 2 · The seven items, one by one

### Item 1 · CR-F1 (the HIGH) — **PARTIALLY DISCHARGED**
**The code change is discharged and falsifiable. Its stated justification is a false measurement,
and the published contract it was raised to protect is still unqualified.**

**What holds.** `_COMPOSABLE` (`mapper/canvas.py:50-52`) is consumed at `:173`, and every arm you
asked about behaves as declared. Executed against the live allowlist:

```
composable=1  ''                         composable=0  'frame'
composable=1  '#1783ff'                  composable=0  'bold #000000 on #1783ff'
composable=1  'bold #1783ff'             composable=0  'ON #1783ff'
composable=1  'italic underline reverse' composable=0  'red' / 'rgb(1,2,3)' / 'color(4)'
```

- A theme-name style keeps its tone: `test_tc_cnv_1_2_a_wire_keeps_its_tone_when_a_background_lands_on_it`
  (`tests/test_canvas.py:139-156`) exercises the **default** `wire()` tone, which is the input the
  module hands itself. That was the missing arm; it now exists.
- A style declaring its own background is untouched (`:130-136`), in both cases (`:159-168`).
- **`_HAS_BG`'s deletion loses nothing — confirmed, not accepted.** `on` is not an allowlist member,
  so any style containing it in any case fails `fullmatch` and keeps what it had. The uppercase arm
  passes today and **reddens** when the allowlist is removed.
- **Falsifiable.** Mutation `M-D` (replace `elif _COMPOSABLE.fullmatch(style)` with an unconditional
  `else`) → **3 arms RED**, including both the wire arm and the uppercase arm. The remedy is not inert.
- No catastrophic backtracking: `"bold "×20000 + "!"` resolves in 6 ms, linear.

**Allowlist gaps — one direction only, and it is the conservative one.** Nothing is composable that
should not be. Four rich-legal styles are *rejected* that rich would compose safely — every named
colour (`red`, `bright_black`), `rgb(...)`, `color(N)`, `not bold`. None appears in the tree: I swept
every `put`/`text`/`wire`/`edge`/`elbow_down` call in `mapper/views/` and every style is a `darkside`
hex, an f-string over hexes, `""`, or `"frame"`. So the allowlist covers the shipped surface exactly.
The residual is that the else-branch drops the background **silently** — see **N-10**.

**Where it does not hold.** The premise does not reproduce in this tree.

```
rich 15.0.0, plain Console (which is what export.save_svg uses):
  get_style('frame')            -> color=None  bg=None            frame=True
  get_style('frame on #121212') -> color=None  bg=#121212         frame=True
  'frame' in rich DEFAULT_STYLES: False
  literal "frame" anywhere in the textual 8.2.8 package: 0 hits
  Theme( / push_theme / theme= anywhere in this repo: 0 hits (one dead line in prototypes/)
```

`"frame"` is not a theme key here — it is ECMA-48's `frame` **attribute**, and it carries no colour
to lose. Rendering the two forms through a real `Console`:

```
POST-FIX  (keeps 'frame', drops the bg): [('-', color=None, bg=None,     frame=True)]
PRE-FIX   (composed 'frame on #121212'): [('-', color=None, bg=#121212,  frame=True)]
```

The pre-fix composition **lost nothing and gained the background**; the post-fix code loses the
background. For the one non-composable style the module actually produces, the change is a small net
regression, not a repair. It is unreachable either way — `radial.py` is still the only `bgs` writer
and it never calls `cv.wire` — so nothing ships broken in either direction, and I am **not** asking
for a revert: `layered.py:254` already computes `"frame"` as an edge tone, `Inc-2` touches all four
renderers, and the guard is right if a theme is ever registered. What must not stand is the reason
written beside it. See **N-1** and **N-2**.

### Item 2 · CR-F5 / A-86 — **PARTIALLY DISCHARGED**

**The factual claim is correct.** `mapper/views/lane.py:64-67`, read in full:
```python
    if state == "pending":
        return Text.assemble(("◐", darkside.WARN), (" run", darkside.WARN))
```
The branch is `state == "pending"`. A-86's correction of A-79 is factually right about the condition.

**The judgement is contestable, and the tree now contradicts itself about it.**
`tests/test_darkside_census.py:342-352` still carries, unedited:

> *"With `or in flight` still in WARN's job, app.py:879 **and lane.py:67** classify under WARN *and*
> PULSE at once, and LLR-S06.3.5's own threshold cannot be met by any implementation."*

`app.py:879` was retoned to `PULSE`. `lane.py:67` was re-judged **conforming to WARN** and registered
at `:165`. Both statements now live in one file, 180 lines apart, and they cannot both be true: if
lane.py:67 classifies under PULSE as well, registering it CONFORMING to WARN is exactly the
"classifies as both" the census forbids. The palette's own discriminator — A-78's *"work the machine
is doing versus work the operator owes — patience versus action"* — puts a CI check that is queued or
running on the machine's side, which is PULSE. A-86 replaced *reading the label* with *reading the
vendor's condition string*, and GitHub's `pending` spans queued **and** running. I am not asking you
to reverse it; I am asking you to reconcile it, because right now the register and the docstring
disagree in writing (**N-9**).

**The four `OPEN_EXCEPTIONS` rows — all four correctly judged.** I re-read each site.

| Row | My judgement |
|---|---|
| `screens/factory.py` `.factory-tag { color: #1783ff; }` | **Correct.** ACCENT is interactivity-only; a kind tag is a label. Inc-9 owns the file |
| `lane.py:41` `("▱", ALERT if behind else STEP)` | **Correct.** Behind is not failure or blockage. Inc-5 owns the file |
| `lane.py:56` `_behind_chip` `("-", ALERT), (str(behind), ALERT)` | **Correct.** Same concept, same file |
| `layered.py:268` removed-node ghost in ALERT | **Correct.** A removed node is absent information → `MUT`. Inc-3 owns the file |

Each names its owning increment; `test_llr_s06_3_2_every_registered_exception_still_exists` and
`…_the_register_is_the_size_the_dispositions_imply` both hold; the ladder 4 → 3 → 1 → 0 is coherent.

**Still mis-classified in `CONFORMING_SEVERITY` — two, and both are the same defect one site over.**

1. **`mapper/views/lane.py:93`** — `_mini_timeline`:
   ```python
   for i in range(min(total, width)):
       if i < ahead:  text.append("▰", style=darkside.INK)
       else:          text.append("▱", style=darkside.ALERT)     # <- registered CONFORMING at census:167
   ```
   This is the **behind** slot. It is the identical concept to the two rows that were just moved to
   `OPEN_EXCEPTIONS`, in the same file, two functions away — and it is worse than they are, because
   `total = max(1, ahead + behind)` paints one ALERT block even when `behind == 0`. Registered
   CONFORMING at `tests/test_darkside_census.py:167`.

2. **`"sin acta"` is painted in two different severity tokens, and both rows are CONFORMING.**
   ```
   mapper/app.py:260   text.append(... "sin acta", style=darkside.INK if doc else darkside.ALERT)   # census:144
   mapper/app.py:410   ("sin acta ", darkside.WARN), (f"{sin} ", darkside.WARN),                    # census:147
   ```
   The same literal string, the same concept — a ficha lacking its acta — in `ALERT` and in `WARN`.
   This is verbatim the pattern F5 named (*"Late and behind are the same concept, painted in two
   different tokens, and both are marked CONFORMING"*), unaddressed.

**`CONFORMING_BLUE` — clean.** All 7 rows are Textual CSS `background:` declarations, the datatable
cursor, or the `ACCENT` definition line itself. No mis-classification found. 7 + 1 exception = the 8
the clause asserts.

### Item 3 · CR-F6 — **PARTIALLY DISCHARGED**

**The parser is correct on all 14 tokens.** Executed `declared_jobs()` against the live docstring:
`parsed 14 of 14 · missing [] · extra []`. Your two named hazards:

- **A wrapped job line** — handled, and more robustly than I expected. I reflowed `ALERT`'s job so its
  continuation sits at a **2-space** indent (mutation `M-G`, the worst case for `^\s{2}`): the parser
  still returned `'failure or blockage: this item cannot proceed as it stands.'` correctly, because
  the terminating lookahead requires a **token name** after the two spaces, not merely two spaces.
- **A token name that is a prefix of another** — safe as constructed. `names` is
  `sorted(..., key=len, reverse=True)`, so the longer alternative is tried first, and the lookahead's
  trailing `\s` blocks a partial match. No current pair is a prefix, so this is a property of the
  construction rather than of the data.
- **A missing job line** reddens (`M-F` → `test_at_003_every_token_states_its_job_in_the_module_docstring` RED).

**But it does silently return a partial-quality dict — for the last token.** `VIOLET`'s parsed job is
**423 characters**: the final alternative terminates at `\Z`, so it swallows the entire trailing
`WARN's job deliberately does NOT read…` paragraph. Actual job: 21 characters. Not load-bearing today
(`TOKEN_JOB` filters to the four adjudicated tokens, and `VIOLET` is not among them), but
`declared_jobs()` is named and documented as *"Every token's job"* and it is wrong for whichever token
is declared last — including any token appended after `VIOLET`. See **N-8**.

**And the one-job claim still quantifies over 4 tokens, not 14.** Mutation `M-C` — give `TEAL` the
same job line as `SAGE` **in `darkside.__doc__`**, a product edit — is **GREEN**. Nothing reddens,
while `mapper/darkside.py:3` asserts *"Every colour token carries EXACTLY ONE job"* over all 14 and
`test_at_003_every_token_states_its_job_in_the_module_docstring` asserts the string `"EXACTLY ONE
job"` is present. `test_llr_s06_3_5` checks `len(set(TOKEN_JOB.values())) == len(TOKEN_JOB)` over the
four adjudicated tokens only. F6's suggested `assert set(jobs) == set(darkside.tokens())` and
`len(set(jobs.values())) == len(jobs)` were not adopted. §8's round-4 line *"giving two tokens one job
in the product now reddens"* is true **only for two of ACCENT/WARN/ALERT/PULSE**. See **N-7**.

### Item 4 · SEC-F3 + SEC-F4 / A-84, A-87 — **DISCHARGED**

**235 re-derived independently, from `unicodedata`, not read from the amendment:**
```
declared ranges: 24        declared points: 235       overlaps: []
_CONTROL_MAP size: 235     keys == declared: True     all values U+FFFD: True
Cc ∪ Cf ∪ Zl ∪ Zp: 237  −  PRESERVED {0x09,0x0A} = 235
declared − target: []      target − declared: []      (unicodedata 15.0.0)
```
Exact, both directions, zero slack. A-84's figure reproduces.

**Equality is asserted in BOTH directions** — `tests/test_darkside_census.py:514` (`declared − derived`)
and `:518` (`derived − declared`), each with its own message. A short range and an over-reaching range
both redden.

**`AT-009` no longer validates the list against itself.** `tests/test_export.py:120-134` keys on
`unicodedata.category(c) in ("Cc","Cf","Zl","Zp")` and carries a positive control planting two points
through the same unmodified oracle. The one residual coupling — the oracle exempts
`darkside.PRESERVED_CODE_POINTS`, so growing that set would widen the exemption — **is closed
elsewhere**: `tests/test_darkside_census.py:526` pins `PRESERVED_CODE_POINTS == {0x09, 0x0A}`.
Verified by mutation `M-E` (add `0x202E` to the preserved set **and** clip `(0x2028,0x202E)` to
`0x202D`, so the two move together): **2 arms RED**. The escape hatch does not exist.

**Does widening to 235 break anything legitimate? — No, nothing new.** The one genuinely load-bearing
pair in the set is `U+200C` ZWNJ and `U+200D` ZWJ: ZWJ builds emoji sequences (`👨‍👩‍👧` becomes
`👨�👩�👧` after `plain()`) and ZWNJ/ZWJ are orthographically required in Persian and Indic scripts.
**Both were already coerced by the pre-review 85-point list** (`0x200B–0x200D`), so the post-review
widening does not introduce them; they entered with Inc-1 relative to `5d8ee0d`'s 63 points. Of the
150 points the widening adds, the only one with any plausible Spanish-text use is `U+00AD` soft
hyphen, which is invisible in a title and carries no meaning there. The rest — Arabic/Syriac/Kaithi
format controls, Egyptian hieroglyph controls, Duployan shorthand, musical beams, the TAG block —
have no path into a ficha title in this product. Recorded as a carry at **N-13**, not as an objection.

### Item 5 · SEC-F5 / A-85 — **DISCHARGED**

`mapper/darkside.py:339` — `name, note = plain(name), plain(note)` — inside `time_row`, before any
assembly, which is the shape `hint_line` and `fit` use.

**`meta` does not need it too, and this is a chain fact, not a judgement.** I read the only call
chain end to end. `mapper/app.py:950-951` is the sole caller (`_time_row` → `darkside.time_row`), and:

```
app.py:980   name = node.ficha.title or nid                 -> passed as `name` -> plain()   ✓
app.py:996   meta = node.ficha.meta or ""
app.py:997-998   if meta and meta != "release": note_parts.append(meta)
app.py:999-1000  if node.ficha.notes ...:      note_parts.append(node.ficha.notes)
app.py:1001  note = " · ".join(note_parts) or "sin datos"    -> passed as `note` -> plain()   ✓
```

All three fields the security review named at `app.py:997-1005` — `title`, `meta`, `notes` — reach
`time_row` through `name` and `note` and are coerced by the two calls that landed. Adding a third
`plain()` on `meta` would be dead code. `glyph` and `style` are not coerced and do not need to be:
every call site passes a literal glyph and a `darkside` constant.

`tests/test_darkside.py:126-152` derives `banned` from `COERCION_RANGES` — self-referential in
principle — but carries a positive control asserting the raw input holds exactly 4 banned points,
which reddens if any of those four ranges is clipped, and the independent oracle lives one file over.
Acceptable.

### Item 6 · CR-F4 / SEC-F7 — **PARTIALLY DISCHARGED**

**It does catch the case it was written for.** Mutation `M-B` — add `cv.dots[(0, 0)] = "not-a-colour"`
to `mapper/views/lane.py`, which contains no `tones=` — → **RED** on
`test_tc_cnv_1_4_every_view_that_writes_a_layer_declares_a_tone_policy`. The positive control
(`"cv.dots[(0, 0)] = h"` matches) and the near-miss control (`"if cv.dots:"` does not) are both sound
and both run before the offender sweep.

**It is FILE-granular, not construction-granular, and that is the hole.** Mutation `M-A` — add a
second, unpoliced `Canvas(inner, body_h)` **inside `mapper/views/radial.py`** and write
`shadow.dots[(0, 0)] = "not-a-colour"` on it — is **GREEN**. The predicate is
`_LAYER_WRITE.search(blob) and "tones=" not in blob`, so one policed construction anywhere in the file
licenses every unpoliced one. `radial.py` is precisely the file most likely to grow a second canvas,
and `Inc-2` touches all four renderers. `"tones=" not in blob` is also a raw substring test — a
comment mentioning `tones=` satisfies it.

**Scope.** Both censuses read `_tracked_view_sources()`, which is `git ls-files "mapper/views/*.py"` —
5 files. I confirmed there is **no `Canvas(` construction outside `mapper/views/`** and exactly two
layer-write sites in the tree (`radial.py:210`, `:229`), so the sweep is complete *today*; a Canvas in
`screens/` or `widgets/` would be unswept. Worth one line in the docstring, not a code change.

### Item 7 · New defects introduced by the fixes

Below, N-1 … N-13. Three MEDIUMs are direct consequences of the fixes; the rest are residue.

---

## 3 · New findings

### N-1 — a **false measured claim** is now written into production source  ·  [MEDIUM]
- **What.** `mapper/canvas.py:41-43`: *"Measured on rich 15.0.0, with the shipped default wire tone:
  bare, it resolves to a colour; composed with a background, the colour becomes None."* And
  `tests/test_canvas.py:144-147`: *"`get_style("frame")` -> colour #262626; `get_style("frame on
  #121212")` -> colour None."*
- **Where.** `mapper/canvas.py:41-43`; `tests/test_canvas.py:144-147`.
- **Why it matters.** Both halves are false. Measured above: `get_style("frame")` → `color=None`;
  `get_style("frame on #121212")` → `color=None, bgcolor=#121212`. `#262626` is `darkside.STEP`,
  which is what `frame` *ought* to mean — the claim was reasoned from intent, not read off a run.
  Nothing in this repo, in rich 15.0.0's `DEFAULT_STYLES`, or in the textual 8.2.8 package registers
  `frame` as a theme key (0 hits for the literal in the whole textual package). This increment's
  entire thesis is that hand-typed claims drift and that oracles must be executed; a fabricated
  measurement in the comment justifying the HIGH's remedy is the same defect in the same batch.
- **Suggested fix.** Replace both with what is true and still argues for the guard:
  ```
  # Measured on rich 15.0.0: nothing in this tree registers `frame` as a theme
  # key, so it resolves to the ECMA-48 `frame` ATTRIBUTE and composing loses
  # nothing TODAY.  The allowlist is here for the case where it does: a theme
  # key resolves only for a BARE name, and `Style.parse` -- which is where a
  # compound string goes -- has no theme.  `layered.py:254` already computes
  # "frame" as an edge tone, and Inc-2 touches all four renderers.
  ```

### N-2 — the published contract is still unqualified, which was CR-F1's own argument  ·  [MEDIUM]
- **What.** `mapper/canvas.py:59-60` and `docs/ARCHITECTURE.md:160` both still say the `bgs`
  background *"applies to whichever glyph won"*, with no mention of the two classes that now keep
  their own style and drop it. The rule is stated only in an inline comment at `canvas.py:175-178`.
- **Where.** `mapper/canvas.py:59-60`; `docs/ARCHITECTURE.md:160`.
- **Why it matters.** CR-F1 blocked on exactly this sentence: *"a published false contract with a
  three-line fix is worth one more turn."* The code moved; the sentence did not — and it is now false
  in a second, larger way, because the exception set grew from "styles that declare their own
  background" to "those plus every non-allowlisted style". The two test names contradict each other
  in one file: `test_tc_cnv_1_2_a_background_reaches_whichever_glyph_won` (`:115`) beside
  `test_tc_cnv_1_2_a_wire_keeps_its_tone_when_a_background_lands_on_it` (`:139`).
- **Suggested fix.** In both places: *"…and a `bgs` background applies to whichever glyph won, unless
  that glyph's style declares its own background or is a name the layer cannot be composed onto, in
  which case the glyph keeps its style and the layer background is dropped."* Rename `:115` to
  `…_a_background_reaches_a_composable_winner`.

### N-3 — **CR-F11 is reported FIXED and the defect is unchanged**  ·  [MEDIUM]
- **What.** §8 says *"`HEX` could not see an 8-digit colour — **FIXED** — trailing `\b` replaced with
  a negative lookahead."* Executed, old versus new, on the exact literal F11 named:
  ```
  'color: #1783ffcc;'      OLD(\b)=[]   NEW(lookahead)=[]     <- unchanged
  'background: #1783ffFF;' OLD=[]       NEW=[]                <- unchanged
  '#1783ffzz'              OLD=[]       NEW=['#1783ff']       <- the only behaviour that moved
  '#1783ff_x'              OLD=[]       NEW=['#1783ff']
  ```
  A negative lookahead for a hex digit fails on `#1783ffcc` for the same reason `\b` did: the 7th
  character *is* a hex digit. The change only widened matching against non-hex word characters, which
  was never the complaint.
- **Where.** `tests/test_darkside_census.py:110`, and its comment at `:107-109` which now cites the
  `\b` failure as the reason for a change that does not repair it. F11 also asked for a control
  beside `HEX`; none was added — `grep HEX` returns exactly the definition and one use.
- **Why it matters.** `test_hue_census_no_undeclared_hue_ships` is the clause that found `#a3a3a3`.
  An alpha-suffixed literal in the Textual CSS blocks — where 6 of the 8 blue literals already live —
  remains invisible to it. This is faithful application of a **bad recommendation of mine**; the
  finding stands, the prescribed fix was wrong, and §8 should not record it as closed.
- **Suggested fix.** `HEX = re.compile(r"#[0-9a-fA-F]{6,8}(?![0-9a-fA-F])")`, normalise a match longer
  than 7 to its first 6 digits (or flag it as undeclared, which is the stronger reading), and add the
  control the finding asked for: `assert HEX.findall("#1783ffcc") == ["#1783ffcc"]`.

### N-4 — `_mini_timeline`'s behind-slot ALERT is registered CONFORMING while its two siblings are exceptions  ·  [MEDIUM]
- **What / where.** `mapper/views/lane.py:93` (`text.append("▱", style=darkside.ALERT)`), registered at
  `tests/test_darkside_census.py:167`. Detail in **Item 2**.
- **Why it matters.** CR-F5 moved two behind-sites out of CONFORMING and left the third, in the same
  file. A register that classifies one instance of a concept as a defect and another as conforming
  has no oracle for that concept — which is F5's own argument, surviving F5's fix.
- **Suggested fix.** Move it to `OPEN_EXCEPTIONS` with `Inc-5` as owner, worded like its two siblings.
  `test_llr_s06_3_2_the_register_is_the_size_the_dispositions_imply` then reads `== 5`, and the ladder
  becomes 5 → 4 (Inc-3) → 1 (Inc-5) → 0 (Inc-9).

### N-5 — `"sin acta"` is painted `ALERT` and `WARN`, and both rows are CONFORMING  ·  [MEDIUM]
- **What / where.** `mapper/app.py:260` vs `mapper/app.py:410`; registered at
  `tests/test_darkside_census.py:144` and `:147`. Detail in **Item 2**.
- **Why it matters.** Same shape as N-4 and as F5's original `late`/`behind` objection, in a third
  file. Under the amended jobs a ficha lacking its acta is *work pending* (`WARN`), not *an item that
  cannot proceed* (`ALERT`).
- **Suggested fix.** Either register `app.py:260` as an exception with an owning increment, or write
  one sentence in the register saying why the inspector's missing-acta is a blockage while the
  dashboard's is not. Do not leave the same string in two tokens with both marked conforming.

### N-6 — the layer-write census is file-granular  ·  [MEDIUM]
- **What / where.** `tests/test_canvas.py:198` — `if _LAYER_WRITE.search(blob) and "tones=" not in blob`.
  Mutation `M-A` GREEN; detail in **Item 6**.
- **Why it matters.** The guard's stated purpose is *"the first view to write `cv.dots[...]` on an
  unpoliced canvas silently gets the pre-Inc-1 fail-open behaviour with a fully green suite."* Inside
  `radial.py` — the only file that writes layers, and the file `Inc-2` touches — that is exactly what
  still happens.
- **Suggested fix.** Bind the write to its receiver rather than to the file:
  ```python
  _CANVAS_BIND = re.compile(r"\b(\w+)\s*=\s*Canvas\(", re.M)
  # for each receiver that appears in a `<recv>.dots[` / `<recv>.bgs[` write,
  # assert `tones=` appears inside that construction's argument list.
  ```
  Or, cheaper and honest: keep the file predicate and state its granularity in the docstring, with a
  carry. Do not leave the docstring claiming a guarantee the predicate does not give.

### N-7 — the one-job census covers 4 of 14 tokens while the docstring claims 14  ·  [MEDIUM]
- **What / where.** Mutation `M-C` GREEN; `tests/test_darkside_census.py:278-279` vs
  `mapper/darkside.py:3`. Detail in **Item 3**.
- **Suggested fix.** Adopt the second half of F6, now that the parser exists and works:
  ```python
  def test_at_003_no_two_tokens_declare_the_same_job():
      jobs = declared_jobs()
      assert set(jobs) == set(darkside.tokens()), "a token has no job line"
      assert len(set(jobs.values())) == len(jobs), "two tokens share a job"
  ```
  This requires N-8 first, or `VIOLET`'s 423-character job makes the equality accidentally true.

### N-8 — `declared_jobs()` over-captures the last declared token  ·  [LOW]
- **What / where.** `tests/test_darkside_census.py:48-51`. `VIOLET`'s parsed job is 423 characters —
  `'relaciones / enlaces. WARN's job deliberately does NOT read "or in flight". Work the machine…'` —
  because the final alternative terminates at `\Z`.
- **Why it matters.** Harmless today (`TOKEN_JOB` filters `VIOLET` out) and load-bearing the moment
  N-7 lands or a token is appended after `VIOLET`.
- **Suggested fix.** Terminate on the blank line as well as on the next name:
  `(?=^\s{2}(?:{names})\s|^\S|\Z)` — the trailing paragraph starts at column 0, so `^\S` closes it.
  Verify against `len(declared_jobs()["VIOLET"]) == 21`.

### N-9 — `test_at_003_warn_does_not_claim_work_that_is_merely_in_flight`'s docstring contradicts the register above it  ·  [LOW]
- **What / where.** `tests/test_darkside_census.py:346-347` names `lane.py:67` as in-flight work
  classifying under both tokens; `:161-165` registers the same line as conforming to `WARN`.
- **Suggested fix.** Whichever way A-86 is finally settled, edit the other. One file must not assert
  both.

### N-10 — the composition's else-branch drops the background with no signal  ·  [LOW]
- **What / where.** `mapper/canvas.py:175-178` — the implicit `else` returns the style unchanged and
  discards `bg` silently, after `_tone(bg)` has already been computed.
- **Why it matters.** For the "declares its own background" case this is correct precedence. For a
  named style it is a silent loss — the same *prevention with no detection* shape you accepted from
  `SEC-F6` and fixed for `tones`/`fallback` in the same file, eight lines up.
- **Suggested fix.** No behaviour change needed; the honest minimum is to say so in the class
  docstring alongside N-2's correction, so a reader knows the drop is deliberate.

### N-11 — `ruff check fixtures/` is a vacuous gate check  ·  [LOW]
- **What.** `fixtures/` contains `legacy.mmd`, `legacy_nodos.yml`, `mapper.db` — **no `.py` file**.
  Ruff prints `warning: No Python files found under the given path(s)` and then `All checks passed!`.
- **Where.** `increment-001.md:92` (§3) and `:107` (§4, recorded as a passing result).
- **Why it matters.** It is recorded as evidence and it examines nothing — the exact vacuous-check
  class this batch's own C-55 discipline exists to catch, in the packet's own results table.
- **Suggested fix.** Drop the line, or replace it with the check it was presumably standing in for
  (`git status --short -- fixtures/` empty, which is the property that actually matters here and which
  I confirmed holds).

### N-12 — the Unicode-class equality is pinned to the runtime's `unicodedata` version  ·  [LOW]
- **What / where.** `tests/test_darkside_census.py:508-521` compares 24 literal ranges against
  `unicodedata` — **15.0.0** on this Python 3.12. A Python upgrade shipping Unicode 15.1 or 16.0 will
  redden it wherever the classes gained a member.
- **Why it matters.** Reddening is arguably the *correct* behaviour — it forces a re-review of a
  security-relevant list — but it is undeclared, so it will read as a spurious failure to whoever
  meets it.
- **Suggested fix.** One line in the test docstring: *"pinned against `unicodedata` 15.0.0 (Python
  3.12); a Unicode upgrade reddens this deliberately — re-derive the ranges, do not widen the oracle."*

### N-13 — ZWJ / ZWNJ are coerced, which corrupts emoji sequences and Persian-Indic text  ·  [LOW]
- **What / where.** `mapper/darkside.py:373` — `(0x200B, 0x200F)`. A ficha title containing `👨‍👩‍👧`
  renders as `👨�👩�👧`; `U+200C`/`U+200D` are orthographically required in Persian and Indic scripts.
- **Why it matters — and why it is not an objection to A-84.** These were already in the pre-review
  85-point list, so the widening to 235 did **not** introduce them; they entered with Inc-1 relative
  to `5d8ee0d`. Of the 150 points A-84 adds, only `U+00AD` has any conceivable Spanish-text use and
  it is invisible in a title. **The widening breaks nothing new.**
- **Suggested fix.** A carry, not a change: record ZWJ/ZWNJ as a *declared accepted cost* beside
  `PRESERVED_CODE_POINTS`, so the next person who meets a broken emoji finds the decision instead of
  filing it as a bug.

---

## 4 · Disposition summary

| Finding | Author's §8 claim | My confirmation |
|---|---|---|
| **CR-F1** (HIGH) | FIXED | **PARTIALLY** — mechanism in place and falsifiable (`M-D` 3 RED); premise false in this tree (N-1); contract still unqualified (N-2) |
| CR-F2 | FIXED | **DISCHARGED** — `ARCHITECTURE.md:68` now carries the real signature; `B-44` correctly carried |
| CR-F3 | renamed, carried `B-43` | **DISCHARGED** — the reviewer's own option (b), taken cleanly; docstring states the scope |
| **CR-F4 / SEC-F7** | FIXED | **PARTIALLY** — catches the unpoliced file (`M-B` RED), blind inside a policed file (`M-A` GREEN) → N-6 |
| **CR-F5** | FIXED | **PARTIALLY** — 3 rows correctly moved, 4 exceptions correctly judged; 2 mis-classifications remain (N-4, N-5) and the tree self-contradicts (N-9) |
| **CR-F6** | FIXED | **PARTIALLY** — parser correct on 14 names; last token over-captures (N-8); the claim still covers 4 (N-7, `M-C` GREEN) |
| CR-F7 | fixed then deleted as INERT | **DISCHARGED** — the deletion loses nothing; verified by construction and by `M-D` |
| CR-F8 | DECLARED | **DISCHARGED** — `canvas.py:136-139` |
| CR-F9 | 63, now 235 | **DISCHARGED** — `increment-001.md:42`, and 63 re-derived from the archived base |
| CR-F10 | FIXED | **DISCHARGED** — `rglob`, tracked-set containment, self-inclusion check, name **and** value sweep at `census.py:568-586` |
| **CR-F11** | FIXED | **NOT DISCHARGED** — behaviour on an 8-digit literal is unchanged (N-3) |
| **SEC-F3** | FIXED, gated pre-merge | **DISCHARGED** — `unicodedata` oracle + positive control; the `PRESERVED` escape hatch is pinned (`M-E` 2 RED) |
| **SEC-F4** | FIXED by widening | **DISCHARGED** — 235 re-derived exactly, both directions asserted, no legitimate loss |
| **SEC-F5** | FIXED in `time_row` | **DISCHARGED** — `meta` is covered transitively; verified on the only call chain |
| SEC-F6 | FIXED | **DISCHARGED** — `Canvas.__init__` refuses `tones=` without `fallback=`, tested at `test_canvas.py:171-176` |
| SEC-F8 | CARRIED `B-45` | **DISCHARGED** as a carry |
| SEC-F1 / SEC-F2 | NOT Inc-1's, batch-close blockers `B-46`/`B-47` | **AGREED** — both are outside this change set; `B-46` and `B-47` land in `A-88` with the blocker flag and no owner, which is the honest state |

**New:** 0 HIGH · 7 MEDIUM (N-1 … N-7) · 6 LOW (N-8 … N-13).

---

## 5 · Evidence checklist

- [x] **Diff read in full** — `git diff 5d8ee0d -- mapper/ tests/ docs/` (9 files, 538+/26−) plus both
      untracked test files read end to end: `mapper/canvas.py:1-182`, `mapper/darkside.py:1-90,328-420`,
      `mapper/views/radial.py:110-259`, `mapper/app.py:876-882,950-1008`, `docs/ARCHITECTURE.md:68,160`,
      `tests/test_canvas.py:1-380`, `tests/test_darkside_census.py:1-587`, `tests/test_export.py` diff,
      `tests/test_darkside.py` diff, `tests/test_repair_depth.py:99-116`, `01-requirements.md:7877-7971`.
- [x] **Correctness pass** — allowlist behaviour enumerated on 17 style strings; backtracking measured
      (linear to 20 000 tokens); `frame` resolution measured through a real `Console` in both forms;
      `time_row`'s call chain traced to its only caller. **Defects found: N-1, N-2, N-3.**
- [x] **Every numeric claim re-derived, not read** — 235 from `unicodedata`; 63 and 630 and ruff 29
      from a `git archive` of `5d8ee0d`; 691/17/28 and all five per-file collection counts from runs here.
- [x] **Six mutations executed in a detached copy**, `PYTHONDONTWRITEBYTECODE=1`, restored and verified
      clean after each — `M-A` GREEN (N-6), `M-B` RED, `M-C` GREEN (N-7), `M-D` 3 RED, `M-E` 2 RED,
      `M-F` RED, `M-G` parser-correct.
- [x] **Simplicity pass** — nothing to delete. `_COMPOSABLE`, `declared_jobs`, `_LAYER_WRITE` and the
      `unicodedata` oracle are each the minimum that does the job; the deleted `_HAS_BG` was correctly
      deleted and I re-measured that its deletion loses nothing.
- [x] **Reuse / duplication checked** — `TOKEN_JOB`'s second copy is gone (F6's real half). The two
      remaining duplications are the register's own contradictions (N-4, N-5), not code.
- [x] **Tests reviewed for intent** — N-3 (a control the fix does not provide), N-6 (a docstring
      claiming more than the predicate gives), N-7 (a claim quantified over 4 of 14), N-9 (two
      contradictory claims in one file), N-11 (a recorded check that inspects nothing).
- [x] **Rules of engagement** — no file under `mapper/`/`tests/`/`docs/` edited; no mutating git
      command; `fixtures/` untouched (`git status` identical before and after); no live `MapperApp`.
- [x] **Verdict explicit** — below.

---

## 6 · Verdict

- [ ] OK to advance
- [x] **OK with the listed fixes applied first**
- [ ] Block

**The increment passes the gate on correctness. It does not pass as documented.**

**The HIGH is discharged.** `_COMPOSABLE` is in the tree, it behaves as declared on every arm you
asked about, the missing test arm exists and exercises the module's own default value, `_HAS_BG`'s
deletion provably loses nothing, and reverting the remedy reddens three arms. Nothing in the post-fix
tree is a HIGH: the widening re-derives to 235 exactly with equality asserted in both directions, the
`AT-009` oracle is genuinely independent and its one residual escape hatch is pinned shut, `time_row`
covers all three fields the security lens named, and every baseline and ledger number reproduces to
the unit.

**What must be fixed before this is signed is the record, not the code.** Three of §8's *"FIXED"*
dispositions are overstated, and §8 is the artifact the operator approves against:

1. **CR-F11 is not fixed** (N-3) — the 8-digit literal is still invisible, identically to before. My
   own prescribed regex was wrong; the row must not read FIXED.
2. **CR-F6 is half fixed** (N-7) — the parser landed, the totality did not, and the round-4 line
   *"give two tokens one job in the product now reddens"* is true for 4 tokens, not 14. `M-C` is GREEN.
3. **CR-F5 is half fixed** (N-4, N-5, N-9) — the four exceptions are judged correctly, and two more
   sites of the same shape are still registered CONFORMING while the file contradicts itself in
   writing about `lane.py:67`.

And one thing the fix itself introduced: **N-1**, a fabricated measurement in production source. In an
increment whose central argument is *"an oracle built from the list can never detect that the list is
short, and twice it was"*, a comment that says *measured* about something that was reasoned is the one
defect this batch cannot afford to ship. It is a comment edit. So is **N-2**.

**Minimum to advance:** N-1, N-2, N-3, and correcting §8's three rows. N-4 and N-5 need a decision
recorded — move to `OPEN_EXCEPTIONS` or justify in the register — before `Inc-3`/`Inc-5` apply the
dispositions mechanically. N-6 and N-7 have short fixes and both harden guarantees `Inc-2` is about to
lean on; N-8 must land before N-7 or the equality passes for the wrong reason. N-9 … N-13 are carries.

**Everything you asked me to attack, I executed.** Your 235-point claim, your both-directions
equality, your `PRESERVED` pin, your `meta` question, your allowlist, your `_HAS_BG` deletion, your
docstring parser and your six baseline numbers are all **correct as stated** — the coercion set
re-derived from `unicodedata` independently, the baselines from an archived `5d8ee0d`, the census
behaviour from six mutations in a detached copy. The one place the tree is wrong is the one you asked
about first, and not in the direction anyone expected: **the HIGH you fixed does not reproduce here.**
`"frame"` is not a theme key in this repo, in rich 15.0.0, or anywhere in textual 8.2.8 — it is the
ECMA-48 attribute, it carries no colour, and composing it preserved everything and added a background.
The guard is still worth keeping for the day a theme exists and because `layered.py:254` already
produces `"frame"` as a tone. The sentence justifying it is not.

*Hand-offs: no security-relevant change found in this confirmation — the coercion work is a strict
improvement and `security-reviewer` already owns `B-46`/`B-47` at batch close. No suite-execution gap:
both lanes are green and every count reconciles; `qa-reviewer` still owns `Inc-2`'s standing re-run
obligation on `AT-007`/`AT-009`, which — with `SEC-F3` landed — is now worth running.*
