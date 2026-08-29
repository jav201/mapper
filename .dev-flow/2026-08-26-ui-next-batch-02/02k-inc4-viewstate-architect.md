# 02k · Inc-4 architect ruling — `ViewState.query` removal, and the fold pill's hit count

**Batch:** `2026-08-26-ui-next-batch-02` (SEALED) · **Branch:** `feat/ui-next-batch-02` · **Base:** `5f4816c`, clean
**Lens:** architect · **Scope:** ruling only. Nothing under `mapper/` or `tests/` was edited.
**Instrument:** a `--local --no-hardlinks` clone at `5f4816c` in the session scratchpad. The repo tree was
read-only throughout; every mutation below happened in the mirror.

**Mirror fidelity, executed before any change** — the instrument reproduces the declared baseline exactly:

```
$ cd <scratch>/mirror && PYTHONUTF8=1 python -m pytest -q
801 passed, 17 deselected, 3 xfailed in 141.36s (0:02:21)
```

---

## BLUF

**Q1 — A3 does NOT fire. The batch does not stop. Remove `query` in Inc-4.**
The A3's subject is the `IRenderer.render` **signature**, and that signature is byte-identical across the
change. The A3's mechanical enforcement — `tests/test_a3_census.py`, 15 arms — is **15/15 green after the
removal**. The roster arm pins a *property* (every field defaulted), not membership. The standing
pre-authorization is **not consumed**, because it authorises *extending* `render` and no extension occurs.
Executed break set across the whole suite: **exactly one test, at exactly one line** —
`tests/test_app.py:448`. Retain-and-deprecate is rejected on measurement, not preference: the three Inc-5
renderers read `selected_id`, `w`, `h` and **nothing else**, so a retained `query` would be retained for
zero consumers while reproducing Inc-2's own declared "two contracts live at once" defect.

**Q2 — `len(_descendants(index, nid) & state.hits)` is correct, AND it is an undeclared, unobserved
behaviour change. It needs a §6.5 amendment.**
Executed on one fixture, same graph, same query: the pill tail moves **`+4 1` → `+4 4`**. The C-26 reverse
census returns **zero** tests that pin it — both `_PILL` regexes capture only the `+(\d+)` hidden count, and
**no test in the tree renders with a live query at all**. Root cause found: **`TC-026`'s second clause
("hit count when a query is live") exists only as a row in the §5 traceability matrix and is implemented
nowhere in `tests/`.** The change would therefore ship silently on a green suite. Owner: a **new
`LLR-N07.1.3`** under `HLR-N07.1`; `HLR-N06.2` supplies the painted form and must be cross-referenced.

---

## 1 · Executed evidence

### P1 — `state.query`: the true reader/writer census (re-derived, not trusted)

```
$ grep -rn '\.query\b' mapper/ tests/ --include=*.py
mapper/views/layered.py:491:        query, diff = state.query, state.diff
tests/test_app.py:448:    assert seen["state"].query == "hij", "the export dropped the active query"
tests/test_attachments.py:418:            s.render().plain for s in inspector.query(".insp-att-target")
tests/test_inspector.py:125:            for s in inspector.query(".insp-label")
tests/test_inspector.py:154:                for s in inspector.query(".insp-label")
```

The last three are Textual `DOMNode.query`, not the field. The single **writer** is `mapper/app.py:1769`
(`query=self.query_text,` inside `MapScreen._view_state`).

> **Correction to the brief.** The pre-brief named one reader, one writer and the declaration. There is a
> **fourth** site: `tests/test_app.py:448` reads the field. It is the sole causal break (§1.5) and the
> brief's plan must budget for it.

### P2 — the `qlower` idiom: 9 hits, not 4 (spec pre-state is decayed)

