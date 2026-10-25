# Design proposal — mapper — Batch 2026-10-25-relmap-r1-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language
> The normative rules below are language-independent. **Where that language is declared:**
> `state.json`'s `language` key in `core` and `full`.

> **Reserved field names.** The **field names and block keywords below are language-independent** — the
> validator parses them literally and they are never translated:
> `Design proposal` · `7 · Forward-applicability table` · `⏸ DEFER`
> Everything else on this page — headings, guidance, the prose in every cell — is translated with the batch.

> **Owed in.** `core` by trigger · `full` ✓ (PDR stands: trigger A1 fired).

> **Where this lives.** The hygiene batch kept its proposal and PDR record under `.dev-flow/<batch>/design/`; this batch does the same, and cites decisions by id (by decision number). What binds code also lands in the requirement or in `docs/ARCHITECTURE.md`.

> **The forward-applicability rule (ISO/IEC/IEEE 15288).** Every section below is named as the input of a later activity (§7). Status: **revised 2026-10-25 after the third P2 pass and the four PDR reviews (architect, QA, security, UX — all approved with conditions); every condition is dispositioned in the PDR record §A and in ledger `.29…43`.** Nothing here relitigates OQ-R1-1…8 or rulings R1–R16.

| Field | Value |
|---|---|
| Id | `PDR-2026-10-25-relmap-r1-batch` |
| Requirements covered | `US-RM-001…004 · HLR-RMP.1/.2, RMM.1/.2/.3, RMG.1, RML.1, RMA.1, RMU.1 · LLR-RMP.1.1/.1.2/.2.1, RMM.1.1/.1.2/.1.3/.2.1/.2.2/.3.1, RMG.1.1/.1.2/.1.3, RML.1.1–.1.6, RMA.1.1–.1.4, RMU.1.1–.1.4 · AT-117…AT-122, AT-124…AT-129 · TC-RM-01/02/03` (contract `01-requirements.md`, ledger `LED-2026-10-25-relmap-r1-batch.1…43`) |
| Modules touched (from `docs/ARCHITECTURE.md`) | `relmap` (new) · `yamlscan` (new) · `store` · `reqharness` (`audit.py` only) · `app` · read-only `osopen`, `reqharness.derive` |
| Triggers that fired | `A1 · A2 · A3 · B1 · C6 · D1 · E1 · F2` (PLAN §Triggers); A4 not fired — one chain, no lane |
| Author / reviewers | `software-dev` (author) · `architect` · `qa-reviewer` · `security-reviewer` (C6) · `ux-reviewer` (D1 — owed at PDR: the only user-visible surface is the `--audit` text block) |

---

## 1 · Objective and scope

**Objective.** Ship the headless core of the relation-map kind in five sequential increments: the `reqharness` profile as data, a typed multi-parent read model, a generic gap detector, bounded relation-file reads, a read-only canon adapter, and the structure block that `mapper --audit <repo>` prints after the verdict line — without moving one existing report line or the exit code, and without touching the tree kind.

**In scope (design level).** Module layout and import order of `mapper/relmap/`; the leaf `mapper/yamlscan.py` and the byte-identical delegation in `mapper/store.py`; the frozen public names and signatures (§4); the per-increment file sets with the allow-list landings (§2.1); the test plan with a RED counterfactual per new file and a mutant per LLR (§5); the reverse census (§5.2).

**Explicitly not.** Any screen, view, matrix or lens (R2); evidence search (R3); timeline (R4); `lineage`, metro, `_map.yml` (R5); editing typed edges; US/AT/TC nodes (B-141); repairing the 7 unparsed canon rows (B-142); folding `reqharness/config.py`'s prescan into the leaf (B-144); any change to `model.py`, `mermaid.py` or the tree `Graph`.

**Mapping chain → increment.** US-RM-001 → Inc-1 (profile, model), Inc-4 (adapter) · US-RM-002 → Inc-2 (gaps) · US-RM-004 → Inc-3 (yamlscan, store, descriptor) · US-RM-003 → Inc-5 (audit, hook).

## 2 · Modules and boundaries

