# Requirements Document — mapper — Batch 2026-10-09-modular-batch

> **Artifact language**
> This template is the canonical **English scaffold**. Generate the artifact in the batch's development language (`state.json` `language`). For Spanish batches, translate the **prose** — section headers and guidance — **and never a label**, and use `deberá` as the normative keyword (≡ `shall`). The normative RULES in this preamble are **language-independent** and enforced regardless of artifact language.

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/docs/req-template.md` explains each field below and the rules that read them. It ships with the flow and is not copied into this batch.

> **Reserved field names.** The **field names and block keywords below are language-independent** — the validator parses them literally and they are never translated:
> `Validation` · `Acceptance test(s)` · `Boundary catalog` · `Negative control` · `Premise evaluation` · `Fork preconditions` · `Ledger` · `Requirement` · `⏸ DEFER`
> Everything else on this page — headings, guidance, the prose in every cell — is translated with the batch.
> **One strategy, not two:** the flow ships no alias table, so a translated label is read as an ABSENT one and the rule keyed on it reports a true-sounding silence.
> **And one FLOW-WIDE reserved token, read out of this artifact by `V42` no matter which template minted it:** `⏸ DEFER`. It is a MARKER rather than a field name, which is why it is stated here *and* in `/dev-flow` §Language of artifacts rather than in a per-template list — a deferral can be written in any batch artifact, including the ones that carry no block at all.

---

## 1. Introduction

### 1.1 Purpose
Modularise `mapper/app.py` (5255 lines, R-009 re-opened) so that later batches can run
parallel product lanes. The operator's words, verbatim: «Ok, tenemos que modularizar para
poder paralelizar el trabajo, eso es primordial.» The batch is behaviour-preserving: no
user of the app observes any change.

### 1.2 Scope
In scope:
- the split of `mapper/app.py` per the ARQ target map: seven sibling-screen modules under
  `mapper/screens/`, the `mapper/screens/map/` package with one concern module per
  MapScreen concern, and `mapper/app.py` reduced to `MapperApp` + `main` + `CSS` +
  re-exports (the eight patch-surface names move to their reading modules, LLR-MOD.3.2);
- the closure of B-02 (the four cycle-dodging function-local imports);
- the generalisation of the six source-reading test files to scan the package (Inc-0);
- guard tests that freeze the F1–F5 interfaces of `docs/ARCHITECTURE.md` §4.

Out of scope:
- any user-visible change (strings, keys, colours, layout);
- the parallel product lanes themselves — they are the **output** of this batch, and they
  fork only after Inc-B11;
- performance (B-33, next batch) and the dev-flow audit tool (separate prototype round).

### 1.3 Definitions, acronyms, abbreviations
| Term | Definition |
|------|------------|
| concern | one of the 12 disjoint method partitions of `MapScreen` (core + 11 concerns) from the census |
| mechanism A | one plain mixin class per concern, composed into `MapScreen(PaintingOps, …, Screen)`; methods use `self.` exactly as today |
| core class | `MapScreen` in `mapper/screens/map/screen.py`: lifecycle concern, all class constants, `BINDINGS`, `__init__` with the 30 attribute slots |
| F1–F5 | the frozen interfaces of `docs/ARCHITECTURE.md` §4: state roster, cross-concern method surface, core class surface, patch surface, app↔screen surface |
| patch surface | the eight names the test suite monkeypatches on the `mapper.app` module object today (premise 4: `MAX_RENDER_NODES`, `refusal_sentence`, `save_svg`, `pan_extent`, `LayeredRenderer`, `preview_csv`, `SearchIndex`, `GitHubConnector`), seven of them repointed in the increment that moves their reader to the module-global of the module that reads the name (LLR-MOD.3.2); `GitHubConnector.fetch` is a class-attribute patch on the shared class object — it survives the move, no repoint (ARCH-11) |
| spine | the serial extraction sequence Inc-0 → A1 (common) → A2 (prompt) → A3 (construct) → A5a (`screens/map/navigation.py`, `NavigationModel` only) → B0 (`MapScreen` wholesale) → A5b (repo) → A6 (plug_repo) → A7 (import_preview) → A4 (home) → B1–B11 → B12; every increment that deletes lines from `app.py`/`screen.py` collides with every other on that file |
| product lane | a post-batch unit of feature work that edits exactly one concern module file |

### 1.4 References
- `.dev-flow/2026-10-09-modular-batch/PLAN.md` (objective, P0 measurements, triggers, risks).
- `.dev-flow/2026-10-09-modular-batch/spike/arq-proposal-kimi-k3.md` (target map §1, mechanism A §2, F1–F5 §3, dependency rules §4, compatibility §5, increment cut §6, risks §7).
- `.dev-flow/2026-10-09-modular-batch/evidence/arq-mro-spike.transcript` (BINDINGS/on_* spike rules, measured on Textual 8.2.8).
- `docs/ARCHITECTURE.md` §2 (amended `screens` / `map screen` / `app` rows), §3 (amended `screens/map`, `screens/common` + `screens/prompt`, `osopen` rules), §4 (F1–F5), §6 (batch worksheet).
- `.dev-flow/BACKLOG.md` B-02 (closed by this batch), R-009 (re-opened by this batch).

### 1.5 Document overview
- §2: stories, premises, fork preconditions.
- §3: HLR, with their acceptance tests.
- §4: LLR (mapped to the increment cut) and the IFC.
- §5: validation strategy.
- §6: design decisions and open risks.

---

## 2. Overall description

### 2.1 Product perspective
`mapper/app.py` is the orchestration root of the TUI and, at 5255 lines, the single file
every feature increment collides on. This batch moves code between files only: every moved
name keeps a re-export in `mapper/app.py`, so the 68 importing test files and the runtime
imports see the identical module object graph. `docs/ARCHITECTURE.md` has already been
amended with the TARGET rows; the batch lands the code that makes the map true.

### 2.2 Product functions
No new function. What changes is the repository layout: one concern of `MapScreen` per
module file, so two workers changing different features never edit the same file.

### 2.3 User characteristics
- The **maintainer**, who edits one feature by editing its own module file only.
- The **operator**, who sees no change at all in the app.
- The **worker/orchestrator pair**, whose safety net is that existing tests keep importing
  and patching what they import and patch today.

### 2.4 Constraints
- **Behaviour-preserving.** No string, key, colour or layout change. A TUI design change
  would need a prototype verdict, and none is wanted here.
- **Platform.** Python 3.11/3.12, Textual 8.2.8 (spike rules in §2.7 premise 8 are
  version-specific and re-measured if the version moves).
- **Increment size.** At most 4 source files per increment; the extraction spine is serial
  (ARCHITECTURE §6 rule: `modules(A) ∩ modules(B) = ∅` at file granularity).
- No operator paths, no Windows user names in any file.
- Colours from `mapper/darkside.py` tokens; keys from `mapper/keymap.py`; no hard-coded
  glyphs or hex.

### 2.5 Assumptions and dependencies
- The MRO spike rules of premise 8 hold on the shipped Textual version (BINDINGS in a
  plain mixin are silently not merged; `on_*` handlers run from every MRO class that
  defines them). If a later Textual upgrade changes them, HLR-MOD.2's guard test reddens
  and the batch re-baselines the spike evidence first.
- The census (spike §3 freeze) is the F1/F2 oracle; the batch's archived census at
  `.dev-flow/2026-10-09-modular-batch/spike/` — the archive location the census guard reads —
  re-runs over the package at B12 (LLR-MOD.7.2).
- All 70 sites that import `mapper.app` (premise 2) are covered by re-exports (LLR-MOD.3.1).

### 2.6 Source user stories

| ID | User Story | Source | DoR status |
|----|------------|--------|------------|
| US-001 | As the maintainer, I want to change one feature by editing its own module file only — two workers never share a file after the split — so that feature work can run in parallel lanes. | Operator 2026-10-09 («…para poder paralelizar el trabajo, eso es primordial»); ARCHITECTURE R-009 re-open condition met | READY |
| US-002 | As the operator, I want to see no change at all in the app, so that a structural refactor never costs a behaviour regression. | PLAN objective 2 (behaviour-preserving) | READY |
| US-003 | As the maintainer, I want the existing tests to keep importing and patching what they import and patch today, with source-reading tests scanning the package, so that the move is invisible to the suite and its pins never rot silently. | PLAN triggers B1 (68 importing test files, 17 source-reading, 2 monkeypatch targets) | READY |

#### Refinement log (one block per story)

**US-001 — one feature, one file**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = maintainer · outcome = after the split, `mapper/screens/map/searching.py`, `editing.py`, `painting.py`, `exporting.py`, `drafts.py`, … are disjoint files, and `mapper/screens/home.py` + `mapper/screens/repo.py` are disjoint files beside them (both live in `mapper/screens/`, NOT in `screens/map/`); a search feature touches only `searching.py` · why = the operator's "primordial" · out of scope = the post-B11 lanes themselves.
- **Feasibility (E, S):** implementation path = mechanism A (spike §2), increments Inc-0, A1, A2, A3, A5a, B0, A5b, A6, A7, A4, B1–B11, B12 per spike §6 (the MOD-REQ2 reorder: the sibling screens that construct `MapScreen` move after B0 and import it from `mapper.screens.map` — never from `mapper.app`; `PlugRepoScreen` pushes `RepoScreen`, so A5b repo lands before A6 plug_repo) · dependencies = the F1–F5 freeze (PDR) · fits one batch? = yes — the spine is serial but each increment is ≤ 4 source files.
- **Evaluability (T) — behavioral, black-box:** "When the maintainer lists the repository tree after the batch, each MapScreen concern is a module file of its own, and the guard test reads those files from the tree." The repository tree is the shipped surface.
- **Open questions:** none.
- **Classification:** `READY`.

**US-002 — the app does not change**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** outcome = every painted outcome equals the pre-split capture; the full suite passes · out of scope = performance, any design change.
- **Feasibility (E, S):** implementation path = byte-identical method bodies (cut/paste, AST-dump compared per increment), full suite at every increment gate, painted-capture parity AT.
- **Evaluability (T) — behavioral, black-box:** "When the operator opens a map, moves, searches, toggles a view, exports and quits at 118 and 87 columns, every painted line equals the pre-split capture." The shipped surface is the painted screen.
- **Open questions:** none.
- **Classification:** `READY`.

**US-003 — the suite sees nothing**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** outcome = all 70 `from mapper.app import` sites keep resolving; the eight patch targets of premise 4 still bite, each through its repointed module-global in the module that reads the name; the 17 source-reading tests scan the package with pins no weaker than today's baselines (AT-069 pins) · out of scope = rewriting test behaviour assertions.
- **Feasibility (E, S):** implementation path = permanent re-export block in `app.py` (LLR-MOD.3.1), patch repoints (LLR-MOD.3.2), Inc-0 generalisation of the six test files before any move.
- **Evaluability (T) — behavioral, black-box:** "When the maintainer runs the suite after any increment, it passes with zero failures and no test file was edited to weaken an assertion."
- **Open questions:** none.
- **Classification:** `READY`.

### 2.7 Premise evaluation (C-43) — MANDATORY, one row per premise

| # | Premise, as a truth-apt proposition | Tier | Verdict | Executed evidence (command output / `file:line` — **NOT** a citation of another document) | Disposition |
|---|---|---|---|---|---|
| 1 | `mapper/app.py` is 5255 lines; `MapScreen` starts at line 1536 and `MapperApp` follows at 4990 | executed | ✅ TRUE | `wc -l mapper/app.py` → `5255 mapper/app.py`; `grep -n "^class MapScreen\|^class MapperApp\|^def main" mapper/app.py` → `1536:class MapScreen(Screen):`, `4990:class MapperApp(App):`, `5239:def main() -> None:` | in scope (HLR-MOD.1, LLR-MOD.1.1–1.3) |
| 2 | 68 test files import `from mapper.app import …`, and two `mapper/` modules also do | executed | ✅ TRUE | `grep -rl "from mapper.app import" tests \| wc -l` → `68`; `grep -rl "from mapper.app import" mapper` → `mapper/screens/factory.py`, `mapper/screens/settings.py` | in scope (HLR-MOD.3, LLR-MOD.3.1) |
| 3 | 17 test files read `app.py`'s source (AST, path pins, `inspect.getsource`) | executed | ✅ TRUE | `grep -rln 'app\.py"\|app\.__file__\|inspect\.getsource' tests \| wc -l` → `17` (lists `test_app_imports_used.py`, `test_darkside_census.py`, `test_draft_hygiene.py`, `test_en5.py`, `test_en7.py`, `test_search.py`, …) | in scope (HLR-MOD.5, LLR-MOD.5.1) |
| 4 | The test suite patches **8 distinct names** on the `mapper.app` module object — not 2 — each with a named reading module: `MAX_RENDER_NODES` ×5 is read by the search/count concern (`screens/map/searching.py`); `refusal_sentence` ×1 by `_path_refusal` (A1 → `screens/common.py`); `save_svg` ×3 by the exporting concern (`screens/map/exporting.py`); `pan_extent` ×1 by the panning concern (`screens/map/panning.py`); `LayeredRenderer` ×1 (test_en8.py:332) through the CSV-import path (`screens/import_preview.py`, NOT panning/render); `preview_csv` ×2 by `screens/import_preview.py`; `SearchIndex` ×1 (direct attribute assignment) by `screens/map/searching.py`; `GitHubConnector.fetch` ×4 (dotted path) is a **class attribute patched on the shared class object — it survives the move, no repoint** — so the module-global repoint set is the other **seven** names | executed | ✅ TRUE | full census over every patch form (dotted-string `setattr`/`patch`, module-object `setattr` with a `mapper.app` alias, direct attribute assignment on the alias), file-prefixed: `grep -Hn "monkeypatch.setattr" tests/test_search.py \| grep MAX_RENDER_NODES` → `tests/test_search.py:2393`, `:2456`, `:2549`, `:2649`, `:2690` (all `monkeypatch.setattr(app_module, "MAX_RENDER_NODES", …)`); `grep -Hn "setattr(app_module, \"refusal" tests/test_inc9q.py` → `tests/test_inc9q.py:393`; `grep -Hn "mapper.app.save_svg" tests/test_app.py tests/test_inc9c.py` → `tests/test_app.py:371`, `tests/test_app.py:475`, `tests/test_inc9c.py:134`; `grep -Hn "mapper.app.pan_extent\|mapper.app.LayeredRenderer" tests/test_en8.py` → `tests/test_en8.py:66`, `tests/test_en8.py:332`; `grep -Hn "mapper.app.preview_csv" tests/test_inc9c.py tests/test_inc9n.py` → `tests/test_inc9c.py:114`, `tests/test_inc9n.py:285`; `grep -Hn "mapper.app.GitHubConnector.fetch" tests/*.py` → `tests/test_app.py:22`, `tests/test_app.py:110`, `tests/test_inc9.py:151`, `tests/test_inc9c.py:488`; `grep -Hn "app_module.SearchIndex =" tests/test_search.py` → `tests/test_search.py:1404` (restored at `:1428`) | in scope (HLR-MOD.3, LLR-MOD.3.2) — the repoint premise |
| 5 | Both patch names are bound at `app.py` module level today (as re-exported imports) | executed | ✅ TRUE | `grep -n "refusal_sentence" mapper/app.py` → `49: ATTACHMENT_HARD_LINKED, OK as OSOPEN_OK, PATH_NOT_SUPPORTED, confine_reason, open_external, refusal_sentence,`; `grep -n "MAX_RENDER_NODES" mapper/app.py` → `58: MAX_RENDER_NODES,` | in scope — today's binding site only; the F4 call-time lazy-read design is REPLACED by the repoint policy (LED-2026-10-09-modular-batch.2) |
| 6 | The four B-02 cycle-dodging function-local imports exist where ARCHITECTURE §3 records them | executed | ✅ TRUE | `grep -n "    import" mapper/screens/factory.py mapper/screens/settings.py \| grep mapper` → factory: `from mapper.app import keybar_groups` (≈:198), `from mapper.app import _save_or_toast` (≈:217), `from mapper.app import _PromptScreen` (≈:507); settings: `from mapper.app import keybar_groups` (≈:89) | in scope (HLR-MOD.6, LLR-MOD.6.1) |
| 7 | `mapper/screens/map/` does not exist yet | executed | ✅ TRUE | `ls mapper/screens/map` → `ls: cannot access 'mapper/screens/map': No such file or directory` | in scope (LLR-MOD.1.2 is the commitment that creates it) |
| 8 | On Textual 8.2.8: BINDINGS declared in a plain mixin are NOT merged; a core binding dispatches to a mixin action; `on_*` handlers run from every MRO class that defines them | executed (spike) | ✅ TRUE | `evidence/arq-mro-spike.transcript`: `screen bindings ['ctrl+c', 'shift+tab', 'super+c', 'tab', 'y']` (mixin-declared `x` absent); `log ['on_mount(mixin)', 'on_mount(mixin2)', …]`; `['ctrl+c', …, 'z']` with `z` → `action_from_mixin` | in scope (HLR-MOD.2, LLR-MOD.2.1, LLR-MOD.2.2) |
| 9 | The runtime is Python 3.12.7 with textual 8.2.8 | executed | ✅ TRUE | `python -c "import textual; print(textual.__version__)"` → `8.2.8`; `python --version` → `Python 3.12.7` | constraint (§2.4) |
| 10 | Tests plus `screens/factory.py` import 21 distinct names from `mapper.app` | executed | ✅ TRUE | AST/join-continuation census over `tests/**/*.py` + `mapper/screens/factory.py` → `21`: `COUNT_REGION_ID ConstructScreen GitHubConnector HomeScreen MapScreen MapperApp NavigationModel PAN_INERT_HINT PlugRepoScreen RepoScreen SEARCH_ACTIVE_LABEL SEARCH_COUNT_SUBJECT SEARCH_SUSPENDED_NOTICE _ConfirmScreen _FichaScreen _ImportPreviewScreen _PromptScreen _QUERY_ECHO_CELLS _save_or_toast keybar_groups map_hint` | in scope (LLR-MOD.3.1) |
| 11 | `MapScreen` (app.py:1536–4989) references none of `HomeScreen`, `RepoScreen`, `PlugRepoScreen`, `_ImportPreviewScreen`; those classes construct `MapScreen` (5× in `HomeScreen`, 1× in `_ImportPreviewScreen`), never the reverse | executed | ✅ TRUE | `sed -n '1536,4989p' mapper/app.py \| grep -c "HomeScreen\|RepoScreen\|PlugRepoScreen\|_ImportPreviewScreen"` → `0`; `grep -n "MapScreen(" mapper/app.py` → `1004`, `1023`, `1032`, `1052`, `1108` (all in `HomeScreen`), `1170` (`_ImportPreviewScreen`), `3810` (`MapScreen` itself, a linked map) | in scope (the MOD-REQ2 spine reorder: the sibling screens that construct `MapScreen` move after B0 and import it from `mapper.screens.map`) |

- **Premise evaluation:** 11 premise(s) · 11 ✅ TRUE / 0 ❌ FALSE / 0 ❓ UNDECIDABLE

### 2.8 Fork preconditions (C-52) — MANDATORY, and the declared empty when the batch does not fork

The batch forks **only after Inc-B11**; during the batch the spine (Inc-0 → A1 → A2 → A3 → A5a → B0 → A5b → A6 → A7 → A4 → B1–B11 → B12) is
**serial**, because every increment that deletes lines from
`app.py`/`screen.py` collides with every other on that file (ARCHITECTURE §6). The MOD-REQ2
reorder puts B0 (the wholesale `MapScreen` move) before A4–A7: `HomeScreen`
(`mapper/app.py:1004,1023,1032,1052,1108`) and `_ImportPreviewScreen` (`:1170`) construct
`MapScreen`, and with it still in `app.py` their modules would have to import `mapper.app` —
the banned edge (premise 11 shows the dependency runs one way only). After B0 they import
`MapScreen` from `mapper.screens.map`. `A5a` (`screens/map/navigation.py`, `NavigationModel`
only) lands before B0 because `MapScreen` itself reads `NavigationModel`. Parallel
product lanes are the **output** of this batch, not its method. The only in-batch
parallelism is Inc-0: six mutually disjoint test-only files, as parallel sub-lanes.

| # | Condition (`C-52`) | Discharged? | The executed evidence |
|---|---|---|---|
| 1 | **Frozen contract** — no shared interface is touched inside a lane; one that must change returns to the trunk (trigger A3) | ✅ | in-batch: the F1–F5 freeze of ARCHITECTURE §4, sealed at the PDR, is the frozen contract; post-B11 lanes consume it read-only and each lane owns exactly one concern module |
| 2 | **Disjoint FILE sets**, not just modules | ✅ | the ARQ target map (spike §1) assigns every file exactly one owner; premise 7 confirms the map package is greenfield; per-lane file sets are singletons, intersection test trivially empty |
| 3 | **Crossed reverse census** — family B run per lane and shared before starting | ✅ | the F2 cross-concern method surface (ARCHITECTURE §4) is the reverse census, frozen and made mechanical by the B12 census-diff test (LLR-MOD.7.2); LLR-MOD.2.2's disjoint-names guard runs at every spine gate |
| 4 | **One owner of the trunk** — requirements, traceability, backlog and spec are never written from a lane | ✅ | the orchestrator (trunk); this document and `docs/ARCHITECTURE.md` are written only on the trunk |

- **Fork preconditions:** 0 lane(s) during the batch — the spine is serial; the batch's deliverable is the fork: parallel product lanes become legal only after Inc-B11, when the concern modules exist as disjoint files.

---

## 3. High-level requirements (HLR)

### HLR-MOD.1 — the target module map is real
- **Traceability:** US-001
- **Ledger:** LED-2026-10-09-modular-batch.2
- **Statement:** When the batch completes, the repository shall hold the ARQ target map: seven sibling-screen modules under `mapper/screens/` (`common`, `prompt`, `construct`, `home`, `repo`, `plug_repo`, `import_preview`), the `mapper/screens/map/` package with one concern module per MapScreen concern plus a re-export-only `__init__.py`, and `mapper/app.py` reduced to `MapperApp`, `main`, the `CSS` block and the re-exports (the patch-surface names live in their reading modules, LLR-MOD.3.2).
- **Rationale (informative):** a map that lies is worse than one that is stale (ARCHITECTURE staleness rule); the TARGET rows are already amended, so the code is the only missing half. Disjoint files are the operator's precondition for parallel lanes.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_structure.py`
- **Numeric pass threshold:** exit code 0; 20 expected files present and owning their names; `mapper/app.py` ≤ 400 lines and holding no `Screen` subclass other than `MapperApp`.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** the repository tree shows `mapper/screens/map/painting.py`, `searching.py`, `panning.py`, `hints.py`, `navigation.py`, `drafts.py`, `editing.py`, `undo.py`, `focus_mode.py`, `opening.py`, `exporting.py` and `screen.py`, and `mapper/app.py` is ~350 lines.
  - **Shipped surface:** the repository tree itself — the story's surface is the set of files a maintainer edits.
  - **Acceptance test(s):** AT-068
  - **Boundary catalog (QC-3):** ☐ empty ☑ boundary — `screen.py` holds exactly the lifecycle concern plus constants; `__init__.py` holds re-export only; `app.py` at the ~350-line boundary ☐ invalid ☑ error — a MapScreen concern method found in the wrong module, or a `Screen` subclass left in `app.py`.
  - **Negative control:** AT-068 is RED on today's tree (premise 7: `mapper/screens/map/` does not exist) and stays RED if any concern method is found in a module other than its own. Executed at Phase 3.

