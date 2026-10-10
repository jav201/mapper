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
  re-exports + the two patch-surface names;
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
| patch surface | the two names bound in `mapper/app.py` and read at call time through the module object: `MAX_RENDER_NODES`, `refusal_sentence` |
| spine | the serial extraction sequence Inc-0 → A1–A7 → B0 → B1–B11 → B12; every increment that deletes lines from `app.py`/`screen.py` collides with every other on that file |
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
- The census (spike §3 freeze) is the F1/F2 oracle; `census/ast_census.py` re-runs over
  the package at B12.
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
- **Functionality (V, N):** user = maintainer · outcome = after the split, `mapper/screens/map/searching.py`, `editing.py`, `painting.py`, `exporting.py`, `drafts.py`, `home.py`, `repo.py`, … are disjoint files; a search feature touches only `searching.py` · why = the operator's "primordial" · out of scope = the post-B11 lanes themselves.
- **Feasibility (E, S):** implementation path = mechanism A (spike §2), increments Inc-0, A1–A7, B0, B1–B11, B12 per spike §6 · dependencies = the F1–F5 freeze (PDR) · fits one batch? = yes — the spine is serial but each increment is ≤ 4 source files.
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
- **Functionality (V, N):** outcome = all 70 `from mapper.app import` sites keep resolving; the 5 `MAX_RENDER_NODES` patches and the 1 `refusal_sentence` patch still bite; the 17 source-reading tests scan the package with pins no weaker than today · out of scope = rewriting test behaviour assertions.
- **Feasibility (E, S):** implementation path = permanent re-export block in `app.py` (LLR-MOD.3.1), F4 lazy reads (LLR-MOD.3.2), Inc-0 generalisation of the six test files before any move.
- **Evaluability (T) — behavioral, black-box:** "When the maintainer runs the suite after any increment, it passes with zero failures and no test file was edited to weaken an assertion."
- **Open questions:** none.
- **Classification:** `READY`.

### 2.7 Premise evaluation (C-43) — MANDATORY, one row per premise

