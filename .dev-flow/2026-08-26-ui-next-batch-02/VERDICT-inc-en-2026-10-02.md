# Operator verdict — Inc-EN plan · 2026-10-02

Base `e747d8d`. The Inc-9 line is closed. A read-only census (AST scan of non-docstring string literals
under `mapper/`, prototypes excluded) found ~230 user-facing Spanish strings in 14 source files, ~150–180
pinning test assertions in ~45 test files, and ~100 quoted Spanish fragments in `01-requirements.md`.
Authority for the language: `VERDICT-inc8-legend-2026-09-28.md` § LANGUAGE RULING ("Todo en inglés,
también la UI"), B-71. Three questions were put to the operator; each took the recommended option.

| id | Question | Answer (verbatim label) | What it rules |
|---|---|---|---|
| EN-Q1 | Approve the 7-increment plan, in order? | Aprobar el plan | EN-1 `osopen`/`github`/`screens/factory`/`screens/editor`; EN-2 `screens/coverage`/`screens/settings`/`widgets/inspector`/`widgets/rail`; EN-3 `views/*`; EN-4 `store`/`darkside`/`widgets/components`; EN-5 `app.py` alone; EN-6 palette footer `↑↓ move` (N2: `keymap`, `screens/palette`); EN-7 `?` in text fields (T3). Max 4 source files each, one review round each |
| EN-Q2 | Translate new-map seed content (`nuevo mapa`, `primer hijo`, `dueño`, `auditoría legacy`)? | Traducir también | Seeds are written in English; fixtures that depend on them are re-derived (EN-4) |
| EN-Q3 | Does T3 (`?` types in a text field) apply to the connect-repo field too? | Sí, `?` escribe en todo campo | One rule: in every text field `?` is a character; the legend opens with `?` outside fields or from the palette. Supersedes INC9-UX-F2 (EN-7) |

Rules for every EN increment: requirement text that quotes Spanish copy is amended by a dated A-1NN
note (never rewritten); a sealed arm that pins a Spanish string changes its LABEL only and is declared;
wording is plain operator English, matching the existing English sentences (U1, V1, V2, W1, W2, X1, Y1).

## Round 2 — after the Inc-X3 review (2026-10-02)

X3 review: OK, no HIGH (X3-REV-F1 test gap folded into EN-1). Two pre-existing UX items, now visible
because attachments open, were put to the operator; both took the recommended option.

| id | Question | Answer (verbatim label) | What it rules |
|---|---|---|---|
| Z1 · X3-REV-F2 | Opening an attachment toggles its chip's selected look | Que no alterne | Attachment chips only open; they never toggle `selected`. Routed to EN-4 (`widgets/components.py`) |
| Z2 · X3-REV-F3 | With an attachment chip focused the hint says `↵ open card` | «↵ open attachment» | A focus-aware hint: `↵ open attachment` while an `insp-att-*` chip has focus. Routed to EN-2 (inspector); if it needs `keymap`/`app`, to EN-5/EN-6 |
