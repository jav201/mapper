# Code Review — Increment 001

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Increment | `001` |
| Base | `5d8ee0d` on `feat/ui-next-batch-02` |
| Reviewer | `code-reviewer` (independent; author's reasoning re-derived, not accepted) |
| Date | 2026-08-28 |
| **Verdict** | **BLOCK — 1 HIGH must be fixed before the increment advances** |

---

## Scope reviewed

Working-tree diff against `5d8ee0d` over `mapper/ tests/ docs/`, plus the two untracked
test files, plus amendment set 4 in `01-requirements.md`.

```
docs/ARCHITECTURE.md         |   2 +-
mapper/app.py                |   2 +-
mapper/canvas.py             |  83 +++++++++--
mapper/darkside.py           | 115 +++++++++++++--
mapper/views/radial.py       |  15 ++--
tests/test_export.py         |  94 +++++++++++-
tests/test_radial.py         | 108 ++++++++++++++
tests/test_repair_depth.py   |  19 ++--
tests/test_canvas.py         | 316 (untracked, new)
tests/test_darkside_census.py| 500 (untracked, new)
```

`prototypes/` — **not staged, not modified.** `git status --short` shows 9 modified,
0 renamed, and the untracked set the packet declares. Clean.

---

## What I re-executed (not taken on trust)

| Claim | Method | Result |
|---|---|---|
| `_DOT_BITS` matches the Unicode braille layout | Checked `((0x01,0x08),(0x02,0x10),(0x04,0x20),(0x40,0x80))` against dot numbering 1/4, 2/5, 3/6, 7/8 at bit values 0x01…0x80 | **CORRECT** |
| Negative sub-cell coords | `-1 // 2 == -1`, `-1 // 4 == -1`; any `sx <= -1` folds to `x <= -1` and fails `0 <= x` | **CORRECT — all negatives dropped** |
| `int(dx*2)` truncation hazard in `radial.py:210` | `pos` is clamped to `[0, inner-1]` / `[0, body_h-1]` at `radial.py:142-143`, so `dx, dy >= 0` always | **NOT A DEFECT** — truncation never sees a negative |
| Empty-layer path byte-identical to `5d8ee0d` | `Text.append(" ")` ≡ `append(" ", None)` (rich signature default) | **BYTE-IDENTICAL** |
| `Text.append(ch, "")` ≡ `Text.append(ch)` (your item 8) | Read `rich.text.Text.append` source: `if style:` guards the span append. Constructed all three forms — `spans == []` for each, `a == b == c`, identical ANSI output | **YOUR MEASUREMENT IS CORRECT.** The deleted branch was dead and its comment was false. Deleting it was right |
| `COERCION_RANGES` is a strict widening | Rebuilt the `5d8ee0d` map (`range(0x00,0x20) - {0x09,0x0A}` ∪ `range(0x7F,0xA0)`) and diffed against `_CONTROL_MAP` | **85 declared · 0 survivors through `plain()` · 0 shipped points lost · +22 · TAB & LF preserved · CR coerced.** Ranges do not overlap; `declared == set(_CONTROL_MAP)` |
| The four re-baselined digests | Independent re-derivation in a clean `git worktree` at `5d8ee0d` vs the current tree, recipe re-implemented from `_fingerprint` | **Exactly the 4 `RadialRenderer` keys moved. All 8 `Layered`/`Outline` digests byte-identical to `5d8ee0d`'s output and NOT recaptured. All 4 new literals equal the working tree's true output. The recipe and `fixtures/` are unchanged** |
| Fast lane / ruff | `685 passed, 17 deselected in 56.10s`; `ruff check mapper/ tests/` → **28** | **REPRODUCED** |
| Census arithmetic | 36 severity sites = 35 `CONFORMING_SEVERITY` + 1 severity `OPEN_EXCEPTIONS`; 8 blue = 7 + 1. No stale rows in either conforming set | **RECONCILES** |

**Amendment set 4 (A-77 → A-83): all seven are legitimate Before/After amendments, not quiet
weakenings.** A-77 resolves a real intra-document fork and records the dissenting lens rather than
averaging it. A-78 **narrows** `WARN`, which strengthens the one-job rule. A-80 is a genuine
*strengthening* — the spec's own C0 row was short by `U+000D` and adopting it verbatim would have
regressed shipped coverage; I re-verified the 0-loss claim from the reconstructed baseline map.
A-82 makes an undefined term decidable and its luminance guard fires in **both** directions
(a bright mis-filed surface and a dark mis-filed semantic both redden).
**A-79 is the only amendment that relaxes a number** (register 1 → 2). It is forced by A-78, the
new entry names an owning increment, and `test_llr_s06_3_2_every_registered_exception_still_exists`
makes the handoff mechanical rather than a promise. Legitimate — but see F5.

---

## Findings

### F1 — `rows()`'s background composition silently destroys a named-style foreground  [Severity: HIGH]

- **What:** `mapper/canvas.py:141` composes a background by string concatenation:
  `style = f"{style} on {bg}"`. That is only sound when `style` is a colour/attribute
  string. It is **not** sound when `style` is a **theme style name** — and `"frame"` is the
  default value of `Canvas.wire()` (`canvas.py:64`), `Canvas.edge()` (`:70`),
  `Canvas.elbow_down()` (`:76`) and the fallback at `canvas.py:131`.

  Measured against rich 15.0.0 with a theme defining `frame`:

  ```
  get_style("frame")             -> Style(color='#262626')            # theme resolves
  get_style("frame on #121212")  -> Style(bgcolor='#121212', frame=True)
  ```

  `Console.get_style` resolves a theme key only for a **bare** name; a compound string goes to
  `Style.parse`, which has no theme and happens to accept `frame` as the legacy style *attribute*.
  The wire's tone is dropped, no exception is raised, and the result is a wire painted with **no
  colour at all** — which is exactly the fail-open mode `_tone()` was added to close
  (`canvas.py:92-96`: *"silently paints unstyled, which is indistinguishable from a tone that was
  never applied"*). The increment closes that hole in one branch and re-opens it in the next one,
  in the same function.

- **Where:** `mapper/canvas.py:137-142`, reachable through the defaults at `canvas.py:64,70,76,131`.
  Declared as universally true at `mapper/canvas.py:37-39` and republished as the module contract at
  `docs/ARCHITECTURE.md:160` (*"a `bgs` background applies to whichever glyph won"*).

- **Why it matters:** The composition rule is the increment's central new mechanism and its
  published contract is false for the module's own default value. I confirmed it is **not
  reachable in the product today** — `radial.py` is the only file that writes `bgs` and it never
  calls `cv.wire` (only `cv.put`, at `:240` and `:250`) — so no user-visible defect ships. I am
  still calling it HIGH, on three grounds, and you should overrule me knowingly rather than by
  omission: (i) it is a correctness defect in delivered code, not a hypothesis about future code;
  (ii) `Inc-2` touches all four renderers behind a byte-identity gate that compares a renderer
  against itself, and `layered.py:254` already computes `"frame"` as an edge tone — the first
  renderer to draw a pill over a wired cell loses the wire's colour with nothing to catch it;
  (iii) the covering test dodges the defective input. `test_tc_cnv_1_2_a_background_reaches_whichever_glyph_won`
  (`tests/test_canvas.py:115-127`) exercises the wire branch with `darkside.INK`, never with the
  default `"frame"`, so it asserts a universal it has not tested. The fix is three lines.

- **Suggested fix** (`mapper/canvas.py`, module level and in `rows()`):

  ```python
  _HAS_BG = re.compile(r"(?i)(?:^|\s)on\s")
  # Only these can be safely extended with " on <bg>".  A theme NAME cannot:
  # `Style.parse` never resolves theme keys, so "frame on #121212" parses
  # `frame` as the legacy style ATTRIBUTE and drops the tone entirely.
  _COMPOSABLE = re.compile(r"(?i)^(?:#[0-9a-f]{6}|bold|dim|italic|underline|reverse|\s)*$")
  ```
  ```python
              if key in self.bgs:
                  bg = self._tone(self.bgs[key])
                  if style is None:
                      style = f"on {bg}"
                  elif _HAS_BG.search(style):
                      pass                                   # the winner declares its own bg
                  elif _COMPOSABLE.fullmatch(style):
                      style = f"{style} on {bg}".strip()
                  # else: a named style — keep the tone, drop the background.
  ```
  This also subsumes F7 (the `on` check becomes case-insensitive and anchored on a word
  boundary rather than on `split()`).

  Add the arm that is currently missing:
  ```python
  def test_tc_cnv_1_2_a_wire_keeps_its_tone_when_a_background_lands_on_it():
      """The default wire tone is a THEME NAME, which cannot be string-composed."""
      cv = _canvas(1, 1)
      cv.wire(0, 0, _LR)                      # no tone -> the "frame" default
      cv.bgs[(0, 0)] = darkside.PANEL
      assert "frame" in _style_at(cv.rows()[0], 0)
  ```
  I verified this test **fails** on the current implementation (the span reads
  `"frame on #121212"`, which rich renders with no foreground) and passes under the fix.
  No digest moves: the 8 held `Layered`/`Outline` keys write no `bgs` at all.

---

### F2 — `docs/ARCHITECTURE.md` now contradicts itself about `Canvas`'s constructor  [Severity: MEDIUM]

- **What:** The increment updated the A3 commitment row (`:160`) to
  `Canvas(w, h, tones=(), fallback="")` but left the **module inventory** row at `:68` reading
  `` `Canvas(w, h)` with `put`, `wire`, `edge`, `elbow_down`, `text`, `rows` ``. The map now
  asserts two different constructors for one class, and `:68` is false.
- **Where:** `docs/ARCHITECTURE.md:68` (unchanged) vs `docs/ARCHITECTURE.md:160` (changed).
- **Why it matters:** That exact row carries an in-line correction stamped
  *"Corrected `2026-08-27-repair-batch-02`"* for this precise defect class — a row that named an API
  the code did not have. One batch later the same row is false again, in the opposite direction.
  And the guard that exists for it cannot see it: `tests/test_repair_map_truth.py:112` pins the
  string `` `Canvas(w, h)` with `put`, `wire`, `edge`, `elbow_down`, `text`, `dline` `` and asserts
  it is **absent** from the markdown. It is a substring check on prose — the file imports only
  `re`, `pathlib` and `pytest`, never `mapper`, and the whole 26-arm module runs in 0.04 s. It
  cannot observe `Canvas.__init__` under any circumstance. Its only discriminating token against
  the live line at `:68` is the trailing `dline` vs `rows`, so it stays green while the claim
  beside it goes false. The packet's §2 says the ARCHITECTURE change was *"the `Canvas dots/bgs`
  row moves … to `PRESENT`"* — true, but incomplete: two rows describe this module and only one
  was updated.
- **Suggested fix:** edit `docs/ARCHITECTURE.md:68` to
  `` `Canvas(w, h, tones=(), fallback="")` with `put`, `wire`, `edge`, `elbow_down`, `text`, `rows` ``,
  keeping the existing `dline` correction note intact. Optionally file a carry for `Inc-2`: the
  map-truth pin should assert against `inspect.signature(Canvas.__init__)`, not against document
  wording, or it will keep passing through the next drift.

---

### F3 — the blue census is quantified over 8 of 50 sites; the sibling severity census is not  [Severity: MEDIUM]

- **What:** `BLUE = re.compile(re.escape(darkside.ACCENT), re.IGNORECASE)`
  (`tests/test_darkside_census.py:98`) matches only the **hex literal** `#1783ff`. The severity
  census one line above uses `ADJUDICATED = re.compile(r"\bdarkside\.(WARN|ALERT|PULSE)\b")` — a
  **symbolic** derivation. Executed over the tracked tree: 8 blue literal lines, and **42
  `darkside.ACCENT` symbolic sites, of which 0 are censused.**
- **Where:** `tests/test_darkside_census.py:98`, `:222-232`; the uncovered sites include
  `mapper/views/radial.py:201,230,237,245`, `mapper/views/lane.py:133,150,225,286,349`,
  `mapper/views/layered.py:222,254,279`, `mapper/screens/palette.py:104,122,124`,
  `mapper/app.py:273,522,577-592,1005`.
- **Why it matters:** `LLR-S06.3.3`'s value is a totality claim — *"the blue stays interactivity-only"*
  — and `test_hue_census_the_blue_stays_interactivity_only` covers 16% of the blue surface. The
  docstring is honest (*"over the derived literal set"*), but the test's name and the LLR's claim
  are not, and `CONFORMING_BLUE`'s 7 rows are complete only relative to a derivation that cannot
  see a symbolic use. `test_hue_census_no_undeclared_hue_ships` does **not** close this: it proves
  no *undeclared hue* exists, not that ACCENT is used only for interactivity. Two of the uncovered
  sites are arguably non-affordance labels — `mapper/screens/factory.py:291`
  (`text.append(f"[{doc.kind}] ", style=darkside.ACCENT)`, a kind tag) is the same defect as the
  registered `.factory-tag` exception, one line over and unfiled.
- **Suggested fix:** either widen the pattern to match the severity census —
  ```python
  BLUE = re.compile(rf"\bdarkside\.ACCENT\b|{re.escape(darkside.ACCENT)}", re.IGNORECASE)
  ```
  and extend `CONFORMING_BLUE` to the resulting ~50 rows (this is real work; it is also the only
  thing that makes the clause total) — **or** rename the test to
  `test_hue_census_no_blue_LITERAL_ships_outside_an_interactive_site`, say so in the docstring,
  and file a carry with an owning increment. Do not leave the broad name over the narrow
  derivation.

---

### F4 — the tone policy's fail-open default is unguarded against a future layer writer  [Severity: MEDIUM]

- **What:** `Canvas.__init__`'s `tones=()` default disables the guard entirely
  (`canvas.py:98`: `if not self._tones or tone in self._tones`). `mapper/views/lane.py:197` and
  `mapper/views/layered.py:196` both build `Canvas(inner, body_h)` with no policy. Nothing in the
  suite prevents either from acquiring a layer write. The monkey-patch census
  (`tests/test_canvas.py:52`, `_INSTANCE_ASSIGN = re.compile(r"\b\w+\.(?:dots|bgs)\s*=\s*(?!=)")`)
  bans **whole-attribute** assignment (`cv.dots = {}`) but not the **subscript** write
  (`cv.dots[(x, y)] = hue`) — which is the form `radial.py:210,229` actually uses and the form a
  future writer would copy.
- **Where:** `mapper/canvas.py:49-58`, `:98`; `tests/test_canvas.py:52`, `:65-84`.
- **Why it matters:** Answering your item 3 directly — **injection is the right call** (amending a
  doc row that already owes an un-landed `ARQ-1` edit is worse, and the guard belongs in `rows()`
  for the reason A-81 gives), and **there is no live fail-open hole today**, because `radial.py`
  is the only layer writer and it passes the policy. But injection converts a guarantee into a
  convention, and the convention has no enforcement. `Inc-5` owns `views/lane.py` and `Inc-2`
  touches all four renderers; the first one to write `cv.dots[...]` on an unpoliced canvas gets
  the pre-Inc-1 fail-open behaviour with a full green suite.
- **Suggested fix:** one derived census in `tests/test_canvas.py`, no production change:
  ```python
  _LAYER_WRITE = re.compile(r"\b\w+\.(?:dots|bgs)\s*\[")

  def test_tc_cnv_1_4_every_canvas_that_writes_a_layer_declares_a_tone_policy():
      """The policy is INJECTED, so it is optional; this is what makes it mandatory
      wherever it matters.  A file that writes a layer must construct with `tones=`."""
      offenders = []
      for path in _tracked_view_sources():
          blob = path.read_text(encoding="utf-8")
          if _LAYER_WRITE.search(blob) and "tones=" not in blob:
              offenders.append(path.relative_to(REPO).as_posix())
      assert _LAYER_WRITE.search("cv.dots[(0, 0)] = h")          # positive control
      assert not _LAYER_WRITE.search("if cv.dots:")              # near-miss control
      assert offenders == []
  ```

---

### F5 — three `CONFORMING_SEVERITY` rows contradict the jobs the palette declares  [Severity: MEDIUM]

- **What:** `ALERT`'s declared job (`darkside.py` docstring) is *"failure or blockage: this item
  cannot proceed as it stands."* Three registered-as-conforming rows do not express it:

  | Row | Site | Objection |
  |---|---|---|
  | `census.py:147` | `lane.py:41` — `("▱", darkside.ALERT if behind else darkside.STEP)` | Being *N commits behind* is neither a failure nor a blockage. It is *"pending, due, or at risk"* — **`WARN`'s** job |
  | `census.py:148` | `lane.py:56` — `_behind_chip`, `("-", ALERT), (str(behind), ALERT)` | Same concept, same file |
  | `census.py:157` | `layered.py:268` — `cv.text(gx, gy+2, "~"+ghost[:-1], darkside.ALERT)`, *"Removed nodes rendered as alert ghosts"* | A removed node is **absent information**, which the docstring assigns explicitly to **`MUT`** |

  The first two are internally inconsistent with rows the same register already accepts:
  `("mapper/views/lane.py", '"late": darkside.WARN,')` at `census.py:145`. *Late* and *behind* are
  the same concept, painted in two different tokens, and both are marked CONFORMING.
- **Where:** `tests/test_darkside_census.py:147`, `:148`, `:157`.
- **Why it matters:** The file's own docstring (`:16-18`) declares that job assignment is *"a human
  judgement, made once by reading the line"* — so the register **is** the oracle for
  `HLR-S06.3`, and a mis-judged row is a permanently licensed defect that no mutation can reach.
  A census whose register accepts sites that contradict the jobs it enforces has a weaker oracle
  than its 36/36 totality suggests.
- **Suggested fix:** re-read the three lines and either move them to `OPEN_EXCEPTIONS` with an
  owning increment (`Inc-5` owns `lane.py`; `layered.py` needs an owner), or write one sentence per
  row in a comment stating why *behind* is a blockage and why a removed node is not absent
  information. Whichever you choose, the two lane rows must not stay classified differently from
  `"late": darkside.WARN` in the same file.

  **Related, and worth catching before `Inc-5` applies it mechanically:** `B-38`'s prescribed
  disposition is *"retone to `PULSE`"* for `lane.py:67`. That branch is
  `if state == "pending":` (`lane.py:66`) — the CI state is literally **pending**, which is
  `WARN`'s declared job; only the *label* says `" run"`. Under the amended jobs the correct fix may
  be to relabel, not to retone. Decide it now, in the register's reason string, rather than in
  `Inc-5`.

---

### F6 — `TOKEN_JOB` is a second hand-typed copy of the jobs `darkside.__doc__` declares  [Severity: MEDIUM]

- **What:** The jobs are written twice: as prose in `mapper/darkside.py`'s module docstring, and as
  a 4-entry literal `TOKEN_JOB` at `tests/test_darkside_census.py:39-44` with constants at `:34-37`.
  Only `WARN`'s is tied back to the product — `test_at_003_warn_does_not_claim_work_that_is_merely_in_flight`
  (`:297-307`) parses `darkside.__doc__`. `ALERT`, `PULSE` and `ACCENT`'s jobs are asserted only
  against the test's own table.
- **Where:** `tests/test_darkside_census.py:34-44` vs `mapper/darkside.py:6-30`.
- **Why it matters:** `M-S06.3.5-a` (*"give both severity tokens the single shared job 'severity'"*)
  reddens `test_llr_s06_3_5`'s `len(jobs) == len(TOKEN_JOB)` — but that mutation had to be applied
  to **the test's own table**. Mutating the *product* (giving `WARN` and `ALERT` the same job line
  in `darkside.__doc__`) reddens nothing, because `TOKEN_JOB` is independent of the docstring.
  The RED verdict therefore proves the test can detect a change to itself. This is the same
  defect class `test_llr_coerce_1_the_list_is_declared_exactly_once` and
  `test_llr_coerce_1_no_test_retypes_the_range_list` were written to forbid for
  `COERCION_RANGES` — *"two copies of a list like this agree on the day they are written and drift
  the first time one is edited"* — applied inconsistently one file over.
- **Suggested fix:** derive `TOKEN_JOB` from the docstring the way the coercion tests derive from
  the declaration, so the product is the single source:
  ```python
  def _declared_jobs() -> dict[str, str]:
      """Parsed from darkside.__doc__: the jobs are declared ONCE, in the product."""
      names = "|".join(sorted(darkside.tokens(), key=len, reverse=True))
      body = re.findall(rf"^\s{{2}}({names})\s+(.*?)(?=^\s{{2}}(?:{names})\s|\Z)",
                        darkside.__doc__, re.M | re.S)
      return {n: " ".join(j.split()) for n, j in body}

  TOKEN_JOB = {n: j for n, j in _declared_jobs().items()
               if n in ("ACCENT", "WARN", "ALERT", "PULSE")}
  ```
  Then `assert len(set(TOKEN_JOB.values())) == len(TOKEN_JOB)` reddens on a **product** edit, and
  the "EXACTLY ONE job" claim covers all 14 tokens instead of 4:
  ```python
  def test_at_003_no_two_tokens_declare_the_same_job():
      jobs = _declared_jobs()
      assert set(jobs) == set(darkside.tokens()), "a token has no job line"
      assert len(set(jobs.values())) == len(jobs), "two tokens share a job"
  ```

---

### F7 — the background check is case-sensitive; `Style.parse` is not  [Severity: LOW]

- **What:** `"on" not in style.split()` (`mapper/canvas.py:141`). Rich lowercases each word in
  `Style.parse`, so `"ON #ff0000"` **is** a background — verified:
  `get_style("ON #ff0000") -> Style(bgcolor='#ff0000')`. The check misses it and appends a second
  `on <bg>`; last-wins, so the `bgs` layer overrides a cell that declared its own background,
  inverting the declared precedence.
- **Where:** `mapper/canvas.py:141`.
- **Why it matters:** No caller writes uppercase `ON` today, so this is latent. It is listed
  separately because it is a *different* misfire from F1 and it disappears for free under F1's fix.
- **Suggested fix:** subsumed by F1's `_HAS_BG = re.compile(r"(?i)(?:^|\s)on\s")`.

---

### F8 — the winning dot tone in a shared cell is "first sub-key inserted", which is undeclared  [Severity: LOW]

- **What:** `_braille()` uses `tones.setdefault((x, y), tone)` (`canvas.py:116`). Where two edges of
  different hues pass through one cell, the painted tone is whichever sub-key was inserted into
  `self.dots` first — deterministic, but arbitrary with respect to meaning. In `radial.py:200-210`
  the active-path hue is `darkside.ACCENT` and off-path branches are `_GREYS`; a shared cell can
  therefore paint the **grey** and lose the ACCENT, which is the one hue in that loop carrying a
  user-visible affordance.
- **Where:** `mapper/canvas.py:116`; consumed at `mapper/views/radial.py:200-210`.
- **Why it matters:** The class docstring declares precedence *between* layers and says nothing
  about precedence *within* the dots layer. It is a small visual defect, not a correctness one, and
  it is strictly better than the pre-state (where all dots were discarded). But it is an undeclared
  rule in a function whose whole point is a declared composition order.
- **Suggested fix:** either state it in the `_braille` docstring (*"where two dots share a cell the
  first written tone wins"*) and leave the code alone — the cheap, honest option — or give the
  active path priority by having `radial.py` write its `on_path` edges last and switching
  `setdefault` to a plain assignment. Do not leave it undeclared.

---

### F9 — the packet's coercion baseline is off by one  [Severity: LOW]

- **What:** `increment-001.md:42` says `plain()` widened *"from 62 to 85 covered code points"*.
  Measured: the `5d8ee0d` map covers **63** (30 C0 + 33 for `0x7F..0x9F`). A-80's own arithmetic
  agrees — it states `+22` newly covered, and `85 − 22 = 63`.
- **Where:** `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-001.md:42`.
- **Why it matters:** Nothing in the code or the tests depends on it; it is a transcription error in
  a document whose value is that its numbers were read off a run. Worth correcting precisely
  because the increment's thesis is that hand-typed numbers drift.
- **Suggested fix:** `62` → `63`.

---

### F10 — `no_test_retypes_the_range_list` uses the weaker commit its sibling argues against  [Severity: LOW]

- **What:** `tests/test_darkside_census.py:492-499` derives its sweep from
  `(REPO / "tests").glob("*.py")` — **non-recursive**, so a `tests/<subdir>/` module is invisible —
  and gates it on `assert len(candidates) > 30`, a floor. `test_llr_s06_3_1` at `:67-83`, in the
  same file, argues in its own docstring that a floor *"sits comfortably above … and ships a census
  with holes"* and asserts a **set** instead. The regex also matches on the **name**
  (`^\s*COERCION_RANGES\s*=`), so a retyped copy under any other identifier passes.
- **Where:** `tests/test_darkside_census.py:492`, `:493`, `:497`.
- **Why it matters:** The clause is genuinely useful and its `Path(__file__) in candidates`
  self-inclusion check is a good touch. The inconsistency is with the standard the same file sets
  30 lines earlier.
- **Suggested fix:** `rglob("*.py")` instead of `glob`, and replace the floor with a set comparison
  against the tracked test files plus the untracked additions, mirroring `:76-82`. For the name
  hole, additionally sweep for a retyped **value**: assert no test file outside `darkside.py`
  contains the literal `0x061C` or `0xFFF9`.

---

### F11 — `HEX` cannot see an 8-digit colour  [Severity: LOW]

- **What:** `HEX = re.compile(r"#[0-9a-fA-F]{6}\b")` (`tests/test_darkside_census.py:96`).
  Executed: `HEX.findall("color: #1783ffcc;")` → `[]`. The trailing `\b` fails between `f` and `c`,
  and there is no second `#` to restart from.
- **Where:** `tests/test_darkside_census.py:96`, consumed by
  `_assert_hue_set_is_exactly_the_declared_tokens` at `:113`.
- **Why it matters:** `test_hue_census_no_undeclared_hue_ships` is the clause that found
  `#a3a3a3`. An undeclared hue written with an alpha channel — a plausible form in the Textual CSS
  blocks inside `app.py` and `screens/*.py`, which is where 6 of the 8 blue literals already live —
  is invisible to it.
- **Suggested fix:** `HEX = re.compile(r"#[0-9a-fA-F]{6}(?![0-9a-fA-F])")`, and add a positive
  control beside the existing ones: `assert HEX.findall("#1783ffcc") == []` is the *current*
  behaviour; assert instead that an 8-digit literal is either matched or explicitly rejected with a
  stated reason.

---

### F12 — the census cannot run outside a git checkout  [Severity: LOW]

- **What:** `tracked_sources()` (`:60-63`) and `_tracked_view_sources()` (`tests/test_canvas.py:56-59`)
  shell out to `git ls-files` with `check=True`. No `git` on `PATH`, or an exported source tree,
  turns 9 census nodes into errors rather than skips.
- **Where:** `tests/test_darkside_census.py:60`, `tests/test_canvas.py:56`.
- **Why it matters:** Low today (the suite is run from the checkout). Recorded because `LLR-S06.3.1`
  deliberately names the command, so this is a consequence of a correct decision, not a mistake —
  it just needs a stated environment precondition.
- **Suggested fix:** one line in each module docstring: *"requires a git checkout on `PATH`;
  `LLR-S06.3.1` names the command deliberately."* No code change.

---

## What I looked for and did NOT find

Recorded so the absence is on the record rather than implied.

- **No over-engineering.** Answering your item 8 directly: `_braille`, `_tone` and `rows` are each
  the minimum that does the job. There is no speculative generality, no unused parameter, no
  abstraction for single-use code. `SURFACES` as a declared 4-name frozenset with a derived
  `semantic_tokens()` is the right split — the boundary is the judgement, the pairs stay derived.
  I found **nothing else to delete.**
- **No duplication of an existing util.** `_lab`/`_ciede2000` in the census are ~50 lines of new
  colour maths, but nothing in `mapper/` or `tests/` already implements them and they belong in the
  test that quantifies the floor, not in the product.
- **No `_tone` gap on `cells` / `_wire_tones`.** The guard is scoped to `dots` and `bgs`, which is
  what `LLR-CNV.1.4` says and what the class docstring declares. Correct as scoped.
- **The out-of-bounds guard's discharge is real.** You were right that it was inert: `rows()` only
  looks up in-range cells, so no assertion over painted output can separate the two
  implementations. Asserting on `_braille()`'s returned mask directly (`tests/test_canvas.py:190-195`),
  with the in-range positive control beside it, is the correct discharge.
- **`AT-009`'s on-disk oracle is sound.** Comparing an on-disk code-point count against the
  on-screen count, both computed at run time, with a same-oracle negative control on
  `LayeredRenderer`, is materially stronger than the `size > 0` it replaced. The `_disk_braille`
  docstring's caveat about per-style-run `<text>` spans is correct and non-obvious.
- **The register key is sound.** Keying on `(path, stripped line)` rather than line number is the
  right trade, and the totality clause is **real**: `_sites` returns a list, so a new site whose
  stripped text duplicates a registered one does not slip past — it moves `len(sites)` off 36 and
  reddens the count assertion. I checked the three evasions (move a site, delete-plus-add, add a
  textual duplicate) and all three redden.

---

## Evidence checklist

- [x] **Diff read in full** — `mapper/canvas.py:1-146`, `mapper/darkside.py:1-90,353-385`,
      `mapper/views/radial.py:100-259`, `mapper/app.py:876-882`, `docs/ARCHITECTURE.md:68,160`,
      `tests/test_canvas.py:1-316`, `tests/test_darkside_census.py:1-500`,
      `tests/test_radial.py:1-115`, `tests/test_export.py:1-110`,
      `tests/test_repair_depth.py:99-116`, `01-requirements.md` amendment set 4.
- [x] **Correctness pass (edge / None / error paths)** — `_DOT_BITS` verified against the Unicode
      dot numbering; negative sub-cell coordinates verified dropped; `int()` truncation verified
      unreachable via the clamps at `radial.py:142-143`; `style is None` path verified byte-identical.
      **Defect found: F1** (`canvas.py:141`).
- [x] **Simplicity pass** — no premature abstraction found; the deleted defensive branch was
      correctly deleted and its removal independently re-measured against `rich.text.Text.append`.
      Nothing further to delete.
- [x] **Reuse / duplication checked** — F6 (`TOKEN_JOB` vs `darkside.__doc__`) and F2 (two
      ARCHITECTURE rows describing one constructor) are the two live duplications.
- [x] **Tests reviewed for intent** — F1 (`test_canvas.py:115` dodges the default wire tone),
      F3 (`test_darkside_census.py:222` narrower than its name), F6 (`M-S06.3.5-a` mutates the
      test's own table), F4 (no guard on the injected policy's default).
- [x] **Independent re-derivation of the goldens** — clean `git worktree` at `5d8ee0d`; recipe
      re-implemented from `_fingerprint`; 4 moved / 8 held confirmed; recipe and `fixtures/`
      unchanged; worktree removed; repo tree untouched.
- [x] **No file under `mapper/`, `tests/` or `docs/` edited.** No mutating git command run.
      `prototypes/` untouched and unstaged.
- [x] **Verdict explicit** — below.

---

## Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **Block — must fix HIGH findings before advancing**

**F1 blocks.** It is three lines in `mapper/canvas.py` plus one test arm, it moves no digest, and
the missing arm is written out above. **F2 should ride with it** — it is a one-line doc edit and
leaving the map self-contradicting for a batch is how the `2026-08-27-repair-batch-02` correction
gets made twice.

**F3–F6 are recommendations, not blockers**, but F4 and F6 have short fixes and both harden
guarantees `Inc-2` and `Inc-5` are about to lean on. F5 needs a decision recorded before `Inc-5`
applies `B-38` mechanically.

**On F1's severity, stated plainly so you can overrule me knowingly:** the defect is **not
reachable in the product today** — `radial.py` is the only `bgs` writer and it never calls
`cv.wire`. If you judge reachability the governing criterion, F1 is a MEDIUM and the increment
passes with fixes. I am not recommending that, for the three reasons in F1, and chiefly this one:
`docs/ARCHITECTURE.md:160` now publishes *"a `bgs` background applies to whichever glyph won"* as
the module's contract, and that sentence is false for the module's own default value. A published
false contract with a three-line fix is worth one more turn.

**Everything you asked me to attack, I re-executed rather than reasoned about.** Your `_DOT_BITS`
table, your negative-coordinate handling, your `Text.append` measurement, your 85/0/0 coercion
claim, your four re-baselined digests and your eight held ones are all **correct as stated** — the
digests independently, from a clean worktree, with the recipe re-implemented rather than imported.
The one place you were wrong is the one you asked about first: the background-application rule does
misfire on a legitimate style, and it is the one your own `Canvas.wire` hands it by default.

*Hand-offs: no security-relevant change found in this diff (the coercion widening is a security
**improvement**, and `security-reviewer` owns the hostile-title surface if you want it read).
No suite-execution or coverage gaps beyond F3/F4 — `qa-reviewer` owns the `Inc-2` re-run obligation
the packet records at §5.5.*
