# Increment 004a — US-N07 «búsqueda» · `search core: one owner, one count`

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Increment | `004a` |
| Lane (if the batch forked) | `Inc-4a` · `mapper/search.py`, `mapper/views/state.py`, `mapper/views/layered.py`, `mapper/app.py` |
| Requirement(s) | `HLR-N07.1` / `LLR-N07.1.1` / `LLR-N07.1.2` / **`LLR-N07.1.3`** · `HLR-N07.2` (`#D37`) / `LLR-N07.2.1` · `LLR-N07.3.1` · `LLR-N07.3.3` |
| Acceptance | `AT-018` `AT-019` `AT-020` `AT-021` `AT-052` · white-box **`TC-026b`** · unit `LLR-N07.3.1`, `LLR-N07.3.3`, the shared-resolution arm |
| Agent | `software-dev` (supervised-incremental-development) |
| Date | 2026-08-29 |
| Entry commit | `feat/ui-next-batch-02` @ `5f4816c` |
| **Committed?** | **NO.** Left in the tree for the gate. New test files are `git add`-ed (staged, not committed) because `test_a3_census.py` refuses to see an untracked source file. |

---

## 0 · BLUF, and the two things to read before the rest

**The increment is complete and every predicate is discharged, but two facts change how you read it.**

**⚠ BLOCK 1 — I COULD NOT REPRODUCE A GREEN BASELINE, AND THE RED IS YOURS, NOT MINE.**
The brief pins the baseline at `801 passed / 17 deselected / 3 xfailed, exit 0, zero FAILED lines`.
Executed here before a line was written:

```
1 failed, 800 passed, 17 deselected, 3 xfailed in 117.98s
FAILED tests/test_fold.py::test_no_tracked_file_spells_a_coerced_code_point_INCLUDING_the_artifacts
AssertionError: [('.dev-flow/2026-08-26-ui-next-batch-02/02l-inc4-qa-predicates.md', ['0x202e'])]
```

Same node count (801), one verdict different. The cause is **two literal right-to-left-override
characters (code point U+202E) in `02l-inc4-qa-predicates.md`, at lines 253 and 772** — the pinned
hostile-byte query row in its §6 and the `Text.assemble` transcript in its §8.2. That census
`rglob`s `.dev-flow/**` and deliberately reaches untracked files, so `02l` is inside its scope the
moment it exists. It is one of the three artifacts the brief told me to leave alone, so **I left it
alone.**

I proceeded rather than stopping, and the reasoning is on the record so you can overrule it: the
green-baseline rule exists so that a post-change red is attributable, and that purpose survives one
deterministic red whose cause is identified to the character, lies outside `mapper/`, and is
constant across every run in this session. **Your one-line fix:** replace those two characters with
their escaped spelling; the artifact says the same thing and the census goes green. I did not do it
for you.

**⚠ THE DECLARED C-26 REVERSE-CENSUS HIT DID NOT FIRE — and the one that did was undeclared.**
The pre-gate named `tests/test_darkside_census.py:212` as a legitimate expected drift. Executed: it
did **not** drift and that suite is 24/24 green, because the census pins the literal text of the
`cv.text(...)` call and my change rewrote the *expression that feeds it*, one line above. Instead a
**different** pin fired — `test_a3_census.py`'s arg-ful call-site cardinality, `52 → 57`. It is
itemised in §4. Naming a drift in advance is worth doing; it is not the same as having found them
all.

---

## 1 · What changed

**"What matches" now has exactly one owner, and the screen has exactly one resolution of it.**
`mapper/search.py` — dead at entry, zero importers — becomes that owner: it delegates the widened
match to `Graph.search_hits` (`model.py:224`, six haystacks), adds the tree-order walk
`LLR-N07.3.1` asks for, and refuses a query with no non-whitespace character. The renderer stopped
deciding: `ViewState.query` is gone, `ViewState.hits: frozenset[str]` replaces it, `_matches` and
every `qlower` binding are deleted, and **both** of that predicate's consumers migrated — the card
highlight and the fold pill's hit tail.

**The operator now gets a count, on the named strip.** `#map-pagination` (`#D37`) carries
`n/N coincidencias en el mapa`, with `N` taken over the whole graph and `n` the selection's place in
it; `0 coincidencias en el mapa` when a query came back empty, at the same offset; and **no line at
all** when the query is blank, which is also the state of a screen nobody has searched yet.

**Declared behaviour change, not a refactor.** The widening moves the fold pill's number for
existing maps. Measured on the new fixture with the hidden count held constant so the tail is
isolated: branch `b` **`+2 1` → `+2 2`**, the root **`+5 2` → `+5 4`**. Nothing in the suite could
see that before — `TC-026b` is why it is falsifiable now.

**One defect I introduced and the mutation battery caught before you did.** My first revision let
the count line resolve its own hits while `_view_state` resolved the renderer's separately. Both
called the owner, both were right, and a mutation scoping *one* of them to the visible set left the
other correct and `AT-018` **and** `AT-019` green — risk A-6 shipping under two passing acceptances.
That is US-N07's own defect reproduced inside the screen that closes it. Restructured to a single
`_search_order()` that both consume, and a structural arm now pins that they do.

---

## 2 · Files modified

| File | Kind | Change |
|---|---|---|
| `mapper/search.py` | **source** | the owner: `SearchIndex.hits` (whitespace-refusing set), `SearchIndex.query` (tree-ordered, orphan-safe), new `tree_order` |
| `mapper/views/state.py` | **source** | `query` **removed**, `hits: frozenset[str] = frozenset()` added; docstring closes the silence on removal (A-k4) |
| `mapper/views/layered.py` | **source** | `_matches` deleted, `Node` import dropped with it; card reads `state.hits`; pill tail is `len(_descendants(...) & hit_ids)` |
| `mapper/app.py` | **source** | `COUNT_REGION_ID` + `SEARCH_COUNT_SUBJECT` constants; `_search_order` / `_search_hits` / `_count_line`; `_view_state` writes `hits=`; three `map-pagination` literals routed through the constant |
| `tests/inc4_support.py` | test | **NEW** — the `QA-N-08` generator fixture, the narrow-predicate control, the oracle's own descendant + tree walks |
| `tests/test_search.py` | test | **NEW** — `AT-018` `AT-019` `AT-020` `AT-052` + the `LLR-N07.3.1` / `LLR-N07.3.3` / shared-resolution arms |
| `tests/test_layered.py` | test | `AT-021` (injected id + the AST deletion census, one node) |
| `tests/test_fold.py` | test | `TC-026b` (pilot tail from the frame + the injected-set rename arm) |
| `tests/test_app.py` | test | the one causal break migrated from `query` to `hits` |
| `tests/test_a3_census.py` | test | arg-ful call-site pin `52 → 57`, itemised |

| Count | Value |
|---|---|
| **SOURCE files** | **4 / 4** |
| Test files | 5 (uncapped) |
| Doc files | 0 |

**⚠ At exactly 4 source files — why it could not be cut smaller.** The subject is moving the decision
of *what matches* out of the renderer into one owner. The owner (`search.py`) must reach the
renderer (`layered.py`); the only channel the frozen `IRenderer.render(graph, state)` contract
provides is `ViewState` (`state.py`); and something must resolve the query and write it
(`app.py`). Landing the owner without the channel leaves **two definitions of "hit" live at once**,
which is precisely the defect `HLR-N07.1` exists to close.

**✓ No file from another lane touched.** `mapper/keymap.py` is byte-identical to `HEAD`
(`git diff HEAD --stat mapper/keymap.py` → 0 lines). The seat, the `n`/`N`/`M` rebind, the walk, the
`E1b`/`E1c` toasts, `esc`, and `LLR-N06.2.4`'s fold auto-open are untouched — all Inc-4b's.
`tests/test_inc3_census.py` + `tests/test_key_dispatch.py` → **54 passed**, unchanged.

---

## 3 · How to test

```bash
cd C:/Users/jjgh8/Github/mapper

# the increment's own nodes
PYTHONUTF8=1 python -m pytest tests/test_search.py -q
PYTHONUTF8=1 python -m pytest tests/test_layered.py::test_at_021_hits_come_from_the_state -q
PYTHONUTF8=1 python -m pytest tests/test_fold.py -q -k "026b"

# the regression surface this increment reaches
PYTHONUTF8=1 python -m pytest tests/test_a3_census.py tests/test_darkside_census.py \
                              tests/test_inc3_census.py tests/test_key_dispatch.py \
                              tests/test_app.py tests/test_overflow.py -q

# the gate
PYTHONUTF8=1 python -m pytest -q -m "not slow"
PYTHONUTF8=1 python -m ruff check mapper/ tests/          # scope is load-bearing
```

---

## 4 · Test results

