# Security Review — Inc-B55a (`outline` declares what it hides)

**Reviewer:** security-reviewer (independent, second and final gate)
**Tree:** `C:\Users\jjgh8\Github\mapper` @ `d79602c`, working tree clean before and after.
**Verdict:** **SIGN-OFF** — no HIGH. Two MEDIUM/LOW findings recommended, neither blocking.

---

## Scope reviewed

| Reviewed | Not reviewed |
|---|---|
| `mapper/views/outline.py` — whole file, and diffed against `3122519` (pre-increment) | `mapper/darkside.py`, `mapper/widgets/chrome.py` (Inc-CRUMB, already gated) |
| `mapper/app.py` — `_painted_ids_for`, `_unpainted_ids`, `_declare_after_layout`, `_rendered_for`, `refresh_canvas`, `_pagination_text`, `_canvas_size`, `_view_state`, `on_resize`, `_apply_region_visibility`, `_focus_owner` | `mapper/views/radial.py`, `mapper/views/lane*` (out of cut) |
| `tests/test_a3_census.py`, `tests/test_inc3_census.py` diffs (the two pins this increment moved) | Wording/register of the new Spanish string (routed to `UI-AT058`) |
| `increment-009-b55a.md`, `…-code-review.md`, `02m`/`02n`/`02o`, `state.json` → `p3_progress` | The carried export-toast username (exposure unchanged) |

**I mutated nothing.** No source edit was needed to fire the findings below; the only repo file I created was a temporary probe under `tests/`, deleted before this report. `git status --porcelain` is empty at `d79602c`, `__pycache__` purged, `git rev-parse HEAD` = `d79602c3011734517134f1a17667e38b87a44d62`. **No evidence of another writer.**

---

## What I fired vs. what I reasoned about

| # | Probe | Method | Result |
|---|---|---|---|
| T1 | Hostile title **and** meta (RLO, PDF, ZWSP, ZWJ, NUL, BEL, ESC-CSI, BOM, bidi isolates, TAG block, combining marks, astral, soft hyphen, TAB) through `render` **and** `painted_ids` at **100** `(w,h)` combinations incl. `w=1`, `h=0` | fired | **0 leaks.** No codepoint from `COERCION_RANGES` reached the frame or the id set |
| T2 | Is `rows[0]` — the header the declaration is appended to — file-derived? | fired | **No.** `rows[0][1].plain == "◆ mapper · outline"`, `nid is None`. Refutes the stated suspicion |
| T3 | Hostile node **id** through `_rows`'s cycle `ValueError` | fired | Raw `str(exc)` carries 13 hostile codepoints; its only sink (`refresh_canvas`'s `except`) applies `darkside.plain`. Coerced. Pre-existing |
| T4 | Can one file-derived title evict the whole canvas? | fired | **Yes** — see F2 |
| T5 | Does the 3-pass fixed-point bound ever ship a numeral ≠ the truth? ~15,000 frames swept (title width 1..29 × w 10..59 × h 1..11) | fired | **0 mismatches.** The bound is not reachable as a lie by this input family |
| T6 | Cost of a pathological title through `Console.render_lines` | fired | 200k-char title: 65 ms `render` + 68 ms `painted_ids`. 2000-LF title: 54 + 54 ms |
| T7 | `render` / `painted_ids` agreement on the composited cut, hostile fixture, 114 sizes | fired | **0 disagreements** |
| T8 | `_rendered_for` desynchronisation | fired (Textual pilot) | **P1 violated, two surfaces contradict** — see F1 |
| — | `LookupError` reachability and message flow | reasoned + read | Not data-reachable; message never painted. See "Verified clean" |
| — | Full suite | fired | `968 passed, 19 deselected, 3 xfailed` |

---

## Findings

### F1 — `_rendered_for` records geometry, so the settle guard can decline the re-render the content needs — and the two declaring surfaces then contradict each other  [Severity: MEDIUM]

- **What:** `self._rendered_for` (`app.py:1228`) stores `(w, h)` only. The guard at `app.py:1703` skips the settle re-render when the geometry matches. But the canvas's content is a function of the **renderer** plus **nine** `ViewState` fields (`selected_id`, `focus_owner`, `hits`, `diff`, `pan_x`, `pan_y`, `folded`, `w`, `h`). The guard keys on two of them. When any of the other eight — or the renderer identity — changes without an intervening `refresh_canvas`, `_declare_after_layout` believes the frame is reconciled, skips, and the strip is repainted from the **new** state against a canvas holding the **old** one.

