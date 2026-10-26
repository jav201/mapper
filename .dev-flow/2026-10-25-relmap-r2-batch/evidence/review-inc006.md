# Independent review — Increment 006 (lane L6): shell — Home enumeration + kind routing

| Field | Value |
|---|---|
| Batch | `2026-10-25-relmap-r2-batch` |
| Increment | `006` (lane L6, shell home+app) — lane commit `996b0ca`, reviewed at join HEAD `da6f10b` |
| Reviewer | independent increment reviewer — code + security + UX lenses; authored none of this increment |
| Lenses | `agents/code-reviewer.md` · `agents/security-reviewer.md` · `agents/ux-reviewer.md`; record per `templates/increment-template.md` §4b |
| Scope reviewed | 2 source files: `mapper/screens/home.py` (+142) and `mapper/app.py` (+4) + the 3 lane test files (`tests/test_relmap_shell.py` +458, `tests/test_relmap_isolation.py` +5, `tests/test_inc9c.py` +4) |
| Lane LLRs | RVH.1.1–1.3, 2.1–2.3, 3.1, 5.1/.5.2 (RVH.3.2/.3.3/.4.x host- or trunk-owned, read for context) |
| Verdict | **approve-with-nits** — 0 BLOCKER · 0 MAJOR · 2 MINOR (F1, F2) |

---

## 1 · The key question: does Home learn relation maps without lying about what the workspace holds?

The increment's load-bearing design decision is the derived-row condition: LLR-RVH.3.1 (as amended at `LED-2026-10-25-r2.29`, already integrated into `01-requirements.md:752`) requires the derived reqharness row **only while the default canon's file is present** at the workspace root. The implementation (`mapper/screens/home.py:109-114`) checks `(Path(workspace) / canon).exists()` before appending the row, and the docstring states the honesty rationale (no phantom row for a canon the workspace does not hold). This reading is coherent with AT-145 boundary (a) (`01b-acceptance-design.md:219-220`) and the packet's declared spec-reading (packet §1) is therefore **not** a deviation — it is the amended contract, and the amendment is on disk in the requirements file, not only proposed.

Second key question: does the shell route **by kind** without the descriptor ever being parsed at Home? Yes — `_open_recent` (`home.py:548-573`) hands the descriptor FILE path to `RelMapScreen(name, workspace, descriptor_path=entry.path)` for relation rows and no descriptor at all for the derived row (`home.py:573`), so derivation/refusal stay host-owned (`mapper/screens/relmap/screen.py`) and Home stays a discovery door only (`discover_descriptors`/`default_descriptor`/`DESCRIPTOR_SUFFIX` — the read-only D3 API; the census amendment in `tests/test_relmap_isolation.py` names exactly this, and `home.py` imports nothing from `mapper.relmap.adapter`).

Third: the emitted-form discipline. The badge cell is a stored `Text` with an exact span style (`home.py:399-401`), asserted character-exact by two arms (`tests/test_relmap_shell.py:765-796`); row keys stay backwards-compatible (tree rows key on the bare map name — gate-2 contract verified green below); hostile descriptor names are escaped at the one name sink (`home.py:403`).

---

## 2 · Findings

### BLOCKER — none.

### MAJOR — none.

### MINOR