| # | Premise, as a truth-apt proposition | Tier | Verdict | Executed evidence (command output / `file:line` — **NOT** a citation of another document) | Disposition |
|---|---|---|---|---|---|
| 1 | `mapper/app.py` is 5255 lines; `MapScreen` starts at line 1536 and `MapperApp` follows at 4990 | executed | ✅ TRUE | `wc -l mapper/app.py` → `5255 mapper/app.py`; `grep -n "^class MapScreen\|^class MapperApp\|^def main" mapper/app.py` → `1536:class MapScreen(Screen):`, `4990:class MapperApp(App):`, `5239:def main() -> None:` | in scope (HLR-MOD.1, LLR-MOD.1.1–1.3) |
| 2 | 68 test files import `from mapper.app import …`, and two `mapper/` modules also do | executed | ✅ TRUE | `grep -rl "from mapper.app import" tests \| wc -l` → `68`; `grep -rl "from mapper.app import" mapper` → `mapper/screens/factory.py`, `mapper/screens/settings.py` | in scope (HLR-MOD.3, LLR-MOD.3.1) |
| 3 | 17 test files read `app.py`'s source (AST, path pins, `inspect.getsource`) | executed | ✅ TRUE | `grep -rln 'app\.py"\|app\.__file__\|inspect\.getsource' tests \| wc -l` → `17` (lists `test_app_imports_used.py`, `test_darkside_census.py`, `test_draft_hygiene.py`, `test_en5.py`, `test_en7.py`, `test_search.py`, …) | in scope (HLR-MOD.5, LLR-MOD.5.1) |
| 4 | `MAX_RENDER_NODES` is monkeypatched on the `mapper.app` module object at exactly 5 sites; `refusal_sentence` at exactly 1 | executed | ✅ TRUE | `grep -n "monkeypatch.setattr" tests/test_search.py \| grep MAX_RENDER` → `2393`, `2456`, `2549`, `2649`, `2690`; `sed -n '393p' tests/test_inc9q.py` → `monkeypatch.setattr(app_module, "refusal_sentence", lambda reason, **kw: f"S:{reason}")` | in scope (HLR-MOD.3, LLR-MOD.3.2) |
| 5 | Both patch names are bound at `app.py` module level today | executed | ✅ TRUE | `grep -n "refusal_sentence" mapper/app.py` → `49: ATTACHMENT_HARD_LINKED, OK as OSOPEN_OK, PATH_NOT_SUPPORTED, confine_reason, open_external, refusal_sentence,`; `grep -n "MAX_RENDER_NODES" mapper/app.py` → `58: MAX_RENDER_NODES,` | in scope (F4, LLR-MOD.3.2) |
| 6 | The four B-02 cycle-dodging function-local imports exist where ARCHITECTURE §3 records them | executed | ✅ TRUE | `grep -n "    import" mapper/screens/factory.py mapper/screens/settings.py \| grep mapper` → factory: `from mapper.app import keybar_groups` (≈:198), `from mapper.app import _save_or_toast` (≈:217), `from mapper.app import _PromptScreen` (≈:507); settings: `from mapper.app import keybar_groups` (≈:89) | in scope (HLR-MOD.6, LLR-MOD.6.1) |
| 7 | `mapper/screens/map/` does not exist yet | executed | ✅ TRUE | `ls mapper/screens/map` → `ls: cannot access 'mapper/screens/map': No such file or directory` | in scope (LLR-MOD.1.2 is the commitment that creates it) |
| 8 | On Textual 8.2.8: BINDINGS declared in a plain mixin are NOT merged; a core binding dispatches to a mixin action; `on_*` handlers run from every MRO class that defines them | executed (spike) | ✅ TRUE | `evidence/arq-mro-spike.transcript`: `screen bindings ['ctrl+c', 'shift+tab', 'super+c', 'tab', 'y']` (mixin-declared `x` absent); `log ['on_mount(mixin)', 'on_mount(mixin2)', …]`; `['ctrl+c', …, 'z']` with `z` → `action_from_mixin` | in scope (HLR-MOD.2, LLR-MOD.2.1, LLR-MOD.2.2) |
| 9 | The runtime is Python 3.12.7 with textual 8.2.8 | executed | ✅ TRUE | `python -c "import textual; print(textual.__version__)"` → `8.2.8`; `python --version` → `Python 3.12.7` | constraint (§2.4) |
| 10 | Tests plus `screens/factory.py` import 21 distinct names from `mapper.app` | executed | ✅ TRUE | AST/join-continuation census over `tests/**/*.py` + `mapper/screens/factory.py` → `21`: `COUNT_REGION_ID ConstructScreen GitHubConnector HomeScreen MapScreen MapperApp NavigationModel PAN_INERT_HINT PlugRepoScreen RepoScreen SEARCH_ACTIVE_LABEL SEARCH_COUNT_SUBJECT SEARCH_SUSPENDED_NOTICE _ConfirmScreen _FichaScreen _ImportPreviewScreen _PromptScreen _QUERY_ECHO_CELLS _save_or_toast keybar_groups map_hint` | in scope (LLR-MOD.3.1) |

- **Premise evaluation:** 10 premise(s) · 10 ✅ TRUE / 0 ❌ FALSE / 0 ❓ UNDECIDABLE

### 2.8 Fork preconditions (C-52) — MANDATORY, and the declared empty when the batch does not fork

