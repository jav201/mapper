# P2 review, QA lens, second pass: batch 2026-10-25-relmap-r1-batch

**Mode:** plan (verdict over the amended contract; no result claimed). **Base:** branch `feat/relmap-r1`, HEAD `9b4a8ff`. **Read:** `01-requirements.md` (HLR/LLR amendments, §5.1-§5.4), ledger `.1`-`.16`, last two `decisions_log` entries, `evidence/p2-amendment-probe-2026-10-25.txt`. **Executed:** one Python check (the `_ROW_ID_RE` regex against NBSP and U+202E ids; results quoted in N-1). No test run, nothing changed.

## Verdict: iterate (one more short P1 amendment)

All 16 first-pass findings are verified fixed. The AT bodies are observable and the matrix holds both ways. The second pass found 1 new major that is a factual error in an AT oracle (AT-124 expects a row the canon reader never emits), 1 new major that is an internal contradiction in an AT oracle (AT-119 notes), and 5 minors. Both majors are small text amendments, not design changes.

## First-pass findings

| Id | Status | Evidence |
|---|---|---|
| Q-1 byte-identity vacuous | verified | LLR-RML.1.4 now states the existing suite asserts substrings and `len(msg) <= 160`, not byte identity. It requires `tests/test_prescan_refusal_goldens.py`: 4 refusals × 2 call sites (`load`, `_capped_side_graph` called directly because `git_diff` returns `None`) = 8 exact strings, captured on the base commit before the move. M-RML-6 turns the golden RED while `test_ingestion_limits.py` stays GREEN, so the control is non-vacuous. M-RML-12 covers the `ValueError`-derivation trap. Ledger .1, .15. |
| Q-2 ATs undefined | verified | §5.3 gives 12 AT rows with Given, When, Then, how observed and a negative control. AT-117 is narrowed to the summary line. Caveats are in N-1, N-4 and N-5 (oracle errors and control strength), not a reopening of the finding. |
| Q-3 false-positive gap | verified | `Node.unparsed`; sentence qualifier `(<n> canon rows unparsed under this id)`; LLR-RMA.1.3 rule. Re-derived by hand: `HLR-CAN.1` ← `LLR-CAN.1.1/.1.2` via starts-with; `HLR-REPAIR.1` ← `LLR-REPAIR.1/.2` via the shared-stem branch ("REPAIR" = "REPAIR.1" minus its last segment). The probe file lists 7 gaps with the two qualified and five plain. The figure is now pinned by id, as asked. AT-125 plus M-RMG-4 and M-RMA-5 cover it. |
| Q-4 AT-120 / exit-0 baseline | verified | The raising callable moves to Layer A (TC-RM-02, `run_cli(argv, extra_lines=raiser)`). AT-120 asserts its exit-0 precondition with at least 1 active HLR lacking an LLR, and compares the prefix to a base-commit golden. The mutant for AT-120 is unnamed (N-5). |
| Q-5 AT-122 escaper reach | verified, one defect reopened as N-1 | AT-122 arms are now U+0301 id, U+FE0F id, ESC+U+2028 in a statement, U+0301 descriptor base name, each RED alone under M-RMU-1. LLR-RMU.1.3 states the unsafe-id split correctly. The NBSP claim is wrong (N-1). |
| Q-6 problems unobservable | verified, caveat N-1 | A `structure: notes excluded=<T> (<kind>=<n>) unknown_status=<u> reach_not_computed=<r>` line prints counts only; AT-124 and M-RMU-7 cover it. The reconciliation `nodes + excluded = parsed rows` is undefined for rows the canon reader skips silently (N-1). |
| Q-7 boundary outcomes | verified | Withdrawn-only HLR is not a gap (LLR-RMG.1.2, M-RMG-6, AT-118 fourth arm). Empty canon prints `nodes=0 edges=0 cycles=0` and `gaps: 0 (HIGH=0, MED=0, LOW=0)`. Status: exact `active` only; `Active` and `active (partial)` normalise to `active`; empty and unknown are ineligible and counted (`test_status_words`). Zero-count kinds are omitted everywhere. The first-pass contradiction is gone: grep finds no `US=0` or `prints zero` text left. |
| Q-8 descriptor causes and crashes | verified | The closed set K1-K17 is counted once (K1-K7 read, K8-K10 YAML, K11-K16 schema, K17 path). `profile: [x]`, `{a: b}`, `kind: [1]`, `source: [1]`, empty file, big integer, multi-document, BOM and `RecursionError` are all named arms. Cap−1 is comment-padded valid YAML, and the sparse-file trap is stated. One sub-gap is N-6. |
| Q-9 surface preconditions | verified | LLR-RMU.1.1 defines no-repo and no-registry lines (hook not called) and the root as `report.repo`. AT-126 covers them with M-RMU-4. The fixture helpers are named (`_seed`, `_git_repo`, `_write_canon`), exact reuse deferred to PDR. |
| Q-10 formatter evidence | verified | The pure `format_structure(relmap, gaps, notes, refusals)` is named. `test_line_formats` drives it with a synthetic multi-severity, multi-reach map. §5.2 states those 7 kinds have formatter evidence only. |
| Q-11 determinism | verified, control strength N-3 | LLR-RMU.1.4 defines every order, adds the labelled block line, and AT-128 compares bytes under `PYTHONHASHSEED=0` and `=1`. |
| Q-12 descriptor fan-out | verified | LLR-RML.1.6: at most 8 evaluated, one overflow line, case-sensitive match, link and directory entries refused as K1/K2 under their base name. AT-127 covers 9 files and a directory. |
| Q-13 Node/Edge shape | verified | LLR-RMM.1.1 gives `Node(id, kind, title, status, open, unparsed)` and `Edge(src, dst, type, evidence_missing, in_cycle)` with defaults and the ●◐○ mapping. |
| Q-14 AT-123 | verified | Retired as an AT, now TC-RM-01 (Layer A, M-RMP-4, "gates nothing new"). §5.1 says so and the AT numbering gap is explained. |
| Q-15 two-way matrix | verified | §5.4 forward rows cover all 9 HLR and every LLR group; the reverse list covers AT-117..122 and AT-124..129. I cross-checked each HLR's Acceptance block against the matrix row and found no stale AT reference (the only `AT-123` mention is the retirement note). Layer-A-only HLRs (RMP.2, RMM.2, RMM.3) and their story-level gaps are marked. |
| Q-16 sentence template | verified | The catalogue table (LLR-RMP.1.1) carries a sentence-template column per kind; the 120-character cut applies to `<title>`; `DISPLAY_MAX` applies before escaping. |

