# Increment 2 — `HLR-MAP.1`: the module map is true against the tree

**Batch:** `2026-08-27-repair-batch-02` · **Base ref:** `d877784` · **Branch:** `fix/repair-batch-02`
**Source files: 0 of 4.** `docs/ARCHITECTURE.md` is a product doc; tests are uncapped.

> **BLUF.** The `2026-08-26-ui-next-batch-02` ARQ was approved *with this map amended*, and the
> amendment was **never landed** — its `PLAN.md` §7 recorded as done work that did not exist on disk
> (C-44). Landing it revealed the map asserting **six** provably-false things about the tree, not the
> four the ARQ named. The map is the **oracle the A-family triggers read**, so a false map
> mis-classifies every future change; it now carries a test.

---

## 1 · What changed

**Six false present-tense claims, each executed against disk before correction.**

| # | The map claimed | Executed result | Named by the ARQ? |
|---|---|---|---|
| 1 | `Canvas` exposes `dline` | `hasattr(Canvas, "dline")` is `False`; `grep -rn "dline" mapper/` returns nothing | yes |
| 2 | `MapStore` exposes a public `reindex()` | reindexing is **private**, `store.py:533`; the row also omitted four real public methods | yes |
| 3 | `load(map_id) -> (Graph, Sidecar)` | `store.py:377` returns a **`Graph`**; the sidecar is built inside `save`, not passed in | yes |
| 4 | `SearchIndex(store)` | `search.py:7` takes a **`Graph`** | yes |
| 5 | `Canvas.rows() -> list[str]` | annotated and returning **`list[Text]`** | **no — found here** |
| 6 | `SearchIndex.query`'s consumer is `app` | an AST walk of `app.py` shows it imports **no** `search` module; `grep -rn "SearchIndex" mapper/ tests/` matches only its own definition — the module has **zero consumers** | **no — found here** |

**The forward-looking rows land as COMMITMENTS, never as present-tense facts.** The ARQ proposal
declares `mapper/views/state.py` *"new this batch"* for a file that does not exist. Landing that
verbatim would have traded a C-44 defect (work recorded as done that never landed) for a **false
map** — in the one file the triggers read as an oracle. The `ViewState` / `IRenderer`-as-`Protocol`
contract is therefore recorded under an explicit **`COMMITTED, NOT PRESENT`** marker naming the batch
and increment that will land it.

**`IRenderer` is described as it is.** `grep -rn "IRenderer" mapper/` finds two mentions in comments
and **no class and no `Protocol`**: the contract is enforced by convention among the renderer
modules, not by the interpreter. The map now says so, rather than implying a type exists.

---

## 2 · Files modified

| File | Kind | Note |
|---|---|---|
| `docs/ARCHITECTURE.md` | product doc — **outside the source budget** | six corrections + the commitment row + an amendment header |
| `tests/test_repair_map_truth.py` | test (new, uncapped) | 26 nodes |

**0 source files.** The batch's whole source budget was spent by Inc-1's single file.

---

## 3 · How to test

```bash
PYTHONUTF8=1 python -m pytest tests/test_repair_map_truth.py -q -p no:randomly -o addopts=
```

## 4 · Test results

| Run | Result | Exit |
|---|---|---|
| `test_repair_map_truth.py` | **26 passed** in 0.06s | 0 |
| whole fast lane | **517 passed, 17 deselected** | 0 |
| `ruff` on the new test file | **All checks passed** | 0 |

### 4.1 · Counterfactual — executed, restore proven by sha256

Detached copy; `docs/ARCHITECTURE.md` pristine sha256 `c70350d2…fc27360d`, restored byte-exact.

| Mutant | Mutation | Result |
|---|---|---|
| **`M-MAP-a`** — *the requirement's named weaker variant* | land the ARQ proposal verbatim: declare the unbuilt `mapper/views/state.py` as an owned path | **1 failed** — the path-existence arm reddens |
| `M-MAP-b` | reintroduce the `dline` claim | **1 failed** |
| `M-MAP-c` | drop the `COMMITTED, NOT PRESENT` marker | **1 failed** |
| `M-MAP-d` | restore the tuple return on `load` | **1 failed** |

`M-MAP-a` is the one that matters: it is the requirement's own named variant, and it proves the test
would have caught the exact mistake this increment was at risk of making.

---

## 5 · Risks

1. **`AT-P05` is a set of verbatim-substring PINS, not a general truth check**, and is labelled so in
   the file. It certifies that *these six corrections* survive; it does not and cannot find a
   seventh. Calling it a general guarantee would be the same false record the amendment was fixing.
2. **The oracle reads the composition table's owned-paths column, deliberately.** A naive "every
   path-like string must exist" reddens on `mapper/screens/prompt.py` (a **proposed remediation
   target** for a recorded import-cycle violation) and on the `state.py` commitment — both correct as
   written. Flagging them would false-fail correct work, which costs as much as passing wrong work
   (C-53) and trains people to ignore the check.
3. **A constraint on the map's own prose, learned by tripping over it.** A correction note may
   *describe* the claim it replaced but must not *spell it verbatim*, because the pin cannot tell a
   value being reported from one being declared. My first draft of the `search` note quoted the old
   signature and **reddened its own arm**. This is C-56 — an evidence transcript is corpus input —
   and the remedy applied is C-56's own: describe by position and operation, never paste the token.
   The constraint is recorded in the test file so the next amender does not rediscover it.

## 6 · Pending items

- No independent review of this increment yet — it goes to the whole-branch review with Inc-3.
- Backlog carry: the map still describes `screens` and `app` as separate modules while
  `mapper/app.py` is not split (recorded as `R-009`, unchanged by this batch).

## 7 · Suggested next task

**Increment 3 — `HLR-GOLD.1` + `LLR-PERF.1`:** the derived pin census, the `B3` non-activation
correction, and the honest 51-node measurement fixture.

---

## 8 · Evidence checklist

| Item | ✓/✗ | Evidence |
|---|---|---|
| Tests / lint pass | ✓ | 26 passed exit 0; fast lane 517 passed; ruff clean on the new file, 29 whole-tree = base |
| No secrets | ✓ | documentation and a test; no credential surface touched |
| No destructive command | ✓ | no git mutation; counterfactual on a detached copy |
| File count within cap | ✓ | **0 source files** |
| Counterfactual executed | ✓ | 4 mutants, §4.1, including the requirement's named `M-MAP-a` |
| Restore proven | ✓ | sha256 `c70350d2…fc27360d` returned byte-exact |
| Derived, not hand-listed (C-31) | ✓ | `_declared_paths()` parses the composition table; `test_tc_p05` asserts it is non-degenerate so a reworded header cannot silently empty every arm |
| Pins labelled as pins (C-40) | ✓ | `AT-P05`'s docstring states it certifies these corrections, not general truth |
