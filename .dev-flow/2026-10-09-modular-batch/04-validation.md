# Validation — mapper — Batch 2026-10-09-modular-batch

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`); for Spanish batches **translate the prose, never a label** — the reserved field names are declared in §✅ Verdict and are read literally.
> Phase 4 artifact. Content owner: `qa-reviewer`, who **EVALUATES** the results of the validation strategy fixed in Phase 1, **names who executed each one** and returns the rows; the orchestrator writes `04-validation.md` (`stations/shared-homes-roles.md` §Delegation). The ONE complete gate-suite run is the orchestrator's (`C-25`); a sub-agent consumes the result and never owns the run.
>
> **Owed in.** `core` ✓ · `full` ✓
>
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
- **Layer 0:** 0 unit(s) met the criterion · 0 carry a named reddening mutation (pure cut/paste refactor; requirement-level mutation controls run instead — see the mutation table and Layer A evidence)
- **Requirements:** 24/24 pass (7 HLR-MOD + 17 LLR-MOD) · 0 blocker fails
- **Black-box acceptance (Layer B):** ✓ every story's `AT` observes its outcome through the shipped surface (boundary + negative)
- **Surface-reachability (bidirectional):** ✓ all named inputs AND outputs/deliverables reached/observed at the surface
- **Supersession inspection (read off the P3 packets):** ✓ all surviving refs negative (the dropped F4 lazy-read design has zero live readers — LLR-MOD.3.2's guard proves every patch site repointed and 0 `screens/**` imports of any patch name from `mapper.app`)
- **Test ledger:** ✓ reconciles (`base − D + A = post` → 2941 − 0 + 192 = 3133)
- **Evidence checklist (qa-reviewer):** `qa-reviewer` (Claude Sonnet, independent, read-only) **APPROVE-WITH-CONDITIONS → conditions M-1, M-2 applied**; verdict PASS-WITH-NOTES confirmed · 11 of 11 ✓ with evidence below

> If every line is ✓, the Detail below is reference only. Any ⚠/✗ → read the matching part.

**Verdict reason (3 lines):** all 24 requirements pass with executed evidence and every AT-065…AT-071 is GREEN with an executed RED counterfactual; the ledger reconciles (2941 − 0 + 192 = 3133; collected 3136/3160) and no defect escaped. The notes are three carried minor LOWs from the sealed DDR (census-baseline location, D-C3 guard's direct-importer scope, CR-3 unpatched `pan_extent` reader in `exporting.py`) plus one declared non-run (the 5-test network lane — no network available for this batch's gates; stated as a non-run, not a pass). None blocks the gate.

---

## Detail (reference)

### Layer 0 — unit

| Unit | Which criterion | Node id | Result |
|---|---|---|---|
| none — no unit meets the Layer-0 criterion: the batch moves existing methods byte-identically (LLR-MOD.4.3's AST-dump oracle), so no unit gains branching or new logic; every moved body is cut/paste | — | — | n/a |

**Measured by mutation, never by line coverage.** For each unit, name the mutation and paste the RED:

| Unit | Mutation applied | RED observed? | Transcript |
|---|---|---|---|
| none at unit level — the batch's mutation controls are requirement-level | — | — | — |
| AT-065 parity (all guard files' in-tree RED arms, executed once at the DDR) | painted-string mutant on a tmp copy; `BINDINGS`/mixin-drop/duplicated-`on_*`; repoint-skipped; re-export dropped; concern left in `app.py`; function-local `mapper.app` import restored; synthetic sibling-concern import; second F1 writer; one-token body mutation; raised AT-069 pin | yes — 77 passed at `69676cf` (the arms are permanent in-tree controls, GREEN in every gate; their RED side is structurally guaranteed) | `evidence/ddr-red-arms.transcript` (sha256 `750f2fc78cf404405215e143ea411eed4f7d8edfaed3d1b20f870a434acbb619`) |
| LLR-MOD.5.2 allow-list timing (the C9 condition) | allow-list not extended after B3 / extended before the call site moved | yes — both mutants RED, baseline and restore GREEN | `evidence/ddr-c9-allowlist-mutation.transcript` (sha256 `b8df864050ac0e6d65cab1d439d5f7a2f2dada0b9aff5b01bcd3e97a959e0c08`) + script `evidence/ddr-c9-allowlist-mutation.py` |
| AT-067 repoint-skipped (per-increment RED, stored) | one repoint (`refusal_sentence`) skipped — the patch stops biting while the rest passes | yes — `1 failed, 7 passed`; restore byte-identical (sha256 equal before/after) | `evidence/a1-red-patch-repoint.transcript` (sha256 `e4d781c3331a85e4366fa1733c6758d6148fca4e360f5d312f803842d351f257`) |

### UX walkthrough — only if trigger family D fired

| Criterion (when the user does X, they observe Y) | Driven with the REAL mechanism | Painted result asserted | Verdict |
|---|---|---|---|
| not applicable — family D did not fire | — | — | — |

**Mechanism used:** `none — inspected only`

| Act | What it is | Performed? |
|---|---|---|
| Automated walkthrough | the criteria above, driven through the REAL mechanism | `not applicable — family D did not fire` |
| Expert inspection | a cognitive walkthrough against declared criteria, by a reviewer and not a user | `not applicable — family D did not fire` |
| Evaluation with users | real users of the system, doing the tasks named in the context of use | `not applicable — family D did not fire` |

- **Method:** trigger family D did not fire. The batch is a pure structural refactor of `mapper/app.py` into `mapper/screens/` + `mapper/screens/map/`; §1.2 of the contract forbids any user-visible change (strings, keys, colours, layout). That no behaviour change reached the user is proven by AT-065: the scripted session (open a map, move, search, toggle a view, export, quit) driven with real keys through `MapperApp` + `app.run_test(...)` + `pilot.press(...)` paints byte-equal output against the committed pre-move text goldens at 118 and 87 columns (`evidence/mod_parity_118.txt` sha256 `43af8e1e7613f23e9da0b9a3090c880c6b6f1cc0341f9befb8e032efd95fbf2d`; `evidence/mod_parity_87.txt` sha256 `6ba755535f102742931c93af98c54889ea4ecc6e132f43a1db78f8461a889b9b`).
- **Participants or population:** none — not applicable.
- **Evidence of the evaluation:** none — not applicable (the walkthrough was skipped because family D did not fire, not because a criterion was dropped).
- **Limits:** this establishes nothing about real-user UX because, by design, no user-facing surface changed; the parity goldens bound the claim to the scripted session's steps and the two captured widths.

### Layer A — functional (white-box): per-requirement results
> `TC-NNN` ↔ LLR/HLR. `Result` = pass / fail. `Evidence` = command output, observed behavior, inspection note, or analysis result.
> Selector counts below were re-collected at `c5905d6` (HEAD, which differs from the `69676cf` gate commit only under `.dev-flow/` — verified `git diff --name-only 69676cf HEAD` → 0 non-`.dev-flow` files), so every count equals the gate tree's collection. No cited selector collects 0.

| Req | Method | Executed verification | Numeric threshold | Result | Evidence |
|-----|--------|-----------------------|-------------------|--------|----------|
| HLR-MOD.1 | test | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_structure.py` — 10 tests collected; run inside the P4 gate | exit 0; the 20 expected files present and owning their names; `mapper/app.py` ≤ 400 lines, no `Screen` subclass other than `MapperApp` | pass | gate `evidence/p4-gate-full-suite.transcript` (sha256 `eb263fb1b150c8715874c037bc3147d9cdb242ee49728a14756fc86d7469b161`, 3133 passed / 0 failed); tmp-copy RED arms in `evidence/ddr-red-arms.transcript` — **executed by: orchestrator** (gate), sub-agent (count re-collection) |
| HLR-MOD.2 | test | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_dispatch.py` — 7 tests collected; run inside the P4 gate | exit 0; `BINDINGS` in exactly 1 class (the core); 0 pairwise method-name collisions across the 12 modules; 0 mixin-declared core constants | pass | gate transcript; duplicated-`on_*` / `BINDINGS`-in-mixin RED arms in `evidence/ddr-red-arms.transcript` |
| HLR-MOD.3 | test | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_compat.py tests/test_search.py tests/test_inc9q.py tests/test_en8.py tests/test_app.py tests/test_inc9c.py tests/test_inc9n.py tests/test_inc9.py` — all run inside the P4 gate (guard file: 32 collected) | exit 0; all 21 imported names resolve from `mapper.app`; the 7 module-global patch targets bite through their repointed module-globals at premise 4's site counts; `GitHubConnector.fetch` bites through the shared class object; the patch-site guard passes for every patch site; 0 imports of any patch name from `mapper.app` into a `screens/` module | pass | gate transcript; `evidence/a1-red-patch-repoint.transcript` (repoint-skipped RED, restore sha256-equal) |
| HLR-MOD.4 | test | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_parity.py` — 3 collected; plus the full suite at P4 | exit 0 for both; 0 painted-line diffs across the scripted session at both widths (118 and 87) | pass | `evidence/mod_parity_118.txt` / `evidence/mod_parity_87.txt` (digests above); gate transcript 3133 passed / 0 failed |
| HLR-MOD.5 | test | `python -B -m pytest -q -p no:cacheprovider tests/test_draft_hygiene.py tests/test_darkside_census.py tests/test_keymap.py tests/test_en5.py tests/test_en7.py tests/test_app_imports_used.py` — all run inside the P4 gate | exit 0; per-file assertion floors hold: `test_draft_hygiene.py` ≥ 9, `test_darkside_census.py` ≥ 55, `test_keymap.py` ≥ 35, `test_en5.py` ≥ 34, `test_en7.py` ≥ 37, `test_app_imports_used.py` ≥ 2; the 14 `("mapper/app.py", line)` pins each resolve to exactly one home | pass | gate transcript; AT-069 nodes `tests/test_mod_compat.py -k at069` (2 collected: baseline + RED arm) |
| HLR-MOD.6 | test | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_deps.py` — 13 collected; run inside the P4 gate | exit 0; 0 occurrences of either import form (`import mapper.app` any alias, `from mapper.app import …`) in `mapper/screens/**.py` at any scope; `factory.py`/`settings.py` hold module-level helper imports | pass | gate transcript; AT-070 tmp-copy RED arm in `evidence/ddr-red-arms.transcript` |
| HLR-MOD.7 | test | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_deps.py` — 13 collected (incl. `-k at071`, 1 node); run inside the P4 gate | exit 0; all §3 rule groups asserted against the shipped ASTs (map allow-list + `screen.py`'s 11-concern exception; no sibling-concern imports; only `app`/`repo.py`(NavigationModel)/`home.py`+`import_preview.py`(MapScreen) import `screens/map`; `open_external` call sites ⊆ {`app`, `screens/map/opening`}) | pass | gate transcript; synthetic-mutation RED arms in `evidence/ddr-red-arms.transcript` |
| LLR-MOD.1.1 | test (unit) | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_structure.py -k spine_a` — 3/10 collected | exit 0; each of the 7 sibling modules exists, defines its expected names, and `mapper.app.<name>` resolves with `is` identity | pass | gate transcript; re-export-dropped RED arms in `evidence/ddr-red-arms.transcript` |
| LLR-MOD.1.2 | test (unit) | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_structure.py -k b0` — 3/10 collected | exit 0; `inspect.getfile(MapScreen)` ends with `screens/map/screen.py`; `mapper/app.py` ≤ 400 lines | pass | gate transcript; concern-left-in-`app.py` RED arm in `evidence/ddr-red-arms.transcript` |
| LLR-MOD.1.3 | test (unit) | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_structure.py -k spine_b` — 3/10 collected | exit 0; 11 mixin modules present; every census method assigned to exactly one module; `MapScreen.__mro__` holds the 11 mixins ahead of `Screen` | pass | gate transcript |
| LLR-MOD.2.1 | test (unit) | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_dispatch.py -k bindings` — 2/7 collected | exit 0; exactly 1 `BINDINGS` and 0 `DEFAULT_CSS` across the 11 mixins; 0 `@on`-decorated methods in any mixin; the AST-derived constant roster fully held by `MapScreen.__dict__` | pass | gate transcript; `BINDINGS`-in-mixin RED arm in `evidence/ddr-red-arms.transcript` |
| LLR-MOD.2.2 | test (unit) | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_dispatch.py -k disjoint` — 1/7 collected | exit 0; 0 pairwise intersections across the 12 modules' method sets; 0 `screens/**` imports of the 8 patch names from `mapper.app` (either AST form, any scope) | pass | gate transcript; duplicated-name RED arm in `evidence/ddr-red-arms.transcript` |
| LLR-MOD.2.3 | test (e2e) | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_dispatch.py -k pilot` — 1/7 collected (same node as AT-066's) | exit 0; the hint line after the scripted key sequence equals the pre-B1 capture | pass | gate transcript; baseline `evidence/at066-baseline.txt` (sha256 pinned in `tests/test_mod_dispatch.py`); mixin-drop RED arm in `evidence/ddr-red-arms.transcript` |
| LLR-MOD.3.1 | test (integration) | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_compat.py -k reexport` — 25/32 collected | exit 0; all 21 names resolve from `mapper.app` with object identity to their defining module | pass | gate transcript |
| LLR-MOD.3.2 | test (integration) | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_compat.py -k patch_guard` — 2/32 collected; plus the 7 patch-carrying files (`test_search.py`, `test_inc9q.py`, `test_en8.py`, `test_app.py`, `test_inc9c.py`, `test_inc9n.py`, `test_inc9.py`), all run inside the P4 gate | exit 0; the 7 module-global targets bite at premise 4's site counts and `GitHubConnector.fetch` through the shared class object; the AST guard covers every patch site in `tests/`; 0 patch-name imports from `mapper.app` into `screens/` | pass | gate transcript; `evidence/a1-red-patch-repoint.transcript`; vacuous-repoint guard arms in `evidence/ddr-red-arms.transcript` |
| LLR-MOD.4.1 | test | the gate run itself: `python -B -m pytest -q -p no:cacheprovider tests/` at P4 (commit `69676cf`) | exit 0; 0 failed (P0 baseline 2941 passed / 3 xfailed / 0 failed) | pass | `evidence/p4-gate-full-suite.transcript` — **3133 passed, 24 deselected, 3 xfailed in 1498.87s, exit=0** — **executed by: orchestrator** (C-25) |
| LLR-MOD.4.2 | test (e2e) | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_parity.py -k parity` — 3/3 collected | exit 0; 0 painted-line diffs across all scripted steps at both widths, after volatile-cell normalisation | pass | goldens `evidence/mod_parity_118.txt` / `mod_parity_87.txt` (digests above); gate transcript; mutant-copy RED arm `::test_at065_parity_red_on_a_mutant_copy` in `evidence/ddr-red-arms.transcript` |
| LLR-MOD.4.3 | test (unit) | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_bodies.py` — 4 tests collected; run inside the P4 gate | exit 0; the baseline diff is empty (every census method exactly once, every body `ast.dump`-equal to the Inc-0 baseline at `.dev-flow/2026-10-09-modular-batch/evidence/mod-bodies-baseline.json`); 0 undefined-global references in any new module | pass | gate transcript; one-token body-mutation and deleted-import RED arms in `evidence/ddr-red-arms.transcript` |
| LLR-MOD.5.1 | test (integration) | `python -B -m pytest -q -p no:cacheprovider tests/test_draft_hygiene.py tests/test_darkside_census.py tests/test_keymap.py tests/test_en5.py tests/test_en7.py tests/test_app_imports_used.py` — all run inside the P4 gate | exit 0; the 14 darkside pins resolve to exactly one home each; the `test_draft_hygiene.py` MapScreen arms parse `inspect.getfile(MapScreen)`; the `test_keymap.py` scanned set equals `pkgutil.walk_packages(mapper)` | pass | gate transcript; AT-069 baseline + raised-pin RED arm (`tests/test_mod_compat.py -k at069`, 2 collected) |
| LLR-MOD.5.2 | test (integration) | `python -B -m pytest -q -p no:cacheprovider tests/test_arch_osopen_callers.py tests/test_inc9p.py tests/test_inc9q.py` — 5 + 84 + 68 collected; run inside the P4 gate | exit 0 at the B3 and B9 gates and at P4; the allow-list gained `screens/map/opening.py` with the call site's move | pass | gate transcript; `evidence/ddr-c9-allowlist-mutation.transcript` (both timing mutants RED, baseline/restore GREEN) |
| LLR-MOD.6.1 | test (unit) | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_deps.py -k b02` — 4/13 collected | exit 0; 0 occurrences of either import form referencing `mapper.app` in `mapper/screens/**.py` at any scope; module-level helper imports present in factory/settings | pass | gate transcript; restored-import RED arms in `evidence/ddr-red-arms.transcript` |
| LLR-MOD.6.2 | test (unit) | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_deps.py -k no_app_import` — 2/13 collected | exit 0; 0 AST-detected occurrences of either import form referencing `mapper.app` anywhere under `mapper/screens/`; sibling screens import `MapScreen` from `mapper.screens.map` | pass | gate transcript; synthetic-import RED arm in `evidence/ddr-red-arms.transcript` |
| LLR-MOD.7.1 | test (unit) | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_deps.py -k arch` — 6/13 collected | exit 0; all four rule groups asserted against the shipped ASTs | pass | gate transcript; synthetic sibling-concern import and `MapScreen`-from-`mapper.app` RED arms in `evidence/ddr-red-arms.transcript` |
| LLR-MOD.7.2 | test (unit) | `python -B -m pytest -q -p no:cacheprovider tests/test_mod_census.py` — 3 tests collected; run inside the P4 gate | exit 0; census diff empty against `.dev-flow/2026-10-09-modular-batch/spike/census.json` | pass | gate transcript; second-F1-writer RED arm in `evidence/ddr-red-arms.transcript` |

**A worked example — text to read, never rows of your record.** It sits in a fence so that nothing has to be deleted: a row copied out of it would claim a verification nobody ran. Write your own rows in the table above.

```text
| *(example)* HLR-001 | test | `pytest … -k TC-001` | exit 0 | | |
| *(example)* LLR-001.1 | test (unit) | `…` | `…` | | |
```

### Layer B — behavioral (black-box) acceptance

| US | Acceptance test (`AT-NNN`) | Surface driven | Deliverable observed (path / element) | repr · boundary · negative | Result |
|----|----------------------------|----------------|---------------------------------------|----------------------------|--------|
| US-001 | AT-068 (`tests/test_mod_structure.py -k at068`, 1/10 collected; companions AT-069/AT-070/AT-071, same story per DDR C3) | the repository tree itself — the files a maintainer edits | `mapper/screens/map/{painting,searching,panning,hints,navigation,drafts,editing,undo,focus_mode,opening,exporting,screen}.py`, the 7 sibling modules, and `mapper/app.py` at 340 lines (`wc -l`, qa L-1) | repr: one concern per module file · boundary: `screen.py` holds exactly the lifecycle concern + constants, `__init__.py` re-export only, `app.py` at the ~350-line boundary · negative: concern method in the wrong module / `Screen` subclass left in `app.py` / re-export dropped — tmp-copy RED arms | pass |
| US-002 | AT-065 (`tests/test_mod_parity.py -k at065`, 3/3 collected) and AT-066 (`tests/test_mod_dispatch.py -k at066`, 2/7 collected) | the painted screen of the real app — `MapperApp(tmp_path)` + `app.run_test(size=…)` + `pilot.press(...)` | every painted line of the scripted session (open, move, search, toggle, export, quit) at 118 and 87 columns; the hint line after real-key dispatch through the mixins | repr: golden text lines equal step by step · boundary: wide 118 vs truncated 87 layouts; the patched limit exactly one node below the map size · negative: one-token painted-string mutant on a tmp copy (AT-065); `HintsOps`-dropped / duplicated-`on_*` mutant (AT-066) | pass |
| US-003 | AT-067 (`tests/test_mod_compat.py -k at067`, 3/32 collected), AT-069 (`tests/test_mod_compat.py -k at069`, 2/32), AT-070 (`tests/test_mod_deps.py -k at070`, 1/13), AT-071 (`tests/test_mod_deps.py -k at071`, 1/13) | the shipped screens (search/count line, path-refusal toast) and the shipped source tree (suite's imports, patch sites, pins, module graph) | the 7 module-globals of the reading modules + the biting patched refusal/limit; the 21 re-exported names; the 14 single-home darkside pins; the closed B-02; the §3 module graph | repr: patch bites through the repointed module-global, observed through the shipped screen · boundary: patched limit one node below map size; a pinned string in two homes fails · negative: repoint-skipped (stored transcript); raised pin (AT-069); restored function-local import (AT-070); synthetic `import mapper.app` / sibling-concern import (AT-071) | pass |

### Bidirectional surface-reachability matrix (extends A-5)
> Every named INPUT dimension AND every named OUTPUT/deliverable is exercised/observed through the handler — not only the service API.

| Direction | US dimension / deliverable | Service param / producer | Reached/observed at surface? | TC / AT | Status |
|-----------|---------------------------|--------------------------|------------------------------|---------|--------|
| input | US-002 real keystrokes of the scripted session | `pilot.press(...)` at terminal widths 118 and 87 | yes | AT-065 | ✓ |
| output | US-002 the painted screen lines | the committed text goldens on disk (captured at `90e731b`, Inc-0, before any move — qa L-3) | yes | AT-065 | ✓ |
| input | US-003 the 8 monkeypatch names (7 module-globals + `GitHubConnector.fetch`) | `monkeypatch.setattr` at premise 4's sites, repointed to the reading modules | yes | AT-067 | ✓ |
| output | US-003 the search refusal/count line and the path-refusal toast | the shipped map screen under the patched limit / marker | yes | AT-067 | ✓ |
| input | US-001 the maintainer's view of the repository tree | `inspect` / AST reads of the shipped files | yes | AT-068 | ✓ |
| output | US-001 the concern module files themselves (one feature, one file) | the tree after the batch | yes | AT-068 | ✓ |
| input | US-003 the `screens/` source tree (B-02 closure) | AST scan for both `mapper.app` import forms | yes | AT-070 | ✓ |
| input | US-003 the §3 module graph | AST-derived dependency checkers | yes | AT-071 | ✓ |

### Signed-balance test ledger
> `post = base − D + A`. State counts in collected / passed-lean / passed-full form.

| base | − D | + A | = post | actual collected | passed-lean / full | reconciles? |
|------|-----|-----|--------|------------------|--------------------|-------------|
| 2941 passed + 3 xfailed (P0 at `d8cf942`, PLAN ledger) | 3 — 3 test functions removed and replaced inside modified files — found by `git diff -U0 d8cf942 HEAD -- tests | grep '^-.*def test_'` (qa M-1; a file-level `--diff-filter=D` check cannot see them): `test_at_064_app_imports_nothing_it_does_not_use` → parametrised over the package (`tests/test_app_imports_used.py`), `test_the_launcher_names_appear_only_in_app_and_osopen` → renamed `…_in_osopen_and_opening` (increment 023), `test_the_four_known_back_edges_are_exactly_the_ones_the_map_lists` → `test_b02_closed_there_are_no_screens_to_app_back_edges_at_all` (B-02 closed, a stronger assertion); no test FILE deleted (`git diff --diff-filter=D --stat d8cf942 HEAD -- tests` → empty) | 195 (derived: post − base + D = 3133 − 2941 + 3) | 3133 passed + 3 xfailed = 3136 | 3136 (`3136/3160 tests collected (24 deselected)` at `c5905d6`, the gate commit's tests byte-identical) | 3133 / 3133 + 19 slow (slow lane at `acbd087`, `evidence/ddr-acbd087-slow-lane.transcript` sha256 `1fcab7c50206c396dbe27c006a8ea5d9dc5f922bfa3b0cbf4c736dbb29e02915`); **network lane (5 tests): NOT RUN — no network for this batch's gates, declared non-run, not a pass** | yes |

- Gate evidence: `evidence/p4-gate-full-suite.transcript` at `69676cf` — **3133 passed, 24 deselected, 3 xfailed, 0 failed in 1498.87s, exit=0** (sha256 `eb263fb1b150c8715874c037bc3147d9cdb242ee49728a14756fc86d7469b161`). The 24 deselected are the `slow`/`network` markers (`pyproject.toml:46`).
- Arithmetic: 2941 − 0 + 192 = 3133 (passed-lean) and 2944 − 0 + 192 = 3136 (collected) — both reconcile; the +192 counts every guard/AT node the 23 increments added, incl. increment 023's two guard nodes (not `slow`).

### Gaps detected
| ID | Requirement | Gap | Severity | Proposed action |
|----|-------------|-----|----------|-----------------|
| G-001 | LLR-MOD.7.2 | the census baseline lives in the batch folder (`.dev-flow/2026-10-09-modular-batch/spike/`, read by `tests/test_mod_census.py:39`); archiving the batch folder would break the guard | minor | backlog — move the census baseline under `tests/` before the batch folder is archived (carried LOW from the sealed DDR) |
| G-002 | LLR-MOD.7.1 | the D-C3 cycle guard (`screens_init_sibling_imports`, `tests/test_mod_deps.py:303`) sees only DIRECT importers of `mapper.screens.map`; a re-exported modal importing `home` one hop away would close the cycle unflagged (Python would most likely fail at import time) | minor | backlog — widen the guard's transitive scope in a later batch (carried LOW from the sealed DDR) |
| G-003 | HLR-MOD.3 / LLR-MOD.3.2 | CR-3: `screens/map/exporting.py`'s own `pan_extent` reader (`mapper/screens/map/exporting.py:13`) has no patched test; the suite's single patch site (`tests/test_en8.py:66`) repoints to `screens/map/panning.py` | minor | backlog — add a patch site for the exporting reader or document the single-reader contract (accepted gap, recorded in the sealed DDR) |
| G-004 | LLR-MOD.4.1 | the 5-test network lane was not run (no network available for this batch's gates) | minor | backlog — run `-m network` once network is available; declared non-run, not a pass |

### Escaped-bug regression (if a defect escaped the suite)

| Regression id (`AT-NNN` / `TC-NNN`) | Pre-fix run (evidence it FAILED) | Pre-fix RED kind (value / shape) | Post-fix value-discriminating? (QC-2) | Post-fix result | Reconciled node |
|-------------------------------------|----------------------------------|----------------------------------|----------------------------------------|-----------------|-----------------|
| none — no defect escaped the suite to date in this batch | — | — | — | — | — |

### Evidence checklist — qa-reviewer (full)
> Attach `qa-reviewer`'s completed evidence checklist (items in `agents/qa-reviewer.md`), each marked ✓/✗ with one-line evidence. An unchecked or evidence-less item blocks the gate.

**Who executed what:**
- **The orchestrator (Claude Opus 5.5)** ran the ONE complete gate suite (C-25) at `69676cf`, the slow lane at `acbd087`, the in-tree RED arms (77 passed), the C9 allow-list mutation, and the per-increment gates a1…b10b12. It owns every transcript cited above.
- **Workers (DeepSeek, Kimi, …)** authored the guard/AT test files across the 23 increments; the guard files carry their own in-tree RED arms.
- **The sub-agent (Kimi, this file's drafter)** re-collected every selector count cited in Layer A/Layer B (`--collect-only`, none collects 0), verified the ledger arithmetic, the deleted-test-file check (the function-level check was added by the qa-reviewer, M-1), and the HEAD↔gate-commit diff, and re-hashed every cited evidence file.
- **The `qa-reviewer`** (Claude Sonnet) ran `--collect-only` on 20 selectors, re-hashed the 7 cited evidence files, and ran the function-level deleted-test check (`git diff -U0 d8cf942 HEAD -- tests | grep '^-.*def test_'`); it ran no suite.

| # | Item | ✓/✗ | Evidence |
|---|---|---|---|
| 1 | Acceptance criteria as outcomes | ✓ | AT-065…AT-071 observed in Layer B through the shipped surfaces |
| 2 | Explicit Expected | ✓ | every Layer A row carries the requirement's numeric threshold; gate 3133/3 xfailed/0 failed |
| 3 | Edge cases | ✓ | patched limit one node below map size; widths 118/87; two-homes pin fails; empty-set B-02 boundary; C9 timing mutants |
| 4 | Regression checklist | ✓ | `evidence/p4-gate-full-suite.transcript` (gate) + `evidence/ddr-acbd087-slow-lane.transcript` (19 slow passed); RED arms 77 passed |
| 5 | Exit criteria | ✓ | 100% LLR covered with a pass; every AT GREEN with an executed RED; 0 failed |
| 6 | No PII / secrets | ✓ | no operator paths, no home paths, no account names written anywhere in this artifact |
| 7 | Mode + executor per result | ✓ | "executed by: orchestrator" on the gate rows; sub-agent counts marked as re-collection |
| 8 | Layer B with boundary + negative | ✓ | three story rows, each with repr/boundary/negative |
| 9 | Bidirectional reachability | ✓ | 6 inputs/outputs, all ✓ |
| 10 | Ledger | ✓ | 2941 − 3 + 195 = 3133; collected 3136/3160; 3 test functions rewritten (named in the ledger row), no test file deleted |
| 11 | No unfilled template | ✓ | this checklist pasted; example rows left fenced, not copied |

**Reviewer cell:** `qa-reviewer` (Claude Sonnet, independent of the Kimi drafter and the orchestrator; read-only; 2026-10-10) — **APPROVE-WITH-CONDITIONS**, PASS-WITH-NOTES confirmed (nothing turns it into a FAIL). It re-collected 20 selectors (all non-zero, counts match), re-hashed all 7 cited evidence files (all match), confirmed Layer A covers all 7 HLR-MOD + 17 LLR-MOD and that AT-065 drives the real app (`tests/test_mod_parity.py:149`, widths :51). Conditions applied by the orchestrator: **M-1** the ledger names the 3 rewritten test functions; **M-2** this cell. LOWs applied: L-1 (`app.py` 340 lines), L-3 (golden capture commit `90e731b`, Inc-0, before any move). Noted: AT-065/067/069 realise in one FILE each with 3/3/2 nodes (parametrised widths + RED arm).
