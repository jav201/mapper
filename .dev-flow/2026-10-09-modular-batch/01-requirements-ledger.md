# Requirements ledger — mapper — Batch 2026-10-09-modular-batch

> Append-only. Entries are added in chronological order and never rewritten. The live
> contract is `01-requirements.md`; this file records how it came to say what it says.
> Every entry names the requirement it amends; every requirement names its entries. `V26`
> compares the two sets of pairs both ways.

_No entries yet. The first amendment to the live contract writes the first one, in the
shape the field guide's §7 shows (`req-template.md` in the guide directory init prints), and nothing
above this line is ever edited._

### LED-2026-10-09-modular-batch.1 — ARCH-1 / QA-10: MOD-REQ2 spine reorder, the re-export increment map re-labelled
- **Requirement:** LLR-MOD.3.1
- **Date:** 2026-10-09
- **What changed:** LLR-MOD.3.1's increment map re-labelled from `A1–A7` to the MOD-REQ2 order (A1, A2, A3, A5a, B0, A6, A7, A5b, A4, B0 already placed — final spine Inc-0 → A1 → A2 → A3 → A5a → B0 → A6 → A7 → A5b → A4 → B1–B11 → B12). US-001's outcome paths were corrected in the same amendment: `home.py` + `repo.py` live in `mapper/screens/`, NOT in `screens/map/`.
- **Why:** premise 11 measured that the sibling screens construct `MapScreen` (5× `HomeScreen`, 1× `_ImportPreviewScreen`) and never the reverse; with `MapScreen` still in `app.py` their modules would have to import `mapper.app` — the banned `screens → app` edge. After B0 they import it from `mapper.screens.map`.
- **Evidence:** 02-review.md round 1, ARCH-1 and QA-10; 01-requirements.md:156 (premise 11); `git diff e4d58c1 HEAD -- 01-requirements.md` (LLR-MOD.3.1 heading).

### LED-2026-10-09-modular-batch.2 — ARCH-2 / QA-8 / QA-11: the patch surface is eight repointed module-globals; the F4 lazy-read design is dropped
- **Requirement:** HLR-MOD.1, HLR-MOD.3, HLR-MOD.6, LLR-MOD.2.2, LLR-MOD.3.2, LLR-MOD.6.1, LLR-MOD.6.2
- **Date:** 2026-10-09
- **What changed:** premise 4 re-censused over every patch form (dotted-string `setattr`/`patch`, module-object `setattr` via alias, direct attribute assignment) → 8 distinct targets, not 2. HLR-MOD.1, HLR-MOD.3 and LLR-MOD.3.2 rewritten from "two names read lazily through the module object" to "each target is a module-global of the module that reads it, repointed in the increment that moves the reader, with an AST guard against a vacuous repoint". HLR-MOD.6, LLR-MOD.6.1 and LLR-MOD.6.2 delete the sanctioned F4 function-local exception — 0 imports of `mapper.app` under `screens/` in either AST form (`import mapper.app` any alias, `from mapper.app import …`) at any scope. LLR-MOD.2.2 bans importing any of the eight patch names from `mapper.app`. The §6.3 "F4 lazy reads" risk entry is superseded by "Patch repoints"; the §4 F4 row of docs/ARCHITECTURE.md is retargeted to the reading modules.
- **Why:** the F4 lazy read was itself a `screens → app` back-edge, and a re-exported or privately copied name would silently kill the patches while the suite stayed green.
- **Evidence:** 02-review.md round 1, ARCH-2, QA-8 and QA-11; 01-requirements.md:149–150 (premises 4–5); `git diff e4d58c1 HEAD -- docs/ARCHITECTURE.md` (§3 `screens/map` row, §4 F4 row).