- **Where:** `mapper/app.py:1703` (the guard), `:1228` (the state), `:2455` and `:1714` (the two writers).

- **The docstring's claim is false as written.** `app.py:1691-1696` states *"The guard is `P1` itself, not a second mechanism… the predicate skipped on is the same one the invariant asserts, so the guard cannot drift from the property it protects."* `P1` as the increment defines it is *content and geometry agree at rest* — but "content" is not determined by geometry, so the predicate is **strictly weaker** than the invariant. It is not `P1`; it is a projection of `P1` onto two of its ten inputs. This batch's recorded failure mode is a comment asserting more than the code does, and this is one.

- **Fired.** Pilot at `(50,16)`, `legacy`, settled geometry `(50,4)`, `_rendered_for == (50,4)`. I mutated `screen.outline_mode = True` (no `refresh_canvas`) and armed the settle exactly as `on_resize` does:

  ```
  canvas row0 AFTER : '◆ mapper · árbol legacy▰▰▰▰▰   8 nodos  ▽ 7 f…'   <- layered, says 7
  strip      AFTER  : ' ▰▱▱▱▱▱▱▱   1/8  ▽ 5 fuera de vista '             <- outline, says 5
  geometry   AFTER  : (50, 4)   _rendered_for = (50, 4)                  <- guard skipped
  P1 HOLDS?         : False
  ```

  That is **`B-60` reintroduced through the mechanism built to prevent it**: the canvas and the strip declaring different totals for the same frame, and the settle pass — the thing that used to reconcile them by re-rendering unconditionally — is now the thing that declines to.

- **Why it matters:** the product's entire promise (`LLR-N06.3.3`) is that the operator is never shown a frame that misrepresents what is hidden. Here both declaring surfaces are simultaneously non-silent and mutually inconsistent, which is worse than silence: the operator has two numerals and no way to know which describes the pixels in front of them. Pre-`Inc-B55a` this could not happen, because `_declare_after_layout` re-rendered unconditionally. **This is a capability the increment adds.**

- **Reachability today — stated honestly:** I audited **every** assignment to `self.graph`, `outline_mode`, `radial_mode`, `nav.cursor`, `pan_*`, `folded`, `diff_active` and the search state in `app.py`. Every one is followed by `refresh_canvas()`, which resets `_rendered_for`. So **no shipped keybinding reaches F1.** The nearest operator-reachable variant is `on_field_input_left` (`app.py:2577-2581`): `escape` out of an inspector field calls `set_focus(None)` with no `refresh_canvas`, changing `_focus_owner()`, which `layered.py:643` reads to decide the selection-block tone — carry `B-05`'s exact defect. To land it you additionally need a resize that leaves `(w,h)` unchanged, which requires the `max(20, …)` width floor at `_canvas_width` (`app.py:1470`) with the inspector pinned visible at a sub-58-column terminal. Contrived, cosmetic, and I did **not** fire that variant. **F1 is therefore a latent hazard with a false docstring, not a live defect** — hence MEDIUM, not HIGH.

- **Smallest fix (two lines, no new mechanism):**

  ```python
  # app.py:1228 / 2455 / 1714 — record what the content was actually produced FROM.
  self._rendered_for: tuple[object, ViewState] | None = None
  ...
  self._rendered_for = (renderer, self._view_state(w, h))   # refresh_canvas
  ...
  if (self._current_renderer(), self._view_state(w, h)) != self._rendered_for:   # the guard
  ```

  `ViewState` is `@dataclass(frozen=True)` (`views/state.py:61`) so `==` is already correct and total, and the comparison is O(fields) — it cannot regain the 0.33 s the guard exists to avoid. This makes the guard's predicate genuinely equal to `P1`, which is what the docstring already claims. **If the fix is deferred, the docstring at `app.py:1691-1696` must be corrected in this increment** to say the guard keys on geometry and is sound only under the (unenforced) invariant that every state mutation calls `refresh_canvas`. Shipping the claim as written is the part I will not wave through.

### F2 — one file-derived row's physical cost is unbounded, so a single title can evict the entire map at any terminal size  [Severity: LOW]

- **What:** `_fit` (`outline.py:199-204`) prices each row with `render_lines` and breaks when `used + cost > h`. No per-row ceiling. `darkside.plain` deliberately passes **TAB and LF** through (`darkside.py:476`, "C0 except TAB and LF"), and imposes no length bound. So one node's title can cost more physical rows than the whole budget, and `_fit` then keeps **nothing** past the header.

