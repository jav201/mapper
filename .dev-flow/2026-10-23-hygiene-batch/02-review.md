# Review — mapper — Batch 2026-10-23-hygiene-batch

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`).
> Phase 2 artifact. Reviewers (in parallel): `architect` ∥ `qa-reviewer` ∥ `security-reviewer` by trigger family C (always in `full`).

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/guides/review-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

**BLUF:** the contract is well-built — EARS-clean, two-layer traceability intact, oracle citations verified line-by-line against QuickMap, premises independently re-measured. Three requirement-defect **majors** send it back to P1: (F1) premise 5's "repo maxima" are falsified by tracked perf-evidence workspaces (12,000-node sidecars), so the R1 headroom derivation is overstated; (F2) the mandatory C-52 fork table and the §6 worksheet omit `mapper/osopen.py` from L2's file set although the batch's own ARQ commits to editing it; (F3) LLR-Q3.1.2's pass threshold is keyed on "the recorded state matrix" that no batch artifact records.

## ✅ Verdict (read first)

- **Gate:** `iterate-to-refine` → Phase 1 (0 blockers; three requirement-defect majors — F1, F2, F3). Chosen under the standing authorization declared in PLAN.md §Header: the default for a requirement-defect major is `iterate-to-refine`, and no circumstance here argues for carrying them open — each is a cheap P1 amendment (re-scope a premise, add one file to a mandatory table, record one matrix), and F1 sits on the evidential basis of ruling R1, which the contract itself elevated to a ledger amendment.
- **Out-of-scope findings:** `none`

- **Findings:** `0` blocker · `3` major · `6` minor
- **shall/should check:** ✓ clean
- **Two-layer (blockers):** ✓ every story has an `AT` · output reqs name deliverable+observation · both trace chains complete · ATs are genuinely black-box (reservation m5 on Q2's observation point)
- **Census (change-first):** done — best-effort + gate-confirmed (reservation: F2 — the I-gate must confirm L2's file set INCLUDING `mapper/osopen.py`)
- **Security:** ⚠ `1` finding (LOW — m4)
- **Evidence checklists (architect / qa / security):** ✓ all complete

**Second pass (2026-10-23, over the amended contract, dispositions LED-.5–.8):** all three majors and minors m1–m4 **verified** against the live tree by re-measurement/re-read (evidence: `evidence/recheck-architect.md`, `recheck-qa.md`, `recheck-security.md`); m5/m6 confirmed **open, correctly carried** to Phase 3 with the owning stations named. Gate → `approve` (0 blockers, 0 open majors; two new contract-record minors N1/N2 named below with their owning station — minors never force a return edge). The design-review findings from the same pass live in `design/PDR-2026-10-23-hygiene-batch.md`.

**Reviewers (second pass):**
- `architect — Kimi K3 subagent executing agents/architect.md · approve` (F1, F2, m1, m2, m3 verified; new minors N1, N2)
- `qa-reviewer — Kimi K3 subagent executing agents/qa-reviewer.md · approve` (F3 verified; m5/m6 carries confirmed)
- `security-reviewer — Kimi K3 subagent executing agents/security-reviewer.md · approve` (m4 verified)
- `ux-reviewer — Kimi K3 subagent executing agents/ux-reviewer.md · n/a at P2` (D1 lens owed at PDR; findings recorded there)

**Reviewers (this pass):**
- `architect — Kimi K3 session executing agents/architect.md · iterate-to-refine` (F1, F2, F3, m1, m2, m3)
- `qa-reviewer — Kimi K3 session executing agents/qa-reviewer.md · iterate-to-refine` (F3 co-owned, m5)
- `security-reviewer — Kimi K3 session executing agents/security-reviewer.md · approve` (C6 fired; one LOW, m4; no HIGH)

> If gate = `approve` and every line is ✓, the Detail below is reference. Any blocker/⚠ → read the matching part.

---

## Detail (reference)

### Findings
**Author dispositions (2026-10-23)** — applied under the standing authorization answering the `iterate-to-refine` gate (amendments `LED-2026-10-23-hygiene-batch.5`–`.8`); the reviewers re-check each at the second P2 pass. `fixed` = author-side disposition complete; `open` = carried to its owning station, named in the row.

| ID | Reviewer | Severity | Area / Req | What | Recommendation | Status |
|----|----------|----------|------------|------|----------------|--------|
| F1 | architect | major | Premise 5 / LLR-Q2.1.3 / LLR-Q2.1.1 (Q2 caps) | Premise 5 claims repo maxima "largest generated sidecar 696,062 B / 6,000 nodes … no 'dense' shape exists in this repo" (`01-requirements.md:183`); the tracked tree falsifies both: `.dev-flow/2026-10-10-perf-batch/evidence/perf0b-ws-aa0oz3mw/p_nodos.yml` is committed at 1,369,835 B and parses to **12,000 nodes** (re-measured by this review, `env -u NO_COLOR -u TERM`, 2026-10-23; its sibling `perf0b-ws-9aj_nwaw` identical; `p.mmd` 523,879 B > the claimed "largest .mmd 222,002 B"). The "16.7× headroom both ways" derivation (LLR-Q2.1.3 `:360`, ledger `LED-….1`, PLAN.md:113) is really 8.3× over the largest tracked shape; LLR-Q2.1.1's "11.5× the largest generated sidecar" (`:338`) is really 6.1×. R1's own UNLESS clause spoke of "a measured real map or perf fixture" exceeding 1/10 — a 12,000-node perf workspace was not measured. Same premise's "yaml-depth 3" for `anidado` measures 4 by the prescan's own CollectionStart counting. The cap VALUES survive (100,000 ≥ 8.3× over 12,000; real maps ≤ 8 nodes confirmed) — the evidential record does not. | P1 amendment: re-measure including the tracked perf-evidence workspaces OR name the measurement population precisely (loadable workspaces: `fixtures/`, `maps/`, `tests/goldens/`) and declare `.dev-flow` evidence excluded with the reason; re-state the headroom arithmetic; re-check R1's ≥10× rule against the largest shape of the declared population (12,000 → 100,000 fails ≥10×; either the caps move or the rule is re-ruled). | fixed (author) — premise 5 re-measured over the full committed population incl. `perf0b-ws-*` (largest = 12,000 nodes / 11,999 edges); caps retained 100,000/100,000 at 8.3× under the ≥5× floor re-ruled by the standing authorization; amendment `LED-…batch.5` (asserting test `test_count_caps`, mutant M-Q2-4) · second pass 2026-10-23: verified (evidence/recheck-architect.md §F1) |
| F2 | architect | major | §2.8 fork preconditions / §6 worksheet / Q2 lane | The mandatory C-52 table (`01-requirements.md:203`) lists L2 = `store.py`, `diff.py`, `import_csv.py` — "Intersection: ∅ … each ≤ 4 SOURCE files"; the §6 worksheet (ARCHITECTURE.md:295) and PLAN.md:99-104 repeat "L2 = 3 source files". But the batch's own ARQ commitments put the NEW bounded content reader in `mapper/osopen.py` (ARCHITECTURE.md:65 "joins the exposes", :121, :162, :165; R-015; the contract's own §4 C-36 preamble `:317` names "the osopen reader"). L2 therefore edits FOUR source files, and the mandatory disjointness evidence is incomplete as written. Decisions unaffected (4 ≤ 4; L1/L3 never touch `osopen`) — the mandatory record is wrong. | P1 amendment: add `mapper/osopen.py` to L2's set in §2.8 condition 2, the §6 worksheet (count 3 → 4) and the PLAN roadmap; re-state the intersection evidence over the corrected sets. | fixed (author) — `mapper/osopen.py` added to L2's set in §2.8 condition 2, the ARQ §6 worksheet (3→4) and PLAN.md; amendment `LED-…batch.6` (asserting pin `test_arch_osopen_callers.py`) · second pass 2026-10-23: verified (evidence/recheck-architect.md §F2) |
| F3 | qa-reviewer | major | LLR-Q3.1.2 / HLR-Q3.1 / AT-115 (Q3 sweep) | The sweep's pass threshold is "6 × 5 × \|states\|" over "the recorded state matrix" (`01-requirements.md:402`, `:284`) — but no state matrix is recorded in any batch artifact (grep over the contract, PLAN, ledger: the only two mentions are these two references). The renderer roster is C-31-derived, yet the STATE dimension — the sweep's boundary input (folded/empty/orphan are named only in the boundary catalog) — is left undetermined, so AT-115's completeness cannot be judged at P2 and a trivially small state set would pass vacuously. | P1 amendment: record the state matrix (which graph/view states per renderer, derived from code per C-31 where possible, else enumerated with its source) and bind \|states\| to it. | fixed (author) — state matrix recorded at `design/state-matrix.md` (\|states\| = 4: plain/folded/empty/orphan, code-derived per C-31) and bound in HLR-Q3.1 / LLR-Q3.1.2 (6 × 5 × 4 = 120); amendment `LED-…batch.7` (asserting test `test_sweep`, mutant M-Q3-1) · second pass 2026-10-23: verified (evidence/recheck-qa.md §F3) |
| m1 | architect | minor | PLAN.md:65 | "3 US / 6 HLR / 12 LLR" — the contract holds 11 LLRs (1+3+1+1+2+3 across the six HLRs). Traceability-record drift only; the contract itself states no count. | Correct the count at the next PLAN update. | fixed (author) — PLAN.md count corrected 12 → 11 LLR · second pass 2026-10-23: verified (evidence/recheck-architect.md §m1) |
| m2 | architect | minor | Premises 9 and 12 (citations) | Premise 9 (`01-requirements.md:187`) cites `docs/ARCHITECTURE.md:197` and `:211` for the frozen `Canvas` rows; the actual rows are :200 (§4 interface row) and :214 (LANDED row). Premise 12 (`:190`) cites `mapper/store.py:37-53` for the reserved-name refusal; the operative check is at :58-61 (`_RESERVED_NAMES` at :28-31). Substance verified true; the line ranges miss. | Re-cite on the next contract touch. | fixed (author) — premise 9 re-cited `docs/ARCHITECTURE.md:200` / `:214`; premise 12 re-cited `mapper/store.py:28-31` / `:58-61` · second pass 2026-10-23: verified (evidence/recheck-architect.md §m2) |
| m3 | architect | minor | LLR-Q3.2.1 statement (`:412`) | The normative sentence records an overprint for "every in-bounds write whose cell already holds a different alphanumeric character" — it does not carry ruling R4's second limb (the NEW character must also be alphanumeric; `:296`, `:413` rationale). Read alone, the statement records old-alnum→space as an overprint; R4 says it is not one. Rationale carries the right definition, so this is wording slack, not contradiction. | Fold "…by a write whose character is also alphanumeric" into the statement at the P1 pass. | fixed (author) — LLR-Q3.2.1 statement now requires the written character to also be alphanumeric (R4's second limb); amendment `LED-…batch.8` (asserting test `test_events`, mutant M-Q3-2) · second pass 2026-10-23: verified (evidence/recheck-architect.md §m3) |
| m4 | security-reviewer | minor (LOW) | LLR-Q2.1.1 (`:337`) | The byte cap is "re-checked on the read bytes" — i.e. the whole file is read into memory before refusal. The oracle reads capped (`f.read(MAX_MAP_BYTES + 1)`, `qm:src/quickmap/model.py:498-505`) and never holds more than cap+1 bytes. A multi-GB drop on the workspace is a local-memory exhaustion the oracle's shape avoids for free. LOW: single-operator local tool, no remote surface. | Prefer the oracle's capped read (read cap+1, refuse on overflow) in the Phase-3 design; no P1 change needed — note it for PDR. | fixed (author) — adopted in the PDR design proposal: the bounded reader reads at most cap+1 bytes and refuses on overflow (oracle shape `qm:src/quickmap/model.py:498-505`); Phase 3 implements · second pass 2026-10-23: verified-adopted (evidence/recheck-security.md TASK A) |
| m5 | qa-reviewer | minor | HLR-Q2.1/Q2.2 acceptance (`:240-241`, `:256`) | The named shipped surface for AT-109…114 is "`MapStore.load` → the app's existing error toast path". The store API is an internal symbol; Layer B is satisfied only if the ATs observe the refusal through the running screen's toast (as the observable outcome states), not by catching `MapStoreError` at the API alone. | At Phase 3, drive at least one arm per refusal kind through a screen and assert the toast text; keep store-level arms as TCs. | open — carried to Phase 3 (owning station: the Q2 increment gate): at least one arm per refusal kind driven through the running screen asserting the toast text; consumers verified as `screens/construct.py:57` + `screens/common.py:_save_or_toast` (app.py does NOT consume MapStoreError); arms named as proposed cases in `design-proposal.md` §5 · second pass 2026-10-23: open-carry confirmed (evidence/recheck-qa.md §m5) |
| m6 | qa-reviewer | minor | HLR-Q2.3 / US-Q2-001 | "Discharged by the existing suite (e.g. `tests/test_store.py` reserved-name arms — named at Phase 3 reconciliation)" defers naming the pinning tests. Acceptable for unchanged behaviour, but the reconciliation debt should be visible at the Q2 gate, not discovered there. | Name the existing device-name arms in the Q2 increment packet's test ledger. | open — carried to Phase 3 (owning station: the Q2 increment packet's test ledger): arms named at PDR per `design-proposal.md` §5 — `tests/test_seed_safety.py` `BAD_NAMES` + refusal arms, `tests/test_inc9n.py` refusal-before-open arms (the contract's `test_store.py` example was verified absent); re-run owed at the Q2 gate · second pass 2026-10-23: open-carry confirmed (evidence/recheck-qa.md §m6) |

**Second-pass re-check (2026-10-23)** — each disposition re-verified against the files and the code by the named role; full evidence in `evidence/recheck-*.md`.

| ID | Second-pass verdict | Evidence (spot) |
|----|---------------------|-----------------|
| F1 | **verified** | re-measured 2026-10-23: `perf0b-ws-aa0oz3mw/p_nodos.yml` = 1,369,835 B / 12,000 nodes, `p.mmd` 523,879 B / 11,999 edges; siblings 12,000 and 500 nodes; arithmetic 8.33× / 6.12× checks; anidado yaml-depth 4 by CollectionStart scan; stale figures (`696,062`, `11.5×`) gone from the amended clauses; ledger .5 matches |
| F2 | **verified** | `osopen.py` in §2.8 condition 2 (`01-requirements.md:203`), `docs/ARCHITECTURE.md:295` (count 4), PLAN.md :36/:100/:113-114; intersection ∅ re-stated; ledger .6 matches |
| F3 | **verified** | `design/state-matrix.md` records 4 code-derived states; HLR-Q3.1 (`:284`) / LLR-Q3.1.2 (`:402`,`:405`) bind 6×5×4=120 to it; every cited derivation line holds (layered.py:660-661/:158-168/:382-387, outline.py:147-149/:214-218, radial.py:177-178, lane.py:117-119/:181-185/:326-328); vacuous-pass route closed; ledger .7 matches |
| m1 | **verified** | PLAN.md:65 says 11 LLR; independent count of `### LLR-` headings = 11 |
| m2 | **verified** | `docs/ARCHITECTURE.md:200`/`:214` hold the Canvas rows; `mapper/store.py:28-31` = `_RESERVED_NAMES`, `:58-61` = the operative refusal |
| m3 | **verified** | LLR-Q3.2.1 statement (`:412`) carries R4's second limb; ledger .8 matches |
| m4 | **verified** | `design-proposal.md:172` mandates the capped cap+1 read everywhere a file is read; grep over the design shows no uncapped read reintroduced |
| m5 | **open — carry verified** | proposal §5 carries the screen arm; `MapStoreError` consumed at `screens/construct.py:57` + `screens/common.py` (`_save_or_toast` :217), zero hits in `app.py`; re-run owed at the Q2 gate stands |
| m6 | **open — carry verified** | pins confirmed: `test_seed_safety.py:42` (BAD_NAMES incl. CON), `:230-249`; `test_inc9n.py` `DEVICES` :59-62 + arms :257-283; `test_store.py` grep = zero hits (original example wrong, correction right) |