## New findings

| Id | Sev | Area | Evidence | Fix |
|---|---|---|---|---|
| N-1 | MAJOR | AT-124 oracle wrong for the NBSP row | AT-124 expects `excluded=3 (duplicate id=1, unsafe id=2)` from "one duplicate id, one id with U+202E, one with NBSP, one with `Done` status". Executed: `_ROW_ID_RE = ^(HLR\|LLR)-\S+$` fullmatches an id ending in U+202E (`True`) but NOT an id containing NBSP (`False`, NBSP is whitespace for `\S`). `parse_canon` skips a non-matching row with a bare `continue`: it is neither a node, nor reported, nor counted. So the run prints `unsafe id=1`, `excluded=2`, and the contract's identity "nodes + excluded = parsed rows" is undefined for the silently skipped row. The first-pass Q-5 fix text (LLR-RMM.1.2/RMU.1.3 and ledger .12) repeats "NBSP ids are excluded upstream as `unsafe id` and counted". | Replace NBSP in AT-124, AT-122's parenthesis and LLR-RMU.1.3 with a character that is `\S` yet not printable (U+200B, category Cf). State what happens to a table row whose first cell fails the id regex (silently ignored by the canon reader; not an R1 gap) and define "parsed rows" as rows the regex accepted. |
| N-2 | MAJOR | AT-119 vs the note table | LLR-RMU.1.2's note row says the note carries "the reported-rows count", i.e. one line. AT-119 and LLR-RMA.1.3 ("every row … verbatim and in order, as a derivation note") expect 7 separate notes naming the rows. The two readings print different stdout, and with the 10-note cap the snapshot already spends 7 (reported) + 1 (unlinked) = 8 of 10, leaving 2 for configured sources and ignored keys. AT-117/119 exact-line assertions cannot be written until one is chosen. | Pick one: (a) one count line plus verbatim rows capped (state how many), or (b) one note per reported row. Align LLR-RMU.1.2, LLR-RMA.1.3, AT-119 and the 10-note cap arithmetic (state the snapshot's note count). |
| N-3 | MINOR | AT-128 negative control may not flip | M-RMU-6 iterates a set of kind names. On the live canon only 2 kinds (HLR, LLR) are present, so two seeds give the same order about half the time and the mutant can survive AT-128. | Run at least 4 seeds (0..3) and make the mutant iterate a set large enough to vary (all 5 kinds plus edge types plus gap kinds), or state the probability and the seed list that provably differ for the chosen set. |
| N-4 | MINOR | AT-121 overclaims "one descriptor per cause K1-K17" | K3 (`file not found`) and K4 (`could not read file`) cannot be produced black-box for a discovered descriptor (it exists when listed; a race is not an AT). K17 needs `us_canon`, K2 a directory, K1 a link that a Windows run may not be allowed to create (the arm reports `blocked`, which is stated and acceptable). | Say AT-121 covers K1, K2, K5-K17 and K3/K4 are Layer A (`test_read_repo_text_*`), or name the seam. |
| N-5 | MINOR | Weak or unnamed negative controls in §5.3 | AT-117's control cites M-RMP-1 (hard-code a kind literal in `gaps.py`), which turns the AST census RED, not AT-117's stdout. AT-120's control is "an exit-code-from-gap mutant" with no M-id. AT-129's 1 MiB `us_canon` may be refused by `confine_reason` (K17) before it is printed as a value, which would make the `…` assertion unreachable. | AT-117: cite M-RMA-1 only (edges 199 not 196) and add a count mutant for node count. Give AT-120 an id (M-RMU-8). For AT-129, state the printed surface that carries the long value (a configured, accepted path of a length `confine_reason` allows, and a long gap-sentence title) and probe `confine_reason` at that length at PDR. |
| N-6 | MINOR | Prescan failure vs K10 | LLR-RML.1.1 maps "every `safe_load` failure" to K10, but `yamlscan.prescan` (`yaml.parse`) runs first and a syntactically invalid descriptor (`a: [`) raises `yaml.YAMLError` there, which LLR-RML.1.4 says "propagates to the callers' net". The descriptor's net is not stated to cover the prescan call. | Say K10 covers `yaml.YAMLError`, `ValueError` and `RecursionError` from the prescan AND `safe_load`; add a `a: [` arm. |
| N-7 | MINOR | Snapshot fixture not on disk yet | `tests/fixtures/relmap/REQUIREMENTS.snapshot.md` does not exist; every exact figure (AT-117, AT-119, AT-125, LLR-RMG.1.2) depends on it. This is correct at P2 (planned), but it is the single point all those ATs share. | Name its creation in Inc-4 (adapter) with the sha256 assertion, and add a test that the file's sha256 equals the ledger value (otherwise a quiet edit changes every oracle). |

