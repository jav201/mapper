# Code Review — Increment 016 · Inc-CONFIRM re-ruled · `A-100` · `B-68` · `HERMETIC-1`

| Field | Value |
|---|---|
| Reviewer | `code-reviewer` (independent; authored none of this diff; fresh session) |
| Batch | `2026-08-26-ui-next-batch-02` · FULL protocol per `D35` |
| Commit | `f3398f4` on `feat/ui-next-batch-02`, base `a552783` |
| Date | 2026-09-19 |
| **Verdict** | **OK to advance** — no HIGH. `CR-F1` CLOSED, verified by me on the shipped bytes. 4 MEDIUM + 2 LOW raised, none blocking |

---

## Mirror, and the digest discipline it was measured under

Per the coordinator's correction (control 15 — *parallel review requires one isolated,
digest-verified mirror per reviewer*), every measurement below was taken on **my own two mirrors**,
never shared with the security reviewer and never inside the repo:

| Mirror | Path | Purpose |
|---|---|---|
| `work` | `…/scratchpad/work` | the three lane runs, read-only |
| `mut` | `…/scratchpad/mut` | the 14-site mutation battery and the five probes |

Both were made by filesystem copy (no `git checkout`, so no `autocrlf` could touch a byte) and
**verified against the source by a per-file sha256 manifest over all 299 tracked files**, not by
spot-checking the five the brief named.

| Pin | Value |
|---|---|
| my tree-wide pin — sha256 of the sorted 299-line per-file sha256 manifest | `a499088dd61c5d4d5a18a2026d201896` |
| `mapper/app.py` · `mapper/export.py` · `mapper/views/state.py` | `914afcb8b0a364a6` · `56773345bc4731f1` · `bf239adef8e1c159` |
| `tests/test_pan.py` · `tests/conftest.py` · `tests/test_export_state.py` | `e65128c51866fa05` · `c1acf140b03d3301` · `e5799b0c9ac2ee83` |

**Every digest HELD, and I re-asserted all three trees at the end of the review**, not only at the
start:

- **repo** — `git status --porcelain` empty; all 299 tracked digests identical to the opening pin.
  The only file I wrote in `C:\Users\jjgh8\Github\mapper` is this report.
- **mirror `mut`** — all 299 restored byte-identical after 14 mutation sites.
- **mirror `work`** — all 299 held across three lane runs.

**I measured nothing in the shared tree before the correction arrived.** At that point I had done
read-only `git diff` / `git show` / `sha256sum` reads and had already created both private mirrors;
no edit, battery or probe ever ran in the repo. Stated plainly rather than left to inference.

⚠ **One thing the correction did not cover, and it bit me once.** The session *scratchpad root* is
**shared** between the agents in this session — it holds `mirror-cr/`, `mirror-sec/`, `sec016/`,
other agents' harnesses, and a stray **`inspect.py`** that shadows the stdlib module for any script
run from that directory. My first probe ran from the scratchpad root, imported
`C:\Users\jjgh8\Github\mapper\mapper\__init__.py` (there is an editable install pointing at the
repo) and died on the shadowed `inspect`. **That reading was discarded, not published**; every probe
below was re-run from inside `mut`, and I verified `mapper.__file__` resolves to the mirror there.
Per-reviewer *directories* are not per-reviewer *sys.path* — worth adding to the control.

---

## Scope reviewed

`git diff a552783 f3398f4` in full — 17 files, 3,312 insertions / 63 deletions.

**Under review (product):**
- `mapper/app.py` — `action_export_svg` 3466–3490 (the `ExportTooLarge` handler at 3476–3489),
  `EXPORT_EXTENT_STEPS` 3491–3507, `EXPORT_MAX_CELLS` 3509–3554, `_export_view_state` 3556–3673,
  `_within_export_budget` 3675–3680, imports 23 / 54
- `mapper/export.py` — whole file; `ExportTooLarge` 16–28, `save_svg` 30–61
- `mapper/views/state.py` — `ViewState` 59–101, `EXPORT_FIELD_KINDS` 104–145,
  `TRANSIENT_EXPORT_FIELDS` 147–149, `_declared_default` 152–156, `export_neutralised` 159–173
- `pyproject.toml` — 33–50

**Under review (tests):** `tests/test_export_state.py` 1–464 (new) · `tests/conftest.py` 1–197 ·
`tests/test_hermetic.py` 1–365 (new) · `tests/test_pan.py` 674–840 (new `B-68` block) ·
`tests/test_app.py` · `tests/test_search.py` 1479–1491 · `tests/test_a3_census.py` 219–330

**Records read, not re-litigated:** `.dev-flow/state.json` (`controls_for_engineering_rules`,
`coordinator_rulings`, `p3_progress.open_blocks`) · `increment-015-confirm.md` and both its review
files · `increment-016-confirm-reruled.md` (read as a set of claims) · `01-requirements.md`
amendment sets 7 and 8 (`A-99`, `A-100`).

---