**New findings (second pass, contract record):** two contract-record minors from the re-check; the PDR-lens findings of the same pass (N3, S1, n1–n4, F-UX-1, F-UX-2) are recorded with their dispositions in `design/PDR-2026-10-23-hygiene-batch.md` §B. Minors never force a return edge; none reopens a first-pass verdict.

| ID | Reviewer | Severity | Area / Req | What | Recommendation | Status |
|----|----------|----------|------------|------|----------------|--------|
| N1 | architect | minor | `01-requirements.md:601` · PLAN.md:143 | Stale "696 KB perf sidecar" survives the F1 re-measurement (no such committed file; the perf sidecars are 1,369,835/1,357,836/55,839 B); PLAN.md:202's ledger row still reads "largest measured = 6,000 nodes" without the re-measurement note PLAN.md:127 carries | Correct at the next contract/PLAN touch (trunk, before the L2 gate at the latest) | fixed at the PDR seal (trunk record fix, same unit): contract :601 + PLAN prescan row re-figured; PLAN :202 probe row carries the re-measurement note |
| N2 | architect | minor | Premise 5 (`.mmd` maxima) | "largest .mmd outside .dev-flow = wide6000.mmd 215,973 B" is falsified by `tests/goldens/perf/at076_saved_wide6000_after_add_child.mmd` (222,002 B) — inconsequential to headroom, a precision defect in the re-measured premise | Re-cite at the next contract touch | fixed at the PDR seal (trunk record fix, same unit): premise 5 evidence cell re-cited to the 222,002 B file |

