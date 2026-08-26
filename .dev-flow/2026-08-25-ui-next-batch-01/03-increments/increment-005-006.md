# Increments 5 & 6 — US-N04 coverage worklist · US-N05 destructive-action safety

**Cut together, and declared as such.** The plan had these as separate increments. They share
`mapper/app.py` and one fixture, and together they touch **3 source files** — inside the budget,
where cutting them apart would have meant two increments each editing the same file for related
reasons. Recorded here rather than presented as the original plan.

## 1 · What changed

### US-N04 — the coverage worklist

- **`↵` on a coverage row now jumps AND focuses the gap.** `_goto_gap` moves the cursor, reveals the
  inspector if it was collapsed, and puts keyboard focus on the **first missing required field** —
  not on `schema[0]`. On a node with `documento` filled and `dueño` empty, focus lands on `dueño`.
- **`n` cycles "next missing field" across the whole map**, in the coverage report's own traversal
  order, so "next" in the worklist means the same thing as "next row" in the report. It wraps once.
- **A complete map says so.** The report's empty state is no longer a fake selectable row that `↵`
  dismissed in silence; the table is hidden and a sentence replaces it. `action_next_gap` on a
  complete map reports exhaustion and leaves the cursor alone.
- **The report names fields in words.** `_missing_keys` returned `["O"]`; it now returns
  `["dueño"]`, consuming `Ficha.missing_required` — the model's single owner. A "missing" column
  reading `D,O` tells the operator nothing about what to go and fill in.

### US-N05 — safety

- **Every archive is confirmed, root or not.** A non-root subtree was destroyed with no prompt at
  all, and `x` sits directly beside the navigation keys.
- **The prompt names how much goes.** "archivar" alone does not tell the operator that the children
  go too, so the message counts the descendants.
- **The undo history moved to the App**, keyed by `map_id`, capped at 20 per map. It was a
  `MapScreen` instance attribute, so leaving a map discarded the history and an archived subtree
  became unrecoverable. Per map rather than one global stack: a single stack would let an undo taken
  in map B restore a snapshot of map A — data loss wearing a feature's clothes.
- **A field edit is undoable** (LLR-N05.6): the commit handler snapshots *before* mutating, so `u`
  reverts the edit rather than an unrelated earlier structural change.

## 2 · Files modified

**Source (3 — within the cap of 4).** `mapper/screens/coverage.py`, `mapper/app.py`,
`mapper/keymap.py` (the `n` key; the seat is the single source, so a key cannot be declared
anywhere else).

**Tests:** `tests/test_worklist_safety.py` (new, 9 nodes), `tests/test_coverage.py` (one assertion
re-expressed — see §5).

## 3 · How to test

```
PYTHONUTF8=1 python -m pytest -q
PYTHONUTF8=1 python -m pytest -q tests/test_worklist_safety.py
```

## 4 · Test results — one complete run

```
205 passed in 23.18s
```
Ledger: `205 = 196 - 0 + 9`. Reconciles. (196 was 195 + 1 parametrized arm from the `n` binding.)

**C-40 counterfactuals — executed, restores hash-verified to
`c3e73aff04b54dde63cea8816eee4afd7c3fa37b35a0a83d192952ef5083fcf8`.**

| Mutation | Expected | Observed |
|---|---|---|
| **M6** — restore the unconfirmed fast path for a non-root archive (the exact pre-batch defect) | `AT-N05a` reddens | `1 failed, 8 passed` — `AT-N05a` alone |
| **M7** — move the undo stack back onto `MapScreen.__init__` (the other pre-batch defect) | `AT-N05c` reddens | `2 failed, 7 passed` — `AT-N05c` **and** `AT-N04a` |
| **M8** — focus `schema[0]` instead of the first missing field | `AT-N04a` reddens | `1 failed, 8 passed` — `AT-N04a` alone |

**M7 over-reported and I did not predict it.** It reddened `AT-N04a` as well as its target. The
mutation shadowed the snapshot property, which changed edit-undo behaviour and cascaded into the
worklist fixture. The target arm did redden, so the gate holds — but the honest reading is that M7
is a *coarser* mutation than intended, not that `AT-N04a` independently guards undo placement.
Recorded rather than rounded down to the tidy result.

## 5 · Risks

| # | Risk | Status |
|---|---|---|
| 1 | `tests/test_coverage.py`'s assertion changed from `["O"]` to `["dueño"]`. | Not a weakened test: it asserts the same field is reported, in the form the story requires, and gained an assertion that an optional field is never reported. The old expectation encoded the defect. |
| 2 | `n` is now a map-scope key; it was a home-scope door key (`construir`). | Different scopes, which the seat permits and `duplicate_chords` verifies. `n` still constructs a map from home. |
| 3 | Undo depth is capped at 20 per map. | Deliberate and declared in LLR-N05.5; an uncapped stack of whole-graph snapshots is a memory leak on a long session. |
| 4 | `_goto_gap` reveals a collapsed inspector. | Intended: sending focus to a hidden widget would be a dead keystroke. |

## 6 · Pending items

- Security sign-off on Inc-4 — pending; gates the batch close, not this increment.
- MAN-01 inspection record — Phase 4.
- Carries unchanged: `MapStore.load` KeyError; `screens -> app` back-edge; legacy escape sites; the
  canvas's focus-unaware selection tone (batch 2).

## 7 · Suggested next task

Phase 4 validation: reconcile every `AT` to exactly one on-disk node (C-18), record MAN-01 as
inspection, and run the complete gate suite.

## Evidence checklist

- OK — Tests pass: `205 passed in 23.18s`, one complete run.
- OK — No secrets in code or output.
- OK — No destructive command without approval; three counterfactuals, reverted and hash-verified.
- OK — File count within cap: 3 source files.
- OK — Review packet attached.
- OK — Frozen interfaces untouched.
- OK — Nothing under `prototypes/` modified or staged.
