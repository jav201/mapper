# Increment 011 — operator directive · `personal-reference scrub (CLOSE3 record-only)`

| Field | Value |
|---|---|
| Batch | `2026-10-11-reqharness-batch` |
| Increment | `011` (CLOSE3 — record-only; no product or test change) |
| Lane (if the batch forked) | none — one lane, trunk unit CLOSE3 |
| Requirement(s) | operator directive 2026-10-11 (PLAN.md · Key decisions, CLOSE3 row) — a record-only scrub is governed by no US/HLR/LLR; every `doc` row below traces to the directive entry, every `test` row traces to the requirement its owning increment declared |
| Acceptance | the close-gate reverse trace (V59, ruling Q1) resolves every file the scrub commits touched and every file whose owning packet (`increment-008-ddr-fix.md` / `increment-009-gate-fix.md` / `increment-010-perf.md`) is named outside the `increment-NNN.md` pattern the gate's packet reader parses; `devflow-validate.py --brief` at 0 blocks outside the environment carries V7/V15/V16 |
| Agent | `software-dev` (Kimi, kimi-code / kimi-for-coding), CLOSE3 unit under the orchestrator |
| Date | `2026-10-11` |

---

## 1 · What changed

BLUF: three operator-mandated scrub commits replaced the operator's personal
name, GitHub handle, noreply address, personal paths and employer/client names
with neutral placeholders across tracked text. No functional change anywhere —
string-literal, comment, fixture-data and record-text substitutions only.

