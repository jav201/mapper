# Postmortem — mapper — Batch 2026-10-11-reqharness-batch (P5)

> Phase 5 artifact, full mode. Content owner: `qa-reviewer`. Closes the batch:
> what shipped, what each review caught and where, escapes and lessons, metrics,
> open items, evidence checklist, and the canon-fold preparation list (§fold).

## 0 · Gate record

| Field | Value |
|---|---|
| Gate command | `python <flow bundle>/scripts/devflow-validate.py --brief <project root>` |
| Gate verdict at close | run by the CLOSE2 unit — see §E of the close record; 0 BLOCKs under this batch |
| Gated tree commit | `6b6750e` (batch trunk HEAD at close; the orchestrator re-runs the validator after committing this artifact) |
| Full suite (orchestrator, clean shell, at `6b6750e`) | `3376 passed, 24 deselected, 3 xfailed, 12 warnings in 1674.34s (0:27:54)` — 0 failed |
| Prior full-suite line | `3370 passed … in 1743.24s` at `bac7885` (pre-close1); the +6 nodes are the PERF-RH stat-fast-path arms |

Expected NOTICEs, declared per the flow's bundle-runtime section: `V57`
(record predates this tree once the close commit lands), `V25` (no `origin`
remote), `V30` (a bundle derives the floor of its own file set only). The
three bundle-only skips (`V15`, `V16`, `V17`) are recorded as `not-run` —
this runtime has no canon tree beside the bundle, no checkout table, and no
`settings.json` hooks. Mechanisms unavailable on this runtime (named reviewer
roles, prompts, hooks): named once here; every other artifact points at this
record. Reviews ran as spawned generic sub-agents carrying the flow's
`agents/<role>.md` files, or as cross-model review units recorded per packet;
a gate with no independent reviewer would be a self-review, and the packets
record which independent reviewer produced each verdict.

## 🔑 At a glance

- **Outcome:** PASS-WITH-NOTES → all notes resolved or deferred to backlog; the
  one measurement miss (LLR-RH.5.4) was re-measured MET after the PERF-RH fix.
- **What shipped:** the ReqHarness vertical slice (B-107) — a headless core
  (`mapper/reqharness/`), the roles screen (matrix variant B, B-123), and a
  read-only `mapper --audit` entry, in increments RH1–RH6b plus three repair
  increments (DDR follow-up, gate repair, perf).
- **Top-3 lessons:** (1) worker-environment artefacts (`TERM=dumb`,
  `NO_COLOR`) produced a false "24 pre-existing failures" claim that had to be
  retracted in the record; (2) per-increment test slices missed repo-wide
  guards — the one full-suite gate run caught 8 guard failures the slices never
  saw; (3) a personal path leaked into a committed transcript and was amended
  before any push — the A-110 guard now backstops the whole tree.
- **New control:** `tests/test_no_operator_paths.py` (A-110) — the operator's
  account name appears in no tracked file, and every user-profile path segment
  in tracked files must be a declared placeholder.
- **Open items:** B-124, B-125, B-126 (widened), B-127, plus the stated
  residuals (cache fast-path same-stat rewrite, LOW-2 legal-depth load cost,
  layer-3 rewrite honesty — guard NONE).
- **Metrics:** 9 increments · 40 commits · 3 user stories · 9 HLRs · 36 LLRs ·
  9 acceptance-test ids · 24+ named RED mutations · gate suite 3376 passed /
  0 failed · warm-cache budget 5.27 s → 0.44 s (12×).

## What shipped

Increment map (packets in `03-increments/`, evidence in `evidence/`):

