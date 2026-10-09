# Increment 002 — US-001 / HLR-003 · `Draft guard modal and the draft seat scope`

> Batch-plan name: **Inc-1a**. The file is `increment-002.md` because it is the second increment packet written into this batch's `03-increments/` home (`increment-001.md` is Inc-3).

| Field | Value |
|---|---|
| Batch | `2026-10-08-data-safety-batch` |
| Increment | `002` (plan name Inc-1a) |
| Lane (if the batch forked) | none · worktree `mapper-inc1a`, branch `inc1a/draft-guard`, based on Inc-3's tip `80635a1` |
| Requirement(s) | US-001 · HLR-003 · LLR-003.1 · design rows 1a.1–1a.3 · verdict R4, R9 · PDR conditions C9, C13, C14 (Inc-1a parts) |
| Acceptance | AT-015 (modal-level part only; the AT through `j` is Inc-1b) · white-box TC-003.1 · unit — none beyond the TC-003.1 nodes |
| Agent | `software-dev` |
| Date | 2026-10-08 |

---

## 1 · What changed

The `save · discard · stay` guard modal exists and is bound from a new `draft` modal seat scope. `DraftGuardScreen` dismisses with exactly `"save"`, `"discard"` or `"stay"` (`s`, `d`, `esc`), paints `unsaved draft on «{title}» · {map_id}` with both parts through `darkside.plain` and `markup=False` (R9), and reads its hint row from the seat. Nothing pushes it yet (intermediate state inside one branch, R-10). Two existing census tests were updated because the seat legitimately gained three rows, and `CHROME_LEXICON` gained four words. 3 source files, 17 new nodes of its own plus 6 parametrised arms that appear because the seat grew.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/keymap.py` | source | HLR-003, LLR-003.1, design 1a.1, R4 | `SCOPE_DRAFT`; `GROUP_SCOPE["draft"]` before `"app"`; `GROUP_HEADER["draft"] = "unsaved"`; `MODAL_SCOPES` + `SCOPE_DRAFT`; rows `s`/`d`/`esc` -> `save`/`discard`/`stay`, no `priority` |
| `mapper/screens/draft_guard.py` | source | HLR-003, LLR-003.1, design 1a.2, R4, R9 | new `DraftGuardScreen(ModalScreen[str])` |
| `mapper/screens/__init__.py` | source | HLR-003, design 1a.3 | import + `__all__` |
| `tests/test_draft_save.py` | test | LLR-003.1, TC-003.1, AT-015 (modal part), C13, E-1, E-5 | new, 13 nodes |
| `tests/test_data_safety_census.py` | test | LLR-003.1, E-7, design §5.3 | new, 4 nodes; `DATA_SAFETY_ADDED` (3 rows) |
| `tests/test_inc9.py` | test | HLR-003, design §5.3 (c), C14 | `test_cd25a_…` subtracts `DATA_SAFETY_ADDED` from `after` (stays a statement about Inc-9); `CHROME_LEXICON` + `discard draft stay unsaved` |
| `tests/test_keymap.py` | test | LLR-003.1, design §5.3 (c) | `SCOPE_OWNER[draft] = DraftGuardScreen`; `EXPECTED_PER_SCOPE[draft] = 3` |
| `tests/test_key_dispatch.py` | test | LLR-003.1, design §5.3 (b) | `EXPECTED_SEAT` + 3 `draft` rows; docstring "all 48 entries" -> "every entry" |
| `.dev-flow/2026-10-08-data-safety-batch/evidence/inc1a-*` (4 files) | doc | | mutation driver + 3 transcripts |
| `.dev-flow/2026-10-08-data-safety-batch/03-increments/increment-002.md` | doc | | this packet |

| Count | Value |
|---|---|
| **SOURCE files** | **3** / 4 (no overage, no ⚠) |
| Test files | 5 (2 new, 3 edited; uncapped) |
| Doc files | 5 (outside the count) |

**Why the existing tests changed.** `test_inc9.py::test_cd25a_…` compares the live seat to Inc-9's pinned entry rows and would now see three extra `draft` rows; it subtracts the batch's declared rows (pinned against the live seat by the new census) rather than widening Inc-9's list. `test_keymap.py` and `test_key_dispatch.py` pin the seat exactly by design and are meant to be edited with the seat. `test_inc9.py::test_a112_the_chrome_is_english[seat]` failed on the new labels (`discard`, `stay`) and the group id/header (`draft`, `unsaved`); the lexicon is "a deliberate edit in the commit that paints it", so the four words were added there. `tests/test_inc4_census.py:62` reads the map scope only and does not move in Inc-1a (Inc-1b).

---

## 3 · How to test

```bash
cd <worktree>   # mapper-inc1a
python -B -W error::SyntaxWarning -m pytest -q -rf -p no:cacheprovider tests/test_draft_save.py tests/test_data_safety_census.py tests/test_keymap.py tests/test_key_dispatch.py
python -B -W error::SyntaxWarning -m pytest -q -rf -p no:cacheprovider tests/test_inc9.py tests/test_inc9e.py tests/test_darkside_census.py tests/test_a3_census.py tests/test_inc4_census.py tests/test_no_operator_paths.py tests/test_confirm_markup.py
python -B .dev-flow/2026-10-08-data-safety-batch/evidence/inc1a-mutate.py red            # base-tree counterfactual
python -B .dev-flow/2026-10-08-data-safety-batch/evidence/inc1a-mutate.py K-d-swap       # one mutant: apply, run, restore, sha-verify
python -B -W error::SyntaxWarning -m pytest -q -rf -p no:cacheprovider                    # default lane, ~24 min
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** TC-003.1 | `core` · `full` | `test_draft_save.py`: `test_llr_003_1_modal_returns_the_token_for_each_key[s,d,escape]`, `…an_unbound_key_answers_nothing`, `…the_title_follows_the_ruled_wording`, `…modal_title_is_literal_and_plain[esc,click-markup,surrogate]`, `…a_markup_payload_in_the_title_is_painted_literally`, `…the_hint_row_is_read_from_the_draft_seat`, `…the_hint_follows_the_seat_not_a_literal` | 11 passed |
| **A · white-box** LLR-003.1 | `core` · `full` | `…the_screen_bindings_are_generated_from_the_seat`, `…app_chords_do_not_pass_through_the_guard`; `test_data_safety_census.py` x4 | 6 passed |
| **B · black-box** AT-015 | `core` · `full` | n/a — Inc-1b owns AT-015 through `j` (the guard is not pushed yet). The modal-level title oracle (C13) is the Layer-0 `modal_title_is_literal_and_plain` | n/a |

