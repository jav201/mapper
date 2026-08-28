# Code Review — Increment 1 · `2026-08-27-repair-batch-02`

**Reviewer:** `code-reviewer` (independent; did not author the diff)
**Branch:** `fix/repair-batch-02` · **Base ref:** `d877784`
**Requirement under review:** `HLR-STO.1` / `LLR-STO.1.1` (`01-requirements.md` §2.1, §3.1)

## Verdict

**BLOCKED** — one HIGH finding (`F1`). Everything else is a recommendation.

`F1` is a *test that gives false confidence*, proved by a surviving mutant, and the shipped
diff already contains one live instance of the behaviour that test cannot see. Fix `F1`
(both limbs) and the increment advances; `F2`–`F4` should ride along because their fixes are
one-liners with executed evidence attached.

---

## Scope reviewed

| Artefact | Range read |
|---|---|
| `mapper/store.py` | full file, 485 lines; diff `d877784..worktree` read in full (`git diff mapper/store.py`, 5 hunks) |
| `tests/test_repair_store_boundary.py` | full file, 332 lines (new, untracked) |
| `mapper/model.py` | full file, 240 lines (the derivation's source of truth) |
| `mapper/app.py:1525-1543`, `mapper/diff.py:45-63` | the two callers of `_graph_from_sidecar` outside `load` |
| `tests/test_repair_fields.py:120-180` | the pre-existing `load_warnings` equality assertions |
| whole `tests/` tree | reverse census (C-26), 8 symbols |

### Evidence re-verified before reviewing (C-19: I ran these, I did not read them)

```
$ PYTHONUTF8=1 python -m pytest -q -p no:randomly
470 passed, 16 deselected in 101.55s

$ PYTHONUTF8=1 python -m pytest -q -p no:randomly -m slow
16 passed, 470 deselected in 39.47s

$ PYTHONUTF8=1 python -m pytest -q -p no:randomly --collect-only
470/486 tests collected (16 deselected)

$ PYTHONUTF8=1 python -m ruff check mapper/ tests/
Found 29 errors.
$ PYTHONUTF8=1 python -m ruff check mapper/store.py tests/test_repair_store_boundary.py
All checks passed!
```

All four figures match the packet. The 29 ruff errors are entirely outside the two touched
files, so the "unchanged from base" claim holds by construction, not by comparison.

---

## Findings

### F1 — Threshold 2's containment half is ungated, and the diff already violates it  [Severity: HIGH]

- **What:** `LLR-STO.1.1` threshold 2 requires that a refused container **"leaves that position
  `""` and appends a `campo ilegible:` record"**. The new tests certify only the second half. An
  implementation that *drops the offending entity entirely* — recording a warning — satisfies
  every assertion in the file. And `mapper/store.py:286` is exactly that: a non-`dict` attachment
  entry is silently discarded with **no `load_warnings` record at all**.

- **Where:** `mapper/store.py:284-287` (the `if isinstance(a, dict)` filter);
  `tests/test_repair_store_boundary.py:217-234` (`test_at_p02`, which cannot see a drop);
  `tests/test_repair_store_boundary.py:277-283` (`_MALFORMED_SHAPES`).

- **Evidence — live behaviour (silent drop, no record):**

  ```
  attachments -> [Attachment(kind='img', path='p', caption='')]   warnings -> []
  # input: attachments: [{kind: img, path: p}, 'junk', 42, None]
  # three entries destroyed, load_warnings empty
  ```

- **Evidence — surviving mutant.** In a detached copy of the tree (never the live repo) I
  replaced the filter with one that refuses a container by **dropping** the attachment after
  appending the warning:

  ```python
  # MUTANT: refuse a container by DROPPING the attachment, warning first
  def _drop_att(graph, nid, a) -> bool:
      bad = [k for k, v in a.items() if isinstance(v, (dict, list, set, tuple))]
      for k in bad:
          graph.load_warnings.append(f"campo ilegible: {nid}.{k}")
      return bool(bad)
  ```

  ```
  control (unmutated copy):
  $ pytest -q -p no:randomly tests/test_store.py tests/test_repair_fields.py \
        tests/test_repair_cycles.py tests/test_repair_store_boundary.py
  139 passed, 1 deselected in 7.62s

  mutant:
  139 passed, 1 deselected in 7.47s

  mutant, boundary file alone:
  57 passed in 1.83s
  ```

  **0 of 139 arms reddened, including all 57 new arms.** The `"leaves that position `""`"`
  clause has no gate.

- **The corroborating omission.** `_MALFORMED_SHAPES`
  (`tests/test_repair_store_boundary.py:277-283`) enumerates `nodes-is-a-list`,
  `node-is-a-scalar`, `schema-is-a-mapping`, `schema-item-is-a-scalar`,
  `document-item-is-a-scalar` — and **not** `attachment-item-is-a-scalar`. Every sibling family's
  "item is a scalar" case is present; the one family whose scalar item is silently swallowed is
  the one missing. That is a gap, not a decision.

- **Why it matters:** `US-N13`'s «sala» loads every map on mount. An attachment silently deleted
  at load is deleted from disk on the next `save` — the store's own read side is the only thing
  that reconstructs `_build_sidecar`'s input. Silent destruction of operator data is worse than
  the crash this batch replaced, and the batch's own threshold anticipated it. Separately, the
  test cannot distinguish "refused and left empty" from "refused and destroyed" for **any**
  family, so threshold 2 is half-certified across the board.

- **Suggested fix (both limbs required):**

  1. Record the refusal instead of dropping, following the module's own precedent at
     `mapper/store.py:262-266`:

     ```python
     attachments=[
         Attachment(**_coerce_text_fields(graph, nid, Attachment, a))
         for a in _dict_items(graph, nid, "attachments", ndata.get("attachments", []))
     ],
     ```
     with a small helper that appends `f"campo ilegible: {nid}.attachments"` for each
     non-mapping entry before filtering it out — same shape, same Spanish, same sink as the
     `fields` guard two blocks above.

  2. Add an arm that pins *presence*, not only *type*. Today `test_at_p02` asserts
     `offenders == []`, which a drop satisfies vacuously. Assert the poisoned position is still
     observed and is the empty string:

     ```python
     live = _live_text_values(graph)
     assert (position, "") in live, (
         f"{position} was DROPPED, not left empty -- threshold 2 requires the position "
         "to survive as '' so coverage() keeps counting it as undocumented"
     )
     ```
     and add `"attachment-item-is-a-scalar"` to `_MALFORMED_SHAPES`' sibling set (as a
     `load_warnings` arm, since the correct behaviour there is refuse-and-record, not raise).