## The seven prior findings — CLOSED or OPEN, measured

**Nothing here is cleared on the packet's word.** Each remedy was read on the shipped bytes and, where
it is a behavioural claim, fired as a mutation site on the shipped tree.

### `CR-F1` (HIGH) — **CLOSED**

The remedy is applied at `tests/test_pan.py:683–702`: `_export_bytes` unlinks before the press and
asserts `path.exists()` after, with the reasoning (Windows mtime granularity, byte-identical
re-writes) written into the helper.

**Measured on `f3398f4`, three sites, as a PAIR rather than a kill:**

| Site | Mutation | Expected | **Measured** |
|---|---|---|---|
| `S1` | MUTANT B — `raise` at every non-zero pan, ahead of the render in `action_export_svg` | KILL | **KILL** — RED at `test_b68_the_export_is_invariant_under_the_operators_pan` (1 red / 1 green of 2 resolved) |
| `S2` | the same mutant, with `_export_bytes` reverted to its pre-remedy form | SURVIVE | **SURVIVE** — 0 red / 2 green. `CR-F1` reproduced independently on this tree |
| `S3` | the remedy reverted alone, export healthy | SURVIVE | **SURVIVE** — 0 red / 2 green. The remedy is **inert** on correct work |
| `S14` | negative control, comment-only edit in `app.py` | SURVIVE | **SURVIVE** — 0 red / **15** green |

The kill is attributable to the remedy meeting the defect, not to the remedy false-failing correct
work, and the negative control proves the harness can report a survivor. `CR-F1` is closed on
evidence I produced, against bytes I pinned.

### `CR-F2` (MEDIUM) — **CLOSED**

`mapper/app.py:3669–3673` raises `ExportError` on exhaustion with its own reason, deliberately
**not** `ExportTooLarge` — and the distinction is right: an extent that did not converge can sit
*under* the budget, so `ExportTooLarge` would hand the operator a number contradicting its own
sentence and advice (`f`) that cannot help.

**Measured:** site `S4` (exhaustion returns `self._within_export_budget(state)` instead of raising)
→ **KILL**, RED at exactly
`test_an_extent_that_never_settles_REFUSES_instead_of_shipping_what_it_had`, 12 other arms green.
The branch was unreachable and is now pinned by a forced synthetic instance
(`EXPORT_EXTENT_STEPS = 0`), with the arm's docstring stating in its own words that this is a claim
about the loop's contract and not about a map an operator can build. That is the honest framing.

### `CR-F3` (MEDIUM) — **CLOSED** (as recommended: a boundary statement, no code change)

`mapper/app.py:3625–3632` carries the *HONEST BOUNDARY* paragraph — "full extent" is geometric, the
card is inside the artifact but the title is not printed whole, `layered._geometry` clamps `card_w`
identically to the canvas, and closing that is a separate ruling. That is what I asked for and it is
stated at the seam rather than only in a packet.

### `CR-F4` (MEDIUM) — **CLOSED, and pinned both ways**

`tests/conftest.py:67` is now `{"clone", "fetch", "pull", "push", "ls-remote"}`; lines 56–65 state
why `remote`/`submodule` were removed **and** declare the `remote update` / `submodule update`
omission rather than silently leaving it — the one place in this diff where an undeclared branch was
called out by its author instead of by a reviewer. The negative arms I asked for are at
`tests/test_hermetic.py:197–198`.

**Measured:**

| Site | Mutation | **Measured** |
|---|---|---|
| `S11` | the over-broad `remote`/`submodule` ban restored | **KILL** — RED at 3 params (`argv8`/`argv9`/`argv10`, all `-False`) |
| `S12` | the `-C` value no longer skipped | **KILL** — RED at `argv3-True` (`git -C <path> fetch` walks through) |
| `S13` | a string command waved through instead of refused | **KILL** — RED at `test_os_system_cannot_walk_past_the_guard` |

### `CR-F5` (LOW) — **CLOSED**

`tests/test_hermetic.py:131–140`: the docstring now says the walk is module-wide and
over-approximates, and explicitly names the previous wording as wrong. Correcting the record rather
than quietly replacing it is the right branch here.

### `CR-F6` (LOW) — **CLOSED, and better than recommended**

`VIEWER_LAUNCH_UNGUARDED` no longer exists anywhere in `tests/` or `mapper/` (grepped, 0 hits). It is
replaced by `VIEWER_LAUNCH_ATTRS`, **AST-derived** and compared both ways at
`tests/test_hermetic.py:57–86`. Documentation wearing a constant's clothes became a derived census —
the stronger of the two fixes I offered.

### `CR-F7` (LOW) — **CLOSED**

The `except Exception` comment inside the growth loop no longer claims the fallback is "the old
behaviour"; it now states the actual argument (the render raises on the same graph into the same
handler, so this returns the terminal-sized request rather than inventing a second failure mode).

---

## Findings

### N1 — the packet's mutation battery attests an `app.py` that is not the shipped one  [Severity: **MEDIUM**]