| Module | What it owns here | What it exposes | What it must NOT reach into |
|---|---|---|---|
| `relmap.profile` | `Profile`, `EdgeType`, `GapRow` frozen values and the `REQHARNESS` table (edge types, allowed pairs, direction, evidence, 8-row gap catalogue with sentence templates) | `Profile`, `EdgeType`, `GapRow`, `REQHARNESS` | everything in `mapper` (it is the leaf) |
| `relmap.model` | `Node`, `Edge`, `Problem`, `RelMap`, `build_map`, iterative up/down/reach/neighbourhood/cycles, caps, the per-map visit budget (`VISIT_BUDGET`, `RelMap.visits`), `DISPLAY_MAX` and `cut` | those names, `RelMapLimitError` | `gaps`, `descriptor`, `adapter`, `audit`, `store`, `model` (tree) |
| `relmap.gaps` | generic detectors over `Profile.gaps` (four patterns), qualified sentences, ranking inside the map's visit budget | `Gap`, `detect_gaps`, `rank_gaps` | any kind/edge/gap-kind literal; `descriptor`, `adapter`, `audit` |
| `relmap.descriptor` | `read_repo_text`, the closed causes K1–K17 (a read-only `CAUSE` mapping), descriptor load/schema/path confinement, discovery, the default descriptor | `RepoReadError`, `DescriptorError`, `Descriptor`, `default_descriptor`, `CAUSE`, `read_repo_text`, `refusal_line` (as built Inc-3, ledger .56), `load_descriptor`, `discover_descriptors` | `adapter`, `audit`, any write, any open of `us_canon`/`at_table` |
| `relmap.adapter` | canon → `RelMap` (rule D-1, notes, `unparsed`, status words), read-only | `CanonUnavailable`, `Derivation`, `derive_reqharness_map` | `audit`, any file but the canon (opened only through `read_repo_text`), write, process |
| `relmap.audit` | the line formats, the informational header, truncation (inside `format_structure`), determinism, derive-once, `structure_lines` (returns UNESCAPED lines) | `format_structure`, `structure_lines` (`refusal_line` is defined in `relmap.descriptor` and imported here, ledger .56) | `reqharness.audit` (the hook is injected from `app`), Textual, Rich |
| `yamlscan` | the one iterative prescan, `ANCHOR_NAME_DISPLAY`, `YamlLimitError` | `prescan`, `YamlLimitError`, `ANCHOR_NAME_DISPLAY` | file reads, operator wording, any other `mapper` module |
| `store` | the two call sites, converting `YamlLimitError` to `MapStoreError` with byte-identical text | unchanged | `relmap` (never imports it) |
| `reqharness` (`audit.py`) | the optional `extra_lines` parameter, the fixed unavailable / truncation lines, the bounded consumption of the hook (1,000 lines) | `run_cli(argv, extra_lines=None)` | any import from `relmap` |
| `app` | passing `relmap.audit.structure_lines` into `run_cli` | unchanged | — |

- Boundaries respected as declared in `docs/ARCHITECTURE.md` (§2 rows `relmap`, `yamlscan`; §3 rows `relmap`, `yamlscan`, both `osopen` cells; R-016, R-017 incl. alternative (d)): **✓** — no boundary moves. Internal order (acyclic): `profile` ← `model` ← `gaps`; `profile`, `model` (for `cut`, ledger .57), `yamlscan`, `osopen` ← `descriptor` ← `adapter` (also `model`, `reqharness.derive`) ← `audit` (also `gaps`, `descriptor`, `model`). The ARCHITECTURE `relmap` row's internal-order sentence is amended to `audit` → `adapter`, `gaps`, `descriptor`, `model` (architect PD-4; done at the seal).
- `relmap` imports from `mapper`: `osopen` (`read_capped`, `ContentReadError`, `MAX_MAP_BYTES`, `MAX_NODES`, `MAX_EDGES`, `confine_reason`, `is_link`), `yamlscan`, `reqharness.derive` (`parse_canon`, `CanonObject`, `LIMIT_ROLES_YML_BYTES`). `reqharness` imports nothing from `relmap`; `app` is the only outside importer.
- Deliberate divergence recorded in the `relmap` row: the canon reader refuses a symlinked canon where `load_canon` follows it (architect N-2).

### 2.1 Per-increment file sets (SOURCE ≤ 4 each; tests uncapped)

| Inc | SOURCE files | New tests / fixtures | Same-landing edits (not source) | Exit checks |
|---|---|---|---|---|
| 1 | `mapper/relmap/__init__.py` (empty), `relmap/profile.py`, `relmap/model.py` — **3** | `tests/test_relmap_profile.py`, `test_relmap_model.py` (incl. `test_reach_memo_is_counts`, `test_reach_budget_per_row`), `test_relmap_isolation.py` (incl. TC-RM-01, `test_py310_floor`) | allow-list entry `relmap/model.py: {MAX_NODES, MAX_EDGES}` in `tests/test_arch_osopen_callers.py`; both ARCHITECTURE osopen cells; §2 `relmap` row paths | profile+model+isolation tests; `test_arch_osopen_callers`, `test_repair_map_truth`, `test_mod_*`; `mapper.__file__` probe; measured wall time |
| 2 | `mapper/relmap/gaps.py` — **1** | `tests/test_relmap_gaps.py` (incl. `test_rank_visit_cap` with the `down` tripwire, `test_rank_limit_none`; NO snapshot test here: `test_snapshot_gaps` is Inc-4) | §2 row path | gaps tests; isolation census (no literal in `gaps.py`); measured wall time |
| 3 | `mapper/yamlscan.py`, `mapper/store.py`, `mapper/relmap/descriptor.py` — **3** | FIRST `tests/test_prescan_refusal_goldens.py` (8 constants generated by RUNNING the base `store.py`; capture command and base SHA in the packet; committed ALONE before the `store.py` commit), then `tests/test_yamlscan.py`, `tests/test_relmap_descriptor.py` (incl. the in-process Layer A stand-in `test_descriptor_cause_texts`, `test_cause_is_read_only`, the junction arm, the bytes-read and `st_ino = 0` arms) | allow-list: `yamlscan.py: {MAX_DEPTH}`, `relmap/descriptor.py: {read_capped, ContentReadError, MAX_MAP_BYTES, confine_reason, is_link}`, `store.py` loses `MAX_DEPTH`; ARCHITECTURE osopen cells and §2 paths | golden GREEN at its own commit (store untouched) and after the move; `test_ingestion_limits` unchanged; allow-list equality; fixture-content census (§5.2); measured wall time |
| 4 | `mapper/relmap/adapter.py` — **1** | `tests/test_relmap_adapter.py` (incl. `test_snapshot_gaps`, `test_snapshot_sha256`, `test_snapshot_sha256_crlf_arm`, and the in-process stand-in `test_snapshot_structure_figures` asserting the AT-117/AT-119/AT-125 figures); fixture `tests/fixtures/relmap/REQUIREMENTS.snapshot.md` (LF bytes from `git show HEAD:REQUIREMENTS.md`, LF-normalised sha256 `b093c920…`) | §2 row path; `.gitattributes` gains `tests/fixtures/relmap/** -text` (config, not source) | snapshot census exact; live invariants; `test_snapshot_sha256` re-run from a fresh LF checkout; tripwire `test_report_line_shape_yields_id`; measured wall time |
| 5 | `mapper/relmap/audit.py`, `mapper/reqharness/audit.py`, `mapper/app.py` — **3** | `tests/test_relmap_audit.py` (TC-RM-02, TC-RM-03, AT-117…AT-129 subprocess arms, `test_canon_derived_once`, `test_hook_line_bound`, `test_format_structure_cuts_inside`, `test_refusal_line_hostile_name`, `test_header_first`); `tests/_relmap_fixtures.py` (test helper: IMPORTS `_seed`, `_git_repo`, `_write_canon`, `_audit_cli` from `tests.test_reqharness_release`, adds relmap wrappers; not a copy, and `test_reqharness_release.py` is not edited) | §2 row path; `docs/ARCHITECTURE.md` interface note for `run_cli`, the verdict-by-prefix note, the UNESCAPED/visit-budget notes | `test_reqharness_release` (incl. the hostile-canon arms at `:665-680`, `:755-770`), `test_reqharness_baseline`, `test_reqharness_modgraph`, `test_a3_census` (pin `:329` = 86), `test_mod_structure` (`app.py` 360 → ≤ 400); measured wall time, `test_relmap_audit.py` budget about one minute |

