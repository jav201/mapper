# Security Review — `Inc-CRUMB` (increment 008)

**Batch:** `2026-08-26-ui-next-batch-02` · **Reviewer:** independent (`security-reviewer`), SERIAL, sole writer
**Tree:** `C:\Users\jjgh8\Github\mapper` @ `57fb403` + working-tree diff (post-`F1`/`F2` fix tree)
Python 3.12 / Textual 8.2.8 / Windows, `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`

## VERDICT: **SIGN-OFF** — 0 HIGH

**The `escape()` removal is safe, and it closed more than it touched.** All three limbs of the claim
were executed and all three hold; and because the coercion moved from the *call site* into
`_crumb_line` itself, the **four crumb producers that never applied `plain`** are now coerced for the
first time. Pre-increment `tab_strip` applied only `escape`, which does not coerce a single control
code point — so `_ImportPreviewScreen`'s filename crumb, `RepoScreen`'s repo-name crumb and
`FactoryScreen`'s title crumb were all reaching the composited frame uncoerced, and now are not.
Measured: zero hostile code points on the frame at every width tried, on both screens.

The bound also holds as a **denial-of-service** control: a 4000-cell title at depth 8 leaves
`TabStrip` at ≤ 3 rows and the canvas at ≥ 11 rows at **every width from 20 to 200**, against the 54
rows / 0-row canvas the pre-increment tree produced.

Six findings, none HIGH, none blocking. Three are the increment's own seams (F1, F3, F5); three are
corrections to statements the increment or the code review makes about reachability and coverage
(F2, F4, F6).

---

## Scope reviewed

`git diff HEAD -- mapper/ tests/` — 467 insertions, 19 deletions, 5 files.

| file | reviewed |
|---|---|
| `mapper/darkside.py` | `tab_strip` 164-176, `_crumb_line` / `_cells` 179-259, `plain` 504-515, `fit` 518-525, `COERCION_RANGES` 455-495 |
| `mapper/app.py` | `_event_toast` 2149-2185, every one of the 11 call sites, CSS 3373-3394, `_current_crumb` 1702-1706, `action_open_ficha` 2618-2627, export sink 3095-3110 |
| `mapper/widgets/chrome.py` | `TabStrip` 13-27, `KeyBar` 30-94 |
| `tests/test_crumb.py`, `tests/test_fold.py` | read for oracle strength, not re-reviewed for correctness (code review covered it) |
| **beyond the diff** | **every** producer of a `crumb` list — `app.py:432, 807, 873, 936, 1235, 2383`; `screens/factory.py:129, 351`; `screens/settings.py:65` |