| Incr | Slice | Landed as |
|---|---|---|
| RH1 | HLR-RH.1 — config, typed schema, canonical JSON, email hashing | `ce590a3` (+ code-review follow-up `2c03045`) |
| RH2 | HLR-RH.2/3 — roles chain: genesis, policy events, head binding, verify-by-`prev_hash`, forks, resolve | `b82b575` (+ follow-up `fb4ea82`) |
| RH3 | HLR-RH.7/4 — identity reader + hardened read-only git allowlist | `6b5d6f0` |
| RH4 | HLR-RH.4/5 — immutable content-named review events, pending resolution, content-keyed parse cache, derived states | `0290948` (+ follow-up `f076d3a`) |
| RH5 | HLR-RH.6/7 — baselines (named, commit-bound, dirty flag, five diff classes), release rules, read-only `mapper --audit` | `ba24ed3` (+ follow-ups `6c712e5`, `8561ff9`) |
| RH6a | HLR-RH.8 — roles screen (matrix variant B), home door `R`, status band | `583167a` |
| RH6b | HLR-RH.2/8 — admin `a`/`r` pending resolution on the roles screen | `7cb1b81` (+ follow-up `0d10b7c`) |
| DDRFIX | DDR architect/qa/security conditions — escaping, depth bound, confinement, lock + newline repair, approver ≠ requester | `5492378` |
| Gate fix | 8 repo-wide guard failures fixed at root (audit CLI move, re-export, census pins, parity goldens, `records.py` rename, F2 depth bound) | `bac7885` |
| PERF-RH | LLR-RH.5.4 — parse-cache stat fast path; warm derive 5.27 s → 0.44 s | `6b6750e` |

Full commit list (`git log --oneline fb1d4ce..HEAD`, 40 commits): P0 intake
`0516b04` → P1 requirements/design `ef84d76`, `feeb34d` → P1 iterations and
PDR rulings `8bff52e`, `6bac0af`, `9295124`/`4eb5b58`, `2a2c3e0`, `ee67c21`,
`35a9e28` → RH1–RH6b and their merges/follow-ups `ce590a3` … `0d10b7c` → DDR
amendments `e44105e` → DDRFIX `5492378` → K3 close-out + P4 measurement
`1560066` → gate fix `bac7885` → PERF-RH `6b6750e`. PDR sealed
**approved with conditions** 2026-10-11 (self-approved under the standing
authorization; ux-reviewer stood down, B-123 stands in).

## What each review caught, and at which station

- **P1 round 1 (security BLOCK-UNTIL F1–F3; architect iterate 5H/8M/4L; qa
  iterate 3H/9M/8L):** the two-layer blocker that US-RH-002/003 had no genuine
  black-box AT (AT-080 re-specified; AT-082/083 born here); F1 forged-genesis
  hole later re-opened at RH2's code review and fixed by pinning genesis to
  position 1. Ruled R1–R14.
- **P1 round 2 (architect iterate; qa/security approve-with-conditions):**
  genesis policy-bound from doc 1 (R15), verify-by-`prev_hash` walk (R27
  seed), config_hash required, increment 6 split 6a/6b (R25); deferrals
  B-124..B-126 opened. Ruled R15–R26.
- **P1 round 3 (all three approve-with-conditions, no HIGH):** one ruling R27
  in seven limbs + 3 test arms + 4 mutants; PDR sealed in the same unit.
- **Per-increment code reviews (Claude Sonnet/Opus, spawned reviewers):**
  RH1 REQUEST-CHANGES — `TIME_RE` Unicode `\d`, silent overwrite, bool-as-int,
  yaml.load census, NFC collision (fixed `2c03045`). RH2/RH3 REQUEST-CHANGES —
  F1 forged-seq-2 genesis HIGH, F2 fold leak MED (→ LLR-RH.2.3 amended, LED
  .31), F3 unbound policy MED, F4 cwd-exclusion HIGH, F5 env leak, F6 NUL
  crash, F7 failed-resolution cache (fixed `fb4ea82`). RH4 REQUEST-CHANGES —
  double pending resolution, raw-parse cache poisoning, validator duplication
  (fixed `f076d3a`). RH5 REQUEST-CHANGES — baseline `objects` crash, vacuous
  confine, canon-unreadable hides status; the re-review reopened a HIGH
  baseline-name traversal (fixed `6c712e5`, `8561ff9`). RH6a
  APPROVE-WITH-NITS — prototype drift, width truncation, copy. RH6b
  APPROVE-WITH-NITS — several-pending-on-one-cell refusal, stale authority
  reload (fixed `0d10b7c`).
- **DDR reviews (architect/qa/security conditions):** discharged in
  increment-008; the Opus re-check reopened SEC F2 HIGH (lexical pre-scan
  bypassable → event-stream depth count) plus F1 nits — fixed in the same
  increment.
