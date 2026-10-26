# Increment 006 — HLR-RVH.1/.2/.3 · the shell — Home enumeration + kind routing (lane L6)

> **Artifact language.** Canonical **English scaffold**; generated in the batch's language.

| Field | Value |
|---|---|
| Batch | `2026-10-25-relmap-r2-batch` |
| Increment | `006` |
| Lane (if the batch forked) | L6 · the shell — `mapper/screens/home.py` + `mapper/app.py` (SOURCE **2**) |
| Requirement(s) | `HLR-RVH.1/.2/.3/.5` · `LLR-RVH.1.1–1.3, 2.1–2.3, 3.1, 5.1/.5.2` (RVH.3.2/.3.3, RVH.4.x are trunk-owned — read for context, not implemented here) |
| Acceptance | `AT-145` (enumeration + badge + hostile name), `AT-146` (routing by kind, read-only), `AT-147` (derived row, `default_descriptor()` args, non-git workspace, boundaries) — driven through the real app (`MapperApp(fixture workspace)` → Home → `↵` → `RelMapScreen`) |
| Agent | `software-dev` (lane L6, forked lane of the batch) |
| Date | `2026-10-25` |

---

## 1 · What changed

BLUF: Home learns relation maps. The recents build enumerates the workspace's
`*.relmap.yml` descriptors through the D3 discovery door
(`descriptor.discover_descriptors` — flat, code-point-sorted, ≤8) beside the
existing `*.mmd` glob in ONE name-sorted list (`_recent_entries`,
`mapper/screens/home.py`); each relation row carries the kind badge
`relation·reqharness` in the tree rows' chip style (`INK on STEP`), tree rows
keep their `legacy`/`concept` vocabulary untouched. When ZERO descriptors
exist AND the default canon (`REQUIREMENTS.md`) is present at the workspace
root, Home lists ONE derived relation row named by the canon stem
(`REQUIREMENTS`); opening it hands the host no descriptor, so the host derives
through `default_descriptor()` at open time. `↵` routes by kind
(`_open_recent`): tree rows push `MapScreen(map_id)` exactly as today, relation
rows push `RelMapScreen(name, workspace, descriptor_path=…)` — the descriptor
FILE is handed over, never parsed here, so a refused descriptor or canon
surfaces on the relation screen itself (LLR-RVH.5.1 stays host-owned), and no
route writes the store (LLR-RVH.2.3). `app.py` re-exports `RelMapScreen`
following the `MapScreen` pattern (the ARCHITECTURE-declared `app` →
`screens/relmap` edge). Row keys stay backwards-compatible: a tree row's key
is the bare map name (the gate-2 pin reads it back as the map id); relation
rows key on the descriptor file name, the derived row on `<stem>.derived`.

