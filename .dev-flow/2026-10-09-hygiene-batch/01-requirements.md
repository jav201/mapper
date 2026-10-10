# Requirements Document — mapper — Batch 2026-10-09-hygiene-batch

> **Artifact language**
> This template is the canonical **English scaffold**. Generate the artifact in the batch's development language (`state.json` `language`). For Spanish batches, translate the **prose** — section headers and guidance — **and never a label**, and use `deberá` as the normative keyword (≡ `shall`). The normative RULES in this preamble are **language-independent** and enforced regardless of artifact language.

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/docs/req-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

> **Reserved field names.** The **field names and block keywords below are language-independent** — the
> validator parses them literally and they are never translated:
> `Validation` · `Acceptance test(s)` · `Boundary catalog` · `Negative control` · `Premise evaluation` · `Fork preconditions` · `Ledger` · `Requirement` · `⏸ DEFER`
> Everything else on this page — headings, guidance, the prose in every cell — is translated with the batch.
> **One strategy, not two:** the flow ships no alias table, so a translated label is read as an ABSENT one and the rule keyed on it reports a true-sounding silence.
> **And one FLOW-WIDE reserved token, read out of this artifact by `V42` no matter which template minted it:** `⏸ DEFER`. It is a MARKER rather than a field name, which is why it is stated here *and* in `/dev-flow` §Language of artifacts rather than in a per-template list — a deferral can be written in any batch artifact, including the ones that carry no block at all.

---

## 1. Introduction

### 1.1 Purpose
This batch closes two small debts left by earlier batches:
- **B-103:** the draft-save code hygiene that the data-safety DDR and code review recorded as LOWs.
- **B-99:** the Inc-9g mutant-record debt `INC9G-R8`.

### 1.2 Scope
In scope:
- `mapper/app.py`: a typed failed-save error slot on `MapScreen`, a public read of "is a draft guard open", and the ruling on F5;
- one structural test;
- the executed re-verification of the `INC9G-R8` witness on today's master, plus the backlog record.

Out of scope: any change a user can see (strings, keys, layout), the accepted draft-model residuals (B-102), and any other backlog item.

### 1.3 Definitions, acronyms, abbreviations
| Term | Definition |
|------|------------|
| draft guard | the save · discard · stay modal (`DraftGuardScreen`) that a map screen pushes before an exit drops a draft |
| quit walk | `MapperApp.action_quit`'s walk over every map screen that holds a draft (`2026-10-08-data-safety-batch`, LLR-003.5) |
| `HOME-1` | the Inc-9h mutant that deletes the home screen's `on_mount` hint refresh; it is the reviewer's `R8` of Inc-9g |

### 1.4 References
- `.dev-flow/BACKLOG.md`, rows B-99 and B-103.
- `.dev-flow/2026-10-08-data-safety-batch/` (the DDR and the code-review LOWs).
- `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-033-inc9g.md` (its 2026-10-01 correction) and `increment-034-inc9h.md` §4.

### 1.5 Document overview
- §2: stories, premises and fork preconditions.
- §3: HLR, with their acceptance tests.
- §4: LLR and the IFC.
- §5: validation strategy.

---

## 2. Overall description

### 2.1 Product perspective
The change is internal to the map screen and to the app's quit path. No new module is created, and only one module (`mapper/app.py`) changes.

### 2.2 Product functions
No new function. The failed-draft-save toast and the quit walk keep their shipped behaviour. What changes is how the code reads them: it no longer depends on an untyped attribute or on another class's private field.

### 2.3 User characteristics
The maintainer of mapper (the operator), who reads and changes `app.py`.

### 2.4 Constraints
- **Behaviour-preserving.** No string, key, colour or layout changes. A TUI design change would need a prototype verdict, and none is wanted here.
- **Increment size.** At most 4 source files per increment.
- **Platform.** Python 3.11/3.12, Textual 8.2.8.

### 2.5 Assumptions and dependencies
The two existing nodes named as acceptance below stay green on master today. This was checked in §2.7.

