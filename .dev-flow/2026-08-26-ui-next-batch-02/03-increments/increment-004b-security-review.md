# Security Review — Inc-4b (US-N07 walk, `#D5b` rebind, `#D38` esc)

**Verdict: SIGN-OFF.** No HIGH. Two MEDIUM findings recommended, neither blocking.

Branch `feat/ui-next-batch-02`, entry `a971432`, nothing committed. Source under review: `mapper/app.py`, `mapper/keymap.py`. `.dev-flow/**` ignored.

## Method

Isolated mirror at `…/scratchpad/mirror` (`git clone --local --no-hardlinks` + working-tree overlay of `mapper/` and `tests/`). Overlay fidelity established by sha256 against the real repo before anything ran, and the real repo re-verified untouched at the end:

```
mapper/app.py: OK
mapper/keymap.py: OK
tests/test_inc4_census.py: OK
```

Fast lane in the mirror reproduces the declared baseline exactly:

```
843 passed, 17 deselected, 3 xfailed in 176.42s
```

**Clone artifact, reproduced and confirmed as an artifact.** With `tests/test_inc4_census.py` left un-staged (the fresh-clone state), the census arm `assert on_disk <= seen` goes red; re-staging it in the mirror restores `41 passed`. This is the mirror's index, not a product defect — the real repo has the file staged, so `git ls-files` lists it there. Reconciled in the mirror only.

All hostile fixtures were written under `tempfile.mkdtemp`; `fixtures/` was never touched. Probe scripts live in the scratchpad, outside the mirror tree — verified, because `test_darkside_census.py:677` rglobs `tests/` and a probe file dropped there would have reddened it. No hostile code point is spelled verbatim below.

---

## Findings

### F1 — the fold-auto-open hint line is unbounded file-derived text that drives layout height  [MEDIUM · introduced by this increment]

- **What:** `hint = f"abrió «{names}» · {hint}"` prepends a `", ".join(...)` of branch **titles** — untrusted, file-derived, unbounded in length and in count — ahead of the walk's own affordances. Nothing truncates it and nothing caps `len(opened)`. `HintLine` wraps rather than clips, so the strip grows and takes the space from the canvas.
- **Where:** `mapper/app.py:2452-2453` (`names` / `hint`), consumed at `mapper/app.py:2454`.
- **Why it matters:** measured at the declared context of use (118x34), one folded branch, one real `n` press:

| title length | hint region | canvas region | `esc limpiar` in frame |
|---|---|---|---|
| ~55 chars | h=1 | 58x10 | yes |
| ~2054 chars | h=18 | **56x1** | **no** |
| ~8054 chars | **h=71** (on a 34-row terminal) | **56x1** | **no** |

  The map collapses to a single row on one keypress, and the affordances `n siguiente · N anterior · esc limpiar` leave the painted frame — including `esc limpiar`, the affordance **this increment newly promises** under `#D38`. Same class as the recorded unbounded-pagination-meter finding: unbounded content displaces a declared affordance at 34 rows.
- **Mitigating, measured:** recoverable, and the class is pre-existing.
  - One real `esc` restores it: `canvas 56x1 → 58x10`, `hint h=18 → h=1`, operator stays on `MapScreen`. No lock-in.
  - The shipped, pre-existing `_event_toast("guardado", <long title>)` collapses the canvas identically (`canvas 56x1`, `toast h=18`) with no Inc-4b code involved. So this increment adds an **instance** of an existing unfixed class, not a new class.
- **Recommendation:** bound the segment at the point of composition, and put it after the affordances rather than before:
  ```python
  names = ", ".join(self._branch_name(nid) for nid in opened[:3])
  if len(opened) > 3:
      names += f" +{len(opened) - 3}"
  hint = f"{hint} · abrió «{darkside.fit(names, 40)}»"
  ```
  `darkside.fit` already truncates to display cells and re-coerces. Route the underlying class (chrome strips growing without bound on file-derived text) alongside the pagination-meter finding.

### F2 — `_unfold_onto` duplicates the renderer's descendant traversal on every walk keypress  [MEDIUM · introduced by this increment]

- **What:** `_unfold_onto` runs unconditionally on every `n`/`N` press whenever `folded` is non-empty, and computes a fresh descendant set per folded branch with no memo and no early exit once the target is located. It also rebuilds the child index from `graph.edges` per call.
- **Where:** `mapper/app.py:2332-2360`, called at `mapper/app.py:2448`.
- **Why it matters / measured, 11k-node deep chain:**

| folded | renderer's own `_hidden_ids` (per frame) | Inc-4b `_unfold_onto` (per keypress) |
|---|---|---|
| 100 | 188.5 ms | 164.5 ms |
| 1000 | 1707.2 ms | 1577.8 ms |
| 5000 | 6661.5 ms | **5671.2 ms** |

  On a bushy graph of the same size it is 10–14 ms, so the cost is depth-driven, not size-driven.
