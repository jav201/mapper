# Requirements ledger — mapper — Batch 2026-10-11-fixes-batch

> Append-only. Entries are added in chronological order and never rewritten. The live
> contract is `01-requirements.md`; this file records how it came to say what it says.
> Every entry names the requirement it amends; every requirement names its entries. `V26`
> compares the two sets of pairs both ways.

### LED-2026-10-11-fixes-batch.1 — initial contract authored at P1

- **Requirement:** HLR-FX.1, HLR-FX.2, HLR-FX.3, HLR-FX.4, LLR-FX.1.1, LLR-FX.1.2, LLR-FX.1.3, LLR-FX.2.1, LLR-FX.2.2, LLR-FX.3.1, LLR-FX.3.2, LLR-FX.4.1, LLR-FX.4.2, LLR-FX.4.3, LLR-FX.4.4
- **Date:** 2026-10-11
- **What changed:** initial authoring of the live contract from the four READY stories of the P0 intake (B-115, B-116, B-117, B-127 → US-FX-001…004). Establishes the FX namespace (HLR-FX.1…4, LLR-FX.n.m), the acceptance ids AT-084…AT-087 (next free after the verified maximum AT-083), three increments (001 = B-115 + B-116, 002 = B-117, 003 = B-127), and mutants M-FX1…M-FX12.
- **Why:** the batch objective is four reproduced defects; every threshold is a byte-exact string, a count, or a recorded thread identity, and each LLR names the mutant that reddens it.
- **Evidence:** `01-requirements.md` §2.7 premises 1–8, each with executed output (AT-number grep; the `slugify` caller grep; the scratch-copy suite runs; the gated-git thread probe); `spike/intake.md` for the four P0 reproductions.

### LED-2026-10-11-fixes-batch.2 — ruling R1: a blank parent cell is no parent; an empty slug is never `n`

- **Requirement:** HLR-FX.1, LLR-FX.1.1, LLR-FX.1.2, LLR-FX.1.3
- **Date:** 2026-10-11
- **What changed:** an empty or whitespace-only parent cell means "no parent" (the row is a root candidate), decided before any slugging; a non-blank cell with an empty or unknown slug parks the row. `slugify` returns `""` when nothing survives instead of `"n"`; the CSV importer gives an id with no slug characters the next `row-N` id. Callers read: `import_csv.py:59` (row id), `import_csv.py:70` (parent cell), `screens/map/editing.py:115` (already `slugify(title) or "n"` with a uniqueness loop); the only test pin is `tests/test_mermaid.py:12` and it moves in increment 001.
- **Why:** the orchestrator's R1 asked for the safest behaviour after reading every caller. A raised error would make an importable spreadsheet unimportable, and a hash placeholder is non-deterministic and needed by no caller; returning `""` is honest, lets each caller choose, and leaves the one caller that wants a placeholder untouched.
- **Evidence:** premise 2 (caller grep), premise 7 (empty-parent, `N`-root and punctuation-parent reproductions; 14-file suite: only the slugify pin fails).

### LED-2026-10-11-fixes-batch.3 — ruling R2: the CSV root is chosen by parentage, not row order

- **Requirement:** HLR-FX.2, LLR-FX.2.1, LLR-FX.2.2
- **Date:** 2026-10-11
- **What changed:** after the edges exist, the root is the first row in file order with no parent edge that was not parked for a missing parent (fallbacks: first parentless row; else the first row). Other parentless rows keep the existing forest rule: attached under the root and parked with `? `. A genuine cycle is left unattached and still named by `find_cycle` at the preview and at save.
- **Why:** the base rule (the first row is the root, later parentless rows hang under it) closed a two-cycle for a child-first CSV; the existing forest rule (read in `import_csv.py`, orphan-attach block) is kept for more than one parentless row so no import result changes except where the root was wrong.
- **Evidence:** premise 7 (permutations: patched 24 of 24 one outcome with root `r`; base 6 of 24, 4 distinct outcomes; ring and ring-beside-root cycles still named).

### LED-2026-10-11-fixes-batch.4 — ruling R3: the declared root survives save and reload

