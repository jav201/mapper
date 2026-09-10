# Confirmation Pass — Inc-STRIPS round 2 (`2026-08-26-ui-next-batch-02`, increment 007)

**Reviewer:** code-reviewer (confirmation pass, SERIAL — sole agent) · **Protocol:** FULL
**Subject:** `git diff HEAD -- mapper/ tests/` at the round-2 pins, plus `01-requirements.md`,
`.dev-flow/state.json` and `increment-007-strips.md` §8 treated as claims to check.
**Verdict:** **BLOCK** — **2 HIGH**

---

## BLUF

**Every round-1 HIGH is discharged, and the round-2 evidence ledger is accurate to the digit.**
`MUT-C` is killed by exactly the two acceptance arms; the declaration and legend survive the clip
at every title length and width the two reviews used; the cell budget is observed in the direction
that breaks the strip; `912 / 931 / ruff 27=27 / 1 source file` all reproduce.

**Two HIGHs are new, and both are the same shape as the ones round 1 blocked on — one in the code,
one in the ledger.**

1. **The declaration reserve is unconditional, and on the shipped `legacy` map it manufactures the
   omission it declares.** At 35x14 `legacy` (three branches) now draws **one** branch and declares
   `+2 ramas sin mostrar`. Before this increment it drew all three. Strip height is 3 both ways and
   **canvas height is 3 both ways** — the two branches bought nothing. Measured: with the 26-cell
   declaration reserve taken only when a remainder actually exists, all three names **and** the full
   legend fit in the same three rows. No arm can see this, and the conservation law is green by
   construction (`1 drawn + 2 declared == 3`). This is the direct answer to audit question 3.
2. **`01-requirements.md` marks predicate 1 `✅ CLOSED BY Inc-STRIPS`, unqualified — contradicting
   `state.json` in the same commit, which says the requirement is OPEN.** §8.7's re-scope is honest
   in the fold and honest in `state.json`; it did not reach the artifact of record. This is exactly
   the marking SEC-F2 blocked, reappearing one file over.

Four MEDIUMs follow, one of which is a round-2 claim that is false: §8.3 says CR-F5's meter comment
block was "corrected in place". It is **byte-identical** to round 1.

---

## Tree state during this pass — sole writer, asserted

| moment | `mapper/app.py` | `tests/test_strips.py` | `tests/test_pan.py` |
|---|---|---|---|
| entry | `5cf4b46055d21902` | `7ca0c255d13c4eb3` | `ae4cb900fd1167d9` |
| exit | `5cf4b46055d21902` | `7ca0c255d13c4eb3` | `ae4cb900fd1167d9` |

All three equal the declared pins at entry and exit. Nine mutants installed, each with the on-disk
digest asserted equal to the intended bytes **before** any verdict was read, the digest re-asserted
**unchanged across the run**, and the restore asserted equal to the pin in a `finally`. Every
anchor was matched at a verified occurrence count and every replacement was `ast.parse`-checked;
**no BAD/CRASH mutants occurred this pass, and none would have been reported as a survival.**
`git status --porcelain` is identical to entry; no `__pycache__` survives; `PYTHONDONTWRITEBYTECODE=1`
and `PYTHONUTF8=1` throughout. Layout probes were read-only (in-memory class attributes, restored
and asserted). All paths were Windows-absolute — the POSIX-path no-op hazard could not fire.

Baseline resolves **10 arms** (2 slow `AT` + 2 ceiling + 2 regression + 2 declaration + budget +
two-spellings), confirmed by every mutant run's `N failed + M passed == 10`.

---

## Per-finding disposition

