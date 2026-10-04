# Code Review — Inc-7 (`2026-08-26-ui-next-batch-02`)

**Reviewer:** independent `code-reviewer`. I authored none of this diff. FULL protocol per `D35`.
**Verdict:** **`BLOCK-UNTIL: F1, F2, F3`.** This authorises nothing. `BLOCK-UNTIL` is not
`OK-with-fixes`: the increment does not advance on it, and it is discharged only by my re-reading
the diff after the fixes land.

## Scope reviewed

`git diff 6acaf64 7c99df6`; substance `91fdbbd` (`mapper/darkside.py` +58, `mapper/app.py` +46/-4,
`tests/test_repair_cycles.py` +137), docs `1a718e6` / `7c99df6`. Read in full:
`mapper/darkside.py:543-603`, `mapper/app.py:584-760` (both branches plus the hero `:489-504` and
resume `:512-531` sites the LLR names), `tests/test_repair_cycles.py:453-589`.
Requirements read: `01-requirements.md:3839-3948` (`LLR-N13.1.5` + `PRED-VIS` whole),
`:5153-5240` (`LLR-N16.2.1` census instrument), `:9522-9600` (`A-101`, `A-102`);
`01b-ux-decisions.md:263-320` (DECISION 3 §3.1–§3.4, every row) and `:697-790` (Amendment 1).

**Mirror used:** `…\scratchpad\mirror-inc7-cr` at `7c99df6` (mirror commit `e89036b`).
Provenance asserted inside every probe: `mapper.__file__` =
`…\scratchpad\mirror-inc7-cr\mapper\__init__.py` — printed GREEN on every run, including inside the
mutation battery. **Every digest held** (below). The mirror is byte-clean at exit (`git status`
empty; probe files removed).

## What I reproduced

| Measurement | Author's claim | Mine |
|---|---|---|
| Default lane | `1158 passed, 20 deselected, 3 xfailed` | **identical**, 352.45 s |
| `ruff --isolated` over `git ls-files '*.py'` | 27 | **27**; none of the 27 lands on a line this diff adds |
| SITE A — glyph dropped, string kept | membership + load-warning arms RED, distinguishability arm **GREEN** | **reproduced exactly** (table below) |
| `INK on PANEL` legality | 17.18 : 1 vs `#D28`'s 4.5 floor | not re-derived; style matches `V22` and `PRED-VIS RESOLVED` by inspection |

SITE A, byte-level, one substitution asserted, verdicts printed before restore:

```
app.py sha256 PIN : c7e654a97cbb7baef483684001e440f7ffec73974735f969fddae5c05c8b60e8
CRLF present      : True            substitution sites : 1
mutated  sha256   : cdb9bf14d78bf98aa8136b9f8c380ea15930734ddaa71a5fd5752748769ae662
restored sha256   : c7e654a97cbb7baef483684001e440f7ffec73974735f969fddae5c05c8b60e8   RESTORE HELD: True

  distinguishable_from_a_healthy_EMPTY_one : GREEN -> GREEN
  the_damaged_card_carries_a_DECLARED_glyph: GREEN -> RED
  a_LOAD_WARNING_also_reaches_the_card     : GREEN -> RED
  provenance (mapper.__file__ in mirror)   : GREEN -> GREEN
```

**The arms split the way you said they do, and I confirmed it rather than taking your word.** A
text-only difference keeps the distinguishability arm green — which is `PRED-VIS`'s own argument —
and only the two glyph-bearing arms see the loss. That is the correct shape.

