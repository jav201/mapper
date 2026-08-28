# Security Review — Inc-1 (`S-6` paleta v2 · `HLR-CNV.1` Canvas A3 · `LLR-COERCE.1`)

| | |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Branch | `feat/ui-next-batch-02`, base `5d8ee0d` |
| Reviewed | working tree, uncommitted |
| Environment | Python 3.12 · rich 15.0.0 · textual 8.2.8 · Windows · `PYTHONUTF8=1` |
| Files in scope | `mapper/darkside.py`, `mapper/canvas.py`, `mapper/views/radial.py`, `mapper/app.py`, `tests/test_export.py`, `tests/test_canvas.py`, `tests/test_radial.py`, `tests/test_darkside_census.py` |
| Verdict | **OK to ship with mitigations** for **Inc-1**. **Two HIGH findings block BATCH CLOSE**, neither introduced by this increment. |

No file under `mapper/`, `tests/` or `docs/` was modified. No mutating git command was run. No live
`MapperApp` was started; every probe built its own graph in memory or in a `tempfile.mkdtemp()`.
Every hostile input was constructed with `chr(0x…)` at run time.

---

## 1 · The four claims, independently re-executed

All four hold. Numbers below were produced against the working tree, not read from `A-80`.

### 1.1 Strict widening — **CONFIRMED, all four arms**

```
declared ranges: 12
unique code points: 85          <- claim: 85          ✓
sum of range widths: 85         (no overlap between ranges)
overlapping/duplicated points: []
survivors of plain(): []        <- claim: 0           ✓
_CONTROL_MAP size: 85 ; keys == points: True ; all values '�'
U+0009 preserved: True          <- claim: preserved   ✓
U+000A preserved: True          <- claim: preserved   ✓
U+000D coerced:   True
```

Against the shipped map reconstructed from `5d8ee0d:mapper/darkside.py:272-273`
(`range(0x00,0x20)` minus `{0x09,0x0A}`, plus `range(0x7F,0xA0)` = 63 points):

```
base size 63 ; new size 85
LOST (covered at 5d8ee0d, not now): []      <- claim: 0            ✓
newly covered: 22
  U+061C U+200B U+200C U+200D U+200E U+200F U+2028 U+2029
  U+202A U+202B U+202C U+202D U+202E U+2060 U+2066 U+2067
  U+2068 U+2069 U+FEFF U+FFF9 U+FFFA U+FFFB
```

The change is a **strict superset**. `A-80`'s figures reproduce exactly.

### 1.2 The near-miss — **CONFIRMED FIXED**

`mapper/darkside.py:368` reads `(0x0000, 0x0008), (0x000B, 0x001F)` — 30 points, not the sealed
table's 29. `plain(chr(0x0D)) == '�'`. CR coverage that shipped at `5d8ee0d` is retained.

### 1.3 Other omissions of the same shape in §3.0's table — **ONE FOUND**

Two shapes were checked mechanically, not by reading.

**Shape A — label implies more points than the row enumerates.** Row arithmetic re-derived:

| Row | Enumerated | Label implies | Match |
|---|---|---|---|
| C0 except TAB and LF | 29 | 30 | **NO — the known near-miss, fixed** |
| DEL and C1 | 33 | 33 | ✓ |
| Bidi marks | 3 | 3 | ✓ |
| Bidi embedding and override | 5 | 5 | ✓ |
| Bidi isolates | 4 | 4 | ✓ |
| Zero-width and invisible | 5 | — (open-ended label) | see Shape B |
| Line and paragraph separators | 2 | 2 (Unicode `Zl` ∪ `Zp` is exactly these) | ✓ |
| Interlinear annotation | 3 | 3 | ✓ |

The table's stated total of 84 = 29+33+3+5+4+5+2+3 is internally consistent, so the C0 row is the
**only** Shape-A defect. The table sums correctly to a wrong number — which is why arithmetic alone
never caught it.

**Shape B — the label names a character class and the enumeration omits members of it.** Checked
against Unicode properties rather than against the table. Bidi rows are complete: Unicode
`Bidi_Control` is exactly `{U+061C, U+200E, U+200F, U+202A–U+202E, U+2066–U+2069}` = 12 points, all
12 covered. `Zl`/`Zp` fully covered. `Cc` fully covered except the two deliberately preserved.
**`Cf` (format) is not**: 150 of Unicode's 170 `Cf` code points are uncovered — see **F4**.