**Sole-writer discipline held.** No repo file was mutated. All five restore-to pins re-asserted
byte-identical at exit; `git status --porcelain` matches the entry state; `__pycache__` under
`mapper/` and `tests/` purged to 0. All probes were written to
`%TEMP%\secrev_crumb\` and run with the repo as cwd. No mutant was installed, so the
Windows/POSIX no-op hazard does not arise; the digest gate below is the control that says so.

```
5d2e9c885386fd490629d1428a57f4214e26b9b7370d4374f9ab63a743a5f2bc  mapper/app.py
e3c07df56591b4ddd48f953a21b88925ac7329cdb0feaad5e27f9655cafe1a7a  mapper/darkside.py
ccf06022cc630ae515d8be0b9ef6737ce86a4548dec7a956c9c2dea97d6d9847  mapper/widgets/chrome.py
bac799911d10c22898c93a837e80628f128adaf3fa859a10c64cc2e7e42fb639  tests/test_crumb.py
9a310d34edd9d585ffa5c6d39d76f003db9f0915362a77fdc40adf8c66627302  tests/test_fold.py
```

---

## Q1 — the `escape()` removal: all three limbs VERIFIED, and the census was widened

### Limb C — `Text.assemble` with `(str, style)` tuples does not parse markup. **TRUE.**

```
Text.assemble(("[bold red]X[/]", "dim")).plain  ->  '[bold red]X[/]'
spans: [Span(0, 14, 'dim')]
```

The text is appended literally and the style is applied as a span. There is no markup sink, so the
`escape` had nothing to protect and its backslash was painted. `darkside.plain`'s own docstring
(`:508-511`) already states this rule; `_crumb_line` now conforms to it.

### Limb B — `fit` coerces. **TRUE.**

`fit` calls `plain` at `darkside.py:520`, and `plain` translates every code point in
`COERCION_RANGES` to `U+FFFD`. Executed on four classes:

```
RLO   U+202E   -> U+FFFD      TAG   U+E0041 -> U+FFFD
NUL   U+0000   -> U+FFFD      ZWSP  U+200B  -> U+FFFD
```

`_crumb_line` routes **every** part through `fit` — the tail at `:224` and each ancestor at `:230` —
so coercion is unconditional and happens inside the helper, not at the caller.

### Limb A — `MapScreen` applies `plain` to every part. **TRUE**, at `app.py:2383-2385`.

### The census: SEVEN producers, not one — and four of them never applied `plain`

| # | site | crumb source | applied `plain` before? |
|---|---|---|---|
| 1 | `app.py:432` | literal | n/a |
| 2 | `app.py:807` | `self.source_path.name` — **a filename** | **no** |
| 3 | `app.py:873` | literal | n/a |
| 4 | `app.py:936` | `self.repo` — operator/remote-derived | **no** |
| 5 | `app.py:1235` | `self.source_crumb or [self.map_id]` — file-derived, link chain | **no** |
| 6 | `app.py:2383` | `_current_crumb() + [node_title]` | yes (the one the packet names) |
| 7 | `factory.py:351` | `[self.process_name, node_name]` — ficha title | **no** (it applies `escape`, which coerces nothing) |

**This is the security gain the increment did not claim.** Sites 2, 4, 5 and 7 previously reached
`tab_strip`, which applied `escape(part)` — a no-op against control code points — and rendered. A
hostile filename or repo name carrying `U+202E` or a `U+E0020..U+E007F` TAG payload reached the
composited frame. Post-increment every part passes `fit` → `plain`. Executed on two of them:

```
MapScreen, title 'nodo<U+202E>exe<TAG "SECRET"><U+200B>[b]x[/b]', cursor n3
  w=35/80/118   FRAME leaks = []   STRIP leaks = []
  painted: 'c consultar p repo n construir f fábrica ○ mapper c / nodo<U+FFFD>exe<U+FFFD>...['

_ImportPreviewScreen, filename 'mapa<U+202E>x*300.mmd'   (NO plain at the call site, set_crumb never called)
  w=35   TabStrip h=3  declared=True  leak=[]  tail='+1 … / mapa<U+FFFD>xxxxxxxxxxxxxxxxxxxxx…'
  w=50/60/80/118  same, leak=[]