**F1 — the recents NAME column also header-width-clips long names; the packet's rendering note names only the kind column.**
- **What:** the packet's measured pre-existing rendering note declares the kind-column clip (`legacy`→`leg`, `relation·reqharness`→`rel`). The same mechanism clips the **name** column: in the packet's own renders transcript (`evidence/p3-inc006-renders.txt:67,150`) the derived row paints `REQUIR   rel  —      —` — `REQUIREMENTS` truncated to `REQUIR` — at **both** 118 and 87. The stored/emitted cell carries the full stem (the AT-147 arms assert the stored form), so this is paint-only, but the derived row's canon-stem name is the one new long name this increment introduces onto this table, and "named by the canon stem" is only half-visible on the painted surface.
- **Where:** `mapper/screens/home.py:370` (`table.add_columns("▐ name", "kind", "nodes", "docs")` — unchanged pre-existing line), paint behavior visible in the lane's own renders.
- **Why it matters:** the packet's declared deviation is honest as far as it goes, and the mechanism is verifiably pre-existing (the pre-increment `home.py` (`996b0ca^`) carries byte-identical table construction and tree-row cells; my live probe reproduces `legacy → leg` on the landed tree). But the note is incomplete — the parked "home-table column-width fix" (packet §5) should explicitly cover the name column, or the derived row's identity on screen stays clipped.
- **Suggested fix:** fold the name column into the parked home-table width pass (no in-lane change; the packet already parked the class).

**F2 — new row-key collision class: a tree map named `<x>.relmap.yml.mmd` collides with the descriptor row keyed `<x>.relmap.yml`.**
- **What:** relation rows key on the descriptor FILE name (`home.py:101-103`), and `_recent_routes` is a dict keyed on the same value (`home.py:276`). A workspace holding both `demo.relmap.yml` and `demo.relmap.yml.mmd` (stem `demo.relmap.yml`) collides: the dict silently keeps the last entry, and the DataTable itself raises `DuplicateKey` on the second `add_row` — `on_mount` propagates it and Home dies. Before this increment, tree stems were unique among `*.mmd` and the seat rows could not collide.
- **Where:** `mapper/screens/home.py:101-103,276,402-408,457-463`.
- **Why it matters:** contrived filename, so MINOR not MAJOR — but it is a new crash-on-mount class introduced by the lane's key choice, and a one-line guard (dedupe check or kind-scoped key prefix for relation rows) removes it. The gate-2 contract only pins tree row keys = bare map name, so prefixing relation/derived keys is free.
- **Suggested fix:** key relation rows on a kind-scoped form (e.g. `f"relmap:{path.name}"`) or skip+notice on duplicate keys.

---

## 3 · Controls the reviewer re-ran (evidence states: executed)