### 1.4 `tokens()` and `globals()` — **no external influence path**

`tokens()` filters `mapper.darkside`'s own module namespace to `str` values matching
`^#[0-9a-fA-F]{6}$` on non-underscore uppercase names, and returns exactly the 14 palette names.
`grep` for `exec(`, `eval(`, `setattr(`, `__dict__`, `importlib` over `mapper/` returns **one** hit:
`darkside.py:84`, the comprehension itself. Nothing in the tree writes a module attribute, and no
file-derived value can reach a module namespace. `MUT` (the fallback) is in `tone_set()`; all three
`_GREYS` are in `tone_set()`. The residual is the ordinary Python one — any in-process code can do
`darkside.X = "#000000"` — which requires code execution, at which point the guard is not the
control that matters. **No finding.**

---

## 2 · Findings

### F1 — a ficha title reaches a Textual **markup-parsing** sink on the destructive-action confirmation dialog  ·  **[Severity: HIGH]**

- **What.** `MapScreen.action_archive` binds `name = node.ficha.title or node.id` **uncoerced and
  unescaped**, interpolates it into the confirmation copy, and hands the result to `_ConfirmScreen`,
  whose `compose` yields `Static(self.message)`. `Static.__init__`'s signature in textual 8.2.8 is
  `(content, *, expand=False, shrink=False, markup=True, …)` — **`markup=True` is the default** — so
  the message is parsed by `Content.from_markup`.
- **Where.** `mapper/app.py:1814` (the bind) → `:1828-1834` (the three message forms) → `:1836`
  (the push) → `mapper/app.py:166` (`Static(self.message, id="confirm-label")`).
- **Executed evidence** (the exact message shape from `app.py:1833`):

  ```
  'acta [/b] final'                      -> RAISES MarkupError: closing tag '[/b]' does not match any open tag
  'acta [@click=app.quit]CONFIRMAR[/] x' -> parsed; injected spans: [Span(16, 25, style='@click=app.quit')]
  'acta [red]rojo[/]'                    -> parsed; injected spans: [Span(16, 20, style='red')]
  ```

- **Why it matters.** Two distinct attacks on the **one dialog that gates subtree archival**:
  1. A title containing any stray closing tag raises `MarkupError` while composing the confirmation
     screen — the confirmation gate on a destructive action is destroyed by the very data it is
     asking about.
  2. `[@click=…]` injects a **live action span** into the confirmation text. The operator reads a
     plausible "¿archivar «X» y sus N descendientes?" carrying a crafted clickable region bound to an
     arbitrary Textual action.
- **Not covered by `S-09`.** `S-09` enumerates thirteen `notify()` sites (`app.py:626, 640, 661,
  666, 729, 1022, 1024, 1027, 1682`; `factory.py:350, 371, 395, 397`). `_ConfirmScreen`'s `Static`
  is not among them and is a different sink class. This is a new finding.
- **Sharpest detail.** `app.py:1807`, **seven lines above the defect and inside the same function**,
  already reads `self._event_toast("archivado", darkside.plain(node.ficha.title or node.id))`. The
  discipline was applied and then dropped on the path that guards the destruction.
- **Recommendation.** Both arms — `S-09`'s `M-N1`/`M-N2` mutants apply here unchanged:
  ```python
  # app.py:1814
  name = darkside.plain(node.ficha.title or node.id)
  # app.py:166
  Static(self.message, id="confirm-label", markup=False),
  ```
- **Not introduced by Inc-1.** Inc-1's only `app.py` change is `WARN` → `PULSE` at `:879`.
- **Honest limit.** I established the sink parses markup and that the payload reaches it; I did
  **not** drive a live `MapperApp` (rules of engagement), so whether the `MarkupError` surfaces as a
  hard app crash or is caught by a Textual boundary is **unverified**. The `[@click=…]` arm does not
  depend on that question.