- **`9ec5814`** — the operator's personal name → `username_subject` in batch
  records (13 `.dev-flow/**` files, all closed batches' records plus this
  batch's `increment-006.md`).
- **`ef644cb`** — the personal email local part dropped from two scan-pattern
  lists (2 `.dev-flow/**` files).
- **`3a177c2`** — the GitHub handle and noreply address → `<owner>`-style
  placeholders in 28 tracked files (every file named in §2 group A).

Why this packet exists: the close-gate reverse trace (V59, ruling Q1) charges
every path in the tree's diff against `base_ref` to the §2 tables of the
packets named `increment-NNN.md`. The scrub commits commissioned no increment
and touched no product code; and increments 008/009/010 are named
`increment-008-ddr-fix.md` / `increment-009-gate-fix.md` /
`increment-010-perf.md` — outside the pattern the gate's packet reader parses —
so the files they carry surfaced as V59 blocks at the close gate. This packet
carries those rows: group A records the scrub itself (trace = the directive,
recorded in PLAN.md · Key decisions, 2026-10-11 CLOSE3 row); group B restates,
unchanged, the §2 rows of the unread suffixed packets so the gate can resolve
the paths (no new claim is made — the work, its rulings and its evidence stay
with increments 008/009/010).

Kind note: every group-A row is `doc` because the change is a placeholder
substitution in text, literals or fixture data — there is no behaviour to
trace, and tracing these files to an unrelated US/HLR/LLR would be the false
claim V59's phantom arm exists to refuse; the directive entry is the trace
the operator ruled these rows carry.

---

## 2 · Files modified

### Group A — the personal-reference scrub (`9ec5814` · `ef644cb` · `3a177c2`)

| File | Kind | Traces to | Change |
|---|---|---|---|
| `HANDOFF.md` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: handle/noreply placeholders in the handoff record |
| `handoff-ui-redesign.md` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same substitution in the UI-redesign handoff record |
| `tests/test_app.py` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: `<owner>` placeholder in repo-slug fixture strings and hermetic-test comments — the slugs are opaque data, no assertion's semantics changed |
| `tests/test_hermetic.py` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same substitution in the hermetic-arm record text |
| `prototypes/repo_nav/generate.py` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: `<owner>` placeholder in the demo-data constant |
| `prototypes/repo_nav/prototype.py` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same substitution in the variant demo widgets |
| `prototypes/repo_nav/out/index.html` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: regenerated output of the scrubbed generator — same substitution, no markup change |
| `prototypes/ui_darkside/generate.py` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same substitution in the demo-data constant |
| `prototypes/ui_darkside/out/index.html` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: regenerated output of the scrubbed generator |
| `prototypes/ui_repo/generate.py` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same substitution in the demo-data constant |
| `prototypes/ui_repo/out/index.html` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: regenerated output of the scrubbed generator |
| `.dev-flow/state.json` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: handle/noreply placeholders in the flow state record |
| `.dev-flow/01-requirements.md` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same substitution in the root flow record |
| `.dev-flow/05-postmortem.md` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same substitution in the root flow record |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-015-confirm-security-review.md` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same substitution in the closed batch's record |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-015-confirm.md` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-018-sec-h2-review.md` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-055-en9.md` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same |
| `.dev-flow/2026-08-26-ui-next-batch-02/state-parked.json` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same |
| `.dev-flow/2026-08-26-ui-next-batch-02/state-snapshot-at-close.json` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same |
| `.dev-flow/2026-08-27-repair-batch-02/04-qa-adversarial.md` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same |
| `.dev-flow/2026-10-08-data-safety-batch/state-snapshot-at-close.json` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same |
| `.dev-flow/2026-10-09-canon-batch/state-snapshot-at-close.json` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same |
| `.dev-flow/2026-10-09-hygiene-batch/state-snapshot-at-close.json` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same |
| `.dev-flow/2026-10-09-modular-batch/state-snapshot-at-close.json` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same |
| `.dev-flow/2026-10-10-csv-safety-batch/state-snapshot-at-close.json` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same |
| `.dev-flow/2026-10-10-perf-batch/state-snapshot-at-close.json` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same |
| `.dev-flow/2026-10-11-reqharness-batch/05-postmortem.md` | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | `3a177c2`: same substitution in this batch's P5 post-mortem |
| `9ec5814` — 13 `.dev-flow/**` record files (name → `username_subject`) | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | the first scrub commit: closed batches' records + this batch's `increment-006.md`; every path is under `.dev-flow/`, so the close-gate diff limb does not charge it — recorded here so the directive's full scope sits in one packet |
| `ef644cb` — 2 `.dev-flow/**` record files (email local part dropped) | doc | PLAN.md directive row 2026-10-11 (CLOSE3) | the second scrub commit: two scan-pattern lists in closed batches' records; same `.dev-flow/` exclusion as above |

### Group B — rows restated from the unread suffixed packets (V59 catch-up)

Owning packets `increment-008-ddr-fix.md`, `increment-009-gate-fix.md` and
`increment-010-perf.md` name these files already; the close-gate packet
reader parses only `increment-NNN.md`, so the rows are restated here verbatim
(trace ids unchanged from the owning packets). `mapper/reqharness/records.py`
is NOT restated: its owning row lives in `increment-001.md`, whose file cell
CLOSE3 repaired so the path resolves (and the unit-directed row was added to
`increment-009-gate-fix.md` §2 for the human record).

| File | Kind | Traces to | Change |
|---|---|---|---|
| `tests/test_a3_census.py` | test | LLR-N07.2.2a | the arg-ful call-site pin re-derived and itemised (`82 → 83`) — increment-009 ruling 3; restated from `increment-009-gate-fix.md` §2 |
| `tests/test_app_imports_used.py` | test | LLR-MOD.3.1 | `RolesScreen` recorded as a declared `app.py` re-export (AT-064 allowance row, guard logic untouched) — increment-009 ruling 2; restated from `increment-009-gate-fix.md` §2 |
| `tests/test_darkside_census.py` | test | HLR-S06.1 · LLR-S06.3.4–3.5 | the 14 roles-screen severity/busy sites classified, pin 40 → 54 itemised — increment-009 ruling 4; restated from `increment-009-gate-fix.md` §2 |
| `tests/test_mod_parity.py` | test | LLR-MOD.4.2 | `GOLDEN_SHA256` re-pinned after the RH6a door-count golden regen (AT-065) — increment-009 ruling 5; restated from `increment-009-gate-fix.md` §2 |
| `tests/test_help_scope.py` | test | HLR-RH.8 | the help/key-hint scope census hardened against ambient `NO_COLOR` (RH6a screen work); restated from increment 006's commit record — no suffixed packet names it |
| `tests/test_reqharness_cache_fastpath.py` | test | LLR-RH.5.4 | the parse-cache stat fast-path nodes (warm derive 5.27 s → 0.44 s, LLR-RH.5.4 met); restated from `increment-010-perf.md` §2 |
| `tests/test_reqharness_modgraph.py` | test | HLR-MOD.7 | the AST back-import census + planted function-local negative control (DDR conditions); restated from `increment-008-ddr-fix.md` §2 |
| `tests/test_reqharness_yaml_census.py` | test | LLR-RH.1.1 | the permanent `yaml.load`-ban census follow-ups (exact ASCII time fullmatch arms landed in the registry file; the census file keeps the banned-call guard); restated from increment 001's RHFIX record |

| Count | Value |
|---|---|
| **SOURCE files** | **0** — no product code touched by this increment |
| Test files | 8 restated rows (owned by increments 006/008/009/010) |
| Doc files | 30 — the 28 files of `3a177c2` (each its own row above) + the two summary rows for `9ec5814` / `ef644cb` (their paths are `.dev-flow/`-exempt and too many to itemise twice; both commits' full file lists are in their commit records) |

- Group-A `doc` rows owe no requirement id (V59 ruling D1); their trace is the
  operator directive recorded in PLAN.md · Key decisions (2026-10-11 CLOSE3
  row) — the trace form the operator ruled for a record-only scrub.
- Group-B rows keep the exact `Traces to` ids their owning packets declared;
  every id is declared in a `01-requirements.md` under `.dev-flow/`.

---

## 3 · How to test

Record-only increment — no test is owed (no behaviour changed). The gate is
the validator itself, run from the worktree root:

```bash
python "$HOME/.claude/docs/tools/devflow-validate.py" --brief
```

---

## 4 · Test results

### GREEN — executed now, from the worktree root

The close gate before this packet: **54 blocks**, of which 21 outside the
environment carries (V7/V15/V16): V36 ×1 (`increment-007.md` named no
reviewer) + V59 ×20 (11 scrub-touched files + 8 test files whose owning
packets are suffixed — the full baseline is the `--brief` output of the
CLOSE3 run). After this packet + the `increment-007.md` §4b repair +
`increment-001.md` §2 cell repair + `increment-009-gate-fix.md` §2 row +
the PLAN.md directive row:

```text
0 blocks outside V7/V15/V16
```

(The executed command, the final summary line and the remaining
V7/V15/V16 environment carries are quoted in the CLOSE3 unit report.)

### RED counterfactual — the gate itself is the instrument

With ONLY this packet removed from `03-increments/`, the same command
re-reports the V59 diff-limb blocks for every file named nowhere else
(group B's 8 test files + group A's 11 non-`.dev-flow/` files); with the
packet restored (sha256-verified byte-identical) the blocks clear. A
record-only increment has no product change to revert, so the gate's own
before/after is the executed counterfactual, not a prediction.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | WAIVED-BY-OPERATOR — operator-mandated record-only scrub under the 2026-10-11 directive; no functional surface exists to independently review (string-literal/record placeholder substitutions only) |

---

## 5 · Risks

- Group B restates rows from packets the gate's reader does not parse — a
  future read of increments 008/009/010 must treat THOSE packets as the
  operative record and this packet as the gate-facing mirror; a drift between
  the two would re-surface at the next close gate. Flagged as a dev-flow
  observation (D12-adjacent): the packet-reader pattern and the corpus's
  suffixed packet names disagree.
- The `<owner>` / `username_subject` / `<org>` placeholders must stay opaque
  data: any code that ever parsed them as real slugs would be a regression —
  today nothing does (the guard censuses re-ran green at the gate).
- The `9ec5814` / `ef644cb` summary rows compress 15 file paths into two
  rows; those paths are `.dev-flow/`-exempt at the diff limb, so the
  compression cannot hide an omitted file from the gate.

## 6 · Pending items / spec deviations

- **Packet naming deviation (recorded, not silent):** the CLOSE3 unit brief
  named this packet `increment-011-personal-scrub.md`; it is filed as
  `increment-011.md` because the close-gate packet reader parses only
  `increment-NNN.md` (`_V60_PACKET`) — a suffixed name would leave every
  block in this packet unfixed at re-run. The title carries the scrub name.
- The same pattern gap for `increment-008-ddr-fix.md` / `-009-gate-fix.md` /
  `-010-perf.md` is why group B exists; renaming those packets is the
  orchestrator's call (their increments' gates have already closed), so the
  rows are mirrored here instead.

## 7 · Suggested next task

The orchestrator commits the CLOSE3 record set and re-runs the validator at
the batch close; the remaining V7/V15/V16 carries are environment (flow
version drift) and close with a flow refresh, not with record edits.

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | ≤4 source files | ✓ | 0 source files touched |
| 2 | Tests written in this same increment | ✓ | none owed — record-only, no behaviour changed |
| 3 | Layer 0 written where the criterion applies | ✓ | n/a — no code change |
| 4 | RED counterfactual declared | ✓ | gate before/after + packet-removed re-run, §4 |
| 5 | Security conditions discharged mapped to findings | ✓ | the scrub REMOVES personal references (A-110 direction); no new surface, §1/§5 |
| 6 | `code-reviewer` passed | ⚠ | WAIVED-BY-OPERATOR — §4b |
| 7 | No file from another lane touched | ✓ | one lane; record files only |
| 8 | Frozen interfaces untouched | ✓ | no keymap/seat/`docs/ARCHITECTURE.md` §4 edit |
| 9 | Coverage claims verified on disk | ✓ | §4 quotes the executed validator summary |
| 10 | Residuals stated honestly | ✓ | §5 (mirror drift, placeholder opacity, summary rows) |
| 11 | Evidence files declared | ✓ | §4 (the `--brief` output is the evidence; no transcript owed for a record-only increment) |
| 12 | Independent review names somebody | ✓ | §4b — WAIVED-BY-OPERATOR with its reason |