### LED-2026-10-09-modular-batch.3 — ARCH-4 / QA-1: AT-065 is a committed TEXT golden with a recorded path, commit and sha256
- **Requirement:** HLR-MOD.4, LLR-MOD.4.2
- **Date:** 2026-10-09
- **What changed:** HLR-MOD.4's acceptance and LLR-MOD.4.2 rewritten from "capture before B0 and after the batch, compare the two" to a committed TEXT golden (not SVG) captured at Inc-0 on the pre-move commit, per scripted-session step at 118 and 87 columns, volatile cells normalised, steps gated on condition waits. The golden paths, capture commit and per-width sha256 are written into LLR-MOD.4.2 as a golden record and asserted by the test. "Golden file missing" is no longer the negative control; a one-token mutation in a tmp copy of the product code reddens the comparison.
- **Why:** an SVG golden needs a renderer the suite does not ship; a missing-golden RED cannot prove the oracle sees a line diff; recording path/commit/sha256 in the contract makes the golden self-verifying against tampering.
- **Evidence:** 02-review.md round 1, ARCH-4 and QA-1; 01-requirements.md HLR-MOD.4 acceptance block and LLR-MOD.4.2 golden record.

### LED-2026-10-09-modular-batch.4 — QA-2 / QA-4 / ARCH-5 / ARCH-6: package-root checkers run on tmp-copy mutants; the mixin `@on`/`DEFAULT_CSS`/`BINDINGS` AST ban; the AST-derived constant roster
- **Requirement:** LLR-MOD.1.3, LLR-MOD.2.1, LLR-MOD.2.2, LLR-MOD.4.1, LLR-MOD.4.3, LLR-MOD.7.1
- **Date:** 2026-10-09
- **What changed:** every structural checker becomes a function taking the package root, run GREEN on the real tree and RED on a tmp-copy mutant — a permanent executable negative control (LLR-MOD.1.3, LLR-MOD.2.1, LLR-MOD.2.2, LLR-MOD.7.1; the same shape recorded for LLR-MOD.1.1/1.2 under entry .6). LLR-MOD.2.1/2.2 add the AST ban on `@on`-decorated handlers, `DEFAULT_CSS` and `BINDINGS` in any `screens/map` mixin (spike rules 1–2: keys silently drop, handlers double-fire), and LLR-MOD.2.1's core-constant roster is derived from the AST of the pre-split `MapScreen` — every class-level assignment incl. `AUTO_FOCUS` and `MINIMAP_ROWS` must appear exactly once across the 12 modules — replacing the hand-written list. LLR-MOD.4.3 is restated as `tests/test_mod_bodies.py`: per-method `ast.dump` against the Inc-0 baseline JSON (no method lost or duplicated by a move) plus an undefined-global check per new module; LLR-MOD.4.1's negative control now names it.
- **Why:** a checker that only ever runs on the real tree has no executable failure side; an idempotent duplicated handler can change no paint, so paint comparison cannot carry that RED; a hand-pinned constant list rots on the first extraction.
- **Evidence:** 02-review.md round 1, QA-2, QA-4, ARCH-5 and ARCH-6; 01-requirements.md LLR-MOD.2.1/LLR-MOD.4.3 negative controls.

### LED-2026-10-09-modular-batch.5 — QA-3 / QA-6 / ARCH-7 / QA-9: every AT owns a node distinct from its LLR node; AT-066 narrowed; AT-067 re-labelled
- **Requirement:** HLR-MOD.2, HLR-MOD.3, HLR-MOD.7
- **Date:** 2026-10-09
- **What changed:** §5.1 Layer B rewritten so each acceptance test owns a `-k` node distinct from every LLR node: AT-065 `-k at065` (LLR `-k parity`), AT-066 `-k at066` (LLR `-k pilot`), AT-067 `-k at067` (LLR `-k patch_guard` + patch-carrying files), AT-068 `-k at068` (`-k spine_a`/`b0`/`spine_b`), AT-069 `-k at069`, AT-070 `-k at070` (`-k b02`), AT-071 `-k at071` (`-k arch`). HLR-MOD.2's AT-066 is narrowed per MOD-REQ2: the B1 hints pilot is the one pilot-driven dispatch test, and the duplicated-`on_*` RED is credited to the white-box disjointness guard because an idempotent handler may change no paint. HLR-MOD.3's AT-067 is re-labelled the patch-surface contract AT over all eight targets. HLR-MOD.7 gains its own behavioural node AT-071.
- **Why:** an AT sharing a node with its LLR is not an independent acceptance layer; a paint-based RED cannot catch a double-fired idempotent handler.
- **Evidence:** 02-review.md round 1, QA-3, QA-6, ARCH-7 and QA-9; 01-requirements.md §5.1 Layer B and the HLR-MOD.2/3/7 acceptance blocks.