- **What:** `increment-016-confirm-reruled.md` §4 records the restore digest for `mapper/app.py` as
  `60c5dde90e610e20`, twice (the RED-counterfactual table and the mutation-verdicts table). The
  shipped file is **`914afcb8b0a364a6`**. The other four battery files match to the character —
  `export.py` `56773345bc4731f1`, `views/state.py` `bf239adef8e1c159`, `test_pan.py`
  `e65128c51866fa05`, `conftest.py` `c1acf140b03d3301`. So the battery ran, restored correctly, and
  then `app.py` was edited; eight of the eighteen sites (`M1`, `M2`, `M5`, `M6`, `M7`, `M8`, `M10`,
  `M11`) carry verdicts about a file that is not under review.
- **Where:** `increment-016-confirm-reruled.md` §4 · *RED counterfactual* and *Mutation verdicts*,
  against `mapper/app.py` as shipped at `f3398f4`.
- **Why it matters:** the *entire function* of a restore digest is to make the verdicts attributable
  to the bytes that ship. A digest naming different bytes converts a battery from evidence into a
  report — the exact substitution this increment's own reviewers are instructed to refuse. The
  packet's §*Corrections* framing ("every figure re-measured in this session") is what makes the
  mismatch surprising rather than routine: this is a resumed session that re-measured everything,
  and the digest is the one figure that records *when* it was measured.
- **Why it is MEDIUM and not HIGH:** I re-fired every affected site on the shipped bytes myself
  (`S1`–`S10`, `S14` above) and **all eleven reproduce their claimed verdict**, so the conclusions
  the stale digest supported are independently true. Had I not, they would be unsupported.
- **Suggested fix** — a record correction, not a code change. Either re-fire the `app.py` sites and
  record the new transcript, or amend §4 to:

  ```
  Restore proven by | SHA-256 returned to its pre-mutation value — `mapper/app.py`
  `60c5dde90e610e20`. ⚠ `app.py` WAS EDITED AFTER THIS BATTERY; the shipped file is
  `914afcb8b0a364a6`. The eight app.py sites were re-fired on the shipped bytes by
  `code-reviewer` (increment-016-confirm-code-review.md §Findings), which is what
  attests them — this battery does not.
  ```

  Do not seal the record with the digest as it stands.

### N2 — a refusal leaves the previous artifact standing at the path the success toast named  [Severity: MEDIUM]

- **What:** `action_export_svg` writes to a fixed `{map_id}.svg`. When the export refuses, nothing is
  written — correct — but any artifact from an **earlier successful press stays on disk, unchanged**,
  at exactly the path the earlier `exportado` toast printed. The refusal notice does not mention it.
  At base `a552783` the second press would have overwritten that file, so this is **new behaviour
  introduced by this increment**, not a pre-existing condition.
- **Where:** `mapper/app.py:3466–3489` (the path is fixed at `:3472`; the handler at `:3476–3489`
  toasts without touching the file). The blind spot is `tests/test_export_state.py:148–184`, which
  `path.unlink()`s at `:165` *before* asserting `not path.exists()` at `:180` — structurally unable
  to distinguish "nothing was written" from "the previous artifact is still there".
- **Why it matters:** measured, driven through the real `e` chord on one screen whose graph grows
  past the budget between presses:

  ```
  1st press (small map):  artifact exists=True  size=35122
  2nd press (over budget): notice='mapa demasiado grande para exportar: 974852 celdas, límite 350000. Enf…'
                           artifact STILL on disk=True  size=35122  unchanged_from_1st=True
  ```

  The ruling's harm shape is *a file that looks complete and is not*. A stale artifact is complete —
  for a map that no longer exists — and it sits under the name the operator was told to hand to
  someone. The refusal itself is loud and correct; what is silent is the file.
- **Suggested fix:** the cheap and non-destructive one is the message, since deleting the operator's
  prior file on a refusal is itself a decision nobody has ruled:

  ```python
              path = self.store.workspace / f"{self.map_id}.svg"
              stale = " El archivo anterior sigue en disco y NO se actualizó." if path.exists() else ""
              self.notify(
                  f"mapa demasiado grande para exportar: {too_large.cells} celdas, "
                  f"límite {too_large.limit}.{stale} Enfoca un subárbol con f y exporta esa vista.",
                  severity="warning", markup=False,
              )
  ```

  and an arm that does **not** unlink first, so the absence assertion can see the difference.
  Alternatively `A-100` states staleness is out of scope — but state it, rather than leave it to the
  next reviewer to measure.

### N3 — the SVG text-layer reader is spelled twice, and it is the instrument two acceptance families rest on  [Severity: MEDIUM]

- **What:** the `_SVG_CELL` regex is **byte-identical** in `tests/test_pan.py:714–717` and
  `tests/test_export_state.py:186–189`; `_squash` has an identical body in both
  (`test_pan.py:742–744`, `test_export_state.py:200–201`, differing only by a docstring); and the
  reassembly is the same algorithm under two names — `_svg_emitted_text` (`test_pan.py:720–739`,
  returns a joined string) and `_emitted_rows` (`test_export_state.py:192–197`, returns a list).
