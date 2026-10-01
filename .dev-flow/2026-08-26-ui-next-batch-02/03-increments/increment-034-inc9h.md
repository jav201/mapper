# Increment 034 -- Inc-9h: the Inc-9g review defects

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `8e8f9f0`. Authority: the Inc-9g
independent reviews and the operator's `P1`, `P2` (`VERDICT-inc9-2026-09-30.md`, Round 5). Amendment: `A-116`
(appended to `01-requirements.md`, dated 2026-10-01). Findings are named `INC9G-*`.

## 1. What changed (per finding)

| id | Change | Evidence state |
|---|---|---|
| `INC9G-CR-F1` = `INC9G-UX-F1` | `palette.py`: `on_mount`, `_refresh_list`, `on_input_changed` are `async`; `_refresh_list` does `await list_view.clear()`. Confirmed by me (arm RED on the base, GREEN with the one `await`; mutant `PAL-1` puts it back and goes RED) | executed |
| `P1` (= `INC9G-UX-F2` / `SEC-F3`) | `app.py` `RepoScreen._stages_text`: after the four stages, while `self.stale` and not loading, the line `▲ cached copy: <category>` in INK (through `plain()`) | executed (Pilot, composited fg per glyph, 118 and 87, after `clear_notifications()`) |
| `P2` (= `INC9G-UX-F3`) | `app.py` `RepoScreen.on_mount`: stale connect fires ONE warning `showing the cached copy (N nodes): <category> · q back to retry`; the `conectado: N nodos` toast is the `else`. `q back` is `hint_pair(SCOPE_REPO, 'home')` | executed (toast list counted; relabelled seat) |
| `INC9G-SEC-F1` | `github.py`: on a cache hit `git config --get remote.origin.url` is compared with the URL as typed; a mismatch gives this URL its own directory, and a second mismatch is refused. **Declared: I chose re-clone into a fresh directory (and refuse only when that directory is foreign too), not refuse alone** (section 2) | executed (stub; real local git under `network`) |
| `INC9G-SEC-F2` | `github.py`: refresh is `fetch --prune --all` | executed (argv; real local git, branch deleted on the remote) |
| `INC9G-SEC-F4` | `github.py`: one fixed sentence for every malformed `owner/name`, segment count included; the clone messages show the last segment through `plain()` | executed |
| `INC9G-SEC-F5` | `github.py`: `gh` runs with `GH_PROMPT_DISABLED=1`; `diff.py`: `git show` runs with `env=_git_env()` (imported from `github.py`; no cycle: `github.py` imports only `darkside` and `model`) | executed |
| `INC9G-CR-F2` | arm only: home hint across a push and a pop; **plus** `HomeScreen.compose` now yields `HintLine(home_hint())` (the glob is no longer written twice; `on_mount` sets the real hint before any paint) | executed |
| `INC9G-CR-F3` | arm only: four spellings, one mirror name, no second clone | executed |
| `INC9G-CR-F5` | `github.py`: `GitHubTimeout(GitHubError)`, raised by `_run_git`; `_refresh_mirror` catches only it. Arm: a missing git on a cache hit raises | executed |
| `INC9G-CR-F6` | `github.py`: `url = url.strip()` once at the top of `_ensure_cloned` | executed |
| `INC9G-CR-F7` | `github.py`: `self.stale = ""` at the top of `fetch()` | executed |

## 2. Decisions and deviations (declared)