**A worked example — text to read, never rows of your record.** It sits in a fence so that nothing has to be deleted: a row copied out of it would claim a finding nobody raised. Write your own rows in the table above.

```text
| *(example)* F1 | architect | blocker / major / minor | | | | open / fixed |
```

### shall / should check
> Any modal `should` / `debería` inside an HLR/LLR statement is a writing error → blocker.

✓ clean — `grep -n "should\|debería" 01-requirements.md` returns zero hits; all 6 HLR and 11 LLR statements use `shall` (18 occurrences document-wide).

### Two-layer acceptance review (blockers)
> (a) every story has a black-box `AT`; (b) every output-producing requirement names its observable deliverable + observation method; (c) BOTH traceability chains complete (behavioral US→AT→outcome + functional US→HLR→LLR→TC); (d) each `AT` is genuinely black-box — drives the surface, asserts the outcome, references NO internal symbol.

| Story / Req | (a) AT present | (b) deliverable+method named | (c) both chains | (d) black-box pure | Status |
|-------------|----------------|------------------------------|-----------------|--------------------|--------|
| US-Q1-001 | yes (AT-108) | yes — painted screens observed headless via `run_test()`, the surface the operator watches | yes — US→HLR-Q1.1→LLR-Q1.1.1→planned TC; US→AT-108→outcome | yes — drives the real app, harvests painted segment styles | ✓ |
| US-Q2-001 | yes (AT-109…114; HLR-Q2.3 mints none — unchanged behaviour pinned by the existing suite, m6) | yes — refusal toast naming limit + map id; session stays live | yes — US→HLR-Q2.1/2.2/2.3→LLR-Q2.1.1-3/Q2.2.1/Q2.3.1→planned TCs | yes with reservation m5 — observation point must be the screen toast, not only the store API | ✓ (m5, m6) |
| US-Q3-001 | yes (AT-115, AT-116) | yes — sweep verdict naming renderer/size/state; audit events in test output; bytes identical | yes — US→HLR-Q3.1/3.2→LLR-Q3.1.1-2/Q3.2.1-3→planned TCs; F3: the state dimension of AT-115's threshold is unrecorded | yes — renderer roster exercised as screens/export consume it | ✓ (F3) |

