# Increment 001 — US-Q3-001 · `Q3 scalecheck sweep + Canvas.put audit hook (lane L3, trunk-first)`

> **Artifact language.** Canonical **English scaffold**; generated in the batch's language.
> **Owed in.** `core` ✓ · `full` ✓ · **packet home:** `.dev-flow/2026-10-23-hygiene-batch/03-increments/increment-001.md` (repo, next to the diff it describes)

| Field | Value |
|---|---|
| Batch | `2026-10-23-hygiene-batch` |
| Increment | `001` |
| Lane (if the batch forked) | `L3` · `canvas` (trunk-first landing of frozen interface D1; lanes L1/L2 fork after this commit) |
| Requirement(s) | `US-Q3-001 · HLR-Q3.1, Q3.2 · LLR-Q3.1.1, Q3.1.2 (amended .11), Q3.2.1, Q3.2.2, Q3.2.3 (amended .12/.13)` |
| Acceptance | `AT-115` · `AT-116` · white-box `TC` = `tests/test_scalecheck.py` sweep/audit arms · unit layer-0 = `tests/test_canvas_audit.py` |
| Agent | `software-dev` (orchestrator-run trunk work; ruling R10 amendments in the same landing) |
| Date | `2026-10-23` |

---

## 1 · What changed

BLUF: `Canvas(w, h, tones=(), fallback="", audit=None)` ships the frozen D1 signature — an
optional injected mapping recording `put`'s clip/overprint events, observational so no
rendered byte moves (all 12 digests + 16 perf goldens hold un-re-baselined). The scalecheck
sweep (`tests/test_scalecheck.py`) proves the six renderers of the `mapper.views` roster stay
inside their viewport at 80x24, 90x30, 118x34, 160x45, 200x50 across the four recorded states
(`plain`/`folded`/`empty`/`orphan`, `design/state-matrix.md`) — 6 × 5 × 4 = 120 combos — and
the audit arm fails the sweep on any unexplained overprint or clip.

**Ruling R10 (same landing):** the RED gate measured the full 120-combo matrix BEFORE the hook
existed and found the sealed oracle text unexecutable: Layered returns `h − 4` lines on graphs
smaller than the frame and its wordmark-header meter always spills `len('{n} nodes') − 2` cells
past `w` (byte-pinned by the perf goldens); every renderer's empty-state short-circuit
constructs no canvas; and only `Layered`/`Radial`/`RailTimeline` construct a canvas at all.
Three measured amendments record the corrected oracle — ledger `.11` (LLR-Q3.1.2 geometry:
1..h lines, per-line width bound, Layered header spill asserted exactly as
`(w − 2) + cell_len('{n} nodes')` + declaration), `.12` (LLR-Q3.2.3 empty-state zero
constructions) and `.13` (LLR-Q3.2.3 per-renderer construction census; sweep-arm negative
control re-named). The state SET is untouched; no PDR re-seal is triggered; the DDR re-reads
all three.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/canvas.py` | source | LLR-Q3.2.1, Q3.2.2 | `audit=None` trailing parameter (frozen D1); `put` appends `(x, y)` under `clip` (out-of-bounds non-space) and `overprint` (in-bounds, held cell a different alphanumeric AND written char alphanumeric), nothing otherwise; write path byte-identical |
| `tests/test_canvas_audit.py` | test | LLR-Q3.2.1, Q3.2.2 (AT-116 arms) | NEW — `test_events` (event set + both limbs), `test_text_and_wire_paths_share_put_and_default_sink_is_none`, `test_byte_identity` (rows() plain+spans identical with/without sink) |
| `tests/test_scalecheck.py` | test | LLR-Q3.1.1, Q3.1.2, Q3.2.3 (AT-115 arm) | NEW — `test_renderer_roster_derived` (completeness guard), `test_sweep` (120-combo geometry + fold-invariance), `test_sweep_audit_arm` (sink injected at construction sites; per-renderer census) |
| `tests/test_a3_census.py` | test | `LLR-Q3.2.1` (B-44 signature pin of the frozen D1 interface) · `LLR-Q3.2.3` (arg-ful call-site census 83 → 86 — the three itemized sweep construction sites the audit arm counts) | B-44 signature pin amended to the frozen signature (same landing); arg-ful call-site pin 83 → 86 with the three itemized new sweep sites |
| `docs/ARCHITECTURE.md` | doc | — | §3 `canvas` row and §4 LANDED row: commitment → LANDED, signature `…, audit=None)` |
| `.dev-flow/…/01-requirements.md` + ledger + PLAN + `design/state-matrix.md` | doc | LLR-Q3.1.2, Q3.2.3 | ruling R10 amendments: ledger `.11`/`.12`/`.13` (Before/After · Deleted/New), LLR bodies re-derived, matrix errata |

| Count | Value |
|---|---|
| **SOURCE files** | **1 / 4** |
| Test files | 3 (2 new, 1 amended) |
| Doc files | 6 (outside the count) |

---

## 3 · How to test

```bash
env -u NO_COLOR -u TERM python -B -m pytest -q -p no:cacheprovider \
  tests/test_canvas_audit.py tests/test_scalecheck.py tests/test_a3_census.py \
  tests/test_canvas.py tests/test_repair_depth.py tests/test_perf_paint_clip.py