---

### F2 — `_coerce_text_fields` overrides the dataclass default, silently regressing `kind`  [Severity: MEDIUM]

- **What:** `data.get(name, "")` hard-codes `""` for a MISSING key. Two of the swept fields do
  not default to `""`: `SchemaField.kind = "text"` and `Document.kind = "text"`. A sidecar that
  omits `kind` used to yield `"text"` and now yields `""`. The value is then persisted by the
  next `save`, because `_build_sidecar` writes `f.kind` / `d.kind` verbatim.

- **Where:** `mapper/store.py:82-85`; defaults at `mapper/model.py:14` and `mapper/model.py:86`;
  the replaced call sites were `f.get("kind", "text")` and `d.get("kind", "text")`
  (diff `-` lines). Note `create_from_template` at `mapper/store.py:410` still spells
  `f.get("kind", "text")`, so the two paths now disagree.

- **Evidence — measured on both refs, same input:**

  ```
  BASE d877784: schema.kind -> 'text'      document.kind -> 'text'
  HEAD          schema.kind -> ''          document.kind -> ''
  # sidecar: schema: [{key: E, label: estado, required: true}]   (no `kind`)
  #          documents: [{name: d1, source: s}]                  (no `kind`)
  ```

  The regression is introduced by this diff. It is **uncovered**: `BASE_SIDECAR`
  (`tests/test_repair_store_boundary.py:30-53`) carries `kind` in every entry, so no arm can
  reach the missing-key path.

- **Why it matters:** `mapper/screens/factory.py:291` renders `f"[{doc.kind}] "` — the badge
  becomes `[] `. More importantly the drift is written back to disk, so a hand-edited or legacy
  sidecar is silently rewritten. This behaviour change is not derivable from `LLR-STO.1.1`,
  which asks for coercion of present values, not re-defaulting of absent ones.

- **Suggested fix (verified — reddens nothing):**

  ```python
  import dataclasses
  specs = cls.__dataclass_fields__
  out = {}
  for name in _text_fields(cls):
      default = specs[name].default
      if default is dataclasses.MISSING:
          default = ""
      out[name] = _coerce_field(graph, owner, name, data.get(name, default))
  return out
  ```

  ```
  $ pytest -q -p no:randomly tests/test_store.py tests/test_repair_fields.py \
        tests/test_repair_cycles.py tests/test_repair_store_boundary.py
  139 passed, 1 deselected in 10.81s
  with fix: schema.kind= 'text'   document.kind= 'text'
  ```

  Add one arm poisoning by **omission** rather than by type — the census only poisons values,
  so absence is a shape it structurally cannot reach.

---

### F3 — Coercing field keys collides two keys into one and loses a field, silently  [Severity: MEDIUM]

- **What:** `_coerce_field(...)` is now applied to the field **key**. Two distinct raw keys can
  coerce to the same string; the dict comprehension keeps the last and destroys the first, with
  no `load_warnings` record.

- **Where:** `mapper/store.py:272-279`.

- **Evidence:**

  ```
  input fields: {1: 'from-int', '1': 'from-str'}
  BASE d877784 -> {1: 'from-int', '1': 'from-str'}      (2 fields)
  HEAD         -> {'1': 'from-str'}                     (1 field)
  warnings     -> []
  ```

  Also reachable through refusal: every key that hits the refusal branch coerces to `""`, so
  *n* unreadable keys collapse into one entry.

- **Why it matters:** silent data loss on round-trip — the surviving key is written back and the
  other is gone from disk. `coverage()` is unaffected here (both `.get("1")` lookups already
  resolved to the `str` key), so this is a data-fidelity defect, not a miscount. Answering the
  question directly: the key coercion itself is correct and required; **the missing collision
  record is the defect.**

- **Suggested fix:** build the dict explicitly and record the collision through the same sink:

  ```python
  coerced_fields: dict[str, str] = {}
  for key, value in raw_fields.items():
      ckey = _coerce_field(graph, nid, "key", key)
      if ckey in coerced_fields:
          # Two raw keys coerced to one string; keeping the last silently deletes
          # the first from the file on the next save.
          graph.load_warnings.append(f"campo duplicado: {nid}.{ckey}")
      coerced_fields[ckey] = _coerce_field(graph, nid, str(key), value)
  ```

---

### F4 — The node-id comment claims a repair the code does not perform  [Severity: MEDIUM]

- **What:** the WHY comment states that leaving the id raw *"produces a phantom duplicate node
  … silently moving `coverage()`'s denominator."* Coercion does **not** remove the phantom. It
  only changes the phantom's key type. Worse, a *refused* id now produces a node with id `""`,
  and several refused ids collapse onto it, overwriting each other's fichas.

- **Where:** `mapper/store.py:251-258`.

- **Evidence:**

  ```
  sidecar nodes: {A: {...}, 12345: {title: ghost}}
  HEAD -> node ids ['A', 'B', '12345']   len(graph.nodes) = 3   warnings []

  sidecar nodes: {A: {...}, !!binary "aGk=": {title: ghost1}, !!binary "aGk3": {title: ghost2}}
  HEAD -> nodes ['A', 'B', '']
          graph.nodes[''].ficha.title == 'ghost2'      # ghost1 silently overwritten
          coverage() == (1, 3)                          # denominator still moved
          warnings ['campo ilegible: node.id', 'campo ilegible: node.id']
  ```

- **Why it matters:** the batch's own culture (C-48) treats a false record as a defect in the
  evidence. A comment asserting a consequence the change does not have is the highest-cost kind
  of comment: the next reader will not re-measure it. No arm observes node **count**, so nothing
  contradicts the claim either.

- **Suggested fix:** either narrow the comment to what the change actually does — *the id is
  normalised to `str` so the sidecar's key type cannot vary; the phantom node itself is out of
  this batch's fence* — or, if the phantom is meant to be repaired, skip a node whose id was
  refused (`if not nid: continue`, mirroring the `documents` guard at `:239`) and say so. Do not
  leave the comment as written.

---

### F5 — `_KEY_POSITIONS`' justification is narrower than the exclusion it grants  [Severity: MEDIUM]

- **What:** the exclusion block argues *"a container cannot occupy a MAPPING KEY … thresholds 2
  and 3 are therefore structurally inapplicable to the two key positions"*. That argument covers
  **containers**, but the exclusion removes the positions from every threshold-2/3 arm. A
  non-container, non-scalar, **hashable** value does occupy those positions through ordinary
  YAML, and does exercise `_coerce_field`'s refusal branch.

- **Where:** `tests/test_repair_store_boundary.py:76-85` and
  `tests/test_repair_store_boundary.py:163-182` (`test_tc_p01c`).

