# Security Confirmation — Inc-3 post-fix tree (`feat/ui-next-batch-02`, uncommitted over `954f8f3`)

## VERDICT: **BLOCK — 1 HIGH**

**Both prior HIGHs are DISCHARGED.** `SEC-F1` (`SchemaField.key` → SVG) and `SEC-F2` (`_minimap_text`)
are closed at the sink and each is now killed by a named arm. Both self-reported defects (the
id-less breadcrumb, the `_branch_coverage_glyph` hang) are confirmed real, confirmed fixed, and
confirmed guarded. Nothing in this increment regresses.

The block is **not** on anything Inc-3 changed. It is on **F-A**: the field `SEC-F1` names —
`SchemaField.key` — reaches a *second* sink in the *same* repaint path `LLR-N06.2.3` enumerates,
`FichaInspector`'s widget id, where it **kills the application on map open**. It is pre-existing at
`954f8f3` (reproduced there), so it is a routing decision rather than a rework of this increment —
but it cannot be signed past silently, because it means a hostile `SchemaField.key` can never reach
the SVG sink `SEC-F1` hardened: **the session dies first**, and it dies for ordinary Spanish keys
like `año` and `fecha limite`, not only for hostile ones.

Two acceptable discharges are named under F-A. Either closes the block.

---

## Tree-integrity evidence

The shared working tree was **never written to** by this review, except for this one report file.

| Check | Result |
|---|---|
| Manifest before | `sha256sum` over 325 tracked+untracked files (`.git`, `__pycache__`, `.pyc` excluded) → manifest digest `284ea6730ff1f24e97bba183f087c63d3aa2aef90b8599c57c8a42c0f32b19fe` |
| Manifest after | `diff BEFORE AFTER` → **one added line only**: `.dev-flow/…/increment-003-code-review-confirmation.md`, written by the concurrent code-review gate. **324 of 324 pre-existing files byte-identical.** |
| Where the work ran | `tar`-exported copy at `…/scratchpad/work` with its own `git init` (the censuses call `git ls-files`), plus a second `git archive 954f8f3` export at `…/scratchpad/base` for the base-state reproduction |
| Mutation restores | every mutant restored from the in-memory original and proven by sha256 returning to its pre-mutation value; **21 of 21 `OK`, 0 `MISMATCH`** |
| Scratch worktree at close | `git status --porcelain` → empty |
| Product-file digests, shared tree, at close | `app.py f90835563212f2a0…` · `views/layered.py d4d82a2052a198da…` · `views/outline.py 74604dbfdb6d35c3…` · `views/radial.py def09fbe114af7e5…` · `widgets/rail.py 508b5d5d1ebc644a…` · `widgets/inspector.py 2ace7f91d3bdb946…` · `screens/factory.py 771a15e3c418b4c8…` · `screens/coverage.py 63cf11a4a01b8f8a…` |

Baseline, re-executed independently in the export: `789 passed, 17 deselected in 94.61s`, exit 0;
slow lane `17 passed, 789 deselected in 26.18s`, exit 0. Both match the increment's claim.

**No hostile code point is spelled into any file this review wrote.** Every payload in every probe is
built with `chr(0x…)` at run time; payloads are named below by code point only.

---

## Prior HIGH 1 — `SchemaField.key` reached the exported SVG uncoerced (`SEC-F1` / `B-47`)

### **DISCHARGED**

**Product fix present.** `mapper/views/layered.py:473` — `cv.put(xx, y + 2, darkside.plain(sf.key)[:1] or " ", darkside.MUT)`.

