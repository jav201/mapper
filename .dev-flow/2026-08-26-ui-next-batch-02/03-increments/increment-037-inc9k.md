# Increment 037 -- Inc-9k: the closed allow-list for typed repo URLs

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `a906c80`. Authority: the operator's Round 8, S1
(`VERDICT-inc9-2026-09-30.md`, answer "Lista cerrada"). Amendment: `A-119` (appended to `01-requirements.md`, dated
2026-10-01; `A-117` st. 5 and `A-118` st. 1-2 are marked superseded, not deleted).

## 1. What changed

- `mapper/github.py`: ONE allow-list, `_is_url` (grammar below). It replaces the deny-list (`_URL_RE`, `_http_parts`,
  `redact_userinfo`, `_refuse_userinfo` are gone). `GitHubConnector.fetch` order: `_refuse_unsafe` -> local git directory
  -> `_is_url` (clone) -> `_is_owner_name` (gh) -> the one refusal sentence. `_ensure_cloned` applies `_is_url` right after
  `_refuse_unsafe` (defence in depth, `INC9J-SEC-F2`) and no longer strips. New `painted_repo(text)` = the text only for an
  accepted URL, a valid owner/name or a local git directory, else `(unrecognised URL)`.
- `mapper/app.py`: `RepoScreen.shown = painted_repo(repo)` feeds the crumb and `#repo-name`. `repo` stays as typed; the
  connect-repo field keeps the typed text (unchanged code).
- Tests: new `tests/test_inc9k.py`; reworked arms in `test_inc9d/f/g/h/i/j` (section 2).

### The allow-list grammar, exactly as implemented

```
_HOST = [A-Za-z0-9][A-Za-z0-9.-]*
_SEG  = [A-Za-z0-9._~-]+
https : https://HOST(:[0-9]+)?(/SEG)+/?            (re.fullmatch; scheme case-sensitive)
scp   : git@HOST:SEG(/SEG)*/?                      (re.fullmatch; no port)
then  : every segment of the path is not "." or ".." and does not start with "-"
```

No IPv6, no userinfo, no `?` `#` `%` `@`, whitespace (leading and trailing included), backslash, empty segment, non-ASCII.
`http://` is refused. Refusal sentence (one, nothing echoed): `refusing the repository: not a supported URL, owner/name, or
local folder`.

## 2. Decisions and declared sealed-arm changes

Source files: 2 (`github.py`, `app.py`), as expected. Tests and docs uncapped.

Decisions:
- **`http://` refused** (default taken). **`https://h/o/r@v2` refused** (the `@` in the path), declared in `A-119` st. 3.
- **Host is stricter than the brief by one character class:** it must START with a letter or digit (the brief: not start
  with `-`). A leading `.` is refused too. `h..x` and a trailing `.` are not policed (DNS fails them later).
- **One sentence also for a malformed owner/name, a non-git directory and `HTTPS://...`.** They used to get the `gh` path's
  own sentence; no sealed arm required it. The `-` and transport-helper sentences stay (`test_inc9g` matches
  "transport helpers"), and run first.
- **`_fetch_gh` keeps its own owner/name check** (same predicate, same sentence). Alone it is redundant with the check in
  `fetch`; mutant M16 survives for that reason (section 4).
- **The AST pin from Inc-9j is kept** (still true, and it keeps `fetch` the one typed-URL entry point).
- **`o/..` is not an arm.** On Windows `Path("o/..")` is the working directory (a git checkout), i.e. a real local
  directory, so the arm was environment-dependent; it was dropped, not worked around.
- **The Inc-9j security and code review tables were not on disk** (the batch folder holds `increment-035/036` only). The
  "every form in the review tables" arms are the forms of the Inc-9j arms (`BYPASSES`, `REDACTED`) plus the operator's list.

Sealed-arm changes (each: what, why; no leak assertion weakened):