- **Where:** `mapper/views/outline.py:199-204`; enabler at `mapper/darkside.py:476, 504-515`.

- **Fired** (9-node graph, root title hostile, children benign):

  ```
  LF x50      80x24: painted=0/9  rows=1  header='◆ mapper · outline  ▽ 9 fuera de vista'
  200k chars  80x24: painted=0/9  rows=1  header='◆ mapper · outline  ▽ 9 fuera de vista'
  TAB x400    80x24: painted=0/9  rows=1  header='◆ mapper · outline  ▽ 9 fuera de vista'
  LF x3       80x24: painted=9/9  rows=12 (control — normal frames unaffected)
  ```

  TAB is the realistic vector: Rich expands to 8 cells, so ~400 tabs in a `.mmd` label costs 40 rows at width 80 and eats a 24-row budget. No hostility required — a copy-pasted label can do it.

- **Why it matters — and why it is only LOW.** The map vanishes, but **the frame does not lie**: it declares `▽ 9 fuera de vista`, and T7 confirms the strip agrees. This is degraded-but-truthful, which is the behaviour `LLR-N06.3.5` asks for. It is also **not a regression**: pre-`Inc-B55a` the logical slice `lines[:h]` kept all nine rows, the compositor clipped the eight children off-screen anyway, and **nothing declared them** — the new code loses the same content and says so. Coercion is unchanged either way.

- **Smallest fix (optional, recommend routing to Inc-REPAIR rather than doing it here):** cap one row's charge and mark the overrun, e.g. in `_fit`:
  `cost = min(max(1, len(console.render_lines(line, pad=False))), _MAX_ROW_ROWS)` with `_MAX_ROW_ROWS = 3` — the row still paints (the compositor clips it) and the rest of the map survives. Bounding the *title* instead (a `darkside.fit`-style truncation at the `_rows` title site, which `layered` already does via `_fit(title, card_w - 3)` at `layered.py:647`) is the more principled cut and would close it for every renderer at once — but it changes what `outline` paints, which is outside this increment's approved 2-file cut.

### F3 — the declaration doubles the per-frame walk over file-derived content  [Severity: LOW — overlaps a carry, reported for the measurement only]

- **What:** `render` and `painted_ids` each call `_rows` (walks every node) and `_fit_declared` (up to 3 `_fit` passes). Per frame the file-derived text is now walked **twice**, and `_declare_after_layout` can add a third pass when the geometry moves.
- **Where:** `mapper/views/outline.py:294` and `:307`.
- **Measured:** 200k-char title → 65 ms `render` + 68 ms `painted_ids`; 2000-LF title → 54 + 54 ms. Roughly **2× amplification** of a cost that previously existed once. Scaling is linear in the pathological input, not super-linear — I found **no** input family that makes `render_lines` blow up non-linearly, including combining-mark and astral sequences (T1).
- **Why it matters:** a self-inflicted, local, file-triggered slowdown only. No remote surface, no third party, no client data movement. **The ~150 ms `painted_ids` walk on near-bound graphs is already carried to `Inc-REPAIR`;** this finding adds the amplification factor and the pathological-title regime to that carry. It does not warrant its own action.

---

## Verified clean (reasoned or fired, with the evidence)