**One complete run**, read from that run's own tail:

```
1 failed, 812 passed, 17 deselected, 3 xfailed in 132.81s (0:02:12)
FAILED tests/test_fold.py::test_no_tracked_file_spells_a_coerced_code_point_INCLUDING_the_artifacts
```

The single FAILED line is Block 1 — the operator's artifact, byte-for-byte the same failure as at
entry, before any of my work existed.

| Layer | Nodes | Result |
|---|---|---|
| **0 · unit** | `test_llr_n07_3_1_hits_come_back_in_tree_order`, `test_llr_n07_3_3_a_blank_query_is_not_a_match_everything`, `test_the_search_owner_loses_no_hit_the_root_cannot_reach`, `test_the_count_and_the_paint_share_one_resolution`, `test_the_hit_tone_is_read_from_darkside` | 5 passed |
| **A · white-box** `TC-026b` ↔ `LLR-N07.1.3` | `test_tc_026b_the_fold_pill_hit_tail_counts_the_resolved_hits` (pilot), `test_tc_026b_the_tail_reads_the_state_and_could_not_have_computed_it` (unit) | 2 passed |
| **B · black-box** `AT-NNN` ↔ story | `test_at_018_the_count_covers_the_whole_graph_in_four_states`, `test_at_019_the_count_is_invariant_under_fold`, `test_at_020_hit_widening_is_intentional`, `test_at_021_hits_come_from_the_state`, `test_at_052_the_count_line_names_its_subject` | 5 passed |

### The 9 → 0 deletion census, executed by AST

Instrument: an `ast` walk over `mapper/views/**/*.py`, counting `FunctionDef` named `_matches` and
every `Name` load/store plus every `arg` named `qlower`. **Never a grep** — a grep cannot separate a
call from a mention, and an absence-only assertion is satisfied by a rename, which is why
`AT-021`'s injected-id arm sits beside this one in the same node.

| | modules derived | `FunctionDef _matches` | `qlower` bindings/loads |
|---|---|---|---|
| entry `5f4816c` | 6 (`__init__`, `lane`, `layered`, `outline`, `radial`, `state`) | **1** (all in `layered.py`) | **9** (all in `layered.py`) |
| exit | 6 | **0** | **0** |

### The pill's tail, before and after — measured, with the hidden count held constant

| branch | descendants | narrow definition (entry) | resolved wide set (exit) | painted at 118x34 |
|---|---|---|---|---|
| `b` | `{d, e}` | 1 | **2** | `▐ ▸ Contratos en … +2 2` |
| `riesgo-root` | `{b, c, d, e, f}` | 2 | **4** | `▐ ▸ Carte… +5 4` |
| `c` | `{f}` | 0 | 0 | no tail — the counterfactual that the value is query-driven |

Identical at 100x30. `TC-026b` asserts the tail **moves** (`assert expected != was`), so a
re-narrowing of the definition reddens rather than passing quietly.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Where it ran | **this tree**, one file at a time, `try/finally` restoring from a byte copy taken before the mutation |
| Restore proven by | **sha256 returned to its pre-mutation value** for every mutation, printed per row; `git status` was not used and is vacuous for the untracked half |
| Verdict granularity | **per resolved node id.** Each arm ran in its own `pytest` process; the harness asserts exactly **1** node resolved per run and reports `UNRESOLVED` otherwise, so an inert arm cannot hide behind a failing sibling |
| Arms resolved | 1 per run, asserted; 22 arm-runs across 17 mutations |
| Arms that stayed GREEN | **none, against the arm each mutation is aimed at.** Two secondary targets stayed green and are named below |
| Bytecode cache | ⚠ **`PYTHONDONTWRITEBYTECODE` was NOT set.** Stated rather than glossed. The risk is disproven in the direction that matters: every mutation reddened, which a stale cache would have prevented; and the restored state is re-measured by the full run above in a fresh process |

Mutations are described **by position and operation**. No mutated token is spelled — this packet is
corpus input (C-56) and a mutation spelled in a transcript is a mutation that was not reverted.

| # | Mutation (position · operation) | File | Arm(s) aimed at | Verdict | Restore |
|---|---|---|---|---|---|
| M1 | the screen's resolving helper — filter its result by the descendants of the folded set | `app.py` | `AT-018` · `AT-019` · shared-resolution | **RED · RED · RED** | sha256 OK |
| M1b | the renderer's set — resolve it independently instead of deriving it from the shared helper | `app.py` | shared-resolution | **RED** | sha256 OK |
| M2 | the count line's non-empty branch — drop the subject declaration, leave the numeral | `app.py` | `AT-052` | **RED** | sha256 OK |
| M3 | the count line's blank-query early return — make its condition unreachable | `app.py` | `AT-052` | **RED** | sha256 OK |
| M4 | the owner's whitespace guard — make its condition unreachable | `search.py` | `LLR-N07.3.3` · (`AT-052`) | **RED** · GREEN | sha256 OK |
| M5 | the owner's ordering — walk the node mapping instead of the tree | `search.py` | `LLR-N07.3.1` | **RED** | sha256 OK |
| M6 | the owner's ordered result — drop the trailing unreachable-hit clause | `search.py` | orphan arm · (`LLR-N07.3.3`) | **RED** · GREEN | sha256 OK |
| M7 | the card's hit decision — stop consulting the state's set | `layered.py` | `AT-021` | **RED** | sha256 OK |
| M8 | **`M-N07.1.3-a`** — the pill's hit term falls to a constant zero | `layered.py` | `TC-026b` pilot · `TC-026b` unit | **RED · RED** | sha256 OK |
| M9 | the haystack — remove the attachment term | `model.py` | `AT-020` · `TC-026b` pilot | **RED · RED** | sha256 OK |
| M10 | the haystack — remove the subtitle term | `model.py` | `AT-020` | **RED** | sha256 OK |
| M11 | the haystack — remove the id term | `model.py` | `AT-020` | **RED** | sha256 OK |
| M12 | re-introduce the deleted predicate under its own name (the rename mutant) | `layered.py` | `AT-021` | **RED** | sha256 OK |
| M13 | the pill tail — re-source it from a title-only definition | `layered.py` | `TC-026b` pilot | **RED** | sha256 OK |

`model.py` is **not** in this increment's file set; M9–M11 are probes against it, applied and
restored, never edits. Its digest is unchanged from before the battery to after.

**Digests, entry of the battery → exit (identical):**

```
mapper/app.py            ce15d1a969033e9d988cb33855450f78ce0e775a94a06363d30b9fab3abf594a
mapper/search.py         9830d92dc6f5497d94a40d4d2dcc1a9895693dfc092ce89404818116d07f0bf8
mapper/views/layered.py  3e081a6c61af9a20ec5ec94140e4258226fc0b692c65dea707701ba07c4015b5
mapper/model.py          3d39a861a44f3abef5b73e2b1771f46ebc4b03804867c5d20f25af38c4468688
mapper/views/state.py    0b661033b2ceff9a4ffb31aea260a4cc7c2a638683bfd248398fb4758d50711e
```

#### The two GREEN arms, named rather than buried

Both are **secondary** targets I aimed opportunistically, not the arm the mutation certifies:

- **M4 → `AT-052` GREEN.** Removing the owner's whitespace guard does not redden `AT-052` because
  `_count_line` carries its *own* blank-query guard, which `M3` reddens. The two guards are
  independent by design (the owner refuses blank queries; the strip refuses to paint a line for
  one), and each has its own mutation. Not a hole.
- **M6 → `LLR-N07.3.3` GREEN.** The unreachable-hit clause is orthogonal to blank-query handling;
  the orphan arm is its gate and it reddened.

#### The mutation that could NOT be written, declared

The predicate design names a mutation for `AT-052` of the form *"weaken the subject noun"*. Executed
in pass 1, it stayed **GREEN**, and the reason is structural rather than fixable: `AT-052`'s
expectation is **derived from the shipped constant**, so mutating the constant moves both sides
together. Writing the wording into the test instead would be the second copy of the declaration that
the single-declaration rule exists to prevent. The mutation that *does* belong to `AT-052` is
dropping the declaration from the painted line — that is **M2**, and it reddens. **A constant's value
cannot be gated by a test that derives from it**; what is gated is that the line carries a
declaration at all, is distinguishable from the sibling page numeral, and appears exactly once.
Recorded as a limit, not repaired by pretending.

### Load-bearing emptiness (C-55)

