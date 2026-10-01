# Increment 036 -- Inc-9j: the Inc-9i review defects

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `e3a9c95`. Authority: the Inc-9i code, UX and
security reviews, and the operator's Round 7, R1 (`VERDICT-inc9-2026-09-30.md`). Amendment: `A-118` (appended to
`01-requirements.md`, dated 2026-10-01). Findings are named `INC9I-*`.

## 1. What changed (per finding)

| id | Change | Evidence state |
|---|---|---|
| `INC9I-SEC-F1` (MEDIUM) | `github.py`: `_http_parts` reads an http(s) URL the way curl does (skip every `/` and `\` after `://`, authority up to the first `/?#`); `_refuse_userinfo` refuses when that authority holds `@` or `urlparse(url).netloc` is empty. Same fixed sentence, nothing echoed. `https://tok?@h/o/r` is NOT refused (authority `tok`; measured by an arm) | executed (stub that fails on any process) |
| `INC9I-UX-F1` (operator R1) | `github.py` `redact_userinfo` (one helper, `scheme://***@host/...`, three-slash form included); `app.py` `RepoScreen.shown` feeds the crumb and `#repo-name`. `RepoScreen.repo` stays as typed. The connect-repo field keeps the typed text after `q` | executed (Pilot at 118 and 87, composited frame) |
| `INC9I-CR-F1` | `test_inc9i` stale-line arm parametrised over `CATEGORIES` + `unknown (exit 1)` + `unknown (exit 128)` (14 cases), with `_CategoryMirror` mapping each category to a matching stderr (or a timeout, or junk stderr with that exit code). It also asserts the label row does not carry the category | executed |
| `INC9I-CR-F2` | `test_inc9i` arm (a): after the round trip, `R + "/"` finds `plain` and no third clone | executed |
| `INC9I-CR-F3` | `_ensure_cloned` docstring line; pin test (AST walk of `mapper/`) that `_ensure_cloned` is referenced only by its definition and `GitHubConnector.fetch` | executed |
| `INC9I-CR-F4` | documentation only, section 7 | n/a -- docs |

## 2. Decisions and deviations (declared)

- **Source files: 2** (`mapper/github.py`, `mapper/app.py`), as expected. Tests and docs uncapped.
- **Item 4 placement.** The brief said to add `assert _ensure_cloned(R + "/", cache) == plain and len(_clones(run)) == 2`
  to arm (a). In arm (a) `run.calls` is cleared before the round trip, so the count there is 0, not 2; I wrote
  `... == plain and _clones(run) == []` (no third clone). The first version of the assertion sat in arm (b)
  (`r` then `r.git`), where `R/` finds `R`'s PRIMARY mirror and never reaches the as-typed key, so the mutant could not
  die there; it was moved to (a) in commit `178c582`. The mutant `Mj` kills it in (a).
- **`HTTPS:///u:tok@h/o/r` (upper-case scheme) is a pin, not a RED arm.** `_is_url` is case-sensitive, so the connector
  sends it to the `gh` path, which already refuses it (`refusing the repository: expected owner/name, ...`, nothing
  echoed, no process). The refusal sentence differs from the credential one. Not changed: out of scope.
- **The `lstrip` is redundant for the refusal, needed for the redaction.** Every listed bypass has an empty `urlparse`
  netloc, so the second clause alone refuses them; `Ma` (the `lstrip` removed) is killed by the redaction helper arms,
  not by a refusal arm. The `@`-in-authority clause is killed by the sealed `Inc-9i` arms (`Mc`).
- **A host-less URL (`https:///h/o/r`) now gets the credential sentence.** It carries no credential; the brief's rule
  (refuse on an empty netloc, same sentence) was followed. The sentence is therefore a little inexact for that input.
- **No toast or failure line names the URL.** Checked by reading every `GitHubError` in `github.py` and every `notify`
  in `RepoScreen`: the messages name a fixed sentence or `plain(name)` (the last path segment). The arm asserts the
  captured toasts hold neither `tok` nor `user:`.
- **Arms commit fix.** The first arms commit (`a86c90b`) had a wrong attribute (`Static.renderable`) in the screen arm,
  AFTER the assertions that carry the RED on the base; fixed in `5887154` and the RED table below was re-measured with
  the corrected file. `OPEN_STEPS` held `creds` and `redact` in `a86c90b`; one code commit (`5887154`) closes both
  because the helper arms and the screen arms share `redact_userinfo`.
- **Test file line endings.** `tests/test_inc9i.py` is LF in the index; an earlier write by a script converted it to CRLF
  and it was normalised back to LF before the commit (`git diff` shows only the intended hunks).

## 3. Arm table (`tests/test_inc9j.py`: 33 default; `tests/test_inc9i.py`: 2 reworked arms)

RED: the two arms files copied into a detached `git worktree` of `e3a9c95` in `%TEMP%` (no stash), run with
`--runxfail`, corrected arms file: **26 failed, 31 passed** (`test_inc9j.py` + `test_inc9i.py`, `-m "not slow"`).
GREEN: `246 passed` for `test_inc9j`, `test_inc9i`, `test_inc9h`, `test_inc9d`, `test_inc9f`, `test_inc9g` with `--runxfail`
on `5887154`.

| arm | RED on `e3a9c95` | on HEAD |
|---|---|---|
| `sec_f1_extra_slashes_do_not_hide_userinfo_from_the_refusal` x 4 (`https:///tok@h/o/r`, `http:///u:tok@h/o/r`, `https:////u:p@h/o/r`, `https:///\u:p@h/o/r`) | RED x 4 (`git clone --mirror` started) | green x 4 |
| `sec_f1_a_url_with_no_host_at_all_is_refused_before_any_process` (`https:///h/o/r`) | RED | green |
| `sec_f1_an_upper_case_scheme_is_not_a_url_here_and_starts_no_process` | green (pin) | green |
| `sec_f1_no_false_refusal` x 5 (`git@host:o/r.git`, `.../r@v2`, `.../r.git`, `.../r/`, `https://tok?@h/o/r`) | green (pin) | green |
| `ux_f1_the_helper_keeps_scheme_and_host_and_replaces_userinfo` x 10 | RED x 10 (`AttributeError: redact_userinfo`) | green |
| `ux_f1_the_helper_leaves_a_url_without_userinfo_alone` x 7 | RED x 7 (same) | green |
| `ux_f1_a_typed_credential_is_painted_nowhere_but_in_the_field` x 4 (`user:tok@` and `///user:tok@`, 118 and 87) | RED x 4 (`tok` painted in the crumb and `#repo-name`) | green |
| `cr_f3_ensure_cloned_is_referenced_in_production_only_from_the_connector_fetch` | green (pin) | green |
| `test_inc9i::ux_f1_the_stale_category_is_never_split_across_lines` x 14 (7 categories x 87 and 118) | green (pin; strengthened) | green |
| `test_inc9i::cr_f1_r_dot_git_then_r_...` (with the `R/` assertion) | green (pin; strengthened) | green |

## 4. Mutant table

Harness `mutate9j.py` in the session scratchpad, outside the repo; run on a detached `git worktree` copy of `178c582`
in `%TEMP%`; sha256 of the target file pinned before, byte-level I/O (both sources are CRLF, the old/new text was
converted), the verdict printed before the file is restored, the pin re-checked after: **pin OK 12 of 12**, worktree clean
afterwards. `old` occurs exactly once in each. `\n` in `Mi` is a backslash and an n inside the f-string; a line break
elsewhere is written `<LF>`.

| id | claims | file | old -> new (exact) | verdict | first arm to fail |
|---|---|---|---|---|---|
| `Ma` | `lstrip` of the slashes (redaction) | `github.py` | `    after = after.lstrip("/\\")<LF>` -> `    after = after<LF>` | RED | `ux_f1_the_helper_keeps_scheme_and_host_..._[https:///u:tok@h/o/r-...]` |
| `Mb` | empty-netloc clause | `github.py` | ` or not urlparse(url.strip()).netloc)` -> `)` | RED | `sec_f1_a_url_with_no_host_at_all_is_refused_before_any_process` |
| `Mc` | `@`-in-authority clause | `github.py` | `("@" in parts[1] or not urlparse` -> `(not urlparse` | RED | `test_inc9i::sec_f2_userinfo_in_a_typed_url_is_refused_before_any_process[https://u:tok3n-x@...]` |
| `Md` | authority ends at `?` (no false refusal of `tok?@h`) | `github.py` | `re.split(r"[/?#]", after, maxsplit=1)` -> `re.split(r"[/]", after, maxsplit=1)` | RED | `sec_f1_no_false_refusal[https://tok?@example.invalid/o/r]` |
| `Me` | last `@` splits userinfo from host | `github.py` | `authority.rpartition('@')[2]` -> `authority.partition('@')[2]` | RED | `ux_f1_the_helper_keeps_scheme_and_host_..._[https://a@b@h/o/r-...]` |
| `Mf` | crumb redacted | `app.py` | `crumb=[self.shown])<LF>        with Horizontal(id="repo-dashboard")` -> `crumb=[self.repo])<LF>        with Horizontal(id="repo-dashboard")` | RED | `ux_f1_a_typed_credential_is_painted_nowhere_but_in_the_field[...-size0]` |
| `Mg` | `#repo-name` redacted | `app.py` | `Static(Text(darkside.plain(self.shown)), id="repo-name")` -> `Static(Text(darkside.plain(self.repo)), id="repo-name")` | RED | same |
| `Mh` | the field keeps the typed text | `app.py` | `                self.app.push_screen(RepoScreen(repo))<LF>` -> `                event.input.value = ""<LF>                self.app.push_screen(RepoScreen(repo))<LF>` | RED | same |
| `Mi` | `CR-F1`: own line for every category | `app.py` | `f"▲ cached copy:\n{self.stale}"` -> `(f"▲ cached copy:\n{self.stale}" if self.stale.startswith("unknown") else f"▲ cached copy: {self.stale}")` | RED | `test_inc9i::ux_f1_the_stale_category_is_never_split_across_lines[host not found-size0]` |
| `Mj` | `CR-F2`: fallback key rstrips `/` | `github.py` | `"as-typed:" + url.rstrip("/")` -> `"as-typed:" + url` | RED | `test_inc9i::cr_f1_r_dot_git_then_r_in_one_cache_gives_two_clones_and_no_refusal` |
| `Mk` | the refusal is called before `_ensure_cloned` | `github.py` | `            _refuse_userinfo(self.repo)<LF>            cwd = _ensure_cloned(self.repo, ...)<LF>` -> the `_ensure_cloned` line alone | RED | `sec_f1_extra_slashes_..._[https:///tok@h/o/r]` |
| `Ml` | `CR-F3`: no other production caller | `github.py` | `    def _mark_stale(self, category: str) -> None:<LF>        self.stale = category<LF>` -> same with `        _ensure_cloned("x", self.cache_dir)<LF>` added before `self.stale = category` | RED | `cr_f3_ensure_cloned_is_referenced_in_production_only_from_the_connector_fetch` |

12 harness runs, 12 RED, 0 survived, 0 skipped. (`Mi` runs `test_inc9i.py` only; `Ma` runs both files.) Not run: a mutant of
the `HTTPS://` pin and of the `git@...` no-false-refusal pins (pins green on the base).

## 5. Test results

| check | state |
|---|---|
| `tests/test_inc9j.py` + `tests/test_inc9i.py`, then with `test_inc9h/d/f/g` | executed: 56 passed (1 `network` deselected); 246 passed with `--runxfail` |
| Full default lane, once, uninterrupted, last step, output to a file | FULL_LANE_RESULT |
| `ruff check . --exclude prototypes --output-format concise` set difference vs `e3a9c95` (a detached worktree, line and column stripped) | executed: new = none, gone = none (26 lines each side by this counting) |
| Literal Cf/Cc characters in `tests/test_inc9j.py` and `tests/test_inc9i.py` (scan before every commit) | executed: none |
| Known flakes (`test_llr_cnv_3_1...`, `test_hlr_n16_4_legend_declares_its_own_keys[size2]`) | FLAKES |
| `git stash` | not used |
| Real remote, real `gh`, real cache, real credentials, network, loopback servers | not-run (every arm is a stub; HOME and USERPROFILE in `tmp_path`) |
| A real `git clone` of `https:///u:tok@host/...` against the fix | not-run (the security reviewer measured the bypass; here the refusal is asserted by a stub that fails on any process) |

## 6. Renders (text frames; Pilot, stub that fails on any process; typed `https://user:tok@example.invalid/o/r.git`, then `↵`)

Blank lines condensed. `RepoScreen`, 118x34 and 87x34 (identical in the lines that matter):

```
 browse maps    connect repo    build map    factory                                                          ◕ mapper
https://***@example.invalid/o/r.git
                               (no hay ramas cargadas)
 https://***@example.invalid/
 o/r.git

 ▲ failed
 refusing the URL: it carries
 a credential; use the git
 credential helper instead
 q back

 j next branch
 k previous branch
 q back
 ? legend
```

After `q` (the connect-repo screen; the field keeps the typed text, which is the only place `tok` and `user:` are painted):

```
connect repo
  connect repo
   https://user:tok@example.invalid/o/r.git
next ▸ ingresa owner/name, URL o ruta local y presiona ↵ ↵
```

Not measured: any terminal other than Textual's headless driver; the crumb at widths below 87.

## 7. Risks, carries, next

- **Risks.** (1) A host-less http(s) URL is refused with the credential sentence (section 2). (2) `_ensure_cloned` called
  directly still takes userinfo; `CR-F3` pins who calls it. (3) Only userinfo is redacted: a secret in the path or query
  (`?token=...`) is painted as typed. (4) The field is cleared by nothing, so the credential stays in memory and on screen
  in the field until the operator edits it (operator's R1 ruling).
- **Not measured.** Behaviour against a real remote or a real curl on the three-slash forms in this increment; `\t`/`\n`
  inside a URL (`urlparse` drops them, curl may not).
- **Carries.** `Inc-EN` (not started); `LC_ALL=C` unmeasured on a localised git; orphaned pre-`A-115` mirrors **and the
  base-era fallback directories (`INC9I-CR-F4`): a fallback directory written under the old key (`url` without the
  `as-typed:` prefix, for a URL with no `.git`) is orphaned the same way; nothing reads or deletes it**.
- **Next.** `Inc-EN`, on the operator's order.

## Commits

`a86c90b` arms (strict xfail) · `5887154` `github.py` + `app.py` + `OPEN_STEPS` emptied + the arm fix · `178c582` the
`R/` assertion moved to arm (a) · docs commit (this record, `A-118`) · docs commit (the full-lane result). No push;
`state.json` untouched.
