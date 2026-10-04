# Increment 012 — Inc-REPAIR S-E — independent code review

**Range:** `git diff fdbdd62..ea5d4c2 -- mapper/ tests/`
**Reviewer:** code-reviewer (gate 1 of 2; security review follows)
**Date:** 2026-09-11

## VERDICT: **BLOCK** — 3 HIGH

Four of the five defects are fixed correctly and the fixes are minimal. The stage is blocked on:
one fix that **introduces a new defect at the sink it was meant to harden** (HIGH-1), one fix whose
bound is **defeated by a cheaper input than the one it was measured against** (HIGH-2), and one
**ratified control that is absent**, which I fired and confirmed leaves a shippable wrong
implementation green (HIGH-3).

---

## Boundary statement

**Reviewed.** The full diff (`mapper/store.py`, `mapper/screens/coverage.py`,
`tests/test_repair_sidecar.py`, `tests/test_darkside_census.py`); `01-requirements.md` §3.9
(`HLR-REPAIR.1`, `LLR-REPAIR.1`, `LLR-REPAIR.2` and their boundary catalog);
`.dev-flow/state.json` → `p3_progress.inc_repair_pregate`; `tests/test_repair_store_boundary.py`
(`test_at_p02d`); `tests/test_darkside_census.py`'s `_sites` matcher; `mapper/darkside.py::plain`;
`mapper/app.py:534-552` and `:1277-1290` (the `load_warnings` sinks);
`textual/widgets/_data_table.py::default_cell_formatter`.

**Fired** (see each finding): 4 source mutants (M1–M4, hash-verified), 1 scalar-amplification probe,
1 attachment round-trip probe, 1 coverage-arithmetic probe, 1 path-like-map-id probe, 1 markup-sink
probe, 1 calibration probe. Full suite: **995 passed, 20 deselected, 3 xfailed** at `ea5d4c2`.

**Not reviewed / out of lane.** Security framing of HIGH-1 and HIGH-2 (routed to `security-reviewer`
— I report the correctness fact and the measurement, not the threat model). The Spanish register of
the `B-30` message (routed to `ux-reviewer`). Whether the `HomeScreen` damaged-card pilot arm is
deferred by an authority I did not find — I report only that the ratified threshold names it and
this module does not carry it.

**Could not determine.** Whether the `AT-049` pilot arm (`HomeScreen` damaged card) and the missing
negative arm were deliberately deferred to a later stage: `inc_repair_pregate.S-E_pregate` records
`AT_NODES_MISSING` and says "S-E owes both arms", but records no deferral of either arm's boundary
catalog. If a deferral exists, HIGH-3 downgrades to MEDIUM; nothing I read recorded one.

**Tree state.** Working tree clean at `ea5d4c2` on entry and on exit. Every mutation was byte-level
against CRLF-anchored text with the match count asserted `== 1` before firing, restored
unconditionally, and sha256-verified after each. Final hashes match pristine:
`store.py b5503ef8…`, `coverage.py 925a655c…`, `test_repair_sidecar.py 9a63595d…`,
`test_darkside_census.py 1db89d08…`. `__pycache__` purged. No evidence of another writer.

---

## HIGH findings

### HIGH-1 — the `escape` → `plain` swap REMOVES a markup guard at a sink that parses markup

**Where:** `mapper/screens/coverage.py:94` (the title cell). The second cell, `:96`, is fine.

**What.** `darkside.plain` deliberately does **not** escape markup, and its docstring says why:
*"these strings are placed into `Text` objects with explicit styles, and `Text` does not parse
markup."* **That premise is false at this call site.** `:94` passes a bare `str` to
`DataTable.add_row`, and Textual's `default_cell_formatter` sets `possible_markup = True` for any
`str` and returns `Text.from_markup(content)`
(`textual/widgets/_data_table.py:202-224`). The old `escape()` was the thing making that safe.

**Fired.** Same hostile title through both forms:

```
pre-fix   escape(title)          -> Text.from_markup plain: '[red]rojo[/red] and [link=file:///C:/Users/secret]click[/link]'
                                    spans: []                         MARKUP INTERPRETED: False
shipped   darkside.plain(title)  -> Text.from_markup plain: 'rojo and click'
                                    spans: [Span(0,4,'red'), Span(9,14,'link file:///C:/Users/secret')]
                                    MARKUP INTERPRETED: True
```

