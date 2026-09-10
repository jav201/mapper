# Security Review — Inc-4c (US-N07 / `LLR-N07.3.4`, `#D43`)

**Reviewer:** security-reviewer (independent) · **Date:** 2026-08-29
**Branch:** `feat/ui-next-batch-02` · **Entry:** `9ba2f26` · nothing committed
**Source under review:** `mapper/app.py` (1 file, +339/−? hunks). `.dev-flow/**` ignored.
**Verdict:** **SIGN-OFF** — with F-1 applied first (one line) and F-4 corrected.

---

## Method / fidelity

Reviewed in an isolated mirror (`git clone --local --no-hardlinks` of the real
repo + working-tree overlay of `mapper/app.py` and `tests/test_search.py`).
A second mirror pinned at `9ba2f26` (Inc-4b, no overlay) was used to separate
what this increment **introduces** from what it inherits.

Mirror reproduces the declared baseline exactly:

```
850 passed, 17 deselected, 3 xfailed in 203.07s (0:03:23)
```

The real repo was never mutated. Verified by sha256 before and after:

```
654dba5e9f746e2971aadc45e50c1505ef2c55e4eec6f598c7d3d4162d5fe115 *mapper/app.py
d161c3a7949c95c345cd14845a3b3afaf6ada0f3d47c16ba2d4e2e38a3b20061 *tests/test_search.py
```

`git status` identical before and after (4 modified, 1 untracked, unchanged).
No probe file was written into either mirror — probes ran from the scratchpad
with `PYTHONPATH`, so the coercion census that rglobs untracked files was never
given anything new to find. Hostile fixtures lived in `tempfile.mkdtemp`.
All hostile code points are built from their numbers; none is spelled verbatim
in this document.

---

## Findings

### F-1 — the echo's cap bounds display CELLS, not ROWS  [Severity: MEDIUM] · **INTRODUCED**

- **What:** `_query_echo` bounds the operator's query with `darkside.fit(..., 32)`.
  `fit` bounds *display cells*. `darkside.plain` **deliberately preserves**
  U+000A and U+0009 (`PRESERVED_CODE_POINTS`, `darkside.py:370`), so 32 cells
  can be 32 *rows*. The cap therefore does not bound the dimension that matters.
- **Where:** `mapper/app.py:1833` (`_query_echo`); constant at `mapper/app.py:102`;
  the Input that feeds it at `mapper/app.py:1238`.
- **Why it matters:** measured, with a query of `("z" + U+000A) * 60` in the
  suspended regime at 118x34:

  | | ordinary query | newline-bearing query |
  |---|---|---|
  | count region height | 2 | **32** |
  | `#map-canvas` height | 24 | **1** |
  | `esc limpiar` in painted frame | True | **False** |
  | suspension notice in painted frame | True | **False** |

  This is the **Inc-4b defect shape reproduced one surface over** — unbounded
  text collapsing the canvas and pushing the recovery affordance off-frame —
  which is the specific regression this increment was asked to avoid.

- **Reachability — the reason this is MEDIUM and not HIGH:** it is **not
  reachable through any shipped operator path on Textual 8.2.8.**
  - Typing cannot produce U+000A: `enter` submits.
  - The real `Paste` event is sanitized **upstream**, by
    `textual.widgets.Input._on_paste`, which does `event.text.splitlines()[0]`.
    Measured: a 120-char newline-bearing paste event yields `Input.value` of
    length **1**, no U+000A.
  - Only `Input.insert_text_at_cursor` and direct `.value` assignment carry the
    newline through, and neither is an operator path.
  - The Input declares **no `max_length` and no `restrict`** (`app.py:1238`), so
    this repo contributes no guard of its own.

  The whole defence is a third-party widget's implementation detail that **no
  test in this repo asserts**. That is a control the system does not enforce.

- **Aggravating:** `_query_echo`'s own docstring (`app.py:1801-1831`) states
  *"What must not happen is UNBOUNDED growth, and 32 cells bounds it."* That
  claim is **false in the row dimension**, and the sweep it cites varied only
  ASCII length. A bound argument that names the wrong dimension is how a later
  reader deletes the right guard — the exact hazard this file's own docstrings
  repeatedly warn about.

