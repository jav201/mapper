# Increment 003 — independent gate review

| Field | Value |
|---|---|
| Batch | `2026-08-26-repair-batch` |
| Increment | `003` — `HLR-R03` (S-02) + A-2 + A-3 + A-9 |
| Reviewer | `code-reviewer`, independent of the author |
| Date | 2026-08-27 |
| Packet under review | `03-increments/increment-003.md` |
| **Verdict** | **BLOCKED** — one HIGH (`F1`), four MEDIUM, six LOW |

---

## 0 · BLUF

**The implementation is correct and the packet's headline numbers all reproduce. It is blocked on
one thing: `Graph.resolve_document`'s parent-chain walk is dead computation, and the node the packet
cites as A-3's positive control cannot fail if you delete that walk entirely.**

Measured, not argued: `resolve_document` is a constant function of the graph-level `Document` — in
the rewrite **and on `master`** — so `TC-R22` (6 depths), `TC-R22b`, `TC-R23`'s value assertion and
`AT-R17`'s value assertion all stay **GREEN** against an implementation with the `chain`, the `seen`
set and the fold removed. `TC-R22` appears in **zero of the 18 battery arms**, including `M10`, the
arm that restores the exact implementation `TC-R22` compares itself against. Gate checklist item 3
cites `TC-R22` as the Layer-0 evidence for A-3. It is not evidence of anything.

The same dead walk is the sole reason **Risk 4** exists. The `seen` set guards a loop whose result is
discarded; delete the loop and the hang mode, arm `M12`, and pending item 1 all disappear together.

Everything else is recommendation. The evidence discipline in this packet is otherwise the strongest
in the batch — `M13`'s discovery of the `LLR-R03.4` hole, `M17`'s refuse-after-write arm and `M4`'s
inversion of A-7's own premise are all real, all reproduced below, and all correctly reported.

---

## 1 · What I established independently, and how

Nothing in this section was taken from the packet.

| # | Claim | How I checked it | Result |
|---|---|---|---|
| 1 | suite 409 passed | `PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:randomly -o addopts=` | **409 passed in 69.00s, exit 0** ✓ |
| 2 | lane split 393 / 16 | `--collect-only` both ways | **393 selected, 16 deselected** · **409 collected** ✓ |
| 3 | per-file 48 / 25 / 91 | `--collect-only` per file | **48 · 25 · 91** ✓ |
| 4 | ruff = 29 | `python -m ruff check mapper tests` | **29 errors** ✓ |
| 5 | ledger `409 = 356 − 1 + 54` | `A = 48 + 5 + 1 = 54`; `409 − 54 + 1 = 356` | arithmetic ✓; **base 356 accepted on the packet's word**, corroborated by `PLAN.md` §9's independent Inc-2b record |
| 6 | `resolve_document` ≡ constant | fuzz vs. a constant implementation, 400 random graphs | **2565 comparisons, 0 mismatches** — see `F1` |
| 7 | A-3 nodes are inert | monkeypatched `Graph.resolve_document` to the constant, ran the 9 node-verdicts in-process | **9/9 GREEN** — see `F1` |
| 8 | `TC-R32` excludes `resolve_document` | ran `_structural_graph_members()` and `graph_touching_methods()` directly | **census 35**, `resolve_document` absent from both ✓ Risk 4's exclusion is real |
| 9 | A-2 refuses before writing | read `store.py:285-295` — `find_cycle()` precedes `dump`, `_build_sidecar` and both `_atomic_write` calls | ✓ `TC-R28`'s subject is real |
| 10 | `darkside.plain` at both sinks | read `app.py:459-464` and `app.py:1146-1159` | ✓ both, **and** `markup=False` at both — but see `F3` |
| 11 | A-7's premise measured wrong | read `model.py:246-261` (`search_hits` does not join `state`) and `tests/test_inspector.py:85-108` | ✓ **the packet's §6 item 3 admission is accurate and correctly scoped** |
| 12 | `TC-R15` catches single-member loss | recomputed the test's own two sides against three degraded sets | **reddens on all three** — the packet **understates** this, see `F4` |
| 13 | sibling malformed shapes | drove 5 hand-edited sidecar shapes through `MapStore.load` | **4 of 5 still deny the map**, see `F2` |
| 14 | A-2's message injection surface | built a CSV with ANSI + rich markup in the id column, through `preview_csv` → `save` | ids are slugged upstream; **not exploitable**, see `F11` |

