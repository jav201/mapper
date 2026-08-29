# Increment 4b — US-N07 seat + walk (`#D5b`, `LLR-N06.2.4`, `E1b`/`E1c`, `#D38`)

**Batch:** `2026-08-26-ui-next-batch-02` (SEALED) · **Increment:** `Inc-4b` · **Branch:** `feat/ui-next-batch-02`
**Entry commit:** `a971432`, tree clean · **NOT COMMITTED** — the working tree is what is gated.
**SOURCE FILE COUNT: 2** — `mapper/keymap.py`, `mapper/app.py`. Tests uncapped, as declared.
**Language:** English (engineering artifact).

---

## BLUF

The `#D5b` rebind, the `n`/`N` walk, the fold auto-open, the two empty-state toasts, the one-time
rebind declaration, state-dependent `esc` and the seat-derived hint line all ship, on **2 source
files**. Suite **843 passed / 17 deselected / 3 xfailed, exit 0, zero FAILED**; the slow lane runs
separately at **17 passed**. Ruff SET over `mapper/ tests/` is **IDENTICAL** to the entry pin (27 =
27, zero NEW, zero GONE). **16 mutations, 16 RED, 16 byte-identical restores.**

**Five things the spec had wrong or did not settle, each resolved and declared** — §1.6. The two
that change observable behaviour are the toast collision between `AT-051b` and `E1b` (both fire on
the first `n`), and a **third empty-ish state the sealed text never names**: above the renderer's
bound `E1c` would declare "«q» no aparece en este mapa" over a graph nobody evaluated, which is the
lying affordance `Inc-4a`'s `None` return exists to prevent. Both are implemented, both are gated.

**The entry obligation is discharged by EXEMPTION, not by opening a pass** — §4.6 — with a stated
reason of the same shape as `_pan`'s, and the exact-set opener assertion is left untouched at
`{refresh_canvas, _declare_after_layout}`.

---

## 1 · What changed

### 1.1 · The `#D5b` seat rebind — three rows (`mapper/keymap.py`, +15/−1)

| Row | Before | After | Group |
|---|---|---|---|
| `map/n` | `next_gap` "siguiente faltante" (`view`) | **`next_hit` "siguiente coincidencia"** | `nav` |
| `map/N` | — | **`prev_hit` "coincidencia anterior"** | `nav` |
| `map/M` | — | **`next_gap` "siguiente faltante"** | `view` |

`n`/`N` sit in `nav`, beside the `/` that produces the set they walk. Both labels are true in
**every** state, so the seat stays a static set and the whole-seat pin stays set equality — which is
the condition `#D10` imposed when it rejected the state-dependent chord.

### 1.2 · The walk (`mapper/app.py`)

`action_next_hit` / `action_prev_hit` are two-line wrappers over `_walk_hits(step)`, mirroring the
shipped `action_pan_*` → `_pan` shape. The walk consumes `_search_order()`'s tree-ordered tuple —
`LLR-N07.3.1`'s order is **consumed, never re-derived** — indexes the cursor into it, and wraps with
`% len(hits)` in both directions. The tuple is not mutated.

### 1.3 · `LLR-N06.2.4` — the fold auto-open

`_unfold_onto(nid)` opens every folded branch that hides the target and returns what it opened;
`_walk_hits` then moves the cursor, repaints, and prefixes the hint with `abrió «<branch>»`. The
branch is **not** re-closed when the walk moves past it. The child index is built once per call for
the same reason `search.tree_order` builds one: `Graph.children_of` is a full scan of `graph.edges`.

### 1.4 · `E1b` / `E1c` / the declaration / the third state

Four distinct toasts out of one slot:

| State | Title | Body |
|---|---|---|
| first `n` press on this screen | `n · siguiente coincidencia` | `siguiente faltante ahora en M` |
| `n`/`N`, nothing ever submitted (`E1b`) | `sin búsqueda activa` | `no hay coincidencias que recorrer` |
| `n`, submitted, 0 hits (`E1c`) | `0 coincidencias` | `«<query>» no aparece en este mapa` |
| `n`, above the renderer's bound (**new**, §1.6 C) | `búsqueda sin evaluar` | `el mapa supera el límite de <N> nodos` |

Every string in the declaration is read from the **seat** at call time through `_seat_row`, never
typed. `E1c`'s body routes the operator's query through `darkside.plain` — the coercion rider.

### 1.5 · `esc` (`#D38`) and the hint line

`action_back_or_home`: a live search is cleared and the map **stays**; with none live the screen is
popped, as before. The two identical arms it used to carry (`if self.source_crumb: pop else: pop`)
are gone — a branch whose sides are the same statement reads as a distinction the code does not make.

`_search_hint(hits)` builds `n siguiente · N anterior · esc limpiar` (or `sin coincidencias · esc
limpiar`) with every **glyph read from the seat** and takes the resolved order as an argument, so it
cannot describe a different answer from the one its caller acted on. `DEFAULT_MAP_HINT` is now
declared once and read by the three sites that restore it.

### 1.6 · Five spec corrections, declared rather than absorbed

**A · `AT-051b`'s declaration and `E1b` both fire on the first `n` press, and the sealed text does
not say which wins.** On a fresh screen with no search, `02l` §8.1 requires the first real `n` to
paint the declaration and `02l` §7.6 requires `n` with nothing submitted to paint `E1b`. One toast
slot, two mandated occupants. **Resolved: the declaration outranks the empty-state toast on press
one and never again.** The key having changed meaning is the more urgent of the two facts and the
only one that is ever said; `E1b` is what press two paints. Both predicates are satisfied as written
(`P-051b.1` reads press one, `P-051b.2` reads press two and finds a toast that does not carry the
declaration), and the interaction is **pinned** in `test_at_023_e1b_and_e1c_are_painted_differently`
rather than left to be rediscovered.

**B · `P-047.3` is asserted at the moment of opening, not after the further press.** `02l` §7.9 puts
"the hint names the opened branch" under `AT-047`, which is defined as the state after one MORE
press. `LLR-N06.2.4`'s own statement says the system "shall paint the hint line naming the branch it
opened" — an announcement of an event. Requiring it to survive a subsequent press requires the
announcement to outlive the event, and it collides with `UX-Q3-b`, which requires the same line to
read `n siguiente · N anterior · esc limpiar` while a search is live. The predicate lives in
`test_at_046_the_walk_opens_a_folded_hit_and_says_so`, at both widths, and reads the painted region
as well as the widget.

**C · There is a THIRD empty-ish state and the sealed text never names it.** `_search_order` returns
`None` above `MAX_RENDER_NODES` — `Inc-4a` built that distinction after measuring the strip paint
`0 coincidencias en el mapa` over a graph holding thousands of real matches. A walk that treats
`None` as "empty" paints `E1c`, whose body is a claim about the graph (`no aparece en este mapa`)
that nobody evaluated. **A third branch and a third toast were added**, plus the same guard on the
hint line, and both are gated by `test_the_walk_above_the_render_bound_declares_neither_zero_nor_silence`
and mutation `M16`. This is new copy that no `shall` clause owns; it is flagged for the gate.