- **Requirement:** HLR-FX.3, LLR-FX.3.1, LLR-FX.3.2
- **Date:** 2026-10-11
- **What changed:** `dump` writes the declared root's declaration line first, and drops its orphan-block twin, only when the root appears in the text, is no written edge's child, and is not already the first parentless node of the text; the decision uses bookkeeping inside the two existing edge passes (the 2E + 4 visit bound of LLR-PERF.2.2 holds). `parse` is unchanged. Pins moved in the same increment: the legacy-forest regression gains a root assertion and loses its R11 "root not compared" comment, the `_check_round_trip` docstring stops claiming drift, and the inline `orphan-order` arm of `test_dump_fixture_goldens` declares `root_id = "root"`. No golden FILE changes; no root comparison is added to the round-trip check.
- **Why:** a writer-side rule keeps existing single-root maps byte-identical (8 of 8 goldens, the AT-076 bytes). An unconditional root line moves the `forest` and `wide6000` goldens; a re-walk of the edges failed the visit bound (36000 > 12004) on the first draft. A root comparison in the round-trip check would refuse maps that open today.
- **Evidence:** premises 3 and 4 (suite run of `test_perf_dump`, `test_csv_safety_store`, `test_mermaid`; 8 of 8 re-parse arms); `tests/test_perf_dump.py:130-137` (the fixture whose root is `zeta`).

### LED-2026-10-11-fixes-batch.5 — ruling R4: the roles screen's git reads move to a worker, with no visible change

- **Requirement:** HLR-FX.4, LLR-FX.4.1, LLR-FX.4.2, LLR-FX.4.3, LLR-FX.4.4
- **Date:** 2026-10-11
- **What changed:** `identity.repo_root` and `identity.read` (three git calls) run in a Textual thread worker at mount and at resume; the facts return to the UI thread by `call_from_thread` and the file reads of `_load` run there from those facts. Until the first discovery returns the screen paints nothing (the four Statics stay as composed) and every key is silent and inert; on resume the previous paint stays; the latest discovery wins; keypress-time reloads reuse the cached facts and run no git. No new string, glyph, colour or key.
- **Why:** the operator's non-visual alternative. The existing hints cannot be used while loading: the default snapshot's inert hint says `no repo`, which would be untrue while git is still being read, and a wrong viewer or head must not be painted. Silence is the only copy that is not wrong.
- **Evidence:** premise 8 (gated-git probe: base blocks on the main thread; prototype records 3 of 3 calls off the main thread, empty and inert while gated, painted after release; 22 of 22 existing nodes pass with the helper wait).

### LED-2026-10-11-fixes-batch.6 — P1 findings that correct the P0 intake

- **Requirement:** LLR-FX.1.3, LLR-FX.3.1, HLR-FX.3
- **Date:** 2026-10-11
- **What changed:** (a) the intake's claim that `fixtures/legacy.mmd` is a forest is wrong: it has one parentless node (`erp`), so only the in-test forest of `tests/test_csv_safety_store.py` drifts; (b) the intake's proposal "`dump` emits the declared root first, forests whose root is an edge parent are unaffected" is replaced by the conditional rule of LED-2026-10-11-fixes-batch.4, because an edge-parent root that is not the first edge's parent also drifts (`b --> c`, `a --> d`, root `a`); (c) a CSV row whose id has no slug characters records the typed text as its `raw_id` and as the title fallback while its node id is `row-N`, so the existing collision record keeps showing what the operator typed.
- **Why:** each was found by executing the probe the draft-time rule requires rather than inheriting the intake's prose.
- **Evidence:** premise 5 (parentless-node listing of the shipped fixtures), premise 3 (`b --> c` / `a --> d` arm: base re-parses to `b`, patched to `a`).

### LED-2026-10-11-fixes-batch.7 — P2 MAJOR-1: a result that returns after the roles screen was popped is discarded

- **Requirement:** HLR-FX.4, LLR-FX.4.1, LLR-FX.4.2
- **Date:** 2026-10-15
- **What changed:** LLR-FX.4.1 now requires the screen to cancel its workers on unmount and the hand-back to check that the worker is not cancelled and the screen `is_mounted` before touching any widget; a late result is discarded with no paint, no notification and no exception. LLR-FX.4.2 adds that a result arriving after the pop is never applied. HLR-FX.4's statement, threshold and boundary catalog name the case. New node `test_roles_popped_screen_discards_late_discovery` (press `Esc` with the gate closed, release the gate, assert 0 exceptions, 0 notifications, 0 paints and that the app still answers a key). New mutant M-FX13.
- **Why:** P2 review MAJOR-1 (reviewer role `qa-reviewer`, model DeepSeek): `Esc` is allowed before the first load, and the original text did not say what a worker finishing on a dead screen does. Orchestrator ruling: discard, using Textual's worker cancellation and an is-mounted guard.
- **Evidence:** P2 review file (`screens/roles.py:649` `action_home` pops the screen; the in-repo analogue `screens/repo.py:259-265` guards its hand-back); disposition recorded in `02-review.md`.