A sidecar-controlled title now injects arbitrary Rich style **and a live `link` target** into the
coverage table. The diff traded a control-character hole for a markup hole at the same cell.

**Why it matters.** The diff's own comment at `:86-93` reasons "`escape` guards markup and coerces
nothing else" and concludes `plain` is strictly better. That is true of `:96`, where `Text.assemble`
yields a `Text` and `default_cell_formatter` returns it untouched — and false of `:94`, where the
value is still a `str`. One comment now justifies two call sites that are not alike. This is the
same class the batch keeps cataloguing: a true statement applied one line past where it holds.

**Smallest fix.** Keep `plain` and make the docstring's premise true — hand the sink a `Text`:

```python
Text(darkside.plain(node.ficha.title or node.id)),
```

`Text` is already imported. Rendering is unchanged (`escape` + `from_markup` also rendered the
literal). Prefer this over `escape(darkside.plain(...))`, which re-adds the backslashes `plain`'s
docstring argues against and leaves the site depending on the sink's markup behaviour.

**Also needed:** an arm. No test in this diff observes the rendered cell — the only coverage-screen
arm is the AST arm at `test_repair_sidecar.py:266-283`, which asserts `escape` is *absent* and
therefore **passed throughout this regression**. An arm that drives a markup-bearing title through
`default_cell_formatter` and asserts `spans == []` would have caught it.

---

### HIGH-2 — `_raw_origin`'s TYPE bound is not enough; fired at 348× amplification

**Where:** `mapper/store.py:162-179` (`_raw_origin`) and `mapper/store.py:430` (`{doc.name!r}`).

**Ruling on handoff (1): the type bound is insufficient, and it is a live hole, not a theoretical
one.** I built a sidecar that reaches this line with a huge scalar. It does not need a huge file,
because YAML lets one anchor be *reused* for 3 bytes a time and the duplicate branch fires once per
reuse:

```
payload=50,000 dups= 50   file=51,818 B   load=0.048 s   warn_chars=4,901,421    amplification=94.6x
payload=50,000 dups=200   file=57,168 B   load=0.081 s   warn_chars=19,905,771   amplification=348.2x
```

A **57 KB** sidecar yields **19.9 MB** of load warnings in **0.081 s**. Amplification is linear in
both payload size and duplicate count, and both are nearly free in the file: a 1 MB anchor with
10,000 aliases is a ~1.1 MB file and ~20 GB of warnings.

**Two things make this worse than the alias bomb the fix was measured against.** First, it is
**cheap** — 0.081 s, versus 5.2 s for the 8-level bomb — so nothing times out and nothing looks
wrong. Second, `_raw_origin` is **not the only offender on that line**: each warning measured
100,029 chars = 2 × 50,000, because `{doc.name!r}` at `:430` materialises the coerced name, which for
a `str` *is* the same string. The AST class arm cannot see `doc.name!r` (it is an Attribute, not a
Call), and `_raw_origin` does not guard it.

**Why it matters.** `load_warnings` are not inert. `mapper/app.py:548` does
`darkside.plain('; '.join(graph.load_warnings))` into `self.notify(...)`, and `app.py:1287` does the
same. Twenty megabytes goes through a per-character `str.translate` and then into a Textual toast.
This is the identical defect shape `LLR-N13.1.7` was opened for — the diagnostic performing a
materialisation — surviving its own fix through a different type.

**Smallest fix.** Bound the length as well as the type, and route both halves through it:

```python
_ORIGIN_CHARS = 120

def _raw_origin(value: Any, coordinate: str) -> str:
    if isinstance(value, (str, bytes, int, float, bool)) or value is None:
        shown = repr(value)
        if len(shown) <= _ORIGIN_CHARS:
            return shown
        return f"{shown[:_ORIGIN_CHARS]}… ({coordinate})"
    return coordinate
```

and at `:429-432` apply the same bound to the coerced name:

```python
graph.load_warnings.append(
    f"documento duplicado: {_raw_origin(doc.name, f'document[{i}].name')} <- "
    f"{_raw_origin(d.get('name'), f'document[{i}].name')}"
)
```

