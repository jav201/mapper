# Increment 010 — Inc-B55b — Independent Security Review

**Reviewer:** security-reviewer (independent, second and final gate)
**Range:** `git diff 10fd573..4bb63bf -- mapper/ tests/ fixtures/`
**Tree at review:** `4bb63bf`, clean on entry, clean on exit. **No source mutation was fired**
— every probe ran read-only from `C:\Users\jjgh8\clde\` against temp workspaces, so the
sha256/CRLF-anchor discipline was not exercised because nothing needed it.
**Verdict: SIGN-OFF** — one MEDIUM (carry), one LOW (hardening note). No HIGH.

---

## Verdict summary

| | |
|---|---|
| HIGH | 0 |
| MEDIUM | 1 (S1) |
| LOW | 1 (S2) |
| Verified-OK (explicitly checked, no defect) | 7 (V1–V7) |

**Coercion delta vs `10fd573`: NO LOSS, and a net GAIN in declaration honesty.** The content
coercion site count is **1 before, 1 after**, the same expression, and a hostile payload
reaches neither the frame nor the exported SVG. The one defect found is not a coercion
regression — it is a *width*-accounting gap in a surface this increment newly makes
load-bearing, and even there the increment is strictly better than what it replaced.

---

## S1 — A wide-character title falsifies the new declaration [Severity: MEDIUM]

**Where:** `mapper/views/radial.py:239-241`

```python
title = darkside.plain(node.ficha.title)[:18]
cw = len(title) + 3
x = max(0, min(inner - cw, x - cw // 2))
```

**What.** `darkside.plain` coerces *content*, not *width*. `cw` is a **code-point** count, and
`Canvas.put` (`canvas.py:103-105`) stores one code point per grid cell with no display-width
accounting, so `Canvas.rows()` emits a physical row whose cell width exceeds the logical
`inner`. An 18-code-point CJK title needs 36 display columns while the pill reserves 21. The
ownership ledger, keyed on `(x + j, y)` grid coordinates, sees no collision and declares the
node painted.

**Fired, not reasoned** — on the real composited screen (`canvas_rows(screen)` through a
Textual pilot, hostile map written to `tmp_path` only), a 4-node map whose root title is
`U+6F22 U+5B57` repeated 9 times, at a **30x20** terminal:

```
region w,h = 30 9
hidden (declared) = []            <- the canvas asserts NOTHING is hidden
 row3 |◆漢字漢字漢字漢字漢字漢字漢字 |
 row4 |漢字漢字                      |   <- the title WRAPPED onto a second physical row
DECLARED PAINTED but ABSENT from composited canvas: [('raiz', <18 cp of U+6F22/U+5B57>)]
```

At the renderer level the same map at 40x24 produces a body row of **54 display cells against
`inner = 38`**, and at 24x20 **36 cells against `inner = 22`**.

**Why it matters.** `LLR-N06.3.3` makes the absence of a node from the hidden set a **positive
claim that the operator can read it**. Here the claim is false, and the input that falsifies it
is entirely **file-derived** — the `_nodos.yml` sidecar of a map the operator opens, which in
this practice's use is routinely a file received from a client or a shared repo. Worse than the
single unreadable node: `#map-canvas` is a **wrapping** `Static` (independently measured by the
code review at F5), so an overflowing body row **consumes an extra physical row**, and on a
denser map that pushes the bottom body row out of the region — every node on it declared
painted and invisible. That is `B-61` (`app.py:1448-1458`) reintroduced through a content
channel rather than an arithmetic one.

**Scope — radial is not alone, but it is the worst.** Measured at 40x24 with an emoji title,
max body-row width against `inner = 38`: **layered 38 (correct)**, **outline 42**, **radial
41**. `layered` is width-correct because it routes titles through `darkside.fit`, which
truncates on `Text.cell_len`. `radial` is the only renderer that sizes a pill with raw `len()`.

**THIS IS NOT A REGRESSION — DO NOT READ IT AS ONE.** At `10fd573`, `_painted_ids_for` returned
`None` for radial, and `LLR-N06.3.3` makes that silence mean *"nothing is hidden"* — the **same
false claim, at every size, for every input**. This increment narrows a universally-false
declaration to one that is false only for wide-character titles at narrow terminals. The
posture strictly improves. That is why this is a carry and not a block.

**Smallest fix** (for `Inc-REPAIR`, not this increment) — size the pill in display cells:

```python
from rich.text import Text as _T
title = darkside.plain(node.ficha.title)[:18]
cw = _T(title).cell_len + 3
```

That corrects the reservation and the clamp. It does **not** fix the ledger, which would still
record one grid cell per code point; the honest full fix is for `title_cells` to record
`cell_len(ch)` cells per character, or for radial to adopt `darkside.fit`'s cell-aware
truncation as `layered` does. Recommend raising the choice at `LLR-N06.3.3` rather than
deciding it in the renderer.

---

## S2 — `overflow_phrase` is a new cross-module sink with an annotation-only contract [Severity: LOW]

**Where:** `mapper/views/layered.py:26-51`

```python
def overflow_phrase(hidden: int) -> str:
    return f"{OVERFLOW_TOKEN} {hidden} fuera de vista"
```

**What.** This increment promotes a sentence that was three local f-strings into a **public
function consumed across two module boundaries by three call sites**. It interpolates its
argument with no coercion and no runtime type check; `int` is enforced only by the annotation.

**Verified, no live defect.** All three call sites pass an integer computed from set
cardinalities — `layered.py:423` and `radial.py:368` (`len(graph.nodes) - len(painted)`) and
`app.py:2266` (`len(hidden)`). Nothing attacker-influenced reaches it today. The blast radius
even of a future mistake is small: the result lands in `Text.append(..., style=...)`, which does
not parse markup (`darkside.plain`'s docstring records why that is the actual defence), so a
stray string would be a display defect, not an injection.

**Recommendation** (hardening, not a defect): `return f"{OVERFLOW_TOKEN} {int(hidden)} fuera de
vista"`. One call, and it makes the int-only contract the function's own property rather than
a promise each of three seams must keep. Cheap enough to fold into `Inc-REPAIR`.

---

## Verified OK — checked, no defect

- **V1 — Content coercion is UNCHANGED, exactly one site, and it holds.** `grep` of
  `darkside.plain` in `radial.py`: **1 match at `10fd573:221`, 1 match at `4bb63bf:239`**, the
  same expression (`darkside.plain(node.ficha.title)[:18]`), moved only by the 4-column dedent
  the code review verified as faithful (V1 there). **Fired:** rendered a map whose titles carry
  an OSC-52 clipboard-write payload, a `U+E0020..U+E0024` TAG-block payload, and a `U+202E`
  bidi override. Residual `Cc`/`Cf`/`Zl`/`Zp` code points in the frame: **NONE**.
- **V2 — The SVG export path is unchanged and still coerced.** `git diff 10fd573..4bb63bf`
  touches **no** `mapper/export.py`, `mapper/canvas.py`, `mapper/darkside.py`, `mapper/model.py`
  or `mapper/store.py` (empty `--stat`). The export call site (`app.py:3255-3263`) is outside
  every diff hunk and reaches the canvas through `renderer.render(...)` → `_paint(...)[0]`, the
  coerced path. **Fired:** exported the hostile-payload graph to a temp SVG — residual control/
  format code points **NONE**, and the base64 payload substring **absent**. `painted_ids` is not
  on the export path at all.
- **V3 — Nothing file-derived escapes through the new return path or the new dicts.** `owners`
  values and `title_cells` keys are node **ids**, which are file-derived and never pass through
  `darkside.plain`. They leave `_paint` only inside `painted`, reach `_unpainted_ids`
  (`app.py:1648`) as `frozenset(self.graph.nodes) - painted`, and are consumed at exactly one
  site — `app.py:2262-2266` — as `if hidden:` and `len(hidden)`. Grepped every `_unpainted_ids`
  / `painted_ids` reference in `app.py`; the two other mentions are docstring prose. **No node
  id reaches a painted surface.** An integer does.
- **V4 — `_paint` is pure; the export call site cannot cross-contaminate.** No `global` or
  `nonlocal` in `radial.py`; `owners`/`title_cells` are function-local. This matters because
  `painted_ids`' own docstring justifies module-level purity by the export call site rendering
  the same long-lived renderer at a different size — that justification is now verified, not
  merely asserted.
- **V5 — The `None`-on-layout-failure invariant is TRUE for radial.** `app.py:1622` claims
  "`painted_ids` shares `_geometry` with `render`, so it raises on exactly the frames the canvas
  could not draw." **Fired** on a cyclic graph (reachable from the CSV import preview per
  `radial.py:56-59`): `painted_ids` raises `ValueError` **and so does `render`**. Both surfaces
  degrade together, so the silent strip sits beside a visibly failed canvas rather than beside a
  plausible-looking wrong one. No finding.
- **V6 — The new fixture is clean and changes no corpus posture.** `fixtures/truncado.mmd`
  (134 B) and `fixtures/truncado_nodos.yml` (305 B) are plain ASCII, LF-terminated, byte-dumped
  in full. Three benign Spanish nodes. Secret-shaped scan (`key|token|secret|password|api|
  bearer|ssh|BEGIN|@|http`) yields one hit — `key: D`, a schema field key whose label is
  `documento`, the same shape `fixtures/legacy_nodos.yml` opens with. **No attachments, no
  `kind: file`/`url`/`image`, no paths** — a strict subset of the existing corpus, which already
  carries attachments in `fixtures/anidado_nodos.yml`. **Not reachable from the shipped app:**
  no module under `mapper/` reads `fixtures/` (grep returns only two prose comments), and there
  is no packaging manifest including it. An operator would have to copy it into a workspace by
  hand, and would then get an ordinary three-node map.
- **V7 — The ledger is linear, and the render bound covers `painted_ids`.** No crafted map makes
  the ownership replay superlinear. `|owners| <= inner * body_h` (writes are gated on
  `(x+j, y) in cv.cells`, so it is bounded by the **terminal**, not by the graph, and overlap
  makes it *smaller*, never larger). `|title_cells|` is bounded at 20 entries per node
  regardless of overlap, and the `all(...)` predicate is one pass over it — **O(21·N)**, with
  no pairwise term. The `MAX_RENDER_NODES` gate sits at `radial.py:120-121`, *inside* `_paint`,
  so `painted_ids` short-circuits on an oversized graph exactly as `render` does and returns
  `frozenset()`; the strip then honestly declares every node hidden. The 1.99× amplification is
  a constant factor on a bounded, linear computation. **No DoS finding.** F12's stale rationale
  comment is a documentation carry, already recorded.

---

## Spot-checks of asserted numbers (calibration, as requested)

Three checked; **all three hold.** The comment corrections made in `540123c` are sound.

| Claim | Where | Measured | Holds? |
|---|---|---|---|
| "at 30x6 on `legacy` the region is ZERO rows, the replay paints 0 of 8, placement claims 8 — over-declares by **8 of 8**" | `radial.py:218-223` | `_canvas_size` → `h=1`, `body_h=-3`, `painted_ids` → `frozenset()`, nodes 8 | **YES** |
| "at **50x16** `_canvas_size` hands h=4 so `h-4` is 0; at **30x16** h=3 and `body_h` is -1" | `radial.py:272-276` | 50x16 → h=4, body_h=0. 30x16 → h=3, body_h=-1 | **YES** |
| "all three `overflow_phrase` callers apply `darkside.INK`" | `layered.py:38-41` | `layered.py:423`, `radial.py:368`, `app.py:2266` — all `style=darkside.INK` | **YES** |

**Bonus — the code review's HIGH is genuinely closed.** At the 20x30 size that exposed `CR-F1`,
`_canvas_size` → 20x15, `inner=18`, `body_h=11`, and the declaration is now
`hidden = ['erp', 'inv', 'rrhh']` — `erp` correctly declared **hidden**, where before the fix
it was declared painted with its last character shorn off.

**Suite baseline:** full run at `4bb63bf`, **984 passed, 19 deselected, 3 xfailed** in 245 s.
The named flake (`test_llr_cnv_3_1_...`) did not fire on this run. Per the brief, I weight this
green as a *weaker* green and did not rest any finding on suite colour alone — every conclusion
above is from a probe I ran, not from a passing test.

---

## Boundaries

**Reviewed.** All 5 diffed source/test files plus both new fixtures byte-for-byte.
`mapper/canvas.py` (`put`, `rows`, the bounds guard), `mapper/darkside.py`
(`plain`, `fit`, `COERCION_RANGES`, `PRESERVED_CODE_POINTS`), `mapper/export.py`,
`mapper/app.py` (`_canvas_size`, `_unpainted_ids`, `_painted_ids_for`, `_pagination_text`, the
export call site), and `mapper/views/layered.py` / `outline.py` for the width comparison.

**Fired (5 probes, all read-only, nothing written inside the repo).**
(1) hostile-payload render — OSC-52 + TAG-block + bidi, frame residual check;
(2) hostile-payload **SVG export** to a temp dir, residual + payload-substring check;
(3) width-integrity probe at 40x24 / 24x20 across **all three renderers**, CJK and emoji;
(4) a **Textual pilot** driving the real screen at 40x24 and 30x20 on a hostile map written to
`tmp_path`, reading the composited `#map-canvas` region — this is what produced S1's wrap;
(5) the cycle-path probe (V5). Plus the three numeric spot-checks and one full suite run.

**Did not review** (out of lane, or already gated). Functional/coverage adequacy and the F4
truncation gap → `qa-reviewer`. Correctness of the ownership predicate itself → settled by the
code review, whose HIGH I re-verified as closed rather than re-derived. Test-quality findings
F2–F12 — I did not re-litigate them. The export toast's username (carried, exposure
**UNCHANGED** — I confirmed the export call site is outside every diff hunk and did not
re-report it). `AGREE-1`, Defect 2, `F2`, `DECL-118-TWICE`, `SEC-F1`, outline's remaining
spelling — all carried, not re-reported.