### 2.6 Source user stories

| ID | User Story | Source | DoR status |
|----|------------|--------|------------|
| US-001 | As the maintainer, I want the failed-save error and the "guard is open" state read through declared, public members, so that a rename or a new screen type cannot silently break the failed-save toast or the quit walk. | B-103 (data-safety DDR / code-review LOWs) | READY |
| US-002 | As the operator, I want the `INC9G-R8` record debt closed only on executed evidence, so that the backlog neither carries a debt that was already paid nor closes one that was not. | B-99 (ui-next-batch-02 validation gap `INC9G-R8`) | READY |

#### Refinement log (one block per story)

**US-001 — declared members for the draft-save path**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = maintainer · outcome = the failed-save toast and the quit walk behave as shipped, read through declared members · why = B-103's three LOWs · out of scope = any visible change.
- **Feasibility (E, S):** implementation path = declare `MapScreen._last_save_error: str | None` in `__init__` and read it directly; add `MapScreen.guard_open()`; `action_quit` calls it · dependencies/unknowns = none · fits one batch? = yes, one increment.
- **Evaluability (T) — behavioral, black-box:** two criteria, both observed through the shipped map screen:
  - "When a draft save fails, the operator sees `could not save '<map>' (<ErrorType>) · draft kept · ctrl+s to retry`."
  - "When `ctrl+q` is pressed while a node guard is already up, the quit walk does not stack a second guard and does not wedge."
- **Open questions:** F5 — `toast=False` also suppresses `_refusal_toast`'s `MapIdError` text. Ruled in §6.2 (no change).
- **Classification:** `READY`.

**US-002 — `INC9G-R8` closed on evidence**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = operator · outcome = B-99 is closed with an executed mutation transcript, or reopened as real work · why = the ui-next-batch-02 validation (2026-10-08) still lists `INC9G-R8` as open, while `increment-034-inc9h.md` (2026-10-01) already records the witness and the kill · out of scope = re-running the rest of the Inc-9g battery.
- **Feasibility (E, S):** implementation path = apply `HOME-1` to a copy of master, run the witness, restore, byte-compare · dependencies = none · fits one batch? = yes.
- **Evaluability (T) — behavioral, black-box:** "When the home screen is visited again after the maps on disk changed, the operator sees the hint follow the maps." The witness drives the shipped home screen, and the mutation shows it goes RED without the refresh.
- **Open questions:** none.
- **Classification:** `READY`.

### 2.7 Premise evaluation (C-43) — MANDATORY, one row per premise

| # | Premise, as a truth-apt proposition | Tier | Verdict | Executed evidence (command output / `file:line` — **NOT** a citation of another document) | Disposition |
|---|---|---|---|---|---|
| 1 | `_last_save_error` is read with `getattr` and never declared on `MapScreen` | executed | ✅ TRUE | `grep -n _last_save_error mapper/app.py` → `299: screen._last_save_error = type(e).__name__` and `3565: getattr(self, "_last_save_error", "")`, no declaration | in scope (LLR-001.1) |
| 2 | `MapperApp.action_quit` reads `MapScreen._draft_guard_open` from outside the class | executed | ✅ TRUE | `mapper/app.py:5217` `if screen._draft_guard_open:` inside `MapperApp` | in scope (LLR-001.2) |
| 3 | the `INC9G-R8` witness exists on master and the mutated line is still present | executed | ✅ TRUE | `tests/test_inc9h.py:504` defines `test_inc9h_cr_f2_the_home_hint_follows_the_maps_when_the_screen_resumes`; `mapper/app.py:786` holds `self.query_one(HintLine).set_hint(home_hint(bool(mmd_files)))` | in scope (LLR-002.1) |
| 4 | no test reads `_draft_guard_open` or `_last_save_error` (B1 probe) | executed | ✅ TRUE | `grep -rn "_draft_guard_open\|_last_save_error" tests --include=*.py` → no output | B1 not fired |

- **Premise evaluation:** 4 premise(s) · 4 ✅ TRUE / 0 ❌ FALSE / 0 ❓ UNDECIDABLE