| round-1 finding | disposition |
|---|---|
| **CR-F1** — acceptance predicate unsound both ways, numeric clause missing | **DISCHARGED** (with M3 attached) |
| **CR-F2 / SEC-F1** — declaration and legend clipped off the frame | **DISCHARGED** |
| **CR-F3 / SEC-F3** — `MINIMAP_BRANCHES` unoracled | **DISCHARGED** |
| **SEC-F2** — re-scope predicate 1 to the fanout vector | **NOT DISCHARGED** → **H2** |
| **CR-F5 / SEC-F5** — comments asserting the opposite of the code | **NOT DISCHARGED** → **M1** |
| **CR-F4** — reuse the `_HINT_*` row-remainder pattern | **DISCHARGED** (adopted and cited in place) |
| **CR-F6** — `filled = min(page, steps)` clamp vs "compressed scale" | **NOT DISCHARGED** → **L1** |
| **CR-F7** — module-level constant convention | **NOT DISCHARGED** → **L2** |
| **CR-F8** — `overflow: hidden` observationally inert | **NOT DISCHARGED**, and correctly so — CR-F8 said "do not drop before the cell bound lands". It has landed; re-test or name the case. |
| **CR-F9** — `#D28` cited for an escalation it does not make | **NOT DISCHARGED** (LOW, unchanged wording) |
| **SEC-F4** — `#map-toast` unbounded | **ROUTED** to `Inc-CRUMB` in `state.json` — correct |

---

## Audit 1 · Is CR-F1 closed? — **yes, both directions, measured**

