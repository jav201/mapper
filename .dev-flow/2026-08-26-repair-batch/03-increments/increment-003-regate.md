# Increment 003 — independent RE-GATE of the post-fix tree

| Field | Value |
|---|---|
| Batch | `2026-08-26-repair-batch` |
| Increment | `003` — `HLR-R03` (S-02) + A-2 + A-3 + A-9 |
| Reviewer | `code-reviewer`, independent of the author and of the first pass |
| Date | 2026-08-27 |
| Under re-gate | `03-increments/increment-003.md` **revision 2** |
| First pass | `03-increments/increment-003-review.md` — **BLOCKED**, left sealed and unedited |
| **Verdict** | **PASS** — zero HIGH · three MEDIUM · three LOW, all recommendations |

---

## 0 · BLUF

**`C1`, the HIGH, is genuinely discharged — measured, not read. The walk is gone from
`resolve_document`, `TC-R35` is a real gate with a working positive control, and I reproduced
arm `M12` myself: exactly one RED verdict, `TC-R35`, with 409 green. Nothing found in this pass
rises to HIGH, so the increment advances.**

All six conditions are addressed and every headline number reproduces on this machine: **410
passed exit 0**, ruff **29** on the gate metric, per-file **49 / 25 / 91**, ledger arithmetic
sound, and the transcript's three pinned hashes equal to `sha256sum` of the three source files
as they sit on disk right now. The evidence-integrity incident is repaired correctly and
disclosed adequately.

Three MEDIUM findings, none of them a correctness defect in shipped code:

- **`G1`** — the increment created **three** new `notify` sinks, not two. `C3` armed two of
  them. The third (`app.py:456`) carries `markup=False` over file-derived text and **no node
  asserts it**; I dropped the keyword and the suite stayed at **410 passed, 0 RED**. This is
  `F3`'s exact shape at a sink `C3` did not reach.
- **`G2`** — `TC-R35`'s docstring claims a walk "of any kind, recursive or iterative" reddens
  it. Measured false: a fold that derives the parent by scanning the edge list inline instead
  of through `Graph.parent_of` leaves it **green**, 410 passed, 0 RED. The gate is real and
  correctly scoped to `Graph.parent_of`; the docstring asserts a breadth it does not have.
- **`G3`** — §4's default-lane row still reads `393 / 16` from revision 1's 409-node tree. It
  is `394 / 16`. §0's universal claim that every §4 number comes from the re-run is falsified
  by that one row.

I did not find a reason to withhold the gate. The response to the first review is substantive:
fix A was taken rather than the cheaper fix B, the hazard it dissolves was deleted rather than
carried, and the battery was re-run in full instead of patched.

---

## 1 · What I established independently

Nothing below is taken from the packet or from the first review.

| # | Claim | How I checked it | Result |
|---|---|---|---|
| 1 | suite 410 | `PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:randomly -o addopts=` | **410 passed in 102.12s, exit 0** ✓ |
| 2 | default lane 394 / 16 | `pytest -p no:randomly --collect-only -q` | **394/410 collected, 16 deselected** — packet says 393, see `G3` ✗ |
| 3 | per-file 49 / 25 / 91 | `--collect-only -q` per file | **49 · 25 · 91** ✓ |
| 4 | ruff 29 / 57 | `python -m ruff check mapper tests`; `ruff check .` | **29** and **57** ✓ |
| 5 | ledger `410 = 356 − 1 + 55` | `A = 49 + 5 + 1 = 55`; `410 − 55 + 1 = 356` | arithmetic ✓; base **356** accepted on the packet's word, as the first pass did |
| 6 | transcript hashes = disk | `sha256sum mapper/store.py mapper/model.py mapper/app.py` vs. the transcript's final block | **all three equal** ✓ — `1b1b9e2b…`, `3d39a861…`, `fae8e89d…` |
| 7 | the walk is gone | `git diff -- mapper/model.py` | ✓ `parent_of`, the chain and the fold are all absent from `resolve_document` |
| 8 | `M12` reddens `TC-R35` | **ran it myself** on a copy outside the repo | **1 RED — `test_tc_r35_…`; 409 passed.** Matches the transcript exactly ✓ |
| 9 | the third sink is unarmed | **arm N1** (mine) | **410 passed, 0 RED** — see `G1` |
| 10 | `TC-R35`'s breadth claim | **arm N2** (mine) | **410 passed, 0 RED** — see `G2` |
| 11 | `TC-R15` shares a predicate with its oracle | read `test_repair_fields.py:44-64` against `store.py:28-32` | ✓ both sides are `… in ("str", str)` — the rewritten Risk 2 is accurate |
| 12 | no `TC-R22`/`TC-R23` in test code | `grep` across `tests/` | ✓ zero hits; ids free for `LLR-R04.1` |
| 13 | store.py's revision-2 delta is inert | compared all **eight** `store.py` arm RED counts, v1 vs v2 | **28·13·3·10·8·1·8·2·1·20 — identical in both runs** ✓ the `F10`-only claim is corroborated by execution, not by the author's word |
| 14 | the two `markup` assertions are the only ones in the tree | `grep -rn markup tests/` | ✓ only `test_repair_fields.py:385` and `:428` |