The batch forks **only after Inc-B11**; during the batch the spine (Inc-0 → A1–A7 → B0 →
B1–B11 → B12) is **serial**, because every increment that deletes lines from
`app.py`/`screen.py` collides with every other on that file (ARCHITECTURE §6). Parallel
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
- **Ledger:** none
- **Statement:** When the batch completes, the repository shall hold the ARQ target map: seven sibling-screen modules under `mapper/screens/` (`common`, `prompt`, `construct`, `home`, `repo`, `plug_repo`, `import_preview`), the `mapper/screens/map/` package with one concern module per MapScreen concern plus a re-export-only `__init__.py`, and `mapper/app.py` reduced to `MapperApp`, `main`, the `CSS` block, the re-exports and the two patch-surface names.
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
- **Ledger:** none
- **Statement:** When a key chord or action reaches the map screen, the system shall dispatch it exactly as before the split: `BINDINGS` and every class constant live only on the core `MapScreen` class, `action_*` and `on_*` handlers resolve through the mixin bases, and method names are pairwise-disjoint across the twelve map modules.
- **Rationale (informative):** the spike (premise 8) measured that BINDINGS in a mixin are silently not merged and that an `on_*` name in two MRO classes runs twice; both failure modes are silent, so both need executable guards.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_dispatch.py`
- **Numeric pass threshold:** exit code 0; BINDINGS found in exactly 1 class (the core); 0 pairwise method-name collisions across the 12 modules; 0 mixin-declared core class constants.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** every bound key and every painted hint on the map screen behaves identically to the pre-split capture, including keys whose `action_*` now lives in a mixin.
  - **Shipped surface:** the map screen driven with real keys through `MapperApp` + `app.run_test(...)` + `pilot.press(...)`.
  - **Acceptance test(s):** AT-066
  - **Boundary catalog (QC-3):** ☑ empty — the hints mixin owns 0 shared attributes (B1 spike), so an empty-dependency dispatch is exercised first ☐ invalid ☑ error — a duplicated handler name would fire twice; a mixin `BINDINGS` would silently drop keys.
  - **Negative control:** AT-066 is RED when a second mixin declares an `on_*` name already present in another module, and RED when `BINDINGS` is moved off the core class — both by injected mutation. Executed at Phase 3.

### HLR-MOD.3 — imports and monkeypatches through `mapper.app` keep biting
- **Traceability:** US-003
- **Ledger:** none
- **Statement:** When an existing test imports a moved name from `mapper.app` or monkeypatches `MAX_RENDER_NODES` or `refusal_sentence` on it, the import shall resolve and the patch shall change behaviour exactly as today, with both names read lazily through the module object at call time.
- **Rationale (informative):** a top-level `from mapper.app import MAX_RENDER_NODES` in a concern module binds a copy and the five search patches silently stop biting; the suite would still pass while the guard is dead.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_compat.py tests/test_search.py tests/test_inc9q.py`
- **Numeric pass threshold:** exit code 0; all 21 imported names (premise 10) resolve from `mapper.app`; the 5 `MAX_RENDER_NODES` patch sites and the 1 `refusal_sentence` patch site pass; 0 top-level bindings of the two F4 names outside `app.py`.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** with `MAX_RENDER_NODES` patched below the map size, the search refusal paints at the patched limit; with `refusal_sentence` patched, the refusal text shows the patch's marker — in both cases through the shipped screens.
  - **Shipped surface:** the map screen's search/count line and the path-refusal toast.
  - **Acceptance test(s):** AT-067
  - **Boundary catalog (QC-3):** ☐ empty ☑ boundary — the patched limit one node below the map size (exactly the shipped patch call shapes) ☐ invalid ☑ error — an eager top-level binding of either F4 name.
  - **Negative control:** AT-067 is RED when `_search_order`/`_walk_hits` read an eager copy of `MAX_RENDER_NODES` (the patch then does not bite), and RED when `_path_refusal` binds `refusal_sentence` at import time. Executed at Phase 3 by reverting the F4 lazy-read in a copy.