`MUT-C` (drop `SEARCH_SUSPENDED_NOTICE` from the count region at `app.py:1976` only, leaving
`HintLine`'s copy at `:2647` intact):

```
===== MUT-C  installed 49438c4d7c9e6bca == intended 49438c4d7c9e6bca  OK
    FAILED test_at_llr_n07_3_4_the_count_is_READABLE_at_the_shipped_bound[118x34]
    FAILED test_at_llr_n07_3_4_the_count_is_READABLE_at_the_shipped_bound[80x24]
    2 failed, 8 passed in 30.80s
    hash stable across run: 49438c4d7c9e6bca
    restored 5cf4b46055d21902 == pin  OK
```

**KILLED by exactly the two acceptance arms** — not by the moved-bound `test_search.py` arms that
were the only killers in round 1. §8.4's headline claim reproduces.

At the two widths the review used, on the 12002-node graph with the review's own 64-character query:

| width | region carries notice | **new** region predicate | **old** whole-frame join |
|---|---|---|---|
| 50x34 | **no** (clipped — visible in the rows) | **False** ✓ | `True` ← the **false GREEN**, gone |
| 60x34 | yes (across a wrap) | **True** ✓ | `False` ← the **false RED**, gone |
| 80x24 | yes | True | True |
| 118x34 | yes | True | True |

**Both directions are closed.** The predicate now agrees with the region at the width where the old
one fabricated a match from `HintLine`, and at the width where the raw join destroyed one.

**One residual behaviour, not a regression and not claimed fixed:** at **50 columns** with a
64-character query the notice genuinely is clipped off `#map-pagination`. That is below both
declared widths and no arm drives it, but it is the live instance of the stale `_QUERY_ECHO_CELLS`
rationale in M1 — the comment says an over-long echo "GROWS the strip"; measured, it is now dropped.

---

## Audit 2 · Is CR-F2/SEC-F1 closed at the title lengths that broke it? — **yes, everywhere**

40 branches and 24 branches, 60-cell titles and short titles, at 118x34 / 80x24 / 60x34 — twelve
cells, all four columns green:

```
 branches  cells     size  h   decl legend drawn declared
       24      0  118x34   3   True   True    16        8
       24     60  118x34   3   True   True    16        8
       24     60   80x24   3   True   True     9       15
       24     60   60x34   3   True   True     6       18
       40     60  118x34   3   True   True    16       24
       40     60   80x24   3   True   True     9       31
       40     60   60x34   3   True   True     6       34
```

```
80x24, 40 branches, 60-cell titles:
|  cobertura   rama 0 xxxx… ░   rama 1 xxxx… ░   rama 2 xxxx… ░   rama 3 xxxx… ░ |
|rama 4 xxxx… ░   rama 5 xxxx… ░   rama 6 xxxx… ░   rama 7 xxxx… ░   rama 8 xxxx…|
|░   +31 ramas sin mostrar   █ completa ▒ media ░ baja ╱ sin datos               |
```

The 24-branch row — SEC-F1's sharper case, where nothing is "missing" by the increment's own
accounting and the legend was gone anyway — is green at every width tested. The truncation is
**visible** (`…`), which is the half of the recommendation that mattered.

`darkside.fit` is load-bearing and observed: replacing it with the old `darkside.plain`
(**`MUT-NOFIT`**) reddens both declaration arms.

---

## Audit 3 · Is the cell budget's arm sound, or another reader-as-oracle? — **the arm SET is sound; the conservation law alone is not, and the gap it leaves is H1**

The conservation law is a genuine improvement and is no longer reader-as-oracle: it compares the
**frame's** drawn count against the **code's** declared remainder, so a budget that over-allocates
is caught by the frame side rather than moving with the expectation.

**Fired in both directions** (the round-2 fold fired only the safe one):

| mutant | limit @118 | arms red | verdict |
|---|---|---|---|
| `_MINIMAP_ENTRY_OVERHEAD 5 → 0` (**over**-allocate) | 23 | **3** — both declaration arms **and the conservation arm** | KILLED |
| `_MINIMAP_LEGEND_CELLS 37 → 0` (under-reserve) | 18 | 2 (declaration arms) — conservation **green** | KILLED |
| `_MINIMAP_DECL_CELLS 26 → 0` (under-reserve) | 17 | 2 (declaration arms) — conservation **green** | KILLED |
| `_MINIMAP_NAME_CELLS 12 → 60` | 4 | 1 (declaration @118) | KILLED |
| `darkside.fit` → `darkside.plain` | — | 2 | KILLED |
| `MINIMAP_ROWS 3 → 4` | 21 | 4, incl. the two-spellings arm | KILLED |
| declaration deleted (`MUT-D`) | — | 4 | KILLED |
| `_MINIMAP_ENTRY_OVERHEAD 5 → 40` (**under**-allocate) | 5 | **0** | **SURVIVED** |

**So: can it pass while the strip is wrong? Yes — in exactly one direction, and the shipped code is
already in it.** Under-reservation is caught (the legend leaves the frame). Over-reservation is not:
every entry the budget declines to draw is faithfully declared, so conservation holds no matter how
few are drawn. `MUT-A`'s survival is not an isolated equivalence — it is the blind spot that let H1
ship.

---

## Audit 4 · Is `MUT-A` equivalent-by-contract? — **yes against the stated requirement, and §8.4's own caveat is the load-bearing sentence**

`01-requirements.md:37` states the outcome as *"nothing is hidden without being declared"*, and
`MUT-A` preserves it: fewer entries, all of them declared, conservation intact, legend intact.
No requirement predicate quantifies how many branches the strip must show. **§8.4's claim is
literally correct.**

**But the caveat it appends — "no predicate pins the *usefulness* of the tuning, only its
correctness" — is not a footnote; it is the whole finding.** §8.4 records the limit and then treats
the survival as benign. Measured, the unpinned dimension is where the increment regressed a shipped
map (H1). **Recommend §8.4 be restated:** `MUT-A` survives because the arms cannot see
over-reservation *in either the mutant or the shipped code*, and that is a coverage gap with a live
instance, not an equivalence.

---

## Audit 5 · Did the fold break anything? — **the pad is a real, undisclosed appearance change, and it is how H1 happens**

`darkside.fit` **pads to exactly N cells** (`darkside.py:431-438`). Diffed against `HEAD` on the
real `legacy` fixture and on synthetic maps, both trees driven through the real compositor:

```
=== legacy, 118x34 ===
HEAD |  cobertura   Finanzas █   RRHH █   Inventarios ░   █ completa ▒ media ░ baja ╱ sin datos|
NOW  |  cobertura   Finanzas     █   RRHH         █   Inventarios  ░   █ completa ▒ media ░ …|
```

Every branch name is now padded to a 12-cell column and every name **longer** than 12 cells is
truncated (`Modelo de datos` → `Modelo de d…`). Neither is mentioned anywhere in the packet. The
padding is defensible (aligned glyph columns) and the truncation is SEC-F1's own recommendation —
but 12 cells is tight for ordinary Spanish titles and the alignment is a shipped visual change to
every map. **Routed to `ux-reviewer`, not blocking.**

No test asserts the unpadded form, so nothing reddened. Suite deltas confirm it: `912`/`931` with
zero pre-existing arms moved.

---

## Audit 6 · §8.6's evidence — **confirmed, every line**

```
default lane : 912 passed, 19 deselected, 3 xfailed   exit 0   (202.36s)
all markers  : 931 passed, 3 xfailed                  exit 0   (254.63s)
ruff SET     : working tree 27, HEAD 27 — NEW: none, GONE: none   (--isolated, inside the repo,
                                            compared per (file, rule) from JSON output)
source files : 1  (mapper/app.py; tests/test_pan.py + tests/test_strips.py are tests)
```

Ledger arithmetic checks: `912 = 908 + 4` and `931 = 927 + 4`, the four being the declaration arm at
two sizes, the cell-budget arm and the two-spellings arm.

Reverse census re-swept: `_minimap_text` has **one** definition (`app.py:1789`), **one** production
caller (`app.py:2352`), **one** test caller (`tests/test_pan.py:241`). §8.5's disclosure is accurate.

---

## Audit 7 · §8.7's re-scope — **honest in the fold and in `state.json`; contradicted by the requirements file** → H2

`state.json` is exemplary: `open_blocks` stays **OPEN**, split into `vectors.fanout` (CLOSED) and
`vectors.title_length` (OPEN), `Inc-CRUMB` is inserted between `Inc-STRIPS` and `Inc-B55` with the
measurement and the "land the Python bound first" ordering carried, `recheck_at` moved to
`Inc-CRUMB` close, and the serial-review rule minted with credit to the security reviewer. The
scoping claim **does not overclaim** and the crumb is properly routed (not re-audited here, per
brief).

`01-requirements.md` does not follow. See **H2**.

---

## Findings

### H1 — The declaration reserve is unconditional, so on the shipped `legacy` map it drops branches to declare a remainder that would not otherwise exist [Severity: HIGH]

- **What:** `_minimap_entry_limit` subtracts `_MINIMAP_DECL_CELLS` (26) from the row budget
  **always**, including when every branch fits without it. The reserve manufactures the remainder it
  reserves for, and the declaration then honestly reports a loss the budget itself caused.

- **Where:** `mapper/app.py:1783-1789` (`_minimap_entry_limit`) — `reserved` includes
  `self._MINIMAP_DECL_CELLS` with no dependence on `len(children)`.

- **Measured, real `legacy` fixture (3 branches), both trees through the real compositor:**

  ```
  ### legacy 35x14   HEAD   minimap_h=3 canvas_h=3
     |  cobertura   Finanzas █   RRHH █|
     |Inventarios ░   █ completa ▒ media|
     |░ baja ╱ sin datos|

  ### legacy 35x14   ROUND 2   minimap_h=3 canvas_h=3
     |  cobertura   Finanzas     █   +2|
     |ramas sin mostrar   █ completa ▒|
     |media ░ baja ╱ sin datos|
  ```

  **Same strip height. Same canvas height. Two of three branches gone.** At 40x20 the same map loses
  one (`+1 ramas sin mostrar`), again at identical strip and canvas heights.

  In-memory variation with the reserve taken only when a remainder exists (emulated by
  `_MINIMAP_DECL_CELLS = 0` on the class, restored and asserted):

  ```
  ### legacy 35x14   conditional reserve   minimap_h=3 canvas_h=3
     |  cobertura   Finanzas     █   RRHH|
     |█   Inventarios  ░   █ completa ▒|
     |media ░ baja ╱ sin datos|
  ```

  **All three names and the whole legend, in the same three rows.** The arithmetic:
  caption 14 + 3 x 17 + legend 37 = **102 cells ≤ 3 x 35 = 105**.

  Entry limit is `(3w - 77) // 17`:

  | width | 35 | 40 | 50 | 60 | 80 | 118 |
  |---|---|---|---|---|---|---|
  | branches drawn | **1** | **2** | 4 | 6 | 9 | 16 |

  `legacy`'s three branches are complete only at **w ≥ 43**.

- **Why it matters:**
  - It is a **regression against `HEAD` on a shipped map** with **zero** compensating benefit
    measured — not one row of canvas, not one row of strip. Round 1 blocked because the declaration
    was invisible; this is the mirror, and it costs the operator the coverage glyphs for `RRHH` and
    `Inventarios` on the very widget whose stated job (`app.py:1794-1799`) is *"telling the operator
    WHICH branch is at risk"*.
  - It contradicts the code's own comment three lines up: *"the entries take the ROW'S REMAINDER"*.
    A remainder computed after reserving something that is not needed is not the remainder.
  - **Nothing observes it, and the arm that looks closest is green by construction** — the
    conservation law reads `1 drawn + 2 declared == 3` and passes. That is the *"shipping an
    unobserved behaviour on a green suite"* failure `app.py`'s own docstring names as the one this
    batch is spending its budget to stop.
  - `35x14` is not a stray size: `test_a_small_map_at_a_small_terminal_keeps_its_canvas` drives
    exactly it, on exactly this map shape, and passes.

- **Suggested fix** (inside `_minimap_entry_limit`, no new file, no new constant):
  ```python
  def _minimap_entry_limit(self, width: int, branches: int) -> int:
      """How many branches fit once the affordances have been paid for.

      THE DECLARATION IS RESERVED ONLY WHEN THERE IS SOMETHING TO DECLARE.  An
      unconditional reserve manufactures the remainder it reserves for: `legacy`
      has three branches that fit in three rows at 35 columns, and reserving 26
      cells for a declaration nobody needed dropped two of them and then
      truthfully declared the loss it had just caused.
      """
      rows = self.MINIMAP_ROWS * max(1, width)
      fixed = self._MINIMAP_CAPTION_CELLS + self._MINIMAP_LEGEND_CELLS
      per_entry = self._MINIMAP_NAME_CELLS + self._MINIMAP_ENTRY_OVERHEAD
      if branches * per_entry <= rows - fixed:
          return branches
      return max(0, rows - fixed - self._MINIMAP_DECL_CELLS) // per_entry
  ```
  Caller passes `len(children)`.

  **And the arm that makes it stick — red on today's tree, and it kills `MUT-A`:**
  ```python
  @pytest.mark.asyncio
  async def test_a_map_whose_branches_FIT_declares_no_remainder(tmp_path):
      """A strip that drops what it had room for, then declares the drop, conserves
      perfectly and is still wrong.  `legacy` at 35 columns: three branches, 102 of
      105 cells, and the shipped budget drew one."""
      app = MapperApp(tmp_path)
      async with app.run_test(size=(35, 14)) as pilot:
          await pilot.pause()
          app.store.save("small", branchy_graph(branches=3, total=8))
          screen = await open_map(app, pilot, "small")
          await pilot.pause()
          strip = screen.query_one("#map-minimap")
          painted = " ".join(" ".join(rows_in(screen, strip.region)).split())
          assert len(re.findall(r"rama \d+", painted)) == 3, painted
          assert "ramas sin mostrar" not in painted, (
              "the strip declares a remainder it created by reserving for one; "
              "every branch fit in the rows it already had")
          assert "sin datos" in painted, painted
  ```

---

### H2 — `01-requirements.md` marks predicate 1 `✅ CLOSED`, unqualified, while `state.json` in the same commit says the requirement is OPEN [Severity: HIGH]

- **What:** the closure note added at `01-requirements.md:3162-3166` reads, in full:
  *"✅ **CLOSED BY `Inc-STRIPS` (2026-09-10).** The three unbounded strips are bounded and the count
  is readable in the composited frame at **both** declared sizes, driven at the **shipped** bound
  rather than a moved one."* There is **no fanout-vector qualifier anywhere in it**.

- **Where:** `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md:3162` against
  `.dev-flow/state.json` `open_blocks[0].status` = *"OPEN — fanout vector CLOSED by Inc-STRIPS;
  TITLE-LENGTH vector open, blocked on Inc-CRUMB"*, and against §8.7's *"the requirement stays
  OPEN"*.

- **Why it matters:**
  - **This is the marking SEC-F2 blocked**, verbatim in its recommendation: *"Re-scope the §7 carry:
    predicate 1 is closed **against the fanout vector**. Say it in those words rather than
    'resolved'."* `state.json` says it in those words. The requirements file — the artifact that
    *records requirement closure*, and the one a later reader consults first — does not.
  - Predicate 1 is a **three-clause conjunction** measured at a size, and the title-length vector
    puts the count region off-viewport at 80x24 from one 4000-character title (security F2,
    measured). A reader of `01-requirements.md` alone concludes it is satisfied.
  - "The three unbounded strips are bounded" is also false as written — SEC-F2 counted **five**
    content strips outside `#map-body`, of which this increment bounds two.
  - It is exhibit 6 of this batch's own declaration family: the same fact spelled in two artifacts,
    drifted, in a commit whose `state.json` mints a rule about exactly that.

- **Suggested fix** — amend the note in place, keeping the batch's superseded-text convention:
  > ✅ **CLOSED BY `Inc-STRIPS` (2026-09-10) AGAINST THE FANOUT VECTOR ONLY — the predicate remains
  > OPEN.** `#map-minimap` and `#map-pagination` are bounded and the count is readable **in its own
  > region** at both declared sizes on a 12002-node / 4001-fanout graph, driven at the shipped
  > bound. **The title-length vector is open:** `TabStrip`'s crumb is a fourth unbounded strip
  > taking a raw ficha title, and one 4000-character title puts the count region off-viewport at
  > 80x24. Routed to `Inc-CRUMB`; `state.json.open_blocks` flips only when both vectors close.

---

### M1 — CR-F5 / SEC-F5 are recorded as fixed and are not: the meter block is byte-identical, and three comments still assert `#map-pagination` has no height rule [Severity: MEDIUM]

- **What / where:**
  1. **§8.3's table claims** *"CR-F5 comments contradicting the code | the meter's 'STILL UNBOUNDED'
     block corrected in place"*. `git diff HEAD` shows the hunk at `app.py:2086` is **pure
     addition** — the paragraph beginning *"THE METER IS STILL UNBOUNDED HERE, DELIBERATELY, AND
     BOUNDING IT IS NECESSARY BUT NOT SUFFICIENT"* (`app.py:2068-2087`) is unchanged from round 1,
     with *"THE METER IS BOUNDED HERE"* still appended beneath it. **The claimed fix was not made.**
     The retained block also still presents pre-fix measurements (`y=55`, `#map-minimap` is
     `height: auto`) as current.
  2. `app.py:94-97` still reads *"the count region **WRAPS rather than clips** (`#map-pagination`
     has **no height rule**, so it is `height: auto`) … it GROWS the strip"*. False since
     `app.py:3316`. **And now demonstrably harmful:** measured at 50x34 with a long query, the echo
     is silently *dropped*, which is the behaviour the comment tells a reader cannot happen.
  3. `app.py:1873` (*"a region that WRAPS"*) and `tests/test_search.py:2339-2340` carry the same
     false premise.
  4. **New in this diff:** the stylesheet comment at `app.py:3295-3305` says *"Capping the meter and
     the branch list is **NECESSARY AND NOT SUFFICIENT**"* — a claim §8.1 itself declares **refuted
     by measurement** — and *"the minimap holds **24 branch entries** and its legend at 118 columns"*,
     where `MINIMAP_BRANCHES` no longer exists and the measured limit at 118 is **16**.
