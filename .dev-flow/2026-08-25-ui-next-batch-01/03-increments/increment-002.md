# Increment 2 — US-N01 · the taller recompose and the editable inspector

## 1 · What changed

**BLUF: `MapScreen` is now canvas + inspector side by side, the ficha is rendered once instead of
twice, and every field of the selected node is editable in place and persists through
`MapStore.save`.**

- **`mapper/widgets/inspector.py` (new)** — `FichaInspector`, a `Vertical` panel docked right.
  Rows: header, title, state (a `DsSegmented` over ok/riesgo/tarde/bloq), one row per
  `SchemaField` **labelled from `SchemaField.label`**, notes, and a `DsProgress` coverage meter.
  This is the first production consumer of the nine `Ds*` components, which until now were
  exercised only by the settings canary.
- **The widget cannot write.** `docs/ARCHITECTURE.md` §3 bans `widgets → store`, so a commit posts
  a `FieldCommitted` message and `MapScreen` — which owns the graph and the store — performs the
  whole-graph write. The inspector does not import `mapper.store`.
- **The double render is gone.** Both the app's `#map-ficha` GroupBox *and* `LayeredRenderer`'s own
  ficha strip are deleted. Suppressing the strip with a new `render` kwarg was rejected:
  `IRenderer.render` is frozen this batch. Its signature is byte-identical to `HEAD`; only the body
  changed.
- **Editing does not fight navigation.** `FieldInput` claims `escape` at the widget level, so the
  first `escape` leaves the field keeping the typed value and the second leaves the map. The
  inspector also parks focus after every rebuild.
- **`mapper/model.py`** gains `Ficha.missing_required(schema)` — the single owner of "what is
  missing" (LLR-N01.9), so the inspector, the rail and the worklist cannot drift on what
  "complete" means.
- **`mapper/darkside.py`** gains `plain()`, the one coercion helper for file-derived text, and
  `fit()`/`hint_line()` now use it instead of `rich.markup.escape`.
- **`mapper/widgets/chrome.py`** — `HintLine.set_hint()`, matching its siblings `set_crumb` /
  `set_groups`.

## 2 · Files modified

**Source (5 — ⚠ over the cap of 4, declared).** `mapper/widgets/inspector.py` (new),
`mapper/app.py`, `mapper/views/layered.py`, `mapper/model.py`, `mapper/darkside.py`, plus
`mapper/widgets/chrome.py` — **6**.

*Why, stated rather than hidden:* the plan budgeted four. Two extra files arrived from the PDR
security conditions, which landed after the cut was made: `darkside.plain()` (S-B2, the C0/C1
coercion helper) and the `HintLine` setter that the UX lens' escape-hatch fix depends on (U-B2).
Each is a small, single-purpose addition — `plain()` is 12 lines, `set_hint()` is 6 — and splitting
them into their own increment would have left the tree in a state where the inspector renders
untrusted text with no coercion helper to call, which is worse than a declared overrun. Recorded
for the close review per the budget rule, not waved through.

**Tests:** `tests/test_inspector.py` (new, 12 nodes), `tests/test_legacy_fixture.py` (assertion
ported, see §5).

## 3 · How to test

```
PYTHONUTF8=1 python -m pytest -q
PYTHONUTF8=1 python -m pytest -q tests/test_inspector.py
```

## 4 · Test results — one complete run

```
158 passed in 15.63s
```
Ledger: `158 = 146 − 0 + 12`. Reconciles.

**C-40 counterfactuals — all executed, per resolved arm, all restores hash-verified.**

| Mutation | Expected | Observed |
|---|---|---|
| **M1** — delete the `store.save` call from the commit handler | the persistence ATs redden | `5 failed, 7 passed` — `AT-N01a` plus **all four** `AT-N01b` arms |
| **M2** — clamp the state setter to the default `"ok"` | only the non-default arms redden | `3 failed, 9 passed` — the `risk`, `late` and `blocked` arms; **the `ok` arm stayed green** |
| **M3** — remove `FieldInput`'s widget-level `escape` binding | the escape-hatch AT reddens alone | `1 failed, 11 passed` — `AT-N06b` only |

**M2 is the one worth reading twice.** It is the measured argument for C-10: a single test driven at
the default value would have stayed green against a setter that ignores its argument entirely.
Three of the four arms are what make the assertion mean anything.

Restores: `mapper/app.py` → `04257da8781f49d9407605fcca288af744a26aca21e1a11c3778c77e48eb61ec`,
`mapper/widgets/inspector.py` → `e689b2e952770e9388859d613c67e24069c3c34a9dc3759eeed53f8ac379beaa`,
both matching pre-mutation. `__pycache__` purged and the full suite re-run green afterwards.

## 5 · Risks

| # | Risk | Status |
|---|---|---|
| 1 | **My reverse census (premise P-12) was incomplete.** I grepped the deleted strip for `"selecciona un nodo"` and `"sin acta"` and concluded nothing asserted it. `tests/test_legacy_fixture.py:27` asserted `"cobertura"`, which the strip also emitted, and it broke. | Caught by the suite, not by the census — the census was the wrong instrument, and I am recording that rather than presenting the catch as planned. The assertion was **not deleted**: the coverage-is-visible intent moved to `tests/test_inspector.py`, and the renderer test now asserts the strip's strings do **not** return. |
| 2 | Committing an edit triggers `refresh_canvas`, which rebuilds the inspector and drops focus back to the map. | Deliberate and coherent with `↵` = commit-and-return. Named here because it is a behaviour someone will question. |
| 3 | The canvas now renders at `width − 36`. At an 80-column terminal that leaves ~44 columns. | The UX lens measured that below ~58 columns the coverage-letters row clips mid-field, so a *present* field and a *clipped* field look identical. **Not closed in this increment** — LLR-N06.6 (collapsible rail and inspector) is Inc-3's job and this risk stays open until then. |
| 4 | `plain()` replaces control characters with U+FFFD but leaves the residual text of an ANSI sequence visible (`acta\x1b[31m` renders as `acta�[31m`). | Correct and deliberate: the terminal cannot act on it. Noisy rather than dangerous. |

## 6 · Pending items

- LLR-N06.6 collapsible rail/inspector, and LLR-N06.1–N06.3 the focus signal — Inc-3.
- The ~20 legacy `rich.markup.escape` call sites in `app.py`'s other renderers (`_FichaScreen`,
  `HomeScreen`) still emit visible backslashes. Pre-existing, outside this story's budget — carry.
- `MapStore.load` `KeyError` on a malformed sidecar (security F-M5) — carry.

## 7 · Suggested next task

Increment 3 — the rail, the coverage lattice, the focus signal (HLR-N06), and the keybar truncation
marker (`AT-N03e`): `mapper/widgets/rail.py` (new), `mapper/widgets/chrome.py`, `mapper/app.py`.

## Evidence checklist

- ✓ Tests pass — `158 passed in 15.63s`, one complete run, §4.
- ✓ No secrets in code or output.
- ✓ No destructive command without approval — three counterfactual mutations, all reverted and hash-verified in §4.
- ✗ **File count over the cap** — 6 source files against a budget of 4. Reason declared in §2; flagged for the close review rather than waved through.
- ✓ Review packet attached — this document.
- ✓ Frozen interfaces untouched — `git diff HEAD` over `store.py`, `canvas.py`, `mermaid.py`, `github.py`, `export.py`, `search.py` is empty; `LayeredRenderer.render`'s signature is byte-identical (only the body changed).
- ✓ Dependency ban honoured — `mapper/widgets/inspector.py` does not import `mapper.store`; it posts a message.
- ✓ Nothing under `prototypes/` modified or staged.