| arm | change | justification (S1) |
|---|---|---|
| `test_inc9i::sec_f2_userinfo_..._refused_before_any_process` x3 | `"credential helper" in message` -> `message == <the one sentence>`; the leak list (`tok3n`, `u:`, `example`, `@`, `o/r`) is kept | the credential sentence is superseded (A-119 st. 4) |
| `test_inc9i::sec_f2_a_url_without_userinfo_and_an_scp_style_...still_connect` | `.../r@v2` removed from the connecting list | `@` in a path is refused now (A-119 st. 3); covered by `test_inc9k` |
| `test_inc9d::sec_f3_a_failed_clone_message_carries_no_local_path` | typed URL has no userinfo; the token moves into the stub's stderr (`_TokenStderrRun`); every assertion kept (token, host, cache path, profile) | the token URL can no longer reach a clone; the arm's intent (git text never in the message) is kept |
| `test_inc9d::sec_f3_s1_a_token_url_is_refused_with_nothing_leaked` (new) | the original token URL, direct call: refused, no process, no directory, nothing leaked | the refusal the brief asked for |
| `test_inc9f::m2_git_text_is_never_in_the_message` | typed URL has no userinfo; its stderr (token URL, profile path) and all leak assertions are kept | same |
| `test_inc9h::sec_f4_..._shows_the_name_through_plain` x2 | the hostile name (bidi override, ESC) is refused before any process; message == the sentence, no control character | a name with those characters cannot reach a clone any more; the property is stronger |
| `test_inc9h::cr_f7_a_padded_url_is_cloned_and_keyed_as_its_stripped_form` | padded URL is refused (no clone, no directory); the stripped form clones once and hits its mirror | whitespace is outside the grammar; `_ensure_cloned` no longer strips |
| `test_inc9h::sec_f1/sec_f2`, `test_inc9i::cr_f1`, `test_inc9g::sec_f1` (the 4 `network` real-git arms) | `monkeypatch.setattr("mapper.github._is_url", lambda _v: True)` | they clone real local bare repos through `file://` URLs, outside the allow-list by design; the allow-list is the unit under test in `test_inc9k` |
| `test_inc9g::sec_f2_typed_repo_text_is_shown_literally` x6 | `HOSTILE` markup texts become LOCAL DIRECTORY names (`[b]a`, `[@click=app.quit]q`, `[link=x]a`, a `.git` inside, relative via `chdir`) | a markup-carrying URL is not painted any more; a local directory is painted as typed, so the literal-text property is still exercised |
| `test_inc9j::sec_f1_extra_slashes` x4, `no_host_at_all` | sentence assertion -> the one sentence | superseded sentence |
| `test_inc9j::sec_f1_no_false_refusal` | `.../r@v2` and `https://tok?@h/o/r` removed from the list | `@` outside the grammar |
| `test_inc9j::ux_f1_the_helper_*` x17 (+ `REDACTED`, `UNTOUCHED`) | deleted | they test `redact_userinfo`, which is removed; `test_inc9k` has the `painted_repo` arms |
| `test_inc9j::ux_f1_a_typed_credential_is_painted_nowhere_but_in_the_field` x4 | `***@` painted -> `(unrecognised URL)` painted, no `***`; `tok`/`user:` absence and the field-keeps-text assertions kept | S1 display rule |

Not stopped: every userinfo arm could keep its intent (the two direct-call arms by moving the token into git's stderr, plus a
new refusal arm).

## 3. Arm table

RED: `tests/test_inc9k.py` committed as strict xfail (`3f4bcac`), copied into a detached `git worktree` of `a906c80` in
`%TEMP%` (no stash), `--runxfail`: **237 failed, 43 passed** (280 cases). The 43 passes are pins (green on the base).
GREEN: `test_inc9k` 280 passed on `71d2de2` with `OPEN_STEPS` empty.

