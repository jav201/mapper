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

---

# Round 3 — after the Inc-9d / Inc-SEED-2 / Inc-9e reviews (2026-09-30, base `bd7d673`)

All three lenses PASS: code (uninterrupted lane 1558 passed / 0 failed; FLAKE-1/2 green), security
(no HIGH/MEDIUM; every closure re-executed), ux PASS-WITH-FINDINGS (the eight previous findings
discharged on the painted frame). Two questions were put to the operator; both took the recommended
option.

| id | Question | Answer (verbatim label) | What it rules |
|---|---|---|---|
| M1 · R3-UX-F6 | With the doors first (L3), the home bar never shows `↵ open map` | Ponerlo en la pista de home | The home hint carries `↵ open map` (seat-derived) alongside the invitation to choose a door; the bar is unchanged |
| M2 · R3-UX-F2 | A failed clone says only `git clone failed (exit 128)` | Categorías fijas | Code classifies git's failure into a FIXED set (`host not found`, `not found or private`, `authentication required`, `network unreachable`, `unknown (exit N)`); git's own text is never painted (it names paths, the URL may carry a token); the failure is also painted in the repo screen's stage panel so it outlives the toast |

## Coordinator rulings — Inc-9f scope (defects)

- **Argument injection (from the code review's hand-off, unverified):** `git clone --mirror <url> <target>`
  passes the URL positionally without `--`; a value starting with `-` reaches git as an option. Verify
  reachability with an arm; fix with `--` and by refusing a URL that starts with `-`. Highest priority.
- **R3-CR-F7 (pre-existing, measured):** the cache-hit check looks for `.git`, but `--mirror` is bare,
  so reconnecting a repo always fails. Check `HEAD` instead.
- **R3-SEC-F1:** clone timeout; `_gh` no longer echoes `gh` stderr (same fixed-category treatment).
- **R3-UX-F1 (pre-existing):** the palette never paints its selected row (CSS `--highlight` vs Textual's
  `-highlight`) and arrows do nothing while the Input holds focus. **R3-UX-F7** keys aligned in a column.
- **R3-CR-F1** census holes (re-raising handlers, generator expressions), **R3-CR-F2** palette width pin,
  **R3-CR-F3** home passes the seat key, not the literal `"c"`, **R3-CR-F5** stale assert,
  **R3-CR-F6** record miscount.
- Source files: `github.py`, `app.py`, `screens/palette.py` (3 of the operator's 4).


---

# Round 4 — after the Inc-9f reviews (2026-09-30, base `ce8b240`)

Security PASS (no HIGH; INC9F-SEC-F1..F4 routed to Inc-9g), ux PASS except INC9F-UX-F1 (selected
palette row's key invisible, routed to Inc-9g); the code review was still running when these answers
were taken. Four questions were put to the operator; each answer took the recommended option.

| id | Question | Answer (verbatim label) | What it rules |
|---|---|---|---|
| N1 · INC9F-UX-F2 | With no recent maps the home hint says `↵ open map` and `↵` does nothing | Ocultar «↵ open map» | When there is nothing to open the home hint drops the `↵ open map` part and keeps only the invitation to choose a door. Routed to Inc-9g (`app.py`) |
| N2 · INC9F-UX-F4 | The palette footer does not advertise the arrows | Agregar ↑↓ al pie | The footer reads `↑↓ move · ↵ run · esc close`, seat-derived. Routed to Inc-EN (needs `keymap.py`) |
| N3 · INC9F-UX-F5 | `▲ failed` is painted INK | Dejarlo en blanco | INK stays; amber remains reserved for attention / pending |
| N4 · Inc-9f decisions | Ratify the implementer's four decisions | Ratificar las cuatro | Clone timeout 120 s (reads 30 s); `--end-of-options` (git >= 2.24); `▲` in INK; `timed out` in the fixed category set |

---

# Round 5 — after the Inc-9g reviews (2026-10-01, base `3dbd5a4`)

Security PASS (five LOW). Code BLOCK-UNTIL INC9G-CR-F1 and ux FAIL on the same defect (INC9G-UX-F1):
after any filter edit the palette's first row is painted GROUND on the plain row ground (1.12:1) while
`↵` still runs it — introduced by Inc-9g's repaint (`ListView.clear()` not awaited). Routed to Inc-9h
with the remaining findings. Two questions were put to the operator; both took the recommended option.

| id | Question | Answer (verbatim label) | What it rules |
|---|---|---|---|
| P1 · INC9G-UX-F2 / INC9G-SEC-F3 | The stale cached copy is toast-only; the panel reads `listo · 100%` | Línea fija en el panel | The repo stage panel paints `▲ cached copy: <category>` in INK (as N3) for as long as the cached copy is shown; the toast stays and gains `· q back to retry` |
| P2 · INC9G-UX-F3 | `conectado: N nodos` and the stale warning fire together and contradict | Un solo aviso | On a stale connect only the warning fires, carrying the count: `showing the cached copy (N nodes): <category>` |

---

# Round 6 — Inc-9h landed (2026-10-01, `8e8f9f0..134d74c`)

The Inc-9h implementer found that two coordinator-specified arms conflict (`…/r` vs `…/r.git` distinct;
`tools`, `tools/`, `tools.git`, `tools.git/` one mirror) and resolved it: the directory key keeps the
A-115 normal form, a cache hit compares the mirror's `remote.origin.url` with the typed URL (`.git` kept),
and a mismatch gets its own directory keyed on the typed form.

| id | Question | Answer (verbatim label) | What it rules |
|---|---|---|---|
| Q1 · INC9G-SEC-F1 | In the repo cache, are `…/r` and `…/r.git` one repo or two? | Distintos, se acepta doble clon | Two remotes; a repo is never shown under another's URL; `tools` then `tools.git` from one cache clones twice, accepted |

---

# Round 7 — Inc-9i ux review (2026-10-01, base `e865d43`)

ux PASS-WITH-NOTICES (the three Inc-9i changes discharged). One question was put to the operator; the
answer took the recommended option. Code and security reviews were still running when it was taken.

| id | Question | Answer (verbatim label) | What it rules |
|---|---|---|---|
| R1 · INC9I-UX-F1 | A refused credential URL is still painted, token included (crumb, repo name), and kept in the field after `q` | Ocultar en pantalla, campo se queda | Every surface that paints a typed URL redacts userinfo (`https://***@host/…`); the connect-repo field keeps the operator's own text for correction (never persisted). Routed to the next increment with the Inc-9i review findings |

---

# Round 8 — Inc-9j reviews (2026-10-01, base `c8a692d`)

ux PASS-WITH-NOTICES (R1 discharged), security PASS (INC9I-SEC-F1 verified closed against libcurl's own
parser and git's credential parser; INC9J-SEC-F1 MEDIUM: credential forms without `://` are painted
unredacted). The code review was still running when this answer was taken. Four rounds in a row found a
new odd URL form, so the coordinator proposed replacing the deny-list with an allow-list. The answer took
the recommended option.

| id | Question | Answer (verbatim label) | What it rules |
|---|---|---|---|
| S1 · INC9J-SEC-F1/F3, INC9J-UX-F1 | Replace the URL deny-list with a closed allow-list? | Lista cerrada | A typed repo URL is accepted only as `https://host[:port]/path` or `git@host:path`, simple characters only (no `@` before the host, no userinfo, no `?`, `#`, whitespace, backslash, extra or encoded slashes; ASCII host). Everything else is refused before any process with one fixed sentence that echoes nothing, and every painted surface shows `(unrecognised URL)` instead of the text. The connect field keeps the typed text (R1). The deny-list pieces (`_refuse_userinfo`, `redact_userinfo` heuristics) become redundant and are removed or reduced to the allow-list. `owner/name` (gh path) is unchanged |

Coordinator rulings for the same increment: INC9J-UX-F1 (no-host URL told to use a credential helper)
is subsumed — the allow-list refusal sentence names no cause beyond "not a supported repository URL".
INC9J-UX-F3 (palette test raced once) is logged as FLAKE-3 candidate for the whole-branch gates.

---

# Round 9 — Inc-9k ux review (2026-10-01, base `c6b9d32`)

ux PASS-WITH-NOTICES (S1 display and the accepted forms discharged). Three questions were put to the
operator; each answer took the recommended option. Code and security reviews were still running.

| id | Question | Answer (verbatim label) | What it rules |
|---|---|---|---|
| T1 · INC9K-UX-F1 | The refusal sentence does not say how to write an accepted repo | Decir las formas | The fixed sentence becomes `refusing the repository: use https://host/path, git@host:path, owner/name or a local folder` (still echoes nothing). Routed to the next increment |
| T2 · INC9K-UX-F3 | Refuse `http://`? | Rechazarlo | Ratifies the coordinator default: https only |
| T3 · INC9K-UX-F2 | `?` in the connect field opens help instead of typing | Corregir en Inc-EN | In a text field `?` types; help stays on `?` outside fields. Routed to Inc-EN with B-36 / B-72 |

---

# Round 10 — Inc-9m reviews (2026-10-01, base `c2af781`)

security BLOCK-UNTIL INC9M-SEC-F1 (HIGH, pre-existing: a sidecar `documents[].path` such as `\host\s\a.docx`
is stat'ed when the factory screen opens — SMB/NTLM exposure from a shared map); code OK (no HIGH;
CR-F1 device names, CR-F2 refused-vs-not-found, CR-F3 badge arm, CR-F4 POSIX scope); ux PASS-WITH-NOTICES.
Two questions were put to the operator; both took the recommended option.

| id | Question | Answer (verbatim label) | What it rules |
|---|---|---|---|
| U1 · INC9M-UX-F1 / CR-F2 | A refused path and a missing file both toast `archivo no encontrado` | Aviso propio | A refused path toasts a name-free English sentence, `path not supported: use C:\… or a relative path`; a missing accepted path keeps naming its file. The prompts' placeholders become forms the grammar accepts |
| U2 · INC9M-UX-F3 | A `file` attachment pointing at a network share is refused only at open time | Rechazar al agregar | The local-path rule stays (no network targets); the refusal happens when the attachment is added, with the U1 sentence, not later at open time |

---

# Round 11 — Inc-9n reviews (2026-10-01, base `287681f`)

security BLOCK-UNTIL INC9N-SEC-F1 (HIGH, pre-existing: the sidecar `documents[].name` chooses where
"generate office" writes — `..`, drive-absolute and UNC names reproduced); code OK (CR-F1 relative
workspace, CR-F2 three drifting containment copies, CR-F3 FLAKE-3 diagnosed as a test race, MEDIUM);
ux PASS-WITH-NOTICES. Disclosure: the security reviewer's harness once let a real `resolve()` through to
a link whose target named a non-existent host (`SPYHOST`), which may have caused one name lookup.
Two questions were put to the operator; both took the recommended option.

| id | Question | Answer (verbatim label) | What it rules |
|---|---|---|---|
| V1 · INC9N-UX-F2 | `C:\outside\x.pdf` refused with "use C:\… or a relative path" reads as a contradiction | Segunda frase fija | A path refused for lying outside the workspace toasts `attachment must be inside the workspace: use a relative path` (at add and at open); the U1 sentence stays for UNC, `/x`, `C:x` and devices |
| V2 · INC9N-UX-F1 | The factory says "template file not found" for a template that exists outside the workspace | Decir la causa y la salida | It says `template outside the workspace: import it with i`, derived from the text without touching the disk |