- **Where:** as cited. `tests/conftest.py` is the existing shared home and **this very increment
  added shared machinery to it** (the lane guard, `network_reaching`), so the seam is already open.
- **Why it matters:** this is not incidental duplication — it is the *oracle*. `B-68`'s
  "the export carries what the viewport could not" and `SEC-F1`'s "no rendered row is folded" both
  depend on parsing Rich's per-style-run `<text>` elements correctly. If Rich's emitted form changes
  (a `clip-path` naming change, an attribute reorder), one copy can be repaired and the other left
  to silently reassemble to something wrong — and both arms are written to fail loudly on an *empty*
  parse (`assert emitted, "the reader is broken"`), not on a *subtly wrong* one. The catalog's
  *ANYTHING SPELLED TWICE WILL DRIFT* applies with extra force to an instrument.
- **Suggested fix:** one home, two thin wrappers.

  ```python
  # tests/conftest.py  (or tests/_svg.py, imported by both)
  SVG_CELL = re.compile(
      r'<text[^>]*?x="([0-9.]+)"[^>]*?clip-path="url\(#[^)]*?-line-(\d+)\)"[^>]*?>(.*?)</text>',
      re.S,
  )

  def svg_emitted_rows(svg: str) -> list[str]:
      """The artifact's text layer, reassembled per `line-N` clip path, ordered by x."""
      rows: dict[int, list[tuple[float, str]]] = {}
      for x, line_no, content in SVG_CELL.findall(svg):
          rows.setdefault(int(line_no), []).append((float(x), unescape(content)))
      return ["".join(run for _, run in sorted(rows[n])) for n in sorted(rows)]

  def squash(text: str) -> str:
      return "".join(text.split())
  ```

  `test_pan.py`'s `_svg_emitted_text` then becomes
  `"\n".join(svg_emitted_rows(svg.decode("utf-8", errors="replace")))`.

### N4 — the recorded derivation of `EXPORT_MAX_CELLS` does not reproduce; the conclusion does  [Severity: MEDIUM]

- **What:** `mapper/app.py:3524–3532` records the bracket as
  **315,252 cells → 1.801 s** and **490,052 cells → 2.631 s**, "on wide-and-deep shapes driven
  through this very method", cross-checked by a through-origin fit at **5.4264 µs/cell**. `:3546–3550`
  pins those two cell counts to **161 nodes (80-wide × 80-deep)** and **201 nodes (100×100)**. I drove
  the identical shapes through `_export_view_state` + `renderer.render` + `save_svg` + the write, 3
  reps, max reported:

  | shape | cells | nodes | measured | rate |
  |---|---|---|---|---|
  | 80×80 wide+deep | 315,252 | 161 | **0.321 s** (packet: 1.801 s) | **1.017 µs/cell** |
  | 500-wide | 150,025 | 501 | 0.529 s | 3.529 µs/cell |
  | 0×700 chain | 336,480 | 701 | 0.714 s | 2.121 µs/cell |
  | 1100-wide | 330,025 | 1101 | 1.786 s | 5.411 µs/cell |

  The rate is **not** a function of cells — it tracks **node count at a given area**, spanning
  1.0 to 5.7 µs/cell. The 5.4264 µs/cell fit matches the *wide-only* family; the bracket is attributed
  to the *wide-and-deep* family, which I measure at a fifth of that. The two halves of the derivation
  come from different shape families and are presented as cross-checks of each other.
- **Where:** `mapper/app.py:3509–3554` (the `EXPORT_MAX_CELLS` docstring).
- **Why it matters — and why the constant survives anyway.** I hunted the top of the accepted band
  rather than re-deriving a line, because the only question that decides anything is *can a map the
  budget lets through cost more than 2 s*:

  ```
  1100-wide  330,025 cells  1101 nodes   1.753s  5.312 us/cell
  1130-wide  339,025 cells  1131 nodes   1.862s  5.492 us/cell
  1150-wide  345,025 cells  1151 nodes   1.955s  5.667 us/cell
  1160-wide  348,025 cells  1161 nodes   1.957s  5.622 us/cell
  1170-wide  REFUSED
  ACCEPTED SHAPES OVER TARGET: none found in this sweep
  ```

  **`EXPORT_MAX_CELLS = 350_000` is honest** — the worst accepted shape I could find lands at
  **1.957 s against a 2.000 s target**, and the next one up is refused. The conclusion is right, by a
  margin of **43 ms (2.2 %)**. But the *derivation a maintainer will re-run* does not reproduce, and
  this increment's own headline lesson is a superseded constant whose arithmetic was right and whose
  conclusion was false of the world. Leaving an unreproducible bracket in the docstring is that shape
  one turn later, in the safe direction this time.
