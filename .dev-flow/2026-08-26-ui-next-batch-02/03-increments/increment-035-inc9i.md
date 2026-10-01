# Increment 035 -- Inc-9i: the Inc-9h review defects

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `a0ff3b9`. Authority: the Inc-9h independent
reviews, the coordinator's rulings on `INC9H-UX-F1` / `INC9H-SEC-F2`, and the operator's Round 6 Q1
(`VERDICT-inc9-2026-09-30.md`). Amendment: `A-117` (appended to `01-requirements.md`, dated 2026-10-01). Findings are
named `INC9H-*`.

## 1. What changed (per finding)

| id | Change | Evidence state |
|---|---|---|
| `INC9H-CR-F1` = `INC9H-SEC-F1` (HIGH) | `github.py` `_ensure_cloned`: the fallback key is `"as-typed:" + url.rstrip("/")`, a key space disjoint from the primary `_normalise_url(url)`. Arms (a) `r.git` then `r`, (b) `r` then `r.git`, (c) a base-built cache (only `tools.git` in the primary dir) then `tools`, (d) the reworked "own directory foreign too" arm, plus (a) with real git | executed (stub; real local git under `network`) |
| `INC9H-CR-F2` | arm only: an origin that differs from the typed URL only by case is another remote | executed |
| `INC9H-CR-F3` | arm only: stale connect, `q`, fresh connect: no `▲ cached copy` line, only `conectado`. **Skipped (declared): the optional palette filter-edit serialisation arm.** Textual runs one handler per key and `pilot.press` pauses between keys, so two edits cannot be made to overlap before the first `await list_view.clear()` finishes without private timing hooks; the `cr_f1` arms of `Inc-9h` already kill the missing-`await` mutant | executed (arm); not-run (palette serialisation) |
| `INC9H-UX-F1` | `app.py` `_stages_text`: the stale line is `▲ cached copy:` newline category. Wrapping before the category, not a non-breaking space (a NBSP is a `\s` to Rich's wrapper: measured, section 6) | executed (Pilot, 87 and 118) |
| `INC9H-SEC-F2` | `github.py`: `_refuse_userinfo`, called in `GitHubConnector.fetch` for a typed URL before `_ensure_cloned`. Fixed sentence `refusing the URL: it carries a credential; use the git credential helper instead` | executed (stub; asserts no process, no directory, nothing echoed) |

## 2. Decisions and deviations (declared)

- **Source files: 2** (`mapper/github.py`, `mapper/app.py`), as expected. Tests and docs uncapped.
- **The false claim in `increment-034` section 2 is corrected by an appended note** at the end of that record (the
  section itself is left as written).
- **Declared sealed-arm change (item 1d).** `tests/test_inc9h.py::test_inc9h_sec_f1_when_the_own_directory_is_foreign_too_the_connect_is_refused`
  tampered only the primary directory of `https://example.invalid/alice/tools`, which for a URL with no `.git` was also
  the fallback directory; it asserted a refusal. That asserted the defect: one tampered directory locked the URL out
  for good. It now tampers the primary, lets the URL get its own directory (asserted `own != primary`), tampers that
  one too, and only then asserts the refusal, no clone, no fetch, nothing echoed. No assertion was weakened: the
  refusal arm gained a precondition and the refusal is still asserted with the same messages. The arm is RED on the
  base (the second connect refuses) and green on HEAD. Its `OPEN_STEPS` key (`inc9i`) was added in the RED commit and
  removed in the fix commit.
- **`INC9H-SEC-F2` is enforced in `GitHubConnector.fetch`, not in `_ensure_cloned`.** Two sealed arms
  (`test_inc9d::test_inc9d_sec_f3_a_failed_clone_message_carries_no_local_path`,
  `test_inc9f::test_inc9f_m2_git_text_is_never_in_the_message`) call `_ensure_cloned` directly with a
  `https://user:s3cr3t-token@...` URL and assert a CLONE-failure message that leaks nothing. Refusing inside
  `_ensure_cloned` would have broken both, and the brief says to stop in that case; the connector is where a TYPED
  URL enters (`RepoScreen` goes through it), so the ruling ("a typed URL, before any process") is met without
  touching them. Cost: `_ensure_cloned` called directly still takes userinfo. Only an `http(s)://` authority is read;
  `git@host:o/r` has no userinfo in this sense and an `@` in the path is not userinfo (pin arm, kills `M9`).
- **`INC9H-UX-F1`: wrap before the category, always.** Not width-aware: `_stages_text` does not know the sidebar's
  width at compose time, and a one-line `▲ cached copy: timed out` becomes two lines. The brief allowed either option;
  this one needs no width. `authentication required` (23 cells) already broke BEFORE the category on the base at 30
  cells (measured), so its arm is a pin; `unknown (exit 1)` is the RED arm (`unknown (exit` / `1)` on the base). The
  `host not found` case the coordinator named is covered by the same fix and by the `Inc-9h` panel arms
  (whitespace-normalised, they pass on both sides).
- **`CR-F3` mutant.** `GitHubConnector` is constructed per fetch and the screen is per push, so the reset at the top of
  `fetch()` (`GH-12` of `Inc-9h`) cannot be killed through the screen. The mutant that matches the arm's claim is
  app-wide stickiness (`M5`, section 4); I wrote it myself, the reviewer's text is not known to me.
- **Arm (b) and arm (c) have no mutant of their own that the other arms do not also hit.** (b) is killed by `M2`
  (the origin check removed: `r.git` reuses `r`'s mirror); (c) is killed by `M1`.
- File count: 2 source files, under the cap of 4.

## 3. Arm table (13 default + 1 `network` in `tests/test_inc9i.py`; 1 reworked arm in `tests/test_inc9h.py`)

RED: the two arms files copied into a detached `git worktree` of `a0ff3b9` in `%TEMP%` (no stash), run with
`--runxfail`: **9 failed, 48 passed** (`test_inc9i.py` and `test_inc9h.py`, `-m "not slow"` so the `network` arm is in).
GREEN: all of them on HEAD (`201 passed, 2 xfailed` after the github step, then `174 passed` for the four neighbouring
files after the panel step, `3 passed` for the `network` lane).

| arm | RED on `a0ff3b9` | state on HEAD |
|---|---|---|
| `cr_f1_r_dot_git_then_r_in_one_cache_gives_two_clones_and_no_refusal` (a, stub) | RED (`GitHubError`: refusing the cached copy) | green |
| `cr_f1_real_git_r_dot_git_then_r_shows_each_repos_own_branches` (a, real git, `network`) | RED (same) | green (`-m network`) |
| `cr_f1_r_then_r_dot_git_in_one_cache_still_gives_two_clones` (b) | green (pin) | green |
| `cr_f1_a_cache_the_base_built_with_only_the_dot_git_mirror_accepts_the_plain_url` (c) | RED (refused) | green |
| `test_inc9h::sec_f1_when_the_own_directory_is_foreign_too_the_connect_is_refused` (d, reworked) | RED (second connect refuses) | green |
| `cr_f2_an_origin_that_differs_only_by_case_is_not_this_url` | green (pin) | green |
| `cr_f3_a_fresh_connect_after_a_stale_one_paints_no_cached_copy_line` | green (pin) | green |
| `ux_f1_the_stale_category_is_never_split_across_lines[exit1, 87 and 118]` | RED x 2 | green x 2 |
| `ux_f1_..._[auth, 87 and 118]` | green x 2 (pin) | green x 2 |
| `sec_f2_userinfo_in_a_typed_url_is_refused_before_any_process` x 3 (`u:tok@`, `tok@` + `.git`, `u:@`) | RED x 3 | green x 3 |
| `sec_f2_a_url_without_userinfo_and_an_scp_style_address_still_connect` | green (pin) | green |

## 4. Mutant table

Harness `mutate9i.py` in the session scratchpad, outside the repo; run on a detached `git worktree` copy of `5badbb0`
(the code commit) in `%TEMP%`; sha256 of the target file pinned before, byte-level I/O in the file's own line ending
(CRLF for both `github.py` and `app.py`), the verdict printed before the file is restored, the pin re-checked after:
**pin OK 11 of 11**, plus one extra `-k base_built` run done by hand (restored in a `finally`, not pin-checked). `old`
occurs exactly once in each. `\n` below marks a line break (the file's own ending was used).

| id | claims | file | old -> new (exact) | verdict | first arm to fail |
|---|---|---|---|---|---|
| `M1` | (a), (c) | `github.py` | `"as-typed:" + url.rstrip("/")` -> `url.rstrip("/")` (the base defect) | RED | `cr_f1_r_dot_git_then_r_...` (with `-k base_built` alone: `cr_f1_a_cache_the_base_built...`) |
| `M1d` | (d) | `github.py` | same as `M1` | RED | `test_inc9h::sec_f1_when_the_own_directory_is_foreign_too...` |
| `M1n` | (a) real git | `github.py` | same as `M1` (`-m network`) | RED | `cr_f1_real_git_r_dot_git_then_r_shows_each_repos_own_branches` |
| `M2` | (b) | `github.py` | `    if (target / "HEAD").is_file() and not _is_mirror_of(target, url):\n        # \`INC9G-SEC-F1\`` -> `    if False:\n        # \`INC9G-SEC-F1\`` | RED | `cr_f1_r_then_r_dot_git_in_one_cache_still_gives_two_clones` |
| `M3` | (d) | `github.py` | `            raise GitHubError("refusing the cached copy: it belongs to another repository")\n` -> `            pass\n` | RED | `test_inc9h::sec_f1_when_the_own_directory_is_foreign_too...` |
| `M4` | `CR-F2` | `github.py` | `result.stdout.strip().rstrip("/") == url.rstrip("/")` -> `result.stdout.strip().rstrip("/").lower() == url.rstrip("/").lower()` | RED | `cr_f2_an_origin_that_differs_only_by_case_is_not_this_url` |
| `M5` | `CR-F3` | `app.py` | `        self.stale = connector.stale\n        return graph\n` -> `        self.app.__dict__["_s"] = self.app.__dict__.get("_s") or connector.stale\n        self.stale = self.app.__dict__["_s"]\n        return graph\n` | RED | `cr_f3_a_fresh_connect_after_a_stale_one_paints_no_cached_copy_line` |
| `M6` | `UX-F1` | `app.py` | `f"▲ cached copy:\n{self.stale}"` (a backslash-n inside the f-string, not a line break) -> `f"▲ cached copy: {self.stale}"` | RED | `ux_f1_..._[exit1-unknown (exit 1)-size0]` |
| `M7` | `SEC-F2` | `github.py` | `            _refuse_userinfo(self.repo)\n` -> `` (line removed) | RED | `sec_f2_userinfo_..._[https://u:tok3n-x@...]` |
| `M8` | `SEC-F2` (a token with no password) | `github.py` | `"@" in urlparse(url).netloc` -> `urlparse(url).password is not None` | RED | `sec_f2_userinfo_..._[https://tok3n-x@example.invalid/o/r.git]` |
| `M9` | `SEC-F2` pin (no false refusal) | `github.py` | `"@" in urlparse(url).netloc` -> `"@" in url` | RED | `sec_f2_a_url_without_userinfo_and_an_scp_style_address_still_connect` |

11 harness runs (9 distinct mutations: `M1`, `M1d`, `M1n` are one mutation against three arm sets), 11 RED, 0 survived, 0 skipped.
Not run: a mutant for the `authentication required` pin arm (a pin: green on the base).

## 5. Test results

| check | state |
|---|---|
| `tests/test_inc9i.py` 13 default + 1 `network` (real local bare repositories, HOME and USERPROFILE in `tmp_path`) and `tests/test_inc9h.py` | executed: green on HEAD; RED/GREEN table above |
| Full default lane, once, uninterrupted, last step, output to a file | executed: **1735 passed, 3 xfailed, 24 deselected, 0 failed**, 19:09 (baseline 1722: +13 default arms; the `network` arm is deselected). Run on `7f482d5` after the docs commit, because `test_no_operator_paths` reads `.dev-flow`; this result line is the only edit after it |
| `ruff check . --exclude prototypes` set difference vs `a0ff3b9` (a detached worktree, line and column stripped) | executed: new = none, gone = none (28 findings on each side) |
| Literal Cf/Cc characters in `tests/test_inc9i.py` and `tests/test_inc9h.py` (scan before every commit) | executed: none |
| Known flakes (`test_llr_cnv_3_1...`, `test_hlr_n16_4_legend_declares_its_own_keys[size2]`) | not hit |
| `git stash` | not used |
| Real remote, real `gh`, real cache | not-run (every arm is stubbed or uses local bare repositories under `tmp_path`) |

## 6. Renders (text frames; Pilot, stub mirror)

Stale connect, `authentication required`, 87x34 (the left 40 columns; the `▲` line and its category are two rows):

```
 ● iniciando
 ● leyendo ramas
 ● calculando métricas
 ● listo
 ▲ cached copy:
 authentication required

 ▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱ 0%
```

Same at 87x34 for `unknown (exit 1)` (`▲ cached copy:` / `unknown (exit 1)`) and at 118x34 for `host not found`. Before
(`Inc-9h`, 30-cell sidebar): `▲ cached copy: unknown (exit` / `1)`. NBSP measured on `rich.text.Text.wrap` at 30 cells:
`'aaaaaaaaaaaaaaa unknown<NBSP>(exit<NBSP>1)'` wraps as `...unknown<NBSP>(exit<NBSP>` / `1)`: the wrapper treats NBSP
as a space. Not measured in a Textual render with NBSP; only the chosen fix was rendered.

## 7. Risks, carries, next

- **Risks.** (1) `_ensure_cloned` called directly still takes userinfo (section 2). (2) The panel line is now always
  two lines, so a stale connect takes one more row of the sidebar. (3) A fixed-sentence credential refusal says
  nothing about WHICH part of the URL; by design.
- **Not measured.** Behaviour against a real remote; a case-insensitive filesystem making `.../R` and `.../r`
  collide on the directory name (the key hashes the URL, the directory prefix is the last segment as typed); any
  terminal other than Textual's headless driver.
- **Carries unchanged.** `Inc-EN` (not started); `LC_ALL=C` unmeasured on a localised git; orphaned pre-`A-115` mirrors.
- **Next.** `Inc-EN`, on the operator's order.

## Commits

`ce656dd` arms (strict xfail; the `test_inc9h` arm reworked) · `cb6bced` `github.py` (key, userinfo) and the `OPEN_STEPS`
removal for those arms · `5badbb0` `app.py` (panel line), the last `OPEN_STEPS` removal and `red_marks` · docs commit
(this record, `A-117`, the `increment-034` correction). No push; `state.json` untouched.