- **Evidence:**

  ```yaml
  nodes: {A: {title: a, fields: {!!binary "aGk=": v}}}
  ```
  ```
  fields -> {'': 'v'}      warn -> ['campo ilegible: A.key']
  ```
  ```yaml
  nodes: {!!binary "aGk=": {title: a}}
  ```
  ```
  nodes -> ['A', 'B', '']  warn -> ['campo ilegible: node.id']
  ```

  Both key positions reach the refusal branch, are refused, and are recorded — so the behaviour
  is right, but it is certified by nothing.

- **Answering the question posed:** `test_tc_p01c` is **not vacuous** — it executes real
  assertions (the `TypeError: unhashable` on the two key routes, the poisonability of every other
  position, and the partition). But it does **not fully justify the exclusion**: it proves the
  container half of the claim and grants an exclusion covering the whole refusal branch.

- **Suggested fix:** narrow the exclusion to the poison *value* rather than the position — keep
  the two positions in thresholds 2 and 3, parametrised with a hashable refusable poison
  (`b"hi"`, or a `frozenset`) — or add two explicit arms asserting `campo ilegible: <nid>.key`
  and `campo ilegible: node.id` for a `bytes` poison, and amend the docstring to say the
  exclusion is *container-specific*, not refusal-branch-wide.

---

### F6 — `test_at_p02`'s warning assertion is truthiness-only  [Severity: MEDIUM]

- **What:** threshold 2 requires *a `campo ilegible:` record* for the poisoned position. The
  assertion is `assert graph.load_warnings` — non-emptiness. It cannot see a record with the
  wrong owner, the wrong key, or the wrong count.

- **Where:** `tests/test_repair_store_boundary.py:231-234`. Compare the codebase's own stronger
  precedent at `tests/test_repair_fields.py:134`, `:147`, `:161` (exact list equality).

- **Why it matters:** there is a live mislabel this weak form cannot see (`F7`), and the whole
  point of threshold 2 is that the record is what stops the silent miscount. A record naming the
  wrong field is not much better than no record.

- **Suggested fix:** assert content, in the module's existing style —
  `assert any(position.split(".")[-1] in w for w in graph.load_warnings)`, or better, pin the
  expected string per family the way `test_tc_p19` does.

- **Related, same test, LOW:** `test_at_p01[document.name]` poisons with `12345`, which is
  truthy, so the `if not d.get("name")` guard at `mapper/store.py:239` is never exercised. A `0`
  name drops the document entirely and the arm still passes (no surviving position to offend).
  The guard's falsy-drop is **pre-existing** — base spelled `if d.get("name")` — so it is not a
  regression, but the arm is weaker than it reads.

---

### F7 — The field-key warning label is a literal, so every bad key reports the same position  [Severity: LOW]

- **What:** `mapper/store.py:275` passes the literal `"key"` as the warning label, while
  `:276` passes `str(key)` for the value. A refused key therefore always records
  `campo ilegible: <nid>.key` with no way to tell which key.

- **Where:** `mapper/store.py:275-277`.

- **Evidence:** the `bytes`-key probe under `F5` produced `campo ilegible: A.key` — the literal,
  not the offending key.

- **Answering the question posed:** the two different `key` arguments are **deliberate in shape**
  (a refused key has no faithful text form, so `str(key)` would be misleading) but the result is
  a diagnostic that cannot distinguish cases. Not a correctness bug; a diagnostic one.

- **Suggested fix:** `_coerce_field(graph, nid, f"key[{key!r}]", key)` — `repr` is honest about
  the raw form without claiming it is text. Also note the owner strings are inconsistent across
  the diff: `"schema"` / `"document"` / `"node"` (literals) at `:232`, `:242`, `:256` but `nid`
  at `:269`, `:275`, `:284`. `campo ilegible: schema.key` cannot be traced to which schema entry.
  Consider `f"schema[{i}]"`.

---

### F8 — The two nets are inconsistent, and one interpolates the raw exception into a Spanish operator message  [Severity: LOW]

- **What:** `mapper/store.py:343-345` produces a fixed Spanish notice; `mapper/store.py:351-352`
  produces `f"no se pudo indexar {map_id}: {exc}"`, splicing an arbitrary exception's `str` —
  which for `sqlite3` and `OSError` routinely carries a filesystem path — into UI text.

- **Where:** `mapper/store.py:343-345` vs `:351-352`.

- **Suggested fix:** pick one shape. Either both fixed-Spanish, or both carrying
  `type(exc).__name__` (a type name is diagnostic without leaking a path).

---

### F9 — `except Exception` masks programming errors, and there is no log to recover them  [Severity: LOW — accepted trade, recorded]

- **What:** an `AttributeError` from a typo inside `_graph_from_sidecar` becomes the same
  Spanish "ilegible" notice as a genuinely malformed sidecar, for **every** map. `grep -rn
  "logging\." mapper/` returns **0 hits**, so nothing preserves the traceback for the operator.

- **Where:** `mapper/store.py:332`, `mapper/store.py:350`.

- **Verified correct:** `raise ... from exc` does preserve the chain —
  `tests/test_repair_store_boundary.py:300-304` asserts `__cause__` is non-`None` and not a
  `MapStoreError`, which is the right way to prove the net was traversed. The clause ordering is
  correct in **both** places: `except MermaidError` (a `ParseError`, `mapper/mermaid.py:17` —
  *not* a `MapStoreError` subclass) → `except MapStoreError: raise` → `except Exception`.

- **Assessment:** this is the deliberate trade `LLR-STO.1.1` threshold 3 asks for, and I agree
  with it — a typed refusal degrading to a notice beats an untyped one killing the mount. It is
  recorded, not blocked. `F8`'s fix (carry `type(exc).__name__`) is the cheapest mitigation and
  does not require introducing a logging facility this codebase does not have.

---

## Verified clean — stated explicitly, not by omission

**The coercion generalization is sound (question 1).** `mapper/model.py:2` has
`from __future__ import annotations`, so `spec.type` is the **string** `'str'`; the
`in ("str", str)` filter handles both forms and I confirmed which one is live:

```
Ficha       ('title', 'state', 'meta', 'notes')       4
Attachment  ('kind', 'path', 'caption')               3
SchemaField ('key', 'label', 'kind')                  3
Document    ('name', 'source', 'path', 'kind')        4
                                                     14  + 3 structural = 17
```