- **`INC9G-SEC-F1`: re-clone into a fresh directory, refuse only as a last resort. The brief's pair of arms
  conflict as literally read, and I resolved it this way.** The brief says compare `remote.origin.url` with the
  requested URL "normalised the same way", and asks for an arm with two distinct bare repos `.../c/r` and
  `.../c/r.git`; it also asks (`CR-F3`) that `tools`, `tools/`, `tools.git`, `tools.git/` give one mirror path and
  no second clone. A comparison on the `A-115` normal form (which drops `.git`) cannot tell `r` from `r.git`, so the
  `r`/`r.git` arm cannot pass; a comparison that can tell them re-clones when one cache sees both spellings of
  one GitHub repo. I kept the `A-115` key (so the four spellings still key ONE directory: `CR-F3` holds as an arm
  that connects each spelling in its own cache and then again, and that kills `O4`) and made the cache-hit
  comparison read the URL as typed (stripped, trailing `/` dropped, **`.git` kept**). On a mismatch the URL is
  keyed on that typed form into its own directory; only if that directory is foreign too does the connect refuse
  (fixed sentence, no URL echoed; reachable only when the key and the typed form coincide, i.e. a collision or a
  tampered cache). **Cost, declared:** `tools` and `tools.git` used from the SAME cache are cloned twice. Not
  measured at scale; a user who types one spelling never pays it. If the operator prefers the other reading (one
  mirror per normal form, `r`/`r.git` conflated), the change is one line in `_is_mirror_of`.
- **Arm changed after its RED commit (mine, not an existing arm).** The committed RED arm
  `..._a_mirror_that_holds_another_remote_is_refused_not_reused` assumed "refuse". With the design above a
  foreign mirror under a `.git` URL gets a fresh directory, and only a URL with no `.git` and no `/` is refused.
  It became two arms (`..._is_not_reused_this_url_gets_its_own`, `..._when_the_own_directory_is_foreign_too_the_connect_is_refused`),
  both RED on the base (section 3).
- **`HomeScreen.compose` takes `home_hint()`** (item 11, "only if trivial"). It is one line, but `home_hint()`'s
  default is "has maps": the first, unpainted hint is the maps variant until `on_mount` (synchronous, before any
  paint) sets the real one. If `on_mount` ever raised before `set_hint`, the hint would be the maps variant. The
  N1 arms and the push/pop arm pass; `HOME-1` (the `on_mount` line removed) is killed.
- **Changed existing arms (declared; no assertion weakened):**
  1. `tests/test_inc9g.py::test_inc9g_cr_f4_the_repo_screen_loads_the_cached_copy_and_toasts`: it asserted
     `showing the cached copy: <category>` is among the toasts. `P2` changes that text, so it now asserts the
     exact new sentence (`... ({N} nodes): <category> · {seat's way back} to retry`), N read from the screen's graph.
  2. `tests/test_inc9f.py::_Mirror` (setup helper): the clone records the URL it was given and answers
     `git -C <mirror> config --get remote.origin.url` with it, as git does; unknown mirror gives exit 1. Needed
     because the cache hit now reads the origin. No assertion touched.
- **Timeout inside the origin read of a cache hit is an error, not stale** (only the refresh has a stale path).
- **`could not query '<repo>'` still echoes `self.repo`**: it is reached only after the spec matched
  `[A-Za-z0-9-]+/[A-Za-z0-9._-]+`, so there is nothing to filter. Not changed.
- **`O2`, `O3`, `O4`, `O5` and `R8`: I did not have the reviewers' mutant texts**, only the brief's one-line
  descriptions. The exact text I used for each is in section 4; if a reviewer meant a different mutation, that
  one is not claimed.
- File count: **4 source files** (`palette.py`, `github.py`, `app.py`, `diff.py`), at the cap. Tests and docs uncapped.

## 3. Arm table (43 arms in `tests/test_inc9h.py`: 41 default lane + 2 `network`)

RED on `8e8f9f0`: the arms file and the two test-file edits copied into a detached `git worktree` of the base in
`%TEMP%` (no stash); `pytest tests/test_inc9h.py -m "not slow"` there: **34 failed, 9 passed**. The first commit of
the arms (`f0c52b0`, strict xfail, 42 arms then) showed `31 failed, 9 passed, 2 deselected` with `--runxfail` plus
2 network arms RED; the foreign-mirror arm was split in two afterwards and both halves were re-run RED on the base.
GREEN on HEAD: all 43 (`41 passed` default + `2 passed` with `-m network`, real local git).

