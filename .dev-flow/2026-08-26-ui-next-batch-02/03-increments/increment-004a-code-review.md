# Code Review — Increment 004a (`US-N07` search core)

| Field | Value |
|---|---|
| Reviewer | `code-reviewer` (independent; author does not self-clear) |
| Branch / entry | `feat/ui-next-batch-02` @ `5f4816c`, **nothing committed** |
| Scope reviewed | `git diff HEAD -- mapper/ tests/` + staged `tests/inc4_support.py`, `tests/test_search.py`. `.dev-flow/**` excluded by instruction |
| Source files | `mapper/search.py`, `mapper/views/state.py`, `mapper/views/layered.py`, `mapper/app.py` |
| **Verdict** | **BLOCK** — 2 HIGH |

---

## 0 · BLUF

**The shipped code is correct. Two things block it: the gate on this increment's headline
invariant does not gate it, and the increment puts a quadratic walk in the repaint path.**

The architecture is right and the story is closed properly — `mapper/search.py` really is the
single owner, `ViewState.query` really is gone, both consumers really did migrate, and the walk is
genuinely cycle-safe, forest-safe and orphan-safe. `TC-026b` is a **real** gate on the declared
behaviour change, verified independently. The blank-query guard is genuinely unreachable from every
surface.

But:

- **F1 (HIGH)** — the shared-resolution arm asserts "each named consumer mentions the helper", not
  "the helper is the only resolution". Probed against five variants: it reddens on the historical
  defect (replacement) and is **blind to a second path added alongside**, to a new consumer, and —
  measured, not hypothesised — to a count line that consumes `MapScreen.folded`, which
  `LLR-N07.2.1` forbids by name. That last mutant passes `AT-018`, `AT-019` **and** the structural
  arm simultaneously. Risk A-6 is not closed by the gate that says it is.
- **F2 (HIGH)** — `SearchIndex.query` is `O(N*E)`. Measured **4.05 s** per resolution at
  `MAX_RENDER_NODES`, against **0.144 s** for the entire frame render. Instrumented on the real
  pilot: **4 resolutions per fold keypress**. One `z` at the declared ceiling with a live query is
  a ~16 s freeze. A 3-line, output-identical fix is 274x faster.

Both fixes are small. Neither requires a redesign.

---

## 1 · Verified state (re-verified, not trusted)

| Claim | Result |
|---|---|
| Fast lane `-m "not slow"` | **813 passed, 17 deselected, 3 xfailed — exit 0, zero FAILED** ✓ |
| `mapper/keymap.py` untouched | 0 lines ✓ |
| Packet's **Block 1** (census red from two U+202E in `02l`) | **STALE — now GREEN.** Re-ran the census node: `1 passed`. The operator fixed it after the packet was written. The packet was honest at the time |
| Source digests unchanged across this review | all 7 files `OK` (sha256 identical, start to finish) |

---

## 2 · Findings

### F1 — The shared-resolution arm does not gate what it claims, and an `LLR-N07.2.1` violation survives the whole battery  [Severity: HIGH]

**Where:** `tests/test_search.py:459-501`; requirement at `01-requirements.md:2600-2607`.

**What.** The arm's predicate is **positive membership only**: for each of three named consumers it
asserts the helper's name appears among that method's `self.*` reads. It never asserts the helper is
the *only* resolution, and it applies its `folded` / `pan_x` / `pan_y` ban to `_search_order` alone.

I reproduced the arm's own `self_reads` and all seven of its asserts exactly, then evaluated it
against five candidate shapes of the count-line body:

| Variant (described by position and operation) | Arm |
|---|---|
| V0 — the tree as it stands | GREEN (correct) |
| V1 — count line resolves for itself, helper reference **removed** *(the historical defect, = the packet's M1b)* | **RED** |
| V2 — an independent resolution **added beside** the retained helper call | **GREEN** |
| V3 — V2, and the added path scoped to the viewport *(the A-6 defect)* | **GREEN** |
| V4 — helper stays pure; the **count line** narrows its result by the folded set | **GREEN** |
| V5 — a **new fourth consumer** resolves independently | never inspected (consumers are enumerated by name) |

**V4 is not hypothetical, and no behavioural arm catches it either.** Executed on both acceptance
fixtures: the folded branch id is not itself a hit in either case, so narrowing the count by the
folded set changes neither number.

```
AT-018  folded branch is a hit? False   count 8 -> 8   (unchanged)
AT-019  folded branch is a hit? False   count 1 -> 1   (unchanged)
```

So a count computation that consumes `MapScreen.folded` — which `LLR-N07.2.1`'s **Touched symbols**
forbids in as many words ("must not consume `MapScreen.folded`") — passes `AT-018`, `AT-019` and the
structural arm at once. The LLR governs "the count computation in `mapper/app.py::MapScreen`", which
is **both** `_search_order` and `_count_line`; the arm bans viewport state in only one of them.

**Why it matters.** This arm is the single gate on the increment's headline claim and on the risk
the author reports nearly shipping. Its docstring says it shows the two surfaces "**could not have**"
disagreed, "for a deeper reason than 'both happen to call the same function today'." The predicate
establishes exactly "both happen to call the same function today" and nothing more. That is a test
asserting a strength it does not have, on risk A-6 — and `Inc-4b` adds a fourth consumer next, which
is the one shape the arm is structurally blind to.

**Suggested fix** (all three; the technique is already in this tree at `tests/test_layered.py:196-212`):

1. Extend the viewport ban to the whole count computation, per the LLR's own wording:
   ```python
   for method in (MapScreen._count_line, MapScreen._view_state):
       reads = self_reads(method)
       assert "folded" not in reads and "pan_x" not in reads and "pan_y" not in reads, reads
   ```
2. Make uniqueness structural rather than nominal — an AST census over `mapper/app.py` asserting the
   owner is constructed in exactly one place, so a second path is a red regardless of which method
   grows it and regardless of whether the first is retained:
   ```python
   src = pathlib.Path(inspect.getfile(MapScreen)).read_text(encoding="utf-8")
   sites = [n.lineno for n in ast.walk(ast.parse(src))
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id == "SearchIndex"]
   assert len(sites) == 1, f"a second resolution appeared at {sites}"
   ```
   (Executed against the tree as it stands: exactly 1 site, `app.py:1829`. The census passes today.)
3. Correct the docstring's "could not have" to what the predicate proves, or leave it once (2) makes
   it true.

---

### F2 — `SearchIndex.query` puts an `O(N*E)` walk in the repaint path; 4 resolutions per fold, 4 s each at the declared ceiling  [Severity: HIGH]

**Where:** `mapper/search.py:60` (`children_of` called per node inside the walk) and
`mapper/search.py:93-94` (the tail comprehension rebuilds a set on every iteration).

```python
# search.py:93-94 -- set(walked) is re-evaluated once PER NODE
return walked + [nid for nid in self.graph.nodes
                 if nid in found and nid not in set(walked)]
```

`Graph.children_of` (`model.py:149-150`) is a linear scan of `graph.edges`, so calling it per node
makes `tree_order` quadratic.

**Measured** (`PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1`, synthetic graph, half the nodes matching):

| nodes | `SearchIndex.query` | `SearchIndex.hits` alone | whole `LayeredRenderer.render` |
|---|---|---|---|
| 3 000 | 0.199 s | 0.002 s | 0.049 s |
| 6 000 | 0.793 s | 0.004 s | 0.079 s |
| **12 000** (`MAX_RENDER_NODES`) | **4.033 s** | 0.009 s | **0.144 s** |

The ordering layer costs **450x the matching it orders**, and **28x the entire frame render**. The
repaint path was *not* already quadratic — this increment made it so. At entry, nothing on
`MapScreen` called `SearchIndex` at all and the renderer used an inline `O(N)` predicate.

**Resolutions per keystroke**, instrumented on a real pilot by counting calls to the helper:

```
cursor move (j) : 0
fold        (z) : 4
pan         (L) : 1
```

One `z` with a live query on a graph at the declared ceiling is **~16 s of frozen UI**.

**The declared open item mis-frames the trigger, which is why it was under-measured.** The packet
lists "per-keystroke cost of `_search_order` unmeasured". There is no per-keystroke path: search
commits on `Input.Submitted` (`app.py:2132-2138`). The cost is **per repaint**, and `_declare_after_layout`
(`app.py:1567-1592`) resolves twice per pass while re-scheduling itself until the region settles.

**Suggested fix** — 3 lines, behaviour-identical. Build the child index once inside `tree_order`
instead of calling `children_of` per node, and hoist the set out of the comprehension in `query`:

```python
# tree_order: replace the per-node children_of call
index: dict[str, list[str]] = {}
for e in graph.edges:
    index.setdefault(e.parent_id, []).append(e.child_id)
...
    for cid in reversed(index.get(nid, ())):

# query: hoist
seen = set(walked)
return walked + [nid for nid in self.graph.nodes if nid in found and nid not in seen]
```

Verified: output **identical** at every size tested (`shipped == fixed` asserted), and

| nodes | shipped | fixed | speedup |
|---|---|---|---|
| 3 000 | 0.199 s | 0.0032 s | 62x |
| 6 000 | 0.793 s | 0.0067 s | 119x |
| 12 000 | 3.743 s | 0.0137 s | **274x** |

Since this is output-identical, the existing suite is its own regression gate. Consider also caching
the resolution per `(query_text, graph)` for the repaint pass, but the index fix alone removes the
problem.

---

### F3 — `tree_order` duplicates `MapScreen._incomplete_order`, and nothing pins that they agree  [Severity: MEDIUM]

**Where:** `mapper/search.py:49-63` vs `mapper/app.py:2210-2225`.

The two walks are structurally identical: same root seed, same `nid in seen or nid not in graph.nodes`
guard, same `reversed(children_of(nid))` push, same visited set. Only the filter line differs.

The docstring justifies the copy by rejecting a `search -> app` import ("importing a screen into the
search owner would put the app's event loop inside a headless module"). That is correct but argues
against the wrong direction: **`app.py` already imports `search`** (`app.py:42`), so the available
move is `_incomplete_order` consuming `tree_order(self.graph)` and filtering the result. That is a
strict simplification, creates no new edge, and needs no new abstraction.

**Why it matters.** The docstring itself states the reason the two must agree — that "next match"
and "next missing field" mean the same "next" to the operator. Two hand-maintained copies of a walk
that must agree, with no predicate pinning agreement, is the case where duplication is *not* cheaper
than reuse. This is normally a "three similar lines beat an abstraction" call; it is not, because the
abstraction already exists and only one caller is using it.

**Suggested fix:**
```python
# app.py::MapScreen._incomplete_order
return [nid for nid in tree_order(self.graph)
        if self.graph.nodes[nid].ficha.missing_required(self.graph.schema)]
```
This also inherits F2's fix for free, and removes ~14 lines.

---

### F4 — The `n` numeral is painted and gated by nothing  [Severity: MEDIUM]

**Where:** `mapper/app.py:1727` paints `at`; census over `tests/`.

`group(2)` (the whole-graph total) is asserted at `test_search.py:272`, `:361`, `:430`.
`group(1)` is read at exactly one place, `:447`, and only for the no-hit **bare** `0` form.
`AT-018:272` computes `group(1)` and **discards it** — every call site takes `numerals()[1]`
(`:282`, `:292`, `:310`, `:319`).

So the first numeral of `n/N` has **zero coverage anywhere in the suite**. Any value ships green.
That is the "unobserved behaviour on a green suite" this batch says it is spending its budget to
stop, and `_count_line`'s own docstring argues against "reserving a placeholder numeral that would be
a lie until the walk arrives" while shipping one.

**On the declared open item.** `0/N` is fixture-dependent, not universal: on the `adjuntos` fixture a
fresh screen reads **`1/5`**, because the root matches by id. On a map whose root is not a hit it
reads `0/N`.

**Assessment: shippable at this boundary, but only with a gate.** `0` for "no match selected" is an
honest reading and I would not block on the UX. I do object to shipping it undefended. Three lines
make the contract falsifiable now and give `Inc-4b`'s walk something to land against:

```python
# n is 0 exactly when the cursor is not itself a hit, and its place otherwise
order = SearchIndex(screen.graph).query(QUERY)
n, _N = numerals()
assert n == (order.index(screen.nav.cursor) + 1 if screen.nav.cursor in order else 0)
```

Without it, `Inc-4b` will change `n` with no predicate recording what it was.

---

### F5 — The declared un-writable mutation is honestly reported; one residue is closable  [Severity: LOW]

**Assessment: a real structural limit, not a gap dressed as one.** `AT-052` derives `COUNT_RE` from
`SEARCH_COUNT_SUBJECT`, so mutating the constant moves both sides together, and writing the wording
into the test would be exactly the second copy of the declaration the single-declaration rule exists
to prevent. The author is right, and right to record it rather than repair it by pretending.

**The residue.** The test constrains the constant's *wiring* but never its *shape*. A constant
degraded to a single token would still bind a numeral to a subject and still satisfy every arm,
shipping a line reading `5/5 x` — while the requirement's own words are that the line declares
*which question it answers*. One arm closes it without copying the wording:

```python
assert len(SEARCH_COUNT_SUBJECT.split()) >= 3, SEARCH_COUNT_SUBJECT
```

I did **not** execute this mutation (see §4), so this is reasoned, not measured.

---

### F6 — `COUNT_REGION_ID`'s comment overclaims  [Severity: LOW]

`mapper/app.py:66` states "Predicates read this name; nobody re-types it." `tests/test_overflow.py`
re-types the literal at 7 sites (`:546`, `:614`, `:678`, `:888`, `:945`, `:1024`, `:1035`). The
packet's B1 row reports these accurately, so the *packet* is honest; only the source comment is
wrong. Either route the 7 through the constant or soften the comment to "new predicates read this
name".

---

### F7 — `mapper/search.py` is LF while neighbours are CRLF  [Severity: LOW]

Author-declared. Git warns on every touch. Normalise before commit; not a gate.

---

## 3 · Answers to the specific questions asked

**1 · Is the count whole-graph and provably independent of `MapScreen.folded`?**
In the **shipped code**, yes: `_search_order` reads only `graph` and `query_text` and delegates to a
module importing no Textual and no `views`. The **proof** is incomplete — see F1.

**2 · The tree-order walk on forests, orphans, diamonds and cycles.**
**Correct, no regression.** Iterative stack with an explicit `seen` set, so no recursion and no
`RecursionError` at file-declared depth; `seen` admits each node once, so a cycle terminates and a
diamond is not duplicated; `nid not in graph.nodes` guards a dangling edge. Forests and orphans are
handled by `query`'s tail clause. The documented `len(query(q)) == len(hits(q))` invariant **holds
for every graph**: `search_hits` appends `node.id` while iterating `nodes.values()`, and `add_node`
keys by `node.id` (`model.py:141-142`), so `found` is always a subset of `graph.nodes`. The only
defect in the walk is its cost (F2).

**3 · Is the blank guard's match-everything genuinely unreachable?**
**Yes.** `SearchIndex.hits` guards; `query` routes through `hits`; `_count_line` carries an
independent guard. Both guards have their own mutation in the battery (M3, M4), and the unit arm
asserts the non-trivial pre-state (6/6 for empty, 4/6 for whitespace) rather than describing it. This
is well done.

**4 · The near-miss fix — real or cosmetic?**
**Real, but incomplete.** There *is* exactly one resolution path today (`SearchIndex` constructed at
exactly one site, `app.py:1829`), and the restructure genuinely fixed the code. The gate closes the
*replacement* shape that bit the author and leaves the *additive* shape, the *downstream-narrowing*
shape and the *new-consumer* shape open. See F1.

**5 · `TC-026b` — genuine gate or passes on a re-narrowed implementation?**
**Genuine gate. Verified independently.** Measured on the fixture:

| branch | descendants | narrow tail | wide tail | moves? |
|---|---|---|---|---|
| `b` | 2 | 1 | 2 | yes |
| `riesgo-root` | 5 | 2 | 4 | yes |
| `c` | 1 | 0 | 0 | no — correctly excluded from the loop |

The test asserts `expected != was` **before** asserting `tail == expected`, so a re-narrowed
implementation produces `was`, which is provably not `expected`, and reddens. The declared
`+2 1 -> +2 2` and `+5 2 -> +5 4` match my measurement exactly. The vacuous branch is correctly kept
out of the loop.

**6 · Convention conformance.** Clean. Titles-never-ids respected (`_hit_image` reads spans, ids
travel as data through `painted_ids`). Region rows joined before parsing (`count_region_text`, with
the height-1 measurement recorded and the join kept anyway). Pilot tests assert the configuration
they requested (`assert_declared_layout`). 118x34 declared, and `AT-052` correctly runs a second size
where the rail leaves. Docstring density matches the codebase.

---

## 4 · What I could not verify — stated, not glossed

- **I could not run the author's mutation battery.** The harness auto-mode classifier blocked every
  file edit to the repo, so I could not apply and restore mutations. I selected two and verified
  them by means that require no mutation: the structural arm by reproducing its own `self_reads` and
  all seven asserts and evaluating them against candidate function bodies (exact, since the arm is
  pure AST over source); `TC-026b` by computing the fixture arithmetic its assertions rest on. Both
  are sound for what they claim. Neither exercises the pytest subprocess the author used.
- **M2, M3, M5, M7, M9-M13 were not independently reproduced.** Accepted on the packet's evidence.
  The packet's digest table matches the digests I measured on the tree, which is consistent with a
  clean restore.
- **`PYTHONDONTWRITEBYTECODE` was not set during the author's battery** (declared). All of my own
  measurements were taken with it set.
- **Ruff was not re-run** by me; the entry/exit identity is accepted from the brief.
- No file was mutated during this review; all 7 digests verified identical at start and finish.

---

## 5 · Evidence checklist

- [x] **Diff read in full** — `mapper/search.py:1-95`, `mapper/views/state.py:19-91`,
      `mapper/views/layered.py:110-601`, `mapper/app.py:39-1922`, plus all 5 test files.
- [x] **Correctness pass** — cycles/diamonds/forests/orphans traced; `len(query) == len(hits)`
      invariant proven via `model.py:141-142`; blank guard proven unreachable.
- [x] **Simplicity pass** — one premature-duplication finding (F3, `search.py:49-63` vs
      `app.py:2210-2225`). No speculative abstraction found; every symbol traces to an approved LLR.
- [x] **Reuse / duplication checked** — F3; `SearchIndex` construction census: 1 site.
- [x] **Tests reviewed for intent** — F1 (arm weaker than its docstring), F4 (`n` ungated),
      F5 (declared limit assessed and upheld). `TC-026b`, `AT-020`, `AT-021`, `LLR-N07.3.3`
      confirmed as real gates with real counterfactuals.
- [x] **Performance measured** — F2, at three graph sizes plus pilot call counts.
- [x] **Verdict explicit** — below.

---

## 6 · Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **BLOCK — must fix HIGH findings before advancing**

**Blocking: F1 and F2.** Both have a stated minimal fix; neither is a redesign. F2's fix is
output-identical, so the existing suite gates it. F1's fix is roughly ten lines of predicate using a
technique already present in this tree.

**Strongly recommended in the same pass:** F3 (falls out of F2's fix and deletes code) and F4
(three lines, and it stops `Inc-4b` from moving an undefended numeral).

**Credit where due.** The `search.py` module docstring, the `state.py` removal-is-not-the-symmetric-case
paragraph, the `AT-020` derived-coverage arm, the `LLR-N07.3.1` self-guard, and the honest reporting
of the un-writable mutation are all above the bar this repo sets. F1 is a gap in one predicate, not
in the thinking.