### 2.8 Fork preconditions (C-52) — MANDATORY, and the declared empty when the batch does not fork

| # | Condition (`C-52`) | Discharged? | The executed evidence |
|---|---|---|---|
| 1 | **Frozen contract** | ✅ | one lane; no lane boundary exists |
| 2 | **Disjoint FILE sets** | ✅ | one lane |
| 3 | **Crossed reverse census** | ✅ | one lane |
| 4 | **One owner of the trunk** | ✅ | the orchestrator |

- **Fork preconditions:** none — this batch runs one lane

---

## 3. High-level requirements (HLR)

### HLR-001 — the draft-save path reads declared, public members
- **Traceability:** US-001
- **Ledger:** LED-2026-10-09-hygiene-batch.1, LED-2026-10-09-hygiene-batch.4, LED-2026-10-09-hygiene-batch.5
- **Statement:** When a draft save fails, or when the quit walk reaches a map screen, the system shall read the failure's error type and the screen's guard state through members that `MapScreen` declares, and shall keep the shipped failed-save toast and quit-walk behaviour unchanged.
- **Rationale (informative):**
  - A `getattr` default hides a renamed attribute behind the word `error`.
  - A private read across classes breaks silently when `MapScreen` changes its bookkeeping.
- **Validation:** `test`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_save.py tests/test_draft_exits.py tests/test_draft_hygiene.py`
- **Numeric pass threshold:** exit code 0; 0 failed.
- **Priority:** low
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:**
    - A failed `ctrl+s` shows exactly one toast: `could not save '<map>' (OSError) · draft kept · ctrl+s to retry`.
    - `ctrl+q` over an open node guard stacks no second guard, and a later `ctrl+q` still asks.
  - **Shipped surface:** the map screen's toast and the draft guard modal.
  - **Acceptance test(s):** AT-060, AT-061
  - **Boundary catalog (QC-3):** ☐ empty ☑ boundary — a guard already open when the walk arrives (AT-061) ☐ invalid ☑ error — a save that raises (AT-060).
  - **Negative control:** executed at Phase 3.
    - AT-060 goes RED when `_save_draft` reads a fixed text instead of the recorded type: the toast then reads `(error)`.
    - AT-061 goes RED when the walk ignores the open guard. `_guard_draft` then returns without calling `proceed` or `on_hold`, so the walk never ends. The later `ctrl+q` returns early and opens no guard, so `_guards(app) == 1` fails with 0 at the second assertion.
    - Two mutants are owed at Phase 3, each with its failing line recorded: (1) `action_quit` drops the open-guard check; (2) `guard_open()` returns a constant `False`.
  - **Tagging:** an existing node becomes an acceptance test when its docstring names the AT id: `AT-060` in `test_draft_save.py`, `AT-061` in `test_draft_exits.py`, `AT-062` in `test_inc9h.py`. Those three test files are touched for the tag only; the fourth test file, `tests/test_draft_hygiene.py`, is new. Tests are not capped by the 4-source-file rule, and the one source file is `mapper/app.py` (LED-2026-10-09-hygiene-batch.5).
  - **Regression set:** `tests/test_draft_save.py`, `tests/test_draft_exits.py`, `tests/test_inspector.py` and `tests/test_inc9h.py`. They run at the increment gate, before the full suite at P4.

### HLR-002 — the `INC9G-R8` debt is closed on an executed kill
- **Traceability:** US-002
- **Ledger:** none
- **Statement:** When B-99 is closed, the system's test suite shall hold a witness that goes RED under `HOME-1` on the current master, and the backlog row shall cite that executed run.
- **Rationale (informative):** the ui-next-batch-02 validation recorded the debt after Inc-9h had already paid it. Closing the item on a document citation would repeat the very defect B-99 is about.
- **Validation:** `test`
- **Executed verification:** the `HOME-1` mutation run (Phase 3 transcript), then `python -B -m pytest -q -p no:cacheprovider tests/test_inc9h.py -k cr_f2`.
- **Numeric pass threshold:** the witness reports 1 failed under the mutant and 1 passed after the byte-identical restore (sha256 equal).
- **Priority:** low
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** after saving a map and returning to home, the `↵` pair is in the hint. After deleting the map and returning, it is absent.
  - **Shipped surface:** the home screen's hint line.
  - **Acceptance test(s):** AT-062
  - **Boundary catalog (QC-3):** ☑ empty — no maps on disk ⇒ no `↵` pair ☑ boundary — the maps change between two visits ☐ invalid ☐ error.
  - **Negative control:** `HOME-1` (the `on_mount` refresh line removed) turns AT-062 RED. Executed at Phase 3.

---

## 4. Low-level requirements (LLR)

> Each LLR decomposes an HLR into a verifiable property at the implementation level.

### LLR-001.1 — `MapScreen` declares the failed-save error slot
- **Traceability:** HLR-001
- **Ledger:** LED-2026-10-09-hygiene-batch.2, LED-2026-10-09-hygiene-batch.3
- **Statement:** `MapScreen.__init__` shall declare `_last_save_error: str | None = None`, and `MapScreen._save_draft` shall read it without `getattr`, falling back to `error` when it is `None`.
- **Writers outside `MapScreen` (reverse census):**
  - `_save_or_toast` (`app.py:299`) still writes the slot on whatever screen calls it. Two such callers exist: `screens/factory.py:219` (the factory screen) and `app.py:1167` (`_ImportPreviewScreen`, the CSV "save as").
  - Nothing reads the slot on those screens, so the write stays as it is. A comment at `:299` says the slot is declared on `MapScreen` and is advisory elsewhere.
  - **What would change this:** if a non-`MapScreen` screen ever reads the slot, the slot moves to a shared base, or the helper returns the error type.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_hygiene.py -k last_save_error`, with two checks:
  - (a) behaviour: a `MapScreen` opened through the app holds `_last_save_error is None` before any save;
  - (b) AST: `MapScreen.__init__` holds an annotated assignment to `self._last_save_error`, and no `getattr(..., "_last_save_error", ...)` call remains in `mapper/`.
  - A read through `vars()` or `__dict__` is not detected by (b). That limit is stated here, not claimed away.
