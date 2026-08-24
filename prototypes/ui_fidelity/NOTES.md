# Prototype notes — ui_fidelity (the chrome-system redesign)

**Question.** The mapper UI (HomeScreen / MapScreen / factory / editor) reads
as flat text: no visual cues, no Gestalt separation, no task guidance, and the
four entry points don't feel like one app (`handoff-ui-redesign.md`). This
prototype answers, with real terminal renders: **three chrome systems over the
same four screens** — pick the system, then route implementation through
`/dev-flow`.

**Location.** `prototypes/ui_fidelity/out/index.html` — each screen section
shows all three variants; ←/→ switches variant (V1/V2/V3), ↑/↓ moves between
screens. Regenerate: `python prototypes/ui_fidelity/generate.py`.

## The design system all three variants share (the operator's four points)

1. **Visual cues** — selection = reverse + accent edge; mode badge in the
   header (`browse`/`factory`/`edit`, own width, never stretched); step chips
   for multi-step flows (`1 proceso → 2 oferta → 3 aprobacion → 4 envio`, the
   current step lit); kind badges per map kind (concept / legacy / factory /
   repo / new); position is always visible on the key bar.
2. **Gestalt** — chrome (header + footer) is visually distinct from content
   (boxed panels in V1, rules + whitespace in V2, the tab strip + deck in V3);
   controls group by category (`nav · node · view · app`) with group labels;
   related things align on shared edges.
3. **Guidance** — every screen answers three questions at a glance:
   *Where am I?* = the breadcrumb (`◆ MAPPER / home / contratacion / oferta`,
   current node bold). *What can I do?* = the grouped key bar, every key on it
   live (the taskboard keybar contract). *What's next?* = a literal hint line
   above the key bar (`siguiente ▸ oferta hereda {{depto}} de contratacion —
   d edita el documento`).
4. **One app** — same header shape, same key vocabulary, same palette, one
   `ctrl+p` command palette and one `?` help surface everywhere.

## The three variants (NOT recolours)

- **V1 · Frame & ribbon** — chrome is boxed (bordered header/footer panels,
  door cards with borders, ficha as a bordered panel). Grouping is
  *containment*: the strongest separation, the most "application" look.
- **V2 · Air & rules** — frameless like taskboard: separation by one hairline
  rule, whitespace, and left spines. Grouping is *proximity + alignment*: the
  lightest chrome, the most terminal-native.
- **V3 · Deck & tabs** — the four doors become a persistent facet strip
  (`consult repo construct factory` as tab cards, active lit, breadcrumb as a
  second line). Grouping is *common region*: the four entry points literally
  share one strip; the most "one app" of the three.

## Verdict (placeholder — fill after operator review)

- Variant chosen: …
- Rationale: …

## Notes for implementation

- The badge-stretching bug is a real lesson: a mode badge built with
  `Table.grid(expand=True)` + `on`-colour styles stretches to the cell width;
  compose the header as one `Text` so badges keep their own width.
- The step chips and the hint line are the two cheapest wins — they cost one
  row each and answer two of the operator's three guidance questions.
- The kind-badge set (`concept / legacy / factory / repo / new`) is the
  vocabulary the recents table, the doors, and the header badge should share.