### F2 — `views/outline.py` is a second uncoerced feeder of `save_svg`, and it is assigned to **no** coercion increment  ·  **[Severity: HIGH]**

- **What.** The brief asks whether `views/layered.py::_fit` is the only remaining uncoerced painted
  sink. **It is not.** `LLR-COERCE.2` is scoped verbatim to `mapper/views/layered.py::_fit`
  (`01-requirements.md:420`, `:425`, `:5458`, `:7001`). `views/outline.py` imports `darkside` but
  never calls `plain` or `fit` on any file-derived value, and **`OutlineRenderer` is one of the three
  renderers `MapScreen._current_renderer()` can return into `save_svg`.**
- **Where.**
  - `mapper/views/outline.py:125` — `line.append(node.ficha.title, style=block)`
  - `mapper/views/outline.py:128` — `line.append(node.ficha.title, style="bold")`
  - `mapper/views/outline.py:141` — `line.append(f"  {node.ficha.meta}", …)`
  - `mapper/views/layered.py:38` (`_fit`) — confirmed: `_clip` + space-pad, no coercion at all;
    feeding `:217`, `:227/230`, `:237`, `:247`, `:280`, plus a bare `Canvas.put(sf.key, …)` at `:242`
  - `mapper/views/lane.py` — 9 uncoerced sites (`:101, 132, 136, 137, 140, 151-153, 229, 290, 349`),
    of which `:137` (`ficha.meta`) is not even `escape`d
  - dispatch: `mapper/app.py:1265-1270` → `mapper/app.py:1721-1738` (`action_export_svg`)
- **Executed evidence.** Same hostile title
  (`"acta"+chr(0x1B)+"]52;c;aGk="+chr(0x07)+"fin"+chr(0x202E)+"gpj.exe"`) through all three
  renderers, each written to a real file in a `mkdtemp()`:

  ```
  outline  ESC_in_svg=True  RLO_in_svg=True  xml=NOT well-formed (invalid token, line 66)
  layered  ESC_in_svg=True  RLO_in_svg=True  xml=NOT well-formed (invalid token, line 134)
  radial   ESC_in_svg=False RLO_in_svg=False xml=well-formed
  ```

- **Why it matters.** `AT-009`'s guarantee is real but holds **only while the operator is in radial
  view**. Layered is the default renderer. Two concrete outcomes on an artifact that leaves the
  machine: a raw `U+001B` produces an SVG that is **not well-formed XML**, so `cairosvg` and every
  downstream viewer reject the delivered file; a `U+202E` produces a **silently reordered** exported
  artifact — `S-04`'s spoof, now durable in a file handed to a client. Under LFPDPPP this is a client
  deliverable leaving the operator's control in a state the operator cannot see is wrong.
- **Recommendation.** Do **not** hand-list the fix. Widen `LLR-COERCE.2` to name the renderer **set**,
  and replace `AT-009` with a parametrised arm derived from what `_current_renderer()` can return, so
  a fourth renderer added later cannot silently escape the assertion:
  ```python
  @pytest.mark.parametrize("R", [LayeredRenderer, OutlineRenderer, RadialRenderer, *LANE_RENDERERS])
  def test_at_009b_no_renderer_writes_a_coerced_code_point(R, tmp_path): ...
  ```
  Assign `views/outline.py` and `views/lane.py` to an increment. Today they belong to none.
- **Not introduced by Inc-1.**

### F3 — `AT-009`'s oracle cannot detect an under-inclusive `COERCION_RANGES`  ·  **[Severity: MEDIUM]**

- **What.** `tests/test_export.py` derives `banned` from `darkside.COERCION_RANGES` — the same
  constant `_CONTROL_MAP` is derived from. `plain()` translates exactly `_CONTROL_MAP`'s keys.
  Therefore `leaked == []` is true **for any value of `COERCION_RANGES` whatsoever**, provided the
  coercion is applied at all. The test proves *"radial routes the title through `plain()`"*, which is
  a routing test. It does **not** and cannot prove *"the SVG carries no dangerous code point"*, which
  is what its name and docstring assert.