```
$ grep -rn 'qlower' mapper/views/
mapper/views/layered.py:113:def _matches(node: Node, qlower: str) -> bool:
mapper/views/layered.py:116:    return bool(qlower) and (
mapper/views/layered.py:117:        qlower in node.ficha.title.lower()
mapper/views/layered.py:118:        or qlower in node.ficha.notes.lower()
mapper/views/layered.py:119:        or any(qlower in v.lower() for v in node.ficha.fields.values())
mapper/views/layered.py:530:        qlower = query.lower()
mapper/views/layered.py:535:            hit = _matches(node, qlower)
mapper/views/layered.py:600:                if _matches(graph.nodes[cid], qlower)
mapper/views/layered.py:601:            ) if qlower else 0
```

`HLR-N07.1` records a pre-state of **4 hits at `144,146,147,148`**. Executed: **9 hits**, none at those
lines, and the predicate is no longer inline — Inc-2/Inc-3 extracted it to a module-level `_matches` at
`:113-120`. `grep -rn 'qlower'` over the rest of the repo returns nothing, so **no test names the idiom**.

### P3 — the A3 census does not inspect roster membership

`tests/test_a3_census.py` gates on six properties, all read directly:

| Arm | What it pins | Touched by removing `query`? |
|---|---|---|
| `…_every_definition_takes_graph_and_state` (`:192`) | `render` args `== ["self","graph","state"]` | no |
| `…_no_definition_keeps_kwargs_or_the_explicit_query` (`:208`) | no `**kwargs`; no stale **parameter** named `query` | no — `query` is a `ViewState` field, not a `render` parameter |
| `…_zero_call_sites_of_the_old_shape_survive` (`:225`) | no `render(...)` **call** passes `query=` | no |
| `…_view_state_constructs_with_no_arguments` (`:299`) | **every field has a default** — a property, not a roster | no; preserved |
| `…_view_state_is_frozen` (`:319`) | `FrozenInstanceError` | no |
| `…_every_renderer_signature_equals_graph_and_state` (`:347`) | `inspect.signature` | no |

The roster arm is the only one that touches `dataclasses.fields(ViewState)` (`:312`), and it asks
`f.default is MISSING`, never `f.name`.

### P4 — the decisive experiment: the census after removal

Applied in the mirror: `query` removed from `ViewState`, `hits: frozenset[str] = frozenset()` added;
`_matches` deleted; `hit = nid in hits_set`; pill tail `= len(_descendants(index, nid) & hits_set)`;
`app.py` writer rebuilt on `Graph.search_hits`.

```
$ grep -rn 'qlower' mapper/views/ --include=*.py
[exit 1 -> zero occurrences]          # HLR-N07.1's numeric threshold: MET

$ PYTHONUTF8=1 python -m pytest tests/test_a3_census.py -q
15 passed in 1.26s
```

**Not one A3 arm fires.**

### P5 — the frozen artifact is byte-identical

```
--- tree: C:/Users/jjgh8/Github/mapper   (baseline 5f4816c)
  IRenderer.render : (self, graph: 'Graph', state: 'ViewState') -> 'Text'
  Layered.render   : (self, graph: 'Graph', state: 'ViewState') -> 'Text'
  ViewState roster : ['selected_id','w','h','focus_owner','query','diff','pan_x','pan_y','folded']
  isinstance guard : True
--- tree: <scratch>/mirror              (query removed)
  IRenderer.render : (self, graph: 'Graph', state: 'ViewState') -> 'Text'
  Layered.render   : (self, graph: 'Graph', state: 'ViewState') -> 'Text'
  ViewState roster : ['selected_id','w','h','focus_owner','hits','diff','pan_x','pan_y','folded']
  isinstance guard : True
```

The counterfactual is non-trivial and visible: the rosters **differ**, the signature does **not**.
(An earlier version of this probe `cd`-ed with a colon-split variable, silently read the same tree twice
and printed two identical blocks. It was discarded and re-run. Recorded because a probe that constructs
the world it observes is exactly what this batch bans.)

### P6 — the full break set is one test at one line