- **K3 re-check (close-out security nits, commit `1560066`):** LOW-1
  double-prefixed depth refusal, LOW-3 `_visible` widened to Zs/Mn/Me/variation
  selectors, LOW-4 config.yml 64 KB cap — each RED-proven by
  revert→fail→sha256-restore; LOW-2 (~25 s legal-depth 4 MB load cost)
  accepted as a stated residual in PDR §E.
- **The gate full suite (one clean-shell run, C-25):** caught **8 repo-wide
  guard failures** every per-increment slice had missed (audit CLI import
  graph, ALLOWED_UNUSED, A3 census pin, CONFORMING_SEVERITY rows, parity
  goldens, `model.py` name) — fixed in increment-009 at root per 6 rulings.
- **P4 measurement:** LLR-RH.5.4 warm-cache budget MISSED at 5.27 s vs ≤ 0.5 s
  (I/O-bound: read+sha256 of 5 000 files) → the orchestrator ruled the stat
  fast path (LED .36), re-measured **0.4432 s MET** (increment-010,
  `6b6750e`).

## Escapes and lessons

- **Worker-environment artefacts are a real hazard.** A `TERM=dumb` shell
  turned Textual colour probes into 24 spurious failures; increment-009's
  "24 pre-existing failures" claim was **retracted** in a correction appended
  to the packet — the gate line is 3370 passed at `bac7885`, and the gate-fix
  "fixed" claim was retracted with it. `NO_COLOR=1` ambience also leaked into
  an earlier green capture (help-scope hardening, RH6a). Lesson: full-suite
  verdicts are taken only from a clean shell (`env -u NO_COLOR -u TERM`), and
  a supersession inspection pass now checks surviving claims.
- **Per-increment slices miss repo-wide guards.** Eight guard failures
  surfaced only at the single gate run. Lesson kept: increment slices prove
  the increment; the gate run proves the tree; never report a slice as a tree.
- **A personal path leaked into a committed transcript** and was amended
  before any push; the leak class is now backstopped by A-110
  (`tests/test_no_operator_paths.py`), which reads the real account name at
  run time and can never be widened blind. The CLOSE2 unit additionally
  scrubbed the operator's GitHub handle from all current tracked text (44
  occurrences across 27 files, listed separately for a separate commit).
- **Source-file caps are load-bearing.** RH4 tripped the 4-source-file cap
  (5/4) and the gate repair later renamed `model.py` → `records.py` — both
  needed an orchestrator ruling, not a quiet exception.
- **Perf budgets must name their measurement protocol.** The 5.27 s miss was
  I/O-bound, not parse-bound (CSafeLoader was already in); the fix (stat fast
  path) was ruled as a requirements-level change with a stated, test-pinned
  residual (same-stat in-place rewrite defeats it; `--audit` stays cache-off
  and catches it).

## Metrics

| Metric | Value |
|---|---|
| Increments / commits | 9 / 40 (`fb1d4ce..HEAD`) |
| Requirements | 3 US · 9 HLR · 36 LLR · 9 AT ids |
| Review findings closed | P1 r1: 47 (3 blocker/9 high/23 major/12 low) · r2: ruled R15–R26 · r3: no HIGH; per-increment code reviews: 6 REQUEST-CHANGES rounds; DDR: 12 conditions + re-check HIGH; K3: 4 LOWs |
| RED mutations executed | 24+ named arms (M-RG1..5, M-FN1/2, M-PR1, M-BL1..4, M-RL1, M-AU1/2, M-CH6, M-FS1, M-ID3, DDRFIX arms, CLOSE1 LOW arms), each with a transcript and a sha256 restore digest |
| Gate suite | 3376 passed, 24 deselected, 3 xfailed, 0 failed (1674 s, `6b6750e`) |
| Warm-cache derive (LLR-RH.5.4) | 5.27 s → **0.4432 s** median (budget ≤ 0.5 s, 12×) |
| Audit at scale | `--audit` wall 5.61 s cache-off at 5 000 events (by design) |

## Open items (backlog)

- **B-124** — committer-vs-reviewer email warning (`--audit` WARN on reviewer ≠
  committer email, one `git log --name-only` pass; ships with its own hardened
  pass + increment-1 allowlist amendment).