- **Where.** `tests/test_export.py:105-110` (the `banned` comprehension and the `leaked` assertion).
- **Why it matters.** This is `A-80`'s own lesson recurring one artifact later: *"the Phase-0 probe
  agreed because it was fed the spec's own ranges, validating the list against itself."* `AT-009`
  validates the list against itself too. **Demonstrated:** `pytest tests/test_export.py … -q` →
  `73 passed`, green, while my independent probe shows **19 invisible code points** reaching that
  same SVG (F4). The suite is green on an artifact carrying the payload.
- **Recommendation.** Add an oracle keyed on something the implementation does not define. The
  cheapest independent one is Unicode's own classification:
  ```python
  import unicodedata as u
  survivors = sorted({ord(c) for c in raw if u.category(c) in ("Cf", "Zl", "Zp")})
  assert survivors == [], f"invisible format code points reached the SVG: {survivors}"
  ```
  If any are deliberately preserved, they belong in a **declared, reviewed allowlist** in the test —
  written down as a decision, not inherited from the coercer.

### F4 — the *"Zero-width and invisible"* row is under-inclusive against its own stated rationale; 19 invisible code points reach the screen and the exported SVG  ·  **[Severity: MEDIUM]**

- **What.** §3.0's row gives the reason *"text that occupies no cell but changes matching"* and then
  enumerates only `U+200B–U+200D, U+2060, U+FEFF`. Unicode's `Cf` class has 170 members; 150 are
  uncovered. Notably `(0x2060, 0x2060)` **stops one code point short** of the contiguous invisible-
  operator run `U+2061–U+2064` — structurally the same *"stops short"* shape as the CR near-miss,
  in the adjacent row.
- **Where.** `mapper/darkside.py:373` (`(0x200B, 0x200D), (0x2060, 0x2060), (0xFEFF, 0xFEFF)`);
  `01-requirements.md` §3.0 range table, *Zero-width and invisible* row.
- **Executed evidence.** Eleven hostile titles through `RadialRenderer` → `save_svg` → disk. Banned
  set: clean. Then scanning the same file for `unicodedata.category ∈ {Cf, Zl, Zp}`:

  ```
  U+00AD SOFT HYPHEN
  U+180E MONGOLIAN VOWEL SEPARATOR
  U+2061 FUNCTION APPLICATION   U+2062 INVISIBLE TIMES
  U+2063 INVISIBLE SEPARATOR    U+2064 INVISIBLE PLUS
  U+206A–U+206F  (6 deprecated format controls)
  U+E0001 LANGUAGE TAG
  U+E0045 U+E0047 U+E0049 U+E004E U+E004F U+E0052   <- the ASCII "IGNORE", invisible
  ```

  All 19 reach **both** `text.plain` (the screen) and the written `.svg`.
- **Why it matters.** The `U+E0000` TAG block (97 code points) is the one with a real story: it
  renders as nothing in every browser, editor and terminal, and each point maps 1:1 onto an ASCII
  character. A ficha title can therefore carry an arbitrary hidden ASCII string into a client-
  delivered SVG, invisible to the operator who exports it and to the client who opens it, and fully
  recoverable by anything that reads the file as text — including a downstream LLM. `U+00AD` and the
  zero-width family defeat exactly the *"changes matching"* property the row's own rationale names.
- **This does NOT block Inc-1.** Base coverage at `5d8ee0d` was zero for all 19; Inc-1 is a strict
  improvement and satisfies the sealed requirement **as written**. The defect is in the sealed row,
  not in the implementation of it.
- **Recommendation.** Prefer the derived form over five more hand-typed ranges, so the list stops
  drifting from Unicode:
  ```python
  PRESERVED = frozenset({0x0009, 0x000A})   # declared, with a reason each
  COERCED = frozenset(
      cp for cp in range(0x110000)
      if unicodedata.category(chr(cp)) in ("Cc", "Cf", "Zl", "Zp")
  ) - PRESERVED
  ```
  If the literal-range form must stay for reviewability, the minimum honest widening is
  `(0x00AD,0x00AD)`, `(0x180E,0x180E)`, `(0x2060,0x2064)`, `(0x206A,0x206F)`, `(0xE0000,0xE007F)` —
  and either way the row's label must be brought back into agreement with its contents.