### LED-2026-10-11-fixes-batch.8 — P2 MAJOR-2: the discovery catch names its exception types; the test seam is a monkeypatched function

- **Requirement:** HLR-FX.4, LLR-FX.4.1
- **Date:** 2026-10-15
- **What changed:** the worker wraps the two `identity` calls in `try/except (OSError, ValueError, subprocess.SubprocessError, ValidationError)` and maps any of them to the facts `(NO_REPO, None)`, painting the existing `no repo` state with its existing copy; any other exception type is a defect and propagates (the test asserts a `RuntimeError` surfaces). The failure seam is a monkeypatched function on `identity.repo_root` / `identity.read` that raises the chosen type; no production seam is added. New nodes `test_roles_discovery_failure_degrades_to_no_repo` (4 arms) plus the propagation arm. New mutant M-FX14.
- **Why:** P2 review MAJOR-2: `identity.repo_root` and `identity.read` already degrade without raising, so "a discovery that raises" had no reachable seam and no stated catch type. Orchestrator ruling replaces the reviewer's proposed bare `except Exception`, which would hide defects.
- **Evidence:** P2 review file (`reqharness/identity.py:201-206`); `ValidationError` is `mapper.reqharness.records.ValidationError` (`grep -rn ValidationError mapper`).

### LED-2026-10-11-fixes-batch.9 — P2 MINOR-1 and MINOR-2: counter discipline and depth-column parentage get explicit arms

- **Requirement:** HLR-FX.1, HLR-FX.2, LLR-FX.1.3, LLR-FX.2.1
- **Date:** 2026-10-15
- **What changed:** LLR-FX.1.3 states the `row-N` counter as one shared sequence that advances once per row that takes a `row-N` id, and adds threshold arms for an empty id cell with a punctuation-only title, an empty-slug row followed by an empty-id row, and an operator-typed `row-N` after an auto `row-N` (collision record, not renumbered). LLR-FX.2.1 defines a parent edge as built from the `parent` or `depth` column and adds the arm `a,A,,0` / `b,B,,1` / `c,C,,2` → root `a`, edges `{a→b, b→c}`, no `? `. HLR boundary catalogs updated.
- **Why:** P2 review MINOR-1 (ambiguous counter discipline, unpinned interleavings) and MINOR-2 (depth-column parentage absent from the root-selection truth table).
- **Evidence:** P2 review file (`import_csv.py:52-66`, `:93-98`); the depth semantics are re-confirmed against the code at the increment-001 RED proof.

### LED-2026-10-11-fixes-batch.10 — P2 MINOR-3 and MINOR-4: HLR/LLR agree on `Esc`; AT-085 uses the helper that can complete its save

- **Requirement:** HLR-FX.4, LLR-FX.4.3
- **Date:** 2026-10-15
- **What changed:** HLR-FX.4's statement now says every editing key (cursor keys, `space`, `a`, `r`) is inert before the first load while `Esc` keeps its existing action, matching LLR-FX.4.3. §5.1 (Layer B) points AT-085 at `tests/test_seed_safety.py::_open_import` (full `i`/path/`enter`/`s`/name/`enter` drive) and keeps `_import_and_press_save` for AT-084's preview-only assertion.
- **Why:** P2 review MINOR-3 (surface contradiction between an HLR and its LLR) and MINOR-4 (the named helper stops at `s` and cannot reach a typed-name save).
- **Evidence:** P2 review file (`tests/test_csv_safety_preview.py:76`, `tests/test_seed_safety.py:107`). The §5.1 edit has no requirement id of its own; it is carried by the HLR-FX.4 entry and the AT-085 named in HLR-FX.2 (see LED .9 for HLR-FX.2).

### LED-2026-10-11-fixes-batch.11 — P2 MINOR-5: Unicode scope is what `slugify` already does