### HLR-MOD.4 — the app does not change
- **Traceability:** US-002
- **Ledger:** none
- **Statement:** When any extraction increment of the batch lands, the system's observable behaviour shall equal the pre-split capture, evidenced by a zero-failure full test suite and byte-equal painted output at terminal widths 118 and 87 columns.
- **Rationale (informative):** 3454 lines move; the only honest oracle for "no behaviour change" on a TUI is painted-output comparison over real keystrokes, plus the full suite at every increment gate.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_parity.py` and the full suite `python -B -m pytest -q -p no:cacheprovider tests/` at P4.
- **Numeric pass threshold:** exit code 0 for both; 0 painted-line diffs across the scripted session (open a map, move, search, toggle a view, export, quit) at both widths.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** every line the operator can see during the scripted session equals the pre-split capture, at both 118 and 87 columns.
  - **Shipped surface:** the painted screen of the real app (`MapperApp(tmp_path)` driven with real keys; helpers reused from `tests/test_draft_save.py`).
  - **Acceptance test(s):** AT-065
  - **Boundary catalog (QC-3):** ☐ empty ☑ boundary — the two widths (wide 118 and narrow 87) exercise truncation and wrapping paths differently ☐ invalid ☑ error — a changed hint string, key label or layout cell.
  - **Negative control:** AT-065 is RED when any one painted line is mutated (a one-word hint change in a copy of the product code reddens the comparison), and RED against the pre-capture run before the capture exists. Executed at Phase 3.

### HLR-MOD.5 — source-reading tests scan the package without weakening
- **Traceability:** US-003
- **Ledger:** none
- **Statement:** When a source-reading test looks for a construct that the split moves, the test shall locate it across the `mapper` package (or follow the class to its declaring file) and shall assert no fewer properties than it asserts today.
- **Rationale (informative):** 17 test files read `app.py`'s source today (premise 3); path pins rot per extraction, and a weakened pin is the silent-failure mode Inc-0 exists to prevent (spike R-6).
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_hygiene.py tests/test_darkside_census.py tests/test_keymap.py tests/test_en5.py tests/test_en7.py tests/test_app_imports_used.py`
- **Numeric pass threshold:** exit code 0; the six files pass with assertion counts ≥ today's; the 14 `("mapper/app.py", line)` pins of `test_darkside_census.py` each resolve to exactly one home in the package.
- **Priority:** medium
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** the six generalised test files pass after every increment, and a moved construct is found by content, not by path.
  - **Shipped surface:** the test files themselves — the maintainer's reading of the suite's strength.
  - **Acceptance test(s):** AT-069
  - **Boundary catalog (QC-3):** ☑ empty — a construct absent from the whole package must fail the pin, not skip it ☑ boundary — a pinned string appearing in two homes must fail ("exactly one home") ☐ invalid ☑ error — a deleted or renamed construct.
  - **Negative control:** AT-069 is RED when one pinned darkside line is duplicated into a second module (two homes) and RED when one pin is deleted from the product. Executed at Phase 3.