Truncation preserves what `AT-P02d` actually needs — I read the arm
(`tests/test_repair_store_boundary.py:544-573`); the two document cases assert the exact records
`documento duplicado: '1' <- 1` and `documento duplicado: 'd1' <- 'd1'`, both far under any sane
bound, so `1` stays distinguishable from `'1'` and the pin stays green.

**Also needed:** an arm driving *this* fixture. The existing `< 2_000` oracle is the right oracle and
catches it — I checked: it reports `False` on the 200-dup sidecar. It is the **fixture** that is
incomplete, not the threshold.

---

### HIGH-3 — `AT-049`'s ratified negative arm is absent, and its omission is not theoretical

**Where:** `tests/test_repair_sidecar.py:57-99` (`test_at049_a_phantom_sidecar_id_records_a_load_warning`).

**What.** `01-requirements.md` §3.9 boundary catalog, **empty** row, mandates it verbatim:
*"`AT-049`'s negative arm drives the same workspace with the phantom removed and asserts **no**
warning and a healthy card, so the positive arm is not passing on a constant."* `M-REPAIR.1-a` names
it again as one of the two things that redden that mutant. `LLR-REPAIR.1`'s restated threshold
requires **set equality** — *"the set of named ids shall equal the set of phantoms — set equality,
not a count"*. The shipped arm asserts only `any(phantom in w ...)` per phantom plus the node set.

**Fired — M3.** I moved the append out of the `if nid not in graph.nodes:` guard so the store warns
`nodo fantasma` for **every** sidecar id, phantom or not:

```
### M3 warn on every id (no negative arm): anchor match count = 1
7 passed in 0.17s
RESTORED, sha256 == b5503ef8… OK
```

**All seven arms green.** M3 is not a contrived mutant — it is one indentation level away from the
shipped code, it is the shape an implementer reaches for, and it makes **every healthy map** raise a
warning toast naming each of its nodes. The suite cannot tell it from the fix.

**Why it matters.** This is the false-confidence class exactly: the positive arm cannot distinguish
"warns on phantoms" from "warns on everything", and the requirement anticipated that and mandated the
control that separates them. The arm was skipped.

**Smallest fix.** Add the mandated negative arm and tighten the positive one to the ratified oracle:

```python
def test_at049_a_clean_sidecar_records_no_phantom(tmp_path):
    """The negative control the boundary catalog mandates: without a phantom, silence."""
    store = _write(tmp_path, "schema: []\nnodes:\n  raiz:\n    title: Raiz\n"
                             "  hijo:\n    title: Hijo\n")
    graph = store.load("m")
    assert [w for w in graph.load_warnings if "fantasma" in w] == [], graph.load_warnings
```

and in the positive arm, replace the two `any(...)` loops with set equality:

```python
named = {w.split("'")[1] for w in graph.load_warnings if w.startswith("nodo fantasma:")}
assert named == {"fantasma", "segundo_fantasma"}, graph.load_warnings
```

That kills M3 and satisfies "set equality, not a count" in one line.

---

## MEDIUM findings

### MEDIUM-1 — the AST "class" arm is not a class arm: fired two reintroductions past it

**Where:** `tests/test_repair_sidecar.py:200-225`.

**Ruling on handoff (2): it forbids too little, and it is not a loophole you built for yourself — it
is an arm that would have missed the defect however you had fixed it.** Two mutants:

```
### M1 subscript reintroduction  d['name']!r   -> AST arm PASSED; 2 fixture arms failed
### M2 name-bound reintroduction  raw!r        -> AST arm PASSED; 2 fixture arms failed
```

`ast.Call` is one of at least four spellings of the same defect: `d['name']!r` (Subscript),
`raw!r` (Name), `doc.name!r` (Attribute — **already live on line 430**, see HIGH-2), and
`f"{repr(d.get('name'))}"` (no `!r` conversion at all). The arm's docstring says it "forbids the
shape rather than the instance"; it forbids one of four spellings of the shape.

On the other half of the question — does it forbid too much? No. There is no legitimate
`!r`-on-a-call in `store.py` today and none is likely; the arm is not costly, it is just not
load-bearing. The **structural `< 2_000` arm is what actually killed M1 and M2**, by 261×, in 0.02 s.

