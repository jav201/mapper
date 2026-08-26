# 04b · Security sign-off — Inc-4 (`osopen` / attachments)

**Batch:** `2026-08-25-ui-next-batch-01` · **Repo:** `C:\Users\jjgh8\Github\mapper`
**Reviewer:** `security-reviewer` · **Date:** 2026-08-25
**Gate:** `docs/ARCHITECTURE.md:287` (risk A-4) — *"`security-reviewer` signs off before Inc-4 closes."*
**Predecessor artifact:** `.dev-flow/2026-08-25-ui-next-batch-01/02b-security-review.md` (`approved with conditions`, 2 blockers, 6 majors)

---

## 0 · Verdict

> ## `sign-off blocked`

Two blockers. Both are the **un-landed halves of conditions I raised at PDR** — not new territory, and
not disagreements about design. In each case the corrective pass implemented the condition where the
condition named a file, and stopped at that file's edge while the same untrusted string kept flowing
one function further.

| | |
|---|---|
| **N-1** | A NUL byte in an attachment path raises `ValueError` out of `open_external` and **kills the app**. This is the "shall not raise" half of **C-3**. Proven end-to-end. |
| **N-2** | The refusal notification (`app.py:1389`) is a **markup-parsing sink**. `Toast.render()` raises `MarkupError` on a hostile path, and a benign-looking tag silently rewrites the refusal text the operator reads. This is **C-7** one call frame outside `inspector.py`. Proven at the sink. |

The confinement control itself — the thing this gate exists for — is **correct and it held against
everything I threw at it** (28 file-branch cases, symlinks in both directions, UNC, drive-relative,
long-path prefix, 8.3, a workspace that is itself a symlink). That is real and it is worth saying
plainly.

What is **not** true is that the acceptance suite protects it. **Two independent mutations that
destroy the confinement control leave `tests/test_attachments.py` at 24/24 green**, and one of them
restores the exact three escapes measured in the PDR review (`.gitconfig`, `calc.exe`,
`powershell.exe`). See §3. That is finding **N-3**, and it is the most important thing in this
document, because it means the control is currently held in place by the author's care rather than
by the gate.

### Threat model applied

Local single-operator TUI; the operator already owns the machine. Nothing here is privilege
escalation. The real threat model — as stated in the PDR review and unchanged — is a **shared or
cloned map**: `_nodos.yml` is genuine untrusted input, it arrives with a repo, and activating an
attachment is program execution driven by document content. Severities below are calibrated to that,
not to a server.

### Scope note — concurrent commit

Commit `dd83725` landed **during** this review. I re-verified afterwards: `mapper/osopen.py`
(`sha256 4d07b6a2…`) and `tests/test_attachments.py` (`sha256 0b17eed6…`) were byte-identical
throughout; `mapper/app.py` changed outside the reviewed region and the attachment handlers are
byte-identical, only shifted by one line. **All line numbers in this document are as of `dd83725`.**

---

## 1 · Scope reviewed

| File | sha256 (as reviewed) |
|---|---|
| `mapper/osopen.py` (new — the whole OS-handler boundary) | `4d07b6a2639355cf1ac38b454d73e8671f563fc7d76a810560e3011db4a697c2` |
| `mapper/widgets/inspector.py` (attachment rows + the three `Message` classes) | `a9c0bb248448aae6da6b44c97335a76ec4d96b5edbd14a45540fffeb6a915dc1` |
| `mapper/darkside.py` (`plain()`, the C0/C1 coercion helper) | `29c302469d96ebeff03d1cead8ca4bb7f6206193cc825c1df6f05e7b50c2d8b4` |
| `mapper/app.py` (the call site: `on_ficha_inspector_attachment_*`, `action_add/remove_attachment`) | `c3e73aff04b54dde63cea8816eee4afd7c3fa37b35a0a83d192952ef5083fcf8` |
| `tests/test_attachments.py` (the suite claiming to gate all of this) | `0b17eed63a8e5c994c31e454579e63472a0a331b3fa75ef4d978a80f12e9b66a` |