- **Suggested fix:** no constant change. Re-state the derivation on the axis that actually drives it,
  and record the boundary empirically rather than by interpolation:

  > The rate is not uniform per cell — it tracks NODE COUNT at a given area: 161 nodes over 315,252
  > cells prices at 1.0 µs/cell, 1,101 nodes over 330,025 cells at 5.4. The binding family is
  > WIDE-AND-SHALLOW, and the boundary is measured there rather than interpolated: 1,160 leaves
  > (348,025 cells) costs 1.96 s and is accepted; 1,170 is refused. 350,000 leaves ~2 % of margin
  > against the 2 s target on this machine, which §5's "a slower machine crosses it at fewer cells"
  > is already the declared risk for.

  That margin is thin enough that §5's risk deserves the measured number beside it.

### N5 — `_declared_default`'s `default_factory` branch has no subject and is not declared  [Severity: LOW]

- **What:** `mapper/views/state.py:152–156` branches on `field.default_factory is not MISSING`.
  **No `ViewState` field uses `default_factory`** (derived over `fields(ViewState)`: none). The branch
  is unreachable today and untested by construction.
- **Where:** `mapper/views/state.py:152–156`.
- **Why it matters:** only for consistency with the standard this increment sets for itself.
  `tests/conftest.py:61–65` declines the exactly-analogous `git remote update` branch in those words —
  *"a branch for them would be a rule with no subject and no arm — untested by construction. Declared
  here rather than silently omitted."* The same shape twelve files over is neither declined nor
  declared. The related mismatch is benign and fails in the right direction:
  `tests/test_export_state.py:95` builds its expected defaults from `f.default` **only**, so a future
  factory-defaulted field would make the arm RED rather than green — closed, but it means the arm is
  not an oracle for this branch.
- **Not a correctness risk, checked:** the `MISSING`-leak worry (a transient field with *no* default
  would put `dataclasses.MISSING` into a live `ViewState`) is already foreclosed by
  `tests/test_a3_census.py:477` `test_llr_n07_2_3_view_state_constructs_with_no_arguments`, which
  enforces the dataclass docstring's "EVERY FIELD CARRIES A DEFAULT" invariant.
- **Suggested fix:** either `return field.default` alone, or one line: `#: `default_factory` has no
  subject in `ViewState` today; handled rather than asserted against, because the alternative is a
  branch on a field shape nothing uses.`

### N6 — the export resolves the operator's search and then throws it away  [Severity: LOW]

- **What:** `mapper/app.py:3633–3635` calls `self._view_state(...)`, which resolves the memoised
  search hits, and `export_neutralised` immediately resets `hits` to `frozenset()`. The export never
  uses the value it paid for.
- **Where:** `mapper/app.py:3633–3635`; the exemption it justifies is
  `tests/test_search.py:1482–1491`.
- **Why it matters:** only that the `_PASS_FREE_READERS` rationale — *"the resolution is keyed on
  graph+query, which growing the canvas cannot change"* — is now defending a read whose result is
  discarded. The reason as written is **true**, and I confirmed the loop never re-calls `_view_state`
  (it uses `replace(state, w=…, h=…)`), so the pass is correctly scoped. It is simply no longer the
  *simplest* true statement, and the simplest one is stronger.
- **Suggested fix:** no code change. Sharpen the note: *"…and the export discards the resolution
  entirely (`export_neutralised` zeroes `hits`), so no growth step can observe it at all."*

---

## Claims I was asked to verify — measured, not taken