**Could not determine.**
(a) **The wrap threshold.** I fired one wrap at 30x20 with CJK. I did **not** map how many
overflow columns are needed to push a body row out of the region at each size, so I cannot tell
you the density at which S1 escalates from "one unreadable label" to "a whole row of nodes
declared painted and invisible". If that number matters to the severity, it needs measuring
before `Inc-REPAIR` chooses a fix.
(b) **Whether `node.ficha.title` can be empty in production** — inherited unresolved from the
code review; I did not trace the model's constraints either, and it is orthogonal to S1.
(c) **Whether outline's 42-cell overflow is a live defect or benign** — it is outside this
increment's cut and I measured it only to scope S1. Someone should look, but not here.

---

## Evidence checklist

- [x] **Each finding has what · where · why · recommendation** — S1 (`radial.py:239-241`, fired
  on the composited screen, cell-aware `cw` fix), S2 (`layered.py:26-51`, `int()` coercion).
- [x] **Each finding has a severity rating** — S1 MEDIUM, S2 LOW. Zero HIGH, so the hard rule
  against an unmitigated "OK" is not engaged.
- [x] **No secret values in this output** — none were encountered; the fixture scan's only hit
  is a schema key. Hostile code points are named as `U+XXXX` per `C-56`; the base64 payload I
  injected is my own test string and is referenced by presence, never pasted.