Environment: Python 3.12.7, Textual 8.2.8, Windows 11 Pro 26200. Everything below was **executed**,
not reasoned about. Probe scripts live in the session scratchpad and were not added to the repo.

---

## 2 · Condition-by-condition discharge

| Condition | Landed? | One-line evidence |
|---|---|---|
| **C-1** · signature takes plain strings + workspace, no `mapper` imports | ✅ **verified** | `inspect.signature` → `(kind: str, target: str, *, workspace: Path, launcher: Callable[[str], None] \| None = None) -> str`; imports are `os, subprocess, sys, pathlib, typing, urllib.parse` only |
| **C-2** · workspace confinement before any launcher call; existence is not authorisation | ⚠️ **partially verified** | Control is **correct and unbroken** under 28 attack cases (§4). But **two mutations that delete it keep the suite green** (§3), and 5 of C-2's own required table rows were never written |
| **C-3** · non-`str` targets refused without raising | ⚠️ **partially verified** | Non-`str` half ✅. **"Shall not raise" half ✗** — a YAML `\0` escape reaches `os.startfile`, which raises `ValueError`; `osopen.py:88` catches `OSError` only → **app dies** (N-1) |
| **C-6** · single coercion helper for C0/C1 | ⚠️ **partially verified** | `darkside.plain()` exists, is the only helper, and is correct. Every `inspector.py` render site routes through it ✅. **`app.py:1387` does not** → ESC survives into the emitted byte stream on the *success* path (N-5) |
| **C-7** · no file-derived `str` to a markup-parsing sink | ❌ **not landed** | `inspector.py` is clean ✅ (zero markup sinks; all `Text.assemble` / `Text()` / `Input.value`). **`app.py:1389` `self.notify(f"{status}: {att.path}")`** — Textual `markup=True` by default → `Content.from_markup` → **`MarkupError`** (N-2) |

**Nothing was taken on trust.** Each row above is an executed probe, not a reading of the corrective
pass's own claims.

### C-1 — verified

Executed: `inspect.signature(osopen.open_external)` returns exactly the shape C-1 specified. The AST
import census at `tests/test_attachments.py:146` derives the import list from the module's own source
rather than a hand-written expectation, and asserts the walk found *something* before asserting the
absence — so it cannot pass vacuously. Independently confirmed by grep across the module. The
`widgets → osopen` ban (C-14) also holds: `mapper/app.py:38` is the **only** import of `osopen`
anywhere outside `tests/`, and `mapper/app.py:1382` is the only call.

### C-2 — the control is right; the gate around it is not

Code is correctly **ordered** (`osopen.py:96–105`): resolve → `is_relative_to` → `exists` → launch.
Existence is genuinely not treated as an authorisation, and `resolve()` is called **before** the
containment test, so symlinks are followed and then judged — the correct order. Verified in §4.

What is missing is the *gate*. C-2's verification text named seven table rows. The suite implements
two (`..` traversal, absent-outside). It omits: **an absolute path outside the workspace**, a UNC
path, an ADS path, a directory, and an empty string. The absent absolute-outside row is precisely
what lets mutation **M9** through (§3).

### C-3 — half landed

The `isinstance(target, str) or not target.strip()` guard at `osopen.py:74` is present and correct;
the parametrised test covers `12345, None, "", "   ", ["a"], {"k": "v"}`. That half is done.

The other half — *"shall not raise for any input reachable from a `yaml.safe_load` of `_nodos.yml`"*,
which is also what the module's own docstring promises at `osopen.py:38` — fails. See N-1.

### C-6 — helper is correct, one consumer bypasses it

`darkside.plain()` (`darkside.py:276`) maps C0 `0x00–0x1F` except `\t`/`\n`, plus `0x7F–0x9F`, to
U+FFFD, and coerces non-`str` (`None → ""`). Executed against every payload C-6 named:

```
'\x1b[31m'                   -> '\ufffd[31m'
'\x1b[6A\x1b[40D'            -> '\ufffd[6A\ufffd[40D'
'\x1b]52;c;cGF5bG9hZA==\x07' -> '\ufffd]52;c;cGF5bG9hZA==\ufffd'
12345                        -> '12345'
None                         -> ''
```

