# Review — mapper — Batch 2026-10-25-relmap-r2-batch

> Phase 2 artifact. Independent cross-review of the approved `01-requirements.md` +
> `01b-acceptance-design.md` (P1, 2026-10-25). Four reviewer lenses in parallel —
> `architect` ∥ `qa-reviewer` ∥ `security-reviewer` (triggers C6, C8 fired) ∥ `ux-reviewer`
> (trigger D1 fired). Reviewer evidence: `evidence/p2-architect.md`,
> `evidence/p2-qa-reviewer.md`, `evidence/p2-security-reviewer.md`, `evidence/p2-ux-reviewer.md`.
> The orchestrator's P2 ruling (by-kind toggle ships; hook bound 240 cut after escaping;
> glyph table; the two "assumed — verify in Phase 2" seams are P2 review targets) is
> applied as given, not relitigated.

## ✅ Verdict (read first)

- **Gate:** `iterate-to-refine` → Phase 1 (no blockers; **7 requirement/plan-defect majors** —
  the contract's stated census (26 HLR / 52 LLR) does not match the artifact (20 / 51); the
  two seams the orchestrator designated as P2 review targets remain deferred; the contract
  still presents the by-kind toggle and the hook bound as open PDR questions contrary to the
  standing rulings; and the increment plan contradicts itself on where the keymap seat
  scope lands. A major is never folded in place; all are requirement/plan-class, owned by
  this station's return edge. Recorded per `stations/p2-review.md`: amend P1
  (`devflow-init.py --iterate-to P1`), then the full P2 review re-runs on the amended
  contract.)
- **Out-of-scope findings:** `none` — all 19 findings are requirement/plan-class and ride
  the P1 return edge; no implementation-class finding (carried to Phase 3) and no
  existing-surface security finding (security-reviewer re-invocation) arose.

- **Findings:** `2` blocker (validator V10, pre-existing — see VAL-01/02 below) · `7` major · `12` minor
- **Validator at this station:** `2 block · 813 notice · 56 n/a`, exit 0 — both blocks are
  pre-existing contract defects (IFC `FLOW` keyword syntax, `01-requirements.md:843,851`)
  that only become blocks past Phase 1, so the P1 gate could not see them. They are
  requirement-artifact defects and ride the same P1 return edge; per the commission
  ("do NOT fix the author's artifacts") they are recorded, not patched in place.
- **shall/should check:** ✓ clean — 73 `shall`, zero `should`; the only `shall` outside an
  HLR/LLR block is the §3 convention meta-line (`01-requirements.md:274`)
- **Two-layer (blockers):** ✓ every story has an `AT` · ✓ output reqs name deliverable+observation ·
  ✗ both trace chains complete — chains themselves verified complete both directions (6 US →
  20 HLR → 51 LLR → 27 TC; 23 ATs, zero orphans), but the stated denominator (26/52) is wrong,
  so §5.2 criterion 1 cannot be certified as written (QA-01) · ✓ ATs are genuinely black-box
  (Textual `Pilot` / subprocess on the real surface; no internal symbol referenced)
- **Census (change-first):** done — best-effort + gate-confirmed; reservations ARC-03
  (`tests/test_inc9c.py:271-277` line-pin not in the Inc-6 census; the `test_home*.py` glob
  matches no file), ARC-04 (the three Inc-1 test re-points not enumerated), ARC-05 (shared-fixture
  policy undeclared). The I-gate must confirm these on the amended plan.
- **Security:** ⚠ `3` findings — all MINOR (SEC-1, SEC-2, SEC-3); security verdict `approve`
- **Evidence checklists (architect / qa / security / ux):** ✓ all complete (four evidence
  files written; per-role detail below)

> Gate = `iterate-to-refine`; read the Findings and the per-role evidence.

---

## Detail (reference)

### Findings