- **Recommendation (minimal, at this sink only — `plain` must keep U+000A/U+0009
  because layout elsewhere depends on them):**

  ```python
  return darkside.fit(
      self.query_text.translate({0x0A: " ", 0x09: " "}), _QUERY_ECHO_CELLS
  ).rstrip()
  ```

  Verified: bounds the echo to **1 row** across a U+000A flood, a U+0009 flood,
  2000 ASCII, and 500 wide CJK, while leaving cells at ≤32 in every case.
  Correct the docstring's bound claim in the same edit.

---

### F-2 — above the bound, the first `esc` is a keypress with no visible effect  [Severity: MEDIUM] · **INTRODUCED** (contingent on F-3)

- **What:** `_search_is_live` now reads the query rather than the resolution, so
  above the renderer's bound `esc` clears instead of popping. The affordance
  that justifies this (`esc limpiar` on the count region) **paints zero rows at
  the genuine above-bound size**, so the press changes nothing the operator sees.
- **Where:** `mapper/app.py:2536` (`_search_is_live`), `mapper/app.py:3071`
  (`action_back_or_home`).
- **Why it matters:** measured at 12002 nodes, 118x34, same graph, same query:

  | tree | after one `esc` | frame changed visibly |
  |---|---|---|
  | `9ba2f26` (Inc-4b) | `HomeScreen` — left the map | **True** |
  | working tree (Inc-4c) | `MapScreen`, query cleared | **False** |

  This is the inverse of `#D38` and precisely the failure `_search_is_live`'s own
  Inc-4b docstring named: *"the handler acts where no affordance was
  advertised."* Inc-4c closes that defect below the bound and reintroduces it
  above it, because the surface it relies on is off-viewport.

- **Not a trap.** A second `esc` always pops. Verified across 9 regimes —
  below/above bound, ordinary/hostile/20000-char query, 118x34 and 80x24,
  including the F-1 collapsed state: **9/9 left the map within two presses.**
- **Recommendation:** do not unpick `#D43` for this. Route with F-3, and record
  explicitly in the increment close that **predicate 1 of `LLR-N07.3.4` is not
  satisfied in the real frame above the bound** — the region declares the search
  as a *string*, but nothing is *painted*. Fixing F-3 fixes F-2.

---

### F-3 — the 12002-node collapse is NOT purely cosmetic  [Severity: MEDIUM] · **PRE-EXISTING** (judgement requested)

- **What:** the author proposes deferring the whole-screen collapse to an
  `Inc-STRIPS` and asks whether it is cosmetic. **It is not — it has an
  availability dimension.**
- **Where:** `#map-minimap` (`app.py:1228`), the unbounded meter
  (`app.py:1944-1947`), `#map-canvas` (`app.py:1234`).
- **Measured, identically at `9ba2f26` and at the working tree** (12002 nodes,
  118x34):

  ```
  minimap    y=-627  h=668
  canvas     y=  41  h=  1
  pagination y=  42  h=104/105   painted_rows=0
  'esc limpiar' in frame : False      'coincidencias' in frame : False
  open_map        8.85 s (HEAD) / 9.04 s (working tree)
  'enter' submit  3.68 s (HEAD) / 3.70 s (working tree)
  refresh_canvas  3.50 s (HEAD) / 3.99 s (working tree)
  ```

  The control with **no query live** costs 3.73 s, so this is not the search.
- **Judgement:** a ~4 s repaint and a one-row canvas driven by an unbounded
  render over **operator-openable file data** is the same class as the defects
  already routed to `Inc-REPAIR` — the size of the input controls the cost and
  nothing bounds it. It should carry the same weight as `F-A`, not a lower one.
  It is a denial-of-availability surface, not a cosmetic one.
- **But it does not block this merge:** it is byte-for-byte the same at HEAD.
  Inc-4c's only delta here is pagination height 104→105 (one row), which paints
  0 rows either way.
- **Recommendation:** accept the `Inc-STRIPS` deferral, but file it at the same
  severity as the other unbounded-render findings rather than as a layout nit,
  and note that F-2 rides on it.

---

### F-4 — the docstring's sweep evidence is wrong  [Severity: LOW] · **INTRODUCED**

- **What:** `_query_echo`'s docstring claims *"a 2000-character query costs the
  region the same number of rows as an ordinary one at every width from 65 up,
  and ONE EXTRA ROW at 60."*