The ESC **introducer** is destroyed in every case, which is the control — the residual literal text
is inert without it. Correct, and correctly *not* using `rich.markup.escape` (C-5 honoured;
zero occurrences in `inspector.py`).

### C-7 — not landed

`inspector.py` is genuinely clean, including `DsChip`, which renders its label into a
`rich.Text(...)` constructor (`components.py:414–429`) and therefore never parses markup. The
condition was written as *"no **inspector** code path"*, and by that literal wording it passes. But
the condition exists to stop file-derived text reaching a markup parser, and it now does — from
`app.py`. See N-2.

---

## 3 · The mutations the suite does not catch  ⟵ **the finding that matters most**

Method: mutate `mapper/osopen.py`, run `python -m pytest tests/test_attachments.py -q`, then attack
the mutant directly. **Baseline: 24 passed.** Both mutations were reverted and the revert confirmed
by sha256 (§7).

### M9 — replace confinement with a `..` substring check · **suite stays 24/24 green**

```python
# was:  if not resolved.is_relative_to(root):
if ".." in target:
    return REFUSED_OUTSIDE
```

```
24 passed in 1.42s
gitconfig  -> abierto ['C:\\Users\\jjgh8\\.gitconfig']
calc.exe   -> abierto ['C:\\Windows\\System32\\calc.exe']
powershell -> abierto ['C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe']
```

The workspace confinement is **entirely gone**, the three escapes measured in the PDR review are
**all restored**, and the acceptance suite reports full success.

Why it survives: every negative confinement case in the suite is a `..`-relative traversal —
`"../secret.txt"` (:45), `"../does-not-exist.txt"` (:65), `"../../etc/passwd"` (:297). A mutant that
merely bans the literal `..` satisfies all three. Nothing in the suite ever passes an **absolute path
outside the workspace**, which is the shape a hostile `_nodos.yml` would actually use — and which
C-2's own verification text explicitly required.

### M5 — replace `is_relative_to` with a string prefix check · **suite stays 24/24 green**

```python
if not str(resolved).startswith(str(root)):
    return REFUSED_OUTSIDE
```

```
24 passed in 1.48s
sibling dir -> abierto ['...\\tmp2r8fcfch\\maps-exfil\\p.exe']
via ..      -> abierto ['...\\tmp2r8fcfch\\maps-exfil\\p.exe']
```

The classic sibling-prefix bypass: `<tmp>\maps-exfil` string-prefixes `<tmp>\maps`. Note the second
row — it escapes **even through a `..` path**, so this is not merely the M9 gap restated. The suite
cannot distinguish `is_relative_to` from a naive prefix comparison, so nothing pins the one property
that makes the current implementation correct.

> These two mutants pass the suite, pass the requirement's stated *intent*, and are exploitable. The
> confinement in `osopen.py` is correct today by the author's care, not by the gate. That is the
> definition of an ungated control.

**The counter-case is also true and worth recording:** deleting the `is_relative_to` check outright
reddens 3 tests (verified independently by the requester). The suite catches *deletion*. It does not
catch *substitution with a weaker check* — which is the realistic regression, since the next person
to touch this file will be editing the expression, not removing the line.

---

## 4 · Attacking the confinement — it held

`open_external("file", …)`, recording launcher, 28 cases. Abridged; every escape attempt is shown.