- **Numeric pass threshold:** exit code 0.
- **Negative control:** both checks are RED on today's code: there is no declaration, and `app.py:3565` reads the slot through `getattr`. Executed at Phase 3.
- **Boundary catalog:** none — a property of the class and its source, no input class.

### LLR-001.2 — the quit walk reads the guard state through `MapScreen.guard_open()`
- **Traceability:** HLR-001
- **Ledger:** LED-2026-10-09-hygiene-batch.3
- **Statement:** `MapScreen` shall expose `guard_open() -> bool`, and no code outside `MapScreen` shall read `_draft_guard_open`.
- **Validation:** `test (unit)`
- **Executed verification:** `python -B -m pytest -q -p no:cacheprovider tests/test_draft_hygiene.py -k guard_open`, with two checks:
  - (a) behaviour, through real keys: `guard_open()` is `False` before the guard opens, `True` while it is up, and `False` after it is answered;
  - (b) AST over every module in `mapper/`: no attribute read of `_draft_guard_open` outside the `MapScreen` class body, and `MapperApp.action_quit` calls `guard_open`.
- **Numeric pass threshold:** exit code 0.
- **Negative control:** RED on today's code: `guard_open` does not exist, and `MapperApp.action_quit` reads `screen._draft_guard_open` (`app.py:5217`). Executed at Phase 3.
- **Boundary catalog:** none — a property of the class and its source, no input class.

### LLR-002.1 — the `HOME-1` mutant is killed on master
- **Traceability:** HLR-002
- **Ledger:** none
- **Statement:** The witness `test_inc9h_cr_f2_the_home_hint_follows_the_maps_when_the_screen_resumes` shall fail with the `HomeScreen.on_mount` hint-refresh line removed, and pass with it restored.
- **Validation:** `test (integration)`
- **Executed verification:** the Phase 3 mutation transcript (`evidence/b99-home1-mutation.transcript`).
- **Numeric pass threshold:** 1 failed under the mutant; 1 passed after restore; sha256 before = after.
- **Negative control:** the mutation itself is the RED side.
- **Boundary catalog:** none — one mutant, no input class.