Touched files: 151 passed in the four seat/modal files; the census/related files (7 files) 106 passed after the lexicon edit; `test_inc9.py`+`test_inc9e.py` 57 passed. Python 3.12.7, Textual 8.2.8, executed.

**Default lane (executed once, whole tree, at the final code `8120a24`):** `python -B -W error::SyntaxWarning -m pytest -q -rf -p no:cacheprovider` finished `2828 passed, 24 deselected, 3 xfailed in 1424.00s (0:23:43)`, `EXIT_CODE=0`. Zero failures (Inc-3's `test_at_p07` failure is fixed on this branch's base). The "Task was destroyed but it is pending" lines after the summary are Textual timer teardown noise at interpreter exit. Transcript: `evidence/inc1a-default-lane.transcript`.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | base tree for the three source files: `mapper/keymap.py` and `mapper/screens/__init__.py` replaced by their `HEAD` blobs (`git show HEAD:<path>`), `mapper/screens/draft_guard.py` moved aside (move-aside, C-20; no stash, no checkout); the committed tests unchanged |
| Instrument | project code: `evidence/inc1a-mutate.py red` |
| Where it ran | my own worktree `mapper-inc1a` |
| Transcript | `evidence/inc1a-red-counterfactual.transcript`: 5 FAILED + 2 collection ERRORs, `5 failed, 32 passed, 2 errors`. FAILED: `test_data_safety_census.py` x4 and `test_key_dispatch.py::test_at_n03h_the_whole_seat_matches_its_specification`. ERROR (collection, `ModuleNotFoundError: No module named 'mapper.screens.draft_guard'`): `tests/test_draft_save.py` (all 13 nodes) and `tests/test_keymap.py` (so its draft params) |
| Restore proven by | before/after sha256: `keymap.py` 8555441e0f14be59a2866f7c4e14ce987aa3c5e4243cf4b6e289dd5be0df7e23, `__init__.py` 35b2dcd14c050465fb796ba4d4e9a1bfad0931b23cbd04222753c27833dd66cd, `draft_guard.py` f7488025e595f3cfd4d2725980c17fbeb7fe4355ed70bd957eab02e3191a656e; all three `restored: True` |
| Bytecode cache | `python -B` on every run (C-46) |
| Verdict granularity | per resolved node id where a node resolves; a node in a file that cannot be collected is RED at the file (the module it tests does not exist), not per id |

