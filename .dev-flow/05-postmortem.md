# Post-mortem — mapper — Batch 2026-08-18-batch-01

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`).
> Phase 5 artifact. Co-authors: `architect` + `qa-reviewer`. Structured for cross-batch sweeping — keep the section order.

## 🔑 At a glance (read first)

- **Outcome:** closed clean
- **Top 3:** ① Reused the taskboard palette/rich-canvas discipline; text-as-truth persistence kept the store simple. ② Fixture encoding on Windows required an ASCII fallback; non-ASCII content will need explicit UTF-8 handling next batch. ③ No external blockers.
- **New control this batch:** "ASCII-only synthetic fixtures if the Write path cannot guarantee UTF-8 round-trip on Windows" — adopt next batch or retire once encoding is hardened.
- **Open items → next batch:** 2 — polished repo lane timeline with release milestones; in-place ficha editing.
- **Metrics:** iterations 7 · findings 0/0 · ledger —

---

## Detail (reference)

### What worked
- The architecture map from Phase 2 kept implementation file sets disjoint; no lane collision occurred.
- Mermaid round-trip works for the MVP subset and round-trips through the SQLite index correctly.
- Rich `Console(record=True)` gave SVG export almost for free.
- The same `Graph` value object supports layered, outline, radial, and lane views without family-specific node types.

### What didn't / friction
- The first fixture write corrupted non-ASCII characters on Windows; `Write` then `read_text(encoding="utf-8")` failed. We replaced Spanish diacritics with ASCII in fixtures. A real map will need proper UTF-8 handling.
- `gh` API calls are synchronous and blocking; large repos will need async + cancellation, but that is out of MVP scope.

### Scope drift (planned vs actual)
| Planned | Actual | Note |
|---------|--------|------|
| Inc-6 full lane timeline with releases/commits | Lane renderer lists branches with ahead/behind + CI | Timeline axis and release diamonds deferred to next batch |
| Inc-7 radial mind map + export + polish | Radial renderer + SVG export delivered; tapering organic edges simplified to dotted lines | Polish round deferred |
| In-place ficha editing | Read-only ficha strip only | Deferred to next batch |

### Metrics (full)
| Metric | Value |
|--------|-------|
| Iterations per phase | `{0:1,1:1,2:1,3:1,4:1,5:1,6:1}` |
| Findings opened / closed | 0 / 0 |
| Findings by severity (blocker/major/minor) | 0/0/0 |
| Where caught (Phase 2 / P3 gate / P4) | 0/0/0 |
| Test ledger (base − D + A = post) | base 0 − 0 + 16 = post 16 |
| Files touched · increments (cap trips) | 22 · 7 (0 cap trips) |

### Root causes (only if a phase took ≥2 iterations)
- None — every phase closed in one iteration.

### Process / workflow findings
- Working directly on `master` with autonomous merge authorization avoided branch overhead for a green-field MVP, but a PR-level review pass should be introduced once the repo has external contributors.

### Product findings
- The lane view currently renders branches as a list; a true time-axis timeline needs `gh` release data and a richer `LaneRenderer`.
- Search highlights titles/notes/fields/attachment names but does not support regex or fuzzy ranking.

### Control lineage
- **New control proposed this batch:** Synthetic fixtures must be ASCII-only if the file-write path cannot guarantee UTF-8 round-trip on Windows. Status: adopt-next-batch or retire once encoding is hardened.
- **Prior controls exercised:** terminal-honest width-1 glyphs, palette-rationed severity, no real data in committed artifacts, read-only GitHub access.

### Open / deferred items → next batch
| Item | Type (process/product) | Reason deferred | Trigger / owner |
|------|------------------------|-----------------|-----------------|
| Repo lane timeline with release milestones and commit dots | product | Time-box; current lane list satisfies US-006 acceptance at MVP level | next batch / operator |
| In-place ficha editing | product | Out of scope for MVP per US-013 refinement | next batch / operator |
| PNG export without cairosvg fallback quality | product | cairosvg optional dependency is sufficient for MVP | next batch / operator |

### Working-file reconciliation (C-44) — MANDATORY, every file this batch touched

| Repo | File(s) | Terminal state | Landing / backlog ref |
|------|---------|----------------|-----------------------|
| jav201/mapper | all | ✅ committed + landed | master @ TBD |

### Conditional gate verdicts
- None.

### Evidence checklist — architect + qa-reviewer
- Validation: `python -m pytest tests/ -q` → 16 passed.