**Spec-reading declaration (load-bearing):** the derived row is listed only
while the canon FILE exists at the workspace root. LLR-RVH.3.1's "when the
workspace holds no `*.relmap.yml`, Home shall list one derived relation row"
is read together with AT-145 boundary (a) ("no `*.relmap.yml` → tree rows
only" — its natural fixture has no canon) and with the damaged-card honesty
doctrine (no phantom row for a canon the workspace does not hold): a plain
tree-maps workspace (like `maps/legacy`) gains NO row from this increment.
AT-147 boundary (a) (missing/corrupt canon → the closed-set refusal, app
alive) is fully honored through a DESCRIPTOR row — its refusal path is the
same host-owned door. A contract-clarification amendment is proposed in
Records to integrate.

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/home.py` | source | LLR-RVH.1.1–1.3, 2.1–2.3, 3.1, 5.1/.5.2 | EDIT — `_recent_entries` + `RELATION_KIND_BADGE`; the recents build enumerates descriptors + the derived row in one name-sorted list; `_open_recent` routes by kind; `action_open_selected` + `on_data_table_row_selected` share it; docstring updated |
| `mapper/app.py` | source | LLR-RVH.2.1 (the `MapScreen` pattern; `docs/ARCHITECTURE.md` §3 `app` row) | EDIT — `RelMapScreen` re-export (import + `__all__` + comment) |
| `tests/test_relmap_shell.py` | test | LLR-RVH.1.1–1.3, 2.1–2.3, 3.1, 5.1/.5.2 | APPENDED — 14 shell arms (AT-145/146/147 + boundaries + the M-RVH-5 census predicate `write_vocabulary_in`) |
| `tests/test_inc9c.py` | test | LLR-RVH.5.1 · B-113 (the one-excuse-one-site pin) | the `LEAK_EXCEPTIONS` line-pin re-pinned `176 → 240` with the comment updated (the ONLY possible editor per the PLAN Inc-6 row) |
| `tests/test_relmap_isolation.py` | test | LLR-RVH.1.1/.3.1 (ARQ census) | the importers census allows `screens/home.py` beside `app.py` (enumerated by the failing guard before the edit — see Correction population) |
| `.dev-flow/2026-10-25-relmap-r2-batch/evidence/p3-inc006-*.txt` | generated | US-RMV-004 | RED, GREEN ×2, mutants, renders — redacted, hashed |

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 2** |
| Test files | 4 (1 appended + 2 census/pin repairs + the isolation census amendment; uncapped) |
| Doc files | 0 (the ARCHITECTURE amendment is PROPOSED in Records to integrate — docs are outside the lane's file set) |

## 3 · How to test

```bash
PYTHONPATH=<worktree> python -c "import mapper; print(mapper.__file__)"
# targeted (shell arms + the re-pinned leak census):
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider \
  tests/test_relmap_shell.py tests/test_inc9c.py
# the guard set + the census files this diff touches:
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider \
  tests/test_fold.py tests/test_repair_artifact_claims.py \
  tests/test_relmap_isolation.py tests/test_a3_census.py \
  tests/test_arch_osopen_callers.py tests/test_mod_deps.py tests/test_no_operator_paths.py
```

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `full` | `_recent_entries` order/kind arm + the badge chip-style arm (stored `Text` + spans) + the write-vocabulary census predicate (planted rows) | passed (in the 102) |
| **A · white-box** `TC` ↔ LLR | `full` | `tests/test_relmap_shell.py` — 39 nodes (25 carried host arms + 14 shell arms) | passed |
| **B · black-box** `AT` ↔ story | `full` | AT-145/146/147 through `run_test()` REAL keys (C-16), non-default selection moves (C-10): enumeration + badge + hostile name, routing both kinds + `d`-inert, save-count, derived row + `default_descriptor()` args probe + no-invented-ids census, non-git workspace, missing/corrupt-canon refusals, empty-canon honest map | passed |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | none — the source files pre-exist; the pre-edit failing run IS the RED counterfactual (no move-aside: the shell arms assert absence of relation rows/routing on the shipped tree) |
| Instrument | project code, lane L6's hand |
| Where it ran | this worktree (wt-r2-shell), serialized with the battery |
| Transcript | `evidence/p3-inc006-red-shell.txt` — exit 1, `12 failed, 2 passed, 25 deselected`, wall 5s; pre-edit sha256 of both source files in the header |
| Restore proven by | nothing to restore (no source edit in the RED pass) |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` in every run (C-46) |
| Arms resolved at baseline | 12 RED arms (enumeration, order, badge ×2, routing, save-count, derived ×3, refusal ×2, hostile name), each seen failing |
| Verdict granularity | per arm |
| Arms that stayed GREEN | 2, BY DESIGN: the write-vocabulary census (the seat is trunk-owned and already clean — the arm is the permanent guard) and AT-145 boundary (a) (tree-rows-only is the shipped behavior on a descriptor-less workspace) |

| Field | Value |
|---|---|
| **RED counterfactual** | 12 RED arms on the unmodified home/app, transcript `evidence/p3-inc006-red-shell.txt` (sha256 `cd6c7534…8c77c`) |

### Mutation verdicts

| Field | Value |
|---|---|
| **Mutation verdicts** | 7/7 KILLED, per arm, restore sha256 proven for every file edit: M-RVH-1 (only `*.mmd` enumerated → enumeration arm RED) · M-RVH-2 (ALL-CAPS badge → badge arms RED, 2 nodes) · M-RVH-3 (relation rows appended after tree rows → order arm RED) · M-RVH-4 (relation row routed to `MapScreen` → routing pilot RED) · M-RVH-5 (write action in the relmap seat → the census predicate fires on the planted seat — the seat's only writable site, `keymap.py`, is trunk-owned, so the in-process planted-seat injection through the census predicate is the kill verdict, exactly like the arm's inline planted proof) · M-RVH-6 (the open path persists derived nodes → instrumented save-count arm RED) · M-RVH-7 (hard-coded non-default descriptor → derivation-args probe RED) · arms that stayed GREEN: none · transcript `evidence/p3-inc006-mutants.txt` (sha256 `380af94e…b2a4`), runner exit 0 |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `pytest` | the unmodified home/app (code-absent shell behavior) | `12 failed` — `evidence/p3-inc006-red-shell.txt` |
| the badge census (stored `Text` + spans) | M-RVH-2 applied (caps badge) | `assert relation_cell.plain == ' relation·reqharness '` — printed in the battery transcript |
| the write-vocabulary predicate | planted `save` / `osopen_launch` / `archive_map` rows | `['save', 'osopen_launch', 'archive_map']` — printed by the M-RVH-5 battery step and in the arm |
| the save counter | M-RVH-6 applied (planted `store.save` in the relation route) | `assert calls == []` — printed in the battery transcript |
| the derivation-args counter | M-RVH-7 applied (`Descriptor("reqharness", "OTHER.md", …)`) | `assert descriptor == default_descriptor()` — printed in the battery transcript |
| the mutation runner | its own BAD control (anchor ×0, `MUT_BAD_CONTROL=1`) | `M-RVH-0-BAD: BAD — anchor not found` and the battery stopped — control PASS, recorded in the battery transcript |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 6 instruments, each shown RED before its PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the recents kind cells (stored `Text` + spans — what Home emits into the table) | `cell.plain == ' relation·reqharness '` and a span with style exactly `#f5f5f5 on #262626`; the tree cell ` legacy ` in the same style | asserted in `test_llr_rvh_1_2_badge_census_painted_chip` / `…_kind_badge_values_and_chip_style` |
| the row-key set and order | `[str(k.value) for k in table.rows]` and the name cells across kinds | asserted in AT-145/1.3 arms (tree key = bare map name, gate-2 compatible) |
| the painted frame (crumb, keybar, notice) | `demo / relmap / matrix` crumb; the keybar line carries `matrix`/`gaps`/`sheet`; the K3/K7 refusal lines; the hostile `x[y]` painted LITERALLY; NO `US-`/`AT-`/`TC-` id shape in the whole derived-map frame | asserted in the AT-146/147 arms; frames in `evidence/p3-inc006-renders.txt` |
| **rendering note (pre-existing, measured)** | the recents kind COLUMN renders header-width-clipped (` legacy ` → `leg`, ` relation·reqharness ` → `rel`) | measured on **HEAD's** `home.py` too (scoped stash probe): the clip predates this increment and treats tree and relation chips IDENTICALLY; not introduced by this diff, not in this increment's file scope — reported for the orchestrator's UX ledger |
| **rendering note amendment (review-inc006 F1, declared 2026-10-25)** | the SAME header-width mechanism clips the NAME column: the derived row paints `REQUIREMENTS` → `REQUIR` at BOTH 118 and 87 (`evidence/p3-inc006-renders.txt:67,150`); the stored/emitted cells carry the full stem (the AT-147 arms assert the stored form), so this is paint-only, and it predates this increment (byte-identical table construction at `996b0ca^`) | the packet's original note named only the kind column; the name column is now declared — the parked home-table width pass must cover BOTH columns (BACKLOG B-159) |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 3 artifacts, each asserted on its emitted bytes, plus a measured pre-existing rendering characteristic |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED shell transcript | `…/evidence/p3-inc006-red-shell.txt` | `cd6c7534b7c08f38dc4ea9562f95e5f203a3885c4984f1a7f340c250c3b8c77c` |
| GREEN targeted transcript | `…/evidence/p3-inc006-green-targeted.txt` | `ad15bfbb69eac0045f6feab8b76cf2e5f3fdcee75991c3aa2b6b6f5b3ca85218` |
| GREEN guard+census transcript | `…/evidence/p3-inc006-green-guards.txt` | `fa1479043de994b01367d92db0cd89b1e75db7a253ed7cfcf6ff8787bfc835ca` |
| mutation battery transcript | `…/evidence/p3-inc006-mutants.txt` | `380af94e0de7d7cd62d51d141f998dd7ba0568d1884987d1827cdc02af13b2a4` |
| render captures (118 + 87) | `…/evidence/p3-inc006-renders.txt` | `0430e812a2bd0a2894930ea3583f4b274555a6c49d5ffb64bd2792f2a6940b60` |

All transcripts redacted (account name → `<user>`) with a PYTHON script before hashing; exit codes and wall time in each header.

| Field | Value |
|---|---|
| **Evidence files** | 5 artifacts, each at the declared home, cited with the digest of its stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — (a) the derived row appears only at ZERO descriptors AND a present canon; (b) the relmap seat binds no write action (trunk-owned, frozen at Inc-2) |
| If the result is an ABSENCE, what made the search wide enough | (a) the arms vary each limb: descriptors present (no derived row), no descriptors + canon (derived row), no descriptors + no canon (tree rows only); (b) `write_vocabulary_in` quantifies over the whole seat at runtime, derived from the shipped keymap |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_llr_rvh_2_2_relmap_scope_binds_no_write_action` pins a conclusion about the seat (a census, with its planted-violation proof); `test_d1_surface_names_are_frozen` (carried) pins the frozen surface |
| Conjunctive criteria: one mutation per conjunct | M-RVH-1/3 kill the two enumeration conjuncts (presence / order); M-RVH-2 the badge casing conjunct; M-RVH-4 the routing conjunct; M-RVH-6 the no-write conjunct; M-RVH-7 the default-descriptor conjunct; M-RVH-13/14-adjacent refusal wording/app-lives are pinned by the AT-147 boundary arms through the HOME route |
| Synthetic instance of the absent case | the AT-147 fixtures ARE the synthetic instances (non-git workspace, missing/corrupt canon, empty canon); the M-RVH-5 planted seat is the synthetic write-action case |
| **Positive control for every probe that returned an ABSENCE** | the fixture positive control (`test_fixture_canon_derives_honest_skeleton`, carried) derives the seeded 3-node map through the real adapter; the save-count arm clears setup noise and counts only the open; the badge/order arms assert positive rendered rows, not only absences |

### Reverse census — trigger family B, and A3

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by other tests | `grep -rln "RelMapScreen" tests/ mapper/` | `mapper/app.py` now imports it — EXPECTED (the re-export is this increment's deliverable, the ARCHITECTURE-declared edge); consumers unchanged otherwise |
| B2 file moved on disk | `git log --oneline -- mapper/screens/home.py` | no move — edited in place; not fired |
| B3 byte-identical golden captures this source | `grep -rln "home" tests/goldens/` | no goldens cover home; not fired |
| B4 artifact produced here is consumed elsewhere | `grep -rln "_recent_entries\|RELATION_KIND_BADGE" mapper/ tests/` | exactly one definition site (home.py) + the shell arms; the enumeration single-site rule (MAP-TYPES §6.2) holds |
| A3 interface consumed by another module changed | `grep -rn "\.render(" mapper/screens/home.py mapper/app.py` | zero `.render(` added — the A3 census (`tests/test_a3_census.py`) green |
| the gate-2 row-key contract | `tests/test_gate2.py` (not in this increment's run set — orchestrator's full run) | tree row keys stay the bare map name by construction (`_RecentEntry(mmd.stem, mmd.stem, "tree", …)`); the AT-145 arm asserts the emitted keys |

| Field | Value |
|---|---|
| **Reverse census** | 6 probes run (B1 · B2 · B3 · B4 · A3 · row-key contract); B2/B3 not fired; B1 fired as designed |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| the `LEAK_EXCEPTIONS` line-pin (`home.py`, the `str(exc)` site) | every dynamic `notify` interpolation over the product sources, keyed by (file, line, expr) | `tests/test_inc9c.py::test_inc9c_sec_f1_every_leak_exception_is_still_real` — the failure named the stale line 176 | 1 pin | `tests/test_inc9c.py` — re-pinned `176 → 240`, comment updated | none — the PLAN names this re-pin as Inc-6's own edit; B-113's one-excuse-one-site rule kept (one key, one site) |
| the relmap-importers census | every non-`relmap/` non-`screens/relmap/` module importing `mapper.relmap` | `tests/test_relmap_isolation.py::test_only_app_and_the_package_import_relmap` — AST census; the failure named `screens/home.py` | 1 module | `tests/test_relmap_isolation.py` — the allowed set becomes `{"app.py", "screens/home.py"}` with the reason comment | none — LLR-RVH.1.1/.3.1's draft-time verification names `descriptor.discover_descriptors` / `default_descriptor` for Home's recents build; the isolation census itself derives the population at runtime |
| every OTHER census the diff could touch | guard + census files | the guard run over `test_fold.py`, `test_repair_artifact_claims.py`, `test_a3_census.py`, `test_arch_osopen_callers.py`, `test_mod_deps.py`, `test_no_operator_paths.py` | 6 files | none — all green unamended | n/a — recorded to prove no silent stretch |

| Field | Value |
|---|---|
| **Correction population** | 3 corrections, each enumerated by its own failing census before its first edit (the guard run named every population member; no site was edited ahead of enumeration) |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|---|---|---|---|
| — (no supersession in this increment: no `.toggle(`/`.render(`/module-shape moves) | `grep -rn "\.toggle(\|\.render(" mapper/screens/home.py` → no hits | yes | n/a — recorded to show the inspection ran |

### Signed-balance test ledger

`post = base − deleted + added`: targeted pair `102 = 88 − 0 + 14`
(`tests/test_relmap_shell.py` 25 → 39 nodes, `tests/test_inc9c.py` 63 → 63 —
the re-pin moves no node; the 88 baseline = 25 carried host arms + 63 inc9c
nodes, run at lane entry). Guard+census set (seven files): `337 passed,
3 xfailed` (wall 58s, exit 0) — the two amended censuses reconcile per the
Correction population table, every other guard file unamended. New-arm
inventory (14):
AT-145 enumeration · 1.3 order · 1.2 unit · 1.2 painted chip · 1.1
boundary (a) · AT-146 routing · 2.2 write census · 2.3 save-count ·
AT-147 derived + args · 3.1 derived-absent · 3.1 empty canon · 5.1
missing canon · 5.1 corrupt canon (K7) · 5.2 hostile name.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer — Kimi K2.8 subagent executing agents/code-reviewer.md + agents/security-reviewer.md + agents/ux-reviewer.md · approve-with-nits → discharged fb336ed` |
| Review record | `.dev-flow/2026-10-25-relmap-r2-batch/evidence/review-inc006.md` (sha256 `3b9989db40420d9aae4a7f185cbb8770c7d90911391aa1d237417e7ca32506d9`) |

Follow-ups (2 MINOR, discharged in the review follow-up unit):

| Finding | Disposition | Evidence |
|---|---|---|
| F1 — the recents NAME column also header-width-clips long names (`REQUIREMENTS` → `REQUIR` at both 118 and 87); the packet's rendering note named only the kind column | **declared** — the same pre-existing mechanism (byte-identical table construction at `996b0ca^`), paint-only (the stored/emitted cells carry the full stem, asserted by the AT-147 arms); the packet's rendering note and §5 now declare the name column, and the parked home-table width pass is scoped to BOTH columns as **BACKLOG B-159** | packet rendering note (§4, amended) · `.dev-flow/BACKLOG.md` B-159 |
| F2 — a tree map named `<x>.relmap.yml.mmd` collides with the descriptor row keyed `<x>.relmap.yml` (`DuplicateKey` propagated out of `on_mount`; Home died) | **fixed**: relation rows key `relmap:<descriptor file name>`, the derived row `relmap:<stem>.derived` — the row keys are now disjoint by kind prefix while the tree key stays the bare map name (the gate-2 contract); arm `test_llr_rvh_1_1_row_keys_disjoint_across_kinds` (RED on the unmodified source: the reviewer's `DuplicateKey` reproduced); the reviewer's-shape mutant **M-REV-HOME-1** (prefix dropped) **KILLED**, restore sha256 MATCH; correction population: the failing `test_inc9c` `LEAK_EXCEPTIONS` census named the one sanctioned re-pin `240 → 246` (the `notify(` call-site line per the census convention; B-113 kept, one key one site) | `evidence/p3-inc006-followup-red.txt` (sha256 `56fa923c3977eb158fd4e1b304a450e0c1ef02879ba94feb21f323405251f8f9`) · `evidence/p3-inc006-followup-green.txt` (sha256 `c9b6d8c499cd45b625aa81c97f9d040554cff07b87d86d767a2678df1115e82a`, 203 passed) · `evidence/p3-inc006-followup-mutants.txt` (sha256 `ebc70e765bb2ade61982e63919a7b83e08eff28ade94df1ff5044975f00c2616`) |

## 5 · Risks

- The kind-column rendering clip (`legacy` → `leg`, badge → `rel` on the
  painted table) is PRE-EXISTING (measured on HEAD via a scoped stash probe)
  and hits tree and relation chips identically; this increment pins the
  emitted cell content. A home-table column-width fix is a UX change outside
  the Inc-6 file set — parked for the orchestrator. **Amended per
  review-inc006 F1:** the name column clips by the same pre-existing
  mechanism (`REQUIREMENTS` → `REQUIR` at 118 and 87) — the parked pass must
  cover both columns (BACKLOG B-159).
- The derived-row canon-presence reading is a declared spec interpretation
  (see §1); if the orchestrator reads LLR-RVH.3.1 as unconditional, the
  change is one condition in `_recent_entries` plus the boundary (a) arm —
  both named here.
- `discover_descriptors` caps discovery at 8 (overflow count currently not
  rendered on Home — no AT requires it; the honest-overflow declaration is a
  candidate for the home-table UX pass).
- Lanes 3/4/5 renderers are still `PendingView` in this worktree: the opened
  relation screen paints the placeholder body. Expected mid-batch state.

## 6 · Pending items / spec deviations

- None against the contract beyond the declared reading in §1. COND-QA-4
  discharged (both the derivation-args arm and the save-count arm WRAP the
  real functions, never replace them). C-10 discharged (every AT arm moves a
  non-default selection). C-16 discharged (REAL keys through `run_test()`).
- The shared-census edits applied by this lane (enumerated above):
  `tests/test_inc9c.py` (re-pin, unambiguously this lane's per the PLAN) and
  `tests/test_relmap_isolation.py` (amendment — applied so the lane's guard
  runs are green, exactly like trunk Inc-2 did for `screens/relmap`; no
  sibling lane touches this file).
- PROPOSED, not applied (Records to integrate): the ARCHITECTURE §3
  amendment naming home's D3 discovery edge, and the LLR-RVH.3.1
  canon-presence clarification.

## 7 · Suggested next task

The shell's second half — Inc-6b (help/palette arms) — then the join: every
lane's ATs on the joined tree (F-5), then Inc-7 (the hook bound). The
orchestrator schedules this increment's independent review (§4b) and the
records integration below.

## Records to integrate

Proposed, nothing applied beyond the lane's own files (the two census edits
above are applied and enumerated; everything here is for the trunk):

1. **Ledger entries** —
   `LED-2026-10-25-r2.19`: Inc-6 (lane L6, shell) landed: Home enumerates
   `*.relmap.yml` via `descriptor.discover_descriptors` beside `*.mmd` in one
   name-sorted list; relation rows carry the `relation·reqharness` badge
   (`INK on STEP`); `↵` routes by kind (`MapScreen` | `RelMapScreen`); the
   derived reqharness row appears at ZERO descriptors with the default canon
   present; `app` re-exports `RelMapScreen`.
   `LED-2026-10-25-r2.20`: the relmap-importers census allows `screens/home.py`
   (the D3 discovery door only) beside `app.py`.
   `LED-2026-10-25-r2.21`: the `test_inc9c.py` `LEAK_EXCEPTIONS` pin re-pinned
   `home.py:176 → 240` in the same increment (B-113 kept).
2. **PLAN test-ledger rows** — Inc-6: `tests/test_relmap_shell.py` +14 nodes
   (25 → 39); `tests/test_inc9c.py` 63 → 63 (pin move); guard+census set
   +14 (`337 passed, 3 xfailed`); targeted pair 88 → 102.
3. **Contract clarification (exact text)** — LLR-RVH.3.1 Statement, append:
   "The derived row is listed only while the default canon's file is present
   at the workspace root; a workspace with no descriptor and no canon lists
   tree rows only (AT-145 boundary (a))." And AT-147 boundary (a), append:
   "driven through a descriptor row when no descriptor exists to list."
4. **ARCHITECTURE amendment (exact text)** — §3 `screens` row, append to the
   dependency cell: "*(amended `2026-10-25-relmap-r2-batch` Inc-6: `screens/
   home.py` MAY import `mapper.relmap.descriptor`'s read-only discovery API
   (`discover_descriptors`, `default_descriptor`, `DESCRIPTOR_SUFFIX`) — the
   census record is `tests/test_relmap_isolation.py`)*".
5. **UX ledger** — the pre-existing recents kind-column clip (header-width
   columns; `legacy` → `leg`) measured on HEAD — candidate for the home-table
   width pass.

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 2/2 — home.py + app.py, exactly the PLAN Inc-6 row |
| 2 | Tests written in this same increment | all | ✓ | 14 shell arms appended, run RED-before-GREEN (12 RED on the unmodified tree) |
| 3 | Layer 0 written where the criterion applies | `full` | ✓ | the `_recent_entries` unit arm (branchful: kinds + the derived-row condition) + the badge chip arm + the census predicate |
| 4 | RED counterfactual declared | all | ✓ | 12 RED arms on the unmodified home/app, transcript `evidence/p3-inc006-red-shell.txt` (sha256 `cd6c7534…8c77c`, exit 1) |
| 5 | Reverse census declared | all | ✓ | §Reverse census — 6 probes; B2/B3 not fired; B1 fired as designed (the app re-export) |
| 6 | `code-reviewer` passed | all | ⚠ | `pending — orchestrator schedules` (§4b) |
| 7 | No file from another lane touched | all | ✓ | only home.py + app.py (lane set), the lane's own arms file, the two named census/pin files; no `matrix.py`/`gaps.py`/`sheet.py`/host/keymap edits |
| 8 | Frozen interfaces untouched (or returned to the trunk) | all | ✓ | D1 (base.py) / D3 (the seat) / the host (screen.py) untouched — the shell routes TO the host, never edits it |
| 9 | Coverage claims verified on disk | all | ✓ | 102 targeted nodes + 337 guard nodes collected on disk in the final runs |
| 10 | Load-bearing emptiness declared | all | ✓ | §Load-bearing emptiness — positive controls named per absence |
| 11 | Mutation verdicts declared | all | ✓ | 7/7 KILLED per arm, restore digests cited, battery exit 0 |
| 12 | Instrument RED-proof declared | all | ✓ | 6 instruments each shown RED first (incl. the runner's own BAD control) |
| 13 | Correction population declared | all | ✓ | 3 corrections, each enumerated by its failing census before its first edit |
| 14 | Emitted-form assertion declared | all | ✓ | 3 artifacts asserted on emitted bytes (cells, keys, painted frames) + the measured pre-existing clip |
| 15 | Independent review names somebody | all | ✓ | `pending — orchestrator schedules` (§4b) |
| 16 | Evidence files declared | all | ✓ | 5 files at `artifact_homes.evidence`, digests of stored bytes |