### LED-2026-10-09-modular-batch.6 — ARCH-1 / QA-3 / QA-4: the MOD-REQ2 reorder lands in the structure requirements; the dep statements follow the any-scope ban
- **Requirement:** HLR-MOD.6, LLR-MOD.1.1, LLR-MOD.1.2
- **Date:** 2026-10-09
- **What changed:** LLR-MOD.1.1 re-sequenced to the MOD-REQ2 spine with per-increment owners — A1 common, A2 prompt, A3 construct, A5a `screens/map/navigation.py` (`NavigationModel` only, before B0 because `MapScreen` itself reads it), B0 the wholesale `MapScreen` move, A6 plug_repo, A7 import_preview, A5b repo, A4 home last — and the rule that the sibling screens import `MapScreen` from `mapper.screens.map`, never from `mapper.app`. LLR-MOD.1.1/1.2's negative controls become package-root checkers run on tmp-copy mutants. HLR-MOD.6's statement, observable and threshold drop the F4 exception (either import form, any scope; the empty set is the boundary) and AT-070 becomes its own node distinct from LLR-MOD.6.1's `-k b02`.
- **Why:** premise 11 — the sibling screens construct `MapScreen`, never the reverse — so they can only land after B0 without re-creating the banned `screens → app` edge.
- **Evidence:** 02-review.md round 1, ARCH-1, QA-3 and QA-4; 01-requirements.md:156 (premise 11); `git diff e4d58c1 HEAD -- docs/ARCHITECTURE.md` (§6 order constraints, A4 last of the siblings).

### LED-2026-10-09-modular-batch.7 — QA-5: the F1/F2 census oracle moves under the batch's spike/ directory
- **Requirement:** LLR-MOD.7.2
- **Date:** 2026-10-09
- **What changed:** the census oracle path changes from `census/ast_census.py` diffed against `census.json` to `.dev-flow/2026-10-09-modular-batch/spike/ast_census.py` diffed against the committed `.dev-flow/2026-10-09-modular-batch/spike/census.json`; the §2.5 census bullet is re-pointed the same way (LLR-MOD.7.2 named). The census checker's negative control runs on a tmp-copy mutant — a package-root checker run GREEN on the real tree and RED on the mutant.
- **Why:** the census is the batch's evidence, not a shipped package directory; a committed baseline JSON makes the B12 re-run a mechanical diff and keeps the F1/F2 freeze enforceable without a test edit.
- **Evidence:** 02-review.md round 1, QA-5; 01-requirements.md §2.5 and LLR-MOD.7.2; `.dev-flow/2026-10-09-modular-batch/spike/`.

### LED-2026-10-09-modular-batch.8 — ARCH-3 / QA-7: today's assertion counts are recorded as the no-weaker baseline; test_keymap's scanned module set is derived
- **Requirement:** HLR-MOD.5, LLR-MOD.5.1
- **Date:** 2026-10-09
- **What changed:** HLR-MOD.5's threshold now pins per-file AST assertion-count baselines measured 2026-10-09 — `test_draft_hygiene.py` ≥ 9, `test_darkside_census.py` ≥ 55, `test_keymap.py` ≥ 35, `test_en5.py` ≥ 34, `test_en7.py` ≥ 37, `test_app_imports_used.py` ≥ 2 — recorded as the AT-069 baseline before Inc-0, replacing the unmeasurable "assertion counts ≥ today's". LLR-MOD.5.1 adds that `test_keymap.py`'s scanned module set is derived by `pkgutil.walk_packages` over `mapper` (its hand-pinned list at :214–220 must be gone) so every new module is scanned without a test edit.
- **Why:** "no weaker than today" is unenforceable without a recorded today; a hand-pinned module list rots the first time a new module appears.
- **Evidence:** 02-review.md round 1, ARCH-3 and QA-7; `git diff e4d58c1 HEAD -- 01-requirements.md` (HLR-MOD.5 numeric pass threshold, LLR-MOD.5.1 statement).