- **Why it matters:** the increment sets this standard itself at `app.py:2070-2072`, and round 1
  blocked partly on a ledger claiming what was not done. A round-2 fold that records a comment fix
  it did not make is that same defect, one round later.
- **Suggested fix:** strike `app.py:2068-2087` in place under a `STRUCK` header rather than
  appending a contradiction; amend `:94-97`, `:1873`, `test_search.py:2339`; and correct the two
  false sentences in the new CSS comment (`16`, not `24`; and state the measured
  defence-in-depth claim §8.1 landed on instead of "NECESSARY AND NOT SUFFICIENT"). Then correct
  §8.3's table row.

---

### M2 — Predicate 1's "names the query" clause has no oracle at the shipped bound, and the arm's docstring argues for the omission on grounds the region-scoping removed [Severity: MEDIUM]

- **What:** predicate 1 requires the region to **name the query**, carry the count, and carry the
  notice. The `AT` arm asserts the last two (plus the numeric clause) and not the first.
- **Where:** `tests/test_strips.py:158-175`; the docstring's rationale at `:113-115` — *"A bare query
  echo would NOT discriminate: the fixture's titles are `rama N`, so searching `rama` puts the
  query's letters on the canvas"*. True of a **whole-frame** read; the arm is now **region-scoped**,
  where `SEARCH_ACTIVE_LABEL` discriminates cleanly. The reason was left behind by its own fix.
