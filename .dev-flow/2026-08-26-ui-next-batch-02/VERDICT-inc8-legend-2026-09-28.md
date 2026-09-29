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

---

# Round 2 — operator verdict, 2026-09-29 (base `4ae3091`)

Given on the decision page «Leyenda de mapper, segunda ronda» (renders from the final ux review),
pasted back verbatim, plus one clarifying answer. **Authority for Inc-8 design pass 2.**

| id | Verdict (verbatim) | What it rules |
|---|---|---|
| E1 · UX-F1 · D-Q4 · D-Q5 | (a) panel angosto de ~44 columnas, alto completo, vocabulario primero + la vista no se desplaza con la leyenda acoplada | Docked panel ~44 columns wide (round-10 proportion), full height (needs a dated amendment of the sealed `TC-R36` for the DOCKED layout only), vocabulary section first. Keys stay modal while docked: the view does NOT scroll. The row budget re-derives from the new width |
| E2 · UX-F2 | pintar cada celda de muestra sobre GROUND, el suelo de la vista | Every vocabulary sample cell is painted on GROUND, the view's own ground, so it reads as it does in the view |
| E3 · UX-F3 · A5 | ratificar «en esta leyenda» y comprimir el grupo a dos líneas | A5 ratified — the own-scope group exists and is titled; **its wording follows the English ruling below**. The group compresses to two lines |
| E4 · UX-F8 · D-Q1 · D-Q3 | derivar §3.5 de lo que se pinta, como §3.1–3.4, y dar al rojo su segundo empleo «falta el acta» | 01b §3.5 is derived from what is painted, the same way §3.1–3.4 are; ALERT gets a declared second job: the missing-acta mark `◫` |
| E5 · UX-F5 | todo al español en Inc-9, junto con los encabezados de pantalla de D5; los colores se traducen ya en Inc-8 — nota: El proyecto debe estar en inglés en su completitud. | **SUPERSEDED by the clarification below.** Split kept: the legend's own strings now; key labels, group headers and screen headers in Inc-9 |
| E6 · D-Q6 | aceptar las tres etiquetas corregidas, V35 y D✓ | V19, V21a/b and V31 keep their corrected meanings; V35 becomes "pending fields here and below"; field letters get the sample `D✓`. **Wording in English per the ruling below** |

## LANGUAGE RULING — the whole project is in English, UI included (operator, 2026-09-29)

The E5 note read *"El proyecto debe estar en inglés en su completitud."* Asked whether "the project"
meant code and docs only or the UI too, the operator answered: **"Todo en inglés, también la UI."**

This **reverses** the Spanish-copy direction of round 1's D1 and the Spanish view names of D5. It
does not reverse their substance: D1's copy (what each row says) and D5's one-name-per-view rule
stand, rendered in English. Consequences, as routed by the coordinator:

- **Inc-8 (now):** every string the legend paints is English — vocabulary labels, the §3.5 colour
  labels, the §3.6 section headers and footer, the own-scope group title, the title hint, the view
  names. 01b §3.1–3.6 copy is rewritten in English accordingly.
- **Inc-9:** key labels, key-group headers and the other screens' own headers — the strings Inc-9
  already touches — in English.
- **New increment after Inc-9 — `Inc-EN`:** every remaining user-facing string (sala, ficha,
  inspector, toasts, notices, empty states, the damaged-card state `mapa dañado — ↵ ver por qué`
  and its requirement) moves to English, driven by a MECHANICAL census of painted and notified
  strings, with the requirement/test strings that pin Spanish copy re-derived rather than edited.
  Recorded as `BACKLOG.md` **B-71** until it is cut into the batch.
- The operator's own Spanish terms of art in this batch's records (sala, ficha, acta, leyenda) are
  historical text and are not rewritten.

---

# Round 3 — operator verdict, 2026-09-29 (base `7227521`)

Decision page «Leyenda de mapper, tercera ronda» (renders from the pass-2 ux review), pasted back
verbatim. **Authority for Inc-8 design pass 3.** All five items took the recommended option.

| id | Verdict (verbatim) | What it rules |
|---|---|---|
| F1 · P2-UX-F1 · D2-Q6 | colores por vista (cada leyenda muestra solo los colores que su vista pinta) y el ámbar declara también «faltantes, como conteo» | The colour rows are PER VIEW, derived from each view's own census. WARN (amber) gains a declared second job: missing items as a count (the outline footer and the home hero's "sin acta" counts). ALERT (red) keeps "missing record" and appears only where a view paints it |
| F2 · P2-UX-F2 | al acoplar, desplazar la vista para que la selección quede a la izquierda del panel; al cerrar, volver a la posición anterior | On dock, the view pans so the selection sits left of the panel; on close, the view returns to its prior position. Keys stay modal (E1 unchanged): the view moves only because of docking |
| F9 · D-Q7 | derivar el umbral del ancho de lienzo que queda visible junto al panel de 44 (acoplar mientras quede un mínimo útil) | The dock threshold is DERIVED from the canvas width left visible beside the 44-column panel; dock while a useful minimum remains. The minimum is a named, declared number |
| Q7 · D2-Q7 · P2-CR-F8 | V28 como D░ «field initial · ░ pending», y la letra se pinta en el gris de la vista en V27 y V28 | V28's sample becomes `D░` ("field initial · ░ pending"); in V27 and V28 the letter is painted in the view's grey, as the view paints it |
| copy · P2-UX-F3 · F5 | aplicar todos los ajustes de copy y del modal | All nine copy and modal adjustments on the page apply, including the 12-cell sample column in the modal |

