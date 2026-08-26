# Increment 3 — the rail, the focus signal, the honest keybar

## 1 · What changed

**BLUF: the three-region skeleton is complete, the operator can now tell which region is live, and
the keybar stops lying about what it is hiding — `m cobertura`, the entry point to the coverage
flow, was previously invisible.**

- **`mapper/widgets/rail.py` (new)** — `OutlineRail`: a collapsible outline of the map with a
  **subtree** missing-field count per branch and a coverage lattice at the bottom. It walks the
  `Graph` itself rather than reusing `OutlineRenderer`, which returns a `Text` — a picture, not a
  structure, and no kwarg extracts structure back out of a rendered `Text`. `widgets → model` is
  allowed exactly so the rail can do this without touching a frozen interface.
- **The count is the subtree's, not the node's.** `fin` is complete but its child `cont` is not; a
  node-local count would read 0 and hide the gap behind a collapsed branch, which is the one thing
  the count exists to prevent.
- **The lattice is deterministic** — one dot per node in document order, lit when the node is
  complete. The prototype drew a random field; a decorative random lattice in a coverage instrument
  would be actively misleading.
- **Focus signal (HLR-N06).** The rail's selection is the solid blue block only while the rail holds
  focus; otherwise it sinks to `STEP`. The hint line names the live region in words — the signal
  that survives colour-blindness and a monochrome terminal.
- **Region collapse (LLR-N06.6).** `R` and `I` toggle the rail and the inspector; below a measured
  58-column canvas floor the rail yields automatically, because past that point a card's coverage
  row clips mid-field and a *present* field becomes indistinguishable from a *clipped* one.
- **`darkside.keybar` truncates visibly** and `KeyBar` renders at its **measured** width instead of
  a hard-coded 118.

## 2 · Files modified

**Source (5 — ⚠ over the cap of 4, declared).** `mapper/widgets/rail.py` (new),
`mapper/app.py`, `mapper/darkside.py`, `mapper/widgets/chrome.py`, `mapper/keymap.py`.

*Why:* `keymap.py` is touched only to declare the four new region keys (`R`, `I`, `g`, `z`). The
seat is the single source of truth, so a new key **cannot** be added anywhere else — that is the
constraint Inc-1 deliberately created, and honouring it costs a file here. Splitting it out would
mean an increment whose actions exist but no key reaches.

**Tests:** `tests/test_rail.py` (new, 7 nodes), `tests/test_keymap.py` (fence updated deliberately:
map scope 18 → 22).

## 3 · How to test

```
PYTHONUTF8=1 python -m pytest -q
PYTHONUTF8=1 python -m pytest -q tests/test_rail.py
```

## 4 · Test results — one complete run

```
169 passed in 17.84s
```
Ledger: `169 = 162 − 0 + 7`. Reconciles. (162 was the count after the seat gained its four region
keys, itself `158 + 4` parametrized `AT-N03a`/`AT-N03b` arms.)

**C-40 counterfactuals — executed, restores hash-verified.**

| Mutation | Observed |
|---|---|
| **M4** — drop the count and the help key from the keybar marker, leaving a bare `…` | `1 failed, 6 passed` — `AT-N03e` alone |
| **M5** — make the rail paint the focused style unconditionally | `1 failed, 6 passed` — `AT-N06a` alone |

Restores: `mapper/darkside.py` → `29c302469d96ebeff03d1cead8ca4bb7f6206193cc825c1df6f05e7b50c2d8b4`,
`mapper/widgets/rail.py` → `34c9336cd966221f9317459c66f522afc012202dc0ad8daa372ae4b1edcf5fdf`.

**A failed counterfactual, recorded because a silent one is worthless.** My first attempt at M4
inserted an unreachable `if False:` block, which broke the parse; the run produced **no test output
at all** and my grep pattern silently matched nothing. Had I not noticed the empty output I would
have recorded a mutation that never ran as evidence that the gate holds. M4 was redone as a
targeted edit to the marker itself. This is the third time in this batch that "the command produced
nothing" was the only signal that a measurement was invalid.

## 5 · Risks

| # | Risk | Status |
|---|---|---|
| 1 | The rail is focusable, so Textual focuses it during mount before the screen can park focus. | Handled by deferring the park to `call_after_refresh`. For one frame on a real terminal the rail may hold focus; harmless, but it means the pilot needs two pauses before asserting, which the test documents rather than hides. |
| 2 | `AT-N06a` asserts the rail's focus styling, **not** a global one-ACCENT-run invariant. | Deliberate — see Amendment 3. The canvas's selection block is painted by a frozen renderer that cannot know where focus is, so the global invariant would false-fail correct code. Carried to batch 2, where the canvas is already being reworked. |
| 3 | Auto-collapse is width-driven, but an explicit toggle pins the choice. | Intended: once the operator has decided, the app stops second-guessing. |
| 4 | The lattice renders one dot per node and will not scale to a very large map. | Known; the rail is not paginated. Batch-2 territory. |

## 6 · Pending items

- LLR-N06.3 (`DsChip` renders focused and selected identically) — **moved to Inc-4**, which is where
  `components.py` and the attachment chips belong.
- The canvas's focus-unaware selection tone — carried to batch 2.
- Carries from earlier increments unchanged (`MapStore.load` `KeyError`; the `screens → app`
  back-edge; the legacy `escape()` call sites).

## 7 · Suggested next task

Increment 4 — US-N02 attachments: `mapper/osopen.py` (new, with the security conditions LLR-N02.6
through N02.10), `mapper/widgets/inspector.py`, `mapper/widgets/components.py` (LLR-N06.3),
`mapper/app.py`.

## Evidence checklist

- ✓ Tests pass — `169 passed in 17.84s`, §4.
- ✓ No secrets in code or output.
- ✓ No destructive command without approval — two counterfactuals, reverted and hash-verified; one invalid attempt disclosed in §4.
- ✗ **File count over the cap** — 5 source files against 4. Reason declared in §2.
- ✓ Review packet attached — this document.
- ✓ Frozen interfaces untouched — no diff in `store.py`, `canvas.py`, `mermaid.py`, `github.py`, `export.py`, `search.py`; `IRenderer.render`'s signature unchanged.
- ✓ Dependency ban honoured — `rail.py` imports `darkside` and `model` only; no `store`, no `app`.
- ✓ Nothing under `prototypes/` modified or staged.
