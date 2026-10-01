# Increment 031 — Inc-9e · the design answers L1–L3 and the palette's group column

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Increment | `031` — Inc-9e |
| Agent | `software-dev` |
| Date | 2026-09-30 |
| Authority | `VERDICT-inc9-2026-09-30.md`, "Round 2", the table L1–L4, "Split", **Inc-9e**; `increment-027-inc9c.md`; `increment-029-inc9d.md` |
| Starting state | branch `feat/ui-next-batch-02` @ `e475bd9`, `git status --porcelain` = 0 |
| Commits | `35e77fb` arms (RED) -> `e8283e0` L1 + L2 + CR-F6 -> `54d4a45` L3 -> `0a37fb6` palette -> docs commit (this file) |
| Source files | **4** (`mapper/darkside.py`, `mapper/keymap.py`, `mapper/screens/palette.py`, `mapper/screens/settings.py`); cap 4, given 3. `settings.py` is the declared 4th: CR-F6 is only closed if the screen passes the explicit value. |
| Amendment | none: L1–L3 are the operator's rulings in the verdict; no threshold or rule needed a new requirement. `A-113` stays the last id taken. |

Findings are named `INC9E-Fn`.

---

## 1 · What changed

### Copy and order table

| Surface | Before | After |
|---|---|---|
| Home tab strip | ` c browse   p connect repo   n build   f factory` | ` c browse maps   p connect repo   n build map   f factory` (key glyph and label from the seat rows `consult`, `plug`, `construct`, `factory`) |
| Strip on map, factory, components, connect repo | the same four, with letters | ` browse maps   connect repo   build map   factory` (no key glyph; the seat's labels) |
| Hint prefix (`hint_line`) | `siguiente ▸ ` | `next ▸ ` |
| Components screen's tab | `TabStrip("s", …)` (relies on `s` not being a tab) | `TabStrip(None, …)`; `tab_strip(None)` marks no tab |
| Home key bar and legend, group order | `maps`, `open`, `exit`, `global` | `open`, `maps`, `exit`, `global` (`GROUP_SCOPE` lists `doors` before `list`; `bar_group_order` and `keybar_groups` follow, and so does the legend) |
| Palette, first column | raw group ids (`app`, `doors`, `list`, `nav`, …), sorted alphabetically | header words (`open`, `maps`, `exit`, `global`; map: `move`, `node`, `view`, `leave`, `global`), in the key bar's order |
| Palette footer | ` 14/14 acciones   ↵ ejecutar   esc cerrar` | ` 14/14 actions   ↵ run   esc close` (`run` and `close` from the seat's `palette` rows through `hint_pair`) |
| Palette placeholder | `/comando` | `/command` (chrome: no seat row exists for it) |

### Finding by finding

| Finding | Change |
|---|---|
| **L1 · INC9BC-UX-F1/F2** | `tab_strip` reads the four doors from the seat (`_TAB_ACTIONS`, looked up in `keymap.bindings_for(SCOPE_HOME)` at call time). Letters are painted only on the home strip. The home strip's words now equal the bar's (`browse maps`, `build map`). |
| **L2 · INC9BC-UX-F5** | `hint_line` prefix `next ▸ `. |
| **INC9BC-CR-F6** | `tab_strip(active: str \| None, …)`; `settings.py` passes `None`. |
| **L3 · INC9BC-UX-F7** | one move of one line in `GROUP_SCOPE`. |
| **INC9C-F2 / INC9BC-UX-F4** | `CommandPalette` sorts by `bar_group_order(scope)`, paints `group_header`, sizes the header column to the scope's longest header, builds the footer from the seat. |

### Found by this increment

| id | Finding | Disposition |
|---|---|---|
| `INC9E-F1` | **How the strip knows it is home is implicit.** `TabStrip` has no flag for it, and adding one means editing `chrome.py` and the call sites in `app.py` (six source files, over the cap). `tab_strip` decides `letters = crumb is None and active == <first door>`: home is the only strip with that pair (the map's crumb is never empty; the factory has no crumb but its active tab is `f`). A new screen with that pair would grow letters; a crumb added to home would lose them (the home arm goes RED). | Declared. Proper fix: a `letters` argument on `TabStrip` and `tab_strip`, set by `HomeScreen` (2 files). Carry. |
| `INC9E-F2` | The search hint `n siguiente · N anterior · esc limpiar` (`app.py:3590`) still says `siguiente`: it is a SEAT WORD in Spanish (`K3`), not the prefix, and `test_search.py` pins it in four places. The L2 census covers the hint lines the screens paint at rest, not that transient one. | Not fixed (out of the three files). Carry with `Inc-EN`. |
| `INC9E-F3` | The first RED run (`35e77fb`) did not reach the factory half of two arms: `FactoryScreen()` needs a graph, and the arms failed earlier on the map. Fixed in `e8283e0` (no amend), and RED re-shown on a clean archive of `e475bd9` carrying the corrected file: 15 failed, 2 passed. A second arm bug (the home strip was not re-rendered after the sentinel relabel) was fixed there too. | Fixed. |
| `INC9E-F4` | The non-home strip now paints the seat's labels (`browse maps`, `build map`), not the old short words (`browse`, `build`). The verdict says "tab names without letters"; I read "names" as the same words the bar and the door list use, which is what closes F1 on every screen, not only home. The tab row is 1 cell wider off home (53 vs 52) and 9 wider on home (61 vs 52, before the wordmark), counted from the strings. | Judgement; reversible in `tab_strip` alone. Not measured below 87 columns. |

## 2 · Files modified

| File | Change |
|---|---|
| `mapper/darkside.py` | `from mapper import keymap`; `_TAB_ACTIONS`; `tab_strip` rewritten; `hint_line` prefix |
| `mapper/keymap.py` | `GROUP_SCOPE` order (`doors` before `list`) |
| `mapper/screens/palette.py` | order, header column, footer, placeholder |
| `mapper/screens/settings.py` | `TabStrip(None, …)` (the declared 4th source file) |
| `tests/test_inc9e.py` | new, 17 cases |
| `tests/test_inc9.py`, `tests/test_inc9c.py` | the changed-sealed-arm list below |
| this file | record |

Tests are uncapped; source is 4 of 4. `darkside.py` now imports `mapper.keymap`; `keymap` has no import of `darkside`, so there is no cycle, and `test_keymap`/`test_inc9` (the dependency checks) pass.

### Changed sealed arms (with justification)

Only arms that pin a LABEL, an ORDER or a tab VALUE were touched; every behaviour arm is unchanged (`test_inc9c` K2 `active == []`, the home door list, the key dispatch, the overflow and the crumb arms all ran as they were).

| Arm | Change | Why |
|---|---|---|
| `test_inc9.py::_screen_headers` (the A-112 English census) | tab labels were parsed out of a literal `tabs` list inside `tab_strip`; they are now `keymap.label_for(SCOPE_HOME, action)` for each of `darkside._TAB_ACTIONS` | the literal list is gone by `L1` ("read it from the seat, not hand-written"); the labels still go through the same `_judge`, so a Spanish tab label would still be caught, through the seat label. It pins where the label VALUE comes from, not behaviour. |
| `test_inc9c.py::test_inc9c_k4_connect_repo_is_one_name_on_every_surface` | `"p connect repo" in joined` -> `"connect repo" in joined and "p connect repo" not in joined` | `L1`: the connect repo screen's strip no longer carries the letter. The name is still pinned; the letter is now pinned absent. |

## 3 · How to test

```
PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python -m pytest tests/test_inc9e.py -q
```

By hand, home at 87x34: the bar starts `open c browse maps  p connect repo …`; the strip reads ` c browse maps  p connect repo  n build map  f factory`. Open a map (`↵`): the strip has names and no letters; `n` is `next match` and `f` is `focus branch`, nothing else says otherwise. `ctrl+p` from home: `open …`, `maps …`, `exit …`, `global …`; footer ` 14/14 actions   ↵ run   esc close`.

## 4 · Test results

### Arms first (`executed`)

`35e77fb` committed 15 strict-xfail arms and 2 controls (a real home tab letter opens its tab; `tab_strip(None)` marks nothing: both pass on base by design). `--runxfail` on a clean archive of `e475bd9` plus the corrected `tests/test_inc9e.py`: **15 failed, 2 passed**, each for the stated reason: the home strip says `c browse` (not `c browse maps`); the map strip paints `['c','p','n','f']`; a relabelled seat is not reflected; `hint_line` returns `siguiente ▸ probe`; `settings.py` passes `Constant('s')`; the home order is `['maps','open','exit','global']`; the home bar starts `maps j next map …`; the palette's first row is `app     palette  ctrl+p`; the footer is ` 14/14 acciones   ↵ ejecutar   esc cerrar`. Output: `%TEMP%\inc9e\inc9e_red_base.txt`. Honest limit: see `INC9E-F3` (the committed `35e77fb` arms did not reach the factory; fixed in `e8283e0`).

### Mutants (`executed`)

Harness outside the repo (`%TEMP%\inc9e\mutants9e.py`): per mutant a sha256 pin of every touched file, byte-level edits in each file's own line endings, the killing tests (`tests/test_inc9e.py`, `-x`), the verdict **printed before** the restore, the pins re-checked. Run on `0a37fb6`. **17 of 17 KILLED; 17 of 17 pins matched after restore; the tree was clean afterwards.**

| # | Mutant | File | Killing arm | Verdict |
|---|---|---|---|---|
| L1a | letters on every strip whose active tab is the first door (the map gets them back) | `darkside.py` | `l1_no_other_screen_paints_a_key_letter` | **KILLED** |
| L1b | letters everywhere | `darkside.py` | same | **KILLED** |
| L1c | home labels hand-written, equal to today's seat | `darkside.py` | `l1_the_strip_follows_a_relabelled_seat` (sentinel) | **KILLED** — the equality arm SLIPS PAST |
| L1d | non-home names hand-written | `darkside.py` | sentinel | **KILLED** |
| L1e | home strip back to `browse` / `build` | `darkside.py` | `l1_home_strip_paints_each_tab_letter_and_its_seat_label` | **KILLED** |
| L2 | prefix back to `siguiente ▸` | `darkside.py` | `l2_no_hint_line_says_siguiente` | **KILLED** |
| F6a | components screen passes `"s"` again | `settings.py` | `cr_f6_the_components_screen_passes_none` | **KILLED** |
| F6b | `None` marks the first tab | `darkside.py` | `cr_f6_none_marks_no_tab` | **KILLED** |
| L3 | `maps` before the doors | `keymap.py` | `l3_home_bar_and_legend_order_start_with_open` | **KILLED** |
| P1 | raw group id painted | `palette.py` | `palette_paints_header_words_in_the_bar_order[home]` | **KILLED** |
| P2 | headers hand-written, equal to today's | `palette.py` | `palette_headers_follow_a_relabelled_seat` (sentinel) | **KILLED** — the equality arm SLIPS PAST |
| P3 | sorted by raw group id again | `palette.py` | `…bar_order[home]` | **KILLED** |
| P4 | footer count word `acciones` | `palette.py` | `palette_footer_and_placeholder_are_english` | **KILLED** |
| P5 | footer run word hand-written | `palette.py` | `palette_footer_words_come_from_the_seat` (sentinel) | **KILLED** |
| P6 | footer close word hand-written | `palette.py` | same | **KILLED** |
| P7 | placeholder `/comando` | `palette.py` | `…footer_and_placeholder_are_english` | **KILLED** |
| P8 | sorted by header word alphabetically | `palette.py` | `…bar_order[home]` | **KILLED** |

"SLIPS PAST" for L1c and P2 is by construction (the pre-sentinel arms compare with the seat's current value), not re-run against the old arms.

### Lane, ruff, guards

- Baseline: **1541 passed, 3 xfailed, 20 deselected, 0 failed** (`e475bd9`).
- Full lane on the final code tree (`0a37fb6`): **1558 passed, 3 xfailed, 20 deselected, 0 failed** (1242 s). Reconciliation: 1541 + 17 (`test_inc9e.py`) = 1558; xfailed and deselected unchanged.
- `ruff check .` at the repo root, same command, base = a local clone at `e475bd9`: **26 and 26**; the multiset difference (file and rule, line numbers dropped) is **empty both ways**.
- `tests/test_fold.py` + `tests/test_no_operator_paths.py`: 21 passed, 3 xfailed (the pre-existing marked ones), before this commit.
- Every commit's staged diff and message were byte-scanned for Cc/Cf/Zl/Zp/Cs and for the account name (read from `$USERNAME`, never printed): CLEAN on all four code commits; `git log -1 --format=%B` shows the `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>` trailer on each.

## Renders (`executed`; saved OUTSIDE the repo)

`%TEMP%\inc9e\renders\` (harness `%TEMP%\inc9e\render9e.py`): text dumps of the composited frame, `{home, map, factory, components, connect-repo, palette-from-home, palette-from-map}-{118x34, 87x34, 140x45}.txt` (21 files). Read from the dumps:

```
home 87x34, strip:  ' c browse maps    p connect repo    n build map    f factory      ◕ mapper'
home 87x34, bar:    'open c browse maps  p connect repo  n build map  t from template … +10  ? all keys'
home 118x34, bar:   'open c browse maps  p connect repo  n build map  t from template  i import csv  f factory … +8  ? all keys'
map/factory/components/connect repo, strip (all sizes read):  ' browse maps    connect repo    build map    factory   ◕ mapper'
palette from home:  open x8, maps x3, exit, global x2, footer ' 14/14 actions   ↵ run   esc close'
```

Not measured: the strips below 87 columns (the home tab row is 61 cells before the wordmark; the existing wrap and `max-height: 3` lid are unchanged, but I did not re-measure the narrow band), and no colour was inspected (text dumps only).

## 5 · Risks

- `INC9E-F1`: home is recognised by `crumb is None and active == first door`, not by a flag.
- The home tab row grew 9 cells (the longer seat words); where it wraps to the lid earlier than before is unmeasured.
- `darkside.py` now depends on `keymap` (one direction, no cycle). The strip reads the seat when it renders, so a relabelled seat shows only after the next render (`on_resize` or `set_crumb`).
- The palette's header column is sized per scope (6 cells on both home and the map: `global` is the longest), narrower than the old fixed 8.

## 6 · Pending items

`INC9E-F1` (a `letters` flag, 2 files), `INC9E-F2` (`n siguiente` in the search hint, with `Inc-EN`), and the carries of `increment-029` (`INC9D-F2`, `F3`, `F4`; the Spanish toasts, `B-71`). Not started: Inc-EN, and any review of Inc-9e.

## 7 · Suggested next task

The three reviews of Inc-9e (code, ux, security), then `Inc-EN` with `INC9E-F2` folded in.
