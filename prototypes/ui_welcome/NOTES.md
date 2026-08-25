# Prototype notes — ui_welcome (appeal + the welcoming entry)

**Question.** The operator reviewed the implemented app and found the UI still
too simple: lacking visual appeal, and it doesn't WELCOME you into the app.
References pointed at: `desk` (widget deck), `taskboard` (the aperture),
`s19_app` (Hex Edit Tool). This round raises every view, darkside-compliant.

**Location.** `prototypes/ui_welcome/out/index.html` — five real renders.
Regenerate: `python prototypes/ui_welcome/generate.py` (it reads the REAL
`mapper/darkside.py` + `mapper/keymap.py` — the prototype is the production
chrome plus the new content).

## What the references taught (distilled, and where each landed)

- **desk** — empty states are SENTENCES, never zeroes; one hero per surface;
  the keybar sheds by priority and NAMES what it dropped. → W2's welcome is a
  sentence + a ghost mini-map as the taste; W1's pulse row never shows a zero
  (a map with no docs shows `—`).
- **s19_app** — never mount blank: the status reads "Ready." from
  construction; the help triad (`?` help · `ctrl+p` palette · the keybar) is
  always discoverable. → W5 is the full grouped key surface reading from the
  ONE keymap seat; the intro line is the keybar contract in Spanish ("cada
  tecla mostrada funciona; cada tecla que funciona se muestra").
- **taskboard** — the aperture: a drawn identity element + a glance surface.
  → W1: the big recessive wordmark (4×5 block font, `#3a3a3a`) + the computed
  moon + the date + the workspace pulse row (counts + coverage as a step
  meter) + the resume chip.

## The five views

- **W1 · home as aperture** — identity block (wordmark + moon + date), the
  workspace pulse (`4 mapas · 90 nodos · 11 docs · cobertura ▰▰▰▰▰▰▱▱▱ 67%`),
  the resume row (the one blue affordance), the recents rail with kind chips
  and per-map mini step-meters, the grouped keybar.
- **W2 · first-run welcome** — the identity block centred, the welcome
  sentence, a ghost mini-map as a taste, the four doors as chips with `n`
  lit, and the "empieza con n" line. Never blank.
- **W3 · map with rail + inspector** — the left rail carries the tree's
  guides, the ACTIVE PATH (root → selected) reads blue (D-A applied to the
  layered view, not just radial), the selected node is the solid block, the
  ficha is an inspector (chips + step meter + notes).
- **W4 · factory** — step chips (current = blue block), process tree with
  solid selection, preview + tags tables on the step depth.
- **W5 · help surface** — every live key grouped (nav/node/view/map/app),
  with the triad stated. One seat, three readers (bar/palette/help).

## Verified

Browser pass over all five SVGs, index loads clean. The production keymap
module's Spanish labels surfaced through the shared seat (`j siguiente · k
anterior · ↵ abrir · …`) — the prototype and the app cannot drift because
they read the same list.

## Verdict (placeholder — fill after operator review)

- …