| Control | Method | Result |
|---|---|---|
| Import provenance | `python -c "import mapper; print(mapper.__file__)"` with `PYTHONPATH=<worktree>` | resolves inside the worktree ✓ |
| Lane test run (commission's command) | `pytest -q -p no:cacheprovider tests/test_relmap_shell.py tests/test_relmap_isolation.py tests/test_inc9c.py` | **200 passed, 0 failed** (40s, exit 0) — 39 shell + 63 inc9c + 98 isolation nodes |
| Census spot checks tied to this diff | `pytest -q tests/test_a3_census.py tests/test_gate2.py` | **43 passed** — no `.render(`/`.toggle(` added; gate-2 row-key contract green (tree row keys unchanged by construction) |
| Evidence re-hash (C-59) | `sha256sum` of the packet's 5 evidence files | **5/5 MATCH** the packet's declared digests (see §6) |
| RED counterfactual cross-read | `evidence/p3-inc006-red-shell.txt` | `12 failed, 2 passed, 25 deselected`, exit 1, wall 5s; pre-edit sha256 of both source files in the header — matches packet §4 exactly |
| Live fidelity probe | reviewer pilot under `$TMP/r2-revl-l6/` driving `MapperApp(workspace=…)` via `run_test()` at 118×34 and 87×34 (workspace: `maps/legacy` pair + `demo.relmap.yml`) | see §5 |
| Pre-existing clip verification | live probe on the landed tree + `git show 996b0ca^:mapper/screens/home.py` static comparison of the table-construction and tree-row code | tree-row/table code byte-identical pre-increment → the `legacy → leg` clip predates the lane; the relation badge clip is the same unchanged column geometry |

---

## 4 · PDR-condition verification

**COND-QA-4 (L6-owned) — AT-147/AT-148 derivation observation must WRAP, not replace, `derive_reqharness_map` (C-16).** **SATISFIED.**

- The lane's derivation-args arm (`tests/test_relmap_shell.py:923-953`) captures `real = screen_mod.derive_reqharness_map`, appends `(repo, descriptor)`, **returns `real(repo, descriptor)`** — the real function executes, and the painted-skeleton assertion (`"HLR-DEMO.1" in painted`, `:955`) proves the real derivation produced the rendered map. A replacing stub would still pass the args probe but could not pass the painted assertion with honest data; a replacing stub returning a canned map is exactly what the wrap forbids.
- The lane's save-count arm (`tests/test_relmap_shell.py:887-907`) wraps `MapStore.save`/`create` the same way (counters call through to `_real`) and asserts `calls == []` after open + `r`.
- The carried AT-148 arms (`tests/test_relmap_shell.py:148-165,170-186`) wrap identically.
- **What would falsify:** a `monkeypatch.setattr` whose replacement does not call the original, or an assertion that never consumes the wrapped function's result. None present. The packet's §6 discharge claim ("both arms WRAP the real functions, never replace them") is accurate, and the inline comments name COND-QA-4 at both sites.

---

## 5 · Verdict fidelity vs the prototype

Prototype materials (main checkout, `prototypes/round-2026-10-23/`): `PROTOTYPE.md`, `verdict-2026-10-24.json`, `shots/png{,87}/`, `relmap/`. The verdict PNGs cover the three relation views; the Home recents surface has no verdict PNG — its fidelity contract is MAP-TYPES §6.2 (cited by HLR-RVH.1) plus the unchanged recents/hero chrome. The comparison below is therefore against the declared contract and the unchanged chrome, with the relation-screen chrome checked against the prototype bar (`reqharness / relmap / matrix · panel lens` crumb, view-name bottom bar).

| Width | Result | Detail |
|---|---|---|
| 118×34 | **match, one declared-deviation-accepted (+ F1)** | Home paints one name-sorted list `demo`/`legacy`; relation row `—`/`—`; kind column clipped `rel`/`leg` — the packet's declared pre-existing deviation, verified live and verified pre-existing by parent-code identity. Undeclared: none besides F1 (name column clips `REQUIREMENTS`→`REQUIR` on the derived-row fixture — same mechanism, not in the packet's note). Relation screen from the relation row: crumb `demo / relmap / matrix`, keybar `view 1 matrix 2 gaps 3 sheet … +10 ? all keys`, refusal lines painted (fixture canon absent) — chrome matches the prototype bar. |
| 87×34 | **match, same declared-deviation-accepted (+ F1)** | Identical behavior: list order and `—` cells unchanged; kind clip identical; keybar truncates honestly (`… +10 ? all keys`, 76 cells); crumb intact. No reflow, no overlap, no undeclared deviation. |

Declared-deviation honesty: the kind-column clip is declared where it exists (packet §4 rendering note + the renders transcript header NOTE) and behavior matches the declaration at both widths; the packet's claim that it treats tree and relation chips identically is confirmed live (`rel`/`leg` side by side). The declaration is incomplete only in not also naming the name column (F1). UX-acceptability: the clip is marginal-but-honest (stored cells full, badge distinguishes kinds even clipped); the parked home-table width pass is the right home for the fix. The PendingView relation body is declared mid-batch state (packet §5).

UX walkthrough declaration: the probes above are an **automated walkthrough through the real mechanism** (Textual headless driver, real keys `j`/`k`/`enter`/`q`, painted frames read via the compositor) — *performed* at both widths. **Expert inspection** against the prototype chrome — *performed* (chrome matches the static bar). **Evaluation with users:** *not performed — this team is one person and no user of this surface exists outside it.*

---

## 6 · Traceability and evidence re-hash

### Re-hash (C-59)