| Claim | Evidence |
|---|---|
| **No coercion loss vs `57fb403`.** The two coercion sites in `outline.py` — `darkside.plain(node.ficha.title)` (`:136`) and `darkside.plain(node.ficha.meta)` (`:163`) — are **byte-identical** to `3122519` | `git show 3122519:mapper/views/outline.py`, diffed. No third site existed then or now |
| **No coercion gain either.** The new seams consume `Text` already built in `_rows`; they add no sink | Read. T1: 0 leaks over 100 sizes |
| **`render_lines` on hostile `Text` is inert.** `Text` never parses markup (`darkside.py:508-511`, verified as the real design, not just a claim), and `_fit` discards the rendered output — only `len()` is used. `Console(no_color=True)` writes to no stream | `outline.py:196-205`; T1 |
| **The new header declaration is bounded and carries no file-derived text.** `rows[0]` is the static wordmark; the appended token is `▽` + an `int` ≤ `MAX_RENDER_NODES` (5 digits) + a literal | T2. **This refutes the suspicion put to me** that the declaration is appended to the root node's title. It is not — that is a `_rows` body row, not `rows[0]` |
| **The 3-pass bound does not ship a wrong numeral** in a ~15,000-frame sweep | T5: 0 mismatches |
| **`LookupError` is not data-reachable.** `_painted_ids_for` (`app.py:1623`) dispatches on **instance identity** against the three renderers `MapScreen` constructs. No parse path, fixture, or operator action substitutes a renderer | Read + `tests/test_overflow.py:1228,1243-1246` |
| **The `LookupError` message never reaches the frame.** `_pagination_text` (`app.py:2219-2222`) catches it and paints a **fixed literal**, not `str(exc)`. So `type(renderer).__name__` — the only interpolated value — cannot carry attacker-influenced text anywhere | Read `app.py:2219-2222` |
| **`_unpainted_ids` has exactly one production call site**, and the raise is confined to it | Grep across `mapper/`: `app.py:2219` only |
| **`_rows`'s cycle `ValueError` interpolates a file-derived node id**, and its only sink coerces it | T3. Pre-existing, unchanged |
| **A cyclic map makes the strip silent in outline** (`ValueError` → `_unpainted_ids` `except` → `None`). **Not a regression** — outline returned `None` unconditionally before | Read `app.py:1615-1617` |
| **Full suite green, tree byte-identical to `d79602c`** | `968 passed, 19 deselected, 3 xfailed`; `git status --porcelain` empty |
| **No secrets, credentials, tokens, env files, network calls, subprocesses, filesystem writes or new dependencies** in the cut | Full read of both files |
| **No LFPDPPP / client-data exposure.** Everything stays on the operator's screen; nothing leaves the local system | Full read of both files |

---

## What I could not determine

1. **Whether a `.mmd` / `.yml` title can actually contain `LF`.** I did not read the parsers. TAB and raw length are clearly reachable and are enough to carry F2, so I did not chase it. If titles are line-delimited at parse, the LF arm of F2 is unreachable and only the TAB/length arms stand.
2. **Whether F1's operator-reachable variant (escape-from-field + width-floored resize) actually lands.** I fired the mechanism, not that path. I state F1 as latent rather than live on the strength of the mutation-site audit, not on a negative experiment — an audit can miss a site.
3. **Whether `rich`'s cell-width machinery has a super-linear regime** on some grapheme family I did not construct. T1 and T6 found none across combining marks, astral pairs and 200k-char rows. Measured, not proven.

---

## Evidence checklist

- [x] Each finding has what · where · why · recommendation — F1/F2/F3 above.
- [x] Each finding has a severity rating — MEDIUM, LOW, LOW.
- [x] **No secret values appear in this output.** No secret was found; hostile codepoints are named as `U+XXXX` per `C-56` and never pasted verbatim.
- [x] Verdict is explicit — **SIGN-OFF**, below.
- [x] No new tool/integration was added — nothing reaches the network, the filesystem, a subprocess, or a third party. Scope and blast radius are unchanged from `57fb403`; N/A by absence, verified by reading both files end to end.

---

## Verdict

- [x] **OK to ship — SIGN-OFF.** No HIGH finding. The security surface I was asked to verify holds: **no coercion is lost or bypassed** by the new seams, the new declaration **carries no file-derived text**, the `LookupError` path is **not data-reachable and paints no exception text**, and the bounded fixed point **does not ship a false numeral**.
- [ ] OK to ship with the listed mitigations applied first
- [ ] Block

**Two things I ask for, neither blocking:**

1. **F1 — do one of these before close.** Either take the two-line `ViewState` fix, or correct the docstring at `app.py:1691-1696` so it stops claiming the guard *is* `P1`. The measurement behind the guard is sound; the explanation attached to it is not, which is the specific failure mode this batch keeps paying for.
2. **F2/F3 — route to `Inc-REPAIR`** alongside the `painted_ids`-walk carry already there. A per-row cost ceiling in `_fit` closes F2; neither belongs in this increment's 2-file cut.

**On the calibration offered:** I spot-checked five claims in the new comments. Four held under firing — the physical-row cut is real and the logical slice genuinely shipped a lie (T4's control row); the fixed point genuinely settles (T5); the declaration genuinely informs rather than manufacturing its own omission (T4b); `rows[0]` genuinely is the renderer's own header. **One did not: the `P1`-guard docstring (F1).** The security surface *stated* to me was also wrong in one place — the canvas header does not carry the root node's title — and the correct answer is stronger than the guess, not weaker.