| Field | Value |
|---|---|
| **RED counterfactual** | base tree: 5 nodes RED by assertion, 2 files RED at collection (17 own nodes + the draft params of `test_keymap.py` unreachable); transcript `evidence/inc1a-red-counterfactual.transcript`; all digests restored. **C13 specifically:** the `plain()`-dropped RED is the mutants `G-plain-title` / `G-plain-map` below (`modal_title_is_literal_and_plain[esc]` and `[surrogate]` RED); the oracle reads `Static.content`, the source string, not rendered cells |

### Mutation verdicts — per resolved node (`evidence/inc1a-mutation-battery.transcript`; every mutant restored, digest `restored: True`)

Run over the four node files (152 nodes with the then-count). Pre-mutation digests as above.

| Mutant | Mutation (position · operation) | Verdict | Nodes that went RED |
|---|---|---|---|
| K-d-swap | seat row `d`: action `discard` -> `stay` | **KILLED** | `modal_returns_the_token…[d-discard]`, `screen_bindings_are_generated…`, census x3, `n03h` |
| K-modal-off | `MODAL_SCOPES` drops `SCOPE_DRAFT` | **KILLED** | `hint_row_is_read…`, `screen_bindings_are_generated…`, census `modal_and_borrows_no_chord` |
| K-priority | `esc` row gets `priority=True` | **KILLED** | census `modal_and_borrows_no_chord`, `n03h` |
| K-order | `"draft"` declared after `"app"` in `GROUP_SCOPE` | **KILLED** | census `declared_before_app_and_headed_unsaved` |
| K-header | `GROUP_HEADER["draft"]` `unsaved` -> `draft` | **KILLED** | same census node |
| K-glyph | `esc` glyph spelled `escape` | **KILLED** | `hint_row_is_read…`, `hint_follows_the_seat…`, `test_glyph_is_a_plausible_display_form_of_its_key`, `n03h` |
| G-markup | title `Static` loses `markup=False` | **KILLED** | `a_markup_payload_in_the_title_is_painted_literally` |
| G-plain-title | `darkside.plain(self.node_title)` -> `self.node_title` | **KILLED** | `modal_title_is_literal_and_plain[esc]`, `[surrogate]` |
| G-plain-map | `darkside.plain(self.map_id)` -> `self.map_id` | **KILLED** | same two |
| G-no-map | map id never shown (`if self.map_id` -> `if False`) | **KILLED** | `title_follows_the_ruled_wording`, `…plain[esc,click-markup,surrogate]` |
| G-save-token | `action_save` dismisses `"discard"` | **KILLED** | `…token_for_each_key[s-save]` |
| G-stay-token | `action_stay` dismisses `"save"` | **KILLED** | `…token_for_each_key[escape-stay]` |
| G-hint-key | hint paints `row.key` instead of `row.glyph` | **KILLED** | `hint_row_is_read…`, `hint_follows_the_seat…` |
| G-hint-literal | hint is a literal with today's wording | **KILLED** | `hint_follows_the_seat_not_a_literal` only (the wording-equality node cannot see provenance; the relabel arm exists for this) |
| G-bindings-literal | `BINDINGS` built with `include_app=True` | **KILLED** | `screen_bindings_are_generated…`, `test_keymap.py::test_at_n03f_…[draft]` |