Every increment runs only its targeted tests (`env -u NO_COLOR -u TERM`, `PYTHONPATH=<worktree>`, `mapper.__file__` probed inside the worktree, new files `git add`ed before the A3 census); the orchestrator schedules the one full run.

**Layer phasing (QA D-4).** The twelve Layer B ATs run `mapper --audit` through the hook that lands in Inc-5, so Layer B evidence FIRST exists at Inc-5. Inc-3 and Inc-4 each run an in-process Layer A stand-in that already asserts the figures the ATs will check (the descriptor cause texts at Inc-3; `derive_reqharness_map` over the snapshot with 275/196/7/3, the 8 notes and the 7 gaps at Inc-4), so a defect surfaces in its own increment. **Timing (QA D-9).** Heavy arms (100,000-node chain, hub shape, 100,000 sinks, 8 MiB cap±1, the two-seed subprocess runs, about 12 ATs each building a git repo and spawning `python -c`) live in separately named functions; each increment packet records the measured wall time; the estimate for `test_relmap_audit.py` is on the order of a minute (about 40 subprocess runs at 1-2 s), each run inside its 60 s timeout.

## 3 · Diagrams

**Structure (import order).**

```
osopen ──────────────┐
yamlscan ───────┐    │
profile ─► model ─► gaps ─────────────┐
   │        │                         ▼
   └────────┴─► descriptor ─► adapter ─► audit ◄── (injected by) app ──► reqharness.audit.run_cli
reqharness.derive (parse_canon, CanonObject, LIMIT_ROLES_YML_BYTES) ───► adapter
store ──► yamlscan          (store never imports relmap; reqharness never imports relmap)
model ──► descriptor        (as built Inc-3: `descriptor` imports `model.cut` to cut the base name it prints; accepted, ledger .57)
```

**Interaction — `mapper --audit <repo>`.**

```
app.main ─► run_cli(argv, extra_lines=structure_lines)
   audit() ─► Report ─► print existing report, `verdict:` line (unchanged)
   Report is no-repo / no-registry ─► print one fixed `structure: unavailable (…)` line (told apart by `report.chain_status`: `identity.NO_REPO` / `NO_REGISTRY`), hook NOT called; `audit()` raising (the `--baseline` refusal) ends before any report: no structure line, hook NOT called
   else extra_lines(Path(report.repo)):
        the informational header first, then:
        discover_descriptors ≤ 8 (sorted)           ── each: read_repo_text → load_descriptor ─► Descriptor | DescriptorError(Kn)
        read_repo_text(canon) → parse_canon (ONCE)  ── CanonUnavailable(K1–K7) → `unavailable (canon: …)`
        derive_reqharness_map → RelMap + notes → detect_gaps → rank_gaps(limit=20)
        per descriptor: format_structure(...) → block | refusal line      then overflow line
   every returned line ─► the report's escaper ─► stdout; exit code = the verdict's
   callable raises ─► `structure: unavailable (internal error: <Type>)`, same exit code; more than 1,000 hook lines ─► 1,000 printed + `structure: output truncated at 1000 lines`
```