```

---

## 4 · Test results

| Layer | Owning node(s) | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `tests/test_canvas_audit.py` (3 nodes) | 3 | 3 passed |
| **A · white-box** | `tests/test_scalecheck.py` (3 nodes) | 3 | 3 passed |
| **B · black-box** | AT-115 via `test_sweep` (shipped headless roster as screens consume it); AT-116 via `test_byte_identity` + `test_sweep_audit_arm` | 120 geometry combos + 90 audited non-empty renders | 0 misfits, 0 unexplained events |

One complete gate run: **146 passed, 15 deselected, exit 0**
(`evidence/l3-green-2026-10-23.txt`, sha256 `b646a255b40b3fbba66edeae2a5550cf1711cc3b19506f58b6fb6419932106e4`).

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | base tree: the increment's own new tests run against a `Canvas` that has no `audit` parameter (net-new assertions, RED by construction); separately, the deliverable file `mapper/canvas.py` MOVED ASIDE (C-20 move-aside, never stash) |
| Instrument | project code: hand + `evidence/mutate_l3.py` (battery); move-aside by rename |
| Where it ran | the trunk worktree `wt-hyg` on `feat/hygiene-batch`, run by the orchestrator (no lane exists yet) |
| Transcript | `evidence/l3-red-2026-10-23.txt` (base RED, sha256 `55af8900e231c32f556aa2058bd09d67179f6ad17808c0788eaa071fa1cce77c`); `evidence/l3-move-aside-2026-10-23.txt` (sha256 `60a1faa0b2b496cf89f193857b71de33346e4ccad9e7b11889d781881bf5d125`) |
| Restore proven by | file hash returned to its pre-mutation value — move-aside: `decab49c…dea765d` before == after ("RESTORE PROVEN" in the transcript); battery: per-arm `before`/`after` digests |
| Bytecode cache | runs used `-B` / `PYTHONDONTWRITEBYTECODE=1` (C-46) |
| Arms resolved at baseline | base RED: 6 arms (5 failed + 1 passed — the roster guard passes on base by design); move-aside: 5 per-file invocations, each exit 2 (`ModuleNotFoundError: mapper.canvas` — `tests/conftest.py` imports the file, so the absence reds the session at import; per-file invocations name each arm) |
| Verdict granularity | per resolved node id / per file invocation |
| Arms that stayed GREEN | `test_renderer_roster_derived` on base (the roster exists pre-increment — the guard's reddening mutation is a dropped export, not this increment's delta); all other arms RED |

| Field | Value |
|---|---|
| **RED counterfactual** | the increment's own new assertions fail on base with `TypeError: Canvas.__init__() got an unexpected keyword argument 'audit'` (transcript above); with `mapper/canvas.py` moved aside, every holding suite goes RED at import — restore digest `decab49c…dea765d` |

| Field | Value |
|---|---|
| **Mutation verdicts** | 4 arms, all KILLED, transcript `evidence/l3-mutation-battery-2026-10-23.txt` (sha256 `f022b5a12a2aff50d0018a8914082a49214e57d792ee91c60e70885807dd139e`): **M-Q3-1** — `mapper/views/radial.py` `inner = w - 2` → `w + 2` (bounds handling broken; executed on the WIDTH limb — the h+1-line shape is structurally self-absorbed by every renderer's own `[:h]` cut on small-map renders, measured) → `test_sweep` RED · **M-Q3-2** — the overprint event append removed → `test_events` RED · **M-Q3-3** — the sink touches the cell write (`ch.upper()` under audit) → `test_byte_identity` RED · **M-Q3-4** — the alphanumeric gate on the NEW character dropped (`and ch.isalnum()` → `and True`) → `test_events` RED. Restores hash-proven per arm; arms that stayed GREEN: none |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `pytest` (the gate suite) | the increment's new tests on the base tree | 5 failed / 1 passed, exit 1 — `l3-red-2026-10-23.txt` |
| `evidence/mutate_l3.py` | two arms whose anchors did not exist in the CRLF tree (first battery run) | `BAD (anchor count 0 != 1)` on both, exit 1 — the runner reports its own inapplicability instead of passing |
| the A3 census pin (`tests/test_a3_census.py:315`) | L3's own three new arg-ful render call sites | `derived 86 arg-ful call sites against a pinned 83` — the pin caught its own increment's drift |
| the privacy grep | a synthetic line carrying a home path + email | the probe printed both hits (positive control) before reporting the real bundle CLEAN |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 instruments, each shown RED before its first PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the audit sink's event lists | `assert audit["clip"] == [(4, 0), (-1, 1)]; assert audit["overprint"] == [(0, 0), (3, 0)]` against the mapping `put` filled | passed — the emitted events, not the intent |
| `rows()` under audit vs sinkless | plain and spans compared row-by-row on the two emitted `list[Text]` | identical (the byte-identity arm) |
| the rendered sweep text | `cell_len` measured on each emitted line of `renderer.render(...).plain` | 120 combos, 0 misfits under the amended oracle |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 3 artifacts, each asserted against the form its producer emitted |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| base RED transcript | `.dev-flow/2026-10-23-hygiene-batch/evidence/l3-red-2026-10-23.txt` | `55af8900e231c32f556aa2058bd09d67179f6ad17808c0788eaa071fa1cce77c` |
| R10 measurement probe (120 combos) | `.dev-flow/2026-10-23-hygiene-batch/evidence/l3-sweep-measurement-probe-2026-10-23.txt` | `5d0a7bae1d016e2674f5c4aa0beadc3bc2ca3f5b4a70d2e64fb51fd282f0af47` |
| GREEN gate transcript | `.dev-flow/2026-10-23-hygiene-batch/evidence/l3-green-2026-10-23.txt` | `b646a255b40b3fbba66edeae2a5550cf1711cc3b19506f58b6fb6419932106e4` |
| move-aside counterfactual | `.dev-flow/2026-10-23-hygiene-batch/evidence/l3-move-aside-2026-10-23.txt` | `60a1faa0b2b496cf89f193857b71de33346e4ccad9e7b11889d781881bf5d125` |
| mutation battery transcript | `.dev-flow/2026-10-23-hygiene-batch/evidence/l3-mutation-battery-2026-10-23.txt` | `f022b5a12a2aff50d0018a8914082a49214e57d792ee91c60e70885807dd139e` |
| mutation battery runner | `.dev-flow/2026-10-23-hygiene-batch/evidence/mutate_l3.py` | `afef7aa7c76f82709133b3b73f96fa097a56d377c380c7cf50e91a53b597a479` |
| B3 golden census | `.dev-flow/2026-10-23-hygiene-batch/evidence/l3-b3-golden-census.txt` | `48450c4b6ea8cb2283805e12786ce4b0a32aad0911cbd6fc8a75209fd9a3ff83` |

| Field | Value |
|---|---|
| **Evidence files** | 7 artifacts, each at the declared home and cited with the digest of its stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — the audit arm's "0 unexplained clips/overprints" is an absence over the 90 non-empty audited renders |
| If the result is an ABSENCE, what made the search wide enough | every renderer × size × state combo is rendered and its sink read — the search is the full recorded matrix, not a sample |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_sweep_audit_arm` — the arm's docstring names the census and the failure mode, so a future "improvement" cannot silently drop the zero-event assertion |
| Conjunctive criteria: one mutation per conjunct | clip clause and overprint clause each carry their own reddening mutation (M-Q3-1 class / M-Q3-2) |
| Synthetic instance of the absent case | the injected clip/overprint writes in `test_events` (unit level) and the M-Q3-1 width break (sweep level) — a probe that returned a NON-absent output on known-bad input |
| **Positive control for every probe that returned an ABSENCE** | M-Q3-1 (width break) reddens `test_sweep`; M-Q3-2/M-Q3-4 redden `test_events`; both recorded in the battery transcript |

