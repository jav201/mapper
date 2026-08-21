# Traceability Matrix — mapper — Batch 2026-08-18-batch-01

> Two chains (per the Two-layer validation rule) — a story is complete only when BOTH exist:
> - **Functional (white-box):** User Story → HLR → LLR → `TC-NNN` → File:line.
> - **Behavioral (black-box):** User Story → `AT-NNN` → observed outcome through the shipped surface.
> Every row must be complete when closing the batch (phase 6). Incomplete rows = coverage gaps and must be listed in the gaps section.

---

## 1. Master table — functional chain (white-box)

| US | HLR | LLR | TC | File:line | Status | Notes |
|----|-----|-----|-----|-----------|--------|-------|
| US-001 | HLR-001 | LLR-001.1 | TC-001 | `NEW` | pending | Home screen doors |
| US-001 | HLR-001 | LLR-001.2 | TC-001 | `NEW` | pending | Initial screen push |
| US-001 | HLR-002 | LLR-002.1 | TC-001 | `NEW` | pending | Recent maps order |
| US-001 | HLR-003 | LLR-003.1 | TC-002 | `NEW` | pending | Keybinds for doors |
| US-002 | HLR-004 | LLR-004.1 | TC-003 | `NEW` | pending | Layered layout coords |
| US-002 | HLR-004 | LLR-004.2 | TC-003 | `NEW` | pending | Card rendering |
| US-002 | HLR-005 | LLR-005.1 | TC-004 | `NEW` | pending | Navigation model |
| US-002 | HLR-005 | LLR-005.2 | TC-004 | `NEW` | pending | Selection highlight |
| US-002 | HLR-006 | LLR-006.1 | TC-005 | `NEW` | pending | Box-drawing merge |
| US-003 | HLR-007 | LLR-007.1 | TC-006 | `NEW` | pending | Schema in sidecar |
| US-003 | HLR-007 | LLR-007.2 | TC-006 | `NEW` | pending | Schema validation |
| US-003 | HLR-008 | LLR-008.1 | TC-007 | `NEW` | pending | Per-node coverage |
| US-003 | HLR-009 | LLR-009.1 | TC-008 | `NEW` | pending | Header coverage % |
| US-004 | HLR-010 | LLR-010.1 | TC-009 | `NEW` | pending | Legacy fixture |
| US-004 | HLR-011 | LLR-011.1 | TC-009 | `NEW` | pending | Document chip |
| US-004 | HLR-012 | LLR-012.1 | TC-009 | `NEW` | pending | Reuse renderer |
| US-005 | HLR-013 | LLR-013.1 | TC-010 | `NEW` | pending | Parser syntax |
| US-005 | HLR-013 | LLR-013.2 | TC-010 | `NEW` | pending | Edge labels |
| US-005 | HLR-014 | LLR-014.1 | TC-011 | `NEW` | pending | Exporter round-trip |
| US-005 | HLR-015 | LLR-015.1 | TC-012 | `NEW` | pending | Multiple-parent guard |
| US-006 | HLR-016 | LLR-016.1 | TC-013 | `NEW` | pending | gh connector |
| US-006 | HLR-016 | LLR-016.2 | TC-014 | `NEW` | pending | Caps / +N more |
| US-006 | HLR-017 | LLR-017.1 | TC-014 | `NEW` | pending | Lane renderer |
| US-006 | HLR-018 | LLR-018.1 | TC-015 | `NEW` | pending | CI chip |
| US-007 | HLR-019 | LLR-019.1 | TC-016 | `NEW` | pending | Radial placement |
| US-007 | HLR-020 | LLR-020.1 | TC-016 | `NEW` | pending | Tapered edges |
| US-007 | HLR-020 | LLR-020.2 | TC-017 | `NEW` | pending | Branch hues |
| US-008 | HLR-021 | LLR-021.1 | TC-018 | `NEW` | pending | Search index |
| US-008 | HLR-021 | LLR-021.2 | TC-018 | `NEW` | pending | Search prompt |
| US-008 | HLR-022 | LLR-022.1 | TC-019 | `NEW` | pending | Reverse-light tally |
| US-009 | HLR-023 | LLR-023.1 | TC-020 | `NEW` | pending | Save text files |
| US-009 | HLR-024 | LLR-024.1 | TC-021 | `NEW` | pending | SQLite rebuild |
| US-009 | HLR-024 | LLR-024.2 | TC-021 | `NEW` | pending | .gitignore rule |
| US-009 | HLR-025 | LLR-025.1 | TC-021 | `NEW` | pending | Deterministic rebuild |
| US-010 | HLR-026 | LLR-026.1 | TC-022 | `NEW` | pending | Indented outline |
| US-010 | HLR-027 | LLR-027.1 | TC-023 | `NEW` | pending | Re-parent parser |
| US-010 | HLR-027 | LLR-027.2 | TC-023 | `NEW` | pending | Preserve node data |
| US-011 | HLR-028 | LLR-028.1 | TC-024 | `NEW` | pending | SVG export |
| US-011 | HLR-029 | LLR-029.1 | TC-024 | `NEW` | pending | PNG export |
| US-012 | HLR-030 | LLR-030.1 | TC-025 | `NEW` | pending | Focus filter |
| US-012 | HLR-030 | LLR-030.2 | TC-025 | `NEW` | pending | Focus header |
| US-012 | HLR-031 | LLR-031.1 | TC-025 | `NEW` | pending | Unfocus restore |
| US-013 | HLR-032 | LLR-032.1 | TC-026 | `NEW` | pending | Ficha overlay |
| US-013 | HLR-033 | LLR-033.1 | TC-027 | `NEW` | pending | Ficha sections |
| US-013 | HLR-033 | LLR-033.2 | TC-027 | `NEW` | pending | Modal promotion |
| US-014 | HLR-034 | LLR-034.1 | TC-028 | `NEW` | pending | Attachment schema |
| US-014 | HLR-035 | LLR-035.1 | TC-027 | `NEW` | pending | Attachment grouping |
| US-014 | HLR-035 | LLR-035.2 | TC-028 | `NEW` | pending | Open URL/file |

