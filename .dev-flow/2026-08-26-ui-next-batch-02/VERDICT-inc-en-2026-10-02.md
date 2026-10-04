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

## Round 3 — after the EN-5 and EN-6 reviews (2026-10-02)

EN-5 review: OK (no HIGH; EN5-REV-F2: 18 unpinned `darkside.plain` sites in `app.py`, six on
user- or file-controlled text). EN-6 review: OK (EN6-REV-F2: no test pins that the arrows reach the seat
binding). Three wording questions were put to the operator; each took the recommended option.

| id | Question | Answer (verbatim label) | What it rules |
|---|---|---|---|
| E1 · EN5-REV copy | `edge of the territory` (literal) vs `edge of the map` | edge of the map | The pan-edge notice reads `edge of the map`; `territory` stays only in the rail |
| E2 · EN5-REV copy | Export stale-file sentence | Decir de dónde viene | `Nothing was written; X.svg on disk is from an earlier export.` |
| E3 · EN6-REV-F4 | Palette footer separators (N2 wrote ` · `) | Con « · » como en N2 | ` N/M actions   ↑↓ move · ↵ run · esc close` |

Routed to EN-8 (cleanup, no new features): E1–E3; EN5-REV-F2 arms for the six user/file-controlled
`plain` sites; EN5-REV-F3..F7 (EN2-REV-F1 comment, census words, `record` in the ficha modal, singular
`descendant`, the vacuous `test_inc9m` pin); `Cancel`/`Close` lowercase; `declaration not available`
reworded; EN6-REV-F1..F3; EN4-REV-F1..F5; EN3-REV-F1/F3; EN2-REV-F2/F3 record notes; EN1-REV leftovers.

## Round 4 — after the EN-7 review (2026-10-03)

EN-7 review: OK (no HIGH; EN7-REV-F1 the connect-repo key bar still advertises `? legend` although its
only control is the text field, so `?` always types there; F2 A-135 over-claims "the palette's legend
action opens it from anywhere" — coverage and editor modals have no palette, pre-existing; F3/F4 LOW).
One question was put to the operator; it took the recommended option.

| id | Question | Answer (verbatim label) | What it rules |
|---|---|---|---|
| E4 · EN7-REV-F1 | Connect-repo advertises `? legend` where `?` can only type | Quitar «? legend» ahí | On a screen whose only focusable control is a text field, the key bar and the legend do not list `?`; `ctrl+p palette` (already on the bar) reaches the legend |

Routed to EN-9 (micro): E4; EN7-REV-F2 (amend A-135 to "every seat-migrated screen", backlog the
coverage/editor modals that reach no legend); F3 (record correction: no prompt pre-fills a value);
F4 (the 87-column inspector arms assert the field is displayed, or are labelled programmatic).
