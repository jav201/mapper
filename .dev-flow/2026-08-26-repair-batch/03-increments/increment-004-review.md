# Increment 004 — independent code review

| Field | Value |
|---|---|
| Batch | `2026-08-26-repair-batch` |
| Increment | `004` — S-07 (`HLR-R04`) and S-08 (`HLR-R05`) |
| Reviewer | `code-reviewer`, independent of `software-dev` |
| Base | `origin/master` @ `d6b60e6b4f18b10123fffc76bbb36891473df653`, nothing committed |
| Date | 2026-08-27 |

---

## BLUF — **BLOCKED**

**One HIGH.** `AT-R14`, the node this increment nominates as the guarantor of every
other S-08 result, **does not guard the clip dimension its own requirement names.**
Measured on the pre-fix tree: an oracle that drops the *column* clip and keeps the
*row* clip reports `AT-R12` as **10 of 27 missing instead of 11** — `cobertura`
falsely satisfied by `MapScreen`'s keybar showing through the `ModalScreen`
backdrop, which is verbatim the hazard `01-requirements.md:219-223` says `AT-R14`
exists to prevent — and **`AT-R14` stays GREEN**. The single arm `L8` mutates both
clip conjuncts at once, so its one RED is attributable only to the row clip. Gate
checklist item 7 ("the acceptance oracle is itself guarded") is signed ✓ on this.

The fix is roughly four lines in the test file and does not touch `mapper/`.

**Everything else in this increment holds up, and much of it holds up unusually
well.** The fix itself is correct and minimal, all seven reported numbers reproduce
exactly, the regression claim is true, and three of the four battery arms I
re-executed reproduced their declared RED sets node-for-node. The `L4`/`L4b`/`L4c`
reasoning — which I went in expecting to be a rationalisation — is **correct and
substantiated by execution**. One MEDIUM concerns a factually false sentence in the
evidence record, not the code.

---

## What I established independently

All work on copies under the session scratchpad. The repo was never mutated: the
three files' sha256 at the end of this review are byte-identical to their values at
the start, and `git status --porcelain` is unchanged at 20 entries. All scratch
copies have been deleted.

### The seven numbers — all reproduce

| Claim | Command | Measured | Verdict |
|---|---|---|---|
| suite 425 passed | `pytest -q -p no:randomly -o addopts=` | `425 passed in 82.14s`, exit 0 | ✓ (wall clock 82 s vs 103 s — machine, not method) |
| ruff 29 | `python -m ruff check mapper tests` | `Found 29 errors.` | ✓ |
| new file 15 nodes | `--collect-only tests/test_repair_layout.py` | `15 tests collected` | ✓ |
| total 425 | `--collect-only` | `425 tests collected` | ✓ |
| ledger base 410 | `--collect-only --ignore=tests/test_repair_layout.py` | `410 tests collected` | ✓ `425 = 410 − 0 + 15` |
| sha256 ×3 | `sha256sum` on disk now | `3476bdf5…b9b001a5`, `832f6922…50a89fde`, `516a8756…84e8878a` | ✓ all three prefixes match §4 |
| byte counts | `wc -c` | 81 296 · 3 180 · 20 055 | ✓ |

Ruff attributable to the new test file: `ruff check tests/test_repair_layout.py` →
`All checks passed!`, so "29 before, 29 after" is sound.

### The regression claim — verified by construction, not by inference

I reverted **both** increment-4 source edits on an isolated copy and ran the
pre-existing set:

```
PRE-FIX tree, --ignore=tests/test_repair_layout.py   ->  410 passed in 81.10s
POST-FIX tree, full suite                            ->  425 passed in 82.14s
```

410 green before, the same 410 green after ⇒ **0 pre-existing nodes changed
verdict.** ✓ On the same pre-fix tree the new file resolved **10 failed, 5 passed**;
the 5 green pre-fix are `AT-R10b`, `AT-R14`, `TC-R25`×2, `TC-R26`, which is exactly
what their construction predicts.