### LED-2026-10-09-modular-batch.9 — ARCH-8, ARCH-9, ARCH-10, ARCH-11, QA N-1, N-2: round-2 spine and pinning fixes
- **Requirement:** HLR-MOD.3, LLR-MOD.1.1, LLR-MOD.1.3, LLR-MOD.3.1, LLR-MOD.3.2, LLR-MOD.4.2, LLR-MOD.4.3, LLR-MOD.7.2
- **Date:** 2026-10-09
- **What changed:** ARCH-8 — `MapHintLine` (app.py:165) moves at A1 into `screens/common.py` with the other hint helpers, so B0's `screens/map/screen.py` never imports it from `mapper.app`: LLR-MOD.1.1 gains the A1 ownership, LLR-MOD.1.3 drops "`hints.py` also owning `MapHintLine`". ARCH-9 — `PlugRepoScreen` pushes `RepoScreen` (app.py:1207), so the spine is re-ordered A1 → A2 → A3 → A5a → B0 → A5b repo → A6 plug_repo → A7 import_preview → A4 home in §1.3 (spine), §2.8, US-001, the §4 LLR map and the LLR-MOD.1.1/LLR-MOD.3.1 titles; LLR-MOD.1.1 adds that `screens/plug_repo.py` imports `RepoScreen` from `mapper.screens.repo`, never `MapScreen`. ARCH-10 — premise 4 and LLR-MOD.3.2 now name the reading module for every patch site (`LayeredRenderer` patched at test_en8.py:332 is read through the CSV-import path → `screens/import_preview.py`, not panning/render; `refusal_sentence` → `screens/common.py`; `save_svg` → `screens/map/exporting.py`; `pan_extent` → `screens/map/panning.py`; `preview_csv` → `screens/import_preview.py`; `MAX_RENDER_NODES`/`SearchIndex` → `screens/map/searching.py`), and HLR-MOD.3/LLR-MOD.3.2's AST guard must check the reader of each patch site, not merely that some module binds the name. ARCH-11 — premise 4, HLR-MOD.3 and LLR-MOD.3.2 reclassify `mapper.app.GitHubConnector.fetch` (test_app.py:22, test_inc9.py:151, test_inc9c.py:488) as a class-attribute patch on the shared class object: it survives the move, no repoint; the module-global repoint set is the other seven names (§1.3's patch-surface definition follows). QA N-1 — LLR-MOD.4.3's baseline JSON is pinned to `.dev-flow/2026-10-09-modular-batch/evidence/mod-bodies-baseline.json` with its sha256 recorded in the Inc-0 packet. QA N-2 — LLR-MOD.4.2's `<recorded at Inc-0 capture>` placeholders become "recorded in the Inc-0 increment packet (`03-increments/increment-001.md`)"; no `<…>` left in the contract. QA-5 — §2.5 and LLR-MOD.7.2 state that `.dev-flow/2026-10-09-modular-batch/spike/` is the archive location the census guard reads.
- **Why:** round 2 of 02-review found B0's `screen.py` would import `MapHintLine` from `mapper.app` (a banned back-edge) if it stayed in `hints.py`/B1; `PlugRepoScreen` constructing `RepoScreen` forces repo before plug_repo; a repoint guard keyed on name binding alone could pass a vacuous repoint to a non-reading module; a class-attribute patch cannot be repointed and must not be counted among the module-global repoints; and the golden/baseline/census evidence needs pinned paths and packet-recorded digests before Inc-0.
- **Evidence:** 02-review.md round 2.