```
$ PYTHONUTF8=1 python -m pytest -q                    # patched mirror
FAILED tests/test_app.py::test_llr_cnv_3_1_the_parent_walk_maps_a_nested_widget_to_its_region
FAILED tests/test_app.py::test_b50_the_export_carries_the_diff_the_canvas_is_showing
2 failed, 799 passed, 17 deselected, 3 xfailed
```

The second failure is a **cascade**, not a coupling — proved two ways:

```
$ pytest "tests/test_app.py::test_llr_cnv_3_1_…" -q      -> 1 passed
$ pytest tests/test_app.py -q                            -> 1 failed, 12 passed   (only b50)
$ pytest -q --deselect ".../test_b50_…"                  -> 800 passed, 18 deselected, 3 xfailed
```

With `b50` deselected the **entire suite is green**. The causal break is
`tests/test_app.py:448`: `assert seen["state"].query == "hij"` → `AttributeError`.

### P7 — the two rival definitions, measured

`_matches` (`layered.py:113-119`) matches **title, notes, field values** — 3 haystacks.
`Graph.search_hits` (`model.py:224-236`) matches **id, title, meta, notes, field values, attachment
caption-or-path** — 6. `Ficha.meta` is declared `# short subtitle / status line` (`model.py:30`), so the
spec's "subtitle" is `meta`. The delta is exactly `{id, meta, attachments}`.

```
narrow (_matches)          : ['a']
wide   (Graph.search_hits) : ['a', 'b', 'd', 'zeta-node']
DELTA                      : ['b', 'd', 'zeta-node']    # by meta, by attachment, by id
```

### P8 — the pill tail changes, executed on one fixture

Same graph, same query `"zeta"`, root folded, `+4` hidden either way:

```
baseline (inline predicate) : '▐ ▸ Raiz +4 1'      hidden +N: 4   hit tail: 1
patched  (resolved hits)    : '▐ ▸ Raiz +4 4'      hidden +N: 4   hit tail: 4
counterfactual, no query    : tail = None           (the tail is query-driven, not a constant)
```

### P9 — C-26 reverse census: nothing pins the tail

```
$ grep -rn '_PILL' tests/
tests/test_fold.py:37:_PILL = re.compile(re.escape(FOLD_PILL_TOKEN) + r"\s*(.*?)\s*\+(\d+)")
tests/test_fold.py:47:    return [int(m.group(2)) for m in _PILL.finditer(" ".join(rows))]
tests/test_overflow.py:80:_PILL = re.compile(re.escape(FOLD_PILL_TOKEN) + r".*?\+(\d+)")
tests/test_overflow.py:972:    counts = [int(m.group(1)) for m in _PILL.finditer(...)]
```

Both regexes stop at `+(\d+)`. Neither has a group for the tail. Stronger still:

```
$ grep -rn 'ViewState(' tests/ mapper/ --include=*.py | grep query
[no output -> zero ViewState constructions pass query=]

$ grep -rn 'query_text' tests/
tests/test_app.py:433:        screen.query_text = "hij"       # the export test
$ grep -c 'folded\|action_fold' tests/test_app.py
0
```

**No test in the tree renders a pill with a live query.** The tail is unreachable by the suite — which is
why P6 shows zero fold/overflow failures despite P8's change.

### P10 — root cause: `TC-026` was never implemented

```
$ grep -rn 'tc_026\|TC-026\|tc026' tests/ .dev-flow/2026-08-26-ui-next-batch-02/*.md
.dev-flow/…/01-requirements.md:5411:| HLR-N06.2 | test (pilot) | `TC-026` | pill numeral equals descendant count; hit count when a query is live |
```

One hit, and it is the matrix row itself. `TC-026` exists in `tests/` **nowhere**. Its first clause is
covered incidentally by the `_PILL` `+N` arms; its second clause — *"hit count when a query is live"* —
is uncovered. This is a live Inc-3 coverage gap that Inc-4 inherits, not a defect Inc-4 creates.