`tests/test_rail.py` carries no assertion on the rail's painted region width — only
`rail_hidden` at `tests/test_rail.py:156` and the `RAIL_WIDTH` import at line 9 — so
the layout change could not flip it. `tests/test_repair_depth.py`'s golden constants
(`:94-122`) are keyed `(RendererName, w, h)` and hashed from `renderer.render(...)`
directly (`:183`), never from the compositor, so an allotted-width change is
structurally invisible to them. The packet's B3 reasoning is right.

### Battery arms re-executed on isolated copies

| Arm | Operation | Packet | Measured | Nodes |
|---|---|---:|---:|---|
| `L2` | the `#map-rail` rule's width declaration replaced by a fractional unit | 4 | **4** ✓ | `TC-R22`, `AT-R10`[size0], `AT-R10`[size1], `TC-R23` — and 421 others green |
| `L7` | `_render_keymap` iterates the whole seat instead of the scope's bindings | 4 | **4** ✓ | `TC-R25`[map], `TC-R25`[home], `TC-R26`, + `tests/test_palette.py::test_at_n03d`. `AT-R12`/`AT-R13` stayed **green**, which is precisely the packet's argument for `TC-R25`/`TC-R26` existing |
| `L8` | `_rows_in`'s two slice operations removed | 1 | **1** ✓ | `AT-R14` alone |
| `L4b` | container swapped for the non-scrolling sibling, CSS rule **kept** | 0 | **0** ✓ | 15 passed, and `max_scroll_y = 14` — the pane genuinely still scrolls |
| `L4c` | same, **and** the overflow declaration removed | 3 | **3** ✓ | `AT-R12` at all three sizes |

Every restore returned the file to its pre-mutation sha256.

### Framework claims — checked against Textual 8.2.8, not assumed

```
VerticalScroll.DEFAULT_CSS  ->  overflow-x: hidden;  overflow-y: auto;
Vertical.DEFAULT_CSS        ->  overflow: hidden hidden;
hasattr(MapScreen, "CSS")   ->  True
MapScreen.CSS               ->  ''      (defined on textual.screen.Screen)
"CSS" in MapScreen.__dict__ ->  False
```

`L4`'s no-op diagnosis is **true**. The C-15 inherited-attribute claim behind
`TC-R22`'s `__dict__` predicate is **true**.

### The oracle, measured at every size

```
140x45  dialog=Region(x=30, y=8, w=80, h=28)  pane h=24 virt=38 max_scroll_y=14
120x40  dialog=Region(x=20, y=6, w=80, h=28)  pane h=24 virt=38 max_scroll_y=14
100x24  dialog=Region(x=10, y=1, w=80, h=21)  pane h=17 virt=38 max_scroll_y=21
```

---

## Findings

### F1 — `AT-R14` does not guard the column clip, which is the one that matters  **[HIGH]**