| Field | Value |
|---|---|
| Does any claim rest on the tree holding NO instance of some case? | **Yes — two.** (a) `AT-021`'s injected id `f` rests on `f` being a hit under **neither** definition; (b) the deletion census rests on an absence |
| What made the search wide enough | (a) the test asserts the absence for **both** definitions at run time (`f not in graph.search_hits(QUERY)` **and** `f not in narrow_hits(...)`), so a fixture edit that made `f` match reddens the arm rather than weakening it silently; (b) the census derives its module set by `rglob` and asserts `len(modules) >= 5` **before** evaluating |
| Guard labelled as protecting a CONCLUSION | `test_llr_n07_3_1_hits_come_back_in_tree_order` — the `tree_order != dict_order` self-guard carries an inline note that it exists to make the assertion *able to fail*, so the next reader does not tidy it away |
| Conjunctive criteria: one mutation per conjunct | `AT-020` is a three-way conjunction (id · subtitle · attachment) and has **three** independent mutations, M9/M10/M11, one per conjunct, each RED |
| Synthetic instance of the absent case | `tests/inc4_support.py::build_adjuntos` — the shipped `legacy` fixture has **0 attachments** and 4 of 8 nodes with no subtitle, so two of the three widening arms are undrivable on any fixture that existed |
| **Positive control for every ABSENCE probe** | `AT-021` asserts the empty hit set paints **zero** hit-styled characters *and then* that a non-empty set paints a specific card — same unmodified probe, non-absent output. `AT-052` asserts no count line before the search and a matching one after. `TC-026b` asserts no tail with no query and a non-zero tail with one. The deletion census's positive control is its own entry measurement (1 and 9, non-zero) |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rn "_matches\|qlower" tests/` | **3 hits, all mine or unrelated**: `test_layered.py:196/207/209/212` (my AST census) and `test_key_dispatch.py:105` (a function *name* containing `matches`, not the symbol) |
| B1 | `grep -rn "state.query" mapper/ tests/` | **0** — the field has no surviving reader |
| B1 | `grep -rn "query_text" tests/` | 2, both mine; the historical single reader was `test_app.py`'s export arm, **migrated** |
| B1 | `grep -rn "map-pagination\|COUNT_REGION_ID" tests/` | 7 + 2 — the 7 are `test_overflow.py`'s pre-existing region reads, all green |
| B2 file moved on disk | none moved | n/a |
| B3 byte-identical golden captures this source | `tests/test_darkside_census.py:212` pins the **literal source text** of the pill's tail call | **DID NOT FIRE.** The line is byte-identical; my change rewrote the expression feeding it. Suite 24/24, and the sibling `len(sites) == 38` arm passes |
| B4 artifact produced here consumed elsewhere | `ViewState` roster | `test_a3_census.py` — **15/15 green**, the arm inspects `f.default is MISSING`, never `f.name` |
| **A3** | interface consumed by another module changed | `IRenderer.render` signature | **DID NOT FIRE, verified rather than assumed.** `inspect.signature` is byte-identical before and after: `(self, graph: 'Graph', state: 'ViewState') -> 'Text'`. Roster changed `query` → `hits`; signature did not. The standing pre-authorization is left **unspent** |

**⚠ C-48 — the pin that DID fire, and it was not declared anywhere.**
`test_a3_census.py::test_tc_a3_the_census_cardinalities_are_PINNED` went red: `derived 57 arg-ful
call sites against a pinned 52`. The pin's own docstring demands an itemised reason, so:

```
+3  tests/test_layered.py  AT-021 renders the same graph three times — empty hit set,
                           injected id, second injected id.  One render cannot distinguish
                           the hit style landing on the NAMED node from it landing on any.
+2  tests/test_fold.py     TC-026b's rename arm renders a folded branch with an injected hit
                           set and again with an empty one — the pair that proves the tail is
                           query-driven rather than a constant.
```

The derivation was re-run mechanically (not counted by hand) and the five new sites enumerated by
file and line before the pin was touched. The pin's sibling arms (`zeroarg == 26`,
`render_definitions() == 7`) are unmoved.

### Signed-balance test ledger

Base is the brief's declared figure, and my measured entry has the **same node count** — only one
node's verdict differs (Block 1).

| Lane | base | − D | + A | = post | measured |
|---|---|---|---|---|---|
| default (`-m "not slow"`, incl. xfail) | 804 | 0 | **12** | **816** | 812 passed + 1 failed + 3 xfailed = **816** ✓ |
| all markers (incl. 17 deselected) | 821 | 0 | **12** | **833** | 816 + 17 = **833** ✓ |

The 12 added: `tests/test_search.py` **9**, `tests/test_layered.py` **1**, `tests/test_fold.py` **2**.
**D = 0** — no node was deleted; `test_app.py`'s export arm was *migrated in place*, not replaced.

### Ruff — SET comparison, identical scope at entry and exit

Scope `mapper/ tests/` both times, identical command. **An aggregate cannot see a swap**, so the
comparison is over `(file, rule)` pairs:

```
entry pairs: 19    exit pairs: 19
--- NEW  (in exit, not entry) ---   (none)
--- GONE (in entry, not exit) ---   (none)
Found 27 errors.
```

`19` pairs / `27` findings, matching the pre-gate exactly. Two findings were actively prevented
rather than accidentally absent: dropping the now-unused `Node` import from `layered.py` when
`_matches` went, and removing an unused alias from `test_search.py` caught on the first lint pass.

---

## 5 · Risks

1. **The pill's number changes for every existing map, on purpose.** Anyone reading a stored
   screenshot or a habit of "this branch hides one match" will see a different figure. It is
   declared (`LLR-N07.1.3`), measured (`+2 1 → +2 2`, `+5 2 → +5 4`) and now gated (`TC-026b`) —
   but it is a user-visible change and the release note owes it a line.
2. **`n` in `n/N` is the SELECTION's place, and it is `0` until Inc-4b's walk lands.** On a fresh
   screen the operator sees `0/5 coincidencias en el mapa`, which reads oddly before the walk
   exists. The alternative — reserving a placeholder `1/` — would be false. Inc-4b should re-read
   this the moment `n`/`N` move the cursor; nothing else needs to change for it to become right.
3. **Per-keystroke cost is still unmeasured.** `Graph.search_hits` builds a joined string per node
   per query, and `_search_order` now runs on every `_pagination_text` and every `_view_state`.
   Nothing calls it on `on_input_changed` today (only on submit), so the exposure is one resolution
   per repaint at fixture scale. The architect flagged this as undetermined; I did not measure it
   against `MAX_RENDER_NODES`-scale graphs either.
4. **The empty-result TONE is not painted.** `LLR-N07.3.2` also asks for a muted query chip, a hint
   line and two toasts — all Inc-4b's, all unbuilt here. I deliberately painted the count line in
   one uniform tone rather than shipping a tone split nothing observes; see §6.
5. **`mapper/search.py` is LF while `app.py`, `layered.py` and `model.py` are CRLF.** Written fresh
   by me; git's normalization warning fired on staging, so the committed form will be consistent.
   Harmless, but it is why the mutation harness needed line-ending-aware anchors, and a
   `sed`-style patch against that file will behave differently from one against its neighbours.

---

## 6 · Pending items / spec deviations

**Deviations from `02l`, each with its executed reason:**

1. **`02l` §7.1 limb 5 is WRONG, and following it would have produced a silently vacuous arm.** It
   places `AT-018`'s pan state on `legacy` at 118x34 on the claim that the pan arm is reachable
   there. Executed: `pan_extent(legacy)` at that size returns `((53, 56), (13, 25))`, so
   `max_pan_x` **and** `max_pan_y` are both **0** — `legacy` does not overflow in either axis at the
   declared context, the `L` chord is a no-op (80 presses, `pan_x` still `0`), and state (c) would
   have degraded into state (a) while looking like it exercised the viewport. `AT-018` uses
   `inc3_support.pan_graph` instead (`max_pan_x = 49`), and asserts `pan_x > 0` and that a hit
   *actually left* `painted_ids` before reading anything. `AT-019` keeps the sealed `carlos` /
   `legacy` pin, where it belongs.
2. **`AT-021` is ONE node, not the two I first wrote.** `C-18` maps one acceptance id to one
   on-disk node; the AST census is folded into the same node as the injected-id arm.
3. **`P-021.3` (the pill re-route) moved from `AT-021` to `TC-026b`.** `02l` predates the `#D36`
   fold that created `LLR-N07.1.3`; that LLR's declared acceptance is `TC-026b`, so the pill's
   assertion lives there. `AT-021` keeps `LLR-N07.1.1`'s own chain.
4. **`P-052.2` (the hint line reading its glyphs from the seat) is NOT built.** It gates the hint
   line and the seat, both Inc-4b's. `AT-052` here is `P-052.1` plus the count line's positional
   half of `LLR-N07.3.2`, which is asserted because Inc-4a owns the count line.