| group | RED on the base (arms) | green on the base (pins; killed by a mutant instead) |
|---|---|---|
| `CR-F1` palette | 4 filter+backspace (home/map x 118/87), 2 no-match-then-clear in map scope (x 2 sizes), 1 `↵` runs the lit row = 7 | no-match-then-clear in HOME scope x 2 sizes (the defect does not show there: measured) |
| `P1` panel line | 6 (3 categories incl. `unknown (exit 1)` x 2 sizes) | fresh connect paints no line x 2 |
| `P2` toast | 6 (3 categories x relabelled seat or not) | fresh connect fires only `conectado` x 2 |
| `SEC-F1` | `c/r` vs `c/r.git` (stub), foreign mirror gets its own dir, own dir foreign too is refused, network `c/r` vs `c/r.git` real git = 4 | four spellings, one name, no second clone |
| `SEC-F2` | argv `fetch --prune --all`; network: branch deleted on the remote is gone = 2 | |
| `SEC-F4` | 14 malformed specs share one sentence; clone message through `plain()` x 2 = 3 | |
| `SEC-F5` | `gh` env; `git show` env = 2 | |
| `CR-F2` | | push/pop home hint (kills `R8`, `O2`) |
| `CR-F5` | typed timeout; typed timeout is the stale category = 2 | missing git on a cache hit raises (kills `O5`) |
| `CR-F7`, `CR-F6` | stale reset; padded URL stripped once = 2 | |

## 4. Mutant table (harness `mutate.py` in the session scratchpad, outside the repo; run on a detached `git worktree` copy of HEAD in `%TEMP%`; sha256 pinned, byte-level I/O in each file's own line endings, the verdict printed before the file is restored, pin re-checked after every run: OK 33 of 33 in the full run, on `150943b`; then 6 targeted re-runs on `927da29`, pins OK). Run: `tests/test_inc9h.py -m "not slow" -x` (the targeted re-runs add `-k`). 33 mutants, 33 RED, 0 survived, 0 skipped. Every mutant is one replacement; `old` occurs exactly once.