**Where:** `tests/test_repair_layout.py:74-82` (`_rows_in`), `:85-101`
(`_rows_outside`), `:348-356` (`AT-R14`'s two limbs).

**What.** Limb (b) intersects two string populations that are structurally
incapable of meeting. `_rows_outside` appends `part.rstrip()` / `row.rstrip()`;
`_rows_in` returns fixed-width slices `r[region.x : region.x + region.width]`, which
are space-padded to the dialog's 80 columns. Measured on the shipped tree:

```
eligible inside rows (no trailing space) as shipped: 0 / 28
```

**Zero of the 28 rows limb (b) examines can match an entry in its own input set.**
The set intersection is empty for a reason that has nothing to do with clipping.

**Why it matters — and this is not theoretical.** I enumerated the clip's two
conjuncts separately against the pre-fix tree at 140×45:

```
PRE-FIX TREE, 140x45, no scrolling possible (S-08 present)
  SHIPPED  _rows_in (x+y clip)   AT-R12 missing=11/27   AT-R14 GREEN   cobertura missing? True
  x-clip DROPPED (y kept)        AT-R12 missing=10/27   AT-R14 GREEN   cobertura missing? False
  no clip at all (arm L8)        AT-R12 missing=10/27   AT-R14 RED     cobertura missing? False
```

The middle row is the finding. An oracle clipped in rows but not in columns
**under-reports S-08 by exactly the `cobertura` binding** — donated by `MapScreen`'s
keybar through `background: #000000 70%`, at y=11, which lies *inside* the dialog's
row band (y=8…35) and therefore escapes only via the column clip — and `AT-R14`
raises nothing. That is word-for-word the failure `01-requirements.md:219-223`
declares `AT-R14`'s reason for existing:

> *an unclipped read of the compositor composites `MapScreen`'s keybar through the
> translucent backdrop and counts `m cobertura` as a legend row — measured.*

`L8` removes **both** slice operations at once. It reddens by exactly one row — the
`HomeScreen` keybar line, the single frame row that reaches column 140 with no
trailing blank — so its RED is attributable to the row clip alone and certifies
nothing about the column clip. The packet's own C-55 table demands *"conjunctive
criterion, one mutation per conjunct"*; `_rows_in`'s clip is a two-conjunct
criterion and it received one arm.

This is the node the packet calls *"the arm that decides whether any other S-08
result is worth reading"* and on which gate checklist item 7 is signed ✓. A guard
that passes for a reason unrelated to what it certifies is false confidence, which
is the HIGH bar.

**Suggested fix** — assert the clip's geometry per conjunct, then compare on a
normalised form. Replace the body of `AT-R14` after `outside` is derived:

```python
        inside_raw = _rows_in(app.screen, dialog.region)
        # The clip is TWO-dimensional and the conjuncts fail differently.  A read
        # clipped in rows but not in columns still donates `cobertura` through the
        # translucent backdrop: measured on the pre-fix tree, AT-R12 under-reports
        # 10 missing instead of 11 while a set-intersection limb stays green.
        assert len(inside_raw) == dialog.region.height, (
            f"the oracle read {len(inside_raw)} rows for a {dialog.region.height}-row "
            "dialog; it is not clipped in y"
        )
        assert all(len(r) == dialog.region.width for r in inside_raw), (
            "the oracle returned rows wider than the dialog; it is not clipped in x, "
            "and MapScreen's keybar is being counted as a legend row"
        )
        # rstrip BOTH sides: `_rows_outside` rstrips its fragments while `_rows_in`
        # returns width-padded slices, so a raw intersection is empty by padding
        # rather than by clipping (measured: 0 of 28 rows even eligible to match).
        inside = {r.rstrip() for r in inside_raw if r.strip()}
        leaked = sorted(set(outside) & inside)
        assert not leaked, f"the oracle read {len(leaked)} rows from outside the dialog: {leaked}"
```

Measured discrimination of the `rstrip` half alone (the two geometry asserts add the
rest):

```
=== intersect on rstrip() both sides ===
  AS SHIPPED (x+y clip)        leaked=  0 -> GREEN
  y-clip only (x dropped)      leaked=  2 -> RED      <- currently GREEN
  NO clip at all (arm L8)      leaked= 13 -> RED      <- currently RED by 1
```

**Then re-run the battery with `L8` split into `L8a` (column slice removed) and
`L8b` (row slice removed)**, so each conjunct carries its own arm and item 7's ✓ is
earned rather than asserted.

---

### F2 — the `L5` "no-op mutation" diagnosis is false; `L5` is a genuine inert arm  **[MEDIUM]**

**Where:** `increment-004.md:167` and the surrounding §4 subsection *"The two inert
arms were not inert TESTS — they were no-op MUTATIONS"*; gate checklist item 5.

**What.** The packet retires `L5` on this claim:

> **`height: 90%` binds first** at every size under test — 90 % of 45 is 40, and 40 <
> 44 — so the dialog never changed size

I ran the arm and measured the dialog:

```
unmutated   140x45  dialog h=28   pane h=24  virt=38  max_scroll_y=14
L5 applied  140x45  dialog h=40   pane h=36  virt=38  max_scroll_y= 2
L5 applied  120x40  dialog h=36   pane h=32  virt=38  max_scroll_y= 6
```

**The dialog grows by twelve rows and the scrollable surplus collapses from 14 rows
to 2.** `max-height: 28` — not `height: 90%` — is the declaration governing the
dialog at both wide sizes; `90%` governs only at 100×24, where it yields 21. The
arithmetic in the packet is inverted.

The packet **contradicts itself on this exact point**: Risk 2 (`:264-265`) states it
correctly — *"At 140×45, `90%` is 40 and the cap clips to 28"* — while §4 uses the
inverted form to close the arm.

**Why it matters.** `L5` changed the governed property substantially and still
produced 0 RED. That makes it an **inert arm**, precisely the category the packet
itself says demands *"rewrite the predicate, do not re-argue it"*. It was re-argued,
on a premise that measurement refutes. Gate checklist item 5 — *"Inert arms named and
investigated, not excused"* — is signed ✓ on that premise and should read ⚠.

The substantive gap is narrow: everything still scrolls under `L5`, so no `HLR-R05`
promise is broken, and `L5b` correctly guards *"nothing needs to scroll any more"*
via `TC-R24`'s vacuity assertion. What nothing asserts is **which declaration governs
the dialog's height** — the packet's own Risk 2 / pending item 3.

**Suggested fix.** Correct §4's `L5` row and the no-op subsection to say what was
measured, and take one of two dispositions explicitly:

- **(a)** accept `L5` as an inert arm with a declared reason — *"the property it
  moves (dialog height) is not one `HLR-R05` constrains; reachability is guarded by
  `L5b`/`TC-R24`"* — and downgrade item 5 to ⚠ with that sentence as evidence; or
- **(b)** discharge pending item 3 now by collapsing `height: 90%` / `max-height: 28`
  to one governing declaration, which removes the ambiguity that produced the false
  reading in the first place.

`L4`'s no-op diagnosis is unaffected and stands — I verified it against
`VerticalScroll.DEFAULT_CSS`.

---

### F3 — `AT-R12`'s substring membership is shadowed for 2 of 27 labels  **[LOW]**

**Where:** `tests/test_repair_layout.py:293` — `b.label not in painted`, a substring
test over the joined painted rows.

**What.** Within `SCOPE_MAP`, two labels are proper substrings of others:

```
'siguiente' is contained in ['siguiente faltante']
'hijo'      is contained in ['agregar hijo']
```

Drop the `nav` bindings *siguiente* and *hijo* and `AT-R12` still finds their
characters inside the `view` and `node` rows. (`SCOPE_HOME` has no such pair.)
`AT-R12` also formats its failure message with `b.group`/`b.glyph` while testing only
`b.label`, so glyph/label pairing is unverified at the painted layer.

**Why it's LOW, not higher.** Losing a whole group still reddens on the other four
labels, and `TC-R25`'s `(glyph, label)` set equality closes both gaps exactly at the
white-box layer — `L7` confirms it discriminates. The split is declared honestly in
Risk 6. No false confidence in aggregate; worth a docstring line so the next reader
does not mistake `AT-R12` for per-label precision.

**Suggested fix.** One sentence in `AT-R12`'s docstring: *"membership is substring,
not row-exact; two labels are substrings of others (`siguiente`, `hijo`) and glyphs
are not checked here — `TC-R25` owns exact (glyph, label) equality."*

---

### F4 — `TC-R22`'s `__dict__` guard has a stylesheet-shaped hole  **[LOW]**

**Where:** `tests/test_repair_layout.py:155`.

`"CSS" not in MapScreen.__dict__` is the right correction to the `hasattr` trap and I
verified the trap is real. But Textual resolves screen styling from three places, and
the guard covers one: a `#map-rail` rule arriving on `MapScreen.DEFAULT_CSS` or via
`CSS_PATH` would leave both this guard and `TC-R22`'s read of `MapperApp.CSS` silent.
`TC-R23` catches the painted consequence, so this is completeness, not a live risk.

**Suggested fix.** Widen the membership test:

```python
    for attr in ("CSS", "DEFAULT_CSS", "CSS_PATH"):
        assert attr not in MapScreen.__dict__, (
            f"MapScreen has acquired its own {attr}; A-10's premise correction "
            "needs re-reading, and this rule may belong there after all"
        )
```

---

### F5 — pending item 1 mis-states what is left of `A-10`  **[LOW]**

`increment-004.md:292-295` says *"Amendment `A-10` needs writing into
`01-requirements.md` §6.5"*. **It is already there** — `01-requirements.md:513-544`,
with its Before/After text and verification note. What remains uncorrected is the
requirement body: `01-requirements.md:188` still reads *"Touched symbols:
`mapper/app.py` `MapScreen.CSS` `#map-rail`"*, and that line belongs to **`HLR-R04`**,
not to `LLR-R04.1` as both the packet and `A-10`'s Before text say.

**Suggested fix.** Restate the pending item as: *"`HLR-R04`'s touched-symbols line
(`01-requirements.md:188`) still names `MapScreen.CSS`; `A-10` at §6.5 records the
correction but the body was not edited."*

---

## What holds up

Stated plainly, because most of this increment is right and a blocking review should
not obscure that.

- **The fix is correct and minimal.** Two source files, one CSS rule each in
  substance. `#map-rail { width: 24; height: 100%; }` joins its `#map-canvas` /
  `#map-inspector` siblings; the `VerticalScroll` wraps only the bindings and leaves
  the title fixed, which is what `LLR-R05.1` asks for by its own wording. No
  speculative generality, no abstraction, no adjacent code touched.
- **The literal-not-f-string decision is right** and the comment at
  `mapper/app.py:1946-1951` explains why in the terms `LLR-R04.1` actually needs. An
  interpolated width would have made `TC-R22` an identity. `L2` and `L3` are the arms
  that prove the pair can disagree; `L2` reproduced 4 RED node-for-node.
- **`A-10` is a correct call.** `MapScreen` genuinely declares no `CSS`, verified;
  the sibling rules live on `MapperApp.CSS`; a second stylesheet for one rule would
  fork the convention. The premise was executed and corrected rather than the code
  bent — and the first correction being *also* wrong (the `hasattr` trap) is recorded
  rather than quietly fixed, which is the behaviour this batch is trying to build.
- **`L4b` is a legitimate pre-registered negative control, not a rationalisation.**
  I went in expecting the opposite. Measured: plain container + the CSS rule kept →
  15 passed with `max_scroll_y = 14`, so the pane really does still scroll and
  `#help-bindings { overflow-y: auto }` really is a second guard overriding
  `Vertical`'s `overflow: hidden hidden` (both `DEFAULT_CSS` values verified against
  Textual 8.2.8). Paired with `L4c` at 3 RED, the pair carries its claim. The packet's
  instinct to record the harness's `INERT` label as *"mechanically correct and
  substantively wrong"* was the right instinct and the right disposition.