### Mutation protocol compliance

Three arms were run. **Every one on a copy at
`…/scratchpad/regate/`, outside the repo**, created byte-identical (`app.py`
`fae8e89d…`, `model.py` `3d39a861…` verified after copy) and deleted afterwards. Each arm
recorded its pre-hash, proved application by the hash moving off pristine, and restored to the
exact pre-hash. All arms ran with `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` purged.
Verdicts are per resolved node id, never from the exit code.

Mutations are described by position and operation only, never pasted (C-56).

| Arm | File · site | Operation | Verdict |
|---|---|---|---|
| **M12** (reproduction) | `model.py` · `resolve_document` | reintroduce an iterative parent-chain fold routed through `Graph.parent_of`, bounded by a visited set | **1 RED — `TC-R35`**, 409 green |
| **N1** | `app.py:456` · `HomeScreen.load_or_notice`, the load-failure branch | delete the markup keyword argument from that `notify` call | **0 RED**, 410 passed — `G1` |
| **N2** | `model.py` · `resolve_document` | reintroduce the same bounded fold, but derive the parent by scanning the edge list inline instead of calling `Graph.parent_of` | **0 RED**, 410 passed — `G2` |

**The real tree was not written to at any point.** Its six file hashes are identical at the
start and the end of this review:

```
1b1b9e2b8976f5529e2f11762cf9742ca8f4c6100352ffc91ee43e96c4e84707  mapper/store.py
3d39a861a44f3abef5b73e2b1771f46ebc4b03804867c5d20f25af38c4468688  mapper/model.py
fae8e89df917c3240818a3be1894632883077856db8aeaae05953f49592af7bf  mapper/app.py
cff4e21305cc92d84e23c3e7c809725d60e2346933af4a5fe1a2bf9eda21e7c3  tests/test_repair_fields.py
52773d5fb3676de4b88a2627b8db448f3f675c60fc02b5a0d4b98b76c27a51ba  tests/test_repair_cycles.py
16a6892aca8cd2d87783911857d083785c738879f727648555f7f208d89a4b49  tests/test_repair_depth.py
```

`git status --porcelain` is unchanged from the opening reading. `prototypes/**` untouched.
Nothing committed, stashed, checked out or reset.

---

## 2 · Condition-by-condition adjudication

### C1 (the HIGH) — **DISCHARGED**

Three sub-claims, each checked separately.

**(a) The walk is really gone.** `git diff -- mapper/model.py` shows `resolve_document` reduced
to a `documents.get` plus a copy-returning `Document(...)`. The `parent_of` call, the parent
lookup, the recursive descent and the merge loop are all deleted — not de-recursed, deleted.
The docstring rewrite is honest: it states the absence *is* the repair, records why (graph-level
`documents`, no per-node store), records the measurement that justified it, and explains why
`node` survives in the signature. ✓