**Algorithm — rule D-1 and the qualifier.** LLR id minus its last dotted segment, prefixed `HLR-`, is the parent only when that node is an HLR. An *orphan row* (a reported row, or an unlinked LLR) is *related* to `HLR-<s>` when its stem starts with `<s>.`, or when it is unlinked/reported and its D-1 candidate stem equals `<s>` minus its last segment; `Node.unparsed` counts them and the `lacks_*` sentence ends `(canon rows near this id could not be parsed or linked: <n>)`. Snapshot canon: 7 gaps, `HLR-CAN.1` and `HLR-REPAIR.1` qualified (2 each).

**Algorithm — bounded ranking.** Gaps sort by severity; reach only breaks ties within a band, so only the bands needed to fill `limit` (all of them when `limit=None`) get a reach; one BFS per node reading adjacency through `RelMap.down` (count memoised, never a set), once per cycle component. The map carries ONE budget of 2,000,000 node expansions (`RelMap.visits`), shared by `reach` and `rank_gaps`: a traversal that would pass it is abandoned and `reach` returns `None`; the gap then ranks with reach 0 and is counted in `reach_not_computed`. The `down` seam is also where the tests count (LED .32).

**Resource.** There is NO elapsed-time assertion anywhere: the heavy arms are killed deterministically by the visit counter and the `RelMap.down` tripwire (about two million calls), and the memo type is checked on a 2,000-node chain; a 30 s test timeout is a last resort only. The heavy shapes are the 100,000-node chain, the 100,000-sink and 50,000-hub shapes, and the 8 MiB cap±1 fixtures.

## 4 · Interfaces that change — and which ones FREEZE