- **`_rendered_pairs`'s parse survives the whole keymap.** I checked every glyph:
  `↵`, `/`, `=`, `esc`, `ctrl+p`, `?` and the single characters are all space-free, and
  `_render_keymap` emits `"  " + f"{glyph:<8}"` + label, so `line[2:]` +
  `partition(" ")` recovers each pair exactly. Group headers carry no leading spaces
  and are filtered at `:387`. More importantly the parse **cannot fail silently**: a
  dropped or mis-split pair changes the rendered set, and `TC-R25`'s equality is
  two-directional, so it reddens rather than weakening. The label-collision
  justification is real — `volver` names three bindings and `cerrar` three, verified
  in `mapper/keymap.py:128,136,139,142,146,147`.
- **`TC-R25` / `TC-R26` are not redundant.** `L7` reddens them (and one pre-existing
  palette node) while leaving `AT-R12`/`AT-R13` green — the packet's stated reason for
  the second layer, confirmed by execution rather than argument.
- **`AT-R10b` is a real discriminating negative**, green pre-fix as claimed, and it
  derives its size from the screen's own rule rather than hand-picking one.
- **`TC-R24`'s vacuity guard works as designed** and is the node `L5b` reddens.
- **`AT-R12`'s 60-iteration bound with `pytest.fail`** is the right shape — a
  non-terminating scroll must be a red, not a hang. At the three tested sizes the loop
  needs 2–3 iterations, so the bound is generous.