**(b) `TC-R35`'s subject is in its own expression, and its positive control works.**
`tests/test_repair_fields.py:537-567`. The node patches `Graph.parent_of` with a recording
wrapper, then — before measuring anything — calls `graph.parent_of("n399")` directly and
asserts `calls == ["n399"]` with the message *"the call counter is not wired; every count below
is vacuous"*. That is a real positive control: a monkeypatch that failed to bind reads zero and
the node fails there rather than passing on a silent absence (C-55's rider). Only then does it
clear the list, call `resolve_document`, and assert the list is empty. **The declared subject —
"does not walk the parent chain" — is now observable, which it provably was not before.** ✓

**(c) `M12` reddens it.** I did not take the transcript's word. Reconstructed on the copy and
run to completion: **`1 failed, 409 passed`**, the single failure being
`tests/test_repair_fields.py::test_tc_r35_resolve_document_does_not_walk_the_parent_chain`.
Identical to the transcript's `M12` block. A blast radius of exactly one is the correct size —
the mutation changes no value any other node can observe, which was `F1`'s whole point. ✓

**Consequential deletions checked.** Risk 4 and §6 pending item 1 are deleted rather than
carried, exactly as the first review's §4 note instructed, with the numbering left in place so
the review's references still resolve. The general lesson is routed to the post-mortem instead
of being dropped. That is the right disposal.

**Residual:** the gate is narrower than its own docstring claims — `G2` below. It does not
un-discharge `C1`, because `C1` asked for a reddenable gate with a battery arm that reddens it,
and that exists and was independently reproduced.

### C3 — **DISCHARGED for the two sinks it names; a third sink was missed by both passes**

Both assertions exist, at genuinely distinct sinks:

- `test_repair_fields.py:385` — `TC-R20`, over `MapScreen._notice_load_warnings`
  (`app.py:1152-1159`).
- `test_repair_fields.py:428` — `TC-R20c`, over `HomeScreen.load_or_notice`'s
  **load-warning** branch (`app.py:459-464`).

Both capture kwargs as `(str(msg), kw)` rather than discarding them — which was the mechanical
cause of `F3` — filter to the hits that matter, assert `hits` is non-empty *first* so the
`all(...)` cannot pass over an empty set, and use `is False`, which rejects a falsy stand-in.
Independence is measured, not asserted: **M19 → `TC-R20` alone; M20 → `TC-R20c` alone**, per the
transcript. Two arms for two call sites is the correct design and it does what it claims. ✓

The gap is that the increment created a **third** new sink. See `G1`.

### C4 — **DISCHARGED**

Verified against the code rather than against the packet. `test_repair_fields.py:44-64` computes
`expected` as `{f.name for f in dataclasses.fields(Ficha) if f.type in ("str", str)}`;
`store.py:28-32` computes the derivation as
`... for name, spec in Ficha.__dataclass_fields__.items() if spec.type in ("str", str)`.
**The predicate is character-for-character the same on both sides.** So the rewritten Risk 2 is
exactly right: an annotation-form change shrinks both sides together and `derived == expected`
survives it, leaving only the `>= 4` floor, which holds only while `Ficha` has exactly four
`str` attributes. The first review's two corrections are both carried: `derived == expected`
**is** asserted by name (line 59) and it **does** redden on single-member loss, so the
"future work" the original pending item 2 proposed is correctly withdrawn. §6 item 2 now
proposes the right closure — a floor derived by a *different* predicate. ✓

### C5 — **DISCHARGED**

`grep` across `tests/` returns **zero** occurrences of `TC-R22`, `TC-R23`, `tc_r22` or `tc_r23`
in any node id. `01-requirements.md:190-193` and the §6 traceability row for US-R04 still
allocate both to `LLR-R04.1`, so increment 4 finds them free. `TC-R33`/`TC-R34`/`TC-R35` are
above the requirements' highest allocated id (`TC-R32`), so the new ids collide with nothing. ✓

**The pin relabelling is honest, and I checked it rather than accepting it.**
`TC-R33`'s docstring (`:571-580`) says *"A REGRESSION PIN, not a gate (C-40's corollary) … the
walk it once certified is gone, so no traversal defect can redden it. It earns its place by
pinning that removing the walk changed no observable value."* That is true and correctly
reasoned — both sides of the comparison are constant functions of the graph-level `Document`, so
no traversal mutation can separate them. The node also justifies its own comparison count
(`assert compared == depth`) so agreement over an empty set cannot be reported as agreement, and
`F10`'s chained-comparison nit is applied — the line is split into two. `TC-R34` (`:608-615`)
and `AT-R17` (`:628-637`) carry the same honest labelling, and `AT-R17`'s docstring names the
arm that measured it staying green (`M11`), which is the strongest form of the disclosure.