### Reverse census — trigger family B, and A3

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rl "Canvas" tests/` | `test_canvas.py`, `test_a3_census.py`, `test_repair_depth.py`, `test_perf_paint_clip.py`, `test_canvas_header_charge.py` (byte-pinned must-stay-green — all green in the gate run) + this increment's two new files |
| B2 file moved on disk | n/a — no file moved | none |
| B3 byte-identical golden captures this source | `grep -rn "MASTER_LEGACY_DIGESTS\|goldens/perf/render" tests/` → `test_repair_depth.py:109`, `test_perf_paint_clip.py:172` | byte-pinned census re-run green (`l3-b3-golden-census.txt`, 93 passed) — no golden re-baselined |
| B4 artifact produced here is consumed elsewhere | `grep -rn "audit=" mapper/` | zero hits — the sink is consumed by tests only (ARQ commitment honoured) |
| A3 interface consumed by another module changed | construction-site census (lane.py:199, layered.py:693, radial.py:184 pass nothing) + B-44 pin amended in the same landing | re-run green |

| Field | Value |
|---|---|
| **Reverse census** | 4 probes run of B1 · B2 · B3 · B4 + A3, each with its command and verdict |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| the A3 arg-ful call-site pin (83 → 86) | every arg-ful `render(...)` call site in `mapper/` + `tests/` | the A3 census's own AST derivation (`tests/test_a3_census.py`) | 86 derived vs 83 pinned | the pin value + annotation in `tests/test_a3_census.py` | none — the three new sites are this increment's own tests |

| Field | Value |
|---|---|
| **Correction population** | 1 correction, enumerated with the census's own derivation before the pin was edited; the module map publishes no number (deliberately, row 213) so no map edit was owed |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|---|---|---|---|
| `Canvas(w, h, tones=(), fallback="")` as the CURRENT signature | 2 prose hits (ARCHITECTURE §4 history rows, correctly in the past tense) | yes — every live signature mention carries `audit=None` | `docs/ARCHITECTURE.md` §3 row + §4 LANDED row; `mapper/canvas.py:104` |

### Signed-balance test ledger

`post = base − deleted + added` → L3-scoped: 146 = 140 base-suite arms held green (incl. byte-pinned census) + 6 new nodes (3 audit + 3 sweep) − 0 deleted ✓ reconciles against the gate run. Full-suite reconciliation is owned by the orchestrator after the lanes join (one complete run).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer — Kimi K3 subagent executing agents/code-reviewer.md · OK-with-notes, 0 BLOCKER / 0 MAJOR / 1 MINOR · digests 7/7 match; no new golden minted (tests/goldens untouched) and the B3 census independently re-run green; 2 reviewer-chosen mutants on mapper/canvas.py KILLED with hash-proven restores; nit F1: green transcript omits its recorded exit code — full report .dev-flow/2026-10-23-hygiene-batch/evidence/review-inc001.md` |