| Case | Target | Status | Escaped? |
|---|---|---|---|
| traversal | `../secret.txt` | `fuera del espacio de trabajo` | no |
| nested traversal | `sub/../../secret.txt` | `fuera del espacio de trabajo` | no |
| absolute outside (exists) | `<tmp>\secret.txt` | `fuera del espacio de trabajo` | no |
| absolute outside (real) | `C:\Users\jjgh8\.gitconfig` | `fuera del espacio de trabajo` | no |
| UNC | `\\127.0.0.1\C$\Windows\System32\calc.exe` | `fuera del espacio de trabajo` | no |
| **symlink → outside file** | `link_out.txt` | `fuera del espacio de trabajo` | **no** |
| **symlink dir → outside** | `link_dir/secret.txt` | `fuera del espacio de trabajo` | **no** |
| **workspace *is* a symlink** | `../secret.txt` via symlinked ws | `fuera del espacio de trabajo` | **no** |
| drive-relative up | `C:..\secret.txt` | `fuera del espacio de trabajo` | no |
| long-path prefix | `\\?\<ws>\acta.pdf` | `fuera del espacio de trabajo` | no |
| 8.3 short name | `C:\...\LONGDI~1\f.txt` | `fuera del espacio de trabajo` | no |
| NUL byte in path | `acta.pdf\x00.txt` | `destino inválido` | no |
| non-existent workspace | `../secret.txt` | `fuera del espacio de trabajo` | no |
| case flip | `ACTA.PDF` | `abierto` (in-workspace) | n/a |
| trailing dot / space | `acta.pdf.` / `acta.pdf ` | `abierto` (in-workspace) | n/a |
| **ADS** | `acta.pdf:evil` | **`abierto`** | no — but see N-6 |
| **directory** | `sub`, `.` | **`abierto`** | no — but see N-7 |
| **executable inside ws** | `payload.exe` | **`abierto`** | no — but see N-9 |
| device | `NUL` | `abierto` (inert) | no |
| device | `CON`, `COM1` | `no se pudo abrir` | no |

**Symlinks are handled correctly and this deserves credit.** `resolve()` follows the link and the
containment test runs on the *resolved* target — resolution before judgement, which is the correct
order and the one that is usually got wrong. A workspace that is itself a symlink also behaves: both
sides go through `resolve()`, so the comparison stays consistent. Windows case-insensitivity is
handled by `PureWindowsPath` comparison semantics inside `is_relative_to`.

`kind == "url"` cannot be used to reach a file: `C:\Windows\notepad.exe` and `\\host\share\x` are both
refused as `esquema no permitido`, and `file:` is correctly excluded from `ALLOWED_SCHEMES`
(`osopen.py:35`) — which is what stops the url branch becoming an unconfined path. Good.

**Call-site checks:** `self.store is None` returns early (`app.py:1377`) before any target is read;
the index is bounds-checked (`app.py:1379`); `workspace=self.store.workspace` is the correct root
(the `MapStore` directory, the same root the `.mmd`/`_nodos.yml` pair is loaded from).

---

## 5 · Findings

### Blockers

#### N-1 · A NUL byte in an attachment path kills the app  `[blocker]`

- **What.** `os.startfile` raises `ValueError` — **not** an `OSError` — on an embedded NUL.
  `osopen.py:88` catches `OSError` only, so it propagates out of `open_external`, out of the Textual
  message handler, and terminates the app.
- **Where.** `mapper/osopen.py:87–89` (url branch). Reached from `mapper/app.py:1382`.
- **Reachability — this is the part that makes it real.** A NUL is reachable from a **plain-ASCII,
  fully valid** `_nodos.yml`, because YAML's double-quoted scalars support the `\0` escape:

  ```
  sidecar source (all printable):  path: "\0https://example.com/x"
  yaml.safe_load produced:         '\x00https://example.com/x'
  ```

  `urlparse` reports scheme `https`, the allowlist passes, and the launcher is reached.
- **Executed evidence.**
  ```
  open_external('url', p, workspace=ws)
    -> *** RAISED ValueError: startfile: embedded null character in filepath
  issubclass(ValueError, OSError) -> False
  ```
  End-to-end through the shipped surface, production launcher path:
  ```
  NUL url (real launcher)  *** APP DIED: ValueError: startfile: embedded null character in filepath
    app.py:1382 in on_ficha_inspector_attachment_activated
    osopen.py:87 in open_external
  ```
- **Why it matters.** Denial of service from a shared or cloned map, on the operator's `↵`. It also
  breaks the module's own contract — `osopen.py:38` promises *"this module never raises for anything
  reachable from a `yaml.safe_load` of a sidecar"* — and that contract is what the single call site
  is written against. Not code execution; scoped accordingly.