One thing `C5` asked for is not done: the requirements' §6 traceability row for US-R03 still
reads `TC-R15 … TC-R21` and does not record `TC-R33`/`TC-R34`/`TC-R35`. The ids are recorded in
the packet's Acceptance row instead. Minor — folded into `G5`.

### C2 — **the decline is acceptable; the declaration is thinner than the condition asked for**

`C2` offered a genuine either/or: guard the non-`dict` node entry, **or** declare the four
measured sibling shapes as a risk. The author took the second, and the scope argument is sound
and specific: widening the guard is `F-M5`'s repair, `F-M5` is explicitly fenced out of this
batch (§6 item 6), and half-fixing a defect another batch owns is worse than leaving it whole.
That is the correct call, and it matches this batch's own discipline about fences. **It does not
block.**

What is thinner than asked: `F2`'s stated purpose for the declaration was *"so the next reader
inherits the measurement rather than the impression."* §6 item 7 names **one** of the four
shapes (the non-`dict` node entry) and refers to the rest as "three others". A reader inherits
the existence of a measurement but not the measurement. `G4`, LOW.

### C6 — **the declines are acceptable; the disclosure of them is incomplete**

`F7` (hoist `_text_attributes()` out of the loop, `store.py:226`) and `F9` (the unreachable
`str` in `("str", str)`, `store.py:31`) are both still present — verified on disk — and both are
declared as conscious declines in §2, with the reasoning stated and the file:line left for a
later batch. **The reasoning is right, and I would have made the same call.** Both are cosmetic,
neither changes a value, and applying them would have moved `store.py` after its eight arms had
run — buying a full battery re-run for zero behavioural change, against a rule that says touch
only what you must. Neither should block, and the observation that `F9` slightly obscures Risk 2
is now redundant anyway, because Risk 2 has been rewritten to state the shared predicate
explicitly.

`F11` is correctly carried to the whole-branch security pass rather than absorbed here.