**Accepted on the packet's word** (stated so the distinction is explicit): base **356**; the
per-arm RED counts in the §4 matrix (I spot-verified `M10`, `M11`, `M12`, `M13`, `M14` against the
transcript and they match); the byte-scan table; wall-clock figures.

### Mutation protocol compliance

**I mutated no file.** Findings `F1`, `F4` and `F12` were established by in-process monkeypatching and
by re-running the derivations directly, which is strictly stronger evidence than a disk mutation and
carries no restore risk. All probe fixtures were written to `tempfile.mkdtemp()` outside the repo.

Verifying hashes, taken at the end of the review — **byte-identical to the pristine values**:

```
7f50f2481ae199633bc4bfbe8762e83fc6e8b113c8047fd9be803420c080e25d  mapper/store.py
d1cb6160d4b1f3e57fefc30a5b27174054dc373a4b801aa2fcfe9b29c487706a  mapper/model.py
fae8e89df917c3240818a3be1894632883077856db8aeaae05953f49592af7bf  mapper/app.py
33848fd38761640aed27f3ebc5a4c4860726800fbe7b1e401efade7f8dfa0bea  tests/test_repair_fields.py
52773d5fb3676de4b88a2627b8db448f3f675c60fc02b5a0d4b98b76c27a51ba  tests/test_repair_cycles.py
16a6892aca8cd2d87783911857d083785c738879f727648555f7f208d89a4b49  tests/test_repair_depth.py
```

`prototypes/**` untouched. Nothing committed, stashed, checked out or reset.

---

## 2 · Findings

### F1 — A-3's traversal is dead computation, and every node certifying it is inert · **HIGH**

**Where:** `mapper/model.py:104-161` · `tests/test_repair_fields.py:519-571`

**What.** `resolve_document` reads `doc = self.documents.get(name)` **once**, outside the walk.
`documents` is graph-level and keyed by name — there is no per-node document store — so every
iteration of the fold computes `level_tags = dict(doc.tags)` from the *same* object. After the first
iteration `key not in level_tags` is therefore false for every key, and the merge adds nothing at any
depth. The function returns `Document(tags=dict(doc.tags), inherited=dict(doc.inherited), …)` for
every input.

`master`'s recursion has the identical property: `parent_doc` is built from the same graph-level
`doc`, so `key not in merged_tags` is false at every level. **The rewrite faithfully preserves a
no-op.**

Measured — fuzz against a constant implementation over 400 random graphs:

```
comparisons 2565   mismatches 0
```

**Why it matters.** Three consequences, and the third is the blocking one.

1. **`TC-R22` cannot fail for any traversal defect.** Both sides of `mine == theirs` are the same
   constant function, so the equivalence holds for every graph shape, at every depth, under any
   mutation of `chain`, `seen`, the fold, or the fold's order. Measured — with the entire walk,
   `seen` set and fold **deleted** and replaced by the constant:

   ```
   TC-R22 depth 1..120   GREEN (6/6)
   TC-R22b               GREEN
   TC-R23                GREEN
   AT-R17                GREEN
   ```

   Nine node-verdicts, zero RED, against the most aggressive possible mutation of the thing they
   exist to certify.

2. **The battery already recorded this and no one read it.** `TC-R22` appears **nowhere** in the
   389-line transcript — it reddened under none of the 18 arms. `M10` is the proof: it restores the
   shipped recursion, i.e. exactly the implementation `_shipped_resolve` is a verbatim copy of, and
   its 4 RED verdicts are `AT-R16b`, `TC-R29`, `AT-R17` and `TC-R23` — reddening on *stack
   exhaustion*, not on disagreement. The arm that should be `TC-R22`'s canonical trigger does not
   touch it.

   Gate checklist item 3 nonetheless lists `TC-R22` as *"A-3 equivalence against a verbatim copy of
   the shipped recursion, 6 depths"* — a Layer-0 positive control. **This is C-40 limb 1 in the
   increment whose §1 congratulates itself for finding C-40 limb 1 elsewhere:** the declared subject
   (the rewrite agrees with the original about inheritance) never varies in the predicate's own
   expression.