Exactly the census figure. Nothing is wrongly swept in — `required` / `template` (`'bool'`) and
`fields` / `attachments` / `tags` / `inherited` (`'dict[…]'`, `'list[…]'`) are correctly
excluded — and no text field is missed. *Latent fragility worth one line:* the filter is a
**textual** comparison under PEP 563, so a future `str | None`, `Optional[str]`, `Text`, or a
`str` alias would silently fall out of the derivation. `test_tc_p01`'s `assert len(positions) >= 17`
is the only assertion that would catch that shrink (the `expected` computation reuses the same
derivation and is self-consistent by construction). The literal `17` is doing real work there;
that is honest and correct, and worth keeping.

**The `_live_text_values` walk is complete (question 6).** Measured against the derivation on
the clean map:

```
derived  : 17
observed : 17
NOT observed by walk -> []
observed but not derived -> []
```

Every position the census claims is observed. *Caveat already priced into `F1`:* the walk
observes only positions that **survive** into the graph, which is precisely why a drop is
invisible to it.

**The `Document` loop rewrite is correct (question 2).** Keying by the coerced `doc.name`
instead of the raw `d.get("name","")` is the right change — the raw key was the
`document.name → TypeError` cell of the census. The `if not d.get("name")` guard's falsy-drop
(`0` dropped, `5` → `"5"`) is **pre-existing**: base spelled `if d.get("name")` in the
comprehension filter, so behaviour is unchanged. Consistency with the requirement is fine —
threshold 1 asks for no non-`str` positions, and a dropped document contributes none — but see
the `F6` addendum on the arm's weakness.

**Reverse census (C-26) — clean, per file.**

| Symbol | Where in `tests/` | Verdict |
|---|---|---|
| `_text_attributes` | `test_repair_fields.py:18` (import), `:56`, `:340` | ✅ retained as a shim at `store.py:42-44`; all three sites still resolve. The shim earns its keep. |
| `_text_fields` | — no references | ✅ new symbol, no prior contract |
| `_coerce_field` | `test_repair_fields.py:660`, `:665` — **prose only**, in docstrings | ✅ no assertion binds it |
| `_coerce_text_fields` | — no references | ✅ new symbol |
| `_graph_from_sidecar` | — no test references | ✅ (but see scope note below) |
| `_reindex` | `test_repair_fields.py:203` (prose), `test_repair_store_boundary.py:329` (`monkeypatch.setattr`) | ✅ signature unchanged, monkeypatch still binds |
| `MapStoreError` | `test_store.py:39,53`; `test_repair_cycles.py:19,166,261,392,394`; `test_repair_fields.py:18,449,463,694` | ✅ all pass; no message-text assertion touched by the two new nets |
| `load_warnings` | `test_repair_fields.py:134,147,175` and **`:161` exact list equality**; `test_repair_store_boundary.py:231` | ✅ the two exact-equality assertions (`:161` sorted-list equality, `:175` `== []`) still hold — the new coercion adds **no** warning on a well-formed map, which `test_tc_p21` independently pins |

Executed: `139 passed, 1 deselected` across the four store-facing files; `470 passed` fast lane;
`16 passed` slow lane. **No existing assertion from another batch is invalidated.**

**Scope note (not a finding).** `_graph_from_sidecar` has two callers outside `load` —
`mapper/app.py:1536` (`_pop_snapshot`) and `mapper/diff.py:59` — neither covered by the new
nets. `mapper/diff.py:58-61` already wraps the call in `except Exception: return None`, so it is
safe. `mapper/app.py:1536` is unguarded, but its input is a snapshot the app produced from
`_build_sidecar`, so the hostile-input argument does not reach it. `LLR-STO.1.1` scopes threshold
3 to `MapStore.load`, so the diff conforms. Recording it because "the shapes we know" is the
claim the increment's own comment says was wrong before.

**Simplicity and conventions (question 8).** No over-engineering found. `_coerce_text_fields` is
four lines and used at three sites — it earns the abstraction. `_text_fields(cls)` generalising
`_text_attributes()` is the minimum change that removes the defect, and keeping the old name as
a shim rather than editing three test call sites is correctly surgical (Rule 3). The Spanish UI
strings, the `campo ilegible:` sink, and the docstring-carries-the-WHY convention all match the
surrounding module. Every comment added by the diff explains WHY, not WHAT — the one exception
is `F4`, where the WHY is wrong rather than absent.

---

## Evidence checklist

- [x] **Diff read in full** — `git diff mapper/store.py`, 5 hunks, `store.py:20-44`, `:71-85`,
      `:227-287`, `:318-323`, `:330-353`; plus `tests/test_repair_store_boundary.py:1-332`.
- [x] **Correctness pass (edge / None / error paths)** — 9 executed probes: missing-key defaults
      (`F2`), key collision (`F3`), non-dict / empty attachment (`F1`), falsy & container
      document name, phantom & colliding node ids (`F4`), `bytes` and unhashable YAML keys (`F5`).
- [x] **Simplicity pass** — no premature abstraction; the two new helpers are each used ≥3 times
      and are directly derivable from `LLR-STO.1.1`.
- [x] **Reuse / duplication checked** — the diff correctly reuses `_coerce_field` and the
      `load_warnings` sink rather than re-deriving them; `F1`/`F3`'s fixes are also reuse of the
      existing `store.py:262-266` precedent, not new machinery. One residual duplication:
      `create_from_template` (`store.py:405-413`) still hand-constructs `SchemaField` with the
      old `f.get("kind","text")` shape — out of this increment's fence, flagged for the batch.
- [x] **Tests reviewed for intent** — one HIGH (`F1`, proved by a surviving mutant across 139
      arms), two MEDIUM (`F5`, `F6`), one LOW addendum. `test_tc_p01b`'s positive control,
      `test_tc_p01`'s non-degeneracy guard, `test_at_p03b`'s `__cause__` assertion and
      `test_at_p03`'s honest PIN-not-gate relabelling are all genuinely strong and I want them
      on the record as such.
- [x] **Verdict explicit** — **BLOCKED** on `F1`.

## Could not verify

- **The six-mutant battery reported in the packet.** I re-ran one mutant of my own design and
  the two control runs it needed; I did not reproduce the packet's six. Its methodology
  (detached tree, junitxml per resolved node id, sha256 restore proof) is sound as described,
  and my own control/mutant pair is consistent with it — but the six verdicts are the author's
  measurement, not mine.
- **Whether any real map on disk carries a `kind`-less sidecar.** `F2`'s blast radius is
  therefore bounded by argument (`_build_sidecar` always writes `kind`; only hand-edited or
  legacy files can omit it), not by census.

---
---

# Re-review — Increment 1 (second pass)