```

Note the brackets survive literally (`[b]x[/b]`) — correct, and the point of Limb C.

The only remaining `escape`-inside-`Text.assemble` in `darkside.py` is `kind_chip` (`:373`), which
has **zero callers** repo-wide; it is dead code carrying the corrected-away pattern, not a live sink.

---

## Q4 — denial of service: the bound is sufficient, measured across widths

Real app, `MapperApp`, 4000-cell titles at depth 8, cursor at the deepest node:

```
w    h   TabStrip  canvas  KeyBar  toast  crumb_declared
20   24     3       11       1       1     False
24   24     3       11       1       1     False
28   24     3       12       1       1     False
30   24     3       12       1       1     False
31   24     3       12       1       1     False
33   24     3       12       1       1     False
35   24     3       13       1       1     True
40/50/60   3    14-15       1       1     True
62 .. 200  2    16-17       1       1     True
OUT-OF-BOUND WIDTHS: []
```

Against the packet's pre-gate (`h=54`, canvas 0 rows at 80x24), this is closed. `KeyBar` holds at
one row at every width, which is the `Inc-CRUMB` fix working.

**Crafted titles do not reach past the budget.** `_crumb_line` cell width vs budget, widths 20-129
(110 widths) × 8 hostile families — `T`×4000, `[b]`×1400, CJK×2000, `[`×4000, `U+202E`-runs,
TAG-block runs, combining-mark runs, emoji runs:

```
letters4000 breaches=0   brackets breaches=0   cjk2000 breaches=0   openbrk breaches=0
RLOrun      breaches=0   TAGrun   breaches=0   combining breaches=0  emoji   breaches=0
```

**Crafted depth does not either.** `source_crumb` at depth 2 / 20 / 100 / 200 / 600 × widths
35 / 50 / 60 / 80 / 118 — 25 configurations: `TabStrip` ≤ 3 rows in all 25, and the `+N …`
declaration is painted in all 20 where anything was dropped.

**The carried ≤ 31-column limit reproduces, and it is not MapScreen-specific.** At w=30 the crumb row
is evicted on `_ImportPreviewScreen` too (`declared=False`, only the wrapped tab row is painted). One
measured refinement to the carry: `_CRUMB_TAIL_MIN_CELLS = 12` floors `_crumb_line`'s output at **19
cells** for *any* budget below 19, so below ~20 columns the crumb is over budget on its own terms and
not only because the tab row wrapped. Both sit inside the region §8 already carries.

---

## Findings

### F1 — `TabStrip.__init__` still renders at the 118 fallback; only its sibling was fixed  [Severity: MEDIUM]

- **What:** `KeyBar.__init__` now resolves its width through `_width()` (widget → app → fallback).
  `TabStrip.__init__` does not: it calls `darkside.tab_strip(active, crumb)` with **no `width`**, so
  `_crumb_line` takes its `width <= 0` branch and budgets at 118 regardless of the terminal. The
  increment's §2 argument — *"a resize fires when the size CHANGES, so a layout that hands the widget
  its final width immediately never fires one"* — applies to `TabStrip` verbatim; it is saved only by
  starting at 0, which is a change.
- **Where:** `mapper/widgets/chrome.py:20`, against the fixed `:61` / `:63-80` four lines below it.
- **Executed:**

```
darkside.tab_strip("c", crumb=["anc", "T"*300])   # exactly what chrome.py:20 calls
  -> crumb row = 117 cells, at any terminal width
```

- **Why it matters:** it is a second 118-cell default in the file whose whole subject is that a bound
  must be in the cells the terminal actually has. **Not live today** — `on_resize` corrects it at
  every width measured (20-200 on `MapScreen`, 30-118 on `_ImportPreviewScreen`; `TabStrip` ≤ 3 rows
  throughout), which is why this is MEDIUM and not HIGH. It is a latent regression surface: any
  future layout that hands `TabStrip` its final width at construction reinstates `Inc-STRIPS`' F1.
- **Recommendation:** mirror the sibling.

```python
# mapper/widgets/chrome.py:20 — same rung ladder KeyBar._width() already uses
-        self.update(darkside.tab_strip(active, crumb))
+        self.update(darkside.tab_strip(active, crumb, width=self._width()))
```

  with a `_width()` lifted from `KeyBar` (or shared), returning `self.size.width` → `self.app.size.width`
  → 0 so `_crumb_line`'s own fallback stays the last rung.

---

### F2 — the code review's F5 reachability argument is false: `dropped` is not bounded at 2  [Severity: LOW]

- **What:** code review F5 rates the `_CRUMB_DROP_CELLS` under-reserve LOW because *"`_current_crumb`
  returns at most two elements, so `dropped ≤ 2`."* That holds only when `source_crumb` is `None`.
  `action_open_ficha` pushes `MapScreen(linked, source_crumb=self._current_crumb() + [title])`, and
  `_current_crumb` then returns `source_crumb + ["linked: <map_id>"]` — so **each link-follow adds two
  elements**, and `dropped ≈ 2N` after N follows.
- **Where:** `mapper/app.py:2624-2625` and `:1702-1706`, against the code review's F5 rationale.
- **Executed** — the under-reserve itself, widths 20-129:

```
depth=2     breaches=0          depth=100   breaches=110  max_over=1 cell
depth=9     breaches=0          depth=150   breaches=110  max_over=1 cell
depth=10    breaches=0          depth=999   breaches=110  max_over=1 cell
depth=99    breaches=0          depth=1000+ breaches=110  max_over=2 cells
```

- **Why it matters, and why it is still LOW:** the *reason* the carry gives is wrong, but the carry's
  *conclusion* survives measurement — the 1-2 cell overrun does not breach the lid in the real app
  (25 configurations up to `source_crumb` depth 600, all ≤ 3 rows, declaration painted). The defect
  is documentary, and this batch has paid three times already for a false declaration.
- **Recommendation:** keep F5 carried; replace its reason with the measured one — *"`dropped` grows
  with link-follow depth, not capped at 2; the 1-2 cell overrun at `dropped ≥ 100` was measured not to
  breach the 3-row lid up to depth 600 across widths 35-118."* Or apply the computed reserve the code
  review already drafted.

---

### F3 — the export handler's FAILURE arm does not pass the bounded seam  [Severity: LOW]

- **What:** `_event_toast`'s new docstring says the seam is *"One seam, both defects, every call
  site."* That is true of the eleven `_event_toast` sites. It is not true of the **export handler**,
  whose `except` arm renders through a different sink: `self.notify(f"exportación fallida: {e}", ...)`.
  For an `OSError` from `save_svg`, `str(e)` carries the absolute workspace path — the same path the
  success arm at `:3108` now routes through `fit`. 23 other `self.notify` sites share the shape; seven
  carry `{e}`, `{path}` or `str(exc)`.
- **Where:** `mapper/app.py:3110`, against the now-bounded `:3108`; also `:734, 748, 769, 774, 849, 1144`.
- **Why it is LOW:** all of them pass `markup=False`, so there is no markup-parsing sink — the `C-17`
  crash/injection class does not apply. What is missing is **control-code-point coercion** (`plain`)
  and any length bound.
- **Stated limit on this finding:** by code inspection only. I could not render a Textual notification
  into the composited frame in-harness (`frame_rows` returned no matching row after six pauses), so I
  have **not** reproduced a leak on that surface. It is reported as an unverified adjacency, not as a
  measured defect.
- **Recommendation:** for the next increment that touches this handler, route `{e}` through
  `darkside.plain` at the notify sites that interpolate a path or an exception, or soften the
  `_event_toast` docstring's "every call site" to "every `_event_toast` call site". Out of this cut.

---

### F4 — `factory.py:350` pre-escapes, so the Factory crumb still paints the backslash F2 removed  [Severity: LOW]

- **What:** the increment removed `escape` from `_crumb_line` because `Text.assemble` parses no markup
  and the backslash was painted. `FactoryScreen._refresh` still applies it at the call site:
  `node_name = escape(node.ficha.title or self.nav.cursor or "")`, then `set_crumb([...])`.
- **Where:** `mapper/screens/factory.py:350-351`.
- **Executed:**

```
_crumb_line(["proc", "[draft] informe"], 80).plain          -> 'proc / [draft] informe'
_crumb_line(["proc", escape("[draft] informe")], 80).plain  -> 'proc / \[draft] informe'   <- what factory paints
```

- **Why it matters:** cosmetic on its own, but it also spends budget on a character that carries no
  information, so a bracket-bearing title truncates earlier on that screen than on `MapScreen`. It is
  the same rule the increment just established, contradicted two modules away — and `factory.py`'s
  sibling lines `:342-344` do the same inside `_tags_table`.
- **Recommendation:** drop the `escape` at `:350` (and consider `:342-344`) and let `_crumb_line`/`fit`
  do the coercion. Pre-existing; not introduced here.

---

### F5 — `_event_toast` measures the LABEL in `len()` too, extending code-review F7  [Severity: LOW]

- **What:** code review F7 flags `min(room, len(detail))`. The **label** side has the same unit error:
  `room = max(4, self.size.width - len(label) - 4)`. If a label ever carries a wide glyph, `len`
  under-counts and the composed line is over width.
- **Where:** `mapper/app.py:2172-2176`; the exposed call site is `:2753-2756`, whose label is
  `f"{self._seat_glyph('next_hit')} · {self._seat_label('next_hit')}"` — a glyph read from the seat map.
- **Why it is LOW:** not live. Current seat glyphs (`↵`, `/`) are one cell, and `#map-toast`'s
  `max-height: 2` lid bounds the consequence to one extra row even if that changes. Measured: the
  toast holds at 1 row at every width tried, including with a hostile detail. The arithmetic is
  otherwise exact — at w=118 with label `exportado` the composed line is 118 cells, not 119.
- **Recommendation:** `_cells(label)` for symmetry, or a comment recording that seat glyphs are
  single-cell by construction.

---

### F6 — the export toast still paints the operator's username; exposure is UNCHANGED  [Severity: LOW — carried]

- **What:** `self._event_toast("exportado", str(path))` renders the absolute workspace path. Under a
  Windows profile that is `C:\Users\<username>\...`.
- **Where:** `mapper/app.py:3108`.
- **Executed** (118-column terminal, long path):

```
toast h=1  cells=118
' exportado   C:\Users\jjgh8\Github\mapper\workspace\muy\long\long\long\long\long\…'
```

- **Direction of change — this increment moves it two ways, neither of them worse:**
  - **DoS: CLOSED.** The detail was unbounded and `#map-toast` took its rows from `#map-body`; a long
    path rendered many rows. It is now one row at every width.
  - **Coercion: CLOSED.** `:3108` is the one `_event_toast` site that applies no `plain` at the call
    site; the seam now supplies it. Executed: a detail carrying `U+202E`, a TAG-block payload, `U+200B`
    and `U+0000` paints as `probado det<U+FFFD>×9fin`, frame leaks `[]`.
  - **Username exposure: UNCHANGED.** Truncation is from the right and `<username>` sits in the first
    ~15 cells of a Windows path, so it survives every width. It was visible before and is visible now.
- **Why it stays LOW:** it is the operator's own path on the operator's own screen. It becomes real
  only where the frame leaves the machine — a screenshot, a recorded demo, an exported SVG shared with
  a client. **LFPDPPP note:** the username is personal data under Mexican law once a frame containing
  it is shared with a client or attached to a deliverable; it is not client data and does not leave
  the system on its own.
- **Recommendation:** render `path.name` or a `~`-relative path in the toast and keep the absolute
  path for the log. Carried, not blocking — no change in exposure is introduced here.

---

## Answers to the remaining dispatch questions

**Q2 — does routing `detail` through `fit` close rather than open a path?** **Closes.** `fit` coerces
(`plain`) and truncates, in that order, and it is the only new code on the path. It cannot open a
markup sink because `Text.assemble`'s `(str, style)` tuple appends literally (Limb C). The export
sink at `:3108` is the site that gains the most: it was the one call site with no `plain`, and it is
now covered. See F6 for the direction on each of the three axes, and F3 for the sibling arm the seam
does **not** cover.

**Q3 — are `+N …` and the `…` separator safe?** **Yes.** `dropped = len(crumb) - 1 - len(kept)` is an
`int` from two `len()` calls; it is f-string-interpolated into `f"+{dropped} "` and can only ever be
decimal digits. `"… / "` and `" / "` are module literals, and `INK` / `MUT` are style constants.
**There is no path by which file-derived content reaches the count or the separator.** Executed at
depth 3 / 12 / 150 / 1200 against a 40-cell budget: `+9 … / `, `+147 … / `, `+1197 … / ` — digits
only, and the line stayed at 28-38 cells. The `…` inside a *part* comes from `fit`'s `overflow="ellipsis"`,
which is Rich-supplied, not file-supplied.

**Q5 — can `except NoActiveAppError` now raise where it previously swallowed?** **No, on any operator
path.** Three checks:
- **Identity:** `textual.dom.NoActiveAppError is textual._context.NoActiveAppError` → `True`. (Note the
  code review named it `textual.app.NoActiveAppError`; that alias **does not exist** in Textual 8.2.8
  — `AttributeError`. The import that shipped, from `textual.dom`, is the correct one.)
- **It catches the real raise:** constructing `KeyBar` outside a running app raises from
  `message_pump.py:264 in app`, and `isinstance(e, textual.dom.NoActiveAppError)` → `True`.
- **Nothing else in the `try` body can raise:** the body is `self.app.size.width`. `App.size`
  (`textual/app.py:1655-1669`) is a pure property over `_size` / `_driver._size` / `console.size` with
  no raise path. So the narrowing loses no coverage.

One clarification the packet's §9.5 gets slightly wrong: there was no `except Exception` **in the
shipped predecessor** to narrow *from*. Pre-increment `_width` was `return self.size.width or 118` with
no `try` at all and no `self.app` access; the `except Exception` existed only in this increment's first
draft. The `try/except` as a whole is new, and it is correctly scoped.

Separately, and **pre-existing**: the `NoActiveAppError` observed above is raised by `self.update(...)`
at `chrome.py:61`, *outside* the `try` — `_width()` had already returned its fallback successfully.
`KeyBar` (and `TabStrip`) simply cannot be constructed outside a running app, and could not before
this increment either, since both `__init__`s already called `self.update`. Test-harness path only;
no operator reaches it.

**Q6 — any secret, path, or user-identifying data newly reaching a rendered surface?** **No new one,
and one old one narrowed.** No `.env`, credential, token or key is touched anywhere in the diff; no
new file read, no new network or subprocess call, no new dependency, no new external tool or MCP
surface, nothing added to `.gitignore`'s concern. The only user-identifying datum on a rendered
surface is the workspace path in the export toast (F6), which is pre-existing and whose exposure this
increment does not change. Four previously-uncoerced file-derived crumb sources (filename, repo name,
link chain, factory title) are **newly coerced** — a net reduction.

---

## Suite evidence

Run on the delivered tree, security-relevant lanes only (the code review carries the full ledger):

```
pytest tests/test_darkside_census.py tests/test_crumb.py tests/test_fold.py -m "slow or not slow"
  -> 54 passed, 3 xfailed in 33.78s   exit 0
python -m ruff check .  -> 23 F401 + 4 F841 = 27    (SET-identical to the packet's 27 = 27)
```

`test_darkside_census.py` is the load-bearing one here: it re-derives `COERCION_RANGES` from
`unicodedata` and asserts equality, so the coercion list `_crumb_line` now depends on is verified
against the standard rather than against itself. `rich.markup.escape` remains imported and **live** at
`darkside.py:373`, so its retention is not a new F401.

---

## Evidence checklist

- [x] **Each finding has what · where · why · recommendation** — F1 `chrome.py:20`, F2 `app.py:2624`+`:1702`, F3 `app.py:3110`, F4 `factory.py:350`, F5 `app.py:2172`, F6 `app.py:3108`.
- [x] **Each finding has a severity rating** — 1 MEDIUM (F1), 5 LOW (F2-F6), 0 HIGH.
- [x] **No secret values appear in this output** — no key, token or credential exists in the diff; the one path rendered above is a pytest `tmp_path`/synthetic path, and F6 references the username's *location* in the render, which the finding is about. Hostile code points are named `U+XXXX` per `C-56`; no control byte was written into this file.
- [x] **Verdict is explicit** — SIGN-OFF, below.
- [x] **New tool / integration scope** — **none added.** No MCP server, Composio connector, n8n node, third-party API, subprocess, network call or dependency appears in this diff. Blast radius of the change is confined to three rendering functions in one local TUI process; no outbound action surface, no external state, no auth flow, no destructive command, no deploy path. Nothing to scope-review.
- [x] **Sole-writer discipline** — 5/5 pins byte-identical at exit, `git status --porcelain` == entry state, `__pycache__` purged to 0, no mutant installed (no-op hazard not applicable).

---

## Verdict

- [x] **SIGN-OFF — OK to advance**
- [ ] OK with the listed mitigations applied first
- [ ] Block

**HIGH count: 0.**

The coercion argument for removing `escape()` is sound on all three limbs, and the change is a net
**improvement** to the coercion posture: four crumb producers that previously rendered file-derived
strings with no coercion at all now pass through `plain`. The denial-of-service bound holds against
crafted titles (8 families × 110 widths, zero breaches), crafted depth (up to 600 crumb elements ×
5 widths, lid held in all 25), and in the real app from 20 to 200 columns. The toast seam closes a
coercion gap at the export sink rather than opening one. `NoActiveAppError` is correctly identified
and correctly scoped.

F1 is the one worth fixing soon — not because it is live (it is not; measured) but because it leaves
the file self-inconsistent four lines apart, and the argument the increment used to justify the
`KeyBar` fix is the argument against leaving it. F2 and F4 are corrections to statements the record
now makes. F3, F5, F6 are carries.

**Recommended follow-up order:** F1 (one line + a shared `_width`), F2 and F4 (record/rule
consistency), then F3/F5/F6 as carries for whoever next touches the notify sinks or the export path.

**On `LLR-N07.3.4`'s `open_blocks`:** from the security side there is no remaining objection. The
title-length vector is measured closed at every width from 20 to 200 with the hostile fixture, the
bracket-bearing title that defeated the pre-fix bound is now in bound at all 110 widths swept, and
the frame is clean of hostile code points on both the `MapScreen` and `_ImportPreviewScreen` crumbs.
The tab-row wrap below ~31 columns remains the declared carry, and it is not this increment's.