### F5 — remote-derived text (git commit subject and author) is painted with no coercion  ·  **[Severity: MEDIUM]**

- **What.** The repo screen paints a node's `title`, `meta` and `notes` through `darkside.time_row`,
  which assembles them into a `Text` with **no `plain` and no `escape`**. For repo-derived graphs
  those three fields are populated from `git`.
- **Where.** `mapper/app.py:997-1005` (the bind and the `_time_row` call) →
  `mapper/darkside.py:338, 347` (`Text.assemble` of `name` and `note`). Source:
  `mapper/github.py:191` (`notes = f"{info['author']} {date_str}"`), `:196` (`title=bname`),
  `:221` (`notes=info.get("subject", "")`).
- **Why it matters.** This is the **widest blast radius of the whole class** in this tree. Every other
  uncoerced sink is fed by a file the operator owns. Here the input author is *anyone who has landed
  a commit or a branch or a tag in a repository the operator opens* — a third party. `git log`
  returns the raw subject; a commit subject carrying `U+001B]52;c;…U+0007` is an OSC-52 clipboard
  write into the operator's terminal, and `U+202E` in a branch name reorders the row that reports it.
- **Recommendation.** `darkside.plain()` on `name`, `meta` and `note` at `app.py:997-1004`, or —
  better, because it cannot be forgotten by the next caller — inside `time_row` itself
  (`darkside.py:338, 347`). Note `time_row` is a `darkside` primitive, so coercing there matches how
  `hint_line` (`darkside.py:261`) and `fit` (`:400`) already behave.
- **Not introduced by Inc-1.**

### F6 — the tone guard's own default reproduces the failure the guard exists to prevent  ·  **[Severity: LOW]**

- **What.** `fallback: str = ""`. A caller who passes `tones=` and forgets `fallback=` gets a guard
  that rejects the bad tone and then paints it **unstyled** — which `_tone`'s own docstring names as
  the failure mode: *"a bad tone silently paints unstyled, which is indistinguishable from a tone
  that was never applied."*
- **Where.** `mapper/canvas.py:50` (the default), `:91-100` (`_tone`).
- **Executed evidence.**
  ```
  Canvas(1,1, tones=d.tone_set())                    -> rejected tone paints style ''
  Canvas(1,1, tones=d.tone_set(), fallback=d.MUT)    -> rejected tone paints '#737373'
  malformed SPAN style through rich 15.0.0           -> swallowed, no raise   (the fail-open is real)
  ```
- **Second half — the guard prevents but does not detect.** `radial.py:124` chooses `MUT` as the
  fallback. `MUT`'s declared job is *"secondary or dimmed text, and **absent information**"*. A
  rejected tone therefore paints as a **meaningful, plausible** token: the failure becomes invisible
  rather than merely unstyled. My decision rule is detection > prevention > recovery, and this
  control has prevention with zero detection.
- **Recommendation.** Make the pair atomic and give the failure a signal:
  ```python
  if tones and not fallback:
      raise ValueError("a tone policy requires a fallback; '' reproduces the fail-open")
  ```
  and consider `ALERT` rather than `MUT` as `radial.py:124`'s fallback — a tone that looks *wrong*
  is what turns a silent substitution into a bug report.

### F7 — the guard is opt-in, and two of the three `Canvas` constructions do not opt in  ·  **[Severity: LOW]**

- **What.** `Canvas(w, h)` applies no tone policy. `mapper/views/lane.py:197` and
  `mapper/views/layered.py:196` construct exactly that.
- **Why it is only LOW.** No live exposure: `grep` confirms `dots` and `bgs` are written from
  **exactly two sites in the tree**, both in `radial.py` (`:210` `cv.dots[…] = hue`, `:229`
  `cv.bgs[…] = pill_bg`), and both values are `darkside` constants or `_GREYS` members indexed by an
  integer — **the brief's premise that layer tones are not file-derived still holds after this
  change.** The default is also *declared and tested*
  (`test_tc_cnv_1_4_an_unset_tone_policy_passes_every_value_through`), not an oversight, and `A-81`
  records why injection was chosen over an import. The guard is **not bypassable** as built: `rows()`
  is the only reader of `dots`/`bgs`, so `radial.py`'s direct dict assignment cannot route around it,
  which is exactly what `S-10`'s `M-V1` mutant warned about. **Inc-1 discharges `S-10` correctly.**
