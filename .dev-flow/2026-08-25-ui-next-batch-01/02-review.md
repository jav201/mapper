# 02 — Cross-agent review · `2026-08-25-ui-next-batch-01`

## BLUF

Three lenses reviewed this batch's requirements and design, and each one used a **different
instrument** — which is why they did not overlap and each found something the others did not. The
security lens did not argue that path traversal was possible; it **executed** it. The UX lens did
not reason about focus; it **counted painted cells**.

Consolidated verdict: **`approved with conditions`**. Every condition was folded into
`01-requirements.md` §6.5 as **Amendment 2**, with Before → After text and its executed evidence.

| Lens | Artifact | Verdict | Findings |
|---|---|---|---|
| `architect` (ARQ station) | reported inline; output is the amended `docs/ARCHITECTURE.md` | approved | 7 architectural risks (A-1…A-7); module map 9 → 18 modules |
| `qa-reviewer` (oracle design) | [`01b-acceptance-design.md`](01b-acceptance-design.md) | approved | 20 ATs specified with their RED mutations; 1 story judged not fully testable |
| `security-reviewer` | [`02b-security-review.md`](02b-security-review.md) | approved with conditions | **2 blockers**, 6 majors, 6 minors |
| `ux-reviewer` | [`02c-ux-review.md`](02c-ux-review.md) | approved with conditions | **4 blockers**, 5 majors |

Two later gates belong to Phase 4 but are recorded here for the reader following the review chain:
the Inc-4 [security sign-off](04b-security-signoff.md) (blocked → granted) and the final
[PR-level gate](04c-pr-gate.md) (blocked twice → merge).

---

## 1 · Blockers, and what each one cost

### Security

**S-B1 · `kind == "file"` launched anything on disk.** Measured, not deduced: a `..` traversal
target launched a file outside the workspace, and `calc.exe` and `powershell.exe` both launched.
`os.startfile`'s own documentation says it "acts like double-clicking the file in Explorer". The
confinement the module map mandates was structurally absent because the proposed signature had no
`workspace` parameter to put it in.
→ LLR-N02.6 … LLR-N02.9.

**S-B2 · Terminal control characters reached the terminal.** C-17 covers markup only. Rich emitted
a cursor-move sequence and an OSC-52 clipboard write verbatim. Markup escaping does nothing about
either — and worse, `rich.markup.escape` inside a `Text.append` path is a **no-op that prints
visible backslashes**, so the existing code was wrong in both directions.
→ LLR-N01.10, LLR-N01.11, and `darkside.plain()`.

### UX

**U-B1 · There was no focus signal at all.** With focus in an inspector field, the screen paints
**28 cells of `#1783ff` across three rows** — canvas selection, segmented control, selected chip —
and **none of them is the focused widget**. `DsChip` focused and selected rendered byte-identically.
→ **HLR-N06**, adopted into this batch.

**U-B2 · `escape` while typing popped the whole map and discarded the text.** Verified against the
shipped app. → LLR-N06.4.

**U-B3 · A screen-level `tab` binding disables focus traversal entirely** — 9 presses, 0 focus
moves. The old seat bound `tab`. → LLR-N06.5.

**U-B4 · Committing a field edit pushed no undo snapshot**, so `u` restored an older structural
snapshot and destroyed the edit. → LLR-N05.6.

---

## 2 · Findings classified

| Severity | Count | Disposition |
|---|---|---|
| blocker | **6** (2 security + 4 UX) | all closed in Amendment 2; each has a gating `AT` |
| major | **11** | 9 closed in-batch; 2 recorded as carries (`MapStore.load` KeyError; the `screens → app` back-edge) |
| minor | **11** | 5 closed; 6 recorded in `.dev-flow/BACKLOG.md` as B-06 |

**Normative-language check:** no `should` / `debería` appears as a modal verb inside any HLR or LLR
statement. Verified by grep over `01-requirements.md` §3.

---

## 3 · One finding recorded as explicitly NOT a defect

The nine `Ds*` components are clean. `DsChip`, `DsTextField` and `DsSegmented` all build through the
`Text(...)` constructor, which does not parse markup:
`DsChip(label="[bold red on white]OWNED[/]").render()` yields
`.plain=' [bold red on white]OWNED[/] '`, `.spans=[]`. No component interpolates a caller string
into a markup-parsed path, so reusing them for the inspector was safe. Recorded because "we checked
and it was fine" is evidence too, and the next batch should not re-check it.

---

## 4 · A fixture correction worth more than it looks

An unbalanced **opening** bracket does not raise; an unmatched **closing** tag
(`Static.update('[/bold]saldo')`) raises `MarkupError`. The design's hostile fixture contained only
the opening case, so it would have passed green while the crashing case shipped. `AT-N01e`'s fixture
carries both.

---

## Evidence checklist

- ✓ All three lenses ran in parallel with distinct instruments — artifacts listed in the BLUF table.
- ✓ Every blocker traced to a specific LLR in Amendment 2 — `01-requirements.md` §6.5.
- ✓ Every blocker has a gating `AT` — reconciled at Phase 4 (`04-validation.md` §2), 27 ATs, each one node.
- ✓ `shall`/`should` usage verified — no modal `should` inside a requirement statement.
- ✓ Findings that were NOT fixed are recorded in `.dev-flow/BACKLOG.md`, not dropped — B-01 … B-11.
- ✓ Security lens re-invoked at Inc-4 as the PDR required — `04b-security-signoff.md`.
