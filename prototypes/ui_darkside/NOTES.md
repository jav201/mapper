# Prototype notes — ui_darkside (mapper × Moonshot's language)

**Question.** After the chrome-system round (`ui_fidelity`), the operator
chose the aesthetic: **darkside** (`/tui-design`'s port of Moonshot's
language, verified in taskboard's `themes.py`). This round applies it to all
mapper surfaces and folds the resulting functionality into the batch's user
stories.

**Location.** `prototypes/ui_darkside/out/index.html` — six real renders:
home (with resume row), home empty state, map, factory, editor, command
palette. Regenerate: `python prototypes/ui_darkside/generate.py`.

## The six laws as applied

1. **Achromatic + KMBlue only on interactivity.** The blue `#1783ff` appears
   on exactly four kinds of things: the active tab, key glyphs on the key
   bar, the solid selected row, and the current step chip. Nothing passive
   wears it. (Questioned and kept: factory `{{tags}}` are blue — they are the
   *editable* affordance of factory mode, not data.)
2. **Depth is a grey-step, never a border.** Content groups sit on `#121212`
   over `#000000`; there is not one border anywhere in the round.
3. **Lowercase register.** Every UI string is lowercase except node titles
   and document content (user data keeps its own case).
4. **Moon doodle on the wordmark.** The phase is COMPUTED from the system
   date (synodic 29.5306d from the 2000-01-06 new moon) — `◑ mapper` today,
   never painted by hand.
5. **Semantic severity only.** `SIN ACTA` is `#ff4f42`, coverage gaps are
   `#ffd230`; a calm state renders ink — there is no green anywhere.
6. **Selection is a solid block.** `sel="solid"`: the selected node is a blue
   block with black text, not an outline.

## Functionality folded into the batch (01-requirements.md)

- **US-015** empty states that onboard (no maps / empty map / empty search).
- **US-016** `ctrl+p` palette: grouped commands, fuzzy, first match solid —
  derived from the ONE keymap seat.
- **US-017** `?` help surface: every live key grouped, from the same seat.
- **US-018** resume-where-I-left as the home's first row (last map + node).
- **US-019** `u` undo for structural changes (taskboard's snapshot-stack
  precedent).
- **D-1** (§6.2): the darkside directive recorded as a batch design decision.

## Verdict (placeholder — fill after operator review)

- …