### HLR-MOD.6 — B-02 is closed
- **Traceability:** US-003
- **Ledger:** none
- **Statement:** When the batch completes, no module under `mapper/screens/` shall hold any import of `mapper.app` except the sanctioned function-local read of the two patch names, and the four cycle-dodging function-local imports of B-02 shall be removed.
- **Rationale (informative):** the `screens → app` back-edge is the cycle ARCHITECTURE §3 bans; today four function-local imports dodge it (premise 6). The re-export direction (`app` importing `screens`) is the only legal edge.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_deps.py`
- **Numeric pass threshold:** exit code 0; 0 imports of `mapper.app` in `mapper/screens/**.py` other than function-local F4 reads; `factory.py`/`settings.py` hold module-level imports from `screens/common.py` and `screens/prompt.py`.
- **Priority:** medium
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** `grep -rn "import mapper.app" mapper/screens/` finds only the two sanctioned call-time reads; `screens/factory.py` and `screens/settings.py` import their helpers at module level.
  - **Shipped surface:** the shipped module files, read as source.
  - **Acceptance test(s):** AT-070
  - **Boundary catalog (QC-3):** ☐ empty ☑ boundary — the sanctioned exception is exactly the function-local F4 read; anything else fails ☐ invalid ☑ error — a module-level `import mapper.app` re-introduced anywhere under `screens/`.
  - **Negative control:** AT-070 is RED on today's tree (premise 6: four function-local imports of `mapper.app`) and RED when any one of them is restored after A2. Executed at Phase 3.

### HLR-MOD.7 — the §3 dependency rules are enforced by a test
- **Traceability:** US-001
- **Ledger:** none
- **Statement:** When the batch completes, the dependency rules ARCHITECTURE §3 declares for `screens/map`, `screens/common` + `screens/prompt`, `app` and `osopen` shall be enforced by a test over the shipped ASTs.
- **Rationale (informative):** the rules are the batch's own safety net — a module-level `mapper.app` import from the package would re-enter a partially-initialised module (spike R-8), and a concern importing a sibling concern module would recreate the coupling mechanism A removed.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_deps.py`
- **Numeric pass threshold:** exit code 0; all rules asserted: `screens/map` imports only its allow-list, never a sibling concern module, never `mapper.app` at module level; only `mapper.app` and `screens/repo.py` (`NavigationModel` only) import `screens/map`; `open_external` call sites ⊆ {`app`, `screens/map/opening`}.
- **Priority:** medium
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** the dependency table in ARCHITECTURE §3 cannot be violated without a red test.
  - **Shipped surface:** the module graph of `mapper/`, verified from the shipped ASTs.
  - **Acceptance test(s):** none new — the story's surface is the module graph, verified white-box by `tests/test_mod_deps.py` (TC); its acceptance evidence is AT-068/AT-070 passing on the same tree.
  - **Boundary catalog (QC-3):** none — a structural property of the import graph, no input class.
  - **Negative control:** `tests/test_mod_deps.py` is RED when a synthetic module-level `import mapper.app` is added to any `screens/map` module, and RED when a concern module imports a sibling concern. Executed at Phase 3 by mutation.

---

## 4. Low-level requirements (LLR)

> Each LLR decomposes an HLR into a verifiable property at the implementation level and
> maps to one increment of the cut (Inc-0, A1–A7, B0, B1–B11, B12).

### LLR-MOD.1.1 — the seven sibling-screen modules own their names (Spine A1–A7)
- **Traceability:** HLR-MOD.1
- **Ledger:** none
- **Statement:** `mapper/screens/common.py` shall own the shared helpers and hint-string constants, `screens/prompt.py` the four literal modals, `screens/construct.py` `ConstructScreen`, `screens/home.py` `HomeScreen`, `screens/repo.py` `RepoScreen`, `screens/plug_repo.py` `PlugRepoScreen` and `screens/import_preview.py` `_ImportPreviewScreen`, and each name shall be re-exported from `mapper/app.py`.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_structure.py -k spine_a`
- **Numeric pass threshold:** exit code 0; each of the 7 modules exists, defines its expected names, and `mapper.app.<name>` resolves to the same object (`is` identity through the re-export).
- **Negative control:** RED before A1 (files absent) and RED if a re-export is dropped. Executed at Phase 3.
- **Boundary catalog:** none — a property of the repository tree, no input class.

### LLR-MOD.1.2 — `MapScreen` lives in the package core (B0)
- **Traceability:** HLR-MOD.1
- **Ledger:** none
- **Statement:** `mapper/screens/map/__init__.py` shall re-export `MapScreen` and hold no logic, `mapper/screens/map/screen.py` shall define `class MapScreen` with the lifecycle concern, all class constants and `BINDINGS`, and `mapper/app.py` shall hold no `Screen` subclass other than `MapperApp` and no MapScreen concern method.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_structure.py -k b0`
- **Numeric pass threshold:** exit code 0; `inspect.getfile(MapScreen)` ends with `screens/map/screen.py`; `mapper/app.py` ≤ 400 lines.
- **Negative control:** RED before B0 (premise 7) and RED if any concern method remains in `app.py`. Executed at Phase 3.
- **Boundary catalog:** none — a property of the tree.

### LLR-MOD.1.3 — each concern method lives in its own module (B1–B11)
- **Traceability:** HLR-MOD.1
- **Ledger:** none
- **Statement:** `mapper/screens/map/screen.py` shall end with `class MapScreen(<11 mixins>, Screen)` and each of the 11 concern modules (`hints`, `exporting`, `opening`, `undo`, `focus_mode`, `editing`, `drafts`, `navigation`, `searching`, `panning`, `painting`) shall define exactly the methods its concern owns per the census, with `hints.py` also owning `MapHintLine`.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_structure.py -k spine_b`
- **Numeric pass threshold:** exit code 0; 11 mixin modules present; every method of the census roster assigned to exactly one module; `MapScreen.__mro__` contains the 11 mixins ahead of `Screen`.
- **Negative control:** RED before B1 and RED if any census method has no home or two homes. Executed at Phase 3.
- **Boundary catalog:** none — a property of the tree and the class.

### LLR-MOD.2.1 — `BINDINGS` and class constants live only on the core (B0, F3)
- **Traceability:** HLR-MOD.2
- **Ledger:** none
- **Statement:** `BINDINGS` and the core class constants (`KEY_SCOPE`, `PAN_STEP_X/Y`, `MIN_CANVAS_WIDTH`, `_FOCUS_REGIONS`, `REVEAL_MARGIN_CELLS`, `METER_STEPS`, `_TOAST_CHROME_CELLS`, `UNDO_DEPTH`, `EXPORT_*`, `_MINIMAP_*`) shall be declared only on the core `MapScreen` class and shall not be shadowed by any mixin.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_dispatch.py -k bindings`
- **Numeric pass threshold:** exit code 0; exactly 1 `BINDINGS` declaration across the 12 modules; 0 shadowed constants (`MapScreen.__dict__` holds each constant directly).
- **Negative control:** RED if `BINDINGS` is declared in any mixin (spike rule 1: keys silently drop). Executed at Phase 3 by mutation.
- **Boundary catalog:** ☑ error — a mixin-declared `BINDINGS` or shadowing constant.

### LLR-MOD.2.2 — method names are pairwise-disjoint across the map package (B1, guard, R-5)
- **Traceability:** HLR-MOD.2
- **Ledger:** none
- **Statement:** The twelve `mapper/screens/map/` modules shall declare pairwise-disjoint sets of method names, and no module under `mapper/screens/` shall bind `MAX_RENDER_NODES` or `refusal_sentence` at module level.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_dispatch.py -k disjoint`
- **Numeric pass threshold:** exit code 0; 0 pairwise intersections across the 12 modules' method sets; 0 module-level bindings of the two F4 names outside `mapper/app.py`.
- **Negative control:** RED when a method name is added to two mixins (spike rule 3: the handler would fire twice) and RED on a top-level `from mapper.app import MAX_RENDER_NODES` anywhere under `screens/`. Executed at Phase 3 by mutation.
- **Boundary catalog:** ☑ error — a duplicated handler name; an eager F4 binding.

### LLR-MOD.2.3 — actions and handlers dispatch through mixins with real keys (B1 spike)
- **Traceability:** HLR-MOD.2
- **Ledger:** none
- **Statement:** After the hints mixin moves, `MapScreen` shall dispatch `action_*` methods and `on_*` handlers resolved through the mixin bases exactly as before the move, demonstrated by a pilot-driven hint test pressing real keys.
- **Validation:** `test (e2e)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_dispatch.py -k pilot` (pilot test driving `MapperApp` with `pilot.press`)
- **Numeric pass threshold:** exit code 0; the hint line after a scripted key sequence equals the pre-B1 capture.
- **Negative control:** RED when the same `on_*` name is declared in two mixins (the handler runs twice and the hint drift shows in the capture). Executed at Phase 3.
- **Boundary catalog:** ☑ empty — the hints concern owns 0 shared attributes, so it exercises dispatch with no state coupling.

### LLR-MOD.3.1 — every name the tests import is re-exported (A1–A7, B0)
- **Traceability:** HLR-MOD.3
- **Ledger:** none
- **Statement:** `mapper/app.py` shall re-export every name imported from it by the test files and `screens/factory.py` — the 21 names of premise 10 — so that every `from mapper.app import X` site resolves to the moved definition.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_compat.py -k reexport`
- **Numeric pass threshold:** exit code 0; all 21 names resolve from `mapper.app` with object identity to their defining module.
- **Negative control:** RED if any one re-export is removed. Executed at Phase 3.
- **Boundary catalog:** ☑ empty — the import census itself (21 names) bounds the set; a zero-name census cannot pass.

### LLR-MOD.3.2 — the two patch names are read lazily (A1, B9)
- **Traceability:** HLR-MOD.3
- **Ledger:** none
- **Statement:** `_path_refusal` in `screens/common.py` and `_search_order`/`_walk_hits` in `screens/map/searching.py` shall read `refusal_sentence` and `MAX_RENDER_NODES` at call time through a function-local `import mapper.app`, so the six monkeypatch sites of premise 4 keep biting.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_compat.py tests/test_search.py -k max_render_nodes` and `python -B -m pytest -q -p no:cacheprovider tests/test_inc9q.py -k cr_f1`
- **Numeric pass threshold:** exit code 0; the patched-limit and patched-sentence assertions pass on the shipped module objects.
- **Negative control:** RED when the eager-binding mutant is applied (patch stops biting while the suite otherwise passes — the silent-failure mode). Executed at Phase 3.
- **Boundary catalog:** ☑ boundary — the patched limit exactly one node below the map size.

### LLR-MOD.4.1 — the full suite stays green at every increment gate
- **Traceability:** HLR-MOD.4
- **Ledger:** none
- **Statement:** At every increment gate of the batch and at P4, the full test suite shall pass with zero failures and no test file edited to weaken a behaviour assertion.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/` (per increment gate and at P4).
- **Numeric pass threshold:** exit code 0; 0 failed (baseline at P0: 2941 passed / 3 xfailed / 0 failed, PLAN test ledger).
- **Negative control:** any behaviour drift in the moved code reddens the suite; the byte-identical method-body check (AST dump of moved bodies before/after each move) is the increment-local RED side. Executed per increment.
- **Boundary catalog:** none — a property of the suite.

### LLR-MOD.4.2 — painted output equals the pre-split capture (all increments)
- **Traceability:** HLR-MOD.4
- **Ledger:** none
- **Statement:** `tests/test_mod_parity.py` shall capture the painted screen after each step of a scripted session — open a map, move, search, toggle a view, export, quit — at terminal widths 118 and 87 columns, before the first move (B0) and after the batch, and the two captures shall be byte-equal.
- **Validation:** `test (e2e)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_parity.py`
- **Numeric pass threshold:** exit code 0; 0 painted-line diffs across all scripted steps at both widths.
- **Negative control:** RED when any one shipped string/key/layout cell is mutated in a product copy. Executed at Phase 3.
- **Boundary catalog:** ☑ boundary — widths 118 and 87 exercise wide and truncated layouts.

### LLR-MOD.5.1 — the six source-reading tests generalise to the package (Inc-0)
- **Traceability:** HLR-MOD.5
- **Ledger:** none
- **Statement:** `test_draft_hygiene.py`, `test_darkside_census.py`, `test_keymap.py`, `test_en5.py`, `test_en7.py` and `test_app_imports_used.py` shall locate their pins by content across `mapper/**/*.py` (or via `inspect.getfile(MapScreen)`) instead of by `app.py` path, before any code moves, and their assertion counts shall be no lower than today.
- **Validation:** `test (integration)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_hygiene.py tests/test_darkside_census.py tests/test_keymap.py tests/test_en5.py tests/test_en7.py tests/test_app_imports_used.py`
- **Numeric pass threshold:** exit code 0; each of the 14 darkside pins resolves to exactly one home; the MapScreen arms of `test_draft_hygiene.py` parse `inspect.getfile(MapScreen)`.
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
- **Ledger:** none
- **Statement:** `screens/factory.py` shall import `keybar_groups`, `_save_or_toast` and `_PromptScreen`, and `screens/settings.py` shall import `keybar_groups`, at module level from `screens/common.py` and `screens/prompt.py`, and the four function-local imports of premise 6 shall be deleted.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_deps.py -k b02`
- **Numeric pass threshold:** exit code 0; 0 function-local `import mapper.app` outside the sanctioned F4 reads; module-level helper imports present in factory/settings.
- **Negative control:** RED on today's tree (premise 6) and RED if any one import is restored. Executed at Phase 3.
- **Boundary catalog:** ☑ error — a restored cycle-dodging import.