| Interface | Current | After | Consumers | **Frozen for the fork?** |
|---|---|---|---|---|
| `yamlscan.prescan(text: str) -> None`, `yamlscan.YamlLimitError(Exception)` with `.kind: "anchor"\|"depth"`, `.shown: str`, `.limit: int`, `yamlscan.ANCHOR_NAME_DISPLAY = 40` | none (`MapStore._prescan_sidecar`, `ANCHOR_NAME_DISPLAY` in `store.py`) | NEW leaf; `store` converts the error to `MapStoreError` with byte-identical text; `store` drops `MAX_DEPTH` and `ANCHOR_NAME_DISPLAY` | `store` (2 sites), `relmap.descriptor` | **FREEZE (D1)** |
| `relmap.descriptor.read_repo_text(path: Path, cap: int) -> str`; `RepoReadError(Exception)` with `.cause: str` (K1–K7) and `.limit: int` (the cap, to render K5); `DescriptorError(Exception)` with `.cause: str`, `.name: str`; `Descriptor` frozen value `(profile: str, canon: str, us_canon: str \| None, at_table: str \| None, ignored_keys: tuple[str, ...])`; `default_descriptor() -> Descriptor` (= `Descriptor("reqharness", "REQUIREMENTS.md", None, None, ())`, what `discover_descriptors` falls back to); `load_descriptor(path: Path, repo: Path) -> Descriptor`; `discover_descriptors(repo: Path) -> tuple[tuple[Path, ...], int]` (≤ 8 sorted paths, overflow count); **tested seam, not frozen:** `CAUSE: Mapping[str, str]` (a `types.MappingProxyType`, `"K1"`…`"K17"` → fixed text) | none | NEW | `relmap.adapter`, `relmap.audit` | **FREEZE (D2)** — the names before the seam |
| `relmap.adapter.CanonUnavailable(Exception)` with `.cause: str` (K1–K7) and `.limit: int`; `Derivation` frozen `(map: RelMap, reported: tuple[str, ...], unlinked: tuple[str, ...], unknown_status: int)`; `derive_reqharness_map(repo: Path, descriptor: Descriptor) -> Derivation` | none | NEW | `relmap.audit` | **FREEZE (D3)** |
| `relmap.profile`: `EdgeType(name, pairs, downstream, evidence)`, `GapRow(kind, severity, pattern, node_kind, edge, peer, eligible, open, needs, sentence)`, `Profile(name, node_kinds, edge_types, gaps)` (all frozen), `REQHARNESS` | none | NEW | `model`, `gaps`, `adapter` | **FREEZE (D3)** |
| `relmap.model`: `Node(id, kind, title="", status="active", open=False, unparsed=0)`, `Edge(src, dst, type, evidence_missing=False, in_cycle=False)`, `Problem(kind, subject)` (frozen); `RelMap` with `.profile`, `.nodes: tuple[Node, ...]` and `.edges: tuple[Edge, ...]` (input order), `.problems: tuple[Problem, ...]`, `.cycles: tuple[tuple[str, ...], ...]` (first member first in node input order), `.sourced: frozenset[str]`, `.visits: int` and methods `node(id) -> Node \| None`, `up(id) -> tuple[str, ...]`, `down(id) -> tuple[str, ...]` (ids in edge input order), `reach(id) -> int \| None` (`None` = "not computed", the shared visit budget is spent), `neighbourhood(id, hops) -> frozenset[str]` (NOT on the budget: O(V+E) per call, a view calls it for the focused node only); `VISIT_BUDGET = 2_000_000`; `build_map(profile, nodes, edges, *, sourced) -> RelMap`; `RelMapLimitError(Exception)`; `DISPLAY_MAX = 120`, `cut(text) -> str`. The D3 docstring states the budget (security C1) | none | NEW | `gaps`, `adapter`, `audit`; R2 (the API R2 consumes) | **FREEZE (D3)** |
| `relmap.gaps`: `Gap(severity, kind, node, sentence, reach)` frozen; `detect_gaps(map) -> list[Gap]`; `rank_gaps(map, gaps, limit: int \| None) -> tuple[list[Gap], int]` (ranked, `reach_not_computed`; `limit=None` ranks every band, bounded by the map's visit budget) | none | NEW | `audit`; R2 | **FREEZE (D3)** |
| `relmap.audit`: `structure_lines(repo: Path) -> list[str]` — the ONLY name frozen here: it returns repository-derived UNESCAPED lines (the sink must escape; `run_cli` does) with the informational header first; **tested internal seams, "stable within the batch, not frozen":** `format_structure(relmap, gaps, notes, refusals, *, label, sources=(None, None), unknown_status=0, reach_not_computed=0) -> list[str]` (performs the 120-character cut itself; when `refusals` is non-empty it returns exactly those lines) and `refusal_line(base_name, cause, limit=None) -> str` (defined in `relmap.descriptor` as built in Inc-3 and imported by `relmap.audit`, ledger .56) | none | NEW | `app` (passes `structure_lines`), tests | **FREEZE (D5)** — `structure_lines` only |
| `reqharness.audit.run_cli(argv: list[str], extra_lines: Callable[[Path], Iterable[str]] \| None = None) -> int` | `run_cli(argv)` | optional second parameter; `None` is byte-identical to today; fixed `unavailable` lines for no-repo / no-registry keyed on `report.chain_status` (`identity.NO_REPO`, `reqharness.audit.NO_REGISTRY`), never on verdict text; hook failure line `structure: unavailable (internal error: <Type>)`; at most 1,000 hook lines consumed; no hook call and no structure line when `audit()` raises (the `--baseline` refusal) | `app.py:352` (the only caller), tests via subprocess and in-process | **FREEZE (D4)** — trigger A3 fired; the consumer census is in §5.2 |

**A frozen interface is not touched inside a lane.** There is no lane (one chain); the freeze binds across increments instead: a later increment that needs to change a frozen name returns to the trunk with a ledger entry and a PDR version bump. **The frozen set is exactly:** D1 `yamlscan`; D2 `read_repo_text`, `load_descriptor`, `discover_descriptors`, `default_descriptor`, `Descriptor`, `RepoReadError`, `DescriptorError`; D3 `Profile`/`EdgeType`/`GapRow`/`REQHARNESS`, `Node`/`Edge`/`Problem`/`RelMap` (with `VISIT_BUDGET`), `build_map`, `RelMapLimitError`, `Gap`/`detect_gaps`/`rank_gaps`, `CanonUnavailable`/`Derivation`/`derive_reqharness_map`; D4 `run_cli`; D5 `structure_lines`. `format_structure`, `refusal_line` and `CAUSE` are tested internal seams, stable within the batch and not frozen (architect PD-3).

## 5 · Proposed test cases

### 5.1 Per deliverable file — RED counterfactual and mutants per LLR

*RED counterfactual for every new source file:* move the file aside (or, for `store.py`, apply the named reword) and run its tests: they must fail at import or assertion, then pass when restored. *Mutants:* named in the contract (LLR bodies and ledger); each row's mutant turns the listed test RED.

| New / edited file | Move-aside RED (what fails) | LLR → asserting test (layer) → mutant that turns it RED |
|---|---|---|
| `relmap/profile.py` | `test_relmap_profile` import error | RMP.1.1 → `test_edge_table`, `test_catalogue_table` (0) → M-RMP-3 (flip `verifies`), M-RMP-5 (severity cell); RMP.1.2 → `test_engine_names_no_kind` (A, set ≥ 17) → M-RMP-1 |
| `relmap/__init__.py` + isolation | `test_relmap_isolation` import census finds no package | RMP.2.1 → `test_relmap_isolation`, `test_arch_osopen_callers` (A) → M-RMP-2 (`model.py` imports `relmap`), M-RMP-6 (import without allow-list entry); RMM.1.1 `test_py310_floor` → M-RMM-7 (`import tomllib`), M-RMM-9 (flag bare `walk`); TC-RM-01 → M-RMP-4 |
| `relmap/model.py` | `test_relmap_model` import error | RMM.1.1 `test_multi_parent_and_order`, `test_value_defaults` → M-RMM-4; RMM.1.2 `test_problem_*` (incl. a U+2028-id arm) → M-RMM-1; RMM.1.3 `test_caps` → M-RMM-5; RMM.2.1 `test_direction_per_edge_type` → M-RMM-2; RMM.2.2 `test_reach_*`, `test_reach_chain_at_cap` (no `RecursionError`) → M-RMM-6, M-RMM-8; `test_reach_memo_is_counts` (2,000-node chain, int memo) → M-RMM-10; `test_reach_budget_per_row` (`down` tripwire, `visits ≤ 2,000,000`, a `None`) → M-RMM-11; RMM.3.1 `test_cycle_*` → M-RMM-3 |
| `relmap/gaps.py` | `test_relmap_gaps` import error | RMG.1.1 one arm per row, `test_gap_sentence_qualified` → M-RMG-2, M-RMG-4; RMG.1.2 `test_unsourced_kind_is_silent`, `test_withdrawn_only_llr_is_not_a_gap` → M-RMG-1, M-RMG-3, M-RMG-6 (the snapshot arm `test_snapshot_gaps` is Inc-4, in `test_relmap_adapter.py`); RMG.1.3 `test_ranking`, `test_rank_visit_cap` (visits ≤ 2,000,000, `reach_not_computed > 0`, `down` tripwire), `test_rank_100k_sinks`, `test_rank_limit_none` → M-RMG-2, M-RMG-5 |
| `tests/test_prescan_refusal_goldens.py` (before the move) | on the base `store.py` it is GREEN; reword one refusal (M-RML-6) → RED | RML.1.4 → the 8-string golden (A; constants generated by running the base code, capture command and base SHA in the packet, committed alone before the `store.py` edit) → M-RML-6 (RED while `test_ingestion_limits` stays GREEN), M-RML-12 (`ValueError` base) |
| `yamlscan.py` | `test_yamlscan` import error; `store` still defines the logic → census RED | RML.1.4 → `test_yamlscan`, `test_limit_error_is_not_valueerror` → M-RML-5 (alias check dropped) |
| `store.py` (delegation) | golden RED if text moves | same as above; `test_arch_osopen_callers` (store entry loses `MAX_DEPTH`) → M-RMP-6 |
| `relmap/descriptor.py` | `test_relmap_descriptor` import error | RML.1.1 → causes K1–K10 arms, `test_cause_is_read_only` → M-RML-1, M-RML-2, M-RML-10, M-RML-15, M-RML-17; RML.1.2 `test_schema_table` (incl. the default row) → M-RML-3, M-RML-11; RML.1.3 `test_paths_confined` → M-RML-4; RML.1.5 `test_read_repo_text_*` (link or Windows junction, directory, FIFO where possible, cap±1 with a bytes-read assertion, NUL, non-UTF-8, identity mismatch, `st_ino = 0`) → M-RML-7, M-RML-8, M-RML-14, M-RML-16; RML.1.6 `test_repo_root_census` → M-RML-13 (the derive-once arm `test_canon_derived_once` and M-RML-9 are Inc-5, `test_relmap_audit.py`) |
| `relmap/adapter.py` | `test_relmap_adapter` import error | RMA.1.1 `test_snapshot_census`, `test_live_invariants`, `test_status_words`, `test_canon_causes`, `test_snapshot_sha256` (LF-normalised pin) and `test_snapshot_sha256_crlf_arm` → M-RMA-2, M-RMA-6, M-RMA-7, M-RMA-9; RMA.1.2 `test_rule_d1_table` → M-RMA-1; RMA.1.3 `test_reported_rows_are_notes`, `test_unparsed_counts`, `test_report_line_shape_yields_id` → M-RMA-3, M-RMA-5, M-RMA-8; RMA.1.4 `test_readonly` → M-RMA-4; RMG.1.2 `test_snapshot_gaps` → M-RMG-3 |
| `relmap/audit.py` | `test_relmap_audit` import error | RMU.1.2 `test_line_formats`, `test_header_first`, `test_snapshot_run`, `test_sources_line_configured_string`, `test_format_structure_cuts_inside` (1 MiB values passed directly), `test_refusal_line_hostile_name` → M-RMU-3, M-RMU-5, M-RMU-7, M-RMU-9, M-RMU-11, M-RMU-13, M-RMU-14; RMU.1.3 `test_escaped_and_no_forged_verdict` (five arms + a Layer A arm), `test_exit_code_unchanged` → M-RMU-1, M-RMU-8; RMU.1.4 `test_byte_stable` (seeds 0 and 2), `test_canon_derived_once` → M-RMU-6, M-RML-9 |
| `reqharness/audit.py` + `app.py` | `test_relmap_audit` hook arms RED; `run_cli(argv)` callers still pass (compat limb) | RMU.1.1 TC-RM-02 (A, in-process), TC-RM-03 (A, the `--baseline` refusal path: no structure line, hook never called), `test_hook_line_bound` (A), AT-120/AT-126 (B) → M-RMU-2, M-RMU-4, M-RMU-10, M-RMU-12 |

**Acceptance tests (Layer B)** — AT-117…AT-122, AT-124…AT-129 per contract §5.3, each with its named mutant; they run `mapper --audit` as a subprocess with the 60 s timeout over tmp repos built through `tests/_relmap_fixtures.py`, which IMPORTS `_seed`, `_git_repo`, `_write_canon` and `_audit_cli` from `tests/test_reqharness_release.py` (the repo already imports across test modules, `tests/test_reqharness_release.py:31`); it is a helper module, never a copy, and a renamed source helper fails the import loudly. Layer B evidence first exists at Inc-5 (see §2.1 *Layer phasing*). Layer 0 (unit) applies to `build_map`, rank, the rule-D-1 parser, the K-classifier (cyclomatic ≥ 3 and module-boundary data).

### 5.2 Reverse census — by import AND by fixture content (executed 2026-10-25 on `HEAD` `9b4a8ff`)

By **import / symbol** (`git grep` over `mapper/` and `tests/`):

| Symbol touched | Hits | Consequence |
|---|---|---|
| `run_cli` | one caller, `mapper/app.py:352`; no test calls it in-process (all use a subprocess or `reqharness.audit.render`) | the optional parameter is source-compatible; TC-RM-02 is the first in-process caller |
| `MapStore._prescan_sidecar` | defined `store.py:712`, called `:769` (`_capped_side_graph`) and `:820` (`load`); tests mention it only in docstrings (`test_ingestion_limits.py:129`, `test_repair_sidecar.py:30,286`) | delegation is invisible to them; golden pins the text |
| `_capped_side_graph` / `git_diff` | `store.py`, `diff.py`, `screens/map/painting.py`; tests `test_diff.py`, `test_inc9h.py`, `test_ingestion_limits.py` (diff-side arms assert `None` only) | the golden calls `_capped_side_graph` directly; those arms stay green |
| `MAX_DEPTH` | defined `osopen.py:91`; imported only by `store.py:17`; pinned in `tests/test_arch_osopen_callers.py:103` | moves to `yamlscan.py`; the allow-list changes in Inc-3 |
| `ANCHOR_NAME_DISPLAY` | `store.py:50,734-735` only; no test references it | moves to `yamlscan.py` |
| `reqharness_audit` / `.render(` | `tests/test_a3_census.py:329` pins `== 86` ARG-FUL `.render(` attribute calls; `test_tc_a3_no_source_file_is_invisible_to_the_census` needs staged files | relmap adds no `.render(` call; stage new files first |
| `relmap`, `yamlscan` | no tracked path or import on the tree | new input class |

By **fixture content** (tests whose fixtures the new code will read):

| Fixture class | Tests | Consequence |
|---|---|---|
| tmp repos with a `REQUIREMENTS.md` run through `mapper --audit` | `tests/test_reqharness_release.py` (13 sites: 12 `_audit_cli("--audit", …)` at `:318, 400, 429, 464, 544, 562, 574, 585, 667, 689, 758, 781` and 1 direct subprocess at `:513`, cwd inside a subdirectory), `tests/test_reqharness_baseline.py:182,244,264` — **16 sites in all: 10 print the block** (`:318, 400, 429, 513, 562, 574, 667, 689, 758`, baseline `:182`) **and 6 are refused before a report exists, so the hook never runs** (`:464, 544, 585, 781`, baseline `:244, 264`) | the 10 now ALSO print a structure block from a one-or-few-row canon. Assertions are `in proc.stdout` / `startswith("verdict: ")` / stderr lists (`:587`, `:792`); none counts stdout lines or takes `[-1]`. Safe; AT-120 adds the base-captured prefix golden. `:562` and `:574` gain one extra `structure: unavailable (canon: …)` line beside the old `canon unreadable` line (both kept) |
| the hostile-canon arms of the same suite | `tests/test_reqharness_release.py:665-680` (no raw `\x1b`, `\x7f`, `\r`, C1 over the WHOLE stdout; exactly one `verdict:` line) and `:755-770` (no raw U+2028, U+202E, U+200B) | free regression arms for the new block: they pass only if every printed value is escaped and cut. Named in the Inc-5 exit check; a failure there is a defect in the block, not a stale test. The happy fixtures also assert the ABSENCE of a `structure: unavailable (internal error` line |
| the live `REQUIREMENTS.md` read by other suites | `test_requirements_canon.py`, `test_review_screen.py`, `test_reqharness_registry.py`, `test_reqharness_signing.py` | read only; relmap only reads it |
| a root-level `*.relmap.yml` | none tracked (`git grep '\.relmap\.yml'` outside `.dev-flow` is empty) | the discovery input class is new; re-run at Inc-3 |
| sidecar fixtures with anchors/aliases/depth | `test_ingestion_limits.py`, `test_repair_sidecar.py:286` (hygiene prescan) | green through the delegation; golden is the byte limb |

Census is best-effort; the increment gates confirm completeness. Reservation: a screen-level test that loads maps with `git_diff` over a real repo goes through `_capped_side_graph` (`test_inc9h.py`).

### 5.3 Reading notes for the `--audit` block, and the PDR conditions' homes

*UX (documented in the Inc-5 packet and the ARCHITECTURE `relmap` row; none is a code requirement beyond LLR-RMU.1.2).* (1) The first block line, `structure: informational - does not change the verdict or the exit code`, says on screen that the block never gates. (2) The `verdict: ` line is found by its prefix and is **no longer the last line** of the output: a CI step that reads the last line must switch to `grep '^verdict: '`; moving the block before the verdict was rejected for byte-compatibility and is not reopened. (3) **Width is not guaranteed** (the existing `identity:` line already wraps at 80 columns): a gap row starts with about 60 fixed characters, so the first 40 characters carry severity, kind and node. (4) **Gap rows are for reading, not parsing**: a title may contain ` · `; the stable parse keys are the line prefixes. (5) **Worst case** about 298 lines (8 blocks × 37 lines + the header + the descriptor overflow line), each at most 1,000 characters; the normal case is one block. (6) `reach=<r>` is the number of distinct nodes downstream of the node, 0 when not computed.

*Where each PDR condition is discharged* is tabulated in the PDR record §A (condition table); the design-level ones land in this proposal and in the contract now, the test-level ones at the named increment gate.

## 6 · Risks and rejected alternatives

**Top risks.**

| # | Risk | Mitigation / owner |
|---|---|---|
| 1 | The prescan move (`store.py`) changes a refusal string | golden of 8 strings captured on the base first; M-RML-6 proves it sees what the old suite cannot; stop and re-plan if one string moves (PLAN risk) |
| 2 | A canon quirk breaks an oracle (`_ROW_ID_RE` accepts U+200B/U+202E but rejects NBSP; silent skips) | AT-124 uses the verified characters; "parsed rows" defined as `parse_canon` objects; tripwire on the `cannot parse row for` text |
| 3 | The A3 `.render(` pin or the osopen allow-list drifts | per-increment exit checks; allow-list entries in the same increment as the import; new files staged before census runs |
| 4 | Windows cannot create the symlink for the K1 arm | the K1 arm uses a directory junction (`mklink /J`, no privilege needed; a reparse point `osopen.is_link` is meant to catch); `blocked` is reported only if even the junction cannot be created, and a junction that `is_link` misses is itself a finding; the same code path is covered by the monkeypatched identity-mismatch arm; operator-run on a privileged shell is a Phase 4 item |
| 5 | Heavy arms (8 MiB cap±1, 100,000-node chain, hub shape, two-seed subprocess runs) make the targeted run slow or flaky | NO elapsed-time assertion: ceiling mutants are killed by the deterministic visit counter and the `RelMap.down` tripwire, the memo type by a 2,000-node chain (QA D-1); heavy arms in their own functions so a failure names the shape; each packet records measured wall time, budget about one minute for `test_relmap_audit.py` |
| 6 | The real Python 3.10 run is `not-run` (no interpreter, no CI) | AST floor + qualified-name census; operator-run check in Phase 4 |
| 7 | Contract size (92,888 characters vs 54,000 budget, V26 NOTICE) | accepted: the excess is truth tables and AT bodies the reviewers asked for; narration stays in the ledger |
| 8 | Reach is flat on the skeleton (all 7 live gaps tie at 0) | OQ-R1-8: not in R1; carried to R2 |

**Rejected alternatives — only where a real decision exists.**

| Alternative considered | Why it was rejected |
|---|---|
| Put `read_repo_text` in `osopen` (it is file-boundary safety) | It would reopen a hygiene-batch module whose names were frozen at that batch's PDR, and `read_repo_text` has one consumer (`relmap`); the allow-list and ARCHITECTURE osopen cells already assume `relmap/descriptor.py` is the importer. (A fourth source file in Inc-3 would still be within the cap of 4: size is not the reason.) Revisit if a second package needs it |
| Pass the `Report` (not `Path(report.repo)`) to the hook | Couples `relmap` to `reqharness`'s `Report` type; the contract's callable takes the repository root and `reqharness` stays upstream |
| Store the 8 golden strings under `tests/goldens/**` | The repo convention is module-level constants beside the assertion (`tests/test_repair_golden_census.py:5-7` pins byte identity that way) and `tests/goldens/` is probed to hold only `perf`; eight short strings are clearer next to the test. (That the directory is `-text` is a reason FOR byte-pinning, not against it.) |
| One `format_structure` per whole run | A refused descriptor yields a refusal line and no block, so the unit is one descriptor; `structure_lines` assembles blocks in name order and appends the overflow line |
| Reuse `reqharness.config.load_documents` for the prescan | Already rejected in R-017 (d) — echoes `{exc}`, adds `relmap` → `reqharness.config`, and `reqharness` may import only `osopen`; fold-in is B-144 |
| `n/a` — frozen dataclass vs `NamedTuple` for `Node`/`Edge` | Not a real decision: the repo's value types are frozen dataclasses; the contract already says "frozen value" |

## 7 · Forward-applicability table — **the section that makes this document honest**

| Output of this PDR | Named consumer downstream | Where the consumer will read it |
|---|---|---|
| design characteristics (§2 boundaries, §3 algorithms, the frozen signatures D1–D5) | the Phase-3 increments 1–5, read at each increment gate | increment packets + this proposal §2.1, §4 |
| enablers: the snapshot fixture (Inc-4, LF-normalised pin), the shared AT fixture helper `tests/_relmap_fixtures.py` (Inc-5, imports the release-test helpers), the base-captured golden (Inc-3, generated by running the base, committed alone) | Phase 3 and validation (AT-117…AT-129) | `tests/fixtures/relmap/`, `tests/_relmap_fixtures.py`, `tests/test_prescan_refusal_goldens.py`, `03-increments/` packets |
| proposed test cases and mutants (§5.1) | layers 0/A/B, the RED-battery per increment, and the DDR | each increment packet's RED section + DDR checklist rows 4–5 |
| design → requirement traceability (§1 chain map, §5.1 LLR rows) | the traceability matrix and the DDR | batch `06-docs/traceability-matrix.md` + `PDR-2026-10-25-relmap-r1-batch.md` §A row 4 |
| reverse census (§5.2) | each increment's exit check and the DDR re-check | the PDR record §A row 7 + DDR row 3 |
| frozen-interface list (§4) | `docs/ARCHITECTURE.md` (after the seal) and the R2 batch | the §2 `relmap`/`yamlscan` rows; R2's PDR |

- ⚠ Any row whose consumer column is empty: none.

## 8 · Parallelisation plan *(only if the batch forks)*

Not applicable — trigger A4 did not fire; the five increments are one dependency chain over one package (`modules(A) ∩ modules(B) ≠ ∅` for every adjacent pair, ARCHITECTURE §6), one owner, no lane. File sets are listed per increment in §2.1 and are disjoint by construction (no file appears in two increments).