**Declared gap.** `test_llr_003_1_app_chords_do_not_pass_through_the_guard` (the real-`MapperApp` arm) was RED under **no** mutant, including K-modal-off and G-bindings-literal (the app chords inherited into the guard). Textual already makes `?` and `ctrl+p` inert beneath a modal in this app (probed: depth unchanged), so the arm characterises present framework behaviour and certifies nothing about the seat; the seat-level guarantee is carried by the census node `modal_and_borrows_no_chord` and `screen_bindings_are_generated…`. It is kept as a tripwire if the framework behaviour changes, and is declared here as non-discriminating. Also not run: `G-plain-both` (redundant with `G-plain-title`, removed from the run list).

| Field | Value |
|---|---|
| **Mutation verdicts** | 15 mutants run per resolved node: 15 KILLED, 0 SURVIVED, 0 CRASH, 0 BAD; 1 test node (the app-chord arm) killed by none, declared above; every restore digest equals the pre-mutation digest |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `modal_title_is_literal_and_plain` oracle (source `Static.content`) | `plain()` dropped at the sink (G-plain-title, G-plain-map) | `[esc]` and `[surrogate]` RED in the battery transcript |
| `a_markup_payload_in_the_title_is_painted_literally` (visual `plain` + empty spans) | `markup=False` dropped (G-markup) | RED |
| `hint_follows_the_seat_not_a_literal` | literal hint (G-hint-literal) | RED, while the equality node stayed GREEN |
| `evidence/inc1a-mutate.py` | non-unique anchor prints `BAD`; every run prints `changed: True` then `restored: True` | 15/15 `changed: True`, 15/15 `restored: True` |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 instruments, each shown RED before its first PASS was believed |

### Emitted-form assertion

| Field | Value |
|---|---|
| **Emitted-form assertion** | none — this increment emits no artifact beyond evidence transcripts. The lane transcript was post-processed: the operator profile path prefix is replaced by `<USERPROFILE>` in 6 places (batch guard A-110); counts and tail unchanged. The modal's own emitted string is asserted in `title_follows_the_ruled_wording` (exact sentence) |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED counterfactual transcript | `.dev-flow/2026-10-08-data-safety-batch/evidence/inc1a-red-counterfactual.transcript` | `df1025368618b6b90efe4f62298fa5f2e42710053b691fb371bd935586568aa7` |
| Mutation battery (15 mutants) | `.dev-flow/2026-10-08-data-safety-batch/evidence/inc1a-mutation-battery.transcript` | `d3911aabd12763395f0e0de48fc7ac70abe7a48f0463c15c364d329372b8be99` |
| Mutation / RED driver | `.dev-flow/2026-10-08-data-safety-batch/evidence/inc1a-mutate.py` | `a4462a214b9e399814ce5d8c7641a21df837f06dfbd8cd745d142021526a45fa` |
| Default-lane transcript (path-scrubbed) | `.dev-flow/2026-10-08-data-safety-batch/evidence/inc1a-default-lane.transcript` | `429bad34f1a72a78ea24f8a5994c894b0ed1558106d1d506f26c745ddd7f341e` |

| Field | Value |
|---|---|
| **Evidence files** | 4 artifacts at the declared home with the digest of their working-tree bytes (`.gitattributes` marks them `-text`); the index-blob digests to be re-checked after commit (§6) |

