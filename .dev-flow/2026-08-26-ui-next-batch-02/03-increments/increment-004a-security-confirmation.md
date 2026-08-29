# Security Review — Inc-4a CONFIRMATION pass (independent)

Reviewer: security-reviewer (independent confirmation; no HIGH self-cleared in this batch)
Branch: `feat/ui-next-batch-02` · `HEAD` = `5f4816c` · work uncommitted in the working tree
Method: isolated `git clone --local --no-hardlinks` mirror + working-tree overlay. Real repo never mutated.

## Scope reviewed

- `mapper/search.py`, `mapper/app.py`, `mapper/views/state.py`, `mapper/views/layered.py` (working tree)
- The claimed discharge of the HIGH availability family **F1 / F1a / F1b**
- The new per-paint memo (`_search_memo` / `_open_paint_pass`) as new attack surface
- Re-confirmation of the previously-clean classes: file-derived text sinks, `F-A`, blank-query ownership, secret/path/username sinks

### Fidelity, established before measuring

Mirror reproduces the declared suite exactly:

```
818 passed, 17 deselected, 3 xfailed in 145.56s
```

(First mirror run gave `1 failed, 817 passed` — `tests/inc4_support.py` and `tests/test_search.py` are *staged* in the real repo but untracked in a fresh clone, which the A3 census correctly flags. `git add` of those two in the mirror reproduces the author's state. This was a mirror artifact, not a defect.)

### Non-mutation proof

180 files under `mapper/`, `tests/`, `.dev-flow/` hashed before the review; `sha256sum -c` after: **all OK, zero mismatches**. Real repo `HEAD` unchanged at `5f4816c`. Hostile fixtures were built in `tempfile.mkdtemp`, never in `fixtures/`.

### The keypath gap I declared last time — now CLOSED

Last pass I could not route `pilot.press("j")` and substituted a direct `refresh_canvas()` call. Root cause found: `j` is bound to `next_sibling` (`keymap.py:101`), which is correctly a **no-op at the root**, where the probe's cursor sat. Nothing was wrong with the app or the harness. Re-driven with `l` (`child`, `keymap.py:104`), which always moves from the root, and with the real search sequence `/` → characters → `enter`. Every measurement below is through the shipped key path, asserted by `screen.nav.cursor != before` and `screen.query_text == query`. **No reconstruction stands as the keypath in this pass.**

---

## Verdict on the blocked HIGH family

Measured through the real key path, one repaint, resolutions counted by wrapping `SearchIndex.query`:

| Case | N | Resolutions / repaint | Search cost | Frame |
|---|---|---|---|---|
| At bound, active query `riesgo` | 12000 | **1** | **16.3 ms** | 4285 ms |
| At bound, blank (never searched) | 12000 | **1** | **0.0 ms** | 4375 ms |
| Above bound, active query | 12002 | **0** | **0.0 ms** | 4197 ms |

### F1 — DISCHARGED

Was 25.8 s of a 30.6 s frame at N=12002. Now 16.3 ms of a 4285 ms frame — **0.38 % of the frame**. The child index is built in one `O(E)` pass and `seen` is hoisted out of the comprehension (`search.py:tree_order`, `search.py:query`). Resolutions per repaint went 4 → **1**, confirmed by count, not by claim.

### F1a — DISCHARGED

The blank-query case now costs **0.0 ms** of search per repaint. The guard short-circuits the *work*, not just the result: `query()` early-returns on an empty hit set before the walk. Enforcement verified to still live at the **owner**, and verified to be load-bearing rather than decorative:

```
'' query= [] hits= 0
'   ' query= [] hits= 0
'\t\n' query= [] hits= 0
raw search_hits("") = 6 of 6 nodes   <- owner guard is what stops this
raw search_hits("   ") = 4
```

The new early return sits *after* `hits()`, so it cannot bypass the rule and did not move enforcement to a caller.

### F1b — DISCHARGED

Above `MAX_RENDER_NODES`: **0 resolutions, 0.0 ms**. Search now stops where drawing stops.

### The residual frame is pre-existing, and the author's `S-15` framing is HONEST

Identical probe against pristine `HEAD` (`5f4816c`, no working-tree changes):

| | pristine HEAD | with the fix |
|---|---|---|
| N=12000, active query | 4270 ms | 4285 ms |
| N=12000, blank | 4668 ms | 4375 ms |
| N=12002, above bound | 5334 ms | 4197 ms |

The multi-second frame **predates Inc-4a** and the fix does not regress it. The author claims to have closed only the escalation Inc-4a introduced, not `S-15` itself, and to measure search at 0–1 % of the frame; I independently measure **0.38 %**. The framing is accurate. (I measure ~4.3 s where they report ~8 s — magnitude differs by machine; direction and conclusion agree.)

---

## The memo — probed as a protocol, since that is what it rests on

### Can it serve a stale hit set? Yes in principle, **not reachably** today.

`_search_order` keys the memo on `self.graph` **object identity** plus `query_text`. In-place mutation of the same `Graph` object under the same query defeats both key components. Executed:

```
[P-M3] before             =['riesgo-root', 'b', 'd', 'e', 'c']
       memo_after_mutation=['riesgo-root', 'b', 'd', 'e', 'c']
       truth              =['riesgo-root', 'b', 'd', 'e', 'c', 'f']
       STALE=True
       after_repaint      =['riesgo-root', 'b', 'd', 'e', 'c', 'f']  matches_truth=True
```

So the hazard is real. It is **not reachable** through the shipped path: the one in-place mutation site (`app.py:1991`, the inspector commit) calls `refresh_canvas()` immediately, which opens a pass. Driven through the real message rather than by hand:

```
[P-R1] after shipped inspector edit (no manual repaint):
       memo =['riesgo-root', 'b', 'd', 'e', 'c', 'f']
       truth=['riesgo-root', 'b', 'd', 'e', 'c', 'f']
       REACHABLE STALE=False
```

And a census over every map-scope binding — 19 keys (`l j k h z o r f m n R I g e = x u a d`), comparing the memo against a freshly resolved truth after each:

```
[P-M1] keys driven=19 divergences=[]
```

### Different graph / different query? No.

The guard is identity + string equality. Because the memo holds a **strong** reference to the `Graph`, that graph cannot be freed and its address cannot be recycled under a different object while the memo lives — so `is` cannot alias a stale graph. This is a genuine safety property of the design, not an accident.

### A repaint path that does not open a pass? The settle-chase is safe; **export is not a repaint but is a consumer**.

`refresh_canvas` (`app.py:1897`) and `_declare_after_layout` (`app.py:1573`) both open a pass first. `_declare_after_layout` re-schedules itself while the region keeps changing, and **each invocation opens its own pass**, so the settle-chase is safe — confirmed by the resolution counts above (1 resolution across a whole settled frame, not one per settle pass).

`action_export_svg` is a third consumer and opens **no** pass — measured, see NEW-2.

### Does it hold a `Graph` alive, or key on something mutable?

```
[P-R2] memo holds a strong ref to the Graph: True
       after leaving the screen, Graph still alive=True
       memo still populated on the screen object=True
```

The memo outlives the map screen's use. It adds **no** retention beyond what `screen.graph` already holds, so this is informational rather than a leak. Keys are a `Graph` (identity) and a `str` (immutable) — neither is a mutable key.

---

## Findings

### NEW-1 — Above the render bound the count line asserts zero matches on a graph full of matches  [Severity: MEDIUM]

- **What:** `_search_order` returns `[]` above `MAX_RENDER_NODES`, and `_count_line` cannot tell that `[]` from a genuine empty result, so it paints `0 coincidencias en el mapa` — a false statement about the operator's data.
- **Where:** `mapper/app.py:1853` (the bound) feeding `mapper/app.py:1731-1737` (`_count_line`).
- **Evidence:** N=12002, graph genuinely contains 241 matches for `riesgo`:
  ```
  [P-S1] N=12002  bound=12000  real_matches_in_graph=241
         painted strip: ' <METER>   1/12002  0 coincidencias en el mapa  ▽ 12002 fuera de vista '
  ```
  The control at N=12000 (at the bound, so rendered) is correct: `1/240 coincidencias en el mapa` against 240 real matches.
- **Why it matters:** This is the **exact defect class US-N07 exists to close** — a painted count that disagrees with the graph — reintroduced at a smaller scale by the F1b repair. The code also contradicts its own two docstrings: `_search_order` claims "no tree is painted, so the count declares nothing", but the count declares *zero*; `_count_line` explicitly reserves `0 coincidencias` for "a question that was asked and came back empty", which is not this state.
- **Recommendation:** Distinguish *not computed* from *zero*. Have `_search_order` signal the bound distinctly (e.g. return `None` above it) and have `_count_line` paint **no count line at all** in that state — the strip already declares `12002 fuera de vista`, so the operator is not left uninformed. Do not close US-N07 as satisfied until this is addressed.

### NEW-2 — The open-pass protocol is enforced by an enumeration that is already incomplete, and its comment claims a derivation it does not perform  [Severity: MEDIUM]

- **What:** The memo's whole correctness argument is "every repaint opens a pass". The test that pins it iterates a hand-written two-tuple:
  ```python
  for method in (MapScreen.refresh_canvas, MapScreen._declare_after_layout):
      assert "_open_paint_pass" in _self_reads(method), method.__name__
  ```
  Its comment reads "a new repaint path that forgets it reddens here" — that is **false**. A new path added tomorrow is simply not in the tuple.
- **Where:** `tests/test_search.py:818-819`. The uncovered consumer is `action_export_svg` (`mapper/app.py:2308`), which reaches `_view_state` → `_search_hits` → `_search_order` at `mapper/app.py:2331`.
- **Evidence:** `[P-M2] passes opened during export=0 memo_identical=True` — export consumes the previous frame's memo.
- **Why it matters:** The set of pass-free consumers is already non-empty on the day the protocol ships, and the gate cannot see it. This is the vacuous-check class: a test whose docstring asserts a property stronger than its body. Combined with NEW-1's demonstrated staleness mechanism, the guard against a stale exported artifact is ordering luck, not construction.
- **Recommendation:** Derive the set instead of listing it — assert that every `MapScreen` method transitively reaching `_search_order` either calls `_open_paint_pass` or is named in an explicit, justified pass-free allowlist. At minimum, add `action_export_svg` to that allowlist with a stated reason and correct the comment.

### NEW-3 — `_search_order` hands callers the memo's own list object  [Severity: LOW]

- **What:** The memoised `list[str]` is returned by reference, so any caller can corrupt the frame's shared resolution.
- **Where:** `mapper/app.py:1857-1860`.
- **Evidence:** `[P-M4] caller receives the memo's own list=True corruption_visible_to_next_caller=True len_now=6`
- **Why it matters:** No shipped caller mutates it today (`_search_hits` freezes it; `_count_line` only reads), so this is latent. It is the kind of aliasing the `frozenset` on `ViewState.hits` was deliberately chosen to prevent one layer up, and the two decisions should agree.
- **Recommendation:** Return a `tuple[str, ...]`, or `list(order)`.

---

## Re-confirmations after the round-2 edits — all still CLEAN

- **No new sink for file-derived text.** A hostile map was built in `tempfile.mkdtemp` and loaded through the real `MapStore` — `U+202E`, `U+200B`, an ANSI introducer (`U+001B`) and Rich markup braces placed in node id, title, `meta`, notes, field value, attachment caption **and** attachment path. The count strip came back `' <METER>   1/3  1/2 coincidencias en el mapa  '` with `suspicious code points: []` and `any node id on the strip: []`. Both painted strings still interpolate only integers and a module constant (`SEARCH_COUNT_SUBJECT`, `FOLD_PILL_TOKEN`).
- **`ViewState.hits` is consumed only as membership.** Type confirmed `frozenset` at runtime; the two uses are `nid in hit_ids` (`views/layered.py:528`) and `_descendants(index, nid) & hit_ids` (`views/layered.py:598`). Never rendered as text. The renderer's own predicate `_matches` is deleted, so there is now one definition of a hit.
- **No node id reaches a widget id or CSS selector (`F-A` class).** `[P-S3] intersection: []` against the 14 live widget ids, all static literals. The new `COUNT_REGION_ID` is a module constant, not derived from data.
- **Blank-query rule still enforced at the owner**, and the new early return did not move it (evidence above).
- **No secret, token, absolute path or username added by this diff.** Scan of added lines across all four changed modules returned only prose matches inside comments.

## Pre-existing — recorded and routed, NOT fixed here

- **`F-A`** — HIGH, open, routed to Inc-REPAIR. Untouched by this diff; nothing in Inc-4a widens it.
- **`S-15`** — carried. The author's framing is honest and independently verified (see the HEAD comparison above): they closed the escalation Inc-4a introduced, not `S-15`.
- **Export-toast username path leak** — still present, `self._event_toast("exportado", str(path))`. **The line moved: it is now `mapper/app.py:2337`, not `2296`** — this diff shifted it. Route to Inc-REPAIR with the corrected line number.

## Evidence checklist

- [x] Each finding has what · where · why · recommendation — NEW-1/2/3 above.
- [x] Each finding has a severity rating — MEDIUM / MEDIUM / LOW.
- [x] No secret values appear in this output — none found; hostile code points named as `U+XXXX`, never spelled (this file is rglobbed by `tests/test_fold.py:244`).
- [x] Verdict explicit — below.
- [x] New tool/integration scope and blast radius — **N/A**: no MCP, Composio, n8n, network call, dependency or external action surface is added by this increment. The diff is entirely in-process rendering and search.
- [x] Fidelity established before measuring — `818 passed, 17 deselected, 3 xfailed`.
- [x] Real repo unmutated — 180/180 sha256 verified.

## Verdict

**F1 — DISCHARGED. F1a — DISCHARGED. F1b — DISCHARGED.** All three measured independently through the shipped key path, not reconstructed. The HIGH availability family is genuinely closed and the block is lifted.

The repair introduced **no HIGH**. It introduced two MEDIUM findings and one LOW, of which **NEW-1 is the one that matters**: the F1b bound made the count line assert `0 coincidencias en el mapa` on a graph containing 241 matches, which is the defect US-N07 exists to close, at smaller scale.

- [ ] OK to ship
- [x] **OK to ship with the listed mitigations applied first** — NEW-1 before US-N07 is claimed satisfied; NEW-2 before the memo's lifetime claim is treated as gated.
- [ ] Block

**SIGN-OFF** — the HIGH block on F1 / F1a / F1b is lifted. NEW-1 and NEW-2 are recommended, not blocking, and must not be self-cleared: route them to the author and re-confirm NEW-1 against the painted strip.