## DESIGN PRINCIPLE — terminal width is variable; keep a fixed reference width (operator, 2026-09-29)

Verbatim note on the copy item: *"Usualmente el escalado de la terminal es una herramienta para hacer
fit de más contenido y ese se mantienen variable, al menos así es en otras aplicaciones con TUI. Ten
eso en cuenta también en la toma de decisiones, es bueno tener un ancho de columnas fijo como
referencia considerando lo anterior."*

Reading applied by the coordinator:
- **Behaviour is derived for ANY width.** Operators zoom the terminal to fit more, so no layout may
  assume a width; thresholds and budgets derive from geometry (this is why F9 derives the dock
  threshold instead of fixing it).
- **Decisions and renders use ONE fixed reference width:** the declared context of use,
  `DECLARED_CONTEXT_CELLS` = 118 columns. Every design render shown to the operator includes the
  reference width, alongside a narrower and a wider one.
---

# Round 4 — operator verdict, 2026-09-29 (base `c7cdf85`)

Decision page «Leyenda de mapper, cuarta ronda», pasted back verbatim. **Authority for Inc-8 design pass 4 and for the G6 micro-increment.** All seven took the recommended option.

| id | Verdict (verbatim) | What it rules |
|---|---|---|
| G1 | mantener 43 de lienzo; el rail no cuenta | Dock minimum stays 43 canvas columns; the rail does not count as view. Switch points 87 (bare) / 111 (with rail) stand; `INC8-P3-CR-F4` (derive 43 from renderer constants) stays a carry for when `layered.py` is in scope |
| G2 | enmendar LLR-N06.1.2: mientras la leyenda está acoplada, el rango legal usa el lienzo visible | Dated amendment to `LLR-N06.1.2`: while the legend is docked, the legal pan range is computed on the VISIBLE canvas, so an edge card can be revealed; on close the pan returns to the kept value exactly as today |
| G3 | ampliar a «red — required, missing» | The red row reads `red — required, missing` (covers the atlas record mark and the inspector's required fields) |
| G4 | una fila «amber — attention · missing count», en todas las vistas que pintan ámbar | ONE amber row, `amber — attention · missing count`, declared on every view that paints amber (replaces C2+C3) |
| G5 | aplicar los tres: V34 «in the rail», V28 «field initial, pending», margen de 2 columnas | V34 → `folded branch, in the rail`; V28 → `field initial, pending`; the revealed card keeps a 2-column margin from the panel |
| G6 | micro-incremento propio justo después de Inc-8: limpiar los campos de ficha al entrar al grafo y proteger los 6 guardados | A dedicated micro-increment right after Inc-8: ficha string fields are coerced as they enter the graph (load and in-app mutation), and the 6 unguarded `store.save()` call sites are guarded (`INC8-P3-SEC-F1`) |
| G7 | dejarlo en B-37 (recalibrar MUT en un batch de diseño) | The MUT-on-GROUND 4.43:1 shortfall stays in `BACKLOG.md` B-37 (recalibrate MUT in a design batch) |

Also landed before this record: the pass-3 corrective (`4a372dc`, `60bf183`, `da49eb0`) fixed the code-review BLOCK `INC8-P3-CR-F1` (opening the legend moved keyboard focus) and restores the pre-legend focus on close, including `None` (closes `INC8-P3-UX-F1` / `UX-F7`).

---

# Round 5 — closing questions, operator answers 2026-09-29 (base `3818a96`)

Both closing reviews said **Inc-8 may close** (code PASS, ux PASS-WITH-FINDINGS). Four
questions were put to the operator directly; each answer took the recommended option.

| id | Question | Answer (verbatim label) | What it rules |
|---|---|---|---|
| H1 · CL-UX-F2 | `?` typed in the inspector title field replaces the title with "?" and saves it (select-all on focus; pre-existing; B-36 family) | Junto con B-36, y ajustar el pie ya | The field fix goes with **B-36** (first item of the next design batch). Now: the legend footer stops over-promising — `? explains the view you are in, outside text fields` |
| H2 · CL-UX-F1 | After `tab` into the inspector, closing the legend turns the selected card blue → grey (stale paint: `tab` does not repaint) | Sí, arreglarlo en Inc-8 | Repaint the canvas on every focus change; the arm is driven with real keys, not `set_focus()` |
| H3 · CL-CR-F2/F3 · CL-UX-F3 | The 2-column reveal margin paints as 3 on an ordinary card and 1 at the map's edge; the edge exception was the implementer's | 2 columnas pintadas en todos los casos | The margin counts PAINTED columns, and the edge honours it too (the docked range widens by the margin). The arm asserts the composited frame, not the geometry. The implementer's edge exception in A-109 is withdrawn |
| H4 · CL-UX-F4 | With the rail hidden (`R`, or auto below ~117 columns), the legend still lists rail rows | Ocultarlas cuando el rail no se ve | The legend lists rail rows only while the rail is shown, as colours are already per view |

Also applied in the closing pass, not needing a ruling: `INC8-CL-CR-F1` (re-clamp the pan after
close so a resize while the legend was open cannot leave it outside the legal range), and the
coordinator aligns V27's copy with the operator's G5 wording for V28 (`field initial, filled` /
`field initial, pending`). Carries: `INC8-CL-CR-F4` (no arm pins `_reclamp_pan`'s range) to
qa-reviewer; a FLAKE-2 candidate — `test_hlr_n16_4_legend_declares_its_own_keys[size2]` failed
once ("work but not painted: ['left']") under concurrent load, 0 of 21 since.