- **This is NOT a reintroduction of Inc-4a's quadratic.** Timed on the same 11k graph, same frame, nothing folded, real key presses:

```
j next_sibling (pre-existing)        min=    66.4 ms      (no-op on a chain: no sibling, no repaint)
l child        (pre-existing)        min=  3723.5 ms
h parent       (pre-existing)        min=  3732.2 ms
M next_gap     (RELOCATED by #D5b)   min=  2590.5 ms
n next_hit     (NEW)                 min=  3706.2 ms
N prev_hit     (NEW)                 min=  3735.4 ms
```

  `n` costs what the pre-existing `l`/`h` cost. The multi-second figure is the **pre-existing repaint** (`S-15`'s territory: the bound limits render count, not work), reachable today without this increment. A live search adds nothing measurable (`l` 3723 ms → 3849 ms), so Inc-4a's per-frame search memo is holding. `_unfold_onto`'s contribution is a roughly 1x duplication of a traversal the renderer already performs, on a path that is already degenerate.
- **Recommendation:** skip the work when it cannot change anything, and stop once the target is found:
  ```python
  if not self.folded or nid not in self._hidden_now():   # renderer's union, already computed
      return []
  ```
  At minimum, `break` out of the per-branch DFS as soon as `nid in seen`. Not blocking: the fold counts where this bites (≥1000 folded branches) require ~1000 `z` presses to reach.

### F3 — `_branch_name` subscripts `graph.nodes` directly  [LOW · latent, not reachable via the load path]

- **What:** `title = self.graph.nodes[nid].ficha.title` — a bare subscript. A folded id that is an edge parent with no `Node` entry raises `KeyError` on the keypress.
- **Where:** `mapper/app.py:2374`.
- **Executed:** constructed in memory, `_unfold_onto` returned `opened = ['ghost']` and `_branch_name` then `RAISED: KeyError 'ghost'`.
- **Why it is LOW and not `F-A`'s class:** not producible from file data. The shipped loader synthesises a `Node` for every edge endpoint declared in the `.mmd` even when the `_nodos.yml` sidecar omits it — probed with a sidecar missing a middle node: `nodes: ['a','b','c'], dangling edge parents: none`. So no file reaches this branch.
- **Recommendation:** `node = self.graph.nodes.get(nid)` and fall through to the existing `plain(nid)` arm.

---

## Probed and clear

**1 · The operator's query in `E1c` (`app.py:2439`) — clean.** Query typed **character by character through real `pilot.press`**, including the override and a C0 byte (`typed_ok=True`, input value matched). Painted frame of the toast:

```
query_text : [link=x]qq<U+202E>zz[/]<U+0007>
painted    :  0 coincidencias   «[link=x]qq<U+FFFD>zz[/]<U+FFFD>» no aparece en este mapa
control/format code points surviving in the PAINTED toast: NONE
```

`darkside.plain` replaced U+202E and U+0007 with U+FFFD, so the override cannot reverse the toast's sentence — the guard is load-bearing and present. Markup brackets survive as **literal text**, which is correct: `_event_toast` builds a `Text.assemble` and `Static.update(Text)` does not parse markup, so `C-17`'s bracket gap does not bite here. The query reaches no other new sink: the only interpolation of `query_text` in the diff is `app.py:2439`; `app.py:2254`, `2405`, `2770-2771` are `.strip()` tests and a clear. The hint after `E1c` is generic (`sin coincidencias · esc limpiar`).

**2 · The fold-auto-open hint's branch title (`app.py:2374`, `2452`) — coerced, and not a markup or widget-id sink.** Hostile title carrying markup brackets, an override, a C0 byte and a zero-width space:

```
loaded  : [bold red]rama<U+202E>mala[/]<U+0007><U+200B>
painted : siguiente ▸ abrió «[bold red]rama<U+FFFD>mala[/]<U+FFFD><U+FFFD>» · n siguiente · N anterior · esc limpiar
control/format code points surviving in the PAINTED hint: NONE
```

Double-coerced: `_branch_name` calls `plain`, then `darkside.hint_line` calls `plain` again on the whole assembled string, and returns a `Text` — no markup parse. **No widget id is built from file-derived text anywhere in this diff**, so this increment adds no new instance of `F-A`.

**3 · The one-time rebind declaration — static.** Every string is a `keymap.py` literal read through `_seat_row` at call time: `next_hit` `('n', 'siguiente coincidencia')`, `prev_hit` `('N', 'coincidencia anterior')`, `next_gap` `('M', 'siguiente faltante')`, `back_or_home` `('esc', 'volver')`. Painted on the first press: `n · siguiente coincidencia   siguiente faltante ahora en M`. Nothing operator- or file-supplied reaches it.

**4 · The bound toast (`app.py:2427`)** interpolates `MAX_RENDER_NODES = 12000`, `int`, a module constant. Nothing else.

**5 · `esc` (`#D38`, `app.py:2752`) — bounded, no lock-in.** All transitions driven by real key presses:

- live search → esc #1 clears (`query=''`, stays on `MapScreen`) → esc #2 pops.
- whitespace-only `'   '` → `strip()==''` → **first** esc pops. The reported behaviour is the real one, not a trap.
- `'  plain  '` → treated as live → esc clears, then pops. Correct: the discriminator is `strip()`, not the raw value.
- After a walk (fold opened, hint rewritten): **2 escapes** to leave. Hammered escape in a loop — bounded every time.
- `query_text` does not survive re-entry (fresh `MapScreen` has `''`), so no hidden live search can strand a later operator.

**6 · Walk performance — see F2.** No new super-linear work in the repaint path; `n` costs what pre-existing `l`/`h` cost.

**Cyclic graphs:** a cycle **cannot reach the screen** — refused at the shipped load boundary (`el mapa tiene un ciclo: a→b→c→a`, HLR-R01). My first attempt at a cyclic fixture silently produced a 1-node graph; the cause was this refusal, not the harness, and I chased it down rather than substituting. Defence in depth anyway: a cycle injected in memory terminates in `_unfold_onto` (0.016 ms, `opened=['a','b','c']`) because the DFS carries a `seen` guard. No hang.

**7 · The deleted `if source_crumb: pop else: pop` was genuinely dead** — both arms were the identical statement in the pre-image. No navigation regressed, driven end to end:

```
enter on a linking node -> ['…','MapScreen(outer)','MapScreen(inner)']  source_crumb=['outer','Link']
esc, no query           -> ['…','MapScreen(outer)']          (back on outer)
inner + live search: esc #1 clears, esc #2 -> ['…','MapScreen(outer)']
```

**Memo staleness — not a defect.** `_walk_hits` consumes `_search_order`'s memo without opening a paint pass. The memo is keyed on graph object identity and query text, which would not catch an in-place mutation; but every graph-mutating action (`action_archive:2684`, `action_add_child:2649`, `action_undo:2772`) calls `refresh_canvas`, which calls `_open_paint_pass` and drops the memo. The docstring's claim holds.

## Pre-existing — recorded and routed, not fixed

| Item | Route | New instance added by this diff? |
|---|---|---|
| `F-A` (HIGH, widget id from a schema key) | Inc-REPAIR | **No** — no widget id is built from file-derived text in this diff |
| `S-15` (the bound limits render count, not work) | open | **No** — the multi-second repaint is reachable today via `l`/`h`; `n` matches it |
| Unbounded pagination meter, affordance off-viewport at 34 rows | open | **Yes, one — F1.** Same class, hint line instead of the strip |
| Export-toast operator-path leak, anchor `_event_toast("exportado", …)` | open | **No** — the diff does not touch that call, and grep over the diff's added lines found no path, token, env or home-directory interpolation |

## Evidence checklist

- ✓ Each finding has what · where · why · recommendation — F1 `app.py:2452`, F2 `app.py:2332-2360`, F3 `app.py:2374`.
- ✓ Each finding has a severity — MEDIUM, MEDIUM, LOW.
- ✓ No secret values in this output — no credentials in scope; no hostile code point spelled verbatim (named as `U+202E` etc. throughout).
- ✓ Verdict explicit — SIGN-OFF, below.
- ✓ No new tool/integration added — this increment adds no external action surface, no dependency, no network or filesystem sink; the only new writes are two in-process Textual widget updates.
- ✓ Fidelity established before mutation (`843 passed, 17 deselected, 3 xfailed`) and real-repo integrity re-verified by sha256 after.

## Could not determine

- Whether F1's collapse is worse on a **wrapped** hint at terminal widths below 118. I measured only at the declared 118x34 context of use and at the default 80x24 indirectly; narrower terminals wrap more and would collapse the canvas at a shorter title.
- The **realistic ceiling on `folded`** for F2. I measured the cost curve, not operator behaviour; there is no fold-all chord (`z` folds one branch), so ≥1000 folds needs ~1000 presses, but I did not confirm no other code path populates `folded` in bulk.

---

# Verdict

- [x] **SIGN-OFF** — OK to ship. No HIGH.
- [ ] OK to ship with the listed mitigations applied first
- [ ] Block

F1 and F2 are MEDIUM: recommended, not blocking. F1 is the one worth fixing in this batch — it is cheap (`darkside.fit` already exists), and the affordance it displaces is the one `#D38` newly promises.