**`sano_vacio` is load-bearing** — confirmed by inspection of the lines this diff *deletes*
(`kind, nodos, docs = "concept", "0", "0"`, byte-equal to a healthy empty map's cells) plus the
execution already recorded at `d877784` in `01-requirements.md:3925-3935`. I did **not** re-run the
pre-fix-restore site myself (see *What I did NOT run*).

---

## Findings

### F1 — The card does not carry the declared card state, and no arm asks for it  [Severity: HIGH]

- **What:** `LLR-N13.1.5` writes, as a titled clause, *"**Declared card state (Spanish, the string
  that ships):** `mapa dañado — ↵ ver por qué`"*, and its **Numeric pass threshold** has three
  limbs, the second being *"the broken map's card **contains the declared damaged-state string**"*.
  The card ships ` ⊘ dañado `. Measured in the mirror:

  ```
  roto card       : ['roto', ' ⊘ dañado ', '—', '—', ...]
  card CONTAINS the declared card state : False
  card contains U+21B5 (the ↵ affordance): False
  ```

  Two of the three threshold limbs are implemented and asserted; **the third is neither, and its
  absence is not declared anywhere in the diff or the commit message.** All three new arms pass a
  tree on which this limb is false, so the limb is not merely unmet — it is unmeasured.
- **Where:** `mapper/app.py:739-742`; threshold at `01-requirements.md:3855-3859`.
- **Why it matters:** three things ride on that copy, not on the glyph.
  1. `#D28`'s ruling that the style is `INK` and not `MUT on PANEL` is justified *by the copy*:
     *"the damaged card's copy **invites an action** (`mapa dañado — ↵ ver por qué`), so it is
     readable, load-bearing text, not a passive status"* (`:3884-3887`). ` ⊘ dañado ` invites
     nothing. The shipped card takes the escalated style while removing the reason for it.
  2. `PRED-VIS` is the *visual* limb added **on top of** the string limb — *"the difference is
     carried by a declared token or glyph, **not by the string alone**"*. The increment has
     inverted it into *glyph alone*. The operator who does open the card is told `dañado` and not
     what to do next.
  3. `LLR-N13.1.5`'s **Glyph note** hands `Inc-7` a `shall`: *"`Inc-7` **shall declare which action
     fires on a damaged card**. The Spanish copy itself is judged good and is unchanged"*
     (`:3918-3921`). The diff neither paints `↵` nor declares the action. A `shall` assigned by
     name to this increment is undischarged and unnamed.
