# Review — mapper — Batch 2026-10-25-relmap-r1-batch

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`).
> Phase 2 artifact. Reviewers (in parallel): `architect` ∥ `qa-reviewer` ∥ `security-reviewer` by trigger family C (always in `full`).

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/guides/review-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

**BLUF:** all three independent reviews return `iterate-to-refine`: 1 blocker (Q-1, byte-identity of the moved prescan pinned by nothing) and 22 majors, every one a requirement defect, plus 16 minors. The author amended the P1 contract in the same unit under the orchestrator's rulings R1-R16 (16 ledger entries `LED-2026-10-25-relmap-r1-batch.1` to `LED-2026-10-25-relmap-r1-batch.16`); the reviewers re-check each disposition at the second P2 pass. Nothing was relitigated: OQ-R1-1 to OQ-R1-8 stand as ruled.

## ✅ Verdict (read first)

- **Gate:** `iterate-to-refine` → Phase 1 (1 blocker — Q-1; requirement-defect majors throughout). Recorded with `devflow-init.py --iterate-to P1`; the amendments are already applied, so the second P2 pass reviews the amended contract.
- **Out-of-scope findings:** `1` named and routed — A-7's third prescan copy in `reqharness/config.py` → BACKLOG B-144 (owner: a later batch); B-143 / OQ-R1-4 (MAP-TYPES `binds` prose) taken as ruled.

- **Findings:** `1` blocker · `22` major · `16` minor (rows as each reviewer recorded them; A-1 and Q-1 are the same defect, kept at each reviewer's severity)
- **shall/should check:** ✓ clean (QA read: no `should` inside an HLR/LLR statement; the amended statements use `shall` only)
- **Two-layer (blockers):** ✗ at first pass — AT bodies undefined (Q-2), AT-120's raising arm and AT-123 not black-box (A-6, Q-4, Q-14); amended: bodies in §5.3, TC-RM-01/02 at Layer A, matrix in §5.4 — re-check owed
- **Census (change-first):** done — best-effort + gate-confirmed (reservations: the new osopen importers `relmap/model.py`, `relmap/descriptor.py`, `yamlscan.py` and the dropped `store.py` `MAX_DEPTH` must be confirmed by `tests/test_arch_osopen_callers.py` at Inc-1 and Inc-3; the A3 pin `:329` must not move)
- **Security:** ⚠ `8` findings (F1-F6 major, F7-F8 minor); all dispositioned in the amended contract; none open
- **Evidence checklists (architect / qa / security):** ✗ partial at first pass — architect: two-layer partial (A-6); qa: acceptance Given/When/Then, edge-case outcomes, Layer B and surface-reachability open (Q-2, Q-4, Q-6 to Q-9, Q-14); security: complete (`planned` states). Each re-checked at the second pass.

**Reviewers (this pass):**
- `architect — Claude Sonnet subagent executing agents/architect.md · iterate-to-refine` (A-1 to A-15)
- `qa-reviewer — Claude Sonnet subagent executing agents/qa-reviewer.md · iterate-to-refine` (Q-1 to Q-16)
- `security-reviewer — Claude Sonnet subagent executing agents/security-reviewer.md · iterate-to-refine` (F1 to F8; C6 fired)

**Second pass:** security approve, architect approve, qa iterate (2 majors, 5 minors; 13 new findings in all); all dispositioned in the Detail below, amendments `LED-2026-10-25-relmap-r1-batch.17` to `LED-2026-10-25-relmap-r1-batch.28`; QA re-check of N-1 and N-2 owed before the P2 decision is recorded.

**Third pass and P2 closure (2026-10-25):** `qa-reviewer` re-checked the second-pass dispositions (`evidence/p2-qa-pass3-and-pdr-qa.md`): N-1, N-2, N-4, N-5, N-6 verified; N-7 verified with a nit (X-3); N-3 reopened (minor); one new MAJOR, X-1 (AT-122 arm 3 could not reach the escaper with U+2028). Verdict `iterate (one small amendment)`, not a full third review. The orchestrator closed P2 on the dispositions below WITHOUT a fourth pass, because every remaining item was wording-level or a test-oracle correction (no requirement was added or removed). Amendments `LED-2026-10-25-relmap-r1-batch.29` (X-1), `.30` (N-3), `.31` (N-7); the same unit applied the PDR conditions (`.32`-`.43`, see the PDR record §A). The P2 decision itself is recorded by the orchestrator in `state.json`.

> If gate = `approve` and every line is ✓, the Detail below is reference. Any blocker/⚠ → read the matching part.

---

## Detail (reference)

### Findings
**Author dispositions (2026-10-25)** — applied under the orchestrator's rulings R1-R16 answering the `iterate-to-refine` gate (amendments `LED-2026-10-25-relmap-r1-batch.1` to `LED-2026-10-25-relmap-r1-batch.16`); the reviewers re-check each at the second P2 pass. `fixed (author)` = the amended clause is in `01-requirements.md`; the reviewers' own texts are in `evidence/p2-architect.md`, `p2-qa.md`, `p2-security.md` and are not edited. Contract size after amendment: 92,888 characters against the 54,000-character budget (`V26` NOTICE, see PLAN §Gate notices).

| ID | Reviewer | Severity | Area / Req | What | Recommendation | Status |
|----|----------|----------|------------|------|----------------|--------|
| A-1 | architect | major | LLR-RML.1.4 | Byte-identity of the moved prescan is claimed to be asserted by `tests/test_ingestion_limits.py`; it asserts substrings only and the `_capped_side_graph` site has no message assertion. Same defect as Q-1 (blocker). | Golden of the exact strings on the base before the move. | fixed (author) — R1: LLR-RML.1.4 rewritten, golden of 4 x 2 strings, M-RML-6 (LED-2026-10-25-relmap-r1-batch.1) · second-pass re-check owed |
| A-2 | architect | major | HLR-RMP.1 / LLR-RMP.1.2 | Catalogue is code in `gaps.py` yet no kind literal may appear there: a contradiction. | Catalogue as data in `profile.py`; detectors generic. | fixed (author) — R2: catalogue table in LLR-RMP.1.1, LLR-RMG.1.1 generic, census extended (LED-2026-10-25-relmap-r1-batch.2) · second-pass re-check owed |
| A-3 | architect | major | HLR-RMG.1 / live figure | Two of the 7 live gaps (`HLR-CAN.1`, `HLR-REPAIR.1`) are artefacts of the adapter's own unparsed/unlinked rows. | Qualify, do not suppress; restate the live expectation; add a fixture arm. | fixed (author) — R3: `Node.unparsed`, qualified sentence, 7 gaps of which 2 qualified, AT-125 (LED-2026-10-25-relmap-r1-batch.3) · second-pass re-check owed |
| A-4 | architect | major | LLR-RMA.1.1/.1.2/.1.3, RMU.1.2, HLR-RMA.1 | Absolute counts of a living file pinned as test oracles. | Frozen snapshot for exact figures; invariants for the live file. | fixed (author) — R4: snapshot fixture and live-invariant tests (LED-2026-10-25-relmap-r1-batch.4) · second-pass re-check owed |
| A-5 | architect | major | LLR-RML.1.1/.1.2 | Discovered descriptors read without confinement (links, FIFOs, devices). | Link and regular-file check before any open; name the osopen names. | fixed (author) — R5: LLR-RML.1.5 `read_repo_text`, LLR-RML.1.6 discovery (LED-2026-10-25-relmap-r1-batch.5) · second-pass re-check owed |
| A-6 | architect | major | AT-120 / AT-123 | AT-120's raising-callable arm and AT-123 are not black-box through the shipped surface. | Move to Layer A; make AT-120 a reachable fault. | fixed (author) — R11: TC-RM-01, TC-RM-02, AT-120 exit-0 baseline (LED-2026-10-25-relmap-r1-batch.11) · second-pass re-check owed |
| A-7 | architect | minor | ARCHITECTURE R-017 | `reqharness/config.py` already holds a third prescan copy; R-017 omits the alternative. | Record it, reject it with reasons, log the drift risk. | fixed (author) — R14: R-017 text amended, BACKLOG B-144 (LED-2026-10-25-relmap-r1-batch.14) · second-pass re-check owed |
| A-8 | architect | minor | LLR-RML.1.4 | Owner of the anchor truncation, the error base class and the `MAX_DEPTH` importer unstated. | Specify in the LLR. | fixed (author) — R15: `yamlscan` owns the display, `YamlLimitError(Exception)`, MAX_DEPTH importer named (LED-2026-10-25-relmap-r1-batch.15) · second-pass re-check owed |
| A-9 | architect | minor | Premise 9 / PLAN | `test_a3_census.py:300-312` is mis-described; the real pin is `:329`. | Correct the wording, state the two hazards. | fixed (author) — R16: premise 9, LLR-RMU.1.1, ARCHITECTURE §6 corrected (LED-2026-10-25-relmap-r1-batch.16) · second-pass re-check owed |
| A-10 | architect | minor | ARCHITECTURE osopen rows / allow-list | The osopen cells and the exact-equality allow-list omit the new importers; `relmap/model.py` imports in Inc-1. | Amend both cells; per-increment entries. | fixed (author) — R16: LLR-RMP.2.1, ARCHITECTURE osopen cells amended now (LED-2026-10-25-relmap-r1-batch.16) · second-pass re-check owed |
| A-11 | architect | minor | LLR-RMM.1.1 / premise 3 | "CI owes the real run" but there is no CI; `feature_version` does not catch 3.11+ names. | Declare `not-run`; banned-name census. | fixed (author) — R16: LLR-RMM.1.1, premise 3, §6.3 (LED-2026-10-25-relmap-r1-batch.16) · second-pass re-check owed |
| A-12 | architect | minor | LLR-RMM.1.2 / RMU.1.2 | (a) Problems have no output line; (b) `unavailable (canon: <text>)` can embed an absolute path. | (a) count line; (b) fixed cause words. | fixed (author) — R9 and R6: count line, closed cause set (LED-2026-10-25-relmap-r1-batch.9, LED-2026-10-25-relmap-r1-batch.6) · second-pass re-check owed |
| A-13 | architect | minor | LLR-RMU.1.1 / HLR-RMP.2 | Hook semantics per Report kind, multi-descriptor output, and HLR-RMP.2 wording. | State per kind and the block rule; reword RMP.2. | fixed (author) — R13, R16: fixed no-repo/no-registry lines, one labelled block per descriptor, RMP.2 reworded (LED-2026-10-25-relmap-r1-batch.13, LED-2026-10-25-relmap-r1-batch.16) · second-pass re-check owed |
| A-14 | architect | minor | LLR-RML.1.1, HLR-RML.1, RMM.1, RMG.1, RMM.2.2 | Cap-1 fixture, refusal-kind counts, undefined Node/Edge fields, withdrawn-only HLR, reach recursion. | Specify each. | fixed (author) — R13, R8: closed list of 17, fields, comment-padded fixture, iterative reach (LED-2026-10-25-relmap-r1-batch.13, LED-2026-10-25-relmap-r1-batch.8) · second-pass re-check owed |
| A-15 | architect | minor | PLAN increment plan | Whether `__init__.py` re-exports decides the per-increment source count. | State it; recount. | fixed (author) — R16: `__init__.py` re-exports nothing; every increment still <= 4 (LED-2026-10-25-relmap-r1-batch.16) · second-pass re-check owed |
| Q-1 | qa-reviewer | blocker | LLR-RML.1.4 | Byte-identity limb is vacuous (substring assertions; a reworded refusal stays green). | Equality golden captured on the base, both call sites. | fixed (author) — R1: same clause as A-1 (LED-2026-10-25-relmap-r1-batch.1) · second-pass re-check owed |
| Q-2 | qa-reviewer | major | AT-117..AT-123 | ATs exist only as ids; AT-117 shared by four HLRs. | Full bodies; one AT per claim. | fixed (author) — R10: §5.3 table (12 ATs incl. AT-124..AT-129), §5.4 matrix (LED-2026-10-25-relmap-r1-batch.10) · second-pass re-check owed |
| Q-3 | qa-reviewer | major | HLR-RMG.1 live figure | The gap oracle pins a false positive (`HLR-CAN.1`). | Qualify or exclude; state the live figure by id. | fixed (author) — R3: qualified, ids named in LLR-RMG.1.2 (LED-2026-10-25-relmap-r1-batch.3) · second-pass re-check owed |
| Q-4 | qa-reviewer | major | AT-120 / M-RMU-2 | No shipped input makes the hook raise; exit-code arm vacuous if the baseline exits 1. | Layer A for the raiser; exit-0 fixture. | fixed (author) — R11 (LED-2026-10-25-relmap-r1-batch.11) · second-pass re-check owed |
| Q-5 | qa-reviewer | major | AT-122 | Hostile ids named in the contract never reach the escaper (`isprintable()` is false for them). | Retarget the arms to the escaper's real surface. | fixed (author) — R12: four arms by character class; excluded ids counted (LED-2026-10-25-relmap-r1-batch.12) · second-pass re-check owed |
| Q-6 | qa-reviewer | major | LLR-RMM.1.2 / RMU.1.2 | Problems are never observable on the shipped surface. | Count line or declare Layer A. | fixed (author) — R9: `structure: notes` line, AT-124 (LED-2026-10-25-relmap-r1-batch.9) · second-pass re-check owed |
| Q-7 | qa-reviewer | major | HLR-RMG.1, RMA.1, RMP.1 boundaries | Boundary cases without an expected outcome; zero-count contradiction. | Truth-table rows; one zero-count rule. | fixed (author) — R13: outcomes defined; zero-count kinds omitted, stated once in LLR-RMU.1.2 (LED-2026-10-25-relmap-r1-batch.13) · second-pass re-check owed |
| Q-8 | qa-reviewer | major | HLR-RML.1 / LLR-RML.1.1/.1.2 | Refusal kinds counted inconsistently; crash paths (`profile: [x]`, big int, multi-doc) untested. | Closed numbered list; add arms; catch ladder. | fixed (author) — R13, R6: K1-K17, arms in LLR-RML.1.1/.1.2 (LED-2026-10-25-relmap-r1-batch.13, LED-2026-10-25-relmap-r1-batch.6) · second-pass re-check owed |
| Q-9 | qa-reviewer | major | LLR-RMU.1.1 / AT fixtures | `--audit` preconditions undefined (no repo, no registry, which root). | Truth table per report kind; root; fixture builder. | fixed (author) — R13: LLR-RMU.1.1, AT-126, fixtures named (LED-2026-10-25-relmap-r1-batch.13) · second-pass re-check owed |
| Q-10 | qa-reviewer | major | LLR-RMU.1.2 formatter | The HIGH/LOW/reach renderings of the 7 unsourceable kinds are never exercised. | A pure formatter tested synthetically. | fixed (author) — Author call beyond the rulings: `format_structure` named in LLR-RMU.1.2, formatter evidence stated in §5.2 (LED-2026-10-25-relmap-r1-batch.7) · second-pass re-check owed |
| Q-11 | qa-reviewer | major | LLR-RMU.1.4 (new) | Output determinism not required or tested. | Determinism clause and two-seed AT. | fixed (author) — R13: LLR-RMU.1.4, AT-128 (LED-2026-10-25-relmap-r1-batch.13) · second-pass re-check owed |
| Q-12 | qa-reviewer | minor | LLR-RML.1.6 | Unbounded descriptor count; non-regular files. | Cap at 8; refuse non-regular. | fixed (author) — R5: LLR-RML.1.6, AT-127 (LED-2026-10-25-relmap-r1-batch.5) · second-pass re-check owed |
| Q-13 | qa-reviewer | minor | LLR-RMM.1.1 | Node/edge fields and defaults unspecified. | Field list with defaults. | fixed (author) — R13: LLR-RMM.1.1 (LED-2026-10-25-relmap-r1-batch.13) · second-pass re-check owed |
| Q-14 | qa-reviewer | minor | AT-123 | Not black-box; its negative control cannot flip it. | Layer A, honest control. | fixed (author) — R11: TC-RM-01, M-RMP-4 (LED-2026-10-25-relmap-r1-batch.11) · second-pass re-check owed |
| Q-15 | qa-reviewer | minor | §5 | Reverse traceability cannot be checked; two Layer-A-only HLRs unmarked. | Two-way matrix. | fixed (author) — R10: §5.4 (LED-2026-10-25-relmap-r1-batch.10) · second-pass re-check owed |
| Q-16 | qa-reviewer | minor | LLR-RMG.1.1 | Gap sentence not pinned. | Template per kind. | fixed (author) — R7: sentence column in LLR-RMP.1.1 (LED-2026-10-25-relmap-r1-batch.7) · second-pass re-check owed |
| F1 | security-reviewer | major | LLR-RMA.1.1 / §6.3(a) | The canon read is not a capped read (`load_canon` reads first, no link check). | Link check plus capped read for the canon. | fixed (author) — R5: adapter reads through `read_repo_text` (LED-2026-10-25-relmap-r1-batch.5) · second-pass re-check owed |
| F2 | security-reviewer | major | LLR-RMU.1.2 canon line | `unavailable (canon: <text>)` can print a path. | Fixed cause words. | fixed (author) — R6: K1-K7 only (LED-2026-10-25-relmap-r1-batch.6) · second-pass re-check owed |
| F3 | security-reviewer | major | LLR-RML.1.2 discovery | Links, special files and descriptor count unspecified; canon derived per block. | lstat, cap 8, derive once. | fixed (author) — R5: LLR-RML.1.5/.1.6 (LED-2026-10-25-relmap-r1-batch.5) · second-pass re-check owed |
| F4 | security-reviewer | major | LLR-RMU.1.2/.1.3 | Repository-derived values escaped but not length-bounded. | Cut to N before escaping; cap notes. | fixed (author) — R7: 120 characters, ellipsis marker, 10 note lines (LED-2026-10-25-relmap-r1-batch.7) · second-pass re-check owed |
| F5 | security-reviewer | major | LLR-RML.1.1 | YAML parse-failure text must be a constant. | `not valid YAML`; catch ConstructorError. | fixed (author) — R6: K10 (LED-2026-10-25-relmap-r1-batch.6) · second-pass re-check owed |
| F6 | security-reviewer | major | LLR-RMM.2.2 / RMG.1.3 | No work bound on reach at the caps. | Iterative, memoised, printed gaps only, cap-size arm. | fixed (author) — R8: iterative reach, visit bound 2,000,000, arms (LED-2026-10-25-relmap-r1-batch.8) · second-pass re-check owed |
| F7 | security-reviewer | minor | LLR-RMM.1.2 | Build problems never surfaced. | Count-only line. | fixed (author) — R9 (LED-2026-10-25-relmap-r1-batch.9) · second-pass re-check owed |
| F8 | security-reviewer | minor | LLR-RML.1.3 | Confinement must run before any filesystem call. | Keep the zero-stat UNC arm. | fixed (author) — R6: LLR-RML.1.3 zero-stat arm (LED-2026-10-25-relmap-r1-batch.6) · second-pass re-check owed |

**A worked example — text to read, never rows of your record.** It sits in a fence so that nothing has to be deleted: a row copied out of it would claim a finding nobody raised. Write your own rows in the table above.

```text
| *(example)* F1 | architect | blocker / major / minor | | | | open / fixed |
```

### Second pass (2026-10-25) — over the amended contract, HEAD `9b4a8ff`

Verdicts: `security-reviewer` approve (`evidence/p2-security-pass2.md`, N1-N3 LOW), `architect` approve (`evidence/p2-architect-pass2.md`, N-1 to N-3 minor), `qa-reviewer` iterate (`evidence/p2-qa-pass2.md`, N-1 and N-2 major, N-3 to N-7 minor). All 39 first-pass findings were verified fixed by the three reviewers. The 13 new findings are dispositioned below (amendments `LED-2026-10-25-relmap-r1-batch.17` to `LED-2026-10-25-relmap-r1-batch.28`, the reviewers' texts untouched); the coordinator records the P2 decision after QA re-checks N-1 and N-2.

| ID | Reviewer | Severity | Area / Req | What | Status |
|----|----------|----------|------------|------|--------|
| qa N-1 | qa-reviewer | major | AT-124 / LLR-RMM.1.2 / RMU.1.3 | NBSP ids fail `_ROW_ID_RE`, so the contract's `excluded=3` figure and `nodes + excluded = parsed rows` were wrong. | fixed (author) — U+200B replaces NBSP; "parsed rows" defined; figures restated (LED-2026-10-25-relmap-r1-batch.17) · re-check owed (QA: N-1, N-2) |
| qa N-2 | qa-reviewer | major | AT-119 / LLR-RMU.1.2 / RMA.1.3 | The note table said one count line; AT-119 and RMA.1.3 expected one note per reported row. | fixed (author) — One id-only note per reported row, cap arithmetic 8 of 10, overflow rule (LED-2026-10-25-relmap-r1-batch.18) · re-check owed (QA: N-1, N-2) |
| qa N-3 | qa-reviewer | minor | AT-128 / M-RMU-6 | Two kinds and two seeds coincide half the time. | fixed (author) — Seeds 0-3; mutant over 17 names (LED-2026-10-25-relmap-r1-batch.19) · re-check owed (QA: N-1, N-2) |
| qa N-4 | qa-reviewer | minor | AT-121 | K3/K4 cannot be produced black-box. | fixed (author) — AT-121 covers K1, K2, K5-K17; K3/K4 Layer A (LED-2026-10-25-relmap-r1-batch.20) · re-check owed (QA: N-1, N-2) |
| qa N-5 | qa-reviewer | minor | AT-117 / AT-120 / AT-129 | Controls weak or unnamed; a 1 MiB `us_canon` is refused before printing. | fixed (author) — M-RMA-1/-6, M-RMU-8, four accepted long-value surfaces; probe: 255 ok, 300 refused (LED-2026-10-25-relmap-r1-batch.20) · re-check owed (QA: N-1, N-2) |
| qa N-6 | qa-reviewer | minor | LLR-RML.1.1 | Prescan `YAMLError` not covered by K10. | fixed (author) — K10 covers prescan and safe_load; `a: [` arm (LED-2026-10-25-relmap-r1-batch.21) · re-check owed (QA: N-1, N-2) |
| qa N-7 | qa-reviewer | minor | LLR-RMA.1.1 | Snapshot fixture not on disk; single shared point. | fixed (author) — Created in Inc-4 with `test_snapshot_sha256` (LED-2026-10-25-relmap-r1-batch.22) · re-check owed (QA: N-1, N-2) |
| arch N-1 | architect | minor | LLR-RMG.1.1/.1.2, RMA.1.3 | "unparsed" is false for the parsed-but-unlinked REPAIR rows; report-line text is a silent dependency. | fixed (author) — Qualifier reworded; tripwire test (LED-2026-10-25-relmap-r1-batch.23) · re-check owed (QA: N-1, N-2) |
| arch N-2 | architect | minor | LLR-RMA.1.1 / ARCHITECTURE | The relmap canon reader is stricter than `load_canon` on links. | fixed (author) — Recorded as deliberate in the LLR and the `relmap` row (LED-2026-10-25-relmap-r1-batch.24) · re-check owed (QA: N-1, N-2) |
| arch N-3 | architect | minor | LLR-RMM.1.1 | Bare `walk` in the banned-name census would flag `os.walk`. | fixed (author) — Qualified names, `os.walk` allowed (LED-2026-10-25-relmap-r1-batch.25) · re-check owed (QA: N-1, N-2) |
| sec N1 | security-reviewer | minor (LOW) | LLR-RML.1.5 | lstat-then-open race. | fixed (author) — `os.fstat` identity compared with the lstat result; residual stated (LED-2026-10-25-relmap-r1-batch.26) · re-check owed (QA: N-1, N-2) |
| sec N2 | security-reviewer | minor (LOW) | LLR-RMU.1.2 | Resolved path could print the absolute repository path. | fixed (author) — Configured string printed; `~/x` is K17 (probed) (LED-2026-10-25-relmap-r1-batch.27) · re-check owed (QA: N-1, N-2) |
| sec N3 | security-reviewer | minor (LOW) | LLR-RMM.2.2 / RMG.1.3 | Memo as per-node sets is O(n squared). | fixed (author) — Memo stores counts; test asserts ints (LED-2026-10-25-relmap-r1-batch.28) · re-check owed (QA: N-1, N-2) |

### Third pass (2026-10-25) — QA re-check, dispositions and closure

Verdict (`evidence/p2-qa-pass3-and-pdr-qa.md`): `qa-reviewer` iterate (one small amendment); `security-reviewer` and `architect` stood at approve from the second pass. Dispositions (reviewers' texts untouched):

| ID | Reviewer | Severity | Area / Req | What | Status |
|----|----------|----------|------------|------|--------|
| qa X-1 | qa-reviewer | major | AT-122 arm 3 / LLR-RMM.1.2 / RMU.1.3 | `parse_canon` splits lines at U+2028, so a statement with U+2028 never becomes a title and the U+2028 half of the arm passes whatever the escaper does. | fixed (author) — ESC + U+202E in the statement; U+2028 carried by a descriptor ignored key NAMED `"\u2028verdict: ready"` plus a Layer A `run_cli`/`format_structure` arm; LLR-RMM.1.2 boundary reworded (a U+2028 canon id is a reported row; as a builder input it is `unsafe id`) (LED-2026-10-25-relmap-r1-batch.29) · closed by the orchestrator |
| qa N-3 | qa-reviewer | minor | AT-128 / M-RMU-6 | Reopened: two visible orderings over four seeds coincide with probability 12.5%, so the mutant survives one run in eight. | fixed (author) — two pre-picked seeds (0 and 2) proven to differ by a recorded probe, re-proved against the real mutant at Inc-5 (LED-2026-10-25-relmap-r1-batch.30; `evidence/p2-closure-probe-2026-10-25.txt`) · closed by the orchestrator |
| qa N-7 / X-3 | qa-reviewer | nit | LLR-RML.1.1, LLR-RMA.1.1 | M-RML-15 and M-RMA-7 appear only in the ledger and the proposal. | fixed (author) — named in the LLR negative-control lines (LED-2026-10-25-relmap-r1-batch.31) · closed by the orchestrator |

N-1, N-2, N-4, N-5 and N-6 were verified fixed by QA; the other second-pass rows above (`re-check owed`) are closed by the same record. **Closure:** the orchestrator closed P2 on these dispositions without a fourth pass; the remaining items were wording-level.

### shall / should check
> Any modal `should` / `debería` inside an HLR/LLR statement is a writing error → blocker.

✓ clean at first pass (QA: "`shall` is used consistently in HLR/LLR statements; no `should` found in a requirement statement"). The amended and new statements (LLR-RML.1.5, .1.6, RMU.1.4 and the rewritten ones) use `shall` only.

### Two-layer acceptance review (blockers)
> (a) every story has a black-box `AT`; (b) every output-producing requirement names its observable deliverable + observation method; (c) BOTH traceability chains complete (behavioral US→AT→outcome + functional US→HLR→LLR→TC); (d) each `AT` is genuinely black-box — drives the surface, asserts the outcome, references NO internal symbol.

| Story / Req | (a) AT present | (b) deliverable+method named | (c) both chains | (d) black-box pure | Status |
|-------------|----------------|------------------------------|-----------------|--------------------|--------|
| US-RM-001 | yes (AT-117, AT-119, AT-124) | yes | yes (matrix §5.4) | yes after R11 (TC-RM-01 moved to Layer A) | ✓ amended — re-check owed |
| US-RM-002 | yes (AT-118, AT-125; 7 of 8 kinds Layer A, declared OQ-R1-2) | yes | yes | yes | ✓ amended — re-check owed |
| US-RM-003 | yes (AT-120, AT-122, AT-126, AT-128, AT-129) | yes | yes | yes after R11 (TC-RM-02 at Layer A) | ✓ amended — re-check owed |
| US-RM-004 | yes (AT-121, AT-127) | yes | yes | yes | ✓ amended — re-check owed |

### Supersession census (change-first)
> Planned new/moved/edited files checked against EVERY guard family (behavioral-placeholder · structural/placement · AST-composition · frozen-module). State reservations; the increment gate is the completeness guarantee, not this census.

Best-effort + gate-confirmed, not complete. Planned files: new `mapper/relmap/{__init__,profile,model,gaps,descriptor,adapter,audit}.py` and `mapper/yamlscan.py`; edited `mapper/store.py`, `mapper/reqharness/audit.py`, `mapper/app.py`; new tests and the fixture `tests/fixtures/relmap/REQUIREMENTS.snapshot.md`. Families run by the reviewers: structural/placement (`test_repair_map_truth`, `test_mod_*`: §2 row paths written per increment), AST-composition (`test_arch_osopen_callers` exact equality; per-increment entries now named in LLR-RMP.2.1), frozen-module (`tests/test_ingestion_limits.py` unchanged, plus the new base-captured golden), reverse census by symbol (`run_cli`: one caller, `app.py:352`; `_prescan_sidecar`: two call sites `store.py:769` and `:820`; no test drops a root-level `*.relmap.yml`). Reservations the I-gates must confirm: osopen allow-list at Inc-1 and Inc-3; the A3 `.render(` pin `tests/test_a3_census.py:329` (== 86) unmoved and new files staged before a targeted run; the golden GREEN on the base before the move.

### Security review summary
`security-reviewer` (C6 fired), verdict `iterate-to-refine`, no BLOCKER: F1 canon read not capped (`load_canon` reads first, follows links), F2 a canon path in an `unavailable` line, F3 descriptor discovery unbounded and unconfined, F4 values not length-bounded, F5 YAML error text, F6 reach work bound, F7 build problems silent, F8 confine-before-stat. All eight dispositioned by R5, R6, R7, R8 and R9 in the amended contract (closed cause set K1-K17, link check plus capped reader for every file, 8-descriptor cap, 120-character cut, iterative bounded reach). A clean verdict needs the amendments verified at the second pass and each mitigation at its increment gate. Evidence: `evidence/p2-security.md`.

### Evidence checklists (full) — architect · qa-reviewer · security-reviewer
> Attach each reviewer's completed evidence checklist (items in their agent files), ✓/✗ + one-line evidence.

The three checklists are attached in `evidence/p2-architect.md` (§Evidence checklist), `evidence/p2-qa.md` (§Evidence checklist) and `evidence/p2-security.md` (§Verdict and §Checked and clean). First-pass state: architect ✓ except two-layer requirements (✗ partial, A-6); qa-reviewer ✓ for exit criteria, regression checklist, no PII, mode and `planned` results, ✗/⚠ for AT Given/When/Then (Q-2), edge-case outcomes (Q-7, Q-8), Layer B (Q-4, Q-9, Q-14) and surface-reachability (Q-6, Q-10); security ✓ (every finding `planned`, nothing executed). The second pass re-checks the ✗/⚠ items against the amended contract.
