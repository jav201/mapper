# Operator verdict — Inc-8 legend · 2026-09-28

Given on the decision page «Leyenda de mapper» (renders of the shipped legend vs the round-10
prototype, base `fc57ac3`), pasted back verbatim by the operator. **This record is the authority
for Inc-8's design pass.** Every item below was the page's recommended option unless noted.

| id | Verdict (verbatim) | What it rules |
|---|---|---|
| D1 · UX-F2 · Q3 | adoptar la propuesta del revisor como copy de 01b; se ajusta junto con D2 | Spanish copy for V7, V8, V9, V10, V19, V21 enters 01b from the ux reviewer's proposal; rows that D2 rewrites are re-copied in the same pass |
| D2 · UX-F3 · Q6 · INC8-F2 | derivar el vocabulario de lo que el producto pinta hoy; 01b se reescribe desde renders reales | The vocabulary is re-derived from the SHIPPED renderers' painted forms, catalogued from real renders per view; 01b §3.1–3.4 is rewritten from that catalogue and the existing set-equality arm enforces it |
| D3 · UX-F4 · Q5 | dar vocabulario a radial (braille, ●) y outline (▾ ▸ ▽); el braille sale del atlas | radial and outline get vocabularies; braille leaves the atlas. **Operator note** — a straight-line edge mode for radial — is a NEW capability, recorded as `BACKLOG.md` **B-69** and deferred by the operator; not part of Inc-8 |
| D4 · UX-F14 | panel lateral acoplado a la derecha en ≥ 118 columnas; modal por debajo de ese ancho | The legend docks right beside the view at ≥ 118 columns (round-10 layout); below that width it stays a modal |
| D5 · UX-F13 · A3 | un solo nombre por vista, el mismo en pantalla y leyenda; propuesta: atlas / esquema / mapa mental / sala | One name per view on both surfaces. The legend adopts them in Inc-8; renaming the other screens' own headers touches files outside Inc-8 and goes with Inc-9 |
| Q7 | ⊘ (U+2298) | Keeps the shipped glyph. **Closes item 1 of `PROTOTYPE-render-round-2026-09-19.md`.** Item 2 (unfocused selection tone) stays open — `BACKLOG.md` **B-70** |
| Q4 | marcarlas diferidas como V18 (#D7) y retirarlas de la declaración | V11–V16 (lente, US-N14 deferred) get the `#D7` deferral marker and leave the declaration |
| Q1·Q2 · UX-F5 · UX-F6 | se resuelven con D2/D3: braille a radial con muestra propia; V4 conserva ∙ y pierde el rango braille | V4b's braille moves to radial with its own sample; V4 keeps `∙` and drops `DECLARED_GLYPH_RANGES`' braille range |
| Q8 · CR-F8 | la microbarra █ █ ░ | V19's sample stays the microbar |
| Q9 · CR-F6 · SEC-F5 | reescribir el mensaje antes del push (historial local, sin remoto afectado) | **EXECUTED 2026-09-28 by the coordinator** — see below |

## Q9 execution — history rewrite, messages only

The message of `8dea408` carried a literal U+202E. Rewritten with `git filter-branch --msg-filter`
over `8dea408~1..HEAD` (the U+202E replaced by the six characters `\u202e`); no tree changed
(`git diff --quiet` between the backup and the new tip passes). Backup branch kept:
`backup/pre-q9-reword-2026-09-28` → `c243eff`. The branch was never pushed past `8dea408`'s
parent, so no remote history is affected. **Every hash cited in increment-022 and in reviewer
reports from before this rewrite maps as follows:**

| old | new | subject |
|---|---|---|
| `8dea408` | `e89a347` | test(legend): Inc-8 — spell U+202E as an escape |
| `fc57ac3` | `8e3841e` | docs(legend): Inc-8 — increment record |
| `9295135` | `1996637` | fix(legend): paint the legend's own scope (HLR-N16.4) |
| `e7b2f00` | `cd74eca` | fix(legend): coercion, row-budget and derivation findings |
| `c243eff` | `3756b62` | docs(legend): Inc-8 corrective pass 1 |

Commits before `8dea408` (`1538f4a`, `0f342a1`, `6e5275f`, and everything earlier) are unchanged.

## Still open for the operator
- **A5** — the own-scope group title `en esta leyenda` (corrective pass 1) awaits ratification
  into 01b §3.6; same class as Q3.