- **Recommendation.** Widen the launch guard on **both** branches and refuse NUL explicitly:
  ```python
  if "\x00" in target:
      return REFUSED_TYPE
  ...
  try:
      launch(target.strip())
  except (OSError, ValueError):
      return REFUSED_ERROR
  ```
  Add a test row driven from `yaml.safe_load('path: "\\0https://example.com/x"')` — from the YAML,
  not from a Python literal, so the test proves *reachability* and not just the guard.

#### N-2 · The refusal notification is a markup-parsing sink  `[blocker]`

- **What.** `self.notify(f"{status}: {att.path}", severity="warning")` passes a raw, uncoerced,
  file-derived string into Textual's markup parser.
- **Where.** `mapper/app.py:1389`.
- **Mechanism, executed.** `App.notify` in Textual 8.2.8 is
  `notify(message, *, title='', severity='information', timeout=None, markup: bool = True)` —
  **`markup` defaults to `True`**, and `app.py:1389` does not override it. `Toast.render()` then does
  `Content.from_markup(notification.message) if notification.markup else Content(...)`.
- **Executed evidence** (through the shipped surface, real notification object):
  ```
  notifications: 1
    markup=True  message='esquema no permitido: javascript:[/bold]OWNED'
    *** Toast.render RAISED MarkupError: closing tag '[/bold]' does not match any open tag
  ```
  And the quieter, arguably worse half — a *well-formed* tag is silently consumed:
  ```
  Content.from_markup('esquema no permitido: javascript:[bold red on white]OWNED')
    -> plain='esquema no permitido: javascript:OWNED'  spans=1
  ```