## 1b. Behavioral chain (black-box)

| US | Acceptance test (`AT-NNN`) | Shipped surface | Observed outcome / deliverable | Status |
|----|----------------------------|-----------------|--------------------------------|--------|
| US-001 | AT-001 | Home screen | User sees Consult / Plug / Construct doors with live keybinds. | pending |
| US-002 | AT-002 | Concept map view | User sees layered tree with state-spined cards; cursor moves with j/k/h/l. | pending |
| US-003 | AT-003 | Concept map header + cards | Missing-document node shows `SIN ACTA`; header coverage updates. | pending |
| US-004 | AT-004 | Legacy fixture view | User sees module tree with document chips and schema letters; ficha shows owner/year. | pending |
| US-005 | AT-005 | `.mmd` file on disk | Saving and re-importing produces the same tree. | pending |
| US-006 | AT-006 | Repo lane view | User sees main lane with releases and feature lanes with CI chips. | pending |
| US-007 | AT-007 | Radial view toggle | User sees root centred-left, coloured branches, curved edges. | pending |
| US-008 | AT-008 | Search overlay | Typing `/acta` highlights matches and shows node tally. | pending |
| US-009 | AT-009 | Workspace files | Only `.mmd` and `_nodos.yml` tracked; deleting `mapper.db` rebuilds map. | pending |
| US-010 | AT-010 | Outline screen | User sees indented outline; re-indenting re-parents node. | pending |
| US-011 | AT-011 | Export dialog | User receives SVG and PNG files matching the screen. | pending |
| US-012 | AT-012 | Focus command | User sees only the focused subtree; unfocus restores full map. | pending |
| US-013 | AT-013 | Ficha overlay | User sees notes/fields/links without leaving the map. | pending |
| US-014 | AT-014 | Node ficha | User sees file/url/image attachments and can open a URL. | pending |