Texts are written with `\n` for a line break (the file's own ending was used on disk).

| id | file | old -> new (exact) | verdict | first arm to fail |
|---|---|---|---|---|
| `PAL-1` (the original defect) | `palette.py` | `        await list_view.clear()` -> `        list_view.clear()` | RED | `cr_f1_row_zero..._after_a_filter_edit_and_after_backspace[size0-home]` |
| `PAL-2` (`O1`) | `palette.py` | `        self._labels = []\n        # Grouped` -> `        # Grouped` | RED | same arm, at `assert len(palette._labels) == len(items)`: `(24, 10)` |
| `PAL-3` | `palette.py` | `        if self._items:\n            list_view.index = 0\n` -> `        if False:\n            list_view.index = 0\n` | RED | same arm |
| `REPO-1` | `app.py` | `        if self.stale and not self.loading:\n` -> `        if False:\n` | RED | `p1_the_stage_panel_keeps_the_cached_copy_line[timeout...]` |
| `REPO-2` | `app.py` | `darkside.plain(f"▲ cached copy: {self.stale}"), darkside.INK)` -> `... darkside.MUT)` | RED | same |
| `REPO-3` | `app.py` | `        if self.stale and not self.loading:\n` -> `        if not self.loading:\n` | RED | `p1_a_fresh_connect_paints_no_cached_copy_line[size0]` |
| `REPO-4` | `app.py` | `f"▲ cached copy: {self.stale}"` -> `f"▲ cached copy: {self.stale.split()[0]}"` | RED | `p1_..._keeps_the_cached_copy_line[timeout...]` |
| `REPO-4b` (`O3`) | `app.py` | `f"▲ cached copy: {self.stale}"` -> `f"▲ cached copy: {self.stale.split(chr(40))[0]}"` (only `unknown (exit N)` changes) | RED | `p1_...[exit1-unknown (exit 1)-size0]`: painted `... ▲ cached copy: unknown` |
| `REPO-5` | `app.py` | `            else:\n                self.notify(darkside.plain(f"conectado: {count} nodos"), markup=False)\n` -> `            self.notify(darkside.plain(f"conectado: {count} nodos"), markup=False)\n` | RED | `p2_a_stale_connect_fires_one_warning...` |
| `REPO-6` | `app.py` | `{hint_pair(SCOPE_REPO, 'home')} to retry` -> `q back to retry` | RED | `p2_...[...-True]` (relabelled seat) |
| `REPO-7` | `app.py` | `f"showing the cached copy ({count} nodes): {self.stale} · "` -> `f"showing the cached copy: {self.stale} · "` | RED | `p2_...` |
| `REPO-8` | `app.py` | `f"{hint_pair(SCOPE_REPO, 'home')} to retry"),` -> `"retry"),` | RED | `p2_...` |
| `HOME-1` (`R8`) | `app.py` | `        self.query_one(HintLine).set_hint(home_hint(bool(mmd_files)))\n` -> `` (line removed) | RED | `cr_f2_the_home_hint_follows_the_maps_when_the_screen_resumes` |
| `HOME-2` (`O2`, as I read it) | `app.py` | `set_hint(home_hint(bool(mmd_files)))` -> `set_hint(home_hint(True))` | RED | same |
| `HOME-3` | `app.py` | `set_hint(home_hint(bool(mmd_files)))` -> `set_hint(home_hint(False))` | RED | same |
| `GH-1` | `github.py` | `    if (target / "HEAD").is_file() and not _is_mirror_of(target, url):\n        # \`INC9G-SEC-F1\`` -> `    if False:\n        # \`INC9G-SEC-F1\`` | RED | `sec_f1_c_r_and_c_r_dot_git_are_two_remotes_with_two_mirrors` |
| `GH-2` | `github.py` | `            raise GitHubError("refusing the cached copy: it belongs to another repository")\n` -> `            pass\n` | RED | `sec_f1_when_the_own_directory_is_foreign_too...` |
| `GH-3` | `github.py` | `target = _mirror_dir(cache_dir, name, url.rstrip("/"))` -> `target = _mirror_dir(cache_dir, name, _normalise_url(url))` | RED | `sec_f1_c_r_and_c_r_dot_git...` |
| `GH-4` | `github.py` | `result.stdout.strip().rstrip("/") == url.rstrip("/")` -> `_normalise_url(result.stdout) == _normalise_url(url)` | RED | `sec_f1_c_r_and_c_r_dot_git...` |
| `GH-5` | `github.py` | `["fetch", "--prune", "--all"]` -> `["fetch", "--all"]` | RED | `sec_f2_the_refresh_is_fetch_prune_all` |
| `GH-6` | `github.py` | `raise GitHubError("refusing the repository: expected owner/name, with the characters GitHub allows")` -> `raise GitHubError(f"refusing the repository: {self.repo}")` | RED | `sec_f4_every_malformed...` |
| `GH-7a` | `github.py` | `could not clone '{plain(name)}': {category}` -> `could not clone '{name}': {category}` | RED | `sec_f4_the_clone_message_shows_the_name_through_plain` |
| `GH-7b` | `github.py` | `could not clone '{plain(name)}': {_TIMED_OUT}` -> `could not clone '{name}': {_TIMED_OUT}` | RED | `sec_f4_the_timeout_clone_message...` |
| `GH-8a` | `github.py` | `                env={**os.environ, "GH_PROMPT_DISABLED": "1"},\n` -> `` (line removed) | RED | `sec_f5_gh_runs_with_its_prompts_disabled` |
| `GH-8b` | `github.py` | `"GH_PROMPT_DISABLED": "1"` -> `"GH_PROMPT_DISABLED": "0"` | RED | same |
| `DIFF-1` | `diff.py` | `                env=_git_env(),\n` -> `` (line removed) | RED | `sec_f5_git_show_in_diff_runs_in_the_no_prompt_english_environment` |
| `GH-9` (`O5`) | `github.py` | `    except GitHubTimeout:\n        return _TIMED_OUT\n` -> `    except GitHubError:\n        return _TIMED_OUT\n` | RED | `cr_f5_a_missing_git_on_a_cache_hit_raises_and_is_not_stale`: `DID NOT RAISE` |
| `GH-10` | `github.py` | same old -> `    except GitHubError as exc:\n        if not str(exc).endswith(_TIMED_OUT):\n            raise\n        return _TIMED_OUT\n` | RED | `cr_f5_the_timeout_is_a_typed_signal_not_a_message_suffix` |
| `GH-11` | `github.py` | `raise GitHubTimeout(f"git {args[0]} failed: {_TIMED_OUT}")` -> `raise GitHubError(f"git {args[0]} failed: {_TIMED_OUT}")` | RED | full run: the stale-connect arms (a `git fetch failed: timed out` surfaced as an error); alone with `-k typed_signal`: `cr_f5_the_timeout_is_a_typed_signal_not_a_message_suffix` (a `GitHubError` where `GitHubTimeout` is required) |
| `GH-12` | `github.py` | `        self.stale = ""\n        _refuse_unsafe(self.repo)\n` -> `        _refuse_unsafe(self.repo)\n` | RED | `cr_f7_a_connector_that_connects_twice...` |
| `GH-13` | `github.py` | `    url = url.strip()\n    _refuse_unsafe(url)` -> `    _refuse_unsafe(url)` | RED | `cr_f7_a_padded_url_is_cloned_and_keyed...` |
| `GH-14a` (`O4`) | `github.py` | `return url.strip().rstrip("/").removesuffix(".git")` -> `return url.strip().rstrip("/")` | RED | full run: `sec_f1_a_mirror_that_holds_another_remote...` first; with `-k four_spellings`: `sec_f1_the_same_remote_in_the_four_spellings...`, names `{'tools-2647a1d85eab', 'tools-c6a6531a9e9b'}` |
| `GH-14b` (`O4`) | `github.py` | same old -> `return url.strip().removesuffix(".git")` | RED | `sec_f1_the_same_remote_in_the_four_spellings...`: three names |

Not run: a mutant for the `GH_PROMPT_DISABLED` env being built without `os.environ` (the arm asserts `PATH` is
inherited; no mutant was run for it, so that half of the arm is not claimed). Not run: a mutant that removes
the stale line's `plain()` (the category is a fixed string; an equivalent mutant).

## 5. Test results

| check | state |
|---|---|
| `tests/test_inc9h.py`: 41 default + 2 `network` (real local bare repositories, HOME and USERPROFILE in `tmp_path`) | executed: all green on HEAD; 34 RED + 9 green on the base |
| Full default lane, final run on `150943b`, run once and uninterrupted, output to a file | executed: **1722 passed, 3 xfailed, 23 deselected, 0 failed**, 20:36 (baseline 1681: +41 arms in `test_inc9h.py`; the 2 `network` arms are deselected). A FIRST run on `e2d49a1` had **1 failed, 1721 passed**, 16:01: `test_fold` found the character U+202E written literally in my arms file (the six-character escape I typed was turned into the character on its way to the file; my slip, the same one as Inc-9g); fixed in `150943b`. Two later commits touch only `tests/test_inc9h.py` (`36e21a5` two unused imports, `927da29` env-arm messages): `test_inc9h.py` (43), `test_fold`, `test_no_operator_paths` re-run green after them (see the commit note); the whole lane was NOT re-run a third time |
| `ruff check .` vs `8e8f9f0` (a detached worktree of the base), set difference, line numbers stripped, `prototypes/` excluded | executed: new = none, gone = none (28 findings on each side). The first comparison found 2 new (`pathlib`, `Input` unused in my arms file); removed in `36e21a5` |
| Known flakes (`test_llr_cnv_3_1...`, `test_hlr_n16_4_legend_declares_its_own_keys[size2]`) | not hit in either lane run |
| `git stash` | not used. `git stash list` still holds the PREVIOUS implementer's `stash@{0}` (WIP 8d74b73): untouched, left for the operator |

## 6. Renders (text frames; the colours are asserted per composited cell and printed)

Palette, home scope, after `down down` then `o` (the filter edit; row 0 is the lit one), 118x34:

```
                    o
                    open    browse maps    c        <- lit: ('open    ', #000000 on #1783ff), ('browse maps    ', ...), ('c', ...)
                    open    connect repo   p
                    open    build map      n
                    open    from template  t
                    open    import csv     i
                    open    factory        f
                    open    components     s
                    maps    next map       j
                    maps    previous map   k
                    maps    open map       ↵
                    10/14 actions   ↵ run   esc close
```

Row 0, all three segments `#000000` on `#1783ff`: **5.73:1** (before: `#121212` on `#121212`, 1.12:1). Row 1 keeps
`#3a3a3a` / `#f5f5f5` / `#1783ff` on `#121212`. At 87x34 the same rows, the same measured colours (frame differs
only in the left margin: `    o`, `    open    browse maps    c`, ...).

Repo stage panel, stale (the refresh timed out), toasts cleared, 118x34 and 87x34 (identical in the panel):

```
 ● iniciando
 ● leyendo ramas
 ● calculando métricas
 ● listo
 ▲ cached copy: timed out

 ▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱ 0%
```

(The progress bar reads 0% because the stub mirror has no branches. The `▲` line wraps inside the 30-cell
sidebar for the longer categories; the arms read the wrapped text and the colour of every glyph from the `▲` row.)
**Observed, not in scope and not fixed:** the unselected row's group word is `#3a3a3a` on `#121212` (about 1.6:1,
computed, not asserted anywhere).