### LLR-MOD.6.2 — no module-level `mapper.app` import from the package (B0, all increments)
- **Traceability:** HLR-MOD.6
- **Ledger:** none
- **Statement:** No module under `mapper/screens/` shall import `mapper.app` at module level at any point in the batch; the only sanctioned import shape is the function-local call-time read of the two F4 names.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_deps.py -k no_app_import`
- **Numeric pass threshold:** exit code 0; 0 module-level `mapper.app` imports under `mapper/screens/`.
- **Negative control:** RED when a module-level `import mapper.app` is added to any package module (spike R-8: re-entry into a partially-initialised module). Executed at Phase 3 by mutation.
- **Boundary catalog:** ☑ error — the module-level import shape.

### LLR-MOD.7.1 — the amended §3 dependency rules hold (B3, B12)
- **Traceability:** HLR-MOD.7
- **Ledger:** none
- **Statement:** The AST-derived dependency test shall assert: `screens/map` imports only its §3 allow-list and never a sibling concern module; only `mapper.app` and `screens/repo.py` (`NavigationModel` only) import `screens/map`; `screens/common` and `screens/prompt` import neither `app` nor `widgets` internals; `open_external` is called only from `app` and `screens/map/opening`.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_deps.py -k arch`
- **Numeric pass threshold:** exit code 0; all four rule groups asserted against the shipped ASTs.
- **Negative control:** RED on a synthetic sibling-concern import and RED before B3 (the osopen allow-list then names a file that does not exist yet — the test is scoped to land with B3). Executed at Phase 3.
- **Boundary catalog:** ☑ error — each banned import shape.