3. **Risk 4's hang is self-inflicted.** The `seen` set guards a loop whose result is discarded.
   Delete the walk and `M12`, the 15-second timeout, the "CI does not fail — it stops" disclosure and
   §6 pending item 1 all cease to exist. The packet treats an uncatchable regression mode as a cost
   of the repair; it is a cost of retaining dead code.

**Suggested fix** — pick one, `A` preferred:

**(A) Delete the dead walk.** This is the simplest, removes Risk 4 outright, and keeps `TC-R29` /
`AT-R16b` / `AT-R17` green (a constant return contains no recursion and no unbounded loop):

```python
def resolve_document(self, name: str, node: Node) -> Document:
    """Return the named document.  Inheritance is graph-level (A-3).

    Documents are keyed by name on the Graph, not per node, so every level of a
    parent chain resolves the same object and the shipped recursion's downward
    merge was provably a no-op — measured, 2565 comparisons, 0 mismatches
    against this form.  Walking the chain to reproduce a no-op is what made a
    depth-5000 map raise RecursionError; not walking it is the repair.
    """
    doc = self.documents.get(name)
    if doc is None:
        return Document(name=name, source="")
    return dataclasses.replace(doc, tags=dict(doc.tags), inherited=dict(doc.inherited))
```

Then **retarget `TC-R22`** at what is now the real claim — equivalence to the shipped recursion for
every graph, which this form still satisfies — and keep `_shipped_resolve` as the oracle, but add a
depth to the parametrization at which the *shipped* one would have died so the node's own subject is
visible. Keep `TC-R23` (it still pins termination) and note in its docstring that it asserts
termination only.

**(B) If per-node document inheritance is intended future behaviour**, say so, and make `TC-R22`
discriminating *now* by giving the fixture per-level tags that actually differ, so the fold has
something to fold. Do not leave a fold that folds one value.

**Either way, `TC-R22`'s docstring must stop claiming to be a positive control until an arm reddens
it.** Add that arm to the battery and record its RED count.

---

### F2 — the non-`dict` guard is hand-bounded to `fields`; four sibling shapes still deny the map · **MEDIUM**

**Where:** `mapper/store.py:227-232`

**What.** `LLR-R03.5`'s guard covers `fields` not being a `dict`. It does not cover the same
malformation one level up or one level down. Measured, through `MapStore.load`:

```
node entry is a string      DENIED   AttributeError: 'str' object has no attribute 'get'
node entry is a list        DENIED   AttributeError: 'list' object has no attribute 'get'
nodes block is a list       DENIED   AttributeError: 'list' object has no attribute 'items'
attachments non-list        DENIED   TypeError: string indices must be integers
attachment missing 'kind'   DENIED   KeyError: 'kind'
```

All five are shapes `_build_sidecar` cannot emit and a human editing `_nodos.yml` can — which is
verbatim `TC-R18`'s own justification for guarding the one that is guarded.

**Why it matters.** This is the batch's signature defect, and the batch has now recorded it four
times: A-1 (the sink set), A-5 (the empty census), A-6 (the traversal root), A-7 (the text-attribute
set). Each time a set was bounded by hand inside a requirement and the omitted member was the live
one. `LLR-R03.5` is satisfied *as written* — a malformed **field** does not deny the map — so this is
not a spec violation, and none of the five is a regression (`master` denies all five identically).
But the packet declares no risk for it, and a reader of `TC-R18` would reasonably conclude the loader
is robust against hand-edited sidecars. §6 item 6 disclaims `F-M5` in general terms; it does not say
that four concrete sibling shapes were measured and left.