- **Residual.** *"The system must enforce, not the human"* — a future renderer that writes `dots` or
  `bgs` and forgets `tones=` gets zero guard and zero signal.
- **Recommendation.** F6's `ValueError`, plus a census in `tests/test_canvas.py` — derived from the
  tree, in the style already used at `test_canvas.py:61-84` — asserting that every `Canvas(`
  construction under `mapper/views/` that also writes `dots`/`bgs` passes `tones=`.

### F8 — the two truncators now disagree on a second axis: cells versus code points  ·  **[Severity: LOW]**

- **What.** `darkside.fit` measures in **display cells** (`Text.cell_len`, `darkside.py:402-406`).
  `radial.py:223-224` slices in **code points** (`plain(...)[:18]`) and then sizes the pill with
  `cw = len(title) + 3`, also code points.
- **Where.** `mapper/views/radial.py:223-224`.
- **Why it matters.** A CJK or emoji title of 18 code points occupies ~36 cells, so the pill
  background (`cw = 21` cells, `:228-229`) covers roughly half the glyphs it is meant to sit behind,
  and the overflow is clipped by `Canvas.put`'s bounds check rather than laid out. Not a security
  boundary — no injection, no escape — but the batch is currently reconciling exactly one property
  between the two truncators (coercion order) while a second one silently disagrees.
- **Recommendation.** Out of Inc-1's scope. File as a carry alongside `B-38`–`B-42`; the natural fix
  is `darkside.fit(node.ficha.title, 18)`, which is cell-correct and coerces in the same call.

---

## 3 · Cleared — checked and found clean

| Question | Result |
|---|---|
| **Markup / entity / `<a>` / `<script>` injection into the SVG** | **Impossible.** rich escapes every text run through `html.escape` + nbsp (`rich/console.py:2446-2448`, applied at `:2530`); `title=` is hard-coded `"mapper"` at `export.py:19` and escaped at `:2572`. `get_svg_style` (`:2386-2415`) emits only `fill` / `font-weight` / `font-style` / `text-decoration` from a **typed** `Style`; class names are `r{N}` counters and `unique_id` is an `adler32`. rich's SVG exporter emits **no** `<a>`, `<title>`, `<desc>` or `<foreignObject>`, and **drops `Style.link` entirely**. Measured with a breakout payload through `RadialRenderer` → `save_svg`: `ET.fromstring` parses, element tags are exactly `{circle, clipPath, defs, g, rect, style, svg, text}`, and `<script` / `onload=` / `javascript:` / `<a ` / `xlink` are all absent while `&lt;` `&amp;` `&quot;` are present. |
| **Can a file-derived value reach a *style* slot** (and so a `link` style / OSC-8)? | **No.** Every style in `radial.py` is a `darkside` constant or an f-string over constants (`:230, 237, 239, 243, 245, 247, 249`). `Canvas.put`'s style parameter is unguarded and `_wire_tones` is unguarded, but no caller in the tree passes file-derived text to either. |
| **`save_svg` path traversal** | **Not reachable from file content.** `app.py:1734` builds `self.store.workspace / f"{self.map_id}.svg"`, and `map_id` originates from `Path.stem` of `workspace.glob("*.mmd")` (`app.py:421, 476, 489, 559`) — a stem cannot contain a separator. The one operator-typed name (`app.py:763`, "guardar como") is operator input, not attacker input, and is unvalidated; worth a `Path.name` normalisation someday, not a finding here. |
| **Secrets / credentials** | **None.** `grep -inE 'api[_-]?key\|secret\|token\|password\|bearer\|-----BEGIN\|ghp_\|sk-\|AKIA\|client_secret'` over the full diff returns only the design-system sense of *"token"*. |
| **Dependencies / supply chain** | **No change.** `pyproject.toml` is untouched by the diff; no new import outside the stdlib and the already-pinned rich/textual. |
| **Raw control bytes committed to source** | **None.** All seven changed/new files scanned: 0 banned code points (beyond TAB/LF/CR line endings) and 0 `Cf`/`Zl`/`Zp` characters. The *"written as a number, never as the character itself"* claim at `darkside.py:363` holds. |
| **Destructive command surface in the diff** | None. No deletion, migration, force-push or schema change. |
| **`_CONTROL_MAP` construction** | Sound. 85 keys, no range overlap, every value `U+FFFD`, `str.translate` over an int-keyed dict. |