- **Why it matters.** Two distinct impacts:
  1. **Crash on the refusal path.** A `MarkupError` during compositing, triggered by the very message
     that reports a refusal. The security control fires correctly, and the *reporting* of it breaks.
  2. **Refusal-message forgery — the more serious one.** The map author controls bracketed text in
     `att.path`, and it is *removed* from what the operator reads while a style is applied. The
     operator is shown a doctored refusal at the exact moment they most need an honest string. This
     directly defeats **LLR-N02.10 / C-11** (*"the string the operator reads is the string the
     launcher receives"*), which the inspector honours and the toast does not.
- **Why C-7 did not catch it.** C-7 was scoped *"no **inspector** code path"*. The corrective pass
  cleaned `inspector.py` thoroughly and correctly — and the same untrusted string kept flowing one
  frame further into a sibling sink in `app.py` that the wording never reached.
- **Recommendation.** Coerce and disable markup at the sink:
  ```python
  self.notify(f"{status}: {darkside.plain(att.path)}", severity="warning", markup=False)
  ```
  Then broaden LLR-N01.11 from *"no inspector code path"* to *"no code path"*, and gate it with a
  census test over `mapper/` asserting every `notify(` call carrying file-derived text passes
  `markup=False`.

### Majors

#### N-3 · `tests/test_attachments.py` does not gate the confinement control  `[major]`

- **What.** Two mutations that destroy workspace confinement leave the suite at 24/24 green (§3).
- **Where.** `tests/test_attachments.py:33–71` — the confinement cases.
- **Why it matters.** The suite is the Inc-4 gate. It currently detects *deletion* of the check but
  not *substitution with a weaker one*, which is the realistic regression path.
- **Recommendation.** Write the five missing rows from C-2's own verification table as a single
  parametrised negative case, launcher asserted uncalled on every row: an **absolute path outside the
  workspace that exists** (kills M9), a **sibling directory sharing the root's name prefix**
  (kills M5), a **UNC path**, a **directory**, and an **empty string**. The first two are the ones
  that matter; add them and both mutants redden.

#### N-4 · C-10 (userinfo in the authority) was never implemented  `[major]`

- **What.** No userinfo check exists in the url branch.
- **Where.** `mapper/osopen.py:79–90`.
- **Executed evidence.**
  ```
  https://user:pass@evil.example.com/     -> abierto  (launched)
  https://example.com@evil.example.com/   -> abierto  (launched)
  http://evil@good.example.com/           -> abierto  (launched)
  ```
- **Why it matters.** The middle row is the attack: the inspector honestly displays the full target
  (LLR-N02.10 holds), and the operator reading left-to-right sees `example.com` while the browser
  navigates to `evil.example.com`. Display honesty is defeated by URL syntax rather than by the
  renderer. Under LFPDPPP this also silently exfiltrates the operator's IP and any author-embedded
  userinfo to a third-party host when a **client** map is opened.
- **Recommendation.** `if "@" in urlsplit(target.strip()).netloc: return REFUSED_SCHEME` (or a
  dedicated status word), plus the two test rows C-10 already specified.

### Minors

| # | Finding | Where | Evidence | Recommendation |
|---|---|---|---|---|
| **N-5** | `_event_toast` bypasses `darkside.plain()` on the **success** path, so an OSC-52 clipboard-write sequence in `att.caption`/`att.path` reaches the terminal verbatim | `app.py:1387` | `Text.assemble` with the raw string → `ESC present in emitted bytes: True`; with `plain()` applied the ESC introducer is gone | `self._event_toast("abierto", darkside.plain(att.caption or att.path))` |
| **N-6** | NTFS **alternate data stream** targets are launched, not refused — C-2's table required refusal | `osopen.py:102` | `acta.pdf:evil` → `abierto`, launched as `…\maps\acta.pdf:evil` | Refuse a `:` in any component past the drive anchor. Blast radius is contained (the stream rides an in-workspace file), hence minor — but it is a stated, unimplemented table row |
| **N-7** | **Directory** targets are launched (opens Explorer on the workspace) — C-2's table required refusal | `osopen.py:104` | `sub` and `.` → `abierto` | `if resolved.is_dir(): return REFUSED_TYPE` |
| **N-8** | C-4 specified `urlsplit`; the code uses `urlparse` | `osopen.py:81` | Ran both over the full 37-case corpus: **zero scheme disagreements**. Behaviourally equivalent here | Cosmetic. Either switch to `urlsplit` or amend C-4 — do not leave code and condition disagreeing in writing on a gated control |
| **N-9** | C-16's executable question is still unrecorded, and executables inside the workspace **do** launch | `docs/ARCHITECTURE.md:36`; `osopen.py:107` | `payload.exe` inside the workspace → `abierto`. Row 36 was amended for the scheme allowlist but says nothing about extensions | C-16 was explicitly non-blocking, so this does not gate. But record the **decision** — a cloned map folder is not a trust boundary. The next reviewer should read a decision, not an omission |
| **N-10** | `darkside.plain()` passes U+202E (RTL override) through unchanged | `darkside.py:272` | `plain('\u202egnp.exe') -> '\u202egnp.exe'`; `https://evil.example/\u202egnp.exe` launches | Display-honesty gap against LLR-N02.10, same family as N-4. Consider adding U+202A–U+202E and U+2066–U+2069 to `_CONTROL_MAP` |
| **N-11** | Add-handler kind inference is a substring test | `app.py:1403` | `kind = "url" if "://" in target else "file"` — `\\host\share\x` becomes `kind="file"` (confined, so safe); `javascript:alert(1)` becomes `kind="file"` (refused) | Fails safe in every case I tried, and the input is operator-typed rather than file-derived. Noted for completeness only |

### Explicitly clean

Verified, not assumed: `inspector.py` markup discipline (C-7's own file), `DsChip` label rendering,
the `widgets → osopen` import ban (C-14), the no-shell property (`shell=True`/`os.system` absent, and
the launcher passes a single argument as a list on POSIX), `file:` exclusion from the scheme
allowlist, `self.store is None` handling, attachment index bounds-checking, `workspace` root
correctness, `rich.markup.escape` absent from `inspector.py` (C-5), and the C-15 launcher default
(the real platform launcher — confirmed by the N-1 probe, which reached `os.startfile` with
`launcher` omitted; note this is verified *by my probe*, not by the suite, which always injects).

---

## 6 · What must land before sign-off

**Blocking:**

1. **N-1** — catch `ValueError` alongside `OSError` on both launch paths and refuse NUL explicitly;
   test driven from `yaml.safe_load`, proving reachability.
2. **N-2** — `markup=False` **and** `darkside.plain()` at `app.py:1389`; broaden LLR-N01.11 from
   *"no inspector code path"* to *"no code path"*.
3. **N-3** — add the absolute-path-outside and sibling-prefix rows so mutants **M9** and **M5** both
   redden. I will re-run both mutations at re-review.

**Strongly recommended, not blocking:** N-4 (C-10 was a stated major and is simply absent).

**Not blocking:** N-5 through N-11. N-9 (C-16) needs a written decision, not a code change.

On re-submission I will re-execute the M9 and M5 mutations, the NUL probe, and the toast probe. A
claim that these landed is not evidence that they landed.

---

## 7 · Evidence checklist

| Item | ✓/✗ | Evidence |
|---|---|---|
| Each finding has what · where · why · recommendation | ✓ | §5 — both blockers and both majors carry all four; minors carry where + executed evidence + recommendation |
| Each finding has a severity rating | ✓ | 2 `blocker` (N-1, N-2), 2 `major` (N-3, N-4), 7 `minor` (N-5…N-11) |
| No secret values appear in this output | ✓ | No credential, token or key was read or emitted. `C:\Users\jjgh8\.gitconfig` appears only as a **resolved path** in probe output; its contents were never read |
| Verdict is explicit | ✓ | §0 — **`sign-off blocked`** |
| New tool/integration: scope and blast radius addressed | ✓ | §4 — `osopen` is the external-action surface. **Scope:** OS default-application launch. **Blast radius as implemented:** confined to the workspace root for `kind == "file"` (verified against 28 escape attempts incl. symlinks in both directions), and to `http`/`https` for `kind == "url"` — a genuine and large reduction from the PDR measurement. **Residual:** any file *inside* the workspace including executables (N-9); any http(s) host including one masked by userinfo (N-4). **Reversibility:** none — a launch cannot be undone. **Human-in-the-loop:** the `↵` keystroke is the approval, which is why N-2 (forged refusal text) and N-4 (forged host) matter more than their crash impact. **Data flow:** for `kind == "url"` the target host learns the operator's IP — flag under LFPDPPP where a client map is involved |
| Every condition discharged with executed evidence, not the corrective pass's claim | ✓ | §2 — C-1 ✅, C-2 ⚠️, C-3 ⚠️, C-6 ⚠️, C-7 ❌; each backed by a probe in §3/§4/§5 |
| Mutation testing performed against the acceptance suite | ✓ | §3 — M9 and M5, both **24/24 green while the control is defeated** |
| Mutations reverted; revert confirmed by sha256; `__pycache__` purged | ✓ | `mapper/osopen.py` post-revert `sha256 4d07b6a2639355cf1ac38b454d73e8671f563fc7d76a810560e3011db4a697c2` — **identical to the pre-mutation baseline**; `git status` clean for the file; `find mapper tests -name __pycache__ \| wc -l` → `0`; suite re-run 24 passed |
| No code changed; `prototypes/` untouched | ✓ | Only `mapper/osopen.py` was mutated, twice, both reverted and hash-verified. No file under `prototypes/` was read or written. This artifact is the only file written |

---

## 8 · Gate verdict

> ### `sign-off blocked`
>
> Inc-4 **must not close** until N-1, N-2 and N-3 are fixed and re-verified.

The confinement control is well built and it survived a serious attempt to break it — symlink
handling in particular is correct in the way that is usually got wrong. The gate fails for a
different reason: **two conditions were implemented up to the edge of the file they named** while the
same untrusted string kept flowing (N-1 out of `open_external`'s contract, N-2 into a sibling sink in
`app.py`), and **the suite that is supposed to hold the confinement in place does not** (N-3).

Re-review on re-submission, per `docs/ARCHITECTURE.md:287` (risk A-4).