### Information Flow Contract (IFC) — C-54

- **Part A — flows:**

```
FLOW failed-draft-save-error
SOURCE: MapStore.save raises inside _save_or_toast
NODES: MapScreen._last_save_error (LLR-001.1)
SINK: the failed-save toast text built in MapScreen._save_draft
```

```
FLOW quit-walk-guard-state
SOURCE: MapScreen._guard_draft sets and clears the guard flag
NODES: MapScreen.guard_open (LLR-001.2)
SINK: MapperApp.action_quit's step decision
```

- **Part B — boundary decomposition:** no. The change is internal to one module, and no component of the boundary is addressable on its own.

---

## 5. Validation strategy

### 5.1 Methods

> **Two layers** (per the Two-layer validation rule).
> - **Layer A — white-box / functional (`TC-NNN`):** the structural test `tests/test_draft_hygiene.py` (LLR-001.1, LLR-001.2) and the `HOME-1` mutation run (LLR-002.1).
> - **Layer B — black-box / behavioral acceptance (`AT-NNN`):** AT-060 and AT-061 drive the map screen with real keys; AT-062 drives the home screen.

### 5.2 Batch acceptance criteria
- 100% of LLRs are covered by at least one executed check with a pass result.
- Every AT is executed GREEN, each with an executed RED counterfactual.
- The full suite is green at the P4 gate (0 failed).
- There are 0 user-visible changes: no string, key or layout diff.

---

## 6. Appendices (optional)

### 6.1 Extended glossary
### 6.2 Relevant design decisions
- **F5 (the third B-103 LOW) — no change** (LED-2026-10-09-hygiene-batch.4). `_save_or_toast(toast=False)` suppresses `_refusal_toast`'s `MapIdError` text on a draft save. Reasons:
  - **The case is unreachable.** `store.load` and `store.save` run the same pure `check_map_id` on the same id (`mapper/store.py:681`, `:810`). A map whose id the rule refuses never opens, so it never holds a draft.
  - **The current toast is already honest and safe.** It still names the error type (`MapIdError`) and keeps the draft.
  - **Letting the refusal text through would add a second toast.** Preventing that is exactly why `toast=False` exists.

  Recorded here, and closed together with B-103.
### 6.3 Open risks
- None beyond the external `V7` (the installed flow bundle differs from its manifest; this is not about this project).
- **Security questions (`devflow-scan-spec.py` flagged `expose`, C7).** The flag is a false positive, and the reasons below are checked against the change:
  - "Expose" in LLR-001.2 means a Python method on `MapScreen` (`guard_open()`). It is not a network surface.
  - The change opens no port, socket or file.
  - It reads no new input, and it handles no secret or user data.
  - No auth, external integration or destructive store call is touched (C1–C7 none).
  - No text reaches markup (C8 none).
### 6.4 Phase-1 reconciliation log — moved to the ledger (§7)

### 6.5 Requirement amendments — moved to the ledger (§7)

---

## 7. The ledger — authored as a SEPARATE FILE

The fence below is the ledger's seed: `devflow-init.py` writes it to `01-requirements-ledger.md`. The shape of an entry is in the field guide.

```markdown
# Requirements ledger — mapper — Batch 2026-10-09-hygiene-batch

> Append-only. Entries are added in chronological order and never rewritten. The live
> contract is `01-requirements.md`; this file records how it came to say what it says.
> Every entry names the requirement it amends; every requirement names its entries. `V26`
> compares the two sets of pairs both ways.

_No entries yet. The first amendment to the live contract writes the first one, in the
shape the field guide's §7 shows (`req-template.md` in the guide directory init prints), and nothing
above this line is ever edited._
```