- [x] **Verdict explicit** — SIGN-OFF (below).
- [x] **New tool/integration scope and blast radius addressed** — **none added.** No new
  dependency, no MCP/Composio/n8n connector, no network call, no new outbound surface, no new
  file write. The only new external-state path in the diff is the two fixture files, and V6
  shows they are unreachable from the shipped app.
- [x] **Data-flow / LFPDPPP check** — the one path on which client data leaves the machine is
  `export.save_svg`, and it is **byte-identical to `10fd573`** and still coerced (V2). No client
  data crosses a new boundary in this increment.

---

## Boundary attestation

Sole writer; **no evidence of another writer** — `git status --porcelain` empty on entry and on
exit, `git diff --stat` empty, `git rev-parse HEAD` = `4bb63bf` throughout. No mutating git
command was run. **No source mutation was fired**, so no restore was required; all probe
scripts live in `C:\Users\jjgh8\clde\` and every map the probes built was written to a
`tmp_path` or a `tempfile.mkdtemp()`, never into `fixtures/`. The exported probe SVG went to
`%TEMP%`. `PYTHONUTF8=1` and `PYTHONDONTWRITEBYTECODE=1` on every run. The only repo file this
review writes is this artifact.

---

## Verdict

- [ ] OK to ship
- [x] **OK to ship — SIGN-OFF.** No HIGH. `S1` and `S2` are carried to `Inc-REPAIR`, neither
      blocks, and `S1` is explicitly a **narrowing of a pre-existing false claim**, not a
      regression: at `10fd573` radial's silence asserted "nothing is hidden" at every size for
      every input; it now asserts it falsely only for wide-character titles at narrow terminals.
      Content coercion is unchanged and verified intact on both the frame and the exported SVG.
- [ ] Block

**Carried to `Inc-REPAIR`:** `S1` (cell-aware pill width in radial; raise the ledger's
code-point-vs-cell question at `LLR-N06.3.3`), `S2` (`int()` in `overflow_phrase`).
**Handed to `qa-reviewer`:** a wide-character title has no fixture and no arm — the suite cannot
currently fail on `S1`. The new `fixtures/truncado` corpus is the natural home for one.