| ID | Reviewer | Severity | Area / Req | What | Recommendation | Status |
|----|----------|----------|------------|------|----------------|--------|
| VAL-01 | validator (V10) | blocker | IFC · `01-requirements.md:843` | FLOW block keyword line reads `FLOW rm-graph-to-gaps-screen` — no colon; the template requires `FLOW: <id>`. Unparseable IFC past Phase 1; invisible at the P1 gate (rule fires only past P1). | Add the colon (`FLOW: rm-graph-to-gaps-screen`) in the P1 amendment. | open |
| VAL-02 | validator (V10) | blocker | IFC · `01-requirements.md:851` | Same defect in the second block: `FLOW rm-node-to-sheet` → `FLOW: rm-node-to-sheet`. | Same fix in the P1 amendment. | open |
| ARC-01 | architect | major | census · `01-requirements.md:920`, `PLAN.md:21,62,98` | Stated totals "26 HLR / 52 LLR" do not match the artifact: 20 HLR headings, 51 LLRs (RVM 10, RVG 9, RVS 14, RVH 14, RVT 3, RVU 1). §5.2 criterion 1 ("All 52 LLRs…") is unsatisfiable as written. | Re-count; fix the numbers everywhere or restore the missing requirements; re-run the P1 gate. | open |
| ARC-02 | architect | major | increment plan · `PLAN.md:104` vs `01-requirements.md:752-756` vs `docs/ARCHITECTURE.md:267` | Seat-scope landing contradiction: Inc-2 (trunk host) claims LLR-RVH.4.1–4.3 but not `mapper/keymap.py`, scheduled in parallel Inc-6; `RelMapScreen` cannot generate BINDINGS until `SCOPE_RELMAP` exists, voiding fork preconditions F-2/F-3; ARCHITECTURE §4 says the scope "lands whole in the shell increment". | Move `keymap.py` into trunk Inc-2 (4 files, ≤4 budget holds); drop from Inc-6; amend the ARCHITECTURE §4 wording at the PDR. | open |
| ARC-03 | architect | minor | reverse census · `docs/ARCHITECTURE.md:357-363`, `tests/test_inc9c.py:271-277` | Inc-6 census omits the line-pinned `LEAK_EXCEPTIONS` key `("mapper/screens/home.py", 176, "str(exc)")` (reddens if code is inserted above line 176); the `test_home*.py` glob names no file. | Add `test_inc9c.py` to the Inc-6 census; re-pin in the same increment. | open |
| ARC-04 | architect | minor | C-26 enumeration · `01-requirements.md:808`, `PLAN.md:103` | The three Inc-1 test re-points not enumerated: `tests/test_relmap_model.py:17-26`, `test_relmap_descriptor.py:38`, `test_relmap_audit.py:33-35`; M-RVT-2 names the `relmap.audit` path no test uses (live old path is `relmap.descriptor`). | Name the three files in Inc-1's test ledger; reword M-RVT-2 to the descriptor path. Coverage itself is intact (LLR-RVT.1.2 + reader census) — an enumeration gap. | open |
| ARC-05 | architect | minor | lanes · `PLAN.md:105-108` | Shared-fixture policy undeclared: two renderer lanes appending to `tests/_relmap_fixtures.py` would silently violate the crossed reverse census. | PDR declares: renderer lanes build synthetic maps inline per test file; shared fixture modules are trunk-only. | open |
| ARC-06 | architect | minor | module map · `docs/ARCHITECTURE.md:166` | The `app` row's EXPOSES omits the committed `RelMapScreen` re-export (named only at `:194`/`:165`). | Add `RelMapScreen` to the app row's exposes at the PDR seal. | open |
| QA-01 | qa-reviewer | major | census · `PLAN.md:21,98-99`, `01-requirements.md:920-921` | Same defect as ARC-01 from the traceability side: 51/51 LLRs carry `Asserting tests` (nothing untested), but the 26/52 denominator is wrong, so gate (c) cannot be certified against it; one LLR + six HLRs from the claimed totals are unaccounted. | Reconcile totals (restore or correct to 20/51); re-run the P1 gate after the edit. | open |
| QA-02 | qa-reviewer | major | seam 1 · `01b-acceptance-design.md:13-16`, `01-requirements.md:269,964-967` | AT-driver host push / fixture injection — an orchestrator-designated P2 review target — is still deferred: every view AT (AT-130…149) is unexecutable until trunk Inc-2 + the PDR discharge the seam. Explicit and tracked, but unproven. | Make the discharge condition concrete in F-5 / Inc-2: name the fixture-workspace injection point and verify it exists before lanes 3–5 start, not only at the join. | open |
| QA-03 | qa-reviewer | major | seam 2 · `01-requirements.md:739`, `PLAN.md:124` | Workspace-as-repo derivation — the second P2 review target — is still deferred: `derive_reqharness_map(workspace, …)` over a bare (non-git) directory is unprobed. | PDR proves it against a fixture workspace that is not a repo root (AT-147's fixture shape); close the flag in the ledger. | open |
| QA-04 | qa-reviewer | major | rulings fold-back · `01-requirements.md:535,755`, `01b-acceptance-design.md:92`, `PLAN.md:124` | The by-kind ruling (SHIPS: LLR-RVG.1.5 + `k`) is not folded back — the contract still says "CONTINGENT … PDR rules in or out" and AT-136 says "dropped otherwise"; same staleness for the hook bound (ruling: 240, cut after escaping) vs LLR-RVU.1.1's "decided at the R2 PDR (recommendation: 240)". The ledger — the designated home for rulings — is empty. | Ledger ruling entry; de-contingent the three by-kind sites and pin the 240 bound; keep the PDR freeze of glyph/table details. | open |
| QA-05 | qa-reviewer | minor | AT-152 · `01b-acceptance-design.md:46,255-262`, `01-requirements.md:823-828` | AT-152's numeric oracle (bound = 240) is not pinned in the AT body; it inherits "decided at the R2 PDR". | State bound 240 (per ruling) in AT-152; assert emitted-line length ≤ 240. | open |
| QA-06 | qa-reviewer | minor | black-box arms · `01-requirements.md:464-469,671-677`, `01b:283` | Lens dimming (LLR-RVM.2.3) and the sheet's counted overflow line (LLR-RVS.6.2) have unit coverage only, no black-box arm — both operator-visible. | Add one assertion each to AT-131/132 and AT-141/143, or record explicitly that Layer A owns them. | open |
| QA-07 | qa-reviewer | minor | scale coverage · contract scope-wide | No AT exercises a very large map (the 100k-node class); largest surface is the 303-node live skeleton; budget-spent arms cover `VISIT_BUDGET`, not render scale. | Out of scope as written; if scale matters add an HLR + AT, else note the deliberate omission in §2.5. (Overlaps SEC-2.) | open |
| QA-08 | qa-reviewer | minor | traceability · `01-requirements.md:679-685` | LLR-RVS.7.1 (read-only posture) traces to HLR-RVS.2 (neighbour rows) though its substance is HLR-RVH.2/RVS read-only. | Re-trace to HLR-RVH.2, or accept and note. Cosmetic. | open |
| SEC-1 | security-reviewer | minor | hook bound · `01-requirements.md:823-829`, `01b:254-264` | The ruling's "cut AFTER escaping so an escaped spelling is not sliced mid-sequence" clause is absent from LLR-RVU.1.1. Code-verified cosmetic only: `_visible` (`mapper/reqharness/audit.py:88-118`) emits printable ASCII + `\xNN`/`\uXXXX` spellings — no live ESC/CSI can be reconstituted by a mid-spelling slice. | One sentence in LLR-RVU.1.1 (back the cut to the spelling start) + one AT-152 arm with a straddling payload. | open |
| SEC-2 | security-reviewer | minor | DoS at cap · `mapper/osopen.py:93-94`, `mapper/relmap/model.py:258-261` vs `01-requirements.md:918-930` | No AT exercises the shipped 100,000-node cap; windowing LLRs bound per-render work in words but nothing builds a cap-scale map and asserts windowed render + bounded derivation. | Add one cap-scale arm (in-test `build_map` at MAX_NODES through the matrix window + sheet counted line + timed derivation bound) to AT-137 or a new TC. | open |
| SEC-3 | security-reviewer | minor | cut-before-escape clause · `01-requirements.md:495-501,567-573,655-661` | The C-10 control "truncate BEFORE the escape pass" is never restated as an explicit view-path clause. Mechanism-verified safe: adapter pre-cut at 120 (`mapper/relmap/model.py:34,67-71`; `mapper/relmap/adapter.py:134-142`); `fit`/`shown_cells` measure post-coercion only (`mapper/darkside.py:587-621`). | One line in the sink LLRs' draft-time verification so a future renderer cannot regress it silently. | open |
| F-UX-1 | ux-reviewer | major | ruling drift · `01-requirements.md:535,755,962`, `01-requirements-ledger.md:1-11` | By-kind toggle still written as CONTINGENT against the binding ruling (SHIPS: LLR-RVG.1.5 + `k`); a Phase-3 implementer reading only the contract could lawfully drop the toggle, `k`, and AT-136; the ledger is empty. (Same defect as QA-04, seen from the UX seat.) | Ledger ruling entry; de-contingent the three sites (LLR-RVG.1.5 statement/validation, LLR-RVH.4.1 `k` clause, §6.3 open risk). | open |
| F-UX-2 | ux-reviewer | minor | tone scope · `01-requirements.md:608` vs `:523` | "WARN reserved to the matrix lens reach gauge" (ruling record) vs LLR-RVS.2.3 painting the sheet's `◐` glyph in WARN — reads inconsistent. | PDR disambiguates the ruling's scope in one clause; align `:523` or the sheet tone. | open |

### shall / should check

✓ Clean. 73 `shall` occurrences, all inside HLR/LLR statement blocks except the §3
convention meta-line (`01-requirements.md:274`); zero `should` anywhere in the contract
(architect evidence, focus 5).

### Two-layer acceptance review (blockers)

| Story / Req | (a) AT present | (b) deliverable+method named | (c) both chains | (d) black-box pure | Status |
|-------------|----------------|------------------------------|-----------------|--------------------|--------|
| US-RMV-001 matrix + lens | yes — AT-130…134 | yes — rendered strings, `export_text()`, audit sink | yes — 1→RVM.1-4→10 LLR→TC-RM-04…09; AT-130…134 (denominator: QA-01) | yes | ✓ (major on census) |
| US-RMV-002 gaps | yes — AT-135…139 | yes — literal strings/chips/rows on the frame | yes — 1→RVG.1-3→9 LLR→TC-RM-10…14 (AT-136 contingent — QA-04/F-UX-1) | yes | ✓ (major on ruling drift) |
| US-RMV-003 sheet | yes — AT-140…144 | yes — verbatim crumb/note lines, oracle-compared rows | yes — 1→RVS.1-6→14 LLR→TC-RM-15…20 | yes | ✓ |
| US-RMV-004 shell | yes — AT-145…149 | yes — row/cell census, active-screen assertion, seat equality | yes — 1→RVH.1-5→14 LLR→TC-RM-21…27 | yes | ✓ |
| US-RMV-005 text leaf | yes — AT-150 census + AT-151 `mapper --audit` subprocess | yes — census 1/1/1 + zero old-path hits; byte identity vs R1 goldens | yes — 1→RVT.1→3 LLR→TC-RM-28/29 | yes — AT-150 white-box by design (the story's observable IS code structure, C-31) | ✓ |
| US-RMV-006 hook bound | yes — AT-152 subprocess | yes — line ≤ bound, D4 arms (bound numeric: QA-05) | yes — 1→RVU.1→1 LLR→TC-RM-30 | yes | ✓ |

Traceability totals measured (QA evidence): 6 US · 20 HLR · 51 LLR (all with `Asserting
tests`; 14 planned-name) · 23 AT (AT-130…152) · 27 TC (TC-RM-04…30). Zero orphan ATs/TCs
either direction. Cited precedents verified on disk (`run_test()` pilot idiom
`tests/test_colour_always_on.py:25-34,64-70`; `home.py:209`; R1 test files exist; planned
test files correctly absent). PLAN §Roadmap provisional names match LLR `Asserting tests`
1:1.

Negative controls present: empty-map arms (AT-130/135/138a/140/147b), C-17 hostile-input
mandate satisfied black-box (AT-134/139/144 + AT-145b + AT-148 — literal render, no style
leak, no raise, app alive), 87-col arms (AT-130/131/137/143/148), budget-spent honesty
(AT-132, AT-138b), refused-descriptor (AT-147a, AT-151 byte-identity). Gaps: no cap-scale
arm (QA-07/SEC-2); two unit-only behaviours (QA-06).

### Supersession census (change-first)

Planned new/moved/edited files × guard families, run by the architect lens (full detail +
commands in `evidence/p2-architect.md`):

- **Reverse greps run:** `refusal_line` → 2 test files (`test_relmap_audit.py`,
  `test_relmap_descriptor.py`), none via the `audit` path; `DISPLAY_MAX` →
  `test_relmap_model.py`; `cut` from `relmap.model` → 2 files; `MapScreen` → ~40 files
  (routing branch + re-export added, no move — no re-point owed); home glob `*.mmd` → no
  direct test pin (fixture-workspace hits only).
- **C-26 declarations:** `cut`/`DISPLAY_MAX`/`refusal_line` declared with the reader
  census; **reservation ARC-04** — the three re-point files not enumerated (coverage
  intact via LLR-RVT.1.2); **reservation ARC-03** — `test_inc9c.py` line-pin owed at Inc-6.
- **Behavioral-placeholder / AST-composition / frozen-module families:** R1 BANNED_*
  isolation census (`tests/test_relmap_isolation.py:31-43`) auto-covers the new `text.py`
  leaf; the `relmap` internal-ordering amendment is cycle-free (text is stdlib-only);
  frozen A3 surfaces consumed exactly per R1 D3/§E.
- **Lanes:** file sets pairwise disjoint (4,3,1,1,1,3,2,1 — all ≤4 source files);
  import-surface disjoint (renderers import only the PDR-frozen host surface);
  **reservation ARC-05** — shared-fixture policy undeclared; **reservation ARC-02** —
  the Inc-2/Inc-6 keymap split contradicts the fork preconditions and must be amended
  before the plan can gate.
- What the I-gate must confirm: the amended Inc-1/2/6 censuses (enumerated re-point files,
  `test_inc9c.py` re-pin), the fixture policy, and the re-counted requirement census.

### Security review summary

Triggers C6 + C8 fired; security-reviewer ran (`approve`, 3 MINOR). Markup injection at
the sink: PASS — all four sink LLRs (RVM.4.2, RVG.3.1, RVS.5.1, RVH.5.2) mandate
at-the-sink escaping, name `[`/`]`/ESC/control payloads, cite the `draft_guard.py:54-63`
dual-guard precedent, and are backed by hostile-payload AT arms (AT-134/139/144/145/148);
`darkside.plain` (`mapper/darkside.py:550-561`) deliberately avoids `rich.markup.escape`.
Cut/escape ordering: PASS with SEC-1/SEC-3 clause gaps (mechanism-verified safe).
DoS at scale: PASS with SEC-2 coverage gap (caps at `mapper/osopen.py:93-94`, enforced
`mapper/relmap/model.py:258-261`; windowing LLRs bound per-render work). Read-only:
PASS (BINDINGS census M-RVH-5; no-`mapper.db`-write M-RVH-6; no-`osopen` RVS.7.1; `r`
in-memory). Parser surface: PASS (descriptor caps, byte cap, K1–K17 closed causes, never
`str(exc)`; no new boundary crossing).

### Evidence checklists (full) — architect · qa-reviewer · security-reviewer · ux-reviewer

**architect — Kimi K2.8 subagent executing agents/architect.md · iterate-to-refine**
✓ module boundaries (third screen→core edge coherent; `relmap/text.py` legitimate leaf;
  home routing consistent) · ✓ frozen interfaces touched declared per A3 · ✗ increment
  plan internal contradiction (ARC-02) · ✓ lanes forkable — file/import/test sets disjoint
  (reservation ARC-05) · ✓ Python 3.10 floor (`pyproject.toml:9`; no >3.10 syntax/std) ·
  ✓ shall/should clean · ✓ US→HLR→LLR derivation sound · ✗ census totals wrong (ARC-01)

**qa-reviewer — Kimi K2.8 subagent executing agents/qa-reviewer.md · iterate-to-refine**
✓ every requirement testable with an oracle (51/51 `Asserting tests`) · ✓ AT-130…152
  observable through the real app (Textual `Pilot` / subprocess; no internal symbols) ·
  ✓ negative controls present (empty/87-col/hostile/budget/refused) · ✓ traceability both
  ways (zero orphans) · ✗ stated totals unreconciled (QA-01) · ✗ both P2-review-target
  seams still deferred (QA-02, QA-03) · ✗ rulings not folded back (QA-04)

**security-reviewer — Kimi K2.8 subagent executing agents/security-reviewer.md · approve**
✓ markup injection controlled at the sink (dual-guard; hostile ATs per view) · ✓
  cut-before-escape on the view path (mechanism-verified; clause gap SEC-3) · ✓ hook path
  cut-after-escape per C-42 (mid-spelling clause gap SEC-1, cosmetic) · ✓ read-only
  guarantees (censuses + mutants) · ⚠ DoS at the 100k cap unexercised (SEC-2) · ✓ parser
  limits intact

**ux-reviewer — Kimi K2.8 subagent executing agents/ux-reviewer.md · iterate-to-refine**
✓ prototype-verdict fidelity (matrix-panel + binds-glyphs; gaps-ranked + count column,
  no microbar; sheet-direct + `c` full chain — all verbatim-cited vs the verdict) ·
  ✓ keys via the keymap single seat (no hand-written bindings; M-RVH-10 reddens them) ·
  ✓ help/palette entries mandatory from the seat (AT-149 seat-equality) · ✓ 118 reference
  + 87 checked pinned (LLR-RVM.4.1/RVG.1.4/RVS.6.1; AT-130/131/137/143/148) · ✓ Darkside
  lowercase census-pinned, no Solari ALL-CAPS · ✗ by-kind ruling not folded back (F-UX-1,
  = QA-04) · ⚠ WARN tone scope ambiguous (F-UX-2)


---

## Author dispositions — P1 amendment, 2026-10-25 (P2 first-pass return edge)

Gate `iterate-to-refine` folded as the P1 amendment (iteration recorded in `state.json`;
ledger entries `LED-2026-10-25-r2.01…11`; both seams discharged by executed probes under
`evidence/p2-seam-*.md`). Every finding below is requirement/plan-class and was amended in
the record — none was patched in a reviewer text, none carried to Phase 3, none
backlogged. The gate re-ran after the amendment: `0 block · 814 notice · 57 n/a`, exit 0
(PLAN §Gate notices).

| ID | Disposition | Where it landed |
|----|-------------|-----------------|
| VAL-01 | **fixed** — colon added; all six IFC openers normalized to `FLOW: <id>` (the defect was in every FLOW line; two surfaced as blocks) | `01-requirements.md` IFC Part A; gate re-run 0 BLOCK |
| VAL-02 | **fixed** — same normalization | same |
| ARC-01 | **fixed** — re-counted by script (command + output in the ledger measurement `LED-2026-10-25-r2-census`): 20 HLR / 52 LLR post-amendment (51 + new LLR-RVH.3.3); §5.2 criterion 1, PLAN header + roadmap corrected | `01-requirements.md:§5.2`, `PLAN.md` |
| ARC-02 | **fixed** — `mapper/keymap.py` moved into trunk Inc-2 (`screens/relmap/{__init__,screen,base}.py` + `keymap.py`, 4 ≤ 4); Inc-6 = `home.py` + `app.py` (2); ARCHITECTURE §4 KEYMAP row and §6 worksheet amended; fork preconditions re-checked — F-3 ownership text amended, worksheet intersections stay empty | `PLAN.md` roadmap, `docs/ARCHITECTURE.md` §4/§6, `01-requirements.md` F-3; `LED-2026-10-25-r2.08` |
| ARC-03 | **fixed** — `tests/test_inc9c.py` (`LEAK_EXCEPTIONS` line-pin on `mapper/screens/home.py`) named in the Inc-6 census with the same-increment re-pin declared; the `test_home*.py` glob (matches no file) replaced by the accurate no-direct-pin + home-adjacent pins statement | `docs/ARCHITECTURE.md` §6 reverse census, `PLAN.md` Inc-6 |
| ARC-04 | **fixed** — the three re-pointed files enumerated in Inc-1's test ledger (`test_relmap_model.py:17-26`, `test_relmap_descriptor.py:38`, `test_relmap_audit.py:33-35`); M-RVT-2 reworded to the live old path `mapper.relmap.descriptor` | `PLAN.md` Inc-1, `01-requirements.md` LLR-RVT.1.2; `LED-2026-10-25-r2.11` |
| ARC-05 | **fixed** — policy declared: renderer lanes build synthetic maps inline per test file; shared fixture modules trunk-only | `PLAN.md` §Roadmap |
| ARC-06 | **fixed** — `RelMapScreen` added to the `app` row's EXPOSES (as the R2 target, the `MapScreen` pattern) | `docs/ARCHITECTURE.md:166` |
| QA-01 | **fixed** — same script re-count as ARC-01; the stated denominator now equals the artifact (52/52 LLRs carry asserting tests) | `01-requirements.md:§5.2`, `PLAN.md` |
| QA-02 | **fixed** — seam RESOLVED by executed probe (transcript `evidence/p2-seam-at-driver.md`, PASS on today's code): the injection point is named — `MapperApp(workspace=…)` (`mapper/app.py:250`) under a headless `run_test()` pilot — and F-5 now requires lanes 3–5 to verify it at entry, not only at the join | `01-requirements.md` F-5 + §6.3, `01b` driver seams; `LED-2026-10-25-r2.07` |
| QA-03 | **fixed** — seam RESOLVED by executed probe (transcript `evidence/p2-seam-workspace-repo.md`); rule adopted and pinned: the descriptor/canon resolves RELATIVE TO THE WORKSPACE ROOT, git is never consulted on the screen derivation path, a missing canon gives the closed-set `unavailable` state — never a crash (probe caveat recorded: the R1-frozen `--audit` hook's git gating is the RVU surface, out of scope); new LLR-RVH.3.3 + AT-147 arm; flag closed in the ledger | `01-requirements.md` LLR-RVH.3.1/.3.3, `01b` AT-147; `LED-2026-10-25-r2.03` |
| QA-04 | **fixed** — ruling recorded in the ledger (C11 naming: requirement, asserting test, mutant); all three by-kind sites de-contingented; hook bound 240 folded (no "decided at the R2 PDR" wording remains in the contract outside the historical, superseded PLAN decision row); glyph/table details remain PDR-frozen per the ruling | `01-requirements.md` LLR-RVG.1.5/RVH.4.1/HLR-RVU.1/LLR-RVU.1.1/§6.3/IFC, `01b` AT-136; `LED-2026-10-25-r2.01/r2.02` |
| QA-05 | **fixed** — AT-152 pins bound 240 in the body and asserts the emitted-line length ≤ 240 | `01b` AT-152 |
| QA-06 | **fixed** — black-box arms promoted: FAINT dimming census on AT-131/AT-132, counted overflow line on AT-141/AT-143 | `01b` AT-131/132/141/143; `LED-2026-10-25-r2.10` |
| QA-07 | **fixed** (with SEC-2) — the cap-scale arm of AT-137 at 100,000 nodes is the deliberate scale coverage; §2.5 assumption A5 records that no other AT exercises very large maps | `01b` AT-137, `01-requirements.md` §2.5 A5; `LED-2026-10-25-r2.09` |
| QA-08 | **fixed** — re-traced to HLR-RVH.2 | `01-requirements.md` LLR-RVS.7.1; `LED-2026-10-25-r2.04` |
| SEC-1 | **fixed** — the no-mid-spelling cut clause is verbatim in LLR-RVU.1.1 (cut backs to the spelling start) and HLR-RVU.1; AT-152 carries the straddling-payload arm; new mutant M-RVU-3 | `01-requirements.md`, `01b` AT-152; `LED-2026-10-25-r2.02` |
| SEC-2 | **fixed** — cap-scale arm added (in-test `build_map` at `MAX_NODES` through the matrix window + sheet counted line + bounded derivation wall-clock) | `01b` AT-137; `LED-2026-10-25-r2.09` |
| SEC-3 | **fixed** — the cut-before-coercion clause recorded in the draft-time verification of all three sink LLRs (RVM.4.2, RVG.3.1, RVS.5.1) | `01-requirements.md`; `LED-2026-10-25-r2.06` |
| F-UX-1 | **fixed** — same fold-back as QA-04 from the UX seat: the ledger ruling + the three de-contingented sites; a Phase-3 implementer reading only the contract can no longer lawfully drop the toggle, `k` or AT-136 | `01-requirements.md`, `01b`; `LED-2026-10-25-r2.01` |
| F-UX-2 | **fixed** — WARN scope clause: WARN is reserved to reach/severity-attention signals — the lens gauge, `not computed`, the sheet `◐` — and no tally word, chip or other chrome uses it; LLR-RVG.1.3, LLR-RVS.2.3 and the PLAN OQ-G2 row now read consistently | `01-requirements.md`; `LED-2026-10-25-r2.05` |

**Amended increment plan (recap).** Inc-1 text leaf (4 files, three re-pointed test files
enumerated) → Inc-2 screen host + keymap seat (4 files; additive `SCOPE_RELMAP` incl. `k`;
AT-driver injection verified here) → lanes 3/4/5 (renderers, inline synthetic fixtures) ∥
shell Inc-6 (`home.py` + `app.py`, 2 files; `test_inc9c.py` re-pin) → 6b help/palette → 7
hook bound. Trunk-join F-5 runs the all-lane ATs on the joined tree; fork preconditions
F-1…F-5 re-checked after the keymap move (F-3 text amended; intersections still empty).

**Second P2 pass owed next** on this amended contract (station P2 per the iterate
record), then the PDR.

---

## Second P2 pass — 2026-10-25 (independent; reviewers authored none of the batch)

Second full P2 cross-review of the amended contract (P1 amendment `daddd6d`). Four
fresh reviewer lenses in parallel — `architect` ∥ `qa-reviewer` ∥ `security-reviewer`
∥ `ux-reviewer` — each verifying every first-pass finding of its role against the
amended files and code (verified / reopened, with file:line evidence), then sweeping
the amendment for new defects in its lens. Per-role evidence:
`evidence/p2-pass2-architect.md`, `evidence/p2-pass2-qa-reviewer.md`,
`evidence/p2-pass2-security-reviewer.md`, `evidence/p2-pass2-ux-reviewer.md`.
First-pass text above is untouched.

### Verdicts

| Lens | Verdict | First-pass findings | New findings |
|------|---------|--------------------|--------------|
| architect | approve | ARC-01…ARC-06 all verified (own re-count 20 HLR / 52 LLR; keymap seat in trunk Inc-2 with F-2/F-3 coherent; `test_inc9c.py` census; three re-point files enumerated; fixture policy; app-row EXPOSES) | none |
| qa-reviewer | iterate | QA-01…QA-08 all verified; both deferred seam probes re-run from their stored commands and reproduced (exit 0, outputs match the stored transcripts); LLR-RVH.3.3 + AT-147 arm testable and black-box; AT-152 pins 240 + straddling arm; AT-137 cap-scale arm | P2Q-1 major · P2Q-2, P2Q-3 low |
| security-reviewer | approve | SEC-1…SEC-3 all verified (clause verbatim in LLR-RVU.1.1 + HLR-RVU.1 with AT-152 straddling arm and M-RVU-3; AT-137 cap-scale arm; cut-before-coercion clause in the three sink LLRs — the RVH.5.2 completeness check resolves as NOT needed: markup-safety mandate only, no width-cut/fit behavior, same guarded path). No new surface from LLR-RVH.3.3; `--audit` git-gating carve-out sound | none |
| ux-reviewer | iterate | F-UX-2 verified (WARN scope consistent across LLR-RVG.1.3, LLR-RVS.2.3, `not computed`, PLAN OQ-G2); F-UX-1 partially reopened | P2U-1 major |

### Reopened / new findings (second pass)

| ID | Lens | Severity | Finding |
|----|------|----------|---------|
| P2Q-1 = P2U-1 | qa ∥ ux (independent convergence; orchestrator-verified) | **major** | LLR-RVH.4.1's normative Statement (`01-requirements.md:781`) binds "exactly:" an exhaustive chord list that **omits `k`** — the `k` binding is asserted only in the non-normative draft-time verification (`:784`). Pre-amendment, `k` rode as a PDR-conditional in that same verification slot, so the QA-04/F-UX-1 de-contingenting never reached the Statement. Contradicts LLR-RVG.1.5 (`:548-552` "the `k` binding is pinned in LLR-RVH.4.1"), §6.3 (`:997-998`), and AT-136 (`01b:105`): an implementer following the Statement alone ships a seat without `k` and AT-136 REDs at Phase 4. Fix: add "`k` to the by-kind grouping toggle" to the `:781` enumeration. |
| P2Q-2 | qa | low | Matrix negative-arms column stale vs the amended AT bodies (AT-152 row omits M-RVU-3; AT-137 row omits M-RVM-1). |
| P2Q-3 | qa | low | One residual `assumed — verify in Phase 2` flag (`01-requirements.md:584`, RVT landing order) left while its sibling flags were removed; substance already resolved (`PLAN.md:114`). |
| P2V-1 | validator (V10) | **blocker** | At station P2 the validator reports **6 blocks** — every IFC FLOW block (`01-requirements.md:868,875,883,891,898,904`) "has no node parsed": the blocks list nodes in arrow form (`NODES : enumeration + badge + order -> LLR-…`) instead of the template's `- fn : <name>` items with `owner : <LLR>` lines (`templates/ifc-template.md` §1). Not caused by this pass (verified on the unmodified HEAD tree). Invisible until now: the amendment's "gate re-run 0 block" was measured while `state.json` still declared `current_station: P1` (commit `daddd6d`), where V10's "past Phase 1" condition does not fire — the same blind spot the first pass documented for VAL-01/02. The VAL-01/02 colon blocks themselves stay fixed. Fix in the P1 amendment: re-express the six FLOW blocks' NODES in the `- fn :`/`owner :` format. |

### Gate (second pass)

**`iterate-to-refine`** → Phase 1, on two independent counts:

1. **P2V-1 (blocker)** — six V10 blocks on the amended contract's IFC, surfaced only
   at the true P2 station (the amendment's 0-block re-run was at P1, where the rule
   is blind). Per `stations/p2-review.md`, blockers force `iterate-to-refine`.
2. **P2Q-1 = P2U-1 (major)** — cross-confirmed by two independent lenses and verified
   by the orchestrator at `01-requirements.md:781`; a requirement-defect major the run
   has no approving authority over defaults to `iterate-to-refine`.

The amendment is surgical: add `k` to the `:781` enumeration, re-express the six IFC
NODES lists in the template format, and fold the two lows (P2Q-2/P2Q-3) in the same
edit; then the P2 pass re-runs a third time on the re-amended contract. Architect and
security lenses are clean (both `approve`, zero new findings); no existing-surface
security finding (no security-reviewer re-invocation) and no implementation-class
finding (nothing carried to Phase 3).

**Validator at this station (second pass):** `6 block (V10, P2V-1) · 817 notice ·
56 n/a`, exit 1 — the six blocks are all in the author's contract artifact, which
this pass must not edit; the gate cannot go green until the P1 amendment lands. VAL-01/02
remain fixed (the FLOW-colon defect does not reappear).

---

## Author dispositions — P1 amendment, 2026-10-25 (P2 second-pass return edge)

Gate `iterate-to-refine` folded as the second P1 amendment (iteration 2 recorded in
`state.json`; ledger entries `LED-2026-10-25-r2.12/.13` plus the IFC/matrix amendment
record). Every finding below is requirement/plan-class and was amended in the record — none
was patched in a reviewer text, none carried to Phase 3, none backlogged. The validator was
re-run with `state.json` at the true P2 station (the amendment's blind-spot fix), after one
V26 catch on the new ledger entry's Requirement bullet (a cross-ref id V26 reads as a second
amended requirement — the bullet now names only LLR-RVH.4.1): **0 block · 817 notice ·
56 n/a, exit 0** — the six P2V-1 V10 blocks and the one V26 block are all resolved.

| ID | Disposition | Where it landed |
|----|-------------|-----------------|
| P2Q-1 = P2U-1 | **fixed** — "`k` to the by-kind grouping toggle" added to LLR-RVH.4.1's normative Statement chord list; the draft-time duplicate binding assertion removed (the binding is normative now — the slot keeps only the trunk-increment / ARC-02 ownership note). An implementer reading the Statement alone can no longer ship a seat without `k`; the LLR-RVG.1.5 (`:552`), §6.3 and AT-136 cross-references that already claimed `k` is pinned here are now true | `01-requirements.md` LLR-RVH.4.1; `LED-2026-10-25-r2.12` |
| P2Q-2 | **fixed** — matrix negative-arms column caught up to the amended AT bodies: AT-152 row names M-RVU-1/2/3 (body asserts the straddling arm), AT-137 row names M-RVG-5/6 + M-RVM-1 (cap-scale arm); the AT bodies remain authoritative | `01b` AT↔requirement matrix; ledger amendment record |
| P2Q-3 | **fixed** — the last residual `assumed — verify in Phase 2` flag resolved with the decided rule already pinned at PLAN.md Inc-1: the RVT text leaf lands in trunk Inc-1, first, before any renderer lane forks, so every renderer consumes the frozen leaf names from the start; its sibling flags were already discharged as executed probes (`-r2.03`/`-r2.07`) | `01-requirements.md` LLR-RVG.3.1; `LED-2026-10-25-r2.13` |
| P2V-1 | **fixed** — all six IFC FLOW blocks' NODES re-expressed as `- fn : <name>` items with their own `owner : <LLR>` line; combined owners split one node per owner (template "one owner per node"); every owner→LLR mapping preserved verbatim, only the syntax moved. Surfaced only at P2 because V10's "past Phase 1" condition is blind at P1 — the re-run is measured at the true P2 station | `01-requirements.md` IFC Part A; ledger amendment record |

**Amended increment plan (unchanged).** The second pass raised no plan-class change: Inc-1
text leaf → Inc-2 screen host + keymap seat (incl. `k`, now normative in LLR-RVH.4.1) →
lanes 3/4/5 ∥ shell Inc-6 → 6b help/palette → 7 hook bound; fork preconditions F-1…F-5
unchanged. The PDR follows this gate.