## 7. Risks, carries, next

- **Risks.** (1) `INC9G-SEC-F1` resolved as re-clone, with the duplicate-clone cost above: needs the operator's
  reading. (2) `HomeScreen.compose` default hint is the maps variant for the unpainted first moment. (3) The
  `unknown (exit N)` category carries the exit code to the panel line (a number, no git text).
- **Carries unchanged from `A-115`.** `LC_ALL=C` unmeasured on a localised git; the palette footer's arrows
  (`N2`, `Inc-EN`); Spanish strings on the repo screen (`Inc-EN`); orphaned mirrors under the pre-`A-115` name.
- **Not measured.** Behaviour against a real remote (no network was used); `git config --get` on a mirror
  cloned by a git older than this machine's; any terminal other than Textual's headless driver.
- **Next.** `Inc-EN` (not started).

## Commits

`f0c52b0` arms (strict xfail) and the `_Mirror` helper · `09a7499` palette · `6ddc723` github and diff ·
`e2d49a1` app (panel line, one toast, home hint) and the `test_inc9g` toast text · `150943b` the escape fix
(`test_fold`) · `36e21a5` unused imports (ruff) · `927da29` env-arm messages · docs commit (this record, `A-116`,
the `increment-033` correction). No push; `state.json` untouched.

## Correction (appended in Inc-9i, 2026-10-01; section 2 stands as written above)

Section 2, `INC9G-SEC-F1`, says the connect is refused "only if that directory is foreign too ... reachable only when
the key and the typed form coincide, i.e. a collision or a tampered cache". **That is false.** For a URL with no `.git`
the typed-form key (`url.rstrip("/")`) IS the primary key (`_normalise_url(url)`), so after `.../tools.git` was
connected, connecting `.../tools` from the SAME cache found the same foreign mirror in its "own" directory and was
refused, every time (`INC9H-CR-F1` = `INC9H-SEC-F1`; the arm
`test_inc9h_sec_f1_when_the_own_directory_is_foreign_too_the_connect_is_refused` pinned exactly that as intended). It
also locked out caches the base had already built with `tools.git`. Fixed in `Inc-9i` (`A-117`): the fallback key is
`"as-typed:" + url.rstrip("/")`, so the refusal is reachable only by a tamper or a hash collision of both directories.