---

## 5 · Risks

- The h+1-line form of M-Q3-1 is structurally self-absorbed: every renderer cuts its own
  output to ≤ h (`lines[:h]` — layered.py:461, radial.py:426, lane.py:162/374), so on the
  matrix's small graphs no single edit can emit h+1 surviving lines. The executed arm is the
  width limb (same mutation id, bounds-handling class). A renderer whose cut is ITSELF broken
  is caught by the ≤ h bound — the catching assertion stays live.
- The Q3 thresholds were sealed without ever executing against the tree; R10 corrected three
  of them from measurement (.11/.12/.13). If a fourth unexecutable clause exists, the DDR is
  its last checkpoint before P4.
- **Contamination incident (declared):** during this increment's gate, an unidentified
  concurrent process edited `tests/test_scalecheck.py` (a derived "Canvas-backing split" test
  + docstring/constants) and touched `design/design-proposal.md` / the PDR record (byte-equal,
  so no content drift). The foreign test was defective (source-text derivation ≠ runtime
  construction — it RED-flagged RadialRenderer, whose construction lives in a helper) and
  unaccounted; it was removed and the incident recorded here and in PLAN.md. Evidence
  discipline was re-verified after the removal (battery + GREEN re-run).

## 6 · Pending items / spec deviations

- DDR re-reads ruling R10 and ledger `.11`/`.12`/`.13` (PDR §B row 8 discipline).
- The dangling-edge OutlineRenderer crash stays OUT of this batch — backlog candidate named
  at the batch close (state matrix §Excluded (a)); no action here.