### P11 — `mapper/search.py` is dead, confirmed over import nodes

Zero import statements naming it across `mapper/` and `tests/`; the only textual hit is a comment at
`tests/test_a3_census.py:383`. Its whole body is a 2-line delegation to `Graph.search_hits`
(`search.py:13-14`). It is a wrapper with no callers.

---

## 2 · Q1 — the ruling, limb by limb

### (a) Does A3 fire? **No.**

The A3's subject is named identically in both places it is recorded. `.dev-flow/state.json:314` authorises
*"Extending the frozen **IRenderer.render** contract"*; `docs/ARCHITECTURE.md:148` freezes
*"`render(graph, selected_id, w, h, **kwargs) -> Text`"*. Both name the **callable's signature**. P5 shows
that signature unchanged to the character. P4 shows the fifteen arms that mechanically enforce it all green.

The `state.py` docstring's silence on removal is real, and I decline to read the addition exemption as
covering removal by symmetry — **the two are not symmetric**. Adding a defaulted field cannot break a
reader; removing one breaks every reader. Removal is safe *here* because of a contingent, measured fact —
`query` has exactly one product reader (P1) and that reader is being rewritten by this very increment —
not because removals are exempt as a category. §4's amendment A-k4 records that distinction so the next
increment cannot cite this ruling as a general licence.

### (b) Is the pre-authorization consumed? **No — and it is not needed.**

Its trigger is *extending* `render` with viewport/fold state. No extension occurs: `render` keeps its two
parameters. The pre-authorization is left **unspent**. Its three obligations are therefore not owed;
however, its middle obligation — *record the frozen signature in `docs/ARCHITECTURE.md`* — has an
independent trigger here, because `ARCHITECTURE.md:159` enumerates the roster in prose and that prose
becomes false on removal. §4's A-k3 fixes it.

**The batch does not stop and does not return to the operator.** No sealed decision is disturbed:
`#D25`-`#D28`, the `#D5` increment cut and A-91 are untouched by a field rename inside an object whose
contract the census already governs.

One note the ruling should carry rather than bury: `ARCHITECTURE.md:159` is **already stale** independent
of this increment. It records the roster as `selected_id, w, h, focus_owner, query, diff` — six fields —
while the live roster is nine (P5). Inc-3 added `pan_x`, `pan_y`, `folded` under the additive rule and did
not update the row. That row also already promises this exact change: *"`query` is **transitional** and is
replaced by a resolved `hits` set in Inc-4."* The architecture record anticipates the removal.

### (c) Remove now, or retain-and-deprecate until Inc-5? **Remove now.**

Retention is killed by a direct measurement:

```
$ for f in mapper/views/outline.py mapper/views/radial.py mapper/views/lane.py; do grep -n 'state\.' $f; done
outline.py:49:        selected_id, h = state.selected_id, state.h
radial.py:109:        selected_id, w, h = state.selected_id, state.w, state.h
lane.py:110/167:       selected_id, w, h = state.selected_id, state.w, state.h
lane.py:301:           selected_id, h = state.selected_id, state.h
```

**None of the three Inc-5 renderers reads `state.query`.** Retaining the field "until Inc-5 migrates them"
retains it for consumers that do not exist and never did. `LLR-N07.2.2b`'s observation that those views do
not paint hits yet is confirmed here from the other side: they do not read the input either, so when Inc-5
teaches them to paint hits it will reach for `state.hits`, not for a field kept alive on its behalf.

And retention **does** reproduce Inc-2's declared defect. `test_llr_n07_2_2a_zero_call_sites_of_the_old_shape_survive`
exists because *"the migration half-lands and two contracts are live at once"* (`:230`). Two fields both
answering "what matches", disagreeing by `{id, meta, attachments}` (P7), with nothing forcing agreement, is
that defect in a new location — and the census provably cannot catch it, since P4 shows no arm inspects
roster membership in either direction.

---

## 3 · Rejected candidates, each killed by a measurement