- **Measured** — `MUT-Q` (drop the label from the count region, ASCII-only anchor on
  `head = f"{SEARCH_ACTIVE_LABEL}: `), whole suite, all markers:
  ```
  ===== MUT-Q installed f5bce24a7f32d72a == intended  OK
      FAILED tests/test_search.py::test_above_the_bound_the_count_line_declares_the_search
      FAILED tests/test_search.py::test_the_query_echo_coerces_the_operators_text
      FAILED tests/test_search.py::test_the_suspended_declaration_is_actually_in_the_frame
      FAILED tests/test_search.py::test_a_line_bearing_query_does_not_take_the_frame
      4 failed, 927 passed, 3 xfailed
  ```
  **Zero kills from `test_strips.py`.** The clause is covered only by pre-existing `test_search.py`
  arms — which reach the branch by **lowering `MAX_RENDER_NODES`**, the moved bound this increment
  exists to stop relying on. That is CR-F1's exact argument, surviving on one of the predicate's
  three clauses.
- **Why it matters:** the requirement is being marked closed on this arm. Two clauses of three are
  closed at the shipped bound. The behaviour is correct today (measured: the label is on the region
  at 50, 60, 80 and 118 columns), so this is a coverage gap, not a live defect — hence MEDIUM.
- **Suggested fix:** one line in the existing arm, and delete the superseded sentence from the
  docstring:
  ```python
  assert SEARCH_ACTIVE_LABEL in painted, (
      f"at {size} the count region does not NAME THE QUERY -- the first of "
      "predicate 1's three clauses, and the only one still covered solely by "
      "arms that reach the branch by lowering the bound")
  ```

