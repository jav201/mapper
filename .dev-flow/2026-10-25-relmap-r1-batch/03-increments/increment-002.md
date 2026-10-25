# Increment 002 — US-RM-002 · `Generic gap detection and ranking over the profile catalogue`

> **Artifact language.** English (the batch language). **Owed in.** `core` ✓ · `full` ✓
> Where this lives: the repo, `.dev-flow/2026-10-25-relmap-r1-batch/03-increments/increment-002.md`. Written by the
> `software-dev` author in the batch worktree on branch `feat/relmap-r1` (base `75cf7f4`, Inc-1); the transcripts it cites
> are under `.dev-flow/2026-10-25-relmap-r1-batch/evidence/`, redacted of the account name (`<user>`) before hashing.

| Field | Value |
|---|---|
| Batch | `2026-10-25-relmap-r1-batch` |
| Increment | `002` |
| Lane (if the batch forked) | none — one chain, trigger A4 not fired · module `relmap` |
| Requirement(s) | US-RM-002 · HLR-RMG.1 · LLR-RMG.1.1, LLR-RMG.1.2, LLR-RMG.1.3 (and the Inc-1 rulings recorded first: ledger `.44`–`.50`) |
| Acceptance | Layer B: none in this increment — AT-118 and AT-125 run `mapper --audit` through the hook that lands in Inc-5 (proposal §2.1 *Layer phasing*); `test_snapshot_gaps` is Inc-4's (ledger `.33`) · Layer 0 / A: the 50 nodes of `tests/test_relmap_gaps.py` |
| Agent | `software-dev` |
| Date | 2026-10-25 |

---

## 1 · What changed

**First, the orchestrator's rulings on Inc-1's open items were written into the ledger** (append-only, entries `.44`–`.50`, each with
requirement, asserting test and mutant) with the matching `Ledger:` back-pointers in `01-requirements.md`: `.44` `cut`/`DISPLAY_MAX` is
120 characters in total, the last being `…` (accepted as built; the "121-character id" wording amended); `.45` the memo arm runs on sampled
rows of the 2,000-node chain (LLR-RMM.2.2 wording amended); `.46` a stdlib-ban census (`subprocess`, network modules, write-mode opens) lands
with Inc-3 as a planned Inc-3 test named `test_stdlib_bans` (in the isolation test module), added to PLAN row 3; `.47` the silent-contract choices are stated; and, from the review,
`.48` raw `Problem` subjects (the formatter cuts and escapes; Inc-5 asserts it), `.49` duplicate identical edges are kept, `.50` `sourced` is not
intersected with the node kinds. `.51` records this increment's own readings. F4 is `BACKLOG.md` row `B-145`. The `model.py` module docstring was
corrected as a comment-only edit (F2: the counter lives in `reach`; `down` is the single adjacency read; a ranking must go through `reach`).