**Smallest fix.** Either delete the AST arm and say the structural arm owns the class, or widen its
predicate to any non-constant value under `!r` and add the sibling `repr(...)` call form:

```python
and not isinstance(node.value, (ast.Constant, ast.Name)) or _is_repr_call(node.value)
```

I lean **delete**: an arm that names a class and enforces a quarter of it is worse than no arm,
because its name is what a reader trusts. If it stays, its docstring must say it covers the Call
spelling only, and must not claim "the defect cannot be rewritten elsewhere" — I rewrote it twice.

### MEDIUM-2 — the bounded-warning arms have no positive control

**Where:** `tests/test_repair_sidecar.py:186-196` and `:228-249`.

**Fired — M4.** I replaced the whole duplicate-document warning with `pass`:

```
### M4 delete the duplicate warning entirely: 2 passed in 0.08s
```

Both `LLR-N13.1.7` arms are pure **upper bounds**, so deleting the diagnostic is a green way to
satisfy them. `test_at_p02f` elsewhere in the suite is the control for the *record's presence*, but
nothing in this module ties the bound to a warning that exists.

**Smallest fix.** One line in each arm:

```python
assert any(w.startswith("documento duplicado:") for w in graph.load_warnings), graph.load_warnings
```

### MEDIUM-3 — a false measured number in a shipped comment: 54 s and 522 MB are different depths

**Where:** `mapper/store.py:418-421` and `mapper/store.py:172-175`.

Both say the 9-level sidecar *"loaded in 54 SECONDS and emitted a 522-megabyte warning."* Measured:

```
levels=5: repr() -> 522,220 chars in 0.0044 s
levels=8: repr() -> 522,222,220 chars in 5.2084 s
```

**522 MB is the 8-level figure** (5.2 s). Nine levels is 1000× the 5-level size — **~5.2 GB**, at
~52 s. The comment pairs the 9-level *time* with the 8-level *size*. The test module has it right
(`:239-243`: "5.3 s at this depth, 54 s one level deeper"), so the error is confined to the source
comments, but they are the record a future reader trusts.

**Spot-check that did hold, for the record.** The `522,311 chars / 25 ms` calibration at
`store.py:420-421` is **exactly right**: 522,220 (the repr) + 27 (`documento duplicado: '' <- `) +
2×32 (the two `campo ilegible: document[i].name` records) = 522,311. Measured 25 ms against my
~22 ms. That number is sound; the other one is not.

**Smallest fix.** `store.py:418-421` and `:172-175`: *"…loaded in 54 SECONDS at nine levels, and at
eight emitted a 522-megabyte warning in 5.2 s."*

### MEDIUM-4 — `AT-050`'s ratified boundary arm is absent, and the module's oracle contradicts it

**Where:** `tests/test_repair_sidecar.py:107-131`; §3.9 boundary catalog, **boundary** row:
*"`AT-050` requests a map id that is itself a path-like string, and asserts the message still names
only the id."*

**Fired.** The arm is missing, and had it been written with this module's oracle it would be RED:

```
id='no_such_map'        msg="no existe el mapa 'no_such_map'"           markers hit: []
id='../../etc/passwd'   msg="no existe el mapa '../../etc/passwd'"      markers hit: ['/']
id='sub/dir/mapa'       msg="no existe el mapa 'sub/dir/mapa'"          markers hit: ['/']
```

The code is **correct** — it names only the id. The module's proxy oracle (`"/" not in message`,
`"\\" not in message`) is what does not generalise: it conflates "the store disclosed a path" with
"the string contains a separator". The requirement's oracle is a **sentinel**, not a separator scan.

**Smallest fix.** Add the boundary arm with the requirement's own oracle, and re-key the existing arm
onto a sentinel so both agree:

```python
def test_at050_a_path_like_map_id_is_named_and_nothing_else(tmp_path):
    store = MapStore(tmp_path / "SENTINELA-WS")
    with pytest.raises(MapStoreError) as caught:
        store.load("sub/dir/mapa")
    message = str(caught.value)
    assert "sub/dir/mapa" in message
    assert "SENTINELA-WS" not in message and ".mmd" not in message
```