| arm family (`test_inc9k`) | cases | RED on `a906c80` | on HEAD |
|---|---|---|---|
| a form outside the allow-list is refused before any process (operator list + Inc-9j forms + grammar cuts) | 73 | RED x73 | green |
| `_ensure_cloned` refuses the same forms by itself | 6 | RED x6 | green |
| a malformed owner/name gets the one sentence | 6 | RED x6 | green |
| the predicate refuses a URL-shaped text outside the grammar | 56 | RED x56 | green |
| `painted_repo`: a refused text is never painted / accepted as typed / local dir | 73 / 11 / 1 | RED x85 | green |
| the deny-list pieces are gone | 3 | RED x3 | green |
| Pilot: a refused credential is painted nowhere but in the field (4 forms x 118, 87) | 8 | RED x8 | green |
| accepted URLs reach `git clone --mirror -- URL` as typed | 9 | green (pin) | green |
| predicate accepts the grammar's forms / still refuses non-URL-shaped texts | 9 / 15 | green (pin) | green |
| dash and transport-helper refusals stand | 4 | green (pin) | green |
| owner/name through gh; a local git directory connects | 2 | green (pin) | green |
| Pilot: an allowed URL is painted as typed (118, 87) | 2 | green (pin) | green |

Reworked arms on `a906c80` (the reworked files copied into the same worktree): **16 cases RED** (`test_inc9i` sec_f2 x3,
`test_inc9h` sec_f4 x2 and cr_f7, `test_inc9d` token arm, `test_inc9j` extra_slashes x4, no_host, painted x4); the rest are pins.

## 4. Mutant table

Harness `mutate9k.py` in the session scratchpad, outside the repo; run on a detached `git worktree` of `71d2de2` in `%TEMP%`;
sha256 pinned before (`github.py` `c97183e11be98f49...`, `app.py` `9878dee90dd2d442...`, files are CRLF there), byte-level I/O in
the file's own line endings, the verdict printed before the file is restored, the pin re-checked after: **pin OK 26 of 26**.
`old` occurs exactly once. `<LF>` is a line break. Runs `test_inc9k.py` (the 4 Pilot-arm mutants run its Pilot arms only; M21 adds
`test_inc9g.py`), `-x`.