| # | Candidate | The measurement that killed it |
|---|---|---|
| **C-1** | **A3 fires; stop the batch and return to the operator.** | P4: `pytest tests/test_a3_census.py` → **15 passed** on the removed tree. The A3's own mechanical enforcement declines to fire. P5: the frozen signature is byte-identical. A stop would be justified by prose against an executed instrument that contradicts it. |
| **C-2** | **A3 fires but the pre-authorization covers it; proceed under its three obligations.** | `.dev-flow/state.json:314` scopes the authorisation to *"**Extending** the frozen IRenderer.render contract with viewport/fold state"*. P5 shows no extension: two parameters before, two after. Spending an authorisation on an event outside its trigger would leave the batch believing a one-way door had been used when it had not. |
| **C-3** | **Retain `query`, deprecate it, migrate in Inc-5.** | P19: `grep -n 'state\.' ` over `outline.py`, `radial.py`, `lane.py` returns only `selected_id`, `w`, `h`. Zero readers of `state.query` outside `layered.py`. The field would be retained for nobody, while re-creating the "two contracts live at once" defect (`test_a3_census.py:230`) that the census cannot detect. |
| **C-4** | **Keep `_matches` as the resolver, feeding it from `hits`.** | P2: `_matches` is the *narrow* definition (3 haystacks vs `search_hits`' 6, P7). Keeping it keeps `HLR-N07.1`'s numeric threshold at **9**, not 0 — the requirement's pass condition is literally the absence of these tokens. Measured directly: `grep -rn qlower mapper/views/` must exit 1, and it does only when `_matches` is gone (P4). |
| **C-5** | **Delete the dead `mapper/search.py` in the same increment, since `LLR-N07.1.2` names it the owner.** | P11: zero import nodes — deleting it is free, which is exactly why it is *not* Inc-4's business. `LLR-N07.1.2` names `SearchIndex.query` as the owner, but `search.py:13-14` is a 2-line delegation to `Graph.search_hits`, so the real owner is already `model.py:224`. Touching it widens Inc-4 past its cut for zero behavioural gain. Recorded as a finding, deferred; see §5. |

---

## 4 · Recommended §6.5 amendments

Form follows the existing amendment set (`A-01`…): Before / After / Deleted tokens / New tokens / Evidence /
Parent-HLR re-read. Numbered `A-k1`… to avoid colliding with the sealed sequence; the requirements owner
renumbers on merge.

### A-k1 · `HLR-N07.1`'s pre-state is re-executed (the cited 4 hits are decayed)

- **Before:** *"**Pre-state executed at draft:** `grep -n "qlower" mapper/views/layered.py` returns **4
  hits** at lines `144`, `146`, `147`, `148`, with the `hit` binding at `:145` and its only consumer at
  `:159`."*
- **After:** *"**Pre-state re-executed at `5f4816c`:** `grep -rn "qlower" mapper/views/` returns **9 hits**
  — the predicate at `layered.py:113-119` (extracted to a module-level `_matches` by Inc-2/Inc-3, no longer
  inline), the `qlower` binding at `:530`, and **two** consumers: the card highlight at `:535` and the fold
  pill's hit-count tail at `:598-601`. The threshold is unchanged at **0**; the pre-state is **9**, not 4."*
- **Deleted tokens:** `144`, `145`, `146`, `147`, `148`, `159`, *"its only consumer"*.
- **New tokens:** `113`, `119`, `530`, `535`, `598`, `601`, `_matches`, *"two consumers"*.
- **Evidence, executed:** P2 above.
- **Parent-HLR re-read:** `US-N07` re-read; unaffected. The threshold (**0**) is the normative half and does
  not move — only the counterfactual magnitude does, from 4 to 9, which strengthens it.

### A-k2 · `LLR-N07.1.1`'s Touched-symbols line gains the second consumer

- **Before:** *"the `qlower` binding at `layered.py:144`, the `hit` expression at `:145-148` and the `query`
  parameter at `:83` are **deleted**"*
- **After:** *"the module-level predicate `mapper/views/layered.py::_matches` (`:113-120`) is **deleted**;
  the `qlower` binding at `:530` is **deleted**; the card-highlight consumer at `:535` becomes
  `hit = nid in state.hits`; **the fold pill's hit-count tail at `:598-601` — `HLR-N06.2`'s surface, added
  by Inc-3 after this spec was sealed — becomes `len(_descendants(index, nid) & state.hits)`**; and the
  `ViewState.query` field (`state.py:70`) is **deleted**. `mapper/views/state.py::ViewState.hits` —
  `NEW — created in Phase 3`. **Also migrated: `mapper/app.py::MapScreen._view_state` (`app.py:1769`), the
  field's single writer, and `tests/test_app.py:448`, its single test reader.**"*
- **Deleted tokens:** `:144`, `:145-148`, `:83`.
- **New tokens:** `_matches`, `:113-120`, `:530`, `:535`, `:598-601`, `_descendants`, `state.hits`,
  `app.py:1769`, `tests/test_app.py:448`.
- **Evidence, executed:** P1, P2, P6.
- **Parent-HLR re-read:** `HLR-N07.1` re-read in full; no change beyond A-k1. Its statement
  (*"renderers … shall not evaluate any query predicate"*) already covers the pill consumer — the pill was
  evaluating one. The omission was in the LLR's symbol list, not in the HLR's contract.

### A-k3 · `docs/ARCHITECTURE.md:159` roster prose is refreshed

- **Before:** *"Initial roster: `selected_id`, `w`, `h`, `focus_owner`, `query`, `diff`"*
- **After:** *"Initial roster (Inc-2): `selected_id`, `w`, `h`, `focus_owner`, `query`, `diff`. Roster at
  Inc-4: `selected_id`, `w`, `h`, `focus_owner`, `hits`, `diff`, `pan_x`, `pan_y`, `folded` — `pan_x`,
  `pan_y`, `folded` added additively in Inc-3; `query` **removed** in Inc-4 and replaced by `hits`, with
  `IRenderer.render`'s signature unchanged and `tests/test_a3_census.py` green throughout (15/15)."*
- **Deleted tokens:** none (the initial roster stays readable, per D20). **New tokens:** `hits`, `pan_x`,
  `pan_y`, `folded`, `Inc-3`, `Inc-4`.
- **Evidence, executed:** P5 (both rosters derived via `dataclasses.fields`), P4.
- **Note:** this row is **already stale at `5f4816c`**, by three fields, independent of Inc-4. The row's own
  sentence *"`query` is transitional and is replaced by a resolved `hits` set in Inc-4"* is discharged here.

### A-k4 · The `state.py` docstring's silence on removal is closed

- **Before:** *"ADDING A DEFAULTED FIELD BELOW IS ADDITIVE AND NEVER RE-OPENS THE A3."* (silent on removal)
- **After:** append: *"**REMOVING A FIELD IS NOT THE SYMMETRIC CASE AND IS NOT EXEMPT BY CATEGORY.** An
  addition cannot break a reader; a removal breaks every one. A field may be removed without re-opening the
  A3 only when its product readers are enumerated and migrated in the same increment — the A3's subject is
  `IRenderer.render`'s signature, which a roster change does not touch (asserted by
  `tests/test_a3_census.py`, which pins that every field is defaulted, never which fields exist). `query`
  was removed in Inc-4 under exactly that condition: one product reader (`layered.py:491`), one writer
  (`app.py:1769`), one test reader (`test_app.py:448`)."*