- **B-125** — baseline `reactivated` class (sixth diff class) + review-state
  progression on diff.
- **B-126 (widened)** — fork recovery UI + multi-event excluded-branch core
  recovery (core currently reports `chain broken` per R27e on a multi-event
  excluded branch; screen-side guided resolve flow).
- **B-127** — roles-screen git calls off the UI thread (up to ≈ 30 s mount
  freeze worst case; move off-thread or cache).
- **Stated residuals (not backlog — accepted in-record):** cache fast-path
  same-stat in-place rewrite (test-pinned; `--audit` catches it); LOW-2
  legal-depth 4 MB YAML load cost (~25 s, PDR §E); layer-3 (registry content)
  full-rewrite honesty has no guard — B-122 strong mode + genesis git
  anchoring are the named follow-ups.

## Evidence checklist (qa-reviewer, per the spec)

- Per-increment RED transcripts with sha256 restore digests: ✓
  (`evidence/*-red.transcript`, drivers where a suite arm needed one)
- GREEN slice transcripts incl. CLOSE1 captures: ✓
  (`rh4/rh5/rh6a/rh7-green-close1.transcript`, `close1-green-slice.transcript`)
- P4 timing + re-measurement transcript: ✓ (`evidence/p4-timing.transcript`)
- K3 re-check RED proof: ✓ (`evidence/close1-red.transcript`)
- PDR §E residual record (LOW-2): ✓ (`design/PDR-2026-10-11-reqharness-batch.md`)
- increment-009 correction (retraction) + orchestrator gate lines: ✓ (packet +
  `04-validation.md`)
- DDR unfilled-template caveat: the DDR record file is the sealed template;
  the real DDR conditions live in increment-008 §10 and PDR §E — declared here
  so the record is not misread as missing.
- Committer-identity rulings files (`RH-rulings-r*.md`): held in the
  orchestrator's area, referenced from `02-review.md` — not committed by the
  batch; declared.

## §fold — canon-fold preparation (D)

REQUIREMENTS.md-bound ids this batch adds (the orchestrator runs
`--fold-canon`; this list is the input). Canon-table rows follow the
hygiene-fold shape: `| Id | Statement | Owning batch | Status |` with owner
`2026-10-11-reqharness-batch`, status `active`, statement = record statement
under the fold normaliser + ` (Record id: <id>.)` suffix. Record headings are
already namespaced (`### HLR-RH.1 — …`), so no ALIAS remap is needed — canon
ids = record ids.

- **User stories (§2.6, NOT canon-table rows — narrative source):** US-RH-001,
  US-RH-002, US-RH-003.
- **HLRs (9):** HLR-RH.1, HLR-RH.2, HLR-RH.3, HLR-RH.4, HLR-RH.5, HLR-RH.6,
  HLR-RH.7, HLR-RH.8, HLR-RH.9.
- **LLRs (36):** LLR-RH.1.1–1.4; LLR-RH.2.1–2.5; LLR-RH.3.1–3.5;
  LLR-RH.4.1–4.6; LLR-RH.5.1–5.4; LLR-RH.6.1–6.2; LLR-RH.7.1–7.3;
  LLR-RH.8.1–8.6; LLR-RH.9.1.
- **Acceptance tests (§5, NOT canon-table rows — they map to suite nodes):**
  AT-077a, AT-077b, AT-077c, AT-078, AT-079, AT-080, AT-081, AT-082, AT-083.

`tests/test_requirements_canon.py` expectations checked: (a) canon ids unique —
no `HLR-RH.*`/`LLR-RH.*` collides with the existing 134+ rows (the pinned
HYG alias map is untouched); (b) table row count only grows, the ≥134 pin is
unaffected; (c) the hygiene fold pin reads only the hygiene record, so this
fold changes nothing it asserts; (d) statements must match under the pinned
four-rule normaliser + the record-id suffix — the fold must take each record's
`- **Statement:**` line verbatim; (e) one canon row per id, owner and status
exact. If the fold instead assigns plain sequential canon ids, an ALIAS block
like the hygiene one must be added to the canon test in the SAME commit as
the fold.
