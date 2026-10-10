# Executive summary — mapper — Batch `2026-10-09-modular-batch`

> Phase 6 artifact (drafted by a Kimi `kimi-for-coding` unit). Audience: non-technical stakeholder.

## 🔑 Bottom line (read first)

- **What we delivered:** `mapper/app.py` — a single 5255-line file that every feature increment collided on — is now 340 lines, with the code redistributed into 7 sibling-screen modules and a 13-file `mapper/screens/map/` package, one concern per file.
- **Business outcome:** feature work can now run in **parallel lanes by concern** — two workers changing different features no longer edit the same file. The operator's stated goal («para poder paralelizar el trabajo, eso es primordial», US-001 source) is met, with the app behaving exactly as before.
- **Next step:** the performance/scale batch (B-33 — first datapoint already captured: `test_strips` 16.3 s at 118×34), then ReqHarness (B-107), which awaits the operator's verdict on the unified decision gallery.

---

## Context (reference)

### Context

This is the batch the architecture record had been waiting for: backlog row R-009 (re-opened) named the 5255-line `app.py` as the single reason most batches could not run parallel product lanes. The architecture map (`docs/ARCHITECTURE.md`) had already been amended with the target rows; this batch landed the code that makes the map true.

### Problem

Every feature touched the same file: `MapScreen` alone spanned 3454 lines inside `app.py`, so any two increments collided at file granularity (`modules(A) ∩ modules(B) = ∅` failed for every pair). A structural refactor of this size is dangerous in a different way too: one silent mistake — a dropped key binding, a moved name the tests can no longer patch — would reach the user as a regression without any test failing.

### Solution

A pure cut-and-paste modularisation, proven safe by construction and by measurement. One plain mixin per concern is composed into the core `MapScreen` class (mechanism A), so Textual dispatch, key bindings, colours and layout are untouched. Every name the 68 importing test files use stays importable from `mapper.app` (21 re-exports), and the eight names the suite monkeypatches were repointed to the modules that actually read them — so the entire existing safety net kept working unchanged while the code moved under it.

### Outcomes / results

- `mapper/app.py`: 5255 → **340 lines**; `MapScreen` moved into **12 map modules** (core + 11 concerns) beside **7 sibling screens** (`wc -l`, post-mortem §Product findings).
- **Behaviour identical, proven:** the scripted session (open, move, search, toggle, export, quit) paints byte-equal output against pre-move goldens at 118 and 87 columns (AT-065), and every moved method body is `ast.dump`-identical to its baseline (`tests/test_mod_bodies.py`).
- **Suite: 2941 → 3133 passed, 0 failed** (2941 − 3 + 195 = 3133 reconciles; the 3 rewritten test functions were renamed/stronger, none weakened; gate at `69676cf`).
- **What it unlocks:** parallel lanes by concern — each lane edits exactly one module file, and the dependency rules that make lanes legal are themselves an executable test (AT-071).
- **What it does not yet remove — the shared seams** (post-mortem, restated after the P5 architect review): key changes still meet on the keymap seat / core `BINDINGS`, new public names on `app.py` `__all__`, structural changes on the architecture map and the patch-surface guard, and F1/F2 changes on the census baseline. A merge-hotspot plan (B-111) was proposed and deferred to the first batch that runs parallel lanes.

### Next steps

1. **B-33 — performance/scale** (the NEXT batch by prior routing): `MAX_RENDER_NODES` bounds the drawn node count, not the work done; the slow-lane timings (19 slow tests, `test_strips` 16.3 s at 118×34) are its first datapoint.
2. **B-107 — ReqHarness** (mapper's product direction): awaits the operator's verdict on the unified decision gallery, then the next feature batch.
3. Housekeeping carries before any batch-folder archive: B-108 (census baseline under `tests/`), B-109 (cycle guard one-hop closure), B-110 (one unpatched `pan_extent` reader in the export concern) — all minor, all recorded.