- **Deleted tokens:** none. **New tokens:** the paragraph above.
- **Evidence, executed:** P1, P3, P4, P5.
- **Rationale:** without this, the next increment cites Inc-4 as precedent for removing a field with many
  readers, and the census stays green while a consumer breaks at runtime.

### A-k5 · **NEW `LLR-N07.1.3`** — the fold pill's hit count is a declared consumer of the widening

> `LLR-N07.1.2` declares the widening user-visible; nothing in the sealed spec says the **fold pill's
> hidden-hit count** is one of the surfaces that widens. It is, and by a large factor (P8).

- **Traceability:** `HLR-N07.1`, `HLR-N06.2`, risk A-3
- **Statement:** The fold pill's trailing hit count shall equal the number of the folded branch's
  descendants that are members of the view state's resolved hit set, and shall be absent when that
  intersection is empty.
- **Touched symbols:** `mapper/views/layered.py::LayeredRenderer.render` — the pill hit-count expression at
  `:598-601`, rewritten to `len(_descendants(index, nid) & state.hits)`.
- **Validation:** `test (unit)`
- **Numeric pass threshold — executed pre-state:** one graph, root folded over four descendants matching
  the query by notes, by `meta`, by id and by attachment caption respectively. Under the shipped inline
  predicate the pill paints **`▐ ▸ Raiz +4 1`**; under the resolved wide hit set it paints
  **`▐ ▸ Raiz +4 4`**. The hidden count `+4` is invariant, so the arm isolates the tail. With an empty hit
  set the tail is **absent** — the counterfactual that proves the tail is query-driven and not a constant.