**Reviewed:** `mapper/store.py` (full re-diff, 8 hunks) and `tests/test_repair_store_boundary.py`
(full re-read, 493 lines, 66 arms), after `software-dev` accepted the BLOCKED verdict.

## Verdict: OK WITH FIXES — `G1`, `G2`, `G3` applied before advancing

**Not blocked.** `F1`–`F8` are genuinely fixed, and I gated each one with my own mutants rather
than taking the battery on report. The three new findings are all *coverage holes with no live
defect behind them* — which is exactly what separates them from `F1`. `F1` was HIGH because the
shipped code **contained** the behaviour its tests could not see; here the implementation is
correct in every case the new arms fail to gate. Stating that distinction explicitly so this
reads as a threshold rather than a softening.

### Evidence re-verified (executed here, not read)

```
$ pytest -q -p no:randomly                  479 passed, 16 deselected   (claim 479/16 ✓)
$ pytest -q -p no:randomly --collect-only   479/495 collected           (ledger 495 = 429+66 ✓)
$ ruff check mapper/ tests/                 Found 29 errors             (unchanged ✓)
$ ruff check mapper/store.py tests/test_repair_store_boundary.py
                                            All checks passed!          ✓
```

Slow lane: see **Unresolved**, at the end. It did not reproduce cleanly.

---

## Ruling on the `_mappings` scoping decision (your Q1)

**I agree with you. Keep it attachments-only.** You were right to revert, and right to flag it.

I measured the asymmetry rather than reasoning about it:

```
schema-item-scalar       -> DENIED  MapStoreError: ...m_nodos.yml ilegible
document-item-scalar     -> DENIED  MapStoreError: ...m_nodos.yml ilegible
attachment-item-scalar   -> LOADS,  warnings=['campo ilegible: A.attachments']
```

The `F1` defect was **silent data loss**. That class does not exist in `schema`/`documents`: a
malformed item there is refused *loudly* and *typed*, the operator is told, and nothing is
destroyed. Routing them through `_mappings` would repair nothing, would change behaviour no
finding asked for, and would cost three arms off the typed net's own counterfactual — the same
C-55 mistake the first pass caught in `test_at_p03`. Engineering rules 2 and 3 both back the
revert.

**One condition on the ruling.** The `_mappings` docstring justifies the scoping in *mechanism*
terms ("escapes to the typed net, which is loud"). State it in *observable* terms too, because
that is what a reader is trying to predict: **one malformed attachment → the map loads with a
record; one malformed schema entry → the whole map is denied.** And carry the asymmetry to the
batch record as a known, deliberate divergence. It is a defensible line; it should not be an
undocumented one.

## Ruling on `nodo duplicado` / `campo duplicado` in-fence (your Q3)

**In-fence — repair, not scope creep.** The argument that decides it: coercing keys to `str` is
*what creates the collision*. You cannot implement threshold 1 at `fields.key` or `node.id`
without making two distinct raw keys collapse into one. Recording that repairs a defect the
required change introduces, which is inside the fence by construction — the same footing as
`F2`'s default preservation.

**`documento duplicado` is the partial exception, and you did not raise it.** In-fence for the
coercion-induced case by the identical argument, but it also fires on a case with no coercion in
it at all:

```
documents: [{name: d1, source: first}, {name: d1, source: second}]
-> warnings: ['documento duplicado: d1']
```

Two *literally* identical names silently overwrote each other before this diff and now produce a
record. A real improvement, and I would keep it — but it is a behaviour change outside the
coercion fence, it arrived unannounced in your summary, and it has **zero** test arms (`G3`).
Name it in the batch record.

---

## Findings

### G1 — the `F1` containment assertion is inert on 3 of its 15 arms  [Severity: MEDIUM]

- **What:** `assert (position, "") in live` searches the **whole graph**, not the poisoned
  entity. `MMD` declares `B[Beta]`, so `parse` gives node `B` an empty `Ficha` whose
  `state`/`meta`/`notes` are `""` unconditionally. Three arms therefore assert something already
  true before the poison is applied — C-40 limb 1, invariant under the change it gates.

- **Where:** `tests/test_repair_store_boundary.py:262-265` (the assertion), `:28` (`MMD`),
  `:43-53` (`BASE_SIDECAR` has no `B` entry).

- **Evidence — measured on a clean, unpoisoned load:**

  ```
  nodes in graph -> ['A', 'B']
  positions already paired with "" on a CLEAN load:  node.meta, node.notes, node.state
  container-poisonable arms satisfied WITHOUT the poison:
      ['node.state', 'node.meta', 'node.notes']   -> 3 of 15
  ```

  `node.title` escapes only because mermaid gives `B` the title `Beta`.

- **Evidence — mutant `M-RR1`** (destroy the node when a ficha text attr is refused — exactly the
  destroy-the-entity behaviour this limb exists to catch):

  ```
  control                                148 passed, 1 deselected
  M-RR1                                  1 failed, 147 passed
      FAILED ...test_at_p02[node.title]
      # node.state, node.meta, node.notes all PASS with the node destroyed
  ```

- **Why it matters:** you added this limb because `offenders == []` was vacuous. On three arms
  the replacement is vacuous in the same way for a different reason. The limb is real on the
  other 12 (see `M-RR2` below), so this is a hole, not a false claim.

- **Suggested fix — verified, and it is a fixture change, not new machinery.** Give `B` a sidecar
  entry so `""` can only mean *refused*:

  ```python
  # `B` exists in the MMD, so `parse` gives it an EMPTY ficha.  Its empty
  # state/meta/notes put ("node.state", "") in every walk unconditionally, which
  # made the containment assertion invariant under the poison on three arms.
  "B": {"title": "Beta", "state": "ok", "meta": "mb", "notes": "nb"},
  ```

  ```
  unmutated tree + this fixture        148 passed, 1 deselected    (stays green)
  M-RR1        + this fixture          4 failed, 144 passed
      node.title, node.state, node.meta, node.notes   -> 1 arm becomes 4
  ```

### G2 — the two new collision arms cannot see which record was emitted  [Severity: MEDIUM]

- **What:** `test_at_p02d` and `test_at_p02e` both assert `any("duplicado" in w ...)`. All three
  collision records (`campo duplicado`, `nodo duplicado`, `documento duplicado`) contain that
  substring, so no arm can tell them apart, nor see a corrupted payload. This is the same
  truthiness-class weakness `F6` was raised about, reintroduced in the arms written to close `F3`
  and `F4`.

- **Where:** `tests/test_repair_store_boundary.py:401-403`, `:412-415`.

