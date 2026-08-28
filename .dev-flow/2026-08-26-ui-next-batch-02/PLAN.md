# PLAN — `2026-08-26-ui-next-batch-02` · variant B «atlas» + round-10 capabilities

> **Living compendium.** Updated at every gate and every significant checkpoint. The operator reads
> this file, not `state.json`. Artifact language: **English** (code and engineering docs); **UI
> strings are Spanish** — the project convention, unchanged.

---

## 1 · BLUF — where we are

**Station: PDR, REJECTED at the second pass (2026-08-27) — returning to P1 for amendment set 3.
Read §15 first; it supersedes the status lines below.** The PDR second pass ran four lenses over the
41-amendment fold: architect **REJECTED**, security **BLOCKED**, qa and ux approved-with-conditions
but ux carrying two blocker-class items. Twelve blockers carry into set 3, including a **live `S-02`**
(the un-park's `SATISFIED-EXTERNALLY` strike `D18` is wrong), a **phantom requirement**
(`LLR-STO.1.1`), and **`docs/ARCHITECTURE.md` never actually amended** despite §7 recording ARQ as
approved. A rejection returns to design: **no increment opens.**

**Station (historical): P1, iterating (fold iteration 1). UN-PARKED 2026-08-27 on a new base.** The batch was
parked at its PDR gate on 2026-08-26 with **13 blockers** (10 qa + 3 security) so a repair batch
could ship the four defects the gate had found. That batch merged (`e164a28`); its close,
`d877784`, is this batch's new base. **The parked record is not carried — every premise was
re-executed against the post-repair tree**, and four of the parked scope items came back
`SATISFIED-EXTERNALLY`.

The batch implements the operator's round-9 verdict for variant **B «atlas»** (canvas mechanics)
plus the round-10 capabilities approved for batch 2: **sala** (home 2.0), **lente** (field query),
**leyenda por vista** (`?`), and the **palette-v2 tokens**. It also closes carry **B-05** and the
real `Canvas.rows()` layer-drop defect.

**The one structural fact that shapes this batch:** `IRenderer.render` is frozen, and US-N06
cannot be built without extending it. That is trigger **A3**, it is **pre-authorised in the brief**,
and it forces ARQ + PDR + DDR to be live stations. The migration of every renderer and every call
site happens in **one increment, never half**.

**The un-park record is §12; the blocker fold ledger is §13.** Read those two before §6, whose
premise verdicts are the *parked* run and are superseded where §12 says so.

---

## 2 · Objective

| Field | Value |
|---|---|
| Batch id | `2026-08-26-ui-next-batch-02` |
| Objective | Variant B «atlas» canvas mechanics (pan · fold · overflow · braille edges) + search hit-count/navigation + home 2.0 «sala» + field-query «lente» + per-view «leyenda» + palette-v2 tokens |
| Mode | `full` (client-grade V-model; merge authority granted) |
| Predecessor | `2026-08-25-ui-next-batch-01`, merged `e359148`, closed at `d6b60e6` |
| Base ref (RC-1) | `origin/master` = `d6b60e6b4f18b10123fffc76bbb36891473df653` |
| Flow revision | rev46 (`~/.claude` clean, level with `origin/main`; V7 GREEN, aggregate `9c1449ed815d267c`) |
| Baseline suite | **245 tests collected**, `pytest -q --collect-only`, 2026-08-26 |
| Toolchain | Python 3.12.7 · textual 8.2.8 · ruff 0.8.4 · mypy 1.13.0 · pytest — all present, entry gate PASS |

---

## 3 · Batch-kickoff authorization (recorded verbatim)

Authorization is **per-batch and never carried**. The operator granted it for this batch on
2026-08-25/26:

| Item | Answer |
|---|---|
| Autonomy + **merge authority** | **GRANTED.** Operator's words: *"delega a un opus5 la implementación con /dev-flow… hace push y merge"* and *"todo entra"*. Direction and batch order approved after two prototype rounds. |
| Merge gate that still applies | The grant does **not** waive the gate. After the PR is opened and validation is green, an independent **security sign-off** and an adversarial **PR-level `qa-reviewer` pass over the whole diff vs `master`** must both come back clean before merge. Batch 1's precedent: both found real data-loss defects. A HIGH finding blocks the merge and returns to the operator. |
| Decision recording | Every decision taken instead of asking is recorded in §9 of this file, in `state.json.decisions_log`, in the post-mortem, and carried to the vault at `/dev-flow-sync`. |
| Stop conditions | Scope outside the brief, or un-mitigable data-loss risk. |

---

## 4 · Scope

### In — five stories + tokens

| id | Story | Prototype spec |
|---|---|---|
| US-N06 | **escala** — canvas pan (viewport), fold/expand branches with «▸ rama +N» pills, declared-overflow indicator. *Nothing clips silently.* | `b1_atlas`, `b2_peek` |
| US-N07 | **búsqueda** — hit count + `n`/`N` navigation in every view; visibly distinct empty-result state; hits highlighted as WARN pills | `b1_atlas` |
| US-N13 | **sala** — home 2.0: per-map constellation thumbnail (lit dot = node with acta), coverage microbar, due badges, linked `⇄` and repo `◍` markers, welcome seat so the create door is never blank | `n1_sala` |
| US-N14 | **lente** — `key:value` field query (AND of terms) over schema fields incl. state; matches lit, rest dimmed to ground; `⇥` walks results with the inspector focused; saved lenses on number keys; counts declared | `n4_lente` |
| US-N16 | **leyenda** — `?` opens the **current view's** legend: its real bindings from the keymap seat spec plus its glyph vocabulary. `??` reserved for the guía (batch 3) — routed to a stub | `n6_leyenda` |
| HLR-canvas | `Canvas.rows()` honours the `dots`/`bgs` layers; atlas-style braille free-angle edges for the map canvas. Closes carry **B-05** (focus-unaware selection tone). | `b1_atlas`, `b2_peek` |
| tokens | Paleta v2 into `mapper/darkside.py` with jobs as constants + docstring: `SAGE` `#2fbf71` (completitud/vigente) · `TEAL` `#22b8cf` (procedencia repo) · `VIOLET` `#9775fa` (relaciones/enlaces). Blue stays interactivity-only; severity stays WARN/ALERT. | round-10 verdict |

### Out — declared, not forgotten

recorrido / guía (batch 3) · cronoscopio / relieve (batch 4) · repo-screen redesign (batch 3) ·
the C «plano» blueprint language. **`prototypes/**` is never touched and never staged.**

---

## 5 · Trigger evaluation

*(Recorded per **C-48**: non-activation is evidence too, and carries its probe. Re-evaluated at
every gate for families C and F, and at every increment cut for family B.)*

| id | Verdict | Probe / evidence |
|---|---|---|
| **A1** creates a module or moves a boundary | *pending ARQ* | Decided at ARQ once the increment cut exists. |
| **A2** touches ≥2 modules | **FIRED** | Scope names `canvas`, `views`, `design`, `widgets`, `screens`, `search`, `app`, `keymap` — 8 modules. |
| **A3** changes an interface another module consumes | **FIRED — pre-authorised** | `IRenderer.render` is declared **frozen** in `docs/ARCHITECTURE.md:136` and R-010. US-N06 needs viewport + fold state inside the renderer. The brief pre-authorises the change for this batch; ARQ/PDR record the new frozen signature and one increment migrates every renderer and call site. Measured surface: **6** `def render` across `mapper/views/{lane,layered,outline,radial}.py`, **3** call sites in `mapper/app.py` (`:711`, `:1301`, `:1671`), plus renderer-driving tests in `test_app / test_lane / test_layered / test_legacy_fixture / test_outline / test_radial / test_export`. |
| **A4** plans parallel increments | *pending ARQ* | Batch 1 measured 0 of 15 pairs parallelisable, all colliding on `mapper/app.py`. Re-derived at ARQ, not inherited. |
| **B1** touched symbol asserted by other requirements' tests | **FIRED** | `.render(` appears in 7 test files not owned by this batch's stories (list above). Reverse census owed per increment. |
| **B2** moves a file's on-disk location | *pending* | No move planned yet; re-evaluated at each increment cut. |
| **B3** touches a source a byte-identical golden captures | **NOT FIRED** | `ls tests/goldens` → no such directory; the repo has no byte-identity goldens. |
| **B4** produces an artifact another component consumes | **FIRED** | `Canvas.rows()` output is consumed by every renderer and by `export.save_svg/save_png`. Honouring `dots`/`bgs` changes those bytes. |
| **C** security pattern families | *re-run at every gate over the diff* | Scope adds **file-derived text into new rendered surfaces**: map titles into home thumbnails, ficha field values into the lens query and the legend. C-17's family. `osopen` is not touched. |
| **D1** alters something the user sees or touches | **FIRED** | Every story is a UI change. `ux-reviewer` is a live lens at PDR. |
| **D2** prototype built in a different technology than the target | **FIRED** | The specs are **SVG renders from Python generators**, not running Textual. Interactions (pan keys, `⇥` walk, `n`/`N`, `?`) are **UNVERIFIED for Textual** and every AT must drive the real key. C-16 — batch 1 measured this premise FALSE and it reshaped every acceptance test. |
| **E1** ≥3 stories or ≥3 increments | **FIRED** | Five stories plus tokens. |
| **F** flow currency | **NOT FIRED** | V7 GREEN: local flow is rev46 and matches its manifest (aggregate `9c1449ed815d267c`); `~/.claude` is level with `origin/main` (`git rev-list --left-right --count HEAD...@{u}` → `0 0`). Backlog refreshed 2026-08-25 at batch-01 close. |

---

## 6 · Premises executed at Phase 0 (C-43)

*(Full table with tiers and dispositions lands in `01-requirements.md` §2.7. Executed against disk,
never trusted. Verdicts here are the Phase-0 run.)*

| # | Premise | Tier | Verdict | Executed evidence |
|---|---|---|---|---|
| P-1 | `Canvas.rows()` silently drops the `dots` and `bgs` layers, so `RadialRenderer`'s braille edges and pill backgrounds never reach the screen | premise | ✅ **TRUE** — the defect is real | `mapper/canvas.py:67-82` reads only `self.cells` and `self.bits`. `radial.py:47-48` assigns `cv.dots = {}` / `cv.bgs = {}` onto the instance and writes to both (`:121`, `:135`). Executed: rendering a 6-node graph at 80×24 yields **0** glyphs in the braille block `U+2800–U+28FF`; the distinct painted set is `['A','B','C','H','R',…,'·','◆','●']`. |
| P-2 | `IRenderer.render` is uniform across renderers and has exactly 3 production call sites | premise | ✅ **TRUE** | `grep -rn "def render" mapper/views/` → 6 definitions in 4 files (`lane.py:108,171,311`, `layered.py:78`, `outline.py:17`, `radial.py:33`). Production call sites: `mapper/app.py:711`, `:1301`, `:1671`. |
| P-3 | Palette-v2 tokens do not exist in the product today | premise | ✅ **TRUE** | `grep -n "2fbf71\|22b8cf\|9775fa\|SAGE\|TEAL\|VIOLET" mapper/**/*.py` → **no output**. |
| P-4 | `darkside.microbar(count, total, width, fill)` already exists and is reusable for the sala coverage bar | premise | ✅ **TRUE** | `mapper/darkside.py:232`. |
| P-5 | `?` already opens a **scope**-aware help, so US-N16 extends a surface rather than creating one | premise | ✅ **TRUE** | `mapper/app.py:1986-1987`: `self.push_screen(HelpScreen(getattr(self.screen, "KEY_SCOPE", SCOPE_APP)))`. Four screen-level `action_help` forwarders at `:742`, `:793`, `:1058`, `:1828`. |
| P-6 | Search today is a bare `Input` with no hit count and no n/N navigation | premise | ✅ **TRUE** | `mapper/app.py:1107` (`Input(placeholder="/buscar", id="search-input")`), `:1524` `action_search`, `:1531`/`:1539` submit/change handlers. No count, no cursor, no `n`/`N` binding in `mapper/keymap.py`. |
| P-7 | The module map is current — every tracked `mapper/**` file falls under a declared module | premise | ✅ **TRUE** | `git ls-files 'mapper/*'` → 33 files; each matches a declared `paths` entry in `docs/ARCHITECTURE.md` §2. 0 undeclared. |
| P-8 | The project has no byte-identity goldens (B3's negative) | premise | ✅ **TRUE** | No `tests/goldens/` directory; `ls tests/` lists 27 `test_*.py` files and `conftest.py` only. |
| P-9 | Validator V8 cannot check this project's map because the map declares per-file paths, not `path/**` prefixes | premise | ✅ **TRUE** | `devflow-validate.py` → `[!] V8 docs/ARCHITECTURE.md: map declares no path/** prefixes — it cannot be checked`; the rule's regex (`:249`) matches only `` `X/**` `` tokens. Disposition: decided at **ARQ** — see §9. |
| P-10 | The prototype SVGs verify **design intent only**; no interaction in them is verified for Textual | hypothesis | ❌ **FALSE as a verification claim** — recorded as C-16 | The generators emit SVG from Python; nothing runs Textual. Batch 1 measured the same premise FALSE and it changed every AT (`05-postmortem.md:20-24`). Disposition: **every AT in this batch drives the real key or the real gesture**; a proxy (`.focus()`, calling `action_*`) is not acceptance. |

### Premises executed after the structural census

*(A census report is **a document**. C-43 is explicit that citing a document is not evidence, so
every claim below that this batch will build on was re-executed against disk. **One came back
different from the report** — P-13 — which is the whole argument for the rule.)*

| # | Premise | Tier | Verdict | Executed evidence |
|---|---|---|---|---|
| P-11 | **`n` is already taken in map scope**, so US-N07's "n/N navigation" collides with a shipped binding | premise | ✅ **TRUE — a design decision, not a free key** | Executed over `KEYMAP`: `map 'n' -> next_gap 'siguiente faltante'`; `home 'n' -> construct`. `N` is bound in **no** scope. `keymap.duplicate_chords()` + `test_no_duplicate_chord_inside_one_scope` will reject a second map-scope `n`. **PDR must settle this**, not the implementer. |
| P-12 | **Repo provenance is recorded nowhere in the product**, so US-N13's `◍` marker has no data source today | premise | ✅ **TRUE — a scope question** | `grep -rn "provenance\|repo_slug\|source_repo\|from_repo" mapper/` → **no output**. `RepoScreen` builds a `Graph` in memory and never persists it; `.mapper/state.json` holds `{map_id, node_id}` only. Marking repo origin requires **new persisted state**. Disposition: settled at PDR — see §9 D-3. |
| P-13 | Two screens drop the scope when routing `?` | premise | ❌ **FALSE — it is three, not two** | The census report named `_ImportPreviewScreen` and `PlugRepoScreen` and recorded `RepoScreen` as *"same delegation"*. Executed: `mapper/app.py:742`, `:793` **and `:1058`** all read `self.app.push_screen(HelpScreen())` — no scope argument. Only `MapScreen:1828` delegates to the scope-aware `MapperApp.action_help:1986`. US-N16 inherits **three** broken routes, not two. |
| P-14 | `OutlineRail.NodeSelected` is declared but never posted and never handled | premise | ✅ **TRUE — dead code** | `grep -rn "NodeSelected" mapper/ tests/` → one hit, the declaration at `mapper/widgets/rail.py:26`. No `post_message`, no handler. |
| P-15 | `MapStore` exposes no map-listing API; callers hand-glob the workspace | premise | ✅ **TRUE** | No `def list_maps` in `mapper/store.py`. Two hand-globs: `mapper/app.py:421` (inside a 14-iteration day loop) and `:451`. |
| P-16 | The canvas is a bare `Static` with no scroll container and no offset, so pan has nothing to build on | premise | ✅ **TRUE** | `mapper/app.py:1101` composes `Static("", id="map-canvas")`; CSS `#map-canvas { width: 1fr; height: 100% }` (`:1889-1907`). `LayeredRenderer` writes absolute `cv.put(cx + j, y, …)` and clips by `lines[:h]`. Pan is **new mechanism**, and it is why the renderer contract has to move. |
| P-17 | `Graph.search_hits` returns ids in dict-insertion order, not tree order | premise | ✅ **TRUE** | `mapper/model.py:169-184` iterates `self.nodes.values()`. `n`/`N` walking that order jumps around the canvas. The tree-order idiom already in the tree is `MapScreen._incomplete_order` (`app.py:1601-1623`). |
| P-18 | The renderer's inline query predicate and `Graph.search_hits` **disagree** about what a hit is | premise | ✅ **TRUE — two definitions of "hit" ship today** | `views/layered.py:144-149` matches title + notes + field values. `model.py:169-184` additionally matches `node.id`, `ficha.meta` and attachment captions/paths. A hit **count** taken from one and a highlight taken from the other would disagree on screen. US-N07 must name **one** owner. |
| P-19 | The batch's own baseline is **245 collected nodes**, not the 155 the census reported | premise | ✅ **TRUE — executed** | `pytest -q --collect-only` → `245 tests collected`. A `def test_` count returns **116**; 96 collected node ids carry a `[` parametrization suffix. The census's 155 matches neither. **The ledger uses collected node counts** — this is the C-40 rider (*an arm the harness cannot see is an arm it cannot report inert*) showing up as a bookkeeping error before a single line was written. |
| **P-20** | **The rail \| canvas \| inspector layout renders correctly at the sizes where all three are visible** | axiom (batch 1's headline deliverable, shipped and merged) | ❌ **FALSE — and it is a total-functionality-loss defect on `master`** | See the block below. |

### P-20 — the shipped layout defect, measured under Pilot

**BLUF: on any terminal wide enough for the rail to be shown, the map canvas and the ficha inspector
are laid out entirely off-screen. The operator sees the rail and nothing else.**

Root cause, executed: **`#map-rail` has no CSS width rule at all.** `mapper/app.py:1889-1907` styles
`#map-canvas { width: 1fr }` and `#map-inspector { width: 36 }` and never mentions `#map-rail`.
`RAIL_WIDTH = 24` (`mapper/widgets/rail.py:18`) is used **only** to truncate text inside the rail's own
`render` (`:122`, `:124`, `:142`) — it is never applied as a width. Meanwhile `MapScreen._chrome_width()`
(`app.py:1166`) subtracts `24 + 36` from the terminal width and hands the result to the renderer as `w`,
an assumption nothing enforces.

Measured with `App.run_test()`, reading `widget.region` (post-layout, authoritative) and the compositor's
own painted strips:

| terminal | rail region | canvas region | inspector region | canvas on screen? |
|---|---|---|---|---|
| 140 × 45 | `x0 w140` | `x140 w1` | `x141 w36` | ❌ **no** |
| 120 × 40 | `x0 w120` | `x120 w1` | `x121 w36` | ❌ **no** |
| 100 × 30 | `x0 w0` (auto-hidden) | `x0 w64` | `x64 w36` | ✅ yes |
| 80 × 24 | `x0 w0` (auto-hidden) | `x0 w80` | `x0 w0` (auto-hidden) | ✅ yes |

Painted row 10 at 140 × 45 is `      Nomina` — rail content only. The compositor is 140 columns wide,
so a canvas at `x=140` is past the last addressable column.

**Why 245 green tests cannot see it.** `_apply_region_visibility` (`app.py:1172-1186`) auto-hides the
rail when the canvas would fall below `MIN_CANVAS_WIDTH = 58`. Below ~118 columns the rail is hidden and
the layout is correct — so the suite, running at default and small Pilot sizes, exercises **only the
sizes at which the bug is absent**. This is **C-55 limb 2 verbatim**: the guard is a no-op on today's
data, and the emptiness is an accident of the sizes the tests happen to use.

**Candidate remedy, executed — not proposed:** adding `#map-rail { width: 24 }` restores the layout at
exactly the arithmetic `_chrome_width()` already assumes.

| terminal | rail | canvas | inspector | check |
|---|---|---|---|---|
| 140 × 45 | `x0 w24` | `x24 w80` | `x104 w36` | `140 − (24+36) = 80` ✓ |
| 120 × 40 | `x0 w24` | `x24 w60` | `x84 w36` | `120 − (24+36) = 60` ✓ |

The canvas paints the map (`▐ Finanzas … ▐ RRHH … ▐ Inventarios`) at both sizes. **That the remedy
reproduces `_chrome_width()`'s own numbers is the evidence that the missing rule is the defect and the
arithmetic was right all along.**

**Disposition — folded into this batch's scope.** Shipping pan, fold and an overflow indicator onto a
canvas that is not on screen is not a deliverable. It is one CSS line plus its geometry AT; it lands in
the first increment that touches the canvas, and it gets a regression test that **drives a wide Pilot
size**, since the size is the thing the suite was blind to.

---

## 7 · Roadmap — stations

| Station | Status | Note |
|---|---|---|
| **P0** intake | ✅ **approved** | RC-1 clean at `d6b60e6`; toolchain PASS; 20 premises executed (17 TRUE / 3 FALSE, all dispositioned); triggers recorded; 6 READY + 1 REFINE |
| **ARQ** | ⚠ **approved, but its map amendment NEVER LANDED — see §15.4 `ARQ-1`** | ~~Map amended (+456/−248 lines)~~ **FALSE against disk**: `docs/ARCHITECTURE.md` still declares the old frozen `render` signature at `:58` and `:136`. The amendment lives only as `ARCHITECTURE-proposed-at-ARQ.md`. Original text follows. Map amended (+456/−248 lines), byte-scan clean, **V8 now GREEN**. New frozen signature committed to; Q-1, Q-2, Q-4 answered; **0 of 21 increment pairs parallelisable** (the sala-as-a-lane hypothesis measured FALSE — `HomeScreen` is declared at `app.py:338`); R-009 ruled NO and scheduled; a second A3 (`Canvas`) surfaced and routed to PDR |
| **P1** requirements | ✅ approved (iteration 1) | 21 HLR · 48 LLR · **44** AT (3 rejected as phantom) · 71 TC · IFC Parts A + B |
| **PDR** | ❌ **REJECTED at pass 2 (2026-08-27) — `iterate-to-refine` to P1, iteration 2 of 3 — see §15** | **Pass 2:** architect **REJECTED** (6 blockers; flags ruled as `#D21`/`#D22`); security **BLOCKED** (`S-16`/`S-17`/`S-18`); qa + ux approved-with-conditions, ux carrying 2 blocker-class. **Pass 1 (historical):** architect **approved-with-conditions** (20 sealed decisions; cut re-derived **7 → 9** increments); **qa BLOCKED — 10 blockers / 14 majors / 11 minors**; **security BLOCKED — 3 blockers / 6 majors / 5 minors**. Two further shipped defects (**S-01** cycle/deep-recursion crash, **S-02** non-string ficha field) reproduced independently by the orchestrator. **Scope decision referred to the operator** — see §11. |
| **P2** cross-review | pending | 3 lenses in parallel |
| **P3** implementation | pending | increment cut derived at PDR; ≤4 source files per increment; `code-reviewer` gate per increment |
| **DDR** | pending | crossed reverse census, C-18 sweep, summed ledger |
| **P4** validation | pending | one complete suite run owned by the orchestrator |
| **P5** post-mortem | pending | |
| **P6** docs + PR + merge | pending | security sign-off + adversarial PR-level QA gate before merge |

---

## 8 · Risks and watch-items

| # | Risk | Mitigation |
|---|---|---|
| R-1 | **The A3 migration half-lands.** Extending `render` across 6 definitions and 3 call sites plus 7 test files is the batch's largest blast radius. | One increment, never split. Reverse census of `.render(` derived from the code, not by eye (post-mortem §2.2). The old signature must not survive anywhere — asserted, not assumed. |
| R-2 | **A counterfactual that only deletes.** Batch 1 shipped **five** green-suite weakenings that reviewers caught. | Every security- or correctness-critical control gets a **plausible wrong implementation** mutation, not only removal. Per-arm verdicts, never the process exit code. |
| R-3 | **New file-derived text reaching new rendered surfaces** — map titles into thumbnails, ficha values into lens results and the legend. C-17's family, and batch 1 found the identical defect in siblings of the file it had cleaned. | Requirements scoped to the **sink class**, not to a file. Hostile-input ATs. `security-reviewer` is a live lens. |
| R-4 | **`mapper/app.py` is ~1900 lines and every increment reaches into it.** | R-009 says extraction re-opens when ≥3 increments touch `app.py` for unrelated reasons *and* there is slack. Evaluated at ARQ as a real decision, with its cost stated. |
| R-5 | **Escape sequences collapsing into control bytes.** Three incidents in batch 1, one of them silent (an inert regex that passed on everything). | No escape spelled into source or into an evidence artifact; construct or describe. Byte-scan every touched file before each commit. Every probe carries a positive control. |
| R-6 | **Counts hand-maintained in docs.** | Derived (`git show --stat`, collected node ids), never recalled. Batch 1's own budget disclosure under-reported itself. |

---

## 9 · Decision log (autonomous decisions, recorded not asked)

| # | Date | Decision | Why |
|---|---|---|---|
| D1 | 2026-08-26 | Mode `full`, stations ARQ + PDR + DDR live | A3 fires on a frozen interface; the brief pre-authorises the change and requires the ARQ/PDR steps. E1 and D1/D2 also fired. |
| D2 | 2026-08-26 | Batch id `2026-08-26-ui-next-batch-02`; the batch owns its **own** `01-requirements.md` created at open | The validator's artifact walk otherwise judges this batch against a historical document. Measured hazard, flow-encoded. |
| D3 | 2026-08-26 | **S-7 folded into scope** — the shipped off-screen-canvas layout defect | Pan, fold and an overflow indicator painted onto a canvas laid out past the last addressable column is not a deliverable. One CSS line; the remedy was executed before it was proposed. Owes an escaped-bug RED against `master`. |
| D4 | 2026-08-26 | **Q-1 answered: a `ViewState` frozen dataclass, not additive kwargs.** New frozen signature `render(self, graph: Graph, state: ViewState) -> Text`; `**kwargs` abolished from all six definitions | Decided on measured evidence, not taste: **the additive-kwarg shape is already broken here.** `app.py:1671` passes `query=` without `diff=` while `:1301` passes both, so an SVG exported during a diff **silently drops the tinting today**; and `outline`/`radial`/`lane` declare `**kwargs` and drop `query` on the floor, which makes US-N07's "hit count in *every* view" unbuildable while that swallow lives. Adding a defaulted `ViewState` field later is additive and never A3; ten loose kwargs make every future capability another A3 argument. Recorded as **R-012**; **R-010 marked SUPERSEDED, exactly as R-010 predicted.** |
| D5 | 2026-08-26 | **Q-2 answered: `MapScreen` owns fold state.** `OutlineRail.collapsed` / `.toggle` are removed; the rail receives it via `show(graph, cursor, folded)` | Rejected leaving it in the rail on **ownership lifetime**, not style: `_apply_region_visibility` auto-hides the rail below `MIN_CANVAS_WIDTH = 58`, so fold must keep working on an 80-column terminal where the owning widget is not displayed. Recorded as **R-013**. |
| D6 | 2026-08-26 | **Q-4 answered structurally: `search` becomes the single owner of "what matches".** The lens parser lands in `search`, not `model`; `views/layered.py:144-149`'s inline predicate is **deleted** | Two live definitions of "hit" cannot both survive when the story's whole promise is that the count is trustworthy. The edge `views → search` is deliberately **not** created — the renderer receives `frozenset[str]` id sets, never a predicate. Recorded as **R-014**. |
| D7 | 2026-08-26 | **Validator V8 adopted rather than declared non-applicable.** Three coverage roots declared in a new §2b: `mapper/**`, `tests/**`, `prototypes/**` | Executed against `devflow-validate.py:244-261`: **V8 computes orphans only and runs no double-claim check**, so §2's stated objection is aimed at a check V8 does not perform, and adopting it costs the per-file discipline nothing. Now GREEN — `3 modules, no orphan files`; validator 0 block / 19 notice. |
| D8 | 2026-08-26 | **R-009 ruled NO for this batch, and scheduled as batch 3's Inc-0** | Limbs 1 and 2 are now **met** (7 of 7 increments touch `app.py`, across four genuinely disjoint regions); limb 3 (slack) is not — 1494 lines into ≥5 files, plus 8 test files importing `mapper.app`. **The decisive argument is sequencing, not size:** the extraction moves every `.render(` call site, which is exactly the surface R-1's reverse census must count, so taking it against a file that just changed identity converts a countable check into a judgement call at the worst moment. It goes on `BACKLOG.md` at close — deferring a third time without scheduling is how R-009 becomes a decision nobody makes. |
| D9 | 2026-08-26 | **A second, unnamed A3 surfaced and is routed to PDR: `Canvas`** | §4 declares `Canvas` frozen ("yes for MVP") and the HLR-canvas work moves it. The change is additive/widening, but `rows()`'s output bytes change and `export.save_svg` consumes them (trigger **B4**). The brief did not anticipate this freeze move, so **PDR approves it explicitly** alongside the renderer one rather than letting it ride in unremarked. Recorded as **R-016**. |
| D10 | 2026-08-26 | **Q-3 answered: option (a).** Search takes `n` / `N`; `next_gap` moves `n → M`. New seat rows: `map/n → next_hit "siguiente coincidencia" (nav)` · `map/N → prev_hit "coincidencia anterior" (nav)` · `map/M → next_gap "siguiente faltante" (view)` | Executed over `KEYMAP`: the collision is a **semantics** problem, not scarcity — free lowercase in map scope is `b c i p s t v w y`, every uppercase except `A I R X` is free, and `duplicate_chords()` returns `[]`. **Option (c), the state-dependent chord, was rejected because it cannot survive the whole-seat pin:** under (c) `map/n` has no constant `label`, leaving only two exits — pin a placeholder, which stops pinning the displayed string and is *verbatim narrowing #2 from post-mortem §2.4c* (the one under which swapping the `u`/`z` labels kept all 245 tests green), or make the spec state-dependent, which is no longer set equality. It also breaks one-declaration-four-readers, since `groups_for_keybar` returns `binding.label` straight from the seat. `M` chosen because `m` is already `cobertura` and walks the same tree order — `m` opens the report, `M` walks it; the seat already carries two genuine shift-pairs (`a`/`A`, `x`/`X`). **Condition:** the seat-spec diff is exactly one changed row plus two added rows, reviewed row-by-row at DDR. |
| D11 | 2026-08-26 | **Q-6 answered: an unresolvable lens query is never executed.** `Z:algo` → canvas **unchanged**, chip ` Z ? sin definir ` in ALERT, line `el mapa no define el campo «Z» · campos: …` with the field list **derived from `graph.schema`**. `E:inexistente` → figure-ground **applied**, chip in MUT, line `0 nodos · ningún nodo tiene estado = inexistente` | Executing an unresolvable query would dim the entire canvas and paint **identically** to a zero-match result. Distinguishing *"the map has no such field"* from *"nothing matches"* is the difference the story exists to make. |
| D12 | 2026-08-26 | **S-8 folded into scope — a third shipped defect: `?` hides ten of its own bindings** | See the block below. |
| D32 | 2026-08-28 | **Inc-1 CLOSED and pushed (`4eaba35`).** `code-reviewer` BLOCK on 1 HIGH → fixed → confirmation pass *"the HIGH is discharged, no HIGH survives"*; `security-reviewer` signed off. 4 source files (the declared cap); 6 battery rounds; 154 arms | Four unplanned defects, two of them **in the sealed spec**: `WARN`'s job made `LLR-S06.3.5`'s own threshold unsatisfiable by any implementation (`A-78`); the C0 range row omitted `U+000D`, so adopting it verbatim **narrowed** shipped coverage (`A-80`); `radial` sliced titles raw into the exported SVG; and `AT-009` derived its oracle from the constant it was testing, staying green while 19 invisible code points reached the artifact (`A-87`). The confirmation pass additionally caught a **fabricated measurement in production source** — a probe that constructed the theme it then observed — and a "fix" of mine that repaired nothing |
| **D33** | 2026-08-28 | **`B-47` folded into `Inc-3`; `LLR-COERCE.2` widened from one named truncator to every renderer feeding an operator-visible sink (`A-89`)** | **Coordinator ruling — recorded as such, NOT as operator approval.** The batch's coercion guarantee held only in radial view while `LayeredRenderer` is the **default**; measured, a hostile title through layered or outline writes an SVG that is not well-formed XML. **The narrowing lived in the `Touched symbols` line, not in the Statement**, which was already general — the transferable lesson. `Inc-3` declares a 5-file breach; the renderer set is **derived**, never hand-listed, because a hand-listed set is the defect class this batch has already paid for twice |
| **D34** | 2026-08-28 | **`B-46` gets its own increment, `Inc-CONFIRM`, with `Inc-REPAIR` and before `Inc-7` (`A-90`)** | **Coordinator ruling.** `_ConfirmScreen` renders a ficha title through a markup-parsing sink while composing the dialog that **gates subtree archival** — the newly-reachable-destructive-action class, and the fix is the `darkside.plain` the same function already applies seven lines above. Two acceptance arms, one per failure mode (crash · action-span injection), because they fail independently and one arm would let the other ship. Named rather than numbered so no substring scan collides it |
| **D35** | 2026-08-28 | **Pace calibrated, not uniform (`A-91`)** | **Coordinator ruling.** Full protocol (review + confirmation pass + battery) retained for `Inc-2`, `Inc-3`, `Inc-REPAIR`, `Inc-CONFIRM`, `Inc-7` — anything touching a data path, a destructive action, the A3 contract or a security sink. Lighter protocol (single review, no confirmation pass) permitted for a presentational increment **only while** the review returns zero HIGH and no data path is touched; **any HIGH restores the full protocol for that increment**. Batteries are never skipped, only sized. Recorded so the post-mortem can judge the trade — Inc-1 is the control, and its confirmation pass returned 7 MEDIUM + 6 LOW |

### S-8 — the help overlay silently truncates, and it hides exactly the keys this batch adds

**BLUF: `?` paints 17 of 27 map-scope bindings, and the ten it drops are the entire `view` group.**
Executed at **both** 118 × 34 **and** 200 × 80 — identical result, so this is **not** a small-terminal
problem:

```
size=(118, 34): declared=27  painted=17  MISSING=10
size=(200, 80): declared=27  painted=17  MISSING=10
   missing -> ['f alternar foco', 'o alternar outline', 'r alternar radial', 'e exportar svg',
               '= alternar diff', 'n siguiente faltante', 'R mostrar/ocultar rail',
               'I mostrar/ocultar ficha', 'g ir al rail', 'z plegar rama']
```

Root cause: `mapper/screens/help.py:36-39` styles `#help-dialog { height: auto; max-height: 28 }` on a
**non-scrolling** `Vertical` whose content needs ~38 rows. The overflow is discarded in silence.

**Why this is load-bearing for THIS batch rather than a carry.** `z plegar rama` is the fold chord
US-N06 extends, and US-N16's entire promise is that `?` explains the current view. A legend that drops
the group containing the keys the batch is adding ships the story's own counterexample.

**And it dictates how US-N16's central assertion must be written.** The set-equality check — *the keys
painted equal `keymap.bindings_for(scope)`* — **must read the painted panel**, never `_render_keymap()`'s
return value: asserted against the return value it **passes today on a panel showing 17 of 27**. That is
**C-32** (assert the painted result, never a geometry-independent proxy) deciding a requirement instead of
being recalled at review. The row budget is already adverse — 27 bindings plus a 21-row glyph vocabulary
against 34 terminal rows — so scrolling or panes is a **requirement**, not an implementation detail.

### Decisions D13 – D15, from Phase 1 (each re-executed before ratification)

| # | Decision | Executed evidence |
|---|---|---|
| D13 | **P-13 is corrected upward: FIVE routes drop the help scope, not three.** The requirement is quantified over the derived screen set, and additionally requires every screen to **declare** a `KEY_SCOPE` | My own Phase-0 census was scoped to `app.py` and missed two — **the exact failure shape P-13's own disposition was written to prevent** (batch 1 §2.1b: a requirement scoped to a file gets satisfied at that file's boundary). Executed tree-wide: `grep -rn "HelpScreen(" mapper/` → `app.py:743`, `:794`, `:1059`, **`screens/factory.py:416`**, **`screens/settings.py:95`**. Underneath it, `grep -rn "KEY_SCOPE"` shows `FactoryScreen` and `SettingsScreen` declare **none** — so a route-only fix resolves to app scope and still paints the wrong legend: **a fix that would pass its own test.** |
| D14 | **Three coverage percentages ship, and two disagree by 100 points on the same map.** Folded into `LLR-N13.1.3` — one owner, one definition | On a schema-less map `app.py:379` computes `int(100 * have / max(1, req))` → **0 %**, while `views/layered.py:119` and `widgets/rail.py:149` both compute `… if req else 100` → **100 %**. US-N13's coverage microbar cannot be built on three disagreeing definitions. |
| D15 | **An undeclared hue ships:** `#a3a3a3` at `mapper/views/radial.py:18`, in no token set | Found **only because the census input set was derived from the tree rather than hand-listed** — C-31 paying for itself before implementation began. It is now in scope for S-6's "blue stays interactivity-only, severity stays WARN/ALERT" census, which must account for it rather than pretend it is absent. |

### Q-7 — a new blocking question Phase 1 raised: `⇥` is forbidden

The brief specifies *"`⇥` walks results with the inspector focused"* for US-N14. **Two shipped, green
tests forbid it**, and `tab` is load-bearing:

- `tests/test_keymap.py:160` bans any `tab` entry in the seat; `:165` bans any screen binding `tab`
  outside `TAB_BINDING_EXCEPTIONS`, which is `('SettingsScreen', 'EditorScreen')` — **`MapScreen` is
  not in it.** Executed: `pytest -k tab` → **9 passed**.
- `tab` is the **only keyboard route to the inspector**: 9 real presses give 9 distinct focus targets.
- Batch 1 measured that a screen-level `tab` binding produces **0 focus moves in 9 presses**, so
  binding it would not even work.

**Orchestrator recommendation to PDR — do not take a new chord; unify the concept.** Search hits and
lens matches are both *coincidencias*, and only one result set can be live at a time, so `n` / `N`
(`siguiente coincidencia` / `coincidencia anterior`, already added by D10) walk **whichever result set
is active**. This is **not** the state-dependent label rejected in D10: the label is true in both
cases, so the whole-seat pin stays a static set equality. `⇥` keeps its shipped job — focus traversal.
**PDR rules on it.**

### Corrections the PDR QA lens made to MY OWN artifacts (recorded, not quietly fixed)

Three of the QA lens's findings correct the orchestrator's work rather than the requirements author's.
Each was re-executed before being accepted:

| # | What I wrote | Executed truth |
|---|---|---|
| C-1 | **§5 trigger B1 declared the A3 reverse census as "7 test files".** R-1's whole mitigation was sized against that number. | `grep -rn "\.render(" tests/ mapper/` → **29 sites across 14 files**, 13 of them test files. **My census was 6 files short.** This is post-mortem §2.2 repeating verbatim — a census keyed on files noticed by eye instead of derived from the code. R-1 is re-sized against 29/14. |
| C-2 | **§6 P-19 claimed "155 matches neither" unit.** | 155 **is** the `def test_` count: **116 sync + 39 async**. My grep counted only `^def test_` and missed `async def test_`, so I declared a real number spurious and then built a lesson on it. The *conclusion* survives — the ledger unit is the **245 collected** node count — but the arithmetic under it was wrong, and a probe with no positive control is exactly what post-mortem §2.4b warns about. |
| C-3 | **I recorded the legend defect as "17 of 27 painted" (S-8) and `HLR-N16.1` was built on it.** | Region-clipped to the widget actually under test, the true count is **16**. `HelpScreen` is a `ModalScreen` with `background: #000000 70%`, so `MapScreen`'s keybar **composites through the translucent backdrop** and `m cobertura` was counted as a legend row. At 240 × 100 the same oracle returns **19**. I diagnosed C-32 correctly and then discharged it with an oracle that still reads cells belonging to another widget — and **no AT pins a Pilot size**. |

**C-3 is the one worth sitting with.** I named "assert the painted result, not a proxy" as the
controlling lesson, wrote it into the requirement, and then produced a painted-result oracle that was
itself wrong — because *painted* is not the same as *painted **by the widget under test***. The QA lens
did confirm the live C-32 example stands: the naive oracle over `_render_keymap()` passes set-equality
**27 / 27 today over a panel that paints 16**.

### Findings ARQ produced that were not asked for

Four rows of the standing module map were **provably false** and are now corrected — each verified
independently by execution before ratification:

| Map claim | Executed truth |
|---|---|
| `MapStore.load -> (Graph, Sidecar)`, `save(map_id, graph, sidecar)`, public `reindex()` | `store.py:199` → `load(map_id) -> Graph`; `:217` → `save(map_id, graph)`; `:288` → `_reindex`, **private**. Wrong in two separate sections of the map. |
| `Canvas` exposes `dline` | `grep -rn "dline" mapper/ tests/` → **no output**. The method does not exist. |
| `search` depends on `model`, `store` | `search.py` imports only `.model`. |
| `app` depends on `search` | **`mapper/app.py` does not import `search`. `mapper/search.py` has zero consumers anywhere in `mapper/` or `tests/` — it is dead code.** It is therefore treated as new code that happens to have a legacy filename. |

**And the one that matters most: `IRenderer` does not exist.** `grep -rn "IRenderer" mapper/` returns
**two prose mentions inside comments** — no class, no Protocol. The interface this batch was told was
"frozen" has been enforced by a markdown table and nothing else. Promoting it to a `runtime_checkable`
Protocol in `mapper/views/state.py` makes the freeze **mechanically checkable for the first time**.

---

## 10 · Conventions honoured

- UI strings **Spanish**; code, tests, docs and commit text **English**.
- `mapper.db` is never committed. `prototypes/**` is never staged by this batch.
- Every binding added is declared in the `keymap` seat **and** in the whole-seat conformance
  specification `{(scope, key): (action, label, glyph, priority, group)}`. Counts in docs are
  derived, never hand-maintained.
- No control bytes in any file; every touched file byte-scanned before commit.
- Increment packets declare their **SOURCE** file count (validator V9).

---

## 11 · PDR verdict and the scope question referred to the operator

**Consolidated verdict: BLOCKED — `iterate` to Phase 1.** Blockers force iteration; no increment starts.

| Lens | Verdict | Findings |
|---|---|---|
| architect | **approved with conditions** | 20 sealed decisions; both A3 moves approved (`ViewState.with_header` struck as uncited and never once passed); cut re-derived **7 → 9** increments |
| qa | **BLOCKED** | **10** blocker · 14 major · 11 minor |
| security | **BLOCKED** | **3** blocker · 6 major · 5 minor |

### Four shipped defects found that were NOT in the brief

| id | Defect | Reproduced by the orchestrator |
|---|---|---|
| **S-7** | Rail\|canvas\|inspector: canvas and inspector laid out **off-screen** at any width where the rail shows | ✅ `widget.region` + compositor strips |
| **S-8** | `?` paints **16 of 27** bindings; the missing set is exactly the 11-member `view` group | ✅ Pilot at 118×34 and 200×80 |
| **S-01** | A **cycle** in a `.mmd` `RecursionError`s both renderers; a depth-500 chain does too. `refresh_canvas` has no guard, so the app dies | ✅ with a positive control |
| **S-02** | A **non-string ficha field** loads clean, then `AttributeError` in `missing_required` and `TypeError` in `search_hits`; `coverage()` silently counts it as documented | ✅ with a positive control |

**The principled scope rule proposed:** *this batch repairs exactly what its own stories make newly
reachable, and nothing more.* S-7 and S-8 are preconditions of US-N06 and US-N16. S-01 and S-02 become
reachable **without opening anything** because US-N13's sala loads every map in the workspace on mount.
Under that rule all four are in; nothing else is.

### Corrections to the orchestrator's own artifacts

Recorded in full in §9: the A3 census was **6 files short** (29 sites / 14 files, not 7); P-19's
arithmetic was wrong (155 = 116 sync + 39 async); and the S-8 count was 17/10 rather than the true
**16/11**, because a translucent modal backdrop let another widget's keybar composite into the oracle.
A fourth: an S-02 reproduction attempt first returned a **plausible** all-clear because the fixture used
the wrong sidecar shape — re-run with a positive control, it reproduced. A plausible zero reads as data.

---

## 12 · UN-PARK record — 2026-08-27

> **Everything in this section was executed against the tree at `d877784` in this session.** The
> parked artifacts (§1–§11, `01-requirements.md`, `01b`, `01c`, `02a`, `02b`, the PDR) were read,
> but **no claim in them is relied on without re-execution** — C-43's rule that citing a document
> is not evidence applies with extra force here, because the tree underneath them moved.

### 12.1 — RC-1 and the new base

| Check | Result |
|---|---|
| `git fetch origin` then HEAD / `origin/master` / merge-base | all three = `d8777840313145fec341687f0081afd7230c755b` — **clean, no rebase needed** |
| Superseded base | `d6b60e6` (the parked run's base) |
| Intervening merge | `e164a28` — PR #2, `2026-08-26-repair-batch` |
| Repair-batch diff vs the parked base | **14 files, +4241 / −184**: `mapper/{app,mermaid,model,store}.py`, `mapper/screens/{factory,help}.py`, `mapper/views/{layered,outline,radial}.py`, `mapper/widgets/rail.py`, and four new test files |
| Baseline suite | **429 passed**, exit 0, 133.35 s — `pytest -q -p no:randomly -o addopts=`, one complete run, read from its own captured output (C-19 / C-25) |
| Baseline collected | **429** — `pytest -q --collect-only -p no:randomly -o addopts=`. The parked baseline of **245 is superseded**; the ledger unit stays *collected node ids*, never `def test_` |
| Toolchain | unchanged and present: Python 3.12.7 · textual 8.2.8 · ruff · mypy · pytest, `PYTHONUTF8=1` |

### 12.2 — The mechanical validator, scoped to this batch

`python ~/.claude/docs/tools/devflow-validate.py .` gives **62 block · 107 notice · 12 n/a** over the
whole `.dev-flow/`. Scoped by rule, and each block dispositioned rather than counted:

| Rule | Count | Where | Disposition |
|---|---|---|---|
| **V2** | 47 | `tests/` | **Expected, not a defect.** Every `AT-NNN` this batch declares is unimplemented — implementation has not started. V2 is the C-18 realisation gate and it is *supposed* to be red here. It converts to a real gate at Phase 4. **It also independently corroborates QA-B-03**: 47 ids are declared, and the review measured only 44 predicates. |
| **V12** | 12 | `01-requirements.md:2250`, `:2265`, ... | (X) **REAL — blocks, folded as F-14.** IFC Part B does not balance: `rail` consumes `cursor, folded` and emits `rail_tree_rows`; `canvas` consumes `state` and emits `canvas_rows, painted_map` — none declared on the parent `map_screen`. Containment is a set operation and the parent's list is short. |
| **V7 / V16** | 3 | `~/.claude`, `~/.claude/skills` | (!) **Notice against an AUXILIARY repo, reported as FOUND — not swept up (C-44).** Both are **4 commits ahead of `origin/main` and never pushed**, and `FLOW-VERSION.md` consequently disagrees with the manifest (`5abe414d8e2fdb1f` vs `9c1449ed815d267c`). These commits **pre-date this session**; committing or pushing another session's work in progress is its own defect. The **PULL** half of C-45 is satisfied — `git rev-list --left-right --count HEAD...@{u}` gives `4 0`, i.e. **0 behind**, so this batch does not run a stale flow. The **PUSH** half is broken by work that is not this batch's. Carried to `BACKLOG.md` at close. |

### 12.3 — Premises re-executed against `d877784`

The parked §6 table is the **`d6b60e6` run**. Re-executed here; **five verdicts moved.**

| # | Premise | Parked | Now | Executed evidence at `d877784` |
|---|---|---|---|---|
| P-1 | `Canvas.rows()` drops the `dots` / `bgs` layers | TRUE | **STILL TRUE — the defect is live** | `mapper/canvas.py:67-82` reads `self.cells` and `self.bits` only; `Canvas.__init__` (`:30-33`) declares neither `dots` nor `bgs`. `mapper/views/radial.py:123-124` still assigns `cv.dots = {}` / `cv.bgs = {}` onto the instance and writes at `:209` and `:224`. **The repair batch did not touch this**, and it remains the HLR-canvas story. |
| P-2 | `render` surface: 6 definitions, 3 production call sites | TRUE | **TRUE, at new addresses** | 6 defs: `lane.py:108,171,311` / `layered.py:131` / `outline.py:47` / `radial.py:107`. 3 production call sites: `app.py:737`, `:1352`, `:1727`. Every parked line number is stale. |
| P-3 | Palette-v2 tokens absent | TRUE | **TRUE** | `grep -rn "2fbf71\|22b8cf\|9775fa\|SAGE\|TEAL\|VIOLET" mapper/ --include="*.py"` returns no output. |
| P-4 | `darkside.microbar` exists | TRUE | **TRUE** | `mapper/darkside.py:232`. |
| P-5 | `?` is scope-aware at the app level | TRUE | **TRUE** | `mapper/app.py:2050`. |
| P-6 | Search is a bare `Input`, no count, no `n`/`N` | TRUE | **TRUE** | `app.py:1138` composes `Input(placeholder="/buscar", id="search-input")`; `:1580` `action_search`; `:1587`/`:1595` handlers. No count, no cursor. |
| P-13 | Routes that drop the help scope | FALSE (3, corrected to **5** at D13) | **5 CONFIRMED — unchanged by the repair batch** | `grep -rn "HelpScreen(" mapper/` gives `app.py:774`, `:825`, `:1090`, `screens/factory.py:489`, `screens/settings.py:95`, all constructing `HelpScreen()` with **no scope**. Only `app.py:2050` passes one. `grep -rn "KEY_SCOPE"` shows **no declaration in `factory.py` or `settings.py`** — so a route-only fix still paints the wrong legend. **US-N16 inherits all five.** |
| P-14 | `OutlineRail.NodeSelected` is dead | TRUE | **TRUE** | `grep -rn "NodeSelected" mapper/ tests/` gives one hit, the declaration at `widgets/rail.py:26`. |
| P-15 | No `MapStore.list_maps`; callers hand-glob | TRUE | **TRUE** | No `def list_maps` in `store.py`. Hand-globs at `app.py:421` (inside the 14-iteration day loop) and `:476`. |
| P-16 | The canvas is a bare `Static`, no scroll container, no offset | TRUE | **TRUE** | `app.py` composes `Static("", id="map-canvas")`; pan is still new mechanism. |
| **P-20 / S-7** | The three-region layout is broken | FALSE (defect) | **REPAIRED — `SATISFIED-EXTERNALLY`** | `#map-rail { width: 24 }` shipped; guarded by `tests/test_repair_layout.py::test_tc_r22...` (CSS literal vs `RAIL_WIDTH`, deliberately able to disagree), `test_at_r10...` (three regions disjoint and on-screen, parametrized over wide sizes), `test_at_r10b...` (the discriminating negative, rail absent), `test_at_r11...`, `test_tc_r23...`. |
| **S-8** | `?` paints 16 of 27 bindings | FALSE (defect) | **REPAIRED — `SATISFIED-EXTERNALLY`** | `mapper/screens/help.py:49-53` adds `#help-bindings { height: 1fr; overflow-y: auto }` inside a `VerticalScroll`. |
| **S-01** | A cycle or a deep chain kills the app | FALSE (defect) | **REPAIRED — `SATISFIED-EXTERNALLY`** | `store.py:304` raises a typed `MapStoreError(f"el mapa tiene un ciclo: ...")`. `MAX_RENDER_NODES = 12000` declared in all three renderers (`layered.py:15`, `outline.py:14`, `radial.py:28`) and enforced at `layered.py:143`, `outline.py:65`, `radial.py:117`, with a test keeping the three values in step. |
| **S-02** | A non-string ficha field loads clean then kills every consumer | FALSE (defect) | **REPAIRED — `SATISFIED-EXTERNALLY`** | `store.py:39` `_coerce_field(graph, node_id, key, value) -> str`, applied at the store boundary for both attributes (`:235`) and fields (`:239`); `graph.load_warnings` carries the record. |

### 12.4 — What the repair batch did NOT do, and therefore stays in this batch

Recorded because *"the repair batch fixed the sala's error handling"* is the plausible-but-false
reading, and it is exactly the premise an implementer would carry:

**`HomeScreen.on_mount` contains `load_or_notice` (`app.py:439-461`), which TOASTS and returns
`None`.** A map that fails to load therefore produces a notification and **no card at all**. The
brief's requirement is a **card state** — *«mapa danado — enter ver por que»* — and the security
lens's **M-H1** mutant names this failure precisely: *"the threshold must be painted card count,
not 'the screen did not raise'."* A toast plus a missing card satisfies *"never crash"* and fails
*"never skip silently"*. **`LLR-N13.1.5` is live work, and `HLR-N13.3` (the mount budget) is
entirely unwritten.**

### 12.5 — Un-park decisions (autonomous, recorded not asked)

| # | Decision | Why, with the executed basis |
|---|---|---|
| **D16** | **Section 3.1 (S-7) is struck from scope as `SATISFIED-EXTERNALLY`.** `HLR-S07.1`, its ATs and its TCs are struck, not re-derived. | RC-1's already-shipped check, run at P0 as the flow requires and not deferred to P3. The repair batch's `HLR-R04` covers it with a stronger guard than this batch had specified. **Consequence: `QA-B-02` is DISSOLVED — the requirement it attacked no longer exists here.** Its *lesson* is not dissolved and is re-homed in section 13. |
| **D17** | **The S-8 clipping half of `HLR-N16.1` is struck as `SATISFIED-EXTERNALLY`; the per-view legend half is not.** | The scroll container shipped. What remains is the batch's actual story: the five un-scoped routes (P-13), the two screens with no `KEY_SCOPE`, the glyph vocabulary, the view name in the title, and the `??` stub. |
| **D18** | **S-01 and S-02 are struck as `SATISFIED-EXTERNALLY`; security conditions C-1 and C-2 are discharged by execution.** | See 12.3. **C-3 (S-03, the mount budget) is NOT discharged and remains a blocking condition.** |
| **D19** | **`MAX_RENDER_NODES = 12000` is adopted as a given, not re-litigated**, and `HLR-N13.3`'s budget is expressed **relative to it**. | It is shipped, tested and enforced in all three renderers. Re-deriving a second bound would create two live definitions of *"too big"* — the exact defect `D6` removed for *"hit"* and `D14` for *"coverage"*. |
| **D20** | **The parked `01-requirements.md` is amended in place, not rewritten.** Struck sections are marked `SUPERSEDED — SATISFIED-EXTERNALLY at d877784` with their evidence, and remain readable. | Section 6.5 is the flow's record for exactly this, and a silent deletion would make the batch's own history assert something false. It also keeps the id space stable so the `02a`/`02b` findings still address something. |

---

## 13 · Blocker fold ledger — the 13 PDR blockers, dispositioned

**Two dissolved by the repair batch, one discharged by an artifact it left behind, ten live.**
Every "dissolved" and "discharged" row below was verified by re-execution, not by reading the
repair batch's record.

| # | Blocker | Disposition | Basis |
|---|---|---|---|
| **QA-B-01** | The story's headline identity is unrealisable and green by fixture luck — the canvas paints **titles**, the oracle counts **ids** | **LIVE — decisive.** Replacement oracle: the renderer **returns its painted id set as data**; acceptance consumes that declared set, then asserts *separately* that every declared id has a **truncation-tolerant** trace. Two predicates, not one substring scan. | Measurement lane `M-U1` |
| **QA-B-02** | The root-title oracle is FALSE on a correctly laid-out canvas | **DISSOLVED — the requirement no longer exists.** §3.1 (S-7) is `SATISFIED-EXTERNALLY` (D16). **Its lesson is NOT dissolved** and is re-homed into `HLR-N06.3`: never assert a raw title against a canvas that truncates. | PLAN §12.3, §12.5 D16 |
| **QA-B-03** | `AT-027`, `AT-028`, `AT-045` do not exist; the count is 44, not 47 | **LIVE.** The three ids are struck; every AT count becomes derived. **Independently corroborated:** the mechanical validator reports **47** `AT` ids with no node on disk, against 44 measured predicates. | PLAN §12.2 (V2), measurement lane |
| **QA-B-04** | *"Assert the painted panel"* has no executable definition, and the corrected number is still wrong | **DISCHARGED BY AN ON-DISK ARTIFACT.** `tests/test_repair_layout.py::_rows_in` clips to the widget's own region — which is precisely what the contaminated oracle failed to do — and `::_painted_bindings` unions the dialog's painted rows across **every** scroll position. `test_at_r14_the_oracle_is_clipped_to_the_help_dialog` is already the negative control the review demanded. **Requirement obligation retained:** every legend AT must declare its Pilot size, because the naive oracle was measured size-dependent. | Read at `tests/test_repair_layout.py:60-130` |
| **QA-B-05** | The nested-fold negative control has no fixture, and *"owed at Phase 3"* is not a discharge | **LIVE — a PDR condition.** A synthetic fixture of depth >= 3 with an inner folded branch of >= 2 descendants, plus the executed transcript showing the naive and correct sums **disagree**. Inc-3 does not open until that transcript exists. | Measurement lane `M-U2` |
| **QA-B-06** | The export chain never touches the written artifact (C-12) | **LIVE.** Assert the braille count read back **from the file on disk**. Read-back must scan code points or parse `<text>` nodes — a substring oracle returns False even on correct content because Rich encodes spans (C-42). | Measurement lane `M-U3` |
| **QA-B-07** | The plausible wrong coverage fix passes | **LIVE.** Pin the value: `pct(schema-less) == 100`, plus the agreement clause. Without a pinned value the weaker commit makes all three sites agree on **0 %** and ships *"0 % documented"* on every schema-less map. | Requirements lane |
| **QA-B-08** | `WARN` carries two contradictory jobs; `ALERT` silently acquires a second | **LIVE.** One job statement each, both reconciled with the malformed-lens chip, before the census gate is written. With two live definitions the classifier has no oracle. | Requirements lane |
| **QA-B-09** | The declared subject is not the subject of the change, and `> 0` cannot see a wrong implementation | **LIVE, two limbs.** (a) Subject: relabel as a regression PIN on the radial renderer, or move the subject — decided by measurement. (b) Add the **containment arm**: the distinct painted non-space set shall remain a **subset** after the change. That arm reddens the wrong-precedence mutation; `> 0` does not. | Measurement lane `M-U4` + requirements lane |
| **QA-B-10** | Five blocking questions gate seven ATs | **FOUR RULED BELOW; Q-9 routed to the PDR architect lens with three named options.** A chord-agnostic requirement is legitimate; a chord-agnostic acceptance test is not. | §13.1 |
| **S-01** | A cycle in a `.mmd` kills the app | **DISSOLVED — `SATISFIED-EXTERNALLY`.** Security condition **C-1 discharged.** | PLAN §12.3 |
| **S-02** | A non-string ficha field kills every consumer | **DISSOLVED — `SATISFIED-EXTERNALLY`.** Security condition **C-2 discharged.** | PLAN §12.3 |
| **S-03** | The sala's failure containment is a checkbox, and nothing bounds the mount | **LIVE — the one security blocker still open.** `HLR-N13.3` (mount budget, expressed relative to the shipped `MAX_RENDER_NODES = 12000`) and `LLR-N13.1.5` (per-map containment, threshold = **painted card count**). **Not closed by the repair batch:** `load_or_notice` (`app.py:439-461`) toasts and returns `None`, so a refusable map yields a notice and **no card** — *"never crash"* satisfied, *"never skip silently"* failed. | PLAN §12.4 |

### 13.1 — The five gating questions, ruled

Executed against `d877784` in this session. Map scope holds **25** `KEYMAP` entries while
`bindings_for('map')` returns **27** (it merges two app-scope rows) — `QA-M-04`'s ambiguity
reproduces exactly, and the requirement must pin `bindings_for` explicitly.

| # | Ruling | Executed basis |
|---|---|---|
| **Q-3** — the `n` chord collision | **RATIFIED as D10 option (a).** New seat rows: `map/n -> next_hit "siguiente coincidencia" (nav)` · `map/N -> prev_hit "coincidencia anterior" (nav)` · `map/M -> next_gap "siguiente faltante" (view)`. Exactly **one changed row plus two added rows**, reviewed row-by-row at DDR. | `map` scope enumerated: `n -> next_gap` is taken; **`N` and `M` are both free**; `duplicate_chords()` returns `[]`; free lowercase is `b c i p s t v w y` and free uppercase is everything except `A I R X`. The collision is a **semantics** problem, not scarcity. `M` chosen because `m` is already `cobertura` and walks the same tree order. |
| **Q-7** — the lens walk chord | **RULED: take no new chord; unify the concept.** `n` / `N` walk **whichever result set is live** — search hits and lens matches are both *coincidencias*, and only one set can be active at a time. `⇥` keeps its shipped job, focus traversal. **This is a declared deviation from the brief's `⇥`** — see §13.2. | Two green shipped guards forbid it: `tests/test_keymap.py` bans any `tab` seat entry and any screen binding `tab` outside `TAB_BINDING_EXCEPTIONS = ("SettingsScreen", "EditorScreen")`, and **`MapScreen` is not in it**. `tab` is also the inspector's only keyboard route. **This is not the state-dependent label rejected at D10:** the label *"siguiente coincidencia"* is true for both result sets, so the whole-seat pin stays a static set equality. |
| **Q-8** — bare word semantics in a lens query | **RULED: a token with no colon is MALFORMED, not a free-text term.** It takes Q-6's **malformed** outcome class — `ALERT` chip plus a declared line naming the expected `clave:valor` form — which is already distinguishable from both *"field undefined"* and *"zero matches"*. Free-text lens terms go to the backlog. | Admitting bare words as free text silently merges the lens with search, producing **two live definitions of what matches** — the exact defect `D6` removed for "hit" and `D14` for "coverage". The three outcome classes already carry the vocabulary, so the ruling costs no new mechanism. |
| **Q-9** — migrate or declare, for `FactoryScreen` / `SettingsScreen` | **ROUTED TO THE PDR ARCHITECT LENS, to be ruled in the same sitting** — with three options named and a decision criterion, so it is ruled rather than left open. **It is not the implementer's choice.** | The naive ruling *"declare a scope, don't migrate"* **does not work, and that is why it goes to PDR**: those screens' bindings are not in the seat, so a newly-declared scope would make `bindings_for(scope)` return an **empty** legend — worse than today's wrong one. The three real options: **(a)** migrate both into the seat (retires their `UNMIGRATED_SCREENS` entries; `SettingsScreen` is *also* in `TAB_BINDING_EXCEPTIONS`, so this moves **three fences at once** inside the increment that is rebuilding the legend — R-8 named this intersection); **(b)** build an unmigrated screen's legend from its own real `BINDINGS` rather than the seat, at the cost that the whole-seat pin no longer covers it; **(c)** scope the story to the three `app.py` routes and carry the two unmigrated screens. **Criterion: which option leaves the fewest live definitions of "the bindings that work here".** |
| **Q-10** — the three census exceptions | **RULED: fix all three, exempt none.** (1) `#a3a3a3` at `mapper/views/radial.py:18` becomes a **declared token**. (2) The `WARN` progress use — **`mapper/app.py:879`**, not the parked `:848` — is **re-toned**: severity is `WARN`'s one job and *loading* is not a severity. (3) `.factory-tag { color: #1783ff; }` at `mapper/screens/factory.py:104` is `ACCENT` on a non-interactive tag; **re-toned**. | Declared token set is exactly nine: `GROUND PANEL STEP INK MUT ACCENT WARN ALERT WORDMARK` (`darkside.py:12-20`); v2 adds `SAGE TEAL VIOLET`. **Fixing rather than exempting is what makes the census input set derivable with zero hand-listed carve-outs (C-31)** — and `S-10`'s fallback-tone recommendation *requires* the declared set to contain every live hue. The repair batch's post-mortem records that naming a defect class without landing its census cost six rediscoveries; an exemption list is that pattern. |

### 13.2 — Declared deviation from the brief: `⇥` (Q-7)

**The brief specifies** *"`⇥` walks results with the inspector focused"* for US-N14. **Two green,
shipped tests forbid a `MapScreen` `tab` binding**, and `tab` is the inspector's only keyboard
route — so the briefed mechanism cannot be built without changing guards that exist for a measured
reason.

**The story's promise is preserved; only the chord changes.** The operator still walks the lens's
answer from the keyboard, with the inspector following the selection — via `n` / `N`, the same
chords that walk search hits. **What is given up** is `⇥`'s specific ergonomics. **What is bought**
is one walk concept instead of two, and no change to the `tab` fences.

Recorded here as a visible deviation rather than folded silently, because it contradicts a written
line of the operator's brief. **PDR ratifies it; if the operator prefers the guards move instead,
that is a one-line reversal of this ruling and a larger increment.**

### 13.3 — CORRECTION to §13.1: four of the five were ALREADY ruled, and two of those rulings beat mine

**I ruled Q-3, Q-7, Q-8 and Q-10 in §13.1 and routed Q-9 to PDR — then read the parked
`PDR-2026-08-26-ui-next-batch-02.md` §5 and found the architect lens had already ruled all four of
Q-7 through Q-10, sealed, with executed evidence.** Recorded as a correction rather than quietly
merged, because it changes what `QA-B-10` actually is.

**What `QA-B-10` really says, restated.** It is *not* "these five are unruled". It is that the
rulings live **in the PDR and were never folded into `01-requirements.md`**, so the acceptance tests
are still chord-agnostic. **The fold is the fix; no new ruling was needed.** My §13.1 re-derivation
was therefore redundant work — though not worthless, since two of the four converged independently,
which is worth more than one lens asserting them alone.

| # | My §13.1 ruling | The sealed PDR ruling | Which governs |
|---|---|---|---|
| **Q-7** | No new chord; `n`/`N` walk whichever result set is live | **`#D6` — identical**, and explicitly *"the orchestrator's unification is RATIFIED"* | **Converged.** PDR governs; it adds two conditions mine lacked — **C-D6a**: *"only one result set is live"* becomes an explicit tested invariant at Layer 0, not an assumption, since it is the load-bearing premise of the whole ruling; **C-D6b**: the nine-press `tab` regression guard is retained verbatim and re-run after Inc-4, Inc-6 and Inc-9. |
| **Q-8** | A bare word is malformed, not free text | **`#D8` — identical**, plus a **redirect** in the error line (*the lens expects `campo:valor`; use `/` for free text*) | **Converged.** PDR governs; the redirect is strictly better — the error teaches the model instead of just refusing. |
| **Q-9** | Routed to PDR with three options | **`#D9` — MIGRATE BOTH**, three gated conditions | **PDR governs. My instinct toward declare-only was wrong, and the PDR names why:** `LLR-N16.1.2`'s own threshold requires `len(bindings_for(scope)) >= 3`, so declaring a scope without migrating forces seat rows that **duplicate** hand-written bindings — two declarations of one key, the exact defect the seat abolishes. *"Declare-only is not an option; it only looked like one."* Executed costs: `FactoryScreen` 12 bindings, binds no `tab`; `SettingsScreen` 6, two of which re-declare `tab`/`shift+tab` to Textual's own focus actions. |
| **Q-10** | Fix all three, exempt none | **`#D10` — same direction, better dispositions** | **PDR governs.** It is more precise on all three: `#a3a3a3` is a *legitimate missing ramp step* inside `_GREYS = (INK, "#a3a3a3", MUT)`, not a stray hue → promote with its job documented. The progress `WARN` gets the **busy job assigned to one of the three v2 tokens** — squarely S-6's own work — rather than my vague *"re-tone"*. `.factory-tag` retones to `MUT`, but since `screens/factory.py` is not in Inc-1's file set, **Inc-1 registers it as a known-open exception and Inc-9 closes it**, with the stale-exception guard reddening if Inc-9 forgets — a mechanical handoff instead of a promise. |

**The one place my re-execution still governs:** the PDR cites the progress-`WARN` site as
`app.py:848`. At `d877784` that address is **`app.py:879`** —
`text.append(f"{marker} {stage}", darkside.WARN if self.loading else darkside.INK)`. The PDR's
*disposition* stands; its *citation* is stale, like every other line number in the parked set.

**Also adopted from the PDR, and it is the honest half of `#D9`:** condition **C-D9a** gates the
`tab` drop on `SettingsScreen` behind a probe with a **working positive control**. The architect
drove nine `tab` presses with and without the bindings, got identical results, and **recorded its
own probe as vacuous** rather than banking the green — `app.focused` was `None` throughout, so the
probe could not observe a transition and therefore could not fail. If that control cannot be built,
the drop does not ship. That is the discipline this project has paid for repeatedly, applied by the
reviewer to itself.

### 13.4 — The increment cut, re-derived against the reduced scope

The PDR's `#D5` cut is **9 increments, serial** (ARQ measured 0 of 21 pairs parallelisable —
`modules(A) ∩ modules(B)` contains `app` without exception). The strikes shrink two increments and
**dissolve one hard ordering constraint**:

| Inc | Change from the parked cut | Consequence |
|---|---|---|
| **1** | **S-7's layout work is struck.** Retains S-6 tokens + the `Canvas` A3 + Q-10's two Inc-1 dispositions. | Still 4 source files (`darkside.py`, `canvas.py`, `views/radial.py`, `app.py`) — the freed budget is consumed by the `#a3a3a3` promotion and the busy-token retone. |
| **2** | Unchanged — the `ViewState` / `IRenderer` A3, whole, **6 source files, declared breach**. | **Its byte-identity gate now runs against the 429-test baseline, not 245.** The parked packet's number is superseded. |
| **7** | **Gains S-03** — `HLR-N13.3` (mount budget) and `LLR-N13.1.5` (per-map containment, threshold = painted card count). | 3 source files (`app.py`, `darkside.py`, `store.py`) with one slot free; `store.py` is already there for `MapStore.list_maps`. |
| **8** | **S-8's truncation work is struck** — the scroll container shipped. Reduced to the **glyph vocabulary only**. | Smallest increment in the batch. |
| **9** | Unchanged in content. | — |

**The `8 before 9` HARD ordering is DISSOLVED.** The PDR made it hard because *"Inc-9's acceptance
reads the painted panel; Inc-8 is what makes the panel able to paint 27 rows"*, and reversing it
risked repairing Inc-9 by weakening its oracle back to the return value — which passes on a clipped
panel. **The repair batch made the panel able to paint all of them**, so the hazard is gone and the
dependency is now ordinary, not hard. The serial chain is kept anyway (nothing is gained by
reordering, and `keymap.py` remains a four-way collision resolved by serial ordering), but the
*reason* is now convenience rather than correctness — and that distinction is recorded so a later
reader does not treat a preference as a constraint.

---

## 14 · Corrections and one new defect, from the fold lanes

### 14.1 — CORRECTION to §12.4: my own claim executed FALSE

**I wrote in §12.4 that a map failing to load yields *"a notification and no card at all"*. That is
wrong, and the requirements lane caught it by execution.**

`mapper/app.py:559-573`, read in full rather than inferred from `load_or_notice`'s `return None`:

```
        for mmd in mmd_files:
            map_name = mmd.stem
            graph = load_or_notice(map_name)
            if graph is not None:
                kind = "legacy" if graph.schema else "concept"
                nodos = str(len(graph.nodes))
                docs  = str(len(graph.documents))
            else:
                kind, nodos, docs = "concept", "0", "0"
            table.add_row(...)          # <- UNCONDITIONAL
```

Executed under `App.run_test`: `row_count = 2`, the broken map's row reading
`['roto', ' concept ', '0', '0']`. **The row is always added.**

**Why this is worse than the gap I described, and why it moves the threshold.** A missing card is a
visible absence. What actually ships is a card that **looks exactly like a healthy empty map** —
`concept`, `0` nodes, `0` documents — so the operator reads a confident, wrong fact. The failure is
**misdeclaration, not omission.**

The consequence is the one that matters: **`M-H1`'s remedy as `02b` states it — *"the threshold must
be painted card count"* — is ALREADY GREEN at `d877784`.** A requirement written to painted card
count alone would pass on the shipped defect. `LLR-N13.1.5` therefore asserts **painted card count
AND per-card state distinguishability**, and the brief's «mapa dañado — ↵ ver por qué» is what makes
the second half observable.

**This is the third time in this batch that a plausible-looking value read as data.** It is the
project's own recurring lesson, and this time it was mine.

### 14.2 — NEW DEFECT `S-15`: `MAX_RENDER_NODES` bounds the COUNT and not the WORK

**BLUF: a 73-node map hangs the application for 70 seconds. A 12 000-node map renders in 180 ms.
The shipped cap waves the first one straight through, and US-N13 makes it reachable without the
operator opening anything.**

Found by the requirements lane, **independently reproduced by the orchestrator** on a separately
written probe (different graph builder, different call path) because a finding this size may not
rest on one measurement:

```
layered DAG layers=3 per=  5   nodes=   16   render=        2.2 ms
layered DAG layers=5 per= 10   nodes=   51   render=     1963.9 ms
layered DAG layers=6 per= 12   nodes=   73   render=    70248.5 ms
CONTROL chain                  nodes=12000   render=      179.8 ms    cap=12000
```

The shape is a layered DAG — every node in layer `L` is a parent of every node in layer `L+1`.
Node count grows linearly; **path count grows multiplicatively**, and the renderer's traversal is
keyed on paths. The two lanes' figures agree to within 3 % on independent code, so the effect is
the renderer's and not the harness's.

**Why the shipped guard does not see it.** `MAX_RENDER_NODES = 12000` is a **node-count** bound.
73 < 12 000, so the refusal never fires. This is **`M-H3` verbatim** — *"node count is not a proxy
for traversal cost on an unvalidated edge list"* — promoted from a named hypothetical mutant to a
measured defect on `master`.

**Two corrections this forces on the parked security review.** `02b`'s renderer timings (3.4 s at
n=3280, 9.1 s at n=10 000) were measured **pre-repair** and are now roughly 60 ms — the repair
batch made chain and breadth traversal fast. **The conclusion survives and the numbers must not be
quoted**: the cost did not go away, it moved into a shape nobody had measured. Quoting the old
figures would understate the live defect while appearing to cite evidence.

**Disposition — in scope, under `HLR-N13.3`, no new story.** The batch's standing scope rule is
*"this batch repairs exactly what its own stories make newly reachable"*. The sala loads **every**
map in the workspace on mount, so one pathological map stalls the application at startup, before
any card paints — which is precisely what `S-03` already blocks on. `HLR-N13.3` was going to need a
budget anyway; **this finding fixes what the budget must be a bound on.**

- The bound is on **work**, not on node count and not on map count (`M-H2`, `M-H3` both survive a
  count bound).
- **`MAX_RENDER_NODES` is not replaced or re-litigated** (`D19`) — it stays as the coarse cap it
  is. The work bound is **additional**, and the requirement must say so, or the batch ships two
  competing definitions of *"too big"*.
- The **51-node shape is the acceptance fixture**: at ~1.9 s it is unambiguously over any sane
  budget while staying fast enough to run in a suite. The 73-node shape is the demonstration, not
  the test — a 70-second node has no place in a gate.

**Recorded as `S-15` rather than folded silently into `HLR-N13.3`**, because it is a shipped
app-killing defect found after the PDR that produced the batch's blocker list, and the next reader
needs to know the mount budget exists for a measured reason rather than a precautionary one.

---

## 15 · PDR SECOND PASS — consolidated verdict, 2026-08-27 (resumed session)

> **Base unchanged at `d877784`.** Four lenses ran in parallel over the amended
> `01-requirements.md` (5,199 lines, 41 amendments across two sets). Their artifacts are
> `02c-pdr-architect-pass2.md`, `02d-pdr-qa-pass2.md`, `02e-pdr-security-pass2.md`,
> `02f-pdr-ux-pass2.md`. Nothing under `mapper/` or `tests/` was edited by any lens or by the
> orchestrator during this pass.

### 15.1 — Verdict: **REJECTED · iterate-to-refine to Phase 1** (amendment set 3)

| Lens | Verdict | Findings |
|---|---|---|
| architect | **REJECTED** | 6 blockers; flags (a) and (b) ruled and sealed as `#D21` / `#D22` |
| security | **BLOCKED** | 3 blockers (`S-16`, `S-17`, `S-18`) · 3 majors · 1 minor |
| qa | approved with conditions | 8 conditions; 2 source findings **dropped** by the fold |
| ux | approved with conditions | 10 conditions, **2 blocker-class** |

**A rejection returns to design, not to implementation. No increment opens.** The PDR station is
now at **iteration 2**; the soft cap is 3.

### 15.2 — Re-verification of the resumed session (executed, not carried)

| Check | Result |
|---|---|
| HEAD / base / `origin/master` | `d877784`, all three equal |
| Fast lane | **413 passed · 16 deselected**, 74.32 s, exit 0 |
| Slow lane (manual — repo has no CI workflows) | **16 passed · 413 deselected**, 36.36 s, exit 0 |
| Collected, both lanes | **413 + 16 = 429** |
| `ruff check mapper/ tests/` | **29** errors, exit 1 (pre-existing, unchanged) |
| `git status` before **and after** the battery | byte-identical; only `state.json` + the untracked batch dir |
| Validator (pinned build) | **55 block · 126 notice** |

**Validator reconciliation — the briefed figure was 54.** Blocks are 51×`V2` + `V7` + `V15` +
2×`V16`. **All four non-`V2` blocks target the auxiliary `~/.claude` repo; zero target this batch.**
The 51 `V2` are the C-18 realisation gate, correctly red before implementation.

**Concurrent-session hazard, declared.** `~/.claude/docs/tools/devflow-validate.py` was rewritten
**mid-session at 11:24:07** by another project's batch (119 uncommitted insertions touching `V2`/`V6`).
Measurements were re-taken against a **pinned copy of the committed validator** (`4fdefdd`, md5
`0cda4ab82f96d1a556af0a105b3aa5a3`) held in the orchestrator's scratchpad; the pinned md5 **equals the
shipped bundle copy's**, which is what proves `V15` is an artifact of the other session's uncommitted
work and not a defect here. C-45 **PULL re-executed**: both `~/.claude` and `~/.claude/skills` are
`4 0` — **0 behind** — so this batch does not run a stale flow. The PUSH half is broken by work that
is not this batch's and is reported **FOUND, not swept up** (C-44).

### 15.3 — The two operator-ordered flags, RULED

| Flag | Ruling | Basis |
|---|---|---|
| **(a)** `LLR-N06.2.5` cross-cutting under a story HLR | **option (a2)** — cross-cutting home. Sealed **`#D21`** | The architect adopted the orchestrator's descoping criterion and added a **second, executable** limb: *does satisfying the child require editing files outside the parent increment's declared file set?* Executed — the 15 uncoerced `notify` sites are `app.py` (11) + `screens/factory.py` (4), and Inc-3's set is **4-of-4 without `factory.py`**. The mis-parenting is therefore an **undeclared source-budget breach**, not a stylistic smell. `#D21` **removes** a breach rather than creating one. Option (a3) is unavailable: C-8 has no other HLR owner. Discrimination control: `LLR-N06.2.3`, same parent, passes both limbs. |
| **(b)** the map-canvas braille promise owned by nothing | **option (b2)** — explicit deferral, **and the prose is amended**. Sealed **`#D22`** | Deferral confirmed on scope grounds; the prose obligation is confirmed but **mis-located by the flag**: §3.4 does not mention braille at all. The surviving promise sits at `:107`, `:113` and `:3343`. |

**Flag (b) uncovered a deeper defect one layer down.** `LLR-N16.2.1` asserts set equality against
*"21 rows V1-V21"*; executed, `01b` DECISION 3 carries **23 labels**, with `V4` and `V4a`
byte-identical in glyph, label and style, and it mandates a legend row for the repo marker — which
**`#D7` ruled out of this batch**. `HLR-N16.2`'s *"legend style equals the renderer's style for that
glyph"* has no defined value for six rows no renderer paints.

### 15.4 — Blockers carried into amendment set 3

| id | Blocker | Verified by the orchestrator? |
|---|---|---|
| **S-16** | `_coerce_field` covers **2 of 5** file-derived families; `S-02` is **live**, so `D18`'s `SATISFIED-EXTERNALLY` strike is **wrong** | **independently reproduced on a third harness with a positive control** — see 15.5 |
| **S-17** | `LLR-STO.1.1` **does not exist**: referenced normatively with a `shall`, folded into by `A-40`, **no heading anywhere** | **grep: 24 occurrences, all prose, 0 headings** |
| **S-18** | `HLR-N13.3` **declares** the stall rather than bounding it — threshold 2 measures elapsed time, which requires letting the work finish. Mutant `M-H7` satisfies all four thresholds and still leaves ~54 s of frozen UI. No deadline mechanism exists in `mapper/views/` | not re-executed this pass |
| **ARQ-1** | **`docs/ARCHITECTURE.md` was never amended.** The ARQ map amendment exists only as `ARCHITECTURE-proposed-at-ARQ.md` inside the batch dir. §7 records ARQ as *approved, map amended (+456/-248)* — **false against disk** | live doc `:58`, `:136` still declare `render(graph, selected_id, w, h, **kwargs)` marked **frozen: yes**; `R-010` still reads *"stays frozen through this batch"*; no `ViewState`, no Protocol, no `runtime_checkable` |
| **GOLD-1** | Byte-identity digests over this batch's own surfaces are unaccounted for in all three planning artifacts | **derived: 12 pins** (3 renderers x 4 sizes), *not* the 18 reported. **`RadialRenderer` is pinned at all four sizes**, and Inc-1's job is to make `Canvas.rows()` honour `dots`/`bgs` — so **Inc-1 reddens 4 pins by construction** |
| **B3-FALSE** | **Trigger B3's non-activation record is false.** Probe was `ls tests/goldens` -> no such directory; correct as executed, but its **input set was wrong** — the goldens live in `tests/test_repair_depth.py::MASTER_LEGACY_DIGESTS`. **C-31 verbatim.** B3 firing turns on **C-24** | derived above |
| **CUT-1** | **Two live increment cuts** in `01-requirements.md` — §3.6/§3.7/§3.8 headers plus five body references carry the ARQ 7-cut that `#D5` rejected, alongside the ratified 9-cut | not re-executed this pass |
| **AT-ORPHAN** | `AT-009`, `AT-031`, `AT-040` belong to **no increment** (C-21) | not re-executed this pass |
| **UX-1** | `HLR-N14.3`'s two clauses **cannot both be satisfied, and the near-miss destroys data**: 6 of 8 focusables are `FieldInput`; Textual selects-on-focus, so real `n` **replaces the field value** and `_commit` writes it on blur | not re-executed this pass |
| **UX-2** | **US-N14 has no declared entry chord** — no seat row opens the lens | not re-executed this pass |
| **UX-3** | `WORDMARK` paints US-N06's declared-overflow line at **1.85 : 1** contrast — the story's whole promise, illegible. One rung down, `ACCENT` and `VIOLET`, and `SAGE` and `TEAL`, collide | not re-executed this pass |
| **C4-ORPHAN** | §3.0's `COERCION_RANGES` and the `_CONTROL_MAP` widening — the load-bearing half of security condition **C-4** — have **no HLR, LLR, AT, TC or increment**. Four LLRs in four increments assert against a list nothing creates | not re-executed this pass |

### 15.5 — `S-16` reproduced independently (orchestrator's harness, third measurement)

Positive control first, because a probe that cannot produce a non-absence proves nothing:

```
POSITIVE CONTROL  well-formed          loaded  nodes=2  warnings=0
family 1: int ficha title   (coerced)  loaded  nodes=2  warnings=0   search_hits ok
family 2: int ficha field   (coerced)  loaded  nodes=2  warnings=0   search_hits ok: ['A']
family 3: int attachment path  (RAW)   loaded  nodes=2  warnings=0
                                         -> TypeError: sequence item 0: expected str instance, int found
family 4: int schema key/label (RAW)   loaded  nodes=2  warnings=0   req 0 -> 2
family 5: int NODE ID          (RAW)   loaded  nodes=3  warnings=0   ids=['2','A','B']
```

Three of five families are uncoerced, each failing **silently and differently**, all with
`warnings=0` — the map reports itself healthy. **Honest divergence from the security lens:** it
reported the coverage denominator doubling `2 -> 4`; mine stayed `0` in family 5 because the fixture
carries no schema. That is a fixture difference, not a contradiction — node duplication reproduces
identically, and the structural claim is what governs.

### 15.6 — The instrument finding, recorded because it recurs

**Four of the architect's own first-pass conditions — `C-D4a`, `C-D4c`, `#D15`, and risk `A-11`'s
`isinstance` gate — were dropped by the fold while the 41-row amendment table reported green
throughout.** QA independently measured the same shape: **2 of its source findings dropped**
(`QA-M-02`, `QA-N-08`), both targeting `PLAN.md`, which is the fold's blind spot. This is the
catalog's *"an amendment table is a container; a green amendment count cannot see what the fold
dropped"* — measured here for the second time in one batch. **Amendment set 3 must be audited
against the SOURCE reviews, never against its own table.**

**And the `.render` census is now in its third wrong generation.** The architect's correction:
`.render` is **two protocols**, and the A3 migration surface is 6 definitions plus **22 arg-ful call
sites across 9 files** (3 production, 19 test); 25 further zero-arg Textual sites are not in the A3
at all. The parked *"6 defs / 3 call sites"*, the §9 correction *"29 sites / 14 files"*, and QA's
*"48 sites / 17 files"* each answered a **different question**. Amendment set 3 must state the
question before stating the number.

### 15.7 — Decisions taken autonomously in this pass (recorded, not asked)

| # | Decision | Why |
|---|---|---|
| **D21** | Flag (a) -> cross-cutting home for `LLR-N06.2.5` | Sealed by the architect lens on an executable two-limb criterion; removes a source-budget breach |
| **D22** | Flag (b) -> explicit deferral **plus** prose amendment at `:107`, `:113`, `:3343` | A declared gap contradicting live prose leaves two definitions of what the batch delivers |
| **D23** | **Validator pinned to committed `4fdefdd`** for every measurement in this batch | The canon file is being rewritten by a concurrent session; an unpinned tool makes every figure unreproducible |
| **D24** | `~/.claude` left **untouched** — not committed, not reverted, not stashed | C-44: committing another session's work in progress is its own defect |
| **D25** | **No tree edits while any lens ran** | The corpus records a phantom gate-blocking finding produced by exactly one concurrent read of an artifact mid-write |

---

## 16 · RE-SCOPE — 2026-08-27, operator decision (option A)

### 16.1 — Why the batch was re-scoped rather than folded as briefed

The resumed session's briefing named **six** remaining items for amendment set 3. The RIDER-1
reconciliation (`02g-lens-reconciliation.md`) executed all four lenses' own condition ledgers
against the tree and measured the live set at **≈39 of 51 union items**, of which **≈11 require
design rulings**, plus **4 newly raised findings** and **2 live security defects on `master`**.

**This is C-43 at batch level: the authorization to spend the final PDR iteration rested on a
premise about remaining scope that executes FALSE.** Three of the briefed six were also wrong in
detail — the orphan ATs are **six** not three; the legend census is **23**, and striking the
byte-identical `V4` duplicate takes it to **22**, so "correct 21 to 23" would be wrong twice; and
`S-17`, `UX-3` and `S-18` sit in this PLAN's own §15.4 twelve-blocker table while appearing in the
briefed list not at all.

The structural cause is mechanical: `git log --oneline -- .../01-requirements.md` returns **one
commit** (`8675151`). The requirements document has not been edited since the lenses wrote their
verdicts, so every requirement-side finding is frozen exactly where its lens left it. Only code
moved, and the repair batch touched only `mapper/store.py`, `docs/ARCHITECTURE.md` and five test
files. **All 11 discharges are that shipped code**; no lens condition was closed by a document fold.

Rather than spend the final iteration (soft cap 3) on a set five times the briefed size, the batch
was stopped and referred. **The operator chose option A — re-scope.**

### 16.2 — The cut

| Cut to the follow-on design batch | Why |
|---|---|
| **US-N14 «lente»** (§3.7) | Its two blocker-class UX conditions are design rulings, not document edits: `HLR-N14.3`'s two threshold clauses cannot both be satisfied, and the near-miss **destroys operator data**; and the story has **no declared entry chord**, so no acceptance can drive its real gesture |
| **`S-18` render work-budget, PAIRED with `S-19`** | `S-19` is `S-18`'s **PRECONDITION**, not its sibling. Measured on the 51-node/410-edge shape: Layered **1283 ms**, Outline **337 ms**, **Radial 142 ms — UNDER the 250 ms budget**. So `k = 0` on Radial and threshold 4 cannot distinguish a correct implementation from a missing one. **The follow-on batch's fixture must NAME ITS RENDERER**, or S-18 is untestable by construction |

The cut removes ≈7 of the ≈11 design rulings (`UX2-C-01`, `UX2-C-02`, `S-18`, `S-19`, `P2-C8`,
security `C-3`, and part of `UX2-C-06`), leaving iteration 3 to target **US-N06 · US-N07 · US-N13 ·
US-N16 · palette v2**.

**Nothing is deleted.** The deferred text stays in place, marked, so the follow-on batch inherits
the work rather than re-deriving it.

### 16.3 — Decisions taken in this pass (recorded, not asked)

| # | Decision | Why |
|---|---|---|
| **D26** | **The strict rule is adopted: a code fix never discharges a missing requirement** | It is what keeps `S-17` visible. `mapper/store.py` cites `LLR-STO.1.1` normatively in **five docstrings**, and that identifier has no statement, threshold, `TC`, `AT` or traceability row anywhere. The shipped fix made the hole *harder* to notice, because the tree now looks like the requirement is being obeyed. Under this rule the architect lens is **14 of 14 LIVE**, not 12 |
| **D27** | **`B-29` and `B-30` ride INSIDE this batch** as one small repair increment, with requirement stubs in amendment set 3 | Operator rider 1, orchestrator's call. Measured: `B-30` is one line with **zero** tests asserting the message text; `B-29` is ~3 lines and **only one** test asserts `load_warnings == []`, while the real fixture yields 0 warnings and no phantom. Both are shipped defects with mechanical fixes, not design rulings, so they do not burden the PDR. **Both are newly reachable with zero operator action** — US-N13's sala loads every map on mount |
| **D28** | **`B-29`'s guard ships with a SYNTHETIC fixture** | The guard is a **no-op on the current tree**: no fixture carries a sidecar id absent from its `.mmd`, so a mutation of the guard changes nothing today and the suite stays green either way. C-55 limb 2 — the case the tree lacks must be constructed, or the guard is untested however green the suite |
| **D29** | **The A3 census is settled by AST and stated as question + instrument + SHA** | Four generations of this number were wrong because *"blast radius"* names three different sets. **Generation five was produced during the reconciliation itself, by the orchestrator**: a grep returned 24 sites, the 24th being `renderer.render(...)` inside a **docstring** at `mapper/widgets/rail.py:180`. Settled: **23 arg-ful sites / 10 files / 6 definitions** at `3fe0e4b`. A grep cannot tell a call from a mention of a call |
| **D30** | **Amendment set 3 is authored in TWO SEQUENTIAL passes on `01-requirements.md`, never in parallel lanes** | C-52 condition 2: two lanes may not edit the same file, not even different regions. `PLAN.md` and `state.json` are disjoint and were taken concurrently |
| **D31** | **PR #7 (the reconciliation ledger) merged docs-only before the fold** | Landed evidence, no gated verdict involved. An unmerged evidence branch is the un-landed-record defect (C-44) this project keeps naming |

### 16.4 — The fixture-corruption incident, recorded as a live demonstration

During the UX lens audit, a probe pointed `MapperApp` at the real `fixtures/` directory. The
inspector's commit-on-blur **wrote through**: `fixtures/legacy.mmd` and `fixtures/legacy_nodos.yml`
were modified on disk, turning `erp[Sistema ERP Legacy]` into `erp[n]`.

Restored read-only via `git show HEAD:<path>` (a mutating `git checkout` was correctly refused under
the audit's no-mutating-git instruction) and **verified by sha256 against HEAD — both MATCH**. The
first probe's output was discarded; every later probe ran in a temp directory.

**A single keystroke, with no confirmation and no explicit edit gesture, permanently replaced an
acta reference in a tracked file.** This is the strongest available evidence for `UX2-C-01`,
obtained by accident, on the real store. **It travels with US-N14 to the follow-on design batch**,
which is where the confirmation-affordance ruling lives. Carried as a batch risk, not merely as an
incident log.