| Transcript | Recomputed sha256 (prefix…) | Packet-declared (prefix…) | Verdict |
|---|---|---|---|
| `evidence/p3-inc006-red-shell.txt` | `cd6c7534…c3b8c77c` | `cd6c7534…8c77c` | **MATCH** |
| `evidence/p3-inc006-green-targeted.txt` | `ad15bfbb…ca85218` | `ad15bfbb…ca85218` | **MATCH** |
| `evidence/p3-inc006-green-guards.txt` | `fa147904…fc835ca` | `fa147904…fc835ca` | **MATCH** |
| `evidence/p3-inc006-renders.txt` | `0430e812…6940b60` | `0430e812…6940b60` | **MATCH** |
| `evidence/p3-inc006-mutants.txt` | `380af94e…3b2a4` | `380af94e…b2a4` | **MATCH** |

5/5 MATCH. The transcripts are internally consistent with the packet: the RED run shows `12 failed, 2 passed, 25 deselected` exit 1; the mutants transcript shows 7/7 KILLED with restore digests equal to the landed `home.py` digest (my pre-review baseline, `83ae6235…`), and the runner's own BAD control is recorded there.

### LLR → AT → test → code traces (all verified on disk)

| LLR | AT | Test (oracle) | Code |
|---|---|---|---|
| RVH.1.1 | AT-145 | `test_llr_rvh_1_1_at_145_relation_rows_beside_tree_rows` (`test_relmap_shell.py:725`) — row_count==2, exact names/badges | `home.py:86-116,273-275,391-408` |
| RVH.1.2 | AT-145 kind cells | `…_1_2_kind_badge_values_and_chip_style` (:765, Layer 0) + `…_badge_census_painted_chip` (:779, stored `Text` + span style exact) | `home.py:70,399-401,451-454` |
| RVH.1.3 | AT-145 order | `test_llr_rvh_1_3_one_list_sorted_by_name_across_kinds` (:746) — alfa/delta/echo/hotel interleave | `home.py:115` |
| RVH.2.1 | AT-146 | `test_llr_rvh_2_1_at_146_open_routes_by_kind` (:816) — both kinds + `d`-inert + `q` home | `home.py:548-573`; `app.py:40,48-49,65` |
| RVH.2.2 | AT-146 negative | `test_llr_rvh_2_2_relmap_scope_binds_no_write_action` (:861) — census with planted positive control | seat (`keymap.py`, trunk-owned) + `RelMapScreen.BINDINGS` |
| RVH.2.3 | AT-146 | `test_llr_rvh_2_3_opening_a_relation_map_writes_nothing` (:880) — wrapping save-count, `calls == []` | routes at `home.py:564-573` (no store touch) |
| RVH.3.1 | AT-147 | `test_llr_rvh_3_1_at_147_derived_row_opens_via_default_descriptor` (:915) + derived-absent (:962) + empty canon (:972) | `home.py:109-114,573` |
| RVH.5.1 | AT-147 boundary (a) | `test_llr_rvh_5_1_at_147_boundary_missing_canon_refuses_from_home` (:1002) + K7 (:1028) — closed-set wording, no path, app lives | route to host refusal (`home.py:568-573` → `screens/relmap/screen.py`, host-owned) |
| RVH.5.2 | AT-145 boundary (b) | `test_llr_rvh_5_2_at_145_boundary_hostile_descriptor_name_renders_literally` (:1055) — stored escaped form + painted literal + crumb literal | `home.py:403` (`escape(entry.name)`) |

Every oracle is non-vacuous: fixtures seed both kinds, expected values are exact (names, badge strings, span styles, refusal wording), and each assertion would fail if the behavior were absent — the RED transcript proves 12 of the 14 arms see red on the unmodified tree (the 2 arms that stayed green are by design: the write-vocabulary census is the permanent guard over a trunk-owned clean seat, and boundary (a) asserts shipped behavior; both carry planted/instrument RED-proofs in the packet).

Source-file count: `git show --stat 996b0ca` — exactly 2 source files (`home.py` +142, `app.py` +4), within the ≤4 cap; test edits confined to the lane's own arms file plus the two census/pin files the packet names (each enumerated by its own failing census before edit, per the Correction population table — the re-pin comment and the isolation amendment comment are on disk and accurate; the re-pinned line 240 is the `notify(` call-site, matching the census's call-site-line convention).