---

## 2. Coverage summary

| Metric | Value |
|--------|-------|
| Total user stories | 14 |
| Covered user stories | 14 (100%) |
| Total HLR | 35 |
| Implemented HLR | 0 (0%) |
| Total LLR | 47 |
| Implemented LLR | 0 (0%) |
| Test cases | 28 |
| TC pass | 0 |
| TC fail | 0 |
| TC pending | 28 |

---

## 3. Detected gaps

> Incomplete rows, requirements without TC, or TCs without code mapping.

| ID | Type | Description | Proposed action |
|----|------|-------------|-----------------|
| — | — | None at Phase 1 gate. | — |

---

## 4. Changes from previous batch

| Type | Item | Detail |
|------|------|--------|
| new | HLR-001..HLR-035 | Derived from 14 READY user stories in Phase 1. |
| new | LLR-001.1..LLR-035.2 | Concretised in Phase 1; file:line marked `NEW`. |
| new | TC-001..TC-028 / AT-001..AT-014 | Validation strategy defined in Phase 1. |

---

## 5. Quick bidirectional mapping

### 5.1 By user story
- **US-001** → HLR-001..003 → LLR-001.1, LLR-001.2, LLR-002.1, LLR-003.1 → TC-001, TC-002 → AT-001
- **US-002** → HLR-004..006 → LLR-004.1, LLR-004.2, LLR-005.1, LLR-005.2, LLR-006.1 → TC-003, TC-004, TC-005 → AT-002
- **US-003** → HLR-007..009 → LLR-007.1, LLR-007.2, LLR-008.1, LLR-009.1 → TC-006, TC-007, TC-008 → AT-003
- **US-004** → HLR-010..012 → LLR-010.1, LLR-011.1, LLR-012.1 → TC-009 → AT-004
- **US-005** → HLR-013..015 → LLR-013.1, LLR-013.2, LLR-014.1, LLR-015.1 → TC-010, TC-011, TC-012 → AT-005
- **US-006** → HLR-016..018 → LLR-016.1, LLR-016.2, LLR-017.1, LLR-018.1 → TC-013, TC-014, TC-015 → AT-006
- **US-007** → HLR-019..020 → LLR-019.1, LLR-020.1, LLR-020.2 → TC-016, TC-017 → AT-007
- **US-008** → HLR-021..022 → LLR-021.1, LLR-021.2, LLR-022.1 → TC-018, TC-019 → AT-008
- **US-009** → HLR-023..025 → LLR-023.1, LLR-024.1, LLR-024.2, LLR-025.1 → TC-020, TC-021 → AT-009
- **US-010** → HLR-026..027 → LLR-026.1, LLR-027.1, LLR-027.2 → TC-022, TC-023 → AT-010
- **US-011** → HLR-028..029 → LLR-028.1, LLR-029.1 → TC-024 → AT-011
- **US-012** → HLR-030..031 → LLR-030.1, LLR-030.2, LLR-031.1 → TC-025 → AT-012
- **US-013** → HLR-032..033 → LLR-032.1, LLR-033.1, LLR-033.2 → TC-026, TC-027 → AT-013
- **US-014** → HLR-034..035 → LLR-034.1, LLR-035.1, LLR-035.2 → TC-027, TC-028 → AT-014

### 5.2 By code file

> No source files exist yet; mapping will be filled during Phase 3 increments.

---

## 6. Batch sign-off

| Field | Value |
|-------|-------|
| Batch ID | `2026-08-18-batch-01` |
| Closing date | `2026-08-21` (Phase 1 derivation) |
| Total iterations (sum of phases) | 2 |
| Validation passed | N/A — implementation pending |
| Synced to Obsidian | no |