- **Evidence — mutant `M-RR3`, the two nouns swapped and the payload corrupted:**

  ```python
  f"nodo duplicado: {nid}"         ->  f"campo duplicado: {nid}.WRONG"
  f"campo duplicado: {nid}.{ckey}" ->  f"nodo duplicado: {nid}.WRONG"
  ```
  ```
  66 passed in 2.38s        # 0 of 66 arms reddened
  ```

- **Suggested fix:** apply the discipline you already used for `_WARNING_FRAGMENT` — assert the
  full record, not a substring:

  ```python
  assert "campo duplicado: A.1" in graph.load_warnings, graph.load_warnings
  assert "nodo duplicado: " in graph.load_warnings, graph.load_warnings
  ```
  The second one also exposes `G4`: the record for the common refused-id collision is
  `nodo duplicado: ` with an empty id.

### G3 — `documento duplicado:` is a third collision record with no arm at all  [Severity: MEDIUM]

- **What:** the documents loop gained a collision record your summary did not mention and no test
  references. `grep -rn "documento duplicado" tests/` → **0 hits**.

- **Where:** `mapper/store.py`, the `if doc.name in documents:` branch of the documents loop.

- **Evidence — reachable in both modes:**

  ```
  documents: [{name: 1, source: first}, {name: '1', source: second}]
  -> docs {'1': 'second'}   warnings ['documento duplicado: 1']    # coercion-induced

  documents: [{name: d1, source: first}, {name: d1, source: second}]
  -> warnings ['documento duplicado: d1']                          # NO coercion involved
  ```

- **Why it matters:** it is the ungated sibling of `F3` and `F4`, which you *did* gate. An
  untested record can be deleted or mistyped by the next refactor with nothing reporting it — and
  the second mode is the small out-of-fence step ruled on above.

- **Suggested fix:** one arm mirroring `test_at_p02d`, asserting the full record, plus a line in
  the batch record for the literal-duplicate case.

### G4 — `_mappings` records are identical and un-indexed, against your own `F7` fix  [Severity: LOW]

- **What:** `F7` indexed every owner (`schema[i]`, `document[i]`, `{nid}.att[i]`,
  `key[{key!r}]`). `_mappings`' own refusal record was left un-indexed, so *n* malformed entries
  produce *n* byte-identical warnings.

- **Where:** the two `graph.load_warnings.append(f"campo ilegible: {owner}.{key}")` lines in
  `_mappings`; also the node-id owner is still the bare literal `"node"`.

- **Evidence:**

  ```
  attachments: [{kind: i, path: p}, 7, 'junk', None]
  -> ['campo ilegible: A.attachments',
      'campo ilegible: A.attachments',
      'campo ilegible: A.attachments']
  ```
  Compare, from the same load path: `campo ilegible: A.att[0].kind` — indexed, as `F7` asked.

- **Suggested fix:** `f"campo ilegible: {owner}.{key}[{i}]"` from an `enumerate`, and give the
  node-id owner the raw key's `repr` the way `key[{key!r}]` does.

---

## Verified fixed — each gated by my own mutant, not taken on report

| Finding | Fix reviewed | Independent gate I ran |
|---|---|---|
| **F1 limb 1** | `_mappings` records every refusal | **`M-RR4`** — `_mappings` reverted to the shipped silent filter → **3 failed, 63 passed**; all three `test_at_p02b` arms redden. Gated. |
| **F1 limb 2** | `(position, "") in live` | **`M-RR2`** (my original drop mutant) → **3 failed, 145 passed**: `attachment.kind`, `attachment.path`, `attachment.caption`. Gated — **3 arms, not the 2 your summary reports**; worth reconciling against `M-STO-g`'s shape. Partially inert on 3 other arms → `G1`. |
| **F2** | `specs[name].default`, `MISSING` fallback | `test_at_p01b` asserts `observed == "text"` for `schema.kind` and `document.kind` by **omission** — a shape the value census cannot reach. Real gate; probe confirms absent `kind` → `'text'` on both. |
| **F3** | explicit loop + `campo duplicado` | Record confirmed live. Arm exists but is weak → `G2`. |
| **F4** | comment corrected + `seen_ids` | The comment now states plainly that coercion normalises the key **type** and **does not** remove the phantom. That is the honest form. Collision recorded; arm weak → `G2`. |
| **F5** | container-specific wording + `test_at_p02c` | `bytes` poison drives both key positions; verified `campo ilegible: A.key[b'hi']` and `campo ilegible: node.id`. The no-non-`str` assertion means an uncoerced key reddens it. Real gate. |
| **F6** | `_WARNING_FRAGMENT` + totality assertion | **The best work in this pass.** You found that the naive `position.split(".")[-1]` false-fails a *correct* implementation on `fields.value`, whose record is keyed by the field key (`campo ilegible: A.E`). A reviewer-suggested fix that would have false-failed is worse than the weak assertion it replaced, and you caught it, declared it in the comment, and guarded totality at `:202-204` instead of quietly routing around it. |
| **F7** | owners indexed | Verified: `schema[0].kind`, `document[0].name`, `A.att[0].kind`, `A.key[b'hi']`. Residual → `G4`. |
| **F8** | `type(exc).__name__` | Verified in the diff; no `{exc}` reaches operator text, chain survives on `__cause__`. |
| **F9** | unchanged, accepted | Still the right trade. |

## Reverse census — the new diff's symbols and message formats (your Q4)

**No existing test pins a changed string.** The owner-string change is safe — and here is *why*,
not just *that*:

| Pin | File:line | Form pinned | Touched by the owner change? |
|---|---|---|---|
| `"campo ilegible: root.D"` | `test_repair_fields.py:134`, `:376` | `{nid}.{field_key}` | **No** — field *values* still use `_coerce_field(graph, nid, str(key), value)`, unchanged |
| `"campo ilegible: root.fields"` | `test_repair_fields.py:147` | `{nid}.fields` | **No** — that guard is untouched |
| `["campo ilegible: a.O", "campo ilegible: root.D"]` | `test_repair_fields.py:161-163` | exact sorted list | **No** |
| `== ["campo ilegible: a.O"]` | `test_repair_fields.py:258` | **exact list equality** | **No**, but see the note below |
| `not any("campo ilegible" in n …)` | `test_repair_fields.py:403` | prefix only | **No** |
| `"no se pudo leer la ficha"` | `test_repair_fields.py:698` | unchanged message | **No** |

Only `schema[i]` / `document[i]` / `{nid}.att[i]` / `key[{key!r}]` changed, and nothing pins those
forms. New symbols: `_mappings`, `seen_ids`, `coerced_fields` → **0** references in `tests/`
(correctly private). `_WARNING_FRAGMENT` 5, `_MALFORMED_ITEM_LISTS` 3, `_HASHABLE_REFUSABLE` 2 —
all self-references inside the new file.