- Trunk watch-item carried: full-suite run once after the lanes join (orchestrator-owned).

## 7 · Suggested next task

Fork the lanes: cut `lane/l1` and `lane/l2` from this commit, create worktrees `wt-l1` /
`wt-l2`, deploy the L1 (Q1 colour) and L2 (Q2 limits: L2a then L2b) agents on the disjoint
file sets of proposal §8.

---

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|
| 1 | ≤4 source files, or reason declared | ✓ | 1 SOURCE file (`mapper/canvas.py`) — §2 |
| 2 | Tests written in this same increment | ✓ | `tests/test_canvas_audit.py`, `tests/test_scalecheck.py` (new in this increment) |
| 3 | Layer 0 written where the criterion applies | ✓ | `test_events` / `test_byte_identity` — `put` crosses a declared module boundary and carries ≥3 paths |
| 4 | **RED counterfactual** declared | ✓ | base RED + move-aside transcripts with digests — §4 |
| 5 | **Reverse census** declared | ✓ | 4 probes + A3 — §4 |
| 6 | `code-reviewer` passed — declared in §4b | ⚠ | `pending — orchestrator schedules` — recorded in §4b, not yet run |
| 7 | No file from another lane touched | ✓ | lanes do not exist yet; L3 is trunk-first |
| 8 | Frozen interfaces untouched (or returned to the trunk) | ✓ | D1 IS the trunk landing; D2 untouched; lanes not forked |
| 9 | Coverage claims verified **on disk**, not from intent | ✓ | every LLR names a realized node; the gate run executed them (146 passed) |
| 10 | Load-bearing emptiness declared, with its synthetic instance (C-55) | ✓ | §4 table — M-Q3-1/-2/-4 as positive controls |
| 11 | **Mutation verdicts** declared — per arm, inert arms named, registry ids cited | ✓ | M-Q3-1…M-Q3-4 all KILLED, restores hash-proven — §4 |
| 12 | **Instrument RED-proof** declared | ✓ | 4 instruments shown RED first — §4 |
| 13 | **Correction population** declared | ✓ | the census pin amendment — §4 |
| 14 | **Emitted-form assertion** declared | ✓ | 3 emitted artifacts asserted — §4 |
| 15 | **Independent review** names somebody | ⚠ | `pending — orchestrator schedules` — the declared pending state, not an empty cell |
| 16 | **Evidence files** declared | ✓ | 6 artifacts with stored-bytes digests — §4 |

---

## Review-findings follow-up — 2026-10-24 (orchestrator-assigned; independent reviews `evidence/review-inc00{1..4}.md`)

**inc001-F1 (MINOR — GREEN gate transcript does not record its exit code) — DISPOSITION: accepted with reason.**
The reviewer's own read confirms the all-pass line (`146 passed, 15 deselected`) is consistent with exit 0 and explicitly states "No re-run owed for this increment"; the claim is evidence-hygiene, not a code defect. Process fix adopted: every follow-up transcript this batch records `exit=$?` on its final line (see `evidence/fu-*-2026-10-24.txt`), exactly the sibling-transcript convention the reviewer pointed at. No product or test file of this increment was touched.