**Suggested fix.** Either three lines beside the existing guard —

```python
if not isinstance(ndata, dict):
    graph.load_warnings.append(f"campo ilegible: {nid}")
    ndata = {}
```

— or, if that is out of fence, **declare it**: add a risk naming the four measured shapes so the next
reader inherits the measurement rather than the impression.

---

### F3 — `markup=False` is the whole markup defense at both new sinks, and no node pins it · **MEDIUM**

**Where:** `mapper/app.py:1155-1159`, `mapper/app.py:460-464` · `tests/test_repair_fields.py:369, 389, 409`

**What.** `darkside.plain()` strips control bytes (`_CONTROL_MAP`, `darkside.py:272-273`) but
**deliberately does not escape rich markup** — its own docstring says so, and
`test_darkside.py:119-120` pins that: *"Markup is preserved LITERALLY: safety comes from never using
a markup sink."* `Textual.App.notify` defaults to `markup=True` (verified against textual 8.2.8).
So `markup=False` is the entire markup defense at the two sinks this increment created.

All three notice nodes stub the sink with

```python
app.notify = lambda msg, **kw: notices.append(str(msg))
```

which **discards the kwargs**. Drop `markup=False` from either sink and nothing in the tree reddens.
`M15` does not cover it either — it mutates the message content, not the call's keywords. `node_id`
and `key` are file-derived and flow into that string, so this is the one security-relevant property
of the new surface and it is unarmed.

**Why it matters.** Increment 1's finding `F2` was accepted as a condition for exactly this shape —
*"the code is correct today; nothing stops a future narrowing"* — and increment 4 re-opens `app.py`,
so it would inherit an unarmed guard, which is the reason `F2` was required to be closed *before*
increment 3 landed.

**Suggested fix.** Capture the kwargs in one of the three nodes and assert the security-relevant
ones, plus drive a markup-bearing node id:

```python
calls: list[tuple[str, dict]] = []
app.notify = lambda msg, **kw: calls.append((str(msg), kw))
...
msg, kw = next(c for c in calls if "campo ilegible" in c[0])
assert kw["markup"] is False, "the only markup defense at this sink is unasserted"
assert kw["severity"] == "warning"
```

Add the corresponding battery arm (drop `markup=False`) and record its RED count.

---

### F4 — the packet misdescribes `TC-R15`'s own coverage, in both directions · **MEDIUM**

**Where:** packet §5 Risk 2 and §6 pending item 2 vs. `tests/test_repair_fields.py:55-66`

**What.** Pending item 2 states: *"Nothing currently reddens if exactly one attribute leaves the
derived set while three remain. A census asserting the derived set equals the annotated set by name —
rather than by count — would close it; the node already computes both sides."*

The node does not merely compute both sides. Line 61 **asserts** `derived == expected`. Measured
against three degraded derivations:

```
M4: hand-listed to what breaks today  -> RED on: derived==expected, len>=4, state in derived
drop exactly one member (notes)       -> RED on: derived==expected, len>=4
collapse to empty                     -> RED on: derived==expected, len>=4, state in derived
```

The by-name census the packet files as future work is already shipped, and it reddens on
single-member loss. Risk 2's claim that *"`TC-R15`'s `>= 4` floor catches a collapse, not the loss of
a single member"* is also wrong — with exactly four `str` attributes, the floor catches that too.

**The real residual hole is different and undeclared.** Both sides use the *same* predicate
`f.type in ("str", str)`, so an annotation change shrinks both simultaneously and `derived ==
expected` holds. Today the `len >= 4` floor catches it only because exactly four `str` fields exist;
add a fifth text attribute **and** change one to `str | None` and the node stays green with a member
silently dropped from the coercion set — which per `M4` means it is never passed to the `Ficha`
constructor and reverts to its default.

**Why it matters.** This packet's value is the accuracy of its self-disclosure; that is the standard
it holds increment 2b to. A pending item proposing work that is already done, sitting next to an
undeclared hole of a different shape, inverts that.