**D · `C-D6a` is closed structurally, but NOT by adding an `active_hits` attribute.** `02l` §8.3's
option (a) proposes "a single `MapScreen` attribute (e.g. `active_hits`)". Adding one would create a
**second** owner of "what matches" on the screen `Inc-4a` spent its whole increment giving one
owner. The invariant that matters is *one source, no fallback*, and it is asserted exactly:
`test_cd6a_the_walk_reads_exactly_one_resolution` derives the class's vocabulary of possible
result-set names from its own AST, requires `_walk_hits`'s intersection with it to be exactly
`{_search_order}`, and requires the handler to contain **no `BoolOp` at all** — so
`search_hits or lens_matches` is not expressible in it. **The rule caught real code on the first
run**: a `title or nid` fallback in the hint-naming line. It was lifted into `_branch_name` rather
than the rule being weakened to allow it.

**E · Two measurements in the brief read against a different instrument.** The brief's "29 map-scope
→ 31" counts `b.scope == "map"`; `bindings_for("map")` — which is what `C-D25a` and the Inc-3 census
use — includes the two app-scope rows and reads **31 → 33**. Both are reported in §4.4. And the
brief's whole-seat `sha256 1e7002cb…91eec9e5` could **not** be reproduced: the serialisation it was
taken over is not declared anywhere, and four canonical forms were tried. A serialisation is
declared in §4.4 and both sides are measured under it; the pin still works, because entry and exit
are compared through one instrument.

---

## 2 · Files modified

### Source (2 — the declared budget)

| File | Δ | What |
|---|---|---|
| `mapper/keymap.py` | +14 / −1 | the three `#D5b` rows |
| `mapper/app.py` | +255 / −7 | `_seat_row` `_seat_glyph` `_seat_label` `_search_hint` `_declare_rebind` `_walk_toast` `_unfold_onto` `_branch_name` `_walk_hits` `action_next_hit` `action_prev_hit`; `action_back_or_home` branch; `on_input_submitted` hint; `DEFAULT_MAP_HINT`; `_rebind_declared` |

### Tests (uncapped)

| File | Δ | What |
|---|---|---|
| `tests/test_search.py` | +551 | `AT-022`, `AT-023` (both toasts + the coercion rider), `AT-051` ×2, `AT-051b`, `AT-053`, `P-052.2`, `C-D6a`, the above-the-bound arm, and 4 rows in `_PASS_FREE_READERS` |
| `tests/test_fold.py` | +193 | `AT-046`, `AT-047`, each at 118x34 **and** 80x24 |
| `tests/test_inc4_census.py` | NEW, +119 | `C-D25a` / `C-D25b` for this increment's own three rows — **staged** (`git add`), because `test_a3_census` fails an untracked source file by design |
| `tests/test_inc3_census.py` | +50 / −7 | `EXIT_MAP_SEAT` frozen (§4.5); one docstring corrected; unused import dropped |
| `tests/test_key_dispatch.py` | +8 / −2 | `EXPECTED_SEAT`: `n` rebound, `N` and `M` added |
| `tests/test_keymap.py` | +6 / −1 | `EXPECTED_PER_SCOPE[map]` 29 → 31, itemised |
| `tests/test_a3_census.py` | +14 / −2 | the `render` call-site pin 57 → 58, itemised (§4.7) |

---

## 3 · How to test

```
cd <repo>
set PYTHONUTF8=1
python -m pytest -q                    # default lane (addopts already carry -m 'not slow')
python -m pytest -q -m "slow"          # the 17 deselected
python -m ruff check mapper/ tests/ --output-format=concise
```

Targeted:

```
python -m pytest -q tests/test_inc4_census.py
python -m pytest -q tests/test_search.py -k "at_022 or at_023 or at_051 or at_053 or p052_2 or cd6a or above_the_render_bound"
python -m pytest -q tests/test_fold.py -k "at_046 or at_047"
```

By hand, at 118x34: open a map, `/`, type `riesgo`, `↵`. The first `n` toasts the rebind; further
`n`/`N` walk the matches and wrap; walking into a folded branch opens it and the hint says which;
`esc` clears the search and keeps the map, a second `esc` leaves it; `M` is the coverage worklist.

---

## 4 · Test results

### 4.1 · Baseline, re-derived on entry before a line was written

```
822 passed, 17 deselected, 3 xfailed in 133.77s   exit 0   zero FAILED
ruff check mapper/ tests/  ->  Found 27 errors
keymap: 52 rows, bindings_for("map")=31, scope=="map"=29, duplicate_chords()=[]
```

### 4.2 · Exit — one complete run, read from its own output

```
843 passed, 17 deselected, 3 xfailed in 163.88s   exit 0   zero FAILED
slow lane: 17 passed, 845 deselected in 23.67s
collection, all markers: 846/863 tests collected (17 deselected)
```

### 4.3 · Ledger — `post = base − D + A`

| Lane | base | D | A | post | measured |
|---|---|---|---|---|---|
| default (`-m 'not slow'`) | **825** | 0 | **21** | **846** | 843 passed + 3 xfailed = **846** ✓ |
| all markers | **842** | 0 | **21** | **863** | collected **863** ✓ |

`A = 21`, itemised — **17 new nodes and 4 new parametrized cases**:

- `tests/test_inc4_census.py` — 3
- `tests/test_search.py` — 10 (`AT-022`, `AT-023` ×2, `AT-051` ×2, `AT-051b`, `AT-053`, `P-052.2`, `C-D6a`, above-the-bound)
- `tests/test_fold.py` — 4 (`AT-046`, `AT-047`, each × 2 sizes)
- **+4 without a line of test code**: `test_key_dispatch::test_at_n03g` and `test_keymap::test_at_n03a` parametrize over the seat, so the two new rows generate `[N->prev_hit]`, `[M->next_gap]`, `[map:N:prev_hit]`, `[map:M:next_gap]`. `test_at_n03g[n->next_hit]` presses the real `n` and asserts it dispatches `next_hit` — an independent dispatch check for the rebind that cost nothing.

### 4.4 · `C-D25b` — the whole-seat pin and `duplicate_chords()`, ENTRY and EXIT

| Measurement | ENTRY (`a971432`) | EXIT |
|---|---|---|
| `len(KEYMAP)` | 52 | **54** |
| `len(bindings_for("map"))` | 31 | **33** |
| rows with `scope == "map"` | 29 | **31** |
| `duplicate_chords()` | `[]` | **`[]`** |
| whole-seat sha256 † | `9129543271a8b8cd…d3beb908` | `46ac9fbbf6ddea78…f06c9a7cb` |

† `sha256(repr(sorted((scope, key, glyph, action, label, group, priority) for each row)))`, declared
here because the brief's digest could not be reproduced under any of four canonical forms (§1.6 E).

**`C-D25a` — the declared diff, asserted EQUAL to the measured difference.** Declared:
`+{("n","next_hit"), ("N","prev_hit"), ("M","next_gap")}`, `−{("n","next_gap")}`. Asserted in
`tests/test_inc4_census.py::test_cd25a_the_seat_diff_is_exactly_the_three_rows_inc4b_declares`
against the live seat, in **both** directions, plus an identity on the rebound KEY so a future edit
that dropped `n` and added some other chord could not satisfy it. Mutation `M15` adds a fifth,
undeclared row and the node goes RED — which is the arm's whole point, since `duplicate_chords()`
returns `[]` for it (nothing was duplicated).

### 4.5 · The regression that was RED BY CONSTRUCTION, and its repair

`tests/test_inc3_census.py::test_cd25a_the_seat_diff_is_exactly_the_four_rows_inc3_declares` asserted
`len(bindings_for("map")) == 31` and `ENTRY_MAP_SEAT − exit == frozenset()` against the **live**
seat. This increment takes it to 33 and removes `("n","next_gap")`: all three assertions fail.