- **Where:** `mapper/app.py:1801-1831`.
- **Why it matters:** independently swept, widths 60→160 step 5, len 1 vs 2000 —
  the extra row appears at **w=60, 65, 85, 90, 95**: five widths, not one. The
  *conclusion* stands (bounded, at most +1 row, never off-frame at any of the 168
  configurations tested). The *stated evidence* does not. This file's own
  standard is that a measured claim is load-bearing.
- **Recommendation:** restate as "at most one extra row, at five of the
  twenty-one widths swept (60, 65, 85, 90, 95)."

---

## Probes that came back clean

**P1 — coercion on the new sink.** Real `/` → keys → `enter`. Query built from
numbers: `"ze" + U+202E + "ta" + U+200B + U+001B + "[31m" + U+0007 +
"[bold red]x[/]"`. Everything typeable was pressed for real; the four code
points with no Textual key name were delivered through the Input's own
`insert_text_at_cursor` (the paste path) — departure stated, not hidden.
`screen.query_text` held the hostile string **verbatim**.

`_count_line().plain` above the bound:

```
'búsqueda: «ze�ta��[31m�[bold red]x[/]» · 0 coincidencias en el mapa · esc limpiar · resaltado y recorrido suspendidos  '
```

- U+202E, U+200B, U+001B, U+0007: **absent** from the count line, from the
  region-clipped composite, and from the **whole composited frame**.
- Brackets stay **literal**: `[31m`, `[bold red]` and `[/]` all present as text.
  `darkside.Text(...)` is the constructor, which does not parse markup.
- Control held both ways: `Text.assemble` keeps U+202E (True);
  `darkside.plain` does not (False). The measured asymmetry is real and the new
  sink is on the correct side of it — `_query_echo` routes through `fit`, which
  calls `plain` first, then truncates.
- Below the bound the query is **not echoed at all** (`_count_line` returns
  `n/N` or the reserved `0`), so the new echo exists only in the suspended branch.

**P2 — length.** Widths 60→160 step 5 × lengths {1, 10, 32, 33, 100, 2000,
20000} at height 34, plus height 24 at widths {60, 80, 118} = 168 configurations.
`esc limpiar` present in the frame **168/168**. Suspension notice present
**168/168**. Canvas never collapsed. Maximum region growth from a 20000-char
query: **+1 row**. Cap boundary verified at exactly 32 cells across ASCII 2000,
wide CJK, emoji, combining sequences, an all-control flood and a U+202E flood.

**P3 — escape availability.** No state found in which the operator cannot leave
the map. 9/9 regimes escapable within two presses (see F-2 for the caveat about
the *first* press).

**P4 — cost.** Independently re-measured at 12002 nodes (min / median of 7):

| | measured | author's claim |
|---|---|---|
| `SearchIndex(graph)` construction | 0.0000 s / 0.0000 s | — |
| `idx.hits('zeta')` | 0.0073 s / 0.0076 s | 0.0075 s ✓ |
| `idx.query('zeta')` | 0.0118 s / 0.0129 s | 0.0122 s ✓ |
| `tree_order(graph)` | 0.0036 s / 0.0037 s | 0.0097 s (conservative) |
| `_whole_graph_tally` (ctor + hits, unmemoised) | 0.0072 s / 0.0073 s | — |

**The "stale by two orders of magnitude" correction is CORRECT.** Inc-4a's
"seconds each, four resolutions per repaint" does not hold; ~12 ms is right, and
the bound is now the renderer's argument rather than the search's.

Call counts through **real key presses**: `_whole_graph_tally` is invoked
**exactly once per repaint** (0 when no query is live), so the deliberate
non-memoisation costs one `hits` pass per frame, not four. Frame delta
attributable to the new declaration: **3.85 s with a query vs 3.73 s without —
~0.12 s of a ~3.8 s frame (~3%).**

**Declaring the count above the bound is affordable. The claim the whole
increment rests on holds.** (The ~3.8 s frame itself is F-3 and is present at
HEAD.)