## Checks requested

- **AT bodies observable:** yes. Every AT runs `mapper --audit` as a subprocess and asserts stdout lines or bytes and the return code. TC-RM-01/02 are honestly Layer A.
- **Non-vacuous:** AT-120 now asserts its exit-0 baseline; AT-117/118/119/124/125 use non-default fixtures; AT-122 arms target the escaper's real surface (apart from N-1's NBSP). Residual weak points are N-3 and N-5.
- **Each has a negative control:** yes in form (12 of 12 rows name one); AT-120's is unnamed and AT-117's and AT-128's may not flip (N-5, N-3).
- **Matrix both ways:** holds (Q-15 row). Every LLR appears under exactly one HLR; every AT appears forward and in the reverse list.
- **Layer-A-only honesty:** unchanged and stated per story in §5.2 and §5.4.

## Evidence checklist (qa-reviewer, second pass)

- [x] Mode declared: plan.
- [x] Acceptance criteria Given/When/Then: ✓ §5.3.
- [x] Explicit Expected: ✓ (N-1, N-2 are wrong or ambiguous expected values, listed).
- [x] Edge cases include empty, boundary, invalid, error: ✓ Q-7, Q-8 closed.
- [x] Regression checklist and exit criteria: ✓ §5.2.
- [x] No real PII or secrets: ✓.
- [ ] Layer B negative controls all named and able to flip: ⚠ N-3, N-5.
- [x] Bidirectional surface reachability: ✓ outputs (count line, formatter) and inputs (descriptors, canon causes) reachable; K3/K4 Layer A (N-4).
- [x] No unfilled template placeholders in `01-requirements.md`.