| Claim | My measurement | Verdict |
|---|---|---|
| default lane `1133 passed, 20 deselected, 3 xfailed` | own mirror, `-q -p no:randomly`, exit **0**: `1133 passed, 20 deselected, 3 xfailed in 334.57s` | **TRUE** |
| slow lane `19 passed` | `19 passed, 1137 deselected in 52.73s` | **TRUE** |
| network lane `1 passed` | `1 passed, 1155 deselected in 1.13s` | **TRUE** |
| ruff 27 findings, **sets equal at equal scope**, both parses non-empty, added 0 / removed 0 | `--isolated --output-format=concise mapper tests` on both sides extracted symmetrically: base **27**, head **27**, both non-empty; `comm` both directions **empty** | **TRUE** |
| MUTANT B kills the remedied arm and survives the pre-remedy one — *the pair, not the kill* | `S1` KILL / `S2` SURVIVE / `S3` SURVIVE (remedy inert) — see `CR-F1` above | **TRUE, reproduced independently** |
| negative control survives | `S14` comment-only: **SURVIVE**, 15/15 green | **TRUE** |
| `M7` (exhaustion ships what it had) is now KILLED | `S4` → KILL, RED at exactly the exhaustion arm | **TRUE** |
| `M3` (console back to `width=200`) kills the fold arm, and is **green at 8 leaves** — threshold, not miss | `S5` → KILL, RED at `[20]`, `[40]`, `[120]`; **green at `[8]`** | **TRUE, incl. the threshold** |
| `M4` (the measured `+ 1` dropped) kills **including the smallest parametrisation** | `S6` → KILL, RED at `[8]`, `[20]`, `[40]`, `[120]` — all four | **TRUE** |
| `M5` (budget defanged) kills | `S7` → KILL, RED at the refusal arm **and** the notice arm | **TRUE** |
| `M6` (refusal kept, notice dropped) kills **exactly one** arm | `S8` → KILL, RED at `test_the_refusal_TELLS_the_operator_and_names_the_way_forward` **only**; the budget arm beside it GREEN | **TRUE — the two conjuncts are separately pinned** |
| `M1` (`hits` reclassified transient → content) kills | `S10` → KILL, RED at 3 arms incl. the end-to-end artifact arm, not only the completeness check | **TRUE** |
| `M2` (export stops neutralising) kills | `S9` → KILL, RED at the session arm **and** at `test_b68_…invariant_under_the_operators_pan` | **TRUE** |
| `N5`/`N6`/`N3` guard sites kill | `S11` KILL (3 params) · `S12` KILL · `S13` KILL | **TRUE** |
| the refusal path itself cannot freeze the pump | timed `_export_view_state` on the refused shapes: 201-node wide+deep **0.8 ms**, 1000-chain **4.4 ms**, 4001-wide **12.0 ms**. `pan_extent` is layout-only, not O(cells) — **the refusal does not pay the cost it refuses** | **TRUE (not claimed in the packet; checked because it would have voided the ruling)** |
| the extent settles in **one** growth step | counted by instrumenting the `pan_extent` symbol `_export_view_state` actually calls (not a replay), over 10 shapes from 3,360 to 1.2 M cells: **1 step, every shape** | **TRUE** |
| the measured boundary — 315,252 export / 490,052 refuse | reproduced exactly: 80×80 → ACCEPTED 973×324 = **315,252**; 100×100 → REFUSED **490,052** > 350,000; 1000-chain **480,480**; 4001-wide **1,200,325** | **TRUE** |
| `EXPORT_MAX_CELLS = 350_000` keeps an accepted export under the 2 s target | hunted the top of the accepted band: worst accepted **1.957 s** (1,160-wide, 348,025 cells); next shape up refused. **Margin 43 ms** | **TRUE — but see N4: the recorded DERIVATION does not reproduce** |
| the bracket `315,252 → 1.801 s` | same shape, 3 reps, two independent probe runs: **0.321 s / 0.313 s** | **DOES NOT REPRODUCE — N4** |
| A3 arg-ful pin `63 → 64`, hiding no removed product call site | derived `render_call_sites()` at `a552783` and at head, diffed per file: argful **62 → 64**, delta `tests/test_export_state.py` **+2**, `tests/test_app.py` **net 0** (the −1 Spy removal and +1 third comparand cancel, exactly as itemised). **PRODUCT files with a delta: NONE** | **TRUE — the round trip reconciles and no renderer-protocol site was removed** |
| A3 zero-arg pin `34 → 35` | derived both ends: **34 → 35**, delta `tests/test_app.py` **+1**. **PRODUCT files with a delta: NONE** | **TRUE** |
| the `B-68` arms respect the pan trap | both use `_open_pan_map` (`test_pan.py:304–308`, driven off `pan_graph()`, **not** `legacy`/`anidado`) at `CONTEXT_OF_USE = (118, 34)`, and both carry the `_pan_is_live` guard before asserting | **TRUE — the PAN-1 trap is not re-entered** |
| every return from `_export_view_state` is budget-checked | traced all four exits (non-panning view, `pan_extent` raise, converged, exhausted): three go through `_within_export_budget`, the fourth raises. **No partial-artifact path** | **TRUE** |
| `ExportTooLarge` ordering | `except ExportTooLarge` precedes `except Exception`; the exhaustion `ExportError` is the parent class and correctly falls through to `exportación fallida:` | **TRUE** |
| the field census is closed both ways | `tests/test_export_state.py:33–58` asserts `actual - declared` and `declared - actual` both empty, after asserting the derived set is non-empty — a broken walk cannot pass it | **TRUE** |
| the packet's restore digests | four of five match the shipped bytes exactly; **`mapper/app.py` does not** | **FALSE for `app.py` — N1** |

---

## What I did NOT run — stated, not implied

- **The security lens.** `SEC-F4` (the `eliminados` diff ghost strip riding into the export, §5/§6
  item 1), the `gh` credential surface, `osopen` launch policy, and the socket-level bypass residual
  are `security-reviewer`'s. Routed, not duplicated. I did not form a view on whether `SEC-F4` should
  block.
- **Functional / suite validation beyond the three lane tails.** I ran each lane once and read its
  own exit code and tail. I did **not** do repeated-order runs, coverage analysis, or acceptance
  walkthroughs — `qa-reviewer`'s lane.
- **`FLAKE-1`.** Did not fire in my three lane runs. That is the expected majority outcome at 2-in-9
  and carries no information. I did not attempt to capture the failing order. `blocked`, owed at the
  whole-branch gate.