- **The three sha256 values, the byte counts, and the CRLF/LF endings** in §4's
  byte-scan are all exactly what is on disk right now.
- **`prototypes/**` untouched, frozen interfaces absent from the diff**, both
  confirmed against the diff.

---

## Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **Block — F1 (HIGH) must be fixed before advancing**

**To clear the gate:**

1. Apply **F1**'s fix to `AT-R14`, split `L8` into per-conjunct arms `L8a`/`L8b`, and
   re-run both. Item 7's ✓ is not earned until each conjunct has its own arm.
2. Correct §4's `L5` record per **F2** and downgrade gate item 5 to ⚠ with the
   measured numbers as its evidence, or discharge pending item 3.
3. **F3**, **F4**, **F5** are recommendations; none blocks.

Neither F1 nor F2 requires a change to `mapper/`. The suite should return **425
passed** unchanged after F1, since the fix strengthens a node that is green on the
correct tree — re-run the full suite to confirm, and re-run `L1`–`L3`, `L6`, `L7`,
`L5b` only if the test file's helpers are refactored beyond `AT-R14`'s own body.

Out of my lane and handed off: **`security-reviewer`** owns the C-family triggers
§7 names; **`qa-reviewer`** owns the whole-branch functional pass. I found nothing
security-shaped in this diff (two CSS rules and a container swap) and no coverage gap
beyond F1/F3, which are oracle-strength findings rather than missing cases.