**P5 — no new sink.** The only selector synthesis in the file is
`f"#{COUNT_REGION_ID}"` at `app.py:1642` and `app.py:2221`, from a module
constant. No node id, ficha title, schema key or file-derived value reaches a
widget id or CSS selector in any added line. No `getenv` / `environ` /
`expanduser` / `USERNAME` / `Path(` / token / secret vocabulary in any added
line. `_seat_glyph` reads a **statically declared** keymap table (`keymap.py` has
no file load), so it is not a file-derived sink.

---

## Pre-existing — recorded and routed, not fixed

| Item | Status | Evidence |
|---|---|---|
| `F-A` (HIGH, open, `Inc-REPAIR`) | **no new instance** | only f-string selector is `f"#{COUNT_REGION_ID}"`, `app.py:1642` / `:2221`, from a constant |
| `S-15` | **no new instance**; the diff re-states and narrows it, does not close it | `app.py:2061-2078` |
| unbounded pagination meter | **no new instance**; still unbounded, deliberately, documented | `app.py:1944-1947`; identical at HEAD |
| export-toast username path leak | **NOT TOUCHED by this diff** | anchor `self._event_toast("exportado", str(path))` at `app.py:2904`; `git diff` contains no `exportado` hunk. Still leaks the absolute path. |

---

## What I could not determine

1. **Whether Textual's `Input._on_paste` newline-stripping is a contract or an
   implementation detail.** I read the 8.2.8 source and it strips
   (`event.text.splitlines()[0]`); I found no documented guarantee. F-1's
   reachability judgement — and therefore its MEDIUM rather than HIGH rating —
   rests entirely on that reading. **If Textual is not pinned tightly, F-1's
   severity rises.** Worth confirming against the project's dependency pin.
2. **Predicate 1 of `LLR-N07.3.4` could not be verified as a painted frame above
   the genuine bound**, because the region paints 0 rows there. It is verified
   at `_count_line()`'s output and in a bound-lowered configuration where the
   region is on-viewport. I state this rather than treating the string as the
   frame.
3. **I did not review `tests/test_search.py`'s 382 changed lines as a security
   surface** beyond confirming the suite reproduces the declared baseline; the
   brief scoped source to `mapper/app.py`.
4. **The author's "76,365 chars" minimap figure could not be reconciled.** I
   measure 3,944 region-clipped composited chars over 668 rows — a different
   measurement basis (widget render vs composited frame). It does not change F-3.

---

## Evidence checklist

- [✓] Each finding has what · where · why · recommendation — F-1..F-4 above, each with `file:line`.
- [✓] Each finding has a severity rating — F-1 MEDIUM, F-2 MEDIUM, F-3 MEDIUM (pre-existing), F-4 LOW.
- [✓] No secret values appear in this output — no secrets found; no hostile code point spelled verbatim (named as `U+202E`, `U+200B`, `U+001B`, `U+0007`, `U+000A`, `U+0009`).
- [✓] Verdict is explicit — SIGN-OFF with mitigations, stated below.
- [✓] New tool/integration scope and blast radius — **n/a: this increment adds no MCP, Composio, n8n, network call, subprocess, filesystem write or third-party dependency.** Verified: no added line contains `Path(`, `open(`, `requests`, `subprocess`, `environ`. Blast radius is confined to one screen's painted strip.
- [✓] Fidelity — mirror reproduced `850 passed, 17 deselected, 3 xfailed`.
- [✓] Real repo unmutated — sha256 identical before/after; `git status` identical.

---

## Verdict

- [ ] OK to ship
- [**x**] **OK to ship with the listed mitigations applied first**
- [ ] Block — must fix HIGH findings before ship

**SIGN-OFF.**

**No HIGH finding is introduced by this increment.** The coercion sink is
correctly routed, the length cap holds in the dimension the author swept, `esc`
never traps the operator, the cost claim that the increment rests on is
independently confirmed, and no new secret, selector or file-derived sink is
added.

Apply before merge:
- **F-1** — one line at `app.py:1833`, plus the docstring's bound claim. This is
  the Inc-4b defect shape held back only by an unasserted upstream guard.
- **F-4** — correct the swept widths in the docstring.

Route, do not fix here:
- **F-2** with **F-3** to `Inc-STRIPS`, and record that `LLR-N07.3.4` predicate 1
  is not satisfied in the real frame above the bound.
- **F-3** should be filed at the weight of an unbounded-render availability
  defect, alongside `F-A`, not as a layout nit.