- **The `.dev-flow` validator.** Not run; dispositioned external with 15 pre-existing blocks.
- **A mutation battery over `tests/test_hermetic.py` itself**, beyond the three `conftest.py` sites
  that its arms observe. The census helpers (`_derived_viewer_launch_attrs`, `_resolve_indirect_argv`)
  I read but did not mutate.
- **`tests/test_app.py`'s `b50` double repair and `…keyboard_was` port.** Verified at increment 015
  by me-in-role and unchanged in substance here; I re-read the diff but did not re-fire the
  `diff=None` mutant. `not-run`, inherited-verified, and named rather than counted as coverage.
- **Anything under Codex or another runtime.** The `/code-review` built-in is a Claude Code skill and
  is absent on disk; this file's §*What to review* list was the framing, per the agent definition.

---

## Verdict

- [x] **OK to advance** — no HIGH. `CR-F1` is **APPLIED AND VERIFIED BY ME ON THE SHIPPED BYTES**,
      as a pair (`S1` KILL / `S2` SURVIVE / `S3` inert) with a negative control (`S14` SURVIVE), not
      on the packet's report that the corrective pass ran. `CR-F2`–`CR-F7` are all applied and
      verified, four of them by mutation.
- [ ] `BLOCK-UNTIL: …`
- [ ] Block — HIGH findings open

**This verdict authorises nothing by itself.** It is one of two independent passes and the batch is
FULL protocol per `D35`; `security-reviewer` owes its own, and `SEC-F4` is open on that side.

**One item I would not let the coordinator seal as it stands: `N1`.** The packet's `mapper/app.py`
restore digest names bytes that are not the shipped ones. It does not block the *increment*, because
I re-fired all eleven affected sites on the shipped tree and every one reproduces — but it must not
go into the record uncorrected, because the next reader will take it as attesting a file it does not
attest. `N2`, `N3` and `N4` are recommendations; of those, **`N2` and `N4` are the two I would most
want taken before the whole-branch gate** — `N2` because a stale artifact under the name the toast
printed is the batch's own harm family arriving through the fix for it, and `N4` because 43 ms of
margin deserves to be recorded as the measurement it is rather than as an interpolation that does not
reproduce.

**Everything else in this diff is sound, and the parts that were hardest to get right are right.**
The refusal-not-a-crop principle is held at every exit from `_export_view_state`, including the one
branch nothing can reach. The two conjuncts of the refusal are pinned separately and I measured that
they fail separately. `EXPORT_FIELD_KINDS` turns a ruling-discharged-as-instances into a closed
census with both-ways drift protection, and the `hits` classification is pinned against being edited
away. The `CR-F4` narrowing came with the negative arms rather than just the narrower set. And the
refusal path — which nobody claimed anything about — costs 12 ms on the worst shape it refuses, so
the safeguard does not pay the cost it exists to avoid.

---

## Evidence checklist

| Item | ✓/✗ | Evidence |
|---|---|---|
| Diff read in full | ✓ | `git diff a552783 f3398f4`, all 17 files; product ranges itemised under **Scope reviewed** (`app.py:3466–3680`, `export.py:1–61`, `state.py:59–173`) |
| Correctness pass (edge / None / error paths) | ✓ | all four exits of `_export_view_state` traced to a budget check or a raise; `ExportTooLarge`/`ExportError` handler ordering at `:3476`; the `MISSING`-leak path in `_declared_default` chased and found foreclosed by `test_a3_census.py:477`; refusal-path cost measured (12 ms worst) — **N2**, **N5** |
| Simplicity pass (no premature abstraction) | ✓ | `_within_export_budget` is 4 lines and single-purpose; `export_neutralised` derives from the table rather than re-listing; `EXPORT_EXTENT_STEPS = 6` re-measured at **1 step over 10 shapes**, so the headroom is honest. One speculative branch found — **N5** |
| Reuse / duplication checked against existing utils | ✓ | `_SVG_CELL` byte-identical across two test files, `_squash` identical body, reassembly duplicated under two names — **N3**. On the product side the reuse is correct: `pan_extent` is the shared helper, `_consumes_pan` reuses `_reclamp_pan`'s seam, `conftest.py` is the guard's single home |
| Tests reviewed for intent, not just behavior | ✓ | 14 mutation sites fired on the shipped bytes: **13 KILL as expected, 3 expected survivors incl. the negative control, 0 mismatches**. Each new arm's discriminating power measured rather than read — incl. `M6` killing exactly one arm and `M3` being green at 8 leaves |
| Verdict explicit, every HIGH absent or applied-and-verified | ✓ | **OK to advance**; `CR-F1` closed on `S1`/`S2`/`S3`/`S14` fired by me against pinned bytes, not on the packet's report |
| Mirror isolated and digest-verified, per control 15 | ✓ | two private mirrors, 299-file manifests matched at open **and re-asserted at close**; repo `git status` empty; shared-scratchpad `sys.path` hazard found and the contaminated reading discarded |