The disclosure is incomplete: §0 says "§2 says which" of `F6`–`F10` were applied, and §2 covers
only `F10`, `F7` and `F9`. Measured: **`F6` was applied** (`AT-R15`'s docstring at `:469-477`
now says FORK, explains why a fork is the shape `M18` uses, and cross-references `AT-R03b` for
the true diamond — a better fix than the one-liner `F6` suggested); **`F8` was not** (`:112-113`
still assert `date(...).isoformat()`, and `store.py`'s `datetime` branch is still undriven).
`G5`, LOW.

---

## 3 · New findings

### G1 — the increment created three new `notify` sinks; `C3` armed two · **MEDIUM**

**Where:** `mapper/app.py:452-457` · `tests/test_repair_cycles.py:240, 301, 354`

**What.** `HomeScreen.load_or_notice` is new in this diff and contains **two** `notify` calls:
the load-warning branch (`:459-464`, armed by `TC-R20c`) and the **load-failure** branch
(`:452-457`), which formats `darkside.plain(name)` and `darkside.plain(str(exc))` and passes
`markup=False`. `darkside.plain` strips control bytes and **deliberately preserves markup**
(`test_darkside.py:119-120` pins that), and `App.notify` defaults to `markup=True`, so
`markup=False` is the entire markup defense at that sink too. The exception text is
file-derived: `MapStoreError` from A-2's own refusal interpolates node ids read out of a
sidecar.

The three nodes that drive that sink — `TC-R09`, `TC-R09b` and `TC-R08b`, at
`test_repair_cycles.py:240`, `:301` and `:354` — all stub the sink as
`app.notify = lambda msg, **kw: notices.append(str(msg))`, **discarding the kwargs**. That is
verbatim the mechanism `F3` identified. `grep -rn markup tests/` confirms the only two markup
assertions in the entire tree are `TC-R20`'s and `TC-R20c`'s.

**Measured** — arm N1, deleting that keyword argument from that one call:

```
410 passed   0 RED node-verdicts
```

No battery arm covers it either: `M19` and `M20` target the other two sinks by construction.

**Why it matters.** `TC-R09b` exists *because* increment 1's `F2` found a sink-class guard that
was correct and unasserted, and the packet cites it in §1 as a closed carry. The same file, in
the same increment, added a sibling sink with the same unasserted property. It is not a
correctness defect — the code is right today — but increment 4 re-opens `app.py`, which is the
reason `F3` was made a condition rather than a recommendation in the first place.

**Suggested fix.** One line in `TC-R09b`, whose parametrisation already drives this sink over
five exception types — change its stub to capture kwargs and assert:

```python
notices: list[tuple[str, dict]] = []
app.notify = lambda msg, **kw: notices.append((str(msg), kw))
...
hits = [(m, kw) for m, kw in notices if "no se pudo cargar sano" in m]
assert hits, (raised, notices)
assert all(kw.get("markup") is False for _, kw in hits), hits
```

Add the corresponding arm — delete that keyword at that call site — and record its RED count.
It should redden `TC-R09b` across all five parametrised values and nothing else.

### G2 — `TC-R35` asserts "no call to `parent_of`"; its docstring claims "no walk of any kind" · **MEDIUM**

**Where:** `tests/test_repair_fields.py:547-549`

**What.** The docstring's closing sentence reads: *"The declared subject is in the expression:
reintroduce a chain walk of any kind, recursive or iterative, and this reddens instead of
hanging."* The expression is a call counter on `Graph.parent_of`. Those are not the same claim.

**Measured** — arm N2, reintroducing a bounded parent-chain fold in `resolve_document` that
derives each parent by scanning the edge list inline rather than calling `Graph.parent_of`:

```
410 passed   0 RED node-verdicts     (TC-R35 GREEN)
```

Nothing else closes the gap. `TC-R29`'s AST derivation targets *recursion*; an iterative walk is
not recursion, and it stayed green. `TC-R33`, `TC-R33b`, `TC-R34` and `AT-R17` are all constant
functions of the graph-level `Document` on both sides, so none of them can see a walk at all —
which is exactly why they are correctly labelled pins.

**Why it matters.** Two reasons, and the second is the one that made me weigh HIGH.

1. In this batch a docstring is a load-bearing claim — `C-40` is about declared subjects, and
   the whole first review turned on a docstring that promised a positive control it did not
   deliver. A gate whose docstring overstates its own reach is the same failure at lower
   amplitude.
2. Risk 4 and pending item 1 were **deleted** on the strength of fix A dissolving the hang
   hazard. That is correct for the tree as it stands. But the tree's defense against
   *re-acquiring* that hazard is narrower than the docstring says: an inlined walk without a
   visited set is unbounded, and its regression mode is a hang, which is precisely the mode the
   first review established CI cannot enforce.

**Why it is MEDIUM and not HIGH.** `F1` was HIGH because the certifying node could not fail for
*any* mutation of its subject — it was inert. `TC-R35` is not inert: it reddens under `M12` and
under `M11`, both independently confirmed, and it made `M11` stronger (2 RED → 3). `C1` asked
for a reddenable gate with an arm that reddens it, and that is delivered. The finding is a
breadth overclaim with an escape route, not a false positive control.

**Suggested fix** — either is sufficient, and the first is a two-word edit:

- **Narrow the claim.** Say what is asserted: *"reintroduce a chain walk routed through
  `Graph.parent_of` and this reddens instead of hanging; a walk that inlines the parent lookup
  is not covered here — `TC-R29`'s successor is."*
- **Or widen the gate**, reusing machinery that already exists. `test_repair_depth.py` already
  walks `mapper/`'s AST for `TC-R29`; add a sibling assertion that `resolve_document`'s body
  contains no loop over `self.edges` and no call to `parent_of`. That makes the docstring's
  current sentence true.

### G3 — §4's default-lane row is carried from revision 1 · **MEDIUM**

**Where:** `increment-003.md` §4, the lanes table · contradicted by §0

**What.** The table reads *"default (fast) · 393 selected, 16 deselected · **393 passed**"*.
Measured:

```
$ PYTHONUTF8=1 python -m pytest -p no:randomly --collect-only -q
394/410 tests collected (16 deselected) in 0.22s
```

`TC-R35` carries no `@pytest.mark.slow`, so revision 2's new node lands in the **default** lane
and the fast-lane count moved 393 → 394. The both-lanes row (410) is correct; only the fast row
is stale. The arithmetic gives it away independently: 393 + 16 = 409, the revision-1 total.

**Why it matters.** §0 states, in bold, *"**every number in §4 below is from the re-run battery
over the fixed tree**, not carried over."* One row falsifies that universal claim. In a packet
whose entire value is the accuracy of its self-disclosure — and in a re-gate convened partly
because a stale evidence pointer survived a revision — a number that survived the same way is
worth naming rather than waving through. It is not a correctness defect and it does not block.

**Suggested fix.** `393 selected, 16 deselected → **394 passed**`, and re-check the wall-clock
figure in that row while you are in it.

### G4 — C2's declaration names one of the four measured shapes · **LOW**

**Where:** `increment-003.md` §6 item 7

`F2`'s stated purpose for the declare-instead-of-guard option was *"so the next reader inherits
the measurement rather than the impression."* §6 item 7 names the non-`dict` **node entry** and
refers to the remainder as "three others". The other three are recorded only in
`increment-003-review.md`'s `F2` block — a document a later batch has no reason to open. One
line listing all four (node entry a string, node entry a list, `nodes` block a list,
`attachments` non-list, attachment missing `kind`) carries the measurement forward at no cost.
Also worth filing under §5 Risks rather than §6 Pending, since nothing is planned.

### G5 — C6's and C5's disclosures are incomplete · **LOW**

**Where:** `increment-003.md` §0 C6 row and §2 · `01-requirements.md:269`

Two small gaps, both of the same kind:

- §0 says of `F6`–`F10` that "§2 says which" were applied. §2 covers `F10`, `F7` and `F9` only.
  Measured: **`F6` applied** (`test_repair_fields.py:469-477`, and applied *better* than
  suggested — it explains why the fork is the shape `M18` uses and cross-references `AT-R03b`);
  **`F8` not applied** (`:112-113` still assert the standard library; `store.py`'s `datetime`
  branch is still undriven). Two lines in §2 close it.
- `C5` asked to renumber **and** record the reallocation in the requirements' traceability
  table. `01-requirements.md:269`'s US-R03 row still lists `TC-R15 … TC-R21` and does not
  mention `TC-R33`/`TC-R34`/`TC-R35`. The ids are safe — they are above the highest allocated —
  but a scanner reading the requirements will not find them.

### G6 — the superseded transcript carries no internal marker · **LOW**

**Where:** `03-increments/mutation-battery-inc3-v1-prefix.txt:1-6`

The v1 file opens with a header identical in form to the live one: same title *"INCREMENT 3
MUTATION BATTERY"*, same repo path, same harness path. Only `started: 05:10:28` (vs `05:57:11`)
and the filename distinguish them, and its final block pins `store.py 7f50f248…` and
`model.py d1cb6160…` — precisely the pre-fix values the first review recorded as pristine.

The incident this re-gate examines was *"the wrong one of these two files was cited."* Leaving
the superseded artifact self-describing as authoritative leaves the identical trap set for the
next reader, who will not have the packet's row 15 in hand when they open it. One added header
line — `SUPERSEDED BY mutation-battery-inc3.txt — measures a tree that no longer exists; the
hashes below are pre-fix` — closes it. Prefer that to renaming, since the packet references the
current filename. (The `-prefix` suffix is also a slight misnomer: the arm *list* M1–M18 is a
prefix of v2's M1–M20, but the file's bytes are not a prefix of v2's, and `M10`/`M11`/`M12` have
different results and different definitions.)

---

## 4 · The evidence-integrity incident — assessed

**The landed evidence is sound.** I verified the join independently rather than accepting it:

- `sha256sum` of the three source files on disk equals the transcript's `FINAL FILE HASHES`
  block exactly — `1b1b9e2b…c4e84707`, `3d39a861…c4468688`, `fae8e89d…592af7bf`. The
  measured bytes and the shipped bytes are the same bytes.
- The v1 file's pinned `store.py` and `model.py` hashes are the pre-fix values, confirming the
  incident is exactly as described and not a larger problem wearing a small label.
- `app.py`'s hash is **identical in both runs**, which independently corroborates the packet's
  claim that `C3` was discharged purely in test code and that `app.py`'s bytes were never
  touched by revision 2.
- Cross-checking further: **all eight `store.py` arms have identical RED counts in v1 and v2**
  (28, 13, 3, 10, 8, 1, 8, 2, 1, 20 across M1–M7, M16–M18). That is execution-level evidence
  that the `F10` spelling change was behaviourally inert — a stronger claim than "net −2 bytes,
  no value changed", and one the packet could have made for itself.
- The `model.py` arms moved exactly where the fix predicts: `M10` 4 → 5 RED and `M11` 2 → 3 RED,
  both accounted for by `TC-R35` joining the suite; `M12` redefined from the `seen`-set deletion
  to the fold reintroduction.

**The disclosure is adequate.** Gate checklist row 15 names the failure without softening it
("Found broken and repaired at re-gate"), states what the packet had been pointing at, states
why it mattered (the pinned hashes no longer matched the tree), states the detection mechanism
(hash comparison), states the repair, and states the verification. §0 repeats the substance in
the body where a reader will actually meet it, and marks the v1 file as "not this increment's
evidence and no figure below comes from it." Row 6 keeps the gate at ⚠ rather than self-approving.
That is the right shape for a self-reported evidence failure: the artifact says what went wrong
in the same place it says everything else.

The one residual is `G6` — the disclosure lives in the packet and not in the superseded artifact.

---

## 5 · What holds up

Attacked and did not break. Stated explicitly, per the instruction not to manufacture findings.

- **`TC-R35` is a correctly-built gate.** Positive control before the measurement, cleared
  between them, a failure message that names the vacuity it guards against, and an assertion
  that carries the observed count in its message. Reproduced RED under `M12` at a blast radius
  of exactly one. This is the right discharge for `F1` — it changes *what is observed* rather
  than strengthening an output assertion that provably could not discriminate.
- **Fix A was the right branch.** Fix B would have kept a fold, kept the `seen` set, kept the
  hang mode and kept Risk 4, in exchange for speculative per-node inheritance nobody asked for.
  Taking A and deleting the risk it dissolves is simplicity applied correctly.
- **The two armed `markup` assertions are properly built.** Kwargs captured rather than
  discarded, `hits` asserted non-empty before the `all(...)`, `is False` rather than a
  truthiness test, and independence *measured* by two arms rather than argued.
- **`TC-R33`/`TC-R34`/`AT-R17` are honestly labelled.** All three say pin, not gate, and say
  why. `AT-R17` goes further and names the arm that measured it staying green. Labelling a node
  by what it cannot catch is the harder and more useful direction.
- **`TC-R33` gained a real assertion in the rename.** The aliasing check —
  mutating the returned `tags` and asserting the graph's own mapping is unaffected — is a
  genuine new discriminating property, not a cosmetic addition, and it is the one thing in that
  node that a source mutation (dropping the `dict()` copies) could still redden.
- **The declines are the right calls, both of them.** `F7`/`F9` are cosmetic and moving
  `store.py` post-battery would have bought a re-run for nothing; `C2`'s widening genuinely
  belongs to `F-M5`'s batch. Declining with a stated reason and a file:line pointer is the
  correct handling, and the packet does not pretend otherwise.
- **Risk 2's rewrite is exactly right**, and I verified the characterisation against both files
  rather than accepting it. It correctly withdraws the work that was already shipped, correctly
  names the shared predicate as the real residual, correctly identifies that only the `>= 4`
  floor stands and only while `Ficha` has four `str` attributes, and correctly proposes a
  closure that uses a *different* predicate.
- **The battery is stronger than the one it replaced**, not merely re-run: 18 → 20 arms, an
  inert-arm-free run, and `M12` redefined from an arm whose failure mode was a hang to one whose
  failure mode is a RED verdict. That is the single most valuable change in the revision.
- **Everything the first review passed still passes.** `_coerce_field`'s type ladder, A-9's
  delegation, A-2 refusing before writing, the three `TC-R20` variants, `M18`'s false-refusal
  price, the frozen-interface fence, D12's deletion — none of it moved, and the identical
  `store.py` arm counts across both runs are the evidence that the source did not drift under
  them.

---

## 6 · Verdict

- [x] **OK to advance** — **PASS**
- [ ] OK with the listed fixes applied first
- [ ] Block

**Zero HIGH.** `C1` is discharged in substance and verified by re-execution, not by reading the
claim. `C3`, `C4`, `C5` are discharged. `C2` and `C6` are declined with reasons that are sound
and scoped, which is what the conditions permitted.

**Three MEDIUM** (`G1`, `G2`, `G3`) and **three LOW** (`G4`, `G5`, `G6`), all recommendations.
None is a correctness defect in shipped code and none is a test giving false confidence about
whether the repair works. My suggested disposition: take `G1` and `G3` before increment 4 opens
`app.py` — `G1` is one line in an existing parametrised node plus one arm, `G3` is one number —
and take `G2`'s docstring narrowing now, deferring the AST widening to whoever next touches
`TC-R29`'s family. `G4`, `G5` and `G6` are one line each at batch close.

---

## 7 · Evidence checklist

| Item | ✓/✗ | Evidence |
|---|:--:|---|
| Post-fix diff read in full | ✓ | `git diff` for `model.py` and `app.py` in full; `store.py:25-40, 218-245, 282-296`; `test_repair_fields.py:40-75, 340-440, 468-642`; `test_repair_cycles.py:269-311` |
| Every condition adjudicated by execution, not by the author's claim | ✓ | §2 — C1 by `git diff` + arm M12 reproduced (1 RED); C3 by grep + the transcript's M19/M20; C4 by reading both predicates; C5 by grep + `01-requirements.md:190-193, 269-271` |
| The HIGH's arm re-run independently | ✓ | M12 reconstructed on a copy: **`1 failed, 409 passed`**, the failure being `test_tc_r35_…` |
| New/newly-labelled test surface attacked | ✓ | two novel arms designed and run — N1 (`G1`, 0 RED) and N2 (`G2`, 0 RED); `TC-R35`'s positive control, `TC-R33`/`TC-R34`'s pin labels and both `markup` assertions read against their claims |
| Numbers re-derived, not accepted | ✓ | §1 rows 1–5: 410 passed / 394-16 lanes / 49·25·91 / ruff 29 & 57 / ledger arithmetic. Base **356** accepted on the packet's word, stated so |
| Transcript hashes verified against disk | ✓ | §1 row 6 — all three equal; plus the v1/v2 RED-count cross-check (§1 row 13) corroborating the `F10`-only claim by execution |
| Evidence-integrity incident assessed | ✓ | §4 — landed evidence sound, disclosure adequate, one LOW residual (`G6`) |
| Simplicity pass | ✓ | fix A removes 35 lines and one risk; the declines of `F7`/`F9` correctly avoid churn |
| Reuse / duplication checked | ✓ | `TC-R35` reuses `_chain`; `G2`'s suggested widening reuses `TC-R29`'s existing AST machinery rather than adding new |
| Tests reviewed for intent, not behaviour | ✓ | `TC-R35` gate vs. `TC-R33`/`TC-R33b`/`TC-R34`/`AT-R17` pins, all label-checked; `TC-R09b`'s stub found to discard the kwargs it needs (`G1`) |
| Mutation protocol honoured | ✓ | three arms, all on a copy outside the repo, hash-verified before and after, `PYTHONDONTWRITEBYTECODE=1`, `__pycache__` purged, verdicts per node id; copy deleted |
| Real tree left byte-identical | ✓ | six sha256 values in §1 identical at open and close; `git status --porcelain` unchanged; no file in the repo written |
| Security lens | ✓ | `G1` is the security-relevant finding (unarmed markup defense over file-derived text at a third sink); `F11` correctly carried to `security-reviewer` |
| Scope fence | ✓ | frozen interfaces absent from the diff; `TC-R22`/`TC-R23` confirmed free for increment 4 |
| Verdict explicit | ✓ | **PASS** — zero HIGH |