**Repaired as specified**: Inc-3's exit is frozen as a literal `EXIT_MAP_SEAT` (31 rows, spelled out
rather than derived as `ENTRY | DECLARED_DIFF`, which would make the assertion a tautology), and the
node now asserts `EXIT_MAP_SEAT − ENTRY_MAP_SEAT == DECLARED_DIFF` — a statement about Inc-3's
history, permanently true. Inc-4b's own diff lives in the new census file against the live seat.
`test_key_dispatch::EXPECTED_SEAT` was updated in the same edit, as its own docstring instructs.

Two further pins moved, both itemised in place rather than bumped silently:
`test_keymap::EXPECTED_PER_SCOPE[map]` 29 → 31, and the `render` call-site pin (§4.7).

`test_cd25a_no_chord_collides_on_entry_or_on_exit` (Inc-3's) still passes and was **left alone**, but
its docstring now records that what it reconstructs is "today's seat minus Inc-3's four rows", which
was Inc-3's entry only on the day it was written. Stated rather than left to read as more than it is.

### 4.6 · The entry obligation from Inc-4a round 4

The exact-set arm `openers == {"refresh_canvas", "_declare_after_layout"}` is **untouched and
green**. The keypress-bound consumer declares itself the other way, as an **exemption**, with a
reason of the same shape as `_pan`'s rather than a shrug:

| Exemption added | Reason |
|---|---|
| `_walk_hits` | moves the selection **inside the matches of the frame on screen**, then repaints. The memo is keyed on the graph object and the query text, and a walk changes neither, so the previous pass's memo is the same value a fresh resolution would return. |
| `action_next_hit` | wrapper over `_walk_hits` |
| `action_prev_hit` | wrapper over `_walk_hits` |
| `on_input_submitted` | reads the order of the frame `refresh_canvas` painted **on the line above** |

`_search_hint` takes the order as a parameter precisely so it does **not** become a fifth exemption.
`_search_order`'s returned tuple is never mutated.

### 4.7 · Reverse census over the whole `tests/` tree

Swept for every symbol this increment touches, regardless of which requirement owns the reader:

| Symbol | Test files that read it | Verdict |
|---|---|---|
| `next_gap` | `test_inc3_census` `test_inc4_census` `test_key_dispatch` `test_keymap` `test_search` `test_worklist_safety` | green; `test_worklist_safety` calls `action_next_gap()` directly and is chord-agnostic |
| `next_hit` / `prev_hit` | `test_inc3_census` `test_inc4_census` `test_key_dispatch` `test_search` | green |
| `back_or_home` | `test_inc3_census` `test_inc4_census` `test_key_dispatch` `test_search` | green |
| `bindings_for` | + `test_palette` `test_repair_layout` | green — `AT-R12` derives the legend's expected set from the seat and still paints all 33 |
| `HintLine` | `test_fold` `test_inspector` `test_pan` `test_rail` `test_search` | green — `DEFAULT_MAP_HINT` preserves the literal exactly |
| `duplicate_chords` | `test_inc3_census` `test_inc4_census` `test_keymap` `test_search` | green |
| `map-toast` | `test_search` | green |
| `renderer.render(...)` call sites | `test_a3_census` cardinality pin | **RED, then repaired**: 57 → 58 |

**The `render` pin caught a hit this increment's own census did not name.** `AT-053` reads the hit
style off the returned `Text`'s spans — "`esc` clears the search" has to mean no node is still
painted as a match, and a substring probe cannot tell "this node is a hit" from "some node's title
contains those letters". The pin is bumped **with the reason itemised in place**, which is the
protocol the file itself states. `tests/test_a3_census.py` also fails any untracked file under
`tests/`, which is why the new census file is **staged** — staged, not committed.

`test_worklist_safety.py:158` presses `"n"` on `_ConfirmScreen` (a widget-level decline binding, not
in `KEYMAP`) and is unaffected — confirmed by execution, not by reading.

### 4.8 · Mutation table — 16 arms, 16 RED, 16 byte-identical restores

> **Read this table with `R4.3` below.** Round-1 review ran four self-chosen mutants and **two
> survived** (`H1`, `H2`). "16 mutations, 16 RED" is evidence about the sixteen mutants chosen; it
> is not a mutation-adequacy claim about the increment. The table is left as the record of what was
> run — nothing in it was wrong, it was incomplete.

Every row: sha256 before, sha256 after the mutation **landed** (a typo'd mutation also "fails", for
the wrong reason), the baseline verdict on the same selector, the mutated verdict, and the restore
digest. `git status` is not used: it is vacuous for an untracked file.

| Id | File · operation (by position, never spelled) | Target arm | Base | Mutated | Restore |
|---|---|---|---|---|---|
| M1 | `search.py` — the tree walk in `query` replaced by dict iteration | `AT-022` P-022.1 | 1 passed | **1 failed** | identical |
| M2 | `app.py` — the modulo in the walk index replaced by a clamp | `AT-022` P-022.3/4 | 1 passed | **1 failed** | identical |
| M3 | `app.py` — `_unfold_onto` returns without unfolding | `AT-046` PRED-A/B | 2 passed | **2 failed** | identical |
| M4 | `app.py` — the opened set re-added to `folded` after the repaint | `AT-047` P-047.1 | 2 passed | **2 failed** | identical |
| M5 | `layered.py` — the pill's `cv.text` call removed | `AT-047` P-047.2 (control) | 2 passed | **2 failed** | identical |
| M6 | `app.py` — `E1b`'s two strings replaced by `E1c`'s (one shared toast) | `AT-023` / `M-N07.3-b` | 1 passed | **1 failed** | identical |
| M7 | `app.py` — `plain()` dropped from `E1c`'s interpolated query | `AT-023` coercion rider | 1 passed | **1 failed** | identical |
| M8 | `app.py` — `action_next_gap`'s order forced empty | `AT-051` P-051.1 | 1 passed | **1 failed** | identical |
| M9 | `app.py` — the one-time flag never set (declare on every press) | `AT-051b` P-051b.2 | 1 passed | **1 failed** | identical |
| M10 | `app.py` — `declaring` forced false (never declare) | `AT-051b` P-051b.1 | 1 passed | **1 failed** | identical |
| M11 | `app.py` — `esc` clears and pops anyway | `AT-053` arm 1 | 1 passed | **1 failed** | identical |
| M12 | `app.py` — `esc` never pops | `AT-053` arm 2 (regression limb) | 1 passed | **1 failed** | identical |
| M13 | `app.py` — `_search_hint`'s glyph reads replaced by a literal | `P-052.2` limb (b) | 1 passed | **1 failed** | identical |
| M14 | `app.py` — a boolean fallback added to the walk's resolution | `C-D6a` / `M-N07.3-a` | 1 passed | **1 failed** | identical |
| M15 | `keymap.py` — a fifth seat row added, declared nowhere | `C-D25a` | 3 passed | **2 failed** | identical |
| M16 | `app.py` — the above-the-bound guard narrowed to the empty tuple | the third state | 1 passed | **1 failed** | identical |

**Arm independence, proven rather than asserted** — a node holding two arms can hide the second
behind the first, so the failing assertion was located for every paired mutation:

```
M11 -> assert app.screen is screen          "esc popped the map out from under a live search"   (ARM 1)
M12 -> assert app.screen is not screen      "esc no longer leaves the map"                      (ARM 2)
M9  -> assert <next_hit label> not in second                                                    (press 2)
M10 -> assert <next_hit label> in first                                                         (press 1)
M13 -> assert hint_text(screen).startswith("» siguiente · ")                                    (limb b)
        ... and limb (a) PASSED under the same mutation, which is the point of the pair
```

Expected arm count, asserted so no inert arm hides: `tests/test_inc4_census.py` collects **3**,
`test_search.py -k "at_022 or at_023 or at_051 or at_053 or p052_2 or cd6a or above_the_render_bound"`
collects **10**, `test_fold.py -k "at_046 or at_047"` collects **4**.

### 4.9 · Ruff — SET comparison at identical scope

```
scope: mapper/ tests/     entry: 27 findings     exit: 27 findings
NEW  (in exit, not entry): (none)
GONE (in entry, not exit): (none)
```

Compared as sorted sets, not as counts. Dropping the now-unused `bindings_for` import from
`test_inc3_census.py` is what keeps the set identical rather than gaining an `F401`.

### 4.10 · Terminal size discipline

Every Pilot predicate runs at the declared **118x34** and **asserts the configuration it asked for
is the one it got** before reading anything. `AT-046` and `AT-047` additionally run at **80x24**,
where both the rail and the inspector auto-hide (asserted `display is False`, so the carry-B-54
configuration is pinned rather than stumbled into) and the pill title genuinely truncates —
`PRED-B` is the truncation-tolerant predicate and truncation has to actually happen.

### 4.11 · Fixture and byte hygiene

Every fixture is built by `tests/inc4_support.build_adjuntos` into the pytest `tmp_path` workspace;
nothing under `fixtures/` is written or read for the new arms. The hostile query is built from its
**code point** (`U+202E`) at test time and is never spelled into any source file — and, per `C-56`,
is not spelled into this artifact either, only named.

---

## 5 · Risks

1. **The one-time declaration is scoped to a `MapScreen` INSTANCE, not to the process.** Opening a
   linked map declares again. A process-wide flag is class state shared by every screen and by every
   test in a run, which is a worse trade; `AT-051b`'s own wording ("on a fresh `MapScreen`") reads
   the same way. **Declared, not hidden.**
2. **The declaration lingers in the toast strip on the search-live path.** With a query live, press
   one declares and walks; press two walks and paints no toast, so the declaration is still on
   screen. That is the shipped behaviour of every toast in this product (`guardado`, `exportado`),
   and `P-051b.2` is asserted on the path the predicate names — where press two paints `E1b` and the
   declaration is gone. A reviewer who wants "one-time" to mean "cleared on the next press" should
   say so; it is one line and I did not add it unasked.
3. **New copy that no `shall` clause owns**: `búsqueda sin evaluar` / `el mapa supera el límite de
   <N> nodos` (§1.6 C) and the `abrió «…» · ` hint prefix. Both are gated and both are declared;
   both are wording decisions a ux lens may want to rule on.
4. **`E1b` fires for a submitted whitespace-only query**, because the walk uses
   `query_text.strip()` — the same predicate `_count_line` already uses, where a blank query and a
   never-searched screen are declared to be the same state (`LLR-N07.3.3`). Consistent, and stated
   because "no search ever submitted" reads narrower than what ships.
5. **`esc` uses the same `strip()` predicate**, so a submitted whitespace-only query is *not* "live"
   and `esc` pops. Consistent with 4; a `"   "` left in `query_text` on a popped screen is inert.
6. **The `AT-047` pill oracle matches on a 6-character title stem**, not on the reconstructed
   `_clip` image `02l` §7.9 describes. The stems are asserted mutually distinguishing at run time,
   and both pills are asserted painted **before** anything is walked, so "the pill is gone" cannot
   be green because it was never there. A narrower width than 80 columns could clip below the stem;
   both tested widths are asserted to paint both stems first.
7. **Untouched by choice**: `views/`, `search.py`, `store.py`. The seat's fourth collision
   participants (`Inc-8`, `Inc-9`) will find `map/M` in `view` and `map/N` in `nav`.

---

## 6 · Pending items

- **NOT COMMITTED.** `tests/test_inc4_census.py` is **staged** (`git add`) because `test_a3_census`
  fails any untracked file under `tests/`; nothing is committed.
- `UX-Q3-a` (committed vs editing tone for the query chip) remains **unowned and unshipped** —
  `02l` §8.5, carried by the batch, not by this increment.
- `AT-024` remains `Inc-5`'s; five of six renderers are still query-insensitive.
- The unbounded pagination meter (`per_page = max(1, total)`) is still pre-existing at `HEAD` and
  still carried to `Inc-REPAIR`.
- The operator-username carry opened at Inc-4a round 4 is untouched here; this artifact uses
  repo-relative paths only.
- `test_cd25a_no_chord_collides_on_entry_or_on_exit` (Inc-3's) reconstructs a seat that is no longer
  Inc-3's entry. Documented in place; a later increment may want to freeze it the same way.

## 7 · Suggested next task

**Independent code review and security review of this increment**, then `Inc-5` (`AT-024`: the
remaining renderers paint `state.hits`), which is where `02l` §7.7's two recorded defects — the
threshold worded against text rather than style spans, and the renderer-set derivation sweeping in
the `IRenderer` Protocol — have to be resolved before its census can be written.

---

## Evidence checklist

- [✓] **Tests/type checks/lint pass** — `843 passed, 17 deselected, 3 xfailed`, exit 0, zero FAILED,
  read from that run's own output; slow lane `17 passed`; ruff SET identical at identical scope.
- [✓] **No secrets in code or output** — no credentials, tokens or `.env` touched; the only
  interpolated operator input is the search query, and it is routed through `darkside.plain`.
- [✓] **No destructive commands run without approval** — no commit, no push, no force, no deletion.
  `git add` of one new test file, required by `test_a3_census`, and declared.
- [✓] **File count within cap** — **2 source files**, the declared budget; tests uncapped by §5.4.
- [✓] **Review packet attached** — this file.
- [✓] **Mutation evidence** — 16 arms, 16 RED, 16 byte-identical sha256 restores, applied-digest line
  per row; paired arms shown failing at *different* assertions.
- [✓] **No mutated token or hostile code point spelled** in this artifact — described by position and
  operation, characters named (`U+202E`), per `C-56`.

---

# Review round 2

**Both gates returned. Code review: BLOCK on 2 HIGH. Security: SIGN-OFF with 2 MEDIUM.**
Both HIGHs were test-only, exactly as the reviewer found — **no production code was changed to
"fix" either**, because the shipped behaviour was already correct in both cases. The two MEDIUMs
and both LOWs are also addressed. One MEDIUM fix required a **second attempt**: the recommended
form was measured failing at the narrower declared size, and the arm that caught it is the reason
this section can say so.

Suite **847 passed / 17 deselected / 3 xfailed, exit 0, zero FAILED**, one complete run, read from
its own output. Slow lane **17 passed**. Ruff SET over `mapper/ tests/` **identical to the entry
pin** (27 = 27, zero NEW, zero GONE), diffed as sorted sets. **Source file count still 2**;
`mapper/keymap.py` was not touched this round.

---

## R1 · What changed

### R1.1 · `H1` — the walk's primary entry path was DEAD to the entire suite (HIGH)

`_walk_hits` picks its first target two ways. The `else` limb — taken whenever the cursor is **not
itself a match** — was executed by no test in the suite. This is not a corner: nothing in
`on_input_submitted` moves the cursor onto a hit, so an operator searching for something away from
where they stand takes this limb on their very first `n`. `AT-022` missed it for a fixture reason,
not a design one: on `adjuntos` the resting cursor `riesgo-root` happens to be in the hit set.

**Fix: one new arm, `test_at_022b_the_walk_enters_from_outside_the_hit_set`** (`tests/test_search.py`).
The cursor is placed on a node the index does not match — the precondition is enforced by
**construction**, so a fixture in which everything matched raises `StopIteration` at the selection
rather than passing while testing nothing — and the **self-guard** covers the seam construction
cannot see: the arm resolves hits through `SearchIndex` while the walk reads `_search_order`, so the
guard is taken **after `submit`, against `_search_order()` itself**, and fails exactly when those two
resolutions diverge — the shape of `M-N07.3-a`. **Both directions** are checked: `n` must land on the
first hit in tree order, `N` on the last, each re-entered from outside.
*(Round-2b correction: the first wording of this paragraph, and the docstring it described, claimed
the precondition was ASSERTED. It was not — the assertion so labelled was a tautology. Closed as
`NEW-1`; see "Round 2b" at the end of this artifact.)*

**The `N` limb is the half that matters, and that is now measured rather than argued** — see `R4`
mutation `R1b`. No production code moved.

### R1.2 · `H2` — `AT-047` could not fail on the re-close defect it exists to catch (HIGH)

`_unfold_onto` promises the branch is not re-closed *when the walk moves past it*. `AT-047`'s single
further press does not move past it: on this fixture the walk lands on `d`, opens `b`, and the next
hit `e` is **still inside `b`**. So an implementation that re-closes on every advance re-opens on
that same press and is indistinguishable. Round 1's `M4` is a genuine mutant but a degenerate one —
it corrupts the frame it just painted, which any frame-reading assertion catches.

**Fix: the single press is replaced by a walk that is asserted to leave the branch** — a bounded
loop that breaks when the cursor is outside the pre-walk hidden set, followed by
`assert screen.nav.cursor not in hidden` — with the existing `_pill_titles` assertions unchanged.
The section header's `PRED-C` wording is corrected from "after one further press" to "once the walk
has moved OUT". No production code moved.

### R1.3 · `M1` — `esc` and the hint line disagreed about "a live search" (MEDIUM)

Two guards described the same state and were written differently. Above the render bound the hint
promised nothing while `esc` cleared anyway: no pixel changed, the map did not close, and the
operator had to press `escape` twice — a keypress silently swallowed, the inverse of the defect
`#D38` fixed.

**Fix: one predicate, `MapScreen._search_is_live()`**, consumed by `on_input_submitted` and by
`action_back_or_home`. It puts **two new rows in `_PASS_FREE_READERS`** (`_search_is_live` and, by
transitive closure, `action_back_or_home`), each with a stated reason. That is the entry-obligation
arm working as designed: a consolidation is exactly the kind of edit that grows the derived reader
set, and it has to declare itself. Mutation `R9` proves the new exemption is load-bearing.

### R1.4 · `M2` — the fold-auto-open hint was unbounded file-derived text driving layout height (MEDIUM)

`abrió «{names}»` prepended an unbounded join of branch **titles** ahead of the affordances, and
`HintLine` wraps rather than clips, so the strip grew and took its rows from the canvas.

**Fix: `MapScreen._hint_with_opened(hint, opened, width)`**, with three guards:

1. **Order** — the names go **after** the affordances, so a wrap that still happened could only push
   the announcement off, never `esc limpiar`.
2. **Count** — at most `_HINT_BRANCHES` (3) names, then `+N`.
3. **Width** — the name gets the row's remainder, capped: `min(_HINT_BRANCH_CELLS,
   width - len(hint) - _HINT_NAME_OVERHEAD)`, truncated with the existing `darkside.fit`. Below
   `_HINT_NAME_MIN_CELLS` the announcement is **dropped**: the affordances outrank it.

**Guard 3 is not what the review recommended, and the difference was forced by measurement.** The
recommended fixed `darkside.fit(names, 40)` holds at 118 columns and **wraps at 80**, where the
wrapped strip's region then read back **empty** — `limpiar` gone again, by a different mechanism, on
a build that passed at 118. This is precisely the condition the security review recorded as *could
not determine*. It is now determined: **yes, it is worse at narrower widths**, and mutation `R6`
reddens on exactly that.

### R1.5 · The two LOWs

- **`C-D6a`'s docstring overstated what is enforced.** Corrected in `tests/test_search.py` and in
  `_walk_hits`'s own docstring: the teeth are `used == {"_search_order"}`; the no-`BoolOp` check is
  a **coarse second belt**, and a second result set named outside the vocabulary regex and combined
  by concatenation satisfies both assertions. The claim is now "the two **named** shapes of
  `M-N07.3-a` are structurally unavailable", not "unwritable". **The rule was not weakened.**
- **`_branch_name`'s bare subscript** now reads `self.graph.nodes.get(nid)` and falls through to the
  existing id arm. Latent, not reachable from file data. **Mutation `R7` reverts it and SURVIVES the
  whole lane — declared below, not hidden.**

---

## R2 · Files modified this round

| File | What |
|---|---|
| `mapper/app.py` | `_search_is_live`; `_hint_with_opened` + 4 module constants; `on_input_submitted` and `action_back_or_home` now share the predicate; `_branch_name` `.get` guard; two docstring corrections |
| `tests/test_search.py` | **NEW** `test_at_022b_…`; **NEW** `test_esc_and_the_hint_line_agree_…`; 2 rows in `_PASS_FREE_READERS`; `C-D6a` docstring corrected |
| `tests/test_fold.py` | `AT-047` walk-out predicate + `PRED-C` wording; **NEW** `test_the_opened_branch_name_cannot_push_esc_limpiar_off_the_frame` × 2 sizes |
| `.dev-flow/…/increment-004b.md` | this section |

**Source file count: 2** (`mapper/app.py`, `mapper/keymap.py` — the latter unchanged this round).
Tests uncapped, as declared. **NOT COMMITTED**; `HEAD` is still `a971432`.

---

## R3 · Test results

### R3.1 · Exit, one complete run

```
847 passed, 17 deselected, 3 xfailed in 180.32s     exit 0     zero FAILED
slow lane: 17 passed, 850 deselected in 23.70s
collection, all markers: 867 tests collected
```

**Ledger:** round-1 exit 843 passed + 3 xfailed = 846; **A = 4**, D = 0; post = 850 → measured
847 + 3 = **850** ✓. All-markers 863 + 4 = **867** ✓. The four:

- `test_search.py::test_at_022b_the_walk_enters_from_outside_the_hit_set` — 1
- `test_search.py::test_esc_and_the_hint_line_agree_about_what_a_live_search_is` — 1
- `test_fold.py::test_the_opened_branch_name_cannot_push_esc_limpiar_off_the_frame` — 2 (both sizes)

`AT-047` was strengthened in place and adds no node.

### R3.2 · Expected arm counts, re-asserted

```
tests/test_inc4_census.py                                                    ->  3   (unchanged)
test_search.py -k "at_022 or at_023 or at_051 or at_053 or p052_2 or cd6a
                   or above_the_render_bound or esc_and_the_hint_line"       -> 12   (was 10)
test_fold.py -k "at_046 or at_047 or esc_limpiar_off_the_frame"              ->  6   (was 4)
```

### R3.3 · Ruff — SET comparison at identical scope

```
scope: mapper/ tests/     entry (a971432): 27 findings     exit: 27 findings
NEW  (in exit, not entry): (none)
GONE (in entry, not exit): (none)
```

Compared as sorted sets over a clean `a971432` checkout in the mirror, not as counts. This closes
the review's "the count agreeing is not the same claim" caveat.

### R3.4 · Seat measurements, re-run on the exit tree

`bindings_for("map")` is the instrument `C-D25a` uses, and it reads **33**, not 31:

```
len(KEYMAP)              = 54
len(bindings_for("map")) = 33          rows with scope == "map" = 31
duplicate_chords()       = []
whole-seat sha256        = 46ac9fbbf6ddea78…f06c9a7cb    (identical to §4.4's declared exit)
map-seat  sha256         = e28134fb5182eafd…c922fec92
```

`mapper/keymap.py` is byte-identical to round 1 (`sha256 3846c22e…28d7c159`), so this is a
confirmation, not a change.

---

## R4 · Mutation ledger, round 2

Mirror: `git clone --local --no-hardlinks` of the repo at `a971432`, working tree of `mapper/` and
`tests/` overlaid, `tests/test_inc4_census.py` staged (the real repo has it staged; a fresh clone
does not, and `test_a3_census` fails an untracked file by design). **Overlay fidelity established
BEFORE any mutation** by sha256 against the real repo on all five touched files, and by a full run:
`847 passed, 17 deselected, 3 xfailed` — identical to the exit lane.

Mutations are described **by position and operation; no mutated token is spelled**. Every row
carries the applied digest and a restore verified by sha256 against the pristine value
(`mapper/app.py` = `6f0f1461…95c0b51`).

| Id | Operation | Selector base | Mutated | Verdict |
|---|---|---|---|---|
| `R1` | `app.py` — the else-limb's two endpoints exchanged | 2 passed | **1 failed** | RED |
| `R1b` | `app.py` — the else-limb's conditional collapsed to its forward arm | 2 passed | **1 failed** | RED |
| `R2` | `app.py` — the else limb's body replaced by a raise | 847 passed | **3 failed, 844 passed** | RED |
| `R3` | `app.py` — the opened set recorded, then re-added to `folded` at the TOP of the next call (re-close on advance) | 4 passed | **2 failed** | RED |
| `R4` | `app.py` — `_search_is_live`'s second conjunct dropped | 3 passed | **2 failed** | RED |
| `R5` | `app.py` — the cell bound removed from the name segment | 4 passed | **2 failed** | RED |
| `R6` | `app.py` — the width term removed from the budget (fixed cap) | 4 passed | **1 failed** | RED |
| `R7` | `app.py` — the `_branch_name` `.get` guard reverted to a subscript | 847 passed | **847 passed** | **SURVIVES** |
| `R8` | `app.py` — the branch COUNT cap removed from the name join | 4 passed | **4 passed** | **SURVIVES** |
| `R9` | `test_search.py` — the new `_search_is_live` exemption row removed | 1 passed | **1 failed** | RED |
| `R10` | `app.py` — the announcement suppressed (early return) | 4 passed | **4 failed** | RED |

**11 mutants run: 9 RED, 2 SURVIVING — both survivors predicted in advance and both declared.**
*(Count corrected by the orchestrator at the gate: the round-2 prose first read "10 run", which
does not reconcile against 9 RED + 2 surviving. The table has always carried eleven rows —
`R1b` is a distinct mutant with its own base, its own mutated verdict and its own target arm,
not a variant of `R1`. Nothing measured changed; the arithmetic did.)*

### R4.1 · Arm independence, located rather than asserted

```
R1  -> assert 'c' == 'riesgo-root'                        (AT-022b, forward limb)
R1b -> assert 'riesgo-root' == 'c'                        (AT-022b, BACKWARD limb; forward PASSED)
R3  -> "b's fold pill is painted again: ['Contratos en …', 'Auditoria']"   (AT-047 P-047.1)
R4  -> assert hint != 'sin coincidencias · esc limpiar'   (the above-the-bound arm)
R4  -> assert 'limpiar' not in <hint>                     (the esc arm — a DIFFERENT node)
R5  -> assert 5 == 1  at 118x34   and   assert 7 == 1  at 80x24
R6  -> assert 2 == 1  at 80x24 ONLY; 118x34 PASSED under the same mutation
R10 -> assert 'Contratos en riesgo' in <hint>  (AT-046)   and   assert 'abrió' in <hint>
```

**`R1b` is the receipt the review asked for.** A one-sided endpoint typo — the natural one — leaves
the forward limb correct and is caught **only** by the `N` assertion. A forward-only arm would have
shipped green.

**`R6` is the receipt that the second terminal size earns its place.** It is the shipped code's own
first-attempt fix, and it passes at 118x34 while reddening at 80x24.

**`R2` is the headline.** Before this round, replacing that limb's body with a raise left the whole
lane at **843 passed, zero failed** — the branch was unreached. It now reddens **three** nodes on
two independent paths (`AT-022b`, and both sizes of the hostile-title arm, whose cursor also starts
outside the hit set).

### R4.2 · The two survivors, and why they are declared rather than closed

- **`R7` — the `_branch_name` `.get` guard is not covered by any arm.** Predicted, and confirmed
  against the **whole lane**: 847 passed. The security review established the branch is not
  producible from file data (the loader synthesises a `Node` for every `.mmd` edge endpoint), so an
  arm would need an in-memory graph built specifically to reach it. **I did not add one**: it would
  pin a state the load path cannot produce, and the fix is a one-line fall-through with no
  behaviour to assert. Recorded as an uncovered line, not as a covered one.
- **`R8` — the branch COUNT cap is not covered either.** The fixture opens at most one branch per
  press, so `opened[:3]` and `opened` are the same list in every arm. Closing it needs a fixture
  with **four nested folds** hiding one hit. **Declared as uncovered.** The width budget (`R5`,
  `R6`) bounds the painted result regardless of the count, so the operator-visible claim is pinned
  even where the count cap is not.

### R4.3 · Calibration, taken and applied

The reviewer's own words are the standard this round was held to: *"I ran four mutations of my own
choosing; two survived. The '16 mutations, 16 RED' line should be read as evidence about the sixteen
mutants chosen, not as a mutation-adequacy claim about the increment."*

The same caveat binds this table. **`R1`–`R10` are evidence about ten chosen mutants.** Four of them
(`R3`, `R4`, `R9`, `R10`) were chosen specifically to attack arms I believed were **strong** — the
repaired `AT-047`, the new `esc` arm, the derived exemption table, and `AT-046` — and all four went
RED. Two more (`R7`, `R8`) were chosen because I believed they would **survive**, and both did.
**Round 1's ledger was honest and still missed both HIGHs**; a battery proves only the arms it fires
at, and this one is not offered as an adequacy claim.

### R4.4 · Integrity

The real repository was never mutated. All mutation work ran in the scratchpad mirror; every mutant
was restored and the restore verified by sha256 before the next was applied. At the end of the
round the real tree reads:

```
mapper/app.py        6f0f14614ff93fa8b3bee31d06339954cd3ae0e58149cb48e0159be7995c0b51
mapper/keymap.py     3846c22ebb2f69b5dc7589a0f29444c3e7f90845189b09a49def70d828d7c159
tests/test_search.py d66a21c385dee8ae349bde712daf06378971843a896babc395138335f007ab8f
tests/test_fold.py   420ba5fddb4f9559afed09c9e4c0ee990f24b0bdd744d5a6da289f85f49ea13b
HEAD = a971432, nothing committed
```

---

## R5 · Recorded, not fixed

### R5.1 · Security `F2` — measured NOT a regression, carried as pre-existing `S-15`

`_unfold_onto` duplicating the renderer's descendant traversal per keypress is real, and it is not
this increment's regression. Real key presses on the same 11k-node chain:

| chord | status | min |
|---|---|---|
| `l` child | pre-existing | 3723 ms |
| `h` parent | pre-existing | 3732 ms |
| `n` next_hit | **new** | 3706 ms |
| `N` prev_hit | **new** | 3735 ms |

`n` costs what `l`/`h` already cost. The multi-second figure is the **pre-existing repaint** — the
bound limits render count, not work — reachable today without this increment. **Recorded and routed
to `S-15`; deliberately not optimised here**, and Inc-4a's memo holds.

### R5.2 · The map body's unbounded content is a separate, pre-existing instance of `M2`'s class

Found while building `M2`'s arm, and it is why that arm drives a ~400-character title rather than
the ~2000 the review measured. At **80x24** with a ~2000-character node title, measured with
**nothing searched and nothing walked**:

- while the branch is folded, the **fold pill** carries the same unbounded title and the hint region
  sits at `y=59` of a **24-row** frame — the entire chrome is off-screen;
- after the branch opens, the **canvas** paints the long title as a node label and reads 9 rows
  against 27 for a normal title.

Neither involves any walk code, and both reproduce at `HEAD`. **Same class as the pagination meter
and as `_event_toast("guardado", <long title>)`; routed alongside them, not fixed here.** The new
arm carries an explicit self-guard that fails loudly if a future title length pushes the chrome
off-frame before the walk runs, so it can never silently start measuring that defect instead of
this one.

### R5.3 · Two uncovered lines, declared

`R7` (the `_branch_name` fall-through) and `R8` (the branch count cap) — see `R4.2`. Both are
shipped code no arm can currently redden, and both are stated here rather than left to be found by
the next reviewer's mutant.

---

## R6 · Risks added or changed this round

1. **`esc` above the render bound now POPS on the first press instead of clearing.** This is the
   intended resolution of `M1` and it is pinned in both directions, but it is a **behaviour change**
   on a surface the sealed text does not cover: above the bound the operator leaves the map on one
   `escape` and the (unpainted) query goes with the screen. The alternative resolution — make the
   hint promise `esc limpiar` above the bound too — was available and is the one a ux lens may
   prefer. **Chosen and declared, not absorbed.**
2. **The fold announcement can now be DROPPED entirely on a very narrow terminal** (below
   `_HINT_NAME_MIN_CELLS` of remaining room). No declared size reaches that, and the operator can
   still see the branch opened in the map; but `LLR-N06.2.4` says the system "shall paint the hint
   line naming the branch it opened", and this is a width at which it does not. Losing `esc limpiar`
   is the worse of the two failures, so the affordances win — **declared for the gate.**
3. **`_hint_with_opened` reads the `HintLine`'s current width**, which is the width *before* the
   update. If a previous frame had already wrapped the strip, the budget is computed one or two
   cells conservatively. It can only make the name shorter, never longer, so it cannot cause the
   defect it exists to prevent.
4. **`len(hint)` counts characters, not display cells.** Every character in the composed prefix is
   single-cell (seat glyphs are ASCII; the separators are `·` and `▸`), so the two agree today. A
   future seat row with a wide glyph would make the budget one or two cells optimistic — the arm at
   80x24 is what would catch it.

## R7 · Pending after this round

- **NOT COMMITTED.** `tests/test_inc4_census.py` remains **staged**; nothing else is staged.
- Everything under §6 of round 1 still stands (`UX-Q3-a` unowned, `AT-024` is Inc-5's, the
  pagination meter carried to `Inc-REPAIR`, Inc-3's reconstructed-seat arm).
- **New:** the unbounded-content class now has a third recorded instance (`R5.2`, the map body at
  80x24) to carry alongside the pagination meter.
- **New:** two declared-uncovered lines (`R4.2`).

## R8 · Suggested next task

**Re-review of these four fixes only** — they are narrow and every one is mutation-backed — then
`Inc-5` (`AT-024`) as before. A ux lens on `R6.1` (what `esc` should mean above the bound) and
`R6.2` (whether the fold announcement may be dropped) would settle the two wording decisions this
round created.

---

## Round-2 evidence checklist

- [✓] **Tests pass** — `847 passed, 17 deselected, 3 xfailed`, exit 0, zero FAILED, one complete
      run read from its own output; slow lane `17 passed`.
- [✓] **Ruff SET identical at identical scope** — diffed as sorted sets against a clean `a971432`
      checkout, not compared as counts.
- [✓] **Both HIGH findings closed test-only** — no production code changed for `H1` or `H2`.
- [✓] **Both MEDIUM findings closed**, one of them on the second attempt, with the first attempt's
      failure measured and pinned by `R6`.
- [✓] **Both LOW findings addressed** — one docstring correction (rule not weakened), one guard.
- [✓] **Mutation evidence** — **11** mutants (`R1` `R1b` `R2`…`R10` — `R1b` is a distinct mutant with its own verdict, not a variant of `R1`; the round-2 summary first said 10 and the table has always had 11), 9 RED, 2 predicted survivors declared; applied digest and
      sha256-verified restore per row; paired arms located at *different* assertions.
- [✓] **At least two mutants aimed at arms believed strong** — `R3`, `R4`, `R9`, `R10`; all four RED.
- [✓] **Seat re-measured on the right instrument** — `bindings_for("map")` = **33**.
- [✓] **No mutated token or hostile code point spelled** in this artifact — described by position
      and operation, per `C-56`.
- [✓] **No secrets** — nothing touched credentials, tokens or `.env`.
- [✓] **No destructive commands** — no commit, no push, no force, no deletion; the mirror lives in
      the scratchpad and the real tree is sha256-verified unchanged by anything but the declared edits.
- [✓] **File count** — 2 source files, the declared budget.

---

# Round 2b · `NEW-1` closed — the `AT-022b` self-guard made falsifiable

The confirmation pass returned **PASS**; one LOW remained. `NEW-1`: the assertion labelled
`SELF-GUARD` in `AT-022b` **could not fail**. `outsider` was selected by `nid not in found` and
`order` was built by filtering on `nid in found`, so `outsider not in order` was a theorem about
`order ⊆ found`, not a measurement. The **protection** was real — it came from construction, plus a
loud `StopIteration` if a fixture ever made everything a hit — so no verdict was ever false. What
was wrong was the **description**: the docstring and `R1.1` both named a mechanism that did not
exist, and a real seam went unwatched.

## R2b.1 · What changed — test-only, one arm

`tests/test_search.py`, `test_at_022b_the_walk_enters_from_outside_the_hit_set`:

- the selection of `outsider` is now commented as what it is — **construction**, with `StopIteration`
  as its loud failure mode — and asserts nothing;
- the self-guard **moves below `submit`** and is taken against **`screen._search_order() or ()`**,
  the resolution the walk itself reads.

**The seam it now covers.** The arm computes its hit set from `SearchIndex(...).query(...)`;
production resolves through `_search_order`. A **second, divergent resolution** — the shape of
`M-N07.3-a`, and the exact defect `US-N07` exists to close — would place the cursor node inside
*production's* hits while the arm still believed it outside, silently returning the press to the
`in hits` limb this arm exists to avoid. The guard now pins the arm's hit set to production's.

**Corrected wording, docstring** (replacing "THE PRECONDITION IS ASSERTED, NOT ASSUMED…"):

> THE PRECONDITION IS ENFORCED BY CONSTRUCTION, AND THEN PINNED TO PRODUCTION. The cursor node is
> SELECTED as one the index does not match, so a fixture in which everything matched raises
> `StopIteration` at the selection rather than passing while testing nothing. What construction
> cannot see is the seam the self-guard covers: this arm resolves the hit set through `SearchIndex`,
> while the walk reads `_search_order`. A SECOND, DIVERGENT RESOLUTION — the shape of `M-N07.3-a`,
> and the exact defect `US-N07` exists to close — would put this node INSIDE production's hits while
> the arm still believed it outside, silently returning the press to the `in hits` limb. So the guard
> is taken after `submit`, against the order the walk itself reads, and it is that divergence and not
> the fixture that it can fail on.

`R1.1` above is amended to match, with the correction marked in place.

**No production code changed.** `mapper/app.py` sha256 is unmoved from round 2 (below).

## R2b.2 · Discharge — the new guard measured RED, and the old one measured inert

A guard that could not fire is the class this batch exists to catch, so the replacement is
**measured, not argued**. Mirror as in `R4`: `git clone --local --no-hardlinks` at `a971432`,
working tree overlaid, `tests/test_inc4_census.py` staged. Overlay fidelity established by sha256
against the real repo **before** any mutation (`mapper/app.py 6f0f1461…95c0b51`,
`tests/test_search.py fe5dd6de…51b9cdb`) and by a green base on the selector. Mutation described
**by position and operation; no mutated token is spelled** (`C-56`).

**`N1` — `_search_order`'s resolution assignment replaced by a second, independently built result
set over the whole graph rather than the query** (a divergent second resolution: `M-N07.3-a`'s
shape). Applied digest `f2f6c69b…93ce9eac`.

| Form of the guard | Selector base | Mutated | Assertion that fired | Verdict |
|---|---|---|---|---|
| **shipped** (after `submit`, vs `_search_order()`) | `test_search.py -k at_022` → 2 passed | **2 failed** | the SELF-GUARD itself, `test_search.py:1378` | **RED — guard fires** |
| **pre-fix** (assertion reverted to its round-2 shape and position; docstring left as shipped) | same 2-arm base | 1 failed | `test_search.py:1397`, the backward-limb landing | guard **PASSED** |

Located, not asserted:

```
N1, shipped guard  -> AssertionError: SELF-GUARD: the cursor must start OUTSIDE the
                      resolution the WALK reads, ...
                      assert 'f' not in (('riesgo-root', 'b', 'c', 'd', 'e', 'f'))
                        where (...) = _search_order()
N1, pre-fix guard  -> execution reached :1397 -- the guard above it did not fire
                      assert 'e' == 'c'          (the endpoint comparison, downstream)
N1, AT-022 (peer)  -> assert ['b','c','d',...] == ['b','d','e',...]  at :1311
```

**Read honestly:** `N1` reddens the *arm* in both forms — the downstream endpoint assertions catch
it too. What the fix buys is that the assertion **labelled** SELF-GUARD is the one that fires, at
the seam, naming the divergence; in the pre-fix form that same assertion **passed under exactly the
divergence it claimed to watch**, which is the finding. This is a falsifiability repair, not a new
detection claim, and it is not offered as one.

**Restore, verified.** `mapper/app.py` and `tests/test_search.py` restored in the mirror and
re-hashed to their pre-mutation values, with the selector green again:

```
mapper/app.py         6f0f14614ff93fa8b3bee31d06339954cd3ae0e58149cb48e0159be7995c0b51   (pristine)
tests/test_search.py  fe5dd6de6c49a660ec949aa0325ee162a18a697c5640e74b7c9379ebe51b9cdb   (exit value)
tests/test_search.py -k at_022  ->  2 passed, 28 deselected
```

The real repository was never mutated; all mutation work ran in the scratchpad mirror.

## R2b.3 · Full lane, re-run

```
847 passed, 17 deselected, 3 xfailed in 175.02s     exit 0     zero FAILED
```

Read from that run's own output. Unchanged from the round-2 exit: this round adds no node and
removes none.

**Expected arm counts, re-asserted (collect-only, unchanged):**

```
tests/test_inc4_census.py                                                    ->  3
test_search.py -k "at_022 or at_023 or at_051 or at_053 or p052_2 or cd6a
                   or above_the_render_bound or esc_and_the_hint_line"       -> 12
test_fold.py -k "at_046 or at_047 or esc_limpiar_off_the_frame"              ->  6
```

**Ruff — SET comparison at identical scope, still at the entry pin:**

```
scope: mapper/ tests/     entry (a971432): 27 findings     exit: 27 findings
NEW  (in exit, not entry): (none)
GONE (in entry, not exit): (none)
```

Diffed as sorted sets, not as counts.

## R2b.4 · Files modified this round

| File | What |
|---|---|
| `tests/test_search.py` | `AT-022b` — guard moved below `submit` and pointed at `_search_order()`; docstring paragraph corrected |
| `.dev-flow/…/increment-004b.md` | `R1.1` corrected in place; this Round-2b section |

**Source file count: 0.** No production code moved. **NOT COMMITTED**; `HEAD` is still `a971432`.

Exit tree:

```
mapper/app.py        6f0f14614ff93fa8b3bee31d06339954cd3ae0e58149cb48e0159be7995c0b51  (unchanged)
mapper/keymap.py     3846c22ebb2f69b5dc7589a0f29444c3e7f90845189b09a49def70d828d7c159  (unchanged)
tests/test_fold.py   420ba5fddb4f9559afed09c9e4c0ee990f24b0bdd744d5a6da289f85f49ea13b  (unchanged)
tests/test_search.py fe5dd6de6c49a660ec949aa0325ee162a18a697c5640e74b7c9379ebe51b9cdb  (this round)
```

## R2b.5 · Round-2b evidence checklist

- [✓] **Full lane re-run** — `847 passed, 17 deselected, 3 xfailed`, exit 0, read from that one run's
      own output.
- [✓] **Ruff SET at the entry pin** — 27 = 27 over `mapper/ tests/`, zero NEW, zero GONE, compared as
      sorted sets.
- [✓] **New guard shown RED** — `N1`, per-arm verdict tabled, the guard itself identified as the
      firing assertion at `test_search.py:1378`.
- [✓] **Old guard shown inert under the same mutant** — execution reached `:1397`; the guard did not
      fire. The finding is reproduced, not taken on trust.
- [✓] **Expected arm count asserted** — 3 / 12 / 6, collect-only, unchanged.
- [✓] **Mutation described by position and operation** — no mutated token spelled (`C-56`).
- [✓] **Restore proven by sha256** — both files returned to their pre-mutation digests, selector
      green after restore; real tree never mutated.
- [✓] **No production change** — `mapper/app.py` digest identical to round 2.
- [✓] **No secrets, no destructive commands, no commit.**
- [✓] **File count** — 1 test file + 1 artifact; 0 source files.

## R2b.6 · Declared, not mine

At the moment this round started, `git status` did **not** list
`.dev-flow/…/01-requirements.md`; at exit it does, carrying the `NEW-2` threshold amendment and the
`NEW-3` width proviso (dated 2026-08-29). That edit was made outside this round and is **not** part
of it. Recorded here so the exit tree's modified-file set reconciles rather than surprising the next
reader.