---

## Evidence states

| Item | State |
|---|---|
| `CR-F1` (HIGH — vacuous invariance arm) | **`approved`** — fix APPLIED at `test_pan.py:683–702` and VERIFIED by me as a pair on the shipped bytes: `S1` KILL, `S2` SURVIVE, `S3` inert, `S14` control SURVIVE |
| `CR-F2` (exhaustion silently ships a crop) | **`approved`** — `app.py:3669–3673` raises; `S4` KILLS exactly the new exhaustion arm |
| `CR-F3` (geometric-only "full extent") | **`approved`** — boundary stated at `app.py:3625–3632`, which is the recommendation in full. No arm, by design — it is a boundary statement, not a behaviour |
| `CR-F4` (over-broad git subcommands) | **`approved`** — table narrowed at `conftest.py:67`, omission declared at `:61–65`, negative arms at `test_hermetic.py:197–198`; `S11`/`S12` KILL |
| `CR-F5` (docstring misdescribed its own scope) | **`approved`** — corrected at `test_hermetic.py:131–140`, naming the prior wording |
| `CR-F6` (constant nothing reads) | **`approved`** — constant removed (0 grep hits), replaced by an AST-derived both-ways census at `test_hermetic.py:57–86` |
| `CR-F7` (fallback comment stated wrong prior behaviour) | **`approved`** — rewritten; no longer claims "the old behaviour" |
| `N1` (stale `app.py` restore digest in the packet) | **`failed`** — packet `60c5dde90e610e20` vs shipped `914afcb8b0a364a6`; the other four match. Owed as a record correction before sealing |
| `N2` (stale artifact survives a refusal) | **`executed`** — measured through the real `e` chord; 35,122 B unchanged after the refusal. Fix `planned`, not applied |
| `N3` (SVG reader spelled twice) | **`executed`** — byte-identity of `_SVG_CELL` and `_squash` confirmed across both files. Fix `planned` |
| `N4` (unreproducible cost bracket) | **`executed`** — 80×80 measured at 0.321 s / 0.313 s against a recorded 1.801 s, two independent probe runs, 3 reps each; the CONCLUSION independently confirmed at the boundary (1.957 s at 1,160-wide, next shape refused) |
| `N5` (`default_factory` branch with no subject) | **`executed`** — derived over `fields(ViewState)`: no field uses a factory |
| `N6` (hits resolved then discarded) | **`executed`** — read against `app.py:3633–3635` and `test_search.py:1482–1491`; the exemption's stated reason is true as written |
| three lane tails (1133/20/3 · 19 · 1) | **`approved`** — one complete run each on my own mirror, exit code and tail read from that run |
| ruff set equality (27 = 27, added 0, removed 0) | **`approved`** — both sides extracted to symmetric scope, both parses asserted non-empty before any set arithmetic |
| mutation battery (14 sites) | **`approved`** — 13 KILL / 3 expected SURVIVE / 0 mismatches; substitution count asserted at exactly 1 per site, verdicts printed BEFORE every restore assert, all restores byte-identical, `PYTHONDONTWRITEBYTECODE=1`, CRLF/LF handled per file |
| A3 census pins (argful 64, zeroarg 35) | **`approved`** — derived at `a552783` and at head and diffed per file; PRODUCT delta NONE both sets |
| growth-step count (1 step) | **`approved`** — counted by instrumenting the product's own `pan_extent` symbol, never a replay |
| refusal-path cost | **`approved`** — 0.8 / 4.4 / 12.0 ms on the three refused shapes |
| mirror isolation + hash stability (control 15) | **`approved`** — 299-file manifests matched at open and close across repo and both mirrors; contaminated first probe discarded and declared |
| `b50` double repair · `…keyboard_was` port | **`not-run`** — verified at increment 015 by me-in-role, unchanged in substance; I re-read but did not re-fire the `diff=None` mutant. Named rather than counted |
| full-lane flake behaviour under varied order | **`not-run`** — one ordered run per lane. `FLAKE-1` needs the failing ORDER, which I did not hunt |
| `SEC-F4` (diff ghost strip in the export) | **`n/a — security-reviewer's lane`**; routed, not duplicated. OPEN on that side |
| `gh` credential surface · `osopen` launch policy · socket-level bypass | **`n/a — security-reviewer's lane`** |
| suite/functional validation beyond the lane tails | **`n/a — qa-reviewer's lane`** |
| `FLAKE-1` | **`blocked`** — pre-existing, owed at the whole-branch gate; a green lane containing it is a weaker green and this increment does not change that |
| `.gitattributes` / `autocrlf` · `artifact_homes.evidence` | **`blocked`** — carried by ruling; recorded, not widened. My mirrors were made by filesystem copy specifically so no renormalisation could touch a measured byte |
| `.dev-flow` validator (exit 1, 15 pre-existing blocks) | **`n/a — dispositioned external`** |
