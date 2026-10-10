# Validation — mapper — Batch 2026-10-09-hygiene-batch

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`); for Spanish batches **translate the prose, never a label** — the reserved field names are declared in §✅ Verdict and are read literally.
> Phase 4 artifact. Content owner: `qa-reviewer`, who **EVALUATES** the results of the validation strategy fixed in Phase 1, **names who executed each one** and returns the rows; the orchestrator writes `04-validation.md` (`stations/shared-homes-roles.md` §Delegation). The ONE complete gate-suite run is the orchestrator's (`C-25`); a sub-agent consumes the result and never owns the run.

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/docs/validation-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

## ✅ Verdict (read first)

> **Reserved field names.** The **field names and block keywords below are language-independent** — the
> validator parses them literally and they are never translated:
> `Result` · `Layer 0` · `Evidence checklist` · `⏸ DEFER`
> Everything else on this page — headings, guidance, the prose in every cell — is translated with the batch.
> **One strategy, not two:** the flow ships no alias table, so a translated label is read as an ABSENT one and the rule keyed on it reports a true-sounding silence.
> **And one FLOW-WIDE reserved token, read out of this artifact by `V42` no matter which template minted it:** `⏸ DEFER`. It is a MARKER rather than a field name, which is why it is stated here *and* in `/dev-flow` §Language of artifacts rather than in a per-template list — a deferral can be written in any batch artifact, including the ones that carry no block at all.
>
> **And so are the three verdict tokens** `PASS` · `PASS-WITH-NOTES` · `FAIL`, which are VALUES and not prose.
> A Spanish batch writes `- **Result:** PASS`, not `- **Resultado:** aprobado`: the label, the tokens and the
> reviewer-identity tokens below are the machine's vocabulary.

- **Result:** PASS-WITH-NOTES
- **Layer 0:** 0 unit(s) met the criterion · 0 carry a named reddening mutation
- **Requirements:** 5/5 pass · 0 blocker fails
- **Black-box acceptance (Layer B):** ✓ every story's `AT` observes its outcome through the shipped surface (boundary + negative)
- **Surface-reachability (bidirectional):** ✓ all named inputs AND outputs/deliverables reached/observed at the surface
- **Supersession inspection (read off the P3 packets):** ✓ all surviving refs negative
- **Test ledger:** ✓ reconciles (`base − D + A = post`)
- **Evidence checklist (qa-reviewer):** `qa-reviewer` (Claude Sonnet, independent) · ACCEPT-WITH-FIXES, all fixes applied · 11 of 11 rows ✓ after the fixes (2 were ✗ before them: executor per result, and the unfilled template)

> If every line is ✓, the Detail below is reference only. Any ⚠/✗ → read the matching part.

---

## Detail (reference)

### Layer 0 — unit

| Unit | Which criterion | Node id | Result |
|---|---|---|---|
| none — no unit meets the criterion: `guard_open()` is a one-line read, and nothing in the change reaches cyclomatic ≥3 or crosses a module boundary | — | — | n/a |

**Measured by mutation, never by line coverage.** For each unit, name the mutation and paste the RED:

| Unit | Mutation applied | RED observed? | Transcript |
|---|---|---|---|
| none | — | — | — |

### UX walkthrough — only if trigger family D fired

| Criterion (when the user does X, they observe Y) | Driven with the REAL mechanism | Painted result asserted | Verdict |
|---|---|---|---|
| not applicable — no trigger-D surface | — | — | — |

**Mechanism used:** `none — inspected only`

| Act | What it is | Performed? |
|---|---|---|
| Automated walkthrough | the criteria above, driven through the REAL mechanism | `not applicable — no trigger-D surface` |
| Expert inspection | a cognitive walkthrough against declared criteria, by a reviewer and not a user | `not applicable — no trigger-D surface` |
| Evaluation with users | real users of the system, doing the tasks named in the context of use | `not applicable — no trigger-D surface` |

- **Method:** trigger family D did not fire: this is a behaviour-preserving refactor with no user-visible change (no string, key, colour or layout diff — §2.4). The acceptance outcomes are instead observed through the shipped surface by AT-060 / AT-061 / AT-062 and the two behaviour nodes, which is why no UX walkthrough was performed.
- **Participants or population:** none — not applicable.
- **Evidence of the evaluation:** none — not applicable.
- **Limits:** this establishes nothing about real-user UX, because the change is invisible to a user by design (an internal, behaviour-preserving refactor). The walkthrough was skipped on those grounds, not because a criterion was dropped.

### Layer A — functional (white-box): per-requirement results
> `TC-NNN` ↔ LLR/HLR. `Result` = pass / fail. `Evidence` = command output, observed behavior, inspection note, or analysis result.

| Req | Method | Executed verification | Numeric threshold | Result | Evidence |
|-----|--------|-----------------------|-------------------|--------|----------|
| LLR-001.1 | test (unit) | `python -B -m pytest -q -p no:cacheprovider tests/test_draft_hygiene.py` (all 4 nodes; `inc001-red-after-nits.transcript`: 4 RED on base, `4 passed` on the increment) and the gate suite (`p4-full-suite.transcript`) — **executed by: orchestrator** | exit code 0 | pass | `tests/test_draft_hygiene.py::test_llr_001_1_last_save_error_is_declared_none_before_any_save` · `tests/test_draft_hygiene.py::test_llr_001_1_last_save_error_is_declared_and_never_read_through_getattr` |
| LLR-001.2 | test (unit) | `python -B -m pytest -q -p no:cacheprovider tests/test_draft_hygiene.py` (all 4 nodes; `inc001-red-after-nits.transcript`) and the gate suite (`p4-full-suite.transcript`); the contract's selector is `-k llr_001_2` (LED .6) — **executed by: orchestrator** | exit code 0 | pass | `tests/test_draft_hygiene.py::test_llr_001_2_guard_open_follows_the_guard` · `tests/test_draft_hygiene.py::test_llr_001_2_no_read_of_the_guard_flag_outside_map_screen` |
| LLR-002.1 | test (integration) | `HOME-1` mutation run (`evidence/b99-home1-mutation.transcript`) — **executed by: orchestrator** | 1 failed under the mutant · 1 passed after restore · sha256 equal | pass | `.dev-flow/2026-10-09-hygiene-batch/evidence/b99-home1-mutation.transcript` |
| HLR-001 | test | the regression set `inc001-regression-set.transcript` (187 passed; it contains `tests/test_draft_save.py`, `tests/test_draft_exits.py`, `tests/test_draft_hygiene.py`) and the gate suite `p4-full-suite.transcript` (2924 passed, 0 failed) — **executed by: orchestrator** | exit code 0 · 0 failed | pass | AT-060 (`tests/test_draft_save.py::test_llr_004_2_a_save_failure_names_ctrl_s_to_retry`) · AT-061 (`tests/test_draft_exits.py::test_pdr_c1_quit_while_a_node_guard_is_open_does_not_wedge`) · the 4 hygiene nodes · M1-M3 killed (`inc001-mutation-battery.transcript`) |
| HLR-002 | test | `HOME-1` mutation run (`b99-home1-mutation.transcript`: the witness alone, mutated then restored) and the gate suite (`p4-full-suite.transcript`) — **executed by: orchestrator** | the witness 1 failed under the mutant · 1 passed after byte-identical restore | pass | AT-062 (`tests/test_inc9h.py::test_inc9h_cr_f2_the_home_hint_follows_the_maps_when_the_screen_resumes`) · `evidence/b99-home1-mutation.transcript` |

**A worked example — text to read, never rows of your record.** It sits in a fence so that nothing has to be deleted: a row copied out of it would claim a verification nobody ran. Write your own rows in the table above.

```text
| *(example)* HLR-001 | test | `pytest … -k TC-001` | exit 0 | | |
| *(example)* LLR-001.1 | test (unit) | `…` | `…` | | |
```

### Layer B — behavioral (black-box) acceptance

| US | Acceptance test (`AT-NNN`) | Surface driven | Deliverable observed (path / element) | repr · boundary · negative | Result |
|----|----------------------------|----------------|---------------------------------------|----------------------------|--------|
| US-001 | AT-060 | map screen — `ctrl+s` on a failing save | the failed-save toast: `could not save '<map>' (OSError) · draft kept · ctrl+s to retry` | repr: toast text · boundary: error (a save that raises) · negative: M1 killed | pass |
| US-001 | AT-061 | map screen — `ctrl+q` over an already-open guard | the draft guard modal (still exactly one guard, no wedge) | repr: guard modal · boundary: guard already open · negative: M2/M3 killed | pass |
| US-002 | AT-062 | home screen — push/pop with maps added then deleted | the home hint line (`↵` pair present, then absent) | repr: hint line `↵` pair · boundary: empty (no maps) + maps change between visits · negative: HOME-1 killed | pass |

### Bidirectional surface-reachability matrix (extends A-5)
> Every named INPUT dimension AND every named OUTPUT/deliverable is exercised/observed through the handler — not only the service API.

| Direction | US dimension / deliverable | Service param / producer | Reached/observed at surface? | TC / AT | Status |
|-----------|---------------------------|--------------------------|------------------------------|---------|--------|
| input | `ctrl+s` (a failing save) | `MapScreen._save_draft` / `_save_or_toast` | yes | AT-060 | ✓ |
| input | `ctrl+q` / `j` / `escape` over the guard | `MapperApp.action_quit` / `MapScreen.guard_open()` | yes | AT-061 | ✓ |
| input | home screen push/pop with maps added/deleted | `HomeScreen.on_mount` hint refresh | yes | AT-062 | ✓ |
| output | the failed-save toast text | `MapScreen._save_draft` | yes | AT-060 | ✓ |
| output | the guard modal count (single guard) | `MapScreen._guard_draft` | yes | AT-061 | ✓ |
| output | the hint line `↵` pair | the home `HintLine` | yes | AT-062 | ✓ |

### Signed-balance test ledger
> `post = base − D + A`. State counts in collected / passed-lean / passed-full form.

| base | − D | + A | = post | actual collected | passed-lean / full | reconciles? |
|------|-----|-----|--------|------------------|--------------------|-------------|
| 2923 | 0 | 4 | 2927 | 2927 (`2927/2951 tests collected (24 deselected)`) | — / 2924 passed + 3 xfailed = 2927, 0 failed (`evidence/p4-full-suite.transcript`) | yes |

### Gaps detected
| ID | Requirement | Gap | Severity | Proposed action |
|----|-------------|-----|----------|-----------------|
| G-001 | (watch item — no requirement) | `test_c6_a_hidden_card_hands_the_draft_to_the_hint_line_in_alert` failed under machine load in the worker's run only, and was not reproduced; the P4 full-suite run did NOT fail it (2924 passed, 0 failed in 1498.92s) | minor | watch at P4 — if it fails again it becomes a FLAKE row (increment §6) |
| G-002 | (pre-existing — no requirement) | `ruff check mapper/app.py` reports `F401 re imported but unused` at `mapper/app.py:7`; pre-existing on master, the diff does not touch imports | minor | backlog row B-104 at close (one-line removal in any batch touching `app.py`) |

### Escaped-bug regression (if a defect escaped the suite)

| Regression id (`AT-NNN` / `TC-NNN`) | Pre-fix run (evidence it FAILED) | Pre-fix RED kind (value / shape) | Post-fix value-discriminating? (QC-2) | Post-fix result | Reconciled node |
|-------------------------------------|----------------------------------|----------------------------------|----------------------------------------|-----------------|-----------------|
| none — no defect escaped | — | — | — | — | — |

### Evidence checklist — qa-reviewer (full)
> Attach `qa-reviewer`'s completed evidence checklist (items in `agents/qa-reviewer.md`), each marked ✓/✗ with one-line evidence. An unchecked or evidence-less item blocks the gate.

**Who executed what:**
- The orchestrator (Claude Opus 5.5) ran the gate suite, the mutation battery, the RED re-run, the regression set and `HOME-1`.
- The worker Kimi (`kimi-for-coding`) authored the product change and `tests/test_draft_hygiene.py`. Its own regression run is reported in `inc001-kimi-unit-report.transcript`, and the record does not rely on it.
- The worker DeepSeek (`deepseek-v4-pro`) drafted this file, and the orchestrator then corrected it: the ledger cell and the G-002 action.
- The `qa-reviewer` ran nothing and read the transcripts.

The reviewer's own executor line said "the worker (DeepSeek) wrote the tests". That is wrong, and it is corrected above: Kimi wrote them.

| # | Item | ✓/✗ | Evidence |
|---|---|---|---|
| 1 | Acceptance criteria stated as outcomes | ✓ | `01-requirements.md` §3; Layer B rows |
| 2 | Test cases have explicit Expected | ✓ | AT-060 exact toast text; AT-061 `_guards(app)==1` |
| 3 | Edge cases | ✓ | error (save raises), boundary (guard already open), empty (no maps, AT-062); invalid n/a with reason |
| 4 | Regression checklist | ✓ | `inc001-regression-set.transcript` (187 passed) + the gate suite |
| 5 | Exit criteria | ✓ | 0 failed, 3 xfailed, exit 0 (`p4-full-suite.transcript`) |
| 6 | No PII / secrets | ✓ | transcripts scrubbed to `<wt>`/`<home>`; `tests/test_no_operator_paths.py` green |
| 7 | Mode declared | ✓ | validation; every result executed or n/a with reason |
| 8 | Executor named per result | ✓ (was ✗) | fixed: each Layer A row names its executor |
| 9 | Layer B with boundary + negative | ✓ | M1, M2, M3, HOME-1 killed |
| 10 | Bidirectional reachability | ✓ | 3 inputs, 3 outputs |
| 11 | No unfilled template | ✓ (was ✗) | this checklist pasted; LLR-001.2 selector fixed (LED .6) |