**Transcript 1 — the sink, 30 configurations.** 3 reached renderers (`LayeredRenderer`,
`OutlineRenderer`, `RadialRenderer`) × 5 sizes (80×24, 140×45, 30×12, 200×60, 50×20) × 2 fold states
(`frozenset()`, `frozenset({"root"})`), on a graph whose `graph.schema` carries U+0001 and U+202E in
the **keys** and a 9-code-point payload in the **labels**, and whose fichas carry the payload in
title/meta/notes and in `fields`. For every configuration: the rendered `Text.plain` carries 0 banned
code points; `mapper.export.save_svg` writes a file that **parses under
`xml.etree.ElementTree.fromstring`**; and the SVG carries 0 banned code points.
**30 passed, 0 failed.**

**Transcript 2 — the real chain.** `MapStore.save` → `MapStore.load` → `MapScreen` mount → `e`
keypress → `action_export_svg` → `save_svg`, at a 160×48 terminal, default (`LayeredRenderer`) view
asserted (`screen._current_renderer() is screen.renderer`), 4 nodes asserted surviving the round
trip, hostile payload asserted surviving the load (`any(ord(c) in BANNED for sf in loaded.schema for c in sf.label)`).
Result: written SVG parses as XML, `SVG leaks: []`, composited frame `FRAME leaks: []`.

**The load path really is uncoerced** — the precondition the fix rests on, asserted rather than
assumed: `MapStore._graph_from_sidecar` (`store.py:342-350`) runs `_coerce_text_fields`, which is a
*type* coercion to `str`, not a code-point coercion, and the loaded `SchemaField.key` / `.label`
still carry their payload.

**The census arm genuinely enters the leaking branch — it is not a fix-shaped comment.**
`tests/test_inc3_census.py:271-274` now sets a two-entry `graph.schema`, so `legacy = bool(graph.schema)`
at `layered.py:_geometry` is `True` and the legacy card is drawn. Proven by mutation, not by reading:

| Mutant | Result |
|---|---|
| **M-A** — revert `layered.py:473` to `cv.put(xx, y + 2, sf.key, …)` | **KILLED.** `1 failed, 788 passed, 17 deselected` — `test_inc3_census.py::test_a89_every_reached_renderer_coerces_what_it_paints`. Restore sha256 `d4d82a2052a198da → d4d82a2052a198da OK` |

**`SchemaField.label`, checked as instructed.** It reaches three sinks, and only two are safe:

- `FichaInspector._label` (`inspector.py:132` → `191/194`) — `darkside.plain`. **Safe.**
- `MapScreen`'s hint at `app.py:2030` — `HintLine.set_hint` → `darkside.hint_line` → `plain(text)`. **Safe.**
- `CoverageScreen.on_mount` (`coverage.py:86-89`) — `rich.markup.escape` only. **LEAKS** → finding **F-B**.

`label` reaches no renderer and no `save_svg`, so the hostile `label=` in the A-89 fixture is inert
there. Harmless, but it should not be read as coverage of `label`.

**One thing that changes the risk picture and belongs to this finding.** The chain in Transcript 2 had
to use identifier-safe schema *keys*. A key carrying **any** banned code point cannot be driven to the
export at all, because `FichaInspector._rebuild` kills the app on mount first — finding **F-A**. So the
`layered.py:473` coercion is correct and necessary defence in depth, but the leak `SEC-F1` described is
not the live consequence of a hostile key today; the crash is.

---

## Prior HIGH 2 — `_minimap_text` interpolated a ficha title uncoerced (`SEC-F2`)

### **DISCHARGED**

**Product fix present.** `mapper/app.py:1549` — `name = darkside.plain(self.graph.nodes[cid].ficha.title or cid)`.

| Mutant | Result |
|---|---|
| **M-B** — revert to `name = self.graph.nodes[cid].ficha.title or cid` | **KILLED.** `1 failed, 788 passed` — `tests/test_fold.py::test_llr_n06_2_3_every_repainted_region_coerces_what_it_paints`, failing at the region half with `('map-minimap', ['0x1', '0x200b', '0x202c', '0x202e'])`. Restore sha256 `f90835563212f2a0 → f90835563212f2a0 OK` |