- **Acceptance criteria:** the `+N` hidden count and the hit tail are asserted **separately**. An arm that
  reads only `+N` is green under both definitions — proved: both shipped `_PILL` regexes
  (`test_fold.py:37`, `test_overflow.py:80`) capture only `+(\d+)` and the full suite stayed green across
  the change (P6, P9).
- **Named weaker variant (`M-N07.1.3-a`):** assert the tail on a fixture whose descendants match by
  `title`/`notes` only. Green under both the narrow and the wide definition, because the delta is exactly
  `{id, meta, attachments}` (P7) — the fixture must place a match in each of those three.

### A-k6 · `TC-026`'s live-query clause is recorded as UNIMPLEMENTED and re-homed

- **Before:** §5 row — *"| `HLR-N06.2` | test (pilot) | `TC-026` | pill numeral equals descendant count;
  hit count when a query is live |"*, with no implementation.
- **After:** the row is split. The `+N` clause stays with `HLR-N06.2` and is satisfied by the existing
  `_PILL` arms. **The "hit count when a query is live" clause is re-homed to the new `LLR-N07.1.3` and
  carried as a NEW test case `TC-026b`**, with the row annotated *"second clause **UNIMPLEMENTED at
  `5f4816c`** — `grep -rn 'TC-026' tests/` returns no hit; discovered by the Inc-4 architect ruling."*
- **Deleted tokens:** none. **New tokens:** `TC-026b`, `LLR-N07.1.3`.
- **Evidence, executed:** P10.
- **Why it matters:** this is the reason the behaviour change of P8 is invisible. Without `TC-026b`, Inc-4
  ships a changed user-visible number on a fully green suite.

### A-k7 · `LLR-N07.1.2`'s `search_hits` citation is re-executed

- **Before:** *"`mapper/model.py::Graph.search_hits` (`model.py:169-184`)"*
- **After:** *"`mapper/model.py::Graph.search_hits` (**`model.py:224-236`**)"*
- **Deleted tokens:** `169-184`. **New tokens:** `224-236`.
- **Evidence, executed:** P7. The joined haystacks are confirmed as declared — `node.id`, `ficha.title`,
  `ficha.meta`, `ficha.notes`, the field values, and each attachment's `caption or path`.

---

## 5 · Findings recorded, deliberately NOT actioned in Inc-4

- **`mapper/search.py` is dead code** (P11): zero import nodes, a 2-line delegation to
  `Graph.search_hits`. `LLR-N07.1.2` names it the owner of matching; the executed owner is `model.py:224`.
  Deleting it is safe and free, and it is **out of Inc-4's cut**. Recommend a one-line Inc-5 task, or a
  batch-close cleanup, with `LLR-N07.1.2`'s owner citation re-pointed to `Graph.search_hits` at that time.
  Flagged rather than fixed because widening an increment past its cut is how a clean gate goes soft.