---

## 7 · Reviewer mutation battery (control C-2 — mutants of my own, not the author's 7)

Runner: a throwaway anchor-replace runner under `$TMP/r2-revl-l6/` (no git). Every arm: save byte copy → apply → run the lane trio → restore from the byte copy → **restore sha256 verified against the pre-review baseline** (`home.py` `83ae6235…0233`; `app.py` `1ba185b2…cc8e`).

| Id | Site | Change (a plausible shortcut) | Instruments run | Verdict |
|---|---|---|---|---|
| M-REV-L6-1 | `mapper/screens/home.py:110-111` | the canon-presence condition deleted — the derived row lists for ANY descriptor-less workspace (reading RVH.3.1's first sentence without the r2.29 amendment) | lane trio (200 nodes) | **KILLED ×4** — `test_llr_rvh_1_1_at_145_boundary_no_descriptor_no_canon_tree_rows_only` (the intended arm: phantom `REQUIREMENTS` row), `test_inc9c_ux_f11_enter_on_home_is_a_seat_row_and_opens_the_selected_map` (phantom row sorts first, `↵` opens the wrong screen), and the two `test_inc9c_sec_f1` line-pins (B-113 failing loud on the line shift — by design). Restore `83ae6235…` MATCH |
| M-REV-L6-2 | `mapper/screens/home.py:403` | `escape(entry.name)` → `entry.name` — "Text cells don't parse markup anyway, drop the escape" | lane trio (200 nodes) | **KILLED ×1** — `test_llr_rvh_5_2_at_145_boundary_hostile_descriptor_name_renders_literally` (:1073, the stored emitted-form assertion: the cell no longer equals the escaped form). 201/202 others GREEN. Restore MATCH |
| BAD control | — | anchor string present ×0 in the source, mutant intentionally NOT applied | runner + baseline | runner reported `BAD: anchor not found`, rc=0, file sha256 unchanged — and the unmutated tree's test run is rc=0 by the Step-2 baseline (200 passed). **The harness cannot fabricate kills** |

Author's battery cross-check: the transcript's 7/7 KILLED claims re-read consistently with the arms on disk (each mutant maps to a named arm), restore digests equal the landed source digest, and the runner's own BAD control is recorded in-band. No independent re-application of the author's seven (my two arms target independently-chosen shortcut edits — the spec-reading shortcut and the markup-safety shortcut — and both were killed).

---

## 8 · Verdict

**approve-with-nits** — F1, F2.

The increment implements its lane of the contract faithfully: enumeration, badge, ordering, kind routing, the amended derived-row condition, and the refusal/markup-safety routing are all on disk, all traced to non-vacuous oracles, and the RED counterfactual, the 7/7 author mutants, and my 2/2 reviewer mutants all verify in the direction the packet claims. COND-QA-4 is genuinely satisfied — both instrumented arms wrap and call through, and the painted-skeleton assertion makes a replacing stub unpassable. Evidence is re-hashable (5/5) and the declared rendering deviation is honest at both widths. Both findings are MINOR and out of the lane's frozen scope: F1 asks only that the parked home-table width pass cover the name column the packet's note omitted, and F2 is a one-line hardening against a contrived-filename crash that no AT covers today. Neither blocks the join; both belong on the orchestrator's ledger.

| Lens | State |
|---|---|
| code | 2 MINOR (F1, F2) open — approve-with-nits |
| security | no findings — the one relation-name sink is escaped and pinned by a painted hostile-name arm; refusal lines carry closed-set causes with no path/exception text; the routes write nothing (save-count arm, `calls == []`) |
| ux | real-mechanism walkthrough passed at both widths except the declared (kind) + now-declared-here (name) column clips — pre-existing mechanism, parked fix; user evaluation not performed — one-person team, no external user of this surface |