**The new census is sound in construction.** `test_fold.py:294-323` derives the swept region ids from
the `MapScreen.refresh_canvas` AST (not by name-splitting — it correctly disambiguates
`_ImportPreviewScreen`'s own `refresh_canvas`), asserts `map-minimap ∈ regions` and `len(regions) ≥ 4`
before evaluating anything, reads each region off the **composited frame** via `rows_in`, and then
sweeps the whole frame. It asserts its payload is in `COERCION_RANGES` and asserts the graph survived
the store round trip (`len(screen.graph.nodes) == 7`) before it reads a row — both non-vacuity guards.

---

## Self-reported 1 — the breadcrumb leaked an uncoerced `ficha.title` into the frame

### **CONFIRMED, and the general question answered**

**Product fix present.** `app.py:1690-1692` coerces **every** crumb segment, not only the title.

| Mutant | Result |
|---|---|
| **M-C** — revert to `tab.set_crumb(self._current_crumb() + [node_title])` | **KILLED.** `1 failed, 788 passed` — same arm, at the **frame** half: `['0x1', '0x200b', '0x202c', '0x202e']`. Restore `OK` |

**The general question — does the census catch id-less sinks as a class?**
I built the sibling the brief asks for and two more, all reaching the frame through widgets the
region sweep cannot address:

| Mutant | Sink | Result |
|---|---|---|
| **M-H** (constructed by me) | a **new** `refresh_canvas` sink: `self.query_one(KeyBar).set_groups([("nodo", [("z", node.ficha.title …)])])` — `KeyBar` is composed with **no id** and looked up **by type**, and `darkside.keybar` does not coerce its labels | **KILLED, 2 arms.** `test_llr_n06_2_3_…` + `test_overflow.py::test_a_region_too_short_for_a_body_row_declares_nothing_painted`. Restore `OK` |
| **M-O** | `layered.py:546` selection-highlight title, coercion removed **layout-preservingly** (a golden digest cannot see it) | **KILLED.** `test_llr_n06_2_3_…` |
| **M-Q** | `inspector.py:123` `FieldInput(value=…ficha.title…)` | **KILLED.** `test_llr_n06_2_3_…` |

**Answer: yes — for the map frame.** The frame-level half is lookup-agnostic and catches id-less
sinks as a class.

**But the class is bounded twice, and the bounds are demonstrated, not argued.** The frame sweep can
only see what *that fixture* makes the code paint, on *that screen*. Five mutants that remove a
coercion **survived the entire suite** — see finding **F-D** — and two shipped sinks on other screens
leak today — findings **F-B** and **F-C**.

---

## Self-reported 2 — `_branch_coverage_glyph` HANGS on a cyclic graph

### **CONFIRMED; the `seen` set closes it; all three guard placements are live**

**Product fix present.** `app.py:1514-1518` — a `seen` set skipping already-expanded children.

| Mutant | Result |
|---|---|
| **M-D** — delete the `seen` check | **HANG.** Full suite **TIMED OUT at 600s** against a 95s baseline. Isolated with `-v`: the suite stops at `tests/test_pan.py::test_a_layout_that_cannot_be_drawn_does_not_kill_the_app`, which **hangs instead of failing** — the worst outcome, and exactly what the fix removes. Restore `f90835563212f2a0 → f90835563212f2a0 OK` |

**Guard placement — the author's re-attribution is CORRECT.**

| Mutant | Result |
|---|---|
| **M-I** — narrow `_pan`'s `except Exception` to `except ZeroDivisionError` | **KILLED.** Same arm. `--tb=line`: `mapper/views/layered.py:174: ValueError: cycle through n0: the graph is not a tree` — raised inside `_tree_layout`, reached from `pan_extent`, i.e. **`_pan`'s own call**, not either of the two calls the prior review named |
| **M-J** — move `_reclamp_pan` back **outside** `refresh_canvas`'s `try` | **KILLED.** Same arm, same `ValueError` |
| **M-K** — delete `_unpainted_ids`'s `try/except → None` | **KILLED.** Same arm, same `ValueError` |

All three restores `OK`. Each of the three guard placements is load-bearing and separately killed.

**Reachability, re-verified rather than adopted.** The arm's docstring says the state is not reachable
through the shipped loaders. I confirmed it: `mermaid.parse` calls `_ensure_node` for **both** edge
endpoints and raises `ParseError` on a second parent (`mermaid.py:79-87`), and `MapStore.load` routes
a cycle to `MapStoreError`. So this is defence in depth and is labelled as such — an honest claim,
not an inflated one.

---

## Re-running the guarantee: what is still not in the census

The brief's question is "what is still *not* in the census". Answered by mutation over the shipped
sinks, full suite per mutant. **Survivors are the answer.**

### Field inventory — every file-derived shape, its sinks, and its coverage

| Field | Sinks reached | Coerced? | In a census? |
|---|---|---|---|
| `Node.id` | rail, minimap, inspector header, factory tree, `CoverageScreen` | `plain` everywhere **except** `CoverageScreen` (`escape` only) | partial — **F-B** |
| `Ficha.title` | 3 renderers → canvas + `save_svg`; rail; inspector; minimap; breadcrumb; fold pill; selection block; factory tree; `CoverageScreen` | `plain`/`_fit` everywhere **except** `CoverageScreen` and `FactoryScreen._refresh` crumb | yes, except **F-B**/**F-C** |
| `Ficha.meta` | layered (concept card), outline | `_fit` / `plain` | yes (A-89 fixture sets `meta`) |
| `Ficha.notes` | inspector only (not painted by any renderer) | `plain` | yes |
| `Ficha.state` | dict key into `STATE_STYLE` only — never painted verbatim | n/a | n/a |
| `Ficha.fields` **values** | `layered.py:456-459` legacy `◫` document chip; inspector | `_fit` / `plain` | **NO — M-L2 survived** |
| `Ficha.attachments[].kind/path/caption` | inspector chip + target line; `_event_toast`; `osopen.open_external` | `plain`; `osopen` is separately confined and sound | **NO — M-S survived** |
| `SchemaField.key` | `layered.py:473` legacy letter row; **`inspector.py:138` widget id** | `plain(...)[:1]` at the renderer; **raw into the id** | renderer yes (M-A); **id sink: NO — F-A** |
| `SchemaField.label` | inspector; hint line; `CoverageScreen` | `plain`, `plain`, **`escape` only** | **F-B** |
| `SchemaField.kind` | not painted | n/a | n/a |
| `Edge.label` | not painted; `.mmd` round trip only | n/a | **F-H** (round-trip, not a leak) |
| `DiffResult.changed` (schema keys) | `layered.py:449` diff chip | `_fit` | **NO — M-N survived** |
| `DiffResult.removed_titles` | `layered.py:520` ghost row | `_fit` | **NO — M-M survived** |
| `Document.name/source/tags/inherited/path/kind` | `FactoryScreen._preview`, `_tags_table`; `_tree_lines` | `_tree_lines` uses `plain`; `_preview`/`_tags_table` use **`escape` only** | **NO — F-C, M-T** |
| `Graph.load_warnings` | toast | `plain` | yes |
| `map_id` / link chain | breadcrumb | `plain` | yes (M-C) |

### The `A-89` derivation, re-run against the attribute-form mutant

| Mutant | Result |
|---|---|
| **M-G** — wire `LaneRenderer` into `mapper/app.py` in **attribute form** (`from .views import lane as _lane_mod` / `_lane_mod.LaneRenderer`) | **KILLED, 2 arms.** `test_a89_the_reached_set_is_pinned_so_wiring_lane_up_pulls_it_in` **and** `test_a89_every_reached_renderer_coerces_what_it_paints`. `2 failed, 787 passed`. Restore `OK` |

`reached_renderers()` (`test_inc3_census.py:208-212`) now matches `ast.Attribute.attr` as well as
`ast.Name.id`. The prior pass's survivor is dead. The derivation is genuinely derived: the exclusion
of `mapper/views/` is structural (`rel.startswith("mapper/views/")`), not a hand-listed skip.

### The two coercion properties, and where the kill comes from

| Mutant | Result |
|---|---|
| **M-E** — `layered._clip` stops calling `darkside.plain` | **KILLED, 8 arms.** `test_tc_033_the_fold_pill_coerces_a_hostile_branch_title`; `test_llr_n06_2_3_…`; `test_llr_coerce_2_no_truncator_emits_a_coerced_code_point[5][8][13][40]`; **`test_llr_coerce_2_the_split_at_width_arm`**; `test_a89_every_reached_renderer_coerces_what_it_paints`. `8 failed, 781 passed` |
| **M-F** — `views/outline.py` stops coercing | **KILLED.** `test_a89_every_reached_renderer_coerces_what_it_paints`. `1 failed, 788 passed` |
| **M-U** — `views/radial.py` stops coercing | **KILLED, 2 arms.** `test_export.py::test_at_009_the_exported_svg_carries_no_coerced_code_point` + the A-89 arm |

**The commutation arm (`B-58`) is still inert, and the kill comes from the discriminating arms.**
`test_llr_coerce_2_every_truncator_coerces_before_it_truncates` did **not** appear in M-E's failure
list at any of its six widths. Both properties the brief names hold on the shipped tree (789 green)
and both discriminate under mutation (M-E). The census's own docstring already says the commutation
arm is weak; that reading is confirmed, not merely repeated.

---

## Findings

### F-A — `SchemaField.key` is interpolated into a Textual widget id and kills the app on map open  [Severity: **HIGH**]

- **What:** `FichaInspector._rows` builds a widget id from a file-derived schema key. Textual rejects
  any id outside `[A-Za-z_-][A-Za-z0-9_-]*` with `textual.dom.BadIdentifier`. The exception is raised
  inside `_rebuild`, which `FichaInspector.show` schedules with `call_next` from
  `MapScreen.refresh_canvas` — **outside every guard in that method**. The application dies.
- **Where:** `mapper/widgets/inspector.py:137-140` — `FieldInput(value=…, id=f"insp-field-{field.key}")`.
  Reached from `mapper/app.py:1695` (`FichaInspector.show`), on the first paint of every map.
- **Why it matters:** measured, 6 of 6 keys take `app.is_running` to `False` at context exit, with the
  operator's unsaved edits in the session. It fires for **every** banned code point (U+0001, U+202E,
  U+200B tested) **and** for entirely benign Spanish schema keys — `a`+U+00F1+`o` (`año`) and
  `fecha limite` both kill it — so this is not only an adversarial case; it is the LATAM-Spanish
  happy path for a hand-written sidecar. It also **subsumes `SEC-F1`'s attack**: no hostile
  `SchemaField.key` can reach the SVG the increment hardened, because the session is already gone.
  Reproduced identically on a clean `git archive 954f8f3`, so it is **pre-existing, not a regression**.
- **Why the census cannot see it:** `LLR-N06.2.3` sweeps `#map-inspector` — it is one of the four
  enumerated regions — but it looks for banned **code points in painted rows**, never for **survival**,
  and its fixture (`test_fold.py:264-270`) carries **no schema at all**, so no `insp-field-*` widget is
  ever constructed. The `A-89` fixture was widened with a schema; the `LLR-N06.2.3` fixture was not.
  That asymmetry is the whole gap.
- **Recommendation — either discharge closes the block:**
  1. **Fix at the sink.** Do not put file-derived text in a DOM id. Key the field rows by schema
     *index*, keeping the key in an attribute:
     `FieldInput(value=…, id=f"insp-field-{i}")` with `self._field_keys[i] = field.key`, and update
     `focus_field` / `_commit` / `first_missing_key` to resolve through that map. Add an arm that opens
     a map whose schema keys are `chr(0x01)`, `a`+`chr(0xF1)`+`o` and `"fecha limite"` and asserts
     `app.is_running`. *(Preferred — it is 1 file and removes the class.)*
  2. **Route it,** the way `B-47` was routed into Inc-3 and `store.py` into Inc-REPAIR — but land the
     **red arm now**, in this increment, so the obligation cannot be lost between increments.
  Independently, widen the `LLR-N06.2.3` fixture to carry a non-empty `graph.schema`, attachments and
  documents, and add a survival assertion (`app.is_running`) beside the leak assertion. Without that,
  the census reports "no leak" on a screen that never rendered.

### F-B — `CoverageScreen` paints file-derived text through `escape` only  [Severity: MEDIUM]

- **What:** `rich.markup.escape` is markup escaping, not code-point coercion. `darkside.py:417-428`
  states this explicitly and `factory.py:246-251` records it as a defect fixed once already.
- **Where:** `mapper/screens/coverage.py:86-89` — `escape(node.ficha.title or node.id)` and
  `escape(",".join(missing))`, where `missing` is `[f.label for f in ficha.missing_required(schema)]`.
- **Why it matters:** measured on the composited frame after pressing `m` on a hostile map:
  leaked `['0x1', '0x200b', '0x202c', '0x202e', '0xe0041', '0xfeff']`. This is the surface the operator
  reads to decide **which node to go fix**, and U+202E there reorders one node's missing-field list
  under a neighbour's name — the same deception `SEC-F2` was raised for, one screen over. Pre-existing;
  `coverage.py` is outside Inc-3's declared file set.
- **Recommendation:** replace both `escape(...)` calls with `darkside.plain(...)`, and extend the
  frame sweep to push each modal screen (`m`, `d`, `?`, `ctrl+p`) before reading the frame.

### F-C — `FactoryScreen` paints documents through `escape` only  [Severity: MEDIUM]

- **What:** `Document.source`, `Document.tags` (keys and values), `Document.inherited`, the office
  preview text and the node crumb all reach the frame with `escape` and no coercion — while
  `_tree_lines` in the same file **does** coerce, with a comment explaining why `escape` is wrong.
  The file disagrees with itself.
- **Where:** `mapper/screens/factory.py:291-292, 296-297, 303-315, 337-341, 350`.
- **Why it matters:** measured after pressing `d` on a map whose `documents` carry the payload: leaked
  `['0x1', '0x200b', '0x202c', '0x202e', '0xe0041', '0xfeff']` into the composited frame. Documents come
  from the same `_nodos.yml` and travel with a cloned or shared map. Pre-existing; outside Inc-3's set.
- **Recommendation:** route `doc.source`, tag keys/values and the crumb through `darkside.plain`, in
  the same increment as F-B, and pin the file's own consistency with a per-file arm.

### F-D — five shipped coercions are unprotected: mutants survived the full suite  [Severity: MEDIUM]

- **What:** no live leak — the shipped code coerces at all five. But nothing in the suite can
  *notice* if it stops. Each mutant below removes only the coercion, preserving layout byte-for-byte
  on benign input, so golden digests cannot substitute for a coercion oracle.
- **Where / measured** (each: full suite, `789 passed, 17 deselected`, **0 failed**, restore `OK`):

  | Mutant | Sink | Why the census misses it |
  |---|---|---|
  | **M-L2** | `layered.py:459` legacy `◫` document chip, from `ficha.fields["D"]` | the widened `A-89` fixture has a schema but its fichas have **no `fields`**, so `doc` is always `""` and the branch paints a constant |
  | **M-M** | `layered.py:520` removed-node ghost titles, from `DiffResult.removed_titles` | no census fixture sets `diff` |
  | **M-N** | `layered.py:449` diff chip, from `DiffResult.changed` (schema keys) | same |
  | **M-S** | `inspector.py:155` attachment chip, from `Attachment.kind/caption/path` | no census fixture has attachments |
  | **M-T** | `factory.py:252` factory tree title | no census drives `FactoryScreen` |

- **Not a gap, stated so it is not miscounted:** **M-P** (`rail.py:230` label uncoerced) also survived,
  but it is an **equivalent mutant** — `darkside.fit(body, RAIL_WIDTH - 4)` at `rail.py:245/247` calls
  `plain` downstream on both branches, so no leak exists to detect. Correctly green.
- **Recommendation:** give the `A-89` fixture a `fields` dict, attachments, and a `DiffResult`, and add
  `FactoryScreen` to the frame sweep. That converts five silent survivors into five red arms.

### F-E — banned code points are spelled into shipped `.dev-flow` corpus  [Severity: LOW]

- **What:** the batch's own rule (`test_inc3_census.py:40`, `test_fold.py:186-190`) is that no source
  or artifact file holds a hostile code point; two artifacts violate it. Reported by code point and
  position only.
- **Where:** `.dev-flow/2026-08-25-ui-next-batch-01/02b-security-review.md` — U+202E ×2, character
  offsets 5646 and 29216. `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-001-code-review-confirmation.md`
  — U+200D ×4, first at offset 13430.
- **Why it matters:** both are prior-batch artifacts, **not in Inc-3's diff** — the Inc-3 diff itself is
  clean. But these files are corpus a scanner reads, and an unterminated U+202E in a security review
  reorders the very text that documents the threat.
- **Recommendation:** replace with `U+202E` written as a name; add the artifact tree to the existing
  code-point scan (it currently sweeps `mapper/` and `tests/` only).

### F-F — the operator's absolute path (and Windows username) ships in the artifacts  [Severity: LOW]

- **Where:** `increment-003.md:92`, and the same line in `increment-001.md:87` and `increment-002.md:75`
  — `cd C:/Users/jjgh8/Github/mapper`.
- **Why it matters:** `.dev-flow` is synced to the Obsidian vault by `dev-flow-sync` and these artifacts
  are the kind of thing that ends up in a client-facing report. The local username adds nothing.
- **Recommendation:** `cd <repo root>` in the reproduction blocks.

### F-G — a dangling edge kills `refresh_canvas` after the guard; could not construct from a file  [Severity: LOW]

- **What:** `_minimap_text` (`app.py:1541`) and `_branch_coverage_glyph` (`app.py:1525`) index
  `self.graph.nodes[...]` directly. An edge naming an absent node raises `KeyError` — from lines that
  sit **after** `refresh_canvas`'s `try/except`, so inside the message pump it would be fatal, the same
  shape as the cycle case Inc-3 just guarded.
- **Where:** `mapper/app.py:1525` and `:1541`.
- **Measured:** `refresh_canvas` on a graph with one dangling child edge → `KeyError`.
- **Reachability — "could not construct", not "unreachable":** `mermaid.parse` calls `_ensure_node` for
  both endpoints (asserted: endpoints − nodes = ∅), so I could not build a `.mmd`/`.yml` pair that
  produces one. Inc-3 chose to add a defence-in-depth arm for the sibling (cyclic) case and left this
  one; that asymmetry is the finding.
- **Recommendation:** `.get(cid)` with a skip, or fold the two minimap calls inside the same guard.

### F-H — `MapStore.save` → `load` is not total  [Severity: LOW]

- **What:** not a leak — a round-trip defect. An `Edge.label` containing U+0001 makes the written
  `.mmd` unparseable on the way back (`mermaid.ParseError` → `MapStoreError: … ilegible (ParseError)`),
  and U+0085 is silently rewritten to U+0020 by the YAML round trip (measured over 17 code points; the
  other 16 survive).
- **Where:** `mapper/mermaid.py:140-141` / `mapper/store.py:571`.
- **Why it matters:** contained — the operator gets a Spanish denial — but a map the product itself
  wrote can become one the product cannot open. Found while building the F1 transcript.
- **Recommendation:** coerce or reject control characters in `Edge.label` on save; carry as a repair item.

---

## Standard sweep on the new diff

3,635 added lines across 22 files.

| Check | Result |
|---|---|
| Secrets / API keys / tokens / `.env` / SSH or private keys / bearer tokens | **0.** The 9 regex hits are all the English word "token" in prose about `OVERFLOW_TOKEN` / `FOLD_PILL_TOKEN` |
| Emails · URLs · IP addresses | **0 · 0 · 0** |
| Absolute paths / usernames | **1** — `cd C:/Users/jjgh8/…` in an artifact (**F-F**) |
| Destructive filesystem calls (`rm -rf`, `rmtree`, `unlink`, `remove`, `os.system`, `Popen`) | **0 added** |
| New process surface | `subprocess.run(["git", "ls-files", *globs], cwd=REPO, capture_output=True, check=True)` in two test census helpers — fixed argv, no shell, `cwd` pinned. **Acceptable** |
| New network surface | **none** |
| New dependency | **none**; `pyproject.toml` untouched |
| Banned code points in new/modified fixtures, tests and `.dev-flow` artifacts | **0 in this increment's diff.** Whole-repo scan of 224 text files against `darkside.COERCION_RANGES` returns 2 files, both prior-batch artifacts (**F-E**) |
| New fixtures `fixtures/anidado.mmd` / `anidado_nodos.yml` | benign Spanish business nouns; no PII, no credentials, no code points of interest. Note `schema: []` — like every other fixture, it cannot enter the legacy branch |
| LFPDPPP / client-data exposure | none — no client data in the diff, no data leaves the machine |

---

## Verdict

- [ ] OK to ship
- [ ] OK to ship with the listed mitigations applied first
- [x] **Block — must fix HIGH findings before ship**

**Blocking:** **F-A** (1 HIGH). Discharge by either route named under F-A; both include landing the
red arm in this increment.

**Not blocking, recommended in a repair increment:** F-B, F-C, F-D (MEDIUM); F-E, F-F, F-G, F-H (LOW).

**Explicitly discharged and requiring no further work:** `SEC-F1`, `SEC-F2`, the breadcrumb, the
`_branch_coverage_glyph` hang, the three guard placements, and the `A-89` attribute-form derivation.

---

## Evidence checklist

- [x] Each finding has what · where · why · recommendation — F-A through F-H, all four fields present.
- [x] Each finding has a severity rating — 1 HIGH, 3 MEDIUM, 4 LOW.
- [x] No secret values appear in this output — none were found; no value is reproduced.
- [x] No hostile code point is spelled into this file — every payload is named by code point
      (`U+202E`, `0x200b`, …); every probe builds them with `chr(0x…)` at run time.
- [x] Verdict is explicit — **Block**, with the blocking finding named and two discharge routes.
- [x] New tool/integration scope and blast radius addressed — no new MCP/Composio/n8n/network/
      dependency surface; the only new process call is `git ls-files` with fixed argv and no shell.
      The pre-existing OS-handler boundary (`mapper/osopen.py`) was re-read and is sound: kind
      allowlist, scheme allowlist excluding `file:`, userinfo rejection, control-character rejection,
      and workspace confinement checked **before** any launcher runs.
- [x] Tree integrity proven by sha256, not `git status` — 324 of 324 pre-existing files byte-identical;
      21 of 21 mutation restores `OK`; scratch worktree clean at close.

---

*Independent confirmation pass. The prior review's verdict was not read for its conclusions; every
claim above was re-executed in an exported copy. 21 mutants applied, 16 killed, 5 survived (4 real
census gaps + 1 equivalent mutant), 1 produced a hang. Full suite `789 passed, 17 deselected`, slow
lane `17 passed`, both exit 0.*