---

## Evidence checklist

| # | Item | ✓/✗ | Evidence |
|---|---|:--:|---|
| 1 | Diff read in full | ✓ | `git diff -- mapper/app.py mapper/screens/help.py` read whole; `mapper/screens/help.py:1-94` and `mapper/app.py:1943-1951` read in place; **untracked `tests/test_repair_layout.py:1-428` read whole**, since `git diff` cannot show it |
| 2 | Correctness pass (edge / None / error paths) | ✓ | Layout measured at all three declared sizes; `_painted_bindings`'s scroll loop traced (2–3 iterations of a 60 bound, union covers rows 0–37 of a 38-row virtual height at every size); `_rendered_pairs` parse checked against every glyph in `mapper/keymap.py:87-151` |
| 3 | Simplicity pass (no premature abstraction) | ✓ | Two CSS rules and one container swap. No abstraction, no speculative parameter, no adjacent code touched. The literal-over-f-string choice is the *less* clever option and is the correct one — `tests/test_repair_layout.py:133-136` |
| 4 | Reuse / duplication checked | ✓ | `VerticalScroll` is the framework's own container, not a hand-rolled scroller; the rule joins its `#map-canvas`/`#map-inspector` siblings rather than opening a second stylesheet (`A-10`); `bindings_for` reused as the single source in both test layers |
| 5 | Tests reviewed for intent, not just behaviour | ✗ | **F1** — `AT-R14`'s limb (b) certifies "the read is clipped" but passes by string padding: 0 of 28 rows eligible to match, and the column conjunct is unguarded (measured 10-vs-11 under-report with the guard green). **F3** — 2 of 27 labels substring-shadowed |
| 6 | Verdict explicit | ✓ | **BLOCKED** on F1 |
| 7 | Numbers verified on disk, not from the packet | ✓ | 425 passed / 29 ruff / 15 · 425 · 410 collected / 3 sha256 / 3 byte counts — all re-measured, all match |
| 8 | Mutation protocol observed | ✓ | All work on copies under the session scratchpad; every restore verified by sha256; **repo sha256 unchanged and `git status` unchanged at 20 entries**; scratch copies deleted; `PYTHONDONTWRITEBYTECODE=1` with `__pycache__` purged per arm; one verdict per resolved node id, never the exit code; mutations described here by position and operation only (C-56) |