**Then `mapper/relmap/gaps.py`** (131 lines). `Gap(severity, kind, node, sentence, reach)` is a frozen value. `detect_gaps(map)` is generic over
`map.profile.gaps`: for every catalogue row whose `needs` are all in `map.sourced` it runs the row's pattern — `cycle` (one gap per
`RelMap.cycles` component, on its first member, "cycle of <n> nodes through <id>"), `lacks_in` / `lacks_out` (nodes of `node_kind` that are not the
`dst` / `src` of any edge of the row's type, restricted to `peer` kind when the row names one, only when `status == "active"` for an `eligible` row and
`open` for an `open` row), `edge_unevidenced` (an edge of the row's type with `evidence_missing`, the gap sitting on its `dst`) — and fills the row's
sentence template in one regex pass; a `lacks_*` hit on a node with `unparsed > 0` ends ` (canon rows near this id could not be parsed or linked: <n>)`.
It names no kind, edge type or gap kind (`test_engine_names_no_kind` covers `gaps.py`; so does the adjacency census below). `rank_gaps(map, gaps, limit)`
(`limit: int | None`) asks `RelMap.reach` — and nothing else — for the severity bands needed to fill `limit` printed lines (every band for `None`), ranks all
gaps by severity then reach descending (detection order on ties), and returns `(ranked, reach_not_computed)`, counting the gaps whose reach came back
`None` (they rank with reach 0). `gaps.py` never reads `down`, `up`, `_reach_memo` or `visits` itself, so every traversal is drawn on the map's one shared
visit budget (security C1).

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/relmap/gaps.py` | source | HLR-RMG.1, LLR-RMG.1.1, LLR-RMG.1.2, LLR-RMG.1.3 | NEW: `Gap`, `detect_gaps`, `rank_gaps`; module docstring states the budget rule |
| `mapper/relmap/model.py` | source | LLR-RMM.2.2 | comment-only: module docstring wording (Inc-1 review F2); no code line changed; not counted as a SOURCE file of this increment (declared, see counts) |
| `tests/test_relmap_gaps.py` | test | HLR-RMG.1, LLR-RMG.1.1–.3 | NEW: 50 nodes — one positive and one negative arm per catalogue row, qualifier, one-pass slots, activation, eligibility, ranking, bands, hub and sink shapes with the `down` tripwire, the adjacency census with planted-violation arms |
| `docs/ARCHITECTURE.md` | doc | LLR-RMP.2.1 | §2 `relmap` row: `mapper/relmap/gaps.py` written into the owned paths (as built Inc-2) |
| `.dev-flow/2026-10-25-relmap-r1-batch/01-requirements-ledger.md`, `01-requirements.md`, `PLAN.md`, `03-increments/increment-001.md`, `.dev-flow/BACKLOG.md` | doc | | ledger `.44`–`.51`, back-pointers, wording amendments (`.44`, `.45`), PLAN row 3 (`test_stdlib_bans`), Inc-1 packet §4b and follow-ups, `B-145` |
| this packet and `evidence/inc2-*.txt` | doc | | four redacted transcripts |

| Count | Value |
|---|---|
| **SOURCE files** | **1 / 4** (`gaps.py`; plus a comment-only docstring edit to the Inc-1 file `model.py`, declared above) |
| Test files | 1 new (uncapped) |
| Doc files | 6 (outside the count) |

---

## 3 · How to test

```bash
cd <worktree>   # C:/Users/<user>/AppData/Local/Temp/ds-units/wt-r1
export PYTHONPATH=<worktree>
env -u NO_COLOR -u TERM python -c "import mapper; print(mapper.__file__)"      # must resolve inside the worktree
git add mapper/relmap tests/test_relmap_*.py                                 # the A3 census needs new files staged
env -u NO_COLOR -u TERM python -m pytest -q -p no:cacheprovider tests/test_relmap_gaps.py tests/test_relmap_isolation.py tests/test_relmap_model.py tests/test_relmap_profile.py tests/test_arch_osopen_callers.py
env -u NO_COLOR -u TERM python -m pytest -q -p no:cacheprovider tests/test_mod_*.py tests/test_repair_map_truth.py tests/test_arch_osopen_callers.py tests/test_a3_census.py tests/test_no_operator_paths.py
```

Targeted files only; never the full suite. `mapper.__file__` printed `C:\Users\<user>\AppData\Local\Temp\ds-units\wt-r1\mapper\__init__.py` (executed).

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** (the four detector patterns, activation, eligibility, qualifier, ranking, bands, bounded ranking) | `core` · `full` | `test_relmap_gaps.py` (50 nodes) | executed: GREEN |
| **A · white-box** `TC-NNN` ↔ LLR | `core` · `full` | `test_relmap_isolation.py` (59 nodes; the engine-literal census and the import census now also walk `gaps.py`), `test_gaps_reads_no_adjacency_itself` | executed: GREEN |
| **B · black-box** `AT-NNN` through the shipped surface | `core` · `full` | n/a — no shipped surface in Inc-2; AT-118 and AT-125 first realise at Inc-5 | n/a — Layer B starts at Inc-5 |

Targeted run (5 files): **183 passed**, exit 0, 12.2 s wall (`evidence/inc2-green-first.txt`). Heaviest arms, each its own function and none reading a clock: `test_rank_visit_cap` and `test_rank_limit_none_stays_inside_the_budget` (50,000-gap hub shape, visit counter plus `down` tripwire), `test_rank_100k_sinks`.
Guard run (`test_mod_*` ×7, `test_repair_map_truth`, `test_arch_osopen_callers`, `test_a3_census`, `test_no_operator_paths`): **143 passed**, exit 0, 36.0 s wall (`evidence/inc2-guards.txt`); the A3 pin `test_a3_census.py:329` (86) did not move. `tests/test_no_operator_paths.py` is part of that run and was re-run on the final tree before the commit (see the commit record). Mutation battery driver: 92.1 s wall.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | `gaps.py` moved out of the tree (C-20 move-aside), then the 15 mutants of the next table |
| Instrument | project code: a short Python driver (`battery.py`, scratch outside the repo) — hash before, one edit or one move, the targeted pytest run, restore, hash after, one verdict per mutant |
| Where it ran | the batch worktree, by the `software-dev` author (nothing else mutating it); deterministic, the orchestrator may re-run |
| Transcript | `evidence/inc2-red-code-absent.txt` (tests on the code-absent tree) and `evidence/inc2-red-mutants-battery.txt` (move-aside + mutants) |
| Restore proven by | file sha256 returned to its pre-mutation value after every arm (`gaps.py` `eeb3b1cd…`, `profile.py` `2a759d01…`, equal to the Inc-1 digest) |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` and the `__pycache__` of `mapper/`, `mapper/relmap/`, `tests/` purged before every run |
| Arms resolved at baseline | 50 (battery baseline: `tests/test_relmap_gaps.py` GREEN) |
| Verdict granularity | per mutant, by the failing node ids the driver reports |
| Arms that stayed GREEN | none of the 15 mutants survived |

| Field | Value |
|---|---|
| **RED counterfactual** | (1) code-absent tree: collection `ImportError: cannot import name 'gaps' from 'mapper.relmap'`, `1 error`, exit 2, `evidence/inc2-red-code-absent.txt` (captured before two test-side fixes: a filter on one arm that also saw an `ORPHAN TC` gap, and the added `TC<dst>` one-pass-slot arm; neither changes the collection error). (2) move-aside of `gaps.py`: collection error on `tests/test_relmap_gaps.py`, exit 2, 1.1 s; restored, digest equal `eeb3b1cd229a384b…`, `evidence/inc2-red-mutants-battery.txt` |

| Field | Value |
|---|---|
| **Mutation verdicts** | 15 mutants, **15 KILLED, 0 SURVIVED**, every restore hash-equal. M-RMG-1 (drop the status eligibility) → `test_retired_node_not_reported_but_traversed` ×6 arms, `test_an_active_node_is_reported_where_the_retired_one_is_not`, `test_open_at_without_test_positive_and_negatives` · M-RMG-2 (swap two catalogue severities in `profile.py`: `HLR WITHOUT LLR` ↔ `ORPHAN TC`) → `test_ranking_follows_the_catalogue_severities`, `test_hlr_without_llr_positive_and_negative`, `test_orphan_tc_positive_and_negative_and_no_status_filter` · M-RMG-3 (ignore `sourced`) → `test_unsourced_kind_is_silent` and others (the whole HLR family) · M-RMG-4 (drop the qualifier) → `test_gap_sentence_qualified` · M-RMG-5 (no visit bound: a private BFS over `down`, never `reach`) → `test_rank_visit_cap`, `test_rank_limit_none_stays_inside_the_budget` (the `down` tripwire), `test_gaps_reads_no_adjacency_itself`, and the two band/limit arms · M-RMG-6 (a withdrawn LLR is no child) → `test_withdrawn_only_llr_is_not_a_gap`. Own extra mutants: M-RMG-7 (peer ignored) → `test_peer_kind_restricts_the_linking_edge` · M-RMG-8 (reach for every band despite `limit`) → `test_rank_computes_reach_only_for_the_bands_needed_to_fill_the_limit` · M-RMG-9 (not-computed not counted) → `test_rank_visit_cap` +2 · M-RMG-10 (reach ascending) → `test_ranking`, `test_rank_visit_cap` · M-RMG-11 (severity out of the key) → `test_ranking` +4 · M-RMG-12 (slots filled sequentially) → `test_sentence_slots_are_filled_in_one_pass` (it SURVIVED the first run of the battery: the arm only had a title carrying a slot name, which the sequential order happens to expand last; the `TC<dst>` edge arm was added and the whole battery re-run) · M-RMG-13 (cycle through the last member) → `test_cycle_positive_two_node_ring`, `test_cycle_gap_reach_goes_through_the_first_member` · M-RMG-14 (evidence gap on `src`) → `test_at_tagged_only_…`, `test_verifies_without_evidence_…` · M-RMG-15 (`open` filter inverted) → `test_open_at_without_test_positive_and_negatives` +2 |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| adjacency census (`adjacency_reads`) | 6 planted reads (`m.down`, `m.up`, `m._down`, `m._reach_memo`, `m._visits`, `m.neighbourhood`), each must be reported | `test_the_adjacency_census_finds_a_planted_read` ×6 pass only because each plant is found; M-RMG-5 on the real file → `test_gaps_reads_no_adjacency_itself` RED |
| the `down` tripwire (`tripwire()`) | M-RMG-5: ranking bypasses the shared budget | `AssertionError: tripwire: more node expansions than the budget` after 2,000,001 calls, no hang (`evidence/inc2-red-mutants-battery.txt`, 5.5 s for the whole file) |
| engine-literal census over `gaps.py` | Inc-1's planted literals (`"refines"`, `"US"`, `"HLR WITHOUT LLR"`, `"binds"`) | already shown RED in Inc-1; `test_gaps_module_names_nothing_of_the_profile` and `test_engine_names_no_kind` now walk the real `gaps.py`, which holds none |
| band accounting (`mapper.relmap.model.RelMap.visits`) | M-RMG-8 reaches every band | `test_rank_computes_reach_only_for_the_bands_needed_to_fill_the_limit` RED on `visits == 22` |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 instruments, each shown RED by a planted or mutated known-bad input before its green was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| gap sentences (the strings `detect_gaps` emits, the future audit lines' payload) | every sentence arm compares the full emitted string to the template with its slots filled (`"US1 has no covering AT: u1"`, `"TC1 verifies LLR1 with no evidence"`, the qualifier with its exact parenthetical) | 8 rows asserted by exact string, 50 nodes green |
| `docs/ARCHITECTURE.md` §2 `relmap` row | `test_at_p04_every_owned_path_exists_on_disk[relmap-mapper/relmap/gaps.py]` over the written row | collected and passed (`evidence/inc2-guards.txt`) |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts, each asserted against the form its producer wrote |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED on the code-absent tree (exit code 2, 1.1 s wall) | `.dev-flow/2026-10-25-relmap-r1-batch/evidence/inc2-red-code-absent.txt` | `79a6a686389a44a0c6e820a6725e44df1857d62c1c42e87d7a8db2a5aef7fd69` |
| GREEN, targeted run, 183 passed (exit code 0, 12.2 s wall) | `.dev-flow/2026-10-25-relmap-r1-batch/evidence/inc2-green-first.txt` | `e169d6dc945c3d17b324f402f25d9ffa5ef8f289402af66ef0317b903eb01907` |
| Guard suites, 143 passed (exit code 0, 36.0 s wall) | `.dev-flow/2026-10-25-relmap-r1-batch/evidence/inc2-guards.txt` | `96c861636d851039a6ca9a52f93e8cb9d59d407f69b5067f9a92eba7f4bb3363` |
| Move-aside RED + 15-mutant battery (driver exit code 0, 92.1 s wall) | `.dev-flow/2026-10-25-relmap-r1-batch/evidence/inc2-red-mutants-battery.txt` | `870d264c8407d5bdab635ec402571be11e52dc48acb25402d798a3e612f400fc` |

| Field | Value |
|---|---|
| **Evidence files** | 4 artifacts, each at the declared home and cited with the digest of its stored bytes; every transcript is redacted (`<user>`) before hashing and records its own exit code and wall time |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes: "`gaps.py` names no profile literal" and "reads no adjacency" are absences over today's file; "the reqharness catalogue cannot form a cycle" (premise 5) means the `cycle` arm cannot run on the shipped profile |
| If the result is an ABSENCE, what made the search wide enough | both censuses are AST walks over the whole file (every `Constant` string, every `Attribute`), not greps; the literal set is derived from the shipped profile and guarded by `len >= 17` (Inc-1) |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_the_adjacency_census_finds_a_planted_read` (6 plants) protects `test_gaps_reads_no_adjacency_itself` |
| Conjunctive criteria: one mutation per conjunct | a `lacks_*` hit has four conjuncts (kind, not linked, eligible, open): M-RMG-1 (eligible), M-RMG-15 (open), M-RMG-7 (peer), M-RMG-6 (peer status) and the "linked" check by every negative arm |
| Synthetic instance of the absent case | `LOOPY` (cycle gap), `PEER` (peer restriction), `HUB`/`CHAIN` (reach shapes), `other` (a catalogue the engine has never seen) |
| **Positive control for every probe that returned an ABSENCE** | the adjacency census returns `[]` on the real `gaps.py` and the planted read in each of its 6 forms; the literal census returns `[]` on the real file and ≥ 1 on each Inc-1 plant |

### Reverse census — trigger family B, and A3

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `git grep -l "relmap\|rank_gaps\|detect_gaps" -- tests mapper docs` | only the relmap tests, `test_arch_osopen_callers.py` and `docs/ARCHITECTURE.md`; no test of another batch asserts a symbol this increment adds |
| B2 file moved on disk | none moved | no readers to find |
| B3 byte-identical golden captures this source | `git grep -il relmap -- tests/goldens` | 0 hits |
| B4 artifact produced here is consumed elsewhere | `gaps.py` has no importer in `mapper/` (`git grep -n "relmap.gaps" -- 'mapper/*.py'` → 0 hits); Inc-5 `audit.py` will | no consumers until Inc-5 |
| A3 interface consumed by another module changed | the module-map oracles: `test_mod_*`, `test_repair_map_truth`, `test_arch_osopen_callers`, `test_a3_census` | 143 passed; the A3 pin 86 unmoved |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1, B2, B3, B4, A3), each with its command and verdict; B2 and B3 did not fire |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| "120 characters" wording of `DISPLAY_MAX` amended to "120 characters in total, the last being `…`" (ledger `.44`) | statements in `01-requirements.md` that say a cut value is 120 characters followed by or ending with `…` | `grep -n "121-character\|cut to 120\|120 characters" 01-requirements.md` run before the edit | 3 (line 24 definition, the LLR-RMU.1.2 numeric threshold, and AT-129's "no value longer than 120 characters before escaping") | 2 (the definition and the numeric threshold) | AT-129 already reads "≤ 120 characters before escaping", which the 120-in-total reading satisfies |
| "a 2,000-node chain" memo arm amended to "sampled rows" (ledger `.45`) | places that name the memo arm's chain | `grep -n "2,000-node" 01-requirements.md` | 1 | 1 | none |

| Field | Value |
|---|---|
| **Correction population** | 2 corrections, each enumerated before its first site was edited |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| `planned for Inc-2 to Inc-5` (the old `relmap` owned-paths cell) | `git grep -c "planned for Inc-2 to Inc-5" -- docs` → 0 hits | yes | `docs/ARCHITECTURE.md` §2 `relmap` row now says Inc-3 to Inc-5 and lists `gaps.py` |

### Signed-balance test ledger

`post = base − deleted + added` → `183 = 132 − 0 + 51` for the five targeted files: the Inc-1 four files held 132; this increment adds the 50 nodes of `test_relmap_gaps.py` and one parametrised arm (`gaps.py`) to the import census and the Inc-1 isolation parametrisations (58 → 59) ✓ reconciles with `183 passed` (collected with `--collect-only`: 50 + 59 + 53 + 16 + 5).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer — Claude Sonnet subagent executing agents/code-reviewer.md · iterate (BLOCK-UNTIL: F1) → F1 discharged f02dbbd` · F1 MAJOR (mutant D, the edge-type filter in `_lacks`, survived 50 arms) closed by two arms, RED with mutant D applied and GREEN restored (gaps.py sha256 returned to `eeb3b1cd…` between runs); F2-F5 MINOR taken in the same pass · `evidence/review-inc002.md`, `evidence/inc2f-red-mutant-d.txt`. The orchestrator's re-read of the added arms and the Inc-2 approval are NOT recorded here. |

### Follow-ups after the independent review (Inc-2 review pass, 2026-10-25; ledger `LED-…52`)

| Item | Disposition |
|---|---|
| F1 MAJOR: the edge-type filter in `_lacks` untested (mutant D survived) | FIXED: `test_edge_type_filter_lacks_in_other_edge_type_is_no_verifier` (an LLR whose only edge is a `refines` from its HLR is still `LLR NOT VERIFIED`) and `test_edge_type_filter_lacks_out_other_edge_type_is_no_binding` (an open AT whose only edge is `covers` is still `OPEN AT WITHOUT TEST`; `reqharness` has no other outgoing edge for a `TC` or `HLR`, so the `lacks_out` counterpart uses the `binds` row). RED with mutant D applied to the committed `gaps.py` (`if e.type != row.edge` replaced by `if e.type == "x"`): `3 failed, 50 passed`, exit 1, 6.1 s, the two F1 arms plus the F3 arm, `evidence/inc2f-red-mutant-d.txt` (`65911f3b…`). Restored and hash-verified (`eeb3b1cd229a384b…`), then GREEN. |
| F2 `eligible`/`open`/qualifier apply to `lacks_*` rows only | FIXED: one paragraph in the `gaps.py` module docstring. No construction refusal added (no shipped row sets them elsewhere; optional per the review). |
| F3 `_fill` raised a bare `KeyError` on a slot the pattern does not supply | FIXED: `values.get(name, m.group(0))` (the slot stays as written); arm `test_a_slot_the_pattern_does_not_supply_stays_as_text`, RED on the committed `_fill` (`KeyError: 'src'`, `1 failed, 52 passed`, `evidence/inc2f-red-f3-base.txt`, `dc7b12bc…`). Chosen over profile validation: one line, no new refusal path. |
| F4 LLR-RMG.1.3 names `::test_rank_limit_none` | FIXED: the contract names `::test_rank_limit_none_ranks_every_band` and `::test_rank_limit_none_stays_inside_the_budget`; ledger `.52`. |
| F5 two long docstring lines | FIXED: `gaps.py` `rank_gaps` first line split into a short summary plus a body sentence; `model.py` line wrapped (comment-only). |

Final tree: `gaps.py` sha256 `dd180acf6256830670e33b6b8e721641926a37fa7c0732fc8874ebdcb22a6b3b` (the digest in the commit record above is the pre-review `eeb3b1cd…`); `model.py` `1b602e84…`. GREEN: relmap files plus the files whose docstrings changed, 276 passed, exit 0, 37.7 s, `evidence/inc2f-green-final.txt` (`d653492f…`); guards (`test_mod_*`, `repair_map_truth`, `a3_census`, `no_operator_paths`, plus `test_relmap_descriptor` re-run as a live-mutant check) 229 passed, 1 skipped (`mkfifo` n/a on Windows), exit 0, 43.5 s, `evidence/inc2f-guards.txt` (`1c95102f…`). The review report itself: `evidence/review-inc002.md` (`b8b52ef2…`).

---

## 5 · Risks

- **Reach is flat on the live canon** (OQ-R1-8): all seven live gaps tie at 0, so the ranking arms are proved on synthetic shapes only; the ranking of the live gaps is detection order.
- **Budget exhaustion is sticky and shared**: a view that spends the map's budget before ranking leaves every not-yet-memoised gap "not computed"; the count line (Inc-5) says so. This is the contract; `test_rank_shares_the_budget_with_reach_calls_made_elsewhere` pins that ranking never resets it.
- **Layer B does not exist yet**: AT-118/AT-125 run at Inc-5; `test_snapshot_gaps` (the 7 live gaps, 2 qualified) at Inc-4.
- **A gap on a cycle member's component uses the first member's reach**, per the contract, although a component of the authored graph need not be one of the `down` graph when edge types point both ways; the reqharness profile forms no cycle (premise 5), so this is only visible with a synthetic profile.
- **No real Python 3.10 run** (unchanged from Inc-1): the floor census walks `gaps.py` too and found nothing.

---

## 6 · Pending items / spec deviations

Contract readings made here, all in ledger `.51` (none changes a stated behaviour): an evidence gap sits on the edge's `dst`; `detect_gaps` returns reach 0 and `rank_gaps` returns ALL gaps ranked (the caller prints the first `limit`); sentence slots are filled in one pass; the `peer` restriction counts only edges whose other end has that kind; a cycle gap sits on the first member.

1. **`rank_gaps` returns all gaps, not only `limit`**: the contract says "returns (ranked, reach_not_computed)" and the formatter's "gaps shown X of Y" overflow line needs Y, so the full list is returned. If Inc-5 prefers a truncated list, that is a one-line change plus its test.
2. **`model.py` was touched** by a comment-only docstring edit (Inc-1 follow-up F2, by the orchestrator's instruction); it is not a SOURCE file of this increment and no code line changed.
3. **Gate run** (`PYTHONIOENCODING=utf-8 python devflow-validate.py --brief .`): see §Gate in the commit record below; the expected station reds are the thirteen `V2` nodes (AT-117…AT-129, minted at Inc-5).

Nothing is deferred silently.

---

## 7 · Suggested next task

Inc-3 (`mapper/yamlscan.py`, `mapper/store.py`, `mapper/relmap/descriptor.py`, 3 source files): FIRST the byte-identity golden on the base `store.py`, committed alone; then the extraction; the descriptor reader with causes K1–K17; the stdlib-ban census `test_stdlib_bans` (ledger `.46`) lands with it. Before it starts: the orchestrator's independent review of this diff.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 1 / 4: `mapper/relmap/gaps.py` (§2); plus a declared comment-only edit of Inc-1's `model.py` |
| 2 | Tests written in this same increment | all | ✓ | `tests/test_relmap_gaps.py`, 50 nodes; 183 passed (`evidence/inc2-green-first.txt`) |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | detectors, ranking and bands are branching logic; 50 nodes, mutation-measured 15/15 |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | code-absent RED + move-aside, `evidence/inc2-red-code-absent.txt` (`79a6a686…`) and `evidence/inc2-red-mutants-battery.txt` (`870d264c…`) |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | five probes with commands in §4; A3 pin 86 unmoved (`evidence/inc2-guards.txt`) |
| 6 | `code-reviewer` passed | `core` · `full` | ⚠ | iterate (BLOCK-UNTIL: F1) → F1 discharged f02dbbd (§4b, follow-ups); the re-read and the approval are the orchestrator's |
| 7 | No file from another lane touched | all | ✓ | no lane; paths in the file set of proposal §2.1 row 2 plus the comment-only `model.py` docstring edit the orchestrator ordered |
| 8 | Frozen interfaces untouched (or returned to the trunk) | all | ✓ | `Gap(severity, kind, node, sentence, reach)`, `detect_gaps(map) -> list[Gap]`, `rank_gaps(map, gaps, limit: int \| None) -> tuple[list[Gap], int]` match proposal §4 D3 exactly; no D1/D2/D4/D5 name touched |
| 9 | Coverage claims verified **on disk**, not from intent | all | ✓ | every node named in §4 exists in `tests/test_relmap_gaps.py` and was collected (50 arms) |
| 10 | Load-bearing emptiness declared, with its synthetic instance (C-55) | all | ✓ | §4 *Load-bearing emptiness* |
| 11 | **Mutation verdicts** declared — per arm | all | ✓ | 15 mutants, 15 KILLED, per mutant and node in §4 |
| 12 | **Instrument RED-proof** declared | all | ✓ | 4 instruments, §4 |
| 13 | **Correction population** declared | all | ✓ | §4: 2 corrections, enumerated with their commands |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4: 2 artifacts |
| 15 | **Independent review** names somebody | all | ✓ | `code-reviewer` (Claude Sonnet subagent), iterate then F1 discharged (§4b) |
| 16 | **Evidence files** declared | all | ✓ | §4: 4 artifacts with SHA-256 |