**One fragility to note, not a finding:** `test_repair_fields.py:258` is exact list equality on
`load_warnings`, and three new record types now append to that same list. It passes today because
that fixture triggers none of them, but any future scenario in another batch that emits a
`duplicado` record into an exact-equality fixture will break *there* rather than where the change
was made. Worth a line in the batch record.

## New vacuous arms introduced? (your Q2)

Audited all 66 arms. **One partial vacuity (`G1`, 3 arms) and one weak-assertion pair (`G2`).**
Everything else is sound. Specifically checked and found *not* vacuous: `test_at_p02b` ×3 (gated
by `M-RR4`), `test_at_p02c` ×2 (the no-non-`str` assertion carries them), `test_at_p01b` ×2
(direct equality against the dataclass default), `test_tc_p01c`'s totality assertion, and the
`_WARNING_FRAGMENT` content check on the 12 non-`node.*` arms.

Two residual fragilities, both LOW and both fine to leave: `_WARNING_FRAGMENT["fields.value"]` is
the single character `"E"`, specific enough only because no Spanish record contains an uppercase
E today; and `test_at_p02`'s content check scans *all* warnings rather than the one for the
poisoned position, safe only because exactly one poison is applied per arm.

## Unresolved — reported, not smoothed over

**One slow-lane run failed and I could not reproduce or identify it.** My first execution
returned `1 failed, 15 passed, 479 deselected`; **eight** subsequent runs all returned
`16 passed`. My first command discarded the `FAILED` line before I saw it, so **I cannot name the
test**, and I have not established whether it is pre-existing at `d877784` or introduced here.

This does not change the verdict — the 16 slow tests are pre-existing and none is in this
increment's fence — but your packet reports the slow lane as `16 passed … exit 0`, and I saw it
red once in nine (1/9 ≈ 11%). Treat it as an open item: identify the flake, or record it as a known
intermittent **before** Inc-3 lands `LLR-PERF.1` into that same lane, where a timing-sensitive
fixture will make an unidentified flake much more expensive to diagnose.

## Evidence checklist (re-review)

- [x] **Re-diff read in full** — `mapper/store.py` 8 hunks; `tests/test_repair_store_boundary.py`
      493 lines / 66 arms.
- [x] **Correctness pass** — 6 executed probes: `documento duplicado` both modes, `_mappings`
      multi-refusal, attachment owner labels, the schema/document/attachment asymmetry, the
      clean-load `""` census.
- [x] **Simplicity pass** — `_mappings` is 12 lines, one call site, directly traceable to `F1`;
      no speculative generality. The `enumerate` additions are the minimum `F7` needed.
- [x] **Reuse / duplication** — the new records reuse `graph.load_warnings`; no new sink invented.
- [x] **Tests reviewed for intent** — 4 mutants (`M-RR1`–`M-RR4`) plus 2 controls; 3 findings.
- [x] **Reverse census re-run** — 6 symbols + 6 message-format pins, table above.
- [x] **Verdict explicit** — **OK with `G1`, `G2`, `G3` applied first.** No HIGH; not blocked.

---
---

# Confirmation pass — Increment 1

**Reviewed:** `mapper/store.py` re-diff and `tests/test_repair_store_boundary.py` (572 lines,
70 arms), after `G1`–`G4` landed. Five mutants (`N1`–`N5`) plus a control, in detached copies.

## Verdict: **PASS** — Increment 1 is clear to advance

`G1`–`G4` are fixed, and each is gated by a mutant I built rather than by the battery's report.
Two LOW observations below; neither blocks, and both are follow-ups rather than another gate
cycle.

### Evidence re-verified

```
$ pytest -q -p no:randomly                  483 passed, 16 deselected   (claim 483/16 ✓)
$ pytest -q -p no:randomly --collect-only   483/499 collected           (ledger 499 = 429+70 ✓)
$ ruff check mapper/ tests/                 Found 29 errors             (= base ✓)
$ ruff check mapper/store.py tests/test_repair_store_boundary.py
                                            All checks passed!          ✓
control, four store-facing files            152 passed, 1 deselected
```

---

## Your Q1 — is `G1` actually live, or did the inertness move?

**Live, and it did not move.** Two independent measurements.

**First, the fixture property itself.** On a clean load of the new `BASE_SIDECAR`:

```
positions ALREADY paired with "" on a CLEAN load  ->  []        (was: node.state/meta/notes)
container arms satisfied WITHOUT the poison       ->  []  = 0 of 15
load_warnings on clean map                        ->  []
```

Then, per arm, the count of `(position, "")` pairs in the poisoned load:

```
fields.value 1   node.title 1   node.state 1   node.meta 1   node.notes 1
attachment.kind 1   attachment.path 1   attachment.caption 1
schema.key 1   schema.label 1   schema.kind 1
document.name 1   document.source 1   document.path 1   document.kind 1
```

**Exactly one source for every arm** — stronger than non-vacuity: the `""` the assertion observes
is now uniquely attributable to the poisoned entity. Nothing else in the graph can satisfy it.

**Second, the mutant this limb exists for.** `N1` destroys the node when a ficha text attr is
refused — the destroy-the-entity behaviour, not the refusal-value behaviour `M-RR2` moves:

```
control   152 passed, 1 deselected
N1        4 failed, 148 passed
   test_at_p02[node.title]  [node.state]  [node.meta]  [node.notes]
```

**1 arm → 4.** Before the fixture fix `N1` reddened only `node.title`. And `N2` (destroy the
attachment) still reddens its three:

```
N2        3 failed, 149 passed
   test_at_p02[attachment.kind]  [attachment.path]  [attachment.caption]
```

A note on your proof rather than a criticism of it: `M-RR2` (refusal returns `"?"`) reddens all
15, but it mutates the *refusal value*, which the `offenders`/repr assertions would also have
caught in weaker form. `N1` isolates containment specifically. Both belong in the battery; `N1`
is the one that would have caught `G1`.

## Your Q3 — is `test_at_p02f` a sound negative control?

**Sound, and it does unique work.** I checked the thing that would have made it decorative —
whether some existing test already covers it.

`N3` (all three collision guards → `if True`) reddens 4 arms, three of them in
`test_repair_fields.py`, so at first look `test_at_p02f` reads as redundant. It is not. `N4`
mutates **only** the documents guard:

```
N4        1 failed, 151 passed
   test_at_p02f_a_well_formed_map_records_no_collision
```