### MEDIUM-5 — the contradicted comment was not removed; the new one says it "used to say"

**Where:** `mapper/store.py:442-450` (untouched) against `mapper/store.py:459-467` (added).

`:444-446` still reads: *"a sidecar id matching no parsed node is still added … **That is outside
this batch's fence**, and saying otherwise here would be a false record in the evidence."* Ten lines
below, the new comment says *"The comment above **used to say** the phantom 'is still added … That is
outside this batch's fence'; the fence moved."* It still says it. Two comments, ten lines apart,
disagree about whether this is in scope, and one of them describes the other in the past tense.

`LLR-REPAIR.1`'s own **Value reconciliation (C-36)** clause anticipated this: *"The change is a
change, not a description."* The change landed; the description did not.

**Smallest fix.** Delete `:442-446` (from *"It does NOT remove a phantom node"* through *"false
record in the evidence"*), keeping `:447-450`, which is about the raw id in the label and is still
true.

### MEDIUM-6 — `B-48`'s test oracle is content-based; the implementation is key-based

**Where:** `tests/test_repair_sidecar.py:160-166` against `mapper/store.py:217-226`.

The arm asserts *no* attachment has empty kind, path **and** caption. The implementation refuses on
**key presence**. Fired:

```
only caption           -> Attachment(kind='', path='', caption='pie')  warn=[]
empty mapping {}       -> refused                                      warn=['adjunto sin campos: raiz.attachments[0]']
nulls for all three    -> Attachment(kind='', path='', caption='')     warn=[]      <-- the arm's oracle, RED
unknown key only       -> refused                                      warn=['adjunto sin campos: …']
non-str keys           -> refused                                      warn=['adjunto sin campos: …']
```

A hand-written `- kind: null\n  path: null\n  caption: null` still produces exactly the phantom the
docstring says is now impossible. The arm passes only because its fixture happens to use an unknown
key.

**The implementation is right and the oracle is wrong** — see handoff (3) below; a content-based
refusal would destroy an operator's deliberately-empty attachment on round-trip. So fix the claim,
not the code: narrow the assertion to what the fix does, and say so in the docstring.

```python
assert not [a for a in attachments if not a.kind and not a.path and not a.caption
            and a not in _ROUND_TRIPPED]      # or, simply:
assert any("adjunto sin campos: raiz.attachments[0]" in w for w in graph.load_warnings)
assert len(attachments) == 0
```

### MEDIUM-7 — `LLR-REPAIR.2`'s two numeric clauses are not asserted

**Where:** `tests/test_repair_sidecar.py:118-131`.

The threshold is *"**0** occurrences of the workspace path, **of any of its components**, and of the
platform path separator … the map id appears **exactly once**."* The arm asserts the full path is
absent (not its components) and containment (not `== 1`). A message like
`f"no existe el mapa {map_id!r} en {self.workspace.name}"` discloses a path component and passes
every assertion here. `M-REPAIR.2-a` does die — but on the `.mmd` marker, not on the
"exactly once" clause the requirement named as its killer. Fold into MEDIUM-4's fix:
`assert message.count(map_id) == 1`.

---

## LOW findings

- **LOW-1 — the slow arm.** See handoff (4).
- **LOW-2 — stale number.** `tests/test_repair_sidecar.py:230` says "benign 31 chars". Measured on
  the shipped tree: **49** — because `B-29`'s own fix in this diff added `nodo fantasma: 'n'` (18
  chars) to that very fixture. The number was measured before the fix it ships beside.
- **LOW-3 — the fixture's accidental phantom.** `amplified()` (`:36-48`) declares `nodes: n:`, which
  the `MMD` constant never defines, so every `LLR-N13.1.7` arm now also fires a `B-29` warning.
  Harmless at 125 chars against a 2,000 bound, but it couples two requirements' fixtures for no
  reason. Rename `n` to `raiz`.

---

## The four handoff points — fired vs. reasoned