### Load-bearing emptiness

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — "the `draft` scope is exactly three rows with no app chord and no priority" rests on the seat holding no other `draft` row; pinned both ways by the census, not by a search |
| If the result is an ABSENCE, what made the search wide enough | C-56: hostile code points are built with `chr()`; `grep -n "#[0-9a-fA-F]{6}\|WARN\|ALERT\|PULSE" mapper/screens/draft_guard.py` -> 0 hits (the hue census does not move) |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `assert len(declared) == 3` in the census |
| Conjunctive criteria: one mutation per conjunct | title sink = `plain` AND `markup=False`: G-plain-title/-map and G-markup separately; modal = scope in `MODAL_SCOPES` AND no priority: K-modal-off, K-priority |
| Synthetic instance of the absent case | n/a |
| **Positive control for every probe that returned an ABSENCE** | the hex/WARN grep: the same pattern run on `mapper/screens/help.py` returns hits (it paints `#121212`), so the probe can see a hex literal |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by other tests | `grep -rln "MODAL_SCOPES" mapper tests` | `keymap.py`, `test_inc9.py` (f6 param list excludes modal scopes, so `draft` is excluded, GREEN), `test_data_safety_census.py` (new) |
| B1 | `grep -rln "GROUP_SCOPE\|GROUP_HEADER" tests` | `test_inc9.py`, `test_inc9c.py` (`:363` iterates scopes), `test_inc9d.py`, `test_inc9e.py` (raw-group-id palette check), `test_inc9f.py`, `test_keymap.py`: all green in the lane |
| B2 file moved on disk | none moved | n/a |
| B3 goldens capture this source | `git ls-files \| grep -ci golden` | 1 hit, by name only (`tests/test_repair_golden_census.py`, a test, not a golden file); green in the lane |
| B4 artifact consumed elsewhere | `grep -rln "from mapper.screens import" tests mapper` | `test_app.py`, `test_en7.py`, `test_help_scope.py`, `test_inc9m.py`, `test_inc9q.py`, `test_inc9r.py`, `test_keymap.py`, `test_vocabulary_declaration.py`, `app.py`: all green in the lane |
| A3 interface consumed by another module | `DraftGuardScreen` has no caller yet | n/a until Inc-1b; I-2 deviation declared in §6 |

| Field | Value |
|---|---|
| **Reverse census** | 6 probes run; the hits re-validated green in the default lane; the census nodes `test_a3_census`, `test_darkside_census`, `test_inc4_census`, `test_no_operator_paths` were run at file level and pass (no edit needed) |

### Correction population

| Correction | Population | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| a test that quantifies over the live seat now sees the `draft` scope | tests reading `KEYMAP` / `GROUP_SCOPE` / `MODAL_SCOPES` | the B1 greps above, then the file-level run of every hit | 3 reddened (`test_inc9::cd25a`, `test_inc9::a112[seat]`, plus the `test_keymap`/`test_key_dispatch` pins) | 4 edits (`test_inc9` x2, `test_keymap`, `test_key_dispatch`) | the rest derive from the seat and stayed GREEN |

| Field | Value |
|---|---|
| **Correction population** | 1 correction enumerated with its method before editing; the pins were edited with the seat |

### Signed-balance test ledger

`post = base − deleted + added` gives `2831 = 2808 − 0 + 23` ✓ reconciles. Base: Inc-3's lane result 2808 selected. Post: `--collect-only` at `8120a24` -> `2831/2855 tests collected (24 deselected)`, and the lane: 2828 passed + 3 xfailed = 2831 selected. Added 23 = 13 (`test_draft_save.py`) + 4 (`test_data_safety_census.py`) + 4 (`test_keymap.py`: `n03a` x3 draft bindings, `n03f[draft]`) + 2 (`test_repair_artifact_claims.py`: `…[draft_guard.py]` x2, parametrised over product files). Deleted 0.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | ABSENT — not yet run; owed by the orchestrator (`code-reviewer`) |