- **Suggested fix** (author's choice of the two, but not neither):

  ```python
  kind_cell = Text.assemble(
      (f" {darkside.DAMAGED_MAP_GLYPH} {darkside.DAMAGED_MAP_CARD_STATE} ",
       f"{darkside.INK} on {darkside.PANEL}"),
  )
  ```
  with `DAMAGED_MAP_CARD_STATE = "mapa dañado — ↵ ver por qué"` declared beside the glyph, plus an
  assertion in the membership arm:
  ```python
  assert darkside.DAMAGED_MAP_CARD_STATE in painted, (...)
  ```
  **Or** route a copy amendment that supersedes the declared string, with the `#D28` style
  consequence restated. Shipping a third string (` ⊘ dañado `) that is in neither `01b` nor the LLR
  is the one option that is not open. Note the knock-on: the full copy is what limb 2 of
  `UX2-C-09` was written about, so F10 becomes live the moment this lands.
- **State:** `failed` — measured RED against the requirement in the mirror.

### F2 — A damaged map still paints a hero byte-identical to a healthy empty map's  [Severity: HIGH]

- **What:** you asked whether a damaged map can reach the hero untouched. It can, and it paints the
  same lie the card used to. Measured, two workspaces each holding one map named `m`, one a
  directed cycle and one `graph TD\n`:

  ```
  --- HERO, broken map ---        --- HERO, healthy EMPTY map ---
  ███                             ███
  █ █                             █ █        (the drawn numeral 0)
  ███                             ███
  nodos sin acta                  nodos sin acta
  m                               m
  actividad 14d  ▁…█              actividad 14d  ▁…█

  HERO IDENTICAL: True        GLYPH in broken hero: False
  ```

  `app.py:498-504` substitutes `{"total": 0, "con_acta": 0, "sin_acta": 0, "vencen": 0,
  "coverage": 0}` when the hero's load returns `None`, then `hero_box.display = True` because
  `hero_metrics` is a truthy dict. `_hero_text` reads `sin_acta == 0 and vencen == 0` and paints the
  count in `INK` — **the calm board.** The resume row is the same shape: measured
  `' ↩ retomar  m / a   última sesión'` for the broken map against
  `' ↩ retomar  m / A   última sesión'` for the healthy one — they differ only because `node_id`
  falls back for the title, an artefact of my fixture's casing, not a signal. No glyph, no
  declaration, `resume_shown: True` in both.
- **Where:** `mapper/app.py:496-504` (hero), `:522-525` (resume). Both are named in
  `LLR-N13.1.5`'s **Touched symbols** — *"the hero branch (`:481-492`); the resume branch
  (`:512-531`)"* — and the LLR's own executed note says *"both failure modes are live … **and the
  requirement above names both**"* (`:3935-3937`).
- **Why it matters:** this is not a different defect wearing the same words. It is the *same*
  substitution-of-zeros, in the most prominent element on the screen, surviving in a mount where
  the card beside it now says `⊘`. A `0 nodos sin acta / m` hero is an **affirmative false claim**
  about a file the system could not read, and the batch's own framing — *the sala is scanned, not
  read* — makes the hero the element most likely to be the only thing scanned. The LLR's statement
  clause is about *cards*, so the card limb is genuinely satisfied; but the LLR as scoped by its
  own Touched symbols is not, and your framing is the right one: **half-satisfied**. Also note the
  doc's claim that the hero *"silently vanishes"* is itself stale — at this tree it does not vanish,
  it lies; `hero_map` falls through to `mmd_files[0].stem` and displays.
- **Suggested fix:** carry `damaged` into both branches rather than widening the substitution.

  ```python
  if hero_map is None and mmd_files:
      hero_map = mmd_files[0].stem
      graph = load_or_notice(hero_map)
      if hero_map in damaged:
          hero_box.display = False        # or a declared damaged hero; do not paint zeros
          microbar.display = False
          hero_map = None
      else:
          hero_metrics = self._map_metrics(graph)
  ```
  and in the resume row, when `map_id in damaged`, paint the `V22` glyph in place of the healthy
  chrome. Then an arm per branch, each with a healthy-**empty** control exactly as the card arm has.
  If the coordinator rules the hero and resume out of `LLR-N13.1.5`'s scope, that ruling is the
  discharge — but it has to be *taken*, not assumed; today the omission is silent.
- **State:** `failed` — `HERO IDENTICAL: True` measured in the mirror.

### F3 — `DECLARED_VOCABULARY` drifted from `01b` in at least six rows, and its docstring claims a guard that does not exist  [Severity: HIGH]

- **What:** you predicted errors in the hand transcription. There are more than errors — there are
  inventions. I derived the set from `01b:274-319` myself and diffed it against the declaration.

  | Row | `01b`'s *Glyph, exactly* cell | Declared | Verdict |
  |---|---|---|---|
  | `V1` | `` ` rrhh ` `` (node title, leading/trailing space, on a card) | `▐` | **fabricated** — `01b` names no `▐` here; `▐` is `V11`'s glyph |
  | `V2` | `` ` nómina ` `` (node title on a card) | `▐` | **fabricated**, same |
  | `V6` | `┌─┐` | `┌┐` | **wrong** — the `─` is dropped |
  | `V7` | `plegadas: inventarios · ventas — 41 nodos` | `▽` + label `declaración de desbordamiento` | **fabricated** — `V7` has no glyph and no such label in `01b` |
  | `V8` | `minimapa · 128 nodos` | `▽` + label `minimapa · leyenda de nodos` | **fabricated** — that label appears nowhere in `01b` |
  | `V9` | `┌──┐ │ │ └──┘` | `┌┐` | **wrong** |
  | `V10` | `▓` `▒` `░` (three cells) | `▓` only | silent collapse of a three-glyph cell |
  | `V3`/`V4`/`V5` | `▸ <rama> +N`, `∙ ∙ ∙`, `▔▔▔▔`; label `rama plegada (23 dentro)` | `▸`, `∙`, `▔`; label `rama plegada` | normalised without a stated normalisation rule |
  | `V11`,`V13`,`V14`,`V15`,`V16`,`V17`,`V20`,`V22` | — | — | **faithful** |

  Two further mechanical divergences from `LLR-N16.2.1`'s **instrument** (`:5169-5180`), which is
  the authority `Inc-8` will assert against:
  - **`V18` is included, and the instrument removes it.** *"Remove every triple whose row carries
    the `DEFERRED(#D7)` marker"*, and `:5200-5204` names `V18` as exactly that row: *"`◍`
    repo-provenance … `#D7` rules **out of this batch** … the derivation removes it. A legend
    painting `◍ del repo` in this batch would explain a glyph the batch does not paint."* The
    declaration carries `("◍", "procedencia repo", TEAL on PANEL)`. (`grep DEFERRED` over `01b`
    returns only line 708 — so the two artifacts genuinely disagree about whether `V18` bears the
    marker. That is a conflict to **surface**, not to resolve by quietly including the row.)
  - **`V4b` is missing from both the declaration and the pending list.** `§3.1` carries `V4a` and
    `V4b` beneath its main table (`01b:287-288`), and `LLR-N16.2.1:5192-5197` states explicitly that
    they are in the instrument's scope and that `V4`≡`V4a` collapse to one triple while **`V4b` does
    not**. `V4b` is `braille run tracing a path between two cards` / `enlace entre nodos` /
    `MUT`; ACCENT for the selected path.
- **Where:** `mapper/darkside.py:565-589`. The docstring at `:557-560` is the aggravating part:
  *"`tests/test_home.py` **DERIVES** from that document and compares, so this table is a declaration
  **to be checked** rather than a second opinion."* `grep -rn "DECLARED_VOCABULARY\|01b-ux-decisions"
  tests/` returns **only** `tests/test_repair_cycles.py` — no deriving comparison exists anywhere in
  the suite. The table is, today, precisely an unchecked second opinion, and I have just measured
  that it drifted.
- **Why it matters:** `A-101`'s whole purpose is that *"`Inc-8`'s set-equality assertion has a
  **complete subject** on the day it runs"*, and it says in terms that `Inc-7` creates *"the full
  derived set … not merely the row it paints"*. What `Inc-8` will consume instead is a set that
  (a) invents `▽` twice for rows `01b` gives no glyph, so a legend built from it will paint two
  glyphs the product does not paint and the document never declared; (b) mis-spells two box-drawing
  forms; (c) attributes `V11`'s bar to `V1` and `V2`; (d) includes a `#D7`-excluded row; and
  (e) omits a member the instrument names. `Inc-8`'s set equality will go RED on the day it runs —
  loud, which is good — but it will go RED against a declaration whose errors have to be found one
  at a time, and the statement *"nothing here may be edited without the row in `01b` moving first"*
  will by then be protecting the wrong values.
- **Suggested fix:** do not re-transcribe by hand — that is the same shape a third time. Two
  options, either acceptable:
  1. **Derive it.** Parse `01b` DECISION 3 §3.1–§3.4's tables in a test and assert set equality
     against `DECLARED_VOCABULARY`, which is what the docstring already claims happens and what
     `LLR-N16.2.1`'s instrument describes. Then the declaration's errors surface as one RED arm with
     a full diff instead of as `Inc-8`'s mystery.
  2. **If the derivation is `Inc-8`'s to build**, then fix the seven rows above against `01b` cell by
     cell, delete `V18`, add `V4b` (or name it pending, see F4), and **strike the docstring sentence
     claiming `test_home.py` compares** — replacing it with a stated `Inc-8` obligation. A comment
     that asserts a control which does not exist is the false-confidence shape this batch hunts, and
     it is the reason this finding is HIGH rather than MEDIUM.

  Where `01b`'s glyph cell is genuinely prose and no projection is available — `V1`, `V2`, `V7`,
  `V8`, `V12` (`bare title, no card, no chrome`) — **say so in the declaration** rather than choose a
  codepoint. You asked me to name where the projection is ambiguous rather than guess: those five
  are ambiguous, and four of them were guessed.
- **State:** `failed` — derived against `01b` and diffed; `grep` over `tests/` for the claimed guard
  returns nothing.

### F4 — `COMPOUND_ROWS_PENDING_A_PROJECTION_RULE` is hand-built, unread, and unasserted — and the hand missed a row  [Severity: MEDIUM]

- **What:** you asked two questions. (a) *Was declining the projection rule right?* **Yes.** The
  ambiguity is real — `LLR-N16.2.1`'s instrument says *"project every row onto **the** triple"* and
  never says how a row naming three styles projects — it is a UX decision, and the coordinator has
  since had to rule it (`A-103`, post-`7c99df6`). Taking it silently in `darkside.py` would have been
  the worse failure. (b) *Is the declared absence honest, or a hole wearing a constant's clothes?*
  **It is a real hole, honestly named, by a method that cannot tell whether the naming is complete —
  and it is not complete.** `V4b` (`01b:288`) names two styles in one cell (`MUT`; the path to the
  selected node in `ACCENT`) — the *exact* criterion by which `V19` and `V21` were listed — and it
  appears in neither the declaration nor the pending tuple. The list was hand-derived and the hand
  missed one.
- **Where:** `mapper/darkside.py:603`. `grep -rn COMPOUND_ROWS_PENDING_A_PROJECTION_RULE mapper/ tests/`
  returns **the definition only**: no code reads it, no arm asserts anything about it.
- **Why it matters:** nothing can detect its drift. Nothing asserts that `DECLARED_VOCABULARY`
  excludes exactly the pending rows, that the pending rows are exactly the multi-style rows, or that
  the two lists partition `§3.1–§3.4`. So the constant documents an absence with the same
  reliability as a comment, while carrying a type annotation that reads like a checked artifact. The
  measured proof is `V4b`: a reader trusting the tuple concludes two rows are outstanding; three are.
- **Suggested fix:** make the absence derivable and asserted. In the same arm that derives the set
  from `01b` (F3 fix 1):
  ```python
  multi_style = {row_id for row_id, cell in parsed if _names_more_than_one_style(cell)}
  assert set(darkside.COMPOUND_ROWS_PENDING_A_PROJECTION_RULE) == multi_style
  assert not (declared_labels & {parsed[r].label for r in multi_style})
  ```
  Until then, at minimum add `V4b` to the tuple and say in the comment that the list is hand-derived
  and unchecked — which is the honest description of what it currently is.
- **State:** `failed` (the completeness claim), `not-run` (no arm exists to run).

### F5 — the `else` branch dereferences `graph` on an invariant that lives in a notification-dedupe guard  [Severity: MEDIUM]

- **What:** the guard changed from `if graph is not None:` to `if map_name in damaged:`, so the
  `else` branch reaches `graph.schema` / `graph.nodes` / `graph.documents` with no `None` check. It
  is safe **today**, and only because `damaged.add(name)` sits inside `if name not in broken:` — a
  guard whose purpose is to suppress a duplicate toast, not to maintain card state. The two happen to
  be written adjacently, so `broken` and `damaged` stay in step. Verified: `grep -n broken mapper/app.py`
  shows `broken` is appended at exactly one site (`:603`) and is now read at exactly one site
  (`:602`) — it has no remaining purpose beyond dedupe.
- **Where:** `mapper/app.py:601-605` and `:721-737`.
- **Why it matters:** the invariant "`graph is None` ⟹ `map_name in damaged`" is nowhere stated and
  nowhere asserted, and the one line that maintains it is nested under a condition about
  *notifications*. Anyone who later adds a second `broken.append`, moves the notify out of the guard,
  or returns `None` from a new early path turns a load failure into an `AttributeError` on the home
  screen — which is the precise failure (`HomeScreen.on_mount` raising) that `load_or_notice` exists
  to prevent, reinstated by the fix for it.
- **Suggested fix:** one word, and it documents itself.
  ```python
  if graph is None or map_name in damaged:
  ```
  and lift `damaged.add(name)` out of the `if name not in broken:` block (a set add is idempotent;
  only the `notify` needs the dedupe).
- **State:** `executed` — read and traced; no live crash path found.

### F6 — `DAMAGED_MAP_GLYPH` is defined by a walrus inside a tuple literal  [Severity: MEDIUM]

- **What:** `(DAMAGED_MAP_GLYPH := "⊘", "mapa dañado — …", f"{INK} on {PANEL}"),` at
  `mapper/darkside.py:587`. A module-level public name — imported by `app.py` and by two arms — is
  created as a side effect of building a data table.
- **Where:** `mapper/darkside.py:587`.
- **Why it matters:** it is clever where the file is otherwise plain. A reader (or a tool) looking
  for where `DAMAGED_MAP_GLYPH` is defined scans for a top-level assignment and does not find one;
  the name's existence is now coupled to the tuple literal's evaluation and to that row's position in
  it. `ruff --isolated` is silent on it, so nothing in the lane would catch a later edit that removes
  the row and the export together. Three plain lines beat this.
- **Suggested fix:**
  ```python
  DAMAGED_MAP_GLYPH = "⊘"   # `01b` §3.4 `V22`
  ...
      (DAMAGED_MAP_GLYPH, "mapa dañado — no se pudo leer", f"{INK} on {PANEL}"),
  ```
- **State:** `executed`.

### F7 — the membership arm's first assertion is strictly subsumed by its second  [Severity: MEDIUM]

- **What:** `test_..._carries_a_DECLARED_glyph` asserts `carried` non-empty, then asserts
  `DAMAGED_MAP_GLYPH in painted`. Measured: `V22 in declared-glyph set → True`. So
  `DAMAGED_MAP_GLYPH in painted` ⟹ `carried` non-empty. The first assertion cannot fail while the
  second passes; SITE A reddened both together, which is the same fact seen from the mutant side.
- **Where:** `tests/test_repair_cycles.py:532-540`.
- **Why it matters:** it reads as two independent checks — "some declared glyph" **and** "V22
  specifically" — and is one. The `declared` / `carried` set construction is doing no work, but it
  looks like the arm's membership machinery, which is exactly what a later reader would trust and not
  re-derive. Not vacuous in the dangerous sense (the arm does fail when it should), but it inflates
  the evidence.
- **Suggested fix:** keep the strong assertion; replace the weak one with the check the set
  construction actually enables — that the painted glyph is a member *because it is declared*, not
  because a constant was reused:
  ```python
  assert darkside.DAMAGED_MAP_GLYPH in declared, "V22 is not in the declaration it is drawn from"
  assert darkside.DAMAGED_MAP_GLYPH in painted, (...)
  ```
  The first line then fails if someone paints a constant that has fallen out of the vocabulary — a
  state the current pair cannot distinguish.
- **State:** `executed` — measured, plus SITE A.

### F8 — `_cells` stringifies a missing cell to the text `"None"`  [Severity: MEDIUM]

- **What:** `out.append(cell.plain if hasattr(cell, "plain") else str(cell))`. This is not
  hypothetical: measured today, every recents row carries **eight** cells, four of them `None`, and
  the helper reports `['roto', ' ⊘ dañado ', '—', '—', 'None', 'None', 'None', 'None']`.
- **Where:** `tests/test_repair_cycles.py:456-462`.
- **Why it matters:** an absent cell becomes the four-character string `None`, which compares equal
  across rows and satisfies `in` tests for the letters it contains. Today the padding is symmetric so
  the distinguishability arm is unharmed — I checked — but the helper is the shared instrument for
  all three arms and it silently converts "nothing was painted here" into content. An instrument that
  cannot report absence is the defect these arms hunt.
- **Suggested fix:**
  ```python
  cell = table.get_cell(key, col)
  assert cell is not None, f"row {key!r} has no cell in column {col!r}"
  out.append(cell.plain if hasattr(cell, "plain") else str(cell))
  ```
  This will go RED immediately against the phantom columns — see the observation below, which is
  where that belongs.
- **State:** `failed` (as an instrument property), `executed` (measured).

### F9 — `A-102` makes the same map declare two different truths on one screen  [Severity: MEDIUM]

- **What:** you asked whether a load warning on the *hero* map does the right thing. It does not.
  For a map that loads **with warnings**, `load_or_notice` returns the graph, so the hero branch
  computes `self._map_metrics(graph)` and paints real counts, while the recents loop now paints
  ` ⊘ dañado ` and `—` / `—` for the same map, in the same mount. Before `A-102` the screen was
  consistently wrong; it is now inconsistently right. (It does **not** over-fire in the direction
  you were worried about: `damaged` is keyed per name, the control map in your third arm stays
  healthy, and I reproduced that — SITE A reddens the load-warning arm and nothing else reddens it.)
- **Where:** `mapper/app.py:609-618` (the set), `:496-504` (hero reads the graph anyway).
- **Why it matters:** two secondary points, both worth a decision rather than a default.
  (a) Root cause is F2 — fix the hero and this resolves with it.
  (b) The card now discards information it holds: a raising map has no node count, a warning map
  **does**, and both paint `—`. `LLR-N13.1.5`'s first threshold limb is *"the loadable map's card
  carries its true node count"*; a warning map is loadable. Conflating the two damage kinds under one
  cell may well be right, but it is a choice and the diff does not record it.
- **Suggested fix:** resolve (a) with F2; record (b) either as a one-line comment beside `damaged` or
  by painting the true counts alongside the `⊘` for the warning path.
- **State:** `executed`.

### F10 — every new arm runs at 140 × 45; the requirement says this one shall not  [Severity: LOW]

- **What:** `PRED-VIS` limb 2 (`01-requirements.md:3908-3915`): *"**This arm shall run at 118 x 34**,
  or at both sizes"*, and `C-D27e` asks for *"a legibility arm measured against the background it
  actually paints on, at the declared context of use 118 × 34"*. All three new arms use
  `run_test(size=(140, 45))`; neither arm exists.
- **Where:** `tests/test_repair_cycles.py:470, 511, 566`.
- **Why it matters:** LOW **only because** the shipped copy is ten cells wide, so nothing can
  overflow. It is not low on the tree F1 asks for: the clause was written about the long copy, whose
  width at 118 columns is the open question, and the `17.18 : 1` figure in the commit message is a
  contrast computation, not the painted-row measurement limb 2 asks for (*"The test measures the
  painted row"*). **Fix F1 and this becomes the arm that verifies it.**
- **Suggested fix:** add `size=(118, 34)` to the distinguishability arm, or parametrise all three
  over both sizes.
- **State:** `failed` (clause unmet), `not-run` (no such arm to run).

---

## Out of scope — routed, not folded in

1. **The recents table grows four phantom columns on every return to home.** Measured in the mirror:
   `len(table.columns) == 8` for four declared columns, the last four `None`, on the app's *own*
   `HomeScreen` before any test pushed one. Cause: `DataTable.clear()` does not clear columns, and
   `on_mount` — which calls `add_columns(...)` — is re-entered on every resume from **two** call
   sites, `HomeScreen.on_screen_resume` (`app.py:889`) and `MapperApp.on_screen_resume`
   (`app.py:4378`). Unbounded: eight columns after the first return, twelve after the second. **This
   is pre-existing, not introduced here** (the `add_columns` line is untouched by the diff), but it
   lives in the exact surface this increment repairs and nobody has named it. The same two call sites
   make `MapStore.load` run twice per map per resume, which is `LLR-N13.1.6`'s clause. → `software-dev`
   / coordinator.
2. **`A-103` may be built on the same arithmetic gap as F3.** `A-103` (added after `7c99df6`, so
   outside this review's diff) derives *22 rows → 25 members* without visibly accounting for `V4a`,
   `V4b`, or the `#D7` removal of `V18` that `LLR-N16.2.1:5192-5204` requires. `Inc-8`'s set equality
   will be written against that number. → coordinator, before `Inc-8` opens.
3. `INK on PANEL` gives the damaged chip a **darker** background than the healthy chip's
   `INK on STEP`, so it may read as an absent chip rather than a marked one. Conformant to
   `PRED-VIS RESOLVED`, which fixes the style — flagged for the queued render round only. → `ux-reviewer`.
4. Carried and untouched here, as declared in the task: `FLAKE-1`, `.gitattributes`/autocrlf,
   `SEC-F4`, the socket guard, `B-64`, `UX-HINT1`, `TC-F3-C`, `N3`, `S-F3`/`S-F5`, `CR17-F3`/`F5`, the
   export budget, and the aesthetic choice of glyph and tone.

## What I did NOT run

- The other three sites of your 4-site battery: **pre-fix card restored**, **`A-102` reverted**, and
  the **comment-only control**. I reproduced SITE A only, chose because it is the one whose claimed
  outcome is *asymmetric* and therefore the one that could hide a vacuous arm. The other three are
  your measurement and I did not re-derive them; `sano_vacio`'s load-bearingness I confirmed by
  inspecting the deleted lines rather than by re-running the restore.
- The `-m slow` and `-m network` lanes.
- Any legibility/contrast computation — I took `17.18 : 1` as given and checked only that the style
  the code emits matches `V22` and `PRED-VIS RESOLVED`.
- Anything in the repo working tree: I ran nothing there and wrote nothing there except this file.
- Security review (concurrent `security-reviewer`, separate mirror) and functional/suite validation
  beyond the default lane (`qa-reviewer`).

## Evidence checklist

- [x] **Diff read in full** — `mapper/darkside.py:543-603`, `mapper/app.py:584-760`,
      `tests/test_repair_cycles.py:453-589`, plus the untouched `:489-531` the LLR names.
- [x] **Correctness pass (edge / `None` / error paths)** — F5 (`graph is None` now unguarded, traced
      to no live crash), F2 (hero/resume `None` paths measured), F9 (warning path on both branches).
- [x] **Simplicity pass** — F6 (walrus in a tuple literal), F5 (`broken` and `damaged` are two
      structures for one fact), F7 (one check written as two).
- [x] **Reuse / duplication checked** — the glyph is correctly drawn from the declaration rather than
      spelled at the call site (`app.py:740` reads `darkside.DAMAGED_MAP_GLYPH`); the failure is the
      opposite one, F3: the declaration duplicates `01b` with nothing comparing them.
- [x] **Tests reviewed for intent** — SITE A measured; the arm split confirmed independently; F7 and
      F8 found; `sano_vacio`'s necessity confirmed.
- [x] **Verdict explicit**, and **no HIGH carries applied-and-verified evidence** — F1, F2 and F3 are
      all `failed` and open.

## Verdict

- [ ] OK to advance
- [x] **`BLOCK-UNTIL: F1, F2, F3`** — names what is owed; **authorises nothing**. The increment does
      not proceed on this line. Discharge is by my re-reading the diff after the fixes land, never by
      trusting that a corrective pass ran.
- [ ] Block — HIGH findings open *(equivalent in effect; recorded as `BLOCK-UNTIL` because the three
      HIGHs each have a named, bounded fix)*

**F4–F10 are recommendations** and do not gate. F5, F7 and F8 are cheap and I would take them in the
same pass. **F3 should not be discharged by a second hand-transcription** — that method has now
produced measured errors once, and re-running it is the shape the finding is about.

**What is genuinely right here, stated because it is:** the containment holds (`painted card count
== len(mmd_files)`: two maps in, two rows out, other maps unaffected — measured); the glyph is drawn
from a declaration rather than spelled at the call site, which is the thing `PRED-VIS`'s membership
clause exists to force; the `damaged` set is the correct structure for `A-102` and it does not
over-fire on the card; the arms are not vacuous and they split on a string-only mutation exactly as
claimed; and the lane, the ruff count and SITE A all reproduced to the digit. The three HIGHs are
about scope and about a table nothing checks — not about the mechanism, which is sound.