---

## 4 · Verdict

- [ ] OK to ship
- [x] **OK to ship with the listed mitigations applied first — for Inc-1**
- [ ] Block

**Inc-1 gets a security sign-off.** Nothing in this increment's change set is HIGH. It is a strict
widening with zero coverage lost, it discharges `S-10` by the exact mechanism `S-10` prescribed
(`M-V1` avoided — the guard is in `rows()`, and `radial.py:210`'s direct dict write cannot route
around it), and it discharges `S-12` for the one renderer it owns. `F6`, `F7` and `F8` are LOW and
may be carried. **`F3` should be applied before merge** — it is a five-line test change and it is the
only reason the tree currently reports green on an artifact carrying a live payload.

**This is not an "OK despite a HIGH".** `F1` and `F2` are HIGH and are **outside Inc-1's change
set** — `F1` predates the branch and `F2` is a scope gap in the sealed requirement, not a defect in
what was written. Blocking Inc-1 over them would revert a strict improvement and leave the tree
strictly worse. They are therefore raised as **batch-close blockers with owners**:

| Finding | Gate | Owner needed |
|---|---|---|
| **F1** `_ConfirmScreen` markup sink on the archive confirmation | must be fixed before the batch closes | unassigned — not in `S-09`'s site list, needs a new id (`S-15`?) and an increment |
| **F2** `views/outline.py` + `views/lane.py` uncoerced, and `outline` feeds `save_svg` | must be fixed before the batch closes | `LLR-COERCE.2` is scoped to `views/layered.py::_fit` only; **outline and lane belong to no increment today** |
| **F3** `AT-009`'s oracle validates the list against itself | before Inc-1 merges | Inc-1 |
| **F4** `Cf` coverage gap incl. the `U+E0000` TAG block | a **decision** before the batch closes: widen, or record as accepted with a reason | `HLR-COERCE` |
| **F5** git commit subject/author painted uncoerced | before the batch closes | repo-screen increment |

`Inc-2` carries Inc-1's standing re-run obligation on `AT-007` and `AT-009`; if `F3`'s independent
oracle lands, that obligation becomes worth something. As it stands, re-running `AT-009` at `Inc-2`
would re-confirm a tautology.

---

## 5 · Evidence checklist

| Item | | Evidence |
|---|---|---|
| Each finding has what · where · why · recommendation | ✓ | F1–F8 above, each with a `file:line` |
| Each finding has a severity rating | ✓ | 2 HIGH · 3 MEDIUM · 3 LOW |
| No secret values appear in this output | ✓ | none found to reference; `grep` over the full diff returned only design-token matches |
| Verdict is explicit | ✓ | §4 — sign-off for Inc-1, `F1`/`F2` gated at batch close |
| New tool / integration scope and blast radius addressed | ✓ | n/a — no MCP, Composio, n8n or external connector in this diff; `pyproject.toml` untouched, no new dependency |
| Claims re-executed rather than read | ✓ | §1.1 census, §1.3 Unicode-property sweep, `F2` three-renderer on-disk probe, `F1` `Content.from_markup` probe, `F6` fallback probe — all against the working tree |
| Rules of engagement honoured | ✓ | no file under `mapper/`/`tests/`/`docs/` modified · no mutating git command · no live `MapperApp` · `fixtures/` never opened · every hostile input built with `chr(0x…)` in `tempfile.mkdtemp()` |
| Stated limits | ✓ | `F1`: crash-vs-caught behaviour of the `MarkupError` is **unverified** (no live app driven). `F2`/`F5` sink inventory was derived by an exhaustive tree sweep; I independently confirmed `outline.py:125/128/141`, `layered.py:38`, `app.py:997-1005`, `github.py:191/221` and `app.py:166/1814/1836` by reading the code and running the probes above. |