**Suggested fix.** Rewrite Risk 2 and pending item 2 to name the actual residual: *the derivation and
its oracle share a predicate, so an annotation-form change is invisible to both; only the `>= 4`
floor stands, and it stands only while `Ficha` has exactly four `str` attributes.* If you want to
close it, assert the floor against the count of *all* `Ficha` fields whose annotation mentions `str`
in any form.

---

### F5 — `TC-R22` and `TC-R23` collide with the ids increment 4 owns · **MEDIUM**

**Where:** `tests/test_repair_fields.py:520, 542` vs. `01-requirements.md` §3 `LLR-R04.1` and §6 traceability

**What.** The requirements allocate `TC-R22` and `TC-R23` to `LLR-R04.1` (*"`#map-rail` shall declare
a width equal to `rail.RAIL_WIDTH`"*), and §6's traceability row for US-R04 reads
`TC-R22`, `TC-R23`. Increment 3 has taken both ids for unrelated subjects (`resolve_document`
equivalence and cyclic termination), and neither belongs to US-R04.

**Why it matters.** Increment 4 owns `LLR-R04.1` and will find its two declared ids already occupied
by nodes in another file testing another requirement. Per my scope-fence brief this is exactly the
class of thing I am to flag: **it makes increment 4 harder.** It also defeats the id-scanner
discipline D9 was written to establish — two subjects under one id is worse for a scanner than an
en-dash range.

**Suggested fix.** Renumber this increment's two nodes to unallocated ids (`TC-R33`, `TC-R34`) and
record the reallocation in §6's traceability table, or explicitly reassign `LLR-R04.1` to new ids in
the requirements before increment 4 starts. Do it now, while only three call sites exist.

---

### F6 — `AT-R15`'s docstring names a diamond; the fixture builds a fork · **LOW**

**Where:** `tests/test_repair_fields.py:454-470`

The docstring says *"A diamond is the shape most likely to be mistaken for a cycle"*; the graph is
`root→l`, `root→r` — one parent, two children. A diamond is a **converging** shape (two parents), and
convergence is the only thing that exercises `find_cycle`'s back-edge-vs-re-visit distinction. The
declared subject is not in the expression.

Mitigating, and why this is LOW not MEDIUM: the property **is** genuinely covered upstream by
increment 1 — `test_at_r03_an_acyclic_map_still_loads:412` and `test_at_r03b_a_diamond_is_not_called_a_cycle:429`
both assert `_diamond().find_cycle() is None`, and `AT-R03`'s docstring explicitly records that a
tree-only oracle is inert against the false-refusal arm. `M18`'s 20-node blast radius also confirms
the false-refusal price empirically.

**Suggested fix.** One line — change the docstring to say what it builds (*"a fork: the false-refusal
arm flags any node with more than one child"*) and cross-reference `AT-R03b` for the diamond.

---

### F7 — `_text_attributes()` recomputed once per node · **LOW**

`mapper/store.py:226` — the call sits inside the `for nid, ndata in nodes_data.items()` loop. It
scans `Ficha.__dataclass_fields__` on every node; on the 3000-node tree `AT-R05` renders, that is
3000 redundant scans. Hoist it above the loop. Trivial, but it is inside a loop for no reason.

### F8 — `TC-R16b` asserts the standard library, and no node drives a real `datetime` · **LOW**

`tests/test_repair_fields.py:112-113` assert `date(2026,8,26).isoformat() == "2026-08-26"` and the
`datetime` equivalent. These are assertions about CPython, not about `mapper`; they can never redden
from a change to the diff. Harmless, but they are vacuous checks in the batch's own vocabulary sitting
inside the node that pins determinism. Separately, `store.py:53`'s `datetime` branch is never driven
through the loader — only `date` is. A YAML `D: 2026-08-26 07:05:00` would cover it.

### F9 — `str` in `("str", str)` is unreachable · **LOW**

`mapper/store.py:31` and `tests/test_repair_fields.py:59`. `model.py` opens with
`from __future__ import annotations`, so `__dataclass_fields__[…].type` is **always** the annotation
source string; the `str` member of the tuple can never match. Defensive but dead — and it slightly
obscures Risk 2, whose whole point is that the derivation is string matching on source text.

### F10 — two spelling nits · **LOW**

- `mapper/store.py:288-289` — double blank line inside `save`. Not caught because the project uses
  ruff's default rule set (no `[tool.ruff]` section in `pyproject.toml`), which excludes `E303`.
- `tests/test_repair_fields.py:533` — `assert compared == depth >= 1` is a chained comparison. It
  does what is intended (`compared == depth and depth >= 1`) but reads as a typo. Split it.

### F11 — hand-off to `security-reviewer`, not a finding against this diff · **LOW**

A-2's refusal message interpolates node ids into `MapStoreError`, and that exception reaches
`_ImportPreviewScreen.action_save`'s handler at `mapper/app.py:758`:

```python
self.notify(f"no se pudo guardar: {e}", severity="error")
```

— **no `darkside.plain()`, and `markup` defaults to `True`.** That sink is pre-existing and byte-identical
to `master`, but A-2 is what routes new file-derived text into it.

**Not exploitable today, measured.** `preview_csv` slugs node ids before they reach the graph:

```
csv id column: "\x1b[31mred[bold]x"  ->  node id: "31mred-bold-x"
refusal message: 'el mapa tiene un ciclo: 31mred-bold-x→b→31mred-bold-x'
```

So the defense is an upstream slugger in another module that nothing in `tests/` pins to this
property. Fold it into the C-17 sweep increment 2b already queued for the other 11 `escape(...)`
sites, alongside `F3`.

**Also noted in passing, and out of this increment's scope:** `CYCLE_ARROW` is `chr(0x2192)` with no
surrounding spaces, so the shipped message reads `a→b→a` while `LLR-R01.3` specifies the path *"joined
by `" → "`"*. Neither `TC-R07` nor `TC-R27` pins the separator. Increment 1's deviation; increment 3
is merely its second consumer via A-2's *"the same Spanish message"*. Worth a one-line correction to
`LLR-R01.3` at batch close.

---

## 3 · What holds up, stated explicitly

Per my brief's instruction not to invent issues: the following were attacked and did not break.

- **`_coerce_field`'s discrimination is right.** Scalar/container split is correct; `None → ""`;
  `bool` before the `date` branch is safe (`date` is not an `int` subclass); the `str({})`-is-truthy
  reasoning in D3 is sound and `TC-R17`'s `{}` row is the correct discriminating input.
- **`test_coverage_never_counts_an_unreadable_field_as_documented` is the strongest node in the
  increment.** Ten rows, both polarities, `0` separating readable-from-truthy and `"   "` isolating
  A-9. It has a real single-input blast radius under `M8`, which is the correct size for that defect.
- **A-9 is a genuine find and correctly fixed.** `required_coverage` delegating to `missing_required`
  is the right direction (the duplicate was the drifting copy, and the docstring that claimed sole
  ownership was the one being contradicted). Risk 5 correctly declares the behavioural change to
  `screens/coverage.py` and `widgets/inspector.py`.
- **A-2 refuses before writing.** Verified by reading, not by trusting `TC-R28`: `find_cycle()` at
  `store.py:285` precedes `dump`, `_build_sidecar` and both `_atomic_write` calls. `M17`'s reading is
  correct — `TC-R27` alone would not have caught a refuse-after-write.
- **`TC-R20`/`TC-R20b`/`TC-R20c` are three distinct assertions, not three spellings of one.** Two
  different sinks (`MapScreen`, `HomeScreen`, matching `LLR-R03.4`'s two named screens) plus one
  discriminating negative. `M13` and `M14` redden one each, which is what makes them independent.
  The coverage hole the battery found was real and is genuinely closed — subject to `F3`.
- **Risk 4's census exclusion is real.** I ran the derivation: 35 methods, `resolve_document` in
  neither `_structural_graph_members()` nor `graph_touching_methods()`. It is doubly excluded, in
  fact — `TRAVERSAL_FILES` is only `rail.py` and `factory.py`, so no `Graph` method could be censused
  regardless of the discriminator. The packet's account is true as far as it goes.
- **§6 item 3's honesty check passes.** `search_hits` (`model.py:251-258`) does not join `state`, and
  `test_inspector.py:85-108` does persist it through the store. A-7's stated premise was wrong, the
  conclusion is stronger than the argument, and the packet says so unprompted. Credit where due.
- **D12's deletion is correctly executed.** `DEFERRED_BY_AMENDMENT_A3` is gone, not emptied; the
  successor is named in a comment at `test_repair_depth.py:402-407`; `TC-R29` now asserts
  `== set()` subtracting nothing.
- **Frozen-interface fence held.** `IRenderer.render` and `Canvas` appear nowhere in the three source
  files. No S-07/S-08 work leaked in.
- **`AT-R17`'s `sys.getrecursionlimit() <= 1500` guard** is the right instinct and is in the node
  itself. The packet correctly discloses that it does not survive a *local* limit raise, which is
  what `M11` measured.

---

## 4 · Conditions

Each is individually dischargeable. `C1` is the blocker.

| # | Condition | Discharges |
|---|---|---|
| **C1** | **Resolve the dead walk in `resolve_document` (fix A or B in `F1`), and make `TC-R22` reddenable — with a battery arm that actually reddens it and its RED count recorded.** Until then, remove `TC-R22` from gate checklist item 3's evidence list. | `F1` HIGH |
| C2 | Guard the non-`dict` node entry, **or** declare the four measured sibling shapes as a risk | `F2` |
| C3 | Assert `markup=False` at one of the three notice nodes; add the drop-`markup` battery arm | `F3` |
| C4 | Correct Risk 2 and pending item 2 to the actual residual hole | `F4` |
| C5 | Renumber `TC-R22`/`TC-R23`, or reassign `LLR-R04.1`'s ids, before increment 4 starts | `F5` |
| C6 | Apply the LOW nits `F6`–`F10` at the author's discretion; hand `F11` to `security-reviewer` | `F6`–`F11` |

If `C1` is discharged via fix **A**, note that **Risk 4 and §6 pending item 1 should be deleted, not
carried** — they describe a hazard that fix A removes.

---

## 5 · Evidence checklist

| Item | ✓/✗ | Evidence |
|---|:--:|---|
| Diff read in full | ✓ | `store.py:1-398`, `model.py:1-262`, `app.py:440-474` + `1140-1189`, `test_repair_fields.py:1-572`, `test_repair_cycles.py:257-300`, `test_repair_depth.py:395-420, 505-530, 1240-1262, 1425-1500` |
| Correctness pass (edge / None / error paths) | ✓ | `F1` (dead fold), `F2` (5 malformed shapes measured), `F9` (unreachable branch); `_coerce_field` type-ladder verified sound |
| Simplicity pass (no premature abstraction) | ✓ | `F1` — 35 lines equivalent to 6; `F7` — hoistable call in a loop |
| Reuse / duplication checked | ✓ | A-9's duplicate predicate correctly collapsed into `missing_required`; `_shipped_resolve` duplicates `master` deliberately as an oracle (correct pattern, inert subject — `F1`) |
| Tests reviewed for intent, not behaviour | ✓ | 18 named oracles attacked; `TC-R22`/`TC-R22b` found inert (`F1`), `TC-R16b` partly inert (`F8`), `AT-R15` mislabelled (`F6`), `markup` unasserted (`F3`) |
| Suite / lanes / ruff / ledger re-derived | ✓ | §1 rows 1–5, all reproduced; base 356 accepted with corroboration |
| Security lens over the diff | ✓ | both new sinks scrubbed and `markup=False` ✓; `F3` (unpinned) and `F11` (third sink, unexploitable — measured) |
| Scope fence checked | ✓ | frozen interfaces absent; `F5` flagged as making increment 4 harder |
| Tree left byte-identical | ✓ | six sha256 values in §1, all pristine; no file written |
| Verdict explicit | ✓ | **BLOCKED** on `F1` |