- **Requirement:** HLR-FX.1, LLR-FX.1.1
- **Date:** 2026-10-15
- **What changed:** §1.2 declares that `slugify` keeps any `\w` character today (`niño` stays `niño`), that this is unchanged and is the whole Unicode scope, and that anything beyond it is out of scope. One non-regression arm is added (HLR-FX.1 threshold: `niño,Niño,` imports under id `niño`; LLR-FX.1.1: `slugify("Niño") == "niño"`), asserting exactly the base-tree behaviour.
- **Why:** P2 review MINOR-5: a non-ASCII label was neither covered nor declared out of scope. Orchestrator ruling: state what exists, prove no regression, specify nothing more.
- **Evidence:** P2 review file (`mermaid.py:49` `re.sub` with `\w`; `:31-33` `[\w-]+`).

### LED-2026-10-11-fixes-batch.12 — increment 004 (test-only), B-110: guard `exporting.py`'s own `pan_extent` read

- **Requirement:** HLR-FX.5, LLR-FX.5.1
- **Date:** 2026-10-15
- **What changed:** adds US-FX-005, HLR-FX.5, LLR-FX.5.1, AT-088, mutant M-FX15 and premise 9. One async test, node `tests/test_export_state.py::test_exporting_reads_pan_extent_through_its_own_module_global`, spies on `mapper.screens.map.exporting.pan_extent` (delegating to the real function), drives a real export, asserts the artifact exists and the call count is at least one. Rebinding `exporting.py` to `layered.pan_extent` must turn it RED while the rest of the suite stays GREEN. 0 source files.
- **Why:** the backlog carry B-110 (DDR CR-3): the sole patch site targets `panning.py`, so the export reader is unguarded.
- **Evidence:** read-only spike on B-110 and B-113 (`exporting.py:13,203`; `tests/test_en8.py:66`; `tests/test_mod_compat.py:59`; baseline `pytest tests/test_en8.py -k unlaid_out` → 1 passed).

### LED-2026-10-11-fixes-batch.13 — increment 004 (test-only), B-113: narrow the leak-exception key

- **Requirement:** HLR-FX.6, LLR-FX.6.1
- **Date:** 2026-10-15
- **What changed:** adds US-FX-006, HLR-FX.6, LLR-FX.6.1, AT-089, mutant M-FX16 and premise 10. `LEAK_EXCEPTIONS` in `tests/test_inc9c.py` is retyped `(file, lineno, expr)` (three keys at `home.py:175`, `screens/map/screen.py:214`, `common.py:213`), both consumers compare the full record, and a negative control proves a second `str(exc)` record in an excused file is reported. The backlog row's file pointer (`tests/test_inc9q.py`) is wrong: the coarse key lives in `tests/test_inc9c.py` (correction appended to `BACKLOG.md` B-113, original text kept). Accepted cost: the key is line-sensitive, so moving those three `notify` calls reddens the staleness check, by design.
- **Why:** the backlog carry B-113 (A2–A4+B0 group review, LOW).
- **Evidence:** spike quotes `tests/test_inc9c.py:266,291,299,305`; baseline `pytest tests/test_inc9c.py -k sec_f1` → 13 passed.

### LED-2026-10-11-fixes-batch.14 — PDR architect condition: the worker returns its facts; no `call_from_thread`

- **Requirement:** HLR-FX.4, LLR-FX.4.1
- **Date:** 2026-10-15
- **What changed:** LLR-FX.4.1 now says the thread worker RETURNS the discovered `(top, who)` facts and the screen applies them on the UI thread in `on_worker_state_changed` when the worker state is SUCCESS, after checking the generation of the worker that finished and `is_mounted`. `call_from_thread` is dropped from the statement, from premise 6 (the worker pattern stays, the hand-back does not) and from the §6.3 security paragraph. M-FX13 now removes the generation and `is_mounted` checks in `on_worker_state_changed`. The proposal (diagram, §6 rejected alternatives, §10 thread boundary, TC-FX-4.1b) and the ARQ note §3 follow.
- **Why:** PDR architect review, ruling R7: a `call_from_thread` from a worker still running at app exit can hang the exit; the state-changed route runs on the UI thread by construction.
- **Evidence:** PDR record `design/PDR-2026-10-11-fixes-batch.md` (conditions list C1); `mapper/screens/repo.py:259,267` is the pattern the screen no longer copies for the hand-back.

