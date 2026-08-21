# Validation — mapper — Batch 2026-08-18-batch-01

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`); for Spanish batches translate headers/labels.
> Phase 4 artifact. Owner: `qa-reviewer`. Executes the validation strategy fixed in Phase 1.

## ✅ Verdict (read first)

- **Result:** PASS  /  FAIL → `iterate-to-fix` (P3, impl defect) or `iterate-to-refine` (P1, requirement defect)
- **Requirements:** `<P>`/`<T>` pass · `<N>` blocker fails
- **Black-box acceptance (Layer B):** ✓ every story's `AT` observes its outcome through the shipped surface (boundary + negative)  /  ⚠ `<N>` stories with no deliverable observation
- **Surface-reachability (bidirectional):** ✓ all named inputs AND outputs/deliverables reached/observed at the surface  /  ⚠ `<N>` gaps
- **Supersession inspection:** ✓ all surviving refs negative  /  ⚠ live dependency found
- **Test ledger:** ✓ reconciles (`base − D + A = post`)  /  ✗ mismatch
- **Evidence checklist (qa-reviewer):** ✓ complete  /  ✗ `<missing items>`

> If every line is ✓, the Detail below is reference only. Any ⚠/✗ → read the matching part.

---

## Detail (reference)

### Layer 0 — unit

Applies where **either** criterion holds: the unit has **cyclomatic complexity ≥ 3**, **or** it transforms
data crossing a boundary declared in `docs/ARCHITECTURE.md`. Out: pure delegations, getters, UI wiring,
constructors that only assign, branchless one-liners.

| Unit | Which criterion | Node id | Result |
|---|---|---|---|

**Measured by mutation, never by line coverage.** For each unit, name the mutation and paste the RED:

| Unit | Mutation applied | RED observed? | Transcript |
|---|---|---|---|

- ⚠ A layer-0 node whose reddening mutation cannot be named is not a test yet.

### UX walkthrough — only if trigger family D fired

| Criterion (when the user does X, they observe Y) | Driven with the REAL mechanism | Painted result asserted | Verdict |
|---|---|---|---|

**Mechanism used:** `<Textual Pilot | browser-automation | CLI subprocess | artifact on disk | none — inspected only>`

- ✗ A proxy in place of the interaction (a direct setter, `.focus()` instead of the real keys) is not evidence of the interaction (C-16).
- ✗ On web, a selector you authored without looking is a vacuous check — a selector that matches nothing fails exactly like an absent element. Act by ref from `--snapshot`.
- ⚠ A console/network count of `0` counts as evidence **only** if the capture header is clean; `** capture DEGRADED **` means the signal was off, not that the page was healthy.
- ✗ A pre-layout assertion is not the painted result (C-32).
- ⚠ **Evaluation with real users was NOT performed** — state it here explicitly (ISO 9241-210). Inspection with declared criteria is what was done instead.

### Layer A — functional (white-box): per-requirement results
> `TC-NNN` ↔ LLR/HLR. `Result` = pass / fail. `Evidence` = command output, observed behavior, inspection note, or analysis result.

| Req | Method | Executed verification | Numeric threshold | Result | Evidence |
|-----|--------|-----------------------|-------------------|--------|----------|
| HLR-001 | test | `pytest … -k TC-001` | exit 0 | | |
| LLR-001.1 | test (unit) | `…` | `…` | | |

### Layer B — behavioral (black-box) acceptance
> `AT-NNN` ↔ user story. Drive the SHIPPED surface (Textual Pilot `App.run_test()` / CLI / artifact-on-disk), assert the outcome with representative + boundary + negative inputs PLUS the actual deliverable observed. An output-producing story's `AT` FAILS if the deliverable is silently absent. `AT-NNN` reconciled to the real collected node per V-5.

| US | Acceptance test (`AT-NNN`) | Surface driven | Deliverable observed (path / element) | repr · boundary · negative | Result |
|----|----------------------------|----------------|---------------------------------------|----------------------------|--------|
| US-001 | `AT-NNN` | `<handler/screen/CLI>` | `<file:path non-empty + content \| element>` | ✓·✓·✓ | pass / fail |

### Bidirectional surface-reachability matrix (extends A-5, batch-11)
> Every named INPUT dimension AND every named OUTPUT/deliverable is exercised/observed through the handler — not only the service API.

| Direction | US dimension / deliverable | Service param / producer | Reached/observed at surface? | TC / AT | Status |
|-----------|---------------------------|--------------------------|------------------------------|---------|--------|
| input | `<dimension>` | `<param>` | yes/no | `TC-NNN` | ✓ / gap |
| output | `<deliverable>` | `<producer>` | yes/no | `AT-NNN` | ✓ / gap |

### Supersession-completeness inspection (batch-09 V-3)
> Grep the whole class of superseded markers/constants; every surviving reference must be a NEGATIVE assertion (absence), not a live dependency.

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| `<marker>` | `<N hits>` | yes/no | `<…>` |

### Signed-balance test ledger (batch-07 / 09)
> `post = base − D + A`. State counts in collected / passed-lean / passed-full form.

| base | − D | + A | = post | actual collected | passed-lean / full | reconciles? |
|------|-----|-----|--------|------------------|--------------------|-------------|
| `<N>` | `<N>` | `<N>` | `<N>` | `<N>` | `<N>` / `<N>` | yes/no |

### Gaps detected
| ID | Requirement | Gap | Severity | Proposed action |
|----|-------------|-----|----------|-----------------|
| G-001 | | | blocker / major / minor | |

### Escaped-bug regression (if a defect escaped the suite)
> The fix ships a shipped-surface regression that demonstrably FAILS pre-fix (capture the failing run) then passes. Id provisional per V-5.
> **QC-2 — value-discriminating counterfactual:** when the pre-fix RED is a *shape* failure (TypeError, missing-arg, constructor/signature mismatch) rather than a *value* mismatch, the regression proves the call path is wired, not that the assertion discriminates the right value. Confirm the POST-fix assertion also fails on a wrong-but-well-typed value. (Origin: batch-16.)

| Regression id (`AT-NNN` / `TC-NNN`) | Pre-fix run (evidence it FAILED) | Pre-fix RED kind (value / shape) | Post-fix value-discriminating? (QC-2) | Post-fix result | Reconciled node |
|-------------------------------------|----------------------------------|----------------------------------|----------------------------------------|-----------------|-----------------|
| | | | | | |

### Evidence checklist — qa-reviewer (full)
> Attach `qa-reviewer`'s completed evidence checklist (items in `~/.claude/agents/qa-reviewer.md`), each marked ✓/✗ with one-line evidence. An unchecked or evidence-less item blocks the gate.