5. **`M-N07.1.3-a`'s strict reading is not fully exercised.** It asks the pill fixture to place a
   match of each delta kind among a folded branch's descendants. On `02l` §3's pinned six-node
   shape the only id-only match is the root, which is not its own descendant, so the pill exercises
   the **subtitle** and **attachment** limbs (root: `2 → 4`) and the **attachment** limb (`b`:
   `1 → 2`) but not **id**. The id limb is exercised by `AT-020` and by the card style. I built the
   shape as tabulated rather than adding a seventh node that would have invalidated `02l` §3's
   executed dict/tree-order figures — flagged instead of silently widened.

**Owed, not closed here:**

6. **`A-k3` — `docs/ARCHITECTURE.md:159` is undischarged and now false in one more way.** Its row
   still enumerates `query` in the roster and still promises the replacement as future work. It was
   already stale by three fields at baseline (`pan_x`, `pan_y`, `folded`). A doc is outside the
   source budget, but it is outside my brief too, so I did not edit it.
7. **Block 1's two characters** in `02l`, above.
8. **`C-D6a` remains structurally vacuous** (`02l` §8.3) and needs the explicit ruling that section
   asks for. Inc-4a's `_search_order` happens to satisfy option (a)'s shape — one attribute, no
   `or` fallback — but no predicate here pins it as such, and I am not claiming coverage I did not
   build.
9. **The working tree carried more than the brief declared.** `.dev-flow/.../PLAN.md` is modified
   (its new §17 documents the Inc-4 split, dated today) in addition to the declared
   `01-requirements.md` + `state.json`. Not mine, not test-written, left untouched — recorded so the
   gate does not read it as drift.

---

## 7 · Suggested next task

**Inc-4b**, in this order: (a) the `#D5b` seat rebind plus the `test_cd25a` repair the pre-gate
already specified — freeze Inc-3's exit as a literal snapshot and give Inc-4 its own census — since
that test goes red by construction the moment the seat moves; then (b) the `n`/`N` walk over
`SearchIndex.query`'s tree-ordered list, which is ready and gated; then (c) `LLR-N06.2.4`'s fold
auto-open, `E1b`/`E1c`, and `esc`. Before starting, decide `C-D6a` (§6.8) and re-read risk 2 above:
`n`'s meaning is the one thing Inc-4b inherits from here that it can silently get wrong.

---

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|
| 1 | ≤4 source files, or reason declared | ✓ | §2 — exactly 4, with the "cannot be cut smaller" argument |
| 2 | Tests written in this same increment | ✓ | 12 new nodes, §4 ledger |
| 3 | Layer 0 written where the criterion applies | ✓ | 5 unit nodes, §4 |
| 4 | RED counterfactual captured **and restored by hash** | ✓ | 17 mutations, 22 arm-runs, sha256 table §4 |
| 5 | Reverse census run on every touched symbol | ✓ | §4 B-table; the pin that fired is itemised, the declared one that did not is evidenced |
| 6 | `code-reviewer` passed — a HIGH blocks | ⚠ | **not run** — the brief routes it to an independent reviewer after your gate |
| 7 | No file from another lane touched | ✓ | `git diff HEAD --stat mapper/keymap.py` → 0; `test_inc3_census.py` + `test_key_dispatch.py` 54 passed |
| 8 | Frozen interfaces untouched (or returned to the trunk) | ✓ | `IRenderer.render` signature byte-identical; `test_a3_census.py` 15/15; pre-authorization unspent |
| 9 | Coverage claims verified **on disk**, not from intent | ✓ | every figure in this packet re-derived mechanically this session; no number transcribed from `02l`, `02k` or the pre-gate without re-execution |
| 10 | Load-bearing emptiness declared, with its synthetic instance (C-55) | ✓ | §4 C-55 table; `tests/inc4_support.py::build_adjuntos` |
| 11 | Mutation verdicts recorded **per arm**, inert arms named (C-40 rider) | ✓ | §4 — per-node runs, 1-arm assertion, both GREEN secondaries named, plus the mutation that could not be written |
| 12 | Baseline green before starting | ✗ | **BLOCK 1** — see §0. Pre-existing, cause identified to the character, outside `mapper/`, constant across the session |

**Evidence checklist (agent-level)**

- ✓ Tests / lint pass — 812 passed + the declared pre-existing red; ruff set identical (19 pairs / 27).
- ✓ No secrets in code or output — every fixture synthetic and generated into `tmp_path`.
- ✓ No destructive commands run without approval — no commit, no push, no delete; mutations applied
  in `try/finally` and proven restored by sha256. **Nothing was written into `fixtures/`**:
  `git status` shows no fixture file modified.
- ✓ File count within cap — 4 / 4 source.
- ✓ Review packet attached — this file.

---
---

# Review round 2 — both reviews returned BLOCK; this is the fix pass