### LED-2026-10-11-fixes-batch.15 — PDR architect condition: the on-disk effect of the `dump` hoist is stated correctly

- **Requirement:** LLR-FX.3.1
- **Date:** 2026-10-15
- **What changed:** LLR-FX.3.1 gains an informative "Disk effect" line; `design/arq-note.md` §4 F2 and the proposal's §6 risk row are corrected. A map loaded from disk takes its root from `parse` (first parentless node in text), so the hoist does not fire on resave and bytes stay the same; it fires only when the root was set in-session (CSV import, or `editing.py:221` after a root delete). B-117 stops future drift; it cannot repair a map that already drifted, because the declared root was never stored. The earlier "one-time reorder on the next save" wording is withdrawn.
- **Why:** PDR architect review, finding F2 accepted as a correction, ruling R7. The same review adds a docs amendment owed at increment 003 (`docs/ARCHITECTURE.md:113`: `roles.py` in the `screens` row's paths, "`roles.py` owns `RolesScreen`" in its ownership prose, `RolesScreen` in its exposes list; the `mermaid` row note citing batch `2026-10-11-fixes-batch`); it is recorded in the ARQ note §1.2 and the PDR conditions, with no requirement id of its own.
- **Evidence:** `design/arq-note.md` §1.2 and §4; PDR record conditions C2 and C3.

### LED-2026-10-11-fixes-batch.16 — PDR ux condition: key bar subtraction while loading; painted reads; walkthrough honesty

- **Requirement:** HLR-FX.1, HLR-FX.2, HLR-FX.4, LLR-FX.4.3
- **Date:** 2026-10-15
- **What changed:** LLR-FX.4.3 adds that until the first facts arrive the key bar shows only the navigation keys and `Esc`, none of `space`, `a`, `r` (subtraction of existing chrome; no new string, glyph or colour), with a painted-frame assertion and mutant M-FX17 (key bar left unconditional). §5.1 declares that AT-084, AT-085 and AT-087 assert on the painted frame text, never on `update()` arguments (C-32). Walkthrough honesty and the real-user declaration are recorded in the proposal §9.4: the blank loading window is evidenced `executed (injected delay)` only (the harness cannot observe it at healthy git); real-user evaluation is `not performed — one-person team`. No extra status-line signal is added in this batch.
- **Why:** PDR ux-reviewer review, ruling R8 (J3 accepted as a subtraction; J4 closed with no signal; J1 and J5 go to the backlog).
- **Evidence:** PDR record conditions C4 to C6; backlog rows B-128 (J5) and B-129 (J1).

### LED-2026-10-11-fixes-batch.17 — PDR qa condition: counter-threshold arm and the `row-N` collision surface

- **Requirement:** LLR-FX.1.3
- **Date:** 2026-10-15
- **What changed:** LLR-FX.1.3's threshold gains the arm `,Alpha,` then `,,` imports ids `{alpha, row-1}` (a title-derived id does not advance the shared counter); TC-FX-1.3 carries it. Requirements §6.3 gains one sentence naming the `row-N` collision surface (cross-reference design proposal §10 and §9.1(d)). The optional large-forest dump scaling test is left as a note in the proposal §5, not a requirement.
- **Why:** PDR qa-reviewer review (light security lens), ruling R9; the BOM and quoted-newline findings are pre-existing and go to the backlog (B-130, B-131).
- **Evidence:** PDR record conditions C7 and C8.

### LED-2026-10-11-fixes-batch.18 — `is_mounted` → `is_attached` (increment 003 finding)

- **Requirement:** LLR-FX.4.1
- **What changed:** LLR-FX.4.1, the design proposal §3 and the ARQ note §3 named `is_mounted` as the hand-back guard. In Textual 8.2.8 `is_mounted` stays True after a screen is popped, so that guard can never fire; the shipped code checks `is_attached`. The texts now say `is_attached`.
- **Why:** found while implementing increment 003 (packet §deviations, finding 1); the framework already cancels a popped screen's workers, so the guard is the second line of defence and is exercised by a direct dead-screen SUCCESS arm (M-FX13 / M-FX13b).
- **Ruled by:** the orchestrator, 2026-10-15, under the standing authorization.
