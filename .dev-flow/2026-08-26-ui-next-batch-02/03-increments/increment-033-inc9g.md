# Increment 033 -- Inc-9g: the Inc-9f review defects

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `2d1a1b8`. Authority: the Inc-9f
independent reviews, the coordinator's rulings, and `N1` (`VERDICT-inc9-2026-09-30.md`, Round 4).
Amendment: `A-115` (appended to `01-requirements.md`). Findings are named `INC9F-*`.
Not here: `N2` (arrows in the palette footer) goes to `Inc-EN`.

## 1. What changed (per finding)

| id | Change | Evidence state |
|---|---|---|
| `INC9F-UX-F1` | `palette.py`: the selected row is repainted in one ground-on-accent colour (`#000000` on `#1783ff`, 5.7:1) by `on_list_view_highlighted`; the unselected rows keep their three colours. Before: the key was `#1783ff` on `#1783ff` (1.0:1), the group word 3.1:1, the label 3.36:1 | executed (composited per-cell fg/bg, home and map scope, 118 and 87, relabelled seat) |
| `INC9F-SEC-F1` | `github.py`: mirror directory `<name>-<sha256(normalised url)[:12]>`; normal form: strip, trailing `/`, `.git` | executed (stub; real local git under `network`) |
| `INC9F-SEC-F2` | `app.py`: `Static(Text(darkside.plain(self.repo)))`. The crumb already painted a `Text`; the arm pins both. `a[/b]` used to raise `MarkupError` | executed (Pilot, painted frame, every segment's link and meta) |
| `INC9F-SEC-F3` + `INC9F-CR-F4` | `github.py`: a cache-hit fetch that times out or exits non-zero continues on the mirror, with the 120 s budget; `on_stale` / `GitHubConnector.stale` carry the category; `app.py`: `RepoScreen` toasts `showing the cached copy: <category>` (`plain()`, markup off) | executed (stub; Pilot toast; budget read from the call's `timeout`) |
| `INC9F-SEC-F4` | `github.py`: owner `[A-Za-z0-9-]+`, name `[A-Za-z0-9._-]+`, not `.` or `..`; refused before any process, fixed sentence | executed (11 malformed, 4 well-formed) |
| `N1` / `INC9F-UX-F2` | `app.py`: `home_hint(has_maps)`; no maps gives `choose a door`; the hint is refreshed on every home refresh | executed (painted home frame, both states, 118 and 87, relabelled seat) |
| `INC9F-CR-F1` | arm only: 6 overlapping stderr samples, one per precedence pair, exact equality (classifier and clone message) | executed |
| `INC9F-CR-F2` | arm only: 4 `gh` samples, each with its exact message | executed |
| `INC9F-CR-F3` | arm only: `fact`, left, left, `x`, home, `y` gives `yfaxct`; end, `z` gives `yfaxctz` | executed |
| `INC9F-CR-F5` | `github.py`: marker narrowed to `permission denied (publickey`; a local `Permission denied` is `unknown (exit 128)` | executed |
| `INC9F-CR-F6` | `github.py`: `_TIMED_OUT` and `CATEGORIES` declared once | executed |
| item 13 | `github.py`: `_git_env()` (`LC_ALL=C`, `GIT_TERMINAL_PROMPT=0`) on every git call, `_run_git` and the clone | executed (env recorded on every git call of a connect) |
| item 14 | `github.py`: `_refuse_unsafe` strips before the `::` check | executed |

## 2. Decisions and deviations (declared)

- **`_git_env()` is a function, not a module-level dict.** The brief said "one module-level env". A dict built
  at import snapshots `os.environ` (HOME included), so a test's temp `HOME` would not reach git and every
  hermetic arm would read the real profile. The mutant `ENV-snapshot-at-import` is killed by the HOME check.
- **`CATEGORIES` is imported by the new arms through an oracle, not copied in.** The brief asked the tests to
  import it instead of keeping their own copy. `test_inc9f.py` keeps its literal tuple, because an arm that
  imports the value it checks compares code to itself; `test_inc9g_cr_f6_the_declared_set_is_the_set_the_operator_ruled`
  pins the two to be equal, and the mutant that drops a category is killed by it.
- **Items 7-14 were implemented before their arms were committed.** They arrived while items 1-6 were landing.
  RED was shown on `2d1a1b8` from an archive copy instead of an arms-first commit (section 4). The arms for
  items 1-6 were committed RED first (`36c1701`, `8d74b73`).
- **Changed existing arms (declared; no assertion weakened):**
  1. `test_inc9f.py::test_inc9f_f1_the_clone_argv_ends_options_before_the_url`: the target directory is no
     longer `widget`, it is `widget-<hash>`; the assertion `endswith("widget")` became
     `Path(...).name.startswith("widget-")`. A value change by `A-115` st. 2.
  2. `test_inc9f.py::test_inc9f_m1_the_home_hint_names_enter_and_invites_a_door` and
     `..._follows_a_relabelled_seat`: they now seed one saved map before the app starts, because with no map
     the hint no longer names `↵` (`N1`). Setup only; the assertions are untouched. The no-map state is the
     new arm.
- **The stale toast carries the fixed category only**, never git text. Its severity is `warning`.
- **A git that is not installed on a cache hit** still raises (`git CLI not found`): only the timeout and a
  non-zero exit are the stale path.
- **Selected row colour:** one colour (`#000000`) for group, label and key. The three-tone hierarchy of the
  unselected row does not survive on the accent ground (the two greys are under 4.5:1 on it).
- File count: **3 source files** (`github.py`, `app.py`, `screens/palette.py`), at the cap. Tests and docs uncapped.

## 3. Arm table, RED on `2d1a1b8` (archive copy of the base; `CATEGORIES = ()` shim appended to its `github.py`
because the new arms import that name) and GREEN on HEAD

Command: `pytest tests/test_inc9g.py --runxfail -m "not network"` in the archive: **44 failed, 27 passed**, plus
the one `network` arm RED (1 failed) = 45 RED.

| group | arms RED on base | arms green on base (controls / pins; killed by a mutant instead) |
|---|---|---|
| UX-F1 legibility | 8 + 1 (`every_glyph...` x8, `highlight_moves...`) | none |
| SEC-F1 | `two_remotes...`, `directory_keeps_the_readable_name`, network `real_git...` | `the_same_url_still_hits_its_own_mirror` |
| SEC-F2 | 6 (3 texts x 2 widths) | none |
| SEC-F3 | `fetch_timeout_on_a_cache_hit...` | `a_clone_timeout_is_still_an_error` |
| SEC-F4 | 11 malformed | 4 well-formed |
| N1 | `no_recent_maps...` x2, `relabelled_seat_word...` | `with_recent_maps...` x2 |
| CR-F1, CR-F2, CR-F3 | none (pins) | all |
| CR-F4 | stale flag x2, fresh flag, screen toast x2 | `a_fresh_connect_does_not_toast...` |
| CR-F5 | `local_permission_denied...` | `ssh_key_refusal...` |
| CR-F6 | `declared_set...`, `timeout_is_spelled_once` | none |
| item 13, 14 | env arm, 3 padded-helper | none |

HEAD: `tests/test_inc9g.py` all green; arms listed as controls are green by construction (a pin has no RED on
the base: it is killed by its mutant, section 4).

## 4. Mutant table (harness in the session scratchpad, outside the repo; run on a copy of HEAD; sha256 pinned, byte-level in the file's own line endings, verdict printed before restore, pin re-checked: OK every time)

| mutant | verdict | killed by |
|---|---|---|
| selected key keeps ACCENT | RED | `every_glyph_on_the_selected_row_is_legible` |
| selected row never painted | RED | same |
| previous row not reset on move (`i <= lit`) | RED | `the_highlight_moves_the_legible_paint_with_it` |
| highlight handler absent | RED | `every_glyph...` |
| mirror keyed on the name only | RED | `two_remotes_with_one_last_segment...` |
| mirror directory loses its readable name | RED | `the_directory_keeps_the_readable_name` |
| repo name back to `Static(str)` | RED | `typed_repo_text_is_shown_literally[a[/b]]` |
| fetch timeout re-raised | RED | `sec_f3` and `cr_f4` arms |
| owner unchecked / name unchecked / `.` `..` allowed | RED x3 | `malformed_owner_name_never_reaches_gh` (`../user`, `o/n?x=1`, `o/..`) |
| home hint always `↵ open map` | RED | `no_recent_maps_the_hint_only_invites_a_door` |
| hint never refreshed after mount | RED | same |
| classifier order reversed / rotated | RED x2 | `when_two_categories_match_the_earlier_one_wins` |
| `gh` category fixed to one word | RED | `a_gh_failure_is_its_own_category_exactly` |
| `left` forwarded / `home`+`end` forwarded from the search box | RED x2 | `editing_keys_edit_the_search_box` |
| stale never flagged / non-zero fetch ignored / fetch budget 30 s | RED x3 | `the_connector_flags_a_stale_mirror` |
| screen never toasts / screen loses the flag | RED x2 | `the_repo_screen_loads_the_cached_copy_and_toasts` |
| `permission denied` broad again | RED | `a_local_permission_denied_is_not_an_authentication_failure` |
| timeout spelled as a literal / category dropped from the set | RED x2 | `timeout_category_is_spelled_once`, `declared_set...` |
| prompt allowed / locale dropped / env not passed (read) / env not passed (clone) / env snapshot at import | RED x5 | `every_git_call_runs_in_a_no_prompt_english_environment` |
| transport-helper check unstripped | RED | `refuse_a_padded_transport_helper` |

Not run: the stale-toast `markup=False` mutant. The harness skipped it (the old text occurs twice), and the
toast carries only a fixed category, so `markup=True` would be an equivalent mutant. Not claimed.

## 5. Test results

| check | state |
|---|---|
| `tests/test_inc9g.py`, default lane | executed: 71 arms green in the full lane |
| the one `network`-marked arm (`real_git_two_local_remotes...`), local bare repositories, HOME in a temp dir | executed: green on HEAD, RED on the base |
| Full lane, first run at `e34e65a`: **1 failed, 1680 passed, 3 xfailed, 21 deselected**, 22:39 | executed. The 1 failure was `test_fold`: my arm file spelled two code points as literals; fixed in the next commit, `test_fold` + `test_no_operator_paths` + `test_inc9g` re-run green (92 passed) |
| Full lane, final run | **1681 passed, 3 xfailed, 21 deselected, 0 failed**, 19:02 (at `4f6b568`; reconciled with 1610: +71 arms in `test_inc9g.py`, the `network` arm deselected) |
| `ruff check .` against `2d1a1b8`, set difference (line numbers stripped) | executed: new = none, gone = none (the base archive also lists `prototypes/`, which the working tree does not carry; excluded from both sides) |
| Known flakes (`test_llr_cnv_3_1...`, `test_hlr_n16_4_legend_declares_its_own_keys[size2]`) | not hit |

## 6. Renders of the palette (text frames; the selected row's colours are asserted per cell, printed here)

Home scope, 118x34, `down` twice (third row, `build map`, selected):

```
 c browse maps    p connect repo    n build map    f factory                                                  ◕ mapper
                                                   ◕ mapper   home
c browse maps   abre un mapa reciente
...
                    open    browse maps    c
                    open    connect repo   p
                    open    build map      n          <- selected
                    open    from template  t
 ...
                    14/14 actions   ↵ run   esc close
next ▸ choose a door
```

Selected row, per segment (text, fg, bg): `('open    ', '#000000', '#1783ff')`, `('build map      ', '#000000', '#1783ff')`,
`('n', '#000000', '#1783ff')`: 5.73:1 each. At 87x34 the same three segments, same colours. Both frames are
in `renders/palette-home-118x34.txt` and `palette-home-87x34.txt` in the session scratchpad. The no-map
home hint reads `next ▸ choose a door`. Text frames show layout, not colour; the colours above are measured.

## 7. Risks, carries, next

- **Carries.** (1) `LC_ALL=C` is not measured against a localised `git` (none on this machine). (2) The stale
  toast is a toast: the stage panel does not carry it. (3) `gh` runs in the process environment (no
  `LC_ALL`). (4) The palette footer's arrows: `N2`, `Inc-EN`. (5) `ssh`-form URLs get the dash and `::`
  rules only. (6) The 12-hex mirror key is a cache key, not a security boundary. (7) Spanish strings remain on
  the repo screen: `Inc-EN`. (8) Existing mirrors under the old name (`<name>` without a hash) are orphaned,
  not migrated or deleted: the first connect after this change clones again.
- **A stash entry was left by mistake** (`stash@{0}`, "WIP on feat/ui-next-batch-02: 8d74b73"): a `git stash`
  in a compound command; the working tree was restored from it and the tree is clean. Dropping it was
  denied by the permission classifier, so it is left for the operator. It holds nothing that is not committed.
- **Next.** `Inc-EN` (not started), carrying `N2`.

## Commits

`36c1701` arms (RED) · `4764561` github items · `8d74b73` N1 arms (RED) + 9f seed · `8ad867d` app items ·
`78459bd` palette · `e34e65a` review items 7-14 · `28c6c6d` the `test_fold` escape fix · `4f6b568` docs (this record, `A-115`); a last docs commit fills in the final lane line.
