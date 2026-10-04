# Security Review — increment 013, S-B(+C) (gate 2 of 2)

**VERDICT: PASS** — no HIGH. Ship. Two MEDIUM findings are recommended as a
same-batch fold (**F1** is one test I wrote and verified); **F3**/**F4** are
latent/pre-existing and route to a later increment.

The increment is **net security-positive and I measured that**, not inferred it.
Routing `node.ficha.title` through `layered._clip` closes a real hole that
`outline.py`'s own comment records as open (`B-47`/`A-89`): with the coercion
removed, `U+001B`, `U+202E` and `U+E0041` reach the painted row **and the
exported SVG**, and the SVG stops being well-formed XML. With it, none do and it
parses. The problem is not the code. The problem is that almost nothing tests it.

---

## Scope reviewed

`git diff fc0aeff~1..6bb1abf -- mapper/ tests/` — 6 files, +922/−24:
`mapper/app.py`, `mapper/views/outline.py`, `tests/test_a3_census.py`,
`tests/test_agree_floor.py`, `tests/test_canvas_header_charge.py`,
`tests/test_outline_caps.py`. Read beyond the diff for context:
`mapper/views/layered.py` (`_clip`, `_fit`), `mapper/darkside.py` (`plain`,
`COERCION_RANGES`), `mapper/mermaid.py`, `mapper/import_csv.py`,
`mapper/store.py`, `mapper/export.py`, `mapper/model.py`.

**What I did NOT review:** the docs-only commits (`5333618`, `9c8fe24`,
`ae501ea`) beyond reading `01-requirements.md` for traceability; `views/radial.py`
(`S-D`'s file); the 19 deselected lane tests; `views/lane.py`'s unreachable
renderers (`B-49`'s raw survivors) — outline was my remit and outline is reachable.

**What I could not determine:** whether a lone surrogate can reach a
`ficha.title` in practice (**F5**). Every file read in `mapper/` uses
`encoding="utf-8"` with strict errors, which cannot produce one; a YAML/JSON
`\ud…` escape is the only candidate door and I did not establish that a *title*
can carry one. Reported as an observation, not a finding.

**Tree integrity:** I made **zero** writes to the repo. An `Edit` of
`outline.py:233` was denied by the permission classifier, so I ran every mutant
**in-memory** via a pytest plugin outside the repo — which is strictly better
here, since it removes any restore-failure risk. `git status --porcelain` is
empty and the hashes are unchanged, verified before and after every run:

```
f73f703cfcb4dc695bcb167eff00d3e85edae2423ec9de8ccca3621515a64670  mapper/views/outline.py
ac993a0ab1c6a10125ecbacbf519116481ed6f93488bb16d6072d2b7e81eeea0  mapper/views/layered.py
4568b40d1f4d04470f82deeafad091bec4341093cb731b6dee15792a770fd9f0  mapper/darkside.py
33499cfb0707ad44bdbd44766e9d11d6f1be15177ba102d6cca1e03e8cd79bb5  mapper/app.py
```

Probes live outside the tree in `C:\Users\<operator>\clde\.sec-probe\`.
No ANCHOR MISS — I never anchored on repo text. `FLAKE-1` did not fire in any run.
`ruff` = **27**, unchanged.

---

## THE ONE THING GATE 1 ROUTED TO ME

**Answered by firing: the coercion is preserved, the cut manufactures nothing,
and the ordering claim is true but for the wrong reason.**

`_clip` is `darkside.plain(s)` followed by a prefix truncation, so the coercion
the old `darkside.plain(node.ficha.title)` did is not lost — it moved inside.
Fired over every cap from 1 to 100 against a title carrying `U+202E`, `U+202C`,
`U+200B`, `U+E0041`, `U+0007`, `U+001B`: **zero** covered code points survive any
cut. Row-level check on a real graph: every row clean.

**But `LLR-COERCE.2`'s stated rationale is unsound for the shipped `plain`** —
see **F2**. `_CONTROL_MAP` maps each of the 235 banned code points to exactly one
character (`U+FFFD`), so `plain` is length- and index-preserving, and therefore
`truncate(plain(s)) == plain(truncate(s))` **identically**. Proven by
construction and fuzzed over 20,000 random hostile pairs: **0 differences**. The
comment's scenario — "cutting between a `U+202E` and its terminator manufactures
an unterminated override" — cannot occur, because `plain` *replaces* the
`U+202E` rather than deleting it. There is never an override left to strand.

That is confirmed by mutant **M3** (truncate-then-coerce, the exact order the
requirement forbids): **1058 passed, 19 deselected, 3 xfailed — fully green on
the entire suite.** That is not a test gap; it is the suite correctly failing to
detect a distinction that does not exist.

So the property that is actually load-bearing today is the plain one: *outline's
title path is coerced at all*. That is what **F1** is about.

---

## Findings

### F1 — outline's new coercion call site is not independently armed, and `LLR-COERCE.2`'s designated arm does not exist  [Severity: MEDIUM]

- **What:** Removing the coercion from outline's title path costs **zero test
  signal**. Mutant **M1** (`_clip` → identity: no coercion, no cap) and mutant
  **M2** (`_clip` → `darkside.plain` only: coercion kept, cap removed) fail
  **exactly the same 3 tests**, all of them cap tests
  (`test_a_monster_title_is_clipped_to_one_frame`,
  `test_the_clip_uses_the_existing_ellipsis_idiom`). The coercion contributes
  nothing the suite can see.
  Separately, `01-requirements.md:6088` designates **`TC-081`** as
  `LLR-COERCE.2`'s arm — "`views/layered.py::_fit` coerces before truncating;
  split-at-width arm". `grep -rn "TC-081" tests/` returns **nothing**. The
  requirement is recorded as covered by a test that was never built.
- **Where:** `mapper/views/outline.py:233`;
  `tests/test_outline_caps.py:152-162`; `.dev-flow/.../01-requirements.md:6088`.
- **Why it matters:** measured positive control — with the coercion removed,
  `U+001B` (a terminal escape), `U+202E` and `U+E0041` (TAG block: invisible
  everywhere, maps 1:1 onto ASCII, trivially recovered by any later reader)
  reach the painted row **and** the exported SVG, and the SVG is no longer
  well-formed XML. This batch already has the precedent: `Inc-REPAIR` S-E found
  an `escape`→`plain` swap that **removed** a guard at a parsing sink, and
  `B-49` carries 38 unaudited sinks. An unarmed guard on a **reachable**
  renderer is exactly how that recurs.
  Mitigating: `_clip`'s coercion is *not* wholly undefended — mutant **M7**
  (coercion dropped from `_clip` itself, repo-wide) reddens
  `tests/test_fold.py::test_tc_033_the_fold_pill_coerces_a_hostile_branch_title`
  and `::test_llr_n06_2_3_every_repainted_region_coerces_what_it_paints`. So a
  refactor of `_clip` **would** be caught. What is undefended is a change at
  **outline's own call site** — the line this increment just wrote.
  That is why this is MEDIUM and not HIGH.
- **Aggravating:** `test_the_clip_uses_the_existing_ellipsis_idiom`'s docstring
  claims the security property — "`layered._clip` is also where `LLR-COERCE.2`'s
  ordering lives … so routing through it fixes the ordering as well as the
  bound" — while its only assertion is `fat.endswith("…")`. A reader auditing
  coverage by docstring will conclude this is armed. It is not. This is the
  vacuous-check pattern the batch's own control catalog names.
- **Recommendation:** add the arm below to `tests/test_outline_caps.py`. I wrote
  and **verified** it: green on shipped code (4 passed), red on **M1** (3 failed
  — both parametrised cases plus the SVG sink). It carries its own non-vacuity
  control, and writes every hostile point as a number so the file contains no
  control byte, matching `darkside.py`'s convention.

```python
BANNED = {cp for lo, hi in darkside.COERCION_RANGES for cp in range(lo, hi + 1)}
RLO, PDF, ESC, TAG = 0x202E, 0x202C, 0x001B, 0xE0041

@pytest.mark.parametrize("cut", ["under", "over"])
def test_llr_coerce_2_the_outline_title_is_coerced_on_both_sides_of_the_cut(cut):
    """`_clip` is reached from `_rows` for a FILE-DERIVED value, and it is the
    only thing between a hostile sidecar and BOTH painted surfaces -- the
    terminal row and `export.save_svg`'s output.  Parametrised over a title
    shorter and longer than the cap because the two take different branches of
    `_clip`; a short-only case would not exercise the cut at all."""
    pad = "x" * (W * H * 2 if cut == "over" else 4)
    title = "a" + chr(RLO) + pad + chr(PDF) + chr(ESC) + chr(TAG)
    painted = _row_for(title)          # rows[1] of `_rows` on a one-node graph
    leaked = sorted({ord(c) for c in painted} & BANNED)
    assert leaked == [], f"uncoerced code points reached the painted row: {[f'U+{c:04X}' for c in leaked]}"

def test_llr_coerce_2_positive_control_the_oracle_can_fail():
    """NON-VACUITY: the same oracle over the UNCOERCED title reports four."""
    title = "a" + chr(RLO) + "b" + chr(PDF) + chr(ESC) + chr(TAG)
    assert len(sorted({ord(c) for c in title} & BANNED)) == 4

def test_llr_coerce_2_the_export_sink_stays_well_formed():
    """`B-47`/`A-89`'s sink -- the row outline hands `save_svg` used to carry ESC
    and the TAG block into the file verbatim."""
    text = OutlineRenderer().render(g_with_hostile_title, ViewState(w=W, h=H))
    export.save_svg(text, out)
    raw = out.read_text(encoding="utf-8")
    ET.fromstring(raw)                 # ParseError if the coercion was lost
    assert sorted({ord(c) for c in raw} & BANNED) == []
```

  Also: either build `TC-081` or correct the traceability row so the requirement
  is not recorded as covered by a test that does not exist.

### F2 — the coercion-ordering rationale is unsound for the shipped `plain`, and it was just copied into a second file  [Severity: LOW]

- **What:** Both `layered._clip`'s docstring and the new comment at
  `outline.py:226-232` justify the coerce-then-truncate order with a scenario
  that cannot occur: "cutting between a `U+202E` and its terminator manufactures
  an unterminated override that no later coercion can repair." `_CONTROL_MAP`
  maps every banned point to a single `U+FFFD`, so `plain` is length- and
  index-preserving and the two orderings are **provably identical** — fuzzed
  over 20,000 hostile pairs, 0 differences; mutant **M3** green on all 1058.
  There is never a surviving `U+202E` to leave unterminated.
- **Where:** `mapper/views/layered.py:79-86`; `mapper/views/outline.py:226-232`.
- **Why it matters:** low direct risk — the order is harmless either way today.
  The hazard is that the comment describes a dependency the code does not have,
  so it reads as a satisfied safety requirement. It would become **real** under a
  natural refactor: changing `plain` to *delete* banned points (translate to
  `None`) instead of replacing them — a plausible "stop showing `U+FFFD` noise"
  change — makes `plain` length-*reducing*, at which point the ordering genuinely
  starts to matter and nothing in 1077 tests would notice.
- **Recommendation:** correct the comment to state the actual invariant —
  *`plain` is 1:1 and length-preserving, so the order is currently immaterial;
  it is written coerce-first so that it stays correct if `plain` ever becomes
  length-reducing.* Then pin the invariant itself, which is the cheap durable
  guard: `assert all(len(darkside.plain(chr(c))) == 1 for c in COERCION_RANGES-expansion)`.

### F3 — outline's walk is exponential on a multi-parent graph, and `MAX_RENDER_NODES` does not bound it  [Severity: MEDIUM — latent]

- **What:** `_rows`'s `walk` has **no visited set**. `subtree_counts()` runs
  first and refuses **cycles**, but a diamond DAG is not a cycle — it memoises
  cleanly and passes. `walk` then re-expands every shared node once per path.
  `MAX_RENDER_NODES = 12000` gates `len(graph.nodes)`, which is the wrong
  quantity: measured, **58 nodes** produce **2,097,150 rows**.
- **Where:** `mapper/views/outline.py:212-265` (`walk`), guarded at `:150` by
  `len(graph.nodes) > MAX_RENDER_NODES`.
- **Why it matters:** measured, doubling per rung, from a graph built by the CSV
  importer:

  | CSV bytes | nodes | rows built | time |
  |---|---|---|---|
  | 579 | 43 | 16,382 | 0.09 s |
  | 675 | 49 | 262,142 | 3.1 s |
  | 771 | 55 | 1,048,574 | 12.8 s |
  | 819 | 58 | 2,097,150 | 24.0 s |

  Each further 48 bytes doubles it; ~1.1 KB reaches OOM. `layered.painted_ids`
  (34 ms) and `radial.painted_ids` (117 ms) on the same graph do **not** blow up
  — outline is the only renderer without a visited set.
- **Why it is LATENT and not HIGH:** I fired the reachability chain rather than
  assuming it. `mermaid.parse` **refuses** multi-parent
  (`ParseError: node 's1' has multiple parents (out of MVP scope)`), and
  `MapScreen`'s graph always arrives via `MapScreen(map_id)` → `store.load` →
  `mermaid.parse`, or via `base_graph.focus()` on an already-parsed tree. The
  CSV preview screen renders with `LayeredRenderer` only. So no multi-parent
  graph currently reaches outline in production.
- **Recommendation:** add the visited set — outline is the outlier and it is
  three lines. Defence-in-depth: the only thing preventing exploitation today is
  a guard in a *different module* that outline neither knows about nor asserts.
  Either give `walk` a `seen` set (matching `_branch_coverage_glyph`, which
  already carries one for exactly this reason), or make the tree invariant
  explicit in `subtree_counts` so a DAG is refused where a cycle is.

### F4 — `store.save` accepts a multi-parent graph that `store.load` refuses  [Severity: MEDIUM — pre-existing, outside this diff]

- **What:** `store.save` checks `graph.find_cycle()` but not multi-parent.
  Fired: a CSV-imported diamond (19 nodes, 6 multi-parent, no cycle) → **save
  ACCEPTED**, writing `.mmd` + `.yml`; → **load REFUSED**
  (`MapStoreError: no se pudo leer la ficha de lad: lad_nodos.yml ilegible
  (ParseError)`).
- **Where:** `mapper/store.py:690-710`; the CSV door is
  `mapper/import_csv.py:77-88` (duplicate `id` rows each emit their own edge).
- **Why it matters:** this is precisely the `LLR-R01.5 (A-2)` asymmetry the
  save-side cycle check was added to prevent — "never write what this store's own
  read side refuses" — recurring for a second shape. The operator imports a CSV,
  saves, and the map is listed but unopenable with no in-app repair route.
  Availability/data-integrity, not confidentiality.
- **Recommendation:** extend the save-side refusal from `find_cycle()` to the
  full tree invariant, or reject duplicate `id` rows at CSV import. Note this
  also closes **F3**'s only production door — but F3 should still be fixed in
  outline, because relying on it is the cross-module coupling F3 objects to.

### F5 — lone surrogates survive `darkside.plain` (reachability NOT established)  [Severity: LOW — observation]

- **What:** `COERCION_RANGES` does not cover `U+D800`–`U+DFFF`. Fired:
  `plain()` and `_clip()` both pass `U+DCFF` through unchanged, and the result
  raises `UnicodeEncodeError` on `.encode("utf-8")`.
- **Why I am not rating it higher:** I could not construct a door. All
  `mapper/` file reads use `encoding="utf-8"` with strict errors, which cannot
  yield a lone surrogate; the title path originates in `.mmd` text, where
  `\ud…` is literal characters, not an escape. Pre-existing in `darkside.plain`;
  this increment neither helps nor hurts it.
- **Recommendation:** none blocking. If cheap, add `(0xD800, 0xDFFF)` to
  `COERCION_RANGES` — it is consistent with the existing "may not reach a
  painted surface" rule and costs one tuple.

---

## Cleared by firing — no finding

| Scope item | Result |
|---|---|
| **Truncation seam manufactures anything?** | **No.** No covered code point survives any cut (caps 1..100, and 8..25 straddling an override/terminator pair). |
| **Split surrogate?** | **Impossible.** Python strings are code points; a prefix slice cannot split an astral character — fired, `U+1F600` survives whole. |
| **Combining mark stranded onto the ellipsis / next row?** | **No.** A *prefix* cut can only drop a mark, never its base — the base always precedes. Fired at three boundary caps. Row-level check: adjacent rows inherit nothing. |
| **Depth marker bounded? format/width surprise?** | **Bounded** at `len(str(level)) + 2`. Worst overrun past budget is **1 cell** at realistic depths (≤12000); the 13-cell case needs `level = 10^12` at `budget = 2`. No format-string surface — `level` is an `int` interpolated as a *value*, never a spec. Negative levels return `""`. |
| **`floor_reached` public — misuse / disagreement with `_fit_declared`?** | **Sound.** Swept **1,152 frames** across 4 title shapes (plain, 20k-char monster, hostile-code-point, full-width CJK) × 4 depths × 8 widths × 9 heights: **0 disagreements, 0 silent-hides, 0 empty frames**. Pure, no side effects, cost bounded by `h`. Well armed — mutant **M5** (stub to `False`) reddens 4 tests. |
| **Header-charge degrade exploitable?** | **No.** `_current_renderer()` is a closed 3-way dispatch over instance attributes, so the `LookupError` branch is **unreachable in production** — only `TC-R08`'s injected foreign renderer takes it. The `try` wraps **only the dispatch**, not the invocation, so a `KeyError` raised *inside* a charge function propagates rather than being swallowed. And a wrong charge moves `_canvas_size` and `painted_ids` **together**, so the declaration stays honest: an overcharge under-displays but can never produce a false "nothing hidden". |
| **Indent cap effective?** | **Yes.** Depth 11999 builds 1,189,640 chars, max row 101 cells — against ~144M uncapped. Well armed: mutant **M4** reddens 12 tests. |
| **Row cap effective?** | **Yes.** A 400,000-char title yields a 4,812-cell row against `row_cap` 4,720. `_fit` breaks at budget, so measuring costs `O(h)`, not `O(n)`. |
| **Secrets / deps / external tools / destructive commands** | **None.** The diff is pure rendering code: no new dependency, no network call, no subprocess, no credential, no file write, no new MCP/Composio/integration surface, no destructive command. Nothing to scope-review. |

**Resource note (not a finding):** `_rows` runs once in `render` and again in
`painted_ids`, and `refresh_canvas` can run up to three passes — so `_clip` walks
every full-length title up to ~6× per frame. Coercion necessarily precedes
truncation, so cost is linear in *total input size*, not in the capped output:
12,000 nodes × 400k-char titles took 17.8 s per pass. That is proportional to a
~4.8 GB map file, so it is input-bounded rather than superlinear. Flagging it
only because the caps bound *storage and render* cost, not *coercion* cost.

---

## Evidence checklist

- [x] **Each finding has what · where · why · recommendation** — F1–F5 above, each with file:line.
- [x] **Each finding has a severity rating** — 2 MEDIUM (F1, F3), 1 MEDIUM pre-existing (F4), 2 LOW (F2, F5).
- [x] **No secret values in output** — none present in the diff; the workspace path is redacted as `C:\Users\<operator>\`.
- [x] **Verdict explicit** — PASS, stated first.
- [x] **New tool/integration scope + blast radius** — **N/A, and verified N/A**: the diff adds no external-action surface (no dep, network, subprocess, or connector).
- [x] **Fired, not inferred** — 7 probes + 7 mutants; positive control on the SVG oracle; reachability chain fired end-to-end rather than reasoned.
- [x] **Tree byte-identical** — 4 hashes unchanged, `git status --porcelain` empty, zero repo writes.

**Mutant ledger** (in-memory; baseline for the 6-file subset = 81 passed):

| # | Mutation | Result |
|---|---|---|
| M1 | `outline._clip` → identity (no coercion, no cap) | 3 failed — **all cap tests** |
| M2 | `outline._clip` → `plain` only (cap removed) | 3 failed — **identical set ⇒ coercion unarmed (F1)** |
| M3 | `outline._clip` → truncate-then-coerce | **full suite green: 1058 / 19 / 3 xfail** ⇒ order is a no-op (F2) |
| M4 | `outline._indent` → uncapped | 12 failed — well armed |
| M5 | `outline.floor_reached` → `False` | 4 failed — well armed |
| M6 | `_clip` itself → wrong order, repo-wide | **full suite green: 1058 / 19 / 3 xfail** — as the fuzz proof predicts (identical function) |
| M7 | `_clip` itself → coercion dropped, repo-wide | full suite **1 failed** (`-x`, after 215 passed); on the coercion-relevant subset, **2 failed**, both in `test_fold.py` ⇒ `_clip` **is** armed; outline's **call site** is not |

---

## Verdict

- [x] **OK to ship** — no HIGH finding.
- [ ] OK to ship with the listed mitigations applied first
- [ ] Block

**Recommended fold before close (not blocking):** **F1**'s arm — the test is
written and verified above (green on shipped, red on M1). It is the one place
where this increment's security improvement is real but undefended, and the
batch has a live precedent of exactly that regression. **F2** is a two-line
comment correction that belongs with it.

**Route onward:** **F3** and **F4** to a later increment — both are pre-existing,
both are latent behind `mermaid.parse`, and F4 owns `store.py`, which is not this
stage's file.
