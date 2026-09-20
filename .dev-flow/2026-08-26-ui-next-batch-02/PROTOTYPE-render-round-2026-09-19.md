# Render round — two design items for Javier's verdict · 2026-09-19

Both items are **already shipped in a LEGAL form**, because each splits into a mechanical half and
an aesthetic half and only the second is a design question. The mechanical half was settled by
measurement against a ratified constraint; **this round is the aesthetic half, and nothing is
blocked while it waits.**

Base `91fdbbd`. Every frame below is painted by the shipped widget — no mockups.

---

## Item 1 — the damaged-map card glyph (`LLR-N13.1.5` / `PRED-VIS` / `01b` `V22`)

**What is already settled and is not up for verdict.** The card must carry a *glyph*, not just a
string: the sala is **scanned, not read**, and a card that differs only in text differs only to
someone already reading it. The style is fixed at `INK on PANEL` (17.18 : 1) by `PRED-VIS RESOLVED`,
which also forbids spending a colour token. The codepoint had to be one terminal cell, not already
carrying a meaning among the other 21 rows, not emoji-presentation, and free of a meaning collision.
**Fourteen candidates survived the first three filters; two survived all of them.**

**The question for you: `⊘` or `⦸`?** They are near-identical by design — both are circled slashes,
and they are what remains after the filters. `✗` is shown third *with its caveat* because it is the
strongest-looking option and I want the caveat visible rather than buried.

```
--- ⊘   U+2298 CIRCLED DIVISION SLASH      SHIPPED; best font coverage
     ▐ name       kind        nodos  docs
     presupuesto   concept    3      0
     roto          ⊘ dañado   —      —
     sano_vacio    concept    0      0

--- ⦸   U+29B8 CIRCLED REVERSE SOLIDUS     survived every filter; rarer in fonts
     roto          ⦸ dañado   —      —

--- ✗   U+2717 BALLOT X                    CAVEAT BELOW
     roto          ✗ dañado   —      —
```

> **The `✗` caveat, stated because it is the reason it is not shipped.** `V14` is `ficha completa ✓`.
> `✗` reads as that checkmark's antonym, so on a *card* it invites "ficha incompleta" — which is
> `V15`, a different row with a different meaning. It looks the clearest and is the most likely to
> be misread.

`sano_vacio` is in every frame deliberately: a **healthy map with zero nodes** is the one row the old
code was indistinguishable from, and it is the control that makes the fix visible.

---

## Item 2 — the unfocused selection tone (`UX-F7b`)

**Already fixed, and the fix was forced.** The unfocused selection was painted `INK on STEP`, which
is the **hit livery byte for byte** — so a selected node that was *not* a search hit was painted as
a match. Driven: six titles in hit livery against five declared hits, with the strip in the same
frame reading `0/5`.

**A colour difference cannot be shown in a text frame**, so this item's renders are SVGs rather than
the ASCII above — a text render of the three variants is byte-identical and shows nothing, which is
worth saying because it is why this section looks different from Item 1.

| Variant | Contrast | Status |
|---|---|---|
| **`INK on PANEL`** | **17.18 : 1** | **SHIPPED.** `PANEL` is darker than `STEP`, so the selection sits *recessed* against the hit livery rather than competing with it |
| `MUT on STEP` | **3.19 : 1** | **ILLEGAL** — under `#D28`'s 4.5 floor. Rendered only so the floor is visible |
| `ACCENT on PANEL` | legal | Selection-blue. Legal, but competes with the **focused** selection, which is already `bold GROUND on ACCENT` |

Rendered to `tone-shipped-INK-on-PANEL.svg`, `tone-rejected-MUT-on-STEP.svg` and
`tone-alt-ACCENT-on-PANEL.svg` (scratchpad, out of repo — `.gitignore` excludes `*.svg` so exported
artifacts cannot be committed). Each is the real canvas with the cursor on a **non-hit**, a live
search on another node, and the keyboard owned by the rail.

---

## What a verdict changes, and what it does not

**Neither item blocks anything.** Both ship legal today. A verdict swaps a codepoint and a token
pair — both one-line changes, each already pinned by an arm that fails if the replacement is
illegal or collides.

**What a verdict cannot do is relax a floor.** If you prefer a tone under 4.5 : 1 it does not ship;
`#D28` says the floor stands and the token changes, and restating a floor downward to rescue a token
choice is the defect this batch has caught before.