| Field | Value |
|---|---|
| Date | 2026-08-29 |
| Entry | `feat/ui-next-batch-02` @ `5f4816c`, working tree, **still nothing committed** |
| Reviews answered | `increment-004a-code-review.md` (F1–F7) · `increment-004a-security-review.md` (F1, F1a, F1b, F2) |
| Files touched this round | `mapper/search.py`, `mapper/app.py`, `tests/test_search.py` — 2 source, within the declared 4-file lane |
| `mapper/keymap.py` | **untouched** (Inc-4b's) — `git diff HEAD --stat mapper/keymap.py` → 0 lines |
| Fast lane | **818 passed, 17 deselected, 3 xfailed — exit 0, zero FAILED** |
| Ruff set | **19 pairs / 27 findings — matches the entry pin exactly** |

## R0 · BLUF

**Both HIGHs are fixed and both are now gated by predicates that fail when the fix is
removed.** The quadratic is gone from the repaint path — measured through the real app, the search
went from **65% of a 22.5 s frame to 1.0% of an 8.1 s frame** at the renderer's declared ceiling, and
from **4 resolutions per repaint to 1**. The shared-resolution arm was rebuilt: the reviewer's five
candidate shapes, **three of which passed the old arm**, now all redden, as does the new-consumer
shape the old arm never inspected.

Two corrections to the reviews themselves, both measured rather than argued:

- **The code review's suggested predicate for F1 would have reddened on correct code.** It bans
  `folded`/`pan_x`/`pan_y` from `_view_state`, but `_view_state` reads all three **legitimately** —
  handing the viewport to the *renderer* is its entire job. Executed: `_view_state`'s `self.*` reads
  are `{_focus_owner, _search_hits, diff, diff_active, folded, nav, pan_x, pan_y}`. Applying the
  snippet as written fails on the tree as it stands. The ban is therefore extended to `_count_line` —
  where it *is* clean and where the LLR's wording lands — and `_view_state`'s hit argument is pinned
  structurally instead.
- **F7 (`search.py` line endings) is not this increment's.** Measured at `HEAD`: `search.py` was
  already LF-only there (0 CRLF), as was `views/state.py`. Not a regression, not normalised — see R6.

## R1 · What changed

### H1 — the quadratic in the repaint path · **fixed, all four parts**

| # | Where | Operation |
|---|---|---|
| 1 | `search.py::tree_order` | the child index is built in ONE `O(E)` pass over the edge list before the walk, replacing the per-node call into the model's full edge scan |
| 2 | `search.py::query` | the membership set for the tail clause is bound once before the comprehension instead of being rebuilt per candidate |
| 3 | `search.py::query` | an early return on an empty hit set, placed **before** the walk |
| 4 | `app.py::_search_order` | a size comparison against the renderer's own bound returns the empty order above it; below it, a frame-scoped memo keyed on the graph object and the query text |
| 4b | `app.py::_open_paint_pass` (new, 1 line) | drops the memo; called first by `refresh_canvas` and by `_declare_after_layout` |

**Part 3 mattered more than its size suggests.** The blank-query guard was correct for the *result*
and silent about the *work*: measured before the fix, a whitespace query at 12000 nodes still cost
**3.26 s per call**. That is the state of a screen nobody has searched on — the default, not an edge
case.

**Why the memo cannot go stale.** It is dropped at the *start* of every repaint, so reading a stale
order requires having already painted a stale screen. It holds the graph **object**, not its `id()`,
so a map switch cannot alias it, and the query text is part of the key.

**`shipped == fixed` proven here, not taken from the reviews.** Both reviewers asserted
output-identity independently; I re-derived it. The pre-fix outputs of `query` and `hits` were
captured over **8 queries x 12 graphs = 96 cases** — the two real `.mmd` fixtures, a graph carrying a
4-cycle, a self-loop, a diamond, a dangling edge and a disconnected component, and synthetic trees at
300/1200/3000 nodes — then re-compared after the fix:

```
cases compared: 96   mismatches: 0
shipped == fixed : True
```

### H2 — the shared-resolution arm now gates what it claims · **fixed**

The old predicate was positive membership only. It is replaced by four predicates:

1. the viewport ban, now over **`_search_order` and `_count_line`** — `LLR-N07.2.1` governs "the
   count computation", which is both;
2. `_view_state`'s hit argument pinned **structurally** as a bare unnarrowed call to the helper (an
   AST check on the keyword's value), so the seam can keep reading the viewport for the renderer
   while the hit set cannot be filtered by it;
3. an AST census over the whole module: the owner is **constructed exactly once** (1 site today);
4. a second census: the model's **raw resolver is reached zero times** from `app.py` — closing the
   shape that adds a second resolution *without* constructing the owner and so slips past (3).

**The docstring is corrected.** It no longer claims the surfaces "could not have" disagreed "for a
deeper reason than 'both happen to call the same function today'". It now states what each predicate
proves, and records that the old arm established exactly that and nothing more.

### Medium and low

| Finding | Disposition |
|---|---|
| **M1** · the `n` numeral ungated | **Fixed.** New node asserts the ordinal is the cursor's place in the resolved order, `0` when it is not a hit — **derived**, never spelled, because `0/N` is fixture-dependent (`adjuntos` reads `1/5`; the root matches by id). The loop visits every hit and every non-hit and asserts the set of observed ordinals is exactly `{0..len(order)}`, so it cannot pass having stayed in one branch |
| **M2** · `tree_order` / `_incomplete_order` duplication | **Pinned, not deduped** — reasoning in R4 |
| **L · AT-052 residue** | **Closed.** A floor on the declared subject's word count. The un-writable mutation itself stands as declared in round 1 |
| **L · `COUNT_REGION_ID` comment overclaims** | **Comment corrected**, re-typing left: `test_overflow.py` is outside this lane's 4 files |
| **L · LF/CRLF** | **Not touched** — measured pre-existing at `HEAD`, see R6 |
| **SEC-F2** · `hits.index()` scans twice | **Not fixed**, recorded. Linear, and now runs once per frame rather than four times |

## R2 · Re-measured timings

`PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1`. Same harness for both columns; the pre-fix algorithm is
reconstructed **in the probe**, so no file is edited between the two readings.

**The owner in isolation** — one `SearchIndex.query` call:

| N | query | shipped | fixed | speedup |
|---|---|---|---|---|
| 3 000 | active | 0.2176 s | **0.0031 s** | **70x** |
| 3 000 | blank | 0.1847 s | **0.0000 s** | early return |
| 12 000 | active | 4.1858 s | **0.0132 s** | **317x** |
| 12 000 | blank | 3.2562 s | **0.0000 s** | early return |

`hits` alone is unchanged (0.0020 s / 0.0075 s) — it was never the cost.

**Through the real app**, one `refresh_canvas` on a graph of N nodes, counting *resolutions* rather
than helper calls so a memo hit is visibly not a resolution:

| N | query | resolutions | search time | frame wall | search share |
|---|---|---|---|---|---|
| 3 000 | active | **4 -> 1** | 834.7 ms -> **3.5 ms** | 1359 ms -> **503 ms** | 61.4% -> **0.7%** |
| 3 000 | blank | **3 -> 1** | 550.1 ms -> **0.0 ms** | 1079 ms -> **604 ms** | 51.0% -> **0.0%** |
| 12 000 | active | **4 -> 1** | 14 590.6 ms -> **77.4 ms** | 22 455 ms -> **8 051 ms** | 65.0% -> **1.0%** |
| 12 000 | blank | **3 -> 1** | 9 127.9 ms -> **0.0 ms** | 17 106 ms -> **8 038 ms** | 53.4% -> **0.0%** |

The 4-per-frame and 3-per-frame counts reproduce the security review's instrumentation exactly.

**Above the renderer's bound**, where the frame previously burned seconds to paint a refusal:

```
MAX_RENDER_NODES = 12000
N=12002  over_bound=True   ONE refresh_canvas: resolutions=0   search=0.0 ms
N=15001  over_bound=True   ONE refresh_canvas: resolutions=0   search=0.0 ms
```

**Stated honestly, and NOT claimed as fixed:** the residual frame at 12 000 nodes is still **~8 s**,
and above the bound still **~3.2 s**. None of that is search — measured at 0.0–1.0% — it is the
renderer and layout, which this increment did not touch. That is `S-15`'s underlying observation
("the bound limits the render COUNT, not the WORK"), pre-existing and **still open**. What this
increment closes is the escalation it introduced, not `S-15` itself.

## R3 · Mutation table — per-arm verdicts, sha256 restores

Every mutation is described by **position and operation**; no mutated token is spelled. Each was
applied to the working tree, the named arm run alone, then the file restored and its digest compared
to the pre-mutation digest. A restore mismatch aborts the battery.

```
expected arm count: 10
pre-battery  app.py    sha256 a2b621256c22e533
pre-battery  search.py sha256 77836620bbddec54
```

| id | file · position | operation | node run | verdict | restore |
|---|---|---|---|---|---|
| **MR-1** | `app.py::_count_line`, the line taking the resolved order | narrow it by the screen's fold set | shared-resolution arm | **RED** `1 failed` | ok |
| **MR-2** | `app.py::_search_hits` | replace the delegation with a construction of the owner | shared-resolution arm | **RED** `1 failed` | ok |
| **MR-3** | `app.py::_search_order`, the size comparison | raise the compared bound so it is never reached | bound arm | **RED** `1 failed` | ok |
| **MR-4** | `app.py::_open_paint_pass`, its body | make it a no-op, so the memo outlives its pass | memo arm | **RED** `1 failed` | ok |
| **MR-5** | `search.py::query`, the empty-hit return | delete it | no-walk arm | **RED** `1 failed` | ok |
| **MR-6** | `app.py::_count_line`, the ordinal expression | replace the cursor's place with a constant | selection-numeral arm | **RED** `1 failed` | ok |
| **MR-7** | `app.py::_incomplete_order`, the child push | push in the opposite order | walk-agreement pin | **RED** `1 failed` | ok |
| **MR-8** | `app.py`, the declared count subject | degrade toward a single token | `AT-052` | **RED** `1 failed` | ok |
| **MR-9** | `search.py::tree_order`, the child index | key it by the other edge endpoint | whole file | **RED** `2 failed, 12 passed` | ok |
| **MR-10** | `app.py::_view_state`, the hit argument | narrow it by the fold set at the seam | shared-resolution arm | **RED** `1 failed` | ok |

```
post-battery app.py    sha256 a2b621256c22e533  identical=True
post-battery search.py sha256 77836620bbddec54  identical=True
arms run: 10   RED: 10   INERT: 0
```

**The three the brief required are MR-1 (viewport ban), MR-2 (constructed-once census) and MR-3
(the bound).** MR-4 and MR-5 cover the two remaining parts of the H1 fix. The arm count is asserted
by the harness, so no inert arm can hide behind a failing sibling.

### The reviewer's five shapes, re-executed against the rebuilt arm

Same node, same technique the reviewer used, run on the arm as it now stands:

| Variant | old arm | **new arm** |
|---|---|---|
| V1 — count line resolves for itself, helper reference removed *(the historical defect)* | RED | **RED** |
| V2 — an independent resolution **added beside** the retained helper call | **GREEN** | **RED** |
| V3 — V2, the added path scoped to the viewport *(the A-6 defect)* | **GREEN** | **RED** |
| V4 — helper stays pure; the count line narrows its result by the folded set | **GREEN** | **RED** |
| V5 — a **new fourth consumer** resolving independently *(Inc-4b's next shape)* | never inspected | **RED** |
| V6 — the renderer's set narrowed at the seam while the count stays pure | not probed | **RED** |

```
variants run: 6   blind: none
post app.py sha256 a2b621256c22e533  identical=True
```

## R4 · M2 — the judgement call, and why I chose the pin

**Decision: pin the two walks with a predicate; carry the dedup. I did not change
`_incomplete_order`.**

The reviewer is right that the docstring's stated reason is wrong — `app.py` already imports
`search`, so the `search -> app` direction it rejects is not the direction on offer, and
`_incomplete_order` consuming `tree_order` creates no new edge. That correction is now in the test's
docstring.

I still did not make the change, for one reason that is about risk and not about taste:
`_incomplete_order` is the **US-N04 coverage worklist's ordering** — a different requirement's shipped
behaviour, outside this increment's acceptance. Rewriting it would change a shipped path on a gate
that does not cover it, in a pass whose whole purpose is clearing two blocks. The dedup is a
simplification worth doing; it is not worth doing *here*, unsupervised, while the increment is under
review.

**What the pin buys is the property the dedup would have bought** — that "next match" and "next
missing field" mean the same "next" — at zero behavioural risk. And it is a real pin, not a
formality, because **no shipped fixture discriminates**:

```
legacy       N=   8 incomplete=  2  tree!=insertion:True   MISSORDER discriminates: False
anidado      N=   7 incomplete=  0  tree!=insertion:True   MISSORDER discriminates: False
pan_graph    N=  25 incomplete=  0  tree!=insertion:False  MISSORDER discriminates: False
adjuntos     N=   6 incomplete=  0  tree!=insertion:True   MISSORDER discriminates: False
```

Three fixtures have no incomplete node at all, and on `legacy` the two incomplete nodes emerge in the
same relative order under a tree walk and under dict-insertion order — so a pin on any of them would
have passed against a walk that ignored the tree entirely. The test therefore **builds its own
graph** (insertion order deliberately unequal to tree order, plus a diamond, a self-loop, a dangling
edge and an edge into the reachable set from outside it) and **asserts the discrimination holds**
before asserting agreement. MR-7 confirms it: reversing the worklist's push order reddens it.

**Carry:** `_incomplete_order` consuming `tree_order` — a strict simplification removing ~14 lines,
to be taken in a US-N04-scoped increment where its acceptance covers the change.

## R5 · Corrected ledger and ruff set

Base is the **review-verified** entry, not round 1's packet figure: both reviewers re-ran the fast
lane and measured `813 passed / 17 deselected / 3 xfailed`, Block 1 having gone green when the
orchestrator removed the two hostile code points from the `02l` artifact.

| Lane | base | − D | + A | = post | measured |
|---|---|---|---|---|---|
| default (`-m "not slow"`) | 813 | 0 | **5** | **818** | **818 passed**, 3 xfailed ok |
| all markers (incl. 17 deselected) | 830 | 0 | **5** | **835** | 818 + 17 = **835** ok |

**D = 0.** The shared-resolution node was *rebuilt in place*, not replaced, so it is not an addition;
`AT-052` gained an assertion inside an existing node. The 5 added, all in `tests/test_search.py`:

| node | gates |
|---|---|
| `test_the_selection_numeral_is_the_cursors_place_among_the_hits` | M1 — the `n` numeral |
| `test_the_search_obeys_the_renderers_declared_bound` | H1 part 4 — the bound |
| `test_a_query_that_matches_nothing_does_not_walk_the_tree` | H1 part 3 — the early return, counted not timed |
| `test_one_paint_pass_resolves_exactly_once` | H1 part 4 — the memo, both halves |
| `test_the_two_tree_walks_agree` | M2 — the pin |

Read from the one final run's own output:

```
818 passed, 17 deselected, 3 xfailed in 150.18s (0:02:30)
exit=0
```

**Ruff — SET comparison, same command and same scope (`mapper/ tests/`):**

```
findings: 27   distinct (file,rule) pairs: 19
MATCHES ENTRY PINS (19 pairs / 27 findings): True
```

Unchanged from entry. The one `mapper/app.py F401` in the set is pre-existing (an unused `re` import
at the top of the module); the `MAX_RENDER_NODES` import added this round is used and adds nothing to
the set.

**Digests after everything**, matching the mutation battery's post-battery values — evidence of a
clean restore:

```
77836620bbddec54  mapper/search.py
a2b621256c22e533  mapper/app.py
bd035104c012dee8  tests/test_search.py
0b661033b2ceff9a  mapper/views/state.py   (untouched this round)
3e081a6c61af9a20  mapper/views/layered.py (untouched this round)
```

## R6 · What I did NOT fix, and why

1. **F3 / M2 — the `tree_order` / `_incomplete_order` dedup.** Pinned, not deduped. R4.
2. **F7 — LF vs CRLF.** Measured at `HEAD`: `search.py` was already LF-only there (0 CRLF
   sequences), as was `views/state.py`. This increment did not introduce it, so round 1's
   self-declaration was itself wrong. Normalising would put whole-file churn into a diff under
   review; it belongs in a repo-wide `.gitattributes` pass, and is carried as such.
   **CORRECTED IN ROUND 3 (was NEW-5, and both rounds had the direction wrong).** The files that
   actually moved are **`mapper/app.py` and `mapper/views/layered.py`**, converted wholesale
   LF -> CRLF on disk; `search.py` is the one that did **not** change. Invisible to git
   (`core.autocrlf=true`, `git diff --numstat` `125/4` and `16/19`), so it is not a gate — but the
   `.gitattributes` carry must name `app.py` and `layered.py`, not `search.py`, or `Inc-REPAIR`
   inherits the wrong two files.
3. **F6 — the 7 re-typed literals in `test_overflow.py`.** The *comment* overclaimed and is
   corrected; routing the 7 sites through the constant means editing a file outside this lane's
   declared 4. Carried.
4. **SEC-F2 — the double list scan for the selection ordinal.** LOW, linear, and now executed once
   per frame instead of four times. Recorded, not changed.
5. **`S-15` — the bound limits render count, not work.** Still open, and R2 says so with numbers: the
   ~8 s frame at 12 000 nodes and the ~3.2 s frame above the bound are renderer and layout cost, not
   search. This increment closes only the escalation it introduced.
6. **`F-A`, and the username path leak in the export toast.** Pre-existing, routed to `Inc-REPAIR`,
   untouched here — the security review's own finding, and I confirm the diff adds no sibling.
   **ADDRESS CORRECTED IN ROUND 3:** this diff shifted the line. `:2296` was already stale when
   round 1 wrote it; the security confirmation corrected it to **`:2337`**, which was right for the
   tree it measured. **Round 3's own docstring additions moved it again, to `mapper/app.py:2373`**
   (measured after the edits below, not predicted). `Inc-REPAIR` inherits `:2373`, and the durable
   address is the statement itself — the `_event_toast("exportado", ...)` call in
   `action_export_svg`, which is what a line number keeps failing to hold on to.
7. **The code review's literal snippet for F1 fix (1).** Not applied as written; it reddens on
   correct code. Replaced with the two predicates in R1/H2. Stated in R0.

## R7 · Evidence checklist — round 2

- ok **Full fast lane re-run, evidence from that one run** — `818 passed, 17 deselected, 3 xfailed`,
  exit 0, zero FAILED. No figure in this section is stitched from a partial run.
- ok **Ruff compared as SETS** over `mapper/ tests/` — 19 pairs / 27 findings, matching entry.
- ok **Per-arm mutation verdicts with sha256 restores** — 10 arms, expected count asserted by the
  harness, 10 RED, 0 inert, both source digests byte-identical before and after.
- ok **A mutation for each HIGH fix** — MR-1 (viewport ban), MR-2 (constructed-once census),
  MR-3 (the bound), plus MR-4 and MR-5 for the memo and the early return.
- ok **No mutated token or hostile code point spelled** — every mutation described by position and
  operation. No `.dev-flow` file gained a literal from a probe.
- ok **Perf re-measured at N~3000 and N~12000**, isolated and through the real app, with the
  unfixed residual named rather than absorbed.
- ok **No secrets** — every fixture synthetic, built in `tmp_path` or `tempfile.mkdtemp`.
- ok **No destructive command, nothing committed** — `git status --porcelain` shows the same tracked
  set as at entry plus this file's edit; no fixture file modified.
- ok **File cap** — 2 source files this round (`search.py`, `app.py`), inside the declared 4-file
  lane; tests uncapped by the brief.
- ok **`mapper/keymap.py` untouched** — 0 lines.

## R8 · Verdict on my own round-2 work

Both HIGHs are discharged with predicates that fail when the fix is removed, and the three shapes
that previously slipped the gate no longer do. The one thing a reviewer should look at hardest is
**the memo's staleness argument in R1** — it is the only new construct whose correctness rests on a
protocol ("every repaint opens a pass") rather than on a local property. That protocol is itself
pinned structurally, and MR-4 reddens when the pass stops clearing; but it is the piece I would
probe first.

---

# Review round 3 — both confirmations PASSED with mitigations attached; this discharges them

| Field | Value |
|---|---|
| Trigger | `increment-004a-code-review-confirmation.md` (**PASS**) and `increment-004a-security-confirmation.md` (**SIGN-OFF**) — both conditional on listed mitigations |
| Under repair | code lens NEW-1 / NEW-2 / NEW-3, security lens NEW-1 / NEW-2 / NEW-3, plus the two mis-routed carries |
| Branch / entry | `feat/ui-next-batch-02` @ `5f4816c`, **nothing committed** |
| Entry digests | `app.py a2b621256c22e533`, `test_search.py bd035104c012dee8` — identical to both reviewers' declared values, so this repaired the tree they measured |
| Scope | `mapper/app.py`, `tests/test_search.py` (+ this file). `search.py`, `views/state.py`, `views/layered.py` **not touched this round**; `mapper/keymap.py` **0 lines** |

## S0 · BLUF

**A conditional verdict is not an authorisation, and the mitigation both lenses attached first is
the one that mattered: my own F1b repair painted a false statement.** Above `MAX_RENDER_NODES`
`_search_order` returned an empty order, `_count_line` could not tell that from a question that came
back empty, and the strip therefore declared `0 coincidencias en el mapa` over a graph the security
lens measured as holding **241 real matches**. That is the defect class US-N07 exists to close,
reintroduced at smaller scale by the fix for it, and it contradicted both docstrings I had just
written. **Fixed first: the bound now returns `None`, and the count line paints nothing there.**

**All five items are discharged in code, and each carries a mutation that reddens it.** The two
count-line facts fail **independently** — measured, not asserted: the mutation that collapses the
bound into an empty order reddens the above-bound arm and leaves the empty-state arm GREEN, and the
mutation that deletes the empty-state wording does the exact opposite.

**The open-pass pin is now derived, and I measured that the retired hand-list would have slipped.**
Under a mutation that adds `Inc-4b`'s exact shape — a keypress-bound consumer reaching `_view_state`
with no pass opened — the derived census is **RED** and the retired two-tuple predicate is
**GREEN**. That is C-31 demonstrated on this file rather than quoted at it.

**Nothing was deferred silently.** S6 lists what I did not do and why.

## S1 · R3-1 · The bound painted a false count — fixed first

`_search_order` now returns **`None`** above the renderer's bound, never an empty order, and
`_count_line` paints **no line at all** in that state. The strip's own `N fuera de vista`
declaration is what tells the operator why, so nothing is lost by the silence.

`_search_hits` collapses `None` and empty to the same empty `frozenset` — deliberately, and its
docstring says so: above the bound the renderer paints no tree, so a hit set that highlights nothing
is the truthful parameter. The distinction only matters where something is **declared** about the
answer, which is the count line and nothing else.

Measured after the fix, unmounted, on the shipped `_titled_graph` shape:

```
above bound  N= 12002 real_matches=  6001 order=None      count_line=''
at bound     N= 12000 real_matches=  6000 order=len=6000  count_line='0/6000 coincidencias en el mapa  '
```

**Two acceptance arms, because these are two different facts:**

- `test_above_the_bound_the_count_line_does_not_claim_zero_matches` — above the bound, with matches
  the owner still finds, no count line may be painted. Non-vacuous by an independent
  `SearchIndex(...).hits(...)` assert: without it the arm would pass on a graph that genuinely has
  none, where `0` would be **true** rather than a lie.
- `test_below_the_bound_the_count_line_still_says_zero_when_empty` — the empty-result wording
  survives. The cheapest way to satisfy the first arm is to stop painting the `0` line at all, which
  would silently delete `AT-052`'s empty state; this holds the other half, on the same fixture
  shape, with the side of the bound as the only variable.

Both read the count line through `_count_line_text`, which **asserts structurally** that
`_pagination_text` still appends `_count_line` bare before reading it — so the string under
assertion is the string painted, and the helper cannot drift into reading a surface the operator
does not see.

## S2 · R3-2 · The viewport ban stopped one method short — one token, and it is load-bearing

`MapScreen._search_hits` added to the ban tuple. It reads no viewport state and has no reason to, so
the ban is free, as the code lens said.

**I did not take "it is free" on trust, and I did not take "it was needed" on trust either.** The
control: revert the tuple to its round-2 two-method form, apply the same narrowing inside
`_search_hits`, run the sharing arm.

```
ban reverted to the round-2 two-method form + the same mutation:  GREEN   <- it slips
ban as shipped this round        + the same mutation:             RED
```

So the added token is what catches it, not something else that was already there. The arm's
docstring now records the constructed defect by position and effect — count 5 against 4 painted
highlights on `adjuntos`, for each of the three hits that are foldable branches.

## S3 · R3-3 · The open-pass pin is derived now, and the hand-list is measured to have been blind

Retired: the two-tuple over `refresh_canvas` / `_declare_after_layout` and its false comment.
Shipped: `test_every_reader_of_the_resolution_is_inside_a_paint_pass`.

Seeded from the resolver and the memo, readers are grown transitively over `self.X` calls, and the
growth **stops at any method that opens its own pass** — which is precisely the contract's
semantics: a caller of `refresh_canvas` is covered because `refresh_canvas` opens one. What survives
is the set that reaches the resolution **without** a pass, and every member must carry a stated
reason in `_PASS_FREE_READERS`.

**That dict is a shrinking list, never a defining one.** The set it excuses is derived, so a reader
added tomorrow appears in the derivation and fails as *unexplained*; a stale entry fails too; and an
exemption with an empty reason fails. This is the structural difference from what it replaces.

Measured on the shipped tree: **76 methods parsed, 2 openers, 15 pass-free readers.** The three
exemptions that are judgements rather than bookkeeping are named in the docstring — `_pan` (reads
the extent of the frame already on screen, then repaints), `action_export_svg` (renders the frame
currently painted, so the previous pass's memo is the correct input), `_reclamp_pan` (called from
inside `refresh_canvas`'s own pass). Neither lens could construct a live stale paint through any of
them and neither can I; they are registered as safe **today**, with the reason, not waved through.

**Anti-vacuity, all four limbs asserted before any verdict is read:** the class must parse to a
plausible method count; the seeds must resolve to real methods; the derived set must clear a floor
measured at 15; and `action_pan_left` — which reaches the resolution *only* through `_pan` — must be
present, which is the receipt that the transitive step ran rather than the seed being reported back.

## S4 · R3-4 · The memo's own list is no longer handed out

`_search_order` returns a `tuple`, and stores that same tuple in the memo, so the returned object
and the memoised object are one immutable thing. `__init__`'s annotation moved with it.

`test_the_resolution_cannot_be_corrupted_by_the_caller` asserts the **property, not the type**: it
attempts the corruption and re-reads. It holds for a tuple, for a defensive copy, or for any later
shape — what it forbids is the aliasing.

## S5 · Mutation battery — 12 arms, per-arm verdicts, sha256 restores

Verdicts read **per resolved arm** from that arm's own run with the collected count asserted at 1,
never from a process exit code. Every mutation described by position and operation; no mutated token
is spelled here.

```
pre  app.py         b960f4eff37093c9      (round-2 exit state)
pre  test_search.py e22a72937b268e24
```

| id | position · operation | arm | verdict |
|---|---|---|---|
| **MR3-1a** | `_search_order`, the bound branch → the distinct signal replaced by an empty container | above-bound no-zero arm | **RED** |
| | | empty-state arm | **GREEN** *(independence)* |
| | | the bound arm | **RED** |
| **MR3-1b** | `_count_line`, the empty-result branch → returns the blank text used for the unanswered state | empty-state arm | **RED** |
| | | above-bound no-zero arm | **GREEN** *(independence)* |
| **MR3-2** | `_search_hits`, its body → the derivation narrowed by the fold set | shared-resolution arm | **RED** |
| | *(control)* same mutation, ban reverted to the round-2 form | shared-resolution arm | **GREEN — slips** |
| **MR3-3a** | `MapScreen` → a new keypress-bound consumer reaching `_view_state`, no pass opened *(Inc-4b's shape)* | derived open-pass census | **RED** |
| | *(control)* same mutation, evaluated against the **retired hand-written two-tuple** | retired predicate | **GREEN — slips** |
| **MR3-3b** | `_declare_after_layout`, its first statement → the opener call removed | derived open-pass census | **RED** |
| | | memo-lifetime arm | **GREEN** *(it owns behaviour, not the set)* |
| **MR3-4** | `_search_order`, the returned container → the immutable conversion removed | aliasing arm | **RED** |
| | | the bound arm | **GREEN** *(orthogonal, as intended)* |

```
arms run: 12 (+2 control predicate evaluations)   arm count asserted at 1 per run   INERT: 0
post app.py         b960f4eff37093c9  identical=True
post test_search.py e22a72937b268e24  identical=True
```

**MR3-1a / MR3-1b are the pair the brief asked for**: the two facts fail for different reasons and
neither arm can stand in for the other. **MR3-3a is C-31 made mechanical**: the same mutation is RED
against the derived set and GREEN against the list it replaced.

## S6 · What I did NOT fix this round, and why

1. **The code lens's NEW-4 (LOW) — the constructed-once census reads a bare `Name`.** A method
   reaching the owner through a local alias is invisible to it. Not fixed: the lens filed it as an
   inherent limit of any AST census and a contrived shape, the raw-resolver census already covers
   the realistic bypass, and I have no non-contrived construction for it. **Carried, stated, not
   silently dropped.**
2. **`S-15`, `F-A`, the export-toast path leak, the `.gitattributes` normalisation, the
   `tree_order` / `_incomplete_order` dedup, F6's re-typed literals.** All pre-existing, all already
   routed. Round 3 changed only the two **addresses** that had gone stale (R6 items 2 and 6 above).
3. **The three pass-free readers were exempted, not eliminated.** Routing `_pan` and
   `action_export_svg` through a pass is a behavioural change on paths this increment's acceptance
   does not cover, in a round whose purpose is discharging review mitigations. The honest move was
   to make them **visible and justified** rather than to change them under a gate that would not see
   the change. **`Inc-4b` must now either open a pass or add an entry with a reason — the arm forces
   that choice instead of letting it pass unnoticed, which is the whole point of landing this
   before `Inc-4b` rather than after.**
4. **I did not re-run the perf battery or the `-m slow` lane.** No change this round touches the
   walk, the early return, or the memo's keying. `search.py` is byte-identical to its round-2 state.

## S7 · Evidence checklist — round 3

- ok **Full fast lane, evidence from that one run's own output** — `PYTHONUTF8=1 python -m pytest -q
  -m "not slow"` → **`822 passed, 17 deselected, 3 xfailed in 140.76s`**, **exit 0**, zero `FAILED`.
  818 -> 822 is exactly the four new arms (two for R3-1, one for R3-3, one for R3-4);
  `tests/test_search.py` goes 14 -> 18. *(An earlier draft of this line claimed a fifth arm had been
  retired into the derived census and that this explained the delta. It does not, and there was no
  fifth arm: what R3-3 retired is an ASSERTION inside the memo-lifetime test, not a test function,
  so that test still collects. Corrected rather than left standing.)*
- ok **Ruff SET over `mapper/ tests/` identical to the entry pin** — `Found 27 errors`, and a sorted
  `file|rule` set diffed against the entry capture returns **empty**. *Accounting note, surfaced
  rather than smoothed over:* my dedup yields **21** distinct `file|rule` pairs where the brief pins
  **19**. The finding count (27) and the set identity both hold; the pair count differs by how the
  two derivations dedup, and I did not adopt the brief's number without being able to reproduce it.
- ok **Per-arm mutation verdicts with sha256 restores** — S5. 12 arms, arm count asserted at 1 per
  run, both digests byte-identical before and after, restore in a `finally`.
- ok **A mutation for each of R3-1, R3-2, R3-3, R3-4** — MR3-1a/1b, MR3-2, MR3-3a/3b, MR3-4, plus
  two control evaluations that measure what the *old* predicates would have done.
- ok **No mutated token or hostile code point spelled in any `.dev-flow` file** — every mutation
  described by position and operation.
- ok **No secrets** — no fixture, path, token or username entered this file or the diff. The one
  absolute-path sink is pre-existing and routed, not touched.
- ok **No destructive command; nothing committed** — `HEAD` still `5f4816c`. The mutation harness
  lives in the session scratchpad, never in the repo.
- ok **File cap** — **1 source file** (`mapper/app.py`) plus `tests/test_search.py` and this record.
  Inside the declared 4-file lane; tests uncapped by the brief.
- ok **`mapper/keymap.py` untouched** — 0 lines. `search.py`, `views/state.py`, `views/layered.py`
  byte-identical to their round-2 state.

## S8 · Verdict on my own round-3 work

The item I would probe hardest is **`_PASS_FREE_READERS`**. It is 15 entries, and a reader who skims
will see a hand-written list and read S3 as C-31 repeated. It is not — the derived set drives the
assertion and the dict can only *shrink* the alarm, which MR3-3a measures. But the strength of that
arm rests on the closure's stopping rule being right, and if a future opener clears the memo under a
different name the walk would stop propagating for the wrong reason. That is the seam.

The second is **the three exemptions themselves**. `action_export_svg` consuming the previous
frame's memo is correct today because export follows a paint; nothing enforces that ordering, and
both lenses said the guard is ordering luck rather than construction. I have made it visible and
argued for it; I have not made it structural, and I am not claiming otherwise.

---

# Review round 4 — the two mitigations from security confirmation 2

**Applied by the ORCHESTRATOR, not the implementer, and that is declared rather than blurred.** Both
fixes were specified to the character by the confirming lens and both had already been *measured* by
it (RED on the seams, GREEN on the shipped tree). After three implementation rounds, dispatching a
fourth agent for a one-operator change and a docstring would have been ceremony. The trade is
recorded so a reader can price it: nobody independent re-derived these two edits, and the C-40
discharge below is the orchestrator's own.

## R4-1 · `NEW-4` — the opener classifier accepted a name, not a call

`tests/test_search.py` — the openers guard was a **subset** check
(`{"refresh_canvas", "_declare_after_layout"} <= openers`). Two seams the confirming lens constructed
stayed **GREEN** through it, because the set was permitted to grow 2 → 3 unnoticed:

- **Seam B** — defer the opener via `call_after_refresh` and read the memo now. **This is the house
  idiom**, live at `mapper/app.py:1256` and `:1599`; not a contrivance.
- **Seam C** — name the opener inside a guard that never calls it.

Changed to an **exact-set** assertion. The arm exists to force `Inc-4b`'s keypress-bound consumer to
declare itself, and a subset check is exactly the form that lets it decline in silence.

**C-40 discharge, executed by the orchestrator on the real tree, Seam C reproduced:**

```
pre-mutation sha256 : cb4ba7d47288bb60...64410f94
baseline (unmutated): exit=0  1 passed          -> GREEN
mutation applied    : 6cf53a3bf138af1e...1fce5a8bae   (differs: True)
mutated             : exit=1  1 failed          -> RED
restored sha256     : cb4ba7d47288bb60...64410f94   identical=True
```

The applied-hash line is not decoration: a typo'd mutation also "fails", for the wrong reason, so the
transcript shows the mutation genuinely landed before the verdict is read. The mutated token is
described here by position and operation and is **never spelled** into this artifact (`C-56`).

## R4-2 · `NEW-5` — the silence was justified on a declaration that is not on screen

`mapper/app.py` — the docstring under the above-bound branch claimed the strip's own
`N fuera de vista` is what tells the operator why no count is painted. Measured by the lens: that text
**is** in the `Text`, but it renders at **row 42 of a 34-row terminal** — off-viewport — because the
reserved pagination meter prices one glyph per node (`per_page = max(1, total)`).

**The silence is correct; the reason written under it was false.** The operator is informed by the
**canvas** (`mapa de 12002 nodos: supera el límite de 12000 nodos…`), not by the strip. Docstring
corrected to name the real mechanism. **A justification that names the wrong mechanism is how a later
reader deletes the right one** — which is why this was worth a fix rather than a shrug.

The unbounded pagination meter (`per_page = max(1, total)`) is **pre-existing at `HEAD`** and is
**carried to `Inc-REPAIR`**, not repaired here.

## R4-3 · `NEW-6` — bookkeeping, corrected

The round-3 record labelled `b960f4eff37093c9` as the "round-2 exit" digest; it is the **round-3
post-repair** state. Round-2 entry was `a2b621256c22e533`, as this packet's own header already said.
Verdicts unaffected.

## Verification after the orchestrator's edits

```
822 passed, 17 deselected, 3 xfailed in 136.64s   exit 0   zero FAILED
ruff SET over mapper/ tests/ vs the entry pin     -> IDENTICAL (zero NEW, zero GONE)
source files: app.py search.py views/layered.py views/state.py   (4)
mapper/keymap.py: 0 lines
```

Ledger: base **804** default lane + **21** = **825** = 822 passed + 3 xfailed. ✓

## ⚠ Carry opened at round 4 — the operator's username is in the batch record, and sync ships it

The confirming lens flagged one occurrence at `:122`. **Executed, it is larger than reported: 13
occurrences across 10 files**, seven of them in **already-committed Inc-3 artifacts**.

```
01d-unpark-measurements.md · 02k-inc4-viewstate-architect.md
increment-003-code-review.md · -code-review-confirmation.md
increment-003-security-review.md · -security-confirmation.md · -security-pass3.md
increment-004a.md · increment-004a-security-review.md · -security-confirmation-2.md
```

**NOT scrubbed, and the reasoning is recorded rather than assumed.** They are absolute paths inside
executed evidence transcripts (`C:\Users\<user>\Github\mapper\…`). Rewriting them would (a) edit
**committed** records so they no longer say what was actually measured, and (b) damage the
reproducibility that makes the transcripts evidence at all. Neither is a trade the orchestrator may
make unilaterally on the operator's behalf.

**It is a real pre-sync consideration** because `/dev-flow-sync` pushes `.dev-flow/` to the vault, and
this repo already carries a username-path-leak defect routed to `Inc-REPAIR` — so the project's own
threat model treats the string as sensitive. The vault is the operator's own Drive, so this is
low-severity today and would matter if that vault is ever shared. **Routed to the operator as a
decision at the sync step, with the recommendation to leave the transcripts intact.**
