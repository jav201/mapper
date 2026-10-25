# Re-check — architect — Batch 2026-10-23-hygiene-batch

> Second-pass P2 re-check of the author dispositions (F1, F2, m1, m2, m3) + PDR review of
> `design/design-proposal.md` (architect lens; template rows 1, 2, 4, 7, 8).
> All probes executed 2026-10-23 as `env -u NO_COLOR -u TERM <cmd>` equivalents (bare bash, no
> colour env set). Read-only review: nothing outside this evidence file was written.

## TASK A — P2 finding re-checks

### F1 (premise 5 re-measurement) — **verified** (one residual-drift nit recorded as new finding N1)

1. **Perf-workspace counts re-measured independently:**
   - `.dev-flow/2026-10-10-perf-batch/evidence/perf0b-ws-aa0oz3mw/p_nodos.yml`: `stat -c %s` =
     1,369,835 B ✓; node rows (`grep -cE '^  [A-Za-z0-9_]+:'`) = **12,000** ✓; sibling `p.mmd`
     = 523,879 B ✓, edge lines (`grep -c -- '-->'`) = **11,999** ✓.
   - `perf0b-ws-9aj_nwaw`: sidecar 1,357,836 B / 12,000 nodes; `p.mmd` 519,509 B / 11,999 edges ✓
     (matches premise 5's evidence cell exactly).
   - `perf0b-ws-o3psv_qz`: sidecar 55,839 B / 500 nodes; `p.mmd` 19,019 B / 499 edges ✓.
   - Full committed census (`find … -name '*.mmd' -o -name '*_nodos.yml' | stat | sort -rn`)
     confirms no larger sidecar or `.mmd` exists anywhere in the tree.
2. **Arithmetic:** 100,000/12,000 = 8.333… ✓ (8.3×); 100,000/11,999 = 8.334 ✓;
   8,388,608/1,369,835 = 6.124 ✓ (6.1×). The ≥5× floor is met; the old ≥10× floor would fail —
   the re-rule is recorded in ledger `LED-2026-10-23-hygiene-batch.5` and §6.3.
3. **Stale-figure grep over `01-requirements.md` + `PLAN.md`:**
   - `696,062`: zero hits ✓. `11.5`: zero hits ✓.
   - `16.7`: one hit (PLAN.md:127) — explicitly historical ("16.7× over the then-measured
     population; re-derived 2026-10-23 as 8.3× …") ✓ acceptable.
   - `≥10`: four hits (`01-requirements.md:183,360,596`; PLAN.md:141) — all record the re-rule
     ("fails R1's original ≥10× floor, passes the re-ruled ≥5× floor"), none asserts ≥10× as the
     current rule ✓.
   - `6,000 nodes` as a maximum claim: contract :183/:360 name wide6000 only as a measured shape
     while stating the largest committed map is 12,000 nodes ✓; **but PLAN.md:202's probe-record
     row still reads "largest measured = 6,000 nodes / 5,999 edges → caps 100,000/100,000"**
     without the re-measurement note that PLAN.md:127 carries → new finding N1.
4. **Anidado yaml-depth:** PyYAML event-stream scan with CollectionStart counting →
   `fixtures/anidado_nodos.yml` max depth **4** ✓ (also `fixtures/legacy_nodos.yml` = 4,
   `maps/legacy_nodos.yml` = 4 — matches premise 5's "anidado and legacy both measure 4").
5. **Fixture census:** legacy 1,536 B/8 nodes (both copies), anidado 861 B/7, truncado 323 B/3 ✓;
   `tests/goldens/perf/dump/wide6000.mmd` = 215,973 B ✓ (but see N2).
6. **Ledger:** `01-requirements-ledger.md` `LED-…batch.5` exists (:40) and matches the claim
   (population, 12,000/11,999, 8.3×, ≥5× re-rule, 11.5×→6.1×, anidado 3→4, asserting test
   `test_count_caps`, mutant M-Q2-4) ✓.

### F2 (L2 file set) — **verified**

- Contract §2.8 condition 2 (`01-requirements.md:203`): L2 = `store.py`, `diff.py`,
  `import_csv.py`, **`osopen.py`** (credited to `LED-…batch.6`); intersection ∅ re-stated;
  "each ≤ 4 SOURCE files — L2 = 4" ✓.
- `docs/ARCHITECTURE.md` §6 worksheet :295: L2 row lists all four source files with count **4** ✓;
  intersection rows :300/:302 ✓.
- PLAN.md: roadmap :36 ("`store`/`diff`/`import_csv`/`osopen` (Q2)"), per-story table :100
  ("4 source files"), lanes :113-114 (L2 = the four files), watch/risk rows updated ✓.
- ARQ commitments to edit `osopen.py` confirmed at `docs/ARCHITECTURE.md:65` (two inbound edges,
  reader's home), :121 (§3 osopen row commitment), :162 (store row), :165 (import_csv row),
  R-015 :274 ✓ — the table now matches them.
- Ledger `.6` (:47) matches, incl. the `test_arch_osopen_callers.py` same-landing discipline ✓.

### m1 (LLR count) — **verified**

- PLAN.md:65 now reads "3 US / 6 HLR / **11 LLR**" ✓.
- Independent count: `grep -c '^### LLR-' 01-requirements.md` = **11** (Q1.1.1; Q2.1.1-2.1.3;
  Q2.2.1; Q2.3.1; Q3.1.1-3.1.2; Q3.2.1-3.2.3 — 1+3+1+1+2+3) ✓.

### m2 (premise citations) — **verified**

- Premise 9 (`01-requirements.md:187`) cites `docs/ARCHITECTURE.md:200` and `:214`. Read:
  :200 is the §4 `Canvas` interface row ✓; :214 is the LANDED row quoting
  `Canvas(w, h, tones=(), fallback="")` ✓.
- Premise 12 (:190) cites `mapper/store.py:28-31` and `:58-61`. Read: :28-31 is
  `_RESERVED_NAMES = frozenset({"CON","PRN","AUX","NUL"} | COM/LPT… | {"CONIN$","CONOUT$","CLOCK$"})`
  ✓; :58-61 is the operative `check_map_id` refusal
  (`if map_id.split(".", 1)[0].rstrip().upper() in _RESERVED_NAMES: raise MapIdError(...)`) ✓.

### m3 (LLR-Q3.2.1 second limb) — **verified**

- Statement (`01-requirements.md:412`) now reads: "…under key `overprint` for every in-bounds
  write whose cell already holds a different alphanumeric character **and whose own written
  character is also alphanumeric**…" — R4's second limb is in the normative sentence ✓.
- Ledger `.8` (:61) matches (statement folded; asserting test `test_canvas_audit.py::test_events`;
  mutant M-Q3-2) ✓.

## TASK B — PDR review of `design/design-proposal.md` (template rows 1, 2, 4, 7, 8)

### Row 1 — Proposal complete — **✓**

§§1-6 all populated: objective per Q-module with id chains (§1); module/boundary table (§2);
four IFC-mirroring flows (§3); interface-change table with freeze column (§4); proposed test
cases each naming a reddening mutation or the move-aside counterfactual (§5); risks + rejected
alternatives that are REAL decisions already made and cited (R-015, R3+Q5, R4/B-136 — §6), no
fabricated second designs.

### Row 2 — Respects the boundaries of `docs/ARCHITECTURE.md` — **⚠** (one wording ambiguity, N3)

- "No boundary moves" ✓ — matches the ARQ (`docs/ARCHITECTURE.md:65`: "No module is created and
  no module boundary moves").
- Two new inbound edges into `osopen` (store, import_csv) ✓ — ARQ :65, R-015 :274, §3 rows
  :121/:162/:165 all name exactly those two and call them "the only importers of that one name".
- `import_csv → store` ban preserved ✓ — §3 import_csv row (:165) and R-015 both restate it.
- ⚠ Proposal §2's `diff` row ("No new imports beyond the shared reader") can be read as licensing
  a **third** `diff → osopen` edge that nothing else plans: the ARQ says TWO edges, R-015 says
  store + import_csv are the only importers, and the `ALLOWED_OUTSIDE_APP` amendment (§8) adds
  only `store.py` + `import_csv.py` — a direct `diff`-side import of the reader would redden
  `tests/test_arch_osopen_callers.py` mid-lane. The contract's own IFC already resolves the
  intended route (`01-requirements.md:466-473`: the prescan lives in `mapper.store` as
  `_prescan_sidecar`; `diff_against_git` takes "same caps applied" over its existing
  `diff → store` edge — `mapper/diff.py:11` already imports `MapStore`), so no new edge is
  needed; the proposal cell should say so. Cheap DDR-level fix → recorded as N3, not a block.

### Row 4 — Every requirement has foreseen coverage — **✓**

- Header id list (proposal :29): US-Q1-001/Q2-001/Q3-001; HLR-Q1.1, Q2.1-Q2.3, Q3.1-Q3.2;
  LLR-Q1.1.1, Q2.1.1-2.1.3, Q2.2.1, Q2.3.1, Q3.1.1-3.1.2, Q3.2.1-3.2.3 — matches the contract
  exactly (3 US / 6 HLR / 11 LLR, independently counted) ✓.
- §1 maps each US→HLR→LLR→AT→mutant chain to its lane; §5 carries every AT-108…116 into a
  proposed case ✓.

### Row 7 — Interfaces frozen for the fork are listed — **✓**

- **D1** `Canvas(w, h, tones=(), fallback="", audit=None)`: construction-site census re-run —
  `grep -rn "Canvas(" mapper/` returns **exactly 3** hits: `mapper/views/lane.py:199`,
  `mapper/views/layered.py:693`, `mapper/views/radial.py:184` ✓. B-44 pin read at
  `tests/test_a3_census.py:658-674`: asserts
  `list(inspect.signature(Canvas.__init__).parameters) == ["self","w","h","tones","fallback"]`
  plus the module-map row mention — i.e. it pins the CURRENT signature and must be amended in the
  same landing, exactly as the proposal schedules ✓.
- **D2** osopen bounded reader: `tests/test_arch_osopen_callers.py` exists (9,274 B) and derives
  the importer allow-list by AST walk (`_sources`/`_osopen_imports` :44-87;
  `ALLOWED_OUTSIDE_APP` :89; assertion `seen == ALLOWED_OUTSIDE_APP` :118-127) — adding
  `store.py`/`import_csv.py` to that dict is the correct amendment mechanism ✓. Current osopen
  public surface read (`grep '^def\|^class\|^[A-Z_]* =' mapper/osopen.py`): `open_external`,
  `safe_local_path`, `confine_reason`, `confine`, `refusal_sentence`, `is_link`, `hard_linked` +
  status/refusal constants — the reader name is NEW and frozen at PDR before the fork ✓.
- Third row (`MapStore.load`, no freeze needed, signature untouched) is honest ✓.

### Row 8 — Lane plan: file sets disjoint, family-B census per lane — **✓**

- §8 sets: L1 = {`mapper/app.py`}; L2 = {`store.py`, `diff.py`, `import_csv.py`, `osopen.py`};
  L3 = {`mapper/canvas.py`} — pairwise disjoint ✓; ≤4 SOURCE files per lane (L2 = 4, at budget,
  flagged for DDR row 7) ✓.
- Orphan/double-ownership check: every file the contract/ARQ commits to edit (app, store, diff,
  import_csv, osopen, canvas) appears in exactly one lane's set; test files are lane-suffixed
  (new: `test_colour_always_on.py` L1, `test_ingestion_limits.py` L2, `test_scalecheck.py` +
  `test_canvas_audit.py` L3; same-landing amendments: `test_arch_osopen_callers.py` L2,
  `test_a3_census.py` B-44 L3) — nothing orphaned, nothing double-owned ✓.
- Crossed reverse census spot-checks (proposal §8 block + PDR record §B condition row):
  - `MapStoreError` consumers: `grep -rn "MapStoreError" mapper/ --include='*.py'` → caught only
    at `mapper/screens/construct.py:57`; `screens/common.py:_save_or_toast` (:217) catches
    `Exception` incl. the `MapStoreError` subclass `MapIdError` (`_refusal_toast`,
    common.py:210-214); **zero hits in `mapper/app.py`** ✓ ("NOT app.py" holds).
  - `mapper/views/outline.py:311`: `Console(width=max(1, w), no_color=True)` — the pin exists as
    claimed ✓.
  - `tests/test_repair_store_boundary.py:884`: path-privacy pin (`str(tmp_path) not in
    str(caught.value)`) ✓; :401-431 the typed-refusal-net regression pin ✓.
  - `tests/test_help_scope.py:78-94`: the `monkeypatch.delenv("NO_COLOR")` fixture ✓; :247-274
    the legend-sample pin ✓.
  - `tests/test_repair_depth.py:109`: `MASTER_LEGACY_DIGESTS` ✓; :252-254 `_fingerprint` ✓.
  - `tests/test_perf_paint_clip.py:172`: `def test_render_grid_clip_identity` gating the render
    goldens ✓; `tests/goldens/perf/render/` holds exactly **16** golden files ✓.
  - No claim in the census block failed verification.

## NEW findings (this pass)

| ID | Severity | What | Evidence |
|----|----------|------|----------|
| N1 | minor | Residual stale figures survive the F1 fix: `01-requirements.md:601` and `PLAN.md:143` still measure the prescan watch-item against "the 696 KB perf sidecar" — no ~696 KB committed sidecar exists; the re-measured largest is 1,369,835 B. And `PLAN.md:202`'s probe-record row still claims "largest measured = 6,000 nodes / 5,999 edges" without the re-measurement note PLAN.md:127 carries. Record drift only; no requirement or cap value depends on it. | census `find … -name '*_nodos.yml' \| stat` (no file between 222,002 B and 1,357,836 B); PLAN.md:127 vs :202 internal inconsistency |
| N2 | minor | Premise 5's evidence cell claims "largest committed repo `.mmd` outside `.dev-flow` = `tests/goldens/perf/dump/wide6000.mmd` 215,973 B" — falsified by `tests/goldens/perf/at076_saved_wide6000_after_add_child.mmd` at **222,002 B**, same tree, same shape class. Inconsequential to headroom (both ≪ 523,879 B), but a precision defect in the premise whose fix was measurement precision. | full committed census (this file, F1 §1) |
| N3 | minor | Proposal §2 `diff` row ("No new imports beyond the shared reader") is readable as licensing a third `diff → osopen` edge that the ARQ (:65, "Two dependency edges"), R-015 (:274, "the only importers") and the `ALLOWED_OUTSIDE_APP` amendment plan (store.py + import_csv.py only) do not cover. The intended route needs no edge (prescan `_prescan_sidecar` lives in `store` per IFC `01-requirements.md:466-473`; `diff → store` already exists at `mapper/diff.py:11`). Resolve the wording before the seal so the L2 lane cannot redden `test_arch_osopen_callers.py` by accident. | proposal §2 diff row vs `docs/ARCHITECTURE.md:65`/:274 vs contract IFC |

## Verdict

- P2 re-check: F1, F2, m1, m2, m3 all **verified** against the live tree.
- PDR (architect lens): **approved with conditions** — the single condition is N3 (resolve the
  diff-row import wording before the seal); N1/N2 are trunk record-drift the author can fold into
  the same touch. Rows 1 ✓ · 2 ⚠ (N3) · 4 ✓ · 7 ✓ · 8 ✓.

`architect — Kimi K3 subagent executing agents/architect.md · approved with conditions`