**Exactly one arm in the whole tree, and it is yours.** Nothing else reaches an unconditional
`documento duplicado`. The control is not papering over anything — it is the only thing standing
between that guard and a mutation that fires it on every clean map.

## Your Q2 — ruling on `documento duplicado`

**Keep it. Do not revert.** You offered to, and the reason belongs on the record, not just the
answer.

The decisive argument is not "it is one line" — it is that **the in-fence half and the
out-of-fence half are the same check.** `if doc.name in documents:` fires for the
coercion-induced collision (unambiguously in-fence: the coercion is what creates it) and for the
plainly-identical one. Separating them would mean carrying raw names alongside coerced ones —
*more* code, in order to deliberately preserve a known silent overwrite. Reverting the superset
would be the less simple and less correct option, and Rule 3's "surgical" does not mean
"reintroduce a defect to keep the diff tidy".

It is correctly handled: declared at the call site, recorded in the packet and the decision log,
and now carrying two arms. That is what an out-of-fence addition should look like.

## Count reconciliation — you are right, I withdraw the discrepancy

Verified. `M-STO-g` drops the entry **silently** → the *record* arms (`test_at_p02b`).
`N1`/`M-RR1` **destroys** the entry → the *containment* arms (`test_at_p02`). Disjoint arm sets,
different mutants, both counts right. My re-review flagged this as "one of us has the wrong
count"; neither of us did.

---

## Findings

### C1 — `_poison`'s node.id comment claims an invariant it does not fully deliver  [Severity: LOW]

- **What:** the comment says re-keying `A` only preserves `B`, "or the fixture's whole point (a
  sibling with no empty positions) would be undone by the poison." Preserving `B` is necessary
  but not sufficient: re-keying `A` removes `A` from the sidecar, so the **parsed** `A` loads
  with a default empty `Ficha` and the empty positions come straight back.

- **Where:** `tests/test_repair_store_boundary.py:143-146`.

- **Evidence:**

  ```
  poison=12345  nodes=['A','B','12345']  positions=="" -> ['node.state','node.meta','node.notes']
  poison=b'hi'  nodes=['A','B','']       positions=="" -> ['node.state','node.meta','node.notes','node.id']
  ```

- **Why it matters — and why it is LOW:** harmless today, because `node.id` is in
  `_KEY_POSITIONS` and never reaches the containment assertion. But it is the `F4` class: a
  comment asserting a property the code does not have, in the exact spot a future reader would
  rely on it. If `node.id` ever joined `_container_poisonable`, that arm would be born inert and
  the comment would say it could not be.

- **Suggested fix:** comment only, no code change. Say what it does — *preserves `B`; note that
  the parsed `A` still loads with a default ficha, which is why `node.id` stays out of the
  containment arm.*

### C2 — the boundary file's own record checks are still substring-based  [Severity: LOW]

- **What:** you applied exact-record discipline to `_MALFORMED_ITEM_LISTS` and `_COLLISIONS`, but
  `test_at_p02`'s `_WARNING_FRAGMENT` check and `test_at_p02c`'s `leaf in w` remain substring
  tests. Neither can see a corrupted *owner* coordinate while the leaf survives.

- **Where:** `tests/test_repair_store_boundary.py:288-291`, `:425-428`.

- **Evidence — `N5`, owner coordinate destroyed, leaf left intact:**

  ```python
  f"campo ilegible: {node_id}.{key}"  ->  f"campo ilegible: XXXX.{key}"
  ```
  ```
  N5   8 failed, 144 passed
       ALL 8 in tests/test_repair_fields.py
       ZERO in tests/test_repair_store_boundary.py
  ```

- **Why it matters — and why it is LOW:** the tree *is* covered, so this is not a gap in the
  product's guarantees. But every arm that catches it lives in **another batch's file**, so this
  increment's own suite is not self-sufficient on the property `F6` was raised about. A coupling
  worth knowing about, not a defect.

- **Suggested fix:** give `_WARNING_FRAGMENT` the full expected record rather than the leaf, the
  way `_COLLISIONS` now does. Cheap, and it makes the file stand on its own.

## Slow-lane flake — accepted, and your caveats are worth more than the identification

You identified what I could not:
`test_repair_depth.py::test_at_r16b_the_factory_screen_survives_a_depth_5000_map_composed`,
`WaitForScreenTimeout`. I confirmed the mechanism exists as described —
`FACTORY_TREE_BOUND_SECONDS = 8.0` at `tests/test_repair_depth.py:78`, wall-clock assertions at
`:1236` and `:1270`, both in `test_repair_depth.py`, neither touched by this diff.

Declaring that your one failure in ten landed on the run overlapping your own load experiment —
so you **induced** it rather than observing it spontaneously — is the difference between evidence
and a coincidence dressed as evidence. Same for noting the runs straddled a test-file edit. Keep
both in the backlog item; a future reader needs them to know the 10% is not a clean measurement.

Agreed it is out of fence and belongs on the backlog. The 2.4–3.0× unloaded headroom is the
figure that should drive its priority before `LLR-PERF.1` lands in that lane.

## Evidence checklist (confirmation pass)

- [x] **Re-diff read in full** — `mapper/store.py`; `tests/test_repair_store_boundary.py` 572
      lines / 70 arms.
- [x] **Correctness pass** — clean-load `""` census, per-arm attribution count, `_poison` node.id
      B-survival probe, slow-lane mechanism located.
- [x] **Simplicity pass** — no new abstraction; `_COLLISIONS` and `_MALFORMED_ITEM_LISTS` are
      data tables, which is the right shape. The `sibling_survives=False` flag on
      `attachments-is-a-scalar` is correctly reasoned: asserting a survivor there would demand
      behaviour the input makes impossible (C-53) — the same lesson as `F6`.
- [x] **Reuse / duplication** — no new sink; every record goes through `graph.load_warnings`.
- [x] **Tests reviewed for intent** — 5 mutants (`N1`–`N5`) + control; 2 LOW findings.
- [x] **Reverse census re-run** — no test outside the boundary file pins any new record format.
      The `duplicado` hit at `tests/test_keymap.py:151` is an unrelated `KeyBinding` label; the
      `schema[0]` hits at `tests/test_store.py:22` and `tests/test_worklist_safety.py:50,53` are
      Python indexing, not warning strings.
- [x] **Verdict explicit** — **PASS.**

## Could not verify

- **The 17-mutant battery.** I ran 5 of my own with controls; the 17 verdicts remain your
  measurement. Every one of mine agreed with the corresponding claim.
- **Whether the slow-lane flake is pre-existing at `d877784`.** Neither of us executed it at the
  base ref. The mechanism is untouched by this diff — strong circumstantial evidence, not a
  measurement.