| # | Question | Verdict | Basis |
|---|---|---|---|
| 1 | Is a TYPE bound enough without a LENGTH bound? | **No — live hole.** HIGH-2. | **FIRED.** 348× amplification from a 57 KB file; 19.9 MB of warnings in 0.081 s; and `{doc.name!r}` at `:430` is unbounded too. |
| 2 | Is `{call()!r}` the right CLASS boundary? | **No — too little.** MEDIUM-1. | **FIRED.** M1 (Subscript) and M2 (Name) both pass the AST arm. |
| 3 | Can the derived key set refuse a LEGITIMATE attachment? | **No.** The fix is sound. | **FIRED.** Round-trip probe + 6 hand-written shapes. |
| 4 | Does the slow arm earn its place? | **No — remove it.** LOW-1. | **FIRED.** M2's redness landed at 5.0 s against a `< 5.0` bound. |

**(1) — fired.** Reported as HIGH-2. Your instinct was right and the hole is larger than the form you
proposed: a truncated display fixes `_raw_origin`, but `{doc.name!r}` on the same line needs the same
treatment, and the AST arm cannot see it.

**(2) — fired.** The `_raw_origin` routing is **not** a loophole you built for yourself. I tested that
directly: M1 and M2 reintroduce the defect *without* your helper and pass the arm just the same. The
arm is shape-based where the property is semantic, so it passes your fix and the reintroduced defect
for the same reason. What did the work in both mutants was the structural `< 2_000` arm.

**(3) — fired.** `_build_sidecar` (`store.py:360-363`) emits all three keys unconditionally, so
save→load round-trips cleanly, *including* an operator's deliberately-empty
`Attachment(kind='', path='', caption='')` — I confirmed it survives with no warning. Of the six
hand-written shapes I drove, the three now refused (`{}`, unknown-key-only, non-str-keys) are all
genuine invented phantoms. **No legitimate sidecar shape is refused.** The one thing the change does
not do is what its *test* claims — MEDIUM-6.

**(4) — fired, and the marginal redness is worse than stated.** M2's reintroduction reddened the slow
arm at **5.0 s against `assert elapsed < 5.0`** (M1 at 5.2 s). That is a 0–4% margin: on a faster
machine, a warm cache, or a different YAML build, this arm goes **green against the defect it
exists for**. The default-lane structural arm caught the identical mutants at 522,329 chars against
2,000 — **261×, deterministic, 0.02 s**. The slow arm costs 5.2 s of slow-lane budget to add a
flaky restatement of a claim already proven 261× over.

**Recommendation: delete `test_llr_n13_1_7_an_amplified_sidecar_loads_in_bounded_time`.** The two
alternatives both fail: 9 levels is 54 s and falsifies `pyproject.toml`'s <20 s declaration, and
staying at 8 keeps a discriminator inside its own noise. If a wall-clock arm is genuinely wanted, it
should be reddened by an order of magnitude, not by 0.4% — and nothing in this defect's cost curve
offers that inside the slow lane's budget.

---

## Verified as correct (stated so the gate is not read as blanket doubt)

- **`B-29` warns and still adds — this is what `LLR-REPAIR.1` requires.** The clause is explicit
  (*"shall not change the meaning of the coverage values"*, and **THE FIX IS THE WARNING, NOT
  `coverage()`**). Your first arm asserting absence was wrong and the correction is right. Arithmetic
  verified unchanged by construction — the diff adds one `append` **before** the pre-existing
  `add_node` — and by measurement: a schema with 1 required field, `raiz` complete, `hijo` and one
  phantom empty → `coverage() == (1, 3)`, phantom present in `graph.nodes`, one warning naming it.
- **`B-30` is reachable and its information content is right.** `str(exc)` reaches
  `app.py:541` (`load_or_notice`) and `app.py:1181`. The map id is the only actionable part. Register
  is `ux-reviewer`'s.
- **`B-48`'s derived key set** — handoff (3). Deriving from `fields(Attachment)` rather than spelling
  the set is the right call and the comment's stated reason is the real one.
- **The census pin update is honest and did not widen.** `_sites`
  (`test_darkside_census.py:132-140`) keys on the **exact stripped line**. The new entry
  `'(darkside.plain(",".join(missing)), darkside.ALERT)'` matches only because `coverage.py:95-97`
  was reflowed so the tuple sits alone. The classification (ALERT on a missing-fields list) is
  genuinely unchanged.