| id | claims | file | old -> new (exact) | verdict | first arm to fail |
|---|---|---|---|---|---|
| M1 | host does not start with `-` or `.` | github | `_HOST = r"[A-Za-z0-9][A-Za-z0-9.-]*"` -> `_HOST = r"[A-Za-z0-9.-][A-Za-z0-9.-]*"` | RED | refused `[https://-h/r]` |
| M2 | port needs a digit | github | `(?::[0-9]+)?` -> `(?::[0-9]*)?` | RED | refused `[https://h:/o/r]` |
| M3 | port digits are ASCII | github | `(?::[0-9]+)?` -> `(?::\d+)?` | RED | refused `[https://h:\u0663/o/r]` |
| M4 | segment charset holds `~` | github | `_SEG = r"[A-Za-z0-9._~-]+"` -> `_SEG = r"[A-Za-z0-9._-]+"` | RED | accepted `[.../some-name_v2~x.git]` |
| M5 | trailing `/` accepted (https) | github | `(?P<path>(?:/{_SEG})+/?)` -> `(?P<path>(?:/{_SEG})+)` | RED | accepted `[https://h/o/r/]` |
| M6 | `http://` refused | github | `rf"https://{_HOST}` -> `rf"https?://{_HOST}` | RED | refused `[http://h/o/r]` |
| M7 | `.`/`..` segments refused | github | `seg not in (".", "..") and not` -> `True and not` | RED | refused `[https://h/o/./r]` |
| M8 | a segment starting `-` refused | github | ` and not seg.startswith("-")` -> (empty) | RED | refused `[https://h/-r]` |
| M9 | the scp path does not start with `/` | github | `(?P<path>{_SEG}(?:/{_SEG})*/?)` -> `(?P<path>/?{_SEG}(?:/{_SEG})*/?)` | RED | refused `[git@h:/o/r]` |
| M10 | the whole text must match | github | `.fullmatch(value) or _SCP_URL.fullmatch(value)` -> `.match(value) or _SCP_URL.match(value)` (both) | RED | refused `[https://h/r?access_token=x]` |
| M11 | the scheme is case-sensitive | github | `(?P<path>(?:/{_SEG})+/?)")` -> `(?P<path>(?:/{_SEG})+/?)", re.I)` | RED | refused `[HTTPS://h/o/r]` |
| M12 | no userinfo (host has no `@`) | github | `_HOST = r"[A-Za-z0-9][A-Za-z0-9.-]*"` -> `_HOST = r"[A-Za-z0-9][A-Za-z0-9.@-]*"` | RED | refused `[https://tok@h/o/r]` |
| M13 | no `%` in a segment | github | `_SEG = r"[A-Za-z0-9._~-]+"` -> `_SEG = r"[A-Za-z0-9._~%-]+"` | RED | refused `[https://h/%2e%2e/r]` |
| M14 | `_ensure_cloned` applies the allow-list | github | `    if not _is_url(url):<LF>        raise GitHubError(_UNSUPPORTED)<LF>    name = ` -> `    name = ` | RED | `ensure_cloned_refuses_the_same_forms_by_itself[https://u:tok@h/o/r]` |
| M15 | `fetch` refuses a non owner/name (double mutant: also the check inside `_fetch_gh`) | github | `        if not _is_owner_name(self.repo):<LF>            raise GitHubError(_UNSUPPORTED)<LF>        return self._fetch_gh` -> `        return self._fetch_gh`, and in `_fetch_gh` `        if not _is_owner_name(self.repo):<LF>            raise GitHubError(_UNSUPPORTED)<LF>        owner, name` -> `        owner, name` | RED | refused `[https://u:tok@h/o/r]` (it reaches `gh`) |
| M16 | the `_fetch_gh` check ALONE | github | the second replacement of M15 only | **SURVIVED** | none: equivalent, `fetch` refuses first; kept as a redundant guard (section 2) |
| M17 | owner/name has exactly two parts | github | `return (len(parts) == 2 and` -> `return (len(parts) >= 2 and` | RED | refused `[a/b/c]` |
| M18 | `painted_repo` gates on the predicates | github | `    if _is_url(spec) or _is_owner_name(spec) or _is_local_path(spec):` -> `    if True or _is_owner_name(spec) or _is_local_path(spec):` | RED | `display_a_refused_text_is_never_painted[https://u:tok@h/o/r]` |
| M19 | an accepted URL is painted as typed | github | `    if _is_url(spec) or _is_owner_name` -> `    if _is_owner_name` | RED | `display_an_accepted_text_...[https://h/o/r]` |
| M20 | owner/name is painted as typed | github | `_is_url(spec) or _is_owner_name(spec) or _is_local_path(spec)` -> `_is_url(spec) or _is_local_path(spec)` | RED | `display_an_accepted_text_...[o/r]` |
| M21 | a local directory is painted as typed | github | same -> `_is_url(spec) or _is_owner_name(spec)` | RED | `display_a_local_directory_is_painted_as_typed` |
| M22 | the screen feeds `painted_repo` | app | `self.shown = painted_repo(repo)` -> `self.shown = repo` | RED | `a_refused_credential_is_painted_nowhere...[...-size0]` |
| M23 | the crumb is painted from `shown` | app | `crumb=[self.shown])<LF>        with Horizontal(id="repo-dashboard")` -> `crumb=[self.repo])<LF>        with Horizontal(id="repo-dashboard")` | RED | same |
| M24 | `#repo-name` is painted from `shown` | app | `Static(Text(darkside.plain(self.shown)), id="repo-name")` -> `Static(Text(darkside.plain(self.repo)), id="repo-name")` | RED | same |
| M25 | the field keeps the typed text | app | `                self.app.push_screen(RepoScreen(repo))<LF>` -> `                event.input.value = ""<LF>                self.app.push_screen(RepoScreen(repo))<LF>` | RED | same |
| M26 | `fetch` sends an allowed URL to the clone | github | `        if _is_url(self.repo):<LF>            cwd` -> `        if False:<LF>            cwd` | RED | accepted `[https://h/o/r]` |