### Supersession census (change-first)
> Planned new/moved/edited files checked against EVERY guard family (behavioral-placeholder · structural/placement · AST-composition · frozen-module). State reservations; the increment gate is the completeness guarantee, not this census.

Planned edited source files × guard families, run against the live tree:

- `mapper/app.py` (L1) — NO_COLOR grep over `mapper/` and `tests/`: zero hits in `mapper/` (premise 2 confirmed); the only behavioural pin is `tests/test_help_scope.py:78-94` (fixture deletes the var) + `:247-274` (legend-scope pin), which the contract already subsumes (HLR-Q1.1 executed-verification note). Frozen-module family: `app` is not signature-pinned for this surface.
- `mapper/store.py`, `mapper/diff.py`, `mapper/import_csv.py` (L2) — read sites verified at `store.py:697-706` (uncapped `read_text` + bare `safe_load`, `RecursionError` caught after the fact at :707, bomb comment :715-718), `diff.py:51-59` (`git show` → `safe_load`, only `YAMLError` caught — a depth bomb through git show escapes untyped TODAY; Q2's caps close it via IFC `q2-map-load`), `import_csv.py:39` (unbounded read). Refusal surface exists: `MapStoreError` messages name map id / file NAME only, never a path (`store.py:690,703,726`).
- `mapper/osopen.py` (L2 — **the set the contract omits, F2**) — AST-composition guard `tests/test_arch_osopen_callers.py` derives the importer allow-list; the ARQ amendment already schedules its same-increment amendment (ARCHITECTURE.md:65, :170). Device-name refusal verified at `osopen.py:107` (per-component `is_reserved`) and `store.py:58-61`.
- `mapper/canvas.py` (L3) — frozen-module family: B-44 pin `tests/test_a3_census.py:658-674` asserts `["self","w","h","tones","fallback"]` and the map row; amendment scheduled in the same landing (LLR-Q3.2.1 traceability, §6 worksheet). Structural/placement: construction sites exactly 3 — `lane.py:199`, `layered.py:693`, `radial.py:184` (grep `Canvas(` over `mapper/`), matching premise 7 and the `test_canvas.py:206-213` sweep scope. Behavioural byte-identity family: `MASTER_LEGACY_DIGESTS` (12 keys verified, `test_repair_depth.py:109`, fingerprint :252-254) and 16 perf render goldens (`tests/goldens/perf/render/`, gated at `test_perf_paint_clip.py:172`) — held un-re-baselined by LLR-Q3.2.2.
- Reverse census (C-26, B1): PLAN §Triggers lists the 5 existing test files asserting `Canvas` symbols; per-increment reverse census declared in the increment plan; condition-3 crossed census is PDR-gated (ruling R5) — owed before lanes fork, correctly not discharged here.

Reservations: F2 (the L2 set this census ran over is the CORRECTED one, including `osopen.py` — the contract's own table must catch up). **Best-effort + gate-confirmed — not stamped complete;** the L1/L2/L3 increment gates are the completeness guarantee.

### Security review summary

`security-reviewer — Kimi K3 session executing agents/security-reviewer.md · approve` — trigger family C fired via **C6** (the batch's new code reads operator-supplied files: the prescan). Scope reviewed: `01-requirements.md` §§2-4, §6.3; the current read sites (`store.py:680-740`, `diff.py:40-66`, `import_csv.py:39`, `osopen.py:95-113`); the oracle controls (`qm:src/quickmap/model.py:39-45,461-475,485-521` — verified line-by-line: 8 MiB / 64 / 10,000 / 50,000 / 4 MiB / 8 KiB constants and the iterative, anchor-refusing, capped-read design are exactly as cited).

- **Attack surface:** three existing filesystem read sites, all to be bounded (byte caps, iterative non-recursive prescan, NUL probe); no network, no auth, no secrets, no new dependencies, no destructive surface. `§6.3`'s scan answers (`session`/`expose` = vocabulary collisions) checked against the text — accurate.
- **Privacy posture:** refusal messages name the limit and the map id, never a path — confirmed as the existing `MapStoreError` discipline (`store.py:690,703,726`); contract §2.4 makes it normative ("SHALL NOT … leak paths").
- **Findings:** one LOW — **m4** (uncapped full read before the byte re-check; oracle reads cap+1). No HIGH, no MEDIUM. `devflow-scan-spec.py` flags answered in §6.3 stand.
- **Verdict:** OK to ship from the security lens — no HIGH, and the single LOW is a Phase-3 design note, not a gate item.

### Evidence checklists (full) — architect · qa-reviewer · security-reviewer
> Attach each reviewer's completed evidence checklist (items in their agent files), ✓/✗ + one-line evidence.

**architect — Kimi K3 session executing agents/architect.md:**
- [x] Constraints stated explicitly — §2.4 (caps headroomed over measured repo data · ≤4 source files · env-stripped test runs); F1/F2 are the two constraint-evidence defects found.
- [x] 2+ alternatives where a real decision exists — R-015 (ARCHITECTURE.md:274) weighs reader-in-new-module / reader-in-store / injection shapes and records what would re-open each; ledger `.3` records the Q1 mechanism alternatives (`main()` vs constructor vs filter override).
- [x] Non-applicable constraints marked n/a — boundary balancing declared not-checkable (IFC Part B note, `:502`).
- [x] Recommendation tied to constraints — caps derived from measured maxima (but see F1: the measurement population).
- [x] Risks listed — §6.3 (headroom, prescan cost, diff.py contract, C6 posture) + PLAN watch-items.
- [x] Cost/latency estimated — prescan's added pass declared and scheduled for measurement at the L2 gate (`§6.3`, planned).
- [x] Diagram/flow for non-trivial flow — IFC C-54 flows `q1-env-colour`, `q2-map-load`, `q2-csv-import`, `q3-render` with owners (`:446-500`).
- [x] What would change the recommendation — R-015's last column; §6.3 cap-amendment rule.
- [x] Two-layer requirements — both chains present for all 3 stories (table above); AT-108…116 all assigned.

**qa-reviewer — Kimi K3 session executing agents/qa-reviewer.md (mode: plan):**
- [x] Acceptance criteria in trigger→response form — EARS `When … shall …` statements + observable-outcome blocks per HLR.
- [x] Explicit Expected — numeric pass thresholds on every HLR/LLR (cap±1, depth 64/65, NUL at byte 0 and 8,191, 10,000-deep refusal < 5 s, exactly-h/at-most-w).
- [x] Edge cases — QC-3 boundary catalogs on every HLR/LLR: empty sidecar `{}`, cap−1/cap, NUL at both probe ends, depth boundary, out-of-bounds space write, empty roster guard.
- [x] Regression checklist — byte-identity goldens held un-re-baselined (LLR-Q3.2.2), subsumed legend pin reconciled in L1, existing device-name suite pinned (HLR-Q2.3).
- [x] Exit criteria — §5.2 (100% LLR coverage, 0 blocker fails, full suite under `env -u NO_COLOR -u TERM`, no re-baselining, counterfactual transcripts).
- [x] No real PII / secrets — A-110 guard honoured; refusals never leak paths.
- [x] Mode declared — plan mode; every verification node marked "provisional — Phase 3" = `planned`, none silently blank.
- [x] Layer B black-box — every output-producing story's deliverable observed through a shipped surface with boundary + negative evidence; reservation m5 (Q2's observation point) and F3 (state matrix) recorded.
- [x] Bidirectional surface-reachability — every named input dimension (bytes, depth, anchors/aliases, node/edge counts, NUL, size) and output (toast, sweep verdict, audit events) is exercised through the named handler; F3 is the one undetermined input dimension.
- [x] No unfilled template placeholders — no `<...>`, no unassigned ids in the contract.

**security-reviewer — Kimi K3 session executing agents/security-reviewer.md:**
- [x] Each finding has what · where · why · recommendation — m4 (the only finding).
- [x] Each finding has a severity — m4 = LOW.
- [x] No secret values in this output — none present; none exist in scope.
- [x] Verdict explicit — OK to ship; zero HIGH, so no `BLOCK-UNTIL` owed.
- [x] New tool/integration scope — n/a, none added (C3 not fired; confirmed against the contract and the ARQ amendment).