---

### M3 — §7's carry cites a constant this increment deleted, and understates the bound by an order of magnitude [Severity: MEDIUM]

- **What / where:** §7 still reads *"**Not closed here:** past **24 branches** the minimap shows a
  declared remainder rather than a scrollable list."* `MINIMAP_BRANCHES` was removed; the real
  threshold is width-dependent and much lower — 16 at 118 columns, **9 at 80**, 6 at 60, **1 at 35**.
- **Why it matters:** a carry is what a future increment reads to decide whether a "browse all
  branches" affordance is needed. At 80x24 — a **declared** size — a ten-branch map already shows a
  remainder. The carry as written says that regime does not exist.
- **Suggested fix:** restate as the measured table, and note that the threshold is now a function of
  width rather than a constant.

---

### M4 — `MUT-A`'s survival is reported as an equivalence rather than as the coverage gap it is [Severity: MEDIUM]

- **What / where:** §8.4 and the audit-4 analysis above. `MUT-A` is contract-equivalent and its
  survival is nonetheless the only reason H1 could ship: no arm can see over-reservation.
- **Suggested fix:** fold into H1 — the arm proposed there makes `MUT-A` red at 118x34 with a
  fitting map, converting the survivor into a kill and closing the gap the caveat names.

---

### L1 — `filled = min(page, steps)` is still a clamp under a comment claiming a compressed scale [Severity: LOW]