---

## 5 · Risks

- The modal exists but nothing pushes it; Inc-1b wires it. It must not be merged alone (R-10).
- The app-chord arm is a characterisation of Textual behaviour with no killing mutant (declared).
- The keymap tests read the `draft` group id and header `unsaved`; the language census lexicon is now four words wider.
- Only Python 3.12.7 / Textual 8.2.8 / one machine. No render at 118/87 columns was taken; the guard has no caller to render through yet (UX-1 is at the Inc-1b gate).
- `DEFAULT_CSS` is f-string built from `darkside.GROUND/PANEL` tokens; the guard's look (width 60, centred) was seen only through region numbers, not a screenshot.

---

## 6 · Pending items / spec deviations

- **I-2 deviation (additive):** the design freezes `DraftGuardScreen(title: str)`. This increment ships `DraftGuardScreen(title: str, map_id: str = "")`. Reason: R9 puts the map id in the title, and AT-013 needs a title naming the lower map, so the modal owns the sentence. The one-argument call still works (no `· map` suffix). Inc-1b/Inc-2 callers should pass `map_id`. Needs the orchestrator to amend §4 I-2.
- `tests/test_inc4_census.py:62` and `EXPECTED_PER_SCOPE[map]` are Inc-1b (the `ctrl+s` map row).
- `DATA_SAFETY_ADDED` gets its 4th row in Inc-1b.
- AT-015 through `j` (the full guard on a hostile node title) is Inc-1b.
- After commit: re-derive the evidence digests from the index blobs (`git show :<path> | sha256sum`).

**Conditions (Inc-1a parts):** C9 (title wording R9) discharged: exact-sentence node. C13 discharged at modal level: executed RED with `plain()` dropped, source-content oracle. C14 Inc-1a part discharged: `tests/test_inc9.py` language census (`test_a112…`) and `tests/test_inc9e.py` run at file level and pass; the palette census `test_inc9e` palette nodes pass. The other C14 arms (esc with live search, etc.) belong to later increments.

---

## 7 · Suggested next task

`code-reviewer` on this diff (§4b), then Inc-1b (inspector draft, `ctrl+s`, wiring of `DraftGuardScreen`, `DATA_SAFETY_ADDED` 4th row, `test_inc4_census` edit).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 3 source files (§2) |
| 2 | Tests written in this same increment | all | ✓ | 23 new nodes, 2808 to 2831 |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | TC-003.1 nodes (§4) |
| 4 | RED counterfactual declared | `core` · `full` | ✓ | base-tree run, 5 RED + 2 collection errors, digests restored |
| 5 | Reverse census declared | `core` · `full` | ✓ | §4, 6 probes |
| 6 | `code-reviewer` passed | `core` · `full` | ⚠ | not yet run (§4b ABSENT) |
| 7 | No file from another lane touched | all | ✓ | only the 3 source files, 5 tests, `.dev-flow` batch dirs; `prototypes/`, `mapper.db`, `fixtures/.mapper/` untouched |
| 8 | Frozen interfaces untouched | all | ⚠ | I-2 extended additively (`map_id=""`), declared in §6 |
| 9 | Coverage claims verified on disk | all | ✓ | counts from `--collect-only` and the stored lane transcript |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 |
| 11 | Mutation verdicts declared per arm | all | ✓ | 15 mutants, 15 KILLED, one non-discriminating arm declared |
| 12 | Instrument RED-proof declared | all | ✓ | 4 instruments |
| 13 | Correction population declared | all | ✓ | §4 |
| 14 | Emitted-form assertion declared | all | ✓ | exact-sentence node; path-scrub note |
| 15 | Independent review names somebody | all | ⚠ | ABSENT, owed |
| 16 | Evidence files declared with stored digests | all | ✓ | 4 files |
