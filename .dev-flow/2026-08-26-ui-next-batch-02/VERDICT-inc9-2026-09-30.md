# Operator verdict — Inc-9 follow-through · 2026-09-30

Base `6d7ee71`. Inc-9 landed (`7e64508..a1d1a32`) and all three independent reviews cleared it:
code PASS, security PASS, ux PASS-WITH-FINDINGS. The code reviewer's uninterrupted full lane:
1369 passed, 4 xfailed, 20 deselected, 0 failed. Four questions were put to the operator directly;
each answer took the recommended option. **This record is the authority for Inc-9b and Inc-9c.**

## Operator answers

| id | Question | Answer (verbatim label) | What it rules |
|---|---|---|---|
| K1 · INC9-UX wording table | Apply the ux reviewer's 20 wording proposals? | Aplicar todas | All 20 rows apply, including group `app` → `global`, `doors` → `open`, `list` → `maps`, `nav`/`tree` → `move`; repo `q` → `back`; `ctrl+p` → `palette` everywhere; `? all` → `? all keys`; `home end ends` → `home end top/bottom` |
| K2 · INC9-UX-F7 | The "settings" screen is a component sheet; nothing persists | components | The screen is named `components` on every surface (key `s` label, door, title, legend); the tab strip marks no active tab on it. If it ever holds real settings it is renamed back |
| K3 · INC9-UX-F6 | Key hints in Spanish contradict English key labels on the same screen | Sí, solo las pistas de teclas | The KEY-HINT strings move to English now (repo body panel, palette footer, prompt and confirm footers, the key half of hint lines). Toasts and prose stay for Inc-EN (B-71) |
| K4 · INC9-UX-F8 / INC9-F8 | The plug screen has four names | `connect repo` en todas partes | The screen is `connect repo` on every surface; the legend title reads the screen name, not the scope id (`legend · connect repo`); its key-group header matches. Import and repo stay as they are |

## Coordinator rulings (defects — no operator question needed)

- **INC9-SEC-F1 (MEDIUM)** — toasts paint absolute paths including the Windows profile (create-map
  error, CSV path, export, factory generated/exception). Same class as B-30 and G6-SEC-F2: toasts name
  the map / file relative to the workspace and the exception TYPE, never `str(e)` or an absolute
  path; a regression arm fails on any toast containing a user-profile path.
- **INC9-UX-F1** repo `q` → `back` (covered by K1). **INC9-UX-F2 / INC9-F3** `?` on the connect-repo
  screen gets priority over its text field. **INC9-UX-F3** the components grid scrolls and focus
  starts on screen. **INC9-UX-F10** legend group order follows the key bar's order.
  **INC9-UX-F4** the home door list and the home key bar read their labels from the seat.
- **INC9-CR-F1..F8** (test strength and record accuracy) and **G6-SEC-F9** (the save census is
  evaded by renaming the receiver) are fixed in the same passes.
- **INC9-F2 split**, as planned: map-view canvas headers (`árbol legacy`, `mapa de conceptos`,
  `mapa mental`, the `_degraded` banners), outline reading `VIEW_NAMES`, coverage and editor titles.

## Split (file cap, 5 source files per increment)

- **Inc-9b** — the INC9-F2 headers: `views/layered.py`, `views/radial.py`, `views/outline.py`,
  `screens/coverage.py`, `screens/editor.py`; the widened strict-xfail arm (INC9-CR-F1) is its gate.
- **Inc-9c** — wording, naming, hints, toasts: `keymap.py`, `app.py`, `darkside.py`,
  `screens/settings.py`, `screens/help.py`; plus INC9-CR-F2..F8 and G6-SEC-F9 in tests.

---

# Round 2 — after the Inc-9b/9c reviews (2026-09-30, base `fddd07d`)

Reviews of Inc-9b + Inc-9c: code PASS (uninterrupted lane 1438 passed / 0 failed), ux
PASS-WITH-FINDINGS, security BLOCK-UNTIL INC9BC-SEC-F1 (the factory office-import toast still paints
the expanded profile path). The ux reviewer also reproduced two PRE-EXISTING data defects in
`MapStore.create_seed` (silent overwrite of an existing map; `../x` writes outside the workspace);
the coordinator cut them as **Inc-SEED** (`7521ac9..06d132c`, requirement A-113) without an
operator question — a defect, not a design choice. Four design questions were put to the operator;
each answer took the recommended option.

| id | Question | Answer (verbatim label) | What it rules |
|---|---|---|---|
| L1 · INC9BC-UX-F1/F2 | The tab strip paints `n build` / `f factory` where `n`/`f` mean something else | Letras solo en home | Key letters appear on the tab strip ONLY on home, where they act, with the seat's labels (`c browse maps`, `n build map`); every other screen paints tab names without letters |
| L2 · INC9BC-UX-F5 | Every hint line starts with `siguiente ▸` | `next ▸` ya | The hint prefix is chrome; it moves to `next ▸` now under K3 |
| L3 · INC9BC-UX-F7 | Home bar leads with `maps j/k/↵` | Las puertas primero | On home the `open` group precedes `maps`, in the bar and the legend alike |
| L4 · INC9BC-UX-F6 | The factory hint repeats keys the bar shows and wraps mid-label at 87 | Solo las acciones: d · i · g | The factory hint is `d edit document · i import office file · g generate office file` |

Coordinator ruling on `INC9B-A1`: keep `atlas · concept map` / `atlas · legacy tree` (the ux
reviewer's recommendation; `atlas (legacy tree)` noted as an alternative, not adopted).

## Split (operator's 4-source-file cap)

- **Inc-9d — security and defects:** `screens/factory.py` (INC9BC-SEC-F1 toast, B-77a, the L4 hint,
  INC9BC-SEC-F4 unguarded copy), `github.py` (INC9BC-SEC-F3 clone stderr path, B-77b `..` URL segment),
  `app.py` (the repo worker's `exit_on_error` so the GitHubError toast is reachable; INC9BC-UX-F3 map
  hint; INC9BC-UX-F13 duplicated recents header). Tests: INC9BC-CR-F1 / SEC-F2 census lexical-try gap,
  INC9BC-CR-F2 K3 sentinel arm, INC9BC-CR-F5 `w=36`.
- **Inc-9e — the design answers:** `darkside.py` (L1 tab strip, L2 `next ▸`, INC9BC-CR-F6 explicit no-tab),
  `keymap.py` (L3 home order), `screens/palette.py` (INC9C-F2 / INC9BC-UX-F4: group headers and an
  English footer from the seat).