- **Only ONE pin actually changed, and that is the right outcome.** The brief said three
  (A3 census, hue census, `AT-P02d`). `git show --stat ea5d4c2` lists four files;
  `tests/test_a3_census.py` and `tests/test_repair_store_boundary.py` are **untouched** and green.
  `AT-P02d` in particular was left intact and the fix was built to keep it green — which is the
  correct handling of a ratified acceptance, and better than the "updated" the brief claims. Worth
  correcting in the record: *unchanged because the fix respected them* is a stronger statement than
  *updated*.
- **Full suite green at `ea5d4c2`:** 995 passed, 20 deselected, 3 xfailed, 236 s.

---

## Control 18 — can each arm fail?

| Arm | Can fail | Evidence |
|---|---|---|
| `test_at049_…records_a_load_warning` | **partially** | Kills `M-REPAIR.1-b` (drop-instead-of-warn) and `M-REPAIR.1-c` (warn-once). **Survives M3** (warn on every id) — HIGH-3. |
| `test_at050_…names_the_map_not_the_filesystem` | yes | Was RED pre-fix; kills `M-REPAIR.2-a` on the `.mmd` marker. Oracle does not generalise to the mandated boundary — MEDIUM-4. |
| `test_b48_…refused_not_invented` | yes, on its fixture | Its stated oracle is RED against the shipped code on a neighbouring fixture — MEDIUM-6. |
| `…refusal_warnings_carry_coordinates_not_values` | **yes, strongly** | Killed M1 and M2 at 522,329 vs 2,000 (261×), 0.02 s, deterministic. Cannot pass for a reason unrelated to the defect *except* by the diagnostic being deleted — M4, MEDIUM-2. |
| `…no_warning_interpolates_a_raw_sidecar_value` | **no, for the class it names** | M1 and M2 both green — MEDIUM-1. |
| `…loads_in_bounded_time` (slow) | marginally | M2 red at 5.0 s vs `< 5.0` — LOW-1. |
| `test_coverage_screen_coerces_…_with_plain` | yes, for `escape` | But it passed straight through HIGH-1, because "is `escape` absent" is not "is the cell safe". |

The default-lane structural arm **cannot** pass for a reason unrelated to the defect on its own
fixture — that part of your design is sound and is the strongest thing in the increment.

---

## To clear the gate

1. **HIGH-1** — `Text(darkside.plain(...))` at `coverage.py:94`, plus an arm asserting
   `default_cell_formatter(cell).spans == []` for a markup-bearing title.
2. **HIGH-2** — length-bound `_raw_origin` and route `doc.name` through it; add the multi-duplicate
   scalar fixture to the `< 2_000` arm.
3. **HIGH-3** — add the mandated `AT-049` negative arm and the set-equality assertion.
4. MEDIUM-1…7 and LOW-1…3 are recommendations; MEDIUM-3 and MEDIUM-5 are corrections to the
   **record** and should land with the HIGHs, since the record is what the next reader inherits.

Per **D35**, three HIGH findings restore/confirm full protocol for this stage. HIGH-1 should be
re-read by `security-reviewer` under its own lens; I report it here as a correctness regression with
a measured before/after, not as a threat assessment.

## Evidence checklist

- [x] Diff read in full — `mapper/store.py:153-232, 409-433, 456-469, 520-529`;
      `mapper/screens/coverage.py:1-8, 84-100`; `tests/test_repair_sidecar.py:1-283`;
      `tests/test_darkside_census.py:180-188`.
- [x] Correctness pass (edge / None / error paths) — HIGH-1, HIGH-2, MEDIUM-6 all from this pass.
- [x] Simplicity pass — no premature abstraction found; `_raw_origin` is a single-use helper but
      earns it (it is the seam the AST arm needs and the seam the length bound belongs in).
- [x] Reuse / duplication checked — `_ATTACHMENT_KEYS` correctly reuses `fields()` like
      `_text_fields`/`_str_map_fields`; `darkside.plain` is the batch standard and is reused, though
      misapplied at one site (HIGH-1).
- [x] Tests reviewed for intent — four mutants fired; two arms found non-discriminating (HIGH-3,
      MEDIUM-1), one found without a positive control (MEDIUM-2).
- [x] Verdict explicit — **BLOCK**.
- [x] Tree left byte-identical to `ea5d4c2`, sha256-verified, caches purged.