26 runs: 25 RED, 1 SURVIVED (M16, equivalent, declared). A first harness version ran `-k` through `cmd.exe` with single
quotes, which broke the argument list and reported RED for a collection error; it was found before any result was used, the
harness now passes an argument list and counts only exit code 1 as RED (exit 2 = ERROR), and M1..M8 were re-run. Not mutated:
the dash/transport pins and the owner/name-through-gh and local-directory pins (green on the base).

## 5. Test results

| check | state |
|---|---|
| `tests/test_inc9k.py` + `test_inc9j/i/h/d/f/g`, `test_github`, `test_inc9/c/e` (incl. the 4 `network` real-git arms, local bare repos only) | executed: 623 passed on `71d2de2` |
| Full default lane, once, uninterrupted, last step | see the result line below |
| `ruff check . --exclude prototypes --output-format concise`, set difference vs `a906c80` (a detached worktree; line and column stripped) | executed: 28 lines each side, new = none, gone = none |
| Literal Cf/Cc/C1 characters in the touched test files | executed: none (control and bidi are `\u` escapes) |
| Known flakes | see the result line below |
| `git stash` | not used |
| Real remote, real `gh`, real cache, network, loopback servers | not-run (stubs; HOME and USERPROFILE in `tmp_path`; the 4 `network` arms clone local bare repos) |
| A real `git clone` of an accepted URL form | not-run (the stub asserts the argv `git clone --mirror -- URL target`) |

## 6. Renders (Pilot, real keys, stub that fails on any process; typed `https://user:tok@example.invalid/o/r.git`, then enter)

`RepoScreen`, 118x34 and 87x34 (blank lines condensed; identical in the lines that matter):

```
 browse maps    connect repo    build map    factory                                                          ◕ mapper
(unrecognised URL)
                               (no hay ramas cargadas)
 (unrecognised URL)
 ▲ failed
 refusing the repository: not
 a supported URL, owner/name,
 or local folder
 q back
 j next branch
 k previous branch
 q back
 ? legend
```

After `q`: `Input.value == 'https://user:tok@example.invalid/o/r.git'` (the only place the text is held). `tok` and `user:` appear in
no row of the frame. Not measured: any terminal other than Textual's headless driver; widths other than 118 and 87.

## 7. Risks, carries, next

- **Risks.** (1) An `owner/name`-shaped text can also be a relative path (`o/..`): the local-directory rule wins, as before.
  (2) A LOCAL DIRECTORY is painted as typed whatever its path holds. (3) `h..x` and a trailing-dot host pass the grammar and fail
  at DNS. (4) An IDN host must be typed as `xn--`. (5) `https://h/o/r@v2` and any `@`-in-path spelling no longer connect
  (declared).
- **Not measured.** A real `git clone` of every accepted form; a real curl/git parse of the refused forms (they are refused
  before any process, so curl never sees them); terminals below 87 columns.
- **Carries.** `Inc-EN` (not started); `LC_ALL=C` on a localised git; orphaned pre-`A-115` mirrors and base-era fallback
  directories (`INC9I-CR-F4`).
- **Next.** The independent reviews of `Inc-9k` (code, UX, security), then `Inc-EN` on the operator's order.

## Commits

`3f4bcac` arms (strict xfail) · `71d2de2` `github.py` + `app.py` + sealed-arm reworks + `OPEN_STEPS` emptied · docs commit
(this record, `A-119`) · docs commit (the full-lane result). No push; `state.json` untouched.

## Full-lane result

pending