### LLR-MOD.7.2 — the F1/F2 freeze is mechanical (B12)
- **Traceability:** HLR-MOD.7
- **Ledger:** none
- **Statement:** `tests/test_mod_census.py` shall re-run `census/ast_census.py` over the package and diff the result against `census.json`, so any attribute gaining a writer concern, any new cross-concern attribute, or any F2 name/signature drift goes red without a census amendment.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_mod_census.py`
- **Numeric pass threshold:** exit code 0; census diff empty.
- **Negative control:** RED when a synthetic writer is added to a second concern for any F1 attribute. Executed at Phase 3.
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
SOURCE: the monkeypatch sites (tests/test_search.py ×5, tests/test_inc9q.py ×1)
NODES: the function-local module-object reads (LLR-MOD.3.2, LLR-MOD.2.2)
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
> - **Layer A — white-box / functional (`TC-NNN`):** the structure test `tests/test_mod_structure.py` (LLR-MOD.1.1–1.3), the dispatch guard `tests/test_mod_dispatch.py` (LLR-MOD.2.1–2.3), the compatibility test `tests/test_mod_compat.py` (LLR-MOD.3.1–3.2), the dependency test `tests/test_mod_deps.py` (LLR-MOD.6.1–6.2, LLR-MOD.7.1) and the census-diff test `tests/test_mod_census.py` (LLR-MOD.7.2). The full suite at every increment gate is LLR-MOD.4.1's Layer A.
> - **Layer B — black-box / behavioral acceptance (`AT-NNN`):**
>   - AT-065 (`tests/test_mod_parity.py`) drives the real app with real keys at 118 and 87 columns and compares painted output against the pre-split capture (story 2).
>   - AT-066 (`tests/test_mod_dispatch.py -k pilot`) drives a bound action and an `on_*` handler through the mixins with real keys (story 2 / mechanism A).
>   - AT-067 (`tests/test_mod_compat.py -k patch_surface`) observes the patched refusal/limit through the shipped screens (story 3).
>   - AT-068 (`tests/test_mod_structure.py`) reads the shipped repository tree — story 1's surface (story 1).
>   - AT-069 (the six Inc-0 test files) observes that moved constructs are found by content across the package (story 3).
>   - AT-070 (`tests/test_mod_deps.py -k b02`) greps/ASTs the shipped `screens/` tree for the closed B-02 (story 3).

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
- **F4 lazy reads.** The two patch names are read through a function-local `import mapper.app` at call time; an eager binding would silently kill the patches (LLR-MOD.3.2, LLR-MOD.2.2).
- **Inc-0 first.** The six source-reading tests generalise before any code moves, so no extraction increment ever runs red against a stale pin (spike R-6).

### 6.3 Open risks
- **R-1 (silent double dispatch):** an `on_*` name in two mixins runs twice. Guarded by LLR-MOD.2.2/LLR-MOD.2.3; B1 is the pilot spike. If a future Textual change alters MRO dispatch, the guards redden first.
- **R-2/R-3 (shared state and funnels):** 30 shared attributes, 15 multi-writer; `refresh_canvas` has 25 call sites in 9 concerns. Mitigation: `self.*` semantics kept byte-identical; F1/F2 frozen and made mechanical by LLR-MOD.7.2.
- **R-4 (patch surface):** guarded by LLR-MOD.3.2 and the LLR-MOD.2.2 eager-binding ban; the failure mode is silent, so both guards are executable, not conventions.
- **R-5 (silent import/name drift):** one guard test (LLR-MOD.2.2) asserts disjoint names and the F4 ban together.
- **R-6 (pin rot):** mitigated by Inc-0 ordering (LLR-MOD.5.1); if a pin is found to be ungeneralisable, the fallback recorded in the proposal is Spine A only — a strictly weaker outcome, returned to the trunk as an A3, not improvised in a lane.
- **R-7 (CSS selector drift):** no class is renamed during any move; AT-065 catches a styling break as a painted diff.
- **R-8 (import cycle):** Spine A lands helper homes before B0; LLR-MOD.6.2 bans the module-level edge.
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
