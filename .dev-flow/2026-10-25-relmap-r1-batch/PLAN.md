# PLAN — mapper — Batch 2026-10-25-relmap-r1-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language.
> **Owed in.** `core` ✓ · `full` ✓
> Seeded by `/dev-flow-init` step 4 at both levels; the living plan is owed at every gate
> that follows (`/dev-flow` §Living plan is the rule's home).

> **Field guide:** `templates/guides/plan-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.
> **Two header labels are read literally and are never translated:** `Standing authorization` and `Last updated`; the field guide names their readers.

The living compendium of this batch: where-we-are · objective · per-story/per-station status ·
roadmap + increment plan · key decisions · risks/watch-items · conventions honored ·
out-of-scope carries · test ledger · decision log (the human-readable mirror of `state.json`).

## Header

| Field | Value |
|---|---|
| Project | mapper |
| Batch | 2026-10-25-relmap-r1-batch |
| Objective | Relation-map port R1 (QuickMap handoff C1/C2/C9; MAP-TYPES approved 2026-10-23; strategy S1), HEADLESS: a relation-map KIND beside the tree `Graph`, never a mutation of it. `mapper/relmap/` with (a) the per-profile kinds/edge-types table for the `reqharness` profile (US, HLR, LLR, AT, TC; `refines`/`covers`/`verifies`/`binds`; direction of change; graduated AT→test ● bound · ◐ tagged · ○ none), (b) the typed multi-parent read model (up/down, reach, neighbourhood, cycles reported), (c) the approved gap catalogue ranked by severity then reach, (d) a read-only adapter deriving the map from mapper's own canon — the HLR/LLR skeleton first, because the US canon and the AT→test table do not exist yet, (e) structural-gap lines in `mapper --audit`. The C9 limits shipped in the hygiene batch are reused for any YAML a relation map reads. No screen, no view (views are R2). |
| Last updated | P5 · 2026-10-25 (post-mortem `05-postmortem.md`, `06-docs/executive-summary.md`, `06-docs/functionality.md` and the final traceability sign-off written; BACKLOG B-156…B-158 added); previously: P3 follow-ups 2026-10-25 (fix unit: coerced code points, model.py citation, LED .69-.71); previously: P2 third pass and PDR reviews 2026-10-25 (author unit): QA third pass `iterate` (X-1 major, N-3 minor, N-7 nit) dispositioned by `LED-…29`-`.31`; PDR reviews architect/QA/security/UX all `approved with conditions`, conditions applied by `LED-…32`-`.43` (proposal and contract amended, PDR record filled, sealed `approved with conditions`); per-increment SOURCE counts re-checked: 3, 1, 3, 1, 3 (≤ 4); the orchestrator records the P2 and PDR decisions, station not moved by the author. Before that: P2 2026-10-25 first pass — architect, qa-reviewer and security-reviewer all `iterate-to-refine` (1 blocker, 22 majors, 16 minors across the three); the P1 contract amended by 16 ledger entries (orchestrator rulings R1–R16), increment plan re-checked (still ≤ 4 source files each); second P2 pass owed. Before that: P1 2026-10-25 — P0 intake (4 stories READY), triggers evaluated (fired A1 A2 A3 B1 C6 D1 E1 F2; ARQ/PDR/DDR stand), ARQ written into `docs/ARCHITECTURE.md` as commitments (`relmap`, `yamlscan`, R-016, R-017, §6 worksheet), P1 contract drafted (4 US / 9 HLR / 24 LLR / AT-117…AT-123, 14-row premise table all TRUE, IFC Part A ×3), BACKLOG refreshed (F2) with B-140…B-143, gate run; stops at the P1 gate; records only, nothing pushed |
| Standing authorization | standing authorization — the operator's approval of the relation-map series, quoted by the orchestrator: «Arranca las tres, delega todo lo que puedas a kimi» (2026-10-23) and «continue» (2026-10-25). Runtime cannot prompt: autonomy over the gates the commission opens is read from silence (shared-batch.md §Batch-kickoff authorization); MERGE NOT granted — the default stands. |
| First gate | run before Phase 0 on 2026-10-25 against the outgoing closed batch: V7 reported the bundle identical to the manifest, both directions, at `2026-10-12-rev102` (57 files, `flow_hash` not recomputable from a subset); the remaining NOTICEs are the closed hygiene batch's own (V23/V26/V41/V53/V56/V57) and stand as that batch's record. After the rollover and P1 the run printed 0 BLOCK (see Gate notices). |
| Premises / RC-1 | `git fetch origin` 2026-10-25: `origin/master` = `HEAD` = merge-base = `194f885c3443` (the default branch is `master`; there is no `origin/main`) — base current. RC-2: `git ls-remote --exit-code --heads origin` answered; newest commit 2026-10-24 (`194f885`, 1 day). Already-shipped check (RC-1 b): the four outcomes grepped on `origin/master` — `git ls-files` finds no `mapper/relmap`, no `mapper/yamlscan.py`, no `*.relmap.yml`; no `structure` lines in `mapper/reqharness/audit.py` → none shipped. Outgoing batch (`2026-10-23-hygiene-batch`): closed P6, vault-synced 2026-10-24 (`194f885`), decisions archived (17 entries) to `.dev-flow/2026-10-23-hygiene-batch/decisions-log.json`. The 14 premises of the contract (§2.7) are all TRUE with executed evidence under `evidence/`. |

## Triggers

The trigger evaluation `state.json`'s `triggers.record` points at: one row per trigger evaluated, fired or not.

| Id | Verdict | Probe output |
|---|---|---|
| A1 | fired | judged — creates module `relmap` (`mapper/relmap/`) and leaf `yamlscan`; `docs/ARCHITECTURE.md` §2 had no row for either (now committed) |
| A2 | fired | judged — touches `relmap`, `yamlscan`, `store`, `reqharness` (audit), `app` — five modules |
| A3 | fired | judged — `reqharness.audit.run_cli(argv)` gains an optional callable; consumer `mapper/app.py:352`; pins `tests/test_a3_census.py:300-312`; the `store` prescan delegation is interface-neutral by requirement (byte-identical messages) |
| A4 | not fired | judged — the five increments are a dependency chain over one package (§6 of the module map explains the intersection); one owner, no lane |
| B1 | fired | `git grep -l "run_cli\|_prescan_sidecar\|reqharness_audit\|audit\.render" -- tests` → `test_a3_census.py`, `test_ingestion_limits.py`, `test_repair_sidecar.py`, `test_reqharness_release.py` — assert symbols this batch touches, owned by other batches → reverse census per increment |
| B2 | not fired | judged — no file changes location; `_prescan_sidecar`'s body moves between files, not a file |
| B3 | not fired | `git grep -il audit -- tests/goldens` → no hit (only `tests/goldens/perf`, which holds renders) — no byte-identical golden captures the audit text |
| B4 | not fired | judged — nothing this batch writes is consumed by another component (stdout lines are read by humans and tests; the descriptor is read, never written; the R2 consumer of the API does not exist yet and is declared when R2 opens) |
| C1 | not fired | judged — no authentication surface |
| C2 | not fired | judged — no secrets handling; the descriptor holds repo-relative paths and a profile id |
| C3 | not fired | judged — no external integration |
| C4 | not fired | judged — no sensitive-data category |
| C5 | not fired | judged — no destructive operation |
| C6 | fired | judged — operator-supplied bytes are parsed: the `*.relmap.yml` descriptor (new input class) and the canon, both repository files; the scan output is in §Gate notices |
| C7 | not fired | judged — no network exposure |
| C8 | not fired | judged — headless: no render mode flips to markup interpretation; repository-derived text reaches the terminal only through the audit's escaper (LLR-RMU.1.3) |
| D1 | fired | judged — `mapper --audit` output is user-visible text and gains a block; no layout, no colour, no screen. Raises (never relaxes): `ux-reviewer` is owed at PDR |
| D2 | not fired | judged — no prototype in this batch (R2 owns the views and already has its prototype verdict) |
| E1 | fired | 4 stories (US-RM-001…004) / 5 planned increments |
| E2 | not fired | judged — HANDOFF scores C1 "risk high" for the whole port; R1 is the headless slice with the tree kind untouched by construction (R-016) and `store.py` change bounded by byte-identity |
| E3 | not fired | judged — internal tool; no client or regulated context |
| F1 | not fired | from a bundle — probe is the gate's `V7` line: bundle identical to the manifest, both directions, at 2026-10-12-rev102; `flow_hash` not recomputable from a subset |
| F2 | fired | `BACKLOG.md` header read `Last refresh 2026-10-09` against the last close 2026-10-24 → stale. Discharged at this rollover: header refreshed to 2026-10-25 / `194f885`, B-140…B-143 added |

## Where we are

P0, ARQ, P1, P2, PDR, P3, DDR and P4 are closed (2026-10-25). Validation PASS-WITH-NOTES: 35/35 requirements,
12/12 ATs as `mapper --audit` subprocess nodes, full suite 4017 passed / 0 failed at `934e935`; DDR sealed
approved with conditions; the real Python 3.10 run is `not-run` (B-148). P5 (post-mortem) and P6 (executive
summary, functionality, traceability sign-off) are written. **Owed next:** the operator's P6 gate, merge of
`feat/relmap-r1` (merge authority was not granted; no PR is opened by the P5/P6 unit), the backlog header
refresh and PR/merge marks at merge, then `/dev-flow-sync` to the vault.

## Objective

See the header. Success is observable through one surface: `mapper --audit <repo>` prints, after the existing
report and without moving a line of it or the exit code, the structure block of LLR-RMU.1.2 — for this repo
`nodes=275 (HLR=76, LLR=199) edges=196 (refines=196) cycles=0` and `gaps: 7 (HIGH=0, MED=7, LOW=0)` — and the
`mapper.relmap` API answers up/down/reach/neighbourhood/gaps for the R2 views.

## Per-story / per-station status

| Story / station | Status | Notes |
|---|---|---|
| P0 | approved under the standing authorization | US-RM-001…004 READY |
| ARQ | approved under the standing authorization | commitments in `docs/ARCHITECTURE.md`; no lane |
| P1 | approved; amended after the first P2 pass (16 ledger entries) | contract + empty ledger + premise/IFC/scan records |
| US-RM-001 traceability graph | P1 | Inc-1, Inc-4 · AT-117, AT-119 |
| US-RM-002 ranked gaps | P1 | Inc-2 · AT-118; 7 of 8 kinds Layer A (OQ-R1-2) |
| US-RM-003 audit lines | P1 | Inc-5 · AT-117, AT-120, AT-122 |
| US-RM-004 bounded descriptor | P1 | Inc-3 · AT-121 |
| P2 | first pass done: iterate-to-refine; contract amended; second pass owed | `02-review.md`, `evidence/p2-*.md` |
| PDR · P3 · DDR · P4 · P5 · P6 | not started | PDR/DDR stand (A1 fired) |

## Roadmap + increment plan

Five sequential increments (no lane), each ≤ 4 SOURCE files, tests uncapped. Each carries a move-aside RED
counterfactual per new source file and a named mutation per new assertion (C11 habits); each runs the targeted
tests plus the guard set (which now includes `tests/test_fold.py` and `tests/test_repair_artifact_claims.py`, see "P3 follow-up"), after probing `mapper.__file__` inside the worktree.

| Inc | Story | Source files | What | Owning requirements | Tests (provisional) |
|---|---|---|---|---|---|
| 1 | US-RM-001 | `mapper/relmap/__init__.py` (empty — re-exports nothing), `profile.py`, `model.py` (3) | `Profile` + the `reqharness` table INCLUDING the gap catalogue as data (R2); `Node`/`Edge` value shapes; `build_map` (problems, caps, multi-parent), up/down, iterative reach/neighbourhood, iterative cycles; AST floor + banned-stdlib-name census + isolation census; §2 row paths written; osopen allow-list entry `relmap/model.py` and both ARCHITECTURE osopen cells amended in THIS increment (R16) | HLR-RMP.1/.2, RMM.1/.2/.3 · LLR-RMP.*, RMM.* | `test_relmap_profile.py`, `test_relmap_model.py`, `test_relmap_isolation.py` (incl. TC-RM-01) |
| 2 | US-RM-002 | `mapper/relmap/gaps.py` (1) | generic detectors over the profile catalogue (no kind/edge literal), activation by sourced kinds, eligibility, qualified sentences (R3), ranking with memoised iterative reach and the 2,000,000-visit bound (R8) | HLR-RMG.1 · LLR-RMG.1.1–3 | `test_relmap_gaps.py` (no snapshot test: `test_snapshot_gaps` is Inc-4) |
| 3 | US-RM-004 | `mapper/yamlscan.py`, `mapper/store.py`, `mapper/relmap/descriptor.py` (3) | FIRST the byte-identity golden on the base `store.py` (R1: 8 strings, RED when one is reworded), THEN extract the prescan (store delegates, `YamlLimitError(Exception)`, `store` drops `MAX_DEPTH`); `read_repo_text` (lstat + capped reader, K1–K7), descriptor reader, closed causes K1–K17, schema table, path confinement, discovery cap 8; allow-list entries `yamlscan.py` and `relmap/descriptor.py` and the `store.py` change in THIS increment (R16) | HLR-RML.1 · LLR-RML.1.1–6 | `test_prescan_refusal_goldens.py`, `test_yamlscan.py`, `test_relmap_descriptor.py`, `test_relmap_isolation.py::test_stdlib_bans` (LED .46); `test_ingestion_limits.py` unchanged |
| 4 | US-RM-001 | `mapper/relmap/adapter.py` (1) | canon through `read_repo_text` + `parse_canon` → nodes, rule D-1 edges, reported rows and unlinked LLRs as notes, `Node.unparsed`, status words, staged sources, read-only; snapshot fixture `tests/fixtures/relmap/REQUIREMENTS.snapshot.md` + live invariants (R4) | HLR-RMA.1 · LLR-RMA.1.1–4 | `test_relmap_adapter.py` (incl. `test_snapshot_gaps`, LF-normalised `test_snapshot_sha256`) |
| 5 | US-RM-003 | `mapper/relmap/audit.py`, `mapper/reqharness/audit.py`, `mapper/app.py` (3) | `format_structure` + `structure_lines` (120-character cut, count line, determinism, one derivation), the injected hook with the fixed no-repo / no-registry lines, escaping, exit code; B1 census of `run_cli` tests; A3 pin `test_a3_census.py:329` unmoved | HLR-RMU.1 · LLR-RMU.1.1–4 | `test_relmap_audit.py` (incl. TC-RM-02, TC-RM-03, `test_canon_derived_once`), `tests/_relmap_fixtures.py` (imports the release-test helpers), AT-117…AT-129 per §5.3; `test_reqharness_release.py`, `test_a3_census.py` re-counted |

## Open backlog, ordered (visible in every plan)

71 items are open in `.dev-flow/BACKLOG.md` (90 rows, 19 struck). The ones this batch touches or sits beside,
in the order they matter here: **B-140** relation-map series R2–R5 (R2 views is next after this batch — it needs
the `mapper.relmap` API frozen here) · **B-141** US canon and AT→test table ("B-next-2") — until they exist 7 of 8
gap kinds have no end-to-end AT · **B-142** canon hygiene (7 unparsed rows, 3 unlinked LLRs) · **B-143**
MAP-TYPES `binds` prose · **B-124** committer-vs-reviewer email WARN in `--audit` (same output surface; no
overlap in code) · **B-132** module map `store`→`mermaid` edge (the `store` row is amended here; fold the fix if
the same cell is edited) · **B-137/B-139** known flakes: a red in `test_reqharness_cache_fastpath.py` or the AT-113/AT-114 arms is not automatically a regression (P-05) · **B-138** `OutlineRenderer`
dangling-edge crash (unrelated). All other open rows (B-01…B-97, B-102, B-106…B-136) are unrelated to R1 and stay
where they are. Nothing is closed by this batch.

## Key decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-25 | Separate kind in its own package; reqharness data derived from the canon (R-016) | S1; keeps ~every tree invariant; MAP-TYPES §5 recommendation accepted |
| 2026-10-25 | Extract `MapStore._prescan_sidecar` to leaf `yamlscan` (R-017), `store` delegates byte-identically | the descriptor must read under the SAME refusal; copying forks a security rule, importing `store` breaks the headless ban |
| 2026-10-25 | Rule D-1: HLR→LLR by id structure, unlinked listed and never guessed | the canon has no parent column (premise 1); 196/199 resolve |
| 2026-10-25 | Implement the NORMATIVE direction rule (`binds` upstream), flag the MAP-TYPES prose | premise 6: only the rule answers the lens question "which TCs and ATs need re-review" |
| 2026-10-25 | `--audit` appends after the verdict through an injected callable; exit code untouched | no existing line moves; `reqharness` stays upstream of `relmap` |
| 2026-10-25 | Honest partial map: unsourced kinds produce no nodes and no gaps | MAP-TYPES §6.1 — no noise from missing canon |
| 2026-10-25 | Canon rows are NOT edited in R1 | editing a row flips its object to `changed · review`; the repair is B-142, deliberate and reviewed |

## Open questions (each with a recommended answer; none blocks P1)

| # | Question | Recommended |
|---|---|---|
| OQ-R1-1 | Where does `--audit` find a descriptor? | `<repo>/*.relmap.yml` at the root, sorted, each its own block; none → the default descriptor (as drafted in LLR-RML.1.2) |
| OQ-R1-2 | Accept Layer-A-only evidence in R1 for the direction queries, cycles and 7 of 8 gap kinds, with their end-to-end AT carried to R2's views / B-141? | Yes — no R1 surface can source them; declared in §2.6 and the HLRs, not hidden |
| OQ-R1-3 | Add a catalogue kind `LLR WITHOUT HLR` (MED) so unlinked LLRs are gaps, not notes? | Not in R1 (the catalogue was approved as written, OQ8); raise it as an amendment with R2 once B-142 clears the artefacts |
| OQ-R1-4 | Correct MAP-TYPES §3.2's `binds` prose to match the rule? | Yes, in the QuickMap repo (B-143); R1 follows the rule meanwhile |
| OQ-R1-5 | Should structural gaps ever change the audit exit code? | Not in R1 (informational); revisit as a ratchet (HIGH only) after B-142 |
| OQ-R1-6 | Extract the prescan to a leaf (R-017) or copy it? | Extract; the cost is `store.py` in Inc-3, bounded by byte-identity and the unchanged `test_ingestion_limits.py` |
| OQ-R1-7 | Gap eligibility = status `active` only (`deferred`, `superseded`, `withdrawn`, `split` excluded but traversed)? | Yes |
| OQ-R1-8 | Gap `reach` is QuickMap's down-reach, which is flat (all 7 live gaps tie at 0). Define a sink-aware reach? | Not in R1; revisit when TC/AT/US give the graph depth (R2) |

## Risks / watch-items

- `store.py` is the hygiene batch's highest-census file → Inc-3 is byte-identity-gated; if one refusal string moves, stop and re-plan.
- A new input class (`*.relmap.yml`) → the fixture-content census (LLR-RML.1.2) is re-run at Inc-3 by content, not by name — the hygiene batch's B1 miss.
- Module-map oracle tests (`test_repair_map_truth`, `test_mod_*`, `test_arch_osopen_callers`) are tree-checked: each increment writes its paths into the §2 `relmap` row in the same landing, and the osopen allow-list gains `yamlscan` and `relmap/*` with the owning increment.
- The editable install may import another checkout: every targeted run probes `mapper.__file__` (premise 12).
- No 3.10 interpreter here and no CI: the real 3.10 run is `not-run`; the AST floor guard plus a banned-stdlib-name census proxies; an operator-run 3.10 check goes to Phase 4.

## Conventions honored

English strings; no operator name, account name, email, handle or home path in any file (`<owner>`, `<home>`, `username_subject`); ids grouped by module; ledger append-only and empty; commits local on `feat/relmap-r1`, never pushed; targeted tests only under `env -u NO_COLOR -u TERM`.

## Out-of-scope carries

Views (R2) · evidence search (R3) · timeline (R4) · lineage + metro + `_map.yml` (R5) · typed-edge editing · the US canon / AT table / TC nodes (B-141) · canon repair (B-142) — all tracked in `.dev-flow/BACKLOG.md`, one home each.

## Gate notices and runtime absences

- `V7` bundle identity holds; `flow_hash` not recomputable from a subset (F1 not fired). `V15`/`V17`: running from the mirror — pairing and the hook executor are not checked on this runtime (SKILL.md gate step 5); NOTICEs stand.
- `V2` NOTICE: AT-117…AT-123 declared with no node on disk yet while `current_station` is before P3 — station-expected (V-5), a BLOCK only from P3 on.
- The closed hygiene batch's NOTICEs (V23, V26, V41, V53, V56, V57) belong to its sealed record and stand.
- **P1 gate run (2026-10-25):** `PYTHONIOENCODING=utf-8 python devflow-validate.py --brief .` → exit 0, **0 BLOCK**, 694 NOTICE. This batch's own NOTICEs, all expected: `V22` (14 LLRs never an IFC owner — a constraint may not transform), `V26` (contract 56,205 characters against the 54,000 budget — the excess is the LLR truth tables, requirement content and not narration; the closed hygiene contract ran 58,377), `V40` (owner omitted by design under A-110), `V47`–`V49` (04-validation.md is a Phase-4 artefact, still the template), `V52` (PDR active, proposal staged after P2 by design), `V53` (planned test nodes cited before they exist — the contract SPECIFIES them).
- Security scan (family C, C6 fired): `devflow-scan-spec.py` over `01-requirements.md` — result recorded in the P1 gate decision below.
- Mechanisms unavailable on this runtime: none beyond the above; no rule recorded `not-run`.

## P3 follow-up: what the targeted runs missed (full-suite run, 2026-10-25)

The orchestrator's clean full-suite run gave 4013 passed and 3 failed, all three introduced by this batch:

| # | Failure | Cause | Fix | State |
|---|---|---|---|---|
| 1 | `test_fold.py::test_no_tracked_file_spells_a_coerced_code_point_INCLUDING_the_artifacts` | live U+200B, U+2028, U+202E in `tests/test_relmap_model.py`, this batch's ledger, `02-review.md`, `evidence/p2-qa-pass3-and-pdr-qa.md` | escape spelling (`\u200b`); no hash re-pin (none of the three records is cited by hash) | green; LED .69 |
| 2a | `test_repair_artifact_claims.py::test_every_path_line_citation_resolves[search.py]` | bare `model.py:149` ambiguous once `mapper/relmap/model.py` exists | comment now `mapper/model.py:149` | green; LED .70 |
| 2b | same test, `[04-gate-findings-disposition.md]` | sealed record cites bare `model.py:82-83`; `_resolve` returns `None` on more than one hit; the test has NO exception table | `_CITATION_EXCEPTIONS` row in the test, resolver untouched; sealed record not edited | declared exception, option B (operator ruling); green; LED .71 |

Options for 2b (operator chose B): (A) teach `_resolve` that a bare basename with several hits resolves to the unique hit outside `mapper/relmap/` (one-line change, narrow, but a semantic change to a guard); (B) add a declared-exceptions table to the test (`{(artifact, cited): path}`) with a stated reason, and list this one; (C) edit the sealed record to `mapper/model.py:82-83` (a rewrite of a sealed record, against the rule). Recommended: B, because it is explicit and leaves the resolver's rule untouched.

Lesson: both were missed because the increments ran targeted tests only. The census for "a new file whose basename already exists elsewhere" and for "a literal coerced code point in any tracked file or batch record" belongs in every increment's guard list, so the guard set the plan names is extended by `tests/test_fold.py` and `tests/test_repair_artifact_claims.py` (and stays so for Phase 4 and any further increment).


## Test ledger

| Suite / command | Last run | Result |
|---|---|---|
| `env -u NO_COLOR -u TERM python -m pytest -q -p no:cacheprovider tests/test_mod_census.py tests/test_mod_deps.py tests/test_mod_structure.py tests/test_repair_map_truth.py tests/test_a3_census.py tests/test_arch_osopen_callers.py` (worktree on `PYTHONPATH`) | 2026-10-25 | 90 passed — after the ARCHITECTURE.md amendment (first draft: 9 failed, fixed) |
| QuickMap oracle: `tests/test_model.py tests/test_gaps.py` (read-only, 3.12.7) | 2026-10-25 | 123 passed |
| `tests/test_no_operator_paths.py` | see commit record | must pass before the commit |

## Decision log

Mirror of `state.json` `decisions_log` (machine-readable half); the outgoing batch's 17 entries are archived at `.dev-flow/2026-10-23-hygiene-batch/decisions-log.json`.

| Station | Date | Decision |
|---|---|---|
| P0 | 2026-10-25 | approved under the standing authorization — see `state.json` |
| ARQ | 2026-10-25 | approved under the standing authorization — see `state.json` |
| P2 | 2026-10-25 | first pass: three independent reviews all iterate-to-refine; P1 contract amended under orchestrator rulings R1-R16 (ledger .1-.16); `--iterate-to P1` recorded; second P2 pass owed — see `state.json` |