### HLR-MOD.2 — Textual dispatch is preserved through the mixins
- **Traceability:** US-002
- **Ledger:** LED-2026-10-09-modular-batch.5
- **Statement:** When a key chord or action reaches the map screen, the system shall dispatch it exactly as before the split: `BINDINGS` and every class constant live only on the core `MapScreen` class, `action_*` and `on_*` handlers resolve through the mixin bases, and method names are pairwise-disjoint across the twelve map modules.
- **Rationale (informative):** the spike (premise 8) measured that BINDINGS in a mixin are silently not merged and that an `on_*` name in two MRO classes runs twice; both failure modes are silent, so both need executable guards.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_dispatch.py`
- **Numeric pass threshold:** exit code 0; BINDINGS found in exactly 1 class (the core); 0 pairwise method-name collisions across the 12 modules; 0 mixin-declared core class constants.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** every bound key and every painted hint on the map screen behaves identically to the pre-split capture, including keys whose `action_*` now lives in a mixin.
  - **Shipped surface:** the map screen driven with real keys through `MapperApp` + `app.run_test(...)` + `pilot.press(...)`.
  - **Acceptance test(s):** AT-066 (narrowed per MOD-REQ2): the B1 hints pilot is the one pilot-driven dispatch test; for the later mixins, dispatch preservation rides on the white-box guards (LLR-MOD.2.1/2.2 — disjoint names, `BINDINGS`/constants on the core, no `@on`/`DEFAULT_CSS` in a mixin) plus the AT-065 painted capture across the scripted session.
  - **Boundary catalog (QC-3):** ☑ empty — the hints mixin owns 0 shared attributes (B1 spike), so an empty-dependency dispatch is exercised first ☐ invalid ☑ error — a duplicated handler name would fire twice; a mixin `BINDINGS` would silently drop keys.
  - **Negative control:** the duplicated-`on_*` RED is credited to the white-box disjointness guard (LLR-MOD.2.2), which asserts the handler's call count directly — an idempotent handler may change no paint, so paint comparison cannot carry that RED; `BINDINGS` moved off the core class REDs AT-066/LLR-MOD.2.1 by injected mutation. Executed at Phase 3.

### HLR-MOD.3 — imports and monkeypatches through `mapper.app` keep biting
- **Traceability:** US-003
- **Ledger:** LED-2026-10-09-modular-batch.2, LED-2026-10-09-modular-batch.5, LED-2026-10-09-modular-batch.9
- **Statement:** When an existing test imports a moved name from `mapper.app` or monkeypatches one of the eight patch targets of premise 4, the import shall resolve and the patch shall change behaviour exactly as today, with every module-global patch site repointed to the module-global of the module that reads the name (the reader of that patch site), in the same increment that moves the reader (the F4 call-time lazy-read design is dropped); `GitHubConnector.fetch` is a class-attribute patch on the shared class object and survives the move with no repoint (ARCH-11), leaving seven module-global repoints.
- **Rationale (informative):** a moved module that imported its patch name from `mapper.app` would re-create the banned `screens → app` edge; a module that bound a private copy would silently kill the patches. The repoint keeps the same name, same value, in the module where the name is read — and a guard test proves the target module actually reads it, so a vacuous repoint cannot pass.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_compat.py tests/test_search.py tests/test_inc9q.py tests/test_en8.py tests/test_app.py tests/test_inc9c.py tests/test_inc9n.py tests/test_inc9.py`
- **Numeric pass threshold:** exit code 0; all 21 imported names (premise 10) resolve from `mapper.app`; the 7 module-global patch targets bite through their repointed module-globals (premise 4's site counts per file), and the `GitHubConnector.fetch` class-attribute patch bites through the moved class; the patch-site guard test passes — for every patch site in `tests/`, the site is repointed to the module that actually reads the patched name (the reader of that patch site, not merely a module that binds it); 0 imports of any patch name from `mapper.app` into a `screens/` module (any form, any scope).
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** with `MAX_RENDER_NODES` patched below the map size, the search refusal paints at the patched limit; with `refusal_sentence` patched, the refusal text shows the patch's marker — in both cases through the shipped screens and the repointed module-global.
  - **Shipped surface:** the map screen's search/count line and the path-refusal toast.
  - **Acceptance test(s):** AT-067 — the patch-surface contract AT: the eight targets of premise 4 are module-globals of their reading modules, the suite's patch sites are repointed to them, and the patched refusal/limit is observed through the shipped screens.
  - **Boundary catalog (QC-3):** ☐ empty ☑ boundary — the patched limit one node below the map size (exactly the shipped patch call shapes) ☐ invalid ☑ error — an import of a patch name from `mapper.app` into its reading module (the old F4 shape, any form).
  - **Negative control:** RED when one repoint is skipped (the patch stops biting while the rest of the suite passes — the silent-failure mode), and RED when a patch site's target module does not bind or read the name (the guard test). Executed at Phase 3.

### HLR-MOD.4 — the app does not change
- **Traceability:** US-002
- **Ledger:** LED-2026-10-09-modular-batch.3
- **Statement:** When any extraction increment of the batch lands, the system's observable behaviour shall equal the pre-split capture, evidenced by a zero-failure full test suite and byte-equal painted output at terminal widths 118 and 87 columns.
- **Rationale (informative):** 3454 lines move; the only honest oracle for "no behaviour change" on a TUI is painted-output comparison over real keystrokes, plus the full suite at every increment gate.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_parity.py` and the full suite `python -B -m pytest -q -p no:cacheprovider tests/` at P4.
- **Numeric pass threshold:** exit code 0 for both; 0 painted-line diffs across the scripted session (open a map, move, search, toggle a view, export, quit) at both widths.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** every line the operator can see during the scripted session equals the pre-split capture, at both 118 and 87 columns.
  - **Shipped surface:** the painted screen of the real app (`MapperApp(tmp_path)` driven with real keys; helpers reused from `tests/test_draft_save.py`).
  - **Acceptance test(s):** AT-065 — a committed TEXT golden (not SVG), captured on the pre-move commit after each step of the scripted session at 118 and 87 columns; the requirement records the golden path, the capture commit and its sha256.
  - **Boundary catalog (QC-3):** ☐ empty ☑ boundary — the two widths (wide 118 and narrow 87) exercise truncation and wrapping paths differently ☐ invalid ☑ error — a changed hint string, key label or layout cell.
  - **Negative control:** a mutated-copy RED — a one-token change to a painted string in a tmp copy of the product module reddens the comparison (as does a deliberately wrong golden line); "golden file missing" is NOT the negative control. Executed at Phase 3.

### HLR-MOD.5 — source-reading tests scan the package without weakening
- **Traceability:** US-003
- **Ledger:** LED-2026-10-09-modular-batch.8
- **Statement:** When a source-reading test looks for a construct that the split moves, the test shall locate it across the `mapper` package (or follow the class to its declaring file) and shall assert no fewer properties than it asserts today, with today's per-file assertion counts and census pins recorded as the AT-069 baseline before Inc-0.
- **Rationale (informative):** 17 test files read `app.py`'s source today (premise 3); path pins rot per extraction, and a weakened pin is the silent-failure mode Inc-0 exists to prevent (spike R-6).
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_hygiene.py tests/test_darkside_census.py tests/test_keymap.py tests/test_en5.py tests/test_en7.py tests/test_app_imports_used.py`
- **Numeric pass threshold:** exit code 0; the six files pass with per-file assertion counts no lower than the pinned baselines, measured 2026-10-09 by AST count: `test_draft_hygiene.py` ≥ 9, `test_darkside_census.py` ≥ 55, `test_keymap.py` ≥ 35, `test_en5.py` ≥ 34, `test_en7.py` ≥ 37, `test_app_imports_used.py` ≥ 2; the 14 `("mapper/app.py", line)` pins of `test_darkside_census.py` each resolve to exactly one home in the package.
- **Priority:** medium
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** the six generalised test files pass after every increment, and a moved construct is found by content, not by path.
  - **Shipped surface:** the test files themselves — the maintainer's reading of the suite's strength.
  - **Acceptance test(s):** AT-069
  - **Boundary catalog (QC-3):** ☑ empty — a construct absent from the whole package must fail the pin, not skip it ☑ boundary — a pinned string appearing in two homes must fail ("exactly one home") ☐ invalid ☑ error — a deleted or renamed construct.
  - **Negative control:** AT-069 is RED when one pinned darkside line is duplicated into a second module (two homes) and RED when one pin is deleted from the product. Executed at Phase 3.

### HLR-MOD.6 — B-02 is closed
- **Traceability:** US-003
- **Ledger:** LED-2026-10-09-modular-batch.2, LED-2026-10-09-modular-batch.6
- **Statement:** When the batch completes, no module under `mapper/screens/` shall hold any import of `mapper.app` in any form or scope — the F4 function-local exception is deleted with the F4 design — and the four cycle-dodging function-local imports of B-02 shall be removed.
- **Rationale (informative):** the `screens → app` back-edge is the cycle ARCHITECTURE §3 bans; today four function-local imports dodge it (premise 6). The re-export direction (`app` importing `screens`) is the only legal edge. The deleted F4 exception is superseded by the patch-repoint policy (LLR-MOD.3.2): reading modules bind their patch names at module level from their true homes.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_deps.py`
- **Numeric pass threshold:** exit code 0; 0 occurrences of either import form — `import mapper.app` (any alias) or `from mapper.app import …` — in `mapper/screens/**.py`, at any scope; `factory.py`/`settings.py` hold module-level imports from `screens/common.py` and `screens/prompt.py`.
- **Priority:** medium
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** `grep -rnE "import mapper\.app|from mapper\.app import" mapper/screens/` finds nothing; `screens/factory.py` and `screens/settings.py` import their helpers at module level.
  - **Shipped surface:** the shipped module files, read as source.
  - **Acceptance test(s):** AT-070 (own node `tests/test_mod_deps.py -k at070`, distinct from LLR-MOD.6.1's `-k b02`)
  - **Boundary catalog (QC-3):** ☑ boundary — there is no sanctioned exception anymore: the empty set is the boundary, anything else fails ☐ invalid ☑ error — a module-level `import mapper.app` or `from mapper.app import …` re-introduced anywhere under `screens/`, in any scope.
  - **Negative control:** AT-070 is RED on today's tree (premise 6: four function-local imports of `mapper.app`) and RED when any one of them is restored after A2. Executed at Phase 3.

### HLR-MOD.7 — the §3 dependency rules are enforced by a test
- **Traceability:** US-001
- **Ledger:** LED-2026-10-09-modular-batch.5
- **Statement:** When the batch completes, the dependency rules ARCHITECTURE §3 declares for `screens/map`, `screens/common` + `screens/prompt`, `app` and `osopen` shall be enforced by a test over the shipped ASTs.
- **Rationale (informative):** the rules are the batch's own safety net — a module-level `mapper.app` import from the package would re-enter a partially-initialised module (spike R-8), and a concern importing a sibling concern module would recreate the coupling mechanism A removed.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_deps.py`
- **Numeric pass threshold:** exit code 0; all rules asserted: `screens/map` imports only its allow-list, never a sibling concern module, never `mapper.app` at module level; only `mapper.app`, `screens/repo.py` (`NavigationModel` only) and the sibling screen modules that construct it (`screens/home.py`, `screens/import_preview.py` — `MapScreen` only, imported from `mapper.screens.map`) import `screens/map`; `open_external` call sites ⊆ {`app`, `screens/map/opening`}.
- **Priority:** medium
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** the dependency table in ARCHITECTURE §3 cannot be violated without a red test.
  - **Shipped surface:** the module graph of `mapper/`, verified from the shipped ASTs.
  - **Acceptance test(s):** AT-071 — `tests/test_mod_deps.py -k at071`, the HLR-MOD.7 behavioural chain's own node (distinct from LLR-MOD.7.1's `-k arch`): the §3 rules hold on the shipped module graph, which is what makes post-B11 lanes legal.
  - **Boundary catalog (QC-3):** none — a structural property of the import graph, no input class.
  - **Negative control:** AT-071 is RED when a synthetic module-level `import mapper.app` is added to any `screens/map` module, and RED when a concern module imports a sibling concern. Executed at Phase 3 by mutation on a tmp copy.

---

## 4. Low-level requirements (LLR)

> Each LLR decomposes an HLR into a verifiable property at the implementation level and
> maps to one increment of the cut (Inc-0, A1, A2, A3, A5a, B0, A5b, A6, A7, A4, B1–B11, B12).

### LLR-MOD.1.1 — the seven sibling-screen modules own their names (Spine A1, A2, A3, A5a, A5b, A6, A7, A4)
- **Traceability:** HLR-MOD.1
- **Ledger:** LED-2026-10-09-modular-batch.6, LED-2026-10-09-modular-batch.9
- **Statement:** `mapper/screens/common.py` shall own the shared helpers, hint-string constants and `MapHintLine` (app.py:165, A1 — `MapHintLine` moves at A1 with the other hint helpers, so B0's `screens/map/screen.py` never imports it from `mapper.app`; ARCH-8), `screens/prompt.py` the four literal modals (A2), `screens/construct.py` `ConstructScreen` (A3), `screens/map/navigation.py` `NavigationModel` only (A5a, landing before B0 because `MapScreen` itself reads it), `screens/repo.py` `RepoScreen` (A5b), `screens/plug_repo.py` `PlugRepoScreen` (A6), `screens/import_preview.py` `_ImportPreviewScreen` (A7) and `screens/home.py` `HomeScreen` (A4) — the MOD-REQ2 reorder lands every sibling screen that constructs `MapScreen` after B0 (premise 11), and `PlugRepoScreen` pushes `RepoScreen` (app.py:1207), so A5b repo lands before A6 plug_repo (ARCH-9) — and each name shall be re-exported from `mapper/app.py`. The sibling screens shall import `MapScreen` from `mapper.screens.map`, never from `mapper.app`; `screens/plug_repo.py` shall import `RepoScreen` from `mapper.screens.repo`, never `MapScreen`.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_structure.py -k spine_a`
- **Numeric pass threshold:** exit code 0; each of the 7 modules exists, defines its expected names, and `mapper.app.<name>` resolves to the same object (`is` identity through the re-export).
- **Negative control:** RED before A1 (files absent) and RED if a re-export is dropped. Every structural checker is a function taking the package root; the test runs it on the real tree (GREEN) and on a tmp-copy mutant (RED) — a permanent executable negative control. Executed at Phase 3.
- **Boundary catalog:** none — a property of the repository tree, no input class.

### LLR-MOD.1.2 — `MapScreen` lives in the package core (B0)
- **Traceability:** HLR-MOD.1
- **Ledger:** LED-2026-10-09-modular-batch.6
- **Statement:** `mapper/screens/map/__init__.py` shall re-export `MapScreen` and hold no logic, `mapper/screens/map/screen.py` shall define `class MapScreen` with the lifecycle concern, all class constants and `BINDINGS`, and `mapper/app.py` shall hold no `Screen` subclass other than `MapperApp` and no MapScreen concern method.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_structure.py -k b0`
- **Numeric pass threshold:** exit code 0; `inspect.getfile(MapScreen)` ends with `screens/map/screen.py`; `mapper/app.py` ≤ 400 lines.
- **Negative control:** RED before B0 (premise 7) and RED if any concern method remains in `app.py`. Every structural checker is a function taking the package root; the test runs it on the real tree (GREEN) and on a tmp-copy mutant (RED) — a permanent executable negative control. Executed at Phase 3.
- **Boundary catalog:** none — a property of the tree.

### LLR-MOD.1.3 — each concern method lives in its own module (B1–B11)
- **Traceability:** HLR-MOD.1
- **Ledger:** LED-2026-10-09-modular-batch.4, LED-2026-10-09-modular-batch.9
- **Statement:** `mapper/screens/map/screen.py` shall end with `class MapScreen(<11 mixins>, Screen)` and each of the 11 concern modules (`hints`, `exporting`, `opening`, `undo`, `focus_mode`, `editing`, `drafts`, `navigation`, `searching`, `panning`, `painting`) shall define exactly the methods its concern owns per the census — `MapHintLine` is NOT among them: it moves at A1 into `screens/common.py` with the other hint helpers (ARCH-8).
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_structure.py -k spine_b`
- **Numeric pass threshold:** exit code 0; 11 mixin modules present; every method of the census roster assigned to exactly one module; `MapScreen.__mro__` contains the 11 mixins ahead of `Screen`.
- **Negative control:** RED before B1 and RED if any census method has no home or two homes. Every structural checker is a function taking the package root; the test runs it on the real tree (GREEN) and on a tmp-copy mutant (RED). Executed at Phase 3.
- **Boundary catalog:** none — a property of the tree and the class.

### LLR-MOD.2.1 — `BINDINGS` and class constants live only on the core (B0, F3)
- **Traceability:** HLR-MOD.2
- **Ledger:** LED-2026-10-09-modular-batch.4
- **Statement:** The roster of core class constants shall be derived from the AST — every class-level assignment on the pre-split `MapScreen` (including `AUTO_FOCUS` and `MINIMAP_ROWS`) must appear exactly once across the 12 modules — and `BINDINGS`, `DEFAULT_CSS` and every such constant shall be declared only on the core `MapScreen` class, never in a mixin: an AST ban asserts no `screens/map` mixin declares `BINDINGS`, `DEFAULT_CSS` or an `@on`-decorated handler (spike rules 1–2: keys silently drop, handlers double-fire).
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_dispatch.py -k bindings`
- **Numeric pass threshold:** exit code 0; exactly 1 `BINDINGS` declaration and 0 `DEFAULT_CSS` declarations across the 11 mixins; 0 `@on`-decorated methods in any mixin; the AST-derived constant roster is fully held by `MapScreen.__dict__` with 0 shadowed or dropped constants.
- **Negative control:** RED if `BINDINGS` is declared in any mixin (spike rule 1: keys silently drop), RED if `DEFAULT_CSS` or an `@on` handler lands in a mixin. Executed at Phase 3 on a tmp-copy mutant — every structural checker is a function taking the package root, run on the real tree (GREEN) and the mutant (RED).
- **Boundary catalog:** ☑ error — a mixin-declared `BINDINGS` or shadowing constant.

### LLR-MOD.2.2 — method names are pairwise-disjoint across the map package (B1, guard, R-5)
- **Traceability:** HLR-MOD.2
- **Ledger:** LED-2026-10-09-modular-batch.2, LED-2026-10-09-modular-batch.4
- **Statement:** The twelve `mapper/screens/map/` modules shall declare pairwise-disjoint sets of method names, and no module under `mapper/screens/` shall import any of the eight patch names of premise 4 (`MAX_RENDER_NODES`, `refusal_sentence`, `save_svg`, `pan_extent`, `LayeredRenderer`, `preview_csv`, `SearchIndex`, `GitHubConnector`) from `mapper.app` in any form or scope — each reading module binds its patch names at module level from their true homes (LLR-MOD.3.2). The AST ban of LLR-MOD.2.1 (`@on`, `DEFAULT_CSS`, `BINDINGS` in a mixin) is asserted here against the shipped ASTs as well.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_dispatch.py -k disjoint`
- **Numeric pass threshold:** exit code 0; 0 pairwise intersections across the 12 modules' method sets; 0 `screens/**` imports of any of the eight patch names from `mapper.app` (either AST form, any scope).
- **Negative control:** RED when a method name is added to two mixins (spike rule 3: the handler would fire twice) and RED on any import of a patch name from `mapper.app` under `screens/`. Executed at Phase 3 on a tmp-copy mutant — the checker is a function taking the package root, run on the real tree (GREEN) and the mutant (RED).
- **Boundary catalog:** ☑ error — a duplicated handler name; a `screens/**` import of a patch name from `mapper.app`.

### LLR-MOD.2.3 — actions and handlers dispatch through mixins with real keys (B1 spike)
- **Traceability:** HLR-MOD.2
- **Ledger:** none
- **Statement:** After the hints mixin moves, `MapScreen` shall dispatch `action_*` methods and `on_*` handlers resolved through the mixin bases exactly as before the move, demonstrated by a pilot-driven hint test pressing real keys.
- **Validation:** `test (e2e)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_dispatch.py -k pilot` (pilot test driving `MapperApp` with `pilot.press`)
- **Numeric pass threshold:** exit code 0; the hint line after a scripted key sequence equals the pre-B1 capture.
- **Negative control:** RED when the same `on_*` name is declared in two mixins (the handler runs twice and the hint drift shows in the capture). Executed at Phase 3.
- **Boundary catalog:** ☑ empty — the hints concern owns 0 shared attributes, so it exercises dispatch with no state coupling.

### LLR-MOD.3.1 — every name the tests import is re-exported (A1, A2, A3, A5a, A5b, A6, A7, A4, B0)
- **Traceability:** HLR-MOD.3
- **Ledger:** LED-2026-10-09-modular-batch.1, LED-2026-10-09-modular-batch.9
- **Statement:** `mapper/app.py` shall re-export every name imported from it by the test files and `screens/factory.py` — the 21 names of premise 10 — so that every `from mapper.app import X` site resolves to the moved definition.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_compat.py -k reexport`
- **Numeric pass threshold:** exit code 0; all 21 names resolve from `mapper.app` with object identity to their defining module.
- **Negative control:** RED if any one re-export is removed. Executed at Phase 3.
- **Boundary catalog:** ☑ empty — the import census itself (21 names) bounds the set; a zero-name census cannot pass.

### LLR-MOD.3.2 — the eight patch targets are repointed to their reading modules (per increment)
- **Traceability:** HLR-MOD.3
- **Ledger:** LED-2026-10-09-modular-batch.2, LED-2026-10-09-modular-batch.9
- **Statement:** There shall be no lazy read through `mapper.app` (the F4 design is dropped): each patch target of premise 4 shall be a module-global of the module that reads the name, bound in the increment that moves the reader — `refusal_sentence` with `_path_refusal`'s home (A1, `screens/common.py`), `MAX_RENDER_NODES` and `SearchIndex` with `screens/map/searching.py` (B9), `save_svg` with the exporting concern (`screens/map/exporting.py`), `pan_extent` with the panning concern (`screens/map/panning.py`), `LayeredRenderer` and `preview_csv` with `screens/import_preview.py` (read through the CSV-import path — `LayeredRenderer` at test_en8.py:332 is read by `_ImportPreviewScreen`, NOT by panning/render) — except `GitHubConnector.fetch`: a class-attribute patch on the shared class object, it survives the move with the class and needs no repoint (ARCH-11), leaving seven module-global repoints — and an AST guard shall assert, for every patch site in `tests/`, that the site is repointed to the module-global of the module that actually READS the patched name at that site (the reader of each patch site, not merely some module that binds the name), so a vacuous repoint cannot pass (ARCH-10).
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_compat.py -k patch_guard` (the AST guard) and `python -B -m pytest -q -p no:cacheprovider tests/test_search.py tests/test_inc9q.py tests/test_en8.py tests/test_app.py tests/test_inc9c.py tests/test_inc9n.py tests/test_inc9.py` (the repointed patch sites bite)
- **Numeric pass threshold:** exit code 0; all eight targets bite through their repointed module-globals at premise 4's site counts; the guard passes for every patch site in `tests/`; 0 imports of any patch name from `mapper.app` into a `screens/` module (any form, any scope).
- **Negative control:** RED when one repoint is skipped (the patch stops biting while the rest of the suite passes — the silent-failure mode), and RED when a patch site's target module does not bind or read the name (the guard). Executed at Phase 3 on a tmp-copy mutant.
- **Boundary catalog:** ☑ boundary — the patched limit exactly one node below the map size.

### LLR-MOD.4.1 — the full suite stays green at every increment gate
- **Traceability:** HLR-MOD.4
- **Ledger:** LED-2026-10-09-modular-batch.4
- **Statement:** At every increment gate of the batch and at P4, the full test suite shall pass with zero failures and no test file edited to weaken a behaviour assertion.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/` (per increment gate and at P4).
- **Numeric pass threshold:** exit code 0; 0 failed (baseline at P0: 2941 passed / 3 xfailed / 0 failed, PLAN test ledger).
- **Negative control:** any behaviour drift in the moved code reddens the suite; the byte-identical method-body check (AST dump of moved bodies against the Inc-0 baseline) is the increment-local RED side (LLR-MOD.4.3). Executed per increment.
- **Boundary catalog:** none — a property of the suite.

### LLR-MOD.4.2 — painted output equals the committed text golden (all increments)
- **Traceability:** HLR-MOD.4
- **Ledger:** LED-2026-10-09-modular-batch.3, LED-2026-10-09-modular-batch.9
- **Statement:** A TEXT golden (not SVG) shall be captured at Inc-0 on the pre-move commit, after each step of a scripted session — open a map, move, search, toggle a view, export, quit — at terminal widths 118 and 87 columns, with volatile cells normalised (paths, timestamps) and each step gated on a condition wait rather than a fixed sleep. `tests/test_mod_parity.py` shall then re-drive the same scripted session after every increment gate and compare the painted lines against the committed golden.
- **Golden record:** golden paths `.dev-flow/2026-10-09-modular-batch/evidence/mod_parity_118.txt` and `.../mod_parity_87.txt`; captured on the pre-move commit at Inc-0; capture commit and golden sha256 (one per width) recorded in the Inc-0 increment packet (`03-increments/increment-001.md`) — the three values are written into this requirement when the golden is captured, and the test asserts the on-disk golden still hashes to the recorded sha256.
- **Validation:** `test (e2e)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_parity.py -k parity`
- **Numeric pass threshold:** exit code 0; 0 painted-line diffs across all scripted steps at both widths, after volatile-cell normalisation.
- **Negative control:** a mutated-copy RED — a one-token change to a painted string in a tmp copy of the product module reddens the comparison (as does a deliberately wrong golden line); "golden file missing" is NOT the negative control. Executed at Phase 3.
- **Boundary catalog:** ☑ boundary — widths 118 and 87 exercise wide and truncated layouts.

### LLR-MOD.4.3 — moved method bodies are byte-identical and new modules are name-clean (all increments)
- **Traceability:** HLR-MOD.4
- **Ledger:** LED-2026-10-09-modular-batch.4, LED-2026-10-09-modular-batch.9
- **Statement:** `tests/test_mod_bodies.py` shall assert, per increment: (a) every census method's body is byte-identical across the move — a per-method `ast.dump` compared against a baseline JSON at the pinned path `.dev-flow/2026-10-09-modular-batch/evidence/mod-bodies-baseline.json` (captured at Inc-0; its sha256 recorded in the Inc-0 packet), with every census method appearing exactly once across the package (no method lost or duplicated by a move); and (b) no new module references an undefined global, checked per module by AST/symtable analysis.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_bodies.py`
- **Numeric pass threshold:** exit code 0; the baseline diff is empty (every census method exactly once, every body `ast.dump`-equal to its Inc-0 baseline); 0 undefined-global references in any new module.
- **Negative control:** RED controls run on a tmp copy of the tree — a one-token mutation inside any moved method body reddens the baseline diff, and a deleted import in a new module reddens the undefined-global check. Every structural checker is a function taking the package root, run on the real tree (GREEN) and the mutant (RED). Executed at Phase 3.
- **Boundary catalog:** none — an oracle diff, no input class.

### LLR-MOD.5.1 — the six source-reading tests generalise to the package (Inc-0)
- **Traceability:** HLR-MOD.5
- **Ledger:** LED-2026-10-09-modular-batch.8
- **Statement:** `test_draft_hygiene.py`, `test_darkside_census.py`, `test_keymap.py`, `test_en5.py`, `test_en7.py` and `test_app_imports_used.py` shall locate their pins by content across `mapper/**/*.py` (or via `inspect.getfile(MapScreen)`) instead of by `app.py` path, before any code moves, and their assertion counts shall be no lower than today. This extends to `tests/test_keymap.py:214–220`, whose scanned module set shall be derived by `pkgutil.walk_packages` over `mapper` rather than pinned by hand, so every new module is scanned without a test edit.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_hygiene.py tests/test_darkside_census.py tests/test_keymap.py tests/test_en5.py tests/test_en7.py tests/test_app_imports_used.py`
- **Numeric pass threshold:** exit code 0; each of the 14 darkside pins resolves to exactly one home; the MapScreen arms of `test_draft_hygiene.py` parse `inspect.getfile(MapScreen)`; the `test_keymap.py` module set equals `pkgutil.walk_packages(mapper)` (its former hand-pinned list at :214–220 is gone).
- **Negative control:** RED on a pin duplicated into a second home; RED on a pin pointing at a stale path after B0 (which is why Inc-0 runs first). Executed at Phase 3.
- **Boundary catalog:** ☑ boundary — a pinned string with two homes fails; ☐ empty — a construct absent from the whole package fails.

### LLR-MOD.5.2 — extraction-riding test follow-ups land in their increments (B3, B9)
- **Traceability:** HLR-MOD.5
- **Ledger:** none
- **Statement:** `test_arch_osopen_callers.py`'s allow-list shall gain `screens/map/opening.py` in Inc-B3, and the `test_inc9p.py`/`test_inc9q.py` "one home" arms shall extend their scanned set to the new homes in the increments that create them.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_arch_osopen_callers.py tests/test_inc9p.py tests/test_inc9q.py`
- **Numeric pass threshold:** exit code 0 at the B3 and B9 gates.
- **Negative control:** RED if the allow-list is extended before the call site moves, or not extended after. Executed at the gates.
- **Boundary catalog:** none — test-only follow-ups.

### LLR-MOD.6.1 — the four B-02 function-local imports are removed (A1, A2)
- **Traceability:** HLR-MOD.6
- **Ledger:** LED-2026-10-09-modular-batch.2
- **Statement:** `screens/factory.py` shall import `keybar_groups`, `_save_or_toast` and `_PromptScreen`, and `screens/settings.py` shall import `keybar_groups`, at module level from `screens/common.py` and `screens/prompt.py`, and the four function-local imports of premise 6 shall be deleted. The dependency checker matches BOTH import forms by AST — `import mapper.app` (any alias) and `from mapper.app import …` — at any scope; with the F4 design dropped there is no sanctioned exception.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_deps.py -k b02`
- **Numeric pass threshold:** exit code 0; 0 occurrences of either import form referencing `mapper.app` in `mapper/screens/**.py`, at any scope; module-level helper imports present in factory/settings.
- **Negative control:** RED on today's tree (premise 6) and RED if any one import is restored. Every structural checker is a function taking the package root; the test runs it on the real tree (GREEN) and on a tmp-copy mutant (RED). Executed at Phase 3.
- **Boundary catalog:** ☑ error — a restored cycle-dodging import.

### LLR-MOD.6.2 — no module-level `mapper.app` import from the package (B0, all increments)
- **Traceability:** HLR-MOD.6
- **Ledger:** LED-2026-10-09-modular-batch.2
- **Statement:** No module under `mapper/screens/` shall import `mapper.app` at any point in the batch, in any form (`import mapper.app` under any alias, or `from mapper.app import …`) and at any scope — the F4 function-local exception is deleted with the F4 design; and the sibling screens that construct `MapScreen` (`screens/home.py`, `screens/import_preview.py`) shall import it from `mapper.screens.map`, never from `mapper.app`.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_deps.py -k no_app_import`
- **Numeric pass threshold:** exit code 0; 0 AST-detected occurrences of either import form referencing `mapper.app` anywhere under `mapper/screens/`.
- **Negative control:** RED when either import form targeting `mapper.app` is added to any `screens/` module at any scope (spike R-8: re-entry into a partially-initialised module), and RED if `MapScreen` is imported from `mapper.app` in a sibling screen. Executed at Phase 3 on a tmp-copy mutant — the checker is a function taking the package root, run on the real tree (GREEN) and the mutant (RED).
- **Boundary catalog:** ☑ error — either banned import shape, in any scope.

### LLR-MOD.7.1 — the amended §3 dependency rules hold (B3, B12)
- **Traceability:** HLR-MOD.7
- **Ledger:** LED-2026-10-09-modular-batch.4
- **Statement:** The AST-derived dependency test shall assert: `screens/map` imports only its §3 allow-list and never a sibling concern module; only `mapper.app`, `screens/repo.py` (`NavigationModel` only) and the sibling screens that construct `MapScreen` (`screens/home.py`, `screens/import_preview.py` — `MapScreen` only, imported from `mapper.screens.map`) import `screens/map`; `screens/common` and `screens/prompt` import neither `app` nor `widgets` internals; `open_external` is called only from `app` and `screens/map/opening`.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_deps.py -k arch`
- **Numeric pass threshold:** exit code 0; all four rule groups asserted against the shipped ASTs.
- **Negative control:** RED on a synthetic sibling-concern import, RED on a `MapScreen` import from `mapper.app` in a sibling screen, and RED before B3 (the osopen allow-list then names a file that does not exist yet — the test is scoped to land with B3). Every structural checker is a function taking the package root; the test runs it on the real tree (GREEN) and on a tmp-copy mutant (RED). Executed at Phase 3.
- **Boundary catalog:** ☑ error — each banned import shape.

### LLR-MOD.7.2 — the F1/F2 freeze is mechanical (B12)
- **Traceability:** HLR-MOD.7
- **Ledger:** LED-2026-10-09-modular-batch.7, LED-2026-10-09-modular-batch.9
- **Statement:** `tests/test_mod_census.py` shall re-run `.dev-flow/2026-10-09-modular-batch/spike/ast_census.py` over the package and diff the result against the committed `.dev-flow/2026-10-09-modular-batch/spike/census.json` — the batch's archive location, read by the census guard — so any attribute gaining a writer concern, any new cross-concern attribute, or any F2 name/signature drift goes red without a census amendment.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_census.py`
- **Numeric pass threshold:** exit code 0; census diff empty.
- **Negative control:** RED when a synthetic writer is added to a second concern for any F1 attribute. Executed at Phase 3 on a tmp-copy mutant — the census checker is a function taking the package root, run on the real tree (GREEN) and the mutant (RED).
- **Boundary catalog:** none — an oracle diff, no input class.

### Information Flow Contract (IFC) — C-54

- **Part A — flows:**

```
FLOW moved-names-to-consumers
SOURCE: the defining modules (screens/common.py, screens/prompt.py, screens/map/*, …)
NODES: the re-export block in mapper/app.py (LLR-MOD.1.1, LLR-MOD.1.2, LLR-MOD.3.1)
SINK: the 68 importing test files, screens/factory.py, screens/settings.py
```

```
FLOW patch-surface
SOURCE: the monkeypatch sites (premise 4: tests/test_search.py ×6 — 5 setattr + the SearchIndex
attribute assignment, tests/test_inc9q.py ×1, tests/test_app.py ×4 — 2 save_svg + 2 fetch,
tests/test_en8.py ×2, tests/test_inc9c.py ×3 — save_svg, preview_csv, fetch,
tests/test_inc9n.py ×1, tests/test_inc9.py ×1)
NODES: the repointed module-globals of the modules that read each name (LLR-MOD.3.2), the
AST guard, and the no-import-from-mapper.app ban (LLR-MOD.2.2, LLR-MOD.6.1–6.2)
SINK: the search refusal/count line and the path-refusal toast on the shipped screens
```

```
FLOW key-dispatch
SOURCE: BINDINGS on the core MapScreen class (LLR-MOD.2.1)
NODES: action_*/on_* resolution through the mixin MRO (LLR-MOD.2.2, LLR-MOD.2.3)
SINK: the painted map screen under real keystrokes
```

- **Part B — boundary decomposition:** no. The batch moves code between files of one component; no component of the system's boundary becomes addressable on its own.

---

## 5. Validation strategy

### 5.1 Methods

> **Two layers** (per the Two-layer validation rule).
> - **Layer A — white-box / functional (`TC-NNN`):** the structure test `tests/test_mod_structure.py` (LLR-MOD.1.1–1.3), the dispatch guard `tests/test_mod_dispatch.py` (LLR-MOD.2.1–2.3), the compatibility test `tests/test_mod_compat.py` (LLR-MOD.3.1–3.2), the method-body oracle `tests/test_mod_bodies.py` (LLR-MOD.4.3), the dependency test `tests/test_mod_deps.py` (LLR-MOD.6.1–6.2, LLR-MOD.7.1) and the census-diff test `tests/test_mod_census.py` (LLR-MOD.7.2). The full suite at every increment gate is LLR-MOD.4.1's Layer A.
> - **Layer B — black-box / behavioral acceptance (`AT-NNN`):** each AT owns a node distinct from every LLR node.
>   - AT-065 (`tests/test_mod_parity.py -k at065`; LLR node: `-k parity`) drives the real app with real keys at 118 and 87 columns and compares painted output against the committed text golden (story 2).
>   - AT-066 (`tests/test_mod_dispatch.py -k at066`; LLR node: `-k pilot`) drives a bound action and an `on_*` handler through the mixins with real keys (story 2 / mechanism A).
>   - AT-067 (`tests/test_mod_compat.py -k at067`; LLR nodes: `-k patch_guard` and the patch-carrying files) observes the patched refusal/limit through the shipped screens (story 3).
>   - AT-068 (`tests/test_mod_structure.py -k at068`; LLR nodes: `-k spine_a`/`b0`/`spine_b`) reads the shipped repository tree — story 1's surface (story 1).
>   - AT-069 (the six Inc-0 test files, `-k at069`; LLR node: the same six files without the selector) observes that moved constructs are found by content across the package (story 3).
>   - AT-070 (`tests/test_mod_deps.py -k at070`; LLR node: `-k b02`) greps/ASTs the shipped `screens/` tree for the closed B-02 (story 3).
>   - AT-071 (`tests/test_mod_deps.py -k at071`; LLR node: `-k arch`) asserts the §3 dependency rules on the shipped module graph, which is what makes post-B11 lanes legal (HLR-MOD.7).

### 5.2 Batch acceptance criteria
- 100% of LLRs are covered by at least one executed check with a pass result.
- Every AT is GREEN, each with an executed RED counterfactual.
- The full suite is green at P4 (0 failed; baseline 2941 passed / 3 xfailed).
- The painted-capture comparison reports 0 diffs at both widths.
- The batch forks nothing during the spine; parallel product lanes are declared only after Inc-B11.

---

## 6. Appendices (optional)

### 6.1 Extended glossary
### 6.2 Relevant design decisions
- **Mechanism A (plain mixins on the core class).** The only mechanism of the three the ARQ compared that keeps Textual dispatch, `BINDINGS`, the 30-slot shared state and the `_guard_draft`/`refresh_canvas` funnels byte-identical while giving disjoint feature files. Mechanism B (collaborator objects) is the documented fallback (spike R-1) only if the B1 spike contradicts the MRO evidence.
- **The BINDINGS rule (spike-measured).** `BINDINGS` and every class constant live only on the core `MapScreen`; mixins hold `action_*`/`on_*` methods only. Reason: Textual 8.2.8 silently does not merge mixin-declared BINDINGS (premise 8).
- **Re-export compatibility.** `mapper/app.py` keeps one `from … import` block per new home module, permanently, so the 70 import sites of premise 2 never change. The alternative — rewriting 68 test files — was rejected: the tests are not rewritten for the move.
- **Serial spine, parallel output.** The extraction spine is serial because `modules(A) ∩ modules(B) = ∅` fails on `app.py`/`screen.py` for any two extraction increments. The batch's deliverable is the fork after B11, not parallelism during it (§2.8).
- **Patch repoints (supersedes the F4 lazy reads).** The eight patch names are module-globals of the modules that read them, each rebound in the increment that moves its reader; no module reads them through `mapper.app` at any scope, and an AST guard proves every `tests/` patch site targets a name its module binds or reads (LLR-MOD.3.2, LLR-MOD.2.2). The deleted F4 function-local read would itself have been a `screens → app` back-edge (LLR-MOD.6.2).
- **Inc-0 first.** The six source-reading tests generalise before any code moves, so no extraction increment ever runs red against a stale pin (spike R-6).

### 6.3 Open risks
- **R-1 (silent double dispatch):** an `on_*` name in two mixins runs twice. Guarded by LLR-MOD.2.2/LLR-MOD.2.3; B1 is the pilot spike. If a future Textual change alters MRO dispatch, the guards redden first.
- **R-2/R-3 (shared state and funnels):** 30 shared attributes, 15 multi-writer; `refresh_canvas` has 25 call sites in 9 concerns. Mitigation: `self.*` semantics kept byte-identical; F1/F2 frozen and made mechanical by LLR-MOD.7.2.
- **R-4 (patch surface):** guarded by LLR-MOD.3.2's repoint-plus-AST-guard pair; the failure mode is silent, so both the bite checks and the guard are executable, not conventions.
- **R-5 (silent import/name drift):** one guard test (LLR-MOD.2.2) asserts disjoint method names, the `@on`/`DEFAULT_CSS`/`BINDINGS` mixin ban, and the ban on importing any patch name from `mapper.app` under `screens/`, together.
- **R-6 (pin rot):** mitigated by Inc-0 ordering (LLR-MOD.5.1); if a pin is found to be ungeneralisable, the fallback recorded in the proposal is Spine A only — a strictly weaker outcome, returned to the trunk as an A3, not improvised in a lane.
- **R-7 (CSS selector drift):** no class is renamed during any move; AT-065 catches a styling break as a painted diff.
- **R-8 (import cycle):** the MOD-REQ2 reorder lands the common/prompt/construct helpers and `NavigationModel` before B0; LLR-MOD.6.2 bans the `mapper.app` edge from `screens/` in any form or scope.
- **R-9 (serial calendar cost):** accepted; 12 spine increments, each ≤ 4 source files, is the price of the disjoint-file payoff.
- **External `V7`** (the installed flow bundle differs from its manifest) is not about this project and carries no product risk.
- **Security questions (`devflow-scan-spec.py` flagged `session`, C1).** False positive. The word is the "scripted session" of the parity test (a sequence of key presses), not an auth or user session. The batch moves code between modules and adds no auth, secret, input, network or markup surface. `osopen` stays the only OS-handler crossing (HLR-MOD.7, `tests/test_arch_osopen_callers.py`).

### 6.4 Phase-1 reconciliation log — moved to the ledger (§7)

### 6.5 Requirement amendments — moved to the ledger (§7)

---

## 7. The ledger — authored as a SEPARATE FILE

The fence below is the ledger's seed: `devflow-init.py` writes it to `01-requirements-ledger.md`. The shape of an entry is in the field guide.

```markdown
# Requirements ledger — mapper — Batch 2026-10-09-modular-batch

> Append-only. Entries are added in chronological order and never rewritten. The live
> contract is `01-requirements.md`; this file records how it came to say what it says.
> Every entry names the requirement it amends; every requirement names its entries. `V26`
> compares the two sets of pairs both ways.

_No entries yet. The first amendment to the live contract writes the first one, in the
shape the field guide's §7 shows (`req-template.md` in the guide directory init prints), and nothing
above this line is ever edited._
```