`app.py:2095-2096` unchanged from round 1 (CR-F6), and not carried anywhere in §7 or §8. Pick one:
write `filled = max(1, round(page * steps / per_page)) if per_page else 0`, or correct the comment
to say it is a clamp until pagination is wired. Simplicity favours the second.

### L2 — the render caps remain class attributes against the module's convention [Severity: LOW]

CR-F7 unchanged, and the surface grew: `MINIMAP_ROWS`, `METER_STEPS` and five `_MINIMAP_*` constants
are now `MapScreen` attributes where `_QUERY_ECHO_CELLS` and the four `_HINT_*` are module-level.
The two-spellings arm already has to reach through `MapScreen` to read one. Zero behaviour change;
do it in the H1 pass so the file count does not move.

### L3 — `tests/test_pan.py:211`'s docstring still writes `_minimap_text()` with no argument [Severity: LOW]

The call two lines below is `screen._minimap_text(118)`. Cosmetic, and in a file whose comment
directly above is about signatures.

### L4 — `_MINIMAP_DECL_CELLS = 26` assumes a four-digit remainder [Severity: LOW]

`f"+{undrawn} ramas sin mostrar   "` is `22 + digits(undrawn)` cells. 26 is exact at four digits and
one short at five. Slack absorbs it at 118 (5 cells) and 80 (10); at 60 the slack is 1. Unreachable
below ~10 000 undrawn branches. Worth one clause in the comment beside the constant, not a change.

---

## Evidence checklist