- **`ARCHITECTURE.md:159` is stale by three fields at baseline** (P5), independent of this increment. A-k3
  repairs it as a side effect; if A-k3 is rejected, the staleness still needs an owner.

---

## 6 · What I could not determine

- **Whether `PDR-addendum-3.md` narrows the pre-authorization further.** `grep` for
  `pre-author|preauthor|Extending the frozen` across `PDR-2026-08-26-ui-next-batch-02.md` and
  `PDR-addendum-3.md` returned **no hits**; the only copy of the authorization text in the tree is
  `.dev-flow/state.json:314`. My §2(b) ruling rests on that single source. If a narrower or broader wording
  exists in a document I did not parse, limb (b) should be re-checked against it.
- **Whether the *card highlight* widening (as opposed to the pill tail) is pinned anywhere.** P6 shows no
  test failed, and P9 shows no test renders with a live query — so the highlight is equally unobserved. I
  did not write a separate census for it because the same two probes cover both consumers, but I have not
  proved the absence with a highlight-specific instrument.
- **Runtime cost of the widening.** `Graph.search_hits` builds a joined string per node per query. At the
  batch's fixture sizes this is invisible, and I did not measure it against `MAX_RENDER_NODES`-scale graphs.
  If Inc-4 calls it on every keystroke via `on_input_changed` (`app.py:2054`), that is worth a probe I did
  not run.

---

## 7 · Evidence checklist

| Item | | Evidence |
|---|---|---|
| Constraints stated explicitly | ✓ | Sealed batch, `#D25`-`#D28`/`#D5`/A-91 out of scope; read-only on `mapper/` and `tests/`; one artifact file; ruling not implementation. |
| At least 2 alternatives considered | ✓ | Five rejected candidates, §3, each with its killing measurement. |
| Recommendation tied to constraints | ✓ | §2(a)-(c): removal ruled in on P4 (census green) + P6 (one-line break set), not on preference. |
| Risks listed | ✓ | Silent behaviour change (P8/P9/P10 → A-k5, A-k6); removal-precedent misuse (→ A-k4); stale architecture record (→ A-k3); dead `search.py` (§5); unmeasured per-keystroke cost (§6). |
| Cost / latency estimated where relevant | ✗ | Not estimated. `search_hits` per-keystroke cost is named as undetermined in §6 rather than hand-waved. |
| Diagram included when flow is non-trivial | ✗ | Not warranted. The flow is one field on one dataclass with two consumers; the tables in §1 and §3 carry it without a diagram. |
| What would change the recommendation | ✓ | §2(a): if `query` gained a second product reader, removal leaves the "enumerate and migrate in the same increment" condition and A-k4's rule bites. §6: a narrower pre-authorization wording would re-open limb (b). §3 C-3: if an Inc-5 renderer *did* read `state.query`, retain-and-deprecate would revive. |
| Two-layer traceability | ✓ | Behavioural `US-N07 → AT-020/AT-021 → widened hit painted`; functional `US-N07 → HLR-N07.1 → LLR-N07.1.1/.2/.3 → TC-034/035/036 + TC-026b`. A-k5 creates the missing `LLR-N07.1.3`; A-k6 creates the missing `TC-026b`, closing the gap P10 found. |

**Verdict:** proceed with Inc-4 as cut. `query` is removed, `hits` replaces it, `_matches` is deleted, and
**both** consumers migrate — the card highlight and the fold pill's tail. A3 does not fire; the
pre-authorization stays unspent. The one non-negotiable addition to the increment is `TC-026b` (A-k5/A-k6):
without it the pill's number changes for every existing fixture on a green suite, which is the failure mode
this batch has paid the most to eliminate.
