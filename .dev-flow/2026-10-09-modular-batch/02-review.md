# Review — mapper — Batch 2026-10-09-modular-batch

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`).
> Phase 2 artifact. Reviewers (in parallel): `architect` ∥ `qa-reviewer` ∥ `security-reviewer` by trigger family C (always in `full`).

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/docs/review-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

## ✅ Verdict (read first)

- **Gate:**
  - **Round 1** → `iterate-to-refine` → Phase 1 (4 blockers).
  - **Round 2** → `approve` → PDR, after the round-2 fixes were applied and the spine was verified by a probe.
- **Out-of-scope findings:** none.

- **Findings (round 1):** 4 blocker · 6 major · 8 minor. The orchestrator ruled on the four blockers (below), and Kimi K2 applied all of them in P1 iteration 1 (ledger `LED-2026-10-09-modular-batch.*`).
- **shall/should check:** ✓ clean (`shall` in Statements only).
- **Two-layer (blockers):** ✗ in round 1:
  - US-002: the parity capture was undefined (QA-1).
  - US-003: AT and LLR shared one node (QA-3).
  - HLR-MOD.7: no AT.
- **Census (change-first):** ⚠ in round 1. The patch census covered 2 of 8 patch targets (ARCH-2), and class enumeration by `__module__` was not a census category (ARCH-3).
- **Security:** ✓ not run. Trigger family C did not fire; the scan flag `session` is a false positive (§6.3).
- **Evidence checklists (architect / qa):** attached below.

---

## Detail (reference)

### Findings — round 1

| ID | Reviewer | Severity | Area / Req | What | Recommendation / ruling | Status |
|----|----------|----------|------------|------|------------------------|--------|
| ARCH-1 | architect | blocker | increment cut, LLR-MOD.6.2/7.1 | `HomeScreen` builds `MapScreen` 5× (`app.py:1004,1023,1032,1052,1108`) and `_ImportPreviewScreen` 1× (`:1170`). No legal import edge exists while `MapScreen` is in `app.py`, or after B0 under the §3 rules. | **Ruling:** sibling screens import `MapScreen` from `mapper.screens.map`, never from `mapper.app`. Spine reordered: A1 → A2 → A3 → A5a (NavigationModel) → B0 → A6 → A7 → A5b → A4 → B1…B11 → B12. | applied in iteration 1 |
| ARCH-2 | architect | blocker | HLR-MOD.3, F4 | Tests patch 8 globals of `mapper.app`, not 2: `save_svg`, `pan_extent`, `LayeredRenderer`, `preview_csv`, `SearchIndex` on top of `MAX_RENDER_NODES` and `refusal_sentence`. | **Ruling:** full patch census over every patch form. Each target is repointed to the module that reads it, in the increment that moves the reader. An AST guard checks that every patch target is read by its module. The F4 lazy-read design is dropped. | applied |
| QA-1 | qa-reviewer | blocker | AT-065, LLR-MOD.4.2 | The parity capture is undefined, and it would be taken after A1–A7 had already moved code. The "file missing" control is vacuous. | **Ruling:** a text golden captured at Inc-0 on the pre-move commit, at 118 and 87 columns, normalised (paths, time), with condition waits. Its path, commit and sha256 are recorded. The RED control is a mutated copy. | applied |
| QA-2 | qa-reviewer | blocker | US-002, LLR-MOD.4.1 | No per-method body identity. An identical body can still raise `NameError` in its new module. The scripted session misses edit/undo/draft/focus/open/pan. | **Ruling:** `tests/test_mod_bodies.py` checks per-method `ast.dump` against an Inc-0 baseline, plus an undefined-global check per new module. RED controls run on a tmp copy. | applied |
| ARCH-3 | architect | major | LLR-MOD.5.1 | `tests/test_keymap.py:214–220` enumerates classes by `__module__` over a hand list, so it silently scans less after the move. | Derive the module set, and add "class enumeration by `__module__`" as a census category | applied |
| ARCH-4 | architect | major | AT-065 | Feasibility: capture timing, `tmp_path`, `EXPORT_DECLARE_PAUSE` (`app.py:4337`). | Merged with QA-1 | applied |
| QA-3 | qa-reviewer | major | ATs | Layers conflated (AT = LLR node); HLR-MOD.7 has no AT. | Own node per AT; an HLR-MOD.7 chain | applied |
| QA-4 | qa-reviewer | major | structural tests | "Mutation at Phase 3" has no mechanism. | Checkers take a package root and RED on a tmp-copy mutant | applied |
| QA-5 | qa-reviewer | major | LLR-MOD.7.2 | The census script and JSON were not in the repo. | Committed to `spike/` (`bcf8384` parent) | fixed by the orchestrator |
| QA-6 | qa-reviewer | major | AT-066 | Overclaims "every bound key" from a single mixin pilot. | Narrow the claim, or pilot per mixin; the duplicate-handler RED goes to the disjointness guard | applied |
| QA-7 | qa-reviewer | major | AT-069 | The "no weaker" baseline was not recorded. | Pin per-file counts before Inc-0 | applied |
| ARCH-5 | architect | minor | dispatch guard | `@on`, `DEFAULT_CSS` and `BINDINGS` are silently ignored in a plain mixin (probed). | AST ban in `test_mod_dispatch` | applied |
| ARCH-6 | architect | minor | LLR-MOD.2.1 | The roster missed `AUTO_FOCUS` and `MINIMAP_ROWS`. | Derive it by AST | applied |
| ARCH-7 | architect | minor | AT-066 control | An idempotent handler may not change paint. | Merged with QA-6 | applied |
| QA-8 | qa-reviewer | minor | AT-070 | The grep missed `from mapper.app import`. | AST check of both forms | applied |
| QA-9 | qa-reviewer | minor | AT-067 | Patches an internal symbol by design. | Label it as a patch-surface contract AT | applied |
| QA-10 | qa-reviewer | minor | US-001 | `home.py`/`repo.py` were placed under `screens/map/`. | Correct the paths | applied |
| QA-11 | qa-reviewer | minor | premise 4 | The evidence lines lacked file prefixes. | Re-state them | applied |

**Verified sound by the architect (probed on Textual 8.2.8):**
- `on_*` and `action_*` dispatch from a mixin.
- `watch_*`/reactive work from a mixin.
- The CSS type-name selector `MapScreen` survives, and `isinstance` holds the same class object.
- The 1 `super()` stays in the core `__init__`.
- No `@on`, `compute_*` or `DEFAULT_CSS` is in use today.

### shall / should check
Clean.

### Supersession census (change-first)
Round 1 found two missing census categories: monkeypatch targets in every form (ARCH-2), and class enumeration by `__module__` (ARCH-3). Both are now premises with executed commands in the contract (iteration 1).

### Security review summary
Not run: family C did not fire. Scan flag `session` is a false positive (§6.3).

### Evidence checklists

**architect (round 1):**
- ✓ constraints stated;
- ✓ alternatives A/B/C (proposal §2), but ✗ for the ARCH-1 edge and the ARCH-2 patch policy (both ruled above);
- ✓ n/a rows marked;
- ✗ recommendation tied to constraints (the §3 rules contradicted the needed edges; fixed);
- ✓ risks listed, but ✗ R-4 under-scoped (fixed);
- ✓ cost/latency n/a;
- ✓ diagram n/a;
- ✓ what would change it;
- ✓ two-layer;
- ✓ shall/should.

**qa-reviewer (round 1, mode plan):**
- ✓ G/W/T style;
- ✓ explicit expected;
- ✓ edge cases (✗ unusual paths, fixed by QA-2);
- ✗ regression checklist (fixed: the body-identity plus the full suite at every gate);
- ✓ exit criteria;
- ✓ no PII;
- ✓ mode;
- ✗ Layer B (fixed: QA-3/QA-6);
- ✓ reachability;
- ✗ oracles that can go RED (fixed: QA-1/QA-4);
- ✓ no unfilled template.

### Round 2

- **qa-reviewer:** QA-1…QA-7 resolved (`01-requirements.md:396-414`, `:515-522`, `:293`, `:258`); the two-layer table is ✓ for all three stories. New minors: N-1 (baseline JSON path/hash), N-2 (the golden's `<…>` placeholders), N-3 (the scripted session reaches 6 concerns; covered by LLR-MOD.4.3). Gate: proceed. Size note: the contract is 68.5k characters against a 54k budget, and the candidates to trim are non-normative (refinement logs, rationale, §6.2/§6.3 prose). Recorded as a watch item, not trimmed in this pass.
- **architect:** ARCH-1…ARCH-7 resolved. The architect's AST probe found that MapScreen references none of home/repo/plug/import/construct. The new spine order raised 2 blockers and 2 lesser findings:
  - ARCH-8 (`MapHintLine` would still sit in `app.py` at B0) — fixed: it moves at A1 into `screens/common.py`.
  - ARCH-9 (`PlugRepoScreen` pushes `RepoScreen`, so A6 cannot precede A5b) — fixed: A5b runs before A6.
  - ARCH-10 (major: `LayeredRenderer` has two readers; the patch site names its reader `import_preview.py`) — fixed.
  - ARCH-11 (minor: `GitHubConnector.fetch` is a class-attribute patch and survives the move) — reclassified.
- **Fixes:** applied by two Kimi K2 units (contract + ledger LED .9; `ARCHITECTURE.md`).
- **Orchestrator verification:** `evidence/p2r2-spine-probe.transcript` checks every moved class against the reordered spine. It found **0 illegal edges**, and `app.py` keeps only `MapperApp` and `main`.
- **Verdict round 2:** `approve` → PDR. Self-approved under the standing authorization.