- [x] **Diff read in full** — `mapper/app.py` +121 at `:1734-1815`, `:2054-2100`, `:2345-2360`,
      `:3292-3316`; `tests/test_strips.py:1-375` (all 10 arms); `tests/test_pan.py:233-245`;
      `01-requirements.md:3150-3200` + its diff; `state.json` diff in full; packet §7-§8.7.
- [x] **Correctness pass (edge / None / error paths)** — `undrawn > 0` guarded; `limit` may exceed
      `len(children)` and the slice is safe; `max(1, width)` guards a zero width; `strip.size.width
      or self.size.width` guards the pre-layout frame; `steps >= 1` so `step_meter` never sees
      `total <= 0`. **H1 is the edge case: `branches <= limit_without_decl` is unhandled.**
- [x] **Simplicity pass** — the redundant `MINIMAP_BRANCHES` ceiling is genuinely gone and the
      removal is justified by measurement, not asserted. No premature abstraction added.
- [x] **Reuse / duplication checked** — CR-F4 discharged: `_minimap_entry_limit` adopts the
      `_HINT_*` row-remainder pattern and cites it in place. `rows_in` + whitespace-collapse reuses
      `test_search.py`'s established idiom rather than re-implementing it.
- [x] **Tests reviewed for intent** — 9 mutants installed and digest-verified, all 10 arms resolved
      each run; 8 KILLED, 1 SURVIVED (`MUT-A`, analysed at audit 4 and M4); `MUT-Q` fired against
      the full 931-arm suite. Zero BAD/CRASH mutants; every anchor occurrence-counted and every
      replacement `ast.parse`-checked.
- [x] **Ledger re-executed independently** — `912 / 19 / 3`, `931 / 3`, ruff 27 = 27 with a per-(file,
      rule) set diff against `HEAD`, source files = 1, reverse census re-swept.
- [x] **Tree restored and asserted** — three pins byte-identical at entry and exit, hash stability
      asserted across every mutant run, `__pycache__` purged, `git status --porcelain` unchanged.
- [x] **Verdict explicit** — below.

---

## Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **Block — must fix HIGH findings before advancing**

**HIGH findings: 2 (H1, H2).**

- **H1 blocks the code.** The declaration reserve is unconditional, and on the shipped `legacy` map
  at 35x14 it drops two of three branches — same strip height, same canvas height, nothing bought.
  The fix is one conditional inside `_minimap_entry_limit`, and the arm that pins it also converts
  `MUT-A` from the pass's only survivor into a kill.
- **H2 blocks the closure marking.** `01-requirements.md` says `✅ CLOSED`; `state.json` in the same
  commit says OPEN. The fold's re-scope is right and did not reach the artifact of record. Amend the
  note to name the fanout vector, exactly as SEC-F2 asked and exactly as `state.json` already does.

**What is right, and should not be re-litigated.** All three round-1 HIGHs are genuinely
discharged and I could not find a way past any of them: the acceptance predicate is sound in both
directions at the widths that broke it, with `MUT-C` killed by the two arms that own the claim and
the numeric clause landed; the declaration and legend survive the clip at 24 and 40 branches, at
60-cell titles, at three widths; the cell bound, the row ceiling, the `fit` call and both reserves
each have a mutant that reddens them. Removing `MINIMAP_BRANCHES` rather than writing an arm it
could only pass vacuously is the right call and is measured, not argued. The conservation law is a
real answer to reader-as-oracle. `state.json` is the best-scoped artifact in this increment.
§8.0's process disclosure and the serial-review rule it mints are exemplary, and the credit to the
security reviewer is correctly placed — I asserted hash-stability across every run of this pass
because of it, and the assertion held nine times.

**Is §8.7's re-scope honest?** **Yes in the fold and in `state.json` — the fanout vector is closed
by measurement I reproduced and the title-length vector is correctly named open and routed to
`Inc-CRUMB` — but the re-scope did not reach `01-requirements.md`, which still marks predicate 1
`✅ CLOSED` without qualification, and that unqualified marking is H2.**

**Handoffs:** `darkside.fit`'s 12-cell truncation and the new padded-column appearance of every
minimap are `ux-reviewer`'s call (audit 5), not blocking. The `TabStrip` crumb and `#map-toast`
remain `security-reviewer`'s and are correctly routed to `Inc-CRUMB` — not re-audited here, per
brief.
